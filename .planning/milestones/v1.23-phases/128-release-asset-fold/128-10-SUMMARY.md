---
phase: 128-release-asset-fold
plan: 10
subsystem: ci
tags: [github-actions, release-assets, beta-build, py32f071, rehearsal]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-01..128-09)
    provides: the AVR-assets checker, the composite ARM build action, the folded beta-build.yml with its rehearsal input, the cross-repo filename binding
provides:
  - "128-NONREGRESSION.md §3/§4a/§7/§8: the full CI-only evidence for two real rehearsal dispatches, a documented procedure defect, and a per-criterion discharge mapping"
  - "REL-01..REL-04 ticked in REQUIREMENTS.md, each with named backing evidence and any partially-backed half stated explicitly"
affects: [130-close-milestone]

# Tech tracking
tech-stack:
  added: []
  patterns: ["evidence-artifact discharge pattern: PENDING placeholders written before dispatch, replaced read-only after, never inferred"]

key-files:
  created: []
  modified:
    - .planning/phases/128-release-asset-fold/128-NONREGRESSION.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "REL-03 ticked as a combined-evidence requirement: the 'still publishes under a broken ARM build' half is CI-proven (run 30722537152); the 'assertion demonstrably fails on a missing AVR asset' half is proven only locally (§2.5/§2.6 exit-1 fixtures) — this seam is stated explicitly rather than implied as CI-proven"
  - "REL-04's cross-repo three-way binding is proven locally (10 passed) but restated as NOT enforced by app CI (F-8) — the mechanical in-CI filename/SHA assertions are CI-proven separately"
  - "Both rehearsal releases (draft ids 363647320, 363648361) are deleted; the run URLs and this transcript are declared the durable citation rather than implying the release pages remain inspectable"

requirements-completed: [REL-01, REL-02, REL-03, REL-04]

coverage:
  - id: D1
    description: "Record run A (healthy rehearsal) evidence in 128-NONREGRESSION.md §3, discharging REL-01 (ordering + carried version) and REL-02 (published asset)"
    requirement: "REL-01"
    verification:
      - kind: other
        ref: "CI run https://github.com/henols/firestarter/actions/runs/30722352902 (SHA 7a0a375) — step 19 PASS line + step-order read"
        status: pass
    human_judgment: false
  - id: D2
    description: "Record run A's asset list showing firestarter_py32f071.hex published as a real release asset, discharging REL-02"
    requirement: "REL-02"
    verification:
      - kind: other
        ref: "gh release view output, run 30722352902, asset firestarter_py32f071.hex 77284 bytes"
        status: pass
    human_judgment: false
  - id: D3
    description: "Record run B (planted ARM break) evidence showing the AVR-assets gate runs unconditionally and publishes exactly the three AVR assets under a contained ARM failure — CI half of REL-03"
    requirement: "REL-03"
    verification:
      - kind: other
        ref: "CI run https://github.com/henols/firestarter/actions/runs/30722537152 (SHA 6c1c31f) — step 21 unconditional success, 3-asset release, ::warning:: annotation"
        status: pass
    human_judgment: false
  - id: D4
    description: "Local proof that the AVR-assets checker script demonstrably fails (exit 1) on a missing or zero-byte AVR asset — the local half of REL-03, explicitly not CI-exercised this phase"
    requirement: "REL-03"
    verification:
      - kind: other
        ref: "128-NONREGRESSION.md §2.5/§2.6 (recorded in Task 1, this session)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Record run A's resolved SDK SHA and in-CI filename/SHA assertions, discharging the mechanical half of REL-04"
    requirement: "REL-04"
    verification:
      - kind: other
        ref: "CI run 30722352902 steps 17-18 (success); resolved SDK SHA 0ed2f4b4d3391eccfd4491006a30295fd78e32c2 == pinned GIT_TAG"
        status: pass
    human_judgment: false
  - id: D6
    description: "Document the plan's own procedure defect (§4 step 5 unusable — trips the Phase 123 CMake manifest-drift gate before ARM ever builds) and the substituted break actually used"
    verification:
      - kind: other
        ref: "128-NONREGRESSION.md §4a — local pre-dispatch verification (1 failed, 179 passed on the prescribed break; 180 passed unaffected on the substituted break)"
        status: pass
    human_judgment: false
  - id: D7
    description: "Tick REL-01..REL-04 in REQUIREMENTS.md to exactly the extent the evidence supports, each with named backing and any partial half stated"
    requirement: "REL-01, REL-02, REL-03, REL-04"
    verification:
      - kind: other
        ref: ".planning/REQUIREMENTS.md lines 85-88, 166"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 10: Rehearsal Evidence Recorded, REL-01..REL-04 Discharged Summary

**Recorded both rehearsal dispatches' CI-only evidence into `128-NONREGRESSION.md` §3/§7/§8 and ticked REL-01..REL-04 in REQUIREMENTS.md, each backed by a named run URL + commit SHA, with REL-03's un-CI-exercised half stated explicitly rather than implied.**

## Performance

- **Duration:** 20 min (documentary task only; both rehearsal dispatches were executed and cleaned up by the orchestrator under explicit operator authorisation before this task began)
- **Completed:** 2026-08-01
- **Tasks:** 1 (Task 3 of 128-10; Tasks 1 and 2 were already complete on entry)
- **Files modified:** 2

## Accomplishments
- Replaced every `PENDING — operator dispatch` cell in `128-NONREGRESSION.md` §3 with the operator-authorised rehearsal evidence: run A (`30722352902`, SHA `7a0a375`, healthy) and run B (`30722537152`, SHA `6c1c31f`, contained ARM break), each cited by run URL, commit SHA, and a legible log/API excerpt.
- Added a `## 7. Criterion discharge` section mapping each of the four ROADMAP success criteria to its named evidence row, explicitly splitting REL-03 into a CI-proven half (still publishes under a broken ARM build) and a local-only half (the assertion demonstrably fails on a missing AVR asset).
- Added a `## 8. Deviations recorded during Task 3` section documenting three findings: the plan's own §4 step-5 procedure defect (a CMake-source rename would trip the Phase 123 manifest-drift gate before the ARM build ever ran, disproving REL-03 rather than proving it), a false "confirmed by observation" claim found and fixed pre-dispatch in `beta-build.yml`, and the resulting firmware HEAD move to `7a0a375`.
- Ticked REL-01, REL-02, REL-03, REL-04 in `.planning/REQUIREMENTS.md`, each annotated with its specific backing evidence, and updated the phase's Traceability table row from `Pending` to `Complete`.

## Task Commits

Task 3 is the only outstanding task; Tasks 1 and 2 were completed in prior sessions/by the orchestrator.

1. **Task 3: Record evidence, discharge REL-01..REL-04** - see commit list below (docs commit)

**Plan metadata:** committed alongside Task 3 (single documentary commit, per `commit_docs` convention)

## Files Created/Modified
- `.planning/phases/128-release-asset-fold/128-NONREGRESSION.md` - §3 evidence rows populated, §4a procedure-defect subsection added, §7 criterion discharge added, §8 deviations added
- `.planning/REQUIREMENTS.md` - REL-01..REL-04 ticked with backing evidence; Traceability table row updated

## Decisions Made
- REL-03 ticked as a combined-evidence requirement rather than left partially unticked: the plan's own Task 3 instructions explicitly map Criterion 3 to both a CI row (run B) and a §2 local row (planted-fixture exit codes), so combining them is what the plan itself specified — not an executor overreach. The seam between the two halves is stated explicitly in both `128-NONREGRESSION.md` §7 and `REQUIREMENTS.md`'s REL-03 line so a future reader cannot mistake the local half for CI-proven.
- REL-04's cross-repo binding restated as local-only (F-8), consistent with the phase's standing ceiling — ticking REL-04 does not imply app CI enforces the binding.
- Both draft releases are gone; run URLs + this transcript are declared the durable citation, per the plan's own instruction not to imply future re-inspectability.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's §4 step 5 (Run B's break) does not do what it says**
- **Found during:** Task 3, verifying the evidence against the plan's own procedure text
- **Issue:** `128-NONREGRESSION.md` §4 step 5 (written in Task 1) prescribes renaming a source path in `platform/py32f071/CMakeLists.txt` to break CMake configure. This trips Phase 123's CMake manifest-drift gate (`tests/test_check_cmake_manifest.py::test_armed_and_passing_on_the_real_tree`) inside `pytest tests/` — `beta-build.yml` step 11, which has no `continue-on-error`. The whole job would fail before the ARM build step ever ran, publishing nothing — disproving REL-03 rather than proving it. This was caught and worked around before dispatch (a compile error in `platform/py32f071/src/timing.cpp` was substituted instead, verified ARM-only and non-interfering with any local test suite).
- **Fix:** Documented in `128-NONREGRESSION.md` §4a as a planning-procedure defect for Phase 130's honesty ledger; the substituted break is the one actually evidenced in §3.7-§3.9.
- **Files modified:** `.planning/phases/128-release-asset-fold/128-NONREGRESSION.md` (documentation only — no code changed by this task; the substitution itself happened before this task, on the now-deleted throwaway branch)
- **Verification:** §4a records the exact local pytest counts (`1 failed, 179 passed` for the prescribed break; `180 passed` unaffected for the substituted break)
- **Committed in:** this task's commit

**2. [Rule 1 - Bug] A false, unobserved claim in `beta-build.yml` was found and fixed pre-dispatch**
- **Found during:** pre-dispatch review (prior to this task; recorded here per the objective's instruction)
- **Issue:** `firestarter/.github/workflows/beta-build.yml:50` carried "Confirmed by observation on rehearsal run A (Plan 128-10)", shipped in commit `45d2bce` (Plan 128-05) — a commit that predates run A's existence, so the claim was unobserved when committed.
- **Fix:** Fixed on the milestone branch in firmware commit `7a0a375` ("docs(128-05): drop the unobserved 'confirmed by observation' claim"), replacing it with a pointer to the step-summary line the step actually emits every run. Documented in `128-NONREGRESSION.md` §8.
- **Files modified:** (firmware repo, out of scope for this task's commit; documented only)
- **Verification:** the underlying property is now genuinely observed on run A (§3.3-§3.5)
- **Committed in:** firmware commit `7a0a375` (not this plan's commit — firmware repo is read-only for this task)

**3. [Rule 1 - Bug, consequence of #2] Firmware HEAD moved**
- **Found during:** Task 3, reconciling the header block written at Task 1 against the actual dispatched commits
- **Issue:** `128-NONREGRESSION.md`'s header (written at Task 1) records firmware HEAD `0de57da3...`; the actual HEAD used for both rehearsal dispatches is `7a0a375...`, one commit later (the fix in deviation #2).
- **Fix:** Documented in `128-NONREGRESSION.md` §8 rather than silently rewriting the header's historical record.
- **Files modified:** `.planning/phases/128-release-asset-fold/128-NONREGRESSION.md`
- **Verification:** both run SHAs (`7a0a375` for run A, `6c1c31f` = `7a0a375` + planted break + auto-commit for run B) are internally consistent with this account
- **Committed in:** this task's commit

---

**Total deviations:** 3 (1 planning-procedure defect worked around pre-dispatch, 1 pre-existing false claim found and fixed pre-dispatch, 1 consequential HEAD-tracking correction) — all documentary in this task; no code was changed by Task 3 itself.
**Impact on plan:** None of the three affected requirement discharge. All three are flagged for Phase 130's CLOSE-02 honesty ledger as findings about the phase's own artifacts, not about the shipped feature.

## Issues Encountered
None beyond the three deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- REL-01..REL-04 are closed; Phase 128 (Release-Asset Fold) is now fully discharged at the requirement level.
- Phase 130's CLOSE-02 honesty ledger should pull `128-NONREGRESSION.md` §5 (non-claims), §6 (precedent), §4a and §8 (this task's three deviations) verbatim — all four sections are written for direct citation.
- REL-03's local-only half (assertion behavior on a missing AVR asset was never exercised in CI this phase) is a residual worth naming if Phase 130 or a future phase ever wants full CI-level proof of that half; not a blocker, just an honestly-stated gap.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*

## Self-Check: PASSED
- FOUND: .planning/phases/128-release-asset-fold/128-10-SUMMARY.md
- FOUND: commit 39e2d4b (this task's docs commit)
- FOUND: commit fa1324f (Task 1's earlier commit)
