#include <stdint.h>

volatile uint32_t py32f071_toolchain_smoke = 0xF071B001u;

int main(void)
{
    for (;;) {
        __asm volatile ("nop");
    }
}
