FROM quay.io/pypa/manylinux2010_x86_64

RUN yum install -y gcc \
                   openssl \
                   openssl-devel \
                   opus \
                   opus-devel

RUN cd /tmp \
 && git clone https://github.com/grishka/libtgvoip/ \
 && cd libtgvoip \
 && git checkout b6ac2911 \
 && export CFLAGS="-O3 -std=c99" \
 && export CXXFLAGS="-O3 -D__STDC_FORMAT_MACROS" \
 && autoreconf --force --install \
 && ./configure --enable-audio-callback --enable-static=no \
 && make -j9 \
 && make install \
 && cd .. \
 && rm -rf libtgvoip

COPY build.sh /
ENTRYPOINT ["sh", "/build.sh"]
