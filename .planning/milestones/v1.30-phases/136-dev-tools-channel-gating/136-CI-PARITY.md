# 136-CI-PARITY: Pre-edit CI-parity + CI-replica baseline (plan 136-01, Task 1)

**Owner requirement (evidence foundation for):** every later plan in this phase (136-02, 136-03,
136-04) — this is the pre-edit budget measured **before any production line moves**, mirroring
`134-CI-PARITY.md`'s shape. 136-RESEARCH.md §7 states plainly there is **no mypy number to inherit**
for this phase — this measurement is the phase's only legitimate starting count.

**Date:** 2026-08-05
**Repo:** `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`
**HEAD:** `2b7a702` (plan 134-10's last commit — the last commit before any Phase 136 edit; plan
134-11, the phase-134 close plan, made no submodule commit)
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
This is the **pre-existing dirt** already present at the start of Phases 132/133/134 (see those
phases' own `*-CI-PARITY.md` identical note) — not something this plan introduced. No file under
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
the actual board state as an observation, not as a claimed leg, per `136-VALIDATION.md`'s own
"No hardware is involved anywhere in this phase" note and the cross-cutting instruction carried from
Phases 131/133/134.

### 2. `bash tools/ci_parity.sh` — aggregate result and per-leg detail

```
$ cd /workspaces/firestarter_app && bash tools/ci_parity.sh
...
Leg 1 exit code: 0
...
30 snapshots passed.
Leg 2 exit code: 0
...
All checks passed!
120 files already formatted
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

**Aggregate `CI-PARITY: FAIL (legs:4)` is the expected local shape** — identical to
`134-CI-PARITY.md` §2: the devcontainer's ambient numpy install carries a PEP-695 `type` statement
its own Python 3.12 mypy cannot parse, so leg 4 aborts before completing and reports no count. This
is the hardened watermark gate (GATE-01..04) correctly refusing to fabricate a number for a
truncated run, not a defect. §3 below runs the numpy-free replica venv for the trustworthy count.

**Leg 1** deliberately points `FIRESTARTER_FW_ROOT` at an empty directory — this stops the
devcontainer's sibling layout (`firestarter/` checked out next to `firestarter_app/`) from masking
CI-only test defects, the exact class that fired on the real b15 push (see `tools/ci_parity.sh`'s own
header comment, and Phase 130's post-cut finding).

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
Found 33 errors in 13 files (checked 126 source files)
checked 126 source files
mypy errors: 33 (watermark: 35)
INFO: 33 errors -- 2 below watermark (35). The watermark may be lowered to 33, but only if this run
is complete: this run's mypy invocation passed both the completion-clause guard and the
MIN_CHECKED_SOURCE_FILES coverage floor, which is the evidence of completeness. Lower it in the same
commit as the fixes that reduced the count -- never to make a failing gate pass.
Leg 4 exit code: 0
...
Required test coverage of 70% reached. Total coverage: 82.12%
1437 passed in 213.97s (0:03:33)
Leg 5 (pytest --cov, CI's exact args):   exit 0
=================================
CI-REPLICA SUMMARY
=================================
NUMPY-PRESENT: no
CI-REPLICA: PASS
```

**Real, in-range mypy count: `mypy errors: 33 (watermark: 35)`, `checked 126 source files`.**
136-RESEARCH.md §7 is explicit that there is **no number to inherit for this phase** — this is the
phase's only legitimate starting measurement, and it happens to be byte-identical to Phase 134's own
closing `## After` figures (`134-CI-PARITY.md` §5: mypy 33/126, unchanged across that whole phase).
That is expected, not a coincidence to explain away: nothing landed in the submodule between Phase
134's close and this task (`git log` shows plan 134-11 made no submodule commit; the Phase 135 slot
was deliberately never activated — see `.planning/STATE.md`).

**The starting budget this phase spends against:**
- **mypy headroom: 2** (33 errors vs watermark 35). Do not move the watermark (`35` in
  `pyproject.toml`) — this phase spends against the headroom, never widens it. 136-RESEARCH.md §7
  flags `cli_handlers.py` as inside the strict island (`disallow_untyped_defs = true`); any new
  subclass there (plan 136-03's `_DevGroup`) needs full annotations from birth to avoid spending this
  headroom.
- **`checked` vs `MIN_CHECKED_SOURCE_FILES = 120`**: currently 126, a margin of **6** above the
  floor. `MIN_CHECKED_SOURCE_FILES` is a FLOOR (`checked < 120` ⇒ fail), so adding source/test files
  moves `checked` further ABOVE the floor — never a spend.

### 4. `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` — passed count and coverage

```
$ cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q
...
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1437 passed in 202.47s (0:03:22)
```

**1437 passed** (30 snapshots passed), coverage **82.12%** against the 70% floor (from §3's leg 5,
the same invocation with `--cov`). Test-file count: `ls tests/*.py | wc -l` = **91**, matching
`134-CI-PARITY.md`'s closing figure exactly — no Phase 136 test module exists yet.

### 5. Cross-repo commit note

`136-CI-PARITY.md` (this document) is committed in the **meta repo** (`/workspaces`, branch
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). It makes **no** edit inside the
`firestarter_app` submodule — every command above only reads and runs the submodule's existing
tooling. `firestarter` (firmware) is untouched: this phase is host-only by design.

No `git push`, `git merge`, `git tag`, `gh workflow run`, `gh release`, or `twine upload` was run to
produce any measurement in this document.

---

*The `## After` section is written by plan `136-04` at phase close.*

---

## After (post-edit)

**Date:** 2026-08-05
**Repo:** `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`
**HEAD:** `b1d8f73` (plan `136-04`'s Task 1 commit — the last commit of the phase; Task 2, this
document, makes no submodule commit)
**Interpreter:** Python 3.12.13 (this devcontainer, ambient) / Python 3.11.15 (the numpy-free
`ci_replica_venv.sh`, CI's actual interpreter)
**mypy:** 2.3.0 (compiled: yes)

`git -C /workspaces/firestarter_app status --porcelain -- firestarter` (the firmware submodule):
```
```
**Empty.** No file under `/workspaces/firestarter/` was touched at any point in this phase — this
phase is host-only by design (`136-CONTEXT.md`), and no command in any of the four plans ever `cd`s
into that submodule. No new pip/npm/cargo package was installed anywhere in the phase — `pip list`
was not run again here because `tools/ci_replica_venv.sh` Leg 1 (below) reused the existing venv
without a reinstall, and no plan's action text names a package-manager install command.

### 1. No-board condition (ambient, not a discrete recipe leg)

```
$ ls /dev/ttyACM* /dev/ttyUSB*
ls: cannot access '/dev/ttyACM*': No such file or directory
ls: cannot access '/dev/ttyUSB*': No such file or directory
```

**No board was attached** for any measurement below — unchanged from the `## Before` section, and
consistent with `136-VALIDATION.md`'s own note that this phase has no hardware-dependent claim
anywhere.

### 2. `bash tools/ci_parity.sh` — every leg's exit status

```
$ cd /workspaces/firestarter_app && bash tools/ci_parity.sh
...
Leg 1 exit code: 0
...
30 snapshots passed.
Leg 2 exit code: 0
...
All checks passed!
124 files already formatted
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

**Aggregate `CI-PARITY: FAIL (legs:4)` is the expected local shape, unchanged from `## Before`** —
leg 4's exit 2 is the same ambient-numpy PEP-695 truncation the devcontainer's Python 3.12 mypy hits
every phase; it is the hardened watermark gate correctly refusing to fabricate a count for an
aborted run, not a defect. §3 below runs the numpy-free replica venv for the trustworthy number.
Leg 3's "124 files already formatted" (`## Before`: "120 files already formatted") is +4, exactly
the four new test files this phase added (§5's delta table).

### 3. `bash tools/ci_replica_venv.sh` — REAL mypy count, the only local path to a trustworthy number

```
$ cd /workspaces/firestarter_app && bash tools/ci_replica_venv.sh
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
...
Leg 1 (venv create-or-reuse + install): exit 0
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Found 33 errors in 13 files (checked 130 source files)
checked 130 source files
mypy errors: 33 (watermark: 35)
INFO: 33 errors -- 2 below watermark (35). The watermark may be lowered to 33, but only if this run
is complete: this run's mypy invocation passed both the completion-clause guard and the
MIN_CHECKED_SOURCE_FILES coverage floor, which is the evidence of completeness. Lower it in the same
commit as the fixes that reduced the count -- never to make a failing gate pass.
Leg 4 (mypy watermark gate):             exit 0
...
Required test coverage of 70% reached. Total coverage: 82.14%
1494 passed, 1 warning in 216.70s (0:03:36)
Leg 5 (pytest --cov, CI's exact args):   exit 0
=================================
CI-REPLICA SUMMARY
=================================
NUMPY-PRESENT: no
CI-REPLICA: PASS
```

**`mypy errors: 33 (watermark: 35)`, `checked 130 source files`.** Both thresholds hold:
`33 <= 35` and `130 >= 120` (`MIN_CHECKED_SOURCE_FILES`, unmoved this phase, per this document's
own `## Before` instruction not to move it — confirmed: `pyproject.toml`'s watermark is still `35`).

**Headroom delta against `## Before`: 0.** `## Before` measured `mypy errors: 33 (watermark: 35)`,
headroom 2; this `## After` measurement is the identical `33 (watermark: 35)`, headroom 2. **The
phase spent zero of its entering headroom** — every new/modified symbol this phase introduced
(`channel.py`'s four new functions in plan `136-01`; `cli_handlers.py`'s `_DevGroup` class and
`_DEV_TOOLS_ENABLED` constant in plan `136-02`) was fully annotated from birth, landing inside or
alongside the mypy strict island without adding a single new error. This is a **flat** result, not
a shrink or a grow — stated explicitly per this task's own acceptance criterion, not as "similar."

### 4. `.venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q` — passed count and coverage

```
$ cd /workspaces/firestarter_app && .venv/ci-replica/bin/python -m pytest tests/ -o addopts="" -q
...
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
1494 passed, 1 warning in 201.68s (0:03:21)
```

**1494 passed, 0 failed** (30 snapshots passed, unchanged snapshot count) — **0 failures**, not the
2 pre-existing `test_help`/`test_help_dev` regressions plans `136-02`/`136-03` deferred to this
plan; Task 1 (this plan) discharged both. No third failure appeared. Coverage **82.14%** against
the 70% floor (from §3's leg 5, the same invocation with `--cov`) — up from `## Before`'s 82.12%.
Test-file count: `ls tests/*.py | wc -l` = **95** (`## Before`: 91, +4).

Also independently re-run and confirmed unchanged and green:
- **RESEARCH §5's blast-radius file set** (the six gated commands' existing tests, named in
  `136-VALIDATION.md`'s per-task verification map): `tests/test_cli_handlers.py`,
  `tests/test_consistency_check.py`, `tests/test_eprom_operations.py`, `tests/test_serial_comm.py`,
  `tests/test_validate_oracle.py`, `tests/test_diagnostic_report.py`, `tests/test_matrix_artifact.py`,
  `tests/test_validate_family_cmd.py` — `244 passed` (no failures, no new skips).
- **`tests/test_py32_channel_gating.py`** (the subprocess dual-channel pattern this phase's own
  `test_dev_group_channel_gating.py` was structurally adapted from, per `136-03-SUMMARY.md`) —
  `14 passed`, itself unchanged and still the working regression floor it was before this phase.

### 5. Delta table against `## Before (pre-edit)`

| Metric | Before (136-01, pre-edit) | After (136-04, post-edit) | Delta |
|---|---|---|---|
| mypy errors | 33 | 33 | **0** — unchanged across the whole phase |
| mypy watermark | 35 | 35 | 0 (not touched — out of scope this phase, confirmed via `pyproject.toml`) |
| mypy headroom | 2 | 2 | **0 remaining headroom spent** — flat, not "similar" |
| `checked` source files | 126 | 130 | **+4** (the four new test files, §6) — `MIN_CHECKED_SOURCE_FILES = 120` is a FLOOR, so this moves the margin from 6 above the floor to **10 above the floor**, never a spend |
| test count (`pytest tests/`) | 1437 passed | 1494 passed | **+57** |
| test failures | 0 | 0 | 0 — full suite green at close, not the 2 deferred reds this plan's Task 1 discharged |
| coverage | 82.12% | 82.14% | **+0.02 pp** |
| snapshot count | 30 | 30 | 0 |
| `tests/*.py` file count | 91 | 95 | **+4** |
| ruff-formatted file count | 120 | 124 | +4 (same four files) |

**New test files this phase added (4):** `tests/test_click_group_gate_hook.py` and
`tests/test_dev_tools_channel_gate.py` (plan `136-01`); `tests/test_dev_group_channel_gating.py`
and `tests/test_dev_gate_reads_no_firmware_source.py` (plan `136-03`). Zero test files were deleted
or renamed.

**New/changed production files this phase touched (2):** `firestarter/channel.py` (new module,
plan `136-01` — `BETA_ONLY_DEV_COMMANDS`, `is_prerelease_build`, `dev_tools_enabled_by_env`,
`is_dev_tools_enabled`, `dev_command_gate_message`) and `firestarter/cli_handlers.py` (plan `136-02`
— `_DevGroup(click.Group)`, `_DEV_TOOLS_ENABLED` module constant, six `@dev.command` blocks
re-indented under `if _DEV_TOOLS_ENABLED:` guards, the CHAN-06 tripwire comment, and the rewritten
`dev()` docstring). `git diff --stat 2b7a702..b1d8f73 -- firestarter/ tests/` (phase-entry HEAD to
this plan's final commit): 7 files changed, 1443 insertions(+), 458 deletions(-) — the large
insertion/deletion pair in `cli_handlers.py` is the six gated blocks' four-space re-indentation
under their new guard, not 1000+ new lines of logic.

**mypy count did not move across this entire phase (33 → 33) despite two production files touched
and +4 test files** — every new symbol landed fully annotated. **The mypy headroom this phase was
budgeted to spend (2, per this document's own `## Before` section) was never spent at all** — the
same flat-headroom outcome Phase 134 recorded, not a discrepancy requiring reconciliation.

### 6. Cross-repo commit note

This `## After` section (like the `## Before` section) is committed in the **meta repo**
(`/workspaces`, branch `gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). It makes **no**
edit inside the `firestarter_app` submodule — every command above only reads and runs the
submodule's existing tooling. `firestarter` (firmware) remains untouched throughout this phase, per
§`git status --porcelain -- firestarter` at the top of this section.

No `git push`, `git merge`, `git tag`, `gh workflow run`, `gh release`, or `twine upload` was run to
produce any measurement in this section. No new pip/npm/cargo package was installed at any point in
this phase.
