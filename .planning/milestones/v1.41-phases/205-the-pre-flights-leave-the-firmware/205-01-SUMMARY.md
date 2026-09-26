---
phase: 205-the-pre-flights-leave-the-firmware
plan: 01
subsystem: host-cli
tags: [click, cli-handlers, blank-check, erase, exit-codes, host-side-tracer]

requires:
  - phase: 202
    provides: "check_eprom_blank / _drive_region_compare, the whole-region compare engine and its 0/1/2 verdict contract"
  - phase: 203
    provides: "the write-guard-moves-up-a-layer precedent (host gains a capability before firmware loses it) and its keyword-only plumbing idiom"
provides:
  - "firestarter erase -b re-implemented host-side through check_eprom_blank, with a 0/1/2 exit contract"
  - "erase -s <addr> -b is refused (exit 2, one line) before the erase runs, closing the protocol-0x06 hazard D-01 would otherwise create"
  - "the host-side precondition Phase 205's firmware sweep (plans 02-07) now depends on: erase-end capability exists on the host before eprom.cpp:52-54 is deleted"
affects: [205-02, 205-03, 205-04, 205-05, 205-06, 205-07, 206-session-cost]

actuals:
  tokens: 4600
  tasks: 2
  commits: 2
  plan_head_before: 2a17fd7bd650274361e5730bd9e2eebb753ef069

tech-stack:
  added: []
  patterns:
    - "erase's tail is now sys.exit(verdict) with no bool-to-int mapping layer, matching blank/verify"
    - "OQ-1's pre-wire refusal is a sibling helper next to _region_refusal_exit_code, not a new gate module (Fork B)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/test_cli_handlers.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr

key-decisions:
  - "Fork A upheld: erase_eprom stays bool. Only when -b is set AND the erase succeeded does the handler call check_eprom_blank and exit on ITS verdict; erase_eprom's own failure keeps exit 1."
  - "Fork D upheld: the blank check never runs when erase_eprom returns False -- verified by a dedicated leg."
  - "Fork B/C upheld: the -s/-b refusal lives in cli_handlers.py next to _region_refusal_exit_code (not a new gate module) and returns exit 2, the same class as that helper's two refusals."
  - "test_erase_blank_check_polarity survives this plan unchanged -- neither task touches _build_op_flags; that re-key is Plan 04's job."
  - "The top-level command-list snapshot did not move -- only test_help_erase changed. No command was added or removed."

requirements-completed: [FWBLANK-02]

coverage:
  - id: D1
    description: "erase -b performs a host-side whole-device blank check through check_eprom_blank and exits on its 0/1/2 verdict"
    requirement: FWBLANK-02
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_blank_check_exits_zero_when_the_part_reads_blank"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_blank_check_exits_one_when_the_part_is_not_blank"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_blank_check_exits_two_when_the_check_itself_fails"
        status: pass
    human_judgment: false
  - id: D2
    description: "plain erase (no -b) is behaviourally unchanged: same 0/1 exit codes, one port open, no call into check_eprom_blank"
    requirement: FWBLANK-02
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_without_blank_check_opens_no_second_port_and_keeps_zero_one"
        status: pass
    human_judgment: false
  - id: D3
    description: "a failed post-erase check prints exactly one line and erase gains no --full option"
    requirement: FWBLANK-02
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_blank_check_prints_exactly_one_line_on_a_failed_check"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_has_no_full_option"
        status: pass
    human_judgment: false
  - id: D4
    description: "erase -s <addr> -b is refused with exit 2 and one stated line, before the erase runs; -s alone and -b alone are unaffected"
    requirement: FWBLANK-02
    verification:
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_sector_address_with_blank_check_is_refused_before_the_erase"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_sector_address_without_blank_check_still_runs"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py#test_erase_blank_check_does_not_run_when_the_erase_failed"
        status: pass
    human_judgment: false
  - id: D5
    description: "the erase docstring states both exit contracts, the blank --full composition, the -s/-b constraint, and no longer claims a 0x0D gap"
    requirement: FWBLANK-02
    verification:
      - kind: unit
        ref: "tests/test_characterization.py#test_help_erase"
        status: pass
    human_judgment: false
  - id: D6
    description: "the whole host suite, ruff check and ruff format --check are green on Python 3.11 with no regression in the passed count"
    requirement: FWBLANK-02
    verification:
      - kind: integration
        ref: ".venv311/bin/python -m pytest tests/ -o addopts=\"\" -p no:cacheprovider -q"
        status: pass
      - kind: other
        ref: ".venv311/bin/ruff check firestarter/ tests/ && .venv311/bin/ruff format --check firestarter/ tests/"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-22
status: complete
---

# Phase 205 Plan 01: erase -b moves to the host Summary

**`firestarter erase -b` re-implemented one tier up through Phase 202's `check_eprom_blank`, with a 0/1/2 exit contract and a pre-wire refusal for `-s`+`-b`, closing the one gap before Phase 205's firmware sweep can safely delete `eprom.cpp:52-54`.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-09-22T00:00:00Z (see git commit timestamps for precise timing)
- **Completed:** 2026-09-22
- **Tasks:** 2
- **Files modified:** 3 (`firestarter/cli_handlers.py`, `tests/test_cli_handlers.py`, `tests/__snapshots__/test_characterization.ambr`)

## Accomplishments

- `erase -b`, after a successful erase, now calls `check_eprom_blank` and `sys.exit`s directly on its 0/1/2 verdict — no bool-to-int mapping layer, matching the `blank`/`verify` handlers' shape.
- Plain `erase` (no `-b`) is untouched: still exits 0/1, still opens exactly one port, never calls `check_eprom_blank`.
- A failed check (`erase_eprom` returns `False`) never triggers the blank check (Fork D) — no fabricated "not blank" verdict for a part that was never erased.
- `erase -s <addr> -b` is refused (exit 2, one stated line) before the erase runs, closing the measured protocol-`0x06` hazard: a whole-device check after a sector erase would report the untouched remainder as non-blank, a reliable false negative.
- The `erase` docstring states both exit contracts, the `-s`/`-b` constraint, and the `firestarter blank <chip> --full` composition offered instead of a `--full` option on `erase`; it no longer claims a protocol `0x0D` gap (the host check is protocol-agnostic — a behaviour gain).
- `test_help_erase` hand-edited against the printed diff both times; `--snapshot-update` never run. The top-level command-list snapshot did not move.

## Task Commits

Each task was committed atomically, in the `firestarter_app` submodule, on `v1.41-verification-to-host`:

1. **Task 1: erase -b runs the blank check on the host, end to end, with a 0/1/2 contract** — `9006258` (feat)
2. **Task 2: refuse erase -s together with -b, before the erase runs** — `55859f6` (feat)

**Meta gitlink advance + SUMMARY:** committed separately in the meta repo (see final commit below).

_Both tasks carried `tdd="true"`; each landed as a single commit (tests + implementation + snapshot together), per the plan's own "one commit, three files" instruction — not a separate RED commit. RED was observed and captured (below) before each implementation landed, satisfying the RED-seen-first discipline without a separate commit._

## RED Transcripts (captured before each implementation landed)

### Task 1 — 7 legs authored, run against the unmodified handler

```
tests/test_cli_handlers.py::test_erase_blank_check_exits_zero_when_the_part_reads_blank FAILED
tests/test_cli_handlers.py::test_erase_blank_check_exits_one_when_the_part_is_not_blank FAILED
tests/test_cli_handlers.py::test_erase_blank_check_exits_two_when_the_check_itself_fails FAILED
tests/test_cli_handlers.py::test_erase_blank_check_prints_exactly_one_line_on_a_failed_check FAILED
tests/test_cli_handlers.py::test_erase_without_blank_check_opens_no_second_port_and_keeps_zero_one PASSED
tests/test_cli_handlers.py::test_erase_blank_check_does_not_run_when_the_erase_failed PASSED
tests/test_cli_handlers.py::test_erase_has_no_full_option PASSED
4 failed, 7 passed, 83 deselected in 1.12s
```

4 of the 7 legs failed for the intended reason: the unmodified `erase` handler never calls `check_eprom_blank` at all, so it always exits `0 if ok else 1` regardless of `-b`. The other 3 legs (`..._opens_no_second_port...`, `..._does_not_run_when_the_erase_failed`, `..._has_no_full_option`) were already green against the unmodified tree by design — each pins an invariant the implementation must *preserve*, not introduce (plain `erase` never called `check_eprom_blank` before this plan either; `--full` was never a registered option). Each of the three would fail under a plausible regression (e.g. the implementation always calling `check_eprom_blank` regardless of the flag), so none is the "unreachable pre-authored leg" the house discipline warns about — they are reachable, currently-satisfied pins.

### Task 2 — 2 legs authored, run against the task-1-complete tree

```
tests/test_cli_handlers.py::test_erase_sector_address_with_blank_check_is_refused_before_the_erase FAILED
tests/test_cli_handlers.py::test_erase_sector_address_without_blank_check_still_runs PASSED
1 failed, 1 passed, 94 deselected in 0.39s
```

The refusal leg failed for the intended reason: `_erase_sector_blank_refusal_exit_code` did not exist yet, so `erase -s 0x10000 -b` proceeded into Task 1's flow (erase, then blank check), landing on `check_eprom_blank`'s mock return value instead of the OQ-1 refusal. The second leg (`-s` alone unaffected) was already green, pinning that `-s` without `-b` is untouched — also a reachable pin, not vacuous.

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` — `erase`'s tail widened to a three-arm 0/1/2 exit; `_ERASE_SECTOR_BLANK_REFUSAL` + `_erase_sector_blank_refusal_exit_code` added as siblings to `_region_refusal_exit_code`; docstring rewritten (both contracts, `-s`/`-b` constraint, `blank --full` composition, `0x0D` claim removed).
- `firestarter_app/tests/test_cli_handlers.py` — 9 new legs (7 in task 1, 2 in task 2), all listed in the plan's `<artifacts_this_plan_produces>`.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — `test_help_erase` hand-edited twice against the printed diff (task 1's contract rewrite, task 2's `-s`/`-b` sentence). Top-level command-list snapshot unchanged.

## Decisions Made

- **Fork A upheld** — `erase_eprom` stays `bool`. D-02 widens the *check's* contract, not the erase's; the erase's own failure keeps exit 1 as it always has.
- **Fork B/C upheld** — the OQ-1 refusal is a sibling helper in `cli_handlers.py`, not a new gate module, and returns exit 2 (the same class `_region_refusal_exit_code` returns for both of its refusals).
- **Fork D upheld** — the blank check never runs after a failed erase; verified by `test_erase_blank_check_does_not_run_when_the_erase_failed`.
- **`test_erase_blank_check_polarity` survives unchanged** — neither task touches `_build_op_flags`'s composition; confirmed by running it alongside the new legs (still passing, unmodified). Plan 04 is where that re-key happens.
- **"prints exactly one line" tested via `caplog`, not `result.output`** — this codebase's own established fact (documented at `test_info_elevated_programming_vcc_warns` in this file) is that `result.output` is always `''` for logging-based output under pytest, because pytest's own root log handler suppresses the `logging.lastResort` stderr fallback `CliRunner` would otherwise pick up. `test_erase_blank_check_prints_exactly_one_line_on_a_failed_check` therefore gives the mocked `check_eprom_blank` a `side_effect` that reproduces the real method's single `logger.error(...)` call and asserts `len(caplog.records) == 1` — proving the CLI layer adds no second line on top of the engine's own, without re-testing `check_eprom_blank`'s own message shape (already covered in `tests/test_eprom_operations.py`).

## Deviations from Plan

None — plan executed exactly as written, both tasks. (See "Issues Encountered" below for a verify-script scoping note that required no code or plan change.)

## Issues Encountered

**Task 1's literal `<verify>` structural-check command over-captures unrelated commands.** The plan's own automated check:

```bash
.venv311/bin/python -c "...i=s.index('def erase('); body=s[i:i+6000]; assert 'sys.exit(0 if ok else 1)' not in body, ..."
```

uses a fixed 6000-character window from `def erase(`. Measured against the post-task-1 file, that window extends roughly 2200 characters past the *next* command (`id`) and sweeps in several unrelated commands (`id`, `vpe`, and others) that legitimately use the identical `sys.exit(0 if ok else 1)` idiom for their own bool-to-exit mapping — a pattern used at 14 sites total in this file, none of them `erase`. Run verbatim, the check fails with the stated assertion message even though `erase`'s own body no longer contains that literal.

Re-ran the same check scoped to `def erase( ... )` up to the next `@cli.command` marker (properly bounding the window to just the `erase` function) — all three assertions pass:

```
erase handler wired to the host engine (properly-scoped window: def erase( .. next @cli.command)
```

This is a scoping defect in the plan's verify script, not a defect in the implementation or a reason to alter the plan text. No code change was made in response; the properly-scoped re-run is the authoritative confirmation that acceptance criterion 5 ("`erase`'s body contains `check_eprom_blank` and does not contain `sys.exit(0 if ok else 1)`") holds.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **This plan is the precondition for plans 02-07's firmware sweep.** The host now owns the erase-end blank-check capability through `check_eprom_blank`, so `eprom.cpp:52-54`'s `firestarter_operation_end = mem_util_blank_check` assignment (FWBLANK-02) can be deleted in a later plan without leaving `erase -b` silently inert on the UV family.
- **Phase 206 (SESS-01) inherits a measured session-cost obligation**: `erase -b` now opens a second port (the erase, then the check), adding the derived per-open cost from `203-SESSION-COST.md` (Uno-class 2.518 s / Leonardo-class 2.607 s) to `erase -b` specifically. Not measured fresh in this plan — cited from Phase 203's existing measurement, as `205-RESEARCH.md` directs.
- **Phase 207 (REL-04) owes two wiki obligations filed by this plan**: the new 0/1/2 exit contract for `erase -b` (D-02), and the `-s`/`-b` refusal (OQ-1) — both are one-way, published CLI-contract changes.
- No blockers. No branch in any of the three repositories touched `beta` during this plan.

## Self-Check: PASSED

- `firestarter_app/firestarter/cli_handlers.py` — FOUND
- `firestarter_app/tests/test_cli_handlers.py` — FOUND
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` — FOUND
- `.planning/phases/205-the-pre-flights-leave-the-firmware/205-01-SUMMARY.md` — FOUND
- Commit `9006258` (Task 1) — FOUND in `firestarter_app` history
- Commit `55859f6` (Task 2) — FOUND in `firestarter_app` history
- All `<acceptance_criteria>` re-verified: 13/13 erase-tagged legs pass, `test_help_erase` snapshot matches with 0 generated, whole host suite 2318 passed (baseline 2309 + 9 new legs), `ruff check`/`ruff format --check` clean, `mypy firestarter/cli_handlers.py` clean.

---
*Phase: 205-the-pre-flights-leave-the-firmware*
*Completed: 2026-09-22*
</content>
