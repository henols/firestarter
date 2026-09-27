---
created: 2026-09-20
source: 200-REVIEW.md CR-01 (filed at the v1.40 milestone close, not during Phase 200)
resolves_phase:
severity: critical
---

# `programming_vcc_over_rail_mv` fails closed on a non-dict `electrical`

`firestarter_app/firestarter/eprom_info.py:63-71` — the function's own docstring states it "must
fail open" and enumerates the malformed shapes it defends against. Its `except` tuple is
`(TypeError, ValueError)`, which does not cover `AttributeError`, so a present-but-non-dict
`electrical` value raises instead of returning `None`:

```python
programming_vcc_over_rail_mv({"electrical": "bogus"})   # AttributeError, not None
programming_vcc_over_rail_mv({"electrical": 123})       # AttributeError, not None
programming_vcc_over_rail_mv({"electrical": [1, 2, 3]}) # AttributeError, not None
```

**Why it was not fixed in Phase 200.** No must-have in any of the three plans enumerates a
present-but-non-dict `electrical` — 200-01's D-06 truth and 200-03's fail-open matrix both list
five malformed `vdd_mv` shapes plus an absent key and a `None` record, and every one of those
returns `None` correctly. `200-VERIFICATION.md` judged it real but not a phase blocker and
explicitly recommended filing it as a follow-up. That filing is this file; it did not happen at the
time.

**Why it is narrow today.** `firestarter/database.py:356` does `electrical = ic.get("electrical",
{})` then unconditionally `electrical.get("pin_count")` one call earlier in the same request, so a
malformed `electrical` already raises `AttributeError` in `_map_data` before this predicate is
reached via `info`. The live 746-row shipped database has zero rows in any fail-open state.

**Why it is still worth fixing.** `programming_vcc_over_rail_mv` is a public, standalone, directly
tested predicate — `test_programming_vcc_census.py` calls it with no `_map_data` in the path — and
the operator-supplied `~/.firestarter/database.json` override that `EpromDatabase` merges over the
packaged database is exactly the source of a malformed shape. A docstring that promises fail-open
without carving out this case is false as written.

Also fix `200-REVIEW.md` WR-01 in the same change: the fail-open test's name overstates its
coverage, since it never exercises a non-dict `electrical`.

Suggested fix: add `AttributeError` to the except tuple, or validate `isinstance(electrical, dict)`
explicitly, and add the three cases above to the fail-open test. Two-line change, obvious test.
