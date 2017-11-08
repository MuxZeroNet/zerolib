import hashlib
import unittest
import json
import os
from base64 import b16encode, b16decode, b64encode, b64decode
from coincurve import PublicKey, PrivateKey
import integrity


class TestBitcoin(unittest.TestCase):
    secret_address = '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'
    secret = b'0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D'

    public_address = '16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM'
    public_digest = b'010966776006953D5567439E5E39F86A0D273BEE'
    secret_2 = b'18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725'


    def test_decode_secret(self):
        secretkey = integrity.decode_secret_key(self.secret_address)
        self.assertEqual(self.secret, b16encode(secretkey.secret))

    def test_encode_secret(self):
        secretkey = PrivateKey(secret=b16decode(self.secret))
        self.assertEqual(self.secret_address, integrity.compute_secret_address(secretkey))

    def test_decode_public(self):
        self.assertEqual(self.public_digest, b16encode(integrity.address_public_digest(self.public_address)))

    def test_encode_public(self):
        secretkey = PrivateKey(secret=b16decode(self.secret_2))
        publickey = PublicKey.from_secret(secretkey.secret)

        self.assertEqual(self.public_address, integrity.compute_public_address(publickey))
        self.assertEqual(self.public_digest, b16encode(integrity.public_digest(publickey)))


class TestSig(unittest.TestCase):
    def setUp(self):
        self.secretkey = PrivateKey(b16decode(b'18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725'))

    def test_serialization(self):
        sig = integrity.sign_data(self.secretkey, b'Hello')
        self.assertEqual(len(sig), 65)
        self.assertTrue(27 <= sig[0] <= 30)

    def test_simple(self):
        with open(os.path.dirname(__file__) + '/test_data/sig_simple.txt', 'rb') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                msg, signature, address, secret = line.split(b' ')
                signature = b64decode(signature)

                key_digest = integrity.address_public_digest(address)
                integrity.verify_data(key_digest, signature, msg)
                with self.assertRaises(integrity.SignatureError):
                    integrity.verify_data(key_digest, signature, msg + os.urandom(10))

                if secret != b'*':
                    secretkey = integrity.decode_secret_key(secret)
                    test_sig = integrity.sign_data(secretkey, msg)
                    self.assertEqual(test_sig, signature)


def invalid_sizes(real_size):
    return (0, -1, -real_size, real_size + 1, real_size - 1,
        real_size - 23, real_size + 37, real_size - 111, real_size + 222)


class TestHash(unittest.TestCase):
    hash_tor = b16decode(b'96b848abdadd7f3a1ca2c536c8920916f28c0c99e0a5671d88dfb9434eb21136'.upper())
    hash_whx = b16decode(b'79144d2a7bbff9ca02541784f5d8e2efa6b72489e8ad76b4d9ed8edc302235e8'.upper())
    hash_cnt = b16decode(b'691b1b702771532e6294dc24f8bd7239f0daa638b2b05a08879738887aa4ac4d'.upper())

    path_tor = os.path.dirname(__file__) + '/test_data/Tor.png'
    path_whx = os.path.dirname(__file__) + '/test_data/Whonix_Logo.png'
    path_cnt = os.path.dirname(__file__) + '/test_data/content.json'
    path_srl = os.path.dirname(__file__) + '/test_data/serialize.json'

    size_tor = 6258
    size_whx = 14848
    size_cnt = 3286
    size_srl = 1316


    def test_hash_bytes(self):
        data = b'Test SHA-512/256 !!! ... 0'
        h = b16decode(b'a5a12e8548b7ba0565159d5f6171c3acd93f2ae9290090e283c6de4ed282ce61'.upper())
        self.assertEqual(integrity.digest_bytes(data), (h, 26))

        integrity.verify_digest_bytes(data, h)
        integrity.verify_digest_bytes(data, h, len(data))

        for fake_size in invalid_sizes(len(data)):
            with self.assertRaises(integrity.DigestError):
                integrity.verify_digest_bytes(data, h, fake_size)

    def test_hash_stream(self):
        with open(self.path_tor, 'rb') as f:
            self.assertEqual(integrity.digest_stream(f), (self.hash_tor, self.size_tor))

        with open(self.path_tor, 'rb') as f:
            integrity.verify_digest_stream(f, self.hash_tor, self.size_tor)

        with open(self.path_tor, 'rb') as f:
            integrity.verify_digest_stream(f, self.hash_tor)

        with open(self.path_tor, 'rb') as f:
            with self.assertRaises(integrity.DigestError):
                integrity.verify_digest_stream(f, self.hash_tor, self.size_tor + 1)

        with open(self.path_tor, 'rb') as f:
            with self.assertRaises(integrity.DigestError):
                integrity.verify_digest_stream(f, os.urandom(32), self.size_tor)



    def test_hash_file(self):
        self._test_hash_file(self.path_tor, self.hash_tor, self.size_tor)
        self._test_hash_file(self.path_whx, self.hash_whx, self.size_whx)
        self._test_hash_file(self.path_cnt, self.hash_cnt, self.size_cnt)

    def _test_hash_file(self, path_file, hash_file, size_file):
        self.assertEqual(integrity.digest_file(path_file), (hash_file, size_file))
        integrity.verify_digest_file(path_file, hash_file)
        integrity.verify_digest_file(path_file, hash_file, size_file)

        for fake_size in invalid_sizes(size_file):
            with self.assertRaises(integrity.DigestError):
                integrity.verify_digest_file(path_file, hash_file, fake_size)

        with self.assertRaises(integrity.DigestError):
            integrity.verify_digest_file(path_file, os.urandom(32), None)
        with self.assertRaises(integrity.DigestError):
            integrity.verify_digest_file(path_file, os.urandom(32), size_file)


    def test_json(self):
        with open(self.path_srl, 'r', encoding='utf-8') as f:
            d = json.load(f)
            self.assertTrue(self.size_srl > len(integrity.dumps(d, compact=True)))
