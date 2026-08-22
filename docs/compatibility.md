# CNA compatibility measures

`dependencies.lock` names the exact dependency baseline targeted and audited by this template.
Newer CNA or sharp-runtime revisions are welcome during an intentional upgrade, but are not
silently treated as equivalent: ordinary CMake and Gradle builds compare CNA HEAD and worktree
state with the lock, while the renderer generator and CMake also compare CNA's canonical renderer
set with `cmake/renderers.json`. Use `CNA_ALLOW_UNPINNED=ON` or Gradle's
`cnaAllowUnpinned=true` only for an intentional compatibility test. A source archive without Git
metadata is accepted with an explicit unverifiable-pin warning.

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

The pinned CNA revision `6bba5562d66b2005057569373843be6c843ec8f1` does not finish an Android
C-API build with NDK `29.0.14206865`. `modules/c-api/CMakeLists.txt` assigns
`-Wall -Wextra -Werror -Wno-missing-field-initializers` to `cna_c_api`; the template adds none of
those strict flags. The first reproducible arm64 failure is:

- `modules/audio/include/Microsoft/Xna/Framework/Audio/AudioEngine.hpp:22,131` declares and befriends
  `AudioCategory` as a `class`, while `AudioCategory.hpp:23` defines it as a `struct`
  (`-Werror,-Wmismatched-tags`).

Other concurrently compiled C-API translation units also fail because:

- `modules/math/include/Microsoft/Xna/Framework/BoundingBox.hpp:18`,
  `Plane.hpp:15`, and `BoundingFrustum.hpp:25` disagree on the `struct`/`class` tag for
  `BoundingFrustum` (`-Werror,-Wmismatched-tags`);
- `modules/graphics/include/Microsoft/Xna/Framework/Graphics/VertexPositionColorTexture.hpp:27`
  explicitly defaults a constructor Clang deletes because `Color` has no default constructor
  (`-Werror,-Wdefaulted-function-deleted`);
- `modules/media/include/Microsoft/Xna/Framework/Media/Song.hpp:172,185` hides `Object::Equals` and
  omits `override` on `GetHashCode` (`-Werror,-Woverloaded-virtual` and
  `-Werror,-Winconsistent-missing-override`).

These declarations and the strict target policy belong to CNA, not this template. The Android
build therefore remains intentionally red rather than disabling diagnostics or carrying a broad
shadow copy of dependency headers. The template narrows Gradle's native target request to `main`,
so unrelated CNA tools are no longer requested, but `main` legitimately depends on `CNA::CApi`
and still reaches the upstream failure.

Before that failure, the pinned build completed debug resource processing, Java compilation,
dexing, SDL/CMake configuration, and most arm64 native dependency compilation. AGP's generated
model identifies the intended `libmain.so`, its `libcna_c_api.so` dependency, and SDL3 runtime;
`HelloGameActivity` requests libraries `SDL3` and `main`, and Gradle declares both `arm64-v8a` and
`x86_64`. On Android, `Program.c` includes SDL's public `SDL_main.h`; the pre-blocker CI check
compiles that object and verifies it exports `SDL_main`, the function SDLActivity resolves, rather
than a plain `main`. The blocker prevents linking those libraries and reaching APK packaging, so
neither the packaged `.so` locations nor an installable APK is claimed as verified. Required CI
exercises the strongest passing boundary and the signing negative contract. Re-run `assembleDebug`
against a new candidate pin with the workflow's `verify_android_native` manual input, and make that
step required only after CNA fixes these diagnostics.

When updating the dependency baseline:

1. change the relevant revision in `dependencies.lock`;
2. run `python3 tools/dependency_pins.py` and verify clean checkouts with `--check`;
3. run `python3 tools/gen_renderer_files.py --check --cna-root /path/to/cna`;
4. update the manifest and regenerate if CNA added or removed renderers;
5. configure, build, and run both CTests for at least `headless` and a real rendering backend;
6. review these capability checks against the updated upstream sources.
