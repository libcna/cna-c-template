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
git clone https://github.com/openeggbert/cna.git
git clone https://github.com/openeggbert/sharp-runtime.git

git -C cna checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision CNA)"
git -C sharp-runtime checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision SHARP_RUNTIME)"
git -C cna submodule update --init \
    third_party/SDL third_party/SDL_image third_party/SDL_mixer

python3 cna-c-template/tools/dependency_pins.py \
    --dependencies-dir . --check CNA SHARP_RUNTIME

cd cna-c-template
cmake --preset headless
cmake --build --preset headless -j3
ctest --preset headless
```

`headless` needs no GPU, window, or display server. The test preset runs two tests: a successful
three-frame smoke run and a deliberate draw-failure regression whose non-zero exit is required.

For a visible portable window, use the `sdl-renderer` preset. `opengles3` additionally needs
`easy-gl` and `meta-gl` beside CNA:

```bash
cd ..
git clone https://github.com/openeggbert/easy-gl.git
git clone https://github.com/openeggbert/meta-gl.git
git -C easy-gl checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision EASY_GL)"
git -C meta-gl checkout "$(python3 cna-c-template/tools/dependency_pins.py --revision META_GL)"
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

CMake and Android use the same CNA discovery order: `../cna`, then `../../cna`, relative to this
repository. This supports both an ordinary sibling workspace and this repository living under an
`_bindings/` directory. Override discovery with `-DCNA_ROOT_DIR=/path/to/cna` in CMake or
`-PcnaRootDir=/path/to/cna` in Gradle. Relative overrides are resolved from the template root.
Android also accepts `-PcnaSharpRuntimeRootDir=/path/to/sharp-runtime` when CNA and sharp-runtime
are not siblings; desktop CMake exposes the equivalent `CNA_SHARP_RUNTIME_ROOT` cache variable.

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

The `windows-directx11` and `windows-directx12` presets are MinGW cross-builds from Linux. They
have build presets but intentionally no CTest presets because Linux cannot execute the resulting
Windows binaries directly. If Wine and the required runtime DLLs are available, run the produced
`.exe --smoke-test` explicitly and inspect its exit status.

For web builds, activate Emscripten so `EMSDK` is set; the generated preset already supplies the
toolchain file:

```bash
cmake --preset web-webgl2
cmake --build --preset web-webgl2
```

Web presets also omit CTest presets because the output requires a browser runtime.

## Android

Android builds require JDK 17 or newer plus these Android SDK components:

- Android platform / compile SDK 35;
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

The pinned CNA revision currently has an upstream native-build blocker under NDK Clang: its strict
C-API target promotes diagnostics in CNA headers (including an implicitly deleted default
constructor, mismatched class/struct declarations, and missing override annotations) to errors.
Gradle configuration, resource/Java compilation, and signing behavior remain verifiable, but the
APK cannot complete until CNA fixes those dependency-side diagnostics. This template deliberately
does not suppress them or rewrite the CNA checkout; see [docs/compatibility.md](docs/compatibility.md).

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

`dependencies.lock` is the authoritative compatibility baseline. The quick start checks out its
exact revisions, `tools/dependency_pins.py --check` verifies revision and worktree cleanliness, and
CI reads the same file before checking CNA's renderer list. There is no duplicated workflow pin.

Using a newer sibling checkout is an intentional compatibility test, not an implicit fallback.
Update the lock only after the generator, both smoke tests, and relevant platform builds pass. The
template-side compatibility measures and their upstream status are documented in
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
copied next to native executables and packaged as Android assets.

## Repository checks

```bash
python3 -m py_compile tools/dependency_pins.py tools/gen_renderer_files.py
python3 -m unittest discover -s test -v
python3 tools/gen_renderer_files.py --check
git diff --check
```

## License

This project is licensed under the MIT License; see [LICENSE](LICENSE).
