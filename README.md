# pylibtgvoip
[Join community](https://t.me/pylibtgvoip) if you need help or wish to contribute

## Installation
Requires cmake and libtgvoip ([build instructions](README.libtgvoip.md)) installed

### Windows
Not working on Windows right now, help needed

### Linux
#### Dependencies

Debian-based distributions:
```bash
$ apt install cmake g++
```

Archlinux-based distributions:
```bash
$ pacman -S cmake gcc
```

### MacOS
#### Dependencies
```bash
$ brew install cmake
```

### Install
```bash
$ pip install git+https://github.com/bakatrouble/pylibtgvoip/
```

## Running examples
Examples require tweaking (set app_id and app_hash, change usernames)

Requires Pyrogram installed from repo (as of 2019-02-07, should be installed automatically as dependency)
```bash
$ cd example
$ wget https://github.com/danog/MadelineProto/raw/master/input.raw  # download sample stream to play
$ python make_call.py  # or receive_call.py, alsa.py
```

## Encoding audio streams
```bash
$ ffmpeg -i input.mp3 -f s16le -ac 1 -ar 48000 -acodec pcm_s16le input.raw  # encode
$ ffmpeg -f s16le -ac 1 -ar 48000 -acodec pcm_s16le -i output.raw output.mp3  # decode
```
