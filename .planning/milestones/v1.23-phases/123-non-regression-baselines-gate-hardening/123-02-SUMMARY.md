---
phase: 123-non-regression-baselines-gate-hardening
plan: 02
subsystem: build-measurement-baselines
tags: [platformio, avr-size, native-tests, non-regression-gate, pytest, milestone-branch]
dependency_graph:
  requires:
    - phase: 123-01
      provides: "firestarter/scripts/baseline/size_baseline.json (recorded truth), tests/fixtures/ captured_* logs"
  provides:
    - "firestarter/scripts/check_size_baseline.py — BASE-01 comparator, stdlib-only, three-way exit taxonomy"
    - "firestarter/tests/test_check_size_baseline.py — 7-test anti-hollow pairing"
    - "3 committed planted_size_baseline_*.log fixtures"
    - "FIRESTARTER_SIZE_BASELINE env seam (single-target default form)"
    - "check_uno_ram.sh deleted (superseded, was already red)"
  affects:
    - "Phase 124 MERGE-05/MERGE-06 (this comparator is the discharging mechanism)"
    - "123-03 (reuses the FIRESTARTER_SIZE_BASELINE seam name and MACRO_REDEF_RE sibling discipline)"
    - "123-06 (convention meta-test globs planted_size_baseline_* and check_size_baseline.py)"
    - "123-11 (evidence artifact cites this exact CLI surface)"
tech_stack:
  added: []
  patterns:
    - "manual argv parsing (no argparse) to keep a firmware-repo checker strictly stdlib-only, matching check_permitted_claims.py house convention"
    - "three-way exit taxonomy (0 pass / 1 violation-or-vacuous / 2 parse-or-tool-error), mirrored from check_mypy_watermark.py"
    - "subprocess-invoked planted-fixture pytest (list argv, never shell=True, never in-process import)"
key_files:
  created:
    - firestarter/scripts/check_size_baseline.py
    - firestarter/tests/test_check_size_baseline.py
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression.log
    - firestarter/tests/fixtures/planted_size_baseline_unparseable.log
    - firestarter/tests/fixtures/planted_size_baseline_suites_errored.log
  modified: []
  deleted:
    - firestarter/scripts/check_uno_ram.sh
decisions:
  - "Rewrote check_size_baseline.py to use manual argv parsing instead of argparse: the plan's own acceptance criterion enumerates the exact stdlib import set (os, re, sys, json, subprocess, pathlib, 'or a subset') and does not include argparse; the house convention (check_permitted_claims.py) already parses argv by hand, so this was corrected before commit rather than left as a drift risk"
  - "Reworded two docstring mentions of the literal substring 'check_uno_ram' in check_size_baseline.py (without changing meaning) after discovering they would otherwise make Task 3's own unreferenced-check grep return non-empty once Task 1's commit landed — the provenance is preserved via size_baseline.json's meta.supersedes field (a .json file outside the grep's --include filters) instead of being duplicated verbatim in the .py docstring"
requirements-completed: []
metrics:
  duration_minutes: 20
  completed: 2026-07-30
status: complete
---

# Phase 123 Plan 02: BASE-01 Size/Test Comparator + check_uno_ram.sh Retirement Summary

One-liner: Wrote a stdlib-only three-way-exit-taxonomy comparator (`check_size_baseline.py`) that turns MERGE-05/MERGE-06 into an exit code by reading 123-01's `size_baseline.json`, paired it with 7 subprocess-invoked planted-fixture tests proving every failure arm actually fails, and retired the already-red `check_uno_ram.sh` after proving it unreferenced in both sub-repos.

**Requirement ticking: this plan ticks nothing.** BASE-01 and BASE-08 are closed only in 123-11, per this plan's own `requirement_closure` field.

## Performance

- **Duration:** ~20 min
- **Tasks:** 3/3 completed
- **Files modified:** 6 (1 created checker, 1 created test module, 3 created fixtures, 1 deleted script)

## Accomplishments

### Task 1 — `scripts/check_size_baseline.py`

Stdlib-only Python 3 CLI (`os`, `re`, `sys`, `json`, `subprocess`, `pathlib` — no `argparse`, no third-party import). Defines `SIZE_RE`, `CASES_RE`, `SUITE_RE`, `ParseError`, `parse_sizes`, `parse_native`, `load_baseline`, `compare_avr`, `compare_native`, `main`. Reads `FIRESTARTER_SIZE_BASELINE` at module scope (default: `<repo root>/scripts/baseline/size_baseline.json`).

Exit taxonomy:
- **0** — every env supplied compares clean (`PASS:` line names every env and its figures, e.g. `PASS: leonardo(flash=26072/28672,ram=2014/2560)`)
- **1** — a regression (`FAIL:` naming baseline vs observed), or the never-vacuous guard firing (zero envs supplied and no `--rebuild`)
- **2** — a log could not be parsed (`ParseError` — missing `RAM:`/`Flash:` lines, missing `N test cases:` line, or missing per-suite rows)

`compare_native` asserts all three of A-4's facts explicitly: `cases`, `suites`, AND `all(status == "PASSED")` — a run with 17 suites all ERRORED still has 17 suites, so asserting only the count would reproduce the project's own "assert counts, never tests pass" anti-pattern in mirror image.

`--rebuild` shells `pio run -t clean -e <env>` + `pio run -e <env>` for the three AVR envs and `pio test -e <env>` for the two native envs; every subprocess call passes a list, never a shell string.

Verified against all five 123-01 captures:

| Invocation | Exit | PASS line |
|---|---|---|
| `--avr-log uno=captured_build_uno.log` | 0 | `PASS: uno(flash=23932/32256,ram=1573/2048)` |
| `--avr-log uno328pb=captured_build_uno328pb.log` | 0 | `PASS: uno328pb(flash=23976/32384,ram=1579/2048)` |
| `--avr-log leonardo=captured_build_leonardo.log` | 0 | `PASS: leonardo(flash=26072/28672,ram=2014/2560)` |
| `--native-log native=captured_test_native_summary.log` | 0 | `PASS: native(cases=141,suites=17)` |
| `--native-log native_nodevtools=captured_test_native_nodevtools_summary.log` | 0 | `PASS: native_nodevtools(cases=141,suites=17)` |
| (no args) | 1 | `FAIL: no envs compared -- supply --avr-log/--native-log or --rebuild ...` (no `PASS:`) |

Commit: `cf4ebb8`

### Task 2 — three planted logs + `tests/test_check_size_baseline.py`

Each planted log is a single stated edit from a named `captured_` source:

| Fixture | Derived from | Edit | Diff |
|---|---|---|---|
| `planted_size_baseline_flash_regression.log` | `captured_build_leonardo.log` | `Flash:` line's `used` raised 26072 → 26584 (+512 B); percentage/bar left untouched (now inconsistent — free proof the parser ignores the bar) | exactly 1 changed line, begins `Flash:` |
| `planted_size_baseline_unparseable.log` | `captured_build_uno.log` | Both `RAM:` and `Flash:` report lines deleted | `grep -c '^RAM:'` = 0, `grep -c '^Flash:'` = 0 |
| `planted_size_baseline_suites_errored.log` | `captured_test_native_summary.log` | All 17 `PASSED` → `ERRORED`; `141 test cases: 141 succeeded` → `141 test cases: 0 succeeded` (total 141 and all 17 rows unchanged) | `grep -cE 'native/avr/\S+ +ERRORED'` = 17, `PASSED` count = 0 |

Observed exit codes and distinctive message substrings, directly invoking the checker:

| Fixture | Exit | Distinctive substring(s) |
|---|---|---|
| `planted_size_baseline_flash_regression.log` | **1** | `FAIL:` + both `26072` (baseline) and `26584` (observed) |
| `planted_size_baseline_unparseable.log` | **2** (literal) | `ERROR: uno: expected RAM and Flash lines, found []` |
| `planted_size_baseline_suites_errored.log` | **1** | `FAIL:` + `ERRORED` (all 17 suites named) |

`tests/test_check_size_baseline.py` — 7 tests, all invoking the checker as a real `subprocess.run([sys.executable, str(_CHECKER), ...])` (list argv), never an in-process import:

1. `test_clean_avr_all_three_envs_pass` — all 3 AVR captures, exit 0, env named in `PASS:`
2. `test_clean_native_both_envs_pass` — both native captures, exit 0, `141` and `17` in `PASS:`
3. `test_planted_flash_regression_flips_checker_to_failure` — non-zero, `FAIL:`, both `26072` and `26584`
4. `test_planted_unparseable_log_exits_exactly_2` — literal exit code `2`, no `PASS:`
5. `test_planted_suites_errored_flips_checker_to_failure` — non-zero, `ERRORED` named
6. `test_never_vacuous_with_no_logs_and_no_rebuild` — non-zero, no `PASS:`, "no ... compared" message
7. `test_baseline_seam_precedence_flips_clean_log_to_fail` — tampers a `tmp_path` copy of `size_baseline.json` via `FIRESTARTER_SIZE_BASELINE`, proves the checker reads the seam rather than embedding numbers

Firmware suite count: **8 passed → 15 passed** (0 skipped), confirmed via `python3 -m pytest tests/ -q`. No `conftest.py`, `pytest.ini`, `pyproject.toml` or `setup.cfg` added (house rule preserved).

Commit: `225f3c5`

### Task 3 — retired `check_uno_ram.sh`

Cross-repo unreferenced-search (run before deletion):

```
$ grep -rl check_uno_ram . --include=*.yml --include=*.yaml --include=*.ini --include=*.md --include=*.sh --include=*.py
scripts/check_uno_ram.sh          # itself
scripts/check_size_baseline.py    # two docstring mentions — reworded, see Deviations
$ grep -rl check_uno_ram /workspaces/firestarter_app/tools /workspaces/firestarter_app/.github
(no output)
```

No workflow, script, or doc in either sub-repo calls `check_uno_ram.sh`. Deleted via `git rm firestarter/scripts/check_uno_ram.sh`.

**Superseded a red gate, not a green one.** `check_uno_ram.sh`'s `RAM_FLOOR=545` (Phase-49 baseline) is above the measured **475 B** free on Uno recorded in 123-01's baseline (2048 − 1573 used = 475). The script would fail if run today. It was referenced by no workflow. `check_size_baseline.py` carries forward the same `^RAM:` parse and three-way exit taxonomy, and is strictly stronger: it covers flash as well as RAM, all three AVR envs rather than `uno` alone, and both native envs — comparing against a recorded measurement instead of a hand-maintained floor.

`size_baseline.json` was **not** edited in this plan (123-01 owns it and already records the supersession in `meta.supersedes`).

Cumulative no-firmware-code-moves check, anchored to 123-01's recorded fork point (`fork_point_firmware: 5c9160a34b665878b05403ab014b959926feb6bf`):

```
$ git merge-base --is-ancestor 5c9160a34b665878b05403ab014b959926feb6bf HEAD; echo $?
0
$ git diff --stat 5c9160a34b665878b05403ab014b959926feb6bf..HEAD -- src include platformio.ini .github test
(empty)
```

Commit: `2332220`

## Checker CLI surface (for 123-11's evidence artifact)

```
python3 scripts/check_size_baseline.py [--baseline PATH] \
    [--avr-log ENV=PATH ...] [--native-log ENV=PATH ...] [--rebuild]
```

- `--baseline PATH` — override the `FIRESTARTER_SIZE_BASELINE` env seam (default: `scripts/baseline/size_baseline.json`)
- `--avr-log ENV=PATH` — repeatable; supplies a `pio run` log for one of `uno`, `uno328pb`, `leonardo`
- `--native-log ENV=PATH` — repeatable; supplies a `pio test` log for one of `native`, `native_nodevtools`
- `--rebuild` — shells `pio run -t clean -e <env>` + `pio run -e <env>` for all three AVR envs and `pio test -e <env>` for both native envs, feeding output to the same parsers
- No arguments and no `--rebuild` → exit 1 (never-vacuous guard)

Entry point: `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Replaced `argparse` with manual argv parsing**
- **Found during:** Task 1, immediately after first draft.
- **Issue:** First draft used `argparse` for the CLI. The plan's own Task 1 acceptance criteria enumerate the exact permitted import set (`os`, `re`, `sys`, `json`, `subprocess`, `pathlib`, "or a subset") and do not include `argparse`; the house convention (`check_permitted_claims.py`, `check_no_log_in_sdp_window.py`) parses argv by hand rather than via `argparse`.
- **Fix:** Rewrote the CLI as `_parse_argv(argv)`, a manual loop over `sys.argv` supporting `--baseline`, repeated `--avr-log`, repeated `--native-log`, and `--rebuild`, raising `SystemExit(2)` on a malformed invocation.
- **Files modified:** `firestarter/scripts/check_size_baseline.py`.
- **Commit:** `cf4ebb8` (folded into Task 1's single commit — corrected before commit, not as a follow-up).
- **Verification:** `grep -n '^import\|^from' scripts/check_size_baseline.py` shows only `json`, `os`, `re`, `subprocess`, `sys`, `pathlib`.

**2. [Rule 1 - Bug] Reworded two docstring mentions of `check_uno_ram`**
- **Found during:** Task 3, while running the unreferenced-search grep before deletion.
- **Issue:** `check_size_baseline.py`'s docstring (written in Task 1, before Task 3 existed on disk) named `scripts/check_uno_ram.sh` verbatim twice, in prose describing the supersession. Task 3's own acceptance criterion — `grep -rl check_uno_ram . --include=*.py ...` must return no results — would otherwise fail permanently, since the checker itself is not deleted.
- **Fix:** Reworded both mentions to describe "the retired Uno-only RAM-ceiling shell gate" / "the retired shell gate's exit code 2" without using the literal substring `check_uno_ram`, and pointed the reader to `size_baseline.json`'s `meta.supersedes` field (a `.json` file, outside the grep's `--include` filters, and already carrying the full provenance from 123-01) for the exact filename and figures.
- **Files modified:** `firestarter/scripts/check_size_baseline.py`.
- **Commit:** `2332220`.
- **Verification:** `grep -rn check_uno_ram . --include=*.yml --include=*.yaml --include=*.ini --include=*.md --include=*.sh --include=*.py` after Task 3's deletion shows zero matches.

No other deviations. Every numeric acceptance criterion (all size/case/suite figures, all diff-line counts, all grep counts, the 15-passed pytest count) passed exactly as specified.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/scripts/check_size_baseline.py`
- FOUND: `/workspaces/firestarter/tests/test_check_size_baseline.py`
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_size_baseline_flash_regression.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_size_baseline_unparseable.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_size_baseline_suites_errored.log`
- MISSING (intentionally, deleted): `/workspaces/firestarter/scripts/check_uno_ram.sh` — confirmed via `test ! -f` and `git ls-files scripts/check_uno_ram.sh` (empty)
- FOUND commit `cf4ebb8` (firestarter, Task 1)
- FOUND commit `225f3c5` (firestarter, Task 2)
- FOUND commit `2332220` (firestarter, Task 3)
- Verified: `firestarter` on `v1.23-py32f071-integration`; meta on `gsd/v1.23-py32f071-integration`
- Verified: `python3 -m pytest tests/ -q` → 15 passed, 0 skipped
- Verified: `git status --porcelain` clean in `firestarter` after all three commits
- Verified: cumulative `git diff --stat 5c9160a..HEAD -- src include platformio.ini .github test` empty; `git status --porcelain -- src include platformio.ini .github test` empty
