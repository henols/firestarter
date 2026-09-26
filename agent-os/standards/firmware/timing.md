# Timing, Polls and Delays

Bound new chip-poll loops by an iteration count, not a `millis()` deadline.

```cpp
// An ITERATION COUNT, not a millis() deadline: native suites mock millis() == 0.
#define AT28C_PAGE_POLL_MAX_READS 2000

for (uint16_t n = 0; n < AT28C_PAGE_POLL_MAX_READS; n++) {
    if ((read(addr) & AT28C_DQ7_MASK) == (expected & AT28C_DQ7_MASK)) return true;
}
return false;
```

- Native suites mock `millis()` to 0, so a deadline loop never ends under test.
- The `millis() < deadline` loops in `flash_intel.cpp` and `flash_utils.cpp` are legacy. Do not copy them.
- Every timing value is a named `#define` with a unit suffix (`_US`, `_MS`) and a citation: `[doc number, rev, section, page]`.
- Say in the comment whether the value is a delay to insert or a maximum to stay under (e.g. `t_BLC`).
- Delays above 16383 µs go through `mem_util_delay_us()`. AVR `delayMicroseconds()` is inaccurate above that.
- An erase pulse has its own constant (`EPROM_ERASE_PULSE_US`). Never reuse `handle->pulse_delay` for it; that is the per-byte program width.
