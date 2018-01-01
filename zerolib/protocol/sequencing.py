from collections import OrderedDict, namedtuple
from .packets import response_packets, RespFile
from os import urandom

Info = namedtuple('Info', ['cls', 'attr_dict'])

class PacketInterp(object):
    __slots__ = ['sequence']
    capacity = 10

    def __init__(self):
        self.sequence = OrderedDict()

    @staticmethod
    def new_id():
        return int.from_bytes(urandom(4), byteorder='big')

    def __repr__(self):
        return '<%s object seq_len=%d out of %d>' % (self.__class__.__name__, len(self.sequence), self.capacity)

    def register(self, packet):
        if not hasattr(packet, 'response_cls'):
            return

        self.remove_orphan()
        attr_dict = self.__class__.copy_attrs(packet)

        identifier = (packet.sender, packet.req_id)
        self.sequence[identifier] = Info(packet.response_cls, attr_dict)

    def interpret(self, packet):
        if not packet.__class__ in response_packets:
            return

        cls, attr_dict = self.sequence.pop((packet.sender, packet.req_id))
        if not isinstance(packet, cls):
            raise TypeError('Sequence number %d: expects a %s packet, not %s' %
                (packet.req_id, cls.__name__, packet.__class__.__name__))
        if attr_dict:
            if isinstance(packet, RespFile):
                self.__class__.inject_respfile_attrs(packet, attr_dict)
            else:
                self.__class__.inject_attrs(packet, attr_dict)

    @staticmethod
    def copy_attrs(packet):
        slots = getattr(packet, 'copy_attrs', None)
        if not slots:
            return None

        class AttrDict(object):
            __slots__ = slots

            def items(self):
                for k in self.__slots__:
                    yield (k, getattr(self, k))

            def __repr__(self):
                return '<%s(%s)>' % (
                    self.__class__.__name__,
                    ', '.join((k + '=' + repr(getattr(self, k)) for k in self.__slots__))
                )

        attr_dict = AttrDict()
        for key in slots:
            setattr(attr_dict, key, getattr(packet, key))
        return attr_dict

    @staticmethod
    def inject_attrs(response, attr_dict):
        for (k, v) in attr_dict.items():
            setattr(response, k, v)

    @staticmethod
    def inject_respfile_attrs(response, attr_dict):
        expected, actual = attr_dict.offset, response.offset
        if expected != actual:
            raise ValueError('Non-consecutive file body. Offset should be %r, not %r' % (expected, actual))

        expected, actual = attr_dict.total_size, response.total_size
        if (expected is not None) and (expected != actual):
            raise ValueError('File size does not match - should be %r, found %r' % (expected, actual))

        for (k, v) in attr_dict.items():
            if k not in ('offset', 'total_size'):
                setattr(response, k, v)

    def remove_orphan(self):
        while len(self.sequence) >= self.capacity:
            self.sequence.popitem(last=False)


__all__ = ['PacketInterp']
