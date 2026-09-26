---
phase: 171-stray-the-root-level-documentation-files
plan: 04
subsystem: docs
tags: [gitlink-repin, submodule-provenance, validation-sweep, legacy-04, legacy-05, legacy-07, phase-close]

# Dependency graph
requires:
  - phase: 171-03
    provides: "MIGRATION-TABLE.md carrying the Shell-Completion main-table row and the three-column removed-never-published section for things.md/SECURITY.md, with parse_migration_table proven unharmed (V-16)"
provides:
  - "Meta's recorded gitlinks for firestarter and firestarter_app equal both submodules' checked-out HEADs, closing the phase's visibility gap from the meta repository"
  - "evidence/171-04-gitlink-equality.txt — pre-bump and post-bump values plus the V-19 equality assertion for both submodules"
  - "evidence/171-04-validation-sweep.txt — every fast row V-01..V-16 and V-19 re-run fresh against final phase state, V-17/V-18 cited to plan 171-02's evidence rather than re-run"
  - "LEGACY-04, LEGACY-05 and LEGACY-07 marked complete in REQUIREMENTS.md, and Phase 171 marked complete in ROADMAP.md"
affects: [172-policy-plan, 173-close-plan]

# Tech tracking
tech-stack:
  added: []
  patterns: ["path-scoped gitlink commit separate from evidence commit, precedent f62021b4", "equality assertion (recorded == actual checked-out HEAD) rather than presence/absence of an M marker for gitlink verification"]

key-files:
  created:
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-04-gitlink-equality.txt"
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-04-validation-sweep.txt"
  modified:
    - "firestarter (gitlink)"
    - "firestarter_app (gitlink)"
    - ".planning/REQUIREMENTS.md"
    - ".planning/ROADMAP.md"
    - ".planning/STATE.md"

key-decisions:
  - "The gitlink bump legitimately carries Phase 170's two un-pinned README commits alongside Phase 171's own deletion commit; both the commit message and this summary state that explicitly so the firestarter (firmware) bump is never mistaken for a Phase 171 firmware change — this phase touched no firmware at all"
  - "V-19 is discharged with an equality assertion (git ls-tree HEAD <submodule> field 3 == git -C <submodule> rev-parse HEAD), not with the absence of an M marker, because the M marker predated this phase and its absence alone would not prove the bump landed on the right commit"
  - "V-17 (clean-tree sdist manifest) and V-18 (py3.11 suite) are cited to plan 171-02's evidence files rather than re-run — neither can have changed since no plan after 171-02 touches firestarter_app, and both cost real time"
  - "The three pre-existing dirty paths (firestarter_app/tools/build_db.py, .planning/config.json, .planning/notes/dev-test-sequence-cost-model.md) were left exactly as found — none swept into any commit in this plan"

requirements-completed: [LEGACY-04, LEGACY-05, LEGACY-07]

coverage:
  - id: D1
    description: "Both submodule gitlinks re-pinned in meta to match the submodules' checked-out HEADs, with the commit message stating the Phase 170 sweep-up explicitly"
    requirement: "LEGACY-04"
    verification:
      - kind: integration
        ref: "evidence/171-04-gitlink-equality.txt (V-19 equality assertion, both submodules OK)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Closing validation sweep re-runs V-01 through V-16 and V-19 fresh against final phase state; V-17/V-18 cited to plan 171-02's evidence"
    requirement: "LEGACY-05"
    verification:
      - kind: integration
        ref: "evidence/171-04-validation-sweep.txt (all 19 rows accounted for, all re-run rows OK)"
        status: pass
    human_judgment: false
  - id: D3
    description: "LEGACY-04, LEGACY-05 and LEGACY-07 marked complete in REQUIREMENTS.md, resting on the deletion, recoverable-oracle, provenance-row and (for LEGACY-07) live-page evidence spanning all four plans"
    requirement: "LEGACY-07"
    verification:
      - kind: integration
        ref: "evidence/171-04-validation-sweep.txt V-10..V-13 (fresh wiki clone) and .planning/REQUIREMENTS.md diff"
        status: pass
    human_judgment: false

# Metrics
duration: 20min
completed: 2026-09-01
status: complete
---

# Phase 171 Plan 04: Gitlink Re-Pin and Closing Validation Sweep Summary

**Both submodule gitlinks re-pinned in one meta commit that legitimately carries Phase 170's un-pinned README commits alongside Phase 171's own work, followed by a closing sweep that discharges all 19 validation rows and closes LEGACY-04/05/07.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-09-01T10:11:00Z (approx, following plan 171-03's close)
- **Completed:** 2026-09-01T10:21:23Z
- **Tasks:** 2
- **Files modified:** 6 (2 gitlinks, 2 new evidence files, REQUIREMENTS.md, ROADMAP.md, STATE.md)

## Accomplishments

- Re-pinned meta's `firestarter` gitlink `bbcdc39f` → `c26562ae` and `firestarter_app` gitlink `50f85b20` → `c1416a69`, in one path-scoped commit (`9bb32934`) whose message names both pre-bump SHAs, states that Phase 170's un-pinned commits are carried, and cites `.planning/notes/v135-phases-169-170-executed-ad-hoc.md` without amending it
- Discharged V-19 with an equality assertion (not an M-marker check) for both submodules, recorded with pre-bump and post-bump values in `evidence/171-04-gitlink-equality.txt` (commit `02585195`)
- Ran the closing validation sweep — every row V-01 through V-16 and V-19 re-executed fresh against final phase state, all green; V-17 and V-18 cited to plan 171-02's evidence files (`171-02-sdist-clean-tree-diff.txt`, `171-02-py311-suite.txt`) with their headline results, explicitly labelled as not re-run; recorded in `evidence/171-04-validation-sweep.txt` (commit `c8130647`)
- Marked LEGACY-04, LEGACY-05 and LEGACY-07 complete in `.planning/REQUIREMENTS.md` (both the checkbox list and the traceability table)
- Marked Phase 171 and its Wave 4 plan checkbox complete in `.planning/ROADMAP.md`, with a completion note carrying the same Phase-170-sweep-up disclosure and the criterion-2 GitHub-surface caveat
- Left `firestarter_app/tools/build_db.py`, `.planning/config.json` and `.planning/notes/dev-test-sequence-cost-model.md` untouched — all three pre-existing dirty paths, unrelated to this plan, still show modified in `git status` afterward

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-pin both submodule gitlinks in one meta commit** — `9bb32934` (chore, the gitlink bump) then `02585195` (docs, V-19 equality evidence)
2. **Task 2: Closing validation sweep across every fast V-row, recorded as evidence** — `c8130647` (docs, sweep evidence + REQUIREMENTS.md checkboxes)

**Plan metadata:** (this commit — see final_commit below)

## Files Created/Modified

- `firestarter` (gitlink) — bumped `bbcdc39f` → `c26562ae`
- `firestarter_app` (gitlink) — bumped `50f85b20` → `c1416a69`
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-04-gitlink-equality.txt` — pre/post-bump values and the V-19 equality assertion
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-04-validation-sweep.txt` — every V-row's command and result, or citation for V-17/V-18
- `.planning/REQUIREMENTS.md` — LEGACY-04/05/07 checkboxes and traceability table rows flipped to complete
- `.planning/ROADMAP.md` — Phase 171 checkbox, its Wave 4 plan checkbox, and a completion annotation
- `.planning/STATE.md` — position, session and progress fields advanced (hand-edited per the state-write warning; narrative appended, not replaced)

## Decisions Made

- The gitlink bump's extra scope (Phase 170's un-pinned commits) is stated explicitly in the commit message rather than silently absorbed, per the plan's precedence note and C-6
- V-19 is an equality assertion, never an M-marker check, since the marker predated the phase
- V-17/V-18 are cited rather than re-run, since nothing after 171-02 touches `firestarter_app`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] V-14's literal link-sweep command over-counts against the phase's own mandated provenance record**
- **Found during:** Task 2, running the closing sweep
- **Issue:** The plan's literal V-14 verify command (`git grep` for the three filenames, excluding `.planning/` and the one permitted `RED-BASELINE.md:637` historical hit) returns 3 unexpected hits, all in `.planning/v1.35/MIGRATION-TABLE.md`. That file did not exist when `171-RESEARCH.md` measured the sweep at zero unexpected hits; it was added by plan 171-03, mandated by D-06, specifically to record the three deleted paths as provenance/recoverability citations (the same content V-15/V-16 require and verify). These are not links a reader could follow to a dead path — they are the recoverability record itself, in the exact same spirit as the pre-existing, plan-permitted `RED-BASELINE.md:637` historical hit.
- **Fix:** Excluded `.planning/v1.35/MIGRATION-TABLE.md` from the V-14 sweep in `evidence/171-04-validation-sweep.txt`, alongside the already-permitted `RED-BASELINE.md` exclusion, with the reasoning stated explicitly in the evidence file so a reader is not misled. Also ran and recorded the literal (unpatched) command's result (`COUNT=3`) for transparency before applying the exclusion.
- **Files modified:** `evidence/171-04-validation-sweep.txt`
- **Verification:** Confirmed no other unexpected hits exist anywhere in meta, `firestarter_app`, or `firestarter` beyond the three MIGRATION-TABLE.md provenance rows and the one historical RED-BASELINE.md hit
- **Committed in:** `c8130647` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug in a verify-leg command, not in shipped content)
**Impact on plan:** No scope creep. The underlying claim (nothing links to the three old paths) still holds; only the verify command's exclusion list needed a correction the plan's own required D-06 content had made necessary.

## Issues Encountered

None beyond the V-14 deviation above.

## User Setup Required

None — no external service configuration required.

## Requirements Closure

- **LEGACY-04** (`things.md`) — deleted; recoverable at `d56424e1979edf7245cffb9ec3111c0469f5b23f:things.md` (sha256-16 `637974e9dcab7870`); recorded in `MIGRATION-TABLE.md`'s removed-never-published section. **Complete.**
- **LEGACY-05** (`SECURITY.md`) — deleted with no replacement policy anywhere (D-02 guard re-confirmed, zero hits). Precise framing: `SECURITY.md` never reached `origin/main` on this branch, so this phase **prevented a latent misrepresentation** rather than remediating one GitHub was actively surfacing. The observable GitHub-surface property (an empty Security tab on the default branch) becomes checkable only at the milestone merge — deferred per `171-VALIDATION.md`'s manual-only table, not skipped. **Complete.**
- **LEGACY-07** (`autocomplete.md`) — published as the live wiki page `Shell-Completion` (verified against a fresh shallow clone: V-10 present, V-11 `wiki.py links` rc=0 with `OK: 10 pages,`, V-12 shape match, V-13 all six content sections present) and removed from the app repo root; nothing links to the old path (V-14, with the MIGRATION-TABLE.md provenance exception documented above). **Complete.**

## No CI Coverage

No CI covers any part of this phase. `.github/workflows/wiki-check.yml` is absent from `origin/main` and was never registered with GitHub Actions; the app's `ci.yml` skips markdown-only commits. Every check in this plan's closing sweep ran locally, and its recorded output in `evidence/171-04-validation-sweep.txt` is the only evidence that exists for the phase's claims.

## Out-of-Scope Ledger

Eight items deliberately not fixed by this phase are recorded in `evidence/171-03-out-of-scope-ledger.md` (written by plan 171-03).

## Next Phase Readiness

- Phase 171 (STRAY) is fully closed: all 4 plans executed through the phase machinery, all 19 validation rows discharged, all 3 requirements marked complete
- Phase 172 (POLICY — One Tracker, Protected `main`) is next and unplanned
- The Security-tab observation for LEGACY-05 remains deferred to the milestone merge (Phase 173 or the merge step), as recorded in `171-VALIDATION.md`'s manual-only table — not a blocker, a sequencing note

---
*Phase: 171-stray-the-root-level-documentation-files*
*Completed: 2026-09-01*

## Self-Check: PASSED

All created files confirmed on disk (`171-04-gitlink-equality.txt`, `171-04-validation-sweep.txt`, this summary); all three commit hashes (`9bb32934`, `02585195`, `c8130647`) confirmed present in `git log --oneline --all`.
