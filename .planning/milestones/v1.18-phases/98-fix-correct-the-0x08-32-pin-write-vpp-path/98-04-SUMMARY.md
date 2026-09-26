---
phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path
plan: 04
subsystem: firmware
tags: [firmware, eprom, 0x08, AM27C020, PGM-hold, rw_line, native-test, golden-trace, gap-closure, CR-01]

# Dependency graph
requires:
  - phase: 98-03
    provides: "DIP32_27C020 rw-pin:[31] host half — resolves pin 31 to config.rw_line=22 via pin_conversions[32][31]"
  - phase: 98-02
    provides: "The inert A18-clear firmware branch (memory.cpp ~311-319) that this plan reverts"
provides:
  - "Corrected, revision-agnostic firmware CR-01 fix: pin 31 = /PGM held program-active LOW via the existing rw_line mechanism (CTRL_READ_WRITE 0x40), not a logical CTRL_ADDRESS_LINE_18 clear"
  - "WR-01 revision-parametrized native test (Rev 2 + Rev 0/1) — the missing RED state proving the 98-02 mechanism was a physical no-op on Rev 2 (0x08 alias) and a wrong-pin clear on Rev 0/1 (genuine A18 line)"
  - "WR-02 (RC-98B) pinned to TEST_ASSERT_EQUAL(5, ...) — exact baseline, not <=, closing the write-reducing-regression mask"
  - "RC-98A/C reconciled to the corrected rw_line reality (WR-04) — asserts CTRL_READ_WRITE LOW, not an extra-CONTROL-write count"
  - "Phase-99 HIGH-1 escape clause removed — a still-broken bench result can no longer be pre-dismissed"
affects: [98-05-tests-plan, phase-99-bench]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Revision-agnostic control-bit reliance: CTRL_READ_WRITE (0x40) is in the Rev-2 passthrough mask AND the Rev-0/1 raw passthrough, so a fix expressed via that bit needs no per-revision branching in firmware"
    - "Local test-replica of an AVR-only header function, documented inline, when [env:native]'s build_src_filter cannot link the real implementation without broader restructuring"

key-files:
  created: []
  modified:
    - "firestarter/src/proms/memory.cpp — reverted the gated ctrl & ~CTRL_ADDRESS_LINE_18 clear in memory_set_data; rewrote the RC-1 comment block to describe the corrected rw_line/CTRL_READ_WRITE mechanism; removed the Phase-99 HIGH-1 escape-clause caveat"
    - "firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp — WR-01 revision-parametrized physical-remap test (2 new RUN_TEST cases); RC-98A/C reconciled to the rw_line reality; RC-98B (WR-02) docstring + assertion pinned to EQUAL(5)"

key-decisions:
  - "IN-02 firmware constant (MAX_27C020_SIZE) deferred to 98-05, not added here: the entire size/protocol/pins gate that would have consumed a 262144 literal was removed by the revert (WR-04) — no size literal survives in memory.cpp for this plan to name. If 98-05 or a future plan needs a firmware-side named constant for a different purpose, that is out of this plan's scope."
  - "WR-01 uses LOCAL REPLICA functions (replica_map_ctrl_reg_rev2 / replica_map_ctrl_reg_legacy) mirroring rurp_hw_rev_utils.h lines 21-30 verbatim, rather than linking the real rurp_map_ctrl_reg_for_hardware_revision. That function lives in an AVR-only header (rurp_hw_rev_utils.h), only #included via rurp_register_utils.h from src/boards/{uno,leonardo}_rurp_shield.cpp — both excluded from [env:native]'s build_src_filter (+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>). The shared host stub (host_stubs_common.inc:138) is a plain (uint8_t)data passthrough with no per-revision modeling. Restructuring the native build to link the real AVR shield sources was judged out of scope for a gap-closure plan; the replica is documented in-file with a direct verbatim-mirror claim, verified against the real header at write time."
  - "RC-98B's bus_config for the 512K/A18-user case now sets rw_line=0xFF (the DIP32_27C040 'no rw-pin' shape) rather than reusing the old size-gate predicate — this correctly models D-04 under the corrected mechanism: the rw_line branch in mem_util_remap_address_bus is structurally inert for any chip whose pinout does not assign an rw-pin, with no protocol/size gate needed in firmware at all (WR-04: the removed gate had nothing left to guard)."

requirements-completed: [FIX-01, FIX-02, SAFE-02]

# Metrics
duration: 35min
completed: 2026-07-01
---

# Phase 98 Plan 04: Corrected Firmware CR-01 Fix — Revert Inert A18-Clear, Rely on rw_line Summary

**Reverted Plan 02's physically-inert `CTRL_ADDRESS_LINE_18` clear in `memory_set_data` and relies on the existing, revision-agnostic `rw_line` mechanism (fed by 98-03's `rw-pin:[31]` on `DIP32_27C020`) to hold pin 31 (/PGM = RW = `CTRL_READ_WRITE` physical 0x40) program-active LOW across the full write pulse — closing the CR-01 physical-no-op blocker with a native-test-provable, revision-agnostic fix.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-07-01T09:41:00Z
- **Completed:** 2026-07-01T10:16:00Z
- **Tasks:** 3 (Tasks 1+2 committed; Task 3 = verification-only, no code changes)
- **Files modified:** 2 (in `firestarter` submodule)

## Accomplishments

1. **Task 1 (revert + reconcile):** Deleted the gated `if (handle->protocol == 0x08 && handle->pins == 32 && handle->mem_size <= 262144) { ... ctrl & ~CTRL_ADDRESS_LINE_18 ... }` block from `memory_set_data`. Rewrote the RC-1 comment block to explain the corrected mechanism: pin 31 = /PGM = RW = `CTRL_READ_WRITE` (physical 0x40), revision-invariant (passes through `rurp_map_ctrl_reg_for_hardware_revision` on both the Rev-2 passthrough mask and the Rev-0/1 raw passthrough), already driven LOW on `WRITE_FLAG=0` by the existing `mem_util_remap_address_bus` + `mem_util_calculate_top_address_register` chain now that 98-03 set `config.rw_line=22`. Removed the Phase-99 HIGH-1 escape-clause sentences. `primitives.cpp` and `eprom.cpp` untouched (SAFE-02). `pio run -e uno` and `pio run -e leonardo` compile clean.

2. **Task 2 (WR-01 + WR-02 + RC-98A/C reconcile):** Added `test_wr01_rev2_pin31_pgm_low_with_vpp_concurrent` and `test_wr01_rev01_pin31_pgm_low_legacy` — the missing RED-state native tests, each feeding a program-window CONTROL value through a local replica of the per-revision remap and asserting physical `CTRL_READ_WRITE` (0x40) LOW, with the Rev-2 case additionally asserting `CTRL_VPP_P1_ENABLE` (0x08) stays HIGH concurrently (proving the alias does not defeat 0x40) and both cases showing the old 98-02 comparison value never asserts 0x40 at all. Fixed WR-02: RC-98B docstring corrected "4 writes" → "5 writes"; assertion tightened from `TEST_ASSERT_LESS_OR_EQUAL(5, ...)` to `TEST_ASSERT_EQUAL(5, ...)` (pinned baseline). Reconciled RC-98A/C to the corrected rw_line reality: `bus_config.rw_line` set to `22` (98-03's resolved value); assertions replaced the removed "extra CONTROL write count" discriminator with a check that a WRITE-phase CONTROL write carries `CTRL_READ_WRITE` clear. RC-98B's 512K bus_config uses `rw_line=0xFF` (the `DIP32_27C040` no-rw-pin shape) to model the D-04 exclusion under the corrected mechanism. `pio test -e native -f "*test_val_eprom*"`: 24/24 PASSED.

3. **Task 3 (golden-trace + full-suite verification):** Confirmed `git diff` on `golden_eprom_0x07_write.inc`, `golden_eprom_0x0B_write.inc`, `golden_eprom_chip_id.inc`, and `golden_eprom_0x08_write.inc` is empty — all four traces byte-identical, no re-bless needed (the 0x08 trace uses `pins=0` default, so neither the old nor the new mechanism ever fires in that golden-test context). `pio test -e native`: 119/119 PASSED (117 prior baseline + 2 new WR-01 revision cases). No code changes for this task.

## Task Commits

Each task was committed atomically inside the `firestarter` submodule:

1. **Task 1: Revert the inert A18-clear, rely on rw_line, reconcile the gate (WR-04), remove the escape clause** — `ee2ee22` (fix)
2. **Task 2: WR-01 revision-parametrized physical-remap test + WR-02/RC-98A/C rw_line reconcile** — `9922e5c` (test)
3. **Task 3: Golden-trace byte-identity + full native suite green** — no commit (verification-only; all traces byte-identical, no code changes)

_No plan-metadata commit inside the submodule — the meta-repo's final docs commit (this SUMMARY + STATE/ROADMAP) is the plan-level completion record per the sub-repo commit protocol._

## Files Created/Modified

- `firestarter/src/proms/memory.cpp` — reverted the gated `ctrl & ~CTRL_ADDRESS_LINE_18` clear in `memory_set_data`; the RC-1 comment block now documents the corrected, revision-agnostic `rw_line`/`CTRL_READ_WRITE` mechanism; the Phase-99 HIGH-1 escape-clause caveat sentences are deleted. Net: 50 insertions / 34 deletions (mostly comment).
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` — `test_wr01_rev2_pin31_pgm_low_with_vpp_concurrent` + `test_wr01_rev01_pin31_pgm_low_legacy` added (with `replica_map_ctrl_reg_rev2` / `replica_map_ctrl_reg_legacy` local helper replicas); `test_rc98a_0x08_32pin_256k_pgm_hold_via_rw_line` (renamed from `..._deliberate_pgm_hold_emitted`) and `test_rc98c_...` reconciled to assert `recording_has_ctrl_read_write_low()` instead of a CONTROL-write count; `test_rc98b_...` docstring/assertion pinned to `TEST_ASSERT_EQUAL(5, ...)`; RUN_TEST registrations updated. Net: 200 insertions / 112 deletions.

## Decisions Made

- Followed the plan's corrected mechanism exactly: no new firmware branch, no new wire field — the existing `rw_line` mechanism (already used by `DIP32_SST39SF040`) does the entire job once 98-03 wired `rw-pin:[31]` on `DIP32_27C020`.
- IN-02 firmware constant (a `MAX_27C020_SIZE` analog in `firestarter.h`) is explicitly **deferred to 98-05**, per the plan's own escape hatch: the revert removed the entire size/protocol/pins gate, so there is no `262144` literal left in `memory.cpp` for this plan to name. Recorded here rather than silently dropped.
- WR-01 could not exercise the real `rurp_map_ctrl_reg_for_hardware_revision` (AVR-only header, not linked into `[env:native]`'s `build_src_filter`). Per the plan's explicit permission ("OR by two local replicas mirroring rurp_hw_rev_utils.h lines 21-30 exactly ... document it in a header comment"), used local replica functions verified line-for-line against the real header, documented inline with the exact rationale.
- RC-98B's 512K bus_config now sets `rw_line=0xFF` (modeling `DIP32_27C040`'s "no rw-pin" shape) instead of relying on a removed protocol/size gate — this is the correct WR-04 reconciliation: the mechanism is inert by construction for any pinout that doesn't assign an rw-pin, no firmware-side gate needed.

## Deviations from Plan

None — plan executed as written, including its own documented escape hatches (IN-02 deferral condition met; WR-01 local-replica option exercised and cited).

## Known Stubs

None. The firmware fix is real code (no placeholder values); the WR-01 local replicas are explicitly documented test infrastructure, not production stand-ins, and are verified against the real header they mirror.

## Verification

```
$ pio run -e uno
RAM:   [========  ]  77.8% (used 1594 bytes from 2048 bytes)
Flash: [=======   ]  73.1% (used 23584 bytes from 32256 bytes)
[SUCCESS]

$ pio run -e leonardo
RAM:   [========  ]  79.4% (used 2033 bytes from 2560 bytes)
Flash: [========= ]  89.7% (used 25722 bytes from 28672 bytes)
[SUCCESS]

$ pio test -e native -f "*test_val_eprom*"
24 test cases: 24 succeeded

$ pio test -e native
119 test cases: 119 succeeded

$ git diff --stat src/proms/primitives.cpp src/proms/eprom.cpp
(empty — SAFE-02 confirmed)

$ git diff --stat test/native/avr/test_val_eprom/golden_eprom_0x07_write.inc \
    test/native/avr/test_val_eprom/golden_eprom_0x0B_write.inc \
    test/native/avr/test_val_eprom/golden_eprom_chip_id.inc \
    test/native/avr/test_val_eprom/golden_eprom_0x08_write.inc
(empty — D-05 byte-identity confirmed, including the 0x08 trace)
```

- No code line in `memory.cpp` performs `ctrl & ~CTRL_ADDRESS_LINE_18` — confirmed via grep (comment/header references filtered out).
- `git diff` on `primitives.cpp` + `eprom.cpp` empty — over-voltage / VPP-routing untouched (SAFE-02).
- RC-98B assertion is `TEST_ASSERT_EQUAL(5, ...)` (exact); no "baseline (4 writes)" text remains (grep-confirmed).
- All 4 protected golden traces (0x07, 0x0B, chip-id, 0x08) byte-identical; full native suite 119/119 green (117 prior + 2 new WR-01 cases, exactly as predicted).

## Next Phase Readiness

- **98-05 (tests plan):** IN-01/IN-03 and any remaining WR items from the gap-closure set are 98-05's responsibility; the IN-02 firmware-constant deferral (noted above) should be checked against 98-05's scope.
- **Phase 99 (BENCH + LEDGER):** The corrected firmware fix is committed, compiles clean on both `uno` and `leonardo`, and is now revision-agnostic by construction (no per-revision code branch — `CTRL_READ_WRITE` is a passthrough bit on every hardware revision). Phase 99 remains the sole empirical gate for silicon behavior, LOCKED to Leonardo + Rev 2.0; Rev 0/1 is covered by this code path + the WR-01 native test only, not bench this milestone (per the plan's BENCH CAVEAT).
- **PROTOCOL-LEDGER:** Still `0x08 = open-defect-carried (FUT-06)` pending Phase 99's empirical verdict — this plan does not change that status; it only makes the underlying firmware mechanism physically correct.

## Self-Check: PASSED

- FOUND: `.planning/phases/98-fix-correct-the-0x08-32-pin-write-vpp-path/98-04-SUMMARY.md`
- FOUND: `firestarter/src/proms/memory.cpp` (modified)
- FOUND: `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` (modified)
- FOUND (submodule): `ee2ee22` (Task 1)
- FOUND (submodule): `9922e5c` (Task 2)

---
*Phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path*
*Completed: 2026-07-01*
