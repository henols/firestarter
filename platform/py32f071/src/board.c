#include "py32f071_board.h"
#include "py32f071_regs.h"

void py32_timing_init(uint32_t core_clock_hz);
void py32_gpio_init(void);

static py32_stored_configuration_t g_configuration;

static void clock_init(void)
{
    /* Keep the first implementation on the reset-safe 8 MHz internal clock.
       The final board may switch to PLL/HSI48 when USB clock validation is added. */
    PY32_RCC->CR |= PY32_BIT(0);
    while ((PY32_RCC->CR & PY32_BIT(1)) == 0u) {
    }
    PY32_RCC->CFGR &= ~3u;
}

static void load_configuration(void)
{
    if (py32_storage_load(&g_configuration)) {
        py32_set_vpp_calibration(&g_configuration.vpp);
    } else {
        g_configuration.magic = 0u;
        g_configuration.version = 0u;
        g_configuration.length = 0u;
        g_configuration.sequence = 0u;
        rurp_reset_vpp_calibration();
    }
}

void py32_board_init(void)
{
    py32_irq_disable();
    clock_init();
    py32_gpio_init();
    py32_timing_init(8000000u);
    py32_analog_init();

    /* Safe socket state before communication is exposed. */
    rurp_set_control_pin(PY32_REG_CE, 1u);
    rurp_set_control_pin(PY32_REG_OE, 1u);
    rurp_set_control_pin(PY32_REG_LSB, 0u);
    rurp_set_control_pin(PY32_REG_MSB, 0u);
    rurp_set_control_pin(PY32_REG_CTRL, 0u);
    rurp_vpp_control_enable(false);

    load_configuration();
    py32_usb_init();
    py32_irq_enable();
}

void py32_board_task(void)
{
    py32_usb_task();

    /* Independent software overvoltage interlock even when no target update is active. */
    uint16_t vpp_mv = rurp_read_voltage_mv();
    if (vpp_mv >= PY32_VPP_OVERVOLTAGE_MV) {
        rurp_vpp_control_enable(false);
    }
}

bool py32_save_current_configuration(void)
{
    g_configuration.vpp = *rurp_get_vpp_calibration();
    return py32_storage_save(&g_configuration);
}
