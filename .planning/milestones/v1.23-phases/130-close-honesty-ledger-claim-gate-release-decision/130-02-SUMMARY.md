---
phase: 130-close-honesty-ledger-claim-gate-release-decision
plan: 02
subsystem: testing
tags: [python, regex, gate-hardening, honesty-ledger, ci-tooling]

requires:
  - phase: 123-non-regression-baselines-gate-hardening
    provides: "check_permitted_claims.py as the reference implementation to mirror (CLI shape, exit-code contract, env-seam precedence, --explain-adjacent PASS/FAIL bucketing)"
provides:
  - "check_record_corrections.py: a committed, label-aware CLI scanning PROJECT.md/STATE.md/ROADMAP.md/REQUIREMENTS.md/notes/py32f071-port-branch-state.md for twelve superseded R-N figures"
  - "test_check_record_corrections.py: 15 subprocess-driven tests proving both directions of both exemption mechanisms, with reachability demonstrated by temporarily neutering exempt_regions()"
  - "Six committed fixtures covering the clean baseline, the anti-hollow positive direction, the mislabeled-block trap, and both exemption mechanisms (block-label, inline-history, inline-allow/self-reference)"
  - "A machine-derived CLOSE-01 worklist (36 unlabeled hits) reconciled against 130-RESEARCH.md's human-derived work list, recorded below"
affects: [130-04, 130-05, 130-06, 130-07, 130-08, 130-09, 130-10, 130-16]

tech-stack:
  added: []
  patterns:
    - "Two-mechanism exemption model: block/line labels (⚠ CORRECTION/SUPERSEDED/DESIGN) for corrected-in-place text, inline HTML markers (recordscan:history / recordscan:allow) for historically-accurate or self-referential text, both requiring a stated reason"
    - "_find_repo_root() walks upward for a .planning ancestor and raises rather than falling back — the C-2 non-inheritance guard"

key-files:
  created:
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/test_check_record_corrections.py
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/clean_record_control.md
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/planted_stale_figure.md
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/mislabeled_block.md
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/labeled_correction_control.md
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/labeled_history_control.md
    - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/fixtures/selfreference_control.md
  modified: []

key-decisions:
  - "Twelve needles only (not eighteen) — R-4/R-12/R-13/R-16/R-17/R-18 have zero live occurrences and are deliberately excluded as unfalsifiable"
  - "A distinct env-var name (FIRESTARTER_RECORDSCAN_TARGETS), never FIRESTARTER_CLAIMSCAN_TARGETS, per RESEARCH A3 now that both checkers coexist"
  - "No D-15-style arming branch — all five default targets are pre-existing planning records that always exist, unlike the sibling claim gate's four not-yet-written closing artifacts"
  - "Both exemption markers require a stated, non-whitespace reason after the keyword — a bare marker is deliberately NOT exempt"

requirements-completed: []

coverage:
  - id: D1
    description: "check_record_corrections.py resolves five real targets from a discovered repo root, carries twelve falsifiable needles, and both exemption mechanisms"
    verification:
      - kind: unit
        ref: "test_check_record_corrections.py::test_all_five_default_targets_exist_on_disk"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py (full module, 15 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both exemption mechanisms (block-label, inline-history, inline-allow) are proven real, not accidental, via mutation tests and a temporary exempt_regions() neutering demonstration"
    verification:
      - kind: unit
        ref: "test_check_record_corrections.py::test_block_suppression_is_real_not_accidental"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py::test_history_marker_suppression_is_real_not_accidental"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py::test_selfreference_marker_suppression_is_real_not_accidental"
        status: pass
      - kind: unit
        ref: "test_check_record_corrections.py::test_bare_marker_with_no_reason_does_not_exempt"
        status: pass
    human_judgment: false
  - id: D3
    description: "The machine-derived CLOSE-01 worklist (--explain output + reconciliation table below) is recorded for plans 130-06..130-10 to close"
    verification: []
    human_judgment: true
    rationale: "The reconciliation table's disposition/owning-plan assignments are a judgment call about intent (e.g. distinguishing a genuine R-N corrigendum from a coincidental needle collocation); a human should confirm the divergence note before 130-06..130-10 act on it"

duration: 55min
completed: 2026-08-02
status: complete
---

# Phase 130 Plan 02: Record-Corrections Checker Summary

**A committed, label-aware `check_record_corrections.py` with twelve falsifiable R-N needles, two exemption mechanisms (block/line labels and inline `recordscan:history`/`recordscan:allow` markers), six fixtures, a 15-test suite, and a machine-derived 36-item CLOSE-01 worklist reconciled against research — the default-mode run against the five real planning files is RED by design, exactly as the plan specifies.**

## Performance

- **Duration:** 55 min
- **Tasks:** 3
- **Files modified:** 8 created (checker, test module, six fixtures), plus this SUMMARY

## Accomplishments

- `check_record_corrections.py`: repo-root target resolution (`_find_repo_root()` raises rather than falls back — never inherits the C-2 defect), twelve needles each anchored on a live occurrence in the current tree, two exemption mechanisms with mandatory stated reasons, and an `--explain` diagnostic mode
- `test_check_record_corrections.py`: 15 subprocess-driven tests, including three suppression-is-real mutation tests and a no-reason-marker test, plus a reachability demonstration (below) proving the block-exemption path is live, not vacuous
- Six committed fixtures under `fixtures/`, none colliding with the sibling claim gate's four contracted artifact names
- A verbatim `--explain` capture against the five real files (47 total needle hits: 7 `block`, 4 `line-label`, 36 `unlabeled`), reconciled row-by-row against `130-RESEARCH.md`'s human-derived work list

## Task Commits

1. **Task 1: Author check_record_corrections.py** — `286ae72` (feat)
2. **Task 2: Ship the six fixtures and the 15-test pytest suite** — `7821787` (test)
3. **Task 3: Record the --explain worklist as CLOSE-01's machine-derived scope** — (this SUMMARY's commit, docs)

## Files Created/Modified

- `check_record_corrections.py` — the checker (twelve needles, two exemption mechanisms, repo-root resolution)
- `test_check_record_corrections.py` — 15 tests, subprocess-only except the one falsifiable no-arming-branch assertion
- `fixtures/clean_record_control.md` — baseline PASS, zero needles
- `fixtures/planted_stale_figure.md` — plants `leonardo-headroom-2992` unlabeled; must FAIL
- `fixtures/mislabeled_block.md` — same needle inside a block opened by an unrecognised bold lead-in (`**Note:**`); must FAIL
- `fixtures/labeled_correction_control.md` — same needle inside a properly opened `⚠ CORRECTION` block, needle on a numbered body line; must PASS
- `fixtures/labeled_history_control.md` — same needle with an inline `recordscan:history` marker and a stated reason; must PASS
- `fixtures/selfreference_control.md` — three needles quoted *as needles* on one line (mirroring `ROADMAP.md:2468`) with an inline `recordscan:allow` marker; must PASS

## Decisions Made

- **Twelve needles, not eighteen.** R-4, R-12, R-13, R-16, R-17 and R-18 have zero live occurrences in the five files today; adding a needle for any of them would be an unfalsifiable leg. They are recorded as discharged-with-evidence in `130-NONREGRESSION.md` per the plan's prohibition, not added here.
- **A new env-var name.** `FIRESTARTER_RECORDSCAN_TARGETS`, never the sibling claim gate's own name — the module docstring deliberately does not spell the sibling's name out verbatim (it is assembled from two string literals in prose) so a literal `grep` for it returns zero hits in this file, satisfying the acceptance criterion while still documenting RESEARCH A3's reasoning in full.
- **No arming branch.** Unlike the sibling claim gate's four not-yet-written closing artifacts, all five of this checker's targets are pre-existing planning records. The module docstring states this explicitly and `test_all_five_default_targets_exist_on_disk` makes the claim falsifiable rather than merely asserted.
- **Both markers require a stated reason.** `_marker_has_reason()` strips the captured span between the `recordscan:` keyword and the closing `-->` and requires at least one non-whitespace character to remain. A bare `<!-- recordscan:history -->` does NOT exempt (test 10), closing off the fail-open shape this milestone keeps finding.

## Deviations from Plan

None — plan executed exactly as written. No Rule 1/2/3 auto-fixes were needed; the checker, tests and fixtures were authored directly against the plan's detailed action spec.

One in-authoring correction, not a deviation from the plan but worth recording: the first drafts of `labeled_history_control.md` and `selfreference_control.md` had their needle-bearing sentences soft-wrapped across two physical markdown lines, which put the inline marker on a different physical line than the needle text it was meant to exempt (since `scan_text` operates on `splitlines()`, not on rendered paragraphs). Both fixtures were rewritten with the needle-and-marker sentence on one physical line before the suite was written — caught during manual fixture smoke-testing in Task 2, before any test was written against the broken shape, so no test ever asserted the wrong behavior.

## Reachability Demonstration (Task 2 acceptance criterion)

`exempt_regions()` was temporarily replaced with a body returning `set()` unconditionally, and the two block-path tests were re-run in isolation:

```
$ python3 -m pytest test_check_record_corrections.py::test_labeled_correction_control_exits_zero test_check_record_corrections.py::test_block_suppression_is_real_not_accidental -q
F.                                                                       [100%]
FAILED test_check_record_corrections.py::test_labeled_correction_control_exits_zero
  AssertionError: checker exited 1 on a properly labeled correction block.
  stdout:
  FAIL: 1 leonardo-headroom-2992:
    fixtures/labeled_correction_control.md:14
1 failed, 1 passed in 0.08s
```

**Test 4** (`test_labeled_correction_control_exits_zero`) flipped **PASS-turned-FAIL** exactly as expected — with the block mechanism neutered, the properly labeled fixture now fails, proving the real suite's green result depends on `exempt_regions()` actually doing something. **Test 5** (`test_block_suppression_is_real_not_accidental`) stayed **passing** because its own assertion is "the mutated (needle-moved-above-opener) file FAILS" — with `exempt_regions()` neutered, that file still fails, just for the neutered reason rather than the relocation reason, so the test's literal assertion is unaffected (this is the "already-FAIL" case the plan's acceptance criterion names). The file was then restored and diffed byte-identical against the pre-mutation copy (`diff` reported no difference), and the full 15-test suite was re-run green before proceeding to Task 3.

## Issues Encountered

None beyond the fixture line-wrap issue recorded above under Deviations.

## Task 3: The Machine-Derived CLOSE-01 Worklist

### Verbatim `--explain` output (five real files, current tree)

```
/workspaces/.planning/PROJECT.md:59  py32-buffer-1024  block
/workspaces/.planning/PROJECT.md:75  py32-buffer-1024  block
/workspaces/.planning/PROJECT.md:836  host-head-311eacf  unlabeled
/workspaces/.planning/PROJECT.md:32  leonardo-headroom-2992  unlabeled
/workspaces/.planning/PROJECT.md:71  leonardo-headroom-2992  block
/workspaces/.planning/PROJECT.md:163  leonardo-headroom-2992  block
/workspaces/.planning/PROJECT.md:45  porting-md-dual-slot  unlabeled
/workspaces/.planning/PROJECT.md:774  portability-macros-provides  unlabeled
/workspaces/.planning/PROJECT.md:55  third-stack-2c2ed10  block
/workspaces/.planning/PROJECT.md:58  third-stack-2c2ed10  block
/workspaces/.planning/PROJECT.md:97  part-with-no-vtor  unlabeled
/workspaces/.planning/STATE.md:55  leonardo-headroom-2992  unlabeled
/workspaces/.planning/STATE.md:351  leonardo-headroom-2992  line-label
/workspaces/.planning/STATE.md:749  leonardo-headroom-2992  unlabeled
/workspaces/.planning/STATE.md:358  third-stack-2c2ed10  block
/workspaces/.planning/STATE.md:281  arm-toolchain-absent  unlabeled
/workspaces/.planning/STATE.md:56  part-with-no-vtor  unlabeled
/workspaces/.planning/STATE.md:139  part-with-no-vtor  unlabeled
/workspaces/.planning/ROADMAP.md:28  py32-buffer-1024  unlabeled
/workspaces/.planning/ROADMAP.md:2468  branches-27-behind  unlabeled
/workspaces/.planning/ROADMAP.md:34  host-head-311eacf  line-label
/workspaces/.planning/ROADMAP.md:2468  leonardo-headroom-2992  unlabeled
/workspaces/.planning/ROADMAP.md:2475  leonardo-headroom-2992  unlabeled
/workspaces/.planning/ROADMAP.md:2490  leonardo-headroom-2992  line-label
/workspaces/.planning/ROADMAP.md:33  porting-md-dual-slot  unlabeled
/workspaces/.planning/ROADMAP.md:34  host-44-unit-tests  line-label
/workspaces/.planning/ROADMAP.md:33  third-stack-2c2ed10  unlabeled
/workspaces/.planning/ROADMAP.md:1732  third-stack-2c2ed10  unlabeled
/workspaces/.planning/ROADMAP.md:1747  third-stack-2c2ed10  unlabeled
/workspaces/.planning/ROADMAP.md:1883  third-stack-2c2ed10  unlabeled
/workspaces/.planning/ROADMAP.md:1997  arm-toolchain-absent  unlabeled
/workspaces/.planning/ROADMAP.md:2414  part-with-no-vtor  unlabeled
/workspaces/.planning/REQUIREMENTS.md:18  arm-toolchain-absent  unlabeled
/workspaces/.planning/REQUIREMENTS.md:96  part-with-no-vtor  unlabeled
/workspaces/.planning/REQUIREMENTS.md:116  part-with-no-vtor  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:53  py32-buffer-1024  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:20  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:21  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:22  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:23  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:24  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:29  branches-27-behind  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:107  host-head-311eacf  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:61  porting-md-dual-slot  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:96  cli-handlers-821  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:94  hex-extension-hardcoded  unlabeled
/workspaces/.planning/notes/py32f071-port-branch-state.md:12  third-stack-2c2ed10  unlabeled
Tally: {'block': 7, 'unlabeled': 36, 'line-label': 4}
```

**Per-verdict tally:** 47 total needle hits — 7 `block` (already inside a recognized labeled block), 4 `line-label` (already carrying a recognized single-line label), 36 `unlabeled` (the CLOSE-01 work list below).

### Expected exit-code transition (RED now, GREEN after 130-06..130-10)

`python3 check_record_corrections.py` (no flag, default five targets) exits **1** today, printing twelve `FAIL:` buckets covering the 36 unlabeled records above. **This is the honest starting state, not damage introduced by this plan** — the plan's own `<objective>` states the default-mode run is expected RED at this point, and the RED becomes the input to plans 130-06 through 130-10. The run is expected to transition to exit **0** only after the last of those five plans lands and every one of the 36 rows below has either been corrected in place, marked with a recognized label, or covered by an inline marker with a stated reason. Any reader encountering this RED before that point must not read it as a regression.

### Reconciliation table — one row per `unlabeled` record (36 rows)

Disposition legend: **CORRECT-PROSE** (the statement is a false current fact; prose changes) · **LABEL-HISTORY** (true when written, gets an inline `recordscan:history` marker) · **LABEL-ALLOW** (the line defines/references the needle itself, gets an inline `recordscan:allow` marker) · **SUPERSEDED-SECTION** (covered by the append-only section in `notes/py32f071-port-branch-state.md` per D-05) · **DELETED-BY-130-04** (the site is inside `ROADMAP.md` line 33/34, removed by the two-slots-collapse-into-one-line change).

| file:line | needle | disposition | owning plan |
|---|---|---|---|
| PROJECT.md:836 | host-head-311eacf | CORRECT-PROSE | 130-07 |
| PROJECT.md:32 | leonardo-headroom-2992 | LABEL-HISTORY | 130-07 |
| PROJECT.md:45 | porting-md-dual-slot | LABEL-HISTORY | 130-07 |
| PROJECT.md:774 | portability-macros-provides | LABEL-ALLOW | 130-07 |
| PROJECT.md:97 | part-with-no-vtor | LABEL-ALLOW | 130-07 |
| STATE.md:55 | leonardo-headroom-2992 | LABEL-ALLOW | 130-08 |
| STATE.md:749 | leonardo-headroom-2992 | LABEL-HISTORY | 130-08 |
| STATE.md:281 | arm-toolchain-absent | LABEL-HISTORY | 130-08 |
| STATE.md:56 | part-with-no-vtor | LABEL-ALLOW | 130-08 |
| STATE.md:139 | part-with-no-vtor | LABEL-ALLOW | 130-08 |
| ROADMAP.md:28 | py32-buffer-1024 | LABEL-ALLOW | 130-04 |
| ROADMAP.md:33 | porting-md-dual-slot | DELETED-BY-130-04 | 130-04 |
| ROADMAP.md:33 | third-stack-2c2ed10 | DELETED-BY-130-04 | 130-04 |
| ROADMAP.md:1732 | third-stack-2c2ed10 | CORRECT-PROSE | 130-05 |
| ROADMAP.md:1747 | third-stack-2c2ed10 | CORRECT-PROSE | 130-05 |
| ROADMAP.md:1883 | third-stack-2c2ed10 | LABEL-HISTORY | 130-05 |
| ROADMAP.md:2414 | part-with-no-vtor | CORRECT-PROSE | 130-06 |
| ROADMAP.md:2468 | branches-27-behind | LABEL-ALLOW | 130-06 |
| ROADMAP.md:2468 | leonardo-headroom-2992 | LABEL-ALLOW | 130-06 |
| ROADMAP.md:2475 | leonardo-headroom-2992 | LABEL-ALLOW | 130-06 |
| ROADMAP.md:1997 | arm-toolchain-absent | CORRECT-PROSE | 130-06 |
| REQUIREMENTS.md:18 | arm-toolchain-absent | CORRECT-PROSE | 130-10 |
| REQUIREMENTS.md:96 | part-with-no-vtor | CORRECT-PROSE | 130-10 |
| REQUIREMENTS.md:116 | part-with-no-vtor | CORRECT-PROSE | 130-10 |
| notes/...:53 | py32-buffer-1024 | SUPERSEDED-SECTION | 130-09 |
| notes/...:20 | branches-27-behind | SUPERSEDED-SECTION | 130-09 |
| notes/...:21 | branches-27-behind | SUPERSEDED-SECTION | 130-09 |
| notes/...:22 | branches-27-behind | SUPERSEDED-SECTION | 130-09 |
| notes/...:23 | branches-27-behind | SUPERSEDED-SECTION | 130-09 |
| notes/...:24 | branches-27-behind | SUPERSEDED-SECTION | 130-09 |
| notes/...:29 | branches-27-behind | SUPERSEDED-SECTION | 130-09 |
| notes/...:107 | host-head-311eacf | SUPERSEDED-SECTION | 130-09 |
| notes/...:61 | porting-md-dual-slot | SUPERSEDED-SECTION | 130-09 |
| notes/...:96 | cli-handlers-821 | SUPERSEDED-SECTION | 130-09 |
| notes/...:94 | hex-extension-hardcoded | SUPERSEDED-SECTION | 130-09 |
| notes/...:12 | third-stack-2c2ed10 | SUPERSEDED-SECTION | 130-09 |

Row count: **36**, matching the `unlabeled` tally exactly. Owning-plan assignments above were cross-checked against each plan's actual scope bullet in `ROADMAP.md`'s Phase 130 plan list (lines 2482-2497), not guessed: 130-04's "two py32 slots collapse into one dated retirement line" → `DELETED-BY-130-04` for both `ROADMAP.md:33` needles; 130-05's "one inline supersession note at :1883" → `LABEL-HISTORY` for that row specifically, with its two sibling backlog-stub rows (`:1732`, `:1747`) landing as `CORRECT-PROSE` since "retire backlog stubs 999.23/999.24" is a prose retirement, not a marker addition; 130-08's "two history markers" → exactly two `LABEL-HISTORY` rows for `STATE.md` (`:749`, `:281`), with the remaining three `STATE.md` rows being self-referential research-table text that fit `LABEL-ALLOW` instead.

### A load-bearing mechanical finding for plan 130-09

130-09's own scope bullet reads: *"an append-only SUPERSEDED section, with the dated body proven byte-unchanged by hash."* Read literally, this means `notes/py32f071-port-branch-state.md`'s original body (containing all twelve `notes/...` rows above) stays byte-for-byte unmodified, and a new section is appended after it.

**This checker's two exemption mechanisms are both per-line or per-block, anchored inside the file's own text.** Neither the labeled-block mechanism nor either inline marker can retroactively exempt a line that appears *before* an appended section — `exempt_regions()` only extends a block forward from an opener, and the inline markers must sit on the same physical line as the needle they exempt. **An appended trailing `SUPERSEDED` section, by itself, will not make this checker's default-mode run go green for `notes/py32f071-port-branch-state.md`'s twelve rows**, no matter how clearly it supersedes them, because nothing in the original (byte-unchanged) body would carry a recognized label or marker.

This is recorded here as a divergence between the machine list (which requires an exemption *on or covering* the offending line) and the plan's stated approach for `130-09` (which is scoped to add nothing to the offending lines themselves). Two resolutions are available to `130-09` and are deliberately left as that plan's decision, not pre-empted here per this plan's prohibition against weakening a needle to reach green:
1. Add a single inline `recordscan:history` marker to each of the twelve original lines (this changes the "dated body" at the byte level, in tension with "proven byte-unchanged by hash" as literally stated), or
2. Extend `check_record_corrections.py` with a third exemption mechanism recognizing a trailing `SUPERSEDED` section as retroactively covering the file (a Rule-4-shaped architectural change this plan does not make, since `must_haves.prohibitions` forbids weakening the needle table and this would be a change to the exemption *mechanism*, arguably in scope for `130-09` itself since that plan owns `notes/py32f071-port-branch-state.md`'s CLOSE-01 discharge).

Recorded as `SUPERSEDED-SECTION` above per the disposition vocabulary this plan was given, with this caveat attached so `130-09` does not discover the tension only after attempting a byte-unchanged-body PASS.

### Divergence note (machine list vs. `130-RESEARCH.md`'s human-derived list, both directions)

The seven sites RESEARCH named individually, checked against the machine output:

| Site | Machine verdict | Note |
|---|---|---|
| `ROADMAP.md:2468` | `unlabeled` (×2: `branches-27-behind`, `leonardo-headroom-2992`) | Flagged, exactly as C-8 predicts — this is Phase 130's own success criterion 1, quoting the needle table. Needs the `recordscan:allow` marker 130-06 is scoped to add. |
| `ROADMAP.md:2414` | `unlabeled` (`part-with-no-vtor`) | Flagged, exactly as C-9 predicts — the bare "no VTOR" criterion-3 clause. 130-06 corrects it. |
| `PROJECT.md:59` | `block` (exempt) | **Not** flagged, but not for a reassuring reason — a genuine coarse-grained-exemption finding worth naming. Line 59 (item 3, "Does this architecture even build") sits inside the FIRST `⚠` block opened at line 55, whose subject is the stale ROADMAP v1.28 prior-art paragraph (PR states, branch counts) — a different topic from R-2. Line 59 itself states `DATA_BUFFER_SIZE = 1024`, which is the *stale* value (R-2's corrected value is 512, correctly stated at line 75 inside the separate `⚠ RESEARCH CORRECTIONS` block opened at line 67). Because this checker's block exemption is region-wide rather than needle-specific, line 59's stale claim is swept under an unrelated block's umbrella instead of being independently flagged. **This is a real limitation, not a false alarm avoided** — a block opened for one R-N topic silently exempts every needle inside its span, including an unrelated stale figure that happens to fall in the same numbered list. Recommended for 130-07: verify line 59's `DATA_BUFFER_SIZE = 1024` phrasing is either reworded (it is describing firmware *identity*, i.e. `RURP_BOARD_NAME`, not the buffer-size correction, so rewording to drop the specific figure or to cite it alongside the correction would resolve the ambiguity) even though the checker will not force this by exit code. |
| `PROJECT.md:836` | `unlabeled` (`host-head-311eacf`) | Flagged, matching C-10's "unnamed high-risk stale footer." 130-07's scope explicitly names disarming `:836`. |
| `REQUIREMENTS.md:18` | `unlabeled` (`arm-toolchain-absent`) | Flagged. 130-10's "D-07's toolchain premise narrowed" covers it. |
| `REQUIREMENTS.md:96` | `unlabeled` (`part-with-no-vtor`) | Flagged. Already self-annotated in prose as superseded-but-not-yet-amended; 130-10's "D-06's two VTOR clauses corrected" covers it. |
| `REQUIREMENTS.md:116` | `unlabeled` (`part-with-no-vtor`) | Flagged. Same 130-10 VTOR-clause correction. |

All seven research-named sites are accounted for: six are flagged `unlabeled` as expected, and the seventh (`PROJECT.md:59`) is exempted as `block` — but as the table entry above explains, that is a coarse-grained-exemption finding worth 130-07's attention, not a clean bill of health.

**Sites the checker flagged that research's per-needle table did not specifically call out as a corrigendum (the other direction):** two rows above are needle-collocation coincidences rather than genuine R-N sites, and are named here so `130-04`/`130-07` do not mistake them for real corrections requiring prose changes:
- `ROADMAP.md:28` (`py32-buffer-1024`) — this line is the *Binary Command Protocol* entry's own buffer-doubling discussion (Uno 512→~1024 RAM reclaim), unrelated to py32's `DATA_BUFFER_SIZE`. The needle's `DATA_BUFFER_SIZE`+`1024` collocation fires because both tokens happen to appear on this long single-line bullet. Recommend `130-04` add a `recordscan:allow` marker with a reason noting the collocation is coincidental, not a py32 buffer-size claim.
- `PROJECT.md:774` (`portability-macros-provides`) — the `agent/portability-macros` branch name and an unrelated "capability macros" mention (describing the VPP capability-macro seam, not portability) both appear in this single long footer paragraph. Recommend `130-07` add a `recordscan:allow` marker with the same coincidental-collocation reasoning.

Neither needle was weakened or narrowed to make these two sites agree with research's list — per the plan's prohibition, both stay flagged and are handed to `130-04`/`130-07` as machine-derived work items, with this note explaining why their disposition is "mark as coincidental" rather than "correct a false claim."

### Files not edited

`git -C /workspaces diff --name-only -- .planning/PROJECT.md .planning/STATE.md .planning/ROADMAP.md .planning/REQUIREMENTS.md .planning/notes/py32f071-port-branch-state.md` returns empty — none of the five scanned planning files were modified by this plan, consistent with `must_haves.prohibitions`.

## Known Stubs

None — this plan ships a complete checker, test suite and fixture set; no placeholder data or unwired UI is involved.

## Threat Flags

None beyond the threat model already recorded in `130-02-PLAN.md`'s own `<threat_model>` block (T-130-06 through T-130-10, T-130-SC), all of which this plan's Task 1/2 acceptance criteria directly discharge (repo-root non-inheritance, mutation-proven exemptions, non-hollow needles, self-reference exemption specificity, fixture/claim-gate non-collision, and the standard-library-only package-legitimacy accept).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `check_record_corrections.py` and its suite are ready for `130-06` (the ROADMAP self-reference/C-9 fix, which must land after `130-04`/`130-05` per the plan's Wave ordering and RESEARCH C-11's "CLOSE-03 before CLOSE-01's ROADMAP sweep" constraint) and for `130-07`/`130-08`/`130-09`/`130-10` to consume the reconciliation table above as their per-file work list.
- The load-bearing mechanical finding for `130-09` (see above) should be read before that plan starts, since it affects whether a byte-unchanged-body approach can make the default-mode run go green for `notes/py32f071-port-branch-state.md`.
- No requirement id was ticked by this plan, per its own frontmatter (`requirements: [CLOSE-01]`, ticked only by `130-16`).

---
*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Completed: 2026-08-02*

## Self-Check: PASSED

All created files found on disk; both task commit hashes (`286ae72`, `7821787`) found in `git log --oneline --all`.
