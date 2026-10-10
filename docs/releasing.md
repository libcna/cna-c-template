# Releasing cna-c-template

*Current as of 0.1.0 (2026-10-10).*

cna-c-template follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). A release
is an annotated git tag plus a `CHANGELOG.md` entry — there is no separate release branch, no
release workflow, and nothing is published to a package registry. A game made from this template
inherits the mechanism and renames the project; the steps below then describe the game's release.

## Where the version lives

The version is decided in exactly **one** place:

```cmake
# CMakeLists.txt (repository root)
project(CnaTemplate VERSION 0.1.0 LANGUAGES C CXX)
set(CNA_TEMPLATE_VERSION_PRERELEASE "")   # e.g. "beta.1"; empty on a final release
```

`project(VERSION …)` accepts numeric components only, so the pre-release identifier sits beside it
and the two are joined into `CNA_TEMPLATE_VERSION_STRING` (`0.1.0`, or `0.2.0-beta.1`).
`CNA_TEMPLATE_VERSION_PRERELEASE` is deliberately a normal variable and not a cache entry: a cached
copy would keep an existing build directory reporting the previous release after a bump.

Everything else derives from that:

| Consumer | How it gets the version |
|---|---|
| C code | `#include "CnaTemplate/Version.h"` → `cna_template_version_string()`, `CNA_TEMPLATE_VERSION_MAJOR`, … |
| The game's console banner | `cna-c-template <version> on CNA <CNA version>` |
| The configure banner | `-- cna-c-template: version <x.y.z>` |

`CnaTemplate/Version.h` is **generated** by `cmake/CnaTemplateVersion.cmake` from
`cmake/templates/Version.h.in` into `<build>/generated/include/CnaTemplate/Version.h`. Never
edit the generated file, and never hard-code the version anywhere else.

Two copies are maintained by hand and must be updated as part of a bump:

- `CHANGELOG.md` — the release entry and its link definitions at the bottom.
- `README.md` — the *Version* section.

## Numbers that are *not* the template version

- **CNA's version** (`CNA/Version.hpp`, `CNA::getVersionString()`) and the versions of
  sharp-runtime, easy-gl and meta-gl are the siblings' own. The template *requires* them (below)
  but does not share their number.
- **The CNA C ABI version** (`CNA_ABI_VERSION_*` in `CNA/C/abi.h`) is the binary contract this C
  game is compiled against. It is CNA's number and moves with CNA's C API, not with this template.

## The sibling releases a template release requires

CNA and sharp-runtime are sibling checkouts consumed with `add_subdirectory`, and easy-gl and
meta-gl join only when a GL-family renderer (`OPENGLES3`, `OPENGL33`, `WEBGL2`) is built. A template
tag selects none of them, so each release records them twice:

- `cmake/CnaTemplateDependencies.cmake` — the **versions** (`CNA_TEMPLATE_REQUIRED_*_VERSION`).
  Configuration reads each sibling's generated `Version.hpp` right after CNA is added and refuses
  a checkout that declares neither the required version nor a later patch release of the same
  minor line; `-DCNA_TEMPLATE_CHECK_DEPENDENCY_VERSIONS=OFF` downgrades that to a warning.
- `dependencies.lock` — the exact **commits**, in the `NAME|OWNER/REPOSITORY|DIRECTORY|REVISION`
  records `tools/dependency_pins.py` parses. CMake verifies every consumed checkout against it
  at configure time (`cmake/CnaDependencyPin.cmake`); `-DCNA_ALLOW_UNPINNED=ON` acknowledges a
  deliberate build outside the baseline. CI clones the same pins.

CNA 0.1.0 itself enforces its own sharp-runtime/easy-gl/meta-gl versions
(`cna/cmake/DependencyVersions.cmake`), so the four siblings move together.

## Pre-1.0 policy

While the major version is 0, a minor bump may change anything. Pre-release identifiers are
`alpha.N` → `beta.N` → `rc.N`, ordered as SemVer orders them.

## Cutting a release

1. **Choose the version.** Edit `project(CnaTemplate VERSION …)` and/or
   `CNA_TEMPLATE_VERSION_PRERELEASE` in the root `CMakeLists.txt`.
2. **Require the sibling releases.** Release CNA (and, through it, sharp-runtime, easy-gl and
   meta-gl) first; check their tags out next to this repository; set the versions in
   `cmake/CnaTemplateDependencies.cmake` and the commits in `dependencies.lock`; run
   `python3 tools/gen_renderer_files.py --check` so the manifest still matches CNA's renderer
   list, and `python3 -m unittest discover -s test` for the template's own checks.
3. **Write the changelog entry.** Move what is under `## [Unreleased]` into a new
   `## [x.y.z] — YYYY-MM-DD` section in `CHANGELOG.md`, with a *Dependencies* table naming the
   sibling versions and commits, and add the link definitions at the bottom.
4. **Update `README.md`** — the *Version* section.
5. **Build and test** in the existing shared build directories (the parent `CLAUDE.md` build
   rules: shared ccache, no new directories). The reproducible gate is the one CI runs, the
   `headless` preset with its CTest contract, and the widest native proof is the Linux
   multi-renderer build; windowed smoke runs go on CNA's private display, never on the desktop:

   ```bash
   export CCACHE_DIR=/rv/cnaccache CCACHE_BASEDIR=/rv
   cmake --preset headless && cmake --build --preset headless --parallel
   python3 tools/verify_ctest_contract.py --test-dir build-headless --config Debug
   ctest --preset headless
   cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCNA_GRAPHICS_RENDERER=OPENGLES3 \
       -DCNA_GRAPHICS_RENDERERS="OPENGLES3;OPENGL33;VULKAN;WEBGPU;SDL_GPU;FNA3D;SDL_RENDERER;SOFTWARE;HEADLESS;STUB" \
       -DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DCMAKE_C_COMPILER_LAUNCHER=ccache
   cmake --build build --parallel
   ```

   and the web build (`source ~/emsdk/emsdk_env.sh` first):

   ```bash
   emcmake cmake -S . -B build-web-webgl2 -G Ninja -DCMAKE_BUILD_TYPE=Release \
       -DCNA_GRAPHICS_RENDERER=WEBGL2 -DCNA_GRAPHICS_RENDERERS="WEBGL2;WEBGPU"
   cmake --build build-web-webgl2 --parallel
   ```

   The configure output prints `-- cna-c-template: version <x.y.z>` and one accepted-version line
   per sibling — check them all. Every test must pass.
6. **Commit** the version-bearing files by explicit name (`CMakeLists.txt`,
   `cmake/CnaTemplateDependencies.cmake`, `dependencies.lock`, `CHANGELOG.md`, `README.md`),
   never `git add -A`.
7. **Tag** with a `v` prefix and an annotated tag:

   ```bash
   git tag -a v0.1.0 -m "cna-c-template 0.1.0"
   ```

   The tag string carries the `v`; `CNA_TEMPLATE_VERSION_STRING` never does.
8. **Push only when the project owner asks**, and push the tag explicitly. Never move or recreate
   a pushed tag; release the next patch version instead.
9. **Open the next cycle** by adding an empty `## [Unreleased]` section back to `CHANGELOG.md`.
