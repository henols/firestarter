---
phase: 91-12v-vpp-write-path-regression-rca
plan: 01
subsystem: firmware-rca
tags: [rca, regression, diff-forensics, native-tests, vpp, flash3, eprom, recompose, a-b-prep]
requires:
  - phase: 90-04
    provides: BENCH-LOG FAIL-INVESTIGATE rows (0x06/0x07) + the v1.15 baseline SHAs
  - phase: 89
    provides: recompose firmware a296195 (P3/P4/P5 primitives) under investigation
provides:
  - 91-RCA.md working doc (recompose-innocence verdict + A/B decision tree)
  - diff-forensics.txt (captured git diff a1953c2..a296195 for the write path)
  - b10 baseline firmware built (/tmp/fs-b10, 25654 B) staged for the bench A/B
  - native golden traces re-confirmed green (flash3 6/6, eprom 19/19)
affects: [phase-91-wave2-bench-ab, recompose-write-path-rca, sst39sf040, w27c512]
key-files:
  created:
    - .planning/v1.16/ledger/rca/91-RCA.md
    - .planning/v1.16/ledger/rca/diff-forensics.txt
key-decisions:
  - "Recompose formally EXONERATED for both write paths: flash_type_3.cpp comment-only; eprom_write_execute byte-identical (only eprom_check_vpp/chip-id/init extracted); P3 vpp_check_window body identical AND unused by flash3 (5V-only). The revert-the-recompose hypothesis is closed."
  - "DB wire params byte-identical 98b3a92 vs e46549f for SST39SF040 AND W27C512,W27E512."
  - "Firmware identity discriminator = flash byte count (b10 25654 B vs recompose 25136 B); firestarter fw reports 3.0.0b10 for both."
  - "Deviation: b10 artifact is firestarter_leonardo.hex not firmware.hex (plan's literal verify path was wrong); build SUCCESS, substance met."
requirements-completed: [RCA-91 (analytic foundation; bench attribution in Wave 2)]
duration: ~15min
completed: 2026-06-26
---

# Phase 91 Plan 01: Diff-Forensics + Native Traces + A/B Prep — Summary

**The Phase-89 recompose introduced ZERO behavioral write-path delta on either failing
chip (proven by diff + byte-identity + green golden traces); the b10 baseline is built
and the A/B images are SHA-verified — Wave 2 can run pure silicon.**

## Accomplishments (no hardware, no source modified — SAFE-04 clean)
- **Diff forensics captured** (`diff-forensics.txt`, 29 KB) and classified: flash_type_3.cpp
  (0x06) = comment-only; eprom.cpp (0x07) = `eprom_check_vpp`/chip-id/init extraction only,
  `eprom_write_execute` (program loop) byte-identical. P3 `vpp_check_window` exonerated
  (body identical + flash3 never calls it). **Revert-the-recompose hypothesis closed.**
- **DB parity proven:** SST39SF040 and `W27C512,W27E512` chip_database.json entries
  byte-identical across host revs `98b3a92`↔`e46549f`.
- **Native golden traces green on a296195:** `test_val_flash3` 6/6 (incl. `test_golden_flash3_write`),
  `test_val_eprom` 19/19 (incl. `test_golden_eprom_0x07_write`). Bus sequences preserved →
  any bench failure is rail/timing/chip-state, not a code change.
- **A/B prep staged:** SST39SF040 image B SHA == `a38b13b4…970b96b` (FIX-91 gate); b10
  baseline built in `/tmp/fs-b10` (25654 B); recompose HEAD untouched (a296195); identity
  rule = flash byte count.

## Verification
- `test -s diff-forensics.txt` ✓; `grep "Diff Forensics"` + `grep vpp_check_window` in 91-RCA.md ✓
- `pio test -e native -f "*test_val_flash3*"` exit 0 (6/6) ✓; `*test_val_eprom*` exit 0 (19/19) ✓
- `sha256sum SST39SF040_img_B.bin` == a38b13b4… ✓; b10 build artifact present ✓
- `git -C firestarter status --porcelain src include` empty (SAFE-04) ✓; HEAD == a296195 ✓

## Deviations
- b10 artifact filename is `firestarter_leonardo.hex` (project convention), not the plan's
  literal `firmware.hex`. Build SUCCESS; A/B substance unaffected.

## Self-Check: PASSED
All 3 tasks executed; must_haves truths satisfied; the recompose-innocence verdict is
committed with reproducible evidence. RCA-91 analytic foundation complete — bench
attribution proceeds in Wave 2.
