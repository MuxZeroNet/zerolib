import unittest
from storage import RWLock
from timeout_decorator import timeout
from timeout_decorator.timeout_decorator import TimeoutError as ExpectedTimeout

def assert_timeout(seconds):
    def decorator(func):
        def f(self, *args, **kwargs):
            func_timeout = timeout(seconds)(func)
            with self.assertRaises(ExpectedTimeout):
                func_timeout(self, *args, **kwargs)
        return f
    return decorator

class TestRWLock(unittest.TestCase):
    @timeout(3)
    def test_readers(self):
        rwlock = RWLock()
        for i in range(10):
            rwlock.acquire('r')
        for i in range(10):
            rwlock.release('r')

        with self.assertRaises(ValueError):
            rwlock.release('r')

    @timeout(3)
    def test_rw(self):
        rwlock = RWLock()

        rwlock.acquire('w')
        rwlock.release('w')
        for i in range(10):
            rwlock.acquire('r')
        for i in range(10):
            rwlock.release('r')
        rwlock.acquire('w')
        rwlock.release('w')

    @assert_timeout(1)
    def test_context_rw(self):
        rwlock = RWLock()

        with rwlock.reader():
            with rwlock.writer():
                raise AssertionError('Should not enter')

    @assert_timeout(1)
    def test_context_wr(self):
        rwlock = RWLock()

        with rwlock.writer():
            with rwlock.reader():
                raise AssertionError('Should not enter')

    @assert_timeout(1)
    def test_context_ww(self):
        rwlock = RWLock()

        with rwlock.writer():
            with rwlock.writer():
                raise AssertionError('Should not enter')
