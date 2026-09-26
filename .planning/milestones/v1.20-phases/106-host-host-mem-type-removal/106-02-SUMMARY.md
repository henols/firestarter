---
phase: 106-host-host-mem-type-removal
plan: 02
subsystem: host-cli-display
tags: [python, click, display-labels, mem_type, protocol-dispatch, ruff]

# Dependency graph
requires:
  - phase: 106-01
    provides: "database.py mem_type/_ALGO_MEM_TYPE removal (disjoint files, read for current-state context only)"
provides:
  - "ic_layout.py get_chip_type_string()/resolve_type_label() with the numeric type_map fallback tier fully removed"
  - "eprom_info.py list/search caller updated to the shrunk resolve_type_label() signature"
affects: [107-docs-and-gate-close]

# Tech tracking
tech-stack:
  added: []
  patterns: ["shared label helper with tiered fallback (electrical.type -> protocol -> bare 'Unknown')"]

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/tests/test_ic_layout.py

key-decisions:
  - "get_chip_type_string signature shrunk to (self, protocol_id=None) — chip_type_int param and the local type_map dict deleted; unresolved falls to bare 'Unknown' (was f'Unknown ({chip_type_int})')"
  - "resolve_type_label signature shrunk to (self, electrical_type, protocol_id=None) — type_int param and its docstring Arg line deleted; delegates to get_chip_type_string(protocol_id)"
  - "__main__ self-test block repurposed to exercise the surviving protocol tier: get_chip_type_string(0x08) (known protocol) and get_chip_type_string(0x99) (unknown -> 'Unknown'), replacing the removed numeric-tier calls get_chip_type_string(1)/get_chip_type_string(5)"
  - "eprom_info.py:69 '\"type\": \"unknown\"' (string-typed raw-JSON _clean_config field) left untouched per plan's explicit OUT-OF-SCOPE note — different axis from the numeric mem_type"

requirements-completed: [HOST-03]

coverage:
  - id: D1
    description: "ic_layout.py's get_chip_type_string/resolve_type_label no longer accept a numeric mem_type param and have no type_map fallback; unresolved labels land on bare 'Unknown'"
    requirement: HOST-03
    verification:
      - kind: unit
        ref: "firestarter_app inline verification: EpromSpecBuilder(db_instance=None).resolve_type_label('EEPROM')=='EEPROM' and resolve_type_label(None, 999)=='Unknown'"
        status: pass
    human_judgment: false
  - id: D2
    description: "eprom_info.py list/search caller and test_ic_layout.py's positional test call updated to the shrunk signature with no behavior regression"
    requirement: HOST-03
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_ic_layout.py (11 tests, all pass)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_eprom_info.py (8 tests, all pass)"
        status: pass
    human_judgment: false
  - id: D3
    description: "ruff check + ruff format --check clean on the py3.11 analysis target for the three touched files"
    verification:
      - kind: other
        ref: "cd firestarter_app && ruff check firestarter/ic_layout.py firestarter/eprom_info.py tests/test_ic_layout.py && ruff format --check <same files>"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-07-02
status: complete
---

# Phase 106 Plan 02: Drop the mem_type Numeric Display-Label Tier Summary

**Removed the last numeric `mem_type`-keyed display fallback (`type_map`) from `ic_layout.py`'s shared label helper — `info`/`list`/`search` now derive labels solely from `electrical.type` then protocol, landing on bare `"Unknown"` for anything else.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-07-02T13:23:00Z (approx, first commit 13:23:30Z)
- **Completed:** 2026-07-02T13:26:11Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- `get_chip_type_string` dropped its `chip_type_int` parameter and the `type_map = {1: "EPROM", 2: "Flash type 2", 3: "Flash type 3", 4: "SRAM"}` dict; unresolved protocol now returns the bare string `"Unknown"` (was `f"Unknown ({chip_type_int})"`)
- `resolve_type_label` dropped its `type_int` parameter (and docstring Arg line); it now delegates to `get_chip_type_string(protocol_id)` only, with the tier-1 `_ELECTRICAL_TYPE_LABEL` check unchanged
- `build_specifications` (info view) and `print_eprom_list_table` (list/search view) both drop the dead `eprom_data.get("type", 0)` / `ic.get("type", 0)` positional argument at their `resolve_type_label` call sites
- `test_ic_layout.py`'s positional `get_chip_type_string(0, pid)` call updated to `get_chip_type_string(pid)`, preserving the D-01 single-source assertion semantics
- `ruff check` + `ruff format --check` clean on the py3.11 analysis target for all three touched files

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.20-protocol-only-dispatch`):

1. **Task 1: Drop the numeric tier + param from the shared label helper in ic_layout.py** - `019f47a` (refactor)
2. **Task 2: Drop the dead positional arg at the eprom_info.py list/search caller + fix the test ripple** - `f1457ef` (refactor)
3. **Task 3: py3.11-target static gates on the touched display files** - `c2f359d` (style — ruff-format fixup surfaced by the gate; see Deviations)

**Plan metadata:** (this commit, meta-repo) — SUMMARY.md + STATE.md + ROADMAP.md

## Files Created/Modified
- `firestarter_app/firestarter/ic_layout.py` - `get_chip_type_string`/`resolve_type_label` signatures shrunk, `type_map` deleted, `build_specifications` caller + `__main__` self-test updated
- `firestarter_app/firestarter/eprom_info.py` - `print_eprom_list_table`'s `resolve_type_label` call drops the dead `.get("type", 0)` middle arg
- `firestarter_app/tests/test_ic_layout.py` - positional `get_chip_type_string(0, pid)` → `get_chip_type_string(pid)`

## Decisions Made
- Chose `get_chip_type_string(0x08)` (a real `_PROTOCOL_DISPLAY_NAME` key) and `get_chip_type_string(0x99)` (unrecognized) for the `__main__` self-test replacement calls, rather than reusing the removed numeric values `1`/`5` — those integers no longer map to anything meaningful under the new protocol-only signature, and the plan explicitly asked for one known + one unknown protocol-based call.
- Verified `resolve_type_label`'s tier-1 behavior using `'EEPROM'` (an actual `_ELECTRICAL_TYPE_LABEL` key) rather than the plan verification snippet's literal example `'EPROM'` (not a key in that map) — confirms the acceptance intent (tier-1 resolves; unresolved protocol → bare `"Unknown"`) without asserting a string the source never produces.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] ruff format flagged the reformatted `__main__` self-test block**
- **Found during:** Task 3 (py3.11-target static gates)
- **Issue:** The two-line-wrapped `logger.info(...)` calls written in Task 1 exceeded ruff format's line-collapsing preference; `ruff format --check` failed on `ic_layout.py`.
- **Fix:** Ran `ruff format firestarter/ic_layout.py`, which collapsed both calls back onto single lines (89-char lines, within ruff's line-length allowance for f-strings).
- **Files modified:** `firestarter_app/firestarter/ic_layout.py`
- **Verification:** `ruff format --check` now reports all three files already formatted; `ruff check` still passes; `test_ic_layout.py`/`test_eprom_info.py` re-run green after the reformat.
- **Committed in:** `c2f359d` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking — formatting)
**Impact on plan:** Cosmetic only; no behavior change. No scope creep.

## Issues Encountered
None beyond the Task 3 formatting fixup above.

## Pre-existing Out-of-Scope Failures (not touched, per scope boundary)
Two test failures pre-date this plan and are explicitly out of scope (confirmed in `.planning/phases/106-host-host-mem-type-removal/deferred-items.md`, logged by Plan 106-01):
- `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` — pre-existing golden-fixture drift, unrelated to this axis removal.
- `tests/test_chip_resolver.py::test_resolve_chip_hit_has_required_programmer_keys` — expected ripple from Plan 106-01's `database.py` change; explicitly assigned to Plan 03 to invert.

Both files are disjoint from this plan's `files_modified` scope (`ic_layout.py`, `eprom_info.py`, `test_ic_layout.py`) and were left untouched.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- HOST-03 (display-layer `mem_type` fallback removal) complete. `ic_layout.py`/`eprom_info.py` now derive labels solely from `electrical.type` → protocol → `"Unknown"`.
- Plan 106-03 can proceed to invert `test_chip_resolver.py` and complete the remaining HOST-0x database/wire-emit work; no blockers from this plan.
- Surviving tiers `_ELECTRICAL_TYPE_LABEL` and `_PROTOCOL_DISPLAY_NAME` are untouched and intact for any future consumer.

---
*Phase: 106-host-host-mem-type-removal*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/106-host-host-mem-type-removal/106-02-SUMMARY.md`
- FOUND: `firestarter_app/firestarter/ic_layout.py`
- FOUND: `firestarter_app/firestarter/eprom_info.py`
- FOUND: `firestarter_app/tests/test_ic_layout.py`
- FOUND commit (firestarter_app): `019f47a`
- FOUND commit (firestarter_app): `f1457ef`
- FOUND commit (firestarter_app): `c2f359d`
- FOUND commit (meta-repo): `6181b69`
