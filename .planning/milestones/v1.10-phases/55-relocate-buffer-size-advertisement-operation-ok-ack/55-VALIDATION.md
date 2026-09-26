---
phase: 55
slug: relocate-buffer-size-advertisement-operation-ok-ack
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-04
---

# Phase 55 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Dual-repo: firmware (`firestarter/`, Unity) + host (`firestarter_app/`, pytest).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Firmware framework** | Unity (PlatformIO native env) |
| **Host framework** | pytest 7.x |
| **Config file** | `firestarter/platformio.ini`; `firestarter_app/pyproject.toml` |
| **Firmware quick run** | `cd /workspaces/firestarter && pio test -e native -f "*test_messages*"` |
| **Host quick run** | `cd /workspaces/firestarter_app && pytest tests/test_even_block.py -x` |
| **Full suite (firmware)** | `cd /workspaces/firestarter && pio test` |
| **Full suite (host)** | `cd /workspaces/firestarter_app && pytest --cov=firestarter --cov-fail-under=70` |
| **Drift/parity gate** | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` + `bash tools/catalog/sync_to_subrepos.sh` |
| **Estimated runtime** | firmware ~30s · host ~25s |

---

## Sampling Rate

- **After every task commit:** Run `pio test -e native && pytest tests/ -x` (whichever repo the task touched)
- **After every plan wave:** Run full suite both repos: `pio test && pytest --cov=firestarter --cov-fail-under=70`
- **Before `/gsd-verify-work`:** Full suite green in BOTH repos; `bash tools/catalog/sync_to_subrepos.sh` exits 0 (drift gate)
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Requirement | SC | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|-------------|----|-----------------|-----------|-------------------|-------------|--------|
| catalog: add `bytes` param to MSG_OK_READY | CAP-01 | SC2 | N/A | drift gate | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | ✅ existing | ⬜ pending |
| fw: revert FW_VERSION to `<version>:<board>` | CAP-01 | SC1 | N/A | unit (fw) | `pio test -e native -f "*test_messages*"` | extend | ⬜ pending |
| fw: 4 emit sites → `LOG_OK_ID_U16(MSG_OK_READY, DATA_BUFFER_SIZE)` | CAP-01 | SC2 | N/A | unit (fw) | `pio test -e native -f "*test_messages*"` | new case | ⬜ pending |
| host: `_decode_id_frame` override extracts u16 → `firmware_max_chunk` | CAP-01 | SC3b | un-advertising ack must NOT be dropped | unit (host) | `pytest tests/test_even_block.py::TestCapSafeDefault -x` | ❌ W0 | ⬜ pending |
| host: `_calculate_buffer_size()` returns 512 when absent (no raise) | CAP-01 | SC3a | absent capability → safe 512 floor, never overflow | unit (host) | `pytest tests/test_even_block.py::TestCapSafeDefault -x` | ❌ W0 | ⬜ pending |
| host: remove `fw_fields[2]/[3]` identity parse + `FirmwareOutdatedError` raise | CAP-01 | SC1/SC3 | N/A | unit (host) | `pytest tests/test_serial_comm.py -x` | update | ⬜ pending |
| EVEN-01 preserved: chunks stay 512/1024, whole-block transfer | CAP-01 | SC4 | N/A | unit | `pio test -e native && pytest tests/test_frame_vectors.py -x` | ✅ existing | ⬜ pending |
| dual-repo sync: messages.toml byte-identical + parity | CAP-01 | SC5 | N/A | drift gate | `bash tools/catalog/sync_to_subrepos.sh && pio test -e native && pytest -x` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements (RED tests needed before implementation)

- [ ] `firestarter_app/tests/test_even_block.py` — add `TestCapSafeDefault`:
  - [ ] `test_absent_firmware_max_chunk_returns_512` — absent param → `_calculate_buffer_size()` returns 512, NO `FirmwareOutdatedError` (CAP-01 SC3a; pins the Phase 54 D-05 reversal)
  - [ ] `test_512_ok_ready_ack_via_decode_override` — 2-byte ack body → `firmware_max_chunk == 512` (CAP-01 SC3b)
- [ ] Update `firestarter_app/tests/test_even_block.py::test_calculate_buffer_size_raises_without_max_chunk` — change `pytest.raises(FirmwareOutdatedError)` to `assert result == 512`
- [ ] Update/remove the 3 Phase 54 identity-string parse tests in `firestarter_app/tests/test_serial_comm.py` (no longer parse `<buf>:<maxchunk>` from identity)
- [ ] `firestarter/test/test_messages/` (Unity) — extend to assert `MSG_OK_READY` emits a frame carrying a 2-byte param (the u16 `DATA_BUFFER_SIZE`); current test covers zero-param frames

*If RED-first is not preferred, implement these in Wave 1 alongside the source change.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `firestarter fw` prints `<version>:<board>` only | CAP-01 SC1 | CLI output against live/mocked firmware | Run `firestarter fw`; assert no `:512`/`:1024` or maxchunk suffix |
| Full write+verify on real Leonardo (1024) | CAP-01 SC4 | Hardware bench (per memory: use Leonardo/ACM0, NOT uno328pb — program brownout) | Write+verify a known EPROM image; confirm chunks sized to 1024, whole-block transfer, byte-exact |

*Host/firmware unit + drift gates cover all non-hardware behaviors.*

---

## Validation Sign-Off

- [ ] All tasks have an automated verify command or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING (❌) references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
