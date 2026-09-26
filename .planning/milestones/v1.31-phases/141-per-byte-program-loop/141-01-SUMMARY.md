---
phase: 141-per-byte-program-loop
plan: 01
subsystem: logging
tags: [tri-repo, message-catalog, codegen, messages-toml, error-diagnostics, avr, gh-15]

# Dependency graph
requires:
  - phase: 140-parameter-table
    provides: eprom_params_t PROGMEM table + eprom_params_for() that plan 141-04's loop rewrite will read, and the 140-PREDICTIONS.md predict-then-commit-then-measure precedent this plan's 141-PREDICTIONS.md follows
provides:
  - "Three new ERROR-band message IDs -- 0xAE MSG_ERR_PULSE_TOO_WIDE (D-03 pre-flight refusal), 0xBD MSG_ERR_MAX_PULSES / 0xBE MSG_ERR_ENERGY_CAP (D-04 distinct budget-exhaustion diagnostics) -- authored canonically and synced+regenerated into both sub-repos"
  - "141-PREDICTIONS.md: falsifiable pre-measurement flash-delta (per target, signed), RAM-delta (exactly 0), and D-13 inventory-movement predictions, committed before plan 141-04 moves any eprom.cpp byte"
affects: [141-04-per-byte-loop-rewrite, 141-09-measurement-record, 144-close-reconciliation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Author once in the meta catalog, sync+regenerate into both sub-repos, verify independently via git diff --stat rather than trusting sync_to_subrepos.sh's own step-2/step-3 messages (both are diff -q \"$X\" \"$X\" tautologies)"
    - "Predict-then-commit-then-measure ordering for GC-sensitive flash-delta and inventory-count claims (140-PREDICTIONS.md precedent, reused verbatim for 141-PREDICTIONS.md)"

key-files:
  created:
    - .planning/phases/141-per-byte-program-loop/141-PREDICTIONS.md
  modified:
    - tools/catalog/messages.toml
    - firestarter/tools/catalog/messages.toml
    - firestarter/include/messages.h
    - firestarter_app/tools/catalog/messages.toml
    - firestarter_app/firestarter/messages.py

key-decisions:
  - "D-04: two distinct budget-exhaustion IDs (0xBD MSG_ERR_MAX_PULSES / 0xBE MSG_ERR_ENERGY_CAP) rather than one ID plus a reason-discriminator byte, so the host can tell the two limits apart without a second decode layer"
  - "MSG_INFO_RETRIES (0x51) and DBG_PULSE_DELAY_MISMATCH (0x15) left assigned but now unreferenced by firmware once plan 141-04 lands -- deleting an id risks reuse confusion for zero behavioural gain; the wording question is hand-off to Phase 146 / CLOSE-03"
  - "Committed each sub-repo's synced/generated files before running the firmware pytest leg (deviating from the plan's literal all-in-one-shell verify chain) because test_flash_path_record_sync.py's planted-mutation test asserts the WHOLE firestarter repo's git-porcelain is empty, unscoped to the file it actually tests -- this task's own legitimate uncommitted diff tripped that unrelated precondition; committing first (which the task's action already required) restored a clean tree and the same pytest leg then passed 244/244"

requirements-completed: []

coverage:
  - id: D1
    description: "Three new ERROR-band message IDs (0xAE MSG_ERR_PULSE_TOO_WIDE single-u32; 0xBD MSG_ERR_MAX_PULSES and 0xBE MSG_ERR_ENERGY_CAP, both [u24 hex_addr, u8]) added to the canonical meta catalog in id order with zero reordering, leaving exactly one free ERROR-band slot (0xBF); MSG_INFO_RETRIES/DBG_PULSE_DELAY_MISMATCH untouched"
    verification:
      - kind: other
        ref: "python3 -c tomllib load + assert count==76 + assert three ids/names/severity/params/free-slots (all passed, 'OK 76 messages, three new ERROR ids, one free slot left'); python3 tools/catalog/codegen.py --check -> 'OK: catalog valid (76 messages, version 1)'; git diff -- tools/catalog/messages.toml shows additions only; grep -c MSG_INFO_RETRIES|DBG_PULSE_DELAY_MISMATCH unchanged at 2 before/after"
        status: pass
    human_judgment: false
  - id: D2
    description: "Catalog synced + messages.h/messages.py regenerated in both sub-repos, verified independently (not via the sync script's own tautological success messages); no hand-edit; codegen.py byte-identical in all three copies; firmware pytest suite fully green with the new IDs present"
    verification:
      - kind: other
        ref: "bash tools/catalog/sync_to_subrepos.sh; git -C firestarter diff --stat -- include/messages.h tools/catalog/messages.toml (34 insertions/1 deletion, codegen.py 0-byte diff); git -C firestarter_app diff --stat -- firestarter/messages.py tools/catalog/messages.toml (61 insertions/1 deletion, codegen.py 0-byte diff); diff -q all three messages.toml copies -> byte-identical; grep confirms all three ids present in messages.h and messages.py (param_bytes=4,4,4); ruff check + ruff format --check on messages.py -> 'All checks passed!' / 'file already formatted'; cd firestarter && python3 -m pytest tests/ -q -o addopts=\"\" -> 244 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "141-PREDICTIONS.md committed in the meta repo, before any src/proms/eprom.cpp byte moves, with signed per-target flash-delta predictions against BASE-01, RAM delta predicted exactly 0, a numeric D-13 tier-1/tier-2 inventory-movement prediction, and a re-verified non-ancestry claim for 6fab4ea"
    verification:
      - kind: other
        ref: "python3 token/structure check on 141-PREDICTIONS.md -> 'OK predictions artifact: 224 lines, 21 signed byte figures'; git -C firestarter merge-base --is-ancestor 6fab4ea HEAD -> exit 1 ('OK: 6fab4ea is NOT an ancestor of HEAD'); git log --oneline -1 -- .planning/phases/141-per-byte-program-loop/141-PREDICTIONS.md resolves to 4c5d9172, an ancestor of every later commit; git -C firestarter log --oneline --all -- src/proms/eprom.cpp shows its last touch predates this phase entirely (a296195, Phase 89)"
        status: pass
    human_judgment: false

duration: 21min
completed: 2026-08-10
status: complete
---

# Phase 141 Plan 01: Message Catalog + Pre-Measurement Predictions Summary

**Three new ERROR-band message IDs (0xAE/0xBD/0xBE) authored in the canonical meta catalog and regenerated into both sub-repos, plus a falsifiable flash/RAM/D-13-inventory prediction for plan 141-04's loop rewrite -- committed before any `eprom.cpp` byte moves.**

## Performance

- **Duration:** 21 min
- **Started:** 2026-08-10T14:25:23Z
- **Completed:** 2026-08-10T14:46:00Z
- **Tasks:** 3
- **Files modified:** 6 (across 3 repos), 1 created

## Accomplishments
- Authored `MSG_ERR_PULSE_TOO_WIDE` (0xAE, D-03's pre-flight refusal) and the distinct `MSG_ERR_MAX_PULSES` (0xBD) / `MSG_ERR_ENERGY_CAP` (0xBE) pair (D-04's two budget limits) in `tools/catalog/messages.toml`, in id order, additions-only
- Synced and regenerated `firestarter/include/messages.h` (ID-only `#define`s) and `firestarter_app/firestarter/messages.py` (constants + `MessageDef` entries, `param_bytes=4` each), verified independently of the sync script's own tautological success messages, with all three `messages.toml` copies byte-identical and `codegen.py` at a zero-byte diff in both sub-repos
- Committed a 224-line, falsifiable `141-PREDICTIONS.md`: signed flash-delta predictions per AVR target against BASE-01 (with `uno328pb` named the binding constraint), an exact-zero RAM-delta prediction with its mechanical basis, and a numbered D-13 tier-1/tier-2 inventory-movement prediction (24 -> 33 sites, growth not shrinkage) -- all before plan 141-04 touches `eprom.cpp`

## Task Commits

Each task was committed atomically:

1. **Task 1: Author the three new ERROR-band IDs in the canonical meta catalog** - `ca544b42` (feat, meta repo)
2. **Task 2: Sync + regenerate into both sub-repos and verify the regen independently** - `cfe079b` (feat, firestarter repo) + `924f943` (feat, firestarter_app repo)
3. **Task 3: Commit the pre-measurement flash/RAM and D-13 inventory predictions** - `4c5d9172` (docs, meta repo)

**Plan metadata:** pending (docs: complete plan, this SUMMARY + STATE.md + ROADMAP.md, meta repo)

## Files Created/Modified
- `tools/catalog/messages.toml` (meta) - canonical catalog, +3 `[[messages]]` blocks (0xAE, 0xBD, 0xBE), additions only
- `firestarter/tools/catalog/messages.toml` - synced copy, byte-identical to meta
- `firestarter/include/messages.h` - regenerated, 3 new ID-only `#define`s, header count 73->76
- `firestarter_app/tools/catalog/messages.toml` - synced copy, byte-identical to meta
- `firestarter_app/firestarter/messages.py` - regenerated, 3 new constants + 3 `MessageDef` entries, ruff-clean
- `.planning/phases/141-per-byte-program-loop/141-PREDICTIONS.md` - new, pre-measurement predictions

## Decisions Made
- **D-04 (from CONTEXT.md, applied here):** distinct IDs for `max_pulses` vs energy-cap exhaustion rather than one ID + a reason byte -- the host holds no copy of `eprom_params_t`, so it cannot otherwise disambiguate 255-pulses-by-count from 250-pulses-by-energy.
- **Orphaned IDs left assigned, not deleted:** `MSG_INFO_RETRIES` (0x51) and `DBG_PULSE_DELAY_MISMATCH` (0x15) become caller-less the moment plan 141-04 removes the block-retry loop. Per the plan's explicit instruction, both stay assigned and unedited; their now-unreferenced status is recorded here for Phase 146 / CLOSE-03 to resolve the wording question.
- **Predicted signed flash deltas, not a vague "some growth":** +30 B (`uno`), +30 B (`uno328pb`), +18 B (`leonardo`), derived from an itemized adds/removes ledger read directly from the live `eprom.cpp` source (not recalled), with `uno328pb` flagged binding (only 6 of its 36 B budget predicted unused) and named uncertainty around AVR's 32-bit multiply/divide reclaim.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Reordered Task 2's commit before its own pytest verification leg**
- **Found during:** Task 2 (sync + regenerate)
- **Issue:** The plan's `<verify><automated>` block chains `sync_to_subrepos.sh` -> diff checks -> `pytest tests/` in one shell invocation, with no commit in between. Run exactly that way, `pytest` failed one test: `test_flash_path_record_sync.py::TestFlashPathRecordSync::test_planted_mutation_of_the_real_subset_is_detected` asserts `_git_porcelain(_FW_REPO_ROOT)` (the WHOLE firestarter repo's git status) is empty as its own self-check, unscoped to the one file (`platform/py32f071/FLASH-PATH-AND-PCB.md`) it actually tests. This task's own legitimate, in-progress sync diff (`include/messages.h`, `tools/catalog/messages.toml`) was the only thing dirtying the tree, and tripped that unrelated precondition (1 failed, 243 passed).
- **Fix:** Committed the synced/regenerated files in each sub-repo first (`cfe079b` in `firestarter`, `924f943` in `firestarter_app` -- both required by the task's own action text regardless of ordering), which returned the firestarter repo to a clean working tree, then re-ran the pytest leg. No test code or production code was touched.
- **Files modified:** none beyond what Task 2 already modified (`include/messages.h`, `tools/catalog/messages.toml` in `firestarter`; `firestarter/messages.py`, `tools/catalog/messages.toml` in `firestarter_app`)
- **Verification:** `cd /workspaces/firestarter && python3 -m pytest tests/ -q -o addopts=""` -> 244 passed, 0 failed, on the now-clean tree
- **Committed in:** `cfe079b`, `924f943` (the same Task 2 commits; no separate fix commit needed)

---

**Total deviations:** 1 auto-fixed (1 blocking / ordering, zero code changes)
**Impact on plan:** No scope creep, no code or test changes. The finding itself is worth carrying forward: `test_flash_path_record_sync.py`'s planted-mutation leg requires a fully clean `firestarter` working tree to pass, which makes it order-sensitive to any other uncommitted work in the same repo -- not just to its own planted mutation. Future plans that run this test mid-multi-file-change should commit first, or expect a false failure.

## Issues Encountered
None beyond the deviation above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- The three message IDs plan 141-04 needs to emit D-03's pre-flight refusal and D-04's two budget-exhaustion diagnostics exist, canonically and in both sub-repos' generated artifacts, ready for `LOG_ERROR_ID_U32`/`LOG_ERROR_ID_BYTES` call sites.
- `141-PREDICTIONS.md` is committed and citable by SHA (`4c5d9172`) for plan 141-09 to quote and reconcile once the loop rewrite lands.
- No blockers. `firestarter/src/proms/eprom.cpp` remains byte-unchanged (confirmed via git log), so plan 141-04 starts from the same state this plan's predictions were written against.

---
*Phase: 141-per-byte-program-loop*
*Completed: 2026-08-10*

## Self-Check: PASSED

All 7 claimed files found on disk (`141-PREDICTIONS.md`, `141-01-SUMMARY.md`, `tools/catalog/messages.toml` in all three repos, `firestarter/include/messages.h`, `firestarter_app/firestarter/messages.py`). All 5 claimed commit hashes found in their respective repos' history (`ca544b42`, `4c5d9172`, `743dc3f4` in meta; `cfe079b` in firestarter; `924f943` in firestarter_app).
