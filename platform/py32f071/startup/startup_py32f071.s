.syntax unified
.cpu cortex-m0plus
.thumb

.global g_pfnVectors
.global Reset_Handler

.word _sidata
.word _sdata
.word _edata
.word _sbss
.word _ebss

.section .text.Reset_Handler
.type Reset_Handler, %function
Reset_Handler:
  ldr r0, =_sidata
  ldr r1, =_sdata
  ldr r2, =_edata
1:
  cmp r1, r2
  bcc 2f
  b 3f
2:
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
  bcc 5f
  b 6f
5:
  str r2, [r0]
  adds r0, #4
  b 4b
6:
  bl main
7:
  b 7b
.size Reset_Handler, .-Reset_Handler

.section .text.Default_Handler,"ax",%progbits
Default_Handler:
  b Default_Handler

.macro WEAK_HANDLER name
  .weak \name
  .thumb_set \name, Default_Handler
.endm

WEAK_HANDLER NMI_Handler
WEAK_HANDLER HardFault_Handler
WEAK_HANDLER SVC_Handler
WEAK_HANDLER PendSV_Handler
WEAK_HANDLER SysTick_Handler

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
  .rept 48
  .word Default_Handler
  .endr
.size g_pfnVectors, .-g_pfnVectors
