---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
plan: 11
subsystem: testing
tags: [documentation, sdp, gh-triage, ci-parity, phase-record, backlog]

# Dependency graph
requires:
  - phase: 134-09
    provides: "tests/test_sdp_recovery_wording.py -- LEG-14's committed, scoped gate"
  - phase: 134-10
    provides: "the six laundering-route tests (R1-R6, LEG-17) and the LEG-13 N-of-M pinning
      test -- the phase's final engine + test source, commit 2b7a702"
provides:
  - "134-GH20-TRIAGE.md -- LEG-18's finding: gh#20 triaged against the baseline-transition
    gate, the banner change (4 of 4 -> 6 of 10, correcting D-20's stated 5), D-11's named
    orphaned dedup_fingerprint cost, and the Evidence Ceiling restated verbatim"
  - ".planning/todos/pending/at28c256-write-path-failure-gh20.md -- the underlying AT28C256
    write-path defect filed as a backlog item with Owner: henols"
  - "ROADMAP.md Backlog 999.29 -- cross-links both artifacts"
  - "134-CI-PARITY.md's ## After (post-edit) section -- real ci-replica numbers: mypy
    unchanged 33/35 across the whole phase, checked 124->126, tests 1338->1437 (+99),
    coverage 81.84%->82.12%, 29 new production symbols, 2 new test files"
  - "134-RECORD.md -- the phase's closing record: 18/18 LEG requirements accounted, D-01..D-20
    decision coverage (D-08 superseded-by-D-20 stated plainly, D-18's REFUSE refinement, P-03
    prevention 4 overturned), five ROADMAP success criteria at the Evidence Ceiling, seven
    corrections with both readings, seven non-vacuity obligations, six residuals, the
    Evidence Ceiling restated verbatim"
  - "LEG-18 ticked Complete -- the phase's final requirement; 14/14 LEG-01..18 rows Complete
    for this phase, 18/18 total across Phases 133+134"
affects: [137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A backlog item's owner is named explicitly (Owner: henols) precisely so a real,
      still-open community defect does not become another unowned acknowledgement -- the
      same discipline this project's own backlog already carries for write-sdp-relock."
    - "Measuring a plan's own claimed exemption-row/registry-count text against the live
      source before restating it in a record (D-12's predicted 'five' rows vs the two
      actually dischargeable, _DECLARED_REGISTRY_COUNT vs the real _POLICED_REGISTRY_COUNT/
      _DECLARED_NON_REGISTRY_COUNT names) -- re-derive from a live diff, never copy a design
      document's number forward uncritically."

key-files:
  created:
    - .planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-GH20-TRIAGE.md
    - .planning/todos/pending/at28c256-write-path-failure-gh20.md
    - .planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-RECORD.md
  modified:
    - .planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-CI-PARITY.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Re-verified gh#20 read-only (gh issue view 20) at execution time rather than trusting
    134-RESEARCH.md's earlier capture -- confirmed byte-identical (still OPEN, 0 comments,
    same fields), so the triage document's literals are independently re-confirmed, not
    merely copied forward."
  - "Named the ladder_state finding (134-03/134-06's own carried-forward residual -- a
    genuinely-passing ALLOW chip no longer reaches community-reported) as its OWN residual
    row in 134-RECORD.md rather than folding it into the gh#20 backlog item this plan's Task
    1 scope named -- the two are unrelated defects (one is a real community report about a
    specific bench, the other is a diagnostic_report.py classification-bucket gap), and the
    plan's own Task 1 action text scoped the backlog filing to the AT28C256 defect only."
  - "Measured live (not inherited from 133-CONTEXT.md D-12's prediction) that only TWO of the
    seven Phase-133-authored OP_SDP_LOCK/OP_SDP_UNLOCK parity-exemption rows were dischargeable
    by this phase (both against derive_plan), not the five D-12 anticipated -- confirmed via a
    direct diff of test_op_registration_parity.py between the Phase-133 close commit (57e8eb5)
    and the phase's final source."

requirements-completed: [LEG-18]

coverage:
  - id: D1
    description: "gh#20 triaged against the baseline-transition gate: the finding recorded
      in 134-GH20-TRIAGE.md, stating what the tool would now do on that bench (no lock ever
      emitted) without diagnosing the chip or claiming the lock inhibited any write"
    requirement: LEG-18
    verification:
      - kind: other
        ref: "manual -- 134-GH20-TRIAGE.md exists, contains 3.0.0b14/Rev 2.3/00e121446ceb/11800/13700/4 of 4/6 of 10, and 'no lock is ever emitted'"
        status: pass
    human_judgment: false
  - id: D2
    description: "The underlying AT28C256 write-path defect filed as a backlog item with a
      named owner (Owner: henols), separate from the triage finding, cross-linked from
      ROADMAP.md Backlog 999.29"
    requirement: LEG-18
    verification:
      - kind: other
        ref: "manual -- at28c256-write-path-failure-gh20.md exists with 'Owner: henols'; ROADMAP.md grep -c '999\\.' increased by exactly 1"
        status: pass
    human_judgment: false
  - id: D3
    description: "134-CI-PARITY.md's after-half recorded from real tools/ci_parity.sh and
      tools/ci_replica_venv.sh runs: mypy 33/35 unchanged across the whole phase, checked
      124->126, a delta table naming mypy/checked/tests/coverage before vs after"
    verification:
      - kind: other
        ref: "manual -- tools/ci_replica_venv.sh run live: mypy errors: 33 (watermark: 35), checked 126 source files, 1437 passed, 82.12% coverage"
        status: pass
    human_judgment: false
  - id: D4
    description: "134-RECORD.md carries every correction with both readings (four-vs-six
      step count, exit precedence, MIN_CHECKED_SOURCE_FILES as a floor, the measured
      exemption-row count), all seven non-vacuity obligations, and the Evidence Ceiling
      restated verbatim; LEG-18 ticked as the only requirement row this plan changed"
    requirement: LEG-18
    verification:
      - kind: other
        ref: "manual -- grep -c '^- \\[x\\] \\*\\*LEG-' .planning/REQUIREMENTS.md returns 18; git diff confined to the LEG-18 row + its Traceability row"
        status: pass
    human_judgment: false

# Metrics
duration: 29min
completed: 2026-08-04
status: complete
---

# Phase 134 Plan 11: gh#20 Triage, the Owned Backlog Item, the CI-Parity After-Record, and the Phase Record Summary

**Closed LEG-18 -- gh#20's finding recorded against the new baseline-transition gate (banner drops
from "4 of 4" to "6 of 10", correcting D-20's stated "5 of 10"), the underlying AT28C256 defect
filed as a named-owner backlog item, the CI-parity after-record showing zero mypy delta across the
whole phase (33/35 unchanged) despite 29 new production symbols, and `134-RECORD.md` closing the
phase with every correction stated at both readings and the Evidence Ceiling restated verbatim.**

## Performance

- **Duration:** 29 min
- **Started:** 2026-08-04T20:34:20Z (Task 1's commit)
- **Completed:** 2026-08-04T21:03:34Z (Task 3's commit)
- **Tasks:** 3
- **Files modified:** 6 (3 created, 3 modified), all in the meta repo — this plan touches no
  file inside either submodule

## Accomplishments

- Re-verified gh#20 read-only (`gh issue view 20 --repo henols/firestarter_prom`) — confirmed
  byte-identical to `134-RESEARCH.md`'s earlier capture (still OPEN, 0 comments, same fields).
- Wrote `134-GH20-TRIAGE.md`: the report as measured, the triage against `_baseline_closes_sdp_gate`
  (no lock is ever emitted on this bench), the banner change (4 of 4 -> 6 of 10, with the D-20
  correction stated), D-11's named orphaned `dedup_fingerprint` cost (`00e121446ceb`), the Evidence
  Ceiling restated verbatim, and the explicit statement that the leg is NOT protected by the chip-ID
  gate (this bench's own `id NA` step, all 43 ALLOW chips measured at `chip-id == 0`).
- Filed `.planning/todos/pending/at28c256-write-path-failure-gh20.md` with `Owner: henols`, and a
  cross-linking `999.29` row in `ROADMAP.md`'s `## Backlog` section (scoped `Edit`, single-hunk,
  additive-only).
- Appended `134-CI-PARITY.md`'s `## After (post-edit)` section: `ci_parity.sh` legs unchanged in
  shape; `ci_replica_venv.sh` — **mypy errors: 33 (watermark: 35), checked 126 source files**
  (unchanged mypy count across the ENTIRE phase, despite 29 new production symbols measured live via
  `git diff` against the pre-134 HEAD); `pytest tests/`: 1338 -> 1437 passed (+99), coverage 81.84%
  -> 82.12%; a delta table naming mypy/checked/tests/coverage before vs after plus the new-file and
  new-symbol counts.
- Wrote `134-RECORD.md`: §1 requirement accounting (all 14 LEG-01..18 rows for this phase, each with
  its ticking plan and named evidence; LEG-09/10/11/15 re-verified byte-identically green by a live
  re-run, not merely inherited); §2 all twenty decisions D-01..D-20 (D-08's `sdp-unlock` clause
  stated as measured-wrong and superseded by D-20, with the LEG-09 distinction that makes the
  supersession safe; D-18's REFUSE-chip refinement with its four measurements; P-03 prevention 4
  named as overturned); §3 the five ROADMAP success criteria at the Evidence Ceiling, both readings
  for criterion 1 (four vs six) and the caveat for criterion 2 (exit 1 unreachable until D-14); §4
  seven corrections with both readings, including a live measurement that `_DECLARED_REGISTRY_COUNT`
  does not exist and only two of the five predicted exemption rows were actually dischargeable; §5
  all seven non-vacuity obligations with their planted-break/RED/restore evidence; §6 six residuals
  (including the still-open, still-unowned `ladder_state` finding from 134-03/134-06, named again
  rather than silently dropped); §7 the Evidence Ceiling restated verbatim from `133-RECORD.md` §6.
- Ticked **LEG-18** `Complete` in `REQUIREMENTS.md` — the only requirement this plan may mark.
  `grep -c '^- \[x\] \*\*LEG-'` returns **18**; the diff is confined to the LEG-18 row and its
  Traceability-table row; `RELOCK-*`/`CHAN-*`/`CLOSE-*` unchanged at 14 open rows.

## Task Commits

Each task was committed atomically, in the meta repo (`/workspaces`) on
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`:

1. **Task 1: gh#20 triage finding + owned backlog item** - `9c961ea` (docs)
2. **Task 2: CI-parity after-half** - `1f0d456` (docs)
3. **Task 3: `134-RECORD.md` + LEG-18 tick** - `dc4dd06` (docs)

**Plan metadata:** committed with this SUMMARY (docs: complete plan).

## Files Created/Modified

- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-GH20-TRIAGE.md` (new) —
  LEG-18's finding artifact.
- `.planning/todos/pending/at28c256-write-path-failure-gh20.md` (new) — the owned backlog item.
- `.planning/ROADMAP.md` — Backlog `999.29` row (scoped `Edit`, additive-only, single hunk).
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-CI-PARITY.md` — the
  `## After (post-edit)` section appended (additive-only; `## Before` byte-unchanged).
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-RECORD.md` (new) — the
  phase's closing record.
- `.planning/REQUIREMENTS.md` — LEG-18 ticked, its evidence clause, and its Traceability row.

## Decisions Made

- **Re-verified gh#20 read-only at execution time** rather than trusting the earlier research
  capture — confirmed byte-identical, so the triage's literals are independently re-confirmed.
- **The `ladder_state` finding (134-03/134-06's own carried-forward residual) is its own row in
  `134-RECORD.md` §6, not folded into the gh#20 backlog item** — the two are unrelated defects and
  this plan's Task 1 scope named only the AT28C256 write-path defect for backlog filing.
- **Measured live, not inherited, that only two of D-12's predicted "five Phase-134 exemption rows"
  were actually dischargeable** — confirmed via a direct diff of `test_op_registration_parity.py`
  between the Phase-133 close commit and the phase's final source; recorded in `134-RECORD.md` §4
  Correction 4 alongside the `_DECLARED_REGISTRY_COUNT` non-existence finding.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `134-GH20-TRIAGE.md`'s own prose tripped its Task 1 acceptance-criteria grep**
- **Found during:** Task 1, self-check against the plan's own acceptance criterion
  (`grep -rnE 'gh (issue (comment|close|edit)|...)' ...` must return nothing).
- **Issue:** The hand-off section's prose explicitly named the forbidden `gh issue comment`/
  `gh issue close`/`gh issue edit` commands (to say they were NOT run) — a plain-text grep cannot
  distinguish that prose from an actual invocation, the same self-catch class multiple earlier
  plans in this phase (134-06, 134-07, 134-08) hit for their own acceptance-criteria greps.
- **Fix:** Reworded the sentence to describe the same fact ("no write-shaped GitHub-CLI or
  git-publishing action... was run") without the literal forbidden substrings.
- **Files modified:** `134-GH20-TRIAGE.md`
- **Verification:** the acceptance-criteria grep now returns nothing (exit 1, no match).
- **Committed in:** `9c961ea` (Task 1's commit)

**2. [Rule 1 - Bug] The "no lock is ever emitted" phrase used a capitalized "No", missing the
lowercase acceptance-criteria grep**
- **Found during:** Task 1, self-check against the plan's own acceptance criterion.
- **Issue:** The sentence read "**No lock is ever emitted**" (capital N, for readability as a
  standalone bolded clause) — the acceptance criterion's grep target is the lowercase phrase.
- **Fix:** Reworded the surrounding sentence so the exact lowercase phrase "no lock is ever emitted"
  appears mid-sentence.
- **Files modified:** `134-GH20-TRIAGE.md`
- **Verification:** `grep -c "no lock is ever emitted" 134-GH20-TRIAGE.md` returns 1.
- **Committed in:** `9c961ea` (Task 1's commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1, self-caught during authoring before either reached
a committed state uncorrected — the same acceptance-criteria-self-catch pattern established by
134-06/134-07/134-08/134-10 in this same phase).
**Impact on plan:** Neither affects content or claims. No scope creep.

## Issues Encountered

None beyond the two self-caught deviations documented above.

## User Setup Required

None — no external service configuration required.

## Threat Flags

None new. This plan's `<threat_model>` (T-134-42/43/44/45/46) is fully covered by the implementation
as written: T-134-42 (claiming the lock was proven to inhibit a write) is mitigated by the Evidence
Ceiling restated verbatim in both `134-GH20-TRIAGE.md` and `134-RECORD.md`; T-134-43 (an unowned
acknowledgement) is mitigated by the `Owner: henols` line, filed in both the todo store and the
ROADMAP backlog; T-134-44 (a whole-file `Write` destroying unrelated ROADMAP entries) is mitigated by
the scoped `Edit`, confirmed single-hunk and additive-only via `git diff --stat`; T-134-45 (posting
before the claim gate is armed) is mitigated by zero privileged `gh`/`git` commands anywhere in this
plan's execution or its artifacts, confirmed by grep; T-134-46 (over-ticking requirements) is
mitigated by ticking LEG-18 only, with the 18-row tick count and the confined diff both verified.

## Next Phase Readiness

- Phase 134 is now fully closed: all 14 of its own LEG requirements (LEG-01, 02, 03, 04, 05, 06, 07,
  08, 12, 13, 14, 16, 17, 18) are `Complete`, plus the 4 already-`[x]` from Phase 133
  (LEG-09/10/11/15) — 18/18 LEG rows total across both phases.
- `134-RECORD.md` is the phase's closing artifact for Phase 137's ledger to read from; it names
  every residual with an owner or an explicit "no owner" statement, and the mypy watermark ratchet
  (still unowned, headroom 2 the entire phase) and the `ladder_state` finding (still unowned) are
  both carried forward explicitly rather than silently dropped.
- Per `STATE.md`, the next phase in this milestone's sequence is **Phase 136** (dev-tools channel
  gating, CHAN-*) — the 135 slot stays vacant (`write --sdp-relock` deferred to Backlog 999.28).
- No blockers. Both submodules (`firestarter_app`, `firestarter`) remain untouched by this plan
  beyond their own pre-existing, unrelated dirt (confirmed via `git status --porcelain`, identical
  to every prior plan's own note in this phase).

## Self-Check: PASSED

- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-GH20-TRIAGE.md` — FOUND,
  contains `3.0.0b14`, `Rev 2.3`, `00e121446ceb`, `11800`, `13700`, `4 of 4`, `6 of 10`, "no lock is
  ever emitted", and the Evidence Ceiling restatement.
- `.planning/todos/pending/at28c256-write-path-failure-gh20.md` — FOUND, contains `Owner: henols`.
- `.planning/ROADMAP.md` — FOUND, `grep -c '999\.'` is 92 (was 91 before this plan, +1).
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-CI-PARITY.md` — FOUND, contains
  both `## Before (pre-edit)` and `## After (post-edit)` headings; `mypy errors: 33 (watermark: 35)`
  and `checked 126 source files` both present.
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-RECORD.md` — FOUND, all seven
  mandatory sections present, all twenty D-01..D-20 decisions named.
- `.planning/REQUIREMENTS.md` — `grep -c '^- \[x\] \*\*LEG-'` returns 18; `git diff` confined to the
  LEG-18 row and its Traceability row.
- Commit `9c961ea` (meta) — FOUND in `git log --oneline --all`.
- Commit `1f0d456` (meta) — FOUND in `git log --oneline --all`.
- Commit `dc4dd06` (meta) — FOUND in `git log --oneline --all`.
- `git -C firestarter_app status --porcelain` / `git -C firestarter status --porcelain` — both show
  only pre-existing, unrelated dirt; no file this plan wrote lives inside either submodule.

---
*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Completed: 2026-08-04*
