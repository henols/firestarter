# Spec: Correct VPP/VPE voltage reading — decompose the error, then fix it

Spec folder: `agent-os/specs/2026-09-26-1826-voltage-reading-accuracy/`

## Context

The firmware's VPP/VPE reading is wrong by a measured **+6.8 % to +8.3 %**, high, on two
independently calibrated boards (backlog 999.38, ROADMAP.md:7424). The mechanism has been
**undetermined** since 2026-08-29. It is not a cosmetic reporting problem:

- A correctly set 12.0 V rail reads ~12.9 V, which is **above the hard HIGH error threshold** at
  `handle->vpp_mv + 500` ([eprom.cpp:547](firestarter_fw/src/proms/eprom.cpp#L547)). Cell A3/B2's
  W27C512 write was stopped for exactly this reason. **The instrument error is blocking legitimate
  writes.**
- The −5 % LOW window is *narrower* than the error, so `MSG_WARN_VPP_LOW` is blind to real
  shortfalls. v1.40 RAIL-03 is recorded as adjudicated-UNMET on this basis.
- A standing operational rule exists solely to work around it: never set the pot against the
  firmware's own reading, or the real rail is driven to ~11.2 V.

### What the measurement chain actually is

`rurp_read_voltage_mv` ([rurp_common.cpp:52-96](firestarter_fw/src/boards/rurp_common.cpp#L52-L96)):

```
Vin_mV = (adc × 1100 × (R1 + R2)) / (bandgap_adc × R2)
```

folded for 32-bit as `k = 1100 × (R1+R2) / R2`, `Vin = (adc × k + bg/2) / bg`; at the shipped
defaults `k = 7850` exactly. `rurp_read_vcc_mv` uses `1126400 = 1100 × 1024` from the same reading.

The design is ratiometric, so **VCC cancels exactly and is not an error source**. Only two terms
can be wrong, and both are guesses:

1. **`1100`** — the ATmega bandgap. Datasheet spread is **1.0–1.2 V per chip**, and AVR has no
   factory trim word. Multiplicative on every reading, and it corrupts the VCC report too.
2. **`R1=270000 / R2=44000`** ([rurp_shield.h:47-48](firestarter_fw/include/rurp_shield.h#L47-L48)).
   The Rev 1 schematic carries 270k, but **has no 44k part at all** — its only values are 22k (×38),
   4k7 (×21), 1k (×4), 270k (×3) and a 50k pot. 44000 is presumably 22k+22k, never verified.

### Three pieces of evidence already on file

1. **Every Leonardo bench log since v1.2 reports `Internal VCC: 5.5 V`.** An ATmega32U4 cannot run
   at 5.5 V (operating max). That back-solves to a real bandgap near **1.00–1.01 V**, which alone
   would make VPP read **+9 to +10 % high** — more than the observed error, meaning the divider term
   partly cancels it. Uno logs report 5.0 V, a different and smaller error. This number has been
   printed on screen for two years and never read as an instrument fault. **It is a free,
   no-hardware measurement of error term 1.**
2. **Phase 199's two paired readings decide the error shape.** 18700/17380 = **1.0759** and
   23900/22140 = **1.0795** — two ratios within 0.3 % of each other across a 5 V span. The error is
   **pure gain, no offset**. This retires the seed's D1 hedge ("let the procedure discover the
   model"): the data is already in, and a one-point-through-origin correction is sufficient.
   It also rules out a series drop in the P1 routing, which would have shown as a constant *offset*
   (1320 mV vs 1760 mV), not a constant ratio.
3. **The schematic's own boost math contradicts the ADC.** The Rev 1 sheet states
   `VPE-Max = 1.23 × ((22000+50000+2350+4700)/4700 + 1) = 21.92 V`. The meter read **22.14 V** at
   max pot (+1.0 % — excellent agreement). The firmware read **23900 mV, 9 % above a voltage the
   MIC2288 feedback network physically cannot produce.** The meter agrees with the hardware; the
   ADC is the outlier.

### Why "solve it in firmware" has a hard limit, and what is still firmware-only

**On AVR there is no absolute voltage reference anywhere in the chain.** AVCC is USB-derived and
unspecified better than ±5 %; the bandgap is a ±9 % per-chip part with no factory calibration word.
Every quantity the firmware can read is relative to one of those two. No firmware change can make
the reading *absolutely* accurate. One external measurement per board is unavoidable for term 1 —
but it can be **one number, typed once**.

What **is** firmware-only, and worth doing whatever the measurement says:

- Correcting `VALUE_R1`/`VALUE_R2` if the real parts differ — **shield-wide, fixes every board.**
  This is the part of the user's preferred outcome that may genuinely be reachable.
- Averaging, post-mux settling, and a VCC plausibility guard.
- Reporting full millivolts. **Today the wire carries only tenths of a volt**
  ([hardware_operations.cpp:71-76](firestarter_fw/src/hardware_operations.cpp#L71-L76)), a 100 mV
  grid that caps any future calibration at ~0.8 % resolution before it starts.
- The `CONFIG_VERSION` stranding defect (pending todo): `VER06` was never bumped when `VALUE_R1`
  changed 1000→270000, so an already-written EEPROM keeps the stale value forever.
- Replacing the fail-open `return 0` on an implausible calibration with a real refusal.
- **PY32F071 is a different case.** `rurp_read_vcc_mv` there uses the nominal 1200 mV VREFINT and
  ignores any factory calibration word. If the part has one, that is a genuine firmware-only
  absolute fix on ARM. Verification deferred — no PCB exists.

### Outcome

This spec **decomposes the error into its two terms by measurement**, applies the part of the fix
that is firmware-only, and leaves the per-board calibration design (the dormant seed
`.planning/seeds/voltage-reading-whitebox-calibration.md`, decisions D1–D7 in
`.planning/notes/voltage-cal-design-decisions.md`) as a follow-up spec now grounded in numbers
rather than hypothesis. The guard window is retuned once the reading is trustworthy, which closes
v1.40 RAIL-03.

## Shaping decisions (this session)

- **D-A. Diagnose, then fix.** Operator choice. The bench decomposition runs before any model
  change. Instrument fixes that are correct either way ship first, so the session measures a clean
  instrument.
- **D-B. Probe point = the VPP/VPE net the ADC senses.** Operator choice. The evidence says the drop
  bit switches the MIC2288 *feedback* network — i.e. VPP and VPE are two **regulated setpoints of
  one physical net**, not a series drop: the VPE−VPP difference is not constant and not a constant
  ratio across pot settings (1.7 V, 2.2 V, 4.76 V from the v1.2 and Phase 199 records), which
  neither a fixed series resistor nor a fixed divider can produce, but two affine setpoint curves
  with different slopes can. Confirm this in Task 4 rather than assuming it. Two consequences: the
  net is probeable anywhere, and **one divider calibration serves both rails** — no separate VPE
  path (seed D4). If no test point is accessible, substitute socket pin 1 with the P1 route asserted
  (the Phase 199 method) and **record the substitution explicitly**.
- **D-C. Guard window is in scope, retuned after the fix** — not before. Operator choice. The new
  window is derived from the measured residual uncertainty, not guessed.
- **D-D. Per-board calibration is NOT built in this spec.** The seed's two-stage design stands;
  this spec supplies the numbers that tell us how much of it is actually needed. If the measurement
  shows the divider term dominates, the follow-up may shrink to nothing.
- **D-E. The error model is gain-only.** Evidence 2 settles it. Do not build offset fitting.
- **D-F. Write the predictions before the measurement.** Task 4 records falsifiable predictions for
  each hypothesis first. This project's "honest claims" rule; also the only way a second board tells
  us anything.
- **D-G. Mechanical decisions (taken, not asked):**
  - The pure conversion math is extracted from the AVR register access so it can be natively
    tested. `src/boards/rurp_common.cpp` is outside every `build_src_filter`, so the math has **no
    native and no bench coverage** today — only `tests/test_voltage_reformulation_oracle.py`, a
    source-scanning contract that `testing/no-source-introspection` forbids extending.
  - Raw ADC counts reach the host through a **new dev-gated command**, not by widening the existing
    fixed-length `MSG_DATA_VPP_VOLTAGE` (4×u16, `param_bytes=8`) — widening a fixed-length DATA
    frame breaks older hosts.
  - `tools/catalog/messages.toml`'s comment on `MSG_DATA_VPP_VOLTAGE` is **already stale** (it says
    "raw millivolt integers"; the firmware sends pre-split tenths). Corrected in the same edit.
  - Any `CONFIG_VERSION` bump resets `r1`/`r2` on every board. Accepted — it resolves the stranding
    todo, and the operator's boards are re-measured in this spec anyway.

---

## Task 1: Save spec documentation

Create `agent-os/specs/2026-09-26-1826-voltage-reading-accuracy/`:

- **`plan.md`** — this plan.
- **`shape.md`** — scope, decisions D-A…D-G, context (references, product alignment).
- **`standards.md`** — full text of each standard named below, with why it applies.
- **`references.md`** — the prior art, listed under Task 8.
- **`visuals/`** — the Rev 1 schematic extract (boost feedback math, `R16 270k`, the value census)
  and any bench photographs of the probe points once Task 4 runs.

---

## Task 2: Make the conversion math testable, and fix the instrument

Firmware only. No model change — this task must not move any reading. It exists so Task 4 measures
a clean instrument and so Task 5 can change the model with tests instead of a source scan.

**Split the pure math from the hardware access** in
[rurp_common.cpp](firestarter_fw/src/boards/rurp_common.cpp):

- Extract `rurp_scale_voltage_mv(uint32_t adc, uint32_t bandgap_adc, uint32_t r1, uint32_t r2)` and
  the VCC equivalent into a TU with no `<Arduino.h>` and no AVR registers.
- Add that TU to `build_src_filter` in `[native_base]`, and register a new Unity suite in **both**
  `test_filter` and `shared_build_flags` (per `testing/native-firmware-tests`, one entry in each
  list covers `native` and `native_nodevtools`).
- Port `tests/test_voltage_reformulation_oracle.py`'s cases into the native suite —
  `k == 7850`, the `adc=1023, bg=225 → 35691 mV` point, the two uint32 guards (`sum > 3900000`,
  `k > 4194303`) — then **delete the Python source-contract scan**, as
  `testing/no-source-introspection` requires when you touch one.

**Instrument fixes:**

- **Average.** Both the A2 read and the bandgap read take a single conversion today. Use the
  existing `analog_read_avg8` pattern from
  [rurp_hw_rev_utils.h:52-58](firestarter_fw/include/rurp_hw_rev_utils.h#L52-L58). The rail is a
  ~1 MHz PWM boost; a single sample catches ripple.
- **Settle after the mux change.** `rurp_get_bandgap_adc_reading()` leaves ADMUX on the bandgap
  channel and the next `analogRead(A2)` converts immediately with no delay — the `delay(2)` exists
  only on the bandgap side. Discard the first conversion after a channel change. Cite the AVR
  datasheet figure in the comment (`firmware/timing`).
- **Fail closed on an implausible calibration.** `rurp_read_voltage_mv` currently returns `0` when
  `r2 == 0` or a guard trips. `0` reads as "low" and only raises `MSG_WARN_VPP_LOW`, a *warning*, so
  a write proceeds against an unknown rail. That is fail-open and violates
  `firmware/fail-closed-refusals`. Refuse with an error ID instead.
- **Guard the VCC report.** A reported VCC outside a plausible band (roughly 4.0–5.5 V) is an
  instrument fault, not a supply fault. Surface it — the 5.5 V figure that decides this whole
  investigation has been on screen unremarked since v1.2.
- **Delete the dead `VCC_CALC_CONSTANT`** at
  [leonardo_rurp_shield.cpp:27](firestarter_fw/src/boards/leonardo_rurp_shield.cpp#L27).

Report flash and RAM for `leonardo` (stable **and** `DEV_TOOLS=1`) and `uno`, per
`firmware/size-reporting`. Leonardo margin at last measure was 4856 B of the 28672 B ceiling.

---

## Task 3: Raw-count diagnostic readout

Task 4 cannot decompose anything from a 100 mV grid. It needs the raw ADC counts.

- Add one dev-gated command that returns `bandgap_adc`, `voltage_adc`, the full `vcc_mv`, the full
  `voltage_mv`, and the live `r1`/`r2`. Dev-gated means it ships on beta only, which is where the
  bench board runs.
- Catalog edit in the **meta repo only** (`tools/catalog/messages.toml` + `codegen.py` for both
  targets) — `protocol/message-catalog`. Never hand-edit `messages.h` / `messages.py`.
- Correct the stale `MSG_DATA_VPP_VOLTAGE` comment in the same edit.
- Add the matching host command. New command ordinals go in **both**
  `firestarter_fw/include/firestarter.h` and `firestarter_app/firestarter/constants.py`
  (`protocol/duplicated-constants`), and ship firmware before host (`protocol/rollout-compatibility`).
- Bench prerequisite: `dev reg` only completes on firmware carrying `7eed3af`. Every published beta
  through `3.0.0b33` times out on it. Build and flash a current beta-configured image
  (`PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo`) before the session, and record
  what is actually on the board.

---

## Task 4: The bench decomposition session

**Operator-gated. Must not run under `--auto` or `--chain`.** Chip out of the socket throughout.
Record the port identity per task — `/dev/ttyACM*` numbering shuffles across replug.

**Write the predictions first (D-F), before any reading:**

| If the dominant term is… | Then the two boards will show… | And the fix is… |
|---|---|---|
| Bandgap (per-MCU) | Different reported VCC per board; each board's VPP error tracks its own VCC error; divider resistances measure as expected | Per-board calibration. Not firmware-only. |
| Divider (shield-wide) | Both boards report ~5.0 V VCC yet both over-read VPP by the same %; measured divider ratio ≠ 314/44 | **Corrected compiled defaults — firmware-only, fixes every board.** |
| Both | Reported VCC differs per board *and* the residual after removing the bandgap term is common | Corrected defaults for the shield term + calibration for the MCU term. |

Given the 5.5 V / 5.0 V split already on file, "both" is the expected outcome; the value of the
session is the **split ratio**, which sizes the follow-up.

**Stage 1 — bandgap, per board. No pot, no high voltage.** Meter on the Arduino 5 V header pin;
read the raw bandgap count from Task 3. `V_bg = VCC_meter × bandgap_adc / 1024`. Do this on **both**
boards. A `V_bg` outside 1000–1200 mV means the model is wrong somewhere else and the session stops.

**Stage 2 — divider, per shield.** Hold the rail with `dev reg 0 0 <composite> -f` and the
firmware's own `while (!rurp_user_button_pressed())` wait — **not** `hold_rail.py`, which prints
`RAIL HELD` without reading an ack and has produced dark LEDs and no rail. Confirm the hold is real
by a probe timing out against it. Release by pressing USR, never `pkill`.

At **2–3 pot settings**, record the meter reading at the probe point (D-B) and the raw A2 count at
that instant — one confirmation read, no monitor loop, operator sets the pot alone. With `V_bg`
known, back-solve `(R1+R2)/R2` exactly. Three points test linearity and confirm D-E.

Take at least one pair in the **VPE** composite as well as the VPP composite, at the same pot
setting. That pair tests D-B directly: if it is one net with two setpoints, the same divider ratio
falls out of both, and a single calibration covers both rails. If the two ratios disagree, D-B is
wrong and the routing contributes — say so and stop rather than averaging them.

**Stage 3 — resistance corroboration.** Power off, USB disconnected. Measure A2→GND, VPE-net→A2,
VPE-net→GND. **An in-circuit reading is a lower bound** — parallel paths only lower it — so treat
these as corroboration, not proof. The discriminator is sharp: `44k∥270k = 37.83 kΩ` versus
`47k∥270k = 40.05 kΩ`, ~2.2 kΩ apart and well inside meter resolution.

**Stage 4 — repeat on the second board/shield.** This is the step that separates shield-wide from
per-chip. Without it the session cannot answer the question it exists to answer.

Write `BENCH-RECORD.md` in the spec folder with a fenced `## Measured figures` block of bare
integers, following the `199-BENCH-RECORD.md` convention: later tasks parse integers from that block
and never re-transcribe them from prose. Record every operator statement verbatim and labelled as
an operator statement, not a measurement. Record non-measurements as non-measurements.

---

## Task 5: Apply the fix the measurement selects

Conditional on Task 4. Only the firmware-only arm is specified here; a calibration arm becomes a
follow-up spec.

**If the divider term is confirmed wrong:** correct `VALUE_R1` / `VALUE_R2` in
[rurp_shield.h:47-48](firestarter_fw/include/rurp_shield.h#L47-L48) to the measured values, and
**bump `CONFIG_VERSION` to `VER07`**. The bump resets `r1`/`r2` on every board via
[rurp_config_utils.cpp:35-43](firestarter_fw/src/rurp_config_utils.cpp#L35-L43) — accepted per D-G,
and it resolves the pending stranding todo
(`.planning/todos/pending/config-version-not-bumped-strands-stale-eeprom-calibration.md`), which has
been live since Phase 44. Keep `k` inside the uint32 guards (`R1+R2 ≤ 3900000`, `k ≤ 4194303`); the
native suite from Task 2 proves it.

**If the bandgap term dominates:** do not fold it into `r2`. That is the hand-tuned-`r1` hack the
seed exists to retire, and it leaves the VCC report wrong. Record the measured `V_bg` per board in
the bench record and hand it to the follow-up spec.

Re-report flash and RAM. Re-run both native environments.

---

## Task 6: Retune the guard window

After Task 5, not before (D-C).

The window lives twice, byte-for-byte identical, at
[eprom.cpp:545-555](firestarter_fw/src/proms/eprom.cpp#L545-L555) and
[flash_intel.cpp:37-46](firestarter_fw/src/proms/flash_intel.cpp#L37-L46). Derive the new bounds
from the **measured residual uncertainty** after the Task 5 fix — not from a guess, and not from the
current ±5 %/+500 mV, which predates any knowledge of the instrument error.

Two properties to preserve deliberately, or change deliberately and say so:

- The asymmetry is by design: HIGH is a hard `MSG_ERR_VPP_HIGH` unless `FLAG_FORCE`; LOW is only
  `MSG_WARN_VPP_LOW`. `FLAG_FORCE` is never set in this project, so HIGH stops the write.
- `RURP_VPP_DROP_PATH_MAX_DELIVERABLE_MV` (17380) is a **route-selection ceiling, never compared
  against an ADC reading** (v1.40 D-22/D-23: an ADC-triggered version would have silently missed
  nine of the ten rows the phase existed to rescue). **Keep routing ADC-independent.** This task
  improves the verification leg only.

Close v1.40 RAIL-03 with the reasoning, or record precisely why it still cannot close.

Tests per `testing/non-vacuity`: a violating input on each side, both boundaries, and a case that
proves the instrument is not inert.

---

## Task 7: Disposition and follow-up

- Update backlog **999.38** with the decomposition, or close it if the mechanism is now determined.
- Update the seed and D1–D7 notes: D1's "discover the model" hedge is retired by evidence 2
  (gain-only, D-E). Say which of the seed's two stages the measurement shows is actually needed.
- Update `agent-os/product/roadmap.md`: the "VPP ADC reads about +7.5 % high" deferred item.
- If Task 5 changed the ADC band constants or any figure the wiki repeats, update
  `firestarter.wiki/Shield-Revisions.md` in the same change — nothing checks this automatically.
- **PY32F071, recorded not built:** `rurp_read_vcc_mv` uses nominal 1200 mV VREFINT
  ([py32f071_rurp_shield.cpp:278-290](firestarter_fw/platform/py32f071/src/py32f071_rurp_shield.cpp#L278-L290))
  and ignores any factory calibration word. The SDK is fetched at build time and not vendored, so
  **whether PY32F071 exposes one is unverified.** If it does, that is the firmware-only absolute
  fix that AVR cannot have. File it against the PY32 PCB work.

---

## Standards that apply

| Standard | Why |
|---|---|
| `testing/no-source-introspection` | `test_voltage_reformulation_oracle.py` is the only thing proving the shipped formula, and it is a source scan. Task 2 replaces it with native tests and deletes it. |
| `testing/native-firmware-tests` | The new suite registers in **both** `platformio.ini` lists and runs in both native environments. |
| `testing/non-vacuity` | Violating input, boundaries and an absent-evidence case for the guard window and the conversion math. |
| `firmware/size-reporting` | Flash **and** RAM for `leonardo` stable, `leonardo` `DEV_TOOLS=1`, and `uno`, on every firmware change. |
| `firmware/fail-closed-refusals` | The `return 0` on implausible calibration is fail-open today. |
| `firmware/timing` | Settling delays carry a cited datasheet figure. |
| `protocol/message-catalog` | New message IDs come from `messages.toml` in the meta repo, via codegen. Never hand-edit `messages.h`/`messages.py`. |
| `protocol/duplicated-constants` | A new command ordinal moves in `firestarter.h` and `constants.py` together. |
| `protocol/rollout-compatibility` | Firmware ships before the host that depends on it. No widening of a fixed-length DATA frame. |
| `host/help-docstrings` | Any new host command's docstring is user-facing `--help` text. |
| `host/echo-vs-logger` | `click.echo` for operator facts at default verbosity. |

## Verification

1. **Native, no hardware.** `pio test -e native` and `pio test -e native_nodevtools` both green,
   with the new conversion suite counted in both. Confirm the retired Python oracle is gone and its
   cases live in the native suite.
2. **Build.** `pio run -e leonardo`, `PLATFORMIO_BUILD_FLAGS="-D DEV_TOOLS=1" pio run -e leonardo`,
   `pio run -e uno`. Record RAM and flash, before and after. Leonardo must stay under 28672 B.
3. **Host.** `pytest` with the coverage floor, `ruff check` and `ruff format --check`, mypy on the
   listed modules. Snapshots updated deliberately, not blindly.
4. **Codegen parity.** Run `codegen.py` in the meta repo and confirm both generated files are
   byte-clean and ruff-clean; do not hand-edit either.
5. **On hardware, the acceptance test.** With a meter on the probe point at a pot setting the
   operator chooses, `firestarter vpp` agrees with the meter to within the residual stated in the
   bench record. Before the fix this disagrees by ~8 %. Run it on **both** boards.
6. **The regression that motivated the work.** A 12.0 V rail, set by meter, no longer trips
   `MSG_ERR_VPP_HIGH` on a write. This is the A3/B2 failure, reproduced and cleared.
7. **Integers match their source.** Every figure that reaches `rurp_shield.h` or a guard constant is
   read from `BENCH-RECORD.md`'s fenced block, and a verify leg asserts equality rather than
   trusting a transcription.
