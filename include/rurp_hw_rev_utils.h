#ifndef __RURP_HW_REV_UTILS_H__
#define __RURP_HW_REV_UTILS_H__

#ifdef HARDWARE_REVISION

#include "rurp_shield.h"
#include "rurp_pinout.h"
#include <Arduino.h>
#include <stdint.h>
#include <string.h>

uint8_t revision = 0xFF;

uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) {
    uint8_t ctrl_reg = 0;
    uint8_t hw = rurp_get_hardware_revision();
    switch (hw) {
    case REVISION_2_0:
    case REVISION_2_1:
    case REVISION_2_2: 
        ctrl_reg = data & (CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_ADDRESS_LINE_17 | CTRL_READ_WRITE | CTRL_VPP_REGULATOR_ENABLE);
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_16 ? CTRL_ADDRESS_LINE_16_REV2 : 0;
        ctrl_reg |= data & CTRL_ADDRESS_LINE_18 ? CTRL_ADDRESS_LINE_18_REV2 : 0;
        break;
    case REVISION_0:
    case REVISION_1:
        ctrl_reg = data;
        ctrl_reg |= data & CTRL_VPP_VPE_DROP_ENABLE ? CTRL_VPP_VPE_DROP_ENABLE_REV1 : 0;
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
    pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT_PULLUP);

    int value = digitalRead(PIN_HW_REVISION_DETECT_ADC);
    switch (value) {
    case 1:
        revision = analogRead(PIN_VPP_VOLTAGE_ADC) < 1000 ? REVISION_1 : REVISION_0;
        break;
    case 0:
        revision = REVISION_2_0;
        break;
    default:
        // Unknown hardware revision
        revision = 0xFF;
    }
    pinMode(PIN_VPP_VOLTAGE_ADC, INPUT);
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