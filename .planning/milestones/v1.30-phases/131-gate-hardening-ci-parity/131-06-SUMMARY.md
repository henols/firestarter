---
phase: 131-gate-hardening-ci-parity
plan: 06
subsystem: testing
tags: [ci, shell, gate-hardening, mypy, ruff, pytest, board-stamp]

# Dependency graph
requires:
  - phase: 131-02
    provides: "check_mypy_watermark.py's paired pytest suite, run as part of the whole tests/ suite by legs 1/2"
  - phase: 131-03
    provides: "the 43/41/84 anti-narrowing SDP partition gate, run as part of the whole tests/ suite by legs 1/2"
  - phase: 131-04
    provides: "the derived-subset GATE-10 leg, run as part of the whole tests/ suite by legs 1/2"
provides:
  - "firestarter_app/tools/ci_parity.sh: a runnable, four-leg, location-anchored CI-parity recipe every later v1.30 phase reuses as an acceptance leg"
  - "131-CI-PARITY.md: one recorded no-board run, per-leg exit codes, the D-10 check_no_exists_proxy.py one-time confirmation, and the D-17/D-18 record-only corrections"
affects: [132-mypy-watermark-and-error-fixes, 133, 134, 136, 137-close-honesty-ledger]

tech-stack:
  added: []
  patterns:
    - "Location-anchored batch shell recipe with no early-abort mode -- every leg's exit code is captured, printed, and aggregated at the end, never short-circuited"
    - "Board-attached evidence metadata (a plain /dev glob, never opening a port) stamped into a script's final summary rather than gating on physical hardware state"

key-files:
  created:
    - firestarter_app/tools/ci_parity.sh
    - .planning/phases/131-gate-hardening-ci-parity/131-CI-PARITY.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Two literal-string collisions with this plan's own acceptance grep checks, both fixed by describing the checker/command by role instead of repeating its exact banned substring: the header's mention of tools/check_no_exists_proxy.py (which the acceptance criteria forbid appearing anywhere in the script) was reworded to name it only by role plus a pointer to 131-CI-PARITY.md; the leg-3 banner's duplicate literal 'ruff check firestarter/ tests/' / 'ruff format --check firestarter/ tests/' text (which the acceptance criteria require to appear exactly once each) was reworded to a role description so only the real command lines carry the literal strings."
  - "The closing line of 131-CI-PARITY.md originally read '...gh workflow run...' in prose describing what was NOT run this plan -- tripped the same-named acceptance grep (grep -c 'gh workflow run' must equal 0) that exists to catch an actual dispatch invocation, not a negation sentence. Reworded to 'remote CI dispatch' to preserve the same true claim without the literal banned string."

requirements-completed: [GATE-09]

coverage:
  - id: D1
    description: "tools/ci_parity.sh exists, is executable (100755), is anchored to its own location (proven identical output from /tmp and from the repo root), never aborts early, and prints four per-leg exit codes plus an aggregate CI-PARITY: PASS/FAIL line"
    requirement: "GATE-09"
    verification:
      - kind: other
        ref: "manual dual run: bash /workspaces/firestarter_app/tools/ci_parity.sh (from /tmp) and bash tools/ci_parity.sh (from the repo root) -- both produced identical leg banners, leg exit codes (0,0,0,2), BOARD-ATTACHED: none, and aggregate CI-PARITY: FAIL (legs:4)"
        status: pass
    human_judgment: false
  - id: D2
    description: "One recorded run with BOARD-ATTACHED: none, per-leg exit codes, and leg 4's exit 2 explained as the hardened Phase 131 gate working, not a script defect -- with an explicit statement that firestarter_app's primary ci job stays RED until Phase 132"
    requirement: "GATE-09"
    verification:
      - kind: other
        ref: "131-CI-PARITY.md, recorded transcript and per-leg table"
        status: pass
    human_judgment: false
  - id: D3
    description: "check_no_exists_proxy.py run once as a recorded one-time confirmation (D-10), not a recipe leg -- PASS, exit 0, names the 131-02-added test_check_mypy_watermark.py among 79 scanned files"
    verification:
      - kind: other
        ref: "python3 tools/check_no_exists_proxy.py; echo $? -- PASS: scanned 79 file(s)..., EXIT: 0 (transcript in 131-CI-PARITY.md)"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-17 and D-18 recorded as corrections to the research record, not acted on; D-18's negative criterion (any test this phase added must pass under recipe leg 1) discharged mechanically by leg 1's own run"
    verification:
      - kind: other
        ref: "131-CI-PARITY.md D-17/D-18 sections; leg 1 transcript shows the three 131-02/03/04 modules passing under the empty-sibling-root condition"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-03
status: complete
---

# Phase 131 Plan 06: CI-Parity Recipe Summary

**`firestarter_app/tools/ci_parity.sh` runs four labelled legs (pytest with an empty firmware sibling, pytest with the sibling present, CI-scoped ruff, and the hardened mypy watermark gate), never aborts early, prints per-leg exit codes plus a BOARD-ATTACHED stamp, and one recorded no-board run shows legs 1-3 green and leg 4 exiting 2 -- the Phase 131 hardened gate correctly refusing to trust a numpy-stub-truncated mypy run.**

## Performance

- **Duration:** ~50 min
- **Tasks:** 2 (Task 1: author the four-leg script; Task 2: record a no-board run + the D-10 confirmation)
- **Files modified:** 2 created (`firestarter_app/tools/ci_parity.sh`, `131-CI-PARITY.md`), 1 modified (`.planning/REQUIREMENTS.md`)

## Accomplishments

- Authored `firestarter_app/tools/ci_parity.sh` (162 lines, mode `100755`): four legs, each preceded
  by a banner naming the leg number, its command, and what it proves --
  1. `FIRESTARTER_FW_ROOT=<mktemp -d> python3 -m pytest tests/ -q` (empty sibling root, the
     standalone-CI condition -- the env var is set as a child-process-environment prefix on the
     pytest invocation itself, never monkeypatched, because `tests/fw_presence.py:80` reads it at
     module scope);
  2. `python3 -m pytest tests/ -q` (sibling present);
  3. `ruff check firestarter/ tests/` then `ruff format --check firestarter/ tests/`, CI's exact
     path set, neither wider nor narrower;
  4. `python3 tools/check_mypy_watermark.py`.
  No `set -e` (uses `set -u` only) -- every leg's `$?` is captured and printed immediately, so a
  failing leg never aborts the remaining legs or gets swallowed. Anchors on its own location via
  `dirname "${BASH_SOURCE[0]}"`, proven identical from both `/tmp` and the repo root.
- The header names every CI step this recipe deliberately does not mirror (the two codegen-drift
  gates, the vector-catalog check, pytest's `--cov-fail-under=70` coverage gate, the entry-point
  smoke test, and the separate isolated `ci-py32` job), states why the house module-level
  absence-proxy lint checker is not a fifth leg (D-10 -- covered by its own paired pytest, which
  legs 1-2 already run), and states the leg-4 expected-local-exit-2 shape so a future reader does
  not "fix" it.
- **Board stamp (D-09):** enumerates `/dev/ttyACM*`/`/dev/ttyUSB*` with a plain glob (never opens a
  port) and prints `BOARD-ATTACHED: <list>` or `BOARD-ATTACHED: none` into the final summary.
- **Recorded one run with no board attached**, from both a foreign working directory and the repo
  root -- both produced identical results: leg 1 exit 0 (38 firmware-dependent tests correctly
  skipped under the empty sibling root), leg 2 exit 0 (same tests run, sibling present), leg 3
  exit 0 (`ruff check` "All checks passed!", `ruff format --check` "116 files already formatted"),
  leg 4 exit 2 (the ambient numpy PEP-695 stub truncates mypy in this devcontainer; the hardened
  `classify_mypy_result` correctly refuses to trust the incomplete run). `BOARD-ATTACHED: none`.
  Aggregate script exit: 1 (`CI-PARITY: FAIL (legs:4)`) -- expected and correct per this plan's
  acceptance (a zero aggregate is not required).
- **Ran `tools/check_no_exists_proxy.py` once, separately** (D-10): `PASS: scanned 79 file(s)...`,
  exit 0, names `tests/test_check_mypy_watermark.py` (131-02's addition) among the scanned files --
  confirming its `_DEFAULT_TARGETS` registration survived. Not added as a recipe leg.
- Wrote `131-CI-PARITY.md`: per-leg table, both transcripts' summary blocks, the leg-4 explanation
  (numpy PEP-695 stub, truncated mypy run, hardened gate working, expected CI leg-4 exit 1 instead
  of 2 since CI's Python 3.11 lacks the stub), the D-10 result, and D-17/D-18 recorded as
  corrections with all their stated wrongnesses, explicitly not acted on.
- Ticked `GATE-09` (only this ID) in `.planning/REQUIREMENTS.md` with an evidence clause naming the
  script and the recorded run; updated its Traceability row to Complete.
- `git -C /workspaces/firestarter status --short` empty throughout (firmware untouched);
  `git -C /workspaces/firestarter_app diff --name-only` for this plan's two commits touches
  nothing under `.github/`.

## Task Commits

1. **Task 1: author `tools/ci_parity.sh`** -- `firestarter_app` commit `8caf77f`
   (`feat(131-06): CI-parity recipe script -- four legs, aggregate exit (GATE-09)`), on branch
   `gsd/v1.30-sdp-surface-retirement`.
2. **Task 2: record the no-board run + D-10 confirmation** -- meta repo commit `670ee7d`
   (`docs(131-06): record no-board CI-parity run, tick GATE-09`), files: `131-CI-PARITY.md`
   (created) and `.planning/REQUIREMENTS.md` (GATE-09 tick + traceability row only).

**Plan metadata:** this SUMMARY's own commit (final metadata commit, meta repo).

## Files Created/Modified

- `firestarter_app/tools/ci_parity.sh` -- created, mode `100755`. No analog existed in the repo
  (`tools/` had zero `.sh` files); the banner + trailing-summary convention was taken from
  `firestarter_test.sh:106-110,171`, the leg-aggregation logic authored fresh per D-08.
- `.planning/phases/131-gate-hardening-ci-parity/131-CI-PARITY.md` -- created. Per-leg table, both
  transcripts, the D-10/D-17/D-18 record sections.
- `.planning/REQUIREMENTS.md` -- `GATE-09` ticked with an evidence clause; its Traceability row
  updated Pending -> Complete. No other GATE line touched (verified by diff).

## Decisions Made

See `key-decisions` in frontmatter. Both are corrections to the plan's own literal text, forced by
its own acceptance-criteria greps, discovered by running the greps rather than assuming success:

- The plan's task 1 action text instructs the header comment to *name* `check_no_exists_proxy.py`
  by its file name, while its own acceptance criteria require `grep -c 'check_no_exists_proxy'
  tools/ci_parity.sh` to equal 0. These are only reconcilable by describing the checker's role
  without repeating its exact name -- the same class of self-collision 131-03's SUMMARY recorded
  for the literal string `requires_fw`. Reworded to "the house module-level absence-proxy lint
  checker (D-10, tools/, its name deliberately not repeated here -- see 131-CI-PARITY.md)".
- Similarly, the leg-3 banner text originally repeated the literal `ruff check firestarter/ tests/`
  / `ruff format --check firestarter/ tests/` strings the acceptance criteria require to appear
  **exactly once** each (so the real command line is unambiguous). Reworded the banner's
  description to "ruff lint + ruff format --check, at ci.yml's exact path set", leaving the literal
  strings to appear only on the actual command lines.
- `131-CI-PARITY.md`'s original closing line said "...gh workflow run..." in a negation sentence
  ("no X was run"), which still trips the acceptance grep meant to catch an actual dispatch
  invocation. Reworded to "remote CI dispatch" -- same true claim, no banned literal string.

## Deviations from Plan

None beyond the two literal-string-collision fixes documented above, which are mechanical
self-consistency fixes against the plan's own acceptance criteria (**[Rule 3 - Blocking]**,
analogous to 131-03's `requires_fw` fix) -- not scope changes, not architectural changes, and not
weakenings of any assertion. The script's structure, the four legs' commands, the board-stamp
mechanism, and the recorded run's content all match the plan's `<action>` text exactly.

## Issues Encountered

None beyond the acceptance-grep self-collisions above, both caught and fixed before either commit
landed.

## Known Stubs

None.

## Threat Flags

None -- this plan adds a local shell script that runs already-installed tools (`pytest`, `ruff`,
`mypy`) against the already-checked-out tree, and a documentation file. No new network endpoint,
auth path, or schema change. The plan's own `<threat_model>` T-131-34..40 rows are the ones this
plan directly discharges (see the plan's threat register); T-131-40 in particular notes the script
installs nothing.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- **GATE-09 is ticked Complete in `REQUIREMENTS.md`**, evidenced by `tools/ci_parity.sh` and the
  recorded run in `131-CI-PARITY.md`.
- **This plan set no watermark, deleted nothing, and fixed no mypy errors.**
  `firestarter_app`'s primary `ci` job is **RED before and after this plan, by design** -- leg 4's
  local exit 2 (this devcontainer's numpy-stub truncation) and CI's expected leg-4 exit 1 (the
  69-error-vs-35-watermark overage research measured) are both non-zero for different, legitimate
  reasons, and neither is a Phase 131 achievement to fix. Phase 132 owns turning it green.
- `firestarter` (firmware) remains completely untouched throughout this plan --
  `git -C /workspaces/firestarter status --short` empty, HEAD unchanged at
  `0933bd7d602efb30e4a666e8231ecf724e90ab09`.
- No push, tag, merge, remote CI dispatch, or release/publish command was run by this plan.
- `tools/ci_parity.sh` is now available as the reusable acceptance leg every later v1.30 phase
  (133/134/136/137) can invoke against its own changes before relying on a real CI dispatch.
- Remaining phase 131 plans (`131-05` GATE-07 dispatch, `131-07` close) are unaffected by this
  plan's scope and can proceed independently against the same `gsd/v1.30-sdp-surface-retirement`
  branch tip (`8caf77f`).

---
*Phase: 131-gate-hardening-ci-parity*
*Completed: 2026-08-03*

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/ci_parity.sh`
- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-CI-PARITY.md`
- FOUND: `.planning/phases/131-gate-hardening-ci-parity/131-06-SUMMARY.md`
- FOUND commit `8caf77f` (firestarter_app: CI-parity recipe script) on branch
  `gsd/v1.30-sdp-surface-retirement`
- FOUND commit `670ee7d` (meta repo: recorded run + GATE-09 tick)
- FOUND: `git -C firestarter status --short` empty (firmware untouched)
