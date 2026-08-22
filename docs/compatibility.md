# CNA compatibility measures

`dependencies.lock` names the exact dependency baseline targeted and audited by this template. Newer CNA or
sharp-runtime revisions are welcome during an intentional upgrade, but are not silently treated as
equivalent: the renderer generator and CMake both compare CNA's canonical renderer set with
`cmake/renderers.json`.

The template keeps a few narrow compatibility measures for revisions used while the C binding was
being developed. Each measure detects the upstream shape that needs it. A fixed upstream shape is
accepted without patching, while an unknown or half-fixed shape fails with a diagnostic naming the
files to inspect.

| ID | Dependency-side issue | Template behavior | Baseline status |
| --- | --- | --- | --- |
| CNA-7 | Modular CNA originally added sharp-runtime before declaring its required component closure, and some tools still linked the legacy `SHARP_RUNTIME` target. | Load CNA's own `SharpRuntimeConsumption.cmake` before `add_subdirectory` when present; create the legacy bridge only if CNA did not create it. | Fixed in the pinned CNA revision; guards make the compatibility path inert. |
| CNA-8 | Canvas retained the four-parameter `CreateRenderTargetCube` override after the interface gained `preserveContents`. | For an affected Emscripten Canvas build, verify both exact stale signatures and compile corrected build-tree copies. If both five-parameter signatures are present, do nothing. Mixed or unknown signatures fail precisely. | Fixed in the pinned CNA revision. |
| CNA-9 | Older embedded CNA builds used the consumer's `CMAKE_SOURCE_DIR` when checking CNA's legacy `src/`/`include/` trees and locating CNA's vendored `cgltf`/`stb` headers. CNA's SDL prebuilt cache also defaults inside its source checkout. | Detect the buggy expressions before reserving consumer directory names or adding corrected include paths. Keep the SDL cache in the template's ignored, target-keyed `build/` area unless the caller overrides it. | Source-root bugs are fixed in the pinned CNA revision; the external SDL cache remains intentional. |
| CNA-CAPI-STATIC | CNA's optional combined static C API packaging target reads Makefile-only `CMakeFiles/cna_c_api.dir/link.txt`; Ninja does not create that file, so its `ALL` target fails after the shared C API has built. | Force `CNA_C_API_BUILD_STATIC=OFF`. This application links the supported shared `CNA::CApi` target and does not ship CNA's static distribution package. | Present in the pinned CNA revision; deliberately out of scope for this application template. |
| SHARP-RUNTIME-2 | `RandomAccess.cpp` once compiled native-only helpers on Emscripten, where `-Werror=unused-function` rejected them. | No warning suppression is applied. The pinned sharp-runtime guards the helpers with `!__EMSCRIPTEN__`; reintroducing the bug therefore fails normally instead of weakening warnings. | Fixed in the pinned sharp-runtime revision. |

An older workaround also redefined `CNA_GL_PROFILE_*` on the application target. It was removed:
the current CNA publishes renderer identity to its own targets, and this C application obtains the
renderer name through `cna_graphics_device_copy_renderer_name` at runtime rather than a C++
compile-time accessor.

## Known dependency-side baseline limitation

The pinned CNA revision does not currently finish an Android C-API build with NDK
`29.0.14206865`. CNA gives `cna_c_api` strict Clang warnings-as-errors, while several CNA headers
trigger `-Wdefaulted-function-deleted`, `-Wmismatched-tags`,
`-Winconsistent-missing-override`, and `-Woverloaded-virtual`. These declarations belong to CNA,
not this template. The Android build therefore remains intentionally red rather than disabling
those diagnostics or carrying a broad shadow copy of dependency headers. Gradle configuration,
debug resource/Java compilation, and release-signing task behavior can still be checked here; an
APK build must be re-run when updating the CNA pin.

When updating the dependency baseline:

1. change the relevant revision in `dependencies.lock`;
2. run `python3 tools/dependency_pins.py` and verify clean checkouts with `--check`;
3. run `python3 tools/gen_renderer_files.py --check --cna-root /path/to/cna`;
4. update the manifest and regenerate if CNA added or removed renderers;
5. configure, build, and run both CTests for at least `headless` and a real rendering backend;
6. review these capability checks against the updated upstream sources.
