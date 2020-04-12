#!/usr/bin/env python3

# PytgVoIP - Telegram VoIP Library for Python
# Copyright (C) 2020 bakatrouble <https://github.com/bakatrouble>
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


import multiprocessing
import os
import re
import sys
import platform
import subprocess
import shutil

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


def check_libraries():
    args = 'gcc -lssl -lopus'.split()
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        stdout, stderr = process.communicate()
        match = re.findall(r'cannot find -l(\w+)', stderr.decode())
        if match:
            raise RuntimeError(
                'Following libraries are not installed: {}\nFor installation guide refer to '
                'https://pytgvoip.readthedocs.io/en/latest/guides/install.html'.format(', '.join(match))
            )


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() != 'Windows':
            check_libraries()

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Release'
        build_args = ['--config', cfg, '--target', '_tgvoip']

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            else:
                cmake_args += ['-A', 'Win32']
            build_args += ['--', '/m:{}'.format(multiprocessing.cpu_count() + 1)]
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j{}'.format(multiprocessing.cpu_count() + 1)]

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        shutil.copy(os.path.join('src', '_tgvoip.pyi'), extdir)


def get_version():
    init_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src', 'tgvoip', '__init__.py')
    with open(init_path, encoding='utf-8') as f:
        version = re.findall(r"__version__ = '(.+)'", f.read())[0]
        if os.environ.get('BUILD') is None and 'pip' not in __file__:
            version += '+develop'
        return version


def get_long_description():
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
        return f.read()


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
    ext_modules=[CMakeExtension('_tgvoip')],
    packages=['tgvoip'],
    package_dir={'tgvoip': 'src/tgvoip'},
    cmdclass={'build_ext': CMakeBuild},
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
