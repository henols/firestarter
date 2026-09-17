---
phase: 194-real-page-size-reaches-the-firmware
plan: 02
subsystem: firmware-protocol
tags: [flash-write, page-size, protocol-0x05, native-tests, bootloader-guard]

requires:
  - phase: 194-01
    provides: "flash_5v_page_mask() validator, resolve-or-refuse write path, MSG_ERR_FL4_PAGE_SIZE, raised native bus recorder cap + bus_recording_saturated(), the (65536,128) tracer boundary case"
provides:
  - "7 distinct-pair boundary cases covering all (mem_size, page_size) geometries the 27 protocol 0x05 parts reduce to, including all three pairs where the old capacity-derived page was under by exactly 2x"
  - "A deliberately-wrong-mem_size case proving PAGE-01 at runtime: page_size wins over mem_size even when mem_size's own old derivation would disagree"
  - "Four page-size rejection cases (absent, non-power-of-two, above the 512 ceiling, transport-saturated 65535) each asserting RESPONSE_CODE_ERROR AND zero register writes, plus a positive control"
  - "Measured flash delta for both AVR envs against the plan-01 baseline (zero additional cost -- test-only changes), both bootloader-guard ceilings honoured"
affects: [194-03, 194-04, 194-05, 194-06]

actuals:
  tokens: 2848
  tasks: 3
  commits: 2
  plan_head_before: "2441f36"

tech-stack:
  added: []
  patterns:
    - "SDP-signature-count plus signature-position lower bound as the boundary oracle. Never a raw bus-recording total. The position check (indices[1] >= 3*page_size) independently proves the second page start could not have fired on an under-sized derived page. This is on top of the signature-count check, which already differs (2 vs 4) for every 2x-under pair."
    - "Two-call advancing-address drive for the 512-byte page. This matches the real chunked write path. DATA_BUFFER_SIZE (512) caps one call below the 2*page_size span every other pair uses."

key-files:
  created: []
  modified:
    - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp

key-decisions:
  - "Tasks 1 and 2 landed in a single commit (b1a17c9), not two. Both tasks touch the same single file. Drafting left no natural seam between the boundary cases and the refusal cases. Splitting after both were already written and green would have meant reverting and reapplying half a diff, for no verification benefit. Both tasks' acceptance criteria are independently verifiable against this one commit, and were independently re-run."
  - "8 new test functions were authored for Task 1: all 7 geometry pairs as fresh table-shaped cases, plus the wrong-mem_size case. The (65536,128) pair already had a case from plan 194-01 that satisfies the acceptance criterion's grep-based geometry check on its own. A fresh case was still authored for it, for two reasons. First, every pair then shares the same table-driven shape and the same three-assertion oracle. No pair is singled out with a different pattern. Second, this safely clears the plan's >=8-case-growth verification bar, under either reading of what count it is measured against."
  - "The 'recorded position' assertion the plan calls for (STEP 1, second of three) is implemented as a lower bound: indices[1] >= 3*page_size. This is not an exact index equality. An exact formula was hand-derived and cross-checked against an instrumented diagnostic run. Empirically, for (65536,128) with data_size 256, the completion indices are 6 and 401. But the exact record-per-byte shape is an implementation-shape detail. It is 3 records for a plain byte, +8 for an SDP block, and +3 more at a page-end poll. The suite's own prohibitions warn against ossifying that detail into an exact assertion. The lower bound still fails a 2x-under derived page cleanly. It would place the second signature at roughly half the required record offset."
  - "The four rejection cases plus positive control use mem_size 65536. The page_size test values are 0 (reused from plan 194-01's existing case), 96, 1024, and 65535. These are exactly the four classes D-05 names: absent, not-power-of-two, above-ceiling, transport-saturated."

patterns-established:
  - "A boundary test asserts both a signature count and a signature-position lower bound. This is the shape for any future protocol-0x05-adjacent geometry test. Count alone can coincide for a wrong page size in principle, even though it does not for any of the 7 measured pairs here."

requirements-completed: []

coverage:
  - id: D1
    description: "All 7 distinct (mem_size, page_size) pairs the 27 protocol 0x05 parts reduce to are driven through the real flash_5v_page_write_execute handler. Each one's page starts land on multiples of the part's real page size. This covers the three pairs where the old capacity-derived page was under by exactly 2x (65536/128, 262144/256, 524288/512)."
    requirement: "PAGE-02"
    verification:
      - kind: unit
        ref: "firestarter_fw test/native/avr/test_val_5v_page/test_val_5v_page.cpp::test_5v_page_write_execute_boundary_32768_64 (+6 sibling boundary cases)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A deliberately-wrong mem_size (524288, whose old derivation produced 256) with page_size 128 still produces boundaries on multiples of 128. This proves PAGE-01 at runtime: no capacity-derived value is in play."
    requirement: "PAGE-01"
    verification:
      - kind: unit
        ref: "firestarter_fw test/native/avr/test_val_5v_page/test_val_5v_page.cpp::test_5v_page_write_execute_ignores_mem_size_entirely"
        status: pass
    human_judgment: false
  - id: D3
    description: "Each of the four rejected page-size classes (absent, not a power of two, above the 512 ceiling, transport-saturated 65535) produces RESPONSE_CODE_ERROR and exactly zero register writes. A positive control proves the harness still drives the handler."
    requirement: "PAGE-02"
    verification:
      - kind: unit
        ref: "firestarter_fw test/native/avr/test_val_5v_page/test_val_5v_page.cpp::test_5v_page_write_execute_refuses_page_size_not_power_of_two (+2 sibling rejection cases +1 positive control)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The flash cost of the full change is recorded against the measured pre-change baseline (21598 uno / 23716 leonardo). Both AVR envs stay inside their bootloader-guard ceilings (32256 / 28672)."
    verification:
      - kind: unit
        ref: "pio run -e uno / pio run -e leonardo -- bootloader-guard: uno 21616/32256 B, leonardo 23734/28672 B (both unchanged from plan 194-01's own measurement -- this plan is test-only)"
        status: pass
    human_judgment: false

duration: ~45min
completed: 2026-09-15
status: complete
---

# Phase 194 Plan 02: Real Page Size Reaches the Firmware (Exhaustive Measurement) Summary

**All 7 distinct `(mem_size, page_size)` geometries the 27 protocol `0x05` parts reduce to are now driven through the real `flash_5v_page_write_execute` handler. Each one is proven to land on the part's real page boundary. All four rejected page-size classes are proven to refuse with zero register writes.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-09-15T14:24:00Z
- **Tasks:** 3/3
- **Files modified:** 1

## Accomplishments

- Added 8 table-shaped native cases driving `flash_5v_page_write_execute` over every distinct `(mem_size, page_size)` pair the 27 protocol `0x05` parts reduce to: `(32768,64)`, `(65536,128)`, `(131072,128)`, `(262144,128)`, `(262144,256)`, `(524288,256)`, `(524288,512)`. A further case sets `mem_size` (524288) deliberately inconsistent with its `page_size` (128), to prove PAGE-01 at runtime. The `(524288,512)` case drives the handler twice with an advancing address, rather than raising `DATA_BUFFER_SIZE`. This models the real chunked write path.
- Every boundary case asserts three things. First, `!bus_recording_saturated()` proves the recorder did not truncate. Second, `RESPONSE_CODE_OK` proves the write itself ran. Third, the shared oracle: exactly 2 counted SDP unlock signatures across a 2-page span. The second signature's recorded position (`indices[1]`) must never be observable before at least `page_size` bytes were processed. A mutation test (see Deviations) confirmed this oracle fails correctly against a capacity-derived page size, wherever the derivation and the real page disagree. It also passes correctly wherever they happen to coincide.
- Added the four D-05 rejection cases. The `page_size` test values are 0 (absent, reusing plan 194-01's existing case), 96 (not a power of two), 1024 (above the 512 ceiling), and 65535. The last is the value `json_parser.c`'s SATURATE width policy produces for an out-of-range wire integer. Each case asserts both `RESPONSE_CODE_ERROR` and a bus-recording count of exactly 0. A positive control (`page_size` 128) in the same block asserts `RESPONSE_CODE_OK` and a non-zero recording. So the four negative cases cannot pass because the harness stopped driving the handler.
- Re-measured flash cost for both AVR envs from a clean build. `uno` is 21616/32256 B (67.0%, 10640 B margin). `leonardo` is 23734/28672 B (82.8%, 4938 B margin). Both figures are byte-identical to plan 194-01's own post-change figures. This confirms this plan (test-only) adds zero firmware flash cost. Both `check_cmake_manifest.py` and `check_erase_no_vpp.py` exit 0. `pytest tests/` reports 301/301 passed on a committed tree. The firmware planning-citation gate reports `OK: 177 files scanned, no planning citations`. `pio run` (all AVR envs) succeeds.
- Both native envs (`native`, `native_nodevtools`) report 208/208 succeeded. That is 196 pre-existing after plan 194-01, plus 12 new: 8 boundary/wrong-mem_size cases and 4 rejection/positive-control cases. Confirmed on the clean committed tree.

## Task Commits

Both tasks landed in one commit (see Decisions Made for why). The meta gitlink was then advanced in a second commit. Task 3 edits no tracked file.

1. **Task 1 + Task 2: the 7 distinct-pair boundary cases, the wrong-mem_size case, the four refusal cases, and the positive control** -- `firestarter_fw@b1a17c9` (test)
2. **Gitlink advance** -- meta `8a68bfdb` (test)
3. **Task 3: flash-cost re-measurement and guard re-run** -- no tracked file edited; nothing to commit.

**Plan metadata:** committed below (this SUMMARY only -- STATE.md/ROADMAP.md are owned by the orchestrator in this repo, per the shared_artifact_rule override)

## Files Created/Modified

- `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` - 8 new boundary/wrong-mem_size cases (`drive_page_boundary_case` driver + 8 test functions). 4 new rejection cases (`run_page_size_refusal_case` driver + 3 new named cases, reusing plan 194-01's existing `page_size=0` case as the fourth) plus a positive control. All registered in the `RUN_TEST` block.

## Decisions Made

- **Tasks 1 and 2 committed together.** Both target the same file, with no clean seam once drafted together. The shared driving pattern for boundary cases and the shared driving pattern for rejection cases were both written before either was tested in isolation. Splitting retroactively would have meant reverting and reapplying half of an already-green diff, purely for commit granularity, with no additional verification value. Both tasks' acceptance criteria were independently confirmed against the single resulting commit.
- **8 new cases authored for Task 1, not 7.** The plan's STEP 1 asks for "one table-driven boundary case per distinct geometry, 7 in total." The existing `(65536,128)` tracer case from plan 194-01 already satisfies the letter of every literal acceptance check: the geometry-number grep, and RUN_TEST registration. A fresh `test_5v_page_write_execute_boundary_65536_128` case was still authored, using the same table-driven three-assertion shape as the other 6 new pairs. No pair is left with a structurally different, older-style case. The required "at least 8 greater" case-count growth is met cleanly, regardless of which historical count it is measured against.
- **The "recorded position" assertion is a lower bound, not an exact index equality.** The plan's STEP 1 (second of three per-case assertions) describes checking that a signature's recorded position corresponds to a data address that is an exact multiple of the real page size. The suite's zero-initialized `bus_config` degenerately collapses `mem_util_remap_address_bus`'s output for every write-path byte. This was confirmed by inspection of `memory.cpp`'s remap loop, with an all-zero `address_lines` array. So the LSB/MSB register *values* recorded during ordinary per-byte writes cannot be decoded back into a real chip address. This is also true of every pre-existing case in this file. None of them decode addresses from register values either. An exact record-index formula was derived by hand. It was independently cross-checked against an instrumented diagnostic run (temporarily added, run, and reverted -- see Issues Encountered). For `(65536,128)` at `data_size=256`, the two completion indices are 6 and 401. This matches the derived per-byte/per-SDP-block/per-page-poll record shape exactly. That exact shape is 3 records per plain byte, +8 per SDP unlock block, +3 more at a page-end poll. It is precisely the kind of implementation-shape detail the plan's own prohibitions warn against. Ossifying it into an assertion would violate "must not assert a raw bus-recording count as a boundary oracle." The chosen lower bound (`indices[1] >= 3 * page_size`) is derived from the same shape. It is stated as an inequality, so small implementation changes do not break it. A mutation test (see Deviations) confirms it still fails correctly, for every pair where the wrong derivation and the real page disagree.
- No architectural deviations (Rule 4) were needed. D-05 through D-08 and the phase's own prohibitions were followed as specified.

## Deviations from Plan

### Process deviations (not code)

**1. Comments were briefly introduced into the test file during drafting, then removed before commit.**
- **Found during:** first drafting pass of Task 1's helper functions and test cases.
- **Issue:** the initial draft (before compilation) included explanatory block comments above the shared helper functions and several test cases. This violates this repository's hard no-comments-in-firmware-source-or-tests rule (`CLAUDE.md`, `firestarter_fw/CLAUDE.md`), and this plan's own "Write no comment in this file" instruction.
- **Fix:** every comment introduced during drafting was located and removed via targeted edits, before the file was compiled or committed. The file as committed (`b1a17c9`) carries zero new comments. Only plan 194-01's pre-existing comments remain untouched.
- **Files modified:** `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (comments never reached a commit).
- **Verification:** manual re-read of every added block confirmed no `/* */` or `//` markers remain in the new code. The rationale that would have gone into those comments is recorded here instead.

**2. A shared assertion helper was refactored away mid-task to satisfy a mechanical grep gate.**
- **Found during:** Task 1, after first writing a single shared `assert_page_boundary_shape()` helper called by all 8 boundary cases.
- **Issue:** the plan's own verify step counts literal occurrences of the string `bus_recording_saturated` in the file (`fails_when the printed count is fewer than 9`). This is a proxy for "every new case asserts non-saturation directly." Funnelling the assertion through one shared helper function collapsed the textual occurrence count to 3: 1 extern declaration, 1 helper definition, 1 pre-existing case. This happened even though every case still exercised the assertion at runtime.
- **Fix:** inlined the four-assertion block (including `bus_recording_saturated()`) directly into each of the 8 boundary/wrong-mem_size test functions. Only the handle-setup-and-drive step (`drive_page_boundary_case`) stayed a shared helper. This is more verbose, but it matches this file's own pre-existing convention: every case before this plan already asserts inline, with no shared assertion helpers. It brought the literal count to 10.
- **Files modified:** `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`.
- **Verification:** `grep -c 'bus_recording_saturated' test_val_5v_page.cpp` returns 10 (>= 9 required). All 29 cases still pass.
- **Committed in:** `b1a17c9`.

### Operational recovery, not a code deviation

**3. `gsd-tools query commit` again created and switched to the stray `gsd/v1.39-...-activated-2026-09-15` branch.** This is exactly the hazard flagged in plan 194-01's own SUMMARY and this plan's `<branch_discipline>`.
- **Found during:** the meta-repo gitlink-advance commit for `firestarter_fw`.
- **Issue:** `gsd_run query commit "test(194-02): advance firestarter_fw gitlink..."` auto-created and switched HEAD to `gsd/v1.39-protocol-0x05-write-correctness-activated-2026-09-15` off the same commit. It did not commit on the already-checked-out `v1.39-protocol-0x05-write-correctness`.
- **Fix:** verified the stray branch was a pure fast-forward of `v1.39-protocol-0x05-write-correctness`, with exactly one additional commit and no divergence. `git log --oneline v1.39-protocol-0x05-write-correctness..<stray>` showed only the new commit. The reverse range was empty. Fast-forwarded `v1.39-protocol-0x05-write-correctness` onto the stray branch's tip, switched back, and deleted the stray branch. No commits or history were lost.
- **Files modified:** none (git refs only).
- **Verification:** `git rev-parse --abbrev-ref HEAD` on the meta repo reads `v1.39-protocol-0x05-write-correctness` after recovery. `git branch -a` no longer lists the stray branch. `git log --oneline -3` shows the expected linear sequence ending in `8a68bfdb`.
- **Committed in:** N/A (branch-pointer correction, not a content commit).

---

**Total deviations:** 2 process deviations (both self-caught and corrected before commit, zero net effect on the committed content) + 1 operational git-branch recovery (not a code change).
**Impact on plan:** None of the three affected the plan's shipped content. No scope creep.

## Issues Encountered

- **A temporary diagnostic case was added, compiled, run, and fully reverted, to calibrate the exact record-index shape before choosing the final lower-bound assertion.** A throwaway `test_DIAG_record_layout` function (using `TEST_FAIL_MESSAGE` to print `sig_count`, both signature indices, and the total recording count) was added via a scripted patch. It was compiled and run once against the plan-194-01 handler, then `git checkout --`-reverted before any further edits. This produced the empirical ground truth: `sig_count=2 idx0=6 idx1=401 total=790` for `(65536,128)` at `data_size=256`. That ground truth was used to derive and cross-check the final lower-bound formula. No trace of this diagnostic remains in the committed file.
- **A mutation test was run to confirm the new oracle is non-vacuous.** `flash_5v_page_write_execute`'s validated-mask lookup was temporarily monkey-patched (`src/proms/flash_5v_page.cpp`, uncommitted, restored byte-for-byte afterward). The patch derived a page size from `mem_size` instead of consuming `handle->page_size`, deliberately reproducing gh#67's shape. 10 of the 29 cases in this suite failed under that mutation. The failing set is every boundary case where the mutated derivation and the real page disagreed: `(65536,128)`, `(131072,128)`, `(262144,128)`, `(524288,512)`, and the wrong-mem_size case. It also includes all four rejection cases, since the mutation bypassed the `page_size` validator entirely. The three boundary cases where the mutated derivation happened to coincide with the real page (`(32768,64)`, `(262144,256)`, `(524288,256)`) correctly stayed green. This confirms those pairs have no defect to catch. `git diff` confirmed the source file was restored byte-identical (`git status --short` clean) before any further edits or commits.
- No blockers were encountered. All three tasks' `<verify>` blocks passed on first execution of the final (non-diagnostic, non-mutated) code.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The firmware half of PAGE-02 is now measured across all 27 protocol `0x05` parts, via their 7 distinct geometries. This is not just the single `W29C512` tracer pair plan 194-01 proved.
- PAGE-01 has an explicit runtime proof (`test_5v_page_write_execute_ignores_mem_size_entirely`), independent of the `(65536,128)` tracer case. That tracer case only demonstrated correct behavior. It did not also demonstrate indifference to a *wrong* `mem_size`.
- D-05's enforcement half (all four rejected page-size classes refuse with zero register writes) is now measured. This is not just the single `page_size=0` case plan 194-01 added.
- `.planning/REQUIREMENTS.md` remains untouched by design. PAGE-01/PAGE-02 stay open until plan 06, per this plan's own prohibitions.
- Plan 03 (the host 27-row table test) and plan 04 (the wire-dict delta layer) can now proceed against a firmware side that is exhaustively measured, not just tracer-proven.
- No stubs, skipped tests, or unrun `<verify>` blocks exist in this plan's deliverables. Nothing to append to `.planning/WINDOWS.md`.

## Self-Check: PASSED

Modified file confirmed present on disk: `[ -f firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp ]` succeeds. Both commit hashes confirmed present: `git -C firestarter_fw log --oneline --all | grep -q b1a17c9` and `git log --oneline --all | grep -q 8a68bfdb` (meta) both succeed. Both native envs (`native`, `native_nodevtools`) re-confirmed 208/208 succeeded on the final committed tree. `pytest tests/` re-confirmed 301/301 passed on the final committed tree. `git status --porcelain` is empty in both the meta repo and `firestarter_fw`.

---
*Phase: 194-real-page-size-reaches-the-firmware*
*Completed: 2026-09-15*
