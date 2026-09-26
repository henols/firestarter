---
phase: 121
slug: dev-test-fix-gates-docs-redesign
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-29
---

# Phase 121 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `121-RESEARCH.md` § Validation Architecture (all commands executed live on the milestone branch).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | host: `pytest` ≥8.0 + `syrupy` ≥5.0 (29 snapshots) + `pytest-cov` ≥7.1.0 · firmware: PlatformIO/Unity (`native`, `native_nodevtools`) |
| **Config file** | `/workspaces/firestarter_app/pyproject.toml` (`[tool.ruff]`, `[tool.mypy]`) · `/workspaces/firestarter/platformio.ini` |
| **Quick run command** | `python3 -m pytest tests/test_chip_test.py tests/test_dev_test_cmd.py tests/test_diagnostic_report.py tests/test_submit.py -q` |
| **Full suite command** | `python3 -m pytest tests/ --cov=firestarter --cov-fail-under=70 -q` + `cd /workspaces/firestarter && pio test -e native` |
| **Estimated runtime** | ~5 s quick · ~50 s host full · ~23 s firmware native |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/test_chip_test.py tests/test_dev_test_cmd.py -q` (~5 s)
- **After every plan wave:** Run `python3 -m pytest tests/ -q` + `cd /workspaces/firestarter && pio test -e native`
- **Before `/gsd-verify-work`:** The full GATE-03 nine-row sweep (RESEARCH §F-8 rows 1–18), run under a `uv`-provisioned Python 3.11 venv with the **CI-resolved** ruff version — not the devcontainer's pinned one
- **Max feedback latency:** 5 seconds (quick) / 75 seconds (wave)

---

## Per-Task Verification Map

Task IDs are assigned by the planner; rows below are the requirement-level contract every task must roll up to. `File exists?` reflects the tree state measured during research.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | DEVTEST-04 | Pitfall 1a — silent destructive misdispatch | An unhandled op string never reaches `erase_eprom()` and never reports `OK` | unit | `pytest tests/test_chip_test.py -k unhandled_op_fails_closed -x` (`erase_eprom.assert_not_called()`) | ❌ W0 — **highest priority** | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-04 | Pitfall 1b — ungated partial write | Partial write stays inside the chip-ID destructive gate (`_DESTRUCTIVE_OPS`) | unit | `pytest tests/test_chip_test.py -k partial_write_gated_on_id_mismatch -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-01 | — | `OP_ERASE` is `NA` on `0x0D` with a family-fact reason | unit | `pytest tests/test_chip_test.py -k "erase and 0x0d or na_erase" -x` | ❌ new legs, existing file | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-01 | — | `convert_to_programmer` clears `FLAG_CAN_ERASE` on `0x0D` | unit | `pytest tests/test_database_conversion.py -k flag_can_erase -x` | ✅ (2 legs **invert**) | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-01 | — | Wire `flags` for `at28c256` is 0, not 2 | integration | `pytest tests/test_eprom_operations.py -k can_erase_bit -x` | ✅ (**inverts**) | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-02 | — | `dev test <chip>` accepts no options; each removed flag errors | unit | `pytest tests/test_dev_test_cmd.py -k "no_options or rejects_flag" -x` | ❌ new; 20/23 methods rework | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-02 | — | The 4 other `dev` sub-commands keep their `--output-dir` / `-y` | regression | `pytest tests/test_matrix_artifact.py tests/test_validate_family_cmd.py tests/test_validate_oracle.py tests/test_dev_sdp_cmd.py -q` | ✅ must stay green untouched | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-03 | — | UV-ness decided once in `derive_plan`; 301/301 exact | unit | `pytest tests/test_chip_test.py -k is_uv -x` | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-03 | Pitfall 4 — wrong dict shape | Production path (programmer dict) gets the right region | integration | `pytest tests/test_chip_test.py -k write_region_via_run_plan -x` (must NOT test `_write_region_for(full)`) | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-04 | Unconsented write (D-03, owned) | yes → full device; no → 256 B top-anchored | unit | `pytest tests/test_dev_test_cmd.py -k uv_ask -x` | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-04 | Unconsented write (D-03, owned) | Off-TTY → partial, and it really writes | unit | `pytest tests/test_dev_test_cmd.py -k off_tty_partial -x` — assert `write_eprom` **called** with the 256 B region | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-04 | — | `dedup_fingerprint` differs partial vs full | unit | `pytest tests/test_diagnostic_report.py -k fingerprint_partial -x` | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-04 | — | b11 six-string issue bodies still parse | unit | `pytest tests/test_parse_devtest_issue.py -k legacy_vocabulary -x` | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-05 | — | Every run asks; dedup runs first | unit | `pytest tests/test_submit.py -k "always_asks or dedup_first" -x` | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-05 | — | `gh` failure → ask anyway + explicit line | unit | `pytest tests/test_submit.py -k dedup_check_unavailable -x` | ❌ new | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-06 | Command injection via `gh` shell-out | `create` argv carries no write-gated flag, **including short forms** | unit | `pytest tests/test_submit.py -k permission_gated -x` | ✅ **extend** `:301-320` | ⬜ pending |
| TBD | TBD | TBD | DEVTEST-06 | PII leak into a public issue | `comment` argv carries no mutating flag; targets `SUBMIT_REPO` | unit | `pytest tests/test_submit.py -k comment_argv -x` | ❌ new | ⬜ pending |
| TBD | TBD | TBD | GATE-01 | Widened SDP allow-set | Checker fails on each planted violation class (permit-by-default, widenable allow-set) | unit | `pytest tests/test_check_sdp_capability.py -q` | ❌ W0 — new file + 2 fixtures | ⬜ pending |
| TBD | TBD | TBD | GATE-01 | Hollow gate | Checker is non-vacuous by path | unit | `pytest tests/test_check_sdp_capability.py -k test_gate_is_not_vacuous_by_path` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | GATE-01 | Gate under-coverage (RESEARCH C-4) | Every new `dev test` helper name is in `_HANDLER_FUNCTION_NAMES` | unit | `pytest tests/test_check_devtest_orchestrator.py -q` + a new allow-list-completeness leg | ✅ extend (14 tests) | ⬜ pending |
| TBD | TBD | TBD | GATE-03 | — | Full nine-row non-regression sweep | integration | RESEARCH §F-8 rows 1–18 under `/tmp/venv311` with CI-resolved ruff | ✅ all exist | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `[tool.ruff] extend-exclude = ["tests/golden"]` in `firestarter_app/pyproject.toml` — **must land before any `ruff format` run** (Pitfall 2: ruff 0.16.0 reformats `tests/golden/v1.3-COVERAGE-MATRIX.md`, corrupting D-18's byte-identity golden)
- [ ] The fail-closed `_dispatch_multi_run` / `_dispatch_step` arm + its RED-then-GREEN test — **before** `OP_WRITE_PARTIAL` exists (Pitfall 1a)
- [ ] `tools/check_sdp_capability_invariants.py` — GATE-01's AST checker (new)
- [ ] `tests/test_check_sdp_capability.py` — GATE-01's companion pytest (new file)
- [ ] `tests/fixtures/planted_permit_by_default.py` — D-14 Class 1 fixture
- [ ] `tests/fixtures/planted_widenable_allowset.py` — D-14 Class 2 fixture
- [ ] Framework install: **none needed** — `pip install -e '.[test]'` already satisfied in this devcontainer

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The 8 doc targets no longer describe pre-fix SDP/erase behavior and explicitly state `0x0D` has no erase | GATE-02 | Prose accuracy has no automatable oracle; a grep for absence proves nothing about whether the *replacement* text is correct | Read each of `doc/PROTOCOLS.md` §1.6, `doc/lockable-proms.md`, `doc/protocol-id.md`, `doc/community-validation.md`, `doc/beta-testing-install.md`, `firestarter/CLAUDE.md`, and both READMEs against RESEARCH §F-7's located stale lines; confirm the `-b`-is-required-on-a-non-blank-AT28C statement is present (D-13 / C-8: this is a **docs** statement, not a runtime warning) |
| `dev test` prints the always-writes notice unconditionally as the **first** line of output | DEVTEST-04 (D-04) | Ordering-of-first-line is asserted in unit tests, but the wording's adequacy as a safety notice is a human judgement | Run `dev test <chip>` with no board attached and read line 1 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 75s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
