---
phase: 148-numeric-database-values-the-at28c-vcc-decode
plan: 01
subsystem: testing
tags: [database, golden-fixture, regression-gate, pytest, ruff]

requires: []
provides:
  - "Committed 746-chip pre-Phase-148 host->wire golden (tests/golden/wire_dict_baseline.json)"
  - "Byte-identity regression test proving Phase 148 changes nothing on the wire (tests/test_wire_dict_equivalence.py)"
  - "Measured ## Before state of all four gates in the D-12 review artifact (148-DB-DIFF.md)"
affects: [148-02, 148-03, 148-04, 148-05, 148-06, 148-07, 148-08]

tech-stack:
  added: []
  patterns:
    - "Golden JSON fixture with a meta+records document shape (meta block prose convention from chip_database_field_inventory.json)"
    - "_describe_record_diff: shared helper between the real comparison test and its non-vacuity leg, naming added/removed/changed record keys and differing wire keys"

key-files:
  created:
    - firestarter_app/tests/golden/wire_dict_baseline.json
    - firestarter_app/tests/test_wire_dict_equivalence.py
    - .planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md
  modified: []

key-decisions:
  - "Record key is f\"{mfg}|{pn}|{i}\", never pn alone -- part numbers are not unique across ~9% of the DB"
  - "No pytest.skip path in test_wire_dict_equivalence.py -- the golden lives inside tests/golden/, so a missing golden is always a loud failure, never a standalone-CI skip"
  - "diff_db.py's correct pre-change baseline is 744 changed chips, not zero -- the pre-136.1 baseline is NOT re-pinned by this phase (D-11)"

patterns-established:
  - "A committed golden JSON with a meta block documents its own how_to_update rule in-file, so a regenerate-to-silence attempt is visibly against its own stated contract"

requirements-completed: [DATA-03]

coverage:
  - id: D1
    description: "746-chip pre-Phase-148 host->wire golden fixture committed, with a meta block documenting provenance and the no-silent-regenerate rule"
    requirement: "DATA-03"
    verification:
      - kind: unit
        ref: "manual verification script asserting 746 records, 332716-byte canonical blob, SHA-256 027a43a0dcef1085afa6a35d2500bd35556140dde4b838dfcd65bfae8cac7dab, nine-key union, vcc/vpp_volts absent"
        status: pass
    human_judgment: false
  - id: D2
    description: "Byte-identity equivalence test (5 tests) proving the live 746-chip wire-dict capture matches the golden, including a non-vacuity leg"
    requirement: "DATA-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_wire_dict_equivalence.py -- 5 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-12 review artifact's measured ## Before section (diff_db.py, check_dispatch.py, field-inventory test, firestarter info AT28C256) and Evidence Ceiling non-claim"
    requirement: "DATA-03"
    verification:
      - kind: other
        ref: "grep assertions over 148-DB-DIFF.md for all required literal strings (744, PGSZ_PAGE_SIZE, PROV01_PROTECT_METADATA, EXIT=0, 0 violations, 4.0v, NOT re-pinned, D-11, UNVERIFIED)"
        status: pass
    human_judgment: false

duration: ~12min
completed: 2026-08-19
status: complete
---

# Phase 148 Plan 01: Pre-Change Wire-Dict Golden & D-12 Review Artifact Summary

**Committed a 746-chip byte-identical host->wire golden fixture, a 5-test regression gate proving Phase 148 changes nothing on the wire, and the measured pre-change state of all four gates in the D-12 review artifact.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-08-19T09:39:00Z
- **Completed:** 2026-08-19T09:46:00Z
- **Tasks:** 3 completed
- **Files modified:** 3 (all new files)

## Accomplishments
- Captured the full 746-chip `EpromDatabase(skip_local_override=True) -> get_eprom -> convert_to_programmer` output as a committed golden fixture, reproducing the planner's independently-measured canonical values exactly: 746 records, 332,716-byte canonical blob, SHA-256 `027a43a0dcef1085afa6a35d2500bd35556140dde4b838dfcd65bfae8cac7dab`, exactly nine wire keys, `vcc`/`vpp_volts` confirmed absent from the wire.
- Wrote and committed `tests/test_wire_dict_equivalence.py` (5 tests, 0 skips) that holds the golden byte-identical through the rest of the phase, including a non-vacuity leg that proves the shared diff-reporting helper can actually fail.
- Recorded the measured `## Before` state of all four gates (`diff_db.py`, `check_dispatch.py`, `test_chip_database_field_inventory.py`, `firestarter info AT28C256`) plus the D-11 no-re-pinning note and the Evidence Ceiling non-claim in `148-DB-DIFF.md`.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule (task 1-2) and the meta repo (task 3):

1. **Task 1: Capture the 746-chip pre-change wire-dict golden** - `08d4281` (test) — `firestarter_app`
2. **Task 2: Commit the byte-identity test and prove it green on the pre-change tree** - `70d9a55` (test) — `firestarter_app`
3. **Task 3: Record the measured pre-change state in the D-12 review artifact** - `be44a32c` (docs) — meta repo

_No TDD gate applies (plan type is `execute`, not `tdd`); Task 2 carries the `tdd="true"` attribute but the plan's own instruction was to author the test already green against the unmodified pre-change tree — there is no RED phase because no production code exists yet for this test to fail against._

## Files Created/Modified
- `firestarter_app/tests/golden/wire_dict_baseline.json` - 746-record pre-Phase-148 host->wire capture with a `meta` block (source, generator, recorded_by, requirement, decision, recorded_at_head, how_to_update, why_nine_keys)
- `firestarter_app/tests/test_wire_dict_equivalence.py` - 5-test byte-identity gate: live-vs-golden equality, nine-key union guard, D-06 vcc/vpp_volts absence, non-vacuity proof, golden-exists loud-failure guard
- `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md` - D-12 review artifact `## Before` section + `## Evidence Ceiling`

## Decisions Made
- Followed the plan's pinned P-06 fixture format (full canonical JSON, `json.dumps(out, sort_keys=True, indent=2)`) and record-key scheme (`f"{mfg}|{pn}|{i}"`) exactly as specified — no deviation.
- No `pytest.skip` path added to the equivalence test, per the plan's explicit instruction that a skip here (unlike `test_audit_coverage_matrix.py`'s meta-repo-ledger skip) would hide the phase's central proof.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] `check_dispatch.py`'s actual output text does not contain the literal substring "0 violations"**
- **Found during:** Task 3
- **Issue:** The plan's Task 3 action describes the expected `check_dispatch.py` output as "0 violations", and its own `<verify>` block greps the review artifact for the literal string `0 violations`. The tool's actual measured output reads `"0 dispatch regressions; 0 consistency violations"` — true zero-violation counts, but not the contiguous substring `0 violations` (there is no case where the tool prints exactly that phrase).
- **Fix:** Pasted the tool's actual verbatim output into `148-DB-DIFF.md` (per the action's "paste actual output, not a description" instruction) and added one additional, accurate summary sentence directly beneath it: "Measured summary: 746 scanned, 736 supported, 0 violations (0 dispatch regressions + 0 consistency violations, the tool's own two named violation counters), EXIT=0." This satisfies the literal grep while remaining a true restatement of the measured, already-quoted zero counts — no data was fabricated.
- **Files modified:** `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md`
- **Verification:** `grep -q '0 violations' 148-DB-DIFF.md` passes; the preceding verbatim tool-output block is also present and unedited.
- **Committed in:** `be44a32c` (part of Task 3 commit)

---

**Total deviations:** 1 auto-fixed (Rule 3)
**Impact on plan:** Cosmetic-only — a wording mismatch between the plan's assumed tool phrasing and the tool's actual phrasing. No scope creep; no correctness impact.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

`tests/golden/wire_dict_baseline.json` and `tests/test_wire_dict_equivalence.py` are committed and green on the pre-change tree, giving Plans 02-08 a byte-identical regression gate to run against as they migrate the schema the wire dict is derived from. `148-DB-DIFF.md`'s `## Before` section is in place for later plans to append `## After`, the 56-chip mover list, the D-03 justification, and the non-claim. No blockers.

---
*Phase: 148-numeric-database-values-the-at28c-vcc-decode*
*Completed: 2026-08-19*
