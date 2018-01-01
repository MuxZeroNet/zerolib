import msgpack
from msgpack import Unpacker
from msgpack.exceptions import OutOfData
import re
import struct
from io import BytesIO
from collections import namedtuple
from base64 import b32encode, b32decode

from .sanitizer import Condition, opt, val_types
from . import sanitizer

def unpack(data, sender = None):
    """Unpack a byte string, and indicate that it was sent from a network address.
    Only unpacks one packet at a time.
    """
    return unpack_stream(BytesIO(data), sender)

def unpack_stream(stream, sender = None):
    """Unpack a stream, and indicate that it was sent from a network address.
    Only unpacks one packet at a time.
    Raises: ValueError, TypeError, KeyError, IOError
    """
    generator = packet_unpacker()
    unpacked = next(generator)
    while unpacked is None:
        unpacked = generator.send(stream.read(1))
    return unpacked


def dict_unpacker():
    kwargs = {
        'max_str_len': 512 * 1024,
        'max_bin_len': 512 * 1024,
        'max_buffer_size': 512 * 1024,
        'max_array_len': 4000,
        'max_map_len': 4000,
        'max_ext_len': 0,
    }
    unpacker = msgpack.Unpacker(**kwargs)

    while True:
        data = yield
        unpacker.feed(data)
        try:
            dict_len = unpacker.read_map_header()
            if dict_len > 10:
                raise ValueError('Dict len > 10')
        except OutOfData:
            pass

    iterator = iter(unpacker)
    payload_dict = {}

    for i in range(dict_len):
        while True:
            data = yield
            unpacker.feed(data)
            try:
                key = next(iterator)
                break
            except StopIteration:
                pass
        while True:
            data = yield
            unpacker.feed(data)
            try:
                value = next(iterator)
                break
            except StopIteration:
                pass
        payload_dict[key] = value

    yield payload_dict


def packet_unpacker(sender = None):
    generator = dict_unpacker()
    unpacked = next(generator)
    while unpacked is None:
        data = yield
        unpacked = generator.send(data)
    yield unpack_dict(unpacked, sender)


@val_types(dict)
def unpack_dict(packet, sender = None):
    req_id = packet.get(b'req_id', packet.get(b'to'))
    if not isinstance(req_id, int):
        raise TypeError('Sequence number (req_id) should be an int, not %s' % req_id.__class__.__name__)
    if not (0 <= req_id <= 0xFFffFFff):
        raise ValueError('Sequence number (req_id) out of range')

    if packet[b'cmd'] == b'response':
        instance = unpack_response(packet)
    else:
        instance = unpack_request(packet)

    instance.req_id = req_id
    instance.sender = sender
    return instance

def unpack_request(unpacked):
    cmd, params = unpacked[b'cmd'], unpacked[b'params']
    if not isinstance(params, dict):
        raise TypeError('Parameters should be a dict, not %s' % params.__class__.__name__)
    instance = request_dict[cmd]()
    instance.parse(params)
    return instance

def unpack_response(params):
    for (key, cls) in attr_dict.items():
        if key in params:
            instance = cls()
            instance.parse(params)
            return instance
    for ((key, t), cls) in attr_type_dict.items():
        if isinstance(params.get(key), t):
            instance = cls()
            instance.parse(params)
            return instance

    raise KeyError('Unknown response packet')


def use_condition(func):
    def f(self, params):
        c = Condition(params)
        return func(self, c, params)
    return f



#################### base classes ####################

class Packet(object):
    __slots__ = ['req_id', 'sender']

    def __init__(self):
        pass

    def parse(self, params):
        pass

    def pack(self, recipient):
        raise NotImplementedError()

    def __bytes__(self):
        return msgpack.packb(self.pack(self.sender))

    def write_to(self, stream):
        return msgpack.pack(self.pack(self.sender), stream)

class PrefixIter(object):
    def __iter__(self):
        return iter(self.prefixes)

    def __contains__(self, item):
        return (item in self.prefixes)

    def __len__(self):
        return len(self.prefixes)


#################### ping, pong, ok ####################

class Ping(Packet):
    """Unpacked [ping] packet that checks if the client is still alive."""
    pass

class Predicate(Packet):
    __slots__ = ['ok']

    def parse(self, params):
        self.ok = (b'ok' in params)

class Pong(Packet):
    pass


#################### get file ####################

class RespFile(Packet):
    __slots__ = [
        'body', 'last_byte_offset', 'total_size',
        'site', 'inner_path',
    ]

    @use_condition
    def parse(self, c, params):
        self.total_size = c.as_size('size')
        self.last_byte_offset = c.range('location', (0, self.total_size - 1))

        body = c.as_type('body', bytes)
        if len(body) > self.total_size:
            raise ValueError('File body length out of range. %d > %d' % (len(body), self.total_size))
        if self.last_byte_offset + 1 - len(body) < 0:
            raise ValueError('File offset cannot be negative')
        self.body = body

    @property
    def next_offset(self):
        return self.last_byte_offset + 1

    @property
    def offset(self):
        return self.next_offset - len(self.body)


class GetFile(Packet):
    """Unpacked [getFile] packet that requests for a file."""
    __slots__ = ['site', 'inner_path', 'offset', 'total_size']
    response_cls = RespFile
    copy_attrs = ['site', 'inner_path', 'offset', 'total_size']

    @use_condition
    def parse(self, c, params):
        self.site = c.btc('site')
        self.inner_path = c.inner('inner_path')
        self.offset = c.as_size(opt('location')) or 0
        self.total_size = c.as_size(opt('file_size'))


#################### peer data structure ####################

AddrPort = namedtuple('AddrPort', ['address', 'port'])
# For spec, see https://github.com/HelloZeroNet/Documentation/issues/57

class Address(object):
    __slots__ = ['readable', 'packed']

    def __init__(self, bytes_or_str):
        if isinstance(bytes_or_str, bytes):
            self.init_bytes(bytes_or_str)
        else:
            self.init_str(bytes_or_str)

    @staticmethod
    def strip_suffix(s, suffix):
        s = s.upper()
        if s.endswith(suffix):
            s = s[0:-len(suffix)]
        return s

    def __str__(self):
        return self.readable

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self.packed))

    def __eq__(self, other):
        return self.packed == other.packed

    def __hash__(self):
        return hash(self.packed)


class OnionAddress(Address):
    def init_str(self, s):
        s = self.__class__.strip_suffix(s, '.ONION')
        self.init_bytes(b32decode(s))

    def init_bytes(self, bstr):
        if len(b) not in (10, 35):
            raise ValueError('A packed onion address should be either 10 or 35 bytes long, not %d' % len(b))
        self.readable = b32encode(bstr).decode('ascii').lower() + '.onion'
        self.packed = bstr

class I2PAddress(Address):
    def init_str(self, s):
        s = self.__class__.strip_suffix(s, '.B32.I2P')
        self.init_bytes(b32decode(s + '===='))

    def init_bytes(self, bstr):
        if len(b) != 32:
            raise ValueError('A packed .b32.i2p address should be 32 bytes long, not %d' % len(b))
        self.readable = b32encode(bstr).decode('ascii').lower() + '.b32.i2p'
        self.packed = bstr


@val_types(bytes)
def unpack_ip(b):
    if len(b) == 16 + 2:
        address = IPv6Address(b[0:-2])
    elif len(b) == 4 + 2:
        address = IPv4Address(b[0:-2])
    else:
        raise ValueError('A packed IP address should be either 4 or 16 bytes long, not %d' % len(b) - 2)
    port = struct.unpack('>H', b[-2:])
    return AddrPort(address, port)

@val_types(bytes)
def unpack_onion(b):
    address = OnionAddress(b[0:-2])
    port = struct.unpack('>H', b[-2:])
    return AddrPort(address, port)

@val_types(bytes)
def unpack_i2p(b):
    address = I2PAddress(b)
    return AddrPort(address, 0)


#################### peer exchange ####################

class RespPEX(Packet):
    __slots__ = ['peers', 'onions', 'garlics', 'site']

    @use_condition
    def parse(self, c, params):
        PEX.parse_peers(self, c)

class PEX(Packet):
    """Unpacked [pex] packet that exchanges peers with the client. Peers will be parsed at init."""
    __slots__ = ['site', 'peers', 'onions', 'garlics', 'need']
    response_cls = RespPEX
    copy_attrs = ['site']

    @use_condition
    def parse(self, c, params):
        self.site = c.btc('site')
        self.need = c.range(opt('need'), (0, 10000)) or 0
        self.parse_peers(self, c)

    @staticmethod
    def unpack_peers(c, unpack_func, key):
        raw_list = c.as_type(opt(key), list) or ()
        peers = set()
        for peer in raw_list:
            try:
                peers.add(unpack_func(peer))
            except (TypeError, ValueError):
                pass
        return peers

    def parse_peers(self, c):
        self.peers = self.__class__.unpack_peers(c, unpack_ip, 'peers')
        self.onions = self.__class__.unpack_peers(c, unpack_onion, 'peers_onion')
        self.garlics = self.__class__.unpack_peers(c, unpack_i2p, 'peers_i2p')


#################### file update ####################

class Update(Packet):
    """Unpacked [update] packet that pushes a site file update."""
    __slots__ = ['site', 'inner_path', 'body']
    response_cls = Predicate

    @use_condition
    def parse(self, c, params):
        self.site = c.btc('site')
        self.inner_path = c.inner('inner_path')
        self.body = c.strlen('body', (0, 512*1024))

        # TODO: diff


#################### handshake and response ####################

class Handshake(Packet):
    """Unpacked [handshake] packet sent when the connection is initialized."""
    __slots__ = ['crypto_set', 'port', 'onion_address', 'protocol', 'open', 'peer_id', 'rev', 'version']

    @use_condition
    def parse(self, c, params):
        crypto_list = c.as_type('crypt_supported', list)
        self.crypto_set = set()
        for item in crypt_list:
            try:
                self.crypto_set.add(item.decode('ascii'))
            except (AttributeError, ValueError):
                pass

        self.port = c.port(opt('fileserver_port')) or 0
        self.protocol = c.strlen('protocol', 10).decode('ascii')
        self.peer_id = c.strlen(opt('peer_id'), 64)
        self.rev = c.range(opt('rev'), (0, 0xffFFffFF)) or 0
        self.version = c.strlen('version', 64).decode('ascii')

        onion = c.onion(opt('onion'))
        if onion:
            self.onion_address = OnionAddress(onion)
        else:
            self.onion_address = None

        self.open = (params.get(b'opened') is True)

    @property
    def onion(self):
        if self.onion_address and self.port:
            return AddrPort(self.onion.address, self.port)
        else:
            return None



class ACK(Handshake):
    __slots__ = ['preferred_crypto']

    @use_condition
    def parse(self, c, params):
        super().parse(params)
        crypto = c.as_type(opt('crypt'), bytes)
        if crypto:
            self.preferred_crypto = crypto.decode('ascii')
        else:
            self.preferred_crypto = None


#################### listing modified files ####################

class RespMod(Packet):
    __slots__ = ['timestamps', 'site']

    @use_condition
    def parse(self, c, params):
        files_dict = c.as_type('modified_files', dict)
        self.timestamps = {}
        for item in files_dict.items():
            try:
                path, time = self.parse_item(c, item)
                self.timestamps[path] = time
            except (TypeError, ValueError):
                pass

    def parse_item(self, item):
        path, time = item
        return sanitizer.check_path(path), sanitizer.check_time(time)

    def __iter__(self):
        return iter(self.timestamps)

    def __contains__(self, key):
        return (key in self.timestamps)

    def __len__(self):
        return len(self.timestamps)

    def items(self):
        return self.timestamps.items()


class ListMod(Packet):
    """Unpacked [listModified] packet that requests for the names of
    content.json files modified since the given time.
    It is used to determine a site's new user content."""
    __slots__ = ['site', 'since']
    response_cls = RespMod
    copy_attrs = ['site']

    @use_condition
    def parse(self, c, params):
        self.site = c.btc('site')
        self.since = c.time('since')


#################### hash prefix ####################

@val_types(bytes)
def int_hash_id(bstr, start=0):
    try:
        return struct.unpack('>H', bstr[start:start+2])[0]
    except struct.error as e:
        raise ValueError('Length of Hash ID string should be 2n, not %d' % len(bstr)) from e

@val_types(int)
def hash_prefix(int_hid):
    try:
        return struct.pack('>H', int_hid)
    except struct.error as e:
        raise ValueError('Hash ID out of range(0, 0xFFFF)') from e

prefix_len = 2
@val_types(bytes)
def hash_set(bstr):
    """
    >>> bstr = b'11223344556677889900aaAAbbBBccddCDEFCDCDaaAA1122'
    >>> hash_set(bstr)
    frozenset({b'11', b'22', b'33', b'44', b'55', b'66', b'77', b'88', b'99', \
    b'00', b'aa', b'AA', b'bb', b'BB', b'cc', b'dd', b'CD', b'EF'})
    """

    if len(bstr) > prefix_len * 2000:
        raise ValueError('Too many hash IDs to unpack')
    if len(bstr) % prefix_len != 0:
        raise ValueError('Hash ID string length should be multiples of %d, not %d' % (prefix_len, len(bstr)))
    generator = (bstr[i : i+2] for i in range(0, len(bstr), 2))
    prefixes = frozenset(generator)
    return prefixes


class RespHashSet(Packet, PrefixIter):
    __slots__ = ['prefixes', 'site']

    def parse(self, params):
        SetHash.parse_raw_hash(self, params)


class GetHash(Packet):
    """Unpacked [getHashfield] packet that requests for the client's list of downloaded opt file IDs."""
    __slots__ = ['site']
    response_cls = RespHashSet
    copy_attrs = ['site']

    @use_condition
    def parse(self, c, params):
        self.site = c.btc('site')


class SetHash(Packet, PrefixIter):
    """Unpacked [setHashfield] packet that announces and updates the sender's list of opt file IDs."""
    __slots__ = ['site', 'prefixes']
    response_cls = Predicate

    @use_condition
    def parse(self, c, params):
        self.site = c.btc('site')
        self.parse_raw_hash(params)

    def parse_raw_hash(self, params):
        self.prefixes = hash_set(params.get(b'hashfield_raw'))


class RespHashDict(Packet):
    __slots__ = ['site']

    def parse(self, params):
        raise NotImplementedError()


class FindHash(Packet, PrefixIter):
    """Unpacked [findHashIds] packet that asks if the client knows any peer that has the said Hash IDs."""
    __slots__ = ['site', 'prefixes']
    response_cls = RespHashSet
    copy_attrs = ['site']

    @use_condition
    def parse(self, c, params):
        self.site = c.btc('site')

        def generator(plist):
            for i in plist:
                try:
                    yield hash_prefix(i)
                except (ValueError, TypeError):
                    pass

        prefix_list = c.as_type('hash_ids', list)
        self.prefixes = forzenset(generator(prefix_list))


#################### check port ####################

class RespPort(Packet):
    __slots__ = ['status', 'port']

    @use_condition
    def parse(self, c, params):
        try:
            self.status = c.strlen('status', 32).decode('ascii')
        except AttributeError as e:
            raise TypeError() from e

    @property
    def open(self):
        return self.status == 'open'


class CheckPort(Packet):
    """Unpacked [actionCheckport] packet that asks the client to check the sender's port."""
    __slots__ = ['port']
    response_cls = RespPort
    copy_attrs = ['port']

    @use_condition
    def parse(self, c, params):
        self.port = c.port('port')


#################### big files ####################

class RespPieceDict(Packet):
    def parse(self, params):
        raise NotImplementedError()

class GetPieceStatus(Packet):
    response_cls = RespPieceDict

    def parse(self, params):
        raise NotImplementedError()


class SetPieceStatus(Packet):
    response_cls = Predicate
    def parse(self, params):
        raise NotImplementedError()


#################### DHT ####################

class _DHT(Packet):
    """No Reference Implementation. No Spec.
    Unpacked [*dht*] packet used to collaboratively maintain a DHT."""
    def parse(self, params):
        raise NotImplementedError()


request_dict = {
    b'getFile': GetFile,
    b'pex': PEX,
    b'update': Update,
    b'ping': Ping,
    b'handshake': Handshake,
    b'listModified': ListMod,
    b'getHashfield': GetHash,
    b'setHashfield': SetHash,
    b'findHashIds': FindHash,
    b'actionCheckport': CheckPort,
    b'checkport': CheckPort,
    b'getPieceFields': GetPieceStatus,
    b'setPieceFields': SetPieceStatus,
}

attr_dict = {
    b'protocol': ACK,
    b'ok': Predicate,
    b'error': Predicate,
    b'pong': Pong,
    b'location': RespFile,
    b'modified_files': RespMod,
    b'hashfield_raw': RespHashSet,
    b'status': RespPort,
    b'piecefields_packed': RespPieceDict,
}

attr_type_dict = {
    (b'peers', list): RespPEX,
    (b'peers', dict): RespHashDict,
}

response_packets = set()
for v in request_dict.values():
    try:
        response_packets.add(getattr(v, 'response_cls'))
    except AttributeError:
        pass


__all__ = [
    'unpack', 'unpack_stream', 'unpack_dict', 'response_packets',
    'dict_unpacker', 'packet_unpacker',
    'OnionAddress', 'Packet', 'PrefixIter',

    'GetFile', 'PEX', 'Update', 'Ping', 'Handshake', 'ListMod',
    'GetHash', 'SetHash', 'FindHash', 'CheckPort', 'GetPieceStatus',
    'SetPieceStatus',

    'RespFile', 'RespPEX', 'Predicate', 'Pong', 'ACK', 'RespMod',
    'RespHashSet', 'RespHashDict', 'RespPort', 'RespPieceDict',
]
