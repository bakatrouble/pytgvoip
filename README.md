# pylibtgvoip

## Installation
Requires libssl and libopus installed

#### Linux
##### Dependencies

Debian-based distributions:
```bash
$ apt install openssl libssl-dev libopus0 libopus-dev
```

Archlinux-based distributions:
```bash
$ pacman -S openssl opus
```

##### Install
```bash
$ pip install git+https://github.com/bakatrouble/pylibtgvoip/
```

#### MacOS
##### Dependencies
```bash
$ brew install openssl opus
```

##### Install
Requires manual pointing to openssl headers location
```bash
$ OPENSSL_ROOT_DIR=/usr/local/opt/openssl pip install git+https://github.com/bakatrouble/pylibtgvoip/
```

#### Windows
TBD

## Running examples
Examples require tweaking (set app_id and app_hash, change usernames)

Requires Pyrogram installed from repo (as of 2019-02-07, should be installed automatically as dependency)
```bash
$ cd example
$ wget https://github.com/danog/MadelineProto/raw/master/input.raw  # download sample stream to play
$ python make_call.py  # or receive_call.py
```

## Encoding audio streams
```bash
$ ffmpeg -i input.mp3 -f s16le -ac 1 -ar 48000 -acodec pcm_s16le input.raw  # encode
$ ffmpeg -f s16le -ac 1 -ar 48000 -acodec pcm_s16le -i output.raw output.mp3  # decode
```
