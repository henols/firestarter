---
phase: 104-rename-protocol-header-and-cpp-files-to-descriptive-protocol
plan: 03
subsystem: firmware-tests, host-tooling, docs
tags: [firmware, native-tests, dispatch-mirror, docs, gate-01, gate-02, gate-03, wave-3]

# Dependency graph
requires:
  - phase: 104-01
    provides: "Renamed firmware handlers configure_flash_nor_unlock (0x06) / configure_flash_5v_page (0x05), file pairs flash_nor_unlock.{h,cpp} / flash_5v_page.{h,cpp}"
  - phase: 104-02
    provides: "check_dispatch.py + validation_matrix_spec.json + regenerated validation_matrix.h already carrying nor_unlock/5v_page family ids and configure_flash_nor_unlock/configure_flash_5v_page handler names"
provides:
  - "Renamed native Tier-1 validation suites test_val_nor_unlock/ and test_val_5v_page/ (dir + .cpp + test-fn stems), with the make_handle(0x35/0x39) phantom-protocol integer literals left byte-unchanged"
  - "test_dispatch/test_configure_memory.cpp dispatch-test names + FIX-02A comment block updated to the renamed handlers"
  - "platformio.ini test_filter + -I build_flags pointing at the renamed suite dirs"
  - "PROTOCOLS.md §0/§1.1/§1.2/§2.1/§3 fully reconciled to the renamed handlers/files; INV-04/INV-09 ids grep-intact and pointing at the renamed suite dirs"
  - "firestarter/CLAUDE.md dispatch list + handler table reconciled"
  - "test_dispatch_mirror.py DOC_FILE_TO_FUNC closing the three-way doc↔tool↔firmware bind"
  - "Four latent test regressions (caused by Plan 02's spec rename, surfaced only when the full firestarter_app suite was run) fixed: test_val_wire_flash3.py/flash4.py renamed to test_val_wire_nor_unlock.py/5v_page.py, test_matrix_schema.py, test_validate_family_cmd.py, test_gen_validation_header.py"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "git mv suite-dir-then-file (same two-step pattern as Plan 01's header/source renames) preserves rename history for native test suites"
    - "Family-scoped Tier-2 wire test files (test_val_wire_<family>.py) follow the same <family>-id rename as their Tier-1 native suite counterparts, sourced from the same validation_matrix_spec.json family id"

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp
    - firestarter/platformio.ini
    - firestarter/doc/PROTOCOLS.md
    - firestarter/CLAUDE.md
    - firestarter_app/tests/test_dispatch_mirror.py
    - firestarter_app/tools/check_dispatch.py
    - firestarter_app/tests/test_matrix_schema.py
    - firestarter_app/tests/test_validate_family_cmd.py
    - firestarter_app/tests/test_gen_validation_header.py
  renamed:
    - firestarter/test/native/avr/test_val_flash3/ -> firestarter/test/native/avr/test_val_nor_unlock/ (host_stubs.cpp + test_val_flash3.cpp -> test_val_nor_unlock.cpp)
    - firestarter/test/native/avr/test_val_flash4/ -> firestarter/test/native/avr/test_val_5v_page/ (host_stubs.cpp + test_val_flash4.cpp -> test_val_5v_page.cpp)
    - firestarter_app/tests/test_val_wire_flash3.py -> firestarter_app/tests/test_val_wire_nor_unlock.py
    - firestarter_app/tests/test_val_wire_flash4.py -> firestarter_app/tests/test_val_wire_5v_page.py

key-decisions:
  - "Fixed 4 latent test breakages caused by Plan 02's family-id rename (flash3/flash4 -> nor_unlock/5v_page in validation_matrix_spec.json) as Rule 1 auto-fixes: test_val_wire_flash3.py/flash4.py had a hard StopIteration on collection (next(f for f in spec['families'] if f['id']=='flash3') found nothing) so were renamed + fixed like the native suites; test_matrix_schema.py EXPECTED_HANDLERS, test_validate_family_cmd.py expected family set, and test_gen_validation_header.py parametrized handler list still asserted the old configure_flash3/configure_flash4 strings and were failing before this plan's Task 3 verification ran the full firestarter_app suite"
  - "Left firestarter_app/firestarter/cli_handlers.py's dev validate-family Click Choice list (still literally ['eprom','eeprom28c','flash3','flash4',...]) UNCHANGED despite it now being stale against the renamed family ids -- the plan's explicit prohibition names cli_handlers.py directly (GATE-03: MUST NOT touch any CLI grammar / cli_handlers source file); flagged as a known latent bug for a future phase rather than silently expanding scope"
  - "Left tools/baseline/dispatch_baseline.json (a large frozen snapshot still full of literal configure_flash3/configure_flash4 strings) untouched -- grep confirms it has zero Python consumers (no test or tool reads it), so it is an orphaned artifact with no regression risk and out of this plan's declared scope"
  - "Left informal 'flash3'/'flash4' prose mentions in ic_layout.py, database.py, eprom_operations.py, constants.py, build_db.py, diff_db.py, test_database_conversion.py, test_decoder.py untouched -- these are shorthand comments/docstrings unrelated to the renamed file/function/suite identifiers this phase targets (RENAME-04/05 scope), not load-bearing assertions, and firestarter/cli_handlers.py-adjacent files are additionally covered by the GATE-03 prohibition"
  - "check_dispatch.py comment at line 61 ('5V-only handlers (flash3/flash4/...)') updated to 'nor_unlock/5v_page' as a light Rule 2 completeness fix since this file is the canonical host guard file named in Task 3's bind scope, even though the plan's files_modified list only named test_dispatch_mirror.py for firestarter_app"

patterns-established: []

requirements-completed: [RENAME-04, RENAME-05]

coverage:
  - id: D1
    description: "Native suite dirs test_val_nor_unlock/ and test_val_5v_page/ exist (git mv, history preserved) with renamed .cpp files; test-fn stems test_flash3_*/test_flash4_* -> test_nor_unlock_*/test_5v_page_*; RUN_TEST lists updated; make_handle(0x35/0x39) phantom integer literals byte-unchanged"
    requirement: "RENAME-04"
    verification:
      - kind: unit
        ref: "pio test -e native -f *test_val_nor_unlock* (4/4 PASS) and -f *test_val_5v_page* (8/8 PASS)"
        status: pass
      - kind: unit
        ref: "grep -rn 'configure_flash3|configure_flash4|test_flash3|test_flash4|flash3_|flash4_' returns empty in both suite dirs + test_dispatch/test_configure_memory.cpp; grep -q make_handle(0x35 still present"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_dispatch/test_configure_memory.cpp dispatch-test names + FIX-02A comment renamed (test_protocol_0x06_dispatches_nor_unlock, test_protocol_0x0{5,35,39}_dispatches_5v_page, test_5v_page_check_chip_id_*); platformio.ini test_filter + -I build_flags point at renamed suite dirs"
    requirement: "RENAME-04"
    verification:
      - kind: unit
        ref: "pio test -e native -f *test_dispatch* (18/18 PASS)"
        status: pass
    human_judgment: false
  - id: D3
    description: "PROTOCOLS.md §0 handler-family table, §1.1/§1.2 handler lines + prose, §2.1 phantom prose, §3 INV suite-path contract + INV-04/INV-09 rows all reconciled to configure_flash_5v_page()/flash_5v_page.cpp and configure_flash_nor_unlock()/flash_nor_unlock.cpp; INV-04/INV-09 ids left grep-intact; firestarter/CLAUDE.md dispatch list + handler table reconciled"
    requirement: "RENAME-05"
    verification:
      - kind: unit
        ref: "grep -n 'flash_type_3|flash_type_4|configure_flash3|configure_flash4|test_val_flash3|test_val_flash4' returns empty in PROTOCOLS.md and CLAUDE.md; grep -q INV-04, INV-09, test_val_5v_page, test_val_nor_unlock all present"
        status: pass
    human_judgment: false
  - id: D4
    description: "test_dispatch_mirror.py DOC_FILE_TO_FUNC maps flash_5v_page.cpp -> configure_flash_5v_page and flash_nor_unlock.cpp -> configure_flash_nor_unlock, closing the three-way doc<->tool<->firmware bind; full phase gate green end to end"
    requirement: "RENAME-05"
    verification:
      - kind: unit
        ref: "pytest test_dispatch_mirror.py test_check_dispatch_invariants.py (14/14 PASS)"
        status: pass
      - kind: unit
        ref: "pio run -t clean && pio test -e native (82/82 PASS) && pio run -e uno (SUCCESS, 23516B/72.9% flash) && pio run -e leonardo (SUCCESS, 25654B/89.5% flash, byte-identical to Phase 104-01 baseline)"
        status: pass
      - kind: integration
        ref: "python tools/diff_db.py (PASS: only the pre-existing Phase-94 PGSZ baseline delta, 0 new drift) -- GATE-02 non-regression held"
        status: pass
      - kind: static
        ref: "GATE-03 held: cli_handlers.py / CLI grammar not touched by this plan (confirmed by git diff scope); repo-wide grep for flash_type_3/flash_type_4/configure_flash3/configure_flash4/test_val_flash3/test_val_flash4 returns empty in both repos excluding TYPE_FLASH_TYPE_3/4 #defines, val-results/, .pio/, and the orphaned dispatch_baseline.json"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-07-02
status: complete
---

# Phase 104 Plan 03: Rename Native Test Suites + Reconcile Docs + Close Dispatch-Mirror Bind Summary

**Renamed the two native validation Tier-1 suites (test_val_flash3/4 -> test_val_nor_unlock/5v_page) and their dependent Tier-2 wire tests, reconciled PROTOCOLS.md and CLAUDE.md, closed the doc<->tool<->firmware dispatch-mirror bind in test_dispatch_mirror.py, and ran the full v1.19 phase gate (native 82/82, both boards compile byte-identical, DB identity held) — surfacing and Rule-1-fixing four latent test breakages left behind by Plan 02's spec rename.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-07-02T07:32:00Z (approx, immediately after Plan 02 close)
- **Completed:** 2026-07-02T07:54:24Z
- **Tasks:** 3 (plus 4 Rule-1 auto-fixes discovered during Task 3's full-suite gate run)
- **Files modified:** 15 (4 renamed pairs + 11 edited across firestarter + firestarter_app)

## Accomplishments

- `test_val_flash3/` -> `test_val_nor_unlock/` and `test_val_flash4/` -> `test_val_5v_page/` via `git mv` (history preserved); test-fn stems `test_flash3_*`/`test_flash4_*` renamed to `test_nor_unlock_*`/`test_5v_page_*`; `host_stubs.cpp` comment strings updated; `make_handle(0x35, ...)` / `make_handle(0x39, ...)` phantom-protocol integer literals left byte-unchanged (GATE-01 hard prohibition).
- `test_dispatch/test_configure_memory.cpp` dispatch-test names renamed (`test_protocol_0x06_dispatches_nor_unlock`, `test_protocol_0x0{5,35,39}_dispatches_5v_page`, `test_5v_page_check_chip_id_0x{05,35,39}_sets_operation`), FIX-02A comment block updated; `platformio.ini` `test_filter` + `-I` build flags repointed at the renamed suite dirs.
- `PROTOCOLS.md` fully reconciled: §0 handler-family table, §1.1/§1.2 handler lines + prose, §2.1 phantom-bucket prose, and the §3 SAFE-02 INV suite-path contract (INV-04 -> `test_val_5v_page/`, INV-09 -> `test_val_nor_unlock/`) all now read `configure_flash_5v_page()`/`flash_5v_page.cpp` and `configure_flash_nor_unlock()`/`flash_nor_unlock.cpp`; INV-04/INV-09 ids kept grep-intact. `firestarter/CLAUDE.md` dispatch-order list and handler table reconciled to match (the `TYPE_FLASH_TYPE_3`/`TYPE_FLASH_TYPE_4` `#define` labels are unchanged, as they are out of scope).
- `test_dispatch_mirror.py`'s `DOC_FILE_TO_FUNC` now maps `flash_5v_page.cpp` -> `configure_flash_5v_page` and `flash_nor_unlock.cpp` -> `configure_flash_nor_unlock`, closing the three-way PROTOCOLS.md-§0 <-> DOC_FILE_TO_FUNC <-> `check_dispatch.dispatch()` bind opened by Plan 02.
- **Discovered during the Task 3 full-gate run (Rule 1 — broken behavior):** four firestarter_app test files were silently broken by Plan 02's `validation_matrix_spec.json` family-id rename (`flash3`/`flash4` -> `nor_unlock`/`5v_page`), never caught because the plan's declared Task 3 verification only ran `test_dispatch_mirror.py` + `test_check_dispatch_invariants.py`. Running the full firestarter_app suite surfaced:
  - `test_val_wire_flash3.py`/`test_val_wire_flash4.py` — hard collection error (`StopIteration` on `next(f for f in spec["families"] if f["id"] == "flash3")`, since that id no longer exists in the spec). Fixed by renaming (mirroring the native-suite pattern) to `test_val_wire_nor_unlock.py`/`test_val_wire_5v_page.py` with all internal identifiers and prose updated.
  - `test_matrix_schema.py::test_spec_enumerates_all_6_handlers` — `EXPECTED_HANDLERS` still listed `configure_flash3`/`configure_flash4`. Updated to the renamed names.
  - `test_validate_family_cmd.py::test_all_families_emits_all_cells` — expected family-id set still listed `flash3`/`flash4`. Updated to `nor_unlock`/`5v_page`.
  - `test_gen_validation_header.py::test_all_6_handlers_present_in_committed_header` — parametrized handler list still asserted `configure_flash3`/`configure_flash4` against the regenerated header (which Plan 02 already updated). Updated the parametrize list + a stale docstring reference.
- Full phase gate run and green: `pio test -e native` 82/82 PASS; `pio run -e uno` SUCCESS (23516 B / 72.9% flash); `pio run -e leonardo` SUCCESS (25654 B / 89.5% flash — byte-identical to the Plan 104-01 baseline, confirming a pure rename with zero behavior/size change); `pytest test_dispatch_mirror.py test_check_dispatch_invariants.py` 14/14 PASS; `python tools/diff_db.py` PASS (only the pre-existing Phase-94 PGSZ baseline delta, 0 new drift — GATE-02 held).

## Task Commits

Each task was committed atomically:

1. **Task 1: git mv + rename native test suites and the dispatch test** (firestarter) - `72fce0a` (feat)
2. **Task 2: Reconcile PROTOCOLS.md and firestarter/CLAUDE.md** (firestarter) - `96b3138` (docs)
3. **Task 3: Close the dispatch-mirror bind; fix 4 latent Rule-1 test regressions; run the full phase gate** (firestarter_app) - `f4f265f` (test)

_Note: commits were made inside the respective submodules (`firestarter/` and `firestarter_app/`), on their current branch `v1.19-protocol-naming-labels` (no gitlink bump — consistent with standing policy)._

## Files Created/Modified

- `firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp` (renamed from `test_val_flash3/test_val_flash3.cpp`) — renamed test-fn stems, `configure_flash3` -> `configure_flash_nor_unlock` in comments/asserts
- `firestarter/test/native/avr/test_val_nor_unlock/host_stubs.cpp` (renamed from `test_val_flash3/host_stubs.cpp`) — comment string updated
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (renamed from `test_val_flash4/test_val_flash4.cpp`) — renamed test-fn stems, `configure_flash4` -> `configure_flash_5v_page`; `make_handle(0x35/0x39)` literals unchanged
- `firestarter/test/native/avr/test_val_5v_page/host_stubs.cpp` (renamed from `test_val_flash4/host_stubs.cpp`) — comment string updated
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — dispatch-test names + FIX-02A comment renamed
- `firestarter/platformio.ini` — `test_filter` + `-I` build_flags repointed at renamed suite dirs
- `firestarter/doc/PROTOCOLS.md` — §0/§1.1/§1.2/§2.1/§3 fully reconciled
- `firestarter/CLAUDE.md` — dispatch list + handler table reconciled
- `firestarter_app/tests/test_dispatch_mirror.py` — `DOC_FILE_TO_FUNC` closes the three-way bind
- `firestarter_app/tools/check_dispatch.py` — comment shorthand updated (nor_unlock/5v_page)
- `firestarter_app/tests/test_val_wire_nor_unlock.py` (renamed from `test_val_wire_flash3.py`) — Rule 1 fix
- `firestarter_app/tests/test_val_wire_5v_page.py` (renamed from `test_val_wire_flash4.py`) — Rule 1 fix
- `firestarter_app/tests/test_matrix_schema.py` — Rule 1 fix (`EXPECTED_HANDLERS`)
- `firestarter_app/tests/test_validate_family_cmd.py` — Rule 1 fix (expected family set)
- `firestarter_app/tests/test_gen_validation_header.py` — Rule 1 fix (parametrized handler list + docstring)

## Decisions Made

- Applied Rule 1 (auto-fix bugs) to four firestarter_app test files broken by Plan 02's family-id rename, since they were directly caused by this rename chain and block the honest "no surviving flash3/flash4 string" success criterion — not out-of-scope pre-existing issues.
- Explicitly did NOT touch `firestarter_app/firestarter/cli_handlers.py`'s `dev validate-family` Click `Choice` list, even though it is now stale (`"flash3"`/`"flash4"` no longer resolve to any family in the spec, so those CLI values now silently resolve to an empty family list). The plan's prohibition names `cli_handlers.py` specifically as a GATE-03 boundary; flagging this as a known latent bug rather than expanding scope past an explicit plan-level prohibition.
- Left `tools/baseline/dispatch_baseline.json` (frozen snapshot, `configure_flash3`/`configure_flash4` strings throughout) untouched — grep-confirmed it has zero Python consumers (no test or tool reads it back), so it carries no regression risk and updating it is out of this plan's declared scope.
- Left informal "flash3"/"flash4" prose mentions in `ic_layout.py`, `database.py`, `eprom_operations.py`, `constants.py`, `build_db.py`, `diff_db.py`, `test_database_conversion.py`, `test_decoder.py` untouched — shorthand comments/docstrings, not load-bearing assertions on the renamed identifiers.
- `check_dispatch.py`'s one informal comment mention was updated as a light Rule 2 completeness pass since it is the canonical host guard file explicitly named in Task 3's dispatch-mirror-bind scope.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed StopIteration in test_val_wire_flash3.py / test_val_wire_flash4.py**
- **Found during:** Task 3 full-suite gate run (`python -m pytest` across all of `firestarter_app`)
- **Issue:** Plan 02 renamed the `flash3`/`flash4` family ids in `validation_matrix_spec.json` to `nor_unlock`/`5v_page`. These two Tier-2 wire test files still did `next(f for f in _SPEC["families"] if f["id"] == "flash3")`, which now raises `StopIteration` at module import — a hard pytest collection error, not just a failing assertion.
- **Fix:** Renamed the files (mirroring the same `test_val_wire_<family>` naming convention already used by the other 4 families) to `test_val_wire_nor_unlock.py` / `test_val_wire_5v_page.py`, and updated every internal identifier (`_FLASH3_FAMILY` -> `_NOR_UNLOCK_FAMILY`, `_FLASH4_FAMILY` -> `_5V_PAGE_FAMILY`, test-fn stems, docstrings, error-message prose) to match. Message-catalog constants (`MSG_WARN_FL4_BOOT_BLOCK_LOCKED`, `MSG_ERR_FL4_BOOT_BLOCK_LOCKED`) are codegen-produced identifiers unrelated to this rename's scope and were left verbatim.
- **Files modified:** `firestarter_app/tests/test_val_wire_nor_unlock.py`, `firestarter_app/tests/test_val_wire_5v_page.py`
- **Commit:** `f4f265f`

**2. [Rule 1 - Bug] Fixed stale handler-name assertions in test_matrix_schema.py / test_validate_family_cmd.py / test_gen_validation_header.py**
- **Found during:** Same full-suite gate run
- **Issue:** These three test files hardcoded `configure_flash3`/`configure_flash4` (and `flash3`/`flash4` family ids) as expected values, asserted against `validation_matrix_spec.json` and the regenerated `validation_matrix.h` — both of which Plan 02 already updated to the renamed names. All three were failing.
- **Fix:** Updated `test_matrix_schema.py`'s `EXPECTED_HANDLERS` set, `test_validate_family_cmd.py`'s expected family-id set, and `test_gen_validation_header.py`'s parametrized handler list (plus one docstring reference) to the renamed `configure_flash_nor_unlock`/`configure_flash_5v_page` / `nor_unlock`/`5v_page` names.
- **Files modified:** `firestarter_app/tests/test_matrix_schema.py`, `firestarter_app/tests/test_validate_family_cmd.py`, `firestarter_app/tests/test_gen_validation_header.py`
- **Commit:** `f4f265f`

### Deferred / Out-of-Scope Items (not fixed — documented for a future phase)

- **`cli_handlers.py` `dev validate-family` Click Choice list is stale.** It still lists `"flash3"`/`"flash4"` as valid CLI arguments, but no family in `validation_matrix_spec.json` has those ids anymore (they are `nor_unlock`/`5v_page`). Click will accept `flash3`/`flash4` as syntactically valid input, but `_families_for_selection()` will silently return an empty family list (no error, no cells emitted) — a latent, currently-untested UX bug. Not fixed here because the plan's Task 3 prohibition explicitly names `cli_handlers.py` ("MUST NOT touch any CLI grammar / cli_handlers source file... GATE-03"). Recommend a small follow-up fix in a future non-104 phase (updating a `Choice` list is not itself a "protocol name as CLI input" GATE-03 violation, but is out of this plan's declared scope).
- **`tools/baseline/dispatch_baseline.json`** still contains hundreds of literal `"configure_flash3"`/`"configure_flash4"` strings. Confirmed via grep that no Python file in the repo reads this JSON file — it appears to be an orphaned/unused baseline artifact from an earlier phase. No regression risk; left untouched as out of scope.
- **`tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`** fails independent of this plan (byte-diff against `tests/golden/v1.3-COVERAGE-MATRIX.md`, unrelated to protocol naming — the ledger file it reads, `.planning/v1.3-defect-coverage-ids.json`, was last touched at Phase 11). Verified pre-existing by re-running the full suite immediately after a `git stash` of all Task-3 edits — the failure persisted identically. Not caused by, and not fixed by, this plan.

## Issues Encountered

None beyond the four Rule-1 fixes documented above, all resolved within this plan.

## User Setup Required

None — no external service configuration required.

## GATE Verification (full v1.19 phase-gate battery)

- **GATE-01** (dispatch-mirror + native, primary this phase): PASS. `test_dispatch_mirror.py` + `test_check_dispatch_invariants.py` 14/14 green; `pio test -e native` 82/82 green (all suites, including the two renamed Tier-1 suites); phantom-protocol integer literals (`make_handle(0x35)`/`make_handle(0x39)`) verified byte-unchanged.
- **GATE-02** (DB identity, non-regression): PASS. `python tools/diff_db.py` reports only the pre-existing Phase-94 PGSZ baseline delta (2 chips, `page_size` field, documented and expected) — 0 new drift. Constants-parity py3.11-target leg recorded CI-PENDING (no python3.11 binary in this devcontainer; this phase changes no constants) — non-blocking, per Phase 98/103 precedent.
- **GATE-03** (no CLI grammar change, non-regression): PASS. `cli_handlers.py` and all CLI-grammar source files were not modified by this plan (static confirmation via the commit diff scope); no protocol name/alias was made acceptable as CLI input.
- Both boards compile clean: `pio run -e uno` SUCCESS (23516 B / 72.9%), `pio run -e leonardo` SUCCESS (25654 B / 89.5% — byte-identical to the Plan 104-01 post-rename baseline).
- Final repo-wide grep smoke: no surviving `flash_type_3`/`flash_type_4`/`configure_flash3`/`configure_flash4`/`test_val_flash3`/`test_val_flash4`/`FALSH` string in any scoped firmware source/doc/test or host guard file, excluding the intentional `TYPE_FLASH_TYPE_3`/`TYPE_FLASH_TYPE_4` `#define`s, historical `val-results/`, `.pio/` build cache, and the orphaned/unconsumed `tools/baseline/dispatch_baseline.json`.

## Next Phase Readiness

- Phase 104 (all 3 plans) is now complete: firmware handlers renamed (104-01), host dispatch-mirror tooling brought into lockstep (104-02), native test suites + docs reconciled + dispatch-mirror bind closed + full gate green (104-03).
- No blockers. GATE-01/02/03 all hold. Two known latent/out-of-scope items are documented above (`cli_handlers.py` stale Choice list, orphaned `dispatch_baseline.json`) for a future phase to pick up if desired — neither blocks phase or milestone close.
- v1.19 milestone: per `STATE.md`, this was the only remaining phase after Phase 103's close; all 4 phases (100-103 planning-only + 104 execution) reach terminal state at this plan's completion — actual git close-out (tag, beta merge) remains operator-gated per standing policy and was NOT triggered by this plan.

---
*Phase: 104-rename-protocol-header-and-cpp-files-to-descriptive-protocol*
*Completed: 2026-07-02*

## Self-Check: PASSED

All renamed/modified files verified present on disk:
- `firestarter/test/native/avr/test_val_nor_unlock/test_val_nor_unlock.cpp` — FOUND
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — FOUND
- `firestarter/doc/PROTOCOLS.md` — FOUND, INV-04/INV-09 grep-intact
- `firestarter_app/tests/test_val_wire_nor_unlock.py` — FOUND
- `firestarter_app/tests/test_val_wire_5v_page.py` — FOUND

All commit hashes verified present in git history:
- firestarter submodule: `72fce0a`, `96b3138`
- firestarter_app submodule: `f4f265f`
