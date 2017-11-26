``zerolib.nettools`` - Higher level network I/O utilities
=========================================================

The ``zerolib.nettools`` module defines functions and classes which help in interacting with remote peers in the network.

Connection
----------

.. class:: Connections(object)

    The connection manager.

    .. method:: __init__(self, capacity=200, clean_func = None)

    .. method:: register(self, dest, socket)

    .. method:: __getitem__(self, key)

    .. method:: __delitem__(self, key)

    .. method:: __contains__(self, key)

    .. method:: __iter__(self)

    .. method:: __len__(self)
