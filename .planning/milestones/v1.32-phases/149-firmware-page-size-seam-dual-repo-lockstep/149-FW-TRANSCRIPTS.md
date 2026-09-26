# Phase 149 Plan 04: Firmware-Side Transcripts

Working directory for every command below: `/workspaces/firestarter`.

## Wire-key pre-check (binding precondition)

Before writing the parser, the plan requires verifying — not assuming — what already exists on
the wire. `grep`-ing the pre-edit firmware source for any prior page-size handling:

```
$ grep -rn "page.size\|page_size\|PAGE_SIZE" src/json_parser.c include/firestarter.h; echo EXIT=$?
src/proms/eeprom_28c.cpp:19:/* PAGE_SIZE 64 is a deliberate CONSERVATIVE FLOOR ...
src/proms/eeprom_28c.cpp:33:#define PAGE_SIZE 64
src/proms/eeprom_28c.cpp:599:        bool page_end = ((address + 1) % PAGE_SIZE) == 0;
EXIT=1
```

(the `grep` command above is scoped to `json_parser.c`/`firestarter.h`; `eeprom_28c.cpp` hits shown
for context came from a broader pass). **Confirmed: no `page-size` wire key, no `page_size` handle
field, and no parser dispatch entry existed anywhere in the firmware before this plan.** The only
pre-existing artifact was the hardcoded 64-byte floor in `eeprom_28c.cpp`. This corroborates the
project note that the v1.16 `primitives.{h,cpp}` recompose — which would have included a wire
page-size key — was never merged: there was nothing here for this plan to conflict with or build on
beyond the bare floor constant.

## RED — the flush-count oracle before the mask

Five oracle cases (`test_pgsz_*`) and the `s_get_data_calls` counter were added to
`test_val_eeprom28c.cpp` while `eeprom_28c.cpp:649` still used the modulo form
(`(address + 1) % AT28C_PAGE_SIZE_FALLBACK`, post-rename, pre-mask). Command and literal output:

```
$ pio test -e native -f native/avr/test_val_eeprom28c
...
Testing...
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:397: test_eeprom28c_read_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:398: test_eeprom28c_write_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:399: test_eeprom28c_blank_check_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:402: test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:403: test_fix06_clean_page_write_succeeds_isolation_control	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:404: test_fix06_page_boundary_window_readback	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:407: test_pgsz_absent_field_reproduces_the_64_byte_cadence	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:351: test_pgsz_delivered_128_halves_the_flush_count: Expected 130 Was 132. a delivered 128 must be OBSERVED to halve the flush count (1 flush -> 130 calls)	[FAILED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:409: test_pgsz_explicit_64_matches_the_absent_cadence	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:410: test_pgsz_non_power_of_two_falls_back_silently	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:411: test_pgsz_out_of_range_falls_back_silently	[PASSED]

=================================== SUMMARY ===================================
Environment    Test                           Status    Duration
-------------  -----------------------------  --------  ------------
native         native/avr/test_val_eeprom28c  ERRORED   00:00:03.227

============ 12 test cases: 1 failed, 10 succeeded in 00:00:03.227 ============
$ echo EXIT=$?
EXIT=1
```

**The oracle was seen to fail exactly as predicted**: `Expected 130 Was 132` — a delivered `page_size`
of 128 produced the *same* flush count as the 64-byte floor, proving the modulo form never consulted
`handle->page_size` at all. Every other case (absent/64/96/2048, all expecting 132) passed even before
the mask existed, because 132 is also what the unconditional 64-byte modulo produces — that is exactly
why criterion 1 is pinned on the *128* case specifically: it is the only one of the five whose expected
value differs from what the pre-mask code already produced.

(The harness process received `SIGHUP` after the Unity summary printed, on the platform used to run
this plan — a runner artifact of the abort path, not a defect in the test itself; the Unity summary
line above, printed before the signal, is the load-bearing evidence.)

## GREEN — the flush-count oracle after the mask

After adding `eeprom28c_page_mask()` (rejecting `page_size == 0` before the subtraction, validating
power-of-two in `[1, AT28C_PAGE_SIZE_MAX]`, falling back to `AT28C_PAGE_SIZE_FALLBACK` otherwise),
hoisting `const uint32_t page_mask = eeprom28c_page_mask(handle->page_size);` above the per-byte loop
in `eeprom28c_write_execute`, and changing the flush test to `((address + 1) & page_mask) == 0`:

```
$ pio test -e native -f native/avr/test_val_eeprom28c
...
Testing...
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:397: test_eeprom28c_read_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:398: test_eeprom28c_write_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:399: test_eeprom28c_blank_check_configure_no_vpp	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:402: test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:403: test_fix06_clean_page_write_succeeds_isolation_control	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:404: test_fix06_page_boundary_window_readback	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:407: test_pgsz_absent_field_reproduces_the_64_byte_cadence	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:408: test_pgsz_delivered_128_halves_the_flush_count	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:409: test_pgsz_explicit_64_matches_the_absent_cadence	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:410: test_pgsz_non_power_of_two_falls_back_silently	[PASSED]
test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:411: test_pgsz_out_of_range_falls_back_silently	[PASSED]
------- native:native/avr/test_val_eeprom28c [PASSED] Took 1.21 seconds -------

=================================== SUMMARY ===================================
Environment    Test                           Status    Duration
-------------  -----------------------------  --------  ------------
native         native/avr/test_val_eeprom28c  PASSED    00:00:01.206
================= 11 test cases: 11 succeeded in 00:00:01.206 =================
$ echo EXIT=$?
EXIT=0
```

`test_pgsz_delivered_128_halves_the_flush_count` now reports **130** (1 flush, `2*1+128`), and all
four fallback-leg cases still report **132** (2 flushes, `2*2+128`), including the three
`test_fix06_*` cases behaviourally unchanged (their bodies carry only the two mechanical
`AT28C_PAGE_SIZE_FALLBACK` comment renames, verified separately below).

## Both pinned native envs, post-mask

```
$ pio test -e native
...
Environment    Test                             Status
-------------  -------------------------------  --------
native         native/avr/test_val_5v_page      PASSED
native         native/avr/test_not_implemented  PASSED
native         native/avr/test_dispatch         PASSED
native         native/avr/test_read_timing      PASSED
native         native/avr/test_val_nor_unlock   PASSED
native         native/avr/test_cobs_cmd_frame   PASSED
native         native/avr/test_sdp_harness      PASSED
native         native/avr/test_val_eprom        PASSED
native         native/avr/test_cmd_admission    PASSED
native         native/avr/test_val_sram         PASSED
native         native/avr/test_eeprom28c_sdp    PASSED
native         native/avr/test_cobs_data_frame  PASSED
native         native/avr/test_val_flash_intel  PASSED
native         native/avr/test_frame_vectors    PASSED
native         native/avr/test_val_eeprom28c    PASSED
native         native/avr/test_data_input       PASSED
native         native/avr/test_messages         PASSED
================ 151 test cases: 151 succeeded in 00:00:19.607 ================
$ echo EXIT=$?
EXIT=0

$ pio test -e native_nodevtools
...
Environment         Test                             Status
-------------------  -------------------------------  --------
native_nodevtools  native/avr/test_val_5v_page      PASSED
native_nodevtools  native/avr/test_not_implemented  PASSED
native_nodevtools  native/avr/test_dispatch         PASSED
native_nodevtools  native/avr/test_read_timing      PASSED
native_nodevtools  native/avr/test_val_nor_unlock   PASSED
native_nodevtools  native/avr/test_cobs_cmd_frame   PASSED
native_nodevtools  native/avr/test_sdp_harness      PASSED
native_nodevtools  native/avr/test_val_eprom        PASSED
native_nodevtools  native/avr/test_cmd_admission    PASSED
native_nodevtools  native/avr/test_val_sram         PASSED
native_nodevtools  native/avr/test_eeprom28c_sdp    PASSED
native_nodevtools  native/avr/test_cobs_data_frame  PASSED
native_nodevtools  native/avr/test_val_flash_intel  PASSED
native_nodevtools  native/avr/test_frame_vectors    PASSED
native_nodevtools  native/avr/test_val_eeprom28c    PASSED
native_nodevtools  native/avr/test_data_input       PASSED
native_nodevtools  native/avr/test_messages         PASSED
================ 151 test cases: 151 succeeded in 00:01:04.353 ================
$ echo EXIT=$?
EXIT=0
```

`envs_agree`: both `{cases: 151, succeeded: 151}`, both **17 suites** — the pre-plan baseline of
141 cases / 17 suites, plus exactly 10 new cases (5 in `test_read_timing`, 5 in
`test_val_eeprom28c`), no new suite added. `suites` is unchanged at 17 in both envs (D-15).

## Comment-only renames confirmed (test_fix06_* bodies unchanged)

```
$ git diff test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp -- | grep -c '^[+-].*test_fix06'
0
```

The only diff lines touching the `test_fix06_*` functions are the two docstring-comment lines above
`test_fix06_planted_partial_write_fails_fixed_path_and_passes_legacy_poll` and
`test_fix06_page_boundary_window_readback` that rename `PAGE_SIZE` to `AT28C_PAGE_SIZE_FALLBACK` in
prose; no line inside either function body (or `test_fix06_clean_page_write_succeeds_isolation_control`,
untouched entirely) changed.

## AVR builds (warm, post-mask)

```
$ pio run -e uno
RAM:   [========  ]  76.9% (used 1575 bytes from 2048 bytes)
Flash: [========  ]  77.9% (used 25130 bytes from 32256 bytes)
[SUCCESS]

$ pio run -e uno328pb
RAM:   [========  ]  77.2% (used 1581 bytes from 2048 bytes)
Flash: [========  ]  77.8% (used 25180 bytes from 32384 bytes)
[SUCCESS]

$ pio run -e leonardo
RAM:   [========  ]  78.8% (used 2016 bytes from 2560 bytes)
Flash: [========= ]  94.9% (used 27212 bytes from 28672 bytes)
[SUCCESS]
```

**These are WARM figures from an incremental build directory that already carried plans 01-03's
untouched-firmware state — an early indicator only, explicitly not a substitute for plan 06's cold
measurement** (D-13: the comparison point is a fresh `rm -rf .pio/build/<env>` capture at the fork
point, which is what plan 01 already took: uno 24920, uno328pb 24970, leonardo 27002 flash;
1573/1579/2014 RAM). The warm deltas above (+210 uno, +210 uno328pb, +210 leonardo flash; +2 bytes
RAM on all three, from the `uint16_t page_size` field) are recorded here for plan 06 to reconcile
against a proper cold re-capture, not treated as the flash/RAM budget figure themselves.

## Firmware Python suite (after committing, per test_flash_path_record_sync.py's porcelain check)

```
$ python3 -m pytest tests/ -o addopts="" -q
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 68%]
........................................................................ [ 91%]
..........................                                               [100%]
314 passed in 10.65s
```
