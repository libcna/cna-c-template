<!-- GENERATED FILE — do not edit by hand. -->
<!-- Source: cmake/renderers.json — regenerate with tools/gen_renderer_files.py -->

# CNA renderers

CNA currently exposes **10 renderers**. You pick one at configure time with a single cache variable:

```bash
cmake -S . -B build -DCNA_GRAPHICS_RENDERER=OPENGLES3
```

If you set nothing, CNA chooses for you: `WEBGL2` on the web, `SDLGPU` on Windows, macOS and iOS, and `OPENGLES3` everywhere else (Linux, Android and the BSDs).

## How to read this

**Platforms** are where the renderer is supported. cna-template refuses, with an explanation, to configure a renderer for a platform not listed here. A few renderers additionally have *experimental* platforms — CNA permits them but does not support them, so the template warns instead of refusing.

**Display** says whether the renderer opens a window. Renderers marked **none** (`HEADLESS`, `SOFTWARE`, `STUB`) need no X server, no GPU and no video driver, which makes them the right choice for CI and servers. Note that `SOFTWARE` genuinely rasterizes but presents nowhere.

**Scope** is `2D` or `2D+3D`. On a 2D-only renderer the 3D calls (for example `cna_vertex_buffer_create(...)`, `cna_graphics_device_draw_user_primitives(...)`, and depth/stencil operations) return `CNA_RESULT_NOT_SUPPORTED`. Query `cna_graphics_device_supports_capability(...)` with `CNA_GRAPHICS_CAPABILITY_THREE_D` or the narrower capability at runtime rather than testing the renderer's name.

**CI tier** is scheduling metadata for this template, not evidence of CNA support or a claim that every renderer was run in the current checkout: *baseline selection*, *broad-matrix candidate*, *on demand*, or *not on CI runners*.

## SDL

| Renderer | Platforms | Scope | Display | Dependency | CI tier | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `SDLGPU` | Linux, Windows, macOS | 2D+3D | window | none | broad-matrix candidate | CNA's default on Windows, macOS and iOS. SDL3 selects Vulkan, Direct3D 12 or Metal internally. |

## OpenGL family (shared EasyGL implementation)

| Renderer | Platforms | Scope | Display | Dependency | CI tier | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `OPENGLES3` | Linux, Windows, macOS, Android | 2D+3D | window | sibling ../easy-gl (which needs ../meta-gl) | baseline selection | CNA's default on Linux, Android and other non-web targets. Internally EasyGL. |
| `OPENGL33` | Linux, Windows, macOS | 2D+3D | window | sibling ../easy-gl (which needs ../meta-gl) | broad-matrix candidate | Internally EasyGL, desktop GL 3.3 core profile. |
| `WEBGL2` | Web | 2D+3D | window | sibling ../easy-gl (which needs ../meta-gl) | broad-matrix candidate | CNA's default renderer under Emscripten. Internally EasyGL. |

## Modern GPU APIs

| Renderer | Platforms | Scope | Display | Dependency | CI tier | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `WEBGPU` | Linux, Windows, macOS, Web | 2D+3D | window | wgpu-native binary release, auto-downloaded | broad-matrix candidate | Native wgpu-native on desktop. Under Emscripten it builds through the Dawn (emdawnwebgpu) port, as CNA's own web CI does, alongside WEBGL2 in one -DCNA_GRAPHICS_RENDERERS="WEBGL2;WEBGPU" build; supported, and the browser then needs WebGPU. |

## CPU / diagnostic

| Renderer | Platforms | Scope | Display | Dependency | CI tier | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `HEADLESS` | Linux, Windows, macOS, Android (+ Web experimental) | 2D+3D | **none** | none | baseline selection | No GPU and no window at all. The right choice for CI and servers. |
| `SOFTWARE` | Linux, Windows, macOS, Android (+ Web experimental) | 2D+3D | **none** | none | baseline selection | Real CPU rasterizer. Creates no window, so Present() puts nothing on screen -- it is a compute/test renderer, not a display one. |
| `STUB` | Linux, Windows, macOS, Android (+ Web experimental) | 2D+3D | **none** | none | baseline selection | Deliberate no-op renderer. Draws nothing, touches no GPU or window. |

## Portable middleware

| Renderer | Platforms | Scope | Display | Dependency | CI tier | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `FNA3D` | Linux, Windows, macOS | 2D+3D | window | FNA3D + MojoShader via FetchContent; needs Python3 | broad-matrix candidate | The XNA-shaped C library FNA renders through. Picks SDL_GPU/D3D11/GL internally at runtime; SDL_GPU here is FNA3D's technology name, not CNA's SDLGPU renderer identity. |

## DirectX

| Renderer | Platforms | Scope | Display | Dependency | CI tier | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `DIRECTX9` | Windows | 2D+3D | window | d3d9.h | not on CI runners | Direct3D 9. |

## Presets

Renderers in common use have a ready-made preset; the rest are selected with `-DCNA_GRAPHICS_RENDERER=<NAME>` against any preset or a plain build directory. Every one of the 10 renderers above is selectable either way.

```bash
cmake --list-presets                 # what is available
cmake --preset opengles3             # configure
cmake --build --preset opengles3     # build
ctest --preset opengles3             # smoke test
```

Native configure, build, and runnable test presets all receive the same host condition, derived from every supported desktop platform above. Android uses Gradle instead. Web presets are cross-build routes available on Linux, Windows, and macOS hosts. Runnable test presets treat zero discovered tests as an error. Native and MinGW build presets select `Debug`; web build presets select `Release`. Native test presets select the same configuration as their associated build preset, including with multi-config generators.

Windows-only renderers have native Windows presets (`directx9`) plus MinGW cross-build routes on Linux (`windows-directx9`). Web and MinGW routes intentionally have no CTest preset because their binaries cannot execute directly on the configuring host.
