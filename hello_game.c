#include "hello_game.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    CNA_Handle graphics;
    CNA_Handle content;
    CNA_Handle spriteBatch;
    CNA_Handle logo;
    CNA_Vector2 position;
} HelloGameData;

static CNA_StringView view(const char* const text) {
    CNA_StringView result;
    result.data = text;
    result.byte_length = (uint64_t)strlen(text);
    return result;
}

static CNA_Result HelloGame_LoadContent(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)time;
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    cna_game_get_graphics_device(game, &data->graphics);

    CNA_ContentManagerCreateInfo content_info = { sizeof(CNA_ContentManagerCreateInfo), 1 };
    content_info.root_directory = view("Content");
    cna_content_manager_create(data->graphics, &content_info, &data->content);

    cna_content_manager_load_texture2d(data->content, view("logo"), &data->logo);
    cna_sprite_batch_create(data->graphics, &data->spriteBatch);

    return CNA_RESULT_SUCCESS;
}

static CNA_Result HelloGame_Update(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)game;
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    float seconds = (float)time->total_game_time_ticks / 10000000.0f;
    data->position.x = 640.0f + 200.0f * sinf(seconds);
    data->position.y = 360.0f + 200.0f * cosf(seconds);

    return CNA_RESULT_SUCCESS;
}

static CNA_Result HelloGame_Draw(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)time;
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    cna_game_clear(game, CNA_COLOR_CORNFLOWER_BLUE);

    CNA_SpriteBatchBeginInfo begin_info = { sizeof(CNA_SpriteBatchBeginInfo), 1 };
    begin_info.sort_mode = 0; // Deferred
    cna_sprite_batch_begin(data->spriteBatch, &begin_info);

    CNA_SpriteCommand command = { sizeof(CNA_SpriteCommand), 1 };
    command.texture = data->logo;
    command.destination.x = (int32_t)data->position.x;
    command.destination.y = (int32_t)data->position.y;
    command.destination.width = 256;
    command.destination.height = 256;
    command.source.x = 0;
    command.source.y = 0;
    command.source.width = 256;
    command.source.height = 256;
    command.color = CNA_COLOR_WHITE;
    command.origin.x = 128.0f;
    command.origin.y = 128.0f;

    cna_sprite_batch_submit_many(data->spriteBatch, &command, 1);
    cna_sprite_batch_end(data->spriteBatch);

    return CNA_RESULT_SUCCESS;
}

static CNA_Result HelloGame_UnloadContent(CNA_Handle game, const CNA_GameTime* time, void* context, CNA_CallbackError* error) {
    (void)game;
    (void)time;
    (void)error;
    HelloGameData* data = (HelloGameData*)context;

    cna_sprite_batch_destroy(data->spriteBatch);
    cna_texture2d_destroy(data->logo);
    cna_content_manager_destroy(data->content);

    return CNA_RESULT_SUCCESS;
}

CNA_Handle HelloGame_Create(void) {
    HelloGameData* data = (HelloGameData*)malloc(sizeof(HelloGameData));
    memset(data, 0, sizeof(HelloGameData));

    CNA_GameCallbacks callbacks = { sizeof(CNA_GameCallbacks), 1 };
    callbacks.load_content = HelloGame_LoadContent;
    callbacks.update = HelloGame_Update;
    callbacks.draw = HelloGame_Draw;
    callbacks.unload_content = HelloGame_UnloadContent;
    callbacks.context = data;

    CNA_GameCreateInfo create_info = { sizeof(CNA_GameCreateInfo), 1 };
    create_info.window_title = view("CNA C Hello Game");
    create_info.callbacks = &callbacks;

    CNA_Handle game = CNA_INVALID_HANDLE;
    cna_game_create(&create_info, &game);

    return game;
}
