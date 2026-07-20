#pragma once

#include <stdint.h>

#define PY32_PERIPH_BASE      0x40000000u
#define PY32_AHBPERIPH_BASE   0x40020000u
#define PY32_IOPPERIPH_BASE   0x50000000u

#define PY32_RCC_BASE         0x40021000u
#define PY32_FLASH_BASE       0x40022000u
#define PY32_ADC1_BASE        0x40012400u
#define PY32_DAC1_BASE        0x40007400u
#define PY32_TIM3_BASE        0x40000400u
#define PY32_GPIOA_BASE       0x50000000u
#define PY32_GPIOB_BASE       0x50000400u
#define PY32_GPIOC_BASE       0x50000800u

#define PY32_SYSTICK_BASE     0xE000E010u
#define PY32_NVIC_ISER_BASE   0xE000E100u

typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
    volatile uint32_t BRR;
} py32_gpio_t;

typedef struct {
    volatile uint32_t CR;
    volatile uint32_t ICSCR;
    volatile uint32_t CFGR;
    volatile uint32_t PLLCFGR;
    volatile uint32_t RESERVED0;
    volatile uint32_t CRRCR;
    volatile uint32_t CIER;
    volatile uint32_t CIFR;
    volatile uint32_t CICR;
    volatile uint32_t IOPRSTR;
    volatile uint32_t AHBRSTR;
    volatile uint32_t APBRSTR1;
    volatile uint32_t APBRSTR2;
    volatile uint32_t IOPENR;
    volatile uint32_t AHBENR;
    volatile uint32_t APBENR1;
    volatile uint32_t APBENR2;
} py32_rcc_t;

typedef struct {
    volatile uint32_t ISR;
    volatile uint32_t IER;
    volatile uint32_t CR;
    volatile uint32_t CFGR1;
    volatile uint32_t CFGR2;
    volatile uint32_t SMPR;
    volatile uint32_t RESERVED0[2];
    volatile uint32_t TR;
    volatile uint32_t RESERVED1;
    volatile uint32_t CHSELR;
    volatile uint32_t RESERVED2[5];
    volatile uint32_t DR;
    volatile uint32_t RESERVED3[177];
    volatile uint32_t CCR;
} py32_adc_t;

typedef struct {
    volatile uint32_t CR;
    volatile uint32_t SWTRIGR;
    volatile uint32_t DHR12R1;
    volatile uint32_t DHR12L1;
    volatile uint32_t DHR8R1;
    volatile uint32_t DHR12R2;
    volatile uint32_t DHR12L2;
    volatile uint32_t DHR8R2;
    volatile uint32_t DHR12RD;
    volatile uint32_t DHR12LD;
    volatile uint32_t DHR8RD;
    volatile uint32_t DOR1;
    volatile uint32_t DOR2;
    volatile uint32_t SR;
} py32_dac_t;

typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
} py32_tim_t;

typedef struct {
    volatile uint32_t ACR;
    volatile uint32_t KEYR;
    volatile uint32_t OPTKEYR;
    volatile uint32_t SR;
    volatile uint32_t CR;
    volatile uint32_t ECCR;
} py32_flash_t;

typedef struct {
    volatile uint32_t CTRL;
    volatile uint32_t LOAD;
    volatile uint32_t VAL;
    volatile uint32_t CALIB;
} py32_systick_t;

#define PY32_GPIOA ((py32_gpio_t *)PY32_GPIOA_BASE)
#define PY32_GPIOB ((py32_gpio_t *)PY32_GPIOB_BASE)
#define PY32_GPIOC ((py32_gpio_t *)PY32_GPIOC_BASE)
#define PY32_RCC   ((py32_rcc_t *)PY32_RCC_BASE)
#define PY32_ADC1  ((py32_adc_t *)PY32_ADC1_BASE)
#define PY32_DAC1  ((py32_dac_t *)PY32_DAC1_BASE)
#define PY32_TIM3  ((py32_tim_t *)PY32_TIM3_BASE)
#define PY32_FLASH ((py32_flash_t *)PY32_FLASH_BASE)
#define PY32_SYSTICK ((py32_systick_t *)PY32_SYSTICK_BASE)

#define PY32_BIT(n) (1u << (n))

static inline void py32_irq_enable(void) { __asm volatile ("cpsie i" ::: "memory"); }
static inline void py32_irq_disable(void) { __asm volatile ("cpsid i" ::: "memory"); }
static inline void py32_wait_for_interrupt(void) { __asm volatile ("wfi"); }
