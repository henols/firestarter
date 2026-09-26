---
phase: 52-lockstep-contract-round-trip-tests
plan: "03"
subsystem: test-host
tags: [golden-vectors, pytest, cobs, lockstep, crc8, round-trip, host]
dependency_graph:
  requires: [52-01]
  provides: [test_frame_vectors-pytest-suite, both-legs-host-assertions, crc8-kat-host, cmd-frame-max-parity]
  affects: [firestarter_app/tests/test_frame_vectors.py, firestarter_app/tests/test_revision_constants_parity.py]
tech_stack:
  added: []
  patterns: [both-legs vector assertion (D-02), table-free CRC8 KAT (D-06/SC4), FW_ABSENT skipif guard pattern, encoder-only skip for >511 B (CR-01)]
key_files:
  created:
    - firestarter_app/tests/test_frame_vectors.py
  modified:
    - firestarter_app/tests/test_revision_constants_parity.py
decisions:
  - "Inline _ref_crc8_ccitt in test_frame_vectors.py (matching test_cobs.py approach) rather than importing from conftest — table-free independence is the invariant, inlining makes it explicit"
  - "Added test_encoder_only_vectors_are_skipped sentinel: documents the decode-cap boundary and guards that encoder-only vectors still exist in the catalog (D-03 / LOCK-01)"
metrics:
  duration: 10m
  completed: "2026-06-02"
  tasks: 2
  files: 2
---

# Phase 52 Plan 03: Host Pytest Vector Suite Summary

Added the host-side pytest vector suite (`tests/test_frame_vectors.py`) that pins the COBS frame contract against the frozen golden vectors from Plan 01. Both encoding and decoding legs verified for all eligible vectors; CRC8 KAT pins poly 0x07 independently of the production lookup table. Extended `test_revision_constants_parity.py` with `test_cmd_frame_max_parity` to guard CMD_FRAME_MAX == 512 (D-07). Full host suite: 13 new tests, all green; coverage 71.28% (above 70% floor).

## Tasks Completed

| Task | Name | Commit (app) | Files |
|------|------|--------------|-------|
| 1 | Author tests/test_frame_vectors.py — both-legs vector assertions + CRC8 KAT | ad6a409 | 1 file (app) |
| 2 | Extend test_revision_constants_parity.py with CMD_FRAME_MAX parity | 1034d09 | 1 file (app) |

## Acceptance Criteria Verification

- `pytest tests/test_frame_vectors.py -x -q` passes (0 failures) with encode-leg, decode-leg, and KAT tests collected — PASS (8 tests)
- Encode-leg asserts every FRAME_VECTORS entry (incl. VEC_512_ALL_FF, VEC_512_ALL_ZERO, VEC_1024_ALL_FF, VEC_1024_ALL_ZERO) with `encoded + b"\x00" == vec.frame` — PASS
- Decode-leg skips payloads >511 bytes and asserts `decoded[:-1] == vec.payload` + CRC match for the remaining 8 vectors — PASS
- KAT: `_crc8_ccitt(bytes([0x01])) == 0x07` and `_crc8_ccitt(b"") == 0x00` — PASS
- KAT cross-checked against table-free `_ref_crc8_ccitt` on [0x01], b"", and VEC_JSON_STATE13 payload — PASS
- No corrupt-CRC / truncated-frame negative cases added (D-03) — PASS (negative tests are in test_cobs.py only)
- `pytest tests/test_revision_constants_parity.py -k cmd_frame_max -q` passes — PASS
- New `test_cmd_frame_max_parity` decorated with `@pytest.mark.skipif(FW_ABSENT, ...)` using the existing module-level guard — PASS
- Asserts host `CMD_FRAME_MAX == 512` (Uno DATA_BUFFER_SIZE floor) — PASS
- Docstring records D-07 acceptance (host hardcodes 512; board-variant DATA_BUFFER_SIZE; not a bug to fix) — PASS
- Full host suite coverage at 71.28% (above 70% floor) — PASS

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written.

### Additional Decision: Encoder-Only Sentinel Test

Added `test_encoder_only_vectors_are_skipped` to `TestFrameVectorsDecodeLeg`. This test validates that the catalog still contains at least 4 encoder-only vectors (VEC_512_ALL_FF, VEC_512_ALL_ZERO, VEC_1024_ALL_FF, VEC_1024_ALL_ZERO). This documents the decode-cap boundary explicitly and guards against future catalog shrinkage silently making the skip dead code. Consistent with D-03 (valid-payload-only golden set) — this test exercises the skip boundary, not corrupt frames.

## Known Stubs

None — all test assertions are fully wired against real FRAME_VECTORS data. No placeholder or mock values.

## Threat Flags

No new production network endpoints, auth paths, or trust-boundary schema changes introduced. This plan touches only test files. T-52-07 (host codec drift), T-52-08 (CMD_FRAME_MAX divergence), and T-52-09 (wrong-polynomial KAT) are all fully mitigated as documented in the plan's threat model.

## Self-Check: PASSED

Files created/exist:
- FOUND: firestarter_app/tests/test_frame_vectors.py
- FOUND: firestarter_app/tests/test_revision_constants_parity.py (extended)

Commits exist (firestarter_app):
- FOUND: ad6a409 (Task 1 — test_frame_vectors.py)
- FOUND: 1034d09 (Task 2 — CMD_FRAME_MAX parity)
