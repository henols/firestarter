---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 09
subsystem: testing
tags: [pytest, doc-migration, test-surgery, non-vacuity, packaging]

requires:
  - phase: 168-04
    provides: "the H-1 collection hazard severed -- the app suite no longer aborts at collection when a doc/ directory goes missing"
  - phase: 168-06
    provides: "app-side doc/ references outside the test tree already repointed (CLAUDE.md, README.md, docstrings, printed strings, build_db.py's generator)"
provides:
  - "17 doc-reading test legs removed by name across 5 modules -- 12 from the four documentation-claim modules (Task 1), 5 from the deferred-install-guide packaging module (Task 2) -- with the coverage each one took named, not silently dropped"
  - "the 33 code-side legs sharing those same 5 modules (26 + 7, matching the plan's 26/7 split) still run unchanged"
  - "firestarter_app/doc/ deleted -- all 10 files including the deferred PY32F071-FIRMWARE-INSTALL.md, recoverable from its recorded pre-deletion SHA in .planning/v1.35/MIGRATION-TABLE.md"
  - "the last doc/-citing comment in the test tree (test_diagnostic_report.py:844) deleted"
  - "the tools/baseline/chip_database.baseline.json stale doc/ reference explicitly decided as a named historical exclusion, not fixed here"
affects: ["168-10 (relocates the retired dispatch-mirror gate against the published wiki)", "168-13 (owns the CI-Python-floor MIGRATE-03 evidence run and the closing honesty ledger that reads this plan's coverage-loss accounting)"]

tech-stack:
  added: []
  patterns: ["a fail-closed leg that exercises its parity helper against a monkeypatched tmp_path file, never the real path, survives a doc deletion unchanged -- its module-level path constant must still exist as an attribute for pytest's monkeypatch.setattr(..., raising=True by default) to patch"]

key-files:
  created: []
  modified:
    - firestarter_app/tests/test_lockable_proms_doc_claims.py
    - firestarter_app/tests/test_protect_flags_doc_measurements.py
    - firestarter_app/tests/test_protection_table_citations.py
    - firestarter_app/tests/test_lock_status_class_partition.py
    - firestarter_app/tests/test_py32_packaging.py
    - firestarter_app/tests/test_diagnostic_report.py
  # deleted (not a Write/Edit modification, listed for completeness):
  #   firestarter_app/doc/ (10 files)

key-decisions:
  - "Kept test_py32_packaging.py's _INSTALL_DOC, _INSTALL_DOC_SECTION_3_HEADING, _read_install_doc and _assert_doc_states_app_region_end, deviating from the plan's literal instruction to delete 'the install-doc path constant, its section-heading constant and the read helper that no surviving leg calls' -- the plan's own acceptance criterion (7 surviving legs, matching 12 total minus the 5 named for deletion) requires test_install_doc_address_parity_fails_closed_on_a_planted_file_missing_the_address to survive, and that leg calls monkeypatch.setattr(sys.modules[__name__], \"_INSTALL_DOC\", planted) -- which raises AttributeError with pytest's default raising=True if _INSTALL_DOC does not already exist as a module attribute. Deleting it would have broken the plan's own required 7th leg. Only the genuinely orphaned _assert_doc_states_flash_base and _READBACK_OUTCOME_PHRASES (called exclusively by deleted legs) were removed. See Deviations."
  - "tools/baseline/chip_database.baseline.json's 9 stale firestarter/doc/AT28C04-ADAPTER.md references are an explicit, named historical exclusion, not fixed in this plan -- it is a pinned Phase-98 snapshot (362bfa0, 2026-06-30) consumed by six modules, diff_db.py is measured indifferent to the literal reason-string text (RC=0 under a mutated-string control), and no test asserts the path itself. Re-anchoring a frozen baseline has previously reddened unrelated legs elsewhere in this project. This is the one file the repair sweep still finds after this plan; it is the only entry the acceptance criteria's strict grep pattern lists."
  - "requirements-completed left empty for MIGRATE-02, MIGRATE-03 and MIGRATE-04 despite all three being declared in this plan's frontmatter. MIGRATE-02's literal text (both doc/ directories absent) is now true after this plan, but MIGRATE-03's formal CI-Python-floor evidence run is explicitly deferred to 168-13 by this plan's own task text, and MIGRATE-04's final cross-repo correctness depends on 168-10's meta-repo dispatch-mirror relocation. Per project precedent (168-04-SUMMARY.md, 168-07-SUMMARY.md), a multi-plan requirement is left for whichever plan actually closes it out."

patterns-established:
  - "When a plan's literal deletion instruction would break a leg the same plan requires to survive, keep the code the surviving leg needs and record the conflict as a Rule 1 auto-fix rather than silently following either instruction."

requirements-completed: []

coverage:
  - id: D1
    description: "12 doc-reading legs removed by name from the four documentation-claim modules (test_lockable_proms_doc_claims.py x3, test_protect_flags_doc_measurements.py x6, test_protection_table_citations.py x2, test_lock_status_class_partition.py x1); the 26 code-side legs sharing those modules still run and still pass"
    requirement: "MIGRATE-02"
    verification:
      - kind: unit
        ref: "tests/test_lockable_proms_doc_claims.py tests/test_protect_flags_doc_measurements.py tests/test_protection_table_citations.py tests/test_lock_status_class_partition.py -o addopts=\"\" -q -> 26 passed, 0 failed"
        status: pass
      - kind: other
        ref: "grep -rcE '(^|[^A-Za-z\"])doc/[A-Za-z0-9_.-]+\\.md' across the four modules -> 0; git diff -U0 -- tests/ shows no added line whose first non-space character is '#'"
        status: pass
    human_judgment: false
  - id: D2
    description: "5 install-doc-reading legs removed by name from test_py32_packaging.py's packaging module (the module CONTEXT.md never named); the 7 surviving legs -- including the fail-closed leg exercised against a planted tmp_path file, never the real doc -- still run and still pass; the module's non-vacuity docstring paragraph is retained verbatim"
    requirement: "MIGRATE-02"
    verification:
      - kind: unit
        ref: "tests/test_py32_packaging.py -o addopts=\"\" -q -> 7 passed, 0 failed"
        status: pass
      - kind: other
        ref: "grep -c 'Non-vacuity (research finding A-7)' tests/test_py32_packaging.py -> 1 (unchanged)"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_diagnostic_report.py:844's comment citing doc/community-validation.md deleted; test file's pre-task pass count (70) unchanged"
    requirement: "MIGRATE-04"
    verification:
      - kind: unit
        ref: "tests/test_diagnostic_report.py -o addopts=\"\" -q -> 70 passed, matching pre-task count"
        status: pass
      - kind: other
        ref: "grep -rnE '(^|[^A-Za-z\"])doc/[A-Za-z0-9_.-]+\\.md' firestarter_app/tests/ -> 0 hits (whole test tree)"
        status: pass
    human_judgment: false
  - id: D4
    description: "firestarter_app/doc/ deleted (10 files, including the deferred PY32F071-FIRMWARE-INSTALL.md); pre-deletion SHA re-resolves to non-empty text for all 10 files both before and after the delete; full app suite collects and passes with the directory gone"
    requirement: "MIGRATE-02"
    verification:
      - kind: other
        ref: "git show d56424e1:doc/<file> | wc -c for all 10 files -> non-zero (9779..33638 bytes) both before and after 'git rm -r doc/'; test -d doc -> false; git ls-files doc/ | wc -l -> 0"
        status: pass
      - kind: integration
        ref: "python -m pytest tests/ -o addopts=\"\" -q (firmware sibling present, devcontainer Python 3.12) -> 1955 passed, 0 failed, 0 errors, no 'error during collection' line; delta of 17 from the 1972 pre-plan baseline matches exactly the 17 legs removed in Tasks 1-2"
        status: pass
    human_judgment: false
  - id: D5
    description: "chip_database.baseline.json's 9 stale doc/ references explicitly decided as a named historical exclusion (not a silent omission); it is the only file the strict repair-sweep grep still lists"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "git -C firestarter_app grep -lE '(^|[^A-Za-z\"])doc/[A-Za-z0-9_.-]+\\.md' -- . -> tools/baseline/chip_database.baseline.json (exactly one file)"
        status: pass
    human_judgment: false

duration: ~50min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 09: Remove the 17 Doc-Reading Legs, Delete firestarter_app/doc/ Summary

**Removed 17 named test legs whose oracle was a `firestarter_app/doc/` file (12 from four documentation-claim modules, 5 from a packaging module CONTEXT.md never named), deleted the last doc-citing source comment, then deleted `firestarter_app/doc/` itself (10 files, including the deferred PY32F071 install guide) — leaving the full app suite green at 1955 passed with the exact 17-test delta from the pre-plan 1972 baseline, and every deleted leg's lost coverage named rather than implied.**

## Performance

- **Duration:** ~50 min
- **Completed:** 2026-08-31
- **Tasks:** 3 completed (all `type="auto"`)
- **Files modified:** 6 test files edited, 10 doc files deleted

## Accomplishments

- **Task 1 — the four documentation-claim modules.** Deleted 12 doc-reading legs by name:
  - `test_lockable_proms_doc_claims.py`: `test_section_17_states_at28c64b_at28c256_are_sdp_capable`, `test_section_17_states_at28c16_and_plain_at28c64_are_not_sdp_capable`, `test_no_wrong_blanket_shorthand_anywhere_in_doc`. Kept `test_no_wrong_blanket_shorthand_elsewhere_in_tree` (the one leg independent of `doc/`). Rewrote the module docstring to remove the now-stale historical narrative that named the deleted file directly.
  - `test_protect_flags_doc_measurements.py`: `test_doc_protect_on_after_figures_match_recomputed_db`, `test_doc_protect_off_before_figures_match_recomputed_db`, `test_doc_both_keys_count_matches_recomputed_db`, `test_algorithm_13_promotion_split_matches_doc`, `test_algorithm_6_correlation_is_stated_as_suggestive_not_derivable`, `test_documented_once_one_heading_two_pointers_no_restated_figures`. Removed the now-unused `_DOC_FILE`, `_PKG_DETAILS_FILE`, `_PROTO_FLAGS_FILE`, `_SHARED_POINTER_SUBSTRING` constants and all 8 doc-figure-parsing regex patterns. Kept the 4 code-side legs (the two-row exception, the runtime-consumer source scan, the `sdp_capability.py` untouched-guard, and the recomputation-helper non-vacuity control).
  - `test_protection_table_citations.py`: `test_every_quoted_citation_fragment_resolves_in_the_doc` and its non-vacuity control `test_citation_resolution_non_vacuity_control`, deleted together as instructed. Removed the orphaned `_DOC_FILE`, `_read_doc_text`, `_assert_all_fragments_resolve` and the unused `pytest` import.
  - `test_lock_status_class_partition.py`: `test_every_readable_token_has_a_citation_that_resolves_in_the_doc`. Removed the orphaned `_DOC_FILE`, `_read_doc_text`, `_extract_readable_citation_groups`, `_READABLE_BLOCK_START`, `_QUOTED_FRAGMENT_RE`, `_TOKEN_ON_LINE_RE`, and the now-unused `DOCUMENTED_READABLE_TOKENS` import.
  - Verified: the four modules collectively report **26 passed, 0 failed** — exactly the 38 total legs (4+10+6+18, per `168-RESEARCH.md`'s measured table) minus the 12 removed.
- **Task 2 — the packaging module and the last stray comment.** Deleted `test_py32_packaging.py`'s 5 install-doc legs (`test_install_doc_is_non_vacuous`, `test_install_doc_app_region_end_matches_host_constant`, `test_install_doc_flash_base_matches_host_constant`, `test_install_doc_documents_all_three_readback_outcomes`, `test_install_doc_pyusb_floor_matches_pyproject`) and the now-orphaned `_assert_doc_states_flash_base` helper and `_READBACK_OUTCOME_PHRASES` constant. Kept `_INSTALL_DOC`, `_INSTALL_DOC_SECTION_3_HEADING`, `_read_install_doc` and `_assert_doc_states_app_region_end` — see Deviations for why the plan's literal instruction to delete these would have broken the plan's own required 7th surviving leg. Retained the module docstring's non-vacuity paragraph verbatim and added a 168-09 note explaining the reduced scope of documentation-parity family 3. Deleted `test_diagnostic_report.py:844`'s comment citing `doc/community-validation.md`. Verified: `test_py32_packaging.py` reports **7 passed**; `test_diagnostic_report.py` reports **70 passed**, unchanged from its pre-task count.
- **Task 3 — delete the directory and run the full suite.** Re-resolved all 10 files' pre-deletion SHA (`d56424e1979edf7245cffb9ec3111c0469f5b23f`) to confirm non-empty content (9,779–33,638 bytes each) before deleting. `git rm -r doc/` removed all 10 files, including the deferred `PY32F071-FIRMWARE-INSTALL.md` — deferred means not published, not kept, and MIGRATE-02's "directory does not exist" condition still reaches it. Re-confirmed the SHA still resolves post-deletion. Ran the full app suite with the firmware sibling present, `-o addopts=""` to avoid the doubled-`-q` count-line trap: **1955 passed, 0 failed, 0 errors, no collection-error line**, in 341.86s. The 17-test delta from the pre-plan baseline (1972) is exactly the 17 legs removed across Tasks 1–2, confirming no coverage vanished unaccounted-for and nothing else broke.

## Task Commits

1. **Task 1: Remove the 12 doc legs from the four documentation-claim modules** - `b114697` (test, firestarter_app)
2. **Task 2: Remove the five install-doc legs and the last stray comment** - `f0dbb19` (test, firestarter_app)
3. **Task 3: Delete firestarter_app/doc/ and run the full suite** - `50f85b2` (chore, firestarter_app)

## Files Created/Modified

- `firestarter_app/tests/test_lockable_proms_doc_claims.py` - 3 legs deleted, 1 kept; docstring rewritten
- `firestarter_app/tests/test_protect_flags_doc_measurements.py` - 6 legs deleted, 4 kept; 4 constants + 8 regexes removed; docstring rewritten
- `firestarter_app/tests/test_protection_table_citations.py` - 2 legs deleted, 4 kept; 1 constant + 2 helpers + 1 import removed; docstring rewritten
- `firestarter_app/tests/test_lock_status_class_partition.py` - 1 leg deleted, 17 kept; 1 constant + 3 helpers + 2 regexes + 1 import removed; class docstring updated
- `firestarter_app/tests/test_py32_packaging.py` - 5 legs deleted, 7 kept; 1 helper + 1 constant removed; docstring extended with a 168-09 note
- `firestarter_app/tests/test_diagnostic_report.py` - 1 comment deleted (docstring text, not assertion logic)
- `firestarter_app/doc/*.md` (10 files) - **deleted** (2,880 lines total, including the deferred install guide)

## What Each Deleted Leg's Coverage Cost, and Whether It Is Checked Elsewhere

None of these 17 properties are replaced by anything in this phase. HONEST-02 (a later plan in this phase, 168-12) is a stamp-plus-resolve mechanism over per-chip/per-protocol claim tokens — a different, coarser check than the figure-level and citation-level parity these legs asserted, and it does not cover any of the specific properties below.

| Leg | Property it asserted | Checked elsewhere now? |
|---|---|---|
| `test_section_17_states_at28c64b_at28c256_are_sdp_capable` | Wiki source states the AT28C64B/AT28C256 SDP-capable row in the exact wording | No |
| `test_section_17_states_at28c16_and_plain_at28c64_are_not_sdp_capable` | Wiki source states the AT28C16/plain-AT28C64 not-SDP-capable row, explicitly contrasted | No |
| `test_no_wrong_blanket_shorthand_anywhere_in_doc` | The wiki source specifically never repeats the historical wrong shorthand | Partially — `test_no_wrong_blanket_shorthand_elsewhere_in_tree` still scans the whole `firestarter_app` tree, but never the wiki itself |
| `test_doc_protect_on_after_figures_match_recomputed_db` | Doc's `protect_on_after` headline + by-algorithm figures equal a fresh DB recomputation | No |
| `test_doc_protect_off_before_figures_match_recomputed_db` | Same, for `protect_off_before` | No |
| `test_doc_both_keys_count_matches_recomputed_db` | The "744 of 746 rows carry both fields" figure equals a fresh count | No |
| `test_algorithm_13_promotion_split_matches_doc` | The 18/18 native + 25/66 promoted split is stated in the doc, not just the bare 43 | No |
| `test_algorithm_6_correlation_is_stated_as_suggestive_not_derivable` | The algorithm-6 correlation sentence states the right figures and "non-derivable" framing | No |
| `test_documented_once_one_heading_two_pointers_no_restated_figures` | Exactly one authoritative heading; two pointer files never restate the figures | No |
| `test_every_quoted_citation_fragment_resolves_in_the_doc` | Every `protection_readability.py` citation fragment resolves verbatim in the doc | No |
| `test_citation_resolution_non_vacuity_control` | The above checker actually fails on a fabricated fragment (control for the prior row) | No (control has no subject left to control for) |
| `test_every_readable_token_has_a_citation_that_resolves_in_the_doc` | D-12's citation-presence + doc-resolution for `DOCUMENTED_READABLE_TOKENS` | Partially — citation *presence* is still covered by `test_protection_table_citations.py::test_every_curated_token_has_a_citation_comment`; doc *resolution* is not |
| `test_install_doc_is_non_vacuous` | The install doc exists, is non-empty, and carries its §3 heading | No |
| `test_install_doc_app_region_end_matches_host_constant` | Doc's app-region-end address matches `py32_dfu.APP_REGION_END` | No — **named explicitly as the sharpest loss**: no external cross-check remains on this host constant |
| `test_install_doc_flash_base_matches_host_constant` | Doc's flash-base address matches `py32_dfu.FLASH_BASE` | No — same as above |
| `test_install_doc_documents_all_three_readback_outcomes` | All three non-VERIFIED readback outcome phrases are named in the doc | No |
| `test_install_doc_pyusb_floor_matches_pyproject` | `pyproject.toml`'s `[py32]` pyusb requirement string also appears in the doc | No — restoring this parity gate is owed to whichever phase finally publishes the install guide |

The flash-map and pyusb-floor parity loss (rows 14, 15, 17 above) is the sharpest of the seventeen: it is the only parity gate this project had between `py32_dfu.APP_REGION_END` / `py32_dfu.FLASH_BASE` and any written description of them, and until the install guide is republished those two host constants have no external cross-check at all.

## The `chip_database.baseline.json` Stale-Reference Decision

Plan 168-06 logged that `tools/baseline/chip_database.baseline.json` still carries 9 stale `firestarter/doc/AT28C04-ADAPTER.md` references in its `unsupported_reason` strings, deferred without a decision. This plan makes the decision explicitly: **it is a named historical exclusion, not fixed here.**

Reasoning: the baseline is a pinned Phase-98 snapshot (`362bfa0`, 2026-06-30) consumed by six modules (`test_page_size_invariants.py`, `test_diff_db_gate.py`, `test_chip_database_field_inventory.py`, `test_variant_decode_evidence_stability.py`, `test_vcc_margin_rail.py`, `tools/diff_db.py`). `168-RESEARCH.md` measured `diff_db.py` indifferent to the literal `unsupported_reason` text (RC=0 under a mutated-string control), and no test asserts the path itself — only the `"adapter required:"` prefix and non-emptiness. Re-anchoring a frozen historical baseline has previously reddened unrelated legs elsewhere in this project's history. Under D-18's own reasoning (a frozen snapshot records what was true when it was written), this file is arguably a historical record, and the risk of re-baselining outweighs the cosmetic gain of a repointed string in a file no test reads for content. It is left as-is, and it is the *only* file the strict repair-sweep grep (`git grep -lE '(^|[^A-Za-z"])doc/[A-Za-z0-9_.-]+\.md' -- .`) still lists — confirming this is a scoped, deliberate exclusion, not a missed sweep.

## Decisions Made

- Kept `test_py32_packaging.py`'s `_INSTALL_DOC`, `_INSTALL_DOC_SECTION_3_HEADING`, `_read_install_doc` and `_assert_doc_states_app_region_end` rather than deleting them as the plan's action text literally instructed — see Deviations.
- `tools/baseline/chip_database.baseline.json`'s stale references are an explicit named exclusion (see above), not brought into scope for a generator fix in this plan.
- Left `requirements-completed` empty for MIGRATE-02, MIGRATE-03 and MIGRATE-04 — MIGRATE-02's literal text is now true (both `doc/` directories are absent), but this plan's own task text explicitly defers MIGRATE-03's CI-Python-floor evidence run to 168-13, and MIGRATE-04's cross-repo correctness still depends on 168-10's meta-repo work. Per project precedent, a multi-plan requirement is closed by the plan that actually finishes it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's literal deletion instruction for `test_py32_packaging.py` would have broken its own required 7th surviving leg**
- **Found during:** Task 2, while identifying which constants/helpers become orphaned after the 5 named-leg deletion
- **Issue:** The plan's action text says to delete "the install-doc path constant, its section-heading constant and the read helper that no surviving leg calls" alongside the 5 named legs. But the plan's own acceptance criterion requires **7 surviving legs** (12 total minus 5 named), and the 12th test function — `test_install_doc_address_parity_fails_closed_on_a_planted_file_missing_the_address`, not among the 5 named for deletion — calls `monkeypatch.setattr(sys.modules[__name__], "_INSTALL_DOC", planted)`. Pytest's `MonkeyPatch.setattr` defaults to `raising=True`, which raises `AttributeError` if `_INSTALL_DOC` is not already a module attribute when patched. Deleting `_INSTALL_DOC` (and, transitively, `_read_install_doc` and `_assert_doc_states_app_region_end`, which that surviving leg calls) would have broken this required leg, contradicting the plan's own 7-leg acceptance count.
- **Fix:** Kept `_INSTALL_DOC`, `_INSTALL_DOC_SECTION_3_HEADING`, `_read_install_doc`, and `_assert_doc_states_app_region_end`. Deleted only the genuinely orphaned `_assert_doc_states_flash_base` (called exclusively by the deleted `test_install_doc_flash_base_matches_host_constant`) and `_READBACK_OUTCOME_PHRASES` (called exclusively by the deleted `test_install_doc_documents_all_three_readback_outcomes`).
- **Files modified:** `firestarter_app/tests/test_py32_packaging.py`
- **Verification:** `pytest tests/test_py32_packaging.py -o addopts="" -q` -> 7 passed, 0 failed, matching the plan's own required count.
- **Committed in:** `f0dbb19` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (bug — plan-instruction internal contradiction)
**Impact on plan:** The deviation produces exactly the plan's own stated acceptance criterion (7 surviving legs); following the plan's literal action text instead would have produced 6 passing legs and 1 failure, contradicting the plan's own verification step.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None. All verification ran on the existing devcontainer Python 3.12 interpreter with the firmware sibling present, per this task's explicit scope (the CI-Python-floor run is 168-13's job).

## Next Phase Readiness

- Both `doc/` directories are now gone from the project (`firestarter/doc/` since 168-07, `firestarter_app/doc/` since this plan).
- The full app suite is green (1955 passed, 0 failed, 0 errors) on the devcontainer interpreter with the firmware sibling present; the 17-test delta from the 1972 pre-plan baseline is fully accounted for.
- The MIGRATE-03 CI-Python-floor evidence run (3.11 venv, build/install/full-suite) and the packaging sdist-delta report (0 and 0, per `168-RESEARCH.md`'s measured finding that the sdist premise was false) remain 168-13's work, as this plan's task text explicitly scoped.
- The relocated `tools/wiki/dispatch_mirror.py` gate (168-10) still needs to read the published `Programming-Protocols` wiki page in place of the deleted `firestarter/doc/PROTOCOLS.md` this plan's sibling work already severed the collection-time coupling for (168-04, 168-07).
- The flash-map/pyusb-floor doc-parity loss (see table above) has no owner yet — it is recorded here as owed to whichever phase republishes the PY32F071 install guide.
- No blockers for plan 168-10 or subsequent Wave 5–7 plans.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-09-SUMMARY.md
- FOUND: firestarter_app/doc absent (correct)
- FOUND commit: b114697 (firestarter_app)
- FOUND commit: f0dbb19 (firestarter_app)
- FOUND commit: 50f85b2 (firestarter_app)
