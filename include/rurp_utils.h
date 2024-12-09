#ifndef RURP_UTILS_H
#define RURP_UTILS_H

#include <stdint.h>
#include "config.h"
#include "rurp_defines.h"

#ifdef HARDWARE_REVISION
    int rurp_get_hardware_revision();
    int rurp_get_physical_hardware_revision();

uint8_t rurp_map_ctrl_reg_to_hardware_revision(uint16_t data) {
    uint8_t ctrl_reg = 0;
    int hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2:
        ctrl_reg = data & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | A17 | RW | REGULATOR);
        ctrl_reg |= data & VPE_TO_VPP ? REV_2_VPE_TO_VPP : 0;
        ctrl_reg |= data & A16 ? REV_2_A16 : 0;
        ctrl_reg |= data & A18 ? REV_2_A18 : 0;
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & VPE_TO_VPP ? REV_1_VPE_TO_VPP : 0;
        break;
    default:
        break;
    }

    return ctrl_reg;
}
#endif
#endif // RURP_UTILS_H