# CLAUDE.md — Firestarter Firmware

Arduino C++ firmware for the Firestarter EPROM programmer. Built with PlatformIO.

## Build Commands

```bash
pio run -e uno          # build for Arduino Uno
pio run -e leonardo     # build for Arduino Leonardo
pio run -t upload -e uno   # flash to board
pio test                # run unit tests (all envs)
pio test -e native      # run host-side dispatch tests (no hardware needed)
pio test -e native -f "*test_dispatch*"   # run only the configure_memory dispatch suite
```

## Architecture

### Protocol Dispatch

The firmware dispatches **solely** on `handle->protocol` (populated from the
`algorithm` JSON field). There is no secondary axis: a chip family's electrical
identity is expressed entirely through its `protocol` value, so, for example,
SRAM protocols (`0x0E`, `0x27`, `0x28`, `0x29`) route to `configure_sram` and
never to `configure_eprom` — which matters because `configure_eprom` enables
the 12V VPP boost regulator, a hazard on a 5V SRAM part.

The protocol-prefix chain covers every entry in `KNOWN_PROTOCOLS` (`0x05, 0x06,
0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39`). There is
**no legacy-integer fallback axis** (the pre-v1.20 backward-compat chain was
removed): a command whose `protocol` is unrecognized — including
`protocol == 0` — fail-closes to `configure_not_implemented()` rather than
falling back to any other dispatch axis.

Dispatch reads named `PROTO_<NAME>` constants (`include/proto_constants.h`,
v1.19 naming layer) — every value equals the pre-existing raw-hex dispatch
key it names; numbers stay the dispatch key end to end (GATE-01). Source of
truth for the name set: `firestarter/doc/PROTOCOLS.md` (operator-approved).

Dispatch order in `memory.cpp:configure_memory` (source-of-truth — must match
`firestarter/src/proms/memory.cpp` line-for-line):

1. `protocol == PROTO_FLASH_INTEL (0x10)` → `configure_flash_intel()` — Intel 28F command-register flash
2. `protocol == PROTO_EEPROM_PARALLEL (0x0D)` → `configure_eeprom28c()` — AT28C-series 5V EEPROM with page write
3. `protocol == PROTO_FLASH_NOR_UNLOCK (0x06)` → `configure_flash_nor_unlock()` — AMD unlock flash (sector erase)
4. `protocol ∈ {PROTO_FLASH_5V_PAGE (0x05), PROTO_PHANTOM_0x35, PROTO_PHANTOM_0x39}` → `configure_flash_5v_page()` — page-write flash; 0x05 has DB chips; 0x35 and 0x39 are phantom entries (0 DB chips each — forward-compat dispatch preserved in firmware; host excludes both from KNOWN_PROTOCOLS and routes them to not_implemented)
5. `protocol ∈ {PROTO_EPROM_28PIN (0x07), PROTO_EPROM_32PIN (0x08), PROTO_EPROM_24PIN (0x0B)}` → `configure_eprom()` — UV-EPROM family
6. `protocol ∈ {PROTO_SRAM_32PIN (0x0E), PROTO_SRAM_24PIN (0x27), PROTO_SRAM_28PIN (0x28), PROTO_SRAM_32PIN_NVRAM (0x29)}` → `configure_sram()` — SRAM/NVRAM (BLOCKER-2 mitigation: never reaches VPP regulator)
6a. `protocol ∈ {0x11, 0x2A, 0x2B, 0x2C}` → `configure_not_implemented()` — named infeasibility arms: FWH (0x11) and GAL/PLD (0x2A/0x2B/0x2C); no approved PROTO_ tokens exist for this arm (out of Phase-100 NAME-01 scope) — left as raw hex; infeasible on RURP hardware (DISP-04, Phase 64)
6b. `protocol != 0` → `configure_not_implemented()` — generic fail-closed guard: any non-zero unrecognized protocol (including `PROTO_EEPROM_8051BUS` / 0x34, which has no dedicated dispatch arm) returns MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) with zero hardware side effects; eliminates the 12V VPP hazard for unknown protocols (DISP-01, T-64-01, Phase 64)
7. `protocol == 0` (and any other unrecognized value not caught by 6a/6b) → `configure_not_implemented()` — the single terminal fail-closed exit; returns MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB) with zero hardware side effects (v1.20: removed the legacy-integer fallback chain this arm used to fall through to)

**Fail-closed invariant (Phase 64, extended v1.20):** Steps 6a, 6b, and 7 ensure
every protocol value — named-infeasible, truly-unknown, or zero — reaches
`configure_not_implemented()`. There is no other dispatch axis for firmware to
fall through to.

### Algorithm Handlers

Protocol column uses the operator-approved `PROTO_<NAME>` tokens (`include/proto_constants.h`,
source of truth `firestarter/doc/PROTOCOLS.md`) — the label IS the number; no dispatch/value change.

| Protocol               | PROTO_ token           | File              | VPP             | Notes                                                        |
|------------------------|------------------------|-------------------|-----------------|--------------------------------------------------------------|
| 0x07                   | `PROTO_EPROM_28PIN`    | eprom.cpp         | 13V via CTRL_VPP_VPE_DROP_ENABLE | Pulse width from DB `pulse-delay` (modal 100µs, 113/170 chips); 1000µs is only the `pulse_delay==0` fallback. Per-byte pulse-to-verify loop (Phase 141): fixed-width pulse, verify, repeat; on convergence this row's `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL` (`eprom_params.cpp`) runs 1 additional full-array verify pass, and a mismatch there emits `MSG_ERR_VERIFY` (0xAF) with the same 5-byte payload `memory_verify_execute` uses. Budget exhaustion during the per-byte loop is `MSG_ERR_MAX_PULSES` (0xBD) at `max_pulses` 25; `energy_cap_us` is 0 (uncapped) on this row, so `MSG_ERR_ENERGY_CAP` (0xBE) and the pre-flight `MSG_ERR_PULSE_TOO_WIDE` (0xAE) refusal are both structurally unreachable here -- see the 0x0B row below, where `energy_cap_us > 0` makes both live. No overprogram. DQ7 polling is a flash-family mechanism and is **not** used on this row. See `tests/golden/eprom_params_citations.json`. |
| 0x08                   | `PROTO_EPROM_32PIN`    | eprom.cpp         | 13V via CTRL_VPP_VPE_DROP_ENABLE (pre-existing defect on this row -- see Notes) | Pulse width from DB (modal 100µs, 104/127 chips); 100µs is only the `pulse_delay==0` fallback. Same per-byte loop, `verify_mode == VERIFY_PER_PULSE_PLUS_FINAL` final pass, and `MSG_ERR_VERIFY` behaviour as the 0x07 row above; `max_pulses` 25 (`MSG_ERR_MAX_PULSES`, 0xBD); `energy_cap_us` 0 (uncapped), so `MSG_ERR_ENERGY_CAP` (0xBE) / `MSG_ERR_PULSE_TOO_WIDE` (0xAE) are unreachable on this row too; no overprogram (D-06, resolved from three vendors). **Pre-existing defect, not introduced by Phase 141:** on this `pins == 32` row, `mem_util_calculate_top_address_register`'s preserve mask excludes `CTRL_VPP_VPE_DROP_ENABLE` whenever `handle->pins >= 32`, so the drop bit asserted above does not survive the block's first `set_address()` -- it is cleared before the first pulse is ever emitted, on every board revision (not a bit collision: `CTRL_ADDRESS_LINE_16` and `CTRL_VPP_VPE_DROP_ENABLE` are distinct bits, 0x01 / 0x100, on every build this project ships). Phase 141 makes the clearing explicit and observable via a named `handle->pins >= 32` branch (`eprom.cpp`) instead of leaving it incidental; choosing the final route (P1 vs. drop resistor) and consolidating the mask sets is Phase 142 / VPP-01 and VPP-03's job. See `tests/golden/eprom_params_citations.json`. |
| 0x0B                   | `PROTO_EPROM_24PIN`    | eprom.cpp         | 12–25V direct   | 24-pin; pulse width from DB (modal 500µs, 21/32 chips); 500µs is only the `pulse_delay==0` fallback; `verify_mode == VERIFY_PER_PULSE` -- verify per pulse, no final full-array pass. Per-byte accumulated-energy cap `energy_cap_us` 50ms (50000us): the cap divides evenly by every shipped width (200/500/1000µs give exactly 250/100/50 pulses, `accumulated` landing on exactly 50000), so "capped at 50ms" is exact for shipped data. With an arbitrary `--pulse-us` value the accumulated-at-failure bound is `< energy_cap_us + w`; evaluating that bound at the D-03-permitted ceiling `w = energy_cap_us` naively gives `2 * 50000 - 1 = 99999`, but that ceiling only permits ONE pulse before failing (a second pulse needs `(i-1)*w < energy_cap_us`, which fails once `w == energy_cap_us`) -- the actual achievable worst case is two pulses at `w = 49999` (the largest width for which a second pulse can still occur), giving `2 * 49999 = 99998` us, not 99999. `max_pulses` 255 (`MSG_ERR_MAX_PULSES`, 0xBD, on exhaustion); energy-budget exhaustion is `MSG_ERR_ENERGY_CAP` (0xBE); a pulse wider than 50000us is refused pre-flight, before any high voltage is enabled, as `MSG_ERR_PULSE_TOO_WIDE` (0xAE) -- this row is where all three budget/refusal IDs are actually reachable. No overprogram. See `tests/golden/eprom_params_citations.json`. |
| 0x0D                   | `PROTO_EEPROM_PARALLEL` | eeprom_28c.cpp   | None (5V)       | SDP disable + DQ7 page poll; **no erase operation at all** (each page write auto-erases internally) |
| 0x0E / 0x27 / 0x28 / 0x29 | `PROTO_SRAM_32PIN` / `PROTO_SRAM_24PIN` / `PROTO_SRAM_28PIN` / `PROTO_SRAM_32PIN_NVRAM` | sram.cpp | None (5V) | Generic read/write; no VPP regulator (BLOCKER-2 mitigation)  |
| 0x06                   | `PROTO_FLASH_NOR_UNLOCK` | flash_nor_unlock.cpp | None (5V)       | AMD unlock, sector erase                                     |
| 0x05                   | `PROTO_FLASH_5V_PAGE`  | flash_5v_page.cpp  | None (5V)       | Page write + DQ7                                             |
| 0x35                   | `PROTO_PHANTOM_0x35`   | flash_5v_page.cpp  | None (5V)       | 0 DB chips (phantom — IC2_ALG_ITE is an ITE EC MCU label, not a memory algo); firmware dispatch preserved for forward-compat; host routes to not_implemented (excluded from KNOWN_PROTOCOLS, DEC-05) |
| 0x39                   | `PROTO_PHANTOM_0x39`   | flash_5v_page.cpp  | None (5V)       | 0 DB chips (phantom — no IC2_ALG constant exists); firmware dispatch preserved for forward-compat; host routes to not_implemented (excluded from KNOWN_PROTOCOLS, DEC-05) |
| 0x10                   | `PROTO_FLASH_INTEL`    | flash_intel.cpp   | 12V via CTRL_VPP_P1_ENABLE | Command register, SR polling                                 |
| 0x34                   | `PROTO_EEPROM_8051BUS` | not_implemented.cpp (PCB-blocked, FUT-01) | None (5V) | No dedicated dispatch arm — falls through the generic `protocol != 0` fail-closed guard |

### Protocol 0x0D notes (AT28C / 28C-family EEPROM)

`configure_eeprom28c()` (`eeprom_28c.cpp`) has no erase operation at all — no
chip-erase, no sector-erase, nothing. The only erase-like behavior is the
implicit per-page auto-erase baked into every page write. The auto SDP-disable
sequence emitted before each write reports its own emission (and measured
duration) but the SDP protection state itself is not readable — a successful
emission proves only that the sequence was sent, never the part's actual
protection state before or after. See `doc/PROTOCOLS.md` §1.6 for the full
model.

### JSON Wire Protocol

The firmware receives JSON commands over serial at 250000 baud. The `algorithm` field (integer, upstream `protocol_id`) is parsed into `handle->protocol` and is the primary dispatch key.

Key fields:
- `algorithm` — integer protocol ID, stored in `handle->protocol`
- `vpp_mv` — VPP voltage in millivolts (used by SAF-04 ADC validation)
- `memory-size` — chip size in bytes
- `pulse-delay` — write pulse width in µs (0 = use handler default)
- `chip-id` — expected manufacturer+device ID (0 = skip ID check)

A legacy `type` key (the pre-v1.20 backward-compat integer field) is no longer
parsed — `json_parser.c` silently skips unknown JSON fields, so a stray `type`
from an older host is safely ignored (see `## Breaking Changes (v1.20)` in
`README.md`).

### Key Files

- `src/json_parser.c` — parses JSON command into `firestarter_handle_t`; unknown fields silently skipped
- `src/proms/memory.cpp` — top-level dispatch (`configure_memory()`)
- `include/firestarter.h` — `firestarter_handle_t` struct definition
- `include/rurp_pinout.h` — control register bit definitions (CTRL_VPP_REGULATOR_ENABLE, CTRL_VPP_VPE_DROP_ENABLE, CTRL_VPP_P1_ENABLE, etc.)

### Constants

Control register bits (from `rurp_pinout.h`):
- `CTRL_VPP_REGULATOR_ENABLE (0x80)` — enable VPP boost regulator
- `CTRL_VPP_VPE_DROP_ENABLE (0x01 legacy / 0x100 rev2)` — drop VPE through resistor to VPP level
- `CTRL_VPP_P1_ENABLE (0x08)` — route VPP to socket pin 1
- `CTRL_VPP_A9_ENABLE (0x02)` — route VPP to A9 (for EPROM chip ID read)
- `CTRL_VPE_ENABLE (0x04)` — apply VPE directly to PGM pin

Firmware flags (from `firestarter.h`):
- `FLAG_FORCE (0x01)` — treat ID mismatch as warning, not error
- `FLAG_CAN_ERASE (0x02)` — chip supports erase before write
- `FLAG_SKIP_ERASE (0x04)` — skip auto-erase in write init
- `FLAG_SKIP_BLANK_CHECK (0x08)` — skip blank check
- `FLAG_VPE_AS_VPP (0x10)` — legacy: direct VPE path (backward compat)

### Hardware Revision Documentation

The operator-facing canonical RURP shield revision reference at `firestarter/doc/SHIELD-REVISIONS.md` is a subset clone of the Firestarter meta-repo investigation document at `.planning/v1.7-SHIELD-REVS.md`. It contains the inventory (§1), per-rev capability matrix (§6), silkscreen → code alias table (§7), and per-rev ADC band table (§9). If any of those sections changes in the meta-repo, update the sub-repo doc in lockstep (Phase 35 / v1.7 — close).

The `rurp_pinout.h` `ADC_BAND_R41_*` `#define` values are the firmware-side source of truth for the band-lookup math; the §4 ADC Band Table in `doc/SHIELD-REVISIONS.md` mirrors those values verbatim. Drift between the two = bug; if the values change in `rurp_pinout.h`, update the doc's §4 table + the meta-repo §9 in the same commit-pair.

Post-Phase-35 semantic note: Plan 01 switched `pinMode(PIN_HW_REVISION_DETECT_ADC)` from `INPUT_PULLUP` to `INPUT` (high-Z), disabling the MCU internal pull-up. The R41 detect divider's R_top is therefore no longer active; the existing ADC band thresholds (`200/220/600`) characterize *A3-net composition* (R41-only-to-GND = low; external-pull-up-active = mid; floating = high), not R41 value. Future v1.8 Rev 2.4 PCB could add an external R_top to restore the original schematic-divider semantics.

### PY32F071 Flash-Path and PCB Documentation

`platform/py32f071/FLASH-PATH-AND-PCB.md` is a subset clone of the Firestarter meta-repo decision
record at `.planning/v1.23-FLASH-PATH-DECISION.md`. It carries five shared sections, named by
marker so a reader can find the contract from the sub-repo, from the meta record, or from this
file — the third of the three places the same five keys are named, matching the v1.7 precedent:
`[SHARED:S1]` the three-tier flash path, `[SHARED:S2]` the PCB checklist, `[SHARED:S3]` the flash
budget, `[SHARED:S4]` the USB vendor and product identity, `[SHARED:S5]` the socket-empty
instruction. If any of those sections changes in the meta-repo, update the sub-repo doc in the
**same change** — and unlike the v1.7 precedent above, this one is enforced mechanically by
`tests/test_flash_path_record_sync.py`, not by lockstep discipline alone, so a divergence is a
test failure rather than a latent inconsistency. Stated honestly: that test module runs in no CI leg on this branch,
so the enforcement is a local-run obligation for anyone editing either copy — do not imply CI
coverage. The seam `FIRESTARTER_META_ROOT`, alongside the existing
`FIRESTARTER_FW_ROOT` and `FIRESTARTER_SIZE_BASELINE`, overrides the resolved meta-repo **root
only**, never the marker name, and it binds at import so it must be set in a child process rather
than monkeypatched; this repository has no central environment-variable inventory, so this
sentence is the one place a reader who is not already inside `tests/meta_presence.py` can
discover it. Origin: Phase 129 / v1.23 (the analog above cites Phase 35 / v1.7).

## Native (Host) Test Environment

The dispatch logic in `configure_memory` is exercised by Unity tests that run
on the host via PlatformIO's `platform = native`. No AVR board is needed.

### Invocation

```bash
pio test -e native                          # run every native suite
pio test -e native -f "*test_dispatch*"     # run only configure_memory dispatch tests
```

### Layout

```
firestarter/
├── platformio.ini                          # [env:native] section: platform=native, test_framework=unity,
│                                           # src_filter = +<proms/>, test_build_src = yes,
│                                           # -D RURP_BOARD_NAME=\"native\"
└── test/
    └── native/
        └── avr/
            └── test_dispatch/
                ├── test_configure_memory.cpp   # Unity RUN_TEST cases — one per KNOWN_PROTOCOLS entry
                ├── host_stubs.cpp              # no-op replacements for rurp_* symbols + LOG_*_MSG PROGMEM strings
                └── avr/
                    └── pgmspace.h              # host shim for AVR PROGMEM macros (incl. PGM_P)
```

### Why a host stub TU?

`[env:native]` cross-compiles `src/proms/*.cpp` (the dispatch + handler TUs)
against host libc + ArduinoFake. The AVR-only TUs (`src/boards/*.cpp`,
`src/dev_tools.cpp`, `src/eprom_operations.cpp`, `src/logging.c`) are excluded
by `src_filter = +<proms/>`. The handlers still reference `rurp_*` hardware
symbols (register writes, ADC reads, chip enable/disable) and the eight
`LOG_*_MSG` PROGMEM strings, so `host_stubs.cpp` provides minimal no-op
implementations that resolve the linker without touching real hardware. The
dispatch tests assert on `handle->firestarter_operation_main` and
`handle->response_code` only — never on register side effects — so the no-op
stubs are functionally complete for this test class.

The host shim at `test/native/avr/test_dispatch/avr/pgmspace.h` defines
`PROGMEM`, `PSTR`, `PGM_P`, and `pgm_read_*` as host-memory equivalents so
that headers including `<avr/pgmspace.h>` compile on a non-Harvard host.

### Reuse pattern for future native tests

To add a new host-side Unity suite, drop `test_*.cpp` files under
`test/native/avr/<dirname>/`. Extend `host_stubs.cpp` only if the new test
references additional `rurp_*` symbols.

**Corrected (v1.22 Phase 119 D-04, 119-02):** the claim that `[env:native]`
needs no changes for a new suite is FALSE and was corrected here. `[env:native]`
uses a POSITIVE `test_filter` allowlist (`platformio.ini`) — a suite directory
is invisible to `pio test` until its path appears in `test_filter`, and its
headers are unreachable until a matching `-I test/native/avr/<dirname>` entry
is added to `build_flags`. Both lists must be updated, in that same env. Since
Phase 119 added a second native env, `[env:native_nodevtools]`, a new suite
must be added to **both** envs' `test_filter` and `-I` lists (four new lines
total) to run under both `-D DEV_TOOLS` and no-`DEV_TOOLS` builds.

**Exception (Phase 140 D-11): `native_params_v131` and `native_loop_v131` are added to NEITHER
pinned env.** The instruction directly above — add a new suite to **both** `[env:native]` and
`[env:native_nodevtools]` — is **overridden** for both `native_params_v131` and
`native_loop_v131`, because both pinned envs are asserted at exactly **141 cases / 17 suites** by
`scripts/baseline/size_baseline.json` through `check_size_baseline.py`'s `compare_native`, so
adding a case to either turns a live gate RED. Both envs follow the `native_trace_v131` precedent
(Phase 138) instead: each env's `test_filter` names only its own suite (not folded into either
pinned env's `test_filter`), neither is in `default_envs`, neither is ever passed to
`check_size_baseline.py` (an unrecognized env name raises an uncaught `KeyError`, exit 1 —
F-138-05) nor to `check_build_warnings.py` (exit 2, no baseline entry for either env), and both
run in **no CI leg** of either repository (F-140-11). `native_loop_v131` originates in Phase 141 /
D-10 — it exists because the frozen `native_trace_v131` fixture goes RED by design in that phase
and cannot verify the per-byte program loop rewrite, so Phase 141 authors its own oracle instead,
carrying the identical four constraints stated above. Both envs' counts are therefore a
**run-by-name obligation** recorded in their respective phase records, never implied to be
CI-covered.
