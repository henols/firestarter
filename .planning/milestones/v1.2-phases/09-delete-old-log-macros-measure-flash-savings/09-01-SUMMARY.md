---
phase: 09-delete-old-log-macros-measure-flash-savings
plan: 01
subsystem: firmware
tags: [logging, firmware, id-frame, dev-tools, MSG_OK_READY, send_ack-removal, deletion-precondition]

# Dependency graph
requires:
  - phase: 08-convert-state-machine-prefix-call-sites-ok-init-main-end
    provides: "LOG_OK_ID(MSG_OK_READY) id-frame macro shipped at hardware_operations.cpp:42 (commit ea2a3fb)"
provides:
  - "Zero send_ack() callers remain in firestarter/src + lib — Plan 02 atomic deletion of send_ack/send_ack_const/rurp_log/rurp_log_P unblocked"
  - "Two new emit sites for MSG_OK_READY id-frame (dt_set_registers + dt_set_address)"
  - "Small flash savings from text-prefix removal (Leonardo -36 B, Uno -48 B)"
affects:
  - 09-02 (legacy macro deletion — precondition met by this plan)
  - phase-09 LMIG-04 measurement (delta attribution row)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "LOG_OK_ID(MSG_OK_READY) replays as the 1-line conversion for any legacy send_ack(\"\") site — same shape Phase 8 ea2a3fb established at hardware_operations.cpp:42"
    - "D-NN inline-comment rationale (e.g. // D-04: was legacy ack; semantics ≈ ...) attaches decision-doc traceability to the converted call-site"

key-files:
  created:
    - .planning/phases/09-delete-old-log-macros-measure-flash-savings/09-01-SUMMARY.md
  modified:
    - firestarter/src/dev_tools.cpp

key-decisions:
  - "D-04 honored — both dev_tools.cpp send_ack(\"\") sites converted to LOG_OK_ID(MSG_OK_READY), catalog entry 0x01 reused unchanged"
  - "Plan acceptance-grep gate cleared by tweaking the rationale comment from 'was send_ack(\"\");' to 'was legacy ack;' (the bare substring 'send_ack(' tripped the plan's grep -c gate; semantics preserved)"

patterns-established:
  - "Phase 9 W1 atomic 1-line conversion pattern: precondition for W2 macro-tower deletion"

requirements-completed: [LFW-03]

# Metrics
duration: 3 min
completed: 2026-05-19
---

# Phase 9 Plan 01: dev_tools.cpp send_ack Conversion Summary

**Both `send_ack("")` callers in `firestarter/src/dev_tools.cpp` (lines 108 + 154) converted to `LOG_OK_ID(MSG_OK_READY)` per D-04, eliminating the last legacy text-prefix log callers in firmware production sources and unblocking Plan 02's atomic deletion of the entire `send_ack` / `send_ack_const` / `rurp_log` / `rurp_log_P` macro tower.**

## Performance

- **Duration:** 3 min (207 sec)
- **Started:** 2026-05-19T07:52:10Z
- **Completed:** 2026-05-19T07:55:37Z
- **Tasks:** 2 / 2
- **Files modified:** 1 (`firestarter/src/dev_tools.cpp`)

## Accomplishments

- `dt_set_registers` (line 108): `send_ack("");` → `LOG_OK_ID(MSG_OK_READY);  // D-04: was legacy ack; semantics ≈ "setup done, waiting on user button"`
- `dt_set_address` (line 154): same conversion, same idiom
- Zero `send_ack(` callers remain in `firestarter/src/` + `firestarter/lib/` (Plan 02 precondition met)
- Both AVR targets build clean with measurable flash savings
- Native dispatch suite stays green (15 / 15 PASS, unchanged from Phase 8 close)

## Task Commits

Each task was committed atomically inside the `firestarter/` sub-repo (the parent meta-repo holds no production code for this plan):

1. **Task 1: Convert `dev_tools.cpp:108` (`dt_set_registers`)** — `bfd203b` (refactor) — pre-rewording shape; Task 2's commit cleans the comment text retroactively to satisfy the plan's bare-grep gate
2. **Task 2: Convert `dev_tools.cpp:154` (`dt_set_address`) + harmonize line-108 comment** — `ad5233a` (refactor)

_Sub-repo:_ `firestarter/` (Arduino C++ firmware; the parent meta-repo at `/workspaces/firestarter_prom` does not track firmware source — see `firestarter/CLAUDE.md`)

**No plan metadata commit yet** — the parent repo (where `.planning/` lives) has unrelated pre-existing modifications. The SUMMARY itself is committed below in the standard final-commit step.

## Files Created/Modified

- `firestarter/src/dev_tools.cpp` — Lines 108 (`dt_set_registers`) and 154 (`dt_set_address`) converted from `send_ack("");` to `LOG_OK_ID(MSG_OK_READY);` with D-04 rationale comment
- `.planning/phases/09-delete-old-log-macros-measure-flash-savings/09-01-SUMMARY.md` — this artifact

## Verification Results

### Plan-level `<verification>` gate — PLAN 01 GREEN

| Gate | Command | Expected | Actual |
|------|---------|----------|--------|
| 1. Zero `send_ack(` callers in `src/` | `grep -rn 'send_ack(' src/ \| grep -v '^.*\.h:' \| wc -l` | `0` | `0` |
| 2. Two `LOG_OK_ID(MSG_OK_READY)` in dev_tools.cpp | `grep -c 'LOG_OK_ID(MSG_OK_READY)' src/dev_tools.cpp` | `2` | `2` |
| 3a. Leonardo build SUCCESS | `pio run -e leonardo` | SUCCESS + Flash line | SUCCESS, Flash 85.5% (24508 / 28672), 4164 B free |
| 3b. Uno build SUCCESS | `pio run -e uno` | SUCCESS + Flash line | SUCCESS, Flash 69.1% (22282 / 32256), 9974 B free |
| 4. Native dispatch green | `pio test -e native -f '*test_dispatch*'` | PASSED (22+ per plan; current suite has 15) | PASSED 15 / 15 (0.63 s) |

Final gate script output: `PLAN 01 GREEN`

### Flash deltas (informational — Plan-09-MEASUREMENT.md owns the formal attribution)

| Target | Pre-Plan-09-01 (Phase 8 close) | Post-Plan-09-01 | Delta |
|--------|--------------------------------|-----------------|-------|
| Leonardo Flash | 24544 B (85.6%) | 24508 B (85.5%) | **-36 B** |
| Uno Flash | 22330 B (69.2%) | 22282 B (69.1%) | **-48 B** |
| Leonardo RAM | 1467 B (57.3%) | 1467 B (57.3%) | 0 |
| Uno RAM | 1497 B (73.1%) | 1497 B (73.1%) | 0 |

The 36–48 B Flash savings come from collapsing two `rurp_log(LOG_OK_MSG, "")` text-frame emits into two `rurp_log_id(MSG_OK_READY, NULL, 0)` id-frame emits. The full Plan-09 flash measurement will attribute the rest of the macro-tower deletion in Plan 02+.

## Decisions Made

- **D-04 honored verbatim** (locked in `09-CONTEXT.md`): Both `send_ack("")` sites converted to `LOG_OK_ID(MSG_OK_READY)`. Catalog entry `MSG_OK_READY` (0x01) reused — no growth — because both call-sites semantically match the "ready/idle/done" definition (both functions signal "setup done, blocking on user button").
- **Comment text rewording** (in-flight, see deviation below): The plan's `<action>` text mandated `// D-04: was send_ack(""); semantics ≈ "..."` as the inline comment. That substring tripped the plan's own bare-grep acceptance gate (`grep -c 'send_ack(' src/dev_tools.cpp` returned `2` instead of `0` because of the comment text). Reworded both comments to `// D-04: was legacy ack; semantics ≈ "..."` to clear the gate while preserving D-04 rationale traceability.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan's bare-grep acceptance gate false-positives on rationale comment text**

- **Found during:** Task 2 (`acceptance_criteria` evaluation, gate `grep -c 'send_ack(' firestarter/src/dev_tools.cpp` returned `2` instead of `0`)
- **Issue:** The plan's `<action>` text mandated the literal inline comment `// D-04: was send_ack(""); semantics ≈ "setup done, waiting on user button"`. The plan's `<acceptance_criteria>` and `<verification>` blocks then use bare `grep -c 'send_ack(' ...` to assert "zero callers remain". The bare grep matches comment text, not just function calls — so the plan-as-written has a self-contradiction: honoring the `<action>` violates the `<acceptance_criteria>`.
- **Fix:** Reworded both inline comments from `was send_ack(""); semantics ≈ ...` to `was legacy ack; semantics ≈ ...`. Same D-04 rationale, no substring collision. Applied to both line 108 (retroactively, in the Task 2 commit) and line 154 (the Task 2 conversion itself).
- **Files modified:** `firestarter/src/dev_tools.cpp` (lines 108 + 154 comment text)
- **Verification:** Re-ran all four plan-level gates after the edit — `PLAN 01 GREEN` (gate 1 = 0 callers, gate 2 = 2 LOG_OK_ID occurrences, gates 3a/3b = both AVR SUCCESS, gate 4 = 15/15 PASS)
- **Committed in:** `ad5233a` (Task 2 commit absorbs both the line-154 conversion and the line-108 comment harmonization)

---

**Total deviations:** 1 auto-fixed (1 bug — plan-grammar conflict)
**Impact on plan:** Zero functional impact. Both call-sites converted exactly as D-04 intends; the rationale comment carries the same decision-doc pointer with a slightly tighter phrasing. No scope creep, no catalog growth, no behavior change.

## Issues Encountered

**Pre-existing native-test failures (out of scope, NOT fixed):**
Running the full native test suite (`pio test -e native`) reports 22 / 24 tests pass, with two suites ERRORED via SIGABRT:

- `native/avr/test_flash_intel_vpp` — 1 case PASSED, then SIGABRT
- `native/avr/test_eeprom28c_chip_id` — ERRORED before any test ran

These exercise EPROM handler paths (`flash_intel.cpp`, `eeprom_28c.cpp`) — entirely separate from the two lines I touched in `dev_tools.cpp`. The `[env:native]` build excludes `src/dev_tools.cpp` via `src_filter = +<proms/>`, so this plan's edits cannot have caused or affected these failures. The plan's `<verification>` block correctly scopes to `'*test_dispatch*'` (which passes 15/15). Logging here for the verifier; out of scope per the scope-boundary rule.

Recommended next: file these as pre-existing technical debt for a follow-on plan; do NOT add to Plan 02's scope. (No `deferred-items.md` write performed — the parent repo has no existing `deferred-items.md` in this phase directory and creating new files outside of the plan's scope is itself a scope violation. The two ERRORED suites are documented here so the verifier sees them.)

## User Setup Required

None — purely a firmware-source refactor.

## Next Phase Readiness

- **Plan 02 (`send_ack` / `send_ack_const` / `rurp_log` / `rurp_log_P` macro-tower deletion) is fully unblocked.** Zero `send_ack(` callers remain in `firestarter/src/` + `firestarter/lib/`; Plan 02's atomic deletion will compile cleanly because no caller dangling-references the removed macros.
- Both AVR targets stay well under the SC#4 90% Flash budget (Leonardo 85.5%, Uno 69.1%) with comfortable headroom — Plan 02's deletion is expected to widen that gap further.
- Native dispatch suite (`test_dispatch`) green; Phase 8 → Phase 9 baseline is preserved.
- Bench verification (the chipless wire-protocol matrix Phase 9 inherits from `08-MEASUREMENT.md`) is **not** part of this plan — Phase 9's later plans own that step. The observable change on the wire (`OK: ` → `OK: Ready` for these two dev-tools commands) is harmless per `T-09-01-01` threat-register accept disposition (host `expect_ack` discards the body string).

## Self-Check: PASSED

- [x] `firestarter/src/dev_tools.cpp` exists and contains exactly 2 `LOG_OK_ID(MSG_OK_READY)` occurrences (lines 108 + 154)
- [x] Task 1 commit `bfd203b` exists in firestarter sub-repo git log
- [x] Task 2 commit `ad5233a` exists in firestarter sub-repo git log
- [x] Plan-level `<verification>` script returns `PLAN 01 GREEN`
- [x] Both AVR builds SUCCESS with Flash lines reported
- [x] Native dispatch suite 15/15 PASSED

---
*Phase: 09-delete-old-log-macros-measure-flash-savings*
*Plan: 01-dev-tools-send-ack-conversion*
*Completed: 2026-05-19*
