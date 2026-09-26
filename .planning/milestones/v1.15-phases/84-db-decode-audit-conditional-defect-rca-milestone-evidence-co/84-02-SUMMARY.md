---
phase: 84-db-decode-audit-conditional-defect-rca-milestone-evidence-co
plan: "02"
subsystem: firestarter_app
tags: [sram, blank-check, host-guard, D-30, FIX-01, tdd]
dependency_graph:
  requires: []
  provides: [D-30-host-guard, SRAM-blank-check-short-circuit]
  affects: [firestarter_app/firestarter/eprom_operations.py]
tech_stack:
  added: []
  patterns: [host-short-circuit, class-constant-frozenset, early-return-before-context-manager]
key_files:
  created: []
  modified:
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_eprom_operations.py
decisions:
  - "D-30: SRAM/FRAM blank-check short-circuit implemented in check_eprom_blank() via class constant _SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29}); detection is OR of electrical-type SRAM/FRAM and protocol-id membership"
  - "Short-circuit fires BEFORE _operation_context is entered, so no command reaches the firmware (0xA4 MSG_ERR_EMPTY_INPUT prevented at the host boundary)"
  - "No new message constant added to messages.py (State-of-the-Art constraint honored); plain logger.warning used"
  - "Wire protocol and firmware unchanged (D-11/D-30 bound)"
metrics:
  duration: "9 minutes"
  completed: "2026-06-25T09:09:32Z"
  tasks_completed: 3
  files_changed: 2
---

# Phase 84 Plan 02: SRAM/FRAM Blank-Check Host Short-Circuit Summary

**One-liner:** Host SRAM/FRAM blank-check short-circuit in `check_eprom_blank()` via `_SRAM_PROTO_IDS` frozenset, preventing firmware 0xA4 MSG_ERR_EMPTY_INPUT for FM1608 and all SRAM families.

## What Was Built

Closed D-30 (FIX-01 host half): FM1608 and all SRAM/FRAM chips routed through `configure_sram()` would surface `0xA4 MSG_ERR_EMPTY_INPUT` when `firestarter blank <chip>` was called, because `configure_sram()` leaves a NULL `firestarter_operation_main` for `CMD_BLANK_CHECK`. The fix is a host-side short-circuit that detects SRAM/FRAM before any firmware command is sent.

### Implementation (Task 2 GREEN)

Added to `EpromOperator.check_eprom_blank()` in `eprom_operations.py`:

1. **Class constant:** `_SRAM_PROTO_IDS = frozenset({0x0E, 0x27, 0x28, 0x29})` — all four SRAM protocol families (SRAM_32PIN, SRAM_24PIN, SRAM_STD, SRAM_512K_1M).
2. **Early-return guard:** Before entering `_operation_context`, extract `electrical-type` and `protocol-id` from `eprom_data_dict`. If `etype in ("SRAM", "FRAM")` OR `proto in _SRAM_PROTO_IDS`, emit a `logger.warning` with a clear actionable message and return `False` immediately.
3. **No firmware/wire/messages.py changes:** The fix is purely host-side (D-11/D-30 bounds held).

### Tests (Task 1 RED + Task 2 GREEN)

Added `TestSramBlankCheckShortCircuit` class to `tests/test_eprom_operations.py`:

- **Positive (short-circuit):** `test_sram_blank_check_short_circuits_before_setup` — FM1608-class data (`electrical-type=SRAM`, `protocol-id=0x28`); asserts `_setup_operation` NOT called + result is `False`. FAILED before Task 2 (RED gate), passes after (GREEN).
- **Negative control:** `test_eeprom_blank_check_still_reaches_setup` — W27C512 data (`electrical-type=EEPROM`, `protocol-id=0x07`); asserts `_setup_operation` IS called. Passes both before and after (T-84-04 mitigated).

## Task Commits (inside firestarter_app submodule)

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | RED pinning test | e5bfa3a | tests/test_eprom_operations.py (+94 lines) |
| 2 | GREEN implementation | 4c74b8d | firestarter/eprom_operations.py (+22 lines) |
| 3 | Verification (no code change) | — | (Task 3 is verification-only; no additional commit needed) |

## Verification Results (Task 3)

- **Full host suite:** 665 tests PASSED (663 Phase-82/83 baseline + 2 new SRAM short-circuit tests)
- **0xA4 guard (SAFE-02):** `test_init_phase_data_frames_not_acked` — PASSED
- **CI-scoped ruff:** `ruff check firestarter/ tests/` — PASSED (0 findings)
- **CI-scoped format:** `ruff format --check firestarter/ tests/` — PASSED (73 files already formatted)
- **messages.py unchanged:** `git diff --name-only firestarter/messages.py` — empty (no new message constant)
- **SRAM detection visible:** `grep -n "SRAM\|FRAM" firestarter/eprom_operations.py` confirms lines 1542-1560

## Out-of-Scope Ruff Findings (flagged, not fixed)

Broad `ruff check .` surfaces pre-existing I001 import-sort errors in:
- `tools/audit_coverage_matrix.py:37`
- `tools/catalog/codegen.py:36`
- `tools/catalog/codegen_vectors.py:32`
- `tools/catalog/codegen_vectors.py:189`

These are in the `tools/` tree, **outside the CI scope** (`ci.yml` gates `firestarter/ tests/` only per lines 59-63 of `.github/workflows/ci.yml`). Not introduced by this plan. Not masked. Flagged here for the SAFE-02 bench gate record (D-51).

## Threat Model Compliance

| Threat ID | Status |
|-----------|--------|
| T-84-04 (over-broad short-circuit disables EEPROM blank-check) | MITIGATED — negative control test_eeprom_blank_check_still_reaches_setup passes; W27C512 still reaches _setup_operation |
| T-84-05 (wire protocol / firmware change) | PREVENTED — no messages.py/firmware edit; grep gate confirmed |
| T-84-06 (py3.12 masking CI ruff gate) | MITIGATED — ran ruff against CI scope firestarter/ tests/; tools/ findings flagged not masked (D-51) |
| T-84-SC (package installs) | N/A — no installs (D-52) |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — no new network endpoints, auth paths, file access, or schema changes.

## Self-Check

- [x] `firestarter_app/firestarter/eprom_operations.py` — modified (FOUND)
- [x] `firestarter_app/tests/test_eprom_operations.py` — modified (FOUND)
- [x] Commit e5bfa3a (test RED) — FOUND in submodule log
- [x] Commit 4c74b8d (feat GREEN) — FOUND in submodule log
- [x] Meta gitlink NOT bumped (standing v1.11–v1.15 policy)

## Self-Check: PASSED
