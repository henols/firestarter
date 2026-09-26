---
phase: 116-ground-truth-trace-harness
plan: 03
subsystem: testing
tags: [python, host-pytest, sdp, chip-database, invariant, parity-gate]

# Dependency graph
requires:
  - phase: 116-01
    provides: "v1.22 branch in both sub-repos; 82/82 native baseline"
provides:
  - "test_sdp_db_invariant.py — machine-checked TRACE-05 fact: 84 algorithm==13 chips, all chip_id_check false, all chip_id_value zero sentinel, no FW_ABSENT-style skip marker"
  - "test_sdp_table_parity.py — closes RESEARCH F6's transcription gap: EEPROM_SDP_DISABLE (eeprom_28c.cpp) proven identical to FLASH_DISABLE_WRITE_PROTECTION (flash_utils.h), plus the erase-vs-unlock terminal-byte hazard guard"
affects: [117, 121, 122]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Brace-scoped {address, byte} extraction (locate named declaration, walk brace depth to the matching close) instead of a bare file-wide regex — eeprom_28c.cpp has a non-initializer call site (eeprom28c_wait_for_write(handle, 0x5555, 0x20)) using the identical literal bytes that a loose pattern would false-positive on"
    - "Shared selection/assertion helper used by both the real-DB test and its non-vacuity twin, so the non-vacuity leg exercises the exact same code path as the real assertion, not a parallel reimplementation"
    - "FIRESTARTER_SDP_SRC env-override seam (mirrors check_dispatch.py's FIRESTARTER_DB_FILE idiom) — fails closed (FileNotFoundError) on a missing/unreadable path; exists only so the non-vacuity test can plant an altered fixture without touching the real, clean eeprom_28c.cpp"

key-files:
  created:
    - firestarter_app/tests/test_sdp_db_invariant.py
    - firestarter_app/tests/test_sdp_table_parity.py
  modified: []

key-decisions:
  - "Reworded the module docstring's description of 'no FW_ABSENT-style skipif' to 'no FW_ABSENT-style skip marker' in test_sdp_db_invariant.py — the plan's literal acceptance criterion greps for the substring 'skipif' and expects zero matches even in prose; the docstring's meaning (this module carries no skip decorator) is preserved verbatim while avoiding the literal substring (same class of fix as the Phase 107 decision-coverage wording fix)"
  - "Factored a shared _select_0x0d_chips / _assert_chip_id_check_false helper pair so the non-vacuity test calls the identical code the real-DB test calls, rather than re-deriving the selection logic in a separate assertion"
  - "test_sdp_table_parity.py's fail-closed-seam test (missing override path) carries no FW_ABSENT skip marker even though the module as a whole does — it only exercises _sdp_src_path()'s override branch against a literal nonexistent path and never touches the real firmware checkout, so it stays meaningful even when the firmware sub-repo is absent"

requirements-completed: [TRACE-05, TRACE-02]

coverage:
  - id: D1
    description: "test_sdp_db_invariant.py asserts both halves of the TRACE-05 invariant (exactly 84 algorithm==13 entries, AND every one has chip_id_check is False) plus the companion chip_id_value zero-sentinel fact, over the real chip_database.json read directly (not via EpromDatabase)"
    requirement: "TRACE-05"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_db_invariant.py::test_exactly_84_algorithm_0x0d_entries, ::test_all_0x0d_chips_have_chip_id_check_false, ::test_all_0x0d_chips_have_chip_id_value_zero_sentinel"
        status: pass
    human_judgment: false
  - id: D2
    description: "Non-vacuity: a synthetic algorithm==13 chip with chip_id_check: True makes the shared helper raise, proving the invariant is capable of failing; the module carries zero skip markers (grep -c 'skipif' == 0) so it always runs in host-only CI"
    requirement: "TRACE-05"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_db_invariant.py::test_synthetic_chip_id_check_true_is_flagged_non_vacuous"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_sdp_table_parity.py brace-scoped-parses EEPROM_SDP_DISABLE (eeprom_28c.cpp, internal linkage) and FLASH_DISABLE_WRITE_PROTECTION (flash_utils.h, header) and proves the two ordered 6-pair lists are identical; asserts the distinct erase-vs-unlock terminal-byte hazard fact (first 5 pairs identical to FLASH_ERASE, terminal byte differs)"
    requirement: "TRACE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_table_parity.py::test_eeprom_sdp_disable_matches_flash_disable_write_protection, ::test_unlock_table_terminal_byte_differs_from_erase_terminal_byte"
        status: pass
    human_judgment: false
  - id: D4
    description: "Non-vacuity + fail-closed seam: an altered temp copy of eeprom_28c.cpp (one pair byte flipped) makes the parity assertion fail via the FIRESTARTER_SDP_SRC override; pointing that override at a nonexistent path always raises FileNotFoundError, never a silent pass"
    requirement: "TRACE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_sdp_table_parity.py::test_altered_temp_copy_fails_parity_non_vacuous, ::test_missing_override_path_fails_closed"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-27
status: complete
---

# Phase 116 Plan 03: Ground Truth + Trace Harness — SDP DB Invariant + Table Parity Gates Summary

**Pinned two facts the rest of the v1.22 milestone leans on as executable host tests: the `0x0D` identity gate is dead across all 84 chips (TRACE-05, no skip marker, non-vacuous), and the unlock command table the trace suites will drive is provably the same table the shipped `0x0D` handler uses (closing RESEARCH F6's transcription gap).**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-27T21:07:55Z
- **Tasks:** 2
- **Files modified:** 2 (both in `firestarter_app`)

## Accomplishments

- `firestarter_app/tests/test_sdp_db_invariant.py` (4 tests, 0 skip markers): reads `chip_database.json` directly via the nested `programming` access path, asserts exactly **84** `algorithm == 13` entries, asserts every one has `chip_id_check is False` (identity comparison) and `chip_id_value == "0x00000000"` (the field that actually gates `eeprom28c_write_init`'s identity branch), and proves the shared selection/assertion helper raises on a synthetic violating row.
- `firestarter_app/tests/test_sdp_table_parity.py` (4 tests, `FW_ABSENT`-shaped skip marker on 3 of the 4): brace-scoped `{address, byte}` extraction (never a bare file-wide regex — `eeprom_28c.cpp` has a non-initializer call site using the identical literal bytes that would false-positive a loose pattern) proves `EEPROM_SDP_DISABLE` (internal-linkage `.cpp`) and `FLASH_DISABLE_WRITE_PROTECTION` (linkable header) are the same ordered 6-pair list, pins the erase-vs-unlock terminal-byte hazard distinction against `FLASH_ERASE`, and proves both a non-vacuity leg (altered temp fixture fails parity) and a fail-closed `FIRESTARTER_SDP_SRC` seam (missing path always raises).

## Observed facts

**DB invariant (TRACE-05), read live off `chip_database.json` in this session — matches RESEARCH F9 exactly:**

| Fact | Value |
|---|---|
| `algorithm == 13` count | 84 |
| `chip_id_check` distribution | `{False: 84}` |
| `chip_id_value` distribution | `{"0x00000000": 84}` |

**Table parity — both in-tree unlock tables found byte-for-byte identical:**

```
EEPROM_SDP_DISABLE (eeprom_28c.cpp)          == FLASH_DISABLE_WRITE_PROTECTION (flash_utils.h)
{0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x80} {0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x20}
```

Both tables' first five pairs are also identical to `FLASH_ERASE`'s first five pairs (`...{0x5555,0xAA} {0x2AAA,0x55} {0x5555,0x80} {0x5555,0xAA} {0x2AAA,0x55}...`); the terminal pair correctly diverges — SDP-disable ends `{0x5555, 0x20}`, `FLASH_ERASE` ends `{0x5555, 0x10}`. The one-nibble chip-erase hazard is machine-checked as distinct.

## Task Commits

Each task was committed atomically inside `firestarter_app`:

1. **Task 1: test_sdp_db_invariant.py — pin chip_id_check false across all 84 algorithm==13 entries (TRACE-05)** — `af521c4` (test, in `firestarter_app` sub-repo)
2. **Task 2: test_sdp_table_parity.py — close the F6 transcription gap on the unlock table** — `c5eb17d` (test, in `firestarter_app` sub-repo)

**Plan metadata:** committed in the meta repo (this SUMMARY.md + STATE.md + ROADMAP.md), see final commit below. Meta gitlink pointers for `firestarter` / `firestarter_app` stay unstaged (PINNED policy).

## Files Created/Modified

- `firestarter_app/tests/test_sdp_db_invariant.py` — 4-test DB invariant module, TRACE-05, no skip marker
- `firestarter_app/tests/test_sdp_table_parity.py` — 4-test parity gate, `FW_ABSENT`-shaped skip marker on the 3 firmware-reading tests

## Decisions Made

- Reworded the docstring phrase describing "no `FW_ABSENT`-style skipif" to "no `FW_ABSENT`-style skip marker" in `test_sdp_db_invariant.py` — the plan's literal acceptance criterion (`grep -c 'skipif'` must return 0) matches on the substring anywhere in the file, including explanatory prose. The meaning is unchanged; only the literal word choice moved, matching the project's established pattern of rewording prose to satisfy grep-based acceptance criteria (Phase 107-01 precedent).
- Factored `_select_0x0d_chips` / `_assert_chip_id_check_false` as shared helpers so the non-vacuity test calls the exact code path the real-DB test calls, not a parallel reimplementation — mirrors the `test_check_dispatch_invariants.py` analog's "Non-vacuous proof" convention.
- `test_sdp_table_parity.py`'s fail-closed-seam test (`test_missing_override_path_fails_closed`) carries no `FW_ABSENT` skip marker even though its sibling tests do — it only exercises the override branch of `_sdp_src_path()` against a literal nonexistent path and never touches the real firmware checkout, so it stays meaningful (and runs) even in standalone `firestarter_app` CI where the firmware sub-repo is absent.

## Deviations from Plan

None — plan executed exactly as written. The docstring wording adjustment above is a literal-substring accommodation for the plan's own grep-based acceptance criterion, not a scope or behavior deviation.

## Issues Encountered

- `ruff format` reformatted `test_sdp_table_parity.py` on first pass (line-wrapping/spacing normalization identical in kind to 116-02's `gen_sdp_bus_config.py` experience) — applied directly, re-verified `ruff check` + `ruff format --check` + the full test module clean afterward.
- Ran the full `firestarter_app` pytest suite (not just the two new modules) to satisfy the plan's "no new failures beyond known pre-existing ones" acceptance criterion: exactly one failure, `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches`, matching the pre-existing golden-fixture drift documented in project memory (`reference_audit_coverage_matrix_golden_stale.md`) — not caused by this plan, out of scope, left untouched.

## Known Stubs

None.

## Threat Flags

None — both new modules are read-only test surface; no new network endpoints, auth paths, or schema changes.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- TRACE-05 is now a machine-checked, non-vacuous, always-running (no skip marker) fact: the `0x0D` identity gate is dead across exactly 84 chips. `CLOSE-01`'s "84-chip count unchanged" fact has a home five phases early.
- RESEARCH F6 / Open Question 3's transcription-gap risk is closed: the unlock table the firmware trace suites (Plan 116-05/06) will `#include` and drive via `flash_utils.h`'s `FLASH_DISABLE_WRITE_PROTECTION` is now pinned equal to the shipped `EEPROM_SDP_DISABLE` by an executable, non-vacuous gate.
- `chip_database.json` stayed byte-untouched throughout (`git status --short firestarter/data/chip_database.json` empty; `diff_db.py` reports only the pre-existing 2-chip PGSZ delta, unrelated to this plan).
- No blockers for the remaining Wave 2 sibling (116-04, planted-`LOG_` timing-window scan) or Wave 3 (116-05, the always-green SDP harness suite).

---
*Phase: 116-ground-truth-trace-harness*
*Completed: 2026-07-27*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_sdp_db_invariant.py`
- FOUND: `firestarter_app/tests/test_sdp_table_parity.py`
- FOUND: `.planning/phases/116-ground-truth-trace-harness/116-03-SUMMARY.md`
- FOUND commit `af521c4` (firestarter_app): test(116-03) test_sdp_db_invariant.py
- FOUND commit `c5eb17d` (firestarter_app): test(116-03) test_sdp_table_parity.py
