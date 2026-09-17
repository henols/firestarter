---
phase: 195-partial-writes-stop-destroying-the-page
plan: 01
subsystem: firmware-write-path
tags: [flash4, protocol-0x05, page-write, message-catalog, host-guard, native-tests]

requires:
  - phase: 194-real-page-size-reaches-the-firmware
    provides: "the resolved, database-sourced page size on both the wire dict and the firmware handle, and MSG_ERR_FL4_PAGE_SIZE at 0xBF as the last free ERROR id before this plan"
provides:
  - "MSG_ERR_FL4_PAGE_ALIGN at 0xC0, generated into both sub-repos, plus the ERROR-band-extension convention recorded in the catalog header"
  - "the firmware per-chunk alignment guard in flash_5v_page_write_execute, refusing before any register write"
  - "the host require_page_alignment predicate, wired into both the operator layer and the CLI pre-flight, with its own typed exception and rendering arm"
  - "a page-exact positive control at both layers, proving the guard is not a blanket refusal"
affects: [195-02, 195-03, 195-04, 195-05]

actuals:
  tokens: 6389
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Two-layer refusal (host pre-connect predicate + firmware per-chunk guard) for a protocol whose commit cannot be aborted once started"
    - "ERROR-severity message ids now mint from 0xC0 upward, with severity read from the explicit catalog field, never inferred from the numeric range"

key-files:
  created:
    - firestarter_app/tests/test_page_size_alignment_refusal.py
  modified:
    - tools/catalog/messages.toml
    - firestarter_fw/include/messages.h
    - firestarter_app/firestarter/messages.py
    - firestarter_fw/src/proms/flash_5v_page.cpp
    - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp
    - firestarter_app/firestarter/page_size_gate.py
    - firestarter_app/firestarter/exceptions.py
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_page_size_write_refusal.py
    - .planning/todos/completed/error-message-band-a0-bf-exhausted.md

key-decisions:
  - "D-09 kept: is_first_byte and is_last_byte clauses in flash_5v_page_write_execute stay, because the silicon commits the page on its own 200us after the last load -- deleting them would drop the SDP unlock and the verify poll, not the commit, turning a loud corruption into a silent one. Under the new guard both clauses are provably redundant (never wrong) for any chunk that passes."
  - "The alignment format string reads 'not page-aligned' / 'not a whole page' rather than reusing 0xBF's 'page size %u rejected' wording, so the two messages are never confusable -- 0xBF means no resolvable page size, 0xC0 means a resolvable page size that this chunk does not respect."
  - "require_page_alignment extends page_size_gate.py as a second public function rather than opening a sibling module (D-08), keeping _WRITE_OPERATIONS and FLASH4_PROTOCOL_ID single-sourced. The module docstring's purity claim is narrowed from 'no I/O' to 'no transport I/O' in the same edit, naming the one filesystem size probe and its fail-closed polarity."
  - "make_write_handle_with_data (native fixture) raised from a 4-byte partial-page write to a full 256-byte page (W29C040's real page size), because the new firmware guard would otherwise refuse it and turn two pre-existing green oracles (SDP emission, no-VPP) red. Both oracles were re-verified to still hold at the new size."
  - "Two pre-existing host-side tests in test_page_size_write_refusal.py broke as a direct consequence of adding the CLI/operator alignment call sites: both had used a filename ('in.bin') that never existed on disk, which the page-size-only guard never touched but the new alignment guard's os.path.getsize() probe does. Both were repaired to use a real, page-sized tmp_path file rather than weakened or skipped."

requirements-completed: []

coverage:
  - id: D1
    description: "MSG_ERR_FL4_PAGE_ALIGN minted at 0xC0 in the canonical catalog, both generated artefacts regenerated and proven idempotent, band-extension convention recorded, pending band todo closed"
    requirement: "WRITE-01"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_protection_status_catalog.py#test_error_band_fully_spent_0xa0_through_0xbf"
        status: pass
      - kind: other
        ref: "python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check"
        status: pass
    human_judgment: false
  - id: D2
    description: "Firmware refuses any protocol 0x05 chunk whose address or size is not a whole multiple of the page mask, before the first register write, with zero register writes on refusal and a page-exact positive control"
    requirement: "WRITE-01"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_refuses_unaligned_start"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_execute_accepts_page_exact_write"
        status: pass
    human_judgment: false
  - id: D3
    description: "Host refuses an unaligned or partial-page protocol 0x05 write before the port opens, from both the CLI pre-flight and the operator layer that also covers dev test, with a message naming the chip, page size, start address and length, rendered verbatim through the CLI"
    requirement: "WRITE-02"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_alignment_refusal.py#test_write_eprom_unaligned_start_refuses_before_operation_context"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_alignment_refusal.py#test_write_eprom_page_exact_write_reaches_operation_context"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_page_size_alignment_refusal.py#test_page_alignment_error_renders_through_cli_write_command"
        status: pass
    human_judgment: false

duration: 30min
completed: 2026-09-16
status: complete
---

# Phase 195 Plan 01: Tracer -- one unaligned protocol 0x05 write refused end to end Summary

**MSG_ERR_FL4_PAGE_ALIGN (0xC0) refuses an unaligned or partial-page protocol 0x05 write at both the host pre-connect layer and the firmware, while a page-exact write at a non-zero start still succeeds with exactly one SDP signature.**

## Performance

- **Duration:** 30 min
- **Started:** 2026-09-16T10:45:00Z (approx)
- **Completed:** 2026-09-16T11:12:00Z
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments
- `MSG_ERR_FL4_PAGE_ALIGN` minted at `0xC0` in `tools/catalog/messages.toml`, with a `u24 hex_addr` + `u16 dec` param pair, synced byte-for-byte into `firestarter_fw/include/messages.h` and `firestarter_app/firestarter/messages.py`, proven idempotent across two consecutive sync runs, and the ERROR-band-extension convention recorded in the catalog header.
- The pending `error-message-band-a0-bf-exhausted.md` todo closed in the same commit, naming the id it spent and the convention it established.
- Firmware `flash_5v_page_write_execute` refuses any chunk whose `address` or `data_size` is not a whole multiple of the resolved page mask, placed immediately after the existing page-mask refusal and before the byte loop, so a refused chunk drives zero register writes -- proven by an explicit `bus_recording_count() == 0` assertion, not by the absence of an expected id.
- A non-zero, page-aligned start (`address = 128`, `page_size = 128`) still succeeds with exactly one SDP signature, proving the guard is not a blanket refusal.
- Host `page_size_gate.require_page_alignment` refuses before the serial port opens, wired into both `eprom_operations.write_eprom` (which also covers `dev test`) and the CLI's write pre-flight, each immediately after the existing `require_page_size` call.
- `PageAlignmentError` gets its own `except` arm in `map_typed_errors`, above the generic `EpromOperationError` arm, so the chip-naming, page-size-naming message renders verbatim instead of behind a "Programmer error:" prefix.
- No override flag ships (D-03), per the plan's phase-level closure.

## Task Commits

Each task was committed atomically, across three repositories (`commits_land_in: [firestarter_fw, firestarter_app]`):

1. **Task 1: Mint the alignment refusal id at 0xC0, record the band convention, sync both sub-repos**
   - meta: `e74b7b33` (feat) -- catalog stanza + header convention + todo close
   - firestarter_fw: `43f98d0` (feat) -- regenerated `include/messages.h`
   - firestarter_app: `e86fc62` (feat) -- regenerated `firestarter/messages.py`
2. **Task 2: The firmware alignment guard, before the first register write, with one refusal case and one positive control**
   - firestarter_fw: `30a04d7` (feat)
3. **Task 3: The host pre-connect alignment refusal, wired into both layers and rendered verbatim**
   - firestarter_app: `64f6559` (feat)

**Plan metadata:** this SUMMARY commit, meta repo.

## Files Created/Modified
- `tools/catalog/messages.toml` -- new `0xC0` stanza + header convention line
- `firestarter_fw/include/messages.h` -- regenerated (do not hand-edit)
- `firestarter_app/firestarter/messages.py` -- regenerated, ruff-normalized (do not hand-edit)
- `firestarter_fw/src/proms/flash_5v_page.cpp` -- the per-chunk alignment guard
- `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` -- two new cases; `make_write_handle_with_data` repaired to a full page
- `firestarter_app/firestarter/page_size_gate.py` -- `require_page_alignment`, docstring purity claim narrowed
- `firestarter_app/firestarter/exceptions.py` -- `PageAlignmentError`
- `firestarter_app/firestarter/cli_handlers.py` -- CLI pre-flight call + rendering arm
- `firestarter_app/firestarter/eprom_operations.py` -- operator-layer call
- `firestarter_app/tests/test_page_size_alignment_refusal.py` -- new, 4 tests
- `firestarter_app/tests/test_page_size_write_refusal.py` -- two tests repaired (see Deviations)
- `.planning/todos/completed/error-message-band-a0-bf-exhausted.md` -- closed, moved from `pending/`

## Flash deltas (recorded per plan's `<output>` instruction)

| Environment | Before (baseline, this branch) | After | Delta |
|---|---|---|---|
| uno | 21616 B | 21680 B | +64 B |
| leonardo | 23734 B | 23798 B | +64 B |

Both from a build that actually relinked (`bootloader-guard` line printed for each): `uno 21680/32256 B (67.2%, 10576 B margin)`, `leonardo 23798/28672 B (83.0%, 4874 B margin)`.

## Decisions Made

- **D-09 kept, not removed.** `is_first_byte` / `is_last_byte` in `flash_5v_page_write_execute` stay exactly as they were. Under the new guard they are provably redundant for any chunk that passes (a page-aligned address makes `is_page_start` true at `i==0`; a page-aligned size makes `reached_page_end` true at the final byte) -- but the silicon commits the page on its own 200 microseconds after the last load regardless of firmware behavior, so deleting the clauses would remove the SDP unlock and the verify poll, not the commit, converting a loud corruption into a silent one.
- **Message wording chosen to avoid confusion with 0xBF.** `MSG_ERR_FL4_PAGE_ALIGN`'s format is `"Write refused -- address 0x%06lx not page-aligned or length %u not a whole page"` -- deliberately not using the phrase "page size", which `MSG_ERR_FL4_PAGE_SIZE` (0xBF) already owns for "no resolvable page size at all". The host-side equivalent, `_ALIGNMENT_REFUSAL_FORMAT`, states the page size, the start address (hex), and the payload length (decimal) so the operator can see which clause fired.
- **`make_write_handle_with_data` repaired from 4 bytes to 256 bytes** (one whole page at W29C040's real page size), because the new guard refuses a 4-byte write against a 256-byte page and would have turned `test_5v_page_write_execute_emits_sdp` and `test_5v_page_write_execute_no_vpp` red. Both oracles (exactly one SDP signature; no VPP bit in any control-register write) were re-verified to hold unchanged at the new size. The helper's now-falsified leading comment ("4-byte zero data buffer") and the field's trailing comment ("small: 4 zero bytes at page 0") were deleted with no replacement, per the hard no-comments rule; a stale comment inside the surrounding block doc-comment that also named "data_size=4" was likewise deleted with no replacement. Two `TEST_ASSERT_*_MESSAGE` assertion-failure strings that said "4-byte zero write" were updated to "a full-page zero write" -- these are runtime assertion messages, not comments, so updating stale prose in them is not covered by the no-comments prohibition.
- **`require_page_alignment` extends `page_size_gate.py`** rather than opening a sibling module (D-08), keeping `_WRITE_OPERATIONS` and `FLASH4_PROTOCOL_ID` single-sourced. The module docstring's "no I/O" purity claim is narrowed to "no transport I/O", naming the one filesystem size probe (`os.path.getsize`) and stating it fails closed like everything else in the module.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Two pre-existing tests in `test_page_size_write_refusal.py` broke as a direct consequence of this plan's new call sites**
- **Found during:** Task 3, after wiring `require_page_alignment` into `eprom_operations.write_eprom` and `cli_handlers.write`
- **Issue:** `test_write_eprom_with_page_size_reaches_operation_context` and `test_page_size_unavailable_renders_through_cli_write_command` both passed the literal filename `"in.bin"`, which never exists on disk in the test process. The pre-existing `require_page_size` guard never touches the filesystem, so this was invisible before this plan. The new `require_page_alignment` call performs `os.path.getsize(input_file_path)` at the same call sites and raised `FileNotFoundError` -> `PageAlignmentError` before the tests' own mocked exception could fire, changing both tests' outcome.
- **Fix:** Both tests now write a real, page-sized file to a `tmp_path` fixture (or, for the CLI test, an isolated `tmp_path` file passed as an absolute path) before invoking `write_eprom` / the CLI command, so the alignment guard passes and the originally-intended code path (the page-size guard, or the mocked exception) is what actually fires.
- **Files modified:** `firestarter_app/tests/test_page_size_write_refusal.py`
- **Verification:** `pytest tests/test_page_size_write_refusal.py tests/test_page_size_alignment_refusal.py` -- 13 passed, 0 warnings.
- **Committed in:** `64f6559` (Task 3 commit)

**2. [Rule 1 - Bug, self-inflicted] My own new CLI-rendering test in `test_page_size_alignment_refusal.py` had the identical bug on first write**
- **Found during:** Task 3, immediately after writing the new test module
- **Issue:** `test_page_alignment_error_renders_through_cli_write_command` invoked the CLI with a nonexistent `"in.bin"` and a mocked `write_eprom` side effect; the real CLI-layer `require_page_alignment` call fired first (file-not-found), producing a different message than the test asserted.
- **Fix:** Rewrote the test to write a real 64-byte file to `tmp_path` and pass `-a 0x40`, so the CLI's own real alignment guard produces exactly the message under test (start `0x40` against a 64-byte file on a 128-byte page is genuinely unaligned) -- the assertion no longer depends on which layer raises, both are consistent.
- **Files modified:** `firestarter_app/tests/test_page_size_alignment_refusal.py`
- **Verification:** included in the 13-passed run above.
- **Committed in:** `64f6559` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 -- bugs surfaced by this plan's own new filesystem-touching guard against tests that assumed a filename never needs to exist).
**Impact on plan:** Both fixes were necessary to keep the pre-existing and new test suites green; no scope creep beyond the two affected test functions.

## Issues Encountered

- `firestarter_app/tools/check_mypy_watermark.py`, named in the plan's Task 3 verify block, no longer exists -- it was retired in a prior phase (commit `0f251f0`, "retire the eight remaining check_*.py gates, the mypy CI step and the guard prose"). `CLAUDE.md` confirms mypy now runs only via local `pre-commit`, strict on 8 named modules, and is not a CI gate. Ran `mypy` directly against the strict-checked files touched by this plan (`exceptions.py`, `cli_handlers.py`) instead: one pre-existing, unrelated error in `submit.py` (confirmed present on a clean stash of this plan's changes too), zero new errors introduced by this plan.
- `ruff check` found one pre-existing import-order issue in the edited `page_size_gate.py` (from adding the `os` and `address_parser` imports); fixed with `ruff check --fix` + `ruff format`, both now clean.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The tracer slice is proven end to end: catalog id, firmware guard, host predicate, typed exception, rendering arm, and both test trees all exercise the same refusal and the same non-vacuous positive control.
- Plans 02 (firmware expansion matrix), 03 (host page-size validity + full alignment matrix), 04 (documentation + gitlink advance + todos), and 05 (bench evidence) can proceed against this foundation.
- Per plan's own prohibitions: `WRITE-01`, `WRITE-02`, and `WRITE-03` are deliberately NOT marked Complete in `REQUIREMENTS.md` -- that is Plan 04's job once all software evidence exists (and `WRITE-03` additionally waits for silicon).
- `.planning/STATE.md` and `.planning/ROADMAP.md` were deliberately not touched -- the orchestrator owns those writes after the wave completes.
- The meta repo's gitlinks for `firestarter_fw` and `firestarter_app` show as modified (uncommitted) as an unavoidable side effect of committing inside both submodules; per the plan's own instruction, advancing those gitlink pointers is Plan 04's job, not this plan's.

---
*Phase: 195-partial-writes-stop-destroying-the-page*
*Completed: 2026-09-16*

## Self-Check: PASSED

- All 11 key files confirmed present on disk with `[ -f ]`.
- All 5 production commits confirmed present via `git log --oneline --all` in their respective repos (meta `e74b7b33`; firestarter_fw `43f98d0`, `30a04d7`; firestarter_app `e86fc62`, `64f6559`).
- All task-level `<acceptance_criteria>` re-run and passing (CATALOG-VALID, SYNC-NORMALIZED, SYNC-PRESENT, SYNC-IDEMPOTENT, TODO-CLOSED; GUARD-BEFORE-LOOP, SHAPE-OK, HELPER-REPAIRED, 2/2 RUN_TEST registrations; ALIGN-OK, PURE-OK, WIRING-OK).
- Plan-level `<verification>` re-run: codegen check exits 0; `MSG_ERR_FL4_PAGE_ALIGN` is `0xC0` in both generated artefacts; second sync leaves both files clean; band todo closed under `completed/` naming `0xC0`; firmware guard precedes the loop with both redundant clauses intact; `pio test -e native` and `-e native_nodevtools` both report 210/210; both AVR builds succeed with `bootloader-guard` lines and recorded deltas; `test_page_size_alignment_refusal.py` reports 4/4 passing; whole app suite reports 1900 passed against a porcelain-clean tree in both sub-repos; both planning-citation gates report `OK:` with file counts.
