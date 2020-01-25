.. _libtgvoip:

Building libtgvoip
==================


Requirements
------------

-   Debian-based distributions

    .. code-block:: bash

        $ apt install make autoconf automake gcc g++ openssl libssl-dev libopus0 libopus-dev


-   Archlinux-based distributions

    .. code-block:: bash

        $ pacman -S make autoconf automake gcc openssl opus


-   macOS

    .. code-block:: bash

        $ brew install make autoconf automake gcc g++ openssl opus


Build and install
-----------------

.. code-block:: bash

    $ cd /tmp
    $ git clone https://github.com/telegramdesktop/libtgvoip/
    $ cd libtgvoip
    $ git checkout c5651ff  # confirmed to work with this version, others would require testing

    $ export CFLAGS="-O3"
    $ export CXXFLAGS="-O3"
    $ autoreconf --force --install
    $ ./configure --enable-audio-callback=yes --enable-static=no
    $ make  # add "-jN" flag for multithreaded build, N=(cpu core count + 1) is recommended
    $ make install
