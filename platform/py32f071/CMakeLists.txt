cmake_minimum_required(VERSION 3.20)

set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/cmake/arm-none-eabi.cmake" CACHE FILEPATH "")
project(firestarter_py32f071 C CXX ASM)

set(TARGET firestarter-py32f071)
set(REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../..")
set(LINKER_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/linker/PY32F071xB_FLASH.ld")

# The vendored JSMN header is configured declaration-only. Generate one private
# implementation unit for this native target without altering the shared vendor file.
file(READ "${REPO_ROOT}/lib/jsmn/src/jsmn.h" JSMN_IMPLEMENTATION_TEXT)
string(REPLACE "#define JSMN_HEADER" "/* JSMN implementation enabled */"
       JSMN_IMPLEMENTATION_TEXT "${JSMN_IMPLEMENTATION_TEXT}")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/jsmn_impl.c" "${JSMN_IMPLEMENTATION_TEXT}")

set(PY32_BACKEND_SOURCES
    startup/startup_py32f071.s
    src/main.c
    src/board.c
    src/gpio.c
    src/timing.c
    src/analog.c
    src/vpp_target.c
    src/usb.c
    src/storage.c
    src/platform_compat.cpp
    src/firestarter_entry.cpp
    src/config.cpp
    src/registers.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/jsmn_impl.c
)

set(FIRESTARTER_COMMON_SOURCES
    ${REPO_ROOT}/src/firestarter.cpp
    ${REPO_ROOT}/src/eprom_operations.cpp
    ${REPO_ROOT}/src/hardware_operations.cpp
    ${REPO_ROOT}/src/operation_utils.cpp
    ${REPO_ROOT}/src/json_parser.c
    ${REPO_ROOT}/src/boards/rurp_serial_utils.cpp
    ${REPO_ROOT}/src/proms/memory.cpp
    ${REPO_ROOT}/src/proms/eprom.cpp
    ${REPO_ROOT}/src/proms/eeprom_28c.cpp
    ${REPO_ROOT}/src/proms/flash_type_3.cpp
    ${REPO_ROOT}/src/proms/flash_type_4.cpp
    ${REPO_ROOT}/src/proms/flash_intel.cpp
    ${REPO_ROOT}/src/proms/flash_utils.cpp
    ${REPO_ROOT}/src/proms/sram.cpp
    ${REPO_ROOT}/src/proms/not_implemented.cpp
)

add_executable(${TARGET}.elf ${PY32_BACKEND_SOURCES} ${FIRESTARTER_COMMON_SOURCES})

target_include_directories(${TARGET}.elf PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/include
    ${REPO_ROOT}/include
    ${REPO_ROOT}/lib/jsmn/src
)

target_compile_definitions(${TARGET}.elf PRIVATE
    PY32F071xB
    RURP_PLATFORM_PY32F071=1
    RURP_HAS_VPP_DAC=1
    RURP_BOARD_NAME="py32f071"
    HARDWARE_REVISION
    DATA_BUFFER_SIZE=1024
    MONITOR_SPEED=250000
)

target_compile_features(${TARGET}.elf PRIVATE cxx_std_17)

target_compile_options(${TARGET}.elf PRIVATE
    -mcpu=cortex-m0plus
    -mthumb
    -ffunction-sections
    -fdata-sections
    -fno-common
    -Wall
    -Wextra
    -Os
    $<$<COMPILE_LANGUAGE:CXX>:-fno-exceptions>
    $<$<COMPILE_LANGUAGE:CXX>:-fno-rtti>
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

target_link_libraries(${TARGET}.elf PRIVATE m)
set_target_properties(${TARGET}.elf PROPERTIES LINK_DEPENDS "${LINKER_SCRIPT}")

add_custom_command(TARGET ${TARGET}.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${TARGET}.elf> ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.bin
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${TARGET}.elf> ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.hex
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${TARGET}.elf>
    COMMAND ${CMAKE_COMMAND} -E sha256sum
        $<TARGET_FILE:${TARGET}.elf>
        ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.bin
        ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.hex
        > ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.sha256
    BYPRODUCTS
        ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.bin
        ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.hex
        ${CMAKE_CURRENT_BINARY_DIR}/${TARGET}.sha256
    COMMENT "Generating PY32F071 BIN, HEX and checksums"
)
