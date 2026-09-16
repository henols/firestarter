---
phase: quick-260916-ess
plan: 01
subsystem: testing
tags: [unittest, stdlib, devtest-triage, devtest-rootcause, mutation-testing, ast]

requires: []
provides:
  - "Stdlib `unittest` suite for `devtest_issues.py` pinning all nine documented `supersedes()` outcomes plus the untrusted-body parser, with 4 mutation guards"
  - "Stdlib `unittest` suite for `eprom_ledger.py` proving the render/read round trip, Notes preservation, and the stderr-loud dropped-row path, with 2 mutation guards"
  - "Stdlib `unittest` suite for `infoic_lookup.py` detecting `VPP_MV` drift against `build_db.py` via `ast.literal_eval`"
  - "Shared `_mutation.load_mutant()` helper making every mutation-guard RED demonstration permanent and executable"
  - "One published discovery-loop command in both SKILL.md files, with an explicit no-CI disclosure"
affects: [devtest-triage, devtest-rootcause, eprom_ledger, infoic_lookup]

actuals:
  tokens: 8388
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Mutation guards via `importlib.util.spec_from_file_location` on a text-patched temp copy of the module under test, gated by an anchor-count assertion (`source.count(old) == 1`)"
    - "AST-based cross-module table comparison (`ast.parse` + `ast.literal_eval`) to detect drift without importing the other module"
    - "Real-path testing: every `supersedes()` assertion goes through `_summarize()` on a `gh`-shaped issue dict, never a hand-built summary"

key-files:
  created:
    - .claude/skills/devtest-triage/scripts/tests/_mutation.py
    - .claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py
    - .claude/skills/devtest-triage/scripts/tests/test_eprom_ledger.py
    - .claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py
  modified:
    - .claude/skills/devtest-triage/SKILL.md
    - .claude/skills/devtest-rootcause/SKILL.md
    - .planning/milestones/v1.32-phases/147-report-provenance-every-dev-test-report-names-its-firmware/147-RESEARCH.md
    - .planning/milestones/v1.37-phases/187-answered-reports/187-CONTEXT.md
    - .planning/milestones/v1.37-phases/187-answered-reports/187-PATTERNS.md
    - .planning/milestones/v1.37-phases/187-answered-reports/187-RESEARCH.md

key-decisions:
  - "Followed the plan's itemized mutation-guard tables literally (4 in Task 1, 2 in Task 2 = 6 total) rather than the plan's own rollup prose which said 'seven mutation guards' — the itemized anchors are the authoritative spec; the rollup count appears to be an off-by-one in the plan text itself (see Deviations)."
  - "family_names is confirmed correctly documented (not tested): the docstring now accurately describes that adding a chip can rename an existing family. The remaining question — whether families should be cited by a stable key rather than a name that can shift — is a design decision for the operator, not a defect."
  - "Did not touch the pre-existing uncommitted eprom_ledger.py docstring correction or the firestarter_app/firestarter_fw gitlink diffs already present in the working tree at session start — out of this plan's file scope."
  - "Repaired only the 6 .planning/ file:LINE citations into devtest-triage/SKILL.md that were valid before this edit and were displaced by the uniform +8 line insertion. Left several already-stale citations (into both SKILL.md files) untouched, since they pointed past end-of-file or at unrelated content before this edit — pre-existing drift from an earlier SKILL.md rewrite, out of this task's scope."
  - "Left .planning/graphs/GRAPH_REPORT.md's stale citation alone — it is a generated artifact and its own file says never hand-edited."

requirements-completed: [260916-ess]

duration: ~55min
completed: 2026-09-16
status: complete
---

# Quick Task 260916-ess: Test Coverage for the devtest Skills Summary

**Stdlib-`unittest` suites (41 tests total) for `devtest_issues.py`'s `supersedes()` three-leg
close and `eprom_ledger.py`'s round-trip renderer, plus a `VPP_MV` drift detector for
`infoic_lookup.py` — six mutation guards make the RED demonstration permanent and executable
instead of a commit-message claim.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 3
- **Files created:** 4 test modules (1 shared helper + 3 test files)
- **Files modified:** 2 SKILL.md (test command + no-CI disclosure) + 4 `.planning/` citation repairs

## Accomplishments

- 23 tests pin `devtest_issues.py`: all 9 documented `supersedes()` outcomes (through the real
  `issue dict -> _summarize() -> supersedes()` path, never a hand-built summary), the
  untrusted-body parser (`extract_report`, `parse_title`, `is_devtest`, `fingerprint`,
  `MAX_BODY` DoS safety), `version_key` ordering, and 4 mutation guards.
- 13 tests pin `eprom_ledger.py`: render/read round trip (including a two-issue-reference row
  and a `not reported` firmware row), render idempotence, byte-for-byte Notes preservation, the
  empty-Notes sentinel round trip, the stderr-loud dropped-row path, header-row-based (not
  heading-based) table location, `cmd_add`'s three refusal rules, a guarded live check against
  the real ledger, and 2 mutation guards.
- 5 tests pin `infoic_lookup.py`: `VPP_MV` drift detection against `build_db.py` via
  `ast.literal_eval` (never `import build_db`), a negative control on the drift comparison
  itself, `format_vpp` rendering, and the masked-high-nibble key invariant.
- One command (`for d in $ROOT/.claude/skills/*/scripts/tests; do python3 -m unittest discover
  -s "$d" -t "$d" || break; done`) runs all 41 tests across both skills; published in both
  SKILL.md files with an explicit statement that nothing runs them automatically.
- All firestarter_app-dependent live checks (the ledger `cmd_check` test, the `VPP_MV` drift
  test) ran for real in this environment (the submodule is checked out) rather than skipping —
  both tables/renders are measured equal/consistent today, exactly as the planning facts
  predicted.

## Task Commits

1. **Task 1: Pin the three-leg supersede rule and the untrusted-body parser, with mutation
   guards** - `8ed5d4a1` (test)
2. **Task 2: Prove the ledger round-trips, preserves Notes, and cannot drop a row silently** -
   `0afbc99a` (test)
3. **Task 3: Detect infoic_lookup table drift, then publish the one command in both SKILL.md
   files** - `e5e4ed6f` (test)

## Files Created/Modified

- `.claude/skills/devtest-triage/scripts/tests/_mutation.py` - shared `load_mutant()` helper;
  anchor-count-gated, raises loudly if a refactor dissolves the anchor
- `.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py` - 23 tests, 4 mutation
  guards
- `.claude/skills/devtest-triage/scripts/tests/test_eprom_ledger.py` - 13 tests, 2 mutation
  guards
- `.claude/skills/devtest-rootcause/scripts/tests/test_infoic_lookup.py` - 5 tests, drift
  negative control
- `.claude/skills/devtest-triage/SKILL.md` - added the test-discovery command + no-CI line
- `.claude/skills/devtest-rootcause/SKILL.md` - added the test-discovery command + no-CI line
- `.planning/milestones/v1.32-phases/147-.../147-RESEARCH.md` - repaired `SKILL.md:61-67` ->
  `:69-75` (displaced by insertion)
- `.planning/milestones/v1.37-phases/187-answered-reports/187-CONTEXT.md` - repaired
  `SKILL.md:211-220` -> `:219-228`
- `.planning/milestones/v1.37-phases/187-answered-reports/187-PATTERNS.md` - repaired
  `SKILL.md:345-349` -> `:353-357`
- `.planning/milestones/v1.37-phases/187-answered-reports/187-RESEARCH.md` - repaired
  `SKILL.md:205-225`/`:340-355` -> `:213-233`/`:348-363`, `:208-220` -> `:216-228`, `:345-349`
  -> `:353-357`

## Exact runner command

```bash
for d in $ROOT/.claude/skills/*/scripts/tests; do
  python3 -m unittest discover -s "$d" -t "$d" || break
done
```

Also runnable standalone per module, e.g. `python3
.claude/skills/devtest-triage/scripts/tests/test_devtest_issues.py -v`. **Nothing runs any of
this automatically** — the repository has no `.github/workflows/` directory, so both SKILL.md
files say plainly that the tests are run by hand, not by CI.

## Falsifiability audit — RED evidence per test

Per the plan's `<verification>` contract, every test's RED evidence is recorded below. The
authoritative source for the intended mutation-guard count is the plan's itemized per-task
tables — **6 total** (Task 1: 4, Task 2: 2) — not the plan's own summary-line prose
("seven mutation guards"), which appears to be an off-by-one slip against its own itemized
list; see Deviations.

### The 6 mutation-guarded properties — permanent and executable

Each loads a text-patched copy of the real module via `_mutation.load_mutant()`, gated by
`source.count(old) == 1`, and asserts the mutant answers the guarded scenario wrongly. Observed
live during this session (not just claimed):

1. **`devtest_issues.py` leg 1** (`ok["generated_full"] > fail["generated_full"]` ->
   `!= `): intact code blocks an earlier PASS; mutant wrongly lets it supersede.
2. **`devtest_issues.py` leg 2** (`advanced = oh > fh or (...)` -> `advanced = True`): intact
   code blocks a same-build PASS; mutant wrongly lets it supersede.
3. **`devtest_issues.py` leg 3** (`if got != "OK":` -> `if got not in ("OK", "NA"):`): intact
   code blocks a `write NA` PASS from superseding a `write BAD` failure; mutant wrongly lets it
   supersede. **Observed live against the real, unmutated source** (not just via the temp-copy
   mechanism): editing `devtest_issues.py` directly and re-running the suite produced
   ```
   AssertionError: mutation anchor 'if got != "OK":' occurs 0 time(s) in
   /workspaces/.claude/skills/devtest-triage/scripts/devtest_issues.py, expected exactly 1
   ```
   (the guard's own anchor-count safety net firing, since the anchor no longer existed) AND
   ```
   FAIL: test_write_na_does_not_supersede
   AssertionError: True is not false
   ```
   (the direct scenario test independently catching the real regression). File was restored via
   `git checkout --` immediately after; `git status --short` confirmed clean.
4. **`devtest_issues.py` `version_key`** (`float(pre) if pre is not None else float("inf")` ->
   `... else 0.0`): intact code ranks `3.0.0b22 < 3.0.0`; mutant wrongly reverses the ranking.
5. **`eprom_ledger.py` date regex** (`(?P<date>\d{4}-\d{2}-\d{2})` -> `...\d)`): intact code
   parses every row; mutant returns zero records.
6. **`eprom_ledger.py` Notes else-branch** (`notes.strip("\n") if notes.strip() else "- None."`
   -> `"- None."`): intact code preserves an operator note; mutant always emits `- None.`
   **Observed live against the real, unmutated source**: editing `eprom_ledger.py` directly and
   re-running the suite failed 3 tests —
   ```
   FAIL: test_mutation_guard_notes_else_branch_loses_notes
   AssertionError: 'Operator note' not found in '...## Notes\n\n- None.\n'
   FAIL: test_notes_survive_rewrite_byte_for_byte
   AssertionError: '- None.' != '- W29C040 socket note: verify pin 1 orienta[113 chars]ine.'
   FAIL: test_live_ledger_matches_fresh_render_or_skips
   AssertionError: 1 != 0
   ```
   The third failure is notable: the regression also broke `cmd_check` against the **real**
   `/workspaces/VALIDATED-EPROMS.md`, showing a genuine drift (the real file's authored Notes
   content — the AE29F2008/W29C020 note — got replaced by `- None.` under the mutant). File was
   restored via `git checkout --` immediately after; confirmed clean and green again.

### The drift comparison — permanent, negative-controlled

`table_drift(a, b)` (test helper in `test_infoic_lookup.py`) is asserted empty for the two live
tables (green on arrival — measured equal, 16 entries) and non-empty, naming the key, for a
copy of `VPP_MV` with one value perturbed by +500. This supplies the RED demonstration for a
comparison that is otherwise unfalsifiable when `firestarter_app` is absent.

### Everything else — observed once, by hand, against a deliberately broken input

Captured this session via a scratch copy with swapped-in wrong assertions (`test_eprom_ledger.py`):

```
FAIL: test_round_trip_recovers_every_authored_field
AssertionError: '3.0.0b33' != '3.0.0b33-WRONG'
FAIL: test_notes_survive_rewrite_byte_for_byte
AssertionError: [...] != [...]\nEXTRA
FAIL: test_dropped_row_is_reported_on_stderr_and_dropped_from_render
AssertionError: 'THIS WARNING TEXT DOES NOT EXIST' not found in
  'WARN: not in the database, dropped: UNKNOWNCHIP123\n'
FAIL: test_cmd_add_refuses_duplicate_without_force_and_replaces_with_force
AssertionError: 1 != 0
FAIL: test_read_records_returns_empty_when_header_row_is_corrupted
AssertionError: 0 != 999
```

All five fail as expected against wrong assertions and pass against the real code, confirming
each is a genuine property check rather than a tautology. The remaining tests in
`test_devtest_issues.py` (parser cases, `version_key`, the 5 non-guard supersede outcomes) and
`test_infoic_lookup.py` (`format_vpp`, key invariant) were verified by the same
wrong-input-fails / right-input-passes reasoning during authoring; their construction ties each
assertion directly to a named source-code branch (see the file contents), so a regression in
that branch necessarily flips the corresponding assertion.

## Decisions Made

- **Mutation guard count: followed the itemized tables (6), not the plan's rollup prose ("seven
  mutation guards").** Task 1's table lists exactly 4 anchors; Task 2's table lists exactly 2.
  The `<verification>` section's summary line appears to have miscounted its own itemized list.
  All must-haves and success criteria that reference specific outcomes (nine supersede
  scenarios, the anchor-exactly-once invariant, no `import build_db`, etc.) are met in full;
  only the "seven" figure in the rollup prose doesn't match the itemized total of 6.
- **`family_names` open question — resolved, not deferred as originally scoped.** The plan
  routed this to the SUMMARY as an open question because the function's docstring disagreed
  with its behavior. That disagreement was independently corrected in the working tree before
  this task started (a pre-existing uncommitted edit to `eprom_ledger.py`, left untouched here
  since it's outside this plan's file list) — the docstring now accurately says adding a chip
  can rename an existing family (a second family sharing a protocol forces the first to gain a
  pinout qualifier). Per instruction, `family_names` remains untested here; the remaining open
  question is a design one for the operator: whether families should be cited by a stable key
  rather than a name that can shift under a future chip addition.
- **Citation repair scope limited to insertion-displaced citations.** Both SKILL.md edits
  inserted 8 lines each before all existing prose. Six `.planning/` `file:LINE` citations that
  correctly pointed to content before this edit were repaired with the uniform +8 shift.
  Several other citations into both SKILL.md files (`devtest-triage/SKILL.md:375`,
  `:312-340`, `:310-345`, `:370-380`; `devtest-rootcause/SKILL.md:339`, `:333-345`) were found
  to already point past end-of-file or at unrelated content **before** this edit — pre-existing
  drift from an earlier SKILL.md content rewrite (the schema-2.0 voltage-field rewrite
  referenced in the file's own "Voltage sanity" section), unrelated to and out of scope for this
  test-coverage task. `.planning/graphs/GRAPH_REPORT.md:23359`'s citation is also stale but that
  file is machine-generated and explicitly never hand-edited (per its own directory's
  documentation); left for the next graph rebuild.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Reworded the no-CI prose to match the plan's own literal verify check**
- **Found during:** Task 3
- **Issue:** The plan's `<verify>` script for Task 3 does a case-sensitive substring check for
  lowercase `"nothing runs"`. My first draft of the prose capitalized "Nothing" at the sentence
  start ("Nothing runs those tests automatically...— this repository has no CI workflow; run
  them by hand..."), which would fail that literal check even though it satisfies the intent.
- **Fix:** Reworded to "Run them by hand after editing a script — nothing runs those tests
  automatically, since this repository has no CI workflow." (identical meaning, lowercase
  "nothing runs" substring present, same line count so no further citation shift).
- **Files modified:** `.claude/skills/devtest-triage/SKILL.md`, `.claude/skills/devtest-rootcause/SKILL.md`
- **Verification:** Re-ran the plan's literal Python verify snippet; passes.
- **Committed in:** `e5e4ed6f` (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Cosmetic wording fix to satisfy the plan's own literal verify script. No
scope creep, no behavior change.

## Issues Encountered

- The first attempt at a live RED demonstration on `eprom_ledger.py`'s Notes else-branch used a
  non-raw Python string in the demo script, so the `\n` inside the anchor was interpreted as an
  actual newline by Python before ever reaching `.replace()`, and the anchor silently failed to
  match (caught by an `assert old in s` check rather than corrupting the file). Fixed by using
  raw string literals (`r'...'`) for both the anchor and its replacement, which is also what the
  test file itself does for byte-exact anchor matching.
- **Near-miss: `git checkout --` on `eprom_ledger.py` discarded a pre-existing, uncommitted
  docstring fix that was already in the working tree at session start (the corrected
  `family_names` docstring — see Decisions).** After each live RED demonstration (mutating
  `eprom_ledger.py` in place to observe a real failure), I ran `git checkout --
  .../eprom_ledger.py` to revert my own temporary mutation. Since that file had never been
  `git add`ed by me or anyone in this session, the index still matched HEAD (the version
  *before* the operator's uncommitted docstring correction), so `git checkout --` restored the
  file to HEAD and silently discarded the uncommitted fix along with my mutation. Caught
  immediately afterward when the discovery-loop's `git status --short` output no longer showed
  `eprom_ledger.py` as modified. **Recovered in full**: reapplied the exact corrected docstring
  text from my own initial `Read` of the file (captured before any edits), then verified
  `git diff` against the restored file byte-for-byte matched the diff observed at session start
  (confirmed via matching `md5sum` of the diff output). No data was lost, but the sequence was a
  real close call — a lesson for future sessions: `git checkout --` on any file not already
  staged in the current session can silently erase pre-existing uncommitted work, since it
  restores from the index/HEAD rather than "undo my last edit." Reverting a self-made mutation
  should instead re-apply the known-good content directly (as the RED demos for
  `devtest_issues.py` effectively did, since that file had no prior uncommitted state to lose).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both skills now have a genuinely falsifiable regression net for their highest-risk
  functions (`supersedes()`'s outward-facing close decision, `render()`'s tracked-file rewrite,
  `VPP_MV`'s cross-repo drift potential). `diff_db.py` (excluded by design per the plan's
  objective) remains untested — it is reports-only and was deliberately out of scope.
- No blockers. The suite is ready to be run by hand after any future edit to
  `devtest_issues.py`, `eprom_ledger.py`, or `infoic_lookup.py`.

## Self-Check: PASSED

All 4 created test files and the SUMMARY.md exist on disk; all 3 task commit hashes
(`8ed5d4a1`, `0afbc99a`, `e5e4ed6f`) are present in `git log --oneline --all`.

---
*Phase: quick-260916-ess*
*Completed: 2026-09-16*
