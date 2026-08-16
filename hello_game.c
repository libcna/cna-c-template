#include "hello_game.h"
#include <math.h>

typedef struct {
    CnaGraphicsDeviceManager graphics;
    CnaSpriteBatch spriteBatch;
    CnaTexture2D logo;
    CnaVector2 position;
} HelloGameData;

void HelloGame_Initialize(CnaGame game) {
    HelloGameData* data = CnaGetGameData(game);
    CnaSetPreferredBackBufferWidth(data->graphics, 1280);
    CnaSetPreferredBackBufferHeight(data->graphics, 720);
    CnaApplyGraphicsChanges(data->graphics);
}

void HelloGame_LoadContent(CnaGame game) {
    HelloGameData* data = CnaGetGameData(game);
    data->spriteBatch = CnaCreateSpriteBatch(CnaGetGraphicsDevice(game));
    data->logo = CnaLoadTexture2D(CnaGetContentManager(game), "logo");
}

void HelloGame_Update(CnaGame game, CnaGameTime gameTime) {
    HelloGameData* data = CnaGetGameData(game);
    float time = (float)CnaGetTotalSeconds(gameTime);
    data->position.x = 640.0f + 200.0f * sinf(time);
    data->position.y = 360.0f + 200.0f * cosf(time);
}

void HelloGame_Draw(CnaGame game, CnaGameTime gameTime) {
    HelloGameData* data = CnaGetGameData(game);
    CnaClear(CnaGetGraphicsDevice(game), CNA_COLOR_CORNFLOWER_BLUE);
    CnaSpriteBatchBegin(data->spriteBatch);
    CnaSpriteBatchDraw(data->spriteBatch, data->logo, data->position, CNA_COLOR_WHITE);
    CnaSpriteBatchEnd(data->spriteBatch);
}

CnaGame HelloGame_Create() {
    HelloGameData* data = (HelloGameData*)malloc(sizeof(HelloGameData));
    CnaGame game = CnaCreateGame(data);
    data->graphics = CnaCreateGraphicsDeviceManager(game);
    
    CnaSetInitializeCallback(game, HelloGame_Initialize);
    CnaSetLoadContentCallback(game, HelloGame_LoadContent);
    CnaSetUpdateCallback(game, HelloGame_Update);
    CnaSetDrawCallback(game, HelloGame_Draw);
    
    CnaSetContentRoot(CnaGetContentManager(game), "Content");
    
    return game;
}
