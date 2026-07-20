#include "firestarter.h"
#include "rurp_shield.h"
#include "rurp_pinout.h"
#include "py32f071_board.h"

extern firestarter_handle_t handle;

static uint8_t lsb_address = 0xFFu;
static uint8_t msb_address = 0xFFu;
static rurp_register_t control_register = (rurp_register_t)0xFFFFu;

extern "C" void rurp_prepare_vpp_target(uint16_t target_mv)
{
    py32_set_requested_vpp_mv(target_mv);
}

extern "C" void rurp_write_to_register(uint8_t reg, rurp_register_t data)
{
    if (reg == LEAST_SIGNIFICANT_BYTE) {
        if (lsb_address == (uint8_t)data) return;
        lsb_address = (uint8_t)data;
    } else if (reg == MOST_SIGNIFICANT_BYTE) {
        if (msb_address == (uint8_t)data) return;
        msb_address = (uint8_t)data;
    } else if (reg == CONTROL_REGISTER) {
        if (control_register == data) return;
        rurp_register_t previous = control_register;
        control_register = data;

        bool was_enabled = (previous & CTRL_VPP_REGULATOR_ENABLE) != 0u;
        bool enable = (data & CTRL_VPP_REGULATOR_ENABLE) != 0u;
        if (!was_enabled && enable) {
            uint16_t target = handle.vpp_mv;
            py32_set_requested_vpp_mv(target);
            if (target != 0u) {
                (void)rurp_set_vpp_target_mv(target, 100u, 500u);
            }
        } else if (was_enabled && !enable) {
            rurp_vpp_control_enable(false);
        }
    } else {
        return;
    }

    rurp_write_data_buffer((uint8_t)data);
    rurp_set_control_pin(reg, 1u);
    rurp_delay_us(1u);
    rurp_set_control_pin(reg, 0u);
}

extern "C" rurp_register_t rurp_read_from_register(uint8_t reg)
{
    if (reg == LEAST_SIGNIFICANT_BYTE) return lsb_address;
    if (reg == MOST_SIGNIFICANT_BYTE) return msb_address;
    if (reg == CONTROL_REGISTER) return control_register;
    return 0u;
}
