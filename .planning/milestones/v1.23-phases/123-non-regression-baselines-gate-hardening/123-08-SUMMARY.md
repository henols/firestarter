---
phase: 123-non-regression-baselines-gate-hardening
plan: 08
subsystem: testing
tags: [pytest, cross-repo-gates, fail-closed, scan-path-inventory, rekey]

requires:
  - phase: 123-07
    provides: "tests/fw_presence.py — FW_ROOT, FW_REPO_PRESENT, FW_ABSENT_REASON, requires_fw, fw_path, MissingScanTargetError"
provides:
  - "All 7 proxy-carrying host test modules rekeyed onto tests.fw_presence.requires_fw — 24 decorator legs AND the one non-decorator inline guard (test_sdp_table_parity.py:299)"
  - "tests/scan_paths.py — D-11's single committed cross-repo scan-path inventory covering both populations (tests/ modules + tools/*.py resolvers), plus a documented same-repo-look-alike exclusion list"
  - "tests/test_scan_paths_resolve.py — the one test that resolves the whole inventory and names every missing path"
affects: [123-09, 123-11, "124 (MERGE-07 consumes tests/scan_paths.py)"]

tech-stack:
  added: []
  patterns:
    - "Single shared skip marker (requires_fw) replacing per-module FW_ABSENT/_FW_ABSENT/_FW_HEADER_ABSENT proxies"
    - "fw_path() as the resolution point for every cross-repo path constant, so a present-repo-renamed target is a named MissingScanTargetError, never a silent skip"
    - "Explicit, non-derived scan-path inventory (dataclass tuples, no glob/rglob/walk) covering both the test-module and tool-resolver populations"

key-files:
  created:
    - firestarter_app/tests/scan_paths.py
    - firestarter_app/tests/test_scan_paths_resolve.py
  modified:
    - firestarter_app/tests/test_revision_constants_parity.py
    - firestarter_app/tests/test_dispatch_mirror.py
    - firestarter_app/tests/test_sdp_bus_config_drift.py
    - firestarter_app/tests/test_gen_validation_header.py
    - firestarter_app/tests/test_check_no_log_in_sdp_window.py
    - firestarter_app/tests/test_sdp_table_parity.py
    - firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py

key-decisions:
  - "Chose 'update every decorator site to @requires_fw and delete the local alias' over 'import the shared marker under the existing alias name' — applied consistently across all seven modules, so a grep for fw_presence and for the absence of reason= is unambiguous"
  - "Promoted test_sdp_table_parity.py's bare inline `if _FW_ABSENT: pytest.skip(...)` guard to the same @requires_fw decorator every other leg uses, rather than keying it inline on FW_REPO_PRESENT — the whole test body depends on the real committed eeprom_28c.cpp, so it needs the sibling present exactly like its siblings, and a decorator closes the exact gap a decorator-only rekey pass would otherwise leave open"
  - "Routed every cross-repo path constant (FIRMWARE_HEADER, _PROTOCOLS_MD, _FW_DISPATCH_TEST, _COMMITTED_HEADER, _EEPROM_28C_CPP, _FLASH_UTILS_H, _FIRESTARTER_H) through fw_path() rather than leaving them as manual Path joins, so a present-repo-renamed target is a named MissingScanTargetError at import/collection time instead of a bare FileNotFoundError inside a test body"
  - "Verified each of RESEARCH's 11 population-B tools by reading its source rather than copying the file list — found that 7 of the 11 build their default path with ONE '..' from tools/ (resolving into this app's own package, firestarter_app/firestarter/), not the sibling repo, despite matching RESEARCH's grep -ln 'firestarter\"' tools/*.py. Only 4 of the 11 are genuinely cross-repo, and all 4 name paths already covered by CROSS_REPO_TEST_PATHS, so ALL_CROSS_REPO_PATHS is a verified 6-entry union. The 7 same-repo look-alikes are recorded in SAME_REPO_LOOKALIKES (alongside _REAL_PINOUTS) and still listed in CROSS_REPO_TOOL_RESOLVERS with an empty cross_repo_paths tuple, so a renamed/deleted tool is still caught by the population-B coverage test"
  - "gen_sdp_bus_config.py turned out to carry BOTH shapes in one file: its _TARGET_DEFAULT is genuinely cross-repo (two parents from tools/) while its _PINOUTS_DEFAULT is the exact same same-repo trap as _REAL_PINOUTS (one parent from tools/) — recorded as a second, independent SAME_REPO_LOOKALIKES entry"

requirements-completed: []

coverage:
  - id: D1
    description: "All 7 proxy-carrying modules (24 decorator legs + 1 non-decorator inline guard) rekeyed onto the shared tests.fw_presence.requires_fw marker; zero per-module reason= strings or FW_ABSENT-shaped assignments survive"
    verification:
      - kind: unit
        ref: "tests/test_revision_constants_parity.py, test_dispatch_mirror.py, test_sdp_bus_config_drift.py, test_check_no_log_in_sdp_window.py, test_sdp_table_parity.py, test_check_is_memory_cmd_no_ifdef.py, test_gen_validation_header.py — 49 collected, 0 skipped"
        status: pass
      - kind: unit
        ref: "test_sdp_table_parity.py::test_altered_temp_copy_fails_parity_non_vacuous — still exists, now decorated, still passes"
        status: pass
    human_judgment: false
  - id: D2
    description: "FIRMWARE_HEADER (fixture-injection seam) and _REAL_PINOUTS (same-repo path) preserved untouched through the rekey"
    verification:
      - kind: unit
        ref: "tests/test_revision_constants_parity.py::test_planted_value_drift_is_detected (monkeypatch.setattr on FIRMWARE_HEADER still resolves)"
        status: pass
      - kind: unit
        ref: "tests/test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing (_REAL_PINOUTS still resolves inside the app repo)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-11 single committed cross-repo scan-path inventory (tests/scan_paths.py) covering both populations, with the same-repo look-alike exclusion list, and one resolving test (tests/test_scan_paths_resolve.py) naming every missing path"
    verification:
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py::test_all_cross_repo_paths_resolve"
        status: pass
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py::test_inventory_is_non_vacuous"
        status: pass
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py::test_no_entry_is_a_same_repo_lookalike"
        status: pass
      - kind: unit
        ref: "tests/test_scan_paths_resolve.py::test_all_eleven_tool_resolvers_exist"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-07-31
status: complete
---

# Phase 123 Plan 08: Rekey 7 Proxy Modules + D-11 Cross-Repo Scan-Path Inventory Summary

**All seven cross-repo host test modules (24 decorator legs + the one non-decorator inline guard at `test_sdp_table_parity.py:299`) now key their skip on `tests.fw_presence.requires_fw` instead of a per-module file-existence proxy, and a single committed `tests/scan_paths.py` inventory names every cross-repo scan path across both populations — including a second, independently-verified instance of the `_REAL_PINOUTS` same-repo name-collision trap found in 7 of RESEARCH's 11 listed `tools/*.py` files.**

## Performance

- **Duration:** ~70 min
- **Completed:** 2026-07-31
- **Tasks:** 3 (all `type="auto"`)
- **Files modified:** 7 modified, 2 created

## Accomplishments

- **Task 1 (4 multi-leg modules rekeyed, 19 legs):** `test_revision_constants_parity.py` (8 legs), `test_dispatch_mirror.py` (2 legs, compound two-path proxy collapsed to one repo-presence gate), `test_sdp_bus_config_drift.py` (3 legs), `test_gen_validation_header.py` (6 legs). Every module now imports `requires_fw` (and `fw_path` where it reads a cross-repo file) from `tests.fw_presence`; every local `FW_ABSENT`/`_FW_HEADER_ABSENT` constant and `reason=` string is gone. `FIRMWARE_HEADER` and `_REAL_PINOUTS` preserved exactly as the plan required (fixture-injection seam and same-repo path, respectively).
- **Task 2 (3 remaining modules rekeyed, including the inline guard):** `test_check_no_log_in_sdp_window.py`, `test_check_is_memory_cmd_no_ifdef.py` (single-leg `_requires_fw` alias rekeys), and `test_sdp_table_parity.py` (3 decorator legs **plus** the bare `if _FW_ABSENT: pytest.skip(...)` guard inside `test_altered_temp_copy_fails_parity_non_vacuous`, invisible to a decorator grep — promoted to the same `@requires_fw` decorator every other leg in the file uses). Verified by grepping the three legacy constant names across the whole `tests/` tree, not by counting decorators.
- **Task 3 (D-11 inventory):** `tests/scan_paths.py` — `CROSS_REPO_TEST_PATHS` (6 entries, population A: the paths the 7 rekeyed modules resolve), `CROSS_REPO_TOOL_RESOLVERS` (11 entries, population B: every `tools/*.py` file RESEARCH's grep found), `ALL_CROSS_REPO_PATHS` (the deduplicated union), `SAME_REPO_LOOKALIKES` (8 entries: `_REAL_PINOUTS` plus 7 tool-file same-repo package paths discovered by reading each of the 11 tools individually). `tests/test_scan_paths_resolve.py` — 4 tests: all-paths-resolve (naming every miss), non-vacuity floor, no-same-repo-lookalike, and population-B tool-file existence.

## Task Commits

1. **Task 1: Rekey the four multi-leg modules onto fw_presence (19 legs)** - `3812ab6` (refactor)
2. **Task 2: Rekey the three remaining modules including the non-decorator inline guard** - `e0f920e` (refactor)
3. **Task 3: Create the D-11 cross-repo scan-path inventory and the single resolving test** - `26b6dec` (feat)

All three commits are inside the `firestarter_app` submodule, on branch `v1.23-py32f071-integration`.

## Files Created/Modified

- `firestarter_app/tests/test_revision_constants_parity.py` - 8 legs rekeyed; residual-gap docstring rewritten to describe the BASE-02 split
- `firestarter_app/tests/test_dispatch_mirror.py` - compound 2-path proxy collapsed to one repo-presence gate
- `firestarter_app/tests/test_sdp_bus_config_drift.py` - 3 legs rekeyed; `_REAL_PINOUTS` preserved untouched
- `firestarter_app/tests/test_gen_validation_header.py` - 6 legs rekeyed
- `firestarter_app/tests/test_check_no_log_in_sdp_window.py` - 1 leg rekeyed
- `firestarter_app/tests/test_sdp_table_parity.py` - 3 legs + the inline guard rekeyed
- `firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py` - 1 leg rekeyed
- `firestarter_app/tests/scan_paths.py` - new D-11 inventory (created)
- `firestarter_app/tests/test_scan_paths_resolve.py` - new resolving test (created)

## Decisions Made

See `key-decisions` in frontmatter. Summary:
- Consistent "edit every decorator site to `@requires_fw`, delete the local alias" rekey shape across all seven modules (rather than mixing in the "import under the existing alias name" option).
- The inline guard was promoted to a decorator rather than rekeyed inline, since the whole test body needs the sibling repo present.
- Every cross-repo path constant routed through `fw_path()`, upgrading a present-repo-renamed target from `FileNotFoundError` to a named `MissingScanTargetError`.
- Population-B tool verification found 7 of RESEARCH's 11 listed files are same-repo look-alikes, not cross-repo resolvers — recorded explicitly rather than silently inflating `ALL_CROSS_REPO_PATHS` to 17.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_dispatch_mirror.py` left `import pytest` unused after the rekey**
- **Found during:** Task 1, running `ruff check` on the module
- **Issue:** Removing the last `@pytest.mark.skipif(...)` decorator left `import pytest` with no remaining use (F401).
- **Fix:** Removed the unused import.
- **Files modified:** `firestarter_app/tests/test_dispatch_mirror.py`
- **Verification:** `ruff check tests/test_dispatch_mirror.py` clean; 2/2 tests pass.
- **Committed in:** `3812ab6` (part of Task 1's commit)

**2. [Rule 1 - Bug] `test_gen_validation_header.py` needed `pytest` re-added after the rekey**
- **Found during:** Task 1, running `ruff check` on the module
- **Issue:** The module still uses `@pytest.mark.parametrize` on its handler-coverage leg; the mechanical import swap initially dropped `import pytest` along with the decorator-alias cleanup.
- **Fix:** Re-added `import pytest` (module genuinely needs it for `parametrize`, distinct from the removed skip decorator).
- **Files modified:** `firestarter_app/tests/test_gen_validation_header.py`
- **Verification:** `ruff check` clean; 12/12 tests pass (6 legs + 6 parametrized handler cases).
- **Committed in:** `3812ab6` (part of Task 1's commit)

**3. [Rule 1 - Bug] `test_sdp_table_parity.py` needed `pytest` retained for `pytest.raises`**
- **Found during:** Task 2, running `ruff check` on the module
- **Issue:** The module's `_requires_fw` alias removal initially dropped `import pytest`, but `test_missing_override_path_fails_closed` uses `pytest.raises(FileNotFoundError)` independently of the skip marker.
- **Fix:** Kept `import pytest` (needed for `pytest.raises`, unrelated to the `requires_fw` rekey).
- **Files modified:** `firestarter_app/tests/test_sdp_table_parity.py`
- **Verification:** `ruff check` clean; 5/5 tests pass.
- **Committed in:** `e0f920e` (part of Task 2's commit)

**4. [Rule 1 - Bug] `scan_paths.py`'s own docstring tripped the plan's `no rglob` verification grep**
- **Found during:** Task 3, running the plan's literal `grep -c 'rglob'` verification command
- **Issue:** The module docstring explained the "no glob, no `rglob`, no directory walk" discipline in prose — the word `rglob` in that explanatory sentence itself matched the literal-substring grep meant to prove the module contains no actual `rglob` call.
- **Fix:** Reworded the docstring to describe the same discipline ("No wildcard pattern matching and no directory walk of any kind") without the literal substring `rglob`.
- **Files modified:** `firestarter_app/tests/scan_paths.py`
- **Verification:** `grep -c 'rglob' tests/scan_paths.py` → `0`; module behavior unchanged (no rglob was ever called).
- **Committed in:** `26b6dec` (part of Task 3's commit)

---

**Total deviations:** 4 auto-fixed (all Rule 1, all import-hygiene or self-referential wording collisions with the plan's own literal-substring acceptance checks; no scope creep, no behavioral changes).
**Impact on plan:** All four fixes are mechanical follow-ons of the rekey itself (unused/missing imports discovered by the lint gate) or one-line wording changes; none altered test behavior or the inventory's actual content.

## Issues Encountered

- **RESEARCH's population-B tool list needed per-file verification, not a copy-paste.** RESEARCH's own planner note flagged this risk explicitly ("Confirm each by reading the tool, not by copying the list blindly"), and it proved correct: `grep -ln 'firestarter"' tools/*.py` cannot distinguish a path built with one `".."` from `tools/` (resolves into this app's own `firestarter_app/firestarter/` package) from one built with two (resolves into the sibling repo) — both contain the literal string `firestarter"`. Reading each of the 11 files individually found only 4 are genuinely cross-repo; the other 7 are same-repo look-alikes, now documented in `SAME_REPO_LOOKALIKES` rather than silently inflating the union to an incorrect 17-entry list. This is not a defect in RESEARCH — the file list itself (11 names) was exactly right; only the assumption that every listed file's `firestarter`-shaped path is cross-repo needed correcting.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All 7 proxy-carrying modules key on the shared `../firestarter/.git` marker; a firmware rename can no longer flip a gate leg PASS→SKIP silently (A-7's measured defect is closed for this module set).
- `tests/scan_paths.py` and `tests/test_scan_paths_resolve.py` exist as Phase 124's "manifest paths resolve" artifact, covering the 11 `tools/` resolvers a test-module-only inventory would have left unguarded.
- **BASE-02 remains untouched at the requirement level** — this plan explicitly ticks nothing (per its own `requirement_closure` note); BASE-02 closes only in 123-11 after the skip census (123-09) lands.
- 123-09 (the recurrence lint, D-09's second half) can now build its allow-list against exactly one canonical reason string (`FW_ABSENT_REASON` in `tests/fw_presence.py`) instead of five near-duplicates, since every per-module `reason=` variant is gone.
- Host suite: **1145 passed, 0 skipped** (was 1141 before Task 3's two new files; +4 tests from `test_scan_paths_resolve.py`, matching the plan's expected delta exactly).
- No blockers. Meta repo remains on `gsd/v1.23-py32f071-integration` with no branch switch.

---
*Phase: 123-non-regression-baselines-gate-hardening*
*Completed: 2026-07-31*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_revision_constants_parity.py`
- FOUND: `firestarter_app/tests/test_dispatch_mirror.py`
- FOUND: `firestarter_app/tests/test_sdp_bus_config_drift.py`
- FOUND: `firestarter_app/tests/test_gen_validation_header.py`
- FOUND: `firestarter_app/tests/test_check_no_log_in_sdp_window.py`
- FOUND: `firestarter_app/tests/test_sdp_table_parity.py`
- FOUND: `firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py`
- FOUND: `firestarter_app/tests/scan_paths.py`
- FOUND: `firestarter_app/tests/test_scan_paths_resolve.py`
- FOUND commit `3812ab6` (Task 1)
- FOUND commit `e0f920e` (Task 2)
- FOUND commit `26b6dec` (Task 3)
