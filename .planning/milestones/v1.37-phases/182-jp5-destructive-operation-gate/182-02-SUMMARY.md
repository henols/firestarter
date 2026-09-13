---
phase: 182-jp5-destructive-operation-gate
plan: 02
subsystem: generator
tags: [generator, decode-rule, pinout, constants-retirement, python]

requires:
  - phase: 182-jp5-destructive-operation-gate (182-01)
    provides: "the DIP32_27C801 layout in pinouts.json — the key this plan's new fork resolves to"
provides:
  - "firestarter_app/tools/build_db.py: resolve_pinout_key's 32-pin proto_id==0x08 arm now forks on variant_lo (0x03 -> DIP32_27C801, 0x02 -> DIP32_STD, else -> the residual _PGM_ON_PIN31_MAX_SIZE size arm)"
  - "firestarter_app/tools/build_db.py: _PGM_ON_PIN31_MAX_SIZE (module-local, 262144) replaces the imported MAX_27C020_SIZE"
  - "firestarter_app/firestarter/constants.py: MAX_27C020_SIZE and its false firmware-parity comment deleted"
  - "firestarter_app/tests/test_revision_constants_parity.py: test_max_27c020_size_parity deleted outright"
  - "firestarter_app/tests/test_build_db_inclusion.py: test_thirty_two_pin_0x08_dispatch_forks_on_variant_lo (parametrized) and test_the_pgm_on_pin31_boundary_keeps_sst37vf040_on_dip32_std"
  - "firestarter_app/tools/DECODE-NOTES.md: section 1 current, three new 32-pin pm_idx=12 variant_lo rows, stale 'unedited this phase' claim retracted, pin_map 0x600C correction recorded"
affects: [182-03, 182-06, 182-07]

actuals:
  tokens: 9200
  tasks: 3
  commits: 8

tech-stack:
  added: []
  patterns:
    - "32-pin proto_id==0x08 variant_lo ladder copies the 24-pin/28-pin arms' shape: pm_idx+protocol test, then variant_lo fork, then fall-through — no per-part special case anywhere in resolve_pinout_key"
    - "Module-local decode-boundary constants (_PGM_ON_PIN31_MAX_SIZE) replace host-imported constants that claimed a firmware parity with nothing to be parity with — the boundary lives where the generator uses it, named for what it decides rather than a memory-size class"
    - "Phase 181 precedent followed: test-surface retirement lands in its own commit before the production constant deletion, so the later deletion cannot redden a module at collection time"

key-files:
  created: []
  modified:
    - firestarter_app/tools/build_db.py
    - firestarter_app/firestarter/constants.py
    - firestarter_app/tests/test_revision_constants_parity.py
    - firestarter_app/tests/test_build_db_inclusion.py
    - firestarter_app/tools/DECODE-NOTES.md

key-decisions:
  - "D-02: the 32-pin proto_id==0x08 fork stays strictly inside the proto_id==0x08 test — protocol 0x10 (Intel-flash) rows carry variant_lo 0x10-0x13 at the same pm_idx and would be rerouted if the fork were hoisted above the protocol test. Pinned by four parametrized dispatch-test rows."
  - "D-02: the mem_size threshold survives as the residual fall-through arm (renamed _PGM_ON_PIN31_MAX_SIZE = 262144, module-local), not replaced by a pure variant_lo ladder — SST37VF040 (pm_idx=13, variant_lo=0x04, 524288 bytes) would otherwise move off DIP32_STD onto DIP32_27C020, putting its A18 address line on a PGM strobe. Pinned by a dedicated named test."
  - "Deviation: removed the now-unused 'from firestarter.constants import MAX_27C020_SIZE' import in Task 1's own commit rather than deferring it to Task 2, as the plan's action text instructed. The plan's stated reason for deferring (single reviewable commit for Task 2's deletion) is honored for the deletion that matters — the production constant and its comment block, which Task 2 still deletes in its own commit. But leaving the import unused inside Task 1's commit fails that same task's own 'ruff check exits 0' acceptance criterion (F401), so the two instructions in the plan directly conflicted; the acceptance-criteria gate was treated as authoritative. Also removed an adjacent stale header comment in build_db.py (lines ~24-28, not in the plan's read_first ranges) that described MAX_27C020_SIZE and claimed the same false firmware-parity ('Mirrored in firestarter/include/firestarter.h ... asserted by tests/test_revision_constants_parity.py') — orphaned by the import's removal and matched the acceptance check's per-part-name grep, so it had to go in the same commit."
  - "D-03: MAX_27C020_SIZE and its parity test deleted outright, not reworded — confirmed via 'git -C /workspaces/firestarter grep -n MAX_27C020' (empty) that the firmware macro it claimed parity with does not exist. Firmware repo confirmed unmodified throughout (git -C /workspaces/firestarter status --short empty at every check)."
  - "Sibling-parity-test audit (recorded, not fixed, per plan instruction): test_revision_byte_values_match_firmware_enum (no requires_fw decorator at all) and test_ctrl_values_match_firmware (@requires_fw) both assert hardcoded Python literals rather than a value read from the live firmware header — the same defect *shape* MAX_27C020_SIZE had. Unlike MAX_27C020_SIZE, both cite firmware defines that DO exist (verified: rurp_shield.h REVISION_2_3=5, rurp_pinout.h CTRL_* values match), so this is a lower-severity 'drift undetected until manually updated' risk, not a vacuous self-comparison. test_cmd_frame_max_parity's hardcoded 512 is a separately and explicitly disclosed/accepted decision (D-07), not a defect. None of the three were fixed in this phase; flagged as a Plan 07 / future-audit backlog candidate."
  - "182-CONTEXT.md's D-02 table cites pin_map as 0x000c; RESEARCH.md's correction (pin_map = 0x600C, of which 0x000c/0x0C is only the low byte / pm_idx) is the one build_db.py's own resolve_pinout_key actually acts on. Recorded verbatim in DECODE-NOTES.md section 1 per the plan's explicit instruction; no code depends on the full pin_map value, only pm_idx, so this correction changes no resolved key."

requirements-completed: [SAFE-01]

coverage:
  - id: D1
    description: "resolve_pinout_key's 32-pin protocol-0x08 arm dispatches on variant_lo (0x03->DIP32_27C801, 0x02->DIP32_STD, residual size arm otherwise), with no per-part special case, measured 8-row blast radius"
    requirement: SAFE-01
    verification:
      - kind: unit
        ref: "tests/test_build_db_inclusion.py::TestThirtyTwoPinVariantLoDispatch::test_thirty_two_pin_0x08_dispatch_forks_on_variant_lo"
        status: pass
      - kind: unit
        ref: "tests/test_build_db_inclusion.py::TestThirtyTwoPinVariantLoDispatch::test_the_pgm_on_pin31_boundary_keeps_sst37vf040_on_dip32_std"
        status: pass
    human_judgment: false
  - id: D2
    description: "MAX_27C020_SIZE and its self-comparing parity test are deleted from tracked host source; the firmware repository is confirmed unmodified"
    requirement: SAFE-01
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter_app grep -n 'MAX_27C020_SIZE' -- firestarter/ tools/ tests/  (exit 1, no match)"
        status: pass
      - kind: other
        ref: "git -C /workspaces/firestarter grep -n MAX_27C020  (exit 1, empty) and git -C /workspaces/firestarter status --short (empty)"
        status: pass
    human_judgment: false
  - id: D3
    description: "DECODE-NOTES.md section 1 is current: three new 32-pin rows, stale claim retracted, pin_map 0x600C correction and the proto_id==0x08 nesting hazard both recorded"
    requirement: SAFE-01
    verification:
      - kind: other
        ref: "git -C /workspaces/firestarter_app grep -n 'stays verbatim' -- tools/DECODE-NOTES.md (exit 1, no match) and grep -n '0x600C'/'SST37VF040'/'DIP32_27C801' (all present)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-09-10
status: complete
---

# Phase 182 Plan 02: 32-Pin Variant-Lo Dispatch Fix and MAX_27C020_SIZE Retirement Summary

**`resolve_pinout_key`'s 32-pin protocol-0x08 arm now forks on infoic's `variant_lo` field exactly like its 24-pin and 28-pin siblings, retiring the hand-tuned size threshold that put all eight 1 MB EPROM rows on the wrong pinout key, and the false firmware-parity claim standing where the fix belonged is gone.**

## Performance

- **Duration:** 45 min
- **Started:** 2026-09-10T00:00:00Z (approximate — sequential inline session)
- **Completed:** 2026-09-10
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- `resolve_pinout_key`'s 32-pin `proto_id in {0x07, 0x08, 0x10}` branch now dispatches the 0x08 sub-cluster on `variant_lo` (0x03 → `DIP32_27C801`, 0x02 → `DIP32_STD`, else → the residual size arm), with the fork nested strictly inside the `proto_id == 0x08` test so protocol-0x10 (Intel-flash) parts at the same `pm_idx` are provably unaffected.
- The `mem_size` threshold survives as the fall-through arm, renamed `_PGM_ON_PIN31_MAX_SIZE` (module-local, `262144`), so `SST37VF040` (`pm_idx=13`, `variant_lo=0x04`, 524288 bytes) provably stays on `DIP32_STD` rather than moving to `DIP32_27C020` and putting its A18 address line on a PGM strobe.
- `MAX_27C020_SIZE` and its self-comparing parity test are gone from tracked host source. The parity test's docstring cited `firestarter/include/firestarter.h #define MAX_27C020_SIZE 262144`; that macro does not exist in the firmware tree (confirmed empty `git -C /workspaces/firestarter grep -n MAX_27C020`), so the assertion compared the host constant to a literal copy of itself.
- Two new dispatch tests in `tests/test_build_db_inclusion.py` (10 parametrized/individual assertions total) replace the retired parity arm as the 32-pin dispatch's coverage, and each asserts every resolved key is a member of `VALID_PINOUT_KEYS` (the pinouts.json registration guard) as its self-checking leg.
- `tools/DECODE-NOTES.md` section 1 is brought current: three new `pm_idx=12` `variant_lo` rows, the stale "unedited this phase" claim retracted, the `pin_map = 0x600C` correction to CONTEXT's D-02 table recorded, and the `proto_id == 0x08`-nesting hazard documented alongside the pre-existing 28-pin `0x10`/`0x11` Critical note (left untouched).
- `chip_database.json` was not regenerated or otherwise touched — confirmed clean via `git -C /workspaces/firestarter_app status --short firestarter/data/chip_database.json` at every checkpoint. Regeneration is Plan 182-03's job.
- The firmware repository (`/workspaces/firestarter`) was read (to confirm `MAX_27C020_SIZE`'s absence) but never modified — confirmed via `git -C /workspaces/firestarter status --short` returning empty throughout.

## Task Commits

Each task was committed atomically inside `firestarter_app` (a separate git repository on `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`), followed by a meta-repo commit advancing the gitlink by name:

1. **Task 1: Dispatch the 32-pin 0x08 cluster on variant_lo** — `529d6e1` (feat) in `firestarter_app`; `d999adb8` (chore) in meta.
2. **Task 2: Retire MAX_27C020_SIZE and its self-comparing parity arm** — three commits in `firestarter_app`: `1b0e74e` (test — delete the parity test), `bc8fa05` (docs — deviation fixup, see below), `b7ed310` (fix — delete the constant); `d44b76f3` (chore) in meta.
3. **Task 3: Bring DECODE-NOTES.md section 1 current** — `0612d23` (docs) in `firestarter_app`; `74e636e9` (chore) in meta.

_Note: `bc8fa05` is an unplanned fourth commit inside Task 2 — see Deviations._

## Files Created/Modified

- `firestarter_app/tools/build_db.py` — `resolve_pinout_key`'s 32-pin arm forks on `variant_lo`; `_PGM_ON_PIN31_MAX_SIZE` replaces the imported `MAX_27C020_SIZE`; the now-dead `MAX_27C020_SIZE` import and its adjacent stale header comment are removed.
- `firestarter_app/firestarter/constants.py` — `MAX_27C020_SIZE` and its false firmware-parity comment block deleted.
- `firestarter_app/tests/test_revision_constants_parity.py` — `test_max_27c020_size_parity` and its `@requires_fw` decorator deleted outright.
- `firestarter_app/tests/test_build_db_inclusion.py` — `TestThirtyTwoPinVariantLoDispatch` class added: `test_thirty_two_pin_0x08_dispatch_forks_on_variant_lo` (9-case parametrization covering the measured blast radius, the four protocol-0x10 Intel-flash points, and the pm_idx=0 SRAM sibling-arm point) and `test_the_pgm_on_pin31_boundary_keeps_sst37vf040_on_dip32_std`.
- `firestarter_app/tools/DECODE-NOTES.md` — section 1 extended and its stale claim retracted; heading no longer reads "UNCHANGED".

## Decisions Made

See `key-decisions` in frontmatter. The two load-bearing constraints from D-02 (fork stays inside `proto_id == 0x08`; the size threshold survives as the residual arm) are each pinned by a dedicated test rather than left as prose.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed the unused `MAX_27C020_SIZE` import in Task 1 instead of deferring it to Task 2**
- **Found during:** Task 1 (32-pin variant_lo dispatch)
- **Issue:** The plan's Task 1 action explicitly instructs leaving `from firestarter.constants import MAX_27C020_SIZE` in place "for Task 2 to delete along with the constant itself, so that Task 2's deletion is a single reviewable commit rather than a change split across two." But Task 1's own action already stops using `MAX_27C020_SIZE` (replacing it with `_PGM_ON_PIN31_MAX_SIZE`), which makes that import unused — and Task 1's own acceptance criterion requires `ruff check tools/build_db.py tests/test_build_db_inclusion.py` to exit 0. `ruff`'s `F401` (unused import) is enforced (`select = ["E", "F", "I", "UP"]` in `pyproject.toml`), so the two instructions directly conflicted: honoring the deferral instruction meant failing the task's own hard acceptance gate.
- **Fix:** Removed the import in Task 1's commit. This still honors the plan's stated reasoning as far as it applies — Task 2's deletion of the *production constant and its false-parity comment block* remains a single, separately reviewable commit, which is the deletion the plan's rationale was actually protecting.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** `ruff check` and `ruff format --check` both exit 0 on `tools/build_db.py`; `pytest tests/test_build_db_inclusion.py` — 30 passed (up from a 20-passed baseline).
- **Committed in:** `529d6e1` (Task 1 commit)

**2. [Rule 1 - Bug] Deleted a stale header comment in `build_db.py` that also claimed the false firmware parity**
- **Found during:** Task 1, immediately after removing the `MAX_27C020_SIZE` import
- **Issue:** `tools/build_db.py` carried a second comment block (near the top of the file, outside every `<read_first>` range this plan's tasks named) describing the size boundary and asserting `"Mirrored in firestarter/include/firestarter.h; the pair is asserted by tests/test_revision_constants_parity.py"` — the same false claim D-03 targets in `constants.py`. It also mentioned `AM27C080` by name in prose, which made Task 1's own acceptance-criteria grep for per-part special cases (`git grep -nE 'AM27C080|...' -- tools/build_db.py`) fail — a check that would have failed even before this plan touched the file, since the comment predates this plan.
- **Fix:** Deleted the comment block. No replacement comment was written, per the plan's explicit "Write NO comments in `build_db.py`" instruction and the project's no-comments-in-source hard rule.
- **Files modified:** `firestarter_app/tools/build_db.py`
- **Verification:** `git grep -nE 'AM27C080|AM27LV080|AT27C080|MX27C8000|UPD27C8001|M27C801|SST37VF040' -- tools/build_db.py` now exits 1 (no match).
- **Committed in:** `529d6e1` (Task 1 commit)

**3. [Rule 1 - Bug] Reworded a Task-1 test docstring that named the constant Task 2 retires**
- **Found during:** Task 2 (retiring `MAX_27C020_SIZE`), while checking that acceptance criterion "`grep -n 'MAX_27C020'` prints nothing outside `tools/baseline/` and `tests/golden/`"
- **Issue:** `TestThirtyTwoPinVariantLoDispatch`'s class docstring (added in Task 1's commit) said "replacing the retired MAX_27C020_SIZE self-comparing parity arm," which is a literal, in-scope match for Task 2's acceptance grep.
- **Fix:** Reworded to "replacing the retired size-threshold self-comparing parity arm" — same meaning, no longer names the deleted constant.
- **Files modified:** `firestarter_app/tests/test_build_db_inclusion.py`
- **Verification:** `git grep -n 'MAX_27C020' -- .` (repo-wide) now returns nothing outside `tools/baseline/`/`tests/golden/`.
- **Committed in:** `bc8fa05` (unplanned, between Task 2's two named commits)
- **Note:** This is why `git -C firestarter_app log --oneline -2` shows `[fix, docs]` rather than the plan's literal expectation of `[test, fix]` at exactly two commits back — the ordering invariant the check exists to protect (test-surface retirement before production deletion) is intact at `-3` (`fix` ← `docs` ← `test`); only the exact commit-count the acceptance check names is off by one, caused by this necessary fixup.

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs/contradictions surfaced by the plan's own acceptance criteria). **Impact on plan:** All three were forced by a genuine self-consistency gap between the plan's action prose and its own acceptance criteria (deviations 1 and 2), or by cross-task interaction between Task 1's added test wording and Task 2's later deletion (deviation 3). No scope creep — no per-part special case was added anywhere, and the load-bearing D-02 constraints (fork inside `proto_id == 0x08`, size threshold as residual arm) are exactly as the plan specified.

## Issues Encountered

None beyond the deviations above. The sibling-parity-test audit (Task 2, required by the plan) is recorded in `key-decisions` and in commit `b7ed310`'s message; per the plan's explicit instruction, nothing was fixed there — only recorded, as backlog material for Plan 07 or a future audit.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The corrected `resolve_pinout_key` rule is what Plan 182-03 regenerates `chip_database.json` against; the measured 8-row blast radius (`AM27C080`, `AM27LV080`, `AT27C080`, `M27C801` ×2, `MX27C8000`, `MX27C8000A`, `UPD27C8001`) is unchanged from CONTEXT's D-02 table and RESEARCH.md's measurement — this plan did not re-measure it against a live regen, since regeneration is explicitly out of scope here.
- `tools/diff_db.py` (Plan 03) is the instrument that will confirm whether `support_status`/`programming.*` move on the eight rows; this plan makes no claim either way (flagged_assumption A4 in the PLAN.md frontmatter).
- No blockers for Plan 182-03.

---
*Phase: 182-jp5-destructive-operation-gate*
*Completed: 2026-09-10*
