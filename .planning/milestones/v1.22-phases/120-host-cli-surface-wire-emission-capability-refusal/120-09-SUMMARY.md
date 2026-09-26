---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 09
subsystem: cli
tags: [click, sdp, at28c, eeprom28c, capability-refusal, wire-protocol]

# Dependency graph
requires:
  - phase: 120-01
    provides: "firestarter/sdp_capability.py — the derived 43/41 allow-set + sdp_capability(chip_name, db)"
  - phase: 120-06
    provides: "build_flags(..., skip_sdp_unlock=...) keyword-only wire-flag mapping"
  - phase: 120-08
    provides: "dev sdp CLI surface — sdp_capability import already present in cli_handlers.py"
provides:
  - "firestarter write --skip-sdp-unlock CLI option (write only)"
  - "_build_op_flags(skip_sdp_unlock=...) threading into build_flags"
  - "D-04 auto-set: forces FLAG_SKIP_SDP_UNLOCK for capability-refused protocol-0x0D chips, with a mandatory default-visible report line"
  - "D-18 warn-and-proceed for --skip-sdp-unlock on a non-0x0D chip"
  - "tests/test_write_skip_sdp_unlock.py — wire-boundary proof of all of the above"
affects: [120-10, 120-11, 120-12, 122-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Capability decision made in the Click handler (not the operations layer), because only the handler has both the chip NAME and app.db (resolve_chip's programmer dict carries neither protocol-id nor name)"
    - "Wire-flag composition kept in one function (build_flags) per D-19; callers never OR bits in after the call"

key-files:
  created:
    - firestarter_app/tests/test_write_skip_sdp_unlock.py
  modified:
    - firestarter_app/firestarter/cli_handlers.py
    - firestarter_app/tests/__snapshots__/test_characterization.ambr
    - .planning/REQUIREMENTS.md

key-decisions:
  - "D-04 auto-set is a deliberate divergence from 3.0.0b11 for the capability-refused 0x0D subset, not a no-op — today's write already leaves 0x2AAA<-0x55 / 0x5555<-0x20 stored as data on those parts before the payload"
  - "The refusal-cost trade-off is dissolved, not decided, on the derived 43/41 partition: a part with no SDP has nothing to unlock, so suppressing its auto-unlock costs it nothing"
  - "D-18: a --skip-sdp-unlock flag on a non-0x0D chip warns and proceeds, bit still emitted, write not refused or aborted"
  - "Auto-set decision made from db.get_eprom(eprom)['protocol-id'] plus sdp_capability(eprom, app.db), never from resolve_chip's programmer dict (RESEARCH F-06)"

patterns-established:
  - "Wire-boundary test rigor: assert command_dict['flags'] captured at SerialCommunicator.find_and_connect, not build_flags' function-return value alone"

requirements-completed: [HOST-02, HOST-04]

coverage:
  - id: D1
    description: "write --skip-sdp-unlock CLI option, exposed on write only, threaded through _build_op_flags into build_flags(skip_sdp_unlock=...)"
    requirement: "HOST-02"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_sdp_unlock.py::test_explicit_flag_sets_bit_0x100_on_the_wire"
        status: pass
      - kind: unit
        ref: "tests/test_cli_handlers.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "D-04 auto-set: capability-refused protocol-0x0D chips get FLAG_SKIP_SDP_UNLOCK forced on, with a mandatory default-visible report line naming the chip and the capability reason"
    requirement: "HOST-04"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_sdp_unlock.py::test_refused_0x0d_part_gets_the_bit_auto_set_with_an_unconditional_report_line"
        status: pass
      - kind: unit
        ref: "tests/test_write_skip_sdp_unlock.py::test_no_flag_on_an_allowed_0x0d_part_emits_no_skip_bit_and_no_auto_set_line"
        status: pass
      - kind: unit
        ref: "tests/test_write_skip_sdp_unlock.py::test_auto_set_line_is_not_duplicated_when_the_user_passed_the_flag"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-18 warn-and-proceed: --skip-sdp-unlock on a non-0x0D chip warns, still emits the bit, and the write still runs to a normal exit code"
    requirement: "HOST-02"
    verification:
      - kind: unit
        ref: "tests/test_write_skip_sdp_unlock.py::test_non_0x0d_chip_with_the_flag_warns_and_proceeds"
        status: pass
      - kind: unit
        ref: "tests/test_write_skip_sdp_unlock.py::test_non_0x0d_chip_without_the_flag_is_unchanged"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 09: write --skip-sdp-unlock + capability-refused auto-unlock Summary

**`write --skip-sdp-unlock` now reaches the wire as `FLAG_SKIP_SDP_UNLOCK` (0x100), and the host auto-sets that bit for capability-refused protocol-0x0D parts with a mandatory report line — closing HOST-02 and HOST-04.**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-07-29T12:06:55Z
- **Tasks:** 3
- **Files modified:** 3 (firestarter_app: 1 code file, 1 snapshot, 1 new test file) + 1 meta file (REQUIREMENTS.md)

## Own the divergence — it is deliberate, and it is not a no-op

`write` behaviour for the capability-refused `0x0D` subset **diverges from `3.0.0b11`**. Firmware keys its auto-unlock on **protocol**, not on part: `configure_eeprom28c`'s SDP-disable sequence fires at the start of every protocol-`0x0D` write regardless of whether that specific part has an SDP command decoder. Post-Phase-117 fix, that sequence reaches silicon, so on a capability-refused part (the 2 FRAM parts, the pre-SDP `2804`/`2816`/`2817` class) it is not inert — `0xAA`/`0x55`/`0xA0` are written as **data** at `0x2AAA`/`0x5555` before the real payload. A full-image write overwrites both bytes; an address-ranged or short write does not.

The refusal-cost trade-off that HOST-04's original framing worried about (over-refusing a working write) is **dissolved rather than decided** on the derived 43/41 partition: a part with no SDP has nothing to unlock, so suppressing its auto-unlock costs that part nothing at all, and additionally avoids the stored-byte residue. Residual risk stays confined to `120-WATCHLIST.md`'s 9 entries (bit-15=0 but `page_size > 1`).

## Accomplishments

- **Task 1** — `--skip-sdp-unlock` added to `write` only (mirrors `--skip-erase`'s warning-register help style); `_build_op_flags` grew a keyword-only `skip_sdp_unlock` parameter passed into `build_flags(..., skip_sdp_unlock=...)` as a keyword argument (D-19 — not OR-ed in after the call, unlike the `FLAG_OUTPUT_ENABLE`/`FLAG_CHIP_ENABLE` precedent in the same helper). `read`/`verify`/`blank`/`erase` deliberately do not get the flag (D-17).
- **Task 2** — the `write` handler now calls `sdp_capability(eprom, app.db)` exactly once and reads `app.db.get_eprom(eprom)['protocol-id']` to determine protocol-0x0D-ness (never from `resolve_chip`'s programmer dict, per RESEARCH F-06). For a capability-refused protocol-0x0D chip the user did not already flag, the host force-sets `skip_sdp_unlock = True` and prints an **unconditional, default-visible** (`click.echo`, never gated on `-v`) report line naming the chip and the capability reason. For `--skip-sdp-unlock` on a non-0x0D chip, D-18's warn-and-proceed fires: one warning naming the observed protocol, bit still emitted, write still runs — no refusal, no abort, no bit suppression.
- **Task 3** — `tests/test_write_skip_sdp_unlock.py` (6 tests, one parametrised over 2 chips = 7 collected cases) drives `write` end to end through a REAL `EpromOperator` wired to a fake serial port (INIT_DONE → OK_REQ_DATA → MAIN_DONE → END_DONE, the same happy-path frame sequence `test_characterization.py::test_write_happy_path` pins), asserting the emitted `command_dict["flags"]` value captured at `SerialCommunicator.find_and_connect` — the wire boundary, not `build_flags`' function-return value. `.planning/REQUIREMENTS.md` ticked HOST-02 and HOST-04 via scoped edits; HOST-06 untouched.

## Task Commits

Each task was committed atomically, inside the `firestarter_app` submodule (branch `v1.22-at28c-software-data-protection-lifecycle`):

1. **Task 1: Add `--skip-sdp-unlock` to `write`, thread through `_build_op_flags`** - `c1995a3` (feat)
2. **Task 2: Apply capability refusal to write's automatic unlock, D-04/D-18** - `da896d7` (feat)
3. **Task 3: Test the wire bit, auto-set report, D-18 warn-and-proceed; tick HOST-02/HOST-04** - `075a152` (test)

**Plan metadata:** see final commit below (meta repo: SUMMARY.md, STATE.md, ROADMAP.md, REQUIREMENTS.md).

## Files Created/Modified

- `firestarter_app/firestarter/cli_handlers.py` - `--skip-sdp-unlock` option on `write`; `_build_op_flags(skip_sdp_unlock=...)`; D-04 auto-set block + D-18 warn-and-proceed block in `write`'s body
- `firestarter_app/tests/test_write_skip_sdp_unlock.py` - new wire-boundary test file, 6 test functions (7 collected cases)
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` - regenerated `write --help` snapshot (expected drift from the new option, same as 120-08's `dev --help` precedent)
- `.planning/REQUIREMENTS.md` - HOST-02 and HOST-04 ticked with parentheticals; traceability rows Pending → Complete; HOST-06 untouched

## Decisions Made

- **D-04 auto-set lives in the Click handler, not `write_eprom`.** The handler is the last place with both the chip name and `app.db`; `resolve_chip`'s programmer dict carries neither `protocol-id` nor `name` (RESEARCH F-06).
- **D-18 warn-and-proceed never refuses, aborts, or suppresses the bit** — firmware never reads `FLAG_SKIP_SDP_UNLOCK` outside protocol `0x0D`, so nothing unsafe happens either way, and a blanket-flag script across a mixed batch of chips produces identical wire frames.
- **No duplicate auto-set line when the user already passed the flag** — the host did not decide anything in that case, so echoing "on your behalf" would misreport what happened.
- **Reused `sdp_capability`'s own reason string** in the auto-set report line rather than composing a second wording register — the predicate's reason already names the chip and the specific capability finding (FRAM / pre-SDP generation / wrong protocol).

## Deviations from Plan

None - plan executed exactly as written. The `write --help` characterization snapshot drift was anticipated by the plan's own `<python_test_env>` note (same as 120-08's precedent) and regenerated as in-scope, not treated as a deviation.

## Issues Encountered

None.

## TDD Gate Compliance

Not applicable — this plan's frontmatter does not set `type: tdd`; Tasks 1 and 2 are marked `tdd="true"` at the task level with an accompanying `<verify>` block, which was run and passed for each task before commit, but no separate RED-phase test commit was required or produced (the plan's Task 3 landed the dedicated test file as its own commit after both implementation tasks, per the plan's own task ordering — this is the plan author's chosen shape, not a gate violation).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HOST-02 and HOST-04 closed. Only HOST-06 remains open in Phase 120 (Plan 120-10).
- Plan 120-10 depends on this plan's wire-emission work (`FLAG_SKIP_SDP_UNLOCK` now reachable from `write`) to require firmware's `0x86` ack when the flag was set.
- Firmware repo confirmed byte-untouched at `0048b3d` throughout this plan.
- One pre-existing RED condition re-confirmed, not a regression: `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (stale golden, 186034 vs 184631 bytes).

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED

- FOUND: `firestarter_app/tests/test_write_skip_sdp_unlock.py`
- FOUND: `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-09-SUMMARY.md`
- FOUND commit `c1995a3` (Task 1, firestarter_app)
- FOUND commit `da896d7` (Task 2, firestarter_app)
- FOUND commit `075a152` (Task 3, firestarter_app)
- FOUND commit `f4e0552` (final docs commit, meta repo)
