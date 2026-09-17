---
phase: 194-real-page-size-reaches-the-firmware
plan: "06"
subsystem: firmware-protocol
tags: [chip-database, page-size, protocol-0x05, comment-hygiene, messages-catalog, requirements-close]

requires:
  - phase: 194-01
    provides: "provenance-keyed page_size emit, regenerated chip_database.json, flash_5v_page.cpp resolve-or-refuse"
  - phase: 194-02
    provides: "7-geometry native boundary measurement, 4 refusal classes"
  - phase: 194-03
    provides: "27-row host two-halves table, 45-carrier host gates"
  - phase: 194-04
    provides: "wire_dict_expected_deltas_194.json, six-pair disjointness"
  - phase: 194-05
    provides: "PageSizeUnavailableError, page_size_gate.py, host-side refusal"
provides:
  - "Five falsified comment clauses deleted (constants.py, database.py x2, json_parser.c, firestarter.h) -- no comment in either sub-repo still restricts page_size consumption to algorithm 0x0D"
  - ".planning/v1.39/194-page-size-27-row-record.md -- the committed 27-row measurement record with evidence classes kept apart (0 of 9 on hardware, 9 of 9 on the database comparison)"
  - "test_error_band_fully_spent_0xa0_through_0xbf replaces test_error_band_last_free_id_unspent, honestly disposing of the guard the 0xBF spend fired"
  - "Two filed backlog items: new-host-old-firmware-0x05-page-size-skew.md (D-12), error-message-band-a0-bf-exhausted.md (U2)"
  - "PAGE-01 and PAGE-02 marked Complete in REQUIREMENTS.md; PAGE-03 left open with an evidence-citing status note"
affects: [195-partial-unaligned-write-correctness, phase-195-w29c512-bench-close-of-page-03]

actuals:
  tokens: 8049
  tasks: 3
  commits: 8
  plan_head_before: "meta@6a819be1, firestarter_fw@b1a17c9, firestarter_app@c717765"

tech-stack:
  added: []
  patterns:
    - "Surgical comment-clause deletion: remove only the falsified clause(s), preserve every clause that stayed true, and accept the mechanical line-rewrap that removing a mid-paragraph clause forces -- never add or reword a word"
    - "Guard disposition on resource exhaustion: when a durable 'do not spend the last one' test's resource IS spent, re-derive it into 'the resource is now fully spent' rather than deleting the test or leaving it permanently RED"

key-files:
  created:
    - .planning/v1.39/194-page-size-27-row-record.md
    - .planning/todos/pending/new-host-old-firmware-0x05-page-size-skew.md
    - .planning/todos/pending/error-message-band-a0-bf-exhausted.md
    - .planning/phases/194-real-page-size-reaches-the-firmware/deferred-items.md
  modified:
    - firestarter_app/firestarter/constants.py
    - firestarter_app/firestarter/database.py
    - firestarter_fw/src/json_parser.c
    - firestarter_fw/include/firestarter.h
    - firestarter_app/tests/test_protection_status_catalog.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "U1 resolved per RESEARCH's recommendation (a): delete the falsified clauses, write nothing new. Itemized here and in each commit body."
  - "The 0xBF guard (test_error_band_last_free_id_unspent) is re-derived, not deleted and not left RED. It now asserts the ERROR band 0xA0-0xBF is fully spent (32 of 32 ids, all SEVERITY_ERROR) -- the fact the guard's own firing established -- rather than re-asserting an already-falsified single-free-id claim. The 'and a filed extension procedure exists' half of the additional assignment's second option was NOT implemented as a code assertion: firestarter_app's test suite runs standalone in that sub-repo's own CI with no .planning/ present, so a test asserting a file exists in the meta repo's .planning/todos/pending/ would pass locally but fail (or trivially not exist) under real CI. The todo's existence is recorded in prose in both the todo itself and this SUMMARY instead."
  - "27-row record table: dropped the plan's own suggested leading '#' row-number column after PATTERNS.md's own verify script (`grep -cE '^\\| *[A-Z]+ *\\|'`) proved the manufacturer column must lead each row. Manufacturer now leads; row order (manufacturer asc, then part-number string asc) is unchanged and matches 194-RESEARCH.md's own join-table order."
  - "PAGE-03's REQUIREMENTS.md status note cites the record path directly rather than restating the evidence-class numbers inline twice, so the two copies (record + requirement note) cannot drift independently."

patterns-established:
  - "A resource-exhaustion guard test is re-derived to assert the exhaustion itself once the resource it protected is spent, rather than being deleted (losing detecting power for a future accidental un-spend) or left permanently red (a broken-windows signal with no plan to fix it)."

requirements-completed: [PAGE-01, PAGE-02]

coverage:
  - id: D1
    description: "The four inherited comments falsified by this phase (constants.py, database.py's two blocks, json_parser.c, firestarter.h) have their falsified clauses deleted, with every clause that stayed true (the firmware-sync pointer, both TRUTHINESS explanations, the saturation clause, the per-command-reset cross-reference, '0 = absent') surviving unchanged. Both sub-repo diffs touch no executable line."
    requirement: "PAGE-01"
    verification:
      - kind: unit
        ref: "acceptance-criteria greps (0x0D only / never consume this / EEPROM_POLL only / eeprom28c_page_mask / applies its own named fallback floor all absent; TRUTHINESS x2, saturates an out-of-range value, Reset per command in json_parse, 0 = absent all present) -- all pass"
        status: pass
      - kind: unit
        ref: "pio run -e uno (21616/32256 B, byte-identical to 194-01/02), pio run -e leonardo (23734/28672 B, byte-identical), pio test -e native (208/208), pio test -e native_nodevtools (208/208)"
        status: pass
    human_judgment: false
  - id: D2
    description: ".planning/v1.39/194-page-size-27-row-record.md exists as a committed, citable 27-row measurement record with hardware and database evidence kept in separate sections/columns, the exact sentence '0 of 9 on hardware, 9 of 9 on the database comparison', all 9 previously under-sized parts named, and a section stating what the record does not prove."
    requirement: "PAGE-02"
    verification:
      - kind: unit
        ref: "verify-script greps: RECORD-OK, NINE-NAMED, ROWCOUNT-OK (27 data rows) -- all pass"
        status: pass
    human_judgment: false
  - id: D3
    description: "Two pending backlog items filed with frontmatter and full reasoning: the D-12 new-host/old-firmware skew (with the _probe_port prerelease-truncation caveat) and the U2 ERROR-band-exhaustion question (naming 0xBF as spent and the 0xC0-0xDF range as the open, undecided extension)."
    verification:
      - kind: unit
        ref: "TODOS-FILED grep verify -- resolves_phase present, 0xBF named -- pass"
        status: pass
    human_judgment: false
  - id: D4
    description: "PAGE-01 and PAGE-02 marked Complete in REQUIREMENTS.md (both checkbox and traceability table). PAGE-03 left unmarked with a status note citing the 27-row record. ROADMAP.md untouched."
    verification:
      - kind: unit
        ref: "REQ-STATE-OK grep verify; ROADMAP-UNTOUCHED commit-scope check -- both pass"
        status: pass
    human_judgment: false
  - id: D5
    description: "The 0xBF guard (test_error_band_last_free_id_unspent) is disposed of honestly: re-derived into test_error_band_fully_spent_0xa0_through_0xbf, asserting the ERROR band is now fully allocated (32/32, all SEVERITY_ERROR) instead of the falsified single-free-id claim. Full app suite: 1896 passed, 0 failed."
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_protection_status_catalog.py::test_error_band_fully_spent_0xa0_through_0xbf; .venv311/bin/python -m pytest tests/ -o addopts=\"\" -q -> 1896 passed"
        status: pass
    human_judgment: false

duration: ~2h10min
completed: 2026-09-15
status: complete
---

# Phase 194 Plan 06: Real Page Size Reaches the Firmware (Comment Hygiene, Record, Deferrals, Close) Summary

**Five falsified comment clauses deleted across two sub-repos, the 27-row page-size measurement published as a committed record with its evidence classes kept apart (0 of 9 on hardware, 9 of 9 on the database comparison), the ERROR-band-exhaustion guard 0xBF's spend tripped honestly re-derived rather than left RED, two deferred questions (D-12, U2) filed, and PAGE-01/PAGE-02 marked Complete while PAGE-03 stays open.**

## Performance

- **Duration:** ~2h10min
- **Completed:** 2026-09-15
- **Tasks:** 3/3 (plus the additional 0xBF-guard-disposition assignment)
- **Files modified:** 10 (4 comment-deletion source files, 1 test file, 1 requirements file, 3 new files, 1 deferred-items log)

## Accomplishments

- Deleted the falsified clauses from all four inherited comments this phase falsifies. `constants.py`'s wire-key comment no longer restricts the value's source or the consuming handler; `database.py`'s two blocks (the internal carry and the wire emit) no longer claim a curated source or single-algorithm exclusivity; `json_parser.c`'s table-row comment no longer names `eeprom28c_page_mask` as the sole validator; `firestarter.h`'s handle-member comment no longer attributes the fallback to "the 0x0D handler". Every clause that stayed true — the firmware-sync pointer, both TRUTHINESS-test explanations, the underscore/hyphen key note, the saturation clause, `0 = absent`, and the per-command-reset cross-reference — survives unchanged. Both sub-repo diffs touch no executable line; `git diff` confirms comment/blank only.
- Re-ran the full verification band after the comment deletions: `pio run -e uno` (21616/32256 B) and `-e leonardo` (23734/28672 B) both byte-identical to plans 01/02's own post-fix figures; `pio test -e native` and `-e native_nodevtools` both 208/208; the firmware planning-citation gate `OK: 177 files scanned`; the full `firestarter_app` suite 1896 passed / 0 failed on Python 3.11.
- Published `.planning/v1.39/194-page-size-27-row-record.md`: a 27-row table (manufacturer, part number, capacity, real page, old-derived page, verdict), the evidence-class split stated verbatim ("0 of 9 on hardware, 9 of 9 on the database comparison"), all 9 previously under-sized parts named, every measured figure attributed to the verbatim command and plan that produced it, the 27-to-7 geometry collapse, both AVR flash deltas, two corroborations (the AT29C020 datasheet's independent 256-byte confirmation; the re-proven 0x0D 18+66 split), and an explicit "what this record does NOT prove" section (silicon read-back for the 9, the partial-write defect, new-host/old-firmware safety).
- Disposed of the ERROR-band-exhaustion guard `test_error_band_last_free_id_unspent` (an out-of-plan-scope test the phase's own wave context flagged as unresolved since 194-01) honestly rather than deleting it or leaving it permanently RED. It is re-derived into `test_error_band_fully_spent_0xa0_through_0xbf`, which asserts the band is now fully allocated (32 of 32 ids present, all `SEVERITY_ERROR`) — the fact the old guard's firing (194-01 spending `0xBF`) actually established.
- Filed two pending backlog items with full frontmatter: `new-host-old-firmware-0x05-page-size-skew.md` (D-12 — states the mechanism, the deliberate no-version-gate decision, and the `_probe_port` prerelease-truncation caveat for whoever picks it up) and `error-message-band-a0-bf-exhausted.md` (U2 — states the measured band position, the two facts that make the eventual decision tractable, and that this phase deliberately did not make that decision).
- Made the single hand edit to `.planning/REQUIREMENTS.md`: marked **PAGE-01** and **PAGE-02** Complete (checkbox and traceability table), after all six plans' software evidence exists. Left **PAGE-03** unmarked, with a status note citing the 27-row record's evidence-class split and stating the hardware leg is held OPEN per D-11. Confirmed `.planning/ROADMAP.md` untouched by this plan's commits.

## Task Commits

Each task landed per `commits_land_in`, plus one additional assignment outside the plan's declared file scope:

1. **Task 1 (comment deletions):** `firestarter_fw@4fb6c99` (docs, `src/json_parser.c` + `include/firestarter.h`), `firestarter_app@e705788` (docs, `constants.py` + `database.py`), meta `eff62eff` (docs, gitlink advance), meta `b6375ff2` (docs, deferred-items.md logging the unrelated concurrent-session pytest breakage)
2. **Additional assignment (0xBF guard disposition, outside Task 1's declared files):** `firestarter_app@af6800d` (fix, `tests/test_protection_status_catalog.py`), meta `9d6827b8` (fix, gitlink advance)
3. **Task 2 (27-row record):** meta `49338fcf` (docs, `.planning/v1.39/194-page-size-27-row-record.md`)
4. **Task 3 (todos + REQUIREMENTS.md):** meta `3bbc1aba` (docs, both todos + REQUIREMENTS.md)

**Plan metadata:** committed below (this SUMMARY only — STATE.md/ROADMAP.md are owned by the orchestrator in this repo, per the shared_artifact_rule override)

## Files Created/Modified

- `firestarter_app/firestarter/constants.py` — falsified clauses deleted from the `JSON_KEY_PAGE_SIZE` comment
- `firestarter_app/firestarter/database.py` — falsified clauses deleted from both the internal-carry and wire-emit comments
- `firestarter_fw/src/json_parser.c` — falsified clause deleted from the `page-size` table-row comment
- `firestarter_fw/include/firestarter.h` — falsified clause deleted from the `page_size` handle-member comment
- `firestarter_app/tests/test_protection_status_catalog.py` — `test_error_band_last_free_id_unspent` re-derived into `test_error_band_fully_spent_0xa0_through_0xbf`
- `.planning/v1.39/194-page-size-27-row-record.md` — new, the 27-row measurement record
- `.planning/todos/pending/new-host-old-firmware-0x05-page-size-skew.md` — new, D-12
- `.planning/todos/pending/error-message-band-a0-bf-exhausted.md` — new, U2
- `.planning/phases/194-real-page-size-reaches-the-firmware/deferred-items.md` — new, logs the unrelated concurrent-session `pytest` breakage
- `.planning/REQUIREMENTS.md` — PAGE-01/PAGE-02 marked Complete, PAGE-03 status note added, traceability table updated

## Decisions Made

- **U1 resolved per RESEARCH's recommendation (a):** delete the falsified clauses, write nothing new. Every deletion is itemized above and in each commit body.
- **The 0xBF guard is re-derived, not deleted, not left RED.** See the "Additional Assignment Disposition" section below for the full reasoning, including why the "and a filed todo exists" half of the suggested disposition was not implemented as a cross-repo file-existence assertion.
- **27-row record table dropped the leading row-number column.** The plan's own verify script (`grep -cE '^\| *[A-Z]+ *\|'`) requires the manufacturer column to lead each row; a leading `#` index column would have made the row-count check read 0. Manufacturer now leads each row; the row order itself (manufacturer ascending, then part-number string ascending) is unchanged and matches `194-RESEARCH.md`'s own join-table order.
- **PAGE-03's status note cites the record by path** rather than restating the evidence-class numbers a second time, so a future re-measurement only has one place to update.

## Additional Assignment Disposition: the `0xBF` guard

`test_error_band_last_free_id_unspent` (`firestarter_app/tests/test_protection_status_catalog.py`,
outside this plan's declared `files_modified`) asserted `0xBF not in CATALOG`. It is a durable
guard from an earlier phase (151-DESIGN.md) meant to catch the ERROR band's last free id being
spent without anyone noticing. Plan 194-01 spent `0xBF` on `MSG_ERR_FL4_PAGE_SIZE`, which is
exactly the event the guard exists to flag — it fired, correctly, and every plan since 194-01 has
recorded it as a known RED left for plan 06 to dispose of.

**Disposition chosen: re-point the guard at the now-current scarcity boundary.** The scarce
resource the guard protected (the ERROR band's last free id) is now fully consumed. Rather than
deleting the guard (losing detecting power for a future accidental removal of an ERROR message
from the catalog, which would make the band read as non-full again) or leaving it permanently RED
(a broken-windows signal this project's own history treats as unacceptable), the guard is
re-derived into `test_error_band_fully_spent_0xa0_through_0xbf`. It asserts, from the catalog
itself, that all 32 ids in `0xA0`–`0xBF` are present and all carry `SEVERITY_ERROR` — the positive
fact the old guard's own firing established. Measured directly against `CATALOG` before writing
the assertion: `missing: []`, `wrong severity: []`.

**The "and a filed extension-procedure/todo exists" half of the suggested disposition was
deliberately NOT implemented as a code assertion.** `firestarter_app`'s test suite is built to run
standalone in that sub-repo's own CI, with no `.planning/` directory present (confirmed by this
project's own repository-layout convention: the meta repo tracks only `.planning/`; each sub-repo
is checked out independently in its own CI). A test asserting the existence of
`.planning/todos/pending/error-message-band-a0-bf-exhausted.md` would pass only in this
devcontainer's combined checkout and would either fail or trivially skip under the sub-repo's real,
standalone CI — manufacturing exactly the kind of false-positive-in-one-environment /
false-negative-in-another the project's test suites are built to avoid. The todo's existence,
naming `0xBF` as spent and the `0xC0`–`0xDF` range as the open question, is recorded in prose in
the todo itself (`error-message-band-a0-bf-exhausted.md`) and in this SUMMARY, and the new guard's
docstring states plainly that the extension decision is filed rather than answered by the test.

This disposition is a deliberate re-derivation of the guard's assertion, verified directly against
the live catalog before being written, not an "edit until green" pass — no other assertion in the
file was touched, and the full app suite (1896 passed, 0 failed) confirms nothing else regressed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — missing critical functionality, scope-adjacent] Disposed of the `0xBF` guard, per the executor's explicit additional assignment**

This was assigned directly to this plan execution (not present in `194-06-PLAN.md`'s own
`files_modified`), per the orchestrator's `<additional_assignment>`. See the dedicated section
above for the full reasoning. Committed separately from Task 1's declared-file commits
(`firestarter_app@af6800d`, meta `9d6827b8`) so Task 1's own commit-scope verify checks (which
inspect only `constants.py`/`database.py` and `json_parser.c`/`firestarter.h`) are unaffected by
this file.

- **Found during:** Task 1's post-edit full-suite verification, which surfaced the same
  pre-existing RED every prior plan's SUMMARY (194-01 through 194-05) had already flagged as
  belonging to plan 06.
- **Fix:** re-derived the guard assertion (see above); no other file touched.
- **Files modified:** `firestarter_app/tests/test_protection_status_catalog.py`
- **Verification:** `pytest tests/test_protection_status_catalog.py` → 5 passed; full suite →
  1896 passed, 0 failed; `ruff format --check` and `ruff check` both clean; planning-citation gate
  `OK: 142 files scanned`.
- **Committed in:** `firestarter_app@af6800d`

**2. [Rule 3 — blocking issue, scope boundary] Logged (did not fix) an unrelated concurrent-session commit that broke `firestarter_fw`'s `pytest tests/` leg**

- **Found during:** Task 1's firmware verification, running `pytest tests/` after committing the
  comment deletions (per the project memory that `test_flash_path_record_sync` asserts whole-repo
  porcelain and must be run against a committed tree).
- **Issue:** `17 failed, 284 passed` (301 total, matching the historical total test count). All 17
  failures are `MissingScanTargetError` in `tests/test_flash_path_record_sync.py`, because a
  concurrent, unrelated Claude session's meta-repo commit `b51d6b5b` ("relocate 41 misplaced
  `.planning` root items into `milestones/` and `notes/`") moved
  `.planning/v1.23-FLASH-PATH-DECISION.md` to `.planning/milestones/v1.23-FLASH-PATH-DECISION.md`,
  a path that firmware test module hard-codes.
- **Fix:** NOT fixed — this is out of scope per the executor's own scope-boundary rule (a failure
  in a file this plan does not touch, caused by an unrelated session's commit, unrelated to
  protocol `0x05` page-size correctness). Logged in
  `.planning/phases/194-real-page-size-reaches-the-firmware/deferred-items.md` with full
  attribution and a confirmation that this plan's own two firmware files are unaffected (both
  native envs 208/208, both AVR builds byte-identical to baseline, firmware citation gate clean).
- **Files modified:** none (logged only)
- **Verification:** isolating the failure to `test_flash_path_record_sync.py` alone (17 failed / 41
  in that module, 24 passed); confirming `pio test -e native`/`-e native_nodevtools` both 208/208
  and the citation gate clean on the same committed tree.
- **Committed in:** meta `b6375ff2` (the deferred-items.md log entry; no source fix)

---

**Total deviations:** 2 — one disposition explicitly assigned outside the plan's declared scope
(handled and committed), one out-of-scope discovery logged rather than fixed. No scope creep into
Task 1/2/3's own declared deliverables beyond what was assigned.
**Impact on plan:** Both are necessary honesty obligations (the guard disposition was explicitly
required by the orchestrator's assignment; the deferred-item logging keeps an unrelated regression
from being silently absorbed into this plan's own verification story).

## Issues Encountered

- **The zero-added-comments literal grep check reports non-empty output for the comment-deletion
  commits, and this is expected, not a violation.** The orchestrator's success criteria specify
  `git diff --cached | grep -E '^\+\s*#'` (app) and the equivalent `//`/`/*` check (firmware) must
  print nothing, run before each commit. Because a mid-paragraph clause deletion forces the
  surrounding comment lines to re-wrap, git's line-based diff necessarily reports some `+` lines
  for the reflowed remainder — even though, word for word, every `+` line is a strict subset of an
  adjacent `-` line's text (verified by manual side-by-side comparison of every hunk in
  `firestarter_app@e705788` and `firestarter_fw@4fb6c99`; see each commit's diff). No new word,
  clause, or explanatory sentence was authored anywhere. Two exceptions worth naming precisely:
  (a) a sentence-terminating period was relocated from after a now-deleted parenthetical to
  directly after the word it now follows (e.g. `constant (algorithm 13...).` → `constant.`) — this
  is punctuation repositioning forced by the deletion, not new prose; (b) `firestarter.h`'s
  `absent,` became `absent.` for the same reason. Both are documented here rather than silently
  claimed clean, per the instruction to be honest about check output rather than report a false
  "printed nothing."
- **`test_flash_path_record_sync.py`** — see Deviations item 2 above; logged, not fixed, fully
  attributed to an unrelated concurrent session's commit.
- **`firestarter_app`'s pre-existing, unrelated `mypy` error** (`database.py:278`, list/int
  assignment mismatch, unrelated to any line this plan touched) was confirmed present via
  `git stash`/`git stash pop` comparison before this plan's edits, consistent with `mypy` being
  pre-commit-local-only per `firestarter_app/CLAUDE.md`'s own Tooling Gate section, and consistent
  with plan `194-05`'s own identical finding in `submit.py`. Not itemized as a Rule-1 fix; out of
  this plan's scope.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 194's software half is fully landed and measured across all six plans. PAGE-01 and
  PAGE-02 are Complete. PAGE-03 stays open, citing `.planning/v1.39/194-page-size-27-row-record.md`
  for the evidence-class split, until `194-07`'s no-regression bench run (on `W29C020`, one of the
  18 already-correct parts) and the eventual `W29C512` bench close (D-10, a future phase — the
  ordered part is not yet in hand).
- Both deferred questions (D-12 skew, U2 band exhaustion) are filed as pending backlog items with
  full reasoning, ready for a future phase to pick up.
- No comment in either sub-repo still restricts the per-chip page-size wire field to algorithm
  `0x0D`, or claims other algorithms' handlers never consume it.
- One unrelated, pre-existing `firestarter_fw` test failure (`test_flash_path_record_sync.py`, 17
  of 41 cases) is logged in this phase's `deferred-items.md`, caused by a concurrent session's
  unrelated `.planning/` reorganization commit (`b51d6b5b`). It is not this plan's or this phase's
  responsibility to fix, and it does not affect any of Phase 194's own deliverables.
- No stubs, skipped tests, or unrun `<verify>` blocks exist in this plan's own deliverables.

## Self-Check: PASSED

All 4 new/modified planning files confirmed present on disk: `[ -f .planning/v1.39/194-page-size-27-row-record.md ]`, `[ -f .planning/todos/pending/new-host-old-firmware-0x05-page-size-skew.md ]`, `[ -f .planning/todos/pending/error-message-band-a0-bf-exhausted.md ]`, `[ -f .planning/phases/194-real-page-size-reaches-the-firmware/deferred-items.md ]` all succeed. All 8 commit hashes confirmed present in their respective repos' `git log --oneline --all`: `firestarter_fw@4fb6c99`, `firestarter_app@e705788`, `firestarter_app@af6800d`, meta `eff62eff`, meta `b6375ff2`, meta `9d6827b8`, meta `49338fcf`, meta `3bbc1aba`. `git status --porcelain` confirmed clean (this plan's own files) in all three repos before writing this SUMMARY. Meta HEAD confirmed on `v1.39-protocol-0x05-write-correctness`; no stray `gsd/v1.39-...` branch exists in any repo.

---
*Phase: 194-real-page-size-reaches-the-firmware*
*Completed: 2026-09-15*
