---
phase: 194-real-page-size-reaches-the-firmware
plan: 01
subsystem: firmware-protocol
tags: [flash-write, page-size, protocol-0x05, messages-catalog, chip-database, generator]

requires: []
provides:
  - "Bus recorder cap raised to 4096 (from 256) behind #ifndef HOST_STUBS_MAX_RECORDING, plus bus_recording_saturated()"
  - "MSG_ERR_FL4_PAGE_SIZE minted at 0xBF (ERROR band), synced into both sub-repos"
  - "build_db.py emits page_size for every row whose OWN upstream protocol_id is 0x0D or 0x05, with a fail-closed power-of-two-in-[1,512] assertion before any database write"
  - "Regenerated chip_database.json: 746 rows, 45 carry programming.page_size (18 native 0x0D + 27 native 0x05), 25 rows gained the key"
  - "flash_5v_page_write_execute resolves handle->page_size through a validated mask or refuses with MSG_ERR_FL4_PAGE_SIZE, writing nothing"
  - "Native boundary case proving W29C512 (mem_size 65536, page_size 128) uses its real 128-byte page, not a capacity-derived 64-byte one, plus a refusal case proving zero register writes"
affects: [195-partial-unaligned-write, 194-02, 194-03, 194-04, 194-06]

actuals:
  tokens: 6378
  tasks: 3
  commits: 7

tech-stack:
  added: []
  patterns:
    - "Mask-based page arithmetic (address & page_mask) replacing runtime '%' by a variable divisor, matching eeprom_28c.cpp's eeprom28c_page_mask reference shape"
    - "Resolve-once-or-refuse at the top of operation_main, never in write_init, so native suites that drive operation_main directly still observe the refusal"
    - "Provenance-keyed generator emit: read the row's OWN upstream protocol_id captured before classify() reassigns it, never the resolved/promoted algorithm"

key-files:
  created: []
  modified:
    - firestarter_fw/test/native/avr/_shared/host_stubs_common.inc
    - tools/catalog/messages.toml
    - firestarter_fw/include/messages.h
    - firestarter_app/firestarter/messages.py
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/data/chip_database.json
    - firestarter_fw/src/proms/flash_5v_page.cpp
    - firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp

key-decisions:
  - "D-01/D-02: _PAGE_SIZE_BY_PART (2 entries: W29C040->256, W29C020->128, both output-neutral) is deleted. The emit arm now uses one condition, keyed on the row's own upstream protocol_id being 0x0D or 0x05."
  - "D-03: fail-closed assertion added before the JSON write -- any emitted page_size that is not a power of two in [1,512] aborts the generator run with no database written."
  - "D-05/D-06: flash_5v_page_page_size() (capacity-derived) deleted outright, not gated. flash_5v_page_write_execute now resolves handle->page_size via flash_5v_page_mask() or refuses with MSG_ERR_FL4_PAGE_SIZE, before any address is set or byte written."
  - "U2: 0xBF spent deliberately as the last free ERROR-band id -- not widened into 0xC0-0xDF this phase."
  - "U4: FLASH_5V_PAGE_SIZE_MAX (512) is a #define local to flash_5v_page.cpp, not hoisted into include/."

patterns-established:
  - "Native bus-recorder saturation guard (bus_recording_saturated()) is now a required assertion on any boundary case that could plausibly exceed the recording cap."

requirements-completed: []

coverage:
  - id: D1
    description: "Native bus recorder raised to 4096 entries behind #ifndef, exposing bus_recording_saturated(). All 194 pre-existing native cases, in both pinned envs, stay green at the new default."
    verification:
      - kind: unit
        ref: "pio test -e native && pio test -e native_nodevtools (194/194 succeeded, both envs)"
        status: pass
    human_judgment: false
  - id: D2
    description: "MSG_ERR_FL4_PAGE_SIZE minted at 0xBF, synced into firestarter_fw/include/messages.h and firestarter_app/firestarter/messages.py, sync proven idempotent post-commit."
    verification:
      - kind: unit
        ref: "python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check; bash tools/catalog/sync_to_subrepos.sh (SYNC-IDEMPOTENT)"
        status: pass
    human_judgment: false
  - id: D3
    description: "build_db.py emits page_size for every row whose own upstream protocol_id is 0x0D or 0x05. It carries no curated table and applies a fail-closed power-of-two assertion. The regenerated database carries 45 carriers across 746 rows. 25 rows gained the field relative to before, and no other field moved."
    verification:
      - kind: unit
        ref: "python3 -c DB-OK assertion (rows=746 carriers=45 rawkey=744 alg5=27 values=[64,128,256,512])"
        status: pass
    human_judgment: false
  - id: D4
    description: "W29C512,W29EE512's wire dict emits page-size 128 (previously absent entirely)."
    verification:
      - kind: unit
        ref: "EpromDatabase(skip_local_override=True).convert_to_programmer(...) -> WIRE-OK page-size=128"
        status: pass
    human_judgment: false
  - id: D5
    description: "flash_5v_page_write_execute consumes handle->page_size through a validated mask. A write with no resolvable page size refuses with MSG_ERR_FL4_PAGE_SIZE and performs zero register writes."
    verification:
      - kind: unit
        ref: "test/native/avr/test_val_5v_page/test_val_5v_page.cpp::test_5v_page_write_execute_refuses_with_no_page_size"
        status: pass
    human_judgment: false
  - id: D6
    description: "Native boundary case proves the firmware uses W29C512's real 128-byte page (exactly one SDP signature over 128 bytes), not a capacity-derived 64-byte one, with saturation proven absent."
    verification:
      - kind: unit
        ref: "test/native/avr/test_val_5v_page/test_val_5v_page.cpp::test_5v_page_write_execute_page_starts_at_real_page_not_derived"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-09-15
status: complete
---

# Phase 194 Plan 01: Real Page Size Reaches the Firmware (Tracer) Summary

**W29C512's real 128-byte page now travels from the generator through the regenerated database and the existing wire seam into `flash_5v_page_write_execute`'s mask arithmetic. A `0x05` write with no resolvable page size refuses with `MSG_ERR_FL4_PAGE_SIZE` instead of guessing.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-09-15T13:38:17Z
- **Tasks:** 3/3
- **Files modified:** 8

## Accomplishments

- Raised the native bus recorder's silent-truncation cap from 256 to 4096 (behind `#ifndef HOST_STUBS_MAX_RECORDING`) and added `bus_recording_saturated()`, closing the measured vacuity hazard before any boundary assertion depends on it. All 194 pre-existing native cases stayed green at the new default, in both pinned envs.
- Minted `MSG_ERR_FL4_PAGE_SIZE` at `0xBF` (the last free ERROR-band id, per U2) carrying one `u16` param echoing the rejected value, and synced it into both sub-repos with a proven-idempotent second sync run.
- Deleted `_PAGE_SIZE_BY_PART` (the hand-curated page-size table) from `build_db.py` and collapsed the two-arm `page_size` emit condition to one: emit the row's own upstream `raw_page_size` when its own upstream `protocol_id` is `0x0D` or `0x05`. Added a fail-closed assertion before any database write: an emitted `page_size` that is not a power of two in `[1, 512]` aborts the run with no database written.
- Regenerated `chip_database.json`. Totals: 746 rows. Exactly 45 rows carry `programming.page_size` (18 upstream-native `0x0D` plus 27 upstream-native `0x05`). Exactly 744 rows still carry `infoic_page_size_raw`. Exactly 25 rows gained the `page_size` key relative to the prior database. No other field on any row moved. `W29C512,W29EE512` now carries `page_size` 128, and its wire dict emits `page-size: 128` where it previously emitted nothing at all.
- Deleted `flash_5v_page_page_size()` (the capacity-derived helper) from `flash_5v_page.cpp` outright. `flash_5v_page_write_execute` now resolves `handle->page_size` through a new validator, `flash_5v_page_mask()`. The validator rejects `0` before the power-of-two test, and accepts a power of two up to `FLASH_5V_PAGE_SIZE_MAX` 512. On failure it refuses with `MSG_ERR_FL4_PAGE_SIZE`, sets `RESPONSE_CODE_ERROR`, and returns before any address is set or byte written. Both `%`-by-variable-divisor sites were converted to the mask form.
- Added a native boundary case driving `(mem_size 65536, page_size 128)`, W29C512's real geometry. It asserts exactly one SDP signature over 128 bytes. The old capacity-derived 64-byte page would have produced a second signature at byte 64. `!bus_recording_saturated()` and `RESPONSE_CODE_OK` serve as non-vacuity controls. Added a refusal counterpart asserting `RESPONSE_CODE_ERROR` and zero register writes when `page_size` is `0`. Repaired the two pre-existing write-path cases' shared fixture, now setting `page_size = 256` (W29C040's real page), so they stay green under the new fail-closed behavior.
- `pio run -e uno` (21616/32256 B) and `pio run -e leonardo` (23734/28672 B) both succeed within the bootloader-guard ceilings. Both native envs report 196/196 succeeded (194 pre-existing + 2 new). `firestarter_fw`'s `pytest tests/` reports 301/301 passed on a committed tree.

## Task Commits

Each task was committed atomically, landing in the named sub-repos per `commits_land_in`:

1. **Task 1: Fork both sub-repos onto v1.39, close the recorder's silent-truncation hazard** -- both sub-repos were already on `v1.39-protocol-0x05-write-correctness` off `origin/beta` at spawn time (no branch-creation commit needed). `firestarter_fw@99ec694` (test)
2. **Task 2: Mint MSG_ERR_FL4_PAGE_SIZE at 0xBF and sync into both sub-repos** -- `firestarter_fw@948ebdd` (feat, messages.h), `firestarter_app@b43ad45` (feat, messages.py), meta `e642cccb` (feat, catalog + both gitlinks)
3. **Task 3: The real page size reaches the firmware -- W29C512 end to end** -- `firestarter_fw@2441f36` (fix, handler + native suite), `firestarter_app@859109d` (feat, generator + regenerated database), meta `9334ae11` (fix, both gitlinks)

**Plan metadata:** committed below (this SUMMARY only -- STATE.md/ROADMAP.md are owned by the orchestrator in this repo, per the shared_artifact_rule override)

## Files Created/Modified

- `firestarter_fw/test/native/avr/_shared/host_stubs_common.inc` - bus recorder cap raised to 4096 behind `#ifndef`, `bus_recording_saturated()` added
- `tools/catalog/messages.toml` - `MSG_ERR_FL4_PAGE_SIZE` stanza at `0xBF`
- `firestarter_fw/include/messages.h` - regenerated (codegen output, not hand-edited)
- `firestarter_app/firestarter/messages.py` - regenerated (codegen output, not hand-edited)
- `firestarter_app/tools/build_db.py` - `_PAGE_SIZE_BY_PART` deleted. Emit arm collapsed to one provenance-keyed condition. Fail-closed power-of-two assertion added before the JSON write.
- `firestarter_app/firestarter/data/chip_database.json` - regenerated (generator output, not hand-edited). 45 `page_size` carriers, 25 gained.
- `firestarter_fw/src/proms/flash_5v_page.cpp` - capacity-derived helper deleted. `flash_5v_page_mask()` validator added. Resolve-or-refuse at the top of `write_execute`. Both `%` sites converted to mask form.
- `firestarter_fw/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` - fixture repaired (`page_size = 256`). `count_sdp_signatures()` generalized from the old boolean `recording_contains_sdp_signature()`. Two new cases added: boundary and refusal.

## Decisions Made

- **`requirements-completed: []`** deliberately, even though this plan's frontmatter names `[PAGE-01, PAGE-02]`. Per the plan's own prohibitions and the phase's Multi-Source Coverage Audit, PAGE-01 and PAGE-02 are each measured and closed across plans 01 through 06. Plan 06 is the one that flips the REQUIREMENTS.md checkboxes, after all software evidence exists. Marking them complete here would repeat a premature-completion mistake this project has made before.
- Followed D-01 through D-06 and U2/U4 as specified. No architectural deviations (Rule 4) were needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - dead code / falsified comment] Removed the now-dead `_canon` hoist and its falsified comment**
- **Found during:** Task 3, Step 1(b) (the emit-arm collapse)
- **Issue:** `_canon = name.split(",")[0].split("@")[0].strip()` was hoisted solely to serve the two-arm `_PAGE_SIZE_BY_PART[_canon]` lookup the plan's D-01/D-02 rewrite removes. Once the emit arm collapsed to the single `_upstream_proto_id in (0x0D, 0x05)` condition, `_canon` had zero remaining readers, and its comment's own claim ("hoisted here because the page_size emit arm below needs it in both its lookup and its guard condition") became false the moment the lookup it referred to was deleted.
- **Fix:** Deleted the `_canon` assignment and its comment. Not itemized in the plan's own "DELETED" artifact table, but a direct, necessary consequence of D-01 -- leaving it in would have been dead code sitting beside a comment describing a need that no longer exists, which the project's own hard rule against stale/falsified comments forbids.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** `python3 -m py_compile tools/build_db.py` succeeds. `grep -n _canon tools/build_db.py` returns nothing. Full regeneration and the DB-OK/WIRE-OK assertions still pass.
- **Committed in:** `firestarter_app@859109d`

**2. [Operational recovery, not a code deviation] `gsd-tools query commit` twice created and switched to a stray `gsd/v1.39-...-activated-2026-09-15` branch**
- **Found during:** the meta-repo gitlink/catalog commits in Tasks 2 and 3
- **Issue:** `gsd_run query commit` (used for the meta-repo-only commits, since `commit-to-subrepo` reported `tools/catalog/messages.toml` as unmatched) auto-created and switched HEAD to a new `gsd/v1.39-protocol-0x05-write-correctness-activated-2026-09-15` branch off the same commit, rather than committing on the already-checked-out `v1.39-protocol-0x05-write-correctness`. This is a known project-level tool behavior (it scrapes ROADMAP prose for a milestone-activation branch name), not something the plan or this execution introduced.
- **Fix:** Both times, verified the stray branch was local-only, with no upstream tracking and no push. Fast-forwarded `v1.39-protocol-0x05-write-correctness` onto it, switched back to that branch, and deleted the now-redundant stray branch. No commits, sub-repo state, or history were lost or altered. Only the branch pointer moved.
- **Files modified:** none (git refs only)
- **Verification:** `git branch --show-current` on the meta repo reads `v1.39-protocol-0x05-write-correctness` after each recovery. `git log --oneline` shows the expected linear commit sequence, with no stray branch remaining (`git branch -a` no longer lists it).
- **Committed in:** N/A (branch-pointer correction, not a content commit)

---

**Total deviations:** 1 auto-fixed (dead code/comment cleanup), plus 1 operational git-branch recovery (not a code change).
**Impact on plan:** Both are hygiene-only. No scope creep, no behavioral change beyond what the plan specified.

## Issues Encountered

- **A fifth host gate went RED beyond the four Step 6 named.** `firestarter_app/tests/test_protection_status_catalog.py::test_error_band_last_free_id_unspent` asserts `0xBF not in CATALOG`. It is a guard from an earlier phase (151-DESIGN.md) meant to catch the ERROR band's last free id being spent without anyone noticing. Task 2 spends `0xBF` deliberately per U2, which is exactly the event this guard exists to flag. It is not caused by the database regeneration the plan's Step 6 disclosure was written about. This is a correctly-attributed, anticipated consequence of U2 and RESEARCH C-11 (the phase's own coverage table lists "U2 -- 0xBF is spent here deliberately... plan 06 files it as a backlog item"). Closing or updating this guard belongs to plan 06, not this plan. Recorded here so the RED count is honestly five, not four, going into the next plan.
- The plan's `<precondition>` for Task 3 checks that `curl ... https://gitlab.com` returns exactly `200`. The actual response, without following redirects, is `301` (gitlab.com redirects to itself over a canonicalizing hop). `curl -L` shows genuine reachability and returns `200`. Treated as met. The precondition's intent, that network egress exists, was satisfied. The literal status-code text in the plan was imprecise about gitlab.com's redirect behavior.
- `command -v ruff` (Task 2's precondition) does not resolve on the bare devcontainer `$PATH`. `ruff` exists inside `firestarter_app/.venv311/bin/`. That directory was prepended to `PATH` for the sync-script invocation only. This is not a repo change.
- `firestarter_fw`'s `pytest` (a second, CI-covered Python test tree per this repo's CLAUDE.md) needed a throwaway venv (`/tmp/fw-pytest-venv`, `pip install pytest`) since the devcontainer's system Python has no `pytest` installed and this repo carries no pinned venv for it, unlike `firestarter_app`'s documented `.venv311` requirement.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The tracer is proven end to end for `W29C512,W29EE512`: generator -> regenerated database -> wire dict -> firmware mask arithmetic -> native boundary assertion, all green.
- Four host gates are RED by design, each named for its closing plan:
  - `tests/test_page_size_invariants.py` (2 tests) -> plan 03
  - `tests/test_vcc_margin_rail.py` (1 test) -> plan 03
  - `tests/test_chip_database_field_inventory.py` (1 test, backed by the golden `tests/golden/chip_database_field_inventory.json`) -> plan 03
  - `tests/test_wire_dict_equivalence.py` (2 tests) -> plan 04
- A fifth RED, not named in this plan's own Step 6 but anticipated at the phase level (U2): `tests/test_protection_status_catalog.py::test_error_band_last_free_id_unspent` -> plan 06 (files the ERROR-band-exhaustion backlog item and updates this guard).
- Plans 02-07 can now widen the measurement (all 27 `algorithm: 5` parts, the host 27-row test, the wire-dict delta layer, the 27-row record, and the W29C512 bench leg) on top of a working single-path seam.
- `.planning/REQUIREMENTS.md` is untouched by design -- PAGE-01/PAGE-02 stay open until plan 06.

## Self-Check: PASSED

All 8 modified/created source files are present on disk, verified with `[ -f ... ]`. All 7 commit hashes are present in their respective repos' `git log --oneline --all`: `firestarter_fw@99ec694`, `firestarter_fw@948ebdd`, `firestarter_fw@2441f36`, `firestarter_app@b43ad45`, `firestarter_app@859109d`, meta `e642cccb`, meta `9334ae11`.

---
*Phase: 194-real-page-size-reaches-the-firmware*
*Completed: 2026-09-15*
