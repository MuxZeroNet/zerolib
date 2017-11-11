``zerolib.integrity`` - Working with data integrity
===================================================

This module provides functions and classes for signing and verifying data with appropriate abstration.

It defines the following public functions and classes.


Bitcoin key pair
----------------

.. function:: key_pair()

    Generate a public key and a secret key, returning a tuple containing ``(publickey, secretkey)``.
    
    :rtype: (PublicKey, SecretKey)

.. function:: public_digest(publickey)

    Convert a public key to its ``ripemd160(sha256())`` digest, returning the raw 20-byte digest.
    
    :rtype: bytes


Bitcoin address
---------------

.. function:: compute_public_address(publickey)

    Convert a public key to a public Bitcoin address, returning a Base58Check-encoded string.
    
    :rtype: str

.. function:: compute_secret_address(secretkey)

    Convert a secret key to a secret Bitcoin address, returning a Base58Check-encoded string.
    
    :rtype: str

.. function:: bitcoin_address()

    Generate a public address and a secret address, returing a tuple ``(public_address, secret_address)`` containing two Base58Check-encoded strings.
    
    :rtype: (str, str)

.. function:: address_public_digest(address)

    Convert a public Bitcoin address to its ``ripemd160(sha256())`` digest, returning the raw 20-byte digest.
    
    :rtype: bytes

.. function:: decode_secret_key(address)

    Convert a secret Bitcoin address to a secret key, returning the secret key as a SecretKey object.
    
    :rtype: SecretKey


Digital signature
-----------------

.. function:: recover_public_key(signature, message)

    Recover the public key from the signature and the message, returning a PublicKey object. The recovered public key guarantees a correct signature.
    
    :param bytes signature: the raw signature.
    :param bytes message: the message.
    :return: a PublicKey object.


.. function:: sign_data(secretkey, byte_string)
    
    Sign the message ``byte_string`` with ``secretkey``, returing a 65-byte serialized signature as a bytes-like string. The returned signature is compatible with ZeroNet (i.e. in the Electrum format)

    :param SecretKey secretkey: the secret key.
    :param bytes byte_string: the message.
    :return: a 65-byte binary string.


.. function:: verify_data(key_digest, electrum_signature, byte_string)

    Verify if ``electrum_signature`` is the signature for the message ``byte_string`` and is produced with the secret counterpart of ``key_digest``.

    :param bytes key_digest: the raw ``ripemd160(sha256())`` digest of the public key.
    :param bytes electrum_signature: the raw signature.
    :param bytes byte_string: the message.
    :raises SignatureError: if it finds the signature forged or otherwise problematic.
    :raises ValueError: if it finds the signature cannot be parsed.


Message digest
--------------

.. note:: Unless otherwise noted, ``algo='sha512'`` refers to the SHA-512/256 algorithm.

.. function:: digest_bytes(data, algo='sha512')

    Compute the digest of ``data``, a bytes-like object, returing a tuple containing ``(digest, data_length)``. The first element is the raw digest. The second element is the length of the given data.
    
    :param bytes data: the data to digest.
    :param str algo: the name of the digest algorithm.
    :return: a two-element tuple.
    :rtype: (bytes, int)

.. function:: verify_digest_bytes(data, expect_digest, expect_size = None, algo='sha512')

    Verify if ``data`` have the expected digest ``expect_digest`` and have the expected size ``expect_size``. If ``expect_size`` is *None*, then data size will not be checked.
    
    :param bytes data: the data to digest.
    :param bytes expect_digest: the expected raw digest.
    :param expect_size: the expected data size.
    :type expect_size: int or None
    :raises DigestError: if the digest or size does not match.

.. function:: digest_stream(stream, algo='sha512')

    Compute the digest of `stream`, a stream-like object, returning a tuple containing ``(digest, stream_size)``.  The first element is the raw digest. The second element is the length of the given data.
    
    :param BytesIO stream: the stream to read data from and digest.
    :param str algo: the name of the digest algorithm.
    :return: a two-element tuple.
    :rtype: (bytes, int)

.. function:: verify_digest_stream(stream, expect_digest, expect_size = None, algo='sha512')

    Verify if the data read from ``stream`` have the expected digest ``expect_digest`` and have the expected size ``expect_size``. If ``expect_size`` is *None*, then stream size will not be checked.

    :raises DigestError: if the digest or size does not match.

.. function:: digest_file(path, algo='sha512')

    Compute the data digest of the file located at the given path. The parameter ``path`` should be a unicode string. Returns a tuple containing ``(digest, stream_size)``. The first element is the raw digest. The second element is the length of the given data.
    
    :param str path: the path to the file to read data from and digest.
    :param str algo: the name of the digest algorithm.
    :return: a two-element tuple.
    :rtype: (bytes, int)

.. function:: verify_digest_file(path, expect_digest, expect_size=None, algo='sha512')

    Verify if the file at ``path`` has the expected digest ``expect_digest`` and have the expected size ``expect_size``. If ``expect_size`` is *None*, then file size will not be checked.
    
    :raises DigestError: if the digest or size does not match.


Utilities
---------

.. function:: dumps(json_dict, compact=False)

    Pack the given dictionary to a JSON string, returning a unicode string. **Note that the return value is NOT a bytes-like string.**

    If ``compact`` is *True*, the JSON string will be tightly packed.

    If ``compact`` is *False*, the keys will be sorted and the JSON object will be pretty-printed.
    
    :rtype: str


Exceptions
----------

.. class:: SignatureError(ValueError)

.. class:: DigestError(ValueError)
