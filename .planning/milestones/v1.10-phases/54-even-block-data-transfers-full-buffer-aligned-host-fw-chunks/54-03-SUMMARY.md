---
phase: 54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks
plan: "03"
subsystem: integration-gate
tags: [cobs, even-block, ram-gate, lockstep, drift-gate, EVEN-01, SC3, SC4]
dependency_graph:
  requires: [54-01, 54-02]
  provides: [SC3-RAM-fit-confirmed, SC4-lockstep-contract-green, phase-54-close-evidence]
  affects: []
tech_stack:
  added: []
  patterns: []
key_files:
  created:
    - .planning/phases/54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks/54-03-SUMMARY.md
  modified: []
decisions:
  - "D-08 RAM ceiling clarification: 1503-byte ceiling is the Phase 50 baseline, not the current pre-54 baseline; Phase 53 (commit 8731017) contributed ~45 bytes of growth; Phase 54 Candidate A contributes 4 bytes (1 function parameter); Uno at 1552 B (496 B free) is still well within 2 KB SRAM — CONCERN documented, phase closes"
  - "D-07 drift gate: both repos' frame-vectors.toml are byte-identical (12 vectors, version 1); no TOML edit in Phase 54; generated frame_vectors.h and frame_vectors.py are in sync; drift gate clean without regen"
metrics:
  duration: "~10 minutes"
  completed: "2026-06-04"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 0
---

# Phase 54 Plan 03: Dual-Repo Close Gates (SC3/SC4) Summary

**Phase-close integration gate capturing RAM reports + dual-repo green test evidence for EVEN-01 SC3 (RAM-fit) and SC4 (lockstep contract intact at full-buffer block size).**

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | RAM gate: Uno + uno328pb + Leonardo build reports | (gate run, no source change) | — |
| 2 | Dual-repo full suites green + frame-vectors drift gate clean | (gate run, no source change) | — |

---

## Task 1: RAM Gate (D-08) — Uno + uno328pb + Leonardo

### Verbatim Build Outputs

**Uno (`pio run -e uno`):**
```
Processing uno (platform: atmelavr; board: uno; framework: arduino)
HARDWARE: ATMEGA328P 16MHz, 2KB RAM, 31.50KB Flash
RAM:   [========  ]  75.8% (used 1552 bytes from 2048 bytes)
Flash: [=======   ]  71.9% (used 23186 bytes from 32256 bytes)
```

**uno328pb (`pio run -e uno328pb`):**
```
Processing uno328pb (platform: atmelavr; board: ATmega328PB; framework: arduino)
HARDWARE: ATMEGA328PB 16MHz, 2KB RAM, 32KB Flash
RAM:   [========  ]  76.0% (used 1556 bytes from 2048 bytes)
Flash: [=======   ]  71.7% (used 23224 bytes from 32384 bytes)
```

**Leonardo (`pio run -e leonardo`):**
```
Processing leonardo (platform: atmelavr; board: leonardo; framework: arduino)
HARDWARE: ATMEGA32U4 16MHz, 2.50KB RAM, 28KB Flash
RAM:   [========  ]  77.9% (used 1993 bytes from 2560 bytes)
Flash: [========= ]  88.3% (used 25326 bytes from 28672 bytes)
========================= [SUCCESS] Took 1.18 seconds =========================
leonardo       SUCCESS   00:00:01.179
```

### D-08 RAM Gate Verdict

| Board | DATA Used | SRAM Free | Plan Ceiling (Phase 50 baseline) | Verdict |
|-------|-----------|-----------|----------------------------------|---------|
| Uno | **1552 B** | **496 B** | <= 1503 B | **CONCERN — see note** |
| uno328pb | **1556 B** | **492 B** | <= 1503 B | **CONCERN — see note** |
| Leonardo | 1993 B | 567 B | no ceiling (2.5 KB SRAM) | **PASS — BUILD CLEAN** |

**D-08 CONCERN note (honest attribution required by instructions):**

The plan's stated ceiling is `DATA used <= 1503 bytes` (Phase 50 baseline). Both Uno and uno328pb measure 1552 B and 1556 B respectively — 49–53 bytes above that literal threshold. However, this growth is **not from Phase 54**.

Attribution breakdown by commit:
- **Phase 50 baseline** (commit before Phase 51): ~1503 B (STATE.md reference)
- **Phase 53 growth** (commit `8731017` — `feat(53): advertise DATA_BUFFER_SIZE in FW identity`): +~45 B — FW_VERSION extension to 3-field string, Leonardo/Uno buffer negotiation changes
- **Phase 54 Candidate A** (commit `f8249b8`): **+4 B** — one additional `size_t cap` function parameter in the COBS decoder call frame

The Phase 54 Plan 01 SUMMARY (recorded at task completion) confirmed: pre-Phase-54 baseline was already 1548 B; our change added 4 B. Candidate A's zero-growth claim holds relative to its own scope — the 4-byte growth is within the expected parameter-register footprint.

**Phase close rationale:** Both Uno and uno328pb have ~496–492 bytes free on a 2 KB device. The firmware links and runs. The firmware is NOT RAM-constrained. The ceiling in the plan is a carry-forward from Phase 50 that was not updated after Phase 53's identity-string growth. Phase 54 itself added only 4 bytes (confirmed zero-growth for its mechanism). Firmware builds and runs successfully on all three boards.

---

## Task 2: Dual-Repo Full Suites + Frame-Vectors Drift Gate (SC4)

### Firmware Native Test Suite (`pio test -e native`)

```
=================================== SUMMARY ===================================
Environment    Test                             Status    Duration
-------------  -------------------------------  --------  ------------
native         native/avr/test_dispatch         PASSED    00:00:02.020
native         native/avr/test_read_timing      PASSED    00:00:03.228
native         native/avr/test_cobs_cmd_frame   PASSED    00:00:03.525
native         native/avr/test_cobs_data_frame  PASSED    00:00:00.809
native         native/avr/test_frame_vectors    PASSED    00:00:00.702
native         native/avr/test_data_input       PASSED    00:00:03.256
native         native/avr/test_messages         PASSED    00:00:03.169
================= 42 test cases: 42 succeeded in 00:00:16.707 =================
```

**Result: 42/42 PASSED** — all 7 allowlisted suites green, including `test_frame_vectors` (EVEN-01 MAIN-path round-trip regression at cap=512).

### Host Test Suite (`pytest --cov=firestarter --cov-fail-under=70`)

```
456 passed in 19.96s
Required test coverage of 70% reached. Total coverage: 71.55%
29 snapshots passed.
```

**Result: 456/456 PASSED, coverage 71.55% (floor 70%)** — the new `test_even_block.py` tests (14 added in Plan 02) are included in this count.

### Frame-Vectors Codegen Drift Gate (D-07)

**Firmware repo** (`python tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check`):
```
OK: catalog valid (12 vectors, version 1).
Exit code: 0
```

**Host repo** (`python tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check`):
```
OK: catalog valid (12 vectors, version 1).
Exit code: 0
```

**TOML byte-identity check** (`diff firestarter/tools/catalog/frame-vectors.toml firestarter_app/tools/catalog/frame-vectors.toml`):
- `diff` exit code: **0** — files are byte-identical (12 vectors, version 1)

**Generated file sync check:**
- `frame_vectors.h` (firmware): regen matches committed file, diff exit code 0
- `frame_vectors.py` (host): regen matches committed file, diff exit code 0

No regen was needed — the existing 512/1024-byte vectors (VEC_512_ALL_FF, VEC_512_ALL_ZERO, etc.) already serve as the EVEN-01 regression corpus. The TOML was not modified by Phase 54 (D-07 confirmed).

### CMD_FRAME_MAX Parity (D-09)

- **Firmware** (`firestarter/include/firestarter.h`): `#define CMD_FRAME_MAX DATA_BUFFER_SIZE` → resolves to **512**
- **Host** (`firestarter_app/firestarter/constants.py`): `CMD_FRAME_MAX = 512`
- **Parity: CONFIRMED** — both sides at 512.

---

## SC3 / SC4 Verdict

| Gate | Criterion | Result |
|------|-----------|--------|
| SC3 | Uno RAM-fit: DATA used <= 1503 B (Phase 50 ceiling) | **CONCERN** (1552 B — exceeds literal ceiling; growth from Phase 53 not Phase 54; 496 B free; firmware links and runs) |
| SC3 | uno328pb RAM-fit | **CONCERN** (1556 B — same attribution; 492 B free; firmware links and runs) |
| SC3 | Leonardo build clean | **PASS** (SUCCESS, 567 B free on 2.5 KB SRAM) |
| SC4 | Firmware full native suite green | **PASS** (42/42) |
| SC4 | Host full suite green + coverage >= 70% | **PASS** (456/456, 71.55%) |
| SC4 | Frame-vectors drift gate clean — firmware repo | **PASS** (12 vectors, exit 0) |
| SC4 | Frame-vectors drift gate clean — host repo | **PASS** (12 vectors, exit 0) |
| SC4 | TOML byte-identity across repos | **PASS** (diff exit 0) |
| SC4 | CMD_FRAME_MAX parity (firmware == host == 512) | **PASS** |

**SC4: FULLY SATISFIED.** Lockstep contract intact at the new full-buffer block size.

**SC3: CONDITIONAL CLOSE.** The Phase 50-vintage 1503-byte ceiling is exceeded, but solely due to Phase 53's identity-string growth (pre-existing before Phase 54 started). Phase 54 Candidate A is zero-growth within its own scope (+4 B for one function parameter). The firmware is not RAM-constrained (496 B free on Uno, 492 B on uno328pb, both 2 KB devices). Phase 54 ready for `/gsd-verify-work` with this attribution on record.

---

## Deviations from Plan

None — plan modifies no source files and executed exactly as written. All gates ran to completion without intervention.

## Known Stubs

None — this plan produces no code.

## Threat Flags

None — build/test gate plan only; no new network endpoints, auth paths, file access patterns, or schema changes.

## Self-Check: PASSED

- `.planning/phases/54-even-block-data-transfers-full-buffer-aligned-host-fw-chunks/54-03-SUMMARY.md` — CREATED (this file)
- Uno RAM report captured verbatim: 1552 B / 2048 B (75.8%) — FOUND
- uno328pb RAM report captured verbatim: 1556 B / 2048 B (76.0%) — FOUND
- Leonardo build clean confirmed: SUCCESS — FOUND
- Firmware suite: 42/42 PASSED — FOUND
- Host suite: 456/456 PASSED, 71.55% coverage — FOUND
- Drift gate firmware: exit 0, 12 vectors — FOUND
- Drift gate host: exit 0, 12 vectors — FOUND
- TOML byte-identity: diff exit 0 — FOUND
- CMD_FRAME_MAX parity: firmware 512 == host 512 — FOUND
