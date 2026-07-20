#include "py32f071_board.h"
#include "py32f071_regs.h"

static volatile uint32_t g_milliseconds;
static uint32_t g_core_clock_hz = 8000000u;

void py32_timing_init(uint32_t core_clock_hz)
{
    g_core_clock_hz = core_clock_hz;
    g_milliseconds = 0;
    PY32_SYSTICK->LOAD = (core_clock_hz / 1000u) - 1u;
    PY32_SYSTICK->VAL = 0;
    PY32_SYSTICK->CTRL = PY32_BIT(2) | PY32_BIT(1) | PY32_BIT(0);

    /* TIM3 free-running at 1 MHz for microsecond delays. */
    PY32_RCC->APBENR1 |= PY32_BIT(1);
    PY32_TIM3->CR1 = 0;
    PY32_TIM3->PSC = (core_clock_hz / 1000000u) - 1u;
    PY32_TIM3->ARR = 0xFFFFu;
    PY32_TIM3->EGR = 1u;
    PY32_TIM3->CNT = 0;
    PY32_TIM3->CR1 = 1u;
}

void SysTick_Handler(void)
{
    ++g_milliseconds;
}

uint32_t rurp_millis(void)
{
    return g_milliseconds;
}

void rurp_delay_us(uint32_t microseconds)
{
    while (microseconds != 0u) {
        uint32_t chunk = microseconds > 60000u ? 60000u : microseconds;
        uint16_t start = (uint16_t)PY32_TIM3->CNT;
        while ((uint16_t)((uint16_t)PY32_TIM3->CNT - start) < (uint16_t)chunk) {
        }
        microseconds -= chunk;
    }
}

void rurp_delay_ms(uint32_t milliseconds)
{
    uint32_t deadline = rurp_millis() + milliseconds;
    while ((int32_t)(rurp_millis() - deadline) < 0) {
        py32_usb_task();
        py32_wait_for_interrupt();
    }
}

uint32_t py32_core_clock_hz(void)
{
    return g_core_clock_hz;
}
