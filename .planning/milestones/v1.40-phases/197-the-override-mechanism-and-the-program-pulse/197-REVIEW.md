---
phase: 197-the-override-mechanism-and-the-program-pulse
reviewed: 2026-09-18T00:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/datasheet_overrides.json
  - firestarter_app/tools/DECODE-NOTES.md
  - firestarter_app/tests/test_datasheet_overrides.py
  - firestarter_app/tests/test_build_db_constant_census.py
  - firestarter_app/tests/test_build_db_pinout_fork.py
  - firestarter_app/tests/test_build_db_inclusion.py
  - firestarter_app/tests/test_wire_dict_equivalence.py
  - firestarter_app/tests/golden/build_db_part_specific_constants.json
  - firestarter_app/tests/golden/chip_database_field_inventory.json
  - firestarter_app/tests/__snapshots__/test_characterization.ambr
findings:
  critical: 1
  warning: 4
  info: 0
  total: 5
status: issues_found
---

# Phase 197: Code Review Report

**Reviewed:** 2026-09-18
**Depth:** standard
**Files Reviewed:** 11 (`tests/golden/wire_dict_expected_deltas_197.json` reviewed as a golden data file cited by test_wire_dict_equivalence.py; no separate finding section needed for it)
**Status:** issues_found

## Summary

Reviewed `tools/build_db.py`'s new override mechanism (`load_datasheet_overrides` /
`apply_datasheet_override`), the shipped `tools/datasheet_overrides.json`, the deletion of the four
part-specific hardcodes, and the five new/extended test modules, against the diff from
`firestarter_app` commit `70c92ce`. Confirmed by direct execution: `tests/test_datasheet_overrides.py`,
`tests/test_build_db_constant_census.py`, `tests/test_build_db_pinout_fork.py`,
`tests/test_build_db_inclusion.py` and `tests/test_wire_dict_equivalence.py` all pass against the
current tree, and the constant-census detector independently reproduces the golden's single
survivor (`"DIP28"`) when run by hand against the live source.

The override mechanism's fail-closed contract (stale prior, unknown field, no-op, single-row
duplicate, unsorted file, type mismatch, unmatched key) is real and is exercised by tests, and the
abort genuinely happens before `json.dump`. The VPP ceiling check correctly stayed `>` (not `>=`)
and `support_status` is not an overridable field.

However, the "hoist" is incomplete: two of the six fields the mechanism advertises as overridable —
`electrical.pin_count` and `electrical.size_bytes` — are consumed by `resolve_pinout_key()` and
`classify()` *before* `apply_datasheet_override()` runs, not after. An override targeting either
field would silently produce an internally inconsistent database row (corrected size/pin-count
alongside a pinout/algorithm computed from the stale value), with no error raised and no test
covering the path. This is dormant today only because none of the 9 shipped entries happens to
target those two fields. Four further, lower-severity gaps are listed below.

## Critical Issues

### CR-01: `apply_datasheet_override` runs after two of its six overridable fields have already been consumed

**File:** `firestarter_app/tools/build_db.py:641-699`
**Issue:**

`_OVERRIDABLE_DECODED_FIELDS` (line 356) declares six fields as legitimate override targets,
including `electrical.pin_count` and `electrical.size_bytes`. But in `main()`, the sequence is:

```
641  pinout_key = resolve_pinout_key(pin_count, variant, flags, pm_idx=pm_idx,
                                      proto_id=proto_id, type_int=type_int, mem_size=mem_size)
...
670  _etype, proto_id, pinout_key = classify(type_int, proto_id, pm_idx, flags,
                                              pinout_key, mem_size)
...
679  _decoded_view = {"electrical.size_bytes": mem_size, "electrical.pin_count": pin_count, ...}
687  apply_datasheet_override(_datasheet_overrides, mfg_name, _chip_aliases,
                               _decoded_view, consumed_keys=_consumed_override_keys)
694  mem_size = _decoded_view["electrical.size_bytes"]
695  pin_count = _decoded_view["electrical.pin_count"]
```

`resolve_pinout_key` branches on `pin_count` (its top-level 24/28/32 dispatch) and on `mem_size`
(the 28-pin SRAM-size split and the 32-pin `proto_id==0x08` pin-31 boundary). `classify` also
branches on `mem_size` (the DIP28 SRAM/JEDEC re-route). Both run with the **raw, pre-override**
values. The override is applied only afterward, into a `_decoded_view` dict that is *disconnected*
from the `pin_count`/`mem_size` already baked into `pinout_key` and `proto_id`.

Concretely: if a future entry in `datasheet_overrides.json` corrects a chip's `electrical.pin_count`
or `electrical.size_bytes` (both are advertised as legal targets — `_OVERRIDABLE_DECODED_FIELDS`
lists them, and `tests/test_datasheet_overrides.py::test_boolean_does_not_satisfy_integer_type_check`
exercises `electrical.pin_count` as a target), the resulting `chip_entry` would carry the corrected
value in `electrical.pin_count`/`electrical.size_bytes` while `pinout` and `programming.algorithm`
stay whatever `resolve_pinout_key`/`classify` computed from the *original*, wrong value — an
internally inconsistent row shipped with no error and no test failure. This is invisible in a
byte-identical regeneration today only because none of the 9 shipped override entries targets these
two fields; the moment one does, it silently corrupts the row rather than raising.

**Fix:** Either (a) apply the override to `mem_size`/`pin_count` *before* calling
`resolve_pinout_key`/`classify` (splitting the override application into a pre-classification pass
for `size_bytes`/`pin_count` and a post-classification pass for `vpp_mv`/`vcc_mv`/`vdd_mv`/
`pulse_duration_us`, since the latter genuinely need the post-`classify()` `proto_id`), or (b)
narrow `_OVERRIDABLE_DECODED_FIELDS` to only the four fields the current call site can honor
correctly, and raise instead of silently accepting a `pin_count`/`size_bytes` override until (a) is
done.

## Warnings

### WR-01: Duplicate-target detection is scoped per row, not per override key

**File:** `firestarter_app/tools/build_db.py:440-461`
**Issue:** `apply_datasheet_override`'s `written_by` dict (line 455) is local to a single call, i.e.
to a single upstream `<ic>` row. `check_all_override_keys_consumed` (line 440) only asserts that
every override key was consumed by *at least one* row — it does not track how many rows consumed it.
If two distinct `<ic>` records under the same manufacturer ever shared an alias (a real upstream
data-quality possibility, not something the schema forbids), the same override entry would be
silently applied to both rows, with no duplicate-application error, even though the entry's `was`/
`is` pair was authored against one specific chip's decode. Verified against the live database that
none of the 9 shipped keys currently hits this (each key's alias set maps to exactly one physical
row), so this is a latent gap rather than a live defect.
**Fix:** Track `consumed_keys` per (entry_key) with a count, or refuse a second application of the
same key across rows unless explicitly intended, and add a regression test with two synthetic rows
sharing one alias under the same manufacturer.

### WR-02: A pulse-duration override can be silently discarded by the VPP-ceiling recompute

**File:** `firestarter_app/tools/build_db.py:701-708`
**Issue:**

```
701  if _d_vpp_mv > RURP_VPP_CEILING_MV:
702      _support_status = "vpp-exceeds-max"
...
707      proto_id = NON_DISPATCHABLE_ALGO
708      _d_pulse = interpret_timing(ic.get("pulse_delay"), proto_id)
```

`_d_pulse` was already set from `_decoded_view["programming.pulse_duration_us"]` at line 699 — i.e.
it already reflects any `apply_datasheet_override` correction. If the ceiling branch fires, line 708
unconditionally recomputes `_d_pulse` from the **raw upstream** `pulse_delay` with the demoted
`proto_id`, discarding whatever value the override mechanism had written. Today this is unreachable
(no shipped row carries both a `programming.pulse_duration_us` override and a `electrical.vpp_mv`
value that ends up over the 25 V ceiling), but it is a real contract violation waiting for the next
combination: an override that is supposed to be authoritative can be silently overwritten by later
generator logic with no error.
**Fix:** Either skip this recompute when the row's `programming.pulse_duration_us` was overridden
(track that in `written_by`/a return value from `apply_datasheet_override`), or re-run
`interpret_timing` and *then* re-apply only the pulse override, explicitly, rather than relying on
ordering to avoid collision.

### WR-03: The loader enforces a weaker datasheet-citation contract than the test suite documents

**File:** `firestarter_app/tools/build_db.py:410-422`
**Issue:** `_validate_datasheet_overrides_shape` only checks that a non-`UNSOURCED` `datasheet`
value is a non-absolute string for which `os.path.exists(os.path.join(app_root, datasheet))` is
true. It does not check that the path is git-tracked, and it does not reject `..`-escaping relative
paths that resolve outside the repository. The stronger contract described by the phase ("datasheet
must be either a git-tracked repo-relative path...") is enforced only by
`tests/test_datasheet_overrides.py::TestShippedOverrideFileContract::
test_every_datasheet_value_is_a_tracked_path_or_unsourced_with_note`, which is test-only code.
Running `python tools/build_db.py` standalone — the documented regen command in
`firestarter_app/CLAUDE.md` — would accept an override citing an uncommitted local file or a path
that escapes the repo via `../`, and would happily regenerate `chip_database.json` from it.
**Fix:** Move the git-tracked check (and a `..`-segment rejection) into
`_validate_datasheet_overrides_shape` itself so `build_db.py` fails closed independent of whether the
test suite runs first.

### WR-04: Misleading "Closed by" wording on all 6 UNSOURCED override notes

**File:** `firestarter_app/tools/datasheet_overrides.json:23-64` (all six `UNSOURCED` entries:
`INTEL/M2716`, `INTEL/M2732`, `SGS-THOMSON/M2716`, `SGS-THOMSON/M2732A`, `ST/M2716`, `ST/M2732A`)
**Issue:** Each note ends with a sentence of the shape:

> "No Intel datasheet for the 2716 is vendored in this repository, so that citation cannot be
> verified here. Closed by: Intel's own 2716 datasheet, vendored and git-tracked under datasheets/."

Read together, the second sentence uses present-tense, declarative phrasing ("Intel's own 2716
datasheet, vendored and git-tracked under datasheets/") immediately after stating that no such file
exists — this reads as though the value were already datasheet-confirmed by a tracked file. It is
not: `find`-ing the repo's `datasheets/` directory turns up no 2716/2732/M2732A PDF from any of the
three cited manufacturers. The intent is clearly a *future* closure criterion ("this UNSOURCED
status will be resolved once such a datasheet is vendored"), but the wording as written does not say
that; it reads as a present-tense claim contradicting the sentence right before it. This is exactly
the failure mode the review brief calls out: a note that reads as though an unsourced value were
datasheet-confirmed.
**Fix:** Reword to explicit future/conditional phrasing, e.g. "Will be closed once Intel's own 2716
datasheet is vendored and git-tracked under datasheets/ — no such file exists in this repository
today." Apply the same fix to all six entries.

---

_Reviewed: 2026-09-18_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
