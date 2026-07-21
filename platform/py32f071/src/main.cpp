#include <cstdint>

#include "rurp_platform_compat.h"

namespace {
volatile std::uint32_t py32f071_toolchain_heartbeat = 0;
}

extern "C" int main() {
    for (;;) {
        ++py32f071_toolchain_heartbeat;
        __asm volatile("nop");
    }
}
