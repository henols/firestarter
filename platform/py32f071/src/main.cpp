#include "boards/py32f071_rurp_shield.h"

extern void setup(void);
extern void loop(void);

namespace
{
[[noreturn]] void error_handler()
{
    for (;;)
    {
    }
}

void configure_system_clock()
{
    RCC_OscInitTypeDef oscillator = {};
    RCC_ClkInitTypeDef clocks = {};

    oscillator.OscillatorType =
        RCC_OSCILLATORTYPE_HSE |
        RCC_OSCILLATORTYPE_HSI |
        RCC_OSCILLATORTYPE_LSI |
        RCC_OSCILLATORTYPE_LSE;
    oscillator.HSIState = RCC_HSI_ON;
    oscillator.HSIDiv = RCC_HSI_DIV1;
    oscillator.HSICalibrationValue = RCC_HSICALIBRATION_24MHz;
    oscillator.HSEState = RCC_HSE_OFF;
    oscillator.LSIState = RCC_LSI_OFF;
    oscillator.LSEState = RCC_LSE_OFF;
    oscillator.PLL.PLLState = RCC_PLL_ON;
    oscillator.PLL.PLLSource = RCC_PLLSOURCE_HSI;
    oscillator.PLL.PLLMUL = RCC_PLL_MUL2;

    if (HAL_RCC_OscConfig(&oscillator) != HAL_OK)
    {
        error_handler();
    }

    clocks.ClockType =
        RCC_CLOCKTYPE_HCLK |
        RCC_CLOCKTYPE_SYSCLK |
        RCC_CLOCKTYPE_PCLK1;
    clocks.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    clocks.AHBCLKDivider = RCC_SYSCLK_DIV1;
    clocks.APB1CLKDivider = RCC_HCLK_DIV1;

    if (HAL_RCC_ClockConfig(&clocks, FLASH_ACR_LATENCY_1) != HAL_OK)
    {
        error_handler();
    }
}
}

extern "C" int main(void)
{
    HAL_Init();
    configure_system_clock();
    rurp_timing_init();

    setup();

    for (;;)
    {
        loop();
    }
}
