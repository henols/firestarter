# Phase 60: Display-Layer Decode Correctness — Research

**Researched:** 2026-06-10
**Domain:** Python host CLI display layer — `ic_layout.py`, `database.py`, `eprom_info.py`
**Confidence:** HIGH — all claims verified against live code by direct execution or source read

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** The displayed Type comes from a curated `{electrical.type → display string}` map keyed on `electrical.type`. This map is the sole source of the Type label. The protocol/voltage detail (currently embedded via `get_chip_type_string`'s `proto_display` table) moves to the `protocol_info` block only.
- **D-02:** The "Can be erased" line reports electrical erasability only, derived from `electrical.type` / the erasable flag. EEPROM/Flash → erasable; UV-EPROM → not electrically erasable (UV-only). Does NOT reference firmware erase-command availability.
- **D-03:** `ic_layout.py` reads the raw `electrical` block directly. Fix `_map_data`'s stale erasable-flag derivation: `info_flags |= 0x10` must cover `electrical.type == "EEPROM"` (and `"Flash/EEPROM"`), not just `"Flash/EEPROM"`.
- **D-04:** Both layers: (a) synthetic fixtures per `electrical.type`; (b) parametrized real-DB smoke: EEPROM set (W27C512, SST27VF512, SST27SF512, W27C257) + UV-EPROM control set (M27C512, 27C256, 2764).
- **D-05:** Remove the `-- NOT VERIFIED --` marker from `firestarter info` output (`verified_str` field in `build_specifications`, L490–492).
- **D-06:** Audit every displayed field for correctness under `electrical.type` lens. Bound to correctness/not-misleading — not a redesign.
- **D-07:** Fix the `protocol_info` and `flags_info` blocks: the 0x10 bit semantic collision, the missing erasable property for EEPROMs, dead `_interpret_flags` entries, VPP voltage never shown, and protocol description text accuracy.

### Claude's Discretion

- The exact display strings inside the curated `electrical.type → label` map and the precise yes / no / "UV-only" wording of the "Can be erased" line (within the rules in D-01 / D-02).
- Whether to drop the `verified_str` field entirely or blank it / remove only the output row (D-05).
- Fallback label when `electrical.type` is absent/empty: fall back to the existing protocol-based label rather than crashing.

### Deferred Ideas (OUT OF SCOPE)

- Firmware electrical-erase support (so `firestarter erase W27C512` actually works) — explicit separate firmware backlog item.
- Full fix of the `vpp-pin` list-vs-int TypeError — belongs to v1.9 / GATE-1.8b; only touch it here if it directly blocks the D-04 smoke tests, and only minimally.

</user_constraints>

---

## Summary

Phase 60 is a targeted host-only Python display fix. The root cause is that `get_chip_type_string` (L203, `ic_layout.py`) keys on `protocol_id` to produce the Type label, collapsing W27C512 (EEPROM) and 2764 (UV-EPROM) into the identical "UV-EPROM / MTP-Flash (12V VPP)" string because both use `algorithm=7`. The `electrical.type` field in `chip_database.json` already carries the correct ground-truth distinction ("EEPROM" vs "UV-EPROM") from the Phase 59 `cca7d62` fix. The display layer just does not read it yet.

There are five confirmed, interrelated bugs: (1) the Type label, (2) "Can be erased" logic, (3) the erasable bit never setting in `_map_data` for `electrical.type="EEPROM"` chips, (4) a semantic collision at `_interpret_flags` bit 0x10, and (5) VPP voltage never appearing. All are in `ic_layout.py` and `database.py`. A sixth change (D-05) removes the `-- NOT VERIFIED --` marker.

The implementation requires six targeted edits across two files plus new/updated tests in one test file. The `test_info_known_chip` syrupy snapshot in `test_characterization.py` pins the current (wrong) output for W27C512 and MUST be updated as part of this phase — it is the regression canary after the fix, not a constraint against it.

**Primary recommendation:** Make all six edits to `ic_layout.py` / `database.py`, update the `test_info_known_chip` snapshot to the corrected output, and add the D-04 synthetic + smoke tests. The GATE-1.8b vpp-pin crash is already mitigated (`_first_pin` at L406-414) — the happy-path is safe.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Type label derivation | Host CLI (`ic_layout.py`) | Database mapping (`database.py`) | Label is a display concern; ground truth flows from DB via `electrical.type` |
| Erasable flag derivation | Database mapping (`_map_data`) | Display layer (`build_specifications`) | `info-flags & 0x10` is computed in `_map_data`, consumed in display |
| "Can be erased" string | Host CLI (`ic_layout.py`, `build_specifications`) | Raw config (`electrical.type`) | String composition is display; truth-gate is `electrical.type` |
| VPP display | Host CLI (`ic_layout.py`, `build_specifications`) | Mapped data (`vpp_volts`/`vpp_mv`) | Gating condition must move from `flags & 0x08` (always 0) to `vpp_mv > 0` |
| Test regression guard | Test layer (`test_characterization.py` snapshot) | — | Snapshot captures full operator output; must be updated to post-fix truth |

---

## Verified Line Numbers (CONTEXT.md drift table)

All line numbers were verified against the live code on 2026-06-10.

| CONTEXT.md reference | Actual line | Status |
|----------------------|------------|--------|
| `get_chip_type_string` ~L203 | L203 | EXACT |
| `_interpret_flags` L236–258 | L236–L258 | EXACT |
| `_get_protocol_info_structured` ~L260 | L260 | EXACT |
| `build_specifications` (assembler) | L469 | Not cited in CONTEXT — actual is L469 |
| `verified_str` L490–492 | L490–L492 | EXACT |
| "Can be erased" derivation L504–515 | L504–L515 | EXACT |
| `vpp_str` gate L517–520 | L517–L520 | EXACT |
| `flags_info` assembly L580–583 | L580–L583 | EXACT (was cited as L580–583) |
| `_ALGO_MEM_TYPE` L48 | L48 | EXACT |
| `_map_data` L383–460 | L383–L460 | EXACT |
| `get_eprom` L526 | L526 | EXACT |
| Erasable flag condition (D-03) | L432–L433 | EXACT |
| `_first_pin` ~L406–414 | L406–L414 (fn at L123) | `_first_pin` def = L123; used at L406-420 |

---

## Confirmed Bug Inventory

All six bugs were verified by reading live code and/or executing `prepare_detailed_eprom_data` directly.

### Bug 1: Type label keys on protocol_id, not electrical.type [VERIFIED: source read + live execution]

**File:** `ic_layout.py` L203–234, `build_specifications` L485–502

**Mechanism:** `get_chip_type_string(chip_type_int, protocol_id)` uses `protocol_id` first (the `proto_display` dict, L216–230). For both W27C512 (EEPROM) and 2764 (UV-EPROM), `protocol_id=0x07` maps to `"UV-EPROM / MTP-Flash (12V VPP)"`. The `chip_type_int` fallback (L233) is never reached for either because both have a known protocol.

**Live proof:**
```
W27C512: type_str = "UV-EPROM / MTP-Flash (12V VPP)"   ← WRONG
2764:    type_str = "UV-EPROM / MTP-Flash (12V VPP)"   ← correct for 2764, wrong framing for type
```

**DB truth:**
- W27C512: `electrical.type = "EEPROM"`, `algorithm = 7`
- 2764:    `electrical.type = "UV-EPROM"`, `algorithm = 7`
- SST27VF512: `electrical.type = "EEPROM"`, `algorithm = 7`
- SST27SF512: `electrical.type = "EEPROM"`, `algorithm = 7`
- W27C257:    `electrical.type = "EEPROM"`, `algorithm = 7`
- M27C512:    `electrical.type = "UV-EPROM"`, `algorithm = 7`

**D-01 fix target:** Add a curated `electrical_type_label` map in `build_specifications`; look up `electrical.type` from `raw_config_data["electrical"]["type"]` (already passed in); use it as the primary source for `type_str`. Fall back to the existing `get_chip_type_string` result when `electrical.type` is absent (legacy user-override entries).

### Bug 2: "Can be erased" keys on protocol_id, not electrical.type [VERIFIED: source read + live execution]

**File:** `ic_layout.py` L504–515

**Mechanism:** The can-erase block (L507–515) gates on `eprom_data.get("type") == 1 or 3`, then branches on `proto in (0x07, 0x08, 0x0B)` → `"false (UV erase only)"`. Since W27C512 has type=1 and proto=0x07, it hits the first branch and gets `"false (UV erase only)"` — wrong.

**Note on type=5 gap:** `Flash/EEPROM` chips with proto=0x05 get `type=5` from `_ALGO_MEM_TYPE`. The current can-erase block only checks `type==1 or type==3`, so `type=5` chips never receive a `can_erase_str` entry at all. D-02 will cover all `electrical.type`-based families uniformly, so this gap gets resolved as a side-effect.

**Live proof:**
```
W27C512: can_erase_str = "false (UV erase only)"   ← WRONG
27C256:  can_erase_str = "false (UV erase only)"   ← correct
```

**D-02 fix target:** Derive `can_erase_str` from `electrical.type` (accessed from `raw_config_data`). Map: `"EEPROM"` / `"Flash/EEPROM"` → electrically erasable message; `"UV-EPROM"` → UV-only message; `"SRAM"` → omit or "N/A (volatile)".

### Bug 3: Erasable bit never set in _map_data for electrical.type="EEPROM" [VERIFIED: source read + live execution]

**File:** `database.py` L432–433

**Mechanism:**
```python
if electrical.get("type") == "Flash/EEPROM":
    info_flags |= 0x00000010  # Can be electrically erased
```

The condition is `== "Flash/EEPROM"` but the 28 `electrical.type="EEPROM"` chips (the reclassified EEPROM family including W27C512) never match it. Result: all 28 EEPROM chips have `info-flags = 0x20` (chip_id only), `info-flags & 0x10 = 0`.

**Live proof:**
```
W27C512:    info-flags = 0x20  (bit 0x10 NOT set)
SST27VF512: info-flags = 0x20  (bit 0x10 NOT set)
Flash/EEPROM chips (e.g. AS29F002T): info-flags = 0x30  (bit 0x10 IS set)
```

**D-03 fix target (database.py L432):** Widen the condition to:
```python
if electrical.get("type") in ("EEPROM", "Flash/EEPROM"):
    info_flags |= 0x00000010
```

This also feeds `convert_to_programmer`'s `FLAG_CAN_ERASE` derivation (L587–592) which already reads `info-flags & 0x10`, so once D-03 fires for EEPROMs, the programmer command will also get `FLAG_CAN_ERASE` set — consistent with electrical truth (even though firmware erase command is out of scope, this bit is an accurate capability flag).

### Bug 4: _interpret_flags bit 0x10 semantic collision [VERIFIED: source read + live execution]

**File:** `ic_layout.py` L241–254 (`_interpret_flags` table)

**Mechanism:** `_map_data` sets `info_flags bit 0x10` to mean "electrically erasable" (D-03 will propagate this to EEPROM chips). But `_interpret_flags` labels `0x10` as `"Needs software write-enable/unlock sequence"` (L243) and labels `0x80` as `"Electrically erasable/writable device (EEPROM/Flash/SRAM)"` (L246).

**Live proof:**
```python
_interpret_flags(0x10) = ["Needs software write-enable/unlock sequence"]  ← wrong meaning
_interpret_flags(0x80) = ["Electrically erasable/writable device (EEPROM/Flash/SRAM)"]
```

After D-03 sets bit 0x10 for EEPROM chips, `flags_info` for W27C512 would render "Needs software write-enable/unlock sequence" — the opposite of the correct label.

**Survey of actually-derivable bits:**
Only two bits are ever set by `_map_data` in the current DB:
- `0x20` (458 chips) — set when `chip_id_check = True`
- `0x10` (340 chips) — set when `electrical.type == "Flash/EEPROM"` (these are the Flash/EEPROM family, not the 28-chip EEPROM family)

All other bits in `_interpret_flags` (0x08, 0x40, 0x80, 0x200, 0x4000, 0x8000, 0x400000) can never be set from the current DB pipeline — they are dead entries.

**D-07 fix target:** Reconcile bit 0x10 to mean "electrically erasable" in both `_map_data` and `_interpret_flags`. Remove or comment out the dead entries (0x08, 0x40, 0x80, 0x200, 0x4000, 0x8000, 0x400000) which can never fire from the new DB.

### Bug 5: VPP voltage never shown in firestarter info [VERIFIED: source read + live execution]

**File:** `ic_layout.py` L517–520

**Mechanism:**
```python
if (eprom_data.get("flags", 0) & 0x00000008):
    output_data["vpp_str"] = f"{eprom_data.get('vpp_volts', 'N/A')}v"
```

`_map_data` always sets `"flags": 0` (L447). The bit `0x00000008` never fires. Meanwhile `vpp_volts` is populated for 12V-VPP chips (W27C512: `vpp_volts=12.0`, `vpp_mv=12000`).

**Live proof:**
```
W27C512: vpp_str = "NOT PRESENT"   (despite vpp_volts=12.0, vpp_mv=12000)
```

**D-07 fix target:** Gate on `eprom_data.get("vpp_mv", 0) > 0` (or `vpp_volts > 0`) instead of the dead `flags & 0x08`.

### Bug 6: -- NOT VERIFIED -- marker shown for most chips [VERIFIED: source read + snapshot]

**File:** `ic_layout.py` L490–492

**Mechanism:**
```python
"verified_str": ""
if eprom_data.get("verified", False)
else "-- NOT VERIFIED --",
```

Most chips in `chip_database.json` have `verified=False` (the field is a DB field not set by `build_db.py` for most chips). W27C512 shows `"-- NOT VERIFIED --"` in the snapshot.

**D-05 fix target:** Either set `verified_str` always to `""`, or remove the key/row entirely. The presenter reads `chip_data.get("verified_str", "")` in `present_eprom_details` (eprom_info.py L223) — removing the key entirely is safe.

---

## Snapshot Impact (CRITICAL)

The `test_info_known_chip` syrupy snapshot in `tests/test_characterization.py` (L246) pins the CURRENT (wrong) W27C512 output:

```
  Eprom Info          -- NOT VERIFIED --
  ...
  Type:               UV-EPROM / MTP-Flash (12V VPP)
  Can be erased:      false (UV erase only)
  ...
  Flags: 0x00000020
    - Provides readable manufacturer/device ID
```

After the fix, the correct output will differ on:
- `Eprom Info` header line (D-05: `-- NOT VERIFIED --` removed)
- `Type:` line (D-01: EEPROM label)
- `Can be erased:` line (D-02: electrically erasable message)
- `VPP:` line (D-07: VPP voltage now shown — currently absent)
- `Flags:` value and properties (D-07: 0x30 with correct description after D-03+D-07)

**The planner MUST include a task to update this snapshot after the code edits.** Use `pytest --snapshot-update tests/test_characterization.py::test_info_known_chip` then inspect the new snapshot for correctness.

---

## Data Access Plumbing (D-03 electrical block access)

`ic_layout.py`'s `build_specifications` currently receives `eprom_data` (the `_map_data` output) but does NOT currently access the raw `electrical` block. However, `prepare_detailed_eprom_data` in `eprom_info.py` already receives `raw_config_data` (the full JSON record from `db.get_eprom_config()`), and `raw_config_data["electrical"]["type"]` is exactly what D-01 and D-02 need.

**Two implementation options:**

Option A (minimal change): Pass `electrical_type = raw_config_data.get("electrical", {}).get("type")` from `prepare_detailed_eprom_data` down into `build_specifications` as a new parameter.

Option B (direct): Have `build_specifications` accept an optional `raw_config` parameter (defaulting to `None`) and extract `electrical.type` from it internally. The caller in `prepare_detailed_eprom_data` passes it through.

Either works. The planner can choose; the tests should verify the result, not the path.

**The `raw_config_data` structure (verified):**
```python
raw_config_data = {
    "electrical": {
        "pin_count": 28, "size_bytes": 65536,
        "type": "EEPROM",          # ← ground truth
        "vcc": "5V", "vdd": "5V", "vpp": "12V", "vpp_mv": 12000
    },
    "part_number": "W27C512,W27E512",
    "pinout": "DIP28_27512",
    "programming": { "algorithm": 7, "chip_id_check": True, ... }
}
```

---

## Distinct electrical.type Values in the DB [VERIFIED: live execution]

```
"EEPROM":        28 chips  — the reclassified EEPROM family; bug 3 affects ALL of them
"Flash/EEPROM": 340 chips  — AMD/Intel/etc. flash; already get info-flags 0x10 (correct)
"SRAM":          76 chips  — type int = 4; no can_erase_str (correct — SRAM is volatile)
"UV-EPROM":     299 chips  — traditional UV-erasable EPROMs
```

**No other values exist.** The D-01 curated map needs exactly 4 entries (plus a fallback for absent/unknown). The D-02 can-erase logic needs exactly 3 cases (EEPROM, Flash/EEPROM, UV-EPROM; SRAM omits the row).

---

## vpp-pin list-vs-int TypeError: CONFIRMED MITIGATED [VERIFIED: live execution]

The GATE-1.8b witness (`test_eprom_info.py` docstring, L9–10) documents that the full `prepare_detailed_eprom_data` happy path was historically blocked by a `vpp-pin <= pin_count` TypeError. This crash is **confirmed resolved** by `_first_pin` at L123 (extracts scalar from list before comparison, used at L406-420).

**Live proof — full happy-path executed without crash:**
```python
# W27C512 full happy-path:
result = presenter.prepare_detailed_eprom_data("W27C512", w27_data, None, raw_conf, mfr)
→ OK (no crash, full output_data returned)

# 27C256 full happy-path:
result = presenter.prepare_detailed_eprom_data("27C256", chip_27c256, None, raw_27c256, mfr2)
→ OK (no crash, full output_data returned)
```

D-04's real-DB smoke tests against the full path are safe. The existing `test_info_known_chip` snapshot test (which calls `firestarter info W27C512` as a subprocess) also passes and confirms the full path is live and stable.

The GATE-1.8b constraint in `test_eprom_info.py`'s docstring is now stale — the vpp-pin bug is fixed. The planner should update the docstring comment as part of this phase.

---

## Architecture Patterns

### Data Flow for the info Command

```
cli_handlers.py info()
        |
        v db.get_eprom(chip_name)           → eprom_data dict (mapped by _map_data)
        | db.get_eprom_config(chip_name)    → raw_config_data dict (has electrical block)
        | db.convert_to_programmer(data)   → programmer_cmd dict
        v
eprom_info.py EpromConsolePresenter.prepare_detailed_eprom_data(
    eprom_name, eprom_data, programmer_cmd, raw_config_data, manufacturer
)
        |
        v ic_layout.py EpromSpecBuilder.build_specifications(eprom_data)
          [CURRENTLY: does not receive raw_config_data]
          [AFTER FIX:  receives electrical.type from raw_config_data]
        |
        v present_eprom_details(combined_data)   → logs to terminal
```

### Anti-Patterns to Avoid

- **Accessing `electrical.type` from `eprom_data` (the mapped dict):** `_map_data` does not pass `electrical.type` through to the mapped output. Only `info-flags` carries a derived signal. Always source `electrical.type` from `raw_config_data["electrical"]["type"]`.
- **Treating `flags` (L447, always `0`) as a bitmask for display decisions:** The `flags` key in the mapped dict is always `0` (no raw upstream flags are carried into the new DB format). Use `info-flags` for the erasable/chip-id derivations, or `raw_config_data` for the electrical truth.
- **Relying on `type` integer alone:** `_ALGO_MEM_TYPE` maps both `0x07` (EPROM_STD, used by UV-EPROMs) and `0x0D` (EEPROM_POLL, used by 28C family) to `type=1` (TYPE_EPROM). The `type` integer cannot distinguish EEPROM from UV-EPROM for the `0x07` family.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Snapshot update after display fix | Hand-edit the `.ambr` file | `pytest --snapshot-update tests/test_characterization.py::test_info_known_chip` then review the diff |
| Enumerating all `electrical.type` values | Scanning source manually | Already done: exactly 4 values: `"EEPROM"`, `"Flash/EEPROM"`, `"SRAM"`, `"UV-EPROM"` |
| Checking for new crashes | Writing a full scan test | The D-04 parametrized smoke set covers the relevant families; a crash-only full-DB scan is optional |

---

## Common Pitfalls

### Pitfall 1: Forgetting to update the syrupy snapshot

**What goes wrong:** After fixing the W27C512 display, `test_info_known_chip` fails because the snapshot still contains the old (wrong) output. `pytest` exit code is non-zero; CI fails.

**How to avoid:** Treat snapshot update as a mandatory task step after code edits. Run `pytest --snapshot-update tests/test_characterization.py::test_info_known_chip` and inspect the diff to confirm the new snapshot reflects the correct EEPROM output.

### Pitfall 2: D-03 fix changes convert_to_programmer behavior

**What goes wrong:** Widening the erasable condition in `_map_data` to include `"EEPROM"` causes `info-flags & 0x10` to fire for W27C512 etc., which in turn causes `convert_to_programmer` (L587–592) to set `FLAG_CAN_ERASE` in programmer commands. This is electrically correct (the chip can be erased) but may surprise tests that snapshot the programmer command.

**How to avoid:** Check whether any existing tests snapshot `convert_to_programmer` output for an EEPROM-family chip. If so, update those snapshots too. The D-04 smoke set assertions should explicitly verify `can_erase_str` but not over-constrain the programmer command JSON.

### Pitfall 3: Accessing electrical.type on legacy user-override DB entries

**What goes wrong:** User-override `~/.firestarter/database.json` entries may not have an `electrical.type` field. Using `.get("electrical", {}).get("type")` without a fallback causes `None`, which crashes the curated map lookup or produces a blank label.

**How to avoid:** Always use `electrical_type or ""` as the lookup key, with an explicit fallback to the existing protocol-based label when the value is absent or empty.

### Pitfall 4: Dead _interpret_flags entries creating misleading flags_info output

**What goes wrong:** After D-03 sets bit 0x10 for the 28 EEPROM chips, `_interpret_flags(0x30)` returns `["Needs software write-enable/unlock sequence", "Provides readable manufacturer/device ID"]` — the first entry is wrong. Forgetting D-07's `_interpret_flags` fix means the flags_info block contradicts the Type label.

**How to avoid:** Implement D-07 atomically with D-03. The `_interpret_flags` fix and the `_map_data` fix must land in the same task.

### Pitfall 5: Cover floor regression

**What goes wrong:** Adding new tests to `test_eprom_info.py` that exercise the happy-path for the first time increases `ic_layout.py` and `eprom_info.py` coverage significantly. If any test is accidentally skipped or parametrized incorrectly, coverage may drop below 70%.

**Current baseline:**
- Full suite total: 75.65% (safely above 70% floor)
- `ic_layout.py`: 13% (subset tests only; new tests will raise this significantly)
- `eprom_info.py`: 23% (full-suite); 60% (in targeted subset)

Increased coverage from D-04 tests is expected and welcome. The floor can only go up, not down.

---

## Validation Architecture

All validation is board-independent (no hardware required). `firestarter info` is pure host-side code — confirmed by live execution in devcontainer with no Arduino attached.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (with syrupy for snapshots) |
| Config file | `pyproject.toml` (pytest section) |
| Quick run command | `pytest tests/test_eprom_info.py -x -q` |
| Full suite command | `pytest --cov=firestarter --cov-fail-under=70 -q` |
| Ruff check | `ruff check firestarter/ tests/` |
| Ruff format check | `ruff format --check firestarter/ tests/` |

### Phase Success Criteria → Test Map

| Criterion | Behavior | Test Type | Automated Command | File |
|-----------|----------|-----------|-------------------|------|
| SC-1: EEPROM set shows EEPROM type | W27C512/SST27VF512/SST27SF512/W27C257 → Type = EEPROM label | parametrized real-DB smoke | `pytest tests/test_eprom_info.py::test_eeprom_type_label_smoke -x` | New — Wave 0 |
| SC-1: EEPROM set shows electrically erasable | W27C512/SST27VF512 → can_erase_str reflects electrically erasable | parametrized real-DB smoke | same as above | New — Wave 0 |
| SC-2: UV-EPROM control no regression | M27C512/27C256/2764 → Type = UV-EPROM label, can_erase = UV-only | parametrized real-DB smoke | `pytest tests/test_eprom_info.py::test_uv_eprom_type_label_smoke -x` | New — Wave 0 |
| SC-3: synthetic fixture isolation | Hand-built records per electrical.type drive label/can-erase in isolation | unit (synthetic fixture) | `pytest tests/test_eprom_info.py::test_synthetic_eeprom_type -x` | New — Wave 0 |
| SC-4: D-01 reads electrical.type not protocol | Synthetic EEPROM record with proto=0x07 → shows EEPROM label not UV-EPROM | unit (synthetic fixture) | same test module | New — Wave 0 |
| SC-5: VPP shown for 12V-VPP chips | W27C512 → `vpp_str` present in output_data | unit or smoke | in smoke test assertions | New |
| SC-6: verified_str removed | output_data never contains `-- NOT VERIFIED --` | unit | in synthetic fixture test | New |
| D-03 fix: erasable bit set | `_map_data` for W27C512 → `info-flags & 0x10 != 0` | unit | `pytest tests/test_eprom_database.py::test_eeprom_erasable_flag -x` | New — Wave 0 |
| D-07: flags_info correct label | `_interpret_flags(0x10)` → electrically erasable text (not "needs SWE") | unit | in test_eprom_info or test_ic_layout | New — Wave 0 |
| Snapshot non-regression: W27C512 info | `firestarter info W27C512` full output matches updated snapshot | subprocess snapshot | `pytest tests/test_characterization.py::test_info_known_chip` | Exists — must be UPDATED |
| Existing tests green | All 534+ current tests pass unmodified | suite | `pytest -q` | Exists |
| Ruff clean | No lint or format issues | lint | `ruff check firestarter/ && ruff format --check firestarter/` | Existing CI |
| Coverage floor | Total coverage ≥ 70% | coverage | `pytest --cov-fail-under=70` | Existing CI |

### Synthetic Fixture Design

Synthetic records must be minimal dicts matching the `_map_data` output shape (for `build_specifications` tests) or the raw DB record shape (for `_map_data` unit tests). The D-01 fix requires `electrical.type` from `raw_config_data`, so synthetic tests should also supply a minimal `raw_config_data`.

**Minimum synthetic set (unit coverage for each `electrical.type`):**

```python
# Synthetic EEPROM record (raw_config shape)
SYNTH_EEPROM_RAW = {
    "electrical": {"pin_count": 28, "size_bytes": 65536, "type": "EEPROM",
                   "vcc": "5V", "vpp": "12V", "vpp_mv": 12000},
    "part_number": "SYNTH_EEPROM",
    "pinout": "DIP28_27512",
    "programming": {"algorithm": 7, "chip_id_check": True},
}

# Synthetic UV-EPROM record
SYNTH_UV_EPROM_RAW = {
    "electrical": {"pin_count": 28, "size_bytes": 65536, "type": "UV-EPROM",
                   "vcc": "5V", "vpp": "12V", "vpp_mv": 12000},
    "part_number": "SYNTH_UV_EPROM",
    "pinout": "DIP28_27512",
    "programming": {"algorithm": 7, "chip_id_check": False},
}

# Synthetic Flash/EEPROM record
SYNTH_FLASH_RAW = {
    "electrical": {"pin_count": 32, "size_bytes": 131072, "type": "Flash/EEPROM",
                   "vcc": "5V", "vpp": "0V", "vpp_mv": 0},
    "part_number": "SYNTH_FLASH",
    "pinout": "DIP32_STD",
    "programming": {"algorithm": 5, "chip_id_check": True},
}

# Synthetic SRAM record
SYNTH_SRAM_RAW = {
    "electrical": {"pin_count": 28, "size_bytes": 8192, "type": "SRAM",
                   "vcc": "5V", "vpp": "0V", "vpp_mv": 0},
    "part_number": "SYNTH_SRAM",
    "pinout": "DIP28_27512",
    "programming": {"algorithm": 0x28, "chip_id_check": False},
}
```

### Parametrized Real-DB Smoke Set

```python
@pytest.mark.parametrize("chip_name,expected_type_keyword,expect_erasable", [
    ("W27C512",    "EEPROM",    True),
    ("SST27VF512", "EEPROM",    True),
    ("SST27SF512", "EEPROM",    True),
    ("W27C257",    "EEPROM",    True),
    ("M27C512",    "UV-EPROM",  False),
    ("27C256",     "UV-EPROM",  False),
    ("2764",       "UV-EPROM",  False),
])
def test_type_label_and_erase_smoke(chip_name, expected_type_keyword, expect_erasable, db, presenter):
    data = db.get_eprom(chip_name)
    raw, mfr = db.get_eprom_config(chip_name)
    result = presenter.prepare_detailed_eprom_data(chip_name, data, None, raw, mfr)
    assert result is not None
    assert expected_type_keyword in result["type_str"]
    if expect_erasable:
        assert "erase" in result.get("can_erase_str", "").lower()
        # Must NOT say UV-only
        assert "uv" not in result.get("can_erase_str", "").lower()
    else:
        assert "uv" in result.get("can_erase_str", "").lower()
```

### Wave 0 Gaps (files that must be created before implementation tasks)

- [ ] No new test files needed — tests go into the existing `tests/test_eprom_info.py`
- [ ] The `db` and `presenter` fixtures already exist in `test_eprom_info.py` at module scope — reuse them
- [ ] Optional: a thin `tests/test_ic_layout.py` for the `_interpret_flags` unit test (avoids polluting eprom_info test with a layout-layer concern); or fold into `test_eprom_info.py` — planner's call

### Sampling Rate

- **Per task commit:** `pytest tests/test_eprom_info.py tests/test_characterization.py -q`
- **Per wave merge:** `ruff check firestarter/ && ruff format --check firestarter/ && pytest --cov-fail-under=70 -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

---

## Security Domain

This phase makes no changes to authentication, session management, access control, cryptography, or network transport. The only input is `electrical.type` strings from the already-trusted local `chip_database.json`. No new ASVS categories apply. Security enforcement: not applicable.

---

## Environment Availability

`firestarter info` requires no hardware. Confirmed working in devcontainer:

| Dependency | Available | Version | Notes |
|------------|-----------|---------|-------|
| Python 3.12 | Yes | 3.12.13 | Devcontainer default |
| firestarter (editable install) | Yes | 3.0.0b8 | `pip install -e '.[test]'` if wiped |
| pytest + syrupy | Yes | present | Part of `.[test]` extras |
| ruff | Yes | present | Part of CI gate |
| Arduino / board | Not required | — | `info` is host-only |

---

## Project Constraints (from CLAUDE.md)

- `ruff check` + `ruff format --check` enforced on every PR; must be clean before commit
- `pytest --cov-fail-under=70` enforced; current baseline is 75.65% (healthy headroom)
- **mypy strict applies to 8 modules**: `main`, `cli_handlers`, `chip_resolver`, `frame_parser`, `codec`, `address_parser`, `exceptions`, `serial_comm`. `ic_layout.py` and `eprom_info.py` are NOT in the strict set — non-strict mypy only
- `chip_database.json` is generated (do NOT edit by hand); all DB content comes from `build_db.py` output
- Sub-repo commit discipline: all commits go to `v1.11-infoic-decode-correctness` branch in `firestarter_app/`; no direct commits to main or beta

---

## Open Questions

1. **`_interpret_flags` table pruning scope (D-07)**
   - What we know: Only 2 bits (0x10, 0x20) are ever set from the current DB. The other 7 entries (0x08, 0x40, 0x80, 0x200, 0x4000, 0x8000, 0x400000) are dead code.
   - What's unclear: Whether to remove the dead entries entirely or comment them out as "not derivable from current DB, retained for reference."
   - Recommendation: Remove entirely (cleaner, less misleading). If a future DB revision adds these signals, they can be re-added with proper provenance. Claude's discretion per D-07.

2. **SRAM "Can be erased" display (D-06 audit)**
   - What we know: SRAM chips (type=4) currently get no `can_erase_str` entry, so the "Can be erased" row is absent from their `info` output. This is the current behavior.
   - What's unclear: Whether the operator wants SRAM to show a row (e.g. "N/A (volatile)") or omit it.
   - Recommendation: Omit the row for SRAM (no change from current behavior). SRAM volatility is better conveyed by the Type label than a "can erase" row. Claude's discretion.

3. **`test_list` snapshot update scope**
   - What we know: The `test_list` snapshot (line 362+) pins all chips' Type strings in the list view. `print_eprom_list_table` calls `get_chip_type_string` without `electrical.type` — it uses type int only (L332 of eprom_info.py), which returns `"EPROM"` for type=1 chips (not the protocol-based string). This is a DIFFERENT display path from `info`.
   - What's unclear: D-01 only changes the `info` command; the list view uses a separate code path (`print_eprom_list_table`, not `build_specifications`). Verify during implementation whether `test_list` snapshot needs updating.
   - Recommendation: Audit the list view path for type=1 chips during implementation; if unchanged, the `test_list` snapshot requires no update.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `convert_to_programmer` sets `FLAG_CAN_ERASE` based on `info-flags & 0x10`; after D-03 this will fire for EEPROM chips | Bug 3 / D-03 | If the convert_to_programmer logic changes, programmer commands may be inconsistent — low risk, code was read directly |

All other claims are verified by live execution or direct source read.

---

## Sources

### Primary (HIGH confidence — verified by direct source read and/or live execution)

- `firestarter_app/firestarter/ic_layout.py` — L203-234 `get_chip_type_string`, L236-258 `_interpret_flags`, L260-379 `_get_protocol_info_structured`, L469-587 `build_specifications`, L490-492 `verified_str`, L504-515 can-erase block, L517-520 `vpp_str` gate, L580-583 `flags_info` assembly
- `firestarter_app/firestarter/database.py` — L48 `_ALGO_MEM_TYPE`, L383-460 `_map_data`, L428-433 erasable flag condition, L526 `get_eprom`, L555-595 `convert_to_programmer`
- `firestarter_app/firestarter/eprom_info.py` — L94-163 `prepare_detailed_eprom_data`, L208-311 `present_eprom_details`
- `firestarter_app/firestarter/cli_handlers.py` — L322-354 `info` command, confirming `raw_config_data` is already passed to presenter
- `firestarter_app/tests/test_eprom_info.py` — existing fixtures and GATE-1.8b context
- `firestarter_app/tests/test_characterization.py` — L246-257 `test_info_known_chip` snapshot test
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — L313-360 current W27C512 snapshot
- `firestarter_app/firestarter/data/chip_database.json` — `electrical.type` distribution verified by live Python enumeration

### Live execution results (verified 2026-06-10)

- `EpromDatabase(skip_local_override=True).get_eprom("W27C512")` → `info-flags=0x20`, no 0x10 bit
- `prepare_detailed_eprom_data("W27C512", ...)` → `type_str="UV-EPROM / MTP-Flash (12V VPP)"`, `can_erase_str="false (UV erase only)"`, no crash
- `_interpret_flags(0x10)` → `["Needs software write-enable/unlock sequence"]` (wrong label)
- Full test suite: 534+ tests, 75.65% coverage, all passing including 28 snapshots

---

## Metadata

**Research date:** 2026-06-10
**Valid until:** 2026-07-10 (stable code, 30-day horizon)

**Confidence breakdown:**
- Bug identification: HIGH — each bug verified by direct source read and/or live execution
- Line numbers: HIGH — all confirmed against live code
- Validation architecture: HIGH — test patterns match existing project conventions
- Snapshot impact: HIGH — snapshot content read directly, exact lines cited
