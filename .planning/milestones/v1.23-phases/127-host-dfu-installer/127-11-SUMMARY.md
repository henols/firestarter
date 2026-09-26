---
phase: 127-host-dfu-installer
plan: 11
subsystem: ci-evidence
tags: [ci, github-actions, workflow-dispatch, pyusb, operator-gate, checkpoint, mypy, watermark-gate]

# Dependency graph
requires:
  - phase: 127-06
    provides: "ci.yml's workflow_dispatch: trigger + isolated ci-py32 job (.[test,py32] install, real-pyusb API surface tests)"
  - phase: 127-02
    provides: "the [py32] extra's pyusb>=1.3.1,<2 floor in pyproject.toml"
  - phase: 127-04
    provides: "_reject_py32_only_option() and tests/test_py32_channel_gating.py, the source of the 3 mypy errors this plan's added scope fixes"
provides:
  - "Pre-push state recorded: branch/HEAD, porcelain, all 24 phase commits with changed paths, all eight primary-leg gate exit codes, ci-py32 job steps + all four workflows' on: blocks quoted verbatim, throwaway-venv rehearsal results (pyusb resolved to 1.3.1), and the four anticipated failure modes with recoveries"
  - "The two outward-facing commands (git push -u, gh workflow run) printed fully expanded, neither executed by any task"
  - "HOST-04's CI evidence: run 30707902225, independently re-derived read-only — ci-py32 green (6/6 pytest, pyusb 1.3.1 resolved), primary ci RED at the mypy watermark gate (72 > 35), headSha string-equal to the pushed ref"
  - "3 func-returns-value mypy errors (introduced by 127-04) fixed without weakening the assertions; measured mypy count returns to the pre-127 baseline of 69, proving Phase 127 adds zero mypy debt"
  - "Two stacked fail-open defects in tools/check_mypy_watermark.py documented with reproduction commands, for Plan 127-12 to lift into 127-NONREGRESSION.md"
affects: [127-12]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "mypy's func-returns-value fires on ANY use of a None-annotated function's return value in an expression -- including `assert f() is None` and `x = f()` -- not just on unused-result. The mypy-clean idiom for asserting 'does not raise' against a None-returning function is a bare statement call, not an assertion on its return."

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_py32_channel_gating.py

key-decisions:
  - "Task 1 was executed by a prior session and stopped at Task 2's operator gate. This continuation session did NOT re-execute Task 1 -- it verified the prior session's commits/branch/HEAD exist and proceeded from Task 3."
  - "ATTRIBUTION: the operator explicitly authorised removing the structural push/dispatch gate and directed the ORCHESTRATOR (not this executor, not the operator personally) to run `git push -u origin v1.23-py32f071-integration` and `gh workflow run ci.yml --ref v1.23-py32f071-integration`. This differs from Plans 124-11/125-05/126-11, where the operator ran the commands personally -- recorded accurately here rather than inherited as 'the operator pushed'. The structural gate still held from this plan's own task perspective: no task in 127-11 executed either command."
  - "No task in this session ran git push, gh workflow run, gh release, gh pr, git tag, or any destructive git command. Read-only commands executed in Task 3: gh run view (JSON + --log), gh api .../logs, git fetch origin, git show origin/<branch>:.github/workflows/ci.yml, git rev-parse, git merge-base --is-ancestor, git status --porcelain."
  - "The run's usb.core.find branch (enumerated vs NoBackendError) is recorded as UNRESOLVED from this run's log. tests/test_pyusb_api_surface.py::test_usb_core_find_for_real stores the outcome in a local variable and asserts on it in-process, but never prints it; pytest -q suppresses captured stdout on a passing test, and the raw job log (fetched via gh api .../logs, not just gh run view --log) contains no NoBackendError/enumerated token anywhere in the ci-py32 job. Research assumption A4 (either branch is acceptable) is satisfied by the test passing, but WHICH branch fired on this specific runner is not observable post hoc without re-running with `-s` or a print. This is recorded honestly rather than guessed from the local devcontainer's own enumeration (which is irrelevant -- a different machine)."
  - "The pytest step's collected/passed count (6) is derived by counting the dots in the raw log (`......  [100%]`), not from a printed 'N passed' summary line -- the raw log capture (via `gh api .../logs`, cross-checked against `gh run view --log`) does not contain a final pytest summary line for this step, only the progress dots followed immediately by the next step's setup-python cleanup output. 6 matches the count independently rehearsed locally in Task 1's throwaway venv (`6 passed`), and is non-zero, satisfying the acceptance criterion, but the exact mechanism (why the summary line is absent from the captured log) is noted as an open, non-blocking oddity of this GitHub Actions log capture, not investigated further."
  - "ADDED SCOPE (operator-approved, both halves executed): (1) fixed the 3 `func-returns-value` mypy errors 127-04 introduced in tests/test_py32_channel_gating.py by converting `assert cli_handlers._reject_py32_only_option(...) is None` to a bare call -- the behaviour under test ('does not raise') is asserted identically by a bare statement, with no weakening, no skip, no `# type: ignore`. Committed `a62ca76`. (2) Recorded, but explicitly did NOT fix, the two stacked fail-open layers in tools/check_mypy_watermark.py and the 69 inherited mypy errors -- both are out of this plan's and this phase's scope (Phase 123's gate-hardening charter), per the operator's 'fix my 3, record the rest' instruction."
  - "Mypy counts were measured with a throwaway venv on /home/vscode/.local/bin/python3.11 (`.[test]` installed, then deleted), running `<venv>/bin/python -m mypy firestarter/ tests/` directly -- NOT the repo's own check_mypy_watermark.py gate, which is itself one of the two fail-open defects being documented and cannot be trusted to measure its own bug."
  - "No requirement checkbox in .planning/REQUIREMENTS.md was ticked. HOST-01..HOST-08 confirmed still `[ ]` Pending both before and after this session. Only Plan 127-12 may tick them."

requirements-completed: []  # HOST-04 intentionally left unticked -- only Plan 127-12 may tick HOST-01..HOST-08. This plan's Task 3 records the CI evidence 127-12 needs to cite when it ticks HOST-04.

coverage:
  - id: D1
    description: "HOST-04's CI-only evidence obtained and independently re-derived read-only: ci-py32 job green (checkout, setup-python, .[test,py32] install, pyusb-import-and-version step, pytest step all independently `success`), pyusb resolved to 1.3.1, 6/6 pytest passed, headSha string-equal to the pushed ref, workflow_dispatch + ci-py32 confirmed present on the fetched origin ref"
    requirement: "HOST-04"
    verification:
      - kind: other
        ref: "gh run view 30707902225 --repo henols/firestarter_app --json ... (re-queried live, not accepted on report)"
        status: pass
      - kind: other
        ref: "gh api repos/henols/firestarter_app/actions/jobs/91390092810/logs (raw ci-py32 job log, pyusb 1.3.1 + 6 dots confirmed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The primary ci job's own conclusion recorded as RED at the mypy watermark gate (72 > 35), proving the phase's changes did not silently pass a broken gate -- the gate itself was already broken (fail-open) and this run is the first time anything forced it to actually run mypy for real"
    verification:
      - kind: other
        ref: "gh run view 30707902225 job 91390092867 (ci) -- step 'mypy type check (watermark gate)' conclusion=failure, log line 'mypy errors: 72 (watermark: 35)'"
        status: pass
    human_judgment: false
  - id: D3
    description: "3 func-returns-value mypy errors (127-04's addition) fixed without weakening assertions; re-measured mypy count returns to exactly 69, the pre-127 baseline -- Phase 127 adds zero net mypy debt"
    requirement: null
    verification:
      - kind: unit
        ref: "tests/test_py32_channel_gating.py -q (14 passed, throwaway-venv mypy: 69 errors, matches ccbc401 baseline exactly)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Two stacked fail-open defects in tools/check_mypy_watermark.py documented (bare `mypy` from PATH instead of `sys.executable -m mypy`; a numpy-stub abort under py3.12+python_version=3.9 collapses to '1 error' and passes the gate vacuously) -- NOT fixed, per operator instruction, and carried to Plan 127-12 as an open finding"
    verification: []
    human_judgment: true
    rationale: "This is a documentation/handoff deliverable (a finding for 127-12 to lift into 127-NONREGRESSION.md), not a code change with a pass/fail test. Its completeness is a judgment call for the closing plan/verifier to confirm."

# Metrics
duration: ~1h10m (Task 1 by prior session ~35min + this continuation session ~35min)
completed: 2026-08-01
status: complete
---

# Phase 127 Plan 11: HOST-04 CI Evidence + Zero-Net-Mypy-Debt Fix Summary

**HOST-04's CI evidence obtained via an orchestrator-run (operator-authorised) push + dispatch and independently re-derived read-only: `ci-py32` green (6/6 pytest, pyusb 1.3.1), primary `ci` RED at the mypy watermark gate (72 > 35) -- the first real type-check this branch has ever gotten, because `tools/check_mypy_watermark.py` has been silently fail-open in this devcontainer since roughly Phase 113. Fixed the 3 mypy errors Phase 127 actually added (measured mypy count: 69 -> 72 -> 69, proving zero net debt); recorded, but explicitly did not fix, the fail-open gate and the 69 inherited errors, per the operator's "fix my 3, record the rest."**

## Performance

- **Started:** 2026-08-01 (Task 1, prior session)
- **Task 1:** complete (prior session)
- **Task 2 (operator gate):** RESOLVED -- see Attribution below
- **Task 3:** complete (this session)
- **Added scope (fix the 3 func-returns-value errors):** complete (this session)
- **Files modified:** 1 (`tests/test_py32_channel_gating.py`)
- **Commits this session:** 1 (`a62ca76`, fix)

## Task 1 Accomplishments — Recorded Pre-Push State (prior session, unchanged from original SUMMARY)

### Branch / HEAD / porcelain (`/workspaces/firestarter_app`)

```
branch: v1.23-py32f071-integration
HEAD:   84cdd86e1f21f88d59129c849ca2ab0f8c8e1901
```

`git status --porcelain` — 5 lines, all **pre-existing** (named, not cleaned):
```
 M .gitignore
?? .coverage
?? .planning/config.json
?? SECURITY.md
?? write_test_port.sh
```

### This phase's commits, in order, with changed paths (63ce44e..84cdd86, 24 commits)

| # | Commit | Subject | Changed paths |
|---|--------|---------|----------------|
| 1 | `63ce44e` | merge(127-01): land feature/py32f071-fw-install @ 4ee64a1 (HOST-01, D-16) | merge commit; 2nd parent = `4ee64a14a8933b60896c8b168bb1c7e34d788fa4` |
| 2 | `6c621b4` | docs(127-01): record D-17 accepted-deviation comment at flash_method() | `firestarter/firmware.py` |
| 3 | `4b1165d` | feat(127-04): close --usb-id-accepted-on-stable gap | `firestarter/cli_handlers.py` |
| 4 | `19b41ca` | test(127-04): prove channel gating both ways | `tests/test_py32_channel_gating.py` |
| 5 | `86cbfce` | test(127-04): import-time proof + truth table + one-code-path guard | `tests/test_py32_channel_gating.py` |
| 6 | `7e2459a` | fix(127-04): make test_help_fw correct on both release channels (added scope) | `tests/__snapshots__/test_characterization.ambr`, `tests/test_characterization.py` |
| 7 | `e08a01d` | feat(127-02): raise [py32] extra's pyusb floor to >=1.3.1,<2 | `pyproject.toml` |
| 8 | `d36b53f` | test(127-02): non-vacuous pyusb-floor gate + D-17 record gate | `tests/test_py32_packaging.py` |
| 9 | `5593642` | test(127-03): add independent DFU/DfuSe opcode anchors | `tests/test_dfu_opcode_anchors.py` |
| 10 | `921f9eb` | fix(py32): tighten flash envelope to application region | `firestarter/py32_dfu.py` |
| 11 | `1843962` | test(py32): pin the tightened envelope at both boundaries | `tests/test_py32_flash_map_host.py` |
| 12 | `ee6c5af` | test(py32): fail-closed cross-repo linker-script parity gate | `tests/test_py32_flash_map_host.py` |
| 13 | `e20e9e5` | test(127-06): conditional collect_ignore gate + real-pyusb API surface | `tests/conftest.py`, `tests/test_pyusb_api_surface.py`, `tests/test_pyusb_gating.py` |
| 14 | `5052568` | ci(127-06): workflow_dispatch + isolated ci-py32 job | `.github/workflows/ci.yml`, `tests/test_pyusb_gating.py` |
| 15 | `dde0e32` | test(127-07): remove _require_usb() pragma, cover in-process | `firestarter/py32_dfu.py`, `tests/test_py32_pyusb_absent.py` |
| 16 | `8bdc253` | test(127-07): subprocess sys.meta_path blocker proves CLI survives real pyusb absence | `tests/test_py32_pyusb_absent.py` |
| 17 | `6bad9d9` | refactor(127-08): hoist _finish() into flash() as the sole call site | `firestarter/py32_dfu.py` |
| 18 | `18c95fa` | test(127-08): extend _FakeUsbDevice with an UPLOAD arm | `tests/test_py32_dfu.py` |
| 19 | `71c86d7` | test(127-08): pin _FakeUsbDevice's ctrl_transfer against real pyusb | `tests/test_pyusb_api_surface.py` |
| 20 | `690ffcf` | feat(127-09): DFU_UPLOAD readback, VerifyResult enum, download->readback->_finish | `firestarter/py32_dfu.py`, `tests/test_dfu_opcode_anchors.py` |
| 21 | `dd9f5af` | test(127-09): pin the four VerifyResult outcomes against the mock | `tests/test_py32_dfu.py` |
| 22 | `8a265ef` | feat(127-09): "written but NOT verified" -- verify-aware logging in _install_with_dfu | `firestarter/firmware.py`, `tests/test_py32_dfu.py` |
| 23 | `a195065` | docs(127-10): correct the flash-map figure, document readback verification, record the pyusb floor | `doc/PY32F071-FIRMWARE-INSTALL.md` |
| 24 | `84cdd86` | test(127-10): parity gate holding the install doc against APP_REGION_END/FLASH_BASE | `tests/test_py32_packaging.py` |

This is the complete list of what CI run 30707902225 built.

### Full suite result, collected count, coverage (sibling layout, `firestarter` present, pyusb absent, measured pre-fix)

```
pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
TOTAL: 4767 stmts, 864 miss, 82%
Required test coverage of 70% reached. Total coverage: 81.88%
30 snapshots passed.
1293 passed in 176.97s (0:02:56)
```

**1293 collected / 1293 passed / 0 failed / 0 skipped**, coverage **81.88%** against the 70% floor.

### All eight primary-leg (`ci.yml` `ci` job) gate commands, re-run locally pre-fix — all exit 0

| # | Command | Result |
|---|---------|--------|
| 1 | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (73 messages, version 1).` exit 0 |
| 2 | codegen `messages.py` + `git diff --exit-code firestarter/messages.py` | `OK: wrote firestarter/messages.py (python, 73 messages).` exit 0, no diff |
| 3 | `python3 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check` | `OK: catalog valid (12 vectors, version 1).` exit 0 |
| 4 | codegen `frame_vectors.py` + `git diff --exit-code firestarter/frame_vectors.py` | `OK: wrote firestarter/frame_vectors.py (python-vectors, 12 vectors).` exit 0, no diff |
| 5 | `ruff check firestarter/ tests/` | `All checks passed!` exit 0 |
| 6 | `ruff format --check firestarter/ tests/` | `114 files already formatted` exit 0 |
| 7 | `python tools/check_mypy_watermark.py` | `mypy errors: 1 (watermark: 35)` exit 0 -- **this is the fail-open reading, see below** |
| 8 | `pip install -e . && firestarter --help` | Click help renders, all subcommands listed | exit 0 |

**Note (this session's correction):** gate #7's "1 error" reading is the fail-open bug documented below, not a genuine clean mypy run. See "Fail-Open Gate Findings" for the corrected figures (69/72/69) measured with a real, working mypy invocation.

### `ci.yml`'s `on:` block and the `ci-py32` job, quoted verbatim — unchanged from Task 1's record

See prior record (all four workflows' `on:` blocks re-derived first-hand; pushing `v1.23-py32f071-integration` fires none of them). Re-confirmed this session via the fetched `origin/v1.23-py32f071-integration` ref (see Task 3 below) — `workflow_dispatch:` and the `ci-py32` job are both present on the ref that was actually built.

### Throwaway `.[test,py32]` venv rehearsal (Task 1, created and deleted that session)

- `pip install -e '.[test,py32]'` → resolved **`pyusb==1.3.1`**.
- `pytest tests/test_pyusb_api_surface.py --no-cov` → **6 passed**.
- `pytest tests/ --no-cov` (full suite, pyusb genuinely present) → **1299 passed in 166.57s**.
- Venv deleted afterward. Devcontainer re-confirmed pyusb-absent.

### The two outward-facing commands — printed by Task 1

```bash
cd /workspaces/firestarter_app && git push -u origin v1.23-py32f071-integration
cd /workspaces/firestarter_app && gh workflow run ci.yml --repo henols/firestarter_app --ref v1.23-py32f071-integration
```

## Task 2 — Operator Gate Resolution (ATTRIBUTION)

**The operator explicitly authorised removing the structural gate and directed the ORCHESTRATOR to perform both outward-facing actions.** This is recorded precisely because it differs from the pattern in Plans 124-11/125-05/126-11 (where the operator ran the commands personally):

1. The orchestrator ran `git push -u origin v1.23-py32f071-integration` from `/workspaces/firestarter_app`. This created the remote branch (`git ls-remote` had shown it absent in Task 1). Verified afterward via `gh run list` that the push itself triggered **no** workflow.
2. The orchestrator ran `gh workflow run ci.yml --repo henols/firestarter_app --ref v1.23-py32f071-integration`.

**No task inside this plan (127-11) executed either command** — the structural gate that this plan's own tasks are bound by held throughout. The relaxation was an explicit, out-of-band operator decision executed by the orchestrator, not a task in this plan's `<tasks>` list.

## Task 3 — Every Claimed Fact About the Run, Re-Derived Read-Only (this session)

**Standing policy honored: nothing relayed was accepted. Every field below was independently queried this session.**

### Run identity (re-derived via `gh run view 30707902225 --repo henols/firestarter_app --json ...`)

| Field | Re-derived value |
|---|---|
| Run id | `30707902225` |
| Run URL | `https://github.com/henols/firestarter_app/actions/runs/30707902225` |
| Workflow name | `Host CI` |
| Event | `workflow_dispatch` |
| Head branch | `v1.23-py32f071-integration` |
| Head SHA | `84cdd86e1f21f88d59129c849ca2ab0f8c8e1901` |
| Status | `completed` |
| Conclusion | `failure` |

### Per-job conclusions

| Job | Conclusion |
|---|---|
| `ci-py32` | **success** |
| `ci` (primary) | **failure** |

### `ci-py32` per-step conclusions, in order (all `success` — 9 steps, no skips)

1. Set up job — success
2. Run `actions/checkout@v4` — success
3. Set up Python 3.11 — success
4. **Install package + test + py32 deps** — success (resolved `pyusb 1.3.1`, log: `Collecting pyusb<2,>=1.3.1 (from firestarter==3.0.0b14)` → `Downloading pyusb-1.3.1-py3-none-any.whl`)
5. **Prove pyusb genuinely imports, and record its resolved version** — success, log line: `pyusb 1.3.1`
6. **Run the real-pyusb API surface tests** — success, log: `......  [100%]` (6 dots)
7. Post Set up Python 3.11 — success
8. Post Run `actions/checkout@v4` — success
9. Complete job — success

**Resolved pyusb version, lifted from the log: `1.3.1`.**

**Pytest collected/passed count:** **6**, derived by counting the dots in the raw job log (`gh api repos/henols/firestarter_app/actions/jobs/91390092810/logs`), since the raw log capture does not contain a printed "N passed" summary line for this step (see key-decisions for why this is recorded as an open, non-blocking log-capture oddity rather than investigated further). 6 is non-zero (pytest exits 5 on nothing collected, so a green step could not have collected zero regardless), and matches Task 1's independently-rehearsed local count of 6 passed in the throwaway venv.

**Which branch did `usb.core.find` take on the runner (research assumption A4)?** **UNRESOLVED from this run's log.** `tests/test_pyusb_api_surface.py::test_usb_core_find_for_real` stores the outcome (`"enumerated"` or `"no_backend"`) in a local variable and asserts on it in-process, but never prints it to stdout; `pytest -q` suppresses captured output for a passing test, and a full-text search of the raw log (`gh api .../logs`, not just `gh run view --log`) for `NoBackendError`/`enumerated`/`usb.core.find` returns zero matches inside the `ci-py32` job. The test's own internal either/or assertion did fire correctly (the step is `success`, and the test would fail loudly if `outcome` were never set), so A4's *acceptability* claim is satisfied, but *which* branch fired on this specific GitHub-hosted runner cannot be recovered post hoc from this log. Recorded honestly as unresolved rather than inferred from the local devcontainer's own enumeration (a different, irrelevant machine).

### `ci` (primary) per-step conclusions, in order

| # | Step | Conclusion |
|---|------|------------|
| 1 | Set up job | success |
| 2 | Run `actions/checkout@v4` | success |
| 3 | Set up Python 3.11 | success |
| 4 | Catalog validity check | success |
| 5 | Codegen drift gate (messages.py) | success |
| 6 | Vector catalog validity check | success |
| 7 | Codegen drift gate (frame_vectors.py) | success |
| 8 | Install package + test deps | success |
| 9 | ruff lint | success |
| 10 | ruff format check | success |
| **11** | **mypy type check (watermark gate)** | **failure** |
| 12 | Run pytest with coverage | **skipped** (expected — job stops on step 11's failure) |
| 13 | Smoke test — firestarter entry point and --help | **skipped** (expected, same reason) |
| 25 | Post Set up Python 3.11 | skipped (cleanup step, expected given the failure upstream) |
| 26 | Post Run `actions/checkout@v4` | success |
| 27 | Complete job | success |

**Step 11's log, verbatim:**
```
mypy errors: 72 (watermark: 35)
FAIL: 72 errors exceeds watermark 35. New errors introduced.
##[error]Process completed with exit code 1.
```

This matches Task 1's local pre-fix rehearsal of the *fail-open* reading (`mypy errors: 1`) only in that both used the same `tools/check_mypy_watermark.py` invocation — the discrepancy (1 locally vs. 72 on the runner) is exactly the bug documented below: this devcontainer's `mypy` silently reports 1 (fail-open), while the runner's clean environment reports the true 72.

### Head SHA comparison — string-equal

```
local HEAD before comparison: v1.23-py32f071-integration @ 84cdd86e1f21f88d59129c849ca2ab0f8c8e1901
run.headSha:                                                84cdd86e1f21f88d59129c849ca2ab0f8c8e1901
```
**String-equal: MATCH.** (This session then added commit `a62ca76` on top, after the comparison — see the fix below. `git rev-parse --abbrev-ref HEAD` recorded as `v1.23-py32f071-integration` both before and after the comparison; only `HEAD`'s SHA advanced, via the fix commit made *after* this comparison, not a branch change.)

### Pushed-ref content verification

```bash
git fetch origin   # read-only
git rev-parse origin/v1.23-py32f071-integration
→ 84cdd86e1f21f88d59129c849ca2ab0f8c8e1901   (string-equal to run.headSha)

git show origin/v1.23-py32f071-integration:.github/workflows/ci.yml | grep -c 'ci-py32:'
→ 1
git show origin/v1.23-py32f071-integration:.github/workflows/ci.yml | grep -c 'workflow_dispatch:'
→ 1
```
**Confirmed: the ref that was actually built carries both the `ci-py32` job and the `workflow_dispatch:` trigger.**

### Claim ceiling

A green `ci-py32` leg proves the extra installs resolve, `pyusb` genuinely imports at version `1.3.1`, and its `usb.core`/`ctrl_transfer` API is shaped as the tests expect **on a GitHub-hosted runner**. It proves **nothing** about a PY32F071 board: no PCB exists, no DFU device is present in CI, and HOST-03's readback ceiling remains asserted against a mock only. The primary `ci` job's failure is unrelated to any of that — it is a pre-existing, now-newly-visible mypy debt problem (see below), not a regression in the DFU/py32 code paths this phase built.

## Added Scope (operator-approved: "fix my 3, record the rest")

### Half 1 — Fixed: the 3 `func-returns-value` errors Phase 127 added

**Root cause (independently re-derived, not assumed):** `firestarter/cli_handlers.py:147` declares `def _reject_py32_only_option(name: str, given: bool) -> None:`. Three tests added in Plan 127-04 (`tests/test_py32_channel_gating.py:303,311,319`) asserted `cli_handlers._reject_py32_only_option(...) is None`. mypy's `func-returns-value` check fires on **any** use of a None-annotated function's return value in an expression — confirmed empirically with a 4-case probe script (`r = f(1)`, `assert f(1) is None`, `f(1)` alone, `r2 = f(1); assert r2 is None`): only the bare-call form (`f(1)` alone, no capture, no comparison) is mypy-clean.

**Fix:** rewrote all three assertions as bare calls, each with an inline comment explaining why (no silent change — the next reader sees the mypy rule immediately). The behaviour under test — "does not raise" — is asserted identically by a bare statement (pytest fails the test if the call raises); nothing was weakened, no test was skipped, deleted, or `xfail`'d, and no `# type: ignore` was added anywhere.

```python
# before (3x, at lines 303/311/319):
assert cli_handlers._reject_py32_only_option("--usb-id", False) is None

# after:
cli_handlers._reject_py32_only_option("--usb-id", False)
```

**Verification, all measured this session:**
- `pytest tests/test_py32_channel_gating.py -q --no-cov` → **14 passed** (unchanged count, same as before the fix).
- `pytest tests/ -q --no-cov` (full suite, devcontainer, pyusb absent) → **1293 passed in 169.89s**, **0 failed, 0 skipped** — identical to Task 1's pre-fix baseline.
- `ruff check firestarter/ tests/` → `All checks passed!`
- `ruff format --check firestarter/ tests/` → `114 files already formatted`
- **mypy, measured with a real invocation** (throwaway venv on `/home/vscode/.local/bin/python3.11`, `.[test]` installed, `<venv>/bin/python -m mypy firestarter/ tests/`, venv deleted afterward):

  | Snapshot | mypy error count |
  |---|---|
  | pre-127 baseline (`ccbc401`, via `git archive`) | **69** |
  | post-127, pre-fix (`84cdd86`, this plan's Task 1 HEAD) | **72** |
  | post-127, post-fix (working tree after commit `a62ca76`) | **69** |

  **69 → 72 → 69. The fix returns the branch to exactly the pre-127 baseline — Phase 127 adds zero net mypy debt.** A full-diff comparison of both snapshots' error lists (`diff` of sorted `file:line: error` lines) confirmed the *only* new lines at `84cdd86` were the 3 `func-returns-value` errors in `test_py32_channel_gating.py`; the other line-number deltas between the two snapshots are the same pre-existing errors shifted by unrelated in-between insertions, not new errors.

**Committed:** `a62ca76` (fix), `firestarter_app` repo, `v1.23-py32f071-integration` branch. Staged only `tests/test_py32_channel_gating.py` — the pre-existing ` M .gitignore` line was left untouched and unstaged.

### Half 2 — Recorded, NOT fixed: the fail-open gate and the 69 inherited errors

**Per operator instruction, `tools/check_mypy_watermark.py` was NOT modified, and none of the 69 inherited mypy errors were touched, and the watermark (35) was NOT raised.** This is gate-hardening work belonging to Phase 123's charter, not Phase 127's. Recorded here in a form Plan 127-12 can lift verbatim into `127-NONREGRESSION.md`:

**Finding: `tools/check_mypy_watermark.py` has TWO stacked fail-open defects, confirmed by direct reproduction:**

1. **It shells out to a bare `mypy` from `PATH`** (`tools/check_mypy_watermark.py:56`: `subprocess.run(["mypy", "firestarter/", "tests/"], ...)`), not `sys.executable -m mypy`. This means the gate's result depends on whichever `mypy` binary happens to resolve first on the caller's `PATH` — in this devcontainer, that is `/home/vscode/.local/bin/mypy`, an independently-managed interpreter/environment, not the project's own installed dependency set.

2. **Under this devcontainer's resolved `mypy` (running on Python 3.12), the project's `pyproject.toml` `[mypy]` config (`python_version = "3.9"`) is rejected outright**, and a `numpy` stub then aborts the run before any real project file is checked. mypy reports exactly **1 error**, `count_mypy_errors()`'s `re.search(r"Found (\d+) errors?", ...)` matches it, `1 <= 35`, and the gate prints `OK`/`INFO: ... below watermark` — **without having type-checked a single project file.**

**Reproduction (verbatim, re-run this session):**
```
$ cd /workspaces/firestarter_app && python3 -m mypy firestarter/ tests/
pyproject.toml: [mypy]: python_version: Python 3.9 is not supported (must be 3.10 or higher)
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)

$ python tools/check_mypy_watermark.py
mypy errors: 1 (watermark: 35)
INFO: 1 errors — 34 below watermark. Lower watermark in pyproject.toml.
```

**Measured sequence recorded above (69 / 72 / 69)** was obtained by bypassing both layers — a throwaway `.[test]` venv on `/home/vscode/.local/bin/python3.11` (a supported interpreter matching `python_version = "3.9"`'s intent, i.e. not py3.12), invoking `mypy` via `sys.executable -m mypy` (the venv's own `python -m mypy`, not a bare `PATH` lookup), against `git archive` snapshots of each commit.

**Consequence:** the local mypy gate in this devcontainer has been reporting green **without type-checking anything** since whatever point the devcontainer's Python/mypy combination first hit this rejection (not dated precisely by this plan — that dating is out of scope here). Every phase executed in this devcontainer since roughly Phase 113 has been accumulating mypy debt (69 errors currently, pre-existing and inherited, none from Phase 127) **completely invisible to the local gate**. This branch's first-ever CI run is the first time in this milestone that a genuinely clean environment (the GitHub-hosted runner, Python 3.11.15, `mypy` installed fresh via `pip install -e '.[test]'` inside the job — no devcontainer-specific `PATH` shadowing, no py3.12-vs-3.9-config mismatch) actually ran the check for real, and it surfaced the debt.

**The inherited 69 errors remain OPEN. The primary `ci` job is RED (`72 > 35` at the moment of this run; `69 > 35` even after this plan's fix) until a dedicated phase (Phase 123's charter, or a new one) either fixes the 69 errors or deliberately raises the watermark with justification. Stated plainly, not softened: `ci` will fail on any future dispatch of this branch against `84cdd86`+`a62ca76` (or any descendant) until that work happens, independent of anything in Phase 127.**

## Task Commits

1. **Task 1: Record the pre-push state and print the exact commands** — prior session, no commit (read-only capture into this SUMMARY)
2. **Added scope: fix the 3 func-returns-value mypy errors** — `a62ca76` (fix)

**Meta-repo tracking commit:** pending (this SUMMARY + gitlink bump, committed next per `<final_commit>`)

## Files Created/Modified

- `firestarter_app/tests/test_py32_channel_gating.py` — 3 assertions rewritten from `assert f(...) is None` to bare calls, each with an explanatory comment

## Decisions Made

See `key-decisions` in the frontmatter above for the full list (attribution, the log-capture oddities around the pytest count and the A4 branch, and the added-scope split).

## Deviations from Plan

### Approved Added Scope (not a Rule 1-4 deviation — explicitly directed by the operator via the orchestrator)

**1. [Operator-directed] Fixed the 3 `func-returns-value` mypy errors Phase 127 introduced**
- **Found during:** Task 3, while re-deriving the CI run's facts — the primary `ci` job's failure at the mypy watermark gate surfaced this.
- **Issue:** `tests/test_py32_channel_gating.py` (Plan 127-04) asserted the return value of a `-> None`-annotated function, tripping mypy's `func-returns-value` check 3 times. Combined with a devcontainer-local fail-open bug in the watermark gate itself, this had never been visible locally.
- **Fix:** rewrote the 3 assertions as bare calls (no weakening — the "does not raise" behaviour is preserved identically). Re-measured mypy count with a real (non-fail-open) invocation: 69 (pre-127) → 72 (post-127, pre-fix) → 69 (post-127, post-fix).
- **Files modified:** `firestarter_app/tests/test_py32_channel_gating.py`
- **Commit:** `a62ca76`
- **NOT fixed, per explicit operator instruction:** the fail-open gate itself (`tools/check_mypy_watermark.py`) and the 69 inherited mypy errors. Both are recorded as findings above for Plan 127-12 / a future gate-hardening phase, not altered here.

---

**Total deviations:** 1 approved added-scope item (operator-directed, not an autonomous Rule 1-4 fix), plus 1 explicitly-declined fix (the fail-open gate + inherited debt, recorded not repaired per instruction).
**Impact on plan:** HOST-04's CI evidence is now on the record, independently re-derived. Phase 127's own contribution to mypy debt is provably zero. The pre-existing, much larger mypy-debt-behind-a-broken-gate problem is now visible and documented for the phase/milestone that owns fixing it — it was not introduced by this plan and this plan does not claim to have resolved it.

## Issues Encountered

- The raw ci-py32 job log (fetched both via `gh run view --log` and `gh api .../logs`) does not contain a printed pytest summary line ("N passed in X.XXs") for the API-surface test step — only the dot-progress line followed immediately by the next step's cleanup output. Worked around by counting dots (6) and cross-checking against Task 1's independently rehearsed local count (also 6). Recorded as an open, non-blocking log-capture oddity, not investigated further (out of scope for this plan).
- Similarly, `test_usb_core_find_for_real`'s internal either/or outcome (enumerated vs. `NoBackendError`) is not printed anywhere reachable in the captured log, so research assumption A4's *which-branch* question is recorded as unresolved from this run rather than guessed.

## User Setup Required

None — no external service configuration required. The push and dispatch were already performed (by the orchestrator, under operator authorization) before this session began; no further action is needed to obtain HOST-04's evidence.

## Next Phase Readiness

- **HOST-04's CI evidence is complete and on the record** for Plan 127-12 to cite: run `30707902225`, `https://github.com/henols/firestarter_app/actions/runs/30707902225`, headSha `84cdd86e1f21f88d59129c849ca2ab0f8c8e1901` (string-equal, re-derived), `ci-py32` all-green with pyusb `1.3.1` and 6/6 pytest, per-step detail above.
- **127-12 must also carry forward, as an open non-blocking finding:** `tools/check_mypy_watermark.py`'s two stacked fail-open defects, the reproduction commands above, and the fact that the primary `ci` job will be RED on this branch (72 errors pre-fix / 69 post-fix, both over the 35 watermark) until a dedicated phase addresses the inherited debt or the watermark is deliberately raised with justification.
- Full app suite unaffected: **1293 collected / 1293 passed / 0 failed / 0 skipped**, ruff/format clean, both before and after this plan's fix commit.
- HOST-01..HOST-08 all remain `[ ]` Pending in `.planning/REQUIREMENTS.md` — unticked by this plan, as required. Only Plan 127-12 may tick them.
- No push, no dispatch, no tag, no release performed by this executor. `/workspaces/firestarter` (firmware repo) untouched throughout.

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_py32_channel_gating.py` (modified)
- FOUND: commit `a62ca76` in `firestarter_app` git log
- FOUND: run `30707902225` at `https://github.com/henols/firestarter_app/actions/runs/30707902225` (re-queried live, `conclusion=failure`, `ci-py32` job `conclusion=success`)
- FOUND: `origin/v1.23-py32f071-integration` at `84cdd86e1f21f88d59129c849ca2ab0f8c8e1901`, string-equal to `run.headSha`
- FOUND: `.planning/phases/127-host-dfu-installer/127-11-SUMMARY.md`
- CONFIRMED: HOST-01..HOST-08 all `[ ]` Pending in `.planning/REQUIREMENTS.md`
