# Modified Rev 0 — Hardware Modification Record

> Operator's third RURP shield: a stock upstream Rev 0 board (`parent = upstream-486f3d1`)
> carrying hardware-bug-A/B rework (cuts + jumpers). This file was a long-standing TBD stub
> (Phase 32 deferred it; Phase 35 follow-up #4 never landed because operator photos were
> blocked; v1.34 Phase 164 was scoped to finish it and closed unrun). Created in Phase 44
> (Plan 04, bench session 1). **Upgraded from stub 2026-08-29** — desk work only, no
> photographs taken.
>
> **Provenance discipline:** every row is tagged **[attested]** (sourced from prior operator
> statements / `.planning/milestones/v1.7-SHIELD-REVS.md` with a citation), **[traced]** (read off a
> photograph or probe against the schematic), or **[uncaptured]** (no reading obtained — left
> blank, never fabricated).

## Schematic reference correction (2026-08-29)

**Every prior citation in this project named the wrong schematic blob.** The trace target was
recorded as `d2a7f691` / `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch` — in this
file's own identity table, in `v1.7-SHIELD-REVS.md` §4/§5, and in v1.34 Phase 164 success
criterion 2. Both halves of that citation are wrong:

| | Claimed | Actual |
|---|---|---|
| Blob `d2a7f691` | "upstream Rev 0 schematic" | `hardware/W27C512Programmer.kicad_sch` on **`origin/rev2.0`** — a later revision |
| Container | inside `UniversalProgrammerRev0b0.zip` | a **bare `.kicad_sch`** committed alongside that zip, not inside it |
| True Rev 0 schematic | — | blob **`cfe6139f`**, `hardware/W27C512Programmer.kicad_sch` @ commit **`486f3d1`** |

**Why this is not a cosmetic citation fix.** The two schematics differ by 23 components, and the
differences land exactly where a rework trace would look:

| Aspect | Rev 0 (`cfe6139f`) | rev2.0 (`d2a7f691`) |
|---|---|---|
| Component count | 101 | 124 |
| Jumpers | **JP1** `24pin ROM VCC`, **JP2** `>=SST39SF020 & 28C512 need A17`, **JP3** `W27C010/AT27C010 needs p1 VPE/VPP (32 pin)` | **JP4** `P1_VPP_JMP`, **JP5** `A19_CUT` (JP1–JP3 absent) |
| A3 ADC divider | **none** — no R41 | R41 = 4k7 |
| Resistor packs | RN1, RN9 present; RN2–RN5/RN7–RN8 = **4k7** | RN1/RN9 absent; RN2–RN5/RN7–RN8 = **10k** |
| Transistors | Q1–Q8 | Q1–Q12 (adds Q9–Q12) |
| Global labels | includes `A18` | includes `P2`, `P28`, `P30`, `P31`; no `A18` |

A tracer working from `d2a7f691` would search a Rev 0 board for **JP4/JP5, which are not on it**,
and would never inspect **JP1/JP2/JP3, which are** — and JP1–JP3 are precisely the ROM-configuration
straps a cut-and-jumper rework is most likely to have touched. Note also CHAT-INTEL §2's record
that JP4 is the renamed JP3-mod, so the two designators refer to related but not identical nets.

**Trace against `cfe6139f`. Not `d2a7f691`.**

## Board identity

> **⚠ CORRECTION (2026-06-01), STILL STANDING:** No Modified Rev 0 physical inspection has ever
> occurred. The 2026-06-01 bench session initially believed it was on the Modified Rev 0 board,
> but the board was a **Rev 2.0** shield (firmware `hw` → "Rev 2.0-class"; operator correction).
> The rows below are sourced from prior canonical knowledge in `v1.7-SHIELD-REVS.md`, **not** from
> direct inspection.
>
> **This notice is deliberately NOT discharged.** v1.34 Phase 164 criterion 3 required discharging
> it by quoting the A3 ADC reading captured in Phase 163 cell B1. **Phase 163 never ran**, so that
> reading does not exist, and the criterion was formally **deferred by operator decision
> 2026-08-29**. Discharging it needs one A3 ADC reading taken with this board mounted — a reading
> that can be captured over USB once the board is on a controller, but the mounting is operator-only.

| Field | Value | Source |
|-------|-------|--------|
| Parent | upstream Rev 0 — commit `upstream-486f3d1`, schematic blob **`cfe6139f`** | v1.7-SHIELD-REVS.md §1/§4; corrected 2026-08-29 |
| EEPROM `hw_revision` | cannot distinguish this board from the other two shields — silkscreen is authoritative | memory [[user_shield_revisions]] |
| ADC detect | Modified Rev 0 detects mid-band as `Rev 2.3` (10 kΩ A3 pull-up); a `Rev 2.0-class` reading means the board is **not** the Modified Rev 0 | v1.7-SHIELD-REVS.md §3/§8 |
| ADC collision caveat | **Rev 2.2 also reads 10 kΩ**, so a mid-band reading confirms "not Rev 2.0" but cannot by itself separate Modified Rev 0 from Rev 2.2 | memory [[modified_rev0_never_physically_inspected]] |

## Known / attested modifications

| Mod | Description | Status | Source |
|-----|-------------|--------|--------|
| A3 pull-up | External 10 kΩ pull-up, A3 → +5 V. Lands the board in the ADC mid-band (220–600) → detected as `REVISION_2_3`. Rev 0 ships **no** A3 divider (R41 absent from `cfe6139f`), so this is an addition rather than a value change. | **[attested, untraced]** | v1.7-SHIELD-REVS.md §"Modified Rev 0" (line 209); bench-evidence-35.md |
| Bug-A/B rework | Hardware-bug-A/B rework consists of **cuts + jumpers**; count and locations not inventoried. | **[attested, untraced]** | v1.7-SHIELD-REVS.md §4/§5; memory [[user_shield_revisions]] |

## Rework inventory (the deliverable — blocked on photographs)

Every cut and jumper, both endpoints named in **`cfe6139f`** terms. **Zero rows captured.**

| # | Type | Endpoint A | Endpoint B | Status |
|---|---|---|---|---|
| — | — | — | — | **[uncaptured]** — no photograph of this board exists |

**Inspection targets, in priority order**, derived from the Rev 0 netlist:

1. **JP1** (`24pin ROM VCC`) — fitted / cut / rewired?
2. **JP2** (`>=SST39SF020 & 28C512 need A17`) — the A17 strap; relevant to any upper-address fault.
3. **JP3** (`W27C010/AT27C010 needs p1 VPE/VPP (32 pin)`) — the Rev 0-era VPP strap.
4. Upper-address nets `A15`, `A16`, `A17`, and the Rev 0-only global label **`A18`** — Bug A is upper-address jitter, so these carry the strongest prior.
5. Control lines `~{ROM_CE}`, `~{ROM_OE}`, `~{RW}`, `CTRL_LE`, `RLSBLE`, `RMSBLE`.
6. VPP path `VPE`, `VPE_TO_VPP`, `P1_VPP_ENABLE`, `A9_VPP_ENABLE`.
7. Resistor packs **RN1** and **RN9** (Rev 0-only, both 4k7) — disturbed by the rework or not?

## Signal-integrity trace vs Rev 0 schematic (Phase 44 Task 1 target)

| Net | Measurement | Reading | Status |
|-----|-------------|---------|--------|
| A15 | Series termination, RURP driver → A15 chip pin (expect ~33–100 Ω) | — | **[uncaptured]** Phase 44 session: no quantitative reading dictated |
| D0–D7 | Pull-down to GND, per data line | — | **[uncaptured]** |
| VPP | Voltage at chip pin during read (expect ~0 V) | — | **[uncaptured]** board not connected |
| VCC | Rail sag during rapid A15-toggling reads | — | **[uncaptured]** board not connected |

## Outstanding

- **Photo session (operator-only, the single blocker).** Needed: `top`, `bottom`, `silkscreen`,
  one frame per identified rework region (region count to be stated explicitly), plus one frame
  each of the **JP1 / JP2 / JP3** positions. Destination `.planning/milestones/v1.7-artifacts/photos/modified-rev-0/`,
  which does not yet exist — the directory holds only `rev-2-0/` and `rev-2-2/`.
- **A3 ADC reading** with this board mounted — discharges the 2026-06-01 correction notice and the
  deferred criterion 3. Capturable over USB once the operator mounts the shield.
- **Silkscreen identification by the operator** — mandatory before any electrical claim, since the
  A3 ADC mid-band reading collides with Rev 2.2.
- Full rework inventory traced against `cfe6139f` — desk work, unblocked the moment photos exist.
- A15 series-termination + D0–D7 pull-down DC readings — the evidence that would down-select Bug A
  to a single signal-integrity mechanism. See
  `.planning/phases/44-bug-a-rca-modified-rev-0-upper-address-jitter/evidence/static-check-notes.md`.
