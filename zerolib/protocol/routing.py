default_score = 50

class Peer(object):
    __slots__ = ['address', 'last_seen', 'sites', 'dht', 'score']

    def __init__(self, address, last_seen, sites = None, dht = None, score = None):
        self.address = address
        self.last_seen = last_seen
        self.sites = sites or set()
        self.dht = dht
        self.score = score if score is not None else default_score

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    def __repr__(self):
        return 'Peer(%s)' % repr(self.address)



class Router:
    def __init__(self):
        self.peers = {}

    def put(self, peer, override=False):
        if (override) or (peer.address not in self.peers):
            self.peers[peer.address] = peer

    def get(self, key, default = None):
        return self.peers.get(key, default)

    def items(self):
        return self.peers.items()

    def values(self):
        return self.peers.values()

    def __getitem__(self, key):
        return self.peers[key]

    def __setitem__(self, key, value):
        return self.peers.__setitem__(key, value)

    def __delitem__(self, key):
        return self.peers.__delitem__(key)

    def __contains__(self, key):
        return (key in self.peers)

    def __iter__(self):
        return iter(self.peers)


__all__ = ['default_score', 'Peer', 'Router']
