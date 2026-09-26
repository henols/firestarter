# Plan 138-02 — PREP-04: Live Pulse-Width Distribution (verbatim)

The script `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` re-derives,
this milestone, the live per-protocol `pulse_duration` distribution for algorithms `0x07` /
`0x08` / `0x0B` from the shipped `chip_database.json`, importing (never reimplementing) the
production `_parse_pulse_duration` parser, and proves its own capacity to **fail** — for an
attributable reason — before any of its passing output is trusted. This is C2's evidence
("pulse width is DATA, not a per-protocol constant"), and Phase 139 quotes the output below
verbatim into a public GitHub comment on gh#15.

Three runs are recorded, in this order:

1. **Run 1** — the non-vacuity proof: a deliberately-planted, single-protocol synthetic
   database designed to trip one specific assertion. The script is expected to, and does,
   **FAIL**.
2. **Run 2** — the default invocation, no environment override, against whatever
   `chip_database.json` is on disk in the `firestarter_app` worktree right now.
3. **Run 3** — `DB_REF=origin/beta`, proving the figure is a property of the shipped
   database on the remote `beta` branch, independent of whatever happens to be checked out
   locally.

## Run 1 — the non-vacuity proof (planted failure)

A gate that has only ever passed is untrusted. Before this script's `RESULT: PASS` was relied
on for Runs 2 and 3 below, it was observed to **FAIL**, for an attributable reason, against a
deliberately-broken synthetic database. The input lived only in the session scratchpad
directory — never inside `firestarter`, never inside `firestarter_app`, never inside
`.planning/` — and was deleted immediately after this run; it was **never committed**. Its
exact content (reproduced here so the exercise itself stays re-creatable even though the file
is gone) was a single-manufacturer, two-chip database in which protocol `0x07` carries exactly
one distinct parsed value:

```json
{"SYNTH":[{"part_number":"S1","programming":{"algorithm":7,"pulse_duration":"100 us"}},{"part_number":"S2","programming":{"algorithm":7,"pulse_duration":"100 us"}}]}
```

This was designed to trip assertion 3 (C2 testability) — and nothing else:

```
$ DB_PATH=/tmp/claude-1000/-workspaces/35e45717-6088-4570-9960-5f23ebe48324/scratchpad/138-02-planted-db.json python3 /workspaces/.planning/phases/138-preconditions-baseline/138-pulse-distribution.py
==============================================================================
Phase 138 Plan 02 -- PREP-04: live per-protocol pulse-width distribution
(0x07 / 0x08 / 0x0B), re-derived this milestone from the shipped
chip_database.json -- C2's committed evidence for the gh#15 correction.
==============================================================================

LAYER: chip_database.json carries `pulse_duration` as a STRING, e.g.
"100 us". firestarter/database.py:128 (`_parse_pulse_duration`) converts
that string into the integer-microsecond wire field `pulse-delay` that is
actually sent to the firmware. REQUIREMENTS.md's wording (`pulse_duration`)
and PROJECT.md's wording (`pulse_delay`) are both correct at different layers
-- the database layer and the wire layer, respectively -- and need no
reconciliation.

Protocol 0x07 (n = 2):
  histogram (parsed us x count, descending by count): 100us x2
  modal value: 100us, count 2, share 100.0% of n=2
  distinct parsed values: 1

Protocol 0x08 (n = 0):
  histogram (parsed us x count, descending by count): (no numeric values recorded)
  modal value: UNDEFINED (no numeric values recorded for this protocol)
  distinct parsed values: 0

Protocol 0x0B (n = 0):
  histogram (parsed us x count, descending by count): (no numeric values recorded)
  modal value: UNDEFINED (no numeric values recorded for this protocol)
  distinct parsed values: 0

Bucket table (buckets from the RAW string, never the parsed int -- D-11.
All six kinds are named below even where they measure zero):
  bucket                    0x07    0x08    0x0B
  ----------------------------------------------
  absent                       0       0       0
  non-string                   0       0       0
  empty                        0       0       0
  algorithm-controlled         0       0       0
  unparseable                  0       0       0
  explicit-zero                0       0       0

Whole-database partition: 2 chips on {0x07,0x08,0x0B} + 0 chips on every other protocol = 2 total chips scanned
  crossover (target-protocol id found inside the 'other' bucket): 0
  crossover (entry misfiled into the wrong target bucket): 0

Resolved parser module (firestarter.database.__file__): /workspaces/firestarter_app/firestarter/database.py
Database read from: DB_PATH=/tmp/claude-1000/-workspaces/35e45717-6088-4570-9960-5f23ebe48324/scratchpad/138-02-planted-db.json
Database blob SHA (git blob object id, 40 hex chars): f84ace426ed76399c2368b1472995997bc95f126

VIOLATIONS: 1
  - assertion 3 (C2 testability) protocol 0x07: only 1 distinct parsed value among 2 chip(s) -- this FALSIFIES C2 ('pulse width is DATA, not a per-protocol constant') for this protocol
RESULT: FAIL
```

**Exit code: 1.** The violation list names **exactly one** assertion — assertion 3 — and
nothing else. Protocols `0x08` and `0x0B` correctly show `n = 0` chips in this minimal fixture
and are **not** flagged as violations (a protocol with zero chips in the input cannot falsify a
claim about the *distribution* of its pulse values — that is a distinct, and non-triggered,
degenerate case the script also checks for). After this run, the planted file was deleted from
the scratchpad, and both `git -C /workspaces status --porcelain` and
`git -C /workspaces/firestarter_app status --porcelain` were confirmed to carry no new entries
versus their state immediately before this exercise began — this run touched neither repository.

## Run 2 — default invocation (worktree)

```
$ cd /workspaces && python3 .planning/phases/138-preconditions-baseline/138-pulse-distribution.py
==============================================================================
Phase 138 Plan 02 -- PREP-04: live per-protocol pulse-width distribution
(0x07 / 0x08 / 0x0B), re-derived this milestone from the shipped
chip_database.json -- C2's committed evidence for the gh#15 correction.
==============================================================================

LAYER: chip_database.json carries `pulse_duration` as a STRING, e.g.
"100 us". firestarter/database.py:128 (`_parse_pulse_duration`) converts
that string into the integer-microsecond wire field `pulse-delay` that is
actually sent to the firmware. REQUIREMENTS.md's wording (`pulse_duration`)
and PROJECT.md's wording (`pulse_delay`) are both correct at different layers
-- the database layer and the wire layer, respectively -- and need no
reconciliation.

Protocol 0x07 (n = 170):
  histogram (parsed us x count, descending by count): 100us x113, 200us x27, 1000us x22, 50us x4, 500us x4
  modal value: 100us, count 113, share 66.5% of n=170
  distinct parsed values: 5

Protocol 0x08 (n = 127):
  histogram (parsed us x count, descending by count): 100us x104, 50us x11, 10us x7, 200us x2, 1000us x2, 20us x1
  modal value: 100us, count 104, share 81.9% of n=127
  distinct parsed values: 6

Protocol 0x0B (n = 32):
  histogram (parsed us x count, descending by count): 500us x21, 1000us x6, 200us x5
  modal value: 500us, count 21, share 65.6% of n=32
  distinct parsed values: 3

Bucket table (buckets from the RAW string, never the parsed int -- D-11.
All six kinds are named below even where they measure zero):
  bucket                    0x07    0x08    0x0B
  ----------------------------------------------
  absent                       0       0       0
  non-string                   0       0       0
  empty                        0       0       0
  algorithm-controlled         0       0       0
  unparseable                  0       0       0
  explicit-zero                0       0       0

Whole-database partition: 329 chips on {0x07,0x08,0x0B} + 417 chips on every other protocol = 746 total chips scanned
  crossover (target-protocol id found inside the 'other' bucket): 0
  crossover (entry misfiled into the wrong target bucket): 0

Resolved parser module (firestarter.database.__file__): /workspaces/firestarter_app/firestarter/database.py
Database read from: default path /workspaces/firestarter_app/firestarter/data/chip_database.json
Database blob SHA (git blob object id, 40 hex chars): ebd1eaac01698f64dc0861f8478b8931493d3bab

VIOLATIONS: 0
RESULT: PASS
```

**Provenance note (honest, per this plan's constraints):** this plan's `commits_land_in`
frontmatter forbids switching `firestarter_app`'s checkout, so "default invocation" measured
whatever tree happened to be on disk at run time. At the moment of this run, that tree was
checked out on branch **`fix/dev-test-blank-check-after-erase`** at HEAD
**`7fe8dea9143a6ac4da3d656d3e4d5d538e14a175`** — a v1.31-milestone branch ref
(`gsd/v1.31-27c-programming-algorithm-fidelity`) exists in this repo from Plan 138-01, but is
**not** checked out; Plan 138-04 is the one that switches it. This does not weaken the figure
above: "Independent confirmation — database blob identity" below proves the exact
`chip_database.json` blob measured here is byte-identical to `origin/beta` and to the v1.30
branch tip regardless of which of the three is actually checked out.

## Run 3 — `DB_REF=origin/beta`

```
$ cd /workspaces && DB_REF=origin/beta python3 .planning/phases/138-preconditions-baseline/138-pulse-distribution.py
==============================================================================
Phase 138 Plan 02 -- PREP-04: live per-protocol pulse-width distribution
(0x07 / 0x08 / 0x0B), re-derived this milestone from the shipped
chip_database.json -- C2's committed evidence for the gh#15 correction.
==============================================================================

LAYER: chip_database.json carries `pulse_duration` as a STRING, e.g.
"100 us". firestarter/database.py:128 (`_parse_pulse_duration`) converts
that string into the integer-microsecond wire field `pulse-delay` that is
actually sent to the firmware. REQUIREMENTS.md's wording (`pulse_duration`)
and PROJECT.md's wording (`pulse_delay`) are both correct at different layers
-- the database layer and the wire layer, respectively -- and need no
reconciliation.

Protocol 0x07 (n = 170):
  histogram (parsed us x count, descending by count): 100us x113, 200us x27, 1000us x22, 50us x4, 500us x4
  modal value: 100us, count 113, share 66.5% of n=170
  distinct parsed values: 5

Protocol 0x08 (n = 127):
  histogram (parsed us x count, descending by count): 100us x104, 50us x11, 10us x7, 200us x2, 1000us x2, 20us x1
  modal value: 100us, count 104, share 81.9% of n=127
  distinct parsed values: 6

Protocol 0x0B (n = 32):
  histogram (parsed us x count, descending by count): 500us x21, 1000us x6, 200us x5
  modal value: 500us, count 21, share 65.6% of n=32
  distinct parsed values: 3

Bucket table (buckets from the RAW string, never the parsed int -- D-11.
All six kinds are named below even where they measure zero):
  bucket                    0x07    0x08    0x0B
  ----------------------------------------------
  absent                       0       0       0
  non-string                   0       0       0
  empty                        0       0       0
  algorithm-controlled         0       0       0
  unparseable                  0       0       0
  explicit-zero                0       0       0

Whole-database partition: 329 chips on {0x07,0x08,0x0B} + 417 chips on every other protocol = 746 total chips scanned
  crossover (target-protocol id found inside the 'other' bucket): 0
  crossover (entry misfiled into the wrong target bucket): 0

Resolved parser module (firestarter.database.__file__): /workspaces/firestarter_app/firestarter/database.py
Database read from: DB_REF=origin/beta (git -C /workspaces/firestarter_app show origin/beta:firestarter/data/chip_database.json)
Database blob SHA (git blob object id, 40 hex chars): ebd1eaac01698f64dc0861f8478b8931493d3bab

VIOLATIONS: 0
RESULT: PASS
```

**Runs 2 and 3 agree exactly.** The only line that differs between their two verbatim outputs
is `Database read from:` (the provenance line, which necessarily differs because the two runs
use different seams) — every count, every histogram, every modal value, every share, the bucket
table, the whole-database partition, and the blob SHA are byte-for-byte identical. Diffing the
two captured outputs confirms exactly one differing line, and it is that provenance line.

## Reconciliation

Every headline figure above was **re-measured live this session**, not restated from either
independent source, and is now compared against both:

- Protocol **0x07**: **n = 170**, histogram `100 us ×113, 200×27, 1000×22, 500×4, 50×4`. The
  seed's C2 table (`.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md`, `### C2 —
  Pulse width is DATA, not a per-protocol constant`) records, verbatim: `100 µs ×113, 200 ×27,
  1000 ×22, 500 ×4, 50 ×4`. **Every count reproduced exactly** — zero divergence.
  `138-RESEARCH.md`'s "Pulse Distribution (PREP-04)" section records the identical figure.
  **Zero divergence from either source.**
- Protocol **0x08**: **n = 127**, histogram `100 us ×104, 50×11, 10×7, 200×2, 1000×2, 20×1`.
  The seed records, verbatim: `100 µs ×104, 50 ×11, 10 ×7, 200 ×2, 1000 ×2, 20 ×1`. **Every
  count reproduced exactly.** `138-RESEARCH.md` records the identical figure. **Zero divergence
  from either source.**
- Protocol **0x0B**: **n = 32**, histogram `500 us ×21, 1000×6, 200×5`. The seed records,
  verbatim: `500 µs ×21, 1000 ×6, 200 ×5`. **Every count reproduced exactly.**
  `138-RESEARCH.md` records the identical figure. **Zero divergence from either source.**
- Whole-database partition: **329** chips on `{0x07,0x08,0x0B}` + **417** chips on every other
  protocol = **746** total chips scanned (**329 + 417 = 746**, verifiable by arithmetic on this
  page). `138-RESEARCH.md` records the identical partition (`329 + 417 = 746 exactly, with zero
  crossover in either direction`) and the identical whole-database raw histogram. This run's own
  two crossover checks (a target-protocol id leaking into the "other" bucket; an entry misfiled
  into the wrong target bucket) both independently measured **0**, matching.
- All six D-11 buckets (`absent`, `non-string`, `empty`, `algorithm-controlled`, `unparseable`,
  `explicit-zero`) measured **0** for all three protocols in Runs 2 and 3, on the real shipped
  database. `138-RESEARCH.md` records the same finding for the five buckets it names ("All four
  buckets are empty, and that is the finding — not an omission"). This run's own denominator
  check (assertion 1) confirms independently that the sum of all six bucket counts plus every
  histogram count equals the scanned `n` for each protocol exactly — no chip dropped.

**No figure diverged from either independent source in this run.** Had one diverged, this
section would state both values side by side and record the disagreement as a finding — per
this milestone's own D-06 rule, the measured number wins and neither value is quietly dropped.
That rule did not need to be exercised here.

## Independent confirmation — database blob identity

The `chip_database.json` blob SHA is confirmed identical across every ref this plan cites, with
the verbatim commands that produced each value:

```
$ git -C /workspaces/firestarter_app branch --show-current && git -C /workspaces/firestarter_app rev-parse HEAD
fix/dev-test-blank-check-after-erase
7fe8dea9143a6ac4da3d656d3e4d5d538e14a175

$ git -C /workspaces/firestarter_app hash-object firestarter/data/chip_database.json
ebd1eaac01698f64dc0861f8478b8931493d3bab

$ git -C /workspaces/firestarter_app rev-parse origin/beta:firestarter/data/chip_database.json
ebd1eaac01698f64dc0861f8478b8931493d3bab

$ git -C /workspaces/firestarter_app rev-parse gsd/v1.30-sdp-surface-retirement:firestarter/data/chip_database.json
ebd1eaac01698f64dc0861f8478b8931493d3bab

$ git -C /workspaces/firestarter_app rev-parse origin/beta
4d18b645ab18a2d2465f0f623062e9249eb24132
```

All three resolve to the **same 40-character blob SHA, `ebd1eaac01698f64dc0861f8478b8931493d3bab`**:
the worktree (currently checked out on `fix/dev-test-blank-check-after-erase` @
`7fe8dea9143a6ac4da3d656d3e4d5d538e14a175`, per the provenance note above), the live
`origin/beta` tip (`4d18b645ab18a2d2465f0f623062e9249eb24132`, i.e. `3.0.0b20`), and the v1.30
branch tip `gsd/v1.30-sdp-surface-retirement`. **This is exactly what makes PREP-04 independent
of PREP-01 and PREP-02**: the datum this script measures is unaffected by which of these three
trees `firestarter_app` is forked from, merged into, or currently checked out on, so this
plan's figures never had to wait on either branch decision.

## Independent confirmation — the counted layer

Restating D-11's layer distinction in the body, not a footnote: `chip_database.json` stores
`pulse_duration` as a **string**, e.g. `"100 us"`. `_parse_pulse_duration`, at
`firestarter_app/firestarter/database.py:128`, converts that string into the integer-microsecond
wire field `pulse-delay` that is actually transmitted to the firmware (`database.py:417` builds
`"pulse-delay": _parse_pulse_duration(programming.get("pulse_duration", ""))`, forwarded to the
wire at `database.py:555`). `REQUIREMENTS.md`'s PREP-04 wording says `pulse_duration`;
`PROJECT.md`'s C2 restatement says `pulse_delay`. **Both are correct at different layers** — the
database layer and the wire layer, respectively — and neither needs correcting to match the
other.

The C1 adjudication that Phase 139's ISSUE-01 will cite for the companion `0x0B` pulse-value
correction lives at `firestarter_app/doc/infoic-field-dictionary.md`, in the `pulse_delay`
section (its `### pulse_delay (uint32 hex) — CONFIRMED` heading, lines 196-217). Its table
records:

| Chip | protocol_id | Raw hex | Correct µs | build_db.py output (BUG-2) |
|------|-------------|---------|------------|------------------------------|
| AM2716 | `0x0B` | `0x1F4` | 500 µs | 50000 µs (×100 wrong) |

and its **BUG-2 (DEC-03)** note names the ×100 `interpret_timing()` multiplier — already removed
from `build_db.py` by Phase 57 — as the root cause of gh#15's incorrect `pulse: 50000 us` figure.
This is a different correction (a wrong constant gh#15 asserts for `0x0B`) from the one this
artifact measures (that the pulse is data, not a constant, for any of the three protocols) —
they are cited together here because Phase 139's ISSUE-01 posts both in the same comment.

## What this artifact is — and is not

**This artifact is** the measured input Phase 139 quotes verbatim into a public GitHub comment
on gh#15: a reproducible, self-checking re-derivation of the live per-protocol pulse-width
distribution, proven capable of failing before its passing runs were trusted.

**This artifact is not:**

- A claim about what any protocol's pulse width **should** be. It measures what the shipped
  database **contains**, not what a datasheet prescribes.
- A datasheet-conformance claim of any kind. No datasheet was consulted to produce these
  figures; they come exclusively from `chip_database.json` via the production parser.
- A statement that PREP-01 or PREP-02 are resolved, or that this plan depended on their
  resolution — see "Independent confirmation — database blob identity" above.
- A tick of PREP-04 in `REQUIREMENTS.md` — that happens in Plan 138-07, once this phase's
  baseline is fully assembled from every plan's evidence.

---

*Phase: 138-preconditions-baseline — Plan 02*
*Recorded: 2026-08-08, from live runs against the `firestarter_app` submodule exactly as
checked out this session (see the provenance note under Run 2).*
