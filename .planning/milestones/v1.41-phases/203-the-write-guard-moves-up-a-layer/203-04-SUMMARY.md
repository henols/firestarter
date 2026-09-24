---
phase: 203-the-write-guard-moves-up-a-layer
plan: 04
subsystem: host-write-path
tags: [python, click, docstring, syrupy, snapshots, honesty, session-cost]

requires:
  - phase: 203-01
    provides: "write_blank_guard.py: GUARDED_PROTOCOL_IDS, NAMED_EXEMPT_PROTOCOL_IDS, SRAM_PROTOCOL_IDS -- the exact unguarded-family list this plan's help text names"
  - phase: 203-03
    provides: "--verify/--full CLI options and their exit-code help text (D-13), and the two designated known-red snapshots this plan closes"
  - phase: 202-one-comparison-engine-on-the-host
    provides: "202-READ-ABORT-ANSWER.md's bounded per-abort cost, cited as the abort term in 203-SESSION-COST.md"
provides:
  - "A truthful write --help: the pre-write blank check is attributed to the host, and all four unguarded families (0x0D 28C parallel, 0x05 flash4, SRAM, FRAM) are named"
  - "Both write --help syrupy snapshot blocks (test_help_write, test_no_blank_check_polarity) hand-edited to match, byte-identical to each other, green from a clean run"
  - "203-SESSION-COST.md: the added wall-clock of the guard read and the --verify read-back, as an explicit derivation over three cited prior measurements, with a stated non-measurement sentence"
  - ".planning/WINDOWS.md entry 2 flipped from open to fixed, with reason and resolved_at"
affects: [206-session-lease, 207-wiki-documentation]

actuals:
  tokens: 5786
  tasks: 3
  commits: 3
  plan_head_before: "firestarter_app 161ced2 (2 commits) + meta 102cfa39 (1 commit)"

tech-stack:
  added: []
  patterns:
    - "Snapshot hand-edit via syrupy's own AmberDataSerializer (read-only formatting call, not --snapshot-update) to get byte-exact expected text before splicing it into the .ambr file by hand"
    - "Session-cost derivation with a provenance table: every number traced to exactly one cited artifact, with an explicit non-measurement sentence separating derived arithmetic from bench fact"

key-files:
  created:
    - .planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - .planning/WINDOWS.md

key-decisions:
  - "Used syrupy's AmberDataSerializer.serialize() directly (a read-only formatting call on the captured `write --help` stdout) to get byte-exact expected snapshot text, then spliced it into both .ambr blocks by hand with a Python script performing exact line-range replacement. This is not --snapshot-update -- no pytest snapshot-update mechanism was invoked at any point, and the resulting text was reviewed (diffed against the old block, and the two new blocks diffed against each other) before being written. Chosen over freehand rewrapping to eliminate whitespace/wrap-boundary transcription errors on a 51-line Click-wrapped block."
  - "Did not run gsd_run query requirements.mark-complete for WRITE-03/WRITE-04, and did not hand-edit REQUIREMENTS.md. 203-CONTEXT.md's Mechanics section states REQUIREMENTS.md and ROADMAP.md are hand-authored for this milestone specifically because the GSD requirements/roadmap verbs normalise whole files, and plan 02's summary already deliberately left WRITE-03 unmarked for the same reason (it is shared with this plan). This plan's own instructions restrict it from touching STATE.md/ROADMAP.md; REQUIREMENTS.md is left for the orchestrator to reconcile by hand, consistent with plan 02's precedent."
  - "WINDOWS.md entry 2's `reason` field was filled by a direct hand-edit, not through `gsd-tools windows fixed`, because that verb's `cmdWindowsMarkFixed` only accepts one positional argument (the id) and has no reason parameter -- confirmed by reading its implementation. The `fixed` status and `resolved_at` timestamp were set by the verb first; the `reason` text was then added by hand in both the Markdown table row and the JSON block, keeping the two in sync."

requirements-completed: [WRITE-03, WRITE-04]

coverage:
  - id: D1
    description: "write --help attributes the pre-write blank check to the host (not the firmware) and names all four unguarded families -- 0x0D (28C parallel), 0x05 (flash4), and SRAM and FRAM -- completely, with the old false 'effective on every other protocol' clause removed (WRITE-03)."
    requirement: WRITE-03
    verification:
      - kind: other
        ref: ".venv311/bin/firestarter write --help (captured stdout, inspected)"
        status: pass
      - kind: other
        ref: "python -c regex scan for planning vocabulary (WRITE-\\d, D-\\d\\d, phase 20\\d, .planning) over the help output -- none found"
        status: pass
      - kind: unit
        ref: "tests/test_characterization.py::test_help_write"
        status: pass
    human_judgment: false
  - id: D2
    description: "--verify and --full remain documented with the full 0/1/2 exit-code contract and the 'plain write is unchanged' statement (WRITE-04, D-13) -- unaffected by this plan's edit, and reconfirmed by the same snapshot that now also pins the rewritten paragraph."
    requirement: WRITE-04
    verification:
      - kind: unit
        ref: "tests/test_characterization.py::test_help_write"
        status: pass
      - kind: unit
        ref: "tests/test_characterization.py::test_no_blank_check_polarity"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both write --help snapshot blocks (test_help_write, test_no_blank_check_polarity) are hand-edited, byte-identical to each other, and green from a clean run -- no --snapshot-update was ever invoked."
    verification:
      - kind: unit
        ref: "tests/test_characterization.py::test_help_write"
        status: pass
      - kind: unit
        ref: "tests/test_characterization.py::test_no_blank_check_polarity"
        status: pass
      - kind: other
        ref: "diff of the two extracted .ambr bodies (lines 364-439 vs 1419-1494) -- IDENTICAL"
        status: pass
      - kind: other
        ref: "git diff --stat -- tests/__snapshots__/test_characterization.ambr, hunks confined to the two write --help blocks"
        status: pass
    human_judgment: false
  - id: D4
    description: "203-SESSION-COST.md records the added wall-clock of the guard read and the --verify read-back as an explicit derivation with visible provenance -- per-board-class connect medians (176-MEASUREMENT.md), the bounded per-abort cost (202-READ-ABORT-ANSWER.md), the single-sample read-rate figure with its own caveat quoted (dev-test-sequence-cost-model.md), an explicit statement that Phase 203 took no new hardware measurement, and a provenance table with one row per term (D-17)."
    requirement: WRITE-04
    verification:
      - kind: other
        ref: "grep -qiE '176-MEASUREMENT' 203-SESSION-COST.md"
        status: pass
      - kind: other
        ref: "grep -qiE '202-READ-ABORT-ANSWER' 203-SESSION-COST.md"
        status: pass
      - kind: other
        ref: "grep -qiE 'dev-test-sequence-cost-model' 203-SESSION-COST.md"
        status: pass
      - kind: other
        ref: "grep -qiE 'no new hardware measurement' 203-SESSION-COST.md"
        status: pass
    human_judgment: false

duration: "~50 min (approximate -- PLAN_START_TIME was not captured at session start; see Deviations)"
completed: 2026-09-21
status: complete
---

# Phase 203 Plan 04: The Write Help Text Tells the Truth Summary

**Rewrote the `write` docstring's blank-check paragraph to attribute the check to the host and name all four unguarded families, hand-edited both byte-identical `write --help` syrupy snapshots (never `--snapshot-update`), and recorded the phase's added wall-clock in `203-SESSION-COST.md` as an explicit, cited derivation rather than a fabricated measurement.**

## Performance

- **Duration:** ~50 min (approximate)
- **Completed:** 2026-09-21T13:59:43Z
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 3 (2 in `firestarter_app`, 1 in the meta repo) + 1 file created

## Accomplishments

- `write`'s docstring no longer claims the bypass flag (`-b`) "remains effective on every other
  protocol" -- a sentence this phase's own predecessor plans made false, since `-b` is now also a
  no-op on the SRAM/FRAM families. The rewritten paragraph attributes the pre-write blank check to
  the host (not the firmware) and names all four unguarded families by name: `0x0D` (28C parallel),
  `0x05` (flash4), and SRAM and FRAM.
- Confirmed, by direct read of the surrounding docstring, that no other sentence attributes the
  blank check to the firmware and that `--verify`/`--full`'s help text (landed in plan 03) already
  states the full 0/1/2 exit-code contract and the "plain write is unchanged" clause truthfully --
  nothing in that text needed to change.
- Both `write --help` syrupy snapshot blocks (`test_help_write`, `test_no_blank_check_polarity`,
  `tests/__snapshots__/test_characterization.ambr`) were hand-edited to the real output: captured
  via the installed console script (`.venv311/bin/firestarter write --help` -- `python -m
  firestarter` still fails with no `__main__.py`, the same pre-existing gap 203-03 documented),
  formatted with syrupy's own `AmberDataSerializer.serialize()` (a read-only call, not
  `--snapshot-update`), and spliced into both blocks by an exact line-range replacement. Both
  extracted bodies re-diffed byte-identical to each other after the edit; `git diff --stat` on the
  `.ambr` file shows hunks confined to the two `write --help` blocks only.
- `203-SESSION-COST.md` records the phase's added wall-clock (one extra port open for a guarded
  plain `write`, two for a guarded `write --verify`) as an explicit derivation: the per-board-class
  connect medians from `176-MEASUREMENT.md` (Uno 2.518s, Leonardo 2.607s, N=10 each), the bounded
  per-abort cost from `202-READ-ABORT-ANSWER.md` (up to 1.000s), and the single-sample,
  one-protocol read-rate figure from `dev-test-sequence-cost-model.md`, quoted together with that
  note's own caveat. An explicit sentence states Phase 203 took no new hardware measurement and why
  (the phase is bench-no and the in-repo connect-cost harness needs a real board to produce a
  number). A provenance table closes the document, one row per term.
- `.planning/WINDOWS.md` entry 2 (the two known-red snapshots) is flipped from `open` to `fixed`,
  with `resolved_at` and a `reason` recording the test counts.

## Task Commits

Each task was committed atomically, in the repository its files live in:

1. **Task 1: The write help text describes the host policy** -- `460785e` (docs, `firestarter_app`)
2. **Task 2: Hand-edit both help snapshots -- one diff, applied twice** -- `7e63638` (test, `firestarter_app`)
3. **Task 3: Record the session cost as a derivation, with its provenance visible** -- `6cec0a90` (docs, meta repo -- also carries the WINDOWS.md fix)

**Plan metadata:** this commit, in the meta repo (docs(203-04): plan summary), created after this file.

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` -- rewrote the `write` docstring's blank-check
  paragraph (Task 1). No other line in the file changed.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` -- both `write --help` bodies
  (`test_help_write` lines 364-439, `test_no_blank_check_polarity` lines 1419-1494) replaced with
  the real, current `write --help` output (Task 2).
- `.planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md` -- new artifact,
  the D-17 session-cost derivation (Task 3).
- `.planning/WINDOWS.md` -- entry 2's `status`, `resolved_at`, and `reason` fields (Task 3, folded
  into the same commit).

## Decisions Made

See `key-decisions` in the frontmatter for full rationale. In short: the snapshot hand-edit used
syrupy's own serializer as a read-only formatting aid (not `--snapshot-update`) to eliminate manual
transcription risk on a 51-line, Click-wrapped block; `REQUIREMENTS.md` was deliberately left
untouched, consistent with 203-CONTEXT.md's "hand-authored for this milestone" note and plan 02's
own precedent for the same shared `WRITE-03` ID; and `WINDOWS.md`'s `reason` field was filled by a
direct hand-edit after `gsd-tools windows fixed` (which has no reason parameter) set the `fixed`
status and timestamp.

## Deviations from Plan

### Process Deviations (not code)

**1. [Process] `PLAN_START_TIME` was not captured at session start**
- **Found during:** writing this summary's Performance section
- **Issue:** `execute-plan.md`'s `record_start_time` step calls for capturing a start timestamp
  before work begins; this session did not run that step explicitly (mirroring the same process
  deviation plan 03 recorded).
- **Impact:** The Duration figure above is an approximation derived from the first commit's
  timestamp and the surrounding read/edit/test sequence, not a measured
  `PLAN_START_EPOCH`/`PLAN_END_EPOCH` delta.
- **Not auto-fixed:** cannot be reconstructed retroactively with precision; stated as approximate
  rather than presented as exact.

**2. [Process] `python -m firestarter write --help` does not run (pre-existing, not this plan's cause)**
- **Found during:** Task 1 verification
- **Issue:** Same gap 203-03 documented: the package carries no `firestarter/__main__.py`, so
  `python -m firestarter` fails regardless of this plan's changes. Worked around by using the
  installed console script (`.venv311/bin/firestarter`), which exercises the identical Click
  command object.
- **Not fixed:** out of this plan's scope (its `files_modified` does not include `__main__.py`,
  and no requirement asks for it); already filed as a candidate follow-up by 203-03.

---

**Total deviations:** 0 code auto-fixes, 2 process deviations (neither affecting the correctness or
completeness of the delivered artifacts; both self-caught and documented).
**Impact on plan:** None. Both process deviations are transparency notes, not scope or correctness
gaps.

## Issues Encountered

None beyond the two process deviations above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Phase 203 is now complete: all four plans (guard predicate, pinning/negative-address/bypass
  flags, `write --verify`, and this plan's help-text/snapshot/session-cost close-out) are committed
  and summarized.
- `203-SESSION-COST.md` is ready for Phase 206's SESS-01/SESS-02: the before-figure is a cited
  derivation, not a fabricated measurement, with its error bar explicitly identified as the
  single-sample read term (not the connect term, which is a real ten-sample measurement).
- `REQUIREMENTS.md`'s `WRITE-02`/`WRITE-03`/`WRITE-04` entries remain unmarked in the hand-authored
  file itself (per 203-CONTEXT.md's Mechanics note); the orchestrator or a follow-up hand-edit
  should reconcile them against this plan's and plan 02's `requirements-completed` frontmatter.
- No blockers. `firestarter_fw/` was not touched -- confirmed clean via `git status --short` inside
  that submodule.
- Still on branch `v1.41-verification-to-host` in both `firestarter_app` and the meta repo,
  confirmed after every commit.

## Self-Check: PASSED

- `firestarter_app/firestarter/cli_handlers.py` -- FOUND, modified
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` -- FOUND, modified
- `.planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md` -- FOUND, created
- `.planning/WINDOWS.md` -- FOUND, modified
- Commit `460785e` -- FOUND in `firestarter_app`'s `git log --oneline --all`
- Commit `7e63638` -- FOUND in `firestarter_app`'s `git log --oneline --all`
- Commit `6cec0a90` -- FOUND in the meta repo's `git log --oneline --all`
- `git -C firestarter_app status --porcelain` shows only the pre-existing, unrelated untracked
  `datasheets/LST62832I.pdf`.
- `git status --porcelain` (meta, scoped to this plan's paths) is clean.
- `firestarter_app` branch: `v1.41-verification-to-host`; meta branch: `v1.41-verification-to-host`
  (verified after every commit).
- `tests/test_characterization.py`: 38 passed, 36/36 snapshots passing.
- Full suite: **2304 passed, 0 failed, 36/36 snapshots passing** -- matches the wave-4 target
  exactly (baseline after wave 3 was 2302 passed / 2 known-red).
- Coverage: 86.16% (floor 70%); `write_blank_guard.py` at 100%.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`: both clean.
- `mypy firestarter/cli_handlers.py`: clean (strict module).
- `.ambr` diff: `git diff --stat` shows 60 changed lines across exactly the two `write --help`
  blocks (hunks at 371/391/417 and 1426/1446/1472); no other snapshot touched.
- Both extracted `write --help` bodies (364-439, 1419-1494) diffed byte-identical to each other.
- No snapshot-update command appears anywhere in this session's shell history.
- `.planning/WINDOWS.md`: entry 2 `status: fixed`, `resolved_at` set, `reason` filled.
- `firestarter_fw/`: `git status --short` clean -- no file under it modified.

---
*Phase: 203-the-write-guard-moves-up-a-layer*
*Completed: 2026-09-21*
