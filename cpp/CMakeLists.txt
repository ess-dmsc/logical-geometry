set(EXTRA_MODULES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
list(APPEND CMAKE_MODULE_PATH ${EXTRA_MODULES_DIR})

#=============================================================================
# setting up conan for use from within cmake
#=============================================================================
set(WITH_CONAN OFF CACHE BOOL "Enable dependency build with conan")

if (WITH_CONAN)
  include(${EXTRA_MODULES_DIR}/ConanSetup.cmake)
  conan_cmake_run(CONANFILE conanfile.txt
    BASIC_SETUP
    BUILD missing)
endif ()

if (EXISTS ${PROJECT_BINARY_DIR}/conanbuildinfo.cmake)
  message(STATUS "Using existing conanbuildinfo.cmake file")
  include(${PROJECT_BINARY_DIR}/conanbuildinfo.cmake)
  conan_basic_setup()
endif ()

include(${EXTRA_MODULES_DIR}/FindGTestFix.cmake)
include(${EXTRA_MODULES_DIR}/CoverageReports.cmake)

add_subdirectory(tests)
