import unittest
import protocol.sanitizer as sn
from protocol.sanitizer import opt

def raw_getter(self, key):
    return self.p[bytes(key, 'ascii')]

def str_getter(self, key):
    return self.p[bytes(key, 'ascii')].decode('ascii')


def accept_item(keys, valgetter):
    def decorator(assert_func):
        def f(self):
            print(keys)
            for k in keys:
                assert_func(self, k, valgetter(self, k))
        return f
    return decorator

def func_raises(error_cls, keys):
    def decorator(test_func):
        def f(self):
            print(keys)
            for k in keys:
                with self.assertRaises(error_cls):
                    test_func(self, k)
        return f
    return decorator


class TestCondition(unittest.TestCase):
    def setUp(self):
        self.p = {
            b'none': None,

            b'n1.1': 0,
            b'n1.2': 1024,
            b'n1.3': -1,
            b'n1.4': 0xFFFF,
            b'n2.1': b'\xFF',
            b'n2.2': '\u00FF',
            b'n2.3': [2048],

            b'port1.1': 8080,
            b'port1.2': 15441,
            b'port1.3': 0,
            b'port1.4': 65535,
            b'port2.1': 999999,
            b'port2.2': -1,
            b'port2.3': 65536,
            b'port3.1': [8080],
            b'port3.2': b'8080',

            b'str1': b'',
            b'str2': b'a',
            b'str3': b'\x00\x01\x02',
            b'str4': b'A'*10,

            b'onion1.1': b'3g2upl4pq6kufc4m',
            b'onion1.2': b'BlockChainbdgpzk',
            b'onion2.1': b'.onion',
            b'onion2.2': b'zeronet.io',
            b'onion2.3': b'abcde12345',
            b'onion2.4': b'k1mj0ngun[.]pk',
            b'onion2.5': b'zzz.i2p',
            b'onion2.6': b'127.0.0.1',

            b'btc1.1': b'122tqTo5jTsZfF4xFodhM54b5HUkeVQL4E',
            b'btc1.2': b'1MeFqFfFFGQfa1J3gJyYYUvb5Lksczq7nH',
            b'btc1.3': b'1111112222222222222222222222233333',
            b'btc2.1': b'5KaArUZdHSgjJy6h2e91Xf6j5eDi6notJmyvR7y7qBAxNbGDunv',
            b'btc2.2': b'BM-2cUUs97JykF1wNx9udk8om69EzmM4dwGfJ',
            b'btc2.3': b'44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A',
            b'btc2.4': b'N1KHAL5C1CRzy58NdJwp1tbLze3XrkFxx9',
            b'btc2.5': b'',

            b'path1.1': b'index.HTML',
            b'path1.2': b'static/style.css',
            b'path1.3': b'/etc/passwd',  # will be converted into `etc/passwd`
            b'path1.4': b'./content.json',
            b'path2.1': b'lec*.pdf',
            b'path2.2': b'backslash\\not.allowed',
            b'path2.3': b'static/img.txt\x00.html',
            b'path2.4': b'C:/WINDOWS/notepad.exe',
            b'path2.5': b'./././././////./././..//////././././././../././././././././/////./content.json',
            b'path2.6': b'a' * 300,
        }
        self.c = sn.Condition(self.p)


    # range tests
    @accept_item(('n1.1', 'n1.2'), raw_getter)
    def test_range(self, key, val):
        self.assertEquals(self.c.range(key, (0, 1024)), val)
        self.assertEquals(self.c.range(key, (-1, 1025)), val)

    @func_raises(ValueError, ('n1.3', 'n1.4'))
    def test_range_valueerror(self, key):
        self.c.range(key, (0, 0xFFFE))

    @func_raises(TypeError, ('none', 'n2.1', 'n2.2', 'n2.3'))
    def test_range_typeerror(self, key):
        self.c.range(key, (0, 2048))


    # port tests
    @accept_item(('port1.1', 'port1.2', 'port1.3', 'port1.4'), raw_getter)
    def test_port(self, key, val):
        self.assertEquals(self.c.port(key), val)

    @func_raises(ValueError, ('port2.1', 'port2.2', 'port2.3'))
    def test_port_valueerror(self, key):
        self.c.port(key)

    @func_raises(TypeError, ('none', 'port3.1', 'port3.2'))
    def test_port_typeerror(self, key):
        self.c.port(key)


    # strlen tests
    @accept_item(('str1',), raw_getter)
    def test_strlen(self, key, val):
        self.assertEquals(self.c.strlen(key, 0), val)

    @accept_item(('str1', 'str2'), raw_getter)
    def test_strlen2(self, key, val):
        self.assertEquals(self.c.strlen(key, 1), val)
        self.assertEquals(self.c.strlen(key, 2), val)

    @accept_item(('str1', 'str2', 'str3'), raw_getter)
    def test_strlen3(self, key, val):
        for l in (3, 4, 10):
            self.assertEquals(self.c.strlen(key, l), val)

    @accept_item(('str1', 'str2', 'str3', 'str4'), raw_getter)
    def test_strlen4(self, key, val):
        for l in (10, 11, 65535):
            self.assertEquals(self.c.strlen(key, l), val)

    @func_raises(ValueError, ('str2',))
    def test_strlen_valueerror(self, key):
        self.c.strlen(key, 0)

    @func_raises(ValueError, ('str3', 'str4'))
    def test_strlen_valueerror2(self, key):
        self.c.strlen(key, 2)

    @func_raises(TypeError, ('none', 'n1.1', 'port1.1'))
    def test_strlen_valueerror2(self, key):
        self.c.strlen(key, 2)


    # onion tests
    @accept_item(('onion1.1', 'onion1.2'), str_getter)
    def test_onion(self, key, val):
        self.assertEquals(self.c.onion(key), val)

    @func_raises(ValueError, ('onion2.1', 'onion2.2', 'onion2.3', 'onion2.4', 'onion2.5', 'onion2.6'))
    def test_onion_valueerror(self, key):
        self.c.onion(key)

    @func_raises(TypeError, ('none', 'n1.1', 'port1.1'))
    def test_onion_typeerror(self, key):
        self.c.onion(key)


    # btc tests
    @accept_item(('btc1.1', 'btc1.2', 'btc1.3'), str_getter)
    def test_btc(self, key, val):
        self.assertEquals(self.c.btc(key), val)

    @func_raises(ValueError, ('btc2.1', 'btc2.2', 'btc2.3', 'btc2.4', 'btc2.5'))
    def test_btc_valueerror(self, key):
        self.c.btc(key)

    @func_raises(ValueError, ('onion2.1', 'onion2.2', 'onion2.3', 'onion2.4', 'onion2.5'))
    def test_btc_valueerror2(self, key):
        self.c.btc(key)

    @func_raises(TypeError, ('none', 'n1.1', 'port1.1'))
    def test_btc_typeerror(self):
        self.c.btc(key)


    # inner path tests
    @accept_item(('path1.1', 'path1.2', 'path1.3', 'path1.4'), str_getter)
    def test_path(self, key, val):
        u_path = self.c.inner(key)
        self.assertIsInstance(u_path, str)
        self.assertTrue(not u_path.startswith('/'))
        self.assertTrue(('/' + val).endswith('/' + u_path))
        self.assertTrue('\\' not in u_path)
        self.assertTrue('..' not in u_path)
        self.assertTrue(len(u_path) <= 255)

    @func_raises(ValueError, ('path2.1', 'path2.2', 'path2.3', 'path2.4', 'path2.5', 'path2.6'))
    def test_path_valueerror(self, key):
        self.c.inner(key)

    @func_raises(TypeError, ('none', 'n1.1', 'port1.1'))
    def test_path_valueerror(self, key):
        self.c.inner(key)


    # opt tests
    @accept_item(('path1.1',), str_getter)
    def test_opt(self, key, val):
        self.assertEquals(self.c.inner(opt(key)), val)

    def test_opt_nonexistent(self):
        self.assertEquals(self.c.inner(opt('path_nonexistent')), None)
        with self.assertRaises(ValueError):
            self.c.inner(opt('path2.1'))
        with self.assertRaises(KeyError):
            self.c.inner('path_nonexistent')
