---
phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
plan: 04
subsystem: integration-gate
tags: [cap-01, cobs, drift-gate, integration, verification, messages-toml, messages-h, messages-py]

# Dependency graph
requires:
  - phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
    plan: 02
    provides: "FW_VERSION reverted to <version>:<board>; all 4 MSG_OK_READY emit sites carry DATA_BUFFER_SIZE as u16 param"
  - phase: 55-relocate-buffer-size-advertisement-operation-ok-ack
    plan: 03
    provides: "_decode_id_frame override + _calculate_buffer_size safe-512 default + Phase 54 identity-string parse removed"
provides:
  - "CAP-01 SC4 closed: EVEN-01 preserved — Phase 52 lockstep round-trip / golden-vector tests green at new contract"
  - "CAP-01 SC5 closed: messages.toml byte-identical across all 3 repos; both full suites green; constant parity preserved"
  - "Drift gate: sync_to_subrepos.sh idempotent; git diff --exit-code clean on messages.h and messages.py"
  - "RAM gate: Uno 504 B free (above 480 B floor and 496 B post-Phase-54 baseline)"
  - "D-08-spirit: CMD_FRAME_MAX parity confirmed 512 == Uno DATA_BUFFER_SIZE floor"
  - "SC1 gate: pending human-verify checkpoint (firestarter fw string shape)"
affects: [55-bench, phase-53, phase-45-v1.9-resume]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Integration gate pattern: re-run sync + git diff --exit-code + both full suites as a single compound gate (Wave 3)"
    - "No source changes in integration gate — verification-only plan records evidence rather than producing artifacts"

key-files:
  created:
    - .planning/phases/55-relocate-buffer-size-advertisement-operation-ok-ack/55-04-SUMMARY.md
  modified: []

key-decisions:
  - "Task 1 automation run at 2026-06-05T07:10:32Z; all automated gates passed; SC1 deferred to human-verify checkpoint"
  - "Plan 02 Uno RAM line 504 B free confirmed as D-08-spirit close gate (1544 / 2048 bytes used)"

patterns-established: []

requirements-completed: [CAP-01]

# Metrics
duration: 8min
completed: 2026-06-05
---

# Phase 55 Plan 04: Integration Gate — SC4/SC5 automated verification PASSED; SC1 pending human-verify

**Drift gate clean, firmware native suite 43/43 PASSED, host suite 458/458 PASSED at 72% coverage; EVEN-01 + Phase 52 lockstep + CMD_FRAME_MAX parity all green; Uno 504 B free; SC1 gated on operator hardware-verify**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-05T07:10:32Z
- **Completed:** 2026-06-05T07:18:00Z
- **Tasks:** 1 automated (Task 1 complete); 1 human-verify checkpoint (Task 2 — awaiting operator)
- **Files modified:** 0 source files (verification-only plan)

## Accomplishments

- Drift gate: `bash tools/catalog/sync_to_subrepos.sh` exited 0; both `git diff --exit-code` checks (firestarter/include/messages.h and firestarter_app/firestarter/messages.py) clean — messages.toml byte-identical across all 3 repos, generated artifacts committed match regenerated output
- Codegen validation: `python3 firestarter/tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` confirmed catalog valid (64 messages, version 1)
- Firmware native suite: `pio test -e native` — **43/43 test cases PASSED** across 7 suites (test_dispatch, test_read_timing, test_cobs_cmd_frame, test_cobs_data_frame, test_frame_vectors, test_data_input, test_messages). `test_ok_ready_u16_param_frame` [PASSED] specifically confirmed (Plan 02 Unity test).
- Host suite: `pytest --cov=firestarter --cov-fail-under=70` — **458/458 tests PASSED at 72% coverage** (above 70% floor). `TestCapSafeDefault`, `test_serial_comm`, `test_even_block`, `test_frame_vectors`, and `test_revision_constants_parity` all in the green set.
- EVEN-01 / Phase 52 lockstep confirmed green: firmware `test_frame_vectors` 6/6 PASSED; `test_cobs_cmd_frame` + `test_cobs_data_frame` 11/11 PASSED; host `tests/test_frame_vectors.py` 13/13 PASSED — golden-vector round-trip contract intact at the new MSG_OK_READY shape.
- Constant parity: `test_revision_constants_parity.py` 5/5 PASSED; `test_cmd_frame_max_parity` PASSED — **CMD_FRAME_MAX == 512 unchanged** (D-07 acceptance, T-55-09 mitigated).
- RAM gate (D-08-spirit): Uno build `RAM: [======== ] 75.4% (used 1544 bytes from 2048 bytes)` — **504 B free**, above the 480 B floor and the 496 B post-Phase-54 baseline. No regression.

## Gate Results Table

| Gate | Command | Result |
|------|---------|--------|
| Sync idempotent | `bash tools/catalog/sync_to_subrepos.sh` | PASS — exit 0, no changes |
| Codegen --check | `python3 firestarter/tools/catalog/codegen.py --catalog ... --check` | PASS — 64 messages, version 1 |
| messages.h drift | `git -C firestarter diff --exit-code include/messages.h` | PASS — exit 0 (CLEAN) |
| messages.py drift | `git -C firestarter_app diff --exit-code firestarter/messages.py` | PASS — exit 0 (CLEAN) |
| Firmware native suite | `cd firestarter && pio test -e native` | PASS — 43/43, 7 suites |
| test_ok_ready_u16_param_frame | (in test_messages suite above) | PASS — 6/6 |
| test_frame_vectors (fw) | `pio test -e native -f "*test_frame_vectors*"` | PASS — 6/6 |
| test_cobs_* (fw) | `pio test -e native -f "*test_cobs*"` | PASS — 11/11 |
| Host full suite | `pytest --cov=firestarter --cov-fail-under=70` | PASS — 458/458, 72% coverage |
| test_frame_vectors (host) | (in host suite above) | PASS — 13/13 |
| test_revision_constants_parity | (in host suite above) | PASS — 5/5 |
| CMD_FRAME_MAX parity | test_cmd_frame_max_parity | PASS — 512 == Uno floor |
| TestCapSafeDefault | (in host suite above) | PASS — 3/3 |
| test_even_block | (in host suite above) | PASS — 13/13 |
| Uno RAM gate | `pio run -e uno` | PASS — 504 B free (1544/2048) |
| SC1 gate | `firestarter fw` prints version:board only | PENDING — human-verify checkpoint |

## Task Commits

Task 1 is verification-only — no source commits generated.

**Plan metadata commit:**

1. **Task 1: Automated gate run** — no commit (verification-only)
2. **Plan SUMMARY commit:** (meta-repo) — see final_commit below

## Files Created/Modified

- `.planning/phases/55-relocate-buffer-size-advertisement-operation-ok-ack/55-04-SUMMARY.md` — this file (gate results)

## Decisions Made

- All automated gates from the plan's `<verify>` block passed on first attempt; no remediation required.
- SC1 (`firestarter fw` string shape) correctly deferred to the human-verify checkpoint — cannot be verified without operator hardware access.

## Deviations from Plan

None — plan executed exactly as written. This is a verification-only plan; all gate results matched expectations established in Plans 01-03.

## Issues Encountered

None. Sync script idempotent (Plan 01 already propagated the catalog change). Both suites clean on first run.

## Known Stubs

None — the full CAP-01 implementation is wired end-to-end:
- Catalog (Plan 01): MSG_OK_READY with bytes param (param_bytes=-1) across all 3 repos
- Firmware (Plan 02): 4 emit sites carry DATA_BUFFER_SIZE as u16 param; FW_VERSION is `<version>:<board>` only
- Host (Plan 03): `_decode_id_frame` extracts u16; `_calculate_buffer_size` returns 512 safe default when absent
- Integration (this plan): drift gate clean; both suites green; parity intact; RAM within budget

SC1 (live hardware `firestarter fw` string check) is the sole remaining verification item — gated on operator.

## Threat Flags

No new security-relevant surface. T-55-08 (messages.toml drift) mitigated — drift gate clean. T-55-09 (constant-parity divergence) mitigated — CMD_FRAME_MAX parity test green.

## Self-Check: PASSED

- `.planning/phases/55-relocate-buffer-size-advertisement-operation-ok-ack/55-04-SUMMARY.md` — created (this file)
- `sync_to_subrepos.sh` exit 0 — verified in Bash output
- `git diff --exit-code` both artifacts — CLEAN, verified in Bash output
- `pio test -e native` — 43/43, verified in Bash output
- `pytest --cov=firestarter --cov-fail-under=70` — 458/458, 72%, verified in Bash output
- Uno RAM line — 504 B free, verified in Bash output

## Next Phase Readiness

- **CAP-01 SC4/SC5:** Closed by this automated gate.
- **CAP-01 SC1:** Awaiting operator `firestarter fw` hardware verification (Task 2 checkpoint).
- **Phase 53 bench:** Once SC1 approved, the transport is bench-ready. Phase 53 validates the final COBS transport end-to-end on hardware.
- **v1.9 RCA resume** (`/gsd-plan-phase 45`): After v1.10 ships, Phase 45 (Bug B RCA — Rev 2.0) can resume with hardened serial transport confirmed.

---
*Phase: 55-relocate-buffer-size-advertisement-operation-ok-ack*
*Completed: 2026-06-05*

---

## Human-Verify Checkpoint — Bench Results (2026-06-05, operator-witnessed)

**Hardware:** Leonardo on `/dev/ttyACM0`, Rev 2.0 shield. Phase-55 firmware built (`pio run -e leonardo`) and flashed/verified (avrdude, 25336 bytes). Host = working-tree Phase-55 code (`firestarter` console script, 3.0.0b7).

**SC1 — FW identity `<version>:<board>` only: ✅ PROVEN.**
Raw wire string captured via `firestarter -v fw`:
```
OK: FW: 3.0.0b6:leonardo
```
No trailing `:512`/`:1024`/maxchunk suffix — the buffer-size advertisement is off the identity string.

**SC4 — ack-sourced full-buffer (1024) even-block chunking, byte-exact: ✅ PROVEN (read path) + write-path transport confirmed.**
- Clean `read W27C512` completed byte-exact: 65536 bytes in 7.29s, **64 × `DATA: <chunk: 1024 bytes>`** (even blocks, no odd remainder), MAIN/END clean, no desync from the new 2-byte `MSG_OK_READY` param.
- Decisive proof of ack-sourcing: the Leonardo host *default* is the safe **512** floor; chunks sized to **1024** only because the host decoded `firmware_max_chunk=1024` from the `MSG_OK_READY` ack. The 1024-byte chunking IS the end-to-end confirmation that the relocated advertisement is read off the ack.
- Write path: firmware received and attempted full **1024-byte** blocks (firmware reported "bad bytes: 1019/1024"), confirming the write transport delivers full ack-sized blocks.

**Literal write→verify to chip: ⚠ not demonstrated — blocked by CHIP STATE, not code.**
The seated W27C512 is non-blank and firmware erase is "Not supported" on its `algorithm: 7` (UV-EPROM) path, so random data cannot overwrite existing cells (bits can't flip 0→1 without a UV erase). This is independent of Phase 55. The transport itself delivered full 1024-byte blocks correctly; only cell-level programming failed. A write→verify to a *blank/UV-erased* W27C512 (or an electrically-erasable chip) remains an operator option but is not required to validate CAP-01.

**Verdict:** Operator approved ("continue", 2026-06-05). CAP-01 transport contract verified end-to-end: SC1 proven, ack-sourced 1024 even-block chunking byte-exact, no protocol desync from the relocated advertisement.
