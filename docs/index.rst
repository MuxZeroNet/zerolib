``zerolib``: A Minimalist ZeroNet Protocol Library
==================================================

``zerolib`` is a minimalist utility library for working with the ZeroNet protocol, which is based on MessagePack and uses deterministic elliptic curve signature. It is written for Python 3.5+

This is a highly experimental library. Before its API is stablized, developers should pay close attention to this documentation, as the public API provided by the library may be changed.

**Features include:**

- Digital signatures
- Hashing and data integrity checking
- TLS certificate utilities
- Parsing and formatting packets

``zerolib`` is inspired by the reference ZeroNet implementation written by shortcutme, but features more consistent API and greater flexibility.

``zerolib`` is written and maintained by MuxZeroNet with help from the contributors and is licensed under the GNU General Public License version 3. If you like this project, please consider running a seed box.

.. note:: To avoid confusion, a **private key** is usually called a **secret key** in the documentation.


How to install
--------------

I recommend you use ``zerolib`` in a virtual environment.

.. code-block:: bash

    sudo apt install python3-pip python3-venv

    mkdir devel
    python3 -m venv devel/
    cd devel
    git clone https://github.com/MuxZeroNet/zerolib.git

    # Super important! You must activate the virtual environment.
    # The `source` command activates the virtual environment.
    source ./bin/activate
    which python3 && which pip
    python3 -m pip install -r zerolib/requirements.txt --upgrade

    cd zerolib/zerolib
    python3 run_tests.py


Table of contents
-----------------

.. toctree::
    :maxdepth: 2

    index
    reference/integrity
    reference/protocol
    reference/protocol.packets
    reference/nettools
    discussion/index
