# Cell A3/B2 — P-05 / P-06: chip seating and pot confirmation, calibration cross-check

## P-05 — Seat the W27C512 (2026-08-27, operator)

Operator reply, verbatim (via coordinator relay), in two parts (same class of ambiguity cell A2
recorded — the first reply answered a different, separately-asked question and was not treated as
a state confirmation on its own):
1. "nothing looks of" (i.e. "nothing looks off") — answer to the chip-condition inspection
   question, not a seat/pot state confirmation.
2. "seated and set" — the state confirmation, sought separately and explicitly after (1).

**W27C512 (DIP28) SEATED** in the Rev 2.0 socket on the Leonardo at `/dev/ttyACM0`.

### Inherited chip-condition caveat — CLOSED at this handling (ninth), by inspection

The W27C512 was handled eight times across A1 and A2 with its physical condition never assessed —
the operator was asked twice and did not answer, and it threw a `0x303` contact fault in A2
requiring a Standing bench rule 8 re-seat. Both A2's `CELL.md` and this cell's own `CELL.md` (P-01
section) carried that as explicit, unresolved **uncertainty**.

At this, the part's **ninth** handling, the operator inspected it and reported **"nothing looks
of[f]"** — the first assessment of its physical condition anywhere in the phase. Recorded
precisely, not overstated: this is **an operator visual inspection reporting nothing anomalous at
handling nine**, not a clean bill of health from any measurement, and it is **not** retroactive
clearance for A2's contact fault, which remains a real, separately-recorded observed event (its
own discarded attempt is preserved in `A2/CELL.md`, unchanged by this note). The standing caveat
is closed as of this handling; A2's fault stands as history.

## P-06 — Single confirming `vpp` read (log `10_vpp_confirm`) — a direct calibration cross-check

**Target:** 12.0 V, sourced from `rig-pins.json`'s `chips.w27c512.vpp_mv` /
`chips.w29c020.vpp_mv` (both `12000`) — the single pot setting for the whole cell.

**Operator's multimeter reading, already on record from `P-01`** (`CELL.md`): "messured vpp to be
exactly 12v" -> **12.0 V**, taken **before** any firmware `vpp` query on this board — a properly
ordered paired measurement (meter first, firmware second), unlike A2's retrospective pairing.

**Command:** `timeout --signal=INT 6 env FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config
/workspaces/.v1.34-arms/control/.venv/bin/firestarter -p /dev/ttyACM0 vpp` — exactly one
confirming read, no monitor loop (Standing bench rule 4). `firestarter vpp` has no single-shot
flag (continuous monitor, "Press Ctrl+C to stop."); interrupted via SIGINT (`timeout
--signal=INT`) after the first readings appeared, rc=124 (SIGINT-terminated as expected, not a
tool failure).

**Measured (first reported reading, the confirming value): `VPP: 12.9V, Internal VCC: 5.3V`.**
Subsequent readings in the same brief capture before interrupt: 13.0V / 13.0V / 13.0V / 12.9V.

**`--force used? No`** — no write was attempted; this is a monitor-only read.

### Result: FIRMWARE MATERIALLY OFF THE OPERATOR-MEASURED RAIL — STOPPING PER INSTRUCTION

Firmware-reported VPP (**~12.9-13.0 V**) versus the operator's multimeter reading on this exact
rig (**12.0 V**, taken before this read) differ by **~0.9-1.0 V** — materially off target, and
**above the firmware's own HIGH guard threshold**:

- `firestarter/src/proms/eprom.cpp:713` — HIGH guard fires above `target_mv + 500` = **12.5 V**
  for a 12000 mV target. The measured 12.9-13.0 V reading is **above this threshold**, meaning an
  actual write attempt at this pot setting would very likely trip `MSG_ERR_VPP_HIGH` (a hard
  error, since `FLAG_FORCE` is never set in this project).
- `firestarter/src/proms/eprom.cpp:736` — LOW guard fires below `target_mv * 95%` = 11.4 V; not
  the relevant side here.
- Accepted window for a 12000 mV target: **11.4-12.5 V**. The measured reading is **outside** this
  window, on the high side.

Per the coordinator's explicit instruction for this branch: **no pot adjustment was performed.**
Task 5 (`P-07`, the W27C512 write) was **not** started — proceeding to a write at a VPP reading
already above the guard's own HIGH threshold would risk exactly the failure mode A2's escalation
step 4 recorded ("VPP guard now fires HIGH, unexpectedly"), and the instruction was explicit not
to chase the ADC by re-adjusting the pot (on A2 that drove the real rail to ~11.2 V).

**This is a second, independent VPP ADC finding, same direction as A2's:** A2's uno328pb read
~0.8 V high (firmware 12.5 V vs meter 11.7 V); this Leonardo reads ~0.9-1.0 V high (firmware
12.9-13.0 V vs meter 12.0 V, taken first). Two boards, two ADC chains, both reading high by a
comparable margin, against two independently meter-verified real rails. **Escalated to the
coordinator for a ruling before this cell proceeds** — see the plan-level checkpoint note.

## Orchestrator ruling — P-06 SATISFIED, no further adjustment (2026-08-27)

**Operator response after adjusting the pot down from the earlier position, verbatim:**
"12.3v from board is 11.44 in reality" — firmware-reported VPP **12.3 V**, operator multimeter
**11.44 V**, both at the same (new) pot setting.

**Ruling: 12.3 V is IN BAND.** Accepted window derived from firmware source, not from
string-equality to the 12.0 V target (the same criterion cell A2 established and this project's
only valid one):
- HIGH guard: `firestarter/src/proms/eprom.cpp:713`, fires above `target_mv + 500` = **12.5 V**
  for this 12000 mV target. 12.3 V < 12.5 V — **does not fire**.
- LOW guard: `firestarter/src/proms/eprom.cpp:736`, fires below `target_mv * 95%` = **11.4 V**.
  12.3 V is far above it — **does not fire**.
- **P-06 is satisfied.** No further pot adjustment requested or performed.

## HEADLINE FINDING — the VPP ADC's error is RATIOMETRIC, consistent with a shield-wide gain
## fault, not board-specific (revises the working hypothesis from 161-04-SUMMARY.md)

Three paired firmware-vs-meter measurements now exist across two boards and three pot positions:

| Cell / board | Firmware VPP | Operator meter | Additive offset | Ratio (fw/meter) |
|---|---|---|---|---|
| A2 (uno328pb) | 12.5 V | 11.70 V | +0.80 V | x1.068 (+6.8%) |
| A3/B2 (Leonardo, 1st reading) | 12.9-13.0 V | 12.00 V | +0.90-1.00 V | x1.075-1.083 (+7.5-8.3%) |
| A3/B2 (Leonardo, 2nd reading, post-adjustment) | 12.3 V | 11.44 V | +0.86 V | x1.075 (+7.5%) |

**The ratio holds far tighter than the additive offset — approximately +7.5% (range 6.8-8.3%)
across two boards and three pot positions.** This is **consistent with** a ratiometric (gain)
error — a wrong voltage-divider ratio, which is what the R1/R2 values in `rurp_configuration_t`
encode — rather than a fixed additive offset. **This is an inference, not established:** three
points against one meter cannot conclusively separate a gain error from an offset error, and no
claim beyond "consistent with" is made here.

**Why this matters, and what it revises:**

1. **Refutes the board-specific reading this cell's read was expected to establish.** A clean
   ~12.0 V match here would have shown A2's ~0.8 V error was that board's own EEPROM calibration.
   Instead, two boards with **independent** EEPROM calibrations show the **same proportional**
   error. That points at the **shared component** — the Rev 2.0 shield itself, which carries the
   pot and the divider the ADC measures — not at either board's EEPROM calibration. Flagged
   explicitly as an inference from the ratio consistency, not a proven root cause.

2. **Forces a correction to cell A2's record.** `161-04-SUMMARY.md` filed low real-rail VPP as the
   **leading hypothesis** for A2's four write failures, inferring a real rail near ~11.1-11.2 V
   from firmware's 12.5 V reading via the same ~0.8 V offset it measured. If the error is
   shield-wide (this cell's evidence), then **A1's firmware reading of 12.0 V also corresponded to
   a real rail near ~11.0-11.2 V** — and **A1 passed all four positions at that voltage.** A1
   passing where A2 failed, at a comparable inferred real rail, **substantially weakens** low-VPP
   as A2's explanation. This is **NOT** a retraction performed by editing A2's committed record —
   `161-04-SUMMARY.md` and `A2/CELL.md` are left exactly as they were filed. This is a **forward
   supersession**, recorded here and in `161-05-SUMMARY.md`, and handed to Phase 165 as the
   revision to carry.

3. **Real-rail disclosure for this cell.** This cell runs at a real rail of **~11.44 V** against a
   12.0 V nominal target — marginally below the W27C512's typical programming spec. This is also
   the **best achievable** setting on this shield: the HIGH guard caps the real rail at roughly
   **11.64 V** (the guard fires at firmware-reported 12.5 V, which by the same ~7.5% ratio implies
   a real rail of ~11.6 V at the guard's own ceiling) — no pot position on this shield can put the
   real rail meaningfully higher without tripping the guard.

4. **Comparability caveat across cells.** A1 ran at firmware 12.0 V (inferred real ~11.1-11.2 V);
   A2 ran at firmware 11.9 V (inferred real ~11.05 V); this cell runs at firmware 12.3 V / real
   **11.44 V** — a **higher** real rail than either of the other two cells. The three cells did
   **not** run at identical real voltages; any cross-cell write-outcome comparison must carry this
   caveat.

5. **Sharpens the milestone's own disclosed non-claim.** Phase 160 §6 already discloses that
   program-window VPP/VCC under load is unmeasured (DTR-reset-on-close tooling gap). This finding
   adds: the on-board instrument used for every other VPP reading in this milestone is **~7.5%
   optimistic**, on top of that gap. Flagged for Phase 166's honesty ledger.

6. **Non-claim, stated in both directions:** A1's Uno was **never meter-checked**. Any offset for
   A1 is **inferred** from the shield-wide-gain hypothesis above, not measured. This record does
   **not** assert A1 ran low, and does **not** assert it did not.

**`--force used? No`.** P-06 is now satisfied by ruling against the firmware-derived accepted
window, not by exact-match string comparison. Proceeding to Task 5 (`P-07`, position 1).
