---
created: 2026-08-17T21:40:00Z
title: Phase 130 record gate degrades superlinearly on STATE.md's single-line last_activity_desc
area: tooling
files:
  - .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py
  - .planning/STATE.md (frontmatter field `last_activity_desc`, line 11)
---

## Problem

`check_record_corrections.py` is a required-green gate for every closing phase. Its runtime has
gone from a few seconds to **over two minutes**, and the cause is not the gate — it is the shape of
one of its scan targets.

`.planning/STATE.md` keeps `last_activity_desc` as a **single physical line**. Every plan appends
its record to that one line. Measured across Phase 146's execution:

| commit | plan | line 11 length (chars) |
|---|---|---|
| `d2c212f1` | 146 planning complete | 6,551 |
| `083e4e5f` | 146-03 | 13,619 |
| `0accb44e` | 146-04 | 19,393 |
| `9b93a339` | 146-05 | 26,423 |
| `84c70ec3` | 146-06 | 31,243 |
| `825ead7c` | 146-07 | 35,600 |
| `d7ae43e8` | 146-08 | 42,227 |
| `70671033` | 146-09 | 48,335 |
| `982982dd` | 146-10 | 51,725 |

Growth is roughly linear at **+5,000 chars per plan**. Gate runtime measured at that last value:
**rc=0 in 130 s** (also observed at 114 s and 127 s in plan 146-11's runs), against a few seconds
early in the phase. The tally is unaffected — `{'block': 23, 'line-label': 4, 'inline-history': 6,
'inline-allow': 10, 'superseded': 12}` — so this is cost, not correctness.

## Why it matters more than it looks

**A short `timeout` now produces `rc=124`, which reads exactly like a RED.** This already happened
once during Phase 146 orchestration: a 100 s allowance returned 124 and was briefly misread as a
gate failure. Any plan that wraps this gate in a 60 s or 100 s timeout will report a false RED, and
the natural next move — "investigate why the record gate broke" — burns a whole debugging cycle on
a gate that is passing.

Phase 146's executors were each given the ≥300 s allowance explicitly. That mitigation does not
survive into the next phase unless it is written down somewhere the next planner reads.

## Candidate fixes, in preference order

1. **Stop growing one line.** Give `last_activity_desc` a folded/block scalar, or move the
   per-plan `PRIOR (...)` history out of frontmatter into a body section. The field is already
   append-only history; frontmatter is the wrong home for kilobytes of it. Note that `phase.complete`
   and the `state.*` writers are recorded as destructive against this file, so any restructuring is a
   hand edit with a snapshot-and-diff, not a verb call.
2. **Make the gate's own regexes line-length-insensitive** — profile which pattern dominates before
   touching any of them, since the pattern table is deliberately transcribed-unchanged across
   phases and loosening one silently weakens a real check.
3. **At minimum, document the ≥300 s allowance** in the gate's own module docstring, so the next
   caller sees it without having to rediscover the 124.

## Not resolved by Phase 146

Phase 146 is a documentation-and-closure phase whose D-06 forbids behaviour changes, and the gate
is a live target of its own record checks. Deliberately left as a finding rather than absorbed.

---

## UPDATE 2026-08-18 — largely resolved by Phase 146 plan 146-13

Candidate fix 1 above ("stop growing one line") was effectively applied by `146-13` when it
restructured `last_activity_desc` and moved the per-plan `PRIOR (...)` history into the body.

Measured before and after, same gate, same tally:

| STATE.md line 11 | gate runtime |
|---|---|
| 51,725 chars | **130 s** |
| 2,079 chars | **23 s** |

Tally unchanged at `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10,
'superseded': 12}` across both, confirming this was always cost and never correctness.

**What remains worth doing**, so this does not simply regrow:

1. The field is still a single line and still append-only, so the same drift will recur over the next
   milestone unless the convention changes. Consider capping it, or making the body section the
   canonical home and the frontmatter field a one-line pointer.
2. Candidate fix 3 is still undone and is cheap: document the allowance in
   `check_record_corrections.py`'s module docstring. At 2,079 chars a 60 s timeout is now ample, which
   is exactly when the next caller will hardcode a short one and get bitten after the field regrows.
3. Candidate fix 2 (profiling the dominating pattern) remains untouched and is now lower priority.
