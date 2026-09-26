---
title: dev test — adaptive, evidence-gated test sequencing
trigger_condition: Next milestone that touches `dev test` / chip_test.py. Explicitly NOT v1.35 (documentation-only). Natural carriers, whichever activates first: a `dev test` throughput milestone in its own right, or folded into the next chip-validation milestone that already has the engine open.
planted_date: 2026-08-30
status: R1 and R2 realized by Phase 177 (2026-09-05, PRUNE-01/02/03/04); R3 closed by Phase 180 (2026-09-08) as measured, not worth doing (PRUNE-08); R4 deferred to Future Requirements (R4-01/R4-02)
---

# `dev test` — adaptive, evidence-gated sequencing

Make `dev test` **31% faster across the chip classes modelled, and 55–60% faster
on UV parts, while losing no diagnostic fidelity on any failing run.**

The engine today pays **worst-case diagnostic cost on every run**. It performs
the expensive diagnostics — full-device read-backs — unconditionally, whether or
not there is anything to diagnose. The fix is not to delete diagnostics; it is to
make each one *conditional on a cheap oracle failing*.

Measured evidence, primitive costs, the validated connect model and the four
waste patterns are in
[`../notes/dev-test-sequence-cost-model.md`](../notes/dev-test-sequence-cost-model.md),
with the executable model beside it as `dev-test-sequence-cost-model.py`. This
seed carries only the design.

## The four rules

### R1 — Never read what you can verify

`verify_eprom` streams host→device and the firmware compares
([`memory.cpp:377-396`](../../firestarter/src/proms/memory.cpp#L377-L396)).
Same byte coverage as a read-back, **24% cheaper**, no host file I/O, and it
early-returns on the first mismatch — so failing runs get *faster*, not slower.

Any place the engine reads the whole device back to compare it against a buffer
it already holds is a verify. Two read-backs are excluded by design and
**must stay real reads**: the **fingerprint** read-back, which R2 governs — a
verify returns a bool and one mismatch address, while `classify_fingerprint`
needs the whole mismatch distribution (`ff_ratio` across the buffer,
bit-clustering across every offset), so converting it deletes the diagnostic
R2 exists to preserve — and the **SDP leg**, whose `_read_region` read-back
*is* the verdict. The seam is: verify decides; a read-back diagnoses; the
read-back only needs to run when verify says something is wrong.

### R2 — Diagnose on failure only

Gate the fingerprint read-back at
[`chip_test.py:3100`](../../firestarter_app/firestarter/chip_test.py#L3100) on
`not all(outcomes)`.

- Passing run: **zero** read-backs.
- Failing run: **byte-identical** fidelity to today.

The `ff_ratio` false-PASS check that motivated the unconditional form is
preserved for free — a write that reports OK without driving the bus is caught by
the verify step immediately following it in the same cycle. **This dependency was
asserted structurally** by Phase 175's sentinel
(`tests/test_derive_plan_structural_sentinel.py`) until 2026-09-14, when the three legs that
parsed `chip_test.py` with `ast` were removed by the source-introspection sweep (see
`.planning/notes/test-suite-source-introspection-removal.md`). The module's data-driven
verify-disposition coverage survives; the write-op selector claim is now **assumed, not
asserted**, and needs a behavioural test if it is to be relied on.

Note the pleasing asymmetry: because verify early-returns on first mismatch, the
runs that now pay for a read-back are exactly the runs whose verify was cheapest.

The predicate must consult the step's outcomes **across all cycles**, not
`not all(outcomes)` alone: under `_run_cycle_block` each cycle calls
`_dispatch_multi_run` with `runs=1`, so `outcomes` is a one-element list
describing the final cycle only. A cycle-1-fail / cycle-2-pass run must keep its
fingerprint. And a passing step still **reports** a fingerprint — synthesized
from `bad=0`, `total=region_length`, `ff_ratio: None` and classified `match`.
The read-back is what costs; the classification is free.

### R3 — Sample for a rate, sweep for a map

Read-repeatability is a **statistical** property, and so is `ff_ratio`. Both are
currently established by full-device sweeps.

**Measured and rejected (Phase 180, PRUNE-08).** The bit-structured sample this
rule proposed was priced against `EpromOperator._operation_context`
(`firestarter_app/firestarter/eprom_operations.py:515-550`), which connects on
entry and disconnects inside its own `finally` block: **every** `read_eprom`
call, sampled or full, pays one full connect. At the 64 KiB reference size the
sample was 10 separate `read_eprom` calls — 10 connects — against the 1 whole
`read_eprom` call the full sweep it would replace already costs. Ten connects
exceed one connect on both measured board classes (MEAS-01) at every
reference size this milestone tests, so the sample is dearer than the sweep
it would replace, not cheaper. The full argument, the per-board-class
measured figures and the size-axis finding are in
`.planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md`.
Nothing in this rule is a live instruction to build the sample, and the
design's operative detail — how its blocks were chosen and when it would have
escalated — is deliberately not restated here.

### R4 — One session per plan, not one per call

`run_plan` is the natural connection boundary; `EpromOperator.comm` is currently
torn down after every operator call. Counts are 22 for sst27sf512 and **32 for
at28c256**, whose six-op SDP leg alone costs 12 connects for ~3 KB of traffic.

Cheaper, strictly-additive sub-step available independently: fold `sample_vpp_mv`
and `sample_vpe_mv` into one monitor read (−2 connects per write step).

**Per-connect cost is now measured** (MEAS-01, `176-MEASUREMENT.md` §4a/§4b) —
the counts were already validated; the seconds are Uno-class median 2.518 s
and Leonardo-class median 2.607 s, per board class and never blended. What
that measurement decided about R1 through R3 is recorded in
`.planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md`.
R4 itself remains unscoped: whether leasing one validated link per plan is
worth building is still an open question this phase does not answer.

## Projected effect

From the model (`dev-test-sequence-cost-model.py`), `runs=2`:

| Chip | Class | Now | Proposed | Saved |
| --- | --- | --- | --- | --- |
| sst27sf512 | EEPROM full-device | 121.8s | 92.7s | **23.9%** |
| w27c512 | EEPROM full-device | 121.8s | 92.7s | **23.9%** |
| at28c256 | EEPROM + SDP leg | 61.3s | 47.3s | **23.0%** |
| m27c512 | UV, 256 B slot | 25.4s | 11.2s | **55.8%** |
| am27c020 | UV, 256 B slot | 99.6s | 40.4s | **59.5%** |
| w29c040 | flash4, 480 KiB | 769.3s | 537.5s | **30.1%** |

UV parts gain most because their write is 256 bytes — the run is almost entirely
preflight overhead. W29C040 saves nearly four minutes per run.

These figures exclude connection overhead entirely (unmeasured), so R4's
contribution is **not** in the table. They also assume the sampled preflight;
R1+R2 alone deliver roughly two thirds of each row.

## Per-class characteristics that must survive

The whole point of `dev test` is that the plan is derived per chip. Nothing here
may flatten that:

- **UV-EPROM** — keeps its full-device blank-check (blankness is an
  operator-actionable finding, and blank-check is the *cheapest* primitive per
  byte, so there is no reason to sample it), its top-down slot probe, and its
  tranche staging across cycles.
- **SRAM/FRAM** — keeps `CYCLE_PAYLOAD_ALTERNATE`; a volatile part has no blank
  state and needs the 0→1 transition the alternating payload forces.
- **flash4 / W29C040** — keeps the boot-block carve-out and its NA erase and
  blank-check.
- **AT28C256 / SDP leg** — untouched by R1 and R2. Its `_read_region` read-back
  is a verdict, not decoration, and its length gate and degeneracy gate depend on
  getting real bytes back. R4 is the only rule that helps here, and it helps a
  lot.
- **`--fast`** — unchanged in meaning. It stays the weaker single-run mode and
  must keep re-keying `dedup_fingerprint` through `repeat_policy_tag`.

## Sequencing note

R2 is small, self-contained and worth ~24% on its own — it is filed separately as
todo `2026-08-30-gate-fingerprint-readback-on-step-failure.md` so it can land
without waiting for the rest. R1 and R3 are engine changes with real test
surface. R4 is the largest structural change and the only one whose payoff is
currently unquantified.

## Explicitly out of scope

The write path's 2.2 KB/s — 65% of a full-device run — is the per-byte VPE settle
behaviour and is a firmware concern. No rule here touches it, and no figure above
claims it improves.

## Status: Phase 177 amendment

**Phase 177, 2026-09-05.** R1's final paragraph swept the fingerprint
read-back into the same rule that legitimately excludes the SDP leg, which
directly contradicted R2's own promise of byte-identical fidelity on a
failing run: `verify_eprom` returns a bool and one mismatch address, while
`classify_fingerprint` needs the whole mismatch distribution. Decision `D-1`
(`.planning/REQUIREMENTS.md`) settled the contradiction in R2's favour, and
this amendment replaces R1's paragraph **in place** rather than merely
annotating it, so the destructive reading is not outvoted but absent — a
planner reading only this seed can no longer regenerate it. R2 is corrected
so its own gate predicate consults outcomes across all cycles, not the final
cycle alone, and states that a passing step still reports a synthesized
`match` fingerprint. **Not touched by this amendment:** R3, R4, the
projected-effect table, the per-class characteristics section and the
out-of-scope section above.

## Status: Phase 180 amendment

**Phase 180, 2026-09-08.** R3's live paragraph instructed a future planner to
build the bit-structured sample described above. Phase 176 measured the
per-connect cost this rule needed and Phase 180 spent it: at the 64 KiB
reference size the sample costs 10 connects against the 1 the full sweep it
would replace already pays, on both measured board classes, at every
reference size this milestone tests — so the design this paragraph proposed
is dearer than what it would replace, not cheaper. Decision `D-01`
(`.planning/REQUIREMENTS.md`, PRUNE-08) and MEAS-01's measurement
(`176-MEASUREMENT.md` §4a/§4b) are the deciding authority; the full argument
is `.planning/phases/180-read-step-sampling-conditional-on-phase-176/180-PRUNE-08-CLOSURE.md`.
As with Phase 177's amendment to R1, this amendment replaces R3's paragraph
**in place** rather than merely annotating it, so the destructive reading is
not outvoted but absent — a planner reading only this seed can no longer
regenerate it. R4's opening sentence is also corrected in place: its claim
that the per-connect cost is unmeasured was true when written and is false
now that MEAS-01 exists, so it now cites the measurement instead. **R3 and
one sentence of R4 are now amended by this section. Not touched by this
amendment:** R1, R2, the projected-effect table, the per-class
characteristics section, the sequencing note and the out-of-scope section
above.

**Follow-through, gap closure.** 2026-09-08. `180-VERIFICATION.md` found that
the amendment above still left R3's escalate-on-divergence paragraph and its
stated-cost paragraph standing beneath the rejection verdict, both written in
the present tense as live design description — an escalation policy and a
stride rationale — with no historical framing. They are now removed outright
rather than annotated, and R3's verdict paragraph no longer enumerates which
blocks the sample would have used. An annotated retention — a "for the
historical record" banner in front of the same text — is the exact route
D-09 rejects: the destructive reading must be absent, not merely outvoted by
a paragraph beside it. This follow-through does not touch R1, R2, R4, the
projected-effect table, the per-class characteristics section, the sequencing note,
or the out-of-scope section, exactly as the amendment above it did not.
