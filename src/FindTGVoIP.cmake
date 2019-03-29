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


# - Find tgvoip
# Find the native tgvoip includes and libraries
#
#  TGVOIP_INCLUDE_DIR - where to find VoIPController.h, etc.
#  TGVOIP_LIBRARIES   - List of libraries when using tgvoip.
#  TGVOIP_FOUND       - True if tgvoip found.

if(TGVOIP_INCLUDE_DIR)
        set(TGVOIP_FIND_QUIETLY TRUE)
endif(TGVOIP_INCLUDE_DIR)

set(FIND_TGVOIP_PATHS
        ~/Library/Frameworks
        /Library/Frameworks
        /usr/local
        /usr
        /sw
        /opt/local
        /opt/csw
        /opt
        $ENV{TGVOIP_LIBRARY_ROOT}
        $ENV{TGVOIP_INCLUDE_ROOT}
)

find_path(TGVOIP_INCLUDE_DIR
        VoIPController.h
        PATH_SUFFIXES tgvoip libtgvoip
        PATHS ${FIND_TGVOIP_PATHS}
)
find_library(TGVOIP_LIBRARY
        NAMES tgvoip tgvoip_static libtgvoip libtgvoip_static libtgvoip.dll
        PATHS ${FIND_TGVOIP_PATHS}
)

message(STATUS ${TGVOIP_INCLUDE_DIR})
message(STATUS ${TGVOIP_LIBRARY})

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(TGVOIP DEFAULT_MSG TGVOIP_INCLUDE_DIR TGVOIP_LIBRARY)

if(TGVOIP_FOUND)
        set(TGVOIP_LIBRARIES ${TGVOIP_LIBRARY})
else(TGVOIP_FOUND)
        set(TGVOIP_LIBRARIES)
endif(TGVOIP_FOUND)

mark_as_advanced(TGVOIP_INCLUDE_DIR)
mark_as_advanced(TGVOIP_LIBRARY)
