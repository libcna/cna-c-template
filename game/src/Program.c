#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <CNA/C/cna.h>
#include "HelloGame/HelloGame.h"

int main(int argc, char* argv[]) {
    bool smokeTest = false;
    bool simulateDrawFailure = false;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--smoke-test") == 0) {
            smokeTest = true;
        } else if (strcmp(argv[i], "--simulate-draw-failure") == 0) {
            simulateDrawFailure = true;
        }
    }

    CNA_Handle game = HelloGame_Create(smokeTest, simulateDrawFailure);
    if (game == CNA_INVALID_HANDLE) {
        /* HelloGame_Create has already reported why. Exiting non-zero is what makes a refused
           start visible to a script or to ctest, instead of an empty successful run. */
        return 1;
    }

    const bool runSucceeded = HelloGame_Check(cna_game_run(game), "cna_game_run");
    const bool destroySucceeded = HelloGame_Destroy(game) == CNA_RESULT_SUCCESS;
    return (runSucceeded && destroySucceeded) ? 0 : 1;
}
