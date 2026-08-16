#ifndef HELLO_GAME_H
#define HELLO_GAME_H

#include <stdbool.h>
#include <CNA/C/cna.h>

/**
 * @brief Creates the HelloGame instance.
 * @param smokeTest If true, the game will exit after a few frames.
 * @return A handle to the created game.
 */
CNA_Handle HelloGame_Create(bool smokeTest);

/**
 * @brief Destroys the HelloGame instance.
 * @param game The game handle to destroy.
 */
void HelloGame_Destroy(CNA_Handle game);

#endif
