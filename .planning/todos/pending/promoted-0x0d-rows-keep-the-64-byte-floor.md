---
created: 2026-08-19T00:00:00Z
title: "66 promoted 0x0D rows keep the 64-byte page floor -- floor safety is unproven for 11 of them"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/tools/build_db.py
  - firestarter/src/proms/eeprom_28c.cpp
  - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-CONTEXT.md
---

## Problem

Phase 149 / PGSZ-01 delivers a per-chip `page_size` to firmware only where the upstream `<ic>`
record's own `protocol_id` is `0x0D` (D-01) -- 18 of `chip_database.json`'s 84 `algorithm: 13`
rows qualify. The remaining **66 rows never carried a `0x0D` page value at all**: they arrived
under a different upstream algorithm and were promoted into the `0x0D` handler by
`classify()` **arm 2** (`firestarter_app/tools/build_db.py:371-386`), which routes any
`0x07`/`0x08`/`0x0B` (EPROM-family) part on a `DIP24_2816` / `DIP28_28C64` / `DIP28_28C256`
pinout (or `DIP28_2764` with the CMOS flag set) into the 28C EEPROM handler. Their `page_size`
field is whatever that OTHER algorithm's own record happened to carry -- a reading a
28C-page-write buffer never produced.

## Measured (this phase, D-04)

Full join of all 84 `algorithm: 13` rows against the pinned upstream XML, partitioned by
upstream `protocol_id` and `page_size` value (all 84 matched, zero unmatched):

| upstream `protocol_id` | `page_size` values -> counts | row total |
|---|---|---|
| `0x07` | 1->14 · 16->1 · 32->8 · 64->22 · 128->1 · 256->1 | 47 |
| `0x0B` | 1->17 · 16->2 | 19 |
| `0x0D` | 64->3 · 128->15 | 18 |

Only the 18 `0x0D` rows are upstream-native; their page sizes are exactly the CONFIRMED field
dictionary's documented band ("typically 64 or 128 bytes for 28C-family") and are the ones
PGSZ-01/D-01 delivers.

The remaining **66** rows (47 + 19 = 66, matching `84 - 18`) are promoted, and split by their
raw page value:

- **31** at raw `1` -- 14 from upstream `0x07`, 17 from upstream `0x0B`
- **8** at raw `32` -- all from upstream `0x07`
- **3** at raw `16` -- 1 from upstream `0x07`, 2 from upstream `0x0B`
- **1** at raw `256` -- from upstream `0x07`
- **1** at raw `128` -- from upstream `0x07`
- (the remaining 22 promoted `0x07` rows at raw `64` are numerically indistinguishable from the
  correct 64-byte floor and are not a risk this todo tracks separately)

31 + 8 + 3 + 1 + 1 + 22 = 66.

## Why they keep the 64 floor

A `page_size` value read out of a record filed under another algorithm is not evidence about a
28C page-write buffer -- `0x07`/`0x0B` (UV-EPROM) records have no page-write mechanism at all, so
whatever integer sits in that field describes something else (or nothing) for these parts. D-01
therefore does not deliver any of these 66 values to firmware; all 66 keep the existing
`PAGE_SIZE 64` floor (`firestarter/src/proms/eeprom_28c.cpp:19-33`).

**Precision matters for the safety claim.** For the **31** rows at raw `1` and the **1** at `256`
and the **1** at `128`, the raw value is either obviously not a page size (`1`) or wildly larger
than the shipped 28C family band (`256`), so the 64-byte floor is very likely safe. But for the
**11** rows at 16/32 (3 + 8), the raw value sits inside the plausible 28C page-size range, so it
is **not disproven** that the real chip's page could be smaller than 64 -- the floor's safety for
those 11 rows is **unproven**, not disproven. `eeprom_28c.cpp`'s comment was corrected in this
phase to say exactly that (D-04 deliverable 3).

## What would close it

Any future attempt to deliver a real page size to these 66 rows -- and especially the 11 at
16/32 -- needs either **datasheet curation per family** (looking up each part's actual 28C page
size independently of `infoic.xml`) or a **new corroboration axis**, because `infoic.xml` does
not supply one: `write_buffer_size`, `read_buffer_size` and `pages_per_block` were all measured
during this phase's research and found not to corroborate `page_size` for these rows.

**Explicitly out of scope by `REQUIREMENTS.md` §Out of Scope / DATA-04:** extending
`_PAGE_SIZE_BY_PART` (or any equivalent per-chip guess table) to cover these 66 rows without that
independent corroboration.

## Filed by

Phase 149 (dual-repo lockstep), D-04 deliverable 1, Plan 07.
