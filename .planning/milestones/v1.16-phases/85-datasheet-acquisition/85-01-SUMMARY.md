---
phase: 85-datasheet-acquisition
plan: 01
subsystem: datasheets
tags: [datasheets, validation, shell, bash, firestarter-firmware]

requires: []
provides:
  - v1.16-protocol-first-architecture-rebuild branch forked from beta in the firestarter sub-repo
  - datasheets/datasheets-check.sh: Wave-0 structural gate covering DSHEET-01/02/03 + SAFE-05
  - datasheets/.gitkeep: empty directory marker committed to firestarter sub-repo
affects: [85-02, 85-03, 86-naming-pass, 87-golden-traces]

tech-stack:
  added: []
  patterns:
    - "datasheets-check.sh: %PDF magic-byte check + bucket-dir existence + README exclusion assertions for the phase gate"

key-files:
  created:
    - firestarter/datasheets/datasheets-check.sh
    - firestarter/datasheets/.gitkeep
  modified: []

key-decisions:
  - "v1.16-protocol-first-architecture-rebuild branch forked from beta (not v1.15 tip) in the firestarter sub-repo"
  - "datasheets-check.sh exits non-zero (RED) until all 12 bucket dirs and README are populated — correct Wave-0 state"
  - "SAFE-05 verified: only datasheets/ paths staged/committed; core.* crash dumps and .pio/ artifacts left untracked"
  - "set -euo pipefail + %PDF magic-byte check (head -c4) + forbidden-bucket compgen guard + README exclusion assertions"

patterns-established:
  - "Wave-0 gate: check script exits RED before PDF population; GREEN after — same pattern for DSHEET-01/02/03"
  - "SAFE-05 discipline: explicit per-file git add (never git add -A) verified by git diff --cached --name-only pre-commit"

requirements-completed: [SAFE-05]

duration: 4min
completed: 2026-06-25
---

# Phase 85 Plan 01: Datasheet Acquisition Scaffold Summary

**v1.16 branch forked from beta + `datasheets-check.sh` Wave-0 gate authored enforcing 12-bucket %PDF contract (correctly RED until Plans 02/03 populate the tree)**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-06-25T14:33:00Z
- **Completed:** 2026-06-25T14:36:11Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Forked `v1.16-protocol-first-architecture-rebuild` off `beta` in the firestarter sub-repo (not from the v1.15 tip)
- Authored `datasheets/datasheets-check.sh` (100 lines, executable, `set -euo pipefail`) covering all four requirements: DSHEET-01 (%PDF + size>1k check per bucket), DSHEET-02 (same check for no-silicon buckets), DSHEET-03 (README existence + README exclusion mentions + README→file cross-reference), SAFE-05 (forbidden bucket dir absence)
- Committed only `datasheets/` paths inside the firestarter sub-repo on the v1.16 branch (SAFE-05 invariant holds: commit `11a7c7f` shows only `datasheets/.gitkeep` and `datasheets/datasheets-check.sh`)

## Task Commits

1. **Task 1: Fork the v1.16 milestone branch** — branch-only operation, no commit needed
2. **Task 2: Author datasheets-check.sh and .gitkeep** — files authored, staged in Task 3
3. **Task 3: Commit the Wave-0 scaffold** — `11a7c7f` (docs: wave-0 datasheets validation scaffold) inside firestarter sub-repo

## Files Created/Modified

- `firestarter/datasheets/datasheets-check.sh` — Wave-0 structural gate; 100 lines; checks 12 expected buckets (all named explicitly), 6 forbidden buckets (0x35/0x39/0x11/0x2A/0x2B/0x2C), README existence and exclusion mentions, %PDF magic-byte per PDF; exits RED until Plans 02/03 populate the tree
- `firestarter/datasheets/.gitkeep` — empty directory marker so the datasheets/ dir is committable before bucket folders are created

## Decisions Made

- Branch forked from `beta` as specified in STATE.md §"v1.16 Scope Notes" and ROADMAP.md §"v1.16". The v1.15 branch was NOT the base because the v1.14 beta cut was deferred and beta has the v1.13 → Phase 70 lockstep merge.
- Script uses `set -euo pipefail` for strict error handling. The `compgen -G` guard for forbidden bucket detection handles both `0x35/` and `0x35-SOMETHING/` folder name patterns.
- The README cross-reference check (section 4) is WARN not FAIL, so mid-download runs do not block on partial tree states.
- `datasheets/.gitkeep` used instead of creating bucket folders now — bucket creation belongs to Plan 02 (PDF download).

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 85-02 can now begin: download the 17 PDFs into the 12 bucket folders, run `datasheets-check.sh` after each batch to confirm DSHEET-01/02 green.
- Plan 85-03 can then author `datasheets/README.md` and achieve `datasheets-check: PASS`.
- The v1.16 branch is active in the firestarter sub-repo — all subsequent Phase 85 commits land on the correct branch.

## Known Stubs

None — this plan delivers only the validation scaffold; no PDFs or README yet (intentional: those are Plans 02 and 03).

## Threat Flags

None — static-asset phase, zero executable surface, zero input parsing. T-85-SC1 (downloaded PDF masquerade) is mitigated by the %PDF magic-byte check in `datasheets-check.sh` which Plans 02 and 03 will run.

## Self-Check: PASSED

- `firestarter/datasheets/datasheets-check.sh` — FOUND
- `firestarter/datasheets/.gitkeep` — FOUND
- `85-01-SUMMARY.md` — FOUND
- Commit `11a7c7f` (firestarter sub-repo) — FOUND
- Branch `v1.16-protocol-first-architecture-rebuild` active in firestarter — VERIFIED

---
*Phase: 85-datasheet-acquisition*
*Completed: 2026-06-25*
