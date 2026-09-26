---
phase: 50
slug: data-path-framing-layer-automatic-resync-dual-repo-lockstep
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-01
---

# Phase 50 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Dual-repo: firmware (Unity/PlatformIO `native`) + host (pytest). Both must be green at the phase gate.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity via PlatformIO `[env:native]` (ArduinoFake Serial mock) |
| **Framework (host)** | pytest |
| **Firmware config** | `firestarter/platformio.ini` `[env:native]`, `test_filter` includes `native/avr/test_messages` |
| **Host config** | `firestarter_app/pyproject.toml` `[dev]`/`[test]` extras; ruff+mypy+pytest CI gate (`.github/workflows/ci.yml`) |
| **Firmware quick run** | `pio test -e native -f "*test_messages*"` |
| **Firmware full suite** | `pio test -e native` |
| **Host quick run** | `pytest tests/ -x -k cobs` |
| **Host full suite** | `pytest --cov-fail-under=70` |
| **Firmware RAM gate** | `pio run -e uno` (assert RAM < 545 B free ceiling, no second buffer) |
| **Estimated runtime** | ~30 s (host pytest quick) / ~60–90 s (fw native suite) / ~30 s (uno build) |

---

## Sampling Rate

- **After every task commit:** Run firmware `pio test -e native -f "*test_messages*"` (fw tasks) / `pytest -x -k cobs` (host tasks)
- **After every plan wave:** Run `pio test -e native` (fw full) + `pytest --cov-fail-under=70` (host full) + `pio run -e uno` RAM report
- **Before `/gsd-verify-work`:** Both full suites green AND RAM report under the ~545 B free-RAM ceiling
- **Max feedback latency:** ~90 seconds

---

## Per-Task Verification Map

> Plan/task IDs are filled by the planner; this maps each phase requirement to its load-bearing automated check.

| Req ID | Behavior | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|--------|----------|------------|-----------------|-----------|-------------------|-------------|--------|
| FRAME-01 | `[len_u16][xor]` boundary replaced by `[COBS(payload+CRC8)][0x00]`, host↔fw write path | — | Malformed frame rejected, never mis-parsed as length | unit (round-trip) | `pio test -e native -f "*test_messages*"` + `pytest -k cobs_roundtrip` | ❌ W0 (new cases) | ⬜ pending |
| FRAME-02 | Receiver discards to next `0x00`, recovers within ONE frame after injected fault; flipped `#` marker re-anchors | — | Bounded desync (one frame); immediate clean error, no 2 s hang | unit (fault-injection, both repos) | `pio test -e native -f "*test_messages*"` + `pytest -k cobs_resync` | ❌ W0 | ⬜ pending |
| FRAME-03 | Streaming encode/decode-in-place, no second ~512 B buffer, < 545 B free RAM | — | N/A | build report | `pio run -e uno` (parse RAM line) | ✅ build exists; assertion scripted (W0) | ⬜ pending |
| FRAME-04 | Full 512 B (Uno) / 1024 B (Leonardo) payload frames without operator-visible re-chunking | — | All-`0x00` blank-EPROM payload frames within RAM | unit (full-buffer round-trip) | `pytest -k cobs_full_buffer` + `pio test -e native` | ❌ W0 | ⬜ pending |
| CRC-01 | CRC8-CCITT poly 0x07, seed 0x00, no reflection/final-XOR, over raw payload; byte-compatible both repos | — | Corrupted payload → CRC mismatch → resync, never silently accepted | unit (CRC pin) | existing `test_crc_polynomial_smoke` + new `pytest -k crc8_data_payload` | ⚠ partial (fw smoke exists; data-payload case new) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### SC2 assertion shape (the load-bearing one)

The resync tests MUST assert **bounded recovery**, not mere detection:

- **Host pytest:** feed the decoder `[corrupt-CRC frame][0x00][valid frame][0x00]` and a variant with a flipped/missing delimiter; assert (a) the first frame raises a clean exception / returns an error with no 2 s hang (assert wall-clock < ~0.1 s, or that no blocking read is entered), AND (b) the **next** valid frame decodes to the correct payload. Use an in-memory/fake serial (feed `bytes`), not real hardware.
- **Firmware Unity (`test_messages/`):** using the ArduinoFake `Serial.read`/`available` mock (queued byte vector — extend the existing `When(OverloadedMethod(... read ...))` pattern), feed `[garbled frame][0x00][valid frame][0x00]` into `rurp_communication_read_data`; assert the first call returns `res < 0` AND the read cursor is left at the start of the valid frame, AND a second call returns the correct decoded length with `data_buffer` matching the expected payload.

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_cobs.py` (or extend `tests/test_decoder.py`) — `cobs_encode`/`cobs_decode` round-trip, all-zero 512 B payload, resync-after-fault, CRC8-over-payload — covers FRAME-01/02/04, CRC-01
- [ ] `firestarter/test/native/avr/test_messages/` new RUN_TEST cases for COBS decode-in-place + resync — covers FRAME-01/02
- [ ] ArduinoFake `Serial.read`/`available` queued-byte mock helper in `test_messages/` (suite currently only mocks `Serial.write`; the decoder test needs `read`/`available`)
- [ ] A scripted RAM-ceiling assertion around `pio run -e uno` (parse the `RAM: … (used N bytes…)` line) — covers FRAME-03

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Post-change Uno RAM report under ceiling | FRAME-03 | Build-output inspection; the streaming-no-second-buffer claim is confirmed by the linker RAM line, scriptable but operator-reviewed | Run `pio run -e uno`; confirm `RAM: [== ] used` line shows free RAM ≥ ~545 B and no new ~512 B static buffer vs Phase-49 baseline (1503/2048 B used) |
| Bench round-trip across Uno/Leonardo/uno328pb | (deferred SC) | Requires physical boards + shield-rev confirmation | **Out of scope — Phase 53.** Not validated here. |

*Bench verification (Phase 53) and full byte-compat round-trip matrix (Phase 52) are explicitly out of Phase-50 scope.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (4 items above)
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
