---
phase: 8
slug: convert-state-machine-prefix-call-sites-ok-init-main-end
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-18
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity (PlatformIO `test_framework = unity`) |
| **Framework (host)** | pytest 9.0.3 |
| **Config file (firmware)** | `firestarter/platformio.ini` `[env:native]` |
| **Config file (host)** | `firestarter_app/pyproject.toml` |
| **Quick run (firmware)** | `cd firestarter && pio test -e native -f "*test_messages*"` |
| **Quick run (host)** | `cd firestarter_app && python -m pytest tests/test_decoder.py -v` |
| **Full suite (firmware)** | `cd firestarter && pio test -e native && pio run -e uno && pio run -e leonardo` |
| **Full suite (host)** | `cd firestarter_app && python -m pytest tests/ -v` |
| **Estimated runtime** | ~30 s (firmware native) + ~15 s (host) + ~45 s (board builds) |

---

## Sampling Rate

- **After every task commit:** Run `pio test -e native -f "*test_messages*"` AND `python -m pytest tests/test_decoder.py -v`
- **After every plan wave:** Run full firmware suite + full host suite
- **Before `/gsd-verify-work`:** Full suite must be green AND hardware integration on both Uno + Leonardo
- **Max feedback latency:** ~45 seconds (quick), ~3 minutes (full)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 8-01-* | 01 catalog/codegen | 1 | LMIG-03 / B-03 | — | `[debug]` parsing without injection | unit | `python tools/catalog/codegen.py --catalog tools/catalog/messages.toml --language cpp` | ✅ | ⬜ pending |
| 8-02-* | 02 wire-format len u8→u16 | 2 | LMIG-03 / W-04 | T-W04 (u16 overflow) | u16 frame_len bounded by serial read timeout | unit | `pio test -e native -f "*test_messages*"` + `pytest tests/test_decoder.py` | ✅ (needs update) | ⬜ pending |
| 8-03-* | 03 host parser prefix removal | 3 | LMIG-03 / W-01, W-02 | T-W02 (severity-band routing) | `expect_ack` routes ID-frame OK identical to text | unit | `pytest tests/test_decoder.py -v` | ✅ | ⬜ pending |
| 8-04-* | 04 OK populate-sites + P-01..P-04 | 4 | LMIG-03 / P-01..P-04 | T-P04 (composite frame integrity) | sentinel-byte (0xFF) decode is lossless | unit | `pytest tests/test_decoder.py -v` | ❌ W0 new tests | ⬜ pending |
| 8-05-* | 05 INIT/MAIN/END/DATA populate-sites | 4 | LMIG-03 / W-01, R-02 | — | Two-line emit + state-set | unit | `pytest tests/test_decoder.py -v` | ❌ W0 new tests | ⬜ pending |
| 8-06-* | 06 _check_response strip + response_msg deletion | 5 | LMIG-03 / R-01, R-03 | — | SRAM decreased; no log emits inside switch | smoke + grep | `pio run -e uno && pio run -e leonardo` + `grep -E 'log_info\|log_data' firestarter/src/operation_utils.cpp` (expect zero hits inside _check_response) | ✅ | ⬜ pending |
| 8-07-* | 07 debug() sweep MSG_DEBUG+sub_id | 6 | LMIG-03 / B-01..B-04 | T-B04 (unknown sub_id) | Production build emits no debug bytes | smoke | `pio run -e uno` (no SERIAL_DEBUG flag) | ✅ | ⬜ pending |
| 8-99-* | phase close: hardware integration | end | LMIG-03 (Success Criteria 2,3,4) | — | end-to-end write + read works | manual + automated | `firestarter write -e W27C512 && firestarter read -e W27C512 -o /tmp/out.bin && diff <baseline>` on both boards | ✅ harness | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_decoder.py` — add MSG_OK_INIT_DONE / MSG_MAIN_DONE / MSG_END_DONE ID-frame decode tests (W-01/W-02)
- [ ] `firestarter_app/tests/test_decoder.py` — add MSG_OK_FW_HANDSHAKE composite-frame test (P-04)
- [ ] `firestarter_app/tests/test_decoder.py` — add MSG_OK_REV `u8+u8` shape test with 0xFF sentinel (P-02)
- [ ] `firestarter_app/tests/test_decoder.py` — add MSG_OK_CFG `u32+u32+u8` shape test with 0xFF sentinel (P-03)
- [ ] `firestarter_app/tests/test_decoder.py` — update `test_wire_format_text_catalog_id_rejected_as_id_frame` to drop 0x06 from rejection set (P-04)
- [ ] `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — update byte-offset assertions for `len` field widened to u16 (W-04) — atomic with Group 2 emit change
- [ ] `firestarter_app/tests/conftest.py` — update `build_frame` helper to emit u16 `len` (W-04) — atomic with Group 2 host decoder change
- [ ] `firestarter_app/tests/test_decoder.py` — add MSG_DATA_CHUNK round-trip with chunk-body size > 253 B to exercise u16-required path (W-04)
- [ ] `firestarter/test/native/avr/test_messages/` — add a `test_msg_data_chunk` body asserting the wrapped-chunk frame layout (W-04)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| End-to-end `firestarter write -e W27C512` on real hardware (Uno) | LMIG-03 / Success Criterion 2 | Requires physical EPROM in the RURP socket | Run `firestarter write -e W27C512 /path/to/known.bin`; confirm INIT/MAIN/END renders without text prefixes in CLI |
| End-to-end on real hardware (Leonardo) | LMIG-03 / Success Criterion 2 | Same as above; Leonardo control per repo convention | Run on Leonardo; confirm parity with Uno output |
| Byte-identical chip-read vs Phase 7 baseline | LMIG-03 / Success Criterion 3 | Requires same physical chip and stored baseline | `firestarter read -e W27C512 -o /tmp/p8-out.bin && diff /tmp/p8-out.bin <Phase 7 baseline file>` — exit 0 |
| Flash size measurably smaller than Phase 7 baseline | LMIG-03 / Success Criterion 4 | Read from build output | After Group 7 close: capture `pio run -e uno` + `pio run -e leonardo` flash %, compare to `07-FLASH-MEASUREMENT.md` (Leonardo 27,026 / Uno 24,838) |
| SRAM win from `response_msg[96]` deletion | R-01 | Read from build output `pio run` `RAM:` line | Capture before/after R-01 commit |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 45s (quick); < 3 min (full)
- [ ] `nyquist_compliant: true` set in frontmatter once plans land

**Approval:** pending
