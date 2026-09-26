---
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "03"
subsystem: prose-mechanisation
tags: [pytest, stdlib-only, phrasing-gate, source-contract, oq-5, dead-05]

requires:
  - phase: "155-01"
    provides: "before-figures baseline confirming the pre-change tree, used as read-only context for the coverage-ceiling wording"
provides:
  - "Two-halved DEAD-05 phrasing gate (.planning/v1.33/tools/check_dead05_phrasing.py): negative scan for six forbidden coverage phrasings about rurp_read_voltage_mv, plus a positive assertion that the mandated correct phrasing is present in four required targets"
  - "Committed contract (.planning/v1.33/155-dead05-phrasing-corpus.md) recording the twelve-glob corpus, the three named exclusions with reasons, PARAGRAPH_FLOOR=6 justified by construction, and the four required-positive targets"
  - "Committed planted violation (fixtures/planted_dead05_phrasing_violation.md) and a 9-leg pytest suite proving the gate discriminates: RED on the planted violation, GREEN on a synthetic clean corpus, fail-closed below the floor, fail-closed on a missing/incorrect required target, fail-closed on malformed argv"
affects: ["155-04", "155-06"]

tech-stack:
  added: []
  patterns:
    - "Concatenation-built needles (_forbidden_needles): the six forbidden phrasings are assembled from string fragments at runtime so the gate's own source text cannot literally contain a phrase it exists to detect -- copied in spirit from firestarter/tests/test_write_path_source_contract_v131.py's skip-bypass anti-self-match trick"
    - "Corpus-doc-as-contract: the tool's constants (CORPUS_GLOBS, NAMED_EXCLUSIONS, TRIGGER_TOKENS, PARAGRAPH_FLOOR, REQUIRED_POSITIVE_TARGETS) mirror a committed Markdown record item for item, so scope changes are reviewable prose edits, not buried script constants"
    - "'firestarter/' prefix convention on glob/target strings selects --fw-root vs --corpus-root, letting one flat tuple describe a dual-repo corpus without a second parallel list"

key-files:
  created:
    - .planning/v1.33/155-dead05-phrasing-corpus.md
    - .planning/v1.33/tools/check_dead05_phrasing.py
    - .planning/v1.33/tools/test_check_dead05_phrasing.py
    - .planning/v1.33/tools/fixtures/planted_dead05_phrasing_violation.md
  modified: []

key-decisions:
  - "PARAGRAPH_FLOOR=6 is justified by construction (the corpus doc names the six paragraphs that must exist once plans 04-06 land), not by observation of today's partial corpus -- today's real corpus already clears it without those six specific paragraphs, which is coincidental and not the justification recorded"
  - "A corpus glob matching zero files today (plans 04's oracle pytest, the corrected rurp_common.cpp comment) is silently absent from the resolved file list -- distinct from a REQUIRED_POSITIVE_TARGET missing from disk, which is always exit 2 regardless of glob match. This choice is recorded, with its rationale, in the corpus doc so it cannot be read as an oversight"
  - "The corpus doc's own trigger-scoping paragraph (section 3) was rewritten mid-task after a self-scan caught it quoting three of the six forbidden phrasings verbatim (enumerated in 155-VALIDATION.md item 5) inside a paragraph that also names rurp_read_voltage_mv -- exactly the trap section 9 warns about avoiding. Fixed by referencing 155-VALIDATION.md item 5 instead of naming any example words"
  - "requirements-completed is deliberately empty. DEAD-05 stays Pending in REQUIREMENTS.md: this plan ships the mechanism and proves it discriminating on synthetic fixtures; plan 06 runs it over the finished, real corpus once plans 04-05 have authored the four required-positive targets. Marking the requirement complete here would repeat the exact failure mode 155-02's executor had to revert"

requirements-completed: []

coverage:
  - id: D1
    description: "Committed corpus contract naming the twelve-glob corpus, exactly three named exclusions with reasons, PARAGRAPH_FLOOR=6 justified by construction, and the four required-positive targets"
    verification:
      - kind: other
        ref: "grep-based acceptance checks (PARAGRAPH_FLOOR, rurp_read_voltage_mv, all three exclusion filenames, mandated phrasing) all pass; git status clean after commit 0358596"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two-halved phrasing gate (negative scan + positive assertion) with forbidden needles built by concatenation, word-boundary matching, paragraph-scoped triggering, and a manual (no-argparse) CLI"
    requirement: "DEAD-05"
    verification:
      - kind: unit
        ref: "test_check_dead05_phrasing.py::test_planted_violation_exits_one_and_names_the_paragraph, ::test_paragraph_not_naming_the_function_is_not_flagged, ::test_clean_corpus_with_the_phrasing_exits_zero, ::test_below_paragraph_floor_exits_two, ::test_missing_required_positive_target_exits_two, ::test_present_target_without_the_phrasing_exits_one, ::test_malformed_argv_exits_two, ::test_tool_source_does_not_contain_its_own_needles, ::test_this_module_cannot_be_silently_skipped (9/9 pass)"
        status: pass
      - kind: other
        ref: "explicit CLI invocation against the committed planted fixture: exit 1, FAIL: naming file:line and the matched needle (the first entry in 155-VALIDATION.md item 5)"
        status: pass
      - kind: other
        ref: "explicit CLI invocation against a synthetic clean corpus at exactly PARAGRAPH_FLOOR=6: exit 0, PASS: naming every file and every required target"
        status: pass
      - kind: other
        ref: "explicit CLI invocation with a 1-paragraph corpus: exit 2 (floor breach); explicit CLI invocation with --definitely-not-a-flag: exit 2 (malformed argv)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Gate runs clean (zero forbidden-phrasing violations, floor cleared) over the real, already-committed Phase 155 artefacts -- default-argument invocation against /workspaces and /workspaces/firestarter"
    verification:
      - kind: other
        ref: "python3 .planning/v1.33/tools/check_dead05_phrasing.py (no args) resolves 16 real files, reports zero violations, then ERROR: on the two required targets plan 04/06 have not yet authored -- exactly the documented, expected-absence behaviour, not a violation"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-08-23
status: complete
---

# Phase 155 Plan 03: DEAD-05 Phrasing Gate Summary

**Two-halved DEAD-05 mechanisation (negative scan + positive assertion) over a committed twelve-glob corpus, with forbidden needles built by concatenation, a by-construction paragraph floor, and both RED and GREEN proven by explicit invocation before the artefacts it will judge exist.**

## Performance

- **Duration:** ~30min
- **Completed:** 2026-08-23
- **Tasks:** 2/2 completed
- **Files modified:** 4 created (0 modified)

## Accomplishments

- Wrote `.planning/v1.33/155-dead05-phrasing-corpus.md`: the tool's contract, recording the twelve corpus globs (dual-repo, "firestarter/"-prefix convention), exactly three named exclusions with reasons (`155-RESEARCH.md`, `155-PATTERNS.md`, `155-VALIDATION.md`), `PARAGRAPH_FLOOR=6` justified by construction, the four required-positive targets, the "not-yet-authored corpus member vs. missing required target" distinction, the named unmitigated avr-gcc residual risk, and the "runs in no CI workflow" disclosure.
- Caught and fixed a self-inflicted violation while authoring that same document: its own trigger-scoping paragraph originally quoted three of the six forbidden phrasings verbatim as examples (they are enumerated in `155-VALIDATION.md` item 5) inside a paragraph that also names `rurp_read_voltage_mv` -- exactly the trap the plan warned about avoiding for the tool's own deliverables. Rewrote it to cite `155-VALIDATION.md` item 5 instead of naming any example word, then re-verified with a standalone paragraph-scoped scan before committing.
- Built `.planning/v1.33/tools/check_dead05_phrasing.py`: stdlib-only, manual (no-argparse) CLI, constants mirroring the corpus doc item for item, `_forbidden_needles()` building the six phrasings from concatenated fragments, `_normalise()` stripping C/Python comment leaders and collapsing whitespace so a sentence wrapped across comment lines still matches, `_paragraphs()` splitting on blank-line runs with line-anchored output, and a five-step `main()` (resolve corpus -> negative scan -> floor check -> positive check -> PASS) matching `check_erase_no_vpp.py`'s ordering convention (real violations reported ahead of the anchor/floor check).
- Built the planted fixture (`fixtures/planted_dead05_phrasing_violation.md`) with three paragraphs: one in-scope violation, one in-scope clean paragraph carrying the correct phrasing, and one out-of-scope paragraph carrying a forbidden word without the trigger token -- the discrimination leg.
- Built `test_check_dead05_phrasing.py`: 9 legs (RED, anti-noise, GREEN, floor anti-vacuity, missing-target, present-but-wrong-target, malformed argv, source-self-match, anti-skip), all passing (`9 passed in 0.28s`).
- Ran four **explicit CLI invocations** outside pytest to record RED, GREEN, and both exit-2 paths directly: planted violation (exit 1, naming file:9 and the matched needle), synthetic clean corpus at exactly the floor (exit 0, PASS naming all 5 files and all 4 targets), a 1-paragraph corpus (exit 2, floor breach), and `--definitely-not-a-flag` (exit 2, malformed argv).
- Ran the tool with its **default arguments** (no `--corpus-root`/`--fw-root`) against the real repositories: resolved 16 real files, found **zero forbidden-phrasing violations** in the already-committed Phase 155 corpus, then reported the expected `ERROR:` for the two required targets plans 04/06 have not yet authored -- proving the negative half and the floor both already hold cleanly against real prose, exactly as documented.
- Confirmed throughout: `firestarter` submodule untouched (`git -C firestarter status --porcelain` empty, HEAD still `076abc2`), pre-existing meta noise (`firestarter_app`, `package.json`/`package-lock.json`, `.planning/config.json`) left unstaged, and `DEAD-05` still `Pending` in `REQUIREMENTS.md`.

## Task Commits

1. **Task 1: Record the corpus, its three named exclusions and the non-vacuity floor** - `0358596` (docs)
2. **Task 2: Build the two-halved phrasing gate, its pytest and its planted violation** - `c042186` (test)

**Plan metadata:** committed together with this SUMMARY per the final-commit step (see STATE.md/ROADMAP.md update below).

## Files Created/Modified

- `.planning/v1.33/155-dead05-phrasing-corpus.md` - the committed contract: corpus, exclusions, floor, required targets, residual risk, no-CI disclosure.
- `.planning/v1.33/tools/check_dead05_phrasing.py` - the two-halved gate itself.
- `.planning/v1.33/tools/test_check_dead05_phrasing.py` - 9-leg pytest suite proving the gate discriminates.
- `.planning/v1.33/tools/fixtures/planted_dead05_phrasing_violation.md` - the committed planted violation, with its discrimination paragraph.

## Decisions Made

- See `key-decisions` in frontmatter: the by-construction paragraph floor, the "not-yet-authored glob member vs. missing required target" distinction, the self-caught trigger-scoping fix, and the deliberate `requirements-completed: []`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corpus doc's own trigger-scoping paragraph quoted forbidden words next to the trigger token**
- **Found during:** Task 1, immediately before commit (self-scan of the drafted document)
- **Issue:** Section 3's explanation of the trigger used three of the six forbidden phrasings verbatim as example words (enumerated in `155-VALIDATION.md` item 5) inside the same paragraph that names `rurp_read_voltage_mv` -- a paragraph-scoped scan over the corpus doc would have flagged this as a real violation, which is precisely the self-exemption trap the plan's critical constraints forbid working around.
- **Fix:** Rewrote the paragraph to reference `155-VALIDATION.md` item 5 by pointer instead of naming any example word from the forbidden list.
- **Files modified:** `.planning/v1.33/155-dead05-phrasing-corpus.md`
- **Verification:** Standalone Python paragraph-scoped scan (mirroring the tool's own logic) confirmed zero forbidden-phrase hits in any trigger-token paragraph before committing; the later real-corpus CLI run against this exact file (as part of Task 2's verification) confirmed zero violations independently.
- **Committed in:** `0358596` (the corpus doc's only commit -- the fix landed before the first commit, not as a follow-up)

---

**Total deviations:** 1 auto-fixed (1 self-caught bug in a doc authored this task)
**Impact on plan:** No scope creep. The fix is exactly the discipline the plan's own critical constraint 7 asked for ("write them so the gate passes over them").

## Issues Encountered

None beyond the self-caught issue above.

## User Setup Required

None - no external service configuration required. The gate is a local pytest/CLI tool; no dependency was installed.

## Next Phase Readiness

The gate mechanism, its contract, and its planted-violation proof are committed and stable. Plan 04 must author two of the four required-positive targets (`firestarter/src/boards/rurp_common.cpp`'s corrected comment and `firestarter/tests/test_voltage_reformulation_oracle.py`) while writing its own DEAD-04 oracle; plan 06 authors the third (`.planning/v1.33/155-after-figures.md`) and then runs `check_dead05_phrasing.py` with no arguments against the finished, real corpus, expecting exit 0. `155-VALIDATION.md` (the fourth required target) already carries the mandated phrasing today and needs no further edit for this gate. No blockers. `DEAD-05` remains `Pending` in `REQUIREMENTS.md` by design until that plan-06 run succeeds.

---
*Phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim*
*Completed: 2026-08-23*

## Self-Check: PASSED

- FOUND: `.planning/v1.33/155-dead05-phrasing-corpus.md`
- FOUND: `.planning/v1.33/tools/check_dead05_phrasing.py`
- FOUND: `.planning/v1.33/tools/test_check_dead05_phrasing.py`
- FOUND: `.planning/v1.33/tools/fixtures/planted_dead05_phrasing_violation.md`
- FOUND: commit `0358596` (`git log --oneline --all | grep 0358596`)
- FOUND: commit `c042186` (`git log --oneline --all | grep c042186`)
