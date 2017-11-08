## `zerolib.protocol` - Helpers for network I/O and common data structures

This module offers functions for parsing packets and classes representing common data structures used in the ZeroNet protocol.

It defines the following public functions and classes.

### TLS certificate

`make_cert()`

Generate and return a public key PEM and a secret key PEM. The return value is a tuple `(publickey_pem, secretkey_pem)` containing the bytes of the public PEM file and the bytes of the secret PEM file.

### User certificate

`recover_cert(user_btc, portal, name)`

Recover the certificate from the user's Bitcoin address (string), the portal type (string) and the user's name (string). Returns the recovered certificate, as a bytes-like string.

### Routing

`class Peer(object)`

Attributes:

- `address`
- `last_seen`
- `sites`
- `dht`
- `score`

Methods:

- `__init__(self, address, last_seen, sites = None, dht = None, score = None)`
