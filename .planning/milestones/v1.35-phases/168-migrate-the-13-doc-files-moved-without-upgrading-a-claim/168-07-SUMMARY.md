---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 07
subsystem: docs
tags: [firmware, claude-md, wiki-migration, link-repair, comment-removal]

requires:
  - phase: 168-01
    provides: ".planning/v1.35/MIGRATION-TABLE.md with page names, rendered titles and the pre-deletion SHA (a218b4f5) for the three firmware doc/ files"
  - phase: 168-04
    provides: "the H-1 collection hazard severed — firestarter_app's test suite no longer aborts at collection when firestarter/doc/ is absent"
  - phase: 168-05
    provides: "the three firmware doc/ files published live on firestarter_prom.wiki.git (Programming-Protocols, Shield-Revisions, AT28C04-Adapter)"
provides:
  - "firestarter/doc/ deleted (MIGRATE-02) — 3 files, 844 lines, pre-deletion SHA a218b4f5 confirmed readable before and after the delete"
  - "firestarter/CLAUDE.md's 5 doc/ references repointed to wiki page titles, both lockstep-maintenance rules preserved word-for-word (MIGRATE-04, D-16)"
  - "firestarter/README.md's 3 doc/ markdown links rewritten as full firestarter_prom.wiki URLs (MIGRATE-04, D-13/D-17 README exception)"
  - "the proto_constants.h provenance comment deleted, not repointed (D-15, operator no-comments rule)"
  - "the test_loop_eprom_v131.cpp block comment citing doc/SHIELD-REVISIONS.md and .planning/v1.7-SHIELD-REVS.md deleted; the contradictory jumper-identity finding it recorded is preserved below instead"
affects: ["168-09 (deletes firestarter_app/doc/ next; this plan proves the analogous firmware-side deletion pattern is safe)", "168-13 (closing-phase gates read this plan's repair surface as part of criterion 2)"]

tech-stack:
  added: []
  patterns: ["wiki page title (not URL) for every non-README reference, per D-13 — Backlog 999.9 renames all three repositories and would invalidate a URL silently; a title is not a link and satisfies criterion 2 trivially", "full wiki URL permitted only in the two sub-repo READMEs, which Phases 169/170 rewrite and 999.9 re-sweeps anyway"]

key-files:
  created: []
  modified:
    - firestarter/CLAUDE.md
    - firestarter/README.md
    - firestarter/include/proto_constants.h
    - firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
  # deleted (not a Write/Edit modification, listed for completeness):
  #   firestarter/doc/PROTOCOLS.md
  #   firestarter/doc/SHIELD-REVISIONS.md
  #   firestarter/doc/AT28C04-ADAPTER.md

key-decisions:
  - "Re-confirmed the H-1 severance precondition before deleting: grep across firestarter_app/tests/ for any remaining module-scope resolution of a firmware doc/ path found none — the two textual hits (test_diff_db_gate.py, test_build_db_inclusion.py) are comments naming the D-14 repointing, not fw_path() calls, and the five files resolving `\"doc\"` all key off firestarter_app's OWN doc/ directory (168-09's territory), not the firmware sibling's."
  - "test_loop_eprom_v131.cpp:1739-1763's entire block comment was deleted, not just the sentence citing doc/SHIELD-REVISIONS.md — the plan's read_first names it as one indivisible block comment and D-15's no-comments reasoning applies to the whole block, matching the header-file precedent (delete the block wholesale, do not surgically edit a comment down to a smaller comment). The comment's substantive content (the D-01/D-02/D-04 finding that the drop bit now survives set_address() on Rev-2-class hardware, and the contradictory jumper-identity open finding) is preserved in this SUMMARY's 'Open Finding Carried Forward' section instead of in source."
  - "Both firestarter/CLAUDE.md lockstep rules (:204 shield-revision subset-clone obligation, :206 ADC-band-table mirror obligation) were repointed to name the Shield Revisions wiki page in place of the doc/ path, with every section reference, table name and 'update in lockstep' / 'same commit-pair' obligation left character-for-character otherwise unchanged."
  - "Left requirements-completed empty for MIGRATE-02 and MIGRATE-04 despite both being declared in this plan's frontmatter -- firestarter_app/doc/ still has 10 files on disk (confirmed by ls) and 5 firestarter_app test modules still resolve it at module scope, so neither requirement's both-repos condition is actually true yet. Per project precedent (168-04-SUMMARY.md's identical decision), marking either complete here would repeat a known failure mode of executors prematurely closing multi-plan requirements; both are 168-09's to close. LEGACY-06 was already marked Complete in REQUIREMENTS.md by plan 168-05, before this plan ran, so no action was needed here either."

requirements-completed: []

coverage:
  - id: D1
    description: "firestarter/CLAUDE.md's five doc/ references repointed to wiki page titles (Programming Protocols x3, Shield Revisions x2); both lockstep-maintenance rules survive with every section name and obligation intact"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "grep -cE '(^|[^A-Za-z])doc/[A-Za-z0-9_.-]+\\.md' firestarter/CLAUDE.md -> 0; grep -c 'Shield Revisions' -> 2; grep -c 'Programming Protocols' -> 3; grep -c 'lockstep' -> 2 (unchanged from before this task, confirmed against HEAD~1); grep -c 'https://' -> 0 (unchanged)"
        status: pass
    human_judgment: false
  - id: D2
    description: "firestarter/README.md's three doc/ markdown links rewritten as full firestarter_prom.wiki URLs; proto_constants.h's provenance comment deleted (deletions only, #define lines untouched); test_loop_eprom_v131.cpp's doc-citing block comment deleted; zero comment markers added across both source files"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "grep -cE '(^|[^A-Za-z])doc/' README.md/proto_constants.h/test_loop_eprom_v131.cpp -> 0 each; grep -c 'firestarter_prom/wiki/' README.md -> 3; grep -c PROTO_FLASH_5V_PAGE proto_constants.h -> 1 (unchanged); git diff -U0 -- include/proto_constants.h test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp | grep '^+' | grep -vE '^\\+\\+\\+' | grep -cE '^\\+\\s*(//|/\\*|\\*)' -> 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "firestarter/doc/ deleted (3 files); pre-deletion SHA still resolves after the delete; repair sweep finds only the 3 named D-18 historical exclusions; firmware builds and native tests pass; the app suite still collects/passes under the real deletion"
    requirement: "MIGRATE-02"
    verification:
      - kind: other
        ref: "git show a218b4f5...:doc/PROTOCOLS.md | wc -c -> 49560 (both before and after the git rm); git grep -lE doc/... -- . -> exactly platform/py32f071/FLASH-PATH-AND-PCB.md, test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md, tests/golden/eprom_params_citations.json"
        status: pass
      - kind: integration
        ref: "pio run -e uno -> SUCCESS (RAM 70.0%, Flash 70.1%); pio test -e native -> 184 test cases succeeded"
        status: pass
      - kind: integration
        ref: "cd firestarter_app && FIRESTARTER_FW_ROOT=/workspaces/firestarter python -m pytest tests/ -o addopts='' -q --collect-only -> 1972 tests collected, no abort (matches 168-04's proven baseline)"
        status: pass
    human_judgment: false

duration: ~35min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 07: Delete firestarter/doc/ and Repair Every Reference Summary

**Deleted `firestarter/doc/` (3 files, 844 lines) after re-confirming the H-1 severance precondition, repointed `CLAUDE.md`'s five references to wiki page titles while preserving both lockstep-maintenance rules word-for-word, rewrote `README.md`'s three links as full wiki URLs, and deleted two source comments (a header provenance block and a test block comment) rather than repointing them, per the operator's no-comments rule.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-31
- **Tasks:** 3 completed (all `type="auto"`)
- **Files modified:** 4 tracked-file edits; 3 files deleted

## Accomplishments

- Repointed all 5 `firestarter/doc/` references in `CLAUDE.md` to wiki page titles (`Programming Protocols`, `Shield Revisions`), never a URL — per D-13, because Backlog 999.9 renames all three repositories and a URL written here would break silently. Both lockstep-maintenance rules survive with every section name (inventory §1, capability matrix §6, alias table §7, ADC band table §9 at `:204`; the ADC-band-defines mirror obligation at `:206`) and their "update in lockstep" / "same commit-pair" obligations unchanged in wording. `lockstep` occurrence count (2) and `https://` occurrence count (0) confirmed unchanged from the pre-task state.
- Rewrote `README.md`'s three `doc/` markdown links (`:127`, `:137-138`, `:144`) as full `https://github.com/henols/firestarter_prom/wiki/<Page-Name>` URLs — the one place D-13 permits a URL, because Phases 169/170 rewrite both READMEs and Backlog 999.9 re-sweeps them anyway. Kept all section references (§1.6, §§1.3-1.5) and the shield-revision enumeration.
- Deleted `include/proto_constants.h:11-16`'s provenance comment block (citing `firestarter/doc/PROTOCOLS.md` and a commit hash) outright, per D-15 and the operator's no-comments rule — not repointed. The `#define` lines are byte-for-byte untouched; `git diff` on this file shows deletions only.
- Deleted `test_loop_eprom_v131.cpp:1739-1763`'s block comment in full. This site appeared in neither the phase context's repair list nor its exclusion list; the plan decided it here under D-15's reasoning (see Open Finding Carried Forward below for what the comment recorded).
- Re-confirmed the H-1 severance precondition (168-04) still holds before deleting: no remaining module-scope `fw_path("doc", ...)` call resolves a firmware `doc/` path in `firestarter_app/tests/`. The two textual hits found are comments in `test_diff_db_gate.py` and `test_build_db_inclusion.py` describing the D-14 repointing, not import-time resolutions; the five files that do resolve a `"doc"` path all key off `firestarter_app`'s own `doc/` directory (`_FA_DIR` / `_APP_DIR`), which is 168-09's territory, not this plan's.
- Confirmed the pre-deletion SHA (`a218b4f5273d14f0abd796b21ac104792de01603`, recorded in `.planning/v1.35/MIGRATION-TABLE.md`) resolves to 49560 bytes for `PROTOCOLS.md` — matching the plan's stated oracle — both immediately before and immediately after `git rm -r doc/`.
- Deleted `firestarter/doc/` (`PROTOCOLS.md`, `SHIELD-REVISIONS.md`, `AT28C04-ADAPTER.md`) with `git rm -r`. The firmware repair sweep (`git grep -lE '(^|[^A-Za-z])doc/[A-Za-z0-9_.-]+\.md' -- .`) afterward lists exactly the three D-18 historical exclusions and nothing else: `platform/py32f071/FLASH-PATH-AND-PCB.md`, `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`, `tests/golden/eprom_params_citations.json`.
- Confirmed `pio run -e uno` (SUCCESS, RAM 70.0%/Flash 70.1%) and `pio test -e native` (184 test cases succeeded) both stayed green with `doc/` gone.
- Re-ran the H-1 proof against the real, now-doc-less `firestarter/` checkout (not a scratch clone this time — the real deletion): `firestarter_app`'s suite collects 1972 tests with no abort, matching 168-04's measured baseline exactly.

## Task Commits

1. **Task 1: Repair CLAUDE.md's five references, preserving both lockstep rules** - `d81281d` (docs, firestarter)
2. **Task 2: Repair the README links and delete the two source comment blocks** - `57898e2` (docs, firestarter)
3. **Task 3: Delete the doc directory and prove the firmware is unaffected** - `bf3a4e4` (chore, firestarter)

## Files Created/Modified

- `firestarter/CLAUDE.md` - 5 `doc/` references repointed to wiki page titles; both lockstep rules preserved
- `firestarter/README.md` - 3 `doc/` markdown links rewritten as full wiki URLs
- `firestarter/include/proto_constants.h` - provenance comment block (11-16) deleted; `#define`s untouched
- `firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp` - doc-citing block comment (1739-1763) deleted
- `firestarter/doc/PROTOCOLS.md` - **deleted** (556 lines; content live on the wiki as `Programming-Protocols` since 168-05)
- `firestarter/doc/SHIELD-REVISIONS.md` - **deleted** (128 lines; content live on the wiki as `Shield-Revisions` since 168-05)
- `firestarter/doc/AT28C04-ADAPTER.md` - **deleted** (160 lines; content live on the wiki as `AT28C04-Adapter` since 168-05)

## Open Finding Carried Forward (from the deleted test_loop_eprom_v131.cpp comment)

The deleted comment at `test_loop_eprom_v131.cpp:1739-1763` recorded two things, preserved here rather than in source:

1. **The D-01/D-02/D-04 finding it superseded a prior, opposite reading of:** Plan 142-02 revision-gated `mem_util_calculate_top_address_register`'s preserve mask so `CTRL_VPP_VPE_DROP_ENABLE` now **survives** this block's every `set_address()` call on Rev-2-class hardware — the inverse of what the test case asserted before Phase 142. Plan 142-04 then removed `eprom_write_execute`'s explicit `pins>=32` clear, which is what makes that survival observable in the strobe stream at all.
2. **An open, unresolved finding:** the drop bit is a VPP *level* selector (VPE dropped through the resistor to the ~13V VPP level), never a route — pin-1 VPP routing on a 32-pin part is a separate, physical decision made with a jumper. The comment named no jumper designator and asserted no net, and stated that **this project documents that jumper's identity two contradictory ways** — once in `doc/SHIELD-REVISIONS.md` (now the `Shield Revisions` wiki page) and once in `.planning/v1.7-SHIELD-REVS.md` — an open finding, not resolved by this plan or by Phase 142. Whoever next touches the 32-pin VPP-routing jumper documentation should reconcile these two contradictory sources; this plan only relocates the finding out of source, it does not resolve it.

## Decisions Made

- Both `firestarter/CLAUDE.md` lockstep rules repointed to the `Shield Revisions` wiki page title rather than a URL, with every section name and obligation wording left otherwise unchanged — see key-decisions above.
- `test_loop_eprom_v131.cpp`'s entire block comment (not just the doc-citing sentence) deleted as one unit, matching the header-comment precedent — see key-decisions above.
- H-1 severance re-verified as a precondition before the delete, per the plan's critical-context instruction, rather than trusted from 168-04's prior proof alone.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None.

## Next Phase Readiness

- `firestarter/doc/` no longer exists; the firmware repository points nobody at a path beneath it outside the three named D-18 historical exclusions.
- Both shield-revision lockstep-maintenance rules are intact and repointed — a future edit to `rurp_pinout.h`'s ADC band defines or to the meta-repo's shield-revision investigation document still has a live, discoverable obligation pointing at the `Shield Revisions` wiki page.
- Firmware builds (`pio run -e uno`) and native tests (`pio test -e native`, 184 cases) are unaffected.
- `firestarter_app`'s test suite collects and runs cleanly (1972 tests) against the real, now-doc-less firmware sibling — the H-1 hazard 168-04 severed holds under the actual deletion, not just a scratch-clone rehearsal.
- `firestarter_app/doc/` (10 files including the deferred `PY32F071-FIRMWARE-INSTALL.md`) is untouched — plan 168-09 owns its deletion and the 17 associated doc-leg removals.
- The contradictory jumper-identity documentation finding is now recorded in this phase's record (above) rather than in a test comment; no plan currently owns resolving it, and it is not blocking.
- No blockers for plan 168-08 or subsequent Wave 4 plans.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: firestarter/CLAUDE.md
- FOUND: firestarter/README.md
- FOUND: firestarter/include/proto_constants.h
- FOUND: firestarter/test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp
- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-07-SUMMARY.md
- FOUND: firestarter/doc absent (correct)
- FOUND commit: d81281d (firestarter)
- FOUND commit: 57898e2 (firestarter)
- FOUND commit: bf3a4e4 (firestarter)
