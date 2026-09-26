---
phase: 123-non-regression-baselines-gate-hardening
plan: 05
subsystem: testing
tags: [gate-hardening, coarse-key-arming, python-checker, pytest, firmware, py32f071]

requires:
  - phase: 123-non-regression-baselines-gate-hardening (Plan 04)
    provides: check_cmake_manifest.py's D-07 coarse-key-arming idiom (structural template), the shared tests/fixtures/clean_unarmed_tree/ fixture, the 33-passed baseline
provides:
  - "firestarter/scripts/check_orphan_provisional.py — BASE-05 gate: every RURP_*_PROVISIONAL flag must have ≥1 consumer outside its own definition"
  - "firestarter/tests/test_check_orphan_provisional.py — 8 subprocess-invoked anti-hollow tests"
  - "firestarter/tests/fixtures/planted_orphan_provisional_macro/ and clean_orphan_provisional_consumed/ — the discriminating fixture pair"
affects: [Phase 124 MERGE-04 (provisional-pinmap refusal wiring), 123-06 (convention meta-test glob floor), 123-11 (requirement closure)]

tech-stack:
  added: []
  patterns:
    - "Coarse-key arming (D-07) applied a second time, structurally mirroring check_cmake_manifest.py so the two D-07 gates read as one pattern"
    - "Comment-stripped consumer scan (new to this checker): #undef and comment-only mentions are both excluded from the consumer count, treated as one defect class per threat T-123-05-01"

key-files:
  created:
    - firestarter/scripts/check_orphan_provisional.py
    - firestarter/tests/test_check_orphan_provisional.py
    - firestarter/tests/fixtures/planted_orphan_provisional_macro/README.md
    - firestarter/tests/fixtures/planted_orphan_provisional_macro/include/fixture_provisional.h
    - firestarter/tests/fixtures/planted_orphan_provisional_macro/src/fixture_consumer.cpp
    - firestarter/tests/fixtures/planted_orphan_provisional_macro/platform/py32f071/CMakeLists.txt
    - firestarter/tests/fixtures/clean_orphan_provisional_consumed/README.md
    - firestarter/tests/fixtures/clean_orphan_provisional_consumed/include/fixture_provisional.h
    - firestarter/tests/fixtures/clean_orphan_provisional_consumed/src/fixture_consumer.cpp
    - firestarter/tests/fixtures/clean_orphan_provisional_consumed/platform/py32f071/CMakeLists.txt
  modified: []

key-decisions:
  - "Reading (a) from 123-RESEARCH.md's BASE-05 section: the gate follows D-07 literally (UNARMED until platform/py32f071/ exists), with the rejected always-armed reading (b) recorded in the docstring — consistent with check_cmake_manifest.py and avoiding a special case for D-08's never-vacuous rule"
  - "Comment mentions do NOT count as consumers, matching threat T-123-05-01's framing that a loose comment-match is the same defect class as counting an #undef — implemented via a comment-stripping pass (newlines preserved for line-number fidelity) before the consumer regex runs"
  - "The sibling RURP_PY32F071_PINMAP_CONFIGURED structurally-dead #error is explicitly recorded as MERGE-04's scope, not this gate's — the checker's docstring states this so a future reader does not widen the match pattern to try to catch it"

requirements-completed: []

coverage:
  - id: D1
    description: "check_orphan_provisional.py: repo-wide RURP_*_PROVISIONAL definition scan across include/, src/, platform/, test/, with consumer search excluding the defining line, any #undef, and comment-only mentions; D-07 coarse-key arming on platform/py32f071/; never-vacuous guard for armed-with-zero-definitions"
    requirement: BASE-05
    verification:
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_unarmed_on_the_real_tree_with_no_seam_override"
        status: pass
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_orphan_fails_with_exactly_one_violation"
        status: pass
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_consumed_control_passes"
        status: pass
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_undef_is_not_a_consumer"
        status: pass
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_comment_mention_is_not_a_consumer"
        status: pass
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_armed_with_zero_definitions_fails"
        status: pass
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_real_world_define_spelling_matches_pattern"
        status: pass
    human_judgment: false
  - id: D2
    description: "Two committed fixture trees (planted_orphan_provisional_macro/, clean_orphan_provisional_consumed/) proving the gate is discriminating, not universally failing, per BASE-08's anti-hollow requirement"
    requirement: BASE-08
    verification:
      - kind: unit
        ref: "tests/test_check_orphan_provisional.py::test_unarmed_on_clean_unarmed_tree_fixture"
        status: pass
      - kind: other
        ref: "python3 -m pytest tests/ -q -> 41 passed, 0 skipped"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-07-31
status: complete
---

# Phase 123 Plan 05: BASE-05 Orphan-Provisional-Macro Gate Summary

**`check_orphan_provisional.py` scans the whole firmware repo for `RURP_*_PROVISIONAL` flags with zero consumers, ships UNARMED (exit 0) on today's tree, and is proven — via a planted fixture with both an orphaned and a consumed macro — to fire on a real, non-planted defect the moment Phase 124 lands the py32f071 port unchanged.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-07-31T01:17Z (approx)
- **Completed:** 2026-07-31T01:39Z
- **Tasks:** 2
- **Files modified:** 10 (1 modified across both tasks, 9 net-new)

## Accomplishments

- `scripts/check_orphan_provisional.py`: repo-wide definition scan (`include/`, `src/`, `platform/`, `test/`) for `RURP_[A-Z0-9_]*_PROVISIONAL` macros, with a consumer search that excludes the defining line, any `#undef`, and any comment-only mention
- D-07 coarse-key arming on `platform/py32f071/`, structurally mirroring `check_cmake_manifest.py` (123-04) so the two gates read as one pattern
- Never-vacuous guard: an armed tree with zero `_PROVISIONAL` definitions found is a documented failure, not a pass — the design decision that rules out the rejected always-armed reading
- Two fixture trees proving both directions: `planted_orphan_provisional_macro/` (one orphaned macro + one consumed macro in the same tree, exactly 1 violation expected) and `clean_orphan_provisional_consumed/` (the discriminating control, exit 0)
- 8 subprocess-invoked pytest cases in `tests/test_check_orphan_provisional.py`, including the two decisive negative controls (`#undef` is not a consumer; a comment mention is not a consumer) and the literal real-world define-spelling pin
- Firmware pytest suite: **41 passed, 0 skipped** (33 baseline + 8 new)

## Task Commits

1. **Task 1: Write scripts/check_orphan_provisional.py** — `1af0072` (feat)
2. **Task 2: Build the two fixture trees and write tests/test_check_orphan_provisional.py** — `b916f1c` (test; also carries the Task-1 bugfix below)

**Plan metadata:** (this commit, docs)

## Files Created/Modified

- `firestarter/scripts/check_orphan_provisional.py` — the BASE-05 gate
- `firestarter/tests/test_check_orphan_provisional.py` — 8-test anti-hollow pytest
- `firestarter/tests/fixtures/planted_orphan_provisional_macro/{README.md,include/fixture_provisional.h,src/fixture_consumer.cpp,platform/py32f071/CMakeLists.txt}`
- `firestarter/tests/fixtures/clean_orphan_provisional_consumed/{README.md,include/fixture_provisional.h,src/fixture_consumer.cpp,platform/py32f071/CMakeLists.txt}`

## Decisions Made

- **Arming reading (a) chosen over (b), per 123-RESEARCH.md's explicit discussion:** the gate is UNARMED until `platform/py32f071/` exists, matching D-07 literally. The rejected reading (always-armed, "0 found = pass") is recorded in the docstring — it would collide with D-08's never-vacuous requirement and need a special case.
- **Comment mentions do not count as consumers.** The plan's Task 2 read_first pointed at the threat model, and T-123-05-01 explicitly bundles "a consumer rule loose enough to count an `#undef` **or a comment**" as one high-severity defect class. The checker strips `//` and `/* */` comments (preserving newlines for line-number fidelity) before running the consumer regex, so a bare comment naming the macro is not sufficient.
- **`RURP_PY32F071_PINMAP_CONFIGURED`'s structurally-dead `#error` is out of this gate's scope.** The docstring states explicitly that widening the match pattern to also catch `_CONFIGURED` would conflate two different defect classes (an orphan-flag lint vs. a dead compile-time guard) and is MERGE-04's problem to fix, not this gate's to detect.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `DEFINE_RE`/`UNDEF_RE`'s `^\s*#...` pattern could anchor one line early under `re.MULTILINE`**
- **Found during:** Task 2, while exercising Task 1's checker against the newly-built `planted_orphan_provisional_macro/` fixture — the orphaned macro was incorrectly reported as having 1 consumer.
- **Issue:** `\s` matches a literal newline. With `re.MULTILINE`, `^\s*#\s*define...` could anchor its match at the start of a *preceding blank line* and let `\s*` consume that line's newline before reaching the actual `#define` text — reporting the definition one line earlier than the real line, and (critically) defeating `find_consumers()`'s same-line `(path, line)` exclusion, since the excluded line no longer matched the line the consumer scan actually hit.
- **Fix:** Changed both `DEFINE_RE` and `UNDEF_RE` from `^\s*#\s*...` to `^[ \t]*#[ \t]*...` (horizontal whitespace only), which cannot cross a newline boundary.
- **Files modified:** `firestarter/scripts/check_orphan_provisional.py`
- **Verification:** Manually re-ran the planted fixture before and after — after the fix, `RURP_FIXTURE_ORPHAN_PROVISIONAL` correctly reports 0 consumers (1 violation) and `RURP_FIXTURE_CONSUMED_PROVISIONAL` correctly reports its real consumer. All 8 new tests and the full 41-test suite pass.
- **Committed in:** `b916f1c` (bundled with the Task 2 commit, since the bug was found while building Task 2's fixtures and fixing it was a precondition for Task 2's tests to be meaningful)

**2. [Rule 1 - Bug/spec clarification] Consumer search initially counted comment-only mentions as consumers**
- **Found during:** Task 2, while designing test 6 ("a comment mention is not a consumer") and re-reading the threat model.
- **Issue:** The first draft of `find_consumers()` matched the bare identifier anywhere in the file text, including inside `//` and `/* */` comments — which the plan's threat model (T-123-05-01) explicitly classes as the same defect as counting a bare `#undef`.
- **Fix:** Added `_strip_comments()` (regex-based, newline-preserving) applied to the scan text before the consumer regex runs, so a comment-only mention no longer counts.
- **Files modified:** `firestarter/scripts/check_orphan_provisional.py`
- **Verification:** `test_comment_mention_is_not_a_consumer` (new) passes; manually verified against a `tmp_path` copy with the sole consumer replaced by a comment.
- **Committed in:** `b916f1c`

---

**Total deviations:** 2 auto-fixed (both Rule 1 — bugs found and fixed before Task 1's commit's behavior was ever relied upon by Task 2's tests).
**Impact on plan:** Both fixes are corrections to Task 1's own acceptance criteria (a discriminating, non-vacuous gate) discovered during Task 2's fixture-building; no scope creep, no architectural change.

## Known Stubs

None. All fixture source files are explicitly marked (in-file header comments) as fixture input, not real firmware source, per the plan's own instruction.

## Threat Flags

None. No new network endpoints, auth paths, or trust-boundary schema changes were introduced — this plan adds a text-scanning CI gate over the existing firmware repo, matching the threat model's own scoped register (T-123-05-01 through T-123-05-05, all addressed above or by construction).

## Requirement Ticking

**None.** Per the plan's explicit instruction, BASE-05 and BASE-08 are NOT ticked by this plan — they close only in 123-11.

## Restatement for Phase 124's planner

On the py32 branch (`agent/py32f071-toolchain`), `include/boards/py32f071_rurp_shield.h` defines `RURP_PY32F071_PINMAP_PROVISIONAL` at line 38 with **exactly one repo-wide hit — its own definition**. Landed unchanged, this gate fires immediately with a real violation (not a planted one), forcing MERGE-04 to actually wire the provisional-pinmap refusal rather than leave it decorative. The sibling `RURP_PY32F071_PINMAP_CONFIGURED` — `#define`d `1` at line 37 and tested with `#if !RURP_PY32F071_PINMAP_CONFIGURED -> #error` at lines 71-73 of the SAME header, making that `#error` structurally dead — is explicitly **not** this gate's concern; it is MERGE-04's problem.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/scripts/check_orphan_provisional.py`
- FOUND: `/workspaces/firestarter/tests/test_check_orphan_provisional.py`
- FOUND: `/workspaces/firestarter/tests/fixtures/planted_orphan_provisional_macro/README.md`
- FOUND: `/workspaces/firestarter/tests/fixtures/clean_orphan_provisional_consumed/README.md`
- FOUND commit `1af0072` (firestarter, Task 1)
- FOUND commit `b916f1c` (firestarter, Task 2 + bugfix)
- Verified: `python3 -m pytest tests/ -q` → 41 passed, 0 skipped
- Verified: real tree still prints `UNARMED:` naming `platform/py32f071` and exits 0
- Verified: planted fixture → `FAIL: 1 violation(s)` naming `RURP_FIXTURE_ORPHAN_PROVISIONAL` only
- Verified: clean fixture → `PASS:` naming `RURP_FIXTURE_CONSUMED_PROVISIONAL`
- Verified: `git -C /workspaces/firestarter_py32_ci status --porcelain` unchanged (empty)
- Verified: cumulative no-firmware-code-moves check (`$FORK`..HEAD over `src include platformio.ini .github test`) is empty; `merge-base --is-ancestor` confirms `5c9160a3` is an ancestor of HEAD
- Verified: meta repo HEAD branch unaffected by this plan (firmware-only plan); firestarter submodule on `v1.23-py32f071-integration`
