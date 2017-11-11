``zerolib.protocol`` - Helpers for network I/O and common data structures
=========================================================================

This module offers functions for parsing packets and classes representing common data structures used in the ZeroNet protocol.

It defines the following public functions and classes.


TLS certificate
---------------

.. function:: make_cert()

    Generate and return a public key PEM and a secret key PEM. The return value is a tuple ``(publickey_pem, secretkey_pem)`` containing the bytes of the public PEM file and the bytes of the secret PEM file.

    :rtype: (bytes, bytes)


User certificate
----------------

.. function:: recover_cert(user_btc, portal, name)

    Recover the certificate from the user's Bitcoin address (string), the portal type (string) and the user's name (string). Returns the recovered certificate, as a bytes-like string.

    :param str user_btc: the user's Bitcoin address.
    :param str portal: the portal type, usually defined by the certificate issuer.
    :param str name: the user's name.
    :return: the recovered certificate.
    :rtype: bytes


Routing
-------

.. class:: Peer(object)

    The data structure of a peer.

    .. attribute:: address
    .. attribute:: last_seen
    .. attribute:: sites
    .. attribute:: dht
    .. attribute:: score

    .. method:: __init__(self, address, last_seen, sites = None, dht = None, score = None)


Packets
-------

.. function:: unpack_stream(stream, from_addr = None)

    Unpack a stream, and indicate that it was sent from a network address.

    :param BytesIO stream: the stream to read data from and unpack.
    :param from_addr: where the packet is from.
    :type from_addr: AddrPort or None
    :raises KeyError: when a key it is looking for is missing from the packet.
    :raises TypeError: when the type of a value is wrong and cannot be accepted.
    :raises ValueError: when a value looks wrong.

.. function:: unpack(data, from_addr = None)

    Unpack a byte string, and indicate that it was sent from a network address. Like :func:`unpack_stream`, but only unpacks one packet at a time.

    :param bytes data: the data to unpack.
    :param from_addr: where the packet is from.
    :type from_addr: AddrPort or None

.. class:: AddrPort(object)

    A named ``(address, port)`` tuple.

    .. attribute:: address

        Could be an IPv4Address, an IPv6Address, or an :class:`OnionAddress`.

    .. attribute:: port

        An integer, the port.

.. class:: OnionAddress(object)

    A Tor Onion Service address, either v2 or v3.

    .. attribute:: packed

        The packed version of the address, either 10 bytes or 35 bytes long.

    .. method:: __str__(self)

        Returns the human readable, base-32 encoded version of the address, with the ``.onion`` suffix.

        :rtype: str

.. class:: Packet(object)

    The base class for a packet. Every class below for parsed packets is inherited from this base class.

    .. attribute:: req_id

        An integer. The request ID as indicated on the packet. Since the value of this attribute is taken directly from the packet, request ID is for reference purposes only.

        .. tip::

            By looking for specific attributes of a packet, there is a way to distinguish the type of each response packet without relying on the request ID.

            There should always be a way like this, even in the foreseeable future. You should be able to know what to do by just looking at the packet content. If not, then the protocol design sucks and you should file an issue report to `HelloZeroNet/Documentation <https://github.com/HelloZeroNet/Documentation>`_.

    .. attribute:: from_addr

        An :class:`AddrPort` object or *None*.

.. seealso::

    `A full page of parsed packets <./protocol.packets.html>`_
