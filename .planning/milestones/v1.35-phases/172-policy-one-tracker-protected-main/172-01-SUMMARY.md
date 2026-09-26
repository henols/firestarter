---
phase: 172-policy-one-tracker-protected-main
plan: 01
subsystem: docs
tags: [wiki, github-wiki, contributing, policy, migration-table, honest01]

# Dependency graph
requires:
  - phase: 171-stray-the-root-level-documentation-files
    provides: "the live 10-page wiki, MIGRATION-TABLE.md's provenance schema, and honest01_claims.parse_migration_table's em-dash NO_SHA_MARKER convention this plan reuses"
provides:
  - "the live `Contributing` wiki page — the single canonical statement of POLICY-01's three claims (one tracker, both sub-repos' Issues disabled, PRs route by changed code), gh#9's four-step cross-repo protocol, and D-04's one-sentence security non-claim"
  - "both navigation edits (`_Sidebar.md`, `Home.md`) making the page reachable and enumerated"
  - "the `Contributing` provenance row in `.planning/v1.35/MIGRATION-TABLE.md`, correctly excluded from the SHA-bearing count via the em-dash marker"
affects: [172-04, 172-08]

actuals:
  tokens: 800
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "authored-not-migrated provenance row: em-dash Source path AND Pre-deletion SHA, both copied byte-exact from an existing row rather than retyped, so honest01_claims.parse_migration_table's NO_SHA_MARKER filter excludes it"
    - "independent-clone re-verification: never trust the working clone that authored a wiki commit to prove the push landed — always re-clone into a fresh temp directory and re-run the same oracle"

key-files:
  created:
    - "Contributing.md (live firestarter_prom wiki, root)"
    - ".planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-wiki-links-prepush.txt"
    - ".planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-wiki-links-postpush-freshclone.txt"
    - ".planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-migration-table-parse.txt"
  modified:
    - "_Sidebar.md (live wiki)"
    - "Home.md (live wiki)"
    - ".planning/v1.35/MIGRATION-TABLE.md"

key-decisions:
  - "The em dash (U+2014) in the new Contributing row was copied character-for-character from the existing Home row (line 12) rather than typed, eliminating any risk of a look-alike hyphen or en-dash silently changing what honest01_claims.parse_migration_table counts."
  - "Task 3's re-verification used a brand-new `mktemp -d` clone, never the working clone at /tmp/gsd-172-wiki that authored the commit, per the plan's explicit instruction that a working clone cannot prove a push."

patterns-established:
  - "A wiki page with no doc/ source gets a Pre-deletion SHA of the em-dash NO_SHA_MARKER, not an empty cell, a hyphen-minus, or 'n/a' — any of those would silently change what the honest01 checker counts."

requirements-completed: [POLICY-01]

coverage:
  - id: D1
    description: "Contributing.md is live on the public firestarter_prom wiki with all three POLICY-01 statements, gh#9's four-step cross-repo protocol, and D-04's one-sentence security non-claim"
    requirement: "POLICY-01"
    verification:
      - kind: other
        ref: "python3 tools/wiki/wiki.py links --source-dir <fresh clone> (evidence/172-01-wiki-links-postpush-freshclone.txt)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both navigation edits (_Sidebar.md, Home.md) make Contributing reachable and enumerated"
    verification:
      - kind: other
        ref: "wiki.py links: OK: 11 pages, ... all listed in _Sidebar.md (evidence/172-01-wiki-links-postpush-freshclone.txt)"
        status: pass
    human_judgment: false
  - id: D3
    description: "MIGRATION-TABLE.md records Contributing's provenance as authored-not-migrated without disturbing the SHA-bearing row count"
    requirement: "POLICY-01"
    verification:
      - kind: other
        ref: "honest01_claims.parse_migration_table (evidence/172-01-migration-table-parse.txt) — rows with a SHA: 8, Contributing absent"
        status: pass
    human_judgment: false

duration: 3min
completed: 2026-09-01
status: complete
---

# Phase 172 Plan 01: Publish Contributing.md Summary

**The `Contributing` page is live as the eleventh page of the public `firestarter_prom` wiki, proven from an independent fresh clone, with its provenance recorded as authored-not-migrated in `MIGRATION-TABLE.md` without disturbing the SHA-bearing row count.**

## Performance

- **Duration:** ~3 min (this continuation session, Task 3 only — Task 1 authored the page and Task 2 was a human-action push checkpoint that spanned the wait for operator authorization)
- **Started:** 2026-09-01T18:11:00Z (Task 3 resume)
- **Completed:** 2026-09-01T18:14:37Z
- **Tasks:** 3 (all complete: 1 tracer, 1 checkpoint:human-action, 1 auto)
- **Files modified:** 6 total across the plan (3 live wiki files in Task 1; `.planning/v1.35/MIGRATION-TABLE.md` and 3 evidence files across Tasks 1 and 3)

## Accomplishments
- `Contributing.md` authored, gated locally with `wiki.py links` (`OK: 11 pages,`), committed in one wiki commit alongside both navigation edits, and pushed to the live public wiki with explicit operator authorization
- The push was re-verified from a brand-new independent `--depth 1` clone (never the authoring clone), confirming `Contributing.md` exists, `_Sidebar.md` lists it, `Home.md` links it, and `wiki.py links` exits 0 with `OK: 11 pages,`
- `.planning/v1.35/MIGRATION-TABLE.md` gained the `Contributing` provenance row (em-dash Source path and Pre-deletion SHA, copied byte-exact from the `Home` row) plus a short prose note explaining the page was authored from gh#9, not migrated from a deleted `doc/` file
- `honest01_claims.parse_migration_table` still returns exactly 8 SHA-bearing rows with `Contributing` correctly excluded, preserving Phase 171's assertion

## Task Commits

Each task was committed atomically:

1. **Task 1: Author Contributing.md, both nav edits, gate on wiki.py links** - `e2cebd04` (meta, docs) + wiki commit `dc07042` (local, not pushed at that point)
2. **Task 2: Push to the live public wiki** (`checkpoint:human-action`) - operator authorized ("you can do the push"); orchestrator ran `git -C /tmp/gsd-172-wiki push origin HEAD`, result `bf787fb..dc07042  HEAD -> master`, rc=0. No new commit hash (this task pushes an existing commit).
3. **Task 3: Re-verify from an independent fresh clone, record provenance** - `d6eb5aad` (meta, docs)

**Plan metadata:** pending (this commit)

## Files Created/Modified
- `Contributing.md` (live wiki) - the canonical Contributing page: where to report a problem, where to open a PR, cross-repo protocol, security reports
- `_Sidebar.md` (live wiki) - appended `- [Contributing](Contributing)` navigation bullet
- `Home.md` (live wiki) - appended `Contributing` bullet to the Reference list
- `.planning/v1.35/MIGRATION-TABLE.md` - added the `Contributing` provenance row and its authored-not-migrated prose note
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-wiki-links-prepush.txt` - Task 1's pre-push local gate output
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-wiki-links-postpush-freshclone.txt` - Task 3's independent post-push proof
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-migration-table-parse.txt` - Task 3's `parse_migration_table` oracle output (8 rows, Contributing excluded)

## Decisions Made
- Copied the em dash character from the existing `Home` row rather than typing it, eliminating risk of a look-alike character silently changing what `honest01_claims.py` counts as SHA-bearing.
- Used a brand-new `mktemp -d` clone for Task 3's re-verification rather than reusing `/tmp/gsd-172-wiki`, per the plan's explicit instruction — a working clone cannot prove a push landed.

## Deviations from Plan

### Observed authoring quirk (not a deviation, not auto-fixed)

Task 3's acceptance criteria list one check as `sed -n '21p' .planning/v1.35/MIGRATION-TABLE.md | grep -c $'—'` "returning 2". As literally written this command returns 1, because `grep -c` counts matching *lines* (0 or 1 for a single-line input), not occurrences — the intended check needed `grep -o $'—' | wc -l`, which does return 2 and confirms the row's two em dashes are both present and byte-identical to line 12's. This is a wording quirk in the plan's own acceptance-criteria text, not a defect in the authored row or in any gate that actually runs (the two `<verify><automated>` legs, which are the hard gates, do not contain this check and both passed). No source or plan file was altered to address it — flagging it here for anyone auditing this SUMMARY against the plan text.

None of Rules 1-4 applied to the implementation itself — plan executed exactly as written.

**Total deviations:** 0 auto-fixed. **Impact:** none — the row content and the mechanical gate that actually enforces it (parse_migration_table returning 8 rows) both verified correct.

## Self-Check: PASSED

- `Contributing.md`, `_Sidebar.md` (+1), `Home.md` (+1) — FOUND live on `firestarter_prom.wiki.git` (verified via independent fresh clone in Task 3)
- `.planning/v1.35/MIGRATION-TABLE.md` — FOUND, contains `| firestarter_prom | — | Contributing | Contributing | — | 172 |` at line 21
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-wiki-links-prepush.txt` — FOUND (13 lines, ends `exit 0`)
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-wiki-links-postpush-freshclone.txt` — FOUND (13 lines, ends `exit 0`)
- `.planning/phases/172-policy-one-tracker-protected-main/evidence/172-01-migration-table-parse.txt` — FOUND (10 lines, `rows with a SHA: 8`)
- Commit `e2cebd04` — FOUND in `git log --oneline --all`
- Commit `d6eb5aad` — FOUND in `git log --oneline --all`
- Plan-level `<verification>` re-run: `wiki.py links` against fresh clone exits 0 with `OK: 11 pages,` and `Contributing -> "Contributing"` — PASS; both evidence files non-empty and end `exit 0` — PASS; `parse_migration_table` returns 8 rows, `Contributing` absent — PASS; Task 1's wiki commit touched exactly three files — PASS (verified in Task 1); no HTML comment in `Contributing.md` or `MIGRATION-TABLE.md` — PASS (both `grep -c '<!--'` return 0)

## Issues Encountered
None.

## Next Phase Readiness
- Plan 172-04's three pointer files now have a real, live link target — `Contributing` is reachable and enumerated on the wiki.
- `ROADMAP.md` intentionally left untouched — owned by the orchestrator per this plan's dispatch instructions.

---
*Phase: 172-policy-one-tracker-protected-main*
*Completed: 2026-09-01*
