---
phase: 119-lock-sdp-enable-command-surface-fw-half
plan: 03
subsystem: host-source-scanning-gates
tags: [firestarter_app, source-scan, gate, anti-hollow, cmd-admission, sdp, at28c]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    plan: "02"
    provides: is_memory_cmd() — the static inline, header-resident, DEV_TOOLS-invariant admission predicate this plan reads and scans, and the two-env truth table that supplies D-04's semantic oracle
provides:
  - "tools/check_is_memory_cmd_no_ifdef.py — a fail-closed, brace-matched source-scan gate reading firestarter/include/firestarter.h's is_memory_cmd() predicate, asserting (a) no preprocessor conditional inside the body and (b) the body's CMD_* set matches the frozen eight-name expected set exactly"
  - "tests/test_check_is_memory_cmd_no_ifdef.py — 6-case paired pytest proving the gate is non-hollow (planted fixture, out-of-body control, comment-not-a-violation control, wrong-command-set case, two fail-closed sub-assertions)"
  - "tests/fixtures/planted_ifdef_in_predicate.h — committed planted-violation fixture, conditional planted inside the predicate body only, command enumeration kept correct"
  - "FIRESTARTER_CMD_ADMISSION_SRC — fail-closed env-override seam"
  - "LOCK-03 Complete — both of D-04's oracles now in place"
affects: [119-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Firmware-source-scanning host gate: brace-matched C++ extraction (own definition pattern, not check_no_log_in_sdp_window.py's void-only _func_def_pattern), length/line-preserving comment stripping, fail-closed FIRESTARTER_*_SRC env seam, PASS:/FAIL:/ERROR: exit-code contract — this is the third such gate in the tree and joins the mandatory CORRECTION-4 cross-repo gate checklist (Plan 119-10 records it)"

key-files:
  created:
    - firestarter_app/tools/check_is_memory_cmd_no_ifdef.py
    - firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py
    - firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h
  modified:
    - .planning/REQUIREMENTS.md (LOCK-03 → Complete, both oracles named; LOCK-01/02/04/05/06 confirmed unchanged at Pending)

key-decisions:
  - "The gate's own definition pattern cannot reuse check_no_log_in_sdp_window.py's _func_def_pattern (hardcodes a literal void return type); is_memory_cmd() returns bool, so a new pattern pins static/inline/bool/name/params/{ with tolerant whitespace"
  - "Preprocessor-conditional deny list checks every kind of conditional (#if/#ifdef/#ifndef/#elif/#else/#endif), not only ones naming DEV_TOOLS — a narrower check would be evadable by conditioning on a different macro"
  - "The frozen expected CMD_* set is a module-level constant, not auto-derived from the header — adding a ninth memory command is a deliberate act that must edit this gate's source"
  - "The planted fixture wraps CMD_SDP_UNLOCK/CMD_SDP_LOCK's case labels in #ifdef DEV_TOOLS/#endif inside the switch body: since the checker scans text (never runs a real preprocessor), all eight CMD_* identifiers remain textually present regardless of the wrapping, isolating assertion (a) from assertion (b) as the plan required"

requirements-completed: [LOCK-03]

coverage:
  - id: D1
    description: "check_is_memory_cmd_no_ifdef.py exits 0 against the real firestarter/include/firestarter.h, printing a PASS: line naming the resolved path and the predicate body's line range"
    requirement: LOCK-03
    verification:
      - kind: unit
        ref: "python3 tools/check_is_memory_cmd_no_ifdef.py — PASS: is_memory_cmd() has no preprocessor conditional and enumerates exactly the eight expected commands (…/firestarter/include/firestarter.h, predicate body lines 109-123), exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "Six-case paired pytest, including the load-bearing committed-fixture case (exit 1, FAIL:, fixture-derived line number) and two out-of-band controls proving position-not-presence discrimination"
    requirement: LOCK-03
    verification:
      - kind: unit
        ref: "pytest tests/test_check_is_memory_cmd_no_ifdef.py -q — 6 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Pre-existing host gate baseline held exactly: 21/21 on the four firmware-scanning pytest modules, check_no_log_in_sdp_window.py and check_dispatch.py both exit 0, firestarter/ untouched"
    verification:
      - kind: unit
        ref: "pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py -q — 21 passed"
        status: pass
      - kind: unit
        ref: "python3 tools/check_no_log_in_sdp_window.py && python3 tools/check_dispatch.py — both exit 0"
        status: pass
      - kind: unit
        ref: "git -C firestarter status --short — clean"
        status: pass
    human_judgment: false
  - id: D4
    description: "ruff check + ruff format --check pass against the py3.9 target on both new Python files"
    verification:
      - kind: unit
        ref: "ruff check tools/check_is_memory_cmd_no_ifdef.py tests/test_check_is_memory_cmd_no_ifdef.py && ruff format --check … — All checks passed, 2 files already formatted (ruff 0.15.20, pyproject.toml target-version = py39)"
        status: pass
    human_judgment: false

duration: ~25min
completed: 2026-07-28
status: complete
---

# Phase 119 Plan 03: is_memory_cmd() No-Conditional Source Gate (LOCK-03 close) Summary

**Shipped D-04's textual oracle — a fail-closed, brace-matched host gate proving `is_memory_cmd()`'s body carries no build-configuration conditional and enumerates exactly the eight expected commands, with a committed planted-violation fixture proving the gate can actually fail — closing LOCK-03 alongside Plan 119-02's semantic two-env truth table.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-28
- **Tasks:** 2/2
- **Files modified:** 4 (3 new host files, 1 planning doc)

## Accomplishments

- Created `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py`: copies `check_no_log_in_sdp_window.py`'s five structural elements (env-overridable path constant, definition-only regex pattern, length/line-preserving comment stripping, fail-closed `ValueError` naming the fix, `main()` PASS:/FAIL:/ERROR: exit-code contract) and nothing else. Its own definition pattern (`static\s+inline\s+bool\s+is_memory_cmd\s*\([^)]*\)\s*\{`) is required because the analog's `_func_def_pattern` hardcodes a literal `void` return type.
- Gate asserts two independent things over the brace-matched predicate body: (a) zero preprocessor conditional lines of any kind (`#if`/`#ifdef`/`#ifndef`/`#elif`/`#else`/`#endif` — not narrowed to `DEV_TOOLS`), and (b) the body's `CMD_*` identifier set, deduplicated, equals the frozen eight-name expected set `{CMD_READ, CMD_WRITE, CMD_ERASE, CMD_BLANK_CHECK, CMD_CHECK_CHIP_ID, CMD_VERIFY, CMD_SDP_UNLOCK, CMD_SDP_LOCK}` exactly, reporting missing/unexpected names separately.
- Verbatim run against the real header: `PASS: is_memory_cmd() has no preprocessor conditional and enumerates exactly the eight expected commands (/workspaces/firestarter_app/tools/../../firestarter/include/firestarter.h, predicate body lines 109-123)`, exit 0.
- Created `tests/fixtures/planted_ifdef_in_predicate.h`: a minimal, standalone, never-compiled header carrying the predicate's shape with `#ifdef DEV_TOOLS` / `#endif` planted **inside** the switch body around the `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` case labels. Since the checker scans text rather than running a real preprocessor, all eight `CMD_*` names remain present regardless of the wrapping — the fixture trips assertion (a) only, never (b), so a single test failure cannot be ambiguous about which check fired. Do-not-fix header comment included, matching `planted_log_in_window.cpp`'s contract.
- Created `tests/test_check_is_memory_cmd_no_ifdef.py` with the required six cases: clean control; the load-bearing committed-fixture case (exit 1 AND `FAIL:` AND `f"line {planted_line}"`, line number derived from the fixture at test time via `_line_number_of_marker`, never hardcoded); out-of-body control (a legitimate conditional around a `CMD_DEV_*`-style pair outside the predicate, mirroring the real header); comment-not-a-violation control (a rationale comment inside the body naming the conditional by name); wrong-command-set case (omits `CMD_VERIFY`, asserts exit 1 and the name in stdout); and one fail-closed case with two sub-assertions (missing path → `ERROR:` on stderr; predicate absent → `ERROR:` on stderr naming the fix).
- `pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` → **6 passed**.
- Re-ran the full pre-existing host gate set at baseline: `pytest tests/test_sdp_table_parity.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_bus_config_drift.py tests/test_revision_constants_parity.py -q` → **21 passed** (unchanged — this plan touches no firmware source); `check_no_log_in_sdp_window.py` and `check_dispatch.py` both exit 0.
- `ruff check` and `ruff format --check` validated against the CI target: `pyproject.toml`'s `[tool.ruff] target-version = "py39"` (ruff 0.15.20 installed). Both new Python files needed one `ruff format` pass each (minor whitespace joins) before `--check` passed clean. Note for the record: the repo's actual `ci.yml` runs only Python 3.11 at the interpreter level (no 3.9 job exists), so `target-version = "py39"` is ruff's lint/pyupgrade target, not a runtime-tested interpreter version — `from __future__ import annotations` was added to both new files defensively so their `X | None` / `tuple[...]` annotations remain safe under an actual 3.9 interpreter regardless.
- `git -C /workspaces/firestarter status --short` confirmed clean before and after both tasks — no firmware file was read-only-scanned-but-modified.
- Marked **LOCK-03 Complete** in `.planning/REQUIREMENTS.md`, with a parenthetical naming both of D-04's oracles (the two-env truth table from Plan 119-02, and this gate with its planted-violation fixture from this plan). Re-read LOCK-01, LOCK-02, LOCK-04, LOCK-05, LOCK-06 — confirmed all five still read Pending; no other requirement row was touched.

## CORRECTION-4 cross-repo gate checklist (for Plan 119-10)

This is a **new firmware-source-scanning host gate** joining the mandatory checklist the milestone has required since Phase 117's four-times-bitten lesson: it reads `firestarter/include/firestarter.h` by name and by brace-matched position, so a firmware rename of `is_memory_cmd()` (or a firmware edit that reintroduces a conditional, or changes the eight-command set) will fail this gate closed even though the firmware suite itself stays green. **Plan 119-10 must add `python3 tools/check_is_memory_cmd_no_ifdef.py` to the 9-row cross-repo gate table** alongside `check_no_log_in_sdp_window.py` and `check_dispatch.py`. Recorded here so Phase 119's later meta plan does not have to rediscover it.

## Task Commits

Each task was committed atomically inside the `firestarter_app/` submodule:

1. **Task 1: Write the fail-closed is_memory_cmd() source-scan gate** — `51b2618` (feat)
2. **Task 2: Ship the planted-violation fixture and the paired pytest, then re-run the full host gate set** — `84ce9fd` (test)

**Plan metadata:** committed alongside this SUMMARY (docs, meta commit, staging the `firestarter_app` gitlink bump).

## Files Created/Modified

- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` — the fail-closed source-scan gate
- `firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py` — 6-case paired pytest
- `firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h` — committed planted-violation fixture
- `.planning/REQUIREMENTS.md` — LOCK-03 → Complete (both oracles named); traceability table row updated; LOCK-01/02/04/05/06 confirmed unchanged

## Decisions Made

See `key-decisions` in frontmatter. All four match the plan's `must_haves.truths`/`prohibitions` verbatim — none required deviation from the plan's explicit instructions.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' acceptance criteria were met without any Rule 1-4 auto-fixes. One clarifying note (not a deviation): the plan's critical constraint #6 states "host CI runs py3.9 and py3.11" — `firestarter_app/.github/workflows/ci.yml` as read during this plan actually configures only a single Python 3.11 job (no 3.9 job exists in CI today). This does not change any action taken: the gate and its test were still written and validated against `pyproject.toml`'s `target-version = "py39"` ruff target, with `from __future__ import annotations` added defensively so the files remain safe under an actual 3.9 interpreter regardless of whether CI currently exercises one. Recorded here as a factual correction, not acted on further (out of this plan's scope to change CI).

## Issues Encountered

None. The same pre-existing untracked/modified `firestarter_app` files noted in 119-02's SUMMARY (`.gitignore` local edit, `.coverage`, `.planning/config.json`, `SECURITY.md`, `doc/lockable-proms.md`, `write_test_port.sh`) remain present and unrelated to this plan's host-only scope — confirmed unchanged by `git status --short` before and after, out of scope per the scope boundary rule.

## User Setup Required

None — no external service configuration required.

## Known Stubs

None. This plan lands a source-scanning gate, its paired test, and a fixture — no UI or data-rendering path is affected.

## Requirement Status

**LOCK-03 is Complete** — the only requirement row this plan changed. Both of D-04's oracles are now in place: the semantic two-env truth table (Plan 119-02) and this plan's textual source-scan gate with its planted-violation fixture. LOCK-01, LOCK-02, LOCK-04, LOCK-05, LOCK-06 all confirmed still Pending (re-read directly from `REQUIREMENTS.md` before and after this plan's edit) — none re-derived or touched.

## Next Phase Readiness

- `check_is_memory_cmd_no_ifdef.py` is ready to be added to Plan 119-10's 9-row cross-repo gate table (CORRECTION-4 item).
- LOCK-03 closed; Plan 119-04 (firmware + host, LOCK-01/LOCK-02/LOCK-05) is next in the strictly-sequential Phase 119 chain, per `depends_on`.
- No blockers for Plan 119-04.

---
*Phase: 119-lock-sdp-enable-command-surface-fw-half*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py`
- FOUND: `firestarter_app/tests/test_check_is_memory_cmd_no_ifdef.py`
- FOUND: `firestarter_app/tests/fixtures/planted_ifdef_in_predicate.h`
- FOUND: `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-03-SUMMARY.md`
- FOUND: `51b2618` (Task 1 commit, firestarter_app submodule)
- FOUND: `84ce9fd` (Task 2 commit, firestarter_app submodule)
- FOUND: `4fb01f3` (meta commit, staging gitlink + REQUIREMENTS.md + SUMMARY.md)
