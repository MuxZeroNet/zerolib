import unittest
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

    def test_packet_inject(self):
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
            n = state_machine.next_number()
            self.assertFalse(n in id_set)
            id_set.add(n)
