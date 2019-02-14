# libtgvoip

It might be available from official repositories, otherwise you must build it manually

Requires `libopus` and `libssl` installed

### Windows
[![Build status](https://ci.appveyor.com/api/projects/status/hiugc2951g7u98r3?svg=true)](https://ci.appveyor.com/project/bakatrouble/libtgvoip) https://github.com/bakatrouble/libtgvoip/tree/msvc_static

Build notes:

Add `__declspec(dllexport)` to following symbols:
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
$ ./configure --enable-static=no
$ make  # add "-jN" flag for multithreaded build, N=(cpu core count + 1) is recommended
$ make install
```

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