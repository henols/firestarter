# Phase 77: Erase Write-Path Graduation (0x07 EE-EPROMs) - Research

**Researched:** 2026-06-21
**Domain:** Host-only flag wiring (`firestarter_app/firestarter/database.py`) + read-only firmware confirmation (`firestarter/src/proms/eprom.cpp`, `eeprom_28c.cpp`)
**Confidence:** HIGH — all five open questions answered by reading live code + running the actual code path; no assumptions needed for the core implementation decisions

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** `FLAG_CAN_ERASE` is wired from the **canonical erase-capability ground truth** — the infoic.xml `flags & 0x10` (`MP_ERASE_MASK`) — which `build_db.py` already decodes into `electrical.type`. Wire it off `electrical.type`, NOT a `protocol_id` heuristic and NOT the raw runtime `info-flags` field.
- **D-02:** Set the flag for **all erasable types** — `electrical.type in {"EEPROM", "Flash/EEPROM"}` (operator decision: uniform with the mask semantics). This matches the existing `_map_data` keying (`database.py:434`). The flag only changes firmware behavior on the `configure_eprom` (0x07/0x08/0x0B) path; on the 0x0D `configure_eeprom28c` path it is expected to be **inert** (that handler manages its own erase).
- **D-03 (downstream verify — MANDATORY):** Because D-02 now also sets the flag on the 0x0D `Flash/EEPROM` parts, the researcher/planner MUST confirm the firmware `configure_eeprom28c` path genuinely **ignores** `FLAG_CAN_ERASE` (no double-erase, no VPP/behavior change, no hazard for 28C-family chips). If it does NOT ignore it, narrow the scope back to the `configure_eprom` EEPROMs only and record why.
- **D-04:** Bench proof = a **single** write→auto-erase→program→verify cycle per SC#2 (N≥5 NOT required here): one `firestarter write` (no `-b`) of a **non-blank** real W27C512 on Leonardo, an independent post-write full read that SHA-matches the source file, and a **non-vacuous negative control** (a wrong-file verify exits non-zero). Standing bench precondition applies.
- **D-05:** SAFE-01's host-guard removal is **N/A-no-refusal** here — the chips are already `supported`, so there is no `chip_resolver.resolve_chip` refusal to drop. Document this explicitly so downstream agents do not hunt for / fabricate a refusal. The evidence-gated "FINAL step" that the SAFE discipline protects is instead the **`FLAG_CAN_ERASE` wiring itself** — it lands only after the native + wire round-trip + Leonardo bench evidence is on record.
- **D-06:** SAFE-02 (full-DB `check_dispatch.py` VPP-safety gate green after the change) and SAFE-03 (firmware↔host constant parity if any `FLAG_*`/protocol constant in `constants.py` ↔ `firestarter.h` is touched, parity tests green) **still fully apply**.
- **D-07:** Add an explicit **host-side regression test** asserting the default (no `-b`) auto-erase write path keeps `ack_data=False` on INIT/END DATA frames, so the 2026-06-17 0xA4 desync cannot silently return. Plus a bench note confirming the no-`-b` write completes clean (the SC#2 cycle doubles as the live proof).

### Claude's Discretion

- Exact placement/shape of the `convert_to_programmer` edit and the regression test (file, fixture style) — planner's call, consistent with existing patterns.

### Deferred Ideas (OUT OF SCOPE)

- None — discussion stayed within phase scope. (Phases 78–80 cover the other three v1.14 gaps; v1.9 covers the read-bug RCA.)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ERASE-01 | Writing a W27C512-class EE-EPROM auto-erases before programming — `FLAG_CAN_ERASE` wired from `electrical.type=="EEPROM"` in `convert_to_programmer` | RF-01: flag is already being set via the synthetic `info-flags` round-trip (CONFIRMED); the fix is to make the derivation explicit from `electrical-type`, not to add new plumbing — the wiring itself already works |
| ERASE-02 | write→auto-erase→program→verify cycle bench-confirmed on Leonardo with real W27C512 (14V erase-rail chip-OUT VPP dry-run first, under ceiling) | Firmware erase path confirmed working (Phase 73 A2-CONFIRMED); 14V rail is VPE without the dropping resistor (read ROADMAP §SC#3 + Phase 72 research) |
| SAFE-01 | Host-guard refusal removed only as FINAL step after all evidence is on record | N/A-no-refusal for Phase 77: all 8 chips already `support_status: supported`, `chip_resolver.resolve_chip` does NOT refuse them (CONFIRMED by live run) |
| SAFE-02 | `check_dispatch.py` full-DB VPP-safety gate passes after change | `check_dispatch.py` currently PASSES (744 chips, 0 violations); this phase touches `convert_to_programmer` flag derivation, NOT the dispatch sim — gate should remain green; must be re-run and confirmed after edit |
| SAFE-03 | Firmware↔host `FLAG_*` constant parity preserved; parity tests green | `FLAG_CAN_ERASE = 0x02` in both `constants.py` (line 80) and `firestarter.h` (line 60); this phase does NOT touch either constant (we read the flag, not redefine it); `test_revision_constants_parity.py::test_flag_values_match_firmware` is the parity test — must confirm still green post-edit |
</phase_requirements>

---

## Summary

Phase 77 is a small, precise host-only change with a well-defined edit site: `convert_to_programmer` in `firestarter_app/firestarter/database.py` (~line 595). The goal is to make the `FLAG_CAN_ERASE` derivation **explicit and canonical** — reading `electrical-type` directly rather than relying on the fragile synthetic `info-flags` round-trip that happens to work today.

**The most important research finding (RF-01):** `FLAG_CAN_ERASE` is **already being set** on the wire for all 8 target EE-EPROMs today. The current code path works: `_map_data` (line 434) injects `info_flags |= 0x10` for `electrical.type in ("EEPROM", "Flash/EEPROM")`, and `convert_to_programmer` (line 597) reads `info-flags & 0x10` → sets `FLAG_CAN_ERASE = 0x02`. Live execution confirms `W27C512` receives `flags=0x2` in the converted programmer dict. The ROADMAP's "always-zero" description was a wording trap referring to a hypothetical path that was already fixed — not the current code state.

**The fix is therefore a code-quality/canonicality change, not a behavioral change.** The planner should frame the implementation task as: replace the `info-flags & 0x10` read in `convert_to_programmer` with a direct check on `electrical-type`, so the derivation survives any future refactor that touches the synthetic `info_flags` assembly in `_map_data`. This also satisfies D-01 (canonical ground truth, not indirection).

**D-03 (CONFIRMED SAFE):** `configure_eeprom28c` (`eeprom_28c.cpp`) does not read `FLAG_CAN_ERASE` anywhere. It uses only `FLAG_FORCE` and `FLAG_SKIP_BLANK_CHECK`. Setting `FLAG_CAN_ERASE` on 0x0D `Flash/EEPROM` chips has zero firmware effect on that handler. D-02's "set for all erasable types" is safe to implement without narrowing scope.

**Primary recommendation:** Edit `convert_to_programmer` (~line 595–600) to derive `FLAG_CAN_ERASE` from `full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM")` instead of `info-flags & 0x10`. Add a targeted test asserting this derivation for a W27C512 (EEPROM), an AT28C256 (Flash/EEPROM), and a UV-EPROM control. Then bench-prove the no-`-b` write auto-erase cycle on Leonardo.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| FLAG_CAN_ERASE flag derivation | Host API (database.py) | — | `convert_to_programmer` assembles the wire JSON; this is where flag bits are set before serial dispatch |
| Auto-erase execution | Firmware (`eprom.cpp`) | — | `eprom_write_init` already consumes the flag and calls `eprom_internal_erase`; no change needed |
| VPP/erase voltage rail | Firmware hardware layer | — | `CTRL_VPP_REGULATOR_ENABLE` without drop resistor = full VPE rail (nominally ~14V for W27C512); firmware owns rail control |
| Wire round-trip correctness | Host + Firmware | — | `check_dispatch.py` simulates dispatch; native recording-stub test verifies flag propagation |
| Bench proof (ERASE-02) | Hardware bench | — | Leonardo + W27C512 + operator; `autonomous: false` for VPP multimeter dry-run |

---

## Standard Stack

### Core (no new packages)

| File | Purpose | Edit Type |
|------|---------|-----------|
| `firestarter_app/firestarter/database.py` | `convert_to_programmer` flag derivation | Edit — 1 condition change (~line 595–599) |
| `firestarter_app/tests/test_database_conversion.py` | Existing convert_to_programmer tests | Add — new `test_convert_w27c512_flag_can_erase` and UV-EPROM negative control |
| `firestarter_app/tests/test_eprom_database.py` or `test_eprom_operations.py` | `ack_data=False` regression test | Add — D-07 assertion |

No new third-party packages. No firmware changes.

**Installation:** none needed.

---

## Open Question RF-01 — ANSWERED

### RF-01: Is FLAG_CAN_ERASE Already Set on the Wire for W27C512 Today?

**Answer: YES — CONFIRMED by running the live code path.**

**Trace (CONFIRMED by code read + live execution):**

1. `build_db.py` Pass-2 (lines 629–638): for `proto_id in {0x07, 0x08, 0x0B}`, if `flags & 0x10` → `_etype = "EEPROM"`. W27C512 has `flags & 0x10` set in infoic.xml → stored as `electrical.type = "EEPROM"` in `chip_database.json`. [CONFIRMED: live DB query]

2. `database.py _map_data` (line 434): `if electrical.get("type") in ("EEPROM", "Flash/EEPROM"): info_flags |= 0x00000010`. W27C512's `electrical.type = "EEPROM"` → `info_flags bit 0x10` is SET. [CONFIRMED: read source]

3. `database.py convert_to_programmer` (lines 595–599): `if full_eprom_data.get("info-flags", 0) & 0x00000010: simple_flags |= FLAG_CAN_ERASE`. W27C512's `info-flags = 0x30` → bit 0x10 is set → `simple_flags = 0x02` (FLAG_CAN_ERASE). [CONFIRMED: read source]

4. Live execution result (run 2026-06-21):
   ```
   W27C512  electrical-type=EEPROM  info-flags=0x30  info-flags & 0x10 = 0x10
   convert_to_programmer flags = 0x2  FLAG_CAN_ERASE=True
   ```

5. `chip_resolver.resolve_chip("W27C512", db)` → RESOLVED, `flags=0x2`. [CONFIRMED: live run]

**All 8 target chips confirmed (live execution):**

| Chip | electrical-type | info-flags | FLAG_CAN_ERASE set? | algorithm |
|------|----------------|-----------|---------------------|-----------|
| W27C512 | EEPROM | 0x30 | True (0x02) | 0x07 |
| W27E512 | EEPROM | 0x30 | True (0x02) | 0x07 |
| W27C257 | EEPROM | 0x30 | True (0x02) | 0x07 |
| W27E257 | EEPROM | 0x30 | True (0x02) | 0x07 |
| SST27SF256 | EEPROM | 0x30 | True (0x02) | 0x07 |
| SST27SF512 | EEPROM | 0x30 | True (0x02) | 0x07 |
| SST27VF256 | EEPROM | 0x30 | True (0x02) | 0x07 |
| SST27VF512 | EEPROM | 0x30 | True (0x02) | 0x07 |

**UV-EPROM control (flag correctly absent):**

| Chip | electrical-type | FLAG_CAN_ERASE set? |
|------|----------------|---------------------|
| M27C512 | UV-EPROM | False |
| 27C256 | UV-EPROM | False |

**Implication for ERASE-01:** The wiring already works. The task is to make it explicit and canonical (read `electrical-type` directly), not to fix a broken path.

**Implication for ROADMAP premise:** The ROADMAP's "always-zero `info-flags & 0x10`" phrasing was inaccurate — it referred to an older state predating the Phase 60 `_map_data` fix that added `"EEPROM"` to the `info_flags |= 0x10` condition. The current code already injects the bit correctly.

---

## Open Question D-03 — ANSWERED

### D-03: Does configure_eeprom28c (0x0D) Read FLAG_CAN_ERASE?

**Answer: NO — CONFIRMED. The flag is completely inert on the 0x0D path.**

**Evidence (CONFIRMED: read `firestarter/src/proms/eeprom_28c.cpp` in full):**

`configure_eeprom28c` (`eeprom_28c.cpp`, line 35) switches on `handle->cmd`. For `CMD_WRITE` it sets `handle->firestarter_operation_init = eeprom28c_write_init`. The `eeprom28c_write_init` function (line 97) calls:
1. `eeprom28c_check_chip_id` (uses `FLAG_FORCE` only)
2. `flash_execute_command(EEPROM_SDP_DISABLE)` — fixed 6-byte SDP-disable sequence
3. `eeprom28c_wait_for_write` — polling loop
4. `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))` — reads `FLAG_SKIP_BLANK_CHECK` only

`is_flag_set(FLAG_CAN_ERASE)` is **never called** in `eeprom_28c.cpp`. The AT28C28c handler manages its own write-enable protocol via the SDP-disable sequence; it does not engage the VPP regulator (`CTRL_VPP_REGULATOR_ENABLE` never set), and has no concept of a pre-erase step controlled by `FLAG_CAN_ERASE`.

**Verdict:** D-02 (set FLAG_CAN_ERASE for all `"EEPROM"` + `"Flash/EEPROM"` types) is **safe to implement without scope narrowing**. Setting `FLAG_CAN_ERASE` on 0x0D `Flash/EEPROM` chips (AT28C256, AT28C64, etc.) has zero firmware behavior change.

---

## Open Question (eprom_write_init + Erase Voltage)

### Firmware: How eprom_write_init Consumes FLAG_CAN_ERASE

**CONFIRMED by reading `firestarter/src/proms/eprom.cpp`:**

`eprom_write_init` (line 93):
```cpp
void eprom_write_init(firestarter_handle_t* handle) {
    if (!is_operation_in_progress(handle)) {
        eprom_generic_init(handle);         // eprom_check_vpp + chip-id verify
        if (handle->response_code == RESPONSE_CODE_ERROR) { return; }

        if (is_flag_set(FLAG_CAN_ERASE)) {
            if (!is_flag_set(FLAG_SKIP_ERASE)) {
                eprom_internal_erase(handle);   // <-- fires when FLAG_CAN_ERASE set
            } else {
                LOG_INFO_ID(MSG_INFO_SKIPPING_ERASE);
            }
        }
    }
    if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) {
        mem_util_blank_check(handle);       // fires AFTER erase
    }
}
```

**Erase voltage / rail (CONFIRMED by reading `eprom_internal_erase`, line 274):**

`eprom_internal_erase` enables `CTRL_VPP_REGULATOR_ENABLE` (without `CTRL_VPP_VPE_DROP_ENABLE`), then asserts `CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE`. This routes the unregulated VPE/VPP boost rail (no dropping resistor) to A9 and VPE simultaneously, producing the higher voltage the W27C512 datasheet specifies for erase (14V OE/VPP and A9=14V) vs. the lower programming voltage (12V via the drop resistor).

**VPP values in chip_database.json for the 8 chips (CONFIRMED: live DB query):**
- W27C512, W27E512, W27C257, SST27SF*: `vpp_mv = 12000` (programming VPP)
- W27E257: `vpp_mv = 13500`

The `vpp_mv` field controls the write-path VPP check via `eprom_check_vpp`. The erase path uses the full unregulated rail (physically ~14V on a well-calibrated shield) — the ROADMAP SC#3 "14V erase-rail chip-OUT VPP multimeter dry-run" refers to measuring the unregulated VPE output, which is higher than the `vpp_mv` setpoint.

**Safety:** 14V is well within the 22V ceiling (`RURP_VPP_CEILING_MV = 22000`). The firmware erase path is firmware-side only; host sends `FLAG_CAN_ERASE` in the `flags` field of the wire JSON command; the firmware then decides when to call `eprom_internal_erase`.

---

## Open Question D-07 — ANSWERED

### 0xA4 Regression: Where ack_data=False Is Set and Test Surface

**The fix (commit fcf7974, 2026-06-17) lives in `firestarter_app/firestarter/eprom_operations.py`.**

**Location (CONFIRMED: read source):** `_execute_phase` (line 347):

```python
def _execute_phase(self, phase_name: str, progress: ClassProgressHandler) -> Optional[str]:
    """Executes a single phase (INIT or END) of the state machine."""
    self.comm.send_ack()
    ...
    while True:
        response = self.comm.get_response()
        if response.type == phase_name:
            break
        ...
        # INIT/END phases: render DATA progress frames but do NOT ack them.
        # #write-empty-input-regression (Option C): ...
        self._handle_progress_response(response, progress, ack_data=False)  # <-- line 372
```

The `ack_data=False` is passed on line 372, inside `_execute_phase`, which handles both INIT and END phases. The `_handle_progress_response` helper (line 376) only calls `self.comm.send_ack()` if `ack_data=True` (line 397). MAIN phase callers use `ack_data=True` (default, line 419).

**Does auto-erase change the INIT sequence in a way that could re-trigger desync?**

When `FLAG_CAN_ERASE` is set, `eprom_write_init` calls `eprom_internal_erase` before the blank check. This erase step is handled entirely inside the firmware INIT phase — the firmware emits `MSG_DATA_PROGRESS` frames during the blank check portion of INIT, not during the erase itself (erase is a single pulse sequence with no per-chunk feedback). The host receives only DATA progress frames from the blank check sub-step. Since `_execute_phase` already passes `ack_data=False` for ALL DATA frames in INIT (line 372), the fix is already in place for the auto-erase write path.

**Risk:** Minimal. The 0xA4 regression path requires a series of spurious acked DATA frames in INIT to pile up in the firmware RX buffer. The fix unconditionally sets `ack_data=False` for all DATA frames during INIT/END — it does not depend on whether auto-erase is active.

**Recommended regression test surface (D-07):**

- **File:** `firestarter_app/tests/test_eprom_operations.py`
- **Pattern:** Existing test `test_eprom_operations.py` tests mock `EpromOperator` with a fake serial. Add a test that exercises `_execute_phase("INIT", ...)` with a mock that returns a sequence of DATA responses followed by INIT, and asserts `send_ack()` is called exactly once (for the initial ACK that starts the phase), NOT for each DATA frame.
- **Alternative site:** `tests/test_serial_comm.py` if the test is simpler at the comm layer.
- **Closest analog:** Search `test_eprom_operations.py` for `write_cycle` or `_execute_phase` tests using `MagicMock` / `fake_serial`.

---

## Open Question SAFE-01/02/03 — ANSWERED

### SAFE-01: Support Status and chip_resolver Behavior for the 8 Chips

**CONFIRMED by live run of `chip_resolver.resolve_chip` for all 8 chips:**

All 8 target EE-EPROMs are `support_status: supported` in `chip_database.json`. `chip_resolver.resolve_chip` does NOT refuse any of them. Results:

```
W27C512    RESOLVED  algo=0x7  flags=0x2
W27E512    RESOLVED  algo=0x7  flags=0x2
W27C257    RESOLVED  algo=0x7  flags=0x2
W27E257    RESOLVED  algo=0x7  flags=0x2
SST27SF256 RESOLVED  algo=0x7  flags=0x2
SST27SF512 RESOLVED  algo=0x7  flags=0x2
SST27VF256 RESOLVED  algo=0x7  flags=0x2
SST27VF512 RESOLVED  algo=0x7  flags=0x2
```

Note W27E512 is stored as a combined entry `W27C512,W27E512` in chip_database.json but resolves as a distinct lookup via the alias mechanism.

**SAFE-01 for Phase 77 = N/A-no-refusal.** There is no host-guard refusal to remove. The "graduation gate last" discipline applies here as: the explicit `FLAG_CAN_ERASE` wiring in `convert_to_programmer` (the canonical source change) lands only after the native test + wire round-trip + Leonardo bench are on record. D-05 mandates this is documented explicitly so downstream agents do not fabricate a refusal-drop task.

### SAFE-02: check_dispatch.py

**Invocation (CONFIRMED: run on 2026-06-21):**
```bash
cd firestarter_app && python3 tools/check_dispatch.py
```

**Current status:**
```
PASS: all 744 chips scanned; 730 supported; 14 chips confirmed non-dispatchable;
0 non_supported_dispatchable; 0 dispatch regressions; 0 consistency violations
```

This phase edits only `convert_to_programmer` (the flag derivation for the wire JSON). It does NOT change:
- The `algorithm` field (dispatch key)
- `vpp_mv`
- `support_status`
- `electrical.type` storage
- `check_dispatch.py`'s `_FAMILY_VPP_INVARIANTS`

Therefore `check_dispatch.py` should remain green after the edit. **Must be re-run after the edit and its output recorded** as a gate artifact (SAFE-02).

### SAFE-03: FLAG_CAN_ERASE Parity

**CONFIRMED (read both files + live parity test run):**

| Location | Value |
|----------|-------|
| `firestarter_app/firestarter/constants.py` line 80 | `FLAG_CAN_ERASE = 0x02` |
| `firestarter/include/firestarter.h` line 60 | `#define FLAG_CAN_ERASE 0x02` |

**This phase does NOT modify either file.** The `convert_to_programmer` edit reads `FLAG_CAN_ERASE` (does not redefine it). SAFE-03 parity is trivially preserved.

**Parity test:** `tests/test_revision_constants_parity.py::test_flag_values_match_firmware` — currently PASSES (5/5). Must confirm still green after the edit.

---

## Architecture Patterns

### The FLAG_CAN_ERASE Decode Chain (end-to-end)

```
infoic.xml flags & 0x10
         ↓ build_db.py Pass-2 (lines 629-638)
chip_database.json   electrical.type = "EEPROM" | "UV-EPROM" | "Flash/EEPROM"
         ↓ database.py _map_data (line 434)
_map_data return dict   info-flags bit 0x10 set (synthetic injection)
         ↓ database.py convert_to_programmer (line 597) ← EDIT SITE
wire JSON   flags = 0x02 (FLAG_CAN_ERASE) or 0x00
         ↓ serial → firmware
firmware handle->flags
         ↓ eprom_write_init (eprom.cpp:100)
is_flag_set(FLAG_CAN_ERASE)
         ↓ if True and !FLAG_SKIP_ERASE
eprom_internal_erase → CTRL_VPP_REGULATOR_ENABLE | A9 | VPE (14V rail)
```

**Current path (FRAGILE):** `convert_to_programmer` reads `info-flags & 0x10`, which is a synthetic field injected by `_map_data`. If `_map_data` is refactored, the `info-flags` injection could disappear silently.

**Proposed canonical path (D-01):** `convert_to_programmer` reads `full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM")` directly. This is robust to `_map_data` refactors and is the authoritative ground truth (the same field the display layer uses).

### Edit Site

**File:** `firestarter_app/firestarter/database.py`
**Lines:** 592–600 (CONFIRMED: read source)

Current code:
```python
# Calculate the simple 'flags' key for the programmer
# Inferring from mapped 'type': Type 2 (Flash 2) and Type 3 (Flash 3) are electrically erasable.
# New requirement: FLAG_CAN_ERASE should be set if info-flags has the 0x00000010 bit.
simple_flags = 0
if (
    full_eprom_data.get("info-flags", 0) & 0x00000010
):  # Check for "Can be electrically erased" bit
    simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE is 0x02
programmer_data["flags"] = simple_flags
```

Proposed replacement (canonical derivation per D-01/D-02):
```python
# FLAG_CAN_ERASE: set from electrical-type (the canonical erase-capability ground truth,
# decoded from infoic.xml flags & 0x10 by build_db.py Pass-2). Reading electrical-type
# directly is more robust than the synthetic info-flags round-trip.
# D-02: covers both "EEPROM" (0x07/0x08/0x0B EE-EPROMs) and "Flash/EEPROM" (0x0D/0x05/0x06/0x10).
# On the 0x0D configure_eeprom28c path FLAG_CAN_ERASE is inert (eeprom_28c.cpp never reads it).
simple_flags = 0
if full_eprom_data.get("electrical-type", "") in ("EEPROM", "Flash/EEPROM"):
    simple_flags |= FLAG_CAN_ERASE  # FLAG_CAN_ERASE = 0x02
programmer_data["flags"] = simple_flags
```

**Behavioral delta:** None. All 8 target chips already get `flags=0x02` today; so do all `Flash/EEPROM` chips. UV-EPROMs get `flags=0x00`. The new code produces identical wire output — it just reads from a more stable source.

### Recommended Project Structure (no changes)

```
firestarter_app/
├── firestarter/
│   └── database.py          # EDIT: convert_to_programmer (~line 595-600)
└── tests/
    ├── test_database_conversion.py    # ADD: FLAG_CAN_ERASE flag tests
    ├── test_eprom_database.py         # EXISTING TestErasableFlag (passes; no change needed)
    └── test_eprom_operations.py       # ADD: ack_data=False regression test (D-07)
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Flag derivation correctness gate | Custom script | `check_dispatch.py` + existing pytest suite |
| Wire round-trip proof | New integration harness | Existing `test_database_conversion.py` pattern |
| Bench write/verify | New CLI tooling | Existing `firestarter write / read / verify` CLI commands |
| Parity check | Manual diff | `test_revision_constants_parity.py::test_flag_values_match_firmware` |

---

## Common Pitfalls

### Pitfall 1: Thinking FLAG_CAN_ERASE Is Broken and Needs a Real Fix

**What goes wrong:** The planner creates tasks to "wire" the flag as if it does nothing today — adding new code paths, plumbing, or changing firmware.

**Why it happens:** The ROADMAP and old planning artifacts describe the flag as "always-zero `info-flags & 0x10`", which was accurate before Phase 60's `_map_data` fix.

**How to avoid:** The CONTEXT.md RF-01 hint is correct — `_map_data` already injects `info_flags |= 0x10` for `"EEPROM"` chips (added in Phase 60 as part of the display-layer decode correctness work). The fix is a code quality improvement (read canonical `electrical-type` directly), not a gap fill.

### Pitfall 2: Testing info-flags Instead of the Wire Output

**What goes wrong:** New tests assert `info-flags & 0x10` is set (which TestErasableFlag already covers) rather than asserting `convert_to_programmer` produces `flags & FLAG_CAN_ERASE`.

**How to avoid:** The new test in `test_database_conversion.py` should call `db.convert_to_programmer(db.get_eprom("W27C512"))` and assert `result["flags"] & FLAG_CAN_ERASE`. This is the actual wire-level assertion ERASE-01 requires.

### Pitfall 3: Forgetting the UV-EPROM Negative Control

**What goes wrong:** Tests only assert positive cases (EEPROM → flag set). UV-EPROMs could silently acquire the flag if the condition is written wrong.

**How to avoid:** Add a negative-control test: `db.convert_to_programmer(db.get_eprom("M27C512"))["flags"] & FLAG_CAN_ERASE == 0`. M27C512 is `electrical-type = "UV-EPROM"` and must NOT get the flag.

### Pitfall 4: Failing to Record the Bench VPP Measurement

**What goes wrong:** The bench task runs the write cycle but skips the 14V VPP multimeter dry-run (chip-OUT), so SC#3 is not closed.

**How to avoid:** The bench plan must have an explicit `autonomous: false` step: remove W27C512 from socket, run `firestarter vpp W27C512` or equivalent to raise the erase rail, measure with multimeter, record the value. Then re-seat chip and run the write cycle. The erase rail is VPE without the dropping resistor — expect ~14V on a well-calibrated Rev 2.2 shield; value may vary on Rev 2.0/Rev 0.

### Pitfall 5: Misunderstanding the 0xA4 Regression Scope

**What goes wrong:** The D-07 regression test is written against the MAIN phase data flow (ack_data=True) rather than INIT/END (ack_data=False).

**How to avoid:** The 0xA4 desync originated from acking DATA frames during INIT/END phases. The fix (`ack_data=False` on line 372) applies to `_execute_phase` which handles both INIT and END. The regression test should inject DATA responses into an `_execute_phase("INIT", ...)` call and count `send_ack` calls.

### Pitfall 6: Running check_dispatch.py Before the Edit Instead of After

**What goes wrong:** The planner records the pre-edit check_dispatch.py pass as the SAFE-02 artifact.

**How to avoid:** SAFE-02 requires the gate to pass AFTER the `convert_to_programmer` edit is applied. The pre-edit baseline (744 chips, 0 violations) is documented here as context, but the SAFE-02 gate artifact must be captured post-edit.

---

## Code Examples

### Existing TestErasableFlag (do not duplicate — extend instead)

```python
# Source: firestarter_app/tests/test_eprom_database.py:207-241
class TestErasableFlag:
    """D-03 — info-flags bit 0x10 must fire for EEPROM family."""

    def test_w27c512_info_flags_has_erasable_bit(self):
        db = EpromDatabase(skip_local_override=True)
        eprom = db.get_eprom("W27C512")
        assert eprom.get("info-flags", 0) & 0x10  # already covered; don't duplicate
```

### New Test: Wire-Level FLAG_CAN_ERASE Assertion (add to test_database_conversion.py)

```python
# Source: pattern from firestarter_app/tests/test_database_conversion.py
from firestarter.constants import FLAG_CAN_ERASE

def test_convert_w27c512_flag_can_erase(db):
    """W27C512 (EEPROM) must produce FLAG_CAN_ERASE in convert_to_programmer output."""
    full = db.get_eprom("W27C512")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE, "W27C512 wire flags must have FLAG_CAN_ERASE (0x02)"

def test_convert_uv_eprom_no_flag_can_erase(db):
    """M27C512 (UV-EPROM) must NOT produce FLAG_CAN_ERASE in convert_to_programmer output."""
    full = db.get_eprom("M27C512")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert not (out["flags"] & FLAG_CAN_ERASE), "UV-EPROM must NOT have FLAG_CAN_ERASE"

def test_convert_at28c256_flash_eeprom_flag_can_erase(db):
    """AT28C256 (Flash/EEPROM via WARNING-5 override) must also produce FLAG_CAN_ERASE."""
    full = db.get_eprom("AT28C256")
    assert full is not None
    out = db.convert_to_programmer(full)
    assert out["flags"] & FLAG_CAN_ERASE, "Flash/EEPROM type must have FLAG_CAN_ERASE"
```

### D-07 Regression Test Pattern (add to test_eprom_operations.py)

```python
# Conceptual — planner determines exact fixture style consistent with existing tests
from unittest.mock import MagicMock, patch

def test_init_phase_data_frames_not_acked():
    """INIT-phase DATA frames must NOT be acked (0xA4 regression guard, D-07).
    
    Reproduces the 2026-06-17 fix: _execute_phase passes ack_data=False so
    per-chunk blank-check progress frames in INIT do not desync the MAIN handshake.
    """
    comm = MagicMock()
    # Simulate: firmware sends DATA then DATA then INIT (blank-check progress + completion)
    comm.get_response.side_effect = [
        MagicMock(type="DATA", message="1/128"),
        MagicMock(type="DATA", message="64/128"),
        MagicMock(type="INIT", message="OK"),
    ]
    operator = EpromOperator(comm=comm, ...)
    operator._execute_phase("INIT", progress=MagicMock())
    # The initial send_ack() that starts the phase fires once;
    # DATA frames must NOT trigger additional acks.
    assert comm.send_ack.call_count == 1  # only the phase-start ack
```

### firestarter CLI Commands for Bench Proof

```bash
# ERASE-02 bench sequence on Leonardo:
# 1. Confirm controller identity
firestarter --port /dev/ttyACM0 version   # verify Leonardo responds

# 2. VPP dry-run (chip-OUT, measure multimeter on socket VPP pin)
firestarter --port /dev/ttyACM0 vpp W27C512  # raises erase rail; measure ~14V

# 3. Re-seat W27C512 (non-blank chip). Default no-b write triggers auto-erase.
firestarter --port /dev/ttyACM0 write W27C512 firmware.bin  # no -b flag

# 4. Independent post-write SHA verification
firestarter --port /dev/ttyACM0 read W27C512 readback.bin
sha256sum firmware.bin readback.bin  # must match

# 5. Non-vacuous negative control (wrong file)
firestarter --port /dev/ttyACM0 verify W27C512 wrong.bin  # must exit non-zero
```

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.0 (confirmed installed) |
| Config file | `firestarter_app/pyproject.toml` |
| Quick run command | `cd firestarter_app && python3 -m pytest tests/test_database_conversion.py tests/test_eprom_database.py::TestErasableFlag tests/test_revision_constants_parity.py -v` |
| Full suite command | `cd firestarter_app && python3 -m pytest --cov --cov-fail-under=70` |
| Lint gate | `ruff check . && ruff format --check .` |
| Type gate | `mypy firestarter/database.py` (database.py is NOT in the strict-8 module list; check CLAUDE.md) |

**Strict mypy modules (per firestarter_app/CLAUDE.md):** `main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`. `database.py` is NOT in this list — mypy strict overrides do not apply to the edit site.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ERASE-01 | `convert_to_programmer` sets FLAG_CAN_ERASE from `electrical-type` for W27C512 | unit | `pytest tests/test_database_conversion.py::test_convert_w27c512_flag_can_erase -x` | ❌ Wave 0 |
| ERASE-01 | UV-EPROM does NOT get FLAG_CAN_ERASE | unit | `pytest tests/test_database_conversion.py::test_convert_uv_eprom_no_flag_can_erase -x` | ❌ Wave 0 |
| ERASE-01 | AT28C256 (Flash/EEPROM) gets FLAG_CAN_ERASE | unit | `pytest tests/test_database_conversion.py::test_convert_at28c256_flash_eeprom_flag_can_erase -x` | ❌ Wave 0 |
| ERASE-02 | write→auto-erase→program→verify cycle completes | hardware/bench | manual — Leonardo W27C512 + SHA match | N/A |
| SAFE-01 | 8 chips are `supported`, resolve_chip does not refuse | unit (existing) | `pytest tests/test_chip_resolver.py -v` | ✅ (no new test needed) |
| SAFE-02 | check_dispatch.py passes after edit | integration | `python3 tools/check_dispatch.py` | ✅ |
| SAFE-03 | FLAG_CAN_ERASE parity constants.py = firestarter.h | unit (existing) | `pytest tests/test_revision_constants_parity.py -v` | ✅ |
| D-07 | INIT-phase DATA frames not acked (0xA4 guard) | unit | `pytest tests/test_eprom_operations.py::test_init_phase_data_frames_not_acked -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_database_conversion.py tests/test_revision_constants_parity.py -v`
- **Per wave merge:** `pytest --cov --cov-fail-under=70 && python3 tools/check_dispatch.py && ruff check . && ruff format --check .`
- **Phase gate:** Full suite green + check_dispatch.py PASS before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_database_conversion.py` — add 3 `convert_to_programmer` FLAG_CAN_ERASE tests
- [ ] `tests/test_eprom_operations.py` — add D-07 `ack_data=False` regression test

---

## Security Domain

SAFE gates are the security mechanism for this phase (hardware damage prevention, not software security). No ASVS categories apply — this is a firmware programmer tool, not a networked application.

| ASVS Category | Applies | Note |
|---------------|---------|------|
| V2 Authentication | No | Local tool, no auth |
| V5 Input Validation | No | DB field is controlled by build_db.py pipeline |
| V6 Cryptography | No | N/A |

Hardware safety gates (domain-specific):
- VPP multimeter dry-run before chip insertion (prevents wrong-VPP damage)
- `check_dispatch.py` VPP-safety scan (prevents DB change from routing wrong voltage)
- Firmware `eprom_check_vpp` (rejects VPP > setpoint + 500 mV before writing)

---

## Environment Availability

| Dependency | Required By | Available | Notes |
|------------|------------|-----------|-------|
| Python 3.12 | Host tests | ✅ | Devcontainer default; masks CI py3.9/3.11 — validate ruff clean |
| pytest 9.1.0 | Test suite | ✅ | Confirmed installed |
| firestarter_app (editable) | Tests | ✅ | pip install -e . done |
| firestarter firmware checkout | SAFE-03 parity test | ✅ | `/workspaces/firestarter/` present |
| Leonardo board | ERASE-02 bench | hardware-gated | `autonomous: false`; operator bench |
| W27C512 (non-blank) | ERASE-02 bench | hardware-gated | Operator chip inventory |
| Shield (Rev ask) | ERASE-02 bench | hardware-gated | Must ask which rev is mounted |

**Missing dependencies with no fallback:**
- Leonardo + W27C512 + mounted shield (all hardware-gated; bench task is `autonomous: false`)

---

## Project Constraints (from CLAUDE.md)

From `firestarter_app/CLAUDE.md`:

- `chip_database.json` is generated by `build_db.py` — do NOT edit by hand
- Serial protocol changes must be kept in sync between `serial_comm.py` and `firestarter.cpp` (not relevant to this phase — no protocol change)
- Constants/flag bits are duplicated between `constants.py` and `firestarter.h` — change both together. **This phase does NOT touch either file**; parity is preserved trivially.
- Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules: `main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`) + `pytest --cov-fail-under=70`
- Devcontainer Python 3.12 masks CI py3.9/3.11 — validate ruff against target before claiming green (ruff f-string backslashes trap, non-ruff-clean codegen trap)

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `electrical-type` key in `_map_data` return dict is always a string (never None/missing) for chips in chip_database.json | Edit Site | If empty/None for some chip, `in ("EEPROM", "Flash/EEPROM")` returns False — behaves identically to current path (flag stays clear); safe degradation |
| A2 | W27C512 datasheet erase voltage = 14V; the actual VPE rail on a Rev 2.2 shield at vpp_mv=12000 is ~14V without the dropping resistor | Bench SC#3 | If bench measures significantly different voltage, may need shield recalibration; does not block software work |

**Most claims in this research were CONFIRMED by reading live code or running it directly.**

---

## Sources

### Primary (HIGH confidence — code read or live execution)

- `firestarter_app/firestarter/database.py` lines 430–602 — `_map_data` (info_flags injection) + `convert_to_programmer` (flag derivation); CONFIRMED by reading and live execution
- `firestarter/src/proms/eprom.cpp` lines 93–111 + 274–288 — `eprom_write_init` FLAG_CAN_ERASE consumption + `eprom_internal_erase` voltage rail; CONFIRMED by reading
- `firestarter/src/proms/eeprom_28c.cpp` lines 35–155 — `configure_eeprom28c` full source; FLAG_CAN_ERASE absent; CONFIRMED by reading
- `firestarter_app/firestarter/constants.py` lines 79–80 — FLAG_CAN_ERASE = 0x02; CONFIRMED
- `firestarter/include/firestarter.h` lines 59–60 — FLAG_CAN_ERASE = 0x02; CONFIRMED
- `firestarter_app/firestarter/eprom_operations.py` lines 347–420 — `_execute_phase` + `_handle_progress_response` ack_data=False; CONFIRMED
- Live Python execution: all 8 target chips → `flags=0x2`, resolve_chip RESOLVED; UV-EPROMs → `flags=0x0`
- Live `python3 tools/check_dispatch.py` → PASS 744 chips, 0 violations

### Secondary (MEDIUM confidence — read planning artifacts)

- `.planning/phases/72-re-research-the-protocol-landscape/72-RESEARCH.md` line 93 + 173 — W27C512 datasheet 14V erase rail, erase path firmware analysis
- `.planning/STATE.md` Phase 73 decision: "A2-CONFIRMED: W27C512 erase fires correctly in write_cycle_eprom; Tier-3 PASS authoritative on Leonardo"
- `.planning/STATE.md` Phase 60 work context: `_map_data` fix adding "EEPROM" to the `info_flags |= 0x10` condition

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| RF-01 (flag already set) | HIGH | Confirmed by live execution |
| D-03 (eeprom_28c ignores flag) | HIGH | Read full eeprom_28c.cpp; FLAG_CAN_ERASE absent from all is_flag_set() calls |
| Edit site / approach | HIGH | Single condition change; confirmed behavioral delta = zero |
| Test locations | HIGH | Existing test files confirmed; patterns confirmed |
| Bench erase voltage (14V) | MEDIUM | Inferred from firmware path + Phase 72 research + datasheet reference; confirmed indirectly by Phase 73 bench pass |

**Research date:** 2026-06-21
**Valid until:** Stable (no firmware changes in this phase; database.py and constants.py are well-established)
