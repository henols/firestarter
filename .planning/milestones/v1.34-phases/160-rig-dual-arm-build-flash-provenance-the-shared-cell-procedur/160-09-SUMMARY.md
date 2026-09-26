---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 09
subsystem: infra
tags: [bench, on-device, uno328pb, urclock, vector-bootloader, falsification, avrdude]

requires:
  - phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur (plan 08)
    provides: run_gates.sh, judge_readback.py, probe_board.py, gate_record.py, render_evidence.py, the BRINGUP-uno proven read chain, and the hex_span_expected_by_arm per-arm fix
provides:
  - "The uno328pb judged-span policy resolved from a live -xshowvector interrogation (vector-exclusion, 2 windows, 8 bytes) -- replaces rig-pins.json's PENDING-xshowvector placeholder"
  - "The uno328pb read chain proven on-device under that policy (32768 B read, -A explicit, judged_match=true)"
  - "D-03's wrong-arm detector observed firing for real on this target (22300/26066 judged bytes differ) and recovering"
  - "One EVIDENCE.jsonl bring-up row (BRINGUP-uno328pb), EVIDENCE.md re-rendered"
affects: [160-10-leonardo-bringup, 161-board-01-sweep-cells]

tech-stack:
  added: []
  patterns:
    - "Vector-bootloader judged-span exclusion derived from a live flash+read-back byte diff, not a recalled datasheet formula"
    - "Tool-defect discovery on first real-hardware exercise of a --show-urclock-class probe (mirrors 160-08's six live-hardware defects)"

key-files:
  created:
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/probe.json
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/BOOTLOADER.md
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/READBACK-VERDICT.json
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/CROSSFLASH.md
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/flash_readback.bin
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/SHA256SUMS.txt
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/crossflash/
    - .planning/v1.34/bench/cells/BRINGUP-uno328pb/logs/
  modified:
    - .planning/v1.34/rig-pins.json
    - .planning/v1.34/tools/probe_board.py
    - .planning/v1.34/tools/gate_record.py
    - .planning/v1.34/bench/EVIDENCE.jsonl
    - .planning/v1.34/bench/EVIDENCE.md
    - .planning/v1.34/PROCEDURE.md

key-decisions:
  - "This bootloader IS a vector bootloader (-xshowvector reported 'vector 25 (SPM_Ready)'); the milestone's sharpest false-RED risk is resolved by measurement, not by assumption."
  - "vector_exclusions windows (offset 0/length 4 for the reset vector; offset 100/length 4 for vector 25) were derived from a live flash+read-back diff against the control arm's own compiled hex -- exactly 5 bytes differed across the full 26074 B extent, all 5 inside these two windows, zero unexplained diffs elsewhere."
  - "The judged span for this target is arm-dependent (26074 B control / 23000 B v1.33, per rig-pins.json's hex_span_expected_by_arm, already fixed in 160-08); the plan's own prose/verify-script references to a flat 23000 B span are stale for the control arm and were not followed literally."

requirements-completed: []  # RIG-01 SC#2 is only partially discharged (uno + uno328pb); plan 10 still owes the leonardo leg before RIG-01 can be marked complete (per this plan's own "Requirement completion" instruction).

coverage:
  - id: D1
    description: "uno328pb judged-span policy resolved from a live -xshowvector bootloader interrogation (vector-exclusion, 8 bytes excluded), replacing rig-pins.json's PENDING-xshowvector placeholder"
    requirement: "RIG-01"
    verification:
      - kind: other
        ref: "python3 .planning/v1.34/tools/gate_record.py --cell (probe.json + rig-pins.json check embedded in 160-09-PLAN.md task 2 verify block)"
        status: pass
    human_judgment: false
  - id: D2
    description: "uno328pb read chain proven on-device (32768 B read-back, -A explicit, judged_match=true under the resolved policy) and D-03's wrong-arm detector observed firing (22300/26066 differing bytes) then recovering"
    requirement: "RIG-01"
    verification:
      - kind: other
        ref: "sha256sum -c SHA256SUMS.txt; python3 .planning/v1.34/tools/gate_record.py --jsonl .planning/v1.34/bench/EVIDENCE.jsonl; bash .planning/v1.34/tools/run_gates.sh"
        status: pass
    human_judgment: false

duration: 23min
completed: 2026-08-27
status: complete
---

# Phase 160 Plan 09: uno328pb Vector-Bootloader Judged-Span Resolution & Read-Chain Proof Summary

**Resolved the milestone's sharpest false-RED risk by direct measurement: `-xshowvector` proved the `uno328pb` bootloader patches the reset vector and vector 25 (SPM_Ready), and a live flash+read-back diff pinpointed the exact 8-byte exclusion windows, letting the read chain and D-03 wrong-arm detector run clean.**

## Performance

- **Duration:** ~23 min (operator gate at 06:19:38Z through final commit at 06:42:49Z)
- **Tasks:** 3/3 (task 1 operator gate was pre-satisfied by the orchestrator before this agent was spawned)
- **Files modified:** 6 modified, ~20 created (see frontmatter)

## Accomplishments

- Board identity confirmed by signature probe (`0x1e9516`, ATmega328PB) agreeing with the
  operator's silkscreen declaration, plus a corroborating signal (the `arduino` programmer
  fails to open against this board).
- The four `-xshowvector`/`-xshowall`/`-xshowboot`/`-xshowversion` bootloader interrogation
  queries run and recorded in full — `-xshowvector` answers the central question directly:
  `vector 25 (SPM_Ready)`, confirming this is a **vector** bootloader.
- The exact `vector_exclusions` windows (reset vector `[0,4)`, vector 25 `[100,104)`) derived
  from a live flash+read-back byte diff against the control arm's own compiled hex — 5
  differing bytes total, all inside these two windows, none unexplained.
- `rig-pins.json`'s `PENDING-xshowvector` placeholder replaced with the resolved
  `vector-exclusion` policy (scoped edit, diff-verified to touch only the two declared keys).
- The `uno328pb` read chain proven on-device: 32768 B read-back with `-A` explicit,
  `judged_match=true` under the resolved policy.
- D-03's deliberate wrong-arm cross-flash fired the negative control for real: the v1.33 arm
  flashed and judged against control's hex reported MISMATCH (22300 of 26066 actually-judged
  bytes differ, 85.6%), then the control arm was re-flashed and the correction observed
  matching (byte-identical whole-flash SHA to the pre-crossflash baseline).
- One `EVIDENCE.jsonl` row appended (`BRINGUP-uno328pb__control__none`), `EVIDENCE.md`
  re-rendered, `gate_record.py --jsonl` and `render_evidence.py --check` both green.
- `bash .planning/v1.34/tools/run_gates.sh` exits 0 (ALL GATES PASSED, 13 gate_record.py
  selftest legs + all live gates) before the final commit.

## Task Commits

1. **Task 1: Operator gate (board swap)** — pre-satisfied by the orchestrator before this
   agent was spawned; no separate commit (recorded verbatim below).
2. **Task 2: Interrogate the bootloader and derive the judged-span policy** — `1221196b` (feat)
3. **Task 3: Prove the read chain, D-03 cross-flash** — `fbd60380` (feat)

**Additional commit (in-scope minor doc fix, explicitly instructed in this plan's
`bench_rules_binding_on_you` section):** `15bbc282` (docs) — widened `PROCEDURE.md`'s
`ttyACM`-only wording to also cover `ttyUSB` (this board's CH340 bridge enumerates as
`ttyUSB0`), recorded as `PROCEDURE.md`'s Amendment 1.

_No plan-metadata commit was made separately from this SUMMARY's own commit below — this
plan's task commits already carry the full record; the final commit below adds only
SUMMARY.md/STATE.md/ROADMAP.md._

## Task 1 — Operator Gate (verbatim record, pre-satisfied)

Per the orchestrator's `<task_1_operator_gate_ALREADY_SATISFIED>` context, recorded here
verbatim as this plan's own SUMMARY of record:

- Pre-swap enumeration (2026-08-27T06:14:55Z): `["/dev/ttyACM0"]` (the wave-5 Uno)
- Operator-reported USB device: `"Bus 003 Device 023: ID 1a86:7523 QinHeng Electronics CH340 serial converter"`
- Post-swap enumeration (2026-08-27T06:19:38Z): `["/dev/ttyUSB0"]` (`ttyACM0` gone, `ttyUSB0` appeared 06:18)
- Operator's board declaration (silkscreen): **"ATmega328PB"**
- Operator's socket declaration: **"Yes — shield on, chip removed"** — **SUPERSEDED, see
  "Deviation 4" below. This declaration was false; the shield was not fitted during this
  plan's events. The correction does not change any measurement in this plan.**
- DEVPATH for `/dev/ttyUSB0`: `/devices/pci0000:00/0000:00:14.0/usb3/3-3/3-3.1/3-3.1.2/3-3.1.2.4/3-3.1.2.4:1.0/ttyUSB0/tty/ttyUSB0`
- **Port for this plan: `/dev/ttyUSB0`.**

Cross-check performed in Task 2: the operator's declaration (`ATmega328PB`) agrees with the
live signature probe (`0x1e9516` → `atmega328pb`). No disagreement — the plan continued.

## Files Created/Modified

- `.planning/v1.34/rig-pins.json` — `targets.uno328pb.judged_span_policy` resolved
  (`PENDING-xshowvector` → `vector-exclusion`), `vector_exclusions` populated with 2 measured
  windows (scoped edit).
- `.planning/v1.34/tools/probe_board.py` — Rule 1 fix: `_URCLOCK_PROBES` carried the wrong
  urclock option name `-xshowbootsize`; corrected to `-xshowboot`.
- `.planning/v1.34/tools/gate_record.py` — Rule 1 fix: the forbidden-flags check blindly
  token-matched `-b` against every command, rejecting avrdude's own legitimate baud-rate
  argument; scoped the exemption to the pinned avrdude binary, added positive+negative
  selftest legs.
- `.planning/v1.34/bench/cells/BRINGUP-uno328pb/probe.json`, `BOOTLOADER.md` — board identity
  + the four interrogation queries in full + the derivation.
- `.planning/v1.34/bench/cells/BRINGUP-uno328pb/READBACK-VERDICT.json`,
  `flash_readback.bin`, `judged_span.bin`, `SHA256SUMS.txt`, `CROSSFLASH.md`, `crossflash/`,
  `logs/` — the read-chain proof and D-03 cross-flash record.
- `.planning/v1.34/bench/EVIDENCE.jsonl`, `EVIDENCE.md` — one bring-up row appended/rendered.
- `.planning/v1.34/PROCEDURE.md` — widened `ttyACM`-only wording to also name `ttyUSB`
  (Amendment 1).

## Decisions Made

- **Vector bootloader confirmed by direct measurement, not inferred.** `-xshowvector`'s output
  (`vector 25 (SPM_Ready)`) is the specific, quoted evidence establishing the determination;
  no other route (guessing, copying research prose, or picking whatever makes the judge green)
  was used.
- **Exclusion windows derived from a live diff, not a recalled datasheet formula.** A
  diagnostic flash+read-back of the control arm, diffed byte-for-byte against its own compiled
  hex over the full 26074 B extent, found exactly 5 differing bytes, all confined to two 4-byte
  windows (`[0,4)` and `[100,104)`) — both decoding as AVR `JMP` instructions, confirming the
  vector-patch mechanism precisely. Zero unexplained diffs anywhere else in the judged extent.
- **The judged span is arm-dependent; the plan's flat "23000 B" references are stale.** The
  control arm's own `uno328pb` hex spans 26074 B (`rig-pins.json`'s
  `hex_span_expected_by_arm.control`, fixed in 160-08); `23000` is the v1.33 arm's span. Every
  event in this plan judges the control arm against its own arm-correct span. This is the same
  class of pre-existing plan-authoring staleness `BRINGUP-uno`'s `CROSSFLASH.md` already
  documented for `uno` (there, `22952` was mistaken for control's span).
- **Ad hoc diagnostic avrdude/objcopy commands are not duplicated into `EVIDENCE.jsonl`'s
  top-level `commands` list.** They are fully quoted (literal argv + cwd) in `BOOTLOADER.md`'s
  prose instead — consistent with how tool-internal avrdude invocations (inside
  `judge_readback.py`/`probe_board.py`) are also not duplicated at the top level; only
  commands Claude ran directly at the top level (git, pio, the rig's own python tools, and the
  one direct corroborating avrdude open-attempt) are recorded there.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `probe_board.py`'s urclock boot-size query used the wrong option name**
- **Found during:** Task 2 (bootloader interrogation)
- **Issue:** `_URCLOCK_PROBES` carried `-xshowbootsize`, copied verbatim from
  160-RESEARCH.md's own speculative, never-run Code Example 5. Run live, avrdude rejects it
  (`Error: invalid extended parameter -x showbootsize`); the real option is `showboot`.
- **Fix:** Corrected `_URCLOCK_PROBES` to `-xshowboot`; re-ran the corrected four-probe set.
  Both the pre-fix error and the post-fix data are preserved verbatim in `BOOTLOADER.md` and
  `logs/`.
- **Files modified:** `.planning/v1.34/tools/probe_board.py`
- **Verification:** `probe_board.py --selftest` still passes (8/8); the corrected probe
  returned `384` (matching `rig-pins.json`'s recorded `"urboot 384 B"`).
- **Committed in:** `1221196b` (Task 2 commit)

**2. [Rule 1 - Bug] `gate_record.py`'s forbidden-flags check misfired on avrdude's own `-b` (baud) argument**
- **Found during:** Task 3 (assembling the `EVIDENCE.jsonl` row, which includes a direct
  avrdude invocation — the corroborating `arduino`-programmer open-attempt)
- **Issue:** `rig-pins.json`'s `forbidden_flags` includes `-b` for the withdrawn
  `firestarter_app` `--no-blank-check` flag (Phase 145 D-17), but `check_commands()` did a
  blind token match against every recorded command's argv regardless of which binary was
  invoked — rejecting avrdude's own, wholly unrelated `-b <baud>` argument (present in every
  avrdude invocation this rig makes) as though it were the withdrawn app flag.
- **Fix:** Scoped the exemption to the pinned avrdude binary specifically (not a blanket
  exemption); added a positive selftest leg (avrdude's own `-b` passes) and a negative leg
  confirming the exemption does not leak to other binaries (`-b` on an arm `write` command is
  still caught).
- **Files modified:** `.planning/v1.34/tools/gate_record.py`
- **Verification:** `gate_record.py --selftest` passes 13/13 legs (was 11/11; +2 new legs);
  `bash run_gates.sh` still ALL GATES PASSED.
- **Committed in:** `fbd60380` (Task 3 commit)

**3. [Rule 2 - instructed minor scope addition] `PROCEDURE.md`'s port-node wording widened**
- **Found during:** Task 1 (the operator's reported node was `/dev/ttyUSB0`, not `ttyACM*`)
- **Issue:** The orchestrator's own `bench_rules_binding_on_you` context explicitly named this
  as "in scope if you touch it," and this plan's own board is the exact case the old wording
  didn't cover.
- **Fix:** Widened standing bench rule 1 and the `$PORT` token row to name both `ttyACM*` and
  `ttyUSB*`; recorded as `PROCEDURE.md`'s Amendment 1 (dated, naming what/why/which-cells-ran-under-which-text)
  per the file's own amendment-discipline rule.
- **Files modified:** `.planning/v1.34/PROCEDURE.md`
- **Verification:** `render_steps.py --selftest` and the SC#3 live gate (empty diff,
  control=11/v133=11 lines) unaffected — only prose outside the `## Step list` section moved.
- **Committed in:** `15bbc282` (separate docs commit)

**4. [Record correction, added 2026-08-27 at plan closeout] Task 1's socket declaration was false — no shield was fitted during this plan's events**

- **Found during:** Post-execution record correction, before this plan's closeout commit —
  the operator, presented with this plan's own record, corrected their own prior statement.
- **What was recorded (false):** Task 1's operator gate captured the operator's socket
  declaration verbatim as **"Yes — shield on, chip removed"**, and this SUMMARY (the line
  above, now marked SUPERSEDED) and `bench/EVIDENCE.jsonl` row 3's `shield` field both
  faithfully recorded that false declaration at the time. The orchestrator's own presented
  context for this closeout also independently confirmed this declaration was passed to the
  original executor as fact and recorded as reported — the defect entered the record honestly,
  from an input that was itself wrong.
- **What was actually true (operator's own correction, verbatim):** *"I sad the sheil was on
  but it wasnt, so i added it now"* / *"I sad the sheil was on but it wasnt, now its on."* **No
  shield was fitted for the entire duration of this plan's on-device work** — task 2's
  bootloader interrogation and task 3's three flash-and-judge events, spanning
  06:23:xx–06:34:30Z. The operator then unplugged the board, fitted the shield, and replugged it
  (confirmed verbatim: *"Yes — unplugged, fitted, replugged"*), at approximately 06:34:40Z —
  *after* task 3's Event 3 (the correction flash) had already completed. A chip is seated **now**
  (operator: *"Yes — a chip is seated now"*), which is the current, post-run state, not the
  state during any measurement this plan reports.
- **Corroborating evidence (independent of the operator's statement):** `/dev/ttyUSB0`'s device
  node creation time moved from 06:18 to **06:34:40**, matching the operator's described replug.
  The log-file mtimes bracket the event precisely: `09_pio_upload_control_correction_event3.stdout.log`
  is timestamped **06:34:30.52** (Event 3's flash completes — avrdude's own stderr reports
  `"26240 bytes of flash verified"`), and `10_judge_readback_correction_event3.stdout.log` is
  timestamped **06:34:43.55** (Event 3's judged read-back), i.e. ~3 s **after** the replug and
  ~13 s after the correction flash's own self-verification.
- **Three conclusions, derived rather than asserted:**
  1. **No safety invariant was violated.** With no shield fitted, there is no socket and
     therefore no chip present for the board's entire time under test in this plan. The
     Uno-class chip-out rule exists to keep a chip out of the socket while avrdude drives the
     bus; with no shield at all, there is no socket to hold a chip, so the rule is satisfied *a
     fortiori* for every avrdude invocation this plan made. The shield (and, per the operator, a
     chip) arrived only after the last flash in this plan's record.
  2. **The plan's own requirements are unaffected.** Task 1's own text states: *"A shield is
     not required — the flash and read-back need the board only."* The absence of a shield
     during this plan's events is exactly the condition the plan itself anticipated as
     sufficient; every measurement in `BOOTLOADER.md`, `READBACK-VERDICT.json`, and
     `CROSSFLASH.md` stands unchanged. Only the record's *description* of the physical state
     was wrong — not the correctness of anything measured.
  3. **The mid-run replug was harmless, shown rather than assumed.** Event 3's correction flash
     self-verified as complete and byte-correct (avrdude's own "26240 bytes of flash verified")
     roughly 10 s **before** the replug at ~06:34:40. Flash memory is non-volatile, so an
     unplug/replug following a completed, self-verified write does not alter its content; a
     serial replug forces the normal device reset any avrdude read already requires. Event 3's
     judged read-back, run ~3 s after the replug, reported `judged_match = true` with
     `sha_whole_flash_unjudged` byte-identical to Event 1's value — an independent, non-judged
     confirmation that the flash content the replug bracketed did not change. No evidence in
     this plan's record contradicts this; had a truncated read, a whole-flash SHA divergence, or
     a judged mismatch appeared, it would be reported instead of this conclusion.
- **Files corrected:** `bench/EVIDENCE.jsonl` (row 3's `shield` field), `bench/EVIDENCE.md`
  (re-rendered), `probe.json` (added `operator_declared_board`, `operator_declared_socket_state`
  [corrected], `operator_probe_agreement`, `operator_probe_agreement_note`,
  `device_node_enumeration_check`, `device_node_reenumeration_midrun_replug` — bringing this
  cell to parity with plan 08's `BRINGUP-uno/probe.json` shape), `CROSSFLASH.md` (new "Mid-run
  replug" section with the timing table and the harmlessness derivation), this SUMMARY (task 1
  record marked SUPERSEDED above, this Deviation 4 entry).
- **Verification:** `bash .planning/v1.34/tools/run_gates.sh` exits 0 after the correction
  (host-only legs only — no device I/O was performed for this correction, consistent with the
  chip currently seated in this board's socket being unsafe to drive right now).
- **Committed in:** the `fix(160-09):` record-correction commit, separate from this plan's
  original three task commits (which are unchanged and remain correct as measurements — only
  the description of the physical state during them was wrong).

---

**Total deviations:** 3 auto-fixed during execution (2 Rule 1 bugs, 1 Rule 2/instructed doc
addition), plus 1 post-execution record correction (Deviation 4, above) fixing a false operator
declaration that entered the record honestly but was itself wrong.
**Impact on plan:** All three in-execution deviations were necessary for correctness (a wrong
option name, a false-positive gate check) or explicitly instructed; no scope creep beyond what
the plan and its accompanying orchestrator context called for. The record correction affects no
measurement's validity — it corrects only the record's description of a physical state that
was never actually load-bearing for this plan's own requirements (task 1: "a shield is not
required").

## Issues Encountered

None beyond the deviations above. The board swap, signature probe, bootloader interrogation,
read chain, and D-03 cross-flash all completed cleanly on the first attempt once the two tool
defects were fixed.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `uno` (plan 08) and `uno328pb` (this plan) both have proven read chains and observed,
  recovered wrong-arm detectors. Plan 10 (`leonardo`) is the remaining bring-up target before
  RIG-01 SC#2 is fully discharged across all three targets.
- The board currently carries the `control` arm (deliberate, per this plan's own
  correction-sequence instruction). The `firestarter/` submodule is restored to its starting
  ref (`gsd/v1.33-source-hygiene-firmware-size-reduction` @ `5759dc8d`) and porcelain-clean.
- `rig-pins.json`'s `uno328pb.judged_span_policy` is now a resolved, non-placeholder value —
  Phase 161's sweep cells that touch this target can proceed without re-deriving it.

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Plan: 09*
*Completed: 2026-08-27*

## Self-Check: PASSED

All declared artifacts (`probe.json`, `BOOTLOADER.md`, `READBACK-VERDICT.json`,
`CROSSFLASH.md`, `flash_readback.bin`, `SHA256SUMS.txt`, `rig-pins.json`, `probe_board.py`,
`gate_record.py`, `EVIDENCE.jsonl`, `EVIDENCE.md`, `PROCEDURE.md`, this SUMMARY.md) confirmed
present on disk. All three commits (`1221196b`, `fbd60380`, `15bbc282`) confirmed present in
`git log`.
