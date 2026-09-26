# SECURITY.md — Phase 76: spec-only-gaps-adapter-required-x88c64

**ASVS Level:** 1
**block_on:** high
**Audit date:** 2026-06-18
**Verdict:** SECURED — 6/6 threats closed, threats_open: 0

Phase 76 delivered two spec-only gap closures: (1) a named AT28C04/AT28C16
"adapter-required" rule arm + X88C64 reason-string reword in the host DB
pipeline (plan 76-01), and (2) documentation only — DIP24→DIP32 adapter pin-map
spec in two layers + X88C64 feasibility verdict (plan 76-02). The v1.13-close
invariant verified: NOTHING graduates to `supported` and NO firmware handler is
committed.

## Threat Verification

| Threat ID | Category | Disposition | Status | Evidence |
|-----------|----------|-------------|--------|----------|
| T-76-01 | Tampering | mitigate | CLOSED | `tools/build_db.py:454-459` — named arm sets ONLY `_support_status="adapter-required"` (more restrictive) + reason; does NOT touch `proto_id` (per WR-01 comment lines 419-429). `check_dispatch.py` PASS exit 0: 744 chips, 730 supported, 14 non-dispatchable, 0 violations, no chip newly supported. `diff_db.py` PASS exit 0: RULE_PHASE66 field-path set (`diff_db.py:215-220`) cannot explain a `support_status`-graduation or `programming.algorithm` delta — those would route to unexplained → exit 1. |
| T-76-02 | Elevation of Privilege | mitigate | CLOSED | `tools/build_db.py:361-370` — `if proto_id == 0x34:` sets `_support_status="protocol-not-implemented"` and the reworded reason; no "serial-parallel hybrid". Regenerated DB confirms X88C64P/X88C64S `support_status: protocol-not-implemented`, reason contains "protocol not implemented", no hybrid wording. No 0x34 firmware handler: `firestarter/src` + `include` grep finds only a CRC-table byte (`rurp_serial_utils.cpp:371`) and `DBG_ADDR_MASK 0x34` (`messages.h:157`) — neither is a dispatch handler. Chip stays fail-closed at firmware not_implemented guard. `diff_db.py` classifies X88C64P as reason-only RULE_PHASE66 delta. |
| T-76-03 | Tampering | accept | CLOSED | Accepted risk logged below. Named arm does static set-intersection (`build_db.py:451-454`) on chip names from the same upstream `infoic.xml` used by every prior DB phase; no new attack surface, no user-supplied input. |
| T-76-D1 | Tampering / Information disclosure | mitigate | CLOSED | Pin map re-verified against `pinouts.json` ground truth (76-02-SUMMARY Decisions; meta doc cites per-pin sources). `firestarter/doc/AT28C04-ADAPTER.md:101,122-127` documents the /WE reroute chip pin 21 → socket pin 30 against `DIP32_28C512_EEPROM` (8 references); NO `DIP32_STD` reference (grep count 0). Both adapter docs note 5V-only / no vpp-pin (no 12V hazard). Spec only — no chip graduated (verified by T-76-01/D3 gates). |
| T-76-D2 | Repudiation / over-trust | accept | CLOSED | Accepted risk logged below. `.planning/X88C64-FEASIBILITY.md` states explicit MEDIUM verdict, open ALE-routing question, LOW-confidence tWC assumption (Assumptions Log); D-01 forbids a handler this phase (`X88C64-FEASIBILITY.md:27` "No 0x34 firmware handler is committed this phase (D-01 locked)"). Documentation-only; fail-closed at firmware not_implemented guard until a handler is deliberately built. |
| T-76-D3 | Elevation of Privilege | mitigate | CLOSED | Plan 76-02 created only doc files (`firestarter/doc/AT28C04-ADAPTER.md`, `.planning/AT28C04-ADAPTER.md`, `.planning/X88C64-FEASIBILITY.md`) — `key-files.modified: []`. Cannot graduate any chip. Invariant additionally enforced by plan 76-01's green gates: `check_dispatch.py` exit 0 (no chip newly supported); `diff_db.py` exit 0 (no support_status graduation, no dispatch delta). |

## Host Guard (defence-in-depth, verified)

`firestarter/chip_resolver.py:54-57` — `resolve_chip` reads `support_status` and
raises `ChipNotImplementedError` for any status != `"supported"` BEFORE any wire
dict is built (`convert_to_programmer`). This refuses both adapter-required and
protocol-not-implemented chips at the host, independent of firmware behaviour.

## Accepted Risks Log

- **T-76-03 (Tampering — infoic.xml chip-name injection):** The named-arm
  classification keys on chip names parsed from the upstream `infoic.xml` via a
  static set-intersection. This is the same untrusted-XML ingress used by every
  prior DB phase; no new attack surface and no user-supplied runtime input.
  Worst case of a tampered name is misclassification, which is caught fail-closed
  by the host guard (non-supported stays refused) and by the diff_db/check_dispatch
  gates. Low value, accepted.
- **T-76-D2 (Repudiation / over-trust — X88C64 feasibility verdict):** The
  feasibility verdict is documentation only, explicitly MEDIUM, with an open
  ALE-routing question and a LOW-confidence tWC assumption logged. It cannot
  authorize a write path on its own; D-01 forbids a handler this phase and the
  chip remains fail-closed at the firmware not_implemented guard. The next
  milestone must perform bench verification before any handler ships. Accepted.

## Unregistered Flags

None. Both 76-01-SUMMARY (`## Threat Flags`) and 76-02-SUMMARY (`## Threat
Surface Scan`) report no new network endpoints, auth paths, file-access patterns,
or schema changes. No new attack surface mapped outside the threat register.

## Gate Evidence (re-run live during audit)

- `python tools/diff_db.py` → exit 0; 10-chip RULE_PHASE66 delta (9 AT28C04/16 + X88C64P), all reason-only; 0 new, 0 missing, 0 unexplained.
- `python tools/check_dispatch.py` → exit 0; 744 chips, 730 supported, 14 non-dispatchable, 0 non_supported_dispatchable, 0 dispatch regressions, 0 violations.
- Firmware `src/` + `include/` 0x34 grep → only CRC-table byte + DBG_ADDR_MASK; no handler.

## Security Audit 2026-06-18

| Metric | Count |
|--------|-------|
| Threats found | 6 |
| Closed | 6 |
| Open | 0 |

register_authored_at_plan_time: true — register sourced from the `<threat_model>` blocks in 76-01-PLAN.md and 76-02-PLAN.md; auditor verified each mitigation/acceptance against the implementation (mitigations exist; new-threat scan not performed, per the plan-time-register constraint).
