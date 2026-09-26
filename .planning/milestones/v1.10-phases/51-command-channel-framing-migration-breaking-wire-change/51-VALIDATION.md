---
phase: 51
slug: command-channel-framing-migration-breaking-wire-change
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-02
---

# Phase 51 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Dual-repo: firmware (`firestarter/`, Unity/PlatformIO) + host (`firestarter_app/`, pytest).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity via PlatformIO `[env:native]` |
| **Framework (host)** | pytest + coverage |
| **Config file (firmware)** | `firestarter/platformio.ini` — `[env:native]` (lines 67-101) |
| **Config file (host)** | `firestarter_app/pyproject.toml` / `pytest.ini` |
| **Quick run command** | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` (fw) · `python -m pytest tests/test_serial_comm.py tests/test_cobs.py -x` (host) |
| **Full suite command** | `pio test -e native` (fw) · `python -m pytest --cov-fail-under=70` (host) |
| **Estimated runtime** | ~30 seconds (fw native) + ~15 seconds (host) |

---

## Sampling Rate

- **After every task commit:** Run `pio test -e native -f "native/avr/test_cobs_cmd_frame"` + `python -m pytest tests/test_serial_comm.py tests/test_cobs.py -x`
- **After every plan wave:** Run `pio test -e native` + `python -m pytest --cov-fail-under=70`
- **Before `/gsd-verify-work`:** Full dual-repo suite must be green
- **Max feedback latency:** ~45 seconds

---

## Per-Task Verification Map

> Task IDs are provisional (plan IDs assigned by gsd-planner). The Req/behavior/test-type rows are the binding contract; the planner maps them onto concrete tasks.

| Behavior | Repo | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|----------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| Corrupted command frame → `rurp_communication_read_data()` returns < 0, `parse_json()` never called | firmware | FRAME-05 / V5 | T-49-01 / §4.4 | CRC8-before-parse: CRC-failed frame discarded before parser sees bytes | unit (Unity) | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` | ❌ W0 (new dir) | ⬜ pending |
| Valid framed command → decoded correctly, `parse_json()` receives correct payload | firmware | FRAME-05 | — | — | unit (Unity) | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` | ❌ W0 | ⬜ pending |
| Oversized frame (no `0x00`) → bounded recovery (drain + return, no hang) | firmware | FRAME-05 / D-06 | DoS | `CMD_FRAME_MAX` cap + decoder overflow guard → `_drain_to_delimiter()` | unit (Unity) | `pio test -e native -f "native/avr/test_cobs_cmd_frame"` | ❌ W0 | ⬜ pending |
| `send_json_command()` emits correct COBS+CRC8 frame as one atomic write | host | FRAME-05 | SAFE-01 (B) | single `send_bytes()`; no split delimiter write | unit (pytest) | `python -m pytest tests/test_serial_comm.py -x` | ⚠️ file exists, new fns | ⬜ pending |
| Version probe (`CMD_FW_VERSION`) goes through framed path, not raw text | host | FRAME-05 / D-04 | — | no plaintext command escape hatch | unit (pytest) | `python -m pytest tests/test_serial_comm.py -x` | ❌ new fn | ⬜ pending |
| COBS primitives + CRC8 polynomial unchanged from Phase 50 | both | CRC-01 | — | regression guard | regression | `pio test -e native -f "native/avr/test_cobs_data_frame"` + `pytest tests/test_cobs.py` | ✅ Phase 50 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp` — new Unity suite: command-frame decode + CRC8-reject + resync/size-cap
- [ ] `firestarter/test/native/avr/test_cobs_cmd_frame/host_stubs.cpp` — minimal stubs (include `_shared/host_stubs_common.inc`; model on `test_cobs_data_frame/host_stubs.cpp`)
- [ ] `firestarter/platformio.ini` — add `native/avr/test_cobs_cmd_frame` to `test_filter` + `build_flags` `-I` path
- [ ] `firestarter_app/tests/test_serial_comm.py` — add test functions: framed `send_json_command()` output, version-probe framing (D-04), CRC8-reject path

*Existing Phase-50 suites (`test_cobs_data_frame`, host `test_cobs.py`) stay green as the regression layer.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| End-to-end framed command round-trip on real hardware (Uno/Leonardo/uno328pb) | FRAME-05 / SC4 | Requires physical board + shield; operator-gated | Deferred to **Phase 53** (bench). Not part of Phase 51 sign-off. |

*Full byte-compat round-trip / lockstep contract matrix (incl. pathological all-delimiter command payloads) is **Phase 52** — do not pull forward.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (new `test_cobs_cmd_frame` dir + host test fns)
- [ ] No watch-mode flags
- [ ] Feedback latency < 45s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
