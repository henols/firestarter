---
phase: 134-the-plan-derived-sdp-oracle-in-dev-test
verified: 2026-08-04T21:22:52Z
status: passed
score: 5/5 ROADMAP success criteria verified, 14/14 requirements verified
behavior_unverified: 0
overrides_applied: 0
findings:
  - id: F-01
    severity: warning
    area: "LEG-02 evidence citation vs. actual test population"
    statement: >
      REQUIREMENTS.md and 134-RECORD.md both cite LEG-02's evidence as
      "test_derive_plan_refuse_population_emits_six_na_steps_with_reason
      (all 41 measured REFUSE chips)". Independently re-derived: the test's
      own `_allow_refuse_populations()` helper computes REFUSE over the
      ENTIRE chip database (every non-ALLOW entry, all protocols), not the
      protocol-0x0D-scoped subset the ROADMAP's "41 REFUSE chips" describes.
      Measured live: ALLOW=43 (matches), REFUSE=703 (not 41), TOTAL=746.
      The 41-chip figure only exists within the narrower protocol-0x0D
      subset (84 total 0x0D chips = 43 ALLOW + 41 REFUSE, confirmed by a
      separate live count). The test's own docstring inconsistently says
      "84 total among the protocol-0x0D subset" while its assertion sums
      to 746 total DB entries -- an internal inconsistency in the comment,
      not in behavior.
    impact: >
      Not a functional defect -- the code and test correctly validate the
      REFUSE/NA-step behavior for a population that is a STRICT SUPERSET of
      the 41 chips the requirement names (703 ⊇ 41), so the underlying
      claim ("41 REFUSE chips get 6 NA steps carrying the refusal reason")
      is satisfied, not violated. The issue is purely an unflagged citation
      inaccuracy: this phase otherwise disciplines itself to record every
      measured discrepancy explicitly (n_ran=6 vs stated 5, THREE reds vs
      stated TWO, to_dict() ten keys vs stated nine, etc.) -- this one
      slipped through uncaught and uncorrected in both REQUIREMENTS.md and
      134-RECORD.md.
    recommendation: >
      A documentation-only fix for a future plan/close pass: correct the
      "(all 41 measured REFUSE chips)" citation to state the actual tested
      population (703, the full non-ALLOW DB) or explicitly scope a
      dedicated 0x0D-only assertion if the "41" figure is meant to be
      independently pinned. Does not block phase progression.
---

# Phase 134: The Plan-Derived SDP Oracle in `dev test` -- Verification Report

**Phase Goal:** For every SDP-capable chip, `dev test` runs a leg that actually proves whether the
lock inhibited a write -- never a leg that reports success just because a write returned without
error -- and a run that ends early still leaves a visible, honest trace of whether the part was left
locked.

**Verified:** 2026-08-04T21:22:52Z
**Status:** passed (1 non-blocking finding, see F-01 above)
**Re-verification:** No -- initial verification

**Method:** All claims below were re-derived independently against the actual `firestarter_app`
submodule source (`gsd/v1.30-sdp-surface-retirement`, HEAD `2b7a702`) and by running the real test
suite in the CI-replica venv (`.venv/ci-replica`, Python 3.11.15, numpy-free) -- SUMMARY.md and
134-RECORD.md prose was treated as a claim to falsify, not as evidence.

---

## Goal Achievement -- the 5 ROADMAP Success Criteria

### Criterion 1 -- derivation, no new CLI option, both readings recorded

> Running `dev test` against any of the 43 SDP-capable ALLOW chips derives, with no new
> command-line option, a four-step leg ... from `sdp_capability()`; running it against any of the
> 41 REFUSE chips instead produces four NA/SKIPPED steps each carrying the refusal reason.

| Check | Result |
|---|---|
| `_SDP_LEG_STEP_ORDER` single-sourced 6-tuple in `chip_test.py:389-396` | ✓ VERIFIED -- read directly: `write-baseline-b, write-baseline-a, sdp-lock, write-inhibited, sdp-unlock, write-restored` |
| Both readings (inherited "four", shipped "six") recorded in-source, not silently reconciled | ✓ VERIFIED -- `chip_test.py:377-388`'s "CORRECTION 2" comment states both explicitly |
| `derive_plan` derives from `sdp_capability(name, db)`, no re-implemented heuristic | ✓ VERIFIED -- `chip_test.py:693` |
| Live ALLOW count = 43 | ✓ VERIFIED -- independently recomputed via `sdp_capability_for_entry` over the live DB: 43 |
| Zero new CLI options on `dev test` | ✓ VERIFIED by test (`test_derive_plan_allow_dev_test_exposes_zero_cli_options`, passed) |
| REFUSE chips get 6 NA steps carrying `sdp_capability()`'s own reason, identity-compared | ✓ VERIFIED functionally -- see **Finding F-01**: the tested REFUSE population is 703 chips (a superset of the "41" figure), not scoped to protocol 0x0D as the requirement text implies. Behavior is correct for all of them; the "41" citation in REQUIREMENTS.md/134-RECORD.md is imprecise. |

**Verdict: VERIFIED** (with F-01 noted as a documentation-only imprecision, not a functional gap).

### Criterion 2 -- leaked lock is BAD + exit 1; partial/degenerate read-backs never equality

| Check | Result |
|---|---|
| `(True, B) -> BAD` (leaked write) | ✓ VERIFIED in source, `chip_test.py:2120-2131`, and by test `test_lock_leaked_write_ok_true_b_readback_is_bad` (passed) |
| End-to-end exit 1 on a leaked lock, driven through the real CLI | ✓ VERIFIED -- `test_leaked_lock_exits_1` (passed) |
| Mixed BAD+marginal run still exits 1, not 2 | ✓ VERIFIED -- `test_mixed_bad_and_marginal_exits_1_not_2` (passed); `_EXIT_CODE_PRECEDENCE = (1, 2, 0)` read directly at `cli_handlers.py:1926`, confirming the prior naive `max()` defect is fixed |
| Partial read-back reports BAD (gh#11) | ✓ VERIFIED -- `test_partial_readback_reports_bad` (passed) |
| Empty/short/all-0x00/all-0xFF never equality | ✓ VERIFIED -- length gate at `chip_test.py:2076-2087` runs before any `classify_fingerprint` call; 4 named degenerate tests all passed |

**Verdict: VERIFIED.**

### Criterion 3 -- baseline transition proves the write path is live before any lock

| Check | Result |
|---|---|
| Two-direction baseline (write B, verify, write A, verify) strictly before `sdp-lock` | ✓ VERIFIED -- step order in `_SDP_LEG_STEP_ORDER` and `test_derive_plan_baseline_transition_ordering` (passed) |
| Dead-write-path fixture (`write_eprom` claims success, `read_eprom` always returns A) makes the baseline step BAD | ✓ VERIFIED -- `_dead_write_path_operator` + `test_dead_write_path_baseline_b_is_bad` (passed) |
| `_baseline_closes_sdp_gate` closes on any non-OK baseline verdict before a lock is emitted | ✓ VERIFIED in source (`chip_test.py:1306`, `_SDP_LEG_GATED_OPS` membership) and by `test_baseline_gate_closes_dead_write_path_allow_chip_full_leg` (passed) |

**Verdict: VERIFIED.**

### Criterion 4 -- `HELD`/`NOT-HELD`/`NOT-RUN(reason)` in both surfaces; N-of-M drops; 6 laundering routes covered

| Check | Result |
|---|---|
| `sdp_hold_state` reaches both `to_dict()` and `render()`, no boolean anywhere in `to_dict()` | ✓ VERIFIED -- `TestHoldStateLeg12`'s 3 tests (all 3 passed), plus the recursive `test_hold_state_no_boolean_under_lock_or_protect_key_anywhere_in_to_dict` (passed) |
| `SCHEMA_VERSION` bumped to 1.3 | ✓ VERIFIED -- `diagnostic_report.py:55` |
| N-of-M drop on a gated ALLOW chip | ✓ VERIFIED -- `test_count_applicable_sdp_gated_allow_chip_ratio_drops` (passed); measured `m_applicable=10`, `n_ran=6` -- matches the RECORD's stated correction of `134-CONTEXT.md`'s "n_ran=5" |
| 6 laundering routes (R1-R6), each pairing `sdp_lock.assert_not_called()` with a rendered NOT-RUN reason | ✓ VERIFIED -- `TestLaunderingRoutesR1R2SyntheticChipId`, `TestLaunderingRoutesR3R4`, `test_r5_laundering_...`, `test_r6_laundering_...` all present and passed |
| Chip-ID gate is NOT claimed as protective (v1.22 C-5 class overclaim check) | ✓ VERIFIED -- `grep -rniE "gated by chip[- ]id" firestarter/ tests/` returns 0 hits tree-wide (re-run independently) |
| "Seventh route" (baseline gate) named separately, not folded into "six laundering routes" | ✓ VERIFIED -- `test_chip_test.py:2149` comment: "THESE TWO ARE NOT EXHAUSTIVE EITHER: a seventh route..." |

**Verdict: VERIFIED.**

### Criterion 5 -- recovery says "rewrite," never "erase"; gh#20 triaged

| Check | Result |
|---|---|
| `_SDP_RECOVERY_LOUD`/`_SDP_RECOVERY_NEUTRAL` contain "Rewrite"/no "erase" | ✓ VERIFIED by direct read (`cli_handlers.py:2217-2228`) -- no occurrence of "erase" in either constant |
| Scoped, fail-closed grep test (`tests/test_sdp_recovery_wording.py`) | ✓ VERIFIED -- 8 tests, all passed |
| gh#20 triage finding recorded, not posted; backlog item filed with a named owner | ✓ VERIFIED -- `134-GH20-TRIAGE.md` exists with full finding; `.planning/todos/pending/at28c256-write-path-failure-gh20.md` exists, `Owner: henols` |

**Verdict: VERIFIED.**

---

## The Evidence Ceiling -- independently checked for overclaim

The central risk this phase called out for itself: no artifact may claim the causal fact "the lock
inhibited the write" is proven, because no fixture in either repo can simulate real SDP inhibition on
silicon.

- `grep -rniE "lock inhibited the write|proven on silicon|silicon-proven"` across `firestarter/`,
  `tests/`, and `.planning/` returns only the two DISCLAIMING usages inside
  `tests/test_dev_test_cmd.py` ("...the causal claim 'the lock inhibited the write' is NOT provable
  this milestone" / "...is NOT provable this milestone") -- **zero** affirmative-claim occurrences.
- `134-VALIDATION.md`'s Manual-Only Verifications table states this exact caveat and marks it "Not to
  be verified, claimed, or smoothed over in any artifact" -- consistent with what the source and
  tests actually say.
- `134-RECORD.md` §7 restates the Evidence Ceiling verbatim and applies it specifically to
  `134-GH20-TRIAGE.md`, explicitly stating that document does NOT diagnose the reporter's chip and
  does NOT establish any lock ever inhibited any write on that hardware.

**Verdict: No overclaim found anywhere in the codebase or phase artifacts.**

---

## Requirement Coverage (14/14)

| Requirement | Status | Evidence (independently confirmed) |
|---|---|---|
| LEG-01 | ✓ SATISFIED | `_SDP_LEG_STEP_ORDER`, zero-CLI-option test, 43-ALLOW population test -- all read/run directly |
| LEG-02 | ✓ SATISFIED (see F-01) | REFUSE-chip NA-step test passed against a 703-chip population (superset of the "41" cited) |
| LEG-03 | ✓ SATISFIED | `generate_inhibited_pattern` bitwise-complements `generate_pattern` exactly once; `TestInhibitedPattern` (5 tests) passed |
| LEG-04 | ✓ SATISFIED | Baseline ordering test passed; both directions strictly precede `sdp-lock` |
| LEG-05 | ✓ SATISFIED | Full 2x2 read-back-equality oracle, 4 named tests passed |
| LEG-06 | ✓ SATISFIED | Engine + exit-code halves both passed; `_EXIT_CODE_PRECEDENCE` read directly, confirms the fix |
| LEG-07 | ✓ SATISFIED | `test_partial_readback_reports_bad` passed |
| LEG-08 | ✓ SATISFIED | 4 degenerate-fixture tests passed |
| LEG-12 | ✓ SATISFIED | `sdp_hold_state` field/key/row, `TestHoldStateLeg12` (3 tests) passed |
| LEG-13 | ✓ SATISFIED | `m_applicable=10, n_ran=6` reproduced live via the named pinning test |
| LEG-14 | ✓ SATISFIED | Recovery wording grep test (8 tests) passed; "rewrite" present, "erase" absent, confirmed by direct read |
| LEG-16 | ✓ SATISFIED | Dead-write-path fixture + test passed |
| LEG-17 | ✓ SATISFIED | R1-R6 all present and passed; 7th route named separately, not double-counted |
| LEG-18 | ✓ SATISFIED | `134-GH20-TRIAGE.md` + owned backlog item both exist and are substantive |

**Orphaned requirements check:** `grep -E "Phase 134" .planning/REQUIREMENTS.md` maps exactly these 14
IDs to Phase 134 -- no additional Phase-134-mapped requirement exists outside this list.

**Requirement tick discipline (independently re-counted):**
- `grep -c '^- \[x\] \*\*LEG-'` → **18** (14 this phase + 4 carried from Phase 133) -- matches.
- `grep -c '^- \[ \] \*\*RELOCK-\|^- \[ \] \*\*CHAN-\|^- \[ \] \*\*CLOSE-'` → **14**, all still unticked
  -- matches (Phases 136/137 have not run).
- Total ticked project-wide: **36**; total open: **14**. Matches the claimed accounting exactly.

---

## Behavioral Verification (tests actually run by this verifier, not narrated)

All commands below were executed in `.venv/ci-replica` (Python 3.11.15, numpy-free), not the
devcontainer's ambient Python 3.12.

| Command | Result |
|---|---|
| `pytest tests/test_chip_test_sdp_leg.py tests/test_op_registration_parity.py -o addopts="" -q` | **86 passed** |
| `pytest tests/test_dev_test_cmd.py tests/test_sdp_recovery_wording.py tests/test_chip_test.py -o addopts="" -q` | **168 passed** |
| `pytest tests/test_chip_test.py -k "count_applicable_sdp" -o addopts="" -q` | **3 passed** (confirms `n_ran=6`, `m_applicable=10` live) |
| `pytest tests/ -o addopts="" -q` (full suite, run once) | **1437 passed** (30 snapshots), matching `134-CI-PARITY.md`'s own "After" figure exactly |
| `bash tools/ci_replica_venv.sh` (all 5 legs) | **CI-REPLICA: PASS** -- mypy watermark gate exit 0 (33 errors / 35 watermark, unmoved), ruff clean, coverage 82.12% (≥70% floor) |
| Live population count (`sdp_capability_for_entry` over the full DB) | ALLOW=43 (matches), REFUSE=703 (see F-01), TOTAL=746 |
| Live protocol-0x0D-only count | 84 total (43 ALLOW + 41 REFUSE) -- confirms the ROADMAP's "41" figure is real, just scoped narrower than the actual test population |
| `git -C /workspaces/firestarter status --porcelain` (firmware submodule) | clean -- confirms this phase is genuinely host-only |
| Debt-marker scan (`TBD`/`FIXME`/`XXX`) on `chip_test.py`, `cli_handlers.py`, `diagnostic_report.py` | 0 hits |

---

## Anti-Patterns Found

None. No stub returns, no empty handlers, no hardcoded-empty props, no debt markers in the three
phase-owned production files.

---

## Human Verification Required

None. The one behavior this milestone cannot prove by design -- "the lock inhibited the write" on
real silicon -- is explicitly and correctly excluded from verification everywhere in the codebase and
phase record (134-VALIDATION.md: "Not to be verified, claimed, or smoothed over in any artifact"),
so it is not an outstanding gap to route to a human; it is a permanently accepted, honestly-stated
limitation of this milestone's fixtures.

---

## Findings Summary

**F-01 (WARNING, non-blocking):** REQUIREMENTS.md and 134-RECORD.md's LEG-02 evidence line says
"(all 41 measured REFUSE chips)". The actual test (`test_derive_plan_refuse_population_emits_six_na_steps_with_reason`)
enumerates 703 chips -- every non-ALLOW entry in the live database across all protocols, not the
protocol-0x0D-scoped 41 the ROADMAP names. This is a documentation/citation imprecision, not a
functional defect: the 703-chip population is a strict superset of the 41, so the underlying
requirement (REFUSE chips get correctly NA-reasoned steps) is proven more broadly than claimed, never
less. Notably, this phase otherwise polices itself rigorously for exactly this class of
citation-vs-code mismatch (it caught and recorded n_ran=6-not-5, THREE-reds-not-TWO, ten-keys-not-nine,
etc.) -- this one instance slipped through both REQUIREMENTS.md and 134-RECORD.md uncaught. Recommend
a documentation-only correction in a future pass; does not block this phase or the milestone.

---

## Overall Assessment

All 5 ROADMAP success criteria and all 14 requirements (LEG-01..08, 12, 13, 14, 16, 17, 18) are
independently verified against the actual `firestarter_app` source and a live test run (1437/1437
passing, mypy watermark held at 33/35, ruff clean) -- not merely against SUMMARY.md narration. The
Evidence Ceiling is honestly maintained everywhere it is referenced, with zero overclaim of "the lock
inhibited the write" or "gated by chip ID" found anywhere in code, tests, or phase documentation.
Requirement-tick discipline is exactly as claimed (18 LEG rows ticked project-wide, 14 non-LEG rows
still open, Phases 136/137 untouched). The one finding (F-01) is a citation-accuracy issue in
project documentation, not a code defect, and does not change the verdict.

**Verdict: PASS-WITH-FINDINGS.**

---

*Verified: 2026-08-04T21:22:52Z*
*Verifier: Claude (gsd-verifier)*
