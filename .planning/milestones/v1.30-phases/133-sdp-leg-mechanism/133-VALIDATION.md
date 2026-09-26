---
phase: 133
slug: sdp-leg-mechanism
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-04
approved: 2026-08-04
---

# Phase 133 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `133-RESEARCH.md` §"Validation Architecture" (measured 2026-08-04 @ `42a1971`).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` (repo pin); `syrupy` 5.5.3 present for **existing** snapshots only — do NOT add snapshots (Phase 132 D-13: unused snapshots fail the whole session) |
| **Config file** | `firestarter_app/pyproject.toml` → `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| **Quick run command** | `cd firestarter_app && python3 -m pytest tests/test_chip_test.py tests/test_chip_test_sdp_leg.py tests/test_check_devtest_orchestrator.py tests/test_op_registration_parity.py -q` |
| **Full suite command** | `cd firestarter_app && python3 -m pytest tests/ -q` |
| **CI-parity recipe** | `cd firestarter_app && bash tools/ci_parity.sh` — 4 legs; **leg 4 exit 2 is expected locally** (numpy 2.5.1 / py3.12); a real mypy count needs `tools/ci_replica_venv.sh` |
| **Estimated runtime** | ~quick: seconds · full suite: 1297 tests |
| **Measured baseline (pre-edit)** | full suite **green**; **1297 tests** across **88 test files**; **30 syrupy snapshots** pass; **no board attached** (correct state — a live board turns `test_no_programmer_found_*` RED) |

---

## Sampling Rate

- **After every task commit:** the Quick run command above
- **After every plan wave:** `python3 -m pytest tests/ -q` **plus** `ruff check firestarter/ tests/` **plus** `ruff format --check firestarter/ tests/`
- **Before `/gsd-verify-work`:** full suite green, **plus** `bash tools/ci_parity.sh` (record leg 4's exit 2 as expected and record that no board was attached), **plus** a real mypy count via `tools/ci_replica_venv.sh` confirming `errors <= 35` **and** `checked >= 120`
- **Max feedback latency:** < 60s for the quick run

---

## Per-Task Verification Map

Task IDs are assigned by the planner; `Plan`/`Wave`/`Task ID` are filled at execute time. Requirement
column is authoritative: **only** LEG-09, LEG-10, LEG-11, LEG-15 may be marked Complete by this phase.

| Task ID | Plan | Wave | Requirement | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | crit. 4 | pre-edit exception-precedence baseline captured **before** `chip_test.py` is touched | unit | `pytest tests/test_chip_test_sdp_leg.py -k exception_precedence_matrix -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | crit. 4 | pre-edit derived op sequence + per-step `(verdict, run_count)` vs in-test literal | unit | `pytest tests/test_chip_test_sdp_leg.py -k shipped_ops_sequence_unchanged -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-09 | gate-closed-from-start ⇒ `sdp_lock` SKIPPED **and** `sdp_unlock` never attempted | unit | `pytest tests/test_chip_test_sdp_leg.py -k gate_closed_from_start -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-09 | lock-ran-then-gate-closes ⇒ `sdp_unlock` **still** attempted via the drain | unit | `pytest tests/test_chip_test_sdp_leg.py -k lock_ran_then_gate_closes -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-09 | `OP_SDP_UNLOCK not in _DESTRUCTIVE_OPS` as a standing invariant | unit | `pytest tests/test_chip_test_sdp_leg.py -k unlock_exempt_from_destructive -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-10 | mid-leg step raises ⇒ registry still drains | unit | `pytest tests/test_chip_test_sdp_leg.py -k finally_drains_on_exception -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-10 | `KeyboardInterrupt` ⇒ drain runs **and** KI propagates unchanged | unit | `pytest tests/test_chip_test_sdp_leg.py -k keyboard_interrupt -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-10 | `SystemExit` ⇒ drain runs **and** SystemExit propagates unchanged | unit | `pytest tests/test_chip_test_sdp_leg.py -k system_exit -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-10 | empty registry is a proven no-op: zero added calls, `results` unchanged | unit | `pytest tests/test_chip_test_sdp_leg.py -k empty_registry_noop -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-10 | one failing cleanup neither strands the entries behind it nor masks the original exception | unit | `pytest tests/test_chip_test_sdp_leg.py -k drain_continues_after_failure -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-11 | `SerialTimeoutError` mid-step ⇒ that **one** step BAD, `run_plan` returns | unit | `pytest tests/test_chip_test_sdp_leg.py -k serial_timeout_degrades_one_step -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-11 | `HardwareOperationError` mid-step ⇒ that **one** step BAD, `run_plan` returns | unit | `pytest tests/test_chip_test_sdp_leg.py -k hardware_error_degrades_one_step -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-11 | `ProgrammerNotFoundError` / `FirmwareOutdatedError` **escape** `run_plan` (run-fatal, not 6 BAD steps) | unit | `pytest tests/test_chip_test_sdp_leg.py -k run_fatal_escapes -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-11 | the deliberate `AssertionError` still propagates — no broad catch | unit | `pytest tests/test_chip_test_sdp_leg.py -k assertion_error_propagates -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | crit. 4 | (D-13b) sentinel: `_dispatch_sdp` monkeypatched to raise; all **7** shipped ops must not reach it | unit | `pytest tests/test_chip_test_sdp_leg.py -k shipped_ops_never_reach_sdp_arm -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-15 | every op × every policed registry ⇒ membership **or** reasoned exemption | unit | `pytest tests/test_op_registration_parity.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-15 | guard (a): exemption with empty/missing reason **fails** | unit | `pytest tests/test_op_registration_parity.py -k empty_reason_fails -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-15 | guard (b): a stale `(op, registry)` row **fails** | unit | `pytest tests/test_op_registration_parity.py -k stale_row_fails -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-15 | guard (c): registry count ≠ declared constant **fails** | unit | `pytest tests/test_op_registration_parity.py -k declared_count -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-15 | inversion guard: a declared **non**-registry acquiring op vocabulary **fails** | unit | `pytest tests/test_op_registration_parity.py -k non_registry_still_has_no_ops -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | LEG-15 | non-vacuity: an altered in-memory registry copy **must** fail the parity assertion | unit | `pytest tests/test_op_registration_parity.py -k non_vacuous -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | crit. 2/5 | AST gate **GREEN** on real `chip_test.py` with the D-14 `_sample` exemption | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k clean_source -x` | ✅ exists — must stay green | ⬜ pending |
| TBD | TBD | — | crit. 2/5 | AST gate **RED** on a planted `except Exception:` | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k planted_broad_except -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | crit. 2/5 | AST gate **RED** on planted `except BaseException:` and on a tuple containing one | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k planted_broad_except_variants -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | crit. 2/5 | D-14 guard (b): the `_sample` exemption is **stale-proof** — fails if `_sample` is renamed | integration (subprocess) | `pytest tests/test_check_devtest_orchestrator.py -k exemption_stale -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | all | no new skip reason introduced | unit | `pytest tests/test_skip_census.py -x` | ✅ exists — fails closed | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **Capture the two pre-edit baselines BEFORE `chip_test.py` is touched** — `exception_precedence_matrix` (9 exception classes → exact `(escapes?, verdict, error_code)`) and `shipped_ops_sequence_unchanged` (exact derived op sequence + per-step `(verdict, run_count)` against an **in-test literal**, never a syrupy snapshot). These are criterion 4's only real evidence and are **worthless if written afterward**.
- [ ] `tests/test_chip_test_sdp_leg.py` — new module (D-15). LEG-09/10/11 + criterion 4 (D-13a/b). Uses the existing `app_context` (`conftest.py:325`) / `_REAL_DB` idioms — **no new fixture factory needed**.
- [ ] `tests/test_op_registration_parity.py` — new module. LEG-15 + D-12's guards + the inversion guard + non-vacuity. **Must not use `@requires_fw`** (host-local, so it runs in CI, unlike its `test_sdp_table_parity.py` template).
- [ ] `tests/test_check_devtest_orchestrator.py` — **append** ~4 legs for the new broad-except bucket. **Subprocess only** — its three env seams (`:86`, `:98`, `:113`) bind at module import, so `monkeypatch.setenv` is defeated; reuse the module's existing `_run_checker(env)` helper (`:72`).
- [ ] **Framework install: none needed.**

*Settled, no longer Wave-0 design questions:* the `chip_test.py:1035` exemption mechanism (**D-14** — exemption table with mandatory reason + stale-row guard) and test-module placement (**D-15**). Still a required plan-level decision: **the drain must not append into `results`** (research Pitfall 2 — seven consumers at `cli_handlers.py:2161-2216`; latent in 133, detonates in 134).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real mypy count within the watermark | crit. 4 / phase gate | The devcontainer's own py3.12 + numpy 2.5.1 run exits 2 and **cannot** produce a count; A1 (a new plain test module contributes 0) is the one number research left **unmeasured** and flagged LOW | `cd firestarter_app && bash tools/ci_replica_venv.sh` — assert `errors <= 35` (headroom is **3**) and `checked >= 120` (margin is **2**, and D-15 spends both) |
| CI-parity recipe, no-board leg emphasized | ROADMAP cross-cutting | Ambient board state, not a scriptable assertion. ⚠ **`ci_parity.sh` has no discrete "no-board leg"** — research measured this; the board dimension is an ambient condition of legs 1/2. The instruction cannot be followed literally | `cd firestarter_app && bash tools/ci_parity.sh` with **no board attached** (the correct state — a live board turns `test_no_programmer_found_*` RED). Record leg 4's exit 2 as expected |

---

## Evidence Ceiling — what this phase's validation CANNOT prove

Per `REQUIREMENTS.md` §"⚠ Evidence Ceiling" (lines 14–40). **Must not be smoothed over in any artifact.**

- **A locked die is unrepresentable in either repo's stubs.** Both model the bus, never the die's protection state. **No test in this phase can prove SDP inhibition on silicon.**
- The Phase 116 ground-truth trace harness is **unreachable from the host** (a PlatformIO `[env:native]` Unity binary in the *firmware* repo). This phase asserts on an `EpromOperator` **double**, one layer above the wire.
- **Protection state is not readable on this family** (Phase 117 D-05, Phase 119 D-12) — D-03's basis.
- `0x0D` stays `UNVERIFIED`; **no AT28C part has ever been in operator inventory.**

**The honest claim this validation supports:** *the mechanism cannot strand a chip or lose a report to a
transport error, and the op registries fail closed.* It proves **nothing** about SDP behavior on silicon.
Any artifact claiming more is the v1.22 C-5 overclaim class.

Two further residuals belong in the phase record, not in a footnote:
1. **D-07:** after a Ctrl-C mid-leg the chip has an unlock *attempted* but the user sees **no `dev test` report at all** (`results = run_plan(...)` at `cli_handlers.py:2161` never completes).
2. **D-16:** a **failed** unlock is **not user-visible** until Phase 134's `HELD`/`NOT-RUN` field (LEG-12).
3. **D-05:** ROADMAP criterion 4's clause *"an op with `group=None` takes the exact pre-existing dispatch path"* is satisfied **vacuously** — there is no `group` field. The record must say the criterion's *intent* was met by a different mechanism and must **not** restate its literal words as tested.

---

## Validation Sign-Off

- [x] All tasks have an `<automated>` verify or a Wave 0 dependency — verified across `133-01` … `133-07` (17 tasks); every task carries `<verify><automated>`
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — every task has one
- [x] Wave 0 covers all ❌ references — `133-01` (wave 1) captures both pre-edit baselines with **zero** production edits, asserted by a git-diff acceptance criterion; `wave_0_complete` flips to `true` when `133-01` lands
- [x] No watch-mode flags
- [x] No new syrupy snapshot added (Phase 132 D-13) — D-13a uses an in-test literal (`_SHIPPED_OPS_SEQUENCE`)
- [x] Real mypy count obtained via `ci_replica_venv.sh`, not assumed (A1 is LOW confidence) — required by `133-01` and re-asserted by `133-07`
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-08-04 — plan-checker returned VERIFICATION PASSED (0 blockers) across all 7 plans.
