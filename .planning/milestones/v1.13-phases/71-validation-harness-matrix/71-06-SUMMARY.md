---
phase: 71-validation-harness-matrix
plan: "06"
subsystem: validation-harness-tier3-runner
tags:
  - validation
  - cli
  - oracle
  - harn-01
  - harn-02
  - harn-03
dependency_graph:
  requires:
    - 71-02
  provides:
    - dev validate-family subcommand (HARN-01 Tier-3 / D-05)
    - SKIP-deferred exit 0 path (D-06)
    - Non-vacuous PASS oracle (HARN-03 / D-08)
    - validation-matrix.{json,md} results artifact emitter (HARN-02 / D-02)
    - test_validate_family_cmd.py
    - test_matrix_artifact.py
    - test_validate_oracle.py
  affects:
    - firestarter_app/firestarter/cli_handlers.py (new dev subcommand)
    - firestarter_app/tests/ (3 new test files, 44 new tests)
tech_stack:
  added:
    - _emit_skip_deferred_artifact / _write_artifact / _render_markdown helpers
    - _classify_sha_result oracle (Leonardo authoritative vs advisory)
    - _check_r1_precondition (r1 ≈ 270000 ±25%)
    - _EVIDENCE_SHA_SOFTWARE_SENTINEL (tier-software-no-file sentinel)
  patterns:
    - dev subcommand composing cycle methods (D-10 reuse-not-reimpl)
    - SKIP-deferred pattern (D-06 — exit 0 with deferred cells)
    - 3-way verdict (0/1/2) preserved throughout
    - validation-matrix.{json,md} hyphenated artifact (Pitfall 4 / D-02)
key_files:
  created:
    - firestarter_app/tests/test_validate_family_cmd.py
    - firestarter_app/tests/test_matrix_artifact.py
    - firestarter_app/tests/test_validate_oracle.py
  modified:
    - firestarter_app/firestarter/cli_handlers.py (new dev validate-family subcommand + helpers)
    - firestarter_app/tests/__snapshots__/ (dev --help snapshot updated)
decisions:
  - D-05 honored: new subcommand under existing dev group, composes cycle methods (no re-impl)
  - D-06 honored: SKIP-deferred cells + exit 0 when no port/board/chip/source
  - D-02 honored: emitted results artifact (validation-matrix.json, hyphens) distinct from
    authored spec (validation_matrix_spec.json, underscores)
  - D-08 honored: Leonardo-only authoritative PASS; r1 ±25% precondition; uno328pb hard N/A;
    negative control (SHA mismatch → FAIL); retry_count in cell
  - D-10 honored: write_cycle_eprom + consistency_check_eprom composed, not re-implemented
  - Oracle helper functions (_classify_sha_result, _check_r1_precondition) exported from
    cli_handlers.py at module level for direct test access (no monkey-patching needed)
  - r1 value read from ConfigManager key "r1" (mocked in tests via set_value); Phase 73
    will wire the live hardware readback via HardwareManager.set_hardware_config GET path
  - uno328pb guard fires on board= argument, before any chip resolution
metrics:
  duration: ~25min
  completed: 2026-06-16
  tasks_completed: 2
  tasks_total: 2
  files_created: 3
  files_modified: 2
---

# Phase 71 Plan 06: dev validate-family Runner + Oracle Summary

**One-liner:** `dev validate-family` Tier-3 runner composes cycle methods,
records SKIP-deferred at no-hardware, emits `validation-matrix.{json,md}` artifact,
and bakes in the non-vacuous PASS oracle (Leonardo-only, r1 precondition, uno328pb N/A).

## What Was Built

### Task 1: dev validate-family subcommand + SKIP-deferred + artifact

**firestarter_app/firestarter/cli_handlers.py** — New `@dev.command(name="validate-family")`
subcommand under the existing `dev` Click group:

**SKIP-deferred path (D-06):** When `app.config_manager.get_value("port")` is None or
`--board/--chip/--source` are absent, the handler calls `_emit_skip_deferred_artifact()`
which writes `validation-matrix.json` and `validation-matrix.md` with all Tier-3 cells as
`SKIP-deferred` (from `tier3.boards`) and `N/A` (from `tier3.skip_boards`), then `sys.exit(0)`.
Milestone remains closeable at partial bench coverage.

**Hardware path:** Reads `validation_matrix_spec.json` for the target family/families;
composes `write_cycle_eprom` (D-10 reuse-not-reimpl) with `runs=1`; maps 3-way verdict
(0=PASS, 1=FAIL, 2=hw-error) into the artifact cell; emits `validation-matrix.{json,md}`.

**Oracle helpers (module-level, all typed):**
- `_classify_sha_result(readback_sha, source_sha, board)` — Leonardo yields
  `verdict=PASS/FAIL + pass_type=authoritative`; other boards yield `advisory`
- `_check_r1_precondition(r1_value)` — True if `202500 ≤ r1 ≤ 337500`
- `_emit_skip_deferred_artifact(families, output_dir, reason)` — writes artifact
- `_write_artifact(cells, output_dir)` — writes `validation-matrix.json` + `.md`
- `_render_markdown(cells)` — Markdown table renderer

**Artifact schema:** `{"generated": "…", "harness_version": "71", "cells": [...]}`
Each cell: `{family, board, tier, verdict, evidence_sha, retry_count}` (± reason).
File name: `validation-matrix.json/.md` (hyphens — distinct from authored
`validation_matrix_spec.json`, underscore — Pitfall 4 / D-02 compliance).

**Tests:**
- `test_validate_family_cmd.py`: 13 tests — SKIP-deferred exit 0, artifact emitted,
  cells SKIP-deferred or N/A, schema fields present, .md emitted, all-6-families, hyphenated
  naming, authored spec not written, write_cycle called/not-called per path
- `test_matrix_artifact.py`: 13 tests — schema (generated/harness_version/cells), per-cell
  fields (family/board/tier/verdict/evidence_sha/tier-is-int), verdict vocabulary, .md table
  header, SKIP-deferred in .md, hyphen naming, authored spec not written

### Task 2: Non-vacuous PASS oracle tests (HARN-03 / D-08)

All oracle functions were implemented in Task 1 (the handler is one unit). Task 2 adds the
dedicated test file proving the oracle properties:

**test_validate_oracle.py** — 18 tests covering:

| Acceptance Criteria | Test | Result |
|---------------------|------|--------|
| Negative control: mismatch → FAIL | `test_classify_sha_mismatch_is_fail_on_leonardo` | PASS |
| write_cycle returning 1 → exit 1 | `test_negative_control_write_cycle_returns_fail` | PASS |
| uno328pb → N/A verdict | `test_uno328pb_write_cell_is_na` | PASS |
| uno328pb → no cycle invoked | `test_uno328pb_no_write_cycle_called` | PASS |
| r1=1000 → exit 2, no cycle | `test_r1_precondition_aborts_before_cycle` | PASS |
| r1=270000 → cycle proceeds | `test_r1_in_band_allows_cycle` | PASS |
| Leonardo SHA match → authoritative | `test_leonardo_sha_match_is_authoritative_pass` | PASS |
| Other board SHA match → advisory | `test_other_board_sha_match_is_advisory` | PASS |
| Other board SHA mismatch → advisory | `test_other_board_sha_mismatch_is_advisory_not_fail` | PASS |
| retry_count present in all cells | `test_retry_count_present_in_skip_deferred_cell` | PASS |
| retry_count=1 for hardware run | `test_retry_count_is_1_for_hardware_run` | PASS |

## Verification Results

```
pytest tests/test_validate_family_cmd.py tests/test_validate_oracle.py \
       tests/test_matrix_artifact.py -x -q
44 passed, 33 warnings

ruff check firestarter/cli_handlers.py tests/test_validate_family_cmd.py \
           tests/test_matrix_artifact.py tests/test_validate_oracle.py
All checks passed!

ruff format --check firestarter/cli_handlers.py tests/test_validate_family_cmd.py \
            tests/test_matrix_artifact.py tests/test_validate_oracle.py
4 files already formatted

python -m mypy firestarter/cli_handlers.py
Success: no issues found in 1 source file

pytest tests/ --cov=firestarter --cov-fail-under=70 -q
Total coverage: 76.85%   (29 snapshots pass)

python tools/check_dispatch.py
PASS: all 744 chips scanned; exit 0
```

## Commits

| Submodule       | Hash    | Subject |
|-----------------|---------|---------|
| firestarter_app | 824cab8 | test(71-06): add failing tests for dev validate-family + artifact schema |
| firestarter_app | 0cb6c90 | feat(71-06): add dev validate-family subcommand with SKIP-deferred + artifact |
| firestarter_app | ae1d1cf | test(71-06): add oracle tests — negative control, uno328pb N/A, r1 precondition |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Test clarification] SKIP-deferred test assertion broadened for uno328pb**

- **Found during:** Task 1 GREEN phase
- **Issue:** Test `test_artifact_cells_are_skip_deferred` asserted ALL Tier-3 cells
  have verdict `SKIP-deferred`. The spec emits `N/A` for `tier3.skip_boards` (uno328pb),
  which is the correct behavior per D-08 oracle.
- **Fix:** Broadened assertion to accept `{"SKIP-deferred", "N/A"}` as both valid deferred
  verdicts; added a positive assertion that at least one `SKIP-deferred` cell exists.
- **Files modified:** `tests/test_validate_family_cmd.py`

**2. [Rule 2 - Snapshot update] test_characterization.py help snapshot updated**

- **Found during:** Task 1 full-suite run
- **Issue:** The `test_help_dev` characterization snapshot captured the old help text
  (4 dev subcommands). Adding `validate-family` changed the snapshot.
- **Fix:** Updated snapshot via `--snapshot-update` (expected deviation when adding a
  CLI command).
- **Files modified:** `tests/__snapshots__/`

**3. [Rule 1 - Ruff fix] Unused `patch` import removed from oracle test file**

- **Found during:** Task 2 ruff check
- **Issue:** `from unittest.mock import Mock, patch` — `patch` was unused.
- **Fix:** Removed `patch` from import.
- **Files modified:** `tests/test_validate_oracle.py`

## TDD Gate Compliance

**Task 1:**
- RED gate: `test(71-06): add failing tests for dev validate-family + artifact schema` (824cab8) — all tests fail with "No such command validate-family"
- GREEN gate: `feat(71-06): add dev validate-family subcommand with SKIP-deferred + artifact` (0cb6c90) — 26 tests pass

**Task 2:**
- Oracle tests pass immediately because the oracle functions were implemented as part of
  Task 1 (the handler is one logical unit). The test file `test_validate_oracle.py` is the
  TDD "test" commit for Task 2; it exercises oracle rules encoded in Task 1's implementation.
- GREEN gate: `test(71-06): add oracle tests — negative control, uno328pb N/A, r1 precondition` (ae1d1cf)

## Known Stubs

**r1 hardware readback path:** In Phase 71 (software scaffold), the r1 value is read from
`app.config_manager.get_value("r1", None)`. This is a software stub — the live hardware path
(reading r1 from the board via `HardwareManager.set_hardware_config()` GET → `MSG_OK_CFG
params[0]`) is not wired yet. Phase 73 (HIL evidence) will wire the live r1 readback.

The stub is intentional and documented. The precondition guard logic is fully tested via mocked
r1 values in `test_validate_oracle.py`. No impact on Phase 71 objectives.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| T-71-VACUOUS mitigated | cli_handlers.py `_classify_sha_result` | SHA mismatch → FAIL on Leonardo (test_negative_control confirms) |
| T-71-WRONGBOARD mitigated | cli_handlers.py `_classify_sha_result` | Non-Leonardo boards yield advisory, not authoritative PASS |
| T-71-UNO328 mitigated | cli_handlers.py `dev_validate_family` | uno328pb hard N/A guard before any write cycle |
| T-71-STALECAL mitigated | cli_handlers.py `_check_r1_precondition` | r1 ±25% check aborts before write if out-of-band |
| T-71-FORGE mitigated | cli_handlers.py `_validation_spec_path` | Artifact is only written (never read back as input); authored spec is never written by runner |

## Self-Check: PASSED

Files created:
- firestarter_app/tests/test_validate_family_cmd.py ✓
- firestarter_app/tests/test_matrix_artifact.py ✓
- firestarter_app/tests/test_validate_oracle.py ✓

Files modified:
- firestarter_app/firestarter/cli_handlers.py ✓ (dev validate-family + helpers)
- firestarter_app/tests/__snapshots__/ ✓ (dev --help snapshot)

Commits:
- firestarter_app@824cab8 ✓
- firestarter_app@0cb6c90 ✓
- firestarter_app@ae1d1cf ✓

Verification:
- 44 tests pass (test_validate_family_cmd + test_matrix_artifact + test_validate_oracle) ✓
- ruff check: All checks passed ✓
- ruff format --check: 4 files already formatted ✓
- mypy: Success: no issues found ✓
- Coverage: 76.85% ≥ 70% ✓
- check_dispatch.py: exit 0 ✓
- 29 snapshots pass ✓
