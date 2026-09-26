---
phase: 10-static-pins
verified: 2026-05-12T10:16:00Z
status: passed
score: 2/2 must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-FW-05
  - REQ-FW-06
follow_ups:
  - source: v1.0-MILESTONE-AUDIT.md INFO-3 / FW-07 (v1.2 candidate)
    item: "pinouts.json static-high-pins coverage is only populated for DIP24_2716 and DIP24_2732 today; DIP28 and DIP32 quirk pins (CE2 / JEDEC-tied NC) are not declared. REQ-FW-05 wire is correct; coverage data is the gap."
    severity: info
    in_scope: false
    note: "Deferred to v1.2 (FW-07 in REQUIREMENTS.md Future Requirements). Coverage extension, not a wire defect — the static_high_mask plumbing handles any pin populated upstream."
---

# Phase 10: Static Pins, Multi-CE, and Address Bus Correctness — Verification Report

**Phase Goal:** "Add `static_high_mask` to `bus_config_t` so pins that must always be driven HIGH (second CE, tied-high NC pins) are handled by data rather than firmware hacks. Clean up the dead condition in `mem_util_calculate_top_address_register`." Concretely: the `static_high_mask` value flows DB → wire JSON → firmware handle → applied to the address bus by `mem_util_remap_address_bus`; and the VPE_TO_VPP / ADDRESS_LINE_16 conflict is correctly guarded by `if (handle->pins < 32)` in `mem_util_calculate_top_address_register`, with the legacy dead `READ_WRITE == WRITE_FLAG` check removed.
**Verified:** 2026-05-12T10:16:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `static_high_mask` end-to-end wire is intact: DB-side `static-high-pins` declaration → `get_bus_config` pin-translation → wire JSON `"static-high"` array → `parse_bus_config` OR-into-mask → `mem_util_remap_address_bus` mask-application. **REQ-FW-05.** | VERIFIED | Hop 1: `firestarter_app/firestarter/data/pinouts.json:10` (`"static-high-pins": [24]` for DIP24_2716) and `:21` (same for DIP24_2732). Hop 2: `firestarter_app/firestarter/database.py:265` (`get_bus_config` def); `:309-319` translates `static-high-pins` via `pin_conversions`, emitting `map_config["static-high"]`; `pin_conversions[24][24] = 13` at `:87-88` (DIP24 → bus line 13). Hop 3: wire JSON `"static-high":[13]` (post-translation; written into the bus-config sub-object by `get_bus_config`). Hop 4: `firestarter/src/json_parser.c:426` — `handle->bus_config.static_high_mask \|= 1UL << line;` inside `parse_bus_config` (defined at `:193`); init to 0 at `:84`. Hop 5: `firestarter/src/proms/memory.cpp:319` — `reorg_address \|= config.static_high_mask;` inside `mem_util_remap_address_bus` (function opens at `:226`). Wire-contract field declaration: `firestarter/include/firestarter.h:72` — `uint32_t static_high_mask;` in `bus_config_t`. Cross-link `v1.0-INTEGRATION-CHECK.md` rows 10 + 11. |
| 2 | `pins < 32` VPE_TO_VPP guard is intact in `mem_util_calculate_top_address_register` (with the explanatory comment about VPE_TO_VPP/ADDRESS_LINE_16 sharing a CONTROL bit); the legacy dead `READ_WRITE == WRITE_FLAG` check is **absent**. **REQ-FW-06.** | VERIFIED | `firestarter/src/proms/memory.cpp:137` (`mem_util_calculate_top_address_register` def); `:140` (`if (handle->pins < 32) {`); `:141-142` (comment: "VPE_TO_VPP and ADDRESS_LINE_16 share the same CONTROL bit — preserving VPE_TO_VPP would corrupt A16 for 32-pin (512KB) chips. DIP32 chips use P1_VPP_ENABLE instead."); `:143` (`mask \|= VPE_TO_VPP;` inside the guard). Dead-check confirmation: `grep -n "READ_WRITE == WRITE_FLAG" firestarter/src/proms/memory.cpp` returns no matches (verified 2026-05-12). |

**Score:** 2/2 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/data/pinouts.json` | `"static-high-pins": [24]` for DIP24_2716 and DIP24_2732 | VERIFIED | Block at `:10` (DIP24_2716) and `:21` (DIP24_2732). |
| `firestarter_app/firestarter/database.py` | `get_bus_config` translates `static-high-pins` via `pin_conversions`, emits `"static-high"` array; `pin_conversions[24][24] = 13` | VERIFIED | `get_bus_config:265`; `static-high-pins` block at `:309-319` (`map_config["static-high"] = static_high` at `:319`); `pin_conversions[24][24] = 13` at `:87-88`. |
| `firestarter/include/firestarter.h` | `bus_config_t::static_high_mask` field declaration (wire contract) | VERIFIED | `:72` — `uint32_t static_high_mask;` with comment "Bus lines unconditionally driven HIGH (e.g. CE2, tied-high NC pins)". |
| `firestarter/src/json_parser.c` | `parse_bus_config` initializes `static_high_mask = 0`, then ORs each `"static-high"` array element into the mask | VERIFIED | `parse_bus_config:193`; init at `:84`; OR-loop application at `:239`. |
| `firestarter/src/proms/memory.cpp` | `mem_util_remap_address_bus` applies the mask; `mem_util_calculate_top_address_register` guards VPE_TO_VPP with `pins < 32` and has NO `READ_WRITE == WRITE_FLAG` check | VERIFIED | `mem_util_remap_address_bus:226`; mask application at `:247`. `mem_util_calculate_top_address_register:137`; `pins < 32` guard at `:140`; `mask \|= VPE_TO_VPP` at `:143`. No `READ_WRITE == WRITE_FLAG` literal matches in `memory.cpp`. |

---

### Key Link Verification — `static_high_mask` 5-Hop Chain (REQ-FW-05) + `pins < 32` Guard (REQ-FW-06)

| Hop | From | To | Via | Status |
|-----|------|----|----|--------|
| 1 | `pinouts.json:10` and `:21` | DIP24 pin 24 declared as `static-high-pins` | DB-side declaration | WIRED |
| 2 | `pinouts.json::static-high-pins` | `map_config["static-high"]` (wire JSON) | `database.py::get_bus_config:309-319` translates pin → bus line via `pin_conversions[24][24] = 13` (database.py:87-88) | WIRED |
| 3 | wire JSON `"static-high":[13]` | firmware `bus_config_t::static_high_mask` | Phase-02-style key-value wire (no `_mv` rename in this path — `static-high` is the canonical wire key) | WIRED |
| 4 | wire JSON `"static-high":[N]` | `handle->bus_config.static_high_mask |= 1UL << N` | `json_parser.c::parse_bus_config:239` (init at `:84`) | WIRED |
| 5 | `handle->bus_config.static_high_mask` | `reorg_address |= config.static_high_mask` | `memory.cpp::mem_util_remap_address_bus:247` (function at `:226`) | WIRED |
| — | `mem_util_calculate_top_address_register:137` | `mask |= VPE_TO_VPP` guarded for `pins < 32` only | `memory.cpp:140` (`if (handle->pins < 32) {`) + comment `:141-142` + body `:143`; dead `READ_WRITE == WRITE_FLAG` check **absent** | WIRED |

Cross-link `v1.0-INTEGRATION-CHECK.md` rows 10 (REQ-FW-05 wire-trace) and 11 (REQ-FW-06 dead-check removal) — cited by row number; not duplicated here.

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `pinouts.json` | `static-high-pins` array | Static DB declaration per pinout variant | Yes — `[24]` for both DIP24 variants today | FLOWING |
| `database.py:get_bus_config` | `static_high` (wire-side list) | `pin_conversions[pins][pin]` translation | Yes — `[13]` for DIP24 (pin 24 → bus line 13) | FLOWING |
| wire JSON | `"static-high":[13]` | `database.py` emission via `map_config["static-high"]` | Yes — present in every DIP24 command frame | FLOWING |
| `json_parser.c:parse_bus_config:239` | `handle->bus_config.static_high_mask` | `|= 1UL << 13` for line 13 | Yes — mask bit 13 set on the handle | FLOWING |
| `memory.cpp:mem_util_remap_address_bus:247` | `reorg_address` | `|= config.static_high_mask` | Yes — bus line 13 driven HIGH for every DIP24 chip access; supplies VCC to the chip through socket position 28 | FLOWING |

---

### Behavioral Spot-Checks

(All commands cited from existing verification artifacts — Phase 3 does not re-run per CONTEXT.md D-09 / RESEARCH.md Pitfall #3.)

| Behavior | Command | Result | Cited From |
|----------|---------|--------|------------|
| 743-chip wire round-trip — every DIP24 pinout-bearing chip parses and dispatches without regression (`static-high` array round-trips cleanly) | `firestarter_app/tools/check_dispatch.py` | exit 0 | `02-VERIFICATION.md` (v1.1) SC4 |
| Full Phase 1 native suite — no regression in any handler that consumes `bus_config.static_high_mask` | `pio test -e native` | 25/25 PASS | `01-VERIFICATION.md` Behavioral Spot-Check |
| Algo-first dispatch correctness (DIP24-pinout chips reach the right handler via algorithm-first path) | `pio test -e native` (test_dispatch) | 15/15 PASS | `12-VERIFICATION.md` Truth #6 |
| AVR firmware budget (uno + leonardo) with `static_high_mask` field linked | `pio run -e uno` / `-e leonardo` | both SUCCESS | `12-VERIFICATION.md` Truth #7 |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-FW-05 | 10-01 (v1.0) | `static_high_mask` data-driven mechanism replaces hardcoded `ADDRESS_LINE_13` for 24-pin chips; end-to-end wire is intact. | SATISFIED | 5-hop chain rows in Key Link Verification table above. Wire-contract field at `firestarter.h:72`; mask-application at `memory.cpp:319`. Cross-link `v1.0-INTEGRATION-CHECK.md` row 10. |
| REQ-FW-06 | 10-01 (v1.0) | Dead `READ_WRITE == WRITE_FLAG` check removed from `mem_util_calculate_top_address_register`; VPE_TO_VPP guarded by `pins < 32` instead. | SATISFIED | `memory.cpp:140` (`if (handle->pins < 32)` guard); explanatory comment at `:141-142`; `mask \|= VPE_TO_VPP` at `:143`. Dead check confirmed absent (grep returns no matches). Cross-link `v1.0-INTEGRATION-CHECK.md` row 11. |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `pinouts.json` | 10 / 21 | `static-high-pins` only populated for DIP24_2716 and DIP24_2732; DIP28/DIP32 quirk pins (CE2 / JEDEC-tied NC) not declared | Info | Pre-existing — INFO-3 in the v1.0 audit; the wire mechanism is correct, only coverage data is missing. Carried in `follow_ups` (deferred to v1.2 as FW-07 in REQUIREMENTS.md Future Requirements). |
| `firestarter/src/proms/memory.cpp` | 140-143 | `pins < 32` guard predicate is structural (chip-package-pin-count based) rather than feature-flag based | Info | Pre-existing — the hardware constraint (VPE_TO_VPP and ADDRESS_LINE_16 share the same CONTROL bit) is inherently tied to pin-count, not a flag. Comment at `:141-142` documents the rationale. Not a defect. |

No new BLOCKER- or WARNING-level anti-patterns introduced by Phase 10.

---

### SC#4 Explicit Lock — `static_high_mask` end-to-end + `pins < 32` VPE_TO_VPP guard

This subsection records ROADMAP Phase 3 SC#4 — "10-VERIFICATION.md confirms `static_high_mask` end-to-end wiring and the `pins < 32` VPE_TO_VPP guard are intact in the current `memory.cpp`." Both items are verified above with direct `file:line` evidence:

- **`static_high_mask` 5-hop chain** (Key Link Verification table rows 1–5; Required Artifacts table; Data-Flow Trace table) traces the value from `pinouts.json:10`/`:21` through `database.py:get_bus_config:309-319` (pin-translation via `pin_conversions[24][24] = 13` at `:87`), into wire JSON `"static-high":[13]`, OR'd into `handle->bus_config.static_high_mask` at `json_parser.c:426` (init at `:84`), and applied to `reorg_address` at `memory.cpp:319` inside `mem_util_remap_address_bus` (function at `:226`). Wire-contract field declaration: `firestarter.h:72`.
- **`pins < 32` VPE_TO_VPP guard** (Truth #2; Required Artifacts): `memory.cpp:140` (`if (handle->pins < 32) {`) with the explanatory comment at `:141-142` and `mask |= VPE_TO_VPP` at `:143`, inside `mem_util_calculate_top_address_register:137`. The legacy dead `READ_WRITE == WRITE_FLAG` check is confirmed absent in current `memory.cpp` by direct grep (no matches as of 2026-05-12).

**Verdict:** REQ-FW-05 and REQ-FW-06 are SATISFIED. SC#4 is hereby locked: the 10-VERIFICATION.md record establishes that both wire-intactness conditions hold against the live source tree, with grep-verifiable `file:line` citations at every hop.

---

### Gaps Summary

REQ-FW-05 and REQ-FW-06 are SATISFIED against the current source tree. The 5-hop `static_high_mask` chain is intact end-to-end (verified by direct grep at all five hops on 2026-05-12); the `pins < 32` VPE_TO_VPP guard at `memory.cpp:140` is in place with the explanatory comment intact; the dead `READ_WRITE == WRITE_FLAG` check is confirmed absent. **SC#4 lock satisfied (see subsection above).**

One open follow-up carried forward: **INFO-3** — `pinouts.json` `static-high-pins` is only populated for the two DIP24 pinouts today; DIP28 and DIP32 quirk pins (second CE, JEDEC-tied NC pins) are not declared. The `static_high_mask` plumbing handles any pin populated upstream, so this is a coverage-extension item, not a wire defect. Deferred to v1.2 (FW-07 in REQUIREMENTS.md Future Requirements).

No `Cross-Milestone Closure` subsection: REQ-FW-05 and REQ-FW-06 were PARTIAL in v1.0 for verification-gap reasons only — both wires were always intact. No v1.1 work touched the static_high_mask path; this verification confirms the v1.0-as-shipped state is unchanged.

**Operator note:** `.planning/milestones/v1.0-phases/10-static-pins/10-CONTEXT.md` exists as a stray file in this phase directory (CONTEXT.md files normally live in the active phase dir under `.planning/phases/`). Phase 3 reads it for background on the `static_high_mask` rationale; does NOT move or delete it. Cleanup deferred per Phase 3 CONTEXT.md `<deferred>`.

---

_Verified: 2026-05-12T10:16:00Z_
_Verifier: Claude (gsd-verifier)_
