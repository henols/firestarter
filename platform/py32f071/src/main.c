#include "py32f071_board.h"

void firestarter_platform_setup(void);
void firestarter_platform_loop(void);

int main(void)
{
    py32_board_init();
    firestarter_platform_setup();

    for (;;) {
        firestarter_platform_loop();
    }
}
