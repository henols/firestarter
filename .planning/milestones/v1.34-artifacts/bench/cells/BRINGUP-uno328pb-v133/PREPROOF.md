# BRINGUP-uno328pb-v133 — D-10 Pre-Proof

**Cell type:** bring-up pre-proof, not a sweep cell. Holds no `WRV-VERDICT.json` and adds no row
to `EVIDENCE.jsonl` (see rationale below).

## What was previously proven and what was not

Two prior verdicts (`BRINGUP-uno328pb/READBACK-VERDICT.json`, `crossflash/READBACK-VERDICT.json`)
both judged a flash on the ATmega328PB against the **control** arm's span (26074 bytes) — one
deliberately mismatching (the D-03 cross-flash proof). Neither ever flashed the **v1.33** arm and
judged its own span.

| Verdict | Flashed arm | Expect arm | Result |
|---|---|---|---|
| `BRINGUP-uno328pb/READBACK-VERDICT.json` | control | control | judged_match (prior bring-up) |
| `crossflash/READBACK-VERDICT.json` | (other) | control | deliberate MISMATCH (D-03 proof) |
| **This pre-proof** | **v133** | **v133** | see below |

Without this pre-proof, cell A2 (plan 161-04) would be the first time a v1.33 flash on an
ATmega328PB is ever read back at all — and `P-04`'s halt policy (`P-H1`) classifies a read-back
mismatch on a correctly-flashed board as a rig halt. This pre-proof buys that first-contact risk
off the critical path.

## Precondition — no shield, no chip

**Operator-confirmed** (not derived): at the Task 1 checkpoint the operator explicitly stated
"uno328pb has no shield or eprom." This is a direct operator confirmation of the bare-board
precondition, received in-session — not an inference from the shield having stayed mounted on
the Uno that was set aside.

(A prior draft of this record stated the precondition as *derived* from the shield staying on the
set-aside Uno, on the reasoning that the chip socket lives on the shield. That reasoning is
superseded by the operator's direct confirmation above and is retained here only as a record of
the correction — the operative statement is the confirmation, not the inference.)

## Port identity

- Pre-swap enumeration (2026-08-27T12:33:22Z): `/dev/ttyACM0`, `/dev/ttyACM1` present, no
  `ttyUSB*`.
- Post-swap enumeration (orchestrator-measured, 2026-08-27T12:46:49Z): `/dev/ttyACM0` (vid:pid
  2341:8036, "Arduino Leonardo") present; `/dev/ttyUSB0` (vid:pid 1a86:7523, CH340 "USB Serial")
  present — this is the uno328pb; `/dev/ttyACM1` **absent** — the Uno (2341:0043, serial
  55736303739351B040E1) confirmed off the bus by descriptor absence, not merely by operator
  report.
- **Correction to the pre-swap assumption:** `STATE.md`'s SAFETY line, quoted at the Task 1
  checkpoint, claimed the Uno was on `/dev/ttyACM0`. That was stale — sysfs descriptors show
  `ttyACM0` was in fact the Leonardo and `ttyACM1` was the Uno. No node in this record or in any
  later task is re-derived from `STATE.md` prose; every node used below is re-enumerated and
  identity-checked by descriptor/signature.
- `$PORT` for this cell: `/dev/ttyUSB0`, confirmed present in the post-swap enumeration before
  use. Because two candidate serial nodes (`/dev/ttyACM0` Leonardo, `/dev/ttyUSB0` uno328pb) were
  simultaneously present, every avrdude/probe/upload invocation below passes an **explicit**
  `--port` / `-P` / `--upload-port` — none relies on autodetection.

## Commands run (literal, absolute argv)

### Step 0 — identity probe

```
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/probe_board.py --target uno328pb --port /dev/ttyUSB0 \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --out /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb-v133/board_probe.json
```
rc=0. Result: `connected_part=atmega328pb`, `board_signature=0x1e9516`, `mcu_matches=true`,
`signature_route=route1` — matches the expected constants exactly. Logged:
`logs/00_probe_board.std{out,err}.log`.

### Step 1 — firmware source state (assert, not change)

```
git -C /workspaces/firestarter rev-parse HEAD
git -C /workspaces/firestarter status --porcelain
```
`HEAD = 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463` — equal to `rig-pins.json`'s
`arms.v133.fw_sha`. Porcelain empty. No checkout was needed. Logged: `logs/01_git_state.stdout.log`.

### Step 2 — flash

```
cd /workspaces/firestarter && /usr/local/bin/pio run -t upload -e uno328pb --upload-port /dev/ttyUSB0
```
cwd: `/workspaces/firestarter` (never `/workspaces` — Pitfall 4). `--upload-port` passed
explicitly because two candidate nodes were present. rc=0, "1 succeeded in 00:00:08.796". Build
report: `Flash: 70.2% (used 23000 bytes from 32768 bytes)` — matches the v133 arm's expected hex
span (23000) exactly. PlatformIO resolved `urclock` / avrdude 8.1 and supplied its own flags; no
hand-rolled avrdude write was used. Logged: `logs/02_pio_upload.std{out,err}.log`,
`logs/02_pio_upload.argv.txt`.

### Step 3 — the proof (independent read-back judge)

```
python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno328pb --port /dev/ttyUSB0 \
  --flashed-arm v133 --expect-arm v133 \
  --out-dir /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-uno328pb-v133 \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json
```
rc=0. Both arm arguments are `v133` — a same-arm proof, not a cross-flash. Logged:
`logs/03_judge_readback.std{out,err}.log`, `logs/03_judge_readback.argv.txt`.

## The three success facts (measured values)

1. **`judged_match` is `true`.**
2. **`judged_span_bytes` is `23000`**, read at assertion time from `rig-pins.json`'s
   `targets.uno328pb.hex_span_expected_by_arm.v133` — not a literal embedded in any check, and
   explicitly **not** 26074 (the control-arm value) and not the legacy flat
   `hex_span_expected` scalar.
3. **`vector_exclusions_applied` carries both entries**: offset 0 length 4 (reset vector), offset
   100 length 4 (interrupt vector 25 / SPM_Ready) — both derived from the control-arm
   `-xshowvector` interrogation recorded in `rig-pins.json`, and both applied unchanged to this
   v133-arm flash's judgement.

**Explicit non-comparison:** `sha_actual_judged` (`bbf7aa68...`) and `sha_expected_judged`
(`75382672...`) are recorded but were **never compared** anywhere in this record or its
verification. On this target, 8 bytes are excluded from the byte-for-byte comparison
(`judge_span_bytes()`), but the two recorded fields are SHA-256 hashes of the **raw** (unexcluded)
spans — so a correct flash is *expected* to produce unequal raw-span SHAs. `judged_match` (the
byte-for-byte comparison honoring the exclusions) is the only field the success criterion reads;
comparing the two SHA fields directly is exactly the false-RED Pitfall 4 names, and this record
does not do it.

`readback_size_bytes` is `32768` (the whole-flash read), and `flash_readback.bin` on disk is
32768 bytes — matches. `sha_whole_flash_unjudged` (`e8aab2dc...`) is recorded as an explicitly
unjudged datum, never consulted in the match decision, per D-02.

## Vector-offset transfer — no policy change needed

`judged_match=true` on the first attempt, with the control-arm-derived vector offsets applied
unchanged to the v133-arm flash. The `vector-exclusion` policy's two offsets (reset vector at 0,
interrupt vector 25 at 100) transferred cleanly from the control-arm-derived interrogation to the
v1.33 image — both are properties of the **urclock bootloader's** behavior on this target
(where it redirects RESET and where it stores a copy of the original vector), not properties of
which firmware arm is flashed. No re-derivation via a fresh `--show-urclock` interrogation was
necessary, and `rig-pins.json` was **not** changed by this pre-proof.

## Non-claim

This pre-proof proves the **flash-and-read-back chain** on the ATmega328PB for the v1.33 arm —
that a v1.33 build can be flashed via PlatformIO's `urclock` upload path and independently read
back to a judged match against its own hex span, with the vector-exclusion policy applying
correctly. **It proves nothing about the chip-program path** — no chip was seated on this board
at any point (see Precondition above), and Backlog 999.2 predicts the chip-program path will
brown out on this MCU. Observing that is cell A2's job (plan 161-04), not assumed here.

## Why no `EVIDENCE.jsonl` row exists for this cell

This cell's `cell_id` begins with the `BRINGUP-` prefix, which `EVIDENCE.jsonl`'s own schema header (`_schema.bringup_row_exclusion`) names explicitly: a row whose `cell_id` begins with `BRINGUP-` is rig evidence, excluded from the 20-position sweep close-out reconciliation. More directly: this cell holds no `WRV-VERDICT.json` at all -- no chip write ever ran here, so `judge_wrv.py` never produced one -- and `append_evidence.py` requires a `WRV-VERDICT.json` to derive a row's `outcome`/`sha256`/`verdict` columns; it structurally refuses to run without one. The absence of a row here is therefore correct-by-construction, not a gap a later reader should try to fill in.

## Leave-state (this cell only — full plan leave-state in Task 5's record)

- Board: uno328pb, bare (no shield, no chip), still attached at `/dev/ttyUSB0` at the end of this
  task. It is set aside — untouched further — until cell A2 (plan 161-04) asks for it.
- Arm on it: v1.33 (last flash performed, per Step 2 above).
- Chip seated: none (operator-confirmed, see Precondition).
- Pot: untouched by this pre-proof (no chip seated, `P-06` never ran).
- Shield: none fitted.
