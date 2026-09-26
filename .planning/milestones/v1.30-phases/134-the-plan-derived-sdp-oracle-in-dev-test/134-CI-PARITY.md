# 134-CI-PARITY: Pre-edit CI-parity + CI-replica baseline (plan 134-01, Task 1)

**Owner requirement (evidence foundation for):** LEG-03 and every later plan in this phase — this is
the pre-edit budget measured **before any production line moves**, mirroring `133-BASELINE.md`'s shape
and correcting the file-budget reading Phase 133 D-15 left inverted.

**Date:** 2026-08-04
**Repo:** `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`
**HEAD:** `57e8eb5` (plan 133-06's task commit — the last commit before any Phase 134 edit)
**Interpreter:** Python 3.12.13 (this devcontainer, ambient) / Python 3.11.15 (the numpy-free
`ci_replica_venv.sh`, CI's actual interpreter)
**mypy:** 2.3.0 (compiled: yes)

`git -C /workspaces/firestarter_app status --porcelain`:
```
 M .gitignore
?? .coverage
?? .planning/config.json
?? SECURITY.md
?? write_test_port.sh
```
This is the **pre-existing dirt** already present at the start of Phase 133 and Phase 132 (see
`133-CI-PARITY.md`'s identical note) — not something this plan introduced. No file under
`firestarter/` or `tests/` is touched by this task; only this document (a meta-repo artifact) is
written.

---

## Before (pre-edit)

### 1. No-board condition (ambient, not a discrete recipe leg)

```
$ ls /dev/ttyACM* /dev/ttyUSB*
ls: cannot access '/dev/ttyACM*': No such file or directory
ls: cannot access '/dev/ttyUSB*': No such file or directory
```

**No board was attached** for any measurement below.

**`tools/ci_parity.sh` has no no-board leg.** The no-board condition is ambient — a stamp
(`BOARD-ATTACHED:`) in the script's own summary, never a fifth leg with its own pass/fail. Recording
the actual board state as an observation, not as a claimed leg, per this phase's own VALIDATION.md
warning and the ROADMAP's cross-cutting instruction.

### 2. `bash tools/ci_parity.sh` — aggregate result and per-leg detail

```
$ cd /workspaces/firestarter_app && bash tools/ci_parity.sh
...
SKIPPED [1] tests/test_sdp_table_parity.py:176: firestarter firmware checkout absent (no <tmp>/.git marker)
SKIPPED [1] tests/test_sdp_table_parity.py:200: firestarter firmware checkout absent (no <tmp>/.git marker)
SKIPPED [1] tests/test_sdp_table_parity.py:242: firestarter firmware checkout absent (no <tmp>/.git marker)
SKIPPED [1] tests/test_sdp_table_parity.py:300: firestarter firmware checkout absent (no <tmp>/.git marker)
Leg 1 exit code: 0
...
1338 passed (30 snapshots passed)
Leg 2 exit code: 0
...
All checks passed!
119 files already formatted
Leg 3 exit code: 0 (ruff check: 0, ruff format --check: 0)
...
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

**Aggregate `CI-PARITY: FAIL (legs:4)` is the expected local shape** — identical to `133-CI-PARITY.md`
§2: the devcontainer's ambient numpy install carries a PEP-695 `type` statement its own Python 3.12
mypy cannot parse, so leg 4 aborts before completing and reports no count. This is the hardened
watermark gate (GATE-01..04) correctly refusing to fabricate a number for a truncated run, not a
defect. §4 below runs the numpy-free replica venv for the trustworthy count.

**The devcontainer is Python 3.12 while CI is 3.9/3.11**, and the devcontainer's own `mypy` exits 2
against numpy — so only the `ci-replica` numbers below are quotable as this phase's real budget.

### 3. `bash tools/ci_replica_venv.sh` — REAL mypy count, the only local path to a trustworthy number

```
$ cd /workspaces/firestarter_app && bash tools/ci_replica_venv.sh
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
...
Leg 1 (venv create-or-reuse + install): exit 0
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Found 33 errors in 13 files (checked 124 source files)
checked 124 source files
mypy errors: 33 (watermark: 35 )
Leg 4 (mypy watermark gate):             exit 0
...
1338 passed in 147.77s (0:02:27)
Required test coverage of 70% reached. Total coverage: 81.84%
Leg 5 (pytest --cov, CI's exact args):   exit 0
=================================
CI-REPLICA SUMMARY
=================================
NUMPY-PRESENT: no
CI-REPLICA: PASS
```

**Real, in-range mypy count: `mypy errors: 33 (watermark: 35)`, `checked 124 source files`.** This is
byte-identical to `133-CI-PARITY.md` §4's closing figure (Phase 133 closed at 33/124) — expected,
since no Phase 134 edit has landed yet.

**The starting budget this phase spends against:**
- **mypy headroom: 2** (33 errors vs watermark 35). Do not move the watermark (`35` in
  `pyproject.toml`) — this phase spends against the headroom, never widens it.
- **`checked` vs `MIN_CHECKED_SOURCE_FILES = 120`**: currently 124, a margin of **4** above the floor.
  **`MIN_CHECKED_SOURCE_FILES` is a FLOOR** (`checked < 120` ⇒ fail, `tools/check_mypy_watermark.py:48`
  and its docstring), so **adding source/test files moves `checked` further ABOVE the floor** — it is
  not a budget that gets "spent" by adding files. This corrects Phase 133 D-15's inverted reading
  ("file budget is spent — 0 slots for Phase 134"), which is measured-wrong: Phase 134 is free to add
  test modules (`134-CONTEXT.md` correction 4).

### 4. `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` — passed count and coverage

```
$ cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q
...
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1338 passed in 144.38s (0:02:24)
```

**1338 passed** (30 snapshots passed), coverage **81.84%** against the 70% floor (from §3's leg 5,
the same invocation with `--cov`). Test-file count: `ls tests/*.py | wc -l` = **90**, matching
`133-CI-PARITY.md`'s closing figure exactly — no Phase 134 test module exists yet.

### 5. Cross-repo commit note

`134-CI-PARITY.md` (this document) is committed in the **meta repo** (`/workspaces`, branch
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). It makes **no** edit inside the
`firestarter_app` submodule — every command above only reads and runs the submodule's existing
tooling. `firestarter` (firmware) is untouched: this phase is host-only by design.

No `git push`, `git merge`, `git tag`, `gh workflow run`, `gh release`, or `twine upload` was run to
produce any measurement in this document.

---

*The `## After` section is written by plan `134-11` at phase close.*

---

## After (post-edit)

**Date:** 2026-08-04
**Repo:** `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`
**HEAD:** the phase's final engine + test source (last commit of plan `134-10`, `2b7a702`)
**Interpreter:** Python 3.12.13 (this devcontainer, ambient) / Python 3.11.15 (the numpy-free
`ci_replica_venv.sh`, CI's actual interpreter)
**mypy:** 2.3.0 (compiled: yes)

### 1. No-board condition (ambient, not a discrete recipe leg)

```
$ ls /dev/ttyACM* /dev/ttyUSB*
ls: cannot access '/dev/ttyACM*': No such file or directory
ls: cannot access '/dev/ttyUSB*': No such file or directory
```

**No board was attached** for any measurement below — unchanged from the `## Before` section.
`tools/ci_parity.sh` still has **no discrete no-board leg** — the board dimension is an ambient
condition of legs 1 and 2, never a fifth leg with its own pass/fail; the script's only board-related
output is the non-gating `BOARD-ATTACHED:` stamp in its own summary (§2 below). This phase added no
board-dependent test.

### 2. `bash tools/ci_parity.sh` — every leg's exit status

```
$ cd /workspaces/firestarter_app && bash tools/ci_parity.sh
...
Leg 1 exit code: 0
...
Leg 2 exit code: 0
...
Leg 3 exit code: 0 (ruff check: 0, ruff format --check: 0)
...
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

- **Leg 1** (`FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q`, standalone-CI shape,
  firmware sibling absent): **exit 0**. This leg deliberately points `FIRESTARTER_FW_ROOT` at an
  empty directory — the devcontainer's own sibling layout (`firestarter/` checked out next to
  `firestarter_app/`) otherwise masks CI-only test defects, per this phase's own
  `134-VALIDATION.md` warning and the same discipline `133-CI-PARITY.md` §2 recorded. Skips are the
  same `firestarter firmware checkout absent` shape as the `## Before` section — no new skip reason.
- **Leg 2** (`python3 -m pytest tests/ -q`, firmware sibling present): **exit 0**.
- **Leg 3** (`ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/`): **exit
  0** — "All checks passed!" / "120 files already formatted" (`## Before`: "119 files already
  formatted" — +1 file is this phase's one net-new formatted file, `tests/test_sdp_recovery_wording.py`
  minus... see §5's file-count accounting; the fixtures file lives under `tests/fixtures/`, also
  ruff-scoped under `tests/`).
- **Leg 4** (`python3 tools/check_mypy_watermark.py`): **exit 2 — expected locally, unchanged
  reason from the `## Before` section**: the ambient devcontainer numpy install carries a PEP-695
  `type` statement this same Python 3.12 mypy cannot parse, so the run aborts before completing and
  prints no `(checked N source files)` completion clause. The hardened watermark gate correctly
  refuses to report a count for an incomplete run. §3 below runs the numpy-free replica venv, the
  only local path to a trustworthy count.

**Aggregate `CI-PARITY: FAIL (legs:4)` is the expected local shape, unchanged from `## Before`** —
acceptance does not require a zero aggregate exit locally; leg 4's exit 2 is discharged by §3.

### 3. `bash tools/ci_replica_venv.sh` — REAL mypy count, the only local path to a trustworthy number

```
$ cd /workspaces/firestarter_app && bash tools/ci_replica_venv.sh
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
...
Leg 1 (venv create-or-reuse + install): exit 0
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Found 33 errors in 13 files (checked 126 source files)
checked 126 source files
mypy errors: 33 (watermark: 35)
INFO: 33 errors -- 2 below watermark (35). The watermark may be lowered to 33, but only if this run
is complete: this run's mypy invocation passed both the completion-clause guard and the
MIN_CHECKED_SOURCE_FILES coverage floor, which is the evidence of completeness. Lower it in the same
commit as the fixes that reduced the count -- never to make a failing gate pass.
Leg 4 (mypy watermark gate):             exit 0
...
1437 passed in 205.17s (0:03:25)
Required test coverage of 70% reached. Total coverage: 82.12%
Leg 5 (pytest --cov, CI's exact args):   exit 0
=================================
CI-REPLICA SUMMARY
=================================
NUMPY-PRESENT: no
CI-REPLICA: PASS
```

**Real, in-range mypy count: `mypy errors: 33 (watermark: 35)`, `checked 126 source files`.** Both
thresholds hold: `33 <= 35` and `126 >= 120` (`MIN_CHECKED_SOURCE_FILES`, unmoved).

### 4. `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` — passed count and coverage

```
$ cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q
...
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1437 passed in 192.12s (0:03:12)
```

**1437 passed** (30 snapshots passed, unchanged count), coverage **82.12%** against the 70% floor
(from §3's leg 5, the same invocation with `--cov`). Test-file count: `ls tests/*.py | wc -l` =
**91** (`tests/fixtures/*.py` = 4, not counted by this glob but counted by mypy's own `checked` scan
— see §5).

### 5. Delta table against `## Before (pre-edit)`

| Metric | Before (134-01, pre-edit) | After (134-11, post-edit) | Delta |
|---|---|---|---|
| mypy errors | 33 | 33 | **0** — unchanged across the whole phase |
| mypy watermark | 35 | 35 | 0 (not touched — out of scope this phase) |
| mypy headroom | 2 | 2 | **0 remaining headroom spent** — the phase's 33/35 count never moved |
| `checked` source files | 124 | 126 | **+2** — `MIN_CHECKED_SOURCE_FILES = 120` is a **FLOOR** (correction 4, inverting 133 D-15's reading), so this moves the margin from **4 above the floor to 6 above the floor** — an increase is safe, never a spend |
| test count (`pytest tests/`) | 1338 passed | 1437 passed | **+99** |
| coverage | 81.84% | 82.12% | **+0.28 pp** |
| snapshot count | 30 | 30 | 0 |
| `tests/*.py` file count | 90 | 91 | +1 (`test_sdp_recovery_wording.py`, plan `134-09`) |

**New test files this phase added: 2** — `tests/test_sdp_recovery_wording.py` (plan `134-09`) and
`tests/fixtures/synthetic_nonzero_chip_id.py` (plan `134-10`). The second lives under
`tests/fixtures/`, outside the `tests/*.py` glob in the table row above but inside mypy's `checked`
scan — together they account for the `checked` +2.

**New production symbols this phase added: 29**, measured live via
`git diff --stat 57e8eb5..HEAD -- firestarter/chip_test.py firestarter/diagnostic_report.py firestarter/cli_handlers.py`
and a top-level-symbol diff (one pre-existing constant, `_DESTRUCTIVE_OPS`, is widened by this phase
and excluded here as a modification, not an addition): `OP_WRITE_BASELINE_B`, `OP_WRITE_BASELINE_A`,
`OP_WRITE_INHIBITED`, `OP_WRITE_RESTORED`, `_SDP_LEG_OPS`, `generate_inhibited_pattern`,
`_SDP_BASELINE_GATE_REASON`, `_SDP_UNLOCK_GATE_REASON` (134-01); `_dispatch_sdp_leg` (134-02);
`_SDP_LEG_STEP_ORDER`, `_SDP_LOCKED_REASON` (134-03); `_baseline_closes_sdp_gate`,
`_SDP_BASELINE_OPS`, `_SDP_LEG_GATED_OPS`, `sdp_hold_state`, `sdp_oracle_applicable`,
`SDP_HOLD_HELD`, `SDP_HOLD_NOT_HELD`, `SDP_HOLD_NOT_RUN` (134-04); `_EXIT_CODE_PRECEDENCE`,
`_overall_exit_code` (134-05); `DiagnosticReport.sdp_hold_state` field + `SCHEMA_VERSION = "1.3"`
(134-06, counted here as one bumped constant plus one new field — 2 of the 29);
`_dev_test_exit_code` (134-07); `_ALWAYS_WRITES_PASS_COUNT`, `sdp_left_writable`,
`_SDP_RECOVERY_LOUD`, `_SDP_RECOVERY_NEUTRAL`, `SDP_RECOVERY_CONSTANT_NAMES`, `_sdp_recovery_line`
(134-08). Plans `134-09`/`134-10` added zero production symbols (test-only).

**mypy count did not move across this entire phase (33 → 33) despite +29 new production symbols
and +99 tests** — every new handler-side helper landed inside the mypy STRICT island
(`cli_handlers.py`) fully annotated from birth, and every new engine-side symbol
(`chip_test.py`/`diagnostic_report.py`, neither in the strict island) was still written with type
hints even though not required to be. **The mypy headroom this phase was budgeted to spend (2, per
`134-CI-PARITY.md`'s own `## Before` section) was never spent at all** — a stronger outcome than the
phase's own budget anticipated, not a discrepancy requiring reconciliation.

### 6. Cross-repo commit note

This `## After` section (like the `## Before` section) is committed in the **meta repo**
(`/workspaces`, branch `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). It makes **no**
edit inside the `firestarter_app` submodule — every command above only reads and runs the
submodule's existing tooling. `firestarter` (firmware) remains untouched throughout this phase.

No `git push`, `git merge`, `git tag`, `gh workflow run`, `gh release`, or `twine upload` was run to
produce any measurement in this section.
