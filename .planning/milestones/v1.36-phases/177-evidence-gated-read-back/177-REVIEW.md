---
phase: 177-evidence-gated-read-back
reviewed: 2026-09-05T18:26:13Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/tests/fixtures/rekey_ledger.py
  - firestarter_app/tests/fixtures/report_shapes.py
  - firestarter_app/tests/fixtures/reports/at28c256-full-all-ok-sdp.json
  - firestarter_app/tests/fixtures/reports/prune03-synthesized-fingerprint-match.json
  - firestarter_app/tests/fixtures/reports/sst27sf512-full-all-ok.json
  - firestarter_app/tests/fixtures/reports/sst27sf512-six-step-readback-gated.json
  - firestarter_app/tests/fixtures/reports/sst27sf512-six-step.json
  - firestarter_app/tests/fixtures/reports/w27e257-full-all-ok.json
  - firestarter_app/tests/fixtures/shape_ids.json
  - firestarter_app/tests/test_blast_radius_invariance.py
  - firestarter_app/tests/test_chip_test.py
  - firestarter_app/tests/test_chip_test_cycle.py
  - firestarter_app/tests/test_readback_inventory.py
  - firestarter_app/tests/test_rekey_ledger.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 177: Code Review Report

**Reviewed:** 2026-09-05T18:26:13Z
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Reviewed `chip_test.py`'s `FP_MATCH` bucket, `_synthesized_match_fingerprint`, and the
`prior_cycles_failed` threading through `_run_step` → `_run_step_untimed` →
`_dispatch_step` → `_dispatch_multi_run`, plus the fixture/ledger/test surface that pins
the resulting hashes. Traced the four specific concerns called out for this phase:

1. **Classification order (`classify_fingerprint`)** — verified correct. `ff_ratio >=
   0.98` (blank/contact) is checked first, then address-line clustering, then `bad == 0`
   → `match`, then transport, then indeterminate. An all-0xFF bit-perfect compare still
   returns `blank/contact` (confirmed both by reading the code and by
   `test_classify_fingerprint_still_returns_blank_contact_for_an_all_ff_perfect_compare`).
   No re-key of the blank/contact population occurs.

2. **Evidence key parity (synthesized vs. measured)** — verified. The address-line
   clustering loop that would otherwise add `suspected_line`/`cluster_score` to
   `evidence` only executes `if bad and cmp_len > (1 << 8)`; since the `bad == 0` branch
   is only reached when `bad` is falsy, that loop never populates extra keys on the
   `match` path. Both `classify_fingerprint`'s `match` return and
   `_synthesized_match_fingerprint` emit exactly `{ff_ratio, repeat_divergent,
   first_offset, bit_clustering}`. No missing-key tell exists.

3. **Zero-length write regions** — verified. `_synthesized_match_fingerprint(0)` returns
   `total=0, bad=0, bad_pct=0.0` via hardcoded literals with no division performed, so no
   `ZeroDivisionError` is reachable. Confirmed by
   `test_a_zero_length_write_region_synthesizes_a_match_with_no_read`.

4. **`prior_cycles_failed` threading** — verified correct across all four hops (default
   `False`, threaded unchanged, never inverted). The `_RAN_VERDICTS` filter
   (`{OK, BAD, marginal}`) correctly excludes SKIPPED/NA prior cycles from counting as a
   failure, matching the docstring's claim and `test_a_bad_blank_check_does_not_force_a_
   read_back_on_a_passing_write` / `test_a_failing_first_cycle_keeps_the_fingerprint_
   read_back`.

Beyond those four points, tracing `_dispatch_multi_run`'s fingerprint gate down to where
`repeat_divergent` is actually computed surfaced a real defect in the `transport` bucket
that this phase's own docstring claims is preserved (see WR-01). It predates this phase
(introduced by the quick-task cycle refactor, `27021b3`), but this phase's diff touches
the exact same `_dispatch_multi_run` fingerprint site and neither notices nor repairs it,
and no test in the suite (added by this phase or otherwise) exercises the production
write/verify path reaching `transport`. WR-02 notes a related, narrower gap in the same
area. The remaining fixture/ledger/test files (`rekey_ledger.py`, `report_shapes.py`, the
JSON snapshots, `shape_ids.json`, and the four test modules) were cross-checked against
each other and against `chip_test.py` and are internally consistent; no defects found
there.

## Warnings

### WR-01: `classify_fingerprint`'s `transport` bucket is unreachable through the production write/verify path

**File:** `firestarter_app/firestarter/chip_test.py:3191-3197` (site), `firestarter_app/firestarter/chip_test.py:1588-1636` (`_run_cycle_block`), `firestarter_app/firestarter/chip_test.py:163-186` (docstring claim)

**Issue:** `classify_fingerprint`'s docstring states bucket 4 is `"transport -- scattered
+ non-repeatable across N>=2 runs (caller-supplied signal from run1-vs-run2
divergence)"`. The only caller that can set `repeat_divergent=True` for a write/verify
step is `_dispatch_multi_run`, which computes it as:

```python
diverged = len(set(outcomes)) != 1 if outcomes else False
```

`outcomes` is the list of per-run booleans collected by `_dispatch_multi_run`'s own
`for _ in range(runs): ...` loop. Since the repeat-cycle refactor (`27021b3`,
pre-dating this phase), every write/verify step that has a preceding write is always
routed through `_run_cycle_block`, which calls `_run_step(..., runs=1, ...)` once per
cycle. That means `_dispatch_multi_run` is now *always* invoked with `runs=1` for
`OP_WRITE`/`OP_WRITE_PARTIAL`/`OP_VERIFY` in production — `outcomes` always has exactly
one element, `len(set(outcomes))` is always `1`, and `diverged` is therefore always
`False`. `classify_fingerprint` is consequently never called with
`repeat_divergent=True` from this path, so a genuinely scattered, non-repeatable
mismatch (the uno328pb transport signature this bucket exists to name) always falls
through to `indeterminate` instead of `transport` in a real `dev test` run.

This phase (177) adds the `match` bucket and the `_synthesized_match_fingerprint`/
`prior_cycles_failed` gate directly around this same call site
(`chip_test.py:3181-3199`) without addressing or even flagging this — the cross-cycle
verdict-disagreement signal `_aggregate_cycle_results` computes (folding to `marginal`)
is a different, coarser signal than the byte-level `repeat_divergent` `classify_
fingerprint` expects, and nothing bridges the two. No test anywhere in the suite
(`grep -n "repeat_divergent"` across `tests/`) exercises the production `run_plan` →
`_dispatch_multi_run` path reaching `transport`; every exercise of that bucket calls
`classify_fingerprint` directly as a unit test.

**Fix:** Either (a) compute a genuine cross-cycle divergence signal in
`_run_cycle_block` — e.g. whether this step's *own* outcome disagreed with any prior
ran cycle's outcome for the same step — and thread it into `_dispatch_multi_run` the
same way `prior_cycles_failed` is threaded, using it (instead of the now-vacuous local
`diverged`) as `repeat_divergent`; or (b) if the design intent is that `transport` is
now only reachable through some other path (e.g. the SDP leg or the read step), update
`classify_fingerprint`'s docstring and the bucket-order comment to say so explicitly,
and add a regression test proving the intended reachable path still produces
`transport` end-to-end (not just via a direct unit call).

### WR-02: A hardware refusal on a non-final cycle silently forfeits the write/verify step's `Fingerprint` entirely

**File:** `firestarter_app/firestarter/chip_test.py:1622-1636` (`_run_cycle_block`), `firestarter_app/firestarter/chip_test.py:1590` (`final = cycle == cycles - 1`)

**Issue:** `collect_fingerprint` is only `True` on the last planned cycle
(`final = cycle == cycles - 1`). When an earlier cycle's write/verify call raises an
`EpromOperationError` with a non-`None` `error_code` (e.g. the VPP-out-of-range guard,
`0xA9`), `hardware_refused` is set and the cycle loop `break`s immediately after that
cycle finishes, so no later cycle — and in particular never the "final" one — ever
runs. `per_step[i]` for that step then holds exactly one entry (the failing, non-final
cycle's result), `_aggregate_cycle_results` takes the `len(results) == 1` short-circuit
and returns that cycle's `StepResult` verbatim, and since that cycle had
`collect_fingerprint=False`, `fingerprint` is `None` on the aggregated result. The step
correctly reports `BAD` with `error_code=0xA9`, but the diagnostic `Fingerprint` that
`classify_fingerprint` would have named (e.g. distinguishing a contact fault from a
genuine chip defect) is silently absent for the whole run, even though real device
state was read (or could have been) before the refusal broke the loop.

This predates phase 177 (the `final`-gated `collect_fingerprint`/`hardware_refused`
interaction is pre-existing from the same cycle refactor as WR-01), but it directly
adjoins the fingerprint-gating logic this phase modified, and existing tests
(`test_safe02_vpp_guard_refusal_is_a_finding_not_a_retry_multi_run`) only assert
`verdict`/`error_code`/call-count, never `fingerprint`, so this gap is untested.

**Fix:** When `hardware_refused` breaks the loop, treat the break as equivalent to
reaching the final cycle for fingerprint-collection purposes on the step that
triggered it — e.g. re-run the write/verify/erase step's fingerprint-collection branch
once more with `collect_fingerprint=True` before returning, or fall back to computing
the fingerprint from the last cycle's own read-back state so a hardware refusal doesn't
also erase the diagnostic evidence for it.

## Info

### IN-01: No integration test proves `classify_fingerprint`'s `transport` bucket is reachable from `run_plan`

**File:** `firestarter_app/tests/test_chip_test.py` (fingerprint-related tests, e.g. `test_fp_transport_scattered_repeatable` at line 239), `firestarter_app/tests/test_chip_test_cycle.py`

**Issue:** Every test that exercises the `transport` classification calls
`classify_fingerprint(...)` directly with a hand-supplied `repeat_divergent=True`. None
of them run `run_plan`/`_run_cycle_block` end-to-end and assert that a real disagreeing
write/verify sequence reaches `transport` through production code. This is exactly the
gap that let WR-01 go unnoticed through the cycle refactor and through this phase's own
changes to the same dispatch site.

**Fix:** Add a `test_chip_test_cycle.py`-style end-to-end test that drives a scattered,
non-repeatable mismatch pattern through `run_plan` (e.g. an operator double whose
region read-back differs between the cycle that failed and the final cycle) and
asserts the resulting `Fingerprint.classification` is `"transport"`, not
`"indeterminate"` — this would have caught WR-01 directly instead of only reaching it
by tracing the call chain.

---

_Reviewed: 2026-09-05T18:26:13Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
