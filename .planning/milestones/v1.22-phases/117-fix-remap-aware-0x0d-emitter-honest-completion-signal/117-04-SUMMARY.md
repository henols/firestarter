---
phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
plan: 04
subsystem: firmware
tags: [platformio, unity, native-test, avr, sdp, at28c, eeprom28c, terminal-byte-guard]

# Dependency graph
requires:
  - phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal
    provides: "plan 117-02's external linkage grant on EEPROM_SDP_DISABLE (extern const byte_flip_t EEPROM_SDP_DISABLE[6]; in eeprom_28c.cpp), the seam this guard reads through"
provides:
  - "FIX-05: a permanent constant-level guard in the always-green test_sdp_harness suite pinning EEPROM_SDP_DISABLE's terminal byte to 0x20 and FLASH_ERASE's to 0x10, asserting the two tables are distinct objects differing at exactly one element's byte, and cross-guarding EEPROM_SDP_DISABLE against byte-identity with FLASH_DISABLE_WRITE_PROTECTION (D-10/D-11)"
  - "A planted-violation counterpart (test_fix05_guard_rejects_planted_terminal_mutation) proving the comparator can actually fail, reusing the existing TEST_UNLOCK_MUTATED_TERMINAL fixture rather than adding a second copy"
  - "sdp_tables_identical(const byte_flip_t*, const byte_flip_t*, size_t) -- a reusable positional table-comparison helper"
  - "Three stale-comment corrections (file header, TEST_UNLOCK_MUTATED_TERMINAL provenance, mock_get_data_keyed's 0x5555 arm) removing claims plan 117-02/117-03 invalidated"
affects: [117-05-close-frozen-artifact-proof]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Constant-level table guard as the sibling of a stream-level trace negative: sdp_tables_identical() proves the same one-nibble hazard test_negativeA_unlock_mutated_diverges_and_matches_erase proves at the strobe-stream level, but directly on the source tables, no bus drive required."
    - "Anti-hollow counterpart reuses an existing planted-fault fixture (TEST_UNLOCK_MUTATED_TERMINAL) rather than duplicating it -- one planted table, two consumers (the pre-existing stream negative and the new constant guard)."

key-files:
  created: []
  modified:
    - firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp

key-decisions:
  - "Followed 117-CONTEXT.md D-10/D-11 and the plan's own discretion resolutions (guard home = test_sdp_harness, guard reads the production array via extern, planted-violation counterpart reuses TEST_UNLOCK_MUTATED_TERMINAL) exactly as specified -- no deviation from the locked design."
  - "Reworded two in-code comment mentions of the two new test-case names (in the TEST_UNLOCK_MUTATED_TERMINAL provenance block and inside test_fix05_guard_rejects_planted_terminal_mutation's own assertion message) that would otherwise have collided with the acceptance criteria's literal grep requiring each name to appear exactly twice (definition + RUN_TEST) -- meaning preserved (both comments still name FIX-05/D-11 and explain what breaks), the literal function-name substring avoided, matching this project's established pattern (117-02-SUMMARY.md's identical class of adjustment for rurp_set_data_output/eeprom28c_wait_for_write greps)."

requirements-completed: [FIX-05]

coverage:
  - id: D1
    description: "A native test pins EEPROM_SDP_DISABLE's terminal byte to 0x20 and FLASH_ERASE's to 0x10, reading the production array (extern, plan 117-02) rather than a transcribed copy, and asserts the two tables are distinct objects differing at exactly one index"
    requirement: FIX-05
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp test_fix05_terminal_byte_and_table_identity_guards via `pio test -e native -f \"*test_sdp_harness*\"`"
        status: pass
    human_judgment: false
  - id: D2
    description: "EEPROM_SDP_DISABLE is asserted byte-identical to FLASH_DISABLE_WRITE_PROTECTION (D-11's cross-guard), and a planted-violation counterpart proves the comparator can actually fail"
    requirement: FIX-05
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp test_fix05_terminal_byte_and_table_identity_guards (clause 6) and test_fix05_guard_rejects_planted_terminal_mutation via `pio test -e native -f \"*test_sdp_harness*\"`"
        status: pass
    human_judgment: false
  - id: D3
    description: "The anti-hollow proof was actually executed: temporarily mutating the production EEPROM_SDP_DISABLE terminal byte to the chip-erase value drives the constant-level guard RED; restoring it returns the suite to 15/15 GREEN"
    verification:
      - kind: manual_procedural
        ref: "See '## Planted-violation proof (production terminal byte mutated)' below -- verbatim captured RED output, followed by restoration and re-verified GREEN + clean git diff over src/"
        status: pass
    human_judgment: false
  - id: D4
    description: "FIX-04 frozen artifacts stay byte-untouched; full native suite green; both board targets build; this plan's diff is confined to the one test file named in files_modified"
    verification:
      - kind: unit
        ref: "git diff --stat ada4bdc..HEAD over the 6 frozen paths (empty); pio test -e native (108/108, 16 suites); pio run -e uno / -e leonardo (both SUCCESS, unchanged flash/RAM figures); git show --stat --name-only HEAD lists exactly one file"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-07-28
status: complete
---

# Phase 117 Plan 04: FIX-05 Terminal-Byte + Table-Identity Guards Summary

**Added a permanent, executed constant-level guard in the always-green `test_sdp_harness` suite that pins the production `EEPROM_SDP_DISABLE` table's terminal byte to `0x20`, distinguishes it from the chip-erase `FLASH_ERASE` table (`…0x10`), and cross-checks it byte-identical to `FLASH_DISABLE_WRITE_PROTECTION` — with a planted-violation counterpart proving the guard actually bites.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-28T10:20:00Z
- **Completed:** 2026-07-28T10:45:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- `test_sdp_harness.cpp` now declares `extern const byte_flip_t EEPROM_SDP_DISABLE[6];` — the production array defined in `src/proms/eeprom_28c.cpp` and granted external linkage by plan 117-02 — so this guard reads the real table `[env:native]` links into the test binary, not a transcription.
- New file-static `sdp_tables_identical(const byte_flip_t* a, const byte_flip_t* b, size_t len)`: positional (never counting) element-by-element comparison of both `address` and `byte`.
- New `test_fix05_terminal_byte_and_table_identity_guards`: (1) length-sanity on all three tables (6 elements each); (2)/(3) pins `EEPROM_SDP_DISABLE[5]` = `(0x5555, 0x20)` and `FLASH_ERASE[5]` = `(0x5555, 0x10)`; (4) asserts the terminal bytes differ AND the two arrays are distinct objects (pointer inequality); (5) the one-nibble claim made literal — elements 0-4 match on both fields, element 5's address matches while its byte differs; (6) D-11's cross-guard — `EEPROM_SDP_DISABLE` byte-identical to `FLASH_DISABLE_WRITE_PROTECTION`, the table every `SDP_FIXED_*` golden and reference-emitter guard in this suite is driven from.
- New `test_fix05_guard_rejects_planted_terminal_mutation`: reuses the existing `TEST_UNLOCK_MUTATED_TERMINAL` fixture (no second planted table added) to prove `sdp_tables_identical` returns `false` when it should, and that the planted one-nibble slip's element-5 byte equals `FLASH_ERASE`'s — the constant-level twin of `test_negativeA_unlock_mutated_diverges_and_matches_erase`'s stream-level proof.
- Both cases registered in `main()`, taking the file from 13 to 15 `RUN_TEST` lines.
- Three stale comments corrected: the file header's claim that the suite "never drives `eeprom28c_write_init`" (contradicted by its own Task 3 migrated-identity cases); `TEST_UNLOCK_MUTATED_TERMINAL`'s provenance block, which described `EEPROM_SDP_DISABLE` as having internal linkage (invalidated by plan 117-02) and now names the fixture's dual role; `mock_get_data_keyed`'s `addr == 0x5555` arm, which described the deleted inverted `(0x5555, 0x20)` equality check and now describes the current bounded DQ6 toggle-bit poll (D-05: a constant return reads as "settled immediately" and the fixed code draws no conclusion from that).
- `pio test -e native -f "*test_sdp_harness*"`: **15/15 passing** (13 pre-existing + 2 new). Full `pio test -e native`: **108/108 passing** (16 suites — up from 106 at plan start, exactly the +2 this plan adds). `test_eeprom28c_sdp`: still 8/8. `test_val_eeprom28c`: still 6/6. Both `pio run -e uno` and `pio run -e leonardo` report `SUCCESS` with unchanged flash/RAM figures (this plan is test-only; board builds don't even compile the changed file).
- `git diff --stat ada4bdc..HEAD` over all 6 FIX-04 frozen paths (`flash_utils.{cpp,h}`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp`, `_shared/sdp_expected.h`, `_shared/sdp_bus_config.h`): empty. `git show --stat --name-only HEAD` lists exactly `test/native/avr/test_sdp_harness/test_sdp_harness.cpp`.

## Task Commits

1. **Task 1: FIX-05 constant-level guard + planted-violation counterpart** — `353ce8a` (test, firestarter submodule)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md/REQUIREMENTS.md update, in the meta repo (separate commit, see `<final_commit>`).

_Note: this is a firmware-submodule-only plan; the meta repo's docs commit is separate._

## Files Created/Modified
- `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp` — Added the `extern const byte_flip_t EEPROM_SDP_DISABLE[6];` declaration (outside any `extern "C"` block, after the `flash_utils.h` include); added `sdp_tables_identical()`; added `test_fix05_terminal_byte_and_table_identity_guards` and `test_fix05_guard_rejects_planted_terminal_mutation`; registered both in `main()`; corrected three stale comments (file header, `TEST_UNLOCK_MUTATED_TERMINAL` provenance, `mock_get_data_keyed`'s `0x5555` arm). No existing assertion, expected array, drive helper, handle factory, or case name changed — append-only plus targeted comment corrections.

## Decisions Made
- Followed 117-CONTEXT.md's D-10/D-11 and the plan's own discretion resolutions exactly: guard lives in `test_sdp_harness` (not `test_eeprom28c_sdp`), reads the production array via `extern` rather than a transcription, and the planted-violation counterpart reuses `TEST_UNLOCK_MUTATED_TERMINAL` rather than adding a second copy.
- Reworded two in-code comment mentions of the two new test-case names (once in the `TEST_UNLOCK_MUTATED_TERMINAL` provenance block, once inside `test_fix05_guard_rejects_planted_terminal_mutation`'s own assertion message) to avoid a third literal occurrence, since the plan's own acceptance criteria require each new case name to appear **exactly twice** (definition + `RUN_TEST`) in a non-comment-filtered grep. Meaning fully preserved in both spots — both still cite FIX-05/D-11 and explain what a failure would mean; only the literal function-name substring was avoided. This mirrors the same class of adjustment plan 117-02 made for its own literal-substring acceptance gates (see `117-02-SUMMARY.md`'s "Decisions Made").

## Deviations from Plan

None affecting behavior — plan executed exactly as specified. The one comment-wording adjustment above is cosmetic (Rule 3, blocking: the literal acceptance-criteria greps would otherwise fail on the plan's own cross-referencing comments, not on the guard's actual shape) and does not change any assertion, constant value, table, or control flow.

## Issues Encountered

None. The single automated verify gate and every acceptance criterion passed; the suite went 15/15 GREEN on the first `pio test` run after the edits (no debugging iteration needed). The pre-existing uncommitted `firestarter_app/.gitignore` diff noted in `117-02-SUMMARY.md` (dated well before this session) is still present and still out of scope — this plan touched zero `firestarter_app` files.

## Planted-violation proof (production terminal byte mutated)

Per the plan's mandatory anti-hollow proof, the production `EEPROM_SDP_DISABLE` table's terminal byte in `src/proms/eeprom_28c.cpp` was temporarily changed from `0x20` (SDP-disable) to `0x10` (chip-erase), the suite was re-run, the RED output below was captured verbatim, the file was restored, and the suite was re-run to confirm 15/15 GREEN — all before this plan's commit. `git diff --exit-code -- src/` was confirmed clean immediately before committing.

**Step 1 — mutation applied** (`{0x5555, 0x20}` → `{0x5555, 0x10}` at `eeprom_28c.cpp:108`, marked `/* TEMPORARY anti-hollow proof mutation -- 117-04, do not commit */`):

```
$ pio test -e native -f "*test_sdp_harness*"
...
Testing...
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:544: test_case1_ordered_capture_dip28_28c256	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:545: test_case2_elision_is_real	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:546: test_case3_ce_oe_edges_distinguishable	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:549: test_negativeA_unlock_mutated_diverges_and_matches_erase	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:550: test_negativeB_lock_table_swapped_for_write_prefix	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:551: test_lock05_enable_write_and_write_protection_identical	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:332: test_fix05_terminal_byte_and_table_identity_guards: Expected 0x20 Was 0x10. FIX-05: EEPROM_SDP_DISABLE's terminal byte must be 0x20 (SDP-disable) -- if this fails, the production 0x0D write path may now emit a chip-erase command	[FAILED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:394: test_fix05_guard_rejects_planted_terminal_mutation: FIX-05 anti-hollow: sdp_tables_identical must REJECT the planted terminal-byte mutation -- if this passes, the constant-level guard's D-11 cross-check clause is hollow	[FAILED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:554: test_fixed_guard_at28c256	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:555: test_fixed_guard_at28c64	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:556: test_fixed_guard_at28c16	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:557: test_fixed_guard_at28c010	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:558: test_fixed_guard_at28c040	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:561: test_migrated_mismatching_chip_id_errors	[PASSED]
test/native/avr/test_sdp_harness/test_sdp_harness.cpp:562: test_migrated_zero_chip_id_skips_check	[PASSED]
-------- native:native/avr/test_sdp_harness [ERRORED] Took 1.38 seconds --------

=================================== SUMMARY ===================================
Environment    Test                         Status    Duration
-------------  ---------------------------  --------  ------------
native         native/avr/test_sdp_harness  ERRORED   00:00:01.378

============ 16 test cases: 2 failed, 13 succeeded in 00:00:01.378 ============
```

**Both new cases went RED as expected.** `test_fix05_terminal_byte_and_table_identity_guards` failed on its own clause (2) — the direct terminal-byte pin — before ever reaching clause (6)'s cross-guard, exactly the failure mode the guard exists to catch. `test_fix05_guard_rejects_planted_terminal_mutation` **also** failed, for a code-as-subject reason worth recording: the mutation made the production `EEPROM_SDP_DISABLE` byte-for-byte identical to the planted `TEST_UNLOCK_MUTATED_TERMINAL` fixture (both now terminate `…0x10`), so `sdp_tables_identical(TEST_UNLOCK_MUTATED_TERMINAL, EEPROM_SDP_DISABLE, 6)` returned `true` instead of the expected `false` — i.e. under this specific mutation the "anti-hollow" case's own assertion (that the two must differ) is the one that fires, which is a second, independent confirmation that the comparator function itself is sound (it correctly reports two byte-identical arrays as identical) and that the guard's failure surface is real, not a test artifact.

**Step 2 — restoration:**

```
$ git diff --exit-code -- src/
$ echo $?
0
$ pio test -e native -f "*test_sdp_harness*"
...
================= 15 test cases: 15 succeeded in 00:00:01.425 =================
```

Restored to `{0x5555, 0x20}` (byte-identical to the phase-start commit `b30b91c`), re-run: **15/15 GREEN**. `git diff --exit-code -- src/` confirmed clean before the commit below was made.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 117-05 is unblocked: FIX-05 is Complete, leaving only FIX-04 (the six frozen artifacts' byte-identity-by-blob-SHA proof) as the phase's remaining open requirement.
- No blockers. `firestarter/src/` remains byte-unchanged from `c7e55b7` (117-03's HEAD) — confirmed via `git diff --stat ada4bdc..HEAD -- src/ include/ test/native/avr/_shared/` limited to the frozen paths (empty) and `git show --stat --name-only HEAD` (exactly one test file).
- Full native suite grew from 106 to 108 test cases (16 suites), all green; both board targets still build with unchanged flash/RAM figures.

---
*Phase: 117-fix-remap-aware-0x0d-emitter-honest-completion-signal*
*Completed: 2026-07-28*

## Self-Check: PASSED

- FOUND: `firestarter/test/native/avr/test_sdp_harness/test_sdp_harness.cpp`
- FOUND: commit `353ce8a` in `firestarter` submodule history
- FOUND: `.planning/phases/117-fix-remap-aware-0x0d-emitter-honest-completion-signal/117-04-SUMMARY.md`
