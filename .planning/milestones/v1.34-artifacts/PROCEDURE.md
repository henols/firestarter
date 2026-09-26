# v1.34 Bench Procedure — One Arm-Agnostic Cell Run

**Phase:** 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur (RIG-03 / SC#3)
**Status:** Prescriptive. This document says what will be done, in what order, and with which
literal command shapes — it is not a log of what happened (that is `bench/EVIDENCE.jsonl` /
`bench/EVIDENCE.md`).

This procedure is executed **unchanged** by Phases 161 and 163, whose cells are write-read-verify
cells. Phase 162 runs a different command (`firestarter dev test`) and executes the
Chip-sweep step list section (see below) instead of the Step list section — see the amendment
recorded at the bottom of this file.
Every cell either phase runs cites this document's step ids rather than re-describing the run.

---

## Scope

One cell run covers **both arms** (`control` then `v133`) and **both bench chips**
(W27C512 DIP28, then W29C020 DIP32) on one mounted shield/board pair. A cell therefore holds
**four positions**: `{control,v133} × {w27c512,w29c020}`. The five cells this milestone runs
are `A1`, `A2`, `A3/B2`, `B1`, `B3` (`.planning/STATE.md`, `.planning/REQUIREMENTS.md`); one of
those (`A3/B2`) additionally carries a bring-up position (`BRINGUP-wrv`) recorded outside the
five-cell table.

**Two cell shapes, not one.** The paragraph above defines the **WRV cell** — the shape Phases 161
and 163 run, and the only shape the Step list section's `P-01`…`P-11` describe. Phase 162 runs a
**chip-sweep position** instead: one part, one arm, one `firestarter dev test` invocation, on the
standing Leonardo and Rev 2.0 rig Phase 161 leaves assembled. A chip position has no pre-computed
image, no `IMAGE-PLAN.json` row, no full-device SHA judgement and no per-cell arm rotation —
`P-07` and `P-09` do not apply to it at all. Its steps are `C-01`…`C-09` under the Chip-sweep step
list section (see below), and its evidence goes to `bench/CHIP-EVIDENCE.jsonl`, never to
`bench/EVIDENCE.jsonl`, whose position count covers WRV positions only. The **standing bench
rules, the Arm substitution token table, the halt policy, the outcome taxonomy, the forbidden
invocations and the recording discipline bind both shapes identically.**

This document is executed **unchanged** by Phases 161–163. Any change to it after the first
real cell has run must be recorded as a **procedure amendment**: a dated note at the bottom of
this file naming (a) what changed, (b) why, and (c) exactly which cells ran under the old text
and which run under the new text. An amendment is never silent — a step whose text quietly
drifts mid-sweep is exactly the failure mode `render_steps.py`'s gate and this scope note exist
to prevent.

---

## Standing bench rules

These bind every step below; they are restated here as rules, not preferences, and none of
them is new to this milestone — most are standing project memory this procedure is required to
honor.

1. **Port identity is re-verified for every cell, never inherited.** `/dev/ttyACM*` **and
   `/dev/ttyUSB*`** numbering shuffles across replug (160-09's `uno328pb` bring-up board
   enumerates as `ttyUSB*` — a CH340 USB-serial bridge, not the ATmega16U2 that gives a genuine
   Uno its ACM node — so both node classes are in scope for this rule, not only `ttyACM*`), so
   the port used by a previous cell (or a previous session) is never
   assumed for this one.
2. **Chip-out-before-sideload is Uno-class only.** On `uno` and `uno328pb`, the chip must be
   out of its socket before any avrdude invocation that touches the bootloader — a flash **and**
   a read-back are the same electrical situation, so both live inside the chip-out window. The
   **Leonardo is exempt** and is flashed and read back with the chip **seated**.
3. **Photography, multimeter readings, chip handling and pot adjustment are operator-only.**
   Claude drives serial and CLI only — `fw`, `hw`, `read`, `write`, `vpp`, `dev consistency-check`
   and this phase's own tools. Claude never touches the physical rig.
4. **The operator adjusts the pot himself.** Claude states the target, the operator sets it and
   reports back, and Claude takes **exactly one** confirming read — never a live monitor loop.
5. **The VPP and VPE monitors do not route to the socket.** A blank or nonsense reading on
   either means a contact fault, not a rail fault — do not chase it as a voltage problem.
6. **Board identity is by silkscreen and avrdude signature, never by a firmware-reported
   revision field.** `hw_revision` cannot distinguish the operator's three shields (Rev 2.0 /
   Rev 2.2 / Modified Rev 0 collide on the same resistor band), so the operator's silkscreen
   read is authoritative for shield identity and the avrdude signature probe is authoritative
   for board/MCU identity. A firmware-reported field is never used for either.
7. **This procedure must not run under `--auto` / `--chain` / any auto-advance mode.** Those
   modes auto-approve the `human-verify` checkpoints every physical step in this procedure
   depends on; `autonomous: false` on a plan is not self-protecting against that.
8. **A single clean re-seat is allowed per position, carried forward from the prior bench
   phase.** If a failure is attributable to a named physical cause (a suspected bad contact),
   one re-seat and one re-run are permitted — and **both the discarded attempt and the re-run
   are recorded**, never just the re-run.
9. **`FIRESTARTER_CONFIG_DIR` is set inline on every command that invokes an arm binary or a
   tool that itself shells out to one, never by a session-level `export`.** `config.py` computes
   `HOME_PATH`, `DATABASE_FILE` and `PIN_MAP_FILE` as **import-time** constants derived from
   `get_config_dir()`, even though `get_config_dir()` itself is call-time (its own docstring says
   so, for the `dev test` report path). Exporting the variable mid-session, or in a shell other
   than the one that launches the process, fixes only the call-time consumers and silently leaves
   the database and pin-map pointed at the unset default (`~/.firestarter`) — a partial fix that
   *looks* complete. Every step below that names `$ARM_BIN` directly, and every phase tool that
   shells out to an arm binary internally (`capture_provenance.py`), sets
   `FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR` inline on that same command line. If any step
   is ever copy-pasted into a fresh shell, that shell re-establishes the variable itself, inline,
   before the step runs — it is never assumed to already be exported there.

---

## Arm substitution

The single arm-dependent token in this procedure is **`$ARM_BIN`**, resolved to one of the two
absolute arm binary paths recorded in `rig-pins.json` (`arms.control.venv_bin` /
`arms.v133.venv_bin`). **No step's text differs between the arms.** The arm enters a step only
through this token's runtime value, and because the token is never expanded in the rendered
step list (see `tools/render_steps.py` below), the two arms' rendered step lists are
byte-identical — the arm is visible only in the **recorded, literal command line** a step
actually produces on the bench, never in the procedure's own prose.

The reason this is sufficient, stated plainly: both arms self-report the **identical**
application version (`3.0.0b32`) and both firmware builds self-report the **identical**
version literal (`3.0.0b22`). The invoked binary path and the device read-back are therefore
the *only* two places the arm exists at all — everything else about the two arms is
indistinguishable over the wire. A step that tried to name an arm by version string, by a
handshake, or by any firmware-reported identity field would be naming nothing, because both
arms answer identically.

A small number of tools also take the arm's **bare name** (`control` or `v133`) as a required
argument value — `capture_provenance.py --arm`, `judge_readback.py --flashed-arm` /
`--expect-arm`. That name is the *same* selection `$ARM_BIN` encodes, not a second independent
token; a step's command shape writes it as `{control|v133}` inline, exactly mirroring the
tool's own closed-choice argument, and it never appears as a version string or handshake value.

Every other substitution token below is **not** arm-dependent — its value is the same
regardless of which arm is running:

| Token | Meaning |
|---|---|
| `$PORT` | the device node for this cell (e.g. `/dev/ttyACM0` or `/dev/ttyUSB0` — the `uno328pb` bring-up board enumerates via a CH340 bridge as the latter, 160-09), re-verified per Rule 1 above |
| `$CELL_ID` | `A1`, `A2`, `A3/B2`, `B1`, `B3`, or `BRINGUP-wrv` |
| `$POSITION_ID` | `<cell_slug>__<arm>__<chip>`, the `bench/IMAGE-PLAN.json` primary key |
| `$SHIELD_REV` | the operator-declared silkscreen value: `Rev 2.0` / `Rev 2.2` / `Modified Rev 0` |
| `$CHIP` | one of the eleven `rig-pins.json` `chips` map slugs: `w27c512`, `w27e512`, `sst27sf512`, `fm1608`, `sst39sf040`, `w27e040`, `w29c040`, `w29c020`, `am27c020`, `m27c512`, `2516` (widened from the original two-part WRV list by the amendment recorded at the bottom of this file) |
| `$CHIP_TOKEN` | the case-sensitive `firestarter dev test <TOKEN>` CLI token **as typed** (e.g. `W27C512`), from `rig-pins.json` `chips.*.chip_token` — declared separately from `$CHIP` (per the amendment recorded at the bottom of this file) because the report path `dev_test` writes is built from the token as typed and its own sanitiser (`_sanitize_chip_token`) does not normalise case, so the same part invoked in two casings writes two different report files and `append_chip_evidence.py`'s copy-out reads only one of them |
| `$TARGET` | `uno` / `uno328pb` / `leonardo` (the PlatformIO env name) |
| `$MASK` | this position's XOR mask, from `bench/IMAGE-PLAN.json` |
| `$CELL_DIR` | `.planning/milestones/v1.34-artifacts/bench/cells/<cell_slug>/` |
| `$FIRESTARTER_CONFIG_DIR` | the one frozen shared config dir, pinned in `rig-pins.json` (`config_dir`): `/workspaces/.planning/milestones/v1.34-artifacts/config` |

**The annotation syntax `[arm: control]` / `[arm: v133]`** is defined here for
`tools/render_steps.py` to detect, and is used **nowhere** in the `## Step list` section below.
A step carrying that marker would be included in only one arm's render, breaking the empty-diff
property SC#3 requires; its deliberate absence from every real step is exactly what the SC#3
gate measures. If a future edit ever needs a genuinely arm-conditional step, it must carry this
marker and the resulting non-empty diff is the signal that the edit needs a design decision,
not a silent merge.

---

## Step list

Eleven numbered steps, in the order Pattern 6 (RESEARCH.md) derives from two standing rules
colliding with D-05 — not an invented order. The two colliding facts: an avrdude
**read** is the same electrical situation as a **write** (bootloader active, shield GPIO lines
exercised), so the Uno-class chip-out window must cover the flash **and** its read-back proof,
not just the flash; and both bench chips declare the identical `vpp_mv: 12000`, so the pot is
set **once per cell**, not once per chip.

### P-01 — Mount and declare

Operator mounts the shield on the board and **declares the shield revision from the
silkscreen**. Silkscreen is authoritative — `hw_revision` cannot distinguish the operator's
Rev 2.0 / Rev 2.2 / Modified Rev 0 shields (the A3 ADC band collides on 10 kΩ). No command;
performer: operator. Record field: `shield_rev_declared` (`$SHIELD_REV`).

### P-02 — Re-verify port identity

Claude re-verifies port identity for **this cell**, never inheriting it from a previous task:

```
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target $TARGET --port $PORT \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/board_probe.json
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT hw
```

The signature probe (`probe_board.py`) is the **authoritative** board identity; the `hw`
command's printed `I: FW: ` / controller line is a separate, non-authoritative port-identity
datum, recorded alongside it. This is RIG-02's "before any test step executes" capture point —
`capture_provenance.py`'s `captured_at_step` field is fixed at `2` for exactly this reason: the
identity fields a position's provenance record eventually carries were established here, at
step 2, before any flash, write or read has touched the board. Performer: Claude. Record
fields: `board_signature`, `controller_string`.

### P-03 — Uno-class chip-out (flash + read-back window)

**Uno-class only** (`uno`, `uno328pb`): operator removes the chip and confirms. This window
covers the flash **and its read-back proof** in P-04 — an avrdude read is the same electrical
situation as a write, so the chip stays out for both. **The Leonardo is exempt**: it is flashed
and read back with the chip **seated**, per the standing chip-out rule (Standing bench rule 2).
No command; performer: operator.

### P-04 — Flash this arm, then prove it by independent read-back

Claude selects this arm's firmware source state, flashes it via the PlatformIO upload path
(never a hand-rolled avrdude write — PIO supplies the per-target flags this procedure does not
reproduce: `-x nometadata` on `uno328pb`'s urclock bootloader, the 1200-baud touch and
port-wait on `leonardo`'s avr109), then proves the flash with an **independent** avrdude
read-back, never avrdude's own upload-time verify pass (D-01):

```
git -C /workspaces/firestarter checkout <fw_sha for {control|v133}>
git -C /workspaces/firestarter status --porcelain          # must be empty
cd /workspaces/firestarter && pio run -t upload -e $TARGET  # Pitfall 4: cwd MUST be firestarter/, never /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target $TARGET --port $PORT \
  --flashed-arm {control|v133} --expect-arm {control|v133} \
  --out-dir $CELL_DIR --pins .planning/milestones/v1.34-artifacts/rig-pins.json
```

`judge_readback.py` runs its own avrdude read with `-A` explicit (Pitfall 2 — without it the
read-back is truncated), normalizes the flashed arm's `.hex` with the pinned `avr-objcopy`, and
judges the `[0, hex_span)` prefix under the target's `judged_span_policy` — refusing outright on
`uno328pb` while that policy is still the `PENDING-xshowvector` placeholder (see Recording
discipline). **D-05: this read-back proof runs at every cell's flash, not only at bring-up** —
a cell whose arm was mis-flashed is caught at the cell, not at the close. The whole 32768 B
read-back's SHA is recorded as an **unjudged** provenance datum alongside the judged verdict,
never consumed in the match decision (D-02).

The `--flashed-arm`/`--expect-arm` pair is also how D-03's deliberate cross-flash (bring-up
only, Phase 160 plans 08–10) is expressed as a single invocation: flash arm X, judge against
arm Y's hex, observe the MISMATCH, then flash and judge the correct arm.

Performer: Claude. Record fields: `fw_sha` (post-checkout `git rev-parse HEAD`),
`host_arm_porcelain_clean` for the firmware checkout, `fw_readback_sha_judged`,
`fw_readback_sha_whole_flash`, the literal `commands` argv for every invocation above.

### P-05 — Uno-class: seat the first chip

**Uno-class only:** operator seats the 28-pin chip (W27C512, DIP28) and confirms. No command;
performer: operator.

### P-06 — Set the pot once per cell

Claude states the target for the declared VPP value (both bench chips declare
`vpp_mv: 12000` — see `rig-pins.json` `chips.*.vpp_mv`), the operator sets the pot and reports,
and Claude takes **exactly one** confirming read:

```
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT vpp
```

The pot is set **once per cell, not once per chip**, because both bench chips agree on the
VPP target — this is the single largest simplification available to this step list, and it is
why this step sits before the chip rotation rather than inside it. If the
historical `VPP is high: 13.1V > 12.0V` init guard fires (Phase 145 D-17), the pot is adjusted
until the reading is in band and the run restarts clean from this step — **the guard is never
bypassed**, and `--force` is never used to push past it (see Forbidden invocations). Performer:
operator (adjustment) + Claude (one confirming read, no monitor loop). Record field: the
confirming VPP reading, plus `--force used? No` as a load-bearing line.

### P-07 — Chip 1 write → read → judge (65536 B)

Claude generates this position's image from its recorded mask and stamp width, writes it with
no forbidden flag, times the write by wall clock, then runs the read set and judges it over
the full 65536 B device size with `judge_wrv.py`:

```
python3 .planning/milestones/v1.34-artifacts/tools/gen_addr_image.py --stamp-width 16 65536 $MASK $CELL_DIR/reads/$POSITION_ID/written.bin
time FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT write w27c512 $CELL_DIR/reads/$POSITION_ID/written.bin
```

Read counts and arbitration (stated here, not as a separate step, because it applies
identically to this step and its W29C020 counterpart below): **three independent reads on the
v1.33 arm at every position**, via
`FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT dev consistency-check w27c512 --runs 3 --output-dir $CELL_DIR/reads/$POSITION_ID --keep-files`;
**a single read on the control arm normally**, via
`FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT read w27c512 $CELL_DIR/reads/$POSITION_ID/run_01.bin`
(the positional-output form, named to match `judge_wrv.py`'s `run_NN.bin` glob) — **escalating to
the same three-run `dev consistency-check` invocation on the control arm only where the v1.33
arm's three reads for this position disagreed**, arbitrating whether the instability is new or
was always there. A disagreement is **recorded as a disagreement and never retried away**.

```
python3 .planning/milestones/v1.34-artifacts/tools/judge_wrv.py --written $CELL_DIR/reads/$POSITION_ID/written.bin --reads $CELL_DIR/reads/$POSITION_ID \
  --expect-size 65536 --app-verdict <dev consistency-check's own 0/1/2, when it ran> \
  --position-id $POSITION_ID --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/WRV-VERDICT_$POSITION_ID.json
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR python3 .planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id $CELL_ID --position-id $POSITION_ID \
  --arm {control|v133} --target $TARGET --port $PORT --chip w27c512 --shield-rev "$SHIELD_REV" \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/provenance_$POSITION_ID.json
python3 .planning/milestones/v1.34-artifacts/tools/append_evidence.py --position-id $POSITION_ID \
  --cell-dir $CELL_DIR --provenance $CELL_DIR/provenance_$POSITION_ID.json \
  --wrv $CELL_DIR/WRV-VERDICT_$POSITION_ID.json --readback $CELL_DIR/READBACK-VERDICT.json \
  --blank-state "<real reading or 'not measured — <reason>'>" \
  --verdict-file <path|-> --anomalies-file <path|-> \
  --write-wallclock-s <measured> --write-app-reported-s <app-reported, or 'not measured — <reason>'> \
  --jsonl .planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl
python3 .planning/milestones/v1.34-artifacts/tools/render_evidence.py --jsonl .planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl \
  --target .planning/milestones/v1.34-artifacts/bench/EVIDENCE.md
```

**(Amendment 3, clause (1)):** the `append_evidence.py` append and its paired
`render_evidence.py` plain re-render run in this same step, immediately after this
position's provenance and WRV-VERDICT both exist — one row per position, as that position
completes, never batched to `P-11`. `append_evidence.py` writes via
`render_evidence.append_row_to_file()` internally, which does **not** itself re-render
`EVIDENCE.md` (its append path returns before the render path), so the two commands above
are an atomic pair: skipping the re-render leaves `render_evidence.py --check` (the
per-cell gate's fourth live leg) red.

`judge_wrv.py` computes SHA-256 over the full 65536 B against the written image — never
`dev consistency-check`'s own exit code (Pitfall 6: that code compares the N reads only to
**each other**, so a chip that reliably returns the wrong bytes still passes it). The app's
0/1/2 is recorded alongside as an unjudged second datum; any disagreement between the two is
itself a finding, not resolved. `capture_provenance.py` runs **after** this position's
read-back verdict exists (it hard-refuses without it), referencing the `fw_readback_sha_*`
fields `judge_readback.py` wrote at `P-04` for this cell/arm and adding this position's
chip-specific fields (`chip`, `chip_package`, `chip_size_bytes`). Performer: Claude (all
commands); the write duration is measured by Claude around the write command.

One clean re-seat is permitted per Standing bench rule 8 if a contact fault is suspected mid-write
— both the discarded attempt and the re-run are recorded, the discard never silent.

### P-08 — Swap to the second chip, no pot re-adjustment

Operator swaps the 28-pin chip for the 32-pin chip (W29C020, DIP32) and confirms. **No pot
re-adjustment happens here** — the declared VPP target (`vpp_mv: 12000`) is the same for both
parts, so `P-06`'s single confirming read stands for the whole cell. No command; performer:
operator.

### P-09 — Chip 2 write → read → judge (262144 B)

As `P-07`, over the full 262144 B device size, with a 32-bit stamp width (the 16-bit stamp used
for W27C512 repeats every 65536 B and would leave an A16/A17 aliasing fault unattributable on
this 18-address-bit part — D-12):

```
python3 .planning/milestones/v1.34-artifacts/tools/gen_addr_image.py --stamp-width 32 262144 $MASK $CELL_DIR/reads/$POSITION_ID/written.bin
time FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT write w29c020 $CELL_DIR/reads/$POSITION_ID/written.bin
```

Read counts and arbitration are exactly `P-07`'s rule, over 262144 B: three independent reads
on the v1.33 arm always (`--output-dir $CELL_DIR/reads/$POSITION_ID`); a single read on the
control arm (`$CELL_DIR/reads/$POSITION_ID/run_01.bin`), escalating to three only where the
v1.33 arm's three reads for this position disagreed. A disagreement is recorded, never retried.

```
python3 .planning/milestones/v1.34-artifacts/tools/judge_wrv.py --written $CELL_DIR/reads/$POSITION_ID/written.bin --reads $CELL_DIR/reads/$POSITION_ID \
  --expect-size 262144 --app-verdict <dev consistency-check's own 0/1/2, when it ran> \
  --position-id $POSITION_ID --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/WRV-VERDICT_$POSITION_ID.json
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR python3 .planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id $CELL_ID --position-id $POSITION_ID \
  --arm {control|v133} --target $TARGET --port $PORT --chip w29c020 --shield-rev "$SHIELD_REV" \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/provenance_$POSITION_ID.json
python3 .planning/milestones/v1.34-artifacts/tools/append_evidence.py --position-id $POSITION_ID \
  --cell-dir $CELL_DIR --provenance $CELL_DIR/provenance_$POSITION_ID.json \
  --wrv $CELL_DIR/WRV-VERDICT_$POSITION_ID.json --readback $CELL_DIR/READBACK-VERDICT.json \
  --blank-state "<real reading or 'not measured — <reason>'>" \
  --verdict-file <path|-> --anomalies-file <path|-> \
  --write-wallclock-s <measured> --write-app-reported-s <app-reported, or 'not measured — <reason>'> \
  --jsonl .planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl
python3 .planning/milestones/v1.34-artifacts/tools/render_evidence.py --jsonl .planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl \
  --target .planning/milestones/v1.34-artifacts/bench/EVIDENCE.md
```

**(Amendment 3, clause (1)):** same atomic append-then-re-render pair as `P-07`'s, for this
position — see `P-07`'s own note above; not repeated per step.

Performer: Claude.

### P-10 — Arm switch

Return to `P-03` for the **second** arm. **Arm order is control first, then v1.33**, so the
control arm never inherits the other arm's chip contents — the first pass through `P-03`–`P-09`
is always the control arm's, the second is always v1.33's. Performer: Claude (sequencing) +
operator (the physical steps `P-03`/`P-05`/`P-08` repeat).

### P-11 — Teardown

Record the final board and arm state: re-run `probe_board.py` to confirm the board identity
has not changed since `P-02`, then run the config-dir check below, then assert this cell's
evidence is complete and declare the leave-state. Performer: Claude.

**(Amendment 3, clause (1)):** the per-position `EVIDENCE.jsonl` append moved to `P-07` and
`P-09` — one row per position, written as that position completes. `P-11` is therefore a
**completeness assertion**, not a write step: confirm that all four of this cell's
`position_id`s are present in `bench/EVIDENCE.jsonl` (or, for a cell that has fewer than four
positions by design, that every position this cell actually ran has a row), and that
`render_evidence.py --jsonl .planning/milestones/v1.34-artifacts/bench/EVIDENCE.jsonl --target
.planning/milestones/v1.34-artifacts/bench/EVIDENCE.md --check` is green (no hand-edit drift).

**(Amendment 3, clause (2), D-12):** `P-11` also carries a general, **cell-agnostic**
leave-state declaration: record the board, port, arm, chip seated (or removed), pot
setting, and shield state this cell is left in. The concrete value for each of the six is
supplied by the executing phase's own plan, never by conditional text in this procedure —
this clause names the six fields every cell must declare; it does not itself declare a
value for any of them.

```
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target $TARGET --port $PORT \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/board_probe_teardown.json
```

**This re-probe writes to a distinct output path from `P-02`'s** (`board_probe_teardown.json`,
never `board_probe.json`), so the pre-flash and post-flash signature captures are two separate,
individually-inspectable artifacts rather than one file silently overwritten — a re-run that
reused `P-02`'s filename would make it impossible to tell, after the fact, whether the teardown
probe ever ran at all. (Amendment 2 below: this literal command block did not exist when
`BRINGUP-wrv`'s own teardown ran, Phase 160 Plan 12 — that cell's teardown never re-ran
`probe_board.py` at all, only the config-dir check; the gap is recorded, not backfilled, in
`bench/cells/BRINGUP-wrv/RECONSTRUCTION-DIFF.md`.)

**The config-dir check is two assertions, in order — not one.** An unchanged SHA proves nothing
by itself if nothing this cell ran ever pointed at the frozen directory in the first place; that
is a vacuous pass, not a clean one (Standing bench rule 9).

A structural note on *why* this is two assertions and not an argv inspection: a shell-level
`FIRESTARTER_CONFIG_DIR=<path> $ARM_BIN ...` assignment (Standing bench rule 9's inline form) is
stripped by the shell before it executes the program — the child process sees the variable in its
own environment, never as a token in its own `argv`. That is true at every level this procedure's
tools shell out through (`capture_provenance.py`'s internal call to the arm's own `hw` command
inherits the variable the same way). So **no recorded `commands[].argv` entry will ever contain
the assignment literally**, by the nature of what an environment variable is — `gate_record.py`'s
existing argv re-parse (`check_commands`) has nothing to inspect here, and this procedure does not
pretend otherwise. The two assertions below are the mechanisms that actually exist today:

1. **(Amendment 3, clause (4)) Assert `~/.firestarter` is unchanged from the recorded
   baseline** — restated from the original "assert it still does not exist" now that the
   directory is a known, disclosed, carried-forward artifact on this container (see below).
   The pinned baseline: path `/home/vscode/.firestarter`; exactly one file, `config.json`,
   30 bytes; `config.json` sha256
   `b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79`; tree sha (sorted
   relpath plus content) `423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951`;
   mtime `1787854674` (`2026-08-27 18:17:54 UTC`). A **change** to any of those four values
   (file count/size, `config.json` sha256, tree sha, mtime) is the `P-H1` finding — the seam
   this rule exists to prove was not actually used by at least one invocation. Deletion is
   **never** attempted: the sandbox denies it, and deleting it destroys the evidence. This is
   the cheap, falsifiable positive proof that no invocation in this cell fell back to the
   unset default (`config.py`'s `get_config_dir()` resolves there when
   `FIRESTARTER_CONFIG_DIR` is absent, and `HOME_PATH`/`DATABASE_FILE`/`PIN_MAP_FILE` would
   have been computed against it at import time for that invocation) — it is checkable
   today, without a device, and it is exactly the failure mode a missing env-var prefix
   would produce.
2. **Only then**, re-verify `$FIRESTARTER_CONFIG_DIR`'s content SHA is unchanged from the value
   seeded at bring-up, via `gate_record.py`'s existing `check_config_dir_sha` (D-07 — either arm
   writing to the shared config dir mid-cell is a visible, recorded event, not invisible drift),
   and confirm each of this cell's four position records carries a **non-null** `config_dir_sha`
   field at all (a field silently omitted would let the SHA check pass by never running — the
   same vacuous-pass shape (1) exists to close, applied to the record itself rather than to the
   filesystem). With (1) holding and the field genuinely present, the SHA check is now
   falsifiable on its own terms: it fails if either arm actually wrote to the frozen dir.

---

## Chip-sweep step list

These nine steps are the chip-sweep position's prescription (Phase 162's amendment, recorded at
the bottom of this file) — one part,
one arm, one `firestarter dev test` invocation, on the standing Leonardo + Rev 2.0 rig Phase 161
leaves assembled (see §Scope, "Two cell shapes, not one"). Five Step list steps apply here **by
reference, and never by copy**: `P-01` (mount and declare — already discharged; Phase 161's A3/B2
left the rig mounted with `Rev 2.0` declared), `P-02` (re-verify port identity, per session,
never inherited), `P-04` (flash this arm, then prove it by independent read-back — fires twice
per divergence, inside `C-08`), `P-06` (set the pot — **superseded per-part** for this shape, see
clause (4) below and `C-02`/`C-03`), and `P-11` (teardown — **retargeted** at
`bench/CHIP-EVIDENCE.jsonl`, see clause (5) below and `C-09`). Six Step list steps are
**explicitly not applicable** to a chip-sweep position: `P-03` and `P-05` are Uno-class-only, and
the standing rig for this sweep is the Leonardo, which is chip-out-exempt (Standing bench rule 2);
`P-07` and `P-09` write a pre-computed `IMAGE-PLAN.json` image and judge a full-device SHA,
neither of which a `dev test` invocation does; `P-08` is the two-chip rotation within one WRV
cell, which has no analogue in an eleven-part sweep; `P-10` is the per-cell arm switch, which
D-17 replaces here with the per-divergence interleave `C-08` performs instead. These six are
named rather than left to inference — Amendment 2's own lesson is that a step whose literal
command must be inferred by analogy is exactly the failure mode this document's prescriptive
contract exists to prevent.

### C-01 — Assert the frozen config dir is pristine

Run `check_arms.py` with the pinned expected config-dir SHA **before** this position's `dev test`
invocation. A dirty digest here means the *previous* position's report was never copied out (its
`C-07` never removed the source files), and the row about to be written would carry a wrong
`config_dir_sha`.

```
python3 .planning/milestones/v1.34-artifacts/tools/check_arms.py --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --expect-config-sha <the pinned config_dir_sha, from arms-provenance.json>
```

Performer: Claude. Record field(s): `config_dir_sha`.

### C-02 — Seat the part; set JP4 and the pot as this position requires

The single operator handover for this position, folding what `P-05`, `P-06` and `P-08` do for
the WRV shape into **one** stop, because the standing requirement is one operator stop per part,
not two. Claude derives the part's own facts from `rig-pins.json` — never from memory — and
states them to the operator: the part, the pin count, the JP4 position and, **only when this
position is a pot-group boundary** (PD-17: the 12 V→13 V transition, and no other position), the
VPP target and a request for **one** meter reading. The operator seats the part, sets JP4, and —
at a boundary only — adjusts the pot and reports back; Claude never adjusts the pot and never
runs a monitor loop. One clean re-seat is permitted per position (Standing bench rule 8), and
**both** the discarded attempt and the re-run are recorded, never just the re-run.

```
python3 -c "
import json
d = json.load(open('.planning/milestones/v1.34-artifacts/rig-pins.json'))
c = d['chips']['$CHIP']
print('part=$CHIP_TOKEN pin_count=%d package=%s vpp_target_mv=%d' % (c['pin_count'], c['package'], c['vpp_mv']))
"
```

Performer: operator (seating, JP4, pot). Record field(s): `jp4_position`, `reseat_count`,
`vpp_real_mv`.

### C-03 — One firmware VPP reading for this part

The arm's `vpp` subcommand, run **exactly once** per position, with the config-dir variable
inline. A blank or `0x303` reading is a **contact fault, not a voltage** (Standing bench rule 5) —
that is `P-H1`, not a pot adjustment. Never chase the database target upward: the firmware guard
is asymmetric — a reading above the target plus 500 mV is a blocking error downgradeable only by
a permanently withdrawn flag (`--force`, Forbidden invocations), while a reading below 95% of
target is a non-blocking warning.

```
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT vpp
```

Performer: Claude. Record field(s): `vpp_target_mv`, `vpp_firmware_mv`, `vpp_shortfall_mv`.

### C-04 — Capture provenance for this position

`capture_provenance.py` with this position's cell id, position id, arm, target, port, chip slug
and declared shield revision, plus `--no-image-plan` — a chip position writes the chip but
generates no pre-computed image, so it has no `IMAGE-PLAN.json` row to resolve (PD-9;
`--no-image-plan`'s help text is widened by this amendment, clause (8), to cover this shape).

```
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR python3 .planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id $CELL_ID --position-id $POSITION_ID \
  --arm v133 --target leonardo --port $PORT --chip $CHIP --shield-rev "$SHIELD_REV" \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --no-image-plan \
  --out $CELL_DIR/provenance_$POSITION_ID.json
```

Performer: Claude. Record field(s): the nineteen provenance columns.

### C-05 — Run dev test under the size-class ceiling, fully logged

One invocation, one argument, no flags — `dev test` takes exactly one argument (the chip token)
and one optional flag (`--fast`), and `--fast` is **forbidden here** because it disables the
two-cycle write/verify comparison and the read-divergence measurement this sweep most needs. The
config-dir variable is inline; the arm binary is the pinned absolute path, never the bare
`firestarter` name on `PATH` (Forbidden invocations). The invocation runs under a timeout derived
from PD-14's size-class ceiling, with full stdout **and** stderr captured into this position's own
numbered log pair. If the ceiling fires, the kill is logged with the last progress frame and
**which step was in flight** (PD-15), and recorded as `timed out at N s against a measured
baseline of M s` — write progress is time-keyed **per block** with the clock restarting each
block, so the last frame names a block, never a byte offset.

```
timeout <PD-14 ceiling for this size class, seconds> \
  env FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT dev test $CHIP_TOKEN \
  > $CELL_DIR/logs/$POSITION_ID.stdout.log \
  2> $CELL_DIR/logs/$POSITION_ID.stderr.log
echo "exit_code=$?"
```

Performer: Claude. Record field(s): `exit_code`, the per-step maps, `write_target`,
`write_coverage`, `banner`, `dedup_query_outcome`.

### C-06 — Read-divergence follow-up, only when the report says the two read runs diverged

`dev test` destroys its read bytes (`_dispatch_read` reads into a `TemporaryDirectory`), so only
the divergence metric survives (PD-7). When and only when this position's copied-out report
carries `read_divergence.repeat_divergent == true`, run **one** `dev consistency-check` at three
runs with the keep-files and output-directory arguments, on the **same seating and the same arm**,
before any re-flash, capturing the actual per-run bytes and SHAs. This is recorded as a data point
against the standing read-instability question and does **not** attempt to close it — never a
prompt to the operator, always automatic.

```
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT dev consistency-check $CHIP_TOKEN \
  --runs 3 --keep-files --output-dir $CELL_DIR/reads/$POSITION_ID
```

Performer: Claude. Record field(s): `read_divergence`, `read_consistency_followup`.

### C-07 — Append the row, then re-render and check

`append_chip_evidence.py` copies the `dev test` report out of the frozen config dir to a
position-keyed path under `$CELL_DIR`, verifies both copies' digests, removes the **two source
files only** (never the `reports/` directory itself), asserts the pristine config-dir digest
again, and appends the row to `bench/CHIP-EVIDENCE.jsonl`. `render_chip_evidence.py --check` runs
immediately after, as one pair. This ordering is the invariant: skip the removal and `C-01`'s
pristine assertion reds from the next position onward, and every already-appended row's recorded
`config_dir_sha` starts failing at the next `run_gates.sh` run.

```
python3 .planning/milestones/v1.34-artifacts/tools/append_chip_evidence.py \
  --position-id $POSITION_ID --arm v133 --chip $CHIP --chip-token $CHIP_TOKEN \
  --cell-dir $CELL_DIR --report-json <path to the dev-test report, pre-copy-out> \
  --report-md <path to the dev-test report's .md sibling, pre-copy-out> \
  --provenance $CELL_DIR/provenance_$POSITION_ID.json \
  --exit-code <C-05's measured exit_code> --console-log $CELL_DIR/logs/$POSITION_ID.stdout.log \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --jsonl .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.jsonl \
  --verdict-file <path|-> --anomalies-file <path|-> --vpp-real-mv "<C-02/C-03's value>" \
  --prior-disposition-file <path to this part's recorded v1.15-or-later disposition> \
  --divergence-verdict "<'same' or 'diverges: <reason>', per PD-16>" \
  --known-carried "<yes|no, per the pre-declared known faults>" \
  --jp4 <28-pin|32-pin> --reseat-count <C-02's measured value>
python3 .planning/milestones/v1.34-artifacts/tools/render_chip_evidence.py \
  --jsonl .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.jsonl --target .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.md
python3 .planning/milestones/v1.34-artifacts/tools/render_chip_evidence.py \
  --jsonl .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.jsonl --target .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.md \
  --check
```

Performer: Claude. Record field(s): the artifact paths and digests, `outcome`,
`divergence_verdict`.

### C-08 — Divergence arbitration, with the chip unmoved

When and only when this position's `divergence_verdict` begins with the diverging prefix
(`chip_sc04_rule`'s "divergence_verdict starts with 'diverges'"): `P-04` runs here, **twice, by
reference** (its literal argv is the block under the `### P-04` heading above, never copied) —
once flashing the **control** arm's `fw_sha` and judging its independent read-back against the
**control-arm-keyed** expected span, once re-flashing **back** to the v133 arm's `fw_sha` and
judging its read-back again. Between the two flashes, re-run the same part on the same seating
under the control arm, then append the control row naming the position it arbitrates. **Two
flashes per divergence, zero extra chip handlings** — the Leonardo is chip-out-exempt, so the part
stays seated throughout both `P-04` invocations and the control re-run between them. On a UV part
the control re-run lands on the **next slot down** (slot selection is stateless and keyed on chip
content) — record that, do not fight it.

```
# P-04 (by reference, see above) flashes the control arm's fw_sha and judges its read-back here.
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR $ARM_BIN -p $PORT dev test $CHIP_TOKEN \
  > $CELL_DIR/logs/$POSITION_ID.control-rerun.stdout.log \
  2> $CELL_DIR/logs/$POSITION_ID.control-rerun.stderr.log
python3 .planning/milestones/v1.34-artifacts/tools/append_chip_evidence.py \
  --position-id $POSITION_ID.control-rerun --arm control --chip $CHIP --chip-token $CHIP_TOKEN \
  --control-rerun-for $POSITION_ID --cell-dir $CELL_DIR \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --jsonl .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.jsonl \
  <the remaining flags, unchanged in shape from C-07>
python3 .planning/milestones/v1.34-artifacts/tools/render_chip_evidence.py \
  --jsonl .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.jsonl --target .planning/milestones/v1.34-artifacts/bench/CHIP-EVIDENCE.md
# P-04 (by reference) re-flashes and re-judges the v133 arm here, restoring the standing state.
```

Performer: Claude. Record field(s): `control_rerun_for`, `fw_readback_sha_judged`,
`fw_readback_judged_span_bytes`.

### C-09 — Per-wave gate

`run_gates.sh` with its exit code taken **directly**, never through a pipe.

```
bash .planning/milestones/v1.34-artifacts/tools/run_gates.sh --quick
RC=$?
echo "run_gates_rc=$RC"
```

Performer: Claude. Record field(s): the measured tool-selftest and live-gate counts and the exit
code.

---

## Outcome taxonomy

**Two axes, not one — and Phase 145 D-14's two-state ban is not being relaxed.**

- **Cell outcome** (the axis this procedure produces, Phases 160–163): exactly **two** states,
  `validated` or `skipped-with-reason`. Anything that is not a clean pass is a **fail**;
  anything not attempted is a **skip**. There is **no third state** at this axis. A cell result
  may never be recorded as `inconclusive` — `gate_record.py` enforces this domain mechanically.
- **Triage classification** (a *different* axis, Phase 165 only, RCA-01): the three-state axis
  — `v1.33-caused` / `pre-existing` / `inconclusive` — applied to a **failure**, after the fact,
  once a cell has already been recorded as `skipped-with-reason`. This axis never touches a
  cell result directly; it classifies a failure a cell result already named.

Stated explicitly: this milestone's Phase 165 triage requirement does **not** relax Phase 145's
prior ban on a third cell state. The two axes coexist because they describe different things —
one produced by this procedure, one applied later to a subset of what this procedure produced.

---

## Halt policy

Two branches, decided in advance so the distinction is never made under pressure mid-sweep.

### P-H1 — Rig failure: halt and fix in-phase

A **rig** failure — a read-back mismatch on a board that was correctly flashed, a judge
crashing, a provenance field missing or refusing to resolve, a gate that cannot read its own
input — **halts the sweep** and is fixed in-phase, because the rig is this phase's deliverable
and every later cell rests on it. Do not carry a rig failure forward; a broken oracle produces
meaningless results for every cell that follows it.

### P-H2 — Cell failure: record and carry forward

A **cell** failure — a write that fails, three reads that disagree, a chip that reds — is
recorded with its observed symptom (`skipped-with-reason`, never `inconclusive`) and **carried
to Phase 165**, and the sweep **continues** to the next position/cell. This is what makes
Phase 165's later classification possible at all — a cell failure that halted the sweep instead
of being recorded would leave nothing for RCA-01 to classify.

**The prior bench phase's policy of halting on any failure and handing to `/gsd-debug`
(Phase 145 D-13) is deliberately not inherited here.** That policy fit a phase with no
designated triage owner; this milestone has Phase 165 as that owner instead, so a cell failure
is data for Phase 165, not an interrupt for this phase.

---

## Write-duration definition

**Wall-clock around the write command is the judged measure.** It is the only measure that
exists for every arm, every target and every outcome — including a position where the write is
*expected* to fail on both arms (cell A2), where the app emits no success line at all. It is
also arm-agnostic by construction: one procedure step (`time $ARM_BIN -p $PORT write ...`), no
per-arm text.

The app's own success-only figure (`Write to {CHIP} successful ({t:.2f}s)`) is recorded
**alongside** it as a **second, unjudged datum**, whenever the write succeeds and the line is
present. State explicitly: wall-clock includes process start-up and the serial handshake, so it
is comparable **arm to arm** on this milestone's own rig, but it is **not** directly comparable
to v1.31's figure unless that figure was taken the same way.

**Which measure v1.31's 0.37 s W27C512 figure was, resolved from the record**
(`.planning/phases/145-bench-validation/145-BENCH-LOG.md`, "Positive findings" #2 and the
"v1.31 write timing" table): it is **not** a single write's duration. It is the **spread**
(max − min) across three full 64 KiB write cycles' **app-reported, success-only** figures —
106.06 s / 105.69 s / 106.06 s, each line read verbatim from
`Write to W27C512 successful ({t:.2f}s).` (`eprom_operations.py:1934`) — never an
independently-timed wall-clock measurement. Phase 145 made **no comparative claim** against any
earlier firmware with that figure (D-08 rejected a pre-v1.31 control run); it is cited here only
as *consistency*, not as a *duration*.

Consequence for this milestone's comparison: v1.34's per-position wall-clock figures are a
**different quantity** (a single measured duration per position, not a three-cycle spread) taken
by a **different method** (independent wall-clock, not the app's own success line) than v1.31's
0.37 s. **Honesty-ledger line for Phase 166:** any figure-to-figure comparison drawn between
v1.34's wall-clock durations and v1.31's 0.37 s figure compares a duration to a spread and a
wall-clock measurement to an app-reported one; it is not an apples-to-apples regression check
and must be stated as such rather than drawn silently. v1.34's own app-reported figures
(recorded alongside wall-clock per position, per this section's first paragraph) are the
directly comparable quantity to v1.31's, and even that comparison is valid only on the one cell
this milestone shares with v1.31's rig — `A3/B2`, Leonardo + Rev 2.0.

---

## Forbidden invocations

Every flag and binary below is **never** used in a bench command, each for a stated reason.
`gate_record.py` rejects any recorded command line carrying a forbidden flag by exact token
match, regardless of its position in the argv.

| Forbidden | Reason |
|---|---|
| `--force` / `-f` | Phase 145 D-17 withdrew the standing permission to force past a guard, permanently. A guard-blocked run (e.g. the W27C512's `VPP is high` init guard) is a bench fault fixed in pre-flight (`P-06`), never bypassed. |
| `-b` / `--no-blank-check` | Skips the pre-write blank check. Has no place in a normal position — every position writes a fresh, known image and the blank check is part of what proves that. **Superseded-framing correction:** this flag does **not** also skip the erase (an older standing memory said otherwise); the erase is now a separate flag (Phase 153) and the current help text is explicit that the erase **still runs** when `-b` is given. This procedure names the current behaviour, not the superseded one. |
| `--skip-erase` | Skips the pre-write erase entirely. Its own help text warns it "leaves un-erased bits that cannot be reprogrammed" on a non-blank electrically-erasable chip while the write still reports success — the exact false-green shape this milestone's oracle design (D-12) exists to avoid. |
| bare `firestarter` | Resolves to the pre-existing user-site editable install (`/home/vscode/.local/bin/firestarter` → `/workspaces/firestarter_app`), a **third, un-named arm** on `PATH`. Every bench command names an arm venv's absolute binary path (`$ARM_BIN`) instead. |
| `firestarter fw -i` (the host app's own firmware-install path) | Requires a firmware handshake (which blocks the D-03 deliberate cross-flash, since a mis-flashed board cannot handshake correctly by design), ignores its own `--board` argument, and omits `urclock`'s `-x nometadata` option — producing **different flash content** from the PlatformIO path on `uno328pb`. This procedure flashes only via `pio run -t upload -e $TARGET` (`P-04`). |
| the stale `tool-avrdude@1.60300.200527` (avrdude 6.3) | Predates the `urclock` programmer entirely; cannot flash or read `uno328pb` correctly. The rig's pinned avrdude is `rig-pins.json`'s `avrdude.binary` (8.1), with `avrdude_fallback` (system 7.1) named only as a fallback, not used unless the pinned binary fails to open the port. |
| any `pio` invocation whose working directory is not `rig-pins.json`'s `pio_project_dir` (`/workspaces/firestarter`) | The generated, untracked, gitignored `/workspaces/platformio.ini` has a duplicate `[platformio]` section that makes `configparser` abort — the identical command string succeeds or fails depending on cwd alone (Pitfall 4, reproduced live). Every `pio` command in this procedure is recorded with its working directory. |
| any `import firestarter` probe run without `python -P` | `/workspaces` contains a directory literally named `firestarter` (the firmware repo) that wins as a PEP 420 namespace-package portion, so the probe silently prints `None` on every interpreter without `-P` (Pitfall 1). Every such probe in this procedure and its tools carries `-P`. |

---

## Recording discipline

Carried forward from the prior bench phase's standing anti-fabrication rule, restated here as a
binding rule for this procedure rather than a norm:

- **Nothing here is fabricated.** A reading that tooling blocks — because a bootloader
  interrogation has not yet been recorded (`judged_span_policy: PENDING-xshowvector` on
  `uno328pb`), because a CLI path does not exist for a value (the R16/R14R15 ohm calibration
  values), or for any other named reason — is recorded as `"not measured — <reason>"` **on the
  same line**, never as a blank. `gate_record.py`'s field-presence check treats this exact
  shape as a valid, non-null value.
- **A negative control is recorded as having FIRED, not as having been configured.** The
  W27C512's VPP-high init guard, and the deliberate wrong-arm cross-flash's MISMATCH, are both
  examples: the record states that the guard/mismatch actually occurred and what happened next,
  not merely that the mechanism which could produce it was present.
- **The judged verdict and the unjudged verdict are recorded separately, and their
  disagreement is itself a finding** — never resolved by preferring one over the other. This
  applies identically to `judge_readback.py`'s judged-span-vs-whole-flash pair and to
  `judge_wrv.py`'s SHA-verdict-vs-app-verdict pair (`verdict_disagreement`).
- **Every recorded command is the literal argv with its working directory.** A `pio` command's
  cwd is part of its record for the same reason Pitfall 4 exists: the same string can succeed or
  fail depending on it.
- **No SHA is ever transcribed by hand.** Every SHA in a cell's record is computed by a tool
  and written by that tool, never copied by a human from one file into another.

---

*Procedure defined: 2026-08-26, Phase 160 Plan 06.*

**Amendment 1 — 2026-08-27, Phase 160 Plan 09:** (a) Standing bench rule 1 and the `$PORT`
token row were widened from `/dev/ttyACM*`-only wording to also name `/dev/ttyUSB*`. (b) The
`uno328pb` bring-up board (this plan) enumerates via a CH340 USB-serial bridge as `ttyUSB0`,
not `ttyACM*` — the rule's substance (never inherit a port across cells/sessions) was already
node-class-agnostic, only the illustrative wording named one class. No mechanical step changed
and no `## Step list` text moved, so this amendment does not affect the SC#3 empty-diff render
gate. (c) Every bring-up cell before this one (`BRINGUP-uno`, plan 08) ran under the old
wording; no real sweep cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run yet under either wording.

**Amendment 2 — 2026-08-27, Phase 160 Plan 13:** (a) What changed: `P-11`'s teardown gained a
literal command block for the `probe_board.py` re-run its prose already prescribed ("re-run
`probe_board.py` to confirm the board identity has not changed since `P-02`"), naming an
explicit, distinct output path (`$CELL_DIR/board_probe_teardown.json`). Every other step in
this list (`P-02`, `P-04`, `P-06`, `P-07`, `P-09`) already carried a literal command block; `P-11`
was the one exception, describing the re-probe only in prose. (b) Why: RIG-05's D-17
fresh-context reconstruction (`bench/cells/BRINGUP-wrv/RECONSTRUCTION.md`,
`RECONSTRUCTION-DIFF.md`) surfaced this as a prescription ambiguity — a fresh context given
only the provenance record and this procedure had to invent an output filename by analogy to
`P-02`'s, because the procedure itself gave none. A step whose literal command must be inferred
by analogy rather than read is exactly the failure mode this document's "prescriptive, not
prose" contract exists to prevent. (c) Which cells ran under which text: every bring-up cell
that has run so far (`BRINGUP-uno`, `BRINGUP-uno328pb`, `BRINGUP-leonardo`, `BRINGUP-wrv`) ran
under the OLD (prose-only) `P-11` text; `BRINGUP-wrv`'s own teardown (Phase 160 Plan 12) in
fact never re-ran `probe_board.py` at teardown at all, only the config-dir check — a genuine
compliance gap against the prose prescription, discovered by this same reconstruction exercise
and recorded, not backfilled, in `RECONSTRUCTION-DIFF.md` (backfilling it now would require an
avrdude signature probe against a board this phase's own constraints forbid touching with a
chip seated). No real sweep cell (`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run yet under either text.
No `## Step list` text outside `P-11`'s own body moved, and the arm-agnostic empty-diff render
gate (`render_steps.py --arm control` vs `--arm v133`) was re-confirmed empty after this edit —
the new command block carries no arm-dependent token (`probe_board.py` takes no `$ARM_BIN`).

**Amendment 3 — 2026-08-27, Phase 161 Plan 01:** (a) What changed: (1) **(D-06)** The
`EVIDENCE.jsonl` append moves out of `P-11` and into `P-07` and `P-09` — one row per
position, written by `append_evidence.py` as that position completes, each append
immediately paired with a plain `render_evidence.py --jsonl … --target …` re-render in the
same step. `P-11` becomes a **completeness assertion**: all four of this cell's rows are
present in `bench/EVIDENCE.jsonl`. (2) **(D-12)** `P-11` gains a general, **cell-agnostic**
requirement: declare and record the leave-state — board, port, arm, chip seated, pot,
shield. The concrete value is supplied by the executing phase's own plan, never by
conditional text here. (3) **(per-position paths)** `P-07`'s and `P-09`'s `--output-dir`,
`--reads`, `written.bin` and verdict paths become `$POSITION_ID`-keyed. The shared
`$CELL_DIR/reads`, `$CELL_DIR/written.bin` and `$CELL_DIR/wrv_verdict.json` in both step
bodies become `$CELL_DIR/reads/$POSITION_ID/` (read set **and** the position's
`written.bin`) and `$CELL_DIR/WRV-VERDICT_$POSITION_ID.json`. The verdict filename is
`WRV-VERDICT` in capitals, matching `BRINGUP-wrv` and D-05, never the lowercase
`wrv_verdict.json` the old blocks showed. The measured layout rationale:
`bench/.gitignore` is exactly `cells/*/reads/` and `cells/*/written.bin`, so a
`positions/<id>/` directory would **not** be ignored and would silently commit ~12 large
binaries, while everything under `reads/<id>/` stays ignored and the committed records
(`provenance_<id>.json`, `WRV-VERDICT_<id>.json`) stay outside it. (4) **(`~/.firestarter`)**
`P-11` teardown assertion (1) of 2 is restated from "assert `~/.firestarter` still does not
exist" to "assert `~/.firestarter` is **unchanged from the recorded baseline**", with the
baseline pinned inline: path `/home/vscode/.firestarter`; exactly one file, `config.json`,
30 bytes; `config.json` sha256
`b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79`; tree sha (sorted
relpath plus content) `423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951`;
mtime `1787817565` (`2026-08-27 07:59:25 UTC`). A **change** to any of those is the `P-H1`
finding. Deletion is never attempted — the sandbox denies it and deleting destroys the
evidence. Assertion (2), the frozen `FIRESTARTER_CONFIG_DIR` content SHA
(`77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`, checked via
`check_arms.py --expect-config-sha`), is unaffected and stays exactly as written. (b) Why:
(1) a kill after position 3 loses all four rows' assembly and `EVIDENCE.jsonl` silently
lags the bench, which is what D-15's append-only design exists to prevent. (2)
cell-conditional text is the same shape as the arm-conditional text this document forbids.
(3) `judge_wrv.load_reads()` globs `run_*.bin` in `--reads` and counts what it finds, so
`P-09` would see `P-07`'s three 65536 B files and record a `size_violations` that makes
`match` unreachable, and across the arm switch a surviving `run_01.bin` from a different
mask would record an N=3 `disagreement` that never happened. (4) the directory exists on
this container right now, a Phase 160 disclosed carry-forward, so the assertion as
literally written is unconditionally red and would book twelve false `P-H1` halts. (c)
Which cells ran under which text: every bring-up cell (`BRINGUP-uno`, `BRINGUP-uno328pb`,
`BRINGUP-leonardo`, `BRINGUP-wrv`) ran under the pre-Amendment-3 text; **no real sweep cell
(`A1`/`A2`/`A3-B2`/`B1`/`B3`) has run under either text** — Amendment 3 lands before the
first sweep cell, so every sweep cell in this milestone runs under the new text. The
arm-agnostic empty-diff render gate (`render_steps.py --arm control` vs `--arm v133`) was
re-confirmed empty after this edit — none of the four clauses adds an `[arm: …]` marker or
an `$ARM_BIN` token, and `$POSITION_ID` is already declared among the non-arm-dependent
substitution tokens in `## Arm substitution`.

**Amendment 4 — 2026-08-28, Phase 162 Plan 04:** (a) What changed: (1) The header sentence and
§Scope corrected to name two cell shapes — the WRV cell Phases 161/163 run, and the chip-sweep
position Phase 162 runs instead, with `P-07`/`P-09` stated as not applying to it at all. (2) A new
`## Chip-sweep step list` H2 added, carrying `C-01`…`C-09`, sharing `P-01`/`P-02`/`P-04`/`P-06`/
`P-11` **by reference** and listing `P-03`/`P-05`/`P-07`/`P-08`/`P-09`/`P-10` as explicitly
**not applicable**, each with its own reason. (3) The `$CHIP` token row in `## Arm substitution`
widened from the two-part WRV list (`w27c512` / `w29c020`) to the full eleven-part inventory, and
a new token `$CHIP_TOKEN` declared alongside it — the case-sensitive CLI token as typed, with the
case-sensitivity reason stated in the table. (4) `P-06`'s once-per-cell pot rule **superseded
per-part for the chip-sweep shape only** (D-11/D-13): every part records its own firmware VPP
reading via `C-03`; the meter comes out only at the two pot-group boundaries (`C-02`); every other
position records `vpp_real_mv` as a named absence naming the boundary position and the group's
meter-to-firmware ratio, never a copied number. The `P-06` text itself is unchanged; the
supersession lives in `C-02`/`C-03` and here. (5) `P-11`'s completeness assertion **retargeted for
the chip-sweep shape** to `bench/CHIP-EVIDENCE.jsonl` and `render_chip_evidence.py --check`
(`C-07`/`C-09`), and its assertion (2) — the recomputed config-dir SHA — is now **load-bearing**
for the copy-out invariant (clause (7) below) rather than merely confirmatory. The `P-11` text
itself is unchanged; the retarget lives in `C-07`/`C-09` and here. (6) The
`~/.firestarter/config.json` mtime baseline re-pinned inside `P-11`'s assertion (1), from
`1787817565` (`2026-08-27 07:59:25 UTC`, the Amendment-3 value) to `1787854674`
(`2026-08-27 18:17:54 UTC`, measured at the moment this amendment was written) — the **fourth**
recurrence of this drift, the first three being Phase 161's cells `A1`, `A2` and `A3/B2`.
`config.json`'s content sha256 (`b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79`)
and the tree sha (`423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951`) are
**unchanged** across all four recurrences. (7) The config-dir copy-out invariant (R3/PD-3) stated
as a step obligation, not merely an implementation detail of one tool: assert pristine before
(`C-01`), copy out, verify, remove the two source files (`C-07`), assert pristine after (`C-07`'s
own re-check, and `C-01`'s next position). (8) `--no-image-plan`'s documented rationale widened
(`C-04`) to cover a chip-sweep position, which writes the chip but has no pre-computed image row
— the mechanism already fit; only the flag's own help text's stated scope did not.

(b) Why: (1) the header and §Scope claim of "executed unchanged by Phase 162" was false the moment
Phase 162 began running a different command over a different step shape; leaving it standing would
have let a later reader believe `## Step list`'s `P-NN` prescriptions applied verbatim to a chip
position, when roughly half do not apply at all. (2) `render_steps.py`'s `_STEP_ID_RE` is anchored
to the `P-NN` shape and `validate_steps()` raises `ProcedureParseError` on anything else — a `C-NN`
heading placed inside the Step list section would have **reded the live gate for the rest of the
milestone** (RESEARCH R6's blocking finding); the new section's own H2 keeps `_NEXT_H2_RE` from
ever bleeding the two sections into each other, and `render_steps.py` (Task 1, this plan) was
taught the second section precisely so the re-confirmation below is not a vacuous pass over text
the gate could not see. (3) a lower-case or differently-cased chip name invoked at the CLI would
otherwise write a report file the appender never reads, silently losing the position's own
evidence — declaring `$CHIP_TOKEN` separately from `$CHIP` and pinning it per part in
`rig-pins.json` closes that gap once, in the document both the operator and the tool read. (4)
per-part VPP figures are materially better evidence for Phase 166's honesty ledger than a single
once-per-cell figure asserted to cover nine dissimilar parts; the meter itself is scarce (operator
time, one physical action) so it is spent only at the two points where the target actually
changes. (5) `P-11`'s literal text names `bench/EVIDENCE.jsonl` and `render_evidence.py`, neither
of which a chip position ever writes; retargeting the *chip-sweep application* of the same
completeness idea, without touching `P-11`'s own prose, keeps the shared-by-reference contract
honest (clause (a)(2) above) while still asserting completeness for the shape that actually runs.
(6) Amendment 3 clause (4) pinned `1787817565`; a live measurement taken while drafting this
amendment reads `1787854674` — content and tree digests unchanged — so `P-11` assertion (1) as
literally written was **unconditionally red before this phase starts** and would have booked a
false `P-H1` halt at every one of the (up to) eleven chip-sweep positions. The mtime is the
**only one of the four values that has ever changed**; dropping it from the assertion, rather than
re-pinning it, would make the assertion vacuous — the same vacuous-pass shape the two-assertion
design (Standing bench rule 9) exists to close. A further change **during** this phase is this
phase's own `P-H1` finding, not a fifth false recurrence. Removal is never attempted: the sandbox
denies it, and Phase 160's one unlogged kill during a removal attempt is what contaminated the
directory in the first place. (7) `check_arms.compute_config_dir_sha()` walks every file under the
frozen config dir; a `dev test` report left in place after this position's row is appended would
permanently corrupt the pinned digest for every position that follows it, so the copy-out-then-
remove sequence has to be a **prescribed obligation** of the step list, not an incidental property
of `append_chip_evidence.py`'s implementation. (8) the flag's own help text scoped it to "a
bring-up pre-proof cell that never generates a chip image (no chip write ever runs here)" — a
chip-sweep position does write the chip, so the mechanism (an explicit not-measured placeholder
naming the reason) fits but the stated rationale did not, and a future reader should not have to
infer why a "no write" flag is used on a step that writes.

(c) Which cells ran under which text: `A1`, `A2` and `A3/B2` ran under the Amendment-3 text and
are **unaffected** — Amendment 4 adds a new `## Chip-sweep step list` H2, corrects the header
sentence and §Scope, widens `## Arm substitution`'s `$CHIP` row and adds `$CHIP_TOKEN`, and changes
**exactly one value** inside the Step list section (the `~/.firestarter` mtime baseline in `P-11`),
which those three cells asserted against a value reality had already overtaken before this phase
began. No prescription any of `A1`, `A2` or `A3/B2` executed has changed, and every `### P-NN —
<title>` heading is byte-identical to what those three cells cited. `B1` and `B3` (Phase 163) will
run under the Step list section at the Amendment-4 text, which for them is identical in substance
to the Amendment-3 text they would otherwise have run under. **No chip-sweep position has run
under any text** — Amendment 4 lands before the first one, so every chip-sweep position in this
phase runs under the new `## Chip-sweep step list` section from its first invocation.

The arm-agnostic empty-diff render gate (`render_steps.py --arm control` vs `--arm v133`) was
re-confirmed empty after this edit, for **both** sections (`--section P` and `--section C`), and it
stays empty because **no new text in either section carries an `[arm: …]` annotation marker** —
the marker, not the arm-binary token, is the mechanism that makes a render differ. Every
substitution token this amendment adds or widens (`$CHIP`, `$CHIP_TOKEN`) is emitted as literal
token text in the render, never expanded, and is therefore diff-neutral by the same construction
`## Arm substitution` already documents for every other non-arm-dependent token.
