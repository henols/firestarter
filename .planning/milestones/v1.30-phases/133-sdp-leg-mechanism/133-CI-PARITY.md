# 133-CI-PARITY: The after-half of the CI-parity recipe (plan 133-07, Task 1)

**Owner requirements (evidence foundation for):** LEG-09, LEG-10, LEG-11, LEG-15 — this is the
after-half of the recipe `133-BASELINE.md` (plan 133-01) recorded before any production edit. Every
figure below is reported as an explicit delta against that baseline.

**Date:** 2026-08-04
**Repo:** `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`
**HEAD:** `57e8eb5` (plan 133-06's task commit — the phase's final engine + gate source; this
plan (133-07) makes no production or test-module edit, only `.planning/` documents and the
`REQUIREMENTS.md` tick)
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
This is the **pre-existing dirt** already present at the start of this phase (and at the start of
Phase 132 — see `132-RECORD.md`'s "pre-existing-dirt substitution" note), not a leak from any plan
in this phase. `git diff --stat HEAD -- pyproject.toml tools/check_mypy_watermark.py` produces
**no output** — the watermark (`35`) and `MIN_CHECKED_SOURCE_FILES` (`120`) are byte-unchanged.

---

## 1. No-board condition (ambient, not a discrete recipe leg)

```
$ ls /dev/ttyACM* /dev/ttyUSB*
ls: cannot access '/dev/ttyACM*': No such file or directory
ls: cannot access '/dev/ttyUSB*': No such file or directory
```

**No board was attached** for every measurement below — unchanged from `133-BASELINE.md` §1.

**Restating this phase's discharge of the ROADMAP's cross-cutting instruction, verbatim from the
baseline (still true — nothing about `ci_parity.sh`'s leg structure changed across the phase):**
`tools/ci_parity.sh` has **no discrete no-board leg**. The board dimension is an ambient condition
of legs 1 and 2, never a fifth leg with its own pass/fail, and the script's only board-related
output is a non-gating `BOARD-ATTACHED:` stamp in the summary. The ROADMAP's instruction is
discharged as: legs 1 and 2 below ran in the no-board condition, and that condition is asserted
above and stamped by the script itself (`BOARD-ATTACHED: none`, §2). No leg name that does not
exist is claimed here.

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

- **Leg 1** (`FIRESTARTER_FW_ROOT=<empty dir> python3 -m pytest tests/ -q`, standalone-CI shape,
  firmware sibling absent): **exit 0**. Skips include four `test_sdp_table_parity.py` legs under
  the expected `firestarter firmware checkout absent` reason — same shape as `133-BASELINE.md`'s
  leg 1, no new skip reason introduced.
- **Leg 2** (`python3 -m pytest tests/ -q`, firmware sibling present): **exit 0**. **1338 passed**,
  30 snapshots passed (unchanged snapshot count from the baseline's 30).
- **Leg 3** (`ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/`, `ci.yml`'s
  exact CI-scoped path set — **not** `tools/`, see §6 below): **exit 0** — "All checks passed!" /
  "119 files already formatted" (baseline: "118 files already formatted"; +1 file is this phase's
  net one new formatted file across `tests/`, reconciled in §5).
- **Leg 4** (`python3 tools/check_mypy_watermark.py`): **exit 2 — expected locally**, identical
  reason to the baseline and to `131-CI-PARITY.md`: the ambient devcontainer numpy install carries a
  PEP-695 `type` statement in its `.pyi` stub that mypy (running under this same Python 3.12
  interpreter) cannot parse, so the run aborts before completing and prints no `(checked N source
  files)` completion clause. The hardened watermark gate (GATE-01..04) correctly refuses to report a
  count for an incomplete run and exits 2 rather than fabricating a plausible-but-wrong number. This
  is the gate working, not a defect introduced by this phase. §4 below runs the numpy-free replica
  venv, the only local path to a trustworthy count.

**Aggregate `CI-PARITY: FAIL (legs:4)` is the expected local shape**, unchanged from the baseline —
acceptance does not require a zero aggregate exit locally; leg 4's exit 2 is discharged by the
replica-venv run in §4.

## 3. `python3 -m pytest tests/ -q` — collected count and pass line, delta against baseline

```
$ cd /workspaces/firestarter_app && python3 -m pytest tests/ -o addopts="" -q
...
1338 passed in 119.79s (0:01:59)
--------------------------- snapshot report summary ----------------------------
30 snapshots passed.
```

**1338 passed** (30 snapshots passed, unchanged). Test-file count: `ls tests/*.py | wc -l` = **90**
(88 pre-existing at `133-BASELINE.md` + this phase's exactly two new modules,
`tests/test_chip_test_sdp_leg.py` and `tests/test_op_registration_parity.py`).

**Delta against `133-BASELINE.md`'s 1301** (measured at plan 133-01's close): **+37 tests**,
attributed plan-by-plan against each plan's own SUMMARY (each row's suite count is quoted verbatim
from that plan's own SUMMARY, not re-derived; the "new test functions" column names the functions a
plan's SUMMARY says it added — collected-item counts run higher than function counts wherever a
function is `@pytest.mark.parametrize`d, e.g. 133-02's `test_run_fatal_escapes` over two exception
classes, so the two columns are not expected to match arithmetically):

| Plan | Suite count at plan close | Delta | New test functions (per plan's own SUMMARY) |
|---|---|---|---|
| 133-01 (baseline) | 1301 | — | harness + `_SHIPPED_OPS_SEQUENCE` + precedence-triple (4 functions) |
| 133-02 | 1306 | +5 | 4 LEG-11 behavioural proofs (one parametrized ×2 → 5 collected items) |
| 133-03 | 1314 | +8 | 5 dispatch-arm/destructive-set tests, some parametrized |
| 133-04 | 1323 | +9 | 9 tests: 5 LEG-10 behavioural/AST proofs + 2 AST structural proofs + 2 LEG-09 criterion-3 proofs |
| 133-05 | 1331 | +8 | 8 tests in `tests/test_check_devtest_orchestrator.py` (18 → 26) |
| 133-06 | 1338 | +7 | 7 tests in `tests/test_op_registration_parity.py` (the phase's second new file) |

**Net: 1301 → 1338, +37 across six plans, zero regressions at any step** — every plan's SUMMARY
records the full suite green immediately after landing its own tests, with the running total
monotonically increasing (1301 → 1306 → 1314 → 1323 → 1331 → 1338).

## 4. `bash tools/ci_replica_venv.sh` — REAL mypy count (research assumption A1, measured)

```
$ cd /workspaces/firestarter_app && bash tools/ci_replica_venv.sh
INTERPRETER: /home/vscode/.local/bin/python3.11 Python 3.11.15
...
Leg 4: "${VENV_DIR}/bin/python" -c '<check_mypy_watermark.py's own run_mypy + classify_mypy_result + enforce_watermark>'
Found 33 errors in 13 files (checked 124 source files)
checked 124 source files
mypy errors: 33 (watermark: 35)
INFO: 33 errors -- 2 below watermark (35). ...
Leg 4 exit code: 0
...
Leg 5: pytest --cov, CI's exact args
... 1338 passed in 116.82s (0:01:56)
Required test coverage of 70% reached. Total coverage: 81.84%
Leg 5 exit code: 0
=================================
CI-REPLICA SUMMARY
=================================
Leg 1 (venv create-or-reuse + install): exit 0
Leg 2 (numpy absent):                   exit 0
Leg 3 (ruff check + format --check):    exit 0
Leg 4 (mypy watermark gate):             exit 0
Leg 5 (pytest --cov, CI's exact args):   exit 0
CI-REPLICA: PASS
```

**Real, in-range mypy count: 33 errors (watermark 35), checked 124 source files.** Both thresholds
hold: `33 <= 35` and `124 >= 120` (`MIN_CHECKED_SOURCE_FILES`).

**Delta against `133-BASELINE.md`'s 32 errors / 123 checked:** **+1 error, +1 checked file** —
across the whole phase, not just this task. This is **not** a smooth, expected-zero delta, and the
honest accounting matters more than the raw number:

- **`checked` moved 123 → 124**, exactly the phase's second new source file
  (`tests/test_op_registration_parity.py`, plan 133-06) — the file-count accounting in §5 confirms
  this is the only file-count change across the whole phase after 133-01's baseline.
- **The error count moved 32 → 33 at plan 133-06's commit specifically** (confirmed by 133-06's own
  SUMMARY and by `deferred-items.md`), and the honest attribution is **not** "a new plain test module
  contributes 0 mypy errors" holding cleanly. What actually happened, stated plainly:
  `tests/test_op_registration_parity.py` itself contributes **zero** mypy errors directly
  (`mypy ... | grep test_op_registration_parity` is empty both with and without the file, per
  133-06's own verification) — but its import of `tools.check_devtest_orchestrator` (to read
  `_HANDLER_FUNCTION_NAMES`) made mypy type-check that module for the **first time ever**, because
  its only prior consumer (`tests/test_check_devtest_orchestrator.py`) drives it exclusively through
  `subprocess`, never `import`. That first-ever type-check surfaced one **pre-existing** type error
  at `tools/check_devtest_orchestrator.py:442` — `visit_ExceptHandler`'s `label` variable, inferred
  `str` from its first assignment, reassigned `str | None` later in the same function. **This error
  was introduced by plan 133-05's commit `feb90f6`** (confirmed by `git blame` at plan-133-05
  authoring time and restated here), not by 133-06, and not by this plan. It was invisible to every
  gate in the phase up to and including 133-05's own close because nothing mypy followed ever
  imported that module.

  **The honest statement, not softened:** 133-05 shipped a real type error that no gate in this
  phase's own toolchain could see at the time it shipped, because the module's only test coverage
  drives it through a subprocess rather than an import — a blind spot in this phase's own gate
  arrangement, not a "pre-existing" condition in the sense of something inherited from before Phase
  133 began. It is a live example of exactly the class of thing `133-RECORD.md` §4 (Corrections)
  exists to carry rather than smooth over. It remains **2 below** the watermark (`33 <= 35`), so it
  is a record item, not a blocking finding, and the watermark and `MIN_CHECKED_SOURCE_FILES` are both
  confirmed byte-unchanged above.

**Research assumption A1 ("a new plain test module contributes 0 mypy errors") — discharged by
measurement, with its real texture stated rather than assumed:** true for the module's own lines in
both cases (133-01's `test_chip_test_sdp_leg.py` and 133-06's `test_op_registration_parity.py` both
measured to contribute zero direct errors), but **not** true for the module's transitive import
graph in 133-06's case — an import can make mypy reach code it never reached before and surface a
real, pre-existing-in-source-but-never-yet-measured error that belongs to a different file entirely.
A1 is confirmed as measured, not as a clean zero-delta; the +1 is fully attributed above, not left as
an unexplained residual.

`pytest --cov` (leg 5): **1338 passed**, coverage **81.84%** against the 70% floor — matches §3's
plain-pytest count exactly.

## 5. Phase file-count accounting (`MIN_CHECKED_SOURCE_FILES` margin)

Measured floor: `MIN_CHECKED_SOURCE_FILES = 120` (`tools/check_mypy_watermark.py`, confirmed
byte-unchanged above). Measured `checked` count at phase close: **124** — a margin of **4** above
the floor (`124 - 120`).

**Exactly two new source files were added across the whole phase**, confirmed by re-listing:
`tests/test_chip_test_sdp_leg.py` (plan 133-01) and `tests/test_op_registration_parity.py` (plan
133-06) — `ls tests/*.py | wc -l` = 90 = 88 (Phase 132 close) + 2. This spends **both** slots of the
`checked 122 / MIN 120` margin `133-CONTEXT.md` D-15 named at plan time, exactly as budgeted: no
third new source file was added anywhere in the phase (confirmed by each plan's own SUMMARY "Files
Created/Modified" section — 133-02/03/04/05 modified only existing files).

`checked` moved 122 (Phase 132 close) → 123 (133-01, +1 file) → 124 (133-06, +1 file) — precisely
two increments for precisely two new files, with 133-02/03/04/05 each measured to leave `checked`
unchanged (123, confirmed in each plan's own SUMMARY).

## 6. `ruff check`/`ruff format --check` — CI scope vs. phase-wide scope

**CI's actual scope** (`tools/ci_replica_venv.sh` leg 3, and `ci.yml` itself): `ruff check
firestarter/ tests/` + `ruff format --check firestarter/ tests/` — **exit 0**, "All checks passed!" /
clean, confirmed in §2 leg 3 and §4 leg 3 above. `tools/` is **not** in CI's ruff scope.

**Running `ruff check firestarter/ tools/ tests/` (a wider, phase-plan-specified command)** surfaces
4 pre-existing findings in `tools/`, all in files last touched in Phase 63/70, unrelated to this
phase and already logged in `deferred-items.md` (from plan 133-06's own discovery): `I001`
unsorted-import findings in `tools/audit_coverage_matrix.py:37`, `tools/catalog/codegen.py:36`,
`tools/catalog/codegen_vectors.py:32`, and one `UP031` percent-format finding in
`tools/catalog/codegen_vectors.py:189`; `ruff format --check` on the same wider scope also flags
`tools/catalog/codegen.py` and `tools/catalog/codegen_vectors.py` as needing reformatting. **None of
these four findings, nor the two format findings, are introduced by this phase** — reproduced with
`git stash -u` at plan 133-06 (this plan's new file removed), the same findings appear; confirmed
again here that these files are untouched by any of this phase's seven plans (`git diff --stat
HEAD~7 -- tools/audit_coverage_matrix.py tools/catalog/` in the submodule, run below, is empty).

```
$ git -C /workspaces/firestarter_app diff --stat HEAD~7 -- tools/audit_coverage_matrix.py tools/catalog/
```
(no output — confirms these three files are untouched across the whole phase's seven plans)

Not fixed here — out of this plan's scope (only auto-fixes issues caused by the current task's own
changes) and already carried in `deferred-items.md` for a future lint-debt sweep.

## 7. `python3 tools/check_devtest_orchestrator.py` — exit 0, four-counter PASS line

```
$ cd /workspaces/firestarter_app && python3 tools/check_devtest_orchestrator.py; echo "exit=$?"
PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py, ../firestarter/submit.py; 0 VPP-set, 0 raw-wire-dict, 0 --force, 0 broad-except; firmware untouched (host-only, asserted)
exit=0
```

Four counters (`VPP-set`, `raw-wire-dict`, `--force`, `broad-except`) all read **0** against the
phase's real, clean, final engine source — the fourth counter (`broad-except`) is plan 133-05's new
deny bucket, proven GREEN here against `chip_test.py`'s one exempted `_sample` handler (D-14).

## 8. `python3 -m pytest tests/test_skip_census.py -x -q` — no new skip reason introduced

```
$ cd /workspaces/firestarter_app && python3 -m pytest tests/test_skip_census.py -x -q
.....                                                                    [100%]
```

5 passed. `ALLOWED_SKIP_REASONS` fails closed on any new skip reason; none was introduced anywhere
in this phase's seven plans.

## 9. Cross-repo commit note

`133-CI-PARITY.md` (this document) is committed in the **meta repo** (`/workspaces`, branch
`gsd/v1.30-sdp-surface-retirement-behavioral-lock-proof`). It makes **no** edit inside the
`firestarter_app` submodule — every command above only reads and runs the submodule's existing
tooling. `firestarter` (firmware) is untouched throughout: this phase is host-only by design (see
`133-CONTEXT.md`'s phase boundary).

No `git push`, `git merge`, `git tag`, `gh workflow run`, `gh release`, or `twine upload` was run to
produce any measurement in this document.
