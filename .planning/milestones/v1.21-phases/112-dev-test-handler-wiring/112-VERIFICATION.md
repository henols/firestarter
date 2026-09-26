---
phase: 112-dev-test-handler-wiring
verified: 2026-07-03T13:00:00Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 8/9
  gaps_closed:

    - "SC2 / SWEEP-05 (derive_plan non-destructive plan = id+read+blank-check only): directly reproduced live, non-mocked, this session — derive_plan('M8720'|'W27C512', db, destructive=False).steps == ['id','read','blank-check'] exactly, OP_VERIFY absent and recorded on locked_destructive as ('verify', 'destructive=False: verify omitted (D-01)'); derive_plan(..., destructive=True).steps unchanged: ['id','read','blank-check','write','verify','erase'] (verify after write, before erase). Fix commit 7a74fcc (chip_test.py), test commit b88649f (test_chip_test.py / test_dev_test_cmd.py) confirmed present in firestarter_app submodule on branch v1.21-community-chip-validation-command."
  gaps_remaining: []
  regressions: []
---

# Phase 112: `dev test` Handler Wiring Verification Report

**Phase Goal:** `@dev.command("test")` in cli_handlers.py (sibling of `dev_validate_family`) — chip arg, `--destructive`/`--output-dir` flags, non-destructive default, exit-code semantics reflecting sweep outcome; integrates the Phase 108–111 engine, address-derived pattern/fingerprint, diagnostic report, and voltage sampler into one runnable CLI surface; unit-testable via `EpromDatabase(skip_local_override=True)` + mock operator (the `validate-family` test seam).
**Verified:** 2026-07-03
**Status:** human_needed
**Re-verification:** Yes — after gap-closure plan 112-05 (SC2/SWEEP-05 verify-gate fix)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `firestarter dev test <chip>` is a registered Click subcommand (sibling of `dev validate-family`), accepting chip / `--destructive` / `--output-dir` / `-y`, running the full sweep → report flow | ✓ VERIFIED | Live: `cli.commands['dev'].commands['test']` exists; `CliRunner(['dev','test','--help'])` lists positional `CHIP` + `--destructive`/`--output-dir`/`-y,--yes`. `cli_handlers.py:1781 @dev.command(name="test")`. Unchanged by 112-05. |
| 2 | Without `--destructive` → non-destructive plan (id+read+blank-check) with Phase-109 banner intact; with `--destructive` → full plan (write/erase/verify) | ✓ VERIFIED (gap closed) | Directly reproduced this session (no mock): `derive_plan('M8720', db, destructive=False).steps` == `['id','read','blank-check']` exactly; `derive_plan('M8720', db, destructive=True).steps` == `['id','read','blank-check','write','verify','erase']` (verify after write, before erase — unchanged from pre-fix). `derive_plan('W27C512', ..., destructive=False)` also confirmed 3-step. Fix at `chip_test.py:387-398`: `OP_VERIFY` append now sits inside `if destructive:` mirroring the `OP_WRITE` block at `:382-385`; non-destructive omission recorded on `locked_destructive` as `('verify', 'destructive=False: verify omitted (D-01)')`. |
| 3 | 3-way exit code (0 clean; 1 any BAD incl. chip-ID mismatch; 2 marginal/indeterminate with no BAD; N<M non-destructive still 0) — `max` over per-verdict codes | ✓ VERIFIED | `_VERDICT_EXIT_CODES` map + `_verdict_code()` (`cli_handlers.py:1654-1665`); `sys.exit(max(_verdict_code(r.verdict) for r in results))` at `:1898` — unchanged. With the SC2 gap now closed, the non-destructive path no longer manufactures a spurious `BAD` from an unreachable verify step, so the "N<M non-destructive still 0" clause is now actually true on a healthy chip (previously it was structurally false — see closed gap). `test_non_destructive_run_never_dispatches_verify` proves exit 0 with `verify_eprom.assert_not_called()`. |
| 4 | Handler unit-testable without hardware via `EpromDatabase(skip_local_override=True)` + mock operator (CliRunner) | ✓ VERIFIED | `tests/test_dev_test_cmd.py` uses `EpromDatabase(skip_local_override=True)` + `Mock(spec=EpromOperator)` + `Mock(spec=HardwareManager)`. Targeted 5-module run (`test_dev_test_cmd.py` + `test_chip_test.py` + `test_check_devtest_orchestrator.py` + `test_provenance.py` + `test_diagnostic_report.py`) → 126 passed, 0 failed, live this session, no serial/hardware access. |
| 5 | D-04 decoupling: `chip_test.py` does NOT import `hardware.py`; `run_plan` has optional `sampler` bracketing OP_WRITE; hardware thunk built in the handler | ✓ VERIFIED | `grep -c 'import hardware\|from firestarter.hardware\|from firestarter import hardware' firestarter/chip_test.py` → 0 (re-confirmed live). Sampler bracket unchanged by 112-05 (Task 1 touched only the `derive_plan` OP_VERIFY branch, not `run_plan`/`_dispatch_multi_run`'s sampler wiring). |
| 6 | SAFE-01/02/03 prohibitions: host-only, no new firmware dispatch, no VPP-set, no `--force`, no raw wire-dict in the handler | ✓ VERIFIED | `grep -nE 'set_vpp\|enable_vpp\|write_vpp\|vpp_enable\|assert_vpp\|raise_vpp' cli_handlers.py` → 0 hits (re-confirmed). `--destructive` is `is_flag=True` only. |
| 7 | SAFE-01/02/03 AST checker scans real `cli_handlers.py`; exits 0; anti-hollow negative-fixture test proves non-zero on planted violation | ✓ VERIFIED | Live run this session: `python tools/check_devtest_orchestrator.py` → exit 0, `PASS: scanned ../firestarter/chip_test.py, ../firestarter/cli_handlers.py; 0 VPP-set, 0 raw-wire-dict, 0 --force; firmware untouched (host-only, asserted)`. `_DESTRUCTIVE_OPS` re-confirmed unchanged (`frozenset({OP_WRITE, OP_ERASE})` — `OP_VERIFY` NOT added, per 112-05's explicit prohibition); `_MULTI_RUN_OPS` re-confirmed unchanged (`frozenset({OP_WRITE, OP_ERASE, OP_VERIFY})` — verify NOT removed). |
| 8 | Every piece built in Phases 108–111 is reachable from one CLI invocation (SWEEP/PATT/RPT/VOLT/XPORT) | ✓ VERIFIED | Handler composes `derive_plan` → `run_plan(sampler=...)` → `count_applicable` → `build_db_diff` → `DiagnosticReport` → `report.render(console)` → optional dual-artifact write → `sys.exit`. Unchanged by 112-05 (source-code composition untouched outside `derive_plan`'s internal OP_VERIFY gating). |
| 9 | (112-04 gap, carried) `dev test --destructive` on a real TTY issues ZERO interactive provenance prompts; `--destructive` safety confirm (SAFE-03) still gates a destructive run | ✓ VERIFIED | `grep -rn 'prompt_provenance\|class Provenance\|SHIELD_REV_CHOICES\|_CHIP_ORIGIN_CHOICES' firestarter/` → 0 hits (re-confirmed live this session). `Confirm.ask("--destructive will sacrifice the chip...")` still present at `cli_handlers.py:1815-1817`, unchanged by 112-05. |

**Score:** 9/9 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/chip_test.py` | `derive_plan` gates `OP_VERIFY` behind `destructive`, mirroring `OP_WRITE`/`OP_ERASE`; sampler threading unchanged | ✓ VERIFIED | Read directly: lines 387-398 show the gated branch, comment explains the D-01 rationale. `_DESTRUCTIVE_OPS`/`_MULTI_RUN_OPS` (453/457) unchanged. |
| `firestarter_app/tests/test_chip_test.py` | New `test_derive_plan_verify_gated_behind_destructive`; 8 repaired tests (5 plan-named + 3 discovered by full-suite run) | ✓ VERIFIED | `pytest -k verify_gated_behind_destructive` selects + passes 1 test; full module run green (part of 98 total in the two named modules). |
| `firestarter_app/tests/test_dev_test_cmd.py` | New `test_non_destructive_run_never_dispatches_verify`, non-masking (`side_effect=AssertionError`, not `return_value`) | ✓ VERIFIED | `grep -n "verify must not run on a non-destructive plan" tests/test_dev_test_cmd.py` → hit at line 237. `pytest -k never_dispatches_verify` selects + passes. |
| `.planning/REQUIREMENTS.md` | RPT-04 reworded to auto-capture model, cites Phase 112 Plan 04, single-line bold label preserved | ✓ VERIFIED | Line 37: `- [x] **RPT-04**: Superseded by Phase 112 Plan 04 descope...` — single line, bold label intact. `grep -c "is prompted before the sweep"` → 0. `git show ba02e1b -- .planning/REQUIREMENTS.md` confirms only RPT-04's line changed (no other row touched). |
| `firestarter_app/tools/check_devtest_orchestrator.py` | SAFE-03 checker still exits 0 post-fix (no handler code changed by 112-05, re-run to prove non-regression) | ✓ VERIFIED | Live run: exit 0, PASS line names both files. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `derive_plan` | plan composition (non-destructive) | non-destructive plan = id+read+blank-check ONLY | ✓ WIRED (gap closed) | Live `derive_plan(chip, db, destructive=False).steps` == exactly `[id, read, blank-check]` for both `M8720` and `W27C512` — verify is structurally absent (not just skipped at exec time), matching D-01. |
| `derive_plan` | plan composition (destructive) | destructive plan = id+read+blank-check+write+verify+erase, verify after write / before erase | ✓ WIRED | Live `derive_plan(chip, db, destructive=True).steps` == `[id, read, blank-check, write, verify, erase]` — byte-for-byte the pre-112-05 destructive output, confirming the fix scoped correctly to only the non-destructive branch. |
| non-destructive `dev test` | `operator.verify_eprom` | `_dispatch_multi_run`'s OP_VERIFY branch | ✓ WIRED (now unreachable, as intended) | With verify absent from the non-destructive plan, `operator.verify_eprom` is structurally unreachable on that path. `test_non_destructive_run_never_dispatches_verify` proves this via `side_effect=AssertionError` + `assert_not_called()`, not just `return_value` masking. |
| `dev_test` handler | `derive_plan` | `derive_plan(chip, app.db, destructive=destructive)` | ✓ WIRED | `:1826`; unchanged by 112-05. |
| `dev_test` handler | `run_plan` (with sampler) | `run_plan(plan, app.eprom_operator, app.db, sampler=sampler)` | ✓ WIRED | `:1848`; sampler only constructed `if destructive` — unchanged. |
| SAFE-03 checker | `cli_handlers.py` / `chip_test.py` (scoped) | `_scan_target_functions` AST filter | ✓ WIRED | Live run confirms both files named in PASS line, exit 0. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `derive_plan(destructive=False)` step composition (the closed gap) | `derive_plan('M8720', db, destructive=False).steps` + `derive_plan('W27C512', db, destructive=False).steps` (live, no mock) | Both return exactly `['id','read','blank-check']` | ✓ PASS |
| `derive_plan(destructive=True)` unchanged | `derive_plan('M8720', db, destructive=True).steps` (live) | `['id','read','blank-check','write','verify','erase']` | ✓ PASS |
| `locked_destructive` records the omitted verify | `derive_plan(..., destructive=False).locked_destructive` (live) | `[('write', ...), ('verify', 'destructive=False: verify omitted (D-01)'), ('erase', ...)]` | ✓ PASS |
| `_DESTRUCTIVE_OPS`/`_MULTI_RUN_OPS` unchanged | `grep -n "_DESTRUCTIVE_OPS = frozenset\|_MULTI_RUN_OPS = frozenset" firestarter/chip_test.py` | `frozenset({OP_WRITE, OP_ERASE})` / `frozenset({OP_WRITE, OP_ERASE, OP_VERIFY})` | ✓ PASS |
| SAFE-03 checker exits 0 | `python tools/check_devtest_orchestrator.py` | exit 0, PASS line names both files | ✓ PASS |
| New named tests select + pass | `pytest tests/test_chip_test.py -k verify_gated_behind_destructive -q` / `pytest tests/test_dev_test_cmd.py -k never_dispatches_verify -q` | Both 1 passed | ✓ PASS |
| Targeted 2-module suite (chip_test + dev_test_cmd) | `pytest tests/test_chip_test.py tests/test_dev_test_cmd.py -q` | 98 passed, 0 failed | ✓ PASS |
| Targeted 5-module suite (full Phase-112 surface) | `pytest tests/test_dev_test_cmd.py tests/test_chip_test.py tests/test_check_devtest_orchestrator.py tests/test_provenance.py tests/test_diagnostic_report.py -q` | 126 passed | ✓ PASS |
| Full suite (run once) | `pytest tests/ -q` | 3 failed — all pre-existing/environmental (see below), 0 new | ✓ PASS (expected) |
| Provenance symbols still fully removed | `grep -rn 'prompt_provenance\|class Provenance\|SHIELD_REV_CHOICES\|_CHIP_ORIGIN_CHOICES' firestarter/` | 0 hits | ✓ PASS |
| `--help` text matches actual behavior | `CliRunner(['dev','test','--help'])` | "Without --destructive: id + read + blank-check only... With --destructive: adds write/erase/verify" | ✓ PASS — now truthful (was already correct text, previously contradicted by code; code now matches) |
| ruff clean on all 112-05-touched files | `ruff check firestarter/chip_test.py tests/test_chip_test.py tests/test_dev_test_cmd.py` + `ruff format --check` (same) | All checks passed; 3 files already formatted | ✓ PASS |
| mypy on chip_test.py | `python -m mypy firestarter/chip_test.py` | "Success: no issues found in 1 source file" | ✓ PASS |
| mypy watermark gate | `python tools/check_mypy_watermark.py` | 1 error, 34 below watermark (35) | ✓ PASS |

### Pre-Existing Failure Verification (Not a Phase-112 Regression)

Independently re-confirmed this session, full suite run once:

- `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` — stale golden fixture predating Phase 112 (documented in `112-01/02-deferred-items.md`); `112-05`'s diff touches only `chip_test.py` + 2 test files + `REQUIREMENTS.md` — zero overlap with coverage-matrix/golden/support_status files.
- `tests/test_characterization.py::test_no_programmer_found_read` / `::test_no_programmer_found_erase` — fail because a live programmer is reachable on `/dev/ttyACM0` in this session (confirmed via `ls /dev/ttyACM*` → `/dev/ttyACM0` present), consistent with the project's USB-passthrough bench-hardware note. Unrelated to any Phase 112/112-05 code change.

**Conclusion: exactly the 3 documented pre-existing failures reproduced, no new regressions.**

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| SWEEP-01..04 | 112-02 | Plan derivation, per-op verdicts, id-first gate, N≥2 runs/marginal | ✓ SATISFIED | Unchanged by 112-05; re-confirmed via targeted suite pass. |
| SWEEP-05 | 112-02, gap-closed by 112-05 | Non-destructive by default (id + read + blank-check only) | ✓ SATISFIED (gap closed) | `derive_plan(chip, db, destructive=False).steps` == exactly `[id, read, blank-check]`, confirmed live, no mock. REQUIREMENTS.md SWEEP-05 text ("id + read + blank-check only") now matches actual code behavior. |
| PATT-01..03 | 112-02 | Address-derived pattern, fingerprint classifier, UV small-region variant | ✓ SATISFIED | Reachable via `run_plan`/`derive_plan` (Phases 108-109), unchanged by 112-05. |
| SAFE-01..03 | 112-03, re-confirmed by 112-05 | `--destructive` CLI-only gate; pure orchestrator; CI gate for zero new dispatch/VPP-set | ✓ SATISFIED | Truths 6 & 7; `_DESTRUCTIVE_OPS` explicitly NOT expanded to include `OP_VERIFY` (112-05's own prohibition, honored); checker exits 0. |
| RPT-01..05 | 112-02, reworked by 112-04, RPT-04 doc-synced by 112-05 | Single-source dual-render report, auto-capture, error_code seam, DB-diff | ✓ SATISFIED | RPT-01/02/03/05 unchanged and satisfied. **RPT-04 now reworded** in REQUIREMENTS.md to the auto-capture model, citing Phase 112 Plan 04 — the previously-flagged documentation debt is closed. |
| VOLT-01 | 112-01, 112-02 | VPP/VPE mV sampler captured into report during write step | ✓ SATISFIED (software); bench re-verify remains human-gated | Sampler thunk wired via `run_plan(sampler=...)`, only constructed on `--destructive`; unit-tested; unchanged by 112-05. Live bench sampler bracket exercise is the carried-forward Phase-111 SC2 human-verification item (see below) — now technically unblocked (operator can trust the non-destructive default before proceeding to `--destructive`), but not yet performed. |
| XPORT-01 | 112-02 | Transport-health counters, degrade to "not measured" if unavailable | ✓ SATISFIED | Unchanged; `TransportHealth()` defaults honest. |

All 17 requirement IDs (SWEEP-01..05, PATT-01..03, SAFE-01..03, RPT-01..05, VOLT-01, XPORT-01) declared across the five plans' frontmatter (112-01..05) match REQUIREMENTS.md's origin table (all marked `Complete`). No orphaned requirements. Both previously-flagged partial items (SWEEP-05, RPT-04) are now fully satisfied.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` found in any of the 112-05-touched files (`chip_test.py`, `test_chip_test.py`, `test_dev_test_cmd.py`, `REQUIREMENTS.md`) | — | None |
| `cli_handlers.py` | 147 | "not yet implemented" string | ℹ️ Info | Pre-existing `map_typed_errors` error message, unrelated to `dev_test`; not touched by 112-05. |

The previously-flagged 🛑 Blocker (docstring/`--help` vs. behavior mismatch at `cli_handlers.py:~1792`) is **resolved**: the `--help` text was already correct and required no edit (confirmed by 112-05's own scope decision to leave it byte-for-byte); the code now matches it.

### Human Verification Required

### 1. Phase-111 SC2 Bench Re-Verify (Hardware-Gated, still outstanding — unchanged by 112-05)

**Test:** On Leonardo + Rev 2.0 with an electrically-erasable chip (W27C512 or W29C020), run `firestarter dev test <chip> --destructive` against real hardware, through to completion.
**Expected:** The rendered report's voltage row shows `vpp_before_mv`/`vpp_after_mv` and `vpe_before_mv`/`vpe_after_mv` tracking real rail behavior (a plausible droop under load) across the write pulse — not flat, static, or absent values.
**Why human:** Requires a live serial connection to real hardware; cannot be exercised through `CliRunner` + `Mock(spec=HardwareManager)`. This is the same deferred Phase-111 SC2 item carried since `112-02-SUMMARY.md`/`112-03-SUMMARY.md`/`112-UAT.md`/prior `112-VERIFICATION.md`. 112-05 does not attempt it (explicitly out of scope per its `carried_forward_deferral` block — cannot be closed by software) but does remove the blocker that made a confident `--destructive` bench attempt impossible: the non-destructive default no longer self-BADs to exit 1 on a healthy chip, so an operator can now trust `exit 0` before escalating to `--destructive` on a scrap chip.

### Gaps Summary

**No remaining code gaps.** The single gap identified in the prior verification pass (SC2/SWEEP-05: `derive_plan(destructive=False)` unconditionally including `OP_VERIFY`, producing a 4-step plan and a spurious `BAD`/exit-1 on the tool's safest default invocation) is closed, verified directly against the codebase in this session:

- **Fix confirmed in source:** `chip_test.py:387-398` now gates the `OP_VERIFY` append behind `if destructive:`, mirroring the pre-existing `OP_WRITE` pattern at `:382-385`. Non-destructive omission is recorded on `locked_destructive`.
- **Fix confirmed via live, non-mocked reproduction:** `derive_plan('M8720'|'W27C512', db, destructive=False).steps` returns exactly `[id, read, blank-check]` (3 steps) in this session — not the previously-observed 4.
- **Destructive plan confirmed unchanged:** `derive_plan(..., destructive=True).steps` still returns `[id, read, blank-check, write, verify, erase]` — verify's position (after write, before erase) is byte-for-byte preserved.
- **Locked invariants confirmed intact:** `_DESTRUCTIVE_OPS` still `frozenset({OP_WRITE, OP_ERASE})` (verify NOT added); `_MULTI_RUN_OPS` still includes `OP_VERIFY` (not removed); `python tools/check_devtest_orchestrator.py` exits 0; zero interactive provenance prompt symbols anywhere in `firestarter/` (112-04 descope not regressed).
- **Behavioral regression coverage confirmed:** `test_non_destructive_run_never_dispatches_verify` uses `verify_eprom.side_effect = AssertionError(...)` (not a masking `return_value`) and passes, proving the non-destructive path cannot reach `operator.verify_eprom` even under test.
- **RPT-04 documentation debt confirmed closed:** REQUIREMENTS.md line 37 no longer describes the deleted interactive-provenance-prompt model; it cites Phase 112 Plan 04 and documents the auto-capture-only model. Only that one line changed in the doc commit.
- **No regressions:** targeted suites (98-test 2-module run, 126-test 5-module run) fully green; full suite run once shows exactly the 3 documented pre-existing/environmental failures (stale golden fixture; two tests that fail only because a live board is attached on `/dev/ttyACM0` in this devcontainer session) and nothing new.

**Only remaining item is the pre-existing, hardware-gated Phase-111 SC2 bench re-verify**, which is a human-verification item, not a code gap — it was never closeable by 112-05 (or any software plan) and is now unblocked (an operator can trust the non-destructive default before attempting `--destructive`) but not yet performed. This routes the overall status to `human_needed` rather than `passed`, per the decision tree (a non-empty human-verification section overrides an otherwise fully-verified score).

---

_Verified: 2026-07-03_
_Verifier: Claude (gsd-verifier)_
