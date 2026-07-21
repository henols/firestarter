#pragma once

#include <stddef.h>
#include <stdint.h>

#include "py32f0xx_hal.h"
#include "rurp_platform.h"

#if !defined(RURP_PLATFORM_PY32F071)
#error "py32f071_rurp_shield.h included for the wrong platform"
#endif

/*
 * This header is the single physical-pin definition point for the PY32F071
 * Firestarter board. The implementation guide explicitly marks its RP2040 pin
 * numbers as examples, so this target must not substitute guessed PY32 pins.
 *
 * Define the actual board wiring below, then set
 * RURP_PY32F071_PINMAP_CONFIGURED to 1.
 *
 * Required definitions:
 *
 *   RURP_PY32F071_ENABLE_GPIO_CLOCKS()
 *
 *   RURP_PY32F071_DATA_PORT          GPIO_TypeDef *
 *   RURP_PY32F071_DATA_SHIFT         first pin number of a contiguous D0-D7 bus
 *
 *   RURP_PY32F071_LSB_PORT           GPIO_TypeDef *
 *   RURP_PY32F071_LSB_PIN            GPIO_PIN_x
 *   RURP_PY32F071_MSB_PORT           GPIO_TypeDef *
 *   RURP_PY32F071_MSB_PIN            GPIO_PIN_x
 *   RURP_PY32F071_OE_PORT            GPIO_TypeDef *
 *   RURP_PY32F071_OE_PIN             GPIO_PIN_x
 *   RURP_PY32F071_CONTROL_PORT       GPIO_TypeDef *
 *   RURP_PY32F071_CONTROL_PIN        GPIO_PIN_x
 *   RURP_PY32F071_CE_PORT            GPIO_TypeDef *
 *   RURP_PY32F071_CE_PIN             GPIO_PIN_x
 *
 *   RURP_PY32F071_VPP_ADC_PORT       GPIO_TypeDef *
 *   RURP_PY32F071_VPP_ADC_PIN        GPIO_PIN_x
 *   RURP_PY32F071_VPP_ADC_CHANNEL    ADC_CHANNEL_x
 *
 * Optional user button:
 *
 *   RURP_PY32F071_HAS_USER_BUTTON    0 or 1
 *   RURP_PY32F071_BUTTON_PORT         GPIO_TypeDef *  (when enabled)
 *   RURP_PY32F071_BUTTON_PIN          GPIO_PIN_x       (when enabled)
 */

#ifndef RURP_PY32F071_PINMAP_CONFIGURED
#define RURP_PY32F071_PINMAP_CONFIGURED 0
#endif

#if !RURP_PY32F071_PINMAP_CONFIGURED
#error "Configure the actual PY32F071 Firestarter wiring in include/boards/py32f071_rurp_shield.h"
#endif

#ifndef RURP_PY32F071_HAS_USER_BUTTON
#define RURP_PY32F071_HAS_USER_BUTTON 0
#endif

#if RURP_PY32F071_DATA_SHIFT > 8
#error "The contiguous PY32F071 D0-D7 bus must fit within one 16-pin GPIO port"
#endif

#ifdef __cplusplus
extern "C" {
#endif

void rurp_communication_begin(void);
void rurp_timing_init(void);

#ifdef __cplusplus
}
#endif
