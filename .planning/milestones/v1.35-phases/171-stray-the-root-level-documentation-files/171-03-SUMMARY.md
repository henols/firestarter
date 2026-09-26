---
phase: 171-stray-the-root-level-documentation-files
plan: 03
subsystem: docs
tags: [provenance, migration-table, honest01, markdown-tables]

# Dependency graph
requires:
  - phase: 171-stray-the-root-level-documentation-files
    plan: "171-02"
    provides: "things.md, SECURITY.md and autocomplete.md deleted from firestarter_app root, with verified recoverability at d56424e1979edf7245cffb9ec3111c0469f5b23f"
provides:
  - "The Shell-Completion main-table row in .planning/v1.35/MIGRATION-TABLE.md, closing the publish-then-record half of D-06"
  - "A new 3-column 'Removed without ever being published' section recording things.md and SECURITY.md, each with a recoverable git-show command"
  - "V-16 evidence proving honest01_claims.parse_migration_table still returns exactly 8 clean SHA-bearing rows"
  - "The Phase 171 out-of-scope ledger (eight items) so a future failure is not misattributed to this phase"
affects: [171-04-plan]

# Tech tracking
tech-stack:
  added: []
  patterns: ["append-only provenance-table edits verified via git diff --numstat", "3-column deletion-section shape that a never-reset single-header table parser absorbs harmlessly"]

key-files:
  created:
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-03-migration-table-parse.txt"
    - ".planning/phases/171-stray-the-root-level-documentation-files/evidence/171-03-out-of-scope-ledger.md"
  modified:
    - ".planning/v1.35/MIGRATION-TABLE.md"

key-decisions:
  - "Reworded the SECURITY.md 'What it was' cell to avoid the literal phrase 'security policy' (used 'the path GitHub surfaces under a repository's Security tab' instead), so the plan's own disclosure-phrase grep guard passes without weakening the factual content"
  - "New section inserted immediately before the '## Honesty note' heading, after the existing 'Retired from the wiki after the migration closed' section, mirroring its exact 3-column shape and recovery-command convention"
  - "Recovery commands carried as inline code inside the third cell only — never as a fifth column — to keep honest01_claims.parse_migration_table's never-reset single header from keying a Pre-deletion SHA cell on the new rows"

requirements-completed: []

coverage:
  - id: D1
    description: "autocomplete.md has a Phase 171 row in the main migration table naming its wiki page, rendered title and full pre-deletion SHA"
    requirement: "LEGACY-07"
    verification:
      - kind: other
        ref: ".planning/v1.35/MIGRATION-TABLE.md:20 — matches the exemplar shape byte-for-byte; grep confirmed in evidence/171-03-migration-table-parse.txt"
        status: pass
    human_judgment: false
  - id: D2
    description: "things.md and SECURITY.md each have a row in a new 3-column section for files removed without ever being published, naming what the file was, why it went, and the recovery command"
    requirement: "LEGACY-04, LEGACY-05"
    verification:
      - kind: other
        ref: ".planning/v1.35/MIGRATION-TABLE.md:68-80 (## Removed without ever being published)"
        status: pass
    human_judgment: false
  - id: D3
    description: "honest01_claims.parse_migration_table returns 8 SHA-bearing rows after the change, none of them a deletion row (V-16)"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "evidence/171-03-migration-table-parse.txt (rows with a SHA: 8; firestarter_app/autocomplete.md -> Shell-Completion 171; no things.md or SECURITY.md row)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The edit to MIGRATION-TABLE.md is append-only — zero deleted or modified existing lines, no comment added"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "git diff HEAD~1 --numstat -- .planning/v1.35/MIGRATION-TABLE.md -> 14 insertions, 0 deletions (task 1 commit 6e87db0b)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The eight known out-of-scope items are recorded so a future red run is not misattributed to Phase 171"
    requirement: "LEGACY-04, LEGACY-05, LEGACY-07"
    verification:
      - kind: other
        ref: "evidence/171-03-out-of-scope-ledger.md (8 items, each with its own anchor string)"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-09-01
status: complete
---

# Phase 171 Plan 03: Record the Migration Table Provenance Summary

**Appended the Shell-Completion main-table row and a new 3-column "Removed without ever being published" section to `.planning/v1.35/MIGRATION-TABLE.md`, then proved `honest01_claims.parse_migration_table` still parses cleanly to 8 rows and recorded the phase's eight out-of-scope items.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-09-01T09:46:00Z
- **Completed:** 2026-09-01T10:11:21Z
- **Tasks:** 2/2 executed, both auto
- **Files modified:** 1 modified (`.planning/v1.35/MIGRATION-TABLE.md`), 2 evidence files created

## Accomplishments

- Appended one main-table row for `autocomplete.md` -> `Shell-Completion` immediately after the `Protocol-ID` row, matching the six-column exemplar shape byte-for-byte, citing the full `d56424e1979edf7245cffb9ec3111c0469f5b23f` SHA
- Inserted a new `## Removed without ever being published` section immediately before the `## Honesty note` heading, mirroring the existing "Retired from the wiki" section's 3-column shape exactly (`| Source path | What it was | What happened |`)
- Recorded `things.md` (LEGACY-04, D-05) as seven lines / 265 bytes with no trailing newline — using C-7's corrected figure, not CONTEXT.md's "five" or the ROADMAP's "six" — with its recovery command as inline code inside the last cell
- Recorded `SECURITY.md` (LEGACY-05, D-01) with its true opening lines and the canonical meta-repo home that makes the deletion lossless, again with the recovery command as inline code
- Reworded one cell to avoid the literal phrase "security policy" so the plan's own disclosure-phrase grep guard (`report a vulnerability` / `security policy` / `responsible disclosure`) returns nothing, while still stating the factual GitHub-surface behavior
- Confirmed with `git diff --numstat` that the edit added 14 lines and deleted zero — the pre-existing `Protocol-Flags` / `Protocol-ID` drift at (now) lines 18-19 was left untouched, as CONTEXT.md's deferred list requires
- Ran the RESEARCH.md §C.9 `parse_migration_table` snippet: printed `rows with a SHA: 8` (V-16), including `firestarter_app/autocomplete.md -> Shell-Completion 171`, and confirmed no row's `Wiki page` field is `things.md` or `SECURITY.md` — the new 3-column section was absorbed and filtered out exactly as the existing retired section already is
- Wrote the eight-item out-of-scope ledger, each item anchored by its own grep-able string, covering the deferred `Protocol-Flags`/`Protocol-ID` drift, the `wiki-check.yml` `--wiki-dir` defect, the unregistered `wiki-check.yml` workflow (no CI covered this phase), the historical `RED-BASELINE.md` hit, the unrelated `build_db.py` modification, the gitignored `SOURCES.txt` false-positive cause, the stale `blob/main` copy, and the deferred Security-tab observation

## Task Commits

Each task was committed atomically:

1. **Task 1: Append the Shell-Completion main-table row and add the removed-never-published section** - `6e87db0b` (docs) — `.planning/v1.35/MIGRATION-TABLE.md` only, 14 insertions, 0 deletions
2. **Task 2: Prove honest01's parse is unharmed, and write the out-of-scope ledger** - `24c3297a` (docs) — both evidence files, 77 insertions

## Files Created/Modified

- `.planning/v1.35/MIGRATION-TABLE.md` - one main-table row appended (line 20) and a new `## Removed without ever being published` section inserted (heading now at line 68, table rows at lines 76-79, `## Honesty note` heading now at line 81); file is now 159 lines
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-03-migration-table-parse.txt` - full output of the §C.9 `parse_migration_table` snippet: 8 rows, `Shell-Completion` present, no deletion row leaked through
- `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-03-out-of-scope-ledger.md` - the eight recorded-not-fixed items with their measured facts, reasons, and owners

## Post-edit line numbers for future `.planning/` citations

Any later citation of `.planning/v1.35/MIGRATION-TABLE.md` should use these post-change numbers rather than the pre-edit ones quoted in `171-PATTERNS.md` (which cited the file at its pre-Task-1 145-line length):

- New main-table row (`Shell-Completion`): line 20
- `## Removed without ever being published` heading: line 68
- The two new deletion rows: lines 78-79
- `## Honesty note: HONEST-01 no longer applies to the surviving rewritten pages` heading: line 81
- File length after this plan: 159 lines

## Decisions Made

- Reworded the `SECURITY.md` "What it was" cell from "the path GitHub reads as a repository's security policy" to "the path GitHub surfaces under a repository's Security tab" — this is the only wording deviation from the plan's suggested prose, made to satisfy the plan's own acceptance criterion (`git grep -in "report a vulnerability\|security policy\|responsible disclosure"` must return nothing) without softening or omitting the underlying fact. Not a Rule 1-4 deviation — it is following the plan's own explicit prohibition to the letter where its suggested wording would have collided with its own verification.
- No other deviations. Both row shapes were built from the exact templates in `171-PATTERNS.md` §4 and the exact prose content specified in the plan's Task 1 action block.

## Deviations from Plan

### Auto-fixed Issues

None beyond the wording adjustment documented above under "Decisions Made" — that adjustment exists specifically to satisfy a verification the plan itself specifies (the disclosure-phrase grep), not to fix a bug, add missing functionality, or resolve a blocker. No Rule 1-4 classification applies.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** None — content and structure delivered exactly as specified; one cell's wording was adjusted in place to satisfy the plan's own literal-phrase guard.

## Issues Encountered

None.

## Known Facts for the Record

- **`things.md`'s line count is recorded as "seven lines"** in the new section, per C-7's correction — not CONTEXT.md's "five lines" nor the ROADMAP's "six lines". Verified absent from the new section: `five lines`, `5 lines`, `six lines`, `6 lines` all return zero matches.
- **The `min_lines: 160` artifact target in the plan's frontmatter was not exactly met** — the file measures 159 lines after this plan's edit (145 pre-edit + 14 inserted). This is a one-line discrepancy against the planner's estimate, not a content gap: every required row, section, heading and recovery command specified by the plan is present and verified. No padding was added to force the count, per the project's standing rule against inventing content.
- **LEGACY-04, LEGACY-05 and LEGACY-07 are NOT complete at this plan's close.** This plan discharges the provenance leg (D-06) of all three requirements — each file now has a recorded, recoverable disposition in `MIGRATION-TABLE.md`. The meta gitlink re-pin still lands in 171-04, which is where the requirement checkboxes are expected to flip. No requirement checkbox was touched by this plan.
- **No CI covered this phase.** `wiki-check.yml` is not registered with GitHub Actions on the default branch (out-of-scope ledger item 3); every check in this plan ran locally, and its output in the evidence directory is the only proof any of it ran.

## User Setup Required

None — no external service configuration required. This plan made only local git commits to the meta repository.

## Next Phase Readiness

- 171-04 is unblocked: the provenance record for all three files is complete and verified, `firestarter_app` HEAD (`c1416a6`, from 171-02) is ready to be re-pinned into the meta gitlink alongside Phase 170's previously-unpinned commits.
- No blockers. Pre-existing meta drift (`M .planning/config.json`, `M .planning/notes/dev-test-sequence-cost-model.md`, `M firestarter`, `M firestarter_app` gitlinks) was present before this plan started, is not this plan's work, and was left untouched — confirmed by `git status --short` after both task commits showing only the intended paths staged and committed.

---
*Phase: 171-stray-the-root-level-documentation-files*
*Completed: 2026-09-01*

## Self-Check: PASSED

- FOUND: `.planning/v1.35/MIGRATION-TABLE.md`
- FOUND: `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-03-migration-table-parse.txt`
- FOUND: `.planning/phases/171-stray-the-root-level-documentation-files/evidence/171-03-out-of-scope-ledger.md`
- FOUND: `.planning/phases/171-stray-the-root-level-documentation-files/171-03-SUMMARY.md`
- FOUND: commit `6e87db0b` (meta, .planning/v1.35/MIGRATION-TABLE.md)
- FOUND: commit `24c3297a` (meta, evidence files)
