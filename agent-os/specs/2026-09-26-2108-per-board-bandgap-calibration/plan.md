# Spec: Per-board bandgap calibration

Follow-up to `2026-09-26-1826-voltage-reading-accuracy`, whose bench record
selected this arm by measurement.

## Context

The VPP/VPE reading error is **per-die ATmega bandgap spread**, measured on
three boards across three shield revisions:

| Board | bandgap adc | VCC (meter) | Vbg_true | VPP error |
|---|---|---|---|---|
| leonardo | 206 | 5090 mV | 1024.0 mV | +7.43 % |
| uno | 228 | 4940 mV | 1099.9 mV | +0.01 % |
| uno328pb | 210 | 5120 mV | 1050.0 mV | +4.76 % |

The divider is nominal (`VALUE_R2 = 44000` confirmed). No firmware-only change
can fix a per-die quantity: AVR carries no factory trim word. The fix is one
external measurement per board, stored.

Today a correctly-set 12.0 V rail reads 12.9 V on the leonardo and trips
`MSG_ERR_VPP_HIGH` at 12.5 V — **that board cannot write.** This spec is what
unblocks it.

Prior art: `.planning/seeds/voltage-reading-whitebox-calibration.md` (Stage 1)
and `.planning/notes/voltage-cal-design-decisions.md` (D1–D7). D1's "let the
procedure discover the error model" is retired — the model is measured.

## Decisions

- **C-A. White-box, per the seed's D2.** Store the measured bandgap in
  millivolts, a physically real per-chip constant. Do not fold the correction
  into `r2`: that leaves the reported VCC wrong and makes the stored numbers
  meaningless.
- **C-B. The firmware does the arithmetic.** The host sends the operator's
  measured supply in millivolts; the firmware reads its own bandgap count and
  back-solves `bandgap_mv = vcc_meter * bandgap_adc / 1024`. The host never
  needs the raw count, so calibration works on a **stable** image and needs no
  dev-gated command.
- **C-C. Reuse `CMD_CONFIG`.** One new JSON key, no new command ordinal. The
  calibration knobs already live there (`r1`, `r2`, `rev`).
- **C-D. Stage 2 (divider trim) is NOT built.** Measured at about 1 % — below
  this instrument's one-count resolution of 0.7 %.
- **C-E. Migrate, do not wipe.** `CONFIG_VERSION` goes to `VER07`. The existing
  `rurp_validate_config` resets r1/r2 **and `hardware_revision`** on any version
  mismatch, which would silently destroy the operator's Rev 2.2 override. The
  migration instead range-checks each field and keeps plausible values. That
  also closes the pending stranding todo by its own option 2
  (`config-version-not-bumped-strands-stale-eeprom-calibration.md`): a stale
  `r1 = 1000` is out of band and gets corrected, where the version gate alone
  could never reach it.
- **C-F. Bands, and why these.** `r1` 202500–337500 and `r2` 33000–55000 are
  ±25 % of the defaults, reusing the tolerance the host already applies in
  `_R1_LO`/`_R1_HI`. `bandgap_mv` 1000–1200 mV is the ATmega datasheet window —
  a value outside it is not a calibration, it is a typo or a bad meter reading,
  and is **refused, not clamped**.
- **C-G. Safety, per the seed's D7.** A bad calibration makes the firmware
  *trust* a wrong voltage. So: plausibility bounds refuse rather than clamp;
  the host shows old → new before writing; and `--reset` restores the nominal.

## Tasks

1. **Firmware storage.** Append `uint16_t bandgap_mv` to
   `rurp_configuration_t`. `CONFIG_VERSION` → `VER07`. Rewrite
   `rurp_validate_config` as a per-field range migration (C-E, C-F).
   ARM is safe: `StoredConfiguration` embeds the struct with `sizeof`/`offsetof`
   and carries length + CRC32, so an old record fails validation and falls back
   to defaults by design. AVR re-reads `EEPROM.get` at the same offset and the
   `version` string still discriminates.
2. **Firmware math.** `rurp_scale_voltage_mv` and `rurp_scale_vcc_mv` take the
   calibrated bandgap instead of the literal `RURP_BANDGAP_NOMINAL_MV`. Extend
   the native suite for the new parameter, including the identity case (1100 in
   → today's numbers out) and the three measured boards.
3. **Wire.** `json_parse_config` accepts `vcc` (measured millivolts) and
   back-solves. `MSG_OK_CFG` widens 9 → 11 bytes with `bandgap_mv`.
   Catalog edit in the meta repo only.
4. **Host.** `firestarter cal` — bare shows the current calibration and what it
   implies; `--vcc <volts>` calibrates; `--reset` restores nominal. Confirm
   old → new before writing.
5. **Verify on silicon.** Calibrate all three boards, then `vpp` against a
   meter on each. The leonardo must stop tripping `MSG_ERR_VPP_HIGH` at a
   correctly-set 12.0 V rail.

## Verification

- `pio test -e native` and `-e native_nodevtools` both green, with the new
  bandgap parameter covered and a planted out-of-band value proven refused.
- A migration test: a VER06 record with a stale `r1 = 1000` is corrected, and
  one with a good `r1` and a set `hardware_revision` keeps both.
- Flash and RAM for leonardo (stable and `DEV_TOOLS=1`), uno, uno328pb.
- `pytest` + ruff + mypy on the host; codegen re-run and byte-clean.
- On hardware: `firestarter cal --vcc <meter>` on each board, then `vpp`
  agreeing with a meter to about 1 %, and a 12.0 V rail that no longer refuses
  to write.
