#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RURP_PLATFORM_PY32F071 1
#define RURP_HAS_VPP_DAC 1
#define RURP_VPP_DAC_BITS 12u
#define RURP_VPP_DAC_MAX_CODE 4095u

/* Temporary pin assignment. Change only this section when the PCB pinout is fixed. */
#define PY32_DATA_GPIO_PORT_INDEX 1u /* GPIOB */
#define PY32_DATA_PIN_SHIFT 0u       /* PB0..PB7 */
#define PY32_CTRL_GPIO_PORT_INDEX 2u /* GPIOC */
#define PY32_CTRL_PIN_SHIFT 0u       /* PC0..PC7 */
#define PY32_USER_BUTTON_PIN 13u     /* PC13, active low */
#define PY32_VPP_ADC_CHANNEL 0u      /* PA0 / ADC_IN0 */
#define PY32_VPP_DAC_PIN 4u          /* PA4 / DAC_OUT1 */
#define PY32_VPP_ENABLE_PIN 8u       /* PA8 */

#define PY32_VPP_DIVIDER_TOP_OHM 270000u
#define PY32_VPP_DIVIDER_BOTTOM_OHM 44000u
#define PY32_VREFINT_MV 1200u
#define PY32_ADC_FULL_SCALE 4095u
#define PY32_MAX_VPP_TARGET_MV 30000u
#define PY32_VPP_OVERVOLTAGE_MV 33000u

/* Logical register select/control identifiers retained from Firestarter. */
#define PY32_REG_LSB 0x01u
#define PY32_REG_MSB 0x02u
#define PY32_REG_OE  0x04u
#define PY32_REG_CTRL 0x08u
#define PY32_REG_CE  0x20u

typedef enum {
    PY32_VPP_OK = 0,
    PY32_VPP_TIMEOUT = -1,
    PY32_VPP_BAD_TARGET = -2,
    PY32_VPP_OVERVOLTAGE = -3,
    PY32_VPP_ADC_FAULT = -4
} py32_vpp_result_t;

typedef struct {
    int32_t gain_ppm;
    int32_t offset_mv;
    uint16_t measured_low_mv;
    uint16_t actual_low_mv;
    uint16_t measured_high_mv;
    uint16_t actual_high_mv;
    uint8_t valid;
} py32_vpp_calibration_t;

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint16_t length;
    uint32_t sequence;
    py32_vpp_calibration_t vpp;
    uint32_t crc32;
} py32_stored_configuration_t;

void py32_board_init(void);
void py32_board_task(void);

uint32_t rurp_millis(void);
void rurp_delay_ms(uint32_t milliseconds);
void rurp_delay_us(uint32_t microseconds);

void rurp_set_data_output(void);
void rurp_set_data_input(void);
void rurp_write_data_buffer(uint8_t data);
uint8_t rurp_read_data_buffer(void);
void rurp_set_control_pin(uint8_t logical_pin, uint8_t state);
uint8_t rurp_user_button_pressed(void);

void py32_analog_init(void);
uint16_t rurp_read_vcc_mv(void);
uint16_t rurp_read_voltage_uncalibrated_mv(void);
uint16_t rurp_read_voltage_mv(void);
void rurp_vpp_dac_write(uint16_t code);
uint16_t rurp_vpp_dac_max_code(void);
void rurp_vpp_control_enable(bool enabled);
py32_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv, uint16_t tolerance_mv, uint32_t timeout_ms);
bool rurp_calibrate_vpp_two_point(uint16_t measured_low_mv, uint16_t actual_low_mv,
                                  uint16_t measured_high_mv, uint16_t actual_high_mv);
void rurp_reset_vpp_calibration(void);
const py32_vpp_calibration_t *rurp_get_vpp_calibration(void);
void py32_set_vpp_calibration(const py32_vpp_calibration_t *calibration);

void py32_usb_init(void);
void py32_usb_task(void);
void py32_usb_rx_bytes(const uint8_t *data, size_t length);
size_t py32_usb_tx_read(uint8_t *data, size_t capacity);
int rurp_communication_available(void);
int rurp_communication_read(void);
int rurp_communication_peak(void);
size_t rurp_communication_read_bytes(char *buffer, size_t length);
size_t rurp_communication_write(const char *buffer, size_t length);
int rurp_communication_read_data(char *buffer, size_t capacity);

bool py32_storage_load(py32_stored_configuration_t *configuration);
bool py32_storage_save(const py32_stored_configuration_t *configuration);
uint32_t py32_crc32(const void *data, size_t length);

#ifdef __cplusplus
}
#endif
