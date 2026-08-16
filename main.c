#include <CNA/C/cna.h>
#include "hello_game.h"

int main(int argc, char* argv[]) {
    (void)argc;
    (void)argv;
    
    CNA_Handle game = HelloGame_Create();
    if (game != CNA_INVALID_HANDLE) {
        cna_game_run(game);
        cna_game_destroy(game);
    }
    
    return 0;
}
