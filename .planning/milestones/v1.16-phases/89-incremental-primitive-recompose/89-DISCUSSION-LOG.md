# Phase 89: Incremental Primitive Recompose — Discussion Log

**Date:** 2026-06-26
**Mode:** discuss (default)

> Human-reference audit trail. Not consumed by downstream agents — see 89-CONTEXT.md
> for the locked decisions.

## Gray areas presented (user selected ALL four)

1. Flash-gate disposition
2. Abort / partial-completion policy
3. Primitive home / module structure
4. Re-bless threshold during extraction

## Area 1 — Flash gate disposition

**Question:** How to enforce the Leonardo flash gate per step, given P4/P3/P5 extraction
adds call overhead while P7 dedup frees headroom?

- Options presented: (a) Per-step ≤+16B + phase net-decrease [recommended];
  (b) Strict per-step ≤0; (c) Cumulative-only (final < baseline).
- **User selected:** (a) Per-step ≤+16B, phase net-decrease.
- Captured as **D-01**. Reuses Phase 87-04 `DELTA≤16` precedent; final flash % reported.

## Area 2 — Abort / partial-completion policy

**Question:** What if one primitive (P3 VPP riskiest) can't meet its gate / reconcile?

- Options: (a) Abort-that-primitive-and-continue [recommended]; (b) Stop whole phase;
  (c) Re-bless and force through.
- **User selected:** (a) Abort that primitive, ship the rest.
- Captured as **D-02**. Each extraction independently reversible; defer the blocked one
  with a documented FUT/CR reason.

## Area 3 — Primitive home / module structure

**Question:** Where do the extracted shared primitives live?

- Options: (a) Dedicated `proms/primitives.cpp` + `include/primitives.h` [recommended];
  (b) Grow `flash_utils`; (c) Fold into `memory.cpp`.
- **User selected:** (a) Dedicated primitives module.
- Captured as **D-03**. Cross-family P4/P3/P5 code → new module; P7 SDP const-tables
  stay flash-local in `flash_utils.h`.

## Area 4 — Re-bless threshold during extraction

**Question:** How strict is the byte-exact golden trace during extraction?

- Options: (a) Zero-diff goal, re-bless only on review [recommended]; (b) Re-bless
  freely; (c) Absolute zero-diff, no re-bless.
- **User selected:** (a) Zero-diff goal, re-bless only on review.
- Captured as **D-04**. Inherits Phase 88 D-02 audit-checkpoint workflow; default to
  zero-diff, re-bless is a reviewed/documented/human-gated event.

## Carried forward (not re-asked — milestone safety model)

D-05 (frozen gates), D-06 (protocol-keyed + WARNING-5 guards), D-07 (INV/golden-trace
oracle), D-08 (over-voltage + resolve_chip + 2516 UNVERIFIED), D-09 (firmware-only no
lockstep; P7→P4→P3→P5 order). See 89-CONTEXT.md `<decisions>`.

## Deferred ideas

- Phase 90 bench validation + PROTOCOL-LEDGER.
- 0x34 X88C64 handler (PCB-blocked, FUT-01).
- Any primitive that can't meet its gate → deferred per D-02.

## Claude's discretion (delegated)

- Exact primitive symbol names / signatures (module location fixed by D-03).
- Commit granularity within the one-atomic-commit-per-primitive pattern.
