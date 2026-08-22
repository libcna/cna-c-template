#include "HelloGame/HelloGame.h"
#include <stdbool.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXIMUM_2D_LOGO_SCALE 1.08f
#define RENDERER_BANNER_SECONDS 5.0f
#define ANIMATION_SPEED 2.0f

typedef struct {
    uint8_t rows[7];
} GlyphRows;

static GlyphRows GetGlyphRows(char character) {
    GlyphRows result;
    switch (character) {
        case 'A': { uint8_t r[] = {0x0e, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11}; memcpy(result.rows, r, 7); break; }
        case 'B': { uint8_t r[] = {0x1e, 0x11, 0x11, 0x1e, 0x11, 0x11, 0x1e}; memcpy(result.rows, r, 7); break; }
        case 'C': { uint8_t r[] = {0x0e, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0e}; memcpy(result.rows, r, 7); break; }
        case 'D': { uint8_t r[] = {0x1e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1e}; memcpy(result.rows, r, 7); break; }
        case 'E': { uint8_t r[] = {0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x1f}; memcpy(result.rows, r, 7); break; }
        case 'F': { uint8_t r[] = {0x1f, 0x10, 0x10, 0x1e, 0x10, 0x10, 0x10}; memcpy(result.rows, r, 7); break; }
        case 'G': { uint8_t r[] = {0x0e, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0e}; memcpy(result.rows, r, 7); break; }
        case 'H': { uint8_t r[] = {0x11, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11}; memcpy(result.rows, r, 7); break; }
        case 'I': { uint8_t r[] = {0x1f, 0x04, 0x04, 0x04, 0x04, 0x04, 0x1f}; memcpy(result.rows, r, 7); break; }
        case 'J': { uint8_t r[] = {0x07, 0x02, 0x02, 0x02, 0x12, 0x12, 0x0c}; memcpy(result.rows, r, 7); break; }
        case 'K': { uint8_t r[] = {0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11}; memcpy(result.rows, r, 7); break; }
        case 'L': { uint8_t r[] = {0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1f}; memcpy(result.rows, r, 7); break; }
        case 'M': { uint8_t r[] = {0x11, 0x1b, 0x15, 0x15, 0x11, 0x11, 0x11}; memcpy(result.rows, r, 7); break; }
        case 'N': { uint8_t r[] = {0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11}; memcpy(result.rows, r, 7); break; }
        case 'O': { uint8_t r[] = {0x0e, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e}; memcpy(result.rows, r, 7); break; }
        case 'P': { uint8_t r[] = {0x1e, 0x11, 0x11, 0x1e, 0x10, 0x10, 0x10}; memcpy(result.rows, r, 7); break; }
        case 'Q': { uint8_t r[] = {0x0e, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0d}; memcpy(result.rows, r, 7); break; }
        case 'R': { uint8_t r[] = {0x1e, 0x11, 0x11, 0x1e, 0x14, 0x12, 0x11}; memcpy(result.rows, r, 7); break; }
        case 'S': { uint8_t r[] = {0x0f, 0x10, 0x10, 0x0e, 0x01, 0x01, 0x1e}; memcpy(result.rows, r, 7); break; }
        case 'T': { uint8_t r[] = {0x1f, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04}; memcpy(result.rows, r, 7); break; }
        case 'U': { uint8_t r[] = {0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0e}; memcpy(result.rows, r, 7); break; }
        case 'V': { uint8_t r[] = {0x11, 0x11, 0x11, 0x11, 0x11, 0x0a, 0x04}; memcpy(result.rows, r, 7); break; }
        case 'W': { uint8_t r[] = {0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0a}; memcpy(result.rows, r, 7); break; }
        case 'X': { uint8_t r[] = {0x11, 0x11, 0x0a, 0x04, 0x0a, 0x11, 0x11}; memcpy(result.rows, r, 7); break; }
        case 'Y': { uint8_t r[] = {0x11, 0x11, 0x0a, 0x04, 0x04, 0x04, 0x04}; memcpy(result.rows, r, 7); break; }
        case 'Z': { uint8_t r[] = {0x1f, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1f}; memcpy(result.rows, r, 7); break; }
        case '0': { uint8_t r[] = {0x0e, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0e}; memcpy(result.rows, r, 7); break; }
        case '1': { uint8_t r[] = {0x04, 0x0c, 0x04, 0x04, 0x04, 0x04, 0x0e}; memcpy(result.rows, r, 7); break; }
        case '2': { uint8_t r[] = {0x0e, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1f}; memcpy(result.rows, r, 7); break; }
        case '3': { uint8_t r[] = {0x1e, 0x01, 0x01, 0x0e, 0x01, 0x01, 0x1e}; memcpy(result.rows, r, 7); break; }
        case '4': { uint8_t r[] = {0x02, 0x06, 0x0a, 0x12, 0x1f, 0x02, 0x02}; memcpy(result.rows, r, 7); break; }
        case '5': { uint8_t r[] = {0x1f, 0x10, 0x10, 0x1e, 0x01, 0x01, 0x1e}; memcpy(result.rows, r, 7); break; }
        case '6': { uint8_t r[] = {0x0e, 0x10, 0x10, 0x1e, 0x11, 0x11, 0x0e}; memcpy(result.rows, r, 7); break; }
        case '7': { uint8_t r[] = {0x1f, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08}; memcpy(result.rows, r, 7); break; }
        case '8': { uint8_t r[] = {0x0e, 0x11, 0x11, 0x0e, 0x11, 0x11, 0x0e}; memcpy(result.rows, r, 7); break; }
        case '9': { uint8_t r[] = {0x0e, 0x11, 0x11, 0x0f, 0x01, 0x01, 0x0e}; memcpy(result.rows, r, 7); break; }
        case '_': { uint8_t r[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1f}; memcpy(result.rows, r, 7); break; }
        case '-': { uint8_t r[] = {0x00, 0x00, 0x00, 0x1f, 0x00, 0x00, 0x00}; memcpy(result.rows, r, 7); break; }
        case ' ': { uint8_t r[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}; memcpy(result.rows, r, 7); break; }
        case '(': { uint8_t r[] = {0x02, 0x04, 0x04, 0x04, 0x04, 0x04, 0x02}; memcpy(result.rows, r, 7); break; }
        case ')': { uint8_t r[] = {0x08, 0x04, 0x04, 0x04, 0x04, 0x04, 0x08}; memcpy(result.rows, r, 7); break; }
        default:  { uint8_t r[] = {0x0e, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04}; memcpy(result.rows, r, 7); break; }
    }
    return result;
}

static void AddFace(CNA_VertexPositionTexture* vertices, size_t* next, 
                    CNA_Vector3 topLeft, CNA_Vector3 topRight, 
                    CNA_Vector3 bottomRight, CNA_Vector3 bottomLeft) {
    vertices[(*next)++] = (CNA_VertexPositionTexture){topLeft,     {0.0f, 0.0f}};
    vertices[(*next)++] = (CNA_VertexPositionTexture){topRight,    {1.0f, 0.0f}};
    vertices[(*next)++] = (CNA_VertexPositionTexture){bottomRight, {1.0f, 1.0f}};
    vertices[(*next)++] = (CNA_VertexPositionTexture){topLeft,     {0.0f, 0.0f}};
    vertices[(*next)++] = (CNA_VertexPositionTexture){bottomRight, {1.0f, 1.0f}};
    vertices[(*next)++] = (CNA_VertexPositionTexture){bottomLeft,  {0.0f, 1.0f}};
}

static void CreateLogoCubeVertices(CNA_VertexPositionTexture* vertices) {
    size_t next = 0;
    AddFace(vertices, &next, (CNA_Vector3){-1.0f,  1.0f,  1.0f}, (CNA_Vector3){ 1.0f,  1.0f,  1.0f},
            (CNA_Vector3){ 1.0f, -1.0f,  1.0f}, (CNA_Vector3){-1.0f, -1.0f,  1.0f});
    AddFace(vertices, &next, (CNA_Vector3){ 1.0f,  1.0f, -1.0f}, (CNA_Vector3){-1.0f,  1.0f, -1.0f},
            (CNA_Vector3){-1.0f, -1.0f, -1.0f}, (CNA_Vector3){ 1.0f, -1.0f, -1.0f});
    AddFace(vertices, &next, (CNA_Vector3){ 1.0f,  1.0f,  1.0f}, (CNA_Vector3){ 1.0f,  1.0f, -1.0f},
            (CNA_Vector3){ 1.0f, -1.0f, -1.0f}, (CNA_Vector3){ 1.0f, -1.0f,  1.0f});
    AddFace(vertices, &next, (CNA_Vector3){-1.0f,  1.0f, -1.0f}, (CNA_Vector3){-1.0f,  1.0f,  1.0f},
            (CNA_Vector3){-1.0f, -1.0f,  1.0f}, (CNA_Vector3){-1.0f, -1.0f, -1.0f});
    AddFace(vertices, &next, (CNA_Vector3){-1.0f,  1.0f, -1.0f}, (CNA_Vector3){ 1.0f,  1.0f, -1.0f},
            (CNA_Vector3){ 1.0f,  1.0f,  1.0f}, (CNA_Vector3){-1.0f,  1.0f,  1.0f});
    AddFace(vertices, &next, (CNA_Vector3){-1.0f, -1.0f,  1.0f}, (CNA_Vector3){ 1.0f, -1.0f,  1.0f},
            (CNA_Vector3){ 1.0f, -1.0f, -1.0f}, (CNA_Vector3){-1.0f, -1.0f, -1.0f});
}

typedef struct {
    CNA_Handle graphics;
    CNA_Handle content;
    CNA_Handle spriteBatch;
    CNA_Handle cubeEffect;
    CNA_Handle logoTexture;
    CNA_Handle solidTexture;
    CNA_Vector2 position;
    CNA_Vector2 velocity;
    char rendererName[256];
    float animationSeconds;
    bool supportsThreeD;
    bool supportsDepth;
    bool hasWindow;
    bool smokeTest;
    bool simulateDrawFailure;
    bool drawFailureInjected;
    CNA_Result injectedDrawFailureResult;
    unsigned int drawnFrames;
    char callbackError[768];
} HelloGameData;

static HelloGameData* activeGameData = NULL;

/* Versioned structures are the ABI's forward-compatibility mechanism: the caller states the size
   and version it compiled against, and a route refuses anything it does not recognise. Passing one
   uninitialised does not merely lose the answer -- the call fails and the caller then reads stack
   garbage, which is exactly how this template drew its logo several million pixels off-screen. */
#define CNA_INIT_VERSIONED(value) do { \
    memset(&(value), 0, sizeof(value)); \
    (value).struct_size = (uint32_t)sizeof(value); \
    (value).struct_version = UINT32_C(1); \
} while (0)

static CNA_StringView view(const char* const text) {
    CNA_StringView result;
    result.data = text;
    result.byte_length = (uint64_t)strlen(text);
    return result;
}

static CNA_Result ReportCnaFailure(CNA_Result result, const char* what,
                                   HelloGameData* data, CNA_CallbackError* error) {
    char message[512] = {0};
    uint64_t length = 0U;
    bool hasMessage = false;

    if (result == CNA_RESULT_SUCCESS) {
        return result;
    }

    if (cna_error_copy_last_message(message, (uint64_t)sizeof(message) - 1U, &length) ==
            CNA_RESULT_SUCCESS && length > 0U) {
        size_t safeLength = (size_t)length;
        if (safeLength >= sizeof(message)) {
            safeLength = sizeof(message) - 1U;
        }
        message[safeLength] = '\0';
        hasMessage = true;
    }

    fprintf(stderr, "cna-c-template: %s failed (CNA_Result %d)", what, (int)result);
    if (hasMessage) {
        fprintf(stderr, ": %s", message);
    }
    fprintf(stderr, "\n");
    fflush(stderr);

    if (data != NULL && error != NULL) {
        if (hasMessage) {
            (void)snprintf(data->callbackError, sizeof(data->callbackError),
                           "%s failed: %s", what, message);
        } else {
            (void)snprintf(data->callbackError, sizeof(data->callbackError),
                           "%s failed with CNA_Result %d", what, (int)result);
        }
        error->message = view(data->callbackError);
    }
    return result;
}

static CNA_Result ReportTemplateFailure(CNA_Result result, const char* message,
                                        HelloGameData* data, CNA_CallbackError* error) {
    fprintf(stderr, "cna-c-template: %s\n", message);
    fflush(stderr);
    if (data != NULL && error != NULL) {
        (void)snprintf(data->callbackError, sizeof(data->callbackError), "%s", message);
        error->message = view(data->callbackError);
    }
    return result;
}

static void RecordCleanupFailure(CNA_Result* firstResult, CNA_Result result,
                                 const char* what, HelloGameData* data,
                                 CNA_CallbackError* error) {
    if (result == CNA_RESULT_SUCCESS) {
        return;
    }

    /* A secondary cleanup failure is still worth reporting, but it must not replace the
       callback diagnostic or result that explains why cleanup was necessary. */
    if (*firstResult == CNA_RESULT_SUCCESS) {
        *firstResult = ReportCnaFailure(result, what, data, error);
    } else {
        (void)ReportCnaFailure(result, what, NULL, NULL);
    }
}

#define CNA_TRY(data, error, expression) do { \
    CNA_Result cnaTryResult = (expression); \
    if (cnaTryResult != CNA_RESULT_SUCCESS) { \
        return ReportCnaFailure(cnaTryResult, #expression, (data), (error)); \
    } \
} while (0)

static CNA_Result ReportRendererCapabilities(HelloGameData* data, CNA_CallbackError* error) {
    /* The renderer NAME is for display only -- never branch on it. Behaviour belongs on
       cna_graphics_device_supports_capability, which reports what the renderer can really do
       rather than what its name suggests. */
    CNA_Bool custom_effects = CNA_FALSE;
    CNA_TRY(data, error, cna_graphics_device_supports_capability(
        data->graphics, CNA_GRAPHICS_CAPABILITY_CUSTOM_EFFECTS, &custom_effects));

    CNA_RendererInfo info;
    memset(&info, 0, sizeof(info));
    info.struct_size = (uint32_t)sizeof(info);
    info.struct_version = UINT32_C(1);
    CNA_TRY(data, error, cna_graphics_device_get_renderer_info(data->graphics, &info));

    printf("cna-c-template: renderer %s\n", data->rendererName);
    printf("  window          : %s\n", data->hasWindow ? "yes" : "no (windowless renderer)");
    printf("  3D pipeline     : %s\n", data->supportsThreeD ? "yes" : "no (2D only)");
    printf("  depth/stencil   : %s\n", data->supportsDepth ? "yes" : "no");
    printf("  custom shaders  : %s\n", (custom_effects != CNA_FALSE) ? "yes" : "no");
    printf("  max texture size: %u\n", (unsigned)info.max_texture_dimension);
    fflush(stdout);
    return CNA_RESULT_SUCCESS;
}

static CNA_Result HelloGame_LoadContent(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)time;
    HelloGameData* data = (HelloGameData*)context;

    CNA_TRY(data, error, cna_game_get_graphics_device(game, &data->graphics));
    CNA_TRY(data, error, cna_sprite_batch_create(data->graphics, &data->spriteBatch));
    CNA_TRY(data, error, cna_game_get_content_manager_ext(game, &data->content));
    CNA_TRY(data, error, cna_content_manager_load_texture2d(
        data->content, view("logo"), &data->logoTexture));

    CNA_Color white = CNA_COLOR_WHITE;
    CNA_TRY(data, error, cna_texture2d_create_from_rgba8(
        data->graphics, 1, 1, &white, 1, &data->solidTexture));

    uint64_t name_len = 0;
    CNA_TRY(data, error, cna_graphics_device_copy_renderer_name(
        data->graphics, data->rendererName,
        (uint64_t)sizeof(data->rendererName) - 1U, &name_len));
    /* The count/copy pair never writes a terminator; this buffer is printed as a C string. */
    if (name_len < sizeof(data->rendererName)) {
        data->rendererName[name_len] = '\0';
    }

    uint64_t native_handle = 0;
    CNA_TRY(data, error, cna_game_window_get_native_handle_ext(game, &native_handle));
    data->hasWindow = (native_handle != 0);

    CNA_Bool threeD = CNA_FALSE;
    CNA_TRY(data, error, cna_graphics_device_supports_capability(
        data->graphics, CNA_GRAPHICS_CAPABILITY_THREE_D, &threeD));
    data->supportsThreeD = (threeD != CNA_FALSE);

    CNA_Bool depth = CNA_FALSE;
    CNA_TRY(data, error, cna_graphics_device_supports_capability(
        data->graphics, CNA_GRAPHICS_CAPABILITY_DEPTH_STENCIL_BUFFER, &depth));
    data->supportsDepth = (depth != CNA_FALSE);

    if (data->supportsThreeD) {
        CNA_TRY(data, error, cna_basic_effect_create(data->graphics, &data->cubeEffect));
        CNA_TRY(data, error, cna_basic_effect_set_texture_enabled(data->cubeEffect, CNA_TRUE));
        CNA_TRY(data, error, cna_basic_effect_set_texture(data->cubeEffect, data->logoTexture));
        CNA_TRY(data, error, cna_effect_lights_set_enabled(data->cubeEffect, CNA_FALSE));
        CNA_TRY(data, error, cna_basic_effect_set_vertex_color_enabled(
            data->cubeEffect, CNA_FALSE));
    }

    CNA_Viewport viewport;
    CNA_TRY(data, error, cna_graphics_device_get_viewport(data->graphics, &viewport));
    data->position.x = (float)viewport.width * 0.5f;
    data->position.y = (float)viewport.height * 0.5f;
    data->velocity.x = 104.0f;
    data->velocity.y = 74.0f;

    {
        CNA_Result result = ReportRendererCapabilities(data, error);
        if (result != CNA_RESULT_SUCCESS) {
            return result;
        }
    }

    return CNA_RESULT_SUCCESS;
}

static CNA_Result Draw2DLogo(HelloGameData* data, CNA_CallbackError* error) {
    float motionSeconds = data->animationSeconds * ANIMATION_SPEED;
    float scale = 0.96f + 0.12f * sinf(motionSeconds * 0.65f);
    float rotation = 0.11f * sinf(motionSeconds * 0.55f);
    
    CNA_Texture2DInfo info;
    CNA_INIT_VERSIONED(info);
    CNA_TRY(data, error, cna_texture2d_get_info(data->logoTexture, &info));
    CNA_Vector2 origin = {(float)info.width * 0.5f, (float)info.height * 0.5f};

    CNA_SpriteBatchBeginInfo begin_info;
    memset(&begin_info, 0, sizeof(begin_info));
    begin_info.struct_size = (uint32_t)sizeof(begin_info);
    begin_info.struct_version = UINT32_C(1);
    CNA_TRY(data, error, cna_sprite_batch_begin(data->spriteBatch, &begin_info));

    /* The position-and-scale command, not the destination-rectangle one. The C API's own header
       spells out why they are not interchangeable: with a position, the origin is measured in
       source-texture pixels and the scale applies after that offset, which is exactly what the
       C++ template's Draw(texture, position, ..., origin, scale, ...) does. Computing a
       destination rectangle instead moved the logo and dropped the origin-relative scaling. */
    CNA_SpriteScaledCommand command;
    memset(&command, 0, sizeof(command));
    command.struct_size = (uint32_t)sizeof(command);
    command.struct_version = UINT32_C(1);
    command.texture = data->logoTexture;
    command.position = data->position;
    /* Zero width and height means "the whole texture", the empty optional of the canonical call. */
    command.source.x = 0;
    command.source.y = 0;
    command.source.width = 0;
    command.source.height = 0;
    command.color = CNA_COLOR_WHITE;
    command.rotation = rotation;
    command.origin = origin;
    command.scale.x = scale;
    command.scale.y = scale;
    command.effects = CNA_SPRITE_EFFECT_NONE;
    command.layer_depth = 0.0f;

    CNA_Result result = cna_sprite_batch_submit_scaled_many(data->spriteBatch, &command, 1);
    if (result != CNA_RESULT_SUCCESS) {
        result = ReportCnaFailure(
            result, "cna_sprite_batch_submit_scaled_many", data, error);
        /* End still releases the batch's retained references after a refused submission. */
        CNA_Result endResult = cna_sprite_batch_end(data->spriteBatch);
        RecordCleanupFailure(&result, endResult,
            "cna_sprite_batch_end after failed submission", data, error);
        return result;
    }
    CNA_TRY(data, error, cna_sprite_batch_end(data->spriteBatch));
    return CNA_RESULT_SUCCESS;
}

static CNA_Result Draw3DLogoCube(HelloGameData* data, CNA_CallbackError* error) {
    static CNA_VertexPositionTexture cubeVertices[36];
    static bool verticesCreated = false;
    if (!verticesCreated) {
        CreateLogoCubeVertices(cubeVertices);
        verticesCreated = true;
    }

    CNA_Viewport viewport;
    CNA_TRY(data, error, cna_graphics_device_get_viewport(data->graphics, &viewport));
    float aspectRatio = (float)viewport.width / (float)(viewport.height > 0 ? viewport.height : 1);
    float motionSeconds = data->animationSeconds * ANIMATION_SPEED;
    float scale = 0.88f + 0.10f * sinf(motionSeconds * 0.48f);
    float moveX = 1.15f * sinf(motionSeconds * 0.24f);
    float moveY = 0.70f * sinf(motionSeconds * 0.19f + 1.1f);

    CNA_Matrix mScale, mRotX, mRotY, mRotZ, mTrans, mWorld, mView, mProj;
    CNA_TRY(data, error, cna_matrix_create_scale_xyz(scale, scale, scale, &mScale));
    CNA_TRY(data, error, cna_matrix_create_rotation_x(motionSeconds * 0.22f, &mRotX));
    CNA_TRY(data, error, cna_matrix_create_rotation_y(motionSeconds * 0.31f, &mRotY));
    CNA_TRY(data, error, cna_matrix_create_rotation_z(motionSeconds * 0.13f, &mRotZ));
    CNA_TRY(data, error, cna_matrix_create_translation_xyz(moveX, moveY, 0.0f, &mTrans));

    CNA_TRY(data, error, cna_matrix_multiply(mScale, mRotX, &mWorld));
    CNA_TRY(data, error, cna_matrix_multiply(mWorld, mRotY, &mWorld));
    CNA_TRY(data, error, cna_matrix_multiply(mWorld, mRotZ, &mWorld));
    CNA_TRY(data, error, cna_matrix_multiply(mWorld, mTrans, &mWorld));

    CNA_Vector3 eye = {0.0f, 0.0f, 6.0f};
    CNA_Vector3 target = {0.0f, 0.0f, 0.0f};
    CNA_Vector3 up = {0.0f, 1.0f, 0.0f};
    CNA_TRY(data, error, cna_matrix_create_look_at(eye, target, up, &mView));
    CNA_TRY(data, error, cna_matrix_create_perspective_field_of_view(
        0.78539816339f, aspectRatio, 0.1f, 100.0f, &mProj));

    CNA_TRY(data, error, cna_effect_matrices_set_world(data->cubeEffect, mWorld));
    CNA_TRY(data, error, cna_effect_matrices_set_view(data->cubeEffect, mView));
    CNA_TRY(data, error, cna_effect_matrices_set_projection(data->cubeEffect, mProj));

    CNA_BlendState blendState;
    CNA_INIT_VERSIONED(blendState);
    CNA_TRY(data, error, cna_blend_state_init(CNA_BLEND_STATE_PRESET_OPAQUE, &blendState));
    CNA_TRY(data, error, cna_graphics_device_set_blend_state(data->graphics, &blendState));

    CNA_DepthStencilState dsState;
    CNA_INIT_VERSIONED(dsState);
    CNA_TRY(data, error, cna_depth_stencil_state_init(
        data->supportsDepth ? CNA_DEPTH_STENCIL_STATE_PRESET_DEFAULT
                            : CNA_DEPTH_STENCIL_STATE_PRESET_NONE,
        &dsState));
    CNA_TRY(data, error, cna_graphics_device_set_depth_stencil_state(data->graphics, &dsState));

    CNA_RasterizerState rsState;
    CNA_INIT_VERSIONED(rsState);
    CNA_TRY(data, error, cna_rasterizer_state_init(
        CNA_RASTERIZER_STATE_PRESET_CULL_NONE, &rsState));
    CNA_TRY(data, error, cna_graphics_device_set_rasterizer_state(data->graphics, &rsState));

    CNA_EffectTechniqueHandle technique = CNA_INVALID_HANDLE;
    CNA_EffectPassCollectionHandle passes = CNA_INVALID_HANDLE;
    CNA_EffectPassHandle pass = CNA_INVALID_HANDLE;
    uint64_t pass_count = 0;
    CNA_Result result = cna_effect_get_current_technique(data->cubeEffect, &technique);
    if (result != CNA_RESULT_SUCCESS) {
        return ReportCnaFailure(result, "cna_effect_get_current_technique", data, error);
    }
    result = cna_effect_technique_get_passes(technique, &passes);
    if (result != CNA_RESULT_SUCCESS) {
        result = ReportCnaFailure(result, "cna_effect_technique_get_passes", data, error);
        goto cleanup;
    }
    result = cna_effect_pass_collection_get_count(passes, &pass_count);
    if (result != CNA_RESULT_SUCCESS) {
        result = ReportCnaFailure(result, "cna_effect_pass_collection_get_count", data, error);
        goto cleanup;
    }
    if (pass_count == 0U) {
        result = ReportTemplateFailure(
            CNA_RESULT_INVALID_STATE,
            "the basic effect exposed zero passes; a frame would contain no 3D draw",
            data, error);
        goto cleanup;
    }
    
    CNA_UserPrimitives primitives;
    CNA_INIT_VERSIONED(primitives);
    primitives.primitive_type = CNA_PRIMITIVE_TRIANGLE_LIST;
    primitives.vertex_source = CNA_USER_VERTEX_SOURCE_POSITION_TEXTURE;
    primitives.vertex_data = cubeVertices;
    primitives.vertex_declaration = CNA_INVALID_HANDLE;
    primitives.vertex_offset = 0;
    primitives.primitive_count = 12;

    for (uint64_t i = 0; i < pass_count; ++i) {
        result = cna_effect_pass_collection_get_at(passes, i, &pass);
        if (result != CNA_RESULT_SUCCESS) {
            result = ReportCnaFailure(
                result, "cna_effect_pass_collection_get_at", data, error);
            goto cleanup;
        }
        result = cna_effect_pass_apply(pass);
        if (result != CNA_RESULT_SUCCESS) {
            result = ReportCnaFailure(result, "cna_effect_pass_apply", data, error);
            goto cleanup;
        }
        result = cna_graphics_device_draw_user_primitives(data->graphics, &primitives);
        if (result != CNA_RESULT_SUCCESS) {
            result = ReportCnaFailure(
                result, "cna_graphics_device_draw_user_primitives", data, error);
            goto cleanup;
        }
        result = cna_effect_pass_destroy(pass);
        if (result != CNA_RESULT_SUCCESS) {
            result = ReportCnaFailure(result, "cna_effect_pass_destroy", data, error);
            goto cleanup;
        }
        pass = CNA_INVALID_HANDLE;
    }

cleanup:
    /* Both views are owned handles, released every frame so the registry does not grow
       for the life of the process. */
    if (pass != CNA_INVALID_HANDLE) {
        CNA_Result cleanupResult = cna_effect_pass_destroy(pass);
        RecordCleanupFailure(
            &result, cleanupResult, "cna_effect_pass_destroy", data, error);
    }
    if (passes != CNA_INVALID_HANDLE) {
        CNA_Result cleanupResult = cna_effect_pass_collection_destroy(passes);
        RecordCleanupFailure(&result, cleanupResult,
            "cna_effect_pass_collection_destroy", data, error);
    }
    if (technique != CNA_INVALID_HANDLE) {
        CNA_Result cleanupResult = cna_effect_technique_destroy(technique);
        RecordCleanupFailure(&result, cleanupResult,
            "cna_effect_technique_destroy", data, error);
    }
    return result;
}

static CNA_Result DrawRendererBanner(HelloGameData* data, CNA_CallbackError* error) {
    CNA_Viewport viewport;
    CNA_TRY(data, error, cna_graphics_device_get_viewport(data->graphics, &viewport));
    int viewportWidth = (int)viewport.width;
    size_t nameLen = strlen(data->rendererName);
    int glyphColumns = (int)(nameLen * 6 > 0 ? nameLen * 6 - 1 : 1);
    int pixelSize = (viewportWidth - 48) / glyphColumns;
    if (pixelSize < 1) pixelSize = 1;
    if (pixelSize > 8) pixelSize = 8;
    int textWidth = glyphColumns * pixelSize;
    int textHeight = 7 * pixelSize;
    int textX = (viewportWidth - textWidth) / 2;
    int textY = 28;
    int padding = 14;
    
    CNA_Color translucentWhite;
    CNA_TRY(data, error, cna_color_from_non_premultiplied_int(
        255, 255, 255, 96, &translucentWhite));

    CNA_SpriteBatchBeginInfo begin_info;
    CNA_INIT_VERSIONED(begin_info);
    CNA_TRY(data, error, cna_sprite_batch_begin(data->spriteBatch, &begin_info));

    CNA_SpriteCommand command;
    CNA_INIT_VERSIONED(command);
    command.texture = data->solidTexture;
    command.destination.x = textX - padding;
    command.destination.y = textY - padding;
    command.destination.width = textWidth + padding * 2;
    command.destination.height = textHeight + padding * 2;
    command.source.x = 0; command.source.y = 0; command.source.width = 1; command.source.height = 1;
    command.color = translucentWhite;
    CNA_Result result = cna_sprite_batch_submit_many(data->spriteBatch, &command, 1);
    if (result != CNA_RESULT_SUCCESS) {
        result = ReportCnaFailure(result, "cna_sprite_batch_submit_many(banner)", data, error);
        goto end_batch;
    }

    for (size_t i = 0; i < nameLen; ++i) {
        GlyphRows rows = GetGlyphRows(data->rendererName[i]);
        int characterX = textX + (int)i * 6 * pixelSize;
        for (int row = 0; row < 7; ++row) {
            for (int col = 0; col < 5; ++col) {
                if ((rows.rows[row] & (1U << (4 - col))) != 0) {
                    command.destination.x = characterX + col * pixelSize;
                    command.destination.y = textY + row * pixelSize;
                    command.destination.width = pixelSize;
                    command.destination.height = pixelSize;
                    command.color = (CNA_Color){24, 36, 55, 255};
                    result = cna_sprite_batch_submit_many(data->spriteBatch, &command, 1);
                    if (result != CNA_RESULT_SUCCESS) {
                        result = ReportCnaFailure(
                            result, "cna_sprite_batch_submit_many(glyph)", data, error);
                        goto end_batch;
                    }
                }
            }
        }
    }

end_batch:
    {
        CNA_Result endResult = cna_sprite_batch_end(data->spriteBatch);
        RecordCleanupFailure(
            &result, endResult, "cna_sprite_batch_end", data, error);
    }
    return result;
}

static CNA_Result HelloGame_Update(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    HelloGameData* data = (HelloGameData*)context;

    /* The graphics-device handle is CALLBACK-SCOPED: CNA invalidates it before the callback that
       produced it returns, and it has no release operation. Caching the one LoadContent obtained
       and reusing it here is what made every draw call in this template fail with
       "The callback-scoped graphics-device handle is invalid for this call" -- silently, until the
       results were checked. It is re-borrowed at the top of every callback that needs it. */
    CNA_TRY(data, error, cna_game_get_graphics_device(game, &data->graphics));

    if (data->hasWindow) {
        CNA_KeyboardState state;
        CNA_INIT_VERSIONED(state);
        CNA_TRY(data, error, cna_keyboard_get_state_for_player(game, 0, &state));
        CNA_Bool escapeDown = CNA_FALSE;
        CNA_TRY(data, error, cna_keyboard_state_is_key_down(
            &state, CNA_KEY_ESCAPE, &escapeDown));
        if (escapeDown != CNA_FALSE) {
            CNA_TRY(data, error, cna_game_request_exit(game));
            return CNA_RESULT_SUCCESS;
        }
    }

    float dt = (float)time->elapsed_game_time_ticks / 10000000.0f;
    data->animationSeconds += dt;

    if (!data->supportsThreeD) {
        float movementDelta = fminf(dt, 0.1f);
        data->position.x += data->velocity.x * movementDelta;
        data->position.y += data->velocity.y * movementDelta;

        CNA_Viewport viewport;
        CNA_TRY(data, error, cna_graphics_device_get_viewport(data->graphics, &viewport));
        
        CNA_Texture2DInfo info;
        CNA_INIT_VERSIONED(info);
        CNA_TRY(data, error, cna_texture2d_get_info(data->logoTexture, &info));
        float logoSize = (float)(info.width > info.height ? info.width : info.height);
        float halfExtent = logoSize * 0.5f * MAXIMUM_2D_LOGO_SCALE * 1.15f;
        
        float minX = fminf(halfExtent, (float)viewport.width * 0.5f);
        float minY = fminf(halfExtent, (float)viewport.height * 0.5f);
        float maxX = fmaxf(minX, (float)viewport.width - minX);
        float maxY = fmaxf(minY, (float)viewport.height - minY);

        if (data->position.x < minX) {
            data->position.x = minX;
            data->velocity.x = fabsf(data->velocity.x);
        } else if (data->position.x > maxX) {
            data->position.x = maxX;
            data->velocity.x = -fabsf(data->velocity.x);
        }

        if (data->position.y < minY) {
            data->position.y = minY;
            data->velocity.y = fabsf(data->velocity.y);
        } else if (data->position.y > maxY) {
            data->position.y = maxY;
            data->velocity.y = -fabsf(data->velocity.y);
        }
    }

    return CNA_RESULT_SUCCESS;
}

static CNA_Result HelloGame_Draw(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)time;
    HelloGameData* data = (HelloGameData*)context;

    /* Re-borrowed every frame; see the note in HelloGame_Update. */
    CNA_TRY(data, error, cna_game_get_graphics_device(game, &data->graphics));

    if (data->simulateDrawFailure && data->drawnFrames == 0U) {
        CNA_Viewport ignored;
        data->injectedDrawFailureResult =
            cna_graphics_device_get_viewport(CNA_INVALID_HANDLE, &ignored);
        data->drawFailureInjected = true;
        fprintf(stderr, "CNA_TEMPLATE_TEST: draw failure injected (result=%d)\n",
                (int)data->injectedDrawFailureResult);
        fflush(stderr);
        if (data->injectedDrawFailureResult == CNA_RESULT_SUCCESS) {
            return ReportTemplateFailure(
                CNA_RESULT_INVALID_STATE,
                "simulated draw failure unexpectedly returned success",
                data, error);
        }
        return ReportCnaFailure(
            data->injectedDrawFailureResult,
            "cna_graphics_device_get_viewport(CNA_INVALID_HANDLE)", data, error);
    }

    if (data->supportsThreeD && data->supportsDepth) {
        CNA_TRY(data, error, cna_graphics_device_clear_color_depth(
            data->graphics, CNA_COLOR_CORNFLOWER_BLUE, 1.0f));
    } else {
        CNA_TRY(data, error, cna_graphics_device_clear_rgba(
            data->graphics, 100.0f/255.0f, 149.0f/255.0f, 237.0f/255.0f, 1.0f));
    }

    CNA_Result result;
    if (data->supportsThreeD) {
        result = Draw3DLogoCube(data, error);
    } else {
        result = Draw2DLogo(data, error);
    }
    if (result != CNA_RESULT_SUCCESS) {
        return result;
    }

    if (data->animationSeconds < RENDERER_BANNER_SECONDS) {
        result = DrawRendererBanner(data, error);
        if (result != CNA_RESULT_SUCCESS) {
            return result;
        }
    }

    if (data->smokeTest && ++data->drawnFrames >= 3) {
        printf("cna-c-template: smoke test drew %u frames; exiting\n", data->drawnFrames);
        CNA_TRY(data, error, cna_game_request_exit(game));
    }

    return CNA_RESULT_SUCCESS;
}

static CNA_Result ReleaseResources(HelloGameData* data, CNA_CallbackError* error) {
    CNA_Result firstResult = CNA_RESULT_SUCCESS;
    CNA_Result result;

    if (data->cubeEffect != CNA_INVALID_HANDLE) {
        result = cna_effect_destroy(data->cubeEffect);
        RecordCleanupFailure(&firstResult, result, "cna_effect_destroy", data, error);
        if (result == CNA_RESULT_SUCCESS) {
            data->cubeEffect = CNA_INVALID_HANDLE;
        }
    }
    if (data->solidTexture != CNA_INVALID_HANDLE) {
        result = cna_texture2d_destroy(data->solidTexture);
        RecordCleanupFailure(&firstResult, result, "cna_texture2d_destroy(solid)", data, error);
        if (result == CNA_RESULT_SUCCESS) {
            data->solidTexture = CNA_INVALID_HANDLE;
        }
    }
    if (data->logoTexture != CNA_INVALID_HANDLE) {
        result = cna_texture2d_destroy(data->logoTexture);
        RecordCleanupFailure(&firstResult, result, "cna_texture2d_destroy(logo)", data, error);
        if (result == CNA_RESULT_SUCCESS) {
            data->logoTexture = CNA_INVALID_HANDLE;
        }
    }
    if (data->spriteBatch != CNA_INVALID_HANDLE) {
        result = cna_sprite_batch_destroy(data->spriteBatch);
        RecordCleanupFailure(&firstResult, result, "cna_sprite_batch_destroy", data, error);
        if (result == CNA_RESULT_SUCCESS) {
            data->spriteBatch = CNA_INVALID_HANDLE;
        }
    }
    return firstResult;
}

static CNA_Result HelloGame_UnloadContent(CNA_Handle game, const CNA_GameTime* time,
                                          void* context, CNA_CallbackError* error) {
    (void)game;
    (void)time;
    return ReleaseResources((HelloGameData*)context, error);
}

/* Every route in this ABI returns a CNA_Result and records a message for the calling thread.
   Ignoring both is how this template used to exit(0) having drawn nothing and printed nothing:
   game creation was refused, the handle stayed invalid, and main() had no way to know. */
bool HelloGame_Check(CNA_Result result, const char* what) {
    return ReportCnaFailure(result, what, NULL, NULL) == CNA_RESULT_SUCCESS;
}

bool HelloGame_GetInjectedDrawFailure(CNA_Result* result) {
    if (activeGameData == NULL || !activeGameData->drawFailureInjected) {
        return false;
    }
    if (result != NULL) {
        *result = activeGameData->injectedDrawFailureResult;
    }
    return true;
}

CNA_Handle HelloGame_Create(bool smokeTest, bool simulateDrawFailure) {
    if (activeGameData != NULL) {
        fprintf(stderr, "cna-c-template: only one HelloGame instance is supported\n");
        return CNA_INVALID_HANDLE;
    }
    HelloGameData* data = (HelloGameData*)malloc(sizeof(HelloGameData));
    if (data == NULL) {
        fprintf(stderr, "cna-c-template: out of memory\n");
        return CNA_INVALID_HANDLE;
    }
    memset(data, 0, sizeof(HelloGameData));
    data->smokeTest = smokeTest;
    data->simulateDrawFailure = simulateDrawFailure;
    data->graphics = CNA_INVALID_HANDLE;
    data->content = CNA_INVALID_HANDLE;
    data->spriteBatch = CNA_INVALID_HANDLE;
    data->cubeEffect = CNA_INVALID_HANDLE;
    data->logoTexture = CNA_INVALID_HANDLE;
    data->solidTexture = CNA_INVALID_HANDLE;

    /* Both structures are zeroed first and then filled field by field. The `{sizeof(T), version}`
       shorthand this template used before leaves every later field at zero, and a zero
       target_elapsed_time_ticks is refused: the ABI requires it to be positive. */
    CNA_GameCallbacks callbacks;
    memset(&callbacks, 0, sizeof(callbacks));
    callbacks.struct_size = (uint32_t)sizeof(callbacks);
    callbacks.struct_version = UINT32_C(1);
    callbacks.load_content = HelloGame_LoadContent;
    callbacks.update = HelloGame_Update;
    callbacks.draw = HelloGame_Draw;
    callbacks.unload_content = HelloGame_UnloadContent;
    callbacks.context = data;

    CNA_GameCreateInfo create_info;
    memset(&create_info, 0, sizeof(create_info));
    create_info.struct_size = (uint32_t)sizeof(create_info);
    create_info.struct_version = UINT32_C(1);
    create_info.is_fixed_time_step = CNA_TRUE;
    create_info.target_elapsed_time_ticks = INT64_C(166667); /* 1/60 s, in 100 ns ticks */
    create_info.window_title = view("cna-c-template - HelloGame");
    create_info.callbacks = &callbacks;

    CNA_Handle game = CNA_INVALID_HANDLE;
    if (!HelloGame_Check(cna_game_create(&create_info, &game), "cna_game_create")) {
        free(data);
        return CNA_INVALID_HANDLE;
    }

    activeGameData = data;
    return game;
}

CNA_Result HelloGame_Destroy(CNA_Handle game) {
    CNA_Result firstResult = CNA_RESULT_SUCCESS;
    if (game != CNA_INVALID_HANDLE) {
        if (activeGameData != NULL) {
            firstResult = ReleaseResources(activeGameData, NULL);
        }
        CNA_Result destroyResult = cna_game_destroy(game);
        if (destroyResult != CNA_RESULT_SUCCESS) {
            CNA_Result reported = ReportCnaFailure(
                destroyResult, "cna_game_destroy", NULL, NULL);
            if (firstResult == CNA_RESULT_SUCCESS) {
                firstResult = reported;
            }
        }
        /* CNA_RESULT_CALLBACK is the game loop's primary callback failure, not a refusal to
           destroy. The public C API contract says the handle is released in both cases. */
        if (destroyResult == CNA_RESULT_SUCCESS || destroyResult == CNA_RESULT_CALLBACK) {
            free(activeGameData);
            activeGameData = NULL;
        }
    }
    return firstResult;
}
