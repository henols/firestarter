---
phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg
plan: 01
subsystem: testing
tags: [wiki, provenance, checker, stdlib-python, argparse, migration-table, honesty-ledger]

requires:
  - phase: 172-policy-one-tracker-protected-main
    provides: "the three tools/wiki checkers (honest01_claims.py, honest02_truth.py, wiki.py, dispatch_mirror.py) and the wiki-check.yml job this checker will join in plan 173-06"
provides:
  - "tools/wiki/provenance_footers.py — a bidirectional, stdlib-only checker/generator asserting every migrated wiki page carries a footer matching MIGRATION-TABLE.md's own fields, and every live page has a table row"
  - "A corrected .planning/v1.35/MIGRATION-TABLE.md: Post-move edits column, Protocol-Flags/Protocol-ID relocated to the retired table, three previously-unrecorded live pages added as rows"
  - "Three evidence files proving the checker RED on real inputs before it is trusted (D-10's bar), and safe to publish against"
affects: [173-05-push-footers, 173-06-wiki-check-leg, 173-08-close-record]

actuals:
  tokens: 9600
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Bidirectional table/page checker: page-accounting (leg 2) gates footer-content checking (leg 1) — a table that does not correctly enumerate the live wiki cannot yet be trusted to name the right footer text either"
    - "Single footer_line() function shared by the generator and the checker so the two cannot disagree, mirroring honest02_truth.py's STAMP_RE convention"
    - "Planted-failure-first: five surgical plants against a scratch clone, each with its own distinct ERROR: word and exit code, restored byte-identically and re-verified GREEN before the checker is trusted"

key-files:
  created:
    - tools/wiki/provenance_footers.py
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-01-tracer-red-green.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-01-planted-failures.txt
    - .planning/phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/173-01-suite-regression.txt
  modified:
    - .planning/v1.35/MIGRATION-TABLE.md

key-decisions:
  - "Footer scope is the 6 provenance-bearing, live rows (per RESEARCH C-1), not the 12 CONTEXT.md named — no set of size 12 exists in the data"
  - "The checker gates leg 1 (footer content) on leg 2 (page accounting) being clean, so a table/wiki mismatch and a footer defect never produce overlapping noise in one run"
  - "Protocol-Flags and Protocol-ID moved to the retired table rather than restored — activation decision 4 is relocate-and-correct-only"
  - "Breaking-Changes, Chip-Database-Fields and Pin-Maps get an em-dash Moved-in cell rather than a guessed phase number — git log --follow puts their earliest wiki commit at 2026-08-31, but no .planning/ artifact names a phase for that commit, and Phase 170 has no plans or summaries to check against"

requirements-completed: [POLICY-05]

coverage:
  - id: D1
    description: "tools/wiki/provenance_footers.py exists, is stdlib-only, carries no comments beyond the shebang, and both checks/generates footers against MIGRATION-TABLE.md"
    requirement: POLICY-05
    verification:
      - kind: other
        ref: "tools/wiki/provenance_footers.py --help; AST import-set check; comment-count grep — all in evidence/173-01-tracer-red-green.txt and this plan's second/third verify legs"
        status: pass
    human_judgment: false
  - id: D2
    description: "The checker demonstrated RED on the table as it stood at HEAD (2 PAGE MISSING, 3 UNRECORDED PAGE) and RED on the corrected table against a footer-free clone (6 FOOTER MISSING), then GREEN after --emit"
    requirement: POLICY-05
    verification:
      - kind: integration
        ref: "evidence/173-01-tracer-red-green.txt (live wiki clone, both directions)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Five named failures each planted, observed RED with a distinct ERROR: word and exit code, restored byte-identically, and re-verified GREEN"
    requirement: POLICY-05
    verification:
      - kind: integration
        ref: "evidence/173-01-planted-failures.txt (scratch clone + scratch table, live wiki never touched)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The six footers do not break any of the three pre-existing tools/wiki checkers, and honest01_claims.parse_migration_table returns exactly the 6 corrected footer-eligible rows"
    requirement: POLICY-05
    verification:
      - kind: integration
        ref: "evidence/173-01-suite-regression.txt (fresh wiki + both sub-repo clones at the milestone branch)"
        status: pass
    human_judgment: false

duration: 27min
completed: 2026-09-02
status: complete
---

# Phase 173 Plan 01: Provenance-Footer Checker Summary

**A bidirectional stdlib-only checker (`tools/wiki/provenance_footers.py`) that generates and verifies per-page wiki provenance footers from a corrected `MIGRATION-TABLE.md`, demonstrated RED on real inputs in both directions before being trusted, and proven safe against all three pre-existing `tools/wiki` checkers.**

## Performance

- **Duration:** ~27 min
- **Started:** 2026-09-02T13:34:17Z
- **Completed:** 2026-09-02T14:01:18Z
- **Tasks:** 3
- **Files modified:** 6 (2 source/data files, 3 evidence files, 1 plan-verify bug fix)

## Accomplishments
- Built `tools/wiki/provenance_footers.py`: `parse_tables` correctly resets the header per table (fixing the accident `honest01_claims.py` carries), `footer_eligible_rows`/`footer_line` are the single source both the generator and checker read, `check_page_accounting` gates `check_footers` so a table/wiki mismatch and a footer-content defect never arrive as one indistinguishable red, and a `MIN_FOOTER_ROWS` vacuity floor returns exit 2 rather than 0 on a degenerate table.
- Corrected `.planning/v1.35/MIGRATION-TABLE.md`: added the `Post-move edits` column so no footer claims unchanged content on a rewritten page, moved `Protocol-Flags`/`Protocol-ID` to the retired table (the two stale rows D-10 predicted), and added rows for the three live pages the table never recorded (`Breaking-Changes`, `Chip-Database-Fields`, `Pin-Maps` — RESEARCH C-2's undiscovered direction).
- Watched the checker fail six distinct ways on real inputs before trusting it: 2 `PAGE MISSING` + 3 `UNRECORDED PAGE` on the table as it stood at HEAD, 6 `FOOTER MISSING` on the corrected table against a footer-free clone, then five planted failures (`FOOTER DRIFTED`, `FOOTER MISSING`, `UNRECORDED PAGE`, exit-2 vacuity, `UNSAFE ROW` path-traversal containment) each restored byte-identically to GREEN.
- Proved the six footers are safe to publish: all three pre-existing `tools/wiki` checkers plus the new one all exit 0 against one fresh clone, with `honest02_truth.py` leg 1 unmoved at 5 matched/0 missing (RESEARCH Pitfall 2's warning sign did not fire).

## Task Commits

Each task was committed atomically:

1. **Task 1: One row end to end** - `ec4a4636` (feat)
2. **Task 2: Plant five named failures** - `9c31e08f` (test)
3. **Task 3: Prove the six footers break none of the three checkers** - `50210880` (test)

**Plan metadata:** (this commit)

## Files Created/Modified
- `tools/wiki/provenance_footers.py` - the bidirectional checker/generator (created)
- `.planning/v1.35/MIGRATION-TABLE.md` - Post-move edits column, retired-table move, three new rows (modified)
- `.planning/phases/173-.../evidence/173-01-tracer-red-green.txt` - Task 1's RED/RED/GREEN sequence
- `.planning/phases/173-.../evidence/173-01-planted-failures.txt` - Task 2's five planted failures
- `.planning/phases/173-.../evidence/173-01-suite-regression.txt` - Task 3's four-checker regression proof
- `.planning/phases/173-.../173-01-PLAN.md` - two verify-script bug fixes (see Deviations)

## Decisions Made
- Footer scope fixed at the 6 provenance-bearing, live rows per RESEARCH C-1 — CONTEXT.md's "twelve" and "21 data rows" were superseded before this plan started and were never used.
- `check_page_accounting` runs before `check_footers`, and `main()` skips footer-content checking entirely when accounting already fails — this is what makes the HEAD-table run report zero `FOOTER MISSING` (all six real rows still lack footers) while the corrected-table run reports exactly six, matching the plan's own machine-checked counts.
- Plant 5's path-traversal row is appended to the scratch table rather than substituted for an existing row, so it does not orphan a legitimate page's accounting entry and produce a spurious second failure.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a plan-authored idempotence check that could never read `porcelain=0`**
- **Found during:** Task 1 (the end-to-end tracer run)
- **Issue:** The plan's verify script ran `--emit` twice against the same freshly-cloned wiki with no commit between the two calls, then asserted `git status --porcelain` was empty. Since the wiki clone's own HEAD commit never carries the six generated footers, any successful `--emit` leaves those six files diffing against HEAD regardless of how many times the (idempotent) call is repeated — the check was measuring "did any emit ever run", not "was the second emit a no-op".
- **Fix:** Inserted a scratch-clone-only checkpoint commit (`git add -A && git commit`, throwaway identity) between the two `--emit` invocations in the plan's `<verify>` block, so the second call's idempotence is measured against the state the first call actually produced.
- **Files modified:** `.planning/phases/173-.../173-01-PLAN.md` (Task 1's `<verify>` block)
- **Verification:** Re-ran the full compound verify assertion; `porcelain=0` now appears and every other assertion in the same leg still passes.
- **Committed in:** `ec4a4636` (Task 1 commit)

**2. [Rule 1 - Bug] Fixed an undercounted `OK:` line assertion in Task 3's verify script**
- **Found during:** Task 3 (the four-checker regression proof)
- **Issue:** The verify script asserted exactly four `^OK: ` lines (one per pre-existing checker plus the new one), but Task 1's own `--emit` spec mandates the emit setup step print its own `OK: N footers written.` line — a fifth, legitimate `OK:` line that a correct implementation always produces.
- **Fix:** Corrected the assertion from `-eq 4` to `-eq 5`, and updated the matching `fails_when` prose and the task's `acceptance_criteria` bullet for consistency.
- **Files modified:** `.planning/phases/173-.../173-01-PLAN.md` (Task 3's `<verify>` and `<acceptance_criteria>`)
- **Verification:** Re-ran the full compound verify assertion; all eight sub-checks pass.
- **Committed in:** `50210880` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs in the plan's own machine-checked verify scripts; neither changed what property was being tested, only how the count was computed).
**Impact on plan:** Both fixes were necessary for the plan's own `<verify>` blocks to be satisfiable at all — the checker's behavior was correct in both cases; the assertions were undercounting. No scope creep, no change to `provenance_footers.py` or `MIGRATION-TABLE.md` beyond what Task 1's action text specified.

## Known Stubs
None.

## Issues Encountered
- An initial `sed` insertion for Plant 5 (path-traversal row) used `\|` inside a default (BRE) `sed -i` address, which GNU sed interprets as alternation rather than a literal pipe — it matched almost every line in the scratch table and corrupted it, producing a spurious "main table not found" error. Replaced with a small inline Python script for that one insertion; no other plant used `sed` for structural table edits.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `tools/wiki/provenance_footers.py` and the corrected `MIGRATION-TABLE.md` are ready for plan 173-05 (push the six footers to the live wiki) and plan 173-06 (register the checker as a `wiki-check.yml` leg).
- `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` are provably untouched by this plan — verified with `git diff --stat` against both `HEAD~1` (immediately prior) and the pre-session baseline `aa7e665a`, both empty. POLICY-04 and POLICY-05 remain unmarked in `REQUIREMENTS.md`, as required — POLICY-05 is completed by this plan's evidence but the checkbox flip is plan 173-09's job, after the closing sweep.
- No blockers for the next plan in this phase.

## Self-Check: PASSED

All created files verified present on disk; all three task commit hashes (`ec4a4636`, `9c31e08f`, `50210880`) verified in `git log`.

---
*Phase: 173-close-beta-cut-under-protection-close-procedure-honesty-ledg*
*Completed: 2026-09-02*
