---
created: 2026-09-20T00:00:00Z
title: CompareAccumulator.feed()'s post-offset empty check is unreachable
area: host
resolves_phase: null
source: .planning/milestones/v1.41-phases/202-one-comparison-engine-on-the-host/202-REVIEW.md § IN-01
files:

  - firestarter_app/firestarter/compare.py (CompareAccumulator.feed, the `if not offs:` branch after the per-offset comprehension)

completed: 2026-09-24
status: completed
---

## Problem

In `CompareAccumulator.feed()`:

```python
offs = [o for o in range(chunk_len) if expected[o] != actual[o]]
if not offs:
    self._close_open_range()
    return
```

This is reached only after the Tier-2 fast path (`if expected == actual: ... return`) has already
established `expected != actual` for the chunk. `feed()`'s docstring guarantees
`len(expected) == len(actual) == chunk_len`, and inequality over equal-length byte sequences means
at least one index differs — so `offs` is never empty here. The branch cannot run.

It is harmless: free at runtime, and it protects a documented invariant a future caller could
unknowingly relax. It is worth recording only because this module's own design principle is to keep
the divergence math to exactly one path with no redundant computation, and a reader checking that
claim will trip over this.

## Fix

Either remove the branch, or keep it and say in a comment that it is deliberate defensive
redundancy against a caller violating the equal-length contract. Silence is the one option that
costs the next reader time.

## Why it was not fixed in phase 202

Informational only — no behavior, no must-have, no requirement depends on it.
