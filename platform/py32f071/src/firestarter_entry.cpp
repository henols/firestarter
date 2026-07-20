#include "py32f071_board.h"

void setup();
void loop();

extern "C" void firestarter_platform_setup(void)
{
    setup();
}

extern "C" void firestarter_platform_loop(void)
{
    py32_board_task();
    loop();
}
