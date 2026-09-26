---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
plan: 01
subsystem: docs
tags: [onboarding, beta-channel, avrdude, community-validation, firestarter_app]

# Dependency graph
requires:
  - phase: 114-disposition-no-auto-graduate-lock
    provides: "community-validation.md graduation-ladder doc (Phase 114) — the hand-off target this doc links into"
provides:
  - "firestarter_app/doc/beta-testing-install.md — stranger-oriented onboarding doc: avrdude prereq, per-board .hex table, fresh-venv install, fw -i flash, ttyACM gotcha, fw/hw smoke test, hand-off into dev test"
  - "README.md pointer link into the new doc (no matrix duplication)"
affects: [115-08-finalize-doc-from-bench-findings, 115-04-app-pypi-publish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Draft-first documentation (D-04): doc authored from known facts before the beta cut, finalized later from live bench findings"
    - "Two-layer doc pattern: operator-canonical doc lives in firestarter_app/doc/, README gets a pointer link only"

key-files:
  created:
    - firestarter_app/doc/beta-testing-install.md
  modified:
    - firestarter_app/README.md

key-decisions:
  - "Doc structure mirrors community-validation.md voice: lead paragraph naming audience/purpose, explicit 'what this is NOT' framing, tables, fenced commands"
  - "328PB-Uno guidance: recommend -b uno328pb first, fall back to -b uno only if avrdude's signature check rejects the flash — never guess/force, per D-05's 'never silently substitute' rule"
  - "README gets exactly one pointer link near the Beta / Pre-release Channel section; the per-board .hex/channel matrix is NOT duplicated (D-09)"

requirements-completed: [ONBOARD-04]

coverage:
  - id: D1
    description: "firestarter_app/doc/beta-testing-install.md exists and covers all D-09 content: per-board commands, avrdude prereq, ttyACM gotcha, correct .hex per board, dev test hand-off"
    requirement: "ONBOARD-04"
    verification:
      - kind: other
        ref: "grep -q 'firestarter_uno.hex|firestarter_leonardo.hex|firestarter_uno328pb.hex|community-validation|avrdude|ttyACM' firestarter_app/doc/beta-testing-install.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "README.md links to the new doc via a single pointer link without duplicating the per-board matrix"
    requirement: "ONBOARD-04"
    verification:
      - kind: other
        ref: "grep -c 'beta-testing-install' firestarter_app/README.md == 1"
        status: pass
    human_judgment: false

duration: 5min
completed: 2026-07-10
status: complete
---

# Phase 115 Plan 01: Beta Onboarding Doc + README Pointer Summary

**New stranger-oriented `firestarter_app/doc/beta-testing-install.md` covering the full fresh-machine install → flash → smoke → dev-test hand-off chain, plus a single non-duplicating README pointer link.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-07-10T20:03:14Z
- **Completed:** 2026-07-10T20:04:59Z
- **Tasks:** 2 completed
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments
- Drafted `firestarter_app/doc/beta-testing-install.md` (ONBOARD-04, draft-first per D-04) — a stranger-facing walkthrough covering the avrdude prerequisite, the board→`.hex`→avrdude-partno/programmer/baud table for all three bench boards (Uno, Leonardo, uno328pb), the fresh-venv `pip install --pre firestarter` recipe, the beta-auto-route `fw -i -b <board>` flash step, the `/dev/ttyACM*` controller-identity shuffle gotcha, the `fw`/`hw` smoke test (explicitly not a chip write/verify), and a closing hand-off into `community-validation.md`.
- Added a single one-line pointer link in `firestarter_app/README.md`'s "Beta / Pre-release Channel" section pointing to the new doc, with no duplication of the existing channel-selection matrix (D-09).

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule (branch `v1.21-community-chip-validation-command`):

1. **Task 1: Draft firestarter_app/doc/beta-testing-install.md** - `544b5da` (docs)
2. **Task 2: Add README pointer link (no duplication)** - `1e1df25` (docs)

_Note: no meta-repo gitlink bump was committed — that is deferred to Plan 115-08 per the plan's explicit instruction._

## Files Created/Modified
- `firestarter_app/doc/beta-testing-install.md` - New stranger-oriented onboarding doc (avrdude prereq, per-board `.hex` table, fresh-venv install commands, `fw -i` flash step, ttyACM gotcha, `fw`/`hw` smoke test, hand-off link into `community-validation.md`)
- `firestarter_app/README.md` - One-line pointer link into the new doc near the Beta / Pre-release Channel section

## Decisions Made
- Matched `community-validation.md`'s structural voice (lead paragraph naming audience + purpose, explicit "what this is NOT" framing, tables for board/`.hex` matrix, fenced command blocks) since it is the doc's structural analog per 115-PATTERNS.md.
- For the uno328pb "may actually be a plain Uno" ambiguity (D-05, `project_uno328pb_correction`), the doc instructs the reader to try `-b uno328pb` first and fall back to `-b uno` only if avrdude's own signature check rejects the flash — never silently guessing, matching the plan's "never silently substitute" language.
- Kept the doc silent on the release-engineering / `3.0.0b11` dispatch runbook itself (operator/CI ceremony, not stranger-facing content), per the plan's explicit exclusion.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`firestarter_app/doc/beta-testing-install.md` exists and is committed on the `v1.21-community-chip-validation-command` branch, so it will be included when Plan 115-02..04 land the `3.0.0b11` beta cut. Plan 115-08 will finalize this doc's content from live per-board bench findings (D-04) once Plans 115-05..07 complete their bench validation runs. No blockers for the next wave.

---
*Phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for*
*Completed: 2026-07-10*

## Self-Check: PASSED

- FOUND: firestarter_app/doc/beta-testing-install.md
- FOUND: 544b5da (firestarter_app submodule)
- FOUND: 1e1df25 (firestarter_app submodule)
