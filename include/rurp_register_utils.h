#ifndef RURP_REGESTERS_UTILS_H
#define RURP_REGESTERS_UTILS_H

#include "rurp_shield.h"
#ifdef HARDWARE_REVISION
#include "rurp_hw_rev_utils.h"
#endif

uint8_t lsb_address = 0xff;
uint8_t msb_address = 0xff;
register_t control_register = 0xff;

void rurp_write_to_register(uint8_t reg, register_t data) {
    bool settle = false;
    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        if (lsb_address == (uint8_t)data) {
            return;
        }
        lsb_address = data;
        break;
    case MOST_SIGNIFICANT_BYTE:
        if (msb_address == (uint8_t)data) {
            return;
        }
        msb_address = data;
        break;
    case CONTROL_REGISTER:
        if (control_register == data) {
            return;
        }
        if ((control_register & P1_VPP_ENABLE) > (data & P1_VPP_ENABLE)) {
            settle = true;
        }
        control_register = data;
#ifdef HARDWARE_REVISION
        data = rurp_map_ctrl_reg_for_hardware_revision(data);
#endif
        break;
    default:
        return;
    }

    rurp_write_data_buffer(data);
    rurp_set_control_pin(reg, 1);
    // Probably useless - verify later 
    delayMicroseconds(1);

    rurp_set_control_pin(reg, 0);
    //Take a break here if an address change needs time to settle
    if (settle) {
        delayMicroseconds(4);
    }
}

register_t rurp_read_from_register(uint8_t reg) {
    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        return lsb_address;
    case MOST_SIGNIFICANT_BYTE:
        return msb_address;
    case CONTROL_REGISTER:
        return control_register;
    }
    return 0;
}


#endif // RURP_REGESTERS_UTILS_H