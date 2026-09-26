---
phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
plan: 01
subsystem: catalog
tags: [codegen, messages-toml, messages-py, messages-h, tdd, cap-01, cobs]

# Dependency graph
requires:
  - phase: 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks
    provides: TestFirmwareMaxChunkParse test class + FirmwareOutdatedError raise behavior (now flipped)
provides:
  - "Canonical messages.toml with MSG_OK_READY params = [{ type = \"bytes\" }] (param_bytes=-1)"
  - "Regenerated firestarter/include/messages.h (ID constant unchanged)"
  - "Regenerated firestarter_app/firestarter/messages.py CATALOG with MSG_OK_READY param_bytes=-1"
  - "TestCapSafeDefault RED gate: 3 tests pinning CAP-01 safe-default contract"
  - "Flipped legacy raise test to assert == 512 (also RED until Plan 03)"
  - "Byte-identity verified across all 3 repos; codegen --check passes"
affects: [55-02, 55-03, plan-02-firmware-emit-sites, plan-03-host-safe-default]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "MSG_OK_READY bytes param: param_bytes=-1 skips shape check so old-firmware 0-param acks pass through"
    - "TDD RED gate: catalog edit + test flip precedes implementation (Plan 03 turns GREEN)"

key-files:
  created: []
  modified:
    - tools/catalog/messages.toml
    - firestarter/tools/catalog/messages.toml
    - firestarter/include/messages.h
    - firestarter_app/tools/catalog/messages.toml
    - firestarter_app/firestarter/messages.py
    - firestarter_app/tests/test_even_block.py

key-decisions:
  - "bytes param type chosen over u16 for MSG_OK_READY: param_bytes=-1 skips the decode_id_frame shape check so old-firmware acks with 0 param bytes are NOT rejected (backward-compat, T-55-01/T-55-02 mitigated)"
  - "format = \"Ready\" kept unchanged: bytes type contributes zero printf specifiers, Rule 9 passes"
  - "unused pytest + FirmwareOutdatedError imports removed from test_even_block.py (Rule 1 auto-fix — ruff F401 would fail CI)"

patterns-established:
  - "Catalog sync: edit meta-repo messages.toml -> run sync_to_subrepos.sh -> commit inside each submodule -> bump meta-repo pointers"
  - "TDD RED wave: write failing tests before implementation; accepted RED output is the success condition"

requirements-completed: [CAP-01]

# Metrics
duration: 20min
completed: 2026-06-05
---

# Phase 55 Plan 01: Declare bytes param on MSG_OK_READY + RED host tests (CAP-01 catalog linchpin)

**MSG_OK_READY catalog changed to bytes param (param_bytes=-1) across all 3 repos; TestCapSafeDefault RED gate established so old-firmware 0-param acks pass shape check instead of timing out**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-06-05T00:00:00Z
- **Completed:** 2026-06-05
- **Tasks:** 2
- **Files modified:** 6 (across 3 repos)

## Accomplishments
- MSG_OK_READY `params = []` changed to `params = [{ type = "bytes" }]` in the canonical meta-repo `tools/catalog/messages.toml`; sync script propagated the change to both sub-repos; codegen `--check` confirms 10/10 rules pass
- `firestarter_app/firestarter/messages.py` CATALOG entry for MSG_OK_READY now shows `param_bytes=-1` (variable-length, skips shape check) — old-firmware acks with 0 param bytes are no longer rejected
- `TestCapSafeDefault` class added to `test_even_block.py` with 3 tests: absent-chunk (RED), 512 (PASS), 1024 (PASS) — pinning the CAP-01 safe-default contract for Plan 03 to turn GREEN
- Legacy `test_calculate_buffer_size_raises_without_max_chunk` flipped to assert `== 512` (RED until Plan 03 implements the safe default)

## Task Commits

Each task was committed atomically with per-submodule commits then meta-repo pointer bumps:

1. **Task 1: Declare bytes param on MSG_OK_READY in catalog + sync to both sub-repos**
   - firestarter submodule: `440c09b` (feat)
   - firestarter_app submodule: `93b2666` (feat)
   - meta-repo: `8eec48d` (feat — includes tools/catalog/messages.toml + submodule pointers)

2. **Task 2 RED: Add TestCapSafeDefault + flip raise test**
   - firestarter_app submodule: `123704e` (test)
   - meta-repo: `65cd111` (test — submodule pointer bump)

## Files Created/Modified
- `/workspaces/tools/catalog/messages.toml` — MSG_OK_READY params changed to `[{ type = "bytes" }]`
- `/workspaces/firestarter/tools/catalog/messages.toml` — byte-identical copy synced by script
- `/workspaces/firestarter/include/messages.h` — regenerated (MSG_OK_READY `#define` ID constant unchanged)
- `/workspaces/firestarter_app/tools/catalog/messages.toml` — byte-identical copy synced by script
- `/workspaces/firestarter_app/firestarter/messages.py` — regenerated; MSG_OK_READY CATALOG entry `param_bytes=-1`
- `/workspaces/firestarter_app/tests/test_even_block.py` — TestCapSafeDefault added; legacy test flipped

## Decisions Made
- **bytes vs u16 for MSG_OK_READY param type:** `bytes` chosen because it sets `param_bytes=-1`, causing `decode_id_frame` shape check to be skipped. `u16` would set `param_bytes=2` and REJECT acks from old firmware that carries 0 param bytes — causing a timeout cascade (T-55-01/T-55-02). The host extracts the u16 only when param body is exactly 2 bytes (Plan 03 responsibility).
- **format = "Ready" kept:** The `bytes` type contributes zero printf specifiers per codegen Rule 9 (same as the `ascii_str` exception). No `%u` added.
- **Removed unused imports (Rule 1 auto-fix):** After flipping `test_calculate_buffer_size_raises_without_max_chunk` to not use `pytest.raises(FirmwareOutdatedError)`, both `import pytest` and `from firestarter.exceptions import FirmwareOutdatedError` became unused. Removed to keep ruff clean (F401 would fail CI).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed unused imports from test_even_block.py**
- **Found during:** Task 2 (after flipping the raise test)
- **Issue:** `import pytest` and `from firestarter.exceptions import FirmwareOutdatedError` became F401 unused-import ruff violations after the `pytest.raises(FirmwareOutdatedError)` block was replaced
- **Fix:** Removed both unused imports
- **Files modified:** `firestarter_app/tests/test_even_block.py`
- **Verification:** `ruff check tests/test_even_block.py` passes clean; RED tests still fail as expected
- **Committed in:** `123704e` (part of Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — import cleanup)
**Impact on plan:** Necessary for CI compliance (ruff gate enforced by firestarter_app CI). No scope creep.

## Issues Encountered
None — catalog edit + codegen + sync script all ran cleanly on first attempt.

## Known Stubs
None — this plan is pure catalog + test scaffolding. No data flows through the new param yet (that is Plan 02 firmware emit + Plan 03 host safe-default).

## Threat Flags
No new security-relevant surface introduced. The `bytes` param declaration is the catalog-level mitigation for T-55-01 (shape check bypass for backward-compat) and T-55-02 (prevents timeout cascade on un-advertising firmware).

## Next Phase Readiness
- **Plan 02 (firmware):** Can now update the 4 `LOG_OK_ID(MSG_OK_READY)` emit sites to `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` — the catalog contract is established
- **Plan 03 (host):** Can implement `_calculate_buffer_size()` safe-default (return 512 when param absent) — the RED gate is live
- **Both plans consume the regenerated catalog** (byte-identical, codegen-verified)

---
*Phase: 55-relocate-buffer-size-advertisement-operation-ok-ack*
*Completed: 2026-06-05*
