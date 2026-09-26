---
phase: 136-dev-tools-channel-gating
plan: 04
subsystem: cli
tags: [syrupy, snapshot-testing, click, mypy, ci-parity, phase-close]

# Dependency graph
requires:
  - phase: 136-dev-tools-channel-gating
    plan: 02
    provides: "the CHAN-05 dev() group docstring rewrite that invalidated test_help_dev (and, discovered by 136-02, test_help too)"
  - phase: 136-dev-tools-channel-gating
    plan: 03
    provides: "final production/test state of the phase -- mypy 33/35 checked 130, full suite 1492 passed / 2 failed (both snapshot-only, both named for this plan)"
provides:
  - "tests/__snapshots__/test_characterization.ambr's test_help and test_help_dev entries, re-baselined deliberately and diff-scoped to exactly the docstring header text"
  - "136-CI-PARITY.md's ## After section -- the phase's real, measured post-edit CI-parity/mypy state, closing the Before/After pair 136-01 opened"
affects: [136.1, 137]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Named, justified snapshot re-baseline: observe RED first (old snapshot vs new rendered text), diff-scope the update to confirm only the intended text changed, state the justification explicitly in the SUMMARY -- never a blind --snapshot-update run-and-commit"

key-files:
  created: []
  modified:
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - .planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md

key-decisions:
  - "Re-baselined BOTH test_help and test_help_dev in a single --snapshot-update invocation scoped with -k, not just the one snapshot the plan's own frontmatter/136-VALIDATION.md named -- 136-02-SUMMARY.md's 'Known Test Regressions' table already flagged the second (test_help) as a plan-time gap discovered during execution, and this plan's own critical-traps context called it out explicitly"
  - "Zero requirements ticked by this plan. CHAN-05 appears in this plan's frontmatter only because Task 1 is a downstream consequence of that requirement's docstring rewrite (plan 136-02); it was already ticked there and is NOT re-ticked here. All seven CHAN-0X requirements were already Complete in REQUIREMENTS.md before this plan ran (confirmed by grep before starting) and remain untouched by this plan's own edits"

requirements-completed: []

coverage:
  - id: D1
    description: "test_help and test_help_dev snapshots re-baselined deliberately (RED observed first, diff scoped to docstring-only text, justification named in this SUMMARY) after the CHAN-05 docstring rewrite"
    verification:
      - kind: unit
        ref: "tests/test_characterization.py::test_help, ::test_help_dev -- pytest tests/test_characterization.py -o addopts=\"\" -q (35 passed, 30 snapshots passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "136-CI-PARITY.md's ## After section records a real post-edit mypy count (33, watermark 35, checked 130) via tools/ci_replica_venv.sh, compared explicitly against ## Before (delta: 0, flat)"
    verification:
      - kind: other
        ref: "tools/ci_replica_venv.sh full run, recorded verbatim in 136-CI-PARITY.md ## After §3"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full test suite green at phase close (0 failures), RESEARCH §5 blast-radius file set and tests/test_py32_channel_gating.py re-confirmed unchanged and green"
    verification:
      - kind: unit
        ref: ".venv/ci-replica/bin/python -m pytest tests/ -o addopts=\"\" -q -- 1494 passed, 0 failed, 30 snapshots passed"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-08-05
status: complete
---

# Phase 136 Plan 04: Snapshot Re-Baseline + CI-Parity Close Summary

**Deliberately re-baselined BOTH the `test_help_dev` snapshot the plan named AND the `test_help` snapshot 136-02 separately discovered breaks by the same mechanism, diff-scoped to prove only the CHAN-05 docstring text changed; then measured and recorded the phase's real post-edit CI-parity state -- mypy flat at 33/35 (checked 130), full suite 1494 passed / 0 failed, zero headroom spent across the whole phase.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-05T12:08:00Z (approx., immediately following 136-03's completion)
- **Completed:** 2026-08-05T12:32:49Z
- **Tasks:** 2 (both `type="auto"`, neither `tdd="true"`)
- **Files modified:** 2 (1 submodule snapshot fixture, 1 meta-repo CI-parity doc)

## Accomplishments

- **Task 1 -- named, justified snapshot re-baseline, scoped to TWO entries, not one.** Ran
  `pytest tests/test_characterization.py -k "test_help_dev or (test_help and not test_help_)" -o addopts="" -q -vv`
  first and confirmed both `test_help` and `test_help_dev` FAILED against the stale snapshot (the
  CHAN-05 docstring rewrite changed the text both tests pin) -- verbatim RED captured below. This
  plan's own frontmatter and `136-VALIDATION.md`'s wave-4 row name only `test_help_dev`; the second
  failure (`test_help`) was flagged as a discovered gap in `136-02-SUMMARY.md`'s "Known Test
  Regressions" table (Click renders a group's top-level `short_help` from the same first docstring
  line, so the `dev` group's own one-line listing in `firestarter --help`'s `Commands:` block
  changed too) and repeated in this plan's own critical-traps context. Re-baselining only the named
  snapshot would have left the suite red; both were re-baselined together, deliberately, in a single
  `-k`-scoped `--snapshot-update` invocation -- never a blanket, unscoped `--snapshot-update`.
- Diffed the `.ambr` file afterward (`git -C /workspaces/firestarter_app diff --unified=0`) and
  confirmed the changed lines are confined to exactly two regions: the `dev` line's rendered
  `short_help` text inside `test_help`'s top-level `Commands:` listing, and the docstring header
  lines inside `test_help_dev`'s own body. `test_help_dev`'s own `Commands:` block -- all 8 `dev`
  subcommands, same order, same one-line summaries -- is byte-identical before and after, confirmed
  by direct inspection of the updated snapshot text.
- **Task 2 -- phase-close CI-parity `## After` section**, appended to `136-CI-PARITY.md` without
  touching the existing `## Before` section. `tools/ci_parity.sh`: legs 1-3 exit 0, leg 4 exit 2
  (expected local ambient-numpy PEP-695 truncation, unchanged shape from `## Before`). `tools/ci_replica_venv.sh`:
  **mypy errors: 33 (watermark: 35), checked 130 source files** -- byte-identical to plan `136-03`'s
  final measurement and to `## Before`'s own 33/35 starting count; **headroom delta: 0, stated
  explicitly as a flat number, not "similar."** Full suite via the ci-replica python:
  **1494 passed, 0 failed**, 30 snapshots passed -- both previously-deferred regressions gone, no
  third failure surfaced. RESEARCH §5's blast-radius file set (`test_cli_handlers.py`,
  `test_consistency_check.py`, `test_eprom_operations.py`, `test_serial_comm.py`,
  `test_validate_oracle.py`, `test_diagnostic_report.py`, `test_matrix_artifact.py`,
  `test_validate_family_cmd.py`) re-run independently: **244 passed**. `tests/test_py32_channel_gating.py`
  (the pattern this phase's own subprocess harness adapted) re-run independently: **14 passed**.
  `git -C /workspaces/firestarter_app status --porcelain -- firestarter` printed nothing -- the
  firmware submodule was never touched, across the whole phase.

## Task Commits

Task 1 committed in the **submodule** (`firestarter_app`, `gsd/v1.30-sdp-surface-retirement`); Task 2
committed in the **meta repo** (`/workspaces`, `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`)
-- per this plan's own `<repo_topology>`, the two commits are separate, in separate repos.

1. **Task 1: Re-baseline `test_help` + `test_help_dev`, named and justified** - `b1d8f73` (test, submodule) - `tests/__snapshots__/test_characterization.ambr`
2. **Task 2: Record the phase's `## After` CI-parity state + full regression** - `0e99fa4` (docs, meta repo) - `.planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md`

**Plan metadata:** committed separately below (meta repo, this SUMMARY + STATE.md + ROADMAP.md; no REQUIREMENTS.md edit -- see Requirements section).

## Files Created/Modified

- `firestarter_app/tests/__snapshots__/test_characterization.ambr` (submodule) -- `test_help` and
  `test_help_dev` entries re-baselined; every other entry in the file untouched.
- `.planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md` (meta repo) -- `## After` section
  appended; the existing `## Before` section left byte-identical.

## Decisions Made

- **Re-baselined two snapshots, not the one named in the plan's own frontmatter/must_haves.** The
  plan's `must_haves.truths` and `136-VALIDATION.md`'s wave-4 row both name only `test_help_dev`.
  `136-02-SUMMARY.md`'s own "Known Test Regressions" table (written during plan 136-02's execution)
  and this plan's `<critical_traps_for_this_plan>` context both already flagged the second failure
  (`test_help`) as a measured, documented correction -- not a silent scope expansion invented here.
  Re-baselining only `test_help_dev` would have left the suite at 1 failure, violating this plan's
  own "full suite must be fully green" success criterion.
- **Single `-k`-scoped `--snapshot-update` invocation covering exactly these two tests**, run only
  after both were independently observed RED against the stale snapshot. This satisfies the
  hard-requirement-6 shape (RESEARCH §4): named, justified, diff-confirmed-scoped -- never a blind,
  broad `--snapshot-update`.
- **No requirement ticked by this plan.** `CHAN-05` sits in this plan's frontmatter `requirements`
  list only because Task 1 exists as a downstream consequence of that requirement's docstring
  rewrite (plan `136-02`, which already ticked it). All seven CHAN-0X rows were confirmed `[x]`
  Complete in `REQUIREMENTS.md` before this plan began (`grep -n "CHAN-0" .planning/REQUIREMENTS.md`)
  and this plan makes no edit to that file at all.

## Deviations from Plan

### Auto-fixed Issues

None. No bug, missing functionality, or blocking issue was discovered outside the plan's own
(corrected, per the critical-traps context) scope.

### Plan-Time Correction (documented, not a deviation)

**1. Re-baselined two snapshots instead of the one named in the plan's `must_haves`/`136-VALIDATION.md`.**
- **Found during:** Task 1's initial RED-observation run.
- **Issue:** The plan's own frontmatter (`must_haves.truths`) and `136-VALIDATION.md`'s wave-4 row
  each name only `test_help_dev`. `136-02-SUMMARY.md`'s "Known Test Regressions" table already
  measured and named the second failure (`test_help`) as a plan-time gap for this plan to inherit,
  and this plan's own execution context repeated that warning explicitly under
  `<critical_traps_for_this_plan>`.
- **Action taken:** Re-baselined both, in the same `-k`-scoped invocation, with the correction
  stated here plainly per this plan's own `<critical_traps_for_this_plan>` instruction ("record in
  your SUMMARY that the plan's own scope said one -- a measured correction, not a silent
  expansion").
- **Files affected:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`.
- **Verification:** Both tests pass individually and as part of the full 35-test
  `test_characterization.py` module (35 passed, 30 snapshots passed); full suite 1494 passed, 0 failed.
- **Committed in:** `b1d8f73`.

---

**Total deviations:** 0 auto-fixed. 1 plan-time correction (measured and pre-flagged by 136-02's own
SUMMARY and this plan's own critical-traps context, not discovered fresh here).
**Impact on plan:** None on scope or requirements -- this plan ticks zero requirements either way.
The correction was necessary to satisfy the plan's own "full suite green, 0 failures" success
criterion; omitting it would have left 1 known failure at phase close.

## Verbatim RED Output (pre-update, both snapshots)

```
$ pytest tests/test_characterization.py -k "test_help_dev or test_help " -o addopts="" -q -vv
...
tests/test_characterization.py::test_help FAILED                         [  7%]
...
tests/test_characterization.py::test_help_dev FAILED                     [100%]

=================================== FAILURES ===================================
__________________________________ test_help ___________________________________
    def test_help(snapshot):
        """Pin top-level --help output."""
        stdout, stderr, rc = run_firestarter("--help")
        assert rc == 0
>       assert stdout == snapshot
E       AssertionError: assert [+ received] == [- snapshot]
E           '''
E            ...
E             config  Handles CONFIGURATION values.
E         -   dev     Debug command for development purposes.
E         +   dev     Development and diagnostic commands for the RURP shield.
E             erase   Erase an EPROM, if supported.
E            ...
E           '''
tests/test_characterization.py:173: AssertionError
________________________________ test_help_dev _________________________________
    def test_help_dev(snapshot):
        stdout, stderr, rc = run_firestarter("dev", "--help")
        assert rc == 0
>       assert stdout == snapshot
E       AssertionError: assert [+ received] == [- snapshot]
E           '''
E           ...
E         -   Debug command for development purposes.
E         +   Development and diagnostic commands for the RURP shield.
E         +
E         +   On a stable install, only `read` and `test` are available in this group --...
E           ...
E           '''
tests/test_characterization.py:331: AssertionError
--------------------------- snapshot report summary ----------------------------
2 snapshots failed. 13 snapshots passed.
=========================== short test summary info ============================
FAILED tests/test_characterization.py::test_help - AssertionError: assert [+ ...
FAILED tests/test_characterization.py::test_help_dev - AssertionError: assert...
================= 2 failed, 12 passed, 21 deselected in 8.21s ==================
```

Both failed for the identical reason (CHAN-05's docstring rewrite), confirming the re-baseline is
justified and not vacuous -- if either had unexpectedly still passed, the docstring rewrite would
not have actually changed anything observable at that surface.

## Post-update diff (scoped, `git -C firestarter_app diff --unified=0`)

```diff
@@ -81 +81 @@
-    dev     Debug command for development purposes.
+    dev     Development and diagnostic commands for the RURP shield.
@@ -128 +128,6 @@
-    Debug command for development purposes.
+    Development and diagnostic commands for the RURP shield.
+
+    On a stable install, only `read` and `test` are available in this group --
+    both are fully supported for end users, despite living inside a group named
+    `dev`. The remaining subcommands are development and bench tooling,
+    available only on a pre-release install.
```

Confirmed by direct inspection of the updated `test_help_dev` entry: the `Commands:` enumeration
(all 8 `dev` subcommands, same order, same one-line summaries) is untouched -- the diff above is the
entirety of the change, confined to the `dev` short_help line (`test_help`) and the docstring header
region (`test_help_dev`).

## Issues Encountered

None. Every command ran clean on the first attempt.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- **Phase 136 (Dev-Tools Channel Gating) is now fully closed.** All seven CHAN-0X requirements were
  ticked by plans `136-02`/`136-03`; this plan re-baselined the last two deferred snapshot
  regressions and recorded the phase's real, measured CI-parity cost: **mypy flat at 33/35 across
  the entire phase (zero headroom spent), full suite 1437 → 1494 passed (+57), 0 failures at close.**
- **Zero requirements ticked by this plan.** No `PROV-*` or `CLOSE-*` row was touched -- those belong
  to Phases 136.1 and 137, neither of which has run.
- `.planning/STATE.md`'s frontmatter (`total_phases: 7`, `total_plans`, `completed_plans`, `percent`)
  will be advanced by this plan's own state-update step; per the recurring state-tool corruption bug
  noted in project memory, the frontmatter will be diffed against a pre-edit snapshot and
  hand-restored if the tool drops or corrupts any field.
- Phase 136.1 (PROV-01…06) and Phase 137 (RELOCK-07 + CLOSE-0X) are next; both were already
  activated in `.planning/REQUIREMENTS.md`'s traceability table (`Pending`) before this plan ran.

## Self-Check: PASSED

`tests/__snapshots__/test_characterization.ambr` confirmed present on disk with the re-baselined
entries; `.planning/phases/136-dev-tools-channel-gating/136-CI-PARITY.md` confirmed present with
both `## Before` and `## After` headings (grep count: 1 `## After` heading, 1 `## Before` heading).
Both commit hashes independently re-verified in their own repo's `git log --oneline --all`:
`b1d8f73` FOUND in `firestarter_app` (submodule); `0e99fa4` FOUND in the meta repo (`/workspaces`).
`136-04-SUMMARY.md` itself confirmed present on disk. No missing items.

---
*Phase: 136-dev-tools-channel-gating*
*Completed: 2026-08-05*
