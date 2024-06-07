#include "chip.h"
#include "config.h"
#include "eprom.h"
#include "sram.h"
#include "rurp_shield.h"

#define TYPE_EPROM 1
#define TYPE_SRAM 4


int configure_chip(firestarter_handle_t* handle)
{
    handle->firestarter_read_data = chip_read_data;
    handle->firestarter_write_data = chip_write_data;
    handle->firestarter_get_data = chip_get_data;
    handle->firestarter_set_data = chip_set_data;
    // handle->firestarter_write_to_register = chip_write_to_register;
    handle->firestarter_set_address = chip_set_address;

    handle->firestarter_set_control_register = chip_set_control_register;
    handle->firestarter_get_control_register = chip_get_control_register;

    if (handle->mem_type == TYPE_EPROM)
    {
        return configure_eprom(handle);
    }
    else if (handle->mem_type == TYPE_SRAM)
    {
        return configure_sram(handle);
    }
    return 0;
}

void chip_set_control_register(firestarter_handle_t* handle, uint8_t bit, bool state)
{
    byte controle_register = read_from_register(CONTROL_REGISTER);
    uint8_t data = state ? controle_register | (bit) : controle_register & ~(bit);
    write_to_register(CONTROL_REGISTER, data);
}

bool chip_get_control_register(firestarter_handle_t* handle, uint8_t bit)
{
    byte controle_register = read_from_register(CONTROL_REGISTER);
    return controle_register & bit;
}

#ifdef CHIP_REMAP_ADDRESS_BUS
uint32_t remap_address_bus(const bus_config_t* config, uint32_t address, uint8_t rw) {
    uint32_t reorg_address = 0;
    for (int i = 0; i < 19 && config->address_lines[i] != 0xFF; i++) {
        if (address & (1 << i)) {
            reorg_address |= (1 << config->address_lines[i]);
        }
    }
    if (config->rw_line != 0xFF) {
        reorg_address |= rw << config->rw_line;
    }
    return reorg_address;
}
#endif
void chip_set_address(firestarter_handle_t* handle, uint32_t address)
{

    byte lsb = address & 0xFF;
    byte msb = ((address >> 8) & 0xFF);
    write_to_register(LEAST_SIGNIFICANT_BYTE, lsb);
    write_to_register(MOST_SIGNIFICANT_BYTE, msb);
    // uint8_t top_address = (address >> 16) & 0xFF;
    // handle->firestarter_set_control_register(handle, A16, top_address & 0x01);
    // handle->firestarter_set_control_register(handle, A17, (top_address >> 1) & 0x01);
    // handle->firestarter_set_control_register(handle, A18, (top_address >> 2) & 0x01);
}

void chip_read_data(firestarter_handle_t* handle)
{
    int buf_size = DATA_BUFFER_SIZE;
    for (int i = 0; i < buf_size; i++)
    {
        handle->data_buffer[i] = handle->firestarter_get_data(handle, handle->address + i);
    }
}

uint8_t chip_get_data(firestarter_handle_t* handle, uint32_t address)
{

#ifdef CHIP_REMAP_ADDRESS_BUS
    if (handle->bus_config.address_lines[0] != 0xff || handle->bus_config.rw_line != 0xff) {
        address = remap_address_bus(&handle->bus_config, address, READ_FLAG);
    }
#endif

    handle->firestarter_set_address(handle, address);
    set_data_as_input();

    set_control_pin(CHIP_ENABLE | OUTPUT_ENABLE, 0);
    delayMicroseconds(2);
    uint8_t data = read_data_buffer();
    set_data_as_output();
    set_control_pin(CHIP_ENABLE | OUTPUT_ENABLE, 1);
    delayMicroseconds(1);

    return data;
}


void chip_write_data(firestarter_handle_t* handle) {

    for (int i = 0; i < DATA_BUFFER_SIZE; i++)
    {
        handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);
    }
    handle->response_code = RESPONSE_CODE_OK;
}

void chip_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
#ifdef CHIP_REMAP_ADDRESS_BUS
    if (handle->bus_config.address_lines[0] != 0xff || handle->bus_config.rw_line != 0xff) {
        address = remap_address_bus(&handle->bus_config, address, WRITE_FLAG);
    }
#endif

    handle->firestarter_set_address(handle, address);
    write_data_buffer(data);
    set_control_pin(CHIP_ENABLE, 0);
    delayMicroseconds(handle->pulse_delay);
    set_control_pin(CHIP_ENABLE, 1);
    delayMicroseconds(1);

}
