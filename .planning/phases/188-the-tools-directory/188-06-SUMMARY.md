---
phase: 188-the-tools-directory
plan: 06
subsystem: firmware-build
tags: [platformio, unity, native-tests, ci, size-baseline, frame-vectors, d-08]

requires:
  - phase: 188-01
    provides: wave ordering / meta-first sequencing this plan runs alongside (188-02 host lane), per D-21
provides:
  - "Firmware half of the frame-vector apparatus deleted whole: generator, catalog, generated header, native suite"
  - "Native size baseline (cases/succeeded/suites, both pinned envs) re-recorded from one cold capture, in the same commit as the deletion"
  - "Twelve AVR figures proven unmoved by a post-deletion cold rebuild of the primary target, not assumed"
affects: [188-09 (verdict note needs this plan's transcribed figures and what the deleted contract test asserted)]

actuals:
  tokens: 36566
  tasks: 2
  commits: 1
  plan_head_before: 3c3c802c18896ad8d498fd8a829b11d2300a72f4

tech-stack:
  added: []
  patterns:
    - "Baseline re-record from one cold rm -rf + pio test capture per pinned env, transcribed verbatim from the N test cases: N succeeded line — never computed by arithmetic on the prior record, never via check_size_baseline.py --rebuild (standing project convention, this file's own meta history)."

key-files:
  created: []
  modified:
    - firestarter/platformio.ini
    - firestarter/.github/workflows/build.yml
    - firestarter/.github/workflows/beta-build.yml
    - firestarter/test/native/avr/_shared/host_stubs_common.inc
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/tests/fixtures/captured_test_native_summary.log
    - firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log
    - firestarter/tests/fixtures/planted_size_baseline_suites_errored.log
    - firestarter/tests/test_check_size_baseline.py (not in plan's files_modified; see Deviations)

key-decisions:
  - "Native baseline moved from {cases:185, succeeded:185, suites:17} to {cases:179, succeeded:179, suites:16} for both native and native_nodevtools — exactly the deleted test_frame_vectors suite's own 6 RUN_TEST cases and 1 suite, transcribed from this plan's own cold pio test captures."
  - "AVR figures proven unmoved, not re-recorded: cold rm -rf .pio/build/uno && pio run -e uno reports flash_used=22734, byte-identical to the pinned figure. frame_vectors.h was reachable only from test/native/avr/, confirmed by an empty git grep of src/."

requirements-completed: [TOOLS-06]

coverage:
  - id: D1
    description: "Firmware frame-vector apparatus (generator, catalog, generated header, 3-file native suite) deleted whole, with all four platformio.ini registrations and all four CI steps across build.yml/beta-build.yml removed in the same commit"
    requirement: "TOOLS-06"
    verification:
      - kind: other
        ref: "git ls-files -- tools/catalog/codegen_vectors.py tools/catalog/frame-vectors.toml include/frame_vectors.h 'test/native/avr/test_frame_vectors/*' (empty)"
        status: pass
      - kind: other
        ref: "git grep -c codegen_vectors|frame.vectors across the repo, and platformio.ini/build.yml/beta-build.yml specifically (all zero except 4 documented historical-narration hits — see Deviations)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Native size baseline (both pinned envs) re-recorded from one cold capture, in the same commit as the deletion; both re-captured summary fixtures and the planted suites-errored fixture updated in place"
    requirement: "TOOLS-06"
    verification:
      - kind: other
        ref: "python3 scripts/check_size_baseline.py --native-log native=... --native-log native_nodevtools=... -> PASS: native(cases=179,suites=16), native_nodevtools(cases=179,suites=16)"
        status: pass
      - kind: other
        ref: "python3 -m pytest tests/ -q -> 360 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "Twelve AVR figures proven unmoved by a post-deletion cold rebuild of the primary target (D-20's go/no-go), not edited"
    requirement: "TOOLS-06"
    verification:
      - kind: other
        ref: "rm -rf .pio/build/uno && pio run -e uno -> flash_used=22734, matches scripts/baseline/size_baseline.json avr_targets.uno.flash_used=22734"
        status: pass
      - kind: other
        ref: "pio run (full build, all 3 AVR envs) -> uno/uno328pb/leonardo all SUCCESS"
        status: pass
    human_judgment: false

duration: 12min
completed: 2026-09-12
status: complete
---

# Phase 188 Plan 06: Delete the firmware frame-vector apparatus, re-record the native baseline Summary

**Deleted the firmware-side frame-vector generator/catalog/header/native-suite whole and re-recorded the native size baseline (185→179 cases, 17→16 suites, both pinned envs) from one cold `pio test` capture in the same commit — then proved the twelve AVR figures unmoved by an independent cold rebuild of `uno` (flash_used 22734, byte-identical to the pin).**

## Performance

- **Duration:** ~12 min (commit timestamp 23:08:36Z to this summary at 23:12:07Z, plus verification time after)
- **Tasks:** 2/2 completed
- **Files modified:** 15 (6 deleted, 9 edited) in firestarter; 1 created in meta (this SUMMARY)

## Accomplishments

- Deleted `firestarter/tools/catalog/codegen_vectors.py`, `firestarter/tools/catalog/frame-vectors.toml`, `firestarter/include/frame_vectors.h`, and the entire `firestarter/test/native/avr/test_frame_vectors/` directory (3 files: `host_stubs.cpp`, `serial_read_mock.h`, `test_frame_vectors.cpp`) — no fragment preserved under any name.
- Removed all four `platformio.ini` registrations (the `test_filter` entry and `-I` include-path flag in both `[env:native]` and `[env:native_nodevtools]`).
- Deleted four CI steps invoking the retired generator — `Vector catalog validity check` and `Codegen drift gate (frame_vectors.h)` in both `.github/workflows/build.yml` and `.github/workflows/beta-build.yml` — plus beta-build.yml's now-false explanatory comment block above its pair. None of these four steps was named by any CONTEXT.md decision; they were found by measurement (D-21's own note) and leaving them would have turned firmware CI red on every branch and every beta push.
- Dropped the suite's name from the opt-in-guard comment listing in `test/native/avr/_shared/host_stubs_common.inc`.
- Re-recorded the native baseline in `scripts/baseline/size_baseline.json` from one cold capture (`rm -rf .pio/build/{native,native_nodevtools}` then one `pio test -e <env>` each): both pinned envs move from `{cases: 185, succeeded: 185, suites: 17}` to `{cases: 179, succeeded: 179, suites: 16}` — exactly the deleted suite's own 6 cases and 1 suite. Rewrote `envs_agree_note`'s prose to quote the new figures and added a `cold_rerecord_plan188_06` meta entry recording the transcription source, following this file's own established convention (`cold_rerecord_plan185_01`, `cold_rerecord_phase158`, etc.).
- Re-captured both native summary fixtures (`captured_test_native_summary.log`, `captured_test_native_nodevtools_summary.log`) in place from the same cold run, truncated to the summary block only.
- Re-derived `planted_size_baseline_suites_errored.log` from the same fresh capture (`s/PASSED/ERRORED/`, succeeded→0, same 179 total) rather than leaving it pointed at the pre-deletion shape.
- Proved (Task 2) the twelve AVR figures unmoved: `git grep -n frame_vectors -- src/` returns nothing (the header was reachable only from the native test tree), and a cold `rm -rf .pio/build/uno && pio run -e uno` reproduces `flash_used=22734`, byte-identical to the pinned figure — so per D-20 no AVR figure was edited.
- Ran the full firmware acceptance battery: both pinned native envs green (179/179/16, all suites PASSED), `check_size_baseline.py` exits 0 printing `PASS: native(cases=179,suites=16), native_nodevtools(cases=179,suites=16)`, the firmware python suite passes (360/360), and `pio run` (all three AVR envs) succeeds.

## What the deleted contract test actually asserted (for plan 188-09's verdict note)

`test_frame_vectors.cpp` was a Unity suite of 6 `RUN_TEST` cases, asserting both legs of the COBS frame contract against a frozen golden-vector catalog (`frame_vectors.h`, generated from `frame-vectors.toml` by `codegen_vectors.py`):

1. `test_crc8_known_answer` — pinned the CRC8 polynomial (0x07, seed 0x00) via known-answer values, independent of the production `CRC8_TABLE`.
2. `test_vector_encode_leg` — for every golden vector, `build_cobs_frame_bytes(payload) == frame` (encode leg, no cap).
3. `test_vector_decode_leg` — for vectors ≤ `DATA_BUFFER_SIZE - 1`, `rurp_communication_read_data(frame, DATA_BUFFER_SIZE - 1) == payload` (CMD_IDLE-path decode).
4. `test_vector_decode_leg_main_path` — for all vectors ≤ `DATA_BUFFER_SIZE` (including full-buffer vectors), the same decode at the MAIN-path cap (`DATA_BUFFER_SIZE`) — the EVEN-01 SC1/SC4 full-block proof.
5. `test_cmd_idle_overflow_at_full_block` — a 512-byte payload must overflow (`< 0`) at the CMD_IDLE cap — the CR-01 NUL-slot regression guard.
6. `test_even_block_no_remainder` — pure arithmetic: `65536 % DATA_BUFFER_SIZE == 0` (no partial last chunk for a full 64 KB chip).

This was the only mechanism in the firmware repo proving host and firmware encode/decode the identical wire bytes for the COBS frame contract (T-188-23, accepted per D-08). `firestarter_app/tests/test_cobs.py` independently covers the COBS/CRC8 algorithm on the host side (confirmed during discussion, per CONTEXT.md); no product code on either side imports the deleted symbols.

## Task Commits

1. **Task 1: Delete the apparatus, its registrations and its CI steps, then re-record the native baseline from one cold capture** — `ffa62f1` (feat, in `firestarter`)
2. **Task 2: Prove the twelve AVR figures did not move, and run the firmware acceptance battery** — no commit (measures and verifies only; `<files>` declared "none", working tree confirmed clean after)

**Plan metadata:** this SUMMARY commit (meta repo)

## Files Created/Modified

- `firestarter/tools/catalog/codegen_vectors.py` — deleted (vector code generator)
- `firestarter/tools/catalog/frame-vectors.toml` — deleted (vector catalog)
- `firestarter/include/frame_vectors.h` — deleted (generated header)
- `firestarter/test/native/avr/test_frame_vectors/{host_stubs.cpp,serial_read_mock.h,test_frame_vectors.cpp}` — deleted (native suite)
- `firestarter/platformio.ini` — removed 4 registrations (test_filter + `-I` in both pinned envs)
- `firestarter/.github/workflows/build.yml` — removed 2 CI steps (vector validity check, codegen drift gate)
- `firestarter/.github/workflows/beta-build.yml` — removed the same 2 CI steps plus their explanatory comment block
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — dropped the deleted suite's name from a comment listing
- `firestarter/scripts/baseline/size_baseline.json` — native_envs figures 185/17 → 179/16 (both pinned envs), envs_agree_note rewritten, new `cold_rerecord_plan188_06` meta entry
- `firestarter/tests/fixtures/captured_test_native_summary.log` — re-captured in place (179/179, 16 suites)
- `firestarter/tests/fixtures/captured_test_native_nodevtools_summary.log` — re-captured in place (179/179, 16 suites)
- `firestarter/tests/fixtures/planted_size_baseline_suites_errored.log` — re-derived from the same fresh capture (all ERRORED, succeeded=0, 179 total)
- `firestarter/tests/test_check_size_baseline.py` — `test_clean_native_both_envs_pass` updated from hardcoded 185/17 to 179/16 (see Deviations — not in plan's `files_modified`)

## Decisions Made

- Followed D-20's native-only re-record path: verified the AVR premise (header unreachable from `src/`) by search first, then confirmed with a cold `uno` rebuild, before touching the baseline. The premise held, so no AVR figure was edited — the fallback (full three-target cold recipe) was not needed.
- The `envs_agree_note` and the new `cold_rerecord_plan188_06` meta entry both narrate the deleted suite by name (`test_frame_vectors`, `codegen_vectors.py`, `frame-vectors.toml`, `frame_vectors.h`), matching this file's own established convention for recording what a baseline move corresponds to (see `cold_rerecord_plan185_01`, `native_case_count_revision_260822`, etc., already in the file). This is historical narration of a past deletion, not a preserved fragment of the apparatus.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated `tests/test_check_size_baseline.py`'s hardcoded 185/17 assertion**
- **Found during:** Task 1 (running the mandatory firmware python suite after the baseline re-record)
- **Issue:** `test_clean_native_both_envs_pass` asserts the literal strings `"185"` and `"17"` appear in the checker's `PASS:` output. This file is not in the plan's `files_modified` list, but the baseline move (185→179, 17→16) reddens it immediately, and "the firmware python suite passes" is a mandatory acceptance criterion (D-19) this plan cannot skip.
- **Fix:** Updated the two assertions to `"179"`/`"16"` and rewrote the test's docstring to describe the new move, following the exact in-place-update convention `test_clean_native_both_envs_pass`'s own docstring already documents Plan 185-01 having used for the prior 184→185 move.
- **Files modified:** `firestarter/tests/test_check_size_baseline.py`
- **Verification:** `python3 -m pytest tests/ -q` → 360 passed (0 failed)
- **Committed in:** `ffa62f1`

**2. [Rule 1 - Bug] Corrected a mis-staged commit before proceeding**
- **Found during:** Task 1, immediately after the first commit attempt
- **Issue:** A `git add` invocation listing both already-git-rm'd paths and genuinely-modified paths aborted partway (git errored on the first pathspec that no longer existed as an unstaged path), so the resulting commit captured only the six file deletions and silently left the nine edited files (platformio.ini, both workflow files, size_baseline.json, the shared stub include, the three fixtures, and the test file) unstaged. This would have split D-21(b)'s required single commit into a broken intermediate state (deletions committed with the registrations/CI steps/baseline still referencing them).
- **Fix:** Staged the nine remaining files individually and amended the same commit (nothing had been pushed or built upon in the interim) rather than creating a second commit, preserving the "one cold capture, one commit" requirement.
- **Files modified:** none beyond what Task 1 already specified — this corrected staging, not content.
- **Verification:** `git show --stat HEAD` confirms 15 files in one commit; `git status --short` clean afterward.
- **Committed in:** `ffa62f1` (amended)

### Plan-authored check discrepancies (not code deviations — documented per D-19's "no ritual" instruction to run the real gates, not chase a miscounted one)

**3. The plan's literal "21 lines" fixture-shape assertion does not hold after a suite is removed.**
- Both re-captured summary fixtures are **20 lines**, not 21. The prior 21-line shape was `3 header/separator lines + 17 suite rows + 1 total line`. Deleting `test_frame_vectors` removes one suite row, so the natural, correct summary-block shape is `3 + 16 + 1 = 20`. The plan's task-1 `<verify>` automated leg and acceptance criteria both hardcode `21`, which was evidently written on the (incorrect) assumption that a suite deletion wouldn't change the row count. Padding the fixture to an artificial 21 lines to satisfy the literal number would mean inserting a fabricated row or blank line — dishonest, and contrary to the acceptance criteria's own stated intent ("still contain only the summary block, not becoming multi-thousand-line raw logs"). Treated as a plan defect (Rule 1): both fixtures are genuine, unaltered summary-block captures at their natural 20-line length. All *other* Task-1 verify legs pass unmodified.

**4. The repository-wide sweep (Task 2) finds 4 hits, not 0 — three are necessary historical narration, one is a pre-existing out-of-scope fixture.**
- `scripts/baseline/size_baseline.json:40` and `:89` — the `cold_rerecord_plan188_06` meta entry and the rewritten `envs_agree_note`, both of which the plan's own Task-1 action text instructs be written, and both of which necessarily name the deleted suite/files to explain why the pinned figures moved (exactly the pattern this same file already uses for every prior baseline move it records).
- `tests/test_check_size_baseline.py:587` — the updated docstring's reconciliation sentence, explaining the 185/17→179/16 move by naming the deleted suite (see deviation #1 above).
- `tests/fixtures/planted_build_warnings_native_excess.log:1256` — a pre-existing, stale fixture for a **different** gate (`check_build_warnings.py`'s excess-warning test), not touched by any prior baseline-moving plan (144/149/153/158/183/185) and not in this plan's `files_modified`. It is a frozen raw build-log capture whose tail happens to include a `test_frame_vectors` row from before this plan; the test that consumes it (`test_check_build_warnings.py`) asserts on warning counts earlier in the log, not on suite names, and the full pytest run (360 passed) confirms it is unaffected.
- None of the four is a surviving *functional* fragment of the apparatus (no code, no registration, no CI step) — all are prose/data narration of the retirement, or an unrelated pre-existing fixture. Left as-is rather than scrubbed or edited outside plan scope; documented here in place of the plan's literal zero-count expectation.

---

**Total deviations:** 2 auto-fixed (1 blocking staging correction, 1 blocking test-assertion fix) + 2 documented plan-check discrepancies (not code changes).
**Impact on plan:** No scope creep. Both auto-fixes were necessary to satisfy the plan's own mandatory acceptance criteria (one commit; firmware python suite green). The two plan-check discrepancies are pre-existing arithmetic/scope mismatches in the plan's authored verify scripts, not defects in the delivered change; every other verify leg in both tasks passes as written.

## Issues Encountered

None beyond the deviations documented above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The firmware half of D-08 is complete: no frame-vector fragment survives functionally in `firestarter/`, the native baseline and both summary fixtures are re-recorded from a genuine cold capture, and the AVR figures are proven (not assumed) unmoved.
- Plan 188-09's verdict note can cite this SUMMARY directly for what the deleted contract test asserted and the exact transcribed figures.
- This plan is file-disjoint from the host lane (188-02/188-05) and required no coordination; the host-side D-08 deletion is a separate plan's work.
- No blockers for the remaining phase-188 plans.

---
*Phase: 188-the-tools-directory*
*Completed: 2026-09-12*
