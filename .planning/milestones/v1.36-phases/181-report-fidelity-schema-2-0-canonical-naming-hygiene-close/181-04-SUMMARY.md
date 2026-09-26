---
phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
plan: 04
subsystem: dev-test-engine
tags: [derive-plan, write-scope, dedup-fingerprint, hyg-04, ast-pin, mutation-testing]

requires:
  - phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close
    plan: "02"
    provides: "the retired write_scope=\"none\" test surface, the re-keyed plan_corpus(), and the five zero-valued de-risking measurements this plan's halt-check reads"
provides:
  - "derive_plan's write_scope narrowed to \"full\"/\"partial\", keyword-only, NO DEFAULT -- a bare two-argument call raises TypeError"
  - "Plan.locked_destructive, BannerCounts.locked_steps, _WRITE_SCOPE_NONE, _SDP_LOCKED_REASON, write_execute (local) and the dead sdp_oracle_applicable second arm all deleted"
  - "cli_handlers._resolve_write_scope deleted; its rule inlined at the single production derive_plan call site in dev_test"
  - "HYG-04 discharged as a four-way edit landed in one commit: the allow-list, its positive membership assertion, the expected-referenced-helpers set, and the re-measured len(derived) floor"
  - "a static AST pin (plus a planted-mutant RED observation) proving write_op and full_device_permitted read off write_scope and never is_uv -- the gate protecting D-16's zero-re-key claim"
  - "D-16 re-proven after the deletion: all 19 FROZEN_HASHES literals byte-identical to app base 04fd982"
  - "181-CONTEXT.md's D-09 amended in place -- the rejected \"drop write_scope entirely\" design and its two falsified justifications are gone, replaced by the measurement and the adjudication"
affects: [181-08]

actuals:
  tokens: 19031
  tasks: 3
  commits: 7

tech-stack:
  added: []
  patterns:
    - "additive-mutant vacuity leg: plant is_uv ALONGSIDE write_scope (an OR, not a full replacement) so a presence-only check stays green on the mutant and only the absence check catches it -- proves the pin's second conjunct is load-bearing, not merely the first"
    - "real-path vs hand-transcribed shape filtering when simulating a rejected design: a naive UV-chip+op=write sweep over-counts by including gh*/synthetic fixtures that never call derive_plan and are therefore immune to a derive_plan-internal mutation by construction"
    - "CONTEXT.md decision amendment: replace the falsified sentences outright (never annotate), add a dated '## Status: Phase N amendment' marker, and name the gate that would redden if the rejected reading were tried again"

key-files:
  created:
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-04-scope-narrowing.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-04-frozen-hash-reproof.txt
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/evidence/181-04-write-op-pin-red.txt
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tools/check_devtest_orchestrator.py
    - firestarter_app/tests/test_blast_radius_invariance.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_provenance.py
    - firestarter_app/tests/test_check_devtest_orchestrator.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_derive_plan_structural_sentinel.py
    - firestarter_app/tests/plan_corpus.py
    - firestarter_app/tests/fixtures/reports/*.json (19 snapshots, one line each)
    - .planning/phases/181-report-fidelity-schema-2-0-canonical-naming-hygiene-close/181-CONTEXT.md

key-decisions:
  - "The operator's 2026-09-09 adjudication reverses D-09's original 'drop write_scope entirely' reading, on a measurement made after that decision was recorded: dropping the parameter moves the write-op selector onto is_uv and re-keys 7 of the 19 frozen dedup hashes -- including the two shapes Phase 174 froze as D-02's rejected alternatives. write_scope is narrowed to two values with no default instead; write_op and full_device_permitted stay byte-unchanged."
  - "The write-op selector pin's planted mutant is additive (is_uv joins write_scope via OR), not a full replacement of write_scope. This is deliberate: a full-replacement mutant would make even a presence-only ('is write_scope mentioned anywhere') check redden, which would not demonstrate why the pin needs an explicit is_uv-absence assertion. The additive form keeps write_scope's literal text in the mutated expression while is_uv joins it, so only the absence check catches it -- proving the second conjunct is load-bearing."
  - "The D-16 re-proof (evidence/181-04-frozen-hash-reproof.txt) independently re-derives the seven before/after pairs rather than copying them from CONTEXT.md/181-PATTERNS.md prose. Restricting the simulation to the ten real-path-built shapes (via _build_real_path_report, which calls derive_plan) rather than all 19 registered shapes is what keeps the count at seven instead of eight: gh28-m27c512-fail is also chip=\"m27c512\" (UV) with a hand-transcribed op=\"write\" step, but because it is built via build_shape_from_step_specs -- never derive_plan -- the mutation cannot reach it. An unfiltered sweep over all 19 shapes would have wrongly counted eight."
  - "181-PATTERNS.md's claim about chip_test.py:894's SDP append ('not a write_scope=\"none\" append') was already corrected by plan 181-02's evidence transcript before this plan started; this plan's Task 1 halt-check read that correction (rows_with_nonempty_locked_destructive_at_reachable_scope=0, sdp_oracle_applicable_second_arm_changes_result_for=0, count_applicable_m_changes_without_locked_term_for=0, all zero) before touching any code, per the plan's own precondition."
  - "The '## Status: Phase 181 amendment' marker is placed as its own paragraph immediately after the '- **D-09:**' bullet marker (breaking out of strict list nesting), rather than embedded inline in the bullet's first line -- matching the 177/180 precedent of a standalone '## Status: Phase N amendment' section rather than a heading token buried mid-sentence inside a list item."
  - "_is_interactive is KEPT (not deleted) per D-19's narrow mandate to remove only _resolve_write_scope. It is now the allow-list's listed-but-unreferenced entry, the role _is_uv_eprom used to hold before this plan made _is_uv_eprom body-referenced by inlining the deleted helper's rule."

requirements-completed: [RPT-B2, HYG-04]

coverage:
  - id: D1
    description: "write_scope narrowed to keyword-only \"full\"/\"partial\" with NO default -- a bare two-argument derive_plan call raises TypeError, and \"none\" raises ValueError"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "Task 1 verify leg 1 (inspect.signature check): kind=KEYWORD_ONLY, default=empty, bare call TypeError, \"none\" ValueError"
        status: pass
      - kind: unit
        ref: "evidence/181-04-scope-narrowing.txt: derive_plan_write_scope_has_default=false, bare_call_raises=TypeError, none_value_raises=ValueError"
        status: pass
    human_judgment: false
  - id: D2
    description: "Plan.locked_destructive, BannerCounts.locked_steps, _WRITE_SCOPE_NONE, _SDP_LOCKED_REASON, write_execute (local), and sdp_oracle_applicable's second arm (provably dead per 181-02's measurement) are all deleted; to_dict()[\"banner\"] has exactly two keys on both the populated and the None-banner branch"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "Task 1 verify legs 2-4: dataclass field absence, banner_keys=[m_applicable, n_ran] on both branches, zero locked_destructive|locked_steps|write_execute|_WRITE_SCOPE_NONE occurrences under firestarter/"
        status: pass
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py::test_to_dict_banner_key_list_is_pinned (_BANNER_KEYS shrunk to 2 entries, first-ever shrink of a Phase-174 key-list pin)"
        status: pass
    human_judgment: false
  - id: D3
    description: "19 tests/fixtures/reports/*.json snapshots regenerated (tools/snapshot_report_shapes.py) to drop the retired locked_steps banner key; every dedup_fingerprint literal inside them is byte-unchanged"
    verification:
      - kind: other
        ref: "tools/snapshot_report_shapes.py --check: 19/19 match after regeneration; git diff per file is exactly one removed line"
        status: pass
    human_judgment: false
  - id: D4
    description: "cli_handlers._resolve_write_scope deleted; its rule inlined at dev_test's single derive_plan call as an explicit write_scope keyword referencing _is_uv_eprom; the interactive = _is_interactive() local (its only consumer) removed with no ruff F841"
    requirement: HYG-04
    verification:
      - kind: unit
        ref: "Task 2 verify legs 1-2: hasattr check, AST leg (exactly one derive_plan call, sole kwarg write_scope, scope expression references _is_uv_eprom)"
        status: pass
      - kind: unit
        ref: "ruff check firestarter/ tests/ (no F841)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The stale \"Design history for dev_test\" / \"ALWAYS WRITES\" / \"REVERSAL\" narrative block is deleted in full (folded todo 3, D-26); _ALWAYS_WRITES_PASS_COUNT survives"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "Task 2 verify leg 3: negative grep for the three narrative anchors, positive grep for _ALWAYS_WRITES_PASS_COUNT = 6"
        status: pass
    human_judgment: false
  - id: D6
    description: "HYG-04 lands as a four-way edit in one commit: _HANDLER_FUNCTION_NAMES drops the deleted name; its positive membership test is dropped and the test renamed; _EXPECTED_DEV_TEST_REFERENCED_HELPERS swaps the deleted name and _is_interactive for _is_uv_eprom; the len(derived) floor moves from the plan's stated 6 to the re-measured 5"
    requirement: HYG-04
    verification:
      - kind: unit
        ref: "tests/test_check_devtest_orchestrator.py (26 passed); tools/check_devtest_orchestrator.py exits 0"
        status: pass
      - kind: unit
        ref: "tests/test_dev_test_cmd.py (61 passed, one signature test deleted -- its subject no longer exists)"
        status: pass
    human_judgment: false
  - id: D7
    description: "The write-op selector pin: write_op and full_device_permitted read off write_scope and never is_uv, static AST claim, observed RED against a planted additive is_uv mutant, with an explicit vacuity leg proving a presence-only check would stay green on the same mutant"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "tests/test_derive_plan_structural_sentinel.py::test_the_write_op_selector_reads_write_scope_and_never_is_uv, ::test_full_device_permitted_reads_write_scope_and_never_is_uv, ::test_a_planted_is_uv_selector_reddens_the_write_op_pin (33 passed total in module)"
        status: pass
      - kind: other
        ref: "evidence/181-04-write-op-pin-red.txt: anchor_count=1, pin_at_head=GREEN, pin_at_planted_is_uv=RED, fixture_files_written=0"
        status: pass
    human_judgment: false
  - id: D8
    description: "D-16 re-proven after the deletion: all 19 FROZEN_HASHES literals byte-identical to app base 04fd982, independently re-derived (not copied) seven-pair before/after table for the avoided re-key"
    requirement: RPT-B2
    verification:
      - kind: unit
        ref: "tests/test_blast_radius_invariance.py -k test_dedup_fingerprint_is_frozen (19 passed); git diff 04fd982 --stat -- tests/fixtures/report_shapes.py (empty)"
        status: pass
      - kind: other
        ref: "evidence/181-04-frozen-hash-reproof.txt: frozen_hash_lines_added_or_removed_since_04fd982=0, shapes_reproducing=19/19, independently re-measured seven pairs matching CONTEXT.md's stated values byte-for-byte"
        status: pass
    human_judgment: false
  - id: D9
    description: "181-CONTEXT.md's D-09 amended in place: both falsified claims removed outright (not annotated), the '## Status: Phase 181 amendment' marker present, the operator-adjudication measurement and the gate that would redden are named, the 'Consequences' list no longer directs full_device_permitted/write_op onto is_uv"
    verification:
      - kind: unit
        ref: "Task 3 verify legs 5-6: positive grep for the marker/adjudication/hash-literal/gate-name, negative grep for both falsified sentences"
        status: pass
    human_judgment: false
  - id: D10
    description: "Zero # comments added to product source across all twelve baselined files (tokenize COMMENT-token census, non-increase gate); a mid-flight regression (one extra comment line in a reworded pre-existing comment) was caught by re-running the census and fixed in a follow-up commit before it reached the SUMMARY"
    verification:
      - kind: unit
        ref: "Full 12-file tokenize census, final measurement: all at or below baseline (893/924, 357/408, 214/214, 563/621, 220/227, 183/183, 98/98, 216/216, 20/27, 21/21, 71/71, 12/12); test_blast_radius_invariance.py and test_derive_plan_structural_sentinel.py both 0/0"
        status: pass
    human_judgment: false
  - id: D11
    description: "Whole-repo porcelain across the meta repo, the firmware submodule, and the app repo after this plan's own commits"
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter status --porcelain (clean); git -C /workspaces/firestarter_app status --porcelain firestarter/ (clean); git -C /workspaces/firestarter_app status --porcelain (clean, whole repo)"
        status: pass
    human_judgment: false

duration: ~105min
completed: 2026-09-09
status: complete
---

# Phase 181 Plan 04: Write-scope narrowing at the operator-adjudicated depth Summary

**D-08's deletion lands whole (`locked_destructive`/`locked_steps`/`write_execute`/`_WRITE_SCOPE_NONE`/`_resolve_write_scope` all gone), D-09 is narrowed rather than dropped on a measurement that would otherwise have re-keyed 7 of the 19 frozen dedup hashes, HYG-04 discharges as the four-way edit the code actually needed, and the whole adjudication is protected by a static AST pin observed RED against the exact planted mutation it exists to catch — all 19 `FROZEN_HASHES` literals stay byte-identical.**

## Performance

- **Duration:** ~105 min
- **Tasks:** 3 of 3 completed
- **Files modified:** 12 app-repo files + 19 regenerated snapshot fixtures + 1 meta-repo record, plus 3 new evidence transcripts

## Accomplishments

- **Task 1 — the deletion, at the adjudicated depth.** `derive_plan`'s `write_scope` narrowed to `"full"`/`"partial"`, keyword-only, **no default** — a bare two-argument call now raises `TypeError` rather than silently selecting the retired `"none"` scope, which is exactly the shape that makes the 15 previously-bare call sites (`181-02`'s measurement) safe. `Plan.locked_destructive`, `BannerCounts.locked_steps`, `_WRITE_SCOPE_NONE`, `_SDP_LOCKED_REASON`, `write_execute` (local) and `sdp_oracle_applicable`'s second arm (proven dead over all 677 names and both SDP classes by `181-02`) are all gone. `diagnostic_report.py`'s `_banner_dict` drops `locked_steps` from **both** branches, including the `None`-banner early return. `_BANNER_KEYS` shrinks to two entries — the first shrink of a Phase-174 key-list pin ever (`git log -S'_VOLTAGE_KEYS'` returns only the pin's creating commit). Surviving `locked_destructive`/`locked_steps` occurrences across `firestarter/`, `tests/`, `tools/` (`*.py` only) fell from 43 to 5, all five legitimate (forward-compat pins on frozen pre-2.0 fixture bodies, or documentation of the deletion) and none inside `firestarter/` product source. 19 `tests/fixtures/reports/*.json` snapshots regenerated to match — one line removed each, `dedup_fingerprint` byte-unchanged in every one.
- **Task 2 — `_resolve_write_scope` is gone, HYG-04 lands as a four-way edit.** Its two-line rule (`"partial"` when `_is_uv_eprom(app, chip)` else `"full"`) is inlined directly at `dev_test`'s single `derive_plan` call, as the explicit `write_scope` keyword's value expression — required so the AST leg proving the scope resolution reaches `derive_plan` can see `_is_uv_eprom` inside the call itself, not merely in a preceding statement. `_is_uv_eprom` becomes body-referenced for the first time; `_is_interactive` stops being referenced (its only caller was the deleted function) and becomes the allow-list's new listed-but-unreferenced entry, taking over the role `_is_uv_eprom` used to hold. The stale `Design history for dev_test` / `ALWAYS WRITES` / `REVERSAL` narrative block (50 lines) is deleted whole — it described a UV write-scope prompt that does not exist — while `_ALWAYS_WRITES_PASS_COUNT` stays, since it backs a live sweep invariant. `_HANDLER_FUNCTION_NAMES` drops the deleted name; the test asserting its positive membership is edited (that assertion, not the whole test, since the test also proves `_is_uv_eprom`'s membership) and renamed; `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` swaps `_resolve_write_scope`/`_is_interactive` for `_is_uv_eprom`; the `len(derived) >= 6` floor is **re-measured**, not computed from the plan's own prose — the live derivation returns 5, not 6, so the floor moves to `>= 5`. One `test_dev_test_cmd.py` test whose whole subject (`_resolve_write_scope`'s signature) no longer exists is deleted. `tests/plan_corpus.py`'s module docstring — not in this task's declared file list, but directly named by the `_resolve_write_scope`-absence gate, which greps all of `tests/` — is corrected: it previously stated this plan would drop `write_scope` entirely, which the adjudication reversed.
- **Task 3 — the pin that protects the whole adjudication, observed RED.** Three new tests in `test_derive_plan_structural_sentinel.py` pin `write_op` and `full_device_permitted`'s selector expressions structurally (AST, never a runtime trace): both must reference `write_scope` and must never reference `is_uv`. The planted-mutant test builds an **additive** mutant — `is_uv` joins `write_scope` via `or`, rather than replacing it — specifically so the vacuity leg has something to prove: a presence-only check (`write_scope` still literally present) would stay green on this exact mutant, and only the absence check (`is_uv not in names`) catches it. `evidence/181-04-frozen-hash-reproof.txt` independently re-derives the seven avoided before/after hash pairs by simulating the rejected mutant against all ten real-path-built shapes (never the nine hand-transcribed `gh*`/synthetic ones, which never call `derive_plan` and are therefore immune by construction) — the re-derived values match CONTEXT.md's stated pairs byte-for-byte, and the filtering by construction-route is what keeps the count at exactly seven rather than eight (`gh28-m27c512-fail` is also a UV chip with a hand-transcribed `op="write"` step, but its subject is immune). `181-CONTEXT.md`'s D-09 is amended in place: the rejected "drop entirely" reading and both falsified justifying sentences are removed outright (never annotated), replaced by the measurement, the adjudication, and the name of the gate that would redden if a later change tried the rejected reading anyway.
- **D-16 re-proven, not merely re-asserted.** All 19 `FROZEN_HASHES` literals in `tests/fixtures/report_shapes.py` are byte-identical to app base `04fd982` — confirmed both by the 19-way parametrized `test_dedup_fingerprint_is_frozen` and by a `git diff` restricted to twelve-hex literal lines (empty).
- **Zero `#` comments added to product source, with a self-caught regression.** A mid-execution comment census re-run found `test_dev_test_cmd.py` one line over its 216-line baseline — a Task 2 reword of a pre-existing comment (naming the deleted helper) had expanded from two lines to three. Compressed back to two lines, same content, net zero, and committed as its own fix before the final battery ran.

## Task Commits

Each task committed atomically, split across the app submodule (code) and the meta repo (docs/evidence):

1. **Task 1: narrow write_scope, delete locked_destructive/locked_steps**
   - `c5db256` (fix, app repo): the deletion, the snapshot regen, the surviving test fallout
   - `5d80d7fa` (docs, meta repo): `181-04-scope-narrowing.txt`
2. **Task 2: delete `_resolve_write_scope`, inline the rule, land HYG-04's four-way edit**
   - `0d2bb97` (fix, app repo): the deletion, the narrative block removal, the four-way allow-list edit
   - `4e56c30` (fix, app repo): follow-up fix — trimmed a comment reword back under its census baseline
3. **Task 3: pin the write-op selector, re-prove D-16, amend CONTEXT.md's D-09**
   - `43a54e2` (test, app repo): the three new pins
   - `a276fafe` (docs, meta repo): D-09 amendment + both evidence transcripts

**Plan metadata commit:** this SUMMARY.md, committed separately per the sequential-executor protocol (`STATE.md`/`ROADMAP.md` are NOT touched — owned by the orchestrator).

_All tasks carry `type="auto"`; Task 3 additionally carries `tdd="true"`, but its "RED" is a mutation-testing observation (a pin proven sensitive against a planted defect) rather than a standard implementation-driving RED/GREEN cycle — the pinned behavior (write_op/full_device_permitted reading off write_scope) already existed at HEAD from Task 1, so there is no failing-then-passing implementation cycle to report for it; the RED/GREEN semantics recorded are `pin_at_head=GREEN` / `pin_at_planted_is_uv=RED`, per `evidence/181-04-write-op-pin-red.txt`._

## Files Created/Modified

- `firestarter_app/firestarter/chip_test.py` — the narrowed two-value no-default `write_scope`; `locked_destructive`/`write_execute`/`_WRITE_SCOPE_NONE`/`_SDP_LOCKED_REASON` deleted; `sdp_oracle_applicable`'s dead second arm removed; `BannerCounts`/`count_applicable` shrunk
- `firestarter_app/firestarter/cli_handlers.py` — `_resolve_write_scope` deleted, rule inlined at `dev_test`'s `derive_plan` call; stale `ALWAYS WRITES`/`REVERSAL`/`Design history` narrative block (50 lines) deleted; `_ALWAYS_WRITES_PASS_COUNT` kept
- `firestarter_app/firestarter/diagnostic_report.py` — `_banner_dict` drops `locked_steps` from both branches; one stale `write_scope="none"` docstring clause corrected
- `firestarter_app/tools/check_devtest_orchestrator.py` — `_HANDLER_FUNCTION_NAMES` drops the deleted name; its fail-open warning comment updated (this file is tooling, not product source, so comments are permitted here)
- `firestarter_app/tests/test_blast_radius_invariance.py` — `_BANNER_KEYS` shrunk to two entries with its counted-keys docstring updated; the anti-vacuity test's docstring corrected to name the actual shrinking plans (181-04/181-05, not 181-02)
- `firestarter_app/tests/test_chip_test.py` — three `plan.locked_destructive == []` assertions deleted (their subject no longer exists); two comments referencing the deleted attribute reworded
- `firestarter_app/tests/test_provenance.py` — `Plan(...)`/`BannerCounts(...)` construction calls drop their deleted keyword arguments
- `firestarter_app/tests/test_check_devtest_orchestrator.py` — the HYG-04 four-way edit's test-side half: one assertion dropped and its test renamed, `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` re-pointed, the `len(derived)` floor re-measured to 5
- `firestarter_app/tests/test_dev_test_cmd.py` — one signature test deleted (its subject no longer exists); one comment reworded (and then trimmed back under baseline in a follow-up commit)
- `firestarter_app/tests/test_derive_plan_structural_sentinel.py` — three new pins, one helper, two anchor constants; `ast`/`pathlib`/`pytest` newly imported (see Deviations)
- `firestarter_app/tests/plan_corpus.py` — module docstring corrected (not in this task's declared file list; required by the `_resolve_write_scope`-absence gate, which greps all of `tests/`)
- `firestarter_app/tests/fixtures/reports/*.json` (19 files) — regenerated via `tools/snapshot_report_shapes.py`; one line removed each (`"locked_steps": []`)
- `.planning/phases/181-.../181-CONTEXT.md` — D-09 amended in place
- `.planning/phases/181-.../evidence/181-04-scope-narrowing.txt` — Task 1's before/after occurrence sweep + scalars
- `.planning/phases/181-.../evidence/181-04-frozen-hash-reproof.txt` — Task 3's independently re-derived seven-pair table + D-16 re-proof
- `.planning/phases/181-.../evidence/181-04-write-op-pin-red.txt` — Task 3's planted-mutant RED transcript

## Anchors That Had Moved (recorded per the plan's environment note)

- **The `_resolve_write_scope` signature comments in `tests/test_chip_test.py:3020-3026` and `tests/test_chip_test_sdp_leg.py:2098-2104`** the plan's read_first cited: neither exists at the measured lines nor anywhere else in either file. A targeted grep for `_resolve_write_scope` or the described "returns only full/partial" phrasing found zero matches in both files. Plan 181-02's test-surface retirement (93 sites, 15 tests deleted) most likely removed this content already, since both files were in 181-02's edit scope. Nothing to delete; recorded as vacuously satisfied.
- **The read_first claim that `tests/test_derive_plan_structural_sentinel.py` "already imports `ast` and the corpus."** Measured false at task start: only the corpus import (`from tests.plan_corpus import (...)`) was present; `ast` was not imported anywhere in the module. `import ast`, `import pathlib` (for reading `chip_test.__file__`'s source) and `import pytest` (for the vacuity leg's `pytest.raises`) were all added as a necessary Rule 3 fix — the AST-based pins cannot exist without them.
- **`tests/test_check_devtest_orchestrator.py`'s baseline collected counts, stated as "26 and 62" with "both fall by one" in the plan's own verify-leg prose.** Measured: `test_check_devtest_orchestrator.py` stays at 26 (the plan's own action text asks for one assertion *within* an existing test to be dropped, not the whole test deleted, so the count does not fall); `test_dev_test_cmd.py` falls from 62 to 61 (one whole test deleted, as instructed). The verify leg's actual `<automated>` command only checks for a bare `N passed` summary with no failures — it does not gate on either specific number — so this drift is informational, not a gate miss.

## Decisions Made

See `key-decisions` in frontmatter for the full text. In summary: the operator's adjudication (documented in the plan's `<orchestrator_dispositions>`) reverses D-09's "drop entirely" reading on a measurement made after that original decision; the write-op pin's planted mutant is deliberately additive rather than a full replacement, so the vacuity leg proves something real; the D-16 re-proof restricts its simulation to real-path-built shapes to avoid over-counting hand-transcribed fixtures that are immune to the mutation by construction; `_is_interactive` is kept per D-19's narrow mandate; and the `## Status: Phase 181 amendment` marker is placed as its own paragraph rather than embedded mid-sentence in the D-09 bullet, matching the 177/180 precedent's standalone-section shape.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] A reworded comment in `test_dev_test_cmd.py` briefly exceeded its own comment-census baseline**
- **Found during:** Task 3's final battery re-run (the plan-level tokenize census)
- **Issue:** Task 2's reword of the `_CHIP_UV` comment (removing the dangling `_resolve_write_scope` name reference) expanded from two `#` comment lines to three, tripping the file's 216-line baseline by one -- a genuine, if small, violation of the non-increase gate this plan's own acceptance criteria require.
- **Fix:** Compressed the reworded comment back to two lines, same content, net zero against baseline.
- **Files modified:** `firestarter_app/tests/test_dev_test_cmd.py`
- **Verification:** `tokenize` COMMENT-token census: 216/216 (was 217/216)
- **Committed in:** `4e56c30`

**2. [Rule 3 - Blocking] `tests/plan_corpus.py`'s module docstring named `_resolve_write_scope`, blocking Task 2's absence gate**
- **Found during:** Task 2, running the `! grep -rqF '_resolve_write_scope' firestarter/ tests/ tools/` verify leg
- **Issue:** `tests/plan_corpus.py` (not in Task 2's declared `<files>` list) referenced `cli_handlers._resolve_write_scope` twice in its module docstring, and additionally stated -- now falsely, per the operator's adjudication -- that "Plan 181-04 drops `derive_plan`'s `write_scope` keyword entirely." Both are false statements about current behaviour in a file the gate scans, and the gate is whole-of-`tests/`, not scoped to Task 2's declared files.
- **Fix:** Reworded both docstring passages to describe the inlined scope rule (never naming the deleted function) and the operator's actual adjudication (narrowed, not dropped).
- **Files modified:** `firestarter_app/tests/plan_corpus.py`
- **Verification:** `! grep -rqF '_resolve_write_scope' firestarter/ tests/ tools/` passes; `pytest tests/test_derive_plan_structural_sentinel.py tests/test_derive_plan_no_drop_sweep.py` (both import `plan_corpus`) still green
- **Committed in:** `0d2bb97`

**3. [Rule 3 - Blocking] `test_derive_plan_structural_sentinel.py` did not already import `ast`/`pathlib`/`pytest`, contradicting the plan's read_first**
- **Found during:** Task 3, before writing the first pin
- **Issue:** The plan's read_first stated the module "already imports `ast` and the corpus"; only the corpus import was actually present. Building an AST-based structural pin is impossible without `ast`; reading `chip_test.py`'s source requires `pathlib`; the vacuity leg's `pytest.raises` requires `pytest`.
- **Fix:** Added all three imports.
- **Files modified:** `firestarter_app/tests/test_derive_plan_structural_sentinel.py`
- **Verification:** `pytest tests/test_derive_plan_structural_sentinel.py` (33 passed); `ruff check`/`ruff format --check` both clean
- **Committed in:** `43a54e2`

---

**Total deviations:** 3 auto-fixed (1 self-caught comment-census regression, 2 blocking fixes to files outside this plan's declared `<files>` lists but directly named by this plan's own verify legs). **Impact:** All three were necessary to satisfy this plan's own acceptance criteria as written; none widened scope beyond what RPT-B2/HYG-04/D-16 already required.

## Issues Encountered

None beyond the deviations above. The concurrent `/gsd-debug` session documented in `181-01-SUMMARY.md`/`181-02-SUMMARY.md` (commits `31f3455`, `b2546da`, `8b3d8f9` on `serial_comm.py`/`test_probe_spurious_setup_ack.py`) had already landed and closed before this plan started -- `git log` shows no new commits from it during this plan's execution window, and no file it touched is in this plan's own `files_modified` list. Whole-repo porcelain is clean.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

RPT-B2 and HYG-04 are both fully discharged. `banner.locked_steps`, `Plan.locked_destructive`, `BannerCounts.locked_steps` and `_resolve_write_scope` are gone from product source; the write-op selector is pinned against the one mutation this whole adjudication exists to prevent, and D-16's zero-re-key claim is re-proven, not merely re-asserted, after the deletion. Remaining phase work (plans 05 through 08+) can proceed against a `derive_plan` whose `write_scope` contract is now `TypeError`-safe rather than silently-defaulting.

**Do not run the seven-leg green-tree battery or `check_rekey_ledger.py` against this plan's own scope** -- per the plan's own `<verification>` section, that battery runs once, in `181-08`, with floor **2239**. This plan's own automated legs (per-module pytest, ruff check, the orchestrator checker, the tokenize census, the three porcelain legs) all pass independently of that battery.

## Self-Check: PASSED

- All three evidence transcripts and the amended `181-CONTEXT.md` confirmed present on disk with `[ -f ]`.
- All six commit hashes confirmed present via `git log --oneline --all`: app `c5db256`, `0d2bb97`, `4e56c30`, `43a54e2`; meta `5d80d7fa`, `a276fafe`.
- `pytest` re-run across all eleven touched/dependent test modules combined: `575 passed`, zero failed/error/skipped.
- All plan-level `<verification>` items re-confirmed: `write_scope` keyword-only/no-default with `TypeError`/`ValueError` on the two boundary calls; `write_op`/`full_device_permitted` unchanged and pinned, observed RED against the planted mutant; zero moved `FROZEN_HASHES` literals, `test_blast_radius_invariance.py` at `103 passed`; zero `locked_destructive`/`locked_steps`/`write_execute`/`_WRITE_SCOPE_NONE`/`_resolve_write_scope` mentions under `firestarter/`; `to_dict()["banner"]` at two keys on both branches; `check_devtest_orchestrator.py` exits 0, `ruff check` clean (no F841); `181-CONTEXT.md` carries the amendment marker and neither falsified claim; the full twelve-file `tokenize` comment census is at or below every baseline (one self-caught and fixed mid-execution); all three porcelain legs print nothing.
- `tools/check_mypy_watermark.py`: `35` errors, at the pre-existing watermark, unchanged by this plan's edits (spot-checked, not a declared verify leg for this plan).

---
*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Completed: 2026-09-09*
