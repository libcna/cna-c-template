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
    if (game != CNA_INVALID_HANDLE) {
        cna_game_run(game);
        HelloGame_Destroy(game);
    }
    
    return 0;
}
