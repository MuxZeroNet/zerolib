import unittest
from ipaddress import IPv4Address
from zerolib.protocol.packets import *
from zerolib.protocol.packets import hash_set
from zerolib.protocol.sequencing import *

class MockString(bytes):
    def __init__(self, length):
        self.length = length
    def __len__(self):
        return self.length
    def __repr__(self):
        return '<%s len=%d>' % (self.__class__.__name__, self.length)


class TestStaticFunc(unittest.TestCase):
    def test_hash_set(self):
        bstr = b'11223344556677889900aaAAbbBBccddCDEFCDCDaaAA1122'
        result = frozenset({b'11', b'22', b'33', b'44', b'55', b'66', b'77',
            b'88', b'99', b'00', b'aa', b'AA', b'bb', b'BB', b'cc', b'dd', b'CD', b'EF'})
        self.assertEquals(hash_set(bstr), result)
        self.assertEquals(hash_set(b''), frozenset({}))

    def test_hash_set_exceptions(self):
        with self.assertRaises(ValueError):
            hash_set(MockString(9999))
        with self.assertRaises(ValueError):
            hash_set(MockString(3))

class TestUnpack(unittest.TestCase):
    def test_unpack_RespHashSet(self):
        packet = unpack_dict({b'cmd': b'response', b'to': 0, b'hashfield_raw': b'\x10\x11ABCDef12'})
        hashes = {b'\x10\x11', b'12', b'ef', b'AB', b'CD'}
        self.assertIsInstance(packet, RespHashSet)
        self.assertEquals(set(iter(packet)), hashes)
        self.assertTrue(b'\x10\x11' in packet)
        self.assertFalse(b'\xA0\xB1' in packet)

    def test_attr_inject(self):
        request = unpack_dict({b'req_id': 0, b'cmd': b'actionCheckport', b'params': {b'port': 15441}})
        response = unpack_dict({b'cmd': b'response', b'to': 0, b'status': b'open', b'ip_external': b'1.2.3.4'})
        self.assertIsInstance(request, CheckPort)
        self.assertIsInstance(response, RespPort)
        self.assertEquals(request.port, 15441)
        self.assertEquals(response.open, True)
        with self.assertRaises(AttributeError):
            request.open
        with self.assertRaises(AttributeError):
            response.port

        state_machine = PacketInterp()
        state_machine.register(request)
        state_machine.interpret(response)
        self.assertEquals(response.port, 15441)
        self.assertEquals(response.open, True)
        self.assertEquals(request.port, 15441)

    def test_packet_id(self):
        state_machine = PacketInterp()
        id_set = set()
        for i in range(100):
            n = PacketInterp.new_id()
            self.assertFalse(n in id_set)
            id_set.add(n)

def setup_packets(key):
    def decorator(func):
        def f(self, *args):
            request = unpack_dict(self.request_dict)
            response = self.responses[key]
            state_machine = PacketInterp()
            state_machine.register(request)
            return func(self, state_machine, request, response, *args)
        return f
    return decorator

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.request_dict = {b'cmd': b'getFile', b'req_id': 1, b'params': {b'site': b'122tqTo5jTsZfF4xFodhM54b5HUkeVQL4E', b'inner_path': b'content.json', b'location': 0}}
        self.endpoint = (IPv4Address('127.0.0.1'), 54321)
        self.responses = {
            'request': self.request_dict,
            'legit': {b'cmd': b'response', b'to': 1, b'body': b'content.json content', b'location': 19, b'size': 20},
            'error': {b'cmd': b'response', b'to': 1, b'error': 'git rekt'},
            'unknown': {b'cmd': b'response', b'to': 2, b'body': b'content.json content', b'location': 19, b'size': 20},
        }

    @setup_packets('legit')
    def test_legit(self, state_machine, request, response):
        pass

    @setup_packets('request')
    def test_request(self, state_machine, request, response):
        pass

    @setup_packets('error')
    def test_error(self, state_machine, request, response):
        pass

    @setup_packets('unknown')
    def test_unknown(self, state_machine, request, response):
        pass
