# Frozen `chips` entries — additive-key discrepancy (orchestrator record)

**Recorded by:** Phase 162 execute-phase orchestrator, after Wave 2.
**Status:** disclosed, not repaired. No value measured by Phase 161 changed.

## The claim

Plan 162-01's `must_haves.truths` states:

> "The two existing `chips` entries (`w27c512`, `w29c020`) are byte-unchanged, because they
> are frozen inputs to Phase 161's twelve recorded positions."

Plan 162-02 inherits the same freeze intent.

## What is actually true

As literally worded, the claim is **false**. Both frozen entries gained two keys:

| key | added by | commit |
|-----|----------|--------|
| `chip_token` | plan 162-01 | `0c04361b` |
| `family_label` | plan 162-02 | `7189332c` |

Pre-phase key set at `d863a247` was
`['algorithm','package','pin_count','size_bytes','stamp_width','vpp_mv']`;
it is now that set plus `chip_token` and `family_label`.

**No pre-existing field changed value, and no key was removed** — the mutation is
purely additive. `162-01-SUMMARY.md` discloses the `chip_token` addition in prose
(lines 94–95) but classifies Deviations as "None"; `162-02-SUMMARY.md` records
`family_label` as an explicit Rule 2 deviation.

## Why this does not invalidate Phase 161

Checked at the time of writing, after Wave 2:

- `rig-pins.json` is **not** SHA-pinned — it does not appear in `images/SHA256SUMS.txt`,
  and no tool recomputes a digest over it.
- `bench/EVIDENCE.jsonl` is byte-identical to its pre-phase state
  (`sha256 792e54e4960a8741595cb0ed6ba9c91c8435be47cf7571d78fd2491c8bad8b83`),
  and `position_count_expected` is still `20`.
- No Phase 161 cell record under `bench/cells/` references either new key.
- `run_gates.sh` is green — 13/13 tool selftests, 5/5 live gates, exit 0 read directly —
  including `render_evidence.py --check` and `gate_record.py --jsonl EVIDENCE.jsonl`,
  so the twelve recorded WRV positions still reconcile against the record.

The freeze existed to stop Phase 161's *measured values* from moving. They did not move.

## Disposition

Not repaired. Both `capture_provenance.py` and `append_chip_evidence.py` now derive from
these keys; reverting them would red the suite to no benefit. The truth statement is
over-strong for what the freeze was protecting — it should have read "every pre-existing
field is value-unchanged" rather than "byte-unchanged".

Carry to the phase verifier and to Phase 166's CLOSE-01 honesty ledger.
