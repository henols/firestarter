# Chip Command Sequences

Every unlock, SDP or erase sequence is a named `byte_flip_t` table that cites its vendor document.

```cpp
// AT28C SDP enable [Atmel doc0270 rev 0270L-PEEPR-2/09 sec 19 note 2]
extern const byte_flip_t EEPROM_SDP_ENABLE[3];   // prior extern: gives external linkage
const byte_flip_t EEPROM_SDP_ENABLE[3] = {
    {0x5555, 0xAA},
    {0x2AAA, 0x55},
    {0x5555, 0xA0},
};
```

- Never dedupe byte-identical tables. `EEPROM_SDP_ENABLE` equals the `FLASH_ENABLE_WRITE` prefix. The array name is the only thing that separates "lock" from "write prefix".
- Declare `extern` before the definition. In C++ a namespace-scope const array has internal linkage without it, and the native guard must read the production array.
- The inline writes in `eeprom28c_erase_execute` are legacy. Do not copy them.
