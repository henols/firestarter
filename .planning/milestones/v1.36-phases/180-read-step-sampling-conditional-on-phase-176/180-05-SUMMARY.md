---
phase: 180-read-step-sampling-conditional-on-phase-176
plan: 05
subsystem: testing
tags: [gap-closure, re-seal, requirements-ledger, roadmap, ast, pytest, mypy]

# Dependency graph
requires:
  - phase: 180-read-step-sampling-conditional-on-phase-176 (plan 04)
    provides: "the seed's R3 removal by absence, WR-01/WR-02 hardened pins, IN-01 closed"
provides:
  - "IN-02 closed: one shared _alternating_read_side_effect builder, both read-step verdict legs call it with their own ordered pair"
  - "PRUNE-08 recorded Complete again in both REQUIREMENTS.md locations, gated on measured fixes rather than a plan promise"
  - "ROADMAP.md's Phase 180 section extended with a Gap closure grouping (180-04/180-05) and a corrected 5-plan count"
  - "The seven-leg green-tree battery re-run and passing at 2247, the phase's final measured floor"
affects: [phase-181-planning, future-dev-test-milestones]

actuals:
  tokens: 4100
  tasks: 3
  commits: 6

tech-stack:
  added: []
  patterns:
    - "Shared test fixture builder replacing duplicated nested closures, without touching the assertions the closures gated (D-09/D-06 precedent: refactor the fixture, never the verdict)"
    - "Gate the Complete flip on measured scalars from disk, not on a plan's promise (same precedent 180-03 set, now re-run against a different precondition)"

key-files:
  created:
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-05-side-effect-helper.txt
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-05-requirement-reseal.txt
    - .planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-05-phase-seal.txt
  modified:
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_readback_inventory.py
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "Fixed a 2-error mypy regression in test_readback_inventory.py (introduced by plan 180-04's WR-02 hardening, not by this plan's own edits) rather than leaving Task 3's battery red — the file is outside this plan's files_modified list but the failure directly blocked this plan's own mypy-watermark gate, and Rule 3 (auto-fix blocking issues) covers a type-narrowing fix that changes no behavior and adds no test."
  - "Corrected a self-authored evidence scalar (plans_3_plans_global_count) from an unanchored substring count of 11 to the exact-line-match count of 7 that the plan's own gate actually measures, in a follow-up commit, rather than leave a wrong number standing in a transcript whose whole purpose is measured accuracy."

requirements-completed: [PRUNE-08]

coverage:
  - id: D1
    description: "IN-02 closed: one _alternating_read_side_effect builder shared by both read-step verdict legs, zero assertion lines removed since app anchor 93a1672"
    requirement: "PRUNE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py -k read_step (4 passed)"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_chip_test.py (162 passed, module total unchanged)"
        status: pass
    human_judgment: false
  - id: D2
    description: "PRUNE-08 re-flipped to Complete in both REQUIREMENTS.md locations, gated on measured fixes (seed fragments at zero, both hardened pins present, builder present, both trees clean) rather than a plan promise; exactly two lines changed"
    requirement: "PRUNE-08"
    verification:
      - kind: other
        ref: "evidence/180-05-requirement-reseal.txt (5 ledger-count assertions, 4-marker diff ceiling against pinned blob 6366d59d, all rc=0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Phase seal: ROADMAP.md Gap closure grouping (5 plans, 180-04/180-05 ticked) with both regions outside the Phase 180 section cmp-identical against pinned blob cc949993; seven-leg battery green with the full suite at the measured floor of 2247"
    requirement: "PRUNE-08"
    verification:
      - kind: other
        ref: "evidence/180-05-phase-seal.txt (7 legs, cleanliness legs, tokenize comment gate, two roadmap cmp legs, all rc=0)"
        status: pass
      - kind: integration
        ref: "firestarter_app: python -m pytest tests/ -o addopts=\"\" -q (2247 passed, 0 failed)"
        status: pass
    human_judgment: false

duration: 19min
completed: 2026-09-08
status: complete
---

# Phase 180 Plan 05: IN-02 Fixture Sharing, PRUNE-08 Re-Seal, Seven-Leg Battery Summary

**One shared alternating-read-side-effect builder closes IN-02, PRUNE-08 re-flips to Complete only after every gap fix measured zero/present/clean, and the seven-leg battery is green at a measured 2247 passed — with a two-error mypy regression from the sibling gap-closure plan caught and fixed along the way.**

## Performance

- **Duration:** 19 min
- **Started:** 2026-09-08T18:11:00Z
- **Completed:** 2026-09-08T18:30:18Z
- **Tasks:** 3
- **Files modified:** 4 (test_chip_test.py, test_readback_inventory.py, REQUIREMENTS.md, ROADMAP.md), plus 3 new evidence files

## Accomplishments

- **Task 1 (IN-02):** Added `_alternating_read_side_effect(*call_returns: bool)` to `firestarter_app/tests/test_chip_test.py`'s existing read-side-effect-builder cluster (between `_writes_fill_at_requested_region` and `test_runs_boundary_rejects_below_2_before_any_operator_call`). Both `test_read_step_last_run_failure_yields_bad` and `test_read_step_first_run_failure_with_passing_last_run_yields_ok` now call it with their own ordered pair (`(True, False)` and `(False, True)`) instead of each defining a nested `_read_side_effect` closure. The pre-existing, genuinely different divergence closure inside `test_read_step_disagreement_is_divergence_metric_not_marginal` (which varies its payload per call) is untouched. Module still reports `162 passed`; `-k read_step` still reports `4 passed`; the diff since app anchor `93a1672` removes zero lines whose first non-space token is `assert`.
- **Task 2 (requirement re-seal):** Verified the Task 2 precondition as measured scalars — all three of the seed's rejected-sampler fragments (`Escalate to the full second read`, `**Cost, stated:**`, `256 B block at each`) at zero occurrences; `connect_route_calls` and `_last_ok_assignment_shape` present in `test_readback_inventory.py`; `_alternating_read_side_effect` present in `test_chip_test.py`; both repositories porcelain-clean — before touching `REQUIREMENTS.md`. Made exactly two hand edits: line 60's checkbox (`[ ]` → `[x]`) and line 175's traceability row (`Gaps Found` → `Complete`). The five ledger counts moved 19/27/18/27/1 → 18/28/18/28/0; `Pending` stayed at 18 because the row this phase flips was reading `Gaps Found`, not `Pending` (unlike plan 180-03's flip, which did move `Pending`). Diff against pinned blob `6366d59d` carries exactly 4 changed-line markers (2 lines changed); MEAS-01, R4-01, the Coverage block and Phase 181's rows are untouched.
- **Task 3 (phase seal):** Extended `ROADMAP.md`'s Phase 180 section by hand: `**Plans**: 3 plans` → `**Plans**: 5 plans` (inside the section only — the exact-line-match global count of that string moved 8 → 7, confirming only the one intended line changed), then appended a `**Gap closure**` grouping (copying Phase 174's form) naming both gap plans with `- [x] 180-04-PLAN.md` and `- [x] 180-05-PLAN.md`. Both roadmap regions outside the section — 434 lines through the `### Phase 180:` heading, 5386 lines from `### Phase 181:` onward — are `cmp`-identical against pinned blob `cc949993`. The phase-level checkbox in the `### Phases` milestone list stays unticked.
- **Battery, re-run and green:** All seven legs pass — `ruff check`/`ruff format --check`, the mypy watermark (exactly `mypy errors: 35 (watermark: 35)`, after the fix below), `snapshot_report_shapes.py --check`, `check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, and the full suite at **2247 passed, 0 failed** — the measured floor (2245 at Phase 180's original final HEAD, plus plan 180-04's two additive `test_readback_inventory.py` legs). `tokenize` COMMENT counts held at exactly 621 (`test_chip_test.py`) and 0 (`test_readback_inventory.py`). Changed-file set since app anchor `93a1672` is exactly `tests/test_chip_test.py` and `tests/test_readback_inventory.py`; both submodules and `firestarter/data/chip_database.json` are porcelain-clean.

## Task Commits

Task 1 (submodule `firestarter_app` on `gsd/v1.36-dev-test-fidelity`, plus meta-repo gitlink bump):
1. **Task 1: shared alternating-read builder (IN-02)** — `dd9fe88` (test, inside `firestarter_app`)
2. **Task 1 evidence + gitlink** — `e39bb91e` (test, in `/workspaces`)

Task 2 (meta repo `/workspaces` on `gsd/v1.36-dev-test-fidelity-planning`):
3. **Task 2: PRUNE-08 re-flip, exactly two lines** — `36135c6c` (docs) — pinned range `36135c6c^..36135c6c` proves exactly two lines of `.planning/REQUIREMENTS.md` changed and no other file
4. **Task 2 evidence** — `61cd927c` (docs)

Task 3 (meta repo, plus one Rule-3 fix inside the submodule discovered while running Task 3's battery):
5. **Rule 3 fix: mypy type-narrowing in `_last_ok_assignment_shape`** — `04fd982` (fix, inside `firestarter_app`) — see Deviations below
6. **Task 3: Gap closure grouping + seven-leg battery seal** — `2b93c20a` (docs, in `/workspaces`)
7. **Evidence scalar correction** — `bc8d0d82` (docs) — see Deviations below

**Plan metadata:** to be committed after this SUMMARY.

## Files Created/Modified

- `firestarter_app/tests/test_chip_test.py` — new `_alternating_read_side_effect` builder; two read-step verdict leg bodies rewritten to call it instead of defining nested closures.
- `firestarter_app/tests/test_readback_inventory.py` — `_last_ok_assignment_shape`'s loop narrowed to the four AST node types it already restricts target extraction to, fixing a 2-error mypy regression introduced by plan 180-04.
- `.planning/REQUIREMENTS.md` — PRUNE-08's v1 checkbox and traceability row both flipped to Complete; no other line touched.
- `.planning/ROADMAP.md` — Phase 180 section: plan count 3→5, `**Gap closure**` grouping appended with both gap-plan boxes ticked; nothing outside the section moved.
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-05-side-effect-helper.txt` — new.
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-05-requirement-reseal.txt` — new.
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-05-phase-seal.txt` — new.

## Measured Values

**Module counts, before → after (Task 1):** `test_chip_test.py` 162 → 162 passed (unchanged — no test added or removed); `-k read_step` 4 → 4 passed. `test_readback_inventory.py` stayed at 12 passed through the Task 3 mypy fix (no test added or removed there either).

**Requirement ledger, before → after (Task 2):** unchecked 19→18, checked 27→28, `Pending` 18→18 (unchanged — see note above), `Complete` 27→28, `Gaps Found` 1→0. Diff against pinned blob `6366d59da8cc946e60f7085092f0ef85c7cc4c75`: exactly 4 changed-line markers (2 lines).

**Roadmap regions (Task 3):** both `cmp`-identical against pinned blob `cc9499934b4757899719ed35acc8d44d9ac89b31` — 434 lines through the `### Phase 180:` heading, 5386 lines from `### Phase 181:` to end of file. Exact-line-match count of `**Plans**: 3 plans` across the whole file: 8 (pinned blob) → 7 (after this plan's one intended edit).

**Full suite (Task 3):** `2247 passed, 1 warning in 360.73s (0:06:00)`, 0 failed — at or above the required floor of 2247.

**mypy watermark (Task 3, before the fix):** `Found 37 errors in 16 files (checked 173 source files)` — 2 over the watermark, both at `test_readback_inventory.py:430` (`"AST" has no attribute "lineno"` / `"col_offset"`). **After the fix:** `mypy errors: 35 (watermark: 35)`.

## Decisions Made

- Fixed the mypy regression via `isinstance` narrowing rather than a `# type: ignore` comment — the latter would be a comment, forbidden by this project's hard rule, and narrowing is also the more correct fix: it makes the type-checker's proof match what the code already guarantees at runtime (the loop only reaches the append when `n` is one of the four node types), rather than suppressing the check.
- Split Task 2's `.planning/REQUIREMENTS.md` edit into its own commit, separate from the evidence-file commit, so the acceptance criterion "this task's own commit changes exactly two lines of `.planning/REQUIREMENTS.md` and no other file" is verifiable directly against a single commit's diff rather than requiring the reader to subtract an evidence file from a combined diff.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed a 2-error mypy regression in `test_readback_inventory.py` discovered while running Task 3's battery**
- **Found during:** Task 3 (running battery leg 3, `tools/check_mypy_watermark.py`)
- **Issue:** Plan 180-04's WR-02 hardening (`_last_ok_assignment_shape`, committed at app `d164d74`, outside this plan's own `files_modified`) walks `ast.walk(fn)`-typed nodes (`ast.AST`) and reads `.lineno`/`.col_offset` off that base type inside an `if` block whose `isinstance` narrowing on `n` does not survive past the `if`/`elif` to the later `append` call. `ast.AST` does not declare `lineno`/`col_offset` in typeshed (only `ast.stmt`/`ast.expr` subclasses do), so mypy reported 2 new errors, pushing the app-wide count from the watermarked 35 to 37 — a hard fail on this plan's own Task 3 acceptance criterion ("prints exactly `mypy errors: 35 (watermark: 35)`"). 180-04 did not run this battery leg itself, so the regression was invisible until this plan's seal.
- **Fix:** Added an `isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.NamedExpr))` check alongside the existing `target` check before the `targets.append(...)` call — the same four types the loop already restricts `target` extraction to, all of which declare `lineno`/`col_offset` via `ast.stmt`/`ast.expr`. No behavior change: `n` was already guaranteed to be one of those four types whenever `target` was set to a non-`None` `ast.Name`, so the added check is always `True` at runtime.
- **Files modified:** `firestarter_app/tests/test_readback_inventory.py`
- **Verification:** `mypy` back to exactly `35 (watermark: 35)`; `test_readback_inventory.py` still `12 passed`; `ruff check`/`ruff format --check` clean; `tokenize` comment count still 0 for the file (no comment added).
- **Committed in:** `04fd982` (fix, inside `firestarter_app`)

**2. [Housekeeping] Corrected a self-authored evidence scalar after re-measuring with the exact gate command**
- **Found during:** Task 3, immediately after writing `evidence/180-05-phase-seal.txt`
- **Issue:** First draft of the transcript recorded `plans_3_plans_global_count=11`, measured with an unanchored `grep -c` (substring match) rather than the plan's own `grep -cxF` (exact-line match). The exact-line count is 7, matching the pinned pre-edit blob's 8 minus the one line this plan's own edit changed.
- **Fix:** Re-measured with the exact gate command and corrected the scalar.
- **Files modified:** `.planning/phases/180-read-step-sampling-conditional-on-phase-176/evidence/180-05-phase-seal.txt`
- **Verification:** Re-ran the full evidence-file verify block; still passes (the scalar is not itself gated, but the transcript's purpose is measured accuracy).
- **Committed in:** `bc8d0d82`

---

**Total deviations:** 2 (1 auto-fixed blocking issue, 1 self-correction of evidence). **Impact on plan:** The mypy fix was necessary for Task 3's own stated acceptance criterion to be true and changed zero behavior; without it the phase seal could not honestly claim "seven legs green." No scope creep — both fixes stayed inside the phase's own two touched test modules and its own evidence directory.

## Issues Encountered

None beyond the two deviations above, both resolved within this plan's own execution.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- IN-02 (`180-REVIEW.md`) is closed: one shared builder, no assertion changed, the genuinely different divergence closure untouched.
- PRUNE-08 is `Complete` in both `.planning/REQUIREMENTS.md` locations, flipped only after every named gap fix measured zero/present/clean — not on the strength of a plan.
- `.planning/ROADMAP.md`'s Phase 180 section is fully caught up: 5 plans, a `**Gap closure**` grouping, nothing outside the section moved. The phase-level checkbox is left unticked for phase completion to decide.
- The seven-leg battery is green with the full suite at 2247, the phase's final measured floor for whatever plan runs next against this app tree.
- Zero product-source lines, zero firmware lines, zero `chip_database.json` bytes changed across the whole gap-closure pass (180-04 + 180-05). `tokenize` COMMENT counts held at 621/0 throughout.
- Phase 180 is ready for `/gsd-verify-work` re-verification and, pending that, phase completion.
- No blockers.

---
*Phase: 180-read-step-sampling-conditional-on-phase-176*
*Completed: 2026-09-08*

## Self-Check: PASSED

- All key files exist on disk: `test_chip_test.py`, `test_readback_inventory.py`, `REQUIREMENTS.md`, `ROADMAP.md`, and all three new evidence transcripts.
- Meta-repo commits found (`git log --oneline --all | grep`): `e39bb91e`, `36135c6c`, `61cd927c`, `2b93c20a`, `bc8d0d82`, `ebf41313` (this SUMMARY's own commit).
- Submodule commits found (`git -C firestarter_app log --oneline --all | grep`, meta-repo `git log` does not carry submodule history): `dd9fe88`, `04fd982`.
- All acceptance criteria for all three tasks independently re-verified in this session and passed: builder call-site counts, nested-closure removal, pytest counts (162/4/12/2247), assertion-safety diff, ledger counts, pinned-blob diff ceilings, roadmap region `cmp` legs, mypy watermark, tokenize comment gate, and the seven-leg battery's `rc=0` count.
