cmake_minimum_required(VERSION 3.20)

set(
    CMAKE_TOOLCHAIN_FILE
    "${CMAKE_CURRENT_LIST_DIR}/cmake/arm-none-eabi.cmake"
    CACHE FILEPATH ""
)

project(firestarter_py32f071 C CXX ASM)

set(TARGET_NAME firestarter-py32f071.elf)
set(REPOSITORY_ROOT "${CMAKE_CURRENT_LIST_DIR}/../..")
set(LINKER_SCRIPT "${CMAKE_CURRENT_LIST_DIR}/linker/PY32F071xB_FLASH.ld")

add_executable(
    ${TARGET_NAME}
    startup/startup_py32f071.s
    src/main.cpp
)

target_include_directories(
    ${TARGET_NAME}
    PRIVATE
        "${REPOSITORY_ROOT}/include"
)

target_compile_definitions(
    ${TARGET_NAME}
    PRIVATE
        RURP_PLATFORM_PY32F071=1
        RURP_BOARD_NAME="py32f071"
)

target_compile_features(${TARGET_NAME} PRIVATE cxx_std_17)

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
