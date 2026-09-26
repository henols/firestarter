---
created: 2026-09-16T00:00:00Z
title: "dev test's fixed 256-byte write region refuses on the two protocol 0x05 parts with page size 512"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/firestarter/chip_test.py
---

## Problem

`dev test`'s chip-test engine writes a fixed 256 bytes at address 0 for every non-UV part
(`_WRITE_REGION_START = 0`, `_WRITE_REGION_LENGTH = 256`). Measured directly against
`chip_database.json`'s 27 protocol-`0x05` rows: this is a whole number of pages -- and therefore
unaffected by Phase 195's alignment refusal -- for **25 of 27 rows** (page size in `{64, 128,
256}`), including all three protocol-`0x05` validated parts (`W29C020`, `W29C040`, `AE29F2008`).
It becomes a **refused partial page** on the remaining **2 of 27 rows**, both recording page size
512: `AT29BV040,AT29LV040` and `AT29C040`. Neither of those two parts has ever been tested on
silicon.

## Why Phase 195 did not fix this

Changing the write region's length changes what every community validation run measures --
`dev test`'s region is what every `dev test` submission against a protocol `0x05` part actually
exercises. That is a ledger-affecting decision with consequences for every future `dev test` run,
not a safety fix, and it must not ride along with the alignment-refusal change that landed in
Phase 195. Folding it in would have made one commit responsible for two different kinds of
correctness: "the write can no longer erase bytes outside its range" and "what `dev test` measures
changed."

## The proposal

Round the write region's length up to the part's recorded page size, where one is recorded, rather
than using a hard-coded 256 for every part. For the 25 rows already at a page size dividing 256
this is a no-op; for the 2 rows at page size 512 it would extend the region to 512 bytes so the
fixed-region write stays aligned under Phase 195's refusal.

## Filed by

Phase 195 (partial writes stop destroying the page), D-12, Plan 04.

## Closed by
