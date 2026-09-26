---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
plan: 02
subsystem: dev-test-engine
tags: [derive-plan, write-scope, plan-corpus, test-hygiene, pytest, sdp-leg]

requires:
  - phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
    plan: "01"
    provides: "to_dict()'s is_uv key, SCHEMA_VERSION 2.0, and the proven additive-key-cannot-re-key mechanism this plan's measurements build on"
provides:
  - "a measured sha256 digest over all 677 reachable-scope plans, proving D-09's write_scope==\"partial\" iff is_uv equivalence rather than asserting it"
  - "five zero-valued de-risking measurements for D-08: empty locked_destructive at reachable scope, both sdp_oracle_applicable and count_applicable unchanged by their locked_destructive-derived terms, resolve_write_scope/Plan.is_uv agreement over all 677 names, and zero production write_scope=\"none\" callers"
  - "a fully retired write_scope=\"none\" test surface: zero explicit occurrences, zero bare derive_plan calls, across all of tests/"
  - "plan_corpus() re-keyed to one plan per part number at its single reachable scope, with every count pin it feeds re-measured against the regenerated tests/fixtures/plan_shapes.json"
affects: [181-04]

actuals:
  tokens: 26900
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "canonical serializer + sha256 digest as an equivalence proof: define ONE field order once, record it in the evidence transcript, so a later plan (181-04) can recompute the identical digest rather than trusting prose"
    - "re-point vs delete disposition, decided per-site by whether the test's claim survives at the reachable scope, never by blanket rule"
    - "measured re-anchoring: every moved count pin (corpus size, total_steps, unsupported_steps, family counts) comes from re-running the generator or the corpus, never from halving the old number by hand"

key-files:
  created:
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-02-derive-plan-equivalence.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-02-none-surface-retirement.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-02-corpus-reanchor.txt
  modified:
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py
    - firestarter_app/tests/test_chip_test_blank_check_order.py
    - firestarter_app/tests/test_chip_test_timing.py
    - firestarter_app/tests/test_erase_flag_invariants.py
    - firestarter_app/tests/test_derive_plan_structural_sentinel.py
    - firestarter_app/tests/test_diagnostic_report.py
    - firestarter_app/tests/plan_corpus.py
    - firestarter_app/tests/test_derive_plan_no_drop_sweep.py
    - firestarter_app/tests/test_plan_shapes_drift.py
    - firestarter_app/tests/fixtures/plan_shapes.json
    - firestarter_app/tools/measure_plan_shapes.py

key-decisions:
  - "tools/measure_plan_shapes.py was edited even though it is not in this plan's <files> list. The plan's own action text authorizes this explicitly (\"Update the generator only if it hard-codes a scope list of its own\"), and it was not discretionary: the generator hard-coded a corpus[(name, \"full\")]/corpus[(name, \"partial\")] pair-per-chip sweep, and after the re-key that call throws KeyError -- the generator could not run at all without the update. Its shape_families schema moved from a {\"full\": [...], \"partial\": [...]} pair to a single \"steps\" list per family, and validate() gained a UV/non-UV family-mixing check (measured: none of the 8 families mixes a UV and a non-UV chip)."
  - "total_steps and unsupported_steps landed at EXACTLY half their prior value (8124=16248/2, 4652=9304/2) -- a real, measured property (write_execute is True at both full and partial scope, so a chip's step count and supported flags are scope-invariant; only the write op's literal string and write_region differ), not an assumption substituted for the required regeneration. Verified by actually running tools/measure_plan_shapes.py, per the plan's explicit prohibition against a re-anchored pin from arithmetic on the number it replaces."
  - "Fixed a real bug the re-key surfaced, not merely a rename: tests/test_derive_plan_structural_sentinel.py's 28C-family carve-out test built `carveout_chips = {name for name, _scope in carveout_plans}`, valid only under the old (name, scope) tuple key. Under the single-key corpus this raises (a plain string is not a 2-tuple) rather than silently misbehaving -- caught by running the test. Fixed to `carveout_chips = set(carveout_plans)`."
  - "Every rationale for a re-point vs delete disposition is recorded here and in evidence/181-02-none-surface-retirement.txt, never as a new # comment in the test files themselves (D-26). Existing pre-existing comments that became stale because of an edit (e.g. a cross-reference to a test that no longer covers the \"none\" scope) were reworded minimally to stay accurate -- not left false, and not expanded into new rationale."
  - "The whole-repo porcelain leg is documented dirty for reasons outside this plan, matching 181-01-SUMMARY.md's precedent exactly: firestarter_app/firestarter/serial_comm.py and tests/test_probe_spurious_setup_ack.py are a separate, concurrently active /gsd-debug session's own work (confirmed by commit history: 31f3455 and b2546da landed on this shared branch during this plan's execution window, neither touching a file in this plan's files_modified list). Scoped to this plan's own files, porcelain is clean."
  - "actuals.commits (5) is the count of THIS plan's own commits across both repos (3 meta + 2 app), hand-verified by hash against the concurrent session's interleaved commits -- not the raw #3968 ledger delta, which on this shared branch would over-count by the 2 foreign commits (2ca18cdb, acd1cd74 in meta; b2546da in app) that landed between this plan's own commits."

requirements-completed: [RPT-B2]

coverage:
  - id: D1
    description: "D-09's write_scope equivalence (partial iff is_uv, else full) is a measured sha256 digest over all 677 reachable-scope plans, with the canonical serializer's field order recorded so 181-04 can reproduce it"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "evidence/181-02-derive-plan-equivalence.txt#reachable_scope_digest"
        status: pass
      - kind: other
        ref: "Task 1 verify leg: grep for a 64-hex reachable_scope_digest= line and the recorded serializer_field_order="
        status: pass
    human_judgment: false
  - id: D2
    description: "D-08's two dead-path claims (Plan.locked_destructive empty at reachable scope; sdp_oracle_applicable's second arm and count_applicable's locked term both provably dead) are measured zero over all 677 names and both SDP classes, not merely believed"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "evidence/181-02-derive-plan-equivalence.txt: rows_with_nonempty_locked_destructive_at_reachable_scope=0, sdp_oracle_applicable_second_arm_changes_result_for=0, count_applicable_m_changes_without_locked_term_for=0"
        status: pass
    human_judgment: false
  - id: D3
    description: "181-PATTERNS.md's claim that the chip_test.py:894 SDP append is 'not a write_scope=\"none\" append' is corrected in writing, with the code citation proving it is reachable only at write_scope=\"none\""
    verification:
      - kind: other
        ref: "evidence/181-02-derive-plan-equivalence.txt, numbered correction section"
        status: pass
    human_judgment: false
  - id: D4
    description: "The write_scope=\"none\" test surface is retired to zero across all of tests/ -- 78 explicit occurrences and 15 bare derive_plan calls, with a disposition (re-point or delete) recorded for every one of the 93 sites in this plan's scope"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "AST census over tests/: bare_derive_plan_after=0, explicit_none_after=0 (Task 2 verify leg)"
        status: pass
      - kind: other
        ref: "evidence/181-02-none-surface-retirement.txt: per-site disposition ledger, 25 repointed + 52 deleted = 77 (Task 2's own scope), plus tests/plan_corpus.py's 1 (Task 3)"
        status: pass
    human_judgment: false
  - id: D5
    description: "test_derive_plan_structural_sentinel.py's module-level _resolve_write_scope import and its own test are removed, so plan 181-04 cannot redden all 31 tests in that module at collection time"
    verification:
      - kind: unit
        ref: "grep leg: neither 'from firestarter.cli_handlers import _resolve_write_scope' nor 'def test_resolve_write_scope_returns_partial_for_every_uv_row' present"
        status: pass
    human_judgment: false
  - id: D6
    description: "plan_corpus() is re-keyed to one plan per part number (677 entries, string keys) at the single reachable scope, and every count pin it feeds (corpus size, total_steps, unsupported_steps, live-erase/carve-out/UV/uv-slot populations) is re-measured, not computed by halving"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "Task 3 verify legs: corpus_size=677, part_numbers=677, M8720 plan carries a write region; literal 1354 absent from tests/"
        status: pass
      - kind: other
        ref: "evidence/181-02-corpus-reanchor.txt: full before/after table, all labelled measured"
        status: pass
    human_judgment: false
  - id: D7
    description: "tests/fixtures/plan_shapes.json is regenerated via tools/measure_plan_shapes.py (never hand-edited), keeps its _generated_by banner, and _EXPECTED_AGGREGATE in test_plan_shapes_drift.py matches it exactly"
    verification:
      - kind: unit
        ref: "tests/test_plan_shapes_drift.py (6 passed); Task 3 verify leg 4 (banner + _EXPECTED_AGGREGATE AST check)"
        status: pass
    human_judgment: false
  - id: D8
    description: "All 19 FROZEN_HASHES literals in tests/fixtures/report_shapes.py remain byte-identical to app base 04fd982, and zero # comments were added to any touched file (tokenize COMMENT-token census stays at or below every app-base baseline)"
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py -k test_dedup_fingerprint_is_frozen (19 passed); git diff 04fd982 --stat -- tests/fixtures/report_shapes.py (empty)"
        status: pass
      - kind: other
        ref: "tokenize COMMENT-token census across the seven baselined files: all at or below baseline (565/621, 220/227, 20/27, 21/21, 4/4, 183/183, 0/0)"
        status: pass
    human_judgment: false
  - id: D9
    description: "Whole-repo porcelain across the meta repo, the firmware submodule, and the app repo after this plan's own commits"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain (clean); git -C /workspaces/firestarter_app status --porcelain scoped to this plan's own 12 files (clean)"
        status: unknown
    human_judgment: true
    rationale: "Identical situation to 181-01-SUMMARY.md's D7: a concurrent, unrelated /gsd-debug session is actively committing to firestarter/serial_comm.py and tests/test_probe_spurious_setup_ack.py on this shared branch (commits 31f3455 and b2546da landed during this plan's execution window; neither file is in this plan's files_modified list). This plan does not revert, stash, or otherwise act on that unrelated work per the deviation-rule scope boundary. A human should confirm this is understood as external before treating the whole-repo porcelain acceptance criterion as met."

duration: 65min
completed: 2026-09-09
status: complete
---

# Phase 181 Plan 02: write_scope="none" test-surface retirement and plan_corpus re-key Summary

**D-09's write_scope equivalence is now a measured sha256 digest over all 677 reachable-scope plans (not a claim in prose), the entire `write_scope="none"` test surface (93 sites: 78 explicit + 15 bare) is retired with 15 tests deleted and 25 re-pointed, and `plan_corpus()` is re-keyed from a 1,354-entry two-scope sweep to a 677-entry single-reachable-scope one, with every count pin it feeds re-measured against a regenerated `tests/fixtures/plan_shapes.json` -- turning plan 181-04's coming deletion into a uniform kwarg-drop across 102 identical call sites instead of a 117-site migration entangled with a product deletion.**

## Performance

- **Duration:** ~65 min
- **Started:** 2026-09-09T09:50:00Z (approx.)
- **Completed:** 2026-09-09T10:44:00Z
- **Tasks:** 3 of 3 completed
- **Files modified:** 12 (7 in Task 2, 6 in Task 3 -- test_derive_plan_structural_sentinel.py appears in both) + 3 evidence transcripts + this SUMMARY

## Accomplishments

- **Task 1 — measured, not asserted.** A canonical serializer (plan name, reason, is_uv, then each step's op/supported/reason/destructive/write_region/region_policy/full_device_permitted, then locked_destructive) produces a stable sha256 digest over all 677 part numbers at the reachable scope (`"partial"` iff `is_uv_eprom`, else `"full"`). Five de-risking measurements all came back zero: `Plan.locked_destructive` is empty for every one of the 677 names at reachable scope; `sdp_oracle_applicable`'s second arm never changes the result; `count_applicable`'s `M` is unchanged without the locked term; `_resolve_write_scope` matches `Plan.is_uv` for all 677 names; and an AST census over `firestarter/` found zero production `derive_plan` callers using `write_scope="none"` (or the bare-defaults-to-"none" form). Also re-measured and corrected two under-counts from the source documents: `explicit_write_scope_none_occurrences=78` (not CONTEXT.md's ~69) and `bare_derive_plan_calls_in_tests=15` (found by neither document). `181-PATTERNS.md`'s claim about the `chip_test.py:894` SDP append was proven wrong and corrected in the transcript: it IS reachable only at `write_scope="none"`.
- **Task 2 — the `"none"` surface is gone.** Every one of the 93 named sites (78 explicit occurrences + 15 bare calls) in this task's 7-file scope is resolved: 25 re-pointed to an explicit `"full"`/`"partial"` where a surviving claim existed, 52 deleted (comments, literal strings, or whole tests) where the subject was the omitted-write shape itself. 15 tests deleted outright, with each one's claim and reason recorded. The module-level `from firestarter.cli_handlers import _resolve_write_scope` import and its own test were removed from `test_derive_plan_structural_sentinel.py`, pre-emptively stopping plan 181-04 from reddening all 31 tests in that module at collection time.
- **Task 3 — the corpus now describes the domain `dev test` can actually reach.** `plan_corpus()` returns `{name: Plan}` (677 entries, string keys) instead of `{(name, scope): Plan}` (1,354 entries). Every consumer's `(name, scope)` lookup and key-unpacking moved to the single-key form, and every count pin it fed was re-measured: corpus size 1354→677, `total_steps` 16248→8124, `unsupported_steps` 9304→4652 (both landed at *exactly* half — a real, measured property of the domain, not an assumed halving), live-erase plans 608→304, 28C-family carve-out plans 162→81, UV plans 540→270, uv-slot steps 1080→540. `tools/measure_plan_shapes.py` (not in this plan's `<files>` but authorized and made necessary by its own action text) was updated to sweep the same single reachable scope, and `tests/fixtures/plan_shapes.json` was regenerated: `plans` 1354→677, `total_steps`/`unsupported_steps` halved, `rows`/`distinct_part_numbers`/`distinct_shape_families` unchanged at 746/677/8. `tests/test_plan_shapes_drift.py`'s `_EXPECTED_AGGREGATE` was re-anchored to the regenerated artifact.
- **A real bug fixed, not just a rename.** The 28C-family carve-out test's `{name for name, _scope in carveout_plans}` line only worked under the old tuple key; under the new corpus it would raise at runtime. Caught by running the test after the re-key, fixed to `set(carveout_plans)`.
- **Zero product-source lines changed.** Every edit landed in `firestarter_app/tests/` or `firestarter_app/tools/` (the latter explicitly exempt from the no-comments rule). `firestarter/chip_test.py`, `firestarter/cli_handlers.py`, and every other product module are byte-unchanged from app base `04fd982` (confirmed by `git diff 04fd982 --stat`, modulo the concurrent session's unrelated `serial_comm.py` edit — see Deviations).
- **Zero `#` comments added.** `tokenize` COMMENT-token census for the seven files with a defined baseline stays at or below every one: `test_chip_test.py` 565/621, `test_chip_test_sdp_leg.py` 220/227, `test_erase_flag_invariants.py` 20/27, `test_chip_test_blank_check_order.py` 21/21, `test_chip_test_timing.py` 4/4, `test_diagnostic_report.py` 183/183, `test_derive_plan_structural_sentinel.py` 0/0. Every rationale that would otherwise have been a new comment is recorded in this SUMMARY and in the evidence transcripts instead.
- **All 19 `FROZEN_HASHES` literals stay byte-identical.** `test_dedup_fingerprint_is_frozen`'s 19-way parametrization passes in full, and `tests/fixtures/report_shapes.py` has zero diff from app base — this plan touched no frozen-hash fixture.

## Task Commits

Each task was committed atomically, split across the app submodule (code) and the meta repo (evidence):

1. **Task 1: D-09 equivalence digest and D-08 de-risking measurements**
   - `7537adb0` (docs, meta repo): `181-02-derive-plan-equivalence.txt` — no app-repo commit (the task's own instruction: "Change no file under `firestarter_app/` in this task")
2. **Task 2: retire the `write_scope="none"` test surface**
   - `784e74c` (test, app repo): 15 tests deleted, 25 sites re-pointed, across 7 test files
   - `cf57f100` (docs, meta repo): `181-02-none-surface-retirement.txt`
3. **Task 3: re-key `plan_corpus()` and re-measure every count pin**
   - `851c93b` (test, app repo): the re-key, its 4 consumer-module updates, the generator update, and the regenerated `plan_shapes.json`
   - `a582681a` (docs, meta repo): `181-02-corpus-reanchor.txt`

**Plan metadata commit:** this SUMMARY.md, committed separately per the sequential-executor protocol (STATE.md/ROADMAP.md are NOT touched — owned by the orchestrator).

_All three tasks carry `type="auto"` (Task 1) or plain test-migration semantics (Tasks 2-3); none carries `tdd="true"`. Task 1 produces zero code changes by design (a pure measurement task), so there is no RED/GREEN cycle to report for it._

## Files Created/Modified

- `firestarter_app/tests/test_chip_test.py` — 12 bare calls made explicit; 3 explicit "none" sites re-pointed; 10 tests deleted (their claim had no subject after D-08/D-09); 1 test rewritten to drop its none-scope comparison while keeping its full-scope structural assertion
- `firestarter_app/tests/test_chip_test_sdp_leg.py` — 2 bare calls made explicit; 3 explicit sites re-pointed (including the shipped-ops-sequence before-image, re-measured at `write_scope="full"`); 2 tests deleted
- `firestarter_app/tests/test_chip_test_blank_check_order.py` — 1 test deleted (the write_scope="none" case-2 counterpart); module docstring's case enumeration corrected
- `firestarter_app/tests/test_chip_test_timing.py` — 4 explicit sites re-pointed to `write_scope="full"` (the fixture chip, w29c020, is not UV)
- `firestarter_app/tests/test_erase_flag_invariants.py` — Leg 6 (the AT28C256 write_scope="none" plan-shape pin) deleted in full, including its constants; coverage docstring moved from 6 legs to 5
- `firestarter_app/tests/test_derive_plan_structural_sentinel.py` — module-level `_resolve_write_scope` import + its test removed; 1 explicit "none" site's real-derive_plan assertion block dropped (its two hand-built-plan cases, unrelated to write_scope, are untouched); every `(name, scope)` corpus lookup moved to single-key form; 8 count pins re-anchored; the 28C carve-out tuple-unpack bug fixed
- `firestarter_app/tests/test_diagnostic_report.py` — the shared `_build_report` helper's bare call made explicit, computed per-chip from `is_uv_eprom` rather than hardcoded, since the helper accepts an overridable `chip_name`
- `firestarter_app/tests/plan_corpus.py` — `plan_corpus()` re-keyed to `{name: Plan}`; `SWEEP_SCOPES` removed; the module docstring's D-08 paragraph rewritten for the single-scope domain
- `firestarter_app/tests/test_derive_plan_no_drop_sweep.py` — both `corpus[("M8720", "full")]` lookups moved to `corpus["M8720"]`; `SENSITIVITY_SLICE` rebuilt as 40 plain names; `plan_count`/`result_count`/`unsupported_count` pins re-anchored
- `firestarter_app/tests/test_plan_shapes_drift.py` — `_EXPECTED_AGGREGATE` re-anchored to the regenerated artifact
- `firestarter_app/tests/fixtures/plan_shapes.json` — regenerated via `tools/measure_plan_shapes.py`
- `firestarter_app/tools/measure_plan_shapes.py` — `derive()`/`validate()` updated to sweep the single reachable scope; `shape_families` schema simplified to one `"steps"` list per family; added a UV/non-UV family-mixing check
- `.planning/phases/181-.../evidence/181-02-derive-plan-equivalence.txt` — Task 1's digest + de-risking transcript
- `.planning/phases/181-.../evidence/181-02-none-surface-retirement.txt` — Task 2's per-site disposition ledger + deleted-test list
- `.planning/phases/181-.../evidence/181-02-corpus-reanchor.txt` — Task 3's before/after aggregate transcript

## Deleted Tests — claim, reason, and where the claim's residue lives

1. **`test_chip_test.py:test_derive_plan_strip_default_only_destructive_ops_removed`** — Claim: at `write_scope="none"`, the executable steps set is exactly `{id, read, blank-check}`. Reason: this IS the omitted-write shape; no residue.
2. **`test_chip_test.py:test_derive_plan_advisory_populated_when_non_destructive`** — Claim: `locked_destructive` is non-empty at `write_scope="none"`. Reason: Task 1 measured `locked_destructive` is empty at every reachable scope; the claim describes a shape that no longer exists.
3. **`test_chip_test.py:test_derive_plan_na_erase_advisory_only_records_write`** — Claim: AM2716's erase is NA and not added to `locked_destructive` at `write_scope="none"`. Reason: the `locked_destructive` half has no subject; the surviving half (erase NA for AM2716) is already covered by `test_derive_plan_uv_eprom_erase_na` (same chip, now at `write_scope="partial"`).
4. **`test_chip_test.py:test_derive_plan_write_scope_none_unchanged_by_region_policy`** — Claim: named delete candidate in the plan text (tests the "none" parameter value itself).
5. **`test_chip_test.py:test_derive_plan_write_scope_rejects_unknown_value`** — Claim: named delete candidate (tests the parameter's own validation ladder, not a surviving behaviour).
6. **`test_chip_test.py:test_no_write_step_means_no_cycle_block`** — Claim: a plan with zero write steps yields `cycle_block_bounds() is None`. Reason: at reachable scope every write-capable chip's plan HAS a write step (either "full" or "partial"); there is no longer a natural way to produce a real derive_plan-derived plan with zero write steps, and the plan's own instructions forbid inventing a hand-built replacement shape to keep this assertion alive.
7. **`test_chip_test.py:test_count_applicable_uv_counts`** — Claim: `count_applicable`'s N<M banner fires for AM2716 at `write_scope="none"` (m_applicable=4 from 3 supported + 1 locked). Reason: at reachable scope `locked_destructive` is always empty, so N always equals M — the banner-triggering shape this test measured is unreachable.
8. **`test_chip_test.py:test_count_applicable_eeprom_counts`** — Same reason as #7, for M8720.
9. **`test_chip_test.py:test_r5_laundering_write_scope_none_locks_all_six_and_never_calls_sdp_lock`** — Claim: an ALLOW chip's SDP leg is laundered into `locked_destructive` at `write_scope="none"`. Reason: its own docstring already stated `write_scope="none"` is unreachable and library/test surface only; the shape it pins no longer exists anywhere in the codebase's live parameter range.
10. **`test_chip_test.py:test_count_applicable_sdp_does_not_change_shipped_non_sdp_counting`** — Claim: re-verifies the exact numbers from #7 and #8 to prove SDP counting didn't silently touch the shipped non-SDP pins. Reason: its subject (those two tests' pinned numbers) no longer exists.
11. **`test_chip_test_sdp_leg.py:test_allow_write_scope_none_locks_six_sdp_leg_steps_and_moves_the_banner`** — Claim: same banner-firing shape as #7/#8, for the SDP leg specifically. Reason: same as #7.
12. **`test_chip_test_sdp_leg.py:test_refuse_write_scope_none_is_byte_identical_to_pre_phase134`** — Claim: a REFUSE chip's `write_scope="none"` plan is byte-identical to a pre-Phase-134 snapshot. Reason: the shape being pinned (three shipped `locked_destructive` entries, no SDP-leg entries) no longer exists at any reachable scope.
13. **`test_chip_test_blank_check_order.py:test_m8720_write_scope_none_is_unchanged`** — Claim: at `write_scope="none"`, no erase step runs so blank-check stays at its historic pre-erase position. Reason: this is a negative-space test about the absence of a scope's erase step; the scope itself is retired.
14. **`test_erase_flag_invariants.py:test_at28c256_write_scope_none_shape_is_pinned`** ("Leg 6") — Claim: AT28C256's `write_scope="none"` plan is pinned at 3 steps (id, read, blank-check) with 9 ops in `locked_destructive`. Reason: this was explicitly the shape "this phase changed that no committed test previously watched" (per its own docstring) — the shape it watches for is retired along with the scope.
15. **`test_derive_plan_structural_sentinel.py:test_resolve_write_scope_returns_partial_for_every_uv_row`** — Claim: `_resolve_write_scope` returns "partial" for every UV row (270 of 677), "full" for every other row (407). Reason: Task 1's `evidence/181-02-derive-plan-equivalence.txt` already measures exactly this claim over all 677 names (`resolve_write_scope_matches_plan_is_uv_for=677`, `resolve_write_scope_mismatches=0`) — cited there as the claim's new home. Removing this test (and the module-level `_resolve_write_scope` import it required) is also what stops plan 181-04 reddening all 31 tests in this module at collection time when it deletes `_resolve_write_scope`.

## Rewritten (not deleted) tests — surviving claim kept, "none"-only claim dropped

- **`test_chip_test.py:test_derive_plan_destructive_flag_strips_not_annotates`** — dropped the `plan_default` (write_scope="none") comparison; kept the full-scope exact op-sequence assertion (including the SDP leg's 6 unsupported ops for the REFUSE chip M8720).
- **`test_chip_test.py:test_derive_plan_verify_gated_behind_destructive`** — dropped the none-scope `nd_ops`/`locked_ops` assertions; kept the full-scope verify-position-between-write-and-erase assertion.
- **`test_chip_test.py:test_derive_plan_is_uv_wired_from_is_uv_eprom`** — re-pointed per-parametrization to `"partial"` when `expected_is_uv` else `"full"` (the claim, `plan.is_uv is expected_is_uv`, is scope-independent).
- **`test_chip_test.py:test_count_applicable_bad_counts_as_ran`** — re-pointed AM2716 to `write_scope="partial"`; measured (not assumed) that `n_ran==2` is unchanged at the new scope.
- **`test_chip_test.py:test_count_applicable_m_from_single_plan_never_rederives`** — re-pointed AM2716 to `write_scope="partial"`; measured `m_applicable==4` is unchanged (locked_destructive is empty either way, so `M` was already just the supported count).
- **`test_chip_test_sdp_leg.py:test_shipped_ops_sequence_unchanged`** — re-anchored `_SHIPPED_OPS_SEQUENCE` from the `write_scope="none"` 3-step before-image to the `write_scope="full"` 12-step one (measured fresh, not derived), since M8720's default scope is retired.
- **`test_chip_test_sdp_leg.py:test_empty_registry_noop`** — re-pointed to `write_scope="full"`; the "empty cleanup registry" precondition still holds (M8720 is REFUSE, `sdp_lock`/`sdp_unlock` are never called at any reachable scope) — verified by measurement, not assumed.
- **`test_chip_test_sdp_leg.py:test_oracle_applicable_true_for_allow_chip_full_and_none_scope`** → renamed **`..._full_and_partial_scope`** — dropped the none-scope check; added a partial-scope check for the same ALLOW chip (measured `sdp_oracle_applicable` is True at both reachable scopes).
- **`test_chip_test_sdp_leg.py:test_oracle_applicable_false_for_refuse_chip_full_and_none_scope`** → renamed **`..._full_and_partial_scope`** — same pattern, for the REFUSE chip (measured False at both reachable scopes).
- **`test_derive_plan_structural_sentinel.py:test_plans_with_no_write_are_vacuously_clean`** — dropped only the real-`derive_plan`-at-`write_scope="none"` assertion block; its two hand-built-plan cases (an empty plan, and an id/read/blank-check plan with no write) never depended on `write_scope` and are unchanged — they already proved the same "no write step ⇒ vacuously clean" claim independent of scope.

## Decisions Made

See `key-decisions` in frontmatter for the full text. In summary: `tools/measure_plan_shapes.py` was edited outside this plan's `<files>` list because the plan's own action text authorized it and the re-key made it mechanically necessary; the halved aggregate numbers were verified by regeneration, not computed; a real tuple-unpacking bug was found and fixed as a side effect of the re-key; and every deletion/re-point rationale lives here or in the evidence transcripts, never as a new source comment.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `tools/measure_plan_shapes.py` required an update to run at all against the re-keyed corpus**
- **Found during:** Task 3
- **Issue:** The generator's `derive()` and `validate()` both hard-coded `corpus[(name, "full")]`/`corpus[(name, "partial")]` lookups. After `plan_corpus()` was re-keyed to `{name: Plan}`, these lookups raise `KeyError` — the generator cannot run, so `tests/fixtures/plan_shapes.json` cannot be regenerated and the whole Task 3 deliverable is blocked.
- **Fix:** Updated `derive()` to read `corpus[name]` and build a single `"steps"` list per shape family (was a `"full"`/`"partial"` pair); updated `validate()` to match, and added a UV/non-UV family-mixing check the new single-list schema depends on for correctness (measured: no family mixes).
- **Files modified:** `firestarter_app/tools/measure_plan_shapes.py` (not product source — `tools/*.py` is explicitly exempt from the no-comments rule per this plan's own comment-discipline section)
- **Verification:** `python tools/measure_plan_shapes.py --check` passes; all three planted-fault legs (`chip-count-skew`, `orphan-family`, `empty-chips`) still exit non-zero and leave the committed artifact byte-unchanged
- **Committed in:** `851c93b`

**2. [Rule 1 - Bug] `carveout_chips = {name for name, _scope in carveout_plans}` would raise under the new corpus key**
- **Found during:** Task 3
- **Issue:** This line in `test_derive_plan_structural_sentinel.py`'s 28C carve-out test unpacks each `carveout_plans` entry as a `(name, scope)` 2-tuple — valid only under the retired tuple key. Under the single-string key, this raises `too many values to unpack`.
- **Fix:** Changed to `carveout_chips = set(carveout_plans)`, since `carveout_plans` is now already a list of plain chip names with the same 1:1 cardinality the old code computed via unpacking.
- **Files modified:** `firestarter_app/tests/test_derive_plan_structural_sentinel.py`
- **Verification:** `pytest tests/test_derive_plan_structural_sentinel.py -o addopts="" -q` — `30 passed`
- **Committed in:** `851c93b`

**3. [Rule 3 - Blocking] Stale `__pycache__` bytecode reintroduced the literal `1354`**
- **Found during:** Task 3, running the leg-2 verify (`grep -rqF '1354' tests/`)
- **Issue:** `tests/__pycache__/test_derive_plan_no_drop_sweep.cpython-*.pyc` files, compiled from the pre-edit source, still contained the literal `1354` and were matched by a recursive grep over `tests/` — a repeat of the exact class of issue 181-01-SUMMARY.md documented (Deviation #2 there).
- **Fix:** Cleared all `__pycache__` directories under the app repo (bytecode cache only, gitignored and untracked, not a `git clean` operation, nothing tracked touched).
- **Files modified:** none tracked (cache only)
- **Verification:** `grep -rqF '1354' tests/` — no matches after clearing
- **Committed in:** n/a (no tracked files changed)

---

**Total deviations:** 3 auto-fixed (1 blocking generator update, 1 bug, 1 blocking stale-cache issue). **Impact:** All three were necessary to complete Task 3 as specified; none widened this plan's scope beyond what D-08/D-09/RPT-B2 already required. The generator update is the most consequential and is fully disclosed above and in `evidence/181-02-corpus-reanchor.txt`.

## Issues Encountered

### Known Environmental Condition — concurrent, unrelated session dirt (not caused by this plan)

Identical in kind to 181-01-SUMMARY.md's documented condition, continuing through this plan's execution window. `firestarter_app/firestarter/serial_comm.py` and `firestarter_app/tests/test_probe_spurious_setup_ack.py` carry uncommitted changes from an active `/gsd-debug` session sharing this branch. Two of that session's commits landed on the app branch during this plan's own execution: `31f3455` (already present when this plan started, and already documented by 181-01-SUMMARY.md) and `b2546da` ("style: carry the probe recovery timeout's unit in its name", landed mid-way through this plan's Task 2/3 work). Neither commit, nor the currently-uncommitted state, touches any file in this plan's `files_modified` list.

Consequences:
- `git -C /workspaces/firestarter status --porcelain` — **clean** (firmware submodule untouched).
- `git -C /workspaces/firestarter_app status --porcelain` (whole repo) — **dirty**: `serial_comm.py` + untracked/modified `test_probe_spurious_setup_ack.py`, neither this plan's file.
- `git -C /workspaces/firestarter_app status --porcelain -- <this plan's 12 files>` (scoped) — **clean**.
- `git diff 04fd982 --name-only -- firestarter/` lists `diagnostic_report.py` (181-01's own change) and `serial_comm.py` (the concurrent session's change) — the plan's own verify leg text anticipates exactly the first case ("Only 181-01's two lines... are permitted, so if that file appears here, confirm the diff is 181-01's and no more") and this SUMMARY extends that same confirmation to the second, unrelated file.

Per the deviation-rule scope boundary, this plan does not touch, revert, stash, or commit that unrelated work. Flagged as `human_judgment: true` (D9 in the coverage block above) rather than silently marked passing.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

RPT-B2's deletion (plan 181-04) now faces a **small, mechanical edit**: `derive_plan`'s `write_scope` parameter, `_WRITE_SCOPE_*` constants, `_WRITE_SCOPES`, the `ValueError` ladder, `Plan.locked_destructive`, `BannerCounts.locked_steps`, `count_applicable`'s extra term, and `sdp_oracle_applicable`'s second arm are all still byte-unchanged (this plan's own hard boundary — "This plan deletes no product symbol"), but every test that would have broken from that deletion has already been re-pointed or removed, and every call site left in `tests/` now passes an explicit `"full"`/`"partial"` literal. 181-04 drops a uniform kwarg across those 102 identical call sites instead of untangling a 117-site migration entangled with the product deletion itself. The measured digest and serializer field order in `evidence/181-02-derive-plan-equivalence.txt` let 181-04 *prove* behaviour-identity on the deletion rather than merely assert it.

**Blocker for the phase, not for this plan:** the whole-repo porcelain state still depends on the concurrent `/gsd-debug` session's work-in-progress on `serial_comm.py` completing (committing or reverting) before any later plan in this phase runs a whole-repo porcelain leg of its own. This plan's own work is fully committed and does not depend on that session resolving.

## Self-Check: PASSED

- All three evidence transcripts, `plan_corpus.py`, and `plan_shapes.json` confirmed present on disk with `[ -f ]`.
- All five commit hashes confirmed present via `git log --oneline --all` (meta: `7537adb0`, `cf57f100`, `a582681a`; app: `784e74c`, `851c93b`).
- `pytest` re-run across all nine touched test modules combined: `367 passed` (152+81+4+6+5+77+30+6+6), zero failed/error/skipped.
- All plan-level `<verification>` items re-confirmed: 64-hex digest + serializer field order present; AST census over `tests/` returns zero bare and zero explicit-"none" `derive_plan` calls; the module-level `_resolve_write_scope` import is absent; `plan_corpus()` is 677 entries keyed by name and the literal `1354` is gone from `tests/`; `plan_shapes.json` regenerated with its `_generated_by` banner and `_EXPECTED_AGGREGATE` matching; all nine modules report bare `N passed`; `git diff 04fd982 --name-only -- firestarter/` lists only `diagnostic_report.py` (181-01) and `serial_comm.py` (documented external); all 19 `FROZEN_HASHES` byte-identical; `tokenize` comment counts at or below every baseline.
- Porcelain: firmware submodule clean; this plan's own 12 files clean when scoped; whole-app-repo leg reads dirty due to the documented, continuing concurrent session (see "Known Environmental Condition" above) — not a failure of this plan's own work.

---
*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Completed: 2026-09-09*
