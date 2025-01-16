/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */


#ifdef ARDUINO_AVR_LEONARDO
#include "rurp_shield.h"
#include <Arduino.h>
// #include <EEPROM.h>
#include "rurp_hw_rev_utils.h"
#include "rurp_config_utils.h"


constexpr int INPUT_RESOLUTION = 1023;
constexpr int AVERAGE_OF = 500;



void set_port_b(uint8_t data);
void set_port_d(uint8_t data);

uint8_t get_port_d();
uint8_t get_port_b();

uint8_t lsb_address;
uint8_t msb_address;
register_t control_register;

void rurp_board_setup() {
    rurp_set_data_as_output();
    

    // Set 'PORTB' to input
    // DDRB |= 0xF0;
    // DDRD |= 0x40;
    // DDRC |= 0x80;
    for (int i = 8; i <= 13; i++) {
        pinMode(i, OUTPUT);
    }


    lsb_address = 0xff;
    msb_address = 0xff;
    control_register = 0xff;
    rurp_write_to_register(LEAST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(MOST_SIGNIFICANT_BYTE, 0x00);
    rurp_write_to_register(CONTROL_REGISTER, 0x00);

    Serial.begin(MONITOR_SPEED); // Initialize serial port
    while (!Serial) {
        delayMicroseconds(1);
    }
    Serial.flush();
    delay(1);
}

int rurp_communication_available() {
    return Serial.available();
}
int rurp_communication_read() {
    return Serial.read();
}

size_t rurp_communication_read_bytes(char* buffer, size_t length) {
    return Serial.readBytes(buffer, length);
}

size_t rurp_communication_write(const char* buffer, size_t size) {
    size_t bytes = Serial.write(buffer, size);
    Serial.flush();
    return bytes;
}


void rurp_log(const char* type, const char* msg) {
    Serial.print(type);
    Serial.print(": ");
    Serial.println(msg);
    Serial.flush();
}

void rurp_set_data_as_output() {
    // DDRD |= 0x04 & 0x08 & 0x02 & 0x01 & 0x10 & 0x80;
    // DDRC |= 0x40;
    // DDRE |= 0x40;
    for (int i = 0; i < 8; i++) {
        pinMode(i, OUTPUT);
    }

}

void rurp_set_data_as_input() {
    // DDRD &= ~(0x04 & 0x08 & 0x02 & 0x01 & 0x10 & 0x80);
    // DDRC &= ~0x40;
    // DDRE &= ~0x40;
    for (int i = 0; i < 8; i++) {
        pinMode(i, INPUT);
    }
}


void rurp_write_to_register(uint8_t reg, register_t data) {
    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        if (lsb_address == (uint8_t)data) {
            return;
        }
        lsb_address = data;
        break;
    case MOST_SIGNIFICANT_BYTE:
        if (msb_address == (uint8_t)data) {
            return;
        }
        msb_address = data;
        break;
    case CONTROL_REGISTER:
        if (control_register == data) {
            return;
        }
        control_register = data;
#ifdef HARDWARE_REVISION
        data = rurp_map_ctrl_reg_to_hardware_revision(data);
#endif
        break;
    default:
        return;
    }
    rurp_write_data_buffer(data);
    uint8_t v = get_port_b();
    set_port_b(v | reg);
    set_port_b(v);
}

register_t rurp_read_from_register(uint8_t reg) {
    switch (reg) {
    case LEAST_SIGNIFICANT_BYTE:
        return lsb_address;
    case MOST_SIGNIFICANT_BYTE:
        return msb_address;
    case CONTROL_REGISTER:
        return control_register;
    }
    return 0;
}

void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    uint8_t b = get_port_b();
    if (state) {
        set_port_b(b |= pin);
    }
    else {
        set_port_b(b &= ~(pin));
    }
    // volatile uint8_t* out = portOutputRegister(PORTD);

}


void rurp_write_data_buffer(uint8_t data) {
    rurp_set_data_as_output();
    set_port_d(data);
}

uint8_t rurp_read_data_buffer() {
    return get_port_d();
}

double rurp_read_vcc() {
    // Read 1.1V reference against AVcc
    // Set the analog reference to the internal 1.1V
    // Default is analogReference(DEFAULT) which is connected to the external 5V
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);

    delay(2); // Wait for voltage to stabilize
    ADCSRA |= _BV(ADSC); // Start conversion
    while (bit_is_set(ADCSRA, ADSC)); // Wait for conversion to complete
    ADCSRA |= _BV(ADSC); // Start conversion
    while (bit_is_set(ADCSRA, ADSC)); // measuring
    long result = ADCL;
    result |= ADCH << 8;

    // Calculate Vcc (supply voltage) in millivolts
    // 1100 mV * 1024 ADC steps / ADC reading
    return 1125300L / result / 1000;
}



double rurp_read_voltage() {
    double refRes = rurp_read_vcc() / INPUT_RESOLUTION;

    long r1 = rurp_config.r1;
    long r2 = rurp_config.r2;

    // Correct voltage divider ratio calculation
    double voltageDivider = 1.0 + static_cast<double>(r1) / r2;

    // Read the analog value and convert to voltage
    double vout = analogRead(VOLTAGE_MEASURE_PIN) * refRes;

    // Calculate the input voltage
    return vout * voltageDivider;
}

double rurp_get_voltage_average() {
    double voltage_average = 0;
    for (int i = 0; i < AVERAGE_OF; i++) {
        voltage_average += rurp_read_voltage();
    }

    return voltage_average / AVERAGE_OF;
}

// Function to set Arduino digital pins 8-13 on the ATmega328U4
void set_port_b(uint8_t data) {
    // Map Arduino digital pins 8-13 to ATmega328U4 port bits
    // Arduino Pin    ATmega328U4 Port Pin
    // 8              PB4
    // 9              PB5
    // 10             PB6
    // 11             PB7
    // 12             PD6
    // 13             PC7

    // // Use masks for efficient clearing and setting
    // PORTB = (PORTB & ~((1 << PB4) | //
    //     (1 << PB5) | (1 << PB6) | //
    //     (1 << PB7))) | //
    //     (((data & 0x01) << PB4) |//
    //         ((data & 0x02) << (PB5 - 1)) |//
    //         ((data & 0x04) << (PB6 - 2)) | //
    //         ((data & 0x08) << (PB7 - 3)));

    // PORTD = (PORTD & ~(1 << PD6)) | ((data & 0x10) << (PD6 - 4));
    // PORTC = (PORTC & ~(1 << PC7)) | ((data & 0x20) << (PC7 - 5));
    for (int i = 8; i <= 13; i++) {
        if (data & (1 << (i - 8))) {
            digitalWrite(i, HIGH);
        }
        else {
            digitalWrite(i, LOW);
        }
    }

}

// Function to get the current state of Arduino digital pins 0-7 on the ATmega328U4
uint8_t get_port_d() {
    uint8_t data = 0;
    // data |= PIND & 0x04 ? 0x01 : 0x00;
    // data |= PIND & 0x08 ? 0x02 : 0x00;
    // data |= PIND & 0x02 ? 0x04 : 0x00;
    // data |= PIND & 0x01 ? 0x08 : 0x00;
    // data |= PIND & 0x0F ? 0x10 : 0x00;
    // data |= PINC & 0x40 ? 0x20 : 0x00;
    // data |= PIND & 0x80 ? 0x40 : 0x00;
    // data |= PINE & 0x40 ? 0x80 : 0x00;
    for (int i = 0; i < 8; i++) {
        data |= digitalRead(i) ? 1 << i : 0x00;
    }
    return data;
}

void set_port_d(uint8_t byte) {
    for (int i = 0; i < 8; i++) {
        if (byte & (1 << i)) {
            digitalWrite(i, HIGH);
        }
        else {
            digitalWrite(i, LOW);
        }
    }
    // Clear all relevant bits on PORTD, PORTE, and PORTF
    // PORTD &= ~((1 << PD1) | (1 << PD0) | (1 << PD4) | (1 << PD6) | (1 << PD7));
    // PORTE &= ~(1 << PE6);
    // PORTF &= ~((1 << PF7) | (1 << PF6));

    // // Set the bits based on the input byte
    // PORTD |= ((byte & 0x01) << PD1) |  // Bit 0 -> PD1 (Pin 2)
    //     ((byte & 0x02) >> 1) |    // Bit 1 -> PD0 (Pin 3)
    //     ((byte & 0x04) << 2) |    // Bit 2 -> PD4 (Pin 4)
    //     ((byte & 0x08) << 3) |    // Bit 3 -> PD6 (Pin 5)
    //     ((byte & 0x10) << 3);     // Bit 4 -> PD7 (Pin 6)
    // PORTE |= ((byte & 0x20) >> 5);     // Bit 5 -> PE6 (Pin 7)
    // PORTF |= ((byte & 0x40) >> 1) |    // Bit 6 -> PF7 (Pin 0)
    //     ((byte & 0x80) >> 1);     // Bit 7 -> PF6 (Pin 1)
}

uint8_t get_port_b() {
    uint8_t data = 0;
    // data |= PINB & 0x10 ? 0x01 : 0x00;
    // data |= PINB & 0x20 ? 0x02 : 0x00;
    // data |= PINB & 0x40 ? 0x04 : 0x00;
    // data |= PINB & 0x80 ? 0x08 : 0x00;
    // data |= PIND & 0x40 ? 0x10 : 0x00;
    // data |= PINC & 0x80 ? 0x20 : 0x00;
    for (int i = 8; i <= 13; i++) {
        data |= digitalRead(i) ? 1 << (i - 8) : 0x00;
    }
    return data;
}

#ifdef SERIAL_DEBUG
void debug_buf(const char* msg) {
    rurp_log("DEBUG", msg);
}
#endif

#endif
