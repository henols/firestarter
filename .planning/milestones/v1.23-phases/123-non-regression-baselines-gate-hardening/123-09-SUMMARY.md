---
phase: 123-non-regression-baselines-gate-hardening
plan: 09
subsystem: testing
tags: [pytest, ast, fail-closed, fixtures, subprocess-testing, skip-census]

requires:
  - phase: 123-08
    provides: "All seven proxy-carrying host modules rekeyed onto tests/fw_presence.py's requires_fw; a single canonical FW_ABSENT_REASON string"
provides:
  - "tests/test_skip_census.py — BASE-03's skip census: subprocess full-suite run, fails on a firmware-absent skip while the sibling repo IS present, fails on any skip reason not on ALLOWED_SKIP_REASONS, no pinned count (D-10)"
  - "tools/check_no_exists_proxy.py — D-09's recurrence lint: AST-based scan forbidding the module-level absence-proxy idiom (simple and compound shape), scoped to module-level statements only"
  - "tests/fixtures/planted_no_exists_proxy.py — committed planted violation (both shapes plus one legitimate in-function check)"
  - "tests/test_check_no_exists_proxy.py — 8-test anti-hollow pairing for the recurrence lint"
affects: [123-11, "Phase 124 (any future gate author must run this lint clean)"]

tech-stack:
  added: []
  patterns:
    - "Skip census via subprocess full-suite run, parsed from pytest -rs short-summary lines, cached once per session via functools.lru_cache"
    - "Liveness signal derived from a --collect-only per-file count sum, NOT the run's trailing summary line (see Deviations — that line was measured to intermittently vanish under -q in this pytest 9.1.1 environment)"
    - "AST-based (not regex) source-scanning lint, scoped to ast.Module.body only so function-body existence checks are structurally invisible to the scan"
    - "Env-seam-without-default + is-not-None precedence + never-vacuous-before-missing-target guard ordering (check_permitted_claims.py lineage)"

key-files:
  created:
    - firestarter_app/tests/test_skip_census.py
    - firestarter_app/tools/check_no_exists_proxy.py
    - firestarter_app/tests/fixtures/planted_no_exists_proxy.py
    - firestarter_app/tests/test_check_no_exists_proxy.py
  modified: []

key-decisions:
  - "D-10 confirmed by direct measurement: 0 skips today on this tree (matches 123-RESEARCH.md's earlier 0-skip session, not the 3-skip session) — ALLOWED_SKIP_REASONS seeded with FW_ABSENT_REASON plus three OTHER pre-existing legitimate skip reasons found by static inspection (firestarter-CLI-not-on-PATH, meta-ledger-not-available, EVIDENCE.json-not-found) even though none fired in this local run, because two of the three are standalone-CI-only conditions that would otherwise trip test 2 the first time this census runs in GitHub Actions"
  - "Census liveness signal changed from the plan's literal 'parse a non-zero collected count from the run's summary line' to a --collect-only per-file count sum — measured this session that pytest 9.1.1 intermittently omits the trailing 'N passed in Xs' line from captured (non-interactive) stdout under -q, reproduced with/without --ignore and at both small and full (~1145-test) scale; the SKIPPED short-summary lines tests 1/2 depend on were unaffected, only the trailing completion line was"
  - "Recurrence lint scoped to ast.Module.body top-level statements only (never descending into FunctionDef/ClassDef) so an in-function existence check used for ordinary control flow is structurally invisible to the scan, verified against the fixture's legitimate_in_function_check and against the real post-rekey tests/ tree"
  - "Default target list is an explicit, literal 78-file enumeration of tests/*.py (never a glob/tree-walk), per this project's established house style (check_permitted_claims.py's five-file list) even though tests/fixtures/ would already be unreachable from a non-recursive glob — the discipline is kept explicit rather than relying on that non-recursion property"

requirements-completed: []

coverage:
  - id: D1
    description: "BASE-03 skip census: fails when a skip claims firmware-absent while the sibling repo is present, and when any skip reason is unrecognised"
    verification:
      - kind: unit
        ref: "tests/test_skip_census.py::test_no_skip_claims_firmware_absent_while_marker_present"
        status: pass
      - kind: unit
        ref: "tests/test_skip_census.py::test_every_skip_reason_is_allow_listed"
        status: pass
      - kind: manual_procedural
        ref: "planted a temporary skip with reason=FW_ABSENT_REASON, confirmed test 1 FAILs naming the offender, reverted, confirmed PASS again"
        status: pass
    human_judgment: false
  - id: D2
    description: "Census carries no skip marker of its own and asserts its own liveness (no pinned count)"
    verification:
      - kind: unit
        ref: "tests/test_skip_census.py::test_census_child_run_is_live"
        status: pass
      - kind: unit
        ref: "tests/test_skip_census.py::test_parser_recognises_a_real_skip"
        status: pass
      - kind: unit
        ref: "tests/test_skip_census.py::test_no_pinned_skip_count"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-09 recurrence lint (AST-based, simple + compound shape, legitimate-check exclusion, never-vacuous, fail-closed, precedence pin, syntax-error exit 2)"
    verification:
      - kind: unit
        ref: "tests/test_check_no_exists_proxy.py (8 tests, all pass)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Host half of MERGE-07's evidence recorded as a local run (49/0, 11-row gate table green, lint clean on real tree, 1158/0 host suite, gate trio green)"
    verification:
      - kind: manual_procedural
        ref: "Task 3 verification commands, all recorded verbatim below"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-07-31
status: complete
---

# Phase 123 Plan 09: Skip Census + Recurrence Lint Summary

**BASE-03's reason-allow-listed skip census (D-10, no pinned count) and D-09's AST-based recurrence lint against the module-level absence-proxy idiom, both proven against committed planted violations — host suite now 1158 passed, 0 skipped.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-07-31
- **Tasks:** 3 (2 code tasks + 1 verification-only task)
- **Files modified:** 4 created (test_skip_census.py, check_no_exists_proxy.py, planted_no_exists_proxy.py, test_check_no_exists_proxy.py)

## Accomplishments

- `firestarter_app/tests/test_skip_census.py` — BASE-03's census. Runs the full host suite (minus itself) as a subprocess, parses pytest `-rs` short-summary skip lines, and FAILs if any skip claims the firmware sibling is absent while `../firestarter/.git` is present (test 1), or if any skip reason is not on the committed `ALLOWED_SKIP_REASONS` allow-list (test 2). Carries no skip marker of its own; asserts its own liveness via a `--collect-only` count (test 3); proves its parser can actually see a real skip via a synthetic `tmp_path` probe (test 4); and asserts by source-scanning itself that it contains no pinned-count assertion (test 5, D-10).
- `firestarter_app/tools/check_no_exists_proxy.py` — D-09's recurrence lint. AST walk over `ast.Module.body` (top-level statements only) looking for a module-level assignment whose value is `not <expr containing a .exists() call>` — catching both the simple shape and the compound boolean-combination shape `test_dispatch_mirror.py` used before its Phase 123 Plan 08 rekey. Env seam `FIRESTARTER_PROXY_LINT_TARGETS` (list-valued, no default, `is not None` precedence), never-vacuous guard hoisted above the missing-target guard, explicit 78-file default target list (never a glob/tree-walk).
- `firestarter_app/tests/fixtures/planted_no_exists_proxy.py` — committed planted violation: `SIMPLE_ABSENCE_PROXY` (simple shape), `COMPOUND_ABSENCE_PROXY` (compound shape), and `legitimate_in_function_check()` (an in-function existence check that must NOT be flagged — proves scope discrimination).
- `firestarter_app/tests/test_check_no_exists_proxy.py` — 8-test anti-hollow pairing: clean control (real tree), simple-shape violation, compound-shape violation, legitimate-check exclusion, never-vacuous, fail-closed missing-target, precedence pin (argv wins over env seam), syntax-error exit 2.

## Task Commits

1. **Task 1: Write tests/test_skip_census.py** — `989c5b5` (test, firestarter_app submodule)
2. **Task 2: Write tools/check_no_exists_proxy.py + fixture + paired test** — `ccbc401` (feat, firestarter_app submodule)
3. **Task 3: Host-side verification set** — no file writes; results recorded below

## Files Created/Modified

- `firestarter_app/tests/test_skip_census.py` — BASE-03's skip census (5 tests)
- `firestarter_app/tools/check_no_exists_proxy.py` — D-09's AST-based recurrence lint
- `firestarter_app/tests/fixtures/planted_no_exists_proxy.py` — committed planted violation
- `firestarter_app/tests/test_check_no_exists_proxy.py` — 8-test anti-hollow pairing

## `ALLOWED_SKIP_REASONS`, as shipped

| Entry | Legitimacy comment |
|---|---|
| `FW_ABSENT_REASON` (imported from `tests.fw_presence`, never re-typed) | Legitimate only when `../firestarter/.git` is genuinely absent — BASE-03's whole assertion; test 1 enforces the "while present" half |
| `"firestarter entry point not found on PATH"` | `tests/test_characterization.py`'s `run_firestarter()` — legitimate only when `pip install -e .` was not run in this environment; CI installs the package first |
| `"meta-repo ledger not available at"` (prefix match) | `tests/test_audit_coverage_matrix.py` — legitimate only in a standalone checkout of `firestarter_app` with no meta-repo `.planning/` one level up (e.g. GitHub Actions cloning only this sub-repo); path is interpolated |
| `"EVIDENCE.json not found at"` (prefix match) | `tests/test_variant_decode_evidence_stability.py` — legitimate only when the meta-repo bench `EVIDENCE.json` artifact is absent (same standalone-checkout class); path is interpolated |

Matching is by `str.startswith`, not exact equality, because two of the four entries embed an interpolated path.

## Skip count observed (as an observation, not a pin)

The census's own child run reported **0 skips** on this tree today, matching `123-RESEARCH.md`'s earlier 0-skip session (not its 3-skip session — that 3→0 delta on the same tree with no code change is exactly why D-10 rejects a pinned count). This module never asserts a total count; `test_no_pinned_skip_count` asserts, by scanning its own source, that no such assertion exists.

## Recurrence lint PASS / FAIL output

**PASS (real tree, 78 files scanned):**
```
PASS: scanned 78 file(s) for the module-level absence-proxy idiom: tests/__init__.py, tests/conftest.py, tests/fw_presence.py, tests/scan_paths.py, ... (78 files total)
```

**FAIL (planted fixture):**
```
FAIL: 2 module-level absence-proxy violation(s):
  tests/fixtures/planted_no_exists_proxy.py:37: SIMPLE_ABSENCE_PROXY = not <...>.exists() -- key on the repo marker via tests/fw_presence.py instead
  tests/fixtures/planted_no_exists_proxy.py:43: COMPOUND_ABSENCE_PROXY = not <...>.exists() -- key on the repo marker via tests/fw_presence.py instead
```

## Host suite count

`python3 -m pytest tests/` (from `/workspaces/firestarter_app`): **1158 passed, 0 skipped** (1145 baseline + 5 census tests + 8 lint tests).

## mypy watermark

`python tools/check_mypy_watermark.py`: **1 error** (watermark 35) — 34 below watermark, unchanged by this plan.

## Task 3 — host-side verification set (local evidence, not CI coverage)

**⚠ `ci.yml` performs a single checkout with no firmware sibling.** Every result below was gathered locally, inside this devcontainer, where the meta-repo and the sibling `firestarter` checkout are both present. None of it is continuously CI-covered — that qualification is D-05's, and it must be carried forward into 123-11 and Phase 124 rather than reported as CI coverage.

1. **Seven proxy modules (`-rs`):** `49 passed in 0.69s` — 0 skips. This is the number BASE-03 exists to keep at zero for firmware-absent reasons.
2. **Eleven-row cross-repo gate set** (per `122-NONREGRESSION.md` §3 — belongs to **MERGE-07's nine-gate set**, C-8's smaller population):
   - `tools/check_no_log_in_sdp_window.py` → `PASS: no logging call in SDP timing window (.../eeprom_28c.cpp, emitter lines 298-314, completion-poll lines 348-361)` — exit 0
   - `tools/check_is_memory_cmd_no_ifdef.py` → `PASS: is_memory_cmd() has no preprocessor conditional and enumerates exactly the eight expected commands` — exit 0
   - `tools/check_dispatch.py` → `PASS: all 746 chips scanned; 736 supported; 10 chips confirmed non-dispatchable; 0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations` — exit 0
   - `tools/check_devtest_orchestrator.py` → `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)` — exit 0
   - `tools/gen_sdp_bus_config.py` idempotence (`tests/test_sdp_bus_config_drift.py::test_codegen_produces_byte_identical_output`): PASS, part of `tests/test_sdp_bus_config_drift.py` → **4 passed**
   - `tests/test_check_dispatch_invariants.py` → **12 passed**
   - `tests/test_check_devtest_orchestrator.py` → **16 passed**
   - `tests/test_check_is_memory_cmd_no_ifdef.py` → **6 passed**
   - `tests/test_check_no_log_in_sdp_window.py` → **7 passed**

   All eleven rows (4 tool invocations + 1 idempotence check + 6 pytest module runs, per `122-NONREGRESSION.md`'s counting — see that document for the exact row-to-artifact mapping) executed and passed.
3. **`python3 tools/check_no_exists_proxy.py`** (real tree): exit **0**, `PASS: scanned 78 file(s)...`.
4. **`python3 -m pytest tests/test_scan_paths_resolve.py tests/test_skip_census.py tests/test_fw_presence.py`**: **16 passed**, all green.
5. **`python3 -m pytest tests/`**: **1158 passed, 0 skipped**.
6. **Gate trio:** `ruff check firestarter/ tests/` → All checks passed. `ruff format --check firestarter/ tests/` → 104 files already formatted. `python tools/check_mypy_watermark.py` → 1 error (watermark 35), 34 below watermark.
7. **`git status --porcelain`** (inside `firestarter_app`): matches the recorded pre-existing dirt exactly (`M .gitignore`; untracked `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) — no tracked file changed by this plan beyond the four files this plan created and committed.

**C-8 distinction, recorded for Phase 124:** the eleven-row table above represents **nine gates** (MERGE-07's population); `tests/test_gen_validation_header.py` contributes paths to D-11's larger cross-repo scan-path inventory (`tests/scan_paths.py`) but is **absent** from this eleven-row table — do not conflate the two populations.

## Decisions Made

- **D-10 seeding:** `ALLOWED_SKIP_REASONS` was seeded with all four known-legitimate reasons present in this codebase's source (not only the ones that fired in this local run, which was 0-skip) — the two standalone-CI-only reasons (`test_audit_coverage_matrix.py`, `test_variant_decode_evidence_stability.py`) would otherwise trip the census's "every reason allow-listed" test the first time it runs in GitHub Actions, where the meta-repo is genuinely absent.
- **Liveness signal changed from the plan's literal wording** ("a non-zero collected count parsed from its summary line") **to a `--collect-only` per-file count sum** — see Deviations below for the measured reason.
- **Default lint target list is a literal 78-entry enumeration**, not a glob, following this project's established house style (`check_permitted_claims.py`), even though `tests/fixtures/` is already unreachable from a non-recursive glob.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Census liveness signal switched from the run's trailing summary line to a `--collect-only` count sum**
- **Found during:** Task 1, while implementing `test_census_child_run_is_live`
- **Issue:** The plan specified parsing "a non-zero collected count parsed from its summary line" from the full subprocess run's pytest output. Measured repeatedly this session: this pytest 9.1.1 environment intermittently omits the trailing `"N passed in Xs"` summary line from captured (non-interactive, `capture_output=True`) stdout under `-q` — reproduced with and without `--ignore`, on both a 2-file selection and the full ~1145-test suite, both via file redirection and piped capture. The `SKIPPED [...]` short-summary lines tests 1/2 depend on were unaffected — only the trailing completion line vanished. Depending on it for liveness would have made the census itself exactly as flaky as D-10 rejects a pinned count for being.
- **Fix:** Added a `--collect-only -q` run (already needed to prove the `--ignore` deselect took effect) and parse its per-file `"tests/test_foo.py: N"` count lines, summing them for the liveness signal. Verified reproducibly identical (1145) across three repeated invocations, matching the known baseline exactly.
- **Files modified:** `firestarter_app/tests/test_skip_census.py`
- **Verification:** `test_census_child_run_is_live` passes; the module docstring records the measurement and rationale in detail so a future reader does not "fix" this back to the flaky approach.
- **Committed in:** `989c5b5` (Task 1 commit)

**2. [Rule 1 - Bug] Self-matching regex in the no-pinned-count test**
- **Found during:** Task 1, writing `test_no_pinned_skip_count`
- **Issue:** The pattern designed to detect a pinned-skip-count assertion (`skip\w*...(?:==|!=)\s*\d+`) textually matched its OWN raw-string literal when scanning the module's full source text, since the pattern definition itself contains the word "skip" within 40 characters of a literal `==`.
- **Fix:** Added `_source_excluding_own_pattern_definition()`, which excises the pattern's own definition (identified by unique start/end marker strings, not a line count) from the scanned source before the check runs.
- **Files modified:** `firestarter_app/tests/test_skip_census.py`
- **Verification:** `test_no_pinned_skip_count` passes; the self-match is documented inline above the pattern definition.
- **Committed in:** `989c5b5` (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs found and fixed during implementation, no scope creep beyond making the two new tests actually correct).
**Impact on plan:** Both fixes were necessary for the census and lint to be genuinely non-flaky and non-vacuous, which is the entire point of this plan. No architectural change; no new files beyond the four the plan specified.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- BASE-03 (skip census) and D-09 (recurrence lint) are both implemented and proven against planted violations, ready for 123-11 to tick the requirement.
- This plan ticks **nothing** per its own spec — BASE-03 and BASE-08 close only in 123-11.
- Host suite stands at 1158 passed, 0 skipped; gate trio green; meta repo unaffected (still on `gsd/v1.23-py32f071-integration`).
- Phase 124 inherits both: any new gate it writes must pass `tools/check_no_exists_proxy.py`, and any new skip it introduces must earn a deliberate `ALLOWED_SKIP_REASONS` entry.

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: firestarter_app/tests/test_skip_census.py
- FOUND: firestarter_app/tools/check_no_exists_proxy.py
- FOUND: firestarter_app/tests/fixtures/planted_no_exists_proxy.py
- FOUND: firestarter_app/tests/test_check_no_exists_proxy.py
- FOUND commit: 989c5b5
- FOUND commit: ccbc401
