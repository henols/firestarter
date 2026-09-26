---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
plan: 03
subsystem: testing
tags: [pyproject, syrupy, tomllib, dependency-hygiene, hyg-01, hyg-02]

requires:
  - phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
    provides: "plan 181-01's schema 2.0 + frozen-hash invariance harness (this plan touches neither)"
provides:
  - "syrupy bounded >=5.0,<7 in pyproject.toml's test extra, with the upper-bound justification in the file's own established style"
  - "a stdlib-only test that pins the runtime dependencies list to exactly six names by exact set equality"
affects: [181-08-green-tree-battery, milestone-close]

actuals:
  tokens: 2464
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "pyproject.toml upper-bound justification comments (py32's pyusb<2, test's mypy<3, now test's syrupy<7) -- config comments, not product source, so the no-comments rule does not reach them"
    - "stdlib-only test module: tomllib to parse pyproject.toml, no toml/tomli dependency added to test that no dependency was added"

key-files:
  created:
    - firestarter_app/tests/test_runtime_dependencies.py
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-03-dependency-pins.txt
  modified:
    - firestarter_app/pyproject.toml

key-decisions:
  - "syrupy>=5.0,<7 keeps the installed 6.0.0 satisfied and refuses a future 7.x whose Amber dataclass serialization change would silently re-render the 19 frozen report snapshots"
  - "HYG-02 is asserted by exact SET equality (not subset, not sorted-list) over {click, packaging, pyserial, requests, rich, tqdm}, proven RED in both drift directions plus a separate empty-expected vacuity leg"
  - "the new test module resolves pyproject.toml from its own file's parent's parent, never a directory-relative path, per the project's recorded check_permitted_claims.py _HERE lesson"

requirements-completed: [HYG-01, HYG-02]

coverage:
  - id: D1
    description: "syrupy bounded >=5.0,<7, upper bound justified in the file's own established comment style, boundary measured on both sides"
    requirement: "HYG-01"
    verification:
      - kind: unit
        ref: "packaging.specifiers.SpecifierSet boundary check (evidence section 2)"
        status: pass
      - kind: integration
        ref: "tools/snapshot_report_shapes.py --check (evidence section 3)"
        status: pass
    human_judgment: false
  - id: D2
    description: "runtime dependencies list pinned to exactly six names by exact set equality, using only the standard library"
    requirement: "HYG-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_runtime_dependencies.py#test_runtime_dependency_set_is_exactly_the_six_shipped_distributions"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_runtime_dependencies.py#test_a_planted_seventh_dependency_reddens_the_pin"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_runtime_dependencies.py#test_a_planted_removal_reddens_the_pin"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_runtime_dependencies.py#test_an_empty_expected_set_fails_rather_than_passing_vacuously"
        status: pass
    human_judgment: false

duration: 4min
completed: 2026-09-09
status: complete
---

# Phase 181 Plan 03: Dependency Hygiene Close Summary

**syrupy bounded `>=5.0,<7` against a future Amber-dataclass-serialization break, and the six runtime distributions pinned by exact set equality using only stdlib `tomllib`**

## Performance

- **Duration:** 4 min
- **Started:** 2026-09-09T10:49:22Z
- **Completed:** 2026-09-09T10:52:33Z
- **Tasks:** 2
- **Files modified:** 3 (1 modified, 2 created)

## Accomplishments
- HYG-01 discharged: `pyproject.toml`'s `test` extra now reads `"syrupy>=5.0,<7",`, with a justification comment above it in the same voice as the existing `pyusb>=1.3.1,<2` and `mypy>=2.1.0,<3` pins — naming syrupy 6.0.0's native Amber dataclass serialization, the affected `Plan`/`Step`/`Fingerprint`/report dataclasses, and the raise-and-re-verify protocol. The installed 6.0.0 release satisfies the bound; `7.0.0` does not — both measured with `packaging.specifiers.SpecifierSet`, not asserted by the specifier's shape alone.
- HYG-02 discharged as a **test**, not a claim: `firestarter_app/tests/test_runtime_dependencies.py` parses `pyproject.toml` with stdlib `tomllib` and asserts the `project.dependencies` list reduces to exactly `{click, packaging, pyserial, requests, rich, tqdm}` — set equality, order-insensitive, with an independent length check so a duplicate entry cannot hide behind the set comparison.
- The pin was observed RED against three planted counter-examples, all in-memory: a seventh distribution appended to a copy of the parsed list, one of the six removed from a copy, and a comparison against an empty expected set — each inside `pytest.raises(AssertionError)`. No fixture file was ever written and `pyproject.toml` is never touched by a test.
- `tools/snapshot_report_shapes.py --check` stayed green under the bounded syrupy with nothing reinstalled, and `project.dependencies` parsed byte-unchanged.

## Task Commits

Each task was committed atomically (two commits per task — one in the app submodule for the code, one in the meta repo for the evidence transcript):

1. **Task 1: Bound syrupy `>=5.0,<7`** — `75ce56a` (fix, `firestarter_app`) + `74f9c53d` (docs, meta evidence)
2. **Task 2: HYG-02 as a test** — `ebf4f2b` (test, `firestarter_app`) + `357afaff` (docs, meta evidence)

**Plan metadata:** SUMMARY.md commit follows this file.

## Files Created/Modified
- `firestarter_app/pyproject.toml` — `syrupy>=5.0` → `syrupy>=5.0,<7` in the `test` extra, with an 8-line upper-bound justification comment above it (config, not product source — comments are correct here). `dependencies` (`:46-53`) is byte-unchanged.
- `firestarter_app/tests/test_runtime_dependencies.py` — new module, 4 tests, stdlib `tomllib` + `pytest` only, 0 comment tokens (verified by a `tokenize.COMMENT` census), ruff-clean.
- `.planning/phases/181-.../evidence/181-03-dependency-pins.txt` — the measured boundary on both sides, the snapshot-suite result, the runtime-dependency parse, the three RED observations, and the three porcelain legs, all as flat `key=value` scalars plus verbatim command tails.

## Decisions Made
- **No installer was invoked at any point in this plan.** No `pip install`, no `pip install -e`, no lockfile regeneration — the syrupy bound is a source-only edit and the installed 6.0.0 release already satisfies both the old and the new specifier.
- The upper-bound justification for syrupy was written in `pyproject.toml` as a comment, matching the file's own established style (`pyusb>=1.3.1,<2`, `mypy>=2.1.0,<3`). `pyproject.toml` is TOML config, not product source under `/workspaces/CLAUDE.md`'s comment rule, so this is a deliberate, cited exception rather than a violation.
- Every rationale that would otherwise have been a source comment in the new test module instead lives in a docstring: the module docstring states HYG-02's claim and why `tomllib` (stdlib) is used instead of `toml`/`tomli`; each private helper and each test function carries its own docstring explaining its role in the anti-vacuity triad.
- No line number anchor had moved since the plan was written: `pyproject.toml`'s `dependencies` at `:46-53` and `syrupy>=5.0` at `:73` were both confirmed exact before editing.

## Deviations from Plan

None - plan executed exactly as written.

One incidental, in-scope fix: `ruff check --fix` reordered the two stdlib imports (`pathlib.Path` before `tomllib`) to satisfy isort grouping — a formatting-only change with no content difference, applied before the first commit of the new test module so the committed file was already ruff-clean. Not logged as a Rule 1-4 deviation since it is exactly the auto-fixable formatting the plan's own environment notes anticipate (`ruff format --check` is part of the green-tree battery), not a defect discovered mid-task.

---

**Total deviations:** 0 auto-fixed (the isort reorder above is a pre-commit formatting pass, not a deviation from the plan's instructions).
**Impact on plan:** None — plan executed exactly as specified, both requirements closed by the mechanisms the plan named.

## Issues Encountered

None. A separate `/gsd-debug` session is active in the same checkout (working on `firestarter/serial_comm.py` and `tests/test_probe_spurious_setup_ack.py`, commit `31f3455` and its follow-ups, all predating this plan's base commit `8b3d8f9`). Its scratch file `.planning/debug/beta-probe-empty-input.md` and its `.planning/debug/resolved/` changes were left untouched — only this plan's own files were staged in every commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HYG-01 and HYG-02 are both closed by test/measurement, not by sentence. The two remaining hygiene requirements (HYG-03, HYG-04) and the RPT-A through RPT-F clusters are carried by other plans in this phase.
- All 19 `FROZEN_HASHES` literals in `tests/fixtures/report_shapes.py` were not touched by this plan (it shares no file with the shape fixtures) and remain the responsibility of the plans that do touch them.
- The seven-leg green-tree battery and the app suite floor were deliberately **not** run here per the plan's own instruction — they run once, in `181-08`.
- Firmware submodule (`firestarter/`) stayed porcelain-clean throughout, confirmed by the porcelain legs after both app commits landed.

---
*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Completed: 2026-09-09*

## Self-Check: PASSED

- `firestarter_app/pyproject.toml` — FOUND
- `firestarter_app/tests/test_runtime_dependencies.py` — FOUND
- `.planning/phases/181-.../evidence/181-03-dependency-pins.txt` — FOUND
- `.planning/phases/181-.../181-03-SUMMARY.md` — FOUND
- App commits `75ce56a`, `ebf4f2b` — FOUND in `firestarter_app`
- Meta commits `74f9c53d`, `357afaff`, `97c2c6db` — FOUND in `/workspaces`
- All plan-level `<verification>` legs re-run and passing; all three porcelain legs print nothing.
