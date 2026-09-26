---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 02
subsystem: host-cli
tags: [wire-protocol, constants, sdp, command-codes, flags]

# Dependency graph
requires:
  - phase: 119-lock-sdp-enable-command-surface-fw-half
    provides: "firmware CMD_SDP_UNLOCK 9 / CMD_SDP_LOCK 10 / FLAG_SKIP_SDP_UNLOCK 0x100 (firestarter.h:61-62,148)"
provides:
  - "firestarter/constants.py — COMMAND_SDP_UNLOCK = 9, COMMAND_SDP_LOCK = 10, FLAG_SKIP_SDP_UNLOCK = 0x100, plus the two mandatory COMMAND_NAMES entries"
affects: [120-05-host-cli-surface-wire-emission-capability-refusal, 120-07-host-cli-surface-wire-emission-capability-refusal, 120-08-host-cli-surface-wire-emission-capability-refusal, 120-09-host-cli-surface-wire-emission-capability-refusal]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Wire constant transcribed directly from the firmware header, with a comment naming the exact header lines and the load-bearing consumer sites, rather than a bare numeric literal"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/constants.py

key-decisions:
  - "Filled the COMMAND_* numeric gap at 9/10 in place (between COMMAND_DEV_REGISTERS=8 and COMMAND_READ_VPP=11) rather than appending at the end, preserving the block's existing ascending-order convention."
  - "Documented in-source, not just in this SUMMARY, that COMMAND_NAMES[cmd] has TWO dereference sites (eprom_operations.py:301 and :377), not one — so a future reader touching only one call site does not assume the other is safe."
  - "Did not touch ROADMAP.md/REQUIREMENTS.md's stale 0x200 reference — the F-120-05 correction (no 0x200 flag exists) is recorded here and in STATE.md's Phase 120 context block, per the plan's explicit prohibition against editing REQUIREMENTS.md for this."

requirements-completed: []  # HOST-03 spans plans 120-02 and 120-07; only 120-07 may close it. Deliberately empty.

coverage:
  - id: D1
    description: "COMMAND_SDP_UNLOCK = 9, COMMAND_SDP_LOCK = 10 added to the COMMAND_* block in ascending order, plus COMMAND_NAMES[9]='SDP_UNLOCK' / COMMAND_NAMES[10]='SDP_LOCK'"
    verification:
      - kind: unit
        ref: "inline python3 -c assertion (COMMAND_SDP_UNLOCK==9, COMMAND_SDP_LOCK==10, COMMAND_NAMES lookups, len==15)"
        status: pass
      - kind: unit
        ref: "tests/test_revision_constants_parity.py -q"
        status: pass
    human_judgment: false
  - id: D2
    description: "FLAG_SKIP_SDP_UNLOCK = 0x100 added as the ninth wire flag, with in-source disambiguation against CTRL_VPP_VPE_DROP_ENABLE's unrelated 0x100"
    verification:
      - kind: unit
        ref: "inline python3 -c assertion (9 FLAG_* constants, max==0x100, no 0x200, CTRL_VPP_VPE_DROP_ENABLE untouched)"
        status: pass
      - kind: unit
        ref: "tests/test_revision_constants_parity.py -q"
        status: pass
    human_judgment: false

# Metrics
duration: 10min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 02: Wire Constants — COMMAND_SDP_UNLOCK/LOCK + FLAG_SKIP_SDP_UNLOCK Summary

**Three new host-side wire constants (`COMMAND_SDP_UNLOCK = 9`, `COMMAND_SDP_LOCK = 10`, `FLAG_SKIP_SDP_UNLOCK = 0x100`) plus the two mandatory `COMMAND_NAMES` entries, transcribed exactly from `firestarter.h:61-62,148`, closing the host-side half of the wire-surface pair Phase 119 deliberately left open.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-07-29T10:27:30Z
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 1 (`firestarter_app/firestarter/constants.py`)

## Accomplishments

- `COMMAND_SDP_UNLOCK = 9` and `COMMAND_SDP_LOCK = 10` inserted into the existing `COMMAND_*` block, filling the numeric gap between `COMMAND_DEV_REGISTERS = 8` and `COMMAND_READ_VPP = 11`, keeping the block in ascending order. Comment records that both are **unconditional** in firmware (`firestarter.h:61-62`, never `DEV_TOOLS`-gated) and that their `COMMAND_NAMES` entries are load-bearing: `COMMAND_NAMES[cmd]` is dereferenced at **both** `eprom_operations.py:301` (`_setup_operation`) and `:377` (`_operation_context`) — a missing entry is a `KeyError` at operation setup, not a cosmetic display gap.
- `COMMAND_NAMES[COMMAND_SDP_UNLOCK] = "SDP_UNLOCK"` and `COMMAND_NAMES[COMMAND_SDP_LOCK] = "SDP_LOCK"` added in dict order matching the constant order (after `DEV_REGISTERS`, before `READ_VPP`). `len(COMMAND_NAMES)` moved from 13 to 15.
- `FLAG_SKIP_SDP_UNLOCK = 0x100` added as the ninth wire flag, immediately after `FLAG_VERBOSE = 0x80`. In-source comment records two facts: (a) this is firmware's flag block **ending point** — there is no `0x200` flag, correcting `ROADMAP.md:363` and Phase 120's *Depends on* line (F-120-05); (b) `CTRL_VPP_VPE_DROP_ENABLE` further down the same file also has value `0x100` but lives in the unrelated control-register namespace (mirror of `rurp_pinout.h`, documentary-only, Python never writes it directly) — the two `0x100`s must not be conflated.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule:

1. **Task 1: Add COMMAND_SDP_UNLOCK / COMMAND_SDP_LOCK and their mandatory COMMAND_NAMES entries** — `665509f` (feat)
2. **Task 2: Add FLAG_SKIP_SDP_UNLOCK = 0x100 with the CTRL-namespace disambiguation comment** — `bfdb287` (feat)

No plan-metadata commit inside `firestarter_app` — this plan's only change is `constants.py`; the metadata commit for this plan lives in the meta repo (below).

## Files Created/Modified

- `firestarter_app/firestarter/constants.py` — three new constants (`COMMAND_SDP_UNLOCK`, `COMMAND_SDP_LOCK`, `FLAG_SKIP_SDP_UNLOCK`) and two new `COMMAND_NAMES` entries, all with provenance comments citing exact `firestarter.h` line numbers.

## The F-120-05 Correction (recorded per plan's `<output>` instruction)

Firmware's `FLAG_*` block **ends** at `FLAG_SKIP_SDP_UNLOCK 0x100` (`firestarter.h:148`) — confirmed by direct read of the header in this plan. **There is no `0x200` flag.** `ROADMAP.md:363` and Phase 120's *Depends on* line both state `0x100`/`0x200` and are wrong; the host wires exactly **one** new flag, not two. `REQUIREMENTS.md` was deliberately **not** edited for this correction, per the plan's explicit prohibition — the correction is recorded here and was already carried into `STATE.md`'s Phase 120 context block (item 4) prior to this plan's execution.

Both `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` are **unconditional** in firmware by design — at file scope, never inside `#ifdef DEV_TOOLS` — because they are real user-facing operations expected in every build, not developer-only tooling.

`COMMAND_NAMES` has **two** dereference sites, not one: `eprom_operations.py:301` (`_setup_operation`) and `eprom_operations.py:377` (`_operation_context`). Both were read and confirmed during this plan; both now resolve cmd 9 and cmd 10 without a `KeyError`.

## Decisions Made

- Filled the numeric gap at 9/10 in place rather than appending, preserving the `COMMAND_*` block's ascending-order convention.
- Kept the `FLAG_*` and `COMMAND_NAMES` additions minimal — no reordering, rewording, or renumbering of any existing constant or entry, per the plan's explicit constraint.
- Left `CTRL_VPP_VPE_DROP_ENABLE` and the rest of the `CTRL_*` block completely untouched; verified via `git diff` scoped to that region showing no change.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' verification blocks passed on the first attempt with no auto-fixes needed.

## Issues Encountered

None.

## Non-regression checks (plan `<verification>` block, run in full)

- `python3 -m pytest tests/test_revision_constants_parity.py tests/test_eprom_operations.py -q` — all passed (38 tests, no failures).
- `python3 -m pytest -q` (full suite) — pre-existing known-RED `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` only (stale golden, explicitly named in this plan's context as not-this-plan's-regression). No live board attached, so `test_no_programmer_found_*` did not trigger.
- `ruff check firestarter/ tests/` and `ruff format --check firestarter/ tests/` — all pass.
- `python3 tools/check_mypy_watermark.py` — 1 error (watermark 35) — unchanged from plan 120-01's baseline.
- `git -C /workspaces/firestarter status --porcelain` — empty; tip still `0048b3d`. Firmware sub-repo byte-untouched.
- `git -C /workspaces/firestarter_app diff --stat -- firestarter/data/ firestarter/messages.py` — empty. DB and codegen artifacts untouched.

## User Setup Required

None.

## Next Phase Readiness

- `constants.py` now exposes `COMMAND_SDP_UNLOCK`, `COMMAND_SDP_LOCK`, and `FLAG_SKIP_SDP_UNLOCK` for the CLI/wire-emission call sites in later plans (120-05, 120-08, 120-09) and for plan 120-07's rebuilt parity gate.
- HOST-03 is **not** ticked by this plan — verified `.planning/REQUIREMENTS.md` is untouched; only plan 120-07 may close it.
- No blockers. Both sub-repo working trees stayed clean throughout except for the two committed changes to `constants.py` above.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter_app/firestarter/constants.py`
- FOUND: `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-02-SUMMARY.md`
- FOUND commit `665509f` (Task 1)
- FOUND commit `bfdb287` (Task 2)
