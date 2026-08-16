# cna-c-template

A starter project for **[CNA](https://github.com/openeggbert/cna)** — a reimplementation of the XNA 4.0 game framework, using the **C binding**.

Clone it, pick a renderer, build, and you have a running game loop with content loading, sprite drawing and input. Then delete `HelloGame` and write your own.

---

## Quick start

```bash
# CNA and its dependencies are sibling checkouts, not submodules.
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
| Siblings | `../cna`, `../sharp-runtime`, `../cnabinding` |
| CNA submodules | `third_party/SDL`, `SDL_image`, `SDL_mixer`, `enet` |

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
