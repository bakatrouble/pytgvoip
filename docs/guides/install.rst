.. _install:

Installation
============


Requirements
------------
On Linux and macOS to install this library you must have ``make``, ``cmake``, C++11 compatible compiler, Python headers, Opus and OpenSSL libraries and headers installed:

-   Debian-based distributions

    .. code-block:: bash

        $ apt install make cmake gcc g++ python3-dev gcc g++ openssl libssl-dev libopus0 libopus-dev


-   Archlinux-based distributions

    .. code-block:: bash

        $ pacman -S make cmake gcc python3 openssl opus


-   macOS

    .. code-block:: bash

        $ brew install make cmake gcc g++ python3 openssl opus


Install pytgvoip
----------------
-   Stable version:

    .. code-block:: bash

        $ pip install pytgvoip


-   Development version:

    .. code-block:: bash

        $ pip install git+https://github.com/bakatrouble/pytgvoip#egg=pytgvoip



