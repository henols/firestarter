---
phase: 88-golden-traces-dispatch-mirror-guard-was-87
plan: 04
subsystem: testing
tags: [dispatch, mirror, protocols, firmware, pytest, ruff]

# Dependency graph
requires:
  - phase: 87-naming-documentation-pass
    provides: PROTOCOLS.md §0 table + handler comment rationale blocks
  - phase: 88-01-through-03
    provides: check_dispatch.py tool leg (already in firestarter_app); test_configure_memory.cpp firmware leg (already in firestarter sub-repo)
provides:
  - firestarter_app/tests/test_dispatch_mirror.py — three-way dispatch-mirror invariant test (doc↔tool↔firmware)
  - parse_protocols_md() helper that parses the §0 pipe table into {hex: handler_file}
  - test_dispatch_mirror_doc_matches_tool — doc↔tool bind across full §0 table (12 rows incl. SRAM/not_implemented)
  - test_dispatch_mirror_firmware_leg_enumerates_all_protocols — firmware-leg drift trap for all §0 real-handler protocols
affects: [88-golden-traces, 89-primitive-recompose, check_dispatch, PROTOCOLS.md, test_configure_memory]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Three-way dispatch bind: PROTOCOLS.md §0 doc-parse + check_dispatch.dispatch() + firmware test enum"
    - "_FA_DIR = pathlib.Path(__file__).parent.parent path discipline (mirrors test_check_dispatch_invariants.py)"
    - "DOC_FILE_TO_FUNC map: handler filename → function name for doc↔tool comparison"
    - "parse_protocols_md() regex: stdlib re only, no markdown lib"

key-files:
  created:
    - firestarter_app/tests/test_dispatch_mirror.py
  modified: []

key-decisions:
  - "D-05/D-06 implemented: full §0 table (12 rows) bound across all three representations — drift in any one trips the test immediately"
  - "0x34 included in doc parse but dispatches to not_implemented per both doc and tool; correctly passes the assertion"
  - "Phantom 0x35/0x39 excluded from doc parse (not in §0) and excluded from firmware-leg assertion; they appear in test_configure_memory.cpp for forward-compat only"
  - "Firmware-leg assertion targets only real-handler protocols (not not_implemented); 0x34 correctly excluded"

patterns-established:
  - "dispatch-mirror pattern: parse §0 pipe table with stdlib re, compare against tool dispatch, grep firmware test file for hex tokens"

requirements-completed: [PRIM-01, SAFE-01, SAFE-02]

# Metrics
duration: 8min
completed: 2026-06-26
---

# Phase 88 Plan 04: Dispatch-Mirror Guard Summary

**Host pytest binding PROTOCOLS.md §0 doc-parse ↔ check_dispatch.dispatch() ↔ firmware test_configure_memory.cpp for all 12 dispatch table entries, ruff-clean for CI py3.11**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-26T08:47:00Z
- **Completed:** 2026-06-26T08:55:11Z
- **Tasks:** 2 (authored together in one file pass)
- **Files modified:** 1

## Accomplishments

- `parse_protocols_md()` parses the §0 pipe table from `PROTOCOLS.md` into `{hex_int: handler_filename}` using stdlib `re` — no markdown library dependency
- `test_dispatch_mirror_doc_matches_tool` checks every §0 protocol (all 12 rows) against `check_dispatch.dispatch()` + `_ALGO_MEM_TYPE`; covers SRAM 0x0E/0x27/0x28/0x29 and 0x34→not_implemented
- `test_dispatch_mirror_firmware_leg_enumerates_all_protocols` greps `test_configure_memory.cpp` for hex tokens and asserts every §0 real-handler protocol appears — drift-trips if any firmware routing test is dropped
- All acceptance criteria met: 2 tests pass, `from tools import check_dispatch` import seam used (never re-implemented), ruff check + ruff format --check clean, no firmware file modified

## Task Commits

Both tasks were implemented atomically as one file creation:

1. **Task 1+2: Author test_dispatch_mirror.py (doc↔tool bind + firmware leg)** — `e46549f` (feat) in `firestarter_app` submodule

**Plan metadata:** to be committed in meta repo

## Files Created/Modified

- `/workspaces/firestarter_app/tests/test_dispatch_mirror.py` — three-way dispatch-mirror invariant test (157 lines, 2 test functions + parse helper)

## Decisions Made

- Tasks 1 and 2 implemented in a single file pass rather than two separate commits because the ruff auto-format was applied after initial creation — the final file state satisfies both tasks' acceptance criteria atomically. A single commit is more accurate than a split that would require re-reading an intermediate state.
- `_ROW_RE` regex matches exactly the §0 table format; correctly skips the header row (`| hex |...`) because the header uses `hex` not `0x...`.
- f-strings used for assertion messages (UP032 compliance with ruff py3.11 target); no backslash-in-f-string constructs (Pitfall 5 avoided).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ruff UP032: .format() → f-string for CI compliance**
- **Found during:** Task 1 (after initial ruff check)
- **Issue:** `.format()` calls flagged as UP032 (prefer f-string) — would fail ruff CI gate
- **Fix:** Replaced two `.format()` calls with f-strings; applied `ruff format` for style normalization
- **Files modified:** `firestarter_app/tests/test_dispatch_mirror.py`
- **Verification:** `ruff check` + `ruff format --check` both exit 0; tests still pass
- **Committed in:** e46549f (incorporated in task commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — ruff UP032 lint compliance)
**Impact on plan:** Trivial formatting fix required by CI py3.11 ruff target. No scope creep.

## Issues Encountered

None beyond the ruff UP032 fix above.

## Known Stubs

None — this plan adds only a test file; no production stubs introduced.

## Threat Flags

None — test-only addition. No new network endpoints, auth paths, file access patterns, or schema changes.

## Self-Check

Files exist:
- `/workspaces/firestarter_app/tests/test_dispatch_mirror.py` — FOUND

Commits exist:
- `e46549f` in `firestarter_app` — FOUND

## Self-Check: PASSED

## Next Phase Readiness

- Dispatch-mirror invariant is now live: any future drift between PROTOCOLS.md §0, check_dispatch.dispatch(), or test_configure_memory.cpp trips this test immediately
- Phase 88 Plan 04 complete; remaining Phase 88 work: the per-family golden register traces (Plans 01–03) if not already complete
- Phase 89 (Incremental Primitive Recompose) can proceed: the D-05 three-way dispatch oracle is in place

---
*Phase: 88-golden-traces-dispatch-mirror-guard-was-87*
*Completed: 2026-06-26*
