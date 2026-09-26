---
phase: 123-non-regression-baselines-gate-hardening
plan: 06
subsystem: build-measurement-baselines
tags: [pytest, meta-test, checker-convention, native-tests, avr-size, firmware]

# Dependency graph
requires:
  - phase: 123-non-regression-baselines-gate-hardening (123-01)
    provides: fork_point_firmware SHA, size_baseline.json, tests/fixtures/ captures
  - phase: 123-non-regression-baselines-gate-hardening (123-02..05)
    provides: check_size_baseline.py, check_build_warnings.py, check_cmake_manifest.py, check_orphan_provisional.py + their paired tests/fixtures
provides:
  - firestarter/tests/test_checker_convention.py (BASE-08's convention meta-test, scoped to firestarter/scripts/)
  - the firmware-side verification record for 123-11 to cite (fresh builds, both native envs, both coarse-key gates, structural no-firmware-code-moves proof)
affects:
  - 123-11 (phase close — BASE-08 requirement ticking happens there, this plan ticks nothing)
  - Phase 124 (asserts check_cmake_manifest.py / check_orphan_provisional.py transition UNARMED -> armed)
  - any later milestone adding a firmware checker under firestarter/scripts/ (must raise FLOOR/FIXTURE_FLOOR in the same commit)

tech-stack:
  added: []
  patterns:
    - "filesystem-convention-as-truth meta-test with a hardcoded non-vacuous floor (D-08), no registry file"
    - "scope-follows-home: D-06 put every v1.23 firmware checker in firestarter/scripts/, so scanning that one directory is exactly the introduced-this-milestone set, with no allow-list"

key-files:
  created:
    - firestarter/tests/test_checker_convention.py
  modified: []

key-decisions:
  - "Scoped CHECKER_GLOB to firestarter/scripts/check_*.py only (non-recursive, single directory level) rather than repo-wide or recursive, because a repo-wide version measured RED-on-arrival against 3 pre-existing firestarter_app/tools/ violations this phase does not own"
  - "Recorded the 3 out-of-scope violators (check_dispatch.py, check_sdp_capability_invariants.py, check_mypy_watermark.py) by name in the module docstring rather than silently blessing or silently omitting them — check_mypy_watermark.py's total absence of a paired test is called out explicitly as a genuine gap, not fixed (out of this phase's scope)"
  - "FLOOR=4 and FIXTURE_FLOOR=9 are hardcoded integer literals asserted with >= before any per-checker assertion runs, so a zero-match glob or an accidental deletion fails instead of passing vacuously"

requirements-completed: []  # BASE-08 is closed only in 123-11 per this plan's requirement_closure note

coverage:
  - id: D1
    description: "test_checker_convention.py enforces the check_*.py <-> test_check_*.py <-> planted_* convention over exactly the v1.23 firmware checker set (firestarter/scripts/), with hardcoded FLOOR=4/FIXTURE_FLOOR=9 floors so a zero-match glob fails rather than passing vacuously"
    requirement: "BASE-08"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_checker_convention.py (7 tests, all passing)"
        status: pass
      - kind: unit
        ref: "manual rename-proof: mv tests/test_check_orphan_provisional.py aside -> suite FAILS (1 failed, 6 passed), then restored -> 48 passed again"
        status: pass
    human_judgment: false
  - id: D2
    description: "Firmware half of Phase 123 verified against a fresh build rather than a committed capture: 48 pytest, both native envs at 141/17/all-PASSED, all three AVR builds matching the recorded baseline through both new gates, both coarse-key gates UNARMED, and a structural fork-point..HEAD diff proving no firmware production source moved across the whole phase"
    verification:
      - kind: unit
        ref: "cd firestarter && python3 -m pytest tests/ -q -> 48 passed, 0 skipped"
        status: pass
      - kind: integration
        ref: "pio test -e native / -e native_nodevtools -> 141 test cases: 141 succeeded, 17 suites each"
        status: pass
      - kind: integration
        ref: "pio run -t clean -e {uno,uno328pb,leonardo} && pio run -e {env} -> check_size_baseline.py + check_build_warnings.py exit 0 for all three"
        status: pass
      - kind: other
        ref: "git diff --stat 5c9160a34b665878b05403ab014b959926feb6bf..HEAD -- src include platformio.ini .github test -> empty output"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-31
status: complete
---

# Phase 123 Plan 06: BASE-08 Checker Convention Meta-Test + Firmware-Side Verification Sweep Summary

**Wrote `firestarter/tests/test_checker_convention.py` — a 7-test, filesystem-convention meta-test scoped to `firestarter/scripts/check_*.py` with hardcoded FLOOR=4/FIXTURE_FLOOR=9 floors — then ran the full firmware-side verification sweep (48 pytest, both native envs at 141/17, all three AVR builds against the recorded baseline, both coarse-key gates UNARMED) proving no production firmware code moved across the whole phase.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-31T01:37:00Z
- **Completed:** 2026-07-31T01:49:00Z
- **Tasks:** 2 completed (Task 2 wrote no files — verification-only)
- **Files modified:** 1 (`firestarter/tests/test_checker_convention.py`, new file)

## Accomplishments

- BASE-08's convention meta-test now exists, scoped correctly (D-06 home choice), with a hardcoded non-vacuous floor and a docstring naming the 3 pre-existing out-of-scope host-repo violators
- Proved the meta-test can actually fail: temporarily renamed `tests/test_check_orphan_provisional.py` aside, re-ran the suite (1 failed, 6 passed, correctly identifying the missing pairing), then restored it and confirmed 48 passed again
- Verified the entire firmware half of Phase 123 against a fresh build (not a committed capture) for the first time this phase, with every count asserted rather than paraphrased

## Task Commits

1. **Task 1: Write tests/test_checker_convention.py — glob, pairing assertions, hardcoded floors** — `34bda8c` (test) — commit made inside the `firestarter` submodule (`git -C /workspaces/firestarter commit`)
2. **Task 2: Verify the firmware half of the phase against the real tree and record the counts** — no commit (task writes no files; verification-run only, per plan's `<files>` spec)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md update (meta repo commit follows)

## Files Created/Modified

- `firestarter/tests/test_checker_convention.py` — BASE-08's convention meta-test. Defines `CHECKER_GLOB = "check_*.py"` (non-recursive, `firestarter/scripts/` only), `FLOOR = 4`, `FIXTURE_FLOOR = 9`. Seven tests: glob non-vacuous, every checker has a paired test module, every checker has a planted fixture, fixture directory non-vacuous, each paired test module names its checker's filename, each paired test module asserts a non-zero exit somewhere, and scope is provably firmware-only (no path in the result touches `firestarter_app`).

## Decisions Made

- **Scope pinned to `firestarter/scripts/check_*.py`, non-recursive.** 123-RESEARCH.md's measured table (Correction C-6) shows only 4 of 7 host-repo checkers conform to the `check_X.py` ↔ `test_check_X.py` ↔ `planted_X*` convention; the 3 violators (`check_dispatch.py`, `check_sdp_capability_invariants.py`, `check_mypy_watermark.py`) all live in `firestarter_app/tools/` and predate v1.23. `check_mypy_watermark.py` has no paired test at all. A repo-wide or recursive glob would be RED on arrival against debt this phase did not create. D-06 already put every v1.23 firmware checker in `firestarter/scripts/` (which held zero Python checkers before this phase), so scanning that one directory is exactly the "introduced in this milestone" set BASE-08 names, with no registry file (forbidden by D-08) and no grandfather allow-list (which would silently bless the violators rather than naming them).
- **FLOOR=4, FIXTURE_FLOOR=9 as hardcoded literals**, counted at authoring time: `check_size_baseline.py`, `check_build_warnings.py`, `check_cmake_manifest.py`, `check_orphan_provisional.py` (4 checkers); `planted_build_warnings_avr_redef.log`, `planted_build_warnings_macro_redef.cpp`, `planted_build_warnings_native_excess.log`, `planted_cmake_manifest_excluded_no_reason`, `planted_cmake_manifest_missing_source`, `planted_orphan_provisional_macro`, `planted_size_baseline_flash_regression.log`, `planted_size_baseline_suites_errored.log`, `planted_size_baseline_unparseable.log` (9 planted_* entries, including 2 directory-shaped fixtures). Both asserted with `>=` before any per-checker assertion runs.
- **The three out-of-scope violators are named in the docstring, not allow-listed.** `check_mypy_watermark.py`'s missing test is explicitly called a genuine gap, not blessed.

## FLOOR / FIXTURE_FLOOR as shipped

| Constant | Value | Basis |
|---|---:|---|
| `FLOOR` | 4 | `check_size_baseline.py`, `check_build_warnings.py`, `check_cmake_manifest.py`, `check_orphan_provisional.py` |
| `FIXTURE_FLOOR` | 9 | count of `planted_*` entries in `firestarter/tests/fixtures/` (2 are directory-shaped) |

## Firmware-Side Verification Record (Task 2)

All commands run from `/workspaces/firestarter` at HEAD `34bda8c` (post Task 1 commit), branch `v1.23-py32f071-integration`.

### 1. Firmware pytest suite

`python3 -m pytest tests/ -q` → **48 passed, 0 skipped** (observed integer, asserted — not paraphrased).

### 2. Native environments — both agree

| Env | Cases | Suites | Result |
|---|---:|---:|---|
| `native` | 141 | 17 | 141 succeeded, 0 failed/errored |
| `native_nodevtools` | 141 | 17 | 141 succeeded, 0 failed/errored |

Both agree exactly, matching the 123-01 baseline recording (`envs_agree: true`) — MERGE-06 remains satisfiable as worded for Phase 124's planner.

### 3. AVR clean builds vs. recorded baseline — all three exit 0 on both gates

| Env | Flash used (fresh) | Flash used (baseline) | RAM used (fresh) | RAM used (baseline) | `check_size_baseline.py` | `check_build_warnings.py` |
|---|---:|---:|---:|---:|---|---|
| uno | 23932 | 23932 | 1573 | 1573 | exit 0 (`PASS: uno(flash=23932/32256,ram=1573/2048)`) | exit 0 (`PASS: uno: macro_redefinition=0 (== 0)`) |
| uno328pb | 23976 | 23976 | 1579 | 1579 | exit 0 (`PASS: uno328pb(flash=23976/32384,ram=1579/2048)`) | exit 0 (`PASS: uno328pb: macro_redefinition=0 (== 0)`) |
| leonardo | 26072 | 26072 | 2014 | 2014 | exit 0 (`PASS: leonardo(flash=26072/28672,ram=2014/2560)`) | exit 0 (`PASS: leonardo: macro_redefinition=0 (== 0)`) |

All three fresh builds byte-exact-match the recorded `scripts/baseline/size_baseline.json` values from 123-01. Macro-redefinition count 0 on all three AVR envs, as expected (the AVR rule is `== 0`; the 360-count native watermark is a separate, pre-existing, native-only allowance and does not apply to AVR).

### 4. Native size-baseline gate — both exit 0

```
PASS: native(cases=141,suites=17)
PASS: native_nodevtools(cases=141,suites=17)
```

### 5. Both coarse-key (armed-on-arrival) gates — verbatim UNARMED lines

```
UNARMED: /workspaces/firestarter/platform/py32f071 absent -- this gate arms itself the moment Phase 124 lands the py32f071 port (no manual flip needed; a rename inside the port cannot disarm it either).
```

Identical verbatim output from both `check_cmake_manifest.py` and `check_orphan_provisional.py`, both exit 0. Both name `platform/py32f071` and reference "Phase 124" implicitly via the port-landing framing — 123-11 can quote these lines directly, and Phase 124 asserts the transition to armed.

### 6. Working tree clean

`git status --porcelain` → empty. `.pio/` confirmed still gitignored (`git check-ignore -v .pio` → matched by `.gitignore:1:.pio`). No build artifact or generated file left behind.

### 7. Cumulative no-firmware-code-moves proof (binding constraint 1)

```
FORK=5c9160a34b665878b05403ab014b959926feb6bf   # 123-01-SUMMARY.md's fork_point_firmware, verified non-empty
git merge-base --is-ancestor "$FORK" HEAD        # exit 0 — FORK is an ancestor of HEAD
git diff --stat "$FORK"..HEAD -- src include platformio.ini .github test
# (empty output)
git status --porcelain -- src include platformio.ini .github test
# (empty output)
```

The cumulative `<fork>..HEAD` range — not a working-tree comparison — proves no firmware production source, build config, workflow, or native test suite was touched by ANY plan across the whole phase (123-01 through this plan's own Task 1 commit), not merely by this task's own edits.

### CI coverage honesty (stated explicitly per plan instruction)

**Neither firmware workflow fires on the `v1.23-py32f071-integration` branch.** `build.yml` triggers on `push: branches: [main]` only; `beta-build.yml` triggers on `beta` only. Neither branch is this milestone's working branch, so both workflows are dormant for the duration of v1.23. Every check recorded above (the pytest suite, both native envs, all three AVR builds against both new gates, both coarse-key gates) is a **local run**, not continuous CI coverage. These checkers become CI-live only when this branch merges toward `beta` in Phase 130 — this must not be described as continuously CI-covered from Phase 123 onward.

## Deviations from Plan

None — plan executed exactly as written. No auto-fixes were needed; the meta-test passed on first write against the real tree (4 checkers, 9 fixtures, all pairings and non-zero-exit assertions already present from Plans 123-02 through 123-05), and Task 2's verification sweep matched the recorded baseline exactly with no divergence to report.

## Issues Encountered

None. One iteration during authoring: the initial docstring used the literal word "rglob" in prose (describing what the glob does *not* do), which the plan's own automated verify block checks for via a literal `grep -c 'rglob'` — rewording the prose to avoid the literal token (without changing the module's actual behavior — it never called `rglob` at any point) resolved this before the first commit; not treated as a deviation since no behavior changed, only prose wording, verified before commit.

## Next Phase Readiness

- BASE-08 is now enforced mechanically over the exact v1.23 firmware checker set; ticking the requirement itself is deferred to 123-11 per this plan's `requirement_closure` note.
- The firmware half of Phase 123 is fully verified against a live tree: 48 pytest / 0 skipped, both native envs 141/17/PASSED, all three AVR builds matching the recorded baseline through both new gates, both coarse-key gates correctly UNARMED with their exact lines recorded for 123-11 and for Phase 124's later armed-transition assertion.
- Meta repo remains on `gsd/v1.23-py32f071-integration`; firmware submodule remains on `v1.23-py32f071-integration` at `34bda8c`. No blockers for 123-11.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/tests/test_checker_convention.py`
- FOUND commit `34bda8c` (firestarter, Task 1)
- Verified: `firestarter` on `v1.23-py32f071-integration`; meta on `gsd/v1.23-py32f071-integration`
- Verified: `cd firestarter && python3 -m pytest tests/ -q` → 48 passed, 0 skipped
- Verified: `pio test -e native` and `-e native_nodevtools` → 141 test cases: 141 succeeded, 17 suites, both
- Verified: all three AVR builds (uno/uno328pb/leonardo) match recorded baseline exactly; both new gates exit 0
- Verified: both coarse-key gates exit 0 with identical UNARMED lines naming `platform/py32f071`
- Verified: `git status --porcelain` clean in `firestarter`; cumulative `5c9160a34b665878b05403ab014b959926feb6bf..HEAD` diff over `src include platformio.ini .github test` is empty

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `.planning/phases/123-non-regression-baselines-gate-hardening/123-06-SUMMARY.md`
- FOUND commit `34bda8c` in `firestarter` (`git log --oneline --all | grep 34bda8c`)
