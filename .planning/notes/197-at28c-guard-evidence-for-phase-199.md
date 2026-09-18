# AT28C DIP24 hardware-damage guard — evidence for Phase 199

Phase 197, plan 197-04. D-07 as amended by D-15: Phase 197 deletes the `_AT28C_DIP24_NAMES`
part-number list from `firestarter_app/tools/build_db.py` and its consuming arm, but does **not**
narrow or delete the hardware-damage guard above it — that guard is what actually selects these
nine rows, and narrowing it is safety-adjacent work the operator has not ruled on. This note is
what Phase 199 inherits instead of having to re-derive it: the measured pinout/flags table, why
the name list's deletion achieves nothing beyond a reason-string swap, the operator ruling that
routes the guard narrowing here, and the exact list of what breaks the moment the guard is
narrowed.

## Search method (reproducible)

The 19-row table below was produced by querying the pinned `infoic.xml` at minipro commit
`a8efaedc236c1d9718bd28299dfbb99536b010ff` (the exact URL `build_db.py`'s `MINIPRO_XML_URL`
fetches) for every `<ic>` element whose decoded fields satisfy all three of:

- `pin_count == 24` — computed as `(int(ic.get("package_details"), 16) & 0x7F000000) >> 24`
- `pm_idx == 23` — computed as `int(ic.get("pin_map", "0"), 16) & 0xFF`
- `variant_lo == 0x10` — computed as `int(ic.get("variant"), 16) & 0xFF`

Those three conditions are exactly what `resolve_pinout_key` uses to select the `DIP24_2816`
pinout family (see `firestarter_app/tools/build_db.py`, the `pin_count == 24` branch). For each
matching `<ic>`, the upstream `protocol_id` and `flags` attributes were read directly and
`flags & 0x10` (the electrically-erasable bit) computed. Membership in the now-deleted
`_AT28C_DIP24_NAMES` set was checked against the comma-split, `@`-suffix-stripped alias list.
This method and its 19-row output were produced during `/gsd-plan-phase 197`'s research pass
(`197-RESEARCH.md` § "C-1 — D-07 achieves none of its stated effect") and are reproduced here
verbatim for Phase 199's use.

## The 19-row table

All 19 rows arrive as upstream `protocol_id 0x0b`. The split between the nine names in the
deleted list and the other ten is **exactly** `flags & 0x10`, with zero exceptions.

| Row | upstream `protocol_id` | upstream `flags` | `flags & 0x10` | in deleted `_AT28C_DIP24_NAMES` |
|---|---|---|---|---|
| AMD/AM28C16A | 0x0b | 0x000000 | False | no |
| ATMEL/AT28C04,AT28HC04 | 0x0b | 0x000010 | **True** | **yes** |
| ATMEL/AT28C04E,AT28C04F | 0x0b | 0x000010 | **True** | **yes** |
| ATMEL/AT28C16,AT28HC16,AT28HC16L | 0x0b | 0x000010 | **True** | **yes** |
| ATMEL/AT28C16E,AT28C16F | 0x0b | 0x000010 | **True** | **yes** |
| CATALYST(CSI)/CAT28C16A,CAT28C16AI | 0x0b | 0x000000 | False | no |
| EXEL/XL2804A | 0x0b | 0x000000 | False | no |
| EXEL/XL2816A,XLE28C16A,XLS28C16A | 0x0b | 0x000000 | False | no |
| EXEL/XLE28C16B,XLS28C16B | 0x0b | 0x000000 | False | no |
| MICROCHIP memory/2804 | 0x0b | 0x000000 | False | no |
| MICROCHIP memory/2816 | 0x0b | 0x000000 | False | no |
| MICROCHIP memory/28C04A | 0x0b | 0x000010 | **True** | **yes** |
| MICROCHIP memory/28C04AF | 0x0b | 0x000010 | **True** | **yes** |
| MICROCHIP memory/28C16A | 0x0b | 0x000010 | **True** | **yes** |
| MICROCHIP memory/28C16AF | 0x0b | 0x000010 | **True** | **yes** |
| NEC/UPD28C04 | 0x0b | 0x000010 | **True** | **yes** |
| XICOR/X2804A,X2804AI | 0x0b | 0x000000 | False | no |
| XICOR/X2816A | 0x0b | 0x000000 | False | no |
| XICOR/X2816B,X2816C | 0x0b | 0x000000 | False | no |

9 rows read `flags & 0x10 == True` and 9 rows were named in the deleted list — the same 9 rows,
in both columns, every time.

## Per-fact disposition

- **VERDICT — the name list and the guard select the identical row set.** The guard at
  `build_db.py`'s hardware-damage check fires on `pin_count == 24 and proto_id in (0x07, 0x08,
  0x0B) and (flags & 0x10)`. All 19 rows arrive as `proto_id 0x0b`, so the guard's condition
  reduces to `flags & 0x10` alone — which is exactly the erasable bit that produces this table's
  9-vs-10 split. The now-deleted name list was never doing independent selection work; it was
  reproducing, by an enumerated list of part names, a selection the guard already made by a flags
  bit. **Deleting the name list therefore changes only the `unsupported_reason` string** on these
  nine rows — from the retired wiki-adapter wording to the guard's own text — and flips zero rows
  to `supported`. This is measured, not inferred: a full simulated regeneration with the name
  list deleted reproduces `support_status: adapter-required` on all nine rows, unchanged.

- **VERDICT — these nine rows do not receive the pinout the guard's own comment names.** The guard
  resolves to `DIP24_2816`, not `DIP24_2716`. `resolve_pinout_key` selects `DIP24_2816` from
  `pm_idx == 23` and `variant_lo == 0x10` alone, independently of `proto_id` — so the guard's
  pre-emptive demotion of `proto_id` to `NON_DISPATCHABLE_ALGO` never actually changes which
  pinout these rows land on. `firestarter/data/pinouts.json` defines `DIP24_2816` with
  `"rw-pin": [21]` and **no `vpp-pin`** at all (its own `comment` field states this explicitly:
  *"NO vpp-pin — configure_eeprom28c is 5V-only ... Pin 21=WE, NOT VPP"*). `DIP24_2716`, by
  contrast, carries `"vpp-pin": [21]`. On the pinout these nine rows actually resolve to, socket
  pin 21 is the write-enable strobe, not the 12 V VPP rail — so the guard's own stated hazard,
  "12V onto a 5V write-enable pin" via the `DIP24_2716` layout, **does not materialise for these
  rows on the pinout they receive.**

- **VERDICT — the guard's pre-emptive algorithm demotion is moot for these rows regardless.**
  `classify()` re-promotes the protocol immediately after `resolve_pinout_key` runs: arm 1 of the
  5V-EEPROM promotion (`pinout_key is DIP24_2816` → promote to algorithm `0x0D` for any protocol)
  fires unconditionally for `DIP24_2816` rows, overwriting whatever the guard set `proto_id` to.
  So even the guard's dispatch-side effect (demoting to `NON_DISPATCHABLE_ALGO`) is superseded by
  `classify()` before `chip_entry` is built — the only effect that survives to the emitted row is
  the `support_status`/`unsupported_reason` pair the guard writes directly.

## Operator ruling (verbatim)

Recorded during `/gsd-plan-phase 197`, asked and answered: **delete the name list now; route the
guard narrowing to Phase 199.** Phase 197 still satisfies OVR-05 and its own success criterion
that no part-number literal survives in the generator — the nine rows keep `adapter-required`
with the guard's own reason text, unchanged in effect, changed only in wording.

The operator's framing from `197-CONTEXT.md` § "Specific Ideas", verbatim: *"No adapter shall be
needed at all, but its only 2.2 and above that supports it by hardware, but that is not a real
blocker, the other versions can do the same with a wire, but that's nothing to care about here."*
The shield-revision distinction (Rev 2.2+ supports these parts in hardware; earlier revisions can
with a wire) is explicitly **not** to be modelled in the database — `support_status` is a
per-part, revision-agnostic field, and CONTEXT.md's domain boundary keeps per-revision modelling
out of this milestone entirely.

## Honesty limit

This is a pinout-and-flags analysis of the pinned `infoic.xml` and the shipped `pinouts.json`,
cross-checked against the generator's own dispatch order (`resolve_pinout_key` then `classify()`).
It is **not a bench measurement.** No AT28C part has been written, read, or erased on any shield
revision as part of Phase 197, and `197-CONTEXT.md`'s deferred list records explicitly that no
bench run is gated on this finding. The conclusion that "the hazard does not materialise" rests on
the pinout definition in `pinouts.json` being an accurate description of the physical wiring — a
description this phase did not independently verify against a shield or a chip on the bench.

## What Phase 199 must decide

1. **Whether to narrow the guard's condition** (`pin_count == 24 and proto_id in (0x07, 0x08,
   0x0B) and (flags & 0x10)`) so these nine rows stop matching it and become `supported` —
   consistent with the operator's stated position that no adapter is needed at all on Rev 2.2+
   hardware.
2. **If narrowed, what happens to the nine `unsupported_reason` strings** the guard currently
   writes — they disappear entirely if the rows become `supported`, since `unsupported_reason` is
   only set on non-`supported` rows.
3. **The three test legs that stay green in Phase 197 precisely because the guard is untouched,
   and that all three redden together the moment it is narrowed:**
   - `tests/test_sdp_capability.py` — its nine-row `adapter-required` assertion
   - `tests/test_chip_resolver.py:87` — `resolve_chip("AT28C04")` raising `ChipNotImplementedError`
   - `tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings::test_at28c16_named_arm_reason_mentions_adapter_doc`
     (197-04's rewritten version, now pinning the guard's own wording — which would itself need
     rewriting again if the guard's reason text disappears)

   None of these three needed to change in Phase 197 because the guard's behavior did not change.
   Narrowing the guard changes what all three assert against, and Phase 199 must rewrite all three
   in the same change that narrows the guard — not as an afterthought.

---

*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Written: 2026-09-18*
