---
phase: 91-12v-vpp-write-path-regression-rca
plan: 02
subsystem: firmware-rca
tags: [rca, regression, bench, ab-test, sst39sf040, erase-completeness, decision-gate, forensic]
requires:
  - phase: 91-01
    provides: recompose-innocence diff verdict + b10 baseline build + A/B images
provides:
  - ebca6266 content forensic (Open Q1 resolved — 3 bytes @0x0-0x2, incomplete erase)
  - reproduced SST39SF040 write failure on recompose (verify 0x1c!=0x04 @0x0)
  - b10 A/B leg (b10 fails IDENTICALLY -> recompose innocent, pre-existing)
  - root-cause attribution (RCA-91): flash3 105ms blind erase-delay marginal
  - both-symptom explanation (erase-before-write axis, NOT 12V-VPP)
affects: [phase-91-wave3-fix, sst39sf040, w27c512]
key-files:
  created:
    - .planning/v1.16/ledger/rca/ebca6266-forensic.txt
    - .planning/v1.16/ledger/bench/SST39SF040-ab/SHA256SUMS.txt
  modified:
    - .planning/v1.16/ledger/rca/91-RCA.md
key-decisions:
  - "Open Q1: the 'deterministically-wrong' content is 99.9994% == imgB; only 3 bytes @0x0-0x2 differ, all == imgA & imgB = incomplete erase at sector 0 (NOR cells can't 0->1 without erase)."
  - "Decision gate: b10 fw (a1953c2) fails byte-identically (verify 0x1c!=0x04 @0x0) to the recompose => recompose INNOCENT; pre-existing marginal chip-erase-completion timing bug in the byte-identical flash3 path."
  - "Both symptoms share the erase-before-write axis (flash3 incomplete erase; W27C512 non-blank chip-state) — NOT 12V-VPP. flash3 is 5V-only and never enables the VPP regulator."
  - "DQ7-only per-byte poll (flash_util_verify_operation & 0x80) masks the failure -> fw reports write 'successful'; only full verify catches it."
  - "Leonardo re-enumerates after reflash (ACM0->ACM1); firestarter CLI auto-detects the port + retries."
requirements-completed: [RCA-91]
duration: ~25min
completed: 2026-06-26
---

# Phase 91 Plan 02: Bench A/B + Decision Gate — Summary

**RCA-91 satisfied: the SST39SF040 failure is an incomplete chip-erase at the 105 ms blind
delay (3 residual bytes @0x0-0x2 = imgA & imgB), reproduced on the recompose AND failing
byte-identically on the b10 baseline — proving the recompose innocent and the bug pre-existing.
Both symptoms share the erase-before-write axis, not 12V-VPP.**

## Accomplishments (all on the seated SST39SF040, autonomous)
- **Open Q1 resolved:** re-read the chip (SHA == Phase-90 `ebca6266…`), byte-compared to image B:
  **524285/524288 match (99.9994%); only 3 bytes wrong, all @0x0-0x2, all == `imgA & imgB`** —
  the textbook NOR incomplete-erase signature.
- **Reproduced on recompose:** `write -b imgB` RC=0 "successful (177.66s)" but `verify` RC=1
  `0x1c != 0x04 @0x000000`.
- **b10 A/B leg (THE experiment):** reflashed b10 (a1953c2, 25654 B avrdude-verified); `write -b
  imgB` + `verify` → **identical failure `0x1c != 0x04 @0x000000`**. Recompose INNOCENT.
- **Root cause (RCA-91):** `flash3_write_init` chip-erase + fixed `delay(105 ms)` (no completion
  poll); this chip's erase finishes a few ms later, so the first bytes program onto un-erased
  cells; DQ7-only poll masks it. Byte-identical b10↔recompose.
- **Both symptoms explained:** erase-before-write axis (SST39SF040 incomplete erase; W27C512
  non-blank chip-state) — NOT VPP (flash3 is 5V-only, no P3, no regulator).

## Verification
- `ebca6266-forensic.txt` non-empty with divergence map + classification ✓
- `bench/SST39SF040-ab/SHA256SUMS.txt` records both legs' outcomes vs `a38b13b4…` ✓
- 91-RCA.md has Content Forensic + Decision Gate + Both Symptoms Explained ✓
- `git -C firestarter status` — flash_type_3.cpp fix staged for Wave 3; VPP guard untouched ✓

## Deviations
- VPP loaded-rail capture: **N/A** — flash3 is 5V-only (regulator never enabled) and a single
  serial port cannot monitor `vpp` and `write` concurrently. Recorded; the axis is erase, not VPP.
- Bench Tool timeout: long writes (~177s) exceed the 2-min foreground Bash limit; run in background.

## Self-Check: PASSED
RCA-91 fully attributed via controlled A/B + content forensic; both symptoms explained; fix branch
(widen flash3 erase settle 105→500 ms) handed to Plan 03 (already applied + built, pending silicon
validation).
