---
phase: 121-dev-test-fix-gates-docs-redesign
plan: 14
subsystem: testing
tags: [non-regression, ci-parity, uv-venv, ruff, requirements-closure, audit]

# Dependency graph
requires:
  - phase: 121-13
    provides: GATE-02 closed (all eight docs corrected), the phase's last content-bearing plan
provides:
  - "121-NONREGRESSION.md: the phase's eight-section audit record, re-run at the final commit"
  - "GATE-03 closed: full non-regression sweep green under both the devcontainer interpreter and a uv-provisioned CI-parity Python 3.11 venv"
  - "DEVTEST-01/02/03/04 and GATE-01 independently re-verified against the live tree and ticked (all five had been left Pending by their landing plans per this phase's requirement-ownership lock)"
affects: ["Phase 122 (closeout builds its honesty ledger on this document)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "uv-provisioned throwaway venv for CI-parity pytest/ruff, cache/install dirs redirected under /tmp (default cache location not writable)"
    - "Live dependency-resolution proof of impossibility (uv venv --python 3.9 + uv pip install, capturing uv's own conflict explanation) in place of a skipped/asserted claim"

key-files:
  created:
    - .planning/phases/121-dev-test-fix-gates-docs-redesign/121-NONREGRESSION.md
  modified:
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Ticked five Pending rows beyond GATE-03 (DEVTEST-01/02/03/04, GATE-01), per the orchestrator's explicit resolved-ambiguity scope: the plan's own Task-2 text ('tick GATE-03 only') predates commit 2492154's deliberate revert of plan 121-08's premature DEVTEST-01 tick, whose surviving REQUIREMENTS.md prose explicitly delegates re-closure to this plan"
  - "Each of the five additionally-ticked rows was independently re-verified against the live tree (a fresh command or assertion run in this session), never against the landing plan's own SUMMARY claim -- per the dispatch's explicit anti-pattern warning"
  - "DEVTEST-05, DEVTEST-06 and GATE-02 (already Complete before this plan) left byte-intact -- confirmed via git diff that only the six rows above moved"
  - "diff_db.py identity recorded explicitly as 'still exactly 2 explained changes, not zero' in both REQUIREMENTS.md's GATE-03 traceability sentence and 121-NONREGRESSION.md, so no future reader misreads the gate as expecting a bare zero-diff"
  - "The devcontainer's own globally-installed ruff has drifted to 0.16.0 (matching the CI-resolved version) since 121-RESEARCH.md recorded a 0.15.20/0.16.0 divergence -- recorded as a finding rather than silently noting 'ruff clean' without the version"

requirements-completed: [GATE-03, DEVTEST-01, DEVTEST-02, DEVTEST-03, DEVTEST-04, GATE-01]

coverage:
  - id: D1
    description: "Full nine-row cross-repo non-regression set re-run verbatim at the phase's final commit (firestarter@48c36e5, firestarter_app@c3c9424), with actual command output recorded, not trusted from any prior plan's SUMMARY"
    requirement: "GATE-03"
    verification:
      - kind: other
        ref: "pio test -e native / native_nodevtools -- 141/141 both, identical"
        status: pass
      - kind: other
        ref: "python3 -m pytest tests/ (devcontainer 3.12.13 AND /tmp/venv311 Python 3.11.15) -- 1134 passed, 0 failed, both"
        status: pass
      - kind: other
        ref: "/tmp/venv311/bin/ruff check/format --check (0.16.0, CI-resolved) -- 4 pre-existing findings, confirmed 0 in this phase's diff via git diff --stat 96e0622..HEAD"
        status: pass
      - kind: other
        ref: "python3 tools/diff_db.py -- PASS: all 2 changed chips explained (0 new, 0 removed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "py3.9 pytest impossibility recorded with its cause (syrupy>=5.0 requires >=3.10), reproduced live rather than asserted from memory; ruff/mypy config-pinning and the packaging classifier recorded as the actual basis for the milestone's py3.9 claim"
    requirement: "GATE-03"
    verification:
      - kind: other
        ref: "uv venv --python 3.9 /tmp/venv39 && uv pip install -e '.[test]' -- unsatisfiable, uv's own conflict explanation captured verbatim"
        status: pass
    human_judgment: false
  - id: D3
    description: "Second audit-matrix regeneration proven byte-identical to the committed golden (cmp exit 0, both 186034 bytes), confirming RESEARCH C-2's no-op prediction rather than silently re-regenerating"
    requirement: "GATE-03"
    verification:
      - kind: other
        ref: "generate_matrix() re-run against the committed ledger, cmp against tests/golden/v1.3-COVERAGE-MATRIX.md -- byte-identical; git status --porcelain tests/golden/ empty"
        status: pass
    human_judgment: false
  - id: D4
    description: "All nine requirement rows independently re-verified against the live tree (fresh command/assertion per row, not the landing plan's own SUMMARY claim); six rows ticked (GATE-03, DEVTEST-01..04, GATE-01), three left untouched (DEVTEST-05, DEVTEST-06, GATE-02), three left unticked (CLOSE-01/02/03)"
    requirement: "DEVTEST-01, DEVTEST-02, DEVTEST-03, DEVTEST-04, GATE-01"
    verification:
      - kind: other
        ref: "derive_plan('AT28C256', db, write_scope='full') erase step: supported=False, reason names 0x0D/28C-family, never FLAG_CAN_ERASE; tests/test_chip_test.py -k devtest01 (2 tests) pass"
        status: pass
      - kind: other
        ref: "inspect.signature(cli_handlers.dev_test.callback) == (app, chip); each of --destructive/--output-dir/-y/--yes/--submit errors 'No such option' exit 2"
        status: pass
      - kind: other
        ref: "chip_test.is_uv_eprom coverage measured 301/301 against the live 746-entry chip_database.json (old algorithm==0x0B proxy: 32/301)"
        status: pass
      - kind: other
        ref: "OP_WRITE_PARTIAL confirmed present in the live _DESTRUCTIVE_OPS frozenset; tests/test_dev_test_cmd.py -k TestUVOnlyStopAndAsk (4 legs) pass"
        status: pass
      - kind: other
        ref: "tools/check_sdp_capability_invariants.py: exit 0 on real source; exit 1 on each of the two planted-violation fixtures via FIRESTARTER_SDP_CAPABILITY_SRC"
        status: pass
    human_judgment: false
  - id: D5
    description: "Validation-ceiling review performed sentence by sentence over 121-NONREGRESSION.md; zero affirmative AT28C-silicon claims, 0x0D stays UNVERIFIED, zero support_status changes, 84-chip count unchanged"
    verification:
      - kind: other
        ref: "121-NONREGRESSION.md ## Validation-Ceiling Review section"
        status: pass
    human_judgment: false

# Metrics
duration: ~110min
completed: 2026-07-29
status: complete
---

# Phase 121 Plan 14: GATE-03 Non-Regression Close Summary

**Full nine-row cross-repo sweep re-run verbatim at the phase's final commit under both the devcontainer interpreter and a `uv`-provisioned CI-parity Python 3.11 venv (1134 passed / 0 failed, both); GATE-03 plus five independently-re-verified Pending rows (DEVTEST-01..04, GATE-01) ticked in `REQUIREMENTS.md`; `121-NONREGRESSION.md` written in the established eight-section shape with a clean validation-ceiling review.**

## Performance

- **Duration:** ~110 min
- **Completed:** 2026-07-29
- **Tasks:** 3/3
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments

- Provisioned a CI-parity Python 3.11.15 venv via `uv` (cache/install dirs redirected under `/tmp`; the default cache location is not writable here), resolving `ruff 0.16.0` — the version CI actually gets from the unpinned `ruff>=0.15.14` constraint.
- Re-ran the full nine-row cross-repo gate table from `119-NONREGRESSION.md` §CORRECTION-4 plus the complete host/firmware gate matrix at the phase's final commit (`firestarter@48c36e5`, `firestarter_app@c3c9424`): both native environments 141/141 identical, `pio run` 3/3 unchanged from Phase 119's final measurement (confirming Plan 121-12's zero-firmware-diff finding independently), host pytest 1134 passed / 0 failed on both the devcontainer interpreter (Python 3.12.13) and the `uv`-provisioned parity venv, coverage 81.86%, mypy watermark 1 error (34 below the 35 watermark).
- Confirmed the four pre-existing ruff findings (across `tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`, `tools/check_mypy_watermark.py`) are genuinely outside this phase's diff via `git diff --stat 96e0622..HEAD` on each file (empty) — not merely restated from a prior sweep's claim.
- Reproduced the py3.9 pytest impossibility live: provisioned a real Python 3.9.25 via `uv` and ran `uv pip install -e '.[test]'` against it, capturing `uv`'s own unsatisfiable-dependency explanation (`syrupy>=5.0` requires Python ≥3.10) rather than asserting the claim from research notes.
- Independently re-derived and recorded that `diff_db.py`'s identity means "still exactly 2 explained `PGSZ_PAGE_SIZE` changes, 0 new, 0 removed" — not a bare zero-diff.
- Re-ran the second audit-matrix golden regeneration and proved it byte-identical to the committed golden (`cmp` exit 0, both 186034 bytes) — confirming RESEARCH C-2's no-op prediction live rather than trusting Plan 121-01's own record.
- Independently re-verified all nine requirement rows against the live tree — a fresh command or assertion per row, never the landing plan's own SUMMARY claim — and found all nine hold.
- Resolved the stale "Tick GATE-03 only" instruction in the plan's own Task-2 text (which predates commit `2492154`'s deliberate revert of Plan 121-08's premature `DEVTEST-01` tick) per the orchestrator's explicit dispatch-time scope: ticked `GATE-03` plus `DEVTEST-01`, `DEVTEST-02`, `DEVTEST-03`, `DEVTEST-04` and `GATE-01` — each independently verified as satisfied, each with a preserved-and-extended traceability sentence (never a rewrite of existing prose), and recorded the stale-instruction discrepancy itself in `121-NONREGRESSION.md`'s corrections section.
- Confirmed via `git diff .planning/REQUIREMENTS.md` that no row beyond those six moved: `DEVTEST-05`, `DEVTEST-06` and `GATE-02` (already Complete) are byte-intact; `CLOSE-01`/`02`/`03` remain unticked.
- Wrote `121-NONREGRESSION.md` in the established eight-section shape (mirroring `119-`/`120-NONREGRESSION.md`), including the mandatory both-directions cross-repo rename check, the three recorded reversals, and a sentence-by-sentence validation-ceiling review finding zero affirmative AT28C-silicon claims.

## Task Commits

Each task was committed atomically in the meta repo:

1. **Task 1: Re-run every gate row at the final commit under CI parity** — `7bc36c1` (docs)
2. **Task 2: Prove the second audit-matrix regeneration is a no-op and re-verify every requirement row** — `ebd1000` (docs)
3. **Task 3: Complete 121-NONREGRESSION.md in the established eight-section shape** — `73d68a1` (docs)

**Plan metadata:** this SUMMARY.md commit (see final commit).

## Files Created/Modified

- `.planning/phases/121-dev-test-fix-gates-docs-redesign/121-NONREGRESSION.md` — the phase's eight-section audit record: precise claims, the command-by-gate matrix, golden/generated-artifact identity, the nine-row cross-repo table, corrections C-1..C-9 + D-06/D-17, the three reversals, known-and-explained conditions, deliberately-not-taken options, and a validation-ceiling review.
- `.planning/REQUIREMENTS.md` — `GATE-03`, `DEVTEST-01`, `DEVTEST-02`, `DEVTEST-03`, `DEVTEST-04` and `GATE-01` ticked with traceability sentences naming Plan 121-14 and the independent live re-verification performed; traceability table Status column updated for the same six rows; every other row (including `DEVTEST-05`/`06`/`GATE-02` already-Complete rows and the three `CLOSE-NN` Pending rows) left byte-intact.

## Decisions Made

- Followed the orchestrator's explicit resolved-ambiguity instruction over the plan file's own (stale) "Tick GATE-03 only" Task-2 text: ticked five additional Pending rows, each independently re-verified against the live tree in this session before being ticked, and recorded the stale-instruction discrepancy in `121-NONREGRESSION.md` so no later reader treats the tick as unauthorized.
- Reported the ruff verdict against the CI-resolved version (0.16.0) throughout, and separately noted that the devcontainer's own globally-installed ruff has since drifted to 0.16.0 as well — the 0.15.20/0.16.0 divergence RESEARCH originally measured is no longer reproducible in this environment, but the plan's mandate to report the CI-resolved version was honored regardless.
- Treated `_MULTI_RUN_OPS` (made live rather than deleted, per an earlier plan's deliberate deviation from the RESEARCH recommendation) and `locked_destructive` (kept as a genuine three-valued API rather than pruned) as findings to record in §8, not defects to fix — neither is this plan's scope to alter.

## Deviations from Plan

None from Rules 1-4 — no bug fix, missing-functionality addition, blocking-issue fix, or architectural change was required. The one process-level deviation (ticking five rows beyond the plan text's literal "GATE-03 only" instruction) was an explicit, pre-authorized resolution of a stale plan/live-tree conflict communicated in the dispatch prompt, not a self-directed deviation — documented above and in `121-NONREGRESSION.md`'s corrections section per the dispatch's own instruction to record it.

## Issues Encountered

- **pytest 9.1.1's final summary line is sometimes absent from a captured multi-file run.** Observed inconsistently across otherwise-identical `pytest tests/ -q --tb=no` invocations in this session (present in some captures, absent in others of the exact same command). Root cause not conclusively isolated (not `-p no:cacheprovider`, not `-q` alone — both were tested in isolation and did not reproduce it deterministically). Worked around by writing output to a file and reading the tail directly, or by using `--tb=short` without `-q`, both of which reliably showed the "`N passed in Xs`" line. All pass/fail counts in this SUMMARY and in `121-NONREGRESSION.md` were confirmed via a run that displayed the explicit summary line (never inferred from dot-counting alone) and cross-checked against the exit code.
- The plan's Task 1 acceptance-criteria command string chains all checks with `&&`, which would abort at the first non-zero exit (the ruff findings and mypy's 1 error, both pre-existing/within-watermark) rather than recording each row's actual output. Ran each command individually instead, matching every prior phase's own non-regression sweep discipline (`119-`/`120-NONREGRESSION.md`), so every row's exact output is recorded rather than the sweep silently stopping at the first non-zero exit.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 121 (`dev test` FIX + GATES + DOCS + REDESIGN) is fully executed: all 14 plans complete, all nine phase-owned requirement rows (`DEVTEST-01..06`, `GATE-01..03`) now read Complete, and `121-NONREGRESSION.md` is the phase's auditable record for Phase 122 to build its honesty ledger on.
- Both sub-repo working trees confirmed clean at the phase's true final commit (only the named, pre-existing, explicitly out-of-scope dirt in each: `firestarter/firestarter/` nested untracked dir in firmware; `.gitignore`/`.coverage`/`.planning/config.json`/`SECURITY.md`/`write_test_port.sh` in the host repo).
- No blockers for Phase 122. The catalog-sync CI workflow remains expected-red-until-milestone-merge (unchanged, Phase 118 pattern) — Phase 122's closeout should not read that as this phase's regression.
- `CLOSE-01`/`02`/`03` remain untouched and Pending, exactly as Phase 122's own scope requires.

---
*Phase: 121-dev-test-fix-gates-docs-redesign*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `.planning/phases/121-dev-test-fix-gates-docs-redesign/121-NONREGRESSION.md`
- FOUND: `.planning/phases/121-dev-test-fix-gates-docs-redesign/121-14-SUMMARY.md`
- FOUND: `.planning/REQUIREMENTS.md`
- FOUND (meta): `7bc36c1`, `ebd1000`, `73d68a1`, `98fe95c`
