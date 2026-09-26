---
phase: 108-test-plan-engine-address-derived-pattern-fingerprint
plan: 03
subsystem: testing
tags: [python, chip-database, test-plan-derivation, sweep-engine]

# Dependency graph
requires:
  - phase: 108-02
    provides: address_fold_byte/generate_pattern/prepass_images/_diff_offsets/Fingerprint/classify_fingerprint in chip_test.py
provides:
  - "derive_plan(name, db, *, destructive=False) -> Plan — guard-bypassing per-chip test-plan derivation"
  - "Step / Plan dataclasses — the step-descriptor record shape (op, supported, reason, destructive)"
  - "Protocol-driven op-inclusion rules: id-first, erase NA (flash4 0x05 / UV-EPROM), blank-check NA (SRAM/FRAM)"
affects: [108-04, 109]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Guard-bypassing derivation: db.get_eprom -> db.convert_to_programmer, never chip_resolver.resolve_chip"
    - "destructive kwarg annotates write/erase steps but never strips them from the plan"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_chip_test.py

key-decisions:
  - "id-check NA rule keyed on the programmer-dict chip-id sentinel value 0 (not key presence) — every DB entry carries a chip-id key, but UV-EPROM and many EEPROM entries carry the literal sentinel 0 meaning no real id to compare"
  - "blank-check NA condition checks BOTH electrical-type in {SRAM,FRAM} AND protocol-id in the SRAM proto-id set (0x0E/0x27/0x28/0x29), mirroring check_eprom_blank's own short-circuit exactly so derive_plan owns the decision up front rather than relying on the operator call"
  - "No named protocol constant exists for flash4 (0x05) in constants.py; used a local module constant _PROTOCOL_FLASH4 = 0x05 with a comment explaining why, mirroring database.py's own algo != 5 check rather than introducing a new cross-module constant"

patterns-established:
  - "Step/Plan dataclasses: every derived op carries supported (bool) + reason (str), destructive (bool) is annotation-only in this plan"

requirements-completed: [SWEEP-01]

coverage:
  - id: D1
    description: "derive_plan reads DB fields via get_eprom + convert_to_programmer only, never calls resolve_chip — works even for support_status-refused chips"
    requirement: "SWEEP-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_reads_via_get_eprom_and_convert_to_programmer_only"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_never_calls_resolve_chip"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_bypasses_guard_for_non_supported_chip"
        status: pass
    human_judgment: false
  - id: D2
    description: "id-check is ordered first in every derived plan"
    requirement: "SWEEP-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_id_check_first"
        status: pass
    human_judgment: false
  - id: D3
    description: "erase step is NA for flash4 (0x05) and UV-EPROM; supported when FLAG_CAN_ERASE set and protocol != 0x05"
    requirement: "SWEEP-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_flash4_erase_na"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_uv_eprom_erase_na"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_eeprom_erase_supported_when_can_erase_set"
        status: pass
    human_judgment: false
  - id: D4
    description: "blank-check is NA for SRAM/FRAM chips, decided by derive_plan up front"
    requirement: "SWEEP-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_blank_check_na_for_sram_chip"
        status: pass
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_blank_check_supported_for_regular_eeprom"
        status: pass
    human_judgment: false
  - id: D5
    description: "FLAG_CAN_ERASE imported from firestarter.constants, not redefined; no runtime classify() call in chip_test.py"
    requirement: "SWEEP-01"
    verification:
      - kind: unit
        ref: "tests/test_chip_test.py#test_derive_plan_flag_can_erase_imported_not_redefined"
        status: pass
      - kind: other
        ref: "grep -c 'classify(' firestarter_app/firestarter/chip_test.py"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-07-02
status: complete
---

# Phase 108 Plan 03: Guard-Bypassing Test-Plan Derivation Summary

**Added `derive_plan()` to `chip_test.py` — derives an ordered, per-chip op list (id/read/blank-check/write/verify/erase) strictly from frozen DB fields via `get_eprom`/`convert_to_programmer`, structurally bypassing `resolve_chip`'s support-status guard so coverage-expansion chips (even `adapter-required` ones) still get a plan.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-07-02T17:58:33Z
- **Completed:** 2026-07-02T18:12:23Z
- **Tasks:** 2 (single TDD cycle covering both — the op-inclusion rules extend the same function derive_plan established)
- **Files modified:** 2

## Accomplishments
- `derive_plan(name, db, *, destructive=False) -> Plan` reads `db.get_eprom(name)` then `db.convert_to_programmer(full)` ONLY — never `chip_resolver.resolve_chip` — proven by a spy `Mock(spec=["get_eprom", "convert_to_programmer"])` DB and a `monkeypatch` assertion that `resolve_chip` is never invoked.
- A non-supported chip (`AT28C04,AT28HC04`, `support_status: adapter-required`, which `resolve_chip` would refuse) still yields a full 6-step plan — the guard-bypass is real, not just documented.
- `Step`/`Plan` dataclasses give the step-descriptor shape: `op`, `supported` (bool), `reason` (str, always populated when `supported=False`), `destructive` (bool).
- id-check is always `steps[0]` (SWEEP-03 ordering precondition); NA when the chip's programmer-dict `chip-id` is the sentinel `0` (no real id to compare — verified against real UV-EPROM/EEPROM DB entries), supported when nonzero.
- read/verify always supported; write always supported and flagged `destructive=True`.
- blank-check NA for SRAM/FRAM — decided by `derive_plan` itself (checking both `electrical-type` and the `_SRAM_PROTO_IDS` set `{0x0E,0x27,0x28,0x29}`, mirroring `check_eprom_blank`'s own short-circuit) rather than relying on the operator's own guard.
- erase supported only when `FLAG_CAN_ERASE` is set AND `protocol != 0x05` (flash4 auto-erases per page, flag deliberately clear — Pitfall 6); NA for UV-EPROM (never has the flag) and NA for flash4 with a distinct reason string.
- `destructive` kwarg is annotation-only in this plan — `derive_plan(..., destructive=False)` and `derive_plan(..., destructive=True)` return identical op sets; the `--destructive` plan-construction gate is Phase 109's responsibility.
- Zero runtime `classify()` calls (`grep -c 'classify(' chip_test.py` == 0) — all derivation reads frozen DB fields only.

## Task Commits

Both tasks landed as a single RED/GREEN TDD cycle inside the `firestarter_app` submodule (on branch `v1.21-community-chip-validation-command`), since Task 2's op-inclusion rules extend the exact same `derive_plan` function Task 1 established:

1. **Tasks 1+2 RED: failing tests for derive_plan** — `0ea2ce0` (test)
2. **Tasks 1+2 GREEN: derive_plan implementation** — `1205280` (feat)

**Plan metadata:** committed in the meta repo (this SUMMARY + STATE.md/ROADMAP.md).

## Files Created/Modified
- `firestarter_app/firestarter/chip_test.py` — added `derive_plan`, `Step`, `Plan`, op-name constants, `_PROTOCOL_FLASH4`, `_SRAM_FRAM_ETYPES`, `_SRAM_PROTO_IDS`
- `firestarter_app/tests/test_chip_test.py` — added 18 new tests for derivation (guard-bypass, ordering, erase/blank-check NA rules, destructive annotation)

## Decisions Made
- Used the sentinel-value check (`chip-id == 0`) rather than key-presence for the id-check NA rule — every real DB entry carries a `chip-id` key (the earlier assumption in RESEARCH.md's Open Question 2 that some entries lack the key was refuted against the live DB; the sentinel `0` is how "no real id" is actually encoded in `convert_to_programmer`'s output).
- `_SRAM_PROTO_IDS` duplicated verbatim from `eprom_operations.py`'s `_SRAM_PROTO_IDS` (same four values) rather than importing it, to keep `chip_test.py` import-light and avoid a dependency on `eprom_operations.py` for a 4-element frozenset — matches the established pattern of copying the small `_diff_offsets` divergence math in 108-02 rather than importing it.
- No named protocol constant exists for `0x05` (flash4) anywhere in `constants.py`; added a local `_PROTOCOL_FLASH4 = 0x05` module constant in `chip_test.py` with a comment pointing to `database.py`'s own `algo != 5` check, rather than inventing a new cross-module constant.

## Deviations from Plan

None - plan executed exactly as written. Task 1 and Task 2 were implemented as a single TDD cycle (one RED commit, one GREEN commit) because Task 2's op-inclusion rules are additions to the exact same `derive_plan` function body Task 1 established, not a separable second pass — this is a scope/sequencing choice, not a deviation from any locked decision or acceptance criterion. All of Task 1's and Task 2's acceptance criteria are independently verified in the test suite and via the grep-based acceptance checks specified in the plan.

## Issues Encountered
- Initial test fixtures assumed `M8720` (protocol 0x08, EEPROM) had a nonzero chip-id per an earlier probe that only checked key presence (`'chip-id' in p`), not value. Re-verified against the live DB and found `M8720`'s chip-id is actually the sentinel `0`; switched the "id-supported" and "erase-supported-with-real-id" fixtures to `AS29F002T` (protocol 0x06, Flash/EEPROM, chip-id 21168, `FLAG_CAN_ERASE` set) — a real chip verified against the shipped `chip_database.json` this session. No functional impact; caught before the GREEN commit.
- `ruff format` reformatted `chip_test.py`'s comment-block whitespace in the new derivation section (no logic change) — applied and re-verified all 32 tests in the file still pass before committing.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `derive_plan` + `Step`/`Plan` are ready for Plan 108-04's `run_plan` (the guard-honoring, non-fatal executor) to consume: each step descriptor already carries enough information (`op`, `supported`, `reason`, `destructive`) for `run_plan` to iterate and, for `supported=True` steps, re-resolve via `chip_resolver.resolve_chip` before calling the corresponding `EpromOperator` method.
- `chip_test.py` verification suite: `python -m pytest tests/test_chip_test.py -q` → 32/32 pass. Full app suite: `python -m pytest -q` → all pass except the pre-existing, out-of-scope `tests/test_audit_coverage_matrix.py::test_golden_file_matches` golden-fixture drift (tracked from Phase 106-01, unrelated to this phase — confirmed unaffected by this plan's diff).
- `ruff check` + `ruff format --check` both pass on `firestarter/chip_test.py` and `tests/test_chip_test.py`.
- No blockers for Plan 108-04.

---
*Phase: 108-test-plan-engine-address-derived-pattern-fingerprint*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/chip_test.py
- FOUND: firestarter_app/tests/test_chip_test.py
- FOUND commit: 0ea2ce0 (test(108-03): add failing tests for derive_plan guard-bypassing derivation path)
- FOUND commit: 1205280 (feat(108-03): add derive_plan guard-bypassing test-plan derivation (SWEEP-01))
