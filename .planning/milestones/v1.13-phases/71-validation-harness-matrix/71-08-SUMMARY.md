---
phase: 71-validation-harness-matrix
plan: "08"
subsystem: validation-harness
tags: [gap-closure, harn-04, flash4, spec-trim, codegen, drift-gate]
dependency_graph:
  requires: [71-07-SUMMARY.md]
  provides: [HARN-04 Complete, drift-gate-11-rows]
  affects: [firestarter_app/tools/validation_matrix_spec.json, firestarter/test/native/avr/_shared/validation_matrix.h]
tech_stack:
  added: []
  patterns: [spec-trim-with-rationale, codegen-drift-gate, cr-02-resolution]
key_files:
  created: []
  modified:
    - firestarter_app/tools/validation_matrix_spec.json
    - firestarter/test/native/avr/_shared/validation_matrix.h
    - firestarter_app/tests/test_gen_validation_header.py
    - .planning/REQUIREMENTS.md
decisions:
  - "CR-02 resolution: flash4 host matrix trimmed to [5] only; 0x35/0x39 intentionally omitted (zero DB chips, host never dispatches them); firmware truth + native coverage retained in test_val_flash4.cpp"
  - "protocols_note field added to spec JSON as a durable rationale (JSON has no comment syntax); validate_spec and emit_cpp_header ignore extra family keys"
  - "VAL_FAMILY_COUNT 13->11: only the two 0x35/0x39 flash4 rows removed; all 6 handler names remain present in the header"
metrics:
  duration: "~7 minutes"
  completed: "2026-06-16T19:15:32Z"
  tasks_completed: 2
  files_changed: 4
---

# Phase 71 Plan 08: Spec Trim (HARN-04 Gap Closure) Summary

**One-liner:** Trimmed flash4 host matrix to protocols=[5] (CR-02 resolution), regenerated 11-row header byte-identically (drift gate green), documented firmware/native vs host-matrix distinction durably, marked HARN-04 Complete.

## Objective

Close GAP-2 (HARN-04 / SC#4): `validation_matrix_spec.json` declared flash4 `"protocols": [5, 53, 57]` (0x05/0x35/0x39), but `check_dispatch.py::dispatch()` only maps 0x05 → configure_flash4 (0x35/0x39 fall through to "not_implemented" path, as zero DB chips carry those protocols). The host validation matrix must reflect what the host dispatch mirror actually routes — not what the firmware internally covers.

Locked operator decision (FINAL): TRIM THE SPEC to the host. Change flash4 `"protocols": [5, 53, 57]` → `"protocols": [5]`. Do NOT modify check_dispatch.py. Regenerate `validation_matrix.h` and keep the drift gate green.

## Tasks Completed

### Task 1: Trim flash4 protocols to [5], add rationale, regenerate header, update drift gate

**Files (firestarter_app submodule, commit `96fe738`):**
- `firestarter_app/tools/validation_matrix_spec.json` — flash4 `protocols: [5, 53, 57]` → `[5]`; added `protocols_note` string key documenting the CR-02 resolution rationale
- `firestarter_app/tests/test_gen_validation_header.py` — renamed `test_committed_header_has_13_rows` → `test_committed_header_has_11_rows`; updated docstring + assertion from `== 13` to `== 11`; updated failure message

**Files (firestarter submodule, commit `8d378b0`):**
- `firestarter/test/native/avr/_shared/validation_matrix.h` — regenerated: `VAL_FAMILY_COUNT 13` → `11`; rows `{ 0x35, "flash4", "configure_flash4" }` and `{ 0x39, "flash4", "configure_flash4" }` removed

**Verification passed:**
- `python -c "...assert p==[5]..."` exits 0
- `python tools/gen_validation_header.py` exits 0
- `pytest tests/test_gen_validation_header.py -q` exits 0 (12 tests, all green)
- `grep -q "VAL_FAMILY_COUNT 11" validation_matrix.h` exits 0
- `ruff check + ruff format --check tests/test_gen_validation_header.py` both exit 0
- `check_dispatch.py` unchanged; `test_val_flash4.cpp` 0x35/0x39 tests retained

### Task 2: Mark HARN-04 Complete in REQUIREMENTS.md; re-run HARN-04 gate

**File (meta repo):** `.planning/REQUIREMENTS.md`
- Checkbox line 18: `- [ ] **HARN-04**:` → `- [x] **HARN-04**:`
- Coverage-table row: `| HARN-04 | Phase 71 | Pending |` → `| HARN-04 | Phase 71 | Complete |`
- HARN-03 confirmed `- [x]` / `Complete` (unchanged)

**HARN-04 gate re-run:**
```
PASS: all 744 chips scanned; 730 supported; 14 chips confirmed non-dispatchable (D-12: host guard covers non-supported chips with real handlers; non-handler outcomes also safe); 0 non_supported_dispatchable (gate GREEN); 0 dispatch regressions; 0 consistency violations
```

## Deviations from Plan

None — plan executed exactly as written.

## Key Decisions

1. **CR-02 resolution documented as a `protocols_note` JSON field.** Since JSON has no comment syntax, a sibling string key on the flash4 family entry is the only way to preserve the rationale durably alongside the data. `validate_spec()` and `emit_cpp_header()` both ignore extra keys, so this is non-breaking. Future readers will see the explanation directly in the spec.

2. **Drift gate test renamed to `test_committed_header_has_11_rows`.** The original `test_committed_header_has_13_rows` name was itself a documentation artifact — renaming it keeps the test self-documenting. The failure message now explains the 13→11 delta explicitly.

3. **Native firmware tests retained.** `test_val_flash4.cpp` hard-codes `make_handle(0x35,...)` and `make_handle(0x39,...)` and calls `configure_memory` directly. These tests prove real firmware behavior and do not iterate VAL_FAMILIES, so trimming the generated header does not affect them. They are the correct home for 0x35/0x39 firmware coverage; the host matrix is not.

## Self-Check: PASSED

- `firestarter_app/tools/validation_matrix_spec.json` — exists, flash4 protocols == [5], protocols_note present
- `firestarter/test/native/avr/_shared/validation_matrix.h` — VAL_FAMILY_COUNT 11, no 0x35/0x39 rows
- `firestarter_app/tests/test_gen_validation_header.py` — test_committed_header_has_11_rows asserts == 11
- `.planning/REQUIREMENTS.md` — HARN-04 [x] / Complete; HARN-03 [x] / Complete
- Commits: firestarter_app `96fe738`, firestarter `8d378b0`
