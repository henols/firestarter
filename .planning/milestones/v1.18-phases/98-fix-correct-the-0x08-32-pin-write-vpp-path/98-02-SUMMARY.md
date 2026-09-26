---
phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path
plan: 02
subsystem: firmware
tags: [firmware, eprom, 0x08, AM27C020, PGM-hold, native-test, golden-trace, TDD, RC-1]

requires:
  - phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path/98-01
    provides: "DIP32_27C020 pinout (pin 31 off address bus) + Q1 RESOLVED verdict (static-high ruled out → firmware hold-LOW is the PGM vehicle)"

provides:
  - "Gated deliberate PGM hold-LOW in memory_set_data (memory.cpp) for protocol==0x08 && pins==32 && mem_size<=262144"
  - "RC-98A/B/C native Unity tests: corrected-path (CODE-STRUCTURE), D-04 gate exclusion, mismatch failure-case"
  - "Golden traces 0x07/0x0B/chip-id byte-identical (D-05); 0x08 trace unchanged (A5 confirmed)"
  - "Full native suite (117/117 tests) green; SAFE-02 integrity (primitives.cpp unchanged)"

affects:
  - 98-03 (Phase 99 bench — empirical gate; this plan is the firmware under test)
  - any future plan modifying the 0x08 write path or memory_set_data

tech-stack:
  added: []
  patterns:
    - "Gated per-byte PGM hold-LOW pattern: protocol+pins+mem_size triple gate before rurp_chip_enable in memory_set_data"
    - "TDD CODE-STRUCTURE assertion: CONTROL write count discriminator (pre-fix=5, post-fix=6) avoids circular bit-level assertion"
    - "MED-5 verified no-op: per-buffer P1-hold already spans CE window; no per-byte churn"

key-files:
  created: []
  modified:
    - "firestarter/src/proms/memory.cpp — gated PGM hold-LOW in memory_set_data (protocol==0x08 && pins==32 && mem_size<=262144)"
    - "firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp — RC-98A/B/C tests + helpers (count_control_reg_writes, recording_has_consecutive_control_writes)"

key-decisions:
  - "A5 CONFIRMED: 0x08 golden trace unchanged — test_golden_eprom_0x08_write uses default pins=0, which fails the pins==32 gate; trace is byte-identical to pre-fix"
  - "MED-5 verified no-op: existing per-buffer CTRL_VPP_P1_ENABLE hold in program_mismatched_bytes already strictly encompasses every per-byte CE pulse in memory_set_data — no redundant per-byte P1 re-assertion added"
  - "TDD discriminator (HIGH-3): pre-fix CONTROL write count=5 (empirically confirmed); post-fix=6 (one extra deliberate PGM-hold write); tested via ≥6 assertion — NOT bit-level LOW-ness (circular at addr=0)"
  - "RC-98C mismatch count: mock replaces firestarter_get_data (not memory_get_data), so set_addr for verify is absent; pre-fix count=62, post-fix=82 per 20 retries"
  - "No new wire field added (Q2/D-03 honored): existing protocol/pins/mem_size struct fields suffice"
  - "SAFE-02: primitives.cpp untouched (git diff empty); vpp_check_window over-voltage ERROR path intact"

requirements-completed: [FIX-01, FIX-02, SAFE-02]

duration: 15min
completed: 2026-06-30
---

# Phase 98 Plan 02: Gated Deliberate PGM Hold-LOW Firmware + Native Tests Summary

**Gated deliberate PGM=VIL hold-LOW in memory_set_data for 0x08 32-pin ≤256K (AM27C020), backed by TDD CODE-STRUCTURE tests (RC-98A/B/C); golden traces 0x07/0x0B/chip-id byte-identical; 0x08 trace unchanged (A5); full native suite 117/117 green**

## HIGH-1 HEADLINE (verbatim — dominant expected outcome, NOT a footnote)

**Under RC-1, the addr-0 register state is byte-unchanged by this firmware fix — pin 31 is already at VIL at addr 0 (line 22 is neither an address bit in DIP32_27C020 nor in static_high_mask, so it is 0 before and after the fix). If Phase 99 still shows 0 bits at addr 0, that is CONSISTENT WITH the analysis, not a new bug. This plan delivers the architecturally-correct firmware PGM-assert (explicit hold-LOW of line 22 across the CE pulse); it does NOT claim to flip bits on silicon — Phase 99 is the sole empirical gate.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-06-30T14:21:11Z
- **Completed:** 2026-06-30T14:36:00Z
- **Tasks:** 3 (Tasks 1+2 committed; Task 3 = no-op, A5 confirmed)
- **Files modified:** 2 (in firestarter submodule)

## Accomplishments

1. **Task 1 (RED native tests):** Added `test_rc98a_0x08_32pin_256k_deliberate_pgm_hold_emitted` (corrected-path, HIGH-3 CODE-STRUCTURE assertion), `test_rc98b_0x08_32pin_512k_pgm_hold_excluded` (D-04 gate exclusion), and `test_rc98c_0x08_32pin_256k_mismatch_errors_and_pgm_asserted` (P89 CR-01 mandatory failure-case). RED state confirmed: RC-98A failed (count 5 < 6) and RC-98C failed (count 62 < 63) pre-fix.

2. **Task 2 (GREEN firmware):** Added gated deliberate PGM hold-LOW in `memory_set_data`: `rurp_read_from_register(CONTROL_REGISTER)` → mask `~CTRL_ADDRESS_LINE_18` → `rurp_write_to_register(CONTROL_REGISTER, ...)` before `rurp_chip_enable()`, gated on `protocol==0x08 && pins==32 && mem_size<=262144`. All three new tests GREEN; 22/22 test_val_eprom tests pass; SAFE-02 intact.

3. **Task 3 (golden discipline):** Ran GOLDEN_BLESS via the compiled test binary. All four traces byte-identical to pre-fix. A5 confirmed: the 0x08 golden test uses default `pins=0`, which fails the `pins==32` gate — the deliberate PGM-hold branch never fires in the golden test context, so the trace is unchanged. Full native suite 117/117 green.

## Task Commits

1. **Task 1 (RED): corrected-path + gate-exclusion + mismatch native tests** — `f8b4a7e` (test)
2. **Task 2 (GREEN): gated deliberate PGM hold-LOW in memory_set_data** — `f1210a6` (feat)
3. **Task 3: golden discipline** — no commit (A5: all four traces byte-identical)

## Gate Acceptance Criteria Verified

- `pio test -e native -f "*test_val_eprom*"`: 22/22 PASSED (RC-98A/B/C green)
- `pio test -e native`: 117/117 PASSED (full suite)
- `git diff --exit-code golden_eprom_0x07_write.inc golden_eprom_0x0B_write.inc golden_eprom_chip_id.inc`: EMPTY (byte-identical, D-05 tripwire clear)
- `git diff --exit-code golden_eprom_0x08_write.inc`: EMPTY (A5 confirmed — trace unchanged)
- `git diff src/proms/primitives.cpp`: EMPTY (SAFE-02 — vpp_check_window over-voltage path untouched)
- `grep -v '^//' src/proms/memory.cpp | grep -c 262144`: 2 (size term present in new branch — D-04 belt confirmed)
- No new wire field (`firestarter.h` unchanged — Q2/D-03 honored)

## Exact Gate Predicate Landed

```cpp
if (handle->protocol == 0x08 && handle->pins == 32 && handle->mem_size <= 262144) {
    rurp_register_t ctrl = rurp_read_from_register(CONTROL_REGISTER);
    rurp_write_to_register(CONTROL_REGISTER, ctrl & ~CTRL_ADDRESS_LINE_18);
}
```

Located in `memory_set_data` in `firestarter/src/proms/memory.cpp`, immediately before `rurp_chip_enable()`. The size term `mem_size <= 262144` makes the 0x08 bit (= CTRL_VPP_P1_ENABLE_REV2 = CTRL_ADDRESS_LINE_18_REV2 on Rev 2.0) UNREACHABLE for any 512K/1M A18 user.

## MED-5 Reconciliation: P1-hold Already Spans the CE Window (Verified No-Op)

Reading `program_mismatched_bytes` (eprom.cpp:168-179) confirms: `firestarter_set_control_register(CTRL_VPE_ENABLE, 1)` is called BEFORE the byte loop (→ sets CTRL_VPP_P1 via the VPE→P1 rewrite when `using_p1_as_vpp=true`), and cleared AFTER. This per-buffer hold strictly encompasses every per-byte CE pulse in `memory_set_data`. **No redundant per-byte CTRL_VPP_P1 re-assertion was added**. The new firmware code only asserts the PGM line (CTRL_ADDRESS_LINE_18 / pin 31 / line 22) — a DISTINCT control from the P1 VPP routing. These are separate concerns: P1-hold is the VPP routing for the program voltage; the PGM-assert is the program-enable control for the chip.

## HIGH-3 TDD Discriminator Design

**Why "≥6 CONTROL writes" and not "line 22 is LOW":**

At addr=0, line 22 (CTRL_ADDRESS_LINE_18) is already 0 pre-fix because:
1. In DIP32_27C020, pin 31 is NOT in address-bus-pins (A18 is excluded)
2. `static_high_mask = 0` (no static-high entry in DIP32_27C020)
3. Address 0 → all address bits = 0

Asserting `line 22 is LOW` would be circular (true before AND after the fix). The RED-able discriminator is the PRESENCE/COUNT of the extra CONTROL write emitted by the gated branch:

| State | Execute-phase CONTROL writes (1 byte, addr=0, DIP32_27C020 bus_config) |
|-------|------------------------------------------------------------------------|
| Pre-fix | 5: VPP-reg set, CTRL_VPP_P1 set, set_addr write, CTRL_VPP_P1 clear, set_addr verify |
| Post-fix | 6: same + 1 deliberate PGM-hold write in memory_set_data |

RC-98A: asserts ≥6 → RED pre-fix (count=5), GREEN post-fix (count=6).
RC-98C: asserts ≥63 (pre-fix=62 for 20 retries, post-fix=82) → RED pre-fix, GREEN post-fix.

A green RC-98A verifies CODE STRUCTURE (deliberate PGM assert is emitted). It does NOT imply bits flip on silicon — see HIGH-1 above.

## Golden Trace Discipline (A5 Confirmed)

- `golden_eprom_0x07_write.inc`: BYTE-IDENTICAL (0x08 path change does not affect 0x07)
- `golden_eprom_0x08_write.inc`: BYTE-IDENTICAL — A5 confirmed. The `test_golden_eprom_0x08_write` function uses `make_handle(0x08, CMD_WRITE)` which leaves `pins=0` (default). The gate `handle->pins == 32` is FALSE → the deliberate PGM-hold branch does NOT fire → the trace is identical to the pre-fix trace (11 entries, same values).
- `golden_eprom_0x0B_write.inc`: BYTE-IDENTICAL
- `golden_eprom_chip_id.inc`: BYTE-IDENTICAL

Pitfall 2 respected: GOLDEN_BLESS was run in an isolated session (via direct binary invocation); the four trace outputs were compared to existing .inc files; all four match — no re-bless needed.

## SAFE-02 Status

- `git diff src/proms/primitives.cpp`: EMPTY — `vpp_check_window` HIGH→ERROR path untouched; no FLAG_FORCE relaxation; no test-only escape hatch. AM27C020 flows through normal 0x08 dispatch.
- No edit to any VPP-routing paths in `primitives.cpp`.

## Files Created/Modified

- `firestarter/src/proms/memory.cpp` — gated deliberate PGM hold-LOW added in `memory_set_data` (41 lines: 39 comment + 4 code)
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` — RC-98A/B/C tests + helpers + RUN_TEST registrations (247 lines added in Task 1)

## Decisions Made

- Q1 RESOLVED (carried from Plan 01): static-high-pins RULED OUT; PGM=VIL assert is explicit firmware hold-LOW (`~CTRL_ADDRESS_LINE_18` mask), NOT `static_high_mask` entry
- Q2 RESOLVED: no new wire field needed (existing `protocol`/`pins`/`mem_size` suffice for the gate); `firestarter.h` unchanged
- A5 CONFIRMED: 0x08 golden trace is byte-identical post-fix; no re-bless needed
- MED-5: per-buffer P1-hold already spans the CE window; no per-byte churn added
- HIGH-1: phase 99 is the sole empirical gate; this fix is a blind architectural correction

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] TDD pre-fix baseline count wrong (4 → 5 CONTROL writes)**
- **Found during:** Task 1 verification (first RED run)
- **Issue:** Initial test analysis estimated 4 CONTROL writes pre-fix (VPE set, set_addr write, VPE clear, set_addr verify). The actual pre-fix count is 5 because `eprom_write_execute` also sets the VPP regulator at the start of each execute call (stub `rurp_read_from_register` always returns 0, so the "already on" branch is never taken).
- **Fix:** Updated test assertions from ≥5 to ≥6 (RC-98A) and from ≤4 to ≤5 (RC-98B). Updated comments with correct baseline analysis including the VPP regulator write.
- **Files modified:** `test/native/avr/test_val_eprom/test_val_eprom.cpp`
- **Committed in:** f8b4a7e (Task 1 commit)

**2. [Rule 1 - Bug] RC-98C mismatch baseline count wrong (82 → 62 CONTROL writes)**
- **Found during:** Task 1 verification (second RED run)
- **Issue:** Analysis assumed `verify_and_update_mask` would call `memory_get_data → mem_util_set_address` (contributing a CONTROL write per retry). However, `mock_rc98c_always_mismatch` replaces `firestarter_get_data` directly — `memory_get_data` is NOT called, so the set_addr for verify is absent. Pre-fix count = 62 (1 VPP-reg + 20×3 + 1 VPP-clear), not 82.
- **Fix:** Updated RC-98C assertion from ≥82 to ≥63 (pre-fix=62, post-fix=82). Updated comments with corrected accounting.
- **Files modified:** `test/native/avr/test_val_eprom/test_val_eprom.cpp`
- **Committed in:** f8b4a7e (Task 1 commit, corrected before final commit)

---

**Total deviations:** 2 auto-fixed (Rule 1 — TDD baseline count errors in test design)
**Impact on plan:** Both fixes necessary for correct TDD RED state. No scope creep.

## Known Stubs

None. The firmware fix is real code; the tests are real assertions. No placeholder values or "coming soon" stubs.

## Next Phase Readiness

- **Phase 99 (BENCH + LEDGER):** The firmware fix is committed and the native tests prove the deliberate PGM assert is emitted. Phase 99 is the sole empirical gate for silicon behavior. Setup: Leonardo + RURP Rev 2.0, seated AM27C020, DMM at socket pins 1 (VPP) and 31 (PGM) during write attempt.
- **Phase 99 must know:** Under RC-1, the addr-0 register state is byte-unchanged by this fix. A continuing 0-bits result at addr 0 is CONSISTENT WITH the analysis (Phase 99 may still show 0 bits if the chip is OTP/dead — PRE-01 writability gate). The diagnostic: write to a non-zero address to see if higher addresses (where A0-A17 vary) show the fix taking effect.
- **PROTOCOL-LEDGER:** Must be updated at Phase 99 close — current status: `0x08 = open-defect-carried (FUT-06)`. Upgrade to `supported` on bench PASS, or re-record as FUT on clean deferral.

## Self-Check: PASSED

- firestarter/src/proms/memory.cpp: FOUND (modified)
- firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp: FOUND (modified)
- Commit f8b4a7e (Task 1 — RED native tests): FOUND
- Commit f1210a6 (Task 2 — GREEN firmware PGM-hold): FOUND
- `pio test -e native -f "*test_val_eprom*"`: 22/22 PASSED (verified)
- `pio test -e native`: 117/117 PASSED (verified)
- `git diff golden_eprom_0x07_write.inc ... chip_id.inc`: EMPTY (D-05 byte-identical verified)
- `git diff golden_eprom_0x08_write.inc`: EMPTY (A5 confirmed)
- `git diff src/proms/primitives.cpp`: EMPTY (SAFE-02 confirmed)
- Size term `262144` in non-comment lines: 2 occurrences (D-04 belt present)

---

*Phase: 98-fix-correct-the-0x08-32-pin-write-vpp-path*
*Completed: 2026-06-30*
