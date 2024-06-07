#ifndef CHIP_H
#define CHIP_H

#include "firestarter.h"

#define WRITE_FLAG  0
#define READ_FLAG  1

int configure_chip(firestarter_handle_t* handle);

void chip_set_address(firestarter_handle_t* handle, uint32_t address);

void chip_set_control_register(firestarter_handle_t* handle, uint8_t bit, bool state);
bool chip_get_control_register(firestarter_handle_t* handle, uint8_t bit);

void chip_read_data(firestarter_handle_t* handle);

uint8_t chip_get_data(firestarter_handle_t* handle, uint32_t address);

void chip_write_data(firestarter_handle_t* handle);

void chip_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data);

#endif // CHIP_H
