``zerolib.protocol`` - Helpers for common data structures
=========================================================

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

    :var AddrPort dest: the destination of the peer.

    :var address: property. The address of a peer, exclusing the port number. It could be an IPv4Address, an IPv6Address, or an :class:`OnionAddress`.

    :var int port: property. The port number.

    :var last_seen: the time when the last request from the peer is received.

    :var sites: the set of sites the peer is hosting.
    :vartype sites: set of str

    :var int score: the score rating of the peer.

    .. method:: __init__(self, dest, last_seen, sites = None, dht = None, score = None)


Packets
-------

.. |param_sender| replace:: where the packet is from.
.. |type_sender| replace:: AddrPort or None
.. |KeyError| replace:: when a key it is looking for is missing from the packet.
.. |TypeError| replace:: when the type of a value is wrong and cannot be accepted.
.. |ValueError| replace:: when a value looks wrong.

.. function:: unpack_stream(stream, sender = None)

    Unpack a stream, and indicate that it was sent from the sender. Only unpacks one packet at a time.

    :param BytesIO stream: the stream to read data from and unpack.

    :param sender: |param_sender|
    :type sender: |type_sender|

    :raises KeyError: |KeyError|
    :raises TypeError: |TypeError|
    :raises ValueError: |ValueError|

.. function:: unpack_dict(packet, sender = None)

    Unpack a dictionary, and indicate that it was sent from sender.

    :param dict packet: the dictionary to unpack.

    :param sender: |param_sender|
    :type sender: |type_sender|

    :raises KeyError: |KeyError|
    :raises TypeError: |TypeError|
    :raises ValueError: |ValueError|

.. function:: unpack(data, sender = None)

    Unpack a byte string, and indicate that it was sent from a network address. Only unpacks one packet at a time.

    :param bytes data: the data to unpack.

    :param sender: |param_sender|
    :type sender: |type_sender|

    :raises KeyError: |KeyError|
    :raises TypeError: |TypeError|
    :raises ValueError: |ValueError|

.. class:: AddrPort(object)

    A named ``(address, port)`` tuple.

    :var address: could be an IPv4Address, an IPv6Address, or an :class:`OnionAddress`.

    :var int port: the port number.

.. class:: OnionAddress(object)

    A Tor Onion Service address, either v2 or v3.

    .. attribute:: packed

        The packed version of the address, either 10 bytes or 35 bytes long.

    .. method:: __str__(self)

        Returns the human readable, base-32 encoded version of the address, with the ``.onion`` suffix.

        :rtype: str

.. class:: Packet(object)

    The base class for a packet. Every class below for parsed packets is inherited from this base class.

    :var int req_id: the request ID (sequence number) as indicated on the packet. Since the value of this attribute is taken directly from the packet, request ID is for reference purposes only.

    :var sender: where the packet is from.
    :vartype sender: AddrPort or None

.. seealso::

    `A full page of parsed packets <./protocol.packets.html>`_

.. class:: PrefixIter(object)

    The base class for a packet that has the ``prefixes`` attribute. It provides helper methods for easier iteration through the prefixes.

    .. method:: __iter__(self)
    .. method:: __contains__(self, item)

        A packet class inherited from :class:`PrefixIter` supports iteration.

        .. code-block:: python

            >>> from protocol import unpack_dict
            >>> packet = unpack_dict({b'cmd': b'response', b'to': 0,
            ... b'hashfield_raw': b'\x10\x11ABCDef12'})
            >>> packet
            <protocol.packets.RespHashSet object at 0x7fc6b1b5ad58>
            >>> iter(packet)
            <set_iterator object at 0x7fc6b3753990>
            >>> list(iter(packet))
            [b'\x10\x11', b'12', b'ef', b'AB', b'CD']
            >>> b'\x10\x11' in packet
            True
            >>> b'\xA0\xB1' in packet
            False

.. class:: PacketInterp(object)

    The packet interpreter. This state machine is used to figure out the contextual meaning of each response packet and translate it. Consider the following example.

    .. code-block:: python

        >>> from protocol import unpack_dict, PacketInterp
        >>> request = unpack_dict({b'req_id': 0, b'cmd': b'actionCheckport',
        ... b'params': {b'port': 15441}})
        >>> response = unpack_dict({b'cmd': b'response', b'to': 0,
        ... b'status': b'open', b'ip_external': b'1.2.3.4'})
        >>> request
        <protocol.packets.CheckPort object at 0x7f71ca453cc8>
        >>> response
        <protocol.packets.RespPort object at 0x7f71c9cd2948>
        >>> request.port
        15441
        >>> response.open
        True
        >>> response.port
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        AttributeError: port
        >>>
        >>> state_machine = PacketInterp()
        >>> state_machine.register(request)
        >>> state_machine.interpret(response)
        >>> response.port
        15441

    .. method:: register(self, packet)

        Register a request packet. If the packet is a symmetrical packet, or is not a request packet, do nothing.

    .. method:: interpret(self, packet)

        Interpret a response packet and inject necessary atrtibutes into the packet instance. After that, the response packet and the corresponding request packet will be forgotten by the packet interpreter.

        If the packet is a symmetrical packet, or is not a response packet, do nothing.

        :raises TypeError: when the type of the packet is unexpected.
        :raises KeyError: when it cannot find any registered request packet that has the same sequence number.

    .. method:: next_number(self)

        Returns a new usable sequence number. The sequence number always increases and never repeats.

.. seealso:: `What are asymmetrical packets and why? <../discussion/>`_
