#include <string.h>

#include "rurp_shield.h"

namespace
{
rurp_configuration_t configuration;
}

extern "C" rurp_configuration_t *rurp_get_config(void)
{
    return &configuration;
}

extern "C" void rurp_validate_config(rurp_configuration_t *value)
{
    if (value == nullptr)
    {
        return;
    }

    if (strcmp(value->version, CONFIG_VERSION) != 0 || value->r2 == 0)
    {
        memset(value, 0, sizeof(*value));
        strcpy(value->version, CONFIG_VERSION);
        value->r1 = VALUE_R1;
        value->r2 = VALUE_R2;
        value->hardware_revision = 0xFFU;
    }
}

extern "C" void rurp_load_config(void)
{
    memset(&configuration, 0, sizeof(configuration));
    rurp_validate_config(&configuration);
}

extern "C" void rurp_save_config(rurp_configuration_t *value)
{
    if (value == nullptr)
    {
        return;
    }

    rurp_validate_config(value);
    configuration = *value;
}
