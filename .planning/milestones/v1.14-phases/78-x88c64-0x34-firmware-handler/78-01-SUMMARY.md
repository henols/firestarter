---
phase: 78-x88c64-0x34-firmware-handler
plan: 01
subsystem: firmware-feasibility-doc
tags: [x88c64, ale-routing, feasibility, deferral, documentation-only]
requires: []
provides:
  - "A6 ALE-routing verdict (PCB-BLOCKED) in X88C64-FEASIBILITY.md"
  - "FUT-01 future-unblock spec"
  - "Graduation-pending-hardware note (SC#4/XIC-04 deferred)"
affects:
  - ".planning/X88C64-FEASIBILITY.md"
tech-stack:
  added: []
  patterns: ["source-trace verdict with line-cited evidence", "PCB-blocked deferral with FUT spec"]
key-files:
  created: []
  modified:
    - ".planning/X88C64-FEASIBILITY.md"
decisions:
  - "A6 VERDICT: PCB-BLOCKED at HIGH confidence — control register fully allocated, 0x100 non-transmissible, no free strobe, D-02 bar prohibits busy-bit reuse"
  - "Section inserted before §7 Sources (logical reading order), not appended at EOF"
  - "Zero code changes — handler-write branch (Plan 02) will no-op on this verdict"
metrics:
  duration: ~12min
  completed: 2026-06-22
  tasks: 2
  files: 1
---

# Phase 78 Plan 01: X88C64 ALE-Routing Trace & A6 Verdict Summary

**One-liner:** Source-traced the RURP control-register allocation and 74HC573 strobe
architecture to resolve Assumption A6 — verdict **PCB-BLOCKED** (HIGH confidence) — and
recorded the FUT-01 future-unblock spec plus the hardware-deferred SC#4 graduation note in
`X88C64-FEASIBILITY.md`, with zero code changes.

## A6 Verdict Outcome (read by Plan 02's gate)

**A6 VERDICT: PCB-BLOCKED**

Plan 02's leading BLOCKING gate task should read this as the **deferral branch** — the
handler-write branch does NOT activate. No `configure_x88c64`, no 0x34 dispatch arm, no
native test suite. X88C64 stays `protocol-not-implemented` and host-refused; FUT-01 stays
open. A documented PCB-block deferral is the clean, expected (RESEARCH HIGH-confidence)
completion — not a failure.

## What Was Built

Two new sections in `.planning/X88C64-FEASIBILITY.md` (inserted before §7 Sources):

- **## A6 ALE-Routing Verdict (Phase 78)** — first content line `A6 VERDICT: PCB-BLOCKED`,
  followed by line-cited trace evidence:
  - CTRL_* bit allocation tables for BOTH the 8-bit (`rurp_pinout.h:74–83`) and wide
    `HARDWARE_REVISION` (`rurp_pinout.h:85–97`) layouts — every bit 0x01..0x80 named and
    cited as allocated.
  - The 0x100 / uint8_t-truncation argument: `rurp_internal_write_to_register`
    (`rurp_register_utils.h:63–89`) → `rurp_write_data_buffer(data)` at
    `rurp_register_utils.h:83`, declared `void rurp_write_data_buffer(uint8_t data)` at
    `rurp_shield.h:113` — so `0x100 & 0xFF == 0x00` and the "9th bit" never reaches the
    74HC573.
  - 74HC573 strobe inventory (`rurp_shield.h:53–57`) — all five strobes assigned; no free
    ALE strobe; shared-bus single-strobe write path (`rurp_register_utils.h:83–88`).
  - Explicit D-02 statement that no speculative reuse of a busy bit was adopted (the
    `CTRL_VPP_REGULATOR_ENABLE` undamped-VPP-spike hazard).
- **### FUT-01 Future-Unblock Spec (D-03)** — three future hardware paths (new shield-rev 9th
  bit; dedicated ALE GPIO; NOT-recommended idle-window reuse) + a `TODO:` to check the
  Leonardo ATmega32u4 GPIO-to-socket map (RESEARCH Open-Question 2).
- **### Graduation Pending Hardware (SC#4 / XIC-04, D-04)** — X88C64 stays
  `protocol-not-implemented` + host-refused; bench graduation (N≥5 Leonardo SHA-match +
  negative control, chip-OUT VPP dry-run / ASK shield rev / live r1 / port identity) tracked
  under FUT-01; no DB change.
- **### SAFE Invariants** — SAFE-01 (host-guard NOT removed), SAFE-02 (`check_dispatch.py`
  unaffected), SAFE-03 (no constant parity touched) confirmed to hold trivially.

## Requirements Satisfied

- **XIC-01** — A6 verdict recorded with concrete line-cited trace evidence from
  `rurp_pinout.h`, `rurp_register_utils.h`, and `rurp_shield.h`.
- **XIC-04** — satisfied as deferral-with-evidence: graduation recorded hardware-blocked
  (D-04 / FUT-01); chip stays refused.

## Deviations from Plan

None - plan executed exactly as written. The trace independently confirmed the
RESEARCH-expected PCB-BLOCKED landing; no free bit was found, so no FREE-BIT-FOUND branch was
taken.

## Commits

- `d5c899d` docs(78-01): record A6 ALE-routing verdict (PCB-BLOCKED) with line-cited trace
- `7236113` docs(78-01): add FUT-01 future-unblock spec + graduation-pending-hardware note

## Verification

- `grep "A6 VERDICT:" .planning/X88C64-FEASIBILITY.md` → `A6 VERDICT: PCB-BLOCKED`
- `grep "FUT-01"` and `grep -i "graduation pending hardware"` → both match
- `grep "TODO:"` + `grep "ATmega32u4"` → both match (Leonardo GPIO TODO present)
- `grep -i "NOT removed"` → SAFE-01 present
- `git -C firestarter status --porcelain` (code) → no firmware code changes
- `git -C firestarter_app status --porcelain` (code) → no host code changes
- Cited line numbers verified against live source: `rurp_pinout.h:74–99`,
  `rurp_register_utils.h:24–89`, `rurp_shield.h:53–57,118`.

## Known Stubs

None. Documentation-only plan; no UI/data wiring.

## Notes for Downstream (Plan 02)

The A6 verdict is **PCB-BLOCKED**. Plan 02's gate must take the no-op/deferral path: do not
write `configure_x88c64`, do not add a 0x34 dispatch arm, do not create
`test_val_x88c64`, do not touch `chip_resolver.py` or `chip_database.json`. The phase closes
clean on the deferral branch with FUT-01 open.

## Self-Check: PASSED

- FOUND: `.planning/X88C64-FEASIBILITY.md`
- FOUND: `.planning/phases/78-x88c64-0x34-firmware-handler/78-01-SUMMARY.md`
- FOUND commit: `d5c899d`
- FOUND commit: `7236113`
