---
phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
plan: 03
subsystem: serial-protocol
tags: [cap-01, serial, cobs, eprom-operations, tdd, buffer-size, msg-ok-ready]

# Dependency graph
requires:
  - phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
    plan: 01
    provides: "MSG_OK_READY param_bytes=-1 catalog entry + TestCapSafeDefault RED tests"
  - phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
    plan: 02
    provides: "Firmware emits DATA_BUFFER_SIZE as u16 param in MSG_OK_READY ack at 4 emit sites"
provides:
  - "SerialCommunicator._decode_id_frame override: extracts big-endian u16 from MSG_OK_READY 2-byte param into firmware_max_chunk (plausibility clamp [1,4096])"
  - "EpromOperator._calculate_buffer_size: returns 512 safe Uno-floor default when firmware_max_chunk absent (Phase 54 D-05 reversed)"
  - "Phase 54 fw_fields[2]/[3] identity-string parse block removed from _probe_port"
  - "Phase 54 identity-string tests replaced with _decode_id_frame seam tests (SC3b)"
  - "CAP-01 SC1 + SC3 + SC4 (host half) closed"
affects: [55-04, v1.10-bench, phase-45-v1.9-resume]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_decode_id_frame override seam: subclass or override pattern (already used by FaultInjectingSerialCommunicator) is the correct injection point for ack-level state — not _read_and_parse_lines (GATE-1.8d)"
    - "CAP-01 safe-default pattern: absent advertisement returns 512 (Uno floor) instead of raising; graceful degradation for mixed-version firmware+host"
    - "Plausibility clamp [1, 4096] on decoded u16: rejects hostile/corrupt ack values before they size file.read() chunks (T-55-05/T-55-06 mitigations)"

key-files:
  created: []
  modified:
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/eprom_operations.py
    - firestarter_app/tests/test_serial_comm.py
    - firestarter_app/tests/test_frame_vectors.py

key-decisions:
  - "firmware_buffer_size __init__ attribute kept (DEPRECATED comment added) because conftest.py make_comm factory mirrors it; removing the declaration would break the factory without benefit"
  - "test_frame_vectors.py had two additional Phase 54 D-05 raise assertions (TestHostChunkFitsFirmwareDecodeCap + TestPerBoardBufferNegotiation) — both flipped to 512 safe-default assertions (Rule 1 auto-fix; they pinned the old contract reversed by CAP-01)"
  - "MSG_OK_READY import placed after frame_parser imports to satisfy ruff I001 import-sort order"

patterns-established:
  - "_decode_id_frame seam test pattern: build a synthetic body bytes([id]) + params + bytes([crc8]) and call comm._decode_id_frame directly — no serial I/O needed, pins the ack-decode contract"

requirements-completed: [CAP-01]

# Metrics
duration: 25min
completed: 2026-06-05
---

# Phase 55 Plan 03: Host half — MSG_OK_READY decode override + Phase 54 identity-string parse removal

**Host reads advertised buffer size from MSG_OK_READY u16 param via _decode_id_frame override; _calculate_buffer_size returns 512 safe default when absent; Phase 54 fw_fields identity-string parse removed; Plan-01 RED tests GREEN; 458/458 tests pass**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-06-05T00:00:00Z
- **Completed:** 2026-06-05
- **Tasks:** 2
- **Files modified:** 4 (inside firestarter_app submodule)

## Accomplishments

- `SerialCommunicator._decode_id_frame` override added: after `codec.decode_id_frame`, when the body id byte is `MSG_OK_READY` and the param region (`body[1:-1]`) is exactly 2 bytes, extract big-endian u16 into `self.firmware_max_chunk`. Plausibility clamp rejects values outside [1, 4096] (T-55-05/T-55-06). Zero-byte param region leaves `firmware_max_chunk` unchanged (T-55-07 graceful degradation).
- `EpromOperator._calculate_buffer_size` updated: replaced `raise FirmwareOutdatedError` with `return 512` (CAP-01 safe Uno-floor default, reversing Phase 54 D-05). `FirmwareOutdatedError` import removed (Rule 1 auto-fix — ruff F401).
- Phase 54 `fw_fields[2]`/`fw_fields[3]` parse block removed from `_probe_port`. Identity string is now `<ver>:<board>` only. `firmware_buffer_size` attribute declared as `DEPRECATED` (kept for conftest compat).
- Phase 54 identity-string parse tests (3) replaced with 2 new `_decode_id_frame` seam tests (SC3b): 2-byte param 512 sets `firmware_max_chunk=512`; 0-byte param leaves it `None`.
- Plan-01 RED tests all GREEN: `TestCapSafeDefault` (3 tests) + `test_calculate_buffer_size_raises_without_max_chunk` (now asserts 512).
- GATE-1.8d: `_read_and_parse_lines` body unchanged — ring-fence test passes.
- 458/458 host tests pass; ruff clean on all edited files.

## Task Commits

Submodule commits (inside `firestarter_app/`), then meta-repo pointer bumps:

1. **Task 1: Add _decode_id_frame MSG_OK_READY override; _calculate_buffer_size defaults to 512**
   - firestarter_app submodule: `1ba6d46` (feat)
   - meta-repo pointer bump: `7d77527` (feat)

2. **Task 2: Remove Phase 54 fw_fields identity-string parse; add _decode_id_frame seam tests**
   - firestarter_app submodule: `b445d6c` (feat)
   - meta-repo pointer bump: `bde8f53` (feat)

## Files Created/Modified

- `/workspaces/firestarter_app/firestarter/serial_comm.py` — `_decode_id_frame` override with MSG_OK_READY u16 extraction + plausibility clamp; `firmware_buffer_size` deprecated; `fw_fields[2]/[3]` parse block removed from `_probe_port`; `MSG_OK_READY` import added
- `/workspaces/firestarter_app/firestarter/eprom_operations.py` — `_calculate_buffer_size` returns 512 instead of raising; `FirmwareOutdatedError` import removed
- `/workspaces/firestarter_app/tests/test_serial_comm.py` — 3 Phase 54 identity-string parse tests removed; 2 new `_decode_id_frame` seam tests added (SC3b pin)
- `/workspaces/firestarter_app/tests/test_frame_vectors.py` — 2 Phase 54 D-05 raise assertions flipped to 512 safe-default (Rule 1 auto-fix)

## Decisions Made

- **firmware_buffer_size kept with DEPRECATED comment:** `conftest.py` make_comm factory mirrors `__init__` attributes including `firmware_buffer_size`. Removing the declaration without updating conftest would silently break the factory (AttributeError in tests that call `comm.firmware_buffer_size`). Cheaper and safer to leave with deprecation comment; removal deferred to a future cleanup phase.
- **MSG_OK_READY import position:** Placed after `from firestarter.frame_parser import (...)` block to satisfy ruff I001 import sort order (isort-compatible canonical order).
- **test_frame_vectors.py update scope:** Two additional Phase 54 raise assertions outside the 3 identity-string tests were pinning the old D-05 contract — both updated as Rule 1 auto-fix since they directly contradict the new CAP-01 behavior.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed unused FirmwareOutdatedError import from eprom_operations.py**
- **Found during:** Task 1 (_calculate_buffer_size update)
- **Issue:** After removing the `raise FirmwareOutdatedError(...)` call, the import became unused (ruff F401)
- **Fix:** Removed `FirmwareOutdatedError` from the `from firestarter.exceptions import (...)` block
- **Files modified:** `firestarter_app/firestarter/eprom_operations.py`
- **Verification:** `ruff check firestarter/eprom_operations.py` passes clean
- **Committed in:** `1ba6d46` (Task 1 commit)

**2. [Rule 1 - Bug] Flipped 2 additional Phase 54 raise assertions in test_frame_vectors.py**
- **Found during:** Task 2 (full test suite run revealed 2 more failing tests)
- **Issue:** `TestHostChunkFitsFirmwareDecodeCap::test_calculate_buffer_size_raises_without_max_chunk` and `TestPerBoardBufferNegotiation::test_calculate_buffer_size_uses_advertised` both used `pytest.raises(FirmwareOutdatedError)` pinning the old D-05 contract. After CAP-01 reversal, these fail.
- **Fix:** Both tests updated to assert `== 512` (safe default); unused `FirmwareOutdatedError` + `pytest` imports removed from each
- **Files modified:** `firestarter_app/tests/test_frame_vectors.py`
- **Verification:** `pytest tests/ -x` — 458/458 pass
- **Committed in:** `b445d6c` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (Rule 1 — import cleanup + test contract update)
**Impact on plan:** Both auto-fixes required for CI compliance (ruff F401 gate + test suite green). No scope creep; both directly caused by the CAP-01 contract reversal planned in this phase.

## Issues Encountered

None — all changes flowed cleanly. The only unexpected work was the 2 additional Phase 54 tests in `test_frame_vectors.py` that weren't listed in the plan's `<read_first>` (which named only `test_serial_comm.py` lines 397-448). Discovered during the post-edit full suite run and fixed as Rule 1.

## Known Stubs

None — `firmware_max_chunk` is fully wired end-to-end:
- Firmware (Plan 02): emits `DATA_BUFFER_SIZE` as u16 param in `MSG_OK_READY` at 4 emit sites
- Catalog (Plan 01): `MSG_OK_READY` with `param_bytes=-1` (skips shape check for backward compat)
- Host (this plan): `_decode_id_frame` override extracts u16 → `firmware_max_chunk`; `_calculate_buffer_size` returns it or 512 safe default

## Threat Flags

No new security-relevant surface beyond what the plan's threat model covers. T-55-05, T-55-06, and T-55-07 are all mitigated by the `len(params_bytes) == 2` guard and plausibility clamp in `_decode_id_frame`.

## Self-Check

Files exist:
- `firestarter_app/firestarter/serial_comm.py` — FOUND (modified)
- `firestarter_app/firestarter/eprom_operations.py` — FOUND (modified)
- `firestarter_app/tests/test_serial_comm.py` — FOUND (modified)
- `firestarter_app/tests/test_frame_vectors.py` — FOUND (modified)

Commits verified: `1ba6d46`, `b445d6c` in submodule; `7d77527`, `bde8f53` in meta-repo.

## Self-Check: PASSED

## Next Phase Readiness

- **Phase 55 Plan 04** (if applicable): CAP-01 host+firmware halves complete. Both SC1, SC3, SC4 host requirements closed. The full dual-repo change is in place for bench verification.
- **v1.9 resume** (`/gsd-plan-phase 45`): After v1.10 ships and merged transport is confirmed, Phase 45 (Bug B RCA — Rev 2.0) can resume. The now-hardened serial transport rules out serial as a read-bug confounder.
- **GATE-1.8d:** `_read_and_parse_lines` body unchanged; ring-fence baseline snapshot still valid; v1.9 RCA N=5 W27C512 baseline binaries remain valid.

---
*Phase: 55-relocate-buffer-size-advertisement-operation-ok-ack*
*Completed: 2026-06-05*
