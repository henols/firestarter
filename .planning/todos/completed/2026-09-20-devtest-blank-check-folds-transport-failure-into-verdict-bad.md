---
created: 2026-09-20T00:00:00Z
title: A transport failure during dev test's blank-check step reads as VERDICT_BAD, not a hardware verdict
area: host
resolves_phase: 206
source: .planning/milestones/v1.41-phases/202-one-comparison-engine-on-the-host/202-REVIEW.md § WR-02
files:
  - firestarter_app/firestarter/chip_test.py (_dispatch_step's OP_BLANK_CHECK arm, and the comment that defers the 3-way verdict to phase 206)
  - firestarter_app/firestarter/eprom_operations.py (check_eprom_blank's 0/1/2 return contract)
---

## Problem

`_dispatch_step`'s `OP_BLANK_CHECK` arm does `is_ok = operator.check_eprom_blank(...) == 0`, which
folds verdict `1` (not blank) and verdict `2` (refusal or failure) into one "not ok" branch that
becomes `VERDICT_BAD` for any non-UV-prewrite chip.

Before phase 202 this was unambiguous: `check_eprom_blank` returned a bool, and verdict 2 did not
exist as a concept. Phase 202 gave it an int contract (0 blank / 1 not blank / 2 refusal) and put
it on `COMMAND_READ`, so it can now fail for reasons that have nothing to do with the chip.

The SRAM/FRAM refusal specifically cannot reach this path — `derive_plan` marks that step
`supported=False` before dispatch. A genuine transport or hardware failure during the blank check's
read is *not* ruled out, and it is what this fold-in silently absorbs. A `dev test` report then
says the chip is not blank when the real cause was a dropped connection, which points the reader at
the part instead of the cable.

## Fix

Phase 206 owns the real migration to the 3-way verdict; that is the proper fix and the code already
says so.

Until then, extend the existing deferral comment by one line to name the residual risk explicitly —
that a genuine transport failure during the blank-check step reads as `VERDICT_BAD` rather than a
distinct hardware verdict — so a future reader does not have to re-derive it from the return
contract.

## Why it was not fixed in phase 202

Out of the phase's stated scope and already deferred in-code to phase 206. It blocks no phase 202
must-have; the phase verified 38/38 with it open.
