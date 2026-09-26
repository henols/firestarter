---
phase: 01-database-pipeline
verified: 2026-05-12T09:55:48Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-DB-01
  - REQ-DB-02
  - REQ-DB-03
  - REQ-DB-04
---

# Phase 01: Database Pipeline — Verification Report

**Phase Goal:** "Establish the canonical XML → JSON → wire-payload database pipeline so every chip in `minipro`'s upstream `infoic.xml` traverses a single deterministic translation chain ending in firmware-consumable wire fields. Drive `mem_type` from the upstream algorithm integer (no string-substring guessing), resolve DIP28 variants via a single map, surface VPP at the source in millivolts, and skip protocols the firmware doesn't implement."
**Verified:** 2026-05-12T09:55:48Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The host-side `_map_data` derives `mem_type` from the upstream `algorithm` integer via a single module-level lookup table (REQ-DB-01) | VERIFIED | `_ALGO_MEM_TYPE` table defined at `firestarter_app/firestarter/database.py:47-61` (13 D3 entries); `_map_data` reads `protocol_id = programming.get("algorithm", 0)` at `:390` then looks up `_ALGO_MEM_TYPE[protocol_id]` at `:395` (legacy substring fallback at `:397` only when algorithm absent) |
| 2 | DIP28 variants resolve to a single canonical pinout key via `DIP28_VARIANT_MAP` (REQ-DB-02) | VERIFIED | `DIP28_VARIANT_MAP` at `firestarter_app/tools/build_db.py:93` (the variant lookup table); resolution call at `:120` (`key = DIP28_VARIANT_MAP.get(variant & 0xFF, "DIP28_2764")`) — every DIP28 chip from `infoic.xml` lands on a deterministic pinout entry |
| 3 | VPP is surfaced at source as integer millivolts (REQ-DB-03) | VERIFIED | `VPP_MV` table at `firestarter_app/tools/build_db.py:82`; written to chip JSON as `"vpp_mv": VPP_MV.get(voltages & 0xFF, 0)` at `:256`; consumed by `_map_data` at `database.py:387` (`vpp_mv = electrical.get("vpp_mv", 0)`); emitted on the wire at `database.py:518` (`"vpp_mv": vpp_mv`). Closes WARNING-3 — see Cross-Milestone Closure below. |
| 4 | Unknown / unimplemented upstream protocols are skipped at build time (REQ-DB-04) | VERIFIED | `KNOWN_PROTOCOLS` set at `firestarter_app/tools/build_db.py:89` (13 entries: {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39}); guard at `:204` (`if proto_id not in KNOWN_PROTOCOLS:`) skips the chip before any JSON emission. Matches the firmware's `memory.cpp` algorithm-first dispatch list verbatim (Phase 12 `12-VERIFICATION.md` Truth #1). |

**Score:** 4/4 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/tools/build_db.py` | Sole upstream XML → JSON pipeline emitting algorithm + vpp_mv + DIP28 pinout key; skipping unknown protocols | VERIFIED | Constants `MINIPRO_XML_URL` at `:10`, `OUTPUT_FILE` at `:12` (target = `chip_database.json` per Phase 11 / CLEAN-01 rename); `VPP_MV` `:82`, `KNOWN_PROTOCOLS` `:89`, `DIP28_VARIANT_MAP` `:93`; WARNING-5 inline override block at `:221-247` (per-chip `0x07 → 0x0D` flip for AT28C256/64 — Phase 13 closure) emits `INFO:` line at `:243`. |
| `firestarter_app/firestarter/database.py` | Host-side mapper reading algorithm-first, emitting `vpp_mv` on the wire, preserving upstream-schema READ at `electrical.get("vpp")` | VERIFIED | `_ALGO_MEM_TYPE` at `:47-61`; `_map_data` at `:370+`; upstream-schema READ preserved at `:375` (`vpp_str = electrical.get("vpp", "0").replace("V", "")`) — intentional per Plan 02-02 D-08-compat (consumes the upstream `"vpp"` *volts* string, NOT the post-WIRE-01 firmware wire key). Wire emitter at `:518` writes `"vpp_mv"` only. |
| `firestarter_app/firestarter/data/chip_database.json` | Generated DB (renamed by Phase 11 CLEAN-01 from `minipro_complete_db.json`); 743 chips | VERIFIED | File exists; size ~335KB; consumed by `database.py:189` (`"chip_database.json"`); regenerated successfully by `build_db.py` (cited from `12-VERIFICATION.md` Truth #4 — 743 chips, 52 SRAM-tagged). |

All artifacts: VERIFIED.

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `build_db.py:KNOWN_PROTOCOLS` (`:89`) | `memory.cpp:configure_memory` protocol-prefix dispatch | identity of the 13-element set | WIRED | Phase 12 `12-VERIFICATION.md` Truth #1 confirms `memory.cpp` lines 72-101 dispatch on the same 13 protocol values. `check_dispatch.py` PASS on 743 chips re-verifies the wire round-trip (cited from `02-VERIFICATION.md` SC4). |
| `build_db.py:VPP_MV` (`:82`) | `database.py:_map_data` (`:387`) | upstream JSON `electrical.vpp_mv` field | WIRED | `build_db.py` writes `"vpp_mv": VPP_MV.get(voltages & 0xFF, 0)` at `:256`; `database.py` reads `vpp_mv = electrical.get("vpp_mv", 0)` at `:387`. End-to-end integer-mV propagation. |
| `database.py:_map_data` (`:518`) | `json_parser.c:get_vpp_mv` (`firestarter/src/json_parser.c:503-497`) | wire JSON key `"vpp_mv"` | WIRED | Python emitter at `database.py:518` writes `"vpp_mv": vpp_mv`. Firmware parser PROGMEM literal at `json_parser.c:62`, dispatch table row at `:74`, getter at `:308-310` reads into `handle->vpp_mv`. Atomic three-site flip landed in v1.1 Plan 02-01 — see Cross-Milestone Closure. |
| `build_db.py:DIP28_VARIANT_MAP` (`:93`) | `database.py:get_bus_config` pin-resolution path | shared `pinout_key` field on each chip | WIRED | `build_db.py:120` resolves a DIP28 variant to a canonical key (e.g. `DIP28_2764`); `database.py:get_bus_config` (called from `_map_data`) looks the key up in `pinouts.json` and translates pin numbers via `pin_conversions` (`database.py:68+`). Single pinout-key contract. |
| `build_db.py:204` (skip unknown protocols) | `database.py:_ALGO_MEM_TYPE` (`:47-61`) | identity of the protocol set | WIRED | `KNOWN_PROTOCOLS` at `build_db.py:89` and `_ALGO_MEM_TYPE` at `database.py:47-61` both enumerate the same 13 D3 algorithm integers. Mismatch would produce `mem_type=None` at host or unmappable chips in DB. Both confirmed identical via `12-VERIFICATION.md` Truth #2. |

---

### Data-Flow Trace (Level 4)

| Hop | Artifact | Data Variable | Source | Produces Real Data | Status |
|-----|----------|---------------|--------|---------------------|--------|
| 1 | `MINIPRO_XML_URL` | `infoic.xml` text | upstream gitlab.com fetch (`build_db.py:159`) | Yes — 743 chips per `12-VERIFICATION.md` Truth #4 | FLOWING |
| 2 | `build_db.py` | per-chip JSON entry | XML parse + `KNOWN_PROTOCOLS` skip + `VPP_MV` lookup + `DIP28_VARIANT_MAP` resolve | Yes — emits to `chip_database.json` at `:277` | FLOWING |
| 3 | `chip_database.json` | persistent DB | `build_db.py` writer | Yes — 335KB file at `firestarter_app/firestarter/data/chip_database.json` | FLOWING |
| 4 | `database.py:_map_data` | wire payload dict | reads `chip_database.json`, applies `_ALGO_MEM_TYPE[protocol_id]`, copies `vpp_mv` through | Yes — confirmed via `check_dispatch.py` PASS in `02-VERIFICATION.md` SC4 | FLOWING |
| 5 | wire JSON `"vpp_mv": NNNN` | firmware-facing payload | `database.py:518` emitter | Yes — `json_parser.c:503-497` `extract_int("vpp_mv", handle->vpp_mv)` populates `handle->vpp_mv` from this exact key | FLOWING |

End-to-end: upstream XML voltage code → integer mV → wire `"vpp_mv"` → firmware `handle->vpp_mv`. No string parsing on the firmware side, no float arithmetic past the host boundary.

---

### Behavioral Spot-Checks

(All commands cited from existing verification artifacts — Phase 3 does not re-run per CONTEXT.md D-09 / RESEARCH.md Pitfall #3.)

| Behavior | Command | Result | Cited From |
|----------|---------|--------|------------|
| `check_dispatch.py` PASS on full 743-chip DB (round-trip wire + dispatch) | `python3 firestarter_app/tools/check_dispatch.py` | exit 0 — "PASS: all 743 chips have a valid dispatch path" | `12-VERIFICATION.md` Truth #5 + `02-VERIFICATION.md` SC4 (post-WIRE-01 + WIRE-02 augmentation) |
| `_ALGO_MEM_TYPE` import + 13-entry parity with build_db.py KNOWN_PROTOCOLS | `python3 -c "from firestarter.database import _ALGO_MEM_TYPE; ..."` | 13 entries, exact D3 match | `12-VERIFICATION.md` Truth #2 + Behavioral Spot-Check row |
| Spot-check W27C512 (algo=0x07) → mem_type=1 | `db.get_eprom('W27C512')` | type=1 | `12-VERIFICATION.md` Behavioral Spot-Check row |
| Spot-check AM29F040 (algo=0x06) → mem_type=3 | `db.get_eprom('AM29F040')` | type=3 | `12-VERIFICATION.md` Behavioral Spot-Check row |
| Build clean (Uno + Leonardo) — implies the wire contract `database.py` emits is the one `json_parser.c` reads | `pio run -e uno`, `pio run -e leonardo` | both SUCCESS | `12-VERIFICATION.md` Truth #7 + `01-VERIFICATION.md` (v1.1) |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-DB-01 | 01-01, 01-02, 01-03 | Algorithm-first `mem_type` derivation | SATISFIED | `_ALGO_MEM_TYPE` table at `database.py:47-61`; lookup at `_map_data:395` via `protocol_id = programming.get("algorithm", 0)` at `:390`. 13/13 KNOWN_PROTOCOLS covered. Phase 12 closed BLOCKER-1 reachability; reachability confirmed by `check_dispatch.py` PASS on 743 chips. |
| REQ-DB-02 | 01-01..03 | DIP28 variant resolution via single map | SATISFIED | `DIP28_VARIANT_MAP` at `build_db.py:93`; resolved at `:120`. Every DIP28 chip in `chip_database.json` carries a canonical `pinout_key` consumable by `database.py:get_bus_config`. |
| REQ-DB-03 | 01-01..03 | VPP at source in millivolts | SATISFIED | `VPP_MV` `build_db.py:82` → DB `vpp_mv` `:256` → `database.py` read `:387` → wire emit `:518` → firmware `json_parser.c:503-497` into `handle->vpp_mv`. WARNING-3 closed by v1.1 Plan 02-01 (WIRE-01); see Cross-Milestone Closure. |
| REQ-DB-04 | 01-01..03 | Unknown protocols skipped at build | SATISFIED | `KNOWN_PROTOCOLS` `build_db.py:89` + skip guard `:204`. Verified parity with firmware dispatch via `12-VERIFICATION.md` Truth #1; no orphan chips can reach `configure_memory` with an unrecognised protocol. |

All four declared requirements SATISFIED against the current source tree.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `firestarter_app/firestarter/database.py` | 375 | `electrical.get("vpp", "0")` (legacy upstream-schema READ) | Info | INTENTIONAL — per Plan 02-02 D-08-compat: this reads the upstream `chip_database.json` `electrical.vpp` *volts* string (pre-WIRE-01 schema artifact retained for `vpp_volts` internal-dict construction at `:417`). Does NOT participate in the wire payload. Wire emitter at `:518` writes only `"vpp_mv"`. Not a defect. |
| `firestarter_app/tools/build_db.py` | 158-163, 179-186 | bare `except:` blocks; missing `requests.raise_for_status()`/`timeout` | Info | Pre-existing in upstream `parse_db_2.py`; not Phase-01-introduced. Carried as `follow_ups` in `11-VERIFICATION.md`. Out of Phase 3 scope. |

No BLOCKER or WARNING level anti-patterns introduced by Phase 01. WARNING-5 (AT28C256/64 12V-on-/WE hazard) is an upstream-DB classification issue closed at the data layer by Phase 13 via the inline override block at `build_db.py:221-247`; broader generalization deferred to v1.2 per `MILESTONES.md` Known Gaps.

---

### Cross-Milestone Closure — REQ-DB-03 (WIRE-01 wire-key rename)

REQ-DB-03 was PARTIAL in v1.0 due to WARNING-3 (`v1.0-MILESTONE-AUDIT.md`): the firmware wire key `"vpp"` was overloaded — it carried millivolts but was named like a volts string, risking silent unit confusion if anyone consumed it via a generic JSON adapter.

**Closed by v1.1 Plan 02-01 (WIRE-01):** atomic three-site firmware flip in `firestarter/src/json_parser.c` (PROGMEM literal at `:62`, dispatch-table row at `:74`, `extract_int` macro arg at `:309`) plus the Python emitter rename at `firestarter_app/firestarter/database.py:518`. Both sides land together in a paired sub-repo commit pair — firmware `firestarter@39b29a9` and app `firestarter_app@20cfe86` — see `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-01-SUMMARY.md` for the atomic-flip narrative and `02-VERIFICATION.md` Observable Truths #1 + #4 for the live grep evidence.

Current source tree emits only `"vpp_mv"` on the wire (`database.py:518`) and reads only `"vpp_mv"` in the firmware parser (`json_parser.c:62/:74/:309`). The upstream-schema READ `electrical.get("vpp", "0")` at `database.py:375` is preserved intentionally — it consumes the upstream `chip_database.json` *volts* string for internal `vpp_volts` arithmetic and is unrelated to the wire key.

**Verdict:** REQ-DB-03 is SATISFIED as of 2026-05-12.

---

### Gaps Summary

No gaps. All four Phase 01 requirements (REQ-DB-01..04) score SATISFIED against the current source tree. WARNING-3 (REQ-DB-03 wire-key overloading) is closed via v1.1 Plan 02-01 (WIRE-01) — see Cross-Milestone Closure subsection above. WARNING-5 (AT28C256/64 upstream-DB classification) is data-layer-closed by Phase 13 inline override at `build_db.py:221-247`; broader override-table generalization deferred to v1.2. Neither carries a Phase-01-scoped follow-up.

---

_Verified: 2026-05-12T09:55:48Z_
_Verifier: Claude (gsd-verifier)_
