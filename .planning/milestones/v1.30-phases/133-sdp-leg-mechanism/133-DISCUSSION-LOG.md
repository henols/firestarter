# Phase 133: SDP Leg Mechanism - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-04
**Phase:** 133-sdp-leg-mechanism
**Areas discussed:** The `_dispatch_sdp` shape, The `finally` + what `_run_step` catches

**Areas offered but not selected:** Parity-test scope (LEG-15), The `group=None` inertness proof —
both resolved under Claude's Discretion (D-12, D-13) rather than left open.

---

## Gray-area selection

| Option | Description | Selected |
|--------|-------------|----------|
| The `_dispatch_sdp` shape | One function for all four SDP ops, or four separate arms? ROADMAP names this the phase's open question; feeds criterion 5's deliberate-break test. | ✓ |
| The `finally` + what `_run_step` catches | Criteria 1 and 2, same code region. Generic registry vs hardcoded window; `SerialError`'s three subclasses. | ✓ |
| Parity-test scope (LEG-15) | 4 of P-23's 10 registries are Phase 134 surfaces — a test authored here either sits RED for a phase or needs fail-open exemptions. | |
| The `group=None` inertness proof | Is a `Step.group` field the right mechanism, and what does the no-op test assert? | |

**User's choice:** the two engine-mechanism areas.
**Notes:** the two unselected areas were folded into Claude's Discretion rather than dropped — see below.

---

## The `_dispatch_sdp` shape

### Q1 — What shape should the SDP dispatch take in chip_test.py?

| Option | Description | Selected |
|--------|-------------|----------|
| One guarded `_dispatch_sdp` | Guard-at-top + internal per-op branch + terminal `AssertionError`, cloning `_dispatch_multi_run` (guard `:1082`, `AssertionError` `:1130`). Gives criterion 5's break-test a single choke point. | ✓ |
| Per-op `_dispatch_sdp_lock` / `_dispatch_sdp_unlock` | Mirrors `_dispatch_id` — flatter, nothing internal to break. Cost: one new `if` arm per op, against criterion 4's "zero added branching cost". | |
| A dict table: op → operator method | Most compact, inherently fail-closed on a missing key. Cost: a new idiom for this module; table-shaped registries are the fail-open shape this phase removes. | |

**User's choice:** One guarded `_dispatch_sdp` (→ D-01)
**Notes:** the recommendation rested on the module already proving this shape fails closed, so no new idiom has to be argued for.

### Q2 — Which SDP op strings does Phase 133 define?

| Option | Description | Selected |
|--------|-------------|----------|
| Just `sdp_lock` + `sdp_unlock` | The only two the mechanism criteria can exercise; Phase 134 adds what its leg needs. | ✓ |
| All four leg ops now | Phase 134 would only wire `derive_plan` and the report. Cost: `ruff`'s `F` rules don't flag unused module constants, so two would be genuinely dead for a phase. | |
| You decide | — | |

**User's choice:** Just `sdp_lock` + `sdp_unlock` (→ D-02)
**Notes:** this is what fixes the 133/134 boundary concretely.

### Q3 — How should single-shot SDP emissions relate to the `runs>=2` machinery?

| Option | Description | Selected |
|--------|-------------|----------|
| Single-run, explicitly excluded from `_MULTI_RUN_OPS` | A second lock is a second mutation with no comparison value; `marginal` is meaningless on an unreadable axis (Phase 117 D-05, Phase 119 D-12). The exclusion becomes an asserted exemption. | ✓ |
| Route through `_dispatch_multi_run` | Free reuse of the runs loop and marginal policy. Cost: two lock emissions per leg on a finite-endurance family; an invented signal. | |
| You decide | — | |

**User's choice:** Single-run, excluded from `_MULTI_RUN_OPS` (→ D-03)

### Q4 — Where does the new arm sit inside `_dispatch_step`?

| Option | Description | Selected |
|--------|-------------|----------|
| Last, above the terminal fail-closed return | All 7 shipped ops return from arms 1–4 and never evaluate the new membership test — makes criterion 4 provable about return points. | ✓ |
| First, above `OP_ID` | Better read-order for safety-relevant ops. Cost: every shipped op pays an extra membership test; criterion 4 needs rewording. | |
| Folded into the terminal return | Same zero-cost property, fewer lines. Cost: the phase's point reads as a special case of the failure path. | |

**User's choice:** Last, above the terminal fail-closed return (→ D-04)

### Q5 — Does `Step.group` exist? (raised because criterion 4's wording presupposes it)

| Option | Description | Selected |
|--------|-------------|----------|
| No `group` field — key on `_SDP_OPS` membership | The op string already carries the distinction, per the module's own `write-partial` argument at `:282-288`. Consequence: criterion 4's `group=None` clause is satisfied vacuously and the record must say so. | ✓ |
| Add `Step.group: str \| None = None` | Honors criterion 4 literally; gives 134 a grouping axis. Cost: a field 7/7 shipped ops leave `None`, plus an eleventh registry for the parity test to police. | |
| You decide | — | |

**User's choice:** No `group` field (→ D-05)
**Notes:** surfaced deliberately rather than decided silently, because it makes a ROADMAP success criterion vacuous — that consequence is recorded in D-05 and must reach the phase record.

**Area closed:** user selected "Next area". One point resolved by measurement instead of asking — P-07 warns `check_devtest_orchestrator.py` won't scan a new leg helper, but its deny-visitor AST-walks all of `chip_test.py`, so a `_dispatch_sdp` there *is* scanned; the gap is specific to `cli_handlers.py` helpers via `_HANDLER_FUNCTION_NAMES`.

---

## The `finally` + what `_run_step` catches

### Q6 — What shape should `run_plan`'s cleanup mechanism take? (LEG-10 / criterion 1)

| Option | Description | Selected |
|--------|-------------|----------|
| Generic registry: steps push cleanup callables | LEG-10's own wording; empty registry = proven no-op, same discipline as `sampler=None` at `:759-761`. | ✓ |
| Hardcoded lock→unlock window | Literally P-20 prevention #2; simpler. Cost: Phase 134's leg and any later cleanup op each re-open `run_plan` to widen the special case. | |
| You decide | — | |

**User's choice:** Generic cleanup registry (→ D-06)

### Q7 — What happens to the report on the propagating path?

| Option | Description | Selected |
|--------|-------------|----------|
| Accept report loss on Ctrl-C; record the attempt on the exception | Chip is safe, report is gone, and the record says so plainly. "Ctrl-C must stay Ctrl-C" per criterion 2. | ✓ |
| Caller-supplied results list so partial results survive | Strictly more honest output. Cost: changes `run_plan`'s signature and ~12 call sites, inside the phase whose criterion 4 is "provably byte-identical". | |
| You decide | — | |

**User's choice:** Accept report loss, record the attempt (→ D-07)
**Notes:** the question was grounded in a measured fact — `cli_handlers.py:2161` assigns `results = run_plan(...)` and `:2166` builds the report from it, so a re-raise loses the report outright. The honest residual is recorded rather than engineered away.

### Q8 — LEG-11 says catch `SerialError`, but it has three subclasses

| Option | Description | Selected |
|--------|-------------|----------|
| Catch `SerialError` but re-raise the two run-fatal subclasses | Half-seated cable (`SerialTimeoutError`) degrades one step; missing programmer / too-old firmware still kills the run loudly. | ✓ |
| Catch `SerialError` flat, as LEG-11 words it | Simplest, exact requirement text. Cost: no-board runs produce a full BAD report instead of one clear error — a documented false-green shape in this project. | |
| Catch only `SerialTimeoutError` + `HardwareOperationError` | Narrowest set covering criterion 2's named case. Cost: other `SerialError`s still kill the report, so LEG-11's intent is only partly met. | |

**User's choice:** Catch `SerialError`, re-raise `ProgrammerNotFoundError` + `FirmwareOutdatedError` (→ D-08)
**Notes:** measured hierarchy made this askable — `HardwareOperationError` is a sibling of `Exception`, not an `EpromOperationError`, which is why the existing handler misses it and LEG-11 is a real gap.

### Q9 — How is "no bare except" proven? (criterion 2)

| Option | Description | Selected |
|--------|-------------|----------|
| Behavioral tests + extend the existing AST gate | Behavioral tests are mandatory anyway; the gate half is one `visit_ExceptHandler` method on machinery that already AST-walks `chip_test.py` and has 18 paired tests. | ✓ |
| Behavioral tests only | Zero new gate surface. Cost: a future bare `except Exception:` elsewhere goes uncaught. | |
| New standalone `tools/check_no_bare_except.py` | Matches the house `tools/check_*.py` family. Cost: a fresh `_HERE`-resolving target list — the shape that scanned nothing and exited 0 on v1.23's only outward gate. | |

**User's choice:** Behavioral tests + extend `_OrchestratorDenyVisitor` (→ D-09)

### Q10 — What if a cleanup callable itself raises during the drain?

| Option | Description | Selected |
|--------|-------------|----------|
| Per-callable try/except over the same named set, record and continue | Original exception stays intact; no cleanup can strand the ones behind it; consistent with criterion 2 at a second site. | ✓ |
| Broad catch in the drain only, with a comment | Defensible best-effort argument (as the module makes for the sampler at `:757-759`). Cost: a second broad catch in the phase whose criterion is "no broad catches"; D-09's new deny-rule would need an exemption. | |
| You decide | — | |

**User's choice:** Per-callable try/except, record and continue (→ D-10)

### Q11 — Is the unlock a plan step, a registry entry, or both?

Raised because the registry decision (D-06) collides with how criterion 3 words LEG-09: the
`_DESTRUCTIVE_OPS` absence only bites if the unlock can appear as a plan step, and in Phase 134 it is
step 4 of the derived leg.

| Option | Description | Selected |
|--------|-------------|----------|
| Registry-only in 133; keep it out of `_DESTRUCTIVE_OPS` anyway and assert that | Both criterion-3 tests satisfied by registry behavior; the absence is recorded as forward-protection for Phase 134, not a live 133 gate. | ✓ |
| Both a plan step and registry-registered, with an idempotence guard | Matches 134's end state now. Cost: needs a guard, and a double emission double-counts in the report and inflates the endurance notice. | |
| Plan step only — drop the registry for unlock | Simplest reading of criterion 3. Cost: reintroduces the exact P-20 hazard the phase exists to close. | |

**User's choice:** Registry-only in 133, absence asserted as a standing invariant (→ D-11)

**Area closed:** user selected "I'm ready for context".

---

## Claude's Discretion

Both areas were offered for discussion and not selected; each was decided rather than left open.

- **D-12 — LEG-15 parity-test scope.** Police every row of P-23's table now, via an exemption table
  requiring a non-empty reason per `(op, registry)` pair, with three fail-closed guards: empty reason
  fails, a stale row naming a nonexistent pair fails, and the policed-registry count must equal a
  declared constant. Rejected scoping to only the three `chip_test.py`-local registries (leaves the
  fail-open five untouched, against LEG-15's "all required registries"), and rejected authoring it RED
  until Phase 134 (a pre-authored gate leg proves nothing until seen to pass, and a RED gate carried
  across a phase boundary gets force-proceeded).
- **D-13 — criterion 4's no-op regression test.** Assert behavior, not diff-emptiness: an in-test
  literal for the derived op sequence and per-step `(verdict, run_count)` — not a syrupy snapshot, per
  Phase 132 D-13's unused-snapshot trap — plus a monkeypatch-`_dispatch_sdp`-to-raise sentinel proving
  no shipped op reaches it. Rejected any empty-`git diff` or byte-identical-file criterion; that shape
  breaks the moment Phase 134 adds a guard to the same file.

## Deferred Ideas

Nothing was raised during discussion that fell outside the phase boundary — no scope-creep redirects
were needed. The deferrals recorded in CONTEXT.md `<deferred>` come from the ROADMAP's own 133/134
split and from this session's measurements, not from the discussion:

- Phase 134: the four-step leg, every report surface, the `_ALWAYS_WRITES_NOTICE` write-count
  correction, gh#20 triage, and discharge of D-12's five exemption rows.
- Backlog 999.28: `write --sdp-relock` (operator decision 2026-08-03).
- Unowned carries: ratcheting the watermark to the measured 32 (Phase 132 D-09 recorded, did not set);
  adding the new parity module to the mypy test strict-island.
- Housekeeping surfaced by measurement: `.planning/codebase/TESTING.md` is stale by ~84 test files and
  asserts the project has no Python tests — a `/gsd-map-codebase` refresh, not this phase's work.
