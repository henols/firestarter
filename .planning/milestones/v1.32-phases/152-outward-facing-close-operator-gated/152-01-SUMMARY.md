---
phase: 152-outward-facing-close-operator-gated
plan: 01
subsystem: testing
tags: [claim-gate, regex, honesty-ledger, python, fixtures]

requires:
  - phase: 149-firmware-page-size-seam-dual-repo-lockstep
    provides: "149-check-claims.py, the sibling gate this plan's script transcribes and renames"
provides:
  - "152-check-claims.py: the file-mode claim gate for OUT-05, armed against 152-CLAIM-CLASSES.md"
  - "152-CLAIM-CLASSES.md: the gate's human-readable contract, and the gate's first scan target"
  - "Seven fixtures proving the two added and one modified forbidden-claim labels in both directions"
affects: [152-02, 152-03, 152-04, 152-05, "every later 152 plan that authors a _DEFAULT_TARGETS or _CAVEAT_RULES member"]

tech-stack:
  added: []
  patterns:
    - "Negative-lookahead-requiring-an-adjacent-withdrawal-predicate for a claim that is mandatory in one framing and forbidden in another"
    - "Citing a gate's own forbidden-label table by row location rather than by literal label spelling, when the label name itself would trip its own pattern"

key-files:
  created:
    - .planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-CLASSES.md
    - .planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/clean_control.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/clean_control_second.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_sdp_relock_as_shipped.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_sdp_relock_bare_flag.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_issue_closed_gh21.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_issue_closed_gh11.md
    - .planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_issue_closed_gh12.md

key-decisions:
  - "issue-closed's 32 alternative dropped so D-05's gh#32 statement is expressible; gh#21/#11/#12 still fire (152-RESEARCH.md §C-5)"
  - "sdp-relock-as-shipped uses a negative lookahead (not a lookbehind, not a verb allow-list) so the mandated withdrawal sentence stays permitted while every shipped-framing phrasing is rejected (152-RESEARCH.md §C-4)"
  - "D-11's non-claim split into two independently-enforced required-caveat rows (no-at28c-part-tested, zero-d-stays-unverified) rather than one combined row"
  - "152-CLAIM-CLASSES.md cites four of its own gate's donor labels by FORBIDDEN_PATTERNS row location instead of literal spelling, because those label names are themselves hyphen-tolerant spellings of the phrase they forbid and tripped the gate on first pass"

requirements-completed: [OUT-05]

duration: 55min
completed: 2026-08-21
status: complete
---

# Phase 152 Plan 01: Claim Gate Foundation Summary

**Built OUT-05's fail-provable claim gate as a sibling of 149-check-claims.py, armed against a new contract document, and proved it rejects the deferred command's shipped-framing planted violation while permitting its mandated withdrawal sentence.**

## Performance

- **Duration:** 55 min
- **Tasks:** 3 completed
- **Files modified:** 9 created

## Accomplishments

- Authored `152-CLAIM-CLASSES.md`, the gate's human-readable contract naming all five forbidden
  claim classes by gate label (citing four donor-inherited labels by table row location rather than
  literal spelling, since those names are themselves hyphen-tolerant spellings of the phrase they
  forbid and would otherwise trip the very gate they describe).
- Copied `149-check-claims.py` to `152-check-claims.py` and applied all seven enumerated edit sites:
  the four mandatory renames, two added forbidden rows for the deferred command's shipped-framing
  claim (command-first and bare-flag forms, each guarded by its own negative lookahead requiring an
  adjacent withdrawal predicate), one modified row (`issue-closed`, narrowed), and three
  required-caveat rows pre-populated across every basename the phase will ever scan.
- Authored and individually probed seven fixtures: two clean controls proving both narrowings permit
  exactly what later plans must say, and five planted violations each failing for exactly one
  labelled reason with demonstrated per-label leg isolation between the command-first and bare-flag rows.
- Verified in-process: the gate rejects 11/11 of the researched shipped-framing phrasings and permits
  7/7 of the researched withdrawal phrasings; an empty env seam and a missing env-seam target each
  exit non-zero, the latter naming the missing path.

## Task Commits

Each task was committed atomically:

1. **Task 1: Author 152-CLAIM-CLASSES.md** - `ad6af1bd` (docs)
2. **Task 2: Copy 149-check-claims.py to 152-check-claims.py, apply 7 edit sites** - `5c29e358` (feat) — folds in a Rule 1 fix to `152-CLAIM-CLASSES.md` discovered while arming the gate against it
3. **Task 3: Author the seven fixtures** - `a17959ce` (test)

_No TDD tasks in this plan; no plan-metadata commit yet (see final commit below)._

## Files Created/Modified

- `.planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-CLASSES.md` - the gate's contract, naming every forbidden label and required-caveat row, and the gate's first scan target
- `.planning/phases/152-outward-facing-close-operator-gated/152-check-claims.py` - the OUT-05 file-mode gate: 19 forbidden-phrase rows, 3 required-caveat rows, fail-closed and never-vacuous
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/clean_control.md` - control 1: all three caveats, the withdrawal phrasing naming Backlog 999.28, and the gh#32 natural-past-tense statement
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/clean_control_second.md` - control 2: a different withdrawal predicate, the parenthetical gh#32 form, and the two D-11-exempted shipped-behaviour statements
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_sdp_relock_as_shipped.md` - the specified planted violation, taken verbatim from ROADMAP.md's pre-amendment criterion 1
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_sdp_relock_bare_flag.md` - the bare-flag companion violation, proving leg isolation from the row above
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_issue_closed_gh21.md` - proves the narrowed row still fires on gh#21
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_issue_closed_gh11.md` - proves the narrowed row still fires on gh#11
- `.planning/phases/152-outward-facing-close-operator-gated/fixtures/planted_issue_closed_gh12.md` - proves the narrowed row still fires on gh#12

## Decisions Made

- Kept `152-check-claims.py` table row 10's `(?<!software-)` lookbehind verbatim per 152-RESEARCH.md §C-6 rather than re-deriving a new spelling, since the compound phrase is already this milestone's established vocabulary in three other measured places.
- Did not port Phase 137's `UNARMED: ... return 0` branch; the gate has no exit-0-on-nothing-scanned path.
- Pre-populated `_CAVEAT_RULES` for every basename this phase will ever produce (through `152-20-SUMMARY.md`) in this plan, so no later plan edits that map and no two later plans can collide on it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `152-CLAIM-CLASSES.md`'s own prose tripped the gate it describes**
- **Found during:** Task 2, arming the gate against its first target and running it for the first time.
- **Issue:** Several `FORBIDDEN_PATTERNS` labels are themselves hyphenated spellings of the exact
  phrase they forbid (their compiled pattern class-matches a hyphen equivalently to whitespace, or
  keys on a bare completion-claim word with only a lookbehind exception for one specific prefix).
  Writing those label names as plain identifier text in the contract document — itself a live scan
  target — reproduced the forbidden phrase mechanically, and two other sentences used the bare
  completion-claim word outside its permitted compound.
- **Fix:** Rewrote the four affected table cells to cite the offending rows by `FORBIDDEN_PATTERNS`
  table location (e.g. "table row 10") instead of by literal label spelling, and rephrased the two
  bare-word prose instances to avoid the word entirely. This mirrors the same by-location citation
  discipline the file already uses for class (e)'s tested phrasings, applied one layer further in.
- **Files modified:** `152-CLAIM-CLASSES.md`
- **Commit:** `5c29e358`

### None Other

All other work executed exactly as planned; no auth gates encountered (this plan is offline,
stdlib-only Python with no network or package-manager calls).

## Known Stubs

None. Every file this plan produces is complete and load-bearing for later plans in this phase.

## Threat Flags

None. The threat model's four `mitigate` items (T-152-01 through T-152-04) are all satisfied by
mechanisms transcribed or authored in this plan, and T-152-SC records that no package install
occurred.

This ships software-proven and unvalidated on silicon.

## Self-Check: PASSED

All 10 created files found on disk; all 3 task commits (`ad6af1bd`, `5c29e358`, `a17959ce`) found in
`git log --oneline --all`. This SUMMARY itself was verified against `152-check-claims.py` via
`FIRESTARTER_CLAIMSCAN_TARGETS_152` before this section was appended — PASS, rc=0.
