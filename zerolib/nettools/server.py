from ..protocol.packets import *

func_routing = {
    Ping: 'ping',
    Pong: 'pong',
    Predicate: 'predicate',
    Handshake: 'handshake',
    OhHi: 'oh_hi',
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
    __slots__ = ()

    def route(self, packet):
        func = getattr(self, func_routing[packet.__class__])
        return func(packet)

    def ping(self, packet):
        return Pong()

    def pong(self, packet):
        pass

    def predicate(self, packet):
        pass

    def handshake(self, packet):
        pass

    def oh_hi(self, packet):
        pass

    def get_file(self, packet):
        pass

    def resp_file(self, packet):
        pass

    def pex(self, packet):
        pass

    def resp_pex(self, packet):
        pass

    def update(self, packet):
        pass

    def list_mod(self, packet):
        pass

    def resp_mod(self, packet):
        pass

    def get_hash(self, packet):
        pass

    def set_hash(self, packet):
        pass

    def find_hash(self, packet):
        pass

    def resp_hash_set(self, packet):
        pass

    def resp_hash_dict(self, packet):
        pass

    def check_port(self, packet):
        pass

    def resp_port(self, packet):
        pass

    def get_piece_status(self, packet):
        pass

    def set_piece_status(self, packet):
        pass

    def resp_piece_dict(self, packet):
        pass


__all__ = ['BaseServer']
