cmake_minimum_required(VERSION 3.0.0)
project(h5cpp
  LANGUAGES CXX C
  VERSION 0.0.1
  )

set(EXTRA_MODULES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
list(APPEND CMAKE_MODULE_PATH ${EXTRA_MODULES_DIR})

include(${EXTRA_MODULES_DIR}/FindGTestFix.cmake)
include(${EXTRA_MODULES_DIR}/CoverageReports.cmake)


if (NOT GTest_FOUND)
  message(WARNING "GTest not found. No tests will be built.")
  return()
endif ()

include_directories(
  ${PROJECT_SOURCE_DIR}
  ${PROJECT_SOURCE_DIR}/src)

set(dir ${CMAKE_CURRENT_SOURCE_DIR})

set(test_sources ${dir}/ESSGeometryTest.cpp)
set(test_headers ${dir}/src/ESSGeometry.h ${dir}/TestBase.h)

add_executable(
  unit_tests
  ${test_sources}
  ${test_headers}
  )
target_include_directories(
  unit_tests
  PRIVATE ${GTEST_INCLUDE_DIRS}
  )
target_link_libraries(
  unit_tests
  ${GTEST_LIBRARIES}
  ${CMAKE_THREAD_LIBS_INIT}
  ${COVERAGE_LIBRARIES})
enable_coverage(unit_tests)

add_custom_target(run_tests
  COMMAND unit_tests "--gtest_output=xml:unit_tests_run.xml"
  DEPENDS unit_tests)
add_test(NAME "RunGoogleTests" COMMAND run_tests)

create_coverage_targets(
  generate_coverage
  run_tests
  ${PROJECT_BINARY_DIR}
  ${PROJECT_SOURCE_DIR}/src
  ${PROJECT_BINARY_DIR}/coverage)
