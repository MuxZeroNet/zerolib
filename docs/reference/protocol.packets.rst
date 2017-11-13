``zerolib.protocol`` - Full list of packets
===========================================

BitTorrent packets are symmetrical. Messages sent in both directions look the same. There is no request or response. The reason behind this choice is to avoid using a sequence number, even when packets may be lost, duplicated or not be received in order.

Unlike BitTorrent, not all ZeroNet packets are symmetrical. To fully interpret an asymmetrical response packet, a computer program has to refer to its previous request packets. This design decision makes every implementation rely on a state machine. This page lists all documented ZeroNet packets in two categories.

Symmetrical Packets
-------------------

Every symmetrical packet contains enough information which the program can interpret without referring to the previous request packets.

.. class:: Handshake(Packet)

    Unpacked ``handshake`` packet sent when the connection was initialized.

    :var crypto_set: the set of supported cryptographic algorithms.
    :vartype crypto_set: set of str
    :var int port: the port number the sender is actively listening on.
    :var onion: the Tor Onion Address of the peer. *(only used in Tor mode)*
    :vartype onion: OnionAddress or None
    :var str protocol: a unicode string representing the protocol version.
    :var bool open: whether the sender believes his port is open.
    :var peer_id: the peer ID as a **binary string**. *(not available in Tor mode)*
    :vartype peer_id: bytes or None
    :var str version: the version string of the sender's software.
    :var int rev: the rev number of the sender's software.

.. class:: OhHi(Handshake)

    Response packet of :class:`Handshake`.

    :var str preferred_crypto: the cryptographic algorithm that the sender would like to use.

    ... as well as the attributes inherited from :class:`Handshake`.

.. class:: Ping(Packet)

.. class:: Pong(Packet)


Asymmetrical Packets
--------------------

An asymmetrical response packet itself does not contain enough information. To fully interpret an asymmetrical response, the program has to refer to its previous requests.

.. |bitcoin| replace:: the site address, a human-readable Bitcoin address.
.. |injected| replace:: The following variables will be injected when the packet is handled by the state machine.

.. class:: PEX(Packet)

    Unpacked ``pex`` packet that exchanges peers with the client. Peers are parsed at construct-time.

    :var str site: |bitcoin|
    :var int need: the number of peers the sender needs.
    :var peers: clearnet peers.
    :vartype peers: set of :class:`AddrPort`
    :var onions: Tor Onion Service peers.
    :vartype onions: set of :class:`AddrPort`

.. class:: RespPEX(Packet)

    Response packet of :class:`PEX`.

    :var peers: clearnet peers
    :vartype peers: set of :class:`AddrPort`
    :var onions: Tor Onion Service peers
    :vartype onions: set of :class:`AddrPort`

    |injected|

    :var str site: |bitcoin|

.. |inner| replace:: the relative path to the requested file.

.. class:: GetFile(Packet)

    Unpacked ``getFile`` packet that requests for a file.

    :var str site: |bitcoin|
    :var str inner_path: |inner|
    :var int offset: request file from this offset.
    :var total_size: the total size of the requested file. *(optional)*
    :vartype total_size: int or None

.. class:: RespFile(Packet)

    Response packet of :class:`GetFile`.

    :var bytes body: a chunk of file content.
    :var int last_byte: the absolute offset of the last byte of ``body``.
    :var int total_size: the total size of the whole file.
    :var int offset: property. The absolute offset of the first byte of ``body``.
    :var int next_offset: property. The start offset of the next ``getFile`` request.

    |injected|

    :var str site: |bitcoin|
    :var str inner_path: |inner|


.. class:: ListMod(Packet)

    Unpacked ``listModified`` packet that requests for the paths of ``content.json`` files modified since the given time. This packet is used to heuristically list a site's new user content.

    :var str site: |bitcoin|
    :var int since: list content.json files since this timestamp. The timestamp is in seconds.

    .. warning::

        This timestamp is defined vaguely in the spec. Is it an int or a float? `Link to the spec. <https://zeronet.readthedocs.io/en/latest/help_zeronet/network_protocol/#listmodified-site-since>`_

.. class:: RespMod(Packet):

    Response packet of :class:`ListMod`.

    :var timestamps: the ``{inner_path : timestamp}`` dictionary.
    :vartype timestamps: dict of str and int

    .. method:: __iter__(self)
    .. method:: __contains__(self, key)
    .. method:: items(self)

        Helper methods for iterating through the ``timestamps``.

        .. code-block:: python

            for (inner_path, timestamp) in packet.items():
                print('File %r was updated on %d' % (inner_path, timestamps))

    |injected|

    :var str site: |bitcoin|

.. class:: GetHash(Packet)

    Unpacked ``getHashfield`` packet that requests for the client's list of downloaded optional file IDs.

    :var str site: |bitcoin|

.. class:: RespHashSet(Packet, PrefixIter)

    Response packet of :class:`GetHash`.

    :var prefixes: hash ID prefixes in a set.
    :vartype prefixes: set of bytes

    |injected|

    :var str site: |bitcoin|


.. class:: FindHash(Packet)

    Unpacked ``findHashIds`` packet that asks if the client knows any peer that has the said optional file IDs.

    :var str site: |bitcoin|
    :var prefixes: the set of optional file IDs. An optional file ID is the first 2 bytes of the file's hash.
    :vartype prefixes: set of bytes

.. class:: RespHashDict(Packet)

    Response packet of :class:`FindHash`.


.. class:: SetHash(Packet)

    Unpacked ``setHashfield`` packet that announces the sender's list of optional file IDs.

    :var str site: |bitcoin|
    :var prefixes: the set of optional file IDs. An optional file ID is the first 2 bytes of the file's hash.
    :vartype prefixes: set of bytes

.. class:: Predicate(Packet):

    Status predicate. Either an ``ok`` packet or an ``error`` packet. Response packet of :class:`Update` and :class:`SetHash`.

    :var bool ok: Okay?

.. class:: Update(Packet)

    Unpacked ``update`` packet that pushes a new site file.

    Its response packet is a :class:`Predicate`.

.. |port| replace:: the port number which the sender would like you to check.

.. class:: CheckPort(Packet):

    Unpacked ``actionCheckport`` packet that asks the client to check the sender's port status.

    :var int port: |port|



.. class:: RespPort(Packet)

    Response packet of :class:`CheckPort`.

    :var str status: port status.

    |injected|

    :var int port: |port|
