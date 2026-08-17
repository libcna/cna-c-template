#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <CNA/C/cna.h>
#include "HelloGame/HelloGame.h"

int main(int argc, char* argv[]) {
    bool smokeTest = false;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--smoke-test") == 0) {
            smokeTest = true;
        }
    }

    CNA_Handle game = HelloGame_Create(smokeTest);
    if (game == CNA_INVALID_HANDLE) {
        /* HelloGame_Create has already reported why. Exiting non-zero is what makes a refused
           start visible to a script or to ctest, instead of an empty successful run. */
        return 1;
    }

    const int failed = HelloGame_Check(cna_game_run(game), "cna_game_run") ? 0 : 1;
    HelloGame_Destroy(game);
    return failed;
}
