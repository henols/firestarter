---
phase: 101-fw-apply-names-in-firmware
plan: 00
subsystem: testing
tags: [pytest, dispatch-guard, protocols-md, regex-parser, doc-code-sync]

# Dependency graph
requires:
  - phase: 100-name-canonical-protocol-name-set-operator-approval
    provides: "Phase-100 restructured firestarter/doc/PROTOCOLS.md into a two-table layout (bucket table + Handler-family layer table), which broke this guard's parser"
provides:
  - "test_dispatch_mirror.py GREEN again — parse_protocols_md() re-pointed to the post-Phase-100 two-table PROTOCOLS.md layout"
  - "Unblocks Wave-0 hard predecessor for every GATE-01 green assertion in the rest of Phase 101"
affects: [101-01, 101-02, "future PROTOCOLS.md restructures"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-table doc-parse join: parse bucket table for hex->family (first token of handler-family column), parse Handler-family layer table for family->file, compose to hex->file"

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_dispatch_mirror.py

key-decisions:
  - "Filtered phantom rows (0x35/0x39, phantom?=YES) out of the doc-leg parse to preserve the original test's documented exclusion (they're absent from check_dispatch.KNOWN_PROTOCOLS and route to not_implemented on the tool leg) — without this exclusion the join would have produced a false mismatch against configure_flash4"
  - "Kept DOC_FILE_TO_FUNC (7 file->func rows) byte-identical per D-01 — no handler rename in this plan"

patterns-established:
  - "When PROTOCOLS.md's bucket table and Handler-family layer table diverge in column shape, doc-side test parsers must join hex->family->file across both tables rather than assume a single-table lookup"

requirements-completed: [GATE-01, FW-03]

coverage:
  - id: D1
    description: "parse_protocols_md() re-pointed to the Phase-100 two-table PROTOCOLS.md layout; returns a non-empty 12-row hex->handler map (0x05-0x34) instead of {}"
    requirement: GATE-01
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_dispatch_mirror.py::test_dispatch_mirror_doc_matches_tool"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_dispatch_mirror.py::test_dispatch_mirror_firmware_leg_enumerates_all_protocols"
        status: pass
    human_judgment: false
  - id: D2
    description: "DOC_FILE_TO_FUNC left byte-identical (no handler rename per D-01) and no edits to check_dispatch.py, memory.cpp, or chip_database.json"
    requirement: FW-03
    verification:
      - kind: other
        ref: "git diff --stat inside firestarter_app submodule — only tests/test_dispatch_mirror.py touched"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-07-01
status: complete
---

# Phase 101 Plan 00: Dispatch-Mirror Guard Reconciliation Summary

**Re-pointed `parse_protocols_md()` in `test_dispatch_mirror.py` to join Phase-100's two-table PROTOCOLS.md layout (bucket table + Handler-family layer table), turning the pre-existing RED guard GREEN with zero change to `DOC_FILE_TO_FUNC` or any firmware/check_dispatch file.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 1
- **Files modified:** 1 (`firestarter_app/tests/test_dispatch_mirror.py`)

## Accomplishments
- Confirmed the RED baseline: `parse_protocols_md()` returned `{}` because Phase 100 moved the `.cpp` filename out of the bucket-table column the old `_ROW_RE` scanned (column 3 is now the frozen `datasheets/` slug).
- Rewrote `parse_protocols_md()` as a two-step join: (1) `_BUCKET_ROW_RE` extracts `hex -> handler-family` from the §0 bucket table (family = first whitespace token of column 6, e.g. `flash4`, `eprom`, `not-implemented`), excluding phantom rows (column 7 `phantom? == YES`); (2) `_FAMILY_ROW_RE` extracts `family -> file` from the separate "Handler-family layer" table; (3) composes to `hex -> file`.
- Verified the resulting dict covers all 12 non-phantom bucket rows (`0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x34`), correctly mapping to their `.cpp` files including the many-to-one `eprom.cpp` (0x07/0x08/0x0B) and `sram.cpp` (0x0E/0x27/0x28/0x29) groupings.
- Both tests in the file now pass: `test_dispatch_mirror_doc_matches_tool` and `test_dispatch_mirror_firmware_leg_enumerates_all_protocols`.
- Confirmed the pre-existing, unrelated `test_audit_coverage_matrix.py::test_golden_file_matches` failure is untouched and out of scope (v1.3 coverage-matrix golden snapshot).

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (on branch `v1.19-protocol-naming-labels`):

1. **Task 1: Re-point parse_protocols_md() to the Phase-100 two-table PROTOCOLS.md layout** - `fb6d167` (fix) — committed inside `firestarter_app/`

**Plan metadata:** this SUMMARY.md commit (meta repo, docs)

_Note: per the submodule-commit protocol for this plan, the code commit lives inside the `firestarter_app` submodule; the meta-repo `firestarter_app` gitlink is intentionally NOT bumped (orchestrator manages gitlink pins at milestone close)._

## Files Created/Modified
- `firestarter_app/tests/test_dispatch_mirror.py` - `parse_protocols_md()` rewritten as a two-table join (`_BUCKET_ROW_RE` + `_FAMILY_ROW_RE`), with phantom-row exclusion; `DOC_FILE_TO_FUNC` and both test functions left unchanged in logic/behavior.

## Decisions Made
- Excluded phantom rows (0x35/0x39) from the doc-leg parse via the bucket table's `phantom?` column, matching the original test's documented scope ("Phantom 0x35/0x39 are NOT in §0 ... excluded from the doc parse ... matching check_dispatch's KNOWN_PROTOCOLS exclusion"). Without this, the join would produce a spurious mismatch (`0x35: doc says configure_flash4 but check_dispatch.dispatch() returned not_implemented`) since `check_dispatch.KNOWN_PROTOCOLS` still excludes 0x35/0x39.
- Kept `DOC_FILE_TO_FUNC` untouched — Phase 100 did not rename any handler, so the existing 7 file→func mappings remain correct (D-01).
- Left `check_dispatch.py`, `memory.cpp`, and `chip_database.json` completely untouched — this plan is scoped to doc-extraction logic only.

## Deviations from Plan

None - plan executed exactly as written. The fix followed the PATTERNS.md two-table join recipe precisely (bucket table hex→family, Handler-family layer family→file, compose).

## Issues Encountered
- First fix iteration correctly joined the two tables but did not yet exclude phantom rows, producing a legitimate assertion failure on 0x35 (`doc says configure_flash4 but check_dispatch.dispatch() returned not_implemented`). Resolved by adding phantom-column filtering to the bucket-row parse, matching the original test's own documented phantom-exclusion contract. This was expected refinement within Task 1's scope, not a deviation from the plan.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `test_dispatch_mirror.py` is GREEN — GATE-01's explicitly-named guard can now be honestly claimed green in subsequent Phase 101 plans (101-01, 101-02) once they add the `PROTO_<NAME>` constants and relabel `memory.cpp`.
- No blockers. The two-table join pattern established here (bucket table + Handler-family layer table) is reusable if PROTOCOLS.md restructures again.

---
*Phase: 101-fw-apply-names-in-firmware*
*Completed: 2026-07-01*

## Self-Check: PASSED

- FOUND: `.planning/phases/101-fw-apply-names-in-firmware/101-00-SUMMARY.md`
- FOUND: `fb6d167` (submodule code commit, `firestarter_app` on branch `v1.19-protocol-naming-labels`)
- FOUND: `b27bed7` (meta-repo SUMMARY commit)
