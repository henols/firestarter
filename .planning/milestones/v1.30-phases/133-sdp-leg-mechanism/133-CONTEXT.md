# Phase 133: SDP Leg Mechanism - Context

**Gathered:** 2026-08-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Harden `dev test`'s step-execution engine (`firestarter/chip_test.py`) so it can carry a lock/unlock
leg safely, and make adding an op to its vocabulary machine-verified against every registry the op
must join — all of it provably inert for the seven ops that ship today.

**In scope:** a `_dispatch_sdp` arm and an `_SDP_OPS` allow-list; the `OP_SDP_LOCK` / `OP_SDP_UNLOCK`
op strings; `sdp_unlock`'s exemption from `_DESTRUCTIVE_OPS`; a cleanup registry drained in a
`run_plan` `finally`; widened-but-named exception handling in `_run_step`; a new bare-except deny-rule
in `tools/check_devtest_orchestrator.py`'s existing AST visitor; the LEG-15 op-registration parity
test; a no-op regression test proving the seven shipped ops are behaviorally unchanged.

**Out of scope — and load-bearing:**
- **No leg derivation.** `derive_plan` is not taught to emit SDP steps. That is Phase 134 (LEG-01/02).
  This phase's ops are reachable only from a directly-constructed `Step` in a test, plus the registry
  drain (D-11).
- **No report surface.** The `HELD`/`NOT-HELD`/`NOT-RUN` field, the N-of-M change, the "rewrite"
  recovery wording, `dedup_fingerprint`, and the `diagnostic_report.py` renderer are all Phase 134
  (LEG-12/13/14). This phase renders nothing new.
- **`_ALWAYS_WRITES_NOTICE` is NOT edited.** Measured this session: it claims "Every write/verify/erase
  step runs TWICE per invocation". Because no plan derives an SDP step in this phase, the true write
  count changes by **zero** here. Editing it now would describe a run that does not yet exist. Phase
  134 owns it (P-08).
- **No baseline gate, no oracle, no truth table, no gh#20 triage.** Phase 134 (LEG-04/05/06/07/08/18).
- **`eprom_operations.py` stays ring-fenced** (`FUT-MYPY-02`, operator decision 2026-08-03). Read
  `sdp_unlock` (`:1736`) and `sdp_lock` (`:1784`); do not type-fix that module.
- **No watermark edit.** The `35` in `pyproject.toml:159` is not touched. See the headroom note in
  `<code_context>` — this phase spends against it, it does not move it.
- **`firestarter` (firmware) is not touched at all.** Host-only, no lockstep, no `.hex` re-cut.
- **No new command-line option.** `dev test` keeps zero options (LEG-01's constraint, inherited).

</domain>

<decisions>
## Implementation Decisions

### Three measured corrections — read before planning

Each was measured in this session against the live milestone branch, not inherited from the record.

1. **The research's phase numbers are off by one against the current ROADMAP.** `research/SUMMARY.md`
   §"Phase 133" (line 726) describes *the oracle* — that is now **Phase 134**, because the ROADMAP
   later split the leg into 133 (mechanism) + 134 (oracle). `PITFALLS.md` P-20 and P-23 say "Phase to
   address: 133" and those **do** land here, but P-20's prevention items 3 and 4 (baseline gate, report
   wording) are Phase 134's. **Cite research by P-number, never by phase number.**

2. **`tools/parse_devtest_issue.py` has no op vocabulary at all.** P-23 lists it as a fail-open
   registry ("a new op in a filed issue may not parse"), but measured: the module is a generic JSON-fence
   extractor (`_FENCE` at `:64`, `_DEV_TEST_MARKER` at `:59`) with **zero** op-string constants. There is
   no allow-list to be omitted from. So P-23's ten rows are **nine policeable registries plus one that
   does not exist**. Re-verify before writing the parity test; do not police a phantom registry, and do
   not silently drop the row either — record the correction (D-12).

3. **P-23's and P-20's line anchors have drifted.** Measured: `run_plan` is at **`:709-794`** (P-20 says
   `:757-802`); `_MULTI_RUN_OPS` is at **`:654`** (P-23 says `:657`); `_dispatch_step` is at
   **`:901-952`** (P-23 says `:903-948`). `_DESTRUCTIVE_OPS` at `:636` is correct. Anchor on **function
   and constant names**; re-measure every number at plan time (Phase 132 D-11's discipline).

### The `_dispatch_sdp` shape

- **D-01:** **One guarded `_dispatch_sdp(op, name, eprom_data, operator)`** — an `if op not in _SDP_OPS: return StepResult(verdict=VERDICT_BAD, ...)` guard at the top, an internal per-op branch, and a terminal `raise AssertionError(f"unreachable: op {op!r} passed the _SDP_OPS guard")`. This is `_dispatch_multi_run`'s existing shape copied structurally (its guard at `:1082-1093`, its terminal `AssertionError` at `:1130`), so the module gains no new idiom, and criterion 5's deliberate-break test gets a single choke point to break. Rejected: per-op `_dispatch_sdp_lock`/`_dispatch_sdp_unlock` functions mirroring `_dispatch_id` (flatter, but each op costs a new `if` arm in `_dispatch_step`, which is exactly what criterion 4's "zero added branching cost" claim has to survive — and there is then no single point a break-test can attack); and a `dict` table mapping op → operator-method name (most compact and inherently fail-closed on a missing key, but every other dispatch in this module is explicit `if` arms, and a table-shaped registry is the fail-open shape this phase exists to remove).

- **D-02:** **Phase 133 defines exactly two op strings: `OP_SDP_LOCK` and `OP_SDP_UNLOCK`.** They are the only two the mechanism criteria can actually exercise — criterion 3 names both, and the cleanup registry needs only the unlock. Rejected: defining all four of Phase 134's leg ops now so that 134 only wires `derive_plan` and the report — `ruff`'s `F` rules do not flag unused module-level constants, so two of the four would be genuinely dead code for a whole phase, and this phase would ship vocabulary no test in it exercises.

- **D-03:** **SDP emissions are single-run and explicitly excluded from `_MULTI_RUN_OPS`.** Running a lock twice is a second mutation with no comparison value, and `_dispatch_multi_run`'s marginal-on-disagreement policy is meaningless for an emission whose result cannot be read back at all (protection state is unreadable on this family — Phase 117 D-05, Phase 119 D-12). The exclusion is not incidental: it becomes one of the parity test's **asserted exemptions** with a reason string (D-12). Rejected: routing lock/unlock through `_dispatch_multi_run` for free reuse of the runs loop — it would emit two locks per leg on a finite-endurance family and would invent a `marginal` verdict on an axis that carries no readable signal, which is the P-06 emission-claim-read-as-state-claim error in verdict form.

- **D-04:** **The `_dispatch_sdp` arm goes last in `_dispatch_step`, immediately above the terminal fail-closed `return`.** The current arm order is `OP_ID` → `OP_BLANK_CHECK` → `OP_READ` → `_MULTI_RUN_OPS` → terminal `BAD`. Placing the new arm at position 5 means all seven shipped ops return from arms 1–4 and **never evaluate the new membership test at all**, which turns criterion 4's "zero added branching cost" from a hand-wave into a provable statement about return points (and D-13's sentinel test proves it mechanically). Rejected: first, above `OP_ID` (better read-order for the safety-relevant ops, but every shipped op then pays one extra frozenset membership test and criterion 4 would need rewording to "no behavioral change"); and folding the dispatch into the terminal `return` (same zero-cost property, fewer lines, but it makes the phase's whole point read as a special case of the failure path).

- **D-05:** **No `Step.group` field. The SDP arm keys on `_SDP_OPS` membership of the op string.** The op string already carries the distinction, which is the argument the module itself makes for `write-partial` at `:282-288` — *"every consumer that reads `StepResult.op` sees it without learning a new field"*. Rejected: adding `Step.group: str | None = None` to honor criterion 4's wording literally and pre-build an axis for Phase 134's four steps — it adds a dataclass field that 7 of 7 shipped ops leave `None`, and it adds an **eleventh registry** for the LEG-15 parity test to police, i.e. it creates fail-open surface inside the phase whose job is removing it. **Honest consequence, to be stated in the phase record and not smoothed over:** ROADMAP criterion 4's clause *"an op with `group=None` takes the exact pre-existing dispatch path"* is then satisfied **vacuously** — there is no `group` field, so no op has `group=None`. The record must say the criterion's *intent* (shipped ops are behaviorally unchanged at zero added branching cost) was met by a different mechanism, and must not restate the criterion's literal words as though they were tested.

### The cleanup registry, the exception set, and the unlock path

- **D-06:** **A generic cleanup registry: `run_plan` keeps a `list` of cleanup callables that a successful `sdp_lock` step appends its unlock to, drained in one `try/finally` around the whole step loop.** This is LEG-10's own wording ("drains a cleanup registry in a `finally`"), and an empty registry is a **proven no-op** for every currently-shipping run — the same discipline the module already documents for `sampler=None` at `:759-761` ("adds zero calls and leaves every existing caller's `StepResult` list unchanged"). Rejected: a hardcoded `try/finally` around just the lock→unlock window with the unlock written inline, which is literally what P-20 prevention #2 describes and is simpler — but Phase 134's four-step leg, and any later cleanup-needing op, would each have to re-open `run_plan` to widen the special case, and a special case widened three times is how the flat-loop shape rotted in the first place.

- **D-07:** **On the propagating path the cleanup drains, the unlock attempt is recorded on the exception (or logged), and `KeyboardInterrupt`/`SystemExit` propagates unchanged — the report is honestly forfeited.** Measured constraint that forces the choice: the production caller does `results = run_plan(...)` at `cli_handlers.py:2161` and builds the report from `results` at `:2166`, so any re-raise means the assignment never happens and there is no report to render. Criterion 2 requires "Ctrl-C must stay Ctrl-C", so swallowing it to save the report is not available. Rejected: changing `run_plan` to append into a caller-owned results list so a partial report always survives — strictly more honest output, but it changes `run_plan`'s signature and every one of its existing call sites (10 in `tests/test_chip_test.py`, 1 in `tests/test_diagnostic_report.py`, 1 in production), which is real blast radius inside the phase whose criterion 4 is *"provably byte-identical in behavior"*. **Honest residual to state plainly in the phase record:** after a Ctrl-C mid-leg the chip is left with an unlock attempted, and the user sees no `dev test` report at all.

- **D-08:** **`_run_step` catches `SerialError` and `HardwareOperationError`, but re-raises `ProgrammerNotFoundError` and `FirmwareOutdatedError` first.** Measured hierarchy (`firestarter/exceptions.py`): `SerialError(Exception)` at `:13` with three subclasses — `SerialTimeoutError` `:19`, `ProgrammerNotFoundError` `:25`, `FirmwareOutdatedError` `:31`; `HardwareOperationError(Exception)` at `:69` is a sibling, **not** an `EpromOperationError` subclass, which is why `_run_step`'s existing `except EpromOperationError` does not reach it and LEG-11 is a real gap. The half-seated-cable case criterion 2 names is `SerialTimeoutError`, which degrades one step. But "no programmer attached" and "firmware too old" are run-fatal host-setup conditions: catching the base class flat would turn them into six BAD steps and a report that reads as a broken chip. This project already has a documented false-green trap in exactly the no-board shape. Rejected: catching `SerialError` flat as LEG-11 words it (simplest, exact requirement text, but manufactures a chip-fault report out of a host-setup fault); and catching only `SerialTimeoutError` + `HardwareOperationError` (narrowest set that covers criterion 2's named case, but any other `SerialError` still kills the whole report, so LEG-11's stated intent is only partly met).

- **D-09:** **No-bare-except is proven two ways: behavioral tests, plus a new deny-rule in `tools/check_devtest_orchestrator.py`'s existing `_OrchestratorDenyVisitor`.** The behavioral tests are mandatory regardless — criterion 1 wants `KeyboardInterrupt`/`SystemExit` reaching the `finally`, criterion 2 wants the deliberate `AssertionError` at `chip_test.py:1130` still escaping `run_plan`. The gate half is cheap because the machinery exists: that tool already does a real `ast.parse` + `ast.NodeVisitor` walk over `chip_test.py` (never a hollow declared-empty detector, per its own docstring at `:32-33`), already has the `FIRESTARTER_DEVTEST_SRC` env-override seam at `:86`, and already has a paired test module with 18 tests (`tests/test_check_devtest_orchestrator.py`) — so this is one `visit_ExceptHandler` method flagging `type is None` or a `type` naming `Exception`/`BaseException`, not a new tool. Rejected: behavioral tests only (zero new gate surface, but a future bare `except Exception:` added elsewhere in the module goes uncaught until something breaks); and a new standalone `tools/check_no_bare_except.py` matching the house `tools/check_*.py` family — it would need a fresh `_HERE`-resolving default target list, which is the exact shape that scanned nothing and exited 0 on v1.23's only outward-facing gate.

- **D-10:** **Each cleanup callable is wrapped in its own `try/except` over the same explicitly-named classes the step path catches (`SerialError`, `HardwareOperationError`, `EpromOperationError`), recorded as a failed-unlock attempt, and the drain then continues.** This keeps the original exception intact rather than masking it, keeps criterion 2's no-bare-except rule consistent at a second site, and stops one failing cleanup from stranding the entries behind it in the registry. Rejected: a broad catch in the drain only, with a comment — defensible on the grounds that the original exception always matters more and the drain is best-effort (the argument the module already makes for the sampler at `:757-759`), but a second broad catch inside the phase whose criterion is "no broad catches" reads as inconsistent to any reviewer, and D-09's new AST deny-rule would have to carve an exemption for it.

- **D-11:** **In Phase 133 the unlock reaches the chip only via the registry drain — it is not a derived plan step — and `OP_SDP_UNLOCK` is kept out of `_DESTRUCTIVE_OPS` anyway, asserted as a standing invariant.** Both of criterion 3's tests are then satisfied by registry behavior: gate-closed-from-the-start ⇒ `sdp_lock` is SKIPPED ⇒ nothing registers ⇒ `sdp_unlock` is never attempted (nothing was locked); lock-ran-then-the-gate-closes ⇒ the unlock is registered ⇒ the drain still runs it. The `_DESTRUCTIVE_OPS` absence is **forward-protection for Phase 134**, where the unlock becomes step 4 of the derived leg, and the phase record must say so rather than implying the absence gates a live 133 path. Rejected: making the unlock both a plan step and registry-registered now, with an idempotence guard (matches 134's end state so 134 adds no new path, but needs a guard so a successful step-4 unlock does not fire twice — harmless on this family, but it double-counts in the report and inflates the endurance notice); and plan-step-only, dropping the registry for the unlock (simplest reading of criterion 3 and makes `_DESTRUCTIVE_OPS` absence directly load-bearing, but it reintroduces the exact P-20 hazard the phase exists to close — a step that never runs because the loop unwound leaves the part locked, which LEG-10 forbids).

### Claude's Discretion

Two areas the operator delegated. Both are grounded in this session's measurements, and each records why.

- **D-12:** **The LEG-15 parity test polices every row of P-23's table in Phase 133, via a committed exemption table that requires a non-empty reason string per `(op, registry)` pair.** For each op string in `chip_test.py`'s `OP_*` constants, the test asserts membership **or** an explicit exemption, and it fails when a pair is neither. In this phase `OP_SDP_LOCK` / `OP_SDP_UNLOCK` carry exemptions for the Phase-134 surfaces (`derive_plan` step construction, `count_applicable`/`_RAN_VERDICTS`, `dedup_fingerprint`, the `diagnostic_report.py` renderer, `_ALWAYS_WRITES_NOTICE`) each reading "Phase 134 surface — not derived as a plan step in 133", and `_MULTI_RUN_OPS` carries D-03's exclusion reason. Three guards make this fail **closed** rather than becoming the eighth fail-open registry: (a) an exemption with an empty or missing reason fails; (b) a **stale-row assertion** fails when the table names an `(op, registry)` pair that no longer exists — otherwise a Phase 134 rename leaves a dead exemption silently permitting an omission; (c) the number of registries policed is asserted equal to a declared constant, so adding an eleventh registry without policing it fails. Rejected: scoping the test to only the three `chip_test.py`-local registries (smaller and fully green, but it leaves the five fail-open registries that P-23 exists to close untouched, and LEG-15's text says *"all required registries"*); and authoring the full test now and accepting it RED until Phase 134 (this project's own record is that a pre-authored gate leg proves nothing until it is *seen to pass*, and a RED gate carried across a phase boundary gets force-proceeded). Naming follows the house: `tests/test_op_registration_parity.py`, alongside `test_revision_constants_parity.py` and `test_sdp_table_parity.py`, and it should carry a non-vacuity leg in the shape of `test_sdp_table_parity.py:301`'s `test_altered_temp_copy_fails_parity_non_vacuous`. **Verify P-23's row 8 first** — measured this session, `tools/parse_devtest_issue.py` has no op vocabulary to police (correction 2 above).

- **D-13:** **Criterion 4's no-op regression test asserts behavior, not diff-emptiness.** Two legs. (a) For a representative non-SDP chip, assert the exact derived op sequence and the exact per-step `(verdict, run_count)` list against an **in-test literal** — not a syrupy snapshot, because syrupy 5.5.3 fails the whole session on unused snapshots and Phase 132 D-13 already documented that trap. (b) Monkeypatch `_dispatch_sdp` to raise, then run each of the seven shipped op strings through `_dispatch_step` and assert none of them reaches it — which is the mechanical proof of D-04's "the new membership test is never evaluated" and therefore of "zero added branching cost". Rejected: an empty-`git diff` or byte-identical-file criterion — this project has already been bitten by exactly that, because such a criterion breaks the moment a later phase adds a guard to the same file, and Phase 134 certainly will. Scope any file-level claim to *assertions-unchanged*, or name blob SHAs, never "the file did not change".

### Settled at plan time (operator, 2026-08-04)

Three questions the researcher raised. The first is a **new finding**, not a re-litigation: it changes
what D-09 requires. All three are operator answers, taken as locked.

- **D-14:** **The `chip_test.py:1035` broad-except is exempted via a committed exemption table.** Measured by research: `_sample` already contains `except Exception:` and its `# noqa: BLE001` is **inert** (ruff `select` is `["E","F","I","UP"]`, so `BLE` is off; `except:` is caught by E722, `except Exception:`/`except BaseException:` by nothing). D-09's new deny-rule therefore fires RED on clean pre-existing source unless exempted — a fact CONTEXT.md did not record and D-09 did not anticipate. The exemption is a `(file, function) → reason` table in `tools/check_devtest_orchestrator.py`, with **guard (a)** an empty/missing reason fails and **guard (b)** a stale row (the exempted function no longer exists — e.g. `_sample` renamed) fails. This shares its idiom with D-12's parity table, so the phase introduces **one** new concept, not two. Rejected: a declared-count watermark in the house mypy shape (cheaper and house-consistent, but records no reason and binds to no location — a *different* broad-except added while `_sample`'s is removed keeps the count at 1 and passes); and narrowing `_sample`'s catch, which research ruled out against criterion 4 because `_make_sampler` is live in production and swallow-all is its documented contract.

- **D-15:** **The LEG-09/10/11 + D-13 behavioral tests live in a new `tests/test_chip_test_sdp_leg.py`.** Isolation and explicit file-count accounting; the SDP leg is auditable as a unit. **Stated cost:** this plus `tests/test_op_registration_parity.py` consumes **both** slots of the measured `checked 122 source files` vs `MIN_CHECKED_SOURCE_FILES = 120` margin, exactly. Rejected: appending to `test_chip_test.py` (zero new source files, leaves both margin slots free, but the module is already 1958 lines with 20 `run_plan` call sites and the leg becomes un-auditable as a unit).

- **D-16:** **A failed unlock is proven by test-observability only in Phase 133, and the residual is written down.** Measured: `chip_test.py` has **no logger and no `logging` import**, `exc.add_note()` is 3.11+ against a 3.9 floor, and appending the attempt into `results` would detonate seven consumers at `cli_handlers.py:2161-2216` in Phase 134 (`count_applicable` would render "8 of 7 ran"). Criteria 1 and 3 only ask *was the unlock attempted?*, which is answerable on the operator double. **Honest residual, to be stated plainly in the phase record and not smoothed over:** a failed unlock is **not user-visible** until Phase 134's `HELD`/`NOT-RUN` field (LEG-12). This is the second residual D-07 creates. Rejected: giving `chip_test.py` a logger now — a new output surface in the module app `CLAUDE.md` describes as the bench-free pure-compute engine that emits nothing, and Phase 134 would then inherit two recording paths.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

`ROADMAP.md` carries no `Canonical refs:` line for this phase; this list is accumulated from the
ROADMAP entry body, `REQUIREMENTS.md`, the research spine, and this session's codebase scout.

### Milestone contract (read first)
- `.planning/REQUIREMENTS.md` §"The `dev test` SDP Leg — the Oracle (LEG)" (lines 186–247) — **LEG-09
  (`:216`), LEG-10 (`:219`), LEG-11 (`:222`), LEG-15 (`:235`) are this phase's four and the only four**;
  the other 14 LEG requirements belong to Phase 134.
- `.planning/REQUIREMENTS.md` §"⚠ Evidence Ceiling" (lines 14–40) — must not be smoothed over in any
  artifact. Load-bearing here: **a locked die is unrepresentable in either repo's stubs**, so no test in
  this phase can simulate inhibition; fixtures pin the host's *response* to a scripted read-back only.
- `.planning/REQUIREMENTS.md` §Out-of-Scope, the `eprom_operations.py` ring-fence row — operator
  decision 2026-08-03 → `FUT-MYPY-02`. Do not reopen.
- `.planning/ROADMAP.md` §"Phase 133: SDP Leg Mechanism" — the goal, the 5 success criteria, and the
  cross-cutting rule to **name at dispatch exactly which of LEG-09/10/11/15 each plan may mark
  Complete** (executors did this prematurely 4× in Phase 116).
- `.planning/ROADMAP.md` §"Phase 134: The Plan-Derived SDP Oracle in `dev test`" — read for the
  **boundary**, not the work. Its "Depends on" line names this phase's three deliverables verbatim:
  the cleanup registry, widened exception handling, and the `_SDP_OPS` dispatch arm.

### The research spine — cite by P-number, never by phase number
- `.planning/research/PITFALLS.md` §**P-20** (line 702, CRITICAL/safety) — the abort-between-lock-and-
  unlock hazard. Preventions **1 and 2** are this phase (LEG-09/LEG-10); **3 (baseline gate) and 4
  (report wording) are Phase 134's**. ⚠ its `run_plan` anchor `:757-802` has drifted to `:709-794`.
- `.planning/research/PITFALLS.md` §**P-23** (line 786) — the ten-registry table LEG-15 is built from.
  ⚠ **row 8 (`parse_devtest_issue.py`) is corrected by this session's measurement** — no op vocabulary
  exists there. ⚠ `_MULTI_RUN_OPS :657` → `:654`; `_dispatch_step :903-948` → `:901-952`.
- `.planning/research/PITFALLS.md` §**P-07** (line 287) — the orchestrator gate's scanning gap.
  **Narrowed by measurement:** its deny-visitor AST-walks all of `chip_test.py`, so a `_dispatch_sdp`
  there *is* scanned; the gap is specific to `cli_handlers.py` helpers via `_HANDLER_FUNCTION_NAMES`
  (`:138-151`), which this phase does not add to.
- `.planning/research/PITFALLS.md` §**P-08** (line 317) — why `_ALWAYS_WRITES_NOTICE` is Phase 134's and
  not this phase's. §**P-06** (line 255) — emission-claim-vs-state-claim, the reasoning behind D-03.
  §**P-14** (line 545) — which fail-open idioms exist here today and which a new gate would inherit.
  §**P-24** (line 812) — the premature-Complete behaviour the cross-cutting rule guards against.
- `.planning/research/SUMMARY.md` — ⚠ **its §"Phase 133" (line 726) is the ORACLE, i.e. ROADMAP Phase
  134.** Do not use its phase headings for scope.

### The immediate predecessor (its outputs are this phase's inputs)
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CONTEXT.md` — D-01…D-14. Load-bearing
  here: **D-10** (the typed `make_app_context` factory + `app_context` fixture this phase's new test
  module builds on), **D-09** (why the watermark stays at 35 and what the measured count means),
  **D-13** (the syrupy unused-snapshot trap D-13 above avoids), **D-02** (`sdp_honesty.py` as a forward
  contract — Phase 134 calls it, this phase does not).
- `.planning/phases/132-retire-dev-sdp-discharge-the-mypy-debt/132-CI-GREEN.md` — the certifying line
  **`mypy errors: 32 (watermark: 35)`** (`:88`) and **`checked 122 source files`**. Read verbatim; this
  is the headroom this phase spends against.
- `.planning/phases/131-gate-hardening-ci-parity/131-CI-PARITY.md` and
  `firestarter_app/tools/ci_parity.sh` — the four-leg recipe. The ROADMAP's cross-cutting rule for this
  phase says to run it **with the no-board leg emphasized**, because this phase's exception handling is
  exactly what a half-seated cable exercises.
- `firestarter_app/tools/ci_replica_venv.sh` (Phase 132 D-07) — the numpy-free venv needed to obtain a
  real mypy count locally; the devcontainer's own run exits 2 against `numpy 2.5.1` and cannot produce
  one.

### Live code this phase edits or must not break
- `firestarter_app/firestarter/chip_test.py` — 1253 lines. Op constants **`:289-295`** (seven strings);
  `Step` **`:298`**; `_DESTRUCTIVE_OPS` **`:636`**; `_MULTI_RUN_OPS` **`:654`**;
  `_DESTRUCTIVE_GATE_REASON` **`:656`**; `StepResult` **`:661`**; `run_plan` **`:709-794`** (flat loop,
  gate check at `:784`, no `finally`); `_id_step_closes_gate` **`:797`**; `_run_step` **`:863-898`**
  (`except EpromOperationError` at `:887`); `_dispatch_step` **`:901-952`** (four arms, terminal
  fail-closed `return` at `:944`); `_dispatch_multi_run` **`:1039`** (its `_MULTI_RUN_OPS` guard
  `:1082-1093`, the deliberate `AssertionError` **`:1130`**); `_RAN_VERDICTS` **`:1209`**;
  `count_applicable` **`:1229`**.
- `firestarter_app/firestarter/exceptions.py` — `SerialError` **`:13`**, `SerialTimeoutError` **`:19`**,
  `ProgrammerNotFoundError` **`:25`**, `FirmwareOutdatedError` **`:31`**, `EpromOperationError`
  **`:37`**, `HardwareOperationError` **`:69`** (a sibling of `Exception`, **not** an
  `EpromOperationError`). D-08's whole basis.
- `firestarter_app/firestarter/eprom_operations.py` — `sdp_unlock` **`:1736`**, `sdp_lock` **`:1784`**.
  **Ring-fenced** — call and reference, never type-fix.
- `firestarter_app/firestarter/cli_handlers.py` — `dev_test` **`:2085`**; `_ALWAYS_WRITES_NOTICE`
  **`:2071`** (not edited, see boundary); `derive_plan` call **`:2138`**; **`run_plan` call `:2164`** and
  `count_applicable` call `:2166` — the two lines D-07 turns on.
- `firestarter_app/tools/check_devtest_orchestrator.py` — `_OrchestratorDenyVisitor` **`:196`**,
  `FIRESTARTER_DEVTEST_SRC` seam **`:86`**, `_HANDLER_FUNCTION_NAMES` **`:138`**. D-09 adds one visitor
  method here.
- `firestarter_app/tests/conftest.py` — `make_app_context(...) -> AppContext` **`:229-237`**,
  `app_context` fixture **`:325`** (Phase 132 D-10, landed). Also carries `build_frame`, `_FakeSerial`,
  `make_comm`.
- `firestarter_app/tests/test_chip_test.py` — 1958 lines, 10 `run_plan` call sites. The blast radius
  D-07 declined to take on.
- `firestarter_app/pyproject.toml` — `[tool.mypy]` global is lenient (`check_untyped_defs = false`
  **`:—`**); the watermark comment **`:159`**; the six-module test strict-island and the nine-module
  production strict-island (`chip_test` is in **neither**).

### Pattern precedents to copy
- `firestarter_app/tests/test_sdp_table_parity.py` — the house parity-test shape D-12 follows,
  including `test_altered_temp_copy_fails_parity_non_vacuous` **`:301`** and
  `test_missing_override_path_fails_closed` **`:349`**.
- `firestarter_app/tests/test_revision_constants_parity.py` — the other parity precedent; also in the
  test strict-island.
- `firestarter_app/tests/test_check_devtest_orchestrator.py` — 18 tests; the paired-test convention
  D-09's new deny-rule extends.
- `firestarter_app/tests/test_skip_census.py` — `ALLOWED_SKIP_REASONS` fails **closed** on any new skip
  reason. This phase should need **no** new skip reason; if a fix wants one, re-examine the fix.

### Milestone design intent (background, not a spec)
- `.planning/notes/sdp-surface-retirement-and-behavioral-proof.md` — Trap 3 is P-20's origin. ⚠ its line
  numbers are superseded.
- `.planning/notes/dev-test-design-decisions.md` — the `dev test` engine's own decision record
  (`Step`/`Plan`/`run_plan` shape, the destructive gate, the N-of-M banner).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`_dispatch_multi_run`'s guard→branch→terminal-`AssertionError` shape** (`:1082-1093`, `:1130`) — D-01
  clones it structurally. The module already proves this shape fails closed; nothing new to argue.
- **`tests/conftest.py`'s typed `make_app_context` + `app_context`** (Phase 132 D-10) — the new test
  module's fixture base. No new factory needed.
- **`tools/check_devtest_orchestrator.py`'s AST visitor + env-override seam + 18-test paired module** —
  D-09 extends this rather than adding a tool.
- **`tests/test_sdp_table_parity.py`'s non-vacuity and fails-closed legs** — D-12's structural template.
- **`tools/ci_parity.sh` (four legs, aggregate exit, board stamping) and `tools/ci_replica_venv.sh`** —
  the pre/post recipe and the only local path to a real mypy count.

### Established Patterns
- **Fail-closed dispatch with an explicit terminal refusal**, not a bare `else`. The pre-Phase-121 shape
  routed any unmapped op to `erase_eprom()` and reported OK. Every new arm inherits the refusal.
- **Module constants, never DB fields, for anything that widens a blast radius** (`_WRITE_REGION_LENGTH`
  / `_UV_WRITE_REGION_LENGTH`, SC4). `_SDP_OPS` is a module frozenset for the same reason.
- **Explicit non-glob target lists in every `tools/check_*.py`** — the property that makes the gates
  honest is the property that makes them brittle to a rename. Any new target list must resolve locally
  and be *proven* to (`_HERE` mis-resolution silently scanned nothing on v1.23's only outward gate).
- **Import-time binding is pervasive and treacherous** — `FW_ROOT`, `FW_REPO_PRESENT`, `_BOARD_CHOICES`,
  `channel.is_prerelease_build()` freeze at import/collection; `monkeypatch.setenv` runs after and has
  no effect. Anything simulating a different environment needs a subprocess.
- **A pre-authored gate leg proves nothing until it is seen to pass.** D-12's whole shape follows from
  this.

### Integration Points
- **`cli_handlers.py:2161-2163`** is the only production consumer of `run_plan`'s return value. D-07's
  honest residual lives exactly here.
- **`_SDP_OPS` + `_dispatch_sdp` become Phase 134's foundation** — ROADMAP 134's "Depends on" names them.
  Their signatures are a **forward contract**, not an internal detail.
- **`sdp_honesty.py` (Phase 132 D-02)** is the caveat carrier Phase 134's report rows will call. This
  phase renders nothing, so it does not touch it — but must not break its import surface.

### Measured live this session (re-verify at plan time; do NOT inherit)
- `firestarter_app` is on **`gsd/v1.30-sdp-surface-retirement`** @ `42a1971`. **The meta repo is on
  `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`** — the branch names deliberately diverge;
  check out the submodule's milestone branch before dispatching executors.
- **mypy headroom is 3.** `mypy errors: 32 (watermark: 35)`. `chip_test.py` is in neither strict island
  and the global has `check_untyped_defs = false`, so a plain new test module should contribute **0** —
  but measure with `tools/ci_replica_venv.sh` before committing, never assume.
- **`checked 122 source files` against `MIN_CHECKED_SOURCE_FILES = 120`** (Phase 131 D-05) → 2 slots.
  This phase **adds** files (a test module, possibly nothing else), so the floor rises rather than falls.
- **84 test files** in `tests/`. ⚠ **`.planning/codebase/TESTING.md` is severely stale** — it asserts
  "The project has **no Python unit tests**" and references `/home/henrik/dev/...` paths. Do not use it;
  the `plan:pre` drift gate is non-blocking and will not stop a planner from believing it.
- **7 shipped op strings**, `chip_test.py:289-295`. This is the set D-13's sentinel test enumerates.
- `tools/parse_devtest_issue.py` contains **no** op-string constants (correction 2).

</code_context>

<specifics>
## Specific Ideas

- **This phase's durable value, stated for the record:** it is the phase that makes it *safe* to add a
  lock to a community member's chip. Nothing it ships is user-visible; everything it ships is what
  stops Phase 134's leg from stranding a locked part on a stranger's bench. Plan it around the safety
  mechanism and the fail-closed gate, not around "wire up two op strings".
- **The two criteria most likely to be quietly mis-satisfied are 4 and 5.** Criterion 4 because D-05
  makes its `group=None` wording vacuous, and the temptation is to restate it as though tested — the
  record must say the intent was met by a different mechanism. Criterion 5 because an exemption table is
  the classic way a fail-closed gate becomes fail-open; D-12's three guards (mandatory reason, stale-row
  assertion, declared-count assertion) exist for that and should be treated as acceptance criteria in
  their own right, not implementation detail.
- **Say the split out loud in the phase record:** this phase proves the *mechanism* cannot strand a
  chip or lose a report, and that the registries fail closed. It proves **nothing** about SDP behaviour
  on silicon. `0x0D` stays `UNVERIFIED`, no AT28C part has ever been in operator inventory, and a locked
  die is unrepresentable in either repo's stubs — so no test here can simulate inhibition.
- **Run the CI-parity recipe with the no-board leg emphasized**, before and after. D-08 is precisely the
  no-board / half-seated-cable code path, so the no-board leg is this phase's most relevant local proof.
- **At dispatch, name the allowed requirement IDs per plan.** LEG-09, LEG-10, LEG-11, LEG-15 — and
  explicitly *not* any of the other 14 LEG requirements. This project's executors have marked multi-plan
  requirements Complete prematurely 4× in one phase.

</specifics>

<deferred>
## Deferred Ideas

- **The four-step leg itself** — derivation from `sdp_capability()`, the baseline transition write, the
  inhibited-write generator, the read-back oracle, the degenerate-read-back arms. **Phase 134**
  (LEG-01…08).
- **Every report surface** — the `HELD`/`NOT-HELD`/`NOT-RUN` field, the N-of-M applicable-step change,
  the "rewrite"-not-"erase" recovery wording and its grep, `dedup_fingerprint`, the
  `diagnostic_report.py` renderer, and the `_ALWAYS_WRITES_NOTICE` write-count correction. **Phase 134**
  (LEG-12/13/14) — and the five exemption rows D-12 writes are exactly what 134 discharges.
- **gh#20 triage** (AT28C256 `dev test` FAIL, open since 2026-07-30) — the live instance of the "lock a
  part whose baseline write never worked" hazard. **Phase 134** (LEG-18).
- **`write --sdp-relock`** — deferred to **Backlog 999.28** by operator decision 2026-08-03; the pending
  todo `write-sdp-relock-deferred.md` tracks it and its stale "v1.23+" label.
- **Adding `tests/test_op_registration_parity.py` to the mypy test strict-island** — the Phase 132 D-02
  "strengthen from birth" precedent argues for it, but with only 3 slots of watermark headroom this
  phase should measure first and not spend headroom on a strengthening it was not asked for. Cheap for
  whichever later phase ratchets the watermark.
- **Ratcheting the watermark to the measured 32** — Phase 132 D-09 recorded the number without setting
  it, and flagged that it needs a named owner or it becomes another acknowledgement. Still unowned.
- **Refreshing `.planning/codebase/TESTING.md`** — stale by ~84 test files and pointing at a foreign
  filesystem path. A map-refresh task (`/gsd-map-codebase`), not this phase's work, but it will mislead
  any agent that reads it in the meantime.

### Reviewed Todos (not folded)

`todo.match-phase 133` returned **14 pending, 12 matches; none folded.** Ten are keyword noise against a
host-only engine-hardening phase — four firmware/hardware items (`skip-vpp-error-and-warning-checks…`,
`prove-pio-dev-flag-fails-closed`, `cobs-decoder-framelevel-deadline-wr01`,
`avrdude-mcu-detection-fallback`), three bench/board items (`photograph-modified-rev-0`,
`fix-jp4-labels-and-rev2-revision-block`, `write-modifications-md-rework-trace`), and three low-score
adjacents (`decode-infoic-flags-bits-14-15-protect-metadata` — a `build_db.py` emitter change, not a
host-surface one; `delete-jp5-dead-renderer`; `fold-response-code-into-log-macro`), all matching on
generic tokens like "phase", "chip", "gate", "block".

The two substantive hits are both owned elsewhere by requirement: **`gh12-followup-after-dev-sdp-retirement`**
belongs to Phase 136/137's close behind a blocking operator wording-review gate, and
**`write-sdp-relock-deferred`** is Backlog 999.28 by operator decision. Neither is foldable into a phase
that renders no user-facing output and publishes nothing.

</deferred>

---

*Phase: 133-SDP Leg Mechanism*
*Context gathered: 2026-08-04*
