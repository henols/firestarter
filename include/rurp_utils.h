#ifndef RURP_UTILS_H
#define RURP_UTILS_H

#include <stdint.h>
#include <EEPROM.h>
#include <string.h>

#include "rurp_shield.h"

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

#define CONFIG_START 48

void load_config() {
    rurp_configuration_t *rurp_config = rurp_get_config();
    EEPROM.get(CONFIG_START, rurp_config);
    rurp_validate_config();
}

void rurp_save_config() {
    rurp_configuration_t *rurp_config = rurp_get_config();
    EEPROM.put(CONFIG_START, rurp_config);
}

void rurp_validate_config() {
        rurp_configuration_t* rurp_config = rurp_get_config();
        if (strcmp(rurp_config->version, "VER03") == 0 || strcmp(rurp_config->version, "VER04") == 0) {
            strcpy(rurp_config->version, CONFIG_VERSION);
            if (strcmp(rurp_config->version, "VER03") == 0 || rurp_config->hardware_revision == 0x00) {
                rurp_config->hardware_revision = 0xFF;
            }
            rurp_save_config();
        }
        else if (strcmp(rurp_config->version, CONFIG_VERSION) != 0) {
            strcpy(rurp_config->version, CONFIG_VERSION);
            rurp_config->vcc = ARDUINO_VCC;
            rurp_config->r1 = VALUE_R1;
            rurp_config->r2 = VALUE_R2;
            rurp_config->hardware_revision = 0xFF;
            rurp_save_config();
        }
    }

#include <string.h>

#endif // RURP_UTILS_H