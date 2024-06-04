#include "memory.h"
#include <stdio.h>
#include "firestarter.h"
#include "chip.h"
#include "rurp_shield.h"

void memory_erase(firestarter_handle_t* handle);
void memory_write_data(firestarter_handle_t* handle);
uint16_t memory_get_chip_id(firestarter_handle_t* handle);

int configure_memory(firestarter_handle_t* handle) {
    handle->firestarter_write_data = memory_write_data;
    return 1;
}

uint16_t memory_get_chip_id(firestarter_handle_t* handle) {
    handle->firestarter_set_control_register(handle, REG_DISABLE, 1);
    delay(100);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE | VPE_TO_VPP, 1);
    delay(100);
    set_control_pin(ROM_CE, 0);
    uint16_t chip_id = handle->firestarter_get_data(handle, 0x0000) << 8;
    chip_id |= (handle->firestarter_get_data(handle, 0x0001));
    set_control_pin(ROM_CE, 1);
    handle->firestarter_set_control_register(handle, REG_DISABLE | A9_VPP_ENABLE | VPE_TO_VPP, 0);
    return chip_id;
}

void memory_erase(firestarter_handle_t* handle) {
    handle->firestarter_set_address(handle, 0x0000);
    handle->firestarter_set_control_register(handle, REG_DISABLE, 1);
    delay(100);
    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE | VPE_ENABLE, 1);
    delay(500);
    set_control_pin(ROM_CE, 0);
    delayMicroseconds(handle->pulse_delay);
    set_control_pin(ROM_CE, 1);

    handle->firestarter_set_control_register(handle, A9_VPP_ENABLE | REG_DISABLE | VPE_ENABLE, 0);
}

void memory_write_data(firestarter_handle_t* handle) {
    if (handle->init) {
        handle->init = 0;
        if (handle->has_chip_id) {
            uint16_t chip_id = memory_get_chip_id(handle);
            if (chip_id != handle->chip_id) {
                handle->response_code = RESPONSE_CODE_ERROR;
                sprintf(handle->response_msg, "Chip ID %u does not match %u", chip_id, handle->chip_id);
                return;
            }
        }
        if (handle->can_erase) {
            memory_erase(handle);
            set_control_pin(ROM_CE, 0);
            for (int i = 0; i < handle->mem_size; i++) {
                if (handle->firestarter_get_data(handle, i) != 0xFF) {
                    handle->response_code = RESPONSE_CODE_ERROR;
                    sprintf(handle->response_msg, "Failed to erase memory, at 0x%x", i);
                    return;
                }
            }
            set_control_pin(ROM_CE, 1);
        }
    }
    handle->firestarter_set_control_register(handle, VPE_TO_VPP| REG_DISABLE, 1);
    delay(50);
    handle->firestarter_set_control_register(handle,  VPE_ENABLE, 1);

    for (int i = 0; i < handle->data_buffer_size; i++)
    {
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
    }
    handle->firestarter_set_control_register(handle, REG_DISABLE |VPE_TO_VPP| VPE_ENABLE, 0);

    for (int i = 0; i < handle->data_buffer_size; i++)
    {
        if(handle->firestarter_get_data(handle, handle->address + i) != handle->data_buffer[i]){
            handle->response_code = RESPONSE_CODE_ERROR;
            sprintf(handle->response_msg, "Value at 0x%x don't match", handle->address + i);
            return;
        }
    }

    handle->response_code = RESPONSE_CODE_OK;

}

