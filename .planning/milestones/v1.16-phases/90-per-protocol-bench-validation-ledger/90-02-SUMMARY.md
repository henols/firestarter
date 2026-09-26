---
phase: 90-per-protocol-bench-validation-ledger
plan: 02
subsystem: documentation
tags: [ledger, json, protocol, validation, cross-reference]

# Dependency graph
requires:
  - phase: 90-01
    provides: check_ledger.py Wave-0 gate with 0/1/2 exit-code contract
  - phase: 90-03
    provides: SAFE-04 verify-present-only evidence for ledger posture section
  - phase: 89-incremental-primitive-recompose
    provides: firmware HEAD a296195 + 89-FLASH-LEDGER.md (primitives, flash deltas)
  - phase: 88-golden-traces-dispatch-mirror
    provides: validation_matrix_spec.json family/protocol join keys
  - phase: 81-84 (v1.15 bench)
    provides: EVIDENCE.json per-chip baseline cells (join keys + chip names)

provides:
  - PROTOCOL-LEDGER.json — machine-readable 12-bucket cross-reference ledger
  - PROTOCOL-LEDGER.md — human-readable companion table (same rows)
  - check_ledger.py exits 0 against live upstream files (LEDGER-01/02/03 + D-09 gate satisfied)
  - bench-pending rows staged for Plan 04 flip to PASS post-bench-session

affects:
  - 90-04 (bench session — flips bench-pending to PASS using artifacts from Plan 04)
  - future phases consuming PROTOCOL-LEDGER.json cross-reference

# Tech tracking
tech-stack:
  added: []
  patterns:
    - compose-by-cross-reference (D-04) — ledger references upstream by key only; no SHA/verdict copied
    - bench-pending status — intermediate state between UNVERIFIED and PASS for on-hand-but-not-yet-benched rows
    - open-defect-carried status — verbatim defect carry from STATE.md; status_changed=false enforced by checker

key-files:
  created:
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.json
    - .planning/v1.16/ledger/PROTOCOL-LEDGER.md
  modified:
    - .planning/v1.16/ledger/tools/check_ledger.py (added bench-pending to _VALID_STATUSES enum)

key-decisions:
  - "bench-pending added to check_ledger.py _VALID_STATUSES — Plan 01 checker was missing this intermediate status; added as targeted enum extension (1 line)"
  - "0x08 and 0x0B rows use open-defect-carried status (not UNVERIFIED) — chips are on hand but represented by FUT-06/FUT-03 per D-07 scope decision"
  - "FM1608 bucket-id is 0x28 not 0x40 — EVIDENCE family label '0x40' is decimal-40 = hex-0x28 (NAME-04 conflation, retired); footnoted in ledger"

patterns-established:
  - "Protocol ledger pattern: JSON rows + MD companion (same data, same status, lockstep — mirrors EVIDENCE.json/.md pair)"
  - "Compose-by-cross-reference: evidence block holds chip name + op string only; SHA lives in EVIDENCE.json"

requirements-completed: [LEDGER-01, LEDGER-03]

# Metrics
duration: 20min
completed: 2026-06-26
---

# Phase 90 Plan 02: Author Protocol Ledger (Bench-Pending State) Summary

**12-bucket PROTOCOL-LEDGER.{json,md} authored with cross-reference-only composition (D-04), 4 bench-pending rows, 6 UNVERIFIED rows, 3 verbatim open-defect carries — check_ledger.py exits 0**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-26T12:25:00Z
- **Completed:** 2026-06-26T12:46:52Z
- **Tasks:** 2
- **Files modified:** 3 (2 created, 1 updated)

## Accomplishments

- Authored `PROTOCOL-LEDGER.json` with all 12 protocol bucket rows; references upstream by join key only (no SHA/verdict copied — D-04 no-copy guard confirmed by checker)
- Authored `PROTOCOL-LEDGER.md` as the human-readable companion (93 lines; mirrors same 12 rows, same statuses)
- `check_ledger.py` exits 0 against live `EVIDENCE.json` + `validation_matrix_spec.json`: LEDGER-01 (join keys resolve, 12 buckets present, D-04 no-copy), LEDGER-02/D-09 (vacuously satisfied — no PASS rows yet), LEDGER-03 (6 UNVERIFIED + 3 defect status_changed=false)

## Task Commits

1. **Task 1: Author PROTOCOL-LEDGER.json** — `520e133` (feat)
2. **Task 2: Render PROTOCOL-LEDGER.md + run checker** — `e8a8036` (feat)

## Files Created/Modified

- `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` — machine-readable 12-bucket cross-reference ledger; bench-pending state (Plan 04 flips to PASS)
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` — human-readable companion table with open-defects subsection and SAFE-04 posture note
- `.planning/v1.16/ledger/tools/check_ledger.py` — added `bench-pending` to `_VALID_STATUSES` enum (Plan 01 checker was missing this intermediate state)

## Decisions Made

- **bench-pending added to checker enum:** Plan 01's `check_ledger.py` `_VALID_STATUSES` did not include `"bench-pending"`. The plan explicitly anticipated this: "If the checker rejects 'bench-pending' as an invalid enum value, ensure 'bench-pending' is in the checker's accepted enum." Applied as a 1-line targeted fix.
- **0x08/0x0B as open-defect-carried (not UNVERIFIED):** These buckets have on-hand chips (AM27C020/2516) but are represented by open defects (FUT-06/FUT-03) per CONTEXT scope. The rows carry `open-defect-carried` status with `defect_ref` pointing to the relevant defect id; defect details live in `open_defects[]`.
- **FM1608 footnoted in ledger:** EVIDENCE.json labels FM1608 `family: "0x40 (SRAM_STD / FRAM)"` where `0x40` is decimal-40 = hex-0x28 (NAME-04 conflation retired in PROTOCOLS.md §1.10). The 0x28 row carries a `notes` field documenting this for anyone comparing the ledger to EVIDENCE.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added bench-pending to check_ledger.py _VALID_STATUSES**
- **Found during:** Task 2 (run the checker)
- **Issue:** `check_ledger.py` `_VALID_STATUSES` only contained `{"PASS", "UNVERIFIED", "FAIL-INVESTIGATE", "open-defect-carried"}` — `"bench-pending"` was missing, causing the checker to emit a LEDGER-03 enum violation for all 4 on-hand rows. The plan explicitly anticipated this and instructed to add it.
- **Fix:** Added `"bench-pending"` to `_VALID_STATUSES` in `check_ledger.py` (1 line change).
- **Files modified:** `.planning/v1.16/ledger/tools/check_ledger.py`
- **Verification:** Checker exits 0 after the fix.
- **Committed in:** `520e133` (Task 1 commit, staged together with PROTOCOL-LEDGER.json)

---

**Total deviations:** 1 auto-fixed (Rule 1 — enum gap in Wave-0 checker, anticipated by plan)
**Impact on plan:** Zero scope change; 1-line checker fix required to satisfy the plan's own acceptance criteria.

## Issues Encountered

None — plan executed cleanly. The checker enum gap was anticipated in the plan text and resolved as a Rule 1 fix.

## User Setup Required

None — pure documentation authoring, no external services.

## Next Phase Readiness

- `PROTOCOL-LEDGER.json` is staged in bench-pending state — Plan 04 (operator-gated bench session) will flip the 4 on-hand rows to PASS by recording p90 artifacts and SHA-match verdicts
- Plan 03 (SAFE-04 verify-only) was executed before this plan (90-03 complete per STATE.md); its evidence is referenced in PROTOCOL-LEDGER.md's SAFE-04 posture section
- Checker exits 0 on the pending-state ledger — LEDGER-01 and LEDGER-03 are structurally satisfied; LEDGER-02/D-09 PASS constraint is vacuously satisfied (no PASS rows yet)

## Self-Check: PASSED

Files exist:
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` ✓
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` ✓
- `check_ledger.py` exits 0 ✓

Commits exist: `520e133` (Task 1), `e8a8036` (Task 2) ✓

---
*Phase: 90-per-protocol-bench-validation-ledger*
*Completed: 2026-06-26*
