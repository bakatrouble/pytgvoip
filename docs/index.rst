Welcome to pytgvoip
===================

|pypi| |libwheels-win| |libtgvoip-win| |license|

**Telegram VoIP Library for Python**

`Community`_

**PytgVoIP** is a `Telegram`_ VoIP library written in Python and C++.

It uses `libtgvoip`_ (a library used in official clients) for voice
encoding and transmission, and `pybind11`_ for simple generation of
Python extension written in C++.

Features
--------

-  Making and receiving Telegram calls
-  Python callbacks for sending and receiving audio stream frames allow
   flexible control
-  Pre-built Windows wheels in PyPI

Requirements
------------

-  Python 3.4 or higher
-  An MTProto client (i.e. Pyrogram, Telethon)

Installing
----------

Refer the corresponding section: :ref:`install`

Encoding audio streams
----------------------

Streams consumed by ``libtgvoip`` should be encoded in 16-bit signed PCM
audio.

.. code-block:: bash

   $ ffmpeg -i input.mp3 -f s16le -ac 1 -ar 48000 -acodec pcm_s16le input.raw  # encode
   $ ffmpeg -f s16le -ac 1 -ar 48000 -acodec pcm_s16le -i output.raw output.mp3  # decode

.. _copyright--license:

Copyright & License
-------------------

-  Copyright (C) 2019 `bakatrouble`_
-  Licensed under the terms of the `GNU Lesser General Public License v3 or later (LGPLv3+)`_


.. _Community: https://t.me/pytgvoip
.. _Telegram: https://telegram.org/
.. _libtgvoip: https://github.com/grishka/libtgvoip
.. _pybind11: https://github.com/pybind/pybind11
.. _bakatrouble: https://github.com/bakatrouble
.. _GNU Lesser General Public License v3 or later (LGPLv3+): https://github.com/bakatrouble/pytgvoip/blob/master/COPYING.lesser

.. |pypi| image:: https://img.shields.io/pypi/v/pytgvoip.svg?style=flat
   :target: https://pypi.org/project/pytgvoip/
.. |libwheels-win| image:: https://img.shields.io/appveyor/ci/bakatrouble/pylibtgvoip.svg?label=windows%20wheels%20build&style=flat
   :target: https://ci.appveyor.com/project/bakatrouble/pylibtgvoip
.. |libtgvoip-win| image:: https://img.shields.io/appveyor/ci/bakatrouble/libtgvoip.svg?label=libtgvoip%20windows%20build&style=flat
   :target: https://ci.appveyor.com/project/bakatrouble/libtgvoip
.. |license| image:: https://img.shields.io/pypi/l/pytgvoip.svg?style=flat


.. toctree::
    :hidden:

    self
    guides/install
    guides/usage

.. toctree::
    :hidden:
    :caption: Module

    module/tgvoip
    module/utils
