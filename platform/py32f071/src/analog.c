#include "py32f071_board.h"
#include "py32f071_regs.h"

#include <limits.h>

#define ADC_ISR_ADRDY PY32_BIT(0)
#define ADC_ISR_EOC PY32_BIT(2)
#define ADC_CR_ADEN PY32_BIT(0)
#define ADC_CR_ADSTART PY32_BIT(2)
#define ADC_CR_ADCAL PY32_BIT(31)
#define ADC_CCR_VREFEN PY32_BIT(22)
#define ADC_VREFINT_CHANNEL 17u
#define DAC_CR_EN1 PY32_BIT(0)

static py32_vpp_calibration_t g_calibration = {
    .gain_ppm = 1000000,
    .offset_mv = 0,
    .valid = 0
};

static uint16_t clamp_u16(uint32_t value)
{
    return value > UINT16_MAX ? UINT16_MAX : (uint16_t)value;
}

static void adc_select_channel(uint32_t channel)
{
    PY32_ADC1->CHSELR = PY32_BIT(channel);
}

static uint16_t adc_read_channel(uint32_t channel)
{
    adc_select_channel(channel);
    PY32_ADC1->ISR = ADC_ISR_EOC;
    PY32_ADC1->CR |= ADC_CR_ADSTART;
    uint32_t timeout = 100000u;
    while ((PY32_ADC1->ISR & ADC_ISR_EOC) == 0u && timeout-- != 0u) {
    }
    if (timeout == 0u) {
        return 0u;
    }
    return (uint16_t)(PY32_ADC1->DR & PY32_ADC_FULL_SCALE);
}

static uint16_t adc_average(uint32_t channel, uint32_t samples)
{
    uint32_t sum = 0u;
    for (uint32_t i = 0; i < samples; ++i) {
        sum += adc_read_channel(channel);
    }
    return (uint16_t)(sum / samples);
}

void py32_analog_init(void)
{
    PY32_RCC->APBENR2 |= PY32_BIT(9);  /* ADC clock */
    PY32_RCC->APBENR1 |= PY32_BIT(29); /* DAC clock */

    /* PA0 and PA4 analog; PA8 VPP enable output is configured by GPIO init. */
    PY32_GPIOA->MODER |= (3u << (PY32_VPP_ADC_CHANNEL * 2u));
    PY32_GPIOA->PUPDR &= ~(3u << (PY32_VPP_ADC_CHANNEL * 2u));
    PY32_GPIOA->MODER |= (3u << (PY32_VPP_DAC_PIN * 2u));
    PY32_GPIOA->PUPDR &= ~(3u << (PY32_VPP_DAC_PIN * 2u));

    PY32_ADC1->CR = 0u;
    PY32_ADC1->CFGR1 = 0u;
    PY32_ADC1->SMPR = 7u;
    PY32_ADC1->CCR |= ADC_CCR_VREFEN;
    PY32_ADC1->CR |= ADC_CR_ADCAL;
    while ((PY32_ADC1->CR & ADC_CR_ADCAL) != 0u) {
    }
    PY32_ADC1->CR |= ADC_CR_ADEN;
    while ((PY32_ADC1->ISR & ADC_ISR_ADRDY) == 0u) {
    }

    PY32_DAC1->CR = 0u;
    PY32_DAC1->DHR12R1 = 0u;
    PY32_DAC1->CR = DAC_CR_EN1;
    rurp_vpp_control_enable(false);
}

uint16_t rurp_read_vcc_mv(void)
{
    uint16_t vref_raw = adc_average(ADC_VREFINT_CHANNEL, 16u);
    if (vref_raw == 0u) {
        return 0u;
    }
    uint32_t vdda = ((uint32_t)PY32_VREFINT_MV * PY32_ADC_FULL_SCALE + (vref_raw / 2u)) / vref_raw;
    return clamp_u16(vdda);
}

uint16_t rurp_read_voltage_uncalibrated_mv(void)
{
    uint16_t vdda_mv = rurp_read_vcc_mv();
    uint16_t raw = adc_average(PY32_VPP_ADC_CHANNEL, 32u);
    if (vdda_mv == 0u) {
        return 0u;
    }

    uint64_t divider_mv = ((uint64_t)raw * vdda_mv + (PY32_ADC_FULL_SCALE / 2u)) / PY32_ADC_FULL_SCALE;
    uint64_t vpp_mv = divider_mv * (PY32_VPP_DIVIDER_TOP_OHM + PY32_VPP_DIVIDER_BOTTOM_OHM);
    vpp_mv = (vpp_mv + (PY32_VPP_DIVIDER_BOTTOM_OHM / 2u)) / PY32_VPP_DIVIDER_BOTTOM_OHM;
    return clamp_u16((uint32_t)vpp_mv);
}

uint16_t rurp_read_voltage_mv(void)
{
    int64_t measured = rurp_read_voltage_uncalibrated_mv();
    int64_t corrected = (measured * g_calibration.gain_ppm + 500000) / 1000000;
    corrected += g_calibration.offset_mv;
    if (corrected < 0) {
        return 0u;
    }
    return clamp_u16((uint32_t)corrected);
}

bool rurp_calibrate_vpp_two_point(uint16_t measured_low_mv, uint16_t actual_low_mv,
                                  uint16_t measured_high_mv, uint16_t actual_high_mv)
{
    if (measured_high_mv <= measured_low_mv || actual_high_mv <= actual_low_mv) {
        return false;
    }

    int64_t measured_span = (int64_t)measured_high_mv - measured_low_mv;
    int64_t actual_span = (int64_t)actual_high_mv - actual_low_mv;
    int64_t gain_ppm = (actual_span * 1000000 + (measured_span / 2)) / measured_span;
    int64_t offset_mv = actual_low_mv - (((int64_t)measured_low_mv * gain_ppm + 500000) / 1000000);

    if (gain_ppm < 500000 || gain_ppm > 1500000 || offset_mv < -5000 || offset_mv > 5000) {
        return false;
    }

    g_calibration.gain_ppm = (int32_t)gain_ppm;
    g_calibration.offset_mv = (int32_t)offset_mv;
    g_calibration.measured_low_mv = measured_low_mv;
    g_calibration.actual_low_mv = actual_low_mv;
    g_calibration.measured_high_mv = measured_high_mv;
    g_calibration.actual_high_mv = actual_high_mv;
    g_calibration.valid = 1u;
    return true;
}

void rurp_reset_vpp_calibration(void)
{
    g_calibration.gain_ppm = 1000000;
    g_calibration.offset_mv = 0;
    g_calibration.measured_low_mv = 0u;
    g_calibration.actual_low_mv = 0u;
    g_calibration.measured_high_mv = 0u;
    g_calibration.actual_high_mv = 0u;
    g_calibration.valid = 0u;
}

const py32_vpp_calibration_t *rurp_get_vpp_calibration(void)
{
    return &g_calibration;
}

void py32_set_vpp_calibration(const py32_vpp_calibration_t *calibration)
{
    if (calibration != 0 && calibration->valid != 0u) {
        g_calibration = *calibration;
    } else {
        rurp_reset_vpp_calibration();
    }
}

void rurp_vpp_dac_write(uint16_t code)
{
    if (code > RURP_VPP_DAC_MAX_CODE) {
        code = RURP_VPP_DAC_MAX_CODE;
    }
    PY32_DAC1->DHR12R1 = code;
}

uint16_t rurp_vpp_dac_max_code(void)
{
    return RURP_VPP_DAC_MAX_CODE;
}

void rurp_vpp_control_enable(bool enabled)
{
    if (enabled) {
        PY32_GPIOA->BSRR = PY32_BIT(PY32_VPP_ENABLE_PIN);
    } else {
        PY32_GPIOA->BSRR = PY32_BIT(PY32_VPP_ENABLE_PIN + 16u);
        rurp_vpp_dac_write(0u);
    }
}

py32_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv, uint16_t tolerance_mv, uint32_t timeout_ms)
{
    if (target_mv == 0u) {
        rurp_vpp_control_enable(false);
        return PY32_VPP_OK;
    }
    if (target_mv > PY32_MAX_VPP_TARGET_MV || tolerance_mv == 0u) {
        return PY32_VPP_BAD_TARGET;
    }

    uint32_t code = ((uint32_t)target_mv * RURP_VPP_DAC_MAX_CODE) / PY32_MAX_VPP_TARGET_MV;
    rurp_vpp_dac_write((uint16_t)code);
    rurp_vpp_control_enable(true);
    uint32_t deadline = rurp_millis() + timeout_ms;

    while ((int32_t)(rurp_millis() - deadline) < 0) {
        uint16_t measured_mv = rurp_read_voltage_mv();
        if (measured_mv == 0u) {
            rurp_vpp_control_enable(false);
            return PY32_VPP_ADC_FAULT;
        }
        if (measured_mv >= PY32_VPP_OVERVOLTAGE_MV) {
            rurp_vpp_control_enable(false);
            return PY32_VPP_OVERVOLTAGE;
        }

        int32_t error_mv = (int32_t)target_mv - measured_mv;
        if (error_mv <= (int32_t)tolerance_mv && error_mv >= -(int32_t)tolerance_mv) {
            return PY32_VPP_OK;
        }

        int32_t step = (error_mv * (int32_t)RURP_VPP_DAC_MAX_CODE) / (int32_t)PY32_MAX_VPP_TARGET_MV;
        if (step == 0) {
            step = error_mv > 0 ? 1 : -1;
        }
        if (step > 128) step = 128;
        if (step < -128) step = -128;

        int32_t next_code = (int32_t)code + step;
        if (next_code < 0) next_code = 0;
        if (next_code > (int32_t)RURP_VPP_DAC_MAX_CODE) next_code = RURP_VPP_DAC_MAX_CODE;
        code = (uint32_t)next_code;
        rurp_vpp_dac_write((uint16_t)code);
        rurp_delay_ms(2u);
    }

    rurp_vpp_control_enable(false);
    return PY32_VPP_TIMEOUT;
}
