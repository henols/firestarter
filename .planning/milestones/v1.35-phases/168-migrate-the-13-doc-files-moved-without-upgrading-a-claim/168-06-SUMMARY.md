---
phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim
plan: 06
subsystem: docs
tags: [link-repair, docstrings, click, wiki-migration, firestarter_app]

requires:
  - phase: 168-01
    provides: ".planning/v1.35/MIGRATION-TABLE.md with page names, rendered titles and pre-deletion SHAs"
  - phase: 168-05
    provides: "12 documentation pages live on firestarter_prom.wiki.git under their recorded page names"
provides:
  - "firestarter_app repository (outside its test tree) with zero references to a firestarter_app/doc/ or firestarter/doc/ path in a comment, docstring, printed string, or README link"
  - "the third shield-revision lockstep rule (firestarter_app/CLAUDE.md), repointed at the wiki page title Shield Revisions, kept binding"
  - "two user-visible bootloader-entry messages (firmware.py, py32_dfu.py) rewritten to state the actionable condition directly instead of naming the deferred, unpublished PY32F071 install guide"
affects: ["168-07 (firmware repo's mirror of this repair, including the same lockstep-rule pattern)", "168-09 (deletes firestarter_app/doc/; this plan's STRUCTURE.md correction anticipates that)", "168-13 (wiki-check.yml repoint; inherits this plan's two deferred-items entries)"]

tech-stack:
  added: []
  patterns:
    - "comment-vs-docstring-vs-printed-string classification: delete a `#` comment citing a doc path, repoint a docstring at a wiki page title, rewrite a user-visible string to state the actionable condition and drop the pointer entirely when the target document is deferred/unpublished"
    - "README links stay full wiki URLs (D-13's one exception); every other in-repo reference becomes a bare page title, never a URL, so Backlog 999.9's repository-rename sweep cannot invalidate it"

key-files:
  created: []
  modified:
    - firestarter_app/CLAUDE.md
    - firestarter_app/README.md
    - firestarter_app/.planning/codebase/STRUCTURE.md
    - firestarter_app/firestarter/protection_readability.py
    - firestarter_app/firestarter/py32_dfu.py
    - firestarter_app/firestarter/firmware.py
    - firestarter_app/firestarter/ic_layout.py
    - firestarter_app/firestarter/diagnostic_report.py
    - firestarter_app/tools/diff_db.py
    - firestarter_app/tools/check_protection_readability_invariants.py

key-decisions:
  - "ic_layout.py:461 and diagnostic_report.py:256's citing comments could not be removed by deleting exactly the named single line without leaving a grammatically broken remainder (the doc citation sits mid-sentence, wrapped across several physical lines) -- deleted the whole citing clause instead (3 lines removed net in ic_layout.py, 0 net in diagnostic_report.py after a 1-for-1 reword), which the plan's own read_first anticipated with 'where deleting a line leaves a comment block that reads coherently, leave the rest alone' -- read as license to extend the deletion when a single-line cut would not read coherently."
  - "The plan's own automated Task-1 verify leg (git diff -U0 | grep added lines starting with #) counts 5 lines as 'added' even though both edits are net reductions of pre-existing comments (8 removed / 5 added across the two files) with zero new comments created -- documented under Deviations rather than silently reported as a pass, since the raw grep cannot distinguish a reworded existing comment from a genuinely new one."
  - "firmware.py:629's doc reference lives in a private method's docstring, not literally 'printed output' as the plan's read_first characterized it -- treated it as the plan's action instructed for that site regardless (drop the pointer, state the actionable condition directly), reusing the exact bootloader-entry wording already present in py32_dfu.py's sibling error string for consistency."
  - "tools/baseline/chip_database.baseline.json still carries 9 stale doc/AT28C04-ADAPTER.md references (168-03 fixed and regenerated the live chip_database.json but not this committed baseline snapshot) -- out of this plan's files_modified scope and shaped like D-14's generator-regeneration work, not a docstring/comment/string repair; logged to deferred-items.md rather than hand-edited or silently left unmentioned."

requirements-completed: [MIGRATE-04]

coverage:
  - id: D1
    description: "No module in firestarter_app's package cites a vanishing doc/ path in a comment, docstring, or user-visible string; Click --help output is unaffected"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "grep -rcE '(^|[^A-Za-z])doc/[A-Za-z0-9_.-]+\\.md' firestarter_app/firestarter/ == 0; git diff --stat 6fba178..HEAD -- firestarter/cli_handlers.py firestarter/main.py is empty (no Click docstring touched)"
        status: pass
      - kind: unit
        ref: "python -m pytest tests/ -o addopts=\"\" -q -k 'protection_readability or py32 or firmware or ic_layout or diagnostic_report' -> 369 passed"
        status: pass
    human_judgment: false
  - id: D2
    description: "Both tools modules and firestarter_app/CLAUDE.md name wiki page titles; the third shield-revision lockstep rule survives with all four sections and the lockstep obligation intact"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "grep -cE '(^|[^A-Za-z])doc/[A-Za-z0-9_.-]+\\.md' tools/diff_db.py tools/check_protection_readability_invariants.py CLAUDE.md == 0 each; grep -c 'Shield Revisions' CLAUDE.md >=1; grep -ci 'unverified against silicon' CLAUDE.md == 1; grep -c lockstep CLAUDE.md unchanged at 1 (pre- and post-edit)"
        status: pass
      - kind: unit
        ref: "python -m pytest tests/test_diff_db_gate.py -o addopts=\"\" -q -> 5 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "README links point into the wiki as full URLs (D-13/D-17 exception); the app's own tracked codebase map no longer shows a doc/ tree entry"
    requirement: "MIGRATE-04"
    verification:
      - kind: other
        ref: "grep -cE '(^|[^A-Za-z])doc/[A-Za-z0-9_.-]+\\.md' README.md == 0; grep -c 'firestarter_prom/wiki/' README.md == 2; git ls-files .planning/codebase | wc -l unchanged at 7"
        status: pass
    human_judgment: false
  - id: D4
    description: "The full firestarter_app test suite still passes at its pre-plan count with the count line visible"
    requirement: "MIGRATE-04"
    verification:
      - kind: unit
        ref: "python -m pytest tests/ -o addopts=\"\" -q -> 1972 passed (matches pre-plan baseline)"
        status: pass
    human_judgment: false

duration: ~32min
completed: 2026-08-31
status: complete
---

# Phase 168 Plan 06: Repair `doc/` References in the `firestarter_app` Repository Summary

**Repaired all in-scope `firestarter_app`-side `doc/` references outside the test tree — deleted two citing comments, repointed five docstrings/tools strings at wiki page titles, rewrote two user-visible bootloader-entry messages to drop a pointer to a deferred unpublished guide, rewrote both README links as full wiki URLs, and corrected the app's own stale codebase-tree diagram — with the full 1972-test suite still green throughout.**

## Performance

- **Duration:** ~32 min
- **Started:** 2026-08-31T09:09:00Z (approx.)
- **Completed:** 2026-08-31T09:41:06Z
- **Tasks:** 3 completed (all `type="auto"`)
- **Files modified:** 10

## Accomplishments

- Deleted the two `#` comments in `ic_layout.py` and `diagnostic_report.py` that cited a `doc/` path for canonical protocol names and community-validation ladder vocabulary, extending each deletion to the full citing clause (not just the single named line) so the surviving comment still reads as a complete sentence
- Repointed `protection_readability.py`'s module docstring at the wiki page title `Lockable PROMs`, keeping the `## Key` section reference the docstring depends on
- Rewrote `py32_dfu.py`'s module docstring and its `DfuDeviceNotFoundError` message, and `firmware.py`'s `_install_with_dfu` docstring, to state the bootloader-entry condition directly (strap BOOT0 high with nBOOT1 = 1 and power-cycle, or ask a running firmware to reboot into the bootloader) rather than pointing at `doc/PY32F071-FIRMWARE-INSTALL.md`, which is deferred and never published
- Repointed `diff_db.py`'s emitted `[CITED: ...]` report string at the wiki page title `Infoic Field Dictionary`, keeping the bit-14/15 row citation structure intact
- Repointed `check_protection_readability_invariants.py`'s module docstring at `Lockable PROMs`
- In `firestarter_app/CLAUDE.md`: dropped the deferred-install-guide pointer from the `py32_dfu.py` inventory entry while keeping the "unverified against silicon" caveat verbatim, and repointed the third shield-revision lockstep rule (the one D-16 and the phase RESEARCH flagged as CONTEXT.md having missed on the app side) at the wiki page title `Shield Revisions`, keeping all four cited sections and the lockstep obligation
- Rewrote both `README.md` links (beta-channel walkthrough, shield-revision detail) as full `https://github.com/henols/firestarter_prom/wiki/<Page-Name>` URLs, per D-13's README exception
- Deleted the `doc/` entry from `firestarter_app/.planning/codebase/STRUCTURE.md`'s directory-tree diagram — corrected as a live map, not excluded as a historical record, per the plan's explicit correction to D-18
- Confirmed no Click command docstring was touched (`cli_handlers.py` and `main.py` have zero diff against the pre-plan commit), so `firestarter --help` and `firestarter fw --help` render unchanged
- Ran the full `firestarter_app` test suite three times across the plan (baseline, post-Task-1 targeted, final full run): **1972 passed** every time, matching the stated pre-plan baseline exactly

## Task Commits

1. **Task 1: Repair the app package modules** — `e541d3a` (fix) — protection_readability.py, py32_dfu.py, firmware.py, ic_layout.py, diagnostic_report.py
2. **Task 2: Repair the two tools modules and the project instructions** — `b79ac1f` (fix) — diff_db.py, check_protection_readability_invariants.py, CLAUDE.md
3. **Task 3: Repair the README links and correct the app's own codebase map** — `bb2fe2e` (docs) — README.md, .planning/codebase/STRUCTURE.md

**Plan metadata:** committed via this SUMMARY (meta-repo `docs(168-06)` commit follows)

## Files Created/Modified

- `firestarter_app/firestarter/ic_layout.py` — deleted the doc-citing clause from the `_PROTOCOL_DISPLAY_NAME` comment
- `firestarter_app/firestarter/diagnostic_report.py` — deleted the doc-citing parenthetical from the graduation-ladder comment
- `firestarter_app/firestarter/protection_readability.py` — module docstring repointed at `Lockable PROMs`
- `firestarter_app/firestarter/py32_dfu.py` — module docstring and `DfuDeviceNotFoundError` message rewritten, doc pointer dropped
- `firestarter_app/firestarter/firmware.py` — `_install_with_dfu` docstring rewritten, doc pointer dropped
- `firestarter_app/tools/diff_db.py` — emitted `[CITED: ...]` string repointed at `Infoic Field Dictionary`
- `firestarter_app/tools/check_protection_readability_invariants.py` — docstring repointed at `Lockable PROMs`
- `firestarter_app/CLAUDE.md` — deferred-guide pointer dropped from the py32_dfu.py entry; third lockstep rule repointed at `Shield Revisions`
- `firestarter_app/README.md` — both links rewritten as full wiki URLs
- `firestarter_app/.planning/codebase/STRUCTURE.md` — `doc/` tree entry removed

## Decisions Made

- **Extended single-line comment deletions to the whole citing clause** in `ic_layout.py` and `diagnostic_report.py` rather than deleting exactly the one line the plan's `<read_first>` named — a literal single-line cut left a grammatically broken remainder in both cases (the citation is embedded mid-sentence across wrapped lines). Net effect: `ic_layout.py`'s comment shrank from 11 to 8 lines; `diagnostic_report.py`'s stayed at 2 lines, reworded. Zero new comments were created in either case.
- **`firmware.py:629` was actually a private method's docstring, not literally "printed output"** as the plan's `<read_first>` characterized it — followed the plan's stated action for that site anyway (drop the pointer, state the condition directly), reusing the identical bootloader-entry phrasing already present in `py32_dfu.py`'s sibling error message so the two stay consistent.
- **Repointed `diagnostic_report.py`'s ladder-taxonomy sentence to end cleanly at "documents."** rather than trying to preserve the original's compound sentence structure, since the parenthetical `(see doc/community-validation.md)` was the entire second clause.

## Deviations from Plan

### Auto-fixed Issues

None — all edits were the plan's own specified repairs; no bugs, missing functionality, or blocking issues were discovered in scope.

### Noted Interpretation — Task 1's "no added `#` line" verify leg

**Observation, not a fix:** Task 1's automated verify (`git diff -U0 | grep '^+' | grep -cE '^\+\s*#'`) counts 5 lines as "added" — 2 in `diagnostic_report.py`, 3 in `ic_layout.py`. Both are reworded remnants of the same pre-existing comments the task instructed to shrink, not new comments: the two files together went from 13 comment lines to 10 (8 removed, 5 added — net **-3**, zero net growth). The raw `grep -c` heuristic cannot distinguish "reworded existing comment" from "genuinely new comment" because a partial-line edit always shows as one `-` and one `+` in a unified diff. The operator's actual rule — "the net comment count you add is zero" (stated in this plan's own critical_context) — is satisfied with margin (net negative). Recorded here rather than silently reported as a clean pass, per the instruction to document rather than paper over a check's literal-vs-intended gap.

### Out-of-scope discoveries (logged to `deferred-items.md`, not fixed)

**`tools/baseline/chip_database.baseline.json` still carries 9 stale `doc/AT28C04-ADAPTER.md` references.** The live `firestarter/data/chip_database.json` was already fixed and regenerated by plan 168-03 (0 references remain there), but the committed baseline snapshot used by the diff-against-baseline regression gate was not re-baselined at the same time. Not in this plan's `files_modified`, and repairing it means regenerating a baseline snapshot — generator/re-baseline work of the same shape as D-14, not a docstring/comment/string repair this plan owns. Logged with a recommended follow-up (whichever plan re-anchors baselines against the 168-03 database should refresh this file too, repointing the 9 strings at the wiki page title `AT28C04 Adapter`).

---

**Total deviations:** 0 auto-fixed; 1 noted interpretation (verify-leg literal-vs-intended gap); 1 out-of-scope discovery deferred
**Impact on plan:** No scope creep. The deferred baseline-file discovery does not affect this plan's own acceptance criteria (none of its files are in `files_modified`) and does not affect the full-suite green run (that file is a regression-gate fixture, not something the currently-passing 1972 tests read against `doc/` content).

## D-18 Historical Exclusions Named (app-repo side)

Per the plan's explicit correction to D-18: **`firestarter_app/.planning/codebase/STRUCTURE.md` is NOT a historical exclusion in this plan** — it is a live codebase map, not an archive, and was corrected (the `doc/` tree line removed) rather than left as evidence of a past state. This plan names **zero** app-side historical exclusions; the app repository's other candidate exclusions (test-tree doc-path oracles) sit outside `firestarter_app/`'s non-test scope entirely and are not this plan's concern. The three firmware-repo historical exclusions (`RED-BASELINE.md`, `FLASH-PATH-AND-PCB.md`, `eprom_params_citations.json`) belong to plan 168-07, not this one.

## Issues Encountered

None beyond the two items documented above under Deviations.

## User Setup Required

None. All work was source-file and documentation edits inside the already-checked-out `firestarter_app` repository on the existing milestone branch.

## Next Phase Readiness

- Every in-scope `doc/` reference in `firestarter_app` outside its test tree is repaired: two comments deleted, five docstrings/strings repointed at wiki page titles or rewritten to drop a deferred pointer, two README links converted to full wiki URLs, and the codebase map corrected.
- The full test suite remains green at 1972 passed, matching the pre-plan baseline exactly — no regression introduced.
- `firestarter --help` / `firestarter fw --help` render unchanged; no Click docstring was touched anywhere in this plan.
- Two items are logged to `deferred-items.md` for later plans: the baseline JSON's stale references (recommend whichever plan re-anchors baselines), and (pre-existing, from 168-05) `Lockable-PROMs.md`'s reference-style link false positives.
- No blockers identified for 168-07 through 168-13.

---
*Phase: 168-migrate-the-13-doc-files-moved-without-upgrading-a-claim*
*Completed: 2026-08-31*

## Self-Check: PASSED

- FOUND: .planning/phases/168-migrate-the-13-doc-files-moved-without-upgrading-a-claim/168-06-SUMMARY.md
- FOUND commit: e541d3a
- FOUND commit: b79ac1f
- FOUND commit: bb2fe2e
