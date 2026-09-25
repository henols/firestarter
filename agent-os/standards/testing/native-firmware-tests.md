# Native Firmware Tests

Unity suites live in `test/native/avr/<suite>/` and run on the host with `platform = native`.

To add a suite, update both lists in `[native_base]` in `platformio.ini`:

```ini
test_filter = ... native/avr/<suite>
shared_build_flags = ... -I test/native/avr/<suite>
```

A suite that is not in `test_filter` never runs.

```bash
pio test -e native && pio test -e native_nodevtools   # run both; CI runs `native` on PRs only
```

Harness blind spots:
- The recording stubs (`test/native/avr/_shared/host_stubs_common.inc`) log every register write. Real `rurp_write_to_register` skips unchanged values. Do not count register writes.
- Time is fake. Most suites mock `millis()` through ArduinoFake to always return 0, and `delay()` records nothing. Do not assert timing.

Golden traces run the happy path (matching chip ID, VPP in window). For every branch, add explicit tests: chip-ID mismatch, each WARNING/ERROR fork, VPP out of window, poll timeout.
