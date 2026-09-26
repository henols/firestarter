---
phase: 137-close-honesty-ledger-claim-gate-gh12-followup
plan: 06
subsystem: testing
tags: [claim-gate, ci-parity, honesty-ledger, phase-close, v1.30, milestone-close]

# Dependency graph
requires:
  - phase: 137-close-honesty-ledger-claim-gate-gh12-followup (plans 01-05)
    provides: "check_permitted_claims.py (137-01), the host-side diagnostic_report.py scan (137-02), 137-LEDGER.md (137-03), 137-RELEASE-NOTES-app.md + 137-DECISION.md (137-04), 137-GH12-COMMENT.md frozen + reviewed (137-05) -- all four of the claim gate's default targets, and every prior finding this record carries forward"
provides:
  - "CLOSE-01 discharged: the claim gate genuinely ARMED and GREEN against all four real closing artifacts, for the first time in this milestone"
  - "137-CI-PARITY.md: the whole-milestone-diff CI-parity recipe, run one final time, every metric reconciled against the Phase 136.1 baseline"
  - "137-RECORD.md: Phase 137's own closing record -- requirement accounting, six ROADMAP success criteria discharged, corrections carried forward, residuals, Evidence Ceiling restated, hand-off"
  - "v1.30-OPERATOR-BATCH.md finalized as one list, ready for the operator immediately before /gsd-complete-milestone"
affects: [gsd-complete-milestone, v1.30-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Armed-vs-UNARMED test replacement: a test whose own docstring pre-announced its own future edit (\"stays green until 137-06 makes all four exist\") was replaced, not merely updated, once its precondition became true"
    - "Whole-milestone CI-parity reconciliation table: every metric diffed against the last prior phase's own close, with every non-zero delta traced to a named, already-disclosed cause rather than silently accepted"

key-files:
  created:
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-CI-PARITY.md
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-RECORD.md
  modified:
    - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/test_check_permitted_claims_v130.py
    - .planning/v1.30-OPERATOR-BATCH.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Followed the dispatching orchestrator's explicit, repeated instruction (requirement_ticking_scope, critical_facts) that CLOSE-06 must remain [ ] open, OVER this plan's own PLAN.md text, which -- in Task 3's action steps, acceptance criteria, and step-6 hand-off narration -- assumes/asserts a 56/56-ticked, zero-open final state. The orchestrator's instruction is authoritative; the plan's own acceptance criterion (grep count == 0) is a measured-stale artifact of this plan having been authored before 137-05 finalized the hold-open decision, and is NOT satisfied by design. Documented in full, with both readings, in 137-RECORD.md section 1."
  - "Did not run the redundant standalone 'pytest tests/ -o addopts=\"\" -q' cross-check that prior CI-PARITY docs' shape included as a nice-to-have step 3 -- ci_replica_venv.sh's own leg 5 already IS that exact invocation (CI's exact args) and is the authoritative measurement; ran it anyway once, non-blocking, and it independently reproduced 1508 passed, confirming leg 5's own count rather than substituting for it."

requirements-completed: [CLOSE-01]

coverage:
  - id: D1
    description: "The claim gate, run with no arguments (its real default targets), is ARMED and GREEN, printing a PASS: line naming all four of this milestone's own closing artifacts -- the literal discharge of CLOSE-01"
    requirement: "CLOSE-01"
    verification:
      - kind: unit
        ref: "python3 check_permitted_claims.py (no args) -> PASS: scanned 137-LEDGER.md, 137-DECISION.md, 137-RELEASE-NOTES-app.md, 137-GH12-COMMENT.md; 4 file(s) carry the required silicon caveat, exit 0"
        status: pass
      - kind: unit
        ref: "test_check_permitted_claims_v130.py::test_armed_and_green_against_the_four_real_artifacts (replacing test_unarmed_when_zero_of_four_default_targets_exist), 11/11 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "The CI-parity recipe was run one final time over the whole milestone diff, every metric reconciled against the Phase 136.1 baseline, mypy watermark NOT moved"
    requirement: null
    verification:
      - kind: unit
        ref: "tools/ci_replica_venv.sh -> CI-REPLICA: PASS; mypy 33/35 (watermark unmoved), checked 129, 1508 passed, coverage 82.14%"
        status: pass
    human_judgment: false
  - id: D3
    description: "137-RECORD.md authored with all six mandated sections; project-wide requirement count freshly measured and reconciled against the plan's own stale expectation"
    requirement: null
    verification:
      - kind: other
        ref: "grep -c '^- \\[x\\]' REQUIREMENTS.md -> 55; grep -c '^- \\[ \\]' REQUIREMENTS.md -> 1 (CLOSE-06, held open by design)"
        status: pass
    human_judgment: false

# Metrics
duration: ~50min (includes ~30min waiting on tools/ci_replica_venv.sh's full mypy+pytest+coverage run and one redundant standalone re-run)
completed: 2026-08-05
status: complete
---

# Phase 137 Plan 06: Phase Close — Claim Gate Armed, Final CI-Parity, Operator Batch, Record Summary

**Armed and greened the v1.30 claim gate against its own four real closing artifacts for the first time this milestone (CLOSE-01), ran the whole-milestone CI-parity recipe a final time with every metric reconciled, and authored Phase 137's own closing record — leaving v1.30 at 55/56 requirements complete, by design, with CLOSE-06 openly outstanding and its single closing action already recorded.**

## Performance

- **Duration:** ~50 min (includes ~30 min of wall-clock time waiting on `tools/ci_replica_venv.sh`'s
  full mypy + pytest + coverage run, plus one non-blocking standalone re-run of the full suite)
- **Started:** 2026-08-05T20:17:00Z (plan/context read)
- **Completed:** 2026-08-05T20:42:00Z
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 5 (2 new: `137-CI-PARITY.md`, `137-RECORD.md`; 3 modified: the claim-gate test
  module, `v1.30-OPERATOR-BATCH.md`, `REQUIREMENTS.md`)

## Accomplishments

- **CLOSE-01 discharged — the literal, first-ever real-defaults run of the claim gate in this
  milestone.** `python3 check_permitted_claims.py`, invoked with no arguments (its real default
  targets) from the phase directory, exits 0 and prints:
  ```
  PASS: scanned 137-LEDGER.md, 137-DECISION.md, 137-RELEASE-NOTES-app.md, 137-GH12-COMMENT.md; 4
  file(s) carry the required silicon caveat (this PASS is the mechanizable half of the honesty ledger
  discipline only -- see the module docstring's explicit non-claim)
  ```
  `test_unarmed_when_zero_of_four_default_targets_exist` — whose own docstring had pre-announced this
  exact edit ("stays green until 137-06 makes all four exist") — was replaced with
  `test_armed_and_green_against_the_four_real_artifacts`, asserting exit 0, `PASS:`, and all four
  basenames present. Full paired suite: 11/11 passed. `grep -c
  'test_unarmed_when_zero_of_four_default_targets_exist' test_check_permitted_claims_v130.py` → 0
  (fully replaced, no dangling reference).

- **Final whole-milestone CI-parity recipe, every metric reconciled, not silently asserted unchanged.**
  `tools/ci_parity.sh`: legs 1-3 exit 0, leg 4 exits 2 (the documented devcontainer ambient-numpy
  shape, unchanged from every prior phase's own recorded run). `tools/ci_replica_venv.sh`:
  **CI-REPLICA: PASS** — mypy **33/35** (watermark explicitly NOT moved, per this task's own
  instruction), checked **129** source files, full suite **1508 passed**, coverage **82.14%**, ruff
  clean. Against the Phase 136.1 baseline (33/35, checked 132, 1504 passed, 82.14%): the checked-file
  count fell 132→129 (**reconciled**: plan 137-02's `tests/fixtures/` mypy exclude, a genuine,
  previously-disclosed, floor-respecting reduction — still 9 above the 120 floor); the suite count
  rose 1504→1508 (**reconciled**: exactly plan 137-02's four new tests, zero other plans in this phase
  touch the submodule). The 43/41/84 SDP partition was independently re-derived three ways this plan
  alone (the invariant test suite, a live `sdp_capability_for_entry` pass over the full DB, and a
  zero-nonzero-chip-id sweep) — unchanged across the entire milestone. Firmware submodule confirmed
  untouched (`git -C /workspaces/firestarter status --porcelain` empty); zero new package installs
  confirmed (`git log --oneline -- '*.txt' pyproject.toml setup.py` empty across this phase's whole
  commit range).

- **`137-RECORD.md` authored** with all six mandated sections: requirement accounting (all seven of
  this phase's own requirements, which plan ticked each, cited evidence); the ROADMAP's six success
  criteria quoted verbatim and discharged with named evidence; corrections carried forward (the six
  `137-LEDGER.md`-mandated corrections restated in one line each, plus this phase's own two — the
  RELOCK-07 fifth citation drift and the CLOSE-06 posting-precondition timing decision); residuals
  (mypy watermark ratchet unowned, C-1's filed todo, gh#20's still-open defect, CLOSE-06's exact
  closing command); the Evidence Ceiling restated verbatim from `134-RECORD.md` §7; and hand-off
  (project-wide count, the two remaining operator actions).

- **`v1.30-OPERATOR-BATCH.md` finalized** with a "PHASE 137 COMPLETE" section presenting the two
  remaining operator actions (A-2: push + open the beta PR; A-1's named `gh issue comment` follow-up)
  as one list, per the file's own standing header instruction, immediately before
  `/gsd-complete-milestone`. Confirmed A-1's row already accurately reflects 137-05's actual outcome
  (wording approved, posting held) and C-1's row already accurately reflects 137-04's disposition
  (defer-with-owner) — neither needed correction, only confirmation, per this task's own instruction.

- **CLOSE-01 ticked in `REQUIREMENTS.md`**, citing the claim gate's live `PASS:` line as evidence.
  **CLOSE-06 deliberately left `[ ]` open** — not ticked by this plan, per the dispatching
  orchestrator's explicit, repeated instruction. Project-wide requirement state, freshly measured:
  **55 ticked `[x]` / 1 open `[ ]`** (`CLOSE-06`).

## Task Commits

Each task was committed atomically:

1. **Task 1: Update the claim-gate test from UNARMED to ARMED-and-green** - `0efd4072` (test)
2. **Task 2: Final whole-milestone CI-parity recipe** - `01fbb57a` (docs)
3. **Task 3: Tick CLOSE-01, finalize operator batch, author 137-RECORD.md** - `22ac6237` (docs)

**Plan metadata:** (this commit, following SUMMARY write)

## Files Created/Modified

- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/test_check_permitted_claims_v130.py`
  — replaced the stale UNARMED-expecting test with an ARMED-and-green one; module docstring's numbered
  coverage list updated to match (still 11 legs total).
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-CI-PARITY.md` — the final
  whole-milestone CI-parity record, Before (Phase 136.1 close) / After (this plan) sections, every
  metric reconciled, plus a whole-milestone summary table (Phases 131 through 137).
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-RECORD.md` — Phase 137's
  closing record, six sections.
- `.planning/v1.30-OPERATOR-BATCH.md` — added the "PHASE 137 COMPLETE" closing section; no other
  section altered (B-1, B-2, C-2, C-3, D-1, D-2, E-1, E-2 left untouched, per this task's own
  instruction).
- `.planning/REQUIREMENTS.md` — CLOSE-01 ticked `[x]` with evidence citation; traceability row updated
  to Complete. CLOSE-06 left `[ ]` open, unchanged. No other requirement checkbox touched.

## Decisions Made

See `key-decisions` in frontmatter above for the full rationale on each. Summary:
- Followed the orchestrator's explicit CLOSE-06-stays-open instruction over this plan's own
  PLAN.md text where the two conflict (documented fully in `137-RECORD.md` §1, not silently
  reconciled).
- Ran one non-blocking standalone full-suite re-run beyond what the task strictly required, as an
  independent cross-check of `ci_replica_venv.sh`'s own leg 5 count (both independently measured
  1508 passed).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 — plan's own acceptance criterion and step-6 narration are measured-wrong] Task 3's
literal acceptance criteria and step-6 hand-off text both expect a 56/56-ticked, zero-open final
state; the correct, orchestrator-mandated state is 55/56 ticked, CLOSE-06 open**
- **Found during:** Task 3, before ticking CLOSE-01
- **Issue:** `137-06-PLAN.md`'s Task 3 action text says "the project-wide requirement count (should
  now read 56/56 ticked, 0 open — confirm via `grep -c ...`)" and its own automated `<verify>` block
  literally asserts `grep -c '^- \[ \] \*\*CLOSE-\|^- \[ \] \*\*RELOCK-' .planning/REQUIREMENTS.md`
  must equal `"0"`. Both directly contradict this plan's own dispatching context
  (`<requirement_ticking_scope>`: "This plan may mark Complete EXACTLY ONE requirement: CLOSE-01...
  CLOSE-06 must remain `[ ]` open... Project-wide must read 55 ticked / 1 open when you finish") and
  contradict 137-05's own SUMMARY, which had already stated the correct expectation verbatim ("v1.30
  will close at 55/56 once 137-06 discharges CLOSE-01, with CLOSE-06 openly outstanding"). The
  PLAN.md text for this specific criterion was very likely drafted before 137-05's own execution
  finalized the operator's hold-open decision for CLOSE-06, and was never updated to match.
- **Fix:** Followed the orchestrator's explicit, repeated instruction (authoritative over the plan
  text) — ticked CLOSE-01 only, left CLOSE-06 `[ ]` open. Did NOT tick CLOSE-06 to force the plan's
  own stale script to report 0/56-56 — doing so would itself be the exact overclaim class ("the
  reply is posted" when it is not) this milestone's honesty discipline exists to catch.
- **Verification:** `grep -c '^- \[ \] \*\*CLOSE-\|^- \[ \] \*\*RELOCK-' .planning/REQUIREMENTS.md`
  → `1` (CLOSE-06 only) — the correct, expected value given the orchestrator's own instruction, NOT
  the `0` the plan's stale acceptance criterion names. `grep -c '^- \[x\]'` → 55, `grep -c '^- \[ \]'`
  → 1. Documented in full, with both readings, in `137-RECORD.md` §1.
- **Files modified:** none beyond the plan's own declared scope; this deviation is a documentation/
  verification-interpretation correction, not a code change.
- **Committed in:** `22ac6237` (Task 3 commit)

---

**Total deviations:** 1 (a plan-text staleness correction, not a Rule 1-3 code/bug fix in the usual
sense — recorded here because the deviation-rules protocol requires tracking any departure from the
plan's own literal acceptance criteria, even when the departure is mandated by a higher-priority
instruction).
**Impact on plan:** None on the milestone's actual state — the orchestrator's instruction and 137-05's
own prior SUMMARY both already correctly anticipated 55/56; only this plan's own PLAN.md text (Task 3's
acceptance criteria and step-6 narration) had not been updated to match. No scope creep; no requirement
was ticked or left untouched contrary to instruction.

## Issues Encountered

- `tools/ci_replica_venv.sh`'s leg 5 (the full pytest + coverage run) took longer than expected in this
  environment (~3.5 minutes wall clock for the outer run, with a nested nested nested subprocess pytest
  invocation from `test_skip_census.py` that itself shells out to `gh issue list` for a dedup-fingerprint
  smoke check) — resolved by waiting; no code issue, purely a duration observation for future plans
  budgeting CI-parity wall-clock time in this devcontainer.

## User Setup Required

None — no external service configuration required. This plan makes no `gh` write calls, no pushes, no
publishes (per the absolute prohibition in this plan's dispatch context).

## Next Phase Readiness

- **v1.30 is ready for `/gsd-complete-milestone`.** All seven active phases (131, 132, 133, 134, 136,
  136.1, 137) are complete. Project-wide requirement state: **55 ticked / 1 open** (`CLOSE-06`, held
  open by explicit operator decision, with its own annotated row and the exact single closing command
  already recorded in both `REQUIREMENTS.md` and `v1.30-OPERATOR-BATCH.md`).
- **Two operator actions remain**, both named in `v1.30-OPERATOR-BATCH.md`'s new "PHASE 137 COMPLETE"
  section: A-2 (push the branch, open the beta PR) and A-1's follow-up `gh issue comment` command (run
  only after A-2's push confirms the removal is live).
- No sub-repo commit was made by this plan (pure meta-repo documentation; `firestarter_app`'s tracked
  gitlink confirmed unchanged before and after, `cc036e8`).
- This is the last plan of the last phase — no further Phase 137 work remains.

---
*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Completed: 2026-08-05*

## Self-Check: PASSED

- FOUND: `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-CI-PARITY.md`
- FOUND: `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-RECORD.md`
- FOUND commit `0efd4072` (Task 1)
- FOUND commit `01fbb57a` (Task 2)
- FOUND commit `22ac6237` (Task 3)
- Re-confirmed `python3 check_permitted_claims.py` (no args, from the phase directory) still exits 0
  with `PASS:` naming all four real artifacts
- Re-confirmed `grep -c '^- \[x\]' .planning/REQUIREMENTS.md` → 55, `grep -c '^- \[ \]'` → 1
- Re-confirmed `grep -q '\[x\] \*\*CLOSE-01' .planning/REQUIREMENTS.md` → match found
