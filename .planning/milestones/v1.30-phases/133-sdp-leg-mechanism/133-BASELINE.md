# 133-BASELINE: The pre-edit half of the CI-parity recipe (plan 133-01, Task 3)

**Owner requirement (evidence foundation for):** LEG-11 (this plan does not tick any requirement —
see 133-01-PLAN.md `<requirement_fence>`; plan 133-07 is the only plan permitted to tick).

This baseline is recorded **before any edit to `firestarter/chip_test.py` or any other production
file in this phase** — it is the pre-edit measurement ROADMAP criterion 4 ("the seven shipped ops
are provably behaviourally unchanged") needs, alongside `tests/test_chip_test_sdp_leg.py`'s two
in-code before-images committed in this same plan (`_SHIPPED_OPS_SEQUENCE`,
`_PRE_EDIT_PRECEDENCE_MATRIX`).

`git -C /workspaces/firestarter_app rev-parse --short HEAD`: `7f62cf5`
`git -C /workspaces/firestarter_app branch --show-current`: `gsd/v1.30-sdp-surface-retirement`

(This HEAD is plan 133-01's own second task commit — `test(133-01): add three-constant
exception-precedence triple with non-vacuity leg`. The measurements below were taken against this
exact commit, with `tests/test_chip_test_sdp_leg.py` on disk and zero production files touched:
`git -C /workspaces/firestarter_app diff --stat HEAD -- firestarter/ tools/` produces no output.)

## 1. No-board condition (ambient, not a discrete recipe leg)

```
$ ls /dev/ttyACM* /dev/ttyUSB*
ls: cannot access '/dev/ttyACM*': No such file or directory
ls: cannot access '/dev/ttyUSB*': No such file or directory
```

**No board was attached** when every command below ran. This is the correct pre-condition: a live
board beats the `comports=[]` patch and would turn the `test_no_programmer_found_*`
characterization tests RED (this project's own recorded false-green trap).

**On the ROADMAP's cross-cutting instruction to "run the CI-parity recipe with the no-board leg
emphasized":** `tools/ci_parity.sh` has **no discrete no-board leg** — read the script directly (its
own header names the board dimension as "ambient condition of legs 1 and 2," not a fifth leg, and
its only board-related output is a non-gating `BOARD-ATTACHED:` stamp in the summary, never a
pass/fail leg). The instruction **cannot be followed literally**; it is discharged here as: legs 1
and 2 below were run in the no-board condition, and that condition was asserted (above) and stamped
by the script itself (`BOARD-ATTACHED: none`, §2).

## 2. `bash tools/ci_parity.sh` — aggregate result and per-leg detail

```
$ cd /workspaces/firestarter_app && bash tools/ci_parity.sh
...
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

- **Leg 1** (`FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q`, the standalone-CI shape
  with the firmware sibling absent): **exit 0**. 51 tests skipped with the expected
  `firestarter firmware checkout absent (no .../.git marker)` reason across the parity/gen-header/
  dispatch-mirror modules — this is the same-shape skip this recipe leg exists to exercise, not a
  new finding.
- **Leg 2** (`python3 -m pytest tests/ -q`, firmware sibling present — this devcontainer's own
  layout): **exit 0**. 1301 passed, 30 snapshots passed (see §3 for the exact collected/passed
  count and its accounting against the phase's pre-edit baseline).
- **Leg 3** (`ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/`, at
  `ci.yml`'s exact path set): **exit 0** — "All checks passed!" / "118 files already formatted".
- **Leg 4** (`python3 tools/check_mypy_watermark.py`): **exit 2**, **expected locally** per this
  script's own header and `131-CI-PARITY.md`. Verbatim:
  ```
  ERROR: mypy exited 2, which is neither the clean-run (0) nor errors-found (1) exit code. Treating
  as a tool/config failure, not a clean tree.
  /usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only
  supported in Python 3.12 and greater  [syntax]
  Found 1 error in 1 file (errors prevented further checking)
  Leg 4 exit code: 2
  ```
  This is the ambient devcontainer numpy PEP-695-stub truncation the hardened watermark gate
  (GATE-01..04) correctly refuses to report a count for — not a defect in this plan's change, and
  not a signal about `chip_test.py` or the new test module. §4 below runs the numpy-free replica
  venv, which is the only local path to a **trustworthy** mypy count.

**Aggregate `CI-PARITY: FAIL (legs:4)` is the expected local shape** (per `tools/ci_parity.sh`'s own
header and `131-CI-PARITY.md`) — acceptance does not require a zero aggregate exit locally; leg 4's
exit 2 is discharged by the replica-venv run in §4.

## 3. `python3 -m pytest tests/ -q` — collected/passed count

Read off leg 2 of §2 (identical invocation) and cross-checked against the replica-venv run in §4:
**1301 passed**, **30 snapshots passed**, zero failures. Test-file count: `ls tests/*.py | wc -l` =
**88** (87 pre-existing + this plan's new `tests/test_chip_test_sdp_leg.py`).

Cross-reference to the phase's own pre-edit note (`133-01-PLAN.md` `<verification>`): "measured
pre-edit baseline: 1297 tests / 88 test files / 30 syrupy snapshots." **1301 = 1297 + 4** — the
exact four tests this plan's two commits added
(`test_shipped_ops_sequence_unchanged`, `test_exception_precedence_matrix`,
`test_precedence_matrix_delta_is_exactly_intended`, `test_precedence_matrix_deriver_is_non_vacuous`).
The 88-file count was already the state 133-01-PLAN.md's own note anticipated (it already accounted
for this plan's one new file), so it is unchanged here, not re-measured upward.

## 4. `bash tools/ci_replica_venv.sh` — REAL mypy count (research assumption A1, measured)

```
$ cd /workspaces/firestarter_app && bash tools/ci_replica_venv.sh
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
...
Leg 4: mypy watermark gate
Found 32 errors in 12 files (checked 123 source files)
checked 123 source files
mypy errors: 32 (watermark: 35)
INFO: 32 errors -- 3 below watermark (35). ...
Leg 4 exit code: 0
...
Leg 5: pytest --cov, CI's exact args
... 1301 passed in 156.10s (0:02:36)
Required test coverage of 70% reached. Total coverage: 81.76%
Leg 5 exit code: 0
=================================
CI-REPLICA SUMMARY
=================================
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
MYPY-VERSION: mypy 2.3.0 (compiled: yes)
NUMPY-PRESENT: no
Leg 1 (venv create-or-reuse + install): exit 0
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Leg 4 (mypy watermark gate):             exit 0
Leg 5 (pytest --cov, CI's exact args):   exit 0
CI-REPLICA: PASS
```

**Real, in-range mypy count: 32 errors (watermark 35), checked 123 source files.** Both bounds hold:
`32 <= 35` and `123 >= 120` (`MIN_CHECKED_SOURCE_FILES`).

**Research assumption A1 ("a new plain test module contributes 0 mypy errors") is CONFIRMED, not
inherited:** `132-CI-GREEN.md` §4 recorded the certifying pre-133 CI run at **`mypy errors: 32
(watermark: 35)`, `checked 122 source files`**. This session's measurement, taken with
`tests/test_chip_test_sdp_leg.py` already on disk, is **`mypy errors: 32`** (unchanged) and
**`checked 123`** (122 + 1, exactly this plan's one new file). A1 held exactly: zero new mypy
errors, and the checked-file count moved by precisely the file count this plan added.

`pytest --cov` (leg 5, CI's exact coverage invocation): **1301 passed**, coverage **81.76%** against
the 70% floor — matches §3's plain-`pytest` count exactly, confirming the same suite under both
invocations.

## 5. Phase file-count accounting (`MIN_CHECKED_SOURCE_FILES` margin)

Measured floor: `MIN_CHECKED_SOURCE_FILES = 120` (`tools/check_mypy_watermark.py`, unedited —
`git -C /workspaces/firestarter_app diff --stat HEAD -- pyproject.toml tools/check_mypy_watermark.py`
produces no output). Measured `checked` count with this plan's one new file already on disk: **123**
— a margin of **3** above the floor (`123 - 120`).

**`tests/test_op_registration_parity.py` (plan 133-06) is the second and last new source file this
phase may add** (133-CONTEXT.md D-15): after it lands, `checked` is expected at 124 (123 + 1),
still comfortably above the 120 floor. **No third new source file may be added anywhere in this
phase** — 133-01-PLAN.md Task 1's own scope discipline states this explicitly, and this baseline
confirms the measured margin does not invite adding a third one either.

Neither `pyproject.toml`'s watermark comment (`35`) nor `MIN_CHECKED_SOURCE_FILES` (`120`) is
edited by this plan — both are out of scope per the plan's own acceptance criteria, and both are
confirmed byte-unchanged above.

## 6. Before-image values, reproduced verbatim outside the test file

Copied from `tests/test_chip_test_sdp_leg.py` at commit `7f62cf5` so this before-image survives
independently of a later refactor of that test module.

### `_SHIPPED_OPS_SEQUENCE` (criterion 4, D-13a — `derive_plan("M8720", _REAL_DB)` +
`run_plan(plan, _mock_operator(), _REAL_DB)`, default `write_scope="none"`)

```python
_SHIPPED_OPS_SEQUENCE = {
    "op_sequence": ["id", "read", "blank-check"],
    "verdict_run_count": [("NA", 0), ("OK", 2), ("OK", 1)],
    "len_results": 3,
}
```

("id" is NA/run_count=0 because "M8720"'s chip-id sentinel in the DB entry is 0 — no real id to
compare — so `derive_plan` marks the id step unsupported. write/verify/erase are structurally
omitted from `Plan.steps` under `write_scope="none"` (D-01, SAFE-01) and recorded instead on
`Plan.locked_destructive` — this literal covers only the three steps that actually execute; D-13b's
sentinel test (plan 133-03) covers the remaining shipped op strings via the fail-closed dispatch-arm
proof, not this literal.)

### `_PRE_EDIT_PRECEDENCE_MATRIX` (criterion 4, D-08 — FROZEN forever, nine exception classes'
measured `(escaped, verdict, error_code)` triple, derived by injecting each exception into
`check_eprom_blank` via a real `run_plan()` call)

```python
_PRE_EDIT_PRECEDENCE_MATRIX = {
    "SerialError": ("SerialError", None, None),
    "SerialTimeoutError": ("SerialTimeoutError", None, None),
    "ProgrammerNotFoundError": ("ProgrammerNotFoundError", None, None),
    "FirmwareOutdatedError": ("FirmwareOutdatedError", None, None),
    "EpromOperationError": (None, "BAD", 0x42),
    "ChipNotImplementedError": (None, "BAD", None),
    "ChipNotFoundError": (None, "SKIPPED", None),
    "HardwareOperationError": ("HardwareOperationError", None, None),
    "AssertionError": ("AssertionError", None, None),
}
```

**The measured finding (133-CONTEXT.md D-08's latent case, confirmed by this run):**
`ChipNotImplementedError` is a **subclass** of `EpromOperationError`, so at this commit it matches
`_run_step`'s **first** except clause (`except EpromOperationError`) — Python matches the first
satisfying class — and lands on **BAD** (`error_code=None`), never reaching the narrower second
clause's (`except (ChipNotImplementedError, ChipNotFoundError)`) SKIPPED mapping. That second
clause is, in practice, live only for `ChipNotFoundError` today (a direct `Exception` sibling, not
an `EpromOperationError` subclass). The measurement wins over the "should be SKIPPED" reading — this
row records what the shipped code actually does, not what would be tidier. `SerialError` and its
three subclasses, plus `HardwareOperationError` and `AssertionError`, all escape `run_plan` entirely
today (none is a subclass of `EpromOperationError`, `ChipNotImplementedError`, or
`ChipNotFoundError`).

`_EXPECTED_PRECEDENCE_MATRIX` is byte-identical to `_PRE_EDIT_PRECEDENCE_MATRIX` at this commit, and
`_INTENDED_PRECEDENCE_DELTA` is the empty `frozenset()` — both verified live by
`test_precedence_matrix_delta_is_exactly_intended`.

## 7. Mutation-proof summary (both gates seen to fail, then pass on revert)

Both proofs performed live during Task 1/Task 2 of this plan (see 133-01-SUMMARY.md for the full
observed failure text of each):

- Mutating `_SHIPPED_OPS_SEQUENCE["op_sequence"]` to append a phantom op made
  `test_shipped_ops_sequence_unchanged` FAIL with an `AssertionError` naming the exact diverging
  list; reverting made it pass again.
- Adding one name to `_INTENDED_PRECEDENCE_DELTA` (both matrices left unchanged) made
  `test_precedence_matrix_delta_is_exactly_intended` FAIL with an `AssertionError` naming the
  false-positive computed delta; reverting made it pass again.

## 8. Cross-repo commit note

`133-BASELINE.md` (this document) is committed in the **meta repo** (`/workspaces`, branch
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). Tasks 1 and 2's code changes are
committed inside the **`firestarter_app` submodule** (branch `gsd/v1.30-sdp-surface-retirement`,
commits `b191952` and `7f62cf5`). The two halves cannot share a commit — two git repos cannot share
a commit — so this document cross-cites the submodule commits by hash rather than assuming a shared
SHA.
