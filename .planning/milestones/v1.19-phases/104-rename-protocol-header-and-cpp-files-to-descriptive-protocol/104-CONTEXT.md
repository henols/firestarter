# Phase 104: Rename protocol header/.cpp files to descriptive protocol-type names — Context

**Gathered:** 2026-07-02
**Status:** Ready for planning
**Source:** Orchestrator-captured decisions (post-research), /gsd-plan-phase 104

<domain>
## Phase Boundary

Trailing legibility cleanup of the v1.19 "Protocol Naming Labels" milestone (Phases 100–103, CLOSED). Phase 100 authored the operator-approved canonical `PROTO_<NAME>` name set; Phase 101 applied the constants + relabeled the `memory.cpp` dispatch chain — but two minipro-heritage handler files/functions kept their hard-to-read `flash_type_N` names. Phase 104 finishes the rename across firmware, the host GATE-01 dispatch-mirror guard tooling, the native validation-test suites, and the docs.

**In scope:**
- Firmware handler files + functions: `flash_type_3.{cpp,h}` / `configure_flash3()` and `flash_type_4.{cpp,h}` / `configure_flash4()`.
- All references: `#include`s and call sites in `firestarter/src/proms/memory.cpp`, header include-guard macros, PlatformIO build config.
- Host GATE-01 guard tooling that keys on these filenames/function-name strings: `test_dispatch_mirror.py`, `check_dispatch.py`, `validation_matrix_spec.json` (+ regenerated `validation_matrix.h`), `test_check_dispatch_invariants.py`, and any host doc tables.
- Native validation test suites `test_val_flash3` / `test_val_flash4` (dirs + family-ids) AND the PROTOCOLS.md §3 INV suite-path contract they satisfy.

**Out of scope (already descriptive — confirmed by research):** `flash_intel`, `eprom`, `sram`, `eeprom_28c`, `not_implemented` files/functions. No `PROTO_<NAME>` numeric-value change, no `chip_database.json` / wire change, no CLI grammar change.
</domain>

<decisions>
## Implementation Decisions

### Rename map (LOCKED — derived verbatim from operator-approved PROTO_ tokens)
- `flash_type_3.{cpp,h}` → `flash_nor_unlock.{cpp,h}`; `configure_flash3()` → `configure_flash_nor_unlock()` — serves `PROTO_FLASH_NOR_UNLOCK` (0x06).
- `flash_type_4.{cpp,h}` → `flash_5v_page.{cpp,h}`; `configure_flash4()` → `configure_flash_5v_page()` — serves `PROTO_FLASH_5V_PAGE` (0x05) + phantoms 0x35/0x39.

### Scope decision Q1 — Files **and** functions (operator-chosen)
Rename both the `.cpp/.h` files AND the `configure_flash3/4` functions. This is a **full dual-repo lockstep** phase: the host GATE-01 dispatch-mirror guard references these C++ names, so `firestarter_app` moves in lockstep with `firestarter`. Wire protocol is genuinely unchanged (only the numeric `algorithm` flows).

### Scope decision Q2 — Rename the native test suites too (operator-chosen)
Rename `test_val_flash3` / `test_val_flash4` suite dirs + their family-ids to descriptive names following the new function stems, and update the PROTOCOLS.md §3 INV-01..09 suite-path contract (SAFE-02) to match. The SAFE-02 contract is intentionally reopened for this rename — keep the INV matrix internally consistent.

### Hygiene decisions (LOCKED)
- Fix the misspelled header guards `__FALSH__TYPE_3_H__` / `__FALSH__TYPE_4_H__` to correct `__FLASH_NOR_UNLOCK_H__` / `__FLASH_5V_PAGE_H__` form during the rename.
- Use `git mv` to preserve file history.
- Preserve the MIT license header block on each renamed file.
- `validation_matrix.h` is GENERATED (`DO NOT EDIT`) — regenerate via the host `gen_validation_header.py` from the updated `validation_matrix_spec.json`; never hand-edit.
- Run `pio run -t clean` before rebuild to avoid stale `.pio` artifacts referencing old object files.

### Claude's Discretion
- Exact descriptive spelling of the renamed test-suite dirs/family-ids (follow the new function stem, e.g. `test_val_nor_unlock` / `test_val_5v_page`), subject to keeping PROTOCOLS.md §3 consistent.
- Ordering/task decomposition (firmware-first then host lockstep, or single atomic dual-repo change) — planner's call, but each repo commits on its own `v1.19-protocol-naming-labels` branch per project sync rules.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Naming source of truth
- `firestarter/doc/PROTOCOLS.md` — operator-approved canonical name set (§0 tokens), four-facet bucket prose (§1), and the INV-01..09 native-test suite-path contract (§3) that must be updated for the test-suite rename.
- `firestarter/include/proto_constants.h` — the `PROTO_<NAME>` tokens (0x05 `PROTO_FLASH_5V_PAGE`, 0x06 `PROTO_FLASH_NOR_UNLOCK`) the new file/function names derive from.

### Firmware
- `firestarter/src/proms/memory.cpp` — dispatch chain + `#include`s + `configure_flash3/4` call sites.
- `firestarter/include/flash_type_3.h`, `firestarter/include/flash_type_4.h`, `firestarter/src/proms/flash_type_3.cpp`, `firestarter/src/proms/flash_type_4.cpp` — the files to rename.
- `firestarter/CLAUDE.md` — PlatformIO build/test conventions; `firestarter/platformio.ini` for any build globbing/filters.

### Host GATE-01 guard tooling (dual-repo lockstep)
- `firestarter_app/.../test_dispatch_mirror.py` (~lines 75–76) — filename→function map.
- `check_dispatch.py`, `validation_matrix_spec.json`, `test_check_dispatch_invariants.py` — function-name-string keyed guards.

### Research
- `.planning/phases/104-rename-protocol-header-and-cpp-files-to-descriptive-protocol/104-RESEARCH.md` — full reference inventory (file:line), pitfalls, gate mechanics, environment notes.
</canonical_refs>

<specifics>
## Specific Ideas

- **Suggested requirement IDs (planner may adopt):** RENAME-01 (firmware files), RENAME-02 (firmware functions), RENAME-03 (host guard tooling lockstep + regenerate validation_matrix.h), RENAME-04 (native test suites + family-ids), RENAME-05 (PROTOCOLS.md §3 INV contract + doc tables). Carry GATE-01/02/03 non-regression.
- **Verification / gates:**
  - GATE-01 (dispatch-mirror guard): `pio test -e native` (pio 6.1.19 present — real PASS) + `check_dispatch.py` green after rename; the dispatch-mirror parse must resolve the new filenames/functions.
  - GATE-02 (DB/constants identity): `diff_db.py` identity vs Phase-94 baseline; constants-parity leg is CI-PENDING (no python3.11 in devcontainer, Phase 98/103 precedent) and this phase touches no constants values, so that leg is weak/non-blocking here.
  - GATE-03: no CLI grammar / no source-CLI file touched, no name accepted as CLI input — must hold (pure rename).
</specifics>

<deferred>
## Deferred Ideas

- Renaming already-descriptive handlers (`flash_intel`, `eprom`, `sram`, `eeprom_28c`) — not needed.
- `datasheets/<hex>-<NAME>/` slug renames (v1.19 NAME-F1) and protocol-name-as-CLI-input (NAME-F2) — remain deferred, unchanged by this phase.
</deferred>

---

*Phase: 104-rename-protocol-header-and-cpp-files-to-descriptive-protocol*
*Context gathered: 2026-07-02 via /gsd-plan-phase 104 (post-research orchestrator capture)*
