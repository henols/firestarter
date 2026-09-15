# Cell A2 — uno328pb (ATmega328PB) on Rev 2.0 shield — the expected-failure cell

Runs `P-01`..`P-11` per `.planning/milestones/v1.34-artifacts/PROCEDURE.md` (Amendment 3), control arm then v1.33,
W27C512 then W29C020, four evidence positions. This is the milestone's expected-failure cell
(Backlog 999.2): the requirement is that the failure be **observed**, not assumed.

## P-01 — Mount and declare (2026-08-27)

**Precondition, inherited from cell A1's own recorded teardown leave-state** (Task 15,
`161-03-SUMMARY.md` / `bench/cells/A1/CELL.md`): A1's Uno-class chip socket was confirmed
**EMPTY** at A1's own teardown (both chips pulled, no chip re-seated afterward). The Rev 2.0
shield carries its socket with it when moved, so that empty state travels with the shield.

**Orchestrator-measured bus state** (sysfs USB descriptors, read-only, 2026-08-27T14:25:33Z):

| Node | Descriptor | State |
|---|---|---|
| `/dev/ttyUSB0` | `1a86:7523` "USB Serial" (CH340) | LIVE — the uno328pb, THE ONLY LIVE NODE |
| `/dev/ttyACM0` | — | ABSENT (Leonardo removed by operator) |
| `/dev/ttyACM1` | — | ABSENT (A1 Uno removed by operator) |

**Independently re-confirmed by Claude** (2026-08-27T14:27:53Z, this task): `ls /dev/ttyACM*` ->
no such file (both absent); `/dev/ttyUSB0` present, `1a86:7523`, mtime `2026-08-27 14:24:30 UTC`
(`readlink -f /sys/class/tty/ttyUSB0/device` walked to the `idVendor`/`idProduct` files directly,
not merely quoted from the orchestrator's figure) — matches the orchestrator's measurement
exactly. **Only one node is live this cell**, but every avrdude/probe/tool invocation below still
passes an explicit `--port`/`-P`/`-p` `/dev/ttyUSB0` — never autodetected, per Standing bench rule
1 and this phase's own prior finding (nodes have shuffled multiple times already).

**Operator statement, recorded verbatim:** "uno328pb is connected and rev 2.0 shiled is on"
(operator's own spelling; the intended word is "shield"). This confirms: the board is connected,
and the Rev 2.0 shield is now mounted on the uno328pb — i.e. the shield has been moved from the
A1 Uno onto this board.

**Declared shield revision** (`shield_rev_declared`, becomes this value on all four A2
positions): **`Rev 2.0`** — normalized from the operator's "rev 2.0" to the canonical
capitalization used everywhere else in this project's record; no other normalization applied.
Silkscreen is authoritative per Standing bench rule 6; the operator's statement is the silkscreen
declaration for this cell.

**Socket-empty confirmation for the Uno-class chip-out precondition (`P-03`, control-arm
pass):** established by the conjunction of (a) A1's own teardown-confirmed empty-socket
leave-state (the state that traveled with the shield) and (b) the operator's statement above,
which reports the shield as mounted with no chip-seating action described. No chip has been
seated on this board at any point in this cell's history to date. `P-03` is therefore satisfied
as a **one-line no-op re-confirmation**, not a second gate — Task 3 (`161-04-PLAN.md`) explicitly
prescribes this shape, mirroring A1's own `P-01`-satisfies-`P-03` precedent.

**`$PORT` for this cell:** `/dev/ttyUSB0`
**`$SHIELD_REV` for this cell:** `Rev 2.0`
**`$TARGET` for this cell:** `uno328pb`

**Pre-cell arm integrity capture** (log `00_check_arms_pre_cell`): `check_arms.py` exit 0, both
arms verified (SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha+cli-surface). `control`
HEAD `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a`, `v133` HEAD
`cb189a9b001e9e34fb7651535de339761301d061`, `config_dir_sha`
`77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0` — matches the frozen pinned
value. `surface_diff_ab`/`surface_diff_ba` both empty; 25/25 CLI surface parity both arms. See
`check_arms_pre_cell.json`.

**Standing carve-out restated (D-07 safety):** this cell is expected to fail its W27C512 write on
both arms — that is the point of running it. The operator was informed at this checkpoint that
the 32-pin part swap later in this cell is conditioned on their own safety judgement of the board
after the W27C512 attempt (Task 6/Task 12's `P-08` gates carry this explicitly).

## P-02 — Board identity + pending provenance, all four positions (2026-08-27)

**Signature probe** (log `01_probe_board`): `board_probe.json` — `connected_part=atmega328pb`,
`board_signature=0x1e9516`, `mcu_matches=true`, `signature_route=route1`. Matches the expected
constants exactly and matches the operator's declaration.

**Control-arm `hw` probe** (log `02_hw_probe_pre_flash`, config dir inline): rc=0,
`Hardware revision: Rev 2.0-class` — the non-authoritative controller-string datum, recorded
alongside the authoritative signature probe. It agrees with the operator's silkscreen
declaration ("Rev 2.0"), a useful (non-authoritative) cross-check.

**Provenance captured for all four positions**, each with `--pending-readback` and its own
`--arm`/`--chip`/`--out`, `--cell-id A2`, `--target uno328pb`, `--port /dev/ttyUSB0`,
`--shield-rev "Rev 2.0"`:

| `position_id` | file | rc | `captured_at_step` |
|---|---|---|---|
| `A2__control__w27c512` | `provenance_A2__control__w27c512.json` | 0 | 2 |
| `A2__control__w29c020` | `provenance_A2__control__w29c020.json` | 0 | 2 |
| `A2__v133__w27c512` | `provenance_A2__v133__w27c512.json` | 0 | 2 |
| `A2__v133__w29c020` | `provenance_A2__v133__w29c020.json` | 0 | 2 |

Verified: `board_signature` matches `rig-pins.json`'s `targets.uno328pb.mcu`; exactly four
`provenance_A2__*.json` files exist with no default `provenance.json` collision; each record's
`captured_at_step==2`, `cell_id=="A2"`, `target_env=="uno328pb"`; each record's `arm`/`chip`
match its own `position_id`; each record's `image_mask`/`image_stamp_width`/`image_sha` equal
`IMAGE-PLAN.json`'s row (masks 20/21/22/23); each record's `fw_sha`/`host_arm_sha` equal
`rig-pins.json`'s pinned values for its own arm.

## P-03 (control pass) — satisfied by P-01, no second gate

Already recorded above: the socket-empty confirmation established at `P-01` covers this pass.

## P-04 (control) — flash + independent read-back judge (2026-08-27)

**Firmware checkout** (log `07_pio_upload_control` covers steps 2-3): `git -C
/workspaces/firestarter checkout 8695ee52c27a4bee4387c5c489afd5f3d7275e8a` — pre-checkout HEAD was
`5759dc8d...` (v133, A1's leave-state); post-checkout HEAD `8695ee52c27a4bee4387c5c489afd5f3d7275e8a`,
equal to `arms.control.fw_sha`; porcelain empty both before and after.

**Flash** (`pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0`, cwd
`/workspaces/firestarter`): rc=0, "1 succeeded in 00:00:09.288". Build report: `Flash: 79.6% (used
26074 bytes from 32768 bytes)` — matches the control arm's expected hex span (26074) exactly.
PlatformIO resolved `urclock`/avrdude 8.1 and supplied its own flags; the host app's own
firmware-install path was never used.

**Independent read-back judge** (`judge_readback.py --target uno328pb --port /dev/ttyUSB0
--flashed-arm control --expect-arm control --out-dir $CELL_DIR --pins rig-pins.json`, log
`08_judge_readback_control`): rc=0.

- `judged_match`: **true**
- `judged_span_bytes`: **26074**, read at assertion time from `hex_span_expected_by_arm.control`
  — **not** the legacy scalar 23000 (`targets.uno328pb.hex_span_expected`)
- `vector_exclusions_applied`: both entries present (offset 0 length 4 — reset vector; offset 100
  length 4 — SPM_Ready/vector 25), unchanged from the control-arm-derived `-xshowvector`
  interrogation recorded in `rig-pins.json`
- `readback_size_bytes`: 32768; `flash_readback.bin` on disk: 32768 bytes — matches
- `sha_actual_judged` (`43dcb663...`) and `sha_expected_judged` (`b18a7151...`): recorded, **never
  compared** — this target's 8 excluded bytes (`[0,4)`, `[100,104)`, both in the vector table) make
  the two raw-span SHAs unequal on a *correct* flash; comparing them would be the exact false-RED
  Pitfall 4 names, and this task did not do it.

**Standing disclosed non-claim (carried, not raised as a new A2 finding):** the 8-byte
vector-exclusion blind spot (`[0,4)` + `[100,104)`, 8 of 26074 judged bytes on this arm) means a
fault confined entirely to those 8 bytes is invisible to A2's judged verdict. This is a Phase 160
§6 disclosed limit, proven live already on this exact silicon (`BRINGUP-uno328pb-v133/PREPROOF.md`,
plan 161-02) — carried here unchanged, not re-raised.

**Provenance patched, control positions only:** `A2__control__w27c512` and `A2__control__w29c020`
now carry `fw_readback_sha_judged == 43dcb663...` (the control verdict's `sha_actual_judged`),
`captured_at_step` still `2`. The two v1.33 positions' provenance are **untouched** — both still
carry the `--pending-readback` placeholder, confirmed above.

## P-05 / P-06 — Seat W27C512, pot confirmed against the firmware guard window (2026-08-27)

Operator (via coordinator relay): "seated and set, 12.0V" — W27C512 (DIP28) seated in the Rev
2.0 socket on the uno328pb at `/dev/ttyUSB0`; pot reported set and reading 12.0 V.

Claude's single confirming `vpp` read: **11.9 V** (first reported reading; band 11.8-11.9V across
the brief capture, no monitor loop). Judged against the firmware-derived accepted window
`[11.4, 12.5]` V for a 12000 mV target (`firestarter/src/proms/eprom.cpp:713` HIGH guard
`target+500mV`, `:736` LOW guard `target*95/100`), **not** string-equality to the target —
**in band**. Full detail, including a corrected first determination recorded honestly rather than
silently rewritten, in `POT.md`. `--force used? No.`

**Avrdude window now closed:** the W27C512 is seated. From this point no avrdude operation of any
kind (upload, read-back, or signature probe) may run on this board until the chip comes out again
at Task 6's swap (`P-08`).

## P-07 (control x W27C512) — position 1 of 4: observed, not asserted (2026-08-27)

Full detail in `WRITE.md` ("Position 5 (1 of 4)"). Summary: the write's INIT phase completed
(65536/65536 B queued), but the MAIN (chip-program) phase stopped at the exact first-block
boundary (0x0200/512 B) and the app's own internal serial-response timeout fired — wall-clock
**15.813 s**, wrapper exit code **1** (not 124 — the D-08 165 s ceiling was never approached). A
subsequent read succeeded (rc=0) and shows exactly 431/512 bytes of the first block were actually
programmed before the stall, everything from the second block onward reading fully erased.

**Matches Backlog 999.2's block-position prediction** (stops on the first program block) while
being materially more precise (bounded by the app's own ~15.8 s internal timeout, not an
unbounded hang; measured at 431/512 bytes into that block, not just "the block").

`judge_wrv.py`: `sha_verdict_judged=mismatch` (expected), `verdict_disagreement=true` (the read
command's own exit code 0 disagrees with the judged mismatch — recorded as a finding, not
resolved). `EVIDENCE.jsonl` row appended, `outcome=skipped-with-reason` (computed, not hand-set).
`render_evidence.py --check`: green.

## P-08 — Swap to W29C020 (2026-08-27, operator)

Operator, verbatim: "W29C020 seated". W27C512 (DIP28) removed, W29C020 (DIP32) seated on the
uno328pb at `/dev/ttyUSB0`. **D-07 safety judgement: the operator inspected the board before the
swap and affirmatively raised no concern** — this is an operator clearance actively given at this
gate, not a silent absence of objection. **Pot not touched** — Task 4's single confirming read
(11.9 V, in band against the firmware guard window) stands for the whole cell; no second `vpp`
invocation was run for this swap.

## P-09 (control x W29C020) — position 2 of 4: the first algorithm-0x05 attempt, a different failure mode (2026-08-27)

Full detail in `WRITE.md` ("Position 6 (2 of 4)"). Summary: **not predictable from position 1** —
a genuinely different failure mechanism. The **firmware itself** reported a verify-timeout error
(`ERROR: Timeout verifying 0x15 at 0x00007f (got 0x13)`), not a bare host communication timeout.
Wall-clock **4.019 s**, wrapper exit code **1** (the derived 391.748 s ceiling was never
approached). The subsequent read **also failed** (rc=1, partial 113152/262144 B) — contradicting
position 1's "the READ path works" observation, not re-asserting it. Byte 0x7f in the partial
read-back independently confirms the firmware's own quoted stop value (`0x13`). The bulk of the
partial read correlates ~65% with a freshly-generated copy of `A1__v133__w29c020`'s own image
(mask `0x13`, matching the stop-point byte) — flagged as an unconfirmed observation for Phase
165's RCA (possible residual chip content from A1's earlier use of this physical part), not
asserted as a proven cause.

`judge_wrv.py`: `sha_verdict_judged=mismatch`, `size_violations` **non-empty** (113152 bytes, not
262144) — this diverges from the plan's own stated acceptance-criteria assumption of an empty
`size_violations` list, which did not anticipate a partial (truncated) read as a real outcome;
recorded honestly rather than forced to match the template. `app_verdict_unjudged=1` **agrees**
with the judged mismatch this time (`verdict_disagreement=false`), unlike position 1's
disagreement. `EVIDENCE.jsonl` row appended, `outcome=skipped-with-reason`. `render_evidence.py
--check`: green.

**Both of cell A2's control-arm positions have now failed, by two distinct mechanisms** — a host
serial-response timeout (W27C512) and a firmware-reported verify timeout (W29C020) — neither a
clean electrical brownout with zero response, both bounded well under their respective D-08
ceilings.

## P-10/P-04 (v1.33) — arm switch, preserve control read-back, flash v1.33, judge (2026-08-27)

**Control read-back set preserved** into `readback_control/` (all six cell-root artifacts,
copied — not moved — before the v133 flash overwrites them), mirroring cell A1's own precedent.

**Firmware checkout:** `git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`
— pre-checkout HEAD `8695ee52...` (control); post-checkout HEAD `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`,
equal to `arms.v133.fw_sha`; porcelain empty both before and after.

**Flash** (`pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0`, cwd
`/workspaces/firestarter`, log `22_pio_upload_v133`): rc=0, "1 succeeded in 00:00:08.124". Build
report: `Flash: 70.2% (used 23000 bytes from 32768 bytes)` — matches the v133 arm's expected hex
span (23000) exactly.

**Independent read-back judge** (`judge_readback.py --target uno328pb --port /dev/ttyUSB0
--flashed-arm v133 --expect-arm v133 --out-dir $CELL_DIR --pins rig-pins.json`, log
`23_judge_readback_v133`): rc=0.

- `judged_match`: **true**
- `judged_span_bytes`: **23000**, read at assertion time from `hex_span_expected_by_arm.v133` —
  **not** the legacy scalar `hex_span_expected` (which for this target numerically **equals**
  23000, the specific trap this target carries — using it would have silently passed a
  wrong-arm judgement on the control side; it was not used)
- `vector_exclusions_applied`: both entries present, unchanged
- `sha_actual_judged` (`bbf7aa68...`): **exact match** to plan 161-02's D-10 pre-proof
  (`BRINGUP-uno328pb-v133/PREPROOF.md`, same value) — an independent consistency confirmation
  that this cell's v133 flash reproduces the already-proven pre-proof result byte-for-byte.
  `sha_expected_judged` (`75382672...`): recorded, **never compared** to `sha_actual_judged` (this
  target's expected inequality on a correct flash, per Pitfall 4)
- **D-10 is closed** (plan 161-02): a v1.33 flash on an ATmega328PB judging a match at span 23000
  is already proven. This flash **reproduces** that result exactly — consistent with a correct
  flash, not merely an untested tool passing by chance.

**Provenance patched, v1.33 positions only:** `A2__v133__w27c512` and `A2__v133__w29c020` now
carry `fw_readback_sha_judged == bbf7aa68...`, `captured_at_step` still `2`. The two control
positions' provenance remain patched to the **control** verdict's SHA (`43dcb663...`) —
confirmed distinct and unaltered by this step.

## P-07 (v1.33 x W27C512) — position 3 of 4: the A/B half, a rule-8 re-seat, and a different mechanism (2026-08-27)

Full detail in `WRITE.md` ("Position 7 (3 of 4)"). Summary: **attempt 1** failed at INIT with a
firmware-reported chip-ID mismatch (`0x303` vs expected `0xda08`) — matching this project's own
standing contact-fault signature. **One clean re-seat performed** under Standing bench rule 8
(operator reported "reseated," no specific physical defect identified — recorded honestly as
"suspected," not "confirmed"). This chip's fifth insertion across A1 and A2 by this point.

**Attempt 2 (the one permitted re-run)** got past INIT and the full transfer, then failed with a
**firmware-diagnosed** program-convergence error at address `0x000179` ("failed to program within
25 pulses... usually means insufficient program voltage or a worn or failing cell, not a timing
problem") — wall-clock **10.245 s**. **This is a genuinely different failure mechanism from the
control-arm baseline** (position 1: host-side comms timeout, no firmware diagnosis, 15.813 s) —
recorded as different, not softened, with chip/contact wear named honestly as an undismissed
alternative to a genuine v1.33 firmware-behavior difference; neither is asserted as proven from
one data point.

**Read set:** three-run `dev consistency-check` **FAILED** — 3 distinct SHAs, no two reads agreed
(first divergence at offset `0x001A`, 23/65536 bytes divergent run1-vs-run2). `judge_wrv.py`:
`sha_verdict_judged=disagreement`, `n3_disagreement=true`, `app_verdict_unjudged=1` agreeing.

**N=3 escalation scheduled, not yet run:** because `distinct_read_shas > 1`, a retroactive
three-run read on the control arm's matching position (`A2__control__w27c512`) is scheduled for
`P-11`/Task 15, per 161-03-PLAN's shared-conventions escalation rule. `EVIDENCE.jsonl` row
appended, `outcome=skipped-with-reason`. `render_evidence.py --check`: green.

## P-08 (second arm) — Swap to W29C020 (2026-08-27, operator)

Operator, verbatim: "W29C020 seated". W27C512 removed, W29C020 (DIP32) seated on the uno328pb at
`/dev/ttyUSB0`. **D-07 safety judgement: operator inspected and proceeded, raising no concern —
an affirmative clearance given at this gate.** The operator was also asked directly about the
W27C512's physical condition after its five insertions (including the rule-8 re-seat) and did not
report on it — **recorded as NOT assessed**, not as "found sound." This matters directly for
plan 161-05 (cell A3/B2), which reuses this same physical part.

**Pot not touched** — Task 4's single confirming read (11.9 V) stands for the whole cell; no
second `vpp` invocation for this swap.

**VPP note carried into position 4, stated explicitly rather than left implicit:** position 3's
re-run failed with the firmware's own diagnosis naming "insufficient program voltage or a worn or
failing cell" as the likely cause — nominating low VPP as a candidate. The pot is **not**
adjusted for position 4 regardless: `P-06` sets VPP once per cell (comparability across all four
positions would break if changed mid-cell, and adjusting now would be chasing a success rather
than measuring one). Task 4's "in band" ruling (11.9 V inside the firmware guard window
`[11.4, 12.5]` V) is **not** the same claim as "VPP is optimal" — the guard not firing only means
the firmware's own init check did not trip; it says nothing about whether 11.9 V is sufficient
for reliable programming margin. This distinction is recorded explicitly so the earlier in-band
ruling is never read as a clearance that VPP is fine.

## P-09 (v1.33 x W29C020) — position 4 of 4: closing the A/B square (2026-08-27)

Full detail in `WRITE.md` ("Position 8 (4 of 4)"). Summary: a **fourth, distinct** failure
mechanism — a bare **connect-level** timeout ("No compatible programmer answered") before even
the INIT/chip-ID handshake was reached, wall-clock **14.288 s** (391.748 s ceiling never
approached). A `hw` probe immediately after succeeded cleanly, confirming the board was not
wedged. **No re-run performed** — Standing bench rule 8's allowance was already spent on position
3, and no other rule licenses retrying a transient connect failure.

Follow-up read failed on its first of three attempts (communication timeout, 4096/262144 B),
producing a partial file. That partial read is **99.1% (4061/4096 B) identical** to a
freshly-generated copy of `A1__v133__w29c020`'s own image (mask `0x13`) — materially stronger
than position 2's ~65% correlation, further reinforcing (not proving) that this physical chip
still carries substantial residual content from cell A1. `judge_wrv.py`:
`sha_verdict_judged=incomplete-read-set`, `size_violations` non-empty, `app_verdict_unjudged=2`
agreeing. `EVIDENCE.jsonl` row appended, `outcome=skipped-with-reason`. `render_evidence.py
--check`: green.

**All four A2 positions now recorded. No two failed by the identical mechanism** (host comms
timeout / firmware verify timeout / chip-ID mismatch + firmware pulse-convergence / bare connect
failure). Every position stopped the chip-program path — consistent with Backlog 999.2's overall
prediction — but with materially more precision than the backlog itself carries. **No completion
occurred on either arm anywhere in this cell** — 999.2 is not contradicted by an unexpected
success.

## Standing Phase 165 hypothesis, named and left open (not resolved here)

**Low VPP as a candidate contributing cause for A2's convergence failures** — named explicitly by
position 3's own firmware diagnosis ("insufficient program voltage or a worn or failing cell, not
a timing problem"). This cell's single confirming read measured **11.9 V**, in band against the
firmware guard window `[11.4, 12.5]` V (Task 4/`POT.md`) but not string-equal to the 12.0 V
target. **The comparison and its confound, stated plainly:** cell A1 measured 12.0 V and passed
all four of its positions; this cell measures 11.9 V and has failed three of four by
program/verify mechanisms (the fourth, position 4, failed at connect level before VPP could even
be relevant). But it is the **same physical pot on the same shield**, moved from the Uno to the
uno328pb between cells — the 0.1 V delta may reflect per-board ADC/EEPROM calibration rather than
a real difference in the rail actually delivered under load. **This confound is not resolved
here — it cannot be, from this cell's own data.**

**This hypothesis sits inside the milestone's own acknowledged blind spot:** program-window
VPP/VCC **under load** is unmeasured on this rig (the Phase-97 DTR-reset-on-close tooling gap),
which is exactly why v1.34 makes no electrical claim anywhere in its record. This is named as a
**standing, unconfirmed Phase 165 hypothesis**, not a finding — framed inside that disclosed
blind spot, not as a claim this cell's own tooling could actually measure.

## P-11 — Teardown (in progress, 2026-08-27)

**v1.33 read-back set preserved** into `readback_v133/` (all six cell-root artifacts), mirroring
`readback_control/` — both arms' firmware evidence now survive side by side, distinguishable
(control span 26074 vs v133 span 23000, confirmed distinct).

**Teardown signature probe** (`board_probe_teardown.json`, a distinct path from `P-02`'s
`board_probe.json`): `connected_part=atmega328pb`, `board_signature=0x1e9516` — **unchanged**
from `P-02`. Board identity stable across the whole cell.

**Config-dir check, two assertions in order:**

1. **`~/.firestarter` — CHANGED — P-H1, a SECOND recurrence.** Measured: `config.json` mtime
   advanced from the Amendment 3 pinned baseline's `1787817565` (2026-08-27T07:59:25Z) to
   `1787849229.89...` (2026-08-27T22:47:09Z-equivalent epoch, i.e. later in this same session);
   content is now `{"port": "/dev/ttyUSB0"}` (sha256
   `e76bb5291979292eef9119cfc449c034dbcbcaef1b8c66357fa698c86244b261`), differing from the pinned
   baseline. File count remains exactly one (`config.json`) — a content change, not a new/removed
   file. **No deletion was attempted.** This is the **same class of finding** cell A1 recorded
   (mirrors `bench/cells/A1/CELL.md`'s identical P-H1, itself a recurrence of the still-unresolved
   Phase 160 Plan 12 finding) — a **second recurrence within this same milestone**, strengthening
   the case that this is a systemic `firestarter_app` behavior rather than session noise. Every
   direct CLI invocation in this cell carried an explicit `-p`/`--port` and an inline
   `FIRESTARTER_CONFIG_DIR=` prefix; no in-scope bench-tool source explains a non-transient
   `remember_port()`-style write to the default config dir. Not root-caused further here — D-16
   boundary, product code, handed to Phase 165.
2. **Frozen `FIRESTARTER_CONFIG_DIR` content SHA — unchanged, confirmed.**
   `check_arms.py --expect-config-sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`
   -> matched (`check_arms_teardown.json`). All four A2 provenance records carry a non-null,
   matching `config_dir_sha` (`77adfdd2...`).

**Completeness assertion:** all four `position_id`s present in `bench/EVIDENCE.jsonl`, each
exactly once, `cell_id == "A2"`, `outcome` in `{validated, skipped-with-reason}` (all four
`skipped-with-reason`), each with a non-null `write_duration_wallclock_s`.

## N=3 escalation — SCHEDULED, blocked on a physical chip-seat

Position 3 (`A2__v133__w27c512`) recorded `distinct_read_shas == 3` — a genuine N=3
disagreement, per the escalation rule (161-03-PLAN's shared conventions). The retroactive
control-arm escalation requires **re-flashing the control arm and re-writing
`A2__control__w27c512`'s own image**, then taking a three-run read — both a write and a read
require a chip **seated**, and this Uno-class board's socket was emptied at Task 14 specifically
for the (now-completed) teardown signature probe. **No chip is currently seated.**

**Cost of running this escalation, stated before doing it (per 161-03-PLAN's own instruction):**
one firmware checkout+flash (control), one full write attempt (expected, based on this cell's own
record, to fail somewhere in the program path — consistent with every other control-arm result in
this cell), one three-run read regardless of write outcome, one judge, then a firmware
checkout+flash back to v1.33 to restore the required cell-end arm state. This is a real physical
operation, not a formality — it is, per the orchestrator's own framing, the only measurement that
separates "v1.33 reads unstably on this board" from "this board reads unstably on both arms," and
that distinction is left **genuinely undetermined** until it runs.

**Escalation method correction, recorded before running:** the retroactive control-arm escalation
runs **read-only** — no re-write. The escalation question is read stability, not write success;
three reads of the content currently on the chip (the residue of position 3's failed v1.33 write)
under the control arm is a direct, controlled comparison — same silicon, same content, only the
arm differs. Re-writing would replace that content and destroy the comparability the escalation
exists to obtain, and position 1 already showed a control-arm write on this board most likely
fails anyway (adding a third partial state as a confound, not removing one). W27C512 seated for
this escalation is this physical part's **sixth** insertion across A1 and A2; its physical
condition was again not assessed and is recorded as such, never as sound.

**Escalation step 1 — chip-out confirmation, recorded precisely:** the operator's first reply to
this gate was the literal text "Remove W27C512" — ambiguous between restating the instruction and
confirming it done. The orchestrator declined to interpret it and asked for an explicit
confirmation rather than risk an avrdude flash with silicon seated; the operator then confirmed
"yes, empty socket". **Recorded as a real limitation of this gate:** the chip-out precondition
for any avrdude flash rests on operator word alone — there is no non-avrdude way to detect a
seated chip, and the probe that would detect one is itself the operation the chip-out rule
forbids. Carried into `SUMMARY.md`.

**Escalation step 2 — control arm re-flashed** (`pio run -t upload -e uno328pb --upload-port
/dev/ttyUSB0`, log `41_pio_upload_control_escalation`): rc=0, `26074/32768 B`. Independent
read-back judge (log `42_judge_readback_escalation`, out-dir
`ESCALATION_A2__control__w27c512/`, distinct from the cell-root and both `readback_*/` sets, none
overwritten): `judged_match=true`, `judged_span_bytes=26074`, both vector exclusions applied,
`sha_actual_judged=43dcb663...` — **byte-identical** to position 1's original control flash
(`flash_readback.bin` MD5-matches `readback_control/flash_readback.bin` exactly). Confirms the
control arm is genuinely re-flashed and correct before the escalation's read-only measurement.

## Escalation step 4 — BLOCKED: VPP guard now fires HIGH, unexpectedly

**All three attempted reads under the control arm failed identically at INIT**, before any bytes
were read (0-byte `run_01.bin`/`run_02.bin`/`run_03.bin`, logs `43-45_escalation_read_{1,2,3}`):
```
ERROR: VPP is high: 12.5V > 12.0V
Programmer error during READ: Programmer error during init: VPP is high: 12.5V > 12.0V
```
All three attempts (~3.7 s each) failed with the **identical** message.

**A single confirming `vpp` read taken afterward** (log `46_vpp_escalation_check`, one read per
Standing bench rule 4): **`VPP: 12.5V, Internal VCC: 5.3V`**, stable across five consecutive
frames in the brief capture (unlike Task 4's original 11.8-11.9V jitter, this reading held
steady at exactly 12.5V).

**This is a genuine, unexpected finding, recorded plainly rather than smoothed over:** the pot
has not been touched by anyone since Task 4's single confirming read of **11.9 V** — every
intervening checkpoint recorded "pot not touched" and no `vpp`-adjusting action was ever
requested or performed. Yet the measured VPP has now shifted from 11.9 V (in band, LOW side) to
12.5 V (at or just past the HIGH edge of the firmware guard window `[11.4, 12.5]` V — the guard
condition is `vpp_mv > target_mv + 500`, strictly greater than 12500 mV, and it fired on all
three attempts, so the true raw value is just above 12500 mV even though it displays as "12.5V"
at one-decimal precision).

**No forbidden flag used, guard never bypassed.** Per Phase 145 D-17 and this plan's own
prohibitions, the guard is never pushed past with `--force`. This blocks the escalation's
read-only measurement entirely until VPP is brought back in band — this is the same "guard
fires, pot is adjusted until in band, the step restarts clean" provision `P-06` itself names for
the historical `VPP is high` scenario, applied here mid-escalation rather than at the original
`P-06`.

**Not chased as a contact-fault question (rule 5 does not apply here)** — rule 5's `0x303`/blank
signature is a distinct symptom class from a real, in-range-looking, stable 12.5 V reading; this
is treated as a genuine (if unexplained) VPP measurement, not a contact artifact.

## HEADLINE FINDING — this board's VPP ADC reads ~0.8 V high (operator multimeter measurement)

**The paired measurement:** operator, verbatim: "about the vpp the reading is alittele bit off i
mesured with a multimeter and its 11.7" — taken with the firmware simultaneously reporting
**12.5 V** at that same moment (Escalation step 4's confirming read, `46_vpp_escalation_check`).
Multimeter readings are operator-only per Standing bench rule 3; this is an **operator
measurement**, not a Claude-derived one. **The on-board VPP ADC on this uno328pb reads
approximately 0.8 V high** (12.5 V firmware-reported vs 11.7 V multimeter-measured). The rail
itself did not run away — the instrument reading it is inaccurate.

**Why no pot adjustment was possible or attempted, stated as the cleanest form of the finding:**
on this specific board, the firmware guard and a correct rail cannot be satisfied simultaneously.
- Adjust until the **firmware** reads 12.0 V -> the real rail falls to **~11.2 V**, below the
  firmware's own 11.4 V LOW threshold in real terms, and genuinely too low for reliable
  programming margin.
- Adjust until the **meter** reads 12.0 V -> the firmware would read **~12.8 V**, and the HIGH
  guard fires harder.
- **There is no pot position that satisfies both.** The gate is unsatisfiable on this board as
  currently calibrated. No `--force` was used and none was requested or considered.

**Ruling: this is NOT a P-H1 rig halt.** P-H1 covers a broken *oracle* — this milestone's judged
oracle is the read-back SHA judge (`judge_wrv.py`/`judge_readback.py`), which does not consult
VPP calibration at all and is unaffected. The uno328pb is the **specimen** in this cell, and its
apparent miscalibration is a finding *about the specimen*, not a broken measuring instrument for
this cell's own record. Per this plan, findings are recorded, never fixed here — RCA belongs to
Phase 165. The board's EEPROM calibration was **not** touched, `firestarter config` was **not**
run, the pot was **not** adjusted.

### Escalation recorded as UNRUN — named reason

The N=3 escalation (retroactive control-arm read of `A2__control__w27c512`'s residual content) is
recorded as **unrun**, not completed and not fabricated. Named reason: blocked by the VPP ADC
miscalibration discovered at escalation step 4 — three read attempts all failed identically at
device init with `VPP is high: 12.5V > 12.0V` before any bytes were read, and the gate is
unsatisfiable on this board as calibrated (see above). **Even had it run, it would have run under
the same faulty gate**, so its answer would have carried the same doubt as everything else this
cell measured under an ADC now known to read high.

**Consequence, stated plainly, not resolved by omission:** the question position 3's three
distinct read SHAs raised — whether that instability is v1.33-specific or a board-wide property
present on both arms — **remains UNDETERMINED.** What would resolve it: a three-read set taken on
a board whose VPP ADC is confirmed calibrated (a fresh meter-cross-checked reading before the
run), or a re-run of this same measurement on this board after its VPP calibration is corrected.
Neither is available within this plan's scope.

### Retroactive impact on this cell — an inference, not a measured historical fact

Task 4's single confirming read at `P-06` reported **11.9 V**. **If** the ~0.8 V ADC offset held
constant across the cell (it was only directly cross-checked once, at escalation step 4, hours
later), the **real** rail during all four write positions may have been approximately **11.1 V**
— *below* the firmware's own 11.4 V LOW-guard floor in real terms. **This is stated as an
inference from a single paired measurement with an assumed-constant offset, not as a measured
historical fact.** It is a strong, testable lead for Phase 165, not a conclusion this cell's own
record can support on its own.

### Reframing the four distinct failure mechanisms — a hypothesis, not a finding

Positions 1-4 each failed by a mechanism this cell's record treated as independent (host
comms timeout / firmware verify timeout / chip-ID mismatch then pulse-convergence / bare connect
failure). **In light of the VPP measurement above, these four may plausibly share one root cause**
— an under-volted programming rail failing at different points in the protocol depending on
timing and which operation was attempted — **rather than four independent faults.** This is
offered explicitly as a **hypothesis for Phase 165**, not asserted as this cell's finding; nothing
in this cell's own tooling can distinguish "one shared cause, four symptoms" from "four
coincidentally different faults."

### The low-VPP hypothesis, promoted

The hypothesis named at Task 12 (position 3's own firmware diagnosis: "insufficient program
voltage or a worn or failing cell, not a timing problem") is **promoted from a long shot to the
leading candidate explanation** by this measurement. The firmware's own diagnostic text
independently pointed here before any multimeter was involved — this measurement is corroborating
evidence for a hypothesis the firmware itself already raised, not a fresh, unrelated finding.

### Backlog 999.2 implication — a lead, not a resolution

Backlog 999.2 has stood as an unexplained "uno328pb cannot finish a program" board fault. This
measurement raises the possibility that the true cause is a **miscalibrated VPP ADC on this
specific board**, rather than a firmware or silicon defect — a materially different, and more
fixable, explanation than "this board's silicon cannot program." **Recorded as a Phase 165 lead
with its evidential limits stated explicitly** (one paired measurement, an inferred — not
measured — historical offset): this cell's record does **not** assert VPP miscalibration as the
cause of 999.2.

### A limit exposed in P-06 itself

`P-06`'s procedure takes **exactly one confirming read per cell** and treats it as standing for
the whole cell's duration. **That design is only sound if the reading is accurate and stable** —
this cell shows a case where the firmware-reported reading was neither, and the discrepancy was
only caught by chance, because the escalation's guard-fire forced a fresh reading late in the
cell. Recorded as a **procedure limitation** for Phase 166's honesty ledger, directly connected to
this milestone's own declared headline non-claim: program-window VPP/VCC **under load** is
unmeasured on this rig (the Phase-97 DTR-reset-on-close tooling gap) — this finding gives that
disclosed non-claim concrete teeth rather than leaving it a formality nobody ever actually hit.

### Non-claim about cell A1

**A1's Uno was never meter-checked.** Whether *its* VPP ADC is accurate is genuinely **unknown**
— this cell's finding must not be read as implying A1 ran at a true 12.0 V, and equally must not
be read as implying it did not. A1's four positions passed their judged SHA oracles regardless,
and that judgment is unaffected by VPP calibration either way (the oracle never consults VPP).

## Escalation step 6 — flash back to v1.33, proven (2026-08-27)

**Firmware checkout:** `git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`
— pre-checkout HEAD `8695ee52...` (control, from the escalation's re-flash); post-checkout HEAD
`5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`, equal to `arms.v133.fw_sha`; porcelain empty both
before and after.

**Flash** (`pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0`, log
`47_pio_upload_v133_final`): rc=0, `23000/32768 B` — matches the v133 arm's expected span exactly.

**Independent read-back judge** (`judge_readback.py`, out-dir `FINAL_READBACK_v133/`, a distinct
path from `readback_control/`, `readback_v133/` and `ESCALATION_A2__control__w27c512/` — none
overwritten, log `48_judge_readback_v133_final`): `judged_match=true`, `judged_span_bytes=23000`,
`sha_actual_judged=bbf7aa68...` — **byte-identical** to Task 9's original v1.33 flash on this
board and to plan 161-02's D-10 pre-proof. Both vector exclusions applied; raw-span SHAs recorded
and never compared, as this target requires.

**Gitlink verified:** `git -C /workspaces/firestarter rev-parse HEAD` = `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`,
porcelain empty. `git -C /workspaces diff --stat -- firestarter` — **empty**. The cell ends on the
v1.33 arm exactly as required, with no gitlink diff to commit (meta's own committed pointer was
already at this SHA before this plan started).

**Both sub-repos confirmed byte-unchanged:** `git -C /workspaces/firestarter status --porcelain`
and `git -C /workspaces/firestarter_app status --porcelain` both empty.

**Completeness assertion:** all four A2 `position_id`s present in `bench/EVIDENCE.jsonl`, each
exactly once, `outcome=skipped-with-reason` for all four, each with a non-null
`write_duration_wallclock_s`.

**Per-cell gate (D-04):** `bash run_gates.sh` — **exit 0** (captured directly via `$?`, never
through a pipe), **12/12 tool selftests, ALL GATES PASSED (5/5 live gates)**. `gate_record.py
--jsonl`: **0 violations**.

**Force-added positions:** **all four.** Every A2 position judged something other than a clean
`match` (`mismatch` x2, `disagreement` x1, `incomplete-read-set` x1) — the commit-on-failure
exception applies to all four, and their `reads/<position_id>/` contents are force-added so
Phase 165's RCA has the actual bytes.

### BOARD-04 non-claims, carried and not re-derived

1. v1.31's **0.37 s** figure is a **spread** (max minus min across three app-reported,
   success-only figures on **Leonardo + Rev 2.0**), not a duration — A2 is a **uno328pb**, so no
   comparison against it is drawn here at all; that comparison is valid only on cell A3/B2.
2. This cell's own write-duration figures (4.019-15.813 s, all failures) are not compared against
   any v1.31 figure as if they were completions of the same kind of measurement.

### P-11 leave-state (cell-agnostic declaration, this cell's concrete values)

| Field | Value |
|---|---|
| Board | uno328pb (ATmega328PB, signature `0x1e9516`) |
| Port | `/dev/ttyUSB0` (CH340, `1a86:7523`) — **only one live node this whole cell** |
| Arm on the board | **v1.33** (fw `5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463`) |
| Chip seated | **None** — socket confirmed empty at Task 14's chip-out, again at escalation step 1, and again at escalation step 5 (this final teardown state) |
| Pot | **NOT adjusted.** Left exactly where the operator had it: the firmware-reported reading there is **~12.5 V**; a multimeter simultaneously reads **11.7 V**. This ~0.8 V ADC discrepancy is the cell's headline finding — the next session must NOT "correct" the pot against the firmware's own (miscalibrated) reading without first re-confirming with a meter, or it risks pushing the real rail further out of range in the wrong direction. |
| Shield | **Rev 2.0** (operator-declared, silkscreen-authoritative) |

This is A2's own accurate leave-state, whatever it is — **nothing here is staged toward plan
161-05** (cell A3/B2), which needs a **Leonardo**, not this board, and no attempt was made to
arrange anything for it. The one item 161-05 explicitly inherits by name is the **shared physical
W27C512**: eight handlings within this cell alone (on top of its two uses in cell A1), its
physical condition **never assessed** at any point — 161-05 must treat that as **uncertainty**,
never as a clearance that the part is sound.
