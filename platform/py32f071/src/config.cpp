#include "rurp_shield.h"
#include "py32f071_board.h"

#include <string.h>

static rurp_configuration_t g_rurp_configuration;

extern "C" rurp_configuration_t *rurp_get_config(void)
{
    return &g_rurp_configuration;
}

extern "C" void rurp_validate_config(rurp_configuration_t *config)
{
    if (strcmp(config->version, CONFIG_VERSION) != 0 || config->r2 <= 0) {
        memset(config, 0, sizeof(*config));
        strcpy(config->version, CONFIG_VERSION);
        config->r1 = VALUE_R1;
        config->r2 = VALUE_R2;
        config->hardware_revision = 0xFFu;
    }
}

extern "C" void rurp_load_config(void)
{
    py32_stored_configuration_t stored;
    if (py32_storage_load(&stored)) {
        g_rurp_configuration = stored.configuration;
        py32_set_vpp_calibration(&stored.vpp);
    } else {
        memset(&g_rurp_configuration, 0, sizeof(g_rurp_configuration));
        rurp_reset_vpp_calibration();
    }
    rurp_validate_config(&g_rurp_configuration);
}

extern "C" void rurp_save_config(rurp_configuration_t *config)
{
    rurp_validate_config(config);
    g_rurp_configuration = *config;

    py32_stored_configuration_t stored = {};
    stored.configuration = g_rurp_configuration;
    stored.vpp = *rurp_get_vpp_calibration();
    (void)py32_storage_save(&stored);
}
