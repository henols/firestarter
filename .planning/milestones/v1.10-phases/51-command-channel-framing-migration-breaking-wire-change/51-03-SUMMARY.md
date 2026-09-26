---
phase: 51-command-channel-framing-migration-breaking-wire-change
plan: "03"
subsystem: breaking-change-documentation
tags: [cobs, crc8, command-channel, framing, documentation, breaking-change, dual-repo-gate]
dependency_graph:
  requires: [phase-51-plan-01-firmware-cobs-command-decode, phase-51-plan-02-host-cobs-command-emit]
  provides: [FRAME-05-SC3-breaking-change-documented, dual-repo-green-gate, CMD_FRAME_MAX-parity-confirmed]
  affects: [firestarter/README.md, firestarter_app/README.md]
tech_stack:
  added: []
  patterns: [breaking-change-lockstep-upgrade-note, dual-repo-green-gate]
key_files:
  created: []
  modified:
    - firestarter/README.md
    - firestarter_app/README.md
decisions:
  - "D-01/D-02 enforced: documentation is the only guard for SC3 — no interop machinery, no negotiation, no fallback; README notes are the breaking-change record"
  - "Both README notes explicitly state: COBS+CRC8 framing, CRC8-before-parse, lockstep upgrade required, no mixed-version interop, beta-only, stable promotion is operator-gated"
metrics:
  duration: "4m"
  completed: "2026-06-02"
  tasks_completed: 2
  files_changed: 2
---

# Phase 51 Plan 03: Breaking-Change Documentation + Dual-Repo Green Gate Summary

Both sub-repo READMEs carry a breaking-change note for the COBS+CRC8 command-channel migration (D-02 / SC3); the full dual-repo test suite is green against the merged Wave-1 changes; CMD_FRAME_MAX parity confirmed at 512 in both repos.

## What Was Built

### Task 1: Document the breaking command-channel wire change in both sub-repo READMEs (D-02 / SC3)

- **`firestarter/README.md`** — Added "Breaking Changes (v1.10)" section with a
  "Command-channel wire protocol — COBS framing + CRC8 (breaking change)" subsection. Note
  states: every command (including the version probe) is `[COBS(JSON + CRC8)][0x00]`; firmware
  verifies CRC8 before the JSON parser sees any byte; legacy `{`-peek plaintext path removed; no
  fallback. Explicitly states this is a breaking wire-protocol change with no mixed-version interop
  and that firmware+host must be upgraded together (lockstep, as in the v1.2 Message-ID rework).
  Beta-only; stable promotion requires operator authorization. Includes the upgrade command.
- **`firestarter_app/README.md`** — Added the equivalent "Breaking Changes (v1.10)" section
  immediately before "Installation". Host-side framing: the CLI now emits a single atomic
  COBS+CRC8 frame per command (`send_bytes()` called once); plaintext `{`-peek path removed from
  firmware; same lockstep/no-interop/beta-only statements as the firmware README, worded from the
  CLI operator's perspective.

Both notes contain the word "breaking" (satisfying the `grep -i breaking` acceptance gate), mention
COBS/CRC8 framing, state the lockstep upgrade requirement, and confirm beta-only / operator-gated
stable promotion. Neither note introduces any negotiation, fallback, interop guard, or dual-protocol
machinery (D-01).

### Task 2: Dual-repo green gate + firmware/host constant-parity check

Verification gate — no production-code edits. Results recorded as Phase-52 gate evidence:

**Firmware native suite (`pio test -e native`):**
```
Environment    Test                             Status    Duration
-------------  -------------------------------  --------  ------------
native         native/avr/test_dispatch         PASSED    00:00:02.701
native         native/avr/test_read_timing      PASSED    00:00:03.628
native         native/avr/test_cobs_cmd_frame   PASSED    00:00:05.119
native         native/avr/test_cobs_data_frame  PASSED    00:00:01.364
native         native/avr/test_data_input       PASSED    00:00:05.083
native         native/avr/test_messages         PASSED    00:00:05.765
================= 33 test cases: 33 succeeded in 00:00:23.660 =================
```
- **33/33 PASSED** — includes `test_cobs_cmd_frame` (Wave-1 from plan 51-01) and `test_cobs_data_frame` (Phase-50 regression); no regressions.

**Host suite (`python -m pytest --cov-fail-under=70`):**
- **413/413 PASSED**; 29 snapshots passed
- **Coverage: 71.21%** (above the 70% floor; `Required test coverage of 70% reached`)
- Includes the three new FRAME-05 tests from plan 51-02: `test_send_json_command_emits_cobs_frame`, `test_send_json_command_atomic_frame`, `test_send_json_command_version_probe_is_framed`

**CMD_FRAME_MAX constant parity:**
```
firestarter/include/firestarter.h:   #define CMD_FRAME_MAX DATA_BUFFER_SIZE  → 512
firestarter_app/firestarter/constants.py:  CMD_FRAME_MAX = 512
```
Parity holds. Both values resolve to 512; CLAUDE.md constant-parity rule satisfied (FRAME-05 / D-06 / T-51-08).

## Verification Results

```
grep -in "breaking" firestarter/README.md firestarter_app/README.md
  → firestarter/README.md:17: ## Breaking Changes (v1.10)
  → firestarter/README.md:19: ### Command-channel wire protocol — COBS framing + CRC8 (breaking change)
  → firestarter/README.md:27: **This is a breaking wire-protocol change ...**
  → firestarter_app/README.md:61: ## Breaking Changes (v1.10)
  → firestarter_app/README.md:63: ### Command-channel wire protocol — COBS framing + CRC8 (breaking change)
  → firestarter_app/README.md:71: **This is a breaking wire-protocol change ...**

grep -il "cobs|crc8|lockstep|frame" firestarter/README.md firestarter_app/README.md
  → firestarter/README.md (FOUND)
  → firestarter_app/README.md (FOUND)

pio test -e native: 33/33 PASSED (exit 0)
python -m pytest --cov-fail-under=70: 413/413 PASSED; 71.21% coverage (exit 0)
CMD_FRAME_MAX = 512 in both firestarter.h and constants.py
```

## Acceptance Criteria Confirmation

| Criterion | Status |
|-----------|--------|
| `grep -i "breaking" firestarter/README.md` returns the command-channel note | PASS |
| `grep -i "breaking" firestarter_app/README.md` returns the command-channel note | PASS |
| Each README note mentions COBS/CRC8 framing AND lockstep upgrade (no mixed-version interop) | PASS |
| Each README note states the change is beta-only / stable promotion is operator-gated | PASS |
| `grep -ri "negotiat\|fallback\|interop guard\|dual-protocol"` returns nothing in new notes (machinery check) | PASS ("no plaintext fallback" documents absence of fallback — no machinery added) |
| `pio test -e native` exits 0 — full firmware native suite green incl. test_cobs_cmd_frame + test_cobs_data_frame | PASS (33/33) |
| `python -m pytest --cov-fail-under=70` exits 0 — full host suite green at 70% coverage floor | PASS (413/413; 71.21%) |
| CMD_FRAME_MAX resolves to 512 in both firestarter.h and constants.py — constant parity holds | PASS |
| SUMMARY records firmware test count, host test count, and coverage % as dual-repo gate evidence | PASS (above) |

## Must-Haves Confirmation

| Truth | Status |
|-------|--------|
| Both sub-repo READMEs document COBS+CRC8 command-channel as breaking change + lockstep upgrade | CONFIRMED |
| Dual-repo full test suite green: `pio test -e native` AND `python -m pytest --cov-fail-under=70` both pass | CONFIRMED (33/33 fw + 413/413 host) |
| CMD_FRAME_MAX defined identically (512) in firestarter.h and constants.py — constant parity holds | CONFIRMED |

## Security (Threat Model)

| Threat | Mitigation Status |
|--------|------------------|
| T-51-07: Repudiation / Misconfiguration — mismatched-version host↔fw pair | MITIGATED — README notes in both repos state lockstep upgrade requirement; `grep -i breaking` gate asserted |
| T-51-08: Tampering — firmware/host constant drift | MITIGATED — CMD_FRAME_MAX = 512 confirmed in both repos; parity holds |
| T-51-SC: No package installs in this plan | ACCEPTED — documentation + test-run gate only |

## Deviations from Plan

None — plan executed exactly as written. Both README notes were placed in a new "Breaking Changes (v1.10)" section (firestarter README: before "Beta / Pre-release Channel"; firestarter_app README: before "Installation") as instructed when no existing protocol/version section was present to anchor to.

## Requirements Closed

- **FRAME-05 SC3**: Breaking lockstep wire change documented for the beta cut (D-02 documentation-as-guard). Both sub-repo READMEs carry the note.
- **FRAME-05** fully closed across all three plans (01: firmware decode; 02: host emit; 03: breaking-change doc + dual-repo gate).

## Commits

| Task | Commit | Repo | Description |
|------|--------|------|-------------|
| Task 1 | ffb1500 | firestarter | docs(51-03): document breaking command-channel wire change (D-02 / SC3) |
| Task 1 | 481de09 | firestarter_app | docs(51-03): document breaking command-channel wire change (D-02 / SC3) |

## Known Stubs

None — README documentation is complete and accurate. No placeholder text.

## Threat Flags

None — no new network endpoints, auth paths, file access patterns, or schema changes. Documentation-only plan.

## Self-Check: PASSED

- firestarter/README.md "Breaking Changes (v1.10)" section — FOUND
- firestarter_app/README.md "Breaking Changes (v1.10)" section — FOUND
- Commit ffb1500 (firestarter) — FOUND
- Commit 481de09 (firestarter_app) — FOUND
- pio test -e native: 33/33 PASSED
- python -m pytest --cov-fail-under=70: 413/413 PASSED; 71.21%
- CMD_FRAME_MAX = 512 in both repos — CONFIRMED
