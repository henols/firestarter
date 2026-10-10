# Product Roadmap

Current version: stable `3.1.0` in both sub-repos (2026-09-26, the first stable 3.x release).
The beta channel continues at `3.1.0b5` (2026-09-27). The operator alone decides when a stable
release happens. `RELEASING.md` in the meta repo is the runbook for it.

## Implemented

**Chip database**
- 746 chips from 59 vendors on 16 pin maps: 736 `supported`, 9 `adapter-required`, 1
  `protocol-not-implemented`. Built by `build_db.py` from minipro `infoic.xml`, with
  `datasheet_overrides.json` (each entry cites a datasheet) and `extra_chips.json` (parts that
  minipro does not have, for example the 2516/2532).
- A regression diff against a committed baseline, and a VPP-safety dispatch gate over every row.
- User overrides in `~/.firestarter/database.json`.

**Protocols in firmware** (`firestarter_fw/PROTOCOLS.md`)
- `0x05` 5 V page-write flash. It preserves the unchanged bytes of a page on a partial write.
- `0x06` AMD/SST unlock-sequence NOR flash.
- `0x07` / `0x08` / `0x0B` UV/EE-EPROM (28, 32 and 24-pin). They share one per-byte
  pulse-to-verify loop with a per-protocol parameter table. The pulse width comes from the database.
  `write --pulse-us` overrides it.
- `0x0D` parallel EEPROM, with SDP auto-unlock (opt-out: `--skip-sdp-unlock`), DQ7 page polling and
  software chip erase.
- `0x10` Intel 28F flash, with a VPP check before the pulse.
- `0x0E` / `0x27` / `0x28` / `0x29` SRAM, FRAM and NVRAM.
- Every other protocol value fails closed (`MSG_ERR_PROTOCOL_NOT_IMPLEMENTED`).

**Host CLI**
- `list`, `search`, `info` (pin layout, jumper settings, adapter view), `read`, `write`, `verify`,
  `blank`, `erase`, `id`, `vpp`, `vpe`, `hw`, `config`, `fw` (install firmware from GitHub releases,
  `--pre` for beta).
- The host does verify and blank check. The host reads the chip and compares it with one streaming
  engine (`compare.py`). `--full` reports all mismatch ranges. The host write guard replaced the
  firmware pre-flight blank checks.
- Safety gates: a JP5 warning for 8 Mbit parts, and a flash4 erase refusal.
- `dev test <chip>`: a community capability sweep with a diagnostic report that names the firmware.
  `--submit` sends it as a GitHub issue after PII removal. On UV parts that are not blank, it uses
  bit-masked (1→0) writes.
- Channel gating: stable builds expose only `dev read` and `dev test`. Beta builds expose all `dev`
  tools (`reg`, `addr`, `consistency-check`, `write-cycle`, `fault-inject`, `lock-status`,
  `validate-family`).

**Transport and boards**
- JSON commands and binary data blocks at 250000 baud, framed with COBS and CRC8, with resync.
- Board targets: Arduino Uno (ATmega328P), Uno with ATmega328PB, and Leonardo (ATmega32U4).
- PY32F071 (Cortex-M0+) builds in CI and publishes a `.hex`, and the host can install it over USB
  DFU. **No PY32F071 PCB exists.** Nothing has run on this silicon, and the firmware refuses every
  command that energises a PROM on this target.

**Release and docs**
- Beta channel: a push to `beta` publishes a PyPI pre-release and a GitHub pre-release with a `.hex`
  for each board. A push to `main` publishes a stable release when the version in the source has
  no tag yet. The promotion PR carries the version. See `RELEASING.md`.
- User documentation is on the `firestarter` GitHub wiki. The only change log is `CHANGELOG.md` in
  the meta repo.
  Validated chips are in `VALIDATED-EPROMS.md`; all 11 rows are 3.0.0bNN evidence and none has been
  re-run on the 3.1.x line.

## In Progress — Jumper display correctness and the 2716 class

1. Bench probes (unpowered) of JP4 on the Rev 2.0 and Rev 2.2 shields, and VPE at socket pin 25.
2. **Done (2026-09-25, spec `agent-os/specs/2026-09-25-1503-info-jumper-table/`).** `info` jumper
   settings from an explicit table for each pin map (`firestarter/jumper_table.py`), keyed on the
   socket pin where VPP lands. This replaces the pin-count heuristic. A test that reads
   `pinouts.json` fails when a pin map has no entry. The output has three revision blocks: Rev 0/1,
   Rev 2.0/2.1 and Rev 2.2/2.3. It also corrects the wrong JP3/JP4 output for `DIP28_27512`,
   `DIP32_27C801`, `DIP32_STD` and `DIP32_27C020`. **Still open:** the Rev 2.0/2.1 JP4 cells of 7
   pin maps come from the schematic. They are marked "not measured" until the PROBE-01 bench probe
   (item 1).
3. **Done (2026-09-25, same spec).** `info` stops showing a WP-pin voltage as VPP on 5 V-only parts.
   "Can be erased" agrees with `erase`. The 0x0B description and the firmware JP4 docs state the
   measured routing.
4. Database safety: `TI/TMS2716` (three supplies) leaves `supported`. `DIP24_2532` fails closed. The
   2516/2532/2716 datasheets go into the repo. The `DIP24_2716` pulse width comes from the datasheet.
5. Firmware `0x0B` fix for 24-pin parts with VPP on pin 21. PGM is active high, and VPP = VCC during
   read. Today the polarity is inverted for all `DIP24_2716` rows. Native trace tests must prove the
   fix before any write to a real part. The host refuses the write on older firmware. **Not in
   `3.1.0b2`** — that release carried the jumper-display work only, so this lands in `3.1.0b3` or
   later.
6. TMS2516 bench on Rev 2.2: N≥3 stable reads, then a bit-masked write. The measured VPP is recorded
   against the 24 V minimum.
7. Per-revision jumper tables and shield photographs on the wiki.

## Planned / Deferred

**Programming and safety**
- A TMS2532 firmware mode (A11 on the CE line, active-low PGM on OE). No bench part is available.
- A gate for the mirrored JP4 hazard: a 28/32-pin part reads the signal at socket pin 25.
- `write --sdp-relock`: deliberate SDP protection, verify-gated. It was deferred two times. Today no
  supported way exists to protect an SDP part.
- AT28C256 write-path failure (gh#21), only partly addressed.
- W27C512 writes 3.7× slower than on v2.x (gh#36).
- A firmware upper bound on `--pulse-us` for `0x07`/`0x08` (their energy cap is 0, which means no
  cap).
- Software chip erase for `0x05`. Erase refusal for families other than flash4.
- `MSG_ERR_EMPTY_INPUT` (0xA4) has more than one meaning. Frame-integrity failures need their own
  ID.

**Hardware-gated validation**
- Chips not yet proven on silicon: AM27C020 (`0x08`), `0x0B` NMOS parts at 25 V (best-effort only),
  X88C64 (PCB-blocked), AT28C04/16 (needs an adapter).
- uno328pb + Rev 2.0 brownout hang during program.
- Bench sweeps on the Rev 2.2 and modified Rev 0 shields. All systematic sweeps to date used Rev 2.0.
- **RESOLVED 2026-09-26 (v1.43).** The VPP reading error is per-die ATmega bandgap spread, not
  the divider. Measured on three boards across three shield revisions: the rails-off ADC count
  measures the divider ratio with no meter and no bandgap involved, and came out 137/138/136 —
  nominal, confirming `VALUE_R2 = 44000`. The bandgap counts were 206/228/210, giving real
  references of 1024/1100/1050 mV against a firmware that assumed 1100 for every board. That alone
  reproduces backlog 999.38's 6.8–8.3 % band: it was a sample of different chips, never a
  systematic offset. **No firmware-only fix was possible** — AVR carries no factory trim word.
  Fixed by per-board calibration: `firestarter cal --vcc <meter reading of the 5 V pin>`. The
  leonardo's VPP reading moved 12994 → 12036 mV on an unchanged rail, so a correctly set 12.0 V rail
  no longer trips `MSG_ERR_VPP_HIGH`. Specs
  `agent-os/specs/2026-09-26-1826-voltage-reading-accuracy/` and
  `agent-os/specs/2026-09-26-2108-per-board-bandgap-calibration/`.
- **Now unblocked:** the `MSG_WARN_VPP_LOW` window is still narrower than the error it was meant to
  catch, but the reading is trustworthy at last, so the −5 %/+500 mV window can finally be judged on
  its merits rather than against instrument error. v1.40 RAIL-03 can close with it.

**Database quality**
- 215 algorithm 7/8 rows have `pulse_duration_us: 100` with no datasheet evidence.
- `FUJITSU/MBM27C1000` has the pin map of a sibling part.
- The 13 non-TI `DIP24_2716` rows have VPP values that do not agree with the datasheets.
- The 255 `DIP32_SST39SF040` rows with A18 on socket pin 1 are deliberately not gated.

**Platform and tooling**
- The `info` view prints through `logger.info`. The `host/echo-vs-logger` standard wants
  `click.echo` for operator facts. Move the whole view in one change, not line by line.
- After PROBE-01, correct the `probe_pending` cells in `firestarter/jumper_table.py` and remove
  their "not measured" note.
- PY32F071: a PCB, a closed-loop VPP DAC with a calibration model, and a bus-trace oracle for ARM.
- A binary command protocol in place of the jsmn JSON layer. It measured −3.7 KB flash on Leonardo.
- `dev test` session reuse. It measured 50–80 s saved per run.
- An OLED status display on the RURP connector (gh#37).
- Python 3.11 reaches EOL on 2027-10-31. The version guard does not run from the console script.
- Wiki content that is not written yet: a compatibility matrix and pages for each family.
- Reverse firmware-pairing check: a CLI newer than the firmware on the board. The forward direction
  is gated by `firestarter/fw_release_gate.py`; this direction is not.
