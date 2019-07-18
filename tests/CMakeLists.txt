include_directories(
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_CURRENT_SOURCE_DIR}/../source)

set(dir ${CMAKE_CURRENT_SOURCE_DIR})

set(test_sources
  ${dir}/ESSGeometryTest.cpp)
set(test_headers
  ${dir}/TestBase.h
  ${dir}/../source/ESSGeometry.h)

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
  PRIVATE ${GTEST_LIBRARIES}
  PRIVATE ${CMAKE_THREAD_LIBS_INIT}
  PRIVATE ${COVERAGE_LIBRARIES}
)
enable_coverage(unit_tests)

add_custom_target(run_tests
  COMMAND unit_tests "--gtest_output=xml:unit_tests_run.xml"
  DEPENDS unit_tests)
add_test(NAME "RunGoogleTests" COMMAND run_tests)

set(gcovr_excl_opts " ")
create_coverage_targets(
  coverage
  run_tests
  ${PROJECT_BINARY_DIR}
  ${PROJECT_SOURCE_DIR}/source
  ${PROJECT_BINARY_DIR}/coverage
  ${gcovr_excl_opts})

