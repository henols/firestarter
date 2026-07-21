if(NOT DEFINED OUTPUT_FILE)
    message(FATAL_ERROR "OUTPUT_FILE is required")
endif()

if(NOT DEFINED INPUT_FILES)
    message(FATAL_ERROR "INPUT_FILES is required")
endif()

file(WRITE "${OUTPUT_FILE}" "")

foreach(input_file IN LISTS INPUT_FILES)
    if(NOT EXISTS "${input_file}")
        message(FATAL_ERROR "Cannot checksum missing file: ${input_file}")
    endif()

    file(SHA256 "${input_file}" checksum)
    get_filename_component(filename "${input_file}" NAME)
    file(APPEND "${OUTPUT_FILE}" "${checksum}  ${filename}\n")
endforeach()
