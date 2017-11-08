## `zerolib.integrity` - Working with data integrity

This module provides functions and classes for signing and verifying data with appropriate abstration.

It defines the following public functions and classes.


### Bitcoin key pair

`key_pair()`

Generate a public key and a secret key, returning a tuple containing `(publickey, secretkey)`. The first element is a PublicKey object. The second element is a SecretKey object.

`public_digest(publickey)`

Convert a public key to its `ripemd160(sha256())` digest, returning the raw 20-byte digest, as a bytes-like string.


### Bitcoin address

`compute_public_address(publickey)`

Convert a public key to a public Bitcoin address, returning a Base58Check-encoded string.

`compute_secret_address(secretkey)`

Convert a secret key to a secret Bitcoin address, returning a Base58Check-encoded string.

`bitcoin_address()`

Generate a public address and a secret address, returing a tuple `(public_address, secret_address)` containing two Base58Check-encoded strings.

`address_public_digest(address)`

Convert a public Bitcoin address to its `ripemd160(sha256())` digest, returning the raw 20-byte digest as a bytes-like string.

`decode_secret_key(address)`

Convert a secret Bitcoin address to a secret key, returning the secret key as a SecretKey object.


### Digital signature

`recover_public_key(signature, message)`

Parameters:

- `signature` - the raw signature, as a bytes-like string.
- `message` - the message, as a bytes-like string.

Recover the public key from the signature and the message, returning a PublicKey object. The recovered public key guarantees a correct signature.


`sign_data(secretkey, byte_string)`

Parameters:

- `secretkey` - the secret key, as a SecretKey object.
- `byte_string` - the message, as a bytes-like string.

Sign the message `byte_string` with `secretkey`, returing a 65-byte serialized signature as a bytes-like string.

The returned signature is compatible with ZeroNet (i.e. in the Electrum format)

`verify_data(key_digest, electrum_signature, byte_string)`

Parameters:

- `key_digest` - the raw `ripemd160(sha256())` digest of the public key.
- `electrum_signature` - the raw signature, a bytes-like string.
- `byte_string` - the message, a bytes-like string.

Verify if `electrum_signature` is the signature for the message `byte_string` and is produced with the secret counterpart of `key_digest`.

Raises SignatureError if it finds the signature forged or otherwise problematic.


### Message digest

`digest_bytes(data, algo='sha512')`

Compute the digest of `data`, a bytes-like object, returing a tuple containing `(digest, data_length)`.

`verify_digest_bytes(data, expect_digest, expect_size=None, algo='sha512')`

Verify if `data` have an expected digest `expect_digest` and has an expected size of `expect_size`. If `expect_size` is None, then data size will not be checked.

Raises DigestError if digest or size mismatches.

`digest_stream(stream, algo='sha512')`

Compute the digest of `stream`, a stream-like object, returning a tuple containing `(digest, stream_size)`.

`verify_digest_stream(stream, expect_digest, expect_size=None, algo='sha512')`

Verify if the data in `stream` have an expected digest `expect_digest` and has a size of `expect_size`. If `expect_size` is None, then stream size will not be checked.

Raises DigestError if digest or size mismatches.

`digest_file(path, hasher='sha512')`

Compute the digest of the file located at the given path. The parameter `path` should be a unicode string. Returns a tuple containing `(digest, stream_size)`.

`verify_digest_file(path, expect_digest, expect_size=None, algo='sha512')`

Verify if the file at `path` has an expected digest `expect_digest` and has a size of `expect_size`. If `expect_size` is None, then file size will not be checked.

Raises DigestError if digest or size mismatches.


### Utilities

`dumps(json_dict, compact=False)`

Pack the given dictionary to a JSON string, returning a unicode string. Note that the return value is NOT a bytes-like string.

If `compact` is True, the JSON string will be tightly packed.

If `compact` is False, the keys will be sorted and the JSON object will be pretty-printed.


### Exceptions

`class SignatureError(ValueError)`

`class DigestError(ValueError)`
