---
phase: 129-flash-path-decision-pcb-requirements-record
plan: 01
subsystem: testing
tags: [pytest, cross-repo-gate, fail-closed, py32f071, presence-probe]

requires: []
provides:
  - "firestarter/tests/meta_presence.py — meta-repo presence probe (parent-not-sibling submodule arithmetic), keyed on an unrenameable <meta root>/.git marker"
  - "firestarter/tests/test_flash_path_record_sync.py (fail-closed half) — the single _extract_shared_section/_shared_sections extractor plus 10 committed fixtures covering all five RESEARCH F-14 fail-open modes"
affects: [129-02, 129-03, 129-04, 129-05, 129-06, 129-07, 129-08, 129-09]

tech-stack:
  added: []
  patterns:
    - "Meta-repo presence probe mirroring firestarter_app/tests/fw_presence.py, adjusted for the parent-not-sibling (submodule) direction"
    - "Fail-closed gate: MissingScanTargetError on present-root-missing-target, never a skip"
    - "Non-vacuity guard per parse ('vacuously true'), before any comparison"
    - "Parser that refuses to guess on duplicate/ambiguous markers ('refusing to guess')"
    - "Subprocess re-invocation to exercise import-time-bound module constants under a different FIRESTARTER_META_ROOT, guarded against infinite recursion via FIRESTARTER_129_GATE_CHILD"

key-files:
  created:
    - firestarter/tests/meta_presence.py
    - firestarter/tests/test_flash_path_record_sync.py
  modified: []

key-decisions:
  - "D-03/D-04 fail-closed machinery built and committed before either flash-path record exists (Phase 123 doctrine); Plan 129-02 adds the parity/content class to the same module"
  - "test_absent_meta_root_skip_is_auditable_not_silent scopes its subprocess re-invocation to itself only (not the whole module), since other tests in this class assume the real present meta root and would fail non-gracefully if re-run under an absent-root child process"

patterns-established:
  - "Single-helper rule: every RED and positive leg calls the same _extract_shared_section/_shared_sections pair"
  - "Import-time-bound module constants (META_ROOT, META_PRESENT, etc.) require a subprocess, never monkeypatch, to test under a different environment"

requirements-completed: []

coverage:
  - id: D1
    description: "meta_presence.py resolves /workspaces as the meta root, keys presence on an unrenameable .git marker, and names that marker in its absent-reason string"
    verification:
      - kind: unit
        ref: "cd /workspaces/firestarter && python -c \"from tests import meta_presence as m; assert str(m.META_ROOT)=='/workspaces'; assert m.META_MARKER.name=='.git'; assert m.META_PRESENT is True; assert str(m.META_MARKER) in m.META_ABSENT_REASON\""
        status: pass
    human_judgment: false
  - id: D2
    description: "test_flash_path_record_sync.py fail-closed half: 10/10 tests green, all five F-14 fail-open modes demonstrated with committed tmp_path-only fixtures"
    requirement: "PCB-01"
    verification:
      - kind: unit
        ref: "tests/test_flash_path_record_sync.py::TestFlashPathRecordSyncFailsClosed (10 tests) -- pytest tests/test_flash_path_record_sync.py -v"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full firmware suite stays green and grows by exactly 10 (180 -> 190 passed), zero skipped"
    verification:
      - kind: unit
        ref: "cd /workspaces/firestarter && python -m pytest tests/ -q"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-08-02
status: complete
---

# Phase 129 Plan 01: Meta-Repo Presence Probe & Fail-Closed Sync Gate Half Summary

**Built and committed the D-03 fail-closed sync-gate machinery — a submodule-aware meta-repo presence probe plus a 10-test fixture suite proving all five RESEARCH F-14 fail-open modes — before either flash-path record exists, per Phase 123's RED-first doctrine.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-02T10:57:00Z (per STATE.md `last_updated`)
- **Completed:** 2026-08-02
- **Tasks:** 4 (1 pin, 2 code, 1 commit)
- **Files modified:** 2 created

## Accomplishments

- `firestarter/tests/meta_presence.py`: mirrors `firestarter_app/tests/fw_presence.py` part-for-part, adjusted for the **parent-not-sibling** direction (the firmware repo is a submodule *of* the meta repo, so `META_ROOT` resolves one level further up than the analog's sibling arithmetic). Resolves `/workspaces` as `META_ROOT`, keys presence on `META_ROOT/.git` probed with `.exists()` (never a directory-only check, since a submodule's own `.git` is a file but the superproject's is a directory), and names the resolved marker path in `META_ABSENT_REASON` so an absence claim is always auditable. `MissingScanTargetError` is the hard-failure half: a present root with a missing named path raises rather than silently downgrading to a skip.
- `firestarter/tests/test_flash_path_record_sync.py` (fail-closed half only — Plan 129-02 adds the parity/content class to this same module): the single module-level `_extract_shared_section`/`_shared_sections` extractor every later content assertion will use, plus 10 tests in `TestFlashPathRecordSyncFailsClosed` demonstrating all five of RESEARCH F-14's fail-open modes purely against synthetic `tmp_path` fixtures and the real (present) meta root — none needs either flash-path record to exist yet.
- Suite grew from **180 passed** (pre-phase baseline) to **190 passed**, zero skipped, with the new gate module itself at 10/10.

## Task Commits

Task 1 (pre-flight pin) wrote no files and required no commit — it recorded and verified the starting state only.

1. **Task 2+3+4 combined into one commit** (per the plan's own Task 4 instruction — both new files staged and committed together): `3393137` (test) — `test(129-01): meta-repo presence probe and the fail-closed half of the flash-path record sync gate`

**Recorded verbatim (per plan's `<output>` instruction):**
- Meta branch: `gsd/v1.23-py32f071-integration`
- Firmware branch before: `v1.23-py32f071-integration` @ `7a0a375de7e71ed3e9108b9531fffb59d8d95cd8`
- Firmware branch after commit: `v1.23-py32f071-integration` @ `3393137778be78044159c2b6cb31895300e3a326a`
- Baseline pytest: `180 passed` (0 skipped)
- After-wave pytest: `190 passed` (0 skipped)
- Commit: `test(129-01): meta-repo presence probe and the fail-closed half of the flash-path record sync gate 3393137778be78044159c2b6cb31895300e3a326a`

## Files Created/Modified

- `firestarter/tests/meta_presence.py` — meta-repo presence probe: `META_ROOT`, `META_MARKER`, `META_PRESENT`, `META_ABSENT_REASON`, `requires_meta`, `MissingScanTargetError`, `meta_path(*parts)`
- `firestarter/tests/test_flash_path_record_sync.py` — fail-closed half: path constants, `_SHARED_KEYS`, `_SHARED_MARKER_RE`, `_extract_shared_section`, `_shared_sections`, `_assert_non_vacuous`, `_git_hash_object`, `_git_porcelain`, `_run_gate_in_subprocess`, `_synthetic_record`, and `class TestFlashPathRecordSyncFailsClosed` (10 tests)

## Decisions Made

- **Subprocess self-targeting for the F-14 mode 3 skip test.** `test_absent_meta_root_skip_is_auditable_not_silent` scopes its child `pytest` re-invocation to *only itself* (via an explicit pytest node id), rather than the whole module. The other 9 tests in the class assume the real, present meta root (e.g. `test_present_root_with_missing_target_raises_not_skips` calls the module-level `meta_path`, which under an overridden absent `FIRESTARTER_META_ROOT` would silently *not* raise, breaking that test's own `pytest.raises` block). Scoping the subprocess to itself avoids this cross-test interference while still proving the subprocess-based, import-time-bound-constant re-test mechanism the module's docstring requires. The recursion guard (`FIRESTARTER_129_GATE_CHILD`) is checked at the very top of the test body (self-skip) as well as inside `_run_gate_in_subprocess` (hard assert) as defense-in-depth.
- **`_assert_non_vacuous` uses lowercase `vacuously true`** (matching the app-repo analog's exact phrase) so `pytest.raises(AssertionError, match="vacuously true")` matches case-sensitively.
- Followed PATTERNS.md's prescribed docstring shape, needle-style Coverage block, and single-helper rule throughout; no `conftest.py` or other pytest config file was added, consistent with the repo's house rule.

## Deviations from Plan

None — plan executed exactly as written. All acceptance criteria for Tasks 1–4 were verified individually (see Self-Check below) before proceeding to the next task.

## Issues Encountered

- Two acceptance-criteria grep checks initially failed and were corrected inline before commit (not deviations from the plan's intent, just wording adjustments to satisfy the plan's own literal grep criteria):
  - `meta_presence.py`'s docstring initially used the literal substring `is_dir()` twice while describing what the probe does *not* do; the plan's acceptance criterion requires `grep -c 'is_dir()' tests/meta_presence.py` to return `0`. Reworded both occurrences to "a directory-only check" without changing the technical meaning.
  - The `NO CI leg on this branch` docstring phrase was initially line-wrapped across two lines, so a single-line grep for the full phrase returned 0. Reflowed the sentence so the full phrase appears on one line in both new files.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The gate module's fail-closed half is green (10/10) and the extractor (`_extract_shared_section`/`_shared_sections`) is ready for Plan 129-02 to build the parity/content class (`TestFlashPathRecordSync`) on top of, per the Validation Strategy's expected total of `31 failed, 190 passed` after wave 2 (RED-by-construction, since neither flash-path record exists yet).
- `meta_path(".planning", ...)` is proven to resolve correctly against the real present meta root and to raise `MissingScanTargetError` on a genuinely missing target — Plan 129-02's content tests can rely on this behavior without re-verifying it.
- No blockers. Firmware tree is clean at commit `3393137778be78044159c2b6cb31895300e3a326a` on `v1.23-py32f071-integration`.

---
*Phase: 129-flash-path-decision-pcb-requirements-record*
*Completed: 2026-08-02*

## Self-Check: PASSED

- FOUND: `firestarter/tests/meta_presence.py`
- FOUND: `firestarter/tests/test_flash_path_record_sync.py`
- FOUND: commit `3393137` in `firestarter` git log
