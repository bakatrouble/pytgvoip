#!/usr/bin/env python3

# PytgVoIP - Telegram VoIP Library for Python
# Copyright (C) 2019 bakatrouble <https://github.com/bakatrouble>
#
# This file is part of PytgVoIP.
#
# PytgVoIP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PytgVoIP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PytgVoIP.  If not, see <http://www.gnu.org/licenses/>.


import os
import re
import sys
import platform

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


def find_libtgvoip_headers():
    search = [
        '/Library/Frameworks/include/tgvoip',
        '/usr/local/include/tgvoip',
        '/usr/include/tgvoip',
        '/sw/include/tgvoip',
        '/opt/local/include/tgvoip',
        '/opt/csw/include/tgvoip',
        '/opt/include/tgvoip',
        os.environ.get('TGVOIP_INCLUDE_ROOT', ''),
    ]
    for path in search:
        if os.path.exists(path) and os.path.exists(os.path.join(path, 'VoIPController.h')):
            return path
    raise RuntimeError('libtgvoip headers are not found\nRefer to '
                       'https://pytgvoip.readthedocs.io/en/latest/guides/libtgvoip.html '
                       'for guide on building libtgvoip')


ext_modules = [
    Extension(
        '_tgvoip',
        [
            'src/_tgvoip_module.cpp',
            'src/_tgvoip.cpp',
        ],
        libraries=['tgvoip'],
        library_dirs=[
            os.environ.get('TGVOIP_LIBRARY_ROOT', ''),
        ],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True),
            find_libtgvoip_headers(),
        ],
        define_macros=[
            ('TGVOIP_USE_CALLBACK_AUDIO_IO', '1'),
            ('WEBRTC_APM_DEBUG_DUMP', '0'),
            ('WEBRTC_NS_FLOAT', '1'),
            ('TGVOIP_USE_DESKTOP_DSP', '1'),
        ],
        language='c++'
    ),
]


def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support is needed!')


class BuildExt(build_ext):
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="{}"'.format(get_version()))
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append(r'/DVERSION_INFO=\"{}\"'.format(get_version()))
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


def get_version():
    init_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src', 'tgvoip', '__init__.py')
    with open(init_path, encoding='utf-8') as f:
        version = re.findall(r"__version__ = '(.+)'", f.read())[0]
        if os.environ.get('BUILD') is None:
            version += '.develop'
        return version


def get_long_description():
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
        return f.read()


def get_data_files():
    data_files = []
    if platform.system() == 'Windows':
        data_files.append(('lib\\site-packages\\', ['libtgvoip.dll']))
    return data_files


setup(
    name='pytgvoip',
    version=get_version(),
    license='LGPLv3+',
    author='bakatrouble',
    author_email='bakatrouble@gmail.com',
    description='Telegram VoIP Library for Python',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/bakatrouble/pytgvoip',
    keywords='telegram messenger voip library python',
    project_urls={
        'Tracker': 'https://github.com/bakatrouble/pytgvoip/issues',
        'Community': 'https:/t.me/pytgvoip',
        'Source': 'https://github.com/bakatrouble/pytgvoip',
    },
    python_required='~=3.5',
    ext_modules=ext_modules,
    packages=['tgvoip'],
    package_dir={'tgvoip': os.path.join('src', 'tgvoip')},
    package_data={'': [os.path.join('src', '_tgvoip.pyi')]},
    data_files=get_data_files(),
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: C++',
        'Topic :: Internet',
        'Topic :: Communications',
        'Topic :: Communications :: Internet Phone',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
