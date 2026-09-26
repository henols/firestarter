---
phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension
plan: 01
subsystem: database
tags: [build_db, decode, voltages, protocol_map, eprom, minipro]

# Dependency graph
requires:
  - phase: 56-snapshot-field-dictionary-corrected-docs
    provides: infoic-field-dictionary.md with verified minipro source citations for all 4 bugs

provides:
  - Corrected VCC_VOLTAGES table with nibbles 0x02 (4V) and 0x03 (4.5V)
  - Correct vcc/vdd label assignment (vcc=bits-11-8, vdd=bits-15-12)
  - interpret_timing returning raw microseconds for 0x07/0x08/0x0B (no x100 multiplier)
  - Canonical PROTOCOL_MAP with IC2_ALG_* names; excluded IDs documented as comments
  - KNOWN_PROTOCOLS and second-pass _etype set dropping 0x35/0x39
  - Focused regression tests in test_decoder.py (10 new assertions)
  - ruff-clean build_db.py (all bare excepts, import sort, format issues resolved)

affects: [57-02, 57-03, 58, 59]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - TDD RED→GREEN for decode table correctness assertions (import from tools.build_db in test class)
    - Citation comment pattern above lookup tables: [VERIFIED: minipro file#L{range} @ a8efaedc]
    - Excluded IDs documented as commented entries inside dict literal for traceability

key-files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/tests/test_decoder.py

key-decisions:
  - "DEC-04/03/05 fixes are surgical line-targeted edits verified against minipro commit a8efaedc"
  - "ruff format applied to pre-existing VPP_MV/KNOWN_PROTOCOLS style violations (pre-existing failures that blocked the plan's ruff gate)"
  - "Excluded PROTOCOL_MAP IDs (0x11/0x2A/0x2C/0x2E/0x35/0x39/0x3C) remain as commented lines for traceability, not deleted"
  - "Two-pass _etype structure (flags-based first pass + protocol-aware second pass) preserved intact for WARNING-5 and fm1608 override correctness"

patterns-established:
  - "Decode table correctness verified via TDD: RED tests written before production fix, GREEN on fix"
  - "VCC_VOLTAGES serves both vcc and vdd lookups (same tl866ii_vcc_voltages[] table in minipro)"

requirements-completed: [DEC-02, DEC-03, DEC-04, DEC-05]

# Metrics
duration: 26min
completed: 2026-06-08
---

# Phase 57 Plan 01: Decode Bug Fixes Summary

**Four confirmed build_db.py decode bugs fixed: VCC nibbles 0x02/0x03, vcc/vdd label swap, interpret_timing x100 multiplier, and PROTOCOL_MAP canonical IC2_ALG_* names — all verified against minipro commit a8efaedc**

## Performance

- **Duration:** ~26 min
- **Started:** 2026-06-08T13:00:00Z
- **Completed:** 2026-06-08T13:26:02Z
- **Tasks:** 3 (2 TDD, 1 auto)
- **Files modified:** 2

## Accomplishments

- BUG-1 (DEC-04): VCC_VOLTAGES now includes 0x02→"4V" and 0x03→"4.5V"; chips with these nibbles no longer silently default to "5V"
- BUG-3 (DEC-04): vcc/vdd labels corrected — vcc reads bits 11-8, vdd reads bits 15-12 (were swapped relative to minipro database.c#L921-923)
- BUG-2 (DEC-03): interpret_timing() removes x100 multiplier for 0x07/0x0B; all three timing protocols return raw microseconds; W27C512 will decode to "100 us" not "10000 us"
- BUG-4 (DEC-05): PROTOCOL_MAP uses canonical IC2_ALG_* names with 7 excluded IDs documented as comments; KNOWN_PROTOCOLS and second-pass _etype set drop 0x35/0x39
- 10 new focused regression tests in TestBuildDbDecodeCorrectness class
- All 480 tests pass; ruff check + ruff format --check clean; two-pass _etype structure preserved

## Task Commits

1. **Task 1 RED: VCC_VOLTAGES/interpret_timing failing tests** — `de18f06` (test)
2. **Task 1 GREEN: VCC_VOLTAGES nibbles and vcc/vdd swap** — `dc6e8e9` (feat)
3. **Task 2 GREEN: interpret_timing x100 fix + bare except + imports** — `8de307f` (feat)
4. **Task 3: PROTOCOL_MAP canonicalize + KNOWN_PROTOCOLS + _etype** — `0ccd5ea` (feat)

## Files Created/Modified

- `firestarter_app/tools/build_db.py` — VCC_VOLTAGES expanded; vcc/vdd labels corrected; interpret_timing rewritten; PROTOCOL_MAP canonical; KNOWN_PROTOCOLS cleaned; _etype second-pass set cleaned; ruff format applied
- `firestarter_app/tests/test_decoder.py` — Added TestBuildDbDecodeCorrectness class with 10 assertions for all four decode bugs

## Decisions Made

- Applied `ruff format` to build_db.py to resolve pre-existing VPP_MV/KNOWN_PROTOCOLS/PIN_MAP_TO_PINOUT style violations that were blocking the plan's ruff gate; this is a pure-style change with no logic impact
- Kept 0x11 (IC2_ALG_FWH) as a commented exclusion entry in PROTOCOL_MAP (real IC2_ALG constant, infeasible on RURP — preserve for traceability per Q2 resolved question in RESEARCH.md)
- The two `except:` bare excepts in the file were both fixed: one in interpret_timing (BUG-2 fix) and one in the main XML parsing loop (pre-existing ruff E722 violation triggered by I001 fix scope)
- Import sort (I001) fixed as part of Task 2 ruff compliance pass

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Applied ruff format to pre-existing style violations**
- **Found during:** Task 1 (ruff format --check on tools/build_db.py)
- **Issue:** VPP_MV was in compact multi-entry-per-line format; KNOWN_PROTOCOLS was a long one-liner; PIN_MAP_TO_PINOUT had column-aligned tuples — all pre-existing format violations that prevented ruff format --check from passing (required by plan acceptance criteria)
- **Fix:** Applied `ruff format tools/build_db.py` to normalize all style; confirmed only whitespace/alignment changes, no logic change
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** `ruff format --check tools/build_db.py` exits 0; all 480 tests pass
- **Committed in:** dc6e8e9 (part of Task 1 feat commit)

**2. [Rule 2 - Missing Critical] Fixed second bare except in main XML parsing loop**
- **Found during:** Task 2 (ruff check after fixing interpret_timing bare except)
- **Issue:** A second bare `except:` existed at line 369 (inside the main XML parsing loop). Ruff E722 violation.
- **Fix:** Changed `except:` to `except Exception:` matching the project idiom
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** `ruff check tools/build_db.py` exits 0; no BLE001/E722 remaining
- **Committed in:** 8de307f (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 2 - missing ruff compliance)
**Impact on plan:** Both auto-fixes were necessary for ruff gate compliance. No logic changes. No scope creep.

## Issues Encountered

None — all four bugs were locatable to exact lines as documented in the research file. The TDD RED/GREEN cycle confirmed the bugs were present before each fix.

## Next Phase Readiness

- build_db.py decode pipeline is correct for VCC nibbles, vcc/vdd assignment, timing, and protocol naming
- Wave-1 decode fix is complete — plan 57-02 (check_dispatch extension) can proceed in parallel
- Wave-2 DB regeneration (plan 57-03) is unblocked — it depends on both wave-1 plans landing
- chip_database.json was NOT regenerated in this plan (that is 57-03 after both wave-1 plans land)

## Self-Check

Files exist:
- `firestarter_app/tools/build_db.py` — modified (confirmed in place)
- `firestarter_app/tests/test_decoder.py` — modified (confirmed in place)

Commits exist in firestarter_app submodule (v1.11-infoic-decode-correctness branch):
- de18f06 test(57-01): add failing tests for VCC_VOLTAGES nibbles, vcc/vdd bits, interpret_timing
- dc6e8e9 feat(57-01): fix VCC_VOLTAGES nibbles 0x02/0x03 and vcc/vdd label swap (DEC-04)
- 8de307f feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts (DEC-03)
- 0ccd5ea feat(57-01): canonicalize PROTOCOL_MAP, KNOWN_PROTOCOLS, _etype set (DEC-05)

## Self-Check: PASSED

All files confirmed present. All 4 task commits confirmed in submodule git log. 480 tests pass. ruff check + format --check clean.

---
*Phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension*
*Completed: 2026-06-08*
