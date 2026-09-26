---
phase: 153-write-path-erase-policy
plan: 11
subsystem: cli
tags: [click, cli-help, docstrings, warning-text, syrupy, write-path]

# Dependency graph
requires:
  - phase: 153-write-path-erase-policy
    provides: "153-07's `write --skip-erase` warning arm, ERASE-01/ERASE-02 blank-check removal, ERASE-03's restored FLAG_CAN_ERASE / standalone `erase`"
provides:
  - "Corrected `write --skip-erase` warning text on protocol-0x0D chips: no longer denies the family has an erase capability, names `firestarter erase` as the standalone command"
  - "Rewritten C-8 comment recording the inverted former reasoning and re-derived (unchanged) decision not to add a second warning"
  - "Extended `write` docstring: `-b`/`--no-blank-check` is unread on protocols 0x0D and 0x05"
  - "Extended `erase` docstring: inverse `-b` polarity (post-erase blank check, unwired on 0x0D per D-153-04), `-s/--sector-address` ignored by the device-global 0x0D chip erase"
  - "New guard leg `test_no_blank_check_vacuity_warning_is_printed_on_0x0d` defending the no-second-warning decision, proven reachable against a temporary echo"
  - "Regenerated `test_help_write`/`test_help_erase` syrupy snapshots for the extended docstrings"
affects: [153-12, 153-13, 152-outward-facing-close-operator-gated]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Module-level literal + negative assertion for a deliberately-not-added warning, proven reachable via a temporary echo before commit, then reverted (guards against future accidental regression of a documented decision-not-to-warn)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_write_skip_erase_0x0d.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "Corrected the false clause in the --skip-erase warning without touching its pinned opening fragment, preserving all pre-existing pinning-suite assertions"
  - "Kept the no-second-warning decision (no new warning for -b/--no-blank-check vacuity on 0x0D), now grounded in RESEARCH Pitfall 5 and 152-CONTEXT.md D-08 rather than the original (now-inverted) C-8 reasoning"
  - "Added a guard leg for the no-second-warning decision, verified reachable via a temporary echo + observed failure before committing the reverted state"

requirements-completed: []

coverage:
  - id: D1
    description: "write --skip-erase warning on a 0x0D chip no longer claims the family lacks an erase capability; names `firestarter erase` instead"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_write_skip_erase_0x0d.py::test_skip_erase_on_0x0d_warns_and_proceeds"
        status: pass
    human_judgment: false
  - id: D2
    description: "C-8 comment records the inverted former reasoning and the re-derived (unchanged) conclusion, citing Pitfall 5 and D-08"
    verification:
      - kind: other
        ref: "firestarter_app/firestarter/cli_handlers.py comment block above the skip_erase warning arm"
        status: pass
    human_judgment: false
  - id: D3
    description: "write and erase docstrings record the new flag semantics (blank-check unread on 0x0D/0x05; erase -b post-erase-check unwired on 0x0D; sector-address ignored on 0x0D)"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_characterization.py::test_help_write, ::test_help_erase (regenerated snapshots)"
        status: pass
    human_judgment: false
  - id: D4
    description: "No second (blank-check-vacuity) warning was added; a committed leg fails loudly if one ever is, and was observed failing against a temporary echo"
    requirement: "ERASE-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_write_skip_erase_0x0d.py::test_no_blank_check_vacuity_warning_is_printed_on_0x0d"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 11: Correct the false skip-erase claim and record new flag semantics Summary

**Corrected the one user-visible string this phase falsifies (`write --skip-erase`'s "no erase operation at all" claim), extended both `write` and `erase` docstrings with the new flag semantics from D-153-04/D-153-05, and added a test that fails loudly if a symmetric-but-rejected blank-check-vacuity warning is ever added.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 2/2 completed
- **Files modified:** 3 (`cli_handlers.py`, `test_write_skip_erase_0x0d.py`, `test_characterization.ambr`)

## Accomplishments

- Corrected the `write --skip-erase` warning on protocol-0x0D chips: it no longer claims the 28C family "has no erase operation at all" (false since ERASE-03 restored `FLAG_CAN_ERASE`); it now states only that the write path performs no erase, and names `firestarter erase` as the unaffected standalone command. The pinned opening fragment (`"has nothing to skip on this chip's protocol"`) was preserved verbatim so all pre-existing pinning-suite legs stayed green by construction, verified rather than assumed.
- Rewrote the C-8 comment above the warning arm to record three things: the arm's scope is unchanged; its own former justification for not extending to `-b`/`--no-blank-check` has inverted (that flag is no longer "genuinely useful on a non-blank part" since ERASE-01 removed the pre-write blank check entirely — it's now itself a no-op, for a different reason); and the conclusion (still no second warning) is unchanged but re-derived, citing RESEARCH §Common Pitfalls Pitfall 5 and 152-CONTEXT.md D-08 (a blank-check-vacuity warning would train users to think the write needs a flag — precisely what D-08 exists to keep out of the public release notes).
- Extended `write`'s docstring: `-b`/`--no-blank-check` is now unread on protocols `0x0D` and `0x05` (neither performs a pre-write blank check any more), remains live elsewhere.
- Extended `erase`'s docstring: per D-153-04, its `-b`/`--blank-check` has the inverse polarity of `write`'s (post-erase check, not skipped pre-check) and is unwired (a documented, not discovered, no-op) on `0x0D`; `-s`/`--sector-address` is ignored by the device-global `0x0D` chip erase.
- Added `test_no_blank_check_vacuity_warning_is_printed_on_0x0d` (leg 7) asserting the absence of a hypothetical second warning against a module-level literal (`_BLANK_CHECK_VACUITY_FRAGMENT`). Reachability was proven before committing: a temporary `click.echo` containing the literal was added to `cli_handlers.py`, the leg was run and observed failing (transcribed below), then the temporary echo was reverted and confirmed absent via `git diff --stat`.
- No new `click.echo` or `click.option` call was added anywhere — counts unchanged at 11/68 (verified against `git show HEAD` pre-task baseline).
- Discovered and fixed a scope gap the plan did not explicitly call out: extending the docstrings changed Click's rendered `--help` text, which broke the two full-text syrupy snapshots (`test_help_write`, `test_help_erase`) plus `test_no_blank_check_polarity` which reuses `test_help_write`'s snapshot. Regenerated all three via `--snapshot-update` and reviewed the diff (28 insertions, 0 deletions — additive only, matching the docstring extensions).
- Ran the full host suite: **1812 passed, 0 failed** (1811 inherited + this plan's new leg).

## Task Commits

Each task was committed atomically:

1. **Task 1: Correct the `--skip-erase` warning text and record the no-second-warning decision** - `50ad097` (fix)
2. **Task 2: Update the pinning suite's narrative and add a guard against a future blank-check warning** - `9af91fe` (test)
3. **Snapshot regeneration (deviation, Rule 3 — blocking fix)** - `e2b807d` (test)

**Plan metadata:** pending (this commit)

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` - corrected `write --skip-erase` warning text, rewrote C-8 comment, extended `write` and `erase` docstrings
- `firestarter_app/tests/test_write_skip_erase_0x0d.py` - updated module/leg-4 docstrings to match the current mechanism, added leg 7 (`test_no_blank_check_vacuity_warning_is_printed_on_0x0d`) and its guard literal
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` - regenerated `test_help_write` and `test_help_erase` full-text snapshots (also covers `test_no_blank_check_polarity`, which reuses `test_help_write`'s snapshot)

## Decisions Made

- Preserved the pinned opening fragment of the `--skip-erase` warning exactly, changing only the clause that became false — verified against all 6 (now 7) legs of `test_write_skip_erase_0x0d.py` rather than assumed safe.
- Kept the C-8 arm's scope unchanged (still no warning on `-b`/`--no-blank-check`) but re-derived the reasoning: RESEARCH Pitfall 5 / 152-CONTEXT.md D-08 replace the now-inverted "genuinely useful on a non-blank part" argument.
- Added a guard test for the no-second-warning decision rather than leaving it as prose-only, and proved it reachable (not merely pre-authored-and-green) via an observed failing run against a temporary echo before commit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking issue] Docstring changes broke two full-text syrupy snapshots**
- **Found during:** Post-task-2 full-suite verification
- **Issue:** Extending `write`'s and `erase`'s docstrings (Task 1) changed Click's rendered `--help` output, which is pinned byte-for-byte by `test_help_write`/`test_help_erase` in `tests/__snapshots__/test_characterization.ambr`. `test_no_blank_check_polarity` also failed because it reuses `test_help_write`'s snapshot. This matched the plan's own `<critical_notes>` warning ("CLI help text is pinned by TWO full-text syrupy snapshots") but the plan's task list did not include an explicit regeneration step.
- **Fix:** Ran `pytest tests/test_characterization.py -k "test_help_write or test_help_erase or test_no_blank_check_polarity" --snapshot-update -o addopts="" -q`, then reviewed the resulting diff (28 insertions, 0 deletions — the new docstring paragraphs only, no unrelated reformatting) before committing.
- **Files modified:** `firestarter_app/tests/__snapshots__/test_characterization.ambr`
- **Verification:** Full host suite re-run after the update: 1812 passed, 0 failed.
- **Committed in:** `e2b807d`

**2. [Rule 3 - Blocking issue] `no erase operation` literal accidentally reintroduced in test narrative**
- **Found during:** Task 2 acceptance-criteria self-check
- **Issue:** The rewritten module docstring's narrative correction initially phrased the pre-153 state as "had no erase operation whatsoever," which reintroduced the exact forbidden literal (`grep -c 'no erase operation'` returned 1, required 0).
- **Fix:** Reworded to "had no erase capability at all," preserving meaning while avoiding the literal.
- **Files modified:** `firestarter_app/tests/test_write_skip_erase_0x0d.py`
- **Verification:** `grep -c 'no erase operation' tests/test_write_skip_erase_0x0d.py` returns `0`; full 7-leg suite still green.
- **Committed in:** `9af91fe`

---

**Total deviations:** 2 auto-fixed (both Rule 3 — blocking issues discovered during verification, not scope changes).
**Impact on plan:** No scope creep. Both fixes were required to leave the pinning suite and snapshot suite genuinely green rather than merely locally green.

## Issues Encountered

**mypy watermark check failed under devcontainer Python 3.12** (`Type statement is only supported in Python 3.12 and greater` inside a numpy stub, causing mypy to exit 2). This matches the standing project note that the devcontainer's default Python masks the CI's actual 3.11-only gate. Resolved by recreating the project's `.venv/ci-replica` 3.11 venv via `uv venv --python 3.11 .venv/ci-replica` (with `UV_CACHE_DIR` set to the session scratchpad) and `uv pip install -p .venv/ci-replica/bin/python3.11 -e '.[test]'`, then running all verification (`pytest`, `ruff check`, `ruff format --check`, `check_mypy_watermark.py`) through that interpreter. Confirmed mypy watermark at exactly 35/35 (zero headroom, as flagged in the plan's critical notes) — this plan added no new mypy errors.

## Verification Summary

- **Pinning suite:** `test_write_skip_erase_0x0d.py` — 7/7 legs pass under the 3.11 CI-replica venv.
- **Guard-leg reachability:** `test_no_blank_check_vacuity_warning_is_printed_on_0x0d` was run against a temporary `click.echo(f"{eprom.upper()}: --no-blank-check has nothing to skip on this chip's protocol (TEMPORARY REACHABILITY PROBE).")` inserted ahead of the existing `--skip-erase` arm (guarded by `if not blank_check and is_protocol_0x0d:`), and observed to fail with:
  ```
  AssertionError: assert 'no-blank-ch...hing to skip' not in 'AT28C256: -...TY PROBE).\n'
    'no-blank-check has nothing to skip' is contained here:
      AT28C256: --no-blank-check has nothing to skip on this chip's protocol (TEMPORARY REACHABILITY PROBE).
  ```
  The temporary echo was then reverted; `git diff --stat -- firestarter/cli_handlers.py` showed no residual change, and `click.echo` count returned to 11 (its pre-task value).
- **Full host suite:** 1812 passed, 0 failed (1811 inherited from prior plans + this plan's new leg 7).
- **ruff check firestarter/ tests/:** All checks passed.
- **ruff format --check firestarter/ tests/:** 154 files already formatted.
- **mypy watermark:** 35/35 (checked 156 source files) — at watermark, zero headroom, no new errors.
- **`git diff --quiet -- tools/check_dispatch.py`:** holds (exit 0, no diff).
- **`firestarter/` (firmware sub-repo):** confirmed clean (`git status --short` empty) — no tracked modifications.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- ERASE-03 remains **In Progress** (not flipped by this plan) — plans 12 and 13 in wave 9+ still own the remainder of that requirement's claims. `.planning/REQUIREMENTS.md` line 311 checkbox is correctly left unchecked.
- The pinning suite (`test_write_skip_erase_0x0d.py`) and the CLI help snapshots are both now internally consistent with the corrected warning text and extended docstrings — plans 12/13 should not need to touch either unless they change `cli_handlers.py`'s write/erase surface further.
- No blockers identified for downstream plans.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

All claimed commits (`50ad097`, `9af91fe`, `e2b807d`) verified present via `git log --oneline --all`.
All claimed files (`firestarter_app/firestarter/cli_handlers.py`, `firestarter_app/tests/test_write_skip_erase_0x0d.py`,
`firestarter_app/tests/__snapshots__/test_characterization.ambr`) verified present on disk.
