---
phase: 58-pinout-re-derivation-24-pin-eeprom-unblock
verified: 2026-06-09T07:45:08Z
status: passed
score: 4/4
overrides_applied: 0
---

# Phase 58: Pinout Re-Derivation + 24-Pin EEPROM Unblock — Verification Report

**Phase Goal:** `resolve_pinout_key` is rebuilt on principled, minipro-source-grounded rules; the survey-built guess tables are retired; the 9 blocked 24-pin EEPROMs are exposed safely via the correct pinout and handler with a completed SR-1 safety review.
**Verified:** 2026-06-09T07:45:08Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The three guess tables (PIN_MAP_TO_PINOUT, PIN_MAP_PROTO_TO_PINOUT, DIP28_VARIANT_MAP) are replaced by a `resolve_pinout_key` grounded in decoded fields — no evidence-free entries remain | VERIFIED | `python3 -c "import tools.build_db as m; [assert not hasattr(m, n) for n in ['PIN_MAP_TO_PINOUT','PIN_MAP_PROTO_TO_PINOUT','DIP28_VARIANT_MAP']]"` exits 0; build_db.py line 125 is a deletion-comment; `TestGuessTablesDeleted` (3 tests) all pass; `resolve_pinout_key` is a pure branch on (pin_count, pm_idx, variant_lo, type_int, mem_size, proto_id) with no per-IC names |
| 2 | The three load-bearing safety overrides intact: WARNING-5 (DIP28_28C256+0x07+Flash/EEPROM → 0x0D), fm1608 (type=4+EPROM-family → 0x28), 24-pin EEPROM skip; `check_dispatch.py` returns 0 violations | VERIFIED | `python3 tools/check_dispatch.py` outputs "PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; 0 Flash/EEPROM chips route to configure_eprom; 0 wire-key regressions" (exit 0); CAT28C256 (the WARNING-5 regression case) has algorithm=0x0D in DB; 0 SRAM chips have EPROM algo; `TestWarning5Rule` passes GREEN |
| 3 | The 9 AT28C04/AT28C16-family chips appear in regenerated chip_database.json with algorithm=0x0D and a safe 24-pin DIP24_2816 pinout; `firestarter info AT28C16` returns a valid entry | VERIFIED | DB query confirms 19 chips on DIP24_2816/algo=0x0D (9 previously blocked + 10 previously dangerous); `firestarter info AT28C16` exits 0 showing Protocol=0x0D, R/W(WE) on pin 21; `TestDangerous24pinEEPROMFixed` (10 tests) all GREEN; no chip on DIP24_2816 has algo != 0x0D |
| 4 | SR-1 safety checklist completed: vpp-pin absent, rw-pin=WE, oe-pin/ce-pin correct, all 24 pins accounted for | VERIFIED | `58-SR-1-CHECKLIST.md` exists with all 9 SR-1 items for DIP24_2816 (item 1 PASS: vpp-pin absent; item 2 PASS: rw-pin=[21]=WE#; items 3-4 PASS: oe=[20] ce=[18]; items 5-6-7 PASS: vcc/gnd/address-bus; item 8 PASS: pin 21 not shared with VPP path; item 9 PASS: all 24 pins accounted for — 11+8+1+1+1+1+1=24); `firestarter_app/doc/pinout-safety-review.md` exists as operator-layer subset (two-layer lockstep per D-10) |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | Principled resolve_pinout_key + Rule 1/2/3 overrides + D-06 fail-safe; guess tables deleted | VERIFIED | Function at line 138, signature `(pin_count, variant, flags_int, pm_idx=None, proto_id=None, type_int=1, mem_size=0)`; deletion comment at line 125; D-06 fail-safe present; Rules 1/2/3 at lines 359/377/413 |
| `firestarter_app/firestarter/data/pinouts.json` | DIP24_2816 entry with no vpp-pin | VERIFIED | Entry present; pins: vcc=[24], gnd=[12], addr=[8,7,6,5,4,3,2,1,23,22,19], data=[9-11,13-17], ce=[18], oe=[20], rw=[21]; NO vpp-pin key |
| `firestarter_app/firestarter/data/chip_database.json` | 743 chips, DIP24_2816 used for 19 24-pin EEPROMs | VERIFIED | 743 total chips; 19 chips on DIP24_2816, all with programming.algorithm=13 (0x0D) |
| `firestarter_app/tests/test_decoder.py` | Five Wave 0 test classes (TestResolvedPinoutKey, TestGuessTablesDeleted, TestWarning5Rule, TestDIP24_2816Pinout, TestDangerous24pinEEPROMFixed) | VERIFIED | All 5 classes present; 36 tests collected; all 36 pass (pytest exit 0) |
| `.planning/phases/58-pinout-re-derivation-24-pin-eeprom-unblock/58-SR-1-CHECKLIST.md` | Full SR-1 planning artifact with DIP24_2816 checklist and all changed pinouts per D-11 | VERIFIED | File exists; covers DIP24_2816 (9 items), DIP24_2716, DIP24_6116, DIP28_28C256, DIP28_2764, DIP28_27512, DIP28_27256, DIP32 family; A1/A2 flagged; BENCH-01 deferral documented |
| `firestarter_app/doc/pinout-safety-review.md` | Operator-visible SR-1 subset (two-layer lockstep) | VERIFIED | File exists; contains DIP24_2816 guarantee, GATE-03 result, configure_eeprom28c safety statement, BENCH-01 deferral, minipro SHA citation |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----| ----|--------|---------|
| `tests/test_decoder.py` | `tools.build_db.resolve_pinout_key` | `from tools.build_db import resolve_pinout_key` inside test methods | WIRED | 16 TestResolvedPinoutKey tests import and call the function; all pass |
| `tests/test_decoder.py` | `firestarter/data/pinouts.json` | DIP24_2816 presence + no-vpp-pin assertions in TestDIP24_2816Pinout | WIRED | 6 tests assert key existence and pin assignments; all pass |
| `tools/check_dispatch.py` | `firestarter/data/chip_database.json` | GATE-03 full-class VPP-safety scan | WIRED | Reads chip_database.json; reports 0 violations on 743 chips |
| `58-SR-1-CHECKLIST.md` | `firestarter_app/doc/pinout-safety-review.md` | Two-layer lockstep (D-10) | WIRED | Operator doc is a strict content subset of planning artifact; both contain DIP24_2816 review and GATE-03 result |

### Data-Flow Trace (Level 4)

Not applicable — this phase produces static data files (JSON DB, pinouts.json) and build tooling, not dynamic UI components.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| GATE-03 returns 0 violations | `python3 tools/check_dispatch.py` | "PASS: all 743 chips ... 0 Flash/EEPROM chips route to configure_eprom" (exit 0) | PASS |
| AT28C16 is CLI-reachable with algo=0x0D | `firestarter info AT28C16` | Protocol: EEPROM (ID: 0x0D), pin 21 = R/W(WE), 24-pin DIP, exit 0 | PASS |
| All 36 Wave 0 tests GREEN | `python3 -m pytest tests/test_decoder.py -q` | "36 passed" (exit 0) | PASS |
| Full test suite green | `python3 -m pytest --tb=no` | "516 passed in 24.61s" (exit 0) | PASS |
| Guess tables absent from module | `python3 -c "import tools.build_db as m; assert not hasattr(m,'PIN_MAP_TO_PINOUT')"` | exit 0 | PASS |

### Probe Execution

No probe scripts declared or conventionally present for this phase.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PIN-01 | Plans 01, 02 | `resolve_pinout_key` re-derived from principled rules, replacing guess tables | SATISFIED | Three guess tables deleted; function is pure branch on decoded fields; TestGuessTablesDeleted + TestResolvedPinoutKey (19 cases) all green |
| PIN-02 | Plans 02, 03 | Safety overrides preserved/verified; no chip gains VPP-on-wrong-pin damage path | SATISFIED | GATE-03 = 0 violations / 743 chips; WARNING-5 (Rule 2) preserved; fm1608 (Rule 3) preserved; D-06 fail-safe present; TestWarning5Rule green |
| PIN-03 | Plans 01, 02, 03 | 9 blocked 24-pin EEPROMs exposed via DIP24_2816 + algo=0x0D; SR-1 reviewed | SATISFIED | AT28C04/AT28C16/28C04A/28C16A/UPD28C04 etc. all in DB with algo=0x0D + DIP24_2816; `firestarter info AT28C16` exits 0; both SR-1 doc layers present |

No orphaned requirements: REQUIREMENTS.md traceability table assigns PIN-01/02/03 exclusively to Phase 58; all three carry status "Complete".

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None found | — | No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER in modified files | — | — |

Note: The code review (58-REVIEW.md) identified 5 WARNING findings (WR-01 through WR-05) about robustness of the rule structure against future upstream XML drift. The reviewer confirmed "no shipping VPP-routing hazard in the current output" and "zero critical findings." GATE-03 provides mechanical proof of 0 violations. These are robustness/future-maintenance concerns, not current correctness failures. None contain unresolved debt markers referencing issues/PRs.

### Human Verification Required

No items require human verification for the phase goal as stated. The following items from the review are forward-action robustness improvements, not blockers to goal achievement:

- WR-01: 24-pin type=4 FRAM/SRAM with pm_idx=23 could resolve to a VPP pinout in a hypothetical future upstream XML change (no current chip affected; GATE-03 catches any regression)
- WR-02: Rule 2 DIP28_2764 arm relies on flags-based _etype which the codebase notes as unreliable for some 28C parts (currently safe; no 28C-family chip should reach DIP28_2764)
- BENCH-01: Real-hardware write/program validation deferred to v2 per REQUIREMENTS.md — explicitly out of scope for Phase 58

### Gaps Summary

No gaps. All 4 observable truths are VERIFIED by direct codebase evidence:

1. Three guess tables are absent from `tools.build_db` module at runtime; `resolve_pinout_key` function is a data-driven branch with no per-IC string literals.
2. GATE-03 (`check_dispatch.py`) returns 0 violations on all 743 chips with exit code 0; WARNING-5 and fm1608 overrides are present as named Rule 2 and Rule 3 in `main()`; full test suite (516 tests) passes.
3. 19 chips in `chip_database.json` have `pinout=DIP24_2816` and `algorithm=0x0D`; `firestarter info AT28C16` exits 0 showing Protocol=0x0D; all 10 TestDangerous24pinEEPROMFixed tests pass.
4. SR-1 planning artifact covers all 9 checklist items for DIP24_2816; operator-layer doc exists as a strict subset; both files contain the DIP24_2816 review and GATE-03 result.

---

_Verified: 2026-06-09T07:45:08Z_
_Verifier: Claude (gsd-verifier)_
