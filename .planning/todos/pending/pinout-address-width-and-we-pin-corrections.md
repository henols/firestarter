---
created: 2026-08-22T00:00:00Z
title: "29 chips ride a pinout too narrow or wrong for them — AM27C080 gets 13V on A19, AT28C040 addresses 64KB of 512KB, and all of them are support_status: supported"
area: host
resolves_phase: unassigned
files:
  - firestarter_app/firestarter/data/pinouts.json
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/check_dispatch.py
  - firestarter_app/tests/
---

## Problem

Five groups of chips — **29 rows, every one `support_status: "supported"`** and reachable by
`firestarter <chip> write` today — are routed to a `pinouts.json` family whose address bus is
too narrow for the part, whose write-strobe pin is wrong, or whose VPP pin lands on an
address line.

Found mechanically, not by inspection: infoic.xml's own `<maps>` table (per-chip bonded-pin
connectivity, indexed by the `pin_map` low byte the generator already parses) crossed with
one-rom's `chip-types.json` (per-layout pin function). Method, validation of the oracle, and
reproduction: [`notes/infoic-maps-onerom-three-way-join.md`](../../notes/infoic-maps-onerom-three-way-join.md).
**Read that first** — in particular §4, because a join keyed on the raw `protocol_id` instead
of `flags & 0x10` re-authors the WARNING-5 hazard, and that trap is live for anyone
regenerating pin maps from these sources.

Not previously recorded: `grep -rn "27C080\|SST28SF040\|AT28C040" .planning/` returns nothing
outside these artifacts.

## The five groups

Address-line requirement is `(size - 1).bit_length()`. "Truth" columns are agreed by both
`<maps>` (which pins are bonded) and one-rom (what each does).

| # | Chips | Currently | Truth | Consequence |
|---|---|---|---|---|
| 1 | `AM27C080`, `AT27C080`, `MX27C8000` (1M, algo `0x08`) | `DIP32_STD` — 19 addr lines, **`vpp-pin: [1]`** | 20 lines with **A19 on pin 1**; **VPP on pin 24**, **PGM on pin 22** (one-rom `27C080`: `pgm 22`, `vpp 24`) | `configure_eprom` asserts VPP → **13V onto A19**. Address bus also one line short. |
| 2 | `SST28SF040`, `SST28SF040A`, `SST28LF040(A)`, `SST28VF040` (512K, algo `0x10`) | `DIP32_STD` — **`vpp-pin: [1]`** | A18 on pin 1, WE on pin 31 (one-rom `SST39SF040`) | Same shape as the 2026-05 `SST39SF040` defect that read as dead silicon on the bench (`a332464`). Address bus scrambled regardless of whether the `0x10` handler asserts VPP — **not traced, do not assume it does not**. |
| 3 | `AT28C040`, `AT28MC040`, `CAT28C040`, `WE512K8` (512K, algo `0x0D`) | `DIP32_28C512_EEPROM` — **16 addr lines**, `rw-pin: [30]` | **19 lines** (A18 on 1, A17 on 30), **WE on 31** | Reaches only the low 64KB of a 512KB part, and strobes WE onto A17. No VPP on this family, so no damage path — functionally broken only. |
| 4 | `AT28C010`, `AT28LV010`, `AT28MC010` + 7 more (128K); `AT28MC020`, `CAT28C020`, `WE256K8` (256K) | same family, 16 addr lines, `rw-pin: [30]` | 17 and 18 lines; **WE on 31** | Same class as #3. `<maps>` shows pin 31 bonded and pin 30 NC on every one of them. |
| 5 | `AT27C011`, `D27011`, `D27C011` (128K in **DIP28**) | `DIP28_2764` — 14 addr lines | 17 lines | 1Mbit part on an 8K/16K layout. |

Only `CAT28C512@DIP32` (64K) actually fits `DIP32_28C512_EEPROM` — **17 of its 18 rows are
mis-provisioned.**

### Why one-rom alone did not catch #3 and #4

[`notes/onerom-pinout-external-corroboration.md`](../../notes/onerom-pinout-external-corroboration.md)
records `DIP32_28C512_EEPROM` as byte-identical to one-rom `28C512`, `rw-pin` included. It
is — but **one-rom is the source that is wrong here.** Its own `SST39SF040`, on the identical
JEDEC 32-pin layout, puts `control.write` at **31**; its `28C512` says **30** and models only
the 64K part, where pin 30 is NC anyway. The agreement was two sources sharing one error, and
that family is one of the two the note already labels **provenance-ambiguous** (`ff70920`,
authored the same day as the cross-check).

`<maps>` breaks the tie because it is per-chip and mechanical rather than per-family and
hand-compared: `maps[9]` for `AT28C010` lists pin 31 bonded and pin 30 not.

## Why no existing gate sees this

- `tools/check_dispatch.py` asserts *no chip routes to `configure_eprom` on a pinout with no
  `vpp-pin`*. Groups 1 and 2 are the **inverse** — a `vpp-pin` that points at an address
  line — which the structural guard cannot express.
- `chip_database.json` is generated, so no reviewer diffs pin assignments per chip.
- `pinouts.json` is a hand-maintained **input** (`tools/build_db.py:204`) and gets no
  protection from the generator's decode tests — the gap
  [`todos/pending/onerom-pinout-external-corroboration-gate.md`](onerom-pinout-external-corroboration-gate.md)
  was filed to close.
- Nothing anywhere compares a row's address-bus width against its `code_memory_size`.

## What to build

Ordered by severity. Group 1 first — it is the only one where a wrong pin carries programming
voltage on an algorithm known to assert it.

1. **Width gate first, as a RED test.** For every row in `chip_database.json`, assert
   `len(address-bus-pins) >= (size_bytes - 1).bit_length()`. This fails today on groups 1, 3,
   4 and 5 — land it red, then fix. Cheap, total, and independent of both external sources.
2. **Connectivity gate.** For every row with `pin_map & 0xFF` resolving to a non-`map[0]`
   entry, assert `{pins assigned by pinouts.json} == {pins bonded per <maps>}`, both
   directions. Over-assignment catches a function on an NC pin; under-assignment is what
   caught groups 3 and 4. Note the family-level limit in the method note §1 — the connected
   set is an upper bound for the smallest member of a map group, so scope the equality to the
   largest member or assert `assigned ⊆ bonded` plus a separate width check.
3. **VPP-sanity gate**, closing the `check_dispatch.py` inverse: a family's `vpp-pin` must
   not appear in any row's sliced `address-bus-pins`. This is the guard that would have
   caught group 1.
4. **Correct `pinouts.json`.** New family for the 27C080 class (A19 on 1, VPP on 24, PGM on
   22 — CE and OE displaced, so it is genuinely a new layout, not a widened `DIP32_STD`).
   Re-route groups 2 and 3 onto the `SST39SF040`-shaped 32-pin layout. Widen or split the
   28C0x0 family and move its `rw-pin` to 31. New family for the DIP28 27C011 class.
5. **Adopt address-bus slicing in the generator** so the width defects cannot recur:
   layouts hold the ordered superset, the generator emits
   `address-bus-pins[:(size-1).bit_length()]`. This is the same change that deletes
   `MAX_27C020_SIZE` — see
   [`todos/pending/derive-away-max-27c020-size-hardcode.md`](derive-away-max-27c020-size-hardcode.md);
   sequence them together, the slice is a prerequisite for both.

## Verification limits — state these, do not paper over them

All five groups are **software-proven and unvalidated on silicon.** None of these parts is
in the bench inventory as far as `.planning/notes/VALIDATED-EPROMS.md` records. The evidence is two
independent documentary sources agreeing, plus datasheet-consistent address arithmetic — the
same evidence class that fixed `SST39SF040` in 2026-05 and was later borne out on the bench.

Group 2's damage question specifically needs the `0x10` / `configure_flash` firmware path
traced for a VPP assert before the hazard is described either way.
