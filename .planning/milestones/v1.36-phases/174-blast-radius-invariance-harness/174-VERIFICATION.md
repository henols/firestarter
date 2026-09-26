---
phase: 174-blast-radius-invariance-harness
verified: 2026-09-03T18:44:55Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "A MILESTONES.md re-key ledger section exists with the fields a declared re-key must carry (change, before-hash, after-hash, date) — the mechanism every later phase's deliberate re-key is recorded into (roadmap SC5 / GATE-06)"
  gaps_remaining: []
  regressions: []
---

# Phase 174: Blast-Radius Invariance Harness Verification Report

**Phase Goal:** A frozen, absolute-value oracle exists proving any later change to `dedup_fingerprint` or the promotion ladder is a declared decision, not a silent accident — built and green before any of this milestone's behaviour changes land.
**Verified:** 2026-09-03T18:44:55Z
**Status:** human_needed
**Re-verification:** Yes — after gap closure (174-06-PLAN.md / 174-06-SUMMARY.md)

## Goal Achievement

### Observable Truths (roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | A frozen table pairing report shapes to expected 12-hex `dedup_fingerprint` values lives in `firestarter_app/tests/fixtures/`, covering the four measured re-key shapes, computed against HEAD | ✓ VERIFIED (regression) | `tests/fixtures/report_shapes.py`'s 16-entry `FROZEN_HASHES` unchanged since prior verification (`git diff 0c709fd..HEAD` on `report_shapes.py` shows no `FROZEN_HASHES`/`LADDER_PINS` hunks). `snapshot_report_shapes.py --check`: `OK: 16 snapshot(s) ... match a fresh regeneration`, independently re-run. |
| 2 | Every assertion in that table is against an absolute expected hash string; none is relational | ✓ VERIFIED (regression) | Code path unchanged by 174-06 (only `check()` and `_clone_with_chip_override` were touched); `test_blast_radius_invariance.py`'s absolute-literal idiom re-confirmed unchanged by diff. |
| 3 | `build_db_diff`'s disposition and ladder output for the same frozen shapes is pinned and asserted the same way | ✓ VERIFIED (regression) | `LADDER_PINS` (16 entries) unchanged by diff; `test_build_db_diff_ladder_pin_for_all_shapes` and `test_ladder_pins_cover_all_four_build_db_diff_arms` both pass in the fresh 122-test run below. |
| 4 | The raw-CLI-token → `part_number` delta across the shipped database is a committed, measured artifact | ✓ VERIFIED (regression) | `part_number_delta.json` unchanged (`git diff` empty); `measure_part_number_delta.py --check` independently re-run: `OK: ... matches a fresh regeneration`. |
| 5 | A `MILESTONES.md` re-key ledger section exists with the fields a declared re-key must carry, and **the mechanism actually binds** | ✓ VERIFIED | Gap closed. Full adversarial re-test below — 9 independent attack legs against `.planning/MILESTONES.md` copies, all fail closed on the fixed checker and all confirmed RED (silently exit 0) against the pinned pre-fix blob `5c0c7c97097f8148182d8df87c75b250c4c3d3d8`. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Adversarial Re-Test of GATE-06 (independent execution, not the SUMMARY's transcripts)

Per the verification brief, the checker was exercised directly against deliberately corrupted **copies** of `.planning/MILESTONES.md` in a scratch directory (real file never touched). Fixed checker = current `tools/rekey/check_rekey_ledger.py` on HEAD (`b954d7cd`). Pre-fix blob = `git cat-file blob 5c0c7c97097f8148182d8df87c75b250c4c3d3d8` (the blob the plan itself pins as the RED baseline).

| # | Attack | Fixed checker | Pre-fix blob (must be RED) | Verdict |
|---|---|---|---|---|
| 1 | Baseline: real, unmutated `.planning/MILESTONES.md` | `OK: 6 ledger row(s), 6 MILESTONES.md row(s) bound`, exit 0 | — (not tested; this is the control) | ✓ PASS |
| 2 | **CR-02 leg (a), reproduced verbatim from the prior gap report:** fabricated, fully-declared duplicate row (`after=ffffffffffff`) inserted immediately before the real `RK-174-01-...` row | `ERROR: duplicate MILESTONES.md row for ledger_id 'RK-174-01-p177-readback-gating'`, exit 2 | `OK: ...`, exit 0 (confirmed RED) | ✓ PASS — gap closed |
| 3 | **CR-02 leg (b), reproduced verbatim:** surviving undeclared row's `shape_id`→`TOTALLY-WRONG-SHAPE`, `before`→`000000000000` | `ERROR: '...' MILESTONES.md row (shape_id, before)=('TOTALLY-WRONG-SHAPE', '000000000000') does not match ledger row ...`, exit 1 | `OK: ...`, exit 0 (confirmed RED) | ✓ PASS — gap closed |
| 4 | Uppercased `before` cell (`4DC282A5D596`) | `ERROR: ... does not match ...`, exit 1 | `OK: ...`, exit 0 (confirmed RED) | ✓ PASS |
| 5 | Wide `after` cell on undeclared row (14-char `ffffffffffffff`) | `ERROR: ... after cell 'ffffffffffffff' is not the exact literal '(undeclared)'`, exit 1 | `OK: ...`, exit 0 (confirmed RED) | ✓ PASS |
| 6 | Short `after` cell on undeclared row (11-char truncation) | `ERROR: ... after cell '4dc282a5d59' is not the exact literal '(undeclared)'`, exit 1 | `OK: ...`, exit 0 (confirmed RED) | ✓ PASS |
| 7 | Zero-row table (every `RK-174-` line stripped) | `ERROR: MILESTONES.md carries 0 RK-174- row(s) while the ledger declares 6 row(s)`, exit 1 | `OK: 6 ledger row(s), 0 MILESTONES.md row(s) bound`, exit 0 (confirmed RED) | ✓ PASS |
| 8 | Order-stability: two consecutive runs of the fixed checker over the identical (leg-5) corrupted input | `cmp` of the two stdout captures: identical | n/a | ✓ PASS |
| 9 | New attack not in the SUMMARY's own legs: orphan row (`RK-174-99-p999-fabricated`, no corresponding ledger row at all) inserted into an otherwise-clean copy | `ERROR: MILESTONES.md row 'RK-174-99-p999-fabricated' has no matching ledger row`, exit 1 | (not run against prefix; orthogonal check of the already-existing reverse-direction guard) | ✓ PASS |

All error text is verbatim-identical to what 174-06-SUMMARY.md transcribed. Independently confirmed both the GREEN behavior and the RED baseline for every leg the prior gap named plus one additional attack the verifier constructed (leg 9). **The binding mechanism now genuinely binds** — no combination of duplicated, fabricated, corrupted, or deleted `MILESTONES.md` rows tested produces a silent exit 0.

### CR-01 (results/plan aliasing) fix independently re-verified

```
same results object: False
same plan object: False
before: 6d3afbc52315 True   (== FROZEN_HASHES['m27c512-full-all-ok'])
after (mutation through clone, base unaffected): 6d3afbc52315 True
```

Reproduced in-process against `build_shape('m27c512-full-all-ok')` vs `build_shape('m27c512-full-canonical-name')`: the two shapes no longer share `results`/`plan`, and mutating the clone's `results[0].verdict` no longer moves the base's frozen hash. This matches 174-06-SUMMARY.md's transcript and independently confirms the fix, not just its RED/GREEN narration.

### Newly Surfaced Findings (post-gap-closure code review, not yet actioned by any plan)

`174-REVIEW.md` was regenerated at `b954d7cd` (2026-09-03T18:42:16Z), **after** 174-06's gap-closure commits and after the "update tracking after gap-closure wave" commit. This is a second, more recent review than the one the original gaps_found verification used, and it surfaced 1 new critical + 4 warnings + 2 info findings that no plan has yet addressed. Each was assessed against the phase's actual roadmap success criteria (not the code-review severity label alone), following the same standard the first verification applied to the original CR-01:

- **New CR-01 (renumbered): `render_shape()`/`_to_dict_with_db_diff()` mutate a cached, `functools.cache`-memoized `DiagnosticReport.db_diff` in place, for 6 of 16 shape ids.** Independently reproduced live: `build_shape('m27c512-full-all-ok').db_diff` is `None`, then becomes a populated `DbDiff(...)` after `render_shape('m27c512-full-all-ok')` runs once in-process, with `r1 is r2 == True`. Confirmed `dedup_fingerprint` never reads `db_diff` (`grep` over its full body: no match), so this does not threaten SC1/SC2. `LADDER_PINS`' ladder-disposition pins (SC3) are still confirmed byte-identical and passing in the fresh 122-test run — the bug is real but, exactly as the review states, currently masked by test ordering rather than defeating any committed truth today. **Carried forward as a WARNING**, same treatment the first verification gave the original (now-fixed) CR-01 — it is a collateral-false-state risk for a future phase, not a silent-pass-of-a-real-change risk today.
- **WR-02: `check()`'s app-side `ledger_by_id` dict silently keeps only the last row for a duplicated `ledger_id`, asymmetric with the MILESTONES.md-side duplicate guard 174-06 just added.** Independently probed with three constructed adversarial `ledger_rows` lists (two declared rows with conflicting `after_hash`, undeclared+declared pairs in both orders) — in every case tested, `check()`'s first loop (which iterates the raw `ledger_rows` list, not the deduplicated dict) still produced at least one `ERROR:` and a non-zero-implying result, because the loop checks each row against the shared `milestones_rows.get(ledger_id)` independently rather than through `ledger_by_id`. Could not construct a case where the app-side duplicate lets a corrupted or fabricated `MILESTONES.md` row pass silently — the `ledger_by_id` dict is used only for the reverse-direction "orphan MILESTONES.md row" check, not for validating declared/undeclared correctness. This is a real robustness/error-message-quality gap (no dedicated "duplicate ledger_id" diagnostic on the app side, unlike the MILESTONES side) and a legitimate defense-in-depth improvement, but adversarial testing did not find it capable of defeating GATE-06's actual "cannot silently pass a corrupted or fabricated row" guarantee. Also independently backstopped today by `test_ledger_id_values_are_unique` in the app-side pytest suite (confirmed passing). **Carried forward as a WARNING**, not a gap.
- **WR-01 (renumbered): GATE-05 snapshot-drift coverage is 1-of-16 shapes in automated `pytest`, not all 16.** `snapshot_report_shapes.py --check` (a separate script, independently re-run and confirmed clean) does cover all 16; only the `pytest`-native leg is narrow. Does not defeat SC1 as measured today (all 16 confirmed drift-free via the script). WARNING, not a gap.
- **WR-03, WR-04, IN-01, IN-02** — all pre-existing, all assessed by the review itself as not currently defeating any committed truth (ambiguity-detection gap in the corpus generator, an `assert` strippable under `-O`, an unbounded `gh issue list --limit 300`, undocumented "last wins" JSON-block selection). Consistent with the review's own classification; no independent evidence found that any of them defeats a roadmap success criterion today.

**None of these four post-gap-closure findings falsify any of the five roadmap success criteria as directly, adversarially re-tested above.** They are real, independently-reproduced defects worth fixing before the phases they threaten (177+, and any future mutation-based anti-vacuity leg), but under the same goal-backward standard this phase's own first verification applied, they do not block this phase's goal today.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/tests/fixtures/report_shapes.py` | 16 shape builders, frozen tables, non-aliasing clone | ✓ VERIFIED | `_clone_with_chip_override` now uses `copy.deepcopy` on `results`/`plan` (confirmed by reading lines 484-504 and by live reproduction above). |
| `tools/rekey/check_rekey_ledger.py` | Fail-closed cross-tree binding checker | ✓ VERIFIED | Duplicate-`ledger_id` guard in `parse_milestones_rows` (exit 2), undeclared-branch `shape_id`/`before_hash`/exact-literal validation, zero-row guard — all read directly and all adversarially re-exercised above. |
| `firestarter_app/tests/test_rekey_ledger.py` | 7 new subprocess-level legs | ✓ VERIFIED | All 7 named tests collected and pass (`10 passed` selecting the parametrized family, matching the 4-case `after_cell` parametrization + 6 others). |
| `firestarter_app/tests/test_blast_radius_invariance.py` | 2 new non-aliasing regression legs | ✓ VERIFIED | Both collected and pass; independently re-confirmed via direct in-process reproduction. |
| Evidence transcripts (3 new files) | RED-then-GREEN pairs against pinned pre-fix blobs | ✓ VERIFIED | All 3 present, non-trivial (10/18/43 lines), and every `rc`/error-text pair independently reproduced by the verifier rather than trusted from the file. |
| `.planning/MILESTONES.md` (v1.36 Re-Key Ledger section) | 6 narrated rows, correct fields | ✓ VERIFIED | Unchanged since prior verification; still present and narrated. |

### Behavioral Spot-Checks / Regression

| Behavior | Command | Result | Status |
|---|---|---|---|
| Four-module phase suite | `pytest tests/test_blast_radius_invariance.py tests/test_rekey_ledger.py tests/test_devtest_issue_corpus.py tests/test_part_number_delta_drift.py -o addopts="" -q` | `122 passed in 11.10s` | ✓ PASS |
| Full app suite (excluding known pre-existing `test_skip_census.py` timeouts) | `pytest -o addopts="" -q --ignore=tests/test_skip_census.py` | `2072 passed, 1 warning in 210.40s` — zero failures | ✓ PASS (no regressions) |
| Snapshot drift | `snapshot_report_shapes.py --check` | `OK: 16 snapshot(s) ... match a fresh regeneration` | ✓ PASS |
| Part-number-delta drift | `measure_part_number_delta.py --check` | `OK: ... matches a fresh regeneration` | ✓ PASS |
| Devtest issue corpus drift | `build_devtest_issue_corpus.py --check` | `OK: ... matches a fresh regeneration` | ✓ PASS |
| Frozen artifacts byte-identical to pre-174-06 state | `git diff 0c709fd..HEAD --stat` over `reports/`, `shape_ids.json`, `devtest_issue_corpus.json`, `part_number_delta.json`, `rekey_ledger.py`; and a targeted diff of `FROZEN_HASHES`/`LADDER_PINS` in `report_shapes.py` | empty in all cases | ✓ PASS — no accidental re-key |
| Working tree clean (meta + submodule) | `git status --porcelain` (both repos) | empty in both | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| GATE-01 | 174-01, 174-02, 174-03, 174-06 (CR-01 fix) | Frozen `(shape → 12-hex hash)` table exists | ✓ SATISFIED | 16-shape `FROZEN_HASHES`, unchanged and passing; aliasing hazard that could have collaterally reddened it (old CR-01) is fixed and independently re-verified. |
| GATE-02 | 174-01, 174-02, 174-03 | Absolute-value assertion discipline | ✓ SATISFIED | Unchanged, re-confirmed by diff. |
| GATE-03 | 174-01, 174-02 | `build_db_diff` ladder output pinned | ✓ SATISFIED | `LADDER_PINS` unchanged, 122-test run passing. |
| GATE-04 | 174-04 | Part-number delta measured artifact | ✓ SATISFIED | Unchanged, `--check` clean. |
| GATE-05 | 174-01 through 174-04 | Report corpus lives in `firestarter_app/tests/fixtures/` | ✓ SATISFIED | Unchanged; note WR-01 (new review) flags automated-`pytest` coverage breadth as a WARNING, not a blocker — the standalone `--check` script covers all 16. |
| GATE-06 | 174-01, 174-03, 174-05, **174-06** | Every deliberate re-key recorded in `MILESTONES.md`, bound to the app-side ledger | ✓ SATISFIED | **Gap closed.** Binding mechanism adversarially re-tested with 9 independent attack legs (2 reproduced verbatim from the prior gap, 4 from the SUMMARY's own claimed fixes, 1 order-stability check, 1 novel orphan-row attack, 1 clean-baseline control) — all fail closed on the fixed checker and all confirmed RED against the pinned pre-fix blob. |

No orphaned requirements: `GATE-01` through `GATE-06` remain the complete set REQUIREMENTS.md maps to Phase 174, and 174-06's frontmatter claims `[GATE-01, GATE-02, GATE-06]` in addition to the plans that already claimed the others.

**Bookkeeping note (not a gap, carried forward unchanged):** `.planning/REQUIREMENTS.md`'s checkboxes for GATE-01 through GATE-06 (lines 40-45) and its Traceability table (lines 148-153) still read unchecked / "Pending" despite all six being satisfied in the codebase. Documentation-sync gap in REQUIREMENTS.md itself, not counted against the phase's score, per the same treatment the first verification gave it.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `firestarter_app/tools/snapshot_report_shapes.py` / `test_blast_radius_invariance.py` | 92 / 404 | New-review CR-01: in-place `db_diff` mutation on 6 cached shapes | ⚠️ Warning (carried forward) | Collateral stale-state risk for a future `db_diff is None` assertion or repeated snapshot generation; does not currently defeat any of the 5 success criteria (confirmed `dedup_fingerprint` never reads `db_diff`). |
| `tools/rekey/check_rekey_ledger.py` | 129 | New-review WR-02: app-side `ledger_by_id` dict silently keeps only the last duplicate row | ⚠️ Warning (carried forward) | Adversarial re-testing found no scenario where this lets a corrupted/fabricated MILESTONES.md row pass silently; a real diagnostic-quality gap, backstopped today by `test_ledger_id_values_are_unique`. |
| `firestarter_app/tests/test_blast_radius_invariance.py` | 561-569 | New-review WR-01: automated `pytest` snapshot-drift coverage is 1/16 shapes | ⚠️ Warning (carried forward) | The standalone `snapshot_report_shapes.py --check` script (not `pytest`) already covers all 16 and is clean; GATE-05 holds today via that script. |
| `firestarter_app/tools/build_devtest_issue_corpus.py` | 169-187 / 78-102 / 116-130 | New-review WR-03, IN-01, IN-02 | ℹ️ Info / Warning (carried forward) | No independent evidence any currently defeats a committed truth; flagged for future hardening. |
| `firestarter_app/tests/fixtures/report_shapes.py` | 647-650 | New-review WR-04: bare `assert` for D-04 reservation check strippable under `-O` | ⚠️ Warning (carried forward) | Not exercised under `-O` in this project's CI as far as verified; a defense-in-depth gap, not a currently-observed failure. |

No `TBD`/`FIXME`/`XXX` debt markers found in any of the four files 174-06 modified. Comment-line count matches the plan's own prohibition exactly: `tools/rekey/check_rekey_ledger.py` carries exactly 1 `#` line (its shebang); `test_rekey_ledger.py`, `report_shapes.py`, `test_blast_radius_invariance.py` carry 0.

### Human Verification Required

### 1. GitHub Actions actually schedules `rekey-ledger-check.yml`

**Test:** After this phase's commits reach a remote branch matching the workflow's triggers (`beta` or any `gsd/**` branch push, or a PR targeting `beta`), run `gh run list --workflow=rekey-ledger-check.yml --limit 5`.
**Expected:** At least one run appears, with a conclusion (success/failure) rather than no runs at all.
**Why human:** No network path exists in this sandbox to make GitHub Actions schedule a run. Carried forward unchanged from the prior (initial) verification — still unproven on GitHub itself, though the workflow file, its trigger branches (`beta`, `gsd/**`), and its invocation of the now-fixed checker were all re-confirmed by direct reading.

### 2. Post-gap-closure code review findings (4 warnings, 1 renumbered critical) are unactioned — human call on whether to schedule a follow-up plan now or defer

**Test:** Review the four carried-forward findings above (`db_diff` cache aliasing, app-side duplicate-`ledger_id` diagnostic asymmetry, 1/16 `pytest` snapshot-drift coverage, and the three lower-severity items) and decide whether any should be closed before Phase 177 (the first consumer phase) lands, versus tracked as backlog.
**Expected:** A decision — fix now via a 174-07 gap-closure-style plan, or explicitly accept and track for a later phase.
**Why human:** These are judgment calls about acceptable risk versus scope creep for a phase whose gap gate (GATE-06) is now genuinely closed; the verifier's adversarial testing found none of them defeats a roadmap success criterion today, but that is a statement about the present state, not about acceptable risk for Phase 177+.

### Gaps Summary

**The single recorded gap is closed.** Re-verification independently, adversarially re-exercised the exact two `CR-02` legs the prior verification used to fail this phase (fabricated duplicate declared row; corrupted `shape_id`/`before_hash` on the surviving undeclared row) plus seven additional legs (uppercase hash, wide/short `after` cell, zero-row table, order-stability, and a novel orphan-row attack not in any prior transcript) — every one fails closed on the fixed `tools/rekey/check_rekey_ledger.py`, and every one is confirmed RED (silently exits 0) against the pinned pre-fix blob `5c0c7c97097f8148182d8df87c75b250c4c3d3d8`, ruling out an unreachable-gate false pass. The companion CR-01 (results/plan aliasing) fix was also independently reproduced live. All five roadmap success criteria now verify directly against the codebase, not merely against SUMMARY.md's narration, and the full 2072-test app suite (excluding the pre-existing, unrelated `test_skip_census.py` timeouts) shows zero regressions.

Status is `human_needed` rather than `passed` for two reasons, neither of which is a gap: (1) the GitHub Actions on-remote firing check carried forward from the first verification remains genuinely unprovable in this sandbox, and (2) a second, more recent code review (`174-REVIEW.md` at `b954d7cd`, committed after 174-06's own completion) surfaced four new-or-renumbered findings that no plan has yet addressed. Independent adversarial testing of all four found none capable of defeating any of the five roadmap success criteria today — they are legitimate carried-forward risk for Phase 177+, assessed and classified using the exact same goal-backward standard the first verification applied to the original CR-01 — but a decision on whether to close them now or track them forward belongs to a human, not the verifier.

---

_Verified: 2026-09-03T18:44:55Z_
_Verifier: Claude (gsd-verifier)_
