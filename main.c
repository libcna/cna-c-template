#include <cna/cna.h>
#include "hello_game.h"

int main(int argc, char* argv[]) {
    CnaGame game = HelloGame_Create();
    CnaRun(game);
    CnaDestroy(game);
    return 0;
}
