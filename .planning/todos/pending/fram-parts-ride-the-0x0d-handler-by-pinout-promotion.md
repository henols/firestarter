---
created: 2026-08-19T00:00:00Z
title: "FM28V020 and MB85R256H (FRAM) ride the 0x0D EEPROM handler by pinout promotion -- a classification question"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/tools/build_db.py
  - firestarter/src/proms/eeprom_28c.cpp
  - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-CONTEXT.md
---

## Problem

Two FRAM parts reach `configure_eeprom28c()` (protocol `0x0D`) purely through `classify()`'s
pinout-promotion arm 2 (`firestarter_app/tools/build_db.py:371-386`), the same mechanism the
`promoted-0x0d-rows-keep-the-64-byte-floor.md` todo covers for page-size purposes. This is filed
as a **separate** todo deliberately: it is a **classification question** (should these parts be
routed to the 28C EEPROM handler at all), not a page-size question.

## The two parts (measured)

- **CYPRESS `FM28V020`** -- upstream `protocol_id 0x07`, upstream `page_size 128`, `vcc_mv 5000`,
  `vpp_mv 12000`.
- **FUJITSU `MB85R256H`** -- upstream `protocol_id 0x07`, upstream `page_size 256`, `vcc_mv
  3300`, `vpp_mv 12000`.

Both are typed `EEPROM` in the database and both reach the `0x0D` handler by the same
`DIP28_28C64`/`DIP28_28C256`-pinout promotion described in the sibling todo above.

## Why this is a genuine question, not a bug

FRAM (ferroelectric RAM) has **no page buffer and no internal write cycle** -- every byte write
completes immediately and independently, unlike true 28C EEPROM's page-write-then-poll model.
A delivered `page_size` would therefore be **meaningless** for these two parts: there is no
buffer boundary for it to describe. D-01's provenance rule (deliver only where the upstream
record's own `protocol_id` is `0x0D`) already **excludes both of these parts by construction** --
neither carries an upstream `0x0D` record, so neither is a D-01 mover -- which is the concrete
harm the provenance rule was built to prevent. What D-01 does *not* answer is the prior
question: should these two parts be dispatched to `configure_eeprom28c()` at all, given they are
electrically FRAM, not EEPROM? `MB85R256H`'s 3.3 V `vcc_mv` also makes it electrically distinct
from the 5 V 28C family the handler was designed around.

## What would close it

An independent classification pass over the database's FRAM-typed parts that reach `0x0D` by
pinout promotion, to decide (a) whether they should be re-typed/re-routed to a dedicated FRAM
path, or (b) whether riding the existing EEPROM handler is electrically harmless for FRAM and can
stay as-is with the classification simply documented. Not attempted in this phase -- no FRAM part
exists in operator inventory (Evidence Ceiling, `PROJECT.md` §Current Milestone: v1.32) and the
question is orthogonal to the page-size seam this phase delivers.

## Filed by

Phase 149 (dual-repo lockstep), D-04 deliverable 2, Plan 07.
