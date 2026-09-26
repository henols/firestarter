---
phase: 88-golden-traces-dispatch-mirror-guard-was-87
plan: 01
subsystem: testing
tags: [unity, native, golden-trace, recording-bus, eprom, prim-01, safe-02]

requires:
  - phase: 87-naming-documentation-pass
    provides: INV-01..09 invariant matrix + test_val_eprom.cpp with recording bus

provides:
  - "_shared/golden_trace.h: assert_trace_eq() count-first byte-exact equality helper + GOLDEN_BLESS print mode"
  - "golden_eprom_0x07_write.inc: pinned 11-entry (reg,data) trace for EPROM_STD 1-byte write"
  - "golden_eprom_0x08_write.inc: pinned 11-entry (reg,data) trace for EPROM_QUICK 1-byte write"
  - "golden_eprom_0x0B_write.inc: pinned 11-entry (reg,data) trace for EPROM_LEGACY 1-byte write"
  - "golden_eprom_chip_id.inc: pinned 5-entry (reg,data) trace for eprom chip-id (P4) path"
  - "test_val_eprom.cpp extended with 4 golden test functions wired in main() RUN_TEST"

affects:
  - 88-02-eeprom28c-and-flash-intel-golden-traces
  - 88-03-flash3-and-flash4-golden-traces
  - 89-primitive-recompose
  - phase-89-recompose-oracle

tech-stack:
  added: []
  patterns:
    - "assert_trace_eq(exp, n, ctx): count-first (D-01) byte-exact equality over recording-bus API with anti-truncation guard"
    - "GOLDEN_BLESS compile flag activates print_trace_inc() for one-step fixture re-bless (D-02)"
    - "golden_entry_t struct + #include 'golden_*.inc' into static const array with sizeof/_n count"
    - "scripted-byte mock re-assigned AFTER configure_memory() to avoid Pitfall 3 pointer clobber"
    - "clear_bus_recording() called after configure_memory() to isolate init+execute from configure-phase address writes"

key-files:
  created:
    - firestarter/test/native/avr/_shared/golden_trace.h
    - firestarter/test/native/avr/test_val_eprom/golden_eprom_0x07_write.inc
    - firestarter/test/native/avr/test_val_eprom/golden_eprom_0x08_write.inc
    - firestarter/test/native/avr/test_val_eprom/golden_eprom_0x0B_write.inc
    - firestarter/test/native/avr/test_val_eprom/golden_eprom_chip_id.inc
  modified:
    - firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp

key-decisions:
  - "Blessed traces via GOLDEN_BLESS pio test run; rows captured from verbose output and committed as .inc fixtures"
  - "All three write protocols (0x07/0x08/0x0B) produce identical 8-bit traces because CTRL_VPP_VPE_DROP_ENABLE=0x100 is invisible in the low-byte recording (Pitfall 1); INV-01/INV-03 bit-level assertions remain as complementary guard"
  - "chip_id trace uses scripted bytes {0x1F, 0x00} → matching chip_id=0x1F00 so no error path fires; 5 entries capture VPP enable + A9 enable + clear"

patterns-established:
  - "Pattern: golden_trace.h assert_trace_eq() is the reusable equality oracle for all five test_val_* suites (88-02 and 88-03 consume it)"
  - "Pattern: .inc fixture header comments MUST contain producing-input description and 'low-byte' caveat for D-02 re-bless reproducibility"
  - "Pattern: GOLDEN_BLESS mode — compile with -DGOLDEN_BLESS, run pio test -v, grep '{ 0x' from verbose output, redirect to .inc"

requirements-completed: [PRIM-01, SAFE-02]

duration: 25min
completed: 2026-06-26
---

# Phase 88 Plan 01: Golden Traces — Eprom Family Summary

**Shared assert_trace_eq() helper + four byte-exact (reg,data) golden fixtures for eprom 0x07/0x08/0x0B write and chip-id (P4) paths, all 16 suite tests green**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-06-26T08:22:00Z
- **Completed:** 2026-06-26T08:47:17Z
- **Tasks:** 2 of 2
- **Files modified:** 6

## Accomplishments

- Authored `_shared/golden_trace.h` with `assert_trace_eq()` (count-first D-01, anti-truncation guard D-04, GOLDEN_BLESS print mode D-02) — the reusable oracle all remaining golden-trace plans consume
- Blessed and pinned four eprom `.inc` fixtures via GOLDEN_BLESS mode; each contains the header comment with producing input + low-byte caveat per acceptance criteria
- Extended `test_val_eprom.cpp` with 4 golden test functions wired in `main()` alongside all 12 existing INV/positive tests — SAFE-02 intact (48 INV- references, none removed)
- All 16 suite tests pass: `pio test -e native -f "*test_val_eprom*"` exits 0

## Task Commits

1. **Task 1: Author shared golden_trace.h helper** — `eaefbb2` (feat)
2. **Task 2: Bless + pin golden traces, wire into suite** — `7577570` (feat)

## Files Created/Modified

- `firestarter/test/native/avr/_shared/golden_trace.h` — `assert_trace_eq()` count-first byte-exact equality + `GOLDEN_BLESS` `print_trace_inc()` mode; include-after-extern-C requirement documented
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` — Added 4 golden test functions, scripted-byte chip-id mock, golden array declarations, 4 new RUN_TEST entries
- `firestarter/test/native/avr/test_val_eprom/golden_eprom_0x07_write.inc` — 11 entries; EPROM_STD 1-byte write trace
- `firestarter/test/native/avr/test_val_eprom/golden_eprom_0x08_write.inc` — 11 entries; EPROM_QUICK 1-byte write trace
- `firestarter/test/native/avr/test_val_eprom/golden_eprom_0x0B_write.inc` — 11 entries; EPROM_LEGACY 1-byte write trace (direct VPE rail; 0x100 DROP bit invisible)
- `firestarter/test/native/avr/test_val_eprom/golden_eprom_chip_id.inc` — 5 entries; eprom P4 chip-id path trace

## Decisions Made

- GOLDEN_BLESS bless workflow: built with `PLATFORMIO_BUILD_FLAGS=-DGOLDEN_BLESS`, ran `pio test -e native -f "*test_val_eprom*" -v`, extracted `{ 0x..., 0x... }` rows from verbose output between test PASS lines, committed to `.inc` files
- All three write protocol traces (0x07/0x08/0x0B) produce identical 8-bit row sequences because CTRL_VPP_VPE_DROP_ENABLE is 0x100 in the HARDWARE_REVISION branch — invisible in the low-byte recording. The golden traces still catch any *count* drift or *other register* drift during Phase 89 refactor. The INV-01/INV-03 bit-level assertions are the complementary guard for the 0x100 bit.
- chip_id scripted bytes {0x1F, 0x00} → chip_id=0x1F00 match path: no error set, trace captures init VPP check (2 writes) + execute VPP+A9 enable/disable (3 writes) = 5 entries

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None. The only notable discovery is that all three write protocol traces are 8-bit-identical due to CTRL_VPP_VPE_DROP_ENABLE=0x100 (invisible in recording). This is expected per Pitfall 1 and already documented in the plan. Each .inc fixture's header comment explicitly notes this, fulfilling D-02 re-bless reproducibility.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes introduced. This plan adds test-only files under `test/native/` and the `_shared/` test header; no production firmware source was modified (D-08 flash delta unaffected).

## Next Phase Readiness

- `golden_trace.h` is ready for 88-02 (eeprom28c + flash_intel) and 88-03 (flash3 + flash4) to `#include` it
- Bless workflow established and documented: run with `-DGOLDEN_BLESS`, extract rows from verbose output, commit to `.inc`
- All eprom INV tests remain green — safe to continue with 88-02

## Self-Check

- [ ] `firestarter/test/native/avr/_shared/golden_trace.h` exists: FOUND
- [ ] `firestarter/test/native/avr/test_val_eprom/golden_eprom_0x07_write.inc` exists: FOUND
- [ ] All four `.inc` files exist: FOUND
- [ ] Commits eaefbb2 and 7577570 exist in firestarter submodule: FOUND (see git log)
- [ ] `pio test -e native -f "*test_val_eprom*"` exits 0: CONFIRMED (16/16 passed)
- [ ] No INV assertions removed: CONFIRMED (48 INV- references)
- [ ] 4 RUN_TEST golden entries: CONFIRMED

## Self-Check: PASSED

---
*Phase: 88-golden-traces-dispatch-mirror-guard-was-87*
*Completed: 2026-06-26*
