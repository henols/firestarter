---
phase: 81
slug: 2516-db-entry-non-destructive-read-sweep
status: verified
threats_open: 0
asvs_level: 2
created: 2026-06-24
---

# Phase 81 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

**Register origin:** authored at plan time (all 3 PLAN files carry a `<threat_model>` block) — VERIFY-MODE.
**Result:** SECURED — 10/10 threats CLOSED, threats_open: 0.

This is a doc/data/test + bench-evidence phase. The only production code touched is a `FIRESTARTER_CONFIG_DIR` test-isolation seam in `firestarter_app/firestarter/config.py` (default behavior unchanged when the env var is unset). No firmware production code changed. Threats T-81-03..09 are guarded by recorded, signed, evidenced human/bench compensating controls — legitimate mitigations for a hardware-bench phase touching an irreplaceable chip.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| DB decode → wire JSON `flags` → firmware write-init | An incorrect `FLAG_CAN_ERASE` derivation reaches the firmware erase-before-write guard; a wrongly-cleared flag skips auto-erase, a wrongly-set flag is firmware-inert on the 0x0D path | `flags` bitfield |
| Host test suite → bench session gate | A removed/red 0xA4 guard lets the empty-input desync regression resurface on every default EEPROM write | test pass/fail signal |
| `~/.firestarter/database.json` (user-override) → EpromDatabase merge → chip_resolver → wire JSON → firmware | The 2516 override bypasses `check_dispatch.py`/`diff_db.py` — a wrong vpp_mv / algorithm / pinout reaches hardware with zero automated software-layer protection | vpp_mv, algorithm, pinout |
| Manual safety review → operator sign-off → bench authorization | The human sign-off is the SOLE compensating control before Phase 83 writes the irreplaceable 2516 | sign-off token |
| physical chip → read path → recorded SHA/verdict | A read on a non-Leonardo board or wrong shield produces self-consistent garbage recorded as a false-PASS | SHA256 / blank-state |
| port assignment → bench command target | `/dev/ttyACM*` shuffle after a USB event can target the wrong board | controller identity |
| UV blank-state record → Phase 83 spend decision | A wrong blank-state gates an irreversible UV write decision on an irreplaceable chip | blank-state verdict |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-81-01 | Tampering | `convert_to_programmer` FLAG_CAN_ERASE derivation (Flash/EEPROM) | mitigate | `database.py:604-606` sets `simple_flags |= FLAG_CAN_ERASE` directly from `electrical-type in ("EEPROM","Flash/EEPROM")` (canonical field, not the synthetic `info-flags & 0x10` round-trip). Pinning test `test_convert_w29c040_flash_eeprom_flag_can_erase` (`test_database_conversion.py:107-116`) + UV negative control `test_convert_uv_eprom_no_flag_can_erase` (M27C512, line 90-95). Ran live: 2 passed. | closed |
| T-81-02 | Denial of Service | 0xA4 empty-input write desync guard | mitigate | `test_init_phase_data_frames_not_acked` (`test_eprom_operations.py`) ran live: 1 passed. Flagged in Plan 01 verify so a removed/red guard blocks progress. | closed |
| T-81-03 | Tampering | 2516 user-override `vpp_mv` (12000 vs 25000) | mitigate | SR-1 Item 2 (`81-2516-SAFETY-REVIEW.md:75-93`) verifies `vpp_mv = 25000` vs datasheet; `firestarter info 2516` transcript `VPP: 25.0v`; live DB readback = 25000; operator sign-off line 363. | closed |
| T-81-04 | Elevation of Privilege | 2516 reaching hardware bypassing check_dispatch/diff_db automated gates | mitigate | `81-2516-SAFETY-REVIEW.md` GATE-03 N/A note (user-overrides not scanned by check_dispatch.py) + SR-1 6/6 PASS (lines 322-331) + blocking-human operator sign-off `[x] Approved — Henrik / 2026-06-23` (line 363). Never auto-approvable. | closed |
| T-81-05 | Spoofing | wrong algorithm (0x07 12V vs 0x0B 25V NMOS) → wrong voltage | mitigate | SR-1 Item 1 (lines 54-71) verifies `algorithm = 0x0B` routes to `configure_eprom`; Item 3 (lines 97-125) confirms UV-EPROM, FLAG_CAN_ERASE NOT set (live flags=0x00). Plan 03 reads apply no VPP. | closed |
| T-81-06 | Spoofing | false-PASS read oracle (wrong board/shield) | mitigate | EVIDENCE.md SAFE-01 header (lines 5-12): board=leonardo, shield=Rev 2.0 (operator-confirmed), controller /dev/ttyACM0, R1=270000. All 10 PASS cells `read_count=3` + non-empty sha256 (validated: no bad-pass rows). Negative control fired RC=1 ×2 (W27C512, ST M27C512). | closed |
| T-81-07 | Tampering | stale R1 calibration → wrong VPP setpoint | mitigate | EVIDENCE.md calibration line: R1=270000, R2=44000 (not the 1000 default). Live `firestarter config` r1 readback recorded as first per-task precondition; re-verified at Task 2 boundary (`81-03-SUMMARY.md:50`). | closed |
| T-81-08 | Repudiation | port-identity drift targets wrong board | mitigate | `controller:` identity re-verified per task and at the Task 2 boundary (not session-start only) — `81-03-SUMMARY.md:50`. Board pinned to leonardo /dev/ttyACM0. | closed |
| T-81-09 | Information Disclosure | wrong UV blank-state mis-gates a Phase 83 irreversible write | mitigate | EVIDENCE.json `uv_blank_states` (validated live): ST M27C512=BLANK, AM27C020=NOT-BLANK, 2516=NOT-BLANK, each from N≥3 reads. The 2516's read instability is recorded as ANOMALY and GATES Phase 83 rather than producing a false blank-state (EVIDENCE.md lines 38-43). | closed |
| T-81-SC | Tampering | npm/pip/cargo installs | accept | See Accepted Risks Log. `git diff 26cc62d..837321d --name-only` shows only `config.py` + 2 test files — NO pyproject/requirements/setup change. EVID-02 upheld. | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-81-SC | T-81-SC | No package installs performed in this phase — all tooling (pytest/ruff/mypy/firestarter CLI) pre-installed; EVID-02 forbids new dependencies. Confirmed by diff: only `config.py` + 2 test files changed, no dependency-manifest delta. | Henrik (operator) | 2026-06-24 |

*Accepted risks do not resurface in future audit runs.*

---

## SAFE-03 Parity (firmware/host constant)

`FLAG_CAN_ERASE = 0x02` in both `firestarter_app/firestarter/constants.py:80` and `firestarter/include/firestarter.h:60`. Parity CONFIRMED.

---

## Note on the verifier's SC#4 finding

`81-VERIFICATION.md` (re-verified PASSED 5/5 per `de42bcd`) recorded a transient `test_list` snapshot break caused by the 2516 override leaking into a subprocess golden. This was a test-isolation weakness, not a threat-mitigation gap, resolved by the `FIRESTARTER_CONFIG_DIR` seam (commit `837321d`). The 0xA4 guard (T-81-02) and the FLAG_CAN_ERASE pinning test (T-81-01) both pass live in the current tree. No security threat is affected. The 2516 ANOMALY and FM1608 blank-check tooling gap are tracked as Phase 84 FIX-01 future work (functional, not security gaps).

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-24 | 10 | 10 | 0 | gsd-security-auditor (VERIFY-MODE, ASVS L2) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-24
