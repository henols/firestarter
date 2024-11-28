#ifndef FLASH_UTIL_H
#define FLASH_UTIL_H
#ifdef __cplusplus
extern "C" {
#endif
#include "firestarter.h"

typedef struct byte_flip {
    uint32_t address;
    uint8_t byte;
} byte_flip_t;

void flash_byte_flipping(firestarter_handle_t* handle, byte_flip_t* byte_flips, size_t size);
void flash_verify_operation(firestarter_handle_t* handle, uint8_t expected_data);
uint8_t flash_data_poll();

#ifdef __cplusplus
}
#endif

#endif // FLASH_UTIL_H