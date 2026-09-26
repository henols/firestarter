---
phase: 136
slug: dev-tools-channel-gating
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-05
approved: 2026-08-05
---

# Phase 136 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `136-RESEARCH.md` and `136-CONTEXT.md`, measured against
> `firestarter_app@2b7a702` on `gsd/v1.30-sdp-surface-retirement`.
> Modeled on `134-VALIDATION.md`'s shape.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (+ `pytest-cov`, `syrupy`) |
| **Config file** | `firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `addopts = "-ra -q"`) |
| **Quick run command** | `.venv/ci-replica/bin/python -m pytest tests/test_click_group_gate_hook.py tests/test_dev_tools_channel_gate.py tests/test_dev_group_channel_gating.py tests/test_dev_gate_reads_no_firmware_source.py -o addopts="" -q` |
| **Full suite command** | `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | ~10-15 s quick (adds 4 subprocess-heavy modules to the quick set) · ~150 s full |

⚠ **Always pass `-o addopts=""`.** `addopts` is `-ra -q`; doubling `-q` suppresses the count line and a
green run looks contentless.

⚠ **`tools/ci_replica_venv.sh` is the only local path to a real mypy count** — the devcontainer's own
mypy exits 2 against numpy, and the devcontainer is py3.12 while CI is py3.9/3.11.

⚠ **This phase's own proof mechanism IS subprocess spawning.** `test_dev_group_channel_gating.py` and
`test_click_group_gate_hook.py` both use `subprocess.run`/`CliRunner` — expect them to run slower per
test than a pure-unit module; this is intrinsic to D-04, not a performance regression to chase.

⚠ **No hardware is involved anywhere in this phase.** Unlike Phase 134, there is no evidence-ceiling
row and no silicon claim to avoid — every behavior here is a CLI/process-boundary fact.

---

## Sampling Rate

- **After every task commit:** quick run above (~10-15 s).
- **After every plan wave:** `tools/ci_replica_venv.sh` (all 5 legs). Record `mypy errors: N (watermark:
  35)` and `checked N source files` **every time** — headroom entering the phase is measured fresh by
  plan `136-01` Task 1 (RESEARCH §7: there is no number to inherit).
- **Before `/gsd-verify-work`:** `tools/ci_parity.sh` **and** `tools/ci_replica_venv.sh` both green, plus
  the before/after record in `136-CI-PARITY.md` (the 131/133/134 shape).
- **Max feedback latency:** ~15 s per commit · ~150 s per wave.

---

## Per-Task Verification Map

Wave numbers are pre-assigned by the planner (1→4, one plan per wave — worktree isolation is OFF
phase-wide, so waves express real dependency order, not parallelism).

| Req | Wave | Behaviour to prove | Test Type | Automated Command | File Exists | Status |
|-----|------|--------------------|-----------|--------------------|-------------|--------|
| — (design spike) | 1 | Click 8.3.3's `get_command` hook intercepts before Click's own generic error; a genuine typo still falls through; `resolve_command` needs no override | unit | `pytest tests/test_click_group_gate_hook.py -o addopts=""` | ❌ new | ⬜ pending |
| CHAN-06 (mechanism) | 1 | `dev_tools_enabled_by_env()` fails CLOSED on unset/empty/`"0"`/`"false"`/whitespace-padded/garbage; exact `"1"` only | unit | `pytest tests/test_dev_tools_channel_gate.py -o addopts=""` | ❌ new | ⬜ pending |
| CHAN-07 (partial, channel.py only) | 1 | `channel.py` itself calls no `open()` | unit | `pytest tests/test_dev_tools_channel_gate.py -k open -o addopts=""` | ❌ new | ⬜ pending |
| CHAN-05 | 2 | `dev()` docstring states `read`/`test` are stable-supported; USR-button line kept | unit | `pytest tests/test_cli_handlers.py -o addopts=""` | ✅ exists (edited) | ⬜ pending |
| CHAN-02 (mechanism) | 2 | 6 gated `@dev.command` blocks wrapped in `if _DEV_TOOLS_ENABLED:`; genuinely absent from the module namespace when closed | unit + syntax | `python -c "import ast; ast.parse(open('firestarter/cli_handlers.py').read())"` + `grep -c 'if _DEV_TOOLS_ENABLED:'` | ✅ exists (edited) | ⬜ pending |
| CHAN-03 (mechanism) | 2 | `_DevGroup.get_command` raises an informative `UsageError` for a known gated name; falls through for a real typo | unit | `pytest tests/test_cli_handlers.py -o addopts=""` (regression only — in-process can't prove the stable case) | ✅ exists (edited) | ⬜ pending |
| CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06 | 3 | Subprocess dual-channel proof: stable lists/registers only `read`+`test`, refuses gated names informatively; prerelease lists/registers all 8; the env override re-enables all 6 on simulated-stable | CLI subprocess | `pytest tests/test_dev_group_channel_gating.py -o addopts=""` | ❌ new | ⬜ pending |
| CHAN-07 | 3 | Comprehensive no-firmware-read assertion across `channel.py` + `cli_handlers.py`'s new symbols | unit (source scan) | `pytest tests/test_dev_gate_reads_no_firmware_source.py -o addopts=""` | ❌ new | ⬜ pending |
| — | 4 | `test_help_dev` snapshot re-baselined, diff-scoped to the docstring only | snapshot | `pytest tests/test_characterization.py -k test_help_dev -o addopts=""` | ✅ exists (edited) | ⬜ pending |
| — | 4 | Phase-close CI-parity + full regression record | doc + full suite | `tools/ci_parity.sh && tools/ci_replica_venv.sh` | ✅ exists (edited) | ⬜ pending |
| — | all | `test_py32_channel_gating.py` (the pattern this phase adapts) stays green throughout | unit | `pytest tests/test_py32_channel_gating.py -o addopts=""` | ✅ exists | ⬜ **regression floor** |
| — | all | RESEARCH §5's blast-radius file set (the 6 gated commands' existing tests) stays green throughout | unit | `pytest tests/test_cli_handlers.py tests/test_consistency_check.py tests/test_eprom_operations.py tests/test_serial_comm.py tests/test_validate_oracle.py tests/test_diagnostic_report.py tests/test_matrix_artifact.py tests/test_validate_family_cmd.py -o addopts=""` | ✅ exists | ⬜ **regression floor** |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

There is no Wave 0, matching Phase 134's own precedent: the 4 plans occupy waves 1→4, and every `❌ new`
row above is created by the plan that owns its requirement, in the same wave, paired with its test in
the same commit — no plan depends on test scaffolding from a later wave. `test_click_group_gate_hook.py`
(wave 1) is intentionally independent of `firestarter.cli_handlers` so it needs no fixture from any
later plan.

---

## Non-Vacuity Obligations

A pre-authored gate proves nothing until it is seen to fail. This project has shipped unreachable-green
gates before (v1.23 P129/P130) — treat that as the standing failure mode to guard against. Each must be
**observed RED once**, then restored **byte-identically**:

| # | Planted break | What must go RED |
|---|---------------|-------------------|
| 1 | Plan `136-01`: `dev_tools_enabled_by_env` broadened to `bool(os.environ.get("FIRESTARTER_DEV_TOOLS"))` | the `"0"`/`"false"`/garbage fail-closed test cases |
| 2 | Plan `136-03`: `cls=_DevGroup` removed from `@cli.group(name="dev", cls=_DevGroup)` | the informative-refusal assertion on simulated-stable in `test_dev_group_channel_gating.py` |
| 3 | Plan `136-03`: `_DEV_TOOLS_ENABLED` hardcoded to `True` | the exact-`{read, test}` registry assertion on simulated-stable |
| 4 | Plan `136-03`: `open("/dev/null")` planted inside `channel.is_dev_tools_enabled` | the no-firmware-read source scan, naming the offending callable |

---

## Manual-Only Verifications

None. Every behavior in this phase is automatable — either as an in-process unit assertion, a source
scan, or a subprocess-simulated channel. Unlike Phase 134, there is no hardware-dependent claim and no
Evidence Ceiling row: the channel gate is entirely a CLI/process-boundary fact, provable end to end
without a chip, a board, or a serial connection.

---

## Validation Sign-Off

- [x] Every task has an `<automated>` verify — measured 2026-08-05: 4 plans, 9 tasks total, 9/9 carry an
      `<automated>` command. Zero tasks without one.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — trivially satisfied (zero
      gaps).
- [x] Wave 0 covers all MISSING references — satisfied by the same mechanism 134-VALIDATION.md recorded:
      there is no Wave 0; each `❌ new` file is created by the plan that owns its requirement, in the
      same wave.
- [x] No watch-mode flags — grepped all 4 plans for `--watch` / `ptw` / `pytest-watch` / `--looponfail`:
      zero hits.
- [x] Feedback latency < 15 s (per commit) — per the Test Infrastructure table above.
- [ ] Every non-vacuity obligation above observed RED, then restored byte-identically — execution-time
      obligation; cannot be discharged before the code exists. 4 such proofs planned.
- [ ] mypy headroom recorded at every wave merge (start: measured fresh by plan `136-01`, no inherited
      number) — execution-time obligation, one record per wave merge, plus the `136-CI-PARITY.md`
      Before/After pair.
- [x] `nyquist_compliant: true` set in frontmatter.

**Requirement coverage:** 7/7 (CHAN-01..07). Tick ownership is fully disjoint — CHAN-05 ticked solely by
plan `136-02`; CHAN-01, CHAN-02, CHAN-03, CHAN-04, CHAN-06, CHAN-07 ticked solely by plan `136-03`. No
requirement is claimable by two plans; no plan ticks a requirement it only contributes to (each
"Contributes to but MUST NOT tick" list names the exact plan that closes it).

**Approval:** approved 2026-08-05 by Claude, planning this phase directly (per `136-CONTEXT.md`'s
header: authored inline, not via `/gsd-discuss-phase`, under the operator's standing instruction to run
136 → 136.1 → 137 without stopping). No `gsd-plan-checker` verdict exists yet for this phase at the time
this file is written — this sign-off does not stand in for one; it records what was verified directly
during planning: requirement coverage 7/7 with disjoint tick ownership, every task carrying an
automated verify, the four non-vacuity obligations named up front (not discovered during execution), and
the Click-hook empirical question routed to an explicit Wave-1 measurement task rather than an assumption
baked into a later plan.
