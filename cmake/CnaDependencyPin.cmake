# Reproducible CNA checkout validation for ordinary CMake builds.

include_guard(GLOBAL)

if(CMAKE_SCRIPT_MODE_FILE AND DEFINED CNA_TEMPLATE_TEST_DEPENDENCY_LOCK)
    # Script-mode regression fixtures can supply a synthetic lock. Project
    # configuration always uses the repository's authoritative file below.
    set(CNA_TEMPLATE_DEPENDENCY_LOCK "${CNA_TEMPLATE_TEST_DEPENDENCY_LOCK}")
else()
    set(CNA_TEMPLATE_DEPENDENCY_LOCK
        "${CMAKE_CURRENT_LIST_DIR}/../dependencies.lock")
endif()

function(cna_template_dependency_pin dependency out_repository out_directory out_revision)
    if(NOT EXISTS "${CNA_TEMPLATE_DEPENDENCY_LOCK}")
        message(FATAL_ERROR
            "cna-c-template: dependency lock is missing at "
            "'${CNA_TEMPLATE_DEPENDENCY_LOCK}'.")
    endif()

    file(STRINGS "${CNA_TEMPLATE_DEPENDENCY_LOCK}" _pin_lines)
    set(_matches 0)
    foreach(_raw_line IN LISTS _pin_lines)
        string(STRIP "${_raw_line}" _line)
        if(_line STREQUAL "" OR _line MATCHES "^#")
            continue()
        endif()
        string(REPLACE "|" ";" _fields "${_line}")
        list(LENGTH _fields _field_count)
        if(NOT _field_count EQUAL 4)
            message(FATAL_ERROR
                "cna-c-template: malformed dependency record '${_line}' in "
                "${CNA_TEMPLATE_DEPENDENCY_LOCK}; expected "
                "NAME|OWNER/REPOSITORY|DIRECTORY|REVISION.")
        endif()
        list(GET _fields 0 _name)
        if(NOT _name STREQUAL dependency)
            continue()
        endif()
        math(EXPR _matches "${_matches} + 1")
        list(GET _fields 1 _repository)
        list(GET _fields 2 _directory)
        list(GET _fields 3 _revision)
    endforeach()

    if(NOT _matches EQUAL 1)
        message(FATAL_ERROR
            "cna-c-template: expected exactly one ${dependency} record in "
            "${CNA_TEMPLATE_DEPENDENCY_LOCK}, found ${_matches}.")
    endif()
    string(LENGTH "${_revision}" _revision_length)
    if(NOT _repository MATCHES "^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
            OR NOT _directory MATCHES "^[A-Za-z0-9][A-Za-z0-9._-]*$"
            OR _directory STREQUAL "."
            OR _directory STREQUAL ".."
            OR NOT _revision_length EQUAL 40
            OR NOT _revision MATCHES "^[0-9a-f]+$")
        message(FATAL_ERROR
            "cna-c-template: invalid ${dependency} record in "
            "${CNA_TEMPLATE_DEPENDENCY_LOCK}.")
    endif()

    set(${out_repository} "${_repository}" PARENT_SCOPE)
    set(${out_directory} "${_directory}" PARENT_SCOPE)
    set(${out_revision} "${_revision}" PARENT_SCOPE)
endfunction()

function(cna_template_verify_dependency_checkout dependency root allow_unpinned)
    cna_template_dependency_pin("${dependency}"
        _expected_repository _expected_directory _expected_revision)

    if(NOT EXISTS "${root}/.git")
        message(WARNING
            "cna-c-template: ${dependency} at '${root}' has no .git metadata; "
            "expected revision ${_expected_revision} cannot be verified. "
            "Source archives remain supported, but this build is not a verified pinned checkout.")
        return()
    endif()

    find_package(Git QUIET)
    if(NOT Git_FOUND)
        message(WARNING
            "cna-c-template: Git is unavailable, so ${dependency} at '${root}' "
            "cannot be compared with expected revision ${_expected_revision}.")
        return()
    endif()

    execute_process(
        COMMAND "${GIT_EXECUTABLE}" -C "${root}" rev-parse HEAD
        RESULT_VARIABLE _head_result
        OUTPUT_VARIABLE _actual_revision
        ERROR_VARIABLE _head_error
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_STRIP_TRAILING_WHITESPACE)
    if(NOT _head_result EQUAL 0)
        message(FATAL_ERROR
            "cna-c-template: Git metadata exists at '${root}', but HEAD could not "
            "be read: ${_head_error}")
    endif()

    execute_process(
        COMMAND "${GIT_EXECUTABLE}" -C "${root}" status --porcelain
                --untracked-files=normal
        RESULT_VARIABLE _status_result
        OUTPUT_VARIABLE _worktree_status
        ERROR_VARIABLE _status_error
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_STRIP_TRAILING_WHITESPACE)
    if(NOT _status_result EQUAL 0)
        message(FATAL_ERROR
            "cna-c-template: Git status failed for '${root}': ${_status_error}")
    endif()

    set(_problems)
    if(NOT _actual_revision STREQUAL _expected_revision)
        list(APPEND _problems
            "revision is ${_actual_revision}, expected ${_expected_revision}")
    endif()
    if(NOT _worktree_status STREQUAL "")
        list(APPEND _problems "worktree has local changes")
    endif()

    if(_problems)
        string(JOIN "; " _problem_text ${_problems})
        if(allow_unpinned)
            message(WARNING
                "cna-c-template: intentional unpinned ${dependency} compatibility "
                "test at '${root}': ${_problem_text}.")
        else()
            message(FATAL_ERROR
                "cna-c-template: ${dependency} checkout drift at '${root}': "
                "${_problem_text}.\n"
                "Use the ${_expected_repository} checkout recorded in dependencies.lock, "
                "or explicitly acknowledge a compatibility test with "
                "-DCNA_ALLOW_UNPINNED=ON.")
        endif()
    else()
        message(STATUS
            "cna-c-template: ${dependency} matches dependencies.lock "
            "(${_expected_revision})")
    endif()
endfunction()

function(cna_template_verify_dependency_target dependency target allow_unpinned)
    if(NOT TARGET "${target}")
        return()
    endif()

    get_target_property(_dependency_source_dir "${target}" SOURCE_DIR)
    if(NOT _dependency_source_dir
            OR _dependency_source_dir MATCHES "-NOTFOUND$")
        message(FATAL_ERROR
            "cna-c-template: cannot determine the source checkout backing "
            "target '${target}' for ${dependency} pin verification.")
    endif()

    file(REAL_PATH "${_dependency_source_dir}" _dependency_source_real)
    message(STATUS
        "cna-c-template: ${target} consumes ${dependency} at "
        "${_dependency_source_real}")
    cna_template_verify_dependency_checkout(
        "${dependency}" "${_dependency_source_real}" "${allow_unpinned}")
endfunction()
