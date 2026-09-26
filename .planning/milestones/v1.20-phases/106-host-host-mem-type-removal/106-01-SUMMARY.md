---
phase: 106-host-host-mem-type-removal
plan: 01
subsystem: database
tags: [python, dispatch, wire-protocol, database, pytest, ruff]

# Dependency graph
requires:
  - phase: 105-firmware-mem-type-removal
    provides: "Firmware no longer parses the `type` JSON field; json_parser.c silently skips unknown fields, so a host briefly still emitting `type` was harmless during the gap."
provides:
  - "database.py no longer defines _ALGO_MEM_TYPE, derives no mem_type/determined_type, and has no 'Generic Flash (legacy fallback only)' default."
  - "convert_to_programmer no longer emits a `type` key on the wire; algorithm (via protocol-id) is the sole surviving dispatch datum."
  - "7 inverted wire-shape test functions across 6 test_val_wire_*.py files positively assert `type` is absent from the wire dict."
  - "test_eprom_database.py's required-keys tuple no longer lists `type`."
affects: [106-02, 106-03, 107-docs-gate]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Wire-absence proof pattern: `assert \"type\" not in wire` replacing a `wire.get(\"type\", 0)` read, with `dispatch(algo, 0)` as the safe stand-in since dispatch()'s mem_type fallback path only fires when protocol==0."

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/database.py
    - firestarter_app/tests/test_val_wire_eprom.py
    - firestarter_app/tests/test_val_wire_flash_intel.py
    - firestarter_app/tests/test_val_wire_nor_unlock.py
    - firestarter_app/tests/test_val_wire_5v_page.py
    - firestarter_app/tests/test_val_wire_eeprom28c.py
    - firestarter_app/tests/test_val_wire_sram.py
    - firestarter_app/tests/test_eprom_database.py

key-decisions:
  - "Kept dispatch()'s second positional arg as a literal 0 rather than removing it, since dispatch()'s mem_type fallback chain only activates on protocol==0 (dead for every real DB chip's non-zero algorithm) — avoids touching dispatch()'s signature, which is out of this plan's scope."
  - "Logged the pre-existing test_audit_coverage_matrix.py::test_golden_file_matches failure and the expected test_chip_resolver.py ripple (explicitly owned by Plan 03 per the plan text) to deferred-items.md rather than fixing/touching either — both are declared out of scope."

patterns-established:
  - "Wire-shape inversion tests as the mechanism for proving a wire-contract deletion (`assert key not in wire` as positive proof of absence, mirroring the SC#1 requirement)."

requirements-completed: [HOST-01, HOST-02]

coverage:
  - id: D1
    description: "database.py deletions: _ALGO_MEM_TYPE dict, determined_type derivation block (incl. 'Generic Flash (legacy fallback only)' default), and both `type` dict keys (mapped-dict + wire-emit) removed"
    requirement: "HOST-02"
    verification:
      - kind: unit
        ref: "grep -nE '_ALGO_MEM_TYPE|determined_type|Generic Flash \\(legacy fallback only\\)' firestarter/database.py (0 matches)"
        status: pass
      - kind: unit
        ref: "python -c \"from firestarter.database import EpromDatabase; ...\" (real W27C512 conversion: no `type` key, `algorithm` present)"
        status: pass
    human_judgment: false
  - id: D2
    description: "7 wire-validation test functions (6 files) inverted to assert `type` absent from wire dict instead of reading it"
    requirement: "HOST-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_val_wire_eprom.py::test_eprom_wire_dict_dispatches_to_configure_eprom"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_val_wire_sram.py (2 functions: dispatches_to_configure_sram, never_dispatches_to_configure_eprom)"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_eprom_database.py required-keys tuple no longer lists `type`; positive absence assertion added"
    requirement: "HOST-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_eprom_database.py::TestConvertToProgrammer::test_convert_to_programmer_required_keys_present"
        status: pass
    human_judgment: false
  - id: D4
    description: "ruff check + ruff format --check clean on all touched files (py3.11-target static gate, py3.12-masks-CI-3.11 trap avoided)"
    verification:
      - kind: other
        ref: "ruff check firestarter/database.py tests/test_val_wire_*.py tests/test_eprom_database.py"
        status: pass
      - kind: other
        ref: "ruff format --check (same file set)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-02
status: complete
---

# Phase 106 Plan 01: database.py mem_type Deletion + Wire-Test Inversion Summary

**Deleted the `_ALGO_MEM_TYPE` fallback dict, `determined_type` derivation, and both `type` dict keys from `database.py`, completing the host emit-side of WIRE-01 — the wire dict now carries `algorithm` as the sole dispatch datum, proven by 8 inverted test functions asserting `type`'s absence.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-07-02T13:11:10Z
- **Completed:** 2026-07-02T13:18:02Z
- **Tasks:** 3
- **Files modified:** 8 (1 source + 7 test files)

## Accomplishments
- `database.py` no longer defines `_ALGO_MEM_TYPE`, derives no `mem_type`/`determined_type`, and has no "Generic Flash (legacy fallback only)" default — `protocol_id`/`algorithm`/`electrical-type` all survive untouched.
- `convert_to_programmer`'s wire-emit dict no longer includes a `type` key; a real chip (W27C512) converts cleanly with `algorithm` present and `type` absent.
- All 7 `test_val_wire_*` test functions (across 6 files) inverted to `assert "type" not in wire` as positive proof of removal, replacing the old `mem_type = wire.get("type", 0)` reads; `dispatch()` calls now pass a literal `0` as the second arg (safe because `dispatch()`'s mem_type fallback only fires when `protocol == 0`, never true for these non-zero-algorithm rep chips).
- `test_eprom_database.py`'s required-keys tuple no longer lists `"type"`; added an explicit `assert "type" not in config`.
- `ruff check` + `ruff format --check` clean on every touched file against the py3.9/py3.11 analysis target.

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.20-protocol-only-dispatch`):

1. **Task 1: Delete the mem_type derivation + both `type` dict keys from database.py** - `6da9cb1` (feat)
2. **Task 2: Invert the wire-shape tests + the required-keys test to prove `type` is absent (D-05)** - `2cb8f06` (test)
3. **Task 3: py3.11-target static gates on the touched files** - `aa841be` (style)

**Plan metadata:** committed in meta-repo (this SUMMARY.md + STATE.md + ROADMAP.md).

## Files Created/Modified
- `firestarter_app/firestarter/database.py` - Removed `_ALGO_MEM_TYPE`, `determined_type` derivation, and both `"type"` dict keys (deletion-only edit, no net-new symbols)
- `firestarter_app/tests/test_val_wire_eprom.py` - Inverted 1 wire-shape test function
- `firestarter_app/tests/test_val_wire_flash_intel.py` - Inverted 1 wire-shape test function
- `firestarter_app/tests/test_val_wire_nor_unlock.py` - Inverted 1 wire-shape test function
- `firestarter_app/tests/test_val_wire_5v_page.py` - Inverted 1 wire-shape test function (+ ruff-format wrap)
- `firestarter_app/tests/test_val_wire_eeprom28c.py` - Inverted 1 wire-shape test function
- `firestarter_app/tests/test_val_wire_sram.py` - Inverted 2 wire-shape test functions
- `firestarter_app/tests/test_eprom_database.py` - Removed `"type"` from required-keys tuple, added absence assertion

## Decisions Made
- Kept `dispatch(algo, 0)` rather than changing `dispatch()`'s signature — per Pitfall 4 in 106-RESEARCH.md, the mem_type fallback chain inside `dispatch()` is `protocol==0`-only, so passing a literal `0` never changes behavior for any real (non-zero-algorithm) chip; removing the parameter entirely is out of this plan's scope.
- Logged (not fixed) two out-of-scope test failures to `deferred-items.md`: the pre-existing `test_audit_coverage_matrix.py::test_golden_file_matches` golden-fixture drift (reproduced independently of this plan's changes via `git stash`), and the expected `test_chip_resolver.py::test_resolve_chip_hit_has_required_programmer_keys` ripple, whose inversion the plan explicitly assigns to Plan 03 to avoid a file-write conflict.

## Deviations from Plan

None - plan executed exactly as written. The plan itself anticipated and pre-authorized the `test_chip_resolver.py` ripple (explicitly out of scope, owned by Plan 03) and the `ruff format` pass in Task 3 (anticipated blank-line/wrap risk after deletion).

## Issues Encountered

Running the full `firestarter_app` test suite (broader than this plan's declared verification scope) surfaced 2 failures, both out of scope and left untouched, logged to `.planning/phases/106-host-host-mem-type-removal/deferred-items.md`:
- `test_audit_coverage_matrix.py::test_golden_file_matches` — pre-existing golden-fixture byte-drift, reproduced identically on a pre-106-01 checkout via `git stash`; unrelated to `mem_type`/`type` removal.
- `test_chip_resolver.py::test_resolve_chip_hit_has_required_programmer_keys` — expected ripple from Task 1's `database.py` change; plan text explicitly reserves this file's inversion for Plan 03.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 106-02 and 106-03 can proceed; Plan 03 owns the `test_chip_resolver.py` inversion left pending here.
- Wire contract's emit-side removal of `type` is now proven (SC#1 partial from this plan); firmware already stopped parsing it in Phase 105 — Phase 106 as a whole should re-verify SC#1 is FULLY closed once Plans 02/03 land.
- Firmware submodule gitlink NOT bumped (PINNED per operator policy) — only `firestarter_app` submodule commits landed.

---
*Phase: 106-host-host-mem-type-removal*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/database.py`
- FOUND: `.planning/phases/106-host-host-mem-type-removal/106-01-SUMMARY.md`
- FOUND commit `6da9cb1` (firestarter_app) - Task 1
- FOUND commit `2cb8f06` (firestarter_app) - Task 2
- FOUND commit `aa841be` (firestarter_app) - Task 3
- FOUND commit `c49795a` (meta-repo) - docs/summary
