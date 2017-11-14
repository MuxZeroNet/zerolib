Discussion
==========

What are asymmetrical packets and why?
--------------------------------------

When messages sent in both directions look the same,  we call these messages symmetrical. BitTorrent packets are symmetrical. A response is a request. A request is a directive. The reason behind this design choice is to avoid using a sequence number, even when packets can be lost, duplicated or received not in order.

Unlike BitTorrent, not all ZeroNet packets are symmetrical. To fully interpret an asymmetrical response packet, a computer program has to refer to its previous request packets.

The reason behind this design decision is to minimize data transfer. For example, the same Bitcoin address that appears in the request is omitted in the response, so that a computer program need not receive and parse the same Bitcoin address twice. However, this design decision makes every implementation of this protocol rely on a state machine.
