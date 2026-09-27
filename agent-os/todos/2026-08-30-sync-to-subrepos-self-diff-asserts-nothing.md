---
created: 2026-08-30T11:20:00Z
title: sync_to_subrepos.sh runs `diff -q $X $X` twice — two verifications that assert nothing
area: tooling
found_in_phase: 167
files:
  - tools/catalog/sync_to_subrepos.sh (lines 84-86 and 97-99 — the two self-comparisons)
  - tools/catalog/sync_to_subrepos.sh (lines 65-70 — the one CORRECT two-distinct-operand assertion, for reference)
---

## Problem

`tools/catalog/sync_to_subrepos.sh` contains two verification blocks that compare a path to
**itself**:

- line 84: `if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then`
  followed by `echo "  OK: firestarter/include/messages.h regenerated."`
- line 97: the same shape for `"$FA_ROOT/firestarter/messages.py"`

Both comparisons are tautologically true. Each prints a success line for a property it never
tested, and neither has a reachable failure branch — there is no `else`, so nothing can ever be
observed red. This sits in the repository's only sync tooling, immediately after the `codegen.py`
invocations whose output it purports to verify.

Same defect class as `.github/workflows/catalog-sync-check.yml` (5 runs, 5 failures, never once
asserted the property it existed to assert) and as the ~20 v1.34 rig defects that were all
fixture-selftest-green and all failed on first hardware contact.

Line numbers re-verified 2026-08-30 while planning Phase 167. `167-RESEARCH.md` cites these as
`:88-90` / `:100-102`; `167-PATTERNS.md`'s `:84-86` / `:97-99` are the correct ones.

## Solution

Out of scope for v1.35 — Phase 167 was told to extract the transferable structure from this file
without carrying the defect, not to fix the file. Candidate fix, whenever it is picked up:

1. Regenerate into a temporary path, then `diff` the committed artifact against that temp copy —
   two traceably distinct operands.
2. Add the missing `else` branch: `echo "ERROR: ..." >&2` and a non-zero exit, so the failure
   branch exists and can be observed.
3. Prove it: mutate the committed `messages.h`, run the script, confirm it goes red, restore.
   A verification whose red state has never been seen proves nothing.

The correct pattern already exists in the same file at lines 65-70 (the cross-sub-repo
byte-identity assertion) — copy that shape.

Reference implementation of the discipline: `tools/wiki/selftest.sh` and its evidence table,
authored in Phase 167, where every case asserts a control leg and a mutated leg.
