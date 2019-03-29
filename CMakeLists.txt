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


cmake_minimum_required(VERSION 2.8.12)
project(pylibtgvoip)
set(CMAKE_CXX_STANDARD 14)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/src")

find_package(TGVoIP)

add_definitions(-DTGVOIP_USE_CALLBACK_AUDIO_IO -DWEBRTC_APM_DEBUG_DUMP=0 -DWEBRTC_NS_FLOAT -DTGVOIP_USE_DESKTOP_DSP)
add_subdirectory(3rdparty/pybind11)
include_directories(${TGVOIP_INCLUDE_DIR})

list(APPEND SOURCES
        src/_tgvoip.cpp
        src/_tgvoip_module.cpp
)

link_libraries(${TGVOIP_LIBRARY})
pybind11_add_module(_tgvoip ${SOURCES})
