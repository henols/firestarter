---
phase: quick-260916-tea
plan: 01
subsystem: testing
tags: [devtest-triage, regex, mutation-testing, ledger, dev-test]

requires:
  - phase: quick-260916-nbc
    provides: "The `firmware_messages.resolve_error` wiring and `_mutation.py` / fixture-loader conventions this plan's test cases build on"
provides:
  - "`VALIDATED-EPROMS.md`: TMS27C512 (#72), W27C040 (#87) and MX27C4000 (#74, #75) rows landed; W29C040 re-stamped to host 3.0.0b44 / firmware 3.0.0b31 with issues #48 and #88; three derived family tables regenerated; a GSD process citation stripped from `## Notes`"
  - "SKILL.md: a standing rule banning GSD process references from ledger `## Notes` entries"
  - "`devtest_issues.py`: `FENCE_RE` replaced with a line-anchored pattern (`^```[^\\n]*\\n(.*?)^```` with `re.DOTALL | re.MULTILINE`) so the report block is found even when other fenced blocks (e.g. the captured-log block `dev test` now emits) precede it"
  - "`fixtures/dev-test-sst39sf040-log-capture-first.md`: hand-authored fixture modelled on issue #90's real shape (step table, captured-log `text` block, then the `json` report), schema 2.2"
  - "Three new cases in `TestUntrustedBodyParser`: report-found-behind-a-preceding-block, a mutation guard proving the fix is load-bearing, and an unclosed-fence case that returns `None` without raising"
  - "SKILL.md section 2: a paragraph documenting the captured-log-block-first shape and naming the new fixture as its committed case"
affects: [devtest-triage]

actuals:
  tokens: 3536
  tasks: 2
  commits: 2
  plan_head_before: e334662062f5534fe9b36c80ed46827aa38fa99f

tech-stack:
  added: []
  patterns:
    - "Line-anchored fence enumeration (`^```...^```` + MULTILINE) replacing a bare/`json`-only fence match, so the info string is never load-bearing for detection -- only content (`schema_version` presence) is"
    - "Mutation-guard idiom reused from `_mutation.py`: the guard swaps the post-fix `re.compile` argument text for the pre-fix text and asserts the mutant answers wrongly, making the RED demonstration permanent"

key-files:
  created:
    - .claude/skills/devtest-triage/fixtures/dev-test-sst39sf040-log-capture-first.md
  modified:
    - VALIDATED-EPROMS.md
    - .claude/skills/devtest-triage/SKILL.md
    - .claude/skills/devtest-triage/scripts/devtest_issues.py
    - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py

key-decisions:
  - "Task 1 committed the ledger and SKILL.md rule unedited, exactly as DD/precondition specified: `git status --porcelain` showed both files already modified in the working tree, `eprom_ledger.py check` already reported a fresh-render match, so no re-render or hand-edit was needed or performed."
  - "Task 2 followed DD-2 literally: replaced only `FENCE_RE`'s pattern and flags, changed nothing else in `extract_report` (the `schema_version`-presence test, `MAX_BODY` bound, fail-soft `except`, and first-match-wins order all stayed as written). Reproduced the pre-fix failure first (`FENCE_RE.findall` on the new fixture returned one empty block, `extract_report` returned `None`), matching DD-1's measured walk exactly."
  - "Reused error codes 183 (`MSG_ERR_OP_TIMEOUT`) and 175 (`MSG_ERR_VERIFY`) from the existing `dev-test-error-codes-populated.md` fixture on the new fixture's write/verify rows -- both are real `firmware_messages` table entries, so `show`'s resolved-name behavior is exercised with values already known to resolve, rather than inventing new ones."
  - "Mutation-guard anchor is the exact `re.compile(...)` argument text (pattern literal plus flags) written as a raw single-quoted Python string in the test file, verified programmatically to occur exactly once in `devtest_issues.py` before relying on `load_mutant`'s own uniqueness assertion."
  - "An explanatory `#`-comment block above the two mutation-guard constants was caught by self-review after the first write and converted to attribute docstrings (string literals immediately following each assignment) -- satisfying the plan's no-new-comment-line rule (docstrings are exempt, `#` comments are not) without losing the explanation."

requirements-completed: [260916-tea]

coverage:
  - id: D1
    description: "Four validated chips (TMS27C512, W27C040, MX27C4000 x2, plus W29C040's re-validation) are committed to VALIDATED-EPROMS.md and reach `beta`'s line of descent, not just the working tree"
    requirement: "260916-tea"
    verification:
      - kind: other
        ref: "python3 .claude/skills/devtest-triage/scripts/eprom_ledger.py check (exit 0, 'matches a fresh render')"
        status: pass
    human_judgment: false
  - id: D2
    description: "SKILL.md's ledger section states the no-GSD-process-reference rule for future Notes entries"
    requirement: "260916-tea"
    verification:
      - kind: other
        ref: "grep -c -e '.planning/' -e 'Phase [0-9]' VALIDATED-EPROMS.md == 0; SKILL.md diff carries the +7-line rule"
        status: pass
    human_judgment: false
  - id: D3
    description: "extract_report finds the report block when a fenced block of another language precedes it, regardless of that block's info string; a schema bump needs no code change"
    requirement: "260916-tea"
    verification:
      - kind: unit
        ref: "test_devtest_issues.py#TestUntrustedBodyParser.test_extract_report_finds_block_behind_preceding_text_block"
        status: pass
      - kind: unit
        ref: "test_devtest_issues.py#TestUntrustedBodyParser.test_fence_enumerator_mutation_guard"
        status: pass
    human_judgment: false
  - id: D4
    description: "Issue #90 renders as a parseable report end to end through the real gh path: list carries no (no JSON report) note, show 90 prints schema 2.2 / host 3.0.0b44 / firmware 3.0.0b31:leonardo and routes FAIL on write, verify"
    requirement: "260916-tea"
    verification:
      - kind: manual_procedural
        ref: "python3 devtest_issues.py show 90 (live gh, authenticated) -- printed schema 2.2, host 3.0.0b44, firmware 3.0.0b31:leonardo, ROUTE FAIL — write, verify; list --state all showed no '(no JSON report)' note on any issue"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-09-16
status: complete
---

# Quick Task 260916-tea: Correct the dev test so all relevant work reaches beta, and fix the fence-detection defect Summary

**Landed four stranded validated-chip ledger rows plus a Notes provenance rule, and fixed `FENCE_RE` so `dev test`'s new captured-log block no longer hides every report behind it.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-09-16T21:29:01Z
- **Tasks:** 2
- **Files modified:** 5 (1 created, 4 modified)

## Accomplishments

- Committed the working-tree-only ledger update (TMS27C512 #72, W27C040 #87, MX27C4000 #74/#75, W29C040 re-stamp #48/#88) plus SKILL.md's matching "no GSD process references in Notes" rule — both already correct on disk, verified against `eprom_ledger.py check` before committing.
- Root-caused and fixed the silent report-detection defect: `FENCE_RE`'s old pattern resynchronised on a preceding fenced block's closing delimiter and consumed the real report block as filler. Replaced it with a line-anchored pattern (`^```[^\n]*\n(.*?)^```` + `re.DOTALL | re.MULTILINE`) that accepts any info string and tries every fenced block in document order — unchanged qualification rule (`json.loads` yields a dict carrying `schema_version`).
- Added a hand-authored fixture (`dev-test-sst39sf040-log-capture-first.md`) modelled on issue #90's real shape, plus a mutation-guarded regression test proving the fix is load-bearing (the pre-fix pattern, restored via `load_mutant`, misses the report on the same body).
- Verified against the live issue tracker: `show 90` now parses end to end (schema 2.2, host 3.0.0b44, firmware 3.0.0b31:leonardo, `ROUTE: FAIL — write, verify`) and `list --state all` shows no `(no JSON report)` note on any of the 39 listed issues.

## Task Commits

1. **Task 1: Commit the stranded ledger rows and the Notes rule** - `f2a6fa6e` (docs)
2. **Task 2: Find the report block behind a preceding log-capture block** - `d4a31c15` (fix, tdd)

_No separate plan-metadata commit was made for this quick task; both commits above are the whole of this plan's work._

## Files Created/Modified

- `VALIDATED-EPROMS.md` — four validated-chip rows added/updated; Notes provenance citation stripped
- `.claude/skills/devtest-triage/SKILL.md` — ledger Notes rule (Task 1); section 2 paragraph on the captured-log-first shape (Task 2)
- `.claude/skills/devtest-triage/scripts/devtest_issues.py` — `FENCE_RE` line-anchored; `extract_report`'s docstring corrected
- `.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py` — three new `TestUntrustedBodyParser` cases plus a fixture loader and mutation anchors
- `.claude/skills/devtest-triage/fixtures/dev-test-sst39sf040-log-capture-first.md` — new hand-authored fixture (created)

## Decisions Made

See `key-decisions` in frontmatter. In short: Task 1 required no editing (the ledger and rule were already correct on disk — only staging and committing); Task 2's fix touched exactly one line plus its governing docstring, per DD-2, and reused known-good error codes from an existing fixture rather than inventing new ones.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 / self-correction] Removed a `#`-comment block that violated the plan's own no-new-comment-line rule**
- **Found during:** Task 2, immediately after first-drafting the mutation-guard constants in `test_devtest_issues.py`
- **Issue:** A three-line `#` comment explaining the two mutation-anchor constants was added above them, violating the plan's explicit "No new `#` comment line in either Python file" instruction (DD-5) and CLAUDE.md's project-wide no-source-comments rule.
- **Fix:** Converted the explanation into attribute docstrings — string literals immediately following each constant's assignment — which the DD-5 instruction (and CLAUDE.md) treats as documentation, not commentary, matching the surrounding module's docstring-only style.
- **Files modified:** `.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py`
- **Verification:** `git diff ... | grep -E '^\+[[:space:]]*#'` returns no matches after the fix; full suite still green (71 tests).
- **Committed in:** `d4a31c15` (the comment never existed in any committed state — caught and fixed pre-commit)

---

**Total deviations:** 1 self-caught-and-fixed (no scope creep; never reached a commit).
**Impact on plan:** None — the violation was caught and corrected before staging, so no commit ever carried it.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The dev-test triage skill's parser now handles the current `dev test` build's output shape; no further chip-detection work is blocked on this defect.
- Issue #90 and any other open issue carrying a captured-log block ahead of its report are now triageable through `list`/`show`/`fold` without manual JSON extraction.
- Four more chips are ready to reach `beta` once this branch merges.

---
*Phase: quick-260916-tea*
*Completed: 2026-09-16*
