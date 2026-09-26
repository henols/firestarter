# Phase 197: The override mechanism and the program pulse - Pattern Map

**Mapped:** 2026-09-18
**Files analyzed:** 5 new + 5 modified
**Analogs found:** 9 / 10 (1 has no in-repo analog: the D-12 inventory has a `.planning/` precedent, not a code one)
**Sub-repo:** `firestarter_app/` (git submodule, read on `beta` — not switched)

---

## ⚠️ Hard rule that governs every proposed excerpt in this document

**Write NO comments into product source.** Nothing under `firestarter_app/` or `firestarter_fw/`
gets a `#`, `//` or `/* */` line, for any reason, and no plan may make "a comment exists" an
acceptance criterion. Click docstrings in `firestarter_app` are user-facing `--help` text and are
exempt; module/class/function docstrings in `tests/` are the established house style and are also
not comments in the sense this rule forbids.

**Every excerpt below tagged `[QUOTED — current state]` reproduces existing source that contains
comments.** That is a quotation, not a template. Copy its *structure*, never its comment lines.
Excerpts tagged `[PROPOSED SHAPE]` are comment-free and must stay that way.

A second consequence the planner must carry into tasks: deleting `NMOS_TRUE_VPP_MV`,
`_AT28C_DIP24_NAMES` and `_ETYPE_RELABEL` **orphans the prose around them** (see the quoted blocks
at `build_db.py:84-90`, `:494-505`, `:567-572`, `:580-585`, `:630-636`). The rule requires reading
the remainder after each deletion and confirming every pronoun still has an antecedent. Adding
replacement prose is forbidden; the correct disposition of an orphaned comment is deletion.

---

## File Classification

| New/Modified File | New/Mod | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `firestarter_app/tools/datasheet_overrides.json` | NEW | config / data | file-I/O (read at build) | `firestarter_app/tools/extra_chips.json` | **partial** — same slot, inverted semantics |
| loader + applier in `firestarter_app/tools/build_db.py` | MOD | utility (generator) | transform (decode → substitute → derive) | the `extra_chips` merge `:716-737` (file read) + `interpret_timing` `:339-365` and the `page_size` check `:739-751` (raise shape) | role-match |
| `firestarter_app/tests/golden/wire_dict_expected_deltas_197.json` | NEW | test fixture (golden) | batch / layered-golden | `tests/golden/wire_dict_expected_deltas_194.json` | **exact** |
| `firestarter_app/tests/test_datasheet_overrides.py` | NEW | test | request-response (unit) | `tests/test_build_db_interpret_timing.py` (import idiom + fail-closed legs) and `tests/test_extra_chips_supplement.py` (sibling-data-file shape) | **exact** (two complementary analogs) |
| D-12 measured inventory (markdown, phase dir) | NEW | doc / evidence | batch | `.planning/milestones/v1.36-phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` | role-match (`.planning/` precedent, not code) |
| `firestarter_app/tools/build_db.py` (3 deletions + 1 derivation) | MOD | utility (generator) | transform | itself — quoted below at real line numbers | n/a |
| `firestarter_app/tests/test_build_db_inclusion.py` | MOD | test | CRUD (DB assertions) | itself `:76-100`, `:576-594` | n/a |
| `firestarter_app/tests/__snapshots__/test_characterization.ambr` | MOD | snapshot | batch | itself `:1001` | n/a |
| `firestarter_app/tests/test_wire_dict_equivalence.py` | MOD | test | batch | its own 194 layer | **exact** |
| `firestarter_app/datasheets/MBM27C1000.pdf` (+ `git add` ×2) | NEW/track | asset | file-I/O | `datasheets/MBM27C1001.pdf` (the only tracked one) | n/a |

**Tracked-source gate:** every analog path above was verified with `git ls-files` inside the
`firestarter_app` submodule. All are tracked. The two exceptions are **deliberately reported**:
`datasheets/MBM27128.pdf` and `datasheets/MBM27C4001.pdf` are **untracked working-tree files** —
confirming RESEARCH C-3 / D-21. An OVR-03 citation to either dangles until `git add`.

---

## Pattern Assignments

### 1. `firestarter_app/tools/datasheet_overrides.json` (config/data, file-I/O)

**Analog:** `firestarter_app/tools/extra_chips.json` (52 lines, whole file read).

**The analog's actual shape** `[QUOTED — current state, tools/extra_chips.json:1-26]`:

```json
{
  "TEXAS INSTRUMENTS": [
    {
      "source": "non-upstream-supplement",
      "datasheet": "firestarter/datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf",
      "provenance": "VAR-05 / D-10 — physically real 24-pin NMOS UV-EPROM, absent from minipro infoic.xml ...",
      "part_number": "2516",
      "support_status": "supported",
      "verification_status": "UNVERIFIED",
      "verification_note": "SAFE-04 / FUT-03: resolvable for read/info but NOT write-graduated. ...",
      "electrical": {
        "type": "UV-EPROM",
        "size_bytes": 2048,
        "pin_count": 24,
        "vpp_mv": 25000,
        "vcc_mv": 5000,
        "vdd_mv": 6500
      },
      "programming": {
        "algorithm": 11,
        "pulse_duration_us": 500,
        "chip_id_check": false,
        "chip_id_value": "0x00000000"
      },
      "pinout": "DIP24_2716"
    },
```

**What transfers:**
- Its *slot*: a curated, hand-maintained JSON file in `tools/`, read by `build_db.py` in `main()`,
  resolved via a `os.path.join(os.path.dirname(__file__), ...)` module constant (`:23`).
- Its *honesty discipline*: every record carries a `datasheet` path and a free-text justification
  field. The override file's `datasheet` + `note` keys are the direct descendant of
  `datasheet` + `provenance`.
- Its *two-level nesting* (`electrical.*`, `programming.*`) is exactly the dotted-path namespace the
  override file addresses.

**What does NOT transfer — state this explicitly in the plan:**

| `extra_chips.json` | `datasheet_overrides.json` |
|---|---|
| Top level keyed by **manufacturer → list of rows** | Top level keyed by **`MANUFACTURER/ALIAS` → one object** (D-01/D-02) |
| **Fully-specified whole rows** | **Partial field substitutions only** |
| Merged **POST-decode**, `complete_db.setdefault(mfg, []).extend(...)` | Applied **PRE-derivation**, between `classify()` and the ceiling check |
| **Bypasses `classify()` and `resolve_pinout_key()` entirely** (`:720-722` says so) | Deliberately runs *before* every derivation so the generator's own rules re-run on the overridden value (D-03) |
| Carries `support_status` **as data** | Must **never** carry `support_status` / `unsupported_reason` (D-05) — those stay derived |
| Adds rows (746 = 744 + 2) | Adds **zero** rows |
| Absent file ⇒ skip with a printed note (`:736-737`) | Absent file ⇒ planner's call, but a present-but-unconsumed **key** must raise (OVR-04) |
| Is invisible to `_generator_chip_entry_keys`'s AST walk, so a second scanner `_extra_chips_entry_keys` exists for it (`test_chip_database_field_inventory.py:265+`) | Emits **no new field**, so it needs no such scanner — and must not add one (adding a provenance field to the DB would redden the frozen inventory) |

**Proposed shape** `[PROPOSED SHAPE]` (from RESEARCH `## The Override File`, D-20):

```json
{
  "FUJITSU/MBM27C1000": {
    "datasheet": "datasheets/MBM27C1000.pdf",
    "note": "AC CHARACTERISTICS (Single Byte Programming), p.4-68: tPW 0.475/0.50/0.525 ms",
    "fields": {
      "programming.pulse_duration_us": { "was": 100, "is": 500 }
    }
  }
}
```

Keys sorted ascending, enforced by the loader (fail closed on unsorted).

---

### 2. Loader + applier in `firestarter_app/tools/build_db.py` (utility, transform)

#### 2a. File-reading analog — the `extra_chips` merge `[QUOTED — current state, build_db.py:716-737]`

```python
    # Merge tools/extra_chips.json after the decode loop, before the JSON write.
    # These are real parts absent from infoic.xml entirely (2516, 2532), so they
    # ship first-class rather than needing per-operator database.json edits.
    #
    # Supplement records arrive FULLY SPECIFIED and are deliberately NOT routed
    # through classify() / resolve_pinout_key() — they have no infoic.xml fields to
    # decode. The merge does not mutate any wire value.
    supplement_count = 0
    if os.path.exists(EXTRA_CHIPS_FILE):
        with open(EXTRA_CHIPS_FILE) as ef:
            extra_db = json.load(ef)
        for mfg_name, extra_chips in extra_db.items():
            if not isinstance(extra_chips, list):
                continue
            complete_db.setdefault(mfg_name, []).extend(extra_chips)
            supplement_count += len(extra_chips)
        print(
            f"Supplement: merged {supplement_count} non-upstream chip(s) "
            f"from {EXTRA_CHIPS_FILE} (post-decode)."
        )
    else:
        print(f"Supplement: {EXTRA_CHIPS_FILE} not found — skipping merge.")
```

Its path constant `[QUOTED — build_db.py:19-23]`:

```python
OUTPUT_FILE = os.path.join(_DATA_DIR, "chip_database.json")
PINOUT_FILE = os.path.join(_DATA_DIR, "pinouts.json")
# Curated non-upstream chip supplement, merged post-decode (see
# the EXTRA_CHIPS block in main()). Physically-real chips absent from infoic.xml.
EXTRA_CHIPS_FILE = os.path.join(os.path.dirname(__file__), "extra_chips.json")
```

Copy: the `os.path.join(os.path.dirname(__file__), "<name>.json")` constant, plain `open()` +
`json.load`, and a stdout progress line. **Do not copy** the `os.path.exists` / `else: skipping`
softness into the *consumed-key* check — an unconsumed key must raise, not print.

Note `build_db.py` uses `import json, os, sys` at `:1-3` and plain `open(path)` without
`encoding=`. `tests/` uses `encoding="utf-8"`; match each file's local idiom.

#### 2b. Fail-closed raise shape — `interpret_timing` `[QUOTED — build_db.py:339-365]`

```python
def interpret_timing(raw_hex, protocol_id):
    # [VERIFIED: minipro database.c#L866 @ a8efaedc]
    # Raw pulse_delay is microseconds for ALL protocols — no multiplier.
    # ... (comment block :340-346 elided) ...
    try:
        val = int(raw_hex, 16)
    except (TypeError, ValueError):
        # ... (comment block :350-357 elided) ...
        raise ValueError(
            f"chip with protocol {protocol_id:#04x} has unparseable "
            f"pulse_delay {raw_hex!r} — refusing to default to 0 us"
        ) from None

    if protocol_id in (0x07, 0x08, 0x0B):
        return val

    return 0
```

*(RESEARCH cites this as `:339-380`; the function actually ends at `:365`. Minor drift, flagged.)*

#### 2c. Fail-closed raise shape — the `page_size` validation `[QUOTED — build_db.py:739-751]`

```python
    for mfg_name, mfg_chips in complete_db.items():
        for chip in mfg_chips:
            emitted_page_size = chip.get("programming", {}).get("page_size")
            if emitted_page_size is not None and (
                emitted_page_size <= 0
                or emitted_page_size > 512
                or (emitted_page_size & (emitted_page_size - 1))
            ):
                raise ValueError(
                    f"{mfg_name}/{chip.get('part_number')} would emit "
                    f"page_size {emitted_page_size!r}, which is not a power "
                    f"of two in [1, 512] — refusing to write {OUTPUT_FILE}"
                )
```

*(RESEARCH cites `:739-752`; `:752` is blank. Immaterial.)*

**House style the new raisers must match — all five elements, in this order:**
1. `raise ValueError(` — never a custom exception class; nothing in `main()` catches `ValueError`,
   so it aborts before `json.dump` and no partial database is written.
2. An implicitly-concatenated f-string across lines, ≤88 columns.
3. The offending **row identity first** (`{mfg_name}/{part_number}` style) or the protocol.
4. The offending **value**, with `!r`.
5. A closing em-dash clause: `— refusing to <do the thing>`. Both existing raisers use a literal
   U+2014 em dash surrounded by spaces. Match it.

The five OVR-04 legs (unknown part key, unknown field path, no-op `was == is`, stale `was` vs live
decode, two keys resolving to the same row+field) each get a raiser in this shape.

#### 2d. Alias parsing — the idiom to converge on

Three copies exist today, all going away with their hardcodes:

```python
# :522-524  (inside the _AT28C_DIP24_NAMES arm)
_chip_aliases = {
    a.split("@")[0].strip() for a in name.split(",") if a.strip()
}
# :574      (inside the _ETYPE_RELABEL arm)
part_aliases_set = {a.split("@")[0].strip() for a in name.split(",")}
# :586      (inside the NMOS arm)
part_aliases = {a.split("@")[0].strip() for a in name.split(",")}
```

`[QUOTED — current state]`. The D-01 key resolver needs this **once**, in the `if a.strip()`-guarded
form (`:522-524`), which is also the form `chip_entry["part_number"]` itself uses at `:618-624`.

#### 2e. The integration point — what exists there today

**There is no row dict at the insertion point.** `chip_entry` is built at `:608-680`, *after* the
ceiling check, with every emitted value computed **inline in the literal**
`[QUOTED — current state, build_db.py:608-680, comment blocks elided]`:

```python
                chip_entry = {
                    "part_number": ",".join(
                        dict.fromkeys(
                            a.split("@")[0].strip()
                            for a in name.split(",")
                            if a.split("@")[0].strip()
                        )
                    ),
                    "support_status": _support_status,
                    "electrical": {
                        "type": _etype,
                        "size_bytes": mem_size,
                        "pin_count": pin_count,
                        "vpp_mv": (
                            _nmos_vpp_mv
                            if _nmos_vpp_mv is not None
                            else VPP_MV.get(voltages & 0xF0, 0)
                        ),
                        "vcc_mv": VCC_VOLTAGES.get(
                            (voltages >> 8) & 0x0F, 5000
                        ),  # bits 11-8
                        "vdd_mv": VCC_VOLTAGES.get(
                            (voltages >> 12) & 0x0F, 5000
                        ),  # bits 15-12
                    },
                    "programming": {
                        "algorithm": proto_id,
                        "pulse_duration_us": interpret_timing(
                            ic.get("pulse_delay"), proto_id
                        ),
                        "chip_id_check": True if (flags & 0x20) else False,
                        "chip_id_value": ic.get("chip_id"),
                        "protect_off_before": True if (flags & 0x4000) else False,
                        "protect_on_after": True if (flags & 0x8000) else False,
                        "infoic_page_size_raw": raw_page_size,
                        **(
                            {"page_size": raw_page_size}
                            if _upstream_proto_id in (0x0D, 0x05)
                            else {}
                        ),
                    },
                    "pinout": pinout_key,
                }
                if _unsupported_reason:
                    chip_entry["unsupported_reason"] = _unsupported_reason
```

That is why `electrical.vpp_mv` resolves to nothing at the D-03 insertion point: the value does not
exist as a name until the literal is evaluated. **Task 1 of the plan must hoist these expressions
into named locals above the ceiling check, and leave the literal's 14 key literals in place**
referencing those names (see §6 below for the AST test that forces this).

#### 2f. The post-literal rewrites the override must survive

`[QUOTED — current state, build_db.py:691-708, comments elided]` — these run *after* the literal and
are exactly the "generator's own rules re-run" D-03 depends on:

```python
                if _etype == "SRAM":
                    chip_entry["electrical"]["vcc_mv"] = chip_entry["electrical"][
                        "vdd_mv"
                    ]

                if chip_entry["electrical"]["vcc_mv"] == _VCC_MARGIN_RAIL_MV:
                    chip_entry["electrical"]["vcc_mv"] = chip_entry["electrical"][
                        "vdd_mv"
                    ]
```

This is the mechanism behind D-17: FM1608's `FRAM` label was bypassing the first branch, so
deleting the relabel flips `vcc_mv` 3300 → 5000 as a second, derived consequence.

---

### 3. `firestarter_app/tests/golden/wire_dict_expected_deltas_197.json` (test fixture, layered golden)

**Analog:** `tests/golden/wire_dict_expected_deltas_194.json` — **exact template**.

**The 194 layer's actual JSON shape** `[QUOTED — current state]`. Two top-level keys, `deltas` and
`meta`; `deltas` is keyed by `MANUFACTURER|PART_NUMBER|<index>` and holds only the wire fields that
move:

```json
{
  "deltas": {
    "ASD|AE29F1008|0": { "page-size": 128 },
    "ASD|AE29F2008|1": { "page-size": 128 },
    "ASD|AE29F4008|2": { "page-size": 256 }
  },
  "meta": {
    "phase": "194-real-page-size-reaches-the-firmware",
    "decision": "Phase 194 D-01/D-02: tests/golden/wire_dict_baseline.json is preserved byte-unchanged. This file is the committed, reviewable expected-delta list ... the golden itself is never re-captured or re-baselined to make this phase's change disappear.",
    "honesty": "This layer records that these 25 records newly emit the page-size wire key. It does not by itself prove the value is correct -- ...",
    "how_to_update": "This layer is regenerated by the same script against the live database and never edited by hand. A new delta must name the chips and the reason in the commit message. ...",
    "provenance": "The 25 upstream-native protocol_id==0x05 rows that did not already carry a page-size value in the frozen baseline ... Generated programmatically from the live capture against the committed golden -- never transcribed by hand ..."
  }
}
```

**The 197 layer's contents are fully determined** by RESEARCH's measured red list — three records,
wire field `pulse-delay` (confirmed as a live wire key at `test_wire_dict_equivalence.py:405`):

```json
{
  "deltas": {
    "FUJITSU|MBM27128|2": { "pulse-delay": 1000 },
    "FUJITSU|MBM27C1000P,MBM27C1000|6": { "pulse-delay": 500 },
    "FUJITSU|MBM27C1001|7": { "pulse-delay": 500 }
  },
  "meta": { "phase": "197-the-override-mechanism-and-the-program-pulse", "...": "..." }
}
```

`[PROPOSED SHAPE]` — the five `meta` keys (`phase`, `decision`, `honesty`, `how_to_update`,
`provenance`) are the 194 layer's set and should be reproduced with 197 content. Note the 194 layer's
own `how_to_update` says it is generated programmatically, never transcribed by hand — the 197 layer
should be produced the same way and the plan should say so.

---

### 4. `tests/test_wire_dict_equivalence.py` — the exact edit sites for a 197 layer

Every live occurrence of `194`, enumerated so the planner can write tasks against line numbers
rather than prose. `[VERIFIED — grep of the live file]`

| Site | Line(s) | Edit needed for 197 |
|---|---|---|
| Module docstring, test-1 name | `:22` | rename `..._182_and_194_deltas` → `..._194_and_197_deltas` |
| Module docstring, layer list | `:29-31` | add the 197 layer + its count |
| Module docstring, "what each layer sets" | `:35-36` | add "197 sets `pulse-delay`" |
| Module docstring, assertion catalogue | `:50-57` | add 197 non-vacuity + exact-count clauses |
| Module docstring, test-4 composition | `:85`, `:89-90` | add the 197 layer |
| Path constant | `:120` (`_DELTAS_194`) | add `_DELTAS_197 = _HERE / "golden" / "wire_dict_expected_deltas_197.json"` |
| Test 1 signature | `:209` | rename (matches `:22`) |
| Test 1 load | `:218` | add `deltas_197 = json.loads(_DELTAS_197.read_text(encoding="utf-8"))["deltas"]` |
| Test 1, 194 non-vacuity block | `:299-312` | clone for 197, keying on `"pulse-delay"` instead of `"page-size"` |
| Test 1, 194 exact count | `:314-317` (`== 25`) | clone: `assert len(deltas_197) == 3` |
| Test 1, **pairwise disjointness** | `:320-325` (6 pairs) + message `:337` | add `("197", deltas_197, "149"/"153"/"182"/"194", …)` → 10 pairs; update the message string |
| Test 1, expected composition | `:344-350` | add `for key, delta_wire in deltas_197.items(): expected[key].update(delta_wire)` |
| Test 1, failure message | `:357-363` | add the 197 clause |
| `test_exactly_84_records_change_flags_and_no_other_field_moves` | `:423` name, `:427-437` loads/compose, `:455-458` `== 84`, `:459-463` `changed_fields == {"flags"}` | **the hard one — see below** |
| `test_the_194_delta_layer_is_capable_of_failing` (if present) | `:427-429` region | mirror for 197 |

**The `== 84` → `== 87` bump is not a one-character change.** `[QUOTED — current state, :423-463]`:

```python
def test_exactly_84_records_change_flags_and_no_other_field_moves() -> None:
    doc = json.loads(_GOLDEN.read_text(encoding="utf-8"))
    recorded = doc["records"]

    deltas_149 = json.loads(_DELTAS_149.read_text(encoding="utf-8"))["deltas"]
    deltas_182 = json.loads(_DELTAS_182.read_text(encoding="utf-8"))["deltas"]
    deltas_194 = json.loads(_DELTAS_194.read_text(encoding="utf-8"))["deltas"]

    expected = copy.deepcopy(recorded)
    for key, delta_wire in deltas_149.items():
        expected[key].update(delta_wire)
    ...
    assert len(changed_keys) == 84, (
        f"expected exactly 84 records to change (golden+149 vs live), found "
        f"{len(changed_keys)}: {changed_keys}"
    )
    assert changed_fields == {"flags"}, (
        "expected the ONLY changed field across all 84 records to be "
        f"'flags', found: {sorted(changed_fields)} -- a second, unnoticed "
        "wire change may be riding along with this one"
    )
```

Note this test composes **149 + 182 + 194 but deliberately NOT 153** — 153 *is* the 84 flags deltas
it is measuring. Two live choices for the planner, and the plan must pick one explicitly:
- **(a)** compose `deltas_197` in as well, keeping `== 84` and `changed_fields == {"flags"}`; or
- **(b)** leave 197 out of the composition, bump to `== 87`, and widen `changed_fields` to
  `{"flags", "pulse-delay"}` — which **weakens the "no second unnoticed wire change" guarantee**.

RESEARCH measured the failure as `== 84` → found 87, i.e. the current uncomposed behaviour.
Option (a) preserves the assertion's teeth; option (b) is what the measured number suggests. **The
test name embeds `84`, so either way the function is renamed** and every docstring reference moves.

---

### 5. `firestarter_app/tests/test_datasheet_overrides.py` (test, unit)

**Analog A — the import idiom that gets `tools/` code into CI coverage**
`[QUOTED — current state, tests/test_build_db_interpret_timing.py:1-62, docstring truncated]`:

```python
"""
Tests for tools/build_db.py::interpret_timing (Phase 148 Plan 03 -- DATA-02 (D-08)).

Defect class this closes: after the string/int schema collapse ... D-08
closes that ambiguity by making the decode-fault path fatal (`ValueError`,
naming both the protocol and the offending raw value) instead of silently
defaulting to `0` ...

Per 148-RESEARCH.md's "D-08 reachability" finding, the fatal branch is
PROVABLY DEAD against the pinned infoic.xml commit (a8efaedc): an exhaustive
scan of all 27,862 `<ic>` elements found 0 missing and 0 unparseable
`pulse_delay` values. That means a green `python3 tools/build_db.py` run
proves NOTHING about this branch -- this module is its ONLY coverage.

Coverage:
  1. `test_fatal_leg_none_raises_naming_protocol_and_value` -- ...
  2. ...
"""

import pytest

from tools import build_db

_FATAL_LEG_PROTOCOL_NONE = 0x07
_FATAL_LEG_PROTOCOL_STRING = 0x0B
_VALID_HEX = "64"  # 0x64 == 100 decimal
_ALGORITHM_CONTROLLED_PROTOCOL = 0x0D  # EEPROM_POLL: does not consume pulse-delay


def test_fatal_leg_none_raises_naming_protocol_and_value():
    with pytest.raises(ValueError) as exc:
        build_db.interpret_timing(None, _FATAL_LEG_PROTOCOL_NONE)
    message = str(exc.value)
    assert "0x07" in message, message
    assert "None" in message, message


def test_fatal_leg_unparseable_string_raises_naming_protocol_and_value():
    with pytest.raises(ValueError) as exc:
        build_db.interpret_timing("zz", _FATAL_LEG_PROTOCOL_STRING)
    message = str(exc.value)
    assert "0x0b" in message, message
    assert "'zz'" in message, message


def test_control_valid_hex_returns_parsed_int():
    """Property C / S-5: proves the fatal legs above are not passing merely
    because interpret_timing raises unconditionally -- a valid hex string on
    a pulse-delay-consuming protocol must still decode and return cleanly."""
    result = build_db.interpret_timing(_VALID_HEX, _FATAL_LEG_PROTOCOL_NONE)
    assert result == 100, result
```

Copy verbatim as a skeleton:
- `from tools import build_db` — module-level import is side-effect-safe (`main()` is
  `__name__`-guarded; module level only opens `pinouts.json`).
- The docstring's **reachability argument** — "a green regeneration proves NOTHING about this
  branch; this module is its ONLY coverage" — applies word-for-word to all five OVR-04 legs. Restate
  it, do not invent a new justification.
- `with pytest.raises(ValueError) as exc:` → `message = str(exc.value)` → one `assert <token> in
  message, message` per identifying token. **This is what makes the raise-message house style (§2c)
  testable**: each leg's test asserts the row key, the field path and the value appear in the text.
- **Control tests.** Note tests 3-5 exist purely to prove the raisers are not unconditional. The 197
  loader needs the same: a happy-path test applying a valid override and asserting the substitution,
  and a test proving an empty/absent override file leaves the decode untouched.
- Module-level `_CONSTANT = value` for fixtures; no classes in this file.

Note this analog carries trailing `#` comments (`:45`, `:46`). It is in `tests/`, not product
source, and the rule's pre-commit check pathspec covers `firestarter_app/*.py` — **do not add new
comment lines here either**; the docstring carries the explanation.

**Analog B — the sibling-data-file test shape**
`[QUOTED — current state, tests/test_extra_chips_supplement.py:1-95, abridged]`:

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 86 Plan 04 — VAR-05 / D-10 / D-11 / SAFE-04 non-upstream supplement gate.

... This test pins:
  (a) 2516 + 2532 are present in the GENERATED chip_database.json with their cited
      wire values (so a regression that drops the merge, or mutates a wire value,
      fails loudly);
  (c) every supplement record carries a non-upstream source marker AND a datasheet
      citation field (D-11 — honest-provenance, not a guessed chip);
...
It reads the GENERATED DB (post-merge) and tools/extra_chips.json + pinouts.json
via FIRESTARTER_* path seams so it runs in both the submodule and the meta-repo
test runner.
"""

import json
import os

# Path seams (mirror the FIRESTARTER_DB_FILE idiom used across the suite)
_HERE = os.path.dirname(__file__)

_DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join(_HERE, "..", "firestarter", "data", "chip_database.json"),
)
_EXTRA_CHIPS_FILE = os.environ.get(
    "FIRESTARTER_EXTRA_CHIPS_FILE",
    os.path.join(_HERE, "..", "tools", "extra_chips.json"),
)

_SUPPLEMENT_SOURCE = "non-upstream-supplement"


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _all_chips(db):
    for mfg, chips in db.items():
        if isinstance(chips, list):
            for chip in chips:
                yield mfg, chip


def _aliases(chip):
    pn = chip.get("part_number", "")
    return {a.split("@")[0].strip() for a in pn.split(",") if a.strip()}


def _find(db, alias):
    """Return the first chip record whose alias-set contains `alias`, or None."""
    for _mfg, chip in _all_chips(db):
        if alias in _aliases(chip):
            return chip
    return None


# (a) presence in the generated DB
class TestSupplementPresent:
    def test_2516_present_in_generated_db(self):
        db = _load(_DB_FILE)
        assert _find(db, "2516") is not None, (
            "2516 absent from generated chip_database.json — "
            "the build_db.py post-decode supplement merge did not run (VAR-05 / D-10)"
        )
```

Copy for the **file-contract half** of the 197 coverage (a second test module, or a second class in
the same one):
- `_HERE` + `os.environ.get("FIRESTARTER_*", os.path.join(_HERE, "..", ...))` **path seams** — the
  suite runs from both the submodule and the meta-repo runner, so a hardcoded relative path breaks
  one of them. A `FIRESTARTER_DATASHEET_OVERRIDES_FILE` seam is the direct descendant.
- `_load`, `_all_chips`, `_aliases`, `_find` helpers — reuse the shapes exactly; `_aliases` is also
  the D-01 key-resolution primitive.
- `class TestXxx:` grouping with a lettered `# (a) …` sectioning comment. **Note those are comment
  lines in a tracked `.py`** — the pre-commit check catches `^\+\s*#` on *added* lines, so a new test
  file must express its sectioning in class names and docstrings instead.
- Assertions carry a failure message that names *the mechanism that must have broken*, not just the
  expected value.

**Ruff applies here and not to `tools/`.** CI runs `ruff check firestarter/ tests/` and
`ruff format --check firestarter/ tests/` on **Python 3.11** with `select = ["E","F","I","UP"]`,
`E501` ignored, `line-length = 88`, `quote-style = "double"`. The new test file must be clean; the
loader in `tools/build_db.py` is lint-invisible but behaviour-gated by these tests.

---

### 6. The constraint that forces the whole design: the AST walk

`[QUOTED — current state, tests/test_chip_database_field_inventory.py:234-262]`

```python
def _generator_chip_entry_keys(source_text: str) -> "set[str]":
    """ast-walk `source_text` (tools/build_db.py's own source) and collect
    every string key literal reaching a variable literally named
    `chip_entry` -- both its dict-literal construction (including nested
    dicts and the `page_size` conditional `**` spread) and every
    `chip_entry[...] = ...` subscript assignment (including the nested
    `chip_entry["electrical"]["vcc"]` chain). This is the D-12/T-140-10
    half: chip_database.json is GENERATED, so a new key reaching
    `chip_entry` here becomes a new database field the moment anyone
    regenerates -- reachable without ever executing the generator.

    Does NOT see the VAR-05/D-10 extra_chips.json merge -- see
    `_extra_chips_entry_keys` and the module docstring's "Generator scan
    scope" section.
    """
    tree = ast.parse(source_text)
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "chip_entry":
                if isinstance(node.value, ast.Dict):
                    _collect_dict_keys(node.value, keys)
            elif isinstance(target, ast.Subscript) and _is_chip_entry_subscript_chain(
                target
            ):
                keys.update(_chip_entry_subscript_constants(target))
    return keys
```

Supporting helpers `[QUOTED — :196-231]`: `_collect_dict_keys` recurses into nested `ast.Dict`
values and, for a `**spread` (`key_node is None`), descends into both branches of an `ast.IfExp` and
into a bare `ast.Dict`; `_is_chip_entry_subscript_chain` walks `.value` down to an `ast.Name` whose
`id == "chip_entry"`; `_chip_entry_subscript_constants` collects the constant string indices along
the chain.

**What this forbids, concretely:**
- `chip_entry = dict(decoded)` → `node.value` is an `ast.Call`, not `ast.Dict` → zero keys collected
  → the golden's 25-entry `generator_emitted_chip_entry_keys` list mismatches → **RED**.
- `chip_entry = {**decoded}` → `ast.Dict` with a single `key_node is None` whose value is an
  `ast.Name`, which `_collect_dict_keys` does not descend into → **zero keys → RED**.
- `chip_entry[section][field] = value` in a loop over override paths → the subscript arm only
  collects **constant** string indices; variable indices contribute nothing, so the keys are lost
  unless the literal still carries them.

**What it permits, and therefore what the design must be:**

> Hoist each inline expression into a named local immediately before the ceiling check, apply the
> override to those locals through a two-level dotted-path view, and leave `chip_entry = { ... }`
> structurally intact with all 14 key literals present, its right-hand sides now being plain names.

`[PROPOSED SHAPE]` — comment-free, as the rule requires:

```python
                _d_vpp_mv = VPP_MV.get(voltages & 0xF0, 0)
                _d_vcc_mv = VCC_VOLTAGES.get((voltages >> 8) & 0x0F, 5000)
                _d_vdd_mv = VCC_VOLTAGES.get((voltages >> 12) & 0x0F, 5000)
                _d_pulse = interpret_timing(ic.get("pulse_delay"), proto_id)

                apply_datasheet_override(_OVERRIDES, mfg_name, _chip_aliases, _decoded)

                if _d_vpp_mv > RURP_VPP_CEILING_MV:
                    _support_status = "vpp-exceeds-max"
                    ...

                chip_entry = {
                    "part_number": ...,
                    "support_status": _support_status,
                    "electrical": {
                        "type": _etype,
                        "size_bytes": _d_size_bytes,
                        "pin_count": _d_pin_count,
                        "vpp_mv": _d_vpp_mv,
                        "vcc_mv": _d_vcc_mv,
                        "vdd_mv": _d_vdd_mv,
                    },
                    "programming": {
                        "algorithm": proto_id,
                        "pulse_duration_us": _d_pulse,
                        ...
                    },
                    "pinout": pinout_key,
                }
```

Two preservation traps in that sketch, both measured in RESEARCH:
- `interpret_timing(ic.get("pulse_delay"), proto_id)` is called with the **post-`classify()`**
  `proto_id` (`classify()` reassigns it at `:563`). The hoisted `_d_pulse` must keep the same
  argument, or 417 rows that currently emit `0` start emitting a value.
- The generalised ceiling check must keep `>`, **not** `>=`. Six rows sit exactly at 25000 mV and
  `>=` would flip them to `vpp-exceeds-max` and redden `tests/test_chip_resolver.py:72-84`.

---

### 7. `tools/build_db.py` — the three deletions, quoted at real line numbers

All `[QUOTED — current state]`. Each block's surrounding prose is the orphaned-comment hazard.

**`NMOS_TRUE_VPP_MV` — `:84-90`** (declaration) and **`:580-606`** (application):

```python
# NMOS VPP correction: promotes the comment above to applied code.
# Matched against part_number aliases; "highest VPP wins" for entries with
# multiple NMOS aliases (e.g., INTEL/2732,2732A,M2732,M2732A).
NMOS_TRUE_VPP_MV: dict[str, int] = {
    "M2716": 25000,  # Intel NMOS 2716: 25V VPP (datasheet)
    "M2732": 25000,  # Intel NMOS 2732: 25V VPP (datasheet)
    "M2732A": 21000,  # Intel NMOS 2732A: 21V VPP (later variant)
}
```

```python
                part_aliases = {a.split("@")[0].strip() for a in name.split(",")}
                for nmos_key, nmos_vpp in NMOS_TRUE_VPP_MV.items():
                    if nmos_key in part_aliases:
                        if _nmos_vpp_mv is None or nmos_vpp > _nmos_vpp_mv:
                            _nmos_vpp_mv = nmos_vpp
                if _nmos_vpp_mv is not None:
                    if _nmos_vpp_mv > RURP_VPP_CEILING_MV:
                        _support_status = "vpp-exceeds-max"
                        _unsupported_reason = (
                            f"VPP {_nmos_vpp_mv // 1000}V exceeds programmer max "
                            f"({RURP_VPP_CEILING_MV // 1000}V)"
                        )
                        proto_id = NON_DISPATCHABLE_ALGO
```

Deleting `_nmos_vpp_mv` removes the gate variable, which is exactly why the ceiling check must be
re-keyed onto the effective `_d_vpp_mv` (§6). Note the reason string's exact wording
(`VPP {x}V exceeds programmer max ({ceil}V)`) must survive the re-keying unchanged — the host
renders it verbatim.

**`_AT28C_DIP24_NAMES` — `:506-530`**, and the hardware-damage guard above it at **`:469-492`** that
D-15 says stays:

```python
                if (
                    pin_count == 24
                    and proto_id in (0x07, 0x08, 0x0B)
                    and (flags & 0x10)
                ):
                    _support_status = "adapter-required"
                    _unsupported_reason = (
                        "adapter required: requires a dedicated DIP24 EEPROM adapter "
                        "or firmware handler — socket pin 21 = WE, which the RURP "
                        "DIP24_2716 pinout maps to the 12V VPP rail (hardware-damage path)"
                    )
                    print(
                        f"INFO: including {mfg_name}/{name} as adapter-required — ...",
                        file=sys.stderr,
                    )
                    proto_id = NON_DISPATCHABLE_ALGO

                _AT28C_DIP24_NAMES = {
                    "AT28C04", "AT28HC04", "AT28C04E", "AT28C04F",
                    "AT28C16", "AT28HC16", "AT28HC16L", "AT28C16E", "AT28C16F",
                    "28C04A", "28C04AF", "28C16A", "28C16AF", "UPD28C04",
                }
                _chip_aliases = {
                    a.split("@")[0].strip() for a in name.split(",") if a.strip()
                }
                if _chip_aliases & _AT28C_DIP24_NAMES:
                    _support_status = "adapter-required"
                    _unsupported_reason = (
                        "adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical "
                        "DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter"
                    )
```

*(The set literal is one-name-per-line at `:507-520` in the real file; collapsed here for width.)*
`_chip_aliases` at `:522-524` is consumed only by this arm today — it is the natural survivor to
repurpose as the D-01 key-resolution alias set.

The 12-line comment block at `:494-505` is entirely about this arm and goes with it. The guard's own
comment at `:466-468` (*"These chips resolve to DIP24_2716, not None"*) is **factually wrong** per
RESEARCH C-1 — they resolve to `DIP24_2816` — but it belongs to the surviving guard, and the no-new-
comments rule means the plan may delete a wrong clause but may not write a corrected one.

**`_ETYPE_RELABEL` — `:567-578`:**

```python
                # Label-only per-chip relabel, keyed on part_number. Runs after
                # classification and must NOT touch proto_id / pinout / vpp /
                # algorithm.
                #
                # SST39SF040 deliberately KEEPS Flash/EEPROM: relabelling it to
                # 'Flash' flips FLAG_CAN_ERASE off and breaks its auto-erase.
                _ETYPE_RELABEL = {"FM1608": "FRAM"}
                part_aliases_set = {a.split("@")[0].strip() for a in name.split(",")}
                for _relabel_pn, _relabel_etype in _ETYPE_RELABEL.items():
                    if _relabel_pn in part_aliases_set:
                        _etype = _relabel_etype
                        break
```

The `SST39SF040` clause at `:571-572` documents a *non-entry* — it explains why something is absent
from the dict. Deleting the dict orphans it completely; it must go too.

**`_PGM_ON_PIN31_MAX_SIZE` — `:148` and its only use at `:241`:**

```python
_PGM_ON_PIN31_MAX_SIZE = 262144
```

```python
            elif proto_id in {0x07, 0x08, 0x10}:
                if proto_id == 0x08 and variant_lo == 0x03:
                    key = "DIP32_27C801"
                elif proto_id == 0x08 and variant_lo == 0x02:
                    key = "DIP32_STD"
                elif proto_id == 0x08 and mem_size <= _PGM_ON_PIN31_MAX_SIZE:
                    key = "DIP32_27C020"
                else:
                    key = "DIP32_STD"
```

The derivation `[PROPOSED SHAPE]` replaces the `:241` condition with
`elif proto_id == 0x08 and (mem_size - 1).bit_length() <= 18:` and deletes `:148`. Acceptance is a
literal `cmp` against `git show HEAD:firestarter/data/chip_database.json` with only this change
applied, run as its own task before anything else lands.

---

### 8. `tests/test_build_db_inclusion.py` — the two red sites

`[QUOTED — current state, :76-100]` (only the `etype` assertion at `:97-100` moves; `algo == 40` and
the pinout assertion stay):

```python
    def test_fm1608_resolves_sram_std(self):
        """FM1608 (RAMTRON) must classify as algorithm 40 (0x28 SRAM_STD),
        electrical.type 'FRAM' (Phase-84 cosmetic relabel survives), and pinout
        'DIP28_JEDEC_SRAM_8K'. GREEN against the current DB.
        """
        db = _load_db()
        found = []
        for mfg, chip in _all_chips(db):
            al = _aliases(chip)
            if "FM1608" in al:
                found.append((mfg, chip))

        assert found, "FM1608 not found in chip_database.json"
        for mfg, chip in found:
            algo = chip.get("programming", {}).get("algorithm")
            etype = chip.get("electrical", {}).get("type")
            pinout = chip.get("pinout")
            assert algo == 40, (...)
            assert etype == "FRAM", (
                f"{mfg}/{chip.get('part_number')}: expected electrical.type='FRAM' "
                f"(Phase-84 cosmetic relabel), got {etype!r}"
            )
```

The class docstring at `:60-74` also states `FRAM` at `:64-65` (this is what D-14 meant by
"`:64`"). **Add a `vcc_mv == 5000` assertion** here — D-17's second field has no other pin.

`[QUOTED — current state, :576-594]` — the second red:

```python
        db = _load_db()
        found = []
        for mfg, chip in _all_chips(db):
            al = _aliases(chip)
            if "AT28C16" in al:
                found.append((mfg, chip))

        assert found, "AT28C16 not found in chip_database.json"
        for mfg, chip in found:
            if chip.get("support_status") != "adapter-required":
                continue
            reason = chip.get("unsupported_reason", "")
            assert reason.startswith("adapter required:"), (...)
            assert "AT28C04 Adapter" in reason, (
                f"{mfg}/{chip.get('part_number')}: named-arm reason must reference "
                f"'AT28C04 Adapter' (the adapter wiki page), got: {reason!r}"
            )
```

Its docstring at `:568-575` enumerates three properties, the third being *"Does NOT contain
'DIP24_2716 pinout maps to the 12V VPP rail' (that is the old generic Site B wording; named arm
overwrites it)"* — **that clause inverts** after the deletion: the guard text is now what the rows
carry. The `startswith("adapter required:")` leg stays green (the guard text starts the same way).
Keep the `support_status != "adapter-required": continue` filter — it is what makes the test survive
the change at all.

**Snapshot** `[QUOTED — tests/__snapshots__/test_characterization.ambr:1001]`:

```
 | FM1608              | RAMTRON          |   28 |            | FRAM        | -    |
```

`FRAM` → `SRAM`. Column widths are fixed; `SRAM` is the same length, so no realignment is needed.

---

### 9. The D-12 measured inventory (doc/evidence)

**No code analog exists.** The `.planning/` precedent is
`/workspaces/.planning/milestones/v1.36-phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md`
(77 lines), the closest measured-inventory artifact in the repo. Its shape
`[QUOTED — current state, abridged]`:

```markdown
# PRUNE-04 Read-Back Call-Site Inventory

Phase 177, plan 177-03. The evidence behind PRUNE-04's closure: every place in
`firestarter_app` that reads a device or a bus back ..., named, and disposed
with a reason. Coverage is judgeable, not asserted — the search method that
produced it is stated below, and ... is additionally pinned by a machine census
in `firestarter_app/tests/test_readback_inventory.py`, which is proven to redden
against a planted third call site rather than merely claimed to cover the module.

## Search method

1. `/usr/bin/grep -rn "read_eprom(" --include=*.py firestarter/` — every read
   entry point in the package.
...
(`/usr/bin/grep` deliberately, not the devcontainer's PATH `grep`, which is
ugrep and honors `.gitignore` and can silently under-scan.)

## The eight-row inventory

| # | Site | What it reads | What it compares against | Disposition |
|---|------|----------------|---------------------------|--------------|
| 1 | `chip_test.py:3108` (`_read_region`, ...) | the **write region** ... | `expected` ... | **EXCLUDED by D-1.** ... |
```

Three structural properties to copy for `197-PULSE-INVENTORY.md` (name is the planner's; file it in
the phase directory per D-12):
1. **A stated, reproducible method section before the data** — the exact command that produced the
   rows, so the count is auditable. RESEARCH `## D-12 — The Inventory` already supplies a runnable
   `python3 -c` one-liner over `chip_database.json`.
2. **Every row disposed with a reason**, in a bolded verdict vocabulary (`EXCLUDED` / `NOT
   APPLICABLE` / `OUT OF SCOPE` there; here: `CORRECTED` / `DATASHEET-CONFIRMED-CORRECT` /
   `NO DATASHEET`). `MBM27C4001` is the `DATASHEET-CONFIRMED-CORRECT` row and must be recorded here
   rather than getting an override entry — an entry for it would be a no-op and **fail the build**
   under D-04.
3. **A named honesty limit** — 177's is "coverage is judgeable, not asserted". Here: the 215
   remaining rows are inventoried, not audited; a row's presence is not a claim that 100 µs is wrong.

A 215-row table is large. 177's precedent is a full table because it was 8 rows; for 215 the
defensible shape is a per-manufacturer summary table plus the full list as a fenced block, with the
generating command adjacent so any reader can regenerate it.

---

## Shared Patterns

### S-1. Fail-closed exception construction
**Source:** `tools/build_db.py:349-363` and `:747-751`
**Apply to:** every new raiser in the loader (5 legs)
**Shape:** `ValueError` + implicitly-concatenated f-string + row identity + `{value!r}` + closing
`— refusing to …` clause. No custom exception class. Nothing catches it; `main()` aborts before
`json.dump` at `:753`.

### S-2. Sibling-data-file path constant
**Source:** `tools/build_db.py:23`
**Apply to:** `DATASHEET_OVERRIDES_FILE`
```python
EXTRA_CHIPS_FILE = os.path.join(os.path.dirname(__file__), "extra_chips.json")
```

### S-3. Alias-set derivation
**Source:** `tools/build_db.py:522-524`, mirrored in `tests/test_extra_chips_supplement.py:68-70`
**Apply to:** D-01 key resolution in the loader, and to every new test that finds a row by name
```python
{a.split("@")[0].strip() for a in name.split(",") if a.strip()}
```

### S-4. `from tools import build_db` — the CI-coverage bridge
**Source:** `tests/test_build_db_interpret_timing.py:41`
**Apply to:** `tests/test_datasheet_overrides.py`
`tools/` is outside `ruff check`, `ruff format --check` and `mypy`, and `--cov=firestarter` excludes
it from coverage. A plain package import from the pytest rootdir is the only thing that puts loader
*behaviour* under CI. Three test modules already do it.

### S-5. Environment-variable path seams in tests
**Source:** `tests/test_extra_chips_supplement.py:40-51`
**Apply to:** any new test reading `tools/datasheet_overrides.json` or `chip_database.json`
```python
_DB_FILE = os.environ.get(
    "FIRESTARTER_DB_FILE",
    os.path.join(_HERE, "..", "firestarter", "data", "chip_database.json"),
)
```
Required so the suite runs from both the submodule and the meta-repo runner.

### S-6. Layered-golden discipline
**Source:** `tests/golden/wire_dict_expected_deltas_194.json` `meta` block + its assertions in
`tests/test_wire_dict_equivalence.py`
**Apply to:** the 197 layer
The baseline is **never re-captured**. Each phase adds a delta layer with an *exact* count assertion
(never "at least"), a *non-vacuity* assertion (the golden must not already carry the delta value),
and *pairwise field-disjointness* against every prior layer. A new layer that omits any of the three
is a laundering channel.

### S-7. No comments in product source
**Source:** `/workspaces/CLAUDE.md` § "Source code comments — hard rule"
**Apply to:** every task touching `firestarter_app/`
Pre-commit check, mandatory, must print nothing:
```
git -C firestarter_app diff --cached -- '*.py' | /usr/bin/grep -E '^\+\s*#' | /usr/bin/grep -v '^\+\s*#!'
```
The pathspec is load-bearing. `/usr/bin/grep` deliberately — the devcontainer's PATH `grep` is ugrep
and honors `.gitignore`. Three consequences for this phase specifically: (a) the deletions orphan
adjacent prose that must be deleted, not rewritten; (b) `tests/test_sdp_honesty.py:59` is a bare
comment line — deleting a stale clause is permitted, rewriting it adds a `+#` line and trips the
check; (c) new `tests/` files must express sectioning in class names and docstrings, not `# (a)`
banner comments like the `test_extra_chips_supplement.py` analog uses.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| D-12 pulse inventory (`197-PULSE-INVENTORY.md`) | doc/evidence | batch | No code analog. Nearest precedent is `.planning/milestones/v1.36-phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` — quoted in §9. There is no in-repo tool that emits an inventory artifact; RESEARCH supplies the generating one-liner. |
| a 746-row regeneration diff tool | utility | transform | `tools/diff_db.py` is **referenced** by `tests/golden/chip_database_field_inventory.json`'s `meta.why_not_diff_db` but **does not exist**. `tools/baseline/chip_database.baseline.json` exists but is stale (475,857 vs 432,461 bytes) — do not diff against it. RESEARCH recommends a throwaway ~25-line script, not a committed tool, and supplies it. The stale `why_not_diff_db` reference is worth a one-line correction. |

---

## Citation Drift From RESEARCH.md

Checked against the live files on `beta`. RESEARCH is accurate; three minor drifts:

| RESEARCH cites | Live | Note |
|---|---|---|
| `interpret_timing` at `:339-380` | `:339-365` | function ends at `:365`; `:366+` is `main()` |
| `page_size` validation `:739-752` | `:739-751` | `:752` is blank |
| `chip_entry` literal `:607-681` | `:608-680`, with `:681-682` the `unsupported_reason` append | off by one |

Everything else — `:87`, `:148`, `:241`, `:506`, `:573`, `:591-600`, `:700-705`, `:716-737`,
`test_chip_database_field_inventory.py:234-263`, `test_wire_dict_equivalence.py:321` — resolves
exactly as cited.

**One RESEARCH finding confirmed independently here:** `datasheets/MBM27128.pdf` and
`datasheets/MBM27C4001.pdf` return nothing from `git ls-files` inside the submodule. Only
`datasheets/MBM27C1001.pdf` is tracked. D-21 stands.

---

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/tests/`,
`firestarter_app/tests/golden/`, `firestarter_app/tests/__snapshots__/`, `.planning/` (inventory
precedent). Submodule read on `beta`; no branch switch, no file modified.
**Files read:** 10 source/test/fixture files + 2 planning documents
**Tracked-source verification:** `git ls-files` run inside `/workspaces/firestarter_app`
**Pattern extraction date:** 2026-09-18
