---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 03
subsystem: chip-database
tags: [generated-data, build_db, chip_database, wiki-migration, doc-repair]

requires: ["168-01"]
provides:
  - "firestarter_app/tools/build_db.py emits an AT28C DIP24 adapter-required reason naming the wiki page 'AT28C04 Adapter' instead of a firestarter/doc/ path"
  - "firestarter_app/firestarter/data/chip_database.json regenerated with exactly the 9 unsupported_reason rows changed, sha256-16 = ccbc8d2c4866a5af"
  - "tools/baseline/chip_database.baseline.json deliberately left untouched, with the diff_db.py RC=0 measurement recorded as evidence"
affects: ["168-05", "168-12", "later 168 plans that stamp wiki pages or check freshness"]

tech-stack:
  added: []
  patterns: ["generated artifact repair: edit the emitter, regenerate, gate the diff shape — never hand-edit the generated file (D-14)"]

key-files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_app/tests/test_build_db_inclusion.py
    - firestarter_app/tests/test_diff_db_gate.py

key-decisions:
  - "Replacement text keeps the 'adapter required:' prefix (pinned by test_build_db_inclusion.py) and names the rendered wiki page title 'AT28C04 Adapter' from MIGRATION-TABLE.md, never a URL or path (D-13)"
  - "tools/baseline/chip_database.baseline.json is NOT re-baselined — measured this session that diff_db.py returns RC=0 with the mutated text, confirming RESEARCH's prediction; the 9 baseline copies of the old path are historical evidence, same reasoning as D-18"
  - "Two pre-existing pinned tests were updated as a direct, unavoidable consequence of the sanctioned text change: test_at28c16_named_arm_reason_mentions_adapter_doc now asserts the wiki page title; test_vcc_margin_rail_bucket_distribution's PROV01_PROTECT_METADATA count moved 686 -> 682 with a new RULE_PHASE66 (4 chips) bucket, both traced to the exact mechanism (28C04A/28C04AF/28C16A/28C16AF's unsupported_reason no longer coincidentally matches the frozen Phase-98 baseline text)"

patterns-established:
  - "A generated-artifact regen that changes only operator-visible prose can still reclassify entries in a diff-report categorizer that keys off field-level equality against an old, frozen baseline — verify with a full before/after report diff, not just the primary numstat"

requirements-completed: [MIGRATE-04]

coverage:
  - id: D1
    description: "The comment at build_db.py naming the doc/ path is deleted outright (no-comments rule); the surrounding dispatch-behaviour comment block is left intact"
    requirement: "MIGRATE-04"
    verification:
      - kind: automated
        ref: "grep -cE '(^|[^A-Za-z])doc/[A-Za-z0-9_.-]+\\.md' firestarter_app/tools/build_db.py == 0; git -C firestarter_app diff -U0 4a156b8^..4a156b8 -- tools/build_db.py shows exactly one deleted comment line, no added '#' line"
        status: pass
    human_judgment: false
  - id: D2
    description: "The emitted unsupported_reason string names the wiki page 'AT28C04 Adapter', keeps the 'adapter required:' prefix, and test_build_db_inclusion.py passes in full"
    requirement: "MIGRATE-04"
    verification:
      - kind: automated
        ref: "python -m pytest tests/test_build_db_inclusion.py -o addopts=\"\" -q -> 20 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "chip_database.json regenerated via build_db.py (746 total chips), diff is exactly 9 added/9 removed unsupported_reason lines, baseline byte-unchanged, diff_db.py exits 0"
    requirement: "MIGRATE-04"
    verification:
      - kind: automated
        ref: "python tools/build_db.py -> 'Done! 744 upstream chips processed + 2 non-upstream supplement chip(s) = 746 total'; git diff --numstat == 9/9; git diff --quiet -- tools/baseline/chip_database.baseline.json (exit 0); python tools/diff_db.py -> RC=0"
        status: pass
    human_judgment: false
  - id: D4
    description: "No regression in the full py3.11 CI-shaped test suite after the two dependent pinned-test updates"
    requirement: "MIGRATE-04"
    verification:
      - kind: automated
        ref: "python -m pytest tests/ -o addopts=\"\" -q -> 1976 passed, 0 failed, 0 skipped (matches 168-RESEARCH.md's measured baseline)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 03: Repointing the Chip Database's Adapter-Required Reason at the Wiki Summary

**Edited `firestarter_app/tools/build_db.py`'s AT28C DIP24 adapter arm to delete its doc-path comment and repoint its emitted `unsupported_reason` string at the wiki page "AT28C04 Adapter" instead of `firestarter/doc/AT28C04-ADAPTER.md`, then regenerated `chip_database.json` (746 chips, exactly 9 rows changed) and deliberately left the historical baseline untouched, with the RC=0 no-op measurement recorded as evidence.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-31
- **Tasks:** 2 completed (both `type="auto"`)
- **Files modified:** 4 (2 planned, 2 additional pinned-test fixes — see Deviations)

## Accomplishments

- Deleted the single `#` comment at `build_db.py` citing `firestarter/doc/AT28C04-ADAPTER.md` (no-comments rule); left the surrounding dispatch-behaviour comment block untouched — the diff is exactly one deleted line, zero added comment lines.
- Rewrote the operator-visible `unsupported_reason` emitted for AT28C04/AT28C16 DIP24 chips to name the wiki page "AT28C04 Adapter" (from `.planning/v1.35/MIGRATION-TABLE.md`'s filled-in rendered title) instead of the doc path, keeping the `"adapter required:"` prefix `test_build_db_inclusion.py:539` pins.
- Regenerated `chip_database.json` via `python tools/build_db.py` against the pinned upstream `infoic.xml` commit: 744 upstream + 2 supplement = 746 total, matching the expected count exactly.
- Confirmed the regeneration touched **exactly** 9 lines (9 added, 9 removed), every one an `unsupported_reason` value, and nothing else — the byte-for-byte round trip RESEARCH measured held except for the intended edit.
- Ran `tools/diff_db.py` against the unmodified, historical `tools/baseline/chip_database.baseline.json`: **RC=0**. Confirms RESEARCH's prediction that the gate is measurably indifferent to this text, so the baseline is deliberately left untouched (its 9 copies of the old path are historical evidence, per the same reasoning as D-18's excluded-records list).
- Traced and fixed the two pinned tests this regeneration legitimately broke (see Deviations) so the full suite stays green.

## Task Commits

1. **Task 1: Edit the emitter — delete the comment, rewrite the emitted string** - `4a156b8` (fix)
2. **Task 2: Regenerate the database, gate it, and record the baseline exclusion** - `c97c90e` (feat)

## Files Created/Modified

- `firestarter_app/tools/build_db.py` - deleted the doc-path comment at the former `:543`; rewrote the emitted `unsupported_reason` string at the former `:569` to name the wiki page instead of the path
- `firestarter_app/firestarter/data/chip_database.json` - regenerated; 9 `unsupported_reason` rows changed (AT28C04/AT28C16 DIP24 family across both MICROCHIP-memory and cross-vendor listings); 746 total chips
- `firestarter_app/tests/test_build_db_inclusion.py` - `test_at28c16_named_arm_reason_mentions_adapter_doc` updated to assert the reason contains the wiki page title `"AT28C04 Adapter"` instead of the retired `"AT28C04-ADAPTER.md"` path
- `firestarter_app/tests/test_diff_db_gate.py` - `test_vcc_margin_rail_bucket_distribution`'s pinned `PROV01_PROTECT_METADATA` count updated `686 -> 682` and a new assertion added for the now-populated `RULE_PHASE66 (4 chips)` bucket, with the class/test docstrings explaining the causal chain

## Decisions Made

- **Replacement wording:** `"...requires a physical DIP24-to-DIP32 adapter; see the wiki page AT28C04 Adapter"` — keeps the pinned prefix, keeps the sentence's meaning (a physical adapter is required), names a wiki page title (not a URL, not a path) per D-13, and contains no `https://`.
- **Do not re-baseline `chip_database.baseline.json`.** Measured this session: `python tools/diff_db.py` (with `FIRESTARTER_DB_FILE` unset, i.e. against the real regenerated file and the real, unmodified baseline) returns exit 0 with `PASS: all 744 changed chips explained`. The baseline's own copies of the old doc path are frozen historical evidence (same class of exclusion as D-18), and re-anchoring a baseline last touched at Phase 98 and consumed by six modules is a move this project has already learned reddens unrelated legs.
- **Two pinned tests were updated, not the generator further constrained to preserve them.** Both assertions encoded the very defect this plan exists to fix (one directly pinned the doc-path string; the other pinned a diff-report bucket count that shifts as a direct, mechanical side effect of the text no longer matching the frozen baseline for 4 specific chips). Rule 1 (bug fix) applies: the test bodies were asserting stale facts, not enforcing a real invariant the code violated.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `test_at28c16_named_arm_reason_mentions_adapter_doc` asserted the retired doc path**
- **Found during:** Task 1's verification (`pytest tests/test_build_db_inclusion.py`)
- **Issue:** The test's own docstring and assertion body required `"AT28C04-ADAPTER.md"` to appear in the reason string — exactly the fact this plan's Task 1 removes.
- **Fix:** Updated the docstring point 2 and the assertion to require the wiki page title `"AT28C04 Adapter"` instead.
- **Files modified:** `firestarter_app/tests/test_build_db_inclusion.py`
- **Commit:** `c97c90e`

**2. [Rule 1 - Bug] `test_vcc_margin_rail_bucket_distribution` pinned a bucket count that legitimately shifted**
- **Found during:** Task 2's verification (`pytest tests/test_diff_db_gate.py`)
- **Issue:** `diff_db.py`'s classifier assigns a chip's PRIMARY rule label by comparing each field against the frozen Phase-98 baseline. For `28C04A`/`28C04AF`/`28C16A`/`28C16AF`, the OLD `unsupported_reason` text happened to still match the frozen baseline's stored value (so `phase66_diff` was False and they fell through to the `PROV01_PROTECT_METADATA` catch-all, which does not check `phase66_diff`). After Task 2's regeneration, their `unsupported_reason` no longer matches the baseline, so `phase66_diff` becomes True and they are correctly reclassified as `RULE_PHASE66` — a bucket that previously reported 0 chips (and was omitted from the report entirely) and now reports 4. `PROV01_PROTECT_METADATA`'s pinned count of 686 therefore drops to 682.
- **Fix:** Updated the pinned assertion to 682, added an assertion for the new `RULE_PHASE66 (4 chips)` bucket, and rewrote the class/test docstrings to explain the mechanism so a future reader does not mistake this for an unexplained drift.
- **Files modified:** `firestarter_app/tests/test_diff_db_gate.py`
- **Commit:** `c97c90e`
- **Verification of root cause:** Confirmed by running `tools/diff_db.py` against both the pre-regeneration and post-regeneration database and diffing the two full reports — the only textual difference beyond the numstat is the 4-chip bucket move, isolated and explained before the test was touched.

## Issues Encountered

None beyond the two auto-fixed test updates above. Both were identified, root-caused with a controlled before/after comparison (not guessed), and fixed within the 3-attempt auto-fix limit (1 attempt each).

## User Setup Required

None. `python tools/build_db.py` required network access to `gitlab.com` (confirmed available) but no credentials or manual configuration.

## Next Phase Readiness

- `chip_database.json`'s new sha256 (truncated to 16 hex): **`ccbc8d2c4866a5af`** — plan 168-05 stamps the wiki pages with this value and plan 168-12's freshness leg compares against it.
- The AT28C04 Adapter wiki page (per `.planning/v1.35/MIGRATION-TABLE.md`) is now the canonical target every operator-visible reference to this chip family's adapter requirement points at — no repository path or URL remains anywhere in `build_db.py` or the generated database.
- `firestarter_app` is on `gsd/v1.35-documentation-consolidation-wiki-migration` with 2 new commits (`4a156b8`, `c97c90e`), full suite green (1976 passed), tree clean except this plan's own changes.
- No blockers for subsequent plans in this phase.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-03-SUMMARY.md
- FOUND: firestarter_app/tools/build_db.py
- FOUND: firestarter_app/firestarter/data/chip_database.json
- FOUND commit: 4a156b8
- FOUND commit: c97c90e
