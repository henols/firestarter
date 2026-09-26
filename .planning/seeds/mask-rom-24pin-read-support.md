---
title: 24/28-pin mask ROM read support (2316 / 2332 / 2364 / 23xxx)
trigger_condition: Next read-path or new-chip-family milestone opens (NOT during a write-path milestone — this is read-only scope and would dilute a write-path goal)
planted_date: 2026-08-20
status: dormant
---

# 24/28-pin mask ROM read support (2316 / 2332 / 2364 / 23xxx)

Firestarter has **zero** coverage of the classic mask-ROM family — the parts that actually
sit in Commodore, Atari and arcade boards. `chip_database.json` has no row matching `2316`,
`2332`, `2364`, `23128`, `23256`, `23512`, `231024`, `23C1001`, `23C1010`, or any of their
aliases (`9316`, `9332`, `4732`, `4764`, `MCM68764`, `MCM68A764`, `MK36000`, `MM52164`,
`TC531000`, `MX23C1000`, …). Checked against all 953 part numbers + aliases in the database
on 2026-08-20 — not one hit.

These are **read-only** parts: no VPP, no programming algorithm, no erase, no protection
state. Single 5 V rail. That makes them the cheapest possible family to add — the entire
delivery is a pin map plus a read path we already have, with **no write-path or VPP risk
whatsoever**. It is also the class of chip a retro user is most likely to want to dump
before replacing, and `MCM68764`/`2364` in particular comes up constantly in that community.

## Why this is now cheap: the pin maps are already published

[One ROM](https://github.com/piersfinlayson/one-rom)'s
[`rust/config/json/chip-types.json`](https://github.com/piersfinlayson/one-rom/blob/main/rust/config/json/chip-types.json)
carries all of them in a schema that maps almost 1:1 onto our `pinouts.json` — ordered
`address` A0..An, `data` D0..D7, `control` with pin + polarity, `power` VCC/GND. MIT-licensed
(see the licensing analysis in
[`notes/onerom-pinout-external-corroboration.md`](../notes/onerom-pinout-external-corroboration.md)),
and independently validated by the emulator working in-circuit in real machines — which is
*read-path* evidence, exactly the axis this seed needs. The same file's 24-pin siblings
(`2716`, `2732`, `6116`, `28C16`) were cross-checked against our existing families and came
back byte-identical, so the source has demonstrated fidelity on this footprint.

Available, with their control pins:

| type | pins | size | CS lines (pin) | aliases |
|---|---|---|---|---|
| `2316` | 24 | 2 KB | cs1@20, cs2@18, cs3@21 | 9316, 9316A |
| `2332` | 24 | 4 KB | cs1@20, cs2@21 | 9332, 4732 |
| `2364` | 24 | 8 KB | cs1@20 | 4764, MCM68764, MCM68A764, MCM68364, MCM68A364, MM52164, MK36000 |
| `23128` | 28 | 16 KB | — | — |
| `23256` | 28 | 32 KB | cs1@20, cs2@22 | — |
| `23512` | 28 | 64 KB | — | — |
| `231024` | 28 | 128 KB | — | TC531000, 23C1000, 23C1000A, MX23C1000 |
| `23QL384` / `23QL512` | 28 | 48/64 KB | — | — |

## The one real design problem: configurable CS polarity

Every one of these carries its chip-selects as `"type": "configurable"` — the polarity is a
**mask option chosen by the ROM's original manufacturer**, not a property of the part number.
A `2364` in one machine wants CS active-low; the same part number in another wants active-high.
This is precisely why One ROM exposes it as configuration rather than baking it in.

Our pinout schema cannot express that today. `firestarter/database.py:297` handles
`static-high-pins` only — there is **no `static-low-pins`**. So before this is plannable,
decide:

1. **Does an unassigned bus line already idle at the level a low-asserted CS needs?** If the
   RURP latch leaves unassigned lines low, active-low CS2/CS3 may already be asserted by
   omission — in which case only the *active-high* case needs new machinery. Verify in code
   (`database.py` bus-config construction + the firmware's control-register path), don't
   assume; [[reference_held_rail_dtr_reset_hold_script]] is the precedent that routing
   questions here are usually answerable in source.
2. **Where does per-sample polarity live?** It cannot be a `chip_database.json` field —
   that file is generated from `infoic.xml` and the generator may not invent fields without
   upstream proof ([[feedback_generator_no_fields_without_infoic_proof]]), and infoic has no
   mask-option data. Candidates: distinct pinout families per polarity combination
   (`DIP24_2364_CSLO` / `DIP24_2364_CSHI`), a CLI flag on `read`, or
   `tools/extra_chips.json` — the existing non-upstream supplement, precedent set by
   `94ea3b5` (86-04) which added `2516`/`2532` + `DIP24_2532` that way. The supplement route
   looks strongest: these parts are genuinely not in infoic, same as 2516/2532.
3. **Scope the polarity guess.** A wrong CS polarity on a read is non-destructive (worst case
   a blank or garbage dump), which is what makes this a low-risk family — but a silent bad
   dump is worse than a refusal. Decide whether an unspecified polarity refuses, or reads and
   loudly flags the result as polarity-unconfirmed.

## Explicitly out of scope

The same upstream file also carries `2704`/`2708` (3-rail, need −5 V and +12 V — the RURP
shield cannot source them), `HM7641` (bipolar fusible-link PROM), and the 40-pin 16-bit
`27C200`/`27C400` (no 40-pin socket, 16-bit data bus). Do not let those ride along; they are
each a hardware problem, not a pin-map problem. `27C301` and `27C080` are 32-pin EPROMs and
belong to a *write*-path discussion instead.
