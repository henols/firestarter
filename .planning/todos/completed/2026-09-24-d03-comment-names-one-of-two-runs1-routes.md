---
created: 2026-09-24
source: .planning/milestones/v1.41-phases/207.1-address-v1-41-tech-debt/207.1-REVIEW.md § WR-01 (filed at the v1.41 milestone close)
resolves_phase:
severity: minor
area: host app
---

# The D-03 comment names only one of the two routes to `runs=1`

The D-03 comment at `firestarter_app/firestarter/chip_test.py:2618-2641` says it states the
mechanism "precisely". It names one route by which a cycle-block run gets the `runs=1` tag: the
`hardware_refused` break after one cycle, with `_aggregate_cycle_results` returning that single
result.

There is a second route. `_aggregate_cycle_results` sets `run_count=len(ran)` (`:1389`), and `ran`
is filtered to `_RAN_VERDICTS = {OK, BAD, MARGINAL}` (`:3928`), which excludes SKIPPED. A cycle
whose `_run_step` raises `SerialError` or `HardwareOperationError` becomes SKIPPED with no
`error_code`. `hardware_refused` stays False, the loop does not break, and the second cycle runs.
`ran` then holds one element, so `repeat_policy_tag` stamps `runs=1`. An `EpromOperationError`
whose `error_code` is `None` takes the same route.

The comment also contradicts itself: "would re-key reports already filed" at `:2626`, and "re-key
none of them" at `:2640`.

**Comment only. The D-03 decision stands**, and "reverting this branch alone would re-key none of
them" is still true, because neither route depends on this `1`. The risk is a future reader who
fixes only the `hardware_refused` break and still sees a default-policy run re-keyed into the
`--fast` group through the SKIPPED route.

## Fix

Name both routes, and remove the contradiction:

```python
# ... On the cycle-block path this `1` equals the `runs` value
# passed in; the tag comes instead from `_aggregate_cycle_results`
# (`run_count=len(ran)`, SKIPPED excluded from `ran`) -- either the
# `hardware_refused` break leaving one cycle, or a cycle that raised
# here (SKIPPED, no error_code, no break) dropping out of `ran`
# while the other cycle ran.
```
