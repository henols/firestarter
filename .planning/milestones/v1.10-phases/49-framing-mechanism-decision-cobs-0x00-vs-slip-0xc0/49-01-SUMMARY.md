---
phase: 49
plan: 01
subsystem: serial-protocol
tags: [framing, COBS, SAFE-01, decision, ADR]
dependency_graph:
  requires:
    - .planning/v1.9-COBS-DECISION.md
    - firestarter/src/boards/uno_rurp_shield.cpp
    - firestarter/src/firestarter.cpp
    - firestarter/src/boards/rurp_serial_utils.cpp
    - firestarter_app/firestarter/serial_comm.py
    - firestarter_app/firestarter/frame_parser.py
  provides:
    - .planning/v1.10-FRAMING-DECISION.md (binding framing-mechanism ADR + frozen D-06 frame contract)
  affects:
    - Phase 50 (data-path framing implementation)
    - Phase 51 (command-channel framing implementation)
    - Phase 52 (lockstep test contract)
tech_stack:
  added: []
  patterns:
    - COBS streaming run-length encoding (0x00 delimiter, no second buffer)
    - CRC8-CCITT poly 0x07 (retained from existing layer)
    - Atomic-write mandate (delimiter in same send_bytes call as frame body)
key_files:
  created:
    - .planning/v1.10-FRAMING-DECISION.md
  modified: []
decisions:
  - "COBS 0x00 selected as the framing mechanism for v1.10 (aggregate matrix 11/12 vs SLIP 10/12)"
  - "SAFE-01 proof conclusive: host 0x00-silence proven via pyserial flush() guarantee, atomic-write mandate, Phase 51 frame-decoder consumption contract"
  - "len_u16 length prefix removed from data-block framing (delimiter-only resync)"
  - "XOR checksum replaced by CRC8-CCITT poly 0x07 on the data-block path (D-05)"
  - "CRC8 must be verified BEFORE handing decoded payload to JSON parser (Phase 51 design constraint, T-49-01)"
  - "Log/telemetry [0xAA55AA55] frame unchanged in v1.10"
metrics:
  duration_minutes: 30
  completed_date: 2026-06-01
  tasks_completed: 3
  tasks_total: 3
  files_created: 1
  files_modified: 0
---

# Phase 49 Plan 01: Framing Mechanism Decision — SUMMARY

**One-liner:** COBS `0x00` selected over SLIP `0xC0` via static SAFE-01 proof (host 0x00-silence confirmed) + scored 4-criterion evidence matrix (11/12 vs 10/12); frozen D-06 frame contract written.

## What Was Built

The single deliverable of Phase 49: `.planning/v1.10-FRAMING-DECISION.md` — a binding framing-mechanism ADR that:

1. Resolves the SAFE-01 `0x00` bus-aliasing safety question (v1.9-COBS-DECISION §5 Q2) via static code/architectural proof across three verified sub-claims.
2. Scores a neutral 4-criterion evidence matrix (safety, byte-exactness, implementation simplicity, overhead) for both finalists with the SAFE-01 outcome feeding the safety score.
3. Names COBS `0x00` as the winner and freezes the full D-06 frame contract: delimiter byte, COBS run-length scheme, exact field table (CRC8 placement, len_u16 removal decision), per-file change map for all four target files, log/telemetry unchanged statement, and the CRC8-before-parse security mandate for Phase 51.
4. Supersedes the v1.9-COBS-DECISION.md DEFER line and closes Q2/Q3.

## Task Outcomes

| Task | Name | Commit | Outcome |
|------|------|--------|---------|
| 1 | SAFE-01 static proof | f829ae2 | All 3 sub-claims confirmed; COBS eligible |
| 2 | Scored neutral evidence matrix | f829ae2 | COBS 11/12 vs SLIP 10/12; safety at parity |
| 3 | Decision + frozen frame contract + supersession | f829ae2 | COBS selected; D-06 frozen; v1.9 DEFER superseded |

All three tasks are in a single commit (f829ae2) because all tasks wrote to the same file `.planning/v1.10-FRAMING-DECISION.md` as a cohesive ADR document.

## Validation Results

All four automated grep assertions passed:

- `grep -qE "Q2|Q3|bus-aliasing"` — PASS (SAFE-01 resolution with Q2/Q3 phrasing)
- `grep -qiE "safety|byte-exact|simplicity|overhead"` — PASS (scored matrix, all 4 criteria)
- `grep -qE "rurp_serial_utils|serial_comm|frame_parser|test_messages"` — PASS (per-file change map)
- `grep -q "v1.9-COBS-DECISION"` — PASS (supersession cross-reference)

Additional assertion: `grep -qiE "CRC8.*(before|prior).*(json|pars)"` — PASS (V5 mandate)

## Key Decisions Made

1. **COBS `0x00` selected** — aggregate matrix score 11/12 vs SLIP 10/12. COBS wins on byte-exactness (0x00-free-body invariant) and overhead (bounded +1/254 vs SLIP theoretical 2x). Safety is a tie after SAFE-01 proof. SLIP wins only on implementation simplicity.

2. **SAFE-01 proof is conclusive** — three sub-claims verified:
   - Sub-claim A: pyserial `flush()` (line 141 of `serial_comm.py`) maps to POSIX `tcdrain()` — blocks until physical TX complete; after `flush()` returns, host goes silent in the response-reading loop.
   - Sub-claim B: atomic-write mandate — the entire COBS frame including `0x00` delimiter MUST be assembled as one `bytes` object and passed to `send_bytes()` in a single call. This is a frozen Phase 51 design constraint.
   - Sub-claim C: the Phase 51 frame decoder must consume the full COBS frame including its `0x00` delimiter before invoking the JSON parser. `rurp_set_programmer_mode()` (called via `_execute_operation()` at `operation_utils.cpp` line 291) is reached only after the frame is decoded and JSON is parsed — so the delimiter is consumed first.

3. **len_u16 prefix removed** — delimiter-only resync; retaining the length prefix would preserve the exact corruption mode the framing is meant to eliminate.

4. **XOR → CRC8-CCITT** — data-block path migrates from XOR checksum to CRC8-CCITT poly 0x07 per D-05.

5. **CRC8-before-parse mandate** — Phase 51 must verify CRC8 before handing decoded payload to `json_parser.c` (T-49-01 / V5 Input Validation).

## Deviations from Plan

None — plan executed exactly as written. All three tasks completed in order; SAFE-01 proof is conclusive (proof-passes branch, not the SLIP-fallback branch); matrix populated from evidence without pre-deciding.

## Threat Flags

None. This is a documentation/analysis phase. No new network endpoints, auth paths, file access patterns, or schema changes introduced. T-49-01 (decoded frame → JSON parser tampering) is mitigated by the CRC8-before-parse mandate recorded in the ADR.

## Self-Check: PASSED

- `.planning/v1.10-FRAMING-DECISION.md` — FOUND (268 lines, commit f829ae2)
- Commit f829ae2 — FOUND (`git log --oneline -1` confirms)
- All 5 grep assertions — PASSED (verified above)
- No source files modified in submodules — CONFIRMED (only `.planning/v1.10-FRAMING-DECISION.md` staged and committed)
