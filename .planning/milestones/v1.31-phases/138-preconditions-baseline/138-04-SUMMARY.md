---
phase: 138-preconditions-baseline
plan: 04
subsystem: infra
tags: [git, pytest, python, ci-parity, host-suite, baseline, firestarter_app]

# Dependency graph
requires:
  - phase: "138-01"
    provides: "gsd/v1.31-27c-programming-algorithm-fidelity ref (created but not checked out) in firestarter_app, base SHA 4d18b645ab18a2d2465f0f623062e9249eb24132, recorded in 138-BRANCH-BASES.md section 4"
provides:
  - "firestarter_app worktree switched to and left checked out on gsd/v1.31-27c-programming-algorithm-fidelity, HEAD verified byte-for-byte equal to Plan 01's recorded base SHA"
  - "138-04-HOST-BASELINE.md -- the PREP-03 host-suite half of the baseline: branch/interpreter/package provenance, the full-suite count (1539 collected / 1539 passed / 0 skipped / 0 failed / 180.89s), both directory-name-dependent tests confirmed passing in place by node id, a verbatim output block, and an explicit, unreconciled divergence finding against 138-RESEARCH.md's figure for the identical commit"
affects: ["138-07 (assembles the whole-phase 138-BASELINE.md and ticks PREP-03/PREP-04, citing this artifact)", "Phase 144 TEST-03 (compares its CI-scoped host-suite claim against this pre-change count)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "In-place, CI-parity measurement discipline: run pytest from the real checkout directory under the pinned .venv/ci-replica interpreter with -o addopts=\"\", never a sibling/renamed directory or the devcontainer's ambient interpreter"
    - "Divergence recording without reconciliation: when a re-measurement disagrees with a prior artifact's figure for the identical ref, state both figures, name the command and location each came from, and record a plausible mechanism as unconfirmed context -- never adjust either number to force agreement"

key-files:
  created:
    - .planning/phases/138-preconditions-baseline/138-04-HOST-BASELINE.md
  modified: []

key-decisions:
  - "Recorded 138-RESEARCH.md's host-suite figure for commit 4d18b64 (1493 passed / 46 skipped) beside this run's in-place figure for the SAME commit (1539 passed / 0 skipped) as an explicit, unreconciled divergence -- neither number was adjusted. Research's own text states that row was measured in a directory named app_beta_live, not firestarter_app; named tests/fw_presence.py's 72 requires_fw sibling-repo-marker references as a plausible (unconfirmed, not independently re-verified) mechanism for the gap, since a differently-named checkout would also fail the ../firestarter/.git marker check"
  - "requirements-completed left empty and REQUIREMENTS.md untouched: this plan produces PREP-03's host-suite evidence only -- the tick is Plan 138-07's job once the whole phase's baseline is assembled, per this plan's own may_tick_requirements: [] constraint and the dispatching orchestrator's explicit requirement_scope_guard"
  - "Self-caught and corrected an internal accuracy overclaim before the Task 2 commit: an early draft sentence claimed the string '3.12' appeared in exactly two places in the artifact, but a later section also named it; reworded to an accurate, non-enumerated statement rather than leaving a false claim on record"
  - "Every numeric figure introduced during the divergence investigation (including the '72' cross-repo-reference count) was given an inline command citation to satisfy the artifact's own 'no orphan numbers' discipline, matching 131-CI-BASELINE.md's precedent"

requirements-completed: []

coverage:
  - id: D1
    description: "firestarter_app worktree switched from fix/dev-test-blank-check-after-erase to gsd/v1.31-27c-programming-algorithm-fidelity, with the zero-tracked-modification precondition asserted first and HEAD verified byte-for-byte equal to Plan 01's recorded base SHA"
    requirement: "PREP-03"
    verification:
      - kind: other
        ref: "138-04-HOST-BASELINE.md section 1 -- git symbolic-ref --short HEAD reads gsd/v1.31-27c-programming-algorithm-fidelity; git rev-parse HEAD == 4d18b645ab18a2d2465f0f623062e9249eb24132, matching 138-BRANCH-BASES.md section 4 exactly"
        status: pass
    human_judgment: false
  - id: D2
    description: "Full host suite measured under .venv/ci-replica (Python 3.11.15), in place in /workspaces/firestarter_app, with -o addopts=\"\" to preserve the count line: 1539 collected, 1539 passed, 0 skipped, 0 failed, 180.89s; both directory-name-dependent tests independently re-run by node id and confirmed passing"
    requirement: "PREP-03"
    verification:
      - kind: other
        ref: "138-04-HOST-BASELINE.md sections 3, 4 and 6 -- verbatim command and tail; the automated <verify> block for Task 1 (branch check + interpreter version check + 2-passed node-id check + 'ci-replica' string presence) passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Narrative artifact completed in 131-CI-BASELINE.md's discipline: verbatim output block, an explicit divergence check against research's figure for the identical commit (both values kept, unreconciled), the interpreter/count-line/directory-name constraints restated as measured facts, a 'what this number is and is not' section naming plan 07 as the CI-evidence owner, and a 5-item 'not established' list"
    requirement: "PREP-03"
    verification:
      - kind: other
        ref: "138-04-HOST-BASELINE.md sections 7-10; the automated <verify> block for Task 2 (addopts=\"\" present, 'divergence' and 'is not' present case-insensitively, firestarter_app count >= 3, a '$ ...pytest' line present) passed"
        status: pass
    human_judgment: false

# Metrics
duration: 16min
completed: 2026-08-08
status: complete
---

# Phase 138 Plan 04: Preconditions & Baseline — Host Baseline Summary

**firestarter_app switched to the v1.31 base (4d18b64) and measured under py3.11.15 CI parity at 1539 passed / 0 skipped — a genuine, unreconciled divergence from 138-RESEARCH.md's 1493 passed / 46 skipped figure for that identical commit, recorded with both values and a named-but-unconfirmed mechanism.**

## Performance

- **Duration:** 16 min
- **Started:** 2026-08-08T23:09:34Z (approximate, from STATE.md's last-updated timestamp immediately preceding dispatch)
- **Completed:** 2026-08-08T23:25:36Z
- **Tasks:** 2
- **Files modified:** 1 (created)

## Accomplishments

- Switched `/workspaces/firestarter_app` from `fix/dev-test-blank-check-after-erase` (`7fe8dea9`) to
  `gsd/v1.31-27c-programming-algorithm-fidelity`, after asserting zero modified tracked files (8
  pre-existing untracked files carried over unchanged). `git rev-parse HEAD` after the switch equals
  `4d18b645ab18a2d2465f0f623062e9249eb24132` — the exact base SHA Plan 01 recorded in
  `138-BRANCH-BASES.md` section 4, matched byte-for-byte.
- Measured the full host suite under the CI-parity interpreter `.venv/ci-replica/bin/python`
  (`Python 3.11.15`, not the devcontainer's ambient `3.12.13`), run in place with
  `-o addopts=""` to preserve the count line: **1539 collected, 1539 passed, 0 skipped, 0 failed,
  180.89s**. Confirmed the imported package (`/workspaces/firestarter_app/firestarter/__init__.py`,
  `3.0.0b20`) is the worktree's own copy, not an ambient or cached one.
- Independently re-ran the two directory-name-dependent tests by node id
  (`test_gen_validation_header.py::test_validate_spec_called_before_emission`,
  `test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing`) and confirmed
  **2 passed** — the positive, in-place evidence the plan required.
- Found a genuine divergence from `138-RESEARCH.md`'s recorded figure for this **identical** commit
  (`4d18b64`): research recorded **1493 passed / 46 skipped**; this run recorded **1539 passed /
  0 skipped**. Collected totals agree exactly (1539 = 1539); the pass/skip split does not. Traced a
  plausible (explicitly unconfirmed) mechanism: research's own text states that row was measured in a
  directory named `app_beta_live`, not `firestarter_app`, and `tests/fw_presence.py` gates 72
  cross-repo-test references on a sibling-repo `../firestarter/.git` marker that a differently-located
  checkout would fail. Recorded both figures, unaltered, per the plan's explicit no-reconciliation
  instruction.
- Authored `138-04-HOST-BASELINE.md` (211 lines) in `131-CI-BASELINE.md`'s narrative discipline: every
  figure attributed to the command and location that produced it, a verbatim output block, the
  divergence check above, the three constraints (interpreter/count-line/directory-name) restated as
  measured facts, a "what this number is — and is not" section naming Plan 07 as the CI-evidence
  owner, and a 5-item "not established by this measurement" list.

## Task Commits

Each task was committed atomically:

1. **Task 1: Switch the app worktree to the v1.31 branch and measure the full suite at CI parity** - `e7b91ed9` (docs)
2. **Task 2: Complete the host baseline narrative with its divergence check and its limits** - `cb04f89d` (docs)

**Plan metadata:** (this commit, immediately following)

_No sub-repo commit was made — this plan's `commits_land_in` is meta-only. `firestarter_app` was
switched to a different branch and measured but received zero commits and zero pushes throughout._

## Files Created/Modified

- `.planning/phases/138-preconditions-baseline/138-04-HOST-BASELINE.md` (created, 211 lines) - branch
  switch provenance (§1), interpreter/package provenance (§2), full-suite measurement provenance (§3),
  directory-name-dependent test proof (§4), post-measurement worktree state (§5), verbatim output (§6),
  the divergence check (§7), the three constraints restated as facts (§8), "what this number is/is
  not" (§9), and "not established by this measurement" (§10)

## Decisions Made

- **Divergence kept unreconciled, mechanism named as context only.** `138-RESEARCH.md` recorded
  1493 passed / 46 skipped for commit `4d18b64`; this run recorded 1539 passed / 0 skipped for the
  same commit, under the same interpreter. Both are stated in `138-04-HOST-BASELINE.md` section 7,
  attributed to their own command and measurement location, with neither number adjusted. A plausible
  mechanism (research's row was measured in a directory named `app_beta_live`, which would fail
  `tests/fw_presence.py`'s sibling-repo marker check and skip all `requires_fw`-gated tests) is offered
  explicitly as unconfirmed observation, not proof — this plan did not re-open or re-measure inside
  that other directory.
- **`requirements-completed: []`, REQUIREMENTS.md untouched.** Although this plan's own frontmatter
  lists `requirements: [PREP-03]`, its `may_tick_requirements: []` and the dispatching orchestrator's
  explicit requirement-scope guard both forbid ticking PREP-03 here. PREP-03 is a multi-plan
  requirement whose firmware halves are Plans 03/05/06's scope and whose tick is Plan 138-07's, once
  the whole-phase baseline is assembled. Verified via `grep`: `PREP-03` and `PREP-04` remain `[ ]` in
  `REQUIREMENTS.md`, unchanged by this plan.
- **Self-caught accuracy correction before commit.** An early draft sentence in section 2 claimed the
  string `3.12` appeared in exactly two places in the artifact; while checking the acceptance criteria
  a third occurrence (section 8's restatement of the interpreter constraint) was found, which would
  have made the claim false. Reworded to an accurate statement before Task 2's commit rather than
  leaving the overclaim on record.
- **Every figure named its command, including ones surfaced mid-investigation.** The "72" cross-repo
  `requires_fw` reference count (found while investigating the divergence) was given an inline
  `grep` citation rather than left as a bare number, to satisfy the artifact's own "no orphan numbers"
  rule.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' automated `<verify>` blocks and every acceptance
criterion in `138-04-PLAN.md` passed; no bug, missing functionality, blocking issue, or architectural
question arose. The divergence investigation (tracing the `fw_presence.py` mechanism) was explicitly
requested by Task 2's own action text ("state both values, identify which tree each belongs to") and
is not a deviation from the plan — it is the plan's own instruction, executed.

## Issues Encountered

None. The one notable finding — the host suite's pass/skip split disagreeing with research's figure
for the identical commit — is not an "issue" in the sense of something blocking execution; it is
exactly the kind of divergence the plan's `<honest_reporting>` instruction anticipated and required be
recorded, not resolved.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `/workspaces/firestarter_app` is left checked out on `gsd/v1.31-27c-programming-algorithm-fidelity`
  at `4d18b645ab18a2d2465f0f623062e9249eb24132`, ready for Phase 143's host-repo plans to land commits
  directly — no further branch setup needed there.
- `138-04-HOST-BASELINE.md` is on record for Plan 138-07 to cite directly into the whole-phase
  `138-BASELINE.md`, exactly as `138-BRANCH-BASES.md` and `138-02-PULSE-DISTRIBUTION.md` already are.
- **The unreconciled divergence (1493/46-skipped in research vs. 1539/0-skipped here, identical
  commit) is carried forward, not resolved.** Plan 138-07, when assembling the whole-phase baseline,
  should cite both figures as this artifact does rather than picking one — and should not attempt to
  re-derive research's exact 46-skipped list unless a future plan has a specific reason to.
- No CI run was dispatched or recorded by this plan — that remains Plan 138-07's scope, per this
  plan's own "what this number is — and is not" section.
- PREP-03 and PREP-04 remain `[ ]` open in `REQUIREMENTS.md`, exactly as before this plan ran — both
  are Plan 138-07's tick.

## Self-Check: PASSED

- FOUND: `.planning/phases/138-preconditions-baseline/138-04-HOST-BASELINE.md`
- FOUND commit: `e7b91ed9`
- FOUND commit: `cb04f89d`
- CONFIRMED: `git -C /workspaces/firestarter_app symbolic-ref --short HEAD` reads
  `gsd/v1.31-27c-programming-algorithm-fidelity`
- CONFIRMED: `git -C /workspaces/firestarter_app rev-parse HEAD` reads
  `4d18b645ab18a2d2465f0f623062e9249eb24132`

No missing items.

---
*Phase: 138-preconditions-baseline*
*Completed: 2026-08-08*
