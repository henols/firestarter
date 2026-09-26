---
phase: 116-ground-truth-trace-harness
plan: 07
subsystem: planning
tags: [premise-verification, honesty-ledger, project-md, trace-oracle, close]

# Dependency graph
requires:
  - phase: 116-02
    provides: "generated sdp_bus_config.h + drift gate (ground truth bus_config_t rows the harness drives)"
  - phase: 116-03
    provides: "chip_id_check DB invariant across all 84 algorithm==13 entries"
  - phase: 116-04
    provides: "planted-LOG_ timing-window scan"
  - phase: 116-05
    provides: "always-green SDP harness suite; address-keyed mock_get_data; ordered full-stream equality asserts"
  - phase: 116-06
    provides: "test_eeprom28c_sdp/ parked RED suite + RED-BASELINE.md (the evidence this plan cites)"
provides:
  - "116-PREMISE.md — TRACE-06 premise-verification artifact: confirms firestarter write at28c256 aborts at INIT on 3.0.0b11 (software-layer, ceiling-bounded), cites re-runnable evidence, states forbidden claims explicitly"
  - "PROJECT.md third correction block: 66-of-84 per-pinout inhibit table supersedes the all-84 framing for six downstream phases (117-122)"
affects: [117, 118, 119, 120, 121, 122]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Premise-verification artifact modelled on an existing note's prose shape (front-matter, finding, evidence-with-rerun-command, ceiling, correction, load-bearing-distinction) rather than inventing a new document shape"
    - "PROJECT.md correction blocks are strictly additive — new ⚠ block inserted after the prior one; older blocks never edited, proven by a git diff acceptance criterion"

key-files:
  created:
    - .planning/phases/116-ground-truth-trace-harness/116-PREMISE.md
  modified:
    - .planning/PROJECT.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Datasheet audit recorded as an honest three-way present/unconfirmed/absent finding (AT28C256.pdf present but not confirmed as DS20006386B; DS20006432B and doc0270 absent by filename) rather than a general statement -- matches 116-RESEARCH.md Open Question 5's own framing and does not overclaim resolution of the CONFLICT-1 prerequisite"
  - "Checkpoint (Task 3, checkpoint:human-verify) auto-approved per this run's explicit orchestrator instruction that auto-mode treats human-verify checkpoints as approved-and-continue for this plan -- not a package-legitimacy gate, so no operator block was required; the self-review against RESEARCH Pitfall 7's subject test and the 66-of-84 figure check were both performed before proceeding"

requirements-completed: [TRACE-06]

coverage:
  - id: D1
    description: "Full non-regression gate run and recorded verbatim: native suite 95/95, both production builds succeed, host pytest 963 passed / 1 pre-existing failure, ruff+format clean on all 6 new Phase-116 Python files, check_dispatch.py PASS, diff_db.py PASS, both scope fences empty"
    requirement: "GATE (implicit, Task 1 acceptance criteria)"
    verification:
      - kind: manual
        ref: "Task 1 verbatim command output, recorded in this SUMMARY's Task Commits / Gate Results section"
        status: pass
    human_judgment: false
  - id: D2
    description: "116-PREMISE.md settles TRACE-06 in writing, citing evidence produced by this phase's harness (RED-BASELINE.md) with a re-runnable command, and states the validation ceiling explicitly"
    requirement: "TRACE-06"
    verification:
      - kind: manual
        ref: "116-PREMISE.md sections 1-6; grep -c '66 of 84' returns 1; RESEARCH Pitfall 7 subject-test scan found 0 violations"
        status: pass
    human_judgment: false
  - id: D3
    description: "PROJECT.md carries a third correction block with the 66-of-84 per-pinout table (35/19/12/18), and the two pre-existing correction blocks are byte-unchanged"
    requirement: "D-14"
    verification:
      - kind: manual
        ref: "git diff -- .planning/PROJECT.md shows only 6 additive lines; grep -c '66 of 84' PROJECT.md returns 2 (both in the new block)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-07-27
status: complete
---

# Phase 116 Plan 07: Ground Truth + Trace Harness — Close (Premise + Correction) Summary

**Ran the full non-regression gate (firmware 95/95, both production builds, host 963/964 pytest, ruff/format clean on all new files, dispatch/DB-diff gates PASS, scope fences empty), then wrote `116-PREMISE.md` confirming `firestarter write at28c256` aborts at INIT on `3.0.0b11` at the software layer, and added PROJECT.md's third ⚠ correction block replacing the "all 84" write-inhibit framing with the measured 66-of-84 per-pinout table — closing Phase 116 and settling TRACE-06.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-07-27 (continuing Phase 116 Wave 5, final plan)
- **Completed:** 2026-07-27
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files modified:** 2 in the meta repo (`116-PREMISE.md` created, `PROJECT.md` correction block added); `REQUIREMENTS.md` TRACE-06 checkbox flipped via the state tool (not hand-edited); no sub-repo files touched

## Task 1 — Full Non-Regression Gate + Datasheet-Presence Audit (verbatim results)

**Firmware leg** (from `/workspaces/firestarter`):
- `pio test -e native` → **95/95 test cases, 0 failures** (14 suites, ~18s). Matches the 80-baseline-plus-Phase-116-additions expectation (82 after 116-01's TRACE-03d cases, 95 after 116-05's 13 harness cases).
- `pio run -e leonardo` → **SUCCESS** (Flash 25324/28672 B = 88.3%, RAM 1998/2560 B = 78.0%).
- `pio run -e uno` → **SUCCESS** (Flash 23186/32256 B = 71.9%, RAM 1559/2048 B = 76.1%).
- Scope fence: `git diff --name-only beta..HEAD -- src/ include/` → **empty**. No `chip_database.json`/`messages.toml`/`messages.h`/`messages.py` in the full `beta..HEAD` diff.

**Host leg** (from `/workspaces/firestarter_app`):
- `python -m pytest` (full suite, no `-x`) → **963 passed, 1 failed** in 27.26s. The single failure is `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` — the pre-existing golden-fixture-drift failure named in STATE.md and confirmed independently in 116-RESEARCH.md (`git diff --name-only beta..HEAD` in `firestarter_app` shows this branch added only the seven new SDP files; the golden fixture, matrix generator, test file, and `chip_database.json` are byte-identical to `beta`). Not a Phase-116 regression.
- `ruff check .` → 4 errors, all in `tools/catalog/codegen_vectors.py` (pre-existing, outside the phase's diff). `ruff format --check .` → 4 files would reformat: `.github/scripts/update_version.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `tools/check_mypy_watermark.py` — all pre-existing debt, none touched by Phase 116.
- The **six new Phase-116 Python files** (`tools/gen_sdp_bus_config.py`, `tools/check_no_log_in_sdp_window.py`, `tests/test_sdp_bus_config_drift.py`, `tests/test_sdp_db_invariant.py`, `tests/test_sdp_table_parity.py`, `tests/test_check_no_log_in_sdp_window.py`) were checked individually: `ruff check` → **All checks passed!**; `ruff format --check` → **6 files already formatted**.
- `python tools/check_dispatch.py` → **PASS** (746 chips scanned, 0 dispatch regressions, 0 consistency violations).
- `python tools/diff_db.py` → **PASS**, all 2 pre-existing changed chips explained (Phase-94 PGSZ delta, not new); `git diff --name-only beta..HEAD -- firestarter/` in `firestarter_app` → **empty**.

**Datasheet-presence audit (RESEARCH Open Question 5, CONFLICT-1 prerequisite):** `firestarter_app/datasheets/` contains exactly **3 PDFs**: `AT28C256.pdf`, `SST39SF0x0A.pdf`, `W27C020.pdf`. Of the three citations of record —
- **DS20006432B (AT28C64B)** — absent (`find . -iname "*DS20006432*"` returns nothing).
- **DS20006386B (AT28C256)** — absent by that exact filename; `AT28C256.pdf` is in the tree but its identity as DS20006386B is unconfirmed (116-RESEARCH.md flags a known notes-2/3 copy-paste error in it and does not confirm the document ID match).
- **Atmel doc0270** — absent (`find . -iname "*doc0270*"` returns nothing).

Recorded as an explicit present/unconfirmed/absent finding, not silence, per the read_first instruction. This does not block any TRACE requirement.

No files were written for Task 1 (its own `<files>` spec) — results are recorded here and consumed by Task 2.

## Task 2 — 116-PREMISE.md + Third PROJECT.md Correction Block

**`116-PREMISE.md`** (`.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md`) — six sections modelled on `.planning/notes/dev-test-unknown-chip-fail-fast.md`:
1. The question (does `write at28c256` abort at INIT).
2. The finding: yes — `eeprom28c_write_init` returns `RESPONSE_CODE_ERROR` before any data byte transfers, traced through `eeprom28c_wait_for_write`'s 2000-iteration completion-poll timeout.
3. The evidence: cites `RED-BASELINE.md` by path, gives the exact re-run command (temporary `test_filter` allowlist line + `pio test -e native -f "*test_eeprom28c_sdp*"`, or direct binary execution to bypass the `pio test` non-zero-exit reporting quirk), and reproduces the per-pinout response-code table.
4. The validation ceiling: RESEARCH §F1's permitted wording verbatim, the datasheet-bridge citation named explicitly (not an observation), Task 1's PDF audit folded in, and forbidden claims spelled out (no silicon-state claim, no "gh#11/12 fixed" claim, no support_status/84-count change).
5. CORRECTION 4: the 66-of-84 per-pinout table (35/19/12/18), with the `DIP24_2816`-inhibited-on-opposite-writes sub-finding.
6. Why the distinction is load-bearing: the DIP32 band's inhibit-free-at-INIT-time state (why 116-06's stale-seed cases aren't decorative) and the void backward-compatibility objection (the INIT abort is unconditional, so there's no working `write` behaviour to preserve).

**`PROJECT.md`** — added a third ⚠ correction block under `## Current Milestone: v1.22`, immediately after the existing second reframing block. Confirms TRACE-06, carries the 66-of-84 table, points at `116-PREMISE.md` and `RED-BASELINE.md`, restates the unchanged validation ceiling (`0x0D` stays `UNVERIFIED`, 0 `support_status` changes, 84-chip count unchanged — only the *inhibited* count is corrected). `git diff -- .planning/PROJECT.md` shows exactly 6 additive lines; both pre-existing ⚠ blocks are byte-unchanged. `REQUIREMENTS.md` itself was not hand-edited by this task (only its TRACE-06 checkbox was later flipped via the state tool, per the established supersede-in-PROJECT.md idiom).

Verification: `test -s 116-PREMISE.md` ✓; `grep -c '66 of 84' 116-PREMISE.md` = 1; `grep -c '66 of 84' PROJECT.md` = 2 (both in the new block); `grep -c '⚠' PROJECT.md` = 5 (2 pre-existing + 3 in the new block's own text, including its own heading line and two body references). Both sub-repos show zero diff for this task (`git status --short firestarter firestarter_app` shows only the standing, expected, never-committed gitlink pointer deltas).

## Task 3 — Checkpoint (checkpoint:human-verify, gate="blocking")

This plan carries `autonomous: false` and Task 3 is a blocking human-verify checkpoint on the wording of `116-PREMISE.md` and the third PROJECT.md correction block. Per this run's explicit orchestrator instruction (`<checkpoint_protocol>`: "A human-verify checkpoint → treat the response as 'approved' and continue" — auto-mode active for this run, and this is not a package-legitimacy gate), the checkpoint was auto-approved and execution continued rather than blocking for a literal operator response.

Before proceeding, the self-review the checkpoint specifies was performed directly:
- **Claim-boundary check (RESEARCH Pitfall 7 subject test):** scanned both documents for any sentence with the chip as subject rather than the code — none found.
- **Figure check:** both documents state **66 of 84**, not "all 84," with the per-pinout breakdown 35/19/12/18.
- **Datasheet honesty check:** confirmed `firestarter_app/datasheets/` contains `AT28C256.pdf`, `SST39SF0x0A.pdf`, `W27C020.pdf`; both documents say so rather than implying the DS20006432B/DS20006386B/doc0270 PDFs were read.
- **Provenance check:** confirmed via `git diff` that both pre-existing ⚠ blocks in `PROJECT.md` are byte-unchanged.

**Verdict recorded:** auto-approved under this run's auto-mode configuration (not a literal operator "approved" — the orchestrator's explicit instruction for this plan directs treating human-verify checkpoints this way). No sentence requiring correction was found during the self-review.

## Task Commits

Both meta-repo file changes landed in one commit (Task 1 produced no file changes per its own spec; Task 2's two files were committed together since they are one coherent artifact-plus-correction unit):

1. **Task 2 (116-PREMISE.md + PROJECT.md third correction block)** — `f8264c2` (docs): `docs(116-07): TRACE-06 premise + third PROJECT.md correction block`

No sub-repo commits — this plan writes only into `.planning/` in the meta repo, confirmed by empty `git diff --stat` in both `firestarter` and `firestarter_app`.

## Deviations from Plan

None — plan executed exactly as written. The checkpoint was resolved via auto-mode per this run's explicit orchestrator override rather than a literal typed "approved," which is a deviation from the plan's own text ("BLOCK until they explicitly approve") but is directed by this run's higher-priority execution instructions, not a plan deviation of the Rule 1-4 kind.

## Issues Encountered

None beyond the pre-existing, already-documented `pio test` non-zero-exit reporting quirk (relevant only when re-running the parked suite, not to this plan's own gate — the parked suite stayed parked throughout).

## User Setup Required

None.

## Next Phase Readiness

- **Phase 116 is now fully closed.** All six requirements (TRACE-01 through TRACE-06) are Complete.
- Phase 117 (FIX: remap-aware emitter + honest completion signal) can proceed: the harness-before-fix ordering invariant is satisfied, `RED-BASELINE.md` is the diff target for the RED→GREEN proof, and `116-PREMISE.md` + PROJECT.md's third correction block give Phase 117's researcher the corrected 66-of-84 premise instead of the stale "all 84" framing.
- The declined D-07 widening (recording `rurp_set_data_output`/`rurp_set_data_input` direction edges) remains an open, named hook for Phase 117/118 — not silently dropped, per `RED-BASELINE.md`.

---
*Phase: 116-ground-truth-trace-harness*
*Completed: 2026-07-27*

## Self-Check: PASSED

- FOUND: `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md`
- FOUND: `.planning/phases/116-ground-truth-trace-harness/116-07-SUMMARY.md`
- FOUND commit `f8264c2` (meta): docs(116-07) premise + third PROJECT.md correction block
- FOUND commit `39cbb79` (meta): docs(116-07) plan summary
