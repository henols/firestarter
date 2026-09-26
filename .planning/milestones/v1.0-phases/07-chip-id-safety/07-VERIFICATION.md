---
phase: 07-chip-id-safety
verified: 2026-05-12T10:13:00Z
status: passed
score: 3/3 must-haves verified
overrides_applied: 0
requirements_verified:
  - REQ-SAF-02
follow_ups:
  - source: v1.0-MILESTONE-AUDIT.md WARNING-5 (escalated by Phase 12)
    item: "AT28C256/64 family routes via algo=0x07 → configure_eprom, not the 0x0D handler. SAF-05's 28C chip-id check (eeprom_28c.cpp:55-77) is forward-compat ready but vacuous for the AT28C-family today (no 0x0D chip in DB has chip_id_value populated; AT28C256 doesn't reach 0x0D at all)."
    severity: warning
    in_scope: false
    note: "Deferred to v1.2 per MILESTONES.md. Closing the AT28C-family routing is an upstream-DB classification fix, not a chip-id-validation defect. SAF-05 forward-compat scope is satisfied."
---

# Phase 07: Chip ID Validation & Pre-Write Safety — Verification Report

**Phase Goal:** "Chip ID is read and validated before every write where the algorithm supports it." Concretely: each write_init handler (Intel-flash, UV-EPROM, AT28C — the 28C portion closed by v1.1 Plan 01-02 / SAF-05) reads the chip's manufacturer/device IDs, compares against `handle->chip_id` when non-zero, and aborts on mismatch with a consistent error format.
**Verified:** 2026-05-12T10:13:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `flash_intel_write_init` validates `handle->chip_id > 0` and dispatches to `flash_intel_check_chip_id` (Intel 28F autoselect: write 0x90, read mfr@0x0000 + device@0x0001, write 0xFF). | VERIFIED | `firestarter/src/proms/flash_intel.cpp:87` (`if (handle->chip_id > 0) { flash_intel_check_chip_id(handle); }`); `:152` (`flash_intel_check_chip_id` definition). Call-site at `:87` follows `flash_intel_check_vpp(handle)` at `:77` (SAF-04). Cross-link `v1.0-INTEGRATION-CHECK.md` REQ-SAF-02 wire-trace row. |
| 2 | `eprom_generic_init` handles the UV-EPROM chip-id branch when `handle->chip_id > 0`. | VERIFIED | `firestarter/src/proms/eprom.cpp:250` (`eprom_generic_init` entry); the function calls `eprom_check_vpp(handle)` at `:251` then proceeds to chip-id handling via the standard `firestarter_operation_main` dispatch (CMD_CHECK_CHIP_ID branch). UV-EPROM uses flash3-style chip-id read; reference logic at `flash_type_3.cpp::flash3_get_chip_id`. |
| 3 | `eeprom28c_write_init` validates `handle->chip_id > 0` and dispatches to `eeprom28c_check_chip_id` (A9-12V identification) BEFORE `EEPROM_SDP_DISABLE` is issued — REQ-SAF-02 28C portion, closed by v1.1 Plan 01-02 / SAF-05. | VERIFIED | `firestarter/src/proms/eeprom_28c.cpp:55-77` (`eeprom28c_check_chip_id` static helper definition — A9-12V identification, not JEDEC AA/55/90 — per STATE.md "D-05 override (SAF-05, load-bearing)"); `:82` (`if (handle->chip_id > 0)` gate); `:83` (`eeprom28c_check_chip_id(handle)` call); `:91` (`flash_execute_command(EEPROM_SDP_DISABLE)`) — call-site precedes SDP_DISABLE by 8 lines. Unity coverage: 4/4 PASS in `test_eeprom28c_chip_id/`. Cross-link `01-VERIFICATION.md` Truth #2 + Truth #4 + Post-Review Fixes CR-02. |

**Score:** 3/3 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/proms/flash_intel.cpp` | `flash_intel_check_chip_id` definition + call from `flash_intel_write_init` when `handle->chip_id > 0` | VERIFIED | Forward declaration at `:22`; definition at `:152`; call-site at `:87` (inside `flash_intel_write_init`, after `flash_intel_check_vpp` at `:77`). |
| `firestarter/src/proms/eprom.cpp` | UV-EPROM chip-id branch reachable from `eprom_generic_init` | VERIFIED | `eprom_generic_init:250` with unconditional `eprom_check_vpp` at `:251`; chip-id handled via standard `firestarter_operation_main` dispatch. |
| `firestarter/src/proms/eeprom_28c.cpp` | `eeprom28c_check_chip_id` static helper + call from `eeprom28c_write_init` gated on `chip_id > 0`, BEFORE SDP_DISABLE | VERIFIED | Helper at `:55-77` (A9-12V identification with CR-02 `mem_size < 64` underflow guard); gate at `:82`; call at `:83`; SDP_DISABLE at `:91`. Forward declaration at `:20`. |
| `firestarter/test/native/avr/test_eeprom28c_chip_id/` | Unity suite covering SAF-05 (matching / mismatching / zero-skip / FORCE) | VERIFIED | Directory exists; 4/4 PASS per `01-VERIFICATION.md` Truth #4. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `flash_intel_write_init:87` | `flash_intel_check_chip_id` (`flash_intel.cpp:152`) | Direct C call gated on `handle->chip_id > 0` | WIRED | Branch follows VPP check (`:77`); chip-id read uses Intel 28F 0x90 autoselect. |
| `eprom_generic_init:250` | UV-EPROM chip-id branch | `firestarter_operation_main` dispatch (CMD_CHECK_CHIP_ID) | WIRED | UV-EPROM chip-id path reuses flash3-style read; unconditional VPP check at `:251` precedes it. |
| `eeprom28c_write_init:83` | `eeprom28c_check_chip_id` (`eeprom_28c.cpp:55-77`) | Direct C call, gated on `chip_id > 0` at `:82`, BEFORE `flash_execute_command(EEPROM_SDP_DISABLE)` at `:91` | WIRED | Ordering: helper `:55`, gate `:82`, call `:83`, SDP_DISABLE `:91` — strictly ascending. SAF-05 closure. |
| `eeprom28c_check_chip_id` | `handle->firestarter_get_data` | Function-pointer dispatch (A9-12V identification with manufacturer/device read at `mfr_addr` and `mfr_addr + 1`) | WIRED | Mocked via `mock_get_data_scripted` in Unity suite (4/4 PASS). |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `database.py::_map_data` | `chip_id_value` | `programming.get("chip_id", 0)` (per-chip DB field) | Yes — populated for the chip families that publish IDs | FLOWING |
| `json_parser.c::parse_json` | `handle->chip_id` | `extract_int("chip_id", handle->chip_id)` | Yes — integer wire value lands on the firmware handle | FLOWING |
| Intel-flash `:87` | chip_id branch dispatched | Branch on `handle->chip_id > 0` | Yes — 39 algo=0x10 chips reach the check when ID is populated | FLOWING |
| UV-EPROM `eprom_generic_init` | chip_id branch dispatched | Standard `firestarter_operation_main` CMD_CHECK_CHIP_ID | Yes — flash3-style autoselect re-used | FLOWING |
| 28C `eeprom_28c.cpp:78-79` | chip_id branch dispatched | Branch on `handle->chip_id > 0`; A9-12V identification | Yes — forward-compat ready; vacuous today (no 0x0D entry in DB has `chip_id_value` populated; AT28C256 doesn't reach 0x0D — WARNING-5 caveat) | FLOWING |

---

### Behavioral Spot-Checks

(All commands cited from existing verification artifacts — Phase 3 does not re-run per CONTEXT.md D-09 / RESEARCH.md Pitfall #3.)

| Behavior | Command | Result | Cited From |
|----------|---------|--------|------------|
| 28C chip-ID check (SAF-05 matching / mismatching / zero-skip / FORCE) | `pio test -e native` (test_eeprom28c_chip_id) | 4/4 PASS | `01-VERIFICATION.md` Truth #4 |
| Full Phase 1 native suite (no regression after SAF-05 helper added) | `pio test -e native` | 25/25 PASS | `01-VERIFICATION.md` Behavioral Spot-Check |
| Intel-flash chip-id check linked into both AVR builds | `pio run -e uno` / `-e leonardo` | both SUCCESS | `12-VERIFICATION.md` Truth #7 |
| CR-02 regression: `mem_size < 64` underflow guard intact in `eeprom28c_check_chip_id` | `eeprom_28c.cpp:56-60` (inside helper at `:55-77`) | Guard present; `01-VERIFICATION.md` Behavioral Spot-Checks records this as PASS | `01-VERIFICATION.md` Post-Review Fixes |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-SAF-02 | 07-01 (v1.0); 28C portion closed by v1.1 Plan 01-02 / SAF-05 | Chip-ID read and validated before write across all handlers that support it: Intel-flash (autoselect 0x90), UV-EPROM (flash3-style), and AT28C (A9-12V via SAF-05). | SATISFIED | Intel: `flash_intel.cpp:87` (call) + `:152` (def). UV-EPROM: `eprom.cpp:250` (`eprom_generic_init`). 28C: `eeprom_28c.cpp:55-77` (helper, SAF-05) + `:82-83` (gate + call) + `:91` (SDP_DISABLE strictly after the check). Unity 4/4 PASS. **See Cross-Milestone Closure subsection below for the 28C SAF-05 closure narrative.** |

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `eeprom_28c.cpp` | 55-77 | A9-12V identification chosen over the AMD/SST JEDEC AA/55/90 sequence proposed in CONTEXT.md D-05 | Info | Pre-existing — STATE.md "D-05 override (SAF-05, load-bearing)" decision: JEDEC AA/55/90 would corrupt address 0x5555 on SDP-disabled AT28C parts. Datasheet evidence (`01-RESEARCH.md`) drove the override. Not a defect. |
| `eeprom_28c.cpp` | 60-64 | `if (handle->mem_size < 64)` underflow guard inside chip-id helper | Info | Pre-existing CR-02 fix — guards against AT28C256/64 small-memory underflow when deriving `mfr_addr`. Recorded in `01-VERIFICATION.md` Post-Review Fixes. |

No new BLOCKER- or WARNING-level anti-patterns introduced.

---

### Cross-Milestone Closure — REQ-SAF-02 (28C SAF-05 closure)

The v1.0 audit WARNING-2 flagged `eeprom_28c.cpp::eeprom28c_write_init` for ignoring `handle->chip_id` — a vacuous-today / forward-compat hazard. REQ-SAF-02 was PARTIAL at v1.0 milestone close because the 28C family path lacked chip-id validation entirely (Intel and UV-EPROM portions were SATISFIED).

**Closed by v1.1 Plan 01-02 (SAF-05):** `eeprom28c_check_chip_id` static helper at `firestarter/src/proms/eeprom_28c.cpp:55-77`, called from `eeprom28c_write_init` at line 83, gated on `handle->chip_id > 0` (line 82), and placed BEFORE `flash_execute_command(EEPROM_SDP_DISABLE)` at line 91. The helper performs A9-12V identification (NOT the AMD/SST JEDEC AA/55/90 sequence proposed in CONTEXT.md D-05 — per STATE.md "D-05 override (SAF-05, load-bearing)", JEDEC would corrupt address 0x5555 on SDP-disabled AT28C parts). The CR-02 regression fix at `:60-64` guards against `mem_size < 64` underflow when deriving the manufacturer-address. Unity coverage: 4/4 PASS in `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp`.

See `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md` Truth #2 + Truth #4 + Post-Review Fixes CR-02 for the canonical v1.1 verification record.

**Current source-tree state:** REQ-SAF-02 is SATISFIED across Intel + UV-EPROM + 28C families as of 2026-05-12. The 28C portion is forward-compat ready (no 0x0D chip in the DB has `chip_id_value` populated today; the AT28C256 family doesn't reach the 0x0D handler at all per WARNING-5 / upstream-DB classification — see `follow_ups`).

---

### Gaps Summary

REQ-SAF-02 is SATISFIED. SAF-05 closure (v1.1 Plan 01-02) discharges the 28C portion; Intel and UV-EPROM portions were always WIRED.

One open follow-up carried forward: **WARNING-5 (related variant)** — the AT28C256/64 family routes via `algo=0x07 → configure_eprom`, not the 0x0D handler. SAF-05's 28C chip-id check is therefore vacuous for AT28C today. Deferred to v1.2 per MILESTONES.md "Known Gaps" — upstream-DB classification fix, not a chip-id-validation defect. SAF-05 forward-compat scope (when a 0x0D chip publishes `chip_id_value`, the check fires correctly) is satisfied.

---

_Verified: 2026-05-12T10:13:00Z_
_Verifier: Claude (gsd-verifier)_
