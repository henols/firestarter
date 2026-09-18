---
phase: 197-the-override-mechanism-and-the-program-pulse
plan: 01
subsystem: database-generator
tags: [python, build_db, chip_database, pinout, git-submodule]

# Dependency graph
requires: []
provides:
  - "firestarter_app submodule moved off beta onto v1.40-program-parameter-fidelity"
  - "Three datasheet PDFs (MBM27C1000.pdf, MBM27128.pdf, MBM27C4001.pdf) git-tracked so OVR-03 citations resolve in a fresh checkout"
  - "_PGM_ON_PIN31_MAX_SIZE derived away from resolve_pinout_key's proto_id=0x08 fork, proven byte-identical"
  - "tests/test_build_db_pinout_fork.py pinning the derived boundary against all eleven real size_bytes values and the 262144/262145 pair"
affects: [197-02, 197-03, 197-04, 197-05]

# Actuals (#2632) — pairs with the plan's `estimate` to calibrate future estimates.
# Multi-repo plan: gsd_run query commit is disabled for this project (it has twice
# self-created a stray gsd/v1.40-... branch), so commits below are measured by hand
# per repo rather than via the SDK ledger.
actuals:
  tokens: 1100
  tasks: 3
  commits: 3
  commits_by_repo:
    firestarter_app: 2
    meta: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Derived-boundary pinout fork: a named size constant replaced with (mem_size - 1).bit_length() <= 18, proven equivalent by exhaustive integer check plus byte-identical regeneration, rather than trusted algebraically"

key-files:
  created:
    - firestarter_app/datasheets/MBM27C1000.pdf
    - firestarter_app/tests/test_build_db_pinout_fork.py
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/datasheets/MBM27128.pdf (newly tracked, pre-existing on disk)
    - firestarter_app/datasheets/MBM27C4001.pdf (newly tracked, pre-existing on disk)

key-decisions:
  - "Task 2 checkpoint (checkpoint:decision, gate=blocking-human): operator selected option id `derive-plus-test` on 2026-09-18 — derive the 262144 threshold away AND commit a permanent boundary test, rather than `derive` alone or `keep` the named constant under OVR-06."
  - "The comment block at build_db.py:144-146 (DIP28_VARIANT_MAP / PIN_MAP_TO_PINOUT / PIN_MAP_PROTO_TO_PINOUT) does not reference _PGM_ON_PIN31_MAX_SIZE, so no sentence needed deletion after removing the constant — only the constant's own line and its trailing blank line were removed."

patterns-established:
  - "A one-way-reversibility fork substitution is proven by two independent methods before it is trusted: an exhaustive integer identity check over the full practical domain, and a byte-identical full-pipeline regeneration against the committed generated artifact."

requirements-completed: []
# OVR-03 and OVR-06 are NOT marked complete here. This plan only makes the OVR-03
# datasheet citations resolvable (a prerequisite) and removes one of several
# part-specific constants OVR-06 requires an accounting of; the override file
# itself (OVR-03's real subject) and the remaining OVR-05/OVR-06 hardcode
# dispositions (D-06/D-07/D-08) land in later plans in this phase (197-03..197-05).
# REQUIREMENTS.md is left untouched per this task's explicit success criteria.

coverage:
  - id: D1
    description: "firestarter_app submodule moved off beta onto v1.40-program-parameter-fidelity; datasheets/MBM27C1000.pdf vendored from the gh#70 attachment and datasheets/MBM27128.pdf + datasheets/MBM27C4001.pdf newly git-tracked, so every OVR-03 citation to these three paths resolves in a fresh checkout"
    verification:
      - kind: other
        ref: "git -C firestarter_app rev-parse --abbrev-ref HEAD == v1.40-program-parameter-fidelity"
        status: pass
      - kind: other
        ref: "git -C firestarter_app ls-files -- datasheets/MBM27C1000.pdf datasheets/MBM27128.pdf datasheets/MBM27C4001.pdf | wc -l == 3"
        status: pass
      - kind: other
        ref: "head -c 4 firestarter_app/datasheets/MBM27C1000.pdf == %PDF"
        status: pass
    human_judgment: false
  - id: D2
    description: "Task 2 decision gate resolved: operator ruled derive-plus-test for D-09's one-way-reversibility fork substitution"
    verification: []
    human_judgment: true
    rationale: "Recording an operator's decision is not a code artifact a test can verify; the decision itself is documented verbatim above and in this file's frontmatter."
  - id: D3
    description: "_PGM_ON_PIN31_MAX_SIZE deleted from tools/build_db.py; resolve_pinout_key's proto_id=0x08 fork now derives the same threshold via (mem_size - 1).bit_length() <= 18; full regeneration against the pinned infoic.xml is byte-identical to the committed chip_database.json"
    requirement: OVR-06
    verification:
      - kind: other
        ref: "cd firestarter_app && python tools/build_db.py && git diff --quiet -- firestarter/data/chip_database.json (exit 0)"
        status: pass
      - kind: other
        ref: "python -c \"assert all(((s-1).bit_length()<=18)==(s<=262144) for s in range(0,2100000))\""
        status: pass
      - kind: unit
        ref: "tests/test_build_db_pinout_fork.py::TestDerivedSizeBoundaryFork (13 cases)"
        status: pass
    human_judgment: false
  - id: D4
    description: "New boundary test module tests/test_build_db_pinout_fork.py pins all eleven real electrical.size_bytes values from the shipped database (512..1048576) plus the 262144/262145 boundary pair against the derived fork"
    verification:
      - kind: unit
        ref: "tests/test_build_db_pinout_fork.py (13 passed)"
        status: pass
    human_judgment: false

duration: ~20min (continuation from Task 2 checkpoint)
completed: 2026-09-18
status: complete
---

# Phase 197 Plan 01: Groundwork and the derived pin-31 threshold Summary

**Moved `firestarter_app` off `beta`, vendored/tracked the three datasheets OVR-03 needs, and derived away `_PGM_ON_PIN31_MAX_SIZE` with a byte-identical regeneration plus a permanent boundary test.**

## Performance

- **Duration:** ~20 min for this continuation (Task 2 checkpoint resume through plan completion); Task 1 was completed in a prior session
- **Started:** 2026-09-18 (continuation)
- **Completed:** 2026-09-18T12:18:29Z
- **Tasks:** 3 (1 auto, 1 checkpoint:decision, 1 auto/tdd)
- **Files modified:** 5 (3 datasheet PDFs, 1 modified generator file, 1 new test module) plus 1 gitlink

## Accomplishments
- `firestarter_app` submodule is on `v1.40-program-parameter-fidelity`, not `beta` — no further commit in this phase risks an accidental PyPI publish
- `datasheets/MBM27C1000.pdf` (the actual gh#70 attachment), `datasheets/MBM27128.pdf`, and `datasheets/MBM27C4001.pdf` are all git-tracked; every OVR-03 citation later plans write against these three paths resolves in a fresh clone
- `_PGM_ON_PIN31_MAX_SIZE` is gone from `tools/build_db.py`; the `DIP32_27C020`/`DIP32_STD` fork at the `proto_id == 0x08` arm now derives the same 262144-byte threshold from `(mem_size - 1).bit_length() <= 18`
- The derivation is proven two ways: an exhaustive integer identity check over `[0, 2100000)` with zero mismatches, and a full pipeline regeneration whose output is `git diff --quiet`-identical to the committed `chip_database.json`
- `tests/test_build_db_pinout_fork.py` permanently pins the boundary against all eleven real `size_bytes` values shipped in the database plus the `262144`/`262145` one-step-past pair — a future edit to this fork reddens immediately instead of only being caught by a future full regeneration

## Task Commits

Each task was committed atomically, inside the submodule (except the gitlink advance):

1. **Task 1: Put the submodule on the milestone branch and make the four datasheets resolve** - `firestarter_app@63fb97f` (docs) — completed in a prior session
2. **Task 2: DECISION checkpoint** - no code commit; operator selected `derive-plus-test` on 2026-09-18, recorded above
3. **Task 3: Derive away the 262144 size threshold and prove the regeneration byte-identical** - `firestarter_app@5fec5eb` (feat)

**Gitlink advance:** `meta@ba6af22a` (chore: advance firestarter_app gitlink)

**Plan metadata:** committed alongside this SUMMARY.md (see final commit in this plan's history)

_Note: Task 3 is `tdd="true"`; behavior was proven via the pre-existing `<verify>` automation (regeneration byte-identity, exhaustive integer check, comment-check) plus the new pinning test module, rather than a separate RED→GREEN→REFACTOR commit sequence, because the change is a single-expression substitution whose correctness gate is the regeneration diff itself, not new application behavior._

## Files Created/Modified
- `firestarter_app/datasheets/MBM27C1000.pdf` - vendored gh#70 attachment (Fujitsu MBM27C1000-15/-20/-25, April 1988, Ed. 2.0)
- `firestarter_app/datasheets/MBM27128.pdf` - newly git-tracked (pre-existing on disk)
- `firestarter_app/datasheets/MBM27C4001.pdf` - newly git-tracked (pre-existing on disk)
- `firestarter_app/tools/build_db.py` - `_PGM_ON_PIN31_MAX_SIZE` constant deleted; its one comparison site now reads `(mem_size - 1).bit_length() <= 18`
- `firestarter_app/tests/test_build_db_pinout_fork.py` - new: 13 parametrized cases pinning the derived boundary
- `firestarter_app` (gitlink in meta repo) - advanced to `5fec5eb`

## Decisions Made
- **Task 2 checkpoint, operator ruling, 2026-09-18: option id `derive-plus-test`.** Derive the threshold away AND add a permanent boundary test, over `derive` alone or `keep` the constant under OVR-06.
- The pre-existing comment neighborhood at `build_db.py:144-146` needed no rewrite after the constant's deletion — it describes unrelated deleted symbols (`DIP28_VARIANT_MAP`, `PIN_MAP_TO_PINOUT`, `PIN_MAP_PROTO_TO_PINOUT`), not `_PGM_ON_PIN31_MAX_SIZE`, so every sentence there still has an antecedent.
- `gsd_run query commit` was not used for any commit in this plan, per this project's standing rule that the verb has twice self-created a stray `gsd/v1.40-...` branch mid-plan in this repository. All commits were made with plain `git commit`, with an explicit branch check before and after each one.

## Deviations from Plan

None - plan executed exactly as written, including the Task 2 operator ruling.

## Issues Encountered
None. `gitlab.com` was reachable for the Task 3 precondition; the regeneration completed in under 2 seconds and reported `746 total` as expected.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter_app` is on the correct milestone branch for every remaining plan in this phase to commit against.
- The three OVR-03-relevant datasheets are resolvable for plan `197-03`'s pulse corrections (D-19) and any later OVR-03 entry citing `MBM27128`, `MBM27C1000`, or `MBM27C4001`.
- `_PGM_ON_PIN31_MAX_SIZE` is fully removed; OVR-06's eventual "empty list" answer no longer needs to account for it. `NMOS_TRUE_VPP_MV`, `_AT28C_DIP24_NAMES`, and `_ETYPE_RELABEL` remain and are the subject of later plans (D-06/D-07/D-08).
- No blockers. Plan `197-02`'s tracer slice (the override file and its loader) can proceed against a byte-identical, unmodified-elsewhere `chip_database.json` baseline.

---
*Phase: 197-the-override-mechanism-and-the-program-pulse*
*Completed: 2026-09-18*
