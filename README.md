# pytgvoip
**Telegram VoIP Library for Python**

[Community](https://t.me/pytgvoip)

Supported MTProto frameworks: [Pyrogram](https://github.com/pyrogram/pyrogram/)

```python
from pyrogram import Client
from tgvoip import VoIPFileStreamService

app = Client('account')
app.start()

service = VoIPFileStreamService(app, receive_calls=False)
call = service.start_call('@bakatrouble')
call.play('input.raw')
call.play_on_hold(['input.raw'])
call.set_output_file('output.raw')

@call.on_call_ended
def call_ended(call):
    app.stop()

app.idle()
```

**PytgVoIP** is a [Telegram](https://telegram.org/) VoIP library written in Python and C++.

It uses [libtgvoip](https://github.com/grishka/libtgvoip) (a library used in official clients) 
for voice encoding and transmission, and [pybind11](https://github.com/pybind/pybind11) for simple 
generation of Python extension written in C++.

## Features
* Making and receiving Telegram calls
* Python callbacks for sending and receiving audio stream frames allow flexible control (see `alsa.py` example which uses system audio devices)
* Included classes that use files for audio playback/record
* Pre-built Windows packages: [![Build status](https://ci.appveyor.com/api/projects/status/l0rwtrhhulrkb07x?svg=true)](https://ci.appveyor.com/project/bakatrouble/pylibtgvoip)

## Requirements
* Python 3.4 or higher
* A [Telegram API key](https://docs.pyrogram.ml/start/ProjectSetup#api-keys)

Linux, MacOS: (use binary wheels from PyPI for Windows)
* [libtgvoip](docs/libtgvoip.md)
* CMake, C++11-compatible compiler, Python headers

## Installing
```pip3 install pytgvoip```


## Encoding audio streams
Streams consumed by `libtgvoip` should be encoded in 16-bit signed PCM audio.
```bash
$ ffmpeg -i input.mp3 -f s16le -ac 1 -ar 48000 -acodec pcm_s16le input.raw  # encode
$ ffmpeg -f s16le -ac 1 -ar 48000 -acodec pcm_s16le -i output.raw output.mp3  # decode
```

## Copyright & License
* Copyright (C) 2019 [bakatrouble](https://github.com/bakatrouble)
* Licensed under the terms of the [GNU Lesser General Public License v3 or later (LGPLv3+)](COPYING.lesser)
