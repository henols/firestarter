---
phase: 77
slug: erase-write-path-graduation-0x07-ee-eproms
status: verified
threats_open: 0
asvs_level: 1
created: 2026-06-22
---

# Phase 77 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.
>
> Register origin: `register_authored_at_plan_time: true` — all 4 PLAN files carried a
> `<threat_model>` block. Verification confirmed each mitigation exists in the
> implementation (no retroactive-STRIDE construction required).

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| host DB → wire JSON | `convert_to_programmer` assembles the `flags` field; an incorrect flag changes firmware erase behavior | `flags` integer (FLAG_CAN_ERASE bit) |
| host → firmware (serial) | `flags` crosses into firmware `eprom_write_init`; FLAG_CAN_ERASE there governs the high-voltage erase rail | wire `flags`, 250000-baud COBS frames |
| host write state machine ↔ firmware | INIT/END-phase DATA frames cross the ACK handshake; an extra ACK desyncs the firmware RX buffer (the 0xA4 fault) | DATA progress frames + send_ack |
| host write command → firmware erase rail | FLAG_CAN_ERASE triggers `eprom_internal_erase`, routing the ~14V unregulated VPE/VPP rail to the socket | high-voltage analog (VPP/VPE) |
| post-write read → verify oracle | the verify board must be trustworthy; Leonardo is the only board not corrupted by the v1.9 read bug | readback bytes / SHA |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-77-SCOPE | Tampering | `convert_to_programmer` flag derivation + FLAG_CAN_ERASE constant | mitigate | Flag keyed to canonical `electrical-type ∈ {EEPROM,Flash/EEPROM}` (`firestarter_app/firestarter/database.py:605-606`); 3 wire-level lock tests pin EEPROM-set / UV-EPROM-clear / Flash-EEPROM-set (`tests/test_database_conversion.py:81-104`); `FLAG_CAN_ERASE = 0x02` parity host (`constants.py:80`) ↔ firmware (`include/firestarter.h:60`), parity test passes | closed |
| T-77-VPP | Information Disclosure / Elevation of Privilege / Damage (hardware) | erase-rail VPP routing · full-DB VPP dispatch · 0x0D `configure_eeprom28c` path | mitigate (+ accept on 0x0D) | `tools/check_dispatch.py` exit 0 — 744 chips scanned, 0 `non_supported_dispatchable`, 0 violations, no VPP above family invariant; 0x0D path (`firestarter/src/proms/eeprom_28c.cpp`) reads only `FLAG_FORCE`/`FLAG_SKIP_BLANK_CHECK`, never `FLAG_CAN_ERASE` → flag inert there (accepted as documented in-code); bench chip-OUT DMM ≈ 14V < 22V `RURP_VPP_CEILING_MV` (Plan 04 SC#3, operator-attested) | closed |
| T-77-A4 | Denial of Service | `EpromOperator._execute_phase` INIT/END DATA handling | mitigate | `test_init_phase_data_frames_not_acked` pins `ack_data=False` — `send_ack` fires exactly once per phase (`tests/test_eprom_operations.py:135`); bench live no-`-b` auto-erase write completed clean in 22.86s with no 0xA4 / empty-input desync (Plan 04 SC#2) | closed |
| T-77-FALSEPASS | Spoofing (false PASS) | post-write verify oracle board | mitigate | Leonardo-only oracle (v1.9 read bug corrupts other boards); independent readback SHA == source (`71189f7f…9063`); non-vacuous negative control `verify W27C512 wrong.bin` exits 1 (`0x00 != 0xff at 0x000000`) (Plan 04 SC#2) | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-77-01 | T-77-VPP (0x0D sub-case) | Setting FLAG_CAN_ERASE on Flash/EEPROM parts routed to the 0x0D `configure_eeprom28c` path is firmware-inert — that path never reads `FLAG_CAN_ERASE` (verified by grep: reads only `FLAG_FORCE`/`FLAG_SKIP_BLANK_CHECK`). No extra voltage routed; no code change required, documented in-code (D-03). | Henrik Olsson | 2026-06-22 |

*Accepted risks do not resurface in future audit runs. The 0x0D inert sub-case is the only "accept" disposition; all other T-77-VPP facets (erase-rail routing, full-DB dispatch) are mitigated and closed.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-06-22 | 4 | 4 | 0 | gsd-secure-phase (orchestrator-verified, plan-time register) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-06-22
