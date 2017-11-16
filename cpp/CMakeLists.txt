set(EXTRA_MODULES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
list(APPEND CMAKE_MODULE_PATH ${EXTRA_MODULES_DIR})

include(${EXTRA_MODULES_DIR}/FindGTestFix.cmake)
include(${EXTRA_MODULES_DIR}/CoverageReports.cmake)

add_subdirectory(tests)
