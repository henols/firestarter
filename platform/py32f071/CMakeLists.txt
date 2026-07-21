cmake_minimum_required(VERSION 3.20)

set(
    CMAKE_TOOLCHAIN_FILE
    "${CMAKE_CURRENT_LIST_DIR}/cmake/arm-none-eabi.cmake"
    CACHE FILEPATH ""
)

project(firestarter_py32f071 C CXX ASM)

include(FetchContent)

FetchContent_Declare(
    py32f071_sdk
    GIT_REPOSITORY https://github.com/OpenPuya/PY32F071_Firmware.git
    GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2
    GIT_SHALLOW FALSE
)

FetchContent_GetProperties(py32f071_sdk)
if(NOT py32f071_sdk_POPULATED)
    FetchContent_Populate(py32f071_sdk)
endif()

set(TARGET_NAME firestarter-py32f071.elf)
set(REPOSITORY_ROOT "${CMAKE_CURRENT_LIST_DIR}/../..")
set(PY32_SDK_ROOT "${py32f071_sdk_SOURCE_DIR}")
set(LINKER_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/linker/PY32F071xB_FLASH.ld")

set(FIRESTARTER_COMMON_SOURCES
    "${REPOSITORY_ROOT}/src/firestarter.cpp"
    "${REPOSITORY_ROOT}/src/eprom_operations.cpp"
    "${REPOSITORY_ROOT}/src/hardware_operations.cpp"
    "${REPOSITORY_ROOT}/src/operation_utils.cpp"
    "${REPOSITORY_ROOT}/src/json_parser.c"
    "${REPOSITORY_ROOT}/src/boards/rurp_serial_utils.cpp"
    "${REPOSITORY_ROOT}/src/proms/memory.cpp"
    "${REPOSITORY_ROOT}/src/proms/eprom.cpp"
    "${REPOSITORY_ROOT}/src/proms/eeprom_28c.cpp"
    "${REPOSITORY_ROOT}/src/proms/flash_type_3.cpp"
    "${REPOSITORY_ROOT}/src/proms/flash_type_4.cpp"
    "${REPOSITORY_ROOT}/src/proms/flash_intel.cpp"
    "${REPOSITORY_ROOT}/src/proms/flash_utils.cpp"
    "${REPOSITORY_ROOT}/src/proms/sram.cpp"
    "${REPOSITORY_ROOT}/src/proms/not_implemented.cpp"
    "${REPOSITORY_ROOT}/lib/jsmn/src/jsmn.c"
)

set(PY32_PLATFORM_SOURCES
    startup/startup_py32f071.s
    src/main.cpp
    src/platform_compat.cpp
    src/timing.cpp
    src/usb_cdc.c
    src/py32f071_rurp_shield.cpp
    src/config.cpp
)

set(PY32_SDK_SOURCES
    "${PY32_SDK_ROOT}/Templates/PY32F071xx_Templates/Src/system_py32f071.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_rcc.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_rcc_ex.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_gpio.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_cortex.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_pwr.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_adc.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_adc_ex.c"
    "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_tim.c"
    "${PY32_SDK_ROOT}/Middlewares/Third_Party/CherryUSB/core/usbd_core.c"
    "${PY32_SDK_ROOT}/Middlewares/Third_Party/CherryUSB/class/cdc/usbd_cdc.c"
    "${PY32_SDK_ROOT}/Middlewares/Third_Party/CherryUSB/port/usb_dc_py32.c"
)

add_executable(
    ${TARGET_NAME}
    ${FIRESTARTER_COMMON_SOURCES}
    ${PY32_PLATFORM_SOURCES}
    ${PY32_SDK_SOURCES}
)

target_include_directories(
    ${TARGET_NAME}
    PRIVATE
        "${CMAKE_CURRENT_LIST_DIR}/include"
        "${REPOSITORY_ROOT}/include"
        "${REPOSITORY_ROOT}/lib/jsmn/src"
        "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Inc"
        "${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Inc/Legacy"
        "${PY32_SDK_ROOT}/Drivers/CMSIS/Device/PY32F071/Include"
        "${PY32_SDK_ROOT}/Drivers/CMSIS/Include"
        "${PY32_SDK_ROOT}/Middlewares/Third_Party/CherryUSB/port"
        "${PY32_SDK_ROOT}/Middlewares/Third_Party/CherryUSB/core"
        "${PY32_SDK_ROOT}/Middlewares/Third_Party/CherryUSB/common"
        "${PY32_SDK_ROOT}/Middlewares/Third_Party/CherryUSB/class/cdc"
)

target_compile_definitions(
    ${TARGET_NAME}
    PRIVATE
        USE_HAL_DRIVER
        PY32F071xB
        RURP_PLATFORM_PY32F071=1
        RURP_BOARD_NAME="py32f071"
        MONITOR_SPEED=250000
        DATA_BUFFER_SIZE=512
)

target_compile_features(${TARGET_NAME} PRIVATE c_std_11 cxx_std_17)

target_compile_options(
    ${TARGET_NAME}
    PRIVATE
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

target_link_options(
    ${TARGET_NAME}
    PRIVATE
        -mcpu=cortex-m0plus
        -mthumb
        "-T${LINKER_SCRIPT}"
        -nostartfiles
        --specs=nano.specs
        --specs=nosys.specs
        -Wl,--gc-sections
        "-Wl,-Map=${CMAKE_CURRENT_BINARY_DIR}/firestarter-py32f071.map,--cref"
)

target_link_libraries(${TARGET_NAME} PRIVATE m)

set_target_properties(
    ${TARGET_NAME}
    PROPERTIES
        LINK_DEPENDS "${LINKER_SCRIPT}"
)

set(BIN_FILE "${CMAKE_CURRENT_BINARY_DIR}/firestarter-py32f071.bin")
set(HEX_FILE "${CMAKE_CURRENT_BINARY_DIR}/firestarter-py32f071.hex")
set(SHA_FILE "${CMAKE_CURRENT_BINARY_DIR}/firestarter-py32f071.sha256")

add_custom_command(
    TARGET ${TARGET_NAME}
    POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:${TARGET_NAME}> "${BIN_FILE}"
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:${TARGET_NAME}> "${HEX_FILE}"
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:${TARGET_NAME}>
    COMMAND
        ${CMAKE_COMMAND}
        "-DOUTPUT_FILE=${SHA_FILE}"
        "-DINPUT_FILES=$<TARGET_FILE:${TARGET_NAME}>;${BIN_FILE};${HEX_FILE}"
        -P "${CMAKE_CURRENT_LIST_DIR}/cmake/write_checksums.cmake"
    BYPRODUCTS
        "${BIN_FILE}"
        "${HEX_FILE}"
        "${SHA_FILE}"
    VERBATIM
)
