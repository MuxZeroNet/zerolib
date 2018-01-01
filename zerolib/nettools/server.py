from ..protocol.packets import *
from ..protocol import PacketInterp
from threading import Lock

func_routing = {
    Ping: 'ping',
    Pong: 'pong',
    Predicate: 'predicate',
    Handshake: 'handshake',
    ACK: 'ack',
    GetFile: 'get_file',
    RespFile: 'resp_file',
    PEX: 'pex',
    RespPEX: 'resp_pex',
    Update: 'update',
    ListMod: 'list_mod',
    RespMod: 'resp_mod',
    GetHash: 'get_hash',
    SetHash: 'set_hash',
    FindHash: 'find_hash',
    RespHashSet: 'resp_hash_set',
    RespHashDict: 'resp_hash_dict',
    CheckPort: 'check_port',
    RespPort: 'resp_port',
    GetPieceStatus: 'get_piece_status',
    SetPieceStatus: 'set_piece_status',
    RespPieceDict: 'resp_piece_dict',
}

class BaseServer(object):
    __default_funcs = frozenset(func_routing.values())

    def __init__(self):
        self.interpreter = PacketInterp()
        self.lock_interp = Lock()

    def handle(self, packet):
        func = getattr(self, func_routing[packet.__class__])
        with self.lock_interp:
            self.interpreter.interpret(packet)
        return func(packet)

    def send_to(self, packet, dest):
        with self.lock_interp:
            self.interpreter.register(packet)

    def __nop(self, packet):
        return None

    def __getattr__(self, name):
        if name in self.__class__.__default_funcs:
            return self.__nop
        else:
            return super().__getattr__(name)

    def ping(self, packet):
        return Pong()


__all__ = ['BaseServer']
