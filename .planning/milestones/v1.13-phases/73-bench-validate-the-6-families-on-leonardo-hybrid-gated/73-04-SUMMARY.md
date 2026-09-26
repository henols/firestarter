---
phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated
plan: "04"
subsystem: testing
tags: [bench-validation, sram, fram, fm1608, val-06, fix-01, two-pattern, hardware]

# Dependency graph
requires:
  - phase: 73-01
    provides: Leonardo precondition armed, R1=270000 confirmed live, port identity verified
  - phase: 71-validation-harness-matrix
    provides: D-08 per-byte verdict logic, D-09 hard gate, two-pattern method, matrix schema
provides:
  - VAL-06 definitive verdict (table-stakes-PASS) with N=2 per-pattern per-byte evidence
  - FIX-01 disposition handed to Phase 74 (CLOSED NOT-NEEDED with evidence)
  - firestarter_app/val-results/sram/ directory with 7 binary artifacts + verdict + matrix
  - Erase path probe result for FM1608 (Open Question 1 answered: exit 1, Not supported)
affects: [73-SUMMARY, 74-per-family-correctness-fixes, Phase 74 FIX-01]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-pattern FRAM write+read-back: write 0x5A x8KB then 0xA5 x8KB each N=2 times — floating-bus echo cannot track two distinct bitwise-complement patterns"
    - "Per-byte D-08 verdict: case(a)=all match→PASS; case(b)=byte-0 only→PASS+parked; case(c)=bytes-beyond-0 fail→FIX-01"
    - "Erase path probe before any write to document configure_sram CMD_ERASE behavior"

key-files:
  created:
    - firestarter_app/val-results/sram/fm1608-baseline.bin
    - firestarter_app/val-results/sram/pattern_a.bin
    - firestarter_app/val-results/sram/pattern_b.bin
    - firestarter_app/val-results/sram/readback_a_run1.bin
    - firestarter_app/val-results/sram/readback_b_run1.bin
    - firestarter_app/val-results/sram/readback_a_run2.bin
    - firestarter_app/val-results/sram/readback_b_run2.bin
    - firestarter_app/val-results/sram/val06-perbyte-verdict.txt
    - firestarter_app/val-results/sram/validation-matrix.json
    - firestarter_app/val-results/sram/validation-matrix.md
  modified: []

key-decisions:
  - "VAL-06 = table-stakes-PASS: configure_sram writes via generic_memory_write_execute — zero mismatches across both patterns both runs (N=2)"
  - "FIX-01 (SRAM real read/write implementation): CLOSED NOT-NEEDED with evidence — no Phase 74 SRAM fix required"
  - "FM1608 erase path: exit 1 (Not supported) — validate_family sram would have exited 2 (hw-error); write -b path was the correct avoidance (Pitfall 3 confirmed)"
  - "Parked byte-0 FRAM bug: NOT triggered in this run (byte 0 matched in all 4 round trips)"
  - "D-09 hard gate: SATISFIED — definitive verdict reached, two runs agreed, no ambiguity"

patterns-established:
  - "FM1608 FRAM write: firestarter write FM1608 <file> -b (never erase, never dev validate-family sram directly)"
  - "Bench binary artifacts: git add -f required for *.bin files in val-results/ (root .gitignore has *.bin)"

requirements-completed: [VAL-06]

# Metrics
duration: 7min
completed: 2026-06-17
---

# Phase 73 Plan 04: VAL-06 FM1608 Two-Pattern Bench Validation Summary

**FM1608 FRAM two-pattern N=2 bench confirms VAL-06 = table-stakes-PASS: configure_sram writes via generic_memory_write_execute with zero mismatches across 0x5A/0xA5 patterns on both runs — FIX-01 closed not-needed with evidence**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-06-17T13:55:15Z
- **Completed:** 2026-06-17T14:03:00Z
- **Tasks:** 2 (auto)
- **Files modified:** 10 (all in firestarter_app/val-results/sram/)

## Accomplishments

- VAL-06 hard gate (D-09) SATISFIED with a DEFINITIVE bench verdict: table-stakes-PASS
- Two-pattern write+read-back x N=2: pattern A (0x5A×8192) and B (0xA5×8192) each round-tripped with ZERO mismatches across all 8192 bytes on both runs
- Erase path probe answered Open Question 1: `firestarter erase FM1608` exits 1 ("Not supported") — confirms erase avoidance (Pitfall 3) was essential; `dev validate-family sram` would have exited 2 (hw-error)
- Negative control proved non-vacuous: verify against baseline after pattern A write → exit 1 (FAIL at byte 0: 0xff != 0x5a)
- Phase 74 FIX-01 (SRAM real read/write) closed not-needed with evidence

## Task Commits

Each task was committed atomically inside the firestarter_app submodule:

1. **Tasks 1+2: FM1608 two-pattern HIL + VAL-06 verdict** - `63624b3` (feat)  
   Both tasks committed together since Task 2 analysis is performed on Task 1 artifacts.

**Plan metadata:** (docs commit — see below)

## Files Created/Modified

- `firestarter_app/val-results/sram/fm1608-baseline.bin` — Initial chip read before any write (8192 bytes, SHA 571fbb8c...)
- `firestarter_app/val-results/sram/pattern_a.bin` — 0x5A repeating 8192 bytes (SHA 1ae62b31...)
- `firestarter_app/val-results/sram/pattern_b.bin` — 0xA5 repeating 8192 bytes (SHA 2ef1444b...)
- `firestarter_app/val-results/sram/readback_a_run1.bin` — FM1608 read after pattern A write, run 1
- `firestarter_app/val-results/sram/readback_b_run1.bin` — FM1608 read after pattern B write, run 1
- `firestarter_app/val-results/sram/readback_a_run2.bin` — FM1608 read after pattern A write, run 2
- `firestarter_app/val-results/sram/readback_b_run2.bin` — FM1608 read after pattern B write, run 2
- `firestarter_app/val-results/sram/val06-perbyte-verdict.txt` — Full per-byte D-08 analysis and definitive VAL-06 verdict
- `firestarter_app/val-results/sram/validation-matrix.json` — sram Tier-3 leonardo cell: verdict=PASS, pass_type=authoritative, retry_count=2
- `firestarter_app/val-results/sram/validation-matrix.md` — Human-readable verdict table

## Pre-Write Gate Results

| Check | Value | Status |
|-------|-------|--------|
| controller | leonardo | CONFIRMED |
| Shield | Rev 2.0-class | CONFIRMED |
| R1 live | 270000 | IN-BAND [202500, 337500] |
| Firmware | 3.0.0b8 | OK |

## Erase Path Probe (Open Question 1)

```
firestarter -p /dev/ttyACM0 erase FM1608
→ ERROR: Not supported
→ Exit code: 1
```

Result: configure_sram CMD_ERASE is NOT a vacuous success — it errors with "Not supported". The direct write+read-back path (`firestarter write FM1608 -b`) was the correct and only viable approach. `dev validate-family sram` would have exited 2 (hw-error on the erase step) confirming Pitfall 3.

## Per-Byte Analysis Results (D-08)

| Run | Pattern | Written | Mismatches | SHA Match |
|-----|---------|---------|-----------|-----------|
| 1 | A (0x5A×8192) | 8192 bytes | **0** | YES |
| 1 | B (0xA5×8192) | 8192 bytes | **0** | YES |
| 2 | A (0x5A×8192) | 8192 bytes | **0** | YES |
| 2 | B (0xA5×8192) | 8192 bytes | **0** | YES |

D-08 case applied: **(a)** — ALL bytes match for both patterns on both runs → persistence confirmed.

## VAL-06 Verdict

```
VAL-06 = table-stakes-PASS
```

- configure_sram DOES write (via generic_memory_write_execute) — NOT a silent no-op
- Two distinct non-trivial patterns (0x5A bitwise-complement 0xA5) both persisted on N=2 runs
- Zero mismatches even at byte 0 (parked FRAM byte-0 bug was NOT triggered in this session)
- Negative control proved oracle non-vacuous (verify against wrong file → exit 1)
- Both runs agreed completely — no ambiguity, D-09 hard gate fully satisfied

## Phase-74 FIX-01 Disposition

**FIX-01 (SRAM real read/write implementation): CLOSED NOT-NEEDED**

VAL-06 = table-stakes-PASS with authoritative Leonardo evidence (retry_count=2).
Phase 74 does NOT need to implement SRAM write/read. `configure_sram` writes correctly via the
existing `generic_memory_write_execute` path. FIX-01 is closed with evidence, not skipped.

## Decisions Made

1. **VAL-06 = table-stakes-PASS** — zero mismatches across both patterns and both runs confirms real persistence, not a no-op confound.
2. **FIX-01 closed not-needed with evidence** — Phase 74 SRAM fix scoped out.
3. **Erase avoidance confirmed correct** — `firestarter erase FM1608` exits 1; the write-only path was essential.
4. **Parked byte-0 bug not triggered** — this session produced byte-0 matches, so the separation logic (D-08 case b) did not need to fire. If byte 0 had mismatched while bytes 1..8191 matched, the verdict would still have been table-stakes-PASS (per D-08); the result here is cleaner still.

## Deviations from Plan

None — plan executed exactly as written.

The erase probe confirmed the expected Pitfall 3 behavior (exit 1, Not supported), and the two-pattern method worked cleanly on first attempt. No auto-fix deviations were needed.

## Issues Encountered

None. All pre-write gate checks passed on first attempt. Both pattern write+read-back cycles completed cleanly. The D-09 hard gate was satisfied on the first bench session with unambiguous results.

## Self-Check Note

The `*.bin` files required `git add -f` due to the root `.gitignore` containing `*.bin`. This is consistent with how prior plans (73-02) handled the `cycle_01_readback.bin` and source image artifacts — force-add is the established pattern for val-results binary artifacts.

## Self-Check: PASSED

All created files verified present:
- 7 binary artifacts: fm1608-baseline.bin, pattern_a.bin, pattern_b.bin, readback_a_run1/b_run1/a_run2/b_run2.bin
- val06-perbyte-verdict.txt, validation-matrix.json, validation-matrix.md
- 73-04-SUMMARY.md

Commit verified: `63624b3` (firestarter_app submodule)
Meta commit: `be00e26` (SUMMARY.md + STATE.md + ROADMAP.md)

## Next Phase Readiness

- Phase 73 is now complete: all 6 families have recorded Tier-3 verdicts (3 on-hand families: eprom=PASS, flash4=FAIL on W29C040, sram=PASS; 3 chipless: flash3/eeprom28c/flash_intel SKIP-deferred)
- Phase 74 FIX-01 (SRAM) is CLOSED NOT-NEEDED with evidence — only FIX-02 (flash4 CMD_CHECK_CHIP_ID) and FIX-03 (0x39 stale-comment) remain as Phase 74 work items
- No blockers for Phase 74 execution

---
*Phase: 73-bench-validate-the-6-families-on-leonardo-hybrid-gated*
*Plan: 04*
*Completed: 2026-06-17*
