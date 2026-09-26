---
phase: 105-fw-firmware-mem-type-removal
verified: 2026-07-02T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 105: FW — Firmware `mem_type` Removal Verification Report

**Phase Goal:** The firmware dispatches only on `handle->protocol` — the `mem_type` fallback chain is gone, `protocol == 0` fail-closes instead of silently falling back, and the wire no longer carries a `type` field for the firmware to parse.
**Verified:** 2026-07-02
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `protocol == 0` fail-closes to `configure_not_implemented()` (0xBB), no `mem_type` fallback (SC#1) | VERIFIED | `src/proms/memory.cpp` tail is one unconditional terminal `configure_not_implemented(handle);` with no `if` guard and no `mem_type` chain (read directly, lines 100-113). `test_protocol_zero_fail_closes_not_implemented` (native suite) asserts `RESPONSE_CODE_ERROR` + all-3-NULL op pointers for `protocol=0`; `pio test -e native -f "*test_not_implemented*"` passes (part of the 80/80 full-suite run below). |
| 2 | A host that still emits the `type` JSON field is silently ignored — the field is not parsed (SC#2 / WIRE-01, firmware-parse-side) | VERIFIED | `src/json_parser.c` `key_parsers[]` allowlist (10 entries) contains no `type`/`key_type` entry; `grep -c 'get_type\|key_type' src/json_parser.c` = 0. Unknown-field-skip is pre-existing parser behavior (unchanged), so a `type` key on the wire is a no-op. |
| 3 | `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) and `TYPE_*` constants are gone from firmware in the same commit as the dispatch deletion (SC#3 / FW-03) | VERIFIED | `grep -rn 'MSG_ERR_MEM_TYPE_UNSUPPORTED\|TYPE_EPROM\|TYPE_SRAM\|TYPE_FLASH_TYPE_3\|TYPE_FLASH_TYPE_4' firestarter/` → 0 hits repo-wide (checked src, include, AND `tools/catalog/messages.toml`, the codegen source of truth). Codegen `--check` on the canonical catalog confirms 64 messages, no drift, tree clean after regen. Landed across `0b7e65f` (dispatch+struct+parser) with a same-day drift-closing follow-up `96b93a9` (catalog+regenerated header) — both on the same branch before phase completion, so no orphaned dead constant survives in the delivered state. |
| 4 | Every currently-dispatchable DB chip still routes to its identical handler via `protocol` alone; removed fallback was dead (SC#4 / SAFE-01) | VERIFIED | `pio test -e native -f "*test_dispatch*"` passes (16/16, all `KNOWN_PROTOCOLS` arms unaffected). `firestarter_app/tools/check_dispatch.py` exits 0: "PASS: all 746 chips scanned; 736 supported... 0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations." |
| 5 | `handle->mem_type` removed from `firestarter_handle_t`; `json_parser.c` no longer extracts the `type` field (FW-02) | VERIFIED | `include/firestarter.h` — only `uint32_t protocol;` remains, no `mem_type` field (`grep -n "protocol\|mem_type"` returns exactly one line, the `protocol` field). `grep -rn 'mem_type' firestarter/src firestarter/include` → 0 hits. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/test/native/avr/test_not_implemented/test_not_implemented.cpp` | Net-new `test_protocol_zero_fail_closes_not_implemented` | VERIFIED | `grep -c 'test_protocol_zero_fail_closes_not_implemented'` = 2 (definition + `RUN_TEST` registration), exactly matching the acceptance criterion. Test passes as part of the green native suite. |
| `firestarter/src/proms/memory.cpp` | D-04 single terminal fail-closed exit | VERIFIED | Read directly: named-infeasibility arm (0x11/0x2A/0x2B/0x2C) unchanged, followed by unconditional `configure_not_implemented(handle);` with no guard — matches D-04 exactly. |
| `firestarter/include/firestarter.h` | `mem_type` field removed | VERIFIED | Confirmed via grep + direct read. |
| `firestarter/src/json_parser.c` | All 4 `type` touchpoints removed | VERIFIED | Forward decl, `key_type[]` PROGMEM string, `key_parsers[]` entry, `get_type()` body — all absent; `key_parsers[]` table now has 10 entries, none named `type`. |
| `firestarter/include/messages.h` + `firestarter/tools/catalog/messages.toml` | `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) removed from BOTH generated header and canonical catalog | VERIFIED | 0 hits in either file; codegen `--check` confirms no drift (64 messages, catalog valid). |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | Fallback test cases deleted | VERIFIED | `test_protocol_zero_with_mem_type_eprom_dispatches_eprom` and `test_unknown_protocol_with_unknown_mem_type_errors` both absent (0 hits). |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `configure_memory()` | `configure_not_implemented()` | single terminal unconditional call, no guard (D-04 collapse) | WIRED | Confirmed by direct source read — no `if (handle->protocol != 0)` condition remains; both `protocol == 0` and any unrecognized non-zero protocol share the same fall-through exit. |
| `json_parser.c` `key_parsers[]` allowlist | dropping `key_type`/`get_type` | table no longer contains a `type` entry, so an unknown `"type"` key is silently skipped by the pre-existing unknown-field-skip parser logic | WIRED | Table enumerated directly (10 entries, `key_algorithm` present, no `key_type`). |
| `firestarter_handle_t.mem_type` removal | forces `memory.cpp` dispatch reads + `json_parser.c` extract removal together | both removed in the same commit (`0b7e65f`) | WIRED | Confirmed — no dangling reference to the deleted field anywhere in `src`/`include`; native suite links cleanly (80/80 pass, proving no orphaned symbol references). |

### Behavioral Spot-Checks / Full Verification Commands Run

| Command | Result | Status |
|---------|--------|--------|
| `pio test -e native` (from `/workspaces/firestarter`) | 80/80 test cases succeeded, incl. `test_dispatch`, `test_not_implemented`, `test_messages`, all `test_val_*` golden traces | PASS |
| `pio run -e uno` | SUCCESS — Flash 71.9% (23178/32256 B), RAM 76.1% | PASS |
| `pio run -e leonardo` | SUCCESS — Flash 88.3% (25316/28672 B), RAM 78.0% | PASS |
| `grep -rn 'mem_type' src include` | 0 hits | PASS |
| `grep -rn 'MSG_ERR_MEM_TYPE_UNSUPPORTED\|TYPE_EPROM\|TYPE_SRAM\|TYPE_FLASH_TYPE_3\|TYPE_FLASH_TYPE_4' src include tools` | 0 hits (checked catalog too) | PASS |
| `grep -c 'get_type\|key_type' src/json_parser.c` | 0 | PASS |
| `grep -c '0xAE' src/boards/rurp_serial_utils.cpp` | 1 (CRC8 table byte, correctly untouched) | PASS |
| `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --target include/messages.h --language cpp --check` | "OK: catalog valid (64 messages, version 1)." — no drift, tree clean | PASS |
| `cd firestarter_app && python3 tools/check_dispatch.py` | Exit 0 — "PASS: all 746 chips scanned; 736 supported... 0 dispatch regressions; 0 consistency violations" | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| FW-01 | 105-01 | `protocol == 0` fail-closes to `configure_not_implemented()`; mem_type fallback chain deleted | SATISFIED | `memory.cpp` direct read + `test_protocol_zero_fail_closes_not_implemented` PASS |
| FW-02 | 105-01 | `mem_type` field removed from `firestarter_handle_t`; `json_parser.c` no longer extracts `type` | SATISFIED | grep 0 hits both files; native suite links (80/80) |
| FW-03 | 105-01 | `MSG_ERR_MEM_TYPE_UNSUPPORTED` (0xAE) + `TYPE_*` constants retired from firmware headers/messages in lockstep | SATISFIED | 0 hits in generated header AND canonical catalog; codegen `--check` confirms no drift |
| WIRE-01 | 105-01 | `type` field removed from host→firmware wire contract (firmware-parse-side, per ROADMAP Phase 105 goal/SC#2 scoping) | SATISFIED (parse-side only — see note below) | `key_parsers[]` allowlist has no `type` entry; unknown-field-skip verified structurally |

**Note on WIRE-01 scope:** `.planning/REQUIREMENTS.md` line 18's one-line summary states WIRE-01 as "the wire carries only `algorithm` as the dispatch key" and marks it `[x]` complete solely against Phase 105. Taken completely literally, this is not yet true today: `firestarter_app/firestarter/database.py:445` still emits a `"type": determined_type` key in every chip's command dict, which `eprom_operations.py`'s `command_dict = eprom_data_dict.copy()` carries onto the wire unchanged — the host has not stopped **sending** `type` yet. However, the authoritative contract for this verification is `.planning/ROADMAP.md`'s Phase 105 goal and Success Criteria, which correctly scope WIRE-01 to the **firmware-parse side only** ("the wire no longer carries a `type` field **for the firmware to parse**"; SC#2: "a hand-crafted JSON command including `type` is silently ignored... rather than acted on"). ROADMAP.md explicitly assigns "WIRE-01's emit-side removal" to Phase 106 (HOST-01/02, still `[ ]` Pending). Phase 105's own PLAN.md must_haves truth is phrased narrowly and correctly ("A host that still emits the type JSON field is silently ignored") and is fully met. This is a pre-existing wording-precision gap in REQUIREMENTS.md's summary sentence, not a Phase 105 code or scope gap — flagged here for awareness, not as a phase-105 blocker.

### Anti-Patterns Found

None. Scanned all 6 modified files (`memory.cpp`, `firestarter.h`, `json_parser.c`, `messages.h`, both native test files) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero hits. No debt markers introduced.

### Deferred / Known Follow-on Items (not gaps — explicitly out of Phase 105 scope, tracked in later phases)

| Item | Addressed In | Evidence |
|------|-------------|----------|
| Host still emits `type` on the wire (`database.py`, `eprom_operations.py`) | Phase 106 | ROADMAP Phase 106 goal: "The host never sends a `type` field..."; requirements HOST-01/HOST-02 Pending |
| `firestarter/CLAUDE.md` "Protocol Dispatch" section still describes the deleted steps 7–11 `mem_type` fallback chain and the `type` wire field as if they still exist | Phase 107 | ROADMAP Phase 107 SC#1: "`firestarter/CLAUDE.md`'s dispatch section no longer describes the removed steps 7-11..."; requirement DOC-01 Pending. Confirmed stale text present in current `firestarter/CLAUDE.md` (Protocol Dispatch section, steps 7-11, "no mem_type == 2" note, "type — legacy mem_type integer" wire-field table row) |
| `firestarter_app/tools/catalog/messages.toml` + `firestarter/firestarter/messages.py` (host mirror) still define `MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE` | Phase 106/107 | SUMMARY explicitly confirms this via grep; host-side is out of Phase 105's `files_modified` scope |

### Human Verification Required

None. All must-haves are verifiable programmatically via grep, direct source read, and passing automated test/build/tooling commands. No visual, real-time, or subjective-judgment items in this phase.

### Gaps Summary

No gaps. All 5 must-have truths verified against the actual codebase (not just SUMMARY claims): direct source reads of `memory.cpp`, `firestarter.h`, and `json_parser.c` confirm the dispatch collapse, struct-field removal, and parser-allowlist removal exactly as specified. All required greps return the expected zero/one counts. The full native test suite (80/80), both AVR builds (Uno + Leonardo), and the cross-repo `check_dispatch.py` (746 chips, 0 regressions) all pass. The codegen drift-check (`--check` against the canonical `messages.toml`) confirms zero drift, closing the gap that the SUMMARY itself documented finding and fixing mid-phase (commit `96b93a9`). The only notable finding is a pre-existing wording-precision issue in `REQUIREMENTS.md`'s WIRE-01 one-line summary (claims "wire carries only algorithm" against Phase 105 alone, when the full removal spans Phase 105+106) — this does not block Phase 105's actual, correctly-scoped ROADMAP goal, which is fully achieved.

---

_Verified: 2026-07-02_
_Verifier: Claude (gsd-verifier)_
