---
quick_id: 260820-a7w
subsystem: firmware
tags: [platformio, avr, atmelavr, minicore, size-baseline, merge-05, flash-ceiling]

requires:
  - phase: 149 (dual-repo lockstep, page-size seam)
    provides: the live baseline's post-149 flash/RAM figures and the two-exemption
      MERGE-05 band mechanism this task reuses unchanged
provides:
  - Both flash-limit guards (PlatformIO's reported ceiling and the recorded
    `flash_total` invariant in both baselines) now report each AVR MCU's real
    32768 B flash size
  - `zero_bootloader_reserve.py`, a `pre:` SCons hook that neutralizes the
    atmelavr MiniCore builder's bootloader-size subtraction on `uno328pb`
  - Three committed cold-build logs as the transcription source for both
    baseline edits
  - Two new fixture families (`captured_build_fullflash_*`,
    `merge05_*_fullflash_*` / `planted_*_fullflash*`) that keep
    `tests/test_check_size_baseline.py` green after both baselines' flash_total
    moved
affects: [firmware-size-baseline, merge-05-band-gate, avr-platformio-config]

tech-stack:
  added: []
  patterns:
    - "PlatformIO `pre:` extra_script guarded on `env['PIOENV']` to scope a
      board-specific manifest override without touching other envs"
    - "Board-identity vs growth-axis split in a frozen comparison baseline:
      `flash_total` may move when the silicon ceiling changes; `flash_used`/
      `ram_used` may not, without separate adjudication"

key-files:
  created:
    - firestarter/zero_bootloader_reserve.py
    - .planning/quick/260820-a7w-make-the-flash-limit-guards-to-be-the-ac/260820-a7w-cold-uno.log
    - .planning/quick/260820-a7w-make-the-flash-limit-guards-to-be-the-ac/260820-a7w-cold-uno328pb.log
    - .planning/quick/260820-a7w-make-the-flash-limit-guards-to-be-the-ac/260820-a7w-cold-leonardo.log
    - firestarter/tests/fixtures/captured_build_fullflash_uno.log
    - firestarter/tests/fixtures/captured_build_fullflash_uno328pb.log
    - firestarter/tests/fixtures/captured_build_fullflash_leonardo.log
    - firestarter/tests/fixtures/planted_size_baseline_flash_regression_fullflash.log
    - firestarter/tests/fixtures/merge05_base01_anchor_fullflash_uno.log
    - firestarter/tests/fixtures/merge05_base01_anchor_fullflash_uno328pb.log
    - firestarter/tests/fixtures/merge05_base01_anchor_fullflash_leonardo.log
    - firestarter/tests/fixtures/merge05_defect_fix_fullflash_uno.log
    - firestarter/tests/fixtures/merge05_defect_fix_fullflash_uno328pb.log
    - firestarter/tests/fixtures/merge05_defect_fix_fullflash_leonardo.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_uno_over_band_fullflash.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_leonardo_growth_fullflash.log
    - firestarter/tests/fixtures/planted_size_baseline_policy_ram_moved_fullflash.log
  modified:
    - firestarter/platformio.ini
    - firestarter/scripts/baseline/size_baseline.json
    - firestarter/scripts/baseline/size_baseline_base01.json
    - firestarter/tests/test_check_size_baseline.py
    - firestarter/tests/fixtures/README.md

key-decisions:
  - "Operator-accepted trade: all three AVR ceilings report the real 32768 B MCU size, forfeiting the linker's protection over each target's bootloader region (uno 512 B optiboot, uno328pb 384 B urclock, leonardo 4096 B Caterina); no compensating guard was added by design."
  - "Operator ruling on BASE-01: flash_total (board identity) moves to 32768 on all three targets; flash_used/ram_used (growth axis) and all five MERGE-05 band/exemption literals stay frozen, so --policy merge05 stays a usable gate instead of red-by-design."

requirements-completed: [QUICK-260820-a7w]

coverage:
  - id: D1
    description: "PlatformIO reports 32768 B flash ceiling on all three AVR targets, transcribed from real cold rebuilds"
    requirement: QUICK-260820-a7w
    verification:
      - kind: integration
        ref: ".planning/quick/260820-a7w-make-the-flash-limit-guards-to-be-the-ac/260820-a7w-cold-{uno,uno328pb,leonardo}.log (cold `pio run`, `from 32768 bytes`, no TypeError)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Recorded flash_total invariant (live baseline) moved in lockstep, transcribed from the cold logs, growth axis unmoved"
    requirement: QUICK-260820-a7w
    verification:
      - kind: unit
        ref: "check_size_baseline.py default mode against the three cold logs, exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "BASE-01's board-identity figure moved by operator ruling; --policy merge05 observed passing with full band decomposition"
    requirement: QUICK-260820-a7w
    verification:
      - kind: integration
        ref: "check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json against the three cold logs: exit 0, +306<=306=band0+exempt96+seam210 (leonardo), +306<=370=band64+exempt96+seam210 (uno, uno328pb), +2<=2=seam2"
        status: pass
    human_judgment: false
  - id: D4
    description: "Nine stranded test legs severed onto fullflash fixture families; full firmware suite green on a committed tree"
    requirement: QUICK-260820-a7w
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_check_size_baseline.py -q (14 passed) and python3 -m pytest tests/ -q (315 passed), both on a porcelain-clean, committed tree"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-08-20
status: complete
---

# Quick Task 260820-a7w: Make the Flash-Limit Guards Report the Real MCU Size — Summary

**Both flash-limit guards (PlatformIO's per-target ceiling and the recorded `flash_total` invariant in both baselines) now report the true 32768 B flash size of the ATmega328P, ATmega328PB and ATmega32U4, forfeiting the linker's protection over each target's bootloader region by explicit, reaffirmed operator request.**

## Performance

- **Duration:** ~10 min (2026-08-20T07:52:33Z -> 2026-08-20T08:02:01Z)
- **Tasks:** 4/4 completed
- **Files modified/created:** 5 modified, 16 created (3 cold logs in the meta repo, 13 fixtures in the submodule)

## Accomplishments

- Raised `board_upload.maximum_size` to 32768 on `[env:uno]`, `[env:uno328pb]`, `[env:leonardo]` in `platformio.ini`, with a comment at each site naming the forfeited reserve and, on leonardo, the bootloader-overwrite consequence.
- Added `zero_bootloader_reserve.py`, a `pre:` SCons hook scoped to `PIOENV == "uno328pb"` that zeroes the atmelavr MiniCore builder's 384 B urclock-bootloader subtraction (`env.BoardConfig().update("bootloader.size", 0)`), because a bare `board_upload.maximum_size` override alone does not reach the reported ceiling on that one target.
- Captured three cold-rebuild logs (`rm -rf .pio/build/<env>` then one `pio run -e <env>` per target) as the sole transcription source for both baseline edits: uno 25130/32768/1575, uno328pb 25180/32768/1581, leonardo 27212/32768/2016 — `flash_used`/`ram_used` byte-identical to the pre-change figures on all three targets.
- Moved `scripts/baseline/size_baseline.json`'s `avr_targets.*.flash_total` to 32768 (transcribed, `flash_free` derived), refreshed `firmware_tree_sha` to the tree the logs were taken against, and added a `meta` note naming both mechanisms, the forfeited reserves, and leonardo's `flash_free` move from 1460 B to 5556 B.
- Moved `scripts/baseline/size_baseline_base01.json`'s `avr_targets.*.flash_total` to 32768 by the operator's explicit two-axis ruling, leaving `flash_used`, `ram_used`, `ram_total`, `ram_free`, `native_envs` and `warnings` byte-identical to the previous commit. Observed `--policy merge05` against BASE-01, fed the three real cold logs, exiting 0 with no `board or framework moved` line and printing the exact expected band decomposition.
- Severed nine stranded `tests/test_check_size_baseline.py` legs onto two new fixture families (`captured_build_fullflash_*` for default mode, `merge05_*_fullflash_*` / `planted_*_fullflash*` for `--policy merge05`) and strengthened `test_base01_is_not_re_anchored_by_the_new_exemption` to machine-check both the frozen growth axis and the new `flash_total` pin. Full firmware suite: 315 passed on a committed, porcelain-clean tree.

## Task Commits

Each task was committed atomically inside the `firestarter` submodule, on `gsd/v1.32-at28c-write-path-root-cause-report-provenance`:

1. **Task 1: Move each target's reported flash ceiling to the true 32768 B and capture cold logs** - `283971d` (feat)
2. **Task 2: Move the recorded flash_total invariant in lockstep, transcribed from the cold logs** - `ed084d6` (feat)
3. **Task 3: Move BASE-01's board-identity figure so --policy merge05 stays usable** - `f7d2297` (feat)
4. **Task 4: Sever every stranded test leg onto fixture families carrying the new ceiling** - `8286916` (test)

No separate plan-metadata commit was made inside the submodule (the meta-repo gitlink bump is explicitly out of scope for this quick task, per the execution environment constraints).

## Files Created/Modified

- `firestarter/platformio.ini` - added `board_upload.maximum_size = 32768` to all three AVR envs, wired `pre:zero_bootloader_reserve.py` into the shared `[env]` `extra_scripts` list (after `pre:name_firmware.py`), with per-target comments naming the forfeited reserve
- `firestarter/zero_bootloader_reserve.py` - new `pre:` SCons hook, `uno328pb`-scoped, zeroes the MiniCore bootloader-size subtraction; documents the rejected `board_bootloader.size = 0` route in its header
- `firestarter/scripts/baseline/size_baseline.json` - `avr_targets.*.flash_total` -> 32768, `flash_free` recomputed, `meta` gained `flash_ceiling_move_260820_a7w` and a corrected `firmware_tree_sha`; the stale leonardo `flash_free`/percentage sentence in the Phase 149 `merge05_clause` corrected by appending a bracketed note
- `firestarter/scripts/baseline/size_baseline_base01.json` - `avr_targets.*.flash_total` -> 32768, `flash_free` recomputed by subtraction; `meta` gained `flash_ceiling_move_260820_a7w` recording the two-axis split
- `firestarter/tests/test_check_size_baseline.py` - module docstring extended with the `_fullflash` derivation record and retirement disposition; nine test functions repointed to new fixtures with corrected docstrings; `test_base01_is_not_re_anchored_by_the_new_exemption` strengthened with `flash_total == 32768` assertions and a corrected docstring
- `firestarter/tests/fixtures/README.md` - new `_fullflash fixture families` section documenting both new families and the keep-not-delete disposition of every retired fixture
- 13 new fixture files under `firestarter/tests/fixtures/` (see `key-files.created` above)

## Decisions Made

- **Forfeited bootloader protection, per target, accepted and documented rather than mitigated:** uno 512 B (optiboot), uno328pb 384 B (urclock), leonardo 4096 B (Caterina). On leonardo specifically, firmware that later grows past the old 28672 B ceiling will now be linked into and flashed over Caterina — the operator was told this in plain terms during planning and reaffirmed the request. No compensating "bootloader-safe" second guard was added, per the locked operator decision.
- **BASE-01's `flash_total` moves too, by operator ruling, while its `flash_used`/`ram_used` growth anchors and all five MERGE-05 band/exemption literals stay frozen.** Leaving BASE-01 at its old ceilings would have made `--policy merge05` report `board or framework moved` on all three targets against every future real log, permanently — a gate that never goes green stops being read. `flash_total` is treated as a board-identity invariant, distinct from the growth axis BASE-01 exists to protect.
- **Retired fixture families are kept, not deleted.** `captured_build_v132_*` (+ its planted sibling), the pre-149 `captured_build_*` trio, `merge05_base01_anchor_*`, and the three pre-`_fullflash` `planted_size_baseline_policy_*` fixtures remain on disk in `tests/fixtures/`, read by no leg. Reasoning recorded in both `tests/fixtures/README.md` and the test module docstring: they are a legible, byte-for-byte measurement record of the pre-260820-a7w ceilings, and this project's fixture-inventory convention already excludes anything a checker/test does not name from being treated as live, so keeping them costs nothing.
- **`merge05_defect_fix_fullflash_*` was given a purpose name rather than inheriting `captured_build_*`**, because after this severance that family is read by exactly one leg (the merge05 defect-fix admission arm), and the old naming convention ("a captured default-mode log") no longer described it.

## CRITICAL FINDING — do not re-attempt

`board_bootloader.size = 0` in `platformio.ini` CRASHES the build. PlatformIO's manifest-override loop (`pioplatform.py:103-114`) only int-coerces an override value when the target key already exists in the board manifest; `ATmega328PB.json`'s `bootloader` section has no `bootloader.size` key, so the override is left as the Python string `"0"`, and the atmelavr builder's MiniCore subtraction at `arduino.py:148` then raises `TypeError: unsupported operand type(s) for -=: 'int' and 'str'`. This was observed directly during planning; it is NOT attempted or re-attempted anywhere in this task. The working mechanism, verified end to end and used in Task 1, is the `pre:` extra_script `zero_bootloader_reserve.py`, which calls `env.BoardConfig().update("bootloader.size", 0)` before `BuildFrameworks` loads `arduino.py`, landing an actual `int` rather than a string.

## Deviations from Plan

None — plan executed exactly as written. All measured figures (post-change cold-build numbers, merge05 band arithmetic, exemption values) matched the orchestrator/planner's measurements exactly on re-verification; no STOP-and-report condition was triggered at any of the plan's explicit checkpoints (no `flash_used`/`ram_used` drift, no missing PASS-text decomposition, no forbidden-file modification).

## Issues Encountered

None. The RED window between Task 3 and Task 4 (five merge05 legs failing or firing for two reasons, as planned) was confirmed exactly as the plan described — `python3 -m pytest tests/test_check_size_baseline.py -q` showed 4 hard failures and 10 passing-but-not-yet-repointed legs after Task 3's commit, and 14/14 passing again after Task 4.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Both flash-limit guards are in lockstep at the real 32768 B ceiling on all three AVR targets. `--policy merge05` remains a usable gate. The firmware test suite is green (315 passed) on a committed, porcelain-clean submodule tree. No blockers for subsequent v1.32 phase work. Note for any future firmware growth on `leonardo`: there is now no automated protection against linking past 28672 B into the Caterina bootloader region — this is the accepted, documented trade this task implements, not a residual risk to be closed later.

---
*Quick task: 260820-a7w*
*Completed: 2026-08-20*

## Self-Check: PASSED

All 17 created files verified present on disk (3 cold logs in the meta repo, 13
fixtures + zero_bootloader_reserve.py in the submodule, plus this SUMMARY.md).
All 4 task commit hashes (`283971d`, `ed084d6`, `f7d2297`, `8286916`) verified
present in `git log --oneline --all` inside the `firestarter` submodule.
