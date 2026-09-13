---
phase: 188-the-tools-directory
plan: 09
subsystem: infra
tags: [gsd-ledger, retirement, roadmap-amendment, requirements-traceability, verdict-note]

requires:
  - phase: 188-the-tools-directory
    provides: "All eight prior plans (188-01 through 188-08) complete — the phase's entire measured outcome, which this plan writes onto the permanent record rather than re-deriving"
provides:
  - "The verdict note at .planning/notes/host-tools-retirement.md — every retired item named with its measured line count, all eight disclosed costs stated as losses, the OD-1-to-D-25 supersession, the deleted CLAUDE.md regression-guard prose quoted verbatim, the TOOLS-04 disposition tension, and the residual-gap statement"
  - "REQUIREMENTS.md's seven TOOLS traceability rows amended per D-22 — five RETIRED with cause, one satisfied by family retirement, one Complete — with only TOOLS-05's checkbox flipped"
  - "ROADMAP.md's Phase 188 section amended in place: all seven success criteria plus the not-in-scope paragraph carry an AMENDED marker with the conflict quoted, and the phase's own plan checklist is complete (9/9)"
  - "The three folded planning items settled: the orphaned-host-tools todo closed with the judgment-vs-reference-count distinction, the provenance todo's tools-half figure corrected to its measured zero, the gate-expiry seed marked resolved"
affects: []

actuals:
  tokens: 7400
  tasks: 3
  commits: 3
  plan_head_before: "dafa8af3"

tech-stack:
  added: []
  patterns:
    - "A whole-phase retirement verdict is written from the sibling SUMMARYs' measured figures, never re-derived from the plan's own projections — every line count, test-collection boundary and disclosed cost in the note traces to a specific prior plan's own measurement."
    - "A requirement answered by subtraction gets a distinct disposition word (RETIRED, or a phase-specific bespoke word like 'satisfied by family retirement') rather than Complete, and only the disposition word — never the checkbox — carries that distinction; the checkbox stays reserved for 'this phase built something.'"
    - "An in-place ROADMAP criterion amendment retains the original text verbatim and appends a bolded, phase-and-decision-attributed correction — never a silent rewrite to match what happened."

key-files:
  created:
    - .planning/notes/host-tools-retirement.md
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md
    - .planning/seeds/phase-gate-expiry-discipline.md
    - .planning/todos/completed/2026-09-12-retire-two-orphaned-host-tools.md

key-decisions:
  - "TOOLS-04's disposition follows D-22's RETIRED word even though the requirement's own text ('each is placed by name') reads as satisfied — recorded as a stated tension in the verdict note's §5, not resolved by inventing a third disposition word or silently picking a side."
  - "The measured deleted-line total across firestarter_app (20,194 lines removed, 90 added, net -20,104 across 76 files) and firestarter (1,262 removed, 85 added, net -1,177 across 16 files) exceeds CONTEXT.md's ~16,700 pre-phase estimate. The gap is not an overclaim: CONTEXT's table enumerated the ten gates, six tools, two CI mirrors, one orphan and the frame-vector apparatus (summing to exactly the ~16,700 estimate), but did not separately enumerate D-25's 90 consuming-test deletions across 11 modules, seven planted-violation fixtures, or two orphaned data artifacts (the 1,270-line golden coverage-matrix file and the 828-line plan_shapes.json fixture) — all discovered and measured only during 188-02 through 188-05's own execution, after CONTEXT.md was written."
  - "Both prose amendment sites where '**AMENDED by Phase' initially wrapped across a Markdown line break (breaking the literal-string verify legs for 'relocated into the test tier' non-occurrence and the ROADMAP AMENDED-marker count) were caught by re-running each task's own <verify> legs before moving to the next task, not assumed passing from visual inspection."

requirements-completed: [TOOLS-01, TOOLS-02, TOOLS-03, TOOLS-04, TOOLS-05, TOOLS-06, TOOLS-07]

coverage:
  - id: D1
    description: "Verdict note written naming every retired item (10 gates, 6 process tools, 2 CI mirrors, 1 orphan, the frame-vector apparatus on both sides, the scan-path pair, the mypy CI leg) with its measured line count, all eight disclosed costs, the OD-1-to-D-25 supersession, the deleted CLAUDE.md prose verbatim, and the TOOLS-04 tension"
    requirement: "TOOLS-01"
    verification:
      - kind: unit
        ref: "test -f .planning/notes/host-tools-retirement.md && grep -c '^## VERDICT' -> 1"
        status: pass
      - kind: unit
        ref: "20-item name-presence loop (10 gates + 6 tools + 2 CI mirrors + orphan + codegen_vectors + scan_paths) -> 0 missing"
        status: pass
      - kind: unit
        ref: "grep -Fe for D-25, OD-1, WR-01, BLOCKER-2, 'zero collateral' -> 0 missing"
        status: pass
      - kind: unit
        ref: "grep -c 'relocated into the test tier' over the note and REQUIREMENTS.md -> 0/0"
        status: pass
      - kind: unit
        ref: "grep -c TOOLS-04, grep -ci tension/'arguably satisfied', grep -c TOOLS-05 -> 6/3/4 (all non-zero)"
        status: pass
    human_judgment: false
  - id: D2
    description: "REQUIREMENTS.md's seven TOOLS traceability rows amended per D-22 row for row; only TOOLS-05's checkbox flipped"
    requirement: "TOOLS-02"
    verification:
      - kind: unit
        ref: "per-row disposition-word match against D-22's fixed word for each of the seven rows -> 0 mismatches"
        status: pass
      - kind: unit
        ref: "grep -c '^- \\[x\\] **TOOLS-05**' -> 1; grep -cE '^- \\[x\\] **TOOLS-0(1|2|3|4|6|7)**' -> 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "ROADMAP.md's Phase 188 section amended in place — all seven success criteria and the not-in-scope paragraph carry an AMENDED marker with the conflict quoted; the diff stays confined to the Phase 188 section; the sub-repository list stays at four entries; 188-09's own plan checkbox is checked"
    requirement: "TOOLS-06"
    verification:
      - kind: unit
        ref: "grep -c 'AMENDED by Phase 188' -> 8 (7 criteria + the not-in-scope paragraph)"
        status: pass
      - kind: unit
        ref: "grep -c '188-0[1-9]-PLAN.md' -> 9; grep -c '^- \\[x\\] 188-0[1-9]-PLAN.md' -> 9"
        status: pass
      - kind: unit
        ref: "grep -c firestarter_py32_ci / firestarter_app_py32 in config.json -> 1/1; git diff --stat ROADMAP.md -> 34 insertions(+), 7 deletions(-), both hunks confined to lines 580-651"
        status: pass
    human_judgment: false
  - id: D4
    description: "The three folded planning items settled: the orphaned-host-tools todo moved to completed/ with the judgment-vs-reference-count distinction; the provenance todo's tools-half figure corrected to its measured live zero with the tests-half left open; the gate-expiry seed marked resolved; no backlog item filed"
    requirement: "TOOLS-07"
    verification:
      - kind: unit
        ref: "ls pending/ | grep -c retire-two-orphaned-host-tools -> 0; ls completed/ | grep -c same -> 1"
        status: pass
      - kind: unit
        ref: "ls pending/ | grep -c strip-gsd-provenance -> 1; grep -ci tests <that file> -> 3"
        status: pass
      - kind: unit
        ref: "grep -ci resolved .planning/seeds/phase-gate-expiry-discipline.md -> 4"
        status: pass
      - kind: unit
        ref: "git diff --name-only origin/beta...HEAD -- .planning/backlog .planning/backlog.md -> 0 lines"
        status: pass
      - kind: unit
        ref: "git status --porcelain (post-commit, non-'??' lines) -> 0"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-09-13
status: complete
---

# Phase 188 Plan 09: The Retirement Record Summary

**Wrote the phase's verdict onto the permanent record: one note naming every retired item and all
eight disclosed costs, seven amended requirement rows distinguishing RETIRED from Complete, eight
amended ROADMAP passages with every conflict quoted, and the three folded planning items settled —
with zero successor guards and zero backlog items filed, exactly as D-23 requires.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-09-13
- **Tasks:** 3/3
- **Files modified:** 6 (1 created, 5 modified — one of the five via `git mv` into `completed/`)

## Accomplishments

- **The verdict note** (`.planning/notes/host-tools-retirement.md`, 259 lines) written on the shape of
  `catalog-sync-check-retirement.md`: a `## VERDICT` section before any evidence; one line per retired
  item (all ten `check_*.py` gates, all six GSD-process tools, both CI mirrors, the one orphan, the
  frame-vector apparatus on both sides, the scan-path pair, and the mypy CI leg) with the exact
  line count measured at the commit that deleted it — re-measured directly from git history in this
  plan (`git show <commit>^:<path> | wc -l`), not carried forward from CONTEXT.md's pre-phase estimate.
- **All eight disclosed costs stated as losses, in one place:** the four from the phase decisions
  (D-08's dead wire-byte contract, D-12's carried-forward audit blind spot, D-13's ungugarded
  firmware-rename defect, D-15's judgment-not-evidence retirement of `derive_sdp_partition.py`); the
  two the execution surfaced (`check_dispatch.py`'s own electrical-safety AST invariant, and the
  now-decorative lock-status AST leg); and D-25's own two (WR-01's snapshot-drift coverage dying with
  its regenerator, and the six wire-contract suites' BLOCKER-2 SRAM/VPP invariant losing all coverage).
- **The OD-1-to-D-25 supersession recorded by name:** the operator's verbatim "Delete the consumers" at
  the 188-02 blocking-human gate, the replanning pass's re-measurement (11 modules not 8, 247 tests not
  ~105), the resulting surgical choice, the confirmation that no relocation helper module exists
  anywhere in the tree, the 90-consuming-test/zero-collateral figure kept distinct from the much larger
  gate/tool test-module count, and the one test (`test_chip_test.py`) repaired rather than deleted.
- **The deleted `CLAUDE.md` regression-guard prose quoted verbatim** — the two-sentence paragraph
  naming `tools/check_dispatch.py`'s structural and type-keyed guards, retrieved from `firestarter_app`'s
  own git history (`0f251f0`) since the source is gone and this note is the only place the correction
  can land.
- **The TOOLS-04 disposition tension recorded, not resolved silently:** the requirement's own wording
  ("each is placed by name") reads as satisfied by all six tools' actual placement, but D-22 fixes the
  word RETIRED anyway — because the underlying question is which tools earned a permanent place in the
  shipped package, not whether each was *decided*. The same passage states why TOOLS-05 alone carries
  the checked box in the TOOLS block: it is the one requirement that produced work, not absence.
- **Two further facts recorded that a later reader would otherwise rediscover the hard way:** the
  coverage-matrix checker's last measured behaviour (exit 1, zero bytes on stdout and stderr on either
  failure path) and `tools/baseline/dispatch_baseline.json`'s now-orphaned status, retained because this
  phase decided scripts and not data (D-14).
- **REQUIREMENTS.md's seven traceability rows amended per D-22, row for row:** TOOLS-01, -02, -04, -06
  and -07 now read `RETIRED — <cause> (188-0N)`; TOOLS-03 reads `Satisfied by family retirement — ...`;
  TOOLS-05 reads `Complete — ...`. Only TOOLS-05's checkbox was flipped to `[x]`; the five RETIRED
  requirements' and TOOLS-03's checkboxes stay unchecked, so a decision not to build stays permanently
  distinguishable from a thing that was built.
- **ROADMAP.md's Phase 188 section amended in place, by hand, with the diff confined to two hunks
  inside that section (34 insertions, 7 deletions — well under the 80-line ceiling):** all seven success
  criteria and the not-in-scope paragraph now carry a bolded `**AMENDED by Phase 188 (D-NN):**` marker
  that retains the original text and quotes the conflict — criterion 2's dropped declaration layer
  against its own "no deletion may precede it" text, and the not-in-scope paragraph's judgment-not-
  reference-count deletion of the exact tool it names as protected. Criterion 6's amendment states the
  no-new-CI-gate constraint was honored in a stronger form than asked (deletion of the checked files,
  not merely withholding a new gate). The phase's own nine-plan checklist is now 9/9 checked; no other
  phase's ROADMAP section was touched; `planning.sub_repos` still lists all four sub-repositories.
- **The three folded planning items settled:** the orphaned-host-tools todo moved to `completed/` with
  a `## CLOSED` section stating that the declaration layer it recommended was dropped (D-12) and that
  its two named tools were deleted anyway — on the operator's judgment about value, not the
  reference-count evidence the todo's own correction had already retracted. The provenance-comment
  todo's stale ~296-hit tools-half figure was replaced with the measured live value (0, per 188-07's
  hand sweep and 188-08's catalog-codegen strip, both asserted with a positive control); its tests-half
  (~1,774 hits) stays open, untouched, in the pending directory. The gate-expiry seed was marked
  resolved: there is no gate family left in `firestarter_app/tools/` for an expiry question to govern.
  No backlog item was filed for anything named in this plan or the verdict note.

## Measured phase-level totals (for the milestone audit)

Deleted-line counts, measured directly from git diff against each repository's own pre-phase base
(`firestarter_app`'s base is 188-03's pinned `f3650ff2`; `firestarter`'s is 188-06's pinned `3c3c802c`),
not carried forward from CONTEXT.md's pre-phase estimate:

| Repository | Files changed | Insertions | Deletions | Net |
|---|---:|---:|---:|---:|
| `firestarter_app` | 76 | 90 | 20,194 | **-20,104** |
| `firestarter` | 16 | 85 | 1,262 | **-1,177** |
| **Total** | **92** | **175** | **21,456** | **-21,281** |

CONTEXT.md's pre-phase estimate was **~16,700** deleted lines (the ten gates + their tests + six tools +
their tests + two CI mirrors + the orphan + the frame-vector apparatus on both sides — a table that,
summed, lands exactly on 16,700). The measured total is larger. This is not an overclaim: CONTEXT's table
did not separately enumerate three populations discovered and measured only during execution —
D-25's 90 consuming-test deletions across 11 modules (found at the 188-02 gate, after CONTEXT.md was
written), seven planted-violation fixtures deleted alongside the ten gates, and two orphaned data
artifacts (the 1,270-line golden coverage-matrix file and the 828-line `plan_shapes.json` fixture)
deleted alongside `audit_coverage_matrix.py`. The gap between 16,700 and 21,281 is exactly the size of
those three populations, not a rounding error or an inflated claim.

## Task Commits

Each task was committed atomically, in the meta repo:

1. **Task 1: Write the verdict document** — `f2079605` (docs)
2. **Task 2: Amend the requirement ledger and the seven success criteria, by hand** — `cccfb7aa` (docs)
3. **Task 3: Settle the three folded planning items** — `02bc004c` (docs)

**Plan metadata:** committed alongside this SUMMARY (see completion format for hash).

## Files Created/Modified

- `.planning/notes/host-tools-retirement.md` — created; the verdict note (259 lines).
- `.planning/REQUIREMENTS.md` — seven TOOLS traceability rows amended; TOOLS-05's checkbox flipped.
- `.planning/ROADMAP.md` — Phase 188's seven success criteria, the not-in-scope paragraph, and the
  188-09 plan checkbox amended (scoped hand edits, two hunks, 34+/7-).
- `.planning/todos/completed/2026-09-12-retire-two-orphaned-host-tools.md` — moved from `pending/`,
  with a `## CLOSED` section added.
- `.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md` — tools-half figure
  corrected to the measured live zero; tests-half untouched.
- `.planning/seeds/phase-gate-expiry-discipline.md` — marked resolved.

## Decisions Made

See `key-decisions` in the frontmatter. In summary: TOOLS-04's disposition follows D-22's RETIRED word
despite the requirement's own wording reading as satisfied, recorded as a stated tension rather than
resolved silently; the measured deleted-line total exceeds CONTEXT.md's estimate for reasons this
SUMMARY reconciles rather than rounds away; and two Markdown line-wrap defects in the first drafting
pass (the literal strings "AMENDED by Phase 188" and "zero collateral" each briefly split across a line
break) were caught by re-running each task's own `<verify>` legs before proceeding, not assumed passing.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Two literal-string verify legs initially failed on a self-inflicted Markdown line wrap**
- **Found during:** Task 1 (the `-Fe 'zero collateral'` leg) and Task 2 (the `AMENDED by Phase 188` count
  leg), both while re-running the task's own `<verify>` block before moving on.
- **Issue:** The verdict note's first draft wrapped "zero\ncollateral" across a line break, and two of
  the ROADMAP amendments wrapped "Phase\n188" the same way — both defeat a literal (non-regex,
  whitespace-sensitive) `grep -F`/`grep -c` match even though the prose reads correctly to a human.
- **Fix:** Reflowed the affected sentences so each literal phrase sits on a single line, without changing
  any substantive wording.
- **Files modified:** `.planning/notes/host-tools-retirement.md`, `.planning/ROADMAP.md`.
- **Verification:** Both verify legs re-run clean afterward (0 missing / 8 AMENDED markers respectively).
- **Committed in:** `f2079605` (note), `cccfb7aa` (ROADMAP) — both fixed before their task's commit, so
  no separate correction commit was needed.

---

**Total deviations:** 1 auto-fixed (Rule 1 — a self-inflicted verify-leg failure caught and fixed before
committing, not a defect in prior plans' work).
**Impact on plan:** No scope creep. Both fixes were pure reflows of already-written prose, caught by the
plan's own mandated verify-before-proceeding discipline.

## Issues Encountered

None beyond the deviation documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 188 is fully executed: all nine plans complete, the ledger amended, the ROADMAP amended, the
  three folded planning items settled. This plan does **not** flip the ROADMAP's own Phase 188 checkbox
  or run the phase-complete transition — per this plan's own scope, that is the orchestrator's next
  move, after its own verification.
- `.planning/WINDOWS.md` carries this phase's three deviation entries (6 open — WR-01; 7 fixed — the two
  render_shape prose mentions; 8 open — the decorative lock-status AST leg), all three now also named in
  the verdict note this plan wrote.
- No blockers. `planning.sub_repos` confirmed intact at four entries throughout this plan's execution;
  no `gsd-tools` state-writing verb was run against this phase at any point.

## Self-Check: PASSED

- `FOUND: 188-09-SUMMARY.md` — `.planning/phases/188-the-tools-directory/188-09-SUMMARY.md` exists on disk.
- `FOUND: host-tools-retirement.md` — `.planning/notes/host-tools-retirement.md` exists on disk, 259 lines.
- `git log --oneline --all` finds all three task commits (`f2079605`, `cccfb7aa`, `02bc004c`), all on
  branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene-activated-202`; `git rev-list --count
  dafa8af3..HEAD` (pre-Task-1 base) → 3, matching `actuals.commits`.
- All three tasks' `<verify>` legs re-run clean at final HEAD: the verdict note's five checks, the
  REQUIREMENTS.md disposition/checkbox checks, the ROADMAP AMENDED-count/plan-checkbox/sub-repo/diff-size
  checks, and the three folded-planning-item checks (todo move, provenance figure, seed resolution,
  backlog untouched, working tree clean) all pass as documented above.
- `git status --porcelain` (meta repo) shows only the pre-existing untracked `anything.txt`, `tmp/`, and
  the `firestarter_app` gitlink's dirty-by-untracked-datasheets state (confirmed via `git diff --
  firestarter_app` → empty, and `git ls-tree HEAD firestarter_app` matching the submodule's own `HEAD`
  exactly) — no tracked file left uncommitted.

---
*Phase: 188-the-tools-directory*
*Completed: 2026-09-13*
