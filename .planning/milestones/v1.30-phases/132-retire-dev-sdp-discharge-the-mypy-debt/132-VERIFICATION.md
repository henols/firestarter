---
phase: 132-retire-dev-sdp-discharge-the-mypy-debt
verified: 2026-08-03T22:14:59Z
status: passed
score: 5/5 must-haves verified (5 roadmap success criteria; 1 amended on measured grounds, not failed)
behavior_unverified: 0
overrides_applied: 0
---

# Phase 132: Retire `dev sdp` & Discharge the mypy Debt — Verification Report

**Phase Goal:** `dev sdp` no longer exists as an invokable command, its removal breaks nothing that
dereferences its surviving pieces, and `firestarter_app`'s primary `ci` job is GREEN at the existing
watermark — without touching the ring-fenced `eprom_operations.py` cluster.

**Verified:** 2026-08-03T22:14:59Z
**Status:** passed
**Re-verification:** No — initial verification

## Method

This is a re-measurement, not a re-read of SUMMARY.md. Every claim below was independently
reproduced against the actual `firestarter_app` submodule (branch `gsd/v1.30-sdp-surface-retirement`,
HEAD `42a1971a072db2f3bcec558a3dc2bcb3d5d65e08`, 19 commits ahead of fork base `8caf77f`) — runtime
command enumeration, `git show`/`git diff` on the exact commits SUMMARY.md cites, live pytest/ruff/mypy
runs, and a fresh `gh run view` read of the certifying CI run. No claim was accepted on SUMMARY.md's
word alone.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | `firestarter dev sdp` is gone; the four gates only it exercised are gone with it | ✓ VERIFIED | `python3 -c "from firestarter.cli_handlers import dev; print(sorted(dev.commands))"` → `['addr', 'consistency-check', 'fault-inject', 'read', 'reg', 'test', 'validate-family', 'write-cycle']` — 8 commands, `sdp` absent. Runtime invocation `python3 -m firestarter.main dev sdp --help` → exit 2, `Error: No such command 'sdp'.` `def dev_sdp` / `@dev.command(name="sdp")` absent from `cli_handlers.py` (2219 lines, was 2321). Zero `.md` hits for "dev sdp" anywhere under `firestarter_app/` (P-17 trace 12, re-run, not inherited). |
| 2 | `check_no_exists_proxy.py`'s target list updated in the same commit as the file move; all four honesty assertions survive under `tests/` | ✓ VERIFIED | `git show --stat 7495c9e` — one commit contains the `git mv tests/test_dev_sdp_cmd.py → tests/test_sdp_honesty.py` rename AND the `tools/check_no_exists_proxy.py` target-list edit. `grep` for all four assertion literals (`"cannot be read back"`, `"not a claim about"`, `"was emitted"`, plus the four named test functions) resolves to `tests/test_sdp_honesty.py` — `test_summary_line_carries_the_unreadable_state_caveat_on_both_directions`, `test_summary_line_carries_no_duration_figure`, `test_no_fabricated_lock_state_boolean_in_the_report`, `test_firmware_too_old_is_reported_when_unknown_cmd_comes_back`, all 5 tests in that file collected and passing (`pytest tests/test_sdp_honesty.py -v` → 5 passed). `check_no_exists_proxy.py` itself runs green (`PASS: scanned 79 file(s)`, exit 0). |
| 3 | `COMMAND_SDP_LOCK`/`COMMAND_SDP_UNLOCK` and their `COMMAND_NAMES` entries survive, exercised by a dereference test | ✓ VERIFIED | `tests/test_revision_constants_parity.py::test_command_names_dereferences_both_sdp_commands` exists, carries NO `@requires_fw` decorator (confirmed by reading the decorator list directly above the `def`), and passes when run alone (`pytest tests/test_revision_constants_parity.py::test_command_names_dereferences_both_sdp_commands -v` → 1 passed). It dereferences `COMMAND_NAMES[COMMAND_SDP_UNLOCK]` and `COMMAND_NAMES[COMMAND_SDP_LOCK]` unconditionally, host-only-CI-reachable. |
| 4 | `firestarter_app`'s primary `ci` job passes end to end at watermark 35, without touching the ring-fenced `eprom_operations.py` cluster | ✓ VERIFIED | Fresh `gh run view 30856059940 --repo henols/firestarter_app --json conclusion,jobs` → `"conclusion":"success"` for both the `ci` job (id `91827219671`, every one of its 15 steps `success`) and the sibling `ci-py32` job. Log line (re-read, not computed): `mypy errors: 32 (watermark: 35)`, `checked 122 source files`. **Independently reproduced locally**, not just re-read: `bash tools/ci_replica_venv.sh` (fresh numpy-free venv, Python 3.11.15, mypy 2.3.0) → Leg 3 (ruff) exit 0, Leg 4 (mypy watermark gate) exit 0, Leg 5 (pytest --cov, CI's exact args) exit 0, `1297 passed`, `Total coverage: 81.72%` ≥ 70% floor. Direct re-run of the gate in that venv: `mypy errors: 32 (watermark: 35)`, `checked 122 source files` — byte-identical to the CI log. Ring-fence: `git diff --stat 8caf77f..HEAD -- firestarter/eprom_operations.py tools/check_mypy_watermark.py tools/ci_parity.sh` is empty; the watermark literal in `pyproject.toml:159` still reads `35`. |
| 5 | A tripwire (comment at the auto-unlock decision site + named test) records the removal-safety dependency; the stale `301`/`377` references are corrected | ✓ AMENDED (satisfied a fortiori) | Tripwire comments confirmed at `cli_handlers.py:301-303` (default) and `:636-640` (D-04 decision block) plus `constants.py:133-136` (`FLAG_SKIP_SDP_UNLOCK` definition), and the named test `test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on` in `tests/test_write_skip_sdp_unlock.py` exists and passes standalone. **Stale-reference correction: the requirement's own text said "three"; the measured count is five, across two files** (`constants.py:69-70` — one; `test_revision_constants_parity.py:71-72`,`:527`,`:549`,`:585-586` — four). All five were corrected in commit `42a1971`, verified by `grep -rn "eprom_operations.py:301\|:377"` returning zero hits tree-wide, and the corrected citations name `_setup_operation` (`eprom_operations.py:329`, confirmed by direct read of that line) and `_operation_context` (`:405`, confirmed) function-name-first, per D-11. Fixing five satisfies "three" a fortiori. This is recorded as AMENDED, not a silent pass — the requirement's own text was wrong and was corrected in-phase (D-12), evidenced by meta-repo commit `88a521e` which cross-cites submodule commit `42a1971` (a literal same-commit binding is impossible across two git repositories; the cross-citation is verified in both directions by reading both commit messages). |

**Score:** 5/5 roadmap success criteria hold (criterion 5 amended on measured grounds — five corrected, not three, satisfying the requirement a fortiori). 0 truths present-but-behavior-unverified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter/sdp_honesty.py` | Shared honesty carrier (D-01/D-02) | ✓ VERIFIED | 93 lines, exists, exports `unreadable_state_caveat()`, `emission_summary()`, `map_unknown_cmd_to_outdated()`. Registered in `pyproject.toml`'s strict island (`disallow_untyped_defs = true`, `check_untyped_defs = true`) alongside the 8 Phase-42 modules — confirmed by direct read of the override block. Import set is `{__future__, firestarter.exceptions, firestarter.messages}` — no `click`, verified live. |
| `tests/test_sdp_honesty.py` | Retargeted honesty tests (RETIRE-02/03) | ✓ VERIFIED | 197 lines, 5 tests collected and passing. |
| `tests/test_revision_constants_parity.py::test_command_names_dereferences_both_sdp_commands` | RETIRE-04 dereference test | ✓ VERIFIED | Exists, not `requires_fw`-skipped, passes standalone. |
| `tests/conftest.py` typed `make_app_context`/`app_context` | RETIRE-05 typed fixture | ✓ VERIFIED | `make_app_context(...) -> AppContext` at `:229`, six explicit typed keyword params, no `**overrides: object`; `app_context` fixture at `:325` wraps it. Two "non-default" test modules (`test_write_skip_sdp_unlock.py`, `test_validate_family_cmd.py`) carry typed local delegates that forward to the shared factory (confirmed by reading both delegate bodies) — matching D-10's documented design, not a regression. Two "default" modules (`test_dev_test_cmd.py`, `test_write_skip_erase_0x0d.py`) import the shared factory directly. Three untyped `**manager_overrides` copies (`test_cli_handlers.py`, `test_protocol_not_implemented.py`, `test_protocol_not_implemented_production_path.py`) remain unconsolidated, as explicitly deferred (out of scope, contribute zero mypy errors). |
| `tools/ci_replica_venv.sh` | Numpy-free CI-replica venv (D-06/D-07) | ✓ VERIFIED | Exists, 363 lines, committed and separate from `tools/ci_parity.sh` (that file's diff across the whole phase is empty). Run live during this verification: all 5 legs exit 0. |
| `.planning/phases/132-.../132-CI-GREEN.md`, `132-RECORD.md`, `132-PRUNE-LEDGER.md`, `132-MYPY-LEDGER.md`, `132-CI-PARITY.md`, `132-CONTEXT.md` | Phase evidence documents | ✓ VERIFIED | All present, internally consistent with each other and with the actual git/CI state re-measured above. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tools/check_no_exists_proxy.py`'s `_DEFAULT_TARGETS` | `tests/test_sdp_honesty.py` | literal list entry at `:188` | ✓ WIRED | Confirmed by grep; gate runs green (exit 0, 79 files scanned). |
| `tests/test_sdp_honesty.py`'s four assertions | `firestarter/sdp_honesty.py` | direct function call (not `CliRunner`) | ✓ WIRED | Confirmed by reading test bodies; all call `emission_summary`/`map_unknown_cmd_to_outdated` directly. |
| `constants.py`'s stale-anchor comment / `test_revision_constants_parity.py`'s citations | `eprom_operations.py:329`/`:405` | corrected line-number citations | ✓ WIRED | `_setup_operation`'s `COMMAND_NAMES[cmd]` deref is at line 329 exactly; `_operation_context`'s is at line 405 exactly — both confirmed by direct read, matching every corrected citation. |
| `cli_handlers.py`'s auto-unlock decision block (`:626-640`) / `constants.py`'s `FLAG_SKIP_SDP_UNLOCK` (`:121`/`:137` comment) | `tests/test_write_skip_sdp_unlock.py::test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on` | tripwire comment naming the test | ✓ WIRED | Comment text names the test by name at both sites; test exists and passes. |
| `ci.yml`'s `ci` job's mypy step | `tools/check_mypy_watermark.py` | `python tools/check_mypy_watermark.py` invocation | ✓ WIRED | Reproduced locally in the numpy-free venv with byte-identical output to the CI log. |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| RETIRE-01 | 132-04 | ✓ SATISFIED | Command absent at runtime; span deleted; snapshot updated. |
| RETIRE-02 | 132-03 | ✓ SATISFIED | Same-commit rename + gate edit (`7495c9e`). |
| RETIRE-03 | 132-02/132-03 | ✓ SATISFIED | Four assertions retargeted, passing, no net loss (measured and itemized in `132-PRUNE-LEDGER.md`, independently spot-checked above). |
| RETIRE-04 | 132-08 | ✓ SATISFIED | Dereference test exists, unconditional, passes. |
| RETIRE-05 | 132-05 | ✓ SATISFIED | Typed factory + fixture exist and are used by 4 of 5 typed copies (2 direct, 2 delegated); 3 untyped copies explicitly out of scope. |
| RETIRE-06 | 132-01/132-06/132-09 | ✓ SATISFIED | CI run `30856059940` conclusion `success`; independently reproduced locally (`mypy errors: 32 (watermark: 35)`); ring-fence diff empty. |
| RETIRE-07 | 132-07 | ✓ SATISFIED | Tripwire comments + named test exist and pass. |
| RETIRE-08 | 132-08 | ✓ SATISFIED (amended) | Five references corrected (not three); requirement text itself corrected in-phase (D-12), cross-commit citation verified. |

No orphaned requirements — all 8 RETIRE-* IDs in `REQUIREMENTS.md` are claimed by at least one plan's frontmatter, and REQUIREMENTS.md's own Traceability table marks all 8 Complete, matching the measured state.

### Anti-Patterns Found

Scanned every file touched by this phase's diff (`git diff 8caf77f..HEAD --name-only`, 17 files) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and empty-implementation idioms.

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `tests/__snapshots__/test_characterization.ambr` | 73 | `XXX` substring match | ℹ️ Info (false positive) | Part of the pre-existing literal string `/dev/ttyXXX` (a placeholder device-name example in `--help` text), not a debt marker. Not introduced by this phase. |

No genuine debt markers found in any file this phase touched. The one `.ambr` diff line (removal of the `sdp` help-text row from `test_help_dev`) matches D-13's stated scope exactly — confirmed by reading the diff directly (`-    sdp                Enable or disable...`, one line removed, nothing else).

### Ring-Fence and Watermark Checks

- `git diff --stat 8caf77f..HEAD -- firestarter/eprom_operations.py tools/check_mypy_watermark.py tools/ci_parity.sh` → empty (re-confirmed).
- `pyproject.toml:159` watermark comment literal → `35`, unchanged.
- Local numpy-free venv mypy run → `32 (watermark: 35)`, `checked 122 source files` — matches CI exactly.
- `firestarter.eprom_operations` remains in the non-strict `follow_imports = "silent"` override block; `firestarter.sdp_honesty` is in the strict-island block from birth.

### Known, Disclosed Residuals (not gaps — carried forward by design, per `132-RECORD.md` and `132-CONTEXT.md`)

These are recorded here for completeness because they are genuine, accounted-for scope reductions, not defects:

1. **Coverage loss, accounted:** the nine-way `_ADAPTER_REQUIRED_CHIPS` capability-before-support-status ordering proof has no successor now that `dev_sdp`'s gate sequence is deleted (`132-PRUNE-LEDGER.md` §4 item 1). Confirmed disclosed, not hidden.
2. **D-05 residual:** no honesty caveat was added to the `write` auto-unlock path; the caveat has no user-reachable production carrier until Phase 134. Deliberate, stated in `132-RECORD.md` residual 1.
3. **D-09 residual:** watermark stays unratcheted at 35 against a measured true count of 32 — 3 of silent headroom, named as an input to a later phase's ratchet, not yet filed with an owner (stated explicitly in `132-RECORD.md` residual 2, not silently enjoyed).
4. **D-12 non-literal honoring:** RETIRE-08's "same commit" binding for the text correction is impossible across two git repositories (submodule `42a1971` vs. meta-repo `88a521e`); honored instead as verified adjacent cross-citing commits, confirmed above in both directions.
5. **Pre-existing working-tree dirt:** baseline dirt in both meta and submodule repos (captured before this phase began at meta `666d2512`/app `8caf77f`) persists unchanged; plan 132-09's "porcelain empty" criterion was discharged as a delta check, disclosed in `132-RECORD.md`, not silently claimed as a literal pass.

None of these affect the phase goal as stated in ROADMAP.md. All are within scope boundaries the phase's own `132-CONTEXT.md` set before execution.

### Human Verification Required

None. Every success criterion resolved to a runnable command or a direct source read; no visual, real-time, or external-service behavior is in scope for this host-only, CI-gate phase.

### Gaps Summary

No gaps found. All 8 RETIRE-* requirements are satisfied with independently reproduced evidence (not SUMMARY.md's word): the command is verifiably absent at runtime, the honesty assertions verifiably survive and pass against a real production SUT, the dereference test verifiably runs unconditionally, the CI run verifiably concluded `success` and its mypy count is verifiably reproducible byte-for-byte in a fresh local venv, the tripwire verifiably exists and its named test verifiably passes, and the stale-reference correction — while its own originating requirement text was itself wrong ("three" vs. the measured "five") — was itself corrected in-phase rather than left as a known error, satisfying the requirement's intent a fortiori. Criterion 5 is recorded as AMENDED rather than a silent pass, per the measured-and-corrected discrepancy.

---

_Verified: 2026-08-03T22:14:59Z_
_Verifier: Claude (gsd-verifier)_
