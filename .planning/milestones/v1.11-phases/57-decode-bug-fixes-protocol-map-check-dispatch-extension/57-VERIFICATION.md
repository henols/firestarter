---
phase: 57-decode-bug-fixes-protocol-map-check-dispatch-extension
verified: 2026-06-08T15:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 57: Decode Bug Fixes + PROTOCOL_MAP + check_dispatch Extension Verification Report

**Phase Goal:** All four confirmed decode bugs are fixed in `build_db.py` and the VPP-safety guard in `check_dispatch.py` covers the full chip set — not just the previously-audited `DIP28_2764` pinout — so no future re-derivation change can introduce an evasive VPP-routing regression.
**Verified:** 2026-06-08T15:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| #   | Truth                                                                                                                  | Status     | Evidence                                                                                           |
| --- | ---------------------------------------------------------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------- |
| 1   | `firestarter info W27C512` reports pulse_duration as 100 µs (DEC-03)                                                  | ✓ VERIFIED | CLI output shows "Pulse delay: 100µS"; DB entry shows "100 us"; interpret_timing('64',0x07)=='100 us' |
| 2   | VCC_VOLTAGES includes nibble 0x02 (4V) and 0x03 (4.5V); AT28C256-class chips decode correct VCC (DEC-04)             | ✓ VERIFIED | Code: VCC_VOLTAGES[0x02]=='4V', [0x03]=='4.5V'; DB: AT28C256 vcc='4V', vdd='5V'                   |
| 3   | vcc=bits-11-8 and vdd=bits-15-12 field names match minipro bit-field layout — swap corrected (DEC-04)                 | ✓ VERIFIED | build_db.py L582: (voltages>>8)&0x0F for vcc; L585: (voltages>>12)&0x0F for vdd; 10 tests pass    |
| 4   | PROTOCOL_MAP uses only canonical IC2_ALG_* names; 0x2A/0x2C/0x2E/0x35/0x3C removed or carry exclusion comments; phantom 0x39 documented (DEC-05) | ✓ VERIFIED | No NVRAM*/FLASH_4MB/FLASH_FWH/FLASH_INTEL_ALT/FLASH_EEPROM_LIKE in live values; excluded IDs as comments in dict literal |
| 5   | check_dispatch.py asserts no 5V Flash/EEPROM chip routes to configure_eprom — full chip set, not just DIP28_2764 — and exits 0 (GATE-03 — corrected implementation) | ✓ VERIFIED (corrected predicate) | Guard keys on `etype == "Flash/EEPROM" AND handler == "configure_eprom"`; fires on synthetic hazard input (exit 1); exits 0 on 734-chip regenerated DB |

**Score:** 5/5 truths verified

### Note on Success Criterion #5 (GATE-03) — Intentional, Justified Correction

The ROADMAP.md text for SC-5 specifies "algorithm in {0x05, 0x06, 0x0D}" as the trigger set. The code review (CR-01, 57-REVIEW.md) independently confirmed this literal phrasing is logically vacuous: `dispatch()` never returns `configure_eprom` for those protocols (they route to `configure_flash4`, `configure_flash3`, and `configure_eeprom28c` respectively). A guard keyed on that algorithm set combined with `handler == "configure_eprom"` can never fire.

The corrected implementation (commit ffa74b6) re-keys on `electrical.type == "Flash/EEPROM" AND handler == "configure_eprom"` — pinout-agnostic, a true superset of the WARNING-5 check, and actually reaches the `configure_eprom` path (which is driven by algorithms 0x07/0x08/0x0B). Verification confirmed the guard fires on a synthetic hazardous input (a Flash/EEPROM chip with proto=0x07 → exit 1 with GATE-03 FAIL message), and exits 0 on the full 734-chip regenerated database (0 Flash/EEPROM chips route to configure_eprom).

The corrected implementation satisfies the phase GOAL's stated intent ("no future re-derivation change can introduce an evasive VPP-routing regression") better than the literal {0x05,0x06,0x0D} phrasing would have. The ROADMAP.md SC-5 criterion text should be updated to reflect the corrected predicate.

A note on the PASS message wording: the plan (57-02) specified the PASS line include "vpp-pin Flash/EEPROM chips route to configure_eprom". The CR-01 fix removed the dynamic `_vpp_pinouts` frozenset (which also resolved WR-03 — the silent no-op risk if `pinouts.json` structure changed). The current PASS line says "0 Flash/EEPROM chips route to configure_eprom" — a stronger guarantee (covers all Flash/EEPROM chips regardless of pinout) at the cost of omitting the "vpp-pin" qualifier. This is a wording deviation, not a safety regression.

### Required Artifacts

| Artifact                                                               | Expected                                   | Status     | Details                                                    |
| ---------------------------------------------------------------------- | ------------------------------------------ | ---------- | ---------------------------------------------------------- |
| `firestarter_app/tools/build_db.py`                                    | Corrected decode tables + interpret_timing | ✓ VERIFIED | Contains VCC_VOLTAGES with 0x02/0x03; vcc bits-11-8; vdd bits-15-12; interpret_timing no x100; PROTOCOL_MAP canonical names; KNOWN_PROTOCOLS without 0x35/0x39 |
| `firestarter_app/tests/test_decoder.py`                                | Regression tests for four decode fixes     | ✓ VERIFIED | TestBuildDbDecodeCorrectness class with 10 assertions — all pass |
| `firestarter_app/tools/check_dispatch.py`                              | Full-class VPP-safety guard + 0x35/0x39 sync | ✓ VERIFIED | GATE-03 guard active; 0x35/0x39 absent; exits 0 on 734-chip DB |
| `firestarter_app/firestarter/data/chip_database.json`                  | Regenerated DB with corrected values       | ✓ VERIFIED | 734 chips; W27C512 pulse_duration="100 us"; AT28C256 vcc="4V" |
| `firestarter_app/tests/golden/v1.3-COVERAGE-MATRIX.md`                | Refreshed golden with corrected pulse values | ✓ VERIFIED | W27C512 shows "100 us" |
| `firestarter_app/firestarter/database.py`                              | 0x35/0x39 removed (WR-01 fix)              | ✓ VERIFIED | Documented as comments; no live entries; commit f2a05e7    |
| `firestarter_app/firestarter/ic_layout.py`                             | 0x35/0x39 removed (WR-01 fix)              | ✓ VERIFIED | Documented as comments; no live entries; commit f2a05e7    |

### Key Link Verification

| From                                          | To                                   | Via                                 | Status     | Details                                          |
| --------------------------------------------- | ------------------------------------ | ----------------------------------- | ---------- | ------------------------------------------------ |
| `build_db.py interpret_timing()`              | `chip_entry programming.pulse_duration` | function call with proto_id at L590 | ✓ WIRED    | L590: `interpret_timing(ic.get("pulse_delay"), proto_id)` |
| `build_db.py VCC_VOLTAGES`                    | `chip_entry electrical.vcc / vdd`    | dict lookup on shifted nibbles      | ✓ WIRED    | L581-586: VCC_VOLTAGES.get((voltages>>8)&0x0F) and (>>12)&0x0F |
| `check_dispatch.py GATE-03 guard`             | `sys.exit(1) gate`                   | `vpp_eeprom_in_eprom` list + L159   | ✓ WIRED    | vpp_eeprom_in_eprom included in exit gate condition at L159 |
| `tools/build_db.py regeneration`             | `firestarter/data/chip_database.json` | python tools/build_db.py            | ✓ WIRED    | DB regenerated (commit 12286df); 734 chips; W27C512=100 us |

### Data-Flow Trace (Level 4)

| Artifact               | Data Variable        | Source                           | Produces Real Data | Status      |
| ---------------------- | -------------------- | -------------------------------- | ------------------ | ----------- |
| `chip_database.json`   | pulse_duration       | `interpret_timing()` in build_db | Yes — raw hex from XML, no multiplier | ✓ FLOWING |
| `chip_database.json`   | electrical.vcc/vdd   | `VCC_VOLTAGES.get()` in build_db | Yes — 0x02/0x03 now decode to 4V/4.5V | ✓ FLOWING |
| `check_dispatch.py`    | vpp_eeprom_in_eprom  | etype + handler check per chip   | Yes — fires on synthetic hazard input | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior                                         | Command                                                | Result                          | Status  |
| ------------------------------------------------ | ------------------------------------------------------ | ------------------------------- | ------- |
| W27C512 pulse_duration in DB                     | `python -c "...json.load(chip_database.json)..."`      | "100 us"                        | ✓ PASS  |
| `firestarter info W27C512` CLI surface           | `firestarter info W27C512`                             | "Pulse delay: 100µS", exit 0    | ✓ PASS  |
| `check_dispatch.py` on regenerated DB            | `python tools/check_dispatch.py`                       | "PASS: all 734 chips...", exit 0 | ✓ PASS  |
| GATE-03 guard fires on synthetic hazard          | `FIRESTARTER_DB_FILE=hazard.json python check_dispatch.py` | "FAIL: 1 Flash/EEPROM...", exit 1 | ✓ PASS |
| Full test suite                                  | `python -m pytest tests/ --cov-fail-under=70`          | 480 passed, coverage ≥70%       | ✓ PASS  |
| Ruff check + format on touched files             | `ruff check ... && ruff format --check ...`            | All checks passed               | ✓ PASS  |
| AT28C256 vcc in regenerated DB                   | `python -c "...chip_database.json...AT28C256..."`      | vcc='4V', vdd='5V'              | ✓ PASS  |
| VCC_VOLTAGES nibbles 0x02/0x03                   | `python -c "...VCC_VOLTAGES..."`                       | [0x02]='4V', [0x03]='4.5V'     | ✓ PASS  |
| interpret_timing no x100 multiplier              | `python -c "...interpret_timing('64',0x07)..."`        | '100 us'                        | ✓ PASS  |

### Requirements Coverage

| Requirement | Source Plan | Description                                                          | Status      | Evidence                                             |
| ----------- | ----------- | -------------------------------------------------------------------- | ----------- | ---------------------------------------------------- |
| DEC-02      | 57-01, 57-03 | build_db.py field decode re-derived to match minipro source semantics | ✓ SATISFIED | Four targeted decode fixes committed; baseline diff confined to pulse_duration + vcc/vdd; no algorithm/pinout/type changes |
| DEC-03      | 57-01, 57-03 | pulse_delay decoded as microseconds (×100 multiplier removed)        | ✓ SATISFIED | interpret_timing('64',0x07)='100 us'; W27C512 DB='100 us'; firestarter info='100µS'; debug fix 8088141 |
| DEC-04      | 57-01, 57-03 | VCC/VDD decode complete and correctly labelled                       | ✓ SATISFIED | VCC_VOLTAGES[0x02]='4V',[0x03]='4.5V'; vcc=bits-11-8, vdd=bits-15-12; AT28C256 vcc='4V' |
| DEC-05      | 57-01, 57-02 | PROTOCOL_MAP canonical IC2_ALG_* names; phantom/non-memory IDs removed | ✓ SATISFIED | 11 canonical memory entries; 7 excluded IDs as comments; KNOWN_PROTOCOLS and _etype set drop 0x35/0x39; sync to database.py and ic_layout.py (WR-01) |
| GATE-03     | 57-02, 57-03 | check_dispatch.py full-class VPP-safety guard across full chip set   | ✓ SATISFIED | Guard fires on synthetic hazard (exit 1); exits 0 on 734-chip DB; corrected predicate (electrical.type not algorithm set) is actually reachable |

All 5 requirements declared for Phase 57 (DEC-02, DEC-03, DEC-04, DEC-05, GATE-03) are satisfied.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| None | — | No TBD/FIXME/XXX markers; no bare excepts; no stubs | — | Clean |

No anti-patterns detected in any of the modified files (`build_db.py`, `check_dispatch.py`, `tests/test_decoder.py`, `database.py`, `ic_layout.py`).

### Human Verification Required

None. All observable truths are verifiable programmatically:
- CLI output confirmed by running `firestarter info W27C512` (exit 0, shows "Pulse delay: 100µS")
- DB field values confirmed by direct JSON parse
- Guard behavior confirmed by synthetic hazard injection test
- Test suite confirmed to pass (480 tests, ≥70% coverage)

### Deferred Items

The code review (57-REVIEW.md) identified two items explicitly deferred with operator approval:
- **WR-02** (protocol-table parity test across build_db/database/check_dispatch) — deferred as debt, no current-DB impact. Not a Phase 57 goal.
- **WR-04** (_first_pin empty-list hardening in ic_layout.py) — latent, not active. Not a Phase 57 goal.

Neither affects Phase 57 goal achievement. No roadmap items from Phases 58/59 are relevant deferral targets for Phase 57 gaps.

### Gaps Summary

None. All 5 roadmap success criteria are verified against the actual codebase.

**ROADMAP.md update recommendation:** Success Criterion #5 literal text (`algorithm in {0x05, 0x06, 0x0D}`) should be updated to reflect the corrected implementation (`electrical.type == "Flash/EEPROM" AND handler == "configure_eprom"`). The corrected predicate is the one that actually works and is verified here. The old wording was a defect in the specification, fixed by commit ffa74b6.

---

## Commit Evidence (firestarter_app submodule, branch v1.11-infoic-decode-correctness)

| Commit   | Description                                                              |
| -------- | ------------------------------------------------------------------------ |
| de18f06  | test(57-01): add failing tests for VCC_VOLTAGES nibbles, vcc/vdd bits, interpret_timing |
| dc6e8e9  | feat(57-01): fix VCC_VOLTAGES nibbles 0x02/0x03 and vcc/vdd label swap (DEC-04) |
| 8de307f  | feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts (DEC-03) |
| 0ccd5ea  | feat(57-01): canonicalize PROTOCOL_MAP, KNOWN_PROTOCOLS, _etype set (DEC-05) |
| 89cae4e  | feat(57-02): remove 0x35/0x39 from check_dispatch.py (DEC-05 sync)      |
| 2c29be6  | feat(57-02): add GATE-03 full-class vpp-pin VPP-safety guard (GATE-03)  |
| 12286df  | feat(57-03): regenerate chip_database.json from corrected build_db.py   |
| 914919e  | feat(57-03): refresh golden matrix + GATE-03 verified on regenerated DB |
| 8088141  | fix(info): resolve vpp-pin TypeError in ic_layout and pulse_duration mapping (DEC-03 CLI surface) |
| ffa74b6  | fix(57): correct GATE-03 VPP-safety guard to key on electrical.type (CR-01) |
| f2a05e7  | fix(57): propagate 0x35/0x39 removal to database + ic_layout (WR-01, DEC-05) |

---

_Verified: 2026-06-08T15:00:00Z_
_Verifier: Claude (gsd-verifier)_
