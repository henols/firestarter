---
phase: 109-destructiveness-gate-safety
plan: 01
subsystem: testing
tags: [chip_test, dev-test, safety-gate, uv-eprom, address-derived-pattern, firestarter_app]

# Dependency graph
requires:
  - phase: 108-test-plan-engine-address-derived-pattern-fingerprint
    provides: "derive_plan (annotate-only), generate_pattern/classify_fingerprint (region-parameterized), run_plan non-fatal executor"
provides:
  - "Plan.locked_destructive advisory field (structural, run_plan never iterates it)"
  - "derive_plan(destructive=False) structurally omits write/erase from Plan.steps"
  - "_UV_WRITE_REGION_LENGTH engine module constant + _write_region_for(eprom_data) selector"
  - "UV-EPROM top-anchored small write window [mem_size-256, mem_size) wired into _dispatch_multi_run"
affects: [110-diagnostic-report-provenance, 112-dev-test-handler-wiring]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Structural safety gate: destructive ops are omitted from an executable list at construction time, not runtime-skipped"
    - "Advisory-only companion field pattern (locked_destructive) for reporting without granting an execution code path"
    - "Dual-signal detection axis (electrical-type OR protocol-id) to bridge the guard-bypass-derivation vs guard-honoring-execution dict-shape gap"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "derive_plan(destructive=False) omits OP_WRITE/OP_ERASE from Plan.steps and records (op, reason) on the new advisory Plan.locked_destructive list; run_plan has no code path to iterate it (SAFE-01, D-01)"
  - "NA erase (UV-EPROM / flash4 / no FLAG_CAN_ERASE) is never added to locked_destructive — it was never a runnable step, so there is nothing to lock"
  - "UV detection at execution time uses algorithm == 0x0B (EPROM_LEGACY) as a fallback signal, because _dispatch_multi_run's eprom_data comes from resolve_chip's programmer dict which drops electrical-type; verified 0x0B is UV-EPROM-exclusive across the full chip database"
  - "_UV_WRITE_REGION_LENGTH (256) is a module constant never read from any DB field; memory-size only bounds window PLACEMENT (top anchor), never WIDTH (SC4)"
  - "UV chip with missing/too-small memory-size falls back to the engine default region rather than producing a negative start"

patterns-established:
  - "locked_destructive advisory field: recorded at plan-construction time, consumed only by future reporting/banner code, never by the executor"
  - "_write_region_for(eprom_data) -> (start, length): pure selector, accepts either the derivation-time full dict or the execution-time programmer dict"

requirements-completed: [SAFE-01, PATT-03]

coverage:
  - id: D1
    description: "derive_plan(destructive=False) structurally omits write/erase from Plan.steps; destructive=True keeps them exactly as Phase 108 produced them"
    requirement: SAFE-01
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_destructive_flag_strips_not_annotates"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_strip_default_only_destructive_ops_removed"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_destructive_keeps_and_empties_advisory"
        status: pass
    human_judgment: false
  - id: D2
    description: "Omitted write/erase steps are recorded on the advisory Plan.locked_destructive field; run_plan never iterates it"
    requirement: SAFE-01
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_advisory_populated_when_non_destructive"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_na_erase_advisory_only_records_write"
        status: pass
    human_judgment: false
  - id: D3
    description: "SAFE-02 guard-bypass derivation split preserved (derive_plan never calls resolve_chip; still reads get_eprom + convert_to_programmer only)"
    requirement: SAFE-01
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_never_calls_resolve_chip"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_derive_plan_reads_via_get_eprom_and_convert_to_programmer_only"
        status: pass
    human_judgment: false
  - id: D4
    description: "UV-EPROM chips write over a small top-anchored high-address window [mem_size-256, mem_size); non-UV chips keep the engine default region; the width is an engine constant no DB field can widen"
    requirement: PATT-03
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_uv_window_top_anchored_default_length"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_uv_window_scales_with_memory_size"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_nonuv_default_region_unchanged"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_cap_not_widenable_by_injected_db_field"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_cap_not_widenable_uv_missing_memory_size_falls_back_to_default"
        status: pass
    human_judgment: false
  - id: D5
    description: "The absolute region start flows into both generate_pattern and classify_fingerprint's addr_base at execution time (Pitfall 3); generate_pattern/classify_fingerprint bodies unchanged"
    requirement: PATT-03
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py::test_addr_base_absolute_matches_region_start"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_dispatch_multi_run_uses_selector_for_uv_chip"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_write_region_for_detects_uv_via_execution_time_programmer_dict"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py::test_generate_pattern_and_classify_fingerprint_source_unchanged"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-02
status: complete
---

# Phase 109 Plan 01: Destructiveness Gate + UV Write Cap Summary

**`derive_plan()` now structurally strips write/erase from non-destructive plans into an advisory `locked_destructive` list, and UV-EPROM chips get a 256 B top-anchored high-address write window enforced as an engine constant no DB field can widen**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-07-02T19:24:07Z
- **Completed:** 2026-07-02T19:42:11Z
- **Tasks:** 2
- **Files modified:** 2 (both inside `firestarter_app/` submodule)

## Accomplishments

- `Plan` dataclass gained an advisory-only `locked_destructive: list[tuple[str, str]]` field; `run_plan` has zero code path to iterate it, making the non-destructive safety gate structural rather than a runtime skip (SAFE-01, D-01).
- `derive_plan(destructive=False)` now omits `OP_WRITE`/`OP_ERASE` from `Plan.steps` entirely (instead of Phase 108's annotate-only behavior) and records `(op, reason)` tuples on `locked_destructive` for future banner/report consumption (Phase 110/112).
- `derive_plan(destructive=True)` is behaviorally unchanged from Phase 108 — write/erase remain in `steps`, `locked_destructive` stays empty.
- NA erase (flash4 auto-erase, UV-EPROM no electrical erase, `FLAG_CAN_ERASE` unset) is never added to `locked_destructive` — it was never runnable, so nothing is "locked."
- Added `_UV_WRITE_REGION_LENGTH = 256` engine module constant and `_write_region_for(eprom_data)` pure selector implementing the PATT-03 UV small-region cap: `[mem_size - 256, mem_size)` for UV-EPROM chips, the pre-existing engine default `(0, 256)` for everyone else.
- Wired the selector into `_dispatch_multi_run`, replacing the two hardcoded `_WRITE_REGION_START`/`_WRITE_REGION_LENGTH` uses with a per-chip `(start, length)` fed into both `generate_pattern` and `classify_fingerprint(addr_base=start)` — preserving Pitfall 3 (absolute-address addr_base wiring).
- `generate_pattern`/`classify_fingerprint` bodies are byte-for-byte untouched (verified via `git diff` and a source-inspection regression test).

## Task Commits

Both tasks committed atomically **inside the `firestarter_app` submodule** (branch `v1.21-community-chip-validation-command`):

1. **Task 1: derive_plan strip + Plan.locked_destructive advisory field (SAFE-01, D-01)** - `b2bdfae` (feat)
2. **Task 2: UV small-region top-anchored write cap replaces the stand-in (PATT-03)** - `c569b12` (feat)

**Meta plan-metadata commit:** recorded below (see Self-Check / final commit).

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` - `Plan.locked_destructive` field; `derive_plan` strip-when-non-destructive logic; `_UV_WRITE_REGION_LENGTH` constant + `_write_region_for` selector; `_dispatch_multi_run` now derives its write/verify region per-chip
- `firestarter_app/tests/test_chip_test.py` - inverted `test_derive_plan_destructive_flag_annotates_not_strips` → `test_derive_plan_destructive_flag_strips_not_annotates`; added strip/advisory/destructive-keeps/na-erase-advisory tests (Task 1); added UV-window/nonuv-default/cap-not-widenable/addr-base-absolute/execution-time-detection/source-unchanged tests (Task 2); fixed two pre-existing tests (`test_derive_plan_write_present_and_destructive`, `test_derive_plan_eeprom_erase_supported_when_can_erase_set`) that implicitly relied on Phase 108's annotate-only default by adding explicit `destructive=True`

## Decisions Made

- **UV detection at execution time uses `algorithm == 0x0B` as a fallback signal.** The plan's pattern guidance assumed `_dispatch_multi_run`'s `eprom_data` would carry `electrical-type` (as `derive_plan`'s `full` dict does), but tracing the real call chain (`run_plan` → `_resolve_or_none` → `resolve_chip` → `convert_to_programmer`) showed the dict `_dispatch_multi_run` actually receives is the **programmer dict**, which drops `electrical-type` entirely (only `derive_plan`'s guard-bypassing derivation dict has it). I verified across the full chip database that protocol-id `0x0B` (`EPROM_LEGACY`) is UV-EPROM-exclusive, and added it as a second detection signal alongside `electrical-type` so `_write_region_for` works correctly both for bench-free unit tests (passing the `full` dict) and for the real execution path (passing the resolved programmer dict). This is documented in-source and covered by a dedicated regression test (`test_write_region_for_detects_uv_via_execution_time_programmer_dict`).
- NA erase steps (unsupported for this chip regardless of the `destructive` kwarg) are never added to `locked_destructive` — only genuinely omitted-but-otherwise-runnable steps are advisory-listed, per the plan's `na_erase_advisory` behavior spec.
- Kept the `_WRITE_REGION_START`/`_WRITE_REGION_LENGTH` stand-in as the non-UV default region exactly as instructed, updating only its comment to note Phase 109 now owns the UV branch.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed two pre-existing tests that implicitly depended on Phase 108's annotate-only default**
- **Found during:** Task 1 (running the full `test_chip_test.py` suite after the strip change)
- **Issue:** `test_derive_plan_write_present_and_destructive` and `test_derive_plan_eeprom_erase_supported_when_can_erase_set` called `derive_plan(name, _REAL_DB)` without an explicit `destructive` kwarg, relying on Phase 108's default behavior (write/erase always present regardless of the kwarg). Once `derive_plan(destructive=False)` (the default) began omitting write/erase, both tests failed with "no step named 'write'/'erase' in plan."
- **Fix:** Added explicit `destructive=True` to both calls — this is exactly what each test intends to verify (a supported destructive step's `.supported`/`.destructive` flags), and destructive=True is the correct path to exercise that assertion post-Phase-109.
- **Files modified:** `firestarter_app/tests/test_chip_test.py`
- **Verification:** `pytest tests/test_chip_test.py -q` — full file green (63 tests, 0 failures)
- **Committed in:** `b2bdfae` (Task 1 commit)

**2. [Rule 1 - Bug] UV detection dict-shape mismatch between derivation-time and execution-time `eprom_data`**
- **Found during:** Task 2 (writing the `test_dispatch_multi_run_uses_selector_for_uv_chip` integration test)
- **Issue:** `_write_region_for(eprom_data)` implemented per the plan's literal wording (`eprom_data.get("electrical-type", "") == "UV-EPROM"`) worked for bench-free unit tests using `db.get_eprom(name)`'s `full` dict, but silently fell through to the non-UV default region when driven through the real `run_plan` → `resolve_chip` execution path, because that path's dict never carries `electrical-type`.
- **Fix:** Added `algorithm == 0x0B` (verified UV-EPROM-exclusive DB-wide) as an additional detection signal in `_write_region_for`, so the selector is correct under both dict shapes.
- **Files modified:** `firestarter_app/firestarter/chip_test.py`, `firestarter_app/tests/test_chip_test.py` (added a dedicated regression test)
- **Verification:** `test_dispatch_multi_run_uses_selector_for_uv_chip` and `test_write_region_for_detects_uv_via_execution_time_programmer_dict` both pass, proving the UV window applies correctly through the real `resolve_chip` execution path, not just the bench-free selector-only path
- **Committed in:** `c569b12` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs that would have silently broken correctness: stale test assumptions and a UV-detection blind spot at execution time). No scope creep; no architectural changes.

## Issues Encountered

None beyond the two auto-fixed items above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `Plan.locked_destructive` is ready for Phase 110's diagnostic report / SWEEP-05 banner to consume (N of M counting) without any further `chip_test.py` change.
- The UV small-region cap (`_write_region_for`) is fully wired into the execution path (`_dispatch_multi_run`) and unit-verified against both AM2716 (2048 B) and AM2732 (4096 B) — ready for Phase 111's voltage sampler and Phase 112's `dev test` CLI wiring to build on top without touching this selector.
- SAFE-02 (guard-bypass derivation / guard-honoring execution split) remains intact and is asserted by the pre-existing tests; no new VPP-set/raw-wire-dict/`--force` call sites were introduced (grep-verified).
- The `firestarter_app` gitlink was intentionally left un-bumped in the meta repo per standing policy (operator-gated at milestone close).

---
*Phase: 109-destructiveness-gate-safety*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: `.planning/phases/109-destructiveness-gate-safety/109-01-SUMMARY.md`
- FOUND: `firestarter_app/firestarter/chip_test.py`
- FOUND: `firestarter_app/tests/test_chip_test.py`
- FOUND: submodule commit `b2bdfae` (Task 1)
- FOUND: submodule commit `c569b12` (Task 2)
- FOUND: meta commit `12fadc6` (SUMMARY.md)
