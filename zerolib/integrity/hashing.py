import hashlib
import json
from hmac import compare_digest

class DigestError(ValueError):
    pass

class SHA512256Hasher:
    def __init__(self, data=b''):
        self.hasher = hashlib.sha512(data)

    def update(self, data):
        return self.hasher.update(data)

    def digest(self):
        return self.hasher.digest()[0:32]

hasher_dict = {
    'sha512': SHA512256Hasher,  # but it really means SHA-512/256
}

def digest_bytes(data, algo='sha512'):
    """Compute the digest of the given bytes. Returns (digest, data_length)"""
    return (hasher_dict[algo](data).digest(), len(data))

def digest_stream(stream, algo='sha512'):
    """Compute the digest of the given stream. Returns (digest, stream_size)"""
    size = 0
    hasher = hasher_dict[algo]()
    data = stream.read(4096)
    while data:
        hasher.update(data)
        size += len(data)
        data = stream.read(4096)
    return (hasher.digest(), size)

def digest_file(path, algo='sha512'):
    """Compute the digest of the file at the given path. Returns (digest, stream_size)"""
    with open(path, 'rb') as f:
        return digest_stream(f, algo)

def verify_digest_bytes(data, expect_digest, expect_size=None, algo='sha512'):
    """Verify if [data] corresponds to [expect_digest] and has a size of [expect_size].
    If [expect_size] is None, data size will not be checked.
    Raise DigestError if digest or size mismatches.
    """
    if expect_size is not None and len(data) != expect_size:
        raise DigestError('Size does not match. %d != %d' % (len(data), expect_size))

    real_digest, _size = digest_bytes(data, algo)
    if not compare_digest(real_digest, expect_digest):
        raise DigestError('Digest does not match.')

def verify_digest_stream(stream, expect_digest, expect_size=None, algo='sha512'):
    """Verify if data in [stream] corresponds to [expect_digest] and has a size of [expect_size].
    If [expect_size] is None, stream size will not be checked.
    Raise DigestError if digest or size mismatches.
    """
    STEP = 4096
    size = 0
    hasher = hasher_dict[algo]()

    data = stream.read(STEP)
    while data:
        hasher.update(data)
        if expect_size is not None:
            size += len(data)
            if size > expect_size:
                raise DigestError('Size exceeds expected size. %d+ > %d' % (size, expect_size))
        data = stream.read(STEP)

    if (expect_size is not None) and (size != expect_size):
        raise DigestError('Size mismatches. %d != %d' % (size, expect_size))

    real_digest = hasher.digest()
    if not compare_digest(real_digest, expect_digest):
        raise DigestError('Digest mismatches. %s != %s' % (repr(real_digest), repr(expect_digest)))


def verify_digest_file(path, expect_digest, expect_size=None, algo='sha512'):
    """Verify if the file at [path] corresponds to [expect_digest] and has a size of [expect_size].
    If [expect_size] is None, file size will not be checked.
    Raise DigestError if digest or size mismatches.
    """
    with open(path, 'rb') as f:
        return verify_digest_stream(f, expect_digest, expect_size, algo)


def dumps(json_dict, compact=False):
    """Pack the given dictionary to a JSON string.
    Returns the JSON string. Note that the return value is NOT a byte string.
    If compact is True, the JSON string will be tightly packed.
    If compact is False, the keys will be sorted and the JSON string will be indented."""
    if not compact:
        return json.dumps(json_dict, sort_keys=True, indent=1)
    else:
        return json.dumps(json_dict, separators=(',', ':'))


__all__ = [
    'DigestError',
    'digest_bytes', 'digest_stream', 'digest_file',
    'verify_digest_bytes', 'verify_digest_stream', 'verify_digest_file',
    'dumps',
]
