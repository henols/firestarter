---
phase: 7
slug: convert-error-warn-info-call-sites
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-18
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `07-RESEARCH.md` §7 (Validation Architecture).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | Unity via PlatformIO `[env:native]` |
| **Framework (host)** | pytest 7+ |
| **Config file (firmware)** | `firestarter/platformio.ini` |
| **Config file (host)** | `firestarter_app/pyproject.toml` |
| **Quick run (firmware)** | `cd firestarter && pio test -e native` |
| **Quick run (host)** | `cd firestarter_app && python -m pytest tests/ -q` |
| **Full build check** | `cd firestarter && pio run -e uno && pio run -e leonardo` |
| **Estimated runtime (full)** | ~90 seconds (firmware build + native tests + host pytest) |

---

## Sampling Rate

- **After every task commit:** `cd firestarter && pio test -e native`
- **After every plan wave (populate-site wave, direct-log wave):** `pio run -e uno && pio run -e leonardo && pio test -e native`
- **Before `/gsd-verify-work`:** Full suite must be green across both sub-repos plus SC#1 grep returns 0 plus `07-FLASH-MEASUREMENT.md` written.
- **Max feedback latency:** ~30s for `pio test -e native`; ~60s including dual-board build.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 (infra: macros) | 1 | LMIG-02 SC#4 | — | `logging_id.h` adds 12 unconditional severity macros without altering wire frame emit | unit | `cd firestarter && pio test -e native -f "*test_messages*"` | ✅ existing (`test_rurp_log_id.cpp`) | ⬜ pending |
| 07-02-* | 02..07 (populate-site wave per PROM) | 2 | LMIG-02 SC#1, SC#2 | — | Each `proms/*.cpp` populate-site emits via `rurp_log_id` AND sets `response_code` — no double-emit | unit | `cd firestarter && pio test -e native -f "*test_dispatch*"` after each PROM-module commit | ✅ existing (`test_configure_memory.cpp`) | ⬜ pending |
| 07-03-* | 08 (`operation_utils.cpp` + `_check_response` surgical edit + breadcrumb deletion) | 3 | LMIG-02 SC#1, SC#3 | — | ERROR case returns false without log_*; WARNING case falls through without log_*; OK + DATA branches untouched | unit | `cd firestarter && pio test -e native -f "*test_dispatch*"` | ✅ existing | ⬜ pending |
| 07-04-* | 09 (`firestarter.cpp` 20 sites incl. firestarter.cpp:171 hybrid + firestarter.cpp:86 dead-code deletion) | 3 | LMIG-02 SC#1 | — | All 20 direct call-sites use `LOG_*_ID_*`; dead `response_code` block removed | build+unit | `pio run -e uno && pio run -e leonardo && pio test -e native` | ✅ existing | ⬜ pending |
| 07-05-* | 10..12 (`dev_tools.cpp`, `eprom_operations.cpp`, `hardware_operations.cpp`) | 3 | LMIG-02 SC#1 | — | All direct-log sites converted; DEV_TOOLS-gated INFO still emits via `LOG_INFO_ID_*` | build | `pio run -e uno && pio run -e leonardo` | ✅ existing | ⬜ pending |
| 07-CATGAP-* | catalog gap chores (3 commits before affected populate-site commits) | 0 | LMIG-02 D-03 | — | `MSG_ERR_VPP_HIGH`, `MSG_ERR_CHIP_ID_MISMATCH`, `MSG_ERR_MEM_SIZE_TOO_SMALL` added; codegen+sync runs clean; CI drift gate passes | drift gate | `cd .planning/catalog && python codegen.py && ./sync_to_subrepos.sh && cd ../.. && git diff --exit-code firestarter/include/messages.h firestarter_app/firestarter/messages.py` | ✅ existing (Phase 6 codegen) | ⬜ pending |
| 07-VERIFY-grep | verification — SC#1 grep | gate | LMIG-02 SC#1 | — | Zero remaining legacy macro call-sites in firestarter/src/ | grep gate | `count=$(grep -rnE "log_info_const\|log_info_format\|log_warn[^_]\|log_error_const\|log_error_format\|firestarter_(error\|warning)_response_format" firestarter/src/ firestarter/include/ firestarter/lib/ 2>/dev/null \| grep -v "//" \| grep -v "^[^:]*:[[:space:]]*#define" \| wc -l); [ "$count" -eq 0 ]` (POSIX-portable counted form; non-zero count names the exact failure mode) | n/a | ⬜ pending |
| 07-VERIFY-e2e | verification — SC#2 toggle | gate | LMIG-02 SC#2 | — | Host renders ERROR/WARN/INFO via `_decode_id_frame`; toggling decoder off makes exactly those lines disappear; temporary `_decode_id_frame` short-circuit edit REVERTED (`git diff --exit-code firestarter/serial_comm.py` exits 0) | E2E manual | Run `firestarter write -e W27C512` against real hardware or `firestarter_test.sh` against the simulator harness; capture output with decoder on, then again with `--no-decode` (or equivalent) and diff; finally `cd firestarter_app && git diff --exit-code firestarter/serial_comm.py` exits 0 | n/a | ⬜ manual |
| 07-VERIFY-acks | verification — SC#3 acks stay text | gate | LMIG-02 SC#3 | — | `OK:` / `INIT:` / `MAIN:` / `END:` / `DATA:` prefixes still emit as text | pytest regression | `cd firestarter_app && python -m pytest tests/test_decoder.py -v` (text-coexistence tests) | ✅ existing | ⬜ pending |
| 07-VERIFY-size | verification — SC#4 flash | gate | LMIG-02 SC#4 | — | Both boards build; Phase 7 firmware binary smaller than Phase 6 close baseline (Leonardo 98.7% used / 380 bytes free; Uno 80.9% used) | build + measurement | `pio run -e uno && pio run -e leonardo`, parse `.pio/build/{uno,leonardo}/firmware.elf` size output, append delta to `07-FLASH-MEASUREMENT.md` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

No new test files are required. All infrastructure was installed by Phase 6:

- `firestarter/test/native/avr/test_messages/test_rurp_log_id.cpp` — covers `rurp_log_id` frame emit path
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — covers dispatch routing + `response_code` flow
- `firestarter_app/tests/test_decoder.py` — 12 tests covering binary frame decode, text coexistence, error paths

**Optional extension (Claude's Discretion, not required for phase gate):**

- [ ] Add 2-3 new tests to `firestarter_app/tests/test_decoder.py` covering multi-param MSG IDs Phase 7 actually emits (e.g., `MSG_ERR_WRITE_FAILED` u24+u8+u16 and `MSG_WARN_VPP_LOW` 4×u16). Improves SC#2 coverage in the automated suite.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ERROR/WARN/INFO lines render via catalog decoder; toggle decoder off and those lines disappear (SC#2) | LMIG-02 SC#2 | Requires end-to-end firmware-host round-trip; no isolated unit-test surface for "decoder produces same line as legacy text path" because the legacy text path is what's being deleted | Run `firestarter write -e W27C512` (canon chip from v1.0) against real hardware OR `firestarter_test.sh` against the simulator harness. Capture host stdout twice: (a) normal (decoder ON), (b) with the decoder disabled via host flag or temporary `_decode_id_frame` short-circuit. The (a) output should show readable INFO/WARN/ERROR lines; (b) should show those exact lines as raw binary or missing. Diff confirms catalog round-trip works. Mirror Uno + Leonardo per project convention (memory: "Always mirror Uno tests on Leonardo"). After both board cycles, verify `git diff --exit-code firestarter/serial_comm.py` exits 0 — temporary short-circuit edit reverted. |
| Both boards remain flashable and self-test (regression smoke) | LMIG-02 SC#4 | Hardware-in-the-loop flash + read-back required to confirm no behavioral regression beyond size | After `pio run -e uno && pio run -e leonardo` succeed, flash each board, run `firestarter --hw-rev` plus a single `read -e W27C512` or `info -e W27C512` end-to-end. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify command OR are listed in Manual-Only Verifications
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (per-commit `pio test -e native` satisfies this)
- [x] Wave 0 covers all MISSING references (no MISSING — all infra exists from Phase 6)
- [x] No watch-mode flags (PlatformIO `pio test` is one-shot; pytest `-q` is one-shot)
- [x] Feedback latency < 60s for `pio test -e native`; < 120s including dual-board build
- [x] `nyquist_compliant: true` set in frontmatter after planner integrates this map

**Approval:** approved 2026-05-18
</content>
</invoke>