from collections import namedtuple

class Conn(object):
    __slots__ = ['socket', 'freq']

    def __init__(self, socket, freq=0):
        self.socket = socket
        self.freq = freq

    def __iter__(self):
        yield self.socket
        yield self.freq

    def __repr__(self):
        return '<Conn fd=%d, freq=%d>' % (self.socket.fileno(), self.freq)


class Connections(object):
    __slots__ = ['capacity', 'clean_func', 'sessions']

    def __init__(self, capacity=200, clean_func = None):
        self.sessions = {}
        self.capacity = capacity

    def register(self, dest, socket):
        self.remove_unused()
        if dest not in self.sessions:
            self.sessions[dest] = Conn(socket)

    def remove_unused(self):
        if len(self.sessions) >= self.capacity:
            if self.clean_func:
                blacklist = self.clean_func(self.sessions.keys())
                self.remove_peers(blacklist)

            real_len, new_len = len(self.sessions), int(self.capacity * 0.8)
            if real_len > new_len:
                bottom_line = real_len - new_len
                items = sorted(self.sessions.items(), key=lambda x: x[1].freq)
                for (k, v) in items[0:bottom_line]:
                    del self.sessions[k]

    def remove_peers(self, blacklist):
        for key in blacklist:
            del self.sessions[key]

    def __getitem__(self, key):
        item = self.sessions[key]
        item.freq += 1
        return item

    def __delitem__(self, key):
        return self.sessions.__delitem__(key)

    def __iter__(self):
        return iter(self.sessions)

    def __len__(self):
        return len(self.sessions)

    def __contains__(self, key):
        return key in self.sessions

__all__ = ['Connections']
