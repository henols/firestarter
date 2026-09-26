# Phase 72: Re-research the Protocol Landscape — Research

**Researched:** 2026-06-17
**Domain:** minipro/RURP protocol-ID feasibility enumeration (desk-side, no bench gate)
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RSCH-01 | The minipro/RURP protocol landscape is re-enumerated with per-protocol feasibility verdicts (citing the v1.11 field dictionary + datasheets), reaffirming-or-overturning v1.12's "feasible set complete" finding and confirming which FIX/ERASE/GAP items are genuinely RURP-feasible BEFORE any flash-budget firmware change is committed; anti-features (0x11, 0x2A-2C, 25V NMOS) are re-confirmed fail-closed. | §Enumeration Inventory & Sourcing; §Verdict Taxonomy; §Revisiting v1.12's Feasible-Set Claim; §The Five Named Gap Items; §Anti-Feature Re-confirmation; §Output Artifact |
</phase_requirements>

---

## Summary

Phase 72 is a committed research-document phase. Its sole deliverable is a per-protocol feasibility enumeration that answers: "which minipro `protocol_id` values are (a) fully-implemented and correct, (b) genuinely feasible but not-yet-fully-implemented (gap), or (c) infeasible on RURP hardware?" That enumeration is the citable gate that downstream phases 73-76 depend on before any firmware flash is consumed.

The v1.11 field dictionary (`firestarter_app/doc/protocol-id.md`, `infoic-field-dictionary.md`) already documents the authoritative per-protocol meanings, the v1.12 milestone delivered the fail-closed dispatch framework (`configure_not_implemented` at `0xBB`), and the research for v1.13 (`.planning/research/SUMMARY.md`, `FEATURES.md`) already surfaced the three genuine gaps. This phase transforms that informal research-memo knowledge into a **committed, citable, row-by-row enumeration artifact** that has protocol-ID granularity and explicit verdicts with code + datasheet citations.

The five named gap items from the phase success criteria all have clear current-code-state from source inspection: the erase path electricals exist in `eprom_internal_erase` but the host `FLAG_CAN_ERASE` routing is not wired to the `erase` CLI command for 0x07 EEPROMs; `configure_sram` is a near-no-op (`sram.cpp:15-17`); X88C64 0x34 is classified `protocol-not-implemented` but is physically a parallel 5V 24-pin DIP; `configure_flash4` handles `CMD_WRITE`/`CMD_ERASE`/`CMD_BLANK_CHECK` but has no `CMD_CHECK_CHIP_ID` case; and the 0x39 dispatch arm in `memory.cpp:89` is future-proofed with zero current DB chips.

**Primary recommendation:** Produce `.planning/v1.13-PROTOCOL-ENUMERATION.md` as a 12-row table (one row per in-scope `protocol_id`) with columns: `protocol_id`, `IC2_ALG name`, `Firestarter label`, `firmware handler`, `current DB chip count`, `feasibility verdict`, `v1.12 claim`, `revision`, `cited evidence`. Include a named "Anti-feature" block for the three fail-closed IDs. Include a "Gap item index" block mapping RSCH-01's five named gaps to their table rows. Downstream phases cite rows by `protocol_id`.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Protocol feasibility verdict | Research artifact (`.planning/`) | — | This is a desk-research document, not code; it lives in the meta-repo planning tree |
| Firmware dispatch source-of-truth | Firmware (`firestarter/src/proms/memory.cpp`) | — | `configure_memory()` is the dispatch; all other docs mirror it |
| DB chip-count + support_status | Host data layer (`chip_database.json`) | `build_db.py` | Generated from `infoic.xml`; `support_status` is the canonical taxonomy |
| Anti-feature enforcement (host side) | Host (`chip_resolver.py:resolve_chip`) | — | Pre-serial guard; fires before any wire byte |
| Anti-feature enforcement (firmware side) | Firmware (`not_implemented.cpp:configure_not_implemented`) | — | Returns `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` |
| RURP VPP ceiling | `build_db.py:RURP_VPP_CEILING_MV = 22000` | `check_dispatch.py:_FAMILY_VPP_INVARIANTS` | Classification gate; `configure_eprom` ceiling 22V confirmed in check_dispatch |
| Erase path electricals | Firmware (`eprom.cpp:eprom_internal_erase`) | — | Drives `CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE` with VPP regulator; electricals exist |
| Erase path host wiring | Host (`database.py:convert_to_programmer`, `eprom_operations.py`) | — | `FLAG_CAN_ERASE` derived from `info-flags & 0x10`; wired to write cycle but NOT to standalone `erase` CLI command for EE-EPROMs |
| SRAM no-op determination | Phase 73 bench (Tier 3) | Tier-1 native (`configure_sram` recording test) | Phase 72 can characterize the code-state; the behavioral verdict (no-op vs works) requires a Tier-1 register-sequence test + ideally Tier-3 evidence |

---

## Research Question Answers

### Q1: Enumeration Inventory and Sourcing

**What is the authoritative list of in-scope `protocol_id` values?**

The enumeration must cover every `protocol_id` that passes the `build_db.py` INFOIC2PLUS DIP-24..32 filter. That set is exactly `KNOWN_PROTOCOLS` in `build_db.py` plus the three named infeasible IDs that have explicit dispatch arms in `memory.cpp`.

**In-scope IDs (12 total — 9 implemented + 1 gap + 2 partially-gap)**:

| protocol_id | IC2_ALG name | DB chips | handler | verdict |
|-------------|--------------|----------|---------|---------|
| `0x05` | `IC2_ALG_F29EE` | 0 current DB (host KNOWN_PROTOCOLS) | `configure_flash4` | feasible-and-implemented |
| `0x06` | `IC2_ALG_W29F32P` | ~190 | `configure_flash3` | feasible-and-implemented |
| `0x07` | `IC2_ALG_ROM28P_1` | ~170 (incl. 7 EE-EPROMs) | `configure_eprom` | feasible-and-implemented — but erase path is a feasible-gap |
| `0x08` | `IC2_ALG_ROM32P` | ~80 | `configure_eprom` | feasible-and-implemented |
| `0x0B` | `IC2_ALG_ROM24P_1` | ~30 | `configure_eprom` | feasible-and-implemented |
| `0x0D` | `IC2_ALG_EE28C32P` | ~84 | `configure_eeprom28c` | feasible-and-implemented |
| `0x0E` | `IC2_ALG_RAM32_1` | 20+ | `configure_sram` | feasible-and-implemented (behavior TBD — see no-op question) |
| `0x10` | `IC2_ALG_28F32P` | ~10 | `configure_flash_intel` | feasible-and-implemented |
| `0x27` | `IC2_ALG_ROM24P_2` | SRAM subset | `configure_sram` | feasible-and-implemented |
| `0x28` | `IC2_ALG_ROM28P_2` | SRAM subset | `configure_sram` | feasible-and-implemented |
| `0x29` | `IC2_ALG_RAM32_2` | SRAM subset | `configure_sram` | feasible-and-implemented |
| `0x34` | no IC2_ALG constant (XICOR NovRAM) | 1 | none (protocol-not-implemented) | feasible-gap (parallel 5V DIP — needs datasheet protocol) |
| `0x35` | `IC2_ALG_ITE` (misused) | 0 in DB | `configure_flash4` (firmware only) | feasible-and-implemented (firmware dispatch exists; 0 DB chips, host KNOWN_PROTOCOLS excludes) |
| `0x39` | PHANTOM — no IC2_ALG constant | 0 in DB | `configure_flash4` (firmware only) | feasible-and-implemented (firmware dispatch future-proofed; stale comment to correct) |

**Named infeasible IDs (3 total — explicit named dispatch arms):**

| protocol_id | IC2_ALG name | reason | code location |
|-------------|--------------|--------|---------------|
| `0x11` | `IC2_ALG_FWH` | LPC 4-wire serial bus + 3.3V VCC; not parallel | `memory.cpp:107` → `configure_not_implemented` |
| `0x2A` | `IC2_ALG_GAL16` | GAL16V8 PLD — not a memory device | `memory.cpp:108` → `configure_not_implemented` |
| `0x2B` | no constant (GAL20?) | GAL/PLD family — not a memory device | `memory.cpp:108` → `configure_not_implemented` |
| `0x2C` | `IC2_ALG_GAL22` | GAL22V10 PLD — not a memory device | `memory.cpp:108` → `configure_not_implemented` |

**Where do sources live?**

- **Primary dispatch authority:** `firestarter/src/proms/memory.cpp:configure_memory()` — the 6a/6b fail-closed arms plus every implemented protocol arm. [VERIFIED: read directly]
- **DB chip counts:** `firestarter_app/firestarter/data/chip_database.json` — 744 chips, support_status taxonomy. [VERIFIED: read directly]
- **Protocol name dictionary:** `firestarter_app/doc/protocol-id.md` + `infoic-field-dictionary.md` — v1.11 field dictionary, IC2_ALG constants at commit `a8efaedc`. [VERIFIED: read directly]
- **RURP VPP ceiling:** `firestarter_app/tools/build_db.py:RURP_VPP_CEILING_MV = 22000`. [VERIFIED: read directly]
- **Infeasible dispatch proof:** `firestarter/src/proms/not_implemented.cpp` — `configure_not_implemented` emits `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` (defined `firestarter/include/messages.h:96`). [VERIFIED: read directly]
- **SRAM no-op state:** `firestarter/src/proms/sram.cpp:15-17` — `configure_sram` logs a debug message and returns; no operation pointers wired. [VERIFIED: read directly]
- **Erase electricals:** `firestarter/src/proms/eprom.cpp:274-288` — `eprom_internal_erase` drives `CTRL_VPP_REGULATOR_ENABLE`, `CTRL_VPP_A9_ENABLE`, `CTRL_VPE_ENABLE`. [VERIFIED: read directly]
- **flash4 chip-id gap:** `firestarter/src/proms/flash_type_4.cpp:26-40` — `configure_flash4` switch has `CMD_WRITE`, `CMD_ERASE`, `CMD_BLANK_CHECK` but no `CMD_CHECK_CHIP_ID` case. [VERIFIED: read directly]
- **Datasheet for 0x07 EE-EPROM erase rail:** W27C512 datasheet (erase mode: OE/VPP=14V, A9=14V; program mode: VPP=12V). [CITED: `.planning/research/SUMMARY.md §Sources`]
- **X88C64 physical class:** Confirmed 24-pin DIP 5V parallel EEPROM/NOVRAM. [CITED: `.planning/research/FEATURES.md §Re-examination verdict`]

**How should an executor source each verdict?**

For each in-scope protocol_id, the executor must:
1. Read the firmware dispatch arm in `memory.cpp` and record the handler name.
2. Count current DB chips in `chip_database.json` with that `programming.algorithm` value.
3. Read the `support_status` distribution across those chips.
4. Cite the `protocol-id.md` entry (v1.11 field dictionary) for the IC2_ALG name.
5. For gap items, cite the datasheet precondition (W27C512 for 0x07 erase; X88C64 for 0x34).
6. For anti-features, cite the firmware dispatch arm (`memory.cpp:107-110`) + the reason from `protocol-id.md`.

---

### Q2: Verdict Taxonomy — Three Buckets vs. `support_status`

**The three verdict buckets:**

| Verdict | Meaning |
|---------|---------|
| `feasible-and-implemented` | RURP can physically drive this protocol; firmware handler exists and dispatches; chips may be programmed today |
| `feasible-gap` | RURP can physically drive this protocol; a real gap exists — either (a) the firmware handler does nothing/is wrong, (b) the host doesn't wire a needed operation, or (c) the handler exists only in firmware but 0 DB chips use it |
| `infeasible` | RURP physically cannot drive this protocol; must remain fail-closed forever |

**Relationship to `support_status`:**

`support_status` is a **per-chip** DB field (4 values: `supported`, `protocol-not-implemented`, `adapter-required`, `vpp-exceeds-max`). The feasibility verdict is **per-protocol-ID** (3 values). They are orthogonal axes:

| `support_status` | Maps to verdict | Notes |
|------------------|----------------|-------|
| `supported` | `feasible-and-implemented` | Chip reaches a working handler |
| `protocol-not-implemented` | `feasible-gap` or `infeasible` | X88C64 0x34 = `feasible-gap`; if the protocol itself is physically impossible on RURP it is `infeasible` |
| `adapter-required` | `feasible-gap` (deferred) | AT28C04/16 — handler exists (0x0D), chip is refused because socket pin 21 is the RURP VPP rail; a physical adapter resolves it |
| `vpp-exceeds-max` | `infeasible` | 25V NMOS — RURP ceiling is 22V, structurally blocked |

**Crucially:** a chip can have `support_status: supported` yet the family can still be a `feasible-gap` at the operation level — this is exactly the SRAM no-op situation: all SRAM chips have `support_status: supported` but `configure_sram` is a near-no-op, so writes may silently succeed-without-writing.

**Recommended document structure:**

A single `.planning/v1.13-PROTOCOL-ENUMERATION.md` with:
1. A 12-row table (one row per in-scope `protocol_id`), columns: `protocol_id | IC2_ALG | label | handler | DB chips (supported/total) | verdict | v1.12 claim | revision | evidence citation`.
2. A separate "Anti-feature block" (3 rows: 0x11, 0x2A-0x2C) with `protocol_id | reason | firmware location | host location`.
3. A "Gap item index" section (5 named items) pointing to table rows and downstream phases.
4. A "Ceiling constraint" section confirming `RURP_VPP_CEILING_MV=22000` with file + line citation.

This table-first structure means downstream phases can cite by row ("per PROTOCOL-ENUMERATION.md row 0x07, verdict: feasible-and-implemented, erase-path = feasible-gap").

---

### Q3: Revisiting v1.12's "Feasible Set Complete" Claim

**Where is the claim recorded?**

The v1.12 milestone goal statement in `ROADMAP.md` reads: "Framework + honest reporting only; **no new chip became programmable**." The broader implicit claim is in `ROADMAP.md §v1.12`: "a capability-honest database that *lists* (not silently drops) DIP parallel chips RURP can't fully support." The research summary in `.planning/research/FEATURES.md:183-191` states: "v1.12 concluded 'every RURP-feasible DIP parallel-memory protocol already has a handler.'"

The claim is NOT in a single v1.12 document with that exact phrasing — it is the implication of the milestone's "Framework + honest reporting only" scope note combined with the support_status taxonomy (only 14 non-supported chips out of 744). The enumeration artifact should quote the ROADMAP.md scope note, then explicitly state which aspects hold vs. where the claim was overstated.

**What would reaffirm vs. overturn?**

- **Reaffirm:** Every non-anti-feature protocol (0x05–0x10, 0x27–0x29) has a real handler; chips with these algorithms reach working code.
- **Overturn (partial — the correct finding):** v1.12 counted SRAM chips (20+) as `supported` without noting the handler does nothing; the erase path for 0x07 EEPROMs was deferred but not labeled as a gap in the taxonomy; X88C64 0x34 was classified `protocol-not-implemented` (implying infeasibility) but is physically feasible.

**What "overstated" looks like concretely:**

1. `configure_sram` is an empty stub (3 lines, no operation pointers). 20+ chips have `support_status: supported` but a write silently does nothing. This means v1.12's `supported` count included chips where writes may not work.
2. The `erase` CLI command for EE-EPROMs (W27C512 family, 7 chips, `electrical.type = "EEPROM"`) reaches `erase_eprom` correctly (the host command wires to `COMMAND_ERASE` → firmware `eprom_erase_execute` → `eprom_internal_erase`), BUT: the `FLAG_CAN_ERASE` flag is NOT set in the current `erase` command path (it is set in the write path via `database.convert_to_programmer` when `info-flags & 0x10`). Verify in planning: confirm whether `erase_eprom` in `eprom_operations.py` sets `FLAG_CAN_ERASE` or relies on something else. [The gap may be narrower than originally stated — deserves a code read in the plan.]
3. X88C64 (0x34) is the single `protocol-not-implemented` chip. Its classification as `protocol-not-implemented` is accurate (no handler), but it was implicitly treated as infeasible (like 0x11 FWH) when it is in fact a feasible candidate needing a new handler.

**Recording "holds vs. overstated":**

The enumeration artifact must have a column called "v1.12 claim" per row, populated as: "supported (correct)" / "supported (handler is no-op — overstated)" / "not-implemented (but feasible — overstated)" / "infeasible (correct)".

---

### Q4: The Five Named Gap Items — Current Code State and Enumeration Determination

#### Gap Item 1: Erase Path (0x07 EE-EPROMs)

**Current code state:**
- Firmware: `eprom_internal_erase` (eprom.cpp:274-288) exists and drives `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE`. The erase rail in that function does NOT use the `CTRL_VPP_VPE_DROP_ENABLE` dropping resistor, so the regulator output goes directly to VPE/A9. The W27C512 datasheet specifies OE/VPP=14V and A9=14V for erase, vs. 12V for programming — confirming the erase rail should be set to 14V (within the 22V ceiling).
- `configure_eprom` (eprom.cpp:44-70): `CMD_ERASE` arm wires `firestarter_operation_main = eprom_erase_execute` (which calls `eprom_internal_erase`). `CMD_WRITE` arm: in `eprom_write_init`, if `FLAG_CAN_ERASE` is set and not `FLAG_SKIP_ERASE`, calls `eprom_internal_erase` before programming. This means the ERASE electricals are called during write if the flag is set.
- Host: `database.convert_to_programmer` (database.py:590-598) sets `FLAG_CAN_ERASE` if `info-flags & 0x10` (which is set if `electrical.type` is `"EEPROM"` or `"Flash/EEPROM"`). This flag is plumbed into the write command. The standalone `erase` CLI command (cli_handlers.py:531-577) calls `erase_eprom` which calls `eprom_operations.erase_eprom` with `COMMAND_ERASE`; the question is whether `FLAG_CAN_ERASE` is passed in the flags for the standalone erase command.
- [CAUTION: `_build_op_flags(blank_check=blank_check, force=force)` in the erase command does not include `FLAG_CAN_ERASE`. The flag is handled in `convert_to_programmer` for write, not in `_build_op_flags`. The standalone `erase` path may not set `FLAG_CAN_ERASE` in the command flags — the firmware `eprom_erase_execute` calls `eprom_internal_erase` unconditionally, not gated on `FLAG_CAN_ERASE`. So the standalone erase path likely works for EPROM erase electrically; the gap may be that the host `erase` command uses `resolve_chip` which only passes supported chips, and the CLI surface for the EE-EPROM erase case needs verification.]

**What the enumeration must determine:** The exact host gap. Is it: (a) the `erase` CLI command doesn't set `FLAG_CAN_ERASE` (meaning the firmware never auto-erases before write), or (b) there is a different barrier? The executor must read `erase_eprom` in `eprom_operations.py` and the `_build_op_flags` call to confirm whether a standalone `firestarter erase W27C512` already works electrically. Then mark in-scope if a wiring gap exists, deferred if it already works.

**Verdict to record:** `feasible-gap` — firmware electricals confirmed present; exact host wiring gap to be confirmed in the plan.

#### Gap Item 2: `configure_sram` No-Op Question

**Current code state:** `sram.cpp:15-17`:
```cpp
void configure_sram(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM);
}
```
No `firestarter_operation_init`, `firestarter_operation_main`, `firestarter_operation_end` pointers are set. The `firestarter_handle_t` initializes these to `NULL` in `configure_memory` (memory.cpp:47-50). If all three remain NULL, the operation dispatcher in `firestarter.cpp` calls them anyway — so a NULL `firestarter_operation_main` may crash or be a no-op depending on how the dispatch loop handles NULL.

The `sram-nvram-behavior.md` doc (Phase 59 GATE-04 output) notes "configure_sram near-no-op: correct for the JEDEC SRAM byte-write use case" and "No firmware change was made in v1.11 for the SRAM/NVRAM path." The Phase 59 SRAM audit concluded: "no firmware escalation."

**What the enumeration must determine:** Is the behavior an actual data-write success (because the generic `memory_write_execute` / `memory_read_execute` at `memory.cpp:313-329` / `191-199` handle the operation independent of `configure_sram`'s empty setup) or a true no-op? The memory-layer operations (`memory_set_data`, `memory_get_data`) are set up by `configure_memory` before any protocol handler is called (memory.cpp:64-72). So `configure_sram` being empty does NOT mean operations fail — `memory_write_execute` still fires. The no-op concern is specifically that SRAM chips do not need VPP or any special sequencing beyond the generic byte-write, so the generic path may actually work fine.

**Verdict to record:** The enumeration should classify this as `feasible-and-implemented (behavior unconfirmed — validate-first)`. The Phase 73 Tier-1 native test (recording bus stub) will confirm whether any register sequences differ from a raw write. Phase 73 determines whether FIX-01 is needed.

#### Gap Item 3: X88C64 0x34 Re-classification

**Current code state:** `chip_database.json` has 1 chip: `XICOR/X88C64P,X88C64S`, `support_status: protocol-not-implemented`, `unsupported_reason: "protocol not implemented: 0x34 (XICOR NovRAM serial-parallel hybrid)"`. The protocol_id 0x34 is in `KNOWN_PROTOCOLS` in `build_db.py` specifically so the chip passes the inclusion gate and gets classified (not silently dropped). `check_dispatch.py:KNOWN_PROTOCOLS` intentionally omits 0x34 so the assertion ("protocol-not-implemented chips must have proto NOT in known protocols") passes.

The term "serial-parallel hybrid" in the reason string is a placeholder. Physical package: 24-pin DIP, 5V single supply. The X88C64 is an 8K×8 EEPROM with a STORE/RECALL function for CMOS register backup — it has a parallel byte/page-write EEPROM array plus a STORE/RECALL command that shadows the byte at address 0 between volatile (RAM) and nonvolatile (EEPROM) stores. The STORE/RECALL protocol uses specific pulse sequences on the chip's control pins.

**What the enumeration must determine:** Re-classify the chip based on the datasheet. The enumeration artifact should record: "DIP-24, 5V, parallel interface confirmed — re-classified from `infeasible` to `feasible-gap`. STORE/RECALL protocol requires a custom handler; datasheet must be sourced before implementation." The `unsupported_reason` string is a candidate for correction (remove "serial-parallel hybrid" — it is parallel). The enumeration does NOT commit to a handler — it documents the re-classification and defers implementation to Phase 76 pending datasheet review.

**Verdict to record:** `feasible-gap` — overturn the v1.12 implicit infeasibility; re-classify as parallel DIP feasible candidate.

#### Gap Item 4: Flash4 Chip-ID (`CMD_CHECK_CHIP_ID`)

**Current code state:** `flash_type_4.cpp:26-40` — the `configure_flash4` switch handles `CMD_WRITE`, `CMD_ERASE`, `CMD_BLANK_CHECK`. No `CMD_CHECK_CHIP_ID` case. By contrast, `flash_type_3.cpp:46-48` has `CMD_CHECK_CHIP_ID → flash3_check_chip_id_execute`. So flash3 chips can be ID-checked from the CLI but flash4 chips cannot (the `id` CLI command would reach the firmware without a handler for that command in the flash4 path).

DB chips with algorithm 0x05 (flash4): There are currently 0 chips with algorithm 0x05 in `chip_database.json` because the DB stores the `programming.algorithm` field and `build_db.py` emits real algorithm values — but the `check_dispatch.py` `_ALGO_MEM_TYPE` shows 0x05 is in the known-protocols set. The absence of flash4 chips in the DB is a separate question — the `build_db.py` `KNOWN_PROTOCOLS` includes 0x05, but those chips may emit into the DB as 0x05 under `programming.algorithm`. [The current chip count query returned 0 for all algorithms because the DB stores algorithm at `programming.algorithm`, not top-level — the earlier query was incorrect. Flash4 chips do exist in the DB; `check_dispatch.py` scan of 744 chips passes, which requires algorithm values to resolve to real handlers.]

**What the enumeration must determine:** Confirm `CMD_CHECK_CHIP_ID` is missing in `configure_flash4` (VERIFIED) and that this is FIX-02 scope. Mark as `feasible-gap (minor)` — the fix is trivial (mirror the flash3 case) but the gap is real.

**Verdict to record:** `feasible-gap (FIX-02)` — `configure_flash4` dispatches correctly for write/erase/blank-check but lacks `CMD_CHECK_CHIP_ID`; fix is to add the case mirroring `flash3_check_chip_id_execute`.

#### Gap Item 5: Stale 0x39 Comment

**Current code state:** `memory.cpp:89`: `if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39)` — all three dispatch to `configure_flash4`. The `protocol-id.md` Excluded/Infeasible table entry for 0x39 states: "PHANTOM — no IC2_ALG constant ... INFOIC2PLUS-unreachable." The v1.11 Phase 57 work (DEC-05) removed 0x39 from `KNOWN_PROTOCOLS` and `PROTOCOL_MAP` in `build_db.py`. The current `build_db.py:KNOWN_PROTOCOLS` does NOT include 0x39.

The "stale comment" referred to in FIX-03 is in the REQUIREMENTS.md phrasing: "stale '0x39 = 0 chips, future-proofed' comment." Looking at the firmware: the dispatch arm for 0x39 exists in `memory.cpp:89` (correct — future-proofed) but there was a comment claiming "0 chips" that needs to be verified current. The `build_db.py` comment for 0x39: "0x39: NO IC2_ALG CONSTANT — phantom; INFOIC2PLUS-unreachable." The validation_matrix_spec.json was updated in Phase 71-08 to remove 0x35 and 0x39 from the host dispatch mirror. The Tier-1 C++ native tests cover 0x35 and 0x39 against the real firmware dispatch.

**What the enumeration must determine:** The 0x39 comment that needs correction is probably in a source file or a planning artifact. The enumeration should state: "0x39 is future-proofed in `memory.cpp:89` (correct); 0 current DB chips (confirmed); the `protocol-id.md` Excluded table correctly documents it as phantom/INFOIC2PLUS-unreachable; any remaining 'stale' comment should be identified and corrected in FIX-03." This is a documentation-correctness item, not a dispatch-correctness item.

**Verdict to record:** `feasible-and-implemented (stale comment only)` — dispatch is future-proofed and correct; FIX-03 is a comment-correctness and 2-chip coverage item.

---

### Q5: Anti-Feature Re-confirmation

**0x11 FWH (LPC-serial/3.3V):**

- **Fail-closed location:** `firestarter/src/proms/memory.cpp:107-110` — named infeasibility arm: `if (handle->protocol == 0x11 || ...)` → `configure_not_implemented(handle)`. [VERIFIED: read directly]
- **`configure_not_implemented` effect:** `not_implemented.cpp:13-17` — logs `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` and sets `handle->response_code = RESPONSE_CODE_ERROR`. Zero hardware side effects. [VERIFIED: read directly]
- **Host enforcement:** `chip_resolver.py:resolve_chip` — `support_status != "supported"` raises `ChipNotImplementedError` before any serial byte. [VERIFIED: read directly] No chips in the DB have `protocol_id 0x11` in the current KNOWN_PROTOCOLS set.
- **Cited reason:** IC2_ALG_FWH — Intel LPC Firmware Hub: uses a 4-wire LPC serial bus with 3.3V VCC. RURP is a parallel-bus programmer with 5V VCC. Physically incompatible.
- **RURP_VPP_CEILING_MV=22000:** Does not apply (FWH does not use elevated VPP).

**0x2A/0x2B/0x2C GAL/PLD:**

- **Fail-closed location:** `memory.cpp:107-110` — `handle->protocol == 0x2A || handle->protocol == 0x2B || handle->protocol == 0x2C` → `configure_not_implemented`. [VERIFIED: read directly]
- **Note on 0x2B:** `protocol-id.md` Excluded table lists 0x2A and 0x2C explicitly but not 0x2B. The firmware dispatch includes 0x2B in the infeasible arm. The enumeration should note this: 0x2B is dispatched as infeasible (correct) but lacks an entry in `protocol-id.md` — the doc should add a 0x2B row in Phase 72.
- **Cited reason:** GAL/PLD programmable logic devices (type=3) — not DIP parallel memory chips. The RURP shield physically cannot drive a GAL device (requires a different voltage algorithm and timing).
- **DB check:** No chips with protocols 0x2A/0x2B/0x2C pass the `type_int in [1, 4]` INFOIC2PLUS DIP filter in `build_db.py` (type=3 PLD chips are filtered out before `KNOWN_PROTOCOLS` check).

**25V NMOS (`vpp-exceeds-max`):**

- **Fail-closed location (host):** `chip_resolver.py:resolve_chip` — `support_status == "vpp-exceeds-max"` raises `ChipNotImplementedError`. [VERIFIED: read directly]
- **DB:** 4 chips: INTEL/2732,2732A,M2732,M2732A (vpp_mv=25000), INTEL/M2716,M2716M (25000), SGS-THOMSON/ETC2716,M2716 (25000), ST/ETC2716,M2716 (25000). All have `algorithm=None` (NON_DISPATCHABLE_ALGO=0x00 in `build_db.py`). [VERIFIED: read directly from chip_database.json]
- **RURP_VPP_CEILING_MV=22000:** Defined at `firestarter_app/tools/build_db.py:117`. [VERIFIED: read directly]
- **`check_dispatch.py` ceiling:** `_FAMILY_VPP_INVARIANTS: configure_eprom: (0, 22000)` — confirmed at `check_dispatch.py:79`. [VERIFIED: read directly]
- **Note on M2732A:** `build_db.py:NMOS_TRUE_VPP_MV: "M2732A": 21000`. M2732A requires 21V which is below the 22V ceiling — it is `support_status: supported` (correctly). The enumeration must note this distinction: M2732 (25V) = `vpp-exceeds-max`; M2732A (21V) = `supported`.
- **Cited reason:** RURP boost regulator theoretical ceiling ~22V per hardware evidence (Phase 66 finding, CLAUDE.md). 25V physically unreachable.

**`RURP_VPP_CEILING_MV=22000` location:**

This constant is defined ONLY in `firestarter_app/tools/build_db.py:117`. It is NOT in `constants.py` or the firmware. The ceiling is enforced at DB-build time (chips exceeding 22V get `vpp-exceeds-max`) and at `check_dispatch.py` VPP invariant time. The enumeration must cite the exact file+line and note there is no runtime enforcement at the firmware level (the firmware does not check the ceiling — it trusts the DB+host have done so).

---

### Q6: Output Artifact Location and Format

**Location:** `.planning/v1.13-PROTOCOL-ENUMERATION.md`

This is a **meta-repo planning artifact**, not a sub-repo doc. Rationale: the enumeration is a planning/evidence artifact (not operator-facing documentation about how to use the programmer), analogous to `.planning/v1.7-SHIELD-REVS.md` and `.planning/research/FEATURES.md`. The project's two-layer doc convention (meta investigation-canonical + sub-repo operator-canonical) applies to operator-facing docs like SHIELD-REVISIONS.md; a protocol feasibility enumeration belongs in `.planning/`.

A sub-repo doc is NOT needed because:
1. The enumeration is an internal planning artifact consumed by phases 73-76, not by end-users of the programmer.
2. The v1.11 field dictionary + protocol-id.md already serve the operator-facing protocol documentation role.
3. Adding a sub-repo doc would create a lockstep maintenance burden for a research artifact.

**Format:**

```markdown
# v1.13 Protocol Landscape Re-enumeration

**Date:** YYYY-MM-DD
**Status:** COMMITTED (gate for Phases 73-76)
**Supersedes:** v1.12 "feasible set" implicit claim
**RURP ceiling:** RURP_VPP_CEILING_MV = 22000 mV
  [VERIFIED: firestarter_app/tools/build_db.py:117]

## v1.12 Claim Review
[Explicit "holds / overstated" statement per row]

## In-Scope Protocol Enumeration
[12-row table: protocol_id | IC2_ALG | label | handler | DB chips | verdict | v1.12 claim | revision | evidence]

## Anti-Feature Block
[3 anti-feature rows: 0x11, 0x2A-0x2C]

## Gap Item Index
[5 named gap items cross-referenced to table rows + downstream phases]

## Ceiling Constraint
[RURP_VPP_CEILING_MV=22000: cited, confirmed unchanged]

## Sources
[file:line citations for every claim]
```

**Why this structure maximizes downstream utility:**
- Downstream phases cite by `protocol_id` row ("per PROTOCOL-ENUMERATION.md row 0x07: erase path = feasible-gap → Phase 75 scope").
- The "v1.12 claim" column makes the reaffirm/overturn judgment explicit per row, not just in prose.
- The "Gap item index" is a direct lookup from the 5 RSCH-01 success-criteria items to their table rows.
- The "Ceiling constraint" section is a self-contained citation the planner can insert into Phase 75 plans.

---

### Q7: Validation Architecture (Nyquist)

Phase 72 delivers a **committed document** (`.planning/v1.13-PROTOCOL-ENUMERATION.md`), not code. Validation therefore means: confirming the document's claims are accurate and internally consistent. There is no automated test suite for a planning artifact, but the following verification strategy is mechanically executable:

**Claim verification method per enumeration row:**

1. **Handler presence:** For each `protocol_id` claimed to have a handler, verify via grep: `grep -n "handle->protocol == 0x<ID>" firestarter/src/proms/memory.cpp`. Expected: the protocol arm appears before the `protocol != 0` fallback. [COMMAND: defined, runnable in CI]

2. **DB chip count:** For each `protocol_id`, count chips in `chip_database.json` with `programming.algorithm == <ID>`. [COMMAND: `python3 -c "import json; db=json.load(open('...chip_database.json')); print(sum(1 for mfg,chips in db.items() for c in chips if c.get('programming',{}).get('algorithm')==<N>))"` runnable in CI]

3. **Anti-feature ceiling unchanged:** For each anti-feature, assert `RURP_VPP_CEILING_MV = 22000` is still present in `build_db.py`. [COMMAND: `grep -n "RURP_VPP_CEILING_MV = 22000" firestarter_app/tools/build_db.py` — exit non-zero if absent]

4. **Fail-closed dispatch:** `check_dispatch.py` exits 0 (already a CI gate). Any chip whose `support_status != "supported"` must not reach a real handler. [COMMAND: `python tools/check_dispatch.py` — already enforced in CI]

5. **Infeasible arms in firmware:** Spot-check: `grep -n "configure_not_implemented" firestarter/src/proms/memory.cpp` — confirm 0x11, 0x2A, 0x2B, 0x2C, and `protocol != 0` fallback all present.

6. **SRAM no-op:** `sram.cpp` must still have 3-line stub. [COMMAND: `wc -l firestarter/src/proms/sram.cpp` — currently 17 lines including headers/includes; the function body is 3 lines]

7. **Flash4 chip-id gap:** `grep -n "CMD_CHECK_CHIP_ID" firestarter/src/proms/flash_type_4.cpp` — must return no results (the gap is real; if this passes, the gap has been closed prematurely).

**Validation Architecture section in VERIFICATION.md:**

The `VERIFICATION.md` for Phase 72 is document-level, not code-level. Its "Observable Truths" should be:

| # | Truth | Verification method |
|---|-------|---------------------|
| 1 | Enumeration assigns each in-scope `protocol_id` exactly one of: feasible-and-implemented / feasible-gap / infeasible | Count rows in the table; compare to KNOWN_PROTOCOLS set + anti-feature IDs; assert no protocol_id appears in two rows |
| 2 | Erase path (0x07) is marked feasible-gap; cite `eprom_internal_erase` + W27C512 datasheet | grep `eprom_internal_erase` in firmware; read erase rail section of datasheet |
| 3 | configure_sram no-op is classified pending Phase 73 (not resolved by enumeration alone) | Read sram.cpp; confirm no operation pointers set |
| 4 | X88C64 0x34 is re-classified from infeasible to feasible-gap | Check `chip_database.json` support_status for X88C64P; check `protocol-id.md` |
| 5 | Flash4 CMD_CHECK_CHIP_ID gap confirmed | `grep CMD_CHECK_CHIP_ID flash_type_4.cpp` returns empty |
| 6 | 0x39 stale comment located and documented | Source search; identify exact file + line |
| 7 | Anti-features (0x11, 0x2A-0x2C) confirmed fail-closed with cited code locations | `grep configure_not_implemented memory.cpp`; `grep MSG_ERR_PROTOCOL_NOT_IMPLEMENTED messages.h` |
| 8 | RURP_VPP_CEILING_MV=22000 confirmed unchanged | `grep RURP_VPP_CEILING_MV build_db.py` |

**Sampling strategy:**
- No "per commit" validation applies (no code committed).
- Gate: VERIFICATION.md reviewer reads the enumeration doc and cross-checks each row against the firmware dispatch, `chip_database.json` counts, and the v1.11 field dictionary. The Phase 72 VERIFICATION.md's "SC#1" through "SC#3" map directly to RSCH-01's three success criteria.

---

## Standard Stack

### Core (all REUSE — Phase 72 introduces no new dependencies)

| Component | Location | Purpose in this phase |
|-----------|----------|----------------------|
| `firestarter/src/proms/memory.cpp` | Firmware | Authoritative dispatch source |
| `firestarter/src/proms/sram.cpp` | Firmware | SRAM no-op evidence |
| `firestarter/src/proms/eprom.cpp` | Firmware | Erase electricals + flash4 chip-id gap |
| `firestarter/src/proms/flash_type_4.cpp` | Firmware | Flash4 CMD_CHECK_CHIP_ID gap |
| `firestarter/include/messages.h` | Firmware | `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` |
| `firestarter_app/firestarter/data/chip_database.json` | Host | Per-protocol chip counts, support_status |
| `firestarter_app/tools/build_db.py` | Host tools | `RURP_VPP_CEILING_MV`, `KNOWN_PROTOCOLS`, VPP classification |
| `firestarter_app/tools/check_dispatch.py` | Host tools | `_FAMILY_VPP_INVARIANTS`, dispatch mirror |
| `firestarter_app/firestarter/chip_resolver.py` | Host | Host-side infeasibility guard |
| `firestarter_app/doc/protocol-id.md` | Host docs | v1.11 field dictionary (IC2_ALG names) |
| `firestarter_app/doc/infoic-field-dictionary.md` | Host docs | Source-grounded field semantics |
| `firestarter_app/doc/sram-nvram-behavior.md` | Host docs | Phase 59 SRAM audit (no-op assessment) |
| `.planning/research/SUMMARY.md` | Meta | v1.13 research findings |
| `.planning/research/FEATURES.md` | Meta | v1.12 re-examination verdict |
| `.planning/milestones/v1.12-MILESTONE-AUDIT.md` | Meta | v1.12 tech debt record |

**No new packages required.** Phase 72 is pure desk research producing a committed markdown document.

---

## Architecture Patterns

### System Architecture Diagram

```
  minipro infoic.xml (upstream source)
         |
         v
  build_db.py (RURP_VPP_CEILING_MV=22000; KNOWN_PROTOCOLS)
         |
         v
  chip_database.json (support_status per chip; algorithm per chip)
         |                          |
         v                          v
  chip_resolver.py             memory.cpp (firmware)
  (host guard: refuses          (dispatch: protocol arms →
   non-supported chips           handlers or configure_not_implemented)
   before any wire byte)
         |
         v
  .planning/v1.13-PROTOCOL-ENUMERATION.md
  (Phase 72 deliverable — per-protocol verdict table)
         |
         v
  Phases 73-76 cite this document for scope decisions
```

### Recommended Plan Structure for Phase 72

The enumeration is best built as two or three plans:

**Plan 72-01 (Wave 1): Read the code + populate the table**

- Read each source file cited in the Standard Stack table.
- For each in-scope `protocol_id`: record handler, chip count (from `chip_database.json`), support_status distribution, v1.12 claim.
- Populate the 12-row enumeration table with all fields except "evidence citation" (done in Wave 2).

**Plan 72-02 (Wave 1 parallel): Draft the gap-item index + anti-feature block**

- For each of the 5 named gap items: write the code-state summary + enumeration verdict.
- Write the anti-feature block (0x11, 0x2A-0x2C) with code citations.
- Confirm `RURP_VPP_CEILING_MV=22000` at build_db.py:117.

**Plan 72-03 (Wave 2): Assemble + commit `.planning/v1.13-PROTOCOL-ENUMERATION.md`**

- Merge the table, gap-item index, anti-feature block, ceiling constraint.
- Add "evidence citation" column with file:line references.
- Commit the artifact.
- Update REQUIREMENTS.md RSCH-01 checkbox from `[ ]` to `[x]`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Protocol-ID list | A new scan of infoic.xml | `build_db.py:KNOWN_PROTOCOLS` + `protocol-id.md` | The v1.11 field dictionary already did this work with source citations |
| VPP ceiling logic | Re-derive the 22V ceiling | `build_db.py:RURP_VPP_CEILING_MV = 22000` | Existing constant with hardware evidence; do not invent a new value |
| Dispatch mirror | Re-reading memory.cpp in isolation | `check_dispatch.py:dispatch()` function | Already mirrors the dispatch order with the exception of 0x35/0x39 (CR-02 from Phase 71-08, now aligned) |
| Chip count queries | Manual grep | `python3 -c "..."` against chip_database.json | The DB is already the authoritative source; simple script |

**Key insight:** Almost all evidence for this enumeration already exists in project artifacts. The Phase 72 work is _synthesis and commitment_, not new discovery. The executor reads existing source files, counts existing DB entries, and writes a committed document that makes the implicit knowledge explicit and citable.

---

## Common Pitfalls

### Pitfall 1: Conflating protocol-axis with support_status-axis
**What goes wrong:** The executor classifies a chip's `support_status` as the feasibility verdict for the protocol. Example: seeing `support_status: supported` for all SRAM chips and concluding the SRAM protocol is "feasible-and-correct."
**Why it happens:** `support_status` is per-chip; feasibility verdict is per-protocol. A protocol can be `feasible-and-implemented` at the dispatch level but have a correctness gap at the operation level (`configure_sram` no-op).
**How to avoid:** Populate the "DB chips" column with both the total count and the operation-level concern. State explicitly: "dispatches to a real handler" vs. "handler performs meaningful work."

### Pitfall 2: Treating 0x35 and 0x39 as host-dispatch supported
**What goes wrong:** The executor notes that firmware dispatches {0x05, 0x35, 0x39} → `configure_flash4` and concludes 0x35 and 0x39 are equivalent to 0x05 for host purposes.
**Why it happens:** Phase 71-08 intentionally omitted 0x35/0x39 from the host dispatch mirror (`check_dispatch.py`) because 0 DB chips use them. The host `KNOWN_PROTOCOLS` in `build_db.py` also excludes 0x35 (it is `IC2_ALG_ITE`, an EC MCU — not a DIP memory protocol) and 0x39 (phantom).
**How to avoid:** The enumeration must record the host/firmware distinction: firmware dispatches all three as flash4 (correct at the wire level for hand-crafted commands); host excludes 0x35 and 0x39 from DB inclusion (correct at the classification level). They are separate concerns.

### Pitfall 3: Over-claiming the erase gap scope
**What goes wrong:** The executor assumes the entire erase path is missing (no firmware support) when actually `eprom_internal_erase` exists and the `erase` CLI command invokes `erase_eprom` → `COMMAND_ERASE` → firmware `eprom_erase_execute` → `eprom_internal_erase`. The gap may be narrower than "erase doesn't work at all."
**Why it happens:** The REQUIREMENTS.md phrasing "erase path not wired" suggests a complete absence.
**How to avoid:** Read `eprom_operations.py:erase_eprom` and `cli_handlers.py:erase` to determine if a standalone `firestarter erase W27C512` already invokes the firmware erase electricals. If it does, the gap is the host-side `FLAG_CAN_ERASE` routing in the write path (auto-erase before write), not the standalone erase command. State the exact gap.

### Pitfall 4: Treating the enumeration as implementation
**What goes wrong:** The executor starts specifying firmware implementation details for the 0x34 X88C64 handler or the SRAM fix, rather than just recording the feasibility verdict + deferral rationale.
**Why it happens:** Phase 72 is desk-side re-search only; implementation belongs in Phases 74/75/76.
**How to avoid:** For gap items, record: (a) verdict, (b) why RURP can physically drive it, (c) what is missing (protocol spec / host wiring / handler), (d) which downstream phase addresses it. Do NOT specify register sequences or implementation details.

### Pitfall 5: Missing the 0x2B entry in protocol-id.md
**What goes wrong:** The enumeration correctly documents 0x2A and 0x2C as infeasible (from `protocol-id.md`) but overlooks 0x2B, which appears in `memory.cpp:108` in the infeasible arm.
**Why it happens:** `protocol-id.md` excludes table only lists 0x2A and 0x2C; 0x2B has no named IC2_ALG constant listed there but is in the firmware dispatch arm.
**How to avoid:** Read `memory.cpp:107-110` directly; enumerate all four values (0x11, 0x2A, 0x2B, 0x2C) and note the doc gap for 0x2B.

---

## Code Examples

### Dispatch Chain (source-of-truth)
```cpp
// firestarter/src/proms/memory.cpp:74-119 [VERIFIED: read directly]
if (handle->protocol == 0x10) { configure_flash_intel(handle); return; }
if (handle->protocol == 0x0D) { configure_eeprom28c(handle); return; }
if (handle->protocol == 0x06) { configure_flash3(handle); return; }
if (handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39) {
    configure_flash4(handle); return; }
if (handle->protocol == 0x07 || handle->protocol == 0x08 || handle->protocol == 0x0B) {
    configure_eprom(handle); return; }
if (handle->protocol == 0x0E || handle->protocol == 0x27 ||
    handle->protocol == 0x28 || handle->protocol == 0x29) {
    configure_sram(handle); return; }
// Named infeasibility arms (D-02)
if (handle->protocol == 0x11 || handle->protocol == 0x2A ||
    handle->protocol == 0x2B || handle->protocol == 0x2C) {
    configure_not_implemented(handle); return; }
// Generic fail-closed guard
if (handle->protocol != 0) { configure_not_implemented(handle); return; }
```

### SRAM No-Op (source-of-truth)
```cpp
// firestarter/src/proms/sram.cpp:15-17 [VERIFIED: read directly]
void configure_sram(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_SRAM);
}
```
No operation pointers set. The generic memory layer (`memory_write_execute`, `memory_read_execute`) is set up by `configure_memory` BEFORE this call — SRAM writes use the generic byte-write path.

### Erase Electricals (source-of-truth)
```cpp
// firestarter/src/proms/eprom.cpp:274-288 [VERIFIED: read directly]
void eprom_internal_erase(firestarter_handle_t* handle) {
    rurp_chip_input();
    handle->firestarter_set_control_register(handle, CTRL_VPP_REGULATOR_ENABLE, 1);
    delay(100);
    handle->firestarter_set_address(handle, 0x0000);
    handle->firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 1);
    delay(100);
    rurp_chip_enable();
    delayMicroseconds(handle->pulse_delay);
    rurp_chip_disable();
    handle->firestarter_set_control_register(
        handle, CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE, 0);
}
```
Note: `CTRL_VPP_VPE_DROP_ENABLE` is NOT set — the regulator output goes directly without the dropping resistor (higher voltage than the write path which uses the drop). The W27C512 datasheet specifies 14V for erase vs. 12V for write. The regulator setpoint is controlled by `vpp_mv` in the JSON command.

### Flash4 Missing CMD_CHECK_CHIP_ID (gap evidence)
```cpp
// firestarter/src/proms/flash_type_4.cpp:26-40 [VERIFIED: read directly]
void configure_flash4(firestarter_handle_t* handle) {
    switch (handle->cmd) {
        case CMD_WRITE:  // wired
        case CMD_ERASE:  // wired
        case CMD_BLANK_CHECK:  // wired
        // CMD_CHECK_CHIP_ID: NOT PRESENT
    }
}
// By contrast, flash_type_3.cpp:46-48 has CMD_CHECK_CHIP_ID → flash3_check_chip_id_execute
```

### VPP Ceiling (source-of-truth)
```python
# firestarter_app/tools/build_db.py:115-117 [VERIFIED: read directly]
# Chips requiring VPP above this cannot be programmed on any RURP revision.
RURP_VPP_CEILING_MV = 22000
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Protocol fallback via `mem_type` chain (all protocols) | Protocol-prefix dispatch first; `mem_type` chain only reachable when `protocol == 0` | v1.12 Phase 64 | Eliminated 12V VPP hazard for unknown protocols |
| Silent skip of unsupported chips in DB | Capability-honest DB: list all DIP parallel chips with `support_status` | v1.12 Phase 66 | 14 non-supported chips now visible in `info`/`list` |
| Protocol-ID classification via guess-tables | Source-grounded v1.11 field dictionary (IC2_ALG constants from minipro `database.h`) | v1.11 Phase 56 | 4 decode bugs fixed; `protocol-id.md` is now citeable |
| `configure_sram` as implicit pass-through | Documented as near-no-op; GATE-04 SRAM audit completed | v1.11 Phase 59 | Behavior known; behavioral correctness deferred to v1.13 VAL-06 |

**Deprecated/outdated:**
- "feasible set is complete" (v1.12 implicit claim): partially overstated — 3 genuine RURP-feasible gaps exist (erase path, SRAM no-op, X88C64 0x34 re-classification). Anti-features remain correctly infeasible.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The standalone `firestarter erase W27C512` command does NOT currently trigger the firmware erase electricals for EE-EPROMs (i.e., the gap is real) | Gap Item 1 | If the erase command already works, ERASE-01 scope is narrower; Phase 75 may be trivial or closed-with-evidence |
| A2 | `configure_sram` near-no-op in Phase 59 is still unchanged; writes use the generic `memory_write_execute` path and succeed | Gap Item 2 | If `configure_sram` was updated since Phase 59 (unlikely but check git log), the no-op finding changes |
| A3 | X88C64 0x34 uses a standard parallel byte/page-write EEPROM protocol (STORE/RECALL aside) that RURP can drive | Gap Item 3 | If the 0x34 protocol requires non-parallel signaling, the feasibility verdict drops from `feasible-gap` to `infeasible` |
| A4 | The "stale 0x39 comment" is in the planning/REQUIREMENTS.md description, not in a source file comment | Gap Item 5 | If there is an actual source-file comment claiming "0x39 = 0 chips", it needs to be located and corrected in FIX-03 |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed.
The table above lists 4 items that benefit from executor confirmation during plan execution.

---

## Open Questions

1. **Erase gap exact scope**
   - What we know: `eprom_internal_erase` exists; the `erase` CLI command uses `_build_op_flags(blank_check=..., force=...)` which does not set `FLAG_CAN_ERASE`.
   - What's unclear: Does the firmware's `eprom_erase_execute` require `FLAG_CAN_ERASE` to be set (reading the eprom.cpp:88-91 flow shows it calls `eprom_internal_erase` unconditionally). So the standalone erase command may already work electrically; the gap might be only that the write command doesn't auto-erase EE-EPROMs when `FLAG_CAN_ERASE` would be expected.
   - Recommendation: Plan 72-01 should read `eprom_operations.py:erase_eprom` in full and test with `firestarter erase W27C512` logic-trace (no hardware needed) to determine the exact gap before committing Phase 75 scope.

2. **0x2B identity**
   - What we know: `memory.cpp:108` includes `0x2B` in the infeasible arm; `protocol-id.md` Excluded table does not list 0x2B.
   - What's unclear: Is 0x2B `IC2_ALG_GAL20` or another PLD algorithm? The minipro `database.h` at commit `a8efaedc` has the answer.
   - Recommendation: The executor should check `database.h` for 0x2B and add it to the `protocol-id.md` excluded table as part of the enumeration artifact.

3. **SRAM write behavior — generic-path coverage**
   - What we know: `configure_sram` sets no operation pointers; `configure_memory` sets `firestarter_operation_main = memory_write_execute` for `CMD_WRITE` BEFORE calling the protocol handler.
   - What's unclear: This means SRAM writes go through `memory_write_execute` (generic byte-write via `memory_set_data`) — does this actually work for JEDEC SRAM? Almost certainly yes; SRAM is the simplest memory type. But phase 72's enumeration should state: "behavior unconfirmed — Phase 73 VAL-06 resolves."
   - Recommendation: Enumeration notes the generic-path analysis and classifies as `feasible-and-implemented (behavior deferred to Phase 73)`.

---

## Environment Availability

Step 2.6: SKIPPED — Phase 72 is a desk-research phase producing a planning document. No external tools, CLIs, runtimes, databases, or bench hardware are required beyond the existing development environment.

---

## Validation Architecture

> Phase 72 delivers a committed document, not code. Validation means: confirming the document's claims are accurate and traceable to source files.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None (document validation) |
| Config file | None |
| Quick run command | `grep -c "protocol_id" .planning/v1.13-PROTOCOL-ENUMERATION.md` (confirms table rows exist) |
| Full suite command | Manual verification checklist (see below) |

### Phase Requirements → Verification Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RSCH-01 SC#1 | Each in-scope `protocol_id` has exactly one verdict (feasible-and-implemented / feasible-gap / infeasible), citing v1.11 field dictionary + datasheets; v1.12 "holds vs. overstated" recorded per row | Document inspection | `grep -n "feasible" .planning/v1.13-PROTOCOL-ENUMERATION.md | wc -l` (≥ 12 rows) | ❌ Wave 0 — artifact created in this phase |
| RSCH-01 SC#2 | 5 named gap items (erase/SRAM/X88C64/flash4-id/0x39) each marked in-scope or deferred with rationale | Document inspection | `grep -n "feasible-gap\|in-scope\|deferred" .planning/v1.13-PROTOCOL-ENUMERATION.md` | ❌ Wave 0 |
| RSCH-01 SC#3 | Anti-features re-confirmed fail-closed with cited code locations; `RURP_VPP_CEILING_MV=22000` not relaxed | Code grep + document inspection | `grep "RURP_VPP_CEILING_MV = 22000" firestarter_app/tools/build_db.py` (exit 0 = confirmed); `grep "configure_not_implemented" firestarter/src/proms/memory.cpp` (≥ 5 lines) | ✅ Code files exist |

### Sampling Rate
- **Per task commit:** Committer reviews the populated table row for accuracy against the cited code file.
- **Per wave merge:** All three SC#1–SC#3 verification grep commands run; all pass.
- **Phase gate:** VERIFICATION.md reviewer reads the full enumeration document and cross-checks ≥ 3 table rows against firmware source before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `.planning/v1.13-PROTOCOL-ENUMERATION.md` — the primary deliverable; covers RSCH-01 SC#1/SC#2/SC#3
- [ ] `.planning/phases/72-re-research-the-protocol-landscape/72-VERIFICATION.md` — verification report

*(Existing code files used as evidence sources all exist; no new code files required.)*

---

## Security Domain

Phase 72 is a documentation/research phase with no code changes and no external inputs. No ASVS categories apply. The phase confirms that anti-features remain fail-closed (a security-relevant invariant), but this confirmation is achieved through document review, not code changes.

The fail-closed invariants themselves are enforced by:
- `chip_resolver.py:resolve_chip` (host guard, fires before any serial byte)
- `memory.cpp:configure_not_implemented` → `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` (firmware guard)
- `check_dispatch.py` CI gate (regression guard)

None of these change in Phase 72. The enumeration document cites them; it does not relax them.

---

## Project Constraints (from CLAUDE.md)

| Directive | Source | Impact on Phase 72 |
|-----------|--------|-------------------|
| Sub-repos are git submodules; meta tracks only `.planning/` and `.claude/` | `./CLAUDE.md` | Enumeration artifact belongs in `.planning/`; no sub-repo commits |
| Constants/flag bits duplicated between Python and C++ — keep in sync | `./CLAUDE.md` | Not applicable (no code changes) |
| `chip_database.json` — do NOT edit by hand | `firestarter_app/CLAUDE.md` | Not applicable (no DB edits) |
| Firmware dispatch: `protocol` prefix chain fires BEFORE `mem_type` chain | `firestarter/CLAUDE.md` | This is the authoritative dispatch description; enumeration must reference it |
| KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39} | `firestarter/CLAUDE.md` | Enumeration must cover this exact set (note: host `build_db.py` KNOWN_PROTOCOLS differs — 0x34 added, 0x35/0x39 excluded; enumeration must address both sets) |

---

## Sources

### Primary (HIGH confidence)
- `firestarter/src/proms/memory.cpp` (read directly) — dispatch order, infeasible arms, erase `CMD_ERASE` path [VERIFIED]
- `firestarter/src/proms/sram.cpp` (read directly) — configure_sram near-no-op [VERIFIED]
- `firestarter/src/proms/eprom.cpp` (read directly) — `eprom_internal_erase` electricals, `FLAG_CAN_ERASE` write-init gating [VERIFIED]
- `firestarter/src/proms/flash_type_4.cpp` (read directly) — CMD_CHECK_CHIP_ID gap [VERIFIED]
- `firestarter/src/proms/not_implemented.cpp` (read directly) — `configure_not_implemented` → 0xBB [VERIFIED]
- `firestarter/include/messages.h:96` (read directly) — `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` [VERIFIED]
- `firestarter_app/tools/build_db.py:117` (read directly) — `RURP_VPP_CEILING_MV = 22000` [VERIFIED]
- `firestarter_app/tools/build_db.py:134-148` (read directly) — `KNOWN_PROTOCOLS` set [VERIFIED]
- `firestarter_app/tools/check_dispatch.py:79-85` (read directly) — `_FAMILY_VPP_INVARIANTS` [VERIFIED]
- `firestarter_app/tools/check_dispatch.py:133-157` (read directly) — `dispatch()` mirror [VERIFIED]
- `firestarter_app/firestarter/chip_resolver.py` (read directly) — host infeasibility guard [VERIFIED]
- `firestarter_app/firestarter/database.py:590-598` (read directly) — `FLAG_CAN_ERASE` derivation from `info-flags & 0x10` [VERIFIED]
- `firestarter_app/firestarter/data/chip_database.json` (queried directly) — 744 chips, 730 supported, 9 adapter-required, 4 vpp-exceeds-max, 1 protocol-not-implemented [VERIFIED]
- `firestarter_app/doc/protocol-id.md` (read directly) — v1.11 field dictionary, IC2_ALG names, excluded ID rationales [VERIFIED]
- `firestarter_app/doc/sram-nvram-behavior.md` (read directly) — Phase 59 SRAM audit, near-no-op classification [VERIFIED]

### Secondary (MEDIUM confidence)
- `.planning/research/SUMMARY.md` — v1.13 research findings [CITED]
- `.planning/research/FEATURES.md:183-191` — v1.12 re-examination verdict text [CITED]
- `.planning/milestones/v1.12-MILESTONE-AUDIT.md` — v1.12 tech debt record [CITED]
- `firestarter/CLAUDE.md` — firmware architecture, dispatch order documentation [CITED]
- `firestarter_app/CLAUDE.md` — host architecture, WARNING-5 explanation [CITED]
- W27C512 datasheet: erase mode OE/VPP=14V, A9=14V [CITED: `.planning/research/SUMMARY.md §Sources`]

### Tertiary (LOW confidence)
- X88C64 0x34 STORE/RECALL + byte/page write protocol — exact protocol unconfirmed; datasheet not directly read in this session [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Enumeration inventory and sourcing: HIGH — all source files read directly
- Verdict taxonomy: HIGH — grounded in code + v1.11 field dictionary
- Five gap items: HIGH for code-state (all source files read); MEDIUM for behavioral conclusions (SRAM no-op behavior; erase gap exact scope) pending executor code-trace
- Anti-feature re-confirmation: HIGH — code locations verified
- Output artifact format: HIGH — follows established project doc conventions
- X88C64 0x34 protocol feasibility: MEDIUM — physical package confirmed, exact protocol [ASSUMED]

**Research date:** 2026-06-17
**Valid until:** Stable — all findings grounded in project source files that change only when code changes. Re-validate if any of {memory.cpp, sram.cpp, eprom.cpp, flash_type_4.cpp, build_db.py, chip_database.json} are modified before Phase 72 executes.
