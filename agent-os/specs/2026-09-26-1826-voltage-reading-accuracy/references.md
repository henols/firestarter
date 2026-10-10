# References for Voltage-Reading Accuracy

> **`.planning/` paths below refer to the retired GSD tree.** Read them at the tag
> `archive/planning-tree-final` — see [PLANNING-ARCHIVE.md](../../PLANNING-ARCHIVE.md).

## The code under change

### AVR conversion path — the whole of it

- **Location:** `firestarter_fw/src/boards/rurp_common.cpp`
- **Relevance:** every AVR voltage number the project has ever reported comes from these 96 lines.
- **Key patterns:**
  - `rurp_get_bandgap_adc_reading()` (:21-40) writes `ADMUX` directly. `_BV(REFS0)` = AVcc as
    reference; the MUX bits select the internal 1.1 V bandgap (channel 14 on 328P/PB, channel 30 on
    32U4). It measures the bandgap *through* VCC — it does not switch to the internal reference.
    `delay(2)` then one conversion. **Leaves ADMUX on the bandgap channel.**
  - `rurp_read_vcc_mv()` (:42-50) — `1126400 / result`, where `1126400 = 1100 × 1024`.
  - `rurp_read_voltage_mv()` (:52-96) — `analogReference(DEFAULT)`, one `analogRead(A2)`, then a
    bandgap read. Folded as `k = 1100×(R1+R2)/R2`, `Vin = (adc×k + bg/2)/bg`; `k = 7850` at shipped
    defaults. uint32 guards at `sum > 3900000` and `k > 4194303`, both `return 0`.
  - **Ordering hazard:** A2 is read *first*, immediately after the mux sat on the bandgap channel,
    with no settling delay — the `delay(2)` exists only on the bandgap side. Worse on the
    `hw_read_voltage` path, where `rurp_read_vcc_mv()` runs first.
  - **No averaging anywhere** on either read. Contrast `analog_read_avg8` in
    `include/rurp_hw_rev_utils.h:52-58`, which does 8 samples for revision detect.

### Constants and config

- `firestarter_fw/include/rurp_shield.h:44-48` — `CONFIG_VERSION "VER06"`, `VALUE_R1 270000`,
  `VALUE_R2 44000`.
- `firestarter_fw/include/rurp_types.h:61-66` — `rurp_configuration_t { version[6], r1, r2,
  hardware_revision }`. A new field forces a `CONFIG_VERSION` bump.
- `firestarter_fw/src/rurp_config_utils.cpp:35-43` — `rurp_validate_config` re-applies defaults
  **only** on a version-string mismatch. This is the stranding mechanism.
- `firestarter_fw/src/boards/rurp_config_storage_eeprom.cpp` — `CONFIG_START 48`.
- `firestarter_fw/src/json_parser.c:548-558` — `get_r1` / `get_r2` / `get_rev`. Unknown keys are
  **rejected** here, unlike the main command parser.
- `firestarter_fw/src/boards/leonardo_rurp_shield.cpp:27` — dead duplicate `VCC_CALC_CONSTANT`,
  referenced nowhere.

### Reporting path (why the host cannot see millivolts)

- `firestarter_fw/src/hardware_operations.cpp:15-90` — `hw_read_voltage`. State 0 sets
  `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` for VPP, regulator alone for VPE, then
  `delay(100)`. State 1+ does `delay(500)` per host ACK.
  **Lines 71-76 pre-split and pre-round to whole volts + one tenth before framing.**
- `firestarter_fw/src/proms/memory.cpp:218-235` — `mem_util_report_voltage`, same 4×u16 shape.
- `firestarter_app/firestarter/hardware.py:360-374` — `_parse_voltage_frame` reconstructs
  `v_int*1000 + v_dec*100`. Returns `None` on no match, never a fabricated 0.
- The only full-mV value that ever reaches the host is the debug frame `DBG_CHECKING_VPP_VOLTAGE`
  (0x18) at `eprom.cpp:546` and `flash_intel.cpp:38`.

### The guard window (Task 6)

- `firestarter_fw/src/proms/eprom.cpp:545-555` and `firestarter_fw/src/proms/flash_intel.cpp:37-46`
  — byte-for-byte identical. HIGH at `+500` mV absolute is a hard `MSG_ERR_VPP_HIGH` unless
  `FLAG_FORCE`; LOW at `×95/100` is only `MSG_WARN_VPP_LOW`.
- `firestarter_fw/include/rurp_pinout.h:120` — `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV 17380`.
  **Route selection only; never compared against an ADC reading.** Keep it that way.

### Host surface

- `firestarter_app/firestarter/cli_handlers.py:1451-1528` — `vpp`, `vpe`, `hw`, `config`
  (`-r1/--r16`, `-r2/--r14r15`, `--rev`). `config` with no args is a GET.
- `firestarter_app/firestarter/cli_handlers.py:2336-2340` — `_R1_TARGET = 270_000`,
  `_R1_TOLERANCE = 0.25`. Read only by `dev validate-family`; nothing ever writes the key.
- No host-side scaling, gain or offset exists anywhere. No calibration key in
  `~/.firestarter/config.json`.

## Prior art — read these before planning any task

| Document | What it gives |
|---|---|
| `.planning/seeds/voltage-reading-whitebox-calibration.md` | The dormant two-stage design. Stage 1 back-solves the true bandgap off the fixed 5 V line; Stage 2 trims the divider with the pot. Names the three error sources and their sizes. **This spec supersedes its D1 only** (the error model is now known to be gain-only). |
| `.planning/notes/voltage-cal-design-decisions.md` | D1–D7, the rationale. D2 white-box over black-box; D3 two nodes; D4 one sense node covers VPP and VPE; D5 no live monitor loop; D6 storage and migration; D7 safety is load-bearing. Do not re-litigate these. |
| `.planning/ROADMAP.md:7424-7432` (backlog 999.38) | The three paired readings, the 6.8–8.3 % band, and the **standing operational rule**: never correct the pot against the firmware's own reading. |
| `.planning/milestones/v1.40-phases/199-what-the-rails-can-actually-deliver/199-BENCH-RECORD.md` | The measured-figures convention (fenced block of bare integers, parsed not transcribed), the two paired readings this spec reasons from, and **three bench tooling traps** — `hold_rail.py` reports success against a refused command, `dev reg` exits 0 while printing an error, and `dt_set_registers` was not re-entrant (fixed at fw `7eed3af`, which no published beta through `3.0.0b33` carries). |
| `.planning/milestones/v1.34-artifacts/bench/cells/A3-B2/POT.md` | The failure this spec exists to clear: firmware 12.9–13.0 V against a metered 12.0 V, above the HIGH guard, write not started. Also the worked pot procedure. |
| `.planning/debug/resolved/firmware-vpp-misread.md` | The 6.8× under-read RCA — a board with stale EEPROM `r1=1000` reporting 1.8 V on a true 12.2 V rail. Shows how far a wrong divider constant can go. |
| `.planning/todos/pending/config-version-not-bumped-strands-stale-eeprom-calibration.md` | The stranding defect and its three options. Task 5 takes option 1 (bump), which this spec's re-measurement makes safe. |
| `firestarter_fw/document/rurp_schematics_rev1.pdf` | The boost feedback network and the resistor census. Extract in `visuals/rev1-schematic-extract.md`. |
| `firestarter.wiki/Shield-Revisions.md` | Max VPP 13 V per revision; Rev 0 cannot read VPP back at all; the A3 detection bands. Must be updated in the same change if any band constant moves — nothing checks this automatically. |
| `agent-os/product/roadmap.md` | Carries "VPP ADC reads about +7.5 % high. `MSG_WARN_VPP_LOW`'s window is narrower than this error" as a deferred item. Task 7 updates it. |

## Patterns to reuse, not reinvent

- **8-sample averaging:** `firestarter_fw/include/rurp_hw_rev_utils.h:52-58` `analog_read_avg8` —
  `sum >> 3`, ~104 µs, ~30 B flash. Already in the tree and already paid for.
- **Bench measured-figures block:** the `## Measured figures` fenced-integer convention from
  `199-BENCH-RECORD.md`. Later tasks parse integers from it; nothing re-transcribes from prose.
- **Holding a rail:** `dev reg 0 0 <composite> -f`, then the firmware's own
  `while (!rurp_user_button_pressed()) delay(200);`. Confirm the hold is real by a probe timing out
  against it. Release with the USR button, never `pkill`. **Do not use `hold_rail.py`.**
- **PY32 ADC, as a contrast:** `firestarter_fw/platform/py32f071/src/py32f071_rurp_shield.cpp:106-155`
  already does the right things AVR does not — `HAL_ADCEx_Calibration_Start`, the longest sample
  time, and a 16-sample average on both channels. Its remaining flaw is the nominal 1200 mV VREFINT
  at :278-290. One caveat: any single sample returning 0 aborts the whole average and returns 0.
