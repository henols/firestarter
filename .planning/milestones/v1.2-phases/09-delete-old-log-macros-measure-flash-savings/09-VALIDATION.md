---
phase: 9
slug: delete-old-log-macros-measure-flash-savings
status: draft
nyquist_compliant: false
wave_0_complete: true
created: 2026-05-19
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source of truth: `09-RESEARCH.md` §"Validation Architecture" (lines 660-710).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Frameworks** | Firmware: PlatformIO + Unity (`[env:native]`). Host: pytest 9.x + `pyproject.toml`. |
| **Config files** | `firestarter/platformio.ini` (lines 43-67 = `[env:native]`); `firestarter_app/pyproject.toml` `[tool.pytest.ini_options]`. |
| **Quick run command** | `cd firestarter && pio run -e leonardo && cd ../firestarter_app && pytest tests/test_fwguard.py tests/test_decoder.py -q` |
| **Full suite command** | `cd firestarter && pio run -e uno && pio run -e leonardo && pio test -e native && cd ../firestarter_app && pytest -q` |
| **Estimated runtime** | Quick ~2 s; Full ~8 s. |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter && pio run -e leonardo` (~1 s) AND `cd firestarter_app && pytest tests/test_fwguard.py tests/test_decoder.py -q` (<1 s).
- **After every plan wave:** Run `cd firestarter && pio run -e uno && pio run -e leonardo && pio test -e native -f '*test_dispatch*' -f '*test_messages*'` (~7 s).
- **Before `/gsd-verify-work`:** Full suite must be green AND `09-MEASUREMENT.md` published with both deltas AND bench-verification matrix re-run on Uno + Leonardo AND Phase 8 SC#2/SC#3 chip-seated UAT closed.
- **Max feedback latency:** ~8 seconds (full suite).

---

## Per-Task Verification Map

| Task slot | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|-----------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 9-01-* | 01 (D-04 dev_tools conversion) | 1 | LFW-03 | — | `dev_tools.cpp` emits `OK: Ready` (id-frame 0x01) at both `dt_set_registers` and `dt_set_address` blocking points | unit + build | `cd firestarter && pio test -e native -f '*test_dispatch*' && pio run -e leonardo` | ✅ | ⬜ pending |
| 9-02-* | 02 (D-01 inline + D-02 deletion + D-06 version bump) | 2 | LFW-03, LFW-04 | — | Legacy log macros, `rurp_log`, `rurp_log_P`, `_firestarter_log_*` helpers, `LOG_OK_MSG`, `debug_setup`/`log_debug`, `logging.h`, `logging.c` all gone; FW version handshake = `3.0.0-dev` byte-identical | grep + build | `bash -c "grep -rn 'send_ack\\|rurp_log\\b\\|rurp_log_P\\|_firestarter_log_\\|LOG_OK_MSG\\|log_info_const\\|log_error_format\\|log_warn\\b\\|debug_setup\\|log_debug\\b' firestarter/src firestarter/include firestarter/lib \| wc -l"` (expect: 0) AND `cd firestarter && pio run -e uno && pio run -e leonardo` | ✅ | ⬜ pending |
| 9-03-* | 03 (host comment update for `FIRESTARTER_DEV_ALLOW_PRE_V12`) | 2 | LFW-05 carry-over | — | Comment block at `serial_comm.py:752-755` drops "until then" framing | source assertion | `bash -c "grep -n 'until then' firestarter_app/firestarter/serial_comm.py \| wc -l"` (expect: 0) | ✅ | ⬜ pending |
| 9-04-* | 04 (`host_stubs_common.inc` trim — D-03) | 3 | LFW-03 | — | Lines 45-67 (8 `LOG_*_MSG` PROGMEM externs + `rurp_log`/`rurp_log_P` no-op stubs) removed; native test build still links | unit | `cd firestarter && pio test -e native -f '*test_dispatch*'` (expect: 22+ PASS) | ✅ | ⬜ pending |
| 9-05-* | 05 (`09-MEASUREMENT.md` + Phase 9 bench) | 4 | LMIG-04, SC#1, SC#3 | — | `09-MEASUREMENT.md` published with Phase 8→9 incremental row + v1.1→v1.2 close row; Leonardo Flash `<` 90%; PROGMEM exemption list enumerated; bench wire matrix re-run on both boards | artifact + build + bench | `test -f .planning/phases/09-*/09-MEASUREMENT.md` AND `cd firestarter && pio run -e leonardo -t clean && pio run -e leonardo \| grep '^Flash:'` (parse < 90.0%) AND operator bench transcript appended | ✅ | ⬜ pending |
| 9-06-* | 05 (Phase 8 SC#2/SC#3 carry-over) | 4 | Phase 8 closure | — | Chip-seated W27C512 end-to-end write succeeds; byte-identical readback on Uno + Leonardo | hardware integration | `firestarter -p /dev/ttyACM0 write -e W27C512 <hex> && firestarter -p /dev/ttyACM0 read -e W27C512 -o out.bin && diff baseline.bin out.bin` (zero diff on both boards) | bench | ⬜ pending |
| SC#3 regression | 02 (rides on existing tests; no edits) | 2 | LFW-04 (host guard) | — | Pre-v1.2 firmware refused with `FirmwareOutdatedError` + "v3.0.0 or later" wording; env-var escape hatch works | unit | `cd firestarter_app && pytest tests/test_fwguard.py -v` (expect: 4 PASS) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**None — existing test infrastructure covers all Phase 9 requirements** (per 09-RESEARCH.md §"Validation Architecture" lines 701-709).

- `test_fwguard.py` already has the 4 SC#3 regression cases on the locked wording. No file edits needed.
- The `pio run` build-output parsing for Flash % is a standard PlatformIO behavior (no new framework needed).
- The grep gates for LFW-03 / LFW-04 are one-liners runnable in any shell.
- The bench-verification recipe is documented in `08-MEASUREMENT.md` §"Bench Verification — Chipless Wire-Protocol Validation" (lines 322-384) and re-used unchanged.

*No new test file creation, no fixture refactor, no framework install required.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Bench wire-protocol re-run post-3.0.0-bump on both boards | LFW-05 + W-04 carry-over | Requires physical Uno + Leonardo on operator's bench connected via USB | Re-run 08-MEASUREMENT.md §"Bench Verification" matrix; confirm `OK: FW: 3.0.0-dev:uno, ...` byte-identical parse on host `firestarter fw` (drop `FIRESTARTER_DEV_ALLOW_PRE_V12=1` to exercise native-pass) |
| Phase 8 SC#2 — W27C512 end-to-end write on Uno + Leonardo | Phase 8 carry-over | Requires chip seated in shield socket; per `[[project_leonardo-shield-socket-wonky]]` Leonardo socket is wonky — suspect contact first if readback corrupts | `firestarter -p /dev/ttyACM0 write -e W27C512 <hex>` on Uno, then re-flash same chip on Leonardo |
| Phase 8 SC#3 — byte-identical W27C512 readback | Phase 8 carry-over | Same as above | `firestarter read -e W27C512 -o out.bin && diff baseline.bin out.bin` (zero diff on both boards) |
| Phase 9 PROGMEM exemption audit (SC#1) | LFW-04 | Output requires human review to confirm remaining hits are genuinely non-log (MAGIC_PREAMBLE, CRC8_TABLE, json_parser keys, F() literals only) | `grep -rn 'PROGMEM' firestarter/src firestarter/include \| tee 09-MEASUREMENT.md§exemption-list` then operator reviews + signs off |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — Wave 0 is empty; existing infra covers all gates.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify — every task ties to a buildable + greppable gate.
- [x] Wave 0 covers all MISSING references — N/A (none missing).
- [x] No watch-mode flags — all commands single-shot.
- [x] Feedback latency < 10 s — full suite ~8 s.
- [ ] `nyquist_compliant: true` set in frontmatter — flip to `true` once plan-checker passes.

**Approval:** pending (set to `approved 2026-05-19` after planning completes and plan-checker passes).
