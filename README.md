# cna-c-template

A starter project for [CNA](https://github.com/openeggbert/cna) using CNA's native C binding. It
contains a small game loop, texture loading, 2D and capability-gated 3D drawing, Android glue, and
a smoke test that exits automatically. Every important CNA failure is returned through the game
callback, so a failed frame makes the process and CTest fail.

## Quick start

The reproducible baseline is recorded once in `dependencies.lock`. The commands below consume
those pins rather than cloning dependency HEAD:

```bash
mkdir cna-workspace
cd cna-workspace

git clone https://github.com/openeggbert/cna-c-template.git
git clone "$(python3 cna-c-template/tools/dependency_pins.py --url CNA)" \
    "$(python3 cna-c-template/tools/dependency_pins.py --directory CNA)"
git clone "$(python3 cna-c-template/tools/dependency_pins.py --url SHARP_RUNTIME)" \
    "$(python3 cna-c-template/tools/dependency_pins.py --directory SHARP_RUNTIME)"

git -C "$(python3 cna-c-template/tools/dependency_pins.py --directory CNA)" \
    checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision CNA)"
git -C "$(python3 cna-c-template/tools/dependency_pins.py --directory SHARP_RUNTIME)" \
    checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision SHARP_RUNTIME)"
git -C "$(python3 cna-c-template/tools/dependency_pins.py --directory CNA)" \
    submodule update --init \
    third_party/SDL third_party/SDL_image third_party/SDL_mixer

python3 cna-c-template/tools/dependency_pins.py \
    --dependencies-dir . --check CNA SHARP_RUNTIME

cd cna-c-template
cmake --preset headless
cmake --build --preset headless -j3
python3 tools/verify_ctest_contract.py --test-dir build-headless --config Debug
ctest --preset headless
```

`headless` needs no GPU, window, or display server. The test preset runs exactly two tests: a
successful three-frame smoke run and a deliberate draw failure. The latter only passes after the
draw callback injects `CNA_RESULT_INVALID_HANDLE`, the game loop returns `CNA_RESULT_CALLBACK`,
the game handle is released while preserving that callback result, and the test-only process status
is exactly 86; an arbitrary failure is rejected.

For a visible portable window, use the `sdl-renderer` preset. `opengles3` additionally needs
`easy-gl` and `meta-gl` beside CNA:

```bash
cd ..
git clone "$(python3 cna-c-template/tools/dependency_pins.py --url EASY_GL)" \
    "$(python3 cna-c-template/tools/dependency_pins.py --directory EASY_GL)"
git clone "$(python3 cna-c-template/tools/dependency_pins.py --url META_GL)" \
    "$(python3 cna-c-template/tools/dependency_pins.py --directory META_GL)"
git -C "$(python3 cna-c-template/tools/dependency_pins.py --directory EASY_GL)" \
    checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision EASY_GL)"
git -C "$(python3 cna-c-template/tools/dependency_pins.py --directory META_GL)" \
    checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision META_GL)"
python3 cna-c-template/tools/dependency_pins.py \
    --dependencies-dir . --check CNA SHARP_RUNTIME EASY_GL META_GL
cd cna-c-template
cmake --preset opengles3
cmake --build --preset opengles3 -j3
ctest --preset opengles3
```

The optional Draco submodule is not needed for this example. If it is absent, the template
configures `CNA_ENABLE_DRACO=OFF` and reports that decision.

## Prerequisites

| Requirement | Version or layout |
| --- | --- |
| CMake | 3.23 or newer for desktop/web configuration |
| Compilers | A C11 compiler for the game and a C++23 compiler for CNA and sharp-runtime |
| Python | Python 3.9 or newer for generators and pin checks |
| Dependencies | `cna` and `sharp-runtime` in one dependency directory; `easy-gl`/`meta-gl` only for the five EasyGL renderers; `free-direct` only for `FREEDIRECT` |
| CNA submodules | `third_party/SDL`, `SDL_image`, and `SDL_mixer`; `draco` is optional here and ENet is tracked normally |
| Renderer SDKs | See the dependency column in [docs/renderers.md](docs/renderers.md) |

The verified pinned Linux baseline uses GCC 14. The pinned CNA C-API target does not compile under
GCC 13 because its own `-Werror` policy rejects hidden media `Equals` overloads; this template does
not suppress that diagnostic. See [docs/compatibility.md](docs/compatibility.md) for the exact
upstream boundary.

CMake and Android use the same CNA discovery order: `../cna`, then `../../cna`, relative to this
repository. This supports both an ordinary sibling workspace and this repository living under an
`_bindings/` directory. Override discovery with `-DCNA_ROOT_DIR=/path/to/cna` in CMake or
`-PcnaRootDir=/path/to/cna` in Gradle. Relative overrides are resolved from the template root.
Android also accepts `-PcnaSharpRuntimeRootDir=/path/to/sharp-runtime` when CNA and sharp-runtime
are not siblings; desktop CMake exposes the equivalent `CNA_SHARP_RUNTIME_ROOT` cache variable.
Every CNA Git checkout selected by CMake or Gradle is compared with the lock during configuration.
See [Dependency policy](#dependency-policy) for the explicit compatibility-test opt-in and
source-archive behavior.

## Building

List the generated configure, build, and runnable test presets with:

```bash
cmake --list-presets
cmake --list-presets=build
cmake --list-presets=test
```

On native Linux or Windows, configure and build a renderer such as:

```bash
cmake --preset sdl-renderer
cmake --build --preset sdl-renderer
ctest --preset sdl-renderer
```

On Windows, `directx11` and `directx12` are native configure/build/test presets. The separate
`windows-directx11` and `windows-directx12` presets are MinGW cross-builds from Linux. They have
build presets but intentionally no CTest presets because Linux cannot execute the resulting Windows
binaries directly. If Wine and the required runtime DLLs are available, run the produced executable
with `--smoke-test` explicitly and inspect its exit status.

For web builds, activate Emscripten so `EMSDK` is set; the generated preset already supplies the
toolchain file:

```bash
cmake --preset web-webgl2
cmake --build --preset web-webgl2
```

Web presets also omit CTest presets because the output requires a browser runtime.
Native preset visibility is derived from every desktop platform in `cmake/renderers.json`: for
example, Linux + Windows renderers are hidden on macOS, while Metal is shown only on macOS.
Configure, build, and runnable test presets carry the same condition, so unsupported or orphan
presets do not leak through inheritance. Native and MinGW build presets explicitly select `Debug`,
web build presets select `Release`, and native test presets select the matching build
configuration. `ctest --preset <native-preset>` therefore works directly with single-config and
multi-config generators such as Visual Studio and Ninja Multi-Config. Android uses Gradle rather
than desktop CMake presets.

## Android

Android builds require JDK 17 or newer plus these Android SDK components:

- Android platform / compile SDK 35;
- Android build-tools `35.0.0`;
- NDK `29.0.14206865`;
- Android SDK CMake `4.1.2`.

Set `sdk.dir` in `android/local.properties` (copy `local.properties.template`) or export
`ANDROID_HOME`, then open `android/` in Android Studio or run:

```bash
cd android
./gradlew assembleDebug
```

Debug builds require no release credentials. CNA uses its Android default renderer
(`SDL_RENDERER`) unless `-PcnaRenderer=OPENGLES3` or another Android-capable renderer is supplied.
The EasyGL renderers still require `easy-gl` and `meta-gl` beside CNA.

The pinned CNA revision currently has an upstream native-build blocker under NDK Clang. Its own
strict C-API target promotes CNA header diagnostics (`-Wmismatched-tags`,
`-Wdefaulted-function-deleted`, `-Woverloaded-virtual`, and
`-Winconsistent-missing-override`) to errors. Required CI therefore validates the Wrapper, Gradle
configuration/help/tasks, debug Java/resources, the arm64 CMake model and exported `SDL_main` entry
object, and the exact release-signing negative path. It does not claim an APK: native compilation
stops in `cna_c_api` before `libmain.so` can link or APK packaging can run. This template
deliberately does not suppress those diagnostics or rewrite CNA; see
[docs/compatibility.md](docs/compatibility.md) for exact files and evidence. A manual CI dispatch
with `verify_android_native` enabled runs the unsuppressed `assembleDebug` path; make that step
required when the locked CNA baseline compiles cleanly.

### Android release signing

Create a keystore outside version control, then create the ignored file `android/key.properties`:

```properties
storeFile=release-key.jks
storePassword=replace-me
keyAlias=release
keyPassword=replace-me
```

Relative `storeFile` paths start in `android/`. A real project should preferably source secrets
from protected CI credentials rather than commit them. `assembleRelease`/`bundleRelease` reaches
the template's `validateCnaReleaseSigning` task and fails with the missing file, key, or keystore
path; Gradle sync, help, and debug tasks remain usable without signing material.

The committed wrapper is generated by Gradle 8.12. Both the wrapper JAR and the distribution ZIP
have published SHA-256 values; `distributionSha256Sum` pins the latter in
`android/gradle/wrapper/gradle-wrapper.properties`.

## Dependency policy

`dependencies.lock` is the authoritative compatibility baseline. Each record contains the GitHub
repository, local directory, and exact revision. The quick start consumes all three fields,
`tools/dependency_pins.py --check` verifies revision and worktree cleanliness, and CI reads the same
records for checkout. There is no duplicated workflow repository or revision pin.

Ordinary CMake and Gradle configuration inspect both always-used checkouts, CNA and sharp-runtime.
CMake also verifies the source checkout behind any EasyGL, MetaGL, or FreeDirect target that CNA
actually creates; Gradle performs the corresponding early check when `-PcnaRenderer` explicitly
selects one of those families, and the nested CMake configure remains authoritative for CNA's
platform default. A dirty or different Git revision fails unless an intentional compatibility test
is explicitly acknowledged with
`-DCNA_ALLOW_UNPINNED=ON` (CMake) or `-PcnaAllowUnpinned=true` (Gradle; it forwards the matching
CMake option). Relative and absolute root overrides remain supported, but an override is not itself
an acknowledgement. A consumed source archive without `.git` metadata remains usable and produces
a clear warning that its pin cannot be verified; Git is not mandatory for that consumption mode.
Update the lock only after the generator, both smoke tests, and relevant platform builds pass. The
template-side compatibility measures and upstream status are documented in
[docs/compatibility.md](docs/compatibility.md).

## Renderer metadata

`cmake/renderers.json` is the template-side source of truth for renderer metadata. CNA remains the
source of truth for renderer names. Regenerate and verify derived files with:

```bash
python3 tools/gen_renderer_files.py
python3 tools/gen_renderer_files.py --check
```

`--check` separately verifies generated freshness and semantic agreement with a discovered CNA
checkout. Generated bytes never contain environment-dependent verification status. CI matrix
queries reject unknown platforms and tiers; a valid platform/tier combination with no renderers is
an intentional successful `[]`.

## Making this your own project

1. Change `CNA_TEMPLATE_APP_NAME` in `CMakeLists.txt` (or pass it as a cache variable).
2. Rename `HelloGame.c`, `Program.c`, and the public header, then update `CNA_TEMPLATE_SOURCES`.
3. Replace the package, activity, labels, icons, and `applicationId` under `android/`.
4. Replace `Content/logo.png` and the example draw/update code.
5. Create new release signing credentials; never reuse the template values above.

Application C sources live under `game/src/` and headers under `game/include/`. `Content/` is
copied next to native executables and packaged as Android assets. The CTest identities
`CnaCTemplateSmoke` and `CnaCTemplateFailurePropagation` are intentionally stable infrastructure
names, and CI configures its executable name through `CNA_TEMPLATE_CI_APP_NAME`; changing the
application's default `CNA_TEMPLATE_APP_NAME` therefore requires no workflow edit.

## Repository checks

```bash
python3 -m py_compile tools/dependency_pins.py tools/gen_renderer_files.py \
    tools/verify_ctest_contract.py
python3 -m unittest discover -s test -v
python3 tools/gen_renderer_files.py --check
# After configuring build-headless:
python3 tools/verify_ctest_contract.py --test-dir build-headless --config Debug
ctest --test-dir build-headless -C Debug --output-on-failure
git diff --check
```

`--config` is required for a multi-config tree; the verifier refuses to guess. It is optional for
a single-config tree, but when supplied it must exactly match the tree's non-empty
`CMAKE_BUILD_TYPE`. If `CMAKE_BUILD_TYPE` is empty, omit `--config` because the verifier cannot
truthfully associate that tree with a named configuration. When invoking CTest by build directory
instead of through a generated test preset, pass the same configuration with `ctest -C Debug`.

## License

This project is licensed under the MIT License; see [LICENSE](LICENSE).
