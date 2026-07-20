#include "py32f071_board.h"
#include "py32f071_regs.h"
#include "rurp_shield.h"

static void clock_init(void)
{
    PY32_RCC->CR |= PY32_BIT(0);
    while ((PY32_RCC->CR & PY32_BIT(1)) == 0u) {
    }
    PY32_RCC->CFGR &= ~3u;
}

void py32_board_init(void)
{
    py32_irq_disable();
    clock_init();
    py32_gpio_init();
    py32_timing_init(8000000u);
    py32_analog_init();

    rurp_set_control_pin(CHIP_ENABLE, 1u);
    rurp_set_control_pin(OUTPUT_ENABLE, 1u);
    rurp_set_control_pin(LEAST_SIGNIFICANT_BYTE, 0u);
    rurp_set_control_pin(MOST_SIGNIFICANT_BYTE, 0u);
    rurp_set_control_pin(CONTROL_REGISTER, 0u);
    rurp_vpp_control_enable(false);

    py32_usb_init();
    py32_irq_enable();
}

void rurp_board_setup(void)
{
    rurp_serial_begin(250000u);
    rurp_set_data_input();
    rurp_chip_disable();
    rurp_chip_input();
    rurp_write_to_register(CONTROL_REGISTER, 0u);
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0u);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0u);
}

void py32_board_task(void)
{
    py32_usb_task();
    if (rurp_read_voltage_mv() >= PY32_VPP_OVERVOLTAGE_MV) {
        rurp_vpp_control_enable(false);
    }
}

void rurp_detect_hardware_revision(void) {}
uint8_t rurp_get_hardware_revision(void) { return REVISION_2_3; }
uint8_t rurp_get_physical_hardware_revision(void) { return REVISION_2_3; }
uint8_t rurp_map_ctrl_reg_for_hardware_revision(rurp_register_t data) { return (uint8_t)data; }

long rurp_get_bandgap_adc_reading(void)
{
    uint16_t vcc = rurp_read_vcc_mv();
    return vcc == 0u ? 0L : (long)((1200u * 4095u) / vcc);
}
