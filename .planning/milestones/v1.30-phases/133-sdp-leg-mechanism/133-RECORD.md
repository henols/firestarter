# Phase 133 Record — SDP Leg Mechanism

**Closing record for Phase 133.** Six mandatory sections: requirement accounting, decision coverage
for D-01…D-16, the five ROADMAP success criteria discharged with named evidence, corrections carried
forward, residuals, and the Evidence Ceiling stated plainly. Every measured figure below is traced to
a named plan SUMMARY, `133-BASELINE.md`, or `133-CI-PARITY.md` — nothing here was measured for the
first time in this document.

---

## 1. Requirement accounting

Four requirements only — LEG-09, LEG-10, LEG-11, LEG-15 — are this phase's, and this plan (133-07) is
the only plan in the phase permitted to tick any of them.

### LEG-09

> **LEG-09**: `sdp_unlock` is **exempt** from the destructive-op set, so a destructive gate closing
> after the lock can never skip the unlock and ship a locked part.

**Delivered by:** 133-03 (the `_DESTRUCTIVE_OPS` asymmetry — `OP_SDP_LOCK` joins the frozenset,
`OP_SDP_UNLOCK` is deliberately kept out) + 133-04 (criterion 3's two behavioural proofs, which need
the cleanup registry 133-03 alone could not provide).

**Green tests (`pytest -k` selectors):**
- `tests/test_chip_test_sdp_leg.py::test_unlock_exempt_from_destructive` (133-03 — the standing
  `_DESTRUCTIVE_OPS` invariant)
- `tests/test_chip_test_sdp_leg.py::test_gate_closed_from_start` (133-04 — with an OPEN-gate
  non-vacuity mirror)
- `tests/test_chip_test_sdp_leg.py::test_lock_ran_then_gate_closes` (133-04 — mutation-proved: adding
  `OP_SDP_UNLOCK` to `_DESTRUCTIVE_OPS` was observed to fail this exact test)

**Qualifier:** D-11 — in Phase 133 the unlock reaches the chip **only** via the registry drain, never
as a derived plan step, so `OP_SDP_UNLOCK`'s absence from `_DESTRUCTIVE_OPS` is **forward-protection
for Phase 134** (where the unlock becomes step 4 of the derived leg), not a live gate on a Phase 133
path. See §3 Criterion 3 below.

### LEG-10

> **LEG-10**: `run_plan` drains a cleanup registry in a `finally`, so the unlock is attempted even
> when a mid-leg step raises.

**Delivered by:** 133-04 in full — the generic `cleanup: list[Callable[[], None]]` registry, the bare
`try/finally` (zero `except` clauses) around the whole step loop, the registration site (an
`OP_SDP_LOCK` step whose verdict is OK), and the per-callable narrow-except drain wrapper.

**Green tests:**
- `tests/test_chip_test_sdp_leg.py::test_finally_drains_on_exception`
- `tests/test_chip_test_sdp_leg.py::test_keyboard_interrupt_drains_and_propagates`
- `tests/test_chip_test_sdp_leg.py::test_system_exit_drains_and_propagates`
- `tests/test_chip_test_sdp_leg.py::test_empty_registry_noop`
- `tests/test_chip_test_sdp_leg.py::test_drain_continues_after_failure`
- `tests/test_chip_test_sdp_leg.py::test_drain_does_not_mutate_results` (AST-level, over the
  installed source — the drain provably never references `results`)

**Qualifier:** D-07 — on the path where the drain runs because an exception is propagating
(`KeyboardInterrupt`/`SystemExit` included), the unlock is *attempted*, but the production caller's
`results = run_plan(...)` assignment (`cli_handlers.py:2161`) never completes, so **the report is
honestly forfeited**. See §3 Criterion 1 below.

### LEG-11

> **LEG-11**: `_run_step` catches `SerialError` and `HardwareOperationError`, so a mid-leg transport
> timeout degrades that step rather than killing the whole report.

**Delivered by:** 133-02 (the implementation — `_run_step` widened to four ordered `except` clauses,
re-raising `ProgrammerNotFoundError`/`FirmwareOutdatedError` first, degrading
`SerialError`/`HardwareOperationError` second — plus four behavioural proofs) **and** 133-05 (the
second, independent proof: a build-time AST gate that denies any bare/broad `except` from ever being
reintroduced).

**Green tests:**
- `tests/test_chip_test_sdp_leg.py::test_serial_timeout_degrades_one_step`
- `tests/test_chip_test_sdp_leg.py::test_hardware_error_degrades_one_step`
- `tests/test_chip_test_sdp_leg.py::test_run_fatal_escapes` (parametrised over both run-fatal
  classes, plus the `SerialError.__subclasses__()` standing-census invariant)
- `tests/test_chip_test_sdp_leg.py::test_assertion_error_propagates`
- `tests/test_check_devtest_orchestrator.py::test_checker_exits_nonzero_on_planted_broad_except` (and
  its three parametrised variants) — the independent build-time proof that no broad catch can be
  reintroduced without the gate catching it

**Qualifier:** D-08 — `ProgrammerNotFoundError`/`FirmwareOutdatedError` are deliberately **re-raised**,
not degraded (they are host-setup-fatal, not chip-fault conditions); only `SerialError`/
`HardwareOperationError` degrade. Research assumption A2 (a `SerialError` unreachable from the
resolver, so `_run_step`'s resolve half stays outside the `try`) is a residual — see §5.

### LEG-15

> **LEG-15**: An op-registration parity test proves every new op is registered in all required
> registries — converting **eight** fail-open registries into one fail-closed gate.

**Delivered by:** 133-06 in full — `tests/test_op_registration_parity.py`, the phase's second and
final new source file.

**Green tests:**
- `tests/test_op_registration_parity.py::test_every_op_is_registered_or_exempt` (the main leg)
- `tests/test_op_registration_parity.py::test_declared_registry_count_matches` (guard c)
- `tests/test_op_registration_parity.py::test_exemption_empty_reason_fails` (guard a)
- `tests/test_op_registration_parity.py::test_stale_row_fails` (guard b)
- `tests/test_op_registration_parity.py::test_non_registry_still_has_no_ops` (the inversion guard)
- `tests/test_op_registration_parity.py::test_altered_registry_copy_fails_parity_non_vacuous` (the
  non-vacuity leg)

**Qualifier — mandatory correction:** the requirement's own inherited "eight" is measured-wrong. See
§3 Criterion 5 for the full measured breakdown (6 policed registries + 6 declared non-registries).

### No other LEG requirement was touched

`.planning/REQUIREMENTS.md`'s other **fourteen** LEG rows belong to Phase 134 and remain `[ ]`,
byte-unchanged in text, untouched by this plan: **LEG-01, LEG-02, LEG-03, LEG-04, LEG-05, LEG-06,
LEG-07, LEG-08, LEG-12, LEG-13, LEG-14, LEG-16, LEG-17, LEG-18.** A later reader can verify this
directly — `git diff -- .planning/REQUIREMENTS.md` for this plan's own commit touches only the four
LEG-09/10/11/15 lines (checkbox + appended `Evidence:` clause), nothing else in the file: no other
checkbox, no requirement text, no section heading.

---

## 2. Decision coverage, D-01 … D-16

One row per decision from `133-CONTEXT.md`. Non-literal or refined honourings are flagged explicitly,
not smoothed over.

| ID | Honoured how | Evidence |
|---|---|---|
| D-01 | **Literal.** One guarded `_dispatch_sdp(op, name, eprom_data, operator)`, structurally cloning `_dispatch_multi_run`'s guard → branch → terminal-`AssertionError` shape. | 133-03; `inspect.signature(_dispatch_sdp)` confirms the four-positional-param forward contract. |
| D-02 | **Literal.** Exactly two op strings, `OP_SDP_LOCK = "sdp-lock"` and `OP_SDP_UNLOCK = "sdp-unlock"`. | 133-03. |
| D-03 | **Literal.** Both SDP ops explicitly excluded from `_MULTI_RUN_OPS`, reasoned in-source; the exclusion is one of 133-06's asserted parity exemptions. | 133-03 (exclusion), 133-06 (parity exemption row). |
| D-04 | **Literal.** `_dispatch_sdp`'s arm is last in `_dispatch_step`, immediately above the terminal fail-closed `return`; mutation-proved (arm moved above `OP_ID` under a widened `_SDP_OPS` made the sentinel fail with the expected message). | 133-03, `test_shipped_ops_never_reach_sdp_arm`. |
| **D-05** | **Honoured non-literally — vacuous by design, and the record says so plainly.** No `Step.group` field exists; the arm keys on `_SDP_OPS` membership of the op string itself. ROADMAP criterion 4's `group=None` clause is therefore satisfied **vacuously** — see §3 Criterion 4. The record does not restate the criterion's literal words as though they were tested. | 133-03; §3 below. |
| D-06 | **Literal.** A **generic** cleanup registry — a `list` of callables drained in one `try/finally` around the whole step loop, not a hardcoded lock-to-unlock window. An empty registry is a proven no-op for every currently-shipping run (mutation-proved: `test_empty_registry_noop`). | 133-04. |
| **D-07** | **Honoured non-literally.** "The unlock attempt is recorded on the exception (or logged)" was **not** implemented as a literal recorder — see the D-10/D-16 reconciliation below. `KeyboardInterrupt`/`SystemExit` propagate unchanged, and on that path **the report is honestly forfeited**: the production caller's `results = run_plan(...)` assignment (`cli_handlers.py:2161`) never completes, so there is no `dev test` report to render after a Ctrl-C mid-leg. This is one of the three residuals carried in §5. | 133-04; `test_keyboard_interrupt_drains_and_propagates`, `test_system_exit_drains_and_propagates`. |
| D-08 | **Literal.** `_run_step` re-raises `ProgrammerNotFoundError`/`FirmwareOutdatedError` **first**, then degrades `SerialError`/`HardwareOperationError` to a BAD step. | 133-02. |
| D-09 | **Literal.** No-bare-except proven two independent ways: behavioural tests (criteria 1/2) plus a new build-time deny-rule in `tools/check_devtest_orchestrator.py`. | 133-02 (behavioural), 133-05 (gate). |
| **D-10** | **Honoured non-literally — see the reconciliation below.** Each cleanup callable is wrapped in its own `try/except _UNLOCK_CLEANUP_SWALLOWED`, and the drain continues past a caught failure — but "recorded as a failed-unlock attempt" landed as test-observability only (the operator double's call assertions), not an in-module recorder. | 133-04. |
| D-11 | **Literal, with the qualifier stated where it belongs.** In Phase 133 the unlock reaches the chip only via the registry drain; `OP_SDP_UNLOCK` is kept out of `_DESTRUCTIVE_OPS` **as a standing invariant**, and the phase record states plainly that this absence is **forward-protection for Phase 134**, not a live gate on any Phase 133 path (133 derives no SDP step at all). **Also recorded here, as a plan-level derivation neither `133-CONTEXT.md` nor `133-RESEARCH.md` stated in so many words:** `OP_SDP_LOCK` was made a **member** of `_DESTRUCTIVE_OPS` while `OP_SDP_UNLOCK` was kept out — D-11's own mechanism *requires* this (gate-closed-from-the-start ⇒ `sdp_lock` SKIPPED is only reachable if a lock can be gated at all), and `_DESTRUCTIVE_OPS`'s own stated purpose ("ops that mutate the chip") requires it independently. Evidence: 133-03's asymmetry-setting commit + `test_unlock_exempt_from_destructive`'s standing invariant; 133-04's `test_gate_closed_from_start`/`test_lock_ran_then_gate_closes` exercise both halves of the mechanism this membership makes possible. | 133-03, 133-04. |
| **D-12** | **Refined by measurement, not honoured literally as scoped.** The LEG-15 parity test polices every `(op, registry)` pair via a committed exemption table requiring a non-empty reason string, exactly as decided — but the *declared registry count* was refined from P-23's inherited ten-row table into a measured **6 policed registries + 6 declared non-registries**, plus an **inversion guard** (re-measuring every declared non-registry's zero-op-vocabulary claim every run) that P-23's original census had no equivalent for. Three guards (empty/whitespace reason, stale row, declared-count mismatch) plus the inversion guard all fail closed, each mutation-proved. | 133-06; §3 Criterion 5 below. |
| D-13 | **Literal, two legs.** (a) The frozen `_SHIPPED_OPS_SEQUENCE` before-image (exact op sequence + per-step verdict/run_count), asserted against a real `derive_plan`+`run_plan` call, never a syrupy snapshot. (b) The seven-op sentinel, mutation-proved sensitive to arm *position* (not merely op-string disjointness) after a redesign — see §4 Corrections. | 133-01 (D-13a), 133-03 (D-13b). |
| D-14 | **Literal.** `chip_test.py:1035`'s (measured; anchor drifted to `:1273` by phase end) `_sample` broad-except is exempted via a committed `(basename, function) → reason` table, guarded on two independent axes (empty/whitespace reason; stale row). | 133-05. |
| D-15 | **Literal.** LEG-09/10/11 + D-13's behavioural tests live in a new `tests/test_chip_test_sdp_leg.py`, isolated from the 1958-line `test_chip_test.py`. Stated cost: this file plus `tests/test_op_registration_parity.py` spend **both** slots of the measured `checked 122` vs `MIN_CHECKED_SOURCE_FILES 120` margin — confirmed spent exactly, `133-CI-PARITY.md` §5. | 133-01, 133-06; `133-CI-PARITY.md` §5. |
| D-16 | **Literal, with the residual named.** A failed unlock is proven by test-observability only in Phase 133 (through the operator double's call assertions); the residual — not user-visible until Phase 134's `HELD`/`NOT-RUN` field (LEG-12) — is stated plainly, not smoothed over. See the reconciliation below and §5. | 133-04. |

**The D-10 / D-16 reconciliation, stated as its own item (per this plan's own instruction not to
smooth it over):** D-10 asks that a failed cleanup be "recorded"; **no in-module recorder was
created.** Why: `chip_test.py` has no logger and no `logging` import at all (the module is documented
as the bench-free pure-compute engine that emits nothing, and giving it a logger now would hand Phase
134 two recording paths instead of one); `exc.add_note()` is 3.11+ against this module's `>=3.9`
floor; the drain must not touch `results` (a finally-time append is visible to the caller by
reference and would detonate seven downstream consumers in `cli_handlers.py`, inflating the N-of-M
banner — mutation-proved in 133-04: planting an unconditional `results.append(...)` in the `finally`
made both `test_empty_registry_noop` and `test_drain_does_not_mutate_results` fail together); and a
local failure list read by nobody would be a dead surface of exactly the kind this module's own
history warns about (`_MULTI_RUN_OPS` once shipped with zero references tree-wide). Instead, the
attempt and its outcome are observable only through the operator double in Phase 133 — D-16's
explicit, deliberate choice, with the user-visibility gap closed only by Phase 134's `HELD`/`NOT-RUN`
field (LEG-12).

---

## 3. The five ROADMAP success criteria, discharged with named evidence

Quoted from `.planning/ROADMAP.md` §"Phase 133: SDP Leg Mechanism".

### Criterion 1

> A mid-leg step that raises still leaves `run_plan`'s cleanup registry to drain in a `finally` block
> — proven by a test that raises partway through a run and asserts the cleanup step still executed
> (including on `KeyboardInterrupt`/`SystemExit`, which a `finally` reaches and `atexit` would not).

**Evidence:** the bare `try/finally` (zero `except` clauses) wrapping `run_plan`'s whole step loop,
proven to drain on an ordinary raised exception (`test_finally_drains_on_exception`), on
`KeyboardInterrupt` (`test_keyboard_interrupt_drains_and_propagates`), and on `SystemExit`
(`test_system_exit_drains_and_propagates`) — all three (133-04).

**Honest caveat (D-07):** on the path where the drain runs because an exception is propagating, **the
report is honestly forfeited**. The production caller does `results = run_plan(...)`
(`cli_handlers.py:2161`) and builds the report from `results` immediately after
(`:2166`); a propagating exception means that assignment never completes, so after a Ctrl-C mid-leg
the chip has an unlock *attempted*, but the user sees **no `dev test` report at all**. This was a
measured constraint, not an oversight: fixing it would require changing `run_plan`'s signature and
every one of its 12 existing call sites, which is real blast radius against criterion 4's
"provably byte-identical in behavior" claim for the seven shipped ops.

### Criterion 2

> A `SerialError` or `HardwareOperationError` raised mid-step (e.g. a half-seated cable) degrades that
> one step to a recorded BAD result instead of propagating out of `run_plan` and killing the whole
> report — proven by a planted-fault test for each exception class, and proven that a bare
> `except Exception`/`BaseException` was **not** used (the deliberate `AssertionError` elsewhere in
> the module must still propagate loudly, and Ctrl-C must stay Ctrl-C).

**Evidence:** `test_serial_timeout_degrades_one_step` and `test_hardware_error_degrades_one_step`
(each degrades exactly one step, later steps still run OK); `test_run_fatal_escapes` (the two
run-fatal classes still escape by identity, with a standing `SerialError.__subclasses__()` census
invariant); `test_assertion_error_propagates` (the deliberate `AssertionError` still escapes — a
temporarily planted `except Exception` clause was observed to make this test fail before being
reverted). The build-time gate half: `tools/check_devtest_orchestrator.py`'s fourth deny bucket,
proven to fire on bare `except:`, `except Exception:`, `except BaseException:`, and tuple forms
containing either, across four parametrised RED demonstrations (133-05).

**Honest caveat:** bare `except:` was **already** gated by ruff's own `E722` rule before this phase
began — that part of the criterion is not new coverage. The phase's **genuinely new** coverage is
`except Exception:` / `except BaseException:` (neither of which ruff's configured `select =
["E","F","I","UP"]` catches — `BLE001` is off). The gate is GREEN on real, clean source only because
of **one** reasoned, guarded exemption for the pre-existing `_sample` sampler swallow (D-14), which
this deny-rule's own commit would otherwise turn RED on unrelated, unedited code.

### Criterion 3

> `sdp_unlock` is absent from `_DESTRUCTIVE_OPS`, proven by two tests: gate-closed-from-the-start ⇒
> `sdp_lock` is SKIPPED and `sdp_unlock` is never attempted (nothing was locked); lock-ran-then-the-
> gate-closes ⇒ `sdp_unlock` is STILL attempted.

**Evidence:** `test_gate_closed_from_start` (with an OPEN-gate non-vacuity mirror proving the test
would actually distinguish the two conditions) and `test_lock_ran_then_gate_closes` (mutation-proved:
temporarily adding `OP_SDP_UNLOCK` to `_DESTRUCTIVE_OPS` was observed to fail this test with the
exact reasoned message, then reverted) — both non-vacuously, not merely asserted (133-04).

**Honest caveat (D-11):** in Phase 133, `OP_SDP_UNLOCK`'s absence from `_DESTRUCTIVE_OPS` is
**forward-protection for Phase 134**, where the unlock becomes step 4 of the derived leg. **It does
not gate a live Phase 133 path** — this phase derives no SDP step at all (`derive_plan` is untaught
to emit them; that is Phase 134's LEG-01/02). Do not read this criterion as proving anything about a
plan-derived unlock in Phase 133; there is none to protect yet.

### Criterion 4

> Every existing, already-shipped `dev test` op is provably byte-identical in behavior after this
> phase lands — an op with `group=None` takes the exact pre-existing dispatch path, at zero added
> branching cost, proven by a no-op regression test.

**Evidence:** the frozen nine-row `_PRE_EDIT_PRECEDENCE_MATRIX` before-image (133-01) and the current
`_EXPECTED_PRECEDENCE_MATRIX`, with `_INTENDED_PRECEDENCE_DELTA` naming exactly the three rows that
legitimately changed (`SerialError`, `SerialTimeoutError`, `HardwareOperationError` — 133-02, criterion
2's own change); the frozen `_SHIPPED_OPS_SEQUENCE` op-sequence literal (133-01); and the seven-op
sentinel (`test_shipped_ops_never_reach_sdp_arm`), mutation-proved to fail under a deliberate
arm-reorder after a necessary redesign (see §4).

**Mandatory caveat, stated plainly:** the criterion's clause *"an op with `group=None` takes the
exact pre-existing dispatch path"* is satisfied **VACUOUSLY**. D-05 dropped the idea of a `Step.group`
field entirely — there is **no `group` field on `Step` at all**, so no op has, or could have,
`group=None`. This record states the criterion's *intent* — shipped ops behaviourally unchanged at
zero added branching cost — was met by a **different mechanism** (the op string's own membership in
`_SDP_OPS`, checked only after the seven shipped ops have already returned from earlier arms). **This
record does not, anywhere, restate the criterion's literal words as though `group=None` were
tested**, because it was not — there is nothing named `group` to test.

Also, per this project's own recorded criterion-shape hazard: any file-level claim here is scoped to
*assertions-and-behaviour unchanged for the seven shipped ops*, never to "the file did not change" —
`chip_test.py` changed substantially across this phase (new op constants, a new dispatch arm, a new
cleanup registry, widened exception handling). What is proved byte-identical is the **shipped ops'
observable behaviour and dispatch return points**, not the file's bytes.

### Criterion 5

> An op-registration parity test exists that fails if a new op string is added to the vocabulary but
> left out of any one of the registries a new op must join (the `_SDP_OPS` dispatch allow-list,
> destructive-set membership, multi-run exclusion, and the others enumerated in the module's own
> comment) — converting **eight** previously fail-open registries into one fail-closed gate.

**Evidence:** `tests/test_op_registration_parity.py`'s main leg
(`test_every_op_is_registered_or_exempt`), its four D-12 guards (`test_exemption_empty_reason_fails`,
`test_stale_row_fails`, `test_declared_registry_count_matches`, and the transitive stale-row/op-level
checks folded into the main leg), the inversion guard (`test_non_registry_still_has_no_ops`), and the
non-vacuity leg (`test_altered_registry_copy_fails_parity_non_vacuous` — a real frozenset narrowing
was observed to fail the gate with the exact reasoned message, then reverted) (133-06).

**Mandatory correction, stated plainly:** the criterion's (and LEG-15's own requirement text's)
"converting **eight** previously fail-open registries into one fail-closed gate" is a **measured-wrong
count**. Re-measured against the phase's final engine source (133-06), the real breakdown is:

**6 policed registries** (a new op must join one of these, or carry a reasoned exemption):
`_DESTRUCTIVE_OPS`, `_MULTI_RUN_OPS`, `_SDP_OPS` (all three real frozensets in `chip_test.py`), plus
three AST-derived function-scoped sites: `_dispatch_step` (needs zero exemptions — all nine ops
resolve into it), `derive_plan`, and `_dispatch_multi_run` (whose inner run-loop branches P-23's
original ten-row table **missed entirely** — this is one real policed registry *more* than P-23
counted, not fewer).

**6 declared non-registries** (zero op vocabulary, or keyed on a materially different axis):
`_RAN_VERDICTS`/`count_applicable` (verdict-keyed), `dedup_fingerprint` and the
`diagnostic_report.py` renderer (both generic over `StepResult.op`), `tools/parse_devtest_issue.py`
(measured to have **zero** op-string constants at all — corrects P-23's row 8, which is the phantom
row this phase's own research process flagged and 133-06 confirmed live), `_ALWAYS_WRITES_NOTICE`
(fixed prose, zero op vocabulary), and `check_devtest_orchestrator.py`'s `_HANDLER_FUNCTION_NAMES`
(keyed on function names, not op strings).

**The number was measured, not inherited.** "Eight" undercounts the real policed set by one
(`_dispatch_multi_run`'s inner branches were absent from P-23 entirely) **and** overcounts the
declared-non-registry set by miscategorising genuinely-empty or different-axis rows as "fail-open
registries" when there was never anything a new op could have been omitted from in the first place.

---

## 4. Corrections carried forward

Every place a measurement overturned a written record, both readings stated.

| # | Artifact measured wrong | Measured truth | How measured |
|---|---|---|---|
| 1 | Research's `PITFALLS.md` P-20 prevention #2 ("wide enough to catch `BaseException`") | **Unnecessary and self-defeating.** A bare `finally` (zero `except` clauses) suffices to reach `KeyboardInterrupt`/`SystemExit` while still letting them propagate; an `except BaseException:` clause would violate criterion 2 and trip this phase's own new deny-rule (133-05). | Design-time measurement, `133-CONTEXT.md`'s research-flag paragraph; confirmed by 133-04's implementation choice and 133-05's gate both agreeing. |
| 2 | `PITFALLS.md` P-23's ten-row registry table | Corrected two ways: row 8 (`tools/parse_devtest_issue.py`) has **zero** op-string constants — not a policeable registry at all; and `_dispatch_multi_run`'s inner run-loop branches were **missing from the table entirely** — a real policed registry P-23 never counted. Net real count: 6 policed + 6 declared non-registries, not P-23's ten. | `133-CONTEXT.md`'s "Three measured corrections" section (correction 2), re-verified live at 133-06 execution time via `_op_names_referenced_in`'s AST derivation. |
| 3 | `chip_test.py`'s `_sample` function's `# noqa: BLE001` comment | **Inert.** Ruff's configured `select` is `["E","F","I","UP"]`; `BLE` is not in it. Bare `except:` is caught by `E722`; `except Exception:`/`except BaseException:` are caught by nothing pre-133-05. | Measured by research, confirmed live at 133-05 plan time (D-14). |
| 4 | `_run_step`'s own docstring | Over-claimed wrapping "the ENTIRE step body (resolve + dispatch)" — measured, the resolve call (`_resolve_or_none`) sits **outside** the `try`, covered only by its own narrower two-class handler. Corrected in-source. | 133-02, live AST/docstring inspection. |
| 5 | Research's phase-number citations in `research/SUMMARY.md`/`PITFALLS.md` | Off by one against the ROADMAP's later split: `research/SUMMARY.md` §"Phase 133" (line 726) actually describes **Phase 134** (the oracle); `PITFALLS.md` P-20/P-23 say "Phase to address: 133" and correctly land here, but P-20's preventions 3/4 are Phase 134's. Also, line anchors drifted: `run_plan` `:757-802` → `:709-794`; `_MULTI_RUN_OPS` `:657` → `:654`; `_dispatch_step` `:903-948` → `:901-952`. | `133-CONTEXT.md`'s "Three measured corrections" (corrections 1 and 3), re-verified at each plan's own execution time against live source. |
| 6 | 133-03's own first-draft sentinel test (`test_shipped_ops_never_reach_sdp_arm`), as literally specified by the plan | **Vacuous as first written.** Mocking `_dispatch_sdp` and asserting not-called stayed green even with the arm deliberately moved to the wrong position, because the seven shipped op strings are never members of `_SDP_OPS` regardless of arm order — the as-specified test proved op-string disjointness, a materially weaker property than arm placement. Corrected: the test also monkeypatches `_SDP_OPS` to a widened frozenset containing every shipped op, making the sentinel genuinely sensitive to arm position. Re-run against the identical arm-reorder mutation: it now fails with the sentinel's own message. | 133-03-SUMMARY.md, "Decisions Made" and "Mutation Proofs". |
| 7 | The plan's own literal action text for the cleanup registration site (`cleanup.append(lambda: _run_step(...))`) | A real mypy `arg-type` mismatch: a `lambda` wrapping `_run_step(...)` infers `Callable[[], StepResult]`, which does not satisfy the registry's declared `Callable[[], None]` element type — raised the measured mypy count from 32 to 33 before the fix. Corrected to a nested `def _unlock_cleanup() -> None:` calling `_run_step(...)` as a bare statement; re-measured count returned to 32 (confirmed identical to 133-03's error set via a temporary `git worktree` diff). | 133-04-SUMMARY.md, "Decisions Made" and "Deviations from Plan". |
| 8 | ROADMAP criterion 4's `group=None` clause | **Vacuous by design (D-05), not an execution-time surprise** — recorded here as a correction to any reading of the criterion's literal words as a tested claim. See §3 Criterion 4. | `133-CONTEXT.md` D-05, confirmed by 133-03's implementation (no `Step.group` field exists anywhere in the module). |
| 9 | ROADMAP criterion 5's / LEG-15's "eight previously fail-open registries" | Measured-wrong; real breakdown is 6 policed + 6 declared non-registries. See §3 Criterion 5. | `133-06-SUMMARY.md`, "Measured Registry Census". |
| 10 | mypy count assumed stable across the phase (research assumption A1, "a new plain test module contributes 0 errors") | True for both new modules' own lines, but **not** a clean zero-delta overall: 133-06's import of `tools.check_devtest_orchestrator` made mypy reach that module for the first time, surfacing one pre-existing (133-05-introduced, never-before-reachable) type error. 32 → 33, still 2 under watermark. | `133-CI-PARITY.md` §4; `deferred-items.md`. |

---

## 5. Residuals, carried unresolved by design

Each with a named owner or a stated reason for having none.

1. **D-07's forfeited report.** After a Ctrl-C mid-leg, the chip has an unlock *attempted* but the
   user sees no `dev test` report at all — the production caller's `results = run_plan(...)`
   assignment never completes on a propagating exception. **No owner within this milestone.** Fixing
   it would require changing `run_plan`'s signature and all twelve of its call sites (ten in
   `tests/test_chip_test.py`, one in `tests/test_diagnostic_report.py`, one in production), which was
   explicitly rejected in `133-CONTEXT.md` D-07 as real blast radius against criterion 4. Not filed as
   a backlog item by this plan.

2. **D-16's failed unlock is not user-visible until Phase 134.** A failed unlock is proven by
   test-observability only in Phase 133 (the operator double's call assertions); nothing renders it to
   a human. **Owner: Phase 134**, via the `HELD`/`NOT-HELD`/`NOT-RUN` report field (LEG-12) — already
   named in the ROADMAP's Phase 134 entry as depending on this phase's mechanism.

3. **Research assumption A2** — a `SerialError` is not currently reachable from `_run_step`'s resolver
   half (`_resolve_or_none`), so that half stays outside the `try` and is covered only by its own
   narrower two-class handler. This is a latent-robustness gap, now **documented in the function's own
   docstring** (133-02) rather than contradicted by an over-claiming one. **No owner** — carried as a
   documented, understood gap, not filed as a backlog item.

4. **The still-unowned mypy watermark ratchet.** Phase 132 measured the true count at 32 (watermark
   35, 3 of headroom) and explicitly left the ratchet unfiled, requiring a named owner "or it becomes
   another acknowledgement" (`132-RECORD.md` residual 2). This phase's own measured count moved to 33
   (2 of headroom) and **still has no named owner** — carried forward as the same open item, now with
   one fewer error of headroom than Phase 132 left it.

5. **Neither new test module (`test_chip_test_sdp_leg.py`, `test_op_registration_parity.py`) was added
   to the mypy test strict-island.** The Phase 132 D-02 "strengthen from birth" precedent argues for
   it, but with only 2-3 slots of watermark headroom throughout this phase, deliberately not spent on
   a strengthening neither plan was asked to perform. **No owner** — cheap for whichever later phase
   ratchets the watermark to pick up alongside it.

6. **`.planning/codebase/TESTING.md` remains stale** — asserts "the project has no Python unit tests"
   and references a foreign filesystem path, against a tree that now has 90 test files. **Owner:**
   `/gsd-map-codebase`, a map-refresh task, not this phase's or this milestone's work — but it will
   mislead any agent that reads it in the meantime, as `133-CONTEXT.md` already flagged.

---

## 6. The Evidence Ceiling — the honest claim, stated plainly

**This phase proves that the mechanism cannot strand a chip or lose a report to a transport error,
and that the op registries fail closed. It proves NOTHING about SDP behaviour on silicon.**

Enumerated, per `.planning/REQUIREMENTS.md` §"⚠ Evidence Ceiling":

- **A locked die is unrepresentable in either repo's stubs.** Both the host repo's fixtures and the
  firmware repo's native test harness model the *bus*, never the die's *protection state* — no test
  anywhere in this phase can simulate real SDP inhibition. Fixtures can only pin the host's *response*
  to a scripted read-back.
- **The Phase 116 ground-truth trace harness is unreachable from the host**, and this phase does not
  even reach a scripted wire. It is a PlatformIO `[env:native]` Unity binary in the *firmware* repo
  (`test/native/avr/test_sdp_harness/`, `test_eeprom28c_sdp/`), whose recorder hooks
  `rurp_write_data_buffer`/`rurp_set_control_pin` directly. This phase's tests assert on an
  `EpromOperator` **double** — one layer above the wire, not the wire itself, and not the die.
- **Protection state is not readable on this family.** This is exactly why D-03 excludes both SDP ops
  from `_MULTI_RUN_OPS`'s marginal-on-disagreement policy — there is no readable signal to compare a
  second run against.
- **`0x0D` stays `UNVERIFIED`** at the database level, unmoved by any plan in this phase.
- **No AT28C part has ever been in operator inventory.** Nothing this phase built has ever run against
  real SDP-capable silicon.

Any artifact — this record included, if it strayed — claiming more than the mechanism-only proof
above is the **v1.22 C-5 overclaim class**. Nothing in this phase's own output is user-visible, which
is precisely why nothing pushes back on an overclaim naturally; the Evidence Ceiling exists to make
refusing one mechanical rather than aspirational.

---

*Phase: 133-sdp-leg-mechanism*
*Recorded: 2026-08-04, plan 133-07, against the phase's final engine source at commit `57e8eb5`
(submodule `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`).*
