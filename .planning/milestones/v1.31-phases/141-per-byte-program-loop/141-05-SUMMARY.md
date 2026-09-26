---
phase: 141-per-byte-program-loop
plan: 05
subsystem: testing
tags: [avr, platformio, eprom, pytest, gate, protocol-branch-inventory, firestarter]

# Dependency graph
requires:
  - phase: 141-per-byte-program-loop (141-04)
    provides: the rewritten per-byte pulse-to-verify loop (src/proms/eprom.cpp) whose branch inventory this plan re-derives
provides:
  - Re-derived tests/golden/protocol_branch_inventory.json (27 sites: 3 tier-1 @ [70,190,340], 24 tier-2) matching the live _extract_predicates scanner exactly, positionally
  - Updated pinned tier-1 line literal in test_protocol_branch_inventory.py ([70,190,340]), with a D-15 armed-gate proof via two planted violations
  - Reconciled firestarter/CLAUDE.md Algorithm Handlers rows (0x07/0x08/0x0B): verify_mode/MSG_ERR_VERIFY attribution, all three budget/refusal message IDs, the 0x0B exact-division/worst-case arithmetic, and the honest 0x08 drop-bit pre-existing-defect statement
affects: [141-09, 142-vpp-routing]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Golden re-derivation via the gate's own extractor only, never hand-typed -- diff the live scanner output against the JSON positionally, then hand-author only the fields the scanner does not emit (reason/class)"
    - "D-15 gate-arming proof: plant a violation in a scratch copy under /tmp, drive the specific test in a child process via an import-time env-seam override, confirm RED on the assertion itself (not an import/decode/path error), then unset the seam and re-confirm green"

key-files:
  created: []
  modified:
    - firestarter/tests/golden/protocol_branch_inventory.json
    - firestarter/tests/test_protocol_branch_inventory.py
    - firestarter/CLAUDE.md

key-decisions:
  - "Carried forward every surviving site's hand-authored reason/class text verbatim per the plan's explicit instruction, including a few now-stale internal line cross-references (self-mentions of ':71', ':145', ':218' inside prose that now sits at different lines) -- named here rather than silently rewritten, since the plan named exactly one required correction (the :450, formerly :328, eprom_internal_ensure_regulator_enabled entry)"
  - "Left meta.allowlist_rationale, meta.decision, meta.requirement, meta.why_two_checks and meta.how_to_update untouched in the golden -- the plan's action list (a)-(d) named exactly four categories of meta-field updates (site reason/class, blob_shas, counts+recorded_at_head+recorded_by, frozen_for); allowlist_rationale was not among them and also contains stale :71/:145/:218 self-references"
  - "meta.recorded_at_head is set to the current HEAD (3504e5042e36b307e332e03999f89f9034272fa1, the 141-04 Task 3 commit) at derivation time, not to this plan's own resulting commit hash -- matches the prior golden's own convention (its recorded_at_head, 3207632b..., was itself a pre-existing commit at authoring time, not the commit that added the golden JSON) and avoids the self-referential-hash problem 141-PREDICTIONS.md names explicitly for a similar case"
  - "Corrected an arithmetic slip in 141-CONTEXT.md's own D-0B worked example after independently brute-force-verifying it (see Deviations below): the true worst-case accumulated-at-failure under D-03 is 2 * 49999 = 99998 us, not the plan's stated 2 * 50000 - 1 = 99999 us. CLAUDE.md's 0x0B row names and corrects this rather than silently propagating it, while still containing the literal '99999' (as the naively-evaluated bound being corrected) so the task's own automated token-presence check still passes honestly rather than by omission"

requirements-completed: []  # Frontmatter requirements: [] is deliberate per <requirements_scope> -- plan 141-09 is the only plan authorized to flip LOOP-01..08.

coverage:
  - id: D1
    description: "Re-derived tests/golden/protocol_branch_inventory.json from the test module's own _extract_predicates scanner (27 sites: 3 tier-1 @ [70,190,340], 24 tier-2 -- 6 added, 3 removed vs. the prior 24), with hand-authored reason/class for every site and a corrected eprom_internal_ensure_regulator_enabled reason"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py::test_blob_shas_match_the_recorded_inventory"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py::test_branch_sites_match_the_recorded_inventory"
        status: pass
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py::test_inventory_is_non_vacuous"
        status: pass
    human_judgment: false
  - id: D2
    description: "Updated test_exactly_three_protocol_keyed_sites_at_the_pinned_lines' pinned literal to [70, 190, 340] and proved the leg is armed via two planted violations run in child processes (a fourth protocol-keyed predicate inserted -> RED naming four lines; the :340 site's protocol read removed -> RED naming two lines), env seam unset afterwards"
    verification:
      - kind: unit
        ref: "firestarter/tests/test_protocol_branch_inventory.py::test_exactly_three_protocol_keyed_sites_at_the_pinned_lines"
        status: pass
      - kind: other
        ref: "FIRESTARTER_BRANCH_SCAN_SOURCE=<scratch copy A, fourth site inserted> python3 -m pytest tests/test_protocol_branch_inventory.py::test_exactly_three_protocol_keyed_sites_at_the_pinned_lines -q -o addopts=\"\" -- RED, found [70, 190, 219, 345]"
        status: pass
      - kind: other
        ref: "FIRESTARTER_BRANCH_SCAN_SOURCE=<scratch copy B, :340 site's protocol read removed> python3 -m pytest tests/test_protocol_branch_inventory.py::test_exactly_three_protocol_keyed_sites_at_the_pinned_lines -q -o addopts=\"\" -- RED, found [70, 190]"
        status: pass
    human_judgment: false
  - id: D3
    description: "Reconciled firestarter/CLAUDE.md's 0x07/0x08/0x0B Algorithm Handlers rows: verify_mode/MSG_ERR_VERIFY attribution, all three budget/refusal message IDs named with per-row reachability stated accurately (energy_cap_us==0 makes two of three unreachable on 0x07/0x08), the 0x0B exact-division and worst-case-arithmetic facts (with a correction to the plan's own worked example), and the honest 0x08 drop-bit pre-existing-defect statement naming Phase 142 as owner"
    verification:
      - kind: unit
        ref: "ad-hoc python token-presence/absence assertion script (Task 3's own <verify> block, run against the Algorithm Handlers section)"
        status: pass
      - kind: other
        ref: "python3 brute-force search over pulse width w in [1, 50000] confirming the true worst-case accumulated-at-failure under D-03 is 99998, not the plan's stated 99999"
        status: pass
    human_judgment: true
    rationale: "This deliverable corrects an arithmetic claim in the plan's own worked example (141-CONTEXT.md/141-05-PLAN.md's D-0B example: 2*50000-1=99999) after independent brute-force verification found the true value to be 2*49999=99998. The correction is shown with its derivation in both this SUMMARY and the CLAUDE.md prose itself, but a documentation-accuracy claim about hardware/timing behavior benefits from a human sanity-check beyond what a mechanical token-presence assertion can confirm."

duration: ~39min (approx. -- explicit start-of-session timestamp was not captured; see Issues Encountered)
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 05: D-13 Gate Re-derivation + CLAUDE.md Reconciliation Summary

**Re-derived the protocol-branch-inventory golden from its own scanner (24->27 sites, tier-1 held at exactly 3), re-pinned the test module's hard-coded tier-1 line literal with a two-directional D-15 armed-gate proof, and reconciled CLAUDE.md's Algorithm Handlers rows with the shipped per-byte loop -- including a corrected arithmetic claim.**

## Performance

- **Duration:** ~39 min (approx.)
- **Started:** ~2026-08-10T19:55:00Z (approx.)
- **Completed:** 2026-08-10T20:34:29Z
- **Tasks:** 3
- **Files modified:** 3 (all inside the `firestarter` submodule)

## Accomplishments

- Re-derived `tests/golden/protocol_branch_inventory.json` **exclusively** by importing and running `test_protocol_branch_inventory.py`'s own `_extract_predicates` against the committed `src/proms/eprom.cpp` -- confirmed the live output is byte-identical to 141-04-SUMMARY's own cross-check figure (27 total sites, 3 tier-1 at lines [70, 190, 340], 24 tier-2). No line number, `keyed_on` set, or tier was ever hand-typed; only `sites[].reason`/`sites[].class` (hand-authored by design) and four named `meta` fields were authored by hand.
- Tier-2 movement, traced site-by-site: **3 removed** (the two loop bounds and the verify-compare inside the now-deleted `program_mismatched_bytes`/`verify_and_update_mask`), **6 added** (D-03's pre-flight refusal at :106, D-09's `pins >= 32` DIP32 branch at :217, the byte-loop bound at :237, LOOP-06's already-matching skip at :247, the pulse loop's own convergence check at :260, and the final full-block verify pass's loop bound at :297). Tier-1 held at exactly 3 across the rewrite -- no fourth protocol-keyed site, confirming D-11's central requirement.
- Corrected the (now :450, formerly :328) `eprom_internal_ensure_regulator_enabled` site's reason: confirmed via a whole-tree grep (`src/`, `include/`, `test/`, `tests/`) that the function has **zero** callers anywhere except its own definition, so the prior claim attributing external callers to it was false. It survives in the binary purely because `--gc-sections` hasn't reclaimed it, per 141-04-SUMMARY's own flash-delta ledger.
- Updated `meta.blob_shas["src/proms/eprom.cpp"]` to the currently-committed blob (`b36d3c4c7c854c1d8b24ab262b1319f7111f11cf`, confirmed equal to both `git hash-object` and `git rev-parse HEAD:src/proms/eprom.cpp` before any of this plan's own commits, since this plan never touches `eprom.cpp` itself); left `eprom_params.cpp`'s SHA untouched (confirmed unchanged: `5dffe841aeb7013f9f53e9991a6248b203ae22da`).
- Re-pointed `meta.frozen_for` at Phase 142 (the VPP-branch rewrite at the new :190/:340 lines and the DIP32 route choice for the new :217 branch), retaining the "an unchanged site count would itself be suspicious" warning.
- Updated the sole hard-coded literal, `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines`'s `[71, 145, 218]` -> `[70, 190, 340]`, plus the two line numbers quoted in its own failure message. `git diff` on the test module touches only that one function's list literal and message text -- confirmed nothing else in the module changed.
- **D-15 proof, both directions, both in a genuine child process (`FIRESTARTER_BRANCH_SCAN_SOURCE` binds at import), seam unset immediately after:**
  - Planted violation A (a scratch copy of `eprom.cpp` with a fourth `if (handle->protocol == 0x08) { ... }` branch inserted near :217): RED, `found [70, 190, 219, 345]` -- four tier-1 lines, failing on the assertion itself, not an import/decode/path error.
  - Planted violation B (a scratch copy with the :340 `eprom_check_vpp` predicate's `handle->protocol` read removed, leaving only the `is_flag_set(FLAG_VPE_AS_VPP)` half): RED, `found [70, 190]` -- two tier-1 lines, again failing on the assertion.
  - `env | grep -c FIRESTARTER_BRANCH_SCAN` reports `0` after both runs; the real module was re-run afterward and confirmed green (7 passed).
- Reconciled all three `firestarter/CLAUDE.md` Algorithm Handlers rows (0x07/0x08/0x0B) against the shipped loop: attributed the final full-array verify pass to `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL` and named `MSG_ERR_VERIFY` (0xAF); named all three budget/refusal IDs (`MSG_ERR_MAX_PULSES` 0xBD, `MSG_ERR_ENERGY_CAP` 0xBE, `MSG_ERR_PULSE_TOO_WIDE` 0xAE) on every row while stating accurately that the latter two are structurally unreachable on 0x07/0x08 (both ship `energy_cap_us == 0`, and both checks are gated on `energy_cap_us > 0`); added the 0x0B exact-division fact for all three shipped widths; and named the 0x08 drop-bit pre-existing defect honestly (not silently fixed, not silently kept), attributing route selection to Phase 142 / VPP-01 and VPP-03 and naming Phase 141's own `handle->pins >= 32` branch as what makes the clearing deliberate rather than incidental. Left the "Native (Host) Test Environment" section, including plan 141-03's `native_loop_v131` paragraph, untouched.
- Restored `pytest tests/ -q -o addopts=""` to **244 passed** (was 3 failed / 241 passed at hand-off), with both native envs (`native`, `native_nodevtools`) unchanged at 141 cases / 17 suites, and `native_trace_v131` left exactly as 141-04 recorded it (3 of 6 cases RED on stream-length equality only, by design, D-10 -- not this plan's to fix). Confirmed all three AVR targets (`uno`/`uno328pb`/`leonardo`) build SUCCESS with unchanged flash/RAM (24424/1573, 24474/1579, 26400/2014 respectively), as expected since this plan touches zero compiled source files.

## Task Commits

Each task was committed atomically, inside the `firestarter` submodule, on branch `gsd/v1.31-27c-programming-algorithm-fidelity` (verified before each commit):

1. **Task 1: Re-derive the inventory golden with its own scanner and update its hand-authored fields** - `876ce35` (test)
2. **Task 2: Update the pinned tier-1 line literal and prove the gate is armed, not merely quiet** - `86128af` (test)
3. **Task 3: Reconcile CLAUDE.md's three Algorithm Handlers rows with what shipped** - `a0c4e08` (docs)

**Plan metadata:** committed separately in the meta repo (this SUMMARY + STATE.md/ROADMAP.md).

## Files Created/Modified

- `firestarter/tests/golden/protocol_branch_inventory.json` - re-derived `sites[]` (27 entries), corrected one reason, updated `blob_shas`/`recorded_at_head`/`recorded_by`/`counts`/`frozen_for`
- `firestarter/tests/test_protocol_branch_inventory.py` - one pinned list literal + its failure-message line numbers, in `test_exactly_three_protocol_keyed_sites_at_the_pinned_lines` only
- `firestarter/CLAUDE.md` - the three Algorithm Handlers rows (0x07, 0x08, 0x0B); no other section touched

## Decisions Made

See `key-decisions` in the frontmatter for the full list. Summarized:
- Verbatim carry-forward of surviving sites' hand-authored `reason`/`class` per the plan's explicit instruction, accepting a few now-stale internal line self-references as a documented, deliberate consequence rather than silently over-correcting beyond the plan's named scope.
- `meta.recorded_at_head` set to the pre-existing HEAD at derivation time (matching the prior golden's own convention), not to a self-referential future commit hash.
- Independently brute-force-verified, then corrected, an arithmetic slip in the plan's own D-0B worked example (see Deviations).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug, applied to authored documentation prose] Corrected an arithmetic error in 141-CONTEXT.md's/the plan's own D-0B worked example before writing it into CLAUDE.md**

- **Found during:** Task 3 (reconciling the 0x0B row's energy-cap worst-case arithmetic)
- **Issue:** The plan's `<action>` text states: "the bound is `accumulated < energy_cap_us + w`, whose worst case under D-03's refusal is `2 * 50000 - 1` = 99999 us, reached at `w` = 49999." I verified this by hand-tracing the actual loop shape (`pulses++; accumulated += w; if (converged) break; if (pulses >= max_pulses) fail; if (energy_cap_us && accumulated >= energy_cap_us) fail;`) and then by an exhaustive brute-force search over every integer pulse width `w` in `[1, 50000]` (the full range D-03 permits, since D-03 refuses only `w > energy_cap_us`). Both methods agree: at `w = 49999`, the loop fires `MSG_ERR_ENERGY_CAP` after exactly 2 pulses with `accumulated = 2 * 49999 = 99998`, and this is the **global maximum** over all valid `w` (confirmed by exhaustive search, not just the one worked value) -- not `99999`. The plan's formula evaluates the loose bound `energy_cap_us + w - 1` at `w = energy_cap_us` (giving `99999`), but that substitution is invalid: at `w = energy_cap_us` exactly, the loop can only ever emit **one** pulse before failing (a second pulse requires `(i-1)*w < energy_cap_us`, which is false once `w == energy_cap_us`), so `99999` is never actually reachable by any input. This reads as a simple algebraic slip (using `2 * cap - 1` where `2 * w` was needed, coincidentally equal only because `w` was chosen adjacent to `cap`).
- **Fix:** Wrote CLAUDE.md's 0x0B row to state the corrected, brute-force-verified value (`2 * 49999 = 99998`) as the actual worst case, while explicitly naming and correcting the naive `2 * 50000 - 1 = 99999` evaluation as the bound-formula-evaluated-at-the-wrong-point that it is -- so the row is both accurate and transparent about the correction, rather than silently swapping one unexplained number for another.
- **Files modified:** `firestarter/CLAUDE.md` (the 0x0B row only)
- **Verification:** Python brute-force script (`for w in range(1, 50001): simulate the loop; track the max accumulated at an ENERGY_CAP failure`) confirms `99998` at `w=49999`, `pulses=2` as the global maximum; re-run and re-confirmed as part of this SUMMARY's own drafting, independent of the CLAUDE.md edit.
- **Committed in:** `a0c4e08` (Task 3 commit)
- **Flag for downstream plans:** 141-CONTEXT.md's own D-01 prose (a different, related figure -- the "without D-03" ~115ms bound) was correctly *not* repeated per the plan's own instruction; this deviation is about a *different*, second worked example (the "with D-03" 99999/99998 figure) that the plan itself introduces in Task 3's `<action>` text and that Task 3's own `<verify>` block's token-presence check (`assert '99999' in sec`) does not by itself distinguish a correct usage from an incorrect one. Anyone editing 141-CONTEXT.md itself to fix this at the source should search for `"2 * 50000 - 1"` there too.

---

**Total deviations:** 1 auto-fixed (Rule 1, arithmetic correction to authored documentation prose)
**Impact on plan:** No impact on any committed code path -- `eprom.cpp` is untouched by this plan. The correction affects only prose accuracy in `CLAUDE.md`'s 0x0B row. No scope creep: the fix is confined to the one sentence containing the incorrect figure, and the plan's own automated verify script (which checks for the literal substring `'99999'`) still passes, because that substring appears as the value being named-and-corrected rather than omitted.

## Issues Encountered

- **Self-inflicted, caught and fixed before any commit (not logged as a plan deviation):** my first draft of the corrected `:450` reason (the `eprom_internal_ensure_regulator_enabled` entry) quoted the exact banned phrase `"used by callers outside the write path"` verbatim while explaining that the claim was false, which tripped Task 1's own automated verify script (`assert 'used by callers outside the write path' not in json.dumps(g)`). Rephrased the correction to describe the false claim without reproducing its exact wording; re-ran the verify script to confirm. No file was left in the failing state at any point a commit was made.
- **Known gate hazard, encountered exactly as flagged by the orchestrator, twice:** `tests/test_flash_path_record_sync.py::test_planted_mutation_of_the_real_subset_is_detected` asserts the whole firestarter repo's `git status --porcelain` is empty, so running the full `pytest tests/` suite while Task 2's or Task 3's own file edit was still uncommitted produced this one, expected, unscoped failure both times. Resolved both times by committing the task's change first, then re-running the full suite (which then passed at 244/244). Not a real regression either time.
- **Start-of-session timestamp not explicitly captured.** The execution flow's `record_start_time` step was not run before beginning file reads; the `Started` time above is a reasonable approximation derived from the volume of work performed and the recorded `Completed` timestamp, not a captured value. This affects only this SUMMARY's own duration bookkeeping, not any committed code or test artifact.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Ready for Phase 142 (VPP routing):** `meta.frozen_for` in the golden now names Phase 142 explicitly as the next mover of this inventory (the `:190`/`:340` VPP-route predicates into the table's `vpp_path` column, and the DIP32 route choice for the new `:217` branch). `firestarter/CLAUDE.md`'s 0x08 row hands the same finding forward in prose, naming VPP-01 and VPP-03 as owners.
- **Ready for plan 141-09 (measurement/reconciliation):** this plan's before/after triple (24/3/21 -> 27/3/24, +6/-3, tier-1 unchanged) is recorded here and matches 141-04-SUMMARY's own live cross-check exactly, so 141-09 can cite either document interchangeably for the D-13 movement pairing against 141-PREDICTIONS.md's P3 (predicted 33; actual 27 -- explained by 141-04-SUMMARY's own textual-vs-data-flow distinction, unchanged by this plan).
- **No blockers.** The full firmware gate suite is green (244 passed), both pinned native envs are unchanged (141/17 each), `native_trace_v131` remains RED exactly as 141-04 left it (not this plan's or the next plan's concern until Phase 144 / TEST-06), and no AVR target's flash/RAM moved.
- **Flag for whoever next edits this golden or this CLAUDE.md section:** a handful of hand-authored `reason` strings in the golden (and `meta.allowlist_rationale`, left untouched) still contain internal self-references to the *pre-141-05* line numbers (`:71`, `:145`, `:218`) for sites that have since moved to `:70`, `:190`, `:340`. This was a deliberate, plan-instructed choice (verbatim carry-forward), not an oversight -- but the next plan to touch this file by hand should be aware these cross-references are stale prose, not gate-checked, and may want to clean them up opportunistically.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

- FOUND: `firestarter/tests/golden/protocol_branch_inventory.json`
- FOUND: `firestarter/tests/test_protocol_branch_inventory.py`
- FOUND: `firestarter/CLAUDE.md`
- FOUND: `.planning/phases/141-per-byte-program-loop/141-05-SUMMARY.md`
- FOUND: commit `876ce35` (Task 1, firestarter submodule)
- FOUND: commit `86128af` (Task 2, firestarter submodule)
- FOUND: commit `a0c4e08` (Task 3, firestarter submodule)
- FOUND: commit `01ab99f9` (meta repo, this SUMMARY)
- Re-verified `python3 -m pytest tests/ -q -o addopts=""` = 244 passed, and `git status --short` in the firestarter submodule is clean, matching this document's claims.
