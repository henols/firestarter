---
phase: 138
slug: preconditions-baseline
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-08
---

# Phase 138 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `138-RESEARCH.md` §"Validation Architecture" (all figures measured live 2026-08-08).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware native)** | PlatformIO **Unity** (`test_framework = unity`), 3 native envs |
| **Framework (firmware gates)** | **pytest** (stdlib + pytest only; **no `conftest.py` anywhere** — house rule) |
| **Framework (host)** | **pytest** + `pytest-cov` + snapshot plugin, `addopts = "-ra -q"`, `testpaths = ["tests"]` |
| **Config file** | `firestarter/platformio.ini` · `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` → **221 passed, 8.8 s** |
| **Full suite command** | `pio test -e native` · `-e native_nodevtools` · `-e native_pinmap_provisional` (≈50 s each warm); host: `cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | ~9 s firmware gates · ~150 s three native envs · ~179 s host suite |

**Interpreter constraint (blocking, recorded trap):** the host suite MUST run under
`.venv/ci-replica/bin/python` (**3.11.15**). The devcontainer's ambient **3.12.13** masks the app's
py39/3.11 CI. Do not substitute.

**Count-line constraint:** host `addopts` is `-ra -q`; adding another `-q` suppresses the count line.
Always pass `-o addopts=""` when the count itself is the measurement.

**Directory-name constraint:** two host tests resolve `_HERE.parent.parent / "firestarter_app"` and
FAIL if the checkout directory is named anything else
(`tests/test_gen_validation_header.py::test_validate_spec_called_before_emission`,
`tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing`).

---

## Sampling Rate

- **After every task commit:** Run the narrowest thing that can go RED — the gate or single pytest
  module the task touched (`python3 scripts/check_size_baseline.py …`, or
  `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q`)
- **After every plan wave:** `pio test -e native && pio test -e native_nodevtools && pio test -e native_pinmap_provisional`
  plus `python3 -m pytest tests/ -q` (firmware waves); full host suite (host waves)
- **Before `/gsd-verify-work`:** every gate green **and** the three native envs at their recorded
  counts **and** the new fixture's identity module green
- **Max feedback latency:** 60 seconds for per-task sampling (single gate or single pytest module)

**Documented exception — firmware cold-build tasks.** Six tasks verify a property that *is* the cold
build, so a faster substitute would not prove the thing being measured. These are bounded by the
**540000 ms** build timeout the Cold Measurement Protocol requires, not by the 60-second default:

| Plan | Tasks | Why the cold build is the measurement |
|------|-------|----------------------------------------|
| `138-03` | T1, T2, T3 | `rm -rf .pio/build/ENV` then a single `pio test -e ENV` — the flag-off proof (141 cases / 17 suites on both pinned envs) and the trace env's first runs must not read a warm cache |
| `138-05` | T1, T3 | The frozen-array assertion and the whole-firmware green-state re-establishment across all four native envs |
| `138-06` | T1 | `pio run -t clean -e ENV` then a single `pio run -e ENV` for the three AVR targets, plus cold native runs — the warning watermark is contaminated by a warm cache (a worked correction is on file) |

The 60-second default remains in force for every other task in the phase, including every python gate,
every single pytest module, and every git or `gh` read. A default two-minute shell timeout truncates a
cold toolchain build mid-compile while still leaving a parseable partial log, which is why the exception
raises the bound rather than lowering the expectation.

---

## Per-Task Verification Map

> Populated by the planner/executor as tasks are authored. Requirement → command mapping below is
> fixed by research; the Task ID / Plan / Wave columns fill in from the PLAN.md files.
> All ten rows below were measured, not assumed — see `138-BASELINE.md` §§3-6 for the live figures
> each row's command actually produced.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| Task 1 | 138-01 | 1 | PREP-01 | — | N/A | integration (git/gh) | `gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit` + `comm -23` of both `git ls-tree -r --name-only` lists + restricted `git diff --stat` | ✅ (`138-BRANCH-BASES.md` §1-2) | green |
| Task 2 | 138-01 | 1 | PREP-02 | — | N/A | integration (git) | `git rev-parse <branch>` + `git merge-base --is-ancestor <base> <branch>` per repo | ✅ | green |
| Task 1 | 138-06 | 4 | PREP-03 (AVR size) | — | N/A | unit (gate) | `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` | ✅ | green (exit 0, `138-BASELINE.md` §5) |
| Task 1 | 138-06 | 4 | PREP-03 (native counts) | — | N/A | unit (gate) | same script, `--native-log native=… --native-log native_nodevtools=…` | ✅ | green (exit 0) |
| Task 1 | 138-06 | 4 | PREP-03 (warnings) | — | N/A | unit (gate) | `python3 scripts/check_build_warnings.py --log <env>=<log>` | ✅ | green (exit 0, all watermarks matched exactly) |
| Task 1 | 138-05 | 3 | PREP-03 (fixture immutability) | — | N/A | unit (pytest) | `python3 -m pytest tests/test_golden_trace_identity_eprom_v131.py -q` | ✅ (delivered this phase — was **W0**) | green (6/6 passed; non-vacuity proven on 3 planted breaks) |
| Task 1 | 138-05 | 3 | PREP-03 (trace content) | — | N/A | unit (Unity) | `pio test -e native_trace_v131` | ✅ (delivered this phase — was **W0**) | green (5/5 cases, full ordered positional equality) |
| Task 1 | 138-06 | 4 | PREP-03 (flag-off byte-exactness) | — | N/A | integration | `pio test -e native && pio test -e native_nodevtools` → re-assert 141/17/all-PASSED via the gate | ✅ | green (141/17 both envs, cold) |
| Task 1 | 138-04 | 2 | PREP-03 (host counts) | — | N/A | integration | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` | ✅ | green (1539 passed, 0 skipped, 0 failed) |
| Task 3 | 138-02 | 1 | PREP-04 | — | N/A | unit (script, self-checking) | `python3 .planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | ✅ (delivered this phase — was **W0**) | green (exit 0, VIOLATIONS: 0; observed FAIL on a planted input first) |

*Status: pending · green · red · flaky. All ten rows are green — no row required a red/flaky
disposition, so §"Wave 0 Requirements"/frontmatter below reflect an all-green map.*

---

## Wave 0 Requirements

All nine items below were delivered across Plans 138-02/03/05/06/07 (none left unticked — every
MISSING reference this phase identified at planning time was closed by execution):

- [x] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — additive `HOST_STUBS_RECORD_TIMING`
      block (storage + `timing_push` + accessors) plus the `HOST_STUBS_CUSTOM_READ_DATA_BUFFER` (R2)
      opt-out guard — delivered Plan 138-03 Task 1; both pinned native envs re-confirmed at 141/17 cold
      (Plan 138-06) — covers PREP-03
- [x] `firestarter/test/native/avr/_shared/eprom_v131_expected.h` — comparator delivered Plan 138-03
      Task 2; the three frozen arrays (198/221/201 entries) delivered Plan 138-05 Task 1 — covers
      PREP-03
- [x] `firestarter/test/native/avr/test_trace_eprom_v131/{host_stubs.cpp,test_trace_eprom_v131.cpp}` —
      the new suite, incl. `reset_register_cache` and the pulse-counting read-back model — delivered
      Plan 138-03 Tasks 2-3, switched to full positional equality Plan 138-05 Task 1
- [x] `firestarter/platformio.ini` — `[env:native_trace_v131]` (1-entry `test_filter`, matching `-I`,
      **not** in `default_envs`) — delivered Plan 138-03 Task 2; measured cold at 5/1 PASSED (Plan
      138-06)
- [x] `firestarter/tests/golden/eprom_v131_trace_inventory.json` +
      `firestarter/tests/test_golden_trace_identity_eprom_v131.py` — delivered Plan 138-05 Task 2,
      6/6 passed, non-vacuity proven on 3 independent planted breaks (Plan 138-05 Task 3)
- [x] `firestarter/scripts/baseline/size_baseline_v131.json` — new immutable freeze (BASE-01 schema) —
      delivered Plan 138-06 Task 2, verified green through `check_size_baseline.py`'s/
      `check_build_warnings.py`'s existing `--baseline` seam
- [x] `.planning/phases/138-preconditions-baseline/138-BASELINE.md` — narrative artifact in
      `131-CI-BASELINE.md` shape — delivered this plan (138-07), Tasks 2-3, ten sections
- [x] `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` + its committed verbatim
      output artifact — delivered Plan 138-02 Tasks 1-3, observed FAILing on a planted input before
      its passing runs were trusted — covers PREP-04
- [x] No framework install needed — Unity, pytest, and the CI-parity venv all exist — confirmed true
      throughout: zero package-manager installs occurred anywhere in this phase (all six prior plans'
      own SUMMARY.md files record "None" under User Setup Required for this reason)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions | Result |
|----------|-------------|------------|-------------------|--------|
| CI run dispatched per repo, run id recorded | PREP-03 (D-06) | `gh workflow run` is blocked by the auto-mode classifier — a dispatch is inherently an operator action. Read-only `gh run view` / `gh api` work fine. | Operator dispatches the workflow; agent reads the run **read-only** and records the run id, plus `outcome`-vs-`conclusion` per step, in `138-BASELINE.md`. Firmware CI is **not** dispatchable (source-level fact); app CI is. | **Done.** Operator pushed all three branches and dispatched the app's `ci.yml`; three runs recorded read-only in `138-BASELINE.md` §§1-2 — firmware runs `31299694430`/`31299694466` (push-produced), app run `31300205900` (dispatch-produced), all `conclusion: success`. |
| Cold-build measurement discipline | PREP-03 (D-06) | A default 2-minute Bash timeout truncates the toolchain build mid-compile and silently contaminates the figure. Automatable only with an explicit extended timeout. | `rm -rf .pio/build/<env>` then a **single** `pio` invocation with an extended timeout. Never guess a figure down from prose or a warm re-run. Warm figures are contamination (998 vs 1166 reproduced this trap live). | **Done.** Plan 138-06 Task 1 ran every AVR target and native env cold at a 540000 ms timeout; figures recorded in `138-06-FIRMWARE-MEASUREMENT.md` and cited in `138-BASELINE.md` §5. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s (the six documented cold-build exceptions above stayed within their own
      540000 ms bound, per this file's own "Documented exception" carve-out, and are not a violation of
      the 60 s default that governs every other task)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved — 2026-08-09, Phase 138 Plan 07 Task 3. All ten per-task verification map rows
above are measured green; no row is red, so both `nyquist_compliant` and `wave_0_complete` are set
`true` in this file's frontmatter, per this plan's own conditional instruction ("only if every map row
is green"). See `138-BASELINE.md` §§3-6 for the underlying figures each row's command produced.
