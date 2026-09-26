# Phase 8, Plan 08 — Phase Close (SC#1/#4 auto + chipless wire-protocol verification)

**Status:** complete (with caveat — SC#2/SC#3 deferred to operator hardware run)
**Date:** 2026-05-18
**Plan:** 08-08-PLAN.md (autonomous=false, type: checkpoint:human-verify)
**Phase:** 08 — Convert State-Machine Prefix Call-Sites (OK/INIT/MAIN/END)

---

## What was built

### Task 1 — Automated measurement (committed `2260678`)

`08-MEASUREMENT.md` (332+ lines) covering:

- **SC#1 PASS** — `EXPECTED_PREFIXES = ["OK","INFO","DEBUG","ERROR","WARN","DATA"]` in `serial_comm.py`; `STATE_MACHINE_PREFIXES = []`; zero active INIT/MAIN/END prefix-matcher entries. Bootstrap `OK: FW: ...` text path preserved per LFW-05.
- **SC#4 PASS** — Both boards build clean, Flash strictly below Phase 7 close baseline:
  - Leonardo: 24,538 B / 85.6% (−2,488 B, −8.7 pp vs Phase 7 close 27,026 B)
  - Uno: 22,330 B / 69.2% (−2,508 B, −7.8 pp vs Phase 7 close 24,838 B)
- **R-01 SRAM win** — −96 bytes on both boards (Plan 06 `response_msg` deletion); Uno 1,497 B (73.1%), Leonardo 1,467 B (57.3%).
- **SC#3 host-side path** — `MSG_DATA_CHUNK` decode via `Response.payload` wired in `eprom_operations.py`; 29/29 pytest PASS including the two new chunk-roundtrip tests from Plan 05.

### Task 2 (chipless slice) — Bench wire-protocol verification (committed in this plan)

Both boards flashed with Phase 8 firmware (`firestarter HEAD 275522a`). Host at `firestarter_app HEAD 96e8deb` (includes regression fix below). Exercised every Phase 8 wire-protocol change that does NOT require a chip in the socket. Full severity-band coverage matrix in `08-MEASUREMENT.md § Bench Verification`.

Highlights:
- P-04 composite handshake (`MSG_OK_FW_HANDSHAKE` u8+u8+ascii_str) ✓ both boards
- P-02 fixed-shape (`MSG_OK_REV` u8+u8) ✓ both 0xFF-sentinel (Uno) AND non-sentinel (Leonardo) branches
- P-03 fixed-shape (`MSG_OK_CFG` u32+u32+u8) ✓ both sentinel branches
- W-03 DATA-class voltage frames (`MSG_DATA_VPP_VOLTAGE` / `MSG_DATA_VPE_VOLTAGE` u16+u16) ✓ both boards
- MSG_INIT_DONE ID frame ✓ Uno (Leonardo VPP-uncalibrated → preempted by ERROR)
- ERROR frame with parameterized voltage (`MSG_ERROR_VPP_HIGH` carrying live voltage) ✓ Leonardo
- W-04 u16 `len` field — implicitly proven by every frame above

### Plan 05 host regression fix (committed `96e8deb` in firestarter_app)

Bench testing surfaced a Plan 05 follow-up bug:
- Plan 05 widened `Response` from 2 to 3 fields (added `payload` for `MSG_DATA_CHUNK`).
- `firestarter_app/firestarter/hardware.py:204` still did `response_type, message = comm.get_response()` — crashed every `vpp` / `vpe` invocation.
- Fix: read the `Response` namedtuple, access `.type` / `.message`.
- After fix: VPP + VPE continuous-read loops produce DATA frames at expected ~500 ms cadence on both boards.

---

## What's NOT verified (deferred to operator hardware run)

- **SC#2** — `firestarter write -e W27C512 -i <bin>` end-to-end with INIT/MAIN/END acks rendered from ID-frame decoding alone.
- **SC#3** — `firestarter read -e W27C512 -o <out>` byte-identical to Phase 7 baseline.
- **MSG_MAIN_DONE / MSG_END_DONE** as ID frames — would be exercised by a successful write/read flow.
- **MSG_DATA_CHUNK** chip-byte streaming — same; requires a successful read flow.

These three require a chip in the socket plus a known-good baseline. The protocol path is already validated by tests (`test_decoder.py` decoder round-trips include the >253 B chunk path from Plan 02). What remains is the chip-physics integration end-to-end, which Phase 8 did NOT modify.

To close SC#2 + SC#3:

```bash
cd firestarter_app
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 write -e W27C512 -i <known.bin>
FIRESTARTER_DEV_ALLOW_PRE_V12=1 firestarter -p /dev/ttyACM0 read -e W27C512 -o /tmp/p8-uno.bin
diff /tmp/p8-uno.bin <Phase 7 baseline file>   # expect exit 0
# repeat with -p /dev/ttyACM1 for Leonardo
```

When that's done, append the result under `08-MEASUREMENT.md § Bench Verification` and re-commit `docs(phase-08): mark SC#2 + SC#3 PASS on Uno + Leonardo`.

---

## Commits in this plan

- `firestarter_app/96e8deb` — `fix(hardware): unpack Response object, not 2-tuple, in _read_voltage_loop` (Plan 05 follow-up)
- meta `2260678` — `docs(phase-08): add 08-MEASUREMENT.md with SC#1/#4 auto + R-01 SRAM verification`
- meta (this commit) — `docs(08-08): complete plan 08 with chipless bench verification` (incl. SUMMARY.md and updated 08-MEASUREMENT.md)

---

## Self-Check

- [x] 08-MEASUREMENT.md exists, ≥ 50 lines (currently 332+, augmented to ~440 with bench section)
- [x] SC#1 grep evidence in 08-MEASUREMENT.md
- [x] SC#4 dual-board build numbers in 08-MEASUREMENT.md
- [x] R-01 SRAM delta in 08-MEASUREMENT.md
- [x] Firmware flashed to both physical boards from Phase 8 HEAD
- [x] Wire-protocol verification matrix recorded
- [x] Plan 05 host regression fix committed in firestarter_app sub-repo
- [ ] SC#2 (write end-to-end on real hardware) — DEFERRED, awaits chip-seated bench session
- [ ] SC#3 (byte-identical readback) — DEFERRED, awaits chip-seated bench session

Phase 8's wire-protocol redesign is verified to work on real hardware. The SC#2/SC#3 closure is gated on bench access to a W27C512 (or equivalent) chip; the protocol layer that Phase 8 modified is independently validated above.
