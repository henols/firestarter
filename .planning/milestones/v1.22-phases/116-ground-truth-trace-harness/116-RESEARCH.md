# Phase 116: GROUND TRUTH + TRACE HARNESS — Research

**Researched:** 2026-07-27
**Domain:** Native (host-side) Unity bus-trace harness for AVR firmware; PlatformIO `[env:native]`; protocol `0x0D` SDP emitter ground truth
**Confidence:** HIGH — every load-bearing claim below was produced by **compiling and running code in this session** against the actual tree, not inferred

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** The RED `0x0D` SDP trace suite is **parked out of `platformio.ini`'s `test_filter`
  allowlist** with a named `TODO(v1.22 Phase 117)`. `pio test -e native` stays green throughout
  Phase 116, so GATE-03 keeps meaning something. **Phase 117's one-line addition of that suite to
  the allowlist IS the RED→GREEN proof.** Rejected: adding it to the allowlist and accepting a red
  native suite for the rest of the milestone (a real regression during 117 would hide inside
  expected noise); rejected: `TEST_IGNORE_MESSAGE` markers (IGNORED does not demonstrate RED, so it
  adds ceremony without adding evidence).

- **D-02:** The RED evidence is pinned as a **committed fixture in the firmware sub-repo** —
  `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md` — carrying the verbatim
  expected-vs-actual divergence. It lives next to the code it describes, survives `.planning/`
  archival, and lets a Phase-117 reviewer diff the recorded actual stream against the fixed one
  without checking out an old tree. (A `.planning/`-only transcript was rejected as too easily
  orphaned from the code.)

- **D-03:** TRACE-01's recording extension gets its **own permanently-GREEN suite**, separate from
  the RED `0x0D` suite, and **enters `test_filter` immediately**. The recorder is a capability with
  no dependency on the fix, so it can be green on day one: it proves ordered capture correctly
  interleaves register writes, data bytes and CE/OE edges, and that flag-off behaviour is
  byte-identical to today. This keeps GATE-03 covering the harness while the `0x0D` suite is parked.

- **D-04:** The four planted-fault negatives are **committed and permanently re-runnable, injected
  in-TU** — never by mutating production source (which this phase may not touch):
  - unlock-table-mutated-to-`0x10` and lock-table-swapped-for-write-prefix become **test-local
    `byte_flip_t` copies** fed through the same emitter and asserted to produce a *different*
    stream. These live in the always-green harness suite (D-03).
  - the `LOG_`-inside-the-timing-window negative needs a **source-scan checker plus a planted
    fixture source file** — the v1.21 SAFE-03 / `FIRESTARTER_DEVTEST_SRC` env-override shape.
  - `protocol != 0x0D` reaching `configure_not_implemented()`/`0xBB` is a **plain positive test**
    (existing `test_not_implemented` pattern).

  Rejected: a one-time local mutation with a recorded transcript (the proof becomes a screenshot;
  nothing stops a later refactor re-hollowing the harness). Rejected: a `tools/` script that
  patches/runs/reverts tracked source (new and risky pattern; leaves a dirty tree on abort).

- **D-05:** The recorder gets its elision behaviour by **`#include`ing the real
  `firestarter/include/rurp_register_utils.h`** under the new opt-in flag — *not* by replicating
  production's cache-compare. Zero drift by construction: the elision IS production's.
  (Two consequences accepted: recording hooks move down to `rurp_write_data_buffer` /
  `rurp_set_control_pin` so the stream is latch-strobe-shaped; and the real cache-backed
  `rurp_read_from_register` replaces the return-0 stub, but **only inside new-flag suites** — the
  six existing `HOST_STUBS_RECORD_BUS` suites must keep today's exact behaviour.)
  Rejected: a hand-replica of the cache-compare (the v1.18 WR-01 approach).

- **D-06:** The expected stream is a **literal tuple array** per case — a static array of
  `{kind, reg-or-pin, value}` entries, compared element-by-element with a
  `TEST_ASSERT_..._MESSAGE` that **names the diverging index**. Matches how
  `test_val_5v_page.cpp` already asserts, keeps everything inside Unity, and makes Phase 117's
  diff a readable change to data rather than to a blob. Rejected: a golden text-trace string.
  A failure-time text renderer is permitted but optional.

- **D-07:** Edge recording is **scoped to what `0x0D` actually touches** — `rurp_write_data_buffer`
  bytes plus the `chip_enable`/`chip_disable` and `chip_input`/`chip_output` transitions the
  `eeprom_28c` + `flash_utils` paths call, enough to pin `(LSB, MSB, data, CE-pulse)` per TRACE-02
  and no more. Rejected: recording every side-effecting `rurp_*` call.

- **D-08:** The four pinouts' `bus_config_t` values are **generated from the host's own
  derivation** — a generator imports `firestarter_app`'s real `database.py` /
  `convert_to_programmer` path and emits a committed header of `bus_config_t` literals.
  Precedent: `gen_validation_header.py` → `_shared/validation_matrix.h`.
  Rejected: hand-coded literals with a derivation comment.

- **D-09:** Coverage is **one representative per pinout, plus at least one extra
  `DIP32_28C512_EEPROM` size band.** The four pinouts are `DIP28_28C256`, `DIP28_28C64`,
  `DIP24_2816`, `DIP32_28C512_EEPROM`. Rejected: all 84 rows table-driven; rejected: exactly 4.

- **D-10:** The generated header is **committed with a `DO NOT EDIT` banner and a CI drift gate**
  that regenerates and diffs.

- **D-11:** **The generator runs host-side; the drift gate is host-side.** The generator lives in
  `firestarter_app/tools/`, emits the header, and the header is **committed under
  `firestarter/test/native/avr/_shared/`**. The drift gate is a `firestarter_app` pytest that
  regenerates and diffs against the firmware repo's committed copy, **skipping cleanly when the
  firmware submodule is absent** (`FW_ABSENT` skipif shape).

- **D-12:** `test_eeprom28c_chip_id` is **migrated and split**, and the old directory retired:
  - `mismatching_chip_id_errors`, `zero_chip_id_skips_check`,
    `mismatching_chip_id_with_force_warns` move onto the **address-keyed** mock and into the
    **always-green** suite (D-03). *(See ⚠ CORRECTION 2 — one of these three cannot be
    always-green.)*
  - `test_eeprom28c_matching_chip_id_proceeds` moves into the **RED-parked** suite (D-01).
    **That failure IS TRACE-06's INIT-abort evidence** — TRACE-04 and TRACE-06 share one mechanism.
  - The `s_mock_bytes[2] = 0x20; /* satisfies eeprom28c_wait_for_write(0x5555, 0x20) */` fixture at
    `test_eeprom28c_chip_id.cpp:104` must not survive in that form anywhere.

- **D-13:** The **Unity-teardown SIGABRT flake debt stays deferred.** Phase 116 reaches into
  `test_eeprom28c_chip_id` **only** to the extent D-12's migration requires.

- **D-14:** TRACE-06 produces `116-PREMISE.md` **and Phase 116 applies the PROJECT.md correction
  itself** — a third ⚠ correction block, in this phase, not deferred to the Phase-122 close.

### Claude's Discretion

- **Suite/directory naming** for the new RED `0x0D` suite and the always-green harness suite.
  (The D-02 fixture path assumes `test_eeprom28c_sdp/`, illustrative not binding.)
- **Whether to add a failure-time text renderer** on top of D-06's tuple-array assert, for
  diagnostic messages only. Permitted; the tuple array remains the single source of truth and any
  renderer needs its own test.
- **The exact `{kind, reg-or-pin, value}` entry layout**, the new opt-in flag's name, and the
  recording-buffer capacity (today `HOST_STUBS_MAX_RECORDING 256` — check the SDP sequence fits
  with headroom).
- **TRACE-05's exact home and form** — which test file, and whether it asserts the literal count
  `84` or derives it.
- **Representative chip selection** within D-09's bands, and how many extra DIP32 bands beyond the
  required one.

### Deferred Ideas (OUT OF SCOPE)

- **Unity-teardown SIGABRT root cause** (D-13) — re-enabling `test_eeprom28c_chip_id` and
  `test_flash_intel_vpp` in `test_filter`. Pre-existing debt since Phase 17 WR-01 / Phase 20.
- **Recording every side-effecting `rurp_*` call** (rejected half of D-07) — revisit if 118/119
  find the scoped recorder insufficient.
- **All-84-chips table-driven trace coverage** (rejected half of D-09).
- **`PAGE_SIZE 64` hard-coded at `eeprom_28c.cpp:19`** while AT28C010's page is 128 B and
  AT28C040's is 256 B (18 chips affected). Explicit deferral, not silence.
- **`DIP24_2816` has no `static-high-pins` key** — tracked as **SDP-F8**. The Phase-116 trace for
  that pinout will make it visible in the recorded stream — record what is observed, do not act.
- **Datasheet verification of SDP magic addresses for AT28C040 / AT28C16 / AT28C04** — SDP-F7.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **TRACE-01** | Native register-trace recording captures data bytes and `/CE`//`/OE` edges in the **same ordered stream** as register writes, behind a new opt-in flag so every existing suite stays byte-exact | **De-risked empirically.** §Architecture Patterns gives a compiling recorder design; the single `rurp_set_control_pin(pin, state)` seam already carries LSB/MSB/CTRL latch strobes **and** CE/OE on one distinguishable pin namespace (§F3). Byte-exactness half **proven**: 80/80 existing tests green with the extension compiled in and not opted into (§F7). ⚠ CORRECTION 1: the naive D-05 include does **not** compile — 6 redefinition errors; the guard set is given in §Code Examples. |
| **TRACE-02** | A `0x0D` SDP trace suite pins the exact ordered `(LSB, MSB, data, CE-pulse)` stream `eeprom28c_write_init` emits for **each of the four `0x0D` pinouts**, and is **RED against today's tree** | **Ground truth derived, per pinout, by execution** — §F4 gives the full 54-entry shipped stream, the remap-aware target stream, and the exact divergence per pinout. ⚠ CORRECTION 3: on `DIP32_28C512_EEPROM` the address bytes are **identical** shipped-vs-fixed; RED on that pinout rests on the OE-edge ordering and requires a stale-upper-address case (§F5). |
| **TRACE-03** | First-class negative traces go RED — unlock table mutated to `0x10`, lock table swapped for write prefix, planted `LOG_` in the timing window, `protocol != 0x0D` → `0xBB` | §Don't Hand-Roll + §Code Examples. `flash_util_byte_flipping` is externally linked so test-local `byte_flip_t` copies work; `EEPROM_SDP_DISABLE` itself is **not** linkable (§F6) which forces the local-copy shape D-04 already chose. `FIRESTARTER_DEVTEST_SRC` env-seam precedent located at `check_devtest_orchestrator.py:86`. |
| **TRACE-04** | Call-ordered scripted mock replaced by an **address-keyed** `mock_get_data`, retiring the `:104` fixture | **Migration matrix executed** (§F8). ⚠ CORRECTION 2: **two** tests go RED under an address-keyed mock, not one — `mismatching_chip_id_with_force_warns` also goes RED because the inverted check's `RESPONSE_CODE_ERROR` clobbers the FORCE `WARNING`. `zero_chip_id_skips_check` needs its call-ordered `s_mock_byte_idx == 1` assertion re-expressed. Three `0x20` fixture sites, not one: `:104`, `:140`, `:160`. |
| **TRACE-05** | DB-invariant host test pins `chip_id_check: false` across all **84** `algorithm == 13` entries | **Verified exactly** (§F9): 84 entries, `chip_id_check: false` ×84, `chip_id_value: "0x00000000"` ×84. Access path and precedents given. |
| **TRACE-06** | Written premise-verification artifact settling whether `write at28c256` aborts at INIT on `3.0.0b11` | **SETTLED IN THIS SESSION** (§F1): `eeprom28c_write_init` returns `RESPONSE_CODE_ERROR` on **all five** representative handles. The prediction is CONFIRMED at the software layer. Exact honesty wording for `116-PREMISE.md` given in §F1. |
</phase_requirements>

---

## Summary

This phase is unusually well-served by research because the oracle it builds is **runnable today**.
Rather than reason about the harness, I built it: patched `host_stubs_common.inc` behind a new
opt-in flag, included the real `rurp_register_utils.h` per D-05, constructed real `bus_config_t`
values for all four `0x0D` pinouts from the host's own `convert_to_programmer`, and executed
`flash_util_byte_flipping`, `memory_set_data` and `eeprom28c_write_init` under
`pio test -e native`. Every number in this document came out of that run. The probe was then
fully reverted; `git status` in the firmware sub-repo is clean.

Three results dominate planning. **First, TRACE-06 is already settled**: `eeprom28c_write_init`
returns `RESPONSE_CODE_ERROR` for every one of the four pinouts, so `firestarter write at28c256`
does abort at INIT — the milestone's highest-value PREDICTED claim is confirmed, and Phase 116's
job on TRACE-06 collapses from investigation to careful, ceiling-respecting *documentation*.
**Second, the harness design is sound but D-05 as written does not compile** — the real header
pulls in `rurp_hw_rev_utils.h` under the inherited `-D HARDWARE_REVISION` and collides with six
stubs in the same translation unit. The fix is a five-line guard set, given verbatim below, and
with it the extension compiles, links, and leaves all 80 existing native assertions green — which
is TRACE-01's byte-exactness success criterion, already demonstrated. **Third, and most
consequential for the plan, TRACE-02's "RED for each of the four pinouts" is not uniformly
achievable on the emitted-address axis**: on `DIP32_28C512_EEPROM` (18 of the 84 chips) the shipped
emitter and the remap-aware emitter produce byte-identical address latches, because that pinout's
`rw` line lands in the CONTROL register which `fu_flash_fast_address` never writes at all. RED on
that pinout survives only via the `/OE`-edge ordering and, properly, via a deliberate
stale-upper-address case — which is exactly the band-distinguishing DIP32 case D-09 already asks
for, now with a mechanical reason rather than a hunch.

A fourth result corrects the milestone framing itself: the claim in `REQUIREMENTS.md` and
`SUMMARY.md` finding 1 that "at least one command write is emitted with `/WE` HIGH on **all 84**
`0x0D` chips" is **false for 18 of them**. The inhibit affects 66 chips (`DIP28_28C64` ×35,
`DIP24_2816` ×19, `DIP28_28C256` ×12) at 4/6, 2/6 and 4/6 writes respectively; the 18
`DIP32_28C512_EEPROM` chips are inhibit-free at INIT-time register state. That correction belongs
in `116-PREMISE.md` alongside the INIT-abort finding, and it makes the Phase-117 requirement
FIX-01's "all four pinouts" wording something the planner should read carefully.

**Primary recommendation:** Plan Wave 1 as the recorder + always-green suite (TRACE-01, TRACE-03's
three in-suite negatives, TRACE-04's migration) using the exact guard set in §Code Examples;
plan Wave 2 as the parked RED suite (TRACE-02) with **five** cases — one per pinout plus the
DIP32 stale-upper-address band case — and treat the DIP32 divergence axis as an explicit,
documented design decision rather than an emergent property. Run TRACE-05 and TRACE-06 in parallel
with Wave 1; both are already fully determined by the findings below.

---

## ⚠ Corrections to Upstream Documents

These four items contradict `CONTEXT.md`, `REQUIREMENTS.md` or `SUMMARY.md`. All were established
by executing code in this session. **The planner must reconcile each before writing tasks.**

### CORRECTION 1 — D-05's "Viability confirmed" is incomplete; the include does not compile
**Status:** `[VERIFIED: compiled in this session]`

`CONTEXT.md` D-05 states the `rurp_register_utils.h` include is viable because the header is
"included only by `src/boards/*.cpp`, which `[env:native]`'s `src_filter = +<proms/>` excludes — so
there is no duplicate-definition conflict." The *link-time* reasoning is correct. The
**compile-time** reasoning is missing: the conflict is **intra-TU**, not inter-TU.

`rurp_register_utils.h:8-10` includes `rurp_hw_rev_utils.h` when `HARDWARE_REVISION` is defined, and
`[env:native]` inherits `-D HARDWARE_REVISION` from `[env]`'s `build_flags`. `rurp_hw_rev_utils.h`
is also a header-with-definitions. Adding the include to a `host_stubs.cpp` that already includes
`host_stubs_common.inc` produces **six redefinition errors**:

| Symbol | Real header | Stub in `.inc` |
|---|---|---|
| `rurp_map_ctrl_reg_for_hardware_revision` | `rurp_hw_rev_utils.h:15` | `:138` |
| `rurp_get_physical_hardware_revision` | `rurp_hw_rev_utils.h:43` | `:134` |
| `rurp_detect_hardware_revision` | `rurp_hw_rev_utils.h:61` | `:126` |
| `rurp_get_hardware_revision` | `rurp_hw_rev_utils.h:100` | `:129` |
| `rurp_write_to_register` | `rurp_register_utils.h:24` | `:69` |
| `rurp_read_from_register` | `rurp_register_utils.h:91` | `:82` |

**Resolution:** D-05's *decision* stands unchanged — the fix is additive guards in
`host_stubs_common.inc`, not a different approach. The exact guard set is in §Code Examples and was
verified to compile, link and run. Linking is fine: `rurp_log_id_u8` (reached via
`rurp_hw_rev_utils.h`'s `LOG_WARN_ID_U8`) is provided by `src/boards/rurp_serial_utils.cpp`, which
**is** in `build_src_filter`.

**Second, unnamed D-05 consequence:** the real header's `rurp_internal_write_to_register:86` calls
`delayMicroseconds(1)`, and the `:58` settle path calls `delayMicroseconds(4)`. **ArduinoFake
aborts (SIGABRT) on an unmocked call**, so every new-flag suite MUST add
`When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();` in `setUp()`. This is not in
CONTEXT.md's "two consequences, accepted" list. It cost one debug cycle in this session and will
present as a bare `SIGABRT` — easily misread as the D-13 Unity-teardown flake.

**Third, unnamed D-05 consequence:** the real `rurp_read_from_register` returns the **real cached
value**, and `rurp_register_utils.h:12-14` initialises the cache to `0xff/0xff/0xff`.
`mem_util_calculate_top_address_register` ORs `rurp_read_from_register(CONTROL_REGISTER) & (A9 |
VPE | P1 | REG_ENABLE)` into every address write — so with the power-on `0xff` cache, the first
CONTROL write carries **`0x8E`**, which has `CTRL_VPP_REGULATOR_ENABLE (0x80)` set. The old return-0
stub silently suppressed this. A new-flag suite that does not deliberately reset the cache will
(a) compute wrong CONTROL expectations and (b) *appear* to show the 5V-only `0x0D` path enabling the
VPP regulator. **The cache is a mutable non-static global** (`lsb_address`, `msb_address`,
`control_register`) that persists across Unity test cases in the same binary, so a reset seam is
mandatory, not optional. See §Runtime State Inventory and §Pitfall 1.

### CORRECTION 2 — D-12 mis-assigns one test: **two** tests go RED, not one
**Status:** `[VERIFIED: executed in this session]`

D-12 routes `mismatching_chip_id_with_force_warns` into the **always-green** suite. It cannot go
there. Driving `eeprom28c_write_init` with an address-keyed mock produces:

| Test | Assertion | Result under address-keyed mock | D-12 says | Reality |
|---|---|---|---|---|
| `matching_chip_id_proceeds` | `NOT_EQUAL(ERROR)` | `ERROR` | RED-parked | ✅ **RED** — agrees |
| `mismatching_chip_id_errors` | `EQUAL(ERROR)` | `ERROR` | always-green | ✅ **green** — agrees |
| `zero_chip_id_skips_check` | `s_mock_byte_idx == 1` | assertion vehicle no longer exists | always-green | ⚠ **green only if re-expressed** |
| `mismatching_chip_id_with_force_warns` | `EQUAL(WARNING)` | **`ERROR`** | always-green | ❌ **RED** |

**Mechanism:** `eeprom28c_check_chip_id` sets `RESPONSE_CODE_WARNING` under `FLAG_FORCE`
(`eeprom_28c.cpp:88`), then `eeprom28c_write_init` continues — the SDP wait is **unconditional**,
there is no flag to skip it — and `eeprom28c_wait_for_write` overwrites
`handle->response_code = RESPONSE_CODE_ERROR` at `:153`. Final state is `ERROR`, not `WARNING`.

**Why this matters beyond bookkeeping:** the force-warning case is precisely the one
`.planning/` memory `reference_golden_trace_misses_severity_fork` says must be preserved — the
v1.16 Phase-89 CR-01 regression was an ERROR→WARNING slip that byte-identical goldens missed. If it
is filed as always-green it will be "fixed" by weakening the assertion, which re-opens exactly that
hole. **Recommendation:** move it into the **RED-parked** suite alongside `matching_chip_id_proceeds`
and note in `RED-BASELINE.md` that its RED-ness is *second-order evidence of the inverted check* —
the check does not merely fail, it **destroys severity information**. That is a stronger finding
than D-12 anticipated and it is free.

**`zero_chip_id_skips_check` re-expression (verified green):** replace the call-ordered
`s_mock_byte_idx == 1` with a per-address read counter and assert `reads_at_mfr_addr == 0`. Measured
under an address-keyed mock: `mfr=0, @0x5555=2000, total=2000` — the intent ("the chip-id helper was
not called") is preserved and is now independent of the SDP outcome.

### CORRECTION 3 — TRACE-02's "RED for each of the four pinouts" needs a per-pinout divergence axis
**Status:** `[VERIFIED: executed in this session]` — see §F4/§F5 for the raw streams

On `DIP32_28C512_EEPROM` the shipped and remap-aware emitters produce **byte-identical LSB/MSB/data
values**. `mem_util_remap_address_bus` returns `0x5555` unchanged for that pinout
(`address_mask == 0xFFFF`, and the `rw_line`-20 bit is `WRITE_FLAG == 0`), so there is no address
correction to observe. The only residual ordered-stream divergence is the `/OE` edge position
(§F5), and that is a weak, incidental hook: a Phase-117 emitter that happened to preserve the OE
ordering would leave the DIP32 case GREEN with nothing proven.

**Root cause:** `DIP32_28C512_EEPROM`'s `rw-pin` resolves to bus line **20**, and
`mem_util_calculate_top_address_register` maps address bit 20 → CONTROL bit `0x10`
(`CTRL_ADDRESS_LINE_17`). `fu_flash_fast_address` writes **only LSB and MSB** — it never writes
CONTROL — so on this pinout the `/WE` state is simply *whatever the previous operation left*. At
INIT-time that is `0`, i.e. write-enabled, i.e. **accidentally correct**.

**Resolution — this strengthens D-09 rather than threatening it.** The DIP32 case must be a
**deliberate stale-upper-address case**: pre-seed the register cache so CONTROL bits `0x10`
(`A17`) and/or `0x20` (`A18`) are HIGH, simulating a preceding high-address operation. Then:
- **shipped:** CONTROL untouched → bits stay high → bus line 20 HIGH → `/WE` inhibited **and** the
  chip's `A17`/`A18` are wrong → sequence not recognised.
- **fixed:** `mem_util_set_address` writes CONTROL with
  `(0x5555 >> 16) & 0x71 == 0` plus only the VPP-mask bits → `0x10`/`0x20` **cleared** → `/WE`
  asserted and upper address correct.

That is a large, unambiguous divergence, it is the FIX-03 requirement made visible, and it is the
band-distinguishing trace D-09 requires. **Plan the DIP32 case this way explicitly**; do not let it
emerge.

*(Adjacent, out of scope, worth recording: `DIP32_28C512_EEPROM` declares only 16 address-bus pins,
so `address_mask == 0xFFFF` for `AT28C010` (128 KB) and `AT28C040` (512 KB) alike — those parts
cannot address beyond 64 KB through the remap at all. Pre-existing, not a v1.22 requirement, but it
means "A16–A18 staleness" after the fix resolves to "A16–A18 forced to 0", which is a fix for
staleness and simultaneously a ceiling on addressable range.)*

### CORRECTION 4 — "all 84 `0x0D` chips" is wrong; it is 66 of 84
**Status:** `[VERIFIED: executed in this session]`

`REQUIREMENTS.md` §Framing and `SUMMARY.md` finding 1 both state: *"At least one command write is
emitted with `/WE` HIGH — a documented Write Inhibit — on all 84 `0x0D` chips."* Measured:

| Pinout | Chips | `rw` bus line | Register domain | Writes inhibited (of 6) |
|---|---|---|---|---|
| `DIP28_28C64` | 35 | 14 | MSB bit 6 | **4** (the four `0x5555` loads) |
| `DIP24_2816` | 19 | 11 | MSB bit 3 | **2** (the two `0x2AAA` loads) |
| `DIP28_28C256` | 12 | 14 | MSB bit 6 | **4** (the four `0x5555` loads) |
| `DIP32_28C512_EEPROM` | 18 | 20 | CONTROL bit `0x10` | **0** at INIT-time state |
| **total** | **84** | | | **66 chips affected** |

Note also that `DIP24_2816` is inhibited on the *opposite* writes from the DIP28 pinouts — the
`0x2AAA` loads, not the `0x5555` loads — because `0x2A` has bit 3 set while `0x55` does not. Any
prose that says "the `0x5555` writes are inhibited" is wrong for 19 chips.

`116-PREMISE.md` (D-14) should carry this correction; the PROJECT.md ⚠ block should say
*66 of 84*, per-pinout, not *all 84*.

---

## Findings (all produced by execution in this session)

### F1 — TRACE-06 is SETTLED: `eeprom28c_write_init` aborts at INIT on every pinout
`[VERIFIED: pio test -e native, this session]`

```
=== TRACE-06: response_code after eeprom28c_write_init (ERROR=0 OK=1)
    DIP28_28C256 (AT28C256 32K)    response_code=0 <== INIT ABORTED   strobes=6057
    DIP28_28C64  (AT28C64  8K)     response_code=0 <== INIT ABORTED   strobes=6054
    DIP24_2816   (AT28C16  2K)     response_code=0 <== INIT ABORTED   strobes=6057
    DIP32_28C512 (AT28C010 128K)   response_code=0 <== INIT ABORTED   strobes=6057
    DIP32_28C512 (AT28C040 512K)   response_code=0 <== INIT ABORTED   strobes=6057
```

Mechanism, fully traced: `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` polls 2000 times
(`eeprom_28c.cpp:131`), never observes `0x20`, emits `MSG_ERR_EEPROM_TIMEOUT` and sets
`RESPONSE_CODE_ERROR` (`:151-153`); `eeprom28c_write_init:111-113` returns early, so the blank
check never runs and no data byte is ever sent.

**Honesty ceiling — the exact claim `116-PREMISE.md` may make.** This is a **software-layer**
proof: it shows the code path aborts whenever `firestarter_get_data(0x5555)` does not return
`0x20`. It is **not** silicon evidence. The bridge to "aborts on a real AT28C256" is the datasheet
statement that command-sequence data *"is not written to the device"*
`[CITED: Microchip DS20006432B §6.6.2 p.10; DS20006386B p.10 — via .planning/research/SUMMARY.md]`,
which makes `0x20` at `0x5555` unreachable on a part that recognised the sequence, and `0xFF` the
expected read on a virgin part either way. Permitted wording:

> On `3.0.0b11`, `eeprom28c_write_init` aborts with `MSG_ERR_EEPROM_TIMEOUT` →
> `RESPONSE_CODE_ERROR` before any data byte is transferred, for all four `0x0D` pinouts. Verified
> by native trace (`pio test -e native`) driving the real `configure_memory` →
> `firestarter_operation_init` path with host-derived `bus_config_t` values. The abort is
> unconditional for any `get_data(0x5555) != 0x20`; per DS20006432B §6.6.2 a part that recognised
> the sequence cannot return `0x20` there. **No AT28C part was on the bench; this is not a
> silicon-state claim.**

Forbidden wording: anything asserting what the silicon did, or that gh#11/gh#12 are *fixed*.

**Corollary the milestone should absorb:** because the abort is unconditional, the
backward-compatibility objection to auto-unlock policy option (d) is void — there is no working
`write` behaviour on this family to preserve. `REQUIREMENTS.md` already anticipates this; Phase 116
now supplies the proof.

### F2 — Baseline is green: 14 suites, 80 assertions
`[VERIFIED: pio test -e native, this session]`

All 14 `test_filter` suites pass; **80 test cases, 0 failures, ~40 s** cold / ~24 s warm.
`test_eeprom28c_chip_id` and `test_flash_intel_vpp` are parked (D-13 debt) and are **not** in the
count. This is the GATE-03 baseline Phase 116 must preserve.

Six suites currently define `HOST_STUBS_RECORD_BUS`: `test_val_eprom`, `test_val_eeprom28c`,
`test_val_nor_unlock`, `test_val_5v_page`, `test_val_flash_intel`, `test_val_sram`. Eight do not.
CONTEXT.md's list of six is correct.

### F3 — The recording seam is cleaner than expected: one hook covers latches **and** CE/OE
`[VERIFIED: rurp_shield.h:53-57, 104-111 + executed]`

`rurp_shield.h` puts latch strobes and chip-control pins in **one `uint8_t` namespace**:

| Constant | Value | Role |
|---|---|---|
| `LEAST_SIGNIFICANT_BYTE` | `0x01` | LSB latch enable |
| `MOST_SIGNIFICANT_BYTE` | `0x02` | MSB latch enable |
| `OUTPUT_ENABLE` | `0x04` | chip `/OE` |
| `CONTROL_REGISTER` | `0x08` | CONTROL latch enable |
| `CHIP_ENABLE` | `0x20` | chip `/CE` |

`rurp_chip_enable()` → `rurp_set_control_pin(CHIP_ENABLE, 0)`;
`rurp_internal_write_to_register(reg, data)` → `rurp_write_data_buffer(data)` then
`rurp_set_control_pin(reg, 1)` then `rurp_set_control_pin(reg, 0)`.

**Consequence:** hooking exactly **two** functions — `rurp_write_data_buffer` and
`rurp_set_control_pin` — yields the complete ordered stream D-07 asks for, with latch strobes and
CE/OE distinguishable by the `pin` field. No third hook, no kind taxonomy beyond `{DATA, PIN}`.
This makes D-07's scoping decision essentially free rather than a compromise.

**Recommended entry layout (resolves a Claude's-Discretion item):**
```c
enum { STROBE_KIND_DATA = 1, STROBE_KIND_PIN = 2 };
struct strobe_entry_t { uint8_t kind; uint8_t pin; uint8_t value; };
```
`kind == DATA` → `value` is the data-buffer byte, `pin` unused (0).
`kind == PIN` → `pin` is one of the five constants above, `value` is the level (0/1).
**Recommended flag name:** `HOST_STUBS_REAL_REGISTER_UTILS` — it names the *mechanism* (D-05's
include) rather than the *output*, which is the thing a future editor must not break. (Alternative
`HOST_STUBS_RECORD_STROBES` reads better next to `HOST_STUBS_RECORD_BUS`; either is fine, but the
guards it must gate are the six symbols in CORRECTION 1, so the name should hint at "real header".)

### F4 — The shipped SDP stream, per pinout, byte-exact
`[VERIFIED: executed]`

Full ordered stream for the shipped `flash_execute_command(EEPROM_SDP_DISABLE)` path on
`DIP28_28C256`, **54 entries**, elision applied:

```
[ 0] DATA 0x55   [ 1] PIN LSB_LE->1  [ 2] PIN LSB_LE->0     <- write#1  addr 0x5555
[ 3] DATA 0x55   [ 4] PIN MSB_LE->1  [ 5] PIN MSB_LE->0
[ 6] DATA 0xAA   [ 7] PIN OE->1      [ 8] PIN CE->0   [ 9] PIN CE->1
[10] DATA 0xAA   [11] PIN LSB_LE->1  [12] PIN LSB_LE->0     <- write#2  addr 0x2AAA
[13] DATA 0x2A   [14] PIN MSB_LE->1  [15] PIN MSB_LE->0
[16] DATA 0x55   [17] PIN OE->1      [18] PIN CE->0   [19] PIN CE->1
[20] DATA 0x55   [21] PIN LSB_LE->1  [22] PIN LSB_LE->0     <- write#3  addr 0x5555
[23] DATA 0x55   [24] PIN MSB_LE->1  [25] PIN MSB_LE->0
[26] DATA 0x80   [27] PIN OE->1      [28] PIN CE->0   [29] PIN CE->1
[30] DATA 0xAA   [31] PIN OE->1      [32] PIN CE->0   [33] PIN CE->1
                 ^^^^^^^^^^^ write#4 addr 0x5555 — LSB *and* MSB ELIDED (cache hit)
[34] DATA 0xAA   [35] PIN LSB_LE->1  [36] PIN LSB_LE->0     <- write#5  addr 0x2AAA
[37] DATA 0x2A   [38] PIN MSB_LE->1  [39] PIN MSB_LE->0
[40] DATA 0x55   [41] PIN OE->1      [42] PIN CE->0   [43] PIN CE->1
[44] DATA 0x55   [45] PIN LSB_LE->1  [46] PIN LSB_LE->0     <- write#6  addr 0x5555
[47] DATA 0x55   [48] PIN MSB_LE->1  [49] PIN MSB_LE->0
[50] DATA 0x20   [51] PIN OE->1      [52] PIN CE->0   [53] PIN CE->1
```

**The elision is real and load-bearing.** Write #4 (`0x5555`, `0xAA`) emits **no address latch at
all** — the cached LSB/MSB already hold `0x55`/`0x55`, so `rurp_write_to_register` returns early at
`rurp_register_utils.h:28-37`. A raw call-log golden would assert 6 entries the shield never sees.
CONTEXT.md's §specifics claim is confirmed **and quantified**: exactly 6 phantom entries at
exactly index 30.

Latched values presented at each `/CE` assertion, per pinout (SHIPPED):

| Pinout | `rw` line | `0x5555` → (LSB, MSB) | `/WE` | `0x2AAA` → (LSB, MSB) | `/WE` |
|---|---|---|---|---|---|
| `DIP28_28C256` | 14 | `(0x55, 0x55)` | **HIGH — inhibit** | `(0xAA, 0x2A)` | low (ok) |
| `DIP28_28C64` | 14 | `(0x55, 0x55)` | **HIGH — inhibit** | `(0xAA, 0x2A)` | low (ok) |
| `DIP24_2816` | 11 | `(0x55, 0x55)` | low (ok) | `(0xAA, 0x2A)` | **HIGH — inhibit** |
| `DIP32_28C512_EEPROM` | 20 | `(0x55, 0x55)` | low (ok)¹ | `(0xAA, 0x2A)` | low (ok)¹ |

¹ bus line 20 lives in CONTROL, which this path never writes — see CORRECTION 3.

### F5 — The remap-aware target stream, and the exact per-pinout divergence
`[VERIFIED: executed]`

`mem_util_remap_address_bus(h, addr, WRITE_FLAG)` outputs, and the resulting latches:

| Pinout | `mask` | `matching_lines` | remap(`0x5555`) | (LSB, MSB) | remap(`0x2AAA`) | (LSB, MSB) |
|---|---|---|---|---|---|---|
| `DIP28_28C256` | `0xBFFF` | 14 | `0x09555` | `(0x55, 0x95)` | `0x02AAA` | `(0xAA, 0x2A)` |
| `DIP28_28C64` | `0x1FFF` | 13 | `0x01555` | `(0x55, 0x15)` | `0x00AAA` | `(0xAA, 0x0A)` |
| `DIP24_2816` | `0x07FF` | 11 | `0x00555` | `(0x55, 0x05)` | `0x002AA` | `(0xAA, 0x02)` |
| `DIP32_28C512_EEPROM` | `0xFFFF` | 16 | `0x05555` | `(0x55, 0x55)` | `0x02AAA` | `(0xAA, 0x2A)` |

Two things fall out, both useful:

**The truncation claim is confirmed through live code, not arithmetic.** `AT28C64` receives
`0x1555`/`0x0AAA` — exactly DS20006432B §6.18/§6.19's documented `1555h`/`0AAAh`. `AT28C16`
receives `0x555`/`0x2AA`. `AT28C256` receives `0x9555`, whose bus line 15 is chip `A14`, so the
chip's internal address is `0x4000 | 0x1555 == 0x5555` — the remap simultaneously fixes `/WE`
**and** the `A14`-on-bus-line-15 defect that made `0x5555` arrive as `0x1555`. `SUMMARY.md`
CONFLICT 3 is upheld in full.

**Divergence per pinout (shipped → fixed), which is what TRACE-02 pins:**

| Pinout | Differing address-byte writes | Structural difference | RED strength |
|---|---|---|---|
| `DIP28_28C256` | 3 × MSB `0x55`→`0x95` | `/OE` edge moves | **strong** |
| `DIP28_28C64` | 3 × MSB `0x55`→`0x15`, 2 × MSB `0x2A`→`0x0A` | `/OE` edge moves | **strong** |
| `DIP24_2816` | 3 × MSB `0x55`→`0x05`, 2 × MSB `0x2A`→`0x02` | `/OE` edge moves | **strong** |
| `DIP32_28C512_EEPROM` | **none** | `/OE` edge moves only | **weak — see CORRECTION 3** |

The structural difference is worth naming because it is the only DIP32 hook and because **stream
length is identical (54 = 54) in every case**: `fu_flash_flip_data` calls `rurp_chip_input()`
*after* the address (`flash_utils.cpp:54-59` → `OE` at index 7 of each write), while
`memory_set_data` calls it *first* (`memory.cpp:229` → `OE` at index 0). So:

```
SHIPPED  per write:  DATA(lsb) LSB^ LSBv  DATA(msb) MSB^ MSBv  DATA(payload) OE->1  CE->0 CE->1
FIXED    per write:  OE->1  DATA(lsb) LSB^ LSBv  DATA(msb) MSB^ MSBv  DATA(payload) CE->0 CE->1
```

**A length- or count-based assertion cannot distinguish these two streams.** `SUMMARY.md` finding
10 warns against counting *register writes*; this is the stronger form of the same warning —
counting *anything* fails here. D-06's element-by-element ordered comparison is not merely
preferable, it is the only thing that works.

**Observation for Phase 117, recorded not acted on:** `fu_flash_flip_data` calls
`rurp_set_data_output()` (`flash_utils.cpp:54`); `memory_set_data` does **not**. Data-bus direction
before `rurp_write_data_buffer` therefore relies on incidental prior state in the fixed path
(on Uno, `rurp_internal_write_to_register`'s MSB branch happens to call it). Recording the two
direction calls costs 2 entry kinds and would make this visible — a middle path between D-07's
chosen scope and its rejected "record every `rurp_*` call" alternative. **Recommended**, flagged as
a small widening of D-07 for the planner to accept or decline.

### F6 — `EEPROM_SDP_DISABLE` is **not linkable** from a test TU
`[VERIFIED: compile error, this session]`

`const byte_flip_t EEPROM_SDP_DISABLE[]` at `eeprom_28c.cpp:24` is `const` at namespace scope in a
C++ TU → **internal linkage**. A test cannot `extern` it. Two consequences:

1. D-04's "test-local `byte_flip_t` copies" is not merely a stylistic choice — it is the **only**
   available shape. Good: the decision is already right.
2. TRACE-02 must pin the stream by driving `eeprom28c_write_init` (reachable via
   `configure_memory` → `h.firestarter_operation_init`), **not** by invoking the production table.
   And the test's local copy of the table is then an **unguarded transcription** — precisely the
   staleness class Pitfall 9 names.

**Recommendation:** pair the local copy with a cheap anti-drift gate. Either (a) a host-side pytest
that greps `eeprom_28c.cpp:26-33` for the six literal `{address, byte}` pairs and compares them to a
single source of truth, or (b) a firmware-side text scan in the same shape as D-04's `LOG_`-scan
checker. (a) is cheaper and reuses the D-11 cross-repo skipif machinery already being built. Flag as
a Claude's-Discretion resolution the planner should adopt.

`flash_util_byte_flipping` **is** externally linked (`flash_utils.cpp:21`), so feeding local tables
through the real emitter works — verified.

Also note `flash_execute_command(command)` (`flash_utils.h:15-16`) is a macro that expands to
`flash_util_byte_flipping(handle, command, ...)` — it requires a variable literally named `handle`
in scope. Tests holding a `firestarter_handle_t h` must call `flash_util_byte_flipping(&h, ...)`
directly. Cost me one compile cycle.

### F7 — TRACE-01's byte-exactness half is already demonstrated
`[VERIFIED: pio test -e native with the extension applied, this session]`

With the guard set from §Code Examples applied to `host_stubs_common.inc` and **no suite opting
in**, the full native run is **80/80 green across all 14 suites** — identical to the F2 baseline.
Because every guard is `#ifndef`/`#elif`-shaped, the flag-off preprocessor output is textually
unchanged for all 14 suites; the run confirms it empirically. TRACE-01's hard success criterion is
therefore low-risk, and the plan can state its verification as a single command.

### F8 — The D-12 migration matrix, executed
`[VERIFIED: executed]` — see CORRECTION 2 for the table and the mechanism.

Additional measured read counts under an address-keyed mock returning virgin `0xFF`:

| Test | reads @ `mfr_addr` | reads @ `0x5555` | total |
|---|---|---|---|
| `matching_chip_id_proceeds` | 2 | **2000** | 2002 |
| `mismatching_chip_id_errors` | 2 | 0 | 2 |
| `zero_chip_id_skips_check` | **0** | 2000 | 2000 |
| `mismatching_chip_id_with_force_warns` | 2 | **2000** | 2002 |

The `2000` figure is `eeprom28c_wait_for_write`'s full timeout loop (`eeprom_28c.cpp:131`). It is
the reason for §Pitfall 2.

The three `0x20` fixture sites TRACE-04 must retire: `test_eeprom28c_chip_id.cpp:104`
(`s_mock_bytes[2] = 0x20`), **`:140`** (`s_mock_bytes[0] = 0x20`), **`:160`**
(`s_mock_bytes[2] = 0x20`). CONTEXT.md names only `:104`; the success criterion says the fixture
"must not survive in that form **anywhere**", so all three are in scope.

### F9 — TRACE-05's DB facts, verified exactly
`[VERIFIED: executed against firestarter_app/firestarter/data/chip_database.json]`

```
algorithm == 13 entries : 84
chip_id_check           : {False: 84}
chip_id_value           : {"0x00000000": 84}
pinout distribution     : DIP28_28C64 35 | DIP24_2816 19 | DIP32_28C512_EEPROM 18 | DIP28_28C256 12
size_bytes >= 65536     : 18  (65536×1, 131072×10, 262144×3, 524288×4) — all on DIP32_28C512_EEPROM
support_status          : {supported: 75, adapter-required: 9}
electrical.type         : {EEPROM: 66, "Flash/EEPROM": 18}
```

**Access path** (the DB is `{manufacturer: [chip, ...]}`, and the fields live in a nested
`programming` object — a naive top-level scan finds nothing):
```python
for mfr, chips in db.items():
    for c in chips:
        if c["programming"]["algorithm"] == 13: ...
        c["programming"]["chip_id_check"]   # False for all 84
        c["programming"]["chip_id_value"]   # "0x00000000" for all 84
        c["pinout"]; c["electrical"]["size_bytes"]
```

**Recommendation on the "assert 84 or derive it" discretion item:** assert **both** — derive the
list, assert every element has `chip_id_check is False`, **and** assert `len(...) == 84` with a
message naming the requirement. The count assertion is what catches a DB change that silently adds
a 85th `0x0D` chip with an ID check; the per-element assertion is what catches a flip on an existing
row. Asserting only the count is hollow; asserting only the elements passes vacuously if the filter
breaks. This also gives the `CLOSE-01` "84-chip count unchanged" requirement a machine-checked home
one phase early.

**Home:** put it in `firestarter_app/tests/` next to D-11's drift gate. It needs no firmware
checkout, so it must **not** carry the `FW_ABSENT` skipif — keep the two concerns in separate test
functions even if they share a file, or the DB invariant silently skips in host-only CI.

### F10 — Branch base resolved: fork off `beta`, both sub-repos
`[VERIFIED: git merge-base --is-ancestor, this session]`

```
firestarter     : v1.21-community-chip-validation-command IS ancestor of beta and origin/beta
firestarter_app : v1.21-community-chip-validation-command IS ancestor of beta and origin/beta
```

Both sub-repos are currently checked out on `v1.21-community-chip-validation-command`; **no v1.22
branch exists yet in either.** ROADMAP's "v1.22 forks off `beta`" is **correct** — this reverses the
v1.15/v1.21 fork-off-the-previous-version exception, and CONTEXT.md's §"Setup precondition" question
is hereby answered with evidence. Meta repo is on
`gsd/v1.22-at28c-software-data-protection-lifecycle`.

**Plan task implication:** the first firmware-touching plan needs an explicit setup step creating
`v1.22-at28c-software-data-protection-lifecycle` off `beta` in **both** sub-repos before any commit.
Phase 116 touches both (`firestarter/` for the harness, `firestarter_app/` for D-11 + TRACE-05).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Ordered strobe capture (data bytes, latch strobes, CE/OE) | **Firmware test harness** (`_shared/host_stubs_common.inc`) | — | The only place all 14 suites share; a single edit point makes the flag-off byte-exactness argument cover every suite at once (F7) |
| Register-write elision + latch sequencing | **Firmware production header** (`rurp_register_utils.h`, included) | — | D-05: zero drift by construction. Never replicate (§Don't Hand-Roll) |
| Expected-stream ground truth (`bus_config_t` literals) | **Host generator** (`firestarter_app/tools/`) | Firmware `_shared/*.h` (committed artifact) | `database.py` lives host-side; firmware CI has no reason to install the host package (D-11, matches the `gen_validation_header.py` precedent exactly) |
| Generated-artifact drift gate | **Host pytest** (`firestarter_app/tests/`) | — | D-11; `FW_ABSENT` skipif for the cross-repo half |
| DB invariant (84 × `chip_id_check: false`) | **Host pytest** | — | Pure DB fact; no firmware checkout needed → must NOT carry the FW skipif (F9) |
| RED-baseline evidence artifact | **Firmware sub-repo** (`RED-BASELINE.md`) | `.planning/` (`116-PREMISE.md`) | D-02: lives next to the code, survives archival |
| `LOG_`-in-window source scan + planted fixture | **Host tool** (`firestarter_app/tools/` + paired pytest) | — | Reuses the `FIRESTARTER_DEVTEST_SRC` env-override seam (`check_devtest_orchestrator.py:86`) |
| `protocol != 0x0D` → `0xBB` negative | **Firmware native suite** | — | Existing `test_not_implemented` pattern |
| PROJECT.md premise correction (D-14) | **Meta `.planning/`** | — | Downstream researchers for 117–122 read it |

**Zero production `src/` responsibility.** This phase writes nothing under `firestarter/src/`.
The one production **header** it touches is an `#include`, not an edit.

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `/workspaces/firestarter/CLAUDE.md`:

| Directive | Phase-116 compliance requirement |
|---|---|
| Meta repo tracks only `.planning/` and `.claude/`; sub-repos are not committed here | Harness code commits go **inside** the `firestarter`/`firestarter_app` submodules on the v1.22 branch; only `116-*.md` + PROJECT.md land in meta |
| Serial-protocol changes must stay in sync between `serial_comm.py` and `firestarter.cpp` | **N/A** — Phase 116 makes no wire change. Verify this stays true; any wire change is a scope breach |
| Constants/flag bits duplicated between `constants.py` and `firestarter.h` — change both together | **N/A** — no new `CMD_*`/`FLAG_*` in this phase (those are Phases 119/120) |
| `firestarter/include/messages.h` is codegen-generated from `messages.toml`; CI drift gate | **Do not touch.** Phase 116 needs no new message IDs (it adds no `LOG_`). If a plan proposes one, that is a signal the plan drifted into Phase 118 |
| `pio test -e native` is the no-hardware validation path; reuse pattern documented | Follow it: new suite dir under `test/native/avr/`, `test_*` prefix required (F-note below), extend `host_stubs.cpp` only for new `rurp_*` symbols |
| `[env:native]` uses a **positive `test_filter` allowlist** (PIO quirk) | A new suite needs **both** a `test_filter` line and an `-I test/native/avr/<dir>` line. This is what makes D-01's park-then-add-in-117 work |
| Generated artifacts carry a `DO NOT EDIT` banner + CI drift gate | D-10; banner text must match the `validation_matrix.h` shape (§Code Examples) |
| Anti-hollow discipline is mandatory: every gate ships a planted-violation fixture | TRACE-03. AST/structural scans preferred over substring greps |
| Validate `ruff check` + `ruff format --check` against py3.9/3.11 CI targets, not the devcontainer's 3.12 | Applies to the D-11 generator + TRACE-05 test. Devcontainer is **Python 3.12.13** (§Environment) |

**PIO discovery quirk worth a plan note** `[VERIFIED: this session]`: PlatformIO only collects test
directories whose name begins with `test`. A suite directory named e.g. `sdp_trace/` is silently
**not collected** — `pio test` reports "Collected N tests" unchanged and "0 test cases", with no
error. Cost me one cycle. Both new suite directories must be `test_*`.

---

## Standard Stack

**Zero new dependencies on either side of the wire.** Everything Phase 116 needs is in-tree or
already installed. `[VERIFIED: this session]`

### Core

| Component | Version | Purpose | Why standard |
|---|---|---|---|
| PlatformIO Core | **6.1.19** | `[env:native]` host test runner | Already pinned/installed; the only no-hardware validation path |
| Unity | **2.6.1** | Assertion framework | `test_framework = unity`; auto-installed by PIO |
| ArduinoFake | **^0.4.0** | `delay`/`delayMicroseconds`/`Serial` fakes | Already in `lib_deps`; **required** by D-05 (see CORRECTION 1) |
| g++ / gnu++17 | system | Host cross-compile | `-std=gnu++17` already in `[env:native]` build_flags |
| pytest | **9.1.1** | D-11 drift gate + TRACE-05 | Existing host test framework |
| ruff | **0.15.20** | lint/format gate | Existing CI gate |

### Supporting (in-tree, reuse verbatim)

| Asset | Path | Use |
|---|---|---|
| `host_stubs_common.inc` | `firestarter/test/native/avr/_shared/` | **The** single edit point for TRACE-01 |
| `rurp_register_utils.h` | `firestarter/include/` | D-05 include — supplies elision + strobe sequencing |
| `gen_validation_header.py` | **`firestarter_app/tools/`** | D-08/D-10 generator shape |
| `validation_matrix.h` | `firestarter/test/native/avr/_shared/` | `DO NOT EDIT` banner + committed-artifact shape |
| `test_gen_validation_header.py` | `firestarter_app/tests/` | D-11 drift-gate + `FW_ABSENT` skipif shape |
| `test_revision_constants_parity.py` | `firestarter_app/tests/` | Original `FW_ABSENT` skipif idiom |
| `check_devtest_orchestrator.py:86` | `firestarter_app/tools/` | `FIRESTARTER_DEVTEST_SRC` env-override seam for D-04's `LOG_` scan |
| `test_val_eeprom28c.cpp` | `firestarter/test/native/avr/` | `make_handle` + recording-assert idiom to extend |
| `test_val_5v_page.cpp` | `firestarter/test/native/avr/` | The strongest existing trace assert — the bar D-06 raises |
| `test_not_implemented` | `firestarter/test/native/avr/` | Ready-made `0xBB` negative pattern |

**Installation:** none. No `npm install`, `pip install` or `pio lib install` step exists in this
phase.

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|---|---|---|
| Including the real `rurp_register_utils.h` (D-05) | Hand-replicated cache-compare (v1.18 WR-01) | Smaller blast radius, but silent drift if production caching changes. **D-05 is correct** — and CORRECTION 1's guards make the include cheap |
| Literal tuple arrays (D-06) | Golden text-trace files | Needs a renderer that itself needs a test; whitespace churn becomes a failure. Also: F5 shows length is identical shipped-vs-fixed, so any digest/hash approach is fine but an element-index-naming assert is what makes the Phase-117 diff readable |
| Host-side generator (D-11) | Firmware-side generator importing the host package | Introduces a firmware→host import direction that does not exist; firmware CI has no reason to install the host package. **Precedent already resolves this** (`gen_validation_header.py` is host-side) |

---

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.**

| Package | Registry | Verdict | Disposition |
|---|---|---|---|
| *(none)* | — | — | — |

Every dependency is already present and pinned: PlatformIO 6.1.19, Unity 2.6.1 (auto-fetched by
PIO from its own registry per `test_framework = unity`), ArduinoFake `^0.4.0` (already in
`[env:native] lib_deps`), pytest 9.1.1, ruff 0.15.20. No new entry is added to `lib_deps`,
`pyproject.toml`, or any manifest.

**Packages removed due to `[SLOP]` verdict:** none.
**Packages flagged as suspicious `[SUS]`:** none.
**No `checkpoint:human-verify` install gate is required for this phase.**

If a plan proposes adding a dependency, treat that as a scope breach and re-run this gate.

---

## Architecture Patterns

### System Architecture Diagram

```
                     ┌─────────────────────────────────────────────────────┐
                     │  HOST REPO (firestarter_app)                        │
                     │                                                     │
   pinouts.json ────►│  database.py :: convert_to_programmer               │
 chip_database.json  │        │                                            │
                     │        ├──► tools/gen_sdp_bus_config.py  (D-08/D-11)│
                     │        │         │                                   │
                     │        │         └─► emits bus_config_t literals ────┼──┐
                     │        │                                             │  │
                     │        └──► tests/test_sdp_bus_config_drift.py ──────┼─┐│
                     │                 (regenerate + diff, FW_ABSENT skipif)│ ││
                     │                                                      │ ││
                     │  tests/test_devtest_sdp_db_invariant.py  (TRACE-05)  │ ││
                     │        └─► 84 × algorithm==13 → chip_id_check False  │ ││
                     │                                                      │ ││
                     │  tools/check_no_log_in_sdp_window.py     (TRACE-03)  │ ││
                     │        ├─ scans FIRESTARTER_SDP_SRC (env seam)       │ ││
                     │        └─ paired pytest points it at a PLANTED       │ ││
                     │           fixture proving the scan actually fails    │ ││
                     └──────────────────────────────────────────────────────┘ ││
                                                                    committed ││
                                                                     artifact ││
                     ┌────────────────────────────────────────────────────────┘│
                     │                                            drift-checked┘
                     ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│  FIRMWARE REPO (firestarter) — test/native/avr/                                  │
│                                                                                  │
│  _shared/sdp_bus_config.h   [DO NOT EDIT — generated]                            │
│  _shared/host_stubs_common.inc                                                   │
│        │                                                                         │
│        ├── flag OFF  ────────────────────────► today's no-op stubs (8 suites)     │
│        ├── HOST_STUBS_RECORD_BUS ────────────► reg-write log      (6 suites)      │
│        └── HOST_STUBS_REAL_REGISTER_UTILS ───► ORDERED STROBE STREAM (new)        │
│                  │                                                               │
│                  │  hooks:  rurp_write_data_buffer  → {DATA, -, byte}             │
│                  │          rurp_set_control_pin    → {PIN, pin, level}           │
│                  │  suppresses: 6 symbols now supplied by the real header         │
│                  ▼                                                               │
│            #include "rurp_register_utils.h"   ◄── production elision + sequencing │
│                  │        (cache: lsb_address / msb_address / control_register)   │
│                  ▼                                                               │
│  ┌───────────────────────────────┐      ┌──────────────────────────────────────┐  │
│  │ test_sdp_harness/  (D-03)     │      │ test_eeprom28c_sdp/  (D-01, PARKED)  │  │
│  │ ALWAYS GREEN, in test_filter  │      │ RED today; Phase 117 adds the        │  │
│  │                               │      │ test_filter line = the RED→GREEN     │  │
│  │ • ordered-capture proof       │      │ proof                                │  │
│  │ • flag-off byte-exactness     │      │                                      │  │
│  │ • cache-reset seam            │      │ • 4 pinouts + 1 DIP32 stale-upper    │  │
│  │ • negatives: 0x10 table,      │      │   band case  (D-09, CORRECTION 3)    │  │
│  │   write-prefix swap           │      │ • matching_chip_id_proceeds          │  │
│  │ • 0xBB not-implemented        │      │ • force_warns  (CORRECTION 2)        │  │
│  │ • migrated ID-gate tests      │      │ • RED-BASELINE.md fixture (D-02)     │  │
│  └───────────────────────────────┘      └──────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                     .planning/116-PREMISE.md  (TRACE-06, D-14)
                     .planning/PROJECT.md  ⚠ third correction block
```

### Recommended Structure

```
firestarter/test/native/avr/
├── _shared/
│   ├── host_stubs_common.inc          # EDITED: new opt-in flag + 5 guards
│   ├── validation_matrix.h            # untouched (precedent only)
│   └── sdp_bus_config.h               # NEW: generated, DO NOT EDIT (D-08/D-10)
├── test_sdp_harness/                  # NEW: always-green (D-03)
│   ├── host_stubs.cpp                 #   defines the flag, includes real header
│   ├── test_sdp_harness.cpp
│   └── sdp_expected.h                 #   literal tuple arrays (D-06)
└── test_eeprom28c_sdp/                # NEW: RED, PARKED out of test_filter (D-01)
    ├── host_stubs.cpp
    ├── test_eeprom28c_sdp.cpp
    ├── sdp_expected_fixed.h           #   the post-117 target streams
    └── RED-BASELINE.md                #   D-02 committed evidence

firestarter_app/
├── tools/
│   ├── gen_sdp_bus_config.py          # NEW (D-08/D-11)
│   └── check_no_log_in_sdp_window.py  # NEW (TRACE-03)
└── tests/
    ├── test_sdp_bus_config_drift.py   # NEW: FW_ABSENT skipif (D-11)
    ├── test_sdp_db_invariant.py       # NEW: 84 × chip_id_check (TRACE-05) — NO skipif
    └── fixtures/planted_log_in_window.py  # NEW: planted-violation fixture (D-04)
```

*(Directory names are the Claude's-Discretion item; these are chosen so Phases 118–119 can add
cases to `test_sdp_harness/` without renaming, while `test_eeprom28c_sdp/` stays the
protocol-specific RED home. D-02's illustrative path is preserved.)*

### Pattern 1 — Two-layer opt-in, `#ifndef`-guarded

The existing `HOST_STUBS_RECORD_BUS` is an opt-**IN** flag (inverse of the opt-**OUT**
`HOST_STUBS_CUSTOM_*` guards). TRACE-01's flag is a **second** opt-in on the same convention, and
it internally sets three opt-out guards so the real header can supply what the stub used to.
Structure: `#ifdef NEW_FLAG … #elif defined(HOST_STUBS_RECORD_BUS) … #else … #endif`. Flag-off
output is textually unchanged → F7's 80/80 result.

### Pattern 2 — Prefix assertion over a flooded stream

`eeprom28c_write_init` records **~6057 strobe entries** (F1) because the timeout poll runs 2000
iterations. The SDP window is entries **0–53**. Assert the **prefix**; the recorder drops the
**tail** on overflow (`if (count < MAX)`), never the head, so a prefix assertion is sound even when
saturated. Add an explicit `strobe_overflowed()` accessor so a test can state whether it is
asserting over a complete or truncated stream — silent truncation is otherwise indistinguishable
from a short stream.

### Pattern 3 — Address-keyed mock (TRACE-04)

Replace `s_mock_bytes[idx++]` with `switch (addr)`. Return virgin `0xFF` by default; plant only the
two chip-id bytes. Re-express any call-ordered assertion as a **per-address read counter**
(`reads_at_mfr_addr == 0`), which is outcome-independent. Remember `configure_memory` overwrites
`firestarter_get_data` **and** `firestarter_set_data`, so both must be re-assigned after it (the
existing comment at `test_eeprom28c_chip_id.cpp:93-99` covers only `get_data`).

### Anti-Patterns to Avoid

- **Counting anything.** F5 proves shipped and fixed streams have identical length (54). Counting
  register writes, strobes, or CE pulses cannot distinguish them.
- **Replicating the cache-compare.** D-05 exists to prevent this. `#include`, never re-implement.
- **Trusting the `0xff` power-on register cache.** It injects `0x8E` (VPP-regulator bit set) into
  the first CONTROL write. Reset deliberately.
- **A suite directory not named `test_*`.** Silently uncollected, no error.
- **Asserting only `len(...) == 84`** in TRACE-05, or only the per-element flag. Both, or the gate is
  hollow in one direction.
- **Letting the DIP32 case be RED by accident** (CORRECTION 3).

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Register-write elision / cache-compare | A stub that mirrors `if (cached == new) return;` | `#include "rurp_register_utils.h"` (D-05) | Silent drift if production caching changes. Verified: the include compiles once CORRECTION 1's guards are in |
| Latch-strobe sequencing (`DATA` → `LE↑` → `LE↓`) | A hand-written triple in the stub | Same include — `rurp_internal_write_to_register:83-88` already does it | The ordering *is* the thing under test; a replica would test itself |
| `bus_config_t` ground truth | Hand-typed literals with a derivation comment | Generator importing `database.py` (D-08) | `pinouts.json` moved twice in four milestones (Phase 94 `page_size`, Phase 98 `rw-pin`). A transcription stales silently |
| Generated-header drift detection | A README note saying "remember to regenerate" | Regenerate-and-diff pytest (D-10/D-11) | Established convention: `messages.h`, `validation_matrix.h` |
| Cross-repo test skipping | `try: import …` / path guesswork | `FW_ABSENT` skipif (`test_revision_constants_parity.py`, `test_gen_validation_header.py:37-41`) | Already solved twice in this repo |
| Source-scan checker + proof it fails | A one-time manual mutation with a pasted transcript | Env-override seam + planted fixture (`FIRESTARTER_DEVTEST_SRC` shape) | D-04 already chose this; the precedent is `check_devtest_orchestrator.py:86` |
| `protocol != 0x0D` fail-closed check | A new bespoke suite | Extend `test_not_implemented` | Ready-made |
| Golden trace rendering | A text serialiser + its own tests | Literal tuple arrays (D-06); renderer optional, diagnostics-only | Whitespace churn becomes a test failure |

**Key insight:** in this domain the *harness* is the thing most likely to be subtly wrong, and every
line of harness logic that duplicates production is a place where the oracle can agree with itself
while both diverge from silicon. That is precisely how abandoned commit `0052c42` reported "22 tests
PASS (zero-diff)" after swapping the SDP tables. Prefer including production code over describing
it — even when the include is inconvenient (it was: six redefinitions and a SIGABRT).

---

## Runtime State Inventory

*Included because TRACE-01 modifies a surface shared by all 14 native suites, and because D-05
introduces mutable process-global state into the test binaries. This is not a rename phase, but the
"what still holds stale state after the source is correct?" question has real answers here.*

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | None — no database, datastore, or persisted record is written by this phase. The DB is **read-only** in TRACE-05 and must stay byte-identical (`diff_db.py` identity is a GATE-03/CLOSE-01 concern). `[VERIFIED]` | None — assert DB untouched |
| **In-process global state** | **`lsb_address`, `msb_address`, `control_register`** (`rurp_register_utils.h:12-14`) are non-`static` globals initialised to `0xff/0xff/0xff`. Once the real header is included they **persist across Unity test cases in the same binary** — case N's cache is case N−1's leftovers. Also `revision = 0xFF` (`rurp_hw_rev_utils.h:13`). `[VERIFIED: executed]` | **Code: add an explicit cache-reset seam** called from `setUp()`. Not optional — without it the D-09 stale-upper-address case and the clean cases contaminate each other, and case order becomes load-bearing |
| **Recording-buffer state** | `s_bus_recording_count` / new `s_strobe_count`, reset by `clear_bus_recording()` / `clear_strobes()`. Overflow is **silently ignored** (`if (count < MAX)`), and `write_init` produces ~6057 entries against today's `HOST_STUBS_MAX_RECORDING 256`. `[VERIFIED: executed]` | **Code: add a saturation flag** + size the new buffer (512 gives ~10× headroom on the 54-entry SDP window) |
| **Live service config** | None — no external service, no n8n workflow, no dashboard. `[VERIFIED: phase touches only test code + host tools]` | None |
| **OS-registered state** | None — no scheduled task, no daemon, no pm2 process. `[VERIFIED]` | None |
| **Secrets / env vars** | One **new** env-override seam (`FIRESTARTER_SDP_SRC` or similar) for D-04's source-scan checker, mirroring `FIRESTARTER_DEVTEST_SRC`. It is a test seam with a safe default, not a secret. No existing secret or env var is renamed. `[VERIFIED]` | Document the default; ensure the checker fails closed if the path is missing |
| **Build artifacts** | `firestarter/.pio/build/native/` is stale after the `.inc` change. PIO rebuilds automatically; no manual step. Untracked `__pycache__` in `firestarter_app/tools/` and `tests/` is pre-existing. **`/workspaces/platformio.ini`** (untracked, auto-generated by `.devcontainer/gen-platformio-ini.py`) is currently **malformed** — duplicate `[platformio]` section at line 26 — so any `pio` invocation from the meta root fails with `InvalidProjectConfError`. `[VERIFIED: reproduced]` | **None required**, but plans must run `pio` from `firestarter/`, never from `/workspaces`. Worth a one-line note in the plan's verification commands |

---

## Common Pitfalls

### Pitfall 1 — The `0xff` register cache injects a VPP-enable bit into the first CONTROL write
**What goes wrong:** with the real header included, `rurp_read_from_register(CONTROL_REGISTER)`
returns the real cache, which starts at `0xff`. `mem_util_calculate_top_address_register` ORs
`cache & (CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE)`
into every address write, so the first CONTROL write carries **`0x8E`** (DIP32/DIP24) or **`0x9E`**
(DIP28, which additionally forces `CTRL_ADDRESS_LINE_17`). `0x8E` has
`CTRL_VPP_REGULATOR_ENABLE (0x80)` set.
**Why it happens:** the old return-0 stub made this invisible. `[VERIFIED: measured 0x8E / 0x9E]`
**How to avoid:** reset the cache to a deliberate, documented value in `setUp()`. Derive the
expected CONTROL bytes from that reset value, never from a guess.
**Warning signs:** a new suite that looks like it proves `configure_eeprom28c` enables the VPP
regulator — the exact opposite of what `test_val_eeprom28c` asserts. If the new suite and the old
one disagree about VPP on the same handler, this is why.

### Pitfall 2 — The timeout poll floods the recording buffer, silently
**What goes wrong:** driving `eeprom28c_write_init` records **~6057** entries. Against today's
`HOST_STUBS_MAX_RECORDING 256` that is 24× over; the recorder drops everything past 256 with no
signal. `[VERIFIED: measured 6054–6057 across five handles]`
**Why it happens:** `eeprom28c_wait_for_write` loops 2000 times (`eeprom_28c.cpp:131`), each
iteration emitting `/OE`, `/CE↓`, `/CE↑` via `memory_get_data`. Address latches are elided (same
address every poll), so only the pin edges accumulate.
**How to avoid:** size the new buffer independently (512 recommended), add `strobe_overflowed()`,
and assert on the **prefix** (entries 0–53). Overflow drops the tail, so prefix assertions stay
valid.
**Warning signs:** an expected-vs-actual mismatch that starts exactly at index 256, or a stream
length that is suspiciously round.

### Pitfall 3 — ArduinoFake SIGABRT reads exactly like the D-13 flake
**What goes wrong:** `pio test` reports `Program received signal SIGABRT (Aborted)` with no Unity
output. It looks identical to the documented `test_eeprom28c_chip_id` / `test_flash_intel_vpp`
Unity-teardown race that D-13 defers. `[VERIFIED: reproduced and resolved]`
**Why it happens:** the real header calls `delayMicroseconds`; ArduinoFake aborts on any unmocked
virtual.
**How to avoid:** `When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();` — plus `delay`
and `millis` if the path reaches `eeprom28c_check_chip_id` or `flash_util_verify_operation`. Put
these in the new suites' `setUp()` from the first commit and comment *why*, so nobody deletes them
as unused.
**Warning signs:** SIGABRT in a **new** suite. D-13's flake is confined to two **existing** parked
suites; a new suite aborting is this, not that. Do not spend the phase chasing D-13.

### Pitfall 4 — Elision makes a raw call-log assert writes the shield never sees
**What goes wrong:** a golden built from an unelided call log asserts 6 phantom entries at index 30
(write #4's LSB+MSB triples). `[VERIFIED: measured — write #4 emits only DATA + OE + CE pulse]`
**Why it happens:** `rurp_write_to_register` returns early on an unchanged cached value
(`rurp_register_utils.h:28-37`); the SDP sequence addresses `0x5555` on consecutive writes 3→4.
**How to avoid:** D-05. This is the pitfall D-05 exists for, and it is now quantified rather than
predicted.
**Warning signs:** an expected array with a suspiciously regular 10-entries-per-write structure.
The real stream is 10, 10, 10, **4**, 10, 10.

### Pitfall 5 — The DIP32 case passing does not mean the DIP32 case proved anything
**What goes wrong:** on `DIP32_28C512_EEPROM`, shipped and fixed address bytes are identical, so a
straightforward trace is GREEN today and stays GREEN after the fix — proving nothing, while looking
like coverage. `[VERIFIED: measured — identical (0x55, 0x55) / (0xAA, 0x2A) both paths]`
**Why it happens:** that pinout's `rw` line is 20 → CONTROL bit `0x10`, and
`fu_flash_fast_address` never writes CONTROL.
**How to avoid:** CORRECTION 3 — make the DIP32 case a deliberate stale-upper-address case.
**Warning signs:** a DIP32 case whose expected-shipped and expected-fixed arrays are equal. If the
plan produces that, the case is decorative.

### Pitfall 6 — Retiring the `0x20` fixture at one site and calling TRACE-04 done
**What goes wrong:** three sites plant `0x20` to satisfy the inverted check — `:104`, `:140`,
`:160`. CONTEXT.md names only `:104`. `[VERIFIED: read]`
**How to avoid:** grep the migrated suites for `0x20` and for `wait_for_write` in comments before
declaring TRACE-04 met. The success criterion says "must not survive in that form **anywhere**".

### Pitfall 7 — Overclaiming in `116-PREMISE.md`
**What goes wrong:** the INIT-abort result is genuinely strong, which makes it tempting to write
"confirmed that AT28C writes fail on real hardware." That crosses the validation ceiling and is the
specific failure mode `REQUIREMENTS.md` §Validation Ceiling was written to prevent.
**How to avoid:** use the wording in §F1. Say **software-layer**, name the datasheet bridge as a
citation not an observation, and state that no AT28C part was on the bench.
**Warning signs:** any sentence in `116-PREMISE.md` whose subject is the chip rather than the code.

---

## Code Examples

### The complete guard set for `host_stubs_common.inc` (resolves CORRECTION 1)
```c
/* Source: verified to compile, link and run in this session.
 * Replaces the `#ifdef HOST_STUBS_RECORD_BUS` opener at :54.
 * Existing HOST_STUBS_RECORD_BUS suites fall through the `#elif` unchanged. */
#ifdef HOST_STUBS_REAL_REGISTER_UTILS
/* Ordered strobe recorder (TRACE-01). rurp_write_to_register and
 * rurp_read_from_register come from the REAL include/rurp_register_utils.h,
 * which the suite's host_stubs.cpp includes AFTER this file — so they must NOT
 * be defined here, and neither may the four HARDWARE_REVISION stubs that
 * rurp_hw_rev_utils.h (pulled in by that header under the inherited
 * -D HARDWARE_REVISION) already defines. Six redefinition errors otherwise. */
#define HOST_STUBS_MAX_STROBES 512
#define HOST_STUBS_CUSTOM_CONTROL_PIN
#define HOST_STUBS_CUSTOM_DATA_BUFFER
#define HOST_STUBS_CUSTOM_HW_REVISION_BLOCK

enum { STROBE_KIND_DATA = 1, STROBE_KIND_PIN = 2 };
struct strobe_entry_t { uint8_t kind; uint8_t pin; uint8_t value; };
static strobe_entry_t s_strobes[HOST_STUBS_MAX_STROBES];
static int s_strobe_count = 0;
static int s_strobe_overflow = 0;

extern "C" void clear_strobes()     { s_strobe_count = 0; s_strobe_overflow = 0; }
extern "C" int  strobe_count()      { return s_strobe_count; }
extern "C" int  strobe_overflowed() { return s_strobe_overflow; }   /* Pitfall 2 */
extern "C" uint8_t strobe_kind(int i)  { return s_strobes[i].kind; }
extern "C" uint8_t strobe_pin(int i)   { return s_strobes[i].pin; }
extern "C" uint8_t strobe_value(int i) { return s_strobes[i].value; }

static void strobe_push(uint8_t kind, uint8_t pin, uint8_t value) {
    if (s_strobe_count < HOST_STUBS_MAX_STROBES) {
        s_strobes[s_strobe_count].kind  = kind;
        s_strobes[s_strobe_count].pin   = pin;
        s_strobes[s_strobe_count].value = value;
        s_strobe_count++;
    } else {
        s_strobe_overflow = 1;   /* tail is dropped; prefix stays valid */
    }
}
/* The two hooks. rurp_set_control_pin carries LSB/MSB/CTRL latch strobes AND
 * chip /CE and /OE in one distinguishable pin namespace (rurp_shield.h:53-57). */
extern "C" void rurp_write_data_buffer(uint8_t data) {
    strobe_push(STROBE_KIND_DATA, 0, data);
}
extern "C" void rurp_set_control_pin(uint8_t pin, uint8_t state) {
    strobe_push(STROBE_KIND_PIN, pin, state);
}
#elif defined(HOST_STUBS_RECORD_BUS)
#define HOST_STUBS_MAX_RECORDING 256
/* ... existing recording body, unchanged ... */
```

Plus these four `#ifndef` wrappers elsewhere in the same file (all verified):
```c
/* around the existing rurp_read_from_register stub at :82 */
#ifndef HOST_STUBS_REAL_REGISTER_UTILS
extern "C" rurp_register_t rurp_read_from_register(uint8_t reg) { (void)reg; return 0; }
#endif

/* around the existing rurp_set_control_pin stub at :90 */
#ifndef HOST_STUBS_CUSTOM_CONTROL_PIN
extern "C" void rurp_set_control_pin(uint8_t pin, uint8_t state) { (void)pin; (void)state; }
#endif

/* around the existing rurp_write_data_buffer stub at :98 */
#ifndef HOST_STUBS_CUSTOM_DATA_BUFFER
extern "C" void rurp_write_data_buffer(uint8_t data) { (void)data; }
#endif

/* the HARDWARE_REVISION block opener at :125 */
#if defined(HARDWARE_REVISION) && !defined(HOST_STUBS_CUSTOM_HW_REVISION_BLOCK)
```

**Verified result:** `pio test -e native` → **80/80 green across all 14 suites** with the above
applied and no suite opting in (TRACE-01's byte-exactness criterion).

### The new suite's `host_stubs.cpp` + the mandatory cache-reset seam
```c
/* Source: verified in this session. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

#define HOST_STUBS_REAL_REGISTER_UTILS      /* MUST precede the include */
#include "../_shared/host_stubs_common.inc"

/* D-05: production's real cache-compare + latch-strobe sequencing. */
#include "rurp_register_utils.h"

/* Pitfall 1 / Runtime State Inventory: lsb_address, msb_address and
 * control_register are non-static globals (rurp_register_utils.h:12-14)
 * initialised to 0xff. They persist across Unity cases in this binary, and the
 * 0xff CONTROL value ORs a VPP-regulator bit into the first address write. Every
 * case must reset them deliberately. */
extern "C" void reset_register_cache(uint8_t lsb, uint8_t msb, rurp_register_t ctrl) {
    lsb_address = lsb; msb_address = msb; control_register = ctrl;
}
```

### Mandatory ArduinoFake mocks (Pitfall 3)
```c
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
    /* REQUIRED by D-05: the real rurp_register_utils.h calls delayMicroseconds
     * (rurp_internal_write_to_register:86 and the settle path :58). ArduinoFake
     * ABORTS (SIGABRT) on an unmocked virtual. Do not remove as "unused". */
    When(Method(ArduinoFake(), delayMicroseconds)).AlwaysReturn();
    When(Method(ArduinoFake(), delay)).AlwaysReturn();       /* check_chip_id path */
    When(Method(ArduinoFake(), millis)).AlwaysReturn(0);
    clear_strobes();
    reset_register_cache(0x00, 0x00, 0x00);
}
```

### Building a `bus_config_t` the way `json_parser.c` does (what the D-08 generator must emit)
```c
/* Source: mirrors src/json_parser.c:401-430 exactly. Verified against the host's
 * convert_to_programmer output for AT28C256: bus [0..13,15], rw-pin 14. */
h.bus_config.matching_lines = 0xFF;
for (uint8_t j = 0; j < bus_len; j++) {
    h.bus_config.address_lines[j] = bus[j];
    h.bus_config.address_mask |= 1UL << bus[j];
    if (h.bus_config.matching_lines == 0xFF && bus[j] != j)
        h.bus_config.matching_lines = j;                     /* AT28C256 -> 14 */
}
if (h.bus_config.matching_lines == 0xFF) h.bus_config.matching_lines = bus_len;
if (bus_len < ADDRESS_LINES_SIZE) h.bus_config.address_lines[bus_len] = 0xFF;
h.bus_config.rw_line          = rw_pin;      /* 14 / 14 / 11 / 20 */
h.bus_config.vpp_line         = 0xFF;        /* no vpp-pin on any 0x0D pinout */
h.bus_config.static_high_mask = 0;           /* none of the four declare static-high-pins */
```
`[VERIFIED]` The four pinouts, straight from `EpromDatabase.convert_to_programmer`:
```
AT28C256 DIP28_28C256          bus [0..13,15]  rw-pin 14   mem 32768
AT28C64  DIP28_28C64           bus [0..12]     rw-pin 14   mem 8192
AT28C16  DIP24_2816            bus [0..10]     rw-pin 11   mem 2048
AT28C010 DIP32_28C512_EEPROM   bus [0..15]     rw-pin 20   mem 131072
AT28C040 DIP32_28C512_EEPROM   bus [0..15]     rw-pin 20   mem 524288   <- same bus_config
(comparator) SST39SF040 DIP32_SST39SF040  bus [0..16,20,21]  rw-pin 22
```
Note `AT28C010` and `AT28C040` share an identical `bus_config` — so D-09's extra "size band" case
is distinguished by `mem_size` and by prior register state, **not** by `bus_config`. That is a
second, independent reason CORRECTION 3's stale-upper-address framing is the right one.

### The generated header's banner (D-10, matching the in-tree convention exactly)
```c
/* DO NOT EDIT -- generated by tools/gen_sdp_bus_config.py
 * Re-run after editing firestarter_app/firestarter/data/pinouts.json */
#pragma once
```
`[VERIFIED: validation_matrix.h:1-2]` The drift gate asserts this exact prefix
(`test_gen_validation_header.py:53-59`) — mirror that assertion.

### Confirming the elision empirically before trusting an expected array
```c
/* The single most valuable diagnostic in this phase: dump, then hand-check. */
static void dump(const char* tag) {
    printf("##### %s total=%d overflow=%d\n", tag, strobe_count(), strobe_overflowed());
    for (int i = 0; i < strobe_count(); i++) {
        if (strobe_kind(i) == STROBE_KIND_DATA) printf("[%3d] DATA 0x%02X\n", i, strobe_value(i));
        else printf("[%3d] PIN  0x%02X -> %d\n", i, strobe_pin(i), strobe_value(i));
    }
}
/* Unity swallows printf; run the binary directly to see it:
 *   pio test -e native -f "*<suite>*" ; ./.pio/build/native/firestarter_native   */
```
`[VERIFIED]` `pio test` does not surface `printf` from test bodies. The built binary is at
`.pio/build/native/firestarter_native` and running it directly prints everything. This is how the
F4/F5 streams in this document were obtained, and the plan should use the same trick to author the
expected arrays instead of hand-deriving them.

---

## State of the Art

No external technology moved. The relevant "state of the art" is entirely in-repo:

| Old approach | Current approach | When changed | Impact on Phase 116 |
|---|---|---|---|
| Per-suite duplicated `rurp_*` stubs | Single `_shared/host_stubs_common.inc` | Phase 6 WR-06 | One edit point covers all 14 suites — F7's argument |
| No register observation | `HOST_STUBS_RECORD_BUS` reg-write log | Phase 71 HARN-01 / D-04 | The precedent TRACE-01 layers onto |
| `test_ignore` | Positive `test_filter` allowlist | PIO version quirk, documented in `platformio.ini` | Makes D-01's park-then-add-in-117 a valid proof mechanism |
| Hand-maintained matrices | Generated header + `DO NOT EDIT` + drift gate | Phase 71 HARN-02 (`validation_matrix.h`) | D-08/D-10/D-11's exact shape |
| Legacy `mem_type`/`type` dispatch axis | `protocol`-only dispatch | v1.20 (Phases 105–107) | `configure_memory` has a single axis; the `0xBB` negative is a clean one-liner |

**Deprecated / absent — do not plan against:**
- `firestarter/src/primitives.cpp` and `include/primitives.h` — **do not exist** on this tree
  `[VERIFIED: absent]`. The v1.16 Phase-89 recompose is on an unmerged branch. No v1.16-era golden
  traces exist to reuse.
- A wire `page_size` / `page-size` field — **does not exist**; `json_parser.c` has no such key and
  the comment in `constants.py:107-111` claiming firmware sync is false (`SUMMARY.md` finding 9).
- `firestarter/tools/gen_validation_header.py` — **wrong path**; the generator is at
  `firestarter_app/tools/gen_validation_header.py` `[VERIFIED]`. CONTEXT.md §canonical_refs cites the
  firmware path; D-11's *decision* (host-side generator) is right and matches the real precedent.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `RESPONSE_CODE_ERROR == 0`, `OK == 1`, `WARNING == 2` — read from the running binary, not from a header grep | F1, F8 | Low. The INIT-abort conclusion would invert if these were mis-read; the probe printed all three side by side, so the risk is near zero, but a plan task should re-assert the constant values |
| A2 | The datasheet bridge from "code aborts unless `get_data(0x5555)==0x20`" to "aborts on real silicon" rests on DS20006432B §6.6.2 / DS20006386B p.10, carried from `SUMMARY.md` — **I did not read the PDFs in this session** | F1, TRACE-06 | Medium-**scoped**. If the citation were wrong, the INIT-abort software finding still stands unchanged; only the silicon inference weakens. `116-PREMISE.md` must present it as a citation, not an observation. CONFLICT 1's prerequisite ("acquire/confirm the AT28C64B + doc0270 PDFs") is **not** discharged by this research |
| A3 | `tBLC` = 100 µs (Xicor/Catalyst floor) rather than Atmel's 150 µs | not load-bearing here | None for Phase 116 (no timing requirement). Matters in Phase 118 (OBS-03) |
| A4 | Recording `rurp_set_data_output`/`rurp_set_data_input` direction edges would be *useful* (F5's closing observation) — I did not measure whether the direction difference is behaviourally significant | F5 | Low. It is a recommendation to widen D-07 slightly, explicitly flagged for planner acceptance. Declining it costs nothing this phase |
| A5 | `AT28C010`/`AT28C040` being capped at `address_mask == 0xFFFF` is a pre-existing defect rather than intentional | CORRECTION 3 note | Low, and out of scope. Recorded as an observation only; no requirement depends on it |
| A6 | Suite/directory names, flag name, buffer size 512, and entry layout are recommendations within Claude's Discretion, not verified-optimal | §Architecture Patterns, F3 | None — explicitly discretionary. 512 was chosen for ~10× headroom on the measured 54-entry window |

**Everything else in this document is `[VERIFIED]` by execution in this session.** The four
CORRECTIONs, the F1–F10 findings, all stream contents, all per-pinout `bus_config` values, the
84-chip DB facts, the 80/80 baseline, the 80/80-with-extension result, and the branch topology were
each produced by running a command and reading its output.

---

## Open Questions

1. **Does the DIP32 stale-upper-address case need a specific prior operation, or can it be seeded
   directly?**
   - What we know: the divergence requires CONTROL bits `0x10`/`0x20` HIGH before the SDP sequence.
     `reset_register_cache(lsb, msb, ctrl)` can seed it directly, and the fixed path provably clears
     them (`(0x5555 >> 16) & 0x71 == 0`).
   - What's unclear: whether a reviewer will accept a directly-seeded cache as representative, or
     want it produced by an actual preceding high-address `memory_get_data` call.
   - Recommendation: **seed directly, and add one case that reaches the same state via a real
     preceding read** — the second case costs ~10 lines and forecloses the objection. Document in
     `RED-BASELINE.md` which mechanism produced the state.

2. **Should TRACE-02 assert the full ~6057-entry stream or the 54-entry SDP prefix?**
   - What we know: the SDP window is entries 0–53; the rest is timeout-poll noise; overflow drops
     the tail.
   - What's unclear: whether "the exact ordered stream `eeprom28c_write_init` emits" (TRACE-02's
     wording) is satisfied by a prefix assertion.
   - Recommendation: **prefix**, plus an explicit assertion that entries 54+ contain no further
     `DATA` strobe with a value in `{0xAA, 0x55, 0x80, 0x20}` — that closes the "did a seventh
     command write sneak in?" gap without pinning 6000 poll edges. State the choice in
     `RED-BASELINE.md`.

3. **Where does the anti-drift guard for the test-local `EEPROM_SDP_DISABLE` copy live?** (F6)
   - What we know: the production table has internal linkage, so a local copy is unavoidable; an
     unguarded copy is a transcription that can stale.
   - Recommendation: a host-side pytest scanning `eeprom_28c.cpp:26-33` for the six literal pairs,
     sharing the D-11 cross-repo skipif machinery. Cheap; resolves a real gap CONTEXT.md does not
     name.

4. **Is `test_eeprom28c_chip_id`'s directory retired, or emptied?** D-12 says "the old directory
   retired". It is currently parked out of `test_filter` (D-13 debt) alongside
   `test_flash_intel_vpp`.
   - Recommendation: delete the directory **and** its `test_filter`/`-I` lines if present
     (verify: it is *not* in `test_filter` today, but it *may* have an `-I` entry — check both), and
     leave the `test_flash_intel_vpp` half of the KNOWN-FLAKY comment block intact with a note that
     the `eeprom28c` half migrated in Phase 116. Removing the whole comment would erase live debt
     documentation for the remaining suite.

5. **Not resolved by this research: the CONFLICT-1 datasheet prerequisite.** The
   `SUMMARY.md` §Research Flags note that Phase 116 "carries the acquire/confirm the AT28C64B +
   doc0270 PDFs prerequisite" is **still open** (A2). `firestarter_app/datasheets/AT28C256.pdf` is
   reported in-tree with a known notes-2/3 copy-paste error; doc0270 is the citation of record and I
   did not confirm its presence.
   - Recommendation: a small verification task — confirm which PDFs are actually in the tree and
     record their absence explicitly if they are not. It costs minutes and it is the only
     LOCK-01 prerequisite that Phase 116 was asked to carry. **It does not block any other
     TRACE requirement.**

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | native test suite (all TRACE reqs) | ✓ | 6.1.19 | — |
| Unity | assertions | ✓ | 2.6.1 (auto-installed) | — |
| ArduinoFake | D-05 mocks (mandatory) | ✓ | ^0.4.0 in `lib_deps` | — |
| g++ / gnu++17 | host cross-compile | ✓ | system gcc | — |
| Python 3 | D-11 generator, TRACE-05 | ✓ | **3.12.13** | — |
| pytest | drift gate, DB invariant | ✓ | 9.1.1 | — |
| ruff | GATE-03 lint/format | ✓ | 0.15.20 | — |
| `firestarter_app` importable (`database.py`) | D-08 generator | ✓ | verified by executing `convert_to_programmer` | — |
| Both sub-repo checkouts side by side | D-11 cross-repo gate | ✓ | meta work-tree | `FW_ABSENT` skipif |
| **AT28C silicon** | nothing in this phase | ✗ | — | **N/A by design** — validation ceiling; no Phase-116 requirement needs it |
| doc0270 / DS20006432B PDFs | A2 / CONFLICT-1 prerequisite only | **unconfirmed** | — | Record UNVERIFIED per §Open Question 5 |

**Missing dependencies with no fallback:** none — every TRACE-01…TRACE-06 requirement is fully
executable on this machine today (demonstrated).

**Version caveats:**
- Devcontainer Python is **3.12.13**; CI targets **py3.9/3.11**. `ruff check` and
  `ruff format --check` must be validated against the CI target, not 3.12 — a recorded recurring
  trap in this project.
- `/workspaces/platformio.ini` is untracked and **malformed** (duplicate `[platformio]` section,
  line 26), so `pio` from the meta root fails. Run `pio` from `firestarter/`.

---

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json` → treated as **enabled**.

### Test Framework

| Property | Value |
|---|---|
| Framework (firmware) | Unity 2.6.1 via PlatformIO 6.1.19, `platform = native` |
| Framework (host) | pytest 9.1.1 |
| Config file | `firestarter/platformio.ini` §`[env:native]` · `firestarter_app/pyproject.toml` |
| Quick run (firmware) | `cd firestarter && pio test -e native -f "*test_sdp_harness*"` (~2–5 s) |
| Quick run (host) | `cd firestarter_app && python -m pytest tests/test_sdp_db_invariant.py tests/test_sdp_bus_config_drift.py -x` (~2 s) |
| Full suite (firmware) | `cd firestarter && pio test -e native` — **baseline 80/80, ~24–40 s** |
| Full suite (host) | `cd firestarter_app && python -m pytest -x` |

### Phase Requirements → Test Map

| Req | Behaviour | Type | Automated command | File exists? |
|---|---|---|---|---|
| TRACE-01a | Ordered stream interleaves data bytes, latch strobes and CE/OE | unit | `pio test -e native -f "*test_sdp_harness*"` | ❌ Wave 0 |
| TRACE-01b | Flag-off is byte-exact — all pre-existing suites unchanged | regression | `pio test -e native` → **80/80** | ✅ exists (F7 proven) |
| TRACE-02 | Ordered `(LSB,MSB,data,CE)` stream pinned per pinout, RED today | unit (parked) | `pio test -e native -f "*test_eeprom28c_sdp*"` **after** adding the `test_filter` line — Phase 117 | ❌ Wave 0 |
| TRACE-03a | Unlock table mutated to `0x10` → different stream | unit | `pio test -e native -f "*test_sdp_harness*"` | ❌ Wave 0 |
| TRACE-03b | Lock table swapped for write prefix → different stream | unit | same | ❌ Wave 0 |
| TRACE-03c | Planted `LOG_` in timing window → scan fails | unit (host) | `pytest tests/test_no_log_in_sdp_window.py -x` | ❌ Wave 0 |
| TRACE-03d | `protocol != 0x0D` → `configure_not_implemented()` / `0xBB` | unit | `pio test -e native -f "*test_not_implemented*"` | ✅ extend existing |
| TRACE-04a | Address-keyed mock replaces call-ordered mock | unit | `pio test -e native -f "*test_sdp_harness*"` | ❌ Wave 0 |
| TRACE-04b | No `s_mock_bytes[n] = 0x20` fixture survives (3 sites) | structural | grep gate or host pytest over the migrated suites | ❌ Wave 0 |
| TRACE-05 | 84 × `algorithm==13` all `chip_id_check: false` **and** count == 84 | unit (host) | `pytest tests/test_sdp_db_invariant.py -x` | ❌ Wave 0 |
| TRACE-06 | INIT-abort premise settled + PROJECT.md corrected | doc + unit | `116-PREMISE.md` reviewed; evidence re-runnable via the RED suite | ❌ Wave 0 (**evidence already obtained** — F1) |
| D-10 | Generated header drift-gated | unit (host) | `pytest tests/test_sdp_bus_config_drift.py -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pio test -e native -f "*test_sdp_harness*"` (firmware tasks) /
  `pytest tests/test_sdp_*.py -x` (host tasks)
- **Per wave merge:** `cd firestarter && pio test -e native` (must stay **80/80** plus the new
  always-green suite's cases) **and** `cd firestarter_app && python -m pytest -x`
- **Phase gate:** both full suites green, plus `ruff check`/`ruff format --check` against the
  py3.9/3.11 CI target, plus `diff_db.py` identity proving the DB is untouched, before
  `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter/test/native/avr/_shared/host_stubs_common.inc` — extend with the CORRECTION 1
      guard set (TRACE-01)
- [ ] `firestarter/test/native/avr/test_sdp_harness/{host_stubs.cpp,test_sdp_harness.cpp,sdp_expected.h}`
      — always-green suite (TRACE-01, TRACE-03a/b, TRACE-04)
- [ ] `firestarter/test/native/avr/test_eeprom28c_sdp/{host_stubs.cpp,test_eeprom28c_sdp.cpp,sdp_expected_fixed.h,RED-BASELINE.md}`
      — parked RED suite (TRACE-02, TRACE-06 evidence)
- [ ] `firestarter/test/native/avr/_shared/sdp_bus_config.h` — generated, `DO NOT EDIT` (D-08)
- [ ] `firestarter/platformio.ini` — `test_filter` + `-I` for the always-green suite **only**;
      `-I` (not `test_filter`) for the parked suite, with the named `TODO(v1.22 Phase 117)`
- [ ] `firestarter_app/tools/gen_sdp_bus_config.py` (D-08/D-11)
- [ ] `firestarter_app/tools/check_no_log_in_sdp_window.py` + planted fixture (TRACE-03c)
- [ ] `firestarter_app/tests/test_sdp_bus_config_drift.py` — `FW_ABSENT` skipif (D-11)
- [ ] `firestarter_app/tests/test_sdp_db_invariant.py` — **no** skipif (TRACE-05, F9)
- [ ] `.planning/phases/116-.../116-PREMISE.md` (TRACE-06, D-14)
- [ ] `.planning/PROJECT.md` — third ⚠ correction block (D-14), carrying CORRECTION 4's *66 of 84*
- [ ] **Setup task:** create `v1.22-...` branch off `beta` in **both** sub-repos (F10)

No framework install is needed — everything is present.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as **enabled**.

This phase adds **no** runtime surface: no wire protocol change, no new command, no network
listener, no parsing of untrusted input, no privilege boundary. It adds host-side test/tooling code
and firmware **test** code that is compiled only into `[env:native]` (never into `env:uno` /
`env:leonardo`, whose `src_filter` excludes `test/`).

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No authn surface in this phase |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | No access-control decision is added or changed |
| V5 Input Validation | **partially** | The D-04/TRACE-03c source-scan checker reads a path from an env var (`FIRESTARTER_SDP_SRC`). Must **fail closed** if the path is absent or unreadable — never silently pass. Mirror `check_devtest_orchestrator.py`'s handling |
| V6 Cryptography | no | No crypto. Never hand-roll if that changes |
| V10 Malicious Code | **yes (relevant)** | The generated header is executable input to a firmware test build. It must carry the `DO NOT EDIT` banner **and** be drift-gated (D-10) so a hand-edit cannot silently redefine ground truth. This is the anti-hollow control, applied as a supply-chain control |
| V14 Configuration | **yes** | New dependencies: **none** (§Package Legitimacy Audit). The `-D HARDWARE_REVISION` inheritance is the mechanism behind CORRECTION 1 — a build-config coupling worth a comment in the `.inc` |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| Hollow gate — a scan/trace that cannot fail | **Tampering** (defeats a control) | Planted-violation fixture proving the gate fails (TRACE-03, project-mandated since the v1.12 hollow-GATE-03 debt) |
| Generated artifact hand-edited to hide drift | **Tampering** | `DO NOT EDIT` banner + regenerate-and-diff CI gate (D-10) |
| Env-var path override used to bypass a checker | **Tampering / Elevation** | Fail closed on missing path; the override exists only so the paired pytest can point at a fixture, and the default must be the real source |
| Test code leaking into a production build | **Elevation** | Already structurally prevented: production `src_filter` excludes `test/`. Assert it stays true — a `pio run -e leonardo` build is the check |
| Overclaimed safety evidence (a trace read as silicon proof) | **Repudiation** | The validation ceiling. This is the highest-likelihood *actual* harm in this phase: an honest-looking artifact asserting more than it proved. §Pitfall 7 and §F1's wording are the control |

**No `checkpoint:human-verify` gate is required for dependencies.** One is worth considering for
`116-PREMISE.md`'s claim wording (D-14 edits PROJECT.md, which six downstream phases read).

---

## Sources

### Primary — code executed and observed in this session (HIGH)
- `pio test -e native` — baseline run (80/80, 14 suites); with-extension run (80/80); probe suite
  compile failures and successes
- `./.pio/build/native/firestarter_native` — direct binary execution for the full strobe dumps
  (F4, F5), the TRACE-06 response codes (F1) and the D-12 migration matrix (F8)
- `EpromDatabase.convert_to_programmer` (`firestarter_app/firestarter/database.py`) — executed for
  `AT28C256`, `AT28C64`, `AT28C16`, `AT28C010`, `AT28C040`, `SST39SF040`
- `firestarter_app/firestarter/data/chip_database.json` — parsed for the 84-chip facts (F9)
- `firestarter_app/firestarter/data/pinouts.json` — parsed for the four pinout definitions and the
  `static-high-pins` absence (SDP-F8 corroborated)
- `git merge-base --is-ancestor` in both sub-repos (F10)

### Primary — in-tree source read directly (HIGH)
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` (:41-81 recording contract, :98
  data-buffer no-op, :125-141 HARDWARE_REVISION block)
- `firestarter/include/rurp_register_utils.h` (:12-14 cache globals, :24-60 elision, :63-89 strobe
  sequencing, :91-101 cached read)
- `firestarter/include/rurp_hw_rev_utils.h` (:13, :15, :43, :61, :100 — the four colliding
  definitions)
- `firestarter/include/rurp_shield.h` (:53-57 pin namespace, :104-111 chip-control macros)
- `firestarter/include/firestarter.h` (:75-82 `bus_config_t`)
- `firestarter/include/flash_utils.h` (:15-16 `flash_execute_command` macro, :19-22 `byte_flip_t`)
- `firestarter/src/proms/eeprom_28c.cpp` (:19 `PAGE_SIZE`, :26-33 SDP table, :97-117 `write_init`,
  :119-133 `write_execute`, :135-155 `wait_for_write`)
- `firestarter/src/proms/flash_utils.cpp` (:20-27 `byte_flipping`, :52-59 `flip_data`, :61-66
  `fast_address`)
- `firestarter/src/proms/memory.cpp` (`configure_memory`, :224-234 `memory_set_data`, `memory_get_data`,
  `mem_util_set_address`, `mem_util_calculate_*_register`, :258-282 `mem_util_remap_address_bus`)
- `firestarter/src/json_parser.c` (:84-88 defaults, :197-243 `parse_bus_config`, :317-321 rw/vpp)
- `firestarter/include/memory_utils.h` (:14-15 `WRITE_FLAG`/`READ_FLAG`)
- `firestarter/include/rurp_pinout.h` (:76-93 `CTRL_ADDRESS_LINE_*`)
- `firestarter/platformio.ini` §`[env:native]`
- `firestarter/test/native/avr/test_val_eeprom28c/{test_val_eeprom28c.cpp,host_stubs.cpp}`
- `firestarter/test/native/avr/test_eeprom28c_chip_id/test_eeprom28c_chip_id.cpp` (:104, :140, :160)
- `firestarter/test/native/avr/_shared/validation_matrix.h` (:1-2 banner)
- `firestarter_app/tools/gen_validation_header.py`, `firestarter_app/tests/test_gen_validation_header.py`
  (:20-41 paths + `FW_ABSENT` shape, :53-59 banner assertion)
- `firestarter_app/tests/test_revision_constants_parity.py` (original skipif idiom)
- `firestarter_app/tools/check_devtest_orchestrator.py` (:86 `FIRESTARTER_DEVTEST_SRC` seam)

### Primary — upstream planning documents (context, not evidence)
- `.planning/phases/116-ground-truth-trace-harness/116-CONTEXT.md` — D-01…D-14, discretion, deferrals
- `.planning/REQUIREMENTS.md` — TRACE-01…06 verbatim, Locked decisions, §Validation Ceiling
- `.planning/research/SUMMARY.md` — 4-stream synthesis; CONFLICT 1/2/3, Critical Pitfalls 1–6,
  PROVEN vs PREDICTED, Findings 1–13
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter/CLAUDE.md`
- `.planning/config.json`

### Secondary (MEDIUM) — carried forward, not re-verified here
- Microchip **DS20006432B** (AT28C64B) §6.6.2 p.10, §6.18/§6.19 — the "data is not written to the
  device" statement and the `1555h`/`0AAAh` pair. **Via `SUMMARY.md`; PDFs not read this session
  (A2).** The truncation half was independently confirmed by executing the remap (F5)
- Microchip **DS20006386B** (AT28C256) p.10 — same statement
- Atmel **doc0270** rev `0270L–PEEPR–2/09` §19 note 2 — CONFLICT 1's citation of record.
  **Presence in-tree unconfirmed** (Open Question 5)

### Tertiary / negative results (LOW)
- `firestarter/tools/gen_validation_header.py` — **does not exist**; CONTEXT.md's canonical-refs path
  is wrong (the generator is host-side). D-11's decision is unaffected
- `firestarter/src/primitives.cpp`, `include/primitives.h` — **do not exist**; confirmed absent
- `/workspaces/platformio.ini` — untracked, malformed, breaks `pio` from the meta root

---

## Metadata

**Confidence breakdown:**
- **Standard stack — HIGH.** Zero new dependencies; every version read from the installed tool.
- **Architecture / harness design — HIGH.** The design was compiled, linked and executed; the
  byte-exactness criterion was demonstrated (80/80).
- **Ground truth (streams, per-pinout divergence, `bus_config`) — HIGH.** Produced by running the
  real `configure_memory` / `flash_util_byte_flipping` / `memory_set_data` / `mem_util_remap_address_bus`
  code against host-derived configs, then hand-checked against the address arithmetic.
- **TRACE-06 INIT-abort — HIGH at the software layer, MEDIUM as a silicon inference** (A2). The
  software result is measured; the bridge to silicon is a carried citation.
- **DB facts (TRACE-05) — HIGH.** Counted directly.
- **Pitfalls — HIGH.** Five of the seven were *encountered* in this session, not predicted.
- **Corrections 1–4 — HIGH.** Each is a reproduced compile error, test result, or measured value.
- **`tBLC` / datasheet PDFs — MEDIUM/UNVERIFIED**, and not load-bearing for any Phase-116
  requirement.

**Probe hygiene:** all experimental edits (`host_stubs_common.inc`, `platformio.ini`, the scratch
suite directory) were reverted. `git status --short` in `firestarter/` is **empty**;
`git diff --stat` is **empty**. Backups were taken before each edit and restored from.

**Research date:** 2026-07-27
**Valid until:** ~2026-08-26 (30 days). Stable — the findings are properties of in-tree code, not of
a moving external ecosystem. Re-verify if `pinouts.json`, `rurp_register_utils.h`,
`host_stubs_common.inc`, `flash_utils.cpp` or `memory.cpp` changes, or once the v1.22 sub-repo
branches are forked off `beta` (which will move the base commit but not, by itself, any finding).
