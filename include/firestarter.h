#ifndef FIRESTARTER_H
#define FIRESTARTER_H
#include <Arduino.h>

#define DATA_BUFFER_SIZE 256

#define STATE_IDLE 0
#define STATE_READ 1
#define STATE_WRITE 2
#define STATE_ERASE 3
#define STATE_CHECK_ERASED 4
#define STATE_READ_VPP 5

#define STATE_DONE 99
#define STATE_ERROR 100

#define RESPONSE_CODE_OK 0
#define RESPONSE_CODE_WARNING 1
#define RESPONSE_CODE_ERROR 2

typedef struct bus_config {
	uint8_t address_lines[19]; // Array mapping address lines
	uint8_t rw_line;           // RW line mapping
} bus_config_t;


typedef struct firestarter_handle {
	uint8_t state;
	uint8_t init;
	uint8_t response_code;
	char response_msg[32];
	// const char* name;
	// const char* manufacturer;
	uint8_t mem_type;
	uint32_t protocol;
	uint8_t pins;
	uint32_t mem_size;
	uint32_t address;
	uint32_t pulse_delay;
	uint8_t can_erase;
	uint8_t has_chip_id;
	uint16_t chip_id;
	int data_buffer_size;
	byte* data_buffer;

	bus_config_t bus_config;

	void (*firestarter_init)(struct firestarter_handle*);
	void (*firestarter_set_data)(struct firestarter_handle*, uint32_t, uint8_t);
	void (*firestarter_write_data)(struct firestarter_handle*);
	uint8_t(*firestarter_get_data)(struct firestarter_handle*, uint32_t);
	void(*firestarter_read_data)(struct firestarter_handle*);
	void (*firestarter_check_erased)(struct firestarter_handle*);
	void (*firestarter_set_address)(struct firestarter_handle*, uint32_t);
	void (*firestarter_set_control_register)(struct firestarter_handle*, uint8_t, bool);

} firestarter_handle_t;


#endif // FIRESTARTER_H