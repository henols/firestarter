---
phase: 144-tests-build-verification
plan: 06
subsystem: testing
tags: [pytest, ci-parity, mypy-watermark, ruff, coverage, constants-parity, dual-repo, fw-presence, measurement-only]

# Dependency graph
requires:
  - phase: 144-05
    provides: "The re-anchored firmware baseline commit a594173d2bbbabe74e6a470b4751528435246326 this plan's mandatory porcelain-clean precondition anchors against, and a firmware tree left committed and clean for every host run"
  - phase: 144-02
    provides: "firestarter_app/tests/test_cap03_ack_layout_parity.py (12 tests, behind requires_fw/fw_path) -- the +12 delta this plan's suite/coverage measurement attributes by name, and a second requires_fw-gated module this plan's absent-path sweep independently exercises"
provides:
  - "The verbatim host-half evidence set for TEST-07: dual-repo constants parity proven in BOTH directions on the CI-parity interpreter, the four ci.yml-scoped commands (:81/:84/:87/:90) all green, and the host suite/coverage figures with their delta against Phase 143's 1578/82.92%"
affects: [144-07]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Bidirectional absence proof via a genuine child process: FIRESTARTER_FW_ROOT set in the CHILD's environment, never monkeypatch.setenv -- fw_presence.py binds FW_ROOT/FW_REPO_PRESENT/requires_fw at import and pytest.mark.skipif binds at collection, so only a fresh interpreter invocation sees a different environment"
    - "Cross-check by total identity across independent runs: present-path (1590 passed, 0 skipped) and absent-path (1540 passed, 50 skipped) both sum to 1590 collected items, and the D-21 coverage run's own header independently reports 'collected 1590 items' -- three separate invocations agreeing on the same total is stronger evidence than any one of them alone"
    - "A below-watermark mypy INFO line is quoted verbatim and explicitly not acted on -- lowering the watermark is a decision for a commit that earns it (fewer real errors), never a byproduct of a measurement-only plan"

key-files:
  created: []
  modified: []

key-decisions:
  - "RESEARCH F-11's claim that all 6 non-requires_fw legs in test_revision_constants_parity.py are 'fixture-driven planted-violation legs' is refined against this plan's own source read: only 4 of the 6 (test_planted_value_drift_is_detected:733, test_planted_host_missing_define_is_detected:750, test_planted_firmware_missing_flag_is_detected:768, test_gate_fails_closed_on_an_unreadable_header_path:855) read a fixture or a deliberately-nonexistent tmp_path. The other 2 (test_revision_byte_values_match_firmware_enum:151, test_command_names_dereferences_both_sdp_commands:801) never touch the firmware repo at runtime at all -- they were never requires_fw candidates, not fixture-driven substitutes for one. Both sub-populations are named precisely below rather than restating the coarser six-as-one claim; the module's own docstring at :801-817 states the second population's rationale ('unconditionally... so a regression is caught in every CI run including host-only CI') independently of this plan."
  - "The present-path full-suite run produced ZERO skips, not merely a nonempty skip list with reasons. That is the correct present-path shape, not an omission: every requires_fw-gated test that would skip when the sibling repo is absent instead runs (and passes) when it is present, so an empty skip list at 1590/0 is itself the evidence the plan's acceptance criteria call for."
  - "Coverage is reported unchanged at 82.92% against Phase 143's identical figure (same to two decimal places). This is recorded as the expected consequence of 144-02's new module adding zero product-code lines to the instrumented firestarter/ package -- it reads existing serial_comm.py source text and the cross-repo firestarter.cpp via fw_path, never adding a statement the coverage tool counts -- not investigated further as an anomaly."
  - "requirements-completed left empty, matching 144-01/144-02/144-04/144-05 precedent: this plan's requirement_scope explicitly forbids ticking TEST-07 here. Plan 144-07 owns the consolidated eight-requirement flip; this plan supplies evidence only."

patterns-established:
  - "A cross-repo requires_fw module's 'stays green with no firmware checkout' set is generally a MIX of three populations, not one: fixture/tmp-path-driven planted-violation legs, self-check/non-vacuity/fail-closed legs, and (occasionally) ordinary host-only checks that never needed firmware presence in the first place. Verified on both requires_fw modules exercised this session (test_revision_constants_parity.py: 3+1+2 = 6; test_cap03_ack_layout_parity.py: 2+3+0 = 5), by reading each module's own @requires_fw placement rather than inferring the split from prose."

requirements-completed: []  # TEST-07 evidence only -- 144-07 owns the flip (requirement_scope, D-19/D-20 precedent).

coverage:
  - id: D1
    description: "Constants parity proven in the PRESENT direction on the CI-parity interpreter: the dedicated parity module reports 14 passed verbatim, and the full host suite (the same run establishing the present-path suite total) reports 1590 passed with a ZERO-length skip list -- every requires_fw leg that could skip instead ran and passed."
    requirement: "TEST-07"
    verification:
      - kind: other
        ref: ".venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts=\"\" -q -- /tmp/gsd-144/parity_present.log (14 passed in 0.07s)"
        status: pass
      - kind: other
        ref: ".venv/ci-replica/bin/python -m pytest tests/ -o addopts=\"\" -rs -q -- /tmp/gsd-144/host_present.log (1590 passed, 1 warning, 0 SKIPPED lines, 220.40s)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Constants parity proven in the ABSENT direction as a genuine child process (FIRESTARTER_FW_ROOT set in the child's environment, scratch dir verified empty and .git-free first): the parity module reports the known-answer 6 passed / 8 skipped with one canonical reason string naming the probed marker path, and the full suite reports exit 0, zero ERROR/E-prefixed lines, and a non-zero 50-skip count across 11 distinct modules."
    requirement: "TEST-07"
    verification:
      - kind: other
        ref: "FIRESTARTER_FW_ROOT=<mktemp -d, verified 0 entries> .venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts=\"\" -rs -q -- /tmp/gsd-144/parity_absent.log (6 passed, 8 skipped in 0.06s)"
        status: pass
      - kind: other
        ref: "same env, tests/ -o addopts=\"\" -rs -q -- /tmp/gsd-144/host_absent.log (1540 passed, 50 skipped, 1 warning, 215.72s; grep -cE \"^(ERROR|E )\" == 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "All four ci.yml-scoped commands (ruff check :81, ruff format --check :84, mypy watermark :87, pytest --cov :90) exit 0 on .venv/ci-replica/bin/python 3.11.15, each captured verbatim; the mypy watermark's below-floor INFO line is quoted and explicitly not acted on."
    requirement: "TEST-07"
    verification:
      - kind: other
        ref: ".venv/ci-replica/bin/ruff check firestarter/ tests/ -- /tmp/gsd-144/ruff.log (All checks passed!, exit 0)"
        status: pass
      - kind: other
        ref: ".venv/ci-replica/bin/ruff format --check firestarter/ tests/ -- /tmp/gsd-144/ruff.log (135 files already formatted, exit 0)"
        status: pass
      - kind: other
        ref: ".venv/ci-replica/bin/python tools/check_mypy_watermark.py -- /tmp/gsd-144/mypy.log (33 errors, watermark 35, exit 0)"
        status: pass
      - kind: other
        ref: ".venv/ci-replica/bin/python -m pytest tests/ -o addopts=\"\" --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -- /tmp/gsd-144/host_cov.log (1590 passed, 82.92% coverage, 231.06s)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both standing absences restated without implying coverage: no CI leg in either repository runs the three *_v131 firmware envs (D-15); the app's CI has no firmware checkout so every requires_fw cross-repo gate skips there -- this plan's own absent-path measurement (1540 passed / 50 skipped) is the direct, quantified proof of exactly what CI experiences today."
    requirement: "TEST-07"
    verification:
      - kind: other
        ref: "This SUMMARY, section 'Standing Absences (restated, not closed)'"
        status: pass
    human_judgment: false

# Metrics
duration: 26min
completed: 2026-08-14
status: complete
---

# Phase 144 Plan 06: TEST-07 Host-Half CI-Parity Sweep Summary

**Constants parity measured in both directions on the CI-parity interpreter (14 passed present / 6 passed + 8 skipped absent, both verbatim), all four `ci.yml`-scoped commands green, and the host suite holding at 1590 passed / 82.92% coverage -- exactly Phase 143's 1578/82.92% plus 144-02's 12 new tests, coverage unmoved.**

## Performance

- **Duration:** ~26 min
- **Tasks:** 2 (both measurement-only; no commit in either sub-repo)
- **Files modified:** 0 in `firestarter` or `firestarter_app` (the transient `.coverage` rewrite aside); 1 in the meta repo (this SUMMARY)

## Accomplishments

- Task 1: D-16's bidirectional constants-parity sweep -- present path (14 passed parity-only; 1590 passed / 0 skipped whole-suite) and absent path via a genuine child process (6 passed / 8 skipped parity-only, matching the known answer exactly; 1540 passed / 50 skipped whole-suite, zero errors, exit 0), both on `.venv/ci-replica/bin/python` 3.11.15.
- Task 2: all four CI-scoped commands (`ci.yml` :81/:84/:87/:90) green, plus the D-21 suite/coverage measurement (1590 passed, 82.92% coverage) with its delta against Phase 143's 1578/82.92% attributed to 144-02's new module, and both standing absences (the three `*_v131` firmware envs; the app CI's missing firmware checkout) restated rather than implied covered.

## Task Commits

Both tasks are measurement-only per this plan's `commits_land_in: meta` / `reads_repos: [firestarter_app, firestarter]` declaration -- neither sub-repo was written to (the transient `.coverage` rewrite aside), so neither task produced a sub-repo commit. Evidence lives in `/tmp/gsd-144/{parity_present,host_present,parity_absent,host_absent,ruff,mypy,host_cov}.log` (scratch, not committed, per this plan's `<artifacts_this_phase_produces>`).

1. **Task 1: D-16's bidirectional constants-parity sweep** -- no commit (measurement-only)
2. **Task 2: The four CI-scoped commands and the D-21 suite/coverage measurement** -- no commit (measurement-only)

**Plan metadata:** this SUMMARY's own commit, in the superproject.

## Files Created/Modified

None in `firestarter` or `firestarter_app` -- both sub-repos are read-only inputs to this plan. `firestarter_app/.coverage` was rewritten by the Task 2 coverage run (an untracked, pre-existing entry; not staged or committed). The only file this plan creates is `.planning/phases/144-tests-build-verification/144-06-SUMMARY.md` itself, in the meta repo.

## Task 1: D-16's Bidirectional Constants-Parity Sweep

### Precondition

```
$ git -C /workspaces/firestarter status --porcelain | wc -l
0
$ git -C /workspaces/firestarter rev-parse HEAD
a594173d2bbbabe74e6a470b4751528435246326
```

Firmware porcelain confirmed EMPTY before any host run. HEAD `a594173d2bbbabe74e6a470b4751528435246326` is 144-05's re-anchor commit -- the firmware tree every measurement below was taken against.

### Interpreter

```
$ .venv/ci-replica/bin/python --version
Python 3.11.15
```

Every host command in both tasks used this interpreter (or its `ruff`), never the ambient 3.12.

### Present path

Parity module only:

```
$ .venv/ci-replica/bin/python -m pytest tests/test_revision_constants_parity.py -o addopts="" -q
..............                                                           [100%]
14 passed in 0.07s
```

Full suite (also establishes the present-path suite total used again in Task 2):

```
$ .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -rs -q
[... 1590-item run ...]
=============================== warnings summary ===============================
tests/test_click_group_gate_hook.py::test_multicommand_is_deprecated_alias_not_in_dir_but_still_reachable[MultiCommand]
  /workspaces/firestarter_app/tests/test_click_group_gate_hook.py:161: DeprecationWarning: 'MultiCommand' is deprecated and will be removed in Click 9.0. Use 'Group' instead.
    assert getattr(click, attr_name) is not None
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1590 passed, 1 warning in 220.40s (0:03:40)
```

**The present-path skip list is empty** -- `grep -c "^SKIPPED" /tmp/gsd-144/host_present.log` returns `0`. That is the correct present-path shape, not an omission: with the sibling firmware repo present, every `requires_fw`-gated test runs (and passes) rather than skipping, so there is no skip list with reasons to report beyond "none, by design."

### Absent path

Scratch directory, verified empty and `.git`-free before use:

```
$ EMPTY=$(mktemp -d)   # /tmp/tmp.TxBaflaOiC
$ ls -A "$EMPTY" | wc -l
0
$ find "$EMPTY" -maxdepth 1 -name ".git" -print
[no output]
```

Parity module only, as a **child process** with `FIRESTARTER_FW_ROOT` set in that child's environment (never `monkeypatch.setenv`, which cannot reach `FW_ROOT`/`FW_REPO_PRESENT`/`requires_fw` -- all three bind at import, and `pytest.mark.skipif` binds at collection):

```
$ FIRESTARTER_FW_ROOT=/tmp/tmp.TxBaflaOiC .venv/ci-replica/bin/python -m pytest \
    tests/test_revision_constants_parity.py -o addopts="" -rs -q
.sssssss...s..                                                           [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/test_revision_constants_parity.py:563: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
SKIPPED [1] tests/test_revision_constants_parity.py:575: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
SKIPPED [1] tests/test_revision_constants_parity.py:585: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
SKIPPED [1] tests/test_revision_constants_parity.py:598: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
SKIPPED [1] tests/test_revision_constants_parity.py:617: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
SKIPPED [1] tests/test_revision_constants_parity.py:658: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
SKIPPED [1] tests/test_revision_constants_parity.py:686: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
SKIPPED [1] tests/test_revision_constants_parity.py:786: firestarter firmware checkout absent (no /tmp/tmp.TxBaflaOiC/.git marker)
6 passed, 8 skipped in 0.06s
```

**Exactly the RESEARCH-measured known answer** (6 passed, 8 skipped), every skip naming the probed marker path `/tmp/tmp.TxBaflaOiC/.git`, one canonical reason string (`firestarter firmware checkout absent (no <marker> marker)`) repeated eight times, never anonymous.

Full suite, same child-process mechanism, teed to `/tmp/gsd-144/host_absent.log`:

```
$ FIRESTARTER_FW_ROOT=/tmp/tmp.TxBaflaOiC .venv/ci-replica/bin/python -m pytest \
    tests/ -o addopts="" -rs -q
[... 50 SKIPPED lines, each naming /tmp/tmp.TxBaflaOiC/.git ...]
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1540 passed, 50 skipped, 1 warning in 215.72s (0:03:35)
```

Assertions made against this run, not merely its exit code:
- `grep -cE "^(ERROR|E )" /tmp/gsd-144/host_absent.log` → `0` (zero errors).
- Exit code corroborated directly on the anchor module (non-piped rerun): `6 passed, 8 skipped in 0.05s` with `echo $?` → `0`.
- The skip count is **50**, non-zero, and cross-checks exactly: `1540 passed + 50 skipped = 1590` -- the identical total the present-path run collected with 0 skips, and the identical total the D-21 coverage run (Task 2) independently reports as "collected 1590 items". Three independent invocations agree on the same denominator.

**Per-module skip breakdown (bracket-summed, totalling exactly 50 across 11 distinct modules):**

| Module | Skips |
|---|---|
| `test_gen_validation_header.py` | 11 |
| `test_revision_constants_parity.py` | 8 |
| `test_cap03_ack_layout_parity.py` | 7 |
| `test_py32_flash_map_host.py` | 6 |
| `test_py32_asset_name_host.py` | 6 |
| `test_sdp_table_parity.py` | 4 |
| `test_sdp_bus_config_drift.py` | 3 |
| `test_dispatch_mirror.py` | 2 |
| `test_scan_paths_resolve.py` | 1 |
| `test_check_no_log_in_sdp_window.py` | 1 |
| `test_check_is_memory_cmd_no_ifdef.py` | 1 |

RESEARCH's F-11 census counted **13** modules using `requires_fw` by occurrence-grep (adding `test_fw_presence.py`, `test_skip_census.py`, and `conftest.py`, each 1-3 occurrences). This run's measured skip list names only the **11** modules above -- the other 2 (plus `conftest.py`, which is not a test module) reference `requires_fw` in prose/docstrings without gating an actual test on it in a way that produces a SKIPPED line here: `test_fw_presence.py` tests the seam mechanism itself and `test_skip_census.py` runs a subprocess census of the rest of the suite's skip reasons -- neither carries its own `@requires_fw`-decorated test. Both statements (13 modules reference the name; 11 modules actually skip a test) are true and non-contradictory; this record states both rather than only the coarser one.

### The 6 surviving legs in `test_revision_constants_parity.py`, verified by reading `@requires_fw` placement directly (not inferred from prose)

Refining RESEARCH F-11's "the 6 are the fixture-driven planted-violation legs" against a direct source read of every `def test_` / `@requires_fw` pair in the module: the 6 non-gated (always-passing) tests split into **two** populations, not one --

- **4 are planted-violation / adversarial-input legs**, deliberately given no `requires_fw` so the checker's failure modes stay exercised even with no firmware checkout:
  - `test_planted_value_drift_is_detected` (:733) -- reads the committed fixture `tests/fixtures/planted_constants_value_drift.h`
  - `test_planted_host_missing_define_is_detected` (:750) -- reads `tests/fixtures/planted_constants_host_missing.h`
  - `test_planted_firmware_missing_flag_is_detected` (:768) -- reads `tests/fixtures/planted_constants_fw_missing.h`
  - `test_gate_fails_closed_on_an_unreadable_header_path` (:855) -- points `FIRMWARE_HEADER` at a deliberately-nonexistent `tmp_path` entry
- **2 never touch the firmware repo at runtime at all**, so they were never `requires_fw` candidates in the first place:
  - `test_revision_byte_values_match_firmware_enum` (:151) -- asserts hardcoded `REVISION_*` byte values, no file read
  - `test_command_names_dereferences_both_sdp_commands` (:801) -- its own docstring (:811-813) states this is deliberate: "unconditionally (no `requires_fw` skip)... so a regression is caught in every CI run including host-only CI"

The same two-population split reproduces on 144-02's `test_cap03_ack_layout_parity.py` (verified the same way): of its 5 non-gated tests, 2 are the committed planted plants (`test_planted_literal_index_is_detected`, `test_planted_truncated_emitted_length_is_detected`) and 3 are self-check/fail-closed legs (`test_gate_fails_closed_on_an_unreadable_firmware_path`, `test_this_module_cannot_be_silently_skipped`, `test_own_needles_do_not_appear_verbatim_in_this_module`) -- zero of its 5 fall into the "never touches firmware" third population, unlike the older module. This is exactly why 144-02's two CAP-03 plants were deliberately given the fixture-driven treatment: it is the established pattern this session confirms is still followed, keeping a new gate's failure modes exercised in host-only CI from the day it lands.

**Honest limit, stated plainly:** `requires_fw` fails OPEN across the repo boundary by design. The app's CI runs with no firmware checkout, so every one of the 50 skips measured above is exactly what happens on every CI run today -- proving nothing about parity there. Adding a firmware checkout to app CI remains deferred (D-16): it forces an unanswered question about which firmware ref to pin, and `beta` and the v1.31 branch disagree today.

**Scope of this sweep:** the whole host suite (1590 collected items) was run in both directions, not a named 13-module subset -- satisfying D-16 via the "run the whole suite twice" option RESEARCH names as equally valid.

## Task 2: The Four CI-Scoped Commands and the D-21 Suite/Coverage Measurement

All four commands below are `ci.yml`'s actual gate steps, cited at their real line numbers (C-02 -- not the ":80-:87" range some earlier documents cite, which would omit the coverage floor at :90 entirely).

### 1. `ruff check firestarter/ tests/` (`ci.yml` :81)

```
$ .venv/ci-replica/bin/ruff check firestarter/ tests/
All checks passed!
```

Exit 0 (verified directly, non-piped).

### 2. `ruff format --check firestarter/ tests/` (`ci.yml` :84)

```
$ .venv/ci-replica/bin/ruff format --check firestarter/ tests/
135 files already formatted
```

Exit 0 (verified directly, non-piped). 135, not Phase 143's 134 -- the +1 is 144-02's new `test_cap03_ack_layout_parity.py`, written to the repo's `py39`/88-column target from the start.

### 3. `python tools/check_mypy_watermark.py` (`ci.yml` :87)

```
$ .venv/ci-replica/bin/python tools/check_mypy_watermark.py
checked 137 source files
mypy errors: 33 (watermark: 35)
INFO: 33 errors -- 2 below watermark (35). The watermark may be lowered to 33,
but only if this run is complete: this run's mypy invocation passed both the
completion-clause guard and the MIN_CHECKED_SOURCE_FILES coverage floor, which
is the evidence of completeness. Lower it in the same commit as the fixes that
reduced the count -- never to make a failing gate pass.
$ echo $?
0
```

Exit 0 -- a genuine pass, not the exit-2 "cannot be trusted" condition. The watermark is **not** lowered here, per this plan's explicit prohibition: the INFO line is quoted verbatim above as a recorded invitation, not acted on. 137 checked source files (Phase 143 recorded 136) and 33 errors (unmoved from Phase 143's 33) -- consistent with this phase adding one new host test module and zero `src/`-equivalent production code.

### 4. `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` (`ci.yml` :90) + `-o addopts=""` for D-21's record

```
$ .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" --cov=firestarter \
    --cov-report=term-missing --cov-fail-under=70
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspaces/firestarter_app
configfile: pyproject.toml
plugins: syrupy-5.5.3, cov-7.1.0
collected 1590 items
[...]
Name                               Stmts   Miss  Cover   Missing
----------------------------------------------------------------
[... per-file table ...]
----------------------------------------------------------------
TOTAL                               5035    860    83%
Required test coverage of 70% reached. Total coverage: 82.92%
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
================= 1590 passed, 1 warning in 231.06s (0:03:51) ==================
```

0 failed, coverage 82.92% (comfortably above the 70% floor), 1590 passed, 30 snapshots passed.

### Delta against Phase 143's recorded state (1578 passed, 82.92% coverage)

| Figure | Phase 143 (`143-HOST-RECORD.md` §7.6) | This plan (144-06) | Delta | Cause |
|---|---|---|---|---|
| Passed | 1578 | 1590 | **+12** | 144-02's `test_cap03_ack_layout_parity.py` (12 tests, verified in its own SUMMARY's GREEN transcript) |
| Coverage | 82.92% | 82.92% | **+0.00 pp** | The new module adds zero product-code lines to the instrumented `firestarter/` package -- it reads `serial_comm.py`'s existing source text and the cross-repo `firestarter.cpp` via `fw_path`, never adding a statement the coverage tool counts. A test-only addition with no new `firestarter/` statements is expected to leave the percentage exactly where it was. |
| ruff-formatted files | 134 | 135 | +1 | Same new module |
| mypy checked files | 136 | 137 | +1 | Same new module |
| mypy errors | 33 | 33 | 0 | New module is fully typed; pre-existing errors untouched |

`1578 + 12 = 1590` -- exact, no discrepancy. Every figure above is reconciled to a named cause, not left as an unexplained movement.

### Both standing absences, restated

- **No CI leg in either repository runs the three `*_v131` firmware envs** (`native_params_v131`, `native_loop_v131`, `native_trace_v131`) -- D-15, unchanged by this plan. They remain a local run-by-name obligation, recorded loudly, never a CI claim.
- **The app's CI has no firmware checkout, so every `requires_fw` cross-repo parity gate skips there** -- D-16. This plan's own absent-path measurement above (1540 passed / 50 skipped, zero errors) is the direct, quantified proof of exactly what every CI run experiences today: not a claim that CI now covers cross-repo parity, but a measurement of the honest gap.

### Git status verification (both repos, after all Task 2 commands)

```
$ git -C /workspaces/firestarter_app status --porcelain
?? .coverage
?? .planning/config.json
?? SECURITY.md
?? datasheets/M27C1001.pdf
?? datasheets/M27C512.pdf
?? datasheets/W27C512.pdf
?? datasheets/W27E257.pdf
?? write_test_port.sh
$ git -C /workspaces/firestarter_app status --porcelain | grep -v '^?? ' | wc -l
0
$ git -C /workspaces/firestarter status --porcelain | wc -l
0
```

`firestarter_app` carries only its 8 pre-existing untracked entries (unchanged set; `.coverage` is the transient rewrite this plan's own coverage run produces), zero tracked-file modifications. `firestarter` is still completely clean at plan end -- the D-20 precondition held throughout both tasks.

## Standing Absences (restated, not closed)

- The three `*_v131` firmware envs run in no CI leg of either repository (D-15).
- The app's CI has no firmware checkout; every cross-repo parity gate fails OPEN there by design (D-16) -- this plan measured exactly what that means (50 skips) rather than asserting it abstractly.
- No claim about real silicon is made anywhere in this plan -- bench evidence is Phase 145's.
- This plan authors no new gate leg, so D-18's RED-then-GREEN planted-violation obligation does not apply to it directly; it belongs to (and was already discharged by) the plans that authored the legs measured here -- 144-01's mapping gate and 144-02's CAP-03 gate, both already carrying their own RED/GREEN transcripts in their SUMMARYs.

## Decisions Made

See frontmatter `key-decisions`. In brief: RESEARCH F-11's six-legs-are-all-planted-violations claim is refined into its true two-population (and, on the older module, three-population) split, verified by reading `@requires_fw` placement directly rather than restating the coarser prose; the present-path's zero-skip result is recorded as the correct shape rather than padded with an empty list's worth of narrative; the unchanged 82.92% coverage figure is attributed to 144-02's module adding no new `firestarter/`-package statements; and `requirements-completed` is left empty per this plan's explicit scope boundary.

## Deviations from Plan

None -- plan executed exactly as written. The refinement of F-11's six-legs framing (see Decisions) is additional verified precision, not a deviation: every figure and acceptance criterion the plan specifies was measured and matched exactly (14 passed present; 6 passed/8 skipped absent; the four CI commands green; 1590/82.92%).

## Issues Encountered

While enumerating `gsd-tools state` subcommand argument requirements ahead of this plan's end-of-plan STATE.md update, two subcommands (`advance-plan`, `record-session`) executed immediately on a bare no-args invocation instead of erroring the way `record-metric`/`add-decision` did -- mutating STATE.md's Current Position from "Plan: 6 of 7" to "Plan: 7 of 7" and bumping both timestamps before this plan had written its SUMMARY. Caught immediately via `git -C /workspaces diff .planning/STATE.md` (confirming nothing else had touched the file since session start) and reverted with `git -C /workspaces checkout -- .planning/STATE.md` before anything was staged or committed. No lasting effect. Recorded here as a tooling caution: `advance-plan` and `record-session` must be invoked exactly once, with correct arguments, at the genuine end of a plan -- not while probing the CLI's usage.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Plan 144-07 can now cite this plan's host-half evidence (both parity directions, all four CI-scoped commands, the suite/coverage delta) alongside 144-01 through 144-05's firmware-half evidence for the consolidated eight-requirement `TEST-01`..`TEST-08` flip.
- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` coverage tables were NOT edited by this plan, per its explicit `requirement_scope` boundary -- `TEST-07` remains `[ ]` / "Pending" in both, exactly as before this plan ran.
- No blockers. `firestarter` remains clean at `a594173`; `firestarter_app` carries only its 8 pre-existing untracked entries (`.coverage` freshly rewritten, as expected of a coverage run).

## Self-Check: PASSED

This SUMMARY file confirmed written before its commit. All quoted figures (14 passed; 6 passed/8 skipped; 1590 passed present; 1540 passed/50 skipped absent; ruff/mypy/coverage verdicts; 82.92% coverage) were captured verbatim from this session's own command output, teed to `/tmp/gsd-144/{parity_present,host_present,parity_absent,host_absent,ruff,mypy,host_cov}.log`, and cross-checked for internal consistency (1540+50=1590=1578+12, matching three independent invocations). `git -C /workspaces/firestarter status --porcelain` and the `firestarter_app` tracked-modification count were both re-verified at 0 immediately before writing this file.

---
*Phase: 144-tests-build-verification*
*Completed: 2026-08-14*
