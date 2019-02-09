cmake_minimum_required(VERSION 2.8.12)
project(pylibtgvoip)
set(CMAKE_CXX_STANDARD 14)

if(UNIX AND NOT APPLE)
        set(LINUX TRUE)
endif()

add_definitions(-DTGVOIP_USE_CALLBACK_AUDIO_IO -DWEBRTC_APM_DEBUG_DUMP=0 -DWEBRTC_NS_FLOAT -DTGVOIP_USE_DESKTOP_DSP)

if(WIN32)
        add_definitions(-DWEBRTC_WIN)
elseif(LINUX)
        add_definitions(-DWEBRTC_POSIX -DWEBRTC_LINUX)
elseif(APPLE)
        add_definitions(-DWEBRTC_POSIX -DWEBRTC_MAC)
endif()

if(NOT CMAKE_BUILD_TYPE MATCHES DEBUG)
    add_definitions(-DTGVOIP_LOG_VERBOSITY=1)
endif()

add_subdirectory(3rdparty/pybind11)
include_directories(3rdparty/libtgvoip)

list(APPEND SOURCES
        src/_tgvoip.cpp
        src/_tgvoip_module.cpp
)

link_libraries(tgvoip)  # stdc++ dl
pybind11_add_module(_tgvoip ${SOURCES})
