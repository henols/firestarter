# PROGMEM Parameter Tables

Const per-protocol data lives in PROGMEM, keyed by protocol, read with `pgm_read_*`.

```cpp
static const uint8_t EPROM_PARAM_KEYS[] PROGMEM = { 0x07, 0x08, 0x0B };
static const eprom_params_t EPROM_PARAMS[] PROGMEM = { ... };  // parallel to KEYS

const eprom_params_t* eprom_params_for(uint32_t protocol) {
    for (size_t i = 0; i < sizeof(EPROM_PARAM_KEYS); i++)
        if (pgm_read_byte(&EPROM_PARAM_KEYS[i]) == protocol) return &EPROM_PARAMS[i];
    return NULL;
}

uint32_t cap = pgm_read_dword(&row->energy_cap_us);   // never row->energy_cap_us
```

Why: AVR RAM is scarcer than flash. A switch on protocol would be a second dispatch key.

- Read every field with `pgm_read_byte/word/dword`. A direct `row->field` compiles, passes native tests, and returns RAM garbage on AVR.
- Accessor is a linear scan, never a `switch`. No match returns NULL.
- Table headers include only `<stdint.h>` and `rurp_platform_compat.h`. Never `Arduino.h`: it adds macro-redefinition warnings on native, and the warning watermark has zero headroom.
- Order struct fields largest-first and keep the `static_assert(sizeof(...))`. avr-gcc aligns to 1 byte; a 64-bit host does not.
