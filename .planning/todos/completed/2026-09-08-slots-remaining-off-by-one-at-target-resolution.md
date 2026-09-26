---
title: slots_remaining is computed before the write that consumes the slot, so a UV run reports one more slot left than it has
date: 2026-09-08
priority: medium
blocked_by: nothing technical — the fix is a one-line index adjustment plus a decision about whether the field means "before this run" or "after this run"; filed as a residual because it was surfaced by Phase 179's bench measurement rather than authored by it, and the field predates the phase.
resolves_phase: 181
resolved: 2026-09-09 (plan 181-08 -- fix applied at the disclosure point, not the resolver)
status: resolved
---

# `slots_remaining` off-by-one at target-resolution time (T-179-07)

## MEASURED, on real hardware

Phase 179's bench run (`179-MEASUREMENT.md`, real ST M27C512 on a Leonardo, firmware `3.0.0b22`,
slot `0xFF00`, exit `0`, `BENCH RESULT: PASS`) emitted this verbatim console line **after** a run
that had just programmed a slot:

```
slot 0xFF00 (256 bytes), 512 bits cleared this cycle; 256 of 256 slots left on this part
```

`256 of 256` is wrong. The run spent one slot — the artifact's own accounting says
`Slots spent this run: 1` — so 255 remained when that line was printed.

## Root cause

`firestarter_app/firestarter/chip_test.py:3014`:

```python
slots_remaining=slots_total - slot_index,
```

This is evaluated at **target-resolution** time, before the write executes. For the top slot
`0xFF00`, `slot_index` is `0`, so `slots_remaining` is `256 - 0 = 256` — a count of slots available
*going in*, reported with wording ("slots left on this part") that a reader takes as the state
*coming out*.

The surrounding retained comment block reasons correctly that a run saturates exactly one slot and
that "slots left" and "runs left on this part" are the same number. Both statements are true. The
defect is purely that the subtraction does not account for the slot the current run is about to
consume.

## Two candidate fixes, and the decision that has to come first

The one-line change is `slots_total - slot_index - 1`, but that is only right if the field is
supposed to mean "after this run". Decide the contract before patching:

1. **Field means "after this run"** (matches the current wording): subtract the current slot.
   Then a part on its last slot correctly reports `0 of 256 slots left`, which is also the signal
   [[project_v132_quick_260821_wna_uv_bitmask]]-adjacent tooling would want for an
   all-slots-exhausted part.
2. **Field means "available going in"**: keep the arithmetic and change the console wording so it
   no longer reads as a post-run state.

Option 1 is the better default — a reader of a completed run's report is asking what is left, not
what was available before it started.

## Why this is not a Phase 179 authoring defect

The field, the arithmetic and the console wording all predate Phase 179; the phase changed the
blank-check adjudication, not the slot accounting. Phase 179 is simply the first run to put a real
UV part through the full two-cycle path on the bench and therefore the first to read this line
against a known-correct expectation. Related but distinct from
`2026-09-08-uv-ladder-flip-on-exhausted-slots.md` (T-179-05), which is about how an
all-slots-exhausted run folds on `build_db_diff`'s ladder — that one is about the ladder arm, this
one is about the count.

## How to verify a fix

There is no committed leg pinning this line today. A fix should add one: build a UV plan whose
target resolves to a known `slot_index`, and assert the emitted `slots_remaining` against the
post-run expectation. The existing `tests/test_chip_test_uv_slot_write.py` module is the natural
home — it already constructs the UV slot-write path end to end against a firmware-faithful double,
so the leg costs no new fixture.

## RESOLUTION (2026-09-09)

Fixed by plan `181-08`, using Option 1 from this todo's own "two candidate fixes" analysis above
("field means after this run"). The fix is deliberately NOT the one-line resolver change this todo
proposed: `WriteTarget.slots_remaining`'s resolve-time expression
(`slots_total - slot_index`, `chip_test.py:3014`) is left byte-unchanged, because the resolver does
not yet know whether the write it is about to attempt will actually run. Instead,
`_write_coverage_line` — the one place that holds both the resolved count and the run's own outcome
— subtracts one from the resolved count when the write actually ran, and reports the resolved count
unreduced when the write was refused (sharing the `_write_step_was_refused` predicate with the
sibling ladder-flip fix, T-179-05). Tests:
`tests/test_chip_test_cycle.py::test_slots_remaining_line_reports_after_this_run_when_the_write_ran`,
`::test_slots_remaining_line_reports_the_resolved_count_when_the_write_was_refused`. Evidence:
`.planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-08-write-refused-predicate.txt`.
