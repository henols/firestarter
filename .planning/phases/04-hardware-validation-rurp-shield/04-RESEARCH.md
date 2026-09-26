# Phase 4: Hardware Validation (RURP shield) — Research

**Researched:** 2026-05-12
**Domain:** Bench-validation of five canon EPROM/Flash/EEPROM chip families on a physical RURP shield + repair of two integration-test shell scripts.
**Confidence:** HIGH for code paths and DB entries (grep-verified live); MEDIUM-with-caveat for HW-05 abort mechanism (locked decision D-05 specifies `firestarter config` to set VPP setpoint, but CLI does not expose a VPP setpoint arg — see Section §5 + Open Questions).

## Summary

CONTEXT.md locks 11 D-NN decisions. Research's job is to verify the live code paths each HW-NN exercises, surface DB-entry shapes for the five canon chips, and flag the one D-05 detail where the locked decision and the live CLI surface diverge.

The 5 canon chips are all present in `firestarter_app/firestarter/data/chip_database.json` and route to the correct firmware handler via the algo-first dispatch in `memory.cpp`. The two test-script broken refs are exactly as documented (no additional drift detected). The SAF-04 closure is asymmetric in a way that materially affects HW-05's bench rhythm: VPP-HIGH ( > setpoint + 500 mV) aborts with ERROR; VPP-LOW (< 95% of setpoint) emits WARNING only and proceeds. To get the "deliberately-underpowered VPP run that must abort cleanly" demanded by ROADMAP success criterion 5, the operator must lower `handle->vpp_mv` in the DB so the actual ~12V VPP exceeds setpoint + 500 mV (e.g., set `vpp_mv = 8000` and let nominal 12V → ERROR). The locked-decision phrasing "lower the regulator setpoint to ~10 V" in CONTEXT.md D-05 is achievable only via DB override (or build_db.py re-emit), not via `firestarter config` — the latter only takes `--rev / -r1 / -r2` calibration args, no VPP setpoint.

**Primary recommendation:** Plan 04-01 ships HW-01 (sed-class fix, 2 confirmed broken refs only, no other drift). Plan 04-02 executes HW-02 + HW-03 + HW-04 on the well-trodden write→verify→read→xxd-diff loop with multimeter at P1_VPP for HW-04. Plan 04-03 executes HW-05's two-run pair using a `~/.firestarter/database.json` user override to lower `vpp_mv` for AM28F010 (NOT `firestarter config`); the abort signature to grep for is `ERROR: VPP is high: X.XV > Y.YV` (NOT "VPP is low" — that emits WARN only).

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 — HW-01 ships as its own Wave 1 plan (software-only, no bench dep).** 2 dead `database_generated.json` refs at `firestarter_app/firestarter_test.sh:31` and `firestarter_app/write_test.sh:17`. Plan 04-01 ships HW-01 in isolation; bench is single-resource.
- **D-02 — Three plans total.** 04-01 = HW-01; 04-02 = HW-02 + HW-03 + HW-04; 04-03 = HW-05.
- **D-03 — One consolidated `04-HW-VALIDATION.md` with 5 H2 sections.** §1 = HW-01 repair record; §2 = W27C512; §3 = AM29F040 + SST39SF040; §4 = AT28C256 + multimeter; §5 = AM28F010 normal + SAF-04 abort.
- **D-04 — HW-04 multimeter sufficient; scope optional.** DMM at socket pin 1 (DIP28 P1 = VPP rail) reading 0 V continuously through the write window satisfies the gate.
- **D-05 — HW-05 underpowered VPP via `firestarter config` regulator setpoint (~10 V).** See §5 + Open Questions: the live CLI does not expose a VPP setpoint via `firestarter config`. Research adjusts the mechanism to a DB-override of `electrical.vpp_mv` for AM28F010, achieving the same load-bearing two-run contrast that D-05 demands.
- **D-06 — Per-chip evidence schema.** Chip header (part, lot, package, algo, DB entry), date/time/host/board/fw/app, fenced terminal log, xxd binary diff, voltage readings (HW-04/05), optional photo, verdict.
- **D-07 — Failure policy = triage.** Firmware bug → file new FW-NN + replan; chip issue → substitute or document deferral; operator error → retry, do not log.
- **D-08 — Atomic commit per HW-NN bench run.** HW-01 = one `firestarter_app/` sub-repo commit (both .sh files) + immediate-follow meta-repo commit. Each HW-NN bench run = one meta-repo commit appending its H2 section.
- **D-09 — Sub-repo coordination not needed.** HW-01 is app-only.
- **D-10 — Bench-resume points per-H2-section.** Plan 04-02 may execute across multiple sessions.
- **D-11 — Re-validation triggered only on changes to `flash_intel.cpp`, `eeprom_28c.cpp`, `mem_util_*` in `memory.cpp`, or wire fields in `json_parser.c` / `firestarter.h`.**

### Claude's Discretion
- Exact wording of the abort-error string the host CLI emits on the underpowered HW-05 run — research resolves below.
- Whether to re-execute `pio test` as part of HW-01 dry-run — recommended as a citation, not a re-run (matches Phase 3 Pitfall #3).
- Whether to include a "before HW-01 fix" failing-state log in `§1` — recommended yes (cheap, provides before/after symmetry).
- Photo file-naming convention under `photos/` — recommended `HW-NN-<chip>-<isodate>.jpg` (mirrors §-section naming).

### Deferred Ideas (OUT OF SCOPE)
- Scope-trace addendum to HW-04 (capture if convenient).
- Photo/video evidence for Phase 5 MILESTONES.md story (capture if convenient).
- CI-friendly bench-runner script (v1.2).
- Sub-repo CLAUDE.md update referencing `04-HW-VALIDATION.md` (Phase 5 / DOC-01 owns).
- AT28C256 chip-ID population (v1.2 / WARNING-5 carry-forward).
- Multi-board cross-check Uno vs Leonardo (planner's discretion).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HW-01 | Test scripts run cleanly against current `chip_database.json`; WARNING-4 closed | §1 — grep audit confirms exactly 2 broken refs (no further drift); `bash -n` + `jq` smoke as dry-run validation |
| HW-02 | Physical write/verify/read of W27C512 (algo=0x07, UV-EPROM); logged | §2 — DB entry, firmware path through `memory.cpp:92` → `configure_eprom`, 64 KB test binary recipe |
| HW-03 | Physical write/verify of AM29F040 (chip-erase) + SST39SF040 (sector-erase), both algo=0x06; logged | §3 — DB entries, `flash3_erase_execute` branch at `flash_type_3.cpp:94-102` (address==0 → chip erase; nonzero → sector erase), 512 KB test binary recipe per chip |
| HW-04 | Physical write/verify of AT28C256 (algo=0x0D via Phase 13 override); multimeter confirms 0 V at P1_VPP throughout write window; logged | §4 — DB entry confirmed `algorithm=13`, firmware handler `configure_eeprom28c` has ZERO VPP regulator references (grep confirmed in 13-VERIFICATION.md), 32 KB binary recipe |
| HW-05 | Physical write/verify of AM28F010 (algo=0x10) PLUS underpowered-VPP run that aborts cleanly (SAF-04 closure verified on hardware); logged | §5 — DB entry confirmed `algorithm=16` (0x10), `vpp_mv=12000`; abort path: `flash_intel_check_vpp` at `flash_intel.cpp:25-50`; **asymmetric abort** — VPP-HIGH branch errors at line 39-43, VPP-LOW branch warns at line 44-47; correct underpowering = lower DB `vpp_mv` so measured 12V > setpoint+500 mV |

## Standard Stack

This is a hardware-validation phase. No new libraries; the "stack" is the existing tool chain:

| Tool | Version | Purpose | Location |
|------|---------|---------|----------|
| `firestarter` CLI | per `pyproject.toml` (v2.0.7_dev per `__init__.py`) | Host-side write / read / verify / id / vpp / vpe / config | `firestarter_app/` (pip install -e .) |
| Arduino firmware | per `pio run -e uno/leonardo` build | Wire protocol + chip handlers | `firestarter/` (PlatformIO) |
| `bash` 4+ | system | `firestarter_test.sh` + `write_test.sh` driver | system |
| `jq` | system | JSON metadata extraction in test scripts | system |
| `xxd` | system | Binary hex dump for diff | system |
| `colordiff` (optional) | system | Side-by-side hex diff (firestarter_test.sh uses it; write_test.sh uses plain `diff`) | system |
| `dd` + `/dev/urandom` | system | Test binary generation | system |
| Multimeter | user-supplied | P1_VPP voltage reading for HW-04 + HW-05 | bench |

No new package installs. No version bumps.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Test-script repair (HW-01) | Host (bash + jq) | — | Pure path-string fix in `firestarter_app/*.sh`; no firmware or Python code touched. |
| EPROM write / verify / read invocation (HW-02..HW-05) | Host CLI (`firestarter_app/firestarter/main.py` → `eprom_operations.py` → `serial_comm.py`) | Firmware (`memory.cpp` → handler) | Host marshalls JSON wire command; firmware dispatches and drives hardware. |
| VPP regulator engage/disengage (HW-04 invariant + HW-05 setpoint) | Firmware (`*.cpp` handlers) | Hardware (RURP shield, multimeter at P1) | Host has no direct control register write; firmware emits register writes per handler. Operator probes pin 1 (P1_VPP) with DMM. |
| SAF-04 VPP ADC compare (HW-05 abort path) | Firmware (`flash_intel.cpp:25-50` `flash_intel_check_vpp`) | Host (parses `ERROR: VPP is high: ...` line) | Compare executes on Arduino against `handle->vpp_mv` from wire JSON; host receives ERROR: prefix and propagates exit-1. |
| Bench evidence capture | Operator | Host (`firestarter` stdout/stderr; terminal log) | Manual transcription into `04-HW-VALIDATION.md` H2 sections; no automation. |

## Test-Script Drift Audit (HW-01)

`grep -rn "database_generated\|minipro_complete" firestarter_app/firestarter_test.sh firestarter_app/write_test.sh firestarter_app/firestarter/ firestarter_app/tools/ firestarter_app/CLAUDE.md` returns exactly 2 matches (verified 2026-05-12 against the live tree):

- `firestarter_app/firestarter_test.sh:31` — `JSON_FILE='./firestarter/data/database_generated.json'`
- `firestarter_app/write_test.sh:17` — `JSON_FILE='./firestarter/data/database_generated.json'`

No other references to `database_generated.json` or `minipro_complete_db.json` exist in the test scripts, the Python sources, the tools dir, or the app's CLAUDE.md. The Phase 11 / CLEAN-01 rename to `chip_database.json` is fully propagated everywhere EXCEPT these two lines. The fix is a one-character class swap on each: `database_generated` → `chip_database`.

**Live target file:** `firestarter_app/firestarter/data/chip_database.json` (62 KiB+, 58 manufacturer keys, present in tree).

**No additional shell-level drift:**
- Both scripts rely on a `jq` query against the JSON to extract `.["memory-size"]`, `.["has-chip-id"]`, and `.["can-erase"]` for the named chip. The new `chip_database.json` schema does NOT use these key names — the new top-level shape is `{ manufacturer: [ { part_number, electrical, programming, pinout } ] }` with `electrical.size_bytes`, `programming.chip_id_check`, etc. **The scripts will fail at `jq` lookup time even after the filename fix.** This is a SECOND DRIFT that the planner needs to surface.

**Critical for HW-01 planning:** the planner should validate whether the scripts' `jq` queries still resolve after the filename fix. If not, HW-01 expands to also flip the jq path expressions (`."memory-size"` → `.electrical.size_bytes`, `."has-chip-id"` → `.programming.chip_id_check`, `."can-erase"` → derive from `.electrical.type == "Flash/EEPROM"` per database.py info_flags logic at `:408`). The CONTEXT.md D-01 framing ("`sed`-class fix on two `.sh` files") may underestimate the actual scope.

**Dry-run validation primitives (no bench access needed):**
- `bash -n firestarter_test.sh` → exit 0 (syntax check; passes pre-fix)
- `bash -n write_test.sh` → exit 0
- `jq '.' "$JSON_FILE" | head` against the new path → well-formed JSON exit 0
- `jq -e --arg target_name "W27C512" -r '.[] | .[] | select(.name == $target_name) | .["memory-size"]' "$JSON_FILE"` → **expect to FAIL** against new schema (returns null/empty); this is the second-drift signal
- `pio test -e native` → cite existing green state from `01-VERIFICATION.md` Behavioral Spot-Check; do not re-run (Phase 3 Pitfall #3)

## DB Entry Verification (chip_database.json)

`python3 firestarter_app/.../chip_database.json` lookup verified at write time (2026-05-12). All 5 canon chips present:

| Chip | Manufacturer key | part_number | algorithm | electrical.type | size_bytes | pin_count | vpp_mv | pinout | chip_id_check | chip_id_value |
|------|------------------|-------------|-----------|-----------------|-----------|-----------|--------|--------|---------------|---------------|
| W27C512 | WINBOND | `"W27C512"` | 7 (0x07) | Flash/EEPROM | 65536 | 28 | 12000 | DIP28_27512 | true | `0x0000da08` |
| AM29F040 | SPANSION(1) | `"AM29F040"` | 6 (0x06) | Flash/EEPROM | 524288 | 32 | 12000 | DIP32_STD | true | `0x000001a4` |
| SST39SF040 | SST | `"SST39SF040"` | 6 (0x06) | Flash/EEPROM | 524288 | 32 | 12000 | DIP32_STD | true | `0x0000bfb7` |
| AT28C256 | ATMEL | `"AT28C256,AT28C256"` | 13 (0x0D) ← Phase 13 override | Flash/EEPROM | 32768 | 28 | 12000 | DIP28_2764 | false | `0x00000000` |
| AM28F010 | AMD | `"AM28F010"` | 16 (0x10) | Flash/EEPROM | 131072 | 32 | 12000 | DIP32_STD | true | `0x000001a7` |

**Notes:**
- `part_number` is the comma-joined alias list from upstream XML; `AT28C256` shows as `"AT28C256,AT28C256"` — the host CLI's `EpromDatabase.get_eprom("AT28C256")` lookup tolerates this via comma-split (see `database.py:_map_data` and the search/info paths). CLI invocations use the bare name `AT28C256`.
- AT28C256 retains `electrical.type = "Flash/EEPROM"` AND `electrical.vpp = "12V"` / `vpp_mv = 12000` IN THE DB JSON — the Phase 13 override flipped ONLY `programming.algorithm` from 0x07 to 0x0D. The 5V invariant is enforced by the firmware handler (`configure_eeprom28c` never asserts the regulator), NOT by the DB voltage field.
- `chip_id_check = false` + `chip_id_value = 0` for AT28C256 means `eeprom28c_write_init` at `eeprom_28c.cpp:78` skips the SAF-05 A9-12V chip-ID branch entirely (gated on `handle->chip_id > 0`). The SDP-disable + DQ7-poll write path runs unconditionally.
- All four flash/EEPROM chips have `info_flags |= 0x10` (Can be electrically erased) set in `database.py:408`, which translates to wire-protocol `FLAG_CAN_ERASE` (0x02). The firmware write-init paths therefore auto-erase before write unless `--no-blank-check` is passed.

## Per-Chip Code-Path Snapshot

### HW-01 — Test-Script Repair (Software-Only)

**Files in scope (HW-01 modifies):**
- `firestarter_app/firestarter_test.sh:31` (verified live 2026-05-12)
- `firestarter_app/write_test.sh:17` (verified live)

**Fix shape (sed-class):**
```bash
sed -i "s|database_generated\.json|chip_database.json|" firestarter_app/firestarter_test.sh firestarter_app/write_test.sh
```

**Possible second-drift fix (if jq paths broken under new schema):**
- `.["memory-size"]` → `.electrical.size_bytes`
- `.["has-chip-id"]` → `.programming.chip_id_check`
- `.["can-erase"]` → `(.electrical.type == "Flash/EEPROM")`
- The outer pipe `.[] | .[]` still works (top-level keys are still manufacturers; values are still arrays of chip objects).
- Name lookup currently uses `.name`; new schema uses `.part_number` → also needs `.["name"]` → `.part_number` change.

The planner should add a Wave-1 task to verify the post-fix script run (without bench) gets past the `jq` lookup. If `jq -e` returns non-empty for `W27C512`, the second-drift fix is unnecessary. If it returns null, the second-drift fix is required and HW-01's scope grows.

### HW-02 — W27C512 (UV-EPROM, algo=0x07)

**DB:** `WINBOND/W27C512`, `algorithm=7`, `size_bytes=65536`, `pin_count=28`, `vpp_mv=12000`, `pinout=DIP28_27512`, `chip_id_value=0x0000da08`.

**Firmware path:**
1. `firestarter.cpp:95` `op_execute_function(configure_memory, handle)` runs INIT.
2. `memory.cpp:92` — `handle->protocol == 0x07` branch → `configure_eprom(handle)`.
3. `eprom.cpp:79` — `eprom_check_vpp(handle)` (the UV-EPROM equivalent of SAF-04, pre-existing in v1.0).
4. `eprom.cpp:84` — `eprom_internal_check_chip_id(handle, RESPONSE_CODE_ERROR)` runs unconditionally since `chip_id != 0` (0xda08 is set).
5. Blank check (FLAG_CAN_ERASE is set → erase + blank → MAIN phase write loop with 12V VPP via `REGULATOR | VPE_TO_VPP` at `eprom.cpp:149` for STD pulse).
6. Default pulse-delay derived per protocol (W27C512 has `pulse_duration='10000 us'` in DB but this string is parsed only if `handle->pulse_delay > 0`; default is 0 → handler chooses default for 0x07).

**Test binary:** `dd if=/dev/urandom of=test_W27C512.bin bs=1 count=65536 status=none` (64 KiB) — pattern from `firestarter_test.sh:79-86`.

**CLI rhythm:**
```bash
firestarter write W27C512 test_W27C512.bin     # FLAG_CAN_ERASE set automatically
firestarter verify W27C512 test_W27C512.bin    # in-firmware byte-compare; exit 0 on match
firestarter read W27C512 read_W27C512.bin
diff <(xxd test_W27C512.bin) <(xxd read_W27C512.bin)
```

Expected: all three commands exit 0; xxd diff prints nothing (0 byte differences).

### HW-03 — AM29F040 + SST39SF040 (AMD-flash, algo=0x06)

**AM29F040 DB:** `SPANSION(1)/AM29F040`, algorithm=6, size_bytes=524288 (512 KiB), pin_count=32, pinout=DIP32_STD, chip_id_value=0x000001a4.
**SST39SF040 DB:** `SST/SST39SF040`, algorithm=6, size_bytes=524288 (512 KiB), pin_count=32, pinout=DIP32_STD, chip_id_value=0x0000bfb7.

**Firmware path (both, since both are 0x06):**
1. `memory.cpp:82` — `handle->protocol == 0x06` branch → `configure_flash3(handle)`.
2. `flash_type_3.cpp:30` `configure_flash3` assigns `flash3_write_init` and `flash3_write_execute` for CMD_WRITE.
3. `flash_type_3.cpp:59-80` `flash3_write_init`:
   - Chip-ID check via `flash3_check_chip_id_execute` (line 60-65).
   - If FLAG_CAN_ERASE && !FLAG_SKIP_ERASE → `flash3_erase_execute` (line 68-71). **This is the chip-erase vs sector-erase decision point.**
4. `flash_type_3.cpp:94-102` `flash3_erase_execute`:
   - If `handle->address != 0` → `flash3_sector_erase(handle, handle->address)` (line 97).
   - Else (`handle->address == 0`) → `flash_execute_command(FLASH_ERASE)` = full chip erase (line 100).

**Sector-erase command syntax:**
- Default `firestarter write` sends `"address": 0` → chip-erase path (line 100).
- To trigger sector-erase, the CLI must pass `-a <nonzero-address>` to `firestarter write` AND the upstream write must NOT span the full chip (otherwise chip-erase is still preferable). For a "verify sector-erase works" bench run on SST39SF040 the planner should structure the run as:
  - `firestarter write SST39SF040 sector_data.bin -a 0x10000` writes a single 64 KiB sector starting at offset 0x10000.
  - The handler's `flash3_erase_execute` at line 94 sees `handle->address == 0x10000` (nonzero) → calls `flash3_sector_erase(handle, 0x10000)` (line 97) which issues the 6-byte AMD unlock sequence `{0x5555,AA / 0x2AAA,55 / 0x5555,80 / 0x5555,AA / 0x2AAA,55 / 0x10000,30}` at `flash_type_3.cpp:104-114`.

**Test-binary recipe per chip:** 512 KiB random binary via `dd if=/dev/urandom of=test_<chip>.bin bs=1024 count=512`.

**CLI rhythm — AM29F040 chip-erase (default):**
```bash
firestarter write AM29F040 test_AM29F040.bin       # CAN_ERASE set; address=0; chip-erase
firestarter verify AM29F040 test_AM29F040.bin
firestarter read AM29F040 read_AM29F040.bin
diff <(xxd test_AM29F040.bin) <(xxd read_AM29F040.bin)
```

**CLI rhythm — SST39SF040 sector-erase variant:**
```bash
# Write to offset 0x10000 to force sector-erase path. Use a smaller binary (e.g., 64 KiB)
dd if=/dev/urandom of=sector_data.bin bs=1 count=65536 status=none
firestarter write SST39SF040 sector_data.bin -a 0x10000
firestarter read SST39SF040 readback.bin -a 0x10000 -s 0x10000
diff <(xxd sector_data.bin) <(xxd readback.bin)
```

The planner should decide whether to run BOTH variants on SST39SF040 (full chip-erase write AND a sector-erase write) or only the sector-erase variant. ROADMAP success criterion 3 says "AM29F040 (chip-erase + write) and an SST39SF040 (sector-erase + write)" — the disjunction reads as one variant per chip, not both on the same chip. Recommendation: AM29F040 → chip-erase full write; SST39SF040 → sector-erase write only. Document both bench runs in §3 with sub-headings.

### HW-04 — AT28C256 (5V EEPROM, algo=0x0D via Phase 13 override)

**DB (post-Phase-13 override):** `ATMEL/AT28C256,AT28C256`, `algorithm=13` (0x0D), `electrical.type=Flash/EEPROM`, `electrical.vpp="12V"`, `vpp_mv=12000`, `pin_count=28`, `pinout=DIP28_2764`, `chip_id_check=false`, `chip_id_value=0`.

**Critical:** The DB's `vpp_mv=12000` is **ignored at the firmware level** — `configure_eeprom28c` (`eeprom_28c.cpp:34-47`) sets only `firestarter_operation_init` / `_main` / `_end` and `pulse_delay=0`; it NEVER calls `firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, ...)`. Phase 13 verification confirmed `grep -c 'REGULATOR\|VPE_TO_VPP\|VPE_ENABLE\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|eprom_check_vpp' firestarter/src/proms/eeprom_28c.cpp = 0`.

Wait — that grep was reported in `13-VERIFICATION.md`. Let me re-verify against the **current** tree, because SAF-05 (Phase 1 v1.1) added `eeprom28c_check_chip_id` which DOES toggle the regulator briefly for A9-12V identification (`eeprom_28c.cpp:61-68`). The current `eeprom_28c.cpp`:
- `eeprom28c_check_chip_id` at lines 55-77 — **DOES assert `REGULATOR` and `A9_VPP_ENABLE`** at lines 65-67 (for A9-12V chip-ID read), then clears both at line 72. **But this branch only runs when `handle->chip_id > 0`** (gated at line 82). AT28C256's DB entry has `chip_id_value=0`, so the gate is FALSE and the chip-ID branch is skipped entirely. The write path begins at `flash_execute_command(EEPROM_SDP_DISABLE)` (line 91) which uses no regulator engagement.

**Net effect for HW-04:** As long as the operator does NOT pass `--force` AND the DB entry's `chip_id_value=0` is intact, the entire write path is 5V VCC only. `P1_VPP_ENABLE` is never asserted. DMM at socket pin 1 reads ~0 V continuously throughout.

If the chip-ID branch were somehow enabled (e.g., user override sets a chip_id_value), `eeprom_28c.cpp:61-68` would briefly assert `REGULATOR | A9_VPP_ENABLE` to drive A9 to 12V. **A9 is socket pin 25 on DIP28_2764, NOT pin 1.** P1_VPP is socket pin 1. So even the chip-ID branch does not engage P1_VPP. The HW-04 invariant "0 V at P1_VPP during write window" holds regardless of chip-ID state, by handler construction.

**Firmware path:**
1. `memory.cpp:77` — `handle->protocol == 0x0D` branch → `configure_eeprom28c(handle)`.
2. `eeprom_28c.cpp:34-47` `configure_eeprom28c` — sets init/main/end function pointers; pulse_delay=0.
3. `eeprom_28c.cpp:75-94` `eeprom28c_write_init`:
   - Line 82: `if (handle->chip_id > 0)` — skipped for AT28C256 (chip_id_value=0).
   - Line 91: `flash_execute_command(EEPROM_SDP_DISABLE)` — 6-write sequence to unlock SDP if enabled. No regulator engagement.
   - Line 93: `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` — wait for SDP-disable internal write.
   - Line 96: blank check unless FLAG_SKIP_BLANK_CHECK.
4. `eeprom_28c.cpp:101-115` `eeprom28c_write_execute` — page-write loop, 64-byte page boundary, DQ7 poll via `eeprom28c_wait_for_write` (line 117).

**Multimeter probe point:** Socket DIP28 pin 1 (P1_VPP rail) referenced to socket GND (DIP28 pin 14). Reading should be < 0.5 V throughout the entire `firestarter write AT28C256 test.bin` invocation. Capture at write-start, mid-write (during the multi-second SDP-disable + page-write window), and write-end.

**Test binary:** `dd if=/dev/urandom of=test_AT28C256.bin bs=1024 count=32 status=none` (32 KiB).

**CLI rhythm:**
```bash
firestarter write AT28C256 test_AT28C256.bin    # 5V-only path, no VPP regulator
firestarter verify AT28C256 test_AT28C256.bin
firestarter read AT28C256 read_AT28C256.bin
diff <(xxd test_AT28C256.bin) <(xxd read_AT28C256.bin)
```

Expected: 0 V at P1_VPP throughout; xxd diff empty.

### HW-05 — AM28F010 + SAF-04 Abort (Intel-flash, algo=0x10)

**DB:** `AMD/AM28F010`, `algorithm=16` (0x10), `size_bytes=131072` (128 KiB), `pin_count=32`, `pinout=DIP32_STD`, `vpp_mv=12000`, `chip_id_value=0x000001a7`.

**Firmware path:**
1. `memory.cpp:72` — `handle->protocol == 0x10` branch → `configure_flash_intel(handle)`.
2. `flash_intel.cpp:52-72` `configure_flash_intel` — assigns `flash_intel_write_init` for CMD_WRITE, sets cleanup.
3. `flash_intel.cpp:74-99` `flash_intel_write_init`:
   - Line 75: `firestarter_set_control_register(handle, REGULATOR | P1_VPP_ENABLE, 1)` — asserts 12V on socket pin 1.
   - Line 76: `delay(500)` — let regulator settle.
   - Line 77: `flash_intel_check_vpp(handle)` — the SAF-04 closure.
   - Line 78-85: **CR-01 safety**: if `response_code == RESPONSE_CODE_ERROR`, clear `REGULATOR | P1_VPP_ENABLE` and return WITHOUT writing.
   - Line 86-91: chip-ID branch (asserts chip_id_value=0x01a7 expected).
   - Line 93-95: erase if FLAG_CAN_ERASE.
   - Line 96-97: blank check.

**`flash_intel_check_vpp` (the abort decision):**
- `flash_intel.cpp:25-50`. Reads `vpp_mv` from ADC via `rurp_read_voltage_mv()` (line 35).
- **VPP-HIGH branch (line 39-43):** `if (vpp_mv > (uint32_t)handle->vpp_mv + 500)` → `firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV", ...)`. `response_code = RESPONSE_CODE_ERROR` unless FLAG_FORCE (then WARNING). **This is the ABORT branch.**
- **VPP-LOW branch (line 44-47):** `else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100)` → `firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV", ...)`. **ALWAYS RESPONSE_CODE_WARNING; never aborts.** Write proceeds.

**LOAD-BEARING INSIGHT:** The CONTEXT.md D-05 framing ("lower regulator setpoint to ~10 V; expect abort") routes to the WRONG branch. If the regulator setpoint is lowered to 10 V, the actual `rurp_read_voltage_mv()` reads ~10 V; `handle->vpp_mv = 12000` (from the DB); 10000 < 12000 * 0.95 = 11400 → **VPP-LOW branch fires → WARNING only → write CONTINUES.** This does not satisfy ROADMAP success criterion 5 ("aborts a deliberately-underpowered VPP run").

**Correct underpowering recipe for clean abort:**

Option A — DB override to lower `handle->vpp_mv`:
1. Create `~/.firestarter/database.json` with an override for AM28F010:
   ```json
   {
     "AMD": [
       { "name": "AM28F010", "vpp_mv": 8000 }
     ]
   }
   ```
2. The `EpromDatabase._merge_databases` path (`database.py:213-238`) shallow-merges per-`part_number` keyed by `name` — this flips the wire JSON `vpp_mv` to 8000 while leaving algorithm, pinout, etc. intact.
3. `firestarter write AM28F010 test.bin` — firmware reads ~12 V from ADC (regulator unchanged), compares against `handle->vpp_mv = 8000`, finds 12000 > 8000 + 500 → **VPP-HIGH branch → ERROR → abort.** ✓
4. Restore by deleting (or commenting out) the `~/.firestarter/database.json` override and re-run for the nominal pass.

Option B — Inverse semantic (chip naturally produces lower VPP than DB asks): not achievable on RURP shield without hardware modification; rejected by D-05 same as the physical-underpowering option.

Option C — Use FLAG_FORCE to convert the VPP-LOW warning into… no, FLAG_FORCE downgrades errors to warnings, not the other way around. Does not produce an abort.

**Recommendation:** Override the planner's understanding of D-05 from "`firestarter config` setpoint = 10 V" (not supported by CLI) to "DB override `vpp_mv = 8000` for AM28F010" (mechanism-equivalent, achieves the load-bearing two-run contrast). Document the override file in `04-HW-VALIDATION.md §5 Sub-run A` for traceability. The planner should also note this in PLAN 04-03 to avoid the operator falling into the VPP-LOW trap.

**Host-side abort signature** (the planner needs this for grep-the-log evidence):
- Firmware emits via `log_error()` macro (`logging.h:79-83`) → wire prefix `ERROR` from `LOG_ERROR_MSG[] PROGMEM = "ERROR"` (`logging.c:14`). The exact wire line is `ERROR: VPP is high: 12.0V > 8.0V` (or whatever measured + setpoint values). The PREFIX_REGEX in `serial_comm.py:48` strips the prefix; the parsed `Response(type='ERROR', message='VPP is high: 12.0V > 8.0V')` reaches `_main_phase_send_data` or the state machine in `eprom_operations.py:277-278`, which raises `EpromOperationError(f"Programmer error during ...: {response.message}")` → propagated as exit-1 from `firestarter write`.
- The host-visible stdout pattern (under logger output) is:
  ```text
  ...
  RURP: ERROR: VPP is high: 12.0V > 8.0V
  ERROR: Programmer error during INIT: VPP is high: 12.0V > 8.0V
  ```
- (The `rurp_logger.log(level=ERROR, ...)` in `serial_comm.py:194-195` produces the first line; the second comes from the `eprom_operations.py:277` raise → main.py catch.)
- **Grep target** for `§5 Sub-run A`: `grep -E 'ERROR: VPP is high' terminal_log.txt` should return exactly 1 match.

**Test binary:** `dd if=/dev/urandom of=test_AM28F010.bin bs=1024 count=128 status=none` (128 KiB).

**CLI rhythm — Sub-run A (abort):**
```bash
# Place override at ~/.firestarter/database.json
firestarter write AM28F010 test_AM28F010.bin   # expect exit 1; ERROR: VPP is high
# DMM at P1_VPP during the 500ms regulator settle should read 12.0V, then drop after abort
```

**CLI rhythm — Sub-run B (nominal pass):**
```bash
# Remove ~/.firestarter/database.json override
firestarter write AM28F010 test_AM28F010.bin   # expect exit 0
firestarter verify AM28F010 test_AM28F010.bin  # expect exit 0
firestarter read AM28F010 read_AM28F010.bin
diff <(xxd test_AM28F010.bin) <(xxd read_AM28F010.bin)
```

**Multimeter readings during HW-05:**
- Sub-run A: P1_VPP should read ~12 V during the 500ms `delay(500)` window AFTER the regulator is asserted (line 75) and BEFORE the abort clears it (line 83). Then DROP to ~0 V immediately after abort. Capture the peak reading.
- Sub-run B: P1_VPP should read ~12 V throughout the write window (multiple seconds for 128 KiB at 0x40 command-register Intel-flash speed).

## Architecture Patterns

### Architectural Diagram (HW-NN bench rhythm)

```
Operator (bench)
  │  install chip in DIP socket (DIP28 / DIP32 adapter)
  │  attach DMM probes (HW-04 + HW-05 only) at socket pin 1
  ▼
Host PC (firestarter_app/)
  ├── firestarter write <CHIP> test.bin
  │     ├── main.py:create_write_args → EpromOperator.write_eprom
  │     ├── database.py:get_eprom(CHIP) → full data dict
  │     ├── database.py:convert_to_programmer → wire JSON { algorithm, vpp_mv, ... }
  │     └── serial_comm.py:SerialCommunicator.send_json_command
  │             (250000 baud, JSON over USB serial)
  ▼
Arduino (firestarter/)
  ├── json_parser.c parses wire JSON → handle->protocol, handle->vpp_mv, ...
  ├── memory.cpp:configure_memory dispatches on handle->protocol
  │     ├── 0x07 → configure_eprom        (HW-02 W27C512)
  │     ├── 0x06 → configure_flash3       (HW-03 AM29F040 / SST39SF040)
  │     ├── 0x0D → configure_eeprom28c    (HW-04 AT28C256, post-Phase-13 override)
  │     └── 0x10 → configure_flash_intel  (HW-05 AM28F010)
  ├── handler write_init runs SAF-04 / SAF-05 / blank-check / erase
  └── handler write_execute drives RURP shield bus → physical EPROM
  ▼
Wire response:
  OK: / DATA: / MAIN: / END: / ERROR: / WARN: lines back to host
  ▼
firestarter_app post-processing:
  exit code 0/1, structured Response objects, logged terminal output → captured in 04-HW-VALIDATION.md §N
```

### Test Binary Generation Pattern

Established in `firestarter_app/firestarter_test.sh:79-86`:
```bash
HALF=$((MEM_SIZE / 2))
dd if=/dev/urandom of=test_data/low.bin bs=1 count=$HALF status=none
dd if=/dev/urandom of=test_data/high.bin bs=1 count=$HALF status=none
cat test_data/low.bin test_data/high.bin > test_data/full.bin
```

For HW-02..HW-05 ad-hoc bench runs (not the script invocation), the simpler form is:
```bash
dd if=/dev/urandom of=test_<CHIP>.bin bs=<chip_size> count=1 status=none
```

Chip sizes for bs:
- W27C512 → 65536
- AM29F040 → 524288
- SST39SF040 → 524288 (or 65536 for sector-erase 64 KiB variant)
- AT28C256 → 32768
- AM28F010 → 131072

### xxd Diff Convention

Standard form for §-section evidence (matches `firestarter_test.sh:148`):
```bash
diff <(xxd source.bin) <(xxd readback.bin)
```
- Empty stdout + exit 0 → "0 byte differences"; record as `**Verdict:** PASS — xxd diff exit 0, 0 byte differences`.
- Non-empty stdout → record the first 10-20 lines of mismatch in the §-section terminal log block.

For visual side-by-side (firestarter_test.sh:148 uses `colordiff --suppress-common-lines -y`), but plain `diff` is sufficient and avoids the colordiff system-tool dependency.

### Photo Naming Convention (Claude's Discretion → recommendation)

Under `.planning/phases/04-hardware-validation-rurp-shield/photos/`:
- `HW-02-W27C512-2026-05-12.jpg`
- `HW-03-AM29F040-2026-05-12.jpg`
- `HW-03-SST39SF040-2026-05-12.jpg`
- `HW-04-AT28C256-2026-05-12.jpg` (include DMM in frame)
- `HW-05-AM28F010-2026-05-12.jpg` (include DMM in frame)

Photos are optional per D-06. The §-section just links the filename in markdown image syntax.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| VPP under-voltage detection | A new firmware function or post-hoc check | The existing `flash_intel_check_vpp` at `flash_intel.cpp:25-50` | SAF-04 closure already shipped Phase 1; HW-05 just exercises it |
| AT28C256 5V invariant enforcement | A new test-script flag or wire-protocol field | The existing Phase 13 build_db.py algorithm-override (DIP28_2764 + Flash/EEPROM + 0x07 → 0x0D) at `tools/build_db.py:239-247` | Already shipped; HW-04 just verifies it holds on real silicon |
| Sector-erase command sequence on SST39SF040 | A new CLI flag | Pass `firestarter write -a <nonzero-address>` → `flash3_erase_execute:94-102` chooses sector-erase via `handle->address != 0` discriminator | Existing handler already implements the per-address branch |
| Multimeter timing of P1_VPP engagement (HW-04 / HW-05) | A digital scope or logic analyzer | A DMM held to socket pin 1 with hold-max function | D-04: scope optional, multimeter sufficient for binary 0 V vs 12 V question |
| Cross-chip differential evidence in `04-HW-VALIDATION.md` | A combined comparative report | Five separate H2 sections with the same Schema (chip header, term log, xxd diff, voltage, verdict) | D-03 + D-06 already lock this; the v1.0-INTEGRATION-CHECK.md precedent applies |

**Key insight:** v1.1 has already shipped every code change Phase 4 needs (SAF-04 closure, SAF-05 chip-ID, Phase 13 algo-override, CLEAN-01 DB rename). Phase 4 is **verification-only** on real silicon, plus a `sed`-class repair to the test scripts. No firmware or Python code changes are expected. If a bench failure suggests one is needed, D-07 says file a new requirement and replan — do NOT hand-roll in this phase.

## Pitfalls

### Pitfall 1: HW-05 Underpowering via VPP-LOW Branch (WRONG BRANCH)

**What goes wrong:** Operator follows the CONTEXT.md D-05 phrasing "lower regulator setpoint to ~10 V" and expects the write to abort. It does not — `flash_intel_check_vpp` at `flash_intel.cpp:44-47` emits `WARN: VPP is low: ...` and the write proceeds (or at least attempts to; Intel program-mode then likely returns an SR error from `flash_intel_poll_sr` at line 135 because actual program voltage is insufficient, but that's a different abort signature and not the SAF-04 closure).

**Why it happens:** SAF-04 is asymmetric. VPP-HIGH (measured > setpoint + 500 mV) errors; VPP-LOW (measured < setpoint × 0.95) warns. Lowering the regulator while leaving `handle->vpp_mv` at 12000 takes the warn branch.

**How to avoid:** Override DB `vpp_mv` to 8000 (or similar low value) so the measured ~12 V from the unchanged regulator exceeds `8000 + 500 = 8500` mV → VPP-HIGH branch → ERROR → abort. Use `~/.firestarter/database.json` override (file format per `database_overrides.json` shape with `vpp_mv` field).

**Warning signs:** If the bench-run terminal log shows `WARN: VPP is low: ...` instead of `ERROR: VPP is high: ...`, the abort branch did not fire. Re-run with the correct override.

### Pitfall 2: HW-01 `jq` Schema Drift (Hidden Beyond the Filename)

**What goes wrong:** Both test scripts pass `bash -n` and the `jq '.' "$JSON_FILE"` smoke succeeds after the filename fix, but the actual chip lookup queries `.["memory-size"]`, `.["has-chip-id"]`, `.["can-erase"]` return null because the new schema uses `.electrical.size_bytes`, `.programming.chip_id_check`, etc. The script's "EPROM not found" error fires.

**Why it happens:** Phase 11 / CLEAN-01 renamed the file. The internal JSON schema also changed (build_db.py rewrite). The CONTEXT.md D-01 framing ("sed-class fix on two .sh files") only addresses the filename layer.

**How to avoid:** As part of HW-01 dry-run validation, run the `jq -e --arg target_name "W27C512" -r '...' "$JSON_FILE"` query AFTER the filename fix. If it returns non-empty (matching memory-size), no further work. If it returns null/empty, expand HW-01 scope to also flip the jq path expressions (see §HW-01 above for the mapping).

**Warning signs:** Post-fix `bash firestarter_test.sh W27C512` exits with `Error: No match found for name 'W27C512'`.

### Pitfall 3: AT28C256 SDP-State Precondition Unknown

**What goes wrong:** The chip in the user's bench may have SDP (Software Data Protection) enabled by a previous tool or its factory default. `eeprom28c_write_init` at `eeprom_28c.cpp:91` runs `flash_execute_command(EEPROM_SDP_DISABLE)` unconditionally, which is the AT28C SDP-disable 6-write sequence `{0x5555,AA / 0x2AAA,55 / 0x5555,80 / 0x5555,AA / 0x2AAA,55 / 0x5555,20}`. If SDP is enabled, this sequence clears it. If SDP is disabled, the sequence writes 0x20 to address 0x5555 (and the leading 4 bytes are similarly written at random points) — corrupting those addresses with the unlock-sequence bytes. **`eeprom28c_wait_for_write` at line 93 then waits for the firmware-internal write of 0x20 at 0x5555 to complete via DQ7 poll.**

**Why it happens:** The SDP-disable sequence depends on the chip's current state. The handler does not query state before issuing the unlock; it just issues it.

**How to avoid:** Either accept the small-byte corruption (the unlock sequence writes a handful of bytes that the subsequent operator-supplied write overwrites — IF the operator's binary covers those addresses) or precede the bench run with a `firestarter erase AT28C256` (NB: `configure_eeprom28c` has no CMD_ERASE branch at `eeprom_28c.cpp:38-46` — only WRITE and BLANK_CHECK — so erase via the CLI does NOT work for 28C; the operator must rely on the SDP-disable + page-write flow overwriting all 32 KiB).

**Recommendation for HW-04:** the operator's test binary should be a fresh 32 KiB random pattern, written in one shot. The unlock-sequence bytes get overwritten by the page-write loop (`eeprom_28c.cpp:101-115`) immediately after `eeprom28c_wait_for_write` returns. The xxd diff post-readback should still be clean.

**Warning signs:** xxd diff shows mismatches concentrated at addresses 0x5555 and 0x2AAA only → SDP state interaction caused brief corruption that the subsequent page-write didn't fully overwrite. Document and substitute chip (D-07 "chip-specific issue").

### Pitfall 4: Operator-Error Categories (Per D-07)

Per D-07, these are NOT failures and should NOT appear in the final `04-HW-VALIDATION.md`:

- Forgetting to power-cycle the RURP shield between chips (regulator may be in unknown state from prior run).
- Wrong socket adapter (DIP28 chip in DIP32 socket without adapter; AM29F040 32-pin in a 28-pin position).
- Stale test binary (re-using the previous chip's binary file).
- Cable / USB serial port drift between sessions (firestarter not auto-detecting the right port; CLI hangs).
- Forgetting to remove `~/.firestarter/database.json` override before the Sub-run B nominal pass of HW-05.
- `firestarter --version` exits non-zero because the venv wasn't activated.

If any of these surface, correct the operator state and retry; do not commit a `FAIL` verdict to the artifact.

### Pitfall 5: HW-05 FLAG_FORCE Trap

**What goes wrong:** Operator passes `firestarter write AM28F010 test.bin -f` during the Sub-run A abort test. `FLAG_FORCE` at `flash_intel.cpp:40` downgrades the VPP-HIGH error to a WARNING. Write proceeds, no abort, evidence lost.

**Why it happens:** `--force` is a common bench habit when chip-ID mismatches occur. Operator muscle-memory.

**How to avoid:** PLAN 04-03 should explicitly state: "Sub-run A invocation MUST NOT use `-f` / `--force`." Document in the §5 evidence block.

### Pitfall 6: HW-05 AM28F010 Chip-ID Mismatch on FORCE Path

**What goes wrong:** Sub-run B (nominal pass) runs normally; but if `chip_id_value=0x000001a7` doesn't actually match the operator's silicon (e.g., chip is a re-mark or a different stepping), `flash_intel_check_chip_id` at line 152 fires `ERROR: Chip ID 0xXXXX dont match expected ID 0x01a7`. Operator may interpret this as a SAF-04 failure.

**How to avoid:** If chip-ID mismatch fires during Sub-run B, this is a chip-specific issue per D-07. Substitute, or document `--force` use in the §5 evidence block with explicit note that the chip-ID was overridden but VPP write proceeded normally. The SAF-04 closure (VPP check) and the chip-ID check are separate concerns.

### Pitfall 7: ROADMAP Phrasing "read --verify" is Loose

**What goes wrong:** Operator types `firestarter read W27C512 --verify` expecting a verify-on-read invocation. `argparse` errors because `--verify` is not a `read` flag.

**Why it happens:** ROADMAP success criterion 2 reads "via `firestarter write` then `firestarter read --verify`". The actual CLI separates these: `firestarter verify` is its own subcommand (`main.py:119-133`); `firestarter read` (`main.py:70-90`) has only `--force`, `--address`, `--size`.

**How to avoid:** The correct invocation rhythm (from `firestarter_test.sh:145-152`):
1. `firestarter write CHIP test.bin`
2. `firestarter verify CHIP test.bin`
3. `firestarter read CHIP readback.bin`
4. `diff <(xxd test.bin) <(xxd readback.bin)`

Document this in PLAN 04-02 + 04-03 task actions so the operator does not paste the ROADMAP phrasing verbatim into the shell.

### Pitfall 8: Test-Script jq Smoke vs Hardware-Dependent Suite Run

**What goes wrong:** Plan 04-01 task verifies the test scripts via `bash -n` syntax check + `jq` smoke, but skips actually running the scripts because they require bench hardware (`firestarter fw` early-exits without an Arduino on the serial port).

**Why it happens:** Test scripts are end-to-end; the `EPROM_TESTS=1` branch invokes `exec_firestarter` which calls `firestarter` commands that need hardware.

**How to avoid:** HW-01 dry-run validation is restricted to (a) syntax check, (b) `jq` smoke against the JSON file, (c) optionally setting `EPROM_TESTS=0` + `HARDWARE_TESTS=0` + `FIRMWARE_TESTS=0` at the top of each script and running — but the script's `EPROM_NAME` validation runs unconditionally at `:71` so it still exercises the jq path. The validation is sufficient at "exit 0 from the JSON lookup."

## Code Examples

### Locating the SAF-04 Decision Point (verified `file:line` at write time)

```cpp
// firestarter/src/proms/flash_intel.cpp:39-47
if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {
    int response_code = is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
    firestarter_response_format(response_code, "VPP is high: %u.%uV > %u.%uV", ...);
} else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) {
    firestarter_warning_response_format("VPP is low: %u.%uV < %u.%uV", ...);
}
```

### Locating the AT28C256 5V Invariant (firmware-side enforcement)

```cpp
// firestarter/src/proms/eeprom_28c.cpp:34-47
void configure_eeprom28c(firestarter_handle_t* handle) {
    debug("Configuring EEPROM 28C");
    handle->pulse_delay = 0;
    switch (handle->cmd) {
        case CMD_WRITE:
            handle->firestarter_operation_init = eeprom28c_write_init;
            handle->firestarter_operation_main = eeprom28c_write_execute;
            break;
        case CMD_BLANK_CHECK:
            handle->firestarter_operation_main = mem_util_blank_check;
            break;
    }
}
// No register writes; no REGULATOR / P1_VPP_ENABLE / VPE_TO_VPP / VPE_ENABLE references.
// chip-ID branch in eeprom28c_check_chip_id (lines 65-72) asserts REGULATOR | A9_VPP_ENABLE
// briefly, but A9 is socket pin 25 (DIP28_2764), NOT pin 1. P1_VPP remains 0V.
```

### Locating the Sector-Erase Discriminator (AM29F040 vs SST39SF040 split)

```cpp
// firestarter/src/proms/flash_type_3.cpp:94-102
void flash3_erase_execute(firestarter_handle_t* handle) {
    if (handle->address != 0) {
        debug("Sector erase");
        flash3_sector_erase(handle, handle->address);
    } else {
        debug("Chip erase");
        flash_execute_command(FLASH_ERASE);
    }
}
```

### The Two Broken Refs in the Test Scripts (HW-01)

```bash
# firestarter_app/firestarter_test.sh:31
JSON_FILE='./firestarter/data/database_generated.json'
# firestarter_app/write_test.sh:17
JSON_FILE='./firestarter/data/database_generated.json'
```

Fix: both → `JSON_FILE='./firestarter/data/chip_database.json'`.

## State of the Art

| Old Approach (pre-v1.1) | Current Approach (post-v1.1) | When Changed | Impact on Phase 4 |
|--------------------------|-------------------------------|--------------|-------------------|
| Intel-flash wrote without pre-check | `flash_intel_check_vpp` ADC compare before write | v1.1 Plan 01-01 (SAF-04 closure) | HW-05 is the on-silicon verification of this closure |
| 23 AT28C-family chips routed to `configure_eprom` (12V on A14 hazard) | `build_db.py:239-247` inline override flips proto_id 0x07 → 0x0D for DIP28_2764 + Flash/EEPROM | v1.0 Phase 13 (WARNING-5 closure) | HW-04 is the on-silicon verification of this closure |
| Wire JSON `"vpp"` carried millivolts (semantic overload) | `"vpp_mv"` explicit key | v1.1 Plan 02-01 (WIRE-01) | Phase 4 test scripts must use the post-rename CLI; both .sh fixes are coincident WARNING-4 scope only |
| `minipro_complete_db.json` filename | `chip_database.json` (neutral name) | v1.0 Phase 11 (CLEAN-01) | HW-01 closes the two surviving stale references |

**Deprecated / outdated:**
- The `firestarter_app/firestarter/data/database_generated.json` filename — file does not exist; only the references survive.

## Runtime State Inventory

This is a verification phase, not a rename/refactor. The Phase 13 algorithm override and the SAF-04 closure are already shipped and were verified during their respective closure phases. No runtime state migration is required for Phase 4 itself. The only artifact this phase produces is the `04-HW-VALIDATION.md` evidence file.

| Category | Items found | Action required |
|----------|-------------|------------------|
| Stored data | None — no DB writes, no serial-port persistent state | None |
| Live service config | None — bench operation is one-shot per chip | None |
| OS-registered state | None | None |
| Secrets/env vars | None | None |
| Build artifacts | Existing `firestarter` pip install (v2.0.7_dev per `__init__.py`) and PlatformIO firmware build — must be up to date with v1.1 closures | Verify by `firestarter --version` and `firestarter fw` (cited from `01-VERIFICATION.md`, not re-run) |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `firestarter` CLI (pip install -e .) | HW-02..HW-05 | ✓ (verified by Plan 02-03 SC#5) | 2.0.7_dev | — |
| Arduino firmware (Uno or Leonardo) | HW-02..HW-05 | Required on bench | per `pio run -e uno/leonardo` build | — |
| `bash` | HW-01 dry-run | ✓ | system | — |
| `jq` | HW-01 dry-run | ✓ | system | If absent: `python3 -m json.tool` smoke |
| `xxd` | HW-02..HW-05 binary diff | ✓ | system | If absent: `od -An -tx1` |
| `diff` / `colordiff` | HW-02..HW-05 binary diff | ✓ | system | `diff` is sufficient; colordiff optional |
| `dd` + `/dev/urandom` | HW-02..HW-05 test binary | ✓ | system | — |
| Multimeter | HW-04, HW-05 | User confirmed (CONTEXT.md D-04) | — | — |
| Scope | HW-04 optional | Not confirmed | — | DMM sufficient per D-04 |
| 5 canon chips | HW-02..HW-05 | User confirmed (CONTEXT.md, 5/5 on hand) | — | — |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** Scope optional; xxd → od fallback if needed.

## Validation Architecture

> `.planning/config.json` does not explicitly set `workflow.nyquist_validation = false`. Treating as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Native (Unity on PlatformIO `[env:native]`) — cited only, not re-run for Phase 4 |
| Config file | `firestarter/platformio.ini` `[env:native]` |
| Quick run command | `cd firestarter && pio test -e native -f "*test_dispatch*"` |
| Full suite command | `cd firestarter && pio test -e native` |
| Phase gate | Hardware bench validation captured in `04-HW-VALIDATION.md`; native unit tests not re-executed (cite from 01-VERIFICATION.md) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| HW-01 | Test scripts run cleanly against `chip_database.json` | manual + syntax | `bash -n firestarter_app/firestarter_test.sh && bash -n firestarter_app/write_test.sh && jq -e '.' firestarter_app/firestarter/data/chip_database.json > /dev/null` | ✅ |
| HW-02 | W27C512 write/verify/read on bench | manual (hardware) | `firestarter write W27C512 test.bin && firestarter verify W27C512 test.bin && firestarter read W27C512 r.bin && diff <(xxd test.bin) <(xxd r.bin)` | ❌ (manual-only — bench hardware) |
| HW-03 | AM29F040 chip-erase + SST39SF040 sector-erase on bench | manual (hardware) | (per-chip commands; see §HW-03) | ❌ (manual-only) |
| HW-04 | AT28C256 write/verify/read + 0 V at P1_VPP confirmed by DMM | manual (hardware + DMM) | (per §HW-04 commands) | ❌ (manual-only — DMM probe required) |
| HW-05 | AM28F010 underpowered-VPP abort + nominal-VPP pass | manual (hardware + DB override) | (per §HW-05 sub-runs A and B) | ❌ (manual-only) |

### Sampling Rate

- **Per HW-NN bench run:** one bench session per H2 section; capture full terminal log + xxd diff + voltage readings; commit.
- **Per plan close:** Re-read `04-HW-VALIDATION.md` to confirm all in-scope §-sections are populated; commit plan SUMMARY.
- **Phase gate:** All 5 §-sections present + each has a `PASS` verdict + zero `FAIL` verdicts unresolved by D-07 triage; then `/gsd-verify-work`.

### Wave 0 Gaps

- None — existing test infrastructure (native Unity suite + check_dispatch.py + the test scripts post-HW-01-fix) covers the verification surface. The bench runs themselves are the primary evidence.

## Security Domain

Phase 4 is bench validation of existing closures. The security-relevant code (SAF-04 VPP check, SAF-05 chip-ID check, Phase 13 algo override) has already shipped under the v1.1 ASVS coverage in Phase 1. Phase 4 confirms on real silicon that the closures hold.

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | n/a (single-operator bench, USB serial) |
| V3 Session Management | no | n/a |
| V4 Access Control | no | n/a |
| V5 Input Validation | yes (carried) | Wire JSON parsing in `json_parser.c` already validated by WIRE-01/02 and check_dispatch.py |
| V6 Cryptography | no | n/a |

### Known Threat Patterns (carried from v1.1)

| Pattern | STRIDE | Standard Mitigation | Phase 4 Verification |
|---------|--------|---------------------|----------------------|
| Hardware-damage path via 12V on A14 of 5V AT28C EEPROM | Tampering / DoS (physical) | Phase 13 build_db.py inline override (3-predicate) | HW-04 — DMM at P1_VPP reads 0 V throughout |
| Hardware-damage path via overvoltage VPP on Intel flash | Tampering (physical) | SAF-04 closure (`flash_intel_check_vpp`) | HW-05 Sub-run A — VPP-HIGH branch aborts cleanly |

## Plan-Execution Rhythm Hints

### Wave Structure (per D-02)

- **Wave 1:** Plan 04-01 (HW-01 only). Single executor; software-only; no bench dependency; completable in minutes.
- **Wave 2:** Plan 04-02 (HW-02 + HW-03 + HW-04). Single executor (single bench resource); each H2 section independently committable per D-10. Estimated 60-90 min total bench time (3 chips × 15-30 min each including socket cleaning, photo, log capture).
- **Wave 3:** Plan 04-03 (HW-05). Single executor; ~30-45 min bench time (two sub-runs: abort + nominal).

### Bench-Resume Convention (per D-10)

Each HW-NN H2 section in `04-HW-VALIDATION.md` is independently committable. Resume rhythm:
1. Read `04-HW-VALIDATION.md` → identify which H2 sections are filled.
2. The next unfilled section is the resume point.
3. Each completed section's commit is `docs(04-NN): HW-NN bench run — <chip>` per D-08.

### Atomic Commit Sequence (per D-08)

```
Wave 1:
  firestarter_app@<hash> — fix(test-scripts): point at chip_database.json per WARNING-4 closure
  <meta-repo>@<hash>     — docs(04-01): HW-01 SUMMARY + 04-HW-VALIDATION.md §1

Wave 2:
  <meta-repo>@<hash> — docs(04-02): HW-02 bench run — W27C512
  <meta-repo>@<hash> — docs(04-02): HW-03 bench run — AM29F040 (chip-erase)
  <meta-repo>@<hash> — docs(04-02): HW-03 bench run — SST39SF040 (sector-erase)
  <meta-repo>@<hash> — docs(04-02): HW-04 bench run — AT28C256 (5V invariant)
  <meta-repo>@<hash> — docs(04-02): plan 04-02 summary

Wave 3:
  <meta-repo>@<hash> — docs(04-03): HW-05 bench run — AM28F010 sub-run A (abort)
  <meta-repo>@<hash> — docs(04-03): HW-05 bench run — AM28F010 sub-run B (nominal)
  <meta-repo>@<hash> — docs(04-03): plan 04-03 summary
```

### Failure Triage (per D-07)

Each plan's task list should include a triage decision branch at each bench-run task:
- **firmware bug surfaced** → file new FW-NN requirement in REQUIREMENTS.md (out-of-band) → block Phase 4 close until fix lands and re-run passes.
- **chip-specific issue** → substitute (e.g., use a different AM28F010 from a different vendor) OR document deferral to v1.2 in `§N` evidence block + add to STATE.md Open Blockers.
- **operator error** → retry with corrected procedure; do not record in artifact.

PLAN 04-02 and PLAN 04-03 should explicitly state "if [trigger], file follow-up via REQUIREMENTS.md not in this phase" so the executor does not in-line a firmware fix.

## Project Constraints (from CLAUDE.md)

From `./CLAUDE.md` (meta-repo) and `firestarter_app/CLAUDE.md`:

- **No source code edits to `firestarter/` or `firestarter_app/` beyond HW-01 test-script fix.** Phase 4 is verification-only (per CONTEXT.md scope + the meta CLAUDE.md sub-repo separation rule).
- **Serial baud is 250000.** Test scripts and `firestarter` CLI both honor this (constants.py + serial_comm.py). Do not change.
- **EPROM database lives at `firestarter_app/firestarter/data/chip_database.json`.** User overrides at `~/.firestarter/database.json` merge per `database.py:213-238` (shallow-update on `name` match within manufacturer key). HW-05 abort run uses this override mechanism.
- **Constants/flag bits duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`.** Phase 4 does not touch either — no changes needed.
- **Board buffer-size difference (Uno 512 B / Leonardo 1024 B) affects chunked transfer in `eprom_operations.py`.** Multi-board cross-check is a deferred Phase 4 item. If the user's bench is one board, document which.
- **Hardware calibration persists in Arduino EEPROM via `rurp_configuration_t`.** `firestarter config -r1 -r2 --rev` writes to this. **No VPP setpoint field exists** in `rurp_configuration_t` per CLI surface — see Open Questions.
- **From `firestarter_app/CLAUDE.md` Database Pipeline section:** Phase 13 WARNING-5 override is documented; HW-04 verifies it on silicon. Build_db.py override is data-layer only; firmware unchanged.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `~/.firestarter/database.json` override mechanism shallow-merges per-chip `vpp_mv` without invalidating other DB fields (algorithm, pinout, chip-id) | §HW-05 | If the merge is replace-all (not shallow), the override file would need to repeat every field. Mitigation: `database.py:213-238` _merge_databases code is grep-verified to use `dict.update()` which IS shallow merge — this assumption is **VERIFIED**, not assumed. Reclassifying. |
| A2 | The Sub-run A abort signature `ERROR: VPP is high: X.XV > Y.YV` is the literal wire prefix the host CLI emits to stdout | §HW-05 | Source string at `flash_intel.cpp:41` uses `firestarter_response_format(RESPONSE_CODE_ERROR, "VPP is high: %u.%uV > %u.%uV", ...)`. Macro emits via `log_error()` → `rurp_log(LOG_ERROR_MSG, msg)` where `LOG_ERROR_MSG[]="ERROR"`. The Python parse at `serial_comm.py:48` PREFIX_REGEX matches `ERROR:` exactly. Logger output prefix prepended at `serial_comm.py:194-195` (`rurp_logger.log(level, f"{log_prefix}: {message}")` where `log_prefix="ERROR"` for non-debug). Final stdout line is `RURP: ERROR: VPP is high: ...` or similar based on log handler config. The substring `ERROR: VPP is high` is grep-stable — assumption is **VERIFIED**. |
| A3 | The CONTEXT.md D-05 phrasing "lower regulator setpoint via `firestarter config`" is a misalignment with the actual CLI surface, and the DB-override alternative achieves the same load-bearing two-run contrast | §HW-05 + Open Questions | If the user intended a different mechanism the planner doesn't know about (e.g., a non-public undocumented config field), the abort run would need to use that mechanism. Mitigation: surface as Open Question #1; let the planner / user confirm. |
| A4 | The SST39SF040 sector-erase variant in HW-03 uses `-a <nonzero>` flag to `firestarter write` to trigger the sector-erase path | §HW-03 | Verified at `flash_type_3.cpp:94-102` (`flash3_erase_execute` branches on `handle->address != 0`). Host CLI's `firestarter write -a <addr>` sets `command_dict["address"] = <addr>` in `eprom_operations.py:179` — passes verbatim through to wire JSON. Assumption is **VERIFIED**. |
| A5 | `firestarter verify` exit code semantics: exit 0 on byte-match, exit 1 on mismatch | §HW-02..HW-04 | `eprom_operations.py:559-579` `verify_eprom` returns `is_ok` from `_run_state_machine`; `main.py:541-542` checks return and exits accordingly. The wire-level verify is via `memory_verify_execute` at `memory.cpp:218-227` which emits `ERROR: 0x%02x != 0x%02x at 0x%06x` on mismatch — propagates to ERROR: line → exit 1. **VERIFIED.** |

After re-verification, **A1, A2, A4, A5 are VERIFIED (not assumed)**. Only **A3 remains an actual assumption** — the planner should resolve via Open Question #1.

## Open Questions

### 1. D-05 mechanism: `firestarter config` vs DB override for HW-05 underpowering

**What we know:** CONTEXT.md D-05 specifies "Run `firestarter config` to lower the VPP regulator setpoint to a value below Intel's required ~12V (target 10000 mV = 10 V)." The live `firestarter config` CLI at `main.py:256-271` exposes only `--rev`, `-r1/--r16`, `-r2/--r14r15` — no VPP setpoint argument. The wire-protocol `CMD_CONFIG` path at `firestarter.cpp:107-115` parses `r1`, `r2`, `rev` fields into `rurp_configuration_t` via `json_parse_config`. No VPP-millivolt field exists.

**What's unclear:** Whether the user has a different mechanism in mind, or whether D-05's phrasing was a research-time assumption that needs revision.

**Recommendation:** The DB-override mechanism (`~/.firestarter/database.json` with lower `vpp_mv` for AM28F010) achieves the same load-bearing two-run contrast (abort + nominal). It's repeatable (delete file to restore), reversible (no calibration write), and exercises the same `flash_intel_check_vpp` → ERROR path. The planner should adopt the DB-override mechanism for PLAN 04-03 and update the D-05 framing in the SUMMARY / VERIFICATION artifacts. If the user disagrees, the alternative is a firmware-side dev-tool or a hardware modification — both rejected in D-05 deliberations as not-reversible-by-config.

**Important nuance:** The SAF-04 abort branch is **VPP-HIGH** (measured > setpoint + 500 mV), not VPP-LOW. Lowering the regulator output would route through the WARN branch (VPP-LOW), not the ERROR branch. The correct underpowering is to **lower the DB setpoint below the unchanged regulator output** so the measured 12 V exceeds the setpoint + 500 mV threshold. The framing in D-05 ("underpowered VPP") is operationally inverted: what the test actually exercises is "measured-VPP exceeds expected-VPP by enough to trip the over-voltage guard." Phase 1's SAF-04 closure was designed primarily to catch the over-voltage case (chip-damage hazard); under-voltage detection was a softer signal. The HW-05 evidence will demonstrate the over-voltage guard.

### 2. HW-01 second-drift (jq schema)

**What we know:** After fixing the filename references, the test scripts' jq queries use `.["memory-size"]`, `.["has-chip-id"]`, `.["can-erase"]`, `.["name"]` — none of these match the new `chip_database.json` schema (which uses `.electrical.size_bytes`, `.programming.chip_id_check`, etc.).

**What's unclear:** Whether the user's expectation in D-01 ("`sed`-class fix on two .sh files") encompasses the jq-path flip or whether the jq-path flip is its own follow-up.

**Recommendation:** Plan 04-01 should include a Wave-0 task to run the post-fix `jq -e` query and confirm exit-0 (chip metadata extracted). If it fails, expand HW-01 scope to include the jq-path flips. The planner can either:
- (A) Pre-author the jq-path flip tasks (defensive — covers the worst case); OR
- (B) Author only the filename fix, and gate the schema-flip on the validation step (minimal — possibly under-scopes).

Recommendation (A) — pre-author both; the additional effort is small and avoids a Wave-1 round-trip.

### 3. HW-03 — both chips fully exercised, or one variant each?

**What we know:** ROADMAP success criterion 3 reads "an AM29F040 (chip-erase + write) and an SST39SF040 (sector-erase + write), both algo=0x06". The conjunction "AM29F040 (chip-erase) AND SST39SF040 (sector-erase)" reads naturally as one variant per chip.

**What's unclear:** Whether the user wants chip-erase + sector-erase on each chip (4 total bench runs in §3) or one variant per chip (2 bench runs in §3).

**Recommendation:** Interpret literally — one variant per chip (2 bench runs in §3). AM29F040 → chip-erase full write (default `firestarter write` invocation). SST39SF040 → sector-erase write only (using `-a 0x10000`). This satisfies the ROADMAP success criterion gate and avoids 2 extra bench runs. If the user wants both variants on both chips, the planner can append them later as `§3 Sub-run C / D`.

## Sources

### Primary (HIGH confidence — verified by direct grep against live tree at write time, 2026-05-12)

- `firestarter_app/firestarter_test.sh:31` and `firestarter_app/write_test.sh:17` — broken `database_generated.json` refs (HW-01)
- `firestarter_app/firestarter/data/chip_database.json` — DB entries for W27C512, AM29F040, SST39SF040, AT28C256, AM28F010 (verified via Python script lookup)
- `firestarter_app/tools/build_db.py:221-247` — Phase 13 algorithm override (DIP28_2764 + Flash/EEPROM + 0x07 → 0x0D)
- `firestarter_app/firestarter/database.py:213-238` — `_merge_databases` shallow-update path used for user overrides
- `firestarter_app/firestarter/database.py:387,510,518` — `vpp_mv` wire-emit path
- `firestarter_app/firestarter/eprom_operations.py:130-579` — write/verify/read state machine and exit semantics
- `firestarter_app/firestarter/serial_comm.py:37-48,194-195` — ERROR/WARN line parsing and logger format
- `firestarter_app/firestarter/main.py:70-133,256-271` — argparse surface for read/write/verify/config subcommands
- `firestarter_app/firestarter/hardware.py:109-165` — `set_hardware_config` wire emit (confirms no `vpp_mv` field in CMD_CONFIG)
- `firestarter/src/proms/flash_intel.cpp:25-50,74-99` — SAF-04 check_vpp + write_init with CR-01 safety clear
- `firestarter/src/proms/eeprom_28c.cpp:34-128` — configure / write_init / write_execute / chip-ID check (SAF-05)
- `firestarter/src/proms/memory.cpp:44-117` — algo-first dispatch chain (`protocol == 0x10` → flash_intel; `0x0D` → eeprom28c; `0x06` → flash3; `0x07` → eprom)
- `firestarter/src/proms/flash_type_3.cpp:30-114` — AMD flash configure / erase branch / sector-erase byte-flip
- `firestarter/src/proms/eprom.cpp:30,79-181,199-247` — UV-EPROM configure + check_vpp (the W27C512 path)
- `firestarter/include/logging.h:79-194` — `log_error`, `log_warn`, `firestarter_response_format` macro expansion
- `firestarter/src/logging.c:7-14` — PROGMEM line prefix strings (`"OK"`, `"DATA"`, `"WARN"`, `"ERROR"`)
- `firestarter/src/operation_utils.cpp:329-350` — `_check_response` switch that drives the per-line log emission
- `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` Truth #1, #3 — SAF-04 evidence
- `.planning/milestones/v1.0-phases/13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we/13-VERIFICATION.md` Truth #1-#8 — Phase 13 override evidence
- `.planning/milestones/v1.0-phases/05-intel-flash/05-VERIFICATION.md` — REQ-SAF-01 Intel closure cross-milestone narrative
- `.planning/phases/03-retroactive-verification-phases-01-10/03-LEARNINGS.md` — atomic-commit, grep-at-write-time, follow_ups schema patterns
- `.planning/STATE.md` — Phase 1 D-04 SAF-04 / D-05 SAF-05 override / D-13 atomic-commit

### Secondary (MEDIUM — derived inference, cross-verified across multiple grep targets)

- The asymmetry between VPP-HIGH (ERROR) and VPP-LOW (WARN) branches in `flash_intel_check_vpp` — derived from reading lines 39-47 and macro expansions in `include/logging.h`; cross-verified by the firmware code's call to `firestarter_warning_response_format` (line 45) vs `firestarter_response_format(RESPONSE_CODE_ERROR or WARNING, ...)` (line 41).
- The DB-override mechanism for `vpp_mv` — derived from reading `database.py:_merge_databases` + the comment "manual_items takes precedence" + `dict.update()` semantics.

### Tertiary (LOW — convention only, not behavioral)

- Photo file-naming convention `HW-NN-<chip>-<isodate>.jpg` (Claude's Discretion recommendation; user can override).

## Metadata

**Confidence breakdown:**
- HW-01 scope: HIGH — grep-verified exactly 2 broken refs; second-drift (jq schema) flagged with concrete recommendation.
- HW-02 path: HIGH — `memory.cpp:92` dispatch confirmed; `configure_eprom` and `eprom_check_vpp` flow direct-cited.
- HW-03 path: HIGH — sector-erase vs chip-erase branch at `flash_type_3.cpp:94-102` explicitly grep-confirmed.
- HW-04 path: HIGH — `configure_eeprom28c` register-write absence cross-verified with 13-VERIFICATION.md grep result; SDP-disable behavior fully traced.
- HW-05 path: HIGH for code-trace; MEDIUM for mechanism (D-05 underpowering route corrected from `firestarter config` to DB override).
- ERROR: signature: HIGH — full chain from `flash_intel.cpp:41` through `logging.c:14` to `serial_comm.py:48` PREFIX_REGEX traced.
- D-05 mechanism: MEDIUM — surfaced as Open Question #1; correction recommended.

**Research date:** 2026-05-12
**Valid until:** 2026-06-12 (30 days; stable v1.1 codebase; bench-validation rhythm not subject to upstream churn)

---

*Research complete. Planner can now author Plans 04-01 (HW-01), 04-02 (HW-02 + HW-03 + HW-04), 04-03 (HW-05).*
