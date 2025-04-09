#ifndef __RURP_CONFIG_UTILS_H__
#define __RURP_CONFIG_UTILS_H__

#include <stdint.h>
#include <EEPROM.h>
#include <string.h>

#include "rurp_shield.h"

#define CONFIG_START 48

rurp_configuration_t rurp_config;

rurp_configuration_t* rurp_get_config() {
    return &rurp_config;
}

void rurp_load_config() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    EEPROM.get(CONFIG_START, *rurp_config);
    rurp_validate_config(rurp_config);
}

void rurp_save_config(rurp_configuration_t* rurp_config) {
    EEPROM.put(CONFIG_START, *rurp_config);
}

void rurp_validate_config(rurp_configuration_t* rurp_config) {
    // if (strcmp(rurp_config->version, "VER03") == 0 || strcmp(rurp_config->version, "VER04") == 0) {
    //     if (strcmp(rurp_config->version, "VER03") == 0 || rurp_config->hardware_revision == 0x00) {
    //         rurp_config->hardware_revision = 0xFF;
    //     }
    //     strcpy(rurp_config->version, CONFIG_VERSION);
    //     rurp_save_config(rurp_config);
    // }
    // else 
    if (strcmp(rurp_config->version, CONFIG_VERSION) != 0) {
        strcpy(rurp_config->version, CONFIG_VERSION);
        rurp_config->r1 = VALUE_R1;
        rurp_config->r2 = VALUE_R2;
        rurp_config->hardware_revision = 0xFF;
        rurp_save_config(rurp_config);
    }
}
#endif // __RURP_CONFIG_UTILS_H__