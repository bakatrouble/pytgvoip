cmake_minimum_required(VERSION 2.8.12)
project(pylibtgvoip)
set(CMAKE_CXX_STANDARD 14)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}")

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
