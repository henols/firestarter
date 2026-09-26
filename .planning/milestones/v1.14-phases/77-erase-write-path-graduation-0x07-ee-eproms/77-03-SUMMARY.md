---
phase: 77-erase-write-path-graduation-0x07-ee-eproms
plan: 03
subsystem: testing
tags: [safe-gates, check_dispatch, vpp-safety, parity, coverage, graduation-discipline]

requires:
  - phase: 77-erase-write-path-graduation-0x07-ee-eproms
    provides: Plan 01 canonical FLAG_CAN_ERASE edit on disk
provides:
  - post-edit SAFE-02/SAFE-03/SAFE-01 gate evidence (no code edits)
affects: [77-04]

tech-stack:
  added: []
  patterns: [post-edit-gate-evidence-capture]

key-files:
  created: []
  modified: []

key-decisions:
  - "SAFE-01 is N/A-no-refusal for Phase 77 (D-05): the 8 target chips are already support_status:supported, so there is NO resolve_chip host-guard refusal to remove"
  - "Treat ci.yml ruff scope (firestarter/ tests/) as the authoritative gate; package-wide `ruff check .` debt in tools/ + .github/ is pre-existing and out-of-gate"

patterns-established:
  - "SAFE graduation gates run AFTER the canonical edit, never before (Pitfall 6)"

requirements-completed: [SAFE-01, SAFE-02, SAFE-03]

duration: 5min
completed: 2026-06-22
---

# Phase 77 Plan 03: SAFE Graduation Gate Evidence Summary

**Gate-verification-only (no code edits): the full-DB VPP-safety gate, FLAG_CAN_ERASE firmware↔host parity, and resolve_chip non-refusal all hold post-edit; SAFE-01 is documented N/A-no-refusal per D-05.**

## Performance

- **Duration:** ~5 min
- **Tasks:** 3 (all gate runs, no files modified)
- **Files modified:** 0

## Accomplishments

### SAFE-02 — full-DB VPP-safety gate (post-edit, Pitfall 6)
`grep electrical-type firestarter/database.py` → present (Plan 01 landed). `python3 tools/check_dispatch.py` exit 0:
```
PASS: all 744 chips scanned; 730 supported; 14 chips confirmed non-dispatchable
(D-12: host guard covers non-supported chips with real handlers; non-handler outcomes also safe);
0 non_supported_dispatchable (gate GREEN because chip_resolver.resolve_chip refuses, not because sim pretends mem_type=None);
0 dispatch regressions; 0 consistency violations
```
Unchanged baseline — the flag-derivation refactor routes no chip's VPP above its family invariant (T-77-VPP mitigated).

### SAFE-03 — FLAG_CAN_ERASE parity preserved
`FLAG_CAN_ERASE = 0x02` in `firestarter/constants.py:80` and `#define FLAG_CAN_ERASE 0x02` in `firestarter/include/firestarter.h:60`. `pytest tests/test_revision_constants_parity.py::test_flag_values_match_firmware` → 1 passed. Neither constant was edited this phase (Plan 01 reads the flag, does not redefine it) — parity trivially held (T-77-SCOPE mitigated).

### SAFE-01 — N/A-no-refusal (D-05)
`pytest tests/test_chip_resolver.py` → 9 passed. Direct check: all 8 target 0x07 EE-EPROMs resolve WITHOUT refusal and carry FLAG_CAN_ERASE on the wire:
```
W27C512: algo=0x07 flag_can_erase=True resolve=OK   (DB record W27C512,W27E512 → 2 part numbers)
SST27SF512 / SST27VF512 / W27C257 / W27E257 / SST27SF256 / SST27VF256: algo=0x07 flag_can_erase=True resolve=OK
```
(7 DB records = 8 part numbers; the `W27C512,W27E512` entry is a dual-name record.) These chips are already `support_status: supported`, so there is **NO `chip_resolver.resolve_chip` host-guard refusal to remove** — unlike Phases 78-80. The evidence-gated FINAL step the SAFE discipline protects in Phase 77 is the `FLAG_CAN_ERASE` wiring itself (Plan 01), which lands before the bench proof (Plan 04). A downstream verifier should NOT hunt for a nonexistent refusal-removal task.

### Task 3 — full host suite + coverage
`python3 -m pytest --cov --cov-fail-under=70` → suite green (incl. the 3 Plan-01 tests + the Plan-02 D-07 test), **76.87% coverage** (≥70 ✓), 29 snapshots passed. `mypy firestarter/database.py` is informational only (database.py is NOT in the strict-mypy-8 list).

## Decisions Made
- SAFE-01 = N/A-no-refusal (D-05) — recorded above so the verifier does not fabricate a refusal-removal task.

## Deviations from Plan

### Note (not a regression): package-wide ruff scope vs CI gate
The plan's Task 3 verify ran `ruff check . && ruff format --check .` (whole package). That surfaces **4 pre-existing errors** (`tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `.github/scripts/update_version.py`, `tools/check_mypy_watermark.py` — I001/UP031 + format). These files:
- are **not** touched by Phase 77 (only `firestarter/database.py`, `tests/test_database_conversion.py`, `tests/test_eprom_operations.py` differ from `beta`),
- are **outside the authoritative CI ruff scope** — `.github/workflows/ci.yml` runs `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`, NOT `.`.

The authoritative CI-scoped gate is clean: `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` → all checks passed, 72 files formatted. The pre-existing tools/ + .github/ debt is left untouched (out of phase scope; would be a separate cleanup).

**Impact:** None on the phase deliverable. The edit sites are fully ruff-clean under the real gate.

## Issues Encountered
None beyond the out-of-scope ruff note above.

## Next Phase Readiness
- All software gates green. Plan 04 (Leonardo bench) is the remaining hardware graduation step — `autonomous: false`, requires the operator.

---
*Phase: 77-erase-write-path-graduation-0x07-ee-eproms*
*Completed: 2026-06-22*
