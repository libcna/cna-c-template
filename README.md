# cna-c-template

> **Status: builds and runs.** Verified on 2026-08-17 against the CNA C ABI on the
> `feature/binding` branch. Four presets build and run with no CNA call reporting a
> failure, and both drawing paths were confirmed **on screen**, not just by exit
> code: `sdl-renderer` (2D — the bouncing logo and the renderer banner),
> `opengles3` (3D — the rotating textured cube), plus `headless` and `software`,
> which execute their paths without presenting anywhere. The remaining presets are
> generated from the renderer manifest and are **not** individually verified here.


A starter project for **[CNA](https://github.com/openeggbert/cna)** — a reimplementation of the XNA 4.0 game framework, using the **C binding**.

Clone it, pick a renderer, build, and you have a running game loop with content loading, sprite drawing and input. Then delete `HelloGame` and write your own.

---

## Quick start

```bash
# CNA and its dependencies are sibling checkouts, not submodules. The C ABI this
# template binds against currently lives on cnabinding's feature/binding branch.
git clone https://github.com/openeggbert/cna.git
git clone https://github.com/openeggbert/sharp-runtime.git
git clone https://github.com/openeggbert/cnabinding.git
git clone https://github.com/openeggbert/cna-c-template.git

# CNA vendors SDL as submodules and needs them present.
git -C cna submodule update --init \
    third_party/SDL third_party/SDL_image third_party/SDL_mixer third_party/enet

cd cna-c-template
cmake --preset headless
cmake --build --preset headless -j3
ctest --preset headless
```

`headless` needs no GPU, no window and no display server, which makes it the fastest way to prove the toolchain works. For something you can actually look at, use `sdl-renderer` (most portable) or `opengles3`.

---

## Prerequisites

**Always:**

| | |
| --- | --- |
| CMake | 3.23 or newer |
| Compiler | C11 (GCC, Clang, MSVC) |
| Siblings | `../sharp-runtime`, and CNA at `../cnabinding`, `../../cnabinding`, `../cna` or `../../cna` — the first that exists wins, and `-DCNA_ROOT_DIR=` overrides the search |
| CNA submodules | `third_party/SDL`, `SDL_image`, `SDL_mixer`, `enet` |
| Optional | `third_party/draco`. When it is not initialised the template configures with `CNA_ENABLE_DRACO=OFF` and says so, rather than failing the configure. |

---

## Project structure

- `game/src/`: C source files.
- `game/include/`: C header files.
- `Content/`: Game assets (textures, etc.).
- `android/`: Android Studio project glue.
- `cmake/`: Renderer selection logic and presets.

---

## Building

This template uses CMake presets for easy building across platforms.

### Linux
```bash
cmake --preset opengles3
cmake --build --preset opengles3
./build-opengles3/HelloGame
```

### Windows (Cross-compiling from Linux)
```bash
cmake --preset mingw-sdl-renderer
cmake --build --preset mingw-sdl-renderer
wine ./build-mingw-sdl-renderer/HelloGame.exe
```

### Web (Emscripten)
```bash
emcmake cmake --preset web-webgl2
cmake --build --preset web-webgl2
# Open build-web-webgl2/HelloGame.html in a browser
```

### Android
Open the `android/` directory in Android Studio. Ensure `cna`, `sharp-runtime`, and `cnabinding` are siblings of this project.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
