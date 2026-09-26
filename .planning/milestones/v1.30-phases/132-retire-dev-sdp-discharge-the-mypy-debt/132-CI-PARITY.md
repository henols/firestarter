# Phase 132 — CI-Parity Readings

Two readings live in this file: a `## 1. Before` section (this plan, 132-01, taken before any
deletion or mypy fix lands) and a `## 2. After` section (appended by a later plan, after the
deletion + discharge, per the ROADMAP's cross-cutting rule that the recipe runs before AND after).

## 1. Before (pre-deletion, pre-discharge)

**Preconditions verified, each a hard stop on failure — none tripped:**

(a) `git -C /workspaces/firestarter_app branch --show-current` printed exactly
`gsd/v1.30-sdp-surface-retirement`.
(b) `git -C /workspaces branch --show-current` printed exactly
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`.
(c) `git -C /workspaces/firestarter_app status --porcelain` was non-empty, but every line matches
the plan's own `<pre_existing_tree_state>` dirt list (` M .gitignore`, `?? .coverage`,
`?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh`) — pre-existing, not
introduced by this plan, and not touched here. No untracked-but-unaccounted change was present.
(d) `BOARD-ATTACHED: none` — read from `tools/ci_parity.sh`'s own stamp below, not probed
separately.

**App-repo HEAD at the time of the run:**
`8caf77f458ba1bd1eeff47f9747838dc4183e2ca` (short: `8caf77f`), on branch
`gsd/v1.30-sdp-surface-retirement`. This matches the plan's `<measured_ground_truth>` HEAD exactly.

**Run: `bash tools/ci_parity.sh` from `/workspaces/firestarter_app`, captured verbatim.**

```
---------------------------------
Leg 1: FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q
Proves: the suite passes with the firmware sibling absent -- the standalone-CI condition.
---------------------------------
[... suite output, various SKIPPED lines for firmware-checkout-absent cases ...]
Leg 1 exit code: 0

---------------------------------
Leg 2: python3 -m pytest tests/ -q
Proves: the suite passes with the firmware sibling present (this devcontainer's own layout).
---------------------------------
[... 100% pass, 30 snapshots passed ...]
Leg 2 exit code: 0

---------------------------------
Leg 3: ruff lint + ruff format --check, at ci.yml's exact path set
Proves: ruff is CI-scoped correctly today; the failure mode this leg guards against is running ruff locally at a different scope.
---------------------------------
All checks passed!
116 files already formatted
Leg 3 exit code: 0 (ruff check: 0, ruff format --check: 0)

---------------------------------
Leg 4: python3 tools/check_mypy_watermark.py
Proves: the hardened watermark gate (GATE-01/02/03/04) reaches a legible terminal state. A local exit 2 here (ambient numpy PEP-695 stub truncating mypy) is the gate working correctly, not a script defect -- see this script's header and 131-CI-PARITY.md.
---------------------------------
ERROR: mypy exited 2, which is neither the clean-run (0) nor errors-found (1) exit code. Treating as a tool/config failure, not a clean tree.
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
Leg 4 exit code: 2

=================================
CI-PARITY SUMMARY
=================================
Leg 1 (pytest, empty sibling root):  exit 0
Leg 2 (pytest, sibling present):     exit 0
Leg 3 (ruff check + format --check): exit 0
Leg 4 (mypy watermark gate):         exit 2
BOARD-ATTACHED: none
Python: Python 3.12.13
CI-PARITY: FAIL (legs:4)
```

**Which legs passed and which did not:** Legs 1, 2, and 3 passed (exit 0 each). Leg 4 exited 2.

**Leg 4's exit 2 is the expected, correct pre-change shape — not a defect.** Quoting
`tools/ci_parity.sh`'s own leg-4 banner: *"A local exit 2 here (ambient numpy PEP-695 stub
truncating mypy) is the gate working correctly, not a script defect."* The devcontainer's ambient
`numpy` install ships a `.pyi` stub using PEP-695 `type` statement syntax that this environment's
mypy target (`python_version = "3.10"`) cannot parse, so mypy aborts with returncode 2 before
producing any per-source-file count. Phase 131's hardened
`classify_mypy_result()` correctly refuses to report a count for this truncated run (guard 1:
"returncode not in (0, 1)") rather than silently reporting a plausible-looking number. This is
exactly why this plan's Task 2 builds a separate numpy-free CI-replica venv — not to "fix" this
leg, and this leg is deliberately left un-weakened: no `|| true`, no guard removal, no forced
green aggregate exit. The aggregate `CI-PARITY: FAIL (legs:4)` is therefore the correct,
expected pre-change reading, and matches the identical shape Phase 131 recorded in its own
`131-CI-PARITY.md`.

**The one gap this recipe does not cover, and that this phase must close by other means.**
`.github/workflows/ci.yml`'s `ci` job runs pytest as:

```
pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70
```

whereas `tools/ci_parity.sh` legs 1 and 2 run `pytest tests/ -q` with **no coverage flags at
all** — this is stated explicitly in the script's own header under "WHAT THIS DELIBERATELY DOES
NOT MIRROR": *"pytest's `--cov=firestarter --cov-report=term-missing --cov-fail-under=70`
coverage gate (legs 1/2 below run the same suite WITHOUT the coverage flags -- proving
suite-pass, not coverage-floor)."* The `--cov-fail-under=70` floor is a real `ci` job step that
neither leg 1 nor leg 2 would catch a drop below. This matters directly to this phase: Phase 132
deletes `dev sdp` — approximately 126 lines of well-covered production code inside
`cli_handlers.py`, plus roughly 550 lines of its test module (`tests/test_dev_sdp_cmd.py` →
`tests/test_sdp_honesty.py`, most content pruned per D-04) — and nothing in `ci_parity.sh`'s
existing two pytest legs would notice if that deletion pushed the suite below the 70% floor.
Task 2's `tools/ci_replica_venv.sh` closes this gap with its own leg 5, running pytest with CI's
exact coverage invocation.

## 2. After (post-deletion, post-discharge)

**Run: `bash tools/ci_parity.sh` from `/workspaces/firestarter_app`, on the finished tree.**

**App-repo HEAD at the time of the run:** `42a1971a072db2f3bcec558a3dc2bcb3d5d65e08` (short:
`42a1971`), on branch `gsd/v1.30-sdp-surface-retirement` — plan 132-08's task 2 commit, the last
submodule commit before this plan. `git status --porcelain` at run time showed only the same
pre-existing dirt this plan's `<pre_existing_tree_state_READ_THIS>` names (` M .gitignore`,
`?? .coverage`, `?? .planning/config.json`, `?? SECURITY.md`, `?? write_test_port.sh`) — no new,
unaccounted change.

```
---------------------------------
Leg 1: FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q
Proves: the suite passes with the firmware sibling absent -- the standalone-CI condition.
---------------------------------
[... 1297 passed, 30 snapshots passed, 38 SKIPPED (firmware-checkout-absent cases) ...]
Leg 1 exit code: 0

---------------------------------
Leg 2: python3 -m pytest tests/ -q
Proves: the suite passes with the firmware sibling present (this devcontainer's own layout).
---------------------------------
[... 1297 passed, 30 snapshots passed, no SKIPPED ...]
Leg 2 exit code: 0

---------------------------------
Leg 3: ruff lint + ruff format --check, at ci.yml's exact path set
Proves: ruff is CI-scoped correctly today; the failure mode this leg guards against is running ruff locally at a different scope.
---------------------------------
All checks passed!
117 files already formatted
Leg 3 exit code: 0 (ruff check: 0, ruff format --check: 0)

---------------------------------
Leg 4: python3 tools/check_mypy_watermark.py
Proves: the hardened watermark gate (GATE-01/02/03/04) reaches a legible terminal state. A local exit 2 here (ambient numpy PEP-695 stub truncating mypy) is the gate working correctly, not a script defect -- see this script's header and 131-CI-PARITY.md.
---------------------------------
ERROR: mypy exited 2, which is neither the clean-run (0) nor errors-found (1) exit code. Treating as a tool/config failure, not a clean tree.
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
Leg 4 exit code: 2

=================================
CI-PARITY SUMMARY
=================================
Leg 1 (pytest, empty sibling root):  exit 0
Leg 2 (pytest, sibling present):     exit 0
Leg 3 (ruff check + format --check): exit 0
Leg 4 (mypy watermark gate):         exit 2
BOARD-ATTACHED: none
Python: Python 3.12.13
CI-PARITY: FAIL (legs:4)
```

**Before-versus-after comparison, one row per leg:**

| Leg | Before (132-01, `8caf77f`) | After (this plan, `42a1971`) | Changed? |
|---|---|---|---|
| Leg 1 (pytest, empty sibling root) | exit 0 | exit 0 | No |
| Leg 2 (pytest, sibling present) | exit 0 | exit 0 | No |
| Leg 3 (ruff check + format --check) | exit 0, 116 files formatted | exit 0, 117 files formatted | File count only — `firestarter/sdp_honesty.py` and `tests/test_sdp_honesty.py` are net-new formatted files this phase added; ruff's own verdict (clean) is unchanged |
| Leg 4 (mypy watermark gate) | exit 2 (ambient numpy PEP-695 stub) | exit 2 (same cause) | No — see below |
| BOARD-ATTACHED | none | none | No |
| Aggregate | `CI-PARITY: FAIL (legs:4)` | `CI-PARITY: FAIL (legs:4)` | No |

**Legs 1 and 2, interpreted by name against their recorded traps.** Leg 1 (empty `FIRESTARTER_FW_ROOT`,
the standalone-CI condition) passed at exit 0 with the same shape of `SKIPPED` lines for
firmware-checkout-absent cases as the before-run — the recorded sibling-layout-masking trap did not
fire, because this plan changed no test that depends on the firmware sibling's presence. Leg 2
(sibling present, this devcontainer's own layout) also passed at exit 0 with zero `SKIPPED` lines,
and the recorded attached-board trap (no-programmer-found tests going red when a live serial device
is present) did not fire either, because no board is attached in this session
(`ls /dev/ttyACM* /dev/ttyUSB*` → no such device), matching the `BOARD-ATTACHED: none` stamp both
runs share. Both legs' outcomes are therefore unchanged and neither recorded trap is implicated.

**Leg 4's exit 2 is unchanged, and that is the correct, expected shape — not a regression and not a
fix.** The ambient numpy stub (`numpy 2.5.1`'s PEP-695 `type` statement) is still present in this
devcontainer's system Python 3.12 interpreter, which `ci_parity.sh` deliberately uses rather than a
numpy-free venv (D-07: this recipe's contract is a faithful CI mirror, not a substitute
environment). The recipe's own leg-4 header — quoted identically in the before-section above — states
this is the gate working correctly, not a defect. No suppression, no `|| true`, and no guard removal
were added: `git -C /workspaces/firestarter_app diff --stat tools/ci_parity.sh` produces no output,
confirmed at commit time. The aggregate `CI-PARITY: FAIL (legs:4)` is therefore the correct, expected
post-change reading too, exactly as it was pre-change — per the recipe's own header, phase acceptance
never required a zero aggregate exit from this script.

**Replica script (`tools/ci_replica_venv.sh`) run on the same tree, all five legs recorded:**

```
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
MYPY-VERSION: mypy 2.3.0 (compiled: yes)
NUMPY-PRESENT: no
Python: Python 3.11.15
Leg 1 (venv create-or-reuse + install): exit 0  (REUSED: .venv/ci-replica already existed)
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Leg 4 (mypy watermark gate):             exit 0
Leg 5 (pytest --cov, CI's exact args):   exit 0
CI-REPLICA: PASS
```

Leg 4's stamp lines, verbatim:

```
Found 32 errors in 12 files (checked 122 source files)
checked 122 source files
mypy errors: 32 (watermark: 35)
INFO: 32 errors -- 3 below watermark (35). The watermark may be lowered to 32, but only if this
run is complete: this run's mypy invocation passed both the completion-clause guard and the
MIN_CHECKED_SOURCE_FILES coverage floor, which is the evidence of completeness. Lower it in the
same commit as the fixes that reduced the count -- never to make a failing gate pass.
```

**This matches plan 132-06's reading exactly: 32 errors, 12 files, checked 122 source files,
watermark 35.** No divergence to record — the count has held stable across plans 132-06, 132-07,
132-08 and now this plan's re-measurement.

Leg 5's coverage result, quoted from its own output:

```
Required test coverage of 70% reached. Total coverage: 81.72%
1297 passed in 117.17s (0:01:57)
30 snapshots passed.
```

Coverage is **81.72%** against the workflow's **70%** floor — well clear, and unchanged from
132-08's own recorded reading, confirming the ~126-line-of-production plus ~550-line-of-test
deletion this phase made did not push the suite toward the floor.

**Tree state after both recipes:** `git -C /workspaces/firestarter_app status --porcelain` showed
only the pre-existing dirt named above (unchanged by either recipe run — both are read-only against
the tracked tree; `.coverage` is regenerated by leg 5 but was already untracked before this run).
`git -C /workspaces log -1 --name-only` at commit time lists only paths under `.planning/`.
