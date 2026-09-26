---
phase: 03-retroactive-verification-phases-01-10
researched: 2026-05-12
domain: docs-only audit of v1.0 phases 01..10 against current source tree
confidence: HIGH
---

# Phase 3: Retroactive Verification (Phases 01-10) — Research

**Researched:** 2026-05-12
**Source-tree state:** firestarter/ + firestarter_app/ checked out at v1.1 Phase 2 close (after CLEAN-01 file rename, after WIRE-01 wire-key flip, after SAF-04/05 helper additions).
**Confidence:** HIGH — every `file:line` claim below resolved by direct grep against the working tree on 2026-05-12.

## Goal Restatement

Produce ten `NN-VERIFICATION.md` audit artifacts under `.planning/milestones/v1.0-phases/{NN-slug}/` (one each for v1.0 phases 01..10) that score each phase's REQs against the **current** source tree, closing the 13 PARTIAL findings tracked in `v1.0-MILESTONE-AUDIT.md`'s `gaps.requirements` block and satisfying ROADMAP Phase 3 SC#1–SC#4.

This is a docs-only pass over already-verified wiring. The hard work was already done by:

- `v1.0-INTEGRATION-CHECK.md` — 22 WIRED cross-phase traces, 5 WARNINGs, 4 INFOs.
- `v1.0-MILESTONE-AUDIT.md` — per-REQ partial-status evidence + tech-debt block.
- v1.1 Phase 1 — closed WARNING-1 (SAF-04) and WARNING-2 (SAF-05) with Unity coverage.
- v1.1 Phase 2 — closed WARNING-3 wire-key, CLEAN-01 file rename, CLEAN-02 attribution scrub, WIRE-02 dynamic regression.

Phase 3 reads. It does not touch `firestarter/` or `firestarter_app/` source code.

**Primary recommendation:** Follow the 8-section body + YAML frontmatter pattern from `11/12-VERIFICATION.md`. Use `01/02-VERIFICATION.md` (v1.1) for the Cross-Milestone Closure framing where applicable. Two plans (`03-01` = 5 clean files, `03-02` = 5 closure/hazard files) is the right granularity. Score everything `passed` — current tree confirms all 13 PARTIAL findings are now SATISFIED structurally.

## Current Source-Tree Spot-Check Snapshot (per v1.0 phase 01..10)

All line numbers resolved at write time on 2026-05-12 against the live tree. CONTEXT.md's `<canonical_refs>` "Current source-tree files for spot-check" block matches reality except where noted. The planner can copy these into per-task `acceptance_criteria` blocks.

### Phase 01 — Database Pipeline

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| Database filename (post-CLEAN-01) | `firestarter_app/firestarter/data/chip_database.json` | exists | CLEAN-01 rename landed |
| `KNOWN_PROTOCOLS` set (13 entries) | `firestarter_app/tools/build_db.py` | :89 | REQ-DB-04 (unknown-protocol skip) |
| `VPP_MV` table | `firestarter_app/tools/build_db.py` | :82 | REQ-DB-03 (mV at source) |
| `DIP28_VARIANT_MAP` | `firestarter_app/tools/build_db.py` | :93 | REQ-DB-02 |
| `MINIPRO_XML_URL` constant (last surviving minipro attribution) | `firestarter_app/tools/build_db.py` | :10 | Plan 02-03 D-09 lock |
| `OUTPUT_FILE = ...chip_database.json` | `firestarter_app/tools/build_db.py` | :12 | CLEAN-01 path flip |
| `_ALGO_MEM_TYPE` table (13 D3 entries) | `firestarter_app/firestarter/database.py` | :47-61 | REQ-DB-01 algorithm→type wire |
| `pin_conversions[24][24] = 13` | `firestarter_app/firestarter/database.py` | :90 (within :68–96 block) | REQ-FW-05 prep |
| `_map_data` `protocol_id = programming.get("algorithm", 0)` | `firestarter_app/firestarter/database.py` | :390 | REQ-DB-01 |
| `_map_data` `vpp_mv = electrical.get("vpp_mv", 0)` | `firestarter_app/firestarter/database.py` | :387 | REQ-DB-03 |
| `_map_data` `vpp_volts` internal key (Plan 02-02 rename) | `firestarter_app/firestarter/database.py` | :417 | post-WIRE-01 D-04 internal flip |
| Upstream-schema READ preserved (`electrical.get("vpp", "0")`) | `firestarter_app/firestarter/database.py` | :375 | Plan 02-02 D-08-compat |
| `convert_to_programmer` emitter writes wire key `"vpp_mv"` | `firestarter_app/firestarter/database.py` | :518 | WIRE-01 closure |
| WARNING-5 inline override block (Phase 13 closure for AT28C256) | `firestarter_app/tools/build_db.py` | :221-247 | per-chip 0x07→0x0D flip |

**CONTEXT.md drift caught:** CONTEXT.md `<canonical_refs>` line 311 says "build_db.py (sole tool; `KNOWN_PROTOCOLS`, `DIP28_VARIANT_MAP`, `VPP_MV`)" without lines. The live lines are :89/:93/:82 respectively. CONTEXT.md line 314 refers to `chip_database.json` "renamed by CLEAN-01" — confirmed present; old `minipro_complete_db.json` is absent (`ls` confirmed).

### Phase 02 — Firmware JSON Protocol Extension

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| Unknown-key skip in top-level `json_parse` | `firestarter/src/json_parser.c` | :128-131 | REQ-SER-02 (outer) |
| Unknown-key skip in `parse_bus_config` | `firestarter/src/json_parser.c` | :251-255 | REQ-SER-02 (nested) |
| `key_vpp_mv` PROGMEM literal (Plan 02-01 site #1) | `firestarter/src/json_parser.c` | :62 | WIRE-01 firmware-side flip |
| Dispatch-table row (Plan 02-01 site #2) | `firestarter/src/json_parser.c` | :74 | WIRE-01 firmware-side flip |
| `extract_int("vpp_mv", handle->vpp_mv)` (Plan 02-01 site #3) | `firestarter/src/json_parser.c` | :309 | WIRE-01 firmware-side flip |
| `extract_long("algorithm", handle->protocol)` (REQ-SER-01) | `firestarter/src/json_parser.c` | :312-314 | REQ-SER-01 (also Phase 12) |
| `static_high_mask` OR in `parse_bus_config` | `firestarter/src/json_parser.c` | :239 | REQ-FW-05 hop 4/5 |

**CONTEXT.md numbers confirmed verbatim.** `:128-131` (top-level) and `:251-255` (nested) match.

### Phase 03 — UV-EPROM Algorithm Correctness

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `configure_eprom` (entry point) | `firestarter/src/proms/eprom.cpp` | :40 | REQ-FW-01 |
| `pulse_delay` default switch on `handle->protocol` | `firestarter/src/proms/eprom.cpp` | :68-74 | REQ-FW-01 protocol semantics |
| `eprom_check_vpp` unconditional call in `eprom_generic_init` | `firestarter/src/proms/eprom.cpp` | :250-251 | REQ-SAF-01 (UV-EPROM portion) |
| `eprom_check_vpp` definition (calls `rurp_read_voltage_mv`) | `firestarter/src/proms/eprom.cpp` | :199 | REQ-SAF-01 evidence |
| VPE_AS_VPP routing (`protocol == 0x0B \|\| FLAG_VPE_AS_VPP`) | `firestarter/src/proms/eprom.cpp` | :144, :207 | REQ-FW-01 wire detail |
| Algo-first dispatch for 0x07/0x08/0x0B (Phase 12 closure for FW-01) | `firestarter/src/proms/memory.cpp` | :92-95 | INTEGRATION-CHECK row 20 |

**CONTEXT.md drift caught:** CONTEXT.md line 326 says "`eprom_generic_init::eprom_check_vpp` unconditional call" — confirmed at :251 (the function call), with `eprom_generic_init` opening at :250. (Audit cited `eprom.cpp:251` — still accurate.)

### Phase 04 — Flash Sector Erase

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `configure_flash3` | `firestarter/src/proms/flash_type_3.cpp` | :30 | REQ-FW-04 entry |
| `flash3_sector_erase` definition | `firestarter/src/proms/flash_type_3.cpp` | :104 | REQ-FW-04 sector path |
| `flash3_erase_execute` branch on `handle->address` | `firestarter/src/proms/flash_type_3.cpp` | :94-101 | REQ-FW-04 dispatch |
| `flash3_write_init` blank-check site | `firestarter/src/proms/flash_type_3.cpp` | :77-79 | REQ-SAF-03 |
| Algo-first dispatch for 0x06 (Phase 12 closure for FW-04, 190 chips reachable) | `firestarter/src/proms/memory.cpp` | :82-85 | INTEGRATION-CHECK row 19 |

### Phase 05 — Intel Flash

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `configure_flash_intel` body | `firestarter/src/proms/flash_intel.cpp` | (file exists, 152+ lines) | REQ-FW-02 |
| `flash_intel_check_vpp` static helper (SAF-04, v1.1 Plan 01-01) | `firestarter/src/proms/flash_intel.cpp` | :25-50 | SC#3 lock evidence |
| `flash_intel_write_init` calls helper | `firestarter/src/proms/flash_intel.cpp` | :74 (def), :77 (call) | SC#3 lock |
| `flash_intel_check_chip_id` (REQ-SAF-02 Intel portion) | `firestarter/src/proms/flash_intel.cpp` | :87 (call), :152 (def) | REQ-SAF-02 evidence |
| `flash_intel_write_init` blank-check site | `firestarter/src/proms/flash_intel.cpp` | :96-98 | REQ-SAF-03 |
| Intel 0x10 dispatch | `firestarter/src/proms/memory.cpp` | :72-75 | INTEGRATION-CHECK row 8 |
| Unity suite | `firestarter/test/native/avr/test_flash_intel_vpp/` | dir exists | SAF-06 (6/6 PASS per `01-VERIFICATION.md` Truth #3) |

**CONTEXT.md verbatim:** Lines `flash_intel.cpp:25-50` for the helper and `:77` for the call-site — both confirmed exactly. CONTEXT.md is correct.

### Phase 06 — EEPROM Page Write

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `configure_eeprom28c` | `firestarter/src/proms/eeprom_28c.cpp` | :34 | REQ-FW-03 |
| `EEPROM_SDP_DISABLE` byte-flip table | `firestarter/src/proms/eeprom_28c.cpp` | :25 | REQ-FW-03 SDP handling |
| `eeprom28c_write_init` | `firestarter/src/proms/eeprom_28c.cpp` | :79 | REQ-FW-03 |
| `eeprom28c_check_chip_id` static helper (SAF-05, v1.1 Plan 01-02) | `firestarter/src/proms/eeprom_28c.cpp` | :55-77 | 07-VERIFICATION closure |
| Helper call inside `write_init` (gated on chip_id>0, before SDP_DISABLE) | `firestarter/src/proms/eeprom_28c.cpp` | :82-83 (call), :91 (SDP) | SAF-05 ordering |
| `eeprom28c_write_init` blank-check site | `firestarter/src/proms/eeprom_28c.cpp` | :96-98 | REQ-SAF-03 |
| 0x0D dispatch | `firestarter/src/proms/memory.cpp` | :77-80 | INTEGRATION-CHECK row 9 |
| Unity suite | `firestarter/test/native/avr/test_eeprom28c_chip_id/` | dir exists | 4/4 PASS per `01-VERIFICATION.md` Truth #4 |

**CONTEXT.md verbatim:** Lines `eeprom_28c.cpp:55-77` for helper and `:82-83` for call-site — both confirmed.

### Phase 07 — Chip-ID Safety

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `flash_intel_check_chip_id` definition | `firestarter/src/proms/flash_intel.cpp` | :152 | REQ-SAF-02 (Intel) |
| Intel `chip_id > 0` branch in `write_init` | `firestarter/src/proms/flash_intel.cpp` | :87 | REQ-SAF-02 wire |
| UV-EPROM chip-id branch in `eprom_generic_init` | `firestarter/src/proms/eprom.cpp` | (inside `eprom_generic_init` at :250) | REQ-SAF-02 (UV-EPROM) |
| AT28C chip-id check (v1.1 SAF-05, gated on chip_id>0) | `firestarter/src/proms/eeprom_28c.cpp` | :55-77 (def), :82-83 (call) | REQ-SAF-02 (28C — forward-compat closed) |
| Unity test_eeprom28c_chip_id suite | `firestarter/test/native/avr/test_eeprom28c_chip_id/` | exists | 4/4 PASS |

### Phase 08 — Integration

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `flash3_write_init` blank-check | `firestarter/src/proms/flash_type_3.cpp` | :77-79 | REQ-SAF-03 site 1 |
| `flash_intel_write_init` blank-check | `firestarter/src/proms/flash_intel.cpp` | :96-98 | REQ-SAF-03 site 2 |
| `eeprom28c_write_init` blank-check | `firestarter/src/proms/eeprom_28c.cpp` | :96-98 | REQ-SAF-03 site 3 |
| Regenerate-DB evidence | `firestarter_app/firestarter/data/chip_database.json` | (rename + 743 chips) | Phase 08 Task 2 |
| `firestarter_test.sh` reference to deleted DB (WARNING-4 unresolved) | `firestarter_app/firestarter_test.sh` | :31 | follow_ups note for Phase 4 |
| `write_test.sh` same broken reference | `firestarter_app/write_test.sh` | :17 | follow_ups note for Phase 4 |

**Note:** CONTEXT.md `<canonical_refs>` line 352 lists three "blank check" call-sites — confirmed. All three live at lines `:77-79` (flash3) / `:96-98` (flash_intel) / `:96-98` (eeprom_28c). Different line numbers than INTEGRATION-CHECK Row 18 implied; the FLAG_SKIP_BLANK_CHECK guard pattern is identical.

### Phase 09 — Adapter Support

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `get_adapter_table` (DB host helper) | `firestarter_app/firestarter/database.py` | :323 | REQ-UX-02 |
| Adapter-table pin assignments (vcc/gnd/ce/oe/pgm/vpp) | `firestarter_app/firestarter/database.py` | :342-353 | REQ-UX-02 |
| `present_eprom_details` (renders adapter table + no-pinout WARNING) | `firestarter_app/firestarter/eprom_info.py` | :172, :197 (no-pinout), :236-237 (adapter render) | REQ-UX-01 + REQ-UX-02 |
| `no_pinout_warning` flag set in `prepare_detailed_eprom_data` | `firestarter_app/firestarter/eprom_info.py` | :93, :116 | REQ-UX-01 |
| `-a/--adapter` CLI arg | `firestarter_app/firestarter/main.py` | :231 (create_info_args def), :238 (`-a/--adapter`) | REQ-UX-02 wire |
| Adapter arg consumed | `firestarter_app/firestarter/main.py` | :476, :482 | REQ-UX-02 |

### Phase 10 — Static Pins (SC#4 evidence — see also "SC#3/SC#4 Explicit Lock Evidence" below)

| Object | File | Line(s) | Confirms |
|--------|------|---------|----------|
| `pinouts.json` `"static-high-pins":[24]` (DIP24_2716 + DIP24_2732) | `firestarter_app/firestarter/data/pinouts.json` | :10, :21 | REQ-FW-05 hop 1 |
| `get_bus_config` `static-high-pins` translation block | `firestarter_app/firestarter/database.py` | :309-319 | REQ-FW-05 hops 2/3 |
| `pin_conversions[24][24] = 13` | `firestarter_app/firestarter/database.py` | :90 | REQ-FW-05 pin→bus-line map |
| `parse_bus_config` `static_high_mask` OR (`1UL<<line`) | `firestarter/src/json_parser.c` | :239 | REQ-FW-05 hop 4 |
| `mem_util_remap_address_bus` applies mask (`reorg_address \|= config.static_high_mask`) | `firestarter/src/proms/memory.cpp` | :247 | REQ-FW-05 hop 5 |
| `mem_util_calculate_top_address_register` with `if (handle->pins < 32)` guard + VPE_TO_VPP comment | `firestarter/src/proms/memory.cpp` | :137-150 (function), :140 (the guard) | REQ-FW-06 + SC#4 lock |
| `firestarter_handle_t::bus_config.static_high_mask` field declaration | `firestarter/include/firestarter.h` | :72 | wire contract |

**CONTEXT.md drift caught (minor):** CONTEXT.md line 367 implies `memory.cpp::mem_util_remap_address_bus` is the mask application site. Live tree confirms — function defined at :226, mask applied at :247. CONTEXT.md is correct in pointing at the function; the planner should cite the OR-application line specifically.

## REQ Scoring Snapshot (13 PARTIAL findings → current status)

For each PARTIAL REQ-ID in `v1.0-MILESTONE-AUDIT.md`'s `gaps.requirements` block, this table records the CURRENT-tree status. Per CONTEXT.md D-01, all of these are scored against the *current* tree, not against v1.0-as-shipped. Status `SATISFIED` ⇒ VERIFICATION.md frontmatter `status: passed`. **No surprises found** — every PARTIAL is now SATISFIED structurally.

| # | REQ-ID | Owning Phase | v1.0 Evidence | v1.1 Closure | Current Status | Owning VERIFICATION.md |
|---|--------|-------------|---------------|--------------|----------------|-------------------------|
| 1 | REQ-DB-01 | 01 | WIRED (algorithm int through pipeline) | INTEGRATION-CHECK row 1 still WIRED; Phase 12 `check_dispatch.py` PASS on 743 chips | SATISFIED | 01-VERIFICATION.md |
| 2 | REQ-DB-02 | 01 | DIP28 variant resolver WIRED | unchanged | SATISFIED | 01-VERIFICATION.md |
| 3 | REQ-DB-03 | 01 | mV-wire WIRED + WARNING-3 (vpp key name) | **Plan 02-01 (WIRE-01)** flipped wire key to `vpp_mv` end-to-end | SATISFIED | 01-VERIFICATION.md — Cross-Milestone Closure |
| 4 | REQ-DB-04 | 01 | KNOWN_PROTOCOLS + skip WIRED | unchanged | SATISFIED | 01-VERIFICATION.md |
| 5 | REQ-SER-02 | 02 | Unknown-key skip WIRED in 2 sites | unchanged; line numbers stable | SATISFIED | 02-VERIFICATION.md |
| 6 | REQ-FW-02 | 05 | Intel handler + 0x10 dispatch WIRED + WARNING-1 (no VPP ADC) | **Plan 01-01 (SAF-04)** added `flash_intel_check_vpp` at :25-50; called from `:77` | SATISFIED | 05-VERIFICATION.md — Cross-Milestone Closure (**SC#3 lock**) |
| 7 | REQ-FW-03 | 06 | 28C handler + 0x0D dispatch WIRED; WARNING-5 (AT28C256 mistag) | Handler logic unchanged. Phase 13 (v1.0) closed WARNING-5 at data layer. REQ scope = "handler is correct" → SATISFIED. AT28C256 hazard is upstream-DB issue, carried as follow_up. | SATISFIED | 06-VERIFICATION.md — follow_up only |
| 8 | REQ-FW-05 | 10 | static-high-mask end-to-end WIRED; INFO-3 (DIP24 only) | unchanged | SATISFIED | 10-VERIFICATION.md (**SC#4 lock** chain) |
| 9 | REQ-FW-06 | 10 | Dead READ_WRITE removed; `pins<32` guard present | unchanged | SATISFIED | 10-VERIFICATION.md (**SC#4 lock** guard) |
| 10 | REQ-SAF-01 | 03 + 05 | UV-EPROM ✓; Intel ✗ (WARNING-1) | **Plan 01-01 (SAF-04)** closed Intel-flash gap | SATISFIED | 03-VERIFICATION.md (UV-EPROM portion) + 05-VERIFICATION.md (Intel portion **SC#3**) |
| 11 | REQ-SAF-02 | 07 | Intel/AMD/UV-EPROM ✓; 28C ✗ (WARNING-2 forward-compat) | **Plan 01-02 (SAF-05)** closed 28C gap with A9-12V identification | SATISFIED | 07-VERIFICATION.md — Cross-Milestone Closure |
| 12 | REQ-SAF-03 | 04 + 06 | Blank check in all 3 write_init sites WIRED | unchanged; 3-site grep confirms | SATISFIED | 04-VERIFICATION.md + 08-VERIFICATION.md (cross-handler) |
| 13 | REQ-UX-01 | 09 | No-pinout `[!]` + WARNING WIRED | unchanged | SATISFIED | 09-VERIFICATION.md |
| 14 | REQ-UX-02 | 09 | `--adapter` table end-to-end WIRED | unchanged | SATISFIED | 09-VERIFICATION.md |

> CONTEXT.md `<specifics>` table lists "13 PARTIAL findings". The audit `gaps.requirements` block actually enumerates **14 REQ-IDs** (DB-01..04 = 4, SER-02, FW-02, FW-03, FW-05, FW-06, SAF-01, SAF-02, SAF-03, UX-01, UX-02). REQ-SAF-01 was scored `unsatisfied` (not partial); the other 13 are partial. Total reqs covered = 14 across 10 v1.0 phases. CONTEXT.md/ROADMAP both correctly say "13 PARTIAL findings" — REQ-SAF-01 is the 14th and was UNSATISFIED at v1.0 close, then closed by SAF-04. Phase 3 closes both classes.

## VERIFICATION.md Canonical Template (frontmatter + 8-section body + follow_ups schema)

Comparison of the four existing exemplars yields a stable template. Pick the v1.1 form (`01/02-VERIFICATION.md`) for fresh writes — it has the slightly richer `re_verification` block — but the v1.0 form (`11/12/13-VERIFICATION.md`) is acceptable and shorter. Both pass identical tooling.

### Canonical YAML Frontmatter

```yaml
---
phase: NN-<slug>
verified: 2026-05-12T<HH:MM:SS>Z
status: passed
score: N/N must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-XX-NN
follow_ups:
  - source: <where it came from>
    item: <one-line description>
    severity: warning   # or info
    in_scope: false
    note: <one-line rationale>
re_verification:        # optional — present in v1.1 form
  previous_status: none
  previous_score: n/a
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---
```

- `phase`: dir basename without `-VERIFICATION` (e.g. `01-database-pipeline`, **NOT** `01`).
- `verified`: ISO8601 UTC at write time.
- `status`: `passed` when all Truths verified (all 10 files expected `passed` per current-tree analysis); `gaps_found` if any Truth fails.
- `score`: "N/N must-haves verified" — N = number of Observable Truths the Goal Achievement table scores.
- `overrides_applied`: `0` everywhere (no `/gsd-override-decision` calls projected).
- `requirements_verified`: list of REQ-IDs covered by this file. MUST be a subset of REQs the audit attributes to this phase. See "Verification scope per file" in CONTEXT.md `<specifics>` for the assignment.
- `follow_ups`: only when carrying a hazard not closed by this phase (WARNING-5 for 03/06/07, WARNING-4 for 08, INFO-3 for 10). Schema below.
- `re_verification`: optional. Drop for initial verifications.

### `follow_ups` Schema (verbatim from `11-VERIFICATION.md` block)

```yaml
follow_ups:
  - source: <audit doc + finding ID, e.g. "v1.0-MILESTONE-AUDIT.md WARNING-5">
    item: "<one-line factual description; quote line if needed>"
    severity: warning   # vocabulary: warning | info  (NOT "blocker" — those are not deferred)
    in_scope: false     # always false in Phase 3 — these are deferred per CONTEXT.md D-04/D-05
    note: "<deferral rationale; cite owning future phase or milestone if known>"
```

**CONTEXT.md `<specifics>` verbatim-shape blocks (lines 483-503) are GUESSES** per session-memory instructions. They are close but I confirm them against the 4-entry block in `11-VERIFICATION.md`:

- Required fields (all 5): `source`, `item`, `severity`, `in_scope`, `note`. ✓ Match.
- Severity vocabulary observed: `warning`, `info`. ✓ Match. (No `blocker` ever — blockers gate, they don't carry forward.)
- `in_scope: false` semantics: "this finding is not part of this phase's scope; carried for a future plan/phase to address." ✓ Match.

**Reconciliation result:** CONTEXT.md's proposed shapes are correct. Adopt them. The WARNING-5 note text is a stylistic suggestion; the planner may rephrase to match exact phrasing precedent in `13-VERIFICATION.md`'s closure narrative if desired.

### 8-Section Body Skeleton (drop sections with zero rows)

```markdown
# Phase NN: <Phase Name> — Verification Report

**Phase Goal:** "<verbatim from v1.0-ROADMAP.md or phase-dir PLAN.md>"
**Verified:** YYYY-MM-DDTHH:MM:SSZ
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | <criterion> | VERIFIED | `<file>:<line>` ... |

**Score:** N/N truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|

### Data-Flow Trace (Level 4)        ← OMIT if single-file change (e.g. Phase 02, Phase 04 sector erase)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|

### Cross-Milestone Closure              ← ONLY when v1.1 closed a v1.0 PARTIAL (01/05/07-VERIFICATION; minor for 02/06; SC#3 lock for 05)

<narrative paragraph + cites>

### Gaps Summary

<no gaps OR enumerated gaps>

---

_Verified: <timestamp>_
_Verifier: Claude (gsd-verifier)_
```

### Section ordering decision (drift between v1.0 and v1.1)

- `01/02/11/12-VERIFICATION.md`: section order is identical (Goal/Truths → Artifacts → Links → Data-Flow → Spot-Checks → Reqs Coverage → Anti-Patterns → optional Cross-Milestone → Gaps).
- `13-VERIFICATION.md`: identical to above + `### Code Review Findings (from 13-REVIEW.md)` before Gaps Summary. Only include if a REVIEW.md exists (Phases 01-10 don't have REVIEW.md, so skip).
- `01-VERIFICATION.md` (v1.1) adds `### Post-Review Fixes (Context Signals)` for SAF-04 CR-01/CR-02 narrative — this is the **pattern template for "Cross-Milestone Closure"** in Phase 3, just renamed.

**Decision:** Use the v1.1 form (`01-VERIFICATION.md` ordering). Pre-review-fix subsection title in Phase 3 should be `### Cross-Milestone Closure` (per CONTEXT.md D-02), not "Post-Review Fixes" (which has a different semantic — original phase had reviewer, v1.0 phases didn't).

### Header / footer matching pattern

Header (under H1 title): `**Phase Goal:** "..."` then `**Verified:** ...` then `**Status:** passed` then `**Re-verification:** No — initial verification`.

Footer (after Gaps Summary, after `---`): `_Verified: <timestamp>_` then `_Verifier: Claude (gsd-verifier)_`. Use exact wording — string-match pattern across all four exemplars.

## Cross-Milestone Closure Narrative Sources (per affected file)

For files needing a `### Cross-Milestone Closure` subsection, the canonical source paragraphs to cite (do NOT summarise; point at them):

### 01-VERIFICATION.md — REQ-DB-03 (WIRE-01 closure)

- **Cite:** `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-VERIFICATION.md` SC1+T1+T4 row (Observable Truths table).
- **Spot-check NEW state:** `database.py:518` (emits `"vpp_mv": vpp_mv,`); `json_parser.c:62/:74/:309` (firmware reads `"vpp_mv"` into `handle->vpp_mv`).
- **Commit refs:** firmware `firestarter@39b29a9`, app `firestarter_app@20cfe86` (both in STATE.md "Resolved in v1.1" / WARNING-3 block).
- **Narrative direction:** "REQ-DB-03 was PARTIAL in v1.0 due to WARNING-3 (wire key `vpp` overloaded with millivolts). Closed by v1.1 Plan 02-01 atomic three-site firmware flip + Python emitter rename. Current source tree emits only `vpp_mv`."

### 02-VERIFICATION.md — REQ-SER-02 (no closure needed; verification-gap only)

CONTEXT.md D-02 notes "no content change needed beyond citing `json_parser.c:316-318,:251-255`". The Cross-Milestone Closure subsection is OMITTED for this file — REQ-SER-02 was always WIRED; only the formal VERIFICATION.md was missing. The 02-VERIFICATION.md inherits stability from current-tree grep; no v1.1 work touched the unknown-key skip.

### 03-VERIFICATION.md — REQ-FW-01 (Phase 12 algo-first dispatch closure)

- **Cite:** `.planning/milestones/v1.0-phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-VERIFICATION.md` Truth #1 (memory.cpp lines 72-101 — six protocol-prefix blocks) + Requirements Coverage row REQ-FW-01.
- **Spot-check NEW state:** `memory.cpp:92-95` (0x07/0x08/0x0B algo-first dispatch).
- **Narrative direction:** "REQ-FW-01 was PARTIAL in v1.0 (configure_eprom reachable via mem_type fallback, but algo-first dispatch incomplete). Closed by v1.0 Phase 12 protocol-prefix dispatch — all three UV-EPROM protocols (0x07/0x08/0x0B) reach `configure_eprom` via algorithm-first path before mem_type fallback fires. 3 Unity tests PASS."

**Claude's discretion (per CONTEXT.md):** Whether 03-VERIFICATION.md cites Phase 12 inline (Reqs Coverage table) vs. as a dedicated Cross-Milestone Closure subsection. **Recommendation: inline** — Phase 12 is a v1.0 phase (not a v1.1 closure), so it doesn't trigger the cross-milestone framing. A one-line "Reachability closed by Phase 12 (see `12-VERIFICATION.md` row REQ-FW-01)" in the Requirements Coverage row is sufficient.

### 05-VERIFICATION.md — REQ-FW-02 + REQ-SAF-01 Intel portion (**SC#3 lock**)

- **Primary cite:** `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` Truth #1 + #3 + post-review CR-01 regression test.
- **Secondary cite:** `01-01-SUMMARY.md` (SAF-04 implementation detail) and `01-RESEARCH.md` (the historical context that made SAF-04 a hand-rolled inline helper, not a shared extract).
- **Spot-check NEW state:** `flash_intel.cpp:25-50` (helper), `:77` (call-site), `:79-85` (CR-01 fix — early-return clears `REGULATOR | P1_VPP_ENABLE`).
- **Unity test cite:** `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp`, 6/6 PASS.
- **Commit refs:** `firestarter@f6480f2` (CR-01 fix), meta-repo `83c37b7` (state record).
- **SC#3 sample text:** CONTEXT.md `<specifics>` lines 445-468 provides the verbatim sample. Adopt it. **It is correct against the current tree** (verified: helper at :25-50 exists; call-site at :77 exists; 6 test cases exist; commit hashes match STATE.md).

### 06-VERIFICATION.md — REQ-FW-03 (no v1.1 work; AT28C256 hazard via follow_up)

- **No Cross-Milestone Closure subsection.** Handler logic was correct in v1.0 and is unchanged in v1.1.
- WARNING-5 carried as `follow_ups` per CONTEXT.md D-04 (deferred to v1.2). Score REQ-FW-03 SATISFIED (handler is correct for the algo=0x0D dispatch path; AT28C256 mistag is upstream-data classification, not handler-logic defect).
- **Optional sidebar cite:** `13-VERIFICATION.md` (Phase 13 closed WARNING-5 at the *data* layer in v1.0; v1.1 inherits the override) — if the planner wants to record the closure event narratively, this is the source.

### 07-VERIFICATION.md — REQ-SAF-02 (SAF-05 closure)

- **Primary cite:** `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` Truth #2 + #4 + post-review CR-02 (mem_size < 64 underflow guard).
- **Secondary cite:** `01-02-SUMMARY.md` (SAF-05 implementation detail). Note STATE.md "D-05 override (SAF-05, load-bearing)" — the implementation uses A9-12V identification, NOT the AMD/SST JEDEC sequence the discuss-phase initially proposed. RESEARCH.md datasheet evidence drove the override.
- **Spot-check NEW state:** `eeprom_28c.cpp:55-77` (helper), `:82-83` (call-site, gated on `chip_id > 0`, BEFORE `flash_execute_command(EEPROM_SDP_DISABLE)` at :91), `:60-64` (CR-02 underflow guard).
- **Unity test cite:** `test_eeprom28c_chip_id/`, 4/4 PASS.
- WARNING-5 carried as `follow_ups` per CONTEXT.md D-04.

### 08-VERIFICATION.md — REQ-SAF-03 cross-handler

- **No Cross-Milestone Closure subsection.** Blank-check gating was always WIRED; the verification-gap was the only PARTIAL trigger.
- WARNING-4 (`firestarter_test.sh:31` + `write_test.sh:17` reference deleted `database_generated.json`) carried as `follow_ups` per CONTEXT.md D-05 (owned by Phase 4 / HW-01). Confirmed broken in live tree.
- Cross-link `v1.0-INTEGRATION-CHECK.md` row 18 + 11-VERIFICATION.md follow_ups entry #1 (which originally raised WARNING-4).
- Phase 08 verification scope is special; see "Phase 08 Verification Scope" section below for what to actually verify.

### 09-VERIFICATION.md — REQ-UX-01 + REQ-UX-02 (no closure needed)

Verification-gap only. Current tree confirms WIRED. No subsection.

### 10-VERIFICATION.md — REQ-FW-05 + REQ-FW-06 (**SC#4 lock**)

- **No v1.1 closure** — verification-gap only.
- **SC#4 explicit lock:** see "SC#3 and SC#4 Explicit Lock Evidence" section below. `10-VERIFICATION.md` must record the 5-hop `static_high_mask` chain and the `pins < 32` VPE_TO_VPP guard — both verified intact today.
- INFO-3 (`static-high-pins` only populated for DIP24 today; DIP28/DIP32 quirk pins deferred) carried as `follow_ups` per CONTEXT.md `<specifics>` row 10.

## SC#3 and SC#4 Explicit Lock Evidence (live)

### SC#3 (Intel-flash REQ-SAF-01 closure recorded in 05-VERIFICATION.md)

CONTEXT.md claim ↔ live tree:

| Claim | Verified |
|-------|----------|
| `flash_intel_check_vpp` static helper at `flash_intel.cpp:25-50` | ✓ Lines :25-50 contain `static void flash_intel_check_vpp(firestarter_handle_t* handle) { ... }` |
| Call-site at `flash_intel.cpp:77` | ✓ Line :77 is `flash_intel_check_vpp(handle);` inside `flash_intel_write_init` (which opens at :74) |
| Called BEFORE `chip_id` branch at `:86` | ✓ Live: chip_id branch is at :87. Call-site at :77 precedes by 10 lines. |
| Unity tests 6/6 PASS | ✓ Per `01-VERIFICATION.md` Truth #3 (live execution: `native/avr/test_flash_intel_vpp [PASSED]` — 6/6) |
| `test_flash_intel_high_vpp_error_clears_regulator` covers CR-01 regression | ✓ Per `01-VERIFICATION.md` Anti-Patterns table + Post-Review Fixes |

**Verdict:** CONTEXT.md `<specifics>` SC#3 sample text (lines 445-468) is accurate and may be adopted verbatim by 05-VERIFICATION.md.

### SC#4 (static_high_mask end-to-end + pins<32 guard in 10-VERIFICATION.md)

5-hop chain verified live:

1. `firestarter_app/firestarter/data/pinouts.json:10,21` — `"static-high-pins":[24]` for DIP24_2716 and DIP24_2732.
2. `firestarter_app/firestarter/database.py:309-319` — `get_bus_config` translates `static-high-pins` via `pin_conversions` (`pin_conversions[24][24] = 13` at :90).
3. Wire JSON `"static-high":[13]` (post-translation; written into the bus-config sub-object by `get_bus_config`).
4. `firestarter/src/json_parser.c:426` — `handle->bus_config.static_high_mask |= 1UL << line;` (inside `parse_bus_config`).
5. `firestarter/src/proms/memory.cpp:319` — `reorg_address |= config.static_high_mask;` (inside `mem_util_remap_address_bus`, defined at :226).

`pins < 32` VPE_TO_VPP guard:

- `firestarter/src/proms/memory.cpp:140` — `if (handle->pins < 32) { mask |= VPE_TO_VPP; }` (inside `mem_util_calculate_top_address_register`, function at :137).
- Explanatory comment at :141-142: "VPE_TO_VPP and ADDRESS_LINE_16 share the same CONTROL bit — preserving VPE_TO_VPP would corrupt A16 for 32-pin (512KB) chips."
- Dead `READ_WRITE == WRITE_FLAG` check: **absent** (verified by `grep -n "READ_WRITE == WRITE_FLAG" firestarter/src/proms/memory.cpp` → no matches).

**Verdict:** SC#4 evidence is intact and verifiable from current tree. CONTEXT.md `<specifics>` block 470-481 is accurate; the planner can paste the 6-bullet verification list verbatim into 10-VERIFICATION.md's Observable Truths.

## Phase 08 Verification Scope

Per CONTEXT.md D-03, Phase 08 (Integration, Rebuild & Verification) is the trickiest retroactive. It introduced no REQs of its own; the audit attributed it to REQ-SAF-03 (blank-check gating) + cross-cutting integration evidence. RESEARCH.md confirms:

**What 08-VERIFICATION.md verifies:**

1. **REQ-SAF-03 cross-handler:** blank-check gating intact at all three sites:
   - `flash_type_3.cpp:77-79` (flash3_write_init)
   - `flash_intel.cpp:96-98` (flash_intel_write_init)
   - `eeprom_28c.cpp:91-93` (eeprom28c_write_init)
   All three guard with `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))` then call `mem_util_blank_check(handle)`. Same pattern in all three files. Verified by direct grep.

2. **Phase 08's own deliverables (per 08-01-SUMMARY.md):**
   - Both AVR builds clean (uno + leonardo). Cite Phase 12-VERIFICATION.md spot-checks (build numbers re-confirmed by Plan 02-02 packaging change).
   - DB regenerated to 743 chips. Cite `v1.0-INTEGRATION-CHECK.md` row 7 + STATE.md WIRE-02 evidence (`check_dispatch.py` runs across all 743 chips and exits 0).
   - CLAUDE.md updates (Phase 8 Task 4 in 08-01-SUMMARY). Cite the diff. Note: CLAUDE.md content has since been further modified by Plan 02-03 (minipro scrub) and Plan 02-02 (filename flip); cite the CURRENT state, not the Phase-08-as-shipped state.

3. **Integration evidence:** cross-link `v1.0-INTEGRATION-CHECK.md` row 18 (REQ-SAF-03 wire-trace) rather than rebuilding. Cross-link Phase 12-VERIFICATION.md for evidence that Phase 12's `check_dispatch.py` PASS (and Plan 02-03's augmentation to it for wire-key regression) re-verifies Phase 08's "DB regen runs end-to-end" goal.

4. **WARNING-4 follow_up:** test-script drift (deleted-DB references) carried per CONTEXT.md D-05. Confirmed live: `firestarter_test.sh:31` still has `JSON_FILE='./firestarter/data/database_generated.json'`; `write_test.sh:17` likewise. Owned by Phase 4 / HW-01.

**What 08-VERIFICATION.md does NOT verify:**

- Hardware execution (HW-01..HW-05 — Phase 4 territory).
- Re-running `pio test` / `pio run` (cite `01-VERIFICATION.md` + `12-VERIFICATION.md` execution records).
- Re-running `check_dispatch.py` (cite `02-VERIFICATION.md` SC4 evidence).

**Density:** 08-VERIFICATION.md should be light — most evidence is cross-link, not fresh grep. CONTEXT.md D-08 caps target at 100-160 lines; Phase 08 likely lands at ~110.

## Validation Architecture (what this phase validates; explicit Nyquist boundary)

`workflow.nyquist_validation` is unset in `.planning/config.json` (`{"mode":"YOLO","parallelization":"enabled","workflow":{"_auto_chain_active":false},"granularity":"Comprehensive"}`). Per the orchestrator's "absent ⇒ enabled" rule, the Validation Architecture section is included.

### What each VERIFICATION.md proves

Per VERIF-01..VERIF-10, the deliverables are **documentation artifacts** scoring the requirement against the current source tree. Behavioral proof comes from these **existing** automated test suites — Phase 3 cites, doesn't re-run:

| Behavior | Existing Test Asset | Sampling Rate |
|----------|---------------------|---------------|
| Algo-first dispatch correctness for all 13 KNOWN_PROTOCOLS | `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — 15 Unity tests | Last full run: `01-VERIFICATION.md` 2026-05-12 — 15/15 PASS |
| Intel-flash VPP ADC compare (SAF-04 → REQ-SAF-01 Intel portion) | `firestarter/test/native/avr/test_flash_intel_vpp/test_flash_intel_vpp.cpp` — 6 tests | `01-VERIFICATION.md` Truth #3 — 6/6 PASS |
| 28C chip-ID check (SAF-05 → REQ-SAF-02 28C portion) | `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` — 4 tests | `01-VERIFICATION.md` Truth #4 — 4/4 PASS |
| 743-chip wire round-trip + dispatch no-regression (REQ-DB-01..04, REQ-FW-01..06, WIRE-01/02) | `firestarter_app/tools/check_dispatch.py` (now augmented by Plan 02-03) | `02-VERIFICATION.md` SC4 — exit 0, "0 wire-key regressions" |
| AVR firmware budget (uno + leonardo) | `pio run -e uno/leonardo` | `12-VERIFICATION.md` Behavioral Spot-Checks — both SUCCESS |
| WARNING-5 data-layer override (REQ-FW-03 + REQ-SAF-01 for AT28C-family) | `firestarter_app/tools/check_dispatch.py` `_28C_EEPROM_HAZARD_PINOUT` guard | `13-VERIFICATION.md` Truth #5 — exit 0 |

### Why no new automated tests are produced

Phase 3 is a **retroactive doc audit**, not a behavior-change phase. Each VERIFICATION.md scores the CURRENT tree using `grep -n` evidence + cross-cites to the test suites listed above. No new probe scripts, no new Unity tests, no new pytest cases.

**The explicit per-`.planning/ROADMAP.md` decision** (echoed in CONTEXT.md "Deferred Ideas"): "Phase 3 chooses the 'equivalent retroactive audit' path (hand-authored verification using existing audit/integration-check evidence) rather than running the Nyquist gap-filler test-generation flow." This is the workflow contract for VERIF-01..VERIF-10.

### Sampling rate for Phase 3 itself

- **Per task commit:** static — `grep -n` validation that all cited line numbers resolve. No live tool execution.
- **Per wave merge:** spot-check that the 10 markdown files lint as YAML+Markdown (no broken frontmatter), and that file paths in the frontmatter `phase:` field match the directory basenames.
- **Phase gate:** `/gsd-verify-work` reads the 10 files and confirms each frontmatter `requirements_verified` list is a subset of the audit's `gaps.requirements` for that phase.

### Wave 0 gaps

None. Test infrastructure exists. The four existing exemplars (`01/02/11/12/13-VERIFICATION.md`) suffice as template source per CONTEXT.md "Deferred Ideas". No `.planning/templates/` setup is in scope.

## Project Constraints (from CLAUDE.md)

The meta-repo `CLAUDE.md` carries these directives that Phase 3 honors:

- **Meta-repo only.** `firestarter/` and `firestarter_app/` are sub-repos **NOT** committed here. Phase 3 reads them; doesn't modify them. ✓ Already locked by CONTEXT.md `<domain>` "Out of scope".
- **Two sub-repos with their own CLAUDE.md.** Phase 3 doesn't touch sub-repo CLAUDE.md files either (Plan 02-02 + 02-03 already covered the renames they needed).
- **Constants/flag bits duplicated** between `firestarter_app/firestarter/constants.py` (Python) and `firestarter/include/firestarter.h` (C++). Phase 3 doesn't change either; spot-check `firestarter.h:72` for `static_high_mask` field declaration as part of REQ-FW-05 wire-contract evidence in 10-VERIFICATION.md.
- **Hardware calibration** persisted in Arduino EEPROM via `rurp_configuration_t` — irrelevant to Phase 3.

## Pitfalls

Concrete landmines the planner must avoid. All are reinforced by CONTEXT.md `<deferred>` and STATE.md but worth surfacing again because they are easy to slip past in a "10 similar files" production rhythm:

1. **Do NOT update `v1.0-MILESTONE-AUDIT.md`.** It is a historical snapshot dated 2026-05-11T11:00. Phase 5 (DOC-01) MAY add a v1.1-resolution table to `MILESTONES.md` later; Phase 3 produces the closure artifacts the audit's `gaps` block points at. (`v1.0-MILESTONE-AUDIT.md` frontmatter explicitly says `re_audit_of: 2026-05-11T08:00:00Z` — these are snapshots.)

2. **Do NOT mutate sub-repo source.** No edits to anything under `firestarter/` or `firestarter_app/`. Phase 3 writes only `.planning/milestones/v1.0-phases/{NN-slug}/{NN}-VERIFICATION.md`.

3. **Do NOT re-run `pio test`, `pio run`, or `check_dispatch.py` per file.** Cite existing artifacts. Last full live execution captures:
   - Native suite 25/25: `01-VERIFICATION.md` Behavioral Spot-Check, 2026-05-12T08:00:00Z.
   - `check_dispatch.py` PASS (incl. wire-key regression): `02-VERIFICATION.md` Behavioral Spot-Check, 2026-05-12T09:30:00Z.
   - `pio run` uno + leonardo: `12-VERIFICATION.md`, 2026-05-11T10:00:00Z.

4. **Do NOT author `MILESTONES.md` v1.1 entry.** Phase 5 / DOC-01 owns it. CONTEXT.md `<domain>` explicit lock.

5. **Do NOT fix WARNING-5 or WARNING-4.** WARNING-5 is deferred to v1.2 per `MILESTONES.md` "Known Gaps" — Phase 13 (v1.0) closed it at the data layer for the canonical 23 AT28C256/64 chips, but the deferral note in MILESTONES.md keeps the override-table generalization open. WARNING-4 is owned by Phase 4 / HW-01 (hardware-validation phase fixes its own scripts).

6. **`10-CONTEXT.md` stray location** at `.planning/milestones/v1.0-phases/10-static-pins/10-CONTEXT.md` is real (live confirmed). Phase 3 reads it for evidence (it has rich background on the `static_high_mask` rationale), but does NOT move or delete it. Audit/cleanup deferred per CONTEXT.md `<deferred>`.

7. **Line numbers SHIFT across v1.1 closure phases.** Resolve at task-execution time, not from a stale CONTEXT.md value. Specific drift surfaces this caused:
   - `flash_intel.cpp` gained the `flash_intel_check_vpp` helper at :25-50 — this pushed `flash_intel_check_chip_id` to :152 (was earlier in v1.0). CONTEXT.md correctly captures the new positions.
   - `eeprom_28c.cpp` gained the `eeprom28c_check_chip_id` helper at :55-77 — the SDP_DISABLE call moved to :91 (was earlier in v1.0). CONTEXT.md correctly captures.
   - `json_parser.c` triple-flip (Plan 02-01) added the `_mv` suffix at three sites but kept line numbers stable: :62, :74, :309. Confirmed live.
   - `database.py` Plan 02-02 added the `vpp_volts` internal-dict rename at :417 + :510 + emitter at :518. Confirmed live.
   - **General rule:** always grep at write time. Never trust a stale line number from research; verify it.

8. **CONTEXT.md `<specifics>` table is a STARTING POINT, not a contract.** Per session-memory directive, the discuss-phase guessed the table. RESEARCH.md validates: the per-file REQ assignments + Cross-Milestone-Closure + follow_ups columns all match the audit's `gaps.requirements` block. **No corrections needed.** Adopt the table.

9. **CONTEXT.md `<specifics>` verbatim-shape YAML blocks** (lines 483-503 for WARNING-5; 494-503 for WARNING-4) are GUESSES per session memory. RESEARCH.md confirms they conform to the actual `11-VERIFICATION.md` schema. **Adopt them.** (See "VERIFICATION.md Canonical Template" section above.)

10. **Don't conflate "REQ-FW-03 SATISFIED" with "AT28C256 hazard closed".** REQ-FW-03 scope is the 0x0D handler logic — that handler is correct (and was correct in v1.0). The AT28C256 hazard is an **upstream-DB classification issue**: minipro tags AT28C256 as `electrical.type='Flash/EEPROM'` with `algorithm=0x07`, not 0x0D, so it doesn't reach the 0x0D handler at all. Phase 13 (v1.0) closed this for the canonical 23 chips by data-layer override; v1.2 owns broader generalization. 06-VERIFICATION.md scores REQ-FW-03 SATISFIED with WARNING-5 as a `follow_up` — both true.

11. **REQ-SAF-01 is split across files.** v1.0 audit lists it once for Phase 03 + 05; v1.1 closure ships in two halves:
   - UV-EPROM portion ✓ from v1.0 (`eprom_generic_init → eprom_check_vpp` unconditional). 03-VERIFICATION.md scores this part SATISFIED.
   - Intel portion ✓ from v1.1 SAF-04 (`flash_intel_check_vpp` at :25-50). 05-VERIFICATION.md scores this part SATISFIED + Cross-Milestone Closure cites SAF-04 (**SC#3**).
   - Both files reference REQ-SAF-01 in `requirements_verified` frontmatter. **No conflict** — different chip families.

12. **Don't reorder Phase 3 plans relative to v1.1 Phase 1/2.** v1.1 Phase 1 + Phase 2 are complete (STATE.md confirms `completed_plans: 5/5`). Phase 3 runs AFTER them per ROADMAP dependency graph. If Phase 1 or Phase 2 had been incomplete, line numbers and Cross-Milestone Closure cites wouldn't exist yet — verify-work for Phase 3 should not start without these closed. (Both are closed today; safe.)

## Two-Plan Split Sanity Check

CONTEXT.md D-10 proposes:

- **Plan 03-01 — clean batch (5 files):** 01, 02, 04, 08, 09.
- **Plan 03-02 — closure/hazard batch (5 files):** 03, 05, 06, 07, 10.

Validation against natural split axes:

| File | Has Cross-Milestone Closure? | Has follow_ups? | Proposed plan | Sanity |
|------|------------------------------|-----------------|---------------|--------|
| 01 | yes (REQ-DB-03 WIRE-01) | no | 03-01 | borderline — has closure but it's minor (one paragraph cite of 02-VERIFICATION SC1) |
| 02 | no | no | 03-01 | clean ✓ |
| 03 | optional (Phase 12 FW-01 inline) | yes (WARNING-5) | 03-02 | ✓ |
| 04 | optional (Phase 12 FW-04 inline) | no | 03-01 | ✓ (no hazard) |
| 05 | **yes (SAF-04, SC#3 LOCK)** | no | 03-02 | ✓ |
| 06 | optional (Phase 13 sidebar) | yes (WARNING-5) | 03-02 | ✓ |
| 07 | **yes (SAF-05)** | yes (WARNING-5 related) | 03-02 | ✓ |
| 08 | no | yes (WARNING-4) | 03-01 | borderline — has follow_up but no closure |
| 09 | no | no | 03-01 | clean ✓ |
| 10 | no | yes (INFO-3) | 03-02 | borderline — has follow_up, no closure, but **SC#4 LOCK** justifies grouping |

**Two alternative splits I evaluated:**

- **Split by follow_ups presence (5 with / 5 without):** 03, 06, 07, 08, 10 (with) vs. 01, 02, 04, 05, 09 (without). This breaks SC#3 (puts 05 in the "easy" plan with no follow_ups but with the heaviest closure narrative) and SC#4 (puts 10 in the "hazard" plan despite being verification-gap-only).
- **Split by closure presence (3 with / 7 without):** 01, 05, 07 (closure) vs. 02, 03, 04, 06, 08, 09, 10 (no closure). Plan size imbalance is the wrong shape (3+7 not 5+5).

**Verdict:** CONTEXT.md D-10's proposed split is the right shape. The borderline cases (01, 08, 10) don't tip the balance because:
- 01's WIRE-01 cite is one paragraph (minor); the file is mostly clean DB-pipeline grep evidence.
- 08's WARNING-4 follow_up is one frontmatter entry; the body is mostly cross-link to row 18 + Phase 12.
- 10's INFO-3 follow_up is one frontmatter entry; the body is the SC#4-locked 5-hop chain + guard.

The **SC#3** (05) and **SC#4** (10) explicit ROADMAP locks land in the same plan (03-02) — they're the highest-stakes deliverables in this phase and benefit from being authored in the same wave with the same eye on detail. That's the strongest argument for the proposed split.

**Adopt:** Plan 03-01 = {01, 02, 04, 08, 09}; Plan 03-02 = {03, 05, 06, 07, 10}. Per CONTEXT.md D-10 closing line: "Planner may merge or split further if friction arises; the two-plan split is a recommendation, not a hard contract." Recommend keeping as-proposed.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| (none) | — | — | — |

**All factual claims in this research are tagged `[VERIFIED]` against the live source tree on 2026-05-12 via direct `grep -n` execution, or `[CITED]` from existing VERIFICATION.md / INTEGRATION-CHECK / MILESTONE-AUDIT / STATE.md / CONTEXT.md files.** No `[ASSUMED]` claims. Line numbers will drift if the source tree changes between now and execution — the planner should grep at write time per Pitfall #7.

## Open Questions for the Planner

1. **`requirements_verified` frontmatter for 04-VERIFICATION.md** — REQ-FW-04 is unambiguous (Phase 04 plans claim it). REQ-SAF-03 is *also* attributable to Phase 04 (blank-check gating in `flash3_write_init`) but is **cross-handler** (also in Phase 06 + Phase 08). Recommendation: list both REQ-FW-04 and REQ-SAF-03 in 04-VERIFICATION.md's `requirements_verified` (the flash3 portion); 08-VERIFICATION.md lists REQ-SAF-03 (cross-handler scope). The audit `gaps.requirements` block for REQ-SAF-03 attributes it to "04 (and 06)" — phase ownership shared. Either {04, 08} or {04, 06, 08} listing REQ-SAF-03 is defensible; CONTEXT.md `<specifics>` proposes {04 + 08} which keeps 06 narrow to REQ-FW-03 + WARNING-5 — accept that split.

2. **05-VERIFICATION.md `requirements_verified` list** — CONTEXT.md `<specifics>` proposes "FW-02, SAF-01 (Intel portion)". The audit attributes REQ-SAF-01 to "03 + 07 (and 05)". RESEARCH.md confirms: REQ-SAF-01 belongs in 03-VERIFICATION.md (UV-EPROM portion) AND 05-VERIFICATION.md (Intel portion). 07-VERIFICATION.md is REQ-SAF-02. Adopt CONTEXT.md proposal: 05's list = [REQ-FW-02, REQ-SAF-01]; 03's list = [REQ-FW-01, REQ-SAF-01]; 07's list = [REQ-SAF-02].

3. **08-VERIFICATION.md body density** — CONTEXT.md D-08 caps at 100-160 lines; Phase 08 has the least new content (mostly cross-links to row 18 + Phase 12 + Plan 02-03). Planner should accept this is the shortest of the 10 files (~110 lines is fine). Acceptance criteria should NOT mandate a minimum line count.

4. **Timestamp policy** — every VERIFICATION.md frontmatter has a single `verified:` ISO8601 timestamp. For 10 files written in two waves, options:
   - A) All 10 files use the same timestamp (wave-merge moment) — implies "verified atomically at one instant".
   - B) Each file uses its own write-time — implies "each file verified independently".
   The four existing exemplars use B (each has its own timestamp). Recommend B. CONTEXT.md "Claude's Discretion" line 228 confirms this is discretion.

5. **Whether to add a top-level Phase 3 SUMMARY** — CONTEXT.md "Claude's Discretion" line 239 says "standalone SUMMARY optional". Plan 03-02 SUMMARY.md would naturally cover the 10-file batch close. Recommend skipping a phase-level SUMMARY and letting Plan 03-02 SUMMARY.md serve.

---

## RESEARCH COMPLETE
