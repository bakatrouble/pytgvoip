# libtgvoip

It might be available from official repositories, otherwise you must build it manually

Requires `libopus` and `libssl` installed

### Windows
Not working on Windows right now, help needed (following are just notes)

First clone and build openssl and opus in Telegram/Libraries
([guide](https://github.com/telegramdesktop/tdesktop/blob/dev/docs/building-msvc.md))
and replace `libtgvoip.gyp` with [this file](https://gist.github.com/bakatrouble/377bcb11b90a472415b19af6217a2d7d)

Then add `__declspec(dllexport)` to following symbols:
* VoIPServerConfig.h
   * class ServerConfig
* VoIPController.h
   * class Endpoint
   * class AudioOutputDevice
   * class AudioInputDevice
   * class VoIPController
* threading.h
   * class Mutex
   * class MutexGuard
* NetworkSocket.h
   * class IPv4Address
   * class IPv6Address

```batch
cd ...Telegram/ThirdParty/libtgvoip
gyp -D OS=win --depth=. --format ninja libtgvoip.gyp
gyp -D OS=win --depth=. --format msvs-ninja libtgvoip.gyp
ninja -C out/Release
```

### Linux
#### Dependencies

Debian-based distributions:
```bash
$ apt install make autoconf automake gcc g++ openssl libssl-dev libopus0 libopus-dev
```

Archlinux-based distributions:
```bash
$ pacman -S make autoconf automake gcc openssl opus
```

#### Build and install
```bash
$ cd /tmp
$ git clone https://github.com/grishka/libtgvoip/
$ cd libtgvoip
$ git checkout fc13464b  # confirmed to work with this version, others would require testing

$ export CFLAGS="-O3"
$ export CXXFLAGS="-O3"
$ autoreconf --force --install
$ ./configure --without-pulse --without-alsa --enable-audio-callback --enable-static=no
$ make  # add "-jN" flag for multithreaded build, N=(cpu core count + 1) is recommended
$ make install
```

#### ARM
Note: for ARM architecture (i.e. Raspberry Pi) you must patch sources before `autoconf`, otherwise it fails to build:
```bash
$ patch -d /tmp/libtgvoip
```
After execution of the command paste contents of `Makefile.am.arm.patch`, newline, Ctrl+D. 

### MacOS
#### Dependencies
```bash
$ brew install make autoconf automake gcc g++ openssl opus  # most of those should be installed with XCode Tools
```

#### Build and install
The same as for Linux, but you should manually point the location of libopenssl headers:
 
```bash
export OPENSSL_ROOT_DIR=/usr/local/opt/openssl
```