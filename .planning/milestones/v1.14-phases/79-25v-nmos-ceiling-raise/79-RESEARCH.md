# Phase 79: 25V NMOS Ceiling Raise — Research

**Researched:** 2026-06-22
**Domain:** Host-only constant change (`build_db.py` + `check_dispatch.py`) with hardware-gated graduation gate
**Confidence:** HIGH — all source-of-truth locations confirmed by reading live code; firmware no-ceiling claim confirmed by source; chip DB entries confirmed by live query

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| NMOS-01 | On-bench shield's ability to safely produce ≥25V VPP at socket pin confirmed by operator multimeter (chip-OUT dry-run) BEFORE ceiling constant changes | Dry-run gate command documented; firmware `vpp` command (no chip argument) measures actual hardware VPP output; R1/R2 calibration is for ADC readback, not for controlling output — hardware PCB feedback resistors set actual VPP level |
| NMOS-02 | `RURP_VPP_CEILING_MV` raised 22000→25000 (`build_db.py`) + `check_dispatch.py` `_FAMILY_VPP_INVARIANTS` ceiling updated; 4 NMOS chips re-classify off `vpp-exceeds-max` | Exact edit sites identified with line numbers; ceiling comparison is strict-greater (`>`), so 25V chips at exactly 25000 mV are accepted; DB regen command documented; 4 chip entries confirmed |
| NMOS-03 | 4 NMOS chips graduate to `supported`; write+verify bench-confirmed on Leonardo | Guard removal pattern from Phase 77; test suite changes catalogued; firmware protocol path confirmed as 0x0B (EPROM_LEGACY); firmware VPP check passes if hardware produces ~25V |

</phase_requirements>

---

## Summary

Phase 79 is a host-only code change — two constant edits and a DB regeneration — followed by a hardware-gated bench proof. The 22V ceiling in `RURP_VPP_CEILING_MV` is a deliberate conservative software limit, not a hardware physical ceiling: the RURP product page states "5–27V VPP" and the AP3012 boost regulator supports that range depending on PCB feedback resistors. The on-bench shield's actual output must be measured before proceeding.

The edit surface is minimal: one integer in `build_db.py` (line 117) and one tuple in `check_dispatch.py` (line 79). After raising both to 25000, running `python3 tools/build_db.py` reclassifies all 4 currently-blocked NMOS chips from `vpp-exceeds-max` to `supported` and restores their protocol to `0x0B` (EPROM_LEGACY). The `chip_resolver.resolve_chip` host-guard is currently the refusal mechanism — it rejects any chip with `support_status != "supported"` — and after reclassification it automatically stops refusing the 4 chips without a separate guard-removal edit.

The most important research finding: **after graduation, zero `vpp-exceeds-max` chips remain in the DB** (no chip has `vpp_mv > 25000`). All existing tests that use M2716 as the exemplar for `vpp-exceeds-max` behavior break and must be replaced.

**Primary recommendation:** Execute in three ordered plans: (1) hardware gate — operator multimeter dry-run ≥25V (`autonomous: false`); (2) ceiling raise + DB regen + test updates + `check_dispatch.py` gate; (3) Leonardo bench write+verify for the graduation proof.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| VPP ceiling enforcement (host) | Host (`build_db.py` + `check_dispatch.py`) | — | The ONLY ceiling is the `RURP_VPP_CEILING_MV` constant in `build_db.py`; firmware has NO ceiling constant |
| Chip classification (`vpp-exceeds-max` → `supported`) | DB pipeline (`build_db.py` Site C) | — | NMOS_TRUE_VPP_MV lookup + strict-greater comparison against ceiling decides support_status |
| Host-guard refusal | Host (`chip_resolver.resolve_chip`) | — | `support_status != "supported"` raises `ChipNotImplementedError` before any wire dict; self-heals automatically when support_status changes |
| VPP family invariant check | CI gate (`check_dispatch.py`) | — | `_FAMILY_VPP_INVARIANTS["configure_eprom"]` must be updated in lockstep with build_db.py ceiling |
| Hardware VPP measurement | Firmware (ADC readback) + Host (`firestarter vpp`) | — | `rurp_read_voltage_mv()` uses R1/R2 divider for ADC scaling; measures actual hardware output |
| 25V VPP rail for programming | Hardware (PCB boost converter feedback resistors) | — | Firmware `eprom_check_vpp` validates measured VPP against requested ±tolerance; does NOT enforce a ceiling |
| Bench graduation proof (NMOS-03) | Hardware bench | — | Leonardo + NMOS chip + operator; `autonomous: false` gate |

---

## Source-of-Truth Locations

### Q1: `RURP_VPP_CEILING_MV` Definition

**File:** `firestarter_app/tools/build_db.py`
**Line:** 117
**Current value:** `RURP_VPP_CEILING_MV = 22000`
**Units:** millivolts (22000 mV = 22V)

**How it gates classification (Site C, lines 645–671):**

```python
# CONFIRMED: firestarter_app/tools/build_db.py lines 645–671
if _nmos_vpp_mv is not None:
    if _nmos_vpp_mv > RURP_VPP_CEILING_MV:           # strict greater-than
        _support_status = "vpp-exceeds-max"
        _unsupported_reason = (
            f"VPP {_nmos_vpp_mv // 1000}V exceeds programmer max "
            f"({RURP_VPP_CEILING_MV // 1000}V)"
        )
        proto_id = NON_DISPATCHABLE_ALGO              # CR-01: demote to 0x00
    # else: leave _support_status as "supported"
```

**Critical detail — strict `>` comparison:** At the new ceiling of 25000, chips with `_nmos_vpp_mv = 25000` evaluate `25000 > 25000 = False` → NOT demoted → classified as `supported` with `proto_id` intact (0x0B). This is the intended behavior.

**NMOS_TRUE_VPP_MV lookup (lines 110–114):**

```python
# CONFIRMED: firestarter_app/tools/build_db.py lines 110–114
NMOS_TRUE_VPP_MV: dict[str, int] = {
    "M2716": 25000,  # Intel NMOS 2716: 25V VPP (datasheet)
    "M2732": 25000,  # Intel NMOS 2732: 25V VPP (datasheet)
    "M2732A": 21000, # Intel NMOS 2732A: 21V VPP (later variant)
}
```

Matching uses part-alias intersection; "highest VPP wins" for combined entries. The INTEL combined entry `2732,2732A,M2732,M2732A` contains both `M2732` (25V) and `M2732A` (21V) — `25000 > 21000` wins → the combined entry gets 25V → currently `vpp-exceeds-max`. SGS-THOMSON and ST `M2732A` standalone entries contain only `M2732A` → 21V → already `supported`. [CONFIRMED: live Python query 2026-06-22]

### Q2: `_FAMILY_VPP_INVARIANTS` in `check_dispatch.py`

**File:** `firestarter_app/tools/check_dispatch.py`
**Lines:** 78–85

```python
# CONFIRMED: firestarter_app/tools/check_dispatch.py lines 78–85
_FAMILY_VPP_INVARIANTS: dict[str, tuple[int, int]] = {
    "configure_eprom": (0, 22000),  # RURP VPP ceiling 22V; any VPP up to that
    "configure_eeprom28c": (0, 6000),
    "configure_flash3": (0, 6000),
    "configure_flash4": (0, 6000),
    "configure_flash_intel": (10000, 22000),
    "configure_sram": (0, 6000),
}
```

**Enforcement scope (line 93):**
```python
_DB_CHECKED_VPP_INVARIANTS: frozenset[str] = frozenset({"configure_flash_intel"})
```

`configure_eprom`'s `(0, 22000)` range is **NOT** used in the DB scan — only in synthetic fixture tests. The DB scan only checks `configure_flash_intel` chips. Changing `(0, 22000)` to `(0, 25000)` does not cause any real chip to fail the `check_dispatch.py` scan. The synthetic fixture test at `tests/test_check_dispatch_invariants.py:153` uses `vpp_mv=12000` to prove non-violation — `12000 <= 25000` still passes, so this test is unaffected by the ceiling change.

Both constants (`RURP_VPP_CEILING_MV` and `_FAMILY_VPP_INVARIANTS["configure_eprom"]`) **must be updated together** to maintain semantic consistency. Updating only one would leave the invariant documentation stale.

### Q3: Firmware VPP Enforcement — CONFIRMED ABSENT

**CONFIRMED by reading:** `firestarter/src/proms/eprom.cpp`, `firestarter/include/rurp_pinout.h`, `firestarter/include/rurp_shield.h`, `firestarter/src/boards/rurp_common.cpp`

The firmware does **NOT** have a VPP ceiling constant. The relevant check in `eprom_check_vpp` (lines 209–268) is:
- `measured_vpp > handle->vpp_mv + 500` → error (VPP too high above requested)
- `measured_vpp < handle->vpp_mv * 95 / 100` → error (VPP too low)

This is a **chip-specific ±tolerance check**, not a ceiling. At 25V: `vpp_mv = 25000` → hardware must deliver between 23750 mV (95%) and 25500 mV (requested + 500). If the on-bench shield hardware cannot reach 25V, `eprom_check_vpp` returns `RESPONSE_CODE_ERROR` before any programming pulse. This is the firmware-side safety net for NMOS-01.

**No firmware changes are needed for this phase.** [CONFIRMED: grep for VPP_CEILING, MAX_VPP, 22000, 25000 in `firestarter/include/` and `firestarter/src/` returned no hits]

**Change surface is host-only:** `firestarter_app/` only. No firmware build, no `pio run`, no lockstep version bump needed.

### Q4: The 4 Target NMOS Chips

Confirmed by live query of `chip_database.json` (2026-06-22):

| Requirement Alias | DB Manufacturer | DB `part_number` | Pinout | Current `vpp_mv` | Current `support_status` | Current `programming.algorithm` |
|---|---|---|---|---|---|---|
| INTEL M2716 | INTEL | `M2716,M2716M` | `DIP24_2716` | 25000 | `vpp-exceeds-max` | 0 (demoted) |
| INTEL M2732 | INTEL | `2732,2732A,M2732,M2732A` | `DIP24_2732` | 25000 | `vpp-exceeds-max` | 0 (demoted) |
| SGS-THOMSON ETC2716 | SGS-THOMSON | `ETC2716,M2716` | `DIP24_2716` | 25000 | `vpp-exceeds-max` | 0 (demoted) |
| ST M2716 | ST | `ETC2716,M2716` | `DIP24_2716` | 25000 | `vpp-exceeds-max` | 0 (demoted) |

**M2732A (21V) confirmed safe:** SGS-THOMSON `M2732A` and ST `M2732A` standalone entries have `vpp_mv=21000`, `support_status=supported`. The INTEL combined `2732,2732A,M2732,M2732A` entry captures the M2732 (25V) alias — that entry is what graduates. The M2732A standalone entries are NOT touched. [CONFIRMED: live query]

**After graduation, ZERO `vpp-exceeds-max` chips remain:** No chip in `chip_database.json` has `vpp_mv > 25000`. All 4 current `vpp-exceeds-max` entries become `supported`. [CONFIRMED: search for vpp_mv > 25000 returned no chips]

**Post-graduation DB state for the 4 chips:**
- `support_status`: `"supported"` (was `"vpp-exceeds-max"`)
- `programming.algorithm`: 0x0B / 11 (restored; was 0 / `NON_DISPATCHABLE_ALGO`)
- `unsupported_reason`: absent (was `"VPP 25V exceeds programmer max (22V)"`)
- All other fields (pinout, electrical, vpp_mv) unchanged

**Verify:** After DB regen, all 4 chips should dispatch to `configure_eprom` (same as AMD/FUJITSU/TI DIP24_2716 chips, all using protocol 0x0B). [CONFIRMED by examining all supported DIP24_2716 and DIP24_2732 chips in DB: all use `programming.algorithm = 11` (0x0B = EPROM_LEGACY)]

### Q5: Host-Guard Refusal Mechanism (from Phase 77 Pattern)

**File:** `firestarter_app/firestarter/chip_resolver.py` (entire file, 64 lines)

```python
# CONFIRMED: firestarter_app/firestarter/chip_resolver.py lines 54–57
support_status = raw_config.get("support_status", "supported")
if support_status != "supported":
    reason = raw_config.get("unsupported_reason", "unsupported on this hardware")
    raise ChipNotImplementedError(f"{name}: {reason}")
```

The guard is **purely driven by `support_status`**. When `build_db.py` reclassifies the 4 chips to `support_status="supported"`, the guard stops firing **automatically** — no separate edit to `chip_resolver.py` is needed. This is different from Phase 77's pattern where no guard existed at all; here the guard self-heals when the DB changes.

**SAFE-01 for Phase 79:** The "guard removal is the FINAL step" discipline is implemented differently than Phase 77. The graduation gate (NMOS-03) is the Leonardo bench write+verify — this is the "final step" the SAFE discipline protects. The host-guard doesn't need a separate removal task because raising the ceiling in `build_db.py` + regenerating the DB accomplishes both classification AND implicit guard clearing simultaneously.

However, the plan must clearly sequence: (1) hardware gate → (2) ceiling change + DB regen → (3) bench proof. Do not flip `support_status` manually; it must come from `python3 tools/build_db.py` regeneration. The host guard drops automatically from the DB output.

### Q6: The 25V Rail Capability Question

**Governing hardware:** The RURP uses an AP3012 boost converter. Its output voltage is set by PCB feedback resistors (the hardware physical limit). The product page states "5–27V VPP"; the AP3012 supports "4.5→36V-ish" depending on those resistors. The current 22V software ceiling is a deliberate conservative limit, not a hardware constraint. [CITED: `.planning/research/STACK.md` lines 167–172, which cites RURP product page + Hackaday project page]

**R1/R2 in firmware EEPROM are for ADC measurement, NOT for controlling output:**

`rurp_read_voltage_mv()` (`firestarter/src/boards/rurp_common.cpp:52–71`) uses the formula:
```
Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)
```
This is a voltage divider readback formula. R1=270000, R2=44000 calibrates the ADC to correctly read the actual voltage produced by the hardware. The firmware does NOT control the boost converter setpoint via R1/R2 — that is fixed by PCB feedback resistors.

**ADC headroom for 25V:** With R1=270k, R2=44k, the maximum measurable voltage before ADC saturation is ~35.6V. A 25V input produces an ADC reading of ~716/1023 — well within the measurable range. The ADC CAN read 25V correctly with the current calibration. [CONFIRMED: calculation from rurp_read_voltage_mv formula]

**Dry-run command:** `firestarter -p <port> vpp`

This command (`cli_handlers.py:626–635`) calls `read_vpp_voltage()`, which sends `CMD_READ_VPP` to firmware. Firmware enables `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` (the drop path, same as programming VPP for 0x07/0x08 EPROM_STD), waits 100ms for stabilization, then measures and streams the voltage. **This command does NOT route voltage to the socket** (per project memory: "vpp/vpe monitors don't route voltage to the socket — safe with a chip seated"). Chip-OUT is still best practice before any unknown VPP measurement. [CONFIRMED: `hardware_operations.cpp` lines 15–80; project memory `reference_vpp_vpe_no_socket_routing.md`]

**The critical hardware question (NMOS-01):** The `firestarter vpp` command measures the hardware's actual VPP output with the drop path enabled. If the PCB boost converter is calibrated to output ~12–14V (the common bench setpoint for 12V EPROM programming), the `vpp` reading will be ~12–14V and the operator will see that 25V is NOT achievable without hardware adjustment. This is the exact gate the plan must enforce.

**If `firestarter vpp` reads < 25V:**
- Option A: R1 recalibration (`firestarter dev calibrate-vpp` or `firestarter config r1 <value>`) to adjust the boost setpoint. Phase 54 precedent: R1=1000→270000 changed the VPP reading.
- Option B: Physical R1 resistor change on the PCB.
- Either way: the ceiling change should NOT proceed until ≥25V is confirmed. The phase gates on the measurement.

**Live R1/R2 reconcile on record:** Per REQUIREMENTS.md NMOS-03, the live R1/R2 values must be recorded as part of the graduation evidence. Run `firestarter config` to read the current R1/R2 stored in Arduino EEPROM.

### Q7: Lockstep / Parity — Confirmed Host-Only

**SAFE-03 applies only if a `FLAG_*` or protocol constant in `constants.py` ↔ `firestarter.h` is touched.** This phase touches:
- `RURP_VPP_CEILING_MV` — only in `build_db.py` (a tools script, not `constants.py`)
- `_FAMILY_VPP_INVARIANTS` — only in `check_dispatch.py` (a tools script)

Neither constant appears in `firestarter_app/firestarter/constants.py` or `firestarter/include/firestarter.h`. [CONFIRMED: grep for RURP_VPP_CEILING, _FAMILY_VPP_INVARIANTS, 22000, 25000 in both files returned no hits]

**No firmware change. No version bump. No lockstep parity test to run.** The existing parity test `test_revision_constants_parity.py::test_flag_values_match_firmware` is unaffected and must remain green. [ASSUMED: parity test doesn't reference build_db.py constants — not verified by running it, but the test targets FLAG_* and protocol constants, not the ceiling]

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| DB classification from ceiling change | Manually edit `chip_database.json` | `python3 tools/build_db.py` | JSON is generated; hand-edits are overwritten on next regen and introduce drift |
| VPP-safety scan after reclassification | Custom script | `python3 tools/check_dispatch.py` | Already scans all 744 chips; result changes from 14→10 non-dispatchable |
| Review of 4-chip reclassification diff | Manual JSON comparison | `python3 tools/diff_db.py` | Purpose-built diff tool for chip_database.json changes |
| VPP measurement on bench | Multimeter alone | `firestarter -p <port> vpp` + multimeter | Firmware-mediated measurement gives software-readable value; multimeter is secondary confirmation |
| Verify guard is gone | Custom test | Run `python3 -c "from firestarter.chip_resolver import resolve_chip; from firestarter.database import EpromDatabase; resolve_chip('M2716', EpromDatabase(skip_local_override=True))"` | guard self-heals from DB; live resolve_chip run confirms |

---

## Architecture Patterns

### System Data Flow After Ceiling Raise

```
infoic.xml
    ↓ build_db.py Site C (NMOS_TRUE_VPP_MV lookup)
    ↓ _nmos_vpp_mv (25000) > RURP_VPP_CEILING_MV (25000) → False
    ↓ support_status = "supported"  (was "vpp-exceeds-max")
    ↓ proto_id = 0x0B (NOT demoted to 0x00)
chip_database.json
    ↓ chip_resolver.resolve_chip("M2716")
    ↓ support_status == "supported" → NO ChipNotImplementedError raised
    ↓ convert_to_programmer → wire dict with algorithm=0x0B, vpp_mv=25000
JSON command over serial
    ↓ firmware configure_memory: protocol == 0x0B → configure_eprom()
    ↓ eprom_check_vpp: measured_vpp must be between 23750–25500 mV
    ↓ eprom_write_init → eprom_generic_init → write pulse loop
```

### Edit Sites (exact, confirmed)

**Edit 1 — `firestarter_app/tools/build_db.py:117`:**
```python
# Current:
RURP_VPP_CEILING_MV = 22000
# Change to:
RURP_VPP_CEILING_MV = 25000
```

**Edit 2 — `firestarter_app/tools/check_dispatch.py:79`:**
```python
# Current:
"configure_eprom": (0, 22000),  # RURP VPP ceiling 22V; any VPP up to that
# Change to:
"configure_eprom": (0, 25000),  # RURP VPP ceiling 25V (raised Phase 79 from 22V)
```

**DB regen (after both edits):**
```bash
cd firestarter_app && python3 tools/build_db.py
```

**Diff review:**
```bash
python3 tools/diff_db.py
# Expect: 4 chips change (M2716, M2732, SGS-THOMSON ETC2716, ST M2716)
# support_status: vpp-exceeds-max → supported
# programming.algorithm: 0 → 11 (0x0B)
# unsupported_reason: "VPP 25V exceeds programmer max (22V)" → absent
```

**Gate (run after DB regen):**
```bash
python3 tools/check_dispatch.py
# Expect: 734 supported (was 730), 10 non-dispatchable (was 14), 0 violations
```

### Test Updates Required (all in `firestarter_app/tests/`)

The ceiling change causes 7 tests to fail because they use M2716 as the sole exemplar for `vpp-exceeds-max` behavior, and after graduation zero `vpp-exceeds-max` chips remain in the DB.

**Tests that must be updated as part of NMOS-02 (ceiling change step):**

| Test | Current behavior | Required update |
|------|-----------------|-----------------|
| `test_build_db_inclusion.py::TestNmosVppCorrection::test_nmos_vpp_exceeds_max` | Asserts M2716/M2732 have `support_status="vpp-exceeds-max"` | Invert: assert they are now `"supported"` with `vpp_mv=25000`; rename to `test_nmos_graduated_to_supported` |
| `test_build_db_inclusion.py::test_vpp_exceeds_max_reason_starts_with_exceeds_programmer_max` | Asserts M2716 has `unsupported_reason` containing "exceeds programmer max" | Replace: after graduation, M2716 has no `unsupported_reason`. New assertion: 0 chips have `support_status="vpp-exceeds-max"` in the DB. Keep the FUT-02 contract as a synthetic invariant. |
| `test_cli_handlers.py::test_info_vpp_exceeds_max_shows_status` | Asserts M2716 `info` shows "Support status" + "exceeds" | Replace M2716 with a chip that stays non-supported; X88C64P (`protocol-not-implemented`) or AT28C16 (`adapter-required`). |
| `test_cli_handlers.py::test_read_vpp_exceeds_max_status_refusal` | Asserts M2716 read exits 1 with "exceeds" | Replace M2716 with X88C64P or AT28C16 for refusal pattern test. |
| `test_chip_resolver.py::test_resolve_chip_vpp_exceeds_max_raises_not_implemented` | Asserts M2716 raises ChipNotImplementedError | After graduation M2716 resolves. Replace with AT28C16 or X88C64P; add a NEW positive test: resolve_chip("M2716") succeeds (no exception). |
| `test_chip_resolver.py::test_resolve_chip_guard_fires_before_convert_to_programmer` | Patches M2716 to assert guard fires before convert | Same replacement; use AT28C16 or X88C64P. |
| `test_cli_handlers.py::test_read_non_supported_typed_refusal` | Asserts M2716 read exits 1 (typed refusal) | Replace M2716 with AT28C16 or X88C64P for the refusal example. |

**Tests NOT broken by the ceiling change:**
- `test_build_db_inclusion.py::TestNmosVppCorrection::test_nmos_m2732a_supported` — M2732A standalone entries are not affected (no change); still passes
- `test_cli_handlers.py::test_info_vpp_exceeds_max_no_crash` — asserts only exit=0 and no traceback; M2716 as supported still exits 0 → still passes
- `test_check_dispatch_invariants.py::test_configure_eprom_with_valid_vpp_is_not_a_violation` — tests vpp_mv=12000, which is still ≤ 25000 → still not a violation; PASSES (docstring text "22000 mV" is informational only)
- All other `test_check_dispatch_invariants.py` tests — synthetic fixture tests unaffected

**New tests to add (NMOS-02 step):**
1. `test_nmos_graduated_to_supported` — asserts all 4 NMOS chip entries (M2716, M2732, ETC2716) have `support_status="supported"` and `vpp_mv=25000` after DB regen
2. `test_zero_vpp_exceeds_max_chips_remain` — asserts no chip in the DB has `support_status="vpp-exceeds-max"` after graduation
3. `test_configure_eprom_with_25v_vpp_is_not_a_violation` (in `test_check_dispatch_invariants.py`) — proves vpp_mv=25000 does NOT violate the new ceiling (non-vacuous positive test for the new range)

### Anti-Patterns to Avoid

- **Manually editing `chip_database.json`:** The DB is generated; hand edits are wiped on next `build_db.py` run. The ceiling change in `build_db.py` is the canonical fix.
- **Running `check_dispatch.py` before DB regen:** The gate must run against the regenerated DB, not the old one. Old DB + new ceiling constant in `check_dispatch.py` would show 4 vpp-exceeds-max chips as non-dispatchable but still safe (because the old DB has them with proto=0x00 = non-dispatchable anyway). Run DB regen first.
- **Raising RURP_VPP_CEILING_MV without updating `check_dispatch.py`:** The two constants must stay in semantic sync. The check_dispatch.py invariant is the CI guard that would catch a future chip with vpp_mv > ceiling being routed to configure_eprom — raising only one is an incomplete change.
- **Proceeding without the hardware gate (NMOS-01):** The firmware `eprom_check_vpp` will enforce the ±tolerance check at runtime (measured_vpp must be ≥ 23750 mV for a 25V chip). If the shield only outputs 12–14V, the firmware returns RESPONSE_CODE_ERROR before any write pulse. This makes NMOS-01 a hard gate, not just a safety precaution.
- **Using `M2716` as the `vpp-exceeds-max` exemplar in new tests:** After graduation, M2716 is supported. New tests needing a "refused chip" example must use `X88C64P` (`protocol-not-implemented`) or `AT28C16` (`adapter-required`).
- **Python 3.12 masks CI (py3.9/3.11) ruff drift:** Any edit to `build_db.py` or `check_dispatch.py` must be validated with `ruff check --target-version py39 .` from `firestarter_app/`. The devcontainer runs Python 3.12; CI targets 3.9/3.11. F-string backslashes and codegen drift are the documented traps.
- **Bumping the gitlink in the meta-repo per phase:** Per project convention, the gitlink for `firestarter_app` in the meta-repo is NOT bumped per-phase. It is updated at the milestone close / beta cut only.

---

## Common Pitfalls

### Pitfall 1: Thinking Firmware Needs a Ceiling Change

**What goes wrong:** Planner adds a task to change a firmware constant or add a firmware VPP ceiling check, making this a dual-repo lockstep phase.

**Why it happens:** REQUIREMENTS.md and STATE.md say "firmware does NO runtime VPP enforcement" but the planner may not trust this without verification.

**How to avoid:** Confirmed by `grep -rn "VPP_CEILING\|22000\|25000\|MAX_VPP" /workspaces/firestarter/include/ /workspaces/firestarter/src/` returning zero hits. The firmware `eprom_check_vpp` only checks measured vs. chip-specific requested VPP — no ceiling. **This phase is host-only.**

### Pitfall 2: Forgetting That Zero vpp-exceeds-max Chips Remain After Graduation

**What goes wrong:** Tests that use M2716 as the `vpp-exceeds-max` exemplar are left unchanged, causing 7 test failures.

**Why it happens:** The tests were written with M2716 as the sole `vpp-exceeds-max` chip example. After graduation there are NO such chips.

**How to avoid:** The test update list above catalogs all 7 affected tests. Run the full suite before/after to catch all failures.

### Pitfall 3: Updating `check_dispatch.py` Without Updating `build_db.py` or Vice Versa

**What goes wrong:** The ceiling in one place raises to 25000 but the other stays at 22000, causing semantic inconsistency in the CI gate.

**How to avoid:** Both edits must be in the same commit. The plan should co-locate them.

### Pitfall 4: Not Reconciling the Hardware VPP Measurement with R1/R2

**What goes wrong:** Operator measures VPP, sees a value, but doesn't record it or reconcile it with the R1/R2 calibration — graduation evidence is incomplete (NMOS-03 SC#3 requires "live R1/R2 reconcile on record").

**How to avoid:** Run `firestarter config` to dump R1/R2 from Arduino EEPROM; record both the VPP measurement and the R1/R2 at the time of measurement. This proves the calibration was correct for the measured voltage.

### Pitfall 5: Running check_dispatch.py Baseline BEFORE DB Regen

**What goes wrong:** Planner uses the pre-edit baseline pass as the SAFE-02 artifact. SAFE-02 requires green AFTER the change.

**How to avoid:** The SAFE-02 gate must be captured after `build_db.py` regenerates the DB. Expect output: "744 chips scanned; 734 supported; 10 non-dispatchable; 0 violations".

### Pitfall 6: Using the INTEL `2732,2732A,M2732,M2732A` Combined Entry as "INTEL M2732"

**What goes wrong:** The planner searches for "M2732" and finds the combined entry, then also finds the SGS-THOMSON/ST `M2732A` standalone entries, and incorrectly includes the latter in the graduation scope.

**How to avoid:** The combined entry `2732,2732A,M2732,M2732A` (INTEL) is the one with `support_status=vpp-exceeds-max`. The SGS-THOMSON/ST `M2732A` standalone entries already have `vpp_mv=21000` and `support_status=supported` — they are UNTOUCHED.

### Pitfall 7: Python 3.12 ruff Target Version Mismatch

**What goes wrong:** Edits to `build_db.py` or `check_dispatch.py` pass `ruff check .` locally (Python 3.12) but fail CI which targets py3.9.

**How to avoid:** After any Python edit in `firestarter_app/`, run `ruff check --target-version py39 . && ruff format --check --target-version py39 .` from `firestarter_app/` before claiming CI green. The codegen emitter is ruff-clean (reference_codegen_ruff_clean_emitter.md); the tools scripts are hand-written and must be checked manually.

---

## Package Legitimacy Audit

This phase installs no new packages. No audit required.

---

## Runtime State Inventory

> This is not a rename/refactor phase. No runtime state migration needed.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None — chip_database.json is generated from infoic.xml; Arduino EEPROM has R1/R2 calibration (unchanged) | None (R1/R2 are READ, not modified) |
| Live service config | None | None |
| OS-registered state | None | None |
| Secrets/env vars | None | None |
| Build artifacts | None — Python tools, no compiled artifacts | None |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.0 |
| Config file | `firestarter_app/pyproject.toml` |
| Quick run command | `cd firestarter_app && python3 -m pytest tests/test_build_db_inclusion.py tests/test_chip_resolver.py tests/test_check_dispatch_invariants.py -v` |
| Full suite command | `cd firestarter_app && python3 -m pytest --cov --cov-fail-under=70` |
| Lint gate | `ruff check --target-version py39 . && ruff format --check --target-version py39 .` |
| VPP-safety gate | `python3 tools/check_dispatch.py` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NMOS-01 | ≥25V VPP at socket measured by operator multimeter (chip-OUT dry-run) | Hardware/manual | `firestarter -p <port> vpp` + multimeter | N/A (hardware gate) |
| NMOS-02 | `RURP_VPP_CEILING_MV` = 25000 in build_db.py | unit | `python3 -c "from tools.build_db import RURP_VPP_CEILING_MV; assert RURP_VPP_CEILING_MV == 25000"` | ✅ (after edit) |
| NMOS-02 | `_FAMILY_VPP_INVARIANTS["configure_eprom"]` = (0, 25000) | unit | `python3 tools/check_dispatch.py` (implicitly checks invariant structure) | ✅ |
| NMOS-02 | 4 NMOS chips reclassified to `supported` with `vpp_mv=25000` | unit | `pytest tests/test_build_db_inclusion.py::TestNmosVppCorrection::test_nmos_graduated_to_supported -x` | ❌ Wave 0 — test needs to be rewritten |
| NMOS-02 | 0 `vpp-exceeds-max` chips remain in DB | unit | `pytest tests/test_build_db_inclusion.py::test_zero_vpp_exceeds_max_chips_remain -x` | ❌ Wave 0 — new test |
| NMOS-02 | full-DB VPP-safety gate green at new ceiling | integration | `python3 tools/check_dispatch.py` | ✅ (tool exists) |
| NMOS-02 | `configure_eprom` invariant allows vpp_mv=25000 (new ceiling proof) | unit | `pytest tests/test_check_dispatch_invariants.py::test_configure_eprom_with_25v_vpp_is_not_a_violation -x` | ❌ Wave 0 — new test |
| NMOS-02 | 7 broken tests updated (new exemplar chips) | unit | `pytest tests/test_build_db_inclusion.py tests/test_chip_resolver.py tests/test_cli_handlers.py -v` | ❌ Wave 0 — multiple updates |
| NMOS-03 | `resolve_chip("M2716")` succeeds (no exception) after graduation | unit | `pytest tests/test_chip_resolver.py::test_resolve_chip_nmos_graduated_resolves -x` | ❌ Wave 0 — new test |
| NMOS-03 | write+verify cycle completed on Leonardo with NMOS chip | hardware/bench | manual — Leonardo + NMOS chip + SHA match | N/A |
| SAFE-02 | `check_dispatch.py` full-DB gate passes after change | integration | `python3 tools/check_dispatch.py` | ✅ |
| SAFE-03 | Firmware↔host parity tests green (no FLAG_* touched) | unit | `pytest tests/test_revision_constants_parity.py -v` | ✅ |

### Sampling Rate

- **Per task commit:** `pytest tests/test_build_db_inclusion.py tests/test_chip_resolver.py tests/test_check_dispatch_invariants.py -v && ruff check --target-version py39 .`
- **Per wave merge:** `pytest --cov --cov-fail-under=70 && python3 tools/check_dispatch.py && ruff check --target-version py39 . && ruff format --check --target-version py39 .`
- **Phase gate:** Full suite green + `check_dispatch.py` PASS before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_build_db_inclusion.py` — rewrite `test_nmos_vpp_exceeds_max` → `test_nmos_graduated_to_supported`; add `test_zero_vpp_exceeds_max_chips_remain`; replace M2716 with X88C64P/AT28C16 in `test_vpp_exceeds_max_reason_*`
- [ ] `tests/test_chip_resolver.py` — update two tests using M2716 as `vpp-exceeds-max`; add `test_resolve_chip_nmos_graduated_resolves`
- [ ] `tests/test_cli_handlers.py` — update three tests using M2716 as `vpp-exceeds-max` / refusal exemplar
- [ ] `tests/test_check_dispatch_invariants.py` — add `test_configure_eprom_with_25v_vpp_is_not_a_violation`

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| 22V conservative software ceiling | 25V ceiling (after Phase 79) | Phase 79 | 4 NMOS chips graduate from `vpp-exceeds-max` to `supported` |
| M2716/M2732 as `vpp-exceeds-max` exemplar in tests | X88C64P or AT28C16 as non-supported exemplar | Phase 79 | Zero `vpp-exceeds-max` chips remain; tests must use other non-supported categories |
| Manual `unsupported_reason` for NMOS chips | Absent (chip is supported) | Phase 79 | DB cleaner; refusal path no longer reached for these chips |

**Deprecated after Phase 79:**
- Any test that asserts `support_status="vpp-exceeds-max"` for M2716 or M2732 — that category becomes empty in the packaged DB
- The `vpp-exceeds-max` category itself remains in taxonomy (REQUIREMENTS.md NMOS-02 preserves FUT-02: >25V chips stay fail-closed if any are added in the future)

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Host tests | ✓ | 3.12.13 (devcontainer) | — |
| pytest 9.1.0 | Test suite | ✓ | confirmed | — |
| firestarter_app (editable) | Tests | ✓ | `pip install -e '.[test]'` | — |
| ruff | Lint gate | ✓ | installed | — |
| Leonardo board | NMOS-03 bench | hardware-gated | `autonomous: false` | — |
| NMOS chip (M2716 or M2732) | NMOS-03 bench | hardware-gated | operator inventory | — |
| Shield (Rev 2.0 or 2.2, not Rev 0) | NMOS-03 bench | hardware-gated | operator bench | — |
| Multimeter | NMOS-01 dry-run | hardware-gated | operator tool | — |

**Missing dependencies with no fallback:**
- Leonardo + NMOS chip + multimeter + Rev 2.0/2.2 shield (all hardware-gated; dry-run + bench tasks are `autonomous: false`)

**Rev 0 shield exclusion:** `eprom_check_vpp` returns `RESPONSE_CODE_WARNING` for `REVISION_0` (not an error). The Rev 0 modified shield is excluded by standing bench rules; only Rev 2.0/2.2 should be used for graduation proof.

---

## Security Domain

No ASVS categories apply — this is a local hardware programmer tool, not a networked application.

Hardware damage prevention gates (domain-specific security equivalent):
- NMOS-01: VPP dry-run before any chip insertion (prevents wrong-VPP damage to the 25V chip)
- SAFE-02: `check_dispatch.py` full-DB gate (prevents any future chip from routing 25V+ VPP to a handler that doesn't expect it)
- FUT-02: Chips with >25V VPP remain `vpp-exceeds-max` fail-closed (no chip in DB exceeds 25V today, but the taxonomy is preserved for future additions)
- Firmware `eprom_check_vpp`: runtime ±tolerance check catches miscalibrated VPP before any write pulse

---

## Project Constraints (from CLAUDE.md)

From `firestarter_app/CLAUDE.md`:
- `chip_database.json` is generated by `build_db.py` — do NOT edit by hand
- Constants/flag bits are duplicated between `constants.py` and `firestarter.h` — change both together. **This phase does NOT touch either file** (ceiling is in `build_db.py` + `check_dispatch.py` only)
- Tooling gate: `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules) + `pytest --cov-fail-under=70`
- Devcontainer Python 3.12 masks CI py3.9/3.11 — validate `ruff check --target-version py39 .` before claiming CI green
- Gitlinks in meta-repo are NOT bumped per-phase — only at beta cut

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The on-bench shield's boost converter PCB hardware can physically output ≥25V (RURP product page "5–27V" claim applies to the operator's Rev 2.2 unit) | 25V Rail Capability | If the bench shield's PCB feedback resistors are calibrated for ≤22V hardware output, the operator must recalibrate R1 or change PCB resistors before graduation can proceed; the hardware gate (NMOS-01) explicitly handles this case |
| A2 | The `firestarter vpp` command (without a chip argument) raises the VPP rail to the hardware setpoint and measures it correctly with current R1/R2 calibration | Dry-Run Command | If the hardware VPP setpoint is lower than expected, the measurement will reveal it — this is the desired behavior of the gate, not a risk |
| A3 | SAFE-03 parity test (`test_revision_constants_parity.py::test_flag_values_match_firmware`) does not reference `build_db.py` constants and therefore requires no update | Lockstep/Parity | If the parity test somehow imports or references the ceiling constant, it might fail; low probability given the test targets FLAG_* and protocol constants |

**Most claims in this research were CONFIRMED by reading live code or running it directly.**

---

## Open Questions

1. **Which shield rev is mounted at phase execution time?**
   - What we know: operator has Rev 2.2, Rev 2.0, and modified Rev 0; only Rev 2.0/2.2 should be used for the bench proof (Rev 0 gets a warning in `eprom_check_vpp` rather than a hard error)
   - What's unclear: which shield will be mounted when the operator runs the dry-run
   - Recommendation: plan must include a `firestarter hw` check to verify shield revision before proceeding; document which rev is used in the VERIFICATION.md

2. **What NMOS chip is physically available for the bench write+verify?**
   - What we know: INTEL M2716 (DIP24, 2KB), INTEL M2732 (DIP24, 4KB), SGS-THOMSON ETC2716, ST ETC2716 are the 4 graduated chips
   - What's unclear: which physical NMOS chip the operator has in inventory
   - Recommendation: plan should call out the chip by alias (`M2716` or `M2732` or `ETC2716`) but let the operator choose from what's available; any of the 4 is valid for the bench proof

---

## Sources

### Primary (HIGH confidence — verified by reading live code or running it)

- `firestarter_app/tools/build_db.py` lines 107–117, 645–671 — `RURP_VPP_CEILING_MV`, `NMOS_TRUE_VPP_MV`, Site C classification logic [VERIFIED: codebase 2026-06-22]
- `firestarter_app/tools/check_dispatch.py` lines 78–93 — `_FAMILY_VPP_INVARIANTS`, `_DB_CHECKED_VPP_INVARIANTS` [VERIFIED: codebase]
- `firestarter_app/firestarter/chip_resolver.py` lines 54–57 — host-guard mechanism (`support_status != "supported"` check) [VERIFIED: codebase]
- `firestarter_app/firestarter/data/chip_database.json` — 4 `vpp-exceeds-max` chip entries confirmed by live Python query; M2732A standalone entries confirmed as already supported; zero chips with `vpp_mv > 25000` [VERIFIED: live query 2026-06-22]
- `firestarter/src/proms/eprom.cpp` lines 209–268 — `eprom_check_vpp` — no VPP ceiling constant; only chip-specific ±tolerance check [VERIFIED: codebase]
- `firestarter/src/boards/rurp_common.cpp` lines 52–71 — `rurp_read_voltage_mv` — R1/R2 are ADC scaling parameters for measurement, not VPP setpoint control [VERIFIED: codebase]
- `firestarter/include/rurp_shield.h` lines 49–50 — `VALUE_R1 = 270000`, `VALUE_R2 = 44000` (default firmware EEPROM values) [VERIFIED: codebase]
- `firestarter_app/tests/test_build_db_inclusion.py`, `test_chip_resolver.py`, `test_cli_handlers.py`, `test_check_dispatch_invariants.py` — all 7 broken tests identified by reading test source [VERIFIED: codebase]
- `python3 tools/check_dispatch.py` live run (2026-06-22) — PASS: 744 chips, 730 supported, 14 non-dispatchable [VERIFIED: live execution]

### Secondary (MEDIUM confidence — planning artifacts)

- `.planning/research/STACK.md` lines 163–188 — Phase 79 summary including RURP 5–27V product page reference, exact edit sites, programming electricals for 25V NMOS [CITED: planning artifact]
- `.planning/REQUIREMENTS.md` lines 24–28 — NMOS-01/02/03 requirements verbatim [CITED: planning artifact]
- `.planning/STATE.md` lines 67–72 — Phase 79 framing: host-only, hardware-gated, NMOS-01 first [CITED: planning artifact]
- `.planning/phases/77-erase-write-path-graduation-0x07-ee-eproms/77-RESEARCH.md` — graduation pattern (guard-removal-last, check_dispatch gate, lockstep parity) [CITED: planning artifact]

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Source-of-truth locations (build_db.py, check_dispatch.py) | HIGH | Confirmed by reading live code with line citations |
| 4 chip entries (vpp-exceeds-max, vpp_mv=25000, algorithm=0) | HIGH | Confirmed by live Python DB query |
| Firmware has no VPP ceiling | HIGH | Confirmed by grep + reading eprom_check_vpp source |
| Test breakage inventory (7 tests) | HIGH | Confirmed by reading all identified test files |
| Hardware VPP capability (25V reachable) | MEDIUM (A1) | RURP product page + AP3012 spec; actual bench shield output is unknown until NMOS-01 measurement |
| ADC can measure 25V (R1/R2 headroom) | HIGH | Calculated from rurp_read_voltage_mv formula; headroom to 35.6V confirmed |

**Research date:** 2026-06-22
**Valid until:** Stable (no firmware changes in this phase; build_db.py/check_dispatch.py are well-established; chip_database.json structure stable since v1.11/v1.12)
