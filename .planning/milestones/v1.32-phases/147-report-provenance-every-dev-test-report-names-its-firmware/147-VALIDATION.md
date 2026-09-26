---
phase: 147
slug: report-provenance-every-dev-test-report-names-its-firmware
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-18
---

# Phase 147 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `147-RESEARCH.md` §"Validation Architecture" — all baselines below are **measured**,
> not estimated.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` 9.1.1 local (pinned `>=8.0`), `syrupy>=5.0` for snapshots |
| **Config file** | `firestarter_app/pyproject.toml` → `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "-ra -q"` |
| **Quick run command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_dev_test_cmd.py tests/test_diagnostic_report.py tests/test_parse_devtest_issue.py tests/test_hardware.py tests/test_provenance.py tests/test_submit.py tests/test_check_devtest_orchestrator.py tests/test_check_diagnostic_report_claims.py -o addopts="" -q` |
| **Full suite command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q` |
| **Estimated runtime** | Quick: ~44 s (measured 239 passed / 43.7 s, 7-file subset). Full: ~229 s (measured **1590 passed, 1 warning / 228.9 s**, 30 snapshots) |

**`addopts` trap (load-bearing).** The project sets `addopts = "-ra -q"`. A second `-q` reaches `-qq`
and **suppresses the `N passed` count line**. Every verification leg that reads a count MUST pass
`-o addopts=""`, as every command in this file does.

**mypy.** `python3 tools/check_mypy_watermark.py` prints a legible summary but **exits 2** in this
devcontainer (ambient numpy). Watermark is **35** (`pyproject.toml:174`). `tools/` is outside mypy's
scope, so new code in `tools/parse_devtest_issue.py` is **not type-checked** — assert on behaviour
there, never on types.

**ruff.** CI scope is exactly `ruff check firestarter/ tests/` and `ruff format --check firestarter/
tests/` (`ci.yml:215,218`). Wider is not CI parity; narrower hides real findings. `tools/` and
`.claude/skills/` are **not** linted by CI.

---

## Sampling Rate

- **After every task commit:** the quick run command above (~44 s) **plus** both gates —
  `python3 tools/check_devtest_orchestrator.py` and `python3 tools/check_diagnostic_report_claims.py`
  (each < 1 s).
- **After every plan wave:** `python3 -m pytest tests/ -o addopts="" -q` (~229 s) plus CI-scoped
  `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/`.
  **Commit before running the suite** — `test_flash_path_record_sync.py` asserts whole-repo
  porcelain and goes RED on any mid-change diff.
- **Phase gate:** `bash tools/ci_parity.sh` (4 legs). **Leg 4 exits 2 in this devcontainer by
  documented design** — the hardened gate refusing to report a count for a truncated run, not a
  defect. Record it as expected; do **not** add `|| true`.
- **Before `/gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 44 s (quick run).

---

## Per-Task Verification Map

Task IDs are assigned by the planner; this map binds each **requirement oracle** to its level and
command so the planner can attach them. `File Exists` is measured against the repo today.

| Requirement | Behavior (observable oracle) | Test Type | Automated Command | File Exists | Status |
|---|---|---|---|---|---|
| PROV-01 | `read_programmer_identity()` returns harvested `comm.firmware_identity` verbatim off a **single** `find_and_connect` | unit (hardware) | `pytest tests/test_hardware.py -o addopts="" -q -k programmer_identity` | ❌ W0 (**W-1**) | ⬜ pending |
| PROV-01 | Identity reaches `to_dict()["auto_capture"]["fw_board_identity"]` in the **saved JSON** and the **rendered output** | handler | `pytest tests/test_dev_test_cmd.py -o addopts="" -q -k fw_board_identity` | ⚠️ extend — mirror `test_hw_revision_auto_captured_end_to_end` (`:730-743`) | ⬜ pending |
| PROV-02 | Exactly **one** `find_and_connect` and **one** `disconnect()` per call; no `EpromOperator` attribute written | unit (hardware) | W-1 command, asserting `call_count == 1` + `disconnect.assert_called_once()` | ❌ W0 (**W-1**) | ⬜ pending |
| PROV-02 | SAFE-02/SAFE-03 AST gate green, still names all three targets in its PASS line | gate | `python3 tools/check_devtest_orchestrator.py` → EXIT 0, output names `chip_test.py`, `cli_handlers.py`, `submit.py` | ✅ measured PASS | ⬜ pending |
| PROV-02 | No new `dev_test` helper slipped past the allow-list | gate (test) | `pytest tests/test_check_devtest_orchestrator.py -o addopts="" -q` | ✅ exists — must stay green **without** editing its expected set | ⬜ pending |
| PROV-03 | **D-08 differing-pair:** `"3.0.0b11:leonardo"` and `"3.0.0b19:leonardo"` land as two **different** JSON values | handler | `pytest tests/test_dev_test_cmd.py -o addopts="" -q -k suffix` | ❌ W0 | ⬜ pending |
| PROV-03 | `comm.firmware_identity` never truncated — the `[\d.x]+` match is a separate local (non-regression on the ring fence) | unit (transport, read-only) | `pytest tests/test_fwguard.py tests/test_fw_version_guard.py -o addopts="" -q` | ✅ exists — **do not add to these and do not edit the fenced path** (D-05) | ⬜ pending |
| PROV-04 | `SCHEMA_VERSION == "1.4"` and the fenced block carries it | unit | `pytest tests/test_diagnostic_report.py -o addopts="" -q -k schema` | ✅ exists (`:516`) — imports the constant, auto-follows the bump | ⬜ pending |
| PROV-04 | A frozen body carrying `fw_board_identity: null` **still parses** on **both** parsers | parser | `pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k legacy` | ❌ W0 (**W-3**) — existing `_B11_BODY` carries a *populated* value | ⬜ pending |
| PROV-04 | Presence-only `schema_version` acceptance survives the bump | parser | `pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k presence` | ✅ exists (`"9.9-future"` at `:138`); a `"1.4"` body pre-verified accepted by both parsers | ⬜ pending |
| PROV-04 | Blast radius: `dedup_fingerprint` + `is_submittable` unchanged | unit | `pytest tests/test_provenance.py -o addopts="" -q` | ✅ exists | ⬜ pending |
| PROV-05 | **D-13(a)** render-level: `AutoCapture(fw_board_identity=None, hw_revision=None)` → marker in **both** rich-table rows, no bare `"None"`, JSON still `null` | unit (render) | `pytest tests/test_diagnostic_report.py -o addopts="" -q -k marker` | ❌ W0 — use existing `_rendered_text(table)` (`:965`) + `_minimal_report()` | ⬜ pending |
| PROV-05 | **D-13(b)** handler-level: mock returns `ProgrammerIdentity(None, None)` → marker in rendered report **and** `null` in saved JSON | handler | `pytest tests/test_dev_test_cmd.py -o addopts="" -q -k unknown` | ❌ W0 — drive via `make_hardware_manager(...)` | ⬜ pending |
| PROV-05 | **D-04 leg 1:** revision ack fails, identity survives → `ProgrammerIdentity(None, "<identity>")` | unit (hardware) | W-1 command, `-k revision_fails` | ❌ W0 (**W-1**) | ⬜ pending |
| PROV-05 | **D-04 leg 2:** transport raises → `ProgrammerIdentity(None, None)`, never a bare `None` return | unit (hardware) | W-1 command, `-k transport_error` | ❌ W0 (**W-1**) — `FirmwareOutdatedError` is a `SerialError`, lands in the existing clause | ⬜ pending |
| PROV-05 | **D-07:** a U+FFFD-bearing identity is scrubbed but stays **visibly faulty** — never converted to the unknown marker | unit (hardware) | W-1 command, `-k scrub` | ❌ W0 (**W-1**) | ⬜ pending |
| PROV-05 | The marker string trips none of the 14 forbidden claim patterns | gate | `python3 tools/check_diagnostic_report_claims.py` → EXIT 0 | ✅ measured PASS; six candidate wordings pre-checked clean | ⬜ pending |
| PROV-06 | `render_diff` emits a **labelled** identity line when populated; marker + not-attributable clause when `null`; `hw_revision` **absent** (D-15) | parser | `pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k render_diff` | ❌ W0 (**W-2**) — `render_diff` has **ZERO** tests today | ⬜ pending |
| PROV-06 | The three marker literals are equal | parity | `pytest tests/test_parse_devtest_issue.py -o addopts="" -q -k marker_string` | ❌ W0 — one assert; the file already imports both worlds | ⬜ pending |
| PROV-06 | Skill `show` render carries the identity, fixes `hw None`, matches `SKILL.md`'s documented example | **manual** (checkpoint) | two offline `show --body-file` runs + diff of `SKILL.md:61-67` against new output | ❌ W0 (**W-4**) — no harness exists; an app-repo test reaching into `/workspaces/.claude/` fails OPEN | ⬜ pending |
| PROV-06 | Criterion #5 — a triager can attribute without asking the reporter | **manual** (checkpoint) | operator reads both renders; attribution answerable for the populated case, explicitly refused for the null case | ❌ judgement criterion — pair with W-4, never claim as automated | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **W-5** `tests/test_dev_test_cmd.py::make_hardware_manager` — must return a real
      `ProgrammerIdentity` and gain a second parameter so D-08 and D-13(b) can vary one field.
      **41 `dev test` invocations depend on this fixture — land it before the render/oracle tasks.**
- [ ] **W-1** `tests/test_hardware.py` — no coverage exists for the value-returning revision read at
      all (the 13 existing tests cover only `get_hardware_revision`). Add: one-connection /
      one-disconnect (PROV-02), happy path (PROV-01), **D-04 leg 1** (revision ack fails, identity
      survives), **D-04 leg 2** (transport raises → `(None, None)`), **D-07** scrub.
      Use existing `hw_config` / `make_comm` / `fake_serial` fixtures and
      `patch("firestarter.serial_comm.SerialCommunicator.find_and_connect")`.
      **`make_comm()` sets `firmware_identity = None` by default** (`conftest.py:225`) — a test
      wanting a populated identity must set it explicitly; the default gives the absent case free.
- [ ] **W-2** `tests/test_parse_devtest_issue.py` — create the **first-ever** tests for `render_diff`
      (PROV-06). Import it alongside the four names already imported at `:50`.
- [ ] **W-3** `tests/test_parse_devtest_issue.py` — a **new** frozen fixture carrying
      `fw_board_identity: null`, asserted to parse and group unchanged. PROV-04's real-world
      population is null-bearing reports; the existing `_B11_BODY` (`:361-374`) is populated.
- [ ] **W-4** Skill-render verification — **no harness exists**. Commit two fixture bodies (one
      populated, one null) and a `checkpoint:human-verify` running the two offline
      `show --body-file` commands. Do **not** add an app-repo test that reaches into
      `/workspaces/.claude/` (fails OPEN in standalone CI).
- [x] Framework install: **none needed** — `pytest`, `syrupy`, `ruff`, `mypy` all present.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Skill `show` render carries the identity and no longer prints `hw None` | PROV-06 | `.claude/skills/devtest-triage/scripts/devtest_issues.py` has **no test harness**, and building one inside the app repo would reach outside it and fail OPEN in standalone CI | Run the two offline `show --body-file` commands (populated + null fixture bodies) and read both renders; diff `SKILL.md:61-67`'s reproduced example against the new output |
| A triager can attribute a parsed report to a firmware version without asking the reporter | PROV-06 / criterion #5 | Judgement criterion — no assertion expresses "a human can answer this" | Same two fixtures: confirm attribution is answerable for the populated case and **explicitly refused** (not silently blank) for the null case |

Everything else in the map above has automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (W-1…W-5)
- [ ] No watch-mode flags
- [ ] Every `pytest` leg passes `-o addopts=""` where it reads a count
- [ ] `ci_parity.sh` leg 4 documented as expected-exit-2, **not** suppressed with `|| true`
- [ ] Feedback latency < 45 s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
