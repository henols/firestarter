---
phase: 54
slug: even-block-data-transfers-full-buffer-aligned-host-fw-chunks
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-04
---

# Phase 54 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `54-RESEARCH.md` § Validation Architecture (mechanism: Candidate A — data-path NUL-skip).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Unity (firmware, PlatformIO native env) + pytest (host) |
| **Config file** | `firestarter/platformio.ini`, `firestarter_app/pyproject.toml` |
| **Quick run command** | `pio test -e native && pytest firestarter_app/tests/test_frame_vectors.py firestarter_app/tests/test_even_block.py -x` |
| **Full suite command** | `pio test && (cd firestarter_app && pytest --cov=firestarter --cov-fail-under=70)` |
| **Estimated runtime** | ~60 seconds (native + host); firmware build/RAM gate adds ~30s |

---

## Sampling Rate

- **After every task commit:** Run `pio test -e native && (cd firestarter_app && pytest tests/ -x)`
- **After every plan wave:** Run `pio test && (cd firestarter_app && pytest --cov=firestarter --cov-fail-under=70)`
- **Before `/gsd-verify-work`:** Full suite green AND RAM gate (SC3/D-08): `pio run -e uno 2>&1 | grep "DATA used"` asserts ≤ ~545 B free-RAM ceiling held
- **Max feedback latency:** ~60 seconds (software); bench (SC1 on-wire) is operator-gated

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 54-XX-XX | fw | 1 | EVEN-01 (SC1) | — | 512-byte data chunk decodes on MAIN path (cap=512) | unit | `pio test -e native -f "*test_frame_vectors*"` | ✅ extend | ⬜ pending |
| 54-XX-XX | fw | 1 | EVEN-01 (SC1) | — | 1024-byte data chunk decodes on MAIN path (cap=1024) | unit | `pio test -e native -f "*test_frame_vectors*"` | ✅ extend | ⬜ pending |
| 54-XX-XX | fw | 1 | EVEN-01 (SC1/SC4) | T-54 overflow guard | 512-byte chunk STILL returns -2 on CMD_IDLE path (cap=511) | unit | `pio test -e native -f "*test_frame_vectors*"` | ✅ extend | ⬜ pending |
| 54-XX-XX | fw | 1 | EVEN-01 (SC4) | — | Round-trip `cobs_encode(512+CRC8)` → decode(cap=512) → original 512 bytes | unit | `pio test -e native -f "*test_frame_vectors*"` | ✅ extend | ⬜ pending |
| 54-XX-XX | host | 1 | EVEN-01 (D-04) | V5 input validation | `firmware_max_chunk` parsed from 4-field identity string (isdigit guard) | unit | `pytest tests/test_serial_comm.py -x -k max_chunk` | ✅ extend | ⬜ pending |
| 54-XX-XX | host | 2 | EVEN-01 (D-04) | — | `_calculate_buffer_size()` returns `firmware_max_chunk` directly (no −2) | unit | `pytest tests/test_eprom_operations.py -x -k buffer_size` | ✅ extend | ⬜ pending |
| 54-XX-XX | host | 1 | EVEN-01 (SC2) | — | 65536 % 512 == 0 (no-remainder, Uno) | unit | `pytest tests/test_even_block.py::test_full_chip_no_remainder_uno -x` | ❌ W0 | ⬜ pending |
| 54-XX-XX | host | 1 | EVEN-01 (SC2) | — | 65536 % 1024 == 0 (no-remainder, Leonardo) | unit | `pytest tests/test_even_block.py::test_full_chip_no_remainder_leonardo -x` | ❌ W0 | ⬜ pending |
| 54-XX-XX | gate | 3 | EVEN-01 (SC3/D-08) | — | Uno SRAM under ~545 B free-RAM ceiling after change (zero-growth expected) | build/RAM | `pio run -e uno 2>&1 \| grep "DATA used"` | build output | ⬜ pending |
| 54-XX-XX | gate | 3 | EVEN-01 (SC3/D-08) | — | uno328pb SRAM under the ceiling | build/RAM | `pio run -e uno328pb 2>&1 \| grep "DATA used"` | build output | ⬜ pending |

*Task IDs are placeholders — the planner assigns concrete IDs. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter_app/tests/test_even_block.py` — no-remainder assertions (EVEN-01 SC2)
- [ ] New Unity MAIN-path cases in `firestarter/test/native/.../test_frame_vectors/` — cap=512/1024 decode + CMD_IDLE overflow at 512 bytes (EVEN-01 SC1/SC4)
- [ ] `firmware_max_chunk` attribute declaration in `SerialCommunicator.__init__` + `_probe_port` parse extension (host `serial_comm.py`)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| On-wire frame sizes are full buffer (512/1024), no `buffer − 2` | EVEN-01 (SC1) | Requires Uno + Leonardo bench hardware; operator-gated per Phase 53 pattern | Run a write/verify against a real chip; capture on-wire DATA frame sizes; assert 512 (Uno) / 1024 (Leonardo), no 510/1022 |
| Full-chip (65536 B) write/verify completes with one fewer round trip | EVEN-01 (SC2) | Hardware end-to-end timing/round-count observation | Bench write+verify of a 64 KB image; confirm 128×512 (Uno) whole blocks, no 256-byte remainder write |

*Software tests (SC3 RAM, SC4 round-trip, no-remainder arithmetic) are fully automated; only the on-wire SC1/SC2 bench legs are operator-gated.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (`test_even_block.py`, Unity MAIN-path cases, `firmware_max_chunk` attr)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
