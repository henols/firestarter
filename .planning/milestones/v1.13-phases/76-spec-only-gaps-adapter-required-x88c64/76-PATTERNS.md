# Phase 76: Spec-Only Gaps — adapter-required + X88C64 - Pattern Map

**Mapped:** 2026-06-18
**Files analyzed:** 5 (2 modified, 3 new)
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter_app/tools/build_db.py` | transform / DB pipeline | batch | Self (Site B block, lines 388–411) | exact — named arm inserts in the same block |
| `firestarter_app/tests/test_build_db_inclusion.py` | test | batch | Self (lines 425–473, `TestUnsupportedReasonStrings`) | exact — extend existing test class |
| `firestarter/doc/AT28C04-ADAPTER.md` | config / spec doc | — | `firestarter/doc/SHIELD-REVISIONS.md` | role-match (operator-facing hardware doc) |
| `.planning/AT28C04-ADAPTER.md` | config / spec doc | — | `.planning/v1.7-SHIELD-REVS.md` | role-match (meta investigation-canonical doc) |
| `.planning/X88C64-FEASIBILITY.md` | config / spec doc | — | `.planning/v1.7-SHIELD-REVS.md` (summary + evidence format) | partial (investigation verdict doc) |

---

## Pattern Assignments

### `firestarter_app/tools/build_db.py` — named rule arm for AT28C04/AT28C16 (D-03)

**Analog:** Self — Site B block, `build_db.py` lines 369–411

**Imports pattern** (lines 1–5): no new imports needed; all supporting infrastructure is present.

**Core pattern — existing Site B block** (lines 369–411):
```python
# build_db.py lines 369–411 (current Site B — the named arm inserts BEFORE or AT the start of this block)
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
        f"INFO: including {mfg_name}/{name} as adapter-required — "
        f"24-pin 5V EEPROM with EPROM-family algo 0x{proto_id:02X} "
        f"(damage hazard: 12V VPP to socket pin 21 = WE of 28C-family "
        f"chips; tracked in follow_up 24pin-eeprom-no-handler).",
        file=sys.stderr,
    )
    proto_id = NON_DISPATCHABLE_ALGO
```

**Named-arm pattern to add** (place immediately BEFORE the Site B `if` block, i.e., before line 388):
```python
# Named rule arm: AT28C04/AT28C16 family (D-03, Phase 76)
# Keys on chip name (not proto_id) so it fires independently of Site B ordering.
# Does NOT encode the DIP24→DIP32 pin remap — that lives in firestarter/doc/AT28C04-ADAPTER.md.
# Reason string must start with "adapter required:" (test_adapter_required_reason_starts_with_adapter_required).
_AT28C_DIP24_NAMES = {
    "AT28C04", "AT28HC04", "AT28C04E", "AT28C04F",
    "AT28C16", "AT28HC16", "AT28HC16L", "AT28C16E", "AT28C16F",
    "28C04A", "28C04AF", "28C16A", "28C16AF",
    "UPD28C04",
}
_chip_aliases = {a.split("@")[0].strip() for a in name.split(",") if a.strip()}
if _chip_aliases & _AT28C_DIP24_NAMES:
    _support_status = "adapter-required"
    _unsupported_reason = (
        "adapter required: AT28C04/AT28C16 DIP24 chip — requires a physical "
        "DIP24-to-DIP32 adapter; see firestarter/doc/AT28C04-ADAPTER.md"
    )
    # proto_id is NOT demoted here; Site B fires next and handles that.
```

**Note on ordering invariant:** Site B (lines 388–411) fires immediately after the named arm and also sets `_support_status = "adapter-required"` for the same chips (same predicate). The named arm's purpose is to overwrite the reason string with the explicit named-arm wording rather than the generic Site B reason. Site B then demotes `proto_id = NON_DISPATCHABLE_ALGO` — this demotion is still needed and must not be skipped. The named arm does NOT set `proto_id`; Site B's demotion fires as normal.

**X88C64P reason-string reword** (line 367 — D-02):
```python
# Current (line 367):
_unsupported_reason = "protocol not implemented: 0x34 (XICOR NovRAM serial-parallel hybrid)"

# Replace with (must contain "protocol not implemented" substring — existing tests assert this):
_unsupported_reason = (
    "protocol not implemented: 0x34 (XICOR X88C64P — parallel DIP24 5V EEPROM, "
    "8051 multiplexed-bus interface (ALE/WR/RD); feasible-candidate, handler not implemented)"
)
```

**Name extraction idiom** (from `_aliases()` in test file — matches build_db.py usage):
```python
# The alias-extraction pattern used throughout build_db.py and tests:
_chip_aliases = {a.split("@")[0].strip() for a in name.split(",") if a.strip()}
```

---

### `firestarter_app/tests/test_build_db_inclusion.py` — new test cases (extend)

**Analog:** `TestUnsupportedReasonStrings` class, lines 395–473

**Test class structure pattern** (lines 395–423, `test_vpp_exceeds_max_reason_starts_with_vpp` shape):
```python
def test_vpp_exceeds_max_reason_starts_with_vpp(self):
    """<docstring citing DB-04 SC#N and invariant>."""
    db = _load_db()
    found = []
    for mfg, chip in _all_chips(db):
        al = _aliases(chip)
        if "<SENTINEL_ALIAS>" in al:
            found.append((mfg, chip))

    assert found, "<SENTINEL_ALIAS> not found in chip_database.json"
    for mfg, chip in found:
        ss = chip.get("support_status")
        if ss != "<expected_status>":
            continue
        reason = chip.get("unsupported_reason", "")
        assert reason.startswith("<expected_prefix>"), (
            f"{mfg}/{chip.get('part_number')}: <status> reason must start "
            f"with '<expected_prefix>', got: {reason!r}"
        )
```

**Existing tests that must remain green** (lines 425–473):
- `test_adapter_required_reason_starts_with_adapter_required` — asserts `reason.startswith("adapter required:")` for AT28C16. The named-arm reason string starts with `"adapter required:"` so this passes.
- `test_protocol_not_implemented_reason_contains_not_implemented` — asserts `"protocol not implemented" in reason.lower()` for X88C64P/S. The reworded string contains this substring.

**New tests to add** (two cases — extend `TestUnsupportedReasonStrings` class):

Case 1 — Named-arm reason string content guard for AT28C04/AT28C16:
```python
def test_at28c16_named_arm_reason_mentions_adapter_doc(self):
    """AT28C16 (adapter-required) unsupported_reason references the adapter spec doc.

    D-03 named arm must produce a reason string that:
      1. Starts with 'adapter required:' (existing invariant)
      2. References 'AT28C04/AT28C16' or 'DIP24' (named-arm text, not generic Site B text)
      3. Does NOT contain 'DIP24_2716 pinout maps to the 12V VPP rail' (that is the
         old generic Site B wording; named arm overwrites it)
    """
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
        assert reason.startswith("adapter required:"), (
            f"{mfg}/{chip.get('part_number')}: reason must start with 'adapter required:', got: {reason!r}"
        )
        assert "AT28C04-ADAPTER" in reason or "DIP24" in reason.upper(), (
            f"{mfg}/{chip.get('part_number')}: named-arm reason must reference adapter doc or DIP24, got: {reason!r}"
        )
```

Case 2 — X88C64P reason does NOT contain old wrong wording:
```python
def test_x88c64p_reason_does_not_say_serial_parallel_hybrid(self):
    """X88C64P unsupported_reason must NOT contain 'serial-parallel hybrid'.

    Regression guard: the old string was datasheet-wrong. D-02 replaces it.
    The chip IS parallel (not a serial-parallel hybrid); the old string must not reappear.
    """
    db = _load_db()
    found = []
    for mfg, chip in _all_chips(db):
        al = _aliases(chip)
        if "X88C64P" in al or "X88C64S" in al:
            found.append((mfg, chip))

    assert found, "X88C64P not found in chip_database.json"
    for mfg, chip in found:
        reason = chip.get("unsupported_reason", "")
        assert "serial-parallel hybrid" not in reason.lower(), (
            f"{mfg}/{chip.get('part_number')}: reason must not contain old wrong wording "
            f"'serial-parallel hybrid', got: {reason!r}"
        )
```

---

### `firestarter/doc/AT28C04-ADAPTER.md` (operator-facing layer, D-04)

**Analog:** `firestarter/doc/SHIELD-REVISIONS.md`

**Document structure pattern** (from SHIELD-REVISIONS.md lines 1–22):
```markdown
# <Title>

<Opening paragraph — 2-3 sentences stating what the doc covers and who needs it.>

If you have <artifact in hand and want to do X>, read [§N (<section>)](#n-section).
If you are <doing Y>, read [§M (<section>)](#m-section).

Full derivation history / investigation evidence: see
`.planning/AT28C04-ADAPTER.md` in the Firestarter meta-repo.

---

## 1. <Section>

<Prose + table>

---

## 2. <Section>

...
```

**Section layout for operator-facing adapter doc** (operator needs the pin table + safety notes to physically build the adapter):

```markdown
# AT28C04 / AT28C16 DIP24 → DIP32 Adapter Spec

<opening: who this doc is for (someone building a physical DIP24-to-DIP32 adapter)>
<cross-ref to full derivation in .planning/AT28C04-ADAPTER.md>

---

## 1. Overview

Which chips this adapter covers; firmware handler (configure_eeprom28c, protocol 0x0D);
support_status = adapter-required until a physical adapter + golden round-trip exists.

---

## 2. Adapter Pin Table

| DIP24 chip pin | Chip function | DIP32 socket pin | RURP bus role | Notes |
(24 rows, one per chip pin + unconnected socket pins noted separately)

---

## 3. Safety Notes

Key re-route (chip pin 21 /WE → socket pin 30); what happens without adapter (wrong bus line);
no VPP rail involved (5V-only chip); AT28C04 differences (pins 22/19 are NC).
```

**Cross-reference pattern** (SHIELD-REVISIONS.md line 20–22):
```markdown
Full investigation history [...]: see
`.planning/v1.7-SHIELD-REVS.md` in the Firestarter meta-repo (sections §2
through §5 and §8 — operator does not need these for normal use).
```
Mirror this: reference `.planning/AT28C04-ADAPTER.md` for derivation + evidence.

---

### `.planning/AT28C04-ADAPTER.md` (meta investigation-canonical layer, D-04)

**Analog:** `.planning/v1.7-SHIELD-REVS.md`

**Document structure pattern** (from v1.7-SHIELD-REVS.md lines 1–14):
```markdown
# <SLUG> — <Title>

**Milestone:** v1.X <milestone-name>
**Source upstream:** <citations>
**Cross-phase accretion:** Phase N (what each phase contributed)
**Schema:** <locked schema note if applicable>

## Summary

<2-5 sentence overview of the full document scope.>

## 1. <First section>
...
```

**Section layout for meta adapter spec** (canonical investigation, full derivation):

```markdown
# AT28C04-ADAPTER — DIP24→DIP32 Adapter Derivation

**Milestone:** v1.13 Programming Algorithm Validation + Gap Implementation
**Phase:** 76 (Spec-Only Gaps — adapter-required + X88C64)
**Cross-phase accretion:** Phase 76 (initial derivation + pin table)

## Summary

Why the adapter is needed; which chips; firmware handler; graduation path.

## 1. Scope — Chips Covered

List of all 9 adapter-required chips with part numbers.

## 2. Pinout Sources

DIP24_2816 entry from pinouts.json (ground truth); DIP32_28C512_EEPROM entry
from pinouts.json; AT28C16 datasheet cross-check.

## 3. Adapter Pin Table

Full 24-row table with source citations per pin mapping.
Unconnected socket pins listed separately.

## 4. Key Re-route: /WE (chip pin 21 → socket pin 30)

Derivation narrative: why chip pin 21 must reach socket pin 30,
what happens without the adapter (socket pin 21 = D7 in DIP32 layout).

## 5. Safety Analysis

No VPP rail; 5V-only chip; no high-voltage hazard; AT28C04 NC pins.

## 6. Future Graduation Steps

What is needed to graduate these chips to supported:
physical adapter + golden write+read-back round-trip + test coverage.
```

---

### `.planning/X88C64-FEASIBILITY.md` (GAP-02 verdict doc, D-01)

**Analog:** `.planning/v1.7-SHIELD-REVS.md` investigation sections (§4 style — evidence + verdict tables)

**Document structure pattern** (investigation verdict format used across meta planning docs):
```markdown
# X88C64-FEASIBILITY — XICOR X88C64P RURP Feasibility Verdict

**Phase:** 76 (Spec-Only Gaps)
**Status:** VERDICT CLOSED — documented feasible-candidate; handler deferred

## Summary

One-paragraph verdict: parallel DIP24, 5V; 8051 multiplexed-bus interface
(ALE/WR/RD); MEDIUM feasibility; no STORE/RECALL pins (correction to prior
wrong classification); handler not committed this phase.

## 1. Device Identity

Part number, manufacturer, organization (8K×8), package (DIP24P), technology,
VCC (5V ±10%), dual-plane architecture. Citations: alldatasheet.com datasheet.

## 2. Interface Architecture

Critical finding: 8051 multiplexed address/data bus — NOT standard /WE /OE /CE.
Pin table (24 pins, citing datasheet page 2).
Comparison to standard RURP parallel bus.

## 3. Write Protocol

ALE latch sequence; /WR strobe; page-write (up to 32 bytes); toggle-bit polling;
write abort via WC; block protect register.
Correction: no STORE/RECALL pins (the X2210/X2212 NOVRAM family has these —
X88C64P does not).

## 4. RURP Feasibility Assessment

| Dimension | Assessment | Notes |
|-----------|-----------|-------|
| Socket | Compatible | DIP24, fits with physical adapter |
| Voltage | Compatible | 5V-only, no VPP required |
| Bus protocol | Non-trivial | ALE-latch + /WR-strobe differs from std parallel |
| ALE signal routing | Open question | Needs RURP control-register investigation |
| Overall | MEDIUM — feasible-candidate | Handler not implemented this phase |

## 5. What is Needed for a Handler

ALE routing investigation (rurp_pinout.h control bits);
firmware ALE/WR/RD sequence implementation;
bench verification on physical DIP24 chip.

## 6. Assumptions Log

| # | Claim | Risk if Wrong |
|---|-------|---------------|
(3–5 rows matching RESEARCH.md assumptions A4/A5)

## 7. Sources

Datasheet citations; bitsavers.org Xicor 1985 Data Book (X2210/X2212 NOVRAM family
confirmation); build_db.py current entry (verified).
```

---

## Shared Patterns

### Alias extraction (chip name matching)
**Source:** `firestarter_app/tests/test_build_db_inclusion.py` lines 49–56; `firestarter_app/tools/build_db.py` (same idiom in context around line 188 per RESEARCH.md)
**Apply to:** Named-arm implementation in build_db.py; new tests in test_build_db_inclusion.py
```python
def _aliases(chip):
    pn = chip.get("part_number", "")
    return {a.split("@")[0].strip() for a in pn.split(",") if a.strip()}

# In build_db.py, `name` is the raw infoic.xml name string (comma-separated aliases):
_chip_aliases = {a.split("@")[0].strip() for a in name.split(",") if a.strip()}
```

### Test scaffold pattern (load DB + iterate + assert)
**Source:** `firestarter_app/tests/test_build_db_inclusion.py` lines 425–447
**Apply to:** All new tests in test_build_db_inclusion.py
```python
db = _load_db()
found = []
for mfg, chip in _all_chips(db):
    al = _aliases(chip)
    if "<SENTINEL>" in al:
        found.append((mfg, chip))
assert found, "<SENTINEL> not found in chip_database.json"
for mfg, chip in found:
    # assert invariant on chip fields
```

### Two-layer lockstep doc pattern
**Source:** `firestarter/doc/SHIELD-REVISIONS.md` (operator-facing) + `.planning/v1.7-SHIELD-REVS.md` (meta)
**Apply to:** `firestarter/doc/AT28C04-ADAPTER.md` + `.planning/AT28C04-ADAPTER.md`
- Operator-facing doc: 3–4 sections, omits full derivation/evidence, cross-references meta doc
- Meta doc: full 5–7 sections, all citations, derivation narrative, assumptions log
- Both files stay in lockstep: changes to the pin table go to BOTH files in the same commit

### reason-string format invariants (locked taxonomy)
**Source:** `firestarter_app/tests/test_build_db_inclusion.py` lines 425–473
**Apply to:** Named-arm reason string + X88C64 reason reword
- `adapter-required` reason: MUST start with `"adapter required:"`
- `protocol-not-implemented` reason: MUST contain `"protocol not implemented"` substring (case-insensitive)
- Both tested by existing tests in `TestUnsupportedReasonStrings`; new strings must pass existing tests without modification

### Gate verification sequence
**Source:** RESEARCH.md §Validation Architecture
**Apply to:** After every build_db.py change
```bash
cd firestarter_app
python tools/build_db.py           # regenerate chip_database.json
python tools/diff_db.py            # expect: 1 chip changed (X88C64P reason), RULE_PHASE66
python tools/check_dispatch.py     # expect: 744 chips, 0 violations
pytest tests/test_build_db_inclusion.py -v
```

---

## No Analog Found

All five files have analogs in the codebase. No new patterns need to be invented.

---

## Metadata

**Analog search scope:** `firestarter_app/tools/`, `firestarter_app/tests/`, `firestarter/doc/`, `.planning/`
**Files scanned:** 5 (build_db.py, test_build_db_inclusion.py, SHIELD-REVISIONS.md, v1.7-SHIELD-REVS.md, plus test scaffold helpers)
**Pattern extraction date:** 2026-06-18
