#!/bin/bash

set -xe

if [[ ! -f "/opt/python/$1/bin/python" ]]; then
    echo "Interpreter \"$1\" was not found"
    exit 1
fi

/opt/python/$1/bin/pip3 install wheel auditwheel
cd /tmp
git clone https://github.com/bakatrouble/pytgvoip --recursive
cd pytgvoip
/opt/python/$1/bin/python setup.py bdist_wheel
/opt/python/$1/bin/auditwheel repair --plat manylinux2010_x86_64 dist/*.whl
cp wheelhouse/*.whl /dist/
cd ..
rm -rf pytgvoip
