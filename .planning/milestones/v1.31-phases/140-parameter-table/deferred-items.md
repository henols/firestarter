# Phase 140 — Deferred Items

Out-of-scope discoveries logged per the executor's SCOPE BOUNDARY rule: found during a plan's
verification pass, confirmed pre-existing and unrelated to that plan's own changes, not fixed here.

## 140-03: `check_mypy_watermark.py` cannot complete in this devcontainer (pre-existing, not caused by 140-03)

**Found during:** Plan 140-03 Task 2's overall verification (`python3 tools/check_mypy_watermark.py`).

**Symptom:** `mypy firestarter/ tests/` exits 2 with:
```
/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: Type statement is only supported in Python 3.12 and greater  [syntax]
Found 1 error in 1 file (errors prevented further checking)
```
This is the exact "truncated-run" shape `check_mypy_watermark.py`'s own completion-clause guard
exists to catch (no `(checked N source files)` clause) -- the gate correctly reports it as a
tool/config failure (exit 2), not a silent pass.

**Confirmed pre-existing, not caused by this plan:** both new files
(`tests/test_chip_database_field_inventory.py`,
`tests/golden/chip_database_field_inventory.json`) were moved out of `tests/` entirely and the
watermark script re-run -- the identical error reproduced byte-for-byte. Neither file imports
`numpy` or anything that could plausibly import it (stdlib `ast`/`json`/`os`/`collections`/`pathlib`/
`typing` only). `mypy tests/test_chip_database_field_inventory.py` run in isolation is clean
("Success: no issues found in 1 source file"), and `mypy firestarter/` alone (no `tests/`) produces
a normal, parseable completion clause (19 pre-existing errors in 5 files, checked 29 source files;
none in this plan's files). The failure is scoped specifically to `mypy tests/` as a whole.

**Root cause, already known and documented before this plan (not a new finding):**
`tests/test_check_mypy_watermark.py:90-98` carries this exact canned fixture, dated 2026-08-03,
predating Phase 140 entirely:
```
# Measured live in this devcontainer, 2026-08-03: `python3 -m mypy firestarter/
# tests/` truncates on an ambient numpy PEP-695 stub, mypy itself exits 2, and
# the output carries NO `(checked N source files)` clause -- the exact
# truncated-run shape GATE-02's completion-clause requirement exists to catch.
TRUNCATED_OUTPUT = (
    "/usr/local/lib/python3.12/site-packages/numpy/__init__.pyi:737: error: "
    "Type statement is only supported in Python 3.12 and greater  [syntax]\n"
    "Found 1 error in 1 file (errors prevented further checking)\n"
)
```
The devcontainer's ambient `numpy` (2.5.1, installed as some other package's transitive dependency
-- not a direct dependency of `firestarter_app` or of any file this plan touches) ships a
PEP 695 (`type X = ...`) stub, and this project's mypy config pins `python_version = "3.10"`
(pyproject.toml, itself a deliberate GATE-05 correction, comment dated Phase 131). CI's pinned
Python versions (3.9/3.11 per `firestarter_app/CLAUDE.md`) evidently do not hit this, or hit a
different numpy version -- this is a devcontainer-local condition, already named as such by a prior
phase's test fixture.

**Why not fixed here:** out of scope per the SCOPE BOUNDARY rule -- pinning/patching an ambient
transitive dependency to work around a documented, pre-existing devcontainer quirk is unrelated to
TABLE-05's database-field-inventory gate and is not "directly caused by this task's changes."

**Substitute evidence recorded in 140-03-SUMMARY.md instead:** the new module verified individually
mypy-clean (`python3 -m mypy tests/test_chip_database_field_inventory.py` -> "Success: no issues
found in 1 source file"), `ruff check` / `ruff format --check` clean, and the full app suite green
(1547 passed).

**Owner:** unassigned (inherited devcontainer condition, first documented 2026-08-03 per
`test_check_mypy_watermark.py`).
