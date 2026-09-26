---
title: A UV run with all slots exhausted flips build_db_diff's fourth ladder arm from community-fail to candidate-for-community-reported
date: 2026-09-08
priority: medium
blocked_by: nothing technical — the fix is a "no write actually ran" guard in build_db_diff, not a UV special case; filed as a residual by Phase 179 rather than fixed in-phase because the underlying hole is PRE-EXISTING and reachable today on any non-UV refused write, and Phase 179's scope was UV-01/02/03, not a general ladder-fold audit.
resolves_phase: 181
resolved: 2026-09-09 (plan 181-08's shared "did a write actually run" predicate, `_write_step_was_refused`)
status: resolved
---

# UV run with exhausted slots: the ladder flip (T-179-05)

## MEASURED, after Phase 179

After Phase 179's UV-02 adjudication change (the standalone `blank-check` step reads `SKIPPED`
instead of `BAD` on a non-blank UV part), a UV run whose part has **all slots already exhausted**
now reads:

```
blank-check   SKIPPED
write         SKIPPED
verify        SKIPPED
```

`build_db_diff`'s fourth arm (`diagnostic_report.py:403-405`) reads that step shape and proposes
`candidate for community-reported` — the same disposition a genuine, successfully-verified PASS
proposes. Before Phase 179, the same all-slots-exhausted run's `blank-check` step read `BAD`, which
landed the run on the ladder's `community-fail` arm instead.

## Why this is FORCED, not a Phase 179 authoring choice

UV-02's whole claim is that a non-blank finding must not dominate `overall_verdict` to `FAIL` — the
finding is adjudicated `SKIPPED` and the run is allowed to reach `PASS` on the write/verify legs that
actually ran. That adjudication is not scoped to "a slot is available"; it is scoped to "the part is
not blank," full stop. When no slot is available, the write and verify steps also read `SKIPPED`
(they never got a target to write to), and the ladder-fold logic that reads step verdicts to decide
`community-fail` vs. `candidate for community-reported` cannot distinguish "wrote nothing because
every step reported a genuine pass" from "wrote nothing because there was nothing left to write."
Any verdict that clears the FAIL fold for the non-blank finding (`SKIPPED`, and identically `NA`)
clears it here too — the flip is a structural consequence of UV-02, not an independent defect Phase
179 introduced through a specific implementation choice.

## The underlying hole is PRE-EXISTING

The real gap `build_db_diff`'s fourth arm has is that it proposes graduation to
`community-reported` off step *verdicts* without checking whether a write step's `SKIPPED` verdict
means "skipped because everything else already passed" or "skipped because nothing ran." That
ambiguity is not new to UV parts — it is reachable TODAY on any non-UV run where the write step is
refused before it starts (a resource that never became available, a locked-out region, any
`SKIP`-with-reason status that isn't "already covered"). Phase 179 did not introduce the hole; it
changed a UV-specific input that happens to walk into it via a path that previously read `BAD`
(chip-verdict FAIL) and now reads `SKIPPED` (a status that the ladder arm currently treats as
"nothing to report, no objection to graduating").

## Disposition

**Accepted for Phase 179.** No fix shipped in this phase — filed here instead. The honest fix, when
this is picked up, is a "no write actually ran" guard in `build_db_diff` (site:
`diagnostic_report.py:403-405`) that distinguishes a `SKIPPED` write step backed by a real pass
elsewhere in the run from a `SKIPPED` write step backed by nothing — not a UV-specific carve-out,
since the same guard closes the pre-existing non-UV gap too.

## RESOLUTION (2026-09-09)

Fixed by plan `181-08`. `chip_test._write_step_was_refused(results)` is exactly the "no write
actually ran" guard this todo asked for: true iff `results` carries a write-op (`OP_WRITE`/
`OP_WRITE_PARTIAL`) result whose verdict is `SKIPPED`, with `NA` deliberately excluded so an
unsupported-write part's disposition never moves. `build_db_diff`'s fourth arm now consults it as an
extra disqualifying condition, computed beside `run_errored`. A full 19-shape before/after census
found exactly 5 flips, all M27C512 shapes whose `write` step genuinely reads `SKIPPED` (every UV
slot exhausted) — moving from candidate/community-reported to no-change/"", closing this exact
defect. Not a UV special case, per this todo's own framing: the same guard closes the pre-existing
non-UV gap identically. Full census: `.planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-08-write-refused-predicate.txt`.
