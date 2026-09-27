---
title: AT28C256 write-path failure (gh#20) — blank-check/write/verify all BAD on Rev 2.3
date: 2026-08-04
priority: medium
blocked_by: nothing technical — no AT28C part in operator inventory to diagnose it against; needs either the reporter's continued engagement or a bench sample
resolves_phase: none (triaged by v1.30 Phase 134 LEG-18; the underlying defect is untouched by that phase)
owner: henols
---

# AT28C256 write-path failure (gh#20) — a real, still-open defect this milestone only triaged

**Owner: henols** (the repo owner/operator). Named explicitly and deliberately, so this does not
become another unowned acknowledgement — the same failure mode this project's own backlog has
flagged before (v1.30's `write-sdp-relock-deferred.md` and the RELOCK pair carry the identical
discipline). May be reassigned to whoever is best positioned to obtain a bench sample or correspond
with the reporter.

## The symptom, as reported

[gh#20](https://github.com/henols/firestarter_prom/issues/20) — OPEN since 2026-07-30, title
`[dev test] at28c256 — FAIL (00e121446ceb)`, 0 comments. Measured facts (re-verified read-only
2026-08-04, unchanged since filing):

- host `3.0.0b14`, `hw_revision Rev 2.3`, chip `at28c256`, protocol `13`
- `blank-check`, `write`, and `verify` steps **all BAD** — the write step's fingerprint is
  `indeterminate`, meaning the read-back neither matched the expected pattern nor classified as a
  recognizable degenerate shape (blank/contact, address-line, transport)
- `id` step is `NA` (no chip-id in this DB entry — expected, `AT28C256` has none), `erase` is `NA`
  (protocol `0x0D` has no erase operation)
- voltage `vpp 11800 mV` / `vpe 13700 mV`, before == after both directions — no droop observed
  across the run
- `dedup_fingerprint 00e121446ceb`; `db_diff`: `current_support_status: supported`,
  `proposed_disposition: suggests community-fail signal`, `ladder_state: community-fail`

## What this phase (v1.30 Phase 134) established, and what it did not

Phase 134's `dev test` SDP leg was **triaged against this bench** (see
[`134-GH20-TRIAGE.md`](../../phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-GH20-TRIAGE.md)):
under the new baseline-transition gate, `write-baseline-b` would itself report BAD on this bench,
the gate would close, and **no SDP lock would ever be emitted** against this part — the mechanism
that prevents "lock a part whose baseline write never worked" is what this milestone shipped.

**This does NOT diagnose the chip.** The Evidence Ceiling (`133-RECORD.md` §6, restated in the
triage artifact) applies here without softening: no fixture in this milestone simulates real SDP
inhibition, and this triage does not establish *why* the write path failed on this specific bench —
only what the tool would now correctly *do* about it (refuse to lock, render the drop visibly).
Candidate causes not distinguished by the report alone: a genuinely SDP-locked die with no
supported unlock path reached, a marginal/failing VPP rail at the measured 11.8 V, a contact fault
not caught by the blank-check's own classification, or a firmware/host protocol mismatch on this
specific board revision (`Rev 2.3`). Diagnosing between these needs either the reporter's continued
engagement (a follow-up `dev test` at a different VPP, or with an oscilloscope on the write strobe)
or a bench sample the maintainer does not currently have.

## What is owed

1. **The public reply to gh#20 is Phase 137's** (CLOSE-06), behind its blocking operator
   wording-review gate, alongside the gh#12 reply. Nothing in this todo, or in `134-GH20-TRIAGE.md`,
   is posted anywhere — this item and its sibling artifact exist so the finding is recorded rather
   than silently dropped, per D-16.
2. **The underlying defect itself** — whether `AT28C256`/Rev 2.3 boards have a real, reproducible
   write-path problem, and if so what causes it — remains open and unowned by any phase in this
   milestone. Named here with an owner so it is tracked rather than lost.
3. **May be reassigned** — `henols` is named as the repo owner/operator, not necessarily as the
   engineer who will investigate; reassignment to whoever picks this up is expected and fine.

## Related

- [`134-GH20-TRIAGE.md`](../../phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-GH20-TRIAGE.md)
  — the full triage finding (LEG-18).
- `134-CONTEXT.md` D-16, D-11 — the decision record for why this is triaged-not-fixed and why the
  `dedup_fingerprint` orphaning is an accepted, recorded cost.
- `.planning/todos/pending/gh12-followup-after-dev-sdp-retirement.md` — the sibling outward-facing
  follow-up this milestone also owes Phase 137, under the same operator wording-review gate.
- ROADMAP `## Backlog` — Backlog **999.29** cross-links this item.
