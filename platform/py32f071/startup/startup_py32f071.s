.syntax unified
.cpu cortex-m0plus
.fpu softvfp
.thumb

.global g_pfnVectors
.global Reset_Handler
.global Default_Handler

.section .text.Reset_Handler,"ax",%progbits
.type Reset_Handler, %function
Reset_Handler:
  ldr r0, =_sidata
  ldr r1, =_sdata
  ldr r2, =_edata
1:
  cmp r1, r2
  bcs 3f
  ldr r3, [r0]
  str r3, [r1]
  adds r0, #4
  adds r1, #4
  b 1b
3:
  ldr r0, =_sbss
  ldr r1, =_ebss
  movs r2, #0
4:
  cmp r0, r1
  bcs 6f
  str r2, [r0]
  adds r0, #4
  b 4b
6:
  bl main
7:
  b 7b
.size Reset_Handler, .-Reset_Handler

.section .text.Default_Handler,"ax",%progbits
.type Default_Handler, %function
Default_Handler:
  b Default_Handler
.size Default_Handler, .-Default_Handler

.macro WEAK_HANDLER name
  .weak \name
  .thumb_set \name, Default_Handler
.endm

WEAK_HANDLER NMI_Handler
WEAK_HANDLER HardFault_Handler
WEAK_HANDLER SVC_Handler
WEAK_HANDLER PendSV_Handler
WEAK_HANDLER SysTick_Handler
WEAK_HANDLER WWDG_IRQHandler
WEAK_HANDLER PVD_IRQHandler
WEAK_HANDLER RTC_IRQHandler
WEAK_HANDLER FLASH_IRQHandler
WEAK_HANDLER RCC_CTC_IRQHandler
WEAK_HANDLER EXTI0_1_IRQHandler
WEAK_HANDLER EXTI2_3_IRQHandler
WEAK_HANDLER EXTI4_15_IRQHandler
WEAK_HANDLER LCD_IRQHandler
WEAK_HANDLER DMA1_Channel1_IRQHandler
WEAK_HANDLER DMA1_Channel2_3_IRQHandler
WEAK_HANDLER DMA1_Channel4_5_6_7_IRQHandler
WEAK_HANDLER ADC_COMP_IRQHandler
WEAK_HANDLER TIM1_BRK_UP_TRG_COM_IRQHandler
WEAK_HANDLER TIM1_CC_IRQHandler
WEAK_HANDLER TIM2_IRQHandler
WEAK_HANDLER TIM3_IRQHandler
WEAK_HANDLER TIM6_LPTIM1_DAC_IRQHandler
WEAK_HANDLER TIM7_IRQHandler
WEAK_HANDLER TIM14_IRQHandler
WEAK_HANDLER TIM15_IRQHandler
WEAK_HANDLER TIM16_IRQHandler
WEAK_HANDLER TIM17_IRQHandler
WEAK_HANDLER I2C1_IRQHandler
WEAK_HANDLER I2C2_IRQHandler
WEAK_HANDLER SPI1_IRQHandler
WEAK_HANDLER SPI2_IRQHandler
WEAK_HANDLER USART1_IRQHandler
WEAK_HANDLER USART2_IRQHandler
WEAK_HANDLER USART3_IRQHandler
WEAK_HANDLER USB_IRQHandler

.section .isr_vector,"a",%progbits
.type g_pfnVectors, %object
g_pfnVectors:
  .word _estack
  .word Reset_Handler
  .word NMI_Handler
  .word HardFault_Handler
  .word 0
  .word 0
  .word 0
  .word 0
  .word 0
  .word 0
  .word 0
  .word SVC_Handler
  .word 0
  .word 0
  .word PendSV_Handler
  .word SysTick_Handler
  .word WWDG_IRQHandler
  .word PVD_IRQHandler
  .word RTC_IRQHandler
  .word FLASH_IRQHandler
  .word RCC_CTC_IRQHandler
  .word EXTI0_1_IRQHandler
  .word EXTI2_3_IRQHandler
  .word EXTI4_15_IRQHandler
  .word LCD_IRQHandler
  .word DMA1_Channel1_IRQHandler
  .word DMA1_Channel2_3_IRQHandler
  .word DMA1_Channel4_5_6_7_IRQHandler
  .word ADC_COMP_IRQHandler
  .word TIM1_BRK_UP_TRG_COM_IRQHandler
  .word TIM1_CC_IRQHandler
  .word TIM2_IRQHandler
  .word TIM3_IRQHandler
  .word TIM6_LPTIM1_DAC_IRQHandler
  .word TIM7_IRQHandler
  .word TIM14_IRQHandler
  .word TIM15_IRQHandler
  .word TIM16_IRQHandler
  .word TIM17_IRQHandler
  .word I2C1_IRQHandler
  .word I2C2_IRQHandler
  .word SPI1_IRQHandler
  .word SPI2_IRQHandler
  .word USART1_IRQHandler
  .word USART2_IRQHandler
  .word USART3_IRQHandler
  .word 0
  .word USB_IRQHandler
.size g_pfnVectors, .-g_pfnVectors
