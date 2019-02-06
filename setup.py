#!/usr/bin/env python3

import multiprocessing
import os
import re
import sys
import platform
import subprocess

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion


debug = len(sys.argv) > 1 and sys.argv[1] == "develop"


def check_libraries():
    args = 'gcc -lpthread -lopus -lcrypto -lssl'.split()
    out = subprocess.run(args, stderr=subprocess.PIPE).stderr.decode()
    match = re.findall(r'cannot find -l(\w+)', out)
    if match:
        raise RuntimeError('Following libraries are not installed: {}'.format(', '.join(match)))


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

        # if platform.system() == "Windows":
        #     cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
        #     if cmake_version < '3.1.0':
        #         raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        check_libraries()

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'DEBUG' if debug else 'RELEASE'
        build_args = ['--config', cfg]

        # if platform.system() == "Windows":
        #     cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
        #     if sys.maxsize > 2**32:
        #         cmake_args += ['-A', 'x64']
        #     build_args += ['--', '/m']
        # else:
        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
        build_args += ['--', '-j{}'.format(multiprocessing.cpu_count() + 1)]

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)


setup(
    name='tgvoip',
    version='0.0.1',
    author='bakatrouble',
    author_email='bakatrouble@gmail.com',
    description='libtgvoip bindings for python',
    dependency_links=['https://github.com/pyrogram/pyrogram/tarball/develop#egg=pyrogram'],
    long_description='',
    ext_modules=[CMakeExtension('_tgvoip')],
    packages=['tgvoip'],
    package_dir={'tgvoip': os.path.join('src', 'tgvoip')},
    package_data={'': [os.path.join('src', '_tgvoip.pyi')]},
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
