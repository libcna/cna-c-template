include_guard(GLOBAL)

# Register the template's stable CTest contract for an application target.
# Keep this wiring reusable so lightweight fixtures exercise the same runtime
# directory and failure-propagation behavior as the production project.
function(cna_template_register_tests)
    set(_one_value_args APPLICATION_TARGET DISPLAY_CLASSIFICATION)
    cmake_parse_arguments(PARSE_ARGV 0 CNA_TEMPLATE_TESTS
        "" "${_one_value_args}" "")

    if(CNA_TEMPLATE_TESTS_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR
            "cna_template_register_tests: unexpected argument(s): "
            "${CNA_TEMPLATE_TESTS_UNPARSED_ARGUMENTS}")
    endif()
    if(NOT CNA_TEMPLATE_TESTS_APPLICATION_TARGET)
        message(FATAL_ERROR
            "cna_template_register_tests: APPLICATION_TARGET is required")
    endif()
    if(NOT TARGET "${CNA_TEMPLATE_TESTS_APPLICATION_TARGET}")
        message(FATAL_ERROR
            "cna_template_register_tests: APPLICATION_TARGET "
            "'${CNA_TEMPLATE_TESTS_APPLICATION_TARGET}' is not a CMake target")
    endif()
    if(NOT DEFINED CNA_TEMPLATE_TESTS_DISPLAY_CLASSIFICATION
            OR CNA_TEMPLATE_TESTS_DISPLAY_CLASSIFICATION STREQUAL "")
        message(FATAL_ERROR
            "cna_template_register_tests: DISPLAY_CLASSIFICATION is required")
    endif()

    set(_app "${CNA_TEMPLATE_TESTS_APPLICATION_TARGET}")
    set(_smoke_test CnaCTemplateSmoke)
    set(_failure_test CnaCTemplateFailurePropagation)

    add_test(NAME ${_smoke_test} COMMAND ${_app} --smoke-test)
    add_test(NAME ${_failure_test}
        COMMAND ${CMAKE_COMMAND}
            "-DTEST_EXECUTABLE=$<TARGET_FILE:${_app}>"
            "-DTEST_WORKING_DIRECTORY=$<TARGET_FILE_DIR:${_app}>"
            -P "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/VerifyFailurePropagation.cmake")

    if(CNA_TEMPLATE_TESTS_DISPLAY_CLASSIFICATION STREQUAL "none")
        set(_labels headless)
    else()
        set(_labels display)
    endif()

    set_tests_properties(${_smoke_test} PROPERTIES
        WORKING_DIRECTORY "$<TARGET_FILE_DIR:${_app}>"
        TIMEOUT 30
        LABELS "${_labels}")
    set_tests_properties(${_failure_test} PROPERTIES
        TIMEOUT 30
        LABELS "${_labels};failure-propagation")
endfunction()
