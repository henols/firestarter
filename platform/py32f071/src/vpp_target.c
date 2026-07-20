#include "py32f071_board.h"

static uint16_t requested_vpp_mv;

void py32_set_requested_vpp_mv(uint16_t target_mv)
{
    requested_vpp_mv = target_mv;
}

uint16_t py32_get_requested_vpp_mv(void)
{
    return requested_vpp_mv;
}
