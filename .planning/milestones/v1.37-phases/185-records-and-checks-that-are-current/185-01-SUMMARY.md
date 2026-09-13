---
phase: 185-records-and-checks-that-are-current
plan: 01
subsystem: infra
tags: [firmware, pio, size-baseline, fixture-severance, ci]

requires: []
provides:
  - "size_baseline.json re-recorded to cold post-Phase-183 figures on both avr_targets and native_envs axes"
  - "captured_build_v185_{uno,uno328pb,leonardo}.log + planted_size_baseline_flash_regression_v185.log fixture family"
  - "captured_test_native{,_nodevtools}_summary.log re-captured in place at 185/17"
  - "four coupled test legs severed onto the v185 generation with reconciliation docstrings"
  - "proof that the frozen v158 generation, BASE-01, and check_size_baseline.py are all byte-unchanged"
affects: [185-02, 185-03, 185-04, 185-05, 185-06]

actuals:
  tokens: 13122
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns: ["fixture severance (six-generation convention)", "transcribe-never-compute baseline provenance"]

key-files:
  created:
    - firestarter/tests/fixtures/captured_build_v185_uno.log
    - firestarter/tests/fixtures/captured_build_v185_uno328pb.log
    - firestarter/tests/fixtures/captured_build_v185_leonardo.log
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression_v185.log
  modified:
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/tests/fixtures/captured_test_native_summary.log
    - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
    - firestarter/tests/test_check_size_baseline.py

key-decisions:
  - "The cold capture confirmed the RESEARCH.md prediction exactly (uno 22734/1434, uno328pb 22778/1440, leonardo 24830/1875, native/native_nodevtools 185/17) -- no capture disagreed with any prediction, so no reconciliation of a figure discrepancy was needed."
  - "The predicted red-leg set (four) matched the observed red-leg set exactly at Task 1 Step 4 -- test_baseline_seam_precedence_flips_clean_log_to_fail was deliberately left on captured_build_v153_leonardo.log, unchanged, matching Phase 158's own choice."
  - "The whole-suite run (`pytest tests/ -q`) requires a clean git working tree because test_flash_path_record_sync.py and the v131 requirement/trace-exhaustiveness modules assert repo porcelain -- the suite was run once pre-commit (informational) and once post-commit (the gating run) to avoid a false failure from this plan's own uncommitted fixtures."

requirements-completed: [CLAIM-04, CLAIM-05]

coverage:
  - id: D1
    description: "scripts/baseline/size_baseline.json's avr_targets and native_envs blocks re-recorded to the cold post-Phase-183 figures, transcribed from a single uninterrupted cold pass"
    requirement: "CLAIM-04"
    verification:
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... --native-log native=... --native-log native_nodevtools=..."
        status: pass
    human_judgment: false
  - id: D2
    description: "CLAIM-04 achieved by fixture severance: new captured_build_v185_* family + planted sibling, frozen v158 family left byte-unchanged, no new MERGE-05 exemption"
    requirement: "CLAIM-05"
    verification:
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_clean_avr_all_three_envs_pass"
        status: pass
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_clean_native_both_envs_pass"
        status: pass
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_planted_flash_regression_flips_checker_to_failure"
        status: pass
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_default_mode_is_unchanged_by_the_new_flag"
        status: pass
      - kind: unit
        ref: "tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption"
        status: pass
      - kind: other
        ref: "git diff --exit-code ec7c1bbd9768c58908a3cf1b3c15b7695036b3e6 -- <four frozen v158 paths>"
        status: pass
      - kind: other
        ref: "git diff --exit-code ec7c1bbd9768c58908a3cf1b3c15b7695036b3e6 -- scripts/check_size_baseline.py scripts/baseline/size_baseline_base01.json"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-09-11
status: complete
---

# Phase 185 Plan 01: Firmware Size Baseline Re-Record by Fixture Severance Summary

**Re-recorded `size_baseline.json` to the cold post-Phase-183 figures (uno 22734/1434, uno328pb 22778/1440, leonardo 24830/1875, native/native_nodevtools 185/17) by severing four coupled test legs onto a new `captured_build_v185_*` fixture generation, leaving the frozen v158 generation and the BASE-01 MERGE-05 anchor provably byte-unchanged.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 2
- **Files modified:** 8 (4 new, 4 modified)
- **Firmware commit:** `14be84c`

## Accomplishments

- `scripts/baseline/size_baseline.json`'s `avr_targets` and `native_envs` blocks moved together, in one commit, to figures transcribed from a single cold pass.
- Four new fixtures: `captured_build_v185_{uno,uno328pb,leonardo}.log` and `planted_size_baseline_flash_regression_v185.log`.
- Two native summary fixtures re-captured in place (D-09): `captured_test_native_summary.log`, `captured_test_native_nodevtools_summary.log`.
- Four coupled test legs severed onto the v185 generation, each with a severance/reconciliation docstring: `test_clean_avr_all_three_envs_pass`, `test_clean_native_both_envs_pass`, `test_planted_flash_regression_flips_checker_to_failure`, `test_default_mode_is_unchanged_by_the_new_flag`.
- Task 2 proved, with an explicit base-sha diff (not merely a worktree diff), that the frozen v158 generation, `scripts/check_size_baseline.py`, and `size_baseline_base01.json` are all byte-unchanged, and that `--policy merge05` still exits 0 against BASE-01 with headroom on all three targets.

## Task Commits

1. **Task 1: TRACER — one cold pass, one commit: capture, transcribe, sever, green** — `14be84c` (feat, firestarter repo)
2. **Task 2: CLAIM-05's freeze proof and the no-new-exemption re-proof** — no commit (this task asserts properties only; both files it names are unmodified, confirmed by empty `git diff --exit-code` against the base sha)

_Firmware repo `firestarter/` is a git submodule. Its gitlink in the meta repo is deliberately NOT staged here — plan 185-06 advances both gitlinks by name._

## Step-by-Step Evidence

### Step 0 — Pin the tree

```
$ git rev-parse HEAD
ec7c1bbd9768c58908a3cf1b3c15b7695036b3e6
$ git status --porcelain
(empty)
```

No modified tracked files; the whole cold pass ran against this exact tree position. (No pre-existing untracked `datasheets/*.pdf` were present in this checkout, contrary to RESEARCH.md's note about a prior session's tree state — this session's tree had none.)

### Step 1 — Three cold AVR captures, in order, no source edit interleaved

```
$ rm -rf .pio/build/uno && pio run -e uno > tests/fixtures/captured_build_v185_uno.log 2>&1
RAM:   (used 1434 bytes from 2048 bytes)
Flash: (used 22734 bytes from 32768 bytes)
exit 0

$ rm -rf .pio/build/uno328pb && pio run -e uno328pb > tests/fixtures/captured_build_v185_uno328pb.log 2>&1
RAM:   (used 1440 bytes from 2048 bytes)
Flash: (used 22778 bytes from 32768 bytes)
exit 0

$ rm -rf .pio/build/leonardo && pio run -e leonardo > tests/fixtures/captured_build_v185_leonardo.log 2>&1
RAM:   (used 1875 bytes from 2560 bytes)
Flash: (used 24830 bytes from 32768 bytes)
exit 0
```

Section-shape diff against `captured_build_v158_<env>.log` (Processing/PACKAGES/Linking/Checking size/RAM/Flash/[SUCCESS]/Environment-Status order) was identical for all three envs (`diff <(grep -oE ...) <(grep -oE ...)` exit 0 on each); only line counts differ (86 vs 91 lines), consistent with more compiled TUs on this tree, not a structural change. Plain redirection (`>`, not `| tee`) was used and is consistent with every prior committed fixture (no ANSI colour on non-TTY stdout).

### Step 2 — Two native re-captures, same pass

```
$ pio test -e native > /tmp/native_full.log 2>&1; exit 0
================ 185 test cases: 185 succeeded in 00:01:11.835 ================

$ pio test -e native_nodevtools > /tmp/native_nodevtools_full.log 2>&1; exit 0
================ 185 test cases: 185 succeeded in 00:01:17.473 ================
```

The `SUMMARY` block (from the `=== SUMMARY ===` line onward) of each full run was written into `tests/fixtures/captured_test_native_summary.log` / `captured_test_native_nodevtools_summary.log` respectively — the same extraction shape the pre-existing fixtures already used. Both are genuine re-captures; the duration figures are real per-suite timings from these two runs, never edited.

### Step 3 — Transcribe, never compute

Every AVR/native figure written into `size_baseline.json`, paired with its source line:

| JSON field | Value | Source line quoted |
|---|---|---|
| `avr_targets.uno.flash_used` | 22734 | `captured_build_v185_uno.log`: `Flash: [=======   ]  69.4% (used 22734 bytes from 32768 bytes)` |
| `avr_targets.uno.ram_used` | 1434 | `captured_build_v185_uno.log`: `RAM:   [=======   ]  70.0% (used 1434 bytes from 2048 bytes)` |
| `avr_targets.uno328pb.flash_used` | 22778 | `captured_build_v185_uno328pb.log`: `Flash: [=======   ]  69.5% (used 22778 bytes from 32768 bytes)` |
| `avr_targets.uno328pb.ram_used` | 1440 | `captured_build_v185_uno328pb.log`: `RAM:   [=======   ]  70.3% (used 1440 bytes from 2048 bytes)` |
| `avr_targets.leonardo.flash_used` | 24830 | `captured_build_v185_leonardo.log`: `Flash: [========  ]  75.8% (used 24830 bytes from 32768 bytes)` |
| `avr_targets.leonardo.ram_used` | 1875 | `captured_build_v185_leonardo.log`: `RAM:   [=======   ]  73.2% (used 1875 bytes from 2560 bytes)` |
| `native_envs.native.cases`/`.succeeded` | 185 | `captured_test_native_summary.log`: `================ 185 test cases: 185 succeeded in 00:01:11.835 ================` |
| `native_envs.native_nodevtools.cases`/`.succeeded` | 185 | `captured_test_native_nodevtools_summary.log`: `================ 185 test cases: 185 succeeded in 00:01:17.473 ================` |

`flash_total`/`ram_total` unchanged (32768/2048/2048/2560, non-gate-bearing but updated for consistency); `flash_free`/`ram_free` recomputed as `total - used` for consistency (record-keeping only, per RESEARCH §A.2). `suites` for both native envs stays 17 (captured line shows 17 rows). A new `meta.cold_rerecord_plan185_01` provenance entry was added in the shape of the existing `cold_rerecord_phase158` key, naming the recipe, the pinned tree sha, and the five committed logs as the transcription source.

**No arithmetic trap:** the capture figures (22734/22778/24830) match RESEARCH.md's own falsification predictions exactly, which in turn match 183-05's own post-deletion transcript figures — confirming that Phase 183's shrink deltas, applied correctly (from 183-01's pre-deletion figures, not from the stale live baseline), land at these exact numbers. No figure was computed by arithmetic on this file's own prior generation.

### Step 4 — Observe the RED before severing (verbatim)

Run: `python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""`, with `size_baseline.json` already moved and all four legs still pointing at the prior generation:

```
FAILED tests/test_check_size_baseline.py::test_clean_avr_all_three_envs_pass
FAILED tests/test_check_size_baseline.py::test_clean_native_both_envs_pass
FAILED tests/test_check_size_baseline.py::test_planted_flash_regression_flips_checker_to_failure
FAILED tests/test_check_size_baseline.py::test_default_mode_is_unchanged_by_the_new_flag
4 failed, 10 passed in 2.24s
```

Representative failure detail (`test_clean_avr_all_three_envs_pass`, uno arm):
```
AssertionError: uno: expected exit 0 on a clean captured log in default mode.
  stdout:
  FAIL:
    uno: flash_used baseline=22734 observed=22952
```

**Observed count: 4. Predicted count: 4. They match exactly** — no reconciliation of a disagreement was needed; the observed set is identical to the predicted set named in the plan (`test_clean_avr_all_three_envs_pass`, `test_clean_native_both_envs_pass`, `test_planted_flash_regression_flips_checker_to_failure`, `test_default_mode_is_unchanged_by_the_new_flag`).

### Step 5 — Derive the planted sibling

```
$ cp tests/fixtures/captured_build_v185_leonardo.log tests/fixtures/planted_size_baseline_flash_regression_v185.log
$ sed -i '84s/used 24830 bytes/used 25342 bytes/' tests/fixtures/planted_size_baseline_flash_regression_v185.log
$ diff tests/fixtures/captured_build_v185_leonardo.log tests/fixtures/planted_size_baseline_flash_regression_v185.log
84c84
< Flash: [========  ]  75.8% (used 24830 bytes from 32768 bytes)
---
> Flash: [========  ]  75.8% (used 25342 bytes from 32768 bytes)
$ diff ... | grep -c '^[<>]'
2
```

Exactly one changed line (the `Flash:` line), percentage/bar columns left as captured. `24830 + 512 = 25342`, the standing offset since Phase 123.

### Step 6 — Sever the four legs

Each of `test_clean_avr_all_three_envs_pass`, `test_clean_native_both_envs_pass`, `test_planted_flash_regression_flips_checker_to_failure`, `test_default_mode_is_unchanged_by_the_new_flag` was repointed onto the v185 generation (or, for the native leg, its literal case-count assertions updated in place) with a per-leg docstring paragraph naming Plan 185-01 as the severing plan, stating why the prior family would now be red, stating explicitly that the prior family is retired-not-repointed, and (in `test_clean_avr_all_three_envs_pass` and `test_default_mode_is_unchanged_by_the_new_flag`) carrying the reconciliation: predicted four red legs, observed four red legs, matching exactly, with `test_baseline_seam_precedence_flips_clean_log_to_fail` named explicitly as deliberately left on `captured_build_v153_leonardo.log` — 4 red + 1 deliberately untouched, not 5 red. No `#` comment line was added to any file (docstrings only); the module docstring gained no new section, and `tests/fixtures/README.md` was not touched (no new `## ` section).

### Step 7 — GREEN, then one commit (verbatim)

```
$ python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""
14 passed in 2.09s

$ python3 scripts/check_size_baseline.py --avr-log uno=tests/fixtures/captured_build_v185_uno.log \
    --avr-log uno328pb=tests/fixtures/captured_build_v185_uno328pb.log \
    --avr-log leonardo=tests/fixtures/captured_build_v185_leonardo.log \
    --native-log native=tests/fixtures/captured_test_native_summary.log \
    --native-log native_nodevtools=tests/fixtures/captured_test_native_nodevtools_summary.log
PASS: uno(flash=22734/32768,ram=1434/2048), uno328pb(flash=22778/32768,ram=1440/2048), leonardo(flash=24830/32768,ram=1875/2560), native(cases=185,suites=17), native_nodevtools(cases=185,suites=17)
```

Committed as `14be84c` (all of Steps 1-6 in one commit). After committing, `git status --porcelain` was empty and `python3 -m pytest tests/ -q -o addopts=""` reported **`360 passed`** (the whole-suite run requires a clean tree because `test_flash_path_record_sync.py` and the `test_requirement_case_mapping_v131.py`/`test_trace_segment_exhaustiveness_v131.py` modules assert repo porcelain as part of their own planted-mutation tests — a pre-commit run of the whole suite showed 5 unrelated failures purely from this plan's own uncommitted fixtures, all of which disappeared after the commit).

Comment-line count in `tests/test_check_size_baseline.py`: 20 before this task, **17 after** (decreased, not increased — three `#` lines inside the native leg's body were removed as part of the docstring rewrite; no new `#` comment was added anywhere).

## Task 2 Evidence (CLAIM-05 freeze proof, no-new-exemption re-proof)

`BASE_SHA=ec7c1bbd9768c58908a3cf1b3c15b7695036b3e6` (the firmware repo's HEAD before Task 1's commit, the literal sha, never a relative `HEAD~N`).

```
$ git diff --exit-code "$BASE_SHA" -- tests/fixtures/captured_build_v158_uno.log \
    tests/fixtures/captured_build_v158_uno328pb.log tests/fixtures/captured_build_v158_leonardo.log \
    tests/fixtures/planted_size_baseline_flash_regression_v158.log
(empty diff, exit 0)
```

All four frozen v158 paths are byte-unchanged against the base commit (not merely against the worktree). `planted_size_baseline_flash_regression_v158.log` — the v158 generation's planted sibling, not matched by the `captured_build_v158_*` glob — is retired in place by the same convention; its survival unchanged is deliberate, not an oversight.

```
$ git diff --exit-code "$BASE_SHA" -- scripts/check_size_baseline.py scripts/baseline/size_baseline_base01.json
(empty diff, exit 0)
```

`MERGE05_*_EXEMPTION_BYTES` count: **34 before, 34 after** (equal, non-zero; the grep pattern also matches usages, not only the four `_EXEMPTION_BYTES` constant definitions plus `PAGE_SIZE_SEAM_RAM`, but the count is what the plan's own `<fails_when>` compares before/after with the identical command).

```
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
    --avr-log uno=tests/fixtures/captured_build_v185_uno.log \
    --avr-log uno328pb=tests/fixtures/captured_build_v185_uno328pb.log \
    --avr-log leonardo=tests/fixtures/captured_build_v185_leonardo.log
PASS: uno(flash=22734/32768[-2090<=788=band64+exempt96+seam210+lock288+erase130],ram=1434/2048[-139<=2=seam2]), uno328pb(flash=22778/32768[-2096<=788=band64+exempt96+seam210+lock288+erase130],ram=1440/2048[-139<=2=seam2]), leonardo(flash=24830/32768[-2076<=724=band0+exempt96+seam210+lock288+erase130],ram=1875/2560[-139<=2=seam2])
(exit 0)
```

`--avr-log` only, no `--rebuild` (avoiding the mode-mismatch false red against BASE-01's frozen `native.cases=184`). Clean exit with headroom on all three targets — a shrink never needs an exemption.

```
$ python3 -m pytest tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption -q -o addopts=""
1 passed in 0.03s
```

No `merge05_*` or `planted_size_baseline_policy_*` fixture appears anywhere in this plan's firmware diff (`git diff --stat "$BASE_SHA" -- tests/fixtures/ | grep -E "merge05_|planted_size_baseline_policy_"` → no match).

## Decisions Made

See `key-decisions` in frontmatter. No architectural decisions were required; every step followed the plan's prescribed recipe exactly, and every capture matched RESEARCH.md's own falsification predictions.

## Deviations from Plan

None — plan executed exactly as written. The whole-suite pre-commit run showing 5 failures (all from repo-porcelain assertions tripped by this plan's own uncommitted fixtures) was expected and resolved by the plan's own Step 7 ordering (commit, then the whole suite is green); it is documented above under Step 7 rather than as a deviation, since no code or test was changed to address it — the fixtures were simply committed as the plan already required.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

The firmware size record now describes the tree that exists; CLAIM-04 and CLAIM-05 are both satisfied with every acceptance criterion evidenced above. Ready for plan 185-02 (the D-12 orphan-fixture disposition) and the rest of this phase's firmware/app/meta work. No blockers.

---
*Phase: 185-records-and-checks-that-are-current*
*Completed: 2026-09-11*
