#pragma once

#include <stddef.h>
#include <stdint.h>

#include "py32f0xx_hal.h"
#include "rurp_platform.h"

#if !defined(RURP_PLATFORM_PY32F071)
#error "py32f071_rurp_shield.h included for the wrong platform"
#endif

/*
 * Provisional example pin map for early firmware builds.
 *
 * IMPORTANT: This is NOT a verified Firestarter PCB assignment. It is a
 * replaceable example chosen to keep the eight-bit data bus contiguous and to
 * use a vendor-documented ADC input. Update every definition below when the
 * final schematic/pinout is available, then validate the signals on hardware
 * before connecting a PROM or enabling programming voltage.
 *
 * Example mapping:
 *
 *   PROM D0-D7       PB0-PB7
 *   LSB latch        PA0
 *   MSB latch        PA1
 *   /OE              PA2
 *   control latch    PA3
 *   VPP measurement  PA4 / ADC channel 4
 *   /CE              PA5
 *   user button      not fitted
 *
 * PA4 / ADC channel 4 follows the official Puya PY32F071 ADC example. The
 * remaining assignments are provisional and describe no existing PCB.
 */

#define RURP_PY32F071_PINMAP_CONFIGURED 1
#define RURP_PY32F071_PINMAP_PROVISIONAL 1

/*
 * Phase 124 Plan 08 (MERGE-04, D-11/D-12): bridge this board-specific
 * provisional flag to the platform-neutral RURP_PINMAP_PROVISIONAL flag
 * that include/rurp_pinmap_guard.h's shared refusal predicate tests. This
 * single block does two jobs at once:
 *
 *   1. The `#if RURP_PY32F071_PINMAP_PROVISIONAL` test below is itself a
 *      real CONSUMER of RURP_PY32F071_PINMAP_PROVISIONAL, discharging
 *      scripts/check_orphan_provisional.py for THIS macro -- before this
 *      block, the flag had zero consumers repo-wide (the exact violation
 *      that gate reported on arrival).
 *   2. It DEFINES the neutral flag, wrapped in its own inner #ifndef so a
 *      command-line definition of RURP_PINMAP_PROVISIONAL still wins
 *      without triggering a macro-redefinition warning
 *      (check_build_warnings.py counts those).
 *
 * Per correction C-12, firestarter/tests/ is NOT scanned by
 * check_orphan_provisional.py, so a pytest cannot serve as either macro's
 * consumer -- both consumers must live in include/, src/, platform/ or
 * test/, which is exactly where this block and rurp_pinmap_guard.h sit.
 *
 * REMOVING this block would make RURP_PY32F071_PINMAP_PROVISIONAL orphaned
 * again (zero consumers) AND would silently stop defining
 * RURP_PINMAP_PROVISIONAL, which would make configure_memory()'s refusal
 * compile away on this board -- do not remove without replacing both jobs.
 */
#if RURP_PY32F071_PINMAP_PROVISIONAL
#ifndef RURP_PINMAP_PROVISIONAL
#define RURP_PINMAP_PROVISIONAL 1
#endif
#endif

#define RURP_PY32F071_ENABLE_GPIO_CLOCKS() \
    do                                             \
    {                                              \
        __HAL_RCC_GPIOA_CLK_ENABLE();              \
        __HAL_RCC_GPIOB_CLK_ENABLE();              \
    } while (0)

#define RURP_PY32F071_DATA_PORT GPIOB
#define RURP_PY32F071_DATA_SHIFT 0U

#define RURP_PY32F071_LSB_PORT GPIOA
#define RURP_PY32F071_LSB_PIN GPIO_PIN_0

#define RURP_PY32F071_MSB_PORT GPIOA
#define RURP_PY32F071_MSB_PIN GPIO_PIN_1

#define RURP_PY32F071_OE_PORT GPIOA
#define RURP_PY32F071_OE_PIN GPIO_PIN_2

#define RURP_PY32F071_CONTROL_PORT GPIOA
#define RURP_PY32F071_CONTROL_PIN GPIO_PIN_3

#define RURP_PY32F071_VPP_ADC_PORT GPIOA
#define RURP_PY32F071_VPP_ADC_PIN GPIO_PIN_4
#define RURP_PY32F071_VPP_ADC_CHANNEL ADC_CHANNEL_4

#define RURP_PY32F071_CE_PORT GPIOA
#define RURP_PY32F071_CE_PIN GPIO_PIN_5

#define RURP_PY32F071_HAS_USER_BUTTON 0

#if !RURP_PY32F071_PINMAP_CONFIGURED
#error "Configure the PY32F071 Firestarter wiring in include/boards/py32f071_rurp_shield.h"
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
