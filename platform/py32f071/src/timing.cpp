#include "boards/py32f071_rurp_shield.h"

namespace
{
TIM_HandleTypeDef microsecond_timer;
}

extern "C" void rurp_timing_init(void)
{
    __HAL_RCC_TIM3_CLK_ENABLE();

    microsecond_timer.Instance = TIM3;
    microsecond_timer.Init.Prescaler = (HAL_RCC_GetPCLK1Freq() / 1000000U) - 1U;
    microsecond_timer.Init.CounterMode = TIM_COUNTERMODE_UP;
    microsecond_timer.Init.Period = 0xFFFFU;
    microsecond_timer.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    microsecond_timer.Init.RepetitionCounter = 0U;
    microsecond_timer.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;

    if (HAL_TIM_Base_Init(&microsecond_timer) != HAL_OK)
    {
        for (;;)
        {
        }
    }

    if (HAL_TIM_Base_Start(&microsecond_timer) != HAL_OK)
    {
        for (;;)
        {
        }
    }
}

extern "C" uint32_t rurp_millis(void)
{
    return HAL_GetTick();
}

extern "C" uint32_t rurp_micros(void)
{
    uint32_t milliseconds_before;
    uint32_t milliseconds_after;
    uint32_t counter;
    uint32_t reload;

    do
    {
        milliseconds_before = HAL_GetTick();
        counter = SysTick->VAL;
        reload = SysTick->LOAD + 1U;
        milliseconds_after = HAL_GetTick();
    } while (milliseconds_before != milliseconds_after);

    const uint32_t elapsed_ticks = reload - counter;
    const uint32_t elapsed_microseconds =
        (elapsed_ticks * 1000U) / reload;

    return (milliseconds_before * 1000U) + elapsed_microseconds;
}

extern "C" void rurp_delay_us(uint32_t microseconds)
{
    while (microseconds != 0U)
    {
        const uint16_t chunk =
            static_cast<uint16_t>(microseconds > 60000U ? 60000U : microseconds);
        const uint16_t start =
            static_cast<uint16_t>(__HAL_TIM_GET_COUNTER(&microsecond_timer));

        while (static_cast<uint16_t>(
                   static_cast<uint16_t>(__HAL_TIM_GET_COUNTER(&microsecond_timer)) - start) < chunk)
        {
        }

        microseconds -= chunk;
    }
}

extern "C" void rurp_delay_ms(uint32_t milliseconds)
{
    HAL_Delay(milliseconds);
}

extern "C" void SysTick_Handler(void)
{
    HAL_IncTick();
}
