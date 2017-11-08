import hashlib
import struct
from coincurve import PrivateKey, PublicKey
from base58 import b58encode_check, b58decode_check
from hmac import compare_digest

RECID_MIN = 0
RECID_MAX = 3
RECID_UNCOMPR = 27
LEN_COMPACT_SIG = 65

class SignatureError(ValueError):
    pass

def bitcoin_address():
    """Generate a public address and a secret address."""
    publickey, secretkey = key_pair()

    public_address = compute_public_address(publickey)
    secret_address = compute_secret_address(secretkey)

    return (public_address, secret_address)

def key_pair():
    """Generate a public key and a secret key."""
    secretkey = PrivateKey()
    publickey = PublicKey.from_secret(secretkey.secret)
    return (publickey, secretkey)

def compute_public_address(publickey):
    """Convert a public key to a public Bitcoin address."""
    public_plain = b'\x00' + public_digest(publickey)
    return b58encode_check(public_plain)

def compute_secret_address(secretkey):
    """Convert a secret key to a secret Bitcoin address."""
    secret_plain = b'\x80' + secretkey.secret
    return b58encode_check(secret_plain)

def public_digest(publickey):
    """Convert a public key to its ripemd160(sha256()) digest."""
    publickey_hex = publickey.format(compressed=False)
    return hashlib.new('ripemd160', hashlib.sha256(publickey_hex).digest()).digest()

def address_public_digest(address):
    """Convert a public Bitcoin address to its ripemd160(sha256()) digest."""
    public_plain = b58decode_check(address)
    if not public_plain.startswith(b'\x00') or len(public_plain) != 21:
        raise ValueError('Invalid public key digest')
    return public_plain[1:]

def _decode_bitcoin_secret(address):
    secret_plain = b58decode_check(address)
    if not secret_plain.startswith(b'\x80') or len(secret_plain) != 33:
        raise ValueError('Invalid secret key. Uncompressed keys only.')
    return secret_plain[1:]

def recover_public_key(signature, message):
    """Recover public key from signature and message.
    Recovered public key guarantees a correct signature"""
    return PublicKey.from_signature_and_message(signature, message)

def decode_secret_key(address):
    """Convert a secret Bitcoin address to a secret key."""
    return PrivateKey(_decode_bitcoin_secret(address))


def coincurve_sig(electrum_signature):
    # coincurve := r + s + recovery_id
    # where (0 <= recovery_id <= 3)
    # https://github.com/bitcoin-core/secp256k1/blob/0b7024185045a49a1a6a4c5615bf31c94f63d9c4/src/modules/recovery/main_impl.h#L35
    if len(electrum_signature) != LEN_COMPACT_SIG:
        raise ValueError('Not a 65-byte compact signature.')
    # Compute coincurve recid
    recid = electrum_signature[0] - RECID_UNCOMPR
    if not (RECID_MIN <= recid <= RECID_MAX):
        raise ValueError('Recovery ID %d is not supported.' % recid)
    recid_byte = int.to_bytes(recid, length=1, byteorder='big')
    return electrum_signature[1:] + recid_byte


def electrum_sig(coincurve_signature):
    # electrum := recovery_id + r + s
    # where (27 <= recovery_id <= 30)
    # https://github.com/scintill/bitcoin-signature-tools/blob/ed3f5be5045af74a54c92d3648de98c329d9b4f7/key.cpp#L285
    if len(coincurve_signature) != LEN_COMPACT_SIG:
        raise ValueError('Not a 65-byte compact signature.')
    # Compute Electrum recid
    recid = coincurve_signature[-1] + RECID_UNCOMPR
    if not (RECID_UNCOMPR + RECID_MIN <= recid <= RECID_UNCOMPR + RECID_MAX):
        raise ValueError('Recovery ID %d is not supported.' % recid)
    recid_byte = int.to_bytes(recid, length=1, byteorder='big')
    return recid_byte + coincurve_signature[0:-1]

def sign_data(secretkey, byte_string):
    """Sign [byte_string] with [secretkey].
    Return serialized signature compatible with Electrum (ZeroNet)."""
    # encode the message
    encoded = _zero_format(byte_string)
    # sign the message and get a coincurve signature
    signature = secretkey.sign_recoverable(encoded)
    # reserialize signature and return it
    return electrum_sig(signature)

def verify_data(key_digest, electrum_signature, byte_string):
    """Verify if [electrum_signature] of [byte_string] is correctly signed and
    is signed with the secret counterpart of [key_digest].
    Raise SignatureError if the signature is forged or otherwise problematic."""
    # reserialize signature
    signature = coincurve_sig(electrum_signature)
    # encode the message
    encoded = _zero_format(byte_string)
    # recover full public key from signature
    # "which guarantees a correct signature"
    publickey = recover_public_key(signature, encoded)

    # verify that the message is correctly signed by the public key
    # correct_sig = verify_sig(publickey, signature, encoded)

    # verify that the public key is what we expect
    correct_key = verify_key(publickey, key_digest)

    if not correct_key:
        raise SignatureError('Signature is forged!')

def verify_sig(publickey, signature, byte_string):
    return publickey.verify(signature, byte_string)

def verify_key(publickey, key_digest):
    return compare_digest(key_digest, public_digest(publickey))


__all__ = [
    'SignatureError',
    'bitcoin_address', 'key_pair', 'compute_public_address', 'compute_secret_address',
    'public_digest', 'address_public_digest', 'recover_public_key', 'decode_secret_key',
    'sign_data', 'verify_data',
]


# Electrum, what the heck?!

def bchr(i):
    return struct.pack('B', i)

def _zero_encode(val, base, minlen=0):
    base, minlen = int(base), int(minlen)
    code_string = b''.join([bchr(x) for x in range(256)])
    result = b''
    while val > 0:
        index = val % base
        result = code_string[index:index + 1] + result
        val //= base
    return code_string[0:1] * max(minlen - len(result), 0) + result

def _zero_int(x):
    x = int(x)
    if x < 253:
        return bchr(x)
    elif x < 65536:
        return bchr(253) + _zero_encode(x, 256, 2)[::-1]
    elif x < 4294967296:
        return bchr(254) + _zero_encode(x, 256, 4)[::-1]
    else:
        return bchr(255) + _zero_encode(x, 256, 8)[::-1]


def _zero_magic(message):
    return b'\x18Bitcoin Signed Message:\n' + _zero_int(len(message)) + message

def _zero_format(message):
    padded = _zero_magic(message)
    return hashlib.sha256(padded).digest()
