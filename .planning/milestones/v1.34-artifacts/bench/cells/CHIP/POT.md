# CHIP cell — POT.md (12 V-group VPP record)

## D-13 scope

This is the **single** meter reading for the whole 12 V group (positions 1-8, per
`162-05-PLAN.md` Task 1). Positions 2 through 8 record their real-rail figure as a **named
absence** pointing back to this position — no second meter reading is taken inside this group
unless a pot boundary is crossed (the 12 V -> 13 V transition ahead of AM27C020, per PD-17).

## Session-open reading (Task 1, operator-performed)

- **12 V-group target:** 12000 mV (`rig-pins.json` `chips.w27c512.vpp_mv` / `chips.w27e512.vpp_mv`,
  both `12000`).
- **Guard band (firestarter/src/proms/eprom.cpp):** low guard fires strictly below
  `target * 95 / 100` = 11400 mV (`:535`); high guard fires above `target + 500 mV` = 12500 mV
  (`:530`). The guards compare the **firmware's own ADC reading**, never the operator's meter —
  the two will not agree exactly (A3/B2's own ratiometric ~+7.5% finding,
  `bench/cells/A3-B2/POT.md`).

### RETRACTION — the "drift" finding below was an orchestrator error, not a rig fault

**The paragraph immediately below this note (kept, struck through, for the record) was wrong and
is retracted by the orchestrator, not by the operator and not by the rig.** The orchestrator cited
Phase 161 cell A3/B2's *first, pre-adjustment* meter reading ("messured vpp to be exactly 12v" ->
12.0 V, `bench/cells/A3-B2/POT.md:34-36`) as though it were that cell's *settled* working state. It
was not: at that setting the firmware read **12.9-13.0 V — above the high guard** (`POT.md:45-63`
in that cell), and the operator then adjusted the pot **down**. A3/B2's actual, explicitly-ruled
settled state was **meter 11.44 V / firmware 12.3 V**, "Orchestrator ruling — P-06 SATISFIED, no
further adjustment" (`bench/cells/A3-B2/POT.md:77-90`).

**Corrected reading of this session's own sequence, no rig fault implied:**

1. **As found (Task 1): meter 11.4 V.** This **was Phase 161's correct, settled working setting**
   (11.44 V, rounded/read as 11.4 V here), **correctly inherited, untouched, exactly as intended.**
   There was no drift and no ~600 mV loss — that claim is retracted outright.
2. Acting on the orchestrator's mistaken citation of A3/B2's superseded pre-adjustment figure, the
   operator was asked to adjust the pot **up** to "restore" a 12.0 V target that was never actually
   A3/B2's working point. **As set: meter 11.97 V.** This is what produced a firmware reading of
   **12800 mV — 300 mV above the 12500 mV high guard** (recorded in C-03 below), correctly halting
   before running `dev test` at a setting that would have produced a pot-artifact failure, not a
   chip or v1.33 finding.
3. Operator re-adjusted the pot down. **As re-set: meter 11.6 V, firmware 12400 mV** — **in band**
   (100 mV of margin below the 12500 mV high guard, comfortably above the 11400 mV low guard).
   This is the setting the 12 V group (positions 1-8) actually runs at.

**No rig fault is implied by any of this** — the rig did not drift, nothing was lost while
standing, and Phase 165 should not be sent chasing a nonexistent hardware defect. The only genuine
error was the orchestrator's mis-citation of a superseded reading from a different cell's record.

~~### Drift finding — same rig, same pot setting, ~600 mV lost while standing (RETRACTED, see above)~~

~~Phase 161's cell A3/B2 `CELL.md` (`bench/cells/A3-B2/CELL.md:27-30`) records the operator's own
pre-flash meter reading on this same rig, this same pot setting, confirmed untouched since:
"messured vpp to be exactly 12v" -> 12.0 V. ~600 mV lost between phases with nothing moved.~~
**Wrong** — that 12.0 V figure was A3/B2's own pre-adjustment reading, not its settled state; see
the retraction above. **The genuine, independently-corroborated finding this session confirms
instead is the shield's ratiometric VPP-ADC gain error** (below), a known-carried characteristic,
not a new defect.

### The pot sequence, plainly (supersedes the "Pot adjusted" note below)

| Step | Meter reading | Firmware reading (if measured) | In band? | Action |
|---|---|---|---|---|
| 1. As found (Task 1) | 11.4 V | not queried at this setting | Phase 161's correct working point | none needed — correctly inherited |
| 2. Adjusted up (orchestrator's mistaken instruction) | 11.97 V | 12800 mV (C-03) | **NO — 300 mV above high guard** | halted, no `dev test` run |
| 3. Re-adjusted down (this correction) | 11.6 V | 12400 mV (C-03 reconfirm) | **YES — 100 mV margin below high guard** | proceeding |

**Operative pot reading for the 12 V group (positions 1-8): meter 11.6 V / firmware 12400 mV.**
This is the value carried into `CELL.md` and into every position's `vpp_real_mv` in this group —
positions 2-8 cite this position (`CHIP__v133__w27c512`) as a named absence for their own
`vpp_real_mv`, per D-13.

No forbidden override flag (`--force`) was used at any point in this session.

## C-03 — per-position firmware VPP readings (one per position, this file's running log)

| Position / reading | Firmware VPP reading | Target | High guard (target+500) | Low guard (target×95%) | In band? |
|---|---|---|---|---|---|
| `CHIP__v133__w27c512`, 1st reading (pot at meter 11.97 V) | **12800 mV (12.8 V)** | 12000 mV | 12500 mV | 11400 mV | **NO — 300 mV ABOVE the high guard** |
| `CHIP__v133__w27c512`, reconfirm after re-adjustment (pot at meter 11.6 V) | **12400 mV (12.4 V)** | 12000 mV | 12500 mV | 11400 mV | **YES — 100 mV margin below the high guard** |
| `CHIP__v133__w27e512` | *(recorded at Task 5, same pot setting, named-absence per D-13)* | 12000 mV | 12500 mV | 11400 mV | *(see below)* |

### FINDING — position 1's firmware VPP reading exceeds the high guard; a pot adjustment is required before `dev test` can run clean

Command run (exactly once, no monitor loop — see the shared conventions; a controlled `timeout -s
INT 4` was used to end the command's own continuous-print loop deterministically rather than let a
harness-level kill happen unlogged, per the standing `BRINGUP-wrv` P-H1 precedent
(`bench/EVIDENCE.md`'s `BRINGUP-wrv` row, an unlogged `vpp` kill left `~/.firestarter` populated)):

```
timeout -s INT 4 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp
```

Output: `VPP: 12.8V, Internal VCC: 5.5V` — one clean reading, then `VPP reading stopped by user.`
No error text; the standalone `vpp` diagnostic does not itself route through the firmware's
`eprom_check_vpp` guard (it printed cleanly at a value that guard would reject).

**12800 mV is 300 mV *above* `eprom.cpp:530`'s high guard** (`vpp_mv > target + 500` = 12500 mV
for this target). That guard **is** in the call path `dev test` will exercise: `eprom_generic_init`
(the init phase of both `write` and `erase`) calls `eprom_check_vpp` unconditionally and returns
`RESPONSE_CODE_ERROR` without `--force` (forbidden here) when the high guard fires — meaning
position 1's `write`/`erase` steps would abort at INIT if `dev test` is run at the pot's current
setting.

**Ratio consistency, not a new phenomenon:** 12800/11970 = **1.069**, in the same range as A3/B2's
measured ~+7.5% (1.075) ratiometric VPP-ADC gain error on this shield
(`bench/cells/A3-B2/POT.md`) — this is the *same* shield-wide gain fault, observed a third time
(two boards, three pot positions in A3/B2, now a fourth data point here), not a new rig defect.

**Precedent for the corrective action, P-06:** "If the historical `VPP is high` init guard fires
..., the pot is adjusted until the reading is in band and the run restarts clean from this step —
the guard is never bypassed, and `--force` is never used to push past it." Per the shared
conventions, only the **operator** adjusts the pot; Claude never adjusts it and never runs a
monitor loop. **A3/B2's own working setting on this exact rig type landed at firmware ≈12.3 V /
meter ≈11.44 V** (in band, ~200 mV of real margin below the 12500 mV high guard) — offered to the
operator as a concrete reference point, not as an instruction to hit that exact number.

**This is a physical pot-movement action and is handed to the operator as a checkpoint** (Task 3
paused; see the plan's checkpoint return). C-05 (the `dev test` invocation) is **not** run at the
current setting — running it now would very likely produce a genuine `MSG_ERR_VPP_HIGH` INIT abort
that is an artifact of the pot setting, not a finding about the chip or about v1.33.

**Resolved below.** This was a genuine physical pot-movement action, correctly handed to the
operator as a checkpoint (Task 3 paused at this point); C-05 was correctly **not** run at this
setting.

### RESOLUTION — reconfirmed in band after re-adjustment; proceeding

Operator re-adjusted the pot down (meter 11.97 V -> 11.6 V). Reconfirming single read (same
policy — exactly once, `timeout -s INT 4`, no monitor loop):

```
timeout -s INT 4 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp
```

Output: `VPP: 12.4V, Internal VCC: 5.5V` — one clean reading, then `VPP reading stopped by user.`
**12400 mV is in band**: below the 12500 mV high guard (100 mV margin — tighter than A3/B2's
settled ~200 mV margin at 12.3 V, but genuinely in band, guard does not fire) and well above the
11400 mV low guard. `dev test` proceeds at this setting (C-04 onward).

**Ratio: 12400/11600 = 1.069**, matching this same session's earlier 12800/11970 = 1.069 and
A3/B2's independently measured ~1.075 (+7.5%) — a **reproducible, shield-wide ratiometric VPP-ADC
gain characteristic**, corroborated a fourth and fifth time here. **Carried forward as a
known-carried rig characteristic** (why the meter and the firmware guard never agree on this
shield), **not as a new defect** and **not as a v1.33 divergence** — the guards compare the
firmware's own ADC reading, never the meter, by design.



