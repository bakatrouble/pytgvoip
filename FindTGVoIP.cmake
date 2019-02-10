# - Find tgvoip
# Find the native tgvoip includes and libraries
#
#  TGVOIP_INCLUDE_DIR - where to find opus.h, etc.
#  TGVOIP_LIBRARIES   - List of libraries when using opus(file).
#  TGVOIP_FOUND       - True if opus found.

if(TGVOIP_INCLUDE_DIR)
        set(TGVOIP_FIND_QUIETLY TRUE)
endif(TGVOIP_INCLUDE_DIR)

find_path(TGVOIP_INCLUDE_DIR tgvoip/VoIPController.h PATH_SUFFIXES tgvoip)
find_library(TGVOIP_LIBRARY NO_DEFAULT_PATH NAMES tgvoip tgvoip_static libtgvoip libtgvoip_static)
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(TGVOIP DEFAULT_MSG TGVOIP_INCLUDE_DIR TGVOIP_LIBRARY)

if(TGVOIP_FOUND)
        set(TGVOIP_LIBRARIES ${TGVOIP_LIBRARY})
else(TGVOIP_FOUND)
        set(TGVOIP_LIBRARIES)
endif(TGVOIP_FOUND)

mark_as_advanced(TGVOIP_INCLUDE_DIR)
mark_as_advanced(TGVOIP_LIBRARY)
