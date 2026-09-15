# BRINGUP-wrv — D-17 Fresh-Context Reconstruction (Plan 13, Task 1)

## Input list

Exactly two inputs were given to the reconstructing context, and nothing else:

1. **`bench/cells/BRINGUP-wrv/provenance.json`** — the bring-up position's provenance record
   (as it stood at the start of each round; round 2 and round 3 ran against a record this task
   itself corrected mid-exercise — see `RECONSTRUCTION-DIFF.md`).
2. **`.planning/milestones/v1.34-artifacts/PROCEDURE.md`** — the prescriptive procedure (round 3 ran against the
   version amended mid-exercise — see `RECONSTRUCTION-DIFF.md`, Amendment 2).

No plan text, no SUMMARY, no session transcript, no other cell artifact (`WRITE.md`, `POT.md`,
`WRV-VERDICT.json`, `READBACK-VERDICT.json`), no `IMAGE-PLAN.json`, and no `rig-pins.json` was
given to the reconstructing context at any round.

## How the separation was achieved

The reconstructing context was a genuinely **fresh context** — a **brand-new, disposable,
separate `claude -p` (Claude Code, model `claude-sonnet-4-5-20250929`) session**, spawned via
the Bash tool from this executing session, once per round, never the same process or context
as this executing session and never the same context as any other round:

- **No shared conversation history.** Each round is a fresh, one-shot, non-interactive,
  separate session (`claude -p ... < preamble.txt`) — not a `--continue` / `--resume` of this
  session or of any prior round. It has never seen this phase's plans, SUMMARYs, or any part
  of this conversation.
- **No tool access at all.** Every round was run with
  `--disallowedTools "Bash,Read,Edit,Write,Glob,Grep,WebFetch,WebSearch,Task,NotebookEdit,Skill"`
  (round 1 additionally listed `NotebookRead`, a no-op typo the CLI itself reported and
  ignored) — the reconstructing context had no filesystem, shell, or web access whatsoever
  and could reason only over the literal text pasted into its own prompt.
- **No project-level auto-context.** The working directory for each invocation was an
  isolated scratch directory outside `/workspaces` (under this session's own
  `scratchpad/recon-fresh*` subdirectories), so no `CLAUDE.md`, no user auto-memory
  (`MEMORY.md`), and no `git status` for this repository was available to auto-load into its
  system prompt — the two documents pasted into the prompt are the *only* channel of
  information into that context, exactly as RIG-05's property requires.
- **The two documents were pasted verbatim** into the one-shot prompt text (not referenced by
  path), so the reconstructing context could not have "found" a third file even if a
  filesystem tool had been left open.

Three rounds were run in total; the mechanism above was identical for all three. Only the
content of `provenance.json` and/or `PROCEDURE.md` differed between rounds, per the fixes
applied in between (see `RECONSTRUCTION-DIFF.md`).

---

## Round 1 — against the original record and the pre-amendment procedure

Captured verbatim, unedited, from the round-1 subprocess's stdout.

```
## Input list

1. **provenance.json** - JSON provenance record for position BRINGUP-wrv__v133__w27c512
2. **PROCEDURE.md** - Prescriptive procedure for v1.34 bench cell runs

---

## Ordered command set

### P-01 — Mount and declare
*(Operator action: Mount shield Rev 2.0 on Uno board, declare shield revision)*

### P-02 — Re-verify port identity

```bash
cd /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target uno --port /dev/ttyACM0 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/board_probe.json

cd /workspaces
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 hw
```

### P-03 — Uno-class chip-out (flash + read-back window)
*(Operator action: Remove ATmega328P from socket, confirm)*

### P-04 — Flash this arm, then prove it by independent read-back

```bash
cd /workspaces
git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463

cd /workspaces
git -C /workspaces/firestarter status --porcelain

cd /workspaces/firestarter
pio run -t upload -e uno

cd /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno --port /dev/ttyACM0 \
  --flashed-arm v133 --expect-arm v133 \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json
```

### P-05 — Uno-class: seat the first chip
*(Operator action: Seat W27C512 DIP28 chip in socket, confirm)*

### P-06 — Set the pot once per cell
*(Operator action: Adjust pot to 12.0V VPP target, report back)*

```bash
cd /workspaces
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp
```

### P-07 — Chip 1 write → read → judge (65536 B)

```bash
cd /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/gen_addr_image.py --stamp-width 16 65536 \
  GUESS/PLACEHOLDER:<mask_value> \
  .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin

cd /workspaces
time FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 write w27c512 \
  .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin

cd /workspaces
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 \
  dev consistency-check w27c512 --runs 3 \
  --output-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/reads --keep-files

cd /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/judge_wrv.py \
  --written .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin \
  --reads .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/reads \
  --expect-size 65536 \
  --app-verdict GUESS/PLACEHOLDER:<0_or_1_or_2_from_consistency_check_exit_code> \
  --position-id BRINGUP-wrv__v133__w27c512 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/wrv_verdict.json

cd /workspaces
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  python3 .planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id BRINGUP-wrv --position-id BRINGUP-wrv__v133__w27c512 \
  --arm v133 --target uno --port /dev/ttyACM0 --chip w27c512 \
  --shield-rev "Rev 2.0" \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/provenance_BRINGUP-wrv__v133__w27c512.json
```

### P-11 — Teardown

```bash
cd /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target uno --port /dev/ttyACM0 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out GUESS/PLACEHOLDER:<teardown_probe_output_path>

# Assertion 1: Verify ~/.firestarter does not exist
# (Shell check - not shown as explicit command in provenance)

cd /workspaces
python3 .planning/milestones/v1.34-artifacts/tools/check_arms.py \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --expect-config-sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0 \
  --out /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/check_arms_teardown.json
```

---

## Physical setup (operator-facing)

1. **Board**: Arduino Uno (ATmega328P-based, confirmed by signature 0x1e950f)
2. **Shield**: Rev 2.0 silkscreen marking
3. **Port**: Verify device enumerates at `/dev/ttyACM0` before starting
4. **Chip preparation**:
   - **Before P-03**: Remove ATmega328P from Uno socket (chip-out for bootloader flash window)
   - **At P-05**: Seat W27C512 DIP28 EPROM chip into shield socket
5. **VPP pot adjustment** (at P-06): Adjust pot to achieve 12.0V reading on VPP rail (operator sets, Claude confirms with one `vpp` read)
6. **No chip swap needed**: This position covers only W27C512 (first chip), not W29C020

---

## Explicit guesses / placeholders

### 1. **XOR mask for gen_addr_image.py** (P-07, first command)
   - **Value needed**: A mask value (likely hex or integer) for the `$MASK` parameter
   - **Why unknown**: The provenance record does not contain a `mask` field. PROCEDURE.md states this comes from `bench/IMAGE-PLAN.json` keyed by `position_id`, but that file was not provided in the two documents. Without this value, the test image cannot be generated and the write/read/judge cycle cannot proceed.

### 2. **app-verdict value for judge_wrv.py** (P-07, judge command)
   - **Value needed**: `0`, `1`, or `2` — the exit code from the `dev consistency-check` command
   - **Why unknown**: This is runtime-dependent (the exit code from the consistency-check that just ran). It's not in the provenance record because it's an outcome, not an input. The procedure says to pass this value to `judge_wrv.py --app-verdict` but marks it as determined at runtime.

### 3. **Teardown probe_board.py output path** (P-11)
   - **Value needed**: The `--out` path for the second (teardown) `probe_board.py` invocation
   - **Why unknown**: The provenance record shows only the P-02 (setup) probe output path (`board_probe.json`). PROCEDURE.md says to "re-run probe_board.py" at teardown but doesn't specify a different output filename. Likely needs a distinct path like `board_probe_teardown.json` to avoid overwriting the P-02 result, but this is not stated in either document.

### 4. **Absolute path to rig-pins.json** (inferred, not guessed)
   - **Used value**: `/workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json`
   - **Confidence**: High — all commands in the provenance show `cwd: /workspaces` and relative path `.planning/milestones/v1.34-artifacts/rig-pins.json`, so absolute path is derivable. Marking here for completeness as an inference rather than a stated value.

### 5. **Cell directory pre-existence** (inferred, not guessed)
   - **Assumption**: `.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/` directory already exists
   - **Why uncertain**: Neither document states whether the cell directory is created beforehand or by the first tool that writes to it. Commands write outputs directly to `$CELL_DIR/*` with no explicit `mkdir` shown, suggesting it pre-exists, but this is inferred behavior, not documented fact.
```

---

## Round 2 — against the record corrected for the mask/stamp_width/sha gap

Run after `capture_provenance.py` was extended (RECORD_KEYS +3: `image_mask`,
`image_stamp_width`, `image_sha`) and `bench/cells/BRINGUP-wrv/provenance.json` was
re-captured via the tool's new `--patch-image-plan` mode (zero device I/O — see
`RECONSTRUCTION-DIFF.md`). `PROCEDURE.md` was **not yet amended** for this round. Captured
verbatim, unedited, from the round-2 subprocess's stdout.

```
## Input list
1. DOCUMENT 1: `provenance.json` — JSON provenance record for position `BRINGUP-wrv__v133__w27c512`
2. DOCUMENT 2: `PROCEDURE.md` — v1.34 Bench Procedure for one arm-agnostic cell run

---

## Ordered command set

**Working directory: `/workspaces` (inferred from provenance `cwd` field on all commands)**

### P-01: Mount and declare (operator action)
Operator mounts shield with silkscreen "Rev 2.0" on uno board and declares it.

### P-02: Re-verify port identity
```bash
/usr/local/bin/python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/probe_board.py \
  --port /dev/ttyACM0 --target uno \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/board_probe.json

FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -v -p /dev/ttyACM0 hw
```

### P-03: Uno-class chip-out (operator action)
Operator removes chip from socket (uno-class requires chip-out for flash + read-back window).

### P-04: Flash this arm, then prove it by independent read-back
```bash
git -C GUESS/PLACEHOLDER: /workspaces/firestarter — reason: fw_sha is given but firmware repo location not explicitly stated in provenance; inferred from procedure text \
  checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463

git -C GUESS/PLACEHOLDER: /workspaces/firestarter — reason: same as above \
  status --porcelain

cd GUESS/PLACEHOLDER: /workspaces/firestarter — reason: same as above && \
  pio run -t upload -e uno

/usr/local/bin/python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/judge_readback.py \
  --target uno --port /dev/ttyACM0 \
  --flashed-arm v133 --expect-arm v133 \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/ \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json
```

### P-05: Uno-class: seat the first chip (operator action)
Operator seats W27C512 chip (DIP28, 28-pin) into socket.

### P-06: Set the pot once per cell
```bash
GUESS/PLACEHOLDER: skip this step if control arm positions already ran in this cell — reason: procedure states pot is set "once per cell, not once per chip", but provenance captured_at_step=2 doesn't tell whether this cell's pot was already set; if running truly "from scratch" then:

FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp
```
Operator adjusts pot to target 12.0V based on reading; Claude confirms with one read (command above).

### P-07: Chip 1 write → read → judge (65536 B)
```bash
/usr/local/bin/python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/gen_addr_image.py \
  --stamp-width 16 65536 36 .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin

time FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 write w27c512 \
  .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin

FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 \
  dev consistency-check w27c512 --runs 3 \
  --output-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/reads --keep-files

/usr/local/bin/python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/judge_wrv.py \
  --written .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin \
  --reads .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/reads \
  --expect-size 65536 \
  --app-verdict GUESS/PLACEHOLDER: <exit code from dev consistency-check above, 0/1/2> — reason: runtime value, not in provenance record \
  --position-id BRINGUP-wrv__v133__w27c512 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/wrv_verdict.json

FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config \
  /usr/local/bin/python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id BRINGUP-wrv --position-id BRINGUP-wrv__v133__w27c512 \
  --arm v133 --target uno --port /dev/ttyACM0 --chip w27c512 \
  --shield-rev "Rev 2.0" \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/provenance_BRINGUP-wrv__v133__w27c512.json
```

### P-11: Teardown (if running as standalone position; full cell would continue to P-08/P-09 for w29c020)
```bash
/usr/local/bin/python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/probe_board.py \
  --target uno --port /dev/ttyACM0 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out GUESS/PLACEHOLDER: .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/board_probe_teardown.json — reason: procedure mentions this but provenance doesn't record the actual output path used

/usr/local/bin/python3 /workspaces/.planning/milestones/v1.34-artifacts/tools/check_arms.py \
  --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --expect-config-sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0 \
  --out /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/check_arms_teardown.json
```

---

## Physical setup (operator-facing)

1. **Board mounting:** Mount the shield marked "Rev 2.0" (read from silkscreen) onto an Arduino Uno board. Ensure secure seating.

2. **Port identification:** Verify the board enumerates as `/dev/ttyACM0` (may require replug/checking; port identity must be re-verified per cell, never inherited).

3. **Chip-out for flash (Uno-class):** Before any programming/reading of the board's bootloader, remove the chip from its socket completely. Keep it out through both the firmware flash AND the read-back proof.

4. **Chip seating:** After firmware flash/read-back complete, seat the W27C512 chip (28-pin DIP28 package) into the socket. Verify orientation (pin 1 alignment).

5. **Pot adjustment (once per cell):** Adjust the potentiometer to achieve 12.0V VPP reading. Claude will confirm with one `vpp` command read — do not adjust during that read, just report the value. **If control arm positions already ran earlier this cell, skip this — pot is set once per cell, not per arm.**

6. **Chip remains seated:** The W27C512 stays in the socket through the write/read/judge sequence (P-07).

---

## Explicit guesses / placeholders

1. **Firmware repository location (`/workspaces/firestarter`)** — Provenance gives fw_sha `5759dc8d...` but doesn't record the git repo path where firmware lives. Procedure text says `git -C /workspaces/firestarter checkout <fw_sha>`, and the procedure's cwd context implies this location, but it's not confirmed in provenance.json itself.

2. **P-06 pot-setting necessity** — Procedure states pot is set "once per cell, not once per chip." Provenance doesn't record whether control arm positions already ran (which would have done P-06). If this position is truly "from scratch" for the entire cell, P-06 runs; if control arm already completed, it's already done. The `eeprom_calibration` fields say "not measured" but that's explained as a CLI limitation, not proof the pot wasn't set.

3. **`judge_wrv.py --app-verdict` value** — Must be the exit code (0/1/2) from the `dev consistency-check` command that runs immediately before it. This is a runtime value; provenance doesn't pre-record it because it's generated during this position's own execution.

4. **Board probe teardown output path** — Procedure mentions re-running `probe_board.py` at P-11 with output to `$CELL_DIR/board_probe_teardown.json`, but provenance's P-11 command only shows `check_arms.py`, not a second probe. Inferred the path from procedure text but not confirmed by provenance.

5. **Whether to continue to P-08/P-09 (w29c020 chip)** — Position ID `BRINGUP-wrv__v133__w27c512` is only the first chip (w27c512). A full cell runs both chips. User asked to re-run "this exact cell position" which could mean just w27c512 (stop at P-07) or continue through w29c020 (P-08/P-09). Commands above cover only w27c512 per the position ID given.

6. **Absolute vs. relative path conventions** — Provenance shows some paths as absolute (`/workspaces/.planning/...`) and others as relative (`.planning/...`), with cwd `/workspaces`. Commands above match provenance's exact argv where given, but for steps not in provenance's command array, the relative/absolute choice is inferred from procedure text and may differ from what actually ran.
```

---

## Round 3 — against the record corrected AND the procedure amended (Amendment 2)

Run after `PROCEDURE.md`'s `P-11` gained the literal `probe_board.py` re-run command block
(Amendment 2 — see `RECONSTRUCTION-DIFF.md`). `provenance.json` unchanged from round 2.
Captured verbatim, unedited, from the round-3 subprocess's stdout. (The first round-3
invocation returned a content-classifier refusal, `API Error: Sonnet 4.5 can't help with
this... Details: [bio]`, unrelated to any content in either document — an infrastructure
flake, not a finding. It was retried once, identically, and the retry is the transcript
below.)

```
## Input list

1. DOCUMENT 1: provenance.json - JSON provenance record for position `BRINGUP-wrv__v133__w27c512`
2. DOCUMENT 2: PROCEDURE.md - v1.34 Bench Procedure prescriptive document

---

## Ordered command set

### P-01: Mount and declare (operator action, no command)

### P-02: Re-verify port identity
```bash
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target uno --port /dev/ttyACM0 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/board_probe.json

FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 hw
```
GUESS/PLACEHOLDER: `/workspaces/.planning/milestones/v1.34-artifacts/config` for FIRESTARTER_CONFIG_DIR — reason: provenance gives only config_dir_sha, not the path; PROCEDURE.md says it comes from rig-pins.json field `config_dir`, but rig-pins.json itself is not provided

### P-03: Uno-class chip-out (operator action, no command)

### P-04: Flash this arm, then prove it by independent read-back
```bash
git -C /workspaces/firestarter checkout 5759dc8d644a8a7fb26e9a0ccd11a8bfd53fc463
git -C /workspaces/firestarter status --porcelain

cd /workspaces/firestarter && pio run -t upload -e uno

python3 .planning/milestones/v1.34-artifacts/tools/judge_readback.py --target uno --port /dev/ttyACM0 \
  --flashed-arm v133 --expect-arm v133 \
  --out-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv --pins .planning/milestones/v1.34-artifacts/rig-pins.json
```

### P-05: Uno-class: seat the first chip (operator action, no command)

### P-06: Set the pot once per cell
```bash
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 vpp
```

### P-07: Chip 1 write → read → judge (65536 B)
```bash
python3 .planning/milestones/v1.34-artifacts/tools/gen_addr_image.py --stamp-width 16 65536 36 .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin

time FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 write w27c512 .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin

FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config /workspaces/.v1.34-arms/v133/.venv/bin/firestarter -p /dev/ttyACM0 dev consistency-check w27c512 --runs 3 --output-dir .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/reads --keep-files

python3 .planning/milestones/v1.34-artifacts/tools/judge_wrv.py --written .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/written.bin \
  --reads .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/reads \
  --expect-size 65536 --app-verdict GUESS/PLACEHOLDER:<exit-code-0-1-or-2> \
  --position-id BRINGUP-wrv__v133__w27c512 --pins .planning/milestones/v1.34-artifacts/rig-pins.json \
  --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/wrv_verdict.json
```
GUESS/PLACEHOLDER: `<exit-code-0-1-or-2>` for --app-verdict — reason: provenance does not record the `dev consistency-check` exit code; PROCEDURE.md says this should be the 0/1/2 result from consistency-check

```bash
FIRESTARTER_CONFIG_DIR=/workspaces/.planning/milestones/v1.34-artifacts/config python3 .planning/milestones/v1.34-artifacts/tools/capture_provenance.py \
  --cell-id BRINGUP-wrv --position-id BRINGUP-wrv__v133__w27c512 \
  --arm v133 --target uno --port /dev/ttyACM0 --chip w27c512 --shield-rev "Rev 2.0" \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/provenance_BRINGUP-wrv__v133__w27c512.json
```

### P-08 through P-10: Not applicable
(This position is v133 arm with w27c512 chip only; chip swap and arm switch steps don't apply to re-running this single position)

### P-11: Teardown
```bash
python3 .planning/milestones/v1.34-artifacts/tools/probe_board.py --target uno --port /dev/ttyACM0 \
  --pins .planning/milestones/v1.34-artifacts/rig-pins.json --out .planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/board_probe_teardown.json

python3 .planning/milestones/v1.34-artifacts/tools/check_arms.py --pins /workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json \
  --expect-config-sha 77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0 \
  --out /workspaces/.planning/milestones/v1.34-artifacts/bench/cells/BRINGUP-wrv/check_arms_teardown.json
```

---

## Physical setup (operator-facing)

1. **Shield mounting (P-01)**: Mount the shield marked **"Rev 2.0"** on the silkscreen onto the target board (Uno-class, board signature 0x1e950f)

2. **Port connection**: Connect the board to port **/dev/ttyACM0** (verify port identity at start of run; do not assume from prior session)

3. **Chip removal for flash (P-03)**: Remove the microcontroller chip from its socket on the Uno board before firmware flash and read-back operations (steps P-04)

4. **Chip seating (P-05)**: Seat the **W27C512** chip (**DIP28 package**) into the EPROM socket on the shield

5. **Pot adjustment (P-06)**:
   - Target voltage: **12.0 V** (12000 mV) on VPP rail
   - Adjust the potentiometer until the VPP reading from the `vpp` command confirms the target
   - Take exactly one confirming read (no continuous monitoring loop)
   - **Important**: VPP and VPE monitors do not route to the socket — a blank/nonsense reading indicates contact fault, not voltage fault

6. **Post-run**: After all write/read operations complete, board can be powered down and disconnected

---

## Explicit guesses / placeholders

1. **FIRESTARTER_CONFIG_DIR path = `/workspaces/.planning/milestones/v1.34-artifacts/config`**
   - **Why guessed**: Provenance record provides only `config_dir_sha` (the content hash: `77adfdd26ed8710c4a70882e6dc9ee7bb494286fe225000d581f9e730dd77ad0`), not the filesystem path
   - **Source of inference**: PROCEDURE.md states this value comes from `rig-pins.json` field `config_dir`, but the rig-pins.json file itself is not provided in either document
   - **Impact**: This path is required for every firestarter command invocation (inline environment variable per Standing bench rule 9)

2. **--app-verdict argument for judge_wrv.py = `<exit-code-0-1-or-2>`**
   - **Why guessed**: The provenance record does not capture the exit code from the `dev consistency-check` command that generates the read files
   - **Source of inference**: PROCEDURE.md P-07 shows this should be the 0/1/2 exit code from consistency-check (0=all reads match, 1=disagreement, 2=error), but this is a runtime result not recorded in the provenance
   - **Impact**: Required argument for judge_wrv.py; affects how the tool interprets read consistency

3. **Absolute path to rig-pins.json = `.planning/milestones/v1.34-artifacts/rig-pins.json` (relative) or `/workspaces/.planning/milestones/v1.34-artifacts/rig-pins.json` (absolute)**
   - **Why uncertain**: Provenance commands show both forms used; working directory context determines which is correct
   - **Source of inference**: Commands in provenance use both forms; PROCEDURE.md tokens don't specify whether paths should be relative or absolute
   - **Impact**: All tool invocations require --pins argument; wrong path would cause tools to fail at startup
```

See `RECONSTRUCTION-DIFF.md` for the classification of every divergence across all three
rounds and the final, explicit sufficiency conclusion.
