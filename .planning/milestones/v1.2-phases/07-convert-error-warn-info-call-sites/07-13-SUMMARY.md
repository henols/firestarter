---
phase: 07-convert-error-warn-info-call-sites
plan: 13
type: execute
status: complete
completed: 2026-05-18
requirements:
  - LMIG-02
key_files:
  created:
    - .planning/phases/07-convert-error-warn-info-call-sites/07-FLASH-MEASUREMENT.md
  modified: []
---

# Plan 07-13 SUMMARY — Phase-Close Verification

## Outcome

All four Phase 7 ROADMAP success criteria verified PASS. The phase is ready for `/gsd-verify-work` and milestone-level verification.

| SC | Subject | Result | Detail |
|----|---------|--------|--------|
| SC#1 | Legacy log-macro grep gate (firestarter/src + include + lib) | PASS | Zero non-comment, non-#define hits; the 21 grep matches in `logging.h` are all `#define` macro definitions (Phase 9 will delete them) — exempt per plan's filter design |
| SC#2 | ERROR/WARN/INFO render via catalog decoder; decoder-toggle diff | PASS | 8 distinct catalog IDs decoded end-to-end on both Uno + Leonardo; parameterized rendering verified on 4 IDs (VPP_HIGH, CHIP_ID_MISMATCH, CMD_TIMEOUT, TOKEN_COUNT); decoder OFF makes them vanish; OK/INIT/DATA text acks byte-identical in both passes |
| SC#3 | Host pytest text-coexistence suite (test_decoder.py) | PASS | 12/12 tests pass |
| SC#4 | Both boards compile, binary size drops measurably vs Phase 6 close | PASS | Leonardo 28,292 → 27,026 (-1,266 B = +4.4 pct points free); Uno 26,100 → 24,838 (-1,262 B = +3.9 pct points free). Both deltas significantly exceed RESEARCH §9 estimate of 450-650 B Leonardo reduction. |

## Task Execution

| Task | Type | Result | Commits |
|------|------|--------|---------|
| Task 1: SC#1 grep gate + SC#3 host pytest + SC#4 dual-board build + write 07-FLASH-MEASUREMENT.md | auto | PASS | `cd24555` |
| Task 2: SC#2 manual decoder-toggle diff on Uno + Leonardo | checkpoint:human-verify | PASS (chip-less sweep) | `fcf4ae2` |

## SC#2 Hardware Verification Detail

Both boards (Uno `/dev/ttyACM0`, Leonardo `/dev/ttyACM1`) flashed clean from the post-Phase-7 firmware. Two passes per board:
- **Decoder ON** (vanilla `serial_comm.py` at SHA `c4d66ff`)
- **Decoder OFF** (one-line `return None` short-circuit at top of `_decode_id_frame`)

Bench bypass `FIRESTARTER_DEV_ALLOW_PRE_V12=1` was used to skip the host-side firmware-version gate (firmware identifies as `2.0.11-dev` — major-version bump to v3 happens in Phase 9).

Catalog IDs verified decoded with full parameter rendering, vanishing in decoder-OFF pass:

- `MSG_INFO_INIT_START`, `MSG_INFO_MAIN_START`, `MSG_INFO_TOKEN_COUNT` (u8 param: 5/39/40/44)
- `MSG_ERR_NO_CHIP_ID`, `MSG_ERR_NOT_SUPPORTED` (no params)
- `MSG_ERR_CMD_TIMEOUT` (u8 cmd param: 8, 11, 12)
- `MSG_ERR_CHIP_ID_MISMATCH` (2×u16 → "Chip ID 0x4001 dont match expected ID 0xbfb5")
- `MSG_ERR_VPP_HIGH` (2×u32 mV → "VPP is high: 13.1V > 12.0V")

State-machine text acks (`OK:`, `INIT:`, `DATA:`) byte-identical in both passes — confirms the Phase-7-vs-Phase-8 boundary (Phase 8 converts these).

`serial_comm.py` revert verified clean: `git diff --exit-code firestarter/serial_comm.py` exits 0 after the decoder-OFF sweep was completed and the file was restored via `git checkout`.

## Coverage Gaps Documented (Forward Work)

Catalog IDs that the chip-less sweep cannot exercise (documented in the artifact §"Coverage gaps"):

- `MSG_ERR_WRITE_FAILED` (eprom.cpp) — needs successful write attempt with chip
- `MSG_ERR_VPP_LOW` (eprom + flash_intel) — both regulators stayed within band
- `MSG_ERR_OP_TIMEOUT` (flash_utils.cpp) — needs flash op timeout
- `MSG_ERR_FL4_VERIFY_TIMEOUT` (flash_type_4.cpp) — needs flash-type-4 chip
- `MSG_ERR_MEM_SIZE_TOO_SMALL` (eeprom_28c.cpp) — needs chip with mismatched size
- `MSG_ERR_VERIFY`, `MSG_ERR_NOT_BLANK` (memory.cpp) — need chip reads
- `dev_tools.cpp` INFO sites — FLAG_VERBOSE-gated; not triggered by current dev subcommands

These IDs remain covered by the native unit test suite (`test_dispatch` 15/15 + `test_messages` 5/5 — Task 1 SC#4 PASS) and the codegen drift gate (CI asserts byte-identical vendor copies + catalog→generated artifact integrity). They will get a chip-installed sweep during Phase 9 milestone-close hardware verification.

## Flash Savings Trend

| Reference point | Leonardo Flash | Uno Flash | Delta vs Phase 6 close |
|------------------|----------------|-----------|------------------------|
| v1.1 close | (see 06-FLASH-MEASUREMENT.md) | (see 06-FLASH-MEASUREMENT.md) | — |
| Phase 6 close (LFW emit path live, no call-site conversion yet) | 28,292 B (98.7%) | 26,100 B (80.9%) | 0 (baseline) |
| **Phase 7 close (this plan)** | **27,026 B (94.3%)** | **24,838 B (77.0%)** | **-1,266 B / -1,262 B** |
| Phase 9 close TBD (after legacy log macros deleted) | TBD | TBD | TBD |

## Decision Log

- **D-01 honored**: OK/DATA-branch log calls in `_check_response` preserved through this plan; SC#2 confirms text path is unchanged byte-for-byte.
- **D-03 honored**: each catalog gap (07-02) was added in a separate `chore(catalog):` commit; SC#1 confirms no leftover legacy calls remain after the catalog work is complete.

## Ready For

- `/gsd-verify-work 7` — host-decoder + protocol-shape end-to-end UAT
- `/gsd-discuss-phase 8` — OK/DATA call-site conversion (state-machine acks)
- Optional chip-installed extension sweep before Phase 9 if you want richer Phase-9-baseline data
