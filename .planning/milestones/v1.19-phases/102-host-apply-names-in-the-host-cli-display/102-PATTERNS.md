# Phase 102: HOST — Apply Names in the Host CLI Display - Pattern Map

**Mapped:** 2026-07-01
**Files analyzed:** 3 (2 modified, 1 test modified) + 1 snapshot regenerated
**Analogs found:** 3 / 3 (all in-file "same construct" analogs — this phase MODIFIES existing structures)

> This is a display-only consolidation phase. There are no net-new files. For each
> modification target the "analog" is (a) the current shape of the same construct
> and (b) the established single-source pattern already applied in this file
> (`resolve_type_label` / `_ELECTRICAL_TYPE_LABEL`, the IN-01 fix). All paths below
> are in the `firestarter_app/` submodule. All line numbers were read live this
> session against the files as they stand.

## File Classification

| Modified/New File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/firestarter/ic_layout.py` (`get_chip_type_string` `proto_display`, L216–234) | presentation-model (label source) | transform (id → display string) | `_ELECTRICAL_TYPE_LABEL` (same file, L475–481) — the module-level single-source dict | exact (in-file, same idiom) |
| `firestarter_app/firestarter/ic_layout.py` (`_get_protocol_info_structured` `protocol_info_data`, L261–378) | presentation-model (info payload) | transform (id → structured dict) | its own current shape + the new canonical dict D-01 feeds | exact (in-file, self) |
| `firestarter_app/tests/test_ic_layout.py` (new invariant test) | test | request-response (assert) | `test_electrical_type_label_includes_fram` / `test_resolve_type_label_fram` (L100–124) | exact (same file, same style) |
| `firestarter_app/tests/__snapshots__/test_characterization.ambr` (`test_info_known_chip`) | test fixture (snapshot) | regenerate | its own current block (L324–368) | exact (self, regenerate one entry) |

## Pattern Assignments

### `firestarter/ic_layout.py` — the D-01 canonical map (NEW module-level dict)

**Analog:** `_ELECTRICAL_TYPE_LABEL` at **ic_layout.py:472–481** — the established
class-level single-source dict this phase mirrors. Note it is defined as a class
attribute (indented one level, sibling of the methods), not truly module-level;
match that placement so `self._PROTOCOL_DISPLAY_NAME` / `self._ELECTRICAL_TYPE_LABEL`
are accessed the same way. The docstring comment block above it (L470–474) is the
in-file convention for documenting why the map exists and which fallback it serves —
replicate that comment style, citing D-01/D-02 and `firestarter/doc/PROTOCOLS.md` col-2.

**Existing single-source dict shape to copy** (ic_layout.py:472–481):
```python
    _ELECTRICAL_TYPE_LABEL = {
        "EEPROM": "EEPROM",
        "Flash/EEPROM": "Flash/EEPROM",
        "FRAM": "FRAM",
        "SRAM": "SRAM",
        "UV-EPROM": "UV-EPROM",
    }
```

The new `_PROTOCOL_DISPLAY_NAME` is an `int → str` dict of the 12 ASCII-normalized
D-02 strings (0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29,
0x34). See RESEARCH §"Recommended Implementation Shape" for the exact literal.
Keep it a plain `int`-keyed dict literal — no typing modernization (py39 target,
Pitfall 4).

---

### `firestarter/ic_layout.py` — `get_chip_type_string` `proto_display` (MODIFIED, L216–234)

**Analog:** the same block, current shape. This is Map A — the **fallback path only**
(reached from `resolve_type_label` L515 when `electrical_type` is absent). No DB chip
triggers it (all carry `electrical.type`), so its strings are not on the rendered CLI
surface — but D-01 still requires it draw from the single map to prevent re-divergence.

**Current construct to replace** (ic_layout.py:215–236):
```python
        if protocol_id is not None:
            proto_display = {
                0x05: "Flash/EEPROM (5V, AMD-std)",
                0x06: "Flash/EEPROM (5V, AMD-alt sector-erase)",
                0x07: "UV-EPROM / MTP-Flash (12V VPP)",
                # ... 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29 ...
                # 0x35 (ITE EC MCU, 0 DB chips) and 0x39 (phantom, 0 DB chips) removed
                # in Phase 57 (DEC-05); ...
            }
            if protocol_id in proto_display:
                return proto_display[protocol_id]
        type_map = {1: "EPROM", 2: "Flash type 2", 3: "Flash type 3", 4: "SRAM"}
        return type_map.get(chip_type_int, f"Unknown ({chip_type_int})")
```

**Pattern to apply:** replace the inline `proto_display` literal with a lookup into
`self._PROTOCOL_DISPLAY_NAME`. **Preserve verbatim:**
- the `type_map` mem-type fallback (L235) and its `f"Unknown ({chip_type_int})"` tail (L236);
- the `0x35`/`0x39` exclusion comment (L228–231) — Pitfall 5, D-04 keeps phantoms out.

The `0x34` add lands automatically once the lookup reads the canonical map. Do NOT
change the `resolve_type_label` signature — it already routes here (L515).

---

### `firestarter/ic_layout.py` — `_get_protocol_info_structured` `protocol_info_data` (MODIFIED, L261–378)

**Analog:** the same list-of-tuples, current shape. This is Map B — the **only
rendered surface that changes** (feeds `eprom_info.py:297` `Protocol: {type} (ID:…)`).

**Current shape (list[tuple[int, str, tuple[str,str,str]]])** — representative tuple
and the return contract (ic_layout.py:280–288, 371–378):
```python
            (
                0x07,
                "EPROM/EEPROM",                              # <- the `type` field this phase changes
                (
                    "JEDEC 28-pin EPROM algorithm (also covers compatible 28C parts)",  # D-03: bullets UNTOUCHED
                    "Requires VPP on OE/VPP pin and byte-program style pulses",
                    "Vendors may enable software data protection/unlock cycles",
                ),
            ),
        # ...
        for pid, ptype, desc_tuple in protocol_info_data:
            if pid == protocol_id:
                return {
                    "id_hex": f"0x{pid:02X}",
                    "type": ptype,
                    "description_points": list(desc_tuple),
                }
        return None
```

**Pattern to apply (D-01 + D-03 + D-04):**
- **`type` field → canonical map.** Source the `type` slot from
  `self._PROTOCOL_DISPLAY_NAME` (either `.get(pid, ...)` in the return dict, or
  restructure so the tuple's name is read from the map). The 3 `description_points`
  bullets stay literal and unchanged (D-03).
- **Drop `0x11`** — delete the entire `0x11` "Flash Memory" / FWH tuple (currently
  ic_layout.py:334–342). D-04: zero DB chips, minipro cruft (Pitfall 5).
- **Add `0x34`** — new tuple. Name comes from the canonical map (`EEPROM - XICOR
  8051-bus`). Bullets: RESEARCH Open Question 1 — add minimal, non-minipro-heritage
  bullets (or a single "not implemented on RURP (FUT-01)" style line) and note the
  choice for Phase 103 (DOC-01), which owns prose. Do NOT import PROTOCOLS.md §1.12
  rich prose here (D-03 defers it).
- Preserve `id_hex` / `description_points` return keys — `eprom_info.py:295–300`
  reads `protocol['type']`, `protocol['id_hex']`, `protocol['description_points']`.

**Presenter (read-only, do NOT edit — consumption reference):**
- `eprom_info.py:297` `logger.info(f"Protocol: {protocol['type']} (ID: {protocol['id_hex']})")`
  — unclamped; full canonical name renders fine.
- `eprom_info.py:253` `Type:` line and `eprom_info.py:406–419` list/search Type
  column both go through `resolve_type_label` → `_ELECTRICAL_TYPE_LABEL` first, so
  they render electrical-type and are UNCHANGED. The `[:12]` clamp at
  **eprom_info.py:419** MUST NOT be widened (Pitfall 2 / GATE-03 layout).

---

### `firestarter_app/tests/test_ic_layout.py` — NEW single-source invariant test (Wave 0)

**Analog:** `test_electrical_type_label_includes_fram` (L100–113) and
`test_resolve_type_label_fram` (L116–124) — same file, same fixture, same idiom.
Copy this structure exactly.

**Fixture + import pattern to reuse** (test_ic_layout.py:17–33):
```python
import pytest

from firestarter.database import EpromDatabase
from firestarter.ic_layout import EpromSpecBuilder

@pytest.fixture(scope="module")
def db() -> EpromDatabase:
    return EpromDatabase(skip_local_override=True)

@pytest.fixture(scope="module")
def spec_builder(db: EpromDatabase) -> EpromSpecBuilder:
    return EpromSpecBuilder(db)
```

**Test-body pattern to copy** (test_ic_layout.py:116–124):
```python
def test_resolve_type_label_fram(
    spec_builder: EpromSpecBuilder,
) -> None:
    """resolve_type_label returns 'FRAM' for electrical_type='FRAM' ..."""
    result = spec_builder.resolve_type_label("FRAM")
    assert result == "FRAM", (
        f"resolve_type_label('FRAM') should return 'FRAM', got {result!r}"
    )
```

**Two new tests to write in this idiom** (RESEARCH Wave 0 Gaps + Phase Req→Test Map):
1. **Single-source invariant** — for a representative protocol id (e.g. `0x07`),
   assert `_get_protocol_info_structured(pid)["type"]` equals the fallback name from
   `get_chip_type_string(_, pid)` (i.e. both read the same `_PROTOCOL_DISPLAY_NAME`
   entry). Pins the D-01 anti-divergence guarantee (Pitfall 3 / IN-01 class).
2. **Coverage reconcile (D-04)** — assert `0x34` resolves to a name and that
   `_get_protocol_info_structured(0x11)` returns `None` (dropped tuple).

Use the same `spec_builder` module-scoped fixture; multi-line assert-with-message
form; f-string `{result!r}` in the message. Note the file already uses `noqa: UP006`
markers elsewhere — do not modernize typing (Pitfall 4).

---

### `firestarter_app/tests/__snapshots__/test_characterization.ambr` — regenerate one entry

**Analog:** the current `test_info_known_chip` block (L324–368), W27C512, protocol 0x07.

**The exact byte that changes** — snapshot line **364**:
```
  Protocol: EPROM/EEPROM (ID: 0x07)
```
becomes:
```
  Protocol: EPROM - 28-pin UV/EE, 13V VPP (ID: 0x07)
```
- L331 `Type: EEPROM` is electrical-type → MUST stay unchanged.
- L365–367 (the 3 bullets) → MUST stay byte-identical (D-03).

**Regeneration pattern (scoped, Pitfall 1):**
```
pytest tests/test_characterization.py::test_info_known_chip --snapshot-update
```
Then `git diff` the `.ambr` to confirm ONLY L364 changed. Do NOT blanket
`--snapshot-update` the suite (it would silently rewrite `test_list` / `test_search_w27` /
help snapshots).

## Shared Patterns

### Single-source / anti-divergence (the phase's core idiom)
**Source:** `resolve_type_label` (ic_layout.py:480–515) + `_ELECTRICAL_TYPE_LABEL`
(ic_layout.py:472–481) — the IN-01 fix.
**Apply to:** the new `_PROTOCOL_DISPLAY_NAME` map and both maps that consume it.
```python
    def resolve_type_label(self, electrical_type, type_int=0, protocol_id=None) -> str:
        etype = electrical_type or ""
        if etype in self._ELECTRICAL_TYPE_LABEL:
            return self._ELECTRICAL_TYPE_LABEL[etype]
        return self.get_chip_type_string(type_int, protocol_id)  # <- fallback into Map A
```
The pattern: one curated dict, consulted by every render path, so the two views can
never re-diverge. D-01 replicates this exact shape for protocol display names.

### Phantom / infeasible-protocol exclusion
**Source:** the `0x35`/`0x39`-removed comment (ic_layout.py:228–231); Phase 57 DEC-05
convention in `database.py` `KNOWN_PROTOCOLS`.
**Apply to:** keep `0x35`/`0x39` out of both maps; drop `0x11` from Map B (D-04).
Preserve the exclusion comment verbatim — it is the in-file record of *why* they are absent.

### ASCII-normalization (D-02)
**Source:** the D-02 decision; canonical strings from `firestarter/doc/PROTOCOLS.md`
col-2 header table (lines 32–43).
**Apply to:** every value in `_PROTOCOL_DISPLAY_NAME` — em-dash `—` and en-dash `–`
rendered as ASCII `-`. No backslashes (py3.11 f-string trap, Pitfall 4). Document the
deviation in the map's comment so Phase 103 (DOC-01) records it.

## No Analog Found

None. Every construct this phase touches already exists in the codebase; the new
invariant test has direct sibling analogs in the same test file. No RESEARCH.md-only
patterns are needed.

## Gate / Regression Guards (read-only — must stay green)

| Guard | Path | Why unaffected (display-only) |
|-------|------|-------------------------------|
| GATE-02 | `firestarter_app/tools/diff_db.py` + `tests/test_diff_db_gate.py` | operates on `chip_database.json` bytes; this edits Python source only |
| GATE-01 | `firestarter_app/tools/check_dispatch.py` + `tests/test_dispatch_mirror.py` + `tests/test_check_dispatch_invariants.py` | numeric dispatch invariants; display strings are not a lookup/dispatch key |
| GATE-03 | structural — verify no edit touches `main.py` / `cli_handlers.py` grammar, and the `[:12]` clamp at `eprom_info.py:419` is not widened | change confined to `ic_layout.py` display maps + one test |

## Metadata

**Analog search scope:** `firestarter_app/firestarter/` (ic_layout.py, eprom_info.py),
`firestarter_app/tests/` (test_ic_layout.py, test_characterization snapshot).
**Files read this session:** ic_layout.py (L205–236, 259–378, 470–515),
eprom_info.py (L245–304, 400–424), test_ic_layout.py (L1–124), the `.ambr`
`test_info_known_chip` block (L324–368).
**Pattern extraction date:** 2026-07-01
**CI note:** ruff target py39 / mypy 3.9, CI runs py3.11; devcontainer is py3.12 —
treat sign-off as CI-PENDING/structurally-green (Phase 98 precedent).
