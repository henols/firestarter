---
phase: 183-flash4-erase-refusal-the-ae29f2008-classification
plan: 04
subsystem: firmware
tags: [platformio, avr-gcc, unity, tdd, flash4, safety-refusal]

# Dependency graph
requires:
  - phase: 183-01
    provides: "firestarter submodule forked onto gsd/v1.37-operator-safety-answered-reports-claim-hygiene, and the cold-build baseline this plan's flash shrink will be measured against in a later plan"
provides:
  - "flash_5v_page.cpp with no 12V bulk-erase path: flash_5v_page_erase_execute (definition + forward declaration), configure_flash_5v_page's CMD_ERASE arm, and flash_5v_page_write_init's FLAG_CAN_ERASE erase-on-write block are all deleted"
  - "a native case, observed RED before the deletion and GREEN after, proving one flash_5v_page_write_init call energises no VPP rail even with FLAG_CAN_ERASE SET"
  - "test_val_5v_page.cpp with every stale reference to the deleted routine repaired by symbol, not by line number"
  - "185-case native baseline (both native and native_nodevtools) recorded as a second input to Phase 185's size_baseline.json re-record"
affects: [183-05, 183-06, 185]

actuals:
  tokens: 2400
  tasks: 3
  commits: 6
  plan_head_before: 70256711

tech-stack:
  added: []
  patterns:
    - "RED-then-GREEN-in-one-commit for a plan-instructed single-commit TDD task: the plan explicitly forbade a standalone RED commit for this task, so the RED observation is recorded in this SUMMARY (verbatim failing-assertion text) rather than as a separate test(...) commit"
    - "ArduinoFake delay() must be stubbed in test_val_5v_page.cpp's setUp() alongside delayMicroseconds() -- any case that reaches flash_5v_page_erase_execute (even transiently, during RED observation) calls delay(), and an unstubbed call aborts the native binary rather than failing an assertion"

key-files:
  created: []
  modified:
    - "firestarter/src/proms/flash_5v_page.cpp (four deletion sites + two stale comment paragraphs removed)"
    - "firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp (new companion case + factory, delay() stub, four prose repairs, one case rename)"

key-decisions:
  - "Task 1's RED and GREEN observations landed in a single feat(183-04) commit, per the plan's explicit instruction not to commit the RED state on its own -- this intentionally departs from the generic TDD test-then-feat two-commit pattern; the RED evidence is instead recorded verbatim in this SUMMARY"
  - "gsd_run check tdd-red-evidence is incompatible with this project's PlatformIO/Unity C++ test output (the checker parses node --test TAP summary lines -- '# tests N', '# pass N', 'ok N - name' -- which PlatformIO's Unity test runner never emits), so it returns a spurious zero_tests_discovered INVALID_RED verdict regardless of the actual test outcome; the plan's own Step 2 instruction (run the suite, confirm the target test fails on the correct assertion, record the failure text) was used instead as the RED-evidence gate for this task"
  - "Added When(Method(ArduinoFake(), delay)).AlwaysReturn() to setUp() (Rule 3 -- blocking issue): without it, the RED observation SIGABRTs on the first unstubbed delay(2) call inside flash_5v_page_erase_execute instead of reaching the assert_no_vpp_in_recording assertion, which would make the RED evidence a fixture crash rather than a real assertion failure"
  - "Disposition (a) confirmed per the plan's adjudication: flash_5v_page_write_init and its firestarter_operation_init assignment are kept even though the function's body is now a no-op past the response_code check -- deleting it and nulling the init pointer would segfault test_val_5v_page.cpp's unguarded h.firestarter_operation_init(&h) call"
  - "The case-count consequence (184 -> 185 on both native envs) is recorded here as a SECOND input to Phase 185's size_baseline.json re-record, alongside the flash-byte shrink CONTEXT.md's D-15 already names -- check_size_baseline.py's compare_native asserts cases EXACTLY, so this plan's own test addition reddens that gate independently of the flash-byte delta"

requirements-completed: [SAFE-08]

coverage:
  - id: D1
    description: "flash_5v_page_erase_execute (definition + forward declaration), configure_flash_5v_page's CMD_ERASE arm, and flash_5v_page_write_init's FLAG_CAN_ERASE erase-on-write block are all deleted from flash_5v_page.cpp"
    requirement: "SAFE-08"
    verification:
      - kind: other
        ref: "/usr/bin/grep -n 'flash_5v_page_erase_execute' src/proms/flash_5v_page.cpp include/flash_5v_page.h (exit 1); /usr/bin/grep -n 'CMD_ERASE' src/proms/flash_5v_page.cpp (exit 1); /usr/bin/grep -c 'is_flag_set' src/proms/flash_5v_page.cpp == 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "A native case proves, RED before the deletion and GREEN after, that one flash_5v_page_write_init call energises no VPP rail even with FLAG_CAN_ERASE SET"
    requirement: "SAFE-08"
    verification:
      - kind: integration
        ref: "test/native/avr/test_val_5v_page/test_val_5v_page.cpp#test_5v_page_write_init_no_vpp_with_flag_can_erase_set"
        status: pass
    human_judgment: false
  - id: D3
    description: "test_val_5v_page.cpp's prose (file-header NOTE, factory block comment, ERASE-02 case name and assertion-3 message) no longer names the deleted symbol or cites a stale line range"
    requirement: "SAFE-08"
    verification:
      - kind: other
        ref: "/usr/bin/grep -n 'flash_5v_page_erase_execute' test_val_5v_page.cpp (exit 1); /usr/bin/grep -n 'flash_5v_page.cpp:' test_val_5v_page.cpp (exit 1); /usr/bin/grep -c 'with_flag_clear' test_val_5v_page.cpp == 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both CI native envs (native, native_nodevtools) pass at 185 cases / 17 suites; the firmware pytest suite passes; the D-04 backstop, the frozen avr-nm fixtures, size_baseline.json and flash_5v_page.h are all byte-unchanged against the phase merge-base"
    requirement: "SAFE-08"
    verification:
      - kind: integration
        ref: "pio test -e native; pio test -e native_nodevtools; python3 -m pytest tests/ -q; git diff --stat $(git merge-base origin/beta HEAD) -- tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno include/flash_5v_page.h src/eprom_operations.cpp scripts/baseline/size_baseline.json"
        status: pass
    human_judgment: false

duration: 55min
completed: 2026-09-11
status: complete
---

# Phase 183 Plan 04: SAFE-08 Flash4 12V Erase Deletion Summary

**Deleted the unreachable 12V bulk-erase routine from `flash_5v_page.cpp` at all four sites, replaced the tautological assertion that used to guard it with a companion native case observed RED (with `FLAG_CAN_ERASE` set) before the deletion and GREEN after, and repaired every stale prose reference the deletion left behind — native case count now 185/185 on both CI envs, backstop and frozen fixtures provably untouched.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-09-11T08:35:00Z (approx)
- **Completed:** 2026-09-11T09:30:00Z (approx)
- **Tasks:** 3
- **Files modified:** 2 (`firestarter/src/proms/flash_5v_page.cpp`, `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp`)

## Accomplishments
- The 12V bulk-erase routine for the 5V-only flash4 family no longer exists anywhere in the tree: `flash_5v_page_erase_execute`'s definition and forward declaration, `configure_flash_5v_page`'s `CMD_ERASE` arm, and `flash_5v_page_write_init`'s `FLAG_CAN_ERASE` erase-on-write block are all gone.
- A new native case (`test_5v_page_write_init_no_vpp_with_flag_can_erase_set`) proves the safety property directly: even with the host wrongly setting `FLAG_CAN_ERASE` on a protocol-`0x05` handle, a single `flash_5v_page_write_init` call energises no VPP rail — observed RED against the pre-deletion tree, GREEN against the post-deletion tree.
- Every stale reference to the deleted routine in `test_val_5v_page.cpp` — the file-header NOTE, a factory comment's `flash_5v_page.cpp:80-86` citation, and the ERASE-02 case's name and third assertion message — is repaired by symbol and enclosing scope, per D-14's citation discipline, not by line number.
- Both CI-run native envs (`native`, `native_nodevtools`) pass at 185 cases / 17 suites (up from 184), and the firmware pytest suite (360 cases, no CI leg) passes. The `eprom_operations.cpp` backstop, both frozen `avr-nm` fixtures, `size_baseline.json`, and `flash_5v_page.h` are all confirmed byte-unchanged against the phase's `origin/beta` merge-base.

## Task Commits

Each task was committed atomically inside the `firestarter` submodule, with the meta repo's gitlink advanced in a paired `chore` commit after each:

1. **Task 1: RED then GREEN — companion case + four-site deletion** (D-12, D-17)
   - `d8cf708` (feat, firestarter) — RED observation recorded below; GREEN observation recorded below; all four deletion sites plus the two now-false comment paragraphs removed in the same commit, per the plan's explicit "do not commit the red state on its own" instruction
   - `7156d870` (chore, meta) — gitlink advance
2. **Task 2: Repair the prose the deletion falsified** (D-17)
   - `fd59234` (test, firestarter) — file-header NOTE deleted, factory comment repaired, ERASE-02 case renamed and its third assertion re-keyed
   - `6f976cf0` (chore, meta) — gitlink advance
   - `24f12fea` (docs, meta) — logged one out-of-scope, pre-existing comment staleness to `deferred-items.md` (see Deviations)
3. **Task 3: Prove the blast radius is contained and the backstop is intact** (D-04, D-13, D-15) — read-only assertions; no files modified, so no source commit. Evidence recorded below.

**Plan metadata:** commit for this SUMMARY.md follows immediately after this file is written (see `git_commit_metadata` step).

## RED-then-GREEN Evidence (Task 1)

**Companion case:** `test_5v_page_write_init_no_vpp_with_flag_can_erase_set` in `test/native/avr/test_val_5v_page/test_val_5v_page.cpp`. Drives a protocol-`0x05` `CMD_WRITE` handle with `ctrl_flags = FLAG_CAN_ERASE` through `configure_memory`, clears the bus recording, calls `h.firestarter_operation_init(&h)` exactly once (through the dispatched pointer, not by function name), then asserts `assert_no_vpp_in_recording`.

**RED (before deletion), command `pio test -e native -f 'native/avr/test_val_5v_page'`, verbatim failing line:**
```
test/native/avr/test_val_5v_page/test_val_5v_page.cpp:116: test_5v_page_write_init_no_vpp_with_flag_can_erase_set: Expected XXXXXXXXXXXXXXXXXXXXXXXX0XXXXXXX Was XXXXXXXXXXXXXXXXXXXXXXXX1XXXXXXX. flash_5v_page_write_init must energise no VPP rail even when FLAG_CAN_ERASE is set	[FAILED]
```
Result line: `15 test cases: 1 failed, 14 succeeded` — the target case failed on the `assert_no_vpp_in_recording` call inside `assert_no_vpp_in_recording`'s `TEST_ASSERT_BITS_LOW_MESSAGE` for `CTRL_VPP_REGULATOR_ENABLE` (bit 7 observed set: `Was ...1...`), i.e. on the intended assertion, for the intended reason — not a compile error, not either of the case's other two assertions. This RED was reached only after adding `When(Method(ArduinoFake(), delay)).AlwaysReturn();` to `setUp()` (see Deviations); before that fix the run `SIGABRT`ed on the unstubbed `delay(2)` inside `flash_5v_page_erase_execute` and never reached the assertion — an invalid RED that was fixed before being recorded.

**GREEN (after deletion), same command:**
```
test/native/avr/test_val_5v_page/test_val_5v_page.cpp:554: test_5v_page_write_init_no_vpp_with_flag_can_erase_set	[PASSED]
```
Result line: `15 test cases: 15 succeeded` — all cases pass, including the companion case and every pre-existing case (nothing regressed).

**On `gsd_run check tdd-red-evidence`:** this generic checker parses `node --test` TAP summary lines (`# tests N`, `# pass N`, `ok N - name`) and returns `INVALID_RED (zero_tests_discovered)` against PlatformIO/Unity output regardless of actual outcome — a tooling-format mismatch, not evidence of an invalid RED. See Deviations.

## Files Created/Modified
- `firestarter/src/proms/flash_5v_page.cpp` — four deletion sites removed (forward declaration, `CMD_ERASE` switch arm, `flash_5v_page_erase_execute`'s whole definition, `flash_5v_page_write_init`'s `FLAG_CAN_ERASE` block); two now-false comment paragraphs removed; `flash_5v_page_write_init` and its `firestarter_operation_init` assignment kept (disposition (a))
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` — new `make_write_init_handle_can_erase_set()` factory and `test_5v_page_write_init_no_vpp_with_flag_can_erase_set` case + `RUN_TEST` registration; `delay()` stub added to `setUp()`; file-header NOTE deleted; factory block comment repaired; ERASE-02 case renamed (`test_5v_page_write_init_no_blank_check_erase02`, dropping `with_flag_clear`) with its `RUN_TEST` registration updated and its third assertion message re-keyed to the blank-check axis

## Decisions Made
- RED-then-GREEN in one commit (Task 1), per the plan's explicit instruction, rather than the generic TDD `test(...)` → `feat(...)` two-commit pattern. See `key-decisions` above and the TDD Gate Compliance note below.
- `gsd_run check tdd-red-evidence` substituted with the plan's own manually-specified RED-evidence procedure, because the generic checker is Node/TAP-specific and produces a false `INVALID_RED` against this project's Unity test output. See `key-decisions` above.
- Disposition (a) confirmed: `flash_5v_page_write_init` kept as a near-no-op function rather than deleted with its init pointer nulled, per the plan's own adjudication and `configure_sram`'s in-tree precedent for a body that is effectively a log line only.

## TDD Gate Compliance

This is a `type: execute` plan (not `type: tdd`), so the plan-level RED/GREEN/REFACTOR gate enforcement in `gsd-core/references/tdd.md` does not formally apply — the `tdd="true"` attribute lives on Task 1 alone, and the plan explicitly instructed a single combined commit rather than the standard `test(...)` → `feat(...)` pair. No `test(183-04):` commit precedes `d8cf708`; the RED evidence is instead the verbatim failing-assertion text recorded above, captured from an actual pre-deletion run of the companion case, and the deletion (GREEN) landed in the same commit exactly as the plan instructed. This is a plan-directed exception, not an undisclosed violation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Stubbed ArduinoFake `delay()` in `test_val_5v_page.cpp`'s `setUp()`**
- **Found during:** Task 1, Step 2 (observing RED)
- **Issue:** The companion case's RED run (with `FLAG_CAN_ERASE` set) reaches `flash_5v_page_erase_execute`, which calls `delay(2)` — unstubbed in this suite's `setUp()` (only `delayMicroseconds` was stubbed). The unstubbed call `SIGABRT`ed the native test binary before Unity could report a `[FAILED]` line for the target assertion, which would have been an `INVALID_RED` (fixture/harness crash, not a real assertion failure) per the #3770 fail-fast rules.
- **Fix:** Added `When(Method(ArduinoFake(), delay)).AlwaysReturn();` to `setUp()`, alongside the existing `delayMicroseconds` stub — the same pattern ten other native suites in this repo already use (`test_val_eprom.cpp`, `test_sdp_harness.cpp`, `test_cmd_admission.cpp`, etc.).
- **Files modified:** `test/native/avr/test_val_5v_page/test_val_5v_page.cpp`
- **Verification:** Re-ran the suite; the target case now fails cleanly on `assert_no_vpp_in_recording` (the intended assertion), not on a signal. After the deletion, the same stub causes no regression (no code path in the post-deletion tree calls `delay()` from this suite's dispatch paths that wasn't already covered).
- **Committed in:** `d8cf708` (Task 1 commit)

**2. [Rule 3 - Blocking, documented not auto-fixed] `gsd_run check tdd-red-evidence` is incompatible with this project's test framework**
- **Found during:** Task 1, Step 2 (attempting to run the generic RED-evidence gate)
- **Issue:** The checker's TAP parser (`parseNodeTestSummary`, `tapFailedTestNames`) expects `node --test` output (`# tests N`, `# pass N`, `ok N - name`) and finds none of those patterns in PlatformIO/Unity's human-readable test-runner output, so it unconditionally returns `INVALID_RED (zero_tests_discovered)` — a false negative caused by a tooling-format mismatch, not by an actual invalid RED.
- **Resolution:** Used the plan's own Step 2 instruction instead — ran the suite directly, confirmed the target test's `[FAILED]` line names the correct assertion and message, and recorded the verbatim output in this SUMMARY (see RED-then-GREEN Evidence above). This is not a code fix; it is a substitution of verification method, disclosed here per Rule 3's "document, don't silently work around" principle. No firmware or gsd-core file was modified for this.
- **Files modified:** None (documentation only)
- **Verification:** The manual RED evidence (verbatim `[FAILED]` line naming `assert_no_vpp_in_recording` on the target case) satisfies the plan's own Step 2 acceptance criterion directly.
- **Committed in:** N/A (procedural substitution, not a code change)

### Out-of-scope Discovery (logged, not fixed)

**`deferred-items.md`** (new file, `.planning/phases/183-flash4-erase-refusal-the-ae29f2008-classification/deferred-items.md`, committed `24f12fea`): `make_write_handle_with_data()`'s inline comment claims `flash_5v_page_write_init` calls blank-check, but the Phase 153 blank-check removal (ERASE-01/ERASE-02) already made that false before this phase touched anything — outside the scope of "correct any prose the deletion made false."

---

**Total deviations:** 2 auto-fixed/documented (1 Rule 3 code fix, 1 Rule 3 tooling substitution), 1 out-of-scope item logged to `deferred-items.md`.
**Impact on plan:** The `delay()` stub fix was necessary for the RED observation to be valid evidence at all; the `tdd-red-evidence` substitution changes verification method, not outcome — the plan's own Step 2 criteria are independently satisfied. No scope creep; the deferred item is explicitly out of scope and untouched.

## Blast-Radius Containment Evidence (Task 3)

**Both CI native envs, run from `firestarter/`:**
```
$ pio test -e native
================ 185 test cases: 185 succeeded in 00:02:34.051 ================
(17 suites, all PASSED, including native/avr/test_val_5v_page)

$ pio test -e native_nodevtools
================ 185 test cases: 185 succeeded in 00:01:25.510 ================
(17 suites, all PASSED, including native/avr/test_val_5v_page)
```
Case count moved from 184 (183-01's recorded baseline) to **185** on both envs, exactly the +1 the companion case adds. `check_size_baseline.py`'s `compare_native` asserts `cases` EXACTLY against `scripts/baseline/size_baseline.json`'s `native_envs` block (`184` recorded there), so this reddens that gate independently of the flash-byte shrink CONTEXT.md's D-15 already names. **This is a SECOND input to Phase 185's `size_baseline.json` re-record** — Phase 185 must re-anchor both `native_envs.cases` to `185`, not only the AVR flash/RAM figures. `183-06`'s ROADMAP amendment should carry both.

**Firmware pytest suite (no CI leg on this branch):**
```
$ python3 -m pytest tests/ -q
360 passed in 46.18s
```
Restating the standing disclosure: this suite runs in NO CI leg of either repository (`build.yml`/`beta-build.yml` run only `pio test -e native` and `pio test -e native_nodevtools`), so this run is the only evidence it was exercised this session.

**Frozen fixtures, header, backstop, and baseline — all byte-unchanged against the phase merge-base:**
```
$ git merge-base origin/beta HEAD
3e26c1bb23e351954227ad48ad6e8f27663914f1

$ git diff --stat 3e26c1bb -- tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno \
    tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno \
    include/flash_5v_page.h src/eprom_operations.cpp
(no output)

$ git diff --stat 3e26c1bb -- scripts/baseline/size_baseline.json
(no output)
```
Both `avr-nm-uno.txt` dumps (which name `flash_5v_page_erase_execute`) are untouched, as required — they are historical records of a specific past build, not descriptions of the live tree.

**Does any gate diff the frozen `avr-nm` fixtures against a live `nm` run?** No. Read `scripts/check_no_heap_or_64bit_symbols.py` and its paired `tests/test_check_no_heap_or_64bit_symbols.py`: both fixture files are consumed exclusively as `--nm-output TARGET=PATH` **input** listings (`_run_checker(["--nm-output", f"uno={_PLANTED_UNO}"])` and the `_CLEAN_POSTCHANGE_UNO` equivalent) — they stand in for a live `avr-nm` invocation in environments without the toolchain; the module never diffs a fixture against a freshly-run `nm` for equality. Each target's listing (live or fixture) is checked independently for the ABSENCE of eleven named heap/64-bit symbols, never compared byte-for-byte against another listing.

**`CMD_ERASE` × protocol `0x05` cross-check**, run with `/usr/bin/grep -rn` (not the devcontainer's `.gitignore`-honouring default `grep`):
```
$ /usr/bin/grep -rn "CMD_ERASE" test/native/avr/ | grep -v test_val_5v_page
```
Every other hit is `CMD_ERASE` combined with a DIFFERENT protocol: `0x0D` (`test_configure_memory.cpp`, `test_eeprom28c_sdp.cpp`, `test_val_eeprom28c.cpp`), `0x06` (`test_val_nor_unlock.cpp`), the SRAM family and `0x07/0x08/0x0B` EPROM protocols (`test_configure_memory.cpp`, `test_vpp_eprom_v131.cpp`), or the `0x05`-agnostic pinmap-refusal check (`test_pinmap_provisional.cpp`). No pre-existing native test drove `CMD_ERASE` on protocol `0x05` — so nothing else in the suite could have gone red for a reason this plan did not author, and the only case exercising that combination is the one this plan's own history added (this plan's own Task 1 companion case exercises `CMD_WRITE`, not `CMD_ERASE`, on `0x05` — the `CMD_ERASE`-on-`0x05` combination itself is now simply unreachable at the dispatch layer, since the arm is deleted).

`size_baseline.json` confirmed unmodified (diffstat above, empty).

## Issues Encountered

None beyond the two documented deviations above (both resolved within Task 1's own execution, no open blockers).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- The 12V bulk-erase routine is gone from the tree, the safety property it used to (not) guarantee is now proved directly by an observed RED-then-GREEN native case, and every stale reference the deletion produced is repaired.
- Both CI native envs are green at 185 cases; Phase 185 has two size_baseline.json inputs waiting (native `cases: 184 -> 185` on both envs, plus whatever flash-byte shrink 183-01's baseline vs. a future cold rebuild records) — not yet re-recorded, by design (out of scope for this phase).
- D-14 (rewriting `check_erase_no_vpp.py`'s impossible line-range citation, `PROTOCOLS.md`'s now-false "capability-gated bulk erase" paragraph, and `CLAUDE.md`'s dangling cross-reference) is NOT covered by this plan — this plan's `files_modified` frontmatter names only `flash_5v_page.cpp` and `test_val_5v_page.cpp`. That work belongs to a later plan in this phase (183-05, by the wave/dependency structure).
- No blockers.

---
*Phase: 183-flash4-erase-refusal-the-ae29f2008-classification*
*Completed: 2026-09-11*

## Self-Check: PASSED
