# BRINGUP-leonardo-provenance — A3/B2 `P-02` Pre-Proof

**Cell type:** bring-up pre-proof, not a sweep cell. Holds no `WRV-VERDICT.json` and adds no row
to `EVIDENCE.jsonl` (see rationale below).

## Purpose

`capture_provenance.py` had run live on exactly one board before this plan (the Uno). It shells
out internally to `probe_board.py` with **no 1200-baud touch**, and a Leonardo running
application firmware was measured (BRINGUP-leonardo, Phase 160 Plan 10) to reject the `avr109`
handshake outright. A3/B2's `P-02` (plan 161-05, the milestone's most expensive cell) would have
hard-refused on its first live attempt. This pre-proof establishes and measures the working
sequence before that cell runs.

## Operator checkpoint — declaration and a genuine deviation from the checkpoint script

**Operator declaration, verbatim:** "Leonardo, rev 2.2, socket empty."

- **Board:** Leonardo, on `/dev/ttyACM0`.
- **Shield silkscreen:** operator wrote "rev 2.2". **Canonical form for `--shield-rev` is
  `Rev 2.2`** (`capture_provenance.py` restricts the argument to exactly `Rev 2.0` / `Rev 2.2` /
  `Modified Rev 0` and rejects anything else) — the case-only normalization from "rev 2.2" to
  "Rev 2.2" is this record's own transcription for the tool's closed choice set, **not** a
  correction of what the operator said; the operator's raw wording is preserved above, verbatim,
  as the primary record.
- **Socket:** **EMPTY, no chip — operator-confirmed in words** ("socket empty"), not derived.

**Deviation from the checkpoint script, recorded rather than papered over:** Task 3's checkpoint
text asked the operator to disconnect the uno328pb first, then take the Leonardo. That did not
happen. Node mtimes confirm neither board was re-enumerated at the swap: `/dev/ttyACM0`
unchanged since `12:41` (pre-existing Leonardo attachment) and `/dev/ttyUSB0` unchanged since
`12:48` (the uno328pb, still attached from Task 2). The operator fitted the Rev 2.2 shield to the
already-attached Leonardo in place, leaving the uno328pb on the bus for the whole of this task.
This is **not a blocker**, but it means two live serial nodes were present throughout Task 4:
every avrdude/probe/`capture_provenance.py`/arm-binary invocation below passes an **explicit**
`--port /dev/ttyACM0` (or `-p`/`-P`); none relies on autodetection. Where a tool enumerates
devices before/after (`touch_1200.py`), `/dev/ttyUSB0` correctly appears in both the before and
after lists throughout — that is the uno328pb sitting still, not a Leonardo re-enumeration, and
is read that way below, not misread as a touch failing to change anything.

## Shield framing — carrier only, and what does/does not transfer to A3/B2

Rev 2.2 is a **carrier for this pre-proof only**. Its A3 ADC reading (via the `hw` call below,
`Rev 2.0-class, Override HW: Rev 2.0-class`/`Rev 2.3` across different attempts — itself
consistent with standing bench rule 6, that the A3 ADC band cannot discriminate the three
shields) is **not** a Rev 2.0 datum and **not** a SHIELD-04 result — Phase 163 owns that.
**A3/B2 will run with Rev 2.0 fitted, not Rev 2.2.** The shield-dependent half of this pre-proof
therefore transfers to A3/B2 only as "the tool completed with SOME valid `--shield-rev` value,"
never as a Rev 2.0 rehearsal — the specific ADC numbers recorded here are not predictive of what
A3/B2 will read.

## Port identity

Post-swap enumeration (orchestrator-measured, 2026-08-27T12:54:01Z): `/dev/ttyACM0` (vid:pid
2341:8036, "Arduino Leonardo") — Rev 2.2 fitted; `/dev/ttyUSB0` (vid:pid 1a86:7523, CH340 "USB
Serial") — the uno328pb, still attached; `/dev/ttyACM1` absent — the chipped Uno, still off the
bus. `$PORT` for this cell: `/dev/ttyACM0`.

## Commands run (literal, absolute argv), in the order actually attempted

### Attempt 1 — the literal A3/B2 `P-02` sequence, run exactly as written, observing what happens

**1. `probe_board.py` direct, no touch (predicted to fail):**
```
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/probe_board.py --target leonardo --port /dev/ttyACM0 \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --out /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-leonardo-provenance/board_probe.json
```
**rc=1, elapsed=6.086s.** `FAIL: neither parse route matched avrdude stderr: 'Error:
initialization failed  (rc = -1) ...'` — matches the prediction exactly: the application
firmware does not speak `avr109`. Logged: `logs/00_probe_board_pretouch.std{out,err}.log`.

**2. `hw` call, v1.33 arm, against the application firmware directly (no touch needed — this is
the app's own normal serial protocol, not the bootloader):**
```
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -v -p /dev/ttyACM0 hw
```
**rc=0, elapsed=3.945s.** Succeeded cleanly — `hw` talks to the running application, not the
bootloader, so no touch is required for this call in isolation. Reported hardware revision:
`Rev 2.0-class, Override HW: Rev 2.3` (a firmware-reported, non-authoritative datum — standing
bench rule 6). Logged: `logs/01_hw_call.std{out,err}.log`.

**3. `capture_provenance.py` itself, as literally specified in the plan (no seam flags,
`--pending-readback` only):**
```
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config python3 \
  /workspaces/.planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id BRINGUP-leonardo-provenance --position-id BRINGUP-leonardo-provenance \
  --arm v133 --target leonardo --port /dev/ttyACM0 --chip w27c512 --shield-rev "Rev 2.2" \
  --pending-readback \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .../provenance_BRINGUP-leonardo-provenance.json
```
**rc=1, elapsed=6.183s.** `FAIL: board-signature probe: probe_board.py exited 1: FAIL: neither
parse route matched avrdude stderr: 'Error: initialization failed ...'` — the tool's own
**internal** `probe_board.py` subprocess call fails identically to step 1, for the identical
reason: no touch precedes it. Confirms the prediction. Logged:
`logs/02_capture_provenance_attempt1.std{out,err}.log`.

### Establishing the working sequence

**4. `touch_1200.py` bare mode, then `probe_board.py` inside the window:**
```
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../touch.json
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/probe_board.py --target leonardo --port /dev/ttyACM0 \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json --out .../board_probe.json
```
Touch: **rc=0, 2.262s.** `touch.json` recorded `"changed": false`,
`devices_before == devices_after == ["/dev/ttyACM0", "/dev/ttyUSB0"]`, `wait_new_port: false` —
the argv carries **no `--wait-new-port` token** anywhere. The Leonardo node does not change; the
`ttyUSB0` entry present in both lists is the still-attached uno328pb, not a re-enumeration.
Probe: **rc=0, 1.399s**, `board_signature=0x1e9587`, `connected_part=atmega32u4`,
`mcu_matches=true` — matches the known-good Leonardo signature and the operator's declaration.
**Total elapsed from touch onset to a completed, parsed identity result: 3.661s** — consistent
with the historical BRINGUP-leonardo figure (3.487s, a different session, same board, same
method). Logged: `logs/03_touch.std{out,err}.log`, `logs/04_probe_board_posttouch.std{out,err}.log`.

**5. A genuinely new finding: a second live-port call immediately after the first, inside the
same touch window, races avrdude's own `avr109` session teardown.** Touching again and
immediately invoking `capture_provenance.py` (still with no seam — testing whether the tool
"just works" once the caller has warmed the window):
```
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../touch_attempt2.json
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config python3 \
  /workspaces/.planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id BRINGUP-leonardo-provenance --position-id BRINGUP-leonardo-provenance \
  --arm v133 --target leonardo --port /dev/ttyACM0 --chip w27c512 --shield-rev "Rev 2.2" \
  --pending-readback \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .../provenance_BRINGUP-leonardo-provenance_attempt2.json
```
Touch: rc=0, 2.257s. `capture_provenance.py`: **rc=1, elapsed=2.387s, total from touch
onset=4.644s.** `FAIL: controller-string probe: controller: string not found in \`hw\` output
(exit 1): '... ERROR :SerialComm : 203: Failed to open serial port /dev/ttyACM0: [Errno 2] could
not open port /dev/ttyACM0: [Errno 2] No such ...'`. `/dev/ttyACM0`'s node mtime was observed to
have advanced (re-created) immediately after this failure, confirming the port genuinely,
transiently vanished. **This is not a timeout** (4.644s is well inside the ~8s Caterina
inactivity window) — it is a **race**: `capture_provenance.py`'s internal `probe_board_signature()`
call (an `avr109` session) ends with avrdude's own "leave prog mode"/"exit bootloader" exchange,
which immediately resets the ATmega32U4 out of Caterina and back into the application — causing a
brief USB re-enumeration. The tool's very next internal call, `probe_controller_string()` (the
`hw` command, a completely different serial protocol at 250000 baud), can land while that
re-enumeration is still in flight. Logged: `logs/05_touch_attempt2.std{out,err}.log`,
`logs/06_capture_provenance_attempt2.std{out,err}.log`.

**6. Isolating and measuring the fix — a settle gap between the two internal probes:**
```
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../touch_attempt3.json
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/probe_board.py --target leonardo --port /dev/ttyACM0 \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json --out .../board_probe_attempt3.json
sleep 2
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -v -p /dev/ttyACM0 hw
```
Touch: rc=0, 2.269s. Probe: rc=0, 1.268s (total from touch: 3.536s). **2.009s settle gap.** `hw`
call after the settle: **rc=0, elapsed=3.678s, total from touch onset=9.223s.** Succeeded. This
confirms the fix precisely: the ~8s Caterina figure governs only the **bootloader** window (touch
onset → the avr109 probe completing, comfortably inside it at ~3.5s); once that probe's own
session exit has reset the MCU back into the **application**, the relevant constraint changes
entirely — no bootloader timeout applies any more, only the application's own USB
re-enumeration needs to settle (~2s), after which the app is available with no further time
pressure (this `hw` call landed at 9.223s total, past the nominal "roughly 8s" figure, and
still succeeded — because that figure describes the bootloader's inactivity timer, which was
long past being relevant by the time the app-mode `hw` call ran). Logged:
`logs/07_touch_attempt3.std{out,err}.log`, `logs/08_probe_attempt3.std{out,err}.log`,
`logs/09_hw_attempt3.std{out,err}.log`.

### A second, independent, non-hardware blocker — found live, unrelated to timing

Before designing the seam, `resolve_image_plan_fields()` was checked directly against the real
`bench/IMAGE-PLAN.json`:
```python
resolve_image_plan_fields('BRINGUP-leonardo-provenance', '.../bench/IMAGE-PLAN.json')
# -> (False, None, None, None, "no image plan row found for position_id
#     'BRINGUP-leonardo-provenance' in '.../bench/IMAGE-PLAN.json'")
```
`bench/IMAGE-PLAN.json` has exactly 21 rows — the 20 real sweep positions plus
`BRINGUP-wrv__v133__w27c512` (the one prior bring-up cell that DOES generate a chip image).
Neither of this plan's two pre-proof cells generates a chip image (no chip is seated, no write
ever runs), so neither has, or ever will have, a row — this is a **permanent** condition, unlike
`--pending-readback`'s temporary "not yet, will be patched later" semantics. `capture_provenance.py`
resolves this lookup **unconditionally**, regardless of `--pending-readback` or any hardware
timing — so `BRINGUP-leonardo-provenance`'s `capture_provenance.py` invocation would have failed
here even with a perfectly-timed board/controller probe pair. Recorded as a second, independent,
genuine blocker, found live rather than assumed from the plan text (which anticipated only the
timing-related seam).

## Decision: `capture_provenance.py` needed two minimal, additive seams

**Evidence for the decision:** attempts 1, 2 and 3 above show `capture_provenance.py` **cannot**
simply consume the two already-obtained results by re-running its own internal probes back to
back — the internal `probe_board_signature()` → `probe_controller_string()` sequence, run without
a caller-controlled settle gap, races the avr109 exit reset (measured: fails at ~4.6s, port
ENOENT). And the tool's unconditional image-plan lookup would fail this position regardless of
timing (measured directly above). Both are genuine, load-bearing blockers for A3/B2's `P-02`,
not hypothetical.

**Seam 1 — `--board-probe-json PATH`:** skip the tool's internal `probe_board.py` subprocess call
entirely; read `board_signature` directly from an ALREADY-OBTAINED `probe_board.py --out` JSON.
This lets the caller run `touch_1200.py` + `probe_board.py` externally, insert the measured ~2s
settle for the post-avr109-exit re-enumeration, and only then invoke `capture_provenance.py` —
whose first live-port action is then the `hw` call, landing safely past the settle. Implemented
as `resolve_board_signature_from_json()`, called from `main()`'s existing board-signature branch;
the `else` branch (no flag given) is **byte-identical** to the pre-existing code — the Uno/uno328pb
path is unchanged.

**Seam 2 — `--no-image-plan`:** skip `resolve_image_plan_fields()` entirely for a position that
has no `bench/IMAGE-PLAN.json` row and never will; write `image_mask`/`image_stamp_width`/
`image_sha` as an explicit `"not measured — <reason>"` placeholder (per PROCEDURE.md's Recording
discipline), naming the position id and the reason on the same line. Implemented as
`build_no_image_plan_reason()`; the default (`--no-image-plan` omitted) path is unchanged — every
real sweep/chip-write position keeps the hard refusal on a missing row.

**Git diff scope, confirmed additive-only:** `git diff .planning/milestones/v1.34-artifacts/tools/capture_provenance.py`
shows two new `argparse` flags, two new small functions (`resolve_board_signature_from_json`,
`build_no_image_plan_reason`), the two call sites replaced with an `if <flag>: <new helper> else:
<original code unchanged>` branch, and new `--selftest` legs. No existing line was altered inside
either `else` branch.

### The final working sequence — A3/B2's `P-02` prescription, verbatim, copy-runnable

```bash
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port $PORT --settle-s 2.0 \
  --out $CELL_DIR/touch.json
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target leonardo --port $PORT \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/board_probe.json
sleep 2   # settle for the post-avr109-exit USB re-enumeration -- measured necessary, not optional
FIRESTARTER_CONFIG_DIR=$FIRESTARTER_CONFIG_DIR python3 .planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id A3/B2 --position-id $POSITION_ID \
  --arm {control|v133} --target leonardo --port $PORT --chip $CHIP --shield-rev "Rev 2.0" \
  --board-probe-json $CELL_DIR/board_probe.json \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out $CELL_DIR/provenance_$POSITION_ID.json
```
(`--no-image-plan` is **not** part of A3/B2's real prescription — every real sweep position DOES
have a row in `bench/IMAGE-PLAN.json`; that flag exists only for this milestone's two bring-up
pre-proof cells, which never generate a chip image. `--pending-readback` is likewise a
bring-up-only concern here — A3/B2's own `P-02` runs before its own cell's flash too, per RIG-02's
ordering, so A3/B2's `P-02` **does** carry `--pending-readback`, exactly as shown above; it is
completed later by `--patch-readback` once `judge_readback.py` (`P-04`) has run, per the standing
procedure.)

### Final, successful invocation for THIS cell (both seams applied)

```
python3 .planning/milestones/v1.34-artifacts/tools/touch_1200.py --port /dev/ttyACM0 --settle-s 2.0 \
  --out .../touch.json
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target leonardo --port /dev/ttyACM0 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out .../board_probe.json
sleep 2
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config python3 \
  /workspaces/.planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id BRINGUP-leonardo-provenance --position-id BRINGUP-leonardo-provenance \
  --arm v133 --target leonardo --port /dev/ttyACM0 --chip w27c512 --shield-rev "Rev 2.2" \
  --pending-readback --board-probe-json .../board_probe.json --no-image-plan \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .../provenance_BRINGUP-leonardo-provenance.json
```
Touch: rc=0, 2.294s. Probe: rc=0, 1.525s (total from touch: 3.819s). Settle: 2.009s.
`capture_provenance.py`: **rc=0, elapsed=4.277s, total from touch onset=10.105s.** `OK: provenance
captured for cell 'BRINGUP-leonardo-provenance' -> provenance_BRINGUP-leonardo-provenance.json`.
Logged: `logs/10_touch_final.std{out,err}.log`, `logs/11_probe_final.std{out,err}.log`,
`logs/12_capture_provenance_final.std{out,err}.log`.

**Resulting record** (`provenance_BRINGUP-leonardo-provenance.json`): `captured_at_step=2`,
`target_env=leonardo`, `arm=v133`, `board_signature=0x1e9587` (non-null, matches the leonardo
signature), `shield_rev_declared="Rev 2.2"` (byte-equal to the operator's canonical-form
declaration), `controller_string` carries the standing, previously-measured `_HW_NOT_MEASURED_REASON`
placeholder (the `hw` CLI's own `-v` forwarding limitation, unrelated to this cell), the three
`image_*` fields carry the `--no-image-plan` not-measured placeholder, the two `fw_readback_sha_*`
fields carry the `--pending-readback` not-measured-pending placeholder, and `commands[]` records
the `hw` call and the four host-arm probe subprocess invocations (git HEAD, git porcelain,
`__file__` probe, interpreter version) — all absolute argv.

## Gate re-confirmation

`python3 .planning/milestones/v1.34-artifacts/tools/capture_provenance.py --selftest`: **31/31 legs PASS, exit 0**
(includes the two new seams' selftest coverage: `resolve_board_signature_from_json` — 1 positive
+ 3 negative legs; `build_no_image_plan_reason` — 2 positive legs).

`bash .planning/milestones/v1.34-artifacts/tools/run_gates.sh`: **12/12 tool selftests, 5/5 live gates, exit 0**
(captured directly via `$?`, never through a pipe) — `ALL GATES PASSED`.

## Non-claims

1. **The shield fitted here is a carrier, not a Rev 2.0 datum.** Its ADC/`hw` readings are not a
   SHIELD-04 result (Phase 163's own).
2. **The Leonardo's chip-out exemption is unchanged.** This pre-proof ran with an empty socket
   (operator-confirmed), consistent with standing bench rule 2's exemption for the Leonardo — but
   nothing here relaxes the Uno-class chip-out-before-sideload rule for A1 or A2; that rule
   applies only to `uno`/`uno328pb` and was never in scope on this board.

## Why no `EVIDENCE.jsonl` row exists for this cell

This cell's `cell_id` begins with the `BRINGUP-` prefix, which `EVIDENCE.jsonl`'s own schema header (`_schema.bringup_row_exclusion`) names explicitly: a row whose `cell_id` begins with `BRINGUP-` is rig evidence, excluded from the 20-position sweep close-out reconciliation. More directly: this cell holds no `WRV-VERDICT.json` at all -- no chip write ever ran here, so `judge_wrv.py` never produced one -- and `append_evidence.py` requires a `WRV-VERDICT.json` to derive a row's `outcome`/`sha256`/`verdict` columns; it structurally refuses to run without one. The absence of a row here is therefore correct-by-construction, not a gap a later reader should try to fill in.

## Leave-state (this cell only — full plan leave-state in Task 5's record)

- Board: Leonardo, Rev 2.2 fitted, on `/dev/ttyACM0`, remains attached at the end of this task.
  The uno328pb is **also** still attached on `/dev/ttyUSB0` (never unplugged this task — see the
  deviation note above); it is set aside logically, not physically, until cell A2 asks for it.
- Arm: v1.33 last invoked (the `hw`/provenance calls above); no flash was performed on the
  Leonardo in this task.
- Chip seated: none (operator-confirmed).
- Pot: untouched (no chip seated, `P-06` never ran).
- Shield: Rev 2.2, a pre-proof carrier only — A3/B2 will fit Rev 2.0.

## Task 5 — Bench handoff record (plan-level, not cell-specific)

Recorded here as the last pre-proof cell touched in this plan; applies to the whole plan, not
only this cell.

### `EVIDENCE.jsonl` unchanged

Line count and content are identical to the state at the end of plan 161-01 (which itself never
touched this file — last real write was Phase 160 Plan 12, `61fa09a4`). `git diff` against
`ecaf06e0` (the phase's first 161 commit) for this path is empty. 5 lines total (1 `_schema`
header + 4 Phase-160 bring-up rows: `BRINGUP-uno`, `BRINGUP-uno328pb`, `BRINGUP-leonardo`,
`BRINGUP-wrv`). No row's `cell_id` begins with `BRINGUP-uno328pb-v133` or
`BRINGUP-leonardo-provenance` — this plan's two pre-proof cells added none, per design.

### `~/.firestarter` baseline check (Amendment 3 clause 4)

```
files:      ['config.json']
tree_sha:   423546cd37b5b45d9654e5acd07bd7e2a3c9e1df77e4d5feb79951bf37329951
config_sha: b323867c1f01b22a705dd9caf003ab7302a249fe46772f5b02e44aaa2760dd79
mtime:      1787817565
```
All four values match the pinned Amendment 3 baseline exactly. **Verdict: unchanged.** No
deletion was attempted (the sandbox denies it, and deleting it would destroy the finding as
evidence).

### `check_arms.py --expect-config-sha` re-verification

```
python3 .planning/milestones/v1.34-artifacts/tools/check_arms.py --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --expect-config-sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0 \
  --out .../check_arms_teardown.json
```
rc=0. `check_arms OK: 2 arms verified (SHA+porcelain+file-probe+dep-freeze+interpreter+config-sha
+cli-surface)`. Recorded at
`.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-leonardo-provenance/check_arms_teardown.json`:
`config_dir_sha` matches the expected value exactly; both arms' `head`/`porcelain_clean`/
`dep_freeze`/`interpreter`/`file_probe` are unchanged from bring-up (Phase 160 Plan 01);
`surface_diff_ab`/`surface_diff_ba` both empty (25/25 CLI surface commands match between arms).
With assertion (1) (the directory's own baseline unchanged) holding and this assertion running
genuinely (not vacuously — every invocation in this plan set `FIRESTARTER_CONFIG_DIR` inline,
per standing bench rule 9), the two-assertion config-dir check for this plan is complete and
green.

### What plan 161-03 (cell A1) inherits

The **Uno + Rev 2.0 shield, W27C512 seated, v1.33 arm flashed, pot at 12.0 V** — untouched by
this plan, per plan 161-02's own prohibition (no chip seated on any board during this plan, no
chip write/read/erase/blank/vpp-set). It sits **disconnected** on the bench (confirmed off the
bus by descriptor absence at the Task 3 checkpoint measurement, `/dev/ttyACM1` absent). A1's own
`P-01` is where it goes back on — **with its chip coming out as part of that same handover**,
because A1's `P-02` runs an avrdude signature probe (`probe_board.py`) and the Uno-class
chip-out rule (standing bench rule 2) covers signature probes, not only writes. This plan does
not perform that handover; it only states what A1 must do first.
