# Phase 174 Plan 01, Task 1: shape_id Name Set — Resolved

**Checkpoint:** `checkpoint:decision`, `gate="blocking-human"`
**Decision:** Freeze the concrete `shape_id` string set that Phases 175 through 181 and the
`MILESTONES.md` re-key ledger will reference by name.
**Resolved by:** the operator, via the orchestrator, before this executor was spawned.
**Resolution:** `full-sixteen`, with one measured amendment below.

## What was frozen

All sixteen names the plan's Task 1 `<context>` table proposed — the eight hand-specified D-02
table-1 rows and the eight real-path D-02 table-2 rows — are approved as the milestone's `shape_id`
namespace. The three later-phase names (`prune03-synthesized-fingerprint-match`,
`attr01-status-axis-transport-fault`, `uv-slot-write-pass`) are reserved, not frozen, in a
`RESERVED_SHAPE_IDS` set asserted disjoint from `SHAPE_IDS` (see
`firestarter_app/tests/fixtures/report_shapes.py`).

**Only `sst27sf512-six-step` is built by this plan** (174-01); the remaining fifteen names are
approved namespace reservations for plans 174-02 through 174-05 and later phases to build against —
this plan's `SHAPE_IDS` therefore holds exactly one member, `sst27sf512-six-step`, and
`FROZEN_HASHES` pins exactly that one hash. Freezing the full sixteen-name *set* now (this decision)
is distinct from *building* all sixteen shapes in this plan (not this plan's job).

## The measured amendment the operator ratified

- **`m27c512-full-canonical-name` freezes at the measured `776846bf2dc8`**, replacing
  `174-CONTEXT.md` D-12's inherited `a00791f1c2b4` → `a6f6c6354047` pair, which 174-RESEARCH.md
  proved does not reproduce from any m27c512 report shape across an exhaustive ~2.1e8-candidate
  pre-image sweep.
- **`uv-slot-write-pass` stays RESERVED, not frozen**, because the m27c512 write step is unreachable
  with the shipped `_mock_operator` test double — any hash frozen for it today would encode a mock
  artifact rather than a real UV write.

## Proceeding on measured values

Every hash literal committed by this plan is recomputed in-session by calling the real
`dedup_fingerprint` on a real `DiagnosticReport` built by a builder committed in the same commit
(D-09's own prohibition: "No hash literal is written into the tree that no committed builder in the
same commit can compute"). `sst27sf512-six-step`'s frozen literal `4dc282a5d596` was recomputed this
session and reproduces byte-exactly.

---
*Phase: 174-blast-radius-invariance-harness*
*Plan: 01*
