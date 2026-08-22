#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <CNA/C/cna.h>
#include "HelloGame/HelloGame.h"

#if defined(__ANDROID__)
/* SDLActivity resolves SDL_main from libmain.so. SDL's public entry-point header both renames
   main and gives the symbol the visibility required when the application is a shared library. */
#include <SDL3/SDL_main.h>
#endif

#define CNA_TEMPLATE_INJECTED_FAILURE_EXIT_CODE 86

int main(int argc, char* argv[]) {
    bool smokeTest = false;
    bool simulateDrawFailure = false;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--smoke-test") == 0) {
            smokeTest = true;
        } else if (strcmp(argv[i], "--simulate-draw-failure") == 0) {
            simulateDrawFailure = true;
        } else {
            fprintf(stderr, "cna-c-template: unknown argument '%s'\n", argv[i]);
            return 2;
        }
    }

    if (simulateDrawFailure && !smokeTest) {
        fprintf(stderr,
                "cna-c-template: --simulate-draw-failure requires --smoke-test\n");
        return 2;
    }

    CNA_Handle game = HelloGame_Create(smokeTest, simulateDrawFailure);
    if (game == CNA_INVALID_HANDLE) {
        /* HelloGame_Create has already reported why. Exiting non-zero is what makes a refused
           start visible to a script or to ctest, instead of an empty successful run. */
        return 1;
    }

    const CNA_Result runResult = cna_game_run(game);
    CNA_Result injectedResult = CNA_RESULT_SUCCESS;
    const bool injectionReached = HelloGame_GetInjectedDrawFailure(&injectedResult);
    const bool runSucceeded = HelloGame_Check(runResult, "cna_game_run");
    const CNA_Result destroyResult = HelloGame_Destroy(game);
    const bool destroySucceeded = destroyResult == CNA_RESULT_SUCCESS;

    if (simulateDrawFailure) {
        const bool exactFailurePropagated =
            injectionReached &&
            injectedResult == CNA_RESULT_INVALID_HANDLE &&
            runResult == CNA_RESULT_CALLBACK &&
            destroyResult == CNA_RESULT_CALLBACK;
        if (exactFailurePropagated) {
            fprintf(stderr,
                    "CNA_TEMPLATE_TEST: draw failure propagated "
                    "(injected_result=%d, run_result=%d, destroy_result=%d, exit_code=%d)\n",
                    (int)injectedResult, (int)runResult, (int)destroyResult,
                    CNA_TEMPLATE_INJECTED_FAILURE_EXIT_CODE);
            return CNA_TEMPLATE_INJECTED_FAILURE_EXIT_CODE;
        }
        fprintf(stderr,
                "cna-c-template: draw-failure contract mismatch "
                "(reached=%d, injected_result=%d, run_result=%d, destroy_result=%d)\n",
                injectionReached ? 1 : 0, (int)injectedResult, (int)runResult,
                (int)destroyResult);
        return 1;
    }

    return (runSucceeded && destroySucceeded) ? 0 : 1;
}
