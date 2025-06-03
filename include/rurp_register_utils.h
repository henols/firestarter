#ifndef __RURP_REGESTERS_UTILS_H__
#define __RURP_REGESTERS_UTILS_H__

#include "rurp_shield.h"
#include "rurp_internal_register_utils.h"

#ifdef HARDWARE_REVISION
#include "rurp_hw_rev_utils.h"
#endif

uint8_t lsb_address = 0xff;
uint8_t msb_address = 0xff;
rurp_register_t control_register = 0xff;

// Function to write data to a specific register on the RURP shield.
// This is an internal function used by rurp_write_to_register.
// 
// Parameters:
//   reg: The register to write to (e.g., LEAST_SIGNIFICANT_BYTE, MOST_SIGNIFICANT_BYTE, CONTROL_REGISTER).
//   data: The data to write to the register.
void rurp_internal_write_to_register(uint8_t reg, rurp_register_t data);

// Function to write data to a specific register on the RURP shield
// This function also caches the register values and adds a small delay
// if the P1_VPP_ENABLE bit is being cleared, to allow voltage to settle.
// It also maps the control register data based on the hardware revision.
//
// Parameters:
//   reg: The register to write to (e.g., LEAST_SIGNIFICANT_BYTE, MOST_SIGNIFICANT_BYTE, CONTROL_REGISTER).
//   data: The data to write to the register.
void rurp_write_to_register(uint8_t reg, rurp_register_t data) {
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
    rurp_internal_write_to_register(reg, data);
    
    //Take a break here if an address change needs time to settle
    if (settle) {
        delayMicroseconds(4);
    }
}


void rurp_internal_write_to_register(uint8_t reg, rurp_register_t data) {
    rurp_write_data_buffer(data);
    rurp_set_control_pin(reg, 1);
    // Probably useless - verify later 
    delayMicroseconds(1);

    rurp_set_control_pin(reg, 0);
}

rurp_register_t rurp_read_from_register(uint8_t reg) {
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


#endif // __RURP_REGESTERS_UTILS_H__