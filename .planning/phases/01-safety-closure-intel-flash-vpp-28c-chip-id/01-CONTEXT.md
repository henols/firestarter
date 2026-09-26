# Phase 1: Safety Closure (Intel-flash VPP + 28C chip-ID) - Context

**Gathered:** 2026-05-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Close two v1.0 audit gaps with surgical firmware edits and host-side Unity coverage:

1. **SAF-04** — `flash_intel_write_init` performs a pre-pulse VPP ADC compare so REQ-SAF-01 ("VPP voltage compared to setpoint before every write pulse") holds for all 39 algorithm=0x10 Intel-flash chips (the only chip family in firmware where it currently doesn't).
2. **SAF-05** — `eeprom28c_write_init` honours `handle->chip_id` when non-zero (proper AT28C JEDEC chip-id mode entry + compare + abort on mismatch), so REQ-SAF-02 holds the moment any algorithm=0x0D entry gains a `chip_id_value`. Currently vacuous (no chip in the regenerated DB sets it for 0x0D), but the firmware path must be ready.
3. **SAF-06** — Unity tests on `[env:native]` cover both new safety checks: low-VPP path returns the existing voltage error code on the Intel-flash side; matching/mismatching fake chip-ID exercises both branches on the 28C side. Pre-existing 15 dispatch tests must remain GREEN.

**In scope:**
- New VPP check inside `flash_intel_write_init` (after regulator is already up + 500ms delay) in `firestarter/src/proms/flash_intel.cpp`.
- New JEDEC chip-id check inside `eeprom28c_write_init` (gated on `handle->chip_id > 0`) in `firestarter/src/proms/eeprom_28c.cpp`.
- New `[env:native]` Unity tests with their own test directories (no growth of `test_dispatch/`).

**Out of scope:**
- Hardware-revision-0 board behaviour beyond mirroring the existing `eprom_check_vpp` guard (REV0 produces a warning + skips ADC).
- Modifying `eprom.cpp` itself beyond what the researcher recommends if a helper is extracted (see D-04 / D-05 below).
- Replacing the v1.0 `vpp` JSON wire key with `vpp_mv` (that is Phase 2 / WIRE-01).
- Reading VPP for any AT28C path — 0x0D chips are 5V-only and never engage the regulator.
- Hardware validation on a real RURP shield (deferred to Phase 4 HW-05, which gates on SAF-04 shipping first).
- VERIFICATION.md artifact for this phase (the milestone is shipping `/gsd-verify-work` per phase + retroactive backfill in Phase 3).

</domain>

<decisions>
## Implementation Decisions

### SAF-04 — Intel-flash VPP check shape
- **D-01:** **Failure semantics mirror `eprom_check_vpp` exactly.** Low VPP → `RESPONSE_CODE_WARNING` (proceeds), High VPP → `RESPONSE_CODE_ERROR` (aborts), `FLAG_FORCE` downgrades errors to warnings. Same tolerance bands as the v1.0 EPROM path: low band = `handle->vpp_mv * 95 / 100`, high band = `handle->vpp_mv + 500` mV. Rationale: consistency with the v1.0 verified pattern beats the audit-text wording "aborts with the existing voltage error code" — the audit text was loose; the actual `eprom_check_vpp` precedent makes low-VPP a warning, and Intel flash hardware has its own SR.VPP-error bit (already polled in `flash_intel_poll_sr`) to catch a fundamentally bad rail at execution time. SAF-06 test phrasing ("low-VPP path returns the voltage error code") refers to the existing voltage-error reporting infrastructure (`firestarter_warning_response_format` is part of the same response family — same wire response prefix `WARN:` vs `ERROR:`); the test must assert response_code is set, not specifically `RESPONSE_CODE_ERROR`.
- **D-02:** **The check runs after the regulator is already up.** `flash_intel_write_init` already enables `REGULATOR | P1_VPP_ENABLE` and sleeps 500 ms before any write pulse — the new check inserts between that delay and the first chip-ID / erase / blank-check call. No new regulator toggling.
- **D-03:** **Mirror the `HARDWARE_REVISION` REV0 guard.** Same `#ifdef HARDWARE_REVISION` block as `eprom_check_vpp`: REV0 boards can't read VPP, so issue `firestarter_warning_response("Rev0 dont support reading VPP/VPE")` and skip the ADC compare. Forward-compat with rev0 hardware that's already in user hands.

### SAF-04 — Code organization (DEFERRED to researcher)
- **D-04:** **Researcher decides** between (a) inline-copy a `flash_intel_check_vpp()` static helper into `flash_intel.cpp`, or (b) extracting `mem_util_check_vpp_low(handle, low_pct, high_offset_mv)` into `memory_utils.{h,cpp}` and refactoring `eprom_check_vpp` to call it. Trade-off: (b) is DRY but touches verified v1.0 code; (a) is audit-text-aligned ("1-2 lines in flash_intel.cpp") and zero-risk to v1.0 paths. `gsd-phase-researcher` should inspect the actual reuse surface — hardware-revision guard, FORCE-flag handling, message formatting, regulator-state assumption — and recommend the shape in RESEARCH.md. Whichever choice the planner adopts, both implementations must keep the v1.0 EPROM behaviour byte-identical (the 15 existing Unity dispatch tests must remain GREEN unchanged, and the W27C512 / 29F040 / SST39SF040 / AT28C256 functional paths must not regress when re-run by Phase 4 hardware validation).

### SAF-05 — AT28C JEDEC chip-id sequence
- **D-05:** **Implement the proper Atmel AT28C JEDEC chip-id mode.** Sequence: write 0xAA → 0x5555, 0x55 → 0x2AAA, 0x90 → 0x5555 (enter chip-id mode), read manufacturer at 0x0000 and device at 0x0001, write 0xF0 → 0x5555 (or any address — JEDEC spec lets the exit command go anywhere) to leave chip-id mode. Pack the 16-bit chip-id as `(mfr << 8) | device` matching `handle->chip_id` and `flash_intel_check_chip_id`'s packing. Rationale: SAF-05 is forward-compat only (no DB chip triggers it today), but doing it right the first time means the moment a user populates `chip_id_value` on a 0x0D entry — via `~/.firestarter/database.json` override or a future upstream DB change — the check works. A weaker "minimal stub" form would create a debug-debt landmine for the next maintainer who hits a real chip.
- **D-06:** **Gate on `handle->chip_id > 0`** (matches `flash_intel_write_init:50` pattern). Zero means "skip the check, no expected ID known." Non-zero means "compare; abort on mismatch."
- **D-07:** **FORCE-flag semantics match the established pattern.** `is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR` — same line as `flash_intel_check_chip_id:121` and `eprom_internal_check_chip_id` (via the `error_code` parameter call sites). Message format: `"Chip ID %#04x dont match expected ID %#04x"` (verbatim from `flash_intel_check_chip_id`).

### SAF-05 — Init ordering (DEFERRED to researcher)
- **D-08:** **Researcher decides** whether the chip-id check runs (a) before the SDP-disable sequence in `eeprom28c_write_init` (fail-fast — verify identity before modifying chip state, matches `flash_intel_write_init`'s "chip_id check then erase then blank check" ordering), or (b) after SDP-disable (some AT28C parts may need SDP cleared before allowing chip-id mode entry). Both sequences share the magic addresses 0x5555 / 0x2AAA, so the order matters — running SDP-disable first changes the device state machine. `gsd-phase-researcher` should consult the Atmel AT28C256 / AT28C64 datasheets on chip-id mode entry preconditions and recommend the safe order in RESEARCH.md. Whichever order is chosen, the blank-check call must remain last (matches current v1.0 init shape).

### SAF-06 — Test layout
- **D-09:** **New test directory per safety check.** Two new dirs under `firestarter/test/native/avr/`:
  - `test_flash_intel_vpp/test_flash_intel_vpp.cpp` — exercises SAF-04 by setting a mocked `rurp_read_voltage_mv()` return value across cases (nominal / low / high / REV0) and calling `flash_intel_write_init` via the same hand-built `firestarter_handle_t` pattern used in `test_configure_memory.cpp`.
  - `test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` — exercises SAF-05 by setting a mocked `firestarter_get_data()` return-sequence (via the handle's function pointer field) for the autoselect-read cycle and asserting response_code branches on matching vs mismatching id.
- **D-10:** **Keep `host_stubs.cpp` shared.** Both new test dirs reuse the existing host stubs via PIO's automatic discovery. For per-test mocking (variable VPP, variable `get_data` returns), prefer per-test mutable globals in a small new `mock_globals.cpp` colocated with each suite, OR have each suite set the handle's function pointers to local lambdas/static functions inside the test body. Choice between approaches is Claude's discretion at planning time — the constraint is that mocking must not require editing `host_stubs.cpp` (which is shared with the dispatch suite and must remain a no-op TU for that suite's contract).
- **D-11:** **Dispatch-suite regression unchanged.** The 15 existing Unity dispatch tests in `test_dispatch/test_configure_memory.cpp` must remain GREEN unchanged. No edits to that suite beyond what (D-04) might require if the planner picks the helper-extraction path.

### Claude's Discretion
- Exact insertion line numbers within `flash_intel_write_init` and `eeprom28c_write_init`.
- Whether to introduce a named constant for the JEDEC unlock magic bytes or inline-write them (the existing `EEPROM_SDP_DISABLE` table demonstrates the project's preference for a `byte_flip_t[]` array — likely worth following).
- Per-test-suite `setUp` / `tearDown` wiring for ArduinoFakeReset() invocations and mutable-mock-state resets.
- Whether to add a `flash_intel_check_vpp` declaration to `firestarter/include/flash_intel.h` (only needed if the helper has external linkage; static-in-TU stays internal).
- Test names, but they should be descriptive (`test_flash_intel_low_vpp_warns`, `test_flash_intel_high_vpp_errors`, `test_eeprom28c_matching_chip_id_proceeds`, `test_eeprom28c_mismatching_chip_id_errors`, …) and one assertion per test.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Audit + milestone context
- `.planning/MILESTONES.md` §"Known Gaps" — WARNING-1 (REQ-SAF-01 partial — Intel-flash) and WARNING-2 (28C chip-id forward-compat) — the audit text the planner must close.
- `.planning/REQUIREMENTS.md` §"Safety Closure" — SAF-04 / SAF-05 / SAF-06 wording.
- `.planning/ROADMAP.md` §"Phase 1: Safety Closure" — Success Criteria 1-5 (the truth checklist).
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — full WARNING-1 / WARNING-2 context (referenced by MILESTONES.md but holds the raw audit findings).
- `.planning/milestones/v1.0-INTEGRATION-CHECK.md` — Phase 12 integration check; baseline for what's already covered by `check_dispatch.py` + existing Unity tests.

### Codebase entry points — firmware
- `firestarter/src/proms/flash_intel.cpp:47-62` — current `flash_intel_write_init` (the SAF-04 edit site). Regulator + 500ms delay already exists; the new check inserts after the delay and before the chip-id branch.
- `firestarter/src/proms/flash_intel.cpp:115-124` — `flash_intel_check_chip_id` — the existing chip-id pattern to mirror for SAF-05 packing / FORCE-flag handling.
- `firestarter/src/proms/eprom.cpp:199-232` — `eprom_check_vpp` — the canonical VPP-compare pattern (REV0 guard, regulator gating, tolerance bands, warn-low / error-high). SAF-04 mirrors this.
- `firestarter/src/proms/eprom.cpp:250-258` — `eprom_generic_init` — the canonical "check vpp THEN check chip_id" init order.
- `firestarter/src/proms/eeprom_28c.cpp:25-32` — `EEPROM_SDP_DISABLE[]` table; the AT28C JEDEC chip-id sequence uses the same magic addresses (0x5555 / 0x2AAA) and the `byte_flip_t` table style is the project convention for this kind of sequence.
- `firestarter/src/proms/eeprom_28c.cpp:45-57` — current `eeprom28c_write_init` (the SAF-05 edit site).
- `firestarter/src/proms/eeprom_28c.cpp:79-90` — `eeprom28c_wait_for_write` — used by the SDP-disable wait; the chip-id read does not need it (autoselect mode is immediate, no polling).
- `firestarter/include/firestarter.h:75-106` — `firestarter_handle_t` struct: `vpp_mv` (uint16, line 85), `chip_id` (uint16, line 88), `response_code`, the `firestarter_*` function pointers (lines 94-104) that the SAF-06 tests will set to mock handlers.
- `firestarter/include/firestarter.h:40-62` — response codes + `is_flag_set` / `FLAG_FORCE`.
- `firestarter/include/logging.h:184-202` — `firestarter_warning_response*` / `firestarter_error_response*` / `firestarter_response_format` macros — the SAF-04 / SAF-05 error-reporting surface.
- `firestarter/include/rurp_shield.h` — `REGULATOR`, `P1_VPP_ENABLE`, `VPE_TO_VPP`, `A9_VPP_ENABLE`, `VPE_ENABLE` bit definitions.
- `firestarter/src/proms/flash_utils.{h,cpp}` — `flash_execute_command(byte_flip_t[])` helper (used by `EEPROM_SDP_DISABLE`); the chip-id sequence can reuse it for the unlock+0x90 writes.

### Codebase entry points — test infra
- `firestarter/platformio.ini` §`[env:native]` — `platform = native`, `test_framework = unity`, `src_filter = +<proms/>`, `test_build_src = yes`. New test dirs need no platformio.ini change.
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — pattern reference: `make_handle()` helper, `setUp` / `tearDown`, `RUN_TEST` enumeration in `main`. SAF-06 suites should mirror this skeleton.
- `firestarter/test/native/avr/test_dispatch/host_stubs.cpp:97` — `rurp_read_voltage_mv()` currently returns 0. SAF-06 must NOT edit this file (shared with dispatch suite); per-suite mocking must use local TU-private state or function-pointer overrides on the handle.
- `firestarter/test/native/avr/test_dispatch/avr/pgmspace.h` — host shim for PROGMEM / PSTR / pgm_read_* on native. New test dirs inherit it transitively via include path.
- `firestarter/CLAUDE.md` §"Native (Host) Test Environment" — explicit reuse pattern: "drop test_*.cpp files under test/native/avr/<dirname>/; extend host_stubs only if the new test references additional rurp_* symbols". SAF-06 follows this contract.
- `firestarter/CLAUDE.md` §"Algorithm Handlers" table — confirms protocol 0x10 = `flash_intel.cpp`, 0x0D = `eeprom_28c.cpp` (the two TUs this phase edits).

### v1.0 phases this phase touches
- `.planning/milestones/v1.0-phases/03-eprom-algorithms/` — Phase that established `eprom_check_vpp` (mirror pattern for SAF-04).
- `.planning/milestones/v1.0-phases/05-intel-flash/` — Phase that built `flash_intel.cpp` (the SAF-04 edit target).
- `.planning/milestones/v1.0-phases/06-eeprom-page-write/` — Phase that built `eeprom_28c.cpp` and the SDP-disable sequence (the SAF-05 edit target).
- `.planning/milestones/v1.0-phases/07-chip-id-safety/` — Phase that established `eprom_internal_check_chip_id` + `flash_intel_check_chip_id` (mirror pattern for SAF-05).
- `.planning/milestones/v1.0-phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/` — Phase that built the `[env:native]` test harness (mirror pattern for SAF-06 test layout).

### Requirements
- REQ-SAF-01 (`.planning/milestones/v1.0-REQUIREMENTS.md`) — "VPP voltage compared to setpoint before every write pulse" — the v1.0 requirement SAF-04 closes for Intel flash.
- REQ-SAF-02 (`.planning/milestones/v1.0-REQUIREMENTS.md`) — "Chip ID validated before write" — the v1.0 requirement SAF-05 forward-closes for 28C.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`eprom_check_vpp` (eprom.cpp:199-232):** Canonical VPP-compare implementation. Already handles REV0 guard, tolerance bands, FORCE-flag downgrade, regulator gating. SAF-04 either copies this shape or — if D-04 picks the helper-extract path — refactors a shared helper.
- **`flash_intel_check_chip_id` (flash_intel.cpp:115-124):** Already-in-place chip-id read + compare + FORCE-flag-aware response. SAF-05 mirrors the response shape and the `chip_id > 0` gate, but the read sequence differs (JEDEC magic-address unlock vs. Intel command-register).
- **`flash_execute_command(byte_flip_t[])` (flash_utils.cpp):** Drives a byte-flip-table sequence. Reusable for the JEDEC chip-id mode-entry unlock writes (0xAA / 0x55 / 0x90 to 0x5555 / 0x2AAA / 0x5555) and the exit write (0xF0).
- **`make_handle()` (test_configure_memory.cpp:50-57):** Pattern for zero-initialized `firestarter_handle_t` with named fields. SAF-06 suites copy this helper.
- **`host_stubs.cpp` (test_dispatch/host_stubs.cpp):** Provides every `rurp_*` symbol the proms TUs link against. New SAF-06 suites inherit it via PIO's `test_build_src = yes` automatic discovery — no edits needed (per D-10).

### Established Patterns
- **Init-time safety order:** `eprom_generic_init` does VPP-check THEN chip-id-check THEN proceed. `flash_intel_write_init` currently does chip-id-check THEN proceed (no VPP-check). SAF-04 adds the VPP-check before the chip-id-check, matching `eprom_generic_init`'s order — chip identity is meaningless if the rail is wrong.
- **FORCE-flag downgrade:** Every safety check uses `is_flag_set(FLAG_FORCE) ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR`. Both new checks honour this.
- **Response message format:** `"Chip ID %#04x dont match expected ID %#04x"` (current literal, verbatim from `flash_intel_check_chip_id`; do NOT "fix" the grammar — it would diverge from grep-able historical messages).
- **`byte_flip_t[]` arrays:** Project convention for fixed sequences of `(address, data)` writes — `EEPROM_SDP_DISABLE` exemplifies. New JEDEC unlock sequence likely follows the same shape.
- **Test layout — one TU per cmd path:** Existing dispatch suite tests `configure_memory()` only; new suites test `*_write_init()` directly via `handle->firestarter_operation_init(&handle)` after dispatch.

### Integration Points
- **No wire-protocol change.** Both new checks read existing `firestarter_handle_t` fields (`vpp_mv`, `chip_id`). The Python emitter is untouched in this phase.
- **No new `rurp_*` symbol.** `rurp_read_voltage_mv()` and the data-bus helpers already exist; SAF-06 only needs to mock them per-suite.
- **No new dispatch entry.** The protocol-prefix dispatch in `memory.cpp::configure_memory` is unchanged; both edits are interior to existing handlers.

</code_context>

<specifics>
## Specific Ideas

### AT28C JEDEC chip-id sequence (concrete reference)
The Atmel AT28C256 / AT28C64 datasheets specify the chip-id mode (sometimes called "Product Identification mode") as:

| Step | Address | Data | Purpose |
|------|---------|------|---------|
| 1    | 0x5555  | 0xAA | Unlock cycle 1 |
| 2    | 0x2AAA  | 0x55 | Unlock cycle 2 |
| 3    | 0x5555  | 0x90 | Enter chip-id mode |
| 4    | 0x0000  | —    | Read manufacturer code |
| 5    | 0x0001  | —    | Read device code |
| 6    | 0x5555  | 0xF0 | Exit chip-id mode (return to read mode) |

Pack as `chip_id = (manufacturer << 8) | device` — matches `flash_intel_check_chip_id`'s packing convention. **Verify against datasheet** during planning — researcher should confirm the exact magic addresses (0x5555 vs 0x0555 vs other) and exit command for the AT28C family the planner targets.

### Tolerance bands (verbatim from eprom_check_vpp)
```c
if (vpp_mv > (uint32_t)handle->vpp_mv + 500) { /* HIGH — error */ }
else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) { /* LOW — warning */ }
```
(Yes, the high check uses `vpp_mv + 500` as a flat offset and the low check uses 95% as a proportional band — that asymmetry is intentional in the v1.0 pattern and SAF-04 reproduces it.)

### REV0 guard pattern (verbatim from eprom_check_vpp)
```c
#ifdef HARDWARE_REVISION
    if (rurp_get_hardware_revision() == REVISION_0) {
        firestarter_warning_response("Rev0 dont support reading VPP/VPE");
        return;
    }
#endif
```

### Test-suite directory skeleton
```
firestarter/test/native/avr/
├── test_dispatch/                  (existing — UNCHANGED)
│   ├── test_configure_memory.cpp
│   ├── host_stubs.cpp
│   └── avr/pgmspace.h
├── test_flash_intel_vpp/           (new — SAF-04 + SAF-06)
│   └── test_flash_intel_vpp.cpp
└── test_eeprom28c_chip_id/         (new — SAF-05 + SAF-06)
    └── test_eeprom28c_chip_id.cpp
```

</specifics>

<deferred>
## Deferred Ideas

- **Extract `mem_util_check_vpp(...)` as a shared helper** — researcher recommendation per D-04. If they pick "inline-copy" in this phase, the extraction can still happen in a future cleanup phase (no v1.1 milestone slot exists for it).
- **Per-cmd VPP check coverage on the other Intel-flash paths** — `flash_intel_erase_execute` also enables `REGULATOR | P1_VPP_ENABLE` and delays 500ms before issuing erase commands. SAF-04 closure scope is `_write_init` only (per audit text and ROADMAP success criterion #1); if `_erase_execute` deserves the same check, that's a follow-up for v1.2.
- **Datasheet variance across AT28C variants** — AT28C17 / AT28BV-family parts may have slightly different chip-id magic addresses or modes. SAF-05 targets the most common (AT28C256 / AT28C64) JEDEC sequence; per-variant divergence becomes interesting only when a user populates `chip_id_value` for one of the rarer parts. Researcher to note in RESEARCH.md whether the chosen sequence is universal across the Phase 13 override-affected chip set.
- **HARDWARE_REVISION REV0 abort-or-warn behaviour for Intel-flash** — current `eprom_check_vpp` issues a warning and silently proceeds on REV0. For 12V Intel-flash that might be too permissive (a REV0 board can't validate the highest-VPP rail in the firmware). Phase 1 mirrors the existing pattern for consistency; tightening to a hard refusal on REV0 is a separate safety call deferred to v1.2.
- **Re-run Phase 12 `check_dispatch.py` against the post-SAF-04 firmware** — the host-side regression scan should be invoked once more to confirm no chip flips dispatch. This is a Phase 3 (Retroactive Verification) concern, not a Phase 1 deliverable.

</deferred>

---

*Phase: 01-safety-closure-intel-flash-vpp-28c-chip-id*
*Context gathered: 2026-05-11*
