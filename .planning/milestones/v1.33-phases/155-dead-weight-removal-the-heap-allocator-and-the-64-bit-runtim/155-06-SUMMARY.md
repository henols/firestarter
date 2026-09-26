---
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "06"
subsystem: firmware-size-landing
tags: [avr-nm, avr-libc, platformio, size-baseline, phase-record, dead-code-elimination, git-worktree]

requires:
  - phase: "155-01"
    provides: "the authoritative before-figures record every after-figure is measured against"
  - phase: "155-02"
    provides: "scripts/check_no_heap_or_64bit_symbols.py, the link-time gate this plan proves from both directions"
  - phase: "155-03"
    provides: ".planning/v1.33/tools/check_dead05_phrasing.py, the phrasing gate this plan runs over the finished corpus"
  - phase: "155-04"
    provides: "the 32-bit voltage reformulation and its committed oracle"
  - phase: "155-05"
    provides: "the heap removal, closing the phase's source changes"
provides:
  - ".planning/v1.33/155-after-figures.md -- the phase's landing record: after-figures vs before, both gate directions, all eight phase-gate legs, five public corrections"
  - "firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/ -- the real post-change clean control replacing the synthetic derived one"
  - "test_real_postchange_listing_exits_zero in tests/test_check_no_heap_or_64bit_symbols.py"
  - "DEAD-01 through DEAD-06 closed in REQUIREMENTS.md against evidence that ran green this session"
affects: ["156", "157", "158", "159"]

tech-stack:
  added: []
  patterns:
    - "Throwaway git worktree for a post-change planted negative: create off FW_POST_SHA under session scratch, reinstate one allocation, build, run the gate with --build-root against the worktree's own .pio/build, then worktree remove --force + prune -- never a branch, never a commit inside it"
    - "A naive unused-malloc+immediate-free planted negative can be silently elided by the compiler; the negative must mirror the pre-change shape (store through the pointer, read it back later) so the pair has an observable effect the compiler cannot prove away"

key-files:
  created:
    - firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/README.md
    - firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt
    - .planning/v1.33/155-after-figures.md
  modified:
    - firestarter/tests/test_check_no_heap_or_64bit_symbols.py
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "The planted post-change negative was built in a throwaway worktree, not the tracked tree. First attempt (malloc + immediate free of an unread pointer) was silently eliminated by the compiler -- avr-nm showed zero allocator symbols even with the malloc/free calls present in source, and flash/RAM were unchanged from the clean post-change figures. Corrected to mirror the pre-change shape exactly (store handle->address through the allocated pointer, read it back in the else branch, then free), which the compiler cannot prove has no observable effect -- confirmed by flash growing 24660->25292 and RAM 1567->1575 before the gate was even run, then the gate itself reporting FAIL naming malloc and free plus all five allocator globals."
  - "The canonical --policy merge05 invocation (Usage: block) omits --native-log flags in its own docstring example, but REQUIREMENTS LAND-03 and the RESEARCH pitfall both describe it failing on a native case-count mismatch -- which requires native logs to be supplied to reproduce. Ran it WITH --native-log flags (matching the historical canonical form used at Phases 144/149/151/153) to reproduce the documented pre-existing red (native: cases baseline=141 observed=172, exit before flash is ever reported) rather than accept a misleading exit-0 result from the docstring's literal, native-log-less example."
  - "One transcription error in a predecessor SUMMARY was caught and corrected rather than propagated: plan 04's SUMMARY quoted the full-bandgap-range bit-identity eval count as 1,046,529; re-running the oracle's own model this session gives 1,047,552 (1023 x 1024), which is what range(1, 1024) x range(0, 1024) actually produces. The corrected figure is recorded in 155-after-figures.md section 9, with the discrepancy stated rather than silently substituted."
  - "REQUIREMENTS.md and ROADMAP.md were hand-edited in place (per house convention -- the GSD requirements/roadmap verbs reformat the whole file) rather than regenerated, ticking DEAD-01..DEAD-06 and correcting the -1364 B header to -1366 B with pointers into 155-after-figures.md for each of the five corrections."

requirements-completed: [DEAD-01, DEAD-02, DEAD-03, DEAD-04, DEAD-05, DEAD-06]

coverage:
  - id: D1
    description: "Real post-change clean control committed (tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/), replacing the synthetic derived control, with its own exit-zero pytest leg"
    requirement: "DEAD-01"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_check_no_heap_or_64bit_symbols.py::test_real_postchange_listing_exits_zero"
        status: pass
      - kind: other
        ref: "python3 scripts/check_no_heap_or_64bit_symbols.py --nm-output uno=tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt -- exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "Gate proven RED from the post-change direction: a throwaway worktree off FW_POST_SHA with one allocation call reinstated, built, and run against the gate with --build-root -- exit 1, naming malloc and free plus the five allocator globals -- then the worktree fully removed and pruned"
    requirement: "DEAD-01"
    verification:
      - kind: other
        ref: "manual: git worktree add off adf1a31's parent 98e70af, patched src/proms/memory.cpp, pio run -e uno, python3 scripts/check_no_heap_or_64bit_symbols.py --build-root <worktree>/.pio/build --baseline <uno-only baseline> -- exit 1, FAIL naming malloc/free/5 globals; git worktree remove --force + prune; git worktree list shows only the pre-existing tree"
        status: pass
    human_judgment: false
  - id: D3
    description: "All eight phase-gate legs run and recorded with their measured figures: both native suites 172/172-17, host pytest 348 passed, both symbol-gate halves 0 on all three ELFs, flash/RAM delta -1366/-8 on all three targets, the size-baseline policy comparison recorded as one-sided with the baseline byte-unchanged, the build-warnings gate clean on a genuine recompile"
    requirement: "DEAD-01, DEAD-03, DEAD-04, DEAD-06"
    verification:
      - kind: other
        ref: "pio test -e native (172/172,17); pio test -e native_nodevtools (172/172,17); python3 -m pytest tests/ -q (348 passed); python3 scripts/check_no_heap_or_64bit_symbols.py (PASS, all three ELFs); pio run -e {uno,uno328pb,leonardo}; python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json (PASS, one-sided); python3 scripts/check_build_warnings.py --log uno=<clean rebuild log> (PASS, macro_redefinition=0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The phase record (155-after-figures.md) written, carrying the five public corrections (OQ-1 2B delta, OQ-2 both 64-bit totals, OQ-3 asymmetric window, OQ-4 corrected RAM derivation, C-5 same-statement correction) plus the SUMMARY-class DEAD-05 correction already applied at b73679aa, and the DEAD-05 phrasing gate run clean over the real corpus"
    requirement: "DEAD-05"
    verification:
      - kind: other
        ref: "python3 .planning/v1.33/tools/check_dead05_phrasing.py (run from /workspaces) -- exit 0, 21 files scanned, 75 in-scope paragraphs (floor 6 cleared), all four required-positive targets confirmed"
        status: pass
    human_judgment: false
  - id: D5
    description: "REQUIREMENTS.md DEAD-01 through DEAD-06 ticked, each with the corrected figure and a pointer to 155-after-figures.md; ROADMAP.md's Phase 155 header and success criteria corrected in place, plan 06 checkbox ticked"
    verification:
      - kind: other
        ref: "manual diff of .planning/REQUIREMENTS.md and .planning/ROADMAP.md against pre-edit content"
        status: pass
    human_judgment: false

duration: ~2h
completed: 2026-08-23
status: complete
---

# Phase 155 Plan 06: Landing -- After-Figures, Both Gate Directions, Eight Legs, Five Corrections Summary

**Measured the after position at -1366 B flash / -8 B RAM on all three AVR targets against the committed before-figures record, proved the symbol gate from both directions (a real post-change clean control plus a throwaway-worktree planted negative), ran all eight phase-gate legs, and wrote the phase record correcting five figures the ROADMAP and REQUIREMENTS got wrong.**

## Performance

- **Duration:** ~2h
- **Completed:** 2026-08-23
- **Tasks:** 3/3 completed
- **Files modified:** 6 (3 created, 3 modified)

## Accomplishments

- Re-measured all three AVR targets warm this session: `uno` 24660/1567, `uno328pb` 24708/1573, `leonardo` 26804/2008 -- exactly matching plans 04+05's combined result, independently reproduced rather than transcribed. Confirmed the per-target delta against `155-before-figures.md` is exactly **-1366 B flash / -8 B RAM** on all three targets.
- Committed the REAL post-change `uno` `avr-nm` listing (`tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/`), replacing the synthetic derived clean control the paired pytest had used since plan 02, and added `test_real_postchange_listing_exits_zero` asserting exit 0 against it.
- Proved the symbol gate RED from the post-change direction for the first time: created a throwaway `git worktree` off `FW_POST_SHA`, reinstated exactly one allocation call in `mem_util_blank_check` (mirroring the pre-change shape closely enough that the compiler could not elide it -- a naive attempt WAS silently eliminated by the compiler on the first try), built `uno` inside the worktree (flash relinked to 25292, RAM to 1575), ran the gate against that build root with `--build-root`, got exit 1 naming `malloc`/`free` and all five allocator globals, then removed and pruned the worktree, leaving `git worktree list` and `git status --porcelain` exactly as they were before.
- Ran all eight phase-gate legs and recorded each with its measured figure: both native suites 172/172 across 17 suites (run sequentially); `python3 -m pytest tests/ -q` at 348 passed (323 pre-change + 9 + 15 + 1 new legs); both symbol-gate halves 0 on all three ELFs, asserted over all eleven 64-bit symbols; the size-baseline policy comparison run under `--policy merge05` against the frozen BASE-01 record, PASSING and recorded AS one-sided with no exemption authored; the canonical policy invocation reproduced the documented pre-existing native-case-count red (`baseline=141 observed=172`, exits before flash is ever reported) and attributed it to Phase 158 / LAND-03, not to this phase; the build-warnings gate clean on a genuinely forced clean recompile of `uno` (both edited firmware files recompiled, zero warnings).
- Wrote `.planning/v1.33/155-after-figures.md`, the phase's landing record, with all 16 sections the plan specifies: git anchors, the measured result, five explicitly labelled corrections (OQ-1's 2 B guard-constant delta, OQ-2's both 64-bit totals, C-2's UNVERIFIED per-half split, the RAM/flash ledgers with the residual recorded not absorbed, OQ-4's corrected RAM derivation, C-5's corrected adjacency formulation, DEAD-04's full reading set re-run and reproduced, OQ-3's corrected asymmetric tolerance window, DEAD-05's coverage ceiling and phrasing-gate verdict, D-03's one-sided policy record), Phase 159's input (five shifted source files, zero citations remapped), the scope-fence confirmation, and the eight phase-gate verdicts.
- Ran the DEAD-05 phrasing gate over the real, complete corpus (`python3 .planning/v1.33/tools/check_dead05_phrasing.py`, from `/workspaces`): first run found one violation inside the phase record's own section 15 (quoting a forbidden needle while describing the fix, the same self-referential trap plan 03's executor hit while authoring the corpus doc) -- reworded to cite `155-VALIDATION.md` item 5 by pointer instead of the needle, per the corpus doc's own rule that no fourth exclusion may be added. Also found the mandated phrasing quoted as a Markdown blockquote failed the positive-half match because `_normalise` does not strip a leading `>` -- reformatted to the same italicised-quote shape `155-VALIDATION.md` already uses. Final run: exit 0, 21 files scanned, 75 in-scope paragraphs (floor 6 cleared), all four required-positive targets confirmed.
- Hand-edited `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` (per house convention: the GSD requirements/roadmap verbs reformat the whole file) to tick DEAD-01 through DEAD-06, correct the `-1364 B` header to `-1366 B` everywhere it appears in both files, and point each corrected clause at the relevant section of `155-after-figures.md`.

## Task Commits

1. **Task 1: Capture the after position, commit the real clean control, and prove the gate RED from the post-change side** - `adf1a31` (test, in `firestarter`)
2. **Task 2: Run all eight phase-gate legs and the one-sided size-baseline policy comparison** - no commit (measurement-only task; no file edited)
3. **Task 3: Write the phase record, then run the DEAD-05 phrasing gate over the real corpus** - `9f9c905c` (docs, in meta)

**Plan metadata:** committed together with this SUMMARY per the final-commit step (see STATE.md/ROADMAP.md update below).

## Files Created/Modified

- `firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/README.md` -- provenance for the real post-change clean control.
- `firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt` -- the verbatim real post-change `uno` `avr-nm` listing.
- `firestarter/tests/test_check_no_heap_or_64bit_symbols.py` -- added `test_real_postchange_listing_exits_zero`; updated the synthetic leg's docstring to point at the new real control.
- `.planning/v1.33/155-after-figures.md` -- the phase's landing record.
- `.planning/REQUIREMENTS.md` -- DEAD-01..DEAD-06 ticked, five corrections recorded, `-1364 B` header corrected to `-1366 B`.
- `.planning/ROADMAP.md` -- Phase 155's `Measured` header corrected, a phase-closed note with the five corrections added, `155-06-PLAN.md` checkbox ticked.

## Decisions Made

See `key-decisions` in the frontmatter for full detail. In brief: the throwaway-worktree planted negative had to mirror the pre-change shape (store-through-pointer, read-back-later) rather than a naive unused malloc+free, because the compiler silently eliminated the naive form; the canonical `--policy merge05` invocation was run WITH `--native-log` flags (not the docstring's literal native-log-less example) to reproduce the documented pre-existing native-case-count red rather than accept a misleadingly-green result; one predecessor SUMMARY transcription error (1,046,529 vs the correct 1,047,552 full-bandgap-range eval count) was caught and corrected in the phase record rather than propagated.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Naive planted-negative malloc/free pair was silently eliminated by the compiler**
- **Found during:** Task 1, step 5 (the throwaway-worktree planted negative)
- **Issue:** The first attempt reinstated `void* p = malloc(sizeof(uint32_t)); free(p);` inside `mem_util_blank_check` -- an allocation whose result is never read. `avr-nm` on the resulting build showed zero allocator symbols, and flash/RAM were unchanged from the clean post-change figures, meaning the compiler had proven the pair had no observable effect and eliminated it entirely. Running the gate against this build would have produced a false GREEN, defeating the whole point of the planted-negative proof.
- **Fix:** Rewrote the planted negative to mirror the pre-change code's own shape: allocate, store `handle->address` through the pointer, read it back in the `else` branch into `handle->address`, then free -- an externally-observable effect through the `handle` parameter that the compiler cannot prove away.
- **Files modified:** none in the tracked tree (the edit lived only inside the throwaway worktree, never committed)
- **Verification:** Rebuilt inside the worktree; flash grew 24660->25292 and RAM grew 1567->1575 (the allocator relinked), then the gate reported `FAIL: 7 forbidden symbol(s) found`, naming `malloc`, `free` and all five allocator globals.
- **Committed in:** N/A -- the worktree and its edit were never committed; only the verbatim FAIL output is quoted in `155-after-figures.md` section 13.

**2. [Rule 1 - Bug] DEAD-05 phrasing gate: one self-referential violation and one Markdown-blockquote match failure, both in this plan's own phase record**
- **Found during:** Task 3, first run of `check_dead05_phrasing.py` against the drafted record
- **Issue:** (a) Section 15's numbered list of corrected preserved-reference defects quoted a forbidden phrasing verbatim while describing the fix -- the same self-referential trap plan 03's executor caught in the corpus doc itself. (b) Section 11's mandated coverage-ceiling phrasing was written as a Markdown blockquote (`> proven by...` / `> shipped C...`); the tool's `_normalise` strips leading `//`, `*` and `#` comment markers but not a leading `>`, so the positive-half match failed even though the phrase was present.
- **Fix:** (a) Reworded to reference `155-VALIDATION.md` item 5 by pointer, per the corpus doc's own rule that no fourth exclusion may be added to turn a red run green. (b) Reformatted the phrase to the same italicised-quote shape `155-VALIDATION.md` already uses (no blockquote markers).
- **Files modified:** `.planning/v1.33/155-after-figures.md` (both fixes landed before the file's first and only commit)
- **Verification:** `python3 .planning/v1.33/tools/check_dead05_phrasing.py` (from `/workspaces`) exits 0 after both fixes: 21 files, 75 in-scope paragraphs, floor 6 cleared, all four required-positive targets confirmed.
- **Committed in:** `9f9c905c` (the record's only commit -- both fixes landed before the first commit, not as a follow-up)

---

**Total deviations:** 2 auto-fixed (both Rule 1 -- correctness bugs in this plan's own artefacts, caught before commit).
**Impact on plan:** No scope creep. Both fixes are confined to this plan's own new content (the throwaway worktree's uncommitted edit, and the phase record before its first commit) and do not touch any predecessor plan's artefact.

## Issues Encountered

**A pre-existing worktree unrelated to this plan.** `git -C firestarter worktree list` showed a second entry, `firestarter_py32_ci`, present since before this session started (unrelated PY32F071 CI work on a different branch). This plan's own throwaway worktree was created, used, and fully removed and pruned; `firestarter_py32_ci` was never touched and remains present, exactly as found -- the plan's "single entry after cleanup" phrasing assumed a clean starting state that this repo did not actually have; the honest, exact outcome (this plan's throwaway removed, the pre-existing unrelated one untouched) is recorded here and in the phase record rather than silently claiming a literal single-entry result.

**A transcription error in plan 04's own SUMMARY.** Re-running the oracle's model this session for the full-bandgap-range bit-identity leg gives 1,047,552 evaluations (`1023 x 1024`, from `range(1, 1024)` x `range(0, 1024)`), not the 1,046,529 plan 04's SUMMARY quoted. Corrected in `155-after-figures.md` section 9 with the discrepancy stated explicitly, per house convention (repair citations/figures, never accept staleness) rather than silently carried forward.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Phase 155 is closed: all six requirements (DEAD-01 through DEAD-06) are ticked in `REQUIREMENTS.md` against evidence that ran green this session, and `ROADMAP.md`'s Phase 155 entry carries a phase-closed note with all five corrections.
- `include/memory_utils.h` (Phase 156's target) was confirmed untouched by this phase; `scripts/baseline/size_baseline.json` is confirmed byte-unchanged (LAND-01 / Phase 158's job); the pre-existing native-case-count mismatch on the canonical `--policy merge05` invocation is recorded and attributed to Phase 158 / LAND-03, not fixed here.
- Five source files' lines shifted this phase (`src/boards/rurp_common.cpp`, `src/proms/memory.cpp`, `include/firestarter.h`, and both edited native test files) and zero `.planning/` citations were remapped, per D-01 -- Phase 159 / REMAP-04 maps the composite pre-154-to-post-158 diff, which now includes this phase's shifts.
- **Re-run obligation, not yet discharged by this SUMMARY's own existence:** `155-after-figures.md`'s own DEAD-05 phrasing-gate run (section 11) was performed before this SUMMARY file existed, and this SUMMARY is itself in the phrasing gate's corpus (glob 2). Per this plan's `<verification>` block, `python3 .planning/v1.33/tools/check_dead05_phrasing.py` must be re-run once more now that this SUMMARY exists, and the phase is not complete until that re-run is also green. This is a `<verification>` obligation of this plan, not an optional extra -- it will be performed as the final step of this execution, after this SUMMARY is committed.
- No blockers. `git -C firestarter status --porcelain` and the meta repo's porcelain are both clean apart from the pre-existing, operator-gated `firestarter`/`firestarter_app` gitlink drift and `package.json`/`package-lock.json`, none of which this plan touched or staged.

---
*Phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim*
*Completed: 2026-08-23*

## Self-Check: PASSED (one noted exception)

- FOUND: `.planning/phases/155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim/155-06-SUMMARY.md`
- FOUND: `.planning/v1.33/155-after-figures.md`
- FOUND: `firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/README.md`
- FOUND: `firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt`
- FOUND: `test_real_postchange_listing_exits_zero` in `firestarter/tests/test_check_no_heap_or_64bit_symbols.py`
- FOUND: commit `adf1a31` in `firestarter` history (`git -C firestarter log --oneline --all | grep adf1a31`)
- FOUND: commit `9f9c905c` in meta history (`git log --oneline --all | grep 9f9c905c`)
- FOUND: commit `8a5f36f2` in meta history (`git log --oneline --all | grep 8a5f36f2`)
- FOUND: commit `fe6a9aca` in meta history (`git log --oneline --all | grep fe6a9aca`)
- FOUND: `.planning/REQUIREMENTS.md` Traceability rows DEAD-01..DEAD-06 all read `Complete`
- CONFIRMED: `git -C firestarter status --porcelain` empty; `git -C firestarter rev-parse --verify wip/v1.33-size-reduction-survey-preserved` still resolves to `a6b46f8b12e81c62d9958945eb0bdbb8c16ae699`, unchanged
- CONFIRMED: `python3 .planning/v1.33/tools/check_dead05_phrasing.py` re-run with this SUMMARY present -- exit 0, 22 files scanned, 75 in-scope paragraphs (floor 6 cleared), all four required-positive targets confirmed. This discharges the "Re-run obligation" bullet above (it was performed; the bullet's future-tense wording is left as originally authored per the orchestrator's instruction not to otherwise edit the record).
- **Noted exception, not silently rounded up:** `git -C firestarter worktree list` shows two entries, not one -- `firestarter` (main tree) and `firestarter_py32_ci`, a worktree present before this session started (unrelated PY32F071 CI work on `feature/py32f071-release-assets`). This plan's own throwaway worktree (the post-change planted-negative proof) was created, used, and fully removed and pruned this session; `firestarter_py32_ci` was never touched by this plan and is not this plan's to remove. The plan's "single entry after cleanup" acceptance phrasing assumed a clean starting state the repo did not actually have. Every other self-check item above is unqualified.
- Phase-gate legs (native 172/172x2, host pytest 348, symbol gate 0/0x3, flash/RAM deltas, size-baseline policy, build-warnings) were NOT re-run for this self-check, per the orchestrator's explicit instruction -- their readings are cited from this SUMMARY's own Task Commits/Accomplishments sections and from `155-after-figures.md` section 13, both already committed and unchanged since.
