/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include <Arduino.h>
#include "rurp_shield.h"
#include "rurp_pinout.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)


/**
 * @brief Reads the raw ADC value for the internal 1.1V bandgap reference.
 * This provides a basis for calculating the actual VCC, and using the raw
 * value in other calculations preserves precision.
 * @return The raw ADC reading as a long.
 */
long rurp_get_bandgap_adc_reading() {
    // Set the analog reference to the internal 1.1V and select the bandgap channel.
    // The MUX settings are different for Uno and Leonardo.
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#elif defined(ARDUINO_AVR_LEONARDO)
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
#else
#error "Unsupported board"
#endif

    delay(2); // Wait for voltage to stabilize
    ADCSRA |= _BV(ADSC);              // Start conversion
    while (bit_is_set(ADCSRA, ADSC))  // Wait for conversion to complete
        ;

    long result = ADCL;
    result |= ADCH << 8;
    return result;
}

uint16_t rurp_read_vcc_mv() {
    long result = rurp_get_bandgap_adc_reading();
    // Calculate Vcc (supply voltage) in millivolts
    // VCC_mV = (V_bandgap * ADC_resolution * 1000) / ADC_reading
    // VCC_mV = (1.1V * 1024 steps * 1000 mV/V) / ADC_reading = 1126400 / ADC_reading
    if (result == 0) return 0;  // Avoid division by zero
    // Add half of the divisor to the numerator to round the result
    return (1126400L + result / 2) / result;
}

uint16_t rurp_read_voltage_mv() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint32_t r1 = rurp_config->r1;
    uint32_t r2 = rurp_config->r2;

    // Set analog reference to default (VCC) for the measurement
    analogReference(DEFAULT);
    uint32_t voltage_adc_reading = analogRead(PIN_VPP_VOLTAGE_ADC);

    long bandgap_adc_reading = rurp_get_bandgap_adc_reading();
    if (bandgap_adc_reading == 0 || r2 == 0) return 0; // Avoid division by zero

    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)
    //
    // Evaluated entirely in 32-bit by folding the resistor divider into a
    // single scale factor FIRST, instead of forming a 64-bit numerator:
    //
    //     k   = 1100 * (R1 + R2) / R2
    //     Vin = (adc * k + bandgap/2) / bandgap
    //
    // At the shipped calibration (VALUE_R1 270000, VALUE_R2 44000) k is
    // 7850 exactly, so this is BIT-IDENTICAL to the uint64 form it
    // replaces -- adc=1023, bandgap=225 gives 35691 mV either way. Across
    // a sweep of off-nominal calibrations (R2 39k-47k, bandgap 200-250,
    // full ADC range) the worst deviation is 5 mV, and it is
    // ONE-DIRECTIONAL: this form only ever under-reads, never over-reads.
    //
    // The consumers' validation window (eprom.cpp / flash_intel.cpp
    // *_check_vpp) is NOT a symmetric +/-5%: the low edge is -5% relative
    // (-600 mV at 12 V) but the high edge is a FIXED +500 mV absolute. So
    // 5 mV is 1.0% of the tighter 500 mV window and 0.83% of the 600 mV
    // edge. Because this form only ever under-reads, it can never
    // suppress the high-side MSG_ERR_VPP_HIGH -- that fires on an
    // over-read condition. Its only possible behavioural effect is a
    // spurious low-side MSG_WARN_VPP_LOW warning for a true voltage
    // within 5 mV of the -5% edge.
    //
    // WHY: this function was the ONLY user-code caller of the entire
    // soft 64-bit runtime -- 528 B across the full contiguous
    // eleven-symbol blob (438 B across the eight helpers this
    // requirement names by identity, plus three fall-through/internal
    // symbols the named list omits) -- for one 7-line function.
    //
    // Both products are kept inside uint32 by the guards below:
    // 1100*(R1+R2) needs R1+R2 <= 3904515, hence the 3900000 guard; and
    // adc*k needs k <= 4198404 given adc <= 1023, hence the 4194303
    // guard -- 0x3FFFFF, so the comparison compiles to a shift test. An
    // implausible calibration returns 0, exactly as r2 == 0 already does.
    //
    // Coverage ceiling: rurp_read_voltage_mv compiles in no native
    // environment (this TU is outside every [env:native*]'s
    // build_src_filter). So, in exactly these terms: it is proven by a
    // committed host-side numerical oracle over a stated input grid,
    // bound to the shipped C by a source-contract scan; no native and no
    // bench coverage exists.
    //
    // Named residual risk, unmitigated by any artefact of this change:
    // avr-gcc miscompiling the 32-bit multiply/divide. Mitigated only by
    // that being AVR's most-exercised code-generation path, and by this
    // change reducing rather than increasing codegen complexity.
    uint32_t sum = r1 + r2;
    if (sum > 3900000UL) {
        return 0;
    }
    uint32_t k = (1100UL * sum) / r2;
    if (k > 4194303UL) {
        return 0;
    }
    uint32_t bg = (uint32_t)bandgap_adc_reading;
    return (uint16_t)((voltage_adc_reading * k + bg / 2) / bg);
}
#endif