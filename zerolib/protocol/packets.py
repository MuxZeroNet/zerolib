import msgpack
import ipaddress
import re
import struct
from io import BytesIO
from collections import namedtuple
from base64 import b32decode
from .sanitizer import Condition, opt, val_types

def unpack(data, from_addr = None):
    """Unpack a byte string sent from a network address.
    Extra data will not be parsed.
    """
    return unpack_stream(BytesIO(data), from_addr)


def unpack_stream(stream, from_addr = None):
    """Unpack a stream sent from a network address.
    Raises: ValueError, TypeError, KeyError
    Raises: IOError
    """
    STEP, STR_LEN, ITER_LEN = (1, 64*1024 + 1, 4000)
    try:
        unpacked = msgpack.unpackb(
            data, read_size=STEP, max_str_len=STR_LEN, max_bin_len=STR_LEN,
            max_array_len=ITER_LEN, max_map_len=ITER_LEN)
    except Exception as e:
        raise ValueError(e.__class__.__name__ + ' : ' + str(e))

    cmd, req_id, params = unpacked[b'cmd'], None, None
    if cmd == b'response':
        req_id = unpacked[b'to']
        params = unpacked
    else:
        req_id = unpacked[b'req_id']
        params = unpacked[b'params']

    if not isinstance(req_id, int) or not(0 <= req_id <= 0xFFFFFFFF):
        raise ValueError('Invalid req_id')

    instance = cls_dict[cmd](params)
    instance.req_id = req_id
    instance.from_addr = from_addr
    return instance


class Packet(object):
    __slots__ = ['req_id', 'from_addr']


class GetFile(Packet):
    """Unpacked [getFile] packet that requests for a file."""
    __slots__ = ['site', 'inner_path', 'offset', 'total_size']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        self.site = c.btc('site')
        self.inner_path = c.inner('inner_path')
        self.offset = c.as_size('location')
        self.total_size = c.as_size(opt('file_size'))


AddrPort = namedtuple('AddrPort', ['address', 'port'])
# For spec, see https://github.com/HelloZeroNet/Documentation/issues/57

class OnionAddress(object):
    __slots__ = ['_str', 'packed']

    def __init__(self, bstr):
        if len(b) not in (10, 35):
            raise ValueError('A packed onion address should be either 10 or 35 bytes long, not %d' % len(b))
        self._str = b32encode(bstr).decode('ascii') + '.onion'
        self.packed = bstr

    def __str__(self):
        return self._str

    def __repr__(self):
        return 'OnionAddress(%s)' % repr(self.packed)

    def __eq__(self, other):
        return self.packed == other.packed

    def __hash__(self):
        return hash(self.packed)


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

class PEX(Packet):
    """Unpacked [pex] packet that exchanges peers with the client. Peers will be parsed at init."""
    __slots__ = ['site', 'peers', 'onions', 'need']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        self.site = c.btc('site')
        self.need = c.range(opt('need'), (0, 10000))

        b_peers = c.as_type(opt('peers'), list)
        b_onions = c.as_type(opt('peers_onion'), list)
        self.peers = set()
        self.onions = set()
        for peer in b_peers:
            try:
                self.peers.add(unpack_ip(peer))
            except (TypeError, ValueError):
                pass
        for onion in b_onions:
            try:
                self.onions.add(unpack_onion(onion))
            except (TypeError, ValueError):
                pass



class Update(Packet):
    """Unpacked [update] packet that pushes a site file update."""
    __slots__ = ['site', 'inner_path', 'body']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        self.site = c.btc('site')
        self.inner_path = c.inner('inner_path')
        self.body = c.strlen('body', (0, 512*1024))


class Handshake(Packet):
    """Unpacked [handshake] packet sent when the connection is initialized."""
    __slots__ = ['crypto_set', 'port', 'onion', 'protocol', 'opened', 'peer_id', 'rev']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        crypto_list = c.as_type('crypt_supported', list)
        self.crypto_set = set()
        for item in crypt_list:
            try:
                self.crypto_set.add(item.decode('ascii'))
            except (AttributeError, ValueError):
                pass

        self.port = c.port(opt('fileserver_port'))
        self.onion = c.onion(opt('onion'))
        self.protocol = c.strlen(opt('protocol'), 10)
        self.peer_id = c.strlen(opt('peer_id'), 64)
        self.rev = c.range(opt('rev'), (0, 0xffFFffFF)) or 0

        self.opened = (params.get(b'opened') is True)


class Ping(Packet):
    """Unpacked [ping] packet that checks if the client is still alive."""
    def __init__(self, params = None):
        pass


class ListMod(Packet):
    """Unpacked [listModified] packet that requests for the names of
    content.json files modified since the given time.
    It is used to determine a site's new user content."""
    __slots__ = ['site', 'since']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        self.site = c.btc('site')
        self.since = c.time('since')


class GetHash(Packet):
    """Unpacked [getHashfield] packet that requests for the client's list of downloaded opt file IDs."""
    __slots__ = ['site']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        self.site = c.btc('site')


@val_types(bytes)
def int_hash_id(bstr, start=0):
    try:
        return struct.unpack('>H', bstr[start:start+2])[0]
    except struct.error as e:
        raise ValueError('Length of HashID string should be 2n, not %d' % len(bstr)) from e

@val_types(int)
def hash_prefix(int_hid):
    try:
        return struct.pack('>H', int_hid)
    except struct.error as e:
        raise ValueError('Hash ID out of range(0, 0xFFFF)') from e


class SetHash(Packet):
    """Unpacked [setHashfield] packet that announces and updates the sender's list of opt file IDs."""
    __slots__ = ['site', 'prefixes']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        self.site = c.btc('site')
        self.prefixes = set()

        bstr = c.strlen('hashfield_raw', 2000)
        for i in range(0, len(bstr), 2):
            rawh = bstr[i : i+2]
            if len(rawh) == 2:
                self.prefixes.add(rawh)


class FindHash(Packet):
    """Unpacked [findHashIds] packet that asks if the client knows any peer that has the said Hash IDs."""
    __slots__ = ['site', 'prefixes']

    def __init__(self, params = None):
        if not params:
            return
        c = Condition(params)

        self.site = c.btc('site')

        prefix_list = c.as_type('hash_ids', list)
        self.prefixes = set()
        for i in prefix_list:
            try:
                self.prefixes.add(hash_prefix(i))
            except (ValueError, TypeError):
                pass


class CheckPort(Packet):
    """Unpacked [actionCheckport] packet that asks the client to check the sender's port."""
    __slots__ = ['port']

    def __init__(self, params):
        if not params:
            return
        c = Condition(params)

        self.port = c.port('port')

class _DHT(Packet):
    """No Reference Implementation. No Spec.
    Unpacked [*dht*] packet used to collaboratively maintain a DHT."""
    def __init__(self, params):
        raise NotImplementedError()

class Response(Packet):
    """Response from peer."""
    def __init__(self, data):
        if not isinstance(data, dict):
            raise TypeError('Response must be a dictionary')
        self.data = data
        raise NotImplementedError()


cls_dict = {
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
    b'response': Response,
}



__all__ = [
    'unpack', 'unpack_stream',
    'GetFile', 'PEX', 'Update', 'Ping', 'Handshake', 'ListMod',
    'GetHash', 'SetHash', 'FindHash', 'CheckPort', 'Response',
]
