---
phase: 179-uv-slot-writes-flag-skip-blank-check-hardware-gated
reviewed: 2026-09-08T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/tests/fake_chip.py
  - firestarter_app/tests/fixtures/rekey_ledger.py
  - firestarter_app/tests/fixtures/report_shapes.py
  - firestarter_app/tests/fixtures/reports/m27c512-full-blank-check-bad.json
  - firestarter_app/tests/fixtures/reports/uv-slot-write-pass.json
  - firestarter_app/tests/fixtures/shape_ids.json
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_chip_test_cycle.py
  - firestarter_app/tests/test_chip_test_uv_slot_write.py
  - firestarter_app/tests/test_dev_test_cmd.py
  - firestarter_app/tests/test_uv_mask.py
findings:
  critical: 0
  warning: 1
  info: 1
  total: 2
status: issues_found
---

# Phase 179: Code Review Report

**Reviewed:** 2026-09-08T00:00:00Z
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

Reviewed the submodule diff (`git -C firestarter_app diff 835baba..HEAD`) for the six phase commits, focused on `chip_test.py`'s changed regions and their immediate callers, plus the full new/changed test and fixture files.

All five claims in `<what_the_phase_claims>` were traced against the actual code and hold:

1. `FLAG_SKIP_BLANK_CHECK` is passed as the 4th **positional** argument at the one live call site (`chip_test.py:3261-3268`, inside `_dispatch_multi_run`), matching `EpromOperator.write_eprom`'s real positional signature (`eprom_operations.py:1967`). No keyword call exists anywhere in the diff. Confirmed two of three write-capable test doubles in `tests/test_dev_test_cmd.py` (pre-existing, not part of this diff) name the 4th parameter `flags` rather than `operation_flags` — a keyword call would silently misroute into `**_kw` on those doubles, but the call site never uses keyword form, so this is inert.
2. The blank-check "not blank" finding survives as `reason` + firmware `error_code` on the new `SKIPPED` verdict (`chip_test.py:2670-2682`) — the adjudication downgrades only the verdict, never the evidence. Confirmed by `tests/test_chip_test_uv_slot_write.py::test_uv_slot_write_preserves_the_not_blank_finding` and the `uv-slot-write-pass.json` fixture.
3. The skip is derived structurally from `_is_monotonic_masked_target` (`target.masked and bool(target.current) and target.current_is_probe_read`), never from `region_policy` or a `current_source` string-equality — confirmed by legs 7/8 in `test_chip_test_uv_slot_write.py`, which construct the two signals in disagreement via the public `WriteContext.cycle_targets` seam, and leg `test_the_prescribed_probe_read_string_equality_would_never_match`, which measures that the staged tranche's `current_source` never equals `"probe read"` verbatim.
4. The twelve legs in `test_chip_test_uv_slot_write.py` are non-vacuous: legs 1-2 assert the double actually refuses without the flag and accepts with it; leg 6 forces the blank-check verdict back to `BAD` on a deep copy and asserts the fold flips to `FAIL`, proving the `PASS` in leg 3 is produced by the adjudication and not by coincidence.
5. `RESERVED_SHAPE_IDS` is `frozenset()` and its emptiness is asserted explicitly in `test_build_shape_raises_for_every_reserved_shape_id` (with an added unregistered-sentinel probe), not left to a now-zero-iteration loop.

Ran the full touched-file test suite under the CI-replica Python 3.11 venv (`.venv/ci-replica`): 239 passed. `ruff check` and `ruff format --check` both clean on all 9 non-fixture-JSON files in scope. No `#`-comments were added by this phase's diff anywhere in the reviewed files (grepped the diff directly), so the project's no-comments rule is not implicated.

One real defect was found in the new test-double code (`tests/fake_chip.py`), detailed below — it does not affect the phase's own tests (unexercised today) but is exactly the "absent-chip false-green" failure pattern this codebase's design otherwise goes out of its way to guard against, so it is worth fixing before it silently defeats a future test.

## Warnings

### WR-01: `WriteInitPreflightChip.__init__` freezes `check_eprom_id` at construction time, defeating `id_ok`/`id_value` and the `calls` log

**File:** `firestarter_app/tests/fake_chip.py:263`
**Issue:** `WriteInitPreflightChip.__init__` does:
```python
setattr(self, "check_eprom_id", Mock(return_value=(True, self.id_value)))
```
This replaces the inherited `FakeChip.check_eprom_id` (which reads `self.id_ok`/`self.id_value` **live**, and appends to `self.calls`) with a `Mock` whose return value is captured **once**, at `__init__` time, when `self.id_value` is still `None` (its `FakeChip.__init__` default). Three consequences:

- `self.id_ok` is ignored entirely — the mock always reports `id_ok=True` regardless of what a test sets it to afterward. A test that does `chip.id_ok = False` to exercise the chip-ID-mismatch destructive gate (`_DESTRUCTIVE_GATE_REASON` / `destructive_gate_closed` in `chip_test.py`) against this specific double would silently get a passing ID check instead — a false green.
- `self.id_value` mutated after construction has no effect — the mock always returns the frozen `None` captured at `__init__`.
- The call is not recorded in `self.calls`, breaking the class-level contract stated in `FakeChip`'s own docstring ("`calls` is a plain list of `(method_name, kwargs)` tuples so a test can assert which addresses/sizes were actually requested").

No test in this phase currently sets `id_ok`/`id_value` on a `WriteInitPreflightChip` instance, so the defect is latent, not currently causing an observed-wrong result. But it is unnecessary: with `id_ok=True, id_value=None` as `FakeChip`'s own defaults, the override is currently a no-op functionally — it exists only as a footgun for the next person who reuses this double for an id-check-focused test, in a codebase whose central design principle (stated repeatedly in `chip_test.py`'s own docstrings — "the absent-chip false-green trap", "a `Mock` that answers `True` with no chip attached") is precisely to prevent this shape of bug.

**Fix:** Delete the `setattr` line; the inherited `FakeChip.check_eprom_id` already does the right thing (reads `id_ok`/`id_value` live, logs to `calls`):
```python
def __init__(self, memory_size: int, *, uv: bool = False):
    super().__init__(memory_size, uv=uv)
    self.last_firmware_error_code: int | None = None
    self.last_firmware_error_message: str | None = None
    self.write_flags_seen: list[int] = []
```

## Info

### IN-01: `WriteInitPreflightChip.write_eprom`'s refusal path does not log the attempt to `self.calls`

**File:** `firestarter_app/tests/fake_chip.py:280-296`
**Issue:** On the firmware-refusal path (target not blank, `FLAG_SKIP_BLANK_CHECK` absent), `write_eprom` returns `False` before ever reaching `super().write_eprom(...)`, so the attempted call is never appended to `self.calls` (unlike every other path through this double, and unlike the class's own stated "`calls` … so a test can assert which addresses/sizes were actually requested" contract). A future test wanting to assert "a write was attempted at address X even though it was refused" cannot do so via `chip.calls` on this double.
**Fix:** Log the attempt before the refusal check, e.g. `self.calls.append(("write_eprom", {"address_str": address_str}))` at the top of the override, mirroring the base class.

---

_Reviewed: 2026-09-08T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
