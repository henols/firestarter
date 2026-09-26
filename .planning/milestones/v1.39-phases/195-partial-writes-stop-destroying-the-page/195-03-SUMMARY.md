---
phase: 195-partial-writes-stop-destroying-the-page
plan: 03
subsystem: host-write-path
tags: [flash4, protocol-0x05, page-size, host-guard, regression-surface, chip-database]

requires:
  - phase: 195-partial-writes-stop-destroying-the-page
    provides: "the tracer slice from plan 01 -- MSG_ERR_FL4_PAGE_ALIGN, the firmware per-chunk guard, and page_size_gate.py's require_page_alignment, all proven end to end on one refusal and one pass-through"
provides:
  - "_ACCEPTED_PAGE_SIZES in page_size_gate.py, so require_page_size refuses the same set of page sizes the firmware's flash_5v_page_mask refuses -- not only an absent one"
  - "the alignment guard's full property matrix in tests/test_page_size_alignment_refusal.py -- every rejected class, a pass-through leg at every page size the shipped database carries, both fail-closed legs, the two no-op legs, the WRITE-02 empty edge, and the dev-test region shape"
  - "tests/test_validated_parts_regression_surface.py, measuring criterion 4's real shape from the shipped database: the SST39SF020 protocol correction, the three validated parts' page sizes, the AE29F2008/W29C020 two-name silicon identity, and the 27-row dev-test region partition"
  - "the host-page-size-gate-accepts-invalid-values todo closed under .planning/todos/completed/"
affects: [195-04, 195-05]

actuals:
  tokens: 7600
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Database-derived test fixtures: pass-through legs pick their part by reading chip_database.json for the first row at each page size, never by a hard-coded part name, so a database regeneration cannot silently invalidate the matrix"
    - "Whole-row dict comparison (minus the name field) as the measured form of a two-name silicon-identity claim"

key-files:
  created:
    - firestarter_app/tests/test_validated_parts_regression_surface.py
  modified:
    - firestarter_app/firestarter/page_size_gate.py
    - firestarter_app/tests/test_page_size_write_refusal.py
    - firestarter_app/tests/test_page_size_alignment_refusal.py
    - .planning/todos/completed/host-page-size-gate-accepts-invalid-values.md

key-decisions:
  - "D-05 closed: _ACCEPTED_PAGE_SIZES is an explicit frozen set {1, 2, 4, 8, 16, 32, 64, 128, 256, 512} rather than a recomputed power-of-two-and-ceiling predicate, so a reader can compare it against flash_5v_page_mask by eye. require_page_size now raises for a recorded-but-invalid value (96, 1024, 65535) using a distinct message naming the offending value, in addition to the pre-existing absent/zero refusal -- no second exception type was added; PageSizeUnavailableError still covers both."
  - "The pass-through matrix in test_page_size_alignment_refusal.py picks its part per page size by reading the live database (first match wins) rather than by name: 64 -> AT29C256, 128 -> AE29F1008, 256 -> AE29F4008, 512 -> AT29BV040,AT29LV040 (as resolved at test-run time; a database regeneration may pick different parts for the same page sizes without invalidating the leg)."
  - "The AE29F2008/W29C020 two-name silicon identity (test_validated_parts_regression_surface.py) is asserted as a whole-row dict comparison with only part_number popped from both sides -- part_number is the name itself and is definitionally different; every other field, including chip_id_value, protect_off_before/after and infoic_page_size_raw, must match or the leg goes red."
  - "The dev-test region matrix is measured directly from chip_database.json's raw programming.algorithm and programming.page_size fields (27 protocol 0x05 rows total), not through EpromDatabase's wire-dict conversion, so the count is over shipped data rather than an interpretation of it."

requirements-completed: []

coverage:
  - id: D1
    description: "The host page-size gate refuses the same set of page sizes the firmware refuses (D-05): a non-zero power of two no greater than 512, closing the pending review finding"
    requirement: "WRITE-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_write_refusal.py#test_write_eprom_invalid_page_size_refuses_before_operation_context"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_write_refusal.py#test_write_eprom_valid_page_size_reaches_operation_context"
        status: pass
    human_judgment: false
  - id: D2
    description: "The alignment guard's full property matrix is proven at every page size the shipped database carries, with parts chosen by reading the database, plus both fail-closed legs and the WRITE-02 empty edge pinned in the accepting direction"
    requirement: "WRITE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_alignment_refusal.py#test_write_eprom_page_exact_write_reaches_operation_context_at_every_shipped_page_size"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_alignment_refusal.py#test_write_eprom_zero_byte_payload_reaches_operation_context"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_alignment_refusal.py#test_write_eprom_unparseable_address_refuses_before_operation_context"
        status: pass
    human_judgment: false
  - id: D3
    description: "Criterion 4's regression surface measured from the shipped database: the SST39SF020 protocol correction, the three validated parts' page sizes, the two-name silicon identity, and the 27-row dev-test region partition"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_validated_parts_regression_surface.py#test_sst39sf020_is_not_flash4_and_the_other_three_validated_parts_are"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_validated_parts_regression_surface.py#test_ae29f2008_and_w29c020_are_the_same_silicon_under_two_names"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_validated_parts_regression_surface.py#test_dev_test_region_matrix_over_all_27_protocol_0x05_rows"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-16
status: complete
---

# Phase 195 Plan 03: Host page-size validity, the full alignment matrix, and criterion 4 measured Summary

**The host gate now refuses the same 96/1024/65535-class page sizes the firmware refuses; the alignment guard's full property matrix is proven at every page size the shipped database actually carries; and criterion 4's four-validated-parts claim is measured from the database rather than transcribed from the roadmap.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-09-16 (approx, continuing from plan 01)
- **Completed:** 2026-09-16
- **Tasks:** 3
- **Files modified:** 4 (1 created)

## Accomplishments

- `page_size_gate.py` gained `_ACCEPTED_PAGE_SIZES = frozenset({1, 2, 4, 8, 16, 32, 64, 128, 256, 512})`, the same non-zero-power-of-two-no-greater-than-512 set `flash_5v_page_mask` enforces firmware-side. `require_page_size` now refuses a recorded-but-invalid value (96, 1024, 65535) with a new message (`_INVALID_PAGE_SIZE_FORMAT`) naming the offending value, in addition to the pre-existing absent/zero refusal (`_REFUSAL_FORMAT`) -- the two messages are worded so neither can be mistaken for the other: "no page size is recorded" only ever fires for absent/zero, "the recorded page size {N} is not one this protocol accepts" only ever fires for a recorded-but-invalid value.
- The pending `host-page-size-gate-accepts-invalid-values.md` todo is closed under `.planning/todos/completed/`, naming the accepted set and the module that now enforces it.
- `tests/test_page_size_write_refusal.py` grew from 9 to 16 tests: one parametrized leg over the three rejected classes (96, 1024, 65535) plus a positive-control leg over all four accepted values (64, 128, 256, 512).
- `tests/test_page_size_alignment_refusal.py` grew from 4 to 29 tests, covering: the three unaligned-refusal classes (unaligned-start-only, partial-length-only, both together); the two fail-closed legs (unparseable address string, missing payload file); a 16-case pass-through matrix (4 page sizes x 1-or-2-page payload x address none-or-one-page), with the part for each page size picked by reading the database rather than hard-coded; the WRITE-02 empty edge, asserted by the operation context having been *entered* rather than by the mere absence of an exception; the two no-op legs (another algorithm, a non-write operation), each proven with a nonexistent payload path so the early returns are shown to run before any filesystem access; and the D-12 dev-test-region-shape leg (256 bytes at address 0 passes at page size 128, refuses at page size 512).
- New `tests/test_validated_parts_regression_surface.py` (5 tests) measures criterion 4 directly from `chip_database.json`: `SST39SF020,SST39SF020A` carries algorithm 6, not the flash4 protocol id, while `W29C020,W29C020C,W29C022`, `W29C040,W29C042` and `AE29F2008` all carry algorithm 5; their recorded page sizes are 128, 256 and 128 respectively (`SST39SF020` records none); `AE29F2008` and `W29C020,...`'s raw rows are equal on every field except `part_number` (the name itself), including `chip_id_value`; and the dev-test region partition over all 27 protocol-0x05 rows is exactly 25 aligned / 2 refused, both refused rows recording page size 512, with none of the three validated parts among them.

## Task Commits

Each task was committed atomically, inside `firestarter_app` on the `v1.39-protocol-0x05-write-correctness` branch, plus one meta-repo commit closing the todo:

1. **Task 1: Make the two refusal layers agree on which page sizes are valid**
   - firestarter_app: `7569dd3` (feat)
   - meta: `fb60812d` (docs) -- todo close
2. **Task 2: The alignment guard's full property matrix, at every page size the database actually carries**
   - firestarter_app: `6a65950` (test)
3. **Task 3: Criterion 4's regression surface, measured from the shipped database**
   - firestarter_app: `2acf5d3` (test)

**Plan metadata:** this SUMMARY commit, meta repo.

## Files Created/Modified

- `firestarter_app/firestarter/page_size_gate.py` -- `_ACCEPTED_PAGE_SIZES`, the widened `require_page_size` predicate, the new `_INVALID_PAGE_SIZE_FORMAT` message, docstring updates naming the shared ceiling
- `firestarter_app/tests/test_page_size_write_refusal.py` -- 7 new tests (3 rejected-class + 4 accepted-value), docstring's property list widened to 5
- `firestarter_app/tests/test_page_size_alignment_refusal.py` -- 25 new tests across the fail-closed, pass-through, empty-edge, no-op and dev-test-shape legs, docstring's property list widened to 9
- `firestarter_app/tests/test_validated_parts_regression_surface.py` -- new, 5 tests, reads `chip_database.json` directly and via `EpromDatabase(skip_local_override=True)`
- `.planning/todos/completed/host-page-size-gate-accepts-invalid-values.md` -- closed, moved from `pending/`, with a `## Closed` section

## Decisions Made

- **The pass-through matrix's parts are resolved at test-run time by reading the database**, not hard-coded: as of this database snapshot, page size 64 -> `AT29C256`, 128 -> `AE29F1008`, 256 -> `AE29F4008`, 512 -> `AT29BV040,AT29LV040` (first match per page size, in database iteration order). A future database regeneration that moves which part carries which page size cannot silently invalidate this leg, because the leg never names a part.
- **The dev-test region matrix is measured from raw JSON, not the wire-dict conversion**, so the 25/2 partition and the "both refused rows are page-size 512" fact are statements about the shipped artifact itself, independent of any host-side interpretation layer.
- **No second exception type.** The widened `require_page_size` still raises only `PageSizeUnavailableError`, distinguishing "absent" from "recorded but invalid" purely through message wording, per the plan's own instruction that a third exception type would need a third rendering arm for no behavioral gain.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocker, pre-existing/documented] `firestarter_app/tools/check_mypy_watermark.py`, named in every task's `<verify>` block, does not exist**
- **Found during:** Task 2's verify step
- **Issue:** The script was retired in a prior phase (per plan `195-01-SUMMARY.md`'s own "Issues Encountered", commit `0f251f0`, "retire the eight remaining check_*.py gates, the mypy CI step and the guard prose"). `firestarter_app/CLAUDE.md` confirms mypy now runs only via local `pre-commit`, strict on 8 named modules (`main.py`, `cli_handlers.py`, `chip_resolver.py`, `frame_parser.py`, `codec.py`, `address_parser.py`, `exceptions.py`, `serial_comm.py`), and is not a CI gate. None of the files this plan touches are in that strict list.
- **Fix:** Ran `mypy` directly against the one production file this plan modified (`page_size_gate.py`): `Success: no issues found in 1 source file`. Ran ruff check + ruff format --check (the two CI-enforced gates) and the planning-citation gate directly, all reporting clean, in place of the nonexistent watermark script.
- **Files modified:** none (verification-only substitution).
- **Verification:** `mypy firestarter/page_size_gate.py` clean; `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` both clean; `planning_citation_gate.py firestarter tests tools` reports `OK: 144 files scanned, no planning citations.`
- **Committed in:** no code change; recorded here as a verification-step substitution, matching the identical, already-documented deviation in `195-01-SUMMARY.md`.

---

**Total deviations:** 1 (Rule 3, verification-step substitution for a pre-existing retired gate script, already documented once in plan 01's SUMMARY and repeated here because every task's `<verify>` block in this plan also names the missing script).
**Impact on plan:** None on scope; the two CI-enforced lint gates and the planning-citation gate were run directly and are all clean, and mypy was additionally run directly (out of caution, not because CI requires it) against the one production file this plan touched.

## Issues Encountered

None beyond the pre-existing missing-script deviation documented above.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- Both refusal layers now agree on the accepted page-size set (D-05), the alignment guard's full property matrix is proven, and criterion 4 is a measured fact in code rather than a written claim (D-07, D-12).
- Per this plan's own prohibitions: `WRITE-01`, `WRITE-02` and `WRITE-03` are deliberately **NOT** marked Complete in `REQUIREMENTS.md` -- that is Plan 04's job once all software evidence exists (`WRITE-03` additionally waits for silicon).
- `firestarter/data/chip_database.json` and `firestarter/chip_test.py` are both unchanged, confirmed by `git status --porcelain` against both paths at every task boundary.
- `.planning/STATE.md` and `.planning/ROADMAP.md` were deliberately not touched -- the orchestrator owns those writes after the wave completes.
- The meta repo's gitlink for `firestarter_app` shows as modified (uncommitted) as an unavoidable side effect of committing inside the submodule; per the plan's own instruction, advancing that gitlink pointer is Plan 04's job, not this plan's.
- Plans 02 (firmware expansion matrix), 04 (documentation + gitlink advance + todos) and 05 (bench evidence) can proceed against this foundation; plan 02 is independent of this plan (both depend only on 195-01).

---
*Phase: 195-partial-writes-stop-destroying-the-page*
*Completed: 2026-09-16*

## Self-Check: PASSED

- All 4 key files confirmed present on disk with `[ -f ]`.
- All 4 production/test commits confirmed present via `git log --oneline --all` (firestarter_app `7569dd3`, `6a65950`, `2acf5d3`; meta `fb60812d`).
- All task-level `<acceptance_criteria>` re-run and passing: `_ACCEPTED_PAGE_SIZES` contains {64,128,256,512} and excludes {96,1024,65535}; `require_page_size` raises for {0,96,1024,65535} and passes for {64,128,256,512}; the recorded-but-invalid message names the value and never claims "no page size is recorded"; `test_page_size_write_refusal.py` reports 16 passed; `TODO-CLOSED` confirmed; `test_page_size_alignment_refusal.py` reports 29 passed; `MATRIX-OK` confirmed (14 references to `PageAlignmentError`, `assert_not_called` present, `chip_test.py` unchanged); `test_validated_parts_regression_surface.py` reports 5 passed; `SURFACE-OK` confirmed (`SST39SF020`, `AE29F2008`, `skip_local_override` all present, `chip_database.json` unchanged).
- Plan-level `<verification>` re-run: whole `firestarter_app` suite reports 1937 passed against a porcelain-clean tree; `ruff check` and `ruff format --check` both clean over `firestarter/` and `tests/`; planning-citation gate reports `OK: 144 files scanned, no planning citations.`; `git status --porcelain` empty in `firestarter_app` at time of this check.
