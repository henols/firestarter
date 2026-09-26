---
phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
plan: 10
subsystem: infra
tags: [bench, avrdude, avr109, caterina, 1200-baud-touch, leonardo, flash-provenance, cross-flash]

requires:
  - phase: 160 (plans 08, 09)
    provides: the uno and uno328pb read-chain proofs and D-03 cross-flash detectors, plus the
      arm-span (hex_span_expected_by_arm) fix this plan's own verify script needed again
provides:
  - The leonardo Caterina/avr109 read chain proven on-device (full 32768 B read-back, judged
    28170 B control hex extent, judged_match=true)
  - The Caterina bootloader-entry behaviour for this exact board measured for the READ
    direction: same-node (not new-node), settle 2.0s, touch-to-responsive-programmer 3.487s
  - D-03 completed across all three targets: leonardo's wrong-arm detector observed FIRING
    (24454/28170 bytes, 86.8%) then corrected
  - RIG-01 (SC#2 on all three targets) marked complete
affects: [161, 162, 163, PROCEDURE.md P-04]

tech-stack:
  added: []
  patterns:
    - "1200-baud touch, then IMMEDIATE avrdude invocation in the same shell block with no
       added delay, is the only mode that fits this board's Caterina window on the read
       direction (the --wait-new-port mode is the wrong one here and burns window time)"

key-files:
  created:
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/probe.json
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/BOOTLOADER-WINDOW.md
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/READBACK-VERDICT.json
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/flash_readback.bin
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/SHA256SUMS.txt
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/CROSSFLASH.md
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/crossflash/ (READBACK-VERDICT.json, flash_readback.bin, judged_span.bin, expected_span.bin, SHA256SUMS.txt, avrdude_read.stderr.log)
    - .planning/v1.34/bench/cells/BRINGUP-leonardo/logs/ (14 invocation logs)
  modified:
    - .planning/v1.34/rig-pins.json (targets.leonardo: measured post-touch behaviour, timing)
    - .planning/v1.34/bench/EVIDENCE.jsonl (BRINGUP-leonardo row appended)
    - .planning/v1.34/bench/EVIDENCE.md (re-rendered)
    - .planning/v1.34/tools/probe_board.py (Rule 1 fix: subprocess decode robustness)
    - .planning/v1.34/tools/judge_readback.py (Rule 1 fix: same class)
    - .planning/REQUIREMENTS.md (RIG-01 marked Complete)

key-decisions:
  - "The Caterina read-direction bootloader-entry behaviour for this board is SAME NODE, not
     a new node -- measured, not assumed, via two independent touch cycles"
  - "The bare (settle-only, reuse --port) touch_1200.py mode is correct for this board's read
     chain; --wait-new-port is the wrong mode and was shown, live, to burn window time"
  - "Both read-back-affecting tools (probe_board.py, judge_readback.py) needed a subprocess
     text-decode robustness fix (errors=\"replace\") before the Leonardo's non-bootloader
     response bytes could be handled as a reported failure instead of a crash"

requirements-completed: [RIG-01]

coverage:
  - id: D1
    description: "leonardo Caterina/avr109 read chain proven on-device: full 32768 B read-back, judged_match=true over the control arm's 28170 B hex extent"
    requirement: RIG-01
    verification:
      - kind: other
        ref: "bash .planning/v1.34/tools/run_gates.sh (ALL GATES PASSED, exit 0); .planning/v1.34/bench/cells/BRINGUP-leonardo/READBACK-VERDICT.json judged_match=true"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-03 wrong-arm cross-flash on leonardo: negative control FIRED (24454/28170 differing bytes) then corrected"
    requirement: RIG-01
    verification:
      - kind: other
        ref: ".planning/v1.34/bench/cells/BRINGUP-leonardo/crossflash/READBACK-VERDICT.json judged_match=false, diff_count=24454; CROSSFLASH.md Event 3 correction judged_match=true"
        status: pass
    human_judgment: false
  - id: D3
    description: "Bootloader-entry behaviour measured and pinned into rig-pins.json for PROCEDURE.md's later cells on this board"
    requirement: RIG-01
    verification:
      - kind: other
        ref: ".planning/v1.34/bench/cells/BRINGUP-leonardo/BOOTLOADER-WINDOW.md; rig-pins.json targets.leonardo.measured_post_touch_port_behavior"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-08-27
status: complete
---

# Phase 160 Plan 10: Leonardo Caterina/avr109 Read Chain + D-03 Completion Summary

**Proved the milestone's lowest-confidence read chain (Caterina bootloader, 1200-baud touch,
avr109) on-device — full 32768 B read-back, judged_match=true, 3.878s from touch to verdict
against an ~8s window — and completed D-03's wrong-arm cross-flash falsification across all
three AVR targets, closing RIG-01.**

## Performance

- **Duration:** ~20 min (on-device portion; excludes prior context-reading)
- **Started:** 2026-08-27T07:07:54Z (cell directory created)
- **Completed:** 2026-08-27T07:22:34Z
- **Tasks:** 3/3 (task 1's operator gate was pre-satisfied by the orchestrator; tasks 2–3 executed)
- **Files modified:** 31 created/modified across the cell directory, `rig-pins.json`,
  `EVIDENCE.jsonl`/`EVIDENCE.md`, two tool files, and `REQUIREMENTS.md`

## Accomplishments

- **Task 1 (operator gate, pre-satisfied):** the orchestrator's pre-swap/post-swap enumeration
  (`["/dev/ttyUSB0"]` → `["/dev/ttyACM0"]`) and the operator's verbatim declaration ("Leonardo,
  sheild and w27c512 seated") were recorded verbatim and carried into task 2, per the
  instruction not to re-ask or re-derive them.
- **Task 2:** measured the Caterina bootloader-entry behaviour for the READ direction on this
  exact board — **same node**, never a new one, confirmed by two independent touch cycles
  (`BOOTLOADER-WINDOW.md`). Identified the board (ATmega32U4, signature `0x1e9587`, matching
  the operator's declaration). Flashed the control arm via PlatformIO and proved the full
  32768 B read-back independently: `judged_match=true`, judged span 28170 B (control's own
  `leonardo` hex extent), completed 3.878 s after the read-back touch — comfortably inside
  Caterina's ~8 s inactivity window, and faster than both the `uno` (~5.5 s) and `uno328pb`
  (~4.07 s) read-chain baselines despite the lowest baud rate of the three (57600).
- **Task 3:** completed D-03 across all three targets. Flashed the v1.33 arm and judged it
  against the control arm's hex — the negative control **FIRED** with 24454/28170 (86.8%)
  differing bytes — then flashed control back and confirmed the correction
  (`judged_match=true`, whole-flash SHA byte-identical to the pre-crossflash baseline).
  `CROSSFLASH.md`'s cross-target rollup states plainly that all three chains (`uno` 86%,
  `uno328pb` 85.6%, `leonardo` 86.8%) now have their detectors observed failing for real, and
  that no named alternative (SC#2's escape hatch) was needed on any of the three targets.
- Appended the `BRINGUP-leonardo` row to `bench/EVIDENCE.jsonl` (three bring-up rows now
  present, zero sweep rows — correctly excluded from the 20-position close-out count),
  re-rendered `EVIDENCE.md`, and ran the full `run_gates.sh` suite: **ALL GATES PASSED**
  (exit 0, measured directly, not through a pipe).
- **RIG-01 marked Complete** in `REQUIREMENTS.md` — this plan is the third and last of the
  three plans (08/09/10) that together discharge SC#2 across all three targets; RIG-01 as a
  whole is complete because plan 02 already closed SC#1.

## Task Commits

1. **Task 2: Measure the bootloader window and prove the leonardo read** — `8ddc06c8` (feat)
2. **Task 3: D-03 on leonardo — completing the cross-flash falsification** — `ac300700` (docs)

**Plan metadata:** (this commit, following)

_Task 1 required no commit — it was a checkpoint gate already satisfied by the orchestrator
before this executor was spawned; its declarations are recorded above and in `probe.json`._

## Files Created/Modified

- `.planning/v1.34/bench/cells/BRINGUP-leonardo/probe.json` — signature probe result, augmented
  with the operator-declaration fields (board, chip-seated state, shield, device-node
  enumeration check) matching the shape the two prior bring-ups established
- `.planning/v1.34/bench/cells/BRINGUP-leonardo/BOOTLOADER-WINDOW.md` — the full bootloader-entry
  measurement: two touch cycles, the informative pre-touch and `--wait-new-port` failures, the
  working procedure, and the timing margin
- `.planning/v1.34/bench/cells/BRINGUP-leonardo/READBACK-VERDICT.json`, `flash_readback.bin`,
  `judged_span.bin`, `expected_span.bin`, `SHA256SUMS.txt` — the control-arm read-back proof
  (Event 1, re-established by Event 3's correction)
- `.planning/v1.34/bench/cells/BRINGUP-leonardo/CROSSFLASH.md` — the three-event cross-flash
  record and the cross-target D-03 rollup
- `.planning/v1.34/bench/cells/BRINGUP-leonardo/crossflash/` — the v1.33-on-control-hex MISMATCH
  artifacts (Event 2)
- `.planning/v1.34/bench/cells/BRINGUP-leonardo/logs/` — 14 per-invocation stdout/stderr captures
- `.planning/v1.34/rig-pins.json` — `targets.leonardo` gains `measured_post_touch_port_behavior`,
  `measured_touch_settle_s`, `measured_touch_to_responsive_programmer_s`,
  `measured_touch_to_read_complete_s` (scoped edit, verified by diff to touch only this target)
- `.planning/v1.34/bench/EVIDENCE.jsonl` — `BRINGUP-leonardo` row appended (append-only, via
  `render_evidence.py --append`)
- `.planning/v1.34/bench/EVIDENCE.md` — re-rendered, `--check` green
- `.planning/v1.34/tools/probe_board.py`, `.planning/v1.34/tools/judge_readback.py` — Rule 1
  fix: `subprocess.run(..., text=True)` → `text=True, errors="replace"` in every avrdude/
  avr-objcopy invocation, so a device answering with non-UTF-8 bytes produces a reported
  `FAIL:` line instead of crashing with `UnicodeDecodeError`
- `.planning/REQUIREMENTS.md` — RIG-01 checkbox and status table flipped to Complete

## Decisions Made

- **Same-node touch mode, not new-node:** measured live rather than assumed, per the plan's
  own instruction and `touch_1200.py`'s own selftest note that this was unproven. Two
  independent cycles agreed; `--wait-new-port` was tried first (per instruction not to assume
  a particular answer) and its failure (timeout, no new node) is recorded as informative data,
  not discarded.
- **Fold the identity probe into the first touch cycle rather than running it pre-touch:**
  the plan's prose lists "First, identity" before "Second, measure the window," but
  `probe_board.py`'s avr109 signature probe requires the Caterina bootloader to be active
  (the application firmware does not answer an avr109 handshake at all). This was measured
  directly (Attempt 0, a clean `FAIL: neither parse route matched` after the Rule 1 decode
  fix) before proceeding, and the identity probe was run immediately after the second,
  successful touch cycle instead.
- **One touch cycle spent purely on measurement, a separate one for the actual read:** matches
  the plan's own task-2/task-3 structure (measure first, then prove); the measurement cycle's
  informative failures cost nothing because Caterina auto-reverted to the application on its
  own afterward.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `probe_board.py` / `judge_readback.py` subprocess text-decode crash**
- **Found during:** Task 2, first live invocation of `probe_board.py` against the Leonardo
  before any touch
- **Issue:** `subprocess.run(..., capture_output=True, text=True, check=False)` decodes stdout/
  stderr with the strict default `'utf-8'` error handler. A Leonardo running its application
  firmware (not the Caterina bootloader) answers an `avr109` handshake attempt with raw,
  non-protocol serial bytes; avrdude echoes some of that into its own diagnostic text, and the
  strict decoder crashed the tool with `UnicodeDecodeError: 'utf-8' codec can't decode byte
  0xaa in position 564` instead of producing a reported `FAIL:` line.
- **Fix:** added `errors="replace"` to the `subprocess.run` call in `probe_board.py`'s
  `run_avrdude()` and to both calls in `judge_readback.py` (`run_avrdude_read()`,
  `run_objcopy_normalize()`) — the same class of device-facing subprocess call in the same
  toolset.
- **Files modified:** `.planning/v1.34/tools/probe_board.py`, `.planning/v1.34/tools/judge_readback.py`
- **Verification:** both tools' `--selftest` re-run clean after the fix (12 selftest legs
  total, all PASS); the subsequent live invocation against the same board produced the clean,
  parseable `FAIL: neither parse route matched avrdude stderr: 'Error: initialization failed...'`
  message this fix exists to make possible.
- **Committed in:** `8ddc06c8` (task 2 commit)

**2. [Rule 1 - Plan-authoring defect, documented not silently corrected] Task 2's embedded
verify script hardcodes a flat, arm-agnostic judged-span literal (25098 B)**
- **Found during:** Task 2's own acceptance-criteria verification step
- **Issue:** `160-10-PLAN.md`'s task 2 `<verify>` block asserts `judged_span_bytes == 25098`
  as the Branch-A full-read criterion. `25098` is the **v1.33** arm's own `leonardo` hex span
  (`rig-pins.json` `hex_span_expected_by_arm.leonardo.v133`), not the **control** arm's
  (`28170`) — the identical class of stale flat-constant defect `BRINGUP-uno` and
  `BRINGUP-uno328pb` already documented for their own targets in plans 08/09 (fixed there in
  160-08 for the pins file itself, but the plan's own prose/verify-script literal was never
  re-derived).
- **Fix:** ran a corrected assertion substituting
  `rig-pins.json`'s `hex_span_expected_by_arm.leonardo.control` (28170) for the plan's
  hardcoded `25098` literal, in place of the plan's own script. The actual read-back is
  correct and was never in question — only the plan's own verify-script literal was stale.
- **Files modified:** none (no code changed; this is a plan-authoring note, recorded per the
  same precedent `BRINGUP-uno`/`BRINGUP-uno328pb` established)
- **Verification:** the corrected assertion passes: `OK branch A (corrected for the arm-span
  defect): full 32768 B read, judged 28170 B matches control hex extent`
- **Committed in:** documented in `CROSSFLASH.md`'s "Deviation note" section (task 3 commit
  `ac300700`) and here

---

**Total deviations:** 2 (1 Rule-1 tool bug fixed in-phase, 1 Rule-1-class plan-authoring defect
documented and worked around without a code change)
**Impact on plan:** Both are the same class of issue the two prior bring-up plans already hit
and fixed for their own targets. No scope creep; both are directly necessary for this plan's
own correctness.

## Issues Encountered

None beyond the two deviations above. The board never became unresponsive; no physical
unplug/replug was needed at any point in this plan.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **RIG-01 is complete.** All three AVR targets (`uno`, `uno328pb`, `leonardo`) now have a
  proven, on-device, independent-read-back flash-provenance chain, and all three have had their
  wrong-arm detector observed FIRING for real (D-03 complete across all three).
- `rig-pins.json`'s `targets.leonardo` now carries the measured bootloader-entry behaviour
  `PROCEDURE.md` step `P-04` needs for every later cell on this board (waves 161–163's Leonardo
  cells, including `A3/B2`, the milestone's reference-rig comparison cell).
- Remaining Phase 160 work per `STATE.md`: waves 8–10 (plans 11–13) — arms-provenance capture,
  the fresh-context record-reconstruction falsification (RIG-05), and phase close-out. This
  plan does not touch chip operations at all; the seated W27C512 remains untouched and ready
  for plan 12's chip-level work.
- **SAFETY note for the next session:** the Leonardo remains attached with a shield mounted and
  a W27C512 seated — this board is exempt from the chip-out rule, so it is safe to continue
  driving without any chip-removal step, unlike the uno-class boards used in plans 08/09.

---
*Phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur*
*Completed: 2026-08-27*

## Self-Check: PASSED

All 13 declared files verified present on disk (probe.json, BOOTLOADER-WINDOW.md,
READBACK-VERDICT.json ×2, flash_readback.bin, SHA256SUMS.txt, CROSSFLASH.md, rig-pins.json,
EVIDENCE.jsonl, EVIDENCE.md, probe_board.py, judge_readback.py, REQUIREMENTS.md). Both task
commits (`8ddc06c8`, `ac300700`) verified present in `git log --oneline --all`.
