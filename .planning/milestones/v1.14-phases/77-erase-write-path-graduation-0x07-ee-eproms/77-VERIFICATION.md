---
phase: 77-erase-write-path-graduation-0x07-ee-eproms
verified: 2026-06-22T08:05:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 77: Erase Write-Path Graduation (0x07 EE-EPROMs) Verification Report

**Phase Goal:** Writing any of the 7–8 `electrical.type=="EEPROM"` chips on protocol 0x07 (W27C512/W27E512/W27C257/W27E257/SST27SF256/SST27SF512/SST27VF256/SST27VF512) auto-erases before programming, and the full write→erase→program→verify cycle is bench-proven clean on Leonardo. First graduation establishing the SAFE-01/02/03 host-guard-removal-last discipline. Host-only change.
**Verified:** 2026-06-22T08:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

The five must-have truths map to the four ROADMAP success criteria (SC#1 = ERASE-01 wiring + wire round-trip; SC#2 = bench cycle + SHA + negative control; SC#3 = chip-OUT 14V VPP under ceiling; SC#4 = SAFE-01/02/03 gates). All are independently verified against the live codebase, the live host suite, and an independent SHA corroboration of the bench artifact.

### Observable Truths

| # | Truth (ROADMAP SC) | Status | Evidence |
| - | ------------------ | ------ | -------- |
| 1 | SC#1 — `convert_to_programmer` sets FLAG_CAN_ERASE from `electrical-type` (not `info-flags & 0x10`); all 8 0x07 EE-EPROMs carry the flag; UV-EPROM stays clear | ✓ VERIFIED | `database.py:604-607` reads `electrical-type ∈ {"EEPROM","Flash/EEPROM"}`; no `info-flags & 0x10` in block. Live round-trip: all 8 targets `flags=2 can_erase=True` (wire `algorithm=0x7`); M27C512 (UV-EPROM) `can_erase=False`. 3 wire-level tests pass. Firmware guard at `eprom_operations.cpp:36` gates erase on `is_flag_set(FLAG_CAN_ERASE)`. |
| 2 | ERASE-01 (D-07) — INIT/END DATA frames not acked; `send_ack` fires once per phase so auto-erase default write cannot re-trigger 0xA4 | ✓ VERIFIED | `test_init_phase_data_frames_not_acked` (test_eprom_operations.py:135-165) drives `_execute_phase("INIT", ...)` with DATA,DATA,INIT and asserts `send_ack.assert_called_once()`. Substantive (real MagicMock side_effect, real EpromOperator). Test PASSES. |
| 3 | SC#4 / SAFE-02 — full-DB VPP-safety gate green post-edit | ✓ VERIFIED | `python3 tools/check_dispatch.py` exit 0: "all 744 chips scanned; 730 supported; 14 confirmed non-dispatchable; 0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations". Re-run live this verification. |
| 4 | SC#4 / SAFE-03 — FLAG_CAN_ERASE 0x02 parity preserved, parity test green | ✓ VERIFIED | `constants.py:80 FLAG_CAN_ERASE = 0x02` == `firestarter.h:60 #define FLAG_CAN_ERASE 0x02`. `test_flag_values_match_firmware` PASSES. Phase diff touches neither constant. |
| 5 | SC#2 / SC#3 / ERASE-02 — Leonardo bench: clean no-`-b` write→auto-erase→program→verify, SHA match, wrong-file verify non-zero, 14V chip-OUT VPP under 22V ceiling | ✓ VERIFIED (operator bench + independent SHA corroboration) | 77-04-SUMMARY: Leonardo fw 3.0.0b8, Rev 2.0, /dev/ttyACM0, R1=270000; chip-OUT erase rail ≈14V (< 22V ceiling); seated non-blank W27C512 default write clean in 22.86s, no 0xA4; readback SHA = source SHA; wrong-file verify exit 1. **Independently corroborated:** `/workspaces/W27C512.bin` exists (65536 B) with SHA-256 `71189f7fb6aed638640078fba3a35fda6c39c8962e74dcc75935aac948da9063` — exactly the source+readback digest recorded. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `firestarter_app/firestarter/database.py` | `convert_to_programmer` reads `electrical-type` for FLAG_CAN_ERASE | ✓ VERIFIED | Lines 593-607: canonical derivation + D-01/D-02/D-03 in-code comments. Substantive, wired, data flows (live round-trip confirms). |
| `firestarter_app/tests/test_database_conversion.py` | 3 wire-level FLAG_CAN_ERASE tests | ✓ VERIFIED | Lines 80-104: 3 named tests with real wire-output assertions incl. UV-EPROM `== 0` negative control. All pass. |
| `firestarter_app/tests/test_eprom_operations.py` | 0xA4 ack_data=False regression test | ✓ VERIFIED | Lines 135-165: `test_init_phase_data_frames_not_acked`, substantive, passes. |
| `77-03-SUMMARY.md` | Post-edit SAFE-02/03/01 gate evidence | ✓ VERIFIED | Records check_dispatch PASS, parity, SAFE-01 N/A-no-refusal (D-05); all re-confirmed live. |
| `77-04-SUMMARY.md` | Bench evidence (rev, port, r1, VPP, write log, SHA, exit code) | ✓ VERIFIED | Complete bench record; SHA digest independently corroborated against on-disk source file. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `convert_to_programmer` | wire JSON `flags` | `electrical-type ∈ {EEPROM,Flash/EEPROM}` | ✓ WIRED | Live: W27C512 wire `flags=2`, `algorithm=0x7`. |
| host FLAG_CAN_ERASE on wire | firmware `eprom_erase`/auto-erase | `is_flag_set(FLAG_CAN_ERASE)` | ✓ WIRED | `firestarter/src/eprom_operations.cpp:36`. Bench cycle exercised it end-to-end. |
| 0xA4 regression test | `EpromOperator._execute_phase` | mocked comm DATA,DATA,INIT → send_ack once | ✓ WIRED | Test drives the real method, passes. |
| Plan-01 edit | check_dispatch.py VPP gate | post-edit 0 violations | ✓ WIRED | 744 chips, 0 violations, live. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `database.py convert_to_programmer` | `simple_flags` / wire `flags` | `full_eprom_data["electrical-type"]` from `_map_data` (canonical field) | Yes — live round-trip yields `flags=2` for all 8 targets, `0` for UV-EPROM | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| 8 target chips carry flag, UV-EPROM clear | python round-trip over DB | all 8 `can_erase=True`, M27C512 `False` | ✓ PASS |
| 3 wire-level tests | `pytest -k flag_can_erase` | 3 passed | ✓ PASS |
| D-07 0xA4 regression | `pytest ...test_init_phase_data_frames_not_acked` | 1 passed | ✓ PASS |
| Full-DB VPP gate | `python3 tools/check_dispatch.py` | exit 0, 0 violations | ✓ PASS |
| FLAG_CAN_ERASE parity + resolver | `pytest test_revision_constants_parity::... test_chip_resolver` | 10 passed | ✓ PASS |
| Full host suite + coverage | `pytest --cov --cov-fail-under=70` | 77.95% cov ≥ 70 (gate exit 0); 2 bench-artifact fails (see below) | ✓ PASS (gate met) |
| Bench-artifact tests with clean config | `HOME=clean pytest test_no_programmer_found_{read,erase}` | 2 passed | ✓ PASS (root cause = live board on saved port, not phase diff) |

### Probe Execution

No conventional `scripts/*/tests/probe-*.sh` declared or implied for this phase. Bench proof was operator-driven via the firestarter CLI (recorded in 77-04-SUMMARY). N/A.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| ERASE-01 | 77-01, 77-02 | FLAG_CAN_ERASE wired from electrical.type, not info-flags & 0x10 | ✓ SATISFIED | database.py:605 + live round-trip + 3 tests + D-07 guard test |
| ERASE-02 | 77-04 | write→auto-erase→program→verify bench-confirmed on Leonardo with real W27C512 (14V chip-OUT VPP under ceiling) | ✓ SATISFIED | 77-04-SUMMARY operator bench; SHA digest independently corroborated |
| SAFE-01 | 77-03 | resolve_chip host-guard refusal removed only as FINAL step | ✓ SATISFIED (N/A-no-refusal, D-05) | 8 chips already `supported`; no refusal exists to remove. test_chip_resolver passes (9). Correctly documented so no fabricated task. |
| SAFE-02 | 77-03 | check_dispatch.py full-DB VPP gate passes after graduation | ✓ SATISFIED | 744 chips, 0 violations, live |
| SAFE-03 | 77-03 | firmware↔host FLAG_* parity preserved, parity tests green | ✓ SATISFIED | 0x02 == 0x02; parity test passes; neither constant edited |

All 5 requirement IDs declared across the 4 plans (ERASE-01, ERASE-02, SAFE-01, SAFE-02, SAFE-03) are accounted for and match the REQUIREMENTS.md mapping for Phase 77 exactly. No orphaned requirements.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (none) | — | No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER in any of the 3 modified files | — | Clean. Ruff check + format clean on all 3 in-scope files (CI-authoritative scope `firestarter/ tests/`). |

Note (not a gap): package-wide `ruff check .` surfaces 4 pre-existing errors in `tools/` + `.github/` — outside the CI ruff scope and untouched by this phase (documented in 77-03-SUMMARY). No impact on the deliverable.

### Test-Environment Note (NOT a gap)

`test_no_programmer_found_read` and `test_no_programmer_found_erase` FAIL in the full suite run **only because a live Leonardo is connected on `/dev/ttyACM0` and that port is saved in `~/.firestarter/config.json`**, so `find_and_connect` reaches the real board and bypasses the test's `comports()→[]` mock. Proven a bench artifact: both tests PASS when run against a clean config HOME (verified live this session). The Phase 77 diff is exactly 3 files (`database.py`, `test_database_conversion.py`, `test_eprom_operations.py` vs `beta`) — none touch port discovery. The coverage gate (`--cov-fail-under=70`) still exits 0 at 77.95%.

### Human Verification Required

None outstanding. The only inherently-physical work (live high-voltage erase rail, DMM VPP reading, destructive chip program) was a `checkpoint:human-verify` task already executed and operator-confirmed during Plan 04, with every acceptance criterion recorded AND the SHA-match digest independently corroborated against the on-disk source file this verification. No re-running of a destructive hardware cycle is warranted.

### Gaps Summary

No gaps. All 5 must-have truths VERIFIED against the live codebase, live host suite, the firmware guard source, and an independent SHA corroboration of the bench artifact. The phase goal — auto-erase wiring for the 8 0x07 EE-EPROMs plus a clean bench-proven write→erase→program→verify cycle on Leonardo, under the SAFE-01/02/03 discipline — is achieved.

Status note (informational, not a gap): the meta-repo `firestarter_app` gitlink is intentionally pinned (not bumped) per operator policy until the beta cut. Source commits (`92898f8`, `b55dd86`, `5d8a5b1`) confirmed present inside the submodule on branch `v1.14-feasible-gap-implementation`.

---

_Verified: 2026-06-22T08:05:00Z_
_Verifier: Claude (gsd-verifier)_
