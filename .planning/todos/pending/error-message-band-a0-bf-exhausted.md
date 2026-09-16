---
created: 2026-09-15T00:00:00Z
title: "The ERROR message band 0xA0-0xBF is now fully spent -- the next ERROR id forces a decision"
area: both
resolves_phase: unassigned
files:
  - tools/catalog/messages.toml
  - tools/catalog/codegen.py
  - firestarter_app/tests/test_protection_status_catalog.py
---

## Problem

`tools/catalog/messages.toml`'s `ERROR` severity band occupies ids `0xA0` through `0xBF` — 32 ids.
Before Phase 194, 31 of the 32 were spent and `0xBF` was the band's single free id. Phase 194
(194-01) spent `0xBF` deliberately on `MSG_ERR_FL4_PAGE_SIZE`, the fail-closed refusal for a
protocol `0x05` write with no resolvable page size — there was no better claimant for the last free
ERROR id, and the alternative (reusing an existing id with an unrelated or misleading format
string) was worse. The band is now **fully allocated: 32 of 32**.

The next plan anywhere in the project that needs a new `ERROR`-severity message has no free id in
the band and must make a decision this phase deliberately did not make.

## The two facts that make the decision tractable

1. **The following range, `0xC0` through `0xDF`, is entirely unallocated** (32 free ids) —
   confirmed in `194-RESEARCH.md` §R3's full-catalog parse. Nothing occupies it today.
2. **Severity is an explicit catalog field, not derived from the id range.** `codegen.py`'s
   validation rules check the `severity` string on each entry; they do not infer severity from
   which numeric band an id falls in. Extending `ERROR` past `0xBF` into `0xC0+` is therefore
   **mechanically possible** with no codegen change — it is a naming-convention decision, not an
   implementation blocker.

## Why this phase did not decide it

Whether to treat `0xA0-0xBF` as a closed, historical ERROR band and start a fresh `0xC0-0xDF`
ERROR sub-range, or to renumber/reorganize the bands, or to adopt some other convention, is a
project-wide catalog convention with consequences for every future message across both sub-repos —
not a decision one phase fixing one write-path defect should make unilaterally.

## The guard that now protects this fact

`firestarter_app/tests/test_protection_status_catalog.py::test_error_band_fully_spent_0xa0_through_0xbf`
(194-06) replaces the prior guard
(`test_error_band_last_free_id_unspent`, which asserted `0xBF` stayed unspent and fired exactly
once, correctly, when 194-01 spent it). The new guard asserts the band is now fully allocated (32
of 32 ids present, all `SEVERITY_ERROR`) rather than re-asserting an already-spent single-id claim.

## What would close it

A decision, recorded as a project convention (in `messages.toml`'s own header comment or in a
future phase's design record), on where the next `ERROR`-severity id is minted from — most likely
`0xC0`, extending the same band, but that is the next phase's call to make and record.

## Filed by

Phase 194 (real page size reaches the firmware), U2, Plan 06.
