#ifndef RURP_SHIELD_H
#define RURP_SHIELD_H

#include <stdint.h>

#define RLSB_LE  0x01
#define RMSB_LE  0x02
#define ROM_OE  0x04
#define CTRL_LE 0x08
#define USRBTN  0x10
#define ROM_CE  0x20

// CONTROLE REGISTER
#define VPE_TO_VPP 0x01
#define A9_VPP_ENABLE 0x02
#define VPE_ENABLE 0x04
#define P1_VPP_ENABLE 0x08
#define RW 0x40
#define REG_DISABLE 0x80

#define A16 VPE_TO_VPP
#define A17 0x10
#define A18 0x20

void rurp_setup();

void set_data_as_output();
void set_data_as_input();

void set_control_pin(uint8_t pin, uint8_t state);

void write_to_register(uint8_t reg, uint8_t data);
uint8_t read_from_register(uint8_t reg);

void write_data_buffer(uint8_t data);
uint8_t read_data_buffer();

float read_voltage();
float get_voltage_average();

#endif // RURP_SHIELD_H