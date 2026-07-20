cmake_minimum_required(VERSION 3.20)

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/cmake/arm-none-eabi.cmake" CACHE FILEPATH "")
project(firestarter_py32f071 C CXX ASM)

set(TARGET firestarter-py32f071)
set(LINKER_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/linker/PY32F071xB_FLASH.ld")

add_executable(${TARGET}.elf
    startup/startup_py32f071.s
    src/main.c
    src/board.c
    src/gpio.c
    src/timing.c
    src/analog.c
    src/usb.c
    src/storage.c
)

target_include_directories(${TARGET}.elf PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/include
)

target_compile_definitions(${TARGET}.elf PRIVATE
    PY32F071xB
    RURP_PLATFORM_PY32F071=1
    RURP_HAS_VPP_DAC=1
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
    -nostartfiles
    --specs=nano.specs
    --specs=nosys.specs
    -Wl,--gc-sections
    -Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.map,--cref
)

set_target_properties(${TARGET}.elf PROPERTIES
    LINK_DEPENDS "${LINKER_SCRIPT}"
)

add_custom_command(TARGET ${TARGET}.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${TARGET}.elf> ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.bin
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${TARGET}.elf> ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.hex
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${TARGET}.elf>
    BYPRODUCTS
        ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.bin
        ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.hex
    COMMENT "Generating PY32F071 BIN and HEX images"
)
