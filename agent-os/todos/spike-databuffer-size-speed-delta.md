---
id: spike-databuffer-size-speed-delta
title: Spike — measure programming-time delta from a larger DATA_BUFFER_SIZE
captured: 2026-07-02
status: pending
type: spike
priority: medium
source: /gsd-explore 2026-07-02 (binary-protocol-savings-analysis.md)
---

# Spike — does a bigger `DATA_BUFFER_SIZE` actually speed programming?

De-risks the *speed* half of the binary-command-protocol seed **before**
committing to a breaking wire change. The whole payoff hinges on: reclaimed RAM →
larger buffer → fewer ack round-trips → faster. That chain's magnitude is
currently unmeasured.

## Experiment

- Bump `DATA_BUFFER_SIZE` within *existing* free RAM (no protocol change needed
  to test the buffer-size effect):
  - Uno: 512 → 1024 (if it fits with token array still present; else free RAM
    first via a temporary token-array shrink)
  - Leonardo: 1024 → 1536
- Time a full write+verify of a representative chip at each buffer size.
- Record: total wall-clock, and if possible per-chunk turnaround vs raw transfer
  time at 250k baud (this ratio is what determines whether more buffer helps).

## Decision it informs

- **Big speedup** → binary-command-protocol seed is worth the breaking change.
- **Marginal** → the RAM reclaim isn't worth a wire break for speed alone;
  reconsider on flash/cruft grounds only.

## Run it

`/gsd-spike` when ready (needs bench hardware — Uno + Leonardo). Operator-gated.

## Related

- Seed: `binary-command-protocol.md`
- Note: `binary-protocol-savings-analysis.md`
