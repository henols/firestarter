---
phase: 123-non-regression-baselines-gate-hardening
plan: 01
subsystem: build-measurement-baselines
tags: [platformio, baseline, avr-size, native-tests, milestone-branch]
dependency_graph:
  requires: []
  provides:
    - firestarter/scripts/baseline/size_baseline.json (BASE-01 recorded truth, consumed by 123-02/123-03)
    - firestarter/tests/fixtures/ (7 committed captures, consumed by 123-02/123-03/123-06)
    - v1.23-py32f071-integration branch in both sub-repos
  affects:
    - Phase 124 MERGE-05/MERGE-06 (baseline comparator input)
    - Phase 123 Plans 02, 03, 06 (comparator, warning gate, convention meta-test)
tech_stack:
  added: []
  patterns:
    - "meta + data JSON convention (firestarter_app/tools/baseline/dispatch_baseline.json analog)"
    - "captured_/planted_/clean_ fixture naming discipline"
key_files:
  created:
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/tests/fixtures/README.md
    - firestarter/tests/fixtures/captured_build_uno.log
    - firestarter/tests/fixtures/captured_build_uno328pb.log
    - firestarter/tests/fixtures/captured_build_leonardo.log
    - firestarter/tests/fixtures/captured_test_native_summary.log
    - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
    - firestarter/tests/fixtures/captured_native_warnings_excerpt.log
  modified: []
decisions:
  - "Recorded firmware_tree_sha as the fork-point SHA (5c9160a...), the actual HEAD at measurement time, not the later fixture-commit SHA — provenance reflects when pio actually ran, not when the JSON was committed"
  - "Documented, rather than fabricated, that `pio test` output never contains a literal 'Compiling .pio/build/...' line (that framing is pio-run-specific) — captured_native_warnings_excerpt.log uses pio test's real framing (Processing/Building) instead"
metrics:
  duration_minutes: 9
  completed: 2026-07-30
status: complete
---

# Phase 123 Plan 01: Milestone Branch Creation + BASE-01 Measured Baseline Summary

One-liner: Forked both sub-repos to `v1.23-py32f071-integration` off level `beta`, re-measured all six AVR flash/RAM figures and both native `{141,17}` pairs from a clean build, and recorded them plus the AVR-zero/native-360 warning policy into a load-bearing `size_baseline.json`.

## Fork Point SHAs

fork_point_firmware: 5c9160a34b665878b05403ab014b959926feb6bf
fork_point_host: e7d3ee8c8a41cd20e9159ab43b5cd969603d773e

## Branch Creation (Task 1)

Both repos were exactly level with `origin/beta` at execute time (re-verified, not assumed):

- `firestarter`: `git rev-list --left-right --count beta...origin/beta` → `0 0`
- `firestarter_app`: same → `0 0`

No fast-forward was needed. Neither `v1.23-py32f071-integration` branch existed beforehand. Created and checked out in both repos off `beta`, zero commits ahead of `origin/beta` at creation time (verified: `git log --oneline origin/beta..HEAD` empty in both). Meta repo remained on `gsd/v1.23-py32f071-integration` throughout, re-verified after both task commits.

Branch tip SHAs at creation (== fork points above):
- `firestarter`: `5c9160a34b665878b05403ab014b959926feb6bf`
- `firestarter_app`: `e7d3ee8c8a41cd20e9159ab43b5cd969603d773e`

No `git push` and no `gh` invocation occurred at any point in this plan.

## Measured Baseline (Task 2 + Task 3)

### AVR flash/RAM — clean rebuild, all reproduced byte-exact against ROADMAP/RESEARCH

| Env | Flash used | Flash free | RAM used | RAM free |
|-----|-----------:|-----------:|---------:|---------:|
| uno | 23932 | 8324 | 1573 | 475 |
| uno328pb | 23976 | 8408 | 1579 (new — never recorded before) | 469 |
| leonardo | 26072 | 2600 | 2014 | 546 |

All three AVR builds: **0 warnings of any kind** (verified via `grep -cE 'warning:'` on each captured build log).

### Native case/suite counts — both environments agree exactly

| Env | Cases | Suites | Result |
|-----|------:|-------:|--------|
| native | 141 | 17 | 141 succeeded, 0 failed/errored |
| native_nodevtools | 141 | 17 | 141 succeeded, 0 failed/errored |

`envs_agree: true` recorded in the JSON with the reason (no test references `DEV_TOOLS`/`CMD_DEV_*`; both `test_filter` blocks carry 17 identical entries) and the Phase 124 consequence (MERGE-06 satisfiable as worded, no amendment needed).

### Warning counting command and per-env output

Command: `pio test -e <env> 2>&1 | grep -cE 'warning: *"[^"]+" +redefined'` (macro-redefinition count), and `grep -cE 'warning:'` for the total.

- `native`: 360 total, 360 macro-redefinition (breakdown: 8 macros × 45 TUs each — `PSTR`, `memcpy_P`, `pgm_read_byte`, `pgm_read_dword`, `pgm_read_ptr`, `pgm_read_word`, `strcpy_P`, `strlen_P`)
- `native_nodevtools`: identical, 360/360

Recorded in the JSON as a `total_watermark` of 360 for each native env, explicitly characterised as pre-existing (present on `beta` at `5c9160a`) and not a regression, per the operator-locked Option A policy: `avr_rule == "== 0"`, `native_rule == "<= total_watermark"`.

### Native capture truncation point

Both `captured_test_native_summary.log` and `captured_test_native_nodevtools_summary.log` begin at the `SUMMARY` table header line (line 2802 of the full `pio test` output for each env) and run through the closing `================ 141 test cases: 141 succeeded ...` line (line 2822) — a 21-line verbatim tail. The truncation point is stated here explicitly per the plan's requirement; the omitted portion (lines 1–2801) is the per-suite compile/warning/PASSED narration, already covered separately by `captured_native_warnings_excerpt.log`.

### Firmware pytest count

`cd firestarter && python3 -m pytest tests/ -q` → **8 passed**, unchanged before and after this plan (this plan adds fixtures + JSON, no new test modules).

### Disagreement with RESEARCH cross-check figures

**None.** All six AVR figures and both native `{141,17}` pairs reproduced byte-exact against both the ROADMAP and the 123-RESEARCH.md measurements. The one figure RESEARCH itself flagged as never-previously-recorded (uno328pb RAM: 1579 B used / 469 B free) is now measured and recorded for the first time, matching RESEARCH's own measurement exactly.

## Deviations from Plan

### Auto-fixed / Adapted (Rule 1 — factual premise correction, D-03 spirit)

**1. `captured_native_warnings_excerpt.log` cannot contain the literal string "Compiling"**
- **Found during:** Task 2, while assembling the warning-excerpt fixture.
- **Issue:** The plan's action text (and 123-RESEARCH.md's general note about "pio wraps compiler output in its own framing, `Compiling .pio/build/...`") describes `pio run`'s framing. `pio test` uses a materially different framing (`Processing <suite> in <env> environment` / `Building...` / raw compiler invocation lines) and **never** emits a literal `Compiling` line. Verified exhaustively this session: default `pio test -e native`, `-v`, and `-vvv` against a from-scratch clean rebuild (`.pio/build/native` removed first) — zero occurrences of `Compiling` in any of the three invocations.
- **Fix:** Captured the excerpt using `pio test`'s real, verbatim framing instead (the `Processing`/`Building...`/include-chain lines immediately preceding a genuine `pgm_read_ptr` redefinition warning + its paired `note:` line), and documented the gap explicitly in `tests/fixtures/README.md` so a later reader does not mistake the absence of the word "Compiling" for an incomplete or hand-edited capture.
- **Files affected:** `firestarter/tests/fixtures/captured_native_warnings_excerpt.log`, `firestarter/tests/fixtures/README.md`.
- **Commit:** `1968128`
- **Note:** This does not affect the plan's `<verify><automated>` block for Task 2, which does not check for the string `Compiling` — only the prose `acceptance_criteria` mentioned it. All automated verification for Task 2 passed. Fabricating a `Compiling` line that pio never actually emits for `pio test` would have violated this entire phase's anti-fabrication premise, so the real framing was used and the gap recorded instead.

No other deviations. Every numeric acceptance criterion (all six AVR figures, both native `{141,17}` pairs, all warning counts, all `git ls-files` counts, the firmware pytest count) passed exactly as specified.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/scripts/baseline/size_baseline.json`
- FOUND: `/workspaces/firestarter/tests/fixtures/README.md`
- FOUND: `/workspaces/firestarter/tests/fixtures/captured_build_uno.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/captured_build_uno328pb.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/captured_build_leonardo.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/captured_test_native_summary.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log`
- FOUND: `/workspaces/firestarter/tests/fixtures/captured_native_warnings_excerpt.log`
- FOUND commit `1968128` (firestarter, Task 2 fixtures)
- FOUND commit `73382d2` (firestarter, Task 3 baseline JSON)
- Verified: `firestarter` and `firestarter_app` both on `v1.23-py32f071-integration`; meta on `gsd/v1.23-py32f071-integration`
- Verified: `git ls-files tests/fixtures/ scripts/baseline/` → 8 files
- Verified: `firestarter/tests/` pytest → 8 passed
- Verified: `git status --porcelain` clean in `firestarter` after both commits
