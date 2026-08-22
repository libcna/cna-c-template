# =============================================================================
# cna-template — a starter project for the CNA game framework.
# =============================================================================
# Everything renderer-specific in this file is driven by cmake/renderers.json
# (see cmake/CnaRenderers.cmake). There is deliberately no per-renderer
# if/elseif chain here: CNA's renderer set keeps growing, so the template
# treats the renderer set as data rather than as code.
#
# CMake 3.23 is the floor because the easy-gl/meta-gl siblings backing the
# OPENGLES2/OPENGLES3/OPENGL33/WEBGL1/WEBGL2 renderers require it (FILE_SET
# HEADERS). CNA itself only needs 3.20, but a template that could not build the
# GL family would be a poor starting point.
cmake_minimum_required(VERSION 3.23)

project(CnaTemplate VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# --- Customization point: rename your application here -----------------------
# Drives the executable name and the CTest name. Renaming the C game itself
# is a separate step -- see "Making this your own project" in README.md.
set(CNA_TEMPLATE_APP_NAME "HelloGame" CACHE STRING
    "Name of the application executable produced by this template")

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(CnaRenderers)

message(STATUS "cna-template: ${PROJECT_NAME} -> ${CNA_TEMPLATE_APP_NAME}")
message(STATUS "cna-template: platform ${CMAKE_SYSTEM_NAME}, "
               "compiler ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")

# -----------------------------------------------------------------------------
# CNA framework location
# -----------------------------------------------------------------------------
# CNA is a sibling checkout, not a submodule, and is consumed from source with
# add_subdirectory(). CNA can install a C-ABI package, but this template also
# configures the selected renderer and framework dependencies, so an installed
# C-API library is not an equivalent input.
#
# Two layouts are supported without configuration: CNA directly beside this
# template (`../cna`), and this template inside a `_bindings/` directory beside
# CNA (`../../cna`). Android and the generator use the same candidates and order.
# The first existing candidate wins; -DCNA_ROOT_DIR overrides the search entirely.
# Keep a command-line relative override as text until it can be resolved from
# the documented base below. Declaring it PATH here would let CMake absolutize
# it from the invoking process's working directory first.
set(CNA_ROOT_DIR "" CACHE STRING "Path to the CNA framework checkout")
if(CNA_ROOT_DIR STREQUAL "")
    foreach(_cna_candidate IN ITEMS
            "${CMAKE_CURRENT_SOURCE_DIR}/../cna"
            "${CMAKE_CURRENT_SOURCE_DIR}/../../cna")
        if(EXISTS "${_cna_candidate}/CMakeLists.txt")
            set(CNA_ROOT_DIR "${_cna_candidate}" CACHE PATH
                "Path to the CNA framework checkout" FORCE)
            break()
        endif()
    endforeach()
else()
    cmake_path(ABSOLUTE_PATH CNA_ROOT_DIR
        BASE_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}" NORMALIZE
        OUTPUT_VARIABLE _cna_root_absolute)
    set(CNA_ROOT_DIR "${_cna_root_absolute}" CACHE PATH
        "Path to the CNA framework checkout" FORCE)
endif()

if(NOT EXISTS "${CNA_ROOT_DIR}/CMakeLists.txt")
    message(FATAL_ERROR
        "cna-c-template: CNA framework not found at '${CNA_ROOT_DIR}'.\n"
        "CNA is a separate sibling repository, not part of this template. It is\n"
        "looked for at ../cna and ../../cna.\n"
        "  cd ${CMAKE_CURRENT_SOURCE_DIR}/.. && git clone https://github.com/openeggbert/cna.git\n"
        "or pass -DCNA_ROOT_DIR=/path/to/cna to cmake. Relative overrides are\n"
        "resolved from the template repository root.\n"
        "README.md \"Prerequisites\" lists every checkout you need.")
endif()
message(STATUS "cna-c-template: using CNA at ${CNA_ROOT_DIR}")

# CNA-9 (module-layout half): older supported CNA revisions accidentally tested
# the consumer's CMAKE_SOURCE_DIR for CNA's own legacy src/include directories.
# Detect that exact implementation before reserving those otherwise-normal names.
set(_cna_modules_cmake "${CNA_ROOT_DIR}/modules/CMakeLists.txt")
set(_cna_has_consumer_layout_bug OFF)
if(EXISTS "${_cna_modules_cmake}")
    file(READ "${_cna_modules_cmake}" _cna_modules_cmake_content)
    string(FIND "${_cna_modules_cmake_content}"
        [=[${CMAKE_SOURCE_DIR}/${_cna_legacy}]=]
        _cna_consumer_layout_bug_position)
    if(NOT _cna_consumer_layout_bug_position EQUAL -1)
        set(_cna_has_consumer_layout_bug ON)
    endif()
endif()
if(_cna_has_consumer_layout_bug)
    foreach(_cna_template_reserved IN ITEMS src include)
        if(EXISTS "${CMAKE_SOURCE_DIR}/${_cna_template_reserved}")
            message(FATAL_ERROR
                "cna-c-template: this CNA revision has CNA-9 and mistakes the consumer's\n"
                "'${_cna_template_reserved}/' directory for CNA's legacy source tree. Keep\n"
                "application sources under game/ or update CNA to the pinned baseline.\n"
                "See docs/compatibility.md for the detection and upstream fix.")
        endif()
    endforeach()
endif()

# Enable the C API in the framework build.
set(CNA_BUILD_C_API ON CACHE BOOL "Build the CNA C API" FORCE)
# This application consumes CNA::CApi, the shared C ABI. CNA's optional static
# packaging target is not part of the application and its link-line extraction
# currently assumes Makefile-only link.txt metadata that Ninja does not emit.
# Disable that unrelated ALL target explicitly rather than letting a successful
# application build fail while producing an unused distribution artifact. See
# docs/compatibility.md (CNA-CAPI-STATIC).
set(CNA_C_API_BUILD_STATIC OFF CACHE BOOL
    "Build CNA's optional combined static C API distribution archive" FORCE)

# Draco is a pinned submodule of CNA that a plain `git clone` does not populate,
# and CNA fails the configure outright when it is enabled but missing. Default it
# off in exactly that case, so the template configures out of the box, and say so
# rather than degrading silently. A populated submodule is left alone: whoever
# initialised it wants the compressed-mesh decoder. Override either way with
# -DCNA_ENABLE_DRACO=ON/OFF.
if(NOT DEFINED CNA_ENABLE_DRACO)
    if(EXISTS "${CNA_ROOT_DIR}/third_party/draco/CMakeLists.txt")
        message(STATUS "cna-c-template: Draco submodule present, leaving KHR_draco_mesh_compression enabled")
    else()
        set(CNA_ENABLE_DRACO OFF CACHE BOOL "Enable Draco mesh decompression in CNA" FORCE)
        message(STATUS
            "cna-c-template: Draco submodule not initialised, building without "
            "KHR_draco_mesh_compression. Run "
            "'git -C ${CNA_ROOT_DIR} submodule update --init third_party/draco' "
            "and reconfigure with -DCNA_ENABLE_DRACO=ON to enable it.")
    endif()
endif()

# -----------------------------------------------------------------------------
# Renderer selection
# -----------------------------------------------------------------------------
# CNA_GRAPHICS_RENDERER is CNA's own public cache variable and this template
# passes it straight through -- it deliberately does not re-declare a default.
# If you set nothing, CNA picks its own (WEBGL2 on the web, OPENGLES3 on Linux,
# SDL_RENDERER elsewhere) and the template validates the result afterwards.
#
# CNA also exposes CNA_RENDERER_<NAME> booleans as an alternative input path.
# They all default to OFF and CNA only consults them if one is switched ON, so
# setting the string alone is sufficient and this file leaves them alone.
if(DEFINED CNA_GRAPHICS_RENDERER AND NOT CNA_GRAPHICS_RENDERER STREQUAL "")
    cna_template_validate_renderer("${CNA_GRAPHICS_RENDERER}" "${CNA_ROOT_DIR}")
    message(STATUS "cna-template: renderer ${CNA_GRAPHICS_RENDERER} (requested)")
else()
    message(STATUS "cna-template: no renderer requested; using CNA's default for this platform")
endif()

# -----------------------------------------------------------------------------
# CNA build options
# -----------------------------------------------------------------------------
# Keep CNA's own footprint small: an application needs neither the framework's
# test suite nor its demo applications. easy-gl's gates default ON and it is
# pulled in for the whole GL renderer family, so silence those too. meta-gl's
# own tests already default OFF, so no BUILD_TESTING override is needed.
set(CNA_BUILD_TESTS       OFF CACHE BOOL "Build CNA tests"                FORCE)
set(CNA_BUILD_EXAMPLES    OFF CACHE BOOL "Build CNA example applications" FORCE)
set(EASYGL_BUILD_TESTS    OFF CACHE BOOL "Build easy-gl tests"            FORCE)
set(EASYGL_BUILD_EXAMPLES OFF CACHE BOOL "Build easy-gl examples"         FORCE)

# CNA's vendored SDL cache defaults inside CNA's own source checkout. That is
# unsuitable for immutable dependency checkouts and failed during the web
# verification here. Keep the persistent, target-keyed cache in this
# consumer's ignored build/ area unless the caller chose another location.
# See docs/compatibility.md (CNA-9).
if(NOT DEFINED CNA_SDL_PREBUILT_ROOT)
    if(EMSCRIPTEN)
        set(_cna_sdl_cache_target emscripten)
    else()
        set(_cna_sdl_cache_target
            "${CMAKE_SYSTEM_NAME}-${CMAKE_SYSTEM_PROCESSOR}-${CMAKE_C_COMPILER_ID}")
    endif()
    set(CNA_SDL_PREBUILT_ROOT
        "${CMAKE_CURRENT_SOURCE_DIR}/build/cna-sdl-prebuilt-${_cna_sdl_cache_target}"
        CACHE PATH "Persistent CNA SDL build cache outside the CNA checkout")
endif()

# CNA's modular consumption layer owns the exact Sharp Runtime component
# closure its public targets need. CNA currently loads that layer only after it
# has already added sharp-runtime, so an embedded build otherwise falls back to
# SharpRuntime::All and needlessly requires optional dependencies such as zlib
# on every cross-target. Read CNA's own list before add_subdirectory() rather
# than duplicating it here. An application that directly uses extra Sharp
# Runtime APIs can set SHARP_RUNTIME_COMPONENTS itself and link their narrow
# SharpRuntime::<Component> targets.
set(_cna_sharp_runtime_consumption
    "${CNA_ROOT_DIR}/cmake/SharpRuntimeConsumption.cmake")
if(EXISTS "${_cna_sharp_runtime_consumption}")
    include("${_cna_sharp_runtime_consumption}")
    if(NOT DEFINED SHARP_RUNTIME_COMPONENTS)
        set(SHARP_RUNTIME_COMPONENTS "${CNA_SHARP_RUNTIME_DEFAULT_COMPONENTS}"
            CACHE STRING "Sharp Runtime components required by CNA")
    endif()
endif()

# Older CNA revisions used the consumer root for vendored content headers,
# adding their single-header include paths as ${CMAKE_SOURCE_DIR}/third_party/...,
# which resolves into the CONSUMER's tree rather than CNA's. Building CNA as a
# subdirectory therefore fails with "fatal error: cgltf.h: No such file or
# directory". INCLUDE_DIRECTORIES is a directory property that subdirectories
# inherit, so setting the correct paths here repairs the search path without
# modifying CNA. Apply the overlay only when that exact CNA-9 expression exists.
set(_cna_content_cmake "${CNA_ROOT_DIR}/modules/content/CMakeLists.txt")
if(EXISTS "${_cna_content_cmake}")
    file(READ "${_cna_content_cmake}" _cna_content_cmake_content)
    string(FIND "${_cna_content_cmake_content}"
        [=[${CMAKE_SOURCE_DIR}/third_party/]=]
        _cna_consumer_header_bug_position)
    if(NOT _cna_consumer_header_bug_position EQUAL -1)
        message(STATUS "cna-c-template: applying detected CNA-9 vendored-header compatibility")
        foreach(_cna_vendored_header_dir IN ITEMS cgltf stb)
            if(EXISTS "${CNA_ROOT_DIR}/third_party/${_cna_vendored_header_dir}")
                include_directories("${CNA_ROOT_DIR}/third_party/${_cna_vendored_header_dir}")
            endif()
        endforeach()
    endif()
endif()

add_subdirectory("${CNA_ROOT_DIR}" CNA)

# CNA's modular targets correctly use SharpRuntime::<Component>, but a few
# ancillary upstream tools still link the legacy SHARP_RUNTIME name directly.
# The modular runtime intentionally creates that compatibility target only for
# the expensive All selection.  Supply an equivalent bridge over CNA's narrow
# component set so those tools remain buildable without enabling every optional
# component (and its cross-platform dependencies). See docs/compatibility.md
# (CNA-7). The TARGET guard makes this inert once CNA supplies its own bridge.
if(NOT TARGET SHARP_RUNTIME
        AND TARGET SharpRuntime::Core.Base
        AND DEFINED CNA_SHARP_RUNTIME_DEFAULT_COMPONENTS)
    add_library(SHARP_RUNTIME INTERFACE)
    foreach(_sharp_component IN LISTS CNA_SHARP_RUNTIME_DEFAULT_COMPONENTS)
        target_link_libraries(SHARP_RUNTIME INTERFACE
            "SharpRuntime::${_sharp_component}")
    endforeach()
endif()

# An older CNA revision changed IGraphicsRenderer::CreateRenderTargetCube()
# from four to five parameters but missed CanvasRenderer's declaration and
# definition. Keep the sibling checkout read-only: derive two build-tree
# compatibility copies, verify the exact stale signatures before replacing
# them, then compile CanvasRenderer.cpp against the corrected overlay header.
# The strict guards make an upstream change fail visibly instead of silently
# applying a stale textual patch. See docs/compatibility.md (CNA-8).
if(EMSCRIPTEN
        AND CNA_GRAPHICS_RENDERER STREQUAL "CANVAS"
        AND TARGET cna_renderer_canvas)
    set(_canvas_source
        "${CNA_ROOT_DIR}/modules/renderers/canvas/src/CanvasRenderer.cpp")
    set(_canvas_header
        "${CNA_ROOT_DIR}/modules/renderers/canvas/include/CNA/Internal/Renderers/Canvas/CanvasRenderer.hpp")
    cmake_path(NORMAL_PATH _canvas_source)
    cmake_path(NORMAL_PATH _canvas_header)
    set(_canvas_compat_root
        "${CMAKE_CURRENT_BINARY_DIR}/cna-template-compat/canvas")
    set(_canvas_compat_source "${_canvas_compat_root}/CanvasRenderer.cpp")
    set(_canvas_compat_header
        "${_canvas_compat_root}/include/CNA/Internal/Renderers/Canvas/CanvasRenderer.hpp")

    file(READ "${_canvas_header}" _canvas_header_content)
    set(_canvas_old_header_signature [=[
        std::unique_ptr<IRenderTargetCubeRenderer> CreateRenderTargetCube(
            int size, int depthFormat, bool mipMap = false,
            int multiSampleCount = 0) override;]=])
    set(_canvas_new_header_signature [=[
        std::unique_ptr<IRenderTargetCubeRenderer> CreateRenderTargetCube(
            int size, int depthFormat, bool preserveContents = false,
            bool mipMap = false, int multiSampleCount = 0) override;]=])
    string(FIND "${_canvas_header_content}"
        "${_canvas_old_header_signature}" _canvas_header_signature_position)
    file(READ "${_canvas_source}" _canvas_source_content)
    set(_canvas_old_source_signature [=[
    std::unique_ptr<IRenderTargetCubeRenderer> CanvasRenderer::CreateRenderTargetCube(
        int size, int, bool, int)]=])
    set(_canvas_new_source_signature [=[
    std::unique_ptr<IRenderTargetCubeRenderer> CanvasRenderer::CreateRenderTargetCube(
        int size, int, bool, bool, int)]=])
    string(FIND "${_canvas_source_content}"
        "${_canvas_old_source_signature}" _canvas_source_signature_position)

    # A fixed CNA is a supported capability, not an error. A mixed or unknown
    # shape is an error because an overlay could then compile only half the fix.
    string(FIND "${_canvas_header_content}"
        "bool preserveContents" _canvas_fixed_header_position)
    string(FIND "${_canvas_source_content}"
        "int size, int, bool, bool, int)" _canvas_fixed_source_position)
    if(NOT _canvas_fixed_header_position EQUAL -1
            AND NOT _canvas_fixed_source_position EQUAL -1)
        message(STATUS "cna-c-template: CNA-8 is fixed upstream; Canvas overlay not needed")
    elseif(_canvas_header_signature_position EQUAL -1
            OR _canvas_source_signature_position EQUAL -1)
        message(FATAL_ERROR
            "cna-c-template: CNA's Canvas CreateRenderTargetCube signatures are "
            "neither the known four-parameter CNA-8 form nor the fixed five-parameter "
            "form. Refusing a partial textual overlay; inspect ${_canvas_header} and "
            "${_canvas_source}, then update docs/compatibility.md and this capability check.")
    else()
        message(STATUS "cna-c-template: applying detected CNA-8 Canvas compatibility overlay")
        string(REPLACE "${_canvas_old_header_signature}"
            "${_canvas_new_header_signature}"
            _canvas_header_content "${_canvas_header_content}")
        string(REPLACE "${_canvas_old_source_signature}"
            "${_canvas_new_source_signature}"
            _canvas_source_content "${_canvas_source_content}")

        file(MAKE_DIRECTORY
            "${_canvas_compat_root}"
            "${_canvas_compat_root}/include/CNA/Internal/Renderers/Canvas")
        file(CONFIGURE OUTPUT "${_canvas_compat_header}"
            CONTENT "${_canvas_header_content}" @ONLY)
        file(CONFIGURE OUTPUT "${_canvas_compat_source}"
            CONTENT "${_canvas_source_content}" @ONLY)

        get_target_property(_canvas_sources cna_renderer_canvas SOURCES)
        list(FIND _canvas_sources "${_canvas_source}" _canvas_source_index)
        if(_canvas_source_index EQUAL -1)
            message(FATAL_ERROR
                "cna-c-template: cannot locate CanvasRenderer.cpp in "
                "cna_renderer_canvas; refusing an incomplete CNA-8 workaround.")
        endif()
        list(REMOVE_ITEM _canvas_sources "${_canvas_source}")
        set_property(TARGET cna_renderer_canvas PROPERTY SOURCES
            ${_canvas_sources} "${_canvas_compat_source}")
        target_include_directories(cna_renderer_canvas BEFORE PRIVATE
            "${_canvas_compat_root}/include")
    endif()
endif()

# CNA has now resolved the renderer (ours or its own default) and published the
# canonical list in the cache. Re-check both against the manifest.
cna_template_assert_no_drift()
cna_template_validate_renderer("${CNA_GRAPHICS_RENDERER}" "${CNA_ROOT_DIR}")

cna_template_renderer_field("${CNA_GRAPHICS_RENDERER}" display   CNA_TEMPLATE_RENDERER_DISPLAY)
cna_template_renderer_field("${CNA_GRAPHICS_RENDERER}" dimension CNA_TEMPLATE_RENDERER_DIMENSION)
message(STATUS "cna-template: renderer ${CNA_GRAPHICS_RENDERER} "
               "(${CNA_TEMPLATE_RENDERER_DIMENSION}, display: ${CNA_TEMPLATE_RENDERER_DISPLAY})")

# SDL's IMPORTED targets are created by find_package() inside CNA's directory
# scope, so they are not visible up here. Re-importing is cheap and idempotent:
# CNA has already cached each *_DIR pointing at the libraries it built. All
# three must be visible here so cna_copy_sdl_runtime() can package their DLLs.
# This must come after add_subdirectory() for exactly that reason.
foreach(_sdl_package IN ITEMS SDL3 SDL3_image SDL3_mixer)
    if(NOT TARGET ${_sdl_package}::${_sdl_package})
        find_package(${_sdl_package} REQUIRED CONFIG)
    endif()
endforeach()

# -----------------------------------------------------------------------------
# The application
# -----------------------------------------------------------------------------
set(CNA_TEMPLATE_SOURCES
    game/src/HelloGame.c
    game/src/Program.c
)

# On Android the "executable" is a shared library that SDL's Java glue loads by
# name, so the target name is fixed regardless of CNA_TEMPLATE_APP_NAME.
if(ANDROID)
    set(_app main)
    add_library(${_app} SHARED ${CNA_TEMPLATE_SOURCES})
else()
    set(_app ${CNA_TEMPLATE_APP_NAME})
    add_executable(${_app} ${CNA_TEMPLATE_SOURCES})
endif()

target_include_directories(${_app} PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/game/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/game/src"
)

# CNA is an INTERFACE umbrella already carrying every framework module, the
# selected renderer target, the required Sharp Runtime component targets, the
# public compile definitions and the public include directories. Linking either
# a renderer or the legacy all-components SHARP_RUNTIME umbrella by hand is
# obsolete. So is the old -Wl,--start-group wrapper: CNA declares its
# static-library cycles on the targets themselves, and a linker group around an
# INTERFACE library expands to nothing anyway.
target_link_libraries(${_app} PRIVATE cna_c_api)

if(UNIX AND NOT APPLE AND NOT ANDROID AND NOT EMSCRIPTEN)
    target_link_libraries(${_app} PRIVATE m)
endif()

if(TARGET SDL3::SDL3main)
    target_link_libraries(${_app} PRIVATE SDL3::SDL3main)
endif()

# -----------------------------------------------------------------------------
# Platform specifics
# -----------------------------------------------------------------------------
if(ANDROID)
    # CNA links android/log PUBLIC on its own device module, so they arrive
    # through the umbrella; only SDL3 has to be named here.
    target_link_libraries(${_app} PRIVATE SDL3::SDL3)
    # Assets are packaged into the APK -- see android/app/build.gradle.

elseif(EMSCRIPTEN)
    target_link_libraries(${_app} PRIVATE SDL3::SDL3)
    set_target_properties(${_app} PROPERTIES SUFFIX ".html")

    # CNA enables the Wasm exception-handling ABI in its own directory scope.
    # Directory properties propagate downward only, so this target -- defined in
    # the parent scope -- must opt in explicitly or the link fails with
    # "wasm-ld: undefined symbol: __cpp_exception".
    target_compile_options(${_app} PRIVATE -fwasm-exceptions)
    target_link_options(${_app} PRIVATE -fwasm-exceptions)

    target_link_options(${_app} PRIVATE
        -sALLOW_MEMORY_GROWTH=1
        -sSTACK_SIZE=1048576
        -sINITIAL_MEMORY=134217728
        -sFORCE_FILESYSTEM=1
        # Let main() actually return, so --smoke-test terminates the process.
        -sEXIT_RUNTIME=1
        "SHELL:--preload-file ${CMAKE_CURRENT_SOURCE_DIR}/Content@/Content")

    # WebGL version constraints are per renderer, not global: pinning
    # MIN/MAX_WEBGL_VERSION=2 for every web build would break WEBGL1, and the
    # CANVAS/HTML_DOM/SVG_DOM renderers create no WebGL context at all.
    cna_template_renderer_field("${CNA_GRAPHICS_RENDERER}" webflags _webflags)
    if(_webflags)
        target_link_options(${_app} PRIVATE ${_webflags})
    endif()

else()
    # Native desktop: put Content/ next to the executable so the relative paths
    # the game uses at runtime resolve.
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/Content")
        add_custom_command(TARGET ${_app} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_directory
                "${CMAKE_CURRENT_SOURCE_DIR}/Content"
                "$<TARGET_FILE_DIR:${_app}>/Content"
            COMMENT "Copying game content next to ${_app}")
    endif()
endif()

if(WIN32)
    # CNA defines these helpers; CMake functions are global once defined, so they
    # are callable here after add_subdirectory(). Fall back to CMake's own
    # TARGET_RUNTIME_DLLS if a CNA revision does not provide them.
    if(COMMAND cna_copy_sdl_runtime)
        cna_copy_sdl_runtime(${_app})
    else()
        add_custom_command(TARGET ${_app} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_RUNTIME_DLLS:${_app}>" "$<TARGET_FILE_DIR:${_app}>"
            COMMAND_EXPAND_LISTS
            COMMENT "Copying runtime DLLs next to ${_app}")
    endif()
endif()

if(MINGW)
    # CNA's full RTTI graph is not compatible with MinGW's static libstdc++:
    # PE-COFF fails to fold the inline std::type_info::operator== emitted by
    # cna_runtime against the identical copy in libstdc++.a. Use the dynamic
    # runtime and ask CNA to package its DLLs next to the executable instead.
    if(COMMAND cna_copy_mingw_cxx_runtime)
        cna_copy_mingw_cxx_runtime(${_app})
    else()
        message(WARNING
            "cna-template: this CNA revision does not provide "
            "cna_copy_mingw_cxx_runtime(); copy the MinGW GCC and C++ runtime "
            "DLLs next to ${_app} before running it.")
    endif()
endif()

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
option(CNA_TEMPLATE_BUILD_TESTS "Register cna-template's own smoke test" ON)

if(CNA_TEMPLATE_BUILD_TESTS AND NOT ANDROID AND NOT EMSCRIPTEN AND NOT CMAKE_CROSSCOMPILING)
    enable_testing()
    add_test(NAME ${CNA_TEMPLATE_APP_NAME}Smoke COMMAND ${_app} --smoke-test)
    add_test(NAME ${CNA_TEMPLATE_APP_NAME}FailurePropagation
        COMMAND ${_app} --smoke-test --simulate-draw-failure)

    # Label the test by what it needs from the environment, so CI can run the
    # display-free renderers with no X server at all and reserve xvfb-run for
    # the ones that genuinely open a window:
    #   ctest -L headless               # no display required
    #   xvfb-run -a ctest -L display
    if(CNA_TEMPLATE_RENDERER_DISPLAY STREQUAL "none")
        set(_labels headless)
    else()
        set(_labels display)
    endif()

    set_tests_properties(${CNA_TEMPLATE_APP_NAME}Smoke PROPERTIES
        TIMEOUT 30
        LABELS "${_labels}")
    set_tests_properties(${CNA_TEMPLATE_APP_NAME}FailurePropagation PROPERTIES
        TIMEOUT 30
        LABELS "${_labels};failure-propagation"
        WILL_FAIL TRUE)
elseif(CNA_TEMPLATE_BUILD_TESTS)
    message(STATUS
        "cna-c-template: smoke tests are not registered for this target "
        "(ANDROID=${ANDROID}, EMSCRIPTEN=${EMSCRIPTEN}, "
        "CMAKE_CROSSCOMPILING=${CMAKE_CROSSCOMPILING})")
endif()
