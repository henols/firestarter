if(NOT DEFINED OUTPUT_FILE)
    message(FATAL_ERROR "OUTPUT_FILE is required")
endif()

if(NOT DEFINED INPUT_FILES_ENCODED)
    message(FATAL_ERROR "INPUT_FILES_ENCODED is required")
endif()

string(REPLACE "|" ";" INPUT_FILES "${INPUT_FILES_ENCODED}")
file(WRITE "${OUTPUT_FILE}" "")

foreach(input_file IN LISTS INPUT_FILES)
    if(NOT EXISTS "${input_file}")
        message(FATAL_ERROR "Cannot checksum missing file: ${input_file}")
    endif()

    file(SHA256 "${input_file}" checksum)
    get_filename_component(filename "${input_file}" NAME)
    file(APPEND "${OUTPUT_FILE}" "${checksum}  ${filename}\n")
endforeach()
