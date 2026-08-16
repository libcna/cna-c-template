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
    unsigned int drawnFrames;
} HelloGameData;

static CNA_StringView view(const char* const text) {
    CNA_StringView result;
    result.data = text;
    result.byte_length = (uint64_t)strlen(text);
    return result;
}

static void ReportRendererCapabilities(HelloGameData* data) {
    CNA_Bool custom_effects = CNA_FALSE;
    cna_graphics_device_supports_capability(data->graphics, CNA_GRAPHICS_CAPABILITY_CUSTOM_EFFECTS, &custom_effects);

    printf("cna-c-template: renderer %s\n", data->rendererName);
    printf("  window          : %s\n", data->hasWindow ? "yes" : "no (windowless renderer)");
    printf("  3D pipeline     : %s\n", data->supportsThreeD ? "yes" : "no (2D only)");
    printf("  depth/stencil   : %s\n", data->supportsDepth ? "yes" : "no");
    printf("  custom shaders  : %s\n", (custom_effects != CNA_FALSE) ? "yes" : "no");
    fflush(stdout);
}

static CNA_Result HelloGame_LoadContent(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)time;
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    cna_game_get_graphics_device(game, &data->graphics);
    cna_sprite_batch_create(data->graphics, &data->spriteBatch);

    cna_game_get_content_manager_ext(game, &data->content);
    cna_content_manager_load_texture2d(data->content, view("logo"), &data->logoTexture);

    CNA_Color white = CNA_COLOR_WHITE;
    cna_texture2d_create_from_rgba8(data->graphics, 1, 1, &white, 1, &data->solidTexture);

    uint64_t name_len = 0;
    cna_graphics_device_copy_renderer_name(data->graphics, data->rendererName, sizeof(data->rendererName), &name_len);

    uint64_t native_handle = 0;
    cna_game_window_get_native_handle_ext(game, &native_handle);
    data->hasWindow = (native_handle != 0);

    CNA_Bool threeD = CNA_FALSE;
    cna_graphics_device_supports_capability(data->graphics, CNA_GRAPHICS_CAPABILITY_THREE_D, &threeD);
    data->supportsThreeD = (threeD != CNA_FALSE);

    CNA_Bool depth = CNA_FALSE;
    cna_graphics_device_supports_capability(data->graphics, CNA_GRAPHICS_CAPABILITY_DEPTH_STENCIL_BUFFER, &depth);
    data->supportsDepth = (depth != CNA_FALSE);

    if (data->supportsThreeD) {
        cna_basic_effect_create(data->graphics, &data->cubeEffect);
        cna_basic_effect_set_texture_enabled(data->cubeEffect, CNA_TRUE);
        cna_basic_effect_set_texture(data->cubeEffect, data->logoTexture);
        cna_effect_lights_set_enabled(data->cubeEffect, CNA_FALSE);
        cna_basic_effect_set_vertex_color_enabled(data->cubeEffect, CNA_FALSE);
    }

    CNA_Viewport viewport;
    cna_graphics_device_get_viewport(data->graphics, &viewport);
    data->position.x = (float)viewport.width * 0.5f;
    data->position.y = (float)viewport.height * 0.5f;
    data->velocity.x = 104.0f;
    data->velocity.y = 74.0f;

    ReportRendererCapabilities(data);

    return CNA_RESULT_SUCCESS;
}

static void Draw2DLogo(HelloGameData* data) {
    float motionSeconds = data->animationSeconds * ANIMATION_SPEED;
    float scale = 0.96f + 0.12f * sinf(motionSeconds * 0.65f);
    float rotation = 0.11f * sinf(motionSeconds * 0.55f);
    
    CNA_Texture2DInfo info;
    cna_texture2d_get_info(data->logoTexture, &info);
    CNA_Vector2 origin = {(float)info.width * 0.5f, (float)info.height * 0.5f};

    CNA_SpriteBatchBeginInfo begin_info = { sizeof(CNA_SpriteBatchBeginInfo), 1 };
    cna_sprite_batch_begin(data->spriteBatch, &begin_info);

    CNA_SpriteCommand command = { sizeof(CNA_SpriteCommand), 1 };
    command.texture = data->logoTexture;
    command.destination.x = (int32_t)data->position.x;
    command.destination.y = (int32_t)data->position.y;
    command.destination.width = (int32_t)((float)info.width * scale);
    command.destination.height = (int32_t)((float)info.height * scale);
    command.source.x = 0; command.source.y = 0; command.source.width = (int32_t)info.width; command.source.height = (int32_t)info.height;
    command.color = CNA_COLOR_WHITE;
    command.origin = origin;
    command.rotation = rotation;
    command.effects = 0;
    command.layer_depth = 0.0f;

    cna_sprite_batch_submit_many(data->spriteBatch, &command, 1);
    cna_sprite_batch_end(data->spriteBatch);
}

static void Draw3DLogoCube(HelloGameData* data) {
    static CNA_VertexPositionTexture cubeVertices[36];
    static bool verticesCreated = false;
    if (!verticesCreated) {
        CreateLogoCubeVertices(cubeVertices);
        verticesCreated = true;
    }

    CNA_Viewport viewport;
    cna_graphics_device_get_viewport(data->graphics, &viewport);
    float aspectRatio = (float)viewport.width / (float)(viewport.height > 0 ? viewport.height : 1);
    float motionSeconds = data->animationSeconds * ANIMATION_SPEED;
    float scale = 0.88f + 0.10f * sinf(motionSeconds * 0.48f);
    float moveX = 1.15f * sinf(motionSeconds * 0.24f);
    float moveY = 0.70f * sinf(motionSeconds * 0.19f + 1.1f);

    CNA_Matrix mScale, mRotX, mRotY, mRotZ, mTrans, mWorld, mView, mProj;
    cna_matrix_create_scale_xyz(scale, scale, scale, &mScale);
    cna_matrix_create_rotation_x(motionSeconds * 0.22f, &mRotX);
    cna_matrix_create_rotation_y(motionSeconds * 0.31f, &mRotY);
    cna_matrix_create_rotation_z(motionSeconds * 0.13f, &mRotZ);
    cna_matrix_create_translation_xyz(moveX, moveY, 0.0f, &mTrans);

    cna_matrix_multiply(mScale, mRotX, &mWorld);
    cna_matrix_multiply(mWorld, mRotY, &mWorld);
    cna_matrix_multiply(mWorld, mRotZ, &mWorld);
    cna_matrix_multiply(mWorld, mTrans, &mWorld);

    CNA_Vector3 eye = {0.0f, 0.0f, 6.0f};
    CNA_Vector3 target = {0.0f, 0.0f, 0.0f};
    CNA_Vector3 up = {0.0f, 1.0f, 0.0f};
    cna_matrix_create_look_at(eye, target, up, &mView);
    cna_matrix_create_perspective_field_of_view(0.78539816339f, aspectRatio, 0.1f, 100.0f, &mProj);

    cna_effect_matrices_set_world(data->cubeEffect, mWorld);
    cna_effect_matrices_set_view(data->cubeEffect, mView);
    cna_effect_matrices_set_projection(data->cubeEffect, mProj);

    CNA_BlendState blendState;
    cna_blend_state_init(CNA_BLEND_STATE_PRESET_OPAQUE, &blendState);
    cna_graphics_device_set_blend_state(data->graphics, &blendState);

    CNA_DepthStencilState dsState;
    cna_depth_stencil_state_init(data->supportsDepth ? CNA_DEPTH_STENCIL_STATE_PRESET_DEFAULT : CNA_DEPTH_STENCIL_STATE_PRESET_NONE, &dsState);
    cna_graphics_device_set_depth_stencil_state(data->graphics, &dsState);

    CNA_RasterizerState rsState;
    cna_rasterizer_state_init(CNA_RASTERIZER_STATE_PRESET_CULL_NONE, &rsState);
    cna_graphics_device_set_rasterizer_state(data->graphics, &rsState);

    CNA_EffectTechniqueHandle technique = CNA_INVALID_HANDLE;
    cna_effect_get_current_technique(data->cubeEffect, &technique);
    CNA_EffectPassCollectionHandle passes = CNA_INVALID_HANDLE;
    cna_effect_technique_get_passes(technique, &passes);
    uint64_t pass_count = 0;
    cna_effect_pass_collection_get_count(passes, &pass_count);
    
    CNA_UserPrimitives primitives = { sizeof(CNA_UserPrimitives), 1 };
    primitives.primitive_type = CNA_PRIMITIVE_TRIANGLE_LIST;
    primitives.vertex_source = CNA_USER_VERTEX_SOURCE_POSITION_TEXTURE;
    primitives.vertex_data = cubeVertices;
    primitives.vertex_declaration = CNA_INVALID_HANDLE;
    primitives.vertex_offset = 0;
    primitives.primitive_count = 12;

    for (uint64_t i = 0; i < pass_count; ++i) {
        CNA_EffectPassHandle pass = CNA_INVALID_HANDLE;
        cna_effect_pass_collection_get_at(passes, i, &pass);
        cna_effect_pass_apply(pass);
        cna_graphics_device_draw_user_primitives(data->graphics, &primitives);
    }
}

static void DrawRendererBanner(HelloGameData* data) {
    CNA_Viewport viewport;
    cna_graphics_device_get_viewport(data->graphics, &viewport);
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
    cna_color_from_non_premultiplied_int(255, 255, 255, 96, &translucentWhite);

    CNA_SpriteBatchBeginInfo begin_info = { sizeof(CNA_SpriteBatchBeginInfo), 1 };
    cna_sprite_batch_begin(data->spriteBatch, &begin_info);

    CNA_SpriteCommand command = { sizeof(CNA_SpriteCommand), 1 };
    command.texture = data->solidTexture;
    command.destination.x = textX - padding;
    command.destination.y = textY - padding;
    command.destination.width = textWidth + padding * 2;
    command.destination.height = textHeight + padding * 2;
    command.source.x = 0; command.source.y = 0; command.source.width = 1; command.source.height = 1;
    command.color = translucentWhite;
    cna_sprite_batch_submit_many(data->spriteBatch, &command, 1);

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
                    cna_sprite_batch_submit_many(data->spriteBatch, &command, 1);
                }
            }
        }
    }

    cna_sprite_batch_end(data->spriteBatch);
}

static CNA_Result HelloGame_Update(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    if (data->hasWindow) {
        CNA_KeyboardState state;
        cna_keyboard_get_state_for_player(game, 0, &state);
        CNA_Bool escapeDown = CNA_FALSE;
        cna_keyboard_state_is_key_down(&state, CNA_KEY_ESCAPE, &escapeDown);
        if (escapeDown != CNA_FALSE) {
            cna_game_request_exit(game);
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
        cna_graphics_device_get_viewport(data->graphics, &viewport);
        
        CNA_Texture2DInfo info;
        cna_texture2d_get_info(data->logoTexture, &info);
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
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    if (data->supportsThreeD && data->supportsDepth) {
        cna_graphics_device_clear_color_depth(data->graphics, CNA_COLOR_CORNFLOWER_BLUE, 1.0f);
    } else {
        cna_graphics_device_clear_rgba(data->graphics, 100.0f/255.0f, 149.0f/255.0f, 237.0f/255.0f, 1.0f);
    }

    if (data->supportsThreeD) {
        Draw3DLogoCube(data);
    } else {
        Draw2DLogo(data);
    }

    if (data->animationSeconds < RENDERER_BANNER_SECONDS) {
        DrawRendererBanner(data);
    }

    if (data->smokeTest && ++data->drawnFrames >= 3) {
        printf("cna-c-template: smoke test drew %u frames; exiting\n", data->drawnFrames);
        cna_game_request_exit(game);
    }

    return CNA_RESULT_SUCCESS;
}

static CNA_Result HelloGame_UnloadContent(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)game;
    (void)time;
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    if (data->cubeEffect != CNA_INVALID_HANDLE) {
        cna_effect_destroy(data->cubeEffect);
    }
    cna_texture2d_destroy(data->solidTexture);
    cna_texture2d_destroy(data->logoTexture);
    cna_sprite_batch_destroy(data->spriteBatch);

    free(data);

    return CNA_RESULT_SUCCESS;
}

CNA_Handle HelloGame_Create(bool smokeTest) {
    HelloGameData* data = (HelloGameData*)malloc(sizeof(HelloGameData));
    memset(data, 0, sizeof(HelloGameData));
    data->smokeTest = smokeTest;

    CNA_GameCallbacks callbacks = { sizeof(CNA_GameCallbacks), 1 };
    callbacks.load_content = HelloGame_LoadContent;
    callbacks.update = HelloGame_Update;
    callbacks.draw = HelloGame_Draw;
    callbacks.unload_content = HelloGame_UnloadContent;
    callbacks.context = data;

    CNA_GameCreateInfo create_info = { sizeof(CNA_GameCreateInfo), 1 };
    create_info.window_title = view("cna-c-template - HelloGame");
    create_info.callbacks = &callbacks;

    CNA_Handle game = CNA_INVALID_HANDLE;
    cna_game_create(&create_info, &game);

    return game;
}

void HelloGame_Destroy(CNA_Handle game) {
    if (game != CNA_INVALID_HANDLE) {
        cna_game_destroy(game);
    }
}
