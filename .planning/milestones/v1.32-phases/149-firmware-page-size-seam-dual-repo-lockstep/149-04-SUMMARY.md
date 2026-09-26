---
phase: 149-firmware-page-size-seam-dual-repo-lockstep
plan: 04
subsystem: firmware-eeprom-28c
tags: [firmware, avr, json-parser, eeprom-28c, page-size, flush-count-oracle, unity, native-test]

# Dependency graph
requires:
  - phase: 149-01
    provides: "the v1.32 firmware fork off origin/beta, verified by content, and the cold pre-edit AVR baseline this plan's warm figures are compared against"
  - phase: 149-03
    provides: "the host now emits programming.page_size -> wire page-size for exactly the 18 provenance-corroborated rows, which this plan's parser consumes"
provides:
  - "the page-size wire key (key_page_size / \"page-size\") parsed into firestarter_handle_t.page_size, reset per command in json_parse beside chip_id (D-05)"
  - "eeprom28c_page_mask(uint16_t): a validated power-of-two mask in [1, AT28C_PAGE_SIZE_MAX], rejecting 0 before the subtraction, falling back to AT28C_PAGE_SIZE_FALLBACK (64) silently (D-06/D-07)"
  - "the 0x0D flush boundary as a bitwise AND against the absolute address, mask hoisted once above the per-byte loop in eeprom28c_write_execute"
  - "a flush-count oracle (s_get_data_calls) proving a delivered 128 halves the flush count (130 vs 132 calls at data_size 128), seen to fail before the mask and pass after"
  - "10 new native cases across two existing suites (test_read_timing, test_val_eeprom28c) -- no new suite, no new translation unit (D-15)"
  - "the corrected AT28C_PAGE_SIZE_FALLBACK header comment (unproven, not disproven, for the 66 promoted rows) and the closed DEFERRED sentence"
  - "deletion of the dead json_init() (definition + declaration), zero call sites, zero flash counted toward any budget"
  - "the Firmware seam evidence section of 149-PAGE-SIZE.md and 149-FW-TRANSCRIPTS.md's RED/GREEN oracle transcripts"
affects: [149-05, 149-06, 149-07, 149-08]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Flush-count oracle: assert an exact call count through the ONE seam production reads through (handle->firestarter_get_data), never the bus-write recorder (wrong seam, caps at 256 entries) -- calls == 2*flushes + data_size is derived from the two production readers' own read counts, not asserted independently"
    - "Mechanism-corrected / intent-satisfied resolve-site note: when a decision's literal site (\"at write-INIT\") is measurably wrong (ram_used-exactly-unchanged gate, a conditional early-return, and existing native cases that never call operation_init), record the corrected site with the three measured reasons in the LOCK-04 voice, never as a failed decision"
    - "Zero-before-subtraction on an unsigned mask: reject requested==0 in a branch that returns before ANY `requested - 1` expression executes, because the power-of-two test alone (`x & (x-1) == 0`) admits 0 and an all-ones mask is the dangerous direction (flushes almost never)"

key-files:
  created:
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-FW-TRANSCRIPTS.md
  modified:
    - firestarter/include/firestarter.h
    - firestarter/include/json_parser.h
    - firestarter/src/json_parser.c
    - firestarter/src/proms/eeprom_28c.cpp
    - firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp
    - firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp
    - firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp
    - .planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md

key-decisions:
  - "Verified by grep, before writing any parser code, that no page-size wire key, handle field, or dispatch entry existed anywhere in the firmware prior to this plan -- confirming the project note that the v1.16 primitives.{h,cpp} recompose (which would have carried a wire page-size key) was never merged"
  - "Resolved the mask once above eeprom28c_write_execute's per-byte loop rather than at write-INIT (D-06's literal site), recorded as mechanism-corrected/intent-satisfied with three measured reasons: the merge05 ram_used-exactly-unchanged gate, write_init's conditional early-return on chip-ID mismatch, and every existing native case reaching write_execute without ever calling operation_init"
  - "Removed a self-introduced AT28C_PAGE_SIZE_FALLBACK literal from firestarter.h's field comment during Task 3's rename pass, so the rename gate's non-vacuity check (exactly 3 source files carry the new identifier) holds -- caught by the plan's own acceptance script before commit"
  - "Wrote the RED oracle transcript noting a runner SIGHUP after the Unity summary printed (a harness artifact of the abort path on this platform, not a test defect) -- the printed summary line, captured before the signal, is the load-bearing evidence"

patterns-established:
  - "The two Phase 44 read-timing knobs (read_settling_us, read_strobe_us) are a documented pre-existing instance of the same stale-value defect page_size's reset now closes -- named in both the json_parse comment and 149-PAGE-SIZE.md so a reader does not mistake their continued absence from the reset block for an oversight this phase introduced; plan 07 owns the todo"

requirements-completed: []  # PGSZ-01/PGSZ-02 span multiple plans; per this phase's planner_decisions, plan 08 alone flips PGSZ-0N checkboxes after the whole-phase gate is green

coverage:
  - id: D1
    description: "Wire key page-size parses into firestarter_handle_t.page_size via the one-line extract_int getter, dispatched from the self-sizing key_parsers table, and resets to 0 per command beside chip_id"
    requirement: "PGSZ-01"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp#test_page_size_parsed_from_json"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp#test_page_size_defaults_zero_when_absent"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp#test_page_size_resets_between_two_parses_on_the_same_handle"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp#test_unknown_key_before_a_known_key_does_not_desync_the_token_walk"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp#test_unknown_key_before_page_size_does_not_desync_the_token_walk"
        status: pass
    human_judgment: false
  - id: D2
    description: "The 0x0D flush boundary uses a validated, hoisted bitwise mask against the absolute address; a delivered 128 is OBSERVED (not merely completion-checked) to halve the flush count versus the 64-byte fallback, and absent/explicit-64/non-power-of-two/out-of-range all reproduce the fallback cadence"
    requirement: "PGSZ-02"
    verification:
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp#test_pgsz_absent_field_reproduces_the_64_byte_cadence"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp#test_pgsz_delivered_128_halves_the_flush_count"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp#test_pgsz_explicit_64_matches_the_absent_cadence"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp#test_pgsz_non_power_of_two_falls_back_silently"
        status: pass
      - kind: unit
        ref: "firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp#test_pgsz_out_of_range_falls_back_silently"
        status: pass
    human_judgment: false
  - id: D3
    description: "The seam is software-proven and unvalidated on silicon -- no AT28C part was involved, no support_status value changed, 0x0D stays UNVERIFIED"
    verification: []
    human_judgment: true
    rationale: "Evidence Ceiling (binding, v1.32): silicon validation is explicitly out of scope for this phase and cannot be verified by any automated check available here -- recorded as a standing constraint, not a deliverable to sign off on."

# Metrics
duration: ~65min
completed: 2026-08-19
status: complete
---

# Phase 149 Plan 04: Firmware Page-Size Seam (Firmware-Side) Summary

**Parsed the host's `page-size` wire key into `firestarter_handle_t`, replaced the 0x0D write path's hardcoded 64-byte modulo flush with a validated, hoisted bitwise mask, and proved a delivered 128 is *observed* to halve the flush count (130 vs 132 native `get_data` calls) with a RED-then-GREEN oracle instead of a completion check.**

## Performance

- **Duration:** ~65 min
- **Completed:** 2026-08-19
- **Tasks:** 3/3 completed
- **Files modified:** 8 (7 in `firestarter`, 1 in meta — plus one new meta file, `149-FW-TRANSCRIPTS.md`)

## Accomplishments

- **Verified, not assumed, the pre-plan wire-key state.** Grepped the firmware source before writing
  any parser code: no `page-size` handling of any kind existed in `json_parser.c` or
  `firestarter.h` prior to this plan — corroborating the project note that the v1.16
  `primitives.{h,cpp}` recompose, which would have carried a wire page-size key, was never merged.
  The only pre-existing artifact was the hardcoded 64-byte floor in `eeprom_28c.cpp`.
- `firestarter_handle_t` gained `uint16_t page_size`, `src/json_parser.c` gained the PROGMEM key
  `key_page_size` (`"page-size"`), a `key_parsers[]` dispatch row, and `get_page_size` using the
  one-line `extract_int` form (validation deliberately stays in the 0x0D handler, D-07). The
  per-command reset (`handle->page_size = 0;`, beside `chip_id`) closes the exact overrun PGSZ-02
  exists to prevent: without it, a 128 parsed for one chip would persist into the next command.
- Deleted the dead `json_init()` (definition in `src/json_parser.c`, declaration in
  `include/json_parser.h`) — its token count was `sizeof()` on a pointer parameter, zero call sites
  in `src/`, zero flash saving counted toward any budget.
- Renamed the 64-byte floor to `AT28C_PAGE_SIZE_FALLBACK` (D-10) across all 8 source occurrences in
  3 source files; the frozen `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` transcript is
  deliberately untouched. Added `AT28C_PAGE_SIZE_MAX` (512), a board-invariant validation ceiling.
  Rewrote the header comment: the floor's safety for the 66 promoted rows is stated as **unproven**
  (not disproven), and the per-chip delivery path this phase closes is stated as
  **software-proven and unvalidated on silicon**, closing the old "DEFERRED ... not yet inserted
  into ROADMAP.md" sentence.
- `eeprom28c_page_mask(uint16_t)` resolves a validated mask — power of two in
  `[1, AT28C_PAGE_SIZE_MAX]`, else the fallback — rejecting `requested == 0` in a branch that
  returns before any `requested - 1` expression executes. Hoisted once as
  `const uint32_t page_mask = eeprom28c_page_mask(handle->page_size);` above
  `eeprom28c_write_execute`'s per-byte loop; the flush test changed from
  `(address + 1) % PAGE_SIZE` to `(address + 1) & page_mask`.
- **The flush-count oracle, seen to fail then pass.** Added `s_get_data_calls` (incremented inside
  the mocked `firestarter_get_data` — the only seam every flush-path read in production goes
  through; the bus-write recorder is the wrong seam) and 5 cases to `test_val_eeprom28c.cpp`. With
  the mask still using modulo, `test_pgsz_delivered_128_halves_the_flush_count` **failed**:
  `Expected 130 Was 132` — proving the modulo form never consulted `handle->page_size`. After the
  mask landed, all 5 cases pass (130 for delivered 128; 132 for absent/explicit-64/non-power-of-two
  (96)/out-of-range (2048)). Both transcripts committed in `149-FW-TRANSCRIPTS.md`.
- Added 5 cases to `test_read_timing_params.cpp` (D-05/D-11): delivered-128 parses, absent defaults
  to 0, one handle parsed twice proves the reset (a stale 128 would otherwise survive into a
  page-size-absent command), and two unknown-key-before-a-known-key directions each asserting a
  landed value rather than only the return code.
- 10 new cases total, in the 2 existing suites (D-15, no new suite/TU): both pinned native envs
  (`native`, `native_nodevtools`) agree at **151/151 cases, 17 suites** (baseline 141 + 10). All
  three `test_fix06_*` cases are behaviourally unchanged — the only diff inside their file is the two
  mechanical `AT28C_PAGE_SIZE_FALLBACK` comment renames. `flash_5v_page.cpp`, `platformio.ini` and
  `include/messages.h` are byte-unchanged. All three AVR envs (`uno`, `uno328pb`, `leonardo`) link
  successfully; warm flash deltas (+210 B on all three, from the mask/oracle code and the
  `uint16_t` field) are recorded as an early indicator only, explicitly not a substitute for plan
  06's cold measurement. `python3 -m pytest tests/ -q` (firmware repo) passes 314/314, run after
  each commit.
- `149-PAGE-SIZE.md`'s Firmware seam evidence section is complete with all required subsections;
  `149-check-claims.py` exits 0 over the edited artifact.

## Task Commits

Each task committed atomically, split across the two repos per `commits_land_in`:

1. **Task 1: Add the wire key, the handle field and the per-command reset; delete the dead
   `json_init`** — `58c6a3c` (feat, `firestarter`)
2. **Task 2: Pin the parse contract, the D-05 reset and the D-11 unknown-key skip in
   `test_read_timing`** — `9c65f0f` (test, `firestarter`)
3. **Task 3: Resolve the validated mask, consume it at the flush boundary, and prove it with the
   flush-count oracle** — `28bf089` (feat, `firestarter`), `b8893923` (docs, meta)

**Plan metadata:** committed after this SUMMARY (STATE.md / ROADMAP.md update, meta).

## Files Created/Modified

- `firestarter/include/firestarter.h` — `uint16_t page_size` field on `firestarter_handle_t`
- `firestarter/include/json_parser.h` — dead `json_init()` declaration removed
- `firestarter/src/json_parser.c` — PROGMEM `key_page_size`, `key_parsers[]` row, `get_page_size`,
  the per-command reset, dead `json_init()` definition removed
- `firestarter/src/proms/eeprom_28c.cpp` — `AT28C_PAGE_SIZE_FALLBACK`/`AT28C_PAGE_SIZE_MAX`,
  `eeprom28c_page_mask`, the hoisted `page_mask` local, the bitwise flush test, the corrected header
  comment
- `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` — 5 new cases, the
  stale `parse_json` rationale comment corrected
- `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — `s_get_data_calls`, 5
  new oracle cases, 2 comment renames
- `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` — 3 comment renames
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` — Firmware
  seam evidence section completed
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-FW-TRANSCRIPTS.md` — new,
  wire-key pre-check, RED/GREEN oracle transcripts, both-envs comparison, warm build figures

## Decisions Made

1. **Verified the wire-key pre-condition by grep before writing the parser**, per the plan's binding
   precondition, rather than assuming either the "primitives never merged" note or its opposite.
   Confirmed zero prior page-size handling in the firmware.
2. **Resolved the mask at `eeprom28c_write_execute`'s top, not at write-INIT** (D-06's literal
   site), recorded as mechanism-corrected/intent-satisfied per the plan's explicit instruction, with
   the three measured reasons transcribed into both the code comment and `149-PAGE-SIZE.md`.
3. **Removed a self-introduced `AT28C_PAGE_SIZE_FALLBACK` literal from `firestarter.h`'s field
   comment**, caught during Task 3's own rename-scope acceptance check (which requires the renamed
   identifier to appear in exactly 3 source files) before it was committed as part of Task 3.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Task 1's `firestarter.h` field comment leaked a Task-3 identifier before it existed**
- **Found during:** Task 3, running the rename-scope acceptance check
- **Issue:** Task 1's own comment on the new `page_size` field named the fallback constant
  `AT28C_PAGE_SIZE_FALLBACK` — a Task-3 rename target — which made the Task 3 acceptance script's
  non-vacuity check (the renamed identifier must appear in exactly 3 named source files) fail: it
  found 4 files, `firestarter.h` being the extra one.
- **Fix:** Reworded the field comment to say "its own named fallback floor" without repeating the
  literal identifier.
- **Files modified:** `firestarter/include/firestarter.h`
- **Verification:** Re-ran the exact non-vacuity grep from the plan's own acceptance script; got the
  expected 3-file set.
- **Committed in:** `28bf089` (Task 3 commit — the field comment fix landed alongside the rename it
  was blocking, never committed in its broken state)

**2. [Rule 1 - Bug] A header-comment cross-reference to `eeprom28c_page_mask` broke the acceptance
script's function-body extraction**
- **Found during:** Task 3, running the mask/validation acceptance script
- **Issue:** An early draft of the corrected floor comment named `eeprom28c_page_mask` in prose
  ("... wire -> json_parser.c -> eeprom28c_page_mask, below"). The acceptance script locates the
  function body via the FIRST occurrence of that literal string in the file; the comment's earlier
  occurrence made the script extract the wrong span (starting mid-header-comment), which then failed
  both the "no `DATA_BUFFER_SIZE` in the function body" check and the zero-before-subtraction order
  check.
- **Fix:** Reworded the comment to say "the mask resolver below" without repeating the function
  name literally.
- **Files modified:** `firestarter/src/proms/eeprom_28c.cpp`
- **Verification:** Re-ran the plan's exact Task 3 acceptance script; all assertions passed.
- **Committed in:** `28bf089` (never committed in its broken state — caught pre-commit)

**3. [Rule 1 - Bug] The corrected `test_read_timing_params.cpp` comment still named the deleted `json_init`**
- **Found during:** Task 2, running the acceptance script's `grep -c 'json_init'` check
- **Issue:** The rewritten `parse_json` rationale comment described the deleted dead helper by
  naming it (`json_init()`), which the acceptance criterion (zero occurrences of the literal
  `json_init` in this test file) correctly rejected.
- **Fix:** Reworded the comment to describe the deleted helper's defect without naming it.
- **Files modified:** `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`
- **Verification:** Re-ran the grep check; 0 occurrences.
- **Committed in:** `9c65f0f` (never committed in its broken state — caught pre-commit)

---

**Total deviations:** 3 auto-fixed (all Rule 1 — self-introduced naming collisions with this plan's
own acceptance gates, each caught by re-running the plan's own verification script before the
responsible commit).
**Impact on plan:** No scope creep. All three fixes are wording corrections to this plan's own
comments; none touches behavior, a test assertion, or a `PGSZ-0N` requirement checkbox.

## Issues Encountered

The native test runner emitted `SIGHUP` immediately after printing the Unity summary line during the
RED run (`pio test -e native -f native/avr/test_val_eeprom28c`, mask still on modulo). The Unity
summary itself printed cleanly before the signal (`Expected 130 Was 132` on the delivered-128 case,
10 of 11 cases passing) and `pio test`'s own exit code was non-zero, so the RED evidence is intact;
this reads as a harness artifact of the abort path on this platform, not a defect in the test or the
oracle. Recorded in `149-FW-TRANSCRIPTS.md` rather than treated as a blocker.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 05 (cross-repo parity: a host test asserting `constants.py`'s `JSON_KEY_PAGE_SIZE` equals the
PROGMEM key string in `firestarter/src/json_parser.c`, plus the `scan_paths.py` inventory entry) can
proceed: the firmware now carries `key_page_size = "page-size"` for that parity test to check against.
Plan 06 (post-change cold measurement and MERGE-05 funding) can proceed: this plan's warm build
figures (+210 B flash, +2 B RAM on all three AVR envs) are recorded as an early indicator, explicitly
not a substitute for the cold `rm -rf .pio/build/<env>` capture plan 06 must take. Plan 07's todo list
should carry forward the Phase 44 read-timing knobs' own missing reset (named in both the
`json_parse` comment and `149-PAGE-SIZE.md`) and the runtime INFO log naming the effective page size
(D-09's declined-here follow-up, tied to the gh#21 re-run request). No `PGSZ-0N` requirement
checkbox or traceability row was touched — plan 08 alone flips them.

## Self-Check: PASSED

- FOUND: `/workspaces/firestarter/include/firestarter.h` (`page_size` field present)
- FOUND: `/workspaces/firestarter/src/json_parser.c` (`key_page_size`, `get_page_size`, reset, `json_init` deleted)
- FOUND: `/workspaces/firestarter/include/json_parser.h` (`json_init` declaration deleted)
- FOUND: `/workspaces/firestarter/src/proms/eeprom_28c.cpp` (`AT28C_PAGE_SIZE_FALLBACK`, `AT28C_PAGE_SIZE_MAX`, `eeprom28c_page_mask`, hoisted `page_mask`, bitwise flush test)
- FOUND: `/workspaces/firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` (9 cases)
- FOUND: `/workspaces/firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` (11 cases)
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-FW-TRANSCRIPTS.md`
- FOUND: `/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-PAGE-SIZE.md` (Firmware seam evidence section present)
- FOUND commit: `58c6a3c` (firestarter)
- FOUND commit: `9c65f0f` (firestarter)
- FOUND commit: `28bf089` (firestarter)
- FOUND commit: `b8893923` (meta)
- CONFIRMED: `pio test -e native` — 151/151 cases, 17 suites
- CONFIRMED: `pio test -e native_nodevtools` — 151/151 cases, 17 suites (envs agree)
- CONFIRMED: `python3 -m pytest tests/ -o addopts="" -q` in `firestarter` — 314 passed
- CONFIRMED: `pio run -e uno && pio run -e uno328pb && pio run -e leonardo` — all `[SUCCESS]`
- CONFIRMED: `git -C /workspaces/firestarter diff --quiet src/proms/flash_5v_page.cpp` — unchanged (D-08)
- CONFIRMED: `git -C /workspaces/firestarter diff --quiet platformio.ini` — unchanged
- CONFIRMED: `git -C /workspaces/firestarter diff --quiet include/messages.h` — unchanged
- CONFIRMED: `git -C /workspaces/firestarter diff --quiet test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — unchanged (frozen transcript)
- CONFIRMED: `python3 /workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py` — EXIT=0
- CONFIRMED: no `PGSZ-0N` checkbox or traceability row touched in `REQUIREMENTS.md` or `ROADMAP.md`
- CONFIRMED: meta `M firestarter` / `M firestarter_app` gitlinks not staged by this plan

---
*Phase: 149-firmware-page-size-seam-dual-repo-lockstep*
*Completed: 2026-08-19*

## Self-Check: PASSED

All files and commits listed in the Self-Check section above were independently re-verified on
disk/in git history after this SUMMARY was written: all 9 files FOUND, all 4 commit hashes FOUND
in their respective repos' history.
