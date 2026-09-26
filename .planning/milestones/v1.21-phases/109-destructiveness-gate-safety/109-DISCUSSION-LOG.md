# Phase 109: Destructiveness Gate + Safety - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-02
**Phase:** 109-Destructiveness Gate + Safety
**Areas discussed:** UV write window, N-of-M banner math, Plan structure fork, SAFE-03 CI gate

---

## UV small-region write window (PATT-03)

Locked upstream: high-address + contiguous + engine-capped, never DB-configurable.
The open variable presented was SIZE (UV writes flip 1→0 irreversibly without a lamp).

| Option | Description | Selected |
|--------|-------------|----------|
| 256 B, top-anchored (Rec) | Last 256 bytes `[size-256, size)`; matches Phase-108 stand-in; tiny consumption → many retries; base pins high bits set | |
| 1 KB, top-anchored | 4× more coverage per write, 4× more consumption of a non-erasable chip | |
| You decide (bench-informed) | Lock only "small + top-anchored + engine-capped constant"; defer exact byte count to planner/researcher per STATE note | ✓ |

**User's choice:** You decide (bench-informed).
**Notes:** Recorded as Claude's Discretion in CONTEXT.md with a recommended 256 B / top-anchored default and the STATE-note "validate size/placement against real UV parts" flag.

---

## "N of M" banner math (SWEEP-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Applicable-only (Rec) | M = steps a `--destructive` run would actually execute for this chip (NA excluded); N = ran this run; ran-but-BAD counts as "ran" | |
| All plan slots | M = every op slot incl. NA (up to 6); simpler but inflates M with never-achievable steps | |
| You decide | Planner's call within SWEEP-05's loud-banner intent | ✓ |

**User's choice:** You decide.
**Notes:** Recorded as Claude's Discretion with the applicable-only counting as the recommended default.

---

## Plan structure fork (SAFE-01 × SWEEP-05)

Tension: SAFE-01 needs write/erase structurally absent from a non-destructive plan;
SWEEP-05's banner needs M (the full-destructive count).

| Option | Description | Selected |
|--------|-------------|----------|
| Advisory locked-list (Rec) | Executable `steps` omits write/erase; Plan carries a separate advisory `locked_destructive` (op+reason) the banner/report reads; one derive call, one object | ✓ |
| Omit + re-derive for M | Omit entirely; banner re-derives the full plan just to count M (double derivation, M outside the plan object) | |
| You decide | Planner's call, hard-constrained by "executable steps must not contain write/erase when non-destructive" | |

**User's choice:** Advisory locked-list (D-01, LOCKED).
**Notes:** Executor never iterates the advisory field → no code path can run a destructive op in a non-destructive run.

---

## SAFE-03 CI gate

Note framed: `dev test` is host-only, so the firmware-dispatch clause is naturally
satisfied — the real risk is a VPP-set / raw-command / `--force` call in the host
orchestrator. Anchored against v1.12's hollow GATE-03 tech debt.

| Option | Description | Selected |
|--------|-------------|----------|
| AST tool in ci.yml (Rec) | `tools/check_devtest_orchestrator.py` (AST, mirrors check_dispatch.py); deny VPP-set/raw-dict/force; own pass/fail fixtures so it can't rot hollow | ✓ |
| Grep-based check | Lighter bash/grep of dev-test files; faster to write, brittle, easy to fool | |
| You decide | Lock only "genuinely populated + build-failing + wired into CI" | |

**User's choice:** AST tool in ci.yml (D-02, LOCKED).
**Notes:** During scouting, discovered `check_dispatch.py` is gated via **pytest** (`test_check_dispatch_invariants.py` subprocess-invokes it, asserts exit 0 on clean), not a bespoke `ci.yml` step. Captured as D-03: the new gate must follow the same tool-plus-negative-fixture-pytest pattern (passing + planted-violation fixtures) so the `Run pytest with coverage` step is the real enforcement point — the anti-hollow contract.

---

## Claude's Discretion

- UV small-region window **size** (locked: small + top-anchored + engine-capped constant; recommended 256 B default; bench-informed).
- "N of M" banner **counting semantics** (recommended: applicable-only; NA excluded from M; ran-but-BAD counts as "ran").
- `locked_destructive` field naming, module-internal helper decomposition, and the exact deny-list of VPP-set / raw-command symbols the AST checker matches.

## Deferred Ideas

None — discussion stayed within phase scope. Adjacent concerns owned by Phases 110 (report/provenance), 111 (voltage sampler), 112 (`dev test` CLI surface + any `--destructive` confirm + exit codes), 113 (submission), 114 (no-auto-graduate lock).

**Reviewed todos (not folded):** `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` (0.9, firmware) — opposite axis (firmware VPP change vs host-only, zero-VPP-set phase); 7 other keyword false-positives not folded.
