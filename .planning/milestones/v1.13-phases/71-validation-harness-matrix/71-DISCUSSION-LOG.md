# Phase 71: Validation Harness + Matrix - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-16
**Phase:** 71-validation-harness-matrix
**Areas discussed:** Matrix source-of-truth, Recording stub strategy, validate-family CLI surface, Scaffold-now vs defer-to-73

---

## Matrix source-of-truth

| Option | Description | Selected |
|--------|-------------|----------|
| App-owned JSON, both read it | Single matrix JSON in firestarter_app; Python reads directly, native gets generated C++ header via codegen. No meta-repo ceremony (test infra, not wire contract). | ✓ |
| Meta-repo JSON + codegen to both | Lives in meta-repo, regenerates into both sub-repos (messages.toml-style lockstep). | |
| Python module + hand-mirrored C++ | Authored as Python dict; native carries hand-maintained mirror — can drift. | |

**User's choice:** App-owned JSON, both read it
**Notes:** Distinction surfaced and recorded — the authored source JSON is separate from the emitted `validation-matrix.{json,md}` results artifact (HARN-02). Two files: hand-authored input vs generated output.

---

## Recording stub strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Opt-in recording in shared .inc | Define-guarded recording buffer in host_stubs_common.inc; existing suites unchanged (flag off = no-op). Preserves WR-06 single-edit-point. | ✓ |
| Separate recording-stub .inc | New _shared/recording_bus_stub.inc family suites include instead; duplicates ~120 lines WR-06 centralized. | |
| Per-suite recording state | Each suite carries its own recording mock; most duplication, least consistent API. | |

**User's choice:** Opt-in recording in shared .inc
**Notes:** Honors the WR-06 consolidation intent; avoids re-introducing drift.

---

## validate-family CLI surface

| Option | Description | Selected |
|--------|-------------|----------|
| `dev validate-family <family>` | Per-family subcommand; bare/`--all` runs all. Matches existing dev verb style. | |
| `dev validate [--family X]` | `validate` verb defaulting to all, optional filter. | |
| You decide at planning | Defer verb/flag spelling; lock only that it's a new dev subcommand composing existing cycle methods + emitting the matrix artifact. | ✓ |

**User's choice:** You decide at planning
**Notes:** Locked constraints: new `dev` subcommand, composes existing cycle methods (no re-impl), emits matrix artifact. Claude-set default: no-board/chip → record SKIP-deferred cell, never hard-fail (keeps milestone closeable at partial coverage).

---

## Scaffold-now vs defer-to-73

| Option | Description | Selected |
|--------|-------------|----------|
| All 6 families' Tier-1/Tier-2 cells GREEN now | Phase 71 stands up native + host software cells for all 6 families (ungated); Phase 73 = Tier-3 HIL + SRAM no-op only. | ✓ |
| Framework + 1-2 reference families | Prove harness on 1-2 families; rest deferred to 73. | |
| You decide at planning | Lock deliverables; planner sizes how many families in 71 vs 73. | |

**User's choice:** All 6 families' Tier-1/Tier-2 cells GREEN now
**Notes:** Front-loads flash-free work per the software-first build-order driver; Phase 73 becomes purely bench.

---

## Claude's Discretion

- Exact `dev validate-family` verb/flag spelling (per-family arg vs `--all`/`--family`).
- Authored-matrix JSON file path within `firestarter_app/`.
- Generated C++ header committed vs built on-the-fly.
- Evidence-SHA capture mechanism for the emitted results artifact.
- Negative-control representation across software tiers vs bench-only.

## Deferred Ideas

None — discussion stayed within phase scope. Tier-3 evidence / SRAM no-op (Phase 73),
fixes (74), erase (75), spec gaps (76), protocol re-research (72) are recorded as
out-of-scope in CONTEXT.md, not as new ideas.
