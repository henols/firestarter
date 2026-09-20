---
phase: 199-what-the-rails-can-actually-deliver
plan: 03
subsystem: firmware
tags: [firestarter_fw, eprom, vpp, vpe-as-vpp, native-test, unity, table-05]

requires:
  - phase: 199-what-the-rails-can-actually-deliver (plan 199-02)
    provides: "199-BENCH-RECORD.md's Measured figures block, including DELIVERABLE_MAX_DROP_PATH_MV = 17380"
  - phase: 199-what-the-rails-can-actually-deliver (plan 199-04)
    provides: "the 30-row VPP-rail census (10 on 0x07, 20 on 0x0B) this plan's routing change acts on"
provides:
  - "RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV (17380), a shield-property constant in rurp_pinout.h"
  - "eprom_hv_route_mask's fourth resolution step: handle->vpp_mv > ceiling routes the undropped rail, decided on path capability alone, never on a voltage reading (D-22)"
  - "test/native/avr/test_hv_route_ceiling, a 15-case native suite registered in both native_base test envs"
  - "Three corrected firmware doc sites (eprom.cpp x2, eprom.h x1) and a re-derived tests/golden/protocol_branch_inventory.json"
  - ".planning/phases/199-what-the-rails-can-actually-deliver/199-03-FIRMWARE-NOTES.md, the constant's provenance record and 199-05's DECODE-NOTES debt"
affects: [199-05]

actuals:
  tokens: 42000
  tasks: 3
  commits: 7
  plan_head_before_fw: b031ec2~1
  plan_head_before_meta: 77c1e8e2

tech-stack:
  added: []
  patterns:
    - "Opt-in voltage-read counter stub (HOST_STUBS_CUSTOM_VOLTAGE_MV): a native test suite supplies its own rurp_read_voltage_mv that counts calls rather than returning a fixed value, turning 'the resolver reads no voltage' from an assertion in prose into a runtime-falsifiable zero-count check on every routing case."
    - "Boundary triple derived from the shipped constant itself (macro +1 / macro / macro -1), never from a hardcoded copy of the shipped integer, so a future re-measurement moves the test with the constant instead of silently going stale or falsely reddening."

key-files:
  created:
    - firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp
    - firestarter_fw/test/native/avr/test_hv_route_ceiling/host_stubs.cpp
    - .planning/phases/199-what-the-rails-can-actually-deliver/199-03-FIRMWARE-NOTES.md
  modified:
    - firestarter_fw/include/rurp_pinout.h
    - firestarter_fw/src/proms/eprom.cpp
    - firestarter_fw/include/eprom.h
    - firestarter_fw/platformio.ini
    - firestarter_fw/tests/golden/protocol_branch_inventory.json

key-decisions:
  - "Followed the OVERRIDE block in 199-03-PLAN.md over the task bodies: the no-comments-in-source rule the plan was authored under was removed mid-phase (meta 41a34c6a, firestarter_fw abfc2ec), so both new test files carry the standard licence header, and the three stale documentation sites are corrected in place in this plan's own commits rather than left for 199-05."
  - "Deviated from the OVERRIDE's literal 'keep each edit to the sentence that is wrong' instruction for eprom.cpp's resolution-order doc block: added a fourth numbered step documenting the new ceiling comparison, rather than only patching steps 1 and 3's wrong claims, because the block's own header says 'Resolution order, exactly' and leaving a 4-branch function documented as 3 steps would trade one stale claim for another. See Deviations."
  - "Re-derived tests/golden/protocol_branch_inventory.json (TABLE-05) after discovering it broken by Task 1's new branch plus this plan's doc-block growth — a real regression against the plan's 'Python suite unmoved' requirement, fixed per that file's own established re-derivation convention (git hash-object for the blob SHA, live _extract_predicates() re-parse for the sites, a new dated entry in its recorded_by history). Not in the plan's original files_modified list. See Deviations."
  - "Read the plan-level <verification> item 2 ('additions only... in rurp_pinout.h, eprom.cpp and eprom.h') as superseded by the OVERRIDE for eprom.cpp and eprom.h: those two files' doc corrections require replacing wrong sentences, which is a delete+add in git diff terms. The OVERRIDE explicitly keeps only the rurp_pinout.h zero-deletion invariant load-bearing ('it never was a comment rule'), and that invariant holds across the whole plan, verified separately from eprom.cpp/eprom.h."

requirements-completed: []

coverage:
  - id: D1
    description: "eprom_hv_route_mask returns CTRL_VPP_REGULATOR_ENABLE for a drop-resistor row (0x07, 0x08) whose required vpp_mv is strictly greater than RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV, and EPROM_HV_ROUTE_MASK otherwise — the boundary is strictly greater-than at ceiling, ceiling+1 and ceiling-1, all derived from the macro (RAIL-04, D-21)"
    requirement: "RAIL-04"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x07_above_ceiling_routes_undropped_rail_reading_no_voltage"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x07_at_ceiling_exactly_stays_on_drop_path"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x07_one_millivolt_above_ceiling_routes_undropped_rail"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x07_one_millivolt_below_ceiling_stays_on_drop_path"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x08_at_ceiling_exactly_stays_on_drop_path"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x08_one_millivolt_above_ceiling_routes_undropped_rail"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x0B_at_zero_required_voltage_returns_undropped_rail"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x0B_at_ceiling_returns_undropped_rail"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_0x0B_above_ceiling_returns_undropped_rail"
        status: pass
    human_judgment: false
  - id: D2
    description: "The routing decision provably reads no voltage: every routing case in the new suite asserts a zero count on a live, non-vacuously-proved rurp_read_voltage_mv counter (D-22)"
    requirement: "RAIL-04"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_voltage_read_counter_is_live_and_moves_on_a_direct_call"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-22's own two-row table is reproduced as falsifiable cases: at a required 18000 mV the existing ADC comparison would stay silent while the path rule routes; at 21000 mV the same ADC comparison would fire"
    requirement: "RAIL-04"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_d22_row_one_18000_required_adc_check_would_stay_silent_while_path_rule_routes"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_d22_row_two_21000_required_adc_check_would_fire_but_only_this_row_would_be_caught"
        status: pass
    human_judgment: false
  - id: D4
    description: "Absent evidence never raises a rail: an unresolved protocol at the largest representable voltage, and a zero required voltage on 0x07, both return the drop-path mask; the manual override still wins first on an unresolved protocol"
    requirement: "RAIL-04"
    verification:
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_unresolved_protocol_at_max_representable_voltage_stays_fail_closed_on_drop_path"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_zero_required_voltage_on_0x07_stays_fail_closed_on_drop_path"
        status: pass
      - kind: unit
        ref: "firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp#test_manual_override_wins_before_any_table_read_on_unresolved_protocol"
        status: pass
    human_judgment: false
  - id: D5
    description: "eprom_check_vpp is byte-unchanged and continues to verify whatever rail eprom_hv_route_mask routes (RAIL-03, D-23) — no host change, no message ID, no wire change"
    requirement: "RAIL-03"
    verification:
      - kind: other
        ref: "git diff across this plan's commits touching src/proms/eprom.cpp, restricted to eprom_check_vpp's own line range — zero lines changed"
        status: pass
    human_judgment: false
  - id: D6
    description: "The three stale documentation sites (eprom.cpp x2, eprom.h x1) are corrected in place, minimally, with no process citations, and the TABLE-05 branch-inventory golden is re-derived to match"
    requirement: ""
    verification:
      - kind: other
        ref: "firestarter_fw/tests/test_hv_routing_source_contract_v142.py (16/16) and tests/test_protocol_branch_inventory.py (7/7)"
        status: pass
    human_judgment: false
  - id: D7
    description: "No CI leg regresses: both native environments run the new suite green with case counts up by exactly 15, all three AVR builds hold flash budget, and pytest tests/ holds at its 17 failed / 284 passed baseline"
    requirement: ""
    verification:
      - kind: integration
        ref: "pio test -e native (232/232), pio test -e native_nodevtools (232/232), pio run -e leonardo/uno/uno328pb, pytest tests/ (17 failed, 284 passed)"
        status: pass
    human_judgment: false

duration: 95min
completed: 2026-09-19
status: complete
---

# Phase 199 Plan 03: VPE-as-VPP Routing Moves to Firmware Summary

**`eprom_hv_route_mask` gains one comparison — `handle->vpp_mv > RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` (17380 mV, measured at socket pin 1) — that routes the undropped VPE rail for the ten algorithm-0x07/0x08 rows the drop-resistor path cannot reach, decided purely on path capability with a 15-case native suite proving the decision reads no voltage (D-22), plus a golden-inventory fix and three corrected stale doc sites the change surfaced.**

## Performance

- **Duration:** 95 min
- **Started:** 2026-09-19T00:00:00Z (approx, sequential executor)
- **Completed:** 2026-09-19
- **Tasks:** 3
- **Files modified:** 5 (2 new)

## Accomplishments

- Task 1 (tracer): added `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` (17380, read from
  `199-BENCH-RECORD.md`'s `## Measured figures` fenced block) to `rurp_pinout.h` with zero deleted
  lines in that file; added the one strictly-greater-than comparison to `eprom_hv_route_mask`;
  registered the new native suite in both `native_base` `test_filter`/`shared_build_flags` lists
  with exactly two lines each (the "four new lines" instruction in `firestarter_fw/CLAUDE.md`
  predates the `native_base` refactor and is stale — reported, not edited); wrote the suite's one
  case, proving the routing decision reads zero voltage.
- Tracer feedback gate: no `gate="blocking-human"`, auto mode inactive, mode `end-of-phase` with
  only `<automated>` verify legs — re-ran all six Task 1 verify legs end-to-end, all passed, expanded
  to Task 2 without a checkpoint.
- Task 2: extended the suite to 15 cases — the boundary triple (all three derived from the macro,
  never a hardcoded copy of 17380), protocol 0x08 on both sides of the boundary, protocol 0x0B
  unaffected at three points, two fail-safes, the manual-override case, a counter non-vacuity proof,
  and the two D-22 falsifiability cases reproducing the reversal's own ADC-vs-path-rule table against
  the bench record's `ADC_PAIRED_DROP_MV` witness (18700).
- Task 3: corrected the three stale documentation sites the OVERRIDE named (two in `eprom.cpp`'s
  resolution-order block, one in `eprom.h`'s declaration block); discovered and fixed a real
  regression in `tests/golden/protocol_branch_inventory.json` (TABLE-05) that Task 1's new branch
  plus the doc growth broke; wrote `199-03-FIRMWARE-NOTES.md`; ran the full regression set and
  confirmed every baseline held.

## Task Commits

Each task was committed atomically, inside `firestarter_fw` on `v1.40-program-parameter-fidelity`,
with the meta gitlink advanced separately for each:

1. **Task 1: the constant, the comparison, the suite's first case** —
   `firestarter_fw@b031ec2` (feat), meta gitlink `db1fb7fb` (docs)
2. **Task 2: boundary triple, fail-safes, D-22 made falsifiable** —
   `firestarter_fw@bdefe38` (test), meta gitlink `af3379ed` (docs)
3. **Task 3a: three stale doc sites corrected, branch-inventory golden re-derived** —
   `firestarter_fw@a050730` (docs), meta gitlink `ea39ba0d` (docs)
3. **Task 3b: firmware notes artifact** — meta `dab944af` (docs)

**7 commits total** (3 in `firestarter_fw`, 4 in the meta repo — 3 gitlink advances plus the notes
commit). No plan-metadata commit follows this SUMMARY (per this plan's explicit instruction: the
orchestrator owns `STATE.md`/`ROADMAP.md`; `REQUIREMENTS.md` is untouched, so no final metadata
commit is needed from this plan either).

## Files Created/Modified

- `firestarter_fw/include/rurp_pinout.h` — `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` (17380), inserted
  after `EPROM_HV_ALL_OFF_MASK` with a blank separator line; zero pre-existing lines touched.
- `firestarter_fw/src/proms/eprom.cpp` — `eprom_hv_route_mask` gains one guard after the
  `row->vpp_path` check and before the final `return EPROM_HV_ROUTE_MASK;`; the function's
  resolution-order doc comment corrected (steps 1 and 3) and extended with a new step 4.
- `firestarter_fw/include/eprom.h` — the declaration comment above `eprom_hv_route_mask` corrected
  to say the route no longer comes from the `vpp_path` column alone.
- `firestarter_fw/platformio.ini` — two new lines in `[native_base]` registering
  `test/native/avr/test_hv_route_ceiling` for both native environments.
- `firestarter_fw/test/native/avr/test_hv_route_ceiling/host_stubs.cpp` (new) — supplies a counting
  `rurp_read_voltage_mv` behind `HOST_STUBS_CUSTOM_VOLTAGE_MV`, plus a reset/accessor pair.
- `firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp` (new) — 15 Unity
  cases, licence header present, no shipped integer hardcoded.
- `firestarter_fw/tests/golden/protocol_branch_inventory.json` — re-derived: new blob SHA for
  `eprom.cpp`, one new site (the ceiling comparison, line 257, class `vpp_route`), every site from
  the old `:266` onward shifted by +9, a new dated entry appended to `recorded_by`.
- `.planning/phases/199-what-the-rails-can-actually-deliver/199-03-FIRMWARE-NOTES.md` (new) — the
  constant's full provenance, the ceiling-vs-threshold distinction, the three corrected doc sites
  quoted before/after, and what `199-05` still owes its DECODE-NOTES section.

## Measured Figures

**Native test case counts:**

| Environment | Before | After | Delta |
|---|---|---|---|
| `native` | 217 | 232 | +15 (the new suite) |
| `native_nodevtools` | 217 | 232 | +15 (the new suite) |

**Leonardo bootloader-guard (bytes / 28672 B safe ceiling):**

| When | Used | % | Margin |
|---|---|---|---|
| Before (Task 1 baseline) | 23798 B | 83.0% | 4874 B |
| After (final, Task 3) | 23816 B | 83.1% | 4856 B |

18 bytes added for the one new comparison and its constant reference; margin unaffected in any
practical sense. `uno` (21698/32256 B, 67.3%, 10558 B margin) and `uno328pb` (21742/32384 B, 67.1%,
10642 B margin) both pass `bootloader_guard.py`; no independent "before" figure was taken for either
since only `leonardo` was baselined per the plan's Task 1 instruction.

**Python suite (`pytest tests/`):** held at **17 failed, 284 passed** before and after — all 17 the
pre-existing stale scan path to `.planning/v1.23-FLASH-PATH-DECISION.md`, none of them new. Verified
with a clean working tree; `test_flash_path_record_sync.py` and `test_trace_segment_exhaustiveness_v131.py`'s
planted-mutation tests both assert `git status --porcelain == ""` internally, so an uncommitted
doc-correction diff at run time briefly and falsely surfaced 4 additional failures — resolved by
committing before the final re-run, not by any code change (see Deviations).

**`tests/test_hv_routing_source_contract_v142.py`:** 16/16, unchanged.

**`tests/test_protocol_branch_inventory.py`:** 7/7 after the golden re-derivation (2/7 failing
before it, both attributable to the SHA/line-position drift Task 1's branch and the doc growth
caused).

## Decisions Made

See `key-decisions` in the frontmatter. In summary:
1. Followed the plan's OVERRIDE block over the task bodies: comments (including the standard
   licence header) are permitted in the two new test files, and the three stale doc sites are
   corrected now rather than deferred to `199-05`.
2. Went one step further than the OVERRIDE's literal instruction for `eprom.cpp`'s resolution-order
   block by documenting a new step 4, because the block explicitly claims to be exhaustive
   ("Resolution order, exactly") and a corrected-but-incomplete doc would still be wrong.
3. Discovered and fixed a real, plan-relevant regression in `tests/golden/protocol_branch_inventory.json`
   not named anywhere in `199-03-PLAN.md`'s `files_modified`, because the plan's own success
   criterion ("No CI leg regresses... `pytest tests/` ... zero failures other than the 17") required
   it.
4. Read the plan-level `<verification>` item 2 ("additions only... in rurp_pinout.h, eprom.cpp and
   eprom.h") as superseded by the OVERRIDE for `eprom.cpp`/`eprom.h`; only `rurp_pinout.h`'s
   zero-deletion invariant was treated as still load-bearing, per the OVERRIDE's own closing
   paragraph naming that check specifically.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Documented a fourth resolution step in `eprom_hv_route_mask`'s doc comment, beyond the OVERRIDE's literal "sentence that is wrong" scope**
- **Found during:** Task 3, while correcting the two named-wrong sentences in the resolution-order
  doc block.
- **Issue:** The OVERRIDE instructed fixing only the specific wrong claims in steps 1 and 3. Doing
  only that would leave a doc comment that says "Resolution order, exactly" enumerating three steps,
  while the function now has four branches — trading one stale claim (the wrong "pure override" and
  "anything else" claims) for a different one (an incomplete "exactly" enumeration).
- **Fix:** Added step 4, documenting the ceiling comparison itself, and referenced it from the
  corrected steps 1 and 3.
- **Files modified:** `firestarter_fw/src/proms/eprom.cpp`
- **Verification:** the two Task 3 stale-doc verify legs pass (`'a pure human override'` absent,
  `'vpp_path'` and `'from the eprom_params vpp_path column'` present in `eprom.h`); manually
  re-read the corrected block for internal consistency.
- **Committed in:** `a050730` (Task 3 commit)

**2. [Rule 3 - Blocking] Re-derived `tests/golden/protocol_branch_inventory.json` (TABLE-05), broken by Task 1's new branch plus this plan's own doc-block growth**
- **Found during:** Task 3, running the full `pytest tests/` regression set for the first time this
  plan — surfaced 21 failed / 280 passed against the required 17 failed / 284 passed baseline.
- **Issue:** `eprom_hv_route_mask`'s new comparison (Task 1) and the corrected resolution-order doc
  comment (this task) together shifted every branch-predicate line number in `eprom.cpp` from the
  old `FLAG_VPE_AS_VPP` site onward, and added one new branch site (the ceiling comparison itself).
  `tests/test_protocol_branch_inventory.py` pins both the file's blob SHA and its full
  positionally-ordered site list, so both the blob-SHA leg and the site-list leg failed
  (2 of 7 node ids), plus two unrelated planted-mutation tests in
  `test_trace_segment_exhaustiveness_v131.py` that assert a clean working tree and briefly, falsely,
  saw the uncommitted diff.
- **Fix:** Ran the module's own `_extract_predicates()` against the live file to get the true site
  list (22 sites, one new at line 257, class `vpp_route`, keyed on `vpp_mv`); computed the new
  `eprom.cpp` blob SHA via `git hash-object` on the working tree before staging (the file's own
  documented convention); mapped every surviving site to its prior `class`/`reason` positionally;
  appended a new dated entry to the JSON's `recorded_by` history field, following the same
  convention every prior re-derivation in that file already uses, including an explicit note on
  the deviation from the file's own "one-commit property" (the break was introduced in Task 1's
  commit, two commits before this fix, because Task 1's own `<verify>` block does not run the
  `tests/` suite).
- **Files modified:** `firestarter_fw/tests/golden/protocol_branch_inventory.json`
- **Verification:** `pytest tests/test_protocol_branch_inventory.py` returns 7/7; full
  `pytest tests/` returns to 17 failed / 284 passed.
- **Committed in:** `a050730` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 Rule 2 documentation-completeness fix, 1 Rule 3 blocking golden-file
regression fix). Both were caught and resolved within Task 3, before that task's commit landed.
**Impact on plan:** Neither changes what the plan ships (the routing rule, the ceiling constant, the
15-case suite); both were necessary to keep the plan's own "no CI leg regresses" success criterion
true. The golden-file fix in particular would have shipped a silently-broken CI gate had it not been
caught by actually running the full `pytest tests/` suite Task 3's action requires.

## Known Stubs

None.

## Threat Flags

None beyond what the plan's own `<threat_model>` already registers (T-199-01 through T-199-06,
T-199-SC) — no new network endpoint, auth path, or wire field was added. `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV`
and the new comparison are exactly the surface the plan's threat register already covers.

## Issues Encountered

- Running the full `pytest tests/` suite against an uncommitted working tree produced 4 false
  failures (two planted-mutation tests in `test_trace_segment_exhaustiveness_v131.py` assert
  `git status --porcelain == ""` internally). Resolved by committing the pending doc/golden changes
  before the final regression run — not a code issue, a run-ordering one. No fix needed beyond
  committing in the right order.
- Otherwise none beyond the two deviations documented above, both resolved within Task 3 before its
  commit.

## User Setup Required

None — no external service configuration required. Firmware-only change; nothing pushed, no tag
created, no workflow dispatched.

## Next Phase Readiness

- RAIL-04 is satisfied by firmware that already ships and now routes correctly (D-21); RAIL-03's
  existing acceptance window follows the new route for free (D-23). Both requirement IDs are left
  **Pending** in `REQUIREMENTS.md`, per this plan's explicit instruction — `RAIL-04` is also
  declared by `199-05`, and requirement state is the orchestrator's/verifier's to move.
- `firestarter_fw` HEAD is on `v1.40-program-parameter-fidelity`; nothing was pushed, no tag was
  created, no workflow was dispatched.
- **`199-05-PLAN.md` still references the reverted host module `firestarter/vpp_rail_gate.py` in
  three places** (carried over from this plan's own `<output>` instruction) **and needs replanning
  before it runs.** `199-03-FIRMWARE-NOTES.md` § 4 records what its DECODE-NOTES section now owes:
  the posture change for all three corrected doc sites, the constant's provenance and one-board
  limit, and that routing now lives in firmware rather than a host module that no longer exists.
- `.planning/STATE.md`, `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md` are untouched by this
  plan.

## Self-Check: PASSED

- `[ -f firestarter_fw/test/native/avr/test_hv_route_ceiling/test_hv_route_ceiling.cpp ]` — FOUND
- `[ -f firestarter_fw/test/native/avr/test_hv_route_ceiling/host_stubs.cpp ]` — FOUND
- `[ -f .planning/phases/199-what-the-rails-can-actually-deliver/199-03-FIRMWARE-NOTES.md ]` — FOUND
- `git -C firestarter_fw log --oneline --all --grep="199-03"` — FOUND `b031ec2`, `bdefe38`, `a050730`
- `git log --oneline --all --grep="199-03"` (meta repo) — FOUND `db1fb7fb`, `af3379ed`, `ea39ba0d`, `dab944af`
- Re-ran all `<verify>` legs from all three tasks and the plan-level `<verification>` block: all
  pass (see Measured Figures above).
- `firestarter_fw` HEAD branch: `v1.40-program-parameter-fidelity` (confirmed via
  `git rev-parse --abbrev-ref HEAD` after every commit).
- `firestarter_fw` working tree: clean (`git status --porcelain` empty).
- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`: untouched by this plan
  (diff-checked before writing this file).
- `git -C firestarter_fw status -sb`: no upstream configured, confirming nothing was pushed.

---
*Phase: 199-what-the-rails-can-actually-deliver*
*Completed: 2026-09-19*
