---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
reviewed: 2026-09-09T00:00:00Z
depth: standard
files_reviewed: 26
files_reviewed_list:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/diagnostic_report.py
  - firestarter_app/firestarter/submit.py
  - firestarter_app/tests/plan_corpus.py
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_canonical_part_number.py
  - firestarter_app/tests/test_check_devtest_orchestrator.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_chip_test_blank_check_order.py
  - firestarter_app/tests/test_chip_test_cycle.py
  - firestarter_app/tests/test_chip_test_sdp_leg.py
  - firestarter_app/tests/test_chip_test_timing.py
  - firestarter_app/tests/test_derive_plan_no_drop_sweep.py
  - firestarter_app/tests/test_derive_plan_structural_sentinel.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_diagnostic_report.py
  - firestarter_app/tests/test_erase_flag_invariants.py
  - firestarter_app/tests/test_plan_shapes_drift.py
  - firestarter_app/tests/test_provenance.py
  - firestarter_app/tests/test_readback_inventory.py
  - firestarter_app/tests/test_runtime_dependencies.py
  - firestarter_app/tests/test_submit.py
  - firestarter_app/tests/test_voltage_field_census.py
  - firestarter_app/tools/check_devtest_orchestrator.py
  - firestarter_app/tools/measure_plan_shapes.py
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 181: Code Review Report

**Reviewed:** 2026-09-09
**Depth:** standard (with targeted cross-file tracing on the flagged risk areas)
**Files Reviewed:** 26
**Status:** issues_found

## Summary

Reviewed the app-side diff between `04fd982` and the current `HEAD` for phase 181
(report fidelity / schema 2.0 / canonical naming / `write_scope` hygiene / close).
This is an unusually well-defended change set: nearly every behavioral change is
backed by an anti-vacuity test (a planted mutation that is observed to redden the
new assertion), and the areas flagged as high-risk in the task brief were traced
in full:

- **`_canonical_part_number`** (`cli_handlers.py`) mirrors `database.get_eprom_config`'s
  exact → alias-exact → paren-stripped ladder rung for rung, confirmed by
  comparing both implementations line by line and by the dedicated
  `test_canonical_part_number.py` sweep over the whole measured alias domain.
  No divergence found.
- **The unified write-refusal predicate** (`chip_test._write_step_was_refused`)
  is consumed at both call sites (`diagnostic_report._write_coverage_line`'s
  `slots_remaining - 1` subtraction and `build_db_diff`'s fourth ladder arm).
  The `slots_remaining` arithmetic in `chip_test._resolve_write_target` is
  intentionally the *before-this-run* count (inclusive of the slot about to be
  consumed); the `-1` correction lives, correctly, at the one point that also
  knows whether the write actually ran. Traced through `WriteTarget`'s
  docstring, `_write_coverage_line`'s docstring, and the dedicated
  `test_slots_remaining_line_reports_after_this_run_when_the_write_ran` /
  `..._reports_the_resolved_count_when_the_write_was_refused` test pair — this
  is by design, not a bug.
- **`duration_s` as a mean**: divisor is `len(durations)`, built only from
  cycles whose verdict is in `_RAN_VERDICTS` (the same population `run_count`
  reports), and the whole expression is guarded by `if durations else None` —
  no division-by-zero path exists.
- **`elapsed`**: stamped exactly once, in `cli_handlers.dev_test`, before the
  first of three `to_dict()` calls; `DiagnosticReport.to_dict()` only reads the
  stored attribute, never recomputes it.
- **`write_scope`**: every call site in production and test code now passes an
  explicit `"full"` or `"partial"` string; the two-value `frozenset` with no
  default is enforced correctly (`derive_plan` raises `ValueError` on anything
  else, `TypeError` on an omitted keyword).
- **`_voltage_dict()`**: `vpp_mv`/`vpe_mv` are gone from the dataclass and the
  dict; no remaining caller (production or test) reads those keys — confirmed
  by grep and by the new `test_voltage_field_census.py` AST census.

One genuine, phase-introduced defect was found: an incomplete cleanup in the
`write_scope`/`_resolve_write_scope` removal left a now-dead helper function
behind, together with test infrastructure that no longer controls what it
claims to control (see WR-01).

## Warnings

### WR-01: `_is_interactive()` is dead code as of this phase, and the tests that patch it no longer control anything

**File:** `firestarter_app/firestarter/cli_handlers.py:2299-2306`
**Also affects:** `firestarter_app/tests/test_dev_test_cmd.py` (module docstring lines 8-14, `_off_tty()` at line 518-520, and the `patch("firestarter.cli_handlers._is_interactive", return_value=True)` sites in `TestUVWriteHasNoPrompt` at lines 843 and 871)

**Issue:** Before this phase, `dev_test`'s body called `interactive = _is_interactive()`
and threaded the result into `_resolve_write_scope(app, chip, interactive=interactive)`
(confirmed against the pre-phase source at `04fd982:firestarter/cli_handlers.py:2401`).
Plan 181-04 deleted `_resolve_write_scope` and inlined its two-line rule directly
at the `derive_plan` call site — but it deleted the `interactive = _is_interactive()`
call site without deleting the `_is_interactive()` function definition itself.
An AST scan of the current `cli_handlers.py` confirms zero call sites:

```
$ python -c "... ast.walk over cli_handlers.py, collect Call nodes whose func.id == '_is_interactive' ..."
call sites: []
```

`_is_interactive` is still present in `tools/check_devtest_orchestrator.py`'s
`_HANDLER_FUNCTION_NAMES` allow-list and is still monkeypatched by several
tests in `test_dev_test_cmd.py` (`_off_tty()`, and the two `return_value=True`
patches in `TestUVWriteHasNoPrompt`), but none of those patches have any
effect on the code under test any more: `dev_test` never reads
`_is_interactive`, and `submit_report`'s own TTY detection
(`firestarter/submit.py:701`, `isatty_fn = isatty_fn or (lambda: sys.stdin.isatty())`)
reads `sys.stdin.isatty()` directly and independently. Under
`click.testing.CliRunner`, `sys.stdin` is always replaced with a non-tty
stream, so every one of these tests already runs the off-TTY path — the
`patch(...return_value=True)` calls that are supposed to simulate an
interactive terminal in `test_uv_part_writes_one_slot_on_a_tty` and
`test_non_uv_part_is_still_written_in_full_without_a_prompt` (lines 843, 871)
do nothing, and those two tests never actually exercise an on-TTY code path
despite their names and docstrings.

The module docstring at the top of `test_dev_test_cmd.py` (lines 8-14) still
asserts this mechanism is load-bearing ("TTY-gating is controlled by patching
the module-level `firestarter.cli_handlers._is_interactive` function directly
… because `patch("sys.stdin.isatty", ...)` … silently does not survive") — that
claim was true before this phase and is stale now.

This is not an observable behavioral regression today (the assertions these
tests make about write-op selection and exit codes still hold, because they
hold identically on and off a real TTY now that the UV write prompt is gone).
It is a maintenance hazard: a future change that reintroduces any interactive
prompt keyed on real TTY detection would not be caught by
`test_uv_part_writes_one_slot_on_a_tty` / `test_non_uv_part_is_still_written_in_full_without_a_prompt`,
because those tests believe they are simulating an interactive terminal and
are not.

**Fix:** Either delete `_is_interactive()` (and its `_HANDLER_FUNCTION_NAMES`
entry, and the `_off_tty()`/`patch(...)` call sites, replacing them with
whatever the real off-TTY control point is — currently none is needed since
`dev_test` has no TTY-conditional logic left) or, if the seam is being kept
intentionally for a future reintroduction, wire it back into `dev_test`'s body
(or into `submit_report`'s `isatty_fn` parameter) so patching it actually
changes behavior again. At minimum, update the `test_dev_test_cmd.py` module
docstring so it no longer claims a mechanism that does not function.

## Info

### IN-01: `_chip_id_fields` walks `results` twice for two related lookups

**File:** `firestarter_app/firestarter/cli_handlers.py:2211-2244`
**Issue:** `_chip_id_fields` iterates `results` once to find `chip_id_actual`
(`for r in results: if r.op == OP_ID: chip_id_actual = r.chip_id_detected; break`)
and then iterates it again for `mismatch_reason` (`for r in results: if r.op ==
OP_ID and r.reason and "mismatch" in r.reason.lower(): ...`). Both loops key on
the same `r.op == OP_ID` predicate and, since a `Plan` only ever emits one `id`
step, could be merged into a single pass. Not a correctness issue (the two
loops cannot disagree on which step they inspect), just a minor duplication.
**Fix:** Combine into one loop over `results` that sets both `chip_id_actual`
and `mismatch_reason` once the `OP_ID` result is found, e.g.:

```python
for r in results:
    if r.op == OP_ID:
        chip_id_actual = r.chip_id_detected
        if r.reason and "mismatch" in r.reason.lower():
            mismatch_reason = r.reason
        break
```

---

_Reviewed: 2026-09-09_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
