### pylibtgvoip
Almost exact port of `php-libtgvoip` and MadelineProto VoIP module

Interfaces are similiar to MadelineProto [PhoneCall](https://docs.madelineproto.xyz/API_docs/types/PhoneCall.html) (= `_tgvoip.VoIP`)

Usage docs: https://docs.madelineproto.xyz/docs/CALLS.html

Method names are transformed to snake_case, check end of the `_tgvoip.cpp` for full list.  

### Building
Requires libcrypto, libssl, libopus and libboost-python headers installed
```bash
$ mkdir build
$ cd build
$ cmake ..
$ make
```

### Running examples
Examples require tweaking (set app_id and app_hash, change usernames)

Requires installed Pyrogram v0.11.0+
```bash
$ cd examples
$ cp ../build/_tgvoip.so _tgvoip.so
$ wget https://github.com/danog/MadelineProto/raw/master/input.raw  # download sample stream to play
$ python make_call.py  # or receive_calls.py, prank.py
```

### Encoding audio streams
```bash
$ ffmpeg -i input.mp3 -f s16le -ac 1 -ar 48000 -acodec pcm_s16le input.raw  # encode
$ ffmpeg -f s16le -ac 1 -ar 48000 -acodec pcm_s16le -i output.raw output.mp3  # decode
```