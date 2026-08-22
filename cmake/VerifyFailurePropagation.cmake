# Verify the failure-injection contract without accepting an arbitrary process failure.

if(NOT DEFINED TEST_EXECUTABLE OR TEST_EXECUTABLE STREQUAL "")
    message(FATAL_ERROR "TEST_EXECUTABLE is required")
endif()
if(NOT DEFINED TEST_WORKING_DIRECTORY OR TEST_WORKING_DIRECTORY STREQUAL "")
    get_filename_component(TEST_WORKING_DIRECTORY "${TEST_EXECUTABLE}" DIRECTORY)
endif()

execute_process(
    COMMAND "${TEST_EXECUTABLE}" --smoke-test --simulate-draw-failure
    WORKING_DIRECTORY "${TEST_WORKING_DIRECTORY}"
    RESULT_VARIABLE _result
    OUTPUT_VARIABLE _stdout
    ERROR_VARIABLE _stderr
    TIMEOUT 25)

set(_injection_marker
    "CNA_TEMPLATE_TEST: draw failure injected (result=2)")
set(_propagation_marker
    "CNA_TEMPLATE_TEST: draw failure propagated (injected_result=2, run_result=9, destroy_result=9, exit_code=86)")
string(FIND "${_stderr}" "${_injection_marker}" _injection_position)
string(FIND "${_stderr}" "${_propagation_marker}" _propagation_position)

if(NOT _result STREQUAL "86"
        OR _injection_position EQUAL -1
        OR _propagation_position EQUAL -1
        OR _propagation_position LESS_EQUAL _injection_position)
    message(FATAL_ERROR
        "Simulated draw failure did not satisfy the exact contract.\n"
        "Expected exit: 86; actual: ${_result}\n"
        "Expected injection marker: ${_injection_marker}\n"
        "Expected propagation marker: ${_propagation_marker}\n"
        "--- stdout ---\n${_stdout}\n"
        "--- stderr ---\n${_stderr}")
endif()

message(STATUS
    "Verified injected draw failure: draw reached, result 2 injected, "
    "callback result 9 propagated through run and destroy, process exited 86")
