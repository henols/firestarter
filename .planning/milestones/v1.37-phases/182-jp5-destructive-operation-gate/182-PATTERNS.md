# Phase 182: JP5 Destructive-Operation Gate - Pattern Map

**Mapped:** 2026-09-10
**Files analyzed:** 13 code/data files to create or modify (RESEARCH.md § *File:line inventory* rows 1-14 and 20-22; rows 15-19 are `.planning/` prose and carry no code pattern)
**Analogs found:** 13 / 13 — every change in this phase has an in-tree precedent. Nothing here needs inventing.

All paths below are relative to `/workspaces/firestarter_app/` unless prefixed. Every analog path was
verified tracked with `git ls-files` inside the `firestarter_app` submodule (18/18 present).

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `tools/build_db.py` (`resolve_pinout_key` 32-pin arm) | generator / pure decode rule | transform | **the same function's 24-pin arm (`:206-224`) and 28-pin arm (`:226-256`)** | exact (same function) |
| `tools/build_db.py` (`:8` import, `:271` use — drop `MAX_27C020_SIZE`) | generator constant | transform | module-local constants block `:150-183` (`PINOUT_FILE`, `VALID_PINOUT_KEYS`) | role-match |
| `firestarter/data/pinouts.json` (new `DIP32_27C801`) | authored data / layout definition | transform | **`DIP32_SST39SF040` (`:75-84`) for the shape + citation style; `DIP28_27512` (`:54-63`) for OE/VPP sharing; `DIP32_STD` (`:64-73`) for the address list this one extends** | exact |
| `firestarter/data/chip_database.json` (8 rows) | generated data | batch | — (never hand-edited; output of `build_db.py`) | n/a by decision D-04 |
| `firestarter/constants.py` (delete `:43-51`) | config constant retirement | — | commits `c5db256` + `784e74c` (Phase 181-04/181-02: `locked_destructive`/`locked_steps` deleted, test surface retired in a separate commit) | role-match |
| `tests/test_revision_constants_parity.py` (delete `:686-710`) | test retirement | — | `784e74c` (test-surface retirement commit shape) | role-match |
| `tools/diff_db.py` (new root-cause rule) | classification ladder | transform | **`RC1_DIP32_27C020`** — rationale `:211`, field paths `:380`, dispatch `:519-534` | exact (a pinout-value-scoped, pinout-only rule) |
| `tests/golden/wire_dict_expected_deltas_182.json` (new) | golden fixture / delta layer | batch | **`tests/golden/wire_dict_expected_deltas_153.json`** (2nd layer; `_149` is the 1st) | exact |
| `tests/test_wire_dict_equivalence.py` (new `_DELTAS_182` layer) | test | batch | the 153 layer's legs: `:97-101`, `:212-318`, `:437-450` | exact |
| `firestarter/ic_layout.py` (delete `:186-201`, `:656`) | renderer deletion | request-response | its live sibling `_get_rev2_jumper_settings_data` `:169-184` (what must SURVIVE) | exact |
| *(gate)* affected-part predicate + hazard text | host policy (pure function) | transform | **`SerialCommunicator._validate_hardware_revision` `firestarter/serial_comm.py:752-806`** + `HardwareRevisionUnsupportedError` `firestarter/exceptions.py:37-58` | **exact — an existing chip-damage refusal gate keyed on a wire value** |
| *(gate)* prompt in `firestarter/cli_handlers.py` `write` `:608`, `erase` `:845` | CLI boundary / interactive | request-response | **`submit.submit_report` `firestarter/submit.py:633-644, 701, 728`** (`isatty_fn`/`confirm_fn` injection) | exact |
| *(gate)* refusal at `eprom_operations.py` `write_eprom :1967`, `erase_eprom :2130` | service guard | request-response | `serial_comm.py:752-806` (same fail-closed pure-policy shape) | role-match |
| *(gate)* tests in `tests/` | test | — | **`tests/test_hw_revision_gate.py`** (policy + real-DB coupling + integration) and `tests/test_submit.py:1076-1104` (fake injection) | exact |
| `tools/DECODE-NOTES.md` (`:53-69`) | doc | — | the §1 `variant_lo` table itself (`:53-64`) — extend rows, retract the "stays verbatim" sentence at `:49-50` | exact |

---

## Pattern Assignments

### 1. `tools/build_db.py` — `resolve_pinout_key` 32-pin `variant_lo` dispatch

**Analog: the same function's own 24- and 28-pin arms.** CONTEXT.md § Reusable Assets names these
explicitly. The 28-pin arm is the closer of the two: it is a `variant_lo` ladder *inside* a `pm_idx`
test, with an `else` fallback, guarding a 12 V-to-wrong-pin hazard.

**28-pin arm — the ladder shape to copy** (`tools/build_db.py:226-236`):

```python
    elif pin_count == 28:
        if pm_idx == 22:
            if variant_lo == 0x10:
                key = "DIP28_27512"
            elif variant_lo == 0x11:
                key = "DIP28_27256"
            else:
                key = "DIP28_2764"
```

**24-pin arm — same shape, three-way with `else` default** (`:206-219`):

```python
    if pin_count == 24:
        if pm_idx == 23:
            if variant_lo == 0x01:
                key = "DIP24_2732"
            elif variant_lo == 0x10:
                key = "DIP24_2816"
            else:
                key = "DIP24_2716"
```

**The 32-pin arm as it stands, showing exactly what the new forks sit in front of** (`:258-284`):

```python
    elif pin_count == 32:
        if pm_idx == 0:
            key = "DIP32_SST39SF040"
        elif pm_idx in {5, 7, 9, 10, 11, 12, 13}:
            if proto_id in {0x05, 0x06}:
                key = "DIP32_SST39SF040"
            elif proto_id == 0x0D:
                key = "DIP32_28C512_EEPROM"
            elif proto_id in {0x07, 0x08, 0x10}:
                if proto_id == 0x08 and mem_size <= MAX_27C020_SIZE:
                    key = "DIP32_27C020"
                else:
                    key = "DIP32_STD"
            else:
                key = None
        else:
            key = None
```

**The residual size-threshold arm MUST survive alongside the new dispatch.** RESEARCH.md § *But
`variant_lo` alone does NOT partition the whole 32-pin 0x08 set* measured that `SST37VF040`
(`pm_idx=13`, `variant_lo=0x04`, 524288 bytes) breaks a pure `variant_lo` ladder — anything-not-0x02-
or-0x03 mapping to `DIP32_27C020` would move a 512 KB part whose pin 31 must stay A18. So the new
forks go **ahead of** the `mem_size <=` test, and the `mem_size` test stays as the residual arm for
the `0x00`/`0x01`/`0x04` classes. Both new forks stay **inside** the `proto_id == 0x08` branch:
protocol `0x10` rows carry `variant_lo` `0x10`-`0x13` and hoisting the fork above the protocol test
reroutes Intel-flash parts.

**Two guards this pattern relies on, unchanged:**

- Fail-safe `key = None` on every unmatched branch — `None` triggers `main()`'s skip.
- `:286-287` — the self-checking registration guard, which is why adding the `pinouts.json` key is
  self-verifying:

```python
    if key is not None and key not in VALID_PINOUT_KEYS:
        print(f"WARN: resolved pinout key '{key}' not in pinouts.json", file=sys.stderr)
```

**Comment hazard — read this before copying.** The analog arms carry `# CRITICAL`, `# [VERIFIED: …]`
and per-branch explanatory comments. `tools/build_db.py` is under `firestarter_app/`, so
`/workspaces/CLAUDE.md` § "Source code comments — hard rule" applies: **the comments are NOT part of
the pattern to copy.** Copy the control-flow shape only. The `variant_lo=0x03` rationale goes in
`tools/DECODE-NOTES.md` §1 (inventory row 6) and the phase `SUMMARY.md`, not in the function.

**`MAX_27C020_SIZE` replacement (inventory row 3).** Analog for a module-local generator constant is
`:150-183`'s block (`PINOUT_FILE`, then `VALID_PINOUT_KEYS = set(json.load(_f).keys())` at `:182-183`).
A module-local name in `build_db.py` with no firmware-parity claim replaces the
`from firestarter.constants import MAX_27C020_SIZE` at `:8`.

---

### 2. `firestarter/data/pinouts.json` — the new `DIP32_27C801` layout

**Analogs: three entries, each supplying a different half of the answer.**

**(a) `DIP32_STD` `:64-73` — the address list the new entry extends, and the exact key ordering:**

```json
    "DIP32_STD": {
        "name": "JEDEC 32-Pin Standard",
        "comment": "Standard 32-pin UV-EPROM layout (27C010/27C020/27C040 family). VPP on pin 1, PGM (where applicable) on pin 31; A18 takes over pin 31 on 27C040. NOT correct for 5V flash (AM29F040/SST39SF040 family — those have A18 at pin 1, WE at pin 31 — see DIP32_SST39SF040).",
        "pins": {
            "vcc-pin": [32], "gnd-pin": [16], "vpp-pin": [1],
            "address-bus-pins": [12, 11, 10, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3, 2, 30, 31],
            "data-bus-pins": [13, 14, 15, 17, 18, 19, 20, 21],
            "ce-pin": [22], "oe-pin": [24]
        }
    },
```

**Field shape and ordering the new entry must match:** top-level `name` → optional `comment` →
`pins`; inside `pins`, `vcc-pin`/`gnd-pin`/`vpp-pin` first (grouped on one line),
then `address-bus-pins`, then `data-bus-pins`, then control pins (`ce-pin`, `oe-pin`, `rw-pin`).
Every value is a **list**, even a single pin. Two-space-per-level indentation is 4 spaces here.

**`address-bus-pins` is an ordered A0..An list — index IS the address bit.** `DIP32_STD`'s list has
19 entries (A0..A18, A18 at pin 31). The new 27C080 list is *this list with `1` appended*, making
index 19 = pin 1 = **A19**. That is the whole mechanism by which SAFE-01's literal wording
("the pin map puts A19 on socket pin 1") becomes expressible — no new field, no new semantics.

**(b) `DIP28_27512` `:54-63` — the OE/VPP-shared precedent the 27C080 needs at pin 24:**

```json
    "DIP28_27512": {
        "name": "JEDEC 27512",
        "pins": {
            "vcc-pin": [28], "gnd-pin": [14],
            "vpp-pin": [22], "oe-pin": [22],
            "address-bus-pins": [10, 9, 8, 7, 6, 5, 4, 3, 25, 24, 21, 23, 2, 26, 27, 1],
            "data-bus-pins": [11, 12, 13, 15, 16, 17, 18, 19],
            "ce-pin": [20]
        }
    },
```

The same pin appears as both `vpp-pin` and `oe-pin`. This is load-bearing: `database.py:277-279`
drops a `vpp-pin` that resolves to the `ROM_OE`/`ROM_CE` sentinel, so `vpp-pin: [24], "oe-pin": [24]`
on a 32-pin map yields **no `vpp-pin` on the wire** and firmware defaults `vpp_line=0xFF`. Note
`DIP28_27512` declares no `rw-pin` — same for the new entry, per RESEARCH (the `/PGM` on pin 22 is
the pin the firmware already strobes as `/CE`).

**(c) `DIP32_SST39SF040` `:75-84` — the citation convention for the `comment` field:**

```json
        "comment": "Per piersfinlayson/one-rom (datasheet-verified): SST39SF040 and same-family 4Mbit/8Mbit 5V flash chips have A18 at pin 1 (NOT VPP) and WE at pin 31 (NOT address bus). Distinct from DIP32_STD (UV-EPROM 27C040 layout) where pins 1 and 31 are swapped. Covers ~47 chips at (pin_count=32, pm_idx=13, protocol_id=0x06): AM29F040, SST39SF040, A29040, EN29F040, MX29F040, etc. — all 5V single-supply flash.",
```

Established `comment` recipe, in order: **source citation** → **what is distinctive about pins 1/31**
→ **what it is distinct FROM (by key name)** → **the exact decode tuple that assigns it** → the
covered part set. RESEARCH.md's verbatim JSON (§ *The new 32-pin layout definition*) already follows
this recipe and additionally adds a `HARDWARE:` clause about JP5 — consistent with `DIP32_27C020`'s
comment, which is the longest in the file and already carries schematic-level hardware reasoning.

**The `comment` key is JSON data, not a source comment.** The CLAUDE.md hard rule does not reach it —
3 of the 15 existing entries carry one, and it is the only place this layout's provenance can live.
Do not let a comment sweep strip it.

**Key name:** `DIP32_27C801` follows the exemplar-part-number convention of `DIP32_27C020` /
`DIP32_SST39SF040` (CONTEXT § Claude's Discretion). Insertion point: after `DIP32_27C020` ends at
`:93`, or at the end of the object. Registration is automatic —
`VALID_PINOUT_KEYS = set(json.load(_f).keys())` (`tools/build_db.py:182-183`).

---

### 3. Deletions — `MAX_27C020_SIZE`, its parity arm, and the dead JP5 renderer

**Prior-phase analog for retiring a constant + its test surface: Phase 181, two commits in the
`firestarter_app` submodule.**

| Commit | What it did | The pattern |
|---|---|---|
| `784e74c` `test(181-02): retire the write_scope="none" test surface -- 93 sites, 15 tests deleted` | Retired the **test** surface FIRST, in its own commit, so the later production deletion could not redden a module at collection time. Its body states per-deletion claim+reason and points at `SUMMARY.md` for the rest. Closes with *"zero product-source lines changed; zero comments added"*. | **Test-surface retirement precedes production deletion, in a separate commit.** |
| `c5db256` `fix(181-04): narrow write_scope to two values, delete locked_destructive/locked_steps` | Deleted the constants outright. No deprecation shim, no alias. | **Outright deletion; no shim.** |

Apply to this phase: delete `tests/test_revision_constants_parity.py:686-710` (the `@requires_fw`
decorator + `test_max_27c020_size_parity` + its 20-line docstring + the assert), then
`firestarter/constants.py:43-51`, then `tools/build_db.py:8`+`:271`. CONTEXT allows replacing the
parity arm with "a test that asserts something real about the 32-pin dispatch" — if the planner takes
that option, the pattern for it is `tests/test_build_db_inclusion.py`'s classification-outcome tests
(`:79-709`, SRAM-pinout class at `:379-475`), which exercise `resolve_pinout_key` through outcomes.

**`ic_layout.py` deletion (SAFE-05).** The analog is the live sibling that must SURVIVE
byte-unchanged — `_get_rev2_jumper_settings_data` `:169-184`:

```python
    def _get_rev2_jumper_settings_data(self, jp4: int) -> dict:
        jp4_label = self._select_jumper_label(jp4, "Open", "Closed")
        jumper_display = [" N/A   ", " ● ●   ", "(● ●)  "]
        return {
            "2.0 & 2.1": {
                "jp4": {
                    "config_text": "28pin",
                    "display": jumper_display[jp4],
                    "pin_text": "32pin",
                    "selected_label": jp4_label,
                },
            }
        }
```

The dead `_get_rev2_2_jumper_settings_data` `:186-201` is a near-copy of it keyed `"2.2"`/`"jp5"`.
Delete the method and the commented call at `:656`:

```python
                # output_data["jumpers"].update( self._get_rev2_2_jumper_settings_data(jp4_rev2))  # noqa: E501
```

Keep the two live `output_data["jumpers"].update(...)` calls at `:649-654` immediately above it.

**Grep trap (RESEARCH § *Success criterion 4 has a grep trap*).** The verification leg must be
`git -C firestarter_app grep -n '_get_rev2_2_jumper_settings_data' -- '*.py'`, not a bare `grep -rn`:
a stale `build/lib/firestarter/ic_layout.py:186` copy exists, `build/` is gitignored, and PATH `grep`
is ugrep which honours `.gitignore` — so the bare command reads GREEN or RED for reasons unrelated to
the deletion.

**Nothing currently guards this code.** `/usr/bin/grep -rln "jumper" tests/` returns no matches;
`tests/test_ic_layout.py` covers pin-name display, type labels and erase-capability rows only. A test
asserting the `"2.2"`/`"jp5"` block is absent from `get_chip_layout`'s output would be the first.

---

### 4. `tools/diff_db.py` — the new root-cause rule

**Analog: `RC1_DIP32_27C020`.** It is the same kind of rule this phase needs — a *pinout-only,
pinout-value-scoped* explanation for a `resolve_pinout_key` change. Three coordinated edits:

**(a) rationale string** (`:211-214`, in `_RATIONALES`):

```python
    "RC1_DIP32_27C020": (
        "Phase 98 RC-1 fix — DIP32_27C020 scoped pinout for 0x08 ≤256K 32-pin chips.\n"
        "  Root cause RC-1: pin 31 was modeled as address line A18 (DIP32_STD) for all\n"
        "  0x08/32-pin chips, but for ≤256K chips (27C010/27C020 class), pin 31 is PGM\n"
        ...
```

Convention: phase number + one-line label, then indented root-cause prose, with a
`[VERIFIED: …]`/`[CITED: …]` citation (module header at `:42-46` states the citation requirement and
the minipro permalink base).

**(b) explained field set** (`:380`, in `_RULE_FIELD_PATHS`):

```python
    "RC1_DIP32_27C020": {
```

Scope it to exactly `("pinout",)` — RESEARCH names the label `RULE_PHASE182_A19_PINOUT`. A tight
field set is what makes a co-occurring unexpected change escalate rather than be absorbed.

**(c) dispatch ladder arm** (`:519-534`, in `_classify_diff`) — the shape, and note the
`not <other>_diff` conjunction plus the **new-pinout-value** scope test:

```python
    elif (
        pinout_diff
        and not algo_diff
        and not timing_diff
        and not voltage_diff
        and not type_diff
        and not vpp_diff
        and cu_chip.get("pinout") == "DIP32_27C020"
    ):
        label = "RC1_DIP32_27C020"
    elif pinout_diff and not algo_diff and not timing_diff:
        label = "SRAM_PINOUT"
```

The new arm goes **before `SRAM_PINOUT`**, same as `RC1_DIP32_27C020` does, and scoped on
`cu_chip.get("pinout") == "DIP32_27C801"`. If the planner also wants a part-number scope (the eight
named rows), the analog for that is `_PHASE84_RELABEL_PART_NUMBERS = frozenset({"FM1608"})` at
`:415-417` plus its `cu_chip.get("part_number") in _PHASE84_RELABEL_PART_NUMBERS` test at `:552`.
The priority-order docstring at `:444-460` is maintained in lockstep — add a numbered line for the
new rule there too.

Without this rule the regeneration exits 1 (`BLOCK: unexplained diff`, `diff_db.py:11-18`).

---

### 5. `tests/golden/wire_dict_expected_deltas_182.json` — the third delta layer

**Analog: `tests/golden/wire_dict_expected_deltas_153.json`** — the *second* layer, so it is the one
that already had to coexist with a predecessor. File shape:

```json
{
  "deltas": {
    "AMD|AM28C16A|22": {
      "flags": 2
    },
    ...
  }
}
```

Record key is `MANUFACTURER|PART_NUMBER(S)|<positional index within that manufacturer's list>`. For
this phase the eight keys start `AMD|AM27C080|12` (`wire_dict_baseline.json:437`) — RESEARCH lists
all eight baseline line numbers at inventory row 9.

**The `meta` block is mandatory and carries five keys** (`_149`'s, verbatim structure):
`decision`, `honesty`, `how_to_update`, `phase`, `provenance`. Copy the semantics:

- `decision` — cite D-17 by name: the golden `wire_dict_baseline.json` is preserved **byte-unchanged**;
  this file is the reviewable delta on top of it.
- `how_to_update` — *"A new delta must name the chips and the reason in the commit message. Growing
  this list without a provenance justification is exactly the re-baselining D-17 exists to prevent"*,
  and point at the anti-laundering assertion in `test_wire_dict_equivalence.py`.
- `provenance` — how the deltas were produced. `_149`'s says *"Generated programmatically from the
  live capture against the committed golden — never transcribed by hand, since the `|<i>` record-key
  suffix is a positional index…"*. **Do the same**: generate, do not transcribe.
- `phase` — the phase dir slug, e.g. `182-jp5-destructive-operation-gate`.

**Composition is a SHALLOW `expected[key].update(delta_wire)`** (`test_wire_dict_equivalence.py:301-305`).
That is why this phase's delta must supply the **whole `bus-config` object** (all 20 bus lines and no
`vpp-pin` key), not a nested patch — a shallow update replaces `bus-config` wholesale, which is
exactly how the `vpp-pin` key disappears.

---

### 6. `tests/test_wire_dict_equivalence.py` — the `_DELTAS_182` layer

**Analog: the 153 layer, leg for leg.** Copy all of it.

**Path constant + provenance comment** (`:93-101`):

```python
_DELTAS_149 = _HERE / "golden" / "wire_dict_expected_deltas_149.json"
# (D-153-05, ERASE-03): the second, field-disjoint delta layer --
# see this file's module docstring and
# tests/golden/wire_dict_expected_deltas_153.json's own "meta" block.
_DELTAS_153 = _HERE / "golden" / "wire_dict_expected_deltas_153.json"
```

**The composition test's legs** (`test_live_capture_matches_golden_plus_the_149_and_153_deltas`,
`:212-318`) — the 153 legs (d), (e), (f) are the template:

```python
    # (d) 153-layer non-vacuity: every 153 delta key must exist in the
    # golden, and the golden's own record for it must NOT already carry the
    # delta's flags value -- mirrors (b) for the new layer.
    missing_from_golden_153 = sorted(k for k in deltas_153 if k not in recorded)
    already_present_153 = sorted(
        k
        for k in deltas_153
        if k in recorded and recorded[k].get("flags") == deltas_153[k].get("flags")
    )
    assert not missing_from_golden_153, (
        f"153 delta keys not found in the golden: {missing_from_golden_153}"
    )
    assert not already_present_153, (
        "153 delta keys whose golden record already carries the delta's "
        f"flags value (the delta would prove nothing): {already_present_153}"
    )

    # (e) 153-layer exact count: len(deltas_153) == 84, not "at least" --
    # mirrors (c) for the new layer.
    assert len(deltas_153) == 84, (
        f"expected exactly 84 Phase 153 deltas, found {len(deltas_153)}: "
        f"{sorted(deltas_153)}"
    )
```

For 182: `already_present_182` keys on `recorded[k].get("bus-config") == deltas_182[k].get("bus-config")`,
and the exact count is `== 8`.

**Field-disjointness leg (f)** (`:293-306`) generalises from a pair to a triple — 149 touches
`page-size`, 153 touches `flags`, 182 touches `bus-config`, so disjointness holds:

```python
    shared_keys = sorted(set(deltas_149) & set(deltas_153))
    field_collisions = {
        k: sorted(set(deltas_149[k]) & set(deltas_153[k])) for k in shared_keys
    }
    field_collisions = {k: v for k, v in field_collisions.items() if v}
    assert not field_collisions, (...)
```

**Composition leg (g)** (`:308-318`) — append a third loop, and update the failure message's chip and
delta counts. The test's **name** carries the layer list (`..._plus_the_149_and_153_deltas`), so it
gets renamed.

**Capability-to-fail leg** — `test_the_153_delta_layer_is_capable_of_failing` (`:437-460`) is a
required sibling; it re-uses `_describe_record_diff`, *"the SAME helper the real comparison test
calls -- rather than a parallel implementation."* Add the 182 equivalent.

**Unaffected:** `test_wire_key_union_is_exactly_nine_keys` (`:325`) — `vpp-pin` is nested inside
`bus-config`, not a top-level wire key. Verify, do not assume.

**Do NOT touch** `tests/golden/wire_dict_baseline.json`. Leg (a) (`:220-238`) is the anti-laundering
assertion that exists precisely to catch a re-capture.

---

### 7. The gate — analog is an existing chip-damage refusal already shipping

This is the single most important pattern in this phase: **the codebase already contains a
hardware-damage refusal gate keyed on a wire value derived from `pinouts.json`.** Commit `344905f`
`feat(safety): refuse pre-Rev-2.2 shields for VPP-on-line-11 chips (#45)`. It is CAP-02, and it gates
the *same two 24-pin parts* the D-15.1 finding is about.

**Pure-policy predicate + hazard text** (`firestarter/serial_comm.py:752-806`):

```python
    _VPP_LINE_REQUIRING_REV_2_2 = 11
    _REVISIONS_WITH_3_POSITION_JP4 = (REVISION_2_2, REVISION_2_3)

    @staticmethod
    def _validate_hardware_revision(
        command_to_send: dict, detected: Optional[int]
    ) -> None:
        """Pure-policy shield-revision guard. Raises on reject, returns on pass.

        Mirrors _validate_firmware_version's shape: no I/O, no environment
        reads, no serial access — just the wire dict the host is about to act
        on and the revision byte the firmware reported. That makes the policy
        testable without a board and keeps _probe_port free of the reasoning.
        """
        bus_config = command_to_send.get("bus-config") or {}
        if bus_config.get("vpp-pin") != SerialCommunicator._VPP_LINE_REQUIRING_REV_2_2:
            return
        if detected in SerialCommunicator._REVISIONS_WITH_3_POSITION_JP4:
            return
        ...
        raise HardwareRevisionUnsupportedError(
            f"This chip routes VPP to socket pin 21, which needs the 3-position "
            f"JP4 header introduced on RURP shield Rev 2.2. The programmer "
            f"reported {reported}. Refusing to program — an earlier shield "
            f"cannot route VPP there and attempting it can damage the EPROM.\n"
            ...,
            detected=detected,
        )
```

**Five properties to copy:** (i) `@staticmethod`, no I/O, no env reads — testable without a board;
(ii) early `return` on "not in scope", so unaffected chips pass untouched; (iii) **allowlist, never a
`>=`** — the `_REVISIONS_WITH_3_POSITION_JP4` tuple exists because `REVISION_UNKNOWN` (0xFE) is
numerically above `REVISION_2_2` (0x04); (iv) fail-closed on `None`/absent evidence; (v) the message
names the pin, the mechanism, the refusal, the damage, and the one legitimate escape.

**Typed exception** (`firestarter/exceptions.py:37-58`) — `HardwareRevisionUnsupportedError(SerialError)`
with a docstring that states the hazard, why the subclass was chosen, why the caller re-raises rather
than degrading it, and what the extra `detected` kwarg carries. A new `Jp5*`/`Pin1AddressLine*` error
should follow the same shape. Check whether reusing `HardwareRevisionUnsupportedError` is honest here
before adding a class.

**Predicate helper for SAFE-01** — RESEARCH's `pin1_carries_an_address_line(pin_map)` reads
`address-bus-pins` and returns `abp.index(1)`. Its seam is `EpromDatabase.get_pin_map`
(`firestarter/database.py:232-238`), which merges user overrides via `_merge_pin_maps` (`:215-230`) —
that is what satisfies SAFE-01's "derived from the shipped pin maps".

**Interactive prompt + injectable fakes** (`firestarter/submit.py:633-644` and `:701`):

```python
def submit_report(
    report: Any,
    ...,
    isatty_fn: Any = None,
    confirm_fn: Any = Confirm.ask,
    console: Any = None,
    ...,
) -> None:
    isatty_fn = isatty_fn or (lambda: sys.stdin.isatty())
    ...
    if not isatty_fn():
        # off-TTY branch: takes its own exit, never calls confirm_fn
        ...
        return

    if prior_url:
        if not confirm_fn(
            f"You appear to have already reported this -- see {prior_url}. "
            "Add this run's evidence as a comment? ...",
            default=False,
        ):
            return
```

Four properties: keyword-only injection points with real defaults; `isatty_fn` defaulted through a
`or (lambda: ...)` so `None` means "use the real one"; the off-TTY branch **returns before
`confirm_fn` is ever reached**; every ask carries `default=False` — never a default-yes (D-07).
`firestarter/firmware.py:20,895` uses `Confirm.ask` directly for the simpler case.

**Take Option B on `_is_interactive`** (RESEARCH § *CLAIM-07 collision*): carry the gate's own
`isatty_fn`, do not revive `cli_handlers._is_interactive:2299-2306`, which Phase 185's CLAIM-07
deletes. The `submit.py` pattern above IS Option B.

**Call-site pattern in the CLI bodies.** `write` `:608` does its pre-flight checks and warnings, then
one `app.eprom_operator.write_eprom(...)` call, then `sys.exit(0 if ok else 1)`. `erase` `:845-870`
is the same, three statements long. The gate goes with the other pre-flight arms — e.g. the
`if skip_erase and is_protocol_0x0d: click.echo(...)` warning immediately above `write_eprom` — after
`resolve_chip(eprom, db=app.db)` (the last place with both the chip name and `app.db`) and before the
operator call.

**Operator-layer refusal.** `write_eprom` `:1967-2000` and `erase_eprom` `:2130-2137` both enter
`with self._operation_context(...)`, which is what opens the serial link. "Stops before touching the
bus" = before that `with`. `write_eprom` already demonstrates pre-`with` guard logic (the `pulse_us`
shallow-copy block at `:1997-2000`).

---

### 8. Gate tests — `tests/test_hw_revision_gate.py` is the template

Structurally this file is exactly what SAFE-01/02/04 need, and it is organised in four numbered
sections announced in the module docstring: **1. Pure policy · 2. Ack decode · 3. Coupling to the
real database · 4. Integration through `_probe_port`**.

**Module docstring** (`:1-26`) states the hazard, then *"Three things are proved here:"* with a
numbered list. Copy that discipline.

**Section 1 — pure policy, parametrized over allowed and refused inputs** (`:47-120`):

```python
GATED_CMD = {"cmd": 1, "bus-config": {"bus": [0, 1, 2], "vpp-pin": GATED_VPP_LINE}}
UNGATED_CMD = {"cmd": 1, "bus-config": {"bus": [0, 1, 2], "vpp-pin": 15}}


def _validate(command, detected):
    return SerialCommunicator._validate_hardware_revision(command, detected)


@pytest.mark.parametrize("allowed", [REVISION_2_2, REVISION_2_3])
def test_gated_chip_passes_on_rev_2_2_and_later(allowed):
    _validate(GATED_CMD, allowed)  # must not raise


def test_absent_revision_is_refused():
    with pytest.raises(HardwareRevisionUnsupportedError) as exc_info:
        _validate(GATED_CMD, None)
    assert exc_info.value.detected is None
    assert "firmware predates" in str(exc_info.value)
```

Note the local `_validate` wrapper over the private symbol, the synthetic in-scope/out-of-scope wire
dicts, and the assertion on the message substring as well as the exception type.

**Section 3 — coupling to the real database. This is the pattern for SAFE-01 success criterion 2:**

```python
def test_exactly_two_pinouts_emit_the_gated_vpp_line():
    """Pins the gate to real data.

    If a pinout edit moves another layout onto bus line 11, or moves the 24-pin
    UV-EPROM layouts off it, this fails -- which is the point. The gate keys on
    a wire value, so its scope is defined by pinouts.json, not by this module.
    """
    db = EpromDatabase(skip_local_override=True)
    gated = set()
    for key in db.pin_maps:
        pin_count = int(key.split("_")[0].removeprefix("DIP"))
        bus_config = db.get_bus_config(pin_count, key)
        if bus_config and bus_config.get("vpp-pin") == GATED_VPP_LINE:
            gated.add(key)

    assert gated == {"DIP24_2716", "DIP24_2532"}
```

For 182 the equality is over the set of layouts whose `address-bus-pins` contains pin 1 —
`{"DIP32_SST39SF040", "DIP32_27C801"}` for the structural set, with the exact-index-19 set being
`{"DIP32_27C801"}`. `skip_local_override=True` is what keeps it deterministic against a developer's
`~/.firestarter/database.json`. RESEARCH additionally proposes injecting a synthetic pin map via
`_merge_pin_maps` so the assertion is written over the predicate function and not a literal list;
`tests/test_eprom_database.py:129-130, 178, 201, 259` is the sibling that already exercises
`get_bus_config` against the real shipped data.

**Section 4 — integration, with the whole transport patched out** (`:143-165`):

```python
def _probe(command, revision):
    with (
        patch.object(SerialCommunicator, "expect_ack", return_value=(True, "Ready")),
        patch.object(SerialCommunicator, "send_json_command", return_value=42),
        ...
    ):
        return SerialCommunicator._probe_port(...)
```

**TTY-refusal test — inject the fakes, do not monkeypatch** (`tests/test_submit.py:1076-1104`):

```python
    confirm_fn = Mock()
    isatty_fn = Mock(return_value=False)
    ...
    submit.submit_report(report, "W27C512", saved, isatty_fn=isatty_fn, confirm_fn=confirm_fn, ...)
    ...
    confirm_fn.assert_not_called()
```

`confirm_fn.assert_not_called()` is the exact assertion SAFE-04 needs: proof the off-TTY path
**never asks**. Its mirror at `:1012-1037` asserts `isatty_fn.assert_not_called()` for a path that
should short-circuit even earlier. And `:274-302` shows the decline path — `Mock(return_value=False)`
plus `confirm_fn.assert_called_once()` — which is the "decline aborts with no operation" test.

---

## Shared Patterns

### Hazard-message text
**Source:** `firestarter/serial_comm.py:795-806` (the existing chip-damage refusal).
**Apply to:** the new gate's message, and any operator-facing JP5 text.
Structure: what the chip needs → what the tool observed → **"Refusing to program"** → the damage
consequence → `\n` → the one legitimate escape, with the exact command. CONTEXT's standard is that the
text be checkable against the silkscreen: *"JP5: Cut for ROMs with A19 on P1"* — unconditional. Do
**not** reproduce *"Open for 32 pin ROMs, Closed for 28 pin ROMs"* (two-state language on a three-pole
jumper, D-10).

### Fail-closed policy shape
**Source:** `serial_comm.py:757-763` (the allowlist comment block) and `:788-792` (`detected is None`
→ refuse).
**Apply to:** the gate predicate and the operator-layer refusal. Absent evidence is a REJECT. Never a
`>=` where the domain is not an ordered scale. Never a default-yes.

### Delta-layer discipline (D-17)
**Source:** `tests/golden/wire_dict_expected_deltas_149.json` `meta` block + the anti-laundering
assertion at `tests/test_wire_dict_equivalence.py:220-238`.
**Apply to:** every generated-artefact change in this phase. Never re-capture a golden to make a
diff disappear; add a named, counted, provenance-carrying delta layer beside it.

### Generated vs authored
**Apply to:** `chip_database.json` (generated — D-04, output of `build_db.py`, never hand-edited) vs
`pinouts.json` (authored). `tests/golden/v1.3-COVERAGE-MATRIX.md` is likewise regenerated, and the
regenerator **mutates the ledger** (memory `reference_audit_coverage_matrix_golden_stale`) — a
deliberate reviewed regeneration, not a sweep.

### No comments in product source
**Source:** `/workspaces/CLAUDE.md` § "Source code comments — hard rule".
**Applies to every excerpt above.** All of `build_db.py`, `diff_db.py`, `serial_comm.py`, `submit.py`,
`ic_layout.py` and the test files quoted here carry pre-existing comments. Those comments are
**not** part of the pattern to copy — copy structure only. Rationale goes to the phase `SUMMARY.md`,
`tools/DECODE-NOTES.md`, or the commit message. Two exemptions worth stating so the planner does not
over-apply the rule: the JSON `comment` key in `pinouts.json` is **data**, and Click docstrings in
`cli_handlers.py` are user-facing `--help` **text**. Neither is a comment.

---

## No Analog Found

None. Every code and data change in RESEARCH.md's inventory has an in-tree precedent.

Two items have no *code* analog by nature and are prose-only (use the target file's own conventions,
per D-13 — inline dated/evidence-cited corrections in the style the R41 error was recorded):

| File | Role | Data Flow | Note |
|------|------|-----------|------|
| `.planning/notes/jumper-display-ground-truth.md` (inventory row 15) | doc | — | JP4 row `:37`, defect 4 `:60-64`, plus the new VPP-destination table |
| `.planning/v1.7-SHIELD-REVS.md` (inventory row 16) | doc | — | ~24 line-level corrections; use the file's existing inline dated/evidence-cited convention |

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tools/`,
`firestarter_app/tests/`, `firestarter_app/tests/golden/`, plus `git log` over the `firestarter_app`
submodule for retirement-commit precedent.
**Files read for excerpts:** 14 (`tools/build_db.py`, `tools/diff_db.py`, `tools/DECODE-NOTES.md`,
`firestarter/data/pinouts.json`, `firestarter/constants.py`, `firestarter/ic_layout.py`,
`firestarter/serial_comm.py`, `firestarter/exceptions.py`, `firestarter/submit.py`,
`firestarter/cli_handlers.py`, `firestarter/eprom_operations.py`,
`tests/test_hw_revision_gate.py`, `tests/test_submit.py`, `tests/test_wire_dict_equivalence.py`)
plus 3 golden fixtures and `tests/test_revision_constants_parity.py`.
**Tracked-source check:** `git ls-files` inside `firestarter_app` returned all 18 cited paths. No
gitignored mirror paths are cited; `firestarter_app/build/lib/` copies are explicitly excluded.
**Pattern extraction date:** 2026-09-10
