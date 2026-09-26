# Phase 179 Plan 04 — Bench Wave: UV Slot Write, Real Hardware

**Written:** 2026-09-08 (Plan 179-04)
**App build measured:** `firestarter_app` HEAD `9f39853` on branch `gsd/v1.36-dev-test-fidelity` (plan 179-03's last commit; this plan modifies no source)

---

## 1. Pre-flight — the three questions, answered by the operator before anything was plugged in

1. **Part on hand and usable?** Confirmed by the operator: a real ST M27C512 UV EPROM, holding data
   outside the top 256-byte slot (`0xFF00-0xFFFF`), with at least one slot unsaturated.
2. **Shield revision and serial port?** **Shield revision: Rev 2.0 — OPERATOR-STATED.** This is not a
   machine measurement; `hw_revision` cannot distinguish Rev 2.2 from Rev 2.0 from a modified Rev 0
   (Rev 2.2 collides with Rev 0 on the 10 kOhm A3 ADC reading), so there is no machine check that could
   confirm or contradict the operator's statement, and it is recorded here verbatim as what the
   operator said, nothing more. (The run's own `hw_revision` telemetry happened to read
   `"Rev 2.0-class, Override HW: Rev 2.0-class"` — see §3 — which is a pre-existing EEPROM-persisted
   override value from a prior bench session, not an independent confirmation of the operator's
   statement; it is reported honestly below and not treated as corroboration.) **Serial port:
   `/dev/ttyACM0`**, confirmed by USB descriptor (`/dev/serial/by-id/usb-Arduino_LLC_Arduino_Leonardo-if00
   -> ../../ttyACM0`) and independently by the firmware's own `controller:` report (§2).
3. **Slot budget acceptable?** Accepted by the operator: at most ONE confirmation run plus one spare,
   no retries. The first run (below) produced `PASS`, so the spare was never spent.

**Controller identity note:** the operator connected a Leonardo for this session, not the board
previously attached for other phase-179 bench work. This is recorded as a session fact, not a
discrepancy — the port-identity check in §2 confirms it before anything else runs.

---

## 2. Port identity, verified by command before driving any port

```
$ firestarter -p /dev/ttyACM0 fw
Beta app detected — defaulting to --pre. Use --firmware-version X.Y.Z to pin a stable version.
Reading current firmware version...
Connecting...Connecting... OK
Current firmware version: 3.0.0b22, for controller: leonardo on port /dev/ttyACM0
New firmware 3.0.0b25 available for leonardo (current: 3.0.0b22). Update now?
[y/n] (n): Firmware update cancelled by user.
```

`controller: leonardo` matches the USB descriptor's `Arduino_LLC_Arduino_Leonardo` identity — no
contradiction, so the run proceeded. The offered `3.0.0b25` update was **declined**;
`firestarter fw --install` was never run this plan (see §7).

---

## 3. Pre-run evidence — the part was NOT blank outside the target slot

```
$ firestarter -p /dev/ttyACM0 read m27c512 <output-file>
Connecting...Connecting... OK
Reading EPROM M27C512, saving to <output-file>
Read complete (7.41s). Data saved to <output-file>
```

Measured from the 65536-byte read-back (`m27c512-preread.bin`):

| Figure | Value |
|---|---|
| Total size | `0x10000` (65536 bytes) |
| Top slot (`0xFF00–0xFFFF`) all `0xFF`? | **True** — blank, unsaturated, available as the write target |
| Bytes outside the top slot that are non-`0xFF` | **16**, at offsets `0x0000–0x000F` |
| First non-`0xFF` byte outside the top slot | offset `0x0000` |
| First 16 bytes (hex) | `44 20 82 3c fd e6 f1 c2 6b 30 f9 0e c7 dd 01 e4` |

This is the exact shape the plan's `read_first` note names — Phase 83's bench PASS was a 16-byte
write at `0x0000`, and that is precisely the non-blank content found here, outside the top slot.
**Precondition confirmed: the part holds data outside the target slot, and the target slot itself was
blank going in.**

---

## 4. The command, run exactly once, two cycles

```
Command: firestarter -p /dev/ttyACM0 dev test m27c512
```

No `--fast` flag was used (confirmed: `firestarter dev test --help` shows `--fast` runs one
write/verify cycle instead of two; it was never passed). The GitHub filing prompt printed a
pre-formed issue URL rather than submitting anything — no network request was made, no issue was
filed.

```
$ echo "exit=$?"
exit=0
```

---

## 5. Full step table, as measured (from the run's own JSON report and terminal table)

| Step | Verdict | Run count | Duration | Reason | Error code |
|---|---|---|---|---|---|
| id | OK | 1 | 3.53s | - | - |
| read | OK | 2 | 21.3s | - | - |
| blank-check | **SKIPPED** | 1 | - | `Not blank, at 0x000000, v: 0x44` | **176** (0xB0) |
| write-partial | OK | **2** | 47.0s | - | - |
| verify | OK | **2** | 7.04s | - | - |
| erase | NA (SKIP) | 0 | - | - | - |
| write-baseline-b | NA (SKIP) | 0 | - | - | - |
| write-baseline-a | NA (SKIP) | 0 | - | - | - |
| sdp-lock | NA (SKIP) | 0 | - | - | - |
| write-inhibited | NA (SKIP) | 0 | - | - | - |
| sdp-unlock | NA (SKIP) | 0 | - | - | - |
| write-restored | NA (SKIP) | 0 | - | - | - |

The `write-partial` step is this run's write step and the `verify` step is this run's verify step —
both show `run_count == 2`, matching UV-02's whole claim. The `blank-check` step's not-blank finding
(`reason`, `error_code=176`) survives verbatim alongside the `SKIPPED` verdict, exactly as UV-02
requires: the finding is preserved, not suppressed.

**Write coverage** (from the `write-partial` step and the terminal summary table, verbatim):
`slot 0xFF00 (256 bytes), 512 bits cleared this cycle; 256 of 256 slots left on this part`
(this is the CLI's own text — recorded exactly as printed, including its "256 of 256" phrasing;
`slots_remaining` per the acceptance gate's terminology is that same figure).

Additional measured fields from the run's JSON report:
- `write_region_start`: 65280 (`0xFF00`)
- `write_region_length`: 256
- `write_bits_cleared`: 512
- `write_bits_retained`: 1024
- `write_current_source`: `"probe read (tranche 2/2)"`
- `dedup_fingerprint`: `dea6e2474d30`
- `is_submittable`: `true`
- `run_status`: `COMPLETE`
- `db_diff.ladder_state`: `community-reported`
- `db_diff.proposed_disposition`: `suggests: candidate for community-reported (advisory)`

**Telemetry captured with the run** (for the record, not part of the pass/fail gate):
`host_version=3.0.0b36`, `fw_board_identity=3.0.0b22:leonardo`,
`hw_revision="Rev 2.0-class, Override HW: Rev 2.0-class"` (machine-reported, see §1 caveat),
`protocol=0x07`, `chip_id=0x203D` (chip-ID check passed), `vpp before/after=12400/12400 mV`,
`vpe before/after=14300/14300 mV`, `banner="4 of 5 ran"`, `sdp_hold_state=NOT-RUN`.

---

## 6. The title line

```
[dev test] m27c512 — PASS (dea6e2474d30)
```

Decoded verbatim from the run's own GitHub-issue-title URL parameter. 12 hex characters, matches the
`dedup_fingerprint` field exactly.

---

## 7. Slot budget spent

- Slots spent this run: **1** (the write to `0xFF00`, the top 256-byte slot, which was blank going
  in per §3 and is now written).
- Slots remaining in the accepted budget: **1** (the spare) — not spent, because the first run
  produced `PASS`. No retry occurred.
- Slots remaining on the physical part: per the CLI's own text, `256 of 256 slots left on this part`
  (recorded verbatim; the part's own slot-accounting phrasing, not the plan's 2-slot session budget).

**No firmware was flashed or modified:**

```
$ git -C /workspaces/firestarter status --porcelain
(clean — no output)
```

`firestarter fw --install` was never run this plan. The only firmware interaction was the read-only
`fw` version check in §2, which declined the offered update.

---

## Disposition

BENCH RESULT: PASS

A real ST M27C512 UV EPROM, seated by the operator, holding data outside its top 256-byte slot,
accepted a slot write at `0xFF00` without being refused (`write-partial` verdict `OK`, `run_count ==
2`; `verify` verdict `OK`, `run_count == 2`). The standalone blank-check found the part genuinely
not-blank (`reason="Not blank, at 0x000000, v: 0x44"`, `error_code=176`) and was adjudicated
`SKIPPED` rather than `BAD`, clearing the run to `overall_verdict == PASS`
(title `[dev test] m27c512 — PASS (dea6e2474d30)`), exit code `0`. One slot was spent of the accepted
two-slot budget; no retry was needed. Port identity, shield revision (operator-stated), the exact
command, the pre-run non-blank evidence, and the full step table are all recorded above from the
actual run — nothing in this document was transcribed from the plan rather than measured.
