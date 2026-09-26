# PRUNE-08's Closure

Phase 180, plan 180-01. The evidence and arithmetic behind PRUNE-08's close: the measured
per-connect cost Phase 176 recorded (MEAS-01), spent here against the connect count a bit-structured
read sample would actually pay.

## The verdict

**PRUNE-08 closes as measured, not worth doing** (D-01), taking roadmap success criterion 2.
Criterion 1 is not taken: `176-MEASUREMENT.md` §4a records the Uno-class connect cost at a median
2.518 s (remainder 0.018 s over a 2.500 s structural floor), and §4b records the Leonardo-class
connect cost at a median 2.607 s (remainder 0.107 s over the same 2.500 s floor) — an 0.089 s gap
between the two classes, which makes board class a non-discriminator for this decision. Per §4a/§4b's
own never-blend rule, these two figures are stated here per board class and never averaged into one
number.

`176-MEASUREMENT.md` §6 is the reason board class is a non-discriminator, and it is quoted rather than
extended: §6 **falsified** the stated Uno-dominance hypothesis (the Uno-class remainder, 0.018 s, is
*smaller* than the Leonardo-class remainder, 0.107 s, not larger) and explicitly attributes no
mechanism — it cannot distinguish "no bootloader wait occurred" from "a bootloader wait occurred and
was fully absorbed by the floor." This document does not claim to know why the two classes differ; it
only uses that they are close enough together (0.089 s apart, against floors of 2.5 s) that neither
board class changes today's verdict.

`176-MEASUREMENT.md` §7 is the licence to spend the measurement: it names PRUNE-08 as one of the two
downstream consumers and records that Phase 176 itself "records the measurement; it does not spend
it — no scoping decision for PRUNE-08 is made here." §7 also states that "both remainders are small
relative to the 2.5 s floor" — that remark is about the *remainders*, not the connect cost as a whole.
A sampler pays the *entire* 2.518 s / 2.607 s, floor included, once per block; nothing about the floor
being large is a reason to treat any individual connect as cheap.

## The connect arithmetic

The recomputable core. Every number below can be re-derived by a reader; none is asked to be taken on
faith.

**The 64 KiB reference block list, enumerated in full** — block 0, one 256 B block at each
power-of-two boundary strictly inside the device, and the top block:

```
0x0000 0x0100 0x0200 0x0400 0x0800 0x1000 0x2000 0x4000 0x8000 0xFF00
```

That is 10 entries. The derivation is `N = log2(size) - 6`: at the 64 KiB reference size,
`log2(65536) = 16`, so `N = 16 - 6 = 10`, matching the enumerated list exactly. Reading the seed's own
range notation (`1 << k` for `k in 8..log2(size)`) literally as an inclusive count of boundary values
yields 11, which contradicts the seed's own stated answer of "10 blocks / 2560 B" for a 64 KiB part —
the enumeration above is authoritative, the range notation is not.

Generalising the same enumeration to other device sizes:

| Size | `log2(size)` | N (`log2(size) - 6`) | Sample bytes (`N × 256`) |
|---|---|---|---|
| 2 KiB | 11 | 5 | 1280 |
| 32 KiB | 15 | 9 | 2304 |
| 64 KiB | 16 | 10 | 2560 |
| 128 KiB | 17 | 11 | 2816 |
| 256 KiB | 18 | 12 | 3072 |
| 512 KiB | 19 | 13 | 3328 |

**The three reference parts this milestone actually tests are all 64 KiB**, so all three land at
`N = 10`:

| Part | Size | N | `support_status` |
|---|---|---|---|
| SST27SF512 | 65536 B | 10 | `supported` |
| W27C512 | 65536 B | 10 | `supported` |
| M27C512 | 65536 B | 10 | `supported` |

**The structural premise the whole arithmetic rests on:** `EpromOperator._operation_context`
(`firestarter_app/firestarter/eprom_operations.py:515-550`) connects on entry — through
`_setup_operation` (`:531`, defined `:454`), which calls `SerialCommunicator.find_and_connect`
(`:499`) — and calls `_disconnect_programmer()` (`:552`) inside its own `finally` block (`:548`), so
every `read_eprom` call pays exactly one full connect. `firestarter_app/tests/test_readback_inventory.py`'s
`test_one_read_eprom_call_costs_exactly_one_connect` holds this structurally, by `ast`, and is proven
to redden against a planted second connect (`test_a_planted_second_operation_context_in_read_eprom_reddens_the_pin`).

**The load-bearing sentence:** replacing the read step's second full sweep (`_dispatch_read`,
`firestarter_app/firestarter/chip_test.py:2767`) with an N-block sample substitutes 10 whole
`read_eprom` calls for the 1 whole `read_eprom` call the sweep it replaces already costs — that is
**10 connects where the sweep it replaces costs 1**, a net plus-nine connects per read step, before a
single byte of the sample's 2560 B ever moves across the wire.

Stated in the measured unit per board class, and never blended: ten connects cost 25.18 s on the
measured Uno-class board (10 × 2.518 s) and 26.07 s on the measured Leonardo-class board
(10 × 2.607 s) — against the one connect the full read already pays.

This argument needs no modelled read rate, wire time, or per-operation overhead at all: even a badly
wrong estimate of how long the sample's 2560 B take to move across the wire leaves ten connects dearer
than one. No figure from `.planning/notes/dev-test-sequence-cost-model.md` is published here (D-04,
Ruling 3) — no read rate, no per-operation overhead, and the factor-of-two-and-a-half illustration
that depends on one is omitted entirely.

**The size-dependence, recorded without a modelled table (D-04, D-05).** N grows with `log2(size)`
while the full read's own wire cost grows linearly with size, so a crossover size exists above which a
sample's connect cost would fall below the full read's wire cost. That crossover lies above every
reference part this milestone tests. Of 746 database rows, 484 are ≤128 KiB, 148 are 256 KiB and 114
are ≥512 KiB; every row at 256 KiB and above is `supported`. This finding is recorded as evidence for
a possible future size-gated variant; it is **not** re-filed as a requirement, backlog item, or todo
(D-05) — the operator was offered exactly that and declined it.

**Criterion 4 is Not Applicable (D-10).** Its own text is conditioned — "If sampling ships,
block-wise `(offset, block)` comparison is used…" — and sampling does not ship under this verdict, so
its precondition is false. No hole-padded fixture or block-wise comparator is built to satisfy a
criterion whose precondition is false.

**How permanently this holds (D-08).** The entire verdict rests on today's one-connect-per-read
design. **R4-01** (`.planning/REQUIREMENTS.md` §Future Requirements — `EpromOperator` leasing one
validated link per plan) would invert the arithmetic completely: a single leased connection could
serve a whole plan, so N region reads would cost roughly one connect plus N small transfers instead of
N connects. This close is conditioned on R4-01 not having shipped; if it ships, this arithmetic must
be redone, not assumed to still hold.

**The primitive a future attempt would use (D-11).** `firestarter_app/firestarter/chip_test.py:2851`
(`_read_region`) already provides what a future size-gated or post-R4-01 sampler would need — an
absolute-offset slice off a hole-padded file, returning `b""` rather than raising on any failure — and
is also the choice that keeps the read-back census at exactly two `read_eprom` call sites, so a future
sampler routed through it would not redden `firestarter_app/tests/test_readback_inventory.py`. This is
a note, not a licence to implement.

## What is excluded, and why

The excluded thing, named rather than left implicit — as `177-READBACK-INVENTORY.md` names its row 6
rather than leaving its exclusion unstated: **the bit-structured sample described in seed R3**, one
256 B block at each device-size-scaled boundary plus block 0 and the top block. The reason is the
arithmetic above, restated once as the exclusion's ground: it costs 10 connects against the 1 connect
the full sweep it would replace already pays, on **both** measured board classes, at every reference
size this milestone tests.

The size axis, stated without a modelled number (D-04): N grows with the base-two logarithm of the
device size, while the full read's own wire cost grows linearly with size. A crossover size therefore
exists above which the sample's connect cost would fall below the full read's wire cost, and that
crossover lies above every reference part this milestone tests.

The corpus context, in the corrected form (C-1): of 746 database rows, 484 are at or below 128 KiB,
148 are 256 KiB and 114 are at or above 512 KiB, and every row at 256 KiB and above is `supported`.
Ten of the 746 rows overall are **not** `supported`, and all ten sit at or below 8 KiB — so the two
load-bearing buckets, 148 of 148 at 256 KiB and 114 of 114 at or above 512 KiB, survive intact. This
document does not claim all 746 rows are supported; it states the per-bucket counts that are true.

**The size-gated variant is recorded as evidence and declined (D-05).** The operator was offered this
finding as both a ship option and a re-file option — close now and ship a size-gated sampler for
≥512 KiB parts, or close now and re-file the size-gated variant as a future requirement — and declined
both. It is recorded here as evidence for a possible future attempt; it is deliberately **not** a new
requirement, backlog item, or todo.

## Criterion 4 — Not Applicable

Roadmap success criterion 4 reads: *"If sampling ships, block-wise `(offset, block)` comparison is
used, never a whole-file compare, proven by a test using a hole-padded region fixture that a
whole-file compare would misreport as a false divergence."* Its precondition is `If sampling ships`.
Under this verdict, sampling does not ship — PRUNE-08 closes as measured, not worth doing, taking
criterion 2 instead. The precondition is therefore false, and criterion 4 is **Not Applicable (D-10)**.

No hole-padded fixture and no block-wise comparator were built to satisfy this criterion. Building
either would misrepresent what happened: it would manufacture proof for a code path this phase does
not ship, dressing an untaken branch as taken. That is the same overstatement-of-evidence failure this
milestone's honesty constraint forbids elsewhere, applied to a test artifact instead of a claim.

**The primitive a future attempt would use, again as a forward note (D-11).** Should sampling ever
ship, `firestarter_app/firestarter/chip_test.py:2851` (`_read_region`) is the primitive it would use:
a region read whose result is sliced at the **absolute** offset, because a region read produces a
hole-padded file whose real bytes sit at offset `start` and never at offset 0 — slicing anywhere else
would silently read zero-padding. It returns empty bytes (`b""`) rather than raising on any failure.
Criterion 4's hole-padding hazard is therefore already solved in this primitive, so a future attempt
would inherit the fix rather than the bug. Routing a future sampler through `_read_region` is also
what would keep Phase 177's read-back census at exactly two `read_eprom` call sites. This is a note,
not a licence to implement.

## The standing this close is granted

`177-READBACK-INVENTORY.md` closes its own row-4/row-6 disposition with: *"PRUNE-04 therefore closes
as measured-empty, with the named-and-excluded reason recorded — the same standing this milestone
grants PRUNE-08 for closing as measured, not worth doing."* This document is that granted standing
being taken: a verdict (D-01), a recomputable arithmetic, a named-and-excluded design with its reason,
and a criterion given an explicit verdict rather than left silently unaddressed — the same form,
applied to PRUNE-08.

## What would invalidate this close

The entire verdict above is a consequence of one design fact, proven structurally and pinned by test:
**one connect per read**. `EpromOperator._operation_context` connects on entry and disconnects inside
its own `finally` block, so every `read_eprom` call — sampled or full — pays exactly one full connect.

**R4-01** (`.planning/REQUIREMENTS.md`, Future Requirements, line 122 — `EpromOperator` leasing one
validated link per plan rather than tearing `self.comm` down after every call) is the specific change
that would invert this arithmetic completely (D-08): a single leased connection could serve a whole
plan, so N region reads would then cost roughly one connect plus N small transfers, not N connects.
This is stated as an honest condition on the close, not a deferral — no new requirement is filed here,
and R4-01 is neither scoped nor implemented by this phase.

The gates that would redden if the read step's verdict source or its one-connect premise moved are
named here, by function and module, because a gate cannot detect a design change that has not
happened yet — which is precisely why R4-01 is stated above as a condition rather than as a test:
- `firestarter_app/tests/test_readback_inventory.py::test_read_verdict_expression_reads_only_the_last_full_read_result` (D-06 leg 3, structural)
- `firestarter_app/tests/test_chip_test.py::test_read_step_last_run_failure_yields_bad` (D-06 leg 1, behavioural)
- `firestarter_app/tests/test_chip_test.py::test_read_step_first_run_failure_with_passing_last_run_yields_ok` (D-06 leg 2, behavioural)
- `firestarter_app/tests/test_readback_inventory.py::test_one_read_eprom_call_costs_exactly_one_connect` (Ruling 1 / D-02, structural, the one-connect pin)
