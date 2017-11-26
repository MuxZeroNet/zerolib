from threading import Lock
from contextlib import contextmanager

class RWLock(object):
    __slots__ = ('lock_ct', 'lock_r', 'lock_q', 'num_readers')

    def __init__(self):
        self.lock_ct = Lock()
        self.lock_r = Lock()
        self.lock_q = Lock()
        self.num_readers = 0

    def begin_read(self):
        with self.lock_q:
            with self.lock_ct:
                if self.num_readers == 0:
                    self.lock_r.acquire()
                self.num_readers += 1

    def begin_write(self):
        with self.lock_q:
            self.lock_r.acquire()

    def end_read(self):
        with self.lock_ct:
            if self.num_readers == 0:
                raise ValueError('Lock released too many times')
            self.num_readers -= 1
            if self.num_readers == 0:
                self.lock_r.release()

    def end_write(self):
        self.lock_r.release()


    def acquire(self, mode):
        if mode == 'r':
            self.begin_read()
            return True
        elif mode == 'w':
            self.begin_write()
            return True
        else:
            raise ValueError('Wrong mode')

    def release(self, mode):
        if mode == 'r':
            self.end_read()
        elif mode == 'w':
            self.end_write()
        else:
            raise ValueError('Wrong mode')

    @contextmanager
    def reader(self):
        self.acquire('r')
        yield self
        self.release('r')

    @contextmanager
    def writer(self):
        self.acquire('w')
        yield self
        self.release('w')
