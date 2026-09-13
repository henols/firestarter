---
phase: 186-the-python-floor-before-the-eol
plan: 02
subsystem: packaging
tags: [python, ruff, pyupgrade, lint, mypy, py311, regex-repair]

requires:
  - phase: 186-01
    provides: "All four floor statements at 3.11 (requires-python, ruff target-version, mypy python_version, CI pins), live before this sweep ran"
provides:
  - "182-finding ruff sweep absorbed at the config-supplied py311 target: 190 mechanical fixes, 3 hand-fixed UP045 sites, a second-order F401 fix, and a formatter pass — both `ruff check` and `ruff format --check` green"
  - "The one existing gate the sweep reds (`tests/test_cap03_ack_layout_parity.py`'s `_DECODE_ID_FRAME_DEF_RE`) repaired with a one-line regex edit matching the new `LogMessage | None` union form"
  - "mypy watermark confirmed unmoved at 35/35 post-sweep, proving the config-before-sweep ordering constraint held"
  - "Full suite back at its pre-phase count (2359 passed, 0 failed) with the 70% coverage floor met (84.76%)"
affects: [186-03, 186-04]

actuals:
  tokens: 13000
  raw_tokens: 13000
  tasks: 2
  commits: 2
  plan_head_before: "2fd23ca55b7dde565d5b46bf9ed5b8d7c9fc7b3b"

tech-stack:
  added: []
  patterns:
    - "Sweep-then-hand-fix-then-second-pass-then-format ordering: ruff's autofix iterates and unmasks a second-order finding (an unused import orphaned by a hand fix) that only a second `--fix` pass catches; the formatter must run last because shortened annotations make previously-wrapped lines fit and the formatter wants to unwrap them — CI checks `ruff format --check` as its own step, so this is not optional cosmetics"
    - "Source-text gates over a signature (regex pinning a spelling) must be repaired to match the new form only, not both old and new — accepting the old spelling as an either/or alternative would pin a spelling lint now forbids, a second stale claim replacing the first"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/address_parser.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/codec.py
    - firestarter_app/firestarter/config.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/firestarter/eprom_info.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/firestarter/hardware.py
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/jp5_gate.py
    - firestarter_app/firestarter/main.py
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/tests/test_dev_gate_reads_no_firmware_source.py
    - firestarter_app/tests/test_runtime_dependencies.py
    - firestarter_app/tests/test_cap03_ack_layout_parity.py

key-decisions:
  - "Every measured prediction in the plan (193 total findings on first --fix, 190 fixed / 3 remaining, the exact 3 UP045 sites, the second-pass F401, the 4 files the formatter unwraps, the 15-file sweep blast radius, the 6 CAP-03 red legs by exact name) matched the observed output exactly — no disagreement to reconcile."
  - "The CAP-03 regex repair matches the new `LogMessage | None` form ONLY, not an either/or over both spellings, per the plan's explicit reasoning: the old form cannot reappear in this tree without ruff flagging it as UP045 at the configured target, so accepting both would pin a spelling lint now forbids."
  - "FLOOR-01 left Pending in REQUIREMENTS.md — not marked complete by this plan, per the plan's own multi-plan accounting (spans 186-01/02/03) and the standing instruction to avoid the known premature-completion defect."

requirements-completed: []

coverage:
  - id: D1
    description: "The 182-finding ruff sweep is absorbed at the config-supplied py311 target with no --target-version override anywhere in the command list"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: ".venv/ci-replica/bin/ruff check firestarter/ tests/ — Task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D2
    description: "The three UP045 findings ruff cannot autofix (eprom_info.py:97:24, :100:36, :103:26, all in prepare_detailed_eprom_data's signature) resolved by hand, named individually, with no --unsafe-fixes used anywhere"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: "/usr/bin/grep -c 'dict | None' firestarter/eprom_info.py; /usr/bin/grep -c 'Optional' firestarter/eprom_info.py — Task 1 <acceptance_criteria>"
        status: pass
    human_judgment: false
  - id: D3
    description: "ruff format --check green (179 files already formatted), satisfying the CI step the fix pass alone does not satisfy"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: ".venv/ci-replica/bin/ruff format --check firestarter/ tests/ — Task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D4
    description: "mypy watermark unmoved at 35/35 post-sweep (181 files checked), confirming the config-before-sweep ordering held"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: ".venv/ci-replica/bin/python tools/check_mypy_watermark.py — Task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D5
    description: "The runtime version guard's UP036 suppression in main.py survived the sweep intact (an autofix tool authorized to rewrite 15 files must not delete a safety guard)"
    verification:
      - kind: unit
        ref: "/usr/bin/grep -c 'noqa: UP036' firestarter/main.py — Task 1 <verify>"
        status: pass
    human_judgment: false
  - id: D6
    description: "The predicted 6 CAP-03 red legs were observed exactly as predicted (same 6 test names) before being repaired, and repaired with a single regex literal matching the new union form"
    requirement: "FLOOR-01"
    verification:
      - kind: unit
        ref: "tests/test_cap03_ack_layout_parity.py -o addopts=\"\" -q — Task 2 <verify>, 12 passed"
        status: pass
    human_judgment: false
  - id: D7
    description: "Full app suite back at its pre-phase count (2359 passed, 0 failed) and the 70% coverage floor is met"
    verification:
      - kind: unit
        ref: "pytest tests/ -o addopts=\"\" -q; pytest tests/ --cov=firestarter --cov-fail-under=70 — Task 2 <verify>"
        status: pass
    human_judgment: false
  - id: D8
    description: "Zero comments written into any source file during the sweep or the hand fixes; only deletions (orphaned inner comments, an unused import, a noqa directive) occurred"
    verification: []
    human_judgment: true
    rationale: "The hard no-comments rule is verified by code review of the diff (git diff was inspected line by line during execution and every touched line is an annotation spelling, a datetime alias, an import sort, or a deletion) rather than by an automated grep asserting a negative claim across arbitrary future comment styles."

duration: 24min
completed: 2026-09-12
status: complete
---

# Phase 186 Plan 02: The Py311 Ruff Sweep, Absorbed Summary

**Absorbed the full 182-finding lint consequence of the new py311 target as its own commit — 190 mechanical fixes, 3 hand-resolved UP045 sites named individually, a second-order F401 fix, and a formatter pass — then repaired the one existing gate (a source-text regex over `_decode_id_frame`'s return spelling) the sweep reds, with every one of the plan's measured predictions matching the observed output exactly.**

## Performance

- **Duration:** ~24 min
- **Completed:** 2026-09-12
- **Tasks:** 2
- **Files modified:** 16 (15 in Task 1, 1 in Task 2)

## Accomplishments

- **Task 1 (the sweep):** Ran `ruff check --fix firestarter/ tests/` with no `--target-version` flag — the target came from `pyproject.toml`'s `target-version = "py311"`, landed by 186-01, so the command's own output (`Found 193 errors (190 fixed, 3 remaining)`) is the proof that config edit is live. The three remaining UP045 findings were all in `firestarter/eprom_info.py`'s `prepare_detailed_eprom_data` signature (`:97:24` `eprom_details`, `:100:36` `eprom_data_for_programmer`, `:103:26` `raw_config_data`) — each an `Optional[...]` subscript spanning lines and enclosing a comment, which is exactly why ruff classifies the fix unsafe. Collapsed all three to `dict | None` by hand, dropping the now-orphaned inner comments (deletion, permitted by the hard rule; no replacement comment added). A second `--fix` pass caught the resulting second-order F401 on the now-unused `typing.Optional` import (`Found 1 error (1 fixed, 0 remaining)`). `ruff format firestarter/ tests/` then reformatted exactly the 4 predicted files (`address_parser.py`, `cli_handlers.py`, `diagnostic_report.py`, `hardware.py`) — shortened annotations made previously-wrapped lines fit, and the formatter wanted to unwrap them; CI checks this as its own step. `--unsafe-fixes` was never run at any point, per the plan's standing prohibition (it would have deleted `main.py`'s runtime-guard `noqa: UP036`, which was independently confirmed intact). Both ruff gates went green (`All checks passed!`, `179 files already formatted`), the mypy watermark held at 35/35 (181 files checked), and the six predicted CAP-03 failures were observed with the exact predicted test names, recorded, and left unrepaired for Task 2.
- **Task 2 (the regex repair):** `_DECODE_ID_FRAME_DEF_RE` in `tests/test_cap03_ack_layout_parity.py` pinned `_decode_id_frame`'s return annotation as source text (`Optional[LogMessage]`); the sweep rewrote both definitions in `serial_comm.py` to the union form (`LogMessage | None`), the regex matched zero definitions, and `_extract_decode_id_frame_body` raised its non-vacuity assertion — failing loud, not open, exactly as designed. Updated the pattern's return-type alternative to match the new union form only (not an either/or over both spellings): the old form cannot reappear in this tree without tripping UP045 at the configured target, so accepting both would pin a spelling lint now forbids — a second stale claim replacing the one being removed. Verified with the sibling firmware repo present: all 12 CAP-03 legs pass. Full suite ran to completion at 2359 passed / 0 failed (unchanged from the pre-phase count), and the coverage floor was met at 84.76% (>= 70% required).

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter_app` on branch `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`:

1. **Task 1: The sweep — mechanical autofix, three hand fixes named individually, then the formatter (D-09)** - `1ebc548` (feat)
2. **Task 2: Repair the one gate the sweep reds — a source-text regex pinning the old return spelling** - `7f53886` (fix)

**Plan metadata:** this SUMMARY.md, committed in the meta repo at `/workspaces` (separate commit, per repository_layout instructions).

**Note on repo layout:** both code commits above live in `firestarter_app` (a separate git repository, submodule-tracked from the meta repo). The meta repo's gitlink for `firestarter_app` is deliberately NOT advanced by this plan — plan 186-04 owns that single bump.

## Files Created/Modified

- `firestarter_app/firestarter/eprom_info.py` - three UP045 sites hand-collapsed to `dict | None`; second-pass F401 removed the now-unused `typing.Optional` import
- `firestarter_app/firestarter/{address_parser,cli_handlers,codec,config,diagnostic_report,eprom_operations,firmware,hardware,ic_layout,jp5_gate,main,serial_comm}.py` - mechanical annotation modernisation (UP045/UP017/UP035/I001); 4 of these additionally reformatted by the formatter pass
- `firestarter_app/tests/test_dev_gate_reads_no_firmware_source.py`, `firestarter_app/tests/test_runtime_dependencies.py` - mechanical annotation modernisation
- `firestarter_app/tests/test_cap03_ack_layout_parity.py` - one regex literal in `_DECODE_ID_FRAME_DEF_RE`, repointed to the swept `LogMessage | None` union form

## Decisions Made

- Every measured prediction from RESEARCH.md/the plan text (findings counts, the 3 named UP045 sites, the second-order F401, the 4 reformatted files, the 15-file blast radius, the 6 CAP-03 red legs by exact name, 12 passed post-repair, 2359 passed / 0 failed, 84.76% coverage) matched the observed output exactly — no disagreement to reconcile at any step.
- The CAP-03 regex repair matches the new form only, not both spellings — see key-decisions above.
- FLOOR-01 left Pending in `.planning/REQUIREMENTS.md` (not marked complete): it spans 186-01/02/03 and this is only the second contributing plan. No `requirements.mark-complete` call was made for it in this plan, per the plan's own hard-rule instruction to avoid the known premature-completion defect regardless of whether the shared-ID gate would have blocked it anyway.

## Deviations from Plan

None - plan executed exactly as written. Every measured figure in the plan text (fix counts, file names, line numbers, test names) matched the observed output with zero disagreement, so no reconciliation was needed and no fallback path was invoked.

## Issues Encountered

None. The full-suite and coverage runs (each ~8-14 min) were run in the background per the environment contract to avoid a foreground-timeout misread as failure; both completed cleanly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Both ruff gates are green at the py311 target with no override flag, the mypy watermark is unmoved at 35/35, and the CAP-03 parity gate matches the code it guards again.
- `firestarter_app/firestarter/py32_dfu.py`'s 14 pre-existing UP045 suppressions remain untouched (out of scope by orchestrator ruling 4, carried from 186-01) — the named residual gap that the new lint target has one file where its consequence is switched off. Recorded here for plan 186-04's rationale note, as 186-01's SUMMARY anticipated.
- FLOOR-01 remains `Pending` in `.planning/REQUIREMENTS.md` — this is the second of three contributing plans (186-01/02/03).
- No blockers for 186-03 or 186-04.

---
*Phase: 186-the-python-floor-before-the-eol*
*Completed: 2026-09-12*

## Self-Check: PASSED

- All 16 files in `key-files.modified` exist in `firestarter_app` and carry the described changes (verified via `git show` diffs during execution).
- Commit `1ebc548` (Task 1) and `7f53886` (Task 2) both found in `firestarter_app`'s `git log --oneline --all`.
- All plan-level `<acceptance_criteria>` re-verified passing: `ruff check` → `All checks passed!`; `ruff format --check` → `179 files already formatted`; mypy watermark → `mypy errors: 35 (watermark: 35)`, `OK: error count at watermark.`, `checked 181 source files`; `grep -c 'dict | None'` and `grep -c 'Optional'` (0) on `eprom_info.py`; `git diff --stat`/`--name-only` against `BASE_SHA` (`2fd23ca55b7dde565d5b46bf9ed5b8d7c9fc7b3b`) names exactly 16 files across both tasks, none under `tools/`, `.github/`, nor `messages.py`/`frame_vectors.py`/`py32_dfu.py`; comment-line counts (`^[[:space:]]*#`) unchanged in every touched file; `noqa: UP036` count 1 in `main.py`; CAP-03 file reports `12 passed`; full suite `2359 passed, 1 warning` (0 failed); coverage `Required test coverage of 70% reached. Total coverage: 84.76%`.
- Plan-level `<verification>` block re-run: all items pass as itemized above.
- `git status --porcelain` in `firestarter_app` names only the two pre-existing untracked datasheet PDFs; no tracked file outside this plan's `files_modified` list.
