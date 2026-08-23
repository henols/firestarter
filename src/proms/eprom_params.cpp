/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 *
 * The const, protocol_id-keyed EPROM parameter table (type declared in
 * eprom_params.h) and its fail-closed linear-scan accessor.
 *
 * No Arduino framework header is included here:
 * src/proms/not_implemented.cpp is the only other translation unit under
 * src/proms/ that omits it, and this file follows that include discipline
 * verbatim so it adds zero macro-redefinition warnings on the native build.
 *
 * protocol_id is the sole lookup key: the accessor below is a
 * linear SCAN over the table, never a switch -- a switch here would be
 * exactly the second dispatch selector this table is designed not to have.
 */
#include "eprom_params.h"

/* Lookup key array, positionally parallel to EPROM_PARAMS below. */
static const uint8_t EPROM_PARAM_KEYS[] PROGMEM = { 0x07, 0x08, 0x0B };

/*
 * Row-value attribution (expanded per-cell in the gate-enforced sidecar at
 * tests/golden/eprom_params_citations.json):
 *
 * 1. 0x07 overprogram_factor = 0 -- operator-decided (2026-08-09); this is
 *    behaviour-preserving, since no protocol applies an overprogram pulse
 *    today, and all three 0x07 datasheets read (Winbond W27C512, ST
 *    M27C512, Microchip 27C512A) specify no overprogram.
 * 2. Named, scoped divergence: the 22 Intel-family 1ms parts on
 *    0x07 genuinely want a 3xN margin pulse. Serving them correctly would
 *    require splitting 0x07 into a second row, which the table's
 *    "no second dispatch key" constraint forbids -- recorded here as a
 *    follow-up candidate, never silently dropped.
 * 3. 0x08 overprogram_factor = 0 is resolved from primary datasheets,
 *    agreeing with PROJECT.md's prose and CONTRADICTING PROJECT.md's own
 *    throughput table -- the contradiction is named here, not smoothed.
 *
 * Per-cell attribution (family, representative part, datasheet revision,
 * or the "no datasheet basis -- reasoned from" form) lives in
 * tests/golden/eprom_params_citations.json.
 */
static const eprom_params_t EPROM_PARAMS[] PROGMEM = {
    /* 0x07 PROTO_EPROM_28PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x08 PROTO_EPROM_32PIN */ { 75000UL, 0UL,     25,  0, VERIFY_PER_PULSE_PLUS_FINAL, VPP_PATH_DROP_RESISTOR },
    /* 0x0B PROTO_EPROM_24PIN */ { 75000UL, 50000UL, 255, 0, VERIFY_PER_PULSE,            VPP_PATH_DIRECT_VPE    },
};

const eprom_params_t* eprom_params_for(uint32_t protocol) {
    for (size_t i = 0; i < sizeof(EPROM_PARAM_KEYS) / sizeof(EPROM_PARAM_KEYS[0]); i++) {
        if ((uint32_t)pgm_read_byte(&EPROM_PARAM_KEYS[i]) == protocol) {
            return &EPROM_PARAMS[i];
        }
    }
    return NULL; /* Fail closed: a null pointer with zero hardware side effects, never &EPROM_PARAMS[0]. */
}
