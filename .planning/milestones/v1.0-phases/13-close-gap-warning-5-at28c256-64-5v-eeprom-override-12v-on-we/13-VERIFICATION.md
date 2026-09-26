---
phase: 13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we
verified: 2026-05-11T20:05:00Z
status: passed
score: 8/8 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: none
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 13: WARNING-5 — AT28C256/64 5V EEPROM Override Verification Report

**Phase Goal:** Make 23 hazardous DIP28_2764 5V EEPROMs (ATMEL AT28C/BV, MICROCHIP 28Cxx, NEC UPD28C, ST M28256, XICOR X28C, EXEL XLE2865A — currently mistagged `algorithm=0x07` + `electrical.type='Flash/EEPROM'` in upstream minipro) route to `configure_eeprom28c` (5V, no VPP regulator) instead of `configure_eprom` (which would assert 12V `P1_VPP_ENABLE` on socket pin 1 = A14 address line = hardware damage). Fix is data-layer only.

**Verified:** 2026-05-11T20:05:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 23 chips in `minipro_complete_db.json` previously algorithm=0x07 with pinout=DIP28_2764 and electrical.type=Flash/EEPROM are now algorithm=0x0D | VERIFIED | `python3` scan of DB: count of `DIP28_2764 + Flash/EEPROM @ 0x0D = 23`; count `@ 0x07 = 0`; histogram shows `0x07: 214, 0x0D: 41` (consistent with -23/+23 delta from Phase 12 baseline 237/18) |
| 2 | AT28C256 is 0x0D | VERIFIED | `db['ATMEL']` AT28C256 entry shows `programming.algorithm = 0x0D`, `electrical.type = "Flash/EEPROM"`, `pinout = "DIP28_2764"` |
| 3 | W27C512 (regression sanity) is still 0x07 | VERIFIED | `db['WINBOND']` W27C512 entry shows `programming.algorithm = 0x07`, `pinout = "DIP28_27512"` (different pinout — discriminator correctly excluded it) |
| 4 | `build_db.py` contains the inline 3-predicate override conditional | VERIFIED | Lines 221-247 of `firestarter_app/tools/build_db.py`: comment block (lines 221-238) + 3-predicate `if` (lines 239-241) + `INFO:` stderr print (lines 242-246) + `proto_id = 0x0D` (line 247). Predicates: `pinout_key == "DIP28_2764"`, `proto_id == 0x07`, `_etype == "Flash/EEPROM"`. No `_PROTOCOL_OVERRIDES` module constant introduced (per plan) |
| 5 | `check_dispatch.py` contains `_28C_EEPROM_HAZARD_PINOUT` guard and exits 0 | VERIFIED | `firestarter_app/tools/check_dispatch.py:62` defines constant; lines 89, 110-121 add violation list, loop check, FAIL block; lines 152-156 extend PASS line. Run output: `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom`, exit=0 |
| 6 | `firestarter_app/CLAUDE.md` contains WARNING-5 documentation paragraph | VERIFIED | `firestarter_app/CLAUDE.md` Database Pipeline section contains "Protocol overrides (WARNING-5):" paragraph (~20 lines) covering: 3-predicate condition, 0x07→0x0D flip, A14-on-pin-1 rationale, ~23 chips across 6 manufacturers, 7-chip regression-safe set (W27C512 etc.), audit pointer, `check_dispatch.py` guard pointer |
| 7 | No firmware changes were needed (firmware-side 0x0D handler exists from Phase 12) | VERIFIED | `firestarter/src/proms/memory.cpp:77-78` has `if (handle->protocol == 0x0D) configure_eeprom28c(handle);`; `firestarter/src/proms/eeprom_28c.cpp` exists (90 lines) with `configure_eeprom28c`, `eeprom28c_write_init` (with SDP disable sequence + DQ7-polling `eeprom28c_wait_for_write`); no firmware files modified in Phase 13 (verified by submodule git log) |
| 8 | All 6 manufacturer families covered by override | VERIFIED | Per-family spot-check confirmed: ATMEL/AT28BV64, MICROCHIP memory/28C17A, NEC/UPD28C256, ST/M28256, XICOR/X28C64, EXEL/XLE2865A all show `algorithm=0x0D` post-regen |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/check_dispatch.py` | Regression scan with `_28C_EEPROM_HAZARD_PINOUT` guard | VERIFIED | 161 lines; constant at line 62; violation list `eeprom28c_in_eprom` at line 89; per-chip check at lines 110-121; FAIL block at lines 141-149; three-clause PASS at lines 152-156 |
| `firestarter_app/tools/build_db.py` | Inline 3-predicate WARNING-5 override block between `_etype` derivation and `chip_entry` construction | VERIFIED | Block at lines 221-247 includes 18-line comment header naming WARNING-5, A14 hazard, references to `.planning/v1.0-MILESTONE-AUDIT.md`; 3-predicate `if`; stderr `INFO:` print; `proto_id = 0x0D` assignment; no module-top constant introduced |
| `firestarter_app/firestarter/data/minipro_complete_db.json` | Regenerated DB with 23 chips moved from algorithm=0x07 to algorithm=0x0D | VERIFIED | Algorithm histogram: 0x07=214, 0x0D=41 (was 237, 18 per Phase 12 baseline); 23 chips with `DIP28_2764 + Flash/EEPROM` at `algorithm=0x0D`; 0 chips at `algorithm=0x07` with this signature |
| `firestarter_app/CLAUDE.md` | Database Pipeline section with WARNING-5 paragraph | VERIFIED | "Protocol overrides (WARNING-5):" paragraph present in Database Pipeline section between "Known protocols" line and `### Constants` heading; references all required elements (DIP28_2764, 0x07→0x0D, EPROM_STD/EEPROM_POLL, configure_eprom/configure_eeprom28c, A14 hazard, 6-manufacturer scope, regression-safe set, audit pointer, `check_dispatch.py` guard) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `build_db.py` inline override | `configure_eeprom28c` (firmware 0x0D handler) | `proto_id = 0x0D` → `chip_entry['programming']['algorithm']` → wire JSON → `memory.cpp::configure_memory` dispatch | WIRED | Override mutates `proto_id` (line 247); `chip_entry["programming"]["algorithm"] = proto_id` (line 261); firmware `memory.cpp:77-78` dispatches `protocol == 0x0D` → `configure_eeprom28c` |
| Regenerated DB | `check_dispatch.py` `_28C_EEPROM_HAZARD_PINOUT` guard | `json.load` → per-chip iteration → handler check | WIRED | `check_dispatch.py` exits 0 with three-clause PASS line; 0 violations in the regenerated DB |
| `check_dispatch.py` constant | `pinouts.json` `DIP28_2764` key | string equality `pinout == _28C_EEPROM_HAZARD_PINOUT` | WIRED | Constant `_28C_EEPROM_HAZARD_PINOUT = "DIP28_2764"` matches the pinout key in `pinouts.json`; 23 chips have this exact pinout in regenerated DB |
| `CLAUDE.md` documentation | `build_db.py` override + `check_dispatch.py` guard | narrative reference | WIRED | Documentation paragraph explicitly references both source files by name (`build_db.py`, `tools/check_dispatch.py`) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `check_dispatch.py` exits 0 with three-clause PASS | `python3 firestarter_app/tools/check_dispatch.py; echo exit=$?` | `PASS: all 743 chips have a valid dispatch path; 0 SRAM chips route to configure_eprom; 0 DIP28_2764 Flash/EEPROM chips route to configure_eprom` / `exit=0` | PASS |
| `build_db.py` regenerates and emits 23 INFO override lines | `python3 firestarter_app/tools/build_db.py 2>/tmp/build_db.stderr; grep -c 'INFO:.*algorithm override 0x07->0x0D' /tmp/build_db.stderr` | `23` | PASS |
| DB integrity: 0 DIP28_2764 Flash/EEPROM chips at algorithm=0x07 | Python scan of regenerated `minipro_complete_db.json` | `DIP28_2764 Flash/EEPROM @ 0x07: 0`; `@ 0x0D: 23` | PASS |
| Firmware native dispatch tests | `cd firestarter && pio test -e native -f "*test_dispatch*"` | `15 test cases: 15 succeeded`; includes `test_protocol_0x0D_dispatches_eeprom28c [PASSED]` | PASS |
| Defense-in-depth: `eeprom_28c.cpp` has zero VPP-regulator engagement | `grep -c 'REGULATOR\|VPE_TO_VPP\|VPE_ENABLE\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|eprom_check_vpp' firestarter/src/proms/eeprom_28c.cpp` | `0` | PASS |
| AT28C256 routed to 0x0D | Python lookup in DB | `AT28C256: algorithm=0x0D, type=Flash/EEPROM, pinout=DIP28_2764` | PASS |
| W27C512 regression: still on 0x07 | Python lookup in DB | `W27C512: algorithm=0x07, type=Flash/EEPROM, pinout=DIP28_27512` (different pinout) | PASS |
| Additional UV-EPROM regression chips on 0x07 | Python scan: W27C512, W27C257, W27E257, SST27SF512, SST27SF256, SST27VF512, SST27VF256 | All 7 chips at `algorithm=0x07`; all on DIP28_27512 or DIP28_27256 pinouts | PASS |

### Probe Execution

No conventional `scripts/*/tests/probe-*.sh` exist in this repo. The phase declares no formal probe paths in PLAN frontmatter; the equivalent gates are the `check_dispatch.py` regression scan and `pio test -e native` Unity suite, both executed under Behavioral Spot-Checks above.

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| (none declared) | n/a | n/a | n/a |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-FW-03 | 13-01, 13-02, 13-03 | `EEPROM_POLL` (0x0D) uses DQ7 data-polling loop; SDP disable applied for AT28C256 | SATISFIED | `firestarter/src/proms/eeprom_28c.cpp:23` defines `EEPROM_SDP_DISABLE` 6-write sequence; `eeprom28c_write_init` (line 49) calls `flash_execute_command(EEPROM_SDP_DISABLE)` before writes; `eeprom28c_wait_for_write` (line 83) implements DQ7 polling (read-back compare). After Phase 13's override, AT28C256 now reaches this codepath (was previously routed to `configure_eprom` due to upstream 0x07 mistag). REQ-FW-03 is now end-to-end reachable for AT28C256. |
| REQ-SAF-01 | 13-01, 13-02, 13-03 | VPP voltage checked via ADC feedback before first write pulse for every chip | SATISFIED | After Phase 13, 23 chips no longer route to a handler that asserts 12V on A14. The 0x0D handler is purely 5V VCC with zero VPP regulator engagement (`grep` confirmed 0 matches for VPP refs in `eeprom_28c.cpp`). The hardware-damage path WARNING-5 introduced by Phase 12's removal of the BLOCKER-1 safety stop is closed. (Note: the original REQ-SAF-01 about pre-pulse ADC check applies to chips that DO use VPP — those still go through `eprom_check_vpp` in the configure_eprom path; the Phase 13 fix removes 23 chips that should never have been on that path in the first place.) |

No orphaned requirements found. REQUIREMENTS.md does not map any additional requirement IDs to Phase 13 that aren't claimed by the plans.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none in phase-modified files) | — | — | — | — |

Pre-existing bare `except:` clauses at `firestarter_app/tools/build_db.py:140, 185` were flagged by the code reviewer (IN-03 in REVIEW.md) — not introduced by Phase 13 and out of scope per SCOPE BOUNDARY rule.

The submodule has unrelated dirty state (carried forward from prior work: `__init__.py`, `ic_layout.py`, deleted `.planning/codebase/*.md`) — not introduced by Phase 13 and explicitly preserved untouched per all three plan SUMMARYs.

### Human Verification Required

None. All goal-relevant truths are programmatically verifiable: file content, JSON DB contents, exit code of regression scan, firmware unit test results, grep-based defense-in-depth check, and per-chip algorithm/pinout verification.

The phase explicitly defers hardware verification on a real RURP shield to a future hardware-test phase per CONTEXT.md "Out of scope" (no hardware available in this environment); this is documented and not a gap for Phase 13.

### Code Review Findings (from 13-REVIEW.md)

The phase's prior code review surfaced 2 WARNING-level and 4 INFO-level findings:

- **WR-01:** Override and regression guard share identical predicates (`_etype == "Flash/EEPROM"`) — not defense-in-depth. A future upstream `minipro` change flipping `flags & 0x10` off on an AT28C variant would slip past both. This is a defense-in-depth concern, NOT a current goal-blocker — the phase goal "make 23 hazardous chips route to `configure_eeprom28c`" is achieved as-built and verified. The review's suggested fix (name-based positive assertion) is documented improvement work, not a gap in the stated goal.
- **WR-02:** `vpp_mv` left at 12000 on overridden chips. Currently safe because `configure_eeprom28c` does not read `vpp_mv`; flagged as latent risk if a future 0x0D codepath consults VPP. Not a current goal-blocker.
- **IN-01..IN-04:** Style/documentation polish; no functional impact.

These review findings are improvement opportunities for future work and do not invalidate Phase 13's goal achievement. The stated goal (data-layer fix routing 23 chips to safe handler, verified by `check_dispatch.py` PASS + 23-chip diff) is met.

### Gaps Summary

No gaps. All 8 must-haves verified against the actual codebase. The regression guard fires PASS, the override emits exactly 23 INFO lines, the regenerated DB has 0 hazardous chips on the 0x07 path, AT28C256 is at 0x0D, W27C512 and 6 other UV-EPROMs remain at 0x07 (regression intact), the firmware 0x0D handler exists with SDP disable and DQ7 polling, and `firestarter_app/CLAUDE.md` documents the override with all required elements including audit cross-reference and regression guard pointer.

---

*Verified: 2026-05-11T20:05:00Z*
*Verifier: Claude (gsd-verifier)*
