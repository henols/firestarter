---
phase: 153-write-path-erase-policy
plan: 14
subsystem: infra
tags: [platformio, avr, size-gate, merge-05, check_size_baseline, cold-build]

# Dependency graph
requires:
  - phase: 153-write-path-erase-policy (plans 02-06)
    provides: the standalone CMD_ERASE feature (eeprom28c_erase_execute, the dispatch arm, the two
      deleted pre-write blank checks) whose cold footprint this plan measures and funds
  - phase: 151-protection-readability-lock-status
    provides: the three-exemption MERGE-05 flash allowance stack and the *_v151* fixture-severance
      precedent this plan's fourth exemption and its own fixture hand-off follow
provides:
  - a measured, cold, all-three-target flash/RAM position for this phase, recorded in
    153-DECISIONS.md, verifying D-153-01's RAM-neutral prediction rather than asserting it
  - MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130, the fourth named, SHA-attributed flash
    exemption, sized from that measurement and never rounded
  - a re-recorded scripts/baseline/size_baseline.json (avr_targets, native_envs, three
    merge05_clause strings, meta) that makes both check_size_baseline.py gate modes green again
  - an enumerated list of 3 test legs left red for plan 15's fixture severance
affects: [153-15]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fourth stacked MERGE-05 flash exemption, same single-consumer / SHA-attributed / seven-element
      comment contract as the prior three (Phase 145/149/151)"
    - "Cold-only measurement discipline (rm -rf .pio/build/<env> before every pio run) as the sole
      source of truth for any figure funding an exemption"

key-files:
  created: []
  modified:
    - firestarter/scripts/check_size_baseline.py
    - firestarter/scripts/baseline/size_baseline.json
    - .planning/phases/153-write-path-erase-policy/153-DECISIONS.md

key-decisions:
  - "MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES sized at exactly 130 B (leonardo BASE-01 delta 724
    minus the existing 594 B allowance), never rounded up for headroom"
  - "RAM allowance and RAM constant left untouched -- Task 1 measured the RAM delta at exactly 0 B
    against the immediately-prior position on all three targets, verifying D-153-01's prediction
    rather than asserting it; no stop-and-report was triggered"
  - "The Caterina cliff headroom (28672-27630 = 1042 B, UNGUARDED) is recorded as a figure distinct
    from the MERGE-05 clause in both 153-DECISIONS.md and all three baseline merge05_clause strings"
  - "3 legs in tests/test_check_size_baseline.py are left failing on purpose
    (test_policy_merge05_admits_the_documented_defect_fix,
    test_policy_merge05_fires_on_uno_class_over_band, test_policy_merge05_fires_on_leonardo_growth)
    -- plan 15 owns re-planting them onto a new *_v153* fixture family"

requirements-completed: []

coverage:
  - id: D1
    description: "Constants lockstep confirmed unchanged between firestarter.h and constants.py
      (CMD_ERASE/CMD_BLANK_CHECK, FLAG_CAN_ERASE/FLAG_SKIP_ERASE/FLAG_SKIP_BLANK_CHECK)"
    requirement: "ERASE-08"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py (14 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Measured cold flash/RAM position on uno, uno328pb, leonardo; RAM delta verified
      at 0 B against the immediately-prior position on all three targets"
    requirement: "ERASE-08"
    verification:
      - kind: other
        ref: "cold rm -rf + pio run -e {uno,uno328pb,leonardo}, transcribed in 153-DECISIONS.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130 authored with the seven-element
      exemption comment contract; _merge05_flash_allowance extended to a 7-tuple;
      compare_avr_policy_merge05 and main()'s PASS-line builder both print the fourth term"
    requirement: "ERASE-08"
    verification:
      - kind: unit
        ref: "python3 -c import check_size_baseline; _merge05_flash_allowance('leonardo') == (0, 96, 210, 288, 130, 724, 'leonardo')"
        status: pass
      - kind: other
        ref: "check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json (all 3 targets exit 0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "size_baseline.json re-recorded in one revision: avr_targets, native_envs (170/17
      both envs), three extended merge05_clause strings, meta superseding entries; both gate modes
      green"
    requirement: "ERASE-08"
    verification:
      - kind: other
        ref: "check_size_baseline.py default mode (3 AVR logs + 2 native logs) exit 0; --policy
          merge05 exit 0 for all 3 targets"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-08-21
status: complete
---

# Phase 153 Plan 14: MERGE-05 Fourth Exemption & Baseline Re-Record Summary

**Measured this phase's firmware footprint cold on all three AVR targets (+130 B flash, +0 B RAM), funded it with a fourth named, SHA-attributed MERGE-05 exemption (`MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130`), and re-recorded `size_baseline.json` so both gate modes are green.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-08-21T09:53:00Z
- **Completed:** 2026-08-21T10:48:09Z
- **Tasks:** 3
- **Files modified:** 3 (`check_size_baseline.py`, `size_baseline.json`, `153-DECISIONS.md`)

## Accomplishments

- Confirmed the ERASE-08 constants lockstep is unmoved (`CMD_ERASE`/`CMD_BLANK_CHECK` and the three
  flag bits identical in both files; host constants-parity test 14/14 passed) and recorded it as a
  measured fact, not an assumption.
- Measured cold flash/RAM figures on `uno`, `uno328pb`, `leonardo` via `rm -rf .pio/build/<env>` +
  one `pio run -e <env>` each: +130 B flash on all three vs. the immediately-prior pre-change
  position, +0 B RAM — verifying `D-153-01`'s RAM-neutral prediction rather than asserting it.
- Sized and authored `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130` (leonardo's BASE-01 delta 724
  minus the existing 594 B allowance), with the full seven-element exemption-comment contract
  (ordinal/scope, phase/decision attribution, single-consumer property, per-commit what-the-bytes-ARE
  breakdown with deletions itemised separately from additions and one 0 B item recorded, the full
  six-alternative rejection list, the Evidence-Ceiling sentence, and a tripwire-still-armed sentence
  naming plan 15's fixture family).
- Extended `_merge05_flash_allowance` to a 7-tuple, `compare_avr_policy_merge05`'s printed allowance
  expression, and `main()`'s PASS-line builder — both now carry the fourth term
  (`+724<=724=band0+exempt96+seam210+lock288+erase130` on leonardo).
- Re-recorded `scripts/baseline/size_baseline.json` in one revision: `avr_targets` (cold figures),
  `native_envs` (170 cases / 17 suites on both `native` and `native_nodevtools`, up from 163/17),
  all three `merge05_clause` strings (fourth term, a `WHAT WAS NOT CHANGED` beat reciting all three
  targets' byte-unchanged BASE-01 figures, a `TRIPWIRE STILL ARMED` beat naming plan 15's new
  `*_v153*` fixture family, and the Caterina paragraph as a distinct figure), and `meta`
  (`roadmap_cross_check` superseding entry, `generated`/`firmware_tree_sha`/`host_app_tree_sha`,
  extended `supersedes`/`consumed_by`).
- Verified both gate modes green: default mode (all 3 AVR logs + both native logs) and
  `--policy merge05 --baseline size_baseline_base01.json` (all 3 targets, four-term flash allowance,
  unchanged `+2<=2=seam2` RAM expression).

## Task Commits

Each task was committed atomically:

1. **Task 1: Measure the constants lockstep, then the cold flash and RAM figures on all three AVR
   targets** — `914d216a` (meta repo, docs: record post-change measured position (cold))
2. **Task 2: Author `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES` and extend the flash allowance** —
   `d1652a5` (firestarter, feat: fund erase's +130 B with a fourth named MERGE-05 exemption)
3. **Task 3: Re-record `size_baseline.json`** — `e0d6a1f` (firestarter, feat: re-record
   size_baseline.json for the erase feature)

**Plan metadata:** this SUMMARY + STATE.md/ROADMAP.md updates, committed separately per the
`sub_repos` config (meta-repo `.planning/` commit).

## Files Created/Modified

- `firestarter/scripts/check_size_baseline.py` — added `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES`,
  extended `_merge05_flash_allowance`/`compare_avr_policy_merge05`/`main()`'s PASS-line builder to a
  fourth term
- `firestarter/scripts/baseline/size_baseline.json` — `avr_targets`, `native_envs`, three
  `merge05_clause` strings, `meta` re-recorded in one revision
- `.planning/phases/153-write-path-erase-policy/153-DECISIONS.md` — added
  `## Post-change measured position (cold)` section

## Decisions Made

- Sized the fourth exemption at exactly 130 B from the measured leonardo delta (BASE-01 724 minus
  existing 594), never rounded up — per `D-153-01`'s funding posture and the plan's explicit
  no-rounding instruction.
- Left the RAM constant/allowance untouched: Task 1's measured RAM delta was exactly 0 B against the
  immediately-prior position on all three targets, so `D-153-01`'s RAM-neutral form is verified, and
  the plan's "stop and report" clause for a non-zero RAM delta was not triggered.
- Did not lower the native warning watermark even though this session's observed counts (872, 998)
  are below the recorded 1166 watermark — the plan permits but does not require lowering it, and no
  new warning class appeared, so the watermark's less-than-or-equal semantics are left exactly as
  they were.
- Left `envs_agree_note`'s prose untouched (it still reads correctly re: the provisional env's
  exclusion) — Task 3's action calls for a confirmation of that note, not a rewrite, and its stray
  historical "163" wording predates this plan and is out of this plan's scope.

## Deviations from Plan

None — plan executed exactly as written. All three tasks' acceptance criteria were met on the first
pass; no auto-fixes, no architectural questions, no auth gates.

## Issues Encountered

None.

## Requirement Flip Note

**ERASE-08 is left `Pending`/unchecked in `REQUIREMENTS.md` and `In Progress` per the phase's own
requirement-flip rule.** Plans 01, 14 and 15 jointly claim ERASE-08; plan 15 (the tripwire
severance onto the new `*_v153*` fixture family) has not run yet, so this plan does not mark
ERASE-08 complete. Plan 15 is the explicit owner of the remainder: re-plant the three legs
enumerated below onto the new fixture family so the tripwire is proven armed at the new allowance,
not merely asserted.

**Legs left red for plan 15, enumerated exactly (not a guess):**
- `test_policy_merge05_admits_the_documented_defect_fix` (Arm 2, its planted-growth fixture is now
  well inside the new 724 B leonardo allowance)
- `test_policy_merge05_fires_on_uno_class_over_band`
- `test_policy_merge05_fires_on_leonardo_growth`

11 of 14 legs in `tests/test_check_size_baseline.py` still pass, including
`test_base01_is_not_re_anchored_by_the_new_exemption` and `test_policy_merge05_fires_on_ram_move`.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `size_baseline.json` is green on both gate modes and reflects this phase's full measured cold
  footprint; plan 15 can proceed directly to severing the three named legs onto a `*_v153*` fixture
  family without any further measurement work.
- The Caterina cliff headroom is now 1042 B on leonardo (down from 1172 B), UNGUARDED — no gate
  catches a future overrun; this is recorded, not mitigated, per the phase's own decisions.
- `firestarter_app/` carries no tracked-file diff from this plan.

## Known Stubs

None.

## Threat Flags

None — no new network endpoint, auth path, file access pattern, or schema change at a trust
boundary was introduced; this plan only measures and funds an already-shipped feature's footprint.

---
*Phase: 153-write-path-erase-policy*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: `.planning/phases/153-write-path-erase-policy/153-14-SUMMARY.md`
- FOUND: `firestarter/scripts/check_size_baseline.py`
- FOUND: `firestarter/scripts/baseline/size_baseline.json`
- FOUND: `.planning/phases/153-write-path-erase-policy/153-DECISIONS.md`
- FOUND commit `914d216a` (meta, Task 1)
- FOUND commit `d1652a5` (firestarter, Task 2)
- FOUND commit `e0d6a1f` (firestarter, Task 3)
- FOUND commit `e5ad092e` (meta, this SUMMARY)
