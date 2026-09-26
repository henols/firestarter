---
phase: 76-spec-only-gaps-adapter-required-x88c64
verified: 2026-06-18T13:30:00Z
status: passed
score: 7/7 must-haves verified
overrides_applied: 0
re_verification: null
gaps: []
deferred: []
human_verification: []
---

# Phase 76: Spec-Only Gaps (adapter-required + X88C64) Verification Report

**Phase Goal:** The two spec-gated gaps are delivered as documented specs/classifications — NOT graduated to programmable. GAP-01: AT28C04/AT28C16 24-pin EEPROM `adapter-required` path has a documented pin-map/adapter spec + a `resolve_pinout_key`/named rule arm (NOT a resurrected guess table); chips remain `support_status: adapter-required` (refused in-host); graduation to `supported` is explicitly OUT of scope. GAP-02: X88C64 (0x34) re-classified with a datasheet-sourced feasibility verdict + protocol; no firmware handler committed — stays a documented feasible-candidate (no blind handler).
**Verified:** 2026-06-18T13:30:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | AT28C04/AT28C16 family chips are classified adapter-required by an explicit NAME-keyed rule arm in build_db.py | VERIFIED | `_AT28C_DIP24_NAMES` set (14 aliases) at line 435 of `build_db.py`; arm fires in main per-chip loop, after Site B |
| 2 | The AT28C04/AT28C16 adapter-required reason string references the adapter spec doc and starts with "adapter required:" | VERIFIED | All 9 adapter-required chips carry: `"adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical DIP24-to-DIP32 adapter; see firestarter/doc/AT28C04-ADAPTER.md"` |
| 3 | X88C64P unsupported_reason is datasheet-accurate and does NOT contain "serial-parallel hybrid" | VERIFIED | DB reason: `"protocol not implemented: 0x34 (XICOR X88C64P — parallel DIP24 5V EEPROM, 8051 multiplexed-bus interface (ALE/WR/RD); feasible-candidate, handler not implemented)"`. No "serial-parallel hybrid" present. |
| 4 | X88C64P support_status stays protocol-not-implemented; no chip becomes newly supported | VERIFIED | `check_dispatch.py`: 744 chips, 730 supported, 14 non-dispatchable, 0 violations. X88C64P remains `protocol-not-implemented`, algorithm=0x34 (0x34=52 decimal). |
| 5 | diff_db.py is green with RULE_PHASE66 reason-string delta (no support_status/dispatch delta) | VERIFIED | `diff_db.py` exits 0; 10-chip RULE_PHASE66 delta (9 AT28C04/16 + X88C64P); all reason-string-only, NO support_status or dispatch change for any chip |
| 6 | DIP24→DIP32 adapter pin-map spec exists in two lockstep layers; cites DIP32_28C512_EEPROM; documents /WE chip-pin-21→socket-pin-30 reroute | VERIFIED | `firestarter/doc/AT28C04-ADAPTER.md` (160 lines, operator-facing) and `.planning/AT28C04-ADAPTER.md` (282 lines, meta). Both contain `DIP32_28C512_EEPROM`, neither contains `DIP32_STD`. Both document pin 21→30 reroute. Operator doc cross-references meta doc. Meta doc has §6 Future Graduation Steps. |
| 7 | X88C64-FEASIBILITY.md exists with MEDIUM verdict, ALE/WR/RD protocol, STORE/RECALL correction, no 0x34 firmware handler committed | VERIFIED | `.planning/X88C64-FEASIBILITY.md` (284 lines): "MEDIUM — documented feasible-candidate"; explicitly states "NO STORE/RECALL pins"; documents ALE/WR/RD multiplexed-bus write protocol; cites `v1.13-PROTOCOL-ENUMERATION.md` row 0x34; "No 0x34 firmware handler is committed this phase (D-01 locked)". No new files in `firestarter/src/proms/` |

**Score:** 7/7 truths verified

---

### WR-02: Plan Must-Have vs Implementation Mismatch — Assessed as Benign

The plan's `must_haves.truths` stated "diff_db.py is green with **exactly a 1-chip** RULE_PHASE66 reason-string delta". The actual delta is **10 chips** (9 AT28C04/16 reason-string updates + X88C64P reword). The REVIEW (WR-02) flagged this as a plan/implementation contract mismatch.

Assessment: the 10-chip delta is electrically correct, gate-clean, and fully explained. The plan's Task 3 acceptance criteria prose acknowledged this possibility: "if diff_db reports additional adapter-required reason-string deltas they must also classify cleanly as RULE_PHASE66 with no status/dispatch change." The plan's `must_haves.truths` was an overstatement — it described only the X88C64P change and did not account for the fact that the named arm also overwrites the 9 AT28C04/16 chips' Site B reason strings with named-arm wording. The diff_db.py output confirms all 10 changed chips are RULE_PHASE66 (reason-string-only, no status/dispatch change). **This does not affect goal achievement.**

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | Named AT28C04/AT28C16 rule arm (D-03) + reworded X88C64 reason string (D-02) | VERIFIED | `_AT28C_DIP24_NAMES` at line 435; 0x34 reason at line 368; WR-01 comment corrected in 9ce42dd |
| `firestarter_app/tests/test_build_db_inclusion.py` | Two new Wave-0 regression tests | VERIFIED | `test_at28c16_named_arm_reason_mentions_adapter_doc` (line 475) and `test_x88c64p_reason_does_not_say_serial_parallel_hybrid` (line 504); both pass green (5/5 TestUnsupportedReasonStrings) |
| `firestarter_app/firestarter/data/chip_database.json` | Regenerated DB: named-arm reason + reworded X88C64 reason | VERIFIED | Codegen-driven (not hand-edited); 9 adapter-required chips carry named-arm reason; X88C64P reason is datasheet-accurate |
| `firestarter/doc/AT28C04-ADAPTER.md` | Operator-facing adapter pin-map spec | VERIFIED | 160 lines; 24-row pin table; DIP32_28C512_EEPROM; /WE reroute pin 21→30; cross-references meta doc |
| `.planning/AT28C04-ADAPTER.md` | Meta investigation-canonical adapter derivation | VERIFIED | 282 lines; per-pin source citations; §Future Graduation Steps; DIP32_28C512_EEPROM; consistent pin table with operator doc |
| `.planning/X88C64-FEASIBILITY.md` | X88C64 feasibility verdict + protocol write-up | VERIFIED | 284 lines; MEDIUM feasibility; STORE/RECALL correction ("NO STORE/RECALL pins"); ALE/WR/RD protocol; cites PROTOCOL-ENUMERATION 0x34 row |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `build_db.py` `_AT28C_DIP24_NAMES` | `chip_database.json` 9 adapter-required entries | `python tools/build_db.py` codegen | VERIFIED | All 9 adapter-required chips carry named-arm reason string referencing AT28C04-ADAPTER.md |
| `build_db.py` 0x34 reword | `chip_database.json` X88C64P entry | codegen | VERIFIED | X88C64P reason is datasheet-accurate; no "serial-parallel hybrid" |
| `chip_database.json` | `diff_db.py` gate | RULE_PHASE66 10-chip delta | VERIFIED | Exit 0; reason-string-only; no support_status/dispatch change |
| `chip_database.json` | `check_dispatch.py` gate | 744 chips 0 violations | VERIFIED | Exit 0; 730 supported; 14 non-dispatchable; 0 violations |
| `firestarter/doc/AT28C04-ADAPTER.md` | `.planning/AT28C04-ADAPTER.md` | cross-reference in operator doc | VERIFIED | Operator doc references ".planning/AT28C04-ADAPTER.md in the Firestarter meta-repo" |

---

### Data-Flow Trace (Level 4)

Not applicable — this phase produces documentation artifacts and DB classification entries. No component renders dynamic user-facing data from a query; the DB is codegen output verified by gate tools.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| diff_db.py gate green | `cd firestarter_app && python tools/diff_db.py` | Exit 0; 10-chip RULE_PHASE66 delta; 0 support_status/dispatch changes | PASS |
| check_dispatch.py gate green | `cd firestarter_app && python tools/check_dispatch.py` | Exit 0; 744 chips; 730 supported; 14 non-dispatchable; 0 violations | PASS |
| New tests pass | `pytest tests/test_build_db_inclusion.py::TestUnsupportedReasonStrings` | 5 passed | PASS |
| Full suite + coverage floor | `pytest --cov-fail-under=70` | 642 passed; 76.83% coverage (floor 70% held) | PASS |
| No 0x34 firmware handler | `ls firestarter/src/proms/` | No new files; only pre-existing handlers present | PASS |

---

### Probe Execution

No probes declared for this phase. Not applicable.

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| GAP-01 | 76-01, 76-02 | AT28C04/AT28C16 adapter-required path: documented pin-map/adapter spec + named rule arm; chips stay adapter-required; graduation out of v1.13 scope | SATISFIED | Named arm in build_db.py; spec in two layers (operator + meta); 9 chips adapter-required; check_dispatch 0 violations |
| GAP-02 | 76-01, 76-02 | X88C64 re-classified: feasibility verdict + protocol; handler only if fully spec'd + RURP-feasible — else documented feasible-candidate (no blind handler) | SATISFIED | X88C64-FEASIBILITY.md (MEDIUM verdict); reason reworded (datasheet-accurate); no 0x34 handler committed; support_status stays protocol-not-implemented |

Both v1.13 GAP requirements are SATISFIED. REQUIREMENTS.md traceability table shows GAP-01/GAP-02 → Phase 76 — verified consistent with implementation.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/tools/build_db.py` | 435 | `_AT28C_DIP24_NAMES` set rebuilt on each loop iteration (named as a module-level constant per convention, placed inside per-chip loop) | INFO (IN-01) | Performance: 14-element set reconstructed ~744 times. No behavior change. Convention inconsistency only. |
| `firestarter_app/tests/test_build_db_inclusion.py` | 481-482 | Docstring point 3 asserts negative ("Does NOT contain...") but no code assertion enforces it | INFO (IN-02) | Docstring overstates test contract. Positive check on AT28C04-ADAPTER.md incidentally distinguishes named-arm wording but explicit negative assertion is absent. |
| `firestarter_app/tests/test_build_db_inclusion.py` | 492-502 | `test_at28c16_named_arm_reason_mentions_adapter_doc` uses `assert found` but not `assert checked` — if all AT28C16 chips are reclassified away from adapter-required, inner assertions are vacuously skipped | INFO (IN-03) | Future regression risk: a build regression that graduated all AT28C16 chips to `supported` would cause this test to pass silently. Does not affect current correctness. |

No TBD/FIXME/XXX markers found in files modified by this phase. No blockers.

**WR-01 resolved:** The false safety-invariant comment (claiming proto_id was "already NON_DISPATCHABLE_ALGO from Site B") was identified by code review and corrected in commit `9ce42dd`. The current comment at lines 420-429 correctly describes the actual mechanism (proto_id stays 0x0D from infoic.xml; chips refused by support_status host guard, not proto_id demotion).

---

### Human Verification Required

None. All phase deliverables are verifiable programmatically:
- DB classification: verified via diff_db.py + check_dispatch.py + JSON inspection
- Spec documents: verified by content checks (DIP32_28C512_EEPROM, /WE reroute, STORE/RECALL correction, feasible-candidate verdict)
- No firmware committed; no hardware-in-the-loop required

---

### Gaps Summary

No gaps. All 7 must-have truths are verified. Both GAP-01 and GAP-02 requirements are satisfied. The phase goal is achieved:

- GAP-01: Named rule arm (`_AT28C_DIP24_NAMES`) in `build_db.py` classifies all 9 AT28C04/AT28C16 family chips as `adapter-required` with an explicit, declarative reason string referencing the adapter spec doc. Two-layer lockstep adapter pin-map spec authored and verified against pinouts.json ground truth.
- GAP-02: X88C64P reason string is datasheet-accurate (parallel DIP24, 8051 multiplexed-bus). No 0x34 firmware handler committed. Feasibility verdict doc (MEDIUM; STORE/RECALL corrected; ALE/WR/RD protocol documented) provides the canonical record.
- All gates green: diff_db.py (10-chip RULE_PHASE66, no status/dispatch change), check_dispatch.py (744/0), 642 tests passing, 76.83% coverage.

The WR-02 plan/implementation mismatch (1-chip vs 10-chip diff_db delta) is a benign plan documentation overstatement — the implementation is correct and all 10 changed chips classify cleanly as RULE_PHASE66 with no support_status or dispatch change.

---

_Verified: 2026-06-18T13:30:00Z_
_Verifier: Claude (gsd-verifier)_
