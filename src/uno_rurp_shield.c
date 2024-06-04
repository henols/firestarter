#include "rurp_shield.h"
#include <Arduino.h>

#if bourd == uno
#define VALUE_R1 440
#define VALUE_R2 2700
#define V_IN = 23.91
#define V_OUT = 3.312

#define VOLTAGE_MESSURE_PIN A2

#define ARDUINO_VCC 5.01
#define VOLTAGE_SOURCE 12
#define INPUT_RESOLUTION 1023
#define AVERAGE_OF 500

#define REFERENCE_RESELUTION (ARDUINO_VCC / (float)INPUT_RESOLUTION)
#define VOLTAGE_DIVIDER (1 + ((float)VALUE_R2 / (float)VALUE_R1))



uint8_t rlsble;
uint8_t rmsble;
uint8_t controle_register;

void rurp_setup() {
    set_data_as_output();
    DDRB = RLSB_LE | RMSB_LE | CTRL_LE | ROM_OE | ROM_CE | RW;

    PORTB = ROM_OE | ROM_CE;
    rlsble=0xff;
    rmsble=0xff;
    controle_register=0xff;
    write_to_register(RLSB_LE, 0x00);
    write_to_register(RMSB_LE, 0x00);
    write_to_register(CTRL_LE, 0x00);

}

void set_data_as_output(){
    DDRD = 0xff;
}

void set_data_as_input(){
    DDRD = 0x00;
}

void write_to_register(uint8_t reg, uint8_t data)
{

    switch (reg)
    {
    case RLSB_LE:
        if (rlsble == data)
        {
            return;
        }
        rlsble = data;
        break;
    case RMSB_LE:
        if (rmsble == data)
        {
            return;
        }
        rmsble = data;
        break;
    case CTRL_LE:
        if (controle_register == data)
        {
            return;
        }
        controle_register = data;
        break;

    default:
        return;
    }

    PORTD = data;
    PORTB |= reg;
    delayMicroseconds(1);
    PORTB &= ~(reg);
}

uint8_t read_from_register(uint8_t reg)
{
    switch (reg)
    {
    case RLSB_LE:
        return rlsble;
    case RMSB_LE:
        return rmsble;
    case CTRL_LE:
        return controle_register;
    }
    return NULL;
}

void set_control_pin(uint8_t pin, uint8_t state)
{
    if (state)
    {
        PORTB |= pin;
    }
    else
    {
        PORTB &= ~(pin);
    }
}


void write_data_buffer(uint8_t data) {
    PORTD = data;
}

uint8_t read_data_buffer() {
    return PIND;
}

float read_voltage()
{
    return analogRead(VOLTAGE_MESSURE_PIN) * REFERENCE_RESELUTION * VOLTAGE_DIVIDER;
}

float get_voltage_average()
{
    float voltage_average = 0;
    for (int i = 0; i < AVERAGE_OF; i++)
    {
        voltage_average += read_voltage();
    }

    return voltage_average / AVERAGE_OF;
}

#endif
