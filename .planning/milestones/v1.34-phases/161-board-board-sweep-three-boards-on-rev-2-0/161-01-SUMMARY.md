---
phase: 161-board-board-sweep-three-boards-on-rev-2-0
plan: 01
subsystem: infra
tags: [bench, rig-tooling, evidence-writer, procedure-amendment, host-only]

# Dependency graph
requires:
  - phase: 160-rig-dual-arm-build-flash-provenance-the-shared-cell-procedur
    provides: judge_wrv.py, render_evidence.py, gate_record.py, capture_provenance.py, PROCEDURE.md P-01..P-11, run_gates.sh, rig-pins.json
provides:
  - append_evidence.py — the deriving EVIDENCE.jsonl row writer (D-05), 12th rig tool
  - PROCEDURE.md Amendment 3 — per-position artifact paths + evidence-append relocation
affects: [161-02, 161-03, 161-04, 161-05, 162, 163]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Deriving evidence writer: 35 of 40 columns computed and cross-checked from a
       position's own artifacts; exactly 5 human-supplied; outcome always derived,
       never accepted as CLI input"
    - "process_position() pipeline: load (accumulate) -> validate_position() cross-checks
       (accumulate) -> human-field + duration + command checks (accumulate) -> build_row()
       pure assembly -> append_row_to_file() delegate"

key-files:
  created:
    - .planning/v1.34/tools/append_evidence.py
  modified:
    - .planning/v1.34/PROCEDURE.md

key-decisions:
  - "build_row() signature diverged from RESEARCH.md's proposal: split into validate_position()
     (accumulate-then-report cross-checks) + build_row() (pure, violation-free assembly taking
     already-derived position_id/commands/outcome) rather than a single build_row() returning
     (row, violations) — lets the selftest exercise cross-checking and assembly independently."
  - "PD-1's per-position layout (cells/<slug>/reads/<position_id>/ for written.bin+run_*.bin,
     cells/<slug>/WRV-VERDICT_<position_id>.json committed outside it) carried into both
     append_evidence.py's --wrv default and PROCEDURE.md P-07/P-09's literal command blocks,
     per the plan's own measured git check-ignore finding."
  - "board_signature/mcu cross-check and family/board label tables implemented as small local
     tool constants (T-column in RESEARCH's derivation map), not imported from probe_board.py —
     they are data this tool cross-checks a provenance field against, not a check owned by
     another tool."

requirements-completed: []

coverage:
  - id: D1
    description: "append_evidence.py derives 35/40 EVIDENCE.jsonl columns from a position's
      three source artifacts, cross-checked against IMAGE-PLAN.json and rig-pins.json, with
      outcome always derived and never accepted as input"
    verification:
      - kind: unit
        ref: "python3 .planning/v1.34/tools/append_evidence.py --selftest (3 positive + 10 named negative legs)"
        status: pass
      - kind: manual_procedural
        ref: "--dry-run against real BRINGUP-wrv artifacts reproduces the 40-key row in schema order with matching outcome=validated"
        status: pass
    human_judgment: false
  - id: D2
    description: "append_evidence.py refuses bad usage (exit 2), advertises --selftest for
      run_gates.sh discovery, and imports gate_record/render_evidence rather than
      re-implementing the not-measured regex, argv check, or JSONL append"
    verification:
      - kind: unit
        ref: "run_gates.sh full suite (12/12 tool selftests, 5/5 live gates, exit 0)"
        status: pass
      - kind: unit
        ref: "ast.parse + grep structure checks (spec_from_file_location, append_row_to_file present; stdlib-only imports)"
        status: pass
    human_judgment: false
  - id: D3
    description: "PROCEDURE.md Amendment 3 lands with four clauses; P-07/P-09/P-11 edited to
      match; arm-agnostic empty-diff render gate stays empty"
    verification:
      - kind: unit
        ref: "render_steps.py --arm control vs --arm v133 byte-identical, 11 lines"
        status: pass
      - kind: unit
        ref: "amendment content assertions (heading, clause labels, pinned SHAs/mtime, render_steps.py mention)"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-08-27
status: complete
---

# Phase 161 Plan 01: Wave 0 — Evidence Writer + Procedure Amendment 3 Summary

**append_evidence.py (12th rig tool) derives 35 of 40 EVIDENCE.jsonl columns per position from
provenance+WRV+READBACK artifacts with 10 named cross-check refusals, and PROCEDURE.md Amendment
3 keys P-07/P-09's per-position paths and moves the evidence append from P-11 into P-07/P-09.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-08-27T12:27:56Z
- **Tasks:** 3
- **Files modified:** 2 (1 new, 1 modified)

## Accomplishments
- Built `append_evidence.py`: a deriving evidence-row writer where only 5 of 40 columns are
  human-supplied (`blank_state`, `verdict`, `anomalies`, two write durations, plus an optional
  `--shield-note`); every other column is derived from the position's own three source artifacts
  and cross-checked against `bench/IMAGE-PLAN.json` and `rig-pins.json`, with a wrong-position
  field transcription refused by name (the exact failure `gate_record.py` cannot structurally
  see).
- `--selftest` carries 3 positive legs + 10 named negative legs, all on-disk fixtures in a
  tempfile directory, accumulate-then-report — every negative leg asserts on the named reason,
  not merely a non-zero return.
- `outcome` is always derived from `wrv.sha_verdict_judged`/`verdict_disagreement`/
  `size_violations`, never accepted as a CLI input.
- Delegated, never re-implemented: `gate_record.py`'s `_NOT_MEASURED_RE` (via
  `check_required_fields`) and `check_commands`; `render_evidence.py`'s
  `append_row_to_file()` for the write itself — reached through the `importlib.util
  .spec_from_file_location` sibling idiom.
- Landed `PROCEDURE.md` Amendment 3 (four clauses): (1) evidence-append moves from `P-11` to
  `P-07`/`P-09`, paired with an immediate `render_evidence.py` re-render, `P-11` becomes a
  completeness assertion; (2) `P-11` gains a cell-agnostic leave-state declaration
  (board/port/arm/chip/pot/shield); (3) `P-07`/`P-09`'s `--output-dir`/`--reads`/`written.bin`/
  verdict paths become `$POSITION_ID`-keyed under `$CELL_DIR/reads/$POSITION_ID/`, verdict file
  renamed `WRV-VERDICT_$POSITION_ID.json`; (4) `P-11`'s `~/.firestarter` teardown assertion
  restated to "unchanged from the recorded baseline" with the baseline pinned inline.
- Re-confirmed the per-cell gate: `run_gates.sh` reports 12/12 tool selftests (up from 11/11)
  and 5/5 live gates, exit 0, measured directly (never through a pipe).

## Task Commits

Each task was committed atomically:

1. **Task 1: Build append_evidence.py** - `b46ecb98` (feat)
2. **Task 2: Write PROCEDURE.md Amendment 3** - `419a6d64` (docs, combined with Task 3's
   verification-and-commit step — see note below)
3. **Task 3: Re-confirm the per-cell gate at 12/12 and commit Wave 0** - verification only;
   the actual commit is `419a6d64` above (Task 2's file was still uncommitted when Task 3's
   verification ran, so both landed in one commit rather than two identical-content commits)

**Plan metadata:** _pending — this SUMMARY's own commit_

_Note on commit count: the plan's Task 3 acceptance criterion asks for "exactly two changed
paths" across the plan's commits. Per this executor's per-task atomic-commit protocol, Task 1's
deliverable (`append_evidence.py`) was committed immediately after Task 1 completed
verification; PROCEDURE.md was committed once, after Task 2's edits were verified and Task 3's
full-suite re-confirmation passed. Across the plan's two commits, exactly the two files named in
`files_modified` were touched — no `bench/` artifact was committed, per the plan's own
instruction that no position exists yet._

## Files Created/Modified
- `.planning/v1.34/tools/append_evidence.py` - the deriving evidence-row writer (D-05), 41 KB,
  `RECORD_KEYS` (40 columns), `validate_position()`, `build_row()`, `process_position()`,
  `build_argparser()`, `main()`, `_run_selftest()`
- `.planning/v1.34/PROCEDURE.md` - Amendment 3 appended; `P-07`, `P-09`, `P-11` bodies edited

## Decisions Made
- **`build_row()` signature diverged from RESEARCH.md's proposal.** RESEARCH proposed
  `build_row(provenance, wrv, readback, image_plan_row, pins, human) -> (row, violations)`.
  This plan split that into `validate_position(position_id, provenance, wrv, readback,
  image_plan_row, pins) -> list[str]` (accumulate-then-report cross-checks) and
  `build_row(provenance, wrv, readback, image_plan_row, pins, human, position_id, commands,
  outcome) -> dict` (pure, violation-free assembly of the already-derived row). Rationale:
  lets the selftest exercise cross-checking (Negative 1-6, 8-10) and pure assembly (Positive
  1-3, Negative 7) independently, and keeps `build_row()` a true pure function with no
  side-channel violation-accumulation state.
- **`_MCU_SIGNATURE` and `_BOARD_LABEL`/`_CHIP_LABEL` are local tool constants**, not imported
  from `probe_board.py`. These are small, stable 3-entry tables this tool cross-checks a
  provenance *field* against (RESEARCH's "T" derivation-map column), not a check another tool
  owns — distinguished from the `_NOT_MEASURED_RE`/`check_commands`/`append_row_to_file`
  imports, which are genuinely owned elsewhere and are imported per the plan's explicit
  prohibition against re-deriving them.
- **`op` and `board`/`family`/`shield` derivation templates** were designed fresh (RESEARCH gave
  a formula, not literal historical text — the four bring-up rows' hand-written prose predates
  this tool). The `--dry-run` acceptance criterion only requires `outcome` to match the
  recorded `BRINGUP-wrv` row, which it does; the four templated fields will differ from that
  hand-written historical row's prose, which is expected and does not affect any check.

## Deviations from Plan

None — plan executed as written, with one bug caught and fixed during self-verification before
any commit (not against the plan's own text, but a fixture bug I introduced while writing the
selftest):

### Auto-fixed Issues

**1. [Rule 1 - Bug] Selftest base fixture omitted the `chip` field**
- **Found during:** Task 1, first `--selftest` run (before any commit)
- **Issue:** `_BASE_PROVENANCE` fixture had no `"chip"` key, so `build_row()`'s `chip_cfg =
  pins["chips"][chip]` lookup resolved `chip=None`, producing a spurious
  `rig-pins.json has no chips entry for chip None` violation on every leg.
- **Fix:** Added `"chip": "w27c512"` to `_BASE_PROVENANCE`.
- **Files modified:** `.planning/v1.34/tools/append_evidence.py` (pre-commit)
- **Verification:** Re-ran `--selftest`; all 13 legs (3 positive + 10 negative) passed.
- **Committed in:** `b46ecb98` (Task 1 commit — fixed before the file was ever committed)

**2. [Rule 1 - Bug] `--dry-run` reading `--verdict-file -` and `--anomalies-file -` both from
   stdin**
- **Found during:** Task 1, manual acceptance-criterion verification against real
  `BRINGUP-wrv` artifacts
- **Issue:** Not a tool bug — a test-invocation error. Passing `-` (stdin) for both
  `--verdict-file` and `--anomalies-file` in the same shell invocation only lets the first
  read consume stdin; the second reads an already-exhausted stream, producing an empty
  string.
- **Fix:** Used two separate real files (`verdict.txt`, `anomalies.txt`) extracted from the
  existing `BRINGUP-wrv` `EVIDENCE.jsonl` row for the manual verification, rather than `-`
  for both.
- **Files modified:** none (test-harness-only correction)
- **Verification:** `--dry-run` succeeded, printed a 40-key row in schema order with
  `outcome=validated` matching the recorded row.

---

**Total deviations:** 1 real fixture bug auto-fixed (Rule 1, pre-commit); 1 test-invocation
correction (not a code defect).
**Impact on plan:** No scope creep — both were caught and resolved during the plan's own
`--selftest`/acceptance-criteria verification, before any commit landed.

## Issues Encountered
None beyond the deviations above.

## Known Stubs
None. Every field `append_evidence.py` writes is either derived from real artifact data or
comes from a required CLI argument; no hardcoded empty value flows to the row.

## Threat Flags
None. All five threat register entries (T-161-01..05, T-161-SC) from the plan's own
`<threat_model>` are addressed by this plan's design (delegation to `gate_record`/
`render_evidence`, PD-1's gitignore-safe layout, accumulate-then-report cross-checks) — no new
security-relevant surface was introduced beyond what the threat model already names.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `append_evidence.py` and `PROCEDURE.md` Amendment 3 are the Wave 0 mechanism every one of
  Phase 161's real sweep cells (161-02..05) needs before they can run — both are landed and
  gated green.
- No `EVIDENCE.jsonl` row was added and no `BOARD-01..04` requirement was marked complete by
  this plan, per the plan's own instruction — every one of those four is closed by a cell plan
  that produces real positions.
- The rig is left exactly as Phase 160 left it (no device touched, no chip operation performed).

---
*Phase: 161-board-board-sweep-three-boards-on-rev-2-0*
*Completed: 2026-08-27*

## Self-Check: PASSED
