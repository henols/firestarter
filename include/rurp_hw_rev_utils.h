#ifndef __RURP_HW_REV_UTILS_H__
#define __RURP_HW_REV_UTILS_H__

#ifdef HARDWARE_REVISION

#include "rurp_shield.h"
#include <Arduino.h>
#include <stdint.h>
#include <string.h>

uint8_t revision = 0xFF;

uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2:
        ctrl_reg = data & (A9_VPP_ENABLE | VPE_ENABLE | P1_VPP_ENABLE | ADDRESS_LINE_17 | READ_WRITE | REGULATOR);
        ctrl_reg |= data & VPE_TO_VPP ? REV_2_VPE_TO_VPP : 0;
        ctrl_reg |= data & ADDRESS_LINE_16 ? REV_2_ADDRESS_LINE_16 : 0;
        ctrl_reg |= data & ADDRESS_LINE_18 ? REV_2_ADDRESS_LINE_18 : 0;
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

uint8_t rurp_get_physical_hardware_revision() {
    return revision;
}

void rurp_detect_hardware_revision() {
    pinMode(HARDWARE_REVISION_PIN, INPUT_PULLUP);
    pinMode(VOLTAGE_MEASURE_PIN, INPUT_PULLUP);

    int value = digitalRead(HARDWARE_REVISION_PIN);
    switch (value) {
    case 1:
        revision = analogRead(VOLTAGE_MEASURE_PIN) < 1000 ? REVISION_1 : REVISION_0;
        break;
    case 0:
        revision = REVISION_2;
        break;
    default:
        // Unknown hardware revision
        revision = 0xFF;
    }
    pinMode(VOLTAGE_MEASURE_PIN, INPUT);
}

uint8_t rurp_get_hardware_revision() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    if (rurp_config->hardware_revision < 0xFF) {
        return rurp_config->hardware_revision;
    }
    return rurp_get_physical_hardware_revision();
}

#endif

#endif // __RURP_HW_REV_UTILS_H__