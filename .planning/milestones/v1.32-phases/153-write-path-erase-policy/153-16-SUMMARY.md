---
phase: 153-write-path-erase-policy
plan: 16
subsystem: docs
tags: [honesty-record, gate-run, roadmap, project-md, erase-policy, merge-05, gate-03]

# Dependency graph
requires:
  - phase: 153-write-path-erase-policy (plans 01-15)
    provides: "all eight code/test-proven ERASE requirements (ERASE-01..08) and the D-153-01..05
      decision record this plan's own record summarises"
  - phase: 152-outward-facing-close-operator-gated
    provides: "D-15 — the record-correction instructions this plan discharges (PROJECT.md/ROADMAP
      firmware-workstream count, deferred to Phase 153 because 153 must touch database.py:617
      anyway)"
provides:
  - "PROJECT.md corrected to three firmware-touching workstreams (149, 151, 153), a new
    workstream-7 table row, and workstream 4's description noting the write-path half is closed"
  - "ROADMAP.md's v1.32 milestone-index bullet corrected to match the already-amended v1.32
    header (three workstreams, phase range through 153)"
  - "153-RECORD.md — the phase's own honesty record: per-requirement outcomes, proof oracles, an
    explicit what-was-NOT-proven section carrying the verbatim honesty phrase, the D-153-01..05
    decision table, the two size figures kept separate, four mechanism corrections, and a
    transcribed full phase-gate run from a committed tree across both sub-repositories"
  - "ERASE-09 flipped to Complete — all nine ERASE requirements now Complete"
  - "ROADMAP.md's v1.32 coverage table (nine ERASE rows) and phase-153 checkbox flipped to
    reflect the closed phase"
affects: [152-outward-facing-close-operator-gated]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Scoped hand-edits to PROJECT.md/ROADMAP.md with an inspected diff, never a whole-file
      rewrite through the requirements/roadmap helper verbs"
    - "Phase outcome record as a load-bearing, not narrative, artifact — proof-oracle-per-claim
      plus an equally weighted what-was-NOT-proven section, ahead of an outward-facing phase that
      drafts from it"

key-files:
  created:
    - .planning/phases/153-write-path-erase-policy/153-RECORD.md
  modified:
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Four mechanism corrections identified and recorded, found by cross-checking the phase's own
    documents against each other and against the working tree: the flash_5v_page.cpp conditional
    is at 88-90 (RESEARCH right, PATTERNS' 87-89 'correction' was itself wrong); the database.py
    ERASE-03 edit site is :620 not :621 (ROADMAP/REQUIREMENTS were off by one); ERASE-06 needed no
    ic_layout.py edit under the 'must not contradict' reading; ERASE-07's comment is the fourth
    recorded reversal in its 119->120->121->153 chain"
  - "Ran the full python-3.11 mypy watermark check through a throwaway uv venv in the session
    scratchpad (devcontainer default is 3.12, which fails this gate on an unrelated numpy-stub
    issue) rather than trusting the devcontainer interpreter's result"
  - "Left the meta repo's pre-existing, unrelated modifications (.planning/config.json's
    _auto_chain_active flag, the firestarter submodule gitlink pointer drift from plan 15,
    devtest-rootcause skill files, package-lock.json/package.json) untouched -- out of this
    plan's files_modified scope and not caused by this plan's work"

requirements-completed: [ERASE-09]

coverage:
  - id: D1
    description: "PROJECT.md's milestone subtitle and workstream table corrected to three
      firmware-touching workstreams (149, 151, 153), with a new row 7 and an updated workstream 4
      description"
    requirement: "ERASE-09"
    verification:
      - kind: other
        ref: "grep -n 'firmware-touching workstream' .planning/PROJECT.md; grep -n '^| 7 |' .planning/PROJECT.md; git diff --numstat -- .planning/PROJECT.md (9 insertions, 4 deletions, 3 hunks)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ROADMAP.md's v1.32 milestone-index bullet corrected to match the already-amended
      v1.32 header (three workstreams, phase range 147-153); deliberate non-numeric phase-checkbox
      order left intact"
    requirement: "ERASE-09"
    verification:
      - kind: other
        ref: "grep -c 'Phases 147–152' .planning/ROADMAP.md == 0; grep -n -A2 'CHECKLIST ORDER IS DELIBERATELY NON-NUMERIC' .planning/ROADMAP.md confirms phase 153 still listed before 152"
        status: pass
    human_judgment: false
  - id: D3
    description: "153-RECORD.md written: verbatim honesty phrase, all nine ERASE ids with
      delivering-plan citations, all five D-153 ids, both size figures with Caterina labelled
      UNGUARDED, and a what-was-NOT-proven section"
    requirement: "ERASE-09"
    verification:
      - kind: other
        ref: "grep -c 'software-proven and unvalidated on silicon' 153-RECORD.md == 3; grep -cE 'ERASE-0[1-9]' == 28; grep -cE 'D-153-0[1-5]' == 11; grep -c UNGUARDED == 1; grep -ciE 'proven on silicon|validated on hardware|graduat' == 3, all three inside explicit negations"
        status: pass
    human_judgment: false
  - id: D4
    description: "Full phase gate run and transcribed from a committed tree: both ERASE-09 gates,
      host suite (1825 passed, 83.61% coverage), lint/format/mypy watermark (35==35 via python
      3.11), GATE-03/SDP-window/cross-repo parity, sibling-absent skip check, both native
      environments (170/17), three cold AVR builds, both check_size_baseline.py modes,
      build-warnings, erase-body checker, checker-convention, firestarter's own 322-test pytest
      suite (including the whole-repo porcelain assertions)"
    requirement: "ERASE-09"
    verification:
      - kind: integration
        ref: "transcribed verbatim in 153-RECORD.md's 'Full Phase Gate' section"
        status: pass
    human_judgment: false
  - id: D5
    description: "ERASE-09 flipped to Complete in REQUIREMENTS.md with evidence quoted inline; all
      nine ERASE requirements and the ROADMAP v1.32 coverage table's nine ERASE rows now read
      Complete; Phase 153 and its last plan checked off in the ROADMAP phase list"
    requirement: "ERASE-09"
    verification:
      - kind: other
        ref: "grep -n 'ERASE-09' .planning/REQUIREMENTS.md shows [x]; grep -c '| Phase 153 | Pending |' .planning/ROADMAP.md == 0"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 16: Honesty Record, Full Phase Gate & D-15 Record Corrections Summary

**Corrected the two stale "one/two firmware-touching workstream" claims in PROJECT.md and ROADMAP.md to three (149, 151, 153), wrote `153-RECORD.md` as the phase's own honesty record carrying the verbatim "software-proven and unvalidated on silicon" phrase and an equally-weighted what-was-NOT-proven section, ran the full phase gate from a committed tree across both sub-repositories, and flipped ERASE-09 — closing all nine ERASE requirements.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-21T11:22Z (approx)
- **Completed:** 2026-08-21T11:43Z
- **Tasks:** 3/3 completed
- **Files modified:** 4 (1 new, 3 modified)

## Accomplishments

- Corrected `PROJECT.md`'s current-milestone subtitle from "one firmware-touching workstream"
  (naming only the page-size seam) to three, naming Phase 149, Phase 151 and Phase 153, with an
  amendment-provenance note; added workstream-7 to the target-workstreams table (write-path erase
  policy, firmware+host, no bench); extended workstream 4's description to note the write-path
  half of the AT28C book is now closed by workstream 7 while the relock half stays deferred.
  Inspected the diff before committing: three scoped hunks, no reflow, field-count uniform across
  the workstream table's data rows.
- Corrected `ROADMAP.md`'s v1.32 milestone-index bullet (phase range 147–152 → 147–153, two
  workstreams → three, naming all three phases) to match the wording the v1.32 header further
  down the file already carried. Left the deliberate non-numeric phase-checkbox order (153 before
  152, per `D-08`) untouched and confirmed intact after the edit.
- Wrote `153-RECORD.md`: a per-requirement "what shipped" section (nine paragraphs, each citing
  its delivering plan), a "what was proven, and how" section naming the specific oracle for each
  central claim, a "what was NOT proven" section stating plainly that `0x0D` stays `UNVERIFIED`,
  no `support_status` moved, gh#21/#32/#11/#12 stay OPEN, and carrying forward the two honest
  limitations RESEARCH logged (the AN 0544B cycle-time figure is an Atmel-family maximum; no
  native test can prove the wall-clock wait), the `D-153-01..05` decision table, the two size
  figures (0 B MERGE-05 leonardo headroom vs. 1042 B UNGUARDED Caterina headroom) kept explicitly
  separate, four mechanism corrections found across the phase's own records, and a "what Phase 152
  must not repeat" list.
- Ran the full phase gate from this plan's own committed tree (after committing Tasks 1 and 2)
  across both sub-repositories and transcribed every command and result into `153-RECORD.md`:
  both ERASE-09 machine gates (exit 0, `chip_database.json` byte-unchanged); the host suite (1825
  passed, 83.61% coverage against a 70% floor); `ruff check`/`ruff format --check` (clean); the
  mypy watermark (35==35, run through a throwaway `uv venv --python 3.11` since the devcontainer's
  default 3.12 fails this gate on an unrelated issue); `check_dispatch.py` (exit 0, byte-unchanged)
  and its invariant suite (12 passed); the SDP-window checker; cross-repo parity (19 passed); the
  cross-repo gates confirmed to SKIP cleanly (not error) with `FIRESTARTER_FW_ROOT` pointed at a
  nonexistent path (1 passed, 6 skipped, each with a named reason); both native environments
  (170 cases/17 suites, agreeing); three cold AVR builds (byte-identical to the committed
  baseline: uno 25548/1575, uno328pb 25598/1581, leonardo 27630/2016); both
  `check_size_baseline.py` gate modes (default and `--policy merge05` with BASE-01 named
  explicitly, all green); the build-warnings checker; the erase-body checker
  (`check_erase_no_vpp.py`); and firestarter's own 322-test pytest suite, which includes the
  whole-repo porcelain assertions (`test_flash_path_record_sync.py`) and both passed.
- Confirmed both sub-repositories end the gate run clean of tracked modifications: `firestarter`
  shows zero changes of any kind; `firestarter_app` shows zero tracked modifications (its six
  untracked files predate this plan, per plans 14/15's own record, and were not touched).
- Flipped `ERASE-09` to Complete in `REQUIREMENTS.md` with the evidence quoted inline against each
  of its four clauses, and updated `ROADMAP.md`'s v1.32 coverage table (all nine ERASE rows now
  Complete) and phase-checklist (Phase 153 and its final plan both checked off).

## Task Commits

1. **Task 1: Correct PROJECT.md's firmware-workstream count and add a workstream row for 153 (D-15)** - `893c3e65` (docs)
2. **Task 2: Correct the ROADMAP milestone-index line (D-15)** - `69210c81` (docs)
3. **Task 3: Write the phase record (ERASE-09), run the full phase gate, flip ERASE-09** - `9c3e2541` (docs)

**Plan metadata:** (final commit hash recorded after this summary is committed)

## Files Created/Modified

- `.planning/PROJECT.md` - milestone subtitle corrected to three firmware-touching workstreams; new workstream-7 row; workstream 4 description extended
- `.planning/ROADMAP.md` - v1.32 milestone-index bullet corrected; v1.32 coverage table's nine ERASE rows flipped to Complete; Phase 153 and its last plan checked off
- `.planning/REQUIREMENTS.md` - ERASE-09 flipped to Complete with inline evidence
- `.planning/phases/153-write-path-erase-policy/153-RECORD.md` - new: the phase's own outcome record

## Decisions Made

- **Four mechanism corrections, found by cross-checking the phase's own records against the
  working tree rather than trusting any single document:** (1) `flash_5v_page.cpp`'s blank-check
  conditional is at `:88-90` — `153-RESEARCH.md` was right, `153-PATTERNS.md`'s "correction" to
  `:87-89` was itself wrong (plan 06's finding); (2) the `database.py` ERASE-03 edit site is
  `:620`, not `:621` as both `ROADMAP.md` and `REQUIREMENTS.md` state — line 621 is the
  `simple_flags |=` body, not the exclusion tuple itself (RESEARCH caught this before any code
  was written, plan 07 confirmed it); (3) ERASE-06's adopted reading ("the two axes must not
  contradict", not "`info` must derive from the wire bit") meant `ic_layout.py`'s `can_erase_str`
  block needed zero edits, confirmed at its PATTERNS-corrected location `:578-586`; (4) ERASE-07's
  `database.py:585-616` comment correction is the fourth recorded reversal in a chain running
  Phase 119 → 120 → 121 → 153.
- **Ran the mypy watermark gate through a throwaway `uv venv --python 3.11`** rather than the
  devcontainer's default Python 3.12 interpreter, which fails this specific gate on an unrelated
  numpy-stub syntax error — a known, pre-existing environment gap, not a regression from this
  plan's work. No repository file was changed to work around it.
- **Left the meta repo's pre-existing, unrelated modifications untouched**: `.planning/config.json`'s
  `_auto_chain_active` flag, the `firestarter` submodule gitlink pointer drift (new commits landed
  in the submodule by plan 15, not yet reflected as a gitlink bump in meta — out of this plan's
  scope), the `devtest-rootcause` skill directory, and `package-lock.json`/`package.json`. None
  of these are caused by or relevant to this plan's `files_modified` scope.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' acceptance criteria were met on the
first pass: the PROJECT.md and ROADMAP.md diffs were each confined to the intended scoped hunks
(verified via `git diff --numstat` and manual inspection before committing), and every gate
command in Task 3's verification block ran clean.

## Issues Encountered

- The devcontainer's default Python (3.12) fails `check_mypy_watermark.py` with a pre-existing,
  unrelated numpy-stub syntax error (`Type statement is only supported in Python 3.12 and
  greater` — ironically inverted, the numpy stub itself requires 3.12+ syntax that mypy's own
  bundled typeshed rejects under strict settings). Worked around, per the standing project
  convention already on record from plan 15, by running the gate through a throwaway
  `uv venv --python 3.11` in the session scratchpad. No repository file was changed.
- A background-run of the full host pytest suite produced an empty output file on first attempt
  (likely a background-task output-capture artifact in this environment); re-ran in the
  foreground with an extended tool timeout and captured the full, correct result (1825 passed,
  83.61% coverage). Not a plan deviation — no repository state was affected by the first attempt.

Neither issue blocked completion of any task or its verification.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 153 (Write-Path Erase Policy) is now closed: all sixteen plans complete, all nine ERASE
  requirements Complete, both stale in-repo firmware-workstream-count claims corrected, and the
  phase's own honesty record written and gate-verified from a committed tree.
- Phase 152 (Outward-Facing Close) can now proceed per `D-08` — its `Depends on` names Phase 153,
  and `153-RECORD.md`'s "What Phase 152 must not repeat" section is the direct input to that
  phase's claim-gate authoring. The ROADMAP's deliberate non-numeric checkbox order (153 checked,
  152 still the first unchecked box) resolves correctly to Phase 152 as next.
- `0x0D` stays `UNVERIFIED`; no `support_status` changed; gh#21/#32/#11/#12 remain OPEN; no AT28C
  part was used or required at any point in this phase.
- Both sub-repositories (`firestarter`, `firestarter_app`) are left clean of tracked modifications.
  `firestarter_app`'s pre-existing untracked files (`SECURITY.md`, `datasheets/*.pdf`,
  `write_test_port.sh`, `.planning/config.json`) predate this phase and remain untouched.

## Known Stubs

None.

## Threat Flags

None — this plan only corrects in-repo prose records, writes a phase outcome record, and runs
existing verification gates; no new network endpoint, auth path, file access pattern, or schema
change at a trust boundary was introduced.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `.planning/phases/153-write-path-erase-policy/153-16-SUMMARY.md`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-RECORD.md`
- FOUND: commit `893c3e65` (Task 1)
- FOUND: commit `69210c81` (Task 2)
- FOUND: commit `9c3e2541` (Task 3)
