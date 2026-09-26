---
phase: 69-cli-command-surface-robustness-audit
reviewed: 2026-06-15T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - firestarter_app/firestarter/ic_layout.py
  - firestarter_app/tests/test_ic_layout.py
  - firestarter_app/tests/test_cli_handlers.py
  - firestarter_app/tests/test_eprom_info.py
  - firestarter_app/tests/test_characterization.py
findings:
  critical: 0
  warning: 3
  info: 5
  total: 8
status: issues_found
---

# Phase 69: Code Review Report

**Reviewed:** 2026-06-15
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Phase 69 fixes the `TypeError: '<=' not supported between instances of 'list' and 'int'`
in `ic_layout._generate_pin_names_for_display` by scalar-extracting list-valued pin
fields (`rw-pin` / `vpp-pin` / `oe-pin`) with the inline `val[0] if isinstance(val, list)
else val` pattern at every comparison/index site. The fix is correct, mirrors the
established `database.get_bus_config` pattern (database.py:289), and is verified against
the real packaged DB for all four representative chips. The full test suite for the
affected files passes (108 tests + 29 snapshots, no failures).

The production change itself is sound. The findings below concern (a) a latent
incomplete-bounds-guard that the new code inherits and does not close, (b) display
correctness gaps for chips whose protocol is unknown to the display tables, and
(c) test-suite quality debt (stale RED-test docstrings, a no-op test).

No BLOCKER-class defects were found: the scalar-extraction fix does not introduce
incorrect behavior, security exposure, or data-loss risk.

## Warnings

### WR-01: Pin-number guards check only the upper bound — `pin_num < 1` would produce a negative index write

**File:** `firestarter_app/firestarter/ic_layout.py:395,400,406,411,417`
**Issue:** Every guarded pin assignment checks only `pin <= pin_count` before doing
`pin_names[pin - 1] = ...`. If any pin field resolved to `0` (or a negative value), the
guard passes and `pin_names[-1]` silently overwrites the **last** pin (VCC) instead of
raising — a silent-corruption path rather than a crash. This is the same class of latent
defect the phase set out to harden (a malformed input producing wrong output instead of a
clean refusal), and the new code re-establishes it at five sites without a lower bound.

Audit of the current packaged `pinouts.json` shows the minimum pin value is `1`, so this
is **not currently triggerable** — hence WARNING, not BLOCKER. But the pin maps are also
sourced from user `~/.firestarter` overrides and the `infoic.xml`→`build_db.py` pipeline,
neither of which is guaranteed to emit `>= 1`.

**Fix:** Tighten each guard to a closed range, e.g.:
```python
rw = rw[0] if isinstance(rw, list) else rw
if 1 <= rw <= pin_count:
    pin_names[rw - 1] = "R/W(WE)"
```
Apply the same `1 <= n <= pin_count` bound to the `vpp`, `oe`, and `address-bus-pins`
(`pin_num`) sites (lines 397, 402, 408, 413, 419).

### WR-02: Empty / non-int list extraction is unguarded — `[]` or `[null]` pin field raises IndexError / TypeError

**File:** `firestarter_app/firestarter/ic_layout.py:394,399,405,410`
**Issue:** The fix assumes a list-valued pin field is always a non-empty list of ints.
`val[0]` on an empty list (`"vpp-pin": []`) raises `IndexError`, and a list of a non-int
(`"vpp-pin": [null]` → `[None]`) makes the subsequent `None <= pin_count` raise the exact
`TypeError` class this phase exists to eliminate — just shifted from "list" to "NoneType".
The membership check (`if "vpp-pin" in pin_map_details`) only proves the key exists, not
that its value is a usable scalar. No current DB entry hits this, but the guard the phase
added is narrower than the failure surface it claims to cover ("the crash class cannot
reappear", test_ic_layout.py:11).

**Fix:** Make extraction defensive, e.g. a small helper:
```python
def _scalar_pin(val):
    if isinstance(val, list):
        val = val[0] if val else None
    return val if isinstance(val, int) else None
...
vpp = _scalar_pin(pin_map_details.get("vpp-pin"))
if vpp is not None and 1 <= vpp <= pin_count:
    ...
```
This collapses WR-01 + WR-02 into one reusable, fully-bounded extraction.

### WR-03: Stale RED-test docstrings assert tests "MUST FAIL until 53-02" but Phase 53 shipped — masks regressions

**File:** `firestarter_app/tests/test_cli_handlers.py:705-778`
**Issue:** The four `dev write-cycle` / `dev fault-inject` tests carry header/docstrings
stating "All four tests MUST FAIL until 53-02 registers the subcommands" and "FAILS RED
until 53-02 ... (Click: 'No such command')". Phase 53 (CAP-01 / write-cycle) shipped per
project history (v1.10), and these tests currently PASS. A reviewer or CI triager reading
these docstrings would mis-diagnose a genuine *future* regression (e.g. the subcommand
gets unregistered) as "expected RED state" and ignore it. The comment block is now
actively misleading about the meaning of a failure.

**Fix:** Delete the obsolete RED-phase preamble (lines 705-711) and the "FAILS RED until
53-02" sentences in each of the four docstrings; replace with a plain statement that these
pin the registered `dev write-cycle` / `dev fault-inject` 3-way verdict contract.

## Info

### IN-01: Redundant `get_chip_type_string` call — computed and assigned twice

**File:** `firestarter_app/firestarter/ic_layout.py:467-469,484-487`
**Issue:** `output_data["type_str"]` is set by a `get_chip_type_string(...)` call inside the
dict literal (line 470-472), then immediately recomputed with identical arguments and
reassigned at lines 484-487. The first computation is dead.
**Fix:** Drop the `type_str` entry from the dict literal (or drop the lines 484-487
recomputation) and keep one call.

### IN-02: Chips with a protocol unknown to the display tables render a misleading type

**File:** `firestarter_app/firestarter/ic_layout.py:204-223,249-368`
**Issue:** `get_chip_type_string` and `_get_protocol_info_structured` carry disjoint,
hand-maintained protocol ID tables. For X88C64P (protocol `0x34`, XICOR NovRAM — exactly
the chip exercised by `test_info_protocol_not_implemented_no_crash`), `0x34` is absent from
both tables: `protocol_info` resolves to `None` and `type_str` falls through to the numeric
`type_map`, displaying **"EPROM"** for a NovRAM. The CLI test only asserts "no traceback /
exit 0", so it does not catch the wrong label. Additionally `get_chip_type_string`'s
`proto_display` lists `0x35`/`0x39` which `_get_protocol_info_structured` omits — the two
tables have drifted. Display-only, pre-existing (not introduced by Phase 69).
**Fix:** Add a `0x34` entry to both tables, and consider deriving both from a single
source-of-truth protocol map to prevent further drift.

### IN-03: Dead method `_get_rev2_2_jumper_settings_data`

**File:** `firestarter_app/firestarter/ic_layout.py:175-190` (call site commented out at 557)
**Issue:** `_get_rev2_2_jumper_settings_data` is never invoked — its only call site is the
commented-out line 557. (Were it re-enabled, line 557 passes `jp4_rev2` for the `jp5`
parameter, so the dead code is also latently incorrect.) Pre-existing.
**Fix:** Remove the method and the commented call, or wire it in correctly with a dedicated
`jp5` value if Rev 2.2 jumper display is intended.

### IN-04: No-assertion test provides no regression value

**File:** `firestarter_app/tests/test_eprom_info.py:105-110`
**Issue:** `test_present_eprom_details_none_returns_early` calls `present_eprom_details(None)`
and asserts nothing ("just that it does not raise"). A test with no assertion only fails on
an exception; it documents intent but does not pin behavior (e.g. that nothing is printed).
**Fix:** Assert the observable contract, e.g. `captured = capsys.readouterr(); assert
captured.out == ""` (the fixture already requests `capsys`).

### IN-05: `tests/test_ic_layout.py:38` docstring mislabels 2732 as "vpp-exceeds-max"

**File:** `firestarter_app/tests/test_ic_layout.py:38`
**Issue:** The parametrize comment for `2732` says "vpp-exceeds-max, shared vpp/oe-pin=[20]".
"vpp-exceeds-max" is a chip *support_status*, unrelated to the pin index; conflating it
with the pin-map shape in a comment that explains *why this chip exercises the fix* is
mildly misleading to a future maintainer. Documentation-only.
**Fix:** Reword to describe the pin-map shape only (e.g. "DIP24, shared vpp/oe-pin=[20] —
list-valued shared pin"), matching the W27C512 entry's style.

---

_Reviewed: 2026-06-15_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
