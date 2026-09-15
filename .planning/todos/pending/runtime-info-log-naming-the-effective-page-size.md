---
created: 2026-08-19T00:00:00Z
title: "Runtime INFO log naming the effective page size firmware actually used"
area: firmware
resolves_phase: 194
files:
  - firestarter/src/proms/eeprom_28c.cpp
  - firestarter/tools/catalog/messages.toml
  - firestarter/include/messages.h
---

## Problem

Phase 149 delivers a per-chip `page_size` to firmware (PGSZ-01/PGSZ-02), with a firmware-side
fallback to the `PAGE_SIZE 64` floor when the value is absent, zero, or not a power of two in
range (D-07). Right now, nothing in the write path reports **which** page size a given write
session actually used -- the host sends it, the firmware applies it (or falls back), and neither
side surfaces that decision back to the operator or to a community `dev test` report.

## The follow-up (D-09)

A runtime `INFO`-level log line naming the effective page size the firmware actually used for a
given write, so a future community `dev test` report can show its own write granularity --
directly useful for re-triaging gh#21 (AT28C256) and any future AT28C-family report, since the
report would then be self-describing about which page size the firmware applied rather than
requiring a source read to infer it.

## Why declined in this phase

**Flash cost.** A new log line needs a new message ID: an entry in
`firestarter/tools/catalog/messages.toml` plus a PROGMEM string, against a leonardo flash budget
whose MERGE-05 headroom was measured at **exactly 0 B** before this phase funded the
page-size-seam exemption (149-06), and remains fully consumed by that exemption afterward (see
`scripts/baseline/size_baseline.json`'s `meta.deltas_vs_base01.leonardo` clause). Adding a new
message here would need its own separately-adjudicated MERGE-05 exemption, which is out of this
phase's scope.

## Edit point (for whoever picks this up)

**The catalog, never `include/messages.h`.** `include/messages.h` is codegen-generated and
ID-only, with a CI drift gate against `firestarter/tools/catalog/messages.toml` -- a wording-only
change there produces zero diff and is never hand-edited. The correct edit point is a new
`[[debug.messages]]` entry appended to `firestarter/tools/catalog/messages.toml:1124` (the file's
current tail, one `[[debug.messages]]` block per message), followed by the codegen run that
regenerates `messages.h`. The log call site would live in `firestarter/src/proms/eeprom_28c.cpp:43`
(`AT28C_PAGE_SIZE_FALLBACK`), where the write session already resolves the effective per-chip
page size.

## Tied to

The gh#21 re-run request: F-01 (root-cause pass) already made every `dev test` report
firmware-attributable via `fw_board_identity`; this INFO log would make it page-size-attributable
too, worth having specifically when a reporter is asked for a fresh run.

## Filed by

Phase 149 (dual-repo lockstep), D-09 follow-up, Plan 07.
