---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 01
subsystem: docs
tags: [git, wiki, migration-table, honest01, sub-repo-branching]

requires: []
provides:
  - "gsd/v1.35-documentation-consolidation-wiki-migration branch in firestarter (at a218b4f5) and firestarter_app (at d56424e1)"
  - ".planning/v1.35/MIGRATION-TABLE.md with all 12 page names, titles and pre-deletion SHAs, plus the deferred PY32F071 SHA"
  - "evidence/oracle-readable.txt proving the HONEST-01 git-show oracle resolves for all 13 rows"
affects: [168-02, 168-03, "later 168 plans that delete doc/ or push wiki pages"]

tech-stack:
  added: []
  patterns: ["git show <sha>:doc/<file> as a zero-duplication pre-deletion content oracle (D-02)"]

key-files:
  created:
    - .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/oracle-readable.txt
  modified:
    - .planning/v1.35/MIGRATION-TABLE.md

key-decisions:
  - "Branch base settled by operator: fork-from-current-head (firestarter a218b4f5, firestarter_app d56424e1) — not beta, to preserve every measured line number in 168-RESEARCH.md"
  - "chore/strip-provenance-comments left untouched at d56424e1 — the new v1.35 branch was created from it, not by moving it"
  - "Hyphen hazards resolved by rewording titles: AT28C04-Adapter (no hyphen needed), SRAM-and-NVRAM-Behavior (slash is illegal under check_page_names)"
  - "How-This-Wiki-Is-Published renamed to How-To-Edit-This-Wiki per D-21 — old title asserted a publishing model that no longer exists"
  - "MIGRATION-TABLE.md header prose rewritten to remove all publish-path claims — D-20 deleted wiki.py publish"

patterns-established:
  - "Pattern: irrecoverable oracle facts (a pre-deletion SHA) are recorded and proven-readable in the same plan, before any dependent deletion happens in a later plan"

requirements-completed: [MIGRATE-01, HONEST-01]

coverage:
  - id: D1
    description: "v1.35 working branches created in both sub-repos at the operator-selected base (fork-from-current-head), with the app's prior branch left unmoved"
    requirement: "MIGRATE-01"
    verification:
      - kind: other
        ref: "git -C firestarter rev-parse --abbrev-ref HEAD; git -C firestarter_app rev-parse --abbrev-ref HEAD; git -C firestarter_app rev-parse --verify chore/strip-provenance-comments"
        status: pass
    human_judgment: false
  - id: D2
    description: "All 12 migrating doc files have a wiki page name, rendered title and 40-char pre-deletion SHA in MIGRATION-TABLE.md; hyphen hazards resolved; deferred PY32F071 file also has a recorded SHA"
    requirement: "HONEST-01"
    verification:
      - kind: other
        ref: "grep -c 'TBD' .planning/v1.35/MIGRATION-TABLE.md (=0); grep -cE '^\\| firestarter(_app)? \\|' (=12); grep -oE '[0-9a-f]{40}' count on those rows (=12)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The git-show oracle is proven readable for all 13 rows (12 migrating + 1 deferred) with non-zero byte counts, and Programming-Protocols pins at the measured 49560 bytes"
    requirement: "HONEST-01"
    verification:
      - kind: other
        ref: ".planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/oracle-readable.txt (13 lines, all >0, Programming-Protocols=49560)"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 01: Sub-repo v1.35 Branches and the HONEST-01 Pre-Deletion Oracle Summary

**Created the v1.35 working branches in both sub-repos at the operator-decided base, then turned `.planning/v1.35/MIGRATION-TABLE.md` into the phase's load-bearing record — all 12 page names/titles/SHAs filled, plus a proven-readable oracle for all 13 rows (12 migrating + 1 deferred) before any `doc/` file is deleted anywhere.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-31T07:38:45Z
- **Completed:** 2026-08-31T07:42:16Z
- **Tasks:** 3 completed (Task 1 checkpoint:decision — pre-answered by operator; Task 2, Task 3 — auto)
- **Files modified:** 2 (1 created)

## Accomplishments
- Created `gsd/v1.35-documentation-consolidation-wiki-migration` in `firestarter` (base `a218b4f5273d14f0abd796b21ac104792de01603`, was detached HEAD) and `firestarter_app` (base `d56424e1979edf7245cffb9ec3111c0469f5b23f`, was on `chore/strip-provenance-comments`) — no commits made in either sub-repo for this task, branch-ref creation only, both trees left `porcelain`-clean
- Filled `.planning/v1.35/MIGRATION-TABLE.md`'s 12 `TBD` rows with page names, rendered titles, and 40-character pre-deletion SHAs; added the `Pre-deletion SHA` column
- Recorded a pre-deletion SHA for the deferred `PY32F071-FIRMWARE-INSTALL.md` file so "deferred" cannot silently become "lost" when its directory is deleted later in the phase
- Proved the HONEST-01 `git show <sha>:<path>` oracle resolves to non-empty content for all 13 rows, capturing byte counts as evidence; pinned `Programming-Protocols` at the measured 49560 bytes as a non-vacuity control
- Repaired the false publish-path prose at the top of `MIGRATION-TABLE.md` (no publish subcommand exists after D-20) without breaking the hyphen-hazard or deferred sections

## Task Commits

Task 1 (branch creation) produced no commit — it is a branch-ref-only action in the sub-repos per the plan's `commits_land_in` field, and `git status --porcelain` was empty in both after checkout, so there was nothing to stage.

1. **Task 2: Fill the 12 page names, rendered titles and pre-deletion SHAs** - `d10bd4b7` (feat)
2. **Task 3: Prove the oracle reads, and repair the false publish prose** - `1595d81b` (test)

_No plan-metadata commit yet — this SUMMARY and STATE/ROADMAP updates follow in the final commit._

## Files Created/Modified
- `.planning/v1.35/MIGRATION-TABLE.md` - added `Pre-deletion SHA` column; filled all 12 rows with page name/title/SHA; resolved both hyphen hazards in prose; renamed `How-This-Wiki-Is-Published` row to `How-To-Edit-This-Wiki`; added deferred-file SHA; repaired header prose to remove publish-path claims
- `.planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/oracle-readable.txt` - 13 `<page> <bytes>` lines proving the git-show oracle resolves for every migrating file plus the deferred one

## Decisions Made
- **Branch base = fork-from-current-head** (operator-answered, recorded in `168-01-PLAN.md`'s `<decision-answered>` block dated 2026-08-31). Both sub-repo branches created at their current working HEADs rather than `beta`, preserving every measured fact in `168-RESEARCH.md`. Cost accepted: v1.35 cannot merge to `beta` before fw#56/app#54 land.
- `chore/strip-provenance-comments` explicitly left unmoved at `d56424e1979edf7245cffb9ec3111c0469f5b23f` — verified via `git -C firestarter_app rev-parse --verify chore/strip-provenance-comments` after branch creation.
- Hyphen hazards resolved per plan instruction: `AT28C04-Adapter` (title needs no hyphen at all) and `SRAM-and-NVRAM-Behavior` (the natural "SRAM/NVRAM" is illegal under `check_page_names`, which rejects `/`).
- `How-This-Wiki-Is-Published` → `How-To-Edit-This-Wiki` per D-21, recorded in the table's prose along with its one-known-inbound-link cost (`Home.md:5`, rewritten in the same wiki commit by a later plan).
- MIGRATION-TABLE.md header prose rewritten to avoid the literal word "publish" in the scanned region (lines 1-8) while still accurately describing D-19's clone-commit-push mechanism, keeping the hyphen-hazard and deferred sections' legitimate discussion of what is/isn't published untouched.

## Deviations from Plan

None - plan executed exactly as written. Task 1's checkpoint was pre-answered by the operator and its `<action>` executed verbatim; Tasks 2 and 3 matched their `<action>` blocks with no additional bugs, missing functionality, or blocking issues encountered.

## Issues Encountered

None. The initial prose rewrite in Task 2 still contained the word "publish" (in "no publish subcommand"), which would have failed Task 3's `sed -n '1,8p' | grep -qi 'publish'` gate — caught and reworded during Task 3 before the check was run, so no failing verification was ever committed.

## User Setup Required

None - no external service configuration required. No push to any remote was made (Task 1 explicitly forbids it; the first sub-repo push happens with the first commit in a later wave).

## Next Phase Readiness

- Both sub-repos are on the named v1.35 branch, unpushed, ready for later plans in this phase to commit `doc/` deletions and repair work directly onto them.
- The HONEST-01 oracle is proven readable for all 13 rows — later plans that delete `firestarter/doc/` and `firestarter_app/doc/` can proceed knowing the pre-deletion content is recoverable via the recorded SHAs.
- `MIGRATION-TABLE.md` is now load-bearing (no more `TBD` cells) and can be read by later plans, the Backlog 999.9 rename sweep, and a future HONEST-01 claim-comparison checker.
- No blockers identified for subsequent plans in this phase.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: .planning/v1.35/MIGRATION-TABLE.md
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/evidence/oracle-readable.txt
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-01-SUMMARY.md
- FOUND commit: d10bd4b7
- FOUND commit: 1595d81b
- FOUND commit: 80d27fb7
