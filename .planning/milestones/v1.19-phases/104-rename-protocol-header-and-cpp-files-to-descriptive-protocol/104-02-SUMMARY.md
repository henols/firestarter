---
phase: 104-rename-protocol-header-and-cpp-files-to-descriptive-protocol
plan: 02
subsystem: host-tooling
tags: [python, dispatch-mirror, validation-matrix, codegen, docs, gate-01]

# Dependency graph
requires:
  - phase: 104-01
    provides: "Renamed firmware handler functions configure_flash_nor_unlock (0x06) and configure_flash_5v_page (0x05), plus renamed file pairs flash_nor_unlock.{h,cpp} / flash_5v_page.{h,cpp}"
provides:
  - "check_dispatch.py dispatch mirror returning configure_flash_nor_unlock/configure_flash_5v_page at both the protocol map and the mem_type fallback map"
  - "_FAMILY_VPP_INVARIANTS keyed by the renamed function names"
  - "validation_matrix_spec.json flash3/flash4 family objects renamed to nor_unlock/5v_page (id/handler/suite/test_module)"
  - "Regenerated firestarter/test/native/avr/_shared/validation_matrix.h carrying descriptive 0x06/0x05 rows"
  - "Host doc tables (protocol-id.md, infoic-field-dictionary.md) renamed to the descriptive handler names"
affects: [104-03-rename-native-tests]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Spec-then-regenerate: edit validation_matrix_spec.json (source of truth), then run gen_validation_header.py to re-emit validation_matrix.h — never hand-edit the generated header"

key-files:
  created: []
  modified:
    - firestarter_app/tools/check_dispatch.py
    - firestarter_app/tests/test_check_dispatch_invariants.py
    - firestarter_app/tools/validation_matrix_spec.json
    - firestarter/test/native/avr/_shared/validation_matrix.h
    - firestarter_app/doc/protocol-id.md
    - firestarter_app/doc/infoic-field-dictionary.md

key-decisions:
  - "New family-id strings introduced for Plan 03: 'nor_unlock' (was 'flash3') and '5v_page' (was 'flash4') — these become the test-suite directory names in Plan 03"
  - "protocols_note prose in the 5v_page family object updated to reference configure_flash_5v_page and test_val_5v_page.cpp while preserving the factual 0x35/0x39 phantom-dispatch explanation verbatim"

patterns-established: []

requirements-completed: [RENAME-03]

coverage:
  - id: D1
    description: "check_dispatch.py dispatch() returns configure_flash_nor_unlock for 0x06 and configure_flash_5v_page for 0x05 at both the protocol map and the mem_type fallback map; _FAMILY_VPP_INVARIANTS keyed by the renamed names"
    requirement: "RENAME-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_check_dispatch_invariants.py::test_family_vpp_invariants_all_six_handlers_present (12/12 tests pass)"
        status: pass
      - kind: unit
        ref: "grep configure_flash3|configure_flash4 in check_dispatch.py + test file returns empty"
        status: pass
    human_judgment: false
  - id: D2
    description: "validation_matrix_spec.json flash3/flash4 family objects renamed to descriptive nor_unlock/5v_page form; validation_matrix.h regenerated (not hand-edited) carrying descriptive 0x06/0x05 rows; flash_intel row unchanged"
    requirement: "RENAME-03"
    verification:
      - kind: unit
        ref: "python firestarter_app/tools/gen_validation_header.py; grep confirms configure_flash_nor_unlock/configure_flash_5v_page present, configure_flash3/flash4/\"flash3\"/\"flash4\" absent, flash_intel row intact"
        status: pass
    human_judgment: false
  - id: D3
    description: "Host doc tables (protocol-id.md, infoic-field-dictionary.md) 0x05/0x06 rows renamed to configure_flash_5v_page/configure_flash_nor_unlock; DB identity holds (GATE-02)"
    requirement: "RENAME-03"
    verification:
      - kind: unit
        ref: "grep confirms no configure_flash3/4 survives in doc/protocol-id.md or doc/infoic-field-dictionary.md"
        status: pass
      - kind: integration
        ref: "python firestarter_app/tools/diff_db.py (PASS: only pre-existing Phase-94 PGSZ baseline delta, 0 new drift)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-02
status: complete
---

# Phase 104 Plan 02: Host GATE-01 Dispatch-Mirror Lockstep Summary

**Brought `check_dispatch.py`, its invariant test, `validation_matrix_spec.json`, the regenerated `validation_matrix.h`, and the host doc tables into lockstep with Plan 01's renamed firmware functions (`configure_flash3` → `configure_flash_nor_unlock`, `configure_flash4` → `configure_flash_5v_page`), holding GATE-01/02 throughout.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-07-02T07:27:00Z (approx, immediately after Plan 01 close)
- **Completed:** 2026-07-02T07:29:52Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- `check_dispatch.py` dispatch mirror updated at all three sites: `_FAMILY_VPP_INVARIANTS` keys, the `dispatch()` protocol map (0x06/0x05 arms), and the `mem_type` legacy fallback map (3/5 arms) — all now return `configure_flash_nor_unlock`/`configure_flash_5v_page`. Integer protocol/mem_type keys untouched.
- `test_check_dispatch_invariants.py` expected-handler-name set updated to match; full suite green (12/12 tests).
- `validation_matrix_spec.json` `flash3`/`flash4` family objects renamed to descriptive `nor_unlock`/`5v_page` form (id, handler, tier1 suite, tier2 test_module), mirroring the golden `flash_intel` shape; the `5v_page` `protocols_note` prose updated to the new handler/test-module names while preserving the 0x35/0x39 phantom-dispatch explanation.
- `firestarter/test/native/avr/_shared/validation_matrix.h` regenerated (not hand-edited) via `gen_validation_header.py` from the updated spec — its 0x06/0x05 rows now read `{ 0x06, "nor_unlock", "configure_flash_nor_unlock" }` / `{ 0x05, "5v_page", "configure_flash_5v_page" }`; the `flash_intel` row and all other rows unchanged.
- Host doc tables `protocol-id.md` and `infoic-field-dictionary.md` renamed at the 0x05/0x06 rows to the descriptive handler names; algorithm-id / minipro-label columns and prose left untouched.
- `diff_db.py` confirms DB identity (GATE-02) — the only reported delta is the pre-existing Phase-94 PGSZ baseline explanation (unrelated to this plan), 0 new drift.

## Task Commits

Each task was committed atomically:

1. **Task 1: Update check_dispatch.py + invariant test to the renamed function names** - `ad223c0` (feat, firestarter_app)
2. **Task 2: Update validation_matrix_spec.json + regenerate validation_matrix.h** - `1d39d8c` (feat, firestarter_app) + `b2be890` (feat, firestarter)
3. **Task 3: Update host doc tables; confirm DB identity (GATE-02)** - `a8d60b2` (docs, firestarter_app)

_Note: all commits were made inside the respective submodules (`firestarter_app/` and `firestarter/`), on their current branch `v1.19-protocol-naming-labels` (no gitlink bump — consistent with standing policy)._

## Files Created/Modified
- `firestarter_app/tools/check_dispatch.py` - `_FAMILY_VPP_INVARIANTS` keys + `dispatch()` protocol/mem_type map returns renamed to `configure_flash_nor_unlock`/`configure_flash_5v_page`
- `firestarter_app/tests/test_check_dispatch_invariants.py` - expected handler-name set updated to the renamed strings
- `firestarter_app/tools/validation_matrix_spec.json` - `flash3`→`nor_unlock`, `flash4`→`5v_page` family objects (id/handler/suite/test_module/protocols_note); protocols arrays/integers unchanged
- `firestarter/test/native/avr/_shared/validation_matrix.h` - regenerated from the updated spec; descriptive 0x06/0x05 rows, `flash_intel` row intact
- `firestarter_app/doc/protocol-id.md` - 0x05/0x06 handler cells renamed
- `firestarter_app/doc/infoic-field-dictionary.md` - 0x05/0x06 handler cells renamed

## Decisions Made
- New family-id strings `nor_unlock` and `5v_page` (replacing `flash3`/`flash4`) are the descriptive form used consistently across the spec, the generated header, and (per the plan's forward note) will seed Plan 03's native test-suite directory renames.
- Preserved the `protocols_note` prose's factual content (0x35/0x39 phantom-dispatch explanation, CR-02 resolution date) verbatim, only substituting the handler/test-module name references.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' verification blocks passed on first attempt with no auto-fixes required.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 03 (native test-suite dir renames: `test_val_flash3` → `test_val_nor_unlock`, `test_val_flash4` → `test_val_5v_page`) is unblocked — the family-id strings `nor_unlock`/`5v_page` and suite names `test_val_nor_unlock`/`test_val_5v_page` it needs are now defined in `validation_matrix_spec.json` and reflected in the regenerated `validation_matrix.h`.
- No blockers. GATE-01 (dispatch mirror + regenerated matrix header) and GATE-02 (DB identity via `diff_db.py`) both hold; no protocol integer, `protocols` array, `chip_database.json` value, or CLI grammar was touched.
- The following files still reference the old `flash_type_3`/`flash_type_4`/`configure_flash3`/`configure_flash4`/`"flash3"`/`"flash4"` names by design, out of this plan's declared scope, and are Plan 03's job: `firestarter/test/native/avr/test_val_flash3/test_val_flash3.cpp`, `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp`, `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`.

---
*Phase: 104-rename-protocol-header-and-cpp-files-to-descriptive-protocol*
*Completed: 2026-07-02*

## Self-Check: PASSED

All modified files verified present on disk (firestarter_app/tools/check_dispatch.py,
firestarter_app/tests/test_check_dispatch_invariants.py,
firestarter_app/tools/validation_matrix_spec.json,
firestarter/test/native/avr/_shared/validation_matrix.h,
firestarter_app/doc/protocol-id.md, firestarter_app/doc/infoic-field-dictionary.md)
and all commit hashes verified present in git history (firestarter_app submodule:
ad223c0, 1d39d8c, a8d60b2; firestarter submodule: b2be890).
