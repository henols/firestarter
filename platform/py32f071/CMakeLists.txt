cmake_minimum_required(VERSION 3.20)

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/cmake/arm-none-eabi.cmake" CACHE FILEPATH "")
project(firestarter_py32f071 C ASM)

set(TARGET firestarter-py32f071)
set(LINKER_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/linker/PY32F071xB_FLASH.ld")

add_executable(${TARGET}.elf
    startup/startup_py32f071.s
    src/main.c
)

target_compile_options(${TARGET}.elf PRIVATE
    -mcpu=cortex-m0plus
    -mthumb
    -ffunction-sections
    -fdata-sections
    -fno-common
    -Wall
    -Wextra
    -Werror
    -Os
)

target_link_options(${TARGET}.elf PRIVATE
    -mcpu=cortex-m0plus
    -mthumb
    -T${LINKER_SCRIPT}
    -nost