---
phase: 81-2516-db-entry-non-destructive-read-sweep
verified: 2026-06-24T09:00:00Z
status: passed
score: 5/5 success criteria verified
overrides_applied: 0
resolved_gaps:
  - truth: "Host suite is green (incl. 0xA4 guard) before any bench session"
    status: resolved
    resolution: "Root cause was a test-isolation weakness, NOT a snapshot needing the 2516 row (the proposed --snapshot-update would have BROKEN CI, where no ~/.firestarter override exists). The subprocess characterization goldens (test_list/info/search) invoked the real `firestarter` CLI which read the developer's ~/.firestarter/database.json, leaking the Phase 81 2516 override into list output (CI stayed green). Fixed by adding a FIRESTARTER_CONFIG_DIR env seam in firestarter/config.py (default behavior unchanged) and pointing the subprocess test harness at an empty temp dir — mirroring EpromDatabase(skip_local_override=True) at the process boundary. HOME could not be used (the editable user-site install of firestarter + deps is HOME-relative). Full suite now green at 651 passed WITH the 2516 override installed; the 0xA4 guard test_init_phase_data_frames_not_acked is among the 651."
    commit: "837321d (firestarter_app submodule, branch v1.15-bench-validation-of-operator-inventory)"
---

# Phase 81: 2516 DB Entry + Non-Destructive Read Sweep — Verification Report

**Phase Goal:** Author the `2516` user-override entry and establish the milestone's evidence record + bench-safety baseline by reading and blank-checking all 11 chips on Leonardo + Rev 2.0 — zero chips consumed, validating the read path and DB decode for every chip, and discovering the blank-state that gates every UV-EPROM write decision.

**Verified:** 2026-06-24T09:00:00Z
**Status:** gaps_found — 4/5 success criteria VERIFIED, 1 FAILED (snapshot test breakage)
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter info 2516` decodes algorithm 0x0B / DIP24_2716 / UV-EPROM / vpp_mv 25000 / 2048 bytes from a manually safety-reviewed user-override entry (operator signed) | VERIFIED | Live run confirmed: Protocol ID: 0x0B, VPP: 25.0v, Type: UV-EPROM, Memory size 0x800 (2048), `flags: 0x00000000` (no FLAG_CAN_ERASE). Entry in `~/.firestarter/database.json` under INTEL key, name-keyed. SR-1 checklist 6/6 items PASS. Operator Henrik signed `[x] Approved — Henrik / 2026-06-23`. |
| 2 | All 11 chips read end-to-end + blank-checked on Leonardo + Rev 2.0, zero chips consumed, each a row in EVIDENCE.{md,json} | VERIFIED | EVIDENCE.json confirmed: 11 cells, all verdicts final (no `pending`), 10 PASS + 1 ANOMALY (2516). All locked columns present. Python completeness check: `uv-blank-state-ok` + `pass-rows-ok`. Zero chips consumed (reads apply no VPP). Board=leonardo, shield=Rev 2.0 (operator-confirmed silkscreen), R1=270000, firmware 3.0.0b8. |
| 3 | The 3 UV-EPROM blank-states (ST M27C512, AM27C020, 2516) recorded — gating Phase 83 | VERIFIED | EVIDENCE.json `sweep_summary.uv_blank_states`: ST M27C512 = BLANK (stable all-0xFF, N=3), AM27C020 = NOT-BLANK (data present), 2516 = NOT-BLANK (read-unstable — 3 distinct SHAs; blank-state recorded as NOT-BLANK by inference). Gating note present: Phase 83 MUST NOT write 2516 until read path is stable. |
| 4 | Code review confirms FLAG_CAN_ERASE derived correctly for BOTH EEPROM and Flash/EEPROM; gap (if any) fixed + pinned by test; host suite green incl. 0xA4 guard | FAILED | DB-02 audit SOUND (chain verified at convert_to_programmer:605). Pinning test `test_convert_w29c040_flash_eeprom_flag_can_erase` exists and passes. 0xA4 guard `test_init_phase_data_frames_not_acked` passes. SAFE-03 parity confirmed. **BUT**: `tests/test_characterization.py::test_list` snapshot is BROKEN — 1 failed / 650 passed (out of 651 collected). The 2516 user-override causes `firestarter list` to emit a 2516 row; the pre-existing snapshot does not include it. Phase SUMMARY claimed "651 tests green" — inaccurate. |
| 5 | Every bench task records preconditions (board=Leonardo, shield=Rev 2.0, controller identity, live r1≈270000); no non-Leonardo read authoritative | VERIFIED | EVIDENCE.json header records: board=leonardo, shield=Rev 2.0 (operator-confirmed), controller=leonardo on /dev/ttyACM0, R1=270000, R2=44000, firmware 3.0.0b8. Per-task re-verification stated at Task 2 boundary. EVIDENCE.md reflects same. |

**Score:** 4/5 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tests/test_database_conversion.py` | Flash/EEPROM pinning test `test_convert_w29c040_flash_eeprom_flag_can_erase` | VERIFIED | Exists at line 107. Committed as 0cfc23b on `v1.15-bench-validation-of-operator-inventory`. Passes. Ruff clean. No new imports added. |
| `~/.firestarter/database.json` | 2516 user-override entry (name-keyed INTEL/2516) | VERIFIED | Present. `name: "2516"` under INTEL key confirmed. Decodes correctly via `firestarter info 2516`. `flags & 0x02 = 0` (UV-EPROM, no erase flag). |
| `.planning/phases/81-2516-db-entry-non-destructive-read-sweep/81-2516-SAFETY-REVIEW.md` | SR-1 checklist with 6 D-02 items + operator sign-off | VERIFIED | Exists. 6/6 D-02 items marked PASS with actual values. `vpp-pin` line present. Full `firestarter info 2516` transcript included. Operator sign-off: `[x] Approved — Henrik / 2026-06-23` at line 363. |
| `.planning/v1.15/bench/EVIDENCE.json` | 11 cells, locked columns, harness_version=81 | VERIFIED | `harness_version: "81"`, 11 cells, all required columns present (chip, family, board, shield, blank_state, op, sha256, verdict, anomalies), plus EVID extensions (read_count, blank_check_result). Python validation: `uv-blank-state-ok`, `pass-rows-ok`. |
| `.planning/v1.15/bench/EVIDENCE.md` | Human-readable 11-chip table with Verdict column | VERIFIED | Exists. 11 chip rows. Verdict column present. Contains "leonardo". Negative control note in header (EVID-03). UV gating blank-states section present. Phase 83 gate / Phase 84 FIX-01 section present. |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `~/.firestarter/database.json` (2516 name-keyed) | EpromDatabase._merge_databases add-new-item path | `name` key triggers add at database.py line 244-246 | VERIFIED | Python confirmed: `name-keyed: True`. `firestarter info 2516` exits 0 with correct decode. |
| `convert_to_programmer` electrical-type check | FLAG_CAN_ERASE (constants.py 0x02) | `electrical-type in ("EEPROM","Flash/EEPROM")` at line 605 | VERIFIED | One-liner confirmed `True`: W29C040/W29C020/W27C512 carry flag; M27C512 does not. Parity: `constants.py:80: FLAG_CAN_ERASE = 0x02` and `firestarter.h:60: #define FLAG_CAN_ERASE 0x02`. |
| `firestarter read` / bench sweep | `.planning/v1.15/bench/EVIDENCE.json` cells | per-chip SHA + blank-check recorded as a cell | VERIFIED | 10 PASS cells with sha256 + read_count=3; 2516 ANOMALY with sha256=null (3 distinct, unstable). |
| 2516 user-override (Plan 02) | the 2516 read (11th chip in sweep) | DB entry must exist before 2516 read resolves (D-10) | VERIFIED | Confirmed: 2516 entry installed before Plan 03 sweep; 2516 is the 11th chip in EVIDENCE with verdict=ANOMALY (the anomaly is a legitimate bench finding, not a missing entry). |

---

## Data-Flow Trace (Level 4)

Not applicable for this phase — no dynamic-data-rendering components (this phase produces JSON/markdown evidence files and tests, not UI components or API routes).

---

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `firestarter info 2516` decodes 0x0B/DIP24_2716/UV-EPROM/25000/2048 | `firestarter info 2516` | Exit 0; Protocol ID 0x0B; VPP 25.0v; UV-EPROM; Memory size 0x800; Flags 0x00000000 | PASS |
| FLAG_CAN_ERASE chain returns True for W29C040/W29C020/W27C512, False for M27C512 | Python one-liner | `True` | PASS |
| Flash/EEPROM pinning test passes | `pytest tests/test_database_conversion.py::test_convert_w29c040_flash_eeprom_flag_can_erase -q` | 1 passed | PASS |
| 0xA4 regression guard passes | `pytest tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -q` | 1 passed | PASS |
| Full host suite is green | `pytest -q` | **1 failed (test_list snapshot), 650 passed** | FAIL |
| EVIDENCE.json completeness | Python validation check | `uv-blank-state-ok`, `pass-rows-ok`, 11 cells, no pending | PASS |

---

## Requirements Coverage

| Requirement | Phase 81 Plans | Description | Status | Evidence |
|-------------|---------------|-------------|--------|----------|
| GRAD-01 | 81-02 | 2516 researched to datasheet level; absent from infoic.xml confirmed | SATISFIED | SUMMARY records: 28 hits for "2516" in infoic.xml are all `25160` SPI serial parts. Datasheet class (NMOS/DIP24/~25V/2KB/2716-read-compatible) captured. SAFETY-REVIEW.md §GRAD-01 section. |
| GRAD-02 | 81-02 | 2516 entry authored in `~/.firestarter/database.json`, manually safety-reviewed, operator-signed | SATISFIED | Entry verified live. SR-1 6/6 PASS. Operator sign-off `[x] Approved — Henrik / 2026-06-23`. `firestarter info 2516` shows correct decode. |
| SWEEP-01 | 81-03 | All 11 chips read + blank-checked on Leonardo + Rev 2.0, zero chips consumed | SATISFIED | 11 EVIDENCE cells, no pending, 0 chips consumed (reads apply no VPP). 10 PASS + 1 ANOMALY (2516). |
| SWEEP-02 | 81-03 | 3 UV-EPROM blank-states recorded | SATISFIED | ST M27C512 = BLANK, AM27C020 = NOT-BLANK, 2516 = NOT-BLANK (read-unstable). All three recorded in EVIDENCE.json `sweep_summary.uv_blank_states`. |
| EVID-01 | 81-02, 81-03 | Per-chip EVIDENCE.{md,json} with locked columns | SATISFIED | EVIDENCE.json: harness_version=81, 11 cells, all locked columns (chip, family, board, shield, blank_state, op, sha256, verdict, anomalies) + EVID extensions. EVIDENCE.md mirrors JSON. |
| EVID-02 | 81-02, 81-03 | No new harness or third-party dependency | SATISFIED | SUMMARY confirms no new dependencies. Reuses `firestarter` CLI and `dev consistency-check` only. No package installs (T-81-SC accepted). |
| EVID-03 | 81-03 | Each PASS verdict non-vacuous (N≥3 + negative control) | SATISFIED | EVIDENCE.json: all 10 PASS cells have `read_count: 3` and non-null sha256. Negative control fired twice: wrong-file verify RC=1 on W27C512 (Task 1) and ST M27C512 (Task 2). Noted in EVIDENCE.md header. |
| DB-02 | 81-01 | FLAG_CAN_ERASE correct for EEPROM and Flash/EEPROM; gap fixed + pinned by test | PARTIALLY SATISFIED | Audit: SOUND. Test `test_convert_w29c040_flash_eeprom_flag_can_erase` pinned and passes. 0xA4 guard green. Parity verified. **Gap**: `test_list` snapshot broken (see SC#4). REQUIREMENTS.md already marks DB-02 Complete. |
| SAFE-01 | 81-03 | Every bench task records preconditions (board, shield, controller, r1) | SATISFIED | EVIDENCE.json header + per-task records: board=leonardo, shield=Rev 2.0, controller=/dev/ttyACM0, R1=270000. Re-verified at Task 2 boundary. REQUIREMENTS.md marks SAFE-01 Pending (traceability not yet updated). |
| SAFE-02 | 81-01 | Host suite green incl. 0xA4 guard | PARTIALLY SATISFIED | `test_init_phase_data_frames_not_acked` passes. But full suite has 1 failing test (test_list snapshot). REQUIREMENTS.md marks SAFE-02 Complete — this is incorrect given the current state. |
| SAFE-03 | 81-01 | No non-Leonardo read authoritative; FLAG_CAN_ERASE parity confirmed | SATISFIED | Parity: `constants.py:80 FLAG_CAN_ERASE = 0x02` and `firestarter.h:60 #define FLAG_CAN_ERASE 0x02`. EVIDENCE.md explicitly states only Leonardo reads are authoritative. No non-Leonardo reads recorded. |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/tests/__snapshots__/test_characterization.ambr` | (snapshot file) | Snapshot pinned without 2516 — `firestarter list` now emits a 2516 row from user-override | BLOCKER | `test_list` fails: 1 failed / 650 passed. Phase SUMMARY claimed "651 tests green" which is inaccurate post-override-install. SC#4 requires host suite green — this directly fails that criterion. |

No `TBD`, `FIXME`, or `XXX` markers found in `tests/test_database_conversion.py` (the only file modified in git).

---

## Probe Execution

Step 7c not applicable — no probe scripts declared in plans or SUMMARY for Phase 81.

---

## Human Verification Required

None. All Phase 81 bench work is complete (operator-executed and reported). The human gate (operator sign-off on SAFETY-REVIEW.md) was satisfied: `[x] Approved — Henrik / 2026-06-23`. The bench sweep (Plan 03 Tasks 1 and 2) was operator-executed and results recorded in EVIDENCE.

---

## Gaps Summary

**1 BLOCKER gap preventing full "host suite green" (SC#4):**

The `tests/test_characterization.py::test_list` snapshot test is broken because the 2516 user-override entry in `~/.firestarter/database.json` causes `firestarter list` (run as a subprocess) to include a 2516 row that the snapshot was not pinned with. Result: 1 failed / 650 passed out of 651 total.

The fix is straightforward: run `python3 -m pytest tests/test_characterization.py::test_list --snapshot-update` to re-pin the snapshot to include the 2516 row, then commit the updated `.ambr` snapshot file. This is a one-command, low-risk fix — the snapshot is a characterization pin of the expected output, and adding the 2516 to the expected list is the correct outcome of this phase's work.

**Root cause of missed gap:** Plan 01 ran the suite and reported "651 passed" at a time when `~/.firestarter/database.json` either did not yet exist or was not yet causing the test_list failure (the override file is installed by Plan 02, which ran in parallel in Wave 1). The final suite run in the SUMMARY captures the state after the override was installed but the snapshot was not updated. The 81-REVIEW.md (code review) was scoped only to `tests/test_database_conversion.py` and did not re-run the characterization suite, so the snapshot failure was not caught in review.

**All other success criteria (SC#1, SC#2, SC#3, SC#5) are VERIFIED.** The 2516 entry is correct, the 11-chip sweep is complete, the UV blank-states are recorded, and the bench preconditions are documented. The snapshot fix is the only gap blocking this phase.

---

## Deferred Items

None identified. The 2516 ANOMALY verdict and Phase 84 FIX-01 flag are intentional outcomes per the plan's D-06/D-07 protocol — they are future-phase work, not gaps in Phase 81's goal.

---

_Verified: 2026-06-24T09:00:00Z_
_Verifier: Claude (gsd-verifier)_
