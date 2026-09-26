---
phase: 86-variant-decode-correct-db-regen
plan: 01
subsystem: testing
tags: [build_db, infoic.xml, variant-decode, minipro, chip-database, pytest, host-only]

# Dependency graph
requires:
  - phase: 85-datasheet-acquisition
    provides: datasheets/README.md provenance-column model + committed 2516 datasheet (referenced by DECODE-NOTES gaps + 86-04)
provides:
  - "tools/DECODE-NOTES.md — VAR-01 variant-field decode dictionary (low + high byte), high-byte census, pinned minipro SHA a8efaedc, X88C64/FM1608 rationale, honest gaps"
  - "TestVariantDecodeClassification — FM1608 (GREEN) + X88C64 (RED-as-designed) classification oracle for Plan 02"
  - "test_variant_decode_evidence_stability.py — D-09 EVIDENCE wire-stability oracle (10 upstream-decoded chips, 2516 excluded)"
affects: [86-02-classifier-rewrite, 86-03-baseline-repin, 86-04-non-upstream-supplement, 87-naming-pass]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Refactor-under-test: Wave-0 tests pin POST-rewrite success criteria (FM1608/X88C64/EVIDENCE) BEFORE the Plan-02 classifier change, so Plan 02 is verified by a pre-existing oracle"
    - "EVIDENCE-sourced test data: chip identifiers loaded from .planning/v1.15/bench/EVIDENCE.json cells at test time (not hand-copied), with env-seam path override"
    - "Pinned-SHA reproducibility doc: record the upstream minipro master commit a live-fetch pipeline ran against"

key-files:
  created:
    - firestarter_app/tools/DECODE-NOTES.md
    - firestarter_app/tests/test_variant_decode_evidence_stability.py
  modified:
    - firestarter_app/tests/test_build_db_inclusion.py

key-decisions:
  - "Pinned minipro master SHA = a8efaedc236c1d9718bd28299dfbb99536b010ff (same commit as existing @ a8efaedc citations); recorded in DECODE-NOTES.md §0 as the regen provenance of record; build_db.py URL pin deferred to Plan 02 (D-05 discretion)"
  - "Variant HIGH byte documented as minipro T56/T76 algo_number (database.c#L1918), explicitly NOT a classification axis — the honest VAR-01 answer; classification keys on type/proto/pm_idx/flags"
  - "X88C64 EEPROM assertion is RED-as-designed against the current DB (UV-EPROM today; flags&0x10==0 misses 0x34); Plan 02 adds the proto_id==0x34 -> EEPROM arm to close it"
  - "2516 cleanly deferred to Plan 86-04: excluded from the EVIDENCE-stability oracle (only upstream-absent chip); no presence/absence assertion made in this plan"
  - "build_db.py NOT modified (verified via git diff across all 3 commits) — this plan writes documentation + tests only"

patterns-established:
  - "Wave-0 refactor-under-test oracle: classification + wire-stability assertions land before the classifier rewrite"
  - "EVIDENCE.json-sourced stability gate with FIRESTARTER_DB_FILE / FIRESTARTER_BASELINE_FILE / FIRESTARTER_EVIDENCE_FILE seams"

requirements-completed: [VAR-01]

# Metrics
duration: 14min
completed: 2026-06-25
---

# Phase 86 Plan 01: Variant-Decode Documentation + Wave-0 Test Oracle Summary

**VAR-01 variant-field decode documented in full (low byte = pinout discriminator, high byte = minipro `algo_number` per `database.c#L1918`, NOT a classifier) with pinned SHA `a8efaedc`, plus the refactor-under-test oracle (FM1608 GREEN / X88C64 RED / 10-chip EVIDENCE wire-stability GREEN) that Plan 02's classifier rewrite must satisfy.**

## Performance

- **Duration:** ~14 min
- **Started:** 2026-06-25
- **Completed:** 2026-06-25
- **Tasks:** 3
- **Files modified:** 3 (1 doc created, 1 test created, 1 test modified)

## Accomplishments

- Authored `tools/DECODE-NOTES.md`: full variant decode (low + high byte), full high-byte census table, the two collision cells (0x41 FRAM-vs-EEPROM by `type`; 0x31 27512-vs-X88C64 by `proto`), pinned minipro `master` SHA `a8efaedc236c1d9718bd28299dfbb99536b010ff`, X88C64 0x34->EEPROM display-only rationale, FM1608 type=4->0x28 identity, honest gaps (none for the high byte), and a cross-reference to Plan 86-04 for the 2516/2532 non-upstream supplement.
- Added `TestVariantDecodeClassification` to `test_build_db_inclusion.py`: FM1608 (algo 40 / FRAM / DIP28_JEDEC_SRAM_8K) PASSES against the current DB; X88C64 (electrical.type EEPROM + support_status protocol-not-implemented) is RED-as-designed (the gap Plan 02 closes).
- Created `test_variant_decode_evidence_stability.py`: the D-09 no-silent-move gate — sources the EVIDENCE chip labels from `EVIDENCE.json` at test time, asserts `algorithm`/`vpp_mv`/`pinout` vs the OLD baseline for the 10 upstream-decoded chips, explicitly excludes 2516 (owned by Plan 86-04), GREEN against the current pre-regen DB.
- Confirmed `build_db.py` is untouched across all three commits (refactor-under-test contract: no production decode logic changed this plan).

## Task Commits

Each task was committed atomically inside the `firestarter_app` submodule on branch `v1.16-protocol-first-architecture-rebuild`:

1. **Task 1: Author DECODE-NOTES.md (VAR-01 decode + pinned SHA)** - `bd462fa` (docs)
2. **Task 2: FM1608 + X88C64 classification assertions** - `a6f7e88` (test, tdd)
3. **Task 3: D-09 EVIDENCE wire-stability oracle** - `68865c1` (test)

**Plan metadata (meta repo):** committed separately with SUMMARY.md + STATE.md + ROADMAP.md.

## Files Created/Modified

- `firestarter_app/tools/DECODE-NOTES.md` (created) - VAR-01 variant decode dictionary: low/high byte semantics, high-byte census, pinned SHA, X88C64/FM1608 rationale, honest gaps, 86-04 cross-reference.
- `firestarter_app/tests/test_build_db_inclusion.py` (modified) - added `TestVariantDecodeClassification` (FM1608 GREEN, X88C64 RED-as-designed).
- `firestarter_app/tests/test_variant_decode_evidence_stability.py` (created) - D-09 EVIDENCE wire-stability oracle (10 upstream-decoded chips, 2516 excluded).

## Decisions Made

- **Pinned SHA = `a8efaedc236c1d9718bd28299dfbb99536b010ff`** — resolved via `git ls-remote ... master`; identical to the commit the existing `[VERIFIED: ... @ a8efaedc]` citations already pin, so the Phase-86 decode and prior v1.11 decode share one upstream reference. Recorded in DECODE-NOTES.md §0 as the load-bearing reproducibility artifact; `MINIPRO_XML_URL` pin (if applied) is deferred to Plan 02 per D-05 discretion.
- **X88C64 RED expectation recorded** — `test_x88c64_electrical_type_eeprom` asserts the POST-Plan-02 state (`electrical.type == "EEPROM"`); against the current DB X88C64P is `UV-EPROM` (flags&0x10==0 makes the flags rule miss proto 0x34), so this test FAILS by design until Plan 02 adds the `proto_id==0x34 -> EEPROM` arm. This is the refactor-under-test contract, not a defect.
- **2516 deferred to Plan 86-04** — the EVIDENCE-stability oracle scopes to the 10 upstream-decoded chips and explicitly excludes 2516 (the only EVIDENCE chip absent from infoic.xml). No presence/absence assertion about 2516 is made here, per D-10/D-11.

## Deviations from Plan

None - plan executed exactly as written.

The Task-2 TDD task's X88C64 assertion is RED, but this is the *designed* outcome (explicitly specified by the plan's acceptance criteria and `<behavior>` block as the gap Plan 02 closes), not a deviation. The plan is a refactor-under-test scaffold: it intentionally writes no production decode logic.

## Issues Encountered

- The Task-3 `<automated>` verify gate piped `pytest -q` output through `grep -Eq "passed|failed"`; this pytest version's `-q` summary prints dot-progress only (`..`) without the literal word "passed", so the grep did not match under `-q`. Resolved by confirming with a non-`-q` run (`2 passed in 0.03s`) — the substantive gate (tests collected + pass/fail to completion, rc=0) is satisfied. No code change needed.

## TDD Gate Compliance

Task 2 carried `tdd="true"`. Per the plan, this is a test-scaffold task that pins POST-rewrite criteria before the Plan-02 implementation:
- **RED gate (test commit):** `a6f7e88` adds the assertions; X88C64 is RED-as-designed against the current DB (the implementation that turns it GREEN is Plan 02, by design — this plan writes no production decode logic).
- FM1608 is GREEN immediately (already algo 40 / FRAM / DIP28_JEDEC_SRAM_8K in the current DB).
- No GREEN/REFACTOR commit in this plan: the GREEN transition for X88C64 is explicitly owned by Plan 86-02 (the classifier rewrite). This is the intended refactor-under-test sequencing, not a missing gate.

## Verification Results

- Task 1 gate: `VAR01-NOTES-OK` (database.c#L1918 + algo_number + X88C64 + 8-hex-char SHA all present); `build_db.py` git diff empty.
- Task 2 gate: `TEST-SCAFFOLD-ADDED`; exactly 2 tests collected by `-k "fm1608 or x88c64"`; FM1608 PASS, X88C64 FAIL (`UV-EPROM != EEPROM`) RED-as-designed; ruff clean.
- Task 3 gate: `EVIDENCE-TEST-ADDED` (`2 passed`); EVIDENCE labels sourced from EVIDENCE.json, 2516 excluded, 10 upstream-decoded chips wire-stable vs OLD baseline; ruff clean.
- Overall: `1 failed (X88C64 RED-as-designed), 3 passed (FM1608 + 2 EVIDENCE)`; `build_db.py` untouched across HEAD~3..HEAD.

## Next Phase Readiness

- Plan 02 (classifier rewrite) has its complete test oracle: FM1608/X88C64 classification + the D-09 EVIDENCE wire-stability gate, all keyed off the OLD baseline. Turning X88C64 GREEN (proto 0x34 -> EEPROM) and keeping FM1608 + the 10 EVIDENCE chips stable is the explicit Plan-02 success bar.
- DECODE-NOTES.md records the pinned SHA Plan 02 should pin `MINIPRO_XML_URL` to (or cite as provenance).
- 2516 handling is cleanly fenced off for Plan 86-04 (non-upstream supplement); no Wave-0 assertion blocks it.
- No blockers.

## Self-Check: PASSED

- FOUND: firestarter_app/tools/DECODE-NOTES.md
- FOUND: firestarter_app/tests/test_variant_decode_evidence_stability.py
- FOUND: firestarter_app/tests/test_build_db_inclusion.py (modified — TestVariantDecodeClassification present)
- FOUND commit: bd462fa (Task 1)
- FOUND commit: a6f7e88 (Task 2)
- FOUND commit: 68865c1 (Task 3)

---
*Phase: 86-variant-decode-correct-db-regen*
*Completed: 2026-06-25*
