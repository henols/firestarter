# Phase 59: Correctness Gate + Per-chip Diff + SRAM Audit - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-09
**Phase:** 59-correctness-gate-per-chip-diff-sram-audit
**Areas discussed:** Diff report form, Diff field scope, SRAM audit depth/location, Unexplained-diff disposition, Phase-close boundary

---

## Diff report form & rationale granularity (GATE-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Re-runnable script, grouped-by-cause | Committed diff script vs pinned baseline; explain reassignments grouped by root-cause rule; doubles as regression check | ✓ |
| Manual jq, per-chip lines | One-time manual jq; every changed chip listed individually with own rationale | |
| You decide | Planner picks mechanism; lock only no-unexplained-diff + auditable | |

**User's choice:** Re-runnable script, grouped-by-cause
**Notes:** Aligns with correctness-first posture; the script becomes a reusable regression check against the immutable baseline.

---

## Diff field scope (GATE-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Full-record diff (catch surprises) | Diff every field, not just the 5 SC fields; 5 SC fields get priority rationale, everything else surfaced | ✓ |
| Only the 5 SC fields | Diff strictly algorithm/pinout/vpp_mv/pulse_duration/electrical.type | |
| You decide | Planner chooses scope | |

**User's choice:** Full-record diff (catch surprises)
**Notes:** Correctness-first + guess-table deletion can move unlisted fields (flags, chip_id, mem_size); a full diff catches collateral changes.

---

## SRAM audit depth & doc location (GATE-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Two-layer doc (audit + shipped), pure-doc | SR-1-style planning audit artifact + shipped GitHub-visible doc; blank-check/WP#/RTC content; escalate only on real safety issue | ✓ |
| Single shipped doc only | Skip the planning-trail artifact; just the shipped doc/comment block | |
| You decide | Planner picks location + layering | |

**User's choice:** Two-layer doc (audit + shipped), pure-doc
**Notes:** Mirrors the shield-revision / SR-1 two-layer lockstep pattern. Documentation only; firmware untouched unless a genuine hazard is found.

---

## Unexplained-diff disposition (GATE-02 gate strictness)

| Option | Description | Selected |
|--------|-------------|----------|
| BLOCK — fix build_db.py | Unexplained diff = Phase 58 logic bug; gate not green until citable rule explains it or build_db.py corrected | ✓ |
| Document-and-accept if benign | If reviewed and judged benign, document rationale and accept without changing build_db.py | |
| You decide | Planner sets policy under no-VPP-accepted-without-cause constraint | |

**User's choice:** BLOCK — fix build_db.py
**Notes:** Honors "no unexplained diffs remain" literally; no document-and-accept escape hatch.

---

## Phase-close boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Stop at green gate | Phase 59 = 4 SCs only; beta cut is a separate operator-gated /gsd-complete-milestone step | ✓ |
| Close includes beta cut | Fold v1.11 beta tag + lockstep release into Phase 59 | |
| You decide | Out of phase scope; roadmap/operator handles sequencing | |

**User's choice:** Stop at green gate
**Notes:** Consistent with "nothing is stable until I say so" — beta cut deferred to operator-gated milestone close.

---

## Claude's Discretion

- Exact diff-script form/location (re-runnable, grouped-by-cause, full-record constraints fixed).
- Exact SRAM shipped-doc location (standalone doc vs sram.cpp comment block) + planning audit artifact filename.
- Determinism (SC#4) check harness + whether CI-wired (only the byte-identical result is required).
- Whether the GATE-04 audit reads the host-side SRAM dispatch path in addition to the firmware no-op.

## Deferred Ideas

- v1.11 beta tag + lockstep release prep — separate operator-gated `/gsd-complete-milestone`.
- BENCH-01 real-hardware AT28C04/16 validation — deferred to v2.
- Full `pinouts.json` regeneration from minipro masks — Phase 58 D-04 follow-up, out of scope.
- Wiring SC#4 determinism check into CI — future hardening.
