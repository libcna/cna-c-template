#ifndef HELLO_GAME_H
#define HELLO_GAME_H

#include <stdbool.h>
#include <CNA/C/cna.h>

/**
 * @brief Reports a failed CNA call, with the diagnostic the ABI recorded for this thread.
 *
 * Every CNA route returns a CNA_Result and leaves a message behind; a template that discards
 * both cannot tell a working frame from a refused one.
 *
 * @param result The result to test.
 * @param what The call being reported, named in the message.
 * @return true when @p result is CNA_RESULT_SUCCESS, false otherwise.
 */
bool HelloGame_Check(CNA_Result result, const char* what);

/**
 * @brief Creates the HelloGame instance.
 * @param smokeTest If true, the game will exit after a few frames.
 * @return A handle to the created game, or CNA_INVALID_HANDLE when creation was refused.
 */
CNA_Handle HelloGame_Create(bool smokeTest);

/**
 * @brief Destroys the HelloGame instance.
 * @param game The game handle to destroy.
 */
void HelloGame_Destroy(CNA_Handle game);

#endif
