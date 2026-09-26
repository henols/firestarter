# Phase 106: HOST — Host `mem_type` Removal - Pattern Map

**Mapped:** 2026-07-02
**Files analyzed:** 9 (5 runtime source + 4 test/tool sites; edit-in-place, no new source files)
**Analogs found:** 9 / 9 (all in-file / sibling-test analogs — no cross-file search needed)

> **Phase shape note:** This is a pure edit-in-place cleanup phase. There are NO
> new source files. The only net-new artifact is one added test case (D-06) in the
> existing `tests/test_chip_resolver.py`. Therefore every "closest analog" is the
> **existing pattern already living in the file being edited** (or its sibling
> test), NOT a different file elsewhere in the codebase. The planner copies from
> the same file it is editing.

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `firestarter/chip_resolver.py` | resolver / guard | request-response (pre-serial refusal) | in-file `support_status` guard (`:51-57`) | exact (same site, same exception) |
| `firestarter/database.py` | model / DB conversion | transform (record → wire dict) | in-file `_map_data`/`convert_to_programmer` mapped-dict pattern | exact (delete-in-place) |
| `firestarter/ic_layout.py` | presentation / label helper | transform (record → display label) | in-file tiered `resolve_type_label` → `get_chip_type_string` (`:502-534`, `:203-223`) | exact (drop last tier + param) |
| `firestarter/eprom_info.py` | view (list/search) | transform (record → table cell) | in-file `resolve_type_label` caller (`:405-410`) | exact (drop dead positional arg) |
| `tests/test_val_wire_*.py` (6 files, 7 fns) | test | request-response (wire-shape assert) | in-file `test_eprom_wire_dict_dispatches_to_configure_eprom` (`:79-91`) | exact (delete-and-invert) |
| `tests/test_chip_resolver.py` (`:43` + D-06 new) | test | request-response (refusal assert) | in-file `support_status` refusal tests (`:66-132`) | exact (D-06 mirrors `:122-132`) |
| `tests/test_eprom_database.py` (`:101`) | test | transform (required-keys assert) | in-file required-keys tuple (`:95-102`) | exact (remove `"type"` from tuple) |
| `tests/test_ic_layout.py` (`:180`) | test | transform (label assert) | in-file positional `get_chip_type_string(0, pid)` call (`:176-185`) | exact (drop dead first arg — forced by D-03) |
| `tools/check_dispatch.py` + 3 dispatch-mirror tests | tool / gate | transform (dispatch simulation) | N/A — see **No Analog / Scope Decision** | scope-boundary (leave; OQ#1) |

## Pattern Assignments

### `firestarter/chip_resolver.py` (resolver / guard — HOST-04, D-01/D-02)

**Analog:** the existing `support_status` refusal in the SAME function, `resolve_chip`.

The new `algorithm`-presence guard MUST mirror this exact site, exception, and
pre-serial ordering. It lands **alongside** (immediately after) the
`support_status` block, still before `db.get_eprom` / `db.convert_to_programmer`
build any wire dict.

**Existing analog — support_status guard** (`chip_resolver.py:43-63`):
```python
    # Read the raw config to access support_status (not carried through _map_data).
    raw_config, _manufacturer = db.get_eprom_config(name)

    # not-found takes priority over the support_status guard: an absent chip cannot
    # have a support_status, so raise ChipNotFoundError immediately.
    if raw_config is None:
        raise ChipNotFoundError(name)

    # Support-status guard (D-12 / T-66-01): refuse every program-capable operation
    # for non-supported chips BEFORE convert_to_programmer builds any wire dict.
    # Driven by support_status, not the incidental electrical.type string.
    support_status = raw_config.get("support_status", "supported")
    if support_status != "supported":
        reason = raw_config.get("unsupported_reason", "unsupported on this hardware")
        raise ChipNotImplementedError(f"{name}: {reason}")

    full = db.get_eprom(name)
    data = db.convert_to_programmer(full) if full else None
    if not data:
        raise ChipNotFoundError(name)
    return data
```

**Copy-from directions for the new guard:**
- Read `algorithm` from the **un-mapped** `raw_config`, same object the
  `support_status` guard already reads — path is
  `raw_config.get("programming", {}).get("algorithm", 0)` (Pitfall 3 / A3: this
  is the DB record path, NOT the mapped `protocol-id` key which only exists
  post-`get_eprom`).
- Reject rule (D-01): refuse only when the value is **absent OR `0`** (present-
  and-non-zero = usable). Do NOT add a `KNOWN_PROTOCOLS` membership check.
- Reuse `ChipNotImplementedError` (already imported at `:13`) — no new exception.
- Message must name the chip and state a protocol/`algorithm` is required (D-02
  Claude's-discretion wording), same `f"{name}: ..."` shape as the analog.
- Place it AFTER the `support_status` block so a broken-but-supported override
  is what trips the algorithm guard (matches D-06 test intent).

**Exception reuse** — `exceptions.py:49-64` already documents the
refuse-before-serial semantics; do NOT add a type:
```python
class ChipNotImplementedError(EpromOperationError):
    """Raised when the host refuses a program-capable operation on a non-supported chip.
    ...
    The guard fires BEFORE any wire dict is built or serial byte emitted — the
    host will not drive hardware for a non-supported chip.
    """
```

---

### `firestarter/database.py` (model / DB conversion — HOST-01/HOST-02, D-04)

**Analog:** the in-file `_ALGO_MEM_TYPE` dict, the `determined_type` derivation,
and the two mapped-dict emit sites. All are deleted in place; no rewrite.

**DELETE — `_ALGO_MEM_TYPE` dict + its now-false header comment** (`database.py:46-65`):
```python
# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.
# Firmware dispatches on protocol first; mem_type is kept consistent for fallback paths.
_ALGO_MEM_TYPE = {
    0x05: 5,  # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
    ...
    0x29: 4,  # SRAM_512K_1M      → TYPE_SRAM
}
```

**DELETE — `determined_type` derivation block, incl. the "Generic Flash (legacy fallback only)" default** (`database.py:415-428`):
```python
        # Read algorithm integer directly — set by build_db.py from upstream protocol_id
        protocol_id = programming.get("algorithm", 0)

        # Derive mem_type from algorithm (D3). Fall back to electrical.type substring
        # only when algorithm is absent / 0 (legacy user-override DB entries).
        if protocol_id and protocol_id in _ALGO_MEM_TYPE:
            determined_type = _ALGO_MEM_TYPE[protocol_id]
        else:
            type_str = electrical.get("type", "")
            determined_type = 1  # Default to EPROM
            if "Flash" in type_str:
                determined_type = 2  # Generic Flash (legacy fallback only)
            elif "SRAM" in type_str:
                determined_type = 4
```
> **Keep** the `protocol_id = programming.get("algorithm", 0)` line — it feeds the
> surviving `"protocol-id"` mapped-dict key (`:454`). Delete only the mem_type
> derivation that follows it.

**DELETE the `"type": determined_type,` key ONLY — keep the mapped dict + `"electrical-type"`** (`database.py:441-457`):
```python
        data = {
            "name": ic.get("part_number"),
            "manufacturer": manufacturer,
            "memory-size": electrical.get("size_bytes", 0),
            "type": determined_type,          # <-- DELETE this line only
            "pin-count": pin_count,
            ...
            "protocol-id": protocol_id,        # <-- STAYS (surviving dispatch datum)
            "pin-map": pinout_key,
            "electrical-type": electrical.get("type", ""),  # <-- STAYS (D-04 ground truth)
        }
```

**DELETE the wire-emit `"type"` line — THE single wire emit site (HOST-01)** (`database.py:582-591`):
```python
        # Keys to keep from the full data
        programmer_data = {
            "memory-size": full_eprom_data.get("memory-size", 0),
            "type": full_eprom_data.get("type", 0),          # <-- DELETE this line only
            "algorithm": full_eprom_data.get("protocol-id", 0),  # <-- STAYS (sole dispatch datum)
            "pin-count": full_eprom_data.get("pin-count", 0),
            "vpp_mv": vpp_mv,
            "pulse-delay": full_eprom_data.get("pulse-delay", 0),
        }
```
> `eprom_operations.py` copies this dict verbatim (`command_dict = eprom_data_dict.copy()`
> at `:307`) with NO independent `type` injection — deleting the line here removes
> `type` from the wire entirely. No `eprom_operations.py` edit needed.

**Leave untouched** — `info_flags` erase-derivation (`:432-435`) keys on
`electrical.type in ("EEPROM","Flash/EEPROM")`, NOT on `mem_type`. Not part of
this axis.

---

### `firestarter/ic_layout.py` (presentation / label helper — HOST-03, D-03)

**Analog:** the in-file two-function tiered-fallback structure. D-03 removes the
LAST tier (numeric `type_map`) and the now-dead `type_int` / `chip_type_int`
parameter from both signatures; the `electrical.type` and protocol tiers stay.

**Tier 1 — `electrical.type` ground truth** (`ic_layout.py:499-531`, `resolve_type_label`):
```python
    def resolve_type_label(
        self,
        electrical_type: Optional[str],  # noqa: UP006
        type_int: int = 0,                       # <-- DROP this param (D-03)
        protocol_id: Optional[int] = None,  # noqa: UP006
    ) -> str:
        ...
        etype = electrical_type or ""
        if etype in self._ELECTRICAL_TYPE_LABEL:          # <-- Tier 1 STAYS
            return self._ELECTRICAL_TYPE_LABEL[etype]
        return self.get_chip_type_string(type_int, protocol_id)  # <-- delegates; drop type_int arg
```

**Tier 2 (protocol) + Tier 3 (numeric — DELETE)** (`ic_layout.py:203-223`, `get_chip_type_string`):
```python
    def get_chip_type_string(
        self, chip_type_int: int, protocol_id: int | None = None   # <-- DROP chip_type_int param (D-03)
    ) -> str:
        ...
        if protocol_id is not None:
            if protocol_id in self._PROTOCOL_DISPLAY_NAME:    # <-- Tier 2 STAYS
                return self._PROTOCOL_DISPLAY_NAME[protocol_id]
        type_map = {1: "EPROM", 2: "Flash type 2", 3: "Flash type 3", 4: "SRAM"}  # <-- DELETE (Tier 3)
        return type_map.get(chip_type_int, f"Unknown ({chip_type_int})")           # <-- REPLACE with: return "Unknown"
```

**Copy-from directions (D-03):**
- Drop `type_int` from `resolve_type_label` and `chip_type_int` from
  `get_chip_type_string` (CONTEXT calls both "`type_int`"; source names differ —
  handle both).
- Delete the numeric `type_map`; when neither `electrical.type` nor a known
  protocol resolves, return the bare string `"Unknown"` (D-03), replacing the
  old `f"Unknown ({chip_type_int})"`.
- Update the `resolve_type_label` docstring: remove the `type_int:` Arg line
  (`:524`).
- Keep tiers `_ELECTRICAL_TYPE_LABEL` (`:494-500`) and `_PROTOCOL_DISPLAY_NAME`
  (`:472-485`) exactly as-is.

**Caller in same file — `build_specifications`** (`ic_layout.py:562-566`): drop the
dead `eprom_data.get("type", 0)` positional arg:
```python
        chip_type_str = self.resolve_type_label(
            electrical_type,
            eprom_data.get("type", 0),   # <-- DROP this positional arg (D-04 ripple)
            eprom_data.get("protocol-id"),
        )
```

---

### `firestarter/eprom_info.py` (view — HOST-03, D-04 ripple)

**Analog:** the sibling `resolve_type_label` caller in `build_specifications`
above — identical shape. Drop the dead `ic.get("type", 0)` positional arg.

**Caller — `print_eprom_list_table`** (`eprom_info.py:405-410`):
```python
        # D-04: Type via the single shared helper (resolve_type_label).
        type_str = spec_builder.resolve_type_label(
            ic.get("electrical-type"),
            ic.get("type", 0),          # <-- DROP this positional arg (D-04 ripple)
            ic.get("protocol-id"),
        )
```

**Leave untouched (Pitfall 2 / Claude's-discretion confirmed):** `eprom_info.py:69`'s
`"type": "unknown"` is a **string-typed** raw-JSON display field in `_clean_config`'s
`key_map`, unrelated to the numeric `mem_type` axis. Removing it would regress the
`info`/`id` Type line. Do NOT touch it.

---

### `tests/test_val_wire_*.py` (test — HOST-01 proof, D-05 delete-and-invert)

**Analog:** the current per-protocol wire-shape test that reads `wire.get("type", 0)`
and passes it as the 2nd `dispatch()` arg. Flip to positively assert `"type"` is
ABSENT — the absence IS HOST-01's proof (same discipline as Phase 105 D-05).

**Current assertion (analog) — `test_val_wire_eprom.py:79-91`:**
```python
def test_eprom_wire_dict_dispatches_to_configure_eprom(make_comm, fake_serial) -> None:
    """dispatch(algorithm, type) returns 'configure_eprom' for the EPROM rep chip."""
    db = EpromDatabase()
    chip = db.get_eprom(_REP_CHIP)
    assert chip is not None, f"rep_chip '{_REP_CHIP}' not found in EpromDatabase"
    wire = db.convert_to_programmer(chip)
    algo = wire.get("algorithm", 0)
    mem_type = wire.get("type", 0)                    # <-- the line to invert
    handler = dispatch(algo, mem_type)
    assert handler == _EXPECTED_HANDLER, (...)
```

**Invert to:** `assert "type" not in wire` (the new positive proof), then for the
handler-dispatch assertion pass `0` as the 2nd arg — `dispatch(algo, 0)` (Pitfall 4:
`dispatch()`'s mem_type fallback chain is `protocol==0`-only, so a real non-zero
`algo` never consults it; the handler assertion stays valid). Do NOT read
`wire.get("type")` post-inversion — it is gone by design.

**Apply to all 7 test functions across 6 files:**
`test_val_wire_eprom.py:86-87`, `test_val_wire_flash_intel.py:84-85`,
`test_val_wire_nor_unlock.py:84-85`, `test_val_wire_5v_page.py:91-92`,
`test_val_wire_eeprom28c.py:84-85`, `test_val_wire_sram.py:88-89` **and** `:111-115`
(two functions in the SRAM file).

---

### `tests/test_chip_resolver.py` (test — D-06 new HOST-04 test + `:43` inversion)

**Analog A (for the new D-06 test):** the existing "guard fires before serial"
refusal test — copy its patch-and-assert-not-called structure exactly.

**`test_resolve_chip_guard_fires_before_convert_to_programmer`** (`test_chip_resolver.py:122-132`):
```python
def test_resolve_chip_guard_fires_before_convert_to_programmer(db):
    """No serial bytes (wire dict) are produced when resolve_chip raises for a non-supported chip.

    Patches db.convert_to_programmer to detect if it is called.  If the support_status
    guard fires correctly (BEFORE convert_to_programmer), the mock must never be called
    when ChipNotImplementedError is raised.
    """
    with patch.object(db, "convert_to_programmer") as mock_convert:
        with pytest.raises(ChipNotImplementedError):
            resolve_chip("X88C64P", db=db)
        mock_convert.assert_not_called()
```

**Copy-from directions for the D-06 test (SC#4):**
- Construct a deliberately-broken entry that is `support_status == "supported"`
  yet has `algorithm` absent / `0` — so the NEW algorithm guard fires, not the
  support_status guard. Recommended (research OQ#3): `patch.object(db, "get_eprom_config")`
  (and/or `get_eprom`) to return a synthetic raw record with
  `programming.algorithm` missing/`0` + `support_status: "supported"`.
- Assert `pytest.raises(ChipNotImplementedError)` AND
  `mock_convert.assert_not_called()` (reuse the `patch.object(db, "convert_to_programmer")`
  pattern above) to prove no serial byte was emitted.
- Fixture `db` (`:28-31`) already gives `EpromDatabase(skip_local_override=True)`.

**Analog B (for the `:43` required-keys inversion):** the existing required-keys
tuple that currently includes `"type"`:
```python
def test_resolve_chip_hit_has_required_programmer_keys(db):
    """The resolved dict carries the keys the firmware command builders expect."""
    result = resolve_chip("W27C512", db=db)
    for key in ("memory-size", "type", "algorithm", "pin-count", "vpp_mv", "flags"):  # <-- remove "type"
        assert key in result, f"Missing required key: {key}"
```
Remove `"type"` from the tuple (research row: `:43` inversion NOT named in CONTEXT
but forced by HOST-01).

---

### `tests/test_eprom_database.py` (test — required-keys inversion, NEW ripple)

**Analog:** identical required-keys tuple pattern as `test_chip_resolver.py:43`.
Remove `"type"` (NOT named in CONTEXT.md — discovered by research).

**`test_convert_to_programmer_required_keys_present`** (`test_eprom_database.py:95-102`):
```python
    def test_convert_to_programmer_required_keys_present(self):
        """Programmer config must carry the keys the firmware expects."""
        db = EpromDatabase(skip_local_override=True)
        eprom = db.get_eprom("W27C512")
        assert eprom is not None
        config = db.convert_to_programmer(eprom)
        for key in ("memory-size", "type", "algorithm", "pin-count", "vpp_mv", "flags"):  # <-- remove "type"
            assert key in config, f"Missing required key: {key}"
```

---

### `tests/test_ic_layout.py` (test — positional-call ripple, forced by D-03)

**Analog:** the in-file positional call to `get_chip_type_string(0, pid)` — the
`0` first arg is the dead `chip_type_int`. After the D-03 signature change, update
to `get_chip_type_string(pid)`.

**Site** (`test_ic_layout.py:176-185`):
```python
    for pid in spec_builder._PROTOCOL_DISPLAY_NAME:
        info = spec_builder._get_protocol_info_structured(pid)
        if info is None:
            continue
        fallback_label = spec_builder.get_chip_type_string(0, pid)   # <-- becomes get_chip_type_string(pid)
        assert info["type"] == fallback_label, (...)
```
> This is a compile-forcing ripple: the positional `0` must be dropped or the call
> will pass `pid` as the (now-removed) first param.

## Shared Patterns

### Refuse-before-serial (fail-closed dispatch)
**Source:** `chip_resolver.py:51-57` (support_status guard) + `exceptions.py:49-64`
(`ChipNotImplementedError`).
**Apply to:** the new HOST-04 algorithm-presence guard.
Single chokepoint, reuse the existing exception, raise BEFORE `convert_to_programmer`.
Mirrors firmware `protocol == 0 → 0xBB` (Phase 105 D-04/D-06). Read the value from
the un-mapped `raw_config`, same object as the support_status read.

### Delete-and-invert test discipline (prove the negative)
**Source:** Phase 105 D-05 (carried into this phase's D-05/D-06).
**Apply to:** all `test_val_wire_*.py` (assert `"type" not in wire`), the two
required-keys tuples (`test_chip_resolver.py:43`, `test_eprom_database.py:101`).
Prove HOST-01 by asserting `type` is ABSENT — do not keep-and-mutate the old
positive assertion.

### Single-source label helper (tiered fallback)
**Source:** `ic_layout.py:499-531` + `:203-223` (`resolve_type_label` →
`get_chip_type_string`); callers `ic_layout.py:562-566` + `eprom_info.py:405-410`.
**Apply to:** D-03. Editing the helper once fixes both `info` (build_specifications)
and `list`/`search` (print_eprom_list_table) views. Keep tier 1 (`_ELECTRICAL_TYPE_LABEL`)
+ tier 2 (`_PROTOCOL_DISPLAY_NAME`); delete tier 3 (numeric `type_map`) + the
`type_int`/`chip_type_int` param; land on `"Unknown"`.

### Verbatim wire-dict copy (one emit site)
**Source:** `database.py:582-591` (`convert_to_programmer`) → `eprom_operations.py:307`
(`command_dict = eprom_data_dict.copy()`, no independent `type` injection).
**Apply to:** HOST-01. There is exactly ONE `type` emit site; deleting the
`database.py:585` line removes `type` from the wire. No `eprom_operations.py` edit.

## No Analog / Scope Decision Required

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `tools/check_dispatch.py` + `tests/test_dispatch_mirror.py` + `tests/test_decoder.py` + `tests/test_build_db_inclusion.py` | tool / gate | transform (dispatch simulation) | These maintain their OWN `_ALGO_MEM_TYPE` and a `dispatch(protocol, mem_type)` **historical deadness-simulation** — distinct from the runtime `database.py` copy. Research OQ#1 + Assumption A1: canonical_refs list these under "non-regression gates (must stay green) ... unaffected by `type` removal." **Recommendation: LEAVE untouched in Phase 106** (verification artifact, not runtime dispatch). This is the ONE scope decision the planner must confirm explicitly in the plan's decision log — removing the tool copy cascades into all 3 test files. The `test_val_wire_*` inversions can still call `dispatch(algo, 0)` (Pitfall 4). |

**Also out of Phase 106 (research OQ#2 / A2):** the host
`MSG_ERR_MEM_TYPE_UNSUPPORTED = 0xAE` mirror in `messages.py` /
`tools/catalog/messages.toml` — CONTEXT.md is silent; it is codegen-generated
(never hand-edit). Flag for Phase 107 close, do NOT touch here.

## Metadata

**Analog search scope:** `firestarter_app/firestarter/{chip_resolver,database,ic_layout,eprom_info,exceptions}.py`;
`firestarter_app/tests/{test_chip_resolver,test_val_wire_eprom,test_eprom_database,test_ic_layout}.py`.
All analogs are in-file / sibling-test — no cross-tree search required for an
edit-in-place cleanup phase.
**Files scanned:** 9 (all read directly at HEAD of `v1.20-protocol-only-dispatch`).
**Pattern extraction date:** 2026-07-02
