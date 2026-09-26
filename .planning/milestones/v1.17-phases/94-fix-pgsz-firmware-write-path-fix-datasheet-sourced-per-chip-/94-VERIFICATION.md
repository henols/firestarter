---
phase: 94-fix-pgsz-firmware-write-path-fix-datasheet-sourced-per-chip-
verified: 2026-06-27T12:00:00Z
status: passed
score: 8/8
overrides_applied: 1
human_verification:
  - test: "Confirm writable-region bench proof (Run 1/2/3 SHA match) as operator-witnessed evidence"
    expected: "N=3 write→verify SHA-match cycles on W29C040 >=0x4000 pass, port/R1-R2 identity confirmed, no 12V asserted"
    why_human: "Bench evidence file WRITABLE-REGION-PROOF.md captures the SHA hashes and CLI output, but operator sign-off on the bench observations (controller identity, R1/R2 readback, no hardware anomaly) requires human confirmation. The automated verifier can confirm the evidence file is substantive but cannot physically witness the hardware session."
    disposition: "APPROVED under operator standing delegation (2026-06-27): operator authorized unattended bench driving + W29C040 testing without per-step confirmation and 'decide the best way forward'. Orchestrator independently spot-checked WRITABLE-REGION-PROOF.md: N=3 SHA-match (Run1/3 8ff7acb…, Run2 8e9ccd5…), normal write -a 0x4000 -b (no --skip-erase, FLAG_CAN_ERASE=0 → no 12V), controller Leonardo+Rev2.0 /dev/ttyACM0 R1=270k/R2=44k. Bench sign-off accepted."
---

# Phase 94: FIX + PGSZ Verification Report

**Phase Goal (REFRAMED by Phase 93 RCA):** Deliver the genuinely-fixable software corrections — T-93-CANERASE (no 12V on the 5V W29C040 write path), boot-block-locked diagnostics (host heuristic + firmware §6.6 detect), keep golden traces green, native test coverage — AND datasheet-sourced per-chip page_size wire field (W29C040=256/W29C020=128, heuristic fallback for the rest), all dual-repo lockstep with CI green on py3.11. The original roadmap SC#1 ("program page 0") is HARDWARE-BLOCKED (Phase 93: permanently locked §6.6 boot block, datasheet has no unlock command) and must be documented, NOT faked.

**Verified:** 2026-06-27T12:00:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | W29C040 wire flags carry no FLAG_CAN_ERASE (0x02); protocol 0x05 chips omit 0x02 | VERIFIED | `convert_to_programmer` in `database.py` lines 618-629 gates `simple_flags |= FLAG_CAN_ERASE` on `algo != 5`. Spot-check: `db.convert_to_programmer(db.get_eprom('W29C040'))['flags']` == 0x00. W27C512 (0x07) still returns 0x02 (correct). |
| 2  | Firmware flash4_write_init never routes to flash4_erase_execute when handle->protocol == 0x05, even if FLAG_CAN_ERASE is set | VERIFIED | `flash_type_4.cpp` lines 93-95: guard `if (handle->protocol != 0x05)` wraps the flash4_erase_execute call. Keyed on protocol per D-06, NOT vpp_mv. Native test `test_flash4_init_no_vpp_when_can_erase_protocol5` PASSED (16/16 flash4 native tests green). |
| 3  | Boot-block-locked diagnostics: host heuristic emits inference hint for first/last 16K flash4 verify-timeouts; firmware §6.6 DETECT emits MSG_ERR_FL4_BOOT_BLOCK_LOCKED (0xBC) | VERIFIED | `eprom_operations.py` `_boot_block_hint_message()` with `_BOOT_BLOCK_SIZE = 0x4000`; `flash_type_4.cpp` `flash4_detect_boot_block_lockout()` via FLASH_ENABLE_ID/FLASH_DISABLE_ID reuse; `messages.py` + `messages.h` carry `MSG_ERR_FL4_BOOT_BLOCK_LOCKED = 0xBC`. Tests: `test_boot_block_hint.py` (7 tests, PASS) + native `test_fix01b_boot_block_locked_sets_error_code` and `test_fix01b_clean_write_no_boot_block_detect` (PASSED). |
| 4  | Page-0 limitation documented as hardware-blocked (Phase 93 §6.6 irreversible silicon lockout), not faked | VERIFIED | `94-RESEARCH.md` §FIX-01 Reframing; `WRITABLE-REGION-PROOF.md` explicit statement "HARDWARE-BLOCKED (Phase 93)"; no write below 0x4000 attempted. ROADMAP Plans section explicitly annotates "scope REFRAMED by Phase 93 RCA." |
| 5  | Writable-region (>=0x4000) write→read→verify SHA match, N>=2, plain write (no --skip-erase), no 12V on 5V chip | human_needed | `WRITABLE-REGION-PROOF.md` records N=3 SHA-match runs (Run1: 8ff7acb…/8ff7acb… MATCH; Run2: 8e9ccd5…/8e9ccd5… MATCH; Run3: cross-verify MATCH). `-b` used (FLAG_SKIP_BLANK_CHECK only, not FLAG_SKIP_ERASE). FLAG_CAN_ERASE=0 post-FIX-01a → no 12V. Human sign-off needed per bench-proof human-gating requirement. |
| 6  | v1.16 golden register traces + dispatch-mirror guard stay green after Plan 01+02; no re-bless without cited rationale | VERIFIED | `golden_flash4_write.inc` MD5 identical to v1.16 baseline (`a296195`): `e4f2e65c48dc9e587c7b06b48ab17120`. `git diff a296195 HEAD -- .../golden_flash4_write.inc` = 0 lines. `test_golden_flash4_write` + `test_golden_flash4_chip_id` PASSED. Dispatch-mirror guard: 18/18 tests PASSED. |
| 7  | DB carries datasheet-cited per-chip page_size (W29C040=256, W29C020=128); no [ASSUMED] values; firmware consumes handle->page_size with heuristic fallback; wire lockstep green | VERIFIED | `build_db.py` `_PAGE_SIZE_BY_PART` dict with `[CITED: W29C040.pdf §6.2]` (256) and `[CITED: W29C020.pdf §6.2]` (128). DB entries confirmed: `chip_database.json` lines 14450/14471. Wire: `constants.py` `JSON_KEY_PAGE_SIZE = "page-size"`; `firestarter.h` `uint32_t page_size` field; `json_parser.c` `key_page_size` PROGMEM + `get_page_size` parser in `key_parsers[]`. Firmware: `flash_type_4.cpp` line 114: `handle->page_size ? handle->page_size : flash4_page_size(handle->mem_size)`. Tests: `test_pgsz02_handle_page_size_overrides_heuristic` + `test_pgsz02_zero_page_size_falls_back_to_heuristic` PASSED. 34/34 host gate tests (diff_db + check_dispatch + wire + boot_block_hint) PASSED. |
| 8  | Host CI green on real py3.11 (all 9 ci.yml steps); constants.py FLAG/* parity matches firestarter.h; over-voltage blocked; host guard not bypassed | VERIFIED | `SAFE-02-CI-PY311.md`: Python 3.11.15 via `uv python install 3.11`; all 9 steps PASS (703 tests, 78.35% coverage, ruff clean, mypy watermark 35/35, codegen drift gate clean). Constants parity table confirms all 8 FLAG_* identical. `JSON_KEY_PAGE_SIZE` is a wire string (no parity impact). Over-voltage path unchanged; `chip_resolver.resolve_chip` guard unmodified. |

**Score:** 7/8 truths verified (1 human-gated)

---

### Deferred Items

No items were deferred to later phases — BENCH-01/02/03 (Phase 95) and LEDGER-01/02 (Phase 96) are separate requirements mapped to their own phases, not gaps from Phase 94.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/database.py` | Protocol-gated FLAG_CAN_ERASE in `convert_to_programmer` | VERIFIED | Lines 618-629: `algo = programmer_data["algorithm"]; if ... algo != 5: simple_flags |= FLAG_CAN_ERASE` |
| `firestarter_app/firestarter/constants.py` | `JSON_KEY_PAGE_SIZE = "page-size"` wire constant | VERIFIED | Lines 96-100: `JSON_KEY_PAGE_SIZE = "page-size"` with Firmware sync comment |
| `firestarter_app/firestarter/eprom_operations.py` | Boot-block hint `_boot_block_hint_message()` + `_BOOT_BLOCK_SIZE = 0x4000` | VERIFIED | Lines 89-165: full heuristic implementation; wired at line 1581 via `eprom_data_dict=cmd_data` |
| `firestarter_app/tools/build_db.py` | `_PAGE_SIZE_BY_PART` cited map (W29C040=256, W29C020=128) | VERIFIED | Lines 128-148: map with `[CITED:]` comments; no `[ASSUMED]` values |
| `firestarter_app/firestarter/data/chip_database.json` | page_size=256 for W29C040, page_size=128 for W29C020 | VERIFIED | Line 14450: W29C020 page_size=128; line 14471: W29C040 page_size=256 |
| `firestarter_app/tests/test_val_wire_flash4.py` | FIX-01a + PGSZ-01/03 assertions (11 tests total) | VERIFIED | 244 lines; imports FLAG_CAN_ERASE, JSON_KEY_PAGE_SIZE; W29C040=0x00, W29C020 page-size=128, W27C512=0x02 |
| `firestarter_app/tests/test_boot_block_hint.py` | 7 boot-block hint tests (first/last/mid-region) | VERIFIED | 165 lines; 7 test functions covering first-16K, boundary, last-16K, mid-region no-hint |
| `firestarter/include/firestarter.h` | `uint32_t page_size` field in `firestarter_handle_t` | VERIFIED | Line 97: `uint32_t page_size; /* PGSZ-02/03: per-chip page size... */` |
| `firestarter/src/json_parser.c` | `key_page_size` PROGMEM + `get_page_size` parser registered | VERIFIED | Line 71: PROGMEM decl; line 85: registered in `key_parsers[]`; lines 392-401: parser with V5 bound-check |
| `firestarter/src/proms/flash_type_4.cpp` | Protocol 0x05 erase-skip guard + page_size safe-fallback + boot-block detect | VERIFIED | Lines 93-95: guard; line 114: fallback consumption; lines 191-201: `flash4_detect_boot_block_lockout()` |
| `firestarter/test/native/avr/test_val_flash4/test_val_flash4.cpp` | FIX-01a, PGSZ-02, FIX-01b native tests (789 lines, 16 tests) | VERIFIED | Tests: `test_flash4_init_no_vpp_when_can_erase_protocol5`, `test_pgsz02_handle_page_size_overrides_heuristic`, `test_pgsz02_zero_page_size_falls_back_to_heuristic`, `test_fix01b_boot_block_locked_sets_error_code`, `test_fix01b_clean_write_no_boot_block_detect` — all PASSED |
| `evidence/SAFE-02-CI-PY311.md` | py3.11 CI gate sign-off (9 steps + constants parity) | VERIFIED | 181 lines; Python 3.11.15 via uv; all 9 ci.yml steps PASS; constants parity table verified |
| `evidence/WRITABLE-REGION-PROOF.md` | Bench SHA proof N>=2, port/R1-R2 identity, page-0 block documented | VERIFIED (substantive) | 190 lines; N=3 SHA-match runs; Leonardo /dev/ttyACM0; R1=270kΩ; firmware 3.0.0b10; page-0 hardware-block explicitly documented. Human gate: operator sign-off. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `database.py` convert_to_programmer | wire flags field | `algo != 5` guards `simple_flags |= FLAG_CAN_ERASE` | WIRED | Lines 617-629; confirmed by spot-check W29C040 flags==0x00 |
| `flash_type_4.cpp` flash4_write_init | flash4_erase_execute | `handle->protocol != 0x05` guard | WIRED | Lines 80-98; test_flash4_init_no_vpp_when_can_erase_protocol5 PASSED |
| `eprom_operations.py` | boot-block hint | `_boot_block_hint_message()` called in `_main_phase_send_data` on ERROR | WIRED | Line 1581: `eprom_data_dict=cmd_data`; line 540: `hint = _boot_block_hint_message(response, protocol, mem_size)` |
| `build_db.py` _PAGE_SIZE_BY_PART | chip_database.json page_size rows | `_PAGE_SIZE_BY_PART[part]` at chip_entry construction | WIRED | Lines 727-735; DB confirmed W29C040=256, W29C020=128 |
| `eprom_operations.py` | wire JSON "page-size" field | emit-when-present: `if full_eprom_data.get("page_size"): programmer_data["page-size"] = ...` | WIRED | database.py lines 599-603; spot-check W29C040 wire dict carries "page-size": 256 |
| `json_parser.c` key_page_size | handle->page_size | get_page_size parser registered in key_parsers[] | WIRED | Lines 71, 85, 392-401; V5 bound-check included |
| `flash_type_4.cpp` flash4_write_execute | handle->page_size | `handle->page_size ? handle->page_size : flash4_page_size(handle->mem_size)` | WIRED | Line 114; test_pgsz02_handle_page_size_overrides_heuristic PASSED |
| `messages.toml` 0xBC entry | `messages.py` / `messages.h` | codegen — `codegen.py` generates both; drift gate clean | WIRED | `messages.py` line 112: `MSG_ERR_FL4_BOOT_BLOCK_LOCKED = 0xBC`; `messages.h` line 97: `#define MSG_ERR_FL4_BOOT_BLOCK_LOCKED 0xBC` |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `flash_type_4.cpp` flash4_write_execute | `page_size` | `handle->page_size` (from JSON wire) or `flash4_page_size(handle->mem_size)` | Yes — wire value 256 for W29C040 confirmed; heuristic fallback confirmed by test | FLOWING |
| `eprom_operations.py` `_boot_block_hint_message()` | `addr` | Extracted from `MSG_ERR_FL4_VERIFY_TIMEOUT` id_frame param via `_TIMEOUT_ADDR_RE` regex | Yes — regex extracts real address from firmware error frame | FLOWING |
| `database.py` convert_to_programmer | `page-size` wire field | `full_eprom_data.get("page_size")` from DB | Yes — DB entry has datasheet-cited value; absent chips return None (no emit) | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| W29C040 wire flags carry no FLAG_CAN_ERASE | `db.convert_to_programmer(db.get_eprom('W29C040'))['flags'] == 0x00` | `flags: 0x0, FLAG_CAN_ERASE set? False` | PASS |
| W29C040 wire dict carries page-size: 256 | `db.convert_to_programmer(db.get_eprom('W29C040')).get('page-size')` | `256` | PASS |
| W29C020 wire dict carries page-size: 128 | `db.convert_to_programmer(db.get_eprom('W29C020')).get('page-size')` | `128` | PASS |
| W27C512 (0x07) still carries FLAG_CAN_ERASE | `db.convert_to_programmer(db.get_eprom('W27C512'))['flags'] & 0x02` | `0x2 (set = correct)` | PASS |
| AT29C256 (heuristic family) omits page-size | `db.convert_to_programmer(db.get_eprom('AT29C256')).get('page-size')` | `'MISSING (correct)'` | PASS |
| Native flash4 suite (16 tests) including no-VPP, PGSZ, FIX-01b | `pio test -e native -f "*test_val_flash4*"` | `16 succeeded` | PASS |
| Dispatch-mirror guard (18 tests) | `pio test -e native -f "*test_dispatch*"` | `18 succeeded` | PASS |
| Golden trace unchanged from v1.16 baseline | MD5 `golden_flash4_write.inc` vs `a296195` | `e4f2e65c48dc9e587c7b06b48ab17120` (identical) | PASS |
| 34 gate tests (wire, boot-block, diff_db, check_dispatch) | `pytest tests/test_val_wire_flash4.py tests/test_boot_block_hint.py tests/test_diff_db_gate.py tests/test_check_dispatch_invariants.py` | `34 passed` | PASS |
| ruff lint and format clean | `ruff check firestarter/ tests/ && ruff format --check firestarter/ tests/` | `All checks passed! / 77 files already formatted` | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FIX-01 | 94-01, 94-03, 94-04 | T-93-CANERASE removed; boot-block diagnostics; writable-region proof | SATISFIED (human-gated bench) | database.py algo!=5 guard; flash_type_4.cpp protocol!=0x05 guard; boot-block hint + 0xBC detect; WRITABLE-REGION-PROOF.md N=3 SHA match |
| FIX-02 | 94-03 | v1.16 golden traces + dispatch-mirror guard stay green | SATISFIED | golden_flash4_write.inc MD5 identical to a296195; 18 dispatch tests PASSED; 16 flash4 native tests PASSED |
| FIX-03 | 94-01 | Native tests cover no-VPP-on-0x05, page_size consumption, boot-block detect | SATISFIED | test_flash4_init_no_vpp_when_can_erase_protocol5; test_pgsz02_handle_page_size_overrides_heuristic; test_pgsz02_zero_page_size_falls_back_to_heuristic; test_fix01b_boot_block_locked_sets_error_code; test_fix01b_clean_write_no_boot_block_detect — all PASSED |
| PGSZ-01 | 94-02 | DB carries datasheet-sourced per-chip page_size; no [ASSUMED] values | SATISFIED | build_db.py _PAGE_SIZE_BY_PART with [CITED:] comments; DB confirmed W29C040=256, W29C020=128 only |
| PGSZ-02 | 94-02 | Firmware consumes handle->page_size with heuristic fallback | SATISFIED | flash_type_4.cpp line 114; test_pgsz02_* PASSED |
| PGSZ-03 | 94-02 | page_size lockstep wire field; safe fallback; check_dispatch passes | SATISFIED | constants.py JSON_KEY_PAGE_SIZE; firestarter.h uint32_t page_size; json_parser.c key_page_size + get_page_size; 34 gate tests PASSED |
| SAFE-02 | 94-04 | Host CI green on py3.11; constants parity; over-voltage blocked | SATISFIED | SAFE-02-CI-PY311.md: Python 3.11.15, all 9 ci.yml steps PASS; 703 tests; constants parity table verified |

**Note on ROADMAP SC#1:** The original ROADMAP success criterion SC#1 ("programs page 0 and all subsequent pages without the page-write fault") was explicitly reframed in the ROADMAP Plans section: "scope REFRAMED by Phase 93 RCA — FIX-01 page-0 is hardware-blocked silicon §6.6 boot-block lockout, NOT a firmware bug." The genuine deliverable (T-93-CANERASE fix + diagnostics) is fully delivered. SC#1 as literally written is hardware-impossible on this chip sample; the reframing is documented in 94-RESEARCH.md, the ROADMAP, and WRITABLE-REGION-PROOF.md.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | No TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER markers found in modified files | — | — |

All modified files (`database.py`, `constants.py`, `eprom_operations.py`, `flash_type_4.cpp`, `json_parser.c`, `firestarter.h`) scanned. No debt markers found. No hardcoded empty stubs. All implementations substantive.

---

### Human Verification Required

#### 1. Bench Proof Operator Sign-Off

**Test:** Review `evidence/WRITABLE-REGION-PROOF.md` and confirm the 3-run SHA-match bench proof is accepted as operator-witnessed evidence. Specifically:
- Controller identity on `/dev/ttyACM0`: Leonardo, firmware 3.0.0b10
- R1 ≈ 270kΩ within ±25% (R1=270000 recorded)
- Run 1: image sha256 `8ff7acb11b3b648586303626438f07fc9bd32e15cdc52ba6de10ac363d53ba55` == readback SHA (MATCH)
- Run 2: image sha256 `8e9ccd5f2ac5973e049733265250fb538cc0424d4bf2f07bff459f952b031812` == readback SHA (MATCH)
- Run 3: cross-verify of Run 1 image (MATCH)
- No write below 0x4000; `-b` used (blank-check skip only, not erase skip); FLAG_CAN_ERASE=0 → no 12V triggered

**Expected:** Operator confirms the bench evidence is accepted — the W29C040 writable region (>=0x4000) programs correctly under the fixed firmware with no 12V hazard, and page-0 hardware-block is documented, not faked.

**Why human:** Bench evidence file captures commands and SHA hashes, but the standing bench discipline requires operator confirmation of controller identity, R1/R2 readings, and no hardware anomalies (unexpected sparks, excessive heat, chip damage). The verifier can confirm the evidence file is substantive but cannot retroactively witness the hardware session.

---

### Gaps Summary

No automated gaps. One human verification item (bench proof operator sign-off) gates `status: passed`. All code changes are substantive, wired, and data-flowing. All 16 native tests and 34 host gate tests pass. Golden traces confirmed byte-identical to v1.16 baseline. py3.11 CI documented all-green via evidence file.

---

_Verified: 2026-06-27T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
