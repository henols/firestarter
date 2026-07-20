#include "py32f071_board.h"
#include "py32f071_regs.h"

int main(void)
{
    py32_board_init();

    for (;;) {
        py32_board_task();
        py32_wait_for_interrupt();
    }
}
