---
created: 2026-06-24T07:41:26Z
title: Skip VPP error/warning checks when VPP is unused (reads/blank-checks)
area: firmware
resolves_phase: 84
files:
  - firestarter/src/firestarter.cpp (read/blank-check init VPP gate)
  - firestarter/src/rurp_shield.cpp (hw_read_voltage / VPP measurement)
  - firestarter_app/firestarter/eprom_operations.py (read/blank-check path)
  - .planning/milestones/v1.15-artifacts/bench/EVIDENCE.md (Phase 81 anomaly evidence)
---

## Problem

During operations that do NOT apply VPP — `read` and `blank-check` — the firmware still
measures the VPP rail and either **refuses** the operation or emits a **warning**, even
though VPP is irrelevant to a read. This caused real friction in the Phase 81 bench sweep:

- **Chip 1 (W27C512): read-init REFUSED** with `VPP is high: 18.8V > 12.0V` — blocked the
  read entirely until a board reset cleared the rail. A read needs no VPP, so this gate
  should not fire.
- **ST M27C512 / 2516: benign `VPP is low` warnings** on reads (11.9V, 15.3V) — noise,
  since reads don't use VPP.
- **2516 (0x0B Legacy, shared OE/VPP pin): read UNSTABLE** (3 distinct SHAs across 3
  reseat cycles) with VPP pinned at 15.3V on the shared OE/VPP pin — the VPP-rail state
  appears to actively corrupt the read on the shared-pin protocol.

User directive (2026-06-24): "don't check or report errors/warnings when VPP isn't used."

## Solution

TBD — candidate for **Phase 84 FIX-01**. Likely:
1. Gate the VPP voltage check (`VPP is high/low`) on operations that actually drive VPP
   (write/program/erase), not on read/blank-check.
2. For shared-OE/VPP protocols (0x0B Legacy), investigate how the VPP rail is driven
   during a read and ensure the OE/VPP shared pin is held at a clean read level (not a
   floating mid-rail ~15V) so reads are stable — this is the load-bearing fix for the
   2516 read instability that currently GATES Phase 83.
3. Keep parity between host (`eprom_operations.py`) and firmware (`firestarter.cpp`) checks.

Related: the Phase 81 EVIDENCE 2516 ANOMALY + chip-1 refusal; the VPP/VPE rail behavior
documented in v1.14 Phase 79 (rail correction). Does NOT block the Phase 81 read baseline
(recorded as anomalies + Phase 83 gate).
