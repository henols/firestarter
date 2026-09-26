---
phase: 124-firmware-integration-merge
plan: 02
subsystem: firmware-ci
tags: [firestarter, python, pytest, checker, merge-gate, size-baseline]

# Dependency graph
requires:
  - phase: 123-non-regression-baselines-gate-hardening
    provides: "scripts/baseline/size_baseline.json (BASE-01 recorded truth) and scripts/check_size_baseline.py's strict-equality comparator + env-seam + never-vacuous-guard shape that this plan extends without altering."
provides:
  - "firestarter/scripts/baseline/size_baseline_base01.json — an immutable, byte-identical freeze of the live BASE-01 baseline (shared blob SHA b940c91655600a57ad7ef67cba723943af929daf), so Plan 124-10's re-baseline of size_baseline.json cannot silently move MERGE-05's judged reference point"
  - "firestarter/scripts/check_size_baseline.py --policy merge05 — MERGE05_UNO_CLASS_FLASH_BAND=64 constant + compare_avr_policy_merge05(): Leonardo flash must not grow, Uno-class flash growth <= 64 B, RAM unchanged on all three envs — MERGE-05's first-ever exit code"
  - "5 new tests in tests/test_check_size_baseline.py: pre-landing proof the band passes on RESEARCH's measured post-landing deltas, three planted-violation FAILs (uno +65, leonardo +1, RAM +1), and a regression pin proving default mode is textually unchanged"
affects: [124-10, 124-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "One-shot policy assertion (--policy VALUE) layered onto an existing strict-equality checker via a fifth _parse_argv tuple element, rather than a separate script — the default (policy=None) path is provably byte-identical in output"
    - "A frozen baseline copy (size_baseline_base01.json) coexists with the live baseline (size_baseline.json) specifically so a later re-baseline plan cannot move an earlier plan's judged reference point; proven with git hash-object rather than a path-scoped git diff"

key-files:
  created:
    - firestarter/scripts/baseline/size_baseline_base01.json
    - firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved.log
  modified:
    - firestarter/scripts/check_size_baseline.py
    - firestarter/tests/test_check_size_baseline.py

key-decisions:
  - "Per-env band literal: leonardo's effective band is 0 (must-not-grow), uno/uno328pb's is MERGE05_UNO_CLASS_FLASH_BAND=64 — implemented as `band = 0 if env == \"leonardo\" else MERGE05_UNO_CLASS_FLASH_BAND` inside compare_avr_policy_merge05, so the single constant still governs the uno-class rule while leonardo's stricter rule is expressed without a second magic number."
  - "PASS-line delta annotation is computed in main() (not returned by the compare function), reusing the same rec/band values already available there — keeps compare_avr_policy_merge05's return shape identical to compare_avr's (list of failure strings only)."
  - "grep -c 'shell=True' tests/test_check_size_baseline.py returns 2, not the plan's expected 0 — both occurrences are Phase-123-authored docstring prose (\"never shell=True\") that predates this plan and that this plan's Task 3 edits did not add to. Documented rather than mangled; see Deviations below."

requirements-completed: [MERGE-05]

coverage:
  - id: D1
    description: "BASE-01 frozen byte-identically as size_baseline_base01.json, blob SHA recorded and mechanically proven equal to the live baseline"
    requirement: "MERGE-05"
    verification:
      - kind: unit
        ref: "git hash-object scripts/baseline/size_baseline.json == git hash-object scripts/baseline/size_baseline_base01.json (both b940c91655600a57ad7ef67cba723943af929daf)"
        status: pass
    human_judgment: false
  - id: D2
    description: "--policy merge05 band mode added to check_size_baseline.py; default (no --policy) mode textually unchanged"
    requirement: "MERGE-05"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py#test_default_mode_is_unchanged_by_the_new_flag"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py#test_policy_merge05_permits_the_measured_landing_deltas"
        status: pass
    human_judgment: false
  - id: D3
    description: "Band comparator proven to FAIL on three distinct planted violations: +65 B uno-class flash, +1 B Leonardo flash, +1 B RAM move"
    requirement: "MERGE-05"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py#test_policy_merge05_fires_on_uno_class_over_band"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py#test_policy_merge05_fires_on_leonardo_growth"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_check_size_baseline.py#test_policy_merge05_fires_on_ram_move"
        status: pass
    human_judgment: false

duration: ~10min
completed: 2026-07-31
status: complete
---

# Phase 124 Plan 02: MERGE-05 Band Comparator + Frozen BASE-01 Summary

**Added `--policy merge05` to `check_size_baseline.py` (Leonardo no-growth / Uno-class <=64 B / RAM-unchanged band, exit-coded for the first time) and froze `size_baseline.json` byte-identically as `size_baseline_base01.json` so Plan 124-10's re-baseline can never move MERGE-05's reference point.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-07-31T08:15:37Z (STATE.md `last_updated` at hand-off from Plan 01)
- **Completed:** 2026-07-31T08:24:51Z
- **Tasks:** 3 completed
- **Files modified:** 6 (5 created, 1 modified — `check_size_baseline.py` counted separately from the 4 new files + `test_check_size_baseline.py`)

## Accomplishments

- `firestarter/scripts/baseline/size_baseline_base01.json` — byte-identical freeze of the live BASE-01 baseline, proven via `git hash-object` (both files hash to `b940c91655600a57ad7ef67cba723943af929daf`), `wc -c` (5423 bytes each), and a Python `json.load` equality check — never a path-scoped `git diff`.
- `check_size_baseline.py` gained `--policy merge05`: `MERGE05_UNO_CLASS_FLASH_BAND = 64` is the single place the band literal lives; `compare_avr_policy_merge05()` enforces Leonardo flash `<=` baseline (no growth), Uno/uno328pb flash `<=` baseline+64, and RAM equality + total-unchanged on all three, reusing `compare_avr`'s existing "board or framework moved" message text for the total checks.
- Default (no `--policy`) mode is provably unchanged: the PASS line for `uno=captured_build_uno.log` is textually identical before and after the change (`PASS: uno(flash=23932/32256,ram=1573/2048)`), and a new regression test pins that the default output never contains the band-mode `<=64` substring.
- Three planted violations, each a single-figure edit of a captured log, each proven to flip the checker to a non-zero exit naming the computed delta: `planted_size_baseline_policy_uno_over_band.log` (+65 B, exceeds the 64 B band), `planted_size_baseline_policy_leonardo_growth.log` (+1 B, Leonardo must not grow at all), `planted_size_baseline_policy_ram_moved.log` (+1 B RAM, equality holds under the band mode too).
- A pre-landing proof (`test_policy_merge05_permits_the_measured_landing_deltas`) synthesizes RESEARCH's measured post-landing figures (Leonardo -56, Uno +22, uno328pb +28, RAM unchanged) in `tmp_path` copies of the captured logs and asserts `--policy merge05 --baseline scripts/baseline/size_baseline_base01.json` exits 0 on them — before the actual landing happens.

## Observed Verification Values

- **BASE-01 shared blob SHA:** `b940c91655600a57ad7ef67cba723943af929daf` (both `scripts/baseline/size_baseline.json` and `scripts/baseline/size_baseline_base01.json`).
- **Default-mode PASS line, before this plan's edits:** `PASS: uno(flash=23932/32256,ram=1573/2048)`
- **Default-mode PASS line, after this plan's edits:** `PASS: uno(flash=23932/32256,ram=1573/2048)` — byte-identical.
- **`--policy merge05` PASS line (uno, delta 0):** `PASS: uno(flash=23932/32256[+0<=64],ram=1573/2048[=])` — contains the literal `[+0<=64]` required by the plan's acceptance criteria.
- **`--policy merge05` PASS line (leonardo, canonical MERGE-05 invocation against the real captured log):** `PASS: leonardo(flash=26072/28672[+0<=0],ram=2014/2560[=])`
- **`--policy bogus`:** exit 2, `ERROR: unrecognized --policy value: 'bogus' (only 'merge05' is recognised)` on stderr.
- **`--policy merge05` with no logs, no `--rebuild`:** exit 1, the same never-vacuous message as default mode (guard is not bypassed by the new flag).
- **Planted uno-over-band FAIL:** `uno: flash_used baseline=23932 observed=23997 delta=+65 exceeds MERGE-05 uno-class band of 64 B`
- **Planted leonardo-growth FAIL:** `leonardo: flash_used baseline=26072 observed=26073 delta=+1 exceeds MERGE-05 leonardo band of 0 B`
- **Planted ram-moved FAIL:** `uno: ram_used baseline=1573 observed=1574 delta=+1 (MERGE-05 requires ram_used unchanged)`
- **`grep -c 'MERGE05_UNO_CLASS_FLASH_BAND' scripts/check_size_baseline.py`:** 4 (constant definition + comment + 2 uses; `>= 2` required).
- **`grep -c 'import argparse' scripts/check_size_baseline.py`:** 0.
- **`pytest tests/test_check_size_baseline.py -q`:** 7 -> **12 passed** (+5, matching the plan's stated expectation).
- **`pytest tests/ -q` new total:** 55 -> **60 passed**, 0 failed (replacing the 124-01-recorded 55).
- **`pytest tests/test_checker_convention.py -q`:** 7 passed, 0 failed — unaffected; `FIXTURE_FLOOR=10` stays satisfied (13 `planted_*` entries now present, `ls tests/fixtures/ | grep -c '^planted_size_baseline_policy_'` = 3).
- **`git diff --name-only bc0ba55 HEAD` (this plan's full diff against the 124-01 tip):** exactly the plan's 6 named paths, no file under `src/`, `include/`, `test/`, `platformio.ini`, or `.github/`.

## Task Commits

Each task was committed atomically, inside the `firestarter` submodule (`/workspaces/firestarter`) on branch `v1.23-py32f071-integration`:

1. **Task 1: Freeze BASE-01 byte-identically and record its blob SHA** - `609d6a7` (feat)
2. **Task 2: Add --policy merge05 band mode to check_size_baseline.py** - `1e8c0cc` (feat)
3. **Task 3: Plant three band violations and extend the paired pytest** - `17c7614` (test)

_No plan-metadata commit is made inside the submodule — the meta-repo's own SUMMARY.md commit (below) is this plan's final commit._

## Files Created/Modified

- `firestarter/scripts/baseline/size_baseline_base01.json` - frozen, byte-identical BASE-01 record
- `firestarter/scripts/check_size_baseline.py` - `--policy merge05` band mode + `MERGE05_UNO_CLASS_FLASH_BAND` constant + `compare_avr_policy_merge05()` + docstring rewrite
- `firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band.log` - planted +65 B Uno-class flash violation
- `firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth.log` - planted +1 B Leonardo flash violation
- `firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved.log` - planted +1 B RAM violation
- `firestarter/tests/test_check_size_baseline.py` - 5 new tests + extended Coverage/provenance docstring blocks

## Decisions Made

- **Per-env band, single named constant:** `MERGE05_UNO_CLASS_FLASH_BAND = 64` governs uno/uno328pb; leonardo's stricter must-not-grow rule uses a locally-computed `band = 0`, so there is exactly one named magic number in the module (satisfying the plan's "the band literal appears exactly once, in the constant" instruction) while leonardo's rule is still expressed without inventing a second constant.
- **PASS-line delta annotation computed in `main()`:** kept `compare_avr_policy_merge05()`'s return shape identical to `compare_avr`'s (failure-strings-only), matching the plan's explicit instruction; the enriched `[delta<=band]`/`[=]` PASS formatting is assembled in `main()` where `baseline` and `env` are already in scope.
- **`grep -c 'shell=True' tests/test_check_size_baseline.py` returns 2, not the plan's stated 0** — both occurrences are Phase-123-authored docstring prose ("never `shell=True`", "as a real subprocess (list argv, never shell=True)") that predates this plan and was not touched or added to by Task 3's edits. Verified via `git log -p --follow` that both lines existed before this plan started. This is a plan-authoring acceptance-criterion imprecision (the literal substring search matches legitimate negation-prose, the same class of issue as 124-01's Deviation #3 "self-matching string assertion"), not a functional defect — no actual `subprocess.run(..., shell=True)` call exists anywhere in the module, confirmed by the full passing test suite and by manual inspection of both hit lines. Left as-is rather than mangling accurate, useful docstring prose to force a substring count to zero.

## Deviations from Plan

### Auto-fixed Issues

None — no bugs, missing functionality, or blocking issues were found during execution; the plan's own action text and acceptance criteria were followed directly.

### Documented Discrepancies (not auto-fixed — pre-existing, out of Task 3's scope)

**1. `grep -c 'shell=True' tests/test_check_size_baseline.py` acceptance criterion cannot be satisfied by 0** — see "Decisions Made" above for full analysis. Not fixed because the two occurrences are legitimate pre-existing docstring prose from Phase 123, not code introduced by this plan's Task 3, and rewriting accurate documentation solely to defeat a literal grep count would be a documentation quality regression for no functional benefit. The actual invariant (no real `shell=True` usage) holds and is proven by the full green test suite.

---

**Total deviations:** 0 auto-fixed; 1 documented discrepancy (pre-existing acceptance-criterion imprecision, not a code defect).
**Impact on plan:** None on scope or correctness — all three tasks' actual acceptance criteria that test real behavior (exit codes, PASS/FAIL text, deltas, byte-identity, default-mode regression) pass. Only a textual-substring criterion that self-matches legitimate prose is unsatisfiable as literally worded.

## Issues Encountered

None beyond the documented discrepancy above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- MERGE-05 has an exit code for the first time in this milestone: `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log leonardo=<log> --avr-log uno=<log> --avr-log uno328pb=<log>` is the canonical invocation Plan 124-10 (or whichever plan lands the real merge) must run against the actual landed tree's build logs.
- BASE-01 is frozen and immutable at `scripts/baseline/size_baseline_base01.json` (blob SHA `b940c91655600a57ad7ef67cba723943af929daf`) — Plan 124-10's rewrite of `scripts/baseline/size_baseline.json` to post-landing figures will not move MERGE-05's reference point.
- The band is proven to pass on the exact RESEARCH-measured post-landing deltas (Leonardo -56, Uno +22, uno328pb +28, RAM unchanged) — when the real landing happens and produces these exact figures (or better), `--policy merge05` will exit 0 against the frozen baseline without further changes to this checker.
- Full firmware pytest suite is green: 60 passed, 0 failed, 0 skipped. No Phase-123 test arm regressed (`test_checker_convention.py` unaffected, `FIXTURE_FLOOR=10` satisfied at 13 entries).
- No blockers for the rest of Phase 124. `124-NONREGRESSION.md` (a later plan's artifact) should re-record 60 as the running total, up from 124-01's recorded 55.

## Self-Check: PASSED

- FOUND: `firestarter/scripts/baseline/size_baseline_base01.json`
- FOUND: `firestarter/scripts/check_size_baseline.py` (modified)
- FOUND: `firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band.log`
- FOUND: `firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth.log`
- FOUND: `firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved.log`
- FOUND: `firestarter/tests/test_check_size_baseline.py` (modified)
- FOUND commit `609d6a7` (firestarter submodule)
- FOUND commit `1e8c0cc` (firestarter submodule)
- FOUND commit `17c7614` (firestarter submodule)

---
*Phase: 124-firmware-integration-merge*
*Completed: 2026-07-31*
