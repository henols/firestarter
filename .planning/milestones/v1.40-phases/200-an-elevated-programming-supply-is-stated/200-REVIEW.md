---
phase: 200-an-elevated-programming-supply-is-stated
reviewed: 2026-09-19T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - firestarter_app/firestarter/eprom_info.py
  - firestarter_app/tests/__snapshots__/test_characterization.ambr
  - firestarter_app/tests/test_characterization.py
  - firestarter_app/tests/test_cli_handlers.py
  - firestarter_app/tests/test_programming_vcc_census.py
findings:
  critical: 1
  warning: 2
  info: 1
  total: 4
status: issues_found
---

# Phase 200: Code Review Report

**Reviewed:** 2026-09-19
**Depth:** standard
**Files Reviewed:** 5 (all inside the `firestarter_app` submodule; diffed against submodule commit `0d6be3f`)
**Status:** issues_found

## Summary

This phase adds `programming_vcc_over_rail_mv()` and the two gated "Programming VCC" output
blocks in `eprom_info.py`, plus a 509-line census test module, two new characterization
snapshots, and two new in-process CLI tests. The numeric claims are not vacuous: I
independently recomputed the census directly against the shipped `chip_database.json` and
`tools/datasheet_overrides.json` (746 total rows, 284 elevated, vdd histogram
`{5500: 164, 6000: 8, 6250: 7, 6500: 105}`, exactly the 3 named datasheet-cited keys) and every
number matches what the tests assert. The source-shape guard's `+`-joined literals genuinely
avoid self-matching (verified by direct string search). The two gated output blocks in
`present_eprom_details` are written from a single call site that always sets
`programming_vcc_mv` and `programming_vcc_str` together, so they cannot disagree. Lint, format,
and the full targeted test run are green.

The one real defect is in the predicate itself: `programming_vcc_over_rail_mv()` documents an
explicit "must fail open" contract (D-06) that its own exception handling does not fully
implement — a plausible class of hand-edited `~/.firestarter/database.json` override
(`"electrical"` present but not a dict/None) raises an uncaught `AttributeError` instead of
returning `None`. The module's own "FAIL-OPEN" test does not exercise this shape, so the gap is
untested as well as unimplemented.

## Critical Issues

### CR-01: `programming_vcc_over_rail_mv` does not fail open when `electrical` is a non-dict, non-empty value

**File:** `firestarter_app/firestarter/eprom_info.py:63-71`

**Issue:** The docstring states (lines 48-57) that this function "must fail open" and enumerates
the malformed shapes it defends against: `raw_config_data` may be `None`, `electrical` may be
absent, and `vdd_mv` may be absent/`None`/`0`/a non-numeric string. The implementation only
catches `(TypeError, ValueError)`:

```python
try:
    vdd_mv = int((raw_config_data.get("electrical") or {}).get("vdd_mv", 0) or 0)
except (TypeError, ValueError):
    return None
```

If a hand-edited override sets `"electrical"` to any truthy non-dict value (a string, an int, a
non-empty list, `True`, or a JSON `null`... wait `None` is falsy so `null` is fine, but a
mistyped string/int/list value is not), `(... or {})` does not substitute `{}` because the value
is truthy, and `.get("vdd_mv", ...)` on that non-dict raises `AttributeError`, which is not in
the caught tuple. Verified directly:

```
>>> programming_vcc_over_rail_mv({"electrical": "bogus"})
AttributeError: 'str' object has no attribute 'get'
>>> programming_vcc_over_rail_mv({"electrical": 123})
AttributeError: 'int' object has no attribute 'get'
>>> programming_vcc_over_rail_mv({"electrical": [1, 2, 3]})
AttributeError: 'list' object has no attribute 'get'
```

This directly contradicts the function's own documented contract, which explicitly frames this
as a live production concern (the `~/.firestarter/database.json` override seam), not a
hypothetical. The `test_predicate_fails_open_on_absent_null_zero_and_non_integer_vdd` test does
not cover this shape, so the gap in the contract is also a gap in the test suite that is named
"FAIL-OPEN" and claims (module docstring, point 7) to prove the predicate "raises nothing" for
all such records.

Transparency note on current reachability: in the one real call path exercised by the CLI
(`cli_handlers.py` calls `app.db.get_eprom(eprom)` before `get_eprom_config(eprom)`), the
database's own `_map_data()` (`firestarter/database.py:356-358`, not in this phase's diff) does
`electrical = ic.get("electrical", {})` then `electrical.get("pin_count")` unconditionally, so
the *same* malformed `electrical` shape already raises `AttributeError` one layer earlier today,
before `programming_vcc_over_rail_mv` is ever reached from the `info` command. That is a
coincidental mitigation in a different, out-of-scope module, not a guarantee: `eprom_info.py`
exports and the test suite imports `programming_vcc_over_rail_mv` as a standalone predicate
(`test_programming_vcc_census.py` calls it directly against raw dicts with no `_map_data` in the
path at all), and the function's own docstring commits to a fail-open contract independent of
any caller. Shipping a predicate whose documented invariant is falsifiable by construction is a
correctness bug in the reviewed file, regardless of what currently shields it in one call site.

**Fix:** Widen the caught exception tuple, or validate the intermediate shape explicitly:

```python
try:
    electrical = raw_config_data.get("electrical")
    if not isinstance(electrical, dict):
        electrical = {}
    vdd_mv = int(electrical.get("vdd_mv", 0) or 0)
except (TypeError, ValueError, AttributeError):
    return None
```

and add a case to `test_predicate_fails_open_on_absent_null_zero_and_non_integer_vdd` (or a
sibling test) asserting `programming_vcc_over_rail_mv({"electrical": "bogus"})` and
`programming_vcc_over_rail_mv({"electrical": 123})` both return `None` rather than raising.

## Warnings

### WR-01: "FAIL-OPEN" test name overstates its own coverage

**File:** `firestarter_app/tests/test_programming_vcc_census.py:339-354`

**Issue:** `test_predicate_fails_open_on_absent_null_zero_and_non_integer_vdd` and the module
docstring's point 7 both claim the predicate "raises nothing" for malformed input, but the test
only exercises `vdd_mv`-level malformation (absent/`None`/`0`/non-numeric string) and
`raw_config_data`-level malformation (`{}`/`None`). It never exercises a malformed
`electrical` value, which is exactly the shape CR-01 breaks on. A reader trusting this test's
name would believe D-06 is fully proven; it is not.

**Fix:** Add the missing cases once CR-01 is fixed, e.g.:

```python
assert programming_vcc_over_rail_mv({"electrical": "bogus"}) is None
assert programming_vcc_over_rail_mv({"electrical": 123}) is None
assert programming_vcc_over_rail_mv({"electrical": [1, 2, 3]}) is None
```

### WR-02: Warning block indexes `chip_data['programming_vcc_mv']` directly instead of via `.get()`

**File:** `firestarter_app/firestarter/eprom_info.py:339-347`

**Issue:** Both the field-row block (line 316) and the warning block (line 339) are gated on the
same `"programming_vcc_str" in chip_data` check, and today they can never disagree because
`prepare_detailed_eprom_data` (lines 208-212) is the single call site that sets
`programming_vcc_mv` and `programming_vcc_str` together — so this is not a live bug. But the
warning block reads `chip_data['programming_vcc_mv']` with direct indexing rather than
`.get(...)`, unlike every other optional field in this same method (`chip_data.get(...)`
throughout). If a future edit ever sets `programming_vcc_str` without also setting
`programming_vcc_mv` (e.g. a refactor that renames one but not the other, or a partial
`combined_data` built by a caller other than `prepare_detailed_eprom_data`), this becomes a
`KeyError` crash on the console output path instead of a silently missing field, with no
compiler or test signal until it fires.

**Fix:** Use `.get("programming_vcc_mv")` for consistency with the rest of the method's
defensive style, or reference the same key both blocks are gated on rather than a second key
assumed to exist alongside it.

## Info

### IN-01: `_format_v_prose`'s `str.replace("v", " V")` depends on `format_mv`'s output shape never containing an incidental lowercase `v`

**File:** `firestarter_app/firestarter/eprom_info.py:28-37`

**Issue:** `_format_v_prose` re-spells `format_mv`'s output by blind substring replacement of the
first (and only) `"v"` in the string, relying on `format_mv` always producing exactly one
lowercase `v` as the trailing unit suffix (`f"{mv / 1000:.1f}v"`). This holds today and is
explicitly documented as intentional (single point of numeric truth), but it is a coupling
between two modules that a future change to `format_mv`'s format string (e.g. adding a unit
prefix, or switching to `"V"`) would silently break in a way `.replace` would not flag — it
would just produce a wrong or doubled substitution instead of an error.

**Fix:** No action required now; this is acceptable given the single-definition constraint the
docstring documents, but a comment note or a small format-mv-aware helper (e.g. splitting
mantissa/unit rather than string-replacing) would make the coupling more resilient to a future
`format_mv` change. Non-blocking.

---

_Reviewed: 2026-09-19_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
