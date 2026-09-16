---
phase: 195-partial-writes-stop-destroying-the-page
plan: 02
subsystem: firmware-write-path
tags: [flash4, protocol-0x05, page-write, native-tests, chunk-boundary]

requires:
  - phase: 195-partial-writes-stop-destroying-the-page
    provides: "MSG_ERR_FL4_PAGE_ALIGN at 0xC0 and the firmware per-chunk alignment guard in flash_5v_page_write_execute, landed by plan 01"
provides:
  - "The full native rejection matrix: partial length alone, both start+length clauses together, and a single-byte payload -- each its own case with its own zero-writes assertion"
  - "Both directions of the WRITE-01 empty edge: a zero-length chunk accepted with zero register writes, a single byte refused"
  - "The interior chunk-boundary loss direction (D-06) modelled end to end and refused, with no memory of the first chunk's history needed"
  - "Aligned multi-chunk ordering proof at P=256 and P=512, each opening exactly one page per whole page spanned"
  - "The guard's measured flash and RAM cost on both AVR environments, from builds that actually relinked"
affects: [195-03, 195-04, 195-05]

actuals:
  tokens: 2313
  tasks: 3
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Repeated-call chunk-boundary drive pattern (established by the pre-existing test_5v_page_write_execute_boundary_524288_512) reused to model the interior page-loss direction -- reassign address and data_size between two firestarter_operation_main calls on one handle, exactly as the real chunked host path does"
    - "Every refusal case asserts an explicit RESPONSE_CODE_ERROR plus a zero bus_recording_count(), never inferred from the absence of an expected id"
    - "Every boundary/ordering positive control asserts bus_recording_saturated() is false before asserting a signature count, so a saturated recorder cannot let the count pass vacuously"

key-files:
  modified:
    - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp

key-decisions:
  - "Task 3 shipped zero source changes, as its own <files> note and the plan's prohibition require -- the guard landed in plan 01, and this plan only measures and covers it. Both AVR builds were force-relinked (build dirs removed and rebuilt) after the first `pio run -e uno` produced no bootloader-guard line, confirming the initial run had short-circuited on a cached ELF rather than actually relinking."
  - "Flash and RAM figures on both environments are identical to plan 01's recorded figures (uno 21680/32256, leonardo 23798/28672; RAM 1394/1835 unchanged) -- expected, since this plan added no firmware source, only native test cases, and RAM moving at all would have meant a staging buffer crept in against D-01."
  - "test_5v_page_write_execute_refuses_unaligned_second_chunk resets response_code to RESPONSE_CODE_OK and clears the recording between its two calls, but does not reconstruct the handle -- the second call's address (0x40 + 512 = 0x240) is still unaligned to page_size 128 purely as a consequence of the first chunk's length, not because the test hand-picked an unaligned value, which is the point of the case."
  - "The two aligned multi-chunk positive controls (P=256, P=512) clear the bus recording between calls and assert the signature count only after the second call, so the asserted count (2 for P=256, 1 for P=512) reflects only the second 512-byte chunk's own page starts -- consistent with 'one page start per whole page spanned' at each geometry."

requirements-completed: []
# WRITE-01 is a shared requirement ID across plans 01-05 of this phase and is deliberately left
# unchecked in REQUIREMENTS.md until plan 04, per plan 01's own recorded precedent -- this plan's
# evidence is necessary but not sufficient on its own (bench evidence and documentation remain).

coverage:
  - id: D1
    description: "Three independent refusal cases -- partial length alone, unaligned start plus partial length together, and a single-byte payload -- each asserting RESPONSE_CODE_ERROR and zero register writes, so no single case stands in for the family and a guard written with && instead of || cannot survive"
    requirement: "WRITE-01"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_refuses_partial_length"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_refuses_unaligned_start_and_partial_length"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_refuses_single_byte_payload"
        status: pass
    human_judgment: false
  - id: D2
    description: "The WRITE-01 empty edge, zero-length direction: a data_size-zero chunk is accepted (RESPONSE_CODE_OK) and drives zero register writes -- refusing it would regress existing empty-input behaviour, and committing a page for it would be the defect"
    requirement: "WRITE-01"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_accepts_zero_length_chunk"
        status: pass
    human_judgment: false
  - id: D3
    description: "The interior chunk-boundary loss direction (D-06) modelled by driving the handler twice with an advancing address: the second chunk is unaligned only because the first ended mid-page, and the guard refuses it on its own terms with no memory of the first chunk's history"
    requirement: "WRITE-01"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_refuses_unaligned_second_chunk"
        status: pass
    human_judgment: false
  - id: D4
    description: "Aligned two-chunk writes at P=256 and P=512 both succeed and open exactly one page per whole page spanned in the second chunk, proving the chunk boundary itself never causes a double-open or double-commit under a fix that respects it"
    requirement: "WRITE-01"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_accepts_aligned_two_chunk_p256"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_accepts_aligned_two_chunk_p512"
        status: pass
    human_judgment: false
  - id: D5
    description: "The guard's flash cost is measured on both AVR environments from builds that actually relinked (bootloader-guard line printed), and its RAM cost is proven to be exactly zero against the pre-guard baseline"
    requirement: "WRITE-01"
    verification:
      - kind: other
        ref: "pio run -e uno && pio run -e leonardo (bootloader-guard: uno 21680/32256 B, leonardo 23798/28672 B; RAM 1394/2048 uno, 1835/2560 leonardo)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-09-16
status: complete
---

# Phase 195 Plan 02: The rejection matrix, the chunk-boundary loss, and the measured guard cost Summary

**Seven new native cases expand the plan-01 tracer into the full partial-write rejection matrix, model the interior chunk-boundary loss direction end to end, and pin an aligned multi-chunk write at both P=256 and P=512 -- with the guard's flash/RAM cost measured from a relinked build rather than assumed.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-09-16T11:00:00Z (approx)
- **Completed:** 2026-09-16T11:25:03Z
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments
- `test_val_5v_page.cpp` gains four rejection-matrix cases (`refuses_partial_length`, `refuses_unaligned_start_and_partial_length`, `refuses_single_byte_payload`, `accepts_zero_length_chunk`), each proving an independent refusal class or edge with its own explicit `RESPONSE_CODE_ERROR`/`RESPONSE_CODE_OK` plus zero-register-writes assertion.
- Three multi-chunk cases (`refuses_unaligned_second_chunk`, `accepts_aligned_two_chunk_p256`, `accepts_aligned_two_chunk_p512`) drive `firestarter_operation_main` twice per handle with an advancing address, modelling the real chunked host path. The interior loss direction (D-06) is refused without the guard needing any memory of the prior chunk's history; the two aligned controls prove each page opens exactly once across the boundary at both 256- and 512-byte page geometries.
- `pio test -e native` and `pio test -e native_nodevtools` both report 217 total cases succeeded (up from 210 before this plan).
- Both AVR builds forced to relink (`bootloader-guard` line printed for each): `uno 21680/32256 B (67.2%, 10576 B margin)`, `leonardo 23798/28672 B (83.0%, 4874 B margin)` -- identical to plan 01's recorded figures, since this plan shipped zero firmware source changes.
- RAM confirmed unchanged: `uno 1394/2048 B`, `leonardo 1835/2560 B` -- the mechanical proof that no staging buffer was allocated against D-01.
- `firestarter_fw`'s pytest suite (`tests/`) reports exactly the pre-existing 17 failures in `test_flash_path_record_sync.py` (Phase 194's dispositioned relocated-planning-path issue) and 284 passed -- no new regressions.
- The two host test modules that scan firmware source paths (`test_page_size_invariants.py`, `test_py32_flash_map_host.py` in `firestarter_app`) both pass with a non-zero count (20 tests), confirmed to have scanned something rather than merely passed.

## Task Commits

Each task was committed atomically, inside `firestarter_fw` on `v1.39-protocol-0x05-write-correctness`:

1. **Task 1: The rejection matrix -- partial length, both clauses, and the two empty-edge cases** - `a8a0ecf` (test)
2. **Task 2: The multi-chunk cases -- the interior loss direction, and aligned continuation at P=256 and P=512** - `b32d1ad` (test)
3. **Task 3: Measure what the guard cost, and re-run every gate that reads firmware source** - no commit (no tracked file edited; builds and measurements only, recorded above and in this SUMMARY)

**Plan metadata:** this SUMMARY commit, meta repo.

## Files Created/Modified
- `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` -- seven new cases: four single-chunk rejection-matrix/edge cases (Task 1), three multi-chunk cases modelling the interior loss direction and aligned continuation at P=256/P=512 (Task 2)

## Decisions Made

- **Task 3 confirmed the flash figures by forcing an actual relink.** The first `pio run -e uno` after this plan's test-only commits produced no `bootloader-guard` line -- proof the build had short-circuited on a cached ELF rather than relinking. Per the task's own instruction, `.pio/build/uno` and `.pio/build/leonardo` were removed by explicit path (never a recursive ignored-file clean) and both environments rebuilt from scratch, after which both printed their guard line.
- **Flash and RAM are byte-identical to plan 01's recorded figures.** This plan adds only native test source under `test/`, which PlatformIO's AVR environments do not compile into the firmware image -- so the +64 B delta on each environment (against the 21616/23734 pre-Phase-195 baselines) is entirely plan 01's guard, and this plan's own contribution to the shipped image is zero, as its prohibitions require.
- **The chunk-boundary loss case reuses the same handle across two calls without reconstructing it**, so the second call's unaligned address (`0x40 + 512 = 0x240`, still not a multiple of 128) arises purely from the first chunk's length rather than being hand-picked -- this is what makes the case a faithful model of the real loss direction rather than a second, independent unaligned-start case.
- **The two aligned multi-chunk controls clear the bus recording between calls** and assert the SDP signature count only after the second call, so the asserted counts (2 at P=256, 1 at P=512) describe the second 512-byte chunk's own page opens -- consistent with "one page start per whole page spanned in that chunk" at each geometry, and matching the shape of the pre-existing `boundary_524288_512` case this plan's Task 2 sits beside.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' acceptance criteria and the plan-level `<verification>` block were satisfied on the first pass; no auto-fixes, no architectural questions, no scope changes.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The native rejection matrix is now complete for this phase's software evidence: every rejected class (no page size, unaligned start, partial length, both together, single byte, interior chunk-boundary loss) has its own case, and every accepted class (page-exact, zero-length, aligned multi-chunk at P=256 and P=512) has its own non-vacuous positive control.
- Plan 03 (host page-size validity + full alignment matrix) and plan 04 (documentation + gitlink advance + todos, including marking WRITE-01/02/03 in REQUIREMENTS.md once all software evidence exists) can proceed against this foundation.
- Plan 05's bench evidence (W29C020 on the Leonardo rig, including the loss-reproduction leg on a reverted firmware build) is unaffected by anything in this plan -- no firmware source changed.
- `.planning/STATE.md` and `.planning/ROADMAP.md` were deliberately not touched -- the orchestrator owns those writes after the wave completes.
- `WRITE-01` is deliberately left unchecked in `REQUIREMENTS.md`, per plan 01's own recorded precedent -- that is plan 04's job once all software evidence (plans 02, 03) and bench evidence (plan 05) exist.

---
*Phase: 195-partial-writes-stop-destroying-the-page*
*Completed: 2026-09-16*

## Self-Check: PASSED

- Key file confirmed present on disk: `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (`[ -f ]` true).
- Both production commits confirmed present via `git log --oneline --all` in `firestarter_fw`: `a8a0ecf`, `b32d1ad`.
- All task-level `<acceptance_criteria>` re-run and passing: MATRIX-REGISTERED (Task 1), MULTICHUNK-REGISTERED (Task 2), all listed criteria for Task 3 (bootloader-guard lines present, flash/RAM figures matched, guard scripts exit 0, citation gate `OK:` with file count, host modules non-zero pass count, `pytest tests/` failures confined to the dispositioned module with 284 passed, porcelain clean).
- Plan-level `<verification>` re-run: `pio test -e native` and `-e native_nodevtools` both report 217/217; both AVR builds print `bootloader-guard` lines with the recorded deltas; RAM unchanged at 1394/1835; leonardo flash (23798) below its 28672 ceiling; `check_cmake_manifest.py` and `check_erase_no_vpp.py` both PASS; citation gate reports `OK: 177 files scanned, no planning citations`; `test_page_size_invariants.py` + `test_py32_flash_map_host.py` report 20 passed; `pytest tests/` in `firestarter_fw` reports 17 failed (all in `test_flash_path_record_sync.py`) and 284 passed; `git status --porcelain` empty in `firestarter_fw`.
