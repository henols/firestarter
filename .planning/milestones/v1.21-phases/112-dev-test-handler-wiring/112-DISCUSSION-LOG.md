# Phase 112: `dev test` Handler Wiring - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-03
**Phase:** 112-`dev test` Handler Wiring
**Areas discussed:** Exit-code contract, Interactive vs CI, Sampler bracketing, Output & rendering

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Exit-code contract | Verdict → process exit-code mapping (scriptability contract) | ✓ |
| Interactive vs CI | Reconcile RPT-04 always-prompt with SC3 scriptable exit code | ✓ |
| Sampler bracketing | Where before/after VPP/VPE sampling happens vs the write step | ✓ |
| Output & rendering | What stdout shows + what/when files write to --output-dir | ✓ |

**User's choice:** All four areas.

---

## Exit-code contract

| Option | Description | Selected |
|--------|-------------|----------|
| 3-way (recommended) | 0=clean (OK/NA/SKIPPED); 1=any BAD (incl. chip-ID mismatch); 2=any marginal/indeterminate. Non-destructive N<M still exits 0. Mirrors sibling `dev` cmds + DB-diff disposition tiers. | ✓ |
| Binary strict 0/1 | 0 only if fully clean; 1 for anything not-clean (BAD OR marginal). Collapses fail vs inconclusive. | |
| Binary literal 0/1 | 0 unless a BAD; marginal → 0. Least friction, weakest signal. | |

**User's choice:** 3-way (recommended) → CONTEXT D-01.
**Notes:** Precedence when multiple verdicts co-occur: 1 (BAD) beats 2 (marginal), computed as `max` over per-verdict codes like validate-family's `overall_verdict`.

---

## Interactive vs CI

| Option | Description | Selected |
|--------|-------------|----------|
| TTY-aware (recommended) | TTY → prompt provenance + `--destructive` confirm; no-TTY → skip both, blank provenance (is_submittable=False), flag=consent; `-y/--yes` bypasses confirm on TTY. | ✓ |
| Always prompt + flag | Always run prompt_provenance; script must pass `--non-interactive`/`-y` or it blocks on stdin. | |
| You decide | Grounded default = TTY-aware. | |

**User's choice:** TTY-aware (recommended) → CONTEXT D-02/D-03.
**Notes:** Phase 112 only collects provenance + computes is_submittable; nothing acts on it (submission is Phase 113). A blank-provenance CI run producing a non-submittable report is the intended outcome, not a gap.

---

## Sampler bracketing

| Option | Description | Selected |
|--------|-------------|----------|
| Hook into run_plan (recommended) | Optional `sampler` callback param to run_plan, invoked immediately before+after the write step (both rails). Handler passes a thunk over sample_vpp_mv/sample_vpe_mv; engine never imports hardware.py; SAFE-02 clean; sampler=None/mock for tests. | ✓ |
| Coarse bracket in handler | No engine change: sample before run_plan and after it returns. Spans the whole sweep → ambiguous droop signal. | |
| Researcher/planner's call | Defer mechanism, constrained to D-03 tight-bracket intent. | |

**User's choice:** Hook into run_plan (recommended) → CONTEXT D-04.
**Notes:** This is the deferred Phase-111 `111-UAT` item (wire the sampler around run_plan; re-verify before/after tracks real rail behavior on W27C512/W29C020, Leonardo+Rev 2.0). Non-destructive standalone read stays in the handler.

---

## Output & rendering

| Option | Description | Selected |
|--------|-------------|----------|
| Table always; files on --output-dir (recommended) | Rich table to stdout every run; write `dev-test-<chip>.{json,md}` (md = self-contained issue body) to --output-dir only when given; no flag → terminal only, cwd stays clean. Hyphenated names mirror validate-family. | ✓ |
| Match validate-family exactly | Default --output-dir to '.' and always write both files. Litters cwd on casual runs. | |
| Table + inline fenced JSON; files optional | Also echo the fenced ```json to stdout. Noisier terminal. | |

**User's choice:** Table always; files on --output-dir (recommended) → CONTEXT D-05.
**Notes:** The `.md` artifact is exactly the Phase-113 self-contained issue body (human table + fenced JSON). validate-family's `_write_artifact` is the shape precedent; hyphenated filename avoids clashing with authored files (Pitfall 4).

---

## Claude's Discretion

Grounded defaults recorded in CONTEXT for the planner/researcher (not user decisions):
- `AutoCapture` sourcing (FW/board identity, host version, chip-ID, protocol path).
- `is_uv` derivation for `prompt_provenance` (protocol 0x0B / electrical-type, host-side).
- `TransportHealth` best-effort capture → `NOT_MEASURED` when unreachable.
- Flag naming (`-y/--yes` vs `--assume-yes`), chip-token filename sanitizer, helper decomposition.

Planner must-do (not open decisions): extend the Phase-109 SAFE-03 AST checker
(`tools/check_devtest_orchestrator.py` + negative-fixture pytest) to scan the new
handler; re-verify the deferred Phase-111 bench SC2 once the sampler is wired.

## Deferred Ideas

None — discussion stayed within phase scope. Adjacent concerns owned elsewhere:
`--submit`/issue upload/PII sanitization = Phase 113; `support_status` taxonomy +
N≥2 promotion + no-auto-graduate lock = Phase 114.
