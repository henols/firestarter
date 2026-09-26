# Phase 133: SDP Leg Mechanism - Research

**Researched:** 2026-08-04
**Domain:** Python host-side execution-engine hardening — `try/finally` cleanup registries, narrow
exception taxonomies, `ast`-based source gates, and fail-closed parity tests
**Confidence:** HIGH (every claim below is measured against the live milestone branch or verified
empirically in-process; no package installs, no new dependencies, no external stack)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `133-CONTEXT.md` §Implementation Decisions. **D-01…D-13 are LOCKED. This research
does not re-litigate them.** Where a measurement bears on one, it is flagged as a
`⚠ Refines locked decision D-NN` or `⚠ Contradicts locked decision D-NN` callout.

- **D-01:** **One guarded `_dispatch_sdp(op, name, eprom_data, operator)`** — an `if op not in _SDP_OPS: return StepResult(verdict=VERDICT_BAD, ...)` guard at the top, an internal per-op branch, and a terminal `raise AssertionError(f"unreachable: op {op!r} passed the _SDP_OPS guard")`. This is `_dispatch_multi_run`'s existing shape copied structurally, so the module gains no new idiom, and criterion 5's deliberate-break test gets a single choke point to break. Rejected: per-op `_dispatch_sdp_lock`/`_dispatch_sdp_unlock` functions mirroring `_dispatch_id`; and a `dict` table mapping op → operator-method name.

- **D-02:** **Phase 133 defines exactly two op strings: `OP_SDP_LOCK` and `OP_SDP_UNLOCK`.** They are the only two the mechanism criteria can actually exercise. Rejected: defining all four of Phase 134's leg ops now.

- **D-03:** **SDP emissions are single-run and explicitly excluded from `_MULTI_RUN_OPS`.** The exclusion is not incidental: it becomes one of the parity test's **asserted exemptions** with a reason string (D-12). Rejected: routing lock/unlock through `_dispatch_multi_run`.

- **D-04:** **The `_dispatch_sdp` arm goes last in `_dispatch_step`, immediately above the terminal fail-closed `return`.** Placing the new arm at position 5 means all seven shipped ops return from arms 1–4 and **never evaluate the new membership test at all**. Rejected: first, above `OP_ID`; and folding the dispatch into the terminal `return`.

- **D-05:** **No `Step.group` field. The SDP arm keys on `_SDP_OPS` membership of the op string.** Rejected: adding `Step.group: str | None = None`. **Honest consequence, to be stated in the phase record and not smoothed over:** ROADMAP criterion 4's clause *"an op with `group=None` takes the exact pre-existing dispatch path"* is then satisfied **vacuously**. The record must say the criterion's *intent* was met by a different mechanism, and must not restate the criterion's literal words as though they were tested.

- **D-06:** **A generic cleanup registry: `run_plan` keeps a `list` of cleanup callables that a successful `sdp_lock` step appends its unlock to, drained in one `try/finally` around the whole step loop.** An empty registry is a **proven no-op** for every currently-shipping run. Rejected: a hardcoded `try/finally` around just the lock→unlock window with the unlock written inline.

- **D-07:** **On the propagating path the cleanup drains, the unlock attempt is recorded on the exception (or logged), and `KeyboardInterrupt`/`SystemExit` propagates unchanged — the report is honestly forfeited.** Criterion 2 requires "Ctrl-C must stay Ctrl-C", so swallowing it to save the report is not available. Rejected: changing `run_plan` to append into a caller-owned results list. **Honest residual to state plainly in the phase record:** after a Ctrl-C mid-leg the chip is left with an unlock attempted, and the user sees no `dev test` report at all.

- **D-08:** **`_run_step` catches `SerialError` and `HardwareOperationError`, but re-raises `ProgrammerNotFoundError` and `FirmwareOutdatedError` first.** "No programmer attached" and "firmware too old" are run-fatal host-setup conditions; catching the base class flat would turn them into six BAD steps and a report that reads as a broken chip. Rejected: catching `SerialError` flat as LEG-11 words it; and catching only `SerialTimeoutError` + `HardwareOperationError`.

- **D-09:** **No-bare-except is proven two ways: behavioral tests, plus a new deny-rule in `tools/check_devtest_orchestrator.py`'s existing `_OrchestratorDenyVisitor`.** This is one `visit_ExceptHandler` method flagging `type is None` or a `type` naming `Exception`/`BaseException`, not a new tool. Rejected: behavioral tests only; and a new standalone `tools/check_no_bare_except.py`.

- **D-10:** **Each cleanup callable is wrapped in its own `try/except` over the same explicitly-named classes the step path catches (`SerialError`, `HardwareOperationError`, `EpromOperationError`), recorded as a failed-unlock attempt, and the drain then continues.** Rejected: a broad catch in the drain only, with a comment.

- **D-11:** **In Phase 133 the unlock reaches the chip only via the registry drain — it is not a derived plan step — and `OP_SDP_UNLOCK` is kept out of `_DESTRUCTIVE_OPS` anyway, asserted as a standing invariant.** The `_DESTRUCTIVE_OPS` absence is **forward-protection for Phase 134**, and the phase record must say so rather than implying the absence gates a live 133 path. Rejected: making the unlock both a plan step and registry-registered now; and plan-step-only, dropping the registry.

- **D-12 (Claude's Discretion):** **The LEG-15 parity test polices every row of P-23's table in Phase 133, via a committed exemption table that requires a non-empty reason string per `(op, registry)` pair.** Three guards make this fail **closed**: (a) an exemption with an empty or missing reason fails; (b) a **stale-row assertion** fails when the table names an `(op, registry)` pair that no longer exists; (c) the number of registries policed is asserted equal to a declared constant. Naming follows the house: `tests/test_op_registration_parity.py`, and it should carry a non-vacuity leg in the shape of `test_sdp_table_parity.py:301`. **Verify P-23's row 8 first.**

- **D-13 (Claude's Discretion):** **Criterion 4's no-op regression test asserts behavior, not diff-emptiness.** Two legs. (a) For a representative non-SDP chip, assert the exact derived op sequence and the exact per-step `(verdict, run_count)` list against an **in-test literal** — not a syrupy snapshot. (b) Monkeypatch `_dispatch_sdp` to raise, then run each of the seven shipped op strings through `_dispatch_step` and assert none of them reaches it. Rejected: an empty-`git diff` or byte-identical-file criterion. Scope any file-level claim to *assertions-unchanged*, or name blob SHAs, never "the file did not change".

### Claude's Discretion

D-12 and D-13 above are the two areas the operator delegated; both are already decided in CONTEXT.md
and are treated here as locked in their *intent*, with this research supplying the measured inputs
their concrete shape depends on (see §"The P-23 Registry Census" and §"Criterion-by-Criterion Proof
Map").

### Deferred Ideas (OUT OF SCOPE)

- **The four-step leg itself** — derivation from `sdp_capability()`, the baseline transition write, the
  inhibited-write generator, the read-back oracle, the degenerate-read-back arms. **Phase 134**
  (LEG-01…08).
- **Every report surface** — the `HELD`/`NOT-HELD`/`NOT-RUN` field, the N-of-M applicable-step change,
  the "rewrite"-not-"erase" recovery wording and its grep, `dedup_fingerprint`, the
  `diagnostic_report.py` renderer, and the `_ALWAYS_WRITES_NOTICE` write-count correction. **Phase 134**
  (LEG-12/13/14) — and the five exemption rows D-12 writes are exactly what 134 discharges.
- **gh#20 triage** (AT28C256 `dev test` FAIL, open since 2026-07-30). **Phase 134** (LEG-18).
- **`write --sdp-relock`** — deferred to **Backlog 999.28** by operator decision 2026-08-03.
- **Adding `tests/test_op_registration_parity.py` to the mypy test strict-island** — measure first;
  do not spend watermark headroom on an unasked strengthening.
- **Ratcheting the watermark to the measured 32** — still unowned.
- **Refreshing `.planning/codebase/TESTING.md`** — a map-refresh task, not this phase's work.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

**These four IDs, and only these four.** The other 14 LEG requirements belong to Phase 134 (P-24: this
project's executors have marked multi-plan requirements Complete prematurely 4× in one phase).

| ID | Description (verbatim, `REQUIREMENTS.md`) | Research Support |
|----|-------------------------------------------|------------------|
| **LEG-09** | `sdp_unlock` is **exempt** from the destructive-op set, so a destructive gate closing after the lock can never skip the unlock and ship a locked part. | §"The Destructive Gate" — measured: the gate is the single `if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed:` at `chip_test.py:784`; `_DESTRUCTIVE_OPS` at `:636`. Both of criterion 3's tests are registry-behavior tests (D-11). |
| **LEG-10** | `run_plan` drains a cleanup registry in a `finally`, so the unlock is attempted even when a mid-leg step raises. | §"The Exact `finally` Shape" — including the **measured `return`-in-`try` + mutate-in-`finally` aliasing trap**, and why the drain must not append into `results`. |
| **LEG-11** | `_run_step` catches `SerialError` and `HardwareOperationError`, so a mid-leg transport timeout degrades that step rather than killing the whole report. | §"The Exception Taxonomy" — full measured hierarchy; the complete `SerialError` subclass census (exactly three, no others); and the measured gap that `_run_step`'s `try` does **not** cover the resolve call. |
| **LEG-15** | An op-registration parity test proves every new op is registered in all required registries — converting eight fail-open registries into one fail-closed gate. | §"The P-23 Registry Census" — an exhaustive repo-wide grep proving **which** of P-23's ten rows are real op-keyed registries and which have no op vocabulary at all. |
</phase_requirements>

---

## Summary

This phase has no external technology domain. It ships zero new dependencies, touches no firmware, and
adds no user-visible surface. Its entire risk surface is *internal mechanics of four Python files*, and
the only honest research method is direct measurement. Accordingly this document is a measurement
record, not a survey. Every anchor CONTEXT.md flagged as drift-prone was independently re-measured;
**all of them verified exactly** (see §"Measured Anchors"), which is itself the notable result — the
drift CONTEXT.md corrected has not drifted again since that session.

Three discoveries materially reshape how the phase should be planned, and none of them contradicts a
locked decision — two of them *confirm* one with evidence it previously lacked:

1. **`chip_test.py:1035` already contains `except Exception`** (in `_sample`, the sampler swallow),
   and its `# noqa: BLE001` is **inert** — ruff's `select` is `["E","F","I","UP"]`, so `BLE001` is not
   enabled. D-09's new deny-rule will therefore fire RED on the *existing, legitimate* source the
   moment it lands unless it carries an exemption. Empirically confirmed against this repo's own ruff
   0.16.0: bare `except:` **is** caught (E722), `except Exception:` and `except BaseException:` are
   **not** caught by anything today. This makes D-09's unique added value precise, and makes the
   exemption a Wave-0 design requirement rather than an afterthought.

2. **The cleanup drain must not append into the list `run_plan` returns.** Measured: `results` is
   returned by reference and mutated-in-`finally` **is** visible to the caller, and
   `cli_handlers.py:2161-2163` feeds that same list into six downstream consumers — `count_applicable`
   (N-of-M), `report.results`, `to_dict()["steps"]`, the markdown table, `build_db_diff`, and
   `sys.exit(max(...))`. Appending an unlock `StepResult` would silently open five Phase-134 report
   surfaces inside a phase whose boundary says "renders nothing new", and would make N exceed M.
   Separately: `chip_test.py` has **no logger and no logging import at all**, so D-07's "or logged"
   has no existing surface, and `exc.add_note()` is unavailable (`requires-python = ">=3.9"`).

3. **P-23's "ten registries" is measurably four-or-five real ones plus five non-registries.** An
   exhaustive repo-wide grep proves that outside `chip_test.py` the *entire* production surface
   contains exactly one op-keyed line of code (`cli_handlers.py:1942`, `OP_ID`-specific). The
   `dedup_fingerprint` hash, the `diagnostic_report.py` renderer, and `parse_devtest_issue.py` carry
   **no op vocabulary whatsoever** — they are fully generic over `StepResult.op`, so there is nothing a
   new op could be "omitted from". CONTEXT.md's correction 2 (row 8) is confirmed **and generalizes to
   rows 6 and 7**. D-12's design survives intact — it already exempts exactly these rows — but its
   guard (c) declared-count constant and its reason strings must distinguish "Phase-134 surface not yet
   joined" from "not an op-keyed registry at all", or the gate becomes theatre that polices phantoms.

**Primary recommendation:** Plan this phase as four independently-provable mechanisms in dependency
order — (1) the exception taxonomy in `_run_step`, (2) the `finally` + registry in `run_plan`, (3) the
`_SDP_OPS`/`_dispatch_sdp` arm, (4) the two gates (AST deny-rule + parity test) — and make the
`chip_test.py:1035` exemption and the "drain does not touch `results`" decision explicit Wave-0
outputs, because every later plan inherits them.

---

## Architectural Responsibility Map

`dev test` is a single-process host CLI with no network tier and no persistence tier beyond report
artifacts. The meaningful tiers here are *layers within the host process*, and the phase's whole
correctness argument is about which layer owns which guarantee.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Op vocabulary + registry membership (`OP_SDP_*`, `_SDP_OPS`) | Engine module constants (`chip_test.py`) | — | Established pattern: "module constants, never DB fields, for anything that widens a blast radius" (SC4). A DB-sourced op set would be an injection surface. |
| Per-step exception → verdict degradation (LEG-11) | Engine step layer (`_run_step`) | — | `_run_step` is the only layer that both knows the `Step` and can still produce a `StepResult`. Catching lower (in `_dispatch_*`) loses the per-op uniformity; catching higher (`run_plan`) loses the step identity. |
| Run-fatal host-setup escalation (`ProgrammerNotFoundError`, `FirmwareOutdatedError`) | CLI error mapper (`cli_handlers.py:186-211`, `@map_typed_errors`) | Engine re-raise in `_run_step` | The mapper already renders these as ClickExceptions with stable exit codes. The engine's job is only to **not** swallow them. |
| Cleanup guarantee (LEG-10) | Engine plan layer (`run_plan` `finally`) | — | Only `run_plan` spans the whole step loop, which is the exact window a mid-leg abort can open. |
| Destructive gating (LEG-09) | Engine plan layer (`run_plan:784`) | `_DESTRUCTIVE_OPS` constant | The gate is deliberately *above* dispatch so a gated step never reaches an operator method. |
| Report rendering / N-of-M / dedup | Report tier (`diagnostic_report.py`) + handler (`cli_handlers.py`) | — | **This phase must not reach this tier.** Generic over `StepResult.op` (measured), which is precisely why an appended cleanup result would leak into it silently. |
| Source-shape enforcement (no broad excepts) | Build-time gate (`tools/check_devtest_orchestrator.py`) | ruff E722 (bare only) | A gate tier, not a runtime tier; it fails the build, never the run. |
| Registry-completeness enforcement (LEG-15) | Test tier (`tests/test_op_registration_parity.py`) | — | Introspects engine constants; must not import the report tier, to keep the phase host-and-engine-local. |
| SDP emission on silicon | **Unrepresentable** (Evidence Ceiling) | — | A locked die cannot be modeled in either repo's stubs. No tier in this phase can prove inhibition. |

---

## Measured Anchors

**Measured 2026-08-04 against `firestarter_app` @ `42a1971`, branch `gsd/v1.30-sdp-surface-retirement`.**
Meta repo on `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof` — the divergence is deliberate
and confirmed.

> **Re-verify every number at execute time.** Anchor on the **name**; the line number is a
> measured-at-research-time convenience only. This project's record is that these drift.

### `firestarter/chip_test.py` — 1253 lines

| Symbol | CONTEXT.md said | **Measured** | Status |
|--------|-----------------|--------------|--------|
| Op constants (7 strings) | `:289-295` | `:289-295` | ✅ exact |
| `Step` | `:298` | `:298` (`@dataclass` at `:298`, `class Step` at `:299`) | ✅ |
| `Plan` | — | `:327-328` | measured |
| `derive_plan` | — | `:394`; `Step(op=…)` sites at `:473, 475, 478, 486, 496, 508, 531, 544, 572` | measured |
| Verdict constants | — | `:620-624` | measured |
| `_DESTRUCTIVE_OPS` | `:636` | `:636` | ✅ exact |
| `_MULTI_RUN_OPS` | `:654` (P-23 said `:657`) | `:654` | ✅ CONTEXT.md correction confirmed |
| `_DESTRUCTIVE_GATE_REASON` | `:656` | `:656` | ✅ exact |
| `StepResult` | `:661` | `:661` (`@dataclass`), `class` at `:662` | ✅ |
| `_skip_result` | — | `:685` | measured |
| `_resolve_or_none` | — | `:689`; its `except (ChipNotImplementedError, ChipNotFoundError)` at `:703` | measured |
| `run_plan` | `:709-794` (P-20 said `:757-802`) | `:709-794`; guard `:763`; `results` init `:776`; loop `:779`; **destructive gate `:784`**; `_run_step` call `:788`; gate update `:791-792`; `return results` `:794` | ✅ CONTEXT.md correction confirmed |
| `_id_step_closes_gate` | `:797` | `:797` | ✅ exact |
| `_write_region_for` | — | `:832` | measured |
| `_run_step` | `:863-898` | `:863-898`; `try` opens `:883`; `except EpromOperationError` **`:887`**; `except (ChipNotImplementedError, ChipNotFoundError)` `:895` | ✅ exact |
| `_dispatch_step` | `:901-952` (P-23 said `:903-948`) | `:901-952`; arms at `:924` (OP_ID), `:926` (OP_BLANK_CHECK), `:931` (OP_READ), `:940` (`_MULTI_RUN_OPS`); **terminal fail-closed `return` `:944-952`** | ✅ CONTEXT.md correction confirmed |
| `_dispatch_id` | — | `:955` | measured |
| `_dispatch_read` | — | `:978` | measured |
| `_sample` | — | `:1026`; **`except Exception:  # noqa: BLE001` at `:1035`** | measured — see §Pitfall 1 |
| `_dispatch_multi_run` | `:1039`, guard `:1082-1093`, `AssertionError` `:1130` | `:1039`; **guard `:1082-1093`**; run-loop branches `:1112-1121`; **terminal `AssertionError` `:1130-1132`** | ✅ exact |
| `_RAN_VERDICTS` | `:1209` | `:1209` | ✅ exact |
| `BannerCounts` | — | `:1212-1213` | measured |
| `count_applicable` | `:1229` | `:1229` | ✅ exact |

**Module has no logger.** Imports are exactly: `hashlib`, `tempfile`, `dataclasses`, `pathlib.Path`,
`typing.Any`, `chip_resolver.resolve_chip`, `constants.FLAG_CAN_ERASE`, and three exception classes
(`:29-41`). **Zero `logging` import, zero `logger` reference** — verified by grep.

### `firestarter/exceptions.py` — 87 lines. Every CONTEXT.md anchor exact.

```
SerialError(Exception)                     :13
├── SerialTimeoutError                      :19
├── ProgrammerNotFoundError                 :25
└── FirmwareOutdatedError                   :31
EpromOperationError(Exception)             :37   [carries .error_code]
├── ProtocolNotImplementedError             :45
└── ChipNotImplementedError                 :51
HardwareOperationError(Exception)          :69   ← sibling of Exception, NOT an EpromOperationError
FirmwareOperationError(Exception)          :75
ChipNotFoundError(Exception)               :81
```

**Answering the orchestrator's explicit question — "does any *other* `SerialError` subclass exist that
should also be run-fatal?"** **No.** `SerialError` has exactly three subclasses, all in this file, and
a repo-wide grep finds no other class deriving from it. D-08's set is therefore complete and
exhaustive as written: re-raise `ProgrammerNotFoundError` + `FirmwareOutdatedError`, catch the
remainder of `SerialError` (which is exactly `SerialError` itself and `SerialTimeoutError`) plus
`HardwareOperationError`. **[VERIFIED: measured source + grep]**

⚠ **Refines locked decision D-08 (does not contradict).** Note that `EpromOperationError`'s two
subclasses (`ProtocolNotImplementedError` `:45`, `ChipNotImplementedError` `:51`) are *already* caught
by `_run_step`'s existing `except EpromOperationError` at `:887` — but `ChipNotImplementedError` is
*also* named in the narrower handler at `:895`. Because `:887` precedes `:895`, **a
`ChipNotImplementedError` raised during dispatch is caught at `:887` and recorded `BAD`, never
reaching the `:895` SKIPPED handler.** The `:895` handler is reachable only for `ChipNotFoundError`.
This is a pre-existing ordering subtlety, not something this phase introduces, but D-08 adds two more
clauses to this same chain and **clause order is load-bearing** — the new `except (ProgrammerNotFoundError, FirmwareOutdatedError): raise`
must precede `except SerialError`, and neither may be placed after `except EpromOperationError` in a
way that changes which handler wins for existing classes. Criterion 4 (byte-identical behavior for
shipped ops) requires a test pinning the existing precedence.

### `firestarter/cli_handlers.py` — the two lines D-07 turns on

| Symbol | CONTEXT.md said | **Measured** |
|--------|-----------------|--------------|
| `_ALWAYS_WRITES_NOTICE` | `:2071` | `:2071-2078` ✅ (echoed at `:2123`) |
| `dev_test` | `:2085` | `:2085` ✅ |
| `derive_plan` call | `:2138` | `:2138` ✅ |
| **`run_plan` call** | `:2164` | **`:2164`** ✅ |
| `report.results = results` | — | **`:2165`** |
| **`count_applicable` call** | `:2166` | **`:2166`** ✅ |
| `build_db_diff(…, results)` | — | `:2178` |
| markdown table `for r in results` | — | `:2200-2201` |
| `sys.exit(max(_verdict_code(r.verdict) for r in results))` | — | **`:2217-2219`** |
| `_verdict_code` | — | `:1900` |
| `@map_typed_errors` exception mapper | — | `:180-211` |
| `if r.op == OP_ID` (only op-keyed line outside `chip_test.py`) | — | **`:1942`** (in `_chip_id_fields`) |

### `firestarter/tools/check_devtest_orchestrator.py` — 445 lines

| Symbol | CONTEXT.md said | **Measured** |
|--------|-----------------|--------------|
| `FIRESTARTER_DEVTEST_SRC` seam | `:86` | `:86` ✅ |
| `FIRESTARTER_DEVTEST_HANDLER` seam | — | `:98-100` |
| `FIRESTARTER_DEVTEST_SUBMIT` seam | — | `:113-115` |
| `_HANDLER_FUNCTION_NAMES` | `:138` | `:138-150` (9 names) ✅ |
| `_OrchestratorDenyVisitor` | `:196` | `:196` ✅ — three buckets, `visit_Call` `:224`, `visit_Dict` `:240`, `visit_Constant` `:254` |
| `_scan_file` | — | `:262` (full-file scan) |
| `_scan_target_functions` | — | `:281` (name-scoped scan) |
| `_assert_host_only` | — | `:321` |
| `_print_bucket` | — | `:344` |
| `main()` | — | `:352`; three-target list `:371-375`; scanned-empty fail-closed `:411-417`; PASS line `:438-441` |

### Other files

| File | Measured |
|------|----------|
| `firestarter/eprom_operations.py` | `sdp_unlock` `:1736`, `sdp_lock` `:1784` ✅ — **ring-fenced**, call/reference only |
| `tests/conftest.py` | `make_app_context(...)` `:229`; `app_context` fixture `:325` ✅ |
| `tests/test_chip_test.py` | 1958 lines; **20 `run_plan(` call sites measured** (CONTEXT.md said 10 — see note below) |
| `tests/test_check_devtest_orchestrator.py` | 667 lines, 18 tests, all via **real `subprocess`** + env-override seams |
| `tests/test_sdp_table_parity.py` | 354 lines; non-vacuity leg `:301`, fails-closed leg `:349` ✅ |
| `pyproject.toml` | `requires-python = ">=3.9"` `:12`; `[tool.ruff]` `target-version="py39"` `:110`; `select = ["E","F","I","UP"]` `:131`; `[tool.mypy] python_version="3.10"` `:155`, `check_untyped_defs = false` `:158`; **watermark comment `:159`** ✅ |
| `tools/ci_parity.sh` | four legs — banners at `:86`, `:94`, `:102`, `:117` |

⚠ **One CONTEXT.md count is stale, in the safe direction.** CONTEXT.md records "10 `run_plan` call
sites" in `tests/test_chip_test.py`; measured **20** (`:837, 854, 878, 894, 910, 951, 986, 1007, 1028,
1058, 1076, 1089, 1102, 1113, 1197, 1222, 1236, 1242, 1264, 1291`, plus further sites beyond the first
20 lines of grep output). This *strengthens* D-07's rejection of a signature change (the blast radius
is larger than recorded, not smaller). Also measured: **88 test files** in `tests/` (CONTEXT.md said
84) and **30 syrupy snapshots** currently passing — confirming the D-13 unused-snapshot trap is live,
not hypothetical.

---

## Standard Stack

**No new dependencies. Nothing to install.** Every mechanism this phase needs is already present in
the Python standard library or the repo's existing dev tooling.

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `ast` (stdlib) | py3.9+ | The `visit_ExceptHandler` deny-rule (D-09) | Already the mechanism `_OrchestratorDenyVisitor` uses for its three existing buckets — extending it adds no idiom. `ast.ExceptHandler.type` is stable across 3.9–3.13. **[VERIFIED: measured locally, py3.12.13]** |
| `try`/`finally` (language) | — | The cleanup registry drain (LEG-10, D-06) | The only construct that runs on `KeyboardInterrupt`/`SystemExit` **and** lets them propagate. Requires no `except` clause at all — which is what keeps D-09's no-broad-except rule satisfiable. **[VERIFIED: measured locally]** |
| `pytest` | (repo pin) | Every behavioral proof | `testpaths = ["tests"]`, `addopts = "-ra -q"` **[VERIFIED: pyproject.toml]** |
| `unittest.mock` via `tests/conftest.py` | stdlib | `make_app_context` / `app_context` fixture base (Phase 132 D-10) | Already landed; no new factory needed. **[VERIFIED: measured `:229`, `:325`]** |
| `ruff` | 0.16.0 | Lint gate leg 3 | **[VERIFIED: `ruff --version`]** |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `subprocess` (stdlib) | py3.9+ | Proving the AST gate fails RED on planted source | The house anti-hollow convention — all 18 tests in `test_check_devtest_orchestrator.py` shell out for real. Use for **every** gate-behavior proof; never an in-process synthetic. **[VERIFIED: measured]** |
| `tmp_path` (pytest fixture) | — | Planted-violation fixture files for the gate's RED leg | Paired with the `FIRESTARTER_DEVTEST_SRC` env seam at `:86`. **[VERIFIED: measured]** |
| `pytest.MonkeyPatch` | — | D-13's `_dispatch_sdp`-raises sentinel; planted-fault injection for D-08 | In-process is sufficient here — no import-time binding is involved (see §Pitfall 5 for where it is **not** sufficient). |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| A plain `list` of callables + per-item `try/except` (D-06/D-10) | `contextlib.ExitStack` + `.callback()` | **Measured and rejected on evidence — this CONFIRMS D-06/D-10.** `ExitStack` is stdlib since 3.3 so availability is fine, but (a) `close()` drains **LIFO**, reversing registration order, and (b) a raising callback makes `close()` **re-raise**, which inside a `finally` **replaces the in-flight exception** (original demoted to `__context__`). That is exactly the masking D-10 exists to prevent. Docs also note `callback()`-registered callables "cannot suppress exceptions (as they are never passed the exception details)". **[CITED: docs.python.org/3/library/contextlib.html]** + **[VERIFIED: measured locally — drain order `['third','second','first']`, `close()` raised `RuntimeError`]** |
| A new AST deny-rule for bare `except:` (D-09, half of it) | ruff `BLE001` (`flake8-blind-except`) | Would be the idiomatic tool, **but `BLE` is not in this repo's `select`**, so enabling it is a repo-wide lint policy change with unknown blast radius across 88 test files + 20 modules — far outside this phase. Keep D-09's AST rule, scoped to three files. See §Pitfall 1. **[VERIFIED: measured empirically]** |
| Recording the failed unlock on the exception | `exc.add_note()` (PEP 678) | **Unavailable.** `requires-python = ">=3.9"`; `add_note` is 3.11+. **[VERIFIED: pyproject.toml `:12`]** |
| An in-test literal for the op sequence (D-13a) | `syrupy` snapshot | Rejected by D-13 and confirmed live: **30 snapshots currently pass**, and syrupy 5.5.3 fails the whole session on unused snapshots (Phase 132 D-13). **[VERIFIED: measured suite output]** |

**Installation:** none.

```bash
# Nothing to install. Verify the existing toolchain instead:
cd firestarter_app && ruff --version && python3 -m pytest tests/ -q --collect-only | tail -1
```

---

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.**

No `pip install`, no new `dependencies` or `[project.optional-dependencies]` entry, no new import of any
third-party module. Every mechanism is stdlib (`ast`, `contextlib` considered-and-rejected,
`subprocess`, `unittest.mock`) or an already-pinned dev tool (`pytest`, `ruff`, `mypy`, `syrupy`).

**Packages removed due to [SLOP] verdict:** none — none were proposed.
**Packages flagged as suspicious [SUS]:** none — none were proposed.

Consequently there is **no** `checkpoint:human-verify` install gate for the planner to insert on
package grounds. (Operator checkpoints may still be warranted on other grounds; see §Validation
Architecture.)

---

## Architecture Patterns

### System Architecture Diagram

Data flow for one `dev test` invocation, with this phase's four additions marked **[133]**. Read it as
the path a single step takes, and note where an exception can escape.

```
  user: `firestarter dev test AT28C256`
        │
        ▼
  cli_handlers.dev_test  :2085          ── @map_typed_errors :180-211 wraps the WHOLE handler
        │                                   (ProgrammerNotFoundError / FirmwareOutdatedError land HERE)
        ├─ echo _ALWAYS_WRITES_NOTICE :2123      (NOT edited this phase — P-08)
        ├─ db.get_eprom → hard-fail if absent :2130
        ├─ _resolve_write_scope  :2137           (UV ask)
        ├─ derive_plan :2138 ───────────────► Plan{steps=[Step(op=…), …]}
        │                                        └─ Step(op=…) sites :473-572
        │                                           **[133] emits NO SDP step (D-11 / out of scope)**
        ▼
  chip_test.run_plan :709 ─────────────────────────────────────────────────────┐
        │  runs<2 guard :763                                                   │
        │  results: list[StepResult] = []  :776                                │
        │  **[133] cleanup: list[Callable] = []  (D-06)**                      │
        │  **[133] try:  ← opens AFTER both locals exist**                     │
        │    for step in plan.steps:  :779                                     │
        │      ├─ not supported ──────────────► NA result :781, continue        │
        │      ├─ op in _DESTRUCTIVE_OPS                                       │
        │      │    AND gate closed :784 ────► SKIPPED result :785, continue   │
        │      │      ▲                                                        │
        │      │      └── **[133] LEG-09: OP_SDP_UNLOCK deliberately ABSENT    │
        │      │           from _DESTRUCTIVE_OPS, so it can never be gated**   │
        │      ├─ _run_step(...) :788 ──────────┐                              │
        │      └─ if op == OP_ID :791 ─► gate = _id_step_closes_gate :797      │
        │  **[133] finally: drain cleanup in registration order,               │
        │           each callable in its OWN narrow try/except (D-10);         │
        │           MUST NOT append into `results` — see Pitfall 2**           │
        │  return results :794 ────────────────────────────────────────────────┘
        │                                       │
        │                                       ▼
        │                        _run_step :863
        │                          ├─ _resolve_or_none :876  ⚠ OUTSIDE the try (Pitfall 3)
        │                          └─ try: :883
        │                               └─ _dispatch_step :901 ──────────┐
        │                             **[133] except (ProgrammerNotFound,│
        │                                FirmwareOutdated): raise  ← FIRST**
        │                             **[133] except (SerialError,       │
        │                                HardwareOperationError): → BAD (D-08)**
        │                               except EpromOperationError :887 → BAD
        │                               except (ChipNotImpl, ChipNotFound) :895 → SKIPPED
        │                                                                │
        │                                                                ▼
        │                                    _dispatch_step arms (order is load-bearing, D-04)
        │                                      1. op == OP_ID          :924 ─► _dispatch_id :955
        │                                      2. op == OP_BLANK_CHECK :926 ─► operator.check_eprom_blank
        │                                      3. op == OP_READ        :931 ─► _dispatch_read :978
        │                                      4. op in _MULTI_RUN_OPS :940 ─► _dispatch_multi_run :1039
        │                                                                        guard :1082, AssertionError :1130
        │                                    **[133] 5. op in _SDP_OPS  ─► _dispatch_sdp (NEW)
        │                                            guard → per-op branch → terminal AssertionError**
        │                                      6. terminal fail-closed BAD :944  ◄── all 7 shipped ops
        │                                                                            return at arms 1-4
        ▼                                                                            and NEVER reach arm 5
  results ──┬─► report.results       :2165 ──► to_dict()["steps"] ──► render() rows / JSON artifact
            ├─► count_applicable     :2166 ──► BannerCounts(n_ran, m_applicable) ──► "N of M ran"
            ├─► build_db_diff        :2178
            ├─► markdown table       :2200
            └─► sys.exit(max(...))   :2217      ⚠ ALL FIVE are Phase-134 surfaces.
                                                  An appended cleanup result reaches every one.

  BUILD-TIME (no runtime path):
    tools/check_devtest_orchestrator.py main() :352
      ├─ _scan_file(chip_test.py)                    FULL file
      ├─ _scan_target_functions(cli_handlers.py, _HANDLER_FUNCTION_NAMES :138)   9 functions only
      └─ _scan_file(submit.py)                       FULL file
           └─ ONE shared _OrchestratorDenyVisitor :196 → 3 buckets
              **[133] + 4th bucket: broad_except_violations (D-09)
                 ⚠ fires on the PRE-EXISTING chip_test.py:1035 unless exempted**
```

### Recommended Project Structure

This phase adds **exactly one new file**. Everything else is an edit to a measured, existing file.

```
firestarter_app/
├── firestarter/
│   ├── chip_test.py                  # EDIT: OP_SDP_*, _SDP_OPS, _dispatch_sdp,
│   │                                 #       run_plan try/finally + registry,
│   │                                 #       _run_step except clauses
│   ├── cli_handlers.py               # NOT EDITED (D-07 declined the signature change;
│   │                                 #   _ALWAYS_WRITES_NOTICE is Phase 134's — P-08)
│   ├── diagnostic_report.py          # NOT EDITED (no report surface this phase)
│   ├── eprom_operations.py           # NOT EDITED — ring-fenced (FUT-MYPY-02); call only
│   └── sdp_honesty.py                # NOT EDITED; import surface must not break
├── tools/
│   └── check_devtest_orchestrator.py # EDIT: one visit_ExceptHandler + 4th bucket + PASS line
└── tests/
    ├── test_op_registration_parity.py   # NEW  ← the only new file (LEG-15, D-12)
    ├── test_chip_test.py                # EDIT: append LEG-09/10/11 + D-13 behavioral tests
    └── test_check_devtest_orchestrator.py # EDIT: append RED/GREEN legs for the new bucket
```

⚠ **Open placement question for the planner (not a locked decision):** D-13's two legs and the
LEG-09/10/11 behavioral tests could go in `test_chip_test.py` (1958 lines, already the home of all 20
`run_plan` call sites) or in a new `tests/test_chip_test_sdp_leg.py`. CONTEXT.md's `<code_context>`
says "this phase's new test module" (singular) and Phase 132 D-10's `app_context` fixture is described
as its base — which implies a new module. Recommendation: **a new module** for the SDP-leg behavioral
tests, because (a) it keeps the `MIN_CHECKED_SOURCE_FILES` accounting explicit, (b) it isolates the new
`finally`-path tests from 1958 lines of existing history, and (c) it lets the mypy strict-island
question (deferred) be decided per-file later. But note the honest cost: **it adds a second new file**,
raising the checked-source-file floor by 2 rather than 1 (see §Pitfall 7).

### Pattern 1: `try/finally` with no `except` — the only construct that satisfies both criteria 1 and 2

**What:** Wrap the step loop in `try:` … `finally:` with **zero** `except` clauses on that statement.
**When to use:** LEG-10 / criterion 1. This is the whole mechanism.
**Why it is the only option:** criterion 1 requires the drain to run on `KeyboardInterrupt` and
`SystemExit`; criterion 2 requires those to keep propagating **and** forbids
`except Exception`/`except BaseException`. A bare `finally` satisfies all three simultaneously.

⚠ **Refines P-20 prevention #2.** P-20 says *"A `try/finally` around the lock→unlock window, **wide
enough to catch `BaseException`**"*. Measured: that clause is unnecessary and, if implemented literally,
**self-defeating** — an `except BaseException:` would be flagged by D-09's own new deny-rule and would
violate criterion 2. `finally` needs no `except` of any width.

```python
# Source: measured empirically, python 3.12.13, this session
def h():
    try:
        raise KeyboardInterrupt()
    finally:
        print('finally reached on KeyboardInterrupt')   # ← prints
try:
    h()
except KeyboardInterrupt:
    print('KI still propagated')                        # ← also prints
```

**[VERIFIED: measured locally]**

### Pattern 2: The house fail-closed dispatch shape (D-01 clones this)

**What:** guard → per-op branch → terminal `raise AssertionError("unreachable: …")`.
**When to use:** `_dispatch_sdp`. Copy `_dispatch_multi_run` structurally.
**Why:** the module already proves this shape fails closed; the pre-Phase-121 shape routed any unmapped
op to `erase_eprom()` and reported `OK`.

```python
# Source: firestarter/chip_test.py:1082-1093 and :1130-1132 (measured verbatim)
    if op not in _MULTI_RUN_OPS:
        return StepResult(
            op=op,
            verdict=VERDICT_BAD,
            run_count=0,
            reason=(
                f"op {op!r} is not in the multi-run dispatch allow-list "
                "(_MULTI_RUN_OPS) — refused fail-closed rather than falling "
                "through to erase_eprom"
            ),
        )
    # ... per-op branches ...
            else:
                raise AssertionError(
                    f"unreachable: op {op!r} passed the _MULTI_RUN_OPS guard"
                )
```

Note the two-part structure: the **guard returns a `StepResult`** (a caller-visible refusal), while the
**terminal `else` raises** (a programmer error that must escape loudly). D-01 asks for both. Criterion
2's "the deliberate `AssertionError` must still propagate" is a claim about the *second* one at `:1130`
— and `AssertionError` is not a `SerialError`, `HardwareOperationError`, or `EpromOperationError`, so
D-08's new clauses do not catch it. **That property must be asserted by test, not assumed**, because it
is the single behavioral invariant that proves no broad catch was introduced.

### Pattern 3: The house gate shape — real `subprocess` + env-override seam + planted RED leg

**What:** every `tools/check_*.py` gate is proven by a paired pytest that (a) runs the real checker as a
subprocess against the real source and asserts exit 0, and (b) writes a deliberately-violating file to
`tmp_path`, points the checker at it via an env seam, and asserts exit non-zero **and** that the
bucket name appears in stdout.
**When to use:** D-09's new deny-rule. Both legs are mandatory.

```python
# Source: tests/test_check_devtest_orchestrator.py:174-200 (measured verbatim, abridged)
def test_checker_exits_nonzero_on_planted_vpp_set(tmp_path: Path) -> None:
    bad = tmp_path / "planted_vpp_set.py"
    bad.write_text(
        "def orchestrate(op):\n"
        "    op.set_vpp(12000)\n"
        "    return op.write_eprom('chip', {}, 'path')\n"
    )
    result = _run_checker({"FIRESTARTER_DEVTEST_SRC": str(bad)})
    assert result.returncode != 0, (
        f"checker exited 0 on a planted VPP-set violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "VPP-set" in result.stdout
```

**Good news, measured:** the existing PASS-line assertions are **loose** — `test_checker_exits_zero_on_clean_source`
asserts only `"PASS:" in result.stdout`, and `test_checker_exits_zero_on_real_submit_and_pass_line_names_it`
asserts only `"PASS:"` and `"submit.py"`. Neither pins the exact
`"0 VPP-set, 0 raw-wire-dict, 0 --force"` text. **So extending the PASS line at `:438-441` with a
fourth counter breaks no existing test.** **[VERIFIED: measured source]**

### Pattern 4: The house parity-test shape (D-12 follows this)

`tests/test_sdp_table_parity.py` supplies two legs D-12 must clone:

```python
# Source: tests/test_sdp_table_parity.py:301-341 (non-vacuity), abridged
    altered = original.replace("{0x5555, 0x20}", "{0x5555, 0x21}", 1)
    assert altered != original, (
        "Fixture setup error: the byte replacement did not apply -- ..."
    )
    # ... point the env seam at the altered temp copy ...
    try:
        _assert_pairs_equal(sdp_pairs, flash_pairs, _PARITY_CONTEXT)
    except AssertionError:
        pass
    else:
        raise AssertionError(
            "Non-vacuity failure: altering one byte in the temp fixture did "
            "not make the parity assertion fail -- the parser or the "
            "parity gate is vacuous."
        )
```

⚠ **One structural difference the planner must honor.** `test_sdp_table_parity.py`'s legs are decorated
`@requires_fw` — they read the **firmware sibling repo** (`eeprom_28c.cpp`), so they **SKIP in
standalone CI** where that sibling is absent. This phase's parity test is host-and-engine-local
(§"The P-23 Registry Census" proves every real registry lives in `chip_test.py`), so it must **not**
use `@requires_fw` and must not read any firmware path — which means, unlike its template, **it will
actually run in CI**. `_assert_host_only` at `check_devtest_orchestrator.py:321` documents the same
host-only framing intent for the gate side.

### Anti-Patterns to Avoid

- **`except BaseException:` / `except Exception:` anywhere in the new code.** Violates criterion 2, and
  after D-09 lands, fails the build. Use `finally` (needs no `except`) or name the classes.
- **Appending the cleanup result into `run_plan`'s returned `results` list.** Silently opens five
  Phase-134 report surfaces. See §Pitfall 2 — this is the highest-severity trap in the phase.
- **Placing the `_dispatch_sdp` arm anywhere but position 5.** D-04's zero-added-branching-cost claim,
  and D-13b's sentinel proof, both depend on all seven shipped ops returning from arms 1–4.
- **Policing a phantom registry in the parity test.** Three of P-23's ten rows have no op vocabulary at
  all. Asserting "membership or exemption" against a registry that cannot have members is theatre that
  inflates the declared-count constant. See §"The P-23 Registry Census".
- **A `dict`-table op→method registry.** D-01 rejected it: "a table-shaped registry is the fail-open
  shape this phase exists to remove."
- **Restating criterion 4's `group=None` wording as though tested.** D-05 makes it vacuous by design.
  Say so.
- **Editing `_ALWAYS_WRITES_NOTICE`.** True write-count delta this phase is **zero** (no derived SDP
  step). Editing it would describe a run that does not exist (P-08).
- **A new skip reason.** `tests/test_skip_census.py`'s `ALLOWED_SKIP_REASONS` fails **closed**. This
  phase should need none; if a fix wants one, re-examine the fix.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Guaranteed cleanup on abort | An `atexit` hook, a signal handler, or a `__del__` finalizer | `try:` … `finally:` in `run_plan` | Criterion 1 names this explicitly: a `finally` reaches `KeyboardInterrupt`/`SystemExit`, "which `atexit` would not". `atexit` also does not run on `SIGKILL`/`os._exit`, and ordering vs. the report write is undefined. |
| Detecting broad `except` in source | A regex over the file text | `ast.NodeVisitor.visit_ExceptHandler` in the **existing** `_OrchestratorDenyVisitor` | A regex cannot distinguish `except Exception:` from the string `"except Exception:"` in a docstring — and `chip_test.py` has **10 docstring/comment mentions of "except"** vs 8 real handlers (measured). The tool's own docstring at `:32-33` commits to "never a hollow declared-empty detector". |
| Enumerating exception handlers | Hand-maintained line lists | `ast.walk` + `isinstance(n, ast.ExceptHandler)` | Measured: this yields exactly 8 handlers in `chip_test.py` with their `type` shapes, immune to line drift. |
| Registering ordered cleanups | `contextlib.ExitStack` | A plain `list` + per-item narrow `try/except` (D-06/D-10) | `ExitStack` drains **LIFO** and **re-raises** out of the `finally`, masking the in-flight exception. Measured, not assumed. |
| Pinning a derived op sequence | A `syrupy` snapshot | An in-test literal (D-13a) | syrupy 5.5.3 fails the whole session on unused snapshots; 30 snapshots are live today. |
| Proving a gate can fail | An in-process synthetic assertion | Real `subprocess` + `tmp_path` planted file + env seam | The house convention across all 18 tests of the paired module; and "a pre-authored gate leg proves nothing until it is *seen to pass*". |
| Mapping transport errors to user-facing exit codes | New rendering in `chip_test.py` | Let them propagate to `@map_typed_errors` (`cli_handlers.py:180-211`) | It already maps `SerialError`, `SerialTimeoutError`, `FirmwareOutdatedError`, `HardwareOperationError`, and 5 more to ClickExceptions with stable codes. `chip_test.py` is a pure engine with no logger and no output. |

**Key insight:** every "don't hand-roll" here resolves to *use the mechanism this repo already proved*.
The phase's risk is not missing library knowledge — it is quietly introducing a **second** idiom for a
problem the module already solves once, which is precisely how the flat-loop shape rotted (D-06's
rationale) and how a fail-open registry gets added (D-05's rationale).

---

## The P-23 Registry Census

**This is the single most plan-shaping measurement in this document.** LEG-15 and D-12 are built
directly on P-23's ten-row table, and CONTEXT.md's correction 2 already flagged one row as a phantom.
Measured exhaustively this session, **that correction generalizes to three rows**.

### Method

An exhaustive grep for every `OP_*` constant reference and every literal op string across the entire
production surface (`firestarter/` + `tools/`), excluding `chip_test.py`:

```bash
grep -rn "OP_ID\|OP_READ\|OP_BLANK_CHECK\|OP_WRITE\b\|OP_WRITE_PARTIAL\|OP_VERIFY\|OP_ERASE" \
  firestarter/ tools/ | grep -v "^firestarter/chip_test.py"
grep -rn "\"blank-check\"\|'blank-check'\|\"write-partial\"\|'write-partial'" \
  firestarter/ tools/ | grep -v chip_test.py
```

### Result — the entire op-keyed surface outside `chip_test.py` is four lines, three of them comments

| Location | Content | Is it a registry? |
|----------|---------|-------------------|
| `cli_handlers.py:38` | `OP_ID,` (import) | no — import only |
| `cli_handlers.py:1942` | `if r.op == OP_ID and r.reason and "mismatch" in r.reason.lower():` | **no** — `OP_ID`-**specific** logic in `_chip_id_fields`. A new op must not, and cannot, "join" it. |
| `diagnostic_report.py:60` | comment: `` (`OP_WRITE_PARTIAL = "write-partial"`, chip_test.py) `` | no — comment |
| `diagnostic_report.py:204-205` | docstring mentioning `OP_WRITE_PARTIAL` / `OP_WRITE` | no — docstring |

### Row-by-row verdict against P-23's table

| # | P-23 row | P-23's "fails closed?" | **Measured verdict** |
|---|----------|------------------------|----------------------|
| 1 | `_DESTRUCTIVE_OPS` (`:636`) | No | ✅ **REAL op-keyed registry.** `frozenset` of op strings. Policeable. |
| 2 | `_MULTI_RUN_OPS` (`:654`) | Yes | ✅ **REAL op-keyed registry.** `frozenset` of op strings. Policeable. |
| 3 | `_dispatch_step`'s arms (`:924-943`) | Yes | ✅ **REAL.** Explicit `if step.op == OP_X` / `in _MULTI_RUN_OPS` comparisons + terminal refusal `:944`. Policeable (by dispatch behavior, not membership). |
| 4 | `derive_plan`'s step construction | No | ✅ **REAL.** 9 `Step(op=…)` sites, `:473-572`. Policeable. **Exempt this phase** — D-11: no SDP step is derived in 133. |
| 5 | `_RAN_VERDICTS` / `count_applicable` M | No | ⚠ **NOT an op-keyed registry.** `_RAN_VERDICTS` (`:1209`) is a **verdict** frozenset (`OK/BAD/marginal`); `count_applicable` (`:1229`) counts `plan.steps`+`locked_destructive` generically. No op string appears. Nothing to join. |
| 6 | `dedup_fingerprint` hash inputs | No | ⚠ **NOT an op-keyed registry.** `:222-224` builds `f"{result.op}={result.verdict}:{cls}"` — fully generic. A new op is picked up automatically; what changes is the hash's *meaning*, not its membership. P-23's own text concedes this. |
| 7 | `diagnostic_report.py` renderer | No | ⚠ **NOT an op-keyed registry.** Measured `render()` `:479-484`: `for step_row in d["steps"]: table.add_row(f"step: {step_row['op']}", …)`. Fully generic — a new op renders **with zero code change**. P-23's "an unrendered op is invisible" is measurably wrong in mechanism. |
| 8 | `tools/parse_devtest_issue.py` | No | ⚠ **NOT a registry — no op vocabulary at all.** 347 lines; only string constants are `_DEV_TEST_MARKER = "[dev test]"` (`:59`), `_FENCE` (`:64`), `_MAX_BODY_BYTES` (`:69`). Zero op strings. **CONTEXT.md correction 2 CONFIRMED.** |
| 9 | `_ALWAYS_WRITES_NOTICE` | No (P-08) | ⚠ **NOT an op-keyed registry.** Prose at `cli_handlers.py:2068-2075`; carries a *write-count claim*, no op vocabulary. Phase 134's (P-08). |
| 10 | `check_devtest_orchestrator.py`'s allow-list | No (P-07) | ⚠ **NOT an op registry.** `_HANDLER_FUNCTION_NAMES` (`:138-150`) holds **function** names, not op strings. P-07 narrowed by measurement: the deny-visitor AST-walks all of `chip_test.py`, so a `_dispatch_sdp` there **is** scanned; the gap is `cli_handlers.py` helpers, which this phase does not add to. |

**Additionally measured — one real registry P-23 does not list:**

| — | `_dispatch_multi_run`'s inner run-loop branches (`:1112-1132`) | ✅ **REAL.** Explicit `if op in (OP_WRITE, OP_WRITE_PARTIAL)` / `elif op == OP_VERIFY` / `elif op == OP_ERASE` + terminal `AssertionError` `:1130`. Reachable only for `_MULTI_RUN_OPS` members, so SDP ops are structurally excluded by D-03 — but it *is* an op-keyed site a future multi-run op must join. |

### Consequence for D-12 (the design survives; the numbers and reasons must change)

D-12 already assigns exemptions to exactly rows 4–9, so **its structure is correct and is not
contradicted**. What must change is *why* those exemptions exist and *what the declared count counts*:

- **Real, policeable op-keyed registries: 4 today, 5 after this phase** — `_DESTRUCTIVE_OPS`,
  `_MULTI_RUN_OPS`, `_dispatch_step`'s arms, `derive_plan`'s `Step(op=…)` construction, **+ `_SDP_OPS`**.
  (`_dispatch_multi_run`'s inner branches are a sixth if the planner chooses to police it; recommended,
  since it is a genuine fail-closed-by-`AssertionError` site.)
- **Non-registries: 5** (rows 5, 6, 7, 8, 9) + row 10 (function names, different axis).
- **Two distinct exemption reason *kinds* are needed**, and conflating them is how the gate rots:
  - `"Phase 134 surface — not derived as a plan step in 133"` → applies to row 4 (`derive_plan`) and to
    the *future* op-keyed checks Phase 134 will add. **This is a real omission, deliberately deferred.**
  - `"not an op-keyed registry — generic over StepResult.op; nothing to register"` → applies to rows 5,
    6, 7, 8, 9. **This is not an omission at all.** A row of this kind must be recorded as a
    *documented non-registry*, and D-12's **stale-row assertion (guard b) should be extended to fire in
    the other direction too**: if a future phase *does* add an op-keyed membership test to one of these
    files, the row must be promoted from non-registry to policed registry. That inversion is the
    genuinely valuable guard, and it is cheap: assert that each declared non-registry file still
    contains zero op-string references (the exact grep above, as a test).

⚠ **Recommendation, flagged for the planner as a refinement of D-12, not a contradiction:** keep the
single test module and the mandatory-reason exemption table exactly as D-12 specifies, but split the
declared-count assertion (guard c) into **two** constants — `_POLICED_REGISTRY_COUNT` and
`_DECLARED_NON_REGISTRY_COUNT` — with the second backed by the zero-op-references grep. This keeps
"ten rows accounted for" honest, keeps LEG-15's "all required registries" satisfied for every registry
that actually exists, and makes the non-registries fail **closed** if they ever acquire op vocabulary.
Without the inversion, a Phase-134 renderer that *does* start switching on op strings would silently
inherit a permanent exemption — which is exactly the fail-open shape LEG-15 exists to remove.

---

## Common Pitfalls

### Pitfall 1: D-09's new deny-rule fires RED on pre-existing, legitimate source

**Severity: HIGH — blocks the gate from ever landing green.**

**What goes wrong:** `chip_test.py:1035` already contains `except Exception:` — inside `_sample`
(`:1026`), the best-effort sampler swallow. D-09's `visit_ExceptHandler` rule as specified
("`type is None` or a `type` naming `Exception`/`BaseException`") flags it immediately, and the gate
exits 1 on the real, clean source. `test_checker_exits_zero_on_clean_source` goes RED.

**Measured evidence.** An exhaustive AST enumeration of every handler in `chip_test.py`:

| Line | Handler `type` | Broad? |
|------|----------------|--------|
| 703 | `Tuple['ChipNotImplementedError','ChipNotFoundError']` | no |
| 887 | `EpromOperationError` | no |
| 895 | `Tuple['ChipNotImplementedError','ChipNotFoundError']` | no |
| **1035** | **`Exception`** | **YES — the only one** |
| 997, 1148, 1165 | `OSError` | no |
| 1150 | `EpromOperationError` | no |

`submit.py`: 2 handlers, `OSError` and `Tuple['json.JSONDecodeError','TypeError']` — clean.
`cli_handlers.py` **within `_HANDLER_FUNCTION_NAMES` scope**: exactly 1 handler,
`_chip_id_fields:1948` = `Tuple['ValueError','IndexError']` — clean.

**So exactly one pre-existing site is affected, and it is in the one file scanned in full.**

**Why it happens:** the `# noqa: BLE001` comment on `:1035` reads as though a lint rule already governs
this site, so it looks pre-sanctioned. It is not. Measured against this repo's own ruff 0.16.0 and
`pyproject.toml` (`select = ["E","F","I","UP"]`):

```
except:            → E722 flagged, exit 1        ← already gated today
except Exception:  → NOT flagged                 ← ungated today
except BaseException: → NOT flagged              ← ungated today
```

`BLE` is not in `select`, so **`BLE001` is disabled and the `noqa` is inert** (and `RUF100`
unused-noqa is also not selected, so nothing reports the dead suppression). **[VERIFIED: empirical
ruff run this session]**

**How to avoid:** decide the exemption mechanism in Wave 0, before the rule is written. Four options,
with the measured tradeoff:

| Option | Assessment |
|--------|------------|
| **(a) Explicit exemption table keyed on `(enclosing function, exception name)` with a mandatory reason string** | **Recommended.** Shares one idiom with D-12's exemption table, so the phase adds one concept rather than two. Fails closed on a new broad handler anywhere else. Needs the visitor to track enclosing-function context (a `visit_FunctionDef` push/pop, ~8 lines). Add a stale-row assertion so the exemption dies if `_sample` is renamed. |
| (b) Honor the `# noqa: BLE001` marker | Rejected — `ast` does not see comments; would need `tokenize`, and a comment-driven gate is trivially defeated by adding a comment. |
| (c) Narrow `_sample`'s catch to named classes | **Rejected on criterion-4 grounds.** `_sample`'s documented contract (`:757-759`, `:1027`) is "swallow all" for an **opaque caller-supplied callable** — a bad sampler can raise literally anything (`AttributeError`, `TypeError`). Narrowing changes shipped behavior, and `_make_sampler` (`cli_handlers.py:2160`) is live in production. Criterion 4 forbids this. |
| (d) A declared-count watermark ("exactly 1 broad handler") | House-consistent with the mypy watermark, but it does not say *which* site is sanctioned, so a new broad handler added while `_sample`'s is removed passes. Weaker than (a) for equal effort. |

**Warning signs:** the gate's RED planted-violation test passes but `test_checker_exits_zero_on_clean_source`
fails; or someone "fixes" it by narrowing `_sample` (option c) and criterion 4's no-op regression test
does not catch it because it only covers `_dispatch_step` arms, not the sampler bracket.

⚠ This pitfall is **not** recorded in CONTEXT.md. D-10's rejected-alternative text references the
sampler's broad-catch *argument* at `:757-759` (the docstring), but no decision states that an actual
`except Exception` exists at `:1035` and that the new rule must exempt it. Treat this as new
information for the planner.

### Pitfall 2: The cleanup drain silently opens five Phase-134 report surfaces

**Severity: HIGH — violates the phase boundary and inverts the N-of-M banner.**

**What goes wrong:** the natural implementation of "record the unlock attempt as a `StepResult`"
(P-20 prevention #2 says exactly this) is `results.append(unlock_result)` inside the `finally`. That
list is `run_plan`'s return value, and it reaches **six** consumers at `cli_handlers.py:2161-2216`.

**Why it happens — measured Python semantics.** A `return results` inside the `try` and a
`results.append(...)` inside the `finally` **do not** isolate the caller from the mutation, because the
returned object is the same list reference:

```python
# Source: measured empirically, python 3.12.13, this session
def f():
    r = []
    try:
        r.append('step')
        return r
    finally:
        r.append('cleanup')

f()   # → ['step', 'cleanup']      ← the caller SEES the cleanup entry
```

**[VERIFIED: measured locally]**

**Measured downstream blast radius of one appended entry:**

| Consumer | Line | Effect |
|----------|------|--------|
| `count_applicable(plan, results)` | `:2166` | `n_ran` counts any verdict in `{OK,BAD,marginal}` (`:1248`); `m_applicable` counts `plan.steps` (`:1245`). The unlock is **not** a plan step → **N exceeds M**, banner renders "8 of 7 ran". This is LEG-13's territory (Phase 134). |
| `report.results = results` | `:2165` | `to_dict()["steps"]` (`:448`) gains a row → JSON artifact changes shape. LEG-12 (Phase 134). |
| `render()` | `:479-484` | `for step_row in d["steps"]` is **fully generic** → a new "step: sdp-unlock" row appears in the human table with zero renderer change. |
| markdown table | `:2200-2201` | gains a row in the persisted `.md` artifact. |
| `dedup_fingerprint` | `:222-224` | hash string gains `sdp-unlock=<verdict>:<cls>` → the issue-dedup key changes. |
| `build_db_diff(chip, db, results)` | `:2178` | `verdicts = {r.verdict for r in results}` (`:290`) widens. |
| `sys.exit(max(_verdict_code(r.verdict) …))` | `:2217-2218` | a `BAD` unlock flips the process exit code to 1. |

**In Phase 133 specifically this is latent, not active** — no plan derives an SDP step (D-11), so the
registry is empty on every shipped run and all seven effects are zero. That is exactly what makes it
dangerous: it will pass every test in this phase and detonate in Phase 134.

**How to avoid:** make it an explicit, recorded decision that **the drain does not append into
`results`**. The drain's record goes somewhere the report does not read. Given the measured
constraints — `chip_test.py` has **no logger and no `logging` import** (so D-07's "or logged" would
introduce a new idiom to a module whose docstring says it "emits no print/render/CLI output"), and
`exc.add_note()` is unavailable on the `>=3.9` floor — the viable options are:

1. **A separate local list, returned nowhere in 133**, with the *test* observing the drain through the
   cleanup callable's own side effect (a `Mock` on `operator.sdp_unlock`, or a test-owned list closed
   over by the registered callable). This is fully sufficient for criterion 1 and criterion 3 — both
   are "was the unlock attempted?" questions, answerable by asserting on the operator double. It keeps
   the phase at zero report surface and zero new idiom. **Recommended.**
2. Add a module logger. Honest and conventional, but introduces a logging idiom to a deliberately
   silent pure-compute module, and the phase gains an untested output surface.
3. Attach to the exception. Not available (`add_note` is 3.11+); a custom attribute assignment on a
   caught-and-re-raised exception is possible but is a new idiom with no precedent in this repo.

⚠ **Refines P-20 prevention #2 and D-07.** P-20 says the `finally` "records the attempt as a
`StepResult` before re-raising", and D-07 says "recorded on the exception (or logged)". Measured: on the
**propagating** path, `results = run_plan(...)` at `:2164` never completes, so **any** record placed in
`results` is lost regardless — P-20's prevention is unobservable there. And on the **non-propagating**
path, a record in `results` is not merely observable but reaches all six consumers above. So the two
paths pull in opposite directions, and "append a `StepResult` to `results`" is the wrong answer on both.
D-07's honest-residual framing ("the report is honestly forfeited") is correct and should be stated
plainly; this measurement is what makes it concrete.

### Pitfall 3: `_run_step`'s `try` does not cover what its docstring claims

**Severity: MEDIUM — a real LEG-11 hole that D-08's clause list alone does not close.**

**What goes wrong:** `_run_step`'s docstring (`:868-869`) states it *"Wraps the ENTIRE step body
(resolve + dispatch) in try/except so no exception escapes to the `run_plan` loop (Pitfall 1)."*
Measured, it does not:

```
:876   eprom_data, skip_stub, reason = _resolve_or_none(name, db)   ← OUTSIDE any try
:877-881   ... early return on refusal ...
:883   try:                                                         ← try opens HERE
:884       return _dispatch_step(...)
:887   except EpromOperationError as exc:
:895   except (ChipNotImplementedError, ChipNotFoundError) as exc:
```

`_resolve_or_none` (`:689`) has its own internal `try` catching only
`(ChipNotImplementedError, ChipNotFoundError)` at `:703`. So **any other exception raised during
resolution propagates straight out of `_run_step` and out of `run_plan`** — the exact "kills the whole
report" failure LEG-11 exists to fix, just on the resolve half rather than the dispatch half.

**Mitigating measurement:** `resolve_chip` (`chip_resolver.py:16`) is a pure DB-lookup +
`convert_to_programmer` transform — it opens no serial port and raises `ChipNotFoundError` (`:49`)
plus support-status refusals. So a `SerialError` from this path is not currently reachable, and this is
a latent-robustness gap rather than a live bug.

**How to avoid:** decide explicitly whether D-08's new clauses attach to the existing `try` at `:883`
(dispatch only — smallest diff, matches D-08's literal wording "in `_run_step`") or whether the `try`
is widened to include `:876`. **Recommendation: keep the `try` where it is** (widening changes the
control flow of every existing early-return path and risks criterion 4), but **fix the docstring**,
which currently over-claims. A docstring that says "wraps the ENTIRE step body" while the resolve sits
outside it is precisely the kind of confident-but-wrong record this project's history warns about, and
the phase is already editing this function.

### Pitfall 4: Exception-clause ordering silently changes which handler wins for existing classes

**Severity: MEDIUM — a criterion-4 (byte-identical behavior) violation that no existing test catches.**

**What goes wrong:** D-08 adds two clauses to a chain that already has two. Python matches the **first**
clause whose class matches. Two orderings are wrong in ways that are invisible without a test:

- `except SerialError` placed **before** the `(ProgrammerNotFoundError, FirmwareOutdatedError): raise`
  re-raise → both run-fatal classes are caught and degraded to `BAD`. This is exactly the false-green
  no-board report D-08 exists to prevent, and this project has a documented instance of that trap.
- Any new clause placed **before** `except EpromOperationError` (`:887`) that also matches an
  `EpromOperationError` subclass → changes which verdict an existing class produces. (`SerialError` and
  `HardwareOperationError` are both siblings of `Exception`, not `EpromOperationError` subclasses —
  measured — so this specific collision does not arise. But it must be *asserted*, not assumed.)

**Already-latent instance, measured:** `ChipNotImplementedError` (`:51`) is an `EpromOperationError`
subclass **and** is named in the narrow handler at `:895`. Because `:887` precedes `:895`, a
`ChipNotImplementedError` raised during dispatch is recorded **`BAD` via `:887`**, never
**`SKIPPED` via `:895`**. The `:895` handler is reachable only for `ChipNotFoundError`. This is
pre-existing, but the phase must not perturb it.

**How to avoid:** write a precedence test **first**, pinning, for each of the six relevant classes
(`SerialError`, `SerialTimeoutError`, `ProgrammerNotFoundError`, `FirmwareOutdatedError`,
`EpromOperationError`, `ChipNotImplementedError`, `ChipNotFoundError`, `HardwareOperationError`,
`AssertionError`), the exact `(escapes? verdict, error_code)` outcome. Run it **before** the edit to
capture today's behavior, then after. This is the cheapest possible criterion-4 evidence and it
doubles as LEG-11's proof.

**Warning signs:** a no-board run producing six `BAD` steps and a rendered report instead of a single
"no programmer found" error; `AssertionError` from `:1130` being reported as a step verdict rather than
escaping.

### Pitfall 5: Import-time binding makes some proofs impossible in-process

**Severity: MEDIUM — silently vacuous tests.**

**What goes wrong:** `FW_ROOT`, `FW_REPO_PRESENT`, `_BOARD_CHOICES`, and
`channel.is_prerelease_build()` are evaluated at **import/collection** time. `monkeypatch.setenv` runs
after, so it has no effect, and a test that "simulates a different environment" that way asserts
nothing while appearing green.

**How this phase is exposed:** the AST gate's env seams (`FIRESTARTER_DEVTEST_SRC` at `:86`,
`_HANDLER`, `_SUBMIT`) are read at **module import** of the checker
(`os.environ.get(...)` at module top). So an in-process `monkeypatch.setenv` + `import` would bind the
wrong value or be defeated by module caching. This is exactly why all 18 existing tests use
`subprocess`. **Any new leg for the fourth bucket must also use `subprocess`.**

**Not exposed:** the engine-side behavioral tests. `chip_test.py` reads no env var at import; D-13b's
`monkeypatch.setattr(chip_test, "_dispatch_sdp", raiser)` and the planted-fault injections on the
operator double are ordinary in-process attribute patches, which work correctly.

### Pitfall 6: The ROADMAP's "no-board leg" is not a leg

**Severity: LOW — a cross-cutting instruction that cannot be followed literally.**

**What goes wrong:** the ROADMAP's cross-cutting rule says *"Run the CI-parity recipe with the no-board
leg emphasized."* Measured, `tools/ci_parity.sh` has exactly four legs and none of them is a board leg:

| Leg | Command (measured, banner lines `:86/:94/:102/:117`) |
|-----|------------------------------------------------------|
| 1 | `FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q` — firmware sibling **absent** (the standalone-CI condition) |
| 2 | `python3 -m pytest tests/ -q` — firmware sibling **present** (devcontainer layout) |
| 3 | `ruff check firestarter/ tests/` + `ruff format --check` |
| 4 | `python3 tools/check_mypy_watermark.py` — **local exit 2 is expected and correct** (ambient numpy PEP-695 stub truncates mypy; documented in the script header and `131-CI-PARITY.md`) |

The board dimension is named in the script's header as defect class 3 ("a live board on
`/dev/ttyACM*|/dev/ttyUSB*` beats a `comports=[]` patch") but is an **ambient condition of legs 1 and
2**, not a discrete leg.

**How to satisfy the intent:** measured this session, **no board is attached**
(`ls /dev/ttyACM* /dev/ttyUSB*` → none). So legs 1 and 2 already run in the no-board condition, and
"emphasize the no-board leg" is satisfied by *asserting and recording that no board was attached* when
the recipe ran. The planner should state it that way rather than looking for a leg that does not exist.
Relatedly: with a board attached, `test_no_programmer_found_*` characterization tests go RED (a live
port beats the `comports=[]` patch) — so a board must **not** be attached for this phase's runs.

### Pitfall 7: The checked-source-file floor rises, and headroom is thin in two dimensions

**Severity: LOW-MEDIUM — a gate that fails on a successful phase.**

**What goes wrong:** two watermark-style gates both move in the wrong direction when a phase adds files:

- `mypy` errors: **32** measured, watermark **35** → **headroom 3**. `chip_test.py` is in neither strict
  island and the global has `check_untyped_defs = false` (`:158`), so a plain new test module should
  contribute **0** — but that is a prediction, not a measurement.
- `MIN_CHECKED_SOURCE_FILES = 120` vs **122 checked** → **2 slots**. This phase **adds** files, so the
  floor rises. Adding one new test module is fine; adding two (see the placement question in
  §"Recommended Project Structure") consumes both slots exactly.

**How to avoid:** obtain a **real** mypy count before committing, via
`firestarter_app/tools/ci_replica_venv.sh` (Phase 132 D-07) — the devcontainer's own python 3.12 +
numpy 2.5.1 run exits 2 and **cannot** produce one. Do not assume the 0 contribution. And prefer one new
test module over two unless there is a measured reason for the split.

### Pitfall 8: Stale planning records that will mislead a planner

**Severity: LOW — but each has already cost this project time.**

- **`.planning/codebase/TESTING.md` is severely stale** — it asserts "The project has **no Python unit
  tests**" and references foreign `/home/henrik/dev/...` paths. Measured: **88 test files**, and a full
  suite that passes with **30 syrupy snapshots**. **Do not cite it.** The `plan:pre` drift gate is
  non-blocking and will not stop a planner from believing it.
- **Cite `.planning/research/` by P-number, never by phase number.** `research/SUMMARY.md` §"Phase 133"
  (line 726) describes the **oracle**, which is now ROADMAP Phase **134**.
- **`.planning/notes/sdp-surface-retirement-and-behavioral-proof.md`** line numbers are superseded.
- CONTEXT.md's own "10 `run_plan` call sites" and "84 test files" are both low (measured 20+ and 88).

---

## Code Examples

Verified patterns, measured from this repo or from an empirical run this session. Line numbers are
measured-at-research-time — **re-verify before editing**.

### The exact `finally` shape for `run_plan` (LEG-10, D-06/D-07/D-10)

Measured context: `results` is created at `:776`, `destructive_gate_closed` at `:777`, the loop opens
at `:779`, and `return results` is at `:794`. The `runs < 2` guard at `:763` returns **before** any of
this and must stay outside the `try` (there is nothing to clean up yet).

```python
# Shape recommendation, grounded in measured chip_test.py:763-794.
# NOT copied from the repo -- this code does not exist yet.
    if runs < 2:                      # :763 -- stays OUTSIDE the try (nothing registered yet)
        return [StepResult(op="__plan__", verdict=VERDICT_BAD, ...)]

    results: list[StepResult] = []              # :776
    destructive_gate_closed = False             # :777
    cleanup: list[Callable[[], None]] = []      # NEW (D-06) -- created BEFORE the try

    try:                                        # NEW -- no `except` clause of any kind
        for step in plan.steps:                 # :779 unchanged
            if not step.supported:
                results.append(_skip_result(step.op, step.reason, verdict=VERDICT_NA))
                continue
            if step.op in _DESTRUCTIVE_OPS and destructive_gate_closed:   # :784 unchanged
                results.append(_skip_result(step.op, _DESTRUCTIVE_GATE_REASON))
                continue
            result = _run_step(plan.name, step, operator, db, runs=runs, sampler=sampler)
            results.append(result)
            # A successful sdp_lock registers its unlock here (D-06/D-11).
            if step.op == OP_ID:                # :791 unchanged
                destructive_gate_closed = _id_step_closes_gate(result)
    finally:
        # Registration order (NOT LIFO -- see the ExitStack tradeoff).
        # Each callable in its OWN narrow try/except (D-10) so one failure
        # neither masks the in-flight exception nor strands the entries behind it.
        for cb in cleanup:
            try:
                cb()
            except (SerialError, HardwareOperationError, EpromOperationError):
                pass   # record the failed-unlock attempt HERE -- but NOT into `results`
                       # (Pitfall 2: `results` is returned by reference and reaches
                       #  six consumers at cli_handlers.py:2161-2216)

    return results                              # :794 unchanged
```

Three measured properties this shape relies on:

1. `finally` runs on `KeyboardInterrupt`/`SystemExit` and they still propagate — **no `except` needed**
   (criterion 1 + criterion 2 simultaneously). **[VERIFIED: measured]**
2. Mutating `results` in the `finally` **is** visible to the caller — which is why the drain must not
   do it. **[VERIFIED: measured]**
3. Per-item `try/except` continues the drain; `ExitStack` would not (it re-raises and reverses order).
   **[VERIFIED: measured]**

### The `visit_ExceptHandler` deny-rule (D-09)

Measured AST shapes, from an empirical run against a probe file plus the real `chip_test.py`:

| Source form | `ast.ExceptHandler.type` |
|-------------|--------------------------|
| `except:` | `None` |
| `except Exception:` | `ast.Name(id='Exception')` |
| `except BaseException:` | `ast.Name(id='BaseException')` |
| `except (ValueError, Exception):` | `ast.Tuple(elts=[Name('ValueError'), Name('Exception')])` |
| `except ValueError:` | `ast.Name(id='ValueError')` |

```python
# Shape recommendation, grounded in the measured _OrchestratorDenyVisitor:196-259 idiom.
# NOT copied from the repo -- this code does not exist yet.
_BROAD_EXCEPT_NAMES = frozenset({"Exception", "BaseException"})

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        offending: str | None = None
        t = node.type
        if t is None:
            offending = "bare except:"                       # also caught by ruff E722
        elif isinstance(t, ast.Name) and t.id in _BROAD_EXCEPT_NAMES:
            offending = f"except {t.id}:"
        elif isinstance(t, ast.Tuple):
            hits = sorted(
                m.id for m in t.elts
                if isinstance(m, ast.Name) and m.id in _BROAD_EXCEPT_NAMES
            )
            if hits:
                offending = f"except (... {', '.join(hits)} ...):"
        if offending is not None and not self._is_exempt(node):
            self.broad_except_violations.append(
                f"{self.filename}:{node.lineno}: broad exception handler `{offending}`"
            )
        self.generic_visit(node)
```

`self._is_exempt(...)` is Pitfall 1's required exemption for `chip_test.py:1035`. Wire the new bucket
into `main()` alongside the existing three at `:383-436` and extend the PASS line at `:438-441` — safe,
because the existing PASS-line assertions are loose (measured).

### `ExitStack` vs. a plain list — the measurement behind D-06/D-10

```python
# Source: measured empirically, python 3.12.13, this session
from contextlib import ExitStack
st = ExitStack()
st.callback(mk('first'))
st.callback(mk('second', boom=True))
st.callback(mk('third'))
st.close()
#   drain order:  ['third', 'second', 'first']     ← LIFO, registration order REVERSED
#   close() RAISED: RuntimeError cleanup second failed   ← escapes the finally, masking the original

# vs. a plain list + per-item narrow except:
#   recorded failure: b
#   drain order: ['a', 'b', 'c']                   ← registration order, nothing stranded, nothing masked
```

**[CITED: docs.python.org/3/library/contextlib.html]** — *"Each instance maintains a stack of registered
callbacks that are called in reverse order when the instance is closed"*; *"Unlike the other methods,
callbacks added this way cannot suppress exceptions (as they are never passed the exception details)"*;
*"Added in version 3.3."*

---

## Runtime State Inventory

**Not a rename/refactor/migration phase in the state-carrying sense** — but this phase *does* add new
op **strings** to a vocabulary, which is the adjacent hazard (a new string that other systems must
learn). The inventory is therefore completed rather than omitted, and every category is answered
explicitly.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | **None.** The `dev test` artifacts are write-only per run: `dev-test-<chip>.json` and `.md` are overwritten at `cli_handlers.py:2189, 2205` under `get_config_dir()/reports`. No database, no ChromaDB/Mem0 collection, no keyed store holds an op string. Verified: no op string is a lookup key anywhere. | none |
| **Live service config** | **None.** No n8n workflow, Datadog service, Tailscale ACL, or Cloudflare tunnel references `dev test` op strings. This phase is host-local Python with no service registration. | none |
| **OS-registered state** | **None.** No Task Scheduler entry, pm2 process, launchd plist, or systemd unit references the op vocabulary. | none |
| **Secrets / env vars** | **Three read, none renamed:** `FIRESTARTER_DEVTEST_SRC` (`:86`), `FIRESTARTER_DEVTEST_HANDLER` (`:98`), `FIRESTARTER_DEVTEST_SUBMIT` (`:113`), plus `FIRESTARTER_CONFIG_DIR` and `FIRESTARTER_FW_ROOT` (ci_parity leg 1). All keep their names; the new fourth bucket reuses the existing seams. **No new env var.** | none |
| **Build artifacts / installed packages** | **One consideration.** `pip install -e .` is an editable install, so `firestarter/*.py` edits take effect without reinstall. But a **new test file** is not packaged and needs no reinstall either. No `egg-info` staleness risk, no compiled artifact, no `.hex` (firmware untouched). | none |
| **Cross-repo state (added category)** | **`firestarter/` firmware repo is not touched at all.** Verified: this phase edits only `firestarter_app/`. `_assert_host_only` (`check_devtest_orchestrator.py:321`) mechanically enforces that no scan target resolves into the firmware sibling. No lockstep, no `.hex` re-cut, no `messages.toml` regen. | none |

**The canonical question — "after every file in the repo is updated, what runtime systems still have the
old string cached, stored, or registered?"** **Answer: none.** This phase *adds* two op strings rather
than renaming any, and the seven existing strings are unchanged. The only "system that must learn the
new string" is the set of op-keyed registries inside `chip_test.py` — which is precisely what LEG-15's
parity test mechanizes, and precisely why §"The P-23 Registry Census" matters.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | ✓ | **3.12.13** (devcontainer) | — ⚠ CI runs 3.9/3.11; mypy targets 3.10. See below. |
| `pytest` | every behavioral proof | ✓ | installed; `testpaths=["tests"]` | — |
| `ruff` | ci_parity leg 3 | ✓ | **0.16.0** | — |
| `mypy` | ci_parity leg 4 | ✓ (exits 2 locally) | pinned `<3` | **`tools/ci_replica_venv.sh`** — the only local path to a real count |
| `syrupy` | existing snapshot tests | ✓ | 5.5.3 | — (do not add snapshots) |
| `git` submodule `firestarter_app` on `gsd/v1.30-sdp-surface-retirement` | all edits | ✓ | @ `42a1971` | — |
| `firestarter/` firmware sibling | `test_sdp_table_parity.py`'s `@requires_fw` legs only | ✓ present | — | ci_parity leg 1 simulates absence via `FIRESTARTER_FW_ROOT=<empty>` |
| Programmer board on `/dev/ttyACM*` / `/dev/ttyUSB*` | **nothing in this phase** | ✗ **not attached** (verified) | — | **Correct state.** A board attached makes `test_no_programmer_found_*` go RED and would corrupt the no-board condition legs 1/2 depend on. |
| Node (for `gsd-tools`) | planning tooling only | ✓ via `.claude/gsd-core/bin/gsd-tools.cjs` | not on PATH | invoke via `node <path>` |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:**
- **A real local mypy error count.** The devcontainer's python 3.12 + numpy 2.5.1 makes leg 4 exit 2
  (correctly — the hardened gate refusing to report a truncated run). Fallback:
  `firestarter_app/tools/ci_replica_venv.sh`. **This is mandatory before committing**, given headroom 3.
- **Python version parity.** Local 3.12 vs CI 3.9/3.11 masks stdlib-API and syntax-floor defects.
  Fallback: `ruff` is pinned `target-version = "py39"` (so it catches 3.10+ *syntax*), but **not** a
  3.10+ *stdlib API*. Concretely relevant here: `exc.add_note()` (3.11+) and
  `Callable` import source. Use `from typing import Callable` or
  `collections.abc.Callable` under the existing `from __future__ import annotations` (`:27`) — the
  latter is safe in annotations on 3.9 **only** because of that future import.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` (version per repo pin); `syrupy` 5.5.3 present for existing snapshots only |
| Config file | `firestarter_app/pyproject.toml` → `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| Quick run command | `cd firestarter_app && python3 -m pytest tests/test_chip_test.py tests/test_check_devtest_orchestrator.py -q` |
| Full suite command | `cd firestarter_app && python3 -m pytest tests/ -q` |
| CI-parity recipe | `cd firestarter_app && bash tools/ci_parity.sh` (4 legs; **leg 4 exit 2 is expected locally**) |
| Baseline | full suite passes; **1297 tests collected** across **88 test files**; **30 syrupy snapshots passed**; no board attached |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LEG-09 | gate-closed-from-start ⇒ `sdp_lock` SKIPPED **and** `sdp_unlock` never attempted | unit | `pytest tests/test_chip_test_sdp_leg.py -k gate_closed_from_start -x` | ❌ Wave 0 |
| LEG-09 | lock-ran-then-gate-closes ⇒ `sdp_unlock` **still** attempted (via the drain) | unit | `pytest tests/test_chip_test_sdp_leg.py -k lock_ran_then_gate_closes -x` | ❌ Wave 0 |
| LEG-09 | `OP_SDP_UNLOCK not in _DESTRUCTIVE_OPS` as a standing invariant | unit | `pytest tests/test_chip_test_sdp_leg.py -k unlock_exempt_from_destructive -x` | ❌ Wave 0 |
| LEG-10 | mid-leg step raises ⇒ registry still drains | unit | `pytest tests/test_chip_test_sdp_leg.py -k finally_drains_on_exception -x` | ❌ Wave 0 |
| LEG-10 | `KeyboardInterrupt` ⇒ drain runs **and** KI propagates | unit | `pytest tests/test_chip_test_sdp_leg.py -k keyboard_interrupt -x` | ❌ Wave 0 |
| LEG-10 | `SystemExit` ⇒ drain runs **and** SystemExit propagates | unit | `pytest tests/test_chip_test_sdp_leg.py -k system_exit -x` | ❌ Wave 0 |
| LEG-10 | empty registry is a proven no-op (zero added calls, `results` unchanged) | unit | `pytest tests/test_chip_test_sdp_leg.py -k empty_registry_noop -x` | ❌ Wave 0 |
| LEG-10 | one failing cleanup does not strand the entries behind it, nor mask the original | unit | `pytest tests/test_chip_test_sdp_leg.py -k drain_continues_after_failure -x` | ❌ Wave 0 |
| LEG-11 | `SerialTimeoutError` mid-step ⇒ that one step `BAD`, `run_plan` returns | unit | `pytest tests/test_chip_test_sdp_leg.py -k serial_timeout_degrades_one_step -x` | ❌ Wave 0 |
| LEG-11 | `HardwareOperationError` mid-step ⇒ that one step `BAD`, `run_plan` returns | unit | `pytest tests/test_chip_test_sdp_leg.py -k hardware_error_degrades_one_step -x` | ❌ Wave 0 |
| LEG-11 | `ProgrammerNotFoundError` / `FirmwareOutdatedError` **escape** `run_plan` (run-fatal) | unit | `pytest tests/test_chip_test_sdp_leg.py -k run_fatal_escapes -x` | ❌ Wave 0 |
| LEG-11 | `AssertionError` (the `:1130` deliberate one) **still propagates** — no broad catch | unit | `pytest tests/test_chip_test_sdp_leg.py -k assertion_error_propagates -x` | ❌ Wave 0 |
| LEG-11 | **precedence matrix**: 9 exception classes → exact `(escapes?, verdict, error_code)` | unit | `pytest tests/test_chip_test_sdp_leg.py -k exception_precedence_matrix -x` | ❌ Wave 0 — **capture BEFORE the edit** |
| LEG-15 | every op × every policed registry ⇒ membership **or** reasoned exemption | unit | `pytest tests/test_op_registration_parity.py -x` | ❌ Wave 0 |
| LEG-15 | guard (a): an exemption with empty/missing reason **fails** | unit | `pytest tests/test_op_registration_parity.py -k empty_reason_fails -x` | ❌ Wave 0 |
| LEG-15 | guard (b): a stale `(op, registry)` row **fails** | unit | `pytest tests/test_op_registration_parity.py -k stale_row_fails -x` | ❌ Wave 0 |
| LEG-15 | guard (c): registry count ≠ declared constant **fails** | unit | `pytest tests/test_op_registration_parity.py -k declared_count -x` | ❌ Wave 0 |
| LEG-15 | **inversion guard** (this research's addition): a declared non-registry acquiring op vocabulary **fails** | unit | `pytest tests/test_op_registration_parity.py -k non_registry_still_has_no_ops -x` | ❌ Wave 0 |
| LEG-15 | non-vacuity: an altered in-memory registry copy **must** fail the parity assertion | unit | `pytest tests/test_op_registration_parity.py -k non_vacuous -x` | ❌ Wave 0 |
| crit. 4 | (D-13a) exact derived op sequence + per-step `(verdict, run_count)` vs in-test literal | unit | `pytest tests/test_chip_test_sdp_leg.py -k shipped_ops_sequence_unchanged -x` | ❌ Wave 0 — **capture BEFORE the edit** |
| crit. 4 | (D-13b) sentinel: `_dispatch_sdp` monkeypatched to raise; all **7** shipped ops must not reach it | unit | `pytest tests/test_chip_test_sdp_leg.py -k shipped_ops_never_reach_sdp_arm -x` | ❌ Wave 0 |
| crit. 2/5 | AST gate: **GREEN** on real `chip_test.py` (with the `:1035` exemption) | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k clean_source -x` | ✅ exists — must stay green |
| crit. 2/5 | AST gate: **RED** on a planted `except Exception:` | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k planted_broad_except -x` | ❌ Wave 0 |
| crit. 2/5 | AST gate: **RED** on a planted `except BaseException:` and on a tuple containing one | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k planted_broad_except_variants -x` | ❌ Wave 0 |
| crit. 2/5 | AST gate: the `:1035` exemption is **stale-proof** (fails if `_sample` is renamed) | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k exemption_stale -x` | ❌ Wave 0 |
| all | no new skip reason introduced | unit | `pytest tests/test_skip_census.py -x` | ✅ exists — fails closed |

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/test_chip_test.py tests/test_chip_test_sdp_leg.py tests/test_check_devtest_orchestrator.py tests/test_op_registration_parity.py -q`
- **Per wave merge:** `python3 -m pytest tests/ -q` **plus** `ruff check firestarter/ tests/` **plus**
  `ruff format --check firestarter/ tests/`
- **Phase gate:** `bash tools/ci_parity.sh` (record leg 4's exit 2 as expected, and record that **no
  board was attached**), plus a real mypy count via `tools/ci_replica_venv.sh` confirming
  `errors <= 35` and `checked >= 120`, then full suite green before `/gsd-verify-work`.

### What is testable purely in-process with the existing `app_context` fixture

- Every LEG-09/10/11 behavioral proof, and both D-13 legs. `run_plan` takes `(plan, operator, db)`
  explicitly, so a `Mock` operator plus the real DB (the existing `_REAL_DB` idiom, used at all 20
  `run_plan` call sites in `test_chip_test.py`) is sufficient. `make_app_context` / `app_context`
  (`conftest.py:229`, `:325`) supply the typed `AppContext` where a handler-level test is wanted.
- Planted-fault injection: set `operator.write_eprom.side_effect = SerialTimeoutError(...)`.
- The `_dispatch_sdp` sentinel: `monkeypatch.setattr(chip_test, "_dispatch_sdp", raiser)`.
- The parity test: pure introspection of `chip_test` module constants + an AST/grep pass over
  `chip_test.py` and the declared non-registry files. No fixture needed at all.

### What needs a subprocess

- **Every** proof about `tools/check_devtest_orchestrator.py`'s behavior. Its three env seams
  (`:86`, `:98`, `:113`) are `os.environ.get(...)` evaluated at **module import**, so
  `monkeypatch.setenv` + `import` is defeated by binding order and module caching. All 18 existing
  tests shell out; the new bucket's legs must too. Reuse the module's existing `_run_checker(env)`
  helper (`:72`).
- The `FIRESTARTER_FW_ROOT=<empty dir>` sibling-absent condition (ci_parity leg 1).

### What is unrepresentable (Evidence Ceiling — must not be smoothed over)

Per `REQUIREMENTS.md` §"⚠ Evidence Ceiling" (lines 14–40):

- **A locked die is unrepresentable in either repo's stubs.** Both model the bus, never the die's
  protection state. **No test in this phase can prove SDP inhibition on silicon.** Fixtures can only
  pin the host's *response* to a scripted read-back.
- **The Phase 116 ground-truth trace harness is UNREACHABLE from the host** — it is a PlatformIO
  `[env:native]` Unity binary in the **firmware** repo. The host repo has no bus stub at all. So
  "emission proof" here means what `conftest.py`'s `build_frame` / `_FakeSerial` / `make_comm` can
  assert over a scripted wire — **not** a bus trace. This phase does not even reach that far: it
  asserts on an `EpromOperator` **double**, one layer above the wire.
- **Protection state is not readable on this family** (Phase 117 D-05, Phase 119 D-12), which is D-03's
  basis for excluding SDP ops from the multi-run comparison policy.
- `0x0D` stays `UNVERIFIED`; **no AT28C part has ever been in operator inventory.**

**The honest claim this phase's validation supports, stated for the record:** *the mechanism cannot
strand a chip or lose a report to a transport error, and the op registries fail closed.* It proves
**nothing** about SDP behavior on silicon. Any artifact claiming more is the v1.22 C-5 overclaim class.

### Criterion-by-Criterion Proof Map

| ROADMAP criterion | Proven by | Honest caveat |
|---|---|---|
| **1.** mid-leg raise ⇒ cleanup still drains, incl. `KeyboardInterrupt`/`SystemExit` | `finally_drains_on_exception`, `keyboard_interrupt`, `system_exit` | On the KI path the **report is forfeited** (D-07): `results = run_plan(...)` at `:2164` never completes. State plainly. |
| **2.** `SerialError`/`HardwareOperationError` degrade one step; no bare `except`; `AssertionError` still loud; Ctrl-C stays Ctrl-C | planted-fault test per class + `assertion_error_propagates` + `exception_precedence_matrix` + the AST gate's RED/GREEN legs | The AST gate needs the `chip_test.py:1035` exemption (Pitfall 1) or it fails on clean source. `except:` was already gated by ruff E722; the **new** coverage is `Exception`/`BaseException`. |
| **3.** `sdp_unlock` absent from `_DESTRUCTIVE_OPS`, two tests | `gate_closed_from_start`, `lock_ran_then_gate_closes`, `unlock_exempt_from_destructive` | D-11: in 133 the absence is **forward-protection for Phase 134**, not a live gated path. Do not imply otherwise. |
| **4.** shipped ops byte-identical, `group=None` takes pre-existing path at zero added branching cost | D-13a in-test literal + D-13b sentinel + `exception_precedence_matrix` | **D-05 makes the `group=None` wording VACUOUS** — there is no `group` field, so no op has `group=None`. Record that the *intent* was met by a different mechanism; do **not** restate the literal words as tested. Also: "byte-identical" must be scoped to *assertions/behavior unchanged*, never "the file did not change" (D-13). |
| **5.** op-registration parity test fails on an op left out of any required registry; "eight fail-open registries → one fail-closed gate" | `test_op_registration_parity.py` + its 4 guards + non-vacuity leg | **The "eight/ten registries" count is measurably wrong** — 3 of P-23's 10 rows have no op vocabulary at all, and 2 more are verdict-keyed or prose. See §"The P-23 Registry Census". Report the measured count; do not inherit "eight". |

### Wave 0 Gaps

- [ ] `tests/test_chip_test_sdp_leg.py` — new module; covers LEG-09, LEG-10, LEG-11 + criterion 4
      (D-13a/b). Uses the existing `app_context` / `_REAL_DB` idioms; **no new fixture factory needed.**
- [ ] `tests/test_op_registration_parity.py` — new module; covers LEG-15 + D-12's 4 guards + non-vacuity.
      **Must not use `@requires_fw`** (host-local, so it runs in CI, unlike its template).
- [ ] `tests/test_check_devtest_orchestrator.py` — **append** ~4 legs for the new broad-except bucket
      (planted `Exception`, planted `BaseException`, planted tuple member, exemption-stale). Subprocess only.
- [ ] **Decide and record the `chip_test.py:1035` exemption mechanism** (Pitfall 1) — a Wave-0 design
      output, because both the gate and its tests depend on it.
- [ ] **Decide and record that the drain does not append into `results`** (Pitfall 2) — a Wave-0 design
      output, because the LEG-10 tests' observation mechanism depends on it.
- [ ] **Capture the pre-edit baselines** (`exception_precedence_matrix`, `shipped_ops_sequence_unchanged`)
      **before** touching `chip_test.py`. These are criterion 4's only real evidence and are worthless
      if written after the change.
- [ ] Framework install: **none needed.**

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Unmapped op falls through to `operator.erase_eprom()` and reports `OK` | Fail-closed allow-list + terminal refusal `StepResult` + terminal `AssertionError` | Phase 121 (121-02, T-121-05/06/07) | The idiom D-01 clones. Never reintroduce a bare `else`. |
| `dev test` had 4 flags (`--destructive`, `--output-dir`, `-y`, `--submit`) | **Zero options**; always writes; report always persisted and always offered for submission | Phase 121 D-01/D-05 | LEG-01's "no new command-line option" is inherited, not new. |
| `_MULTI_RUN_OPS` was documented-but-dead (zero references tree-wide) | Live dispatch allow-list gated in **two** places | Phase 121 | "Documented dead" is this module's known failure mode — a new frozenset must be *referenced*, and the reference *tested*. |
| `dev sdp` host surface | Retired; `sdp_honesty.py` carries the caveats | Phase 132 (RETIRE-*) | This phase must not break `sdp_honesty.py`'s import surface, and must not call it (Phase 134 does). |
| Ad-hoc per-module test factories | Typed `make_app_context` + `app_context` fixture | Phase 132 D-10 | The new modules' fixture base. |
| mypy watermark 35, count 29→32 | 32 measured; watermark unchanged at 35 | Phase 132 D-09 | Headroom 3. Ratcheting to 32 is deferred and **unowned**. |

**Deprecated / outdated:**
- **`.planning/codebase/TESTING.md`** — asserts "no Python unit tests"; measured 88 test files. Do not cite.
- **`research/SUMMARY.md` §"Phase 133"** (line 726) — describes ROADMAP Phase **134**. Cite by P-number.
- **P-20's `run_plan:757-802`, P-23's `_MULTI_RUN_OPS :657` and `_dispatch_step :903-948`** — all
  superseded; corrected values re-measured and confirmed in §"Measured Anchors".
- **P-20 prevention #2's "wide enough to catch `BaseException`"** — unnecessary and self-defeating; a
  bare `finally` suffices and is what criterion 2 requires.
- **P-23's row 7 rationale ("an unrendered op is invisible in the report")** — measurably wrong in
  mechanism; the renderer is fully generic.
- **`# noqa: BLE001` at `chip_test.py:1035`** — inert; `BLE` is not in ruff's `select`.

---

## Sources

### Primary (HIGH confidence)
- **Direct source measurement**, `firestarter_app` @ `42a1971`, branch `gsd/v1.30-sdp-surface-retirement`:
  `firestarter/chip_test.py`, `exceptions.py`, `cli_handlers.py`, `diagnostic_report.py`,
  `chip_resolver.py`, `submit.py`; `tools/check_devtest_orchestrator.py`, `parse_devtest_issue.py`,
  `ci_parity.sh`; `tests/conftest.py`, `test_chip_test.py`, `test_check_devtest_orchestrator.py`,
  `test_sdp_table_parity.py`, `test_skip_census.py`; `pyproject.toml`.
- **Empirical execution this session:** `ast` shape enumeration across probe + real source;
  `try/finally` behavior on `KeyboardInterrupt`; `return`-in-`try` + mutate-in-`finally` aliasing;
  `ExitStack` drain order + re-raise; `ruff 0.16.0 check` against a three-form broad-except probe;
  full `pytest tests/` suite run; `ls /dev/ttyACM* /dev/ttyUSB*`.
- `.planning/REQUIREMENTS.md` §"Evidence Ceiling" (14–40) and §LEG (186–247).
- `.planning/phases/133-sdp-leg-mechanism/133-CONTEXT.md` — D-01…D-13, the locked constraints.

### Secondary (MEDIUM confidence)
- **[CITED: https://docs.python.org/3/library/contextlib.html]** — `ExitStack.callback()` LIFO ordering,
  inability to suppress exceptions, "Added in version 3.3". Cross-checked against the empirical run.
- `.planning/research/PITFALLS.md` §P-06, P-07, P-08, P-14, P-20, P-23, P-24 — cited **by P-number**.
  Three of P-20/P-23's anchors and three of P-23's registry rows are corrected above by measurement.
- `.planning/phases/132-…/132-CONTEXT.md` (D-02, D-09, D-10, D-13) and `132-CI-GREEN.md`
  (`mypy errors: 32 (watermark: 35)`, `checked 122 source files`).

### Tertiary (LOW confidence)
- `.planning/graphs/graph.json` — queried; **806 hours old, 883 commits behind** (`f4150b8` vs
  `051333f`, i.e. predating this entire milestone). **Not used for any claim.** Every relationship it
  might have suggested was instead measured directly from source.
- `.planning/codebase/TESTING.md` — **not cited; known severely stale** (see §"State of the Art").

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A new plain test module contributes **0** mypy errors (`chip_test.py` is in neither strict island; global `check_untyped_defs = false`) | Pitfall 7 | Headroom is 3. If it contributes ≥4, ci_parity leg 4 / the watermark gate fails. **Mitigation is mandatory, not optional:** measure with `tools/ci_replica_venv.sh` before committing. |
| A2 | A `SerialError` is not currently reachable from `resolve_chip` (pure DB lookup + transform) | Pitfall 3 | If reachable, LEG-11 has a live hole outside `_run_step`'s `try` and D-08's clauses do not close it. Verified by reading `chip_resolver.py:16-49`, not by exhaustive call-graph analysis. |
| A3 | The 9-class exception precedence matrix captures today's behavior completely | Pitfall 4 | An unlisted class could change verdict silently, breaking criterion 4 invisibly. Mitigated by capturing the baseline **before** the edit. |
| A4 | Placing the new test module(s) in `tests/` does not push `checked source files` below `MIN_CHECKED_SOURCE_FILES = 120` (it can only rise) | Pitfall 7 | Direction is certain (files are added); the exact new count is not measured. Two new modules consume both slots of the 122-vs-120 margin exactly. |
*(A5 and A6 were resolved by measurement during this session and are recorded below the table rather
than left as assumptions.)*

**Resolved, no longer assumed:**
- **Project skills: none exist.** `/workspaces/.claude/` contains `agents/`, `channels/`, `commands/`,
  `gsd-core/` — **there is no `skills/` directory and no `rules/` directory anywhere under
  `.claude/`**. So no project skill imposes constraints on this phase. **[VERIFIED: `ls -R`, `find -name rules -type d`]**
- **Suite size: 1297 tests collected across 88 test files**, full suite green, 30 syrupy snapshots
  passing, no board attached. **[VERIFIED: `pytest --collect-only` + full run this session]**

**Everything else in this document is `[VERIFIED: measured this session]` or
`[CITED: docs.python.org]`.** No package names, versions, compliance requirements, retention policies,
or performance targets are asserted from training knowledge — this phase has none of those surfaces.

---

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md` and `/workspaces/firestarter_app/CLAUDE.md`. These carry the
same authority as locked decisions.

| Directive | Source | Bearing on this phase |
|-----------|--------|-----------------------|
| Meta-repo tracks only `.planning/` and `.claude/`; sub-repos are **not** committed there | meta CLAUDE.md | RESEARCH.md commits to the meta repo; all code commits go **inside** `firestarter_app` on its own milestone branch (`gsd/v1.30-sdp-surface-retirement`, **not** the meta branch name). |
| `firestarter/` (firmware) and `firestarter_app/` are separate repos with separate CLAUDE.md files | meta CLAUDE.md | **Host-only phase. Firmware untouched.** Mechanically asserted by `_assert_host_only` (`:321`). |
| Serial-protocol changes must be kept in sync between `serial_comm.py` and `firestarter.cpp` | meta CLAUDE.md | **Not triggered** — this phase adds no wire command and no protocol change. |
| `constants.py` ↔ `firestarter.h` flag/command-code sync; `CTRL_*` ↔ `rurp_pinout.h`; `REVISION_*` ↔ `rurp_shield.h` | meta + app CLAUDE.md | **Not triggered** — no constant in any mirrored block is touched. `OP_SDP_*` are engine-local op strings, not wire constants. |
| `chip_database.json` is generated — do NOT edit by hand | app CLAUDE.md | Not triggered; the parity test reads module constants, never the DB. |
| **Tooling gate:** `ruff check` + `ruff format --check` + `mypy` (strict on 9 modules) + `pytest --cov-fail-under=70`, enforced by `.github/workflows/ci.yml` on every PR; `pre-commit` mirrors the hook order | app CLAUDE.md | **Directly binding.** Note `--cov-fail-under=70` is a CI step that `ci_parity.sh` legs 1/2 deliberately do **not** mirror (script header) — so local green does not prove the coverage floor. New code must carry tests, which it does by construction here. |
| `eprom_operations.py` is **ring-fenced** (deliberately excluded from the mypy strict island) | app CLAUDE.md + `pyproject.toml` + operator decision 2026-08-03 (`FUT-MYPY-02`) | **Call `sdp_lock`/`sdp_unlock`; never type-fix that module.** |
| `channel.py`: **never gate on an env var — it fails open** | app CLAUDE.md | Bears on the AST gate's env seams: they are a **test-injection** seam for a build-time checker, never a feature gate, and the checker fails **closed** on an empty scan (`:411-417`). Preserve that property when adding the fourth bucket. |
| `firestarter/` module list and responsibilities (`chip_test.py` is the bench-free pure-compute engine) | app CLAUDE.md | Reinforces Pitfall 2: this module "emits no print/render/CLI output" and has no logger. Do not give it one casually. |

---

## Open Questions (RESOLVED)

*All five were settled after this research session — three by operator decision at plan time
(CONTEXT.md D-14/D-15/D-16), two by the plans themselves. Each carries its resolution inline.*

1. **Where do the LEG-09/10/11 + D-13 behavioral tests live — a new module or appended to
   `test_chip_test.py`?**
   **✔ RESOLVED — CONTEXT.md D-15 (operator, 2026-08-04):** a new `tests/test_chip_test_sdp_leg.py`, the
   recommendation below, with the two-slot `MIN_CHECKED_SOURCE_FILES` cost accepted and stated.
   - What we know: CONTEXT.md's `<code_context>` says "this phase's **new test module**" (singular) and
     names `conftest.py`'s `app_context` as its base. `test_chip_test.py` is 1958 lines with 20
     `run_plan` call sites and the `_REAL_DB` idiom the new tests want.
   - What's unclear: whether the singular "new test module" meant `test_op_registration_parity.py`
     alone (which D-12 names explicitly) or that plus a second SDP-leg module.
   - Recommendation: **a new `tests/test_chip_test_sdp_leg.py`**, for isolation and explicit
     file-count accounting — but flag the cost (two new files consume both `MIN_CHECKED_SOURCE_FILES`
     slots, A4) and let the planner overrule on that basis. Either choice satisfies every criterion.

2. **Which exemption mechanism for `chip_test.py:1035`?** (Pitfall 1)
   **✔ RESOLVED — CONTEXT.md D-14 (operator, 2026-08-04):** option (a), the exemption table with mandatory
   reason strings + a stale-row assertion. Implemented in plan `133-05`, which additionally requires the
   exemption and the deny-rule to land in the **same commit** so the gate is never committed RED.
   - What we know: four options measured, with tradeoffs; option (c) (narrow `_sample`'s catch) is
     ruled out by criterion 4 because `_make_sampler` is live in production and the "swallow all"
     contract is documented.
   - What's unclear: whether the operator/planner prefers the exemption-table shape (a) — which shares
     an idiom with D-12 — or the watermark shape (d), which is house-consistent with the mypy gate.
   - Recommendation: **(a), an exemption table with mandatory reason strings + a stale-row assertion.**
     One new concept for the whole phase instead of two.

3. **Should the parity test police `_dispatch_multi_run`'s inner run-loop branches (`:1112-1132`) as a
   sixth registry?** (§Registry Census)
   **✔ RESOLVED — plan `133-06`:** yes, included as a policed registry with `OP_SDP_*` carrying D-03's
   exclusion reason, per the recommendation below.
   - What we know: it is a genuine op-keyed site with a terminal `AssertionError`; P-23 does not list
     it; SDP ops are structurally excluded from it by D-03.
   - What's unclear: whether including it inflates the declared-count constant past what LEG-15's
     "all required registries" naturally means.
   - Recommendation: **include it, with `OP_SDP_*` carrying D-03's exclusion reason** — it is exactly
     the kind of real registry P-23 missed, and the exemption reason already exists.

4. **How is the failed-unlock attempt recorded, given no logger and no `add_note`?** (Pitfall 2)
   **✔ RESOLVED — CONTEXT.md D-16 (operator, 2026-08-04):** test-observability suffices in 133; no logger
   is added. Plan `133-04` reconciles D-10's "recorded" against D-16 in its action text, and `133-07`
   records it as a **non-literal honouring** of D-10 plus the residual that a failed unlock is not
   user-visible until Phase 134's `HELD`/`NOT-RUN` field.
   - What we know: it must not go into `results`; `chip_test.py` has no logging surface; `add_note` is
     3.11+ and the floor is 3.9.
   - What's unclear: whether "recorded" in D-07 requires any production-visible artifact in Phase 133,
     or whether test-observability suffices until Phase 134 builds the report field (LEG-12).
   - Recommendation: **test-observability suffices in 133** (both criterion 1 and criterion 3 ask "was
     the unlock attempted?", answerable on the operator double), and the phase record should state
     plainly that a failed unlock is **not** user-visible until Phase 134's `NOT-RUN`/`HELD` field.
     This is a real, honest residual — the second one D-07 creates — and it should be written down
     rather than papered over with a logger added for appearance.

5. **Does the `runs < 2` early return at `:763` need to be inside the `try`?**
   **✔ RESOLVED — plan `133-04`:** **outside** the `try`, decided explicitly rather than incidentally; the
   guard's position and behavior stay byte-identical (criterion 4).
   - What we know: it returns before `results` or the registry exist, so there is nothing to drain.
   - What's unclear: nothing substantive — but it is exactly the kind of "where does the `try` open"
     detail the ROADMAP flagged as open, so it should be decided **explicitly** in the plan rather than
     incidentally by whoever types it.
   - Recommendation: **outside.** Keep the guard's current position and behavior byte-identical
     (criterion 4).

---

## Metadata

**Confidence breakdown:**
- **Standard stack: HIGH** — zero new dependencies; every mechanism is stdlib or an already-pinned dev
  tool, each verified by direct execution in this environment (`ruff --version`, `ast` walk, `pytest`
  run). Nothing is asserted from training knowledge.
- **Architecture: HIGH** — the responsibility map, the data-flow diagram, and every line anchor were
  read from the live source at `42a1971`. All 24 anchors CONTEXT.md flagged verified exactly.
- **Pitfalls: HIGH** — Pitfalls 1, 2, 6 and the `SerialError`-subclass census were each established by
  measurement or empirical execution, not inference. Pitfall 3 and 4 are read-from-source with a named
  residual assumption (A2, A3).
- **Registry census: HIGH** — an exhaustive repo-wide grep, reported with the exact commands so it can
  be re-run and falsified.
- **Validation architecture: MEDIUM-HIGH** — the framework, commands, baseline, and subprocess/in-process
  split are measured; the specific test names are proposals the planner may rename.
- **mypy contribution (A1): LOW** — explicitly unmeasured, and flagged as requiring
  `tools/ci_replica_venv.sh` before commit. This is the one number in this document that must not be
  trusted as-is.

**Research date:** 2026-08-04
**Valid until:** ~2026-09-03 for the stack/patterns (stable, stdlib-only), but **line numbers expire on
the next commit to `chip_test.py`** — re-measure at execute time, every time.
