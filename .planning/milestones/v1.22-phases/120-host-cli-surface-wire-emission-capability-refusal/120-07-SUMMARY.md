---
phase: 120-host-cli-surface-wire-emission-capability-refusal
plan: 07
subsystem: testing
tags: [pytest, cross-repo-parity, source-scanning-gate, anti-hollow, constants]

# Dependency graph
requires:
  - phase: 120-02
    provides: "COMMAND_SDP_UNLOCK/COMMAND_SDP_LOCK/FLAG_SKIP_SDP_UNLOCK + mandatory COMMAND_NAMES entries in constants.py"
provides:
  - "A real, bidirectional, header-parsing CMD_*/FLAG_* parity gate replacing the pre-existing 100%-hollow hardcoded-literal legs"
  - "Frozen four-entry _EXEMPT_FW_TO_HOST name-pair map (CMD_IDLE, CMD_FRAME_MAX, CMD_DEV_ADDRESS, CMD_DEV_REGISTER/COMMAND_DEV_REGISTERS)"
  - "COMMAND_NAMES-coverage leg distinguishing the KeyError crash path from the value-drift path"
  - "Machine-checked conditional-compilation assertion ({CMD_DEV_ADDRESS, CMD_DEV_REGISTER} at depth>0)"
  - "Three isolated planted-violation fixtures + a delitem leg + a fail-closed leg proving the gate can fail"
affects: [121-dev-test-fix-gates-docs, 122-close-honesty-ledger]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Depth-tracking #define extractor with header-guard-aware neutralization (avoids a vacuous +1 depth offset from the whole-file #ifndef/#endif include guard)"
    - "Exemption name-PAIR map (never a skip-set) for cross-repo naming mismatches"
    - "FIRMWARE_HEADER module constant doubling as both a skipif-guard proxy and a monkeypatch fixture-injection seam"

key-files:
  created:
    - firestarter_app/tests/fixtures/planted_constants_value_drift.h
    - firestarter_app/tests/fixtures/planted_constants_host_missing.h
    - firestarter_app/tests/fixtures/planted_constants_fw_missing.h
  modified:
    - firestarter_app/tests/test_revision_constants_parity.py
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The gate is header-guard-aware: the whole-file #ifndef __FIRESTARTER_H__/#endif wraps every define at nesting depth 1, which would make the depth>0 assertion vacuously true for every define, not just the two DEV_TOOLS ones — the extractor detects and neutralizes this specific boilerplate idiom before computing depth"
  - "Exemptions are a frozen four-entry name-pair map, deliberately not auto-derived, so a fifth exemption requires a reviewed edit to the dict literal rather than silent absorption"
  - "COMMAND_DEV_REGISTER/COMMAND_DEV_REGISTERS singular/plural mismatch is preserved as an enumerated exemption, never 'fixed' by renaming the host constant (it has callers)"
  - "Three separate planted-violation fixtures instead of one three-drift fixture, so a fixture failing for two reasons at once could not obscure which check fired"
  - "'Same commit pair' in HOST-03's wording is read honestly: firmware landed the new CMD_*/FLAG_* values in Phase 119, host lands the parity gate here in Phase 120 deliberately (HOST-06 forbids the reverse order) — what is proven is that the pair AGREES, bidirectionally, not that they landed in one commit"

requirements-completed: [HOST-03]

coverage:
  - id: D1
    description: "Bidirectional CMD_* and FLAG_* parity between firestarter.h and constants.py, replacing the hollow hardcoded-literal legs"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_every_firmware_cmd_define_maps_two_way_to_constants_py"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_every_firmware_flag_define_maps_two_way_to_constants_py"
        status: pass
    human_judgment: false
  - id: D2
    description: "COMMAND_NAMES coverage for every non-exempt CMD_* (closes the KeyError crash path)"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_every_firmware_cmd_has_a_command_names_entry"
        status: pass
    human_judgment: false
  - id: D3
    description: "Machine-checked conditional-compilation set equals exactly {CMD_DEV_ADDRESS, CMD_DEV_REGISTER}"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_conditionally_compiled_defines_are_exactly_the_dev_tools_pair"
        status: pass
    human_judgment: false
  - id: D4
    description: "Three isolated planted-violation fixtures each trip exactly one leg, proving detection isolation"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_planted_value_drift_is_detected"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_planted_host_missing_define_is_detected"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_planted_firmware_missing_flag_is_detected"
        status: pass
    human_judgment: false
  - id: D5
    description: "Fail-closed on an unreadable/absent header path (never a silent pass with an empty define set)"
    requirement: "HOST-03"
    verification:
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_gate_fails_closed_on_an_unreadable_header_path"
        status: pass
      - kind: unit
        ref: "firestarter_app/tests/test_revision_constants_parity.py#test_missing_command_names_entry_is_detected"
        status: pass
    human_judgment: false

# Metrics
duration: 45min
completed: 2026-07-29
status: complete
---

# Phase 120 Plan 07: Constants Parity Gate Rebuild Summary

**Rebuilt `test_revision_constants_parity.py`'s COMMAND_*/FLAG_* legs from hardcoded Python literals into a real two-way header-parsing gate over `firestarter.h`, with three isolated planted-violation fixtures, a `COMMAND_NAMES`-coverage leg, a fail-closed path, and a machine-checked conditional-compilation assertion — closing HOST-03.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-07-29T11:03:00Z
- **Completed:** 2026-07-29T11:24:00Z
- **Tasks:** 3
- **Files modified:** 5 (3 new fixtures, 1 test file rewrite, 1 REQUIREMENTS.md scoped edit)

## Accomplishments

- The old gate was **100% hollow** with respect to firmware drift: `test_command_values_match_firmware` and `test_flag_values_match_firmware` asserted hardcoded Python literals with the corresponding `firestarter.h` define named only in a trailing comment, and never actually read the header. This is precisely why `CMD_SDP_UNLOCK 9` / `CMD_SDP_LOCK 10` landed in Phase 119 unnoticed by this file — the gate could not have caught it even in principle.
- Both hollow legs are **removed** (not retained alongside the rebuild) and replaced by a real `_strip_comments` + depth-tracking `#define` extractor reading `firestarter/include/firestarter.h`, with bidirectional `CMD_*`/`FLAG_*` parity checks (`_check_cmd_two_way`, `_check_flag_two_way`) that assert BOTH directions: every firmware define maps to a host constant of the same value (or a named exemption), and every host constant traces back to a firmware define.
- **Four enumerated exemptions**, as a frozen name-**pair** map (`_EXEMPT_FW_TO_HOST`, never a skip-set): `CMD_IDLE` (no host counterpart — firmware-internal state), `CMD_FRAME_MAX` (has its own dedicated gate, value is a macro not a literal), and the `#ifdef DEV_TOOLS`-conditional pair `CMD_DEV_ADDRESS` / `CMD_DEV_REGISTER`. The last is also **name-mismatched**: firmware is singular, host is plural (`COMMAND_DEV_REGISTERS`) — a naive `CMD_X` → `COMMAND_X` map would misreport this as a real gap and invite the wrong "fix" of renaming a host constant that has callers.
- A separate `COMMAND_NAMES`-coverage leg (D-13) closes the crash path, not just the drift path: `COMMAND_NAMES[cmd]` is dereferenced at `eprom_operations.py:301` and `:377`, so a missing name entry is a `KeyError` at operation setup.
- A machine-checked conditional-compilation leg turns "these two are `#ifdef DEV_TOOLS`-conditional" from a comment-only assumption into a fact: the set of defines found at depth > 0 must equal exactly `{CMD_DEV_ADDRESS, CMD_DEV_REGISTER}`.
- **Three isolated planted-violation fixtures** were chosen over one three-drift fixture, because a fixture failing for two reasons at once could not prove which check fired: `planted_constants_value_drift.h` (CMD_VERIFY value drift), `planted_constants_host_missing.h` (firmware-only `CMD_DEBUG_DUMP`), `planted_constants_fw_missing.h` (host-only `FLAG_VPE_AS_VPP`). All three, plus a `monkeypatch.delitem` on `COMMAND_NAMES` and a fail-closed unreadable-path leg, call the SAME `_check_cmd_two_way` / `_check_flag_two_way` / `_check_command_names_coverage` helpers the real legs call — not a parallel reimplementation.
- **D-13's residual host-only-CI skip gap is recorded, not silently carried**: in host-only CI (`FW_ABSENT` true), every header-reading leg skips, so a host-only PR cannot catch a real firmware/host drift by itself. Splitting `COMMAND_NAMES` coverage into its own always-on test was considered and declined in favor of one gate with the `FW_ABSENT` skipif retained. The partial offset: the planted-fixture legs and the fail-closed leg read files under `tests/fixtures/` or `tmp_path` (always present), so they do NOT skip in host-only CI even though they cannot exercise the REAL header there.
- **Honest reading of HOST-03's "same commit pair" wording**: firmware landed `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK`/`FLAG_SKIP_SDP_UNLOCK` in **Phase 119**; the host lands the parity gate here in **Phase 120**, deliberately — HOST-06 forbids the reverse order (host emitting a flag firmware doesn't understand yet). What HOST-03 demands and what is now proven is that the pair **agrees**, machine-checked in both directions — not that they landed in a single literal commit.
- **A real bug was found and fixed while building the depth-tracking extractor** (Rule 1): a naive per-line preprocessor-nesting counter treated the whole-file `#ifndef __FIRESTARTER_H__` / `#endif` header guard as a real conditional block, offsetting every define's depth by +1 for the entire file and making the conditional-compilation assertion vacuously fail (every define showed depth ≥ 1, not just the two DEV_TOOLS ones). Fixed by detecting the classic header-guard idiom (first directive is `#ifndef NAME`, immediately followed by `#define NAME`, last directive is the matching `#endif`) and treating those two specific lines as depth-neutral boilerplate — verified against the real header before and after the fix.

## Task Commits

Each task was committed atomically (with one deviation from a strict 1:1 task→commit mapping — see Deviations below):

1. **Task 1: Create three isolated planted-violation fixture headers** - `957f1fb` (test)
2. **Task 2 + Task 3 (code)**: Real two-way header-parsing gate + planted/fail-closed legs - `9347d6d` (test)
3. **Task 3 (REQUIREMENTS.md)**: Close HOST-03 - `daf909a` (docs, meta repo)

_Note: Tasks 2 and 3's test code landed in a single commit (`9347d6d`) because the full rewritten file — including the Task 3 planted-violation legs, the `COMMAND_NAMES`-delitem leg, and the fail-closed leg — was authored in one `Write` pass before being split into per-task verification. See Deviations._

## Files Created/Modified

- `firestarter_app/tests/fixtures/planted_constants_value_drift.h` - CMD_VERIFY drift fixture (106 vs real 6), trips ONLY the value-drift leg
- `firestarter_app/tests/fixtures/planted_constants_host_missing.h` - adds `CMD_DEBUG_DUMP` with no host counterpart, trips ONLY the forward-direction host-missing leg
- `firestarter_app/tests/fixtures/planted_constants_fw_missing.h` - removes `FLAG_VPE_AS_VPP`, trips ONLY the reverse-direction firmware-missing leg
- `firestarter_app/tests/test_revision_constants_parity.py` - rebuilt gate: `_strip_comments`, `_find_header_guard_line_indices`, `_extract_defines`, `_EXEMPT_FW_TO_HOST`, `_host_name`, `_read_header_text`, `_check_cmd_two_way`, `_check_flag_two_way`, `_check_command_names_coverage`, plus 9 new/rewritten test functions; `test_revision_byte_values_match_firmware_enum`, `test_ctrl_values_match_firmware`, `test_cmd_frame_max_parity` verified byte-unchanged
- `.planning/REQUIREMENTS.md` - HOST-03 checkbox `[x]`, traceability row `Complete`, scoped 2-line diff (checkbox + row only)

## Decisions Made

- Header-guard-aware depth tracking (see Accomplishments — the real bug found and fixed).
- Exemption map kept as a name-pair map, never a skip-set, per the plan's explicit prohibition.
- `CMD_DEV_REGISTER` → `COMMAND_DEV_REGISTERS` singular/plural mismatch preserved, not "fixed."
- Three separate fixture files instead of one combined fixture (isolation proof requirement).
- `test_command_values_match_firmware`/`test_flag_values_match_firmware` fully removed (not retained as smoke tests) — the plan's acceptance criteria explicitly required "the two hollow legs are gone."

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Header-guard depth-offset bug in the extractor**
- **Found during:** Task 2, first pytest run of `test_conditionally_compiled_defines_are_exactly_the_dev_tools_pair`
- **Issue:** The initial depth-tracking `_extract_defines` counted every `#ifdef`/`#ifndef`/`#if` as a real conditional, including the whole-file `#ifndef __FIRESTARTER_H__` / `#endif` include guard wrapping the entire header. This offset every define's depth by +1 for the whole file, so the conditional-compilation assertion found 25 defines at depth > 0 instead of exactly 2.
- **Fix:** Added `_find_header_guard_line_indices`, which detects the classic header-guard idiom (first directive `#ifndef NAME` immediately followed by `#define NAME`, last directive the matching `#endif`) and excludes those two specific lines from depth tracking.
- **Files modified:** `firestarter_app/tests/test_revision_constants_parity.py`
- **Verification:** Ran `_extract_defines` against the real header before/after; confirmed depth 0 for all defines except `CMD_DEV_ADDRESS`/`CMD_DEV_REGISTER` at depth 1. Full suite green after the fix (13/13).
- **Committed in:** `9347d6d` (part of the Task 2 rewrite commit)

**2. [Process deviation, not a Rule 1-4 case] Tasks 2 and 3's code landed in one commit**
- **Found during:** Between Task 2 and Task 3
- **Issue:** The rewritten test file was authored in a single `Write` call that included both Task 2's real two-way gate AND Task 3's planted-violation/fail-closed/delitem legs, before per-task verification was run. Splitting them into two separate commits after the fact would have required an artificial partial-revert-then-reapply, which is riskier than accepting the deviation.
- **Resolution:** Committed the combined test-code change as one commit (`9347d6d`), then ran Task 3's specific verification commands and made a separate commit for the `.planning/REQUIREMENTS.md` HOST-03 closure (`daf909a`), preserving atomicity for the requirements-marking step (the part of Task 3 that is genuinely a distinct concern).
- **Impact:** No functional impact — every acceptance criterion for both Task 2 and Task 3 was independently verified against the final state. Documented here for commit-history transparency.

---

**Total deviations:** 1 auto-fixed bug (Rule 1), 1 process deviation (commit granularity, not a Rule 1-4 case).
**Impact on plan:** The depth-offset bug fix was essential for correctness (the conditional-compilation leg would otherwise never pass against the real header). The commit-granularity deviation has no functional impact; all acceptance criteria independently verified.

## Issues Encountered

None beyond the depth-offset bug documented above (fixed inline, verified, and included in the Deviations section).

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries were introduced. This plan touches only test infrastructure and a documentation-scoped requirements edit.

## Known Stubs

None.

## TDD Gate Compliance

N/A — this plan's frontmatter does not set `type: tdd`; tasks are `type="auto"`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HOST-03 closed; the rebuilt gate is a real, non-vacuous, bidirectional parity check that will catch future `CMD_*`/`FLAG_*` drift in both directions, including missing `COMMAND_NAMES` entries.
- HOST-01, HOST-02, HOST-04, HOST-05, HOST-06 remain untouched and Pending, as scoped.
- Firmware repo confirmed byte-untouched at `0048b3d` throughout (verified via `git -C /workspaces/firestarter status --porcelain` after every task).
- **Row 7 correction for the final phase-close sweep:** per this plan's own instruction, row 7 of the nine-row CORRECTION-4 cross-repo gate table (`test_revision_constants_parity.py`) is the ONE row this phase deliberately **changes** — "unchanged" is the wrong verdict for it when Phase 120's non-regression sweep runs. Every other row (`check_is_memory_cmd_no_ifdef.py`, `check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py`, `gen_sdp_bus_config.py` / `test_sdp_bus_config_drift.py`, `check_dispatch.py`, `test_dispatch_mirror.py`, `check_devtest_orchestrator.py`) was re-verified green and confirmed unaffected by this plan (`test_check_is_memory_cmd_no_ifdef.py`, `test_sdp_bus_config_drift.py`, `test_sdp_table_parity.py` all pass, 15/15 combined).
- One pre-existing, unrelated RED baseline confirmed at full-suite run: `tests/test_audit_coverage_matrix.py::TestAuditCoverageMatrix::test_golden_file_matches` (stale golden, 186034 vs 184631 bytes) — not this plan's regression, not touched.

---
*Phase: 120-host-cli-surface-wire-emission-capability-refusal*
*Completed: 2026-07-29*

## Self-Check: PASSED
- FOUND: firestarter_app/tests/fixtures/planted_constants_value_drift.h
- FOUND: firestarter_app/tests/fixtures/planted_constants_host_missing.h
- FOUND: firestarter_app/tests/fixtures/planted_constants_fw_missing.h
- FOUND: firestarter_app/tests/test_revision_constants_parity.py
- FOUND: .planning/REQUIREMENTS.md (HOST-03 scoped edit)
- FOUND commit 957f1fb (firestarter_app)
- FOUND commit 9347d6d (firestarter_app)
- FOUND commit daf909a (meta)
