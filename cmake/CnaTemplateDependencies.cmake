# =============================================================================
# The sibling releases this template release is built and tested against
# (docs/releasing.md).
#
# CNA and sharp-runtime are separate checkouts consumed with add_subdirectory,
# so checking out a template tag does not select them; easy-gl and meta-gl join
# only when a GL-family renderer (OPENGLES3, OPENGL33, WEBGL2) is built, because
# CNA adds them only then. dependencies.lock records (and CMake verifies) the exact commits; this
# file records the *versions* and enforces them: each sibling generates a
# Version.hpp from its own one-place version, and the template reads it right
# after CNA's add_subdirectory and refuses an incompatible checkout.
#
# "Compatible" is the pre-1.0 rule every one of these projects states in its
# docs/releasing.md: a minor bump may break the API, a patch release may not. So
# a checkout satisfies X.Y.Z when it declares X.Y.Z or a later X.Y patch release,
# and not when it declares an X.Y.Z pre-release, which precedes X.Y.Z.
#
# A release bump updates these values, dependencies.lock, the matching
# CHANGELOG.md entry, and nothing else.
# =============================================================================

set(CNA_TEMPLATE_REQUIRED_CNA_VERSION           "0.1.0")
set(CNA_TEMPLATE_REQUIRED_SHARP_RUNTIME_VERSION "0.1.0")
set(CNA_TEMPLATE_REQUIRED_EASYGL_VERSION        "0.1.1")   # GL-family renderers only
set(CNA_TEMPLATE_REQUIRED_METAGL_VERSION        "0.4.1")   # GL-family renderers only

option(CNA_TEMPLATE_CHECK_DEPENDENCY_VERSIONS
    "Fail configuration when a sibling checkout declares a version this template release does not support; OFF reports it as a warning instead"
    ON)

# cna_template_require_sibling_version(<name> <checkout> <generated Version.hpp> <macro> <required>)
function(cna_template_require_sibling_version name checkout header macro required)
    set(declared "")
    if(EXISTS "${header}")
        file(STRINGS "${header}" _line REGEX "^#define ${macro} \"[^\"]*\"$")
        string(REGEX REPLACE "^#define ${macro} \"([^\"]*)\"$" "\\1" declared "${_line}")
    endif()

    if(NOT required MATCHES "^([0-9]+)\\.([0-9]+)\\.([0-9]+)$")
        message(FATAL_ERROR "cna-c-template: required ${name} version '${required}' is not MAJOR.MINOR.PATCH")
    endif()
    set(_major "${CMAKE_MATCH_1}")
    set(_minor "${CMAKE_MATCH_2}")
    set(_patch "${CMAKE_MATCH_3}")

    set(_compatible FALSE)
    if(declared MATCHES "^([0-9]+)\\.([0-9]+)\\.([0-9]+)(-[0-9A-Za-z.-]+)?$")
        set(_have_major "${CMAKE_MATCH_1}")
        set(_have_minor "${CMAKE_MATCH_2}")
        set(_have_patch "${CMAKE_MATCH_3}")
        set(_have_prerelease "${CMAKE_MATCH_4}")
        if(_have_major EQUAL _major AND _have_minor EQUAL _minor)
            if(_have_patch GREATER _patch)
                set(_compatible TRUE)
            elseif(_have_patch EQUAL _patch AND _have_prerelease STREQUAL "")
                set(_compatible TRUE)
            endif()
        endif()
    endif()

    if(_compatible)
        message(STATUS "cna-c-template: ${name} ${declared} at ${checkout} (requires ${required})")
        return()
    endif()

    if(declared STREQUAL "")
        set(declared "no version (a checkout older than its first versioned release)")
    endif()
    string(CONCAT _text
        "cna-c-template ${CNA_TEMPLATE_VERSION_STRING} requires ${name} ${required}, or a later "
        "${_major}.${_minor}.x patch release, but the checkout at ${checkout} declares ${declared}. "
        "Check out the release there (git -C \"${checkout}\" checkout v${required}; "
        "dependencies.lock names the exact commit), or configure with "
        "-DCNA_TEMPLATE_CHECK_DEPENDENCY_VERSIONS=OFF to build against it anyway with a warning.")
    if(CNA_TEMPLATE_CHECK_DEPENDENCY_VERSIONS)
        message(FATAL_ERROR "${_text}")
    else()
        message(WARNING "${_text}")
    endif()
endfunction()
