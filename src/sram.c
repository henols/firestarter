#include "sram.h"
#include "firestarter.h"
#include "chip.h"
#include "rurp_shield.h"

int configure_sram(firestarter_handle_t *handle) {
    // Configure memory
    // handle->firestarter_read_data = chip_read_data;
    // handle->firestarter_write_data = chip_write_data;
    return 1;
}
// void chip_read_data(firestarter_handle_t* handle)
// {
//     int buf_size = DATA_BUFFER_SIZE;

//     set_control_pin(OUTPUT_ENABLE, 0);

//     for (int i = 0; i < buf_size; i++)
//     {
//         handle->data_buffer[i] = handle->firestarter_get_data(handle, handle->address + i);
//     }
//     set_control_pin(OUTPUT_ENABLE, 1);
// }

// uint8_t chip_get_data(firestarter_handle_t* handle, uint32_t address)
// {
//     uint32_t reorg_address= address;
//     if (handle->bus_config.address_lines[0] != 0xff || handle->bus_config.rw_line != 0xff) {
//         reorg_address = map_address_to_bus(&handle->bus_config, address, READ_FLAG);
//     }


//     handle->firestarter_set_address(handle, reorg_address);
//     set_data_as_input();

//     set_control_pin(CHIP_ENABLE, 0);
//     delayMicroseconds(2);
//     uint8_t data = read_data_buffer();
//     set_control_pin(CHIP_ENABLE, 1);
//     set_data_as_output();
//     delayMicroseconds(1);

//     return data;
// }
