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
#define PY32_DATA