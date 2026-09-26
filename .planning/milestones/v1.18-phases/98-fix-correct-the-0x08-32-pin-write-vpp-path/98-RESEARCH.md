# Phase 98: FIX — Correct the 0x08 32-Pin Write/VPP Path - Research

**Researched:** 2026-06-30
**Domain:** Firmware (Arduino C++ / RURP control register) + host (Python pinout/DB pipeline) — a blind, no-bench fix to the `0x08` EPROM-QUICK 32-pin write/VPP path
**Confidence:** HIGH on code seams + mechanism (all read direct, file:line, this session); MEDIUM on whether the fix moves the physical pin-31 signal (the residual that only Phase-99 silicon resolves — D-01/verifier caveat)

---

<user_constraints>
## User Constraints (from 98-CONTEXT.md)

### Locked Decisions
- **D-01 (Belt-and-suspenders):** Implement the named RCA hand-off surfaces (new `DIP32_27C020` pinout redirecting pin 31 to a PGM concept + hold `CTRL_VPP_P1_ENABLE` / P1 route across the **full** program-pulse window, not only the per-byte data-write window) **PLUS an explicit firmware PGM-pulse/program-sequence change** so pin 31 is a *deliberately asserted* control during the CE pulse — not merely coincidentally-VIL via the address bus. Accepted cost: touches the shared program pulse → D-05 regression discipline + D-04 alias guard become hard constraints.
- **D-02 (Pin-31 redirect scoping):** New `DIP32_27C020` pinout class (`pinouts.json` + `database.py`), assigned **only** to the `0x08` ≤256K-class chip(s). 27C040 (A18) and SST39SF040 (WE) stay on their existing pinouts, untouched. Reviewable via `diff_db.py` showing only the intended rows.
- **D-03 (Wire-field appetite):** DB/pinout-only if possible. A new wire field (`firestarter.h` ↔ `constants.py` lockstep, à la v1.17 `page_size`) is allowed **only if** the belt-and-suspenders PGM-assert genuinely cannot be expressed via the new pinout mapping + a protocol-`0x08`-gated firmware branch using existing `CTRL_*` bits. D-01 and D-03 pull against each other — try pinout+protocol-gate first, escalate to a wire field last.
- **D-04 (BLOCKING — alias-collision guard):** On Rev 2.0, `CTRL_VPP_P1_ENABLE_REV2` and `CTRL_ADDRESS_LINE_18_REV2` are the SAME physical bit (`0x08`) (`rurp_pinout.h:121`/`:128`). Holding P1/asserting PGM via this bit is safe for 256K AM27C020 (A18 never set) but corrupts A18 on 512K 27C040. The fix MUST be gated so the PGM/P1-hold cannot leak to any A18 user (≥512K / 27C040 class).
- **D-05 (Regression & test posture):** v1.16 golden register traces + dispatch-mirror guard stay **byte-identical** for the passing `0x07` and `0x0B` paths. Where a `0x08` 32-pin trace legitimately changes, re-pin with cited rationale. Native tests cover the corrected `0x08` write path AND include ≥1 explicit failure-case/mismatch test (P89 CR-01 lesson). The `0x07`/`0x0B` trace-identity check is the primary regression tripwire.
- **D-06 (SAFE-02):** Over-voltage stays ERROR-blocked (`vpp_check_window` HIGH→ERROR, no `FLAG_FORCE` relaxation); host `chip_resolver.resolve_chip` guard never bypassed; no test-only escape hatch. Host CI green on py3.11 (ruff check + ruff format --check + mypy + diff_db + check_dispatch) — avoid py3.12-masks-CI-3.11 trap.

### Claude's Discretion
- **Phase-99 decisiveness instrumentation (you decide):** whether the fix should expose/log the actual pin-31 (PGM) + P1 control-register state during the program window (held-rail-checkable) so Phase 99 can separate "path now correct but chip OTP/dead" from "still broken." Add only if worth the surface; otherwise rely on Phase 99's DMM + write→verify + held-rail proxy.
- Within D-01–D-06: the concrete firmware sequencing for the PGM assert, exact `CTRL_*` composition, the held-rail control-register value used to validate the static pin-31 state, and the precise gate predicate (protocol `0x08` + 32-pin + size/A18-unused) are planner/researcher choices.

### Deferred Ideas (OUT OF SCOPE)
- **Phase 99 bench graduation** — byte-exact write→verify on the seated AM27C020, EVIDENCE record, PROTOCOL-LEDGER `0x08` update, D-06 OTP/dead verdict — all Phase 99, gated on PRE-01.
- **FUT-05** (REWR-02 `0x08` rewritable write proof, W27E040 stuck-bit) — separate deferred requirement, not v1.18 scope.
- **None of the 5 pending todos folded** — none touch the `0x08` write-path fix.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FIX-01 | Firmware/host `0x08` write path corrected so AM27C020 program pulse flips bits (PGM/pin 31 driven program-active and/or P1 routing corrected) — no regression to `0x07`/other EPROM paths. | Mechanism map below: the firmware ALREADY routes `CTRL_VPE_ENABLE`→`CTRL_VPP_P1_ENABLE` for 0x08-32-pin (`eprom.cpp:320-326`), held across the whole `program_mismatched_bytes` window. Pin 31 = address bus line 22 = CONTROL-reg bit 6 (`CTRL_READ_WRITE`/0x40). The deliberate-PGM-assert seam + the host pinout redirect are both identified. |
| FIX-02 | v1.16 golden register traces + dispatch-mirror guard green for passing paths; legitimately changed `0x08` traces re-pinned with cited rationale; native tests cover corrected `0x08` path + a failure-case/mismatch test. | Golden traces live at `firestarter/test/native/avr/test_val_eprom/golden_eprom_0x0{7,8,B}_write.inc`; bless mode + harness shape fully documented below. Existing `test_inv03_eprom_0x08_p1_as_vpp` + WR-02a/b/c mismatch tests are the precedent. |
| FIX-03 | Fix delivered dual-repo lockstep wherever it crosses the wire (`constants.py` ↔ `firestarter.h`; `DIP32_27C020` pinout entry in DB/pinout pipeline). Native + host tests green. | `DIP32_27C020` entry shape mirrors `DIP32_SST39SF040`; `database.py` `pin_conversions[32][31]` change identified; wire-field lockstep precedent (`page_size`) mapped if D-03 escalates. |
| SAFE-02 | Host CI green on py3.11 (ruff check + ruff format --check + mypy + diff_db + check_dispatch); constants/wire parity in sync if fix crosses the wire. | Exact py3.11 invocation + py3.12-masks-3.11 workaround named below. |
</phase_requirements>

## Summary

Phase 98 fixes the AM27C020 0-bits-programmed fault blind, per the Phase-97 confirmed root cause RC-1 (pin 31 modeled as address line A18 instead of a held PGM control; CE-only program pulse). The single most important finding from reading the current firmware directly: **the firmware does NOT strobe CE with pin 31 inert in the way a naive reading of RC-1 might suggest.** For a 0x08 / 32-pin part with `using_p1_as_vpp(handle)==true`, `eprom_internal_set_control_register` (`eprom.cpp:320-326`) already rewrites the program-enable bit `CTRL_VPE_ENABLE`→`CTRL_VPP_P1_ENABLE` (`0x08`), and `program_mismatched_bytes` (`eprom.cpp:168-180`) already holds that bit asserted across the *entire* per-buffer program window (set before the byte loop, cleared after). So the "hold P1 across the full program window" suspenders half of D-01 is **largely already in place** at the per-buffer level. The residual gaps are: (a) it is held per *data buffer*, not per *byte CE pulse*; and (b) **pin 31 itself** (socket PGM) is a different signal from the P1/pin-1 VPP route.

The decisive mechanism fact: pin 31 maps via the host `DIP32_STD` pinout (`pin_conversions[32][31] = 22`, `database.py:141`) to **address bus line 22**. The RURP address bus is composed as LSB latch = lines 0-7, MSB latch = lines 8-15, and the **CONTROL_REGISTER** carries the upper address/control bits (lines 16-23). Bit 22 of the address = bit 6 of the CONTROL register = `CTRL_READ_WRITE` (`0x40`) on the Rev 2.0 layout. At address `0x000000` (the failing address), `mem_util_remap_address_bus` clears line 22, so pin 31 is driven to whatever CONTROL-reg bit 6 holds — i.e. VIL during a write (R/W bit context). This is exactly the verifier's caveat: on a 256K part pin 31 is *coincidentally* at the program-active level, yet 0 bits program. The architectural defect (pin 31 modeled as an address line, not a deliberately-driven PGM control) is real even where the level is right.

**Primary recommendation:** Two-surface, protocol-and-size-gated fix. (1) Host: add a `DIP32_27C020` pinout (mirror `DIP32_SST39SF040`'s scoped-variant shape) that moves pin 31 out of `address-bus-pins` into a non-address role, and reassign **only the ≤256K 0x08 chips** (AM27C020 + 27C020-class) to it via `chip_database.json` — leaving 512K/1M (AM27C040/AM27C080, A18-bearing) on `DIP32_STD`. (2) Firmware: a protocol-`0x08` + 32-pin + A18-unused-gated branch that deliberately drives pin 31 (PGM) program-active (= **VIL**, held LOW across the per-byte CE pulse in `memory_set_data`, `memory.cpp:346`), composed from existing `CTRL_*` bits. The PGM-assert vehicle is the firmware hold-LOW branch (NOT `static-high-pins`), per the now-resolved Q1/Q2 below. **The hard blocker is D-04:** there are **127 chips on protocol 0x08 / DIP32_STD across 128K/256K/512K/1M** — a fix gated on "0x08 + 32-pin" alone would corrupt the 512K+ A18 users. Scope must be size-keyed (≤256K) or pinout-keyed (only chips reassigned to `DIP32_27C020`).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Pin-31 role decision (PGM vs A18) | Host DB/pinout (`pinouts.json` + `chip_database.json` + `database.py`) | Firmware bus-config consumer | RC-1 primary classification is host-pinout; the role is data-driven and must NOT be hardcoded in firmware (CONTEXT Integration Points) |
| Deliberate PGM assert during CE pulse | Firmware (`memory.cpp` / `eprom.cpp`) | — | The program-pulse model lives in firmware; the secondary firmware-algorithm half of RC-1 |
| P1/VPP routing across pulse window | Firmware (`eprom.cpp:320-326` + `program_mismatched_bytes`) | — | Already implemented; "suspenders" extension is firmware-local |
| Alias-collision gate (0x08 bit must not reach A18 users) | Firmware (protocol+size gate) | Host (pinout scoping prevents reassignment) | Defense-in-depth: host scoping + firmware gate (T-93-CANERASE model) |
| Over-voltage block (SAFE-02) | Firmware (`primitives.cpp` `vpp_check_window`) | Host (`chip_resolver.resolve_chip`) | Unchanged invariant; both layers must stay intact |
| Regression tripwire (golden traces) | Firmware native test (`test_val_eprom.cpp`) | Host (diff_db/check_dispatch) | Byte-identical 0x07/0x0B traces + DB diff gate |

## Standard Stack

No new external packages. This is an in-repo firmware + host fix using the existing toolchains.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO | (installed) | Build + native Unity tests for firmware | `firestarter/CLAUDE.md` §Native Test Environment — `pio test -e native` is the harness |
| Unity | (via PlatformIO `test_framework=unity`) | Firmware native test framework | Existing `test_val_eprom` suite uses it |
| ArduinoFake / fakeit | (via PlatformIO) | Mock `delay`/`Serial` in native tests | Used in `test_val_eprom.cpp:61,100-110` |
| ruff | (pinned in pyproject `[dev]`) | Host lint + format gate | CI gate (SAFE-02) |
| mypy | 2.1.0 (per `pyproject.toml:111`) | Host strict type gate on 8 modules | CI gate; `python_version = "3.9"` set in config file |
| pytest | (pinned `[test]`) | Host unit tests + `--cov-fail-under=70` | CI gate |

### Supporting (in-repo guard scripts)
| Script | Path | Purpose | When to Use |
|--------|------|---------|-------------|
| `check_dispatch.py` | `firestarter_app/tools/check_dispatch.py` | Dispatch-mirror + VPP-hazard + WARNING-5 guard | After any pinout/DB change (D-05 tripwire) |
| `diff_db.py` | `firestarter_app/tools/diff_db.py` | Per-chip diff vs pinned baseline (`tools/baseline/chip_database.baseline.json`) | After regenerating `chip_database.json` (D-02 review surface) |
| `build_db.py` | `firestarter_app/tools/build_db.py` | Regenerate `chip_database.json` from `infoic.xml` | If pinout assignment is done at DB-generation time |
| golden bless | `pio test -e native -f "*test_val_eprom*"` + `-DGOLDEN_BLESS` | Re-pin golden traces | Only for the legitimately-changed 0x08 trace (D-05) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| New `DIP32_27C020` pinout (D-02) | Reuse `DIP32_STD` + firmware-only protocol/size gate | Rejected by D-02: host pinout is the RC-1 primary fix surface and must be data-driven, not firmware-hardcoded |
| Express PGM-assert via existing `CTRL_*` bits (D-03 preferred) | New wire field (`firestarter.h` ↔ `constants.py`) | D-03: wire field only as last resort. **RESOLVED (Q2): no new wire field needed** — the firmware hold-LOW branch keyed on existing `protocol`/`pins`/`mem_size`/`bus_config` fields suffices. |
| Express PGM-assert via `static-high-pins` (`static_high_mask`) | Firmware gated hold-LOW of line 22 in `memory_set_data` | **RESOLVED (Q1): `static-high-pins` is RULED OUT** — `static_high_mask` ORs a 1 (HIGH) into line 22 with no inversion (`memory.cpp:402` → CONTROL bit 6 → `rurp_internal_write_to_register` latches bit-for-bit, `rurp_register_utils.h:54,63-89`); PGM program-active is VIL (LOW). HIGH ≠ PGM=VIL, so static-high cannot express the assert. The firmware hold-LOW branch is the vehicle. |
| Edit `chip_database.json` AM27C020 row by hand | Regenerate via `build_db.py` + per-chip override | `chip_database.json` is generated ("do NOT edit by hand", `firestarter_app/CLAUDE.md`). `build_db.py resolve_pinout_key` (`:281-296`) is a pure function of decoded fields incl. `mem_size`, so a ≤256K-keyed arm is expressible at generation time (A1 **CONFIRMED** by PATTERNS — no override needed). |

## Package Legitimacy Audit

Not applicable — this phase installs no external packages. All tools (PlatformIO, ruff, mypy, pytest) are already pinned in the repos and exercised by existing CI.

## Architecture Patterns

### System Architecture Diagram — the 0x08 32-pin write path (current)

```
HOST (firestarter_app)
  chip_database.json  AM27C020 → pinout="DIP32_STD", algorithm=8, pin_count=32, vpp_mv=13000
        │
        ▼
  database.get_eprom() → _map_data() → get_bus_config(32, "DIP32_STD")
        │   pinouts.json: vpp-pin=[1], address-bus-pins=[...,30,31]  (pin 31 in address bus)
        │   pin_conversions[32]:  pin 1→line 21,  pin 31→line 22,  pin 30→line 20
        ▼
  convert_to_programmer() → wire dict:
        bus-config={ bus:[...,20,22], vpp-pin:21 }, algorithm=8, vpp_mv=13000, pulse-delay=100
        │  (serial 250000 baud, JSON)
        ▼
FIRMWARE (firestarter)
  json_parser → handle{ protocol=0x08, pins=32, bus_config.vpp_line=21(=VPP_P1_32_DIP) }
        │
        ▼
  configure_memory() [memory.cpp:121]  protocol∈{07,08,0B} → configure_eprom()
        │   using_p1_as_vpp(handle)==TRUE  (pins==32 && vpp_line==VPP_P1_32_DIP)  [memory_utils.h:24]
        ▼
  CMD_WRITE: eprom_write_init → eprom_generic_init → eprom_check_vpp
        │   sets CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE, vpp_check_window, clears  [eprom.cpp:263-282]
        ▼
  eprom_write_execute [eprom.cpp:197]
        │   re-asserts REGULATOR|VPE_DROP, delay(500)
        ▼
  program_mismatched_bytes [eprom.cpp:168]   ← THE PROGRAM WINDOW
        │   programming_bits = CTRL_VPE_ENABLE
        │   set_control_register(programming_bits,1)   ← intercepted by eprom_internal_set_control_register:
        │        using_p1_as_vpp → strips CTRL_VPE_ENABLE, sets CTRL_VPP_P1_ENABLE(0x08)  [eprom.cpp:320-326]
        │        ── P1 bit HELD across the whole byte loop ──
        │   for each mismatched byte:  firestarter_set_data → memory_set_data [memory.cpp:346]
        │        set_address(remap(addr))  ← pin 31 = line 22 driven by ADDRESS bit, not held PGM
        │        write_data_buffer(data); delayMicroseconds(3)
        │        rurp_chip_enable() (CE low); delayMicroseconds(pulse_delay=100); rurp_chip_disable()
        │   set_control_register(programming_bits,0)   ← clears P1 after loop
        ▼
  verify_and_update_mask → retry up to 20×  →  0 bits flipped  →  ERROR "bad bytes, retries 20"
```

**Where the fix lands (per RC-1 + D-01):**
1. **Host pinout (RC-1 primary):** move pin 31 out of `address-bus-pins` in a new `DIP32_27C020`, so the firmware bus-config no longer drives line 22 from an address bit. Reassign only ≤256K 0x08 chips. (Pin 31's PGM program-active assert is NOT expressed in the pinout — see Q1 RESOLVED — it is the firmware's job below.)
2. **Firmware PGM assert (RC-1 secondary, D-01 belt):** in the per-byte pulse (`memory_set_data`) or in `program_mismatched_bytes`, deliberately drive pin 31's bus line to the program-active level (= VIL, hold LOW; see Q1 RESOLVED) and hold it across the CE pulse, gated on protocol 0x08 + 32-pin + A18-unused.

### Key bus-line / register physical mapping (read direct — load-bearing)

- `rurp_write_to_register` (`rurp_register_utils.h:24`): `LEAST_SIGNIFICANT_BYTE`→lines 0-7, `MOST_SIGNIFICANT_BYTE`→lines 8-15, `CONTROL_REGISTER`→the `rurp_register_t` upper byte (lines 16-23 + control bits).
- Address bit 22 (pin 31 via `pin_conversions[32][31]=22`) therefore lands in the **CONTROL register, bit 6** = `CTRL_READ_WRITE` (`0x40`) on the Rev 2.0 layout (`rurp_pinout.h:82/94`).
- `mem_util_calculate_top_address_register` (`memory.cpp:187`) masks `address>>16` to `CTRL_ADDRESS_LINE_16|17|18|READ_WRITE` then ORs in preserved control bits. `mem_util_remap_address_bus` (`memory.cpp:381-404`) sets line 22 from address bit `i` only when that remap index is active. At addr 0, line 22 is cleared.
- **No inversion in the latch path:** `rurp_internal_write_to_register` (`rurp_register_utils.h:63-89`) → `rurp_write_data_buffer(data)` (e.g. `leonardo_rurp_shield.cpp:80-99`) maps each CONTROL-byte bit straight to a port pin — a `1` bit → physical HIGH, a `0` bit → physical LOW. No XOR/complement anywhere. (Load-bearing for Q1.)
- `CTRL_VPP_VPE_DROP_ENABLE` is `0x100` on Rev 2.0 (16-bit `rurp_register_t`) — **invisible in the 8-bit golden traces** (`golden_trace.h:19-24`). Only the low byte is recorded.
- **D-04 alias (read direct, `rurp_pinout.h:121,127`):** `CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08`. The host `dev reg -f` namespace presents them distinct (`0x008` P1, `0x020` A18) but the physical Rev2 bit is shared. Any PGM/P1-hold on this bit corrupts A18 for a 512K part.

### Pattern 1: Scoped DIP32 pinout variant (the D-02 precedent)
**What:** A sibling of `DIP32_STD` differing only in pin-1/pin-31 roles, assigned to a named chip family.
**When to use:** Pin 31 has a different function for one sub-family (here PGM for ≤256K 27C020-class).
**Example — `DIP32_SST39SF040` (the proven precedent, from `pinouts.json`):**
```json
"DIP32_SST39SF040": {
  "name": "JEDEC 32-pin 5V Flash (SST39SF040/AM29F040 family)",
  "pins": {
    "vcc-pin": [32], "gnd-pin": [16],
    "address-bus-pins": [12,11,10,9,8,7,6,5,27,26,23,25,4,28,29,3,2,30,1],
    "data-bus-pins": [13,14,15,17,18,19,20,21],
    "ce-pin": [22], "oe-pin": [24],
    "rw-pin": [31]
  }
}
```
Note `DIP32_SST39SF040` moves pin 31 OUT of `address-bus-pins` and into `rw-pin`, and moves A18 to pin 1 (no `vpp-pin`). The new `DIP32_27C020` follows the same *structural* move for pin 31 (take it OFF the address bus so it is no longer driven as A18) but keeps `vpp-pin: [1]` (27C020 has VPP on pin 1). **The PGM program-active assert is NOT expressed in the pinout** (see Q1 RESOLVED): `get_bus_config` understands `address-bus-pins`, `rw-pin`, `vpp-pin`, `static-high-pins` (`database.py:289-332`), and `static-high-pins` drives the line HIGH — the wrong polarity for PGM=VIL. So `DIP32_27C020`'s only job for pin 31 is to remove it from the address bus; the program-active hold-LOW is delivered by Plan 02's gated firmware branch.

### Pattern 2: Protocol-keyed defense-in-depth gate (T-93-CANERASE model)
**What:** Gate hardware-affecting behavior on `handle->protocol` in firmware AND mirror host-side.
**When to use:** The D-04 alias guard — PGM/P1-hold must never reach an A18 user.
**Example (the established model, from `database.py:617-630` convert_to_programmer FLAG_CAN_ERASE gate):** algorithm-keyed branch that excludes `algo==5` to avoid a 12V hazard. The Phase-98 analog: gate the PGM-assert on `protocol==0x08 && pins==32 && A18-unused`.
**Gate predicate (recommended concrete form):**
- Host side: only ≤256K 0x08 chips get `DIP32_27C020`. Structural exclusion — 512K/1M stay on `DIP32_STD`, so their bus-config never carries the PGM role.
- Firmware side: `handle->protocol == 0x08 && handle->pins == 32 && handle->mem_size <= 262144` (A18 is bit 18 = mask `0x40000`; "A18 unused" ⟺ `mem_size <= 0x40000`). This is the belt that catches a mis-built DB row even if host scoping fails.

### Anti-Patterns to Avoid
- **Gating on "0x08 + 32-pin" alone:** there are 127 chips on protocol 0x08 / DIP32_STD spanning 128K/256K/512K/1M (verified by DB scan). 512K (AM27C040) and 1M (AM27C080) use pin 31 = A18. A gate without a size/A18-unused term **corrupts A18** on those — the D-04 hazard. **Always include the ≤256K / A18-unused term.**
- **Holding the shared `0x08` bit (P1/A18) high during a high-address write:** for a 256K part A18 is never set so the alias is dormant, but any code that asserts `CTRL_VPP_P1_ENABLE` on a part where `mem_size > 0x40000` collides with A18.
- **Expressing PGM=VIL via `static-high-pins`:** ruled out by Q1 — `static_high_mask` drives HIGH, PGM is active-LOW. Use the firmware hold-LOW branch.
- **Hardcoding pin 31's role in firmware:** the role must flow from the host pinout/bus-config (CONTEXT Integration Points). Firmware reads it; it does not hardcode "pin 31 = PGM."
- **Re-blessing the 0x07 or 0x0B golden trace:** only the 0x08 trace may change. Re-blessing 07/0B masks a regression (D-05).
- **Editing `chip_database.json` by hand instead of via the pipeline** unless the pipeline genuinely cannot express the assignment (then document it).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pin-31 → bus-line redirect | A firmware special-case that rewrites the address | The host pinout + `pin_conversions` to take pin 31 OFF the address bus | The redirect is data-driven by design |
| Holding P1/VPP across the pulse | A new hold/release sequence | The existing `eprom_internal_set_control_register` rewrite (`eprom.cpp:320-326`) — already holds `CTRL_VPP_P1_ENABLE` across `program_mismatched_bytes` | The "suspenders" is already 90% built; extend, don't rebuild |
| Golden-trace capture | A bespoke recording mechanism | `GOLDEN_BLESS` mode + `assert_trace_eq` (`golden_trace.h`) | Existing bless workflow; recording-cap + low-byte caveats already handled |
| Failure-case test | A new mocking framework | The WR-02a/b/c mismatch-test pattern (`test_val_eprom.cpp:621-703`) | The P89 CR-01 lesson is already encoded as a reusable pattern |
| DB diff review | Manual JSON diff | `diff_db.py` against `tools/baseline/chip_database.baseline.json` | Per-chip cited-rule classification; CI gate |

**Key insight:** The fix is mostly *re-scoping and extending existing machinery*, not new mechanism. The P1-hold across the program window already exists for 0x08-32-pin; the missing pieces are (a) moving pin 31 off the address bus (host pinout) and (b) deliberately driving pin 31's line program-active (= VIL, hold LOW) and holding it across the per-byte CE pulse (firmware), both size-gated.

## Runtime State Inventory

This is a code/config fix, not a rename/migration. The only "stored state" concern is the generated DB:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `chip_database.json` (generated artifact) carries `AM27C020.pinout="DIP32_STD"` | Reassign to `DIP32_27C020` — via `build_db.py` regen if expressible, else documented override; re-baseline `diff_db.py` for the intended rows |
| Live service config | None — no external service holds the pinout string | None |
| OS-registered state | None | None |
| Secrets/env vars | None. (`FIRESTARTER_DB_FILE`/`FIRESTARTER_PINOUTS_FILE`/`FIRESTARTER_CONFIG_DIR` are test seams, not secrets) | None |
| Build artifacts | Firmware `.hex` (rebuilt by `pio run`); native test binaries (rebuilt by `pio test`); host `pip install -e .` egg-info | Rebuild firmware + re-run native tests; no stale-artifact migration needed |

**Nothing found requiring data migration** — the AM27C020 chip row is a static-DB pinout reassignment, not a stored-record rewrite.

## Common Pitfalls

### Pitfall 1: The "0x08 + 32-pin" gate corrupts 512K/1M A18 users (D-04 — BLOCKING)
**What goes wrong:** 127 chips share protocol 0x08 + DIP32_STD; 512K (AM27C040) and 1M (AM27C080) use pin 31 = A18. A PGM/P1-hold gated only on protocol+pin-count drives the shared `0x08` Rev2 bit on parts where it means A18, silently corrupting high-address writes.
**Why it happens:** `CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08` (`rurp_pinout.h:121,127`).
**How to avoid:** size-key the gate (`mem_size <= 262144` ⟺ A18 unused) AND structurally scope the host pinout so only ≤256K chips carry the PGM role. Defense-in-depth.
**Warning signs:** `diff_db.py` shows AM27C040/AM27C080 (or any 512K/1M row) changed pinout; the firmware gate lacks a size/mem_size term.

### Pitfall 2: Re-blessing the wrong golden trace
**What goes wrong:** Running `-DGOLDEN_BLESS` re-pins ALL four eprom traces; if you commit the regenerated 0x07/0x0B `.inc` files you mask a regression.
**Why it happens:** `print_trace_inc()` fires for every `test_golden_*` test under `GOLDEN_BLESS`.
**How to avoid:** Bless, then `git diff` and **revert** any change to `golden_eprom_0x07_write.inc` / `golden_eprom_0x0B_write.inc` / `golden_eprom_chip_id.inc`. Keep only the intended `golden_eprom_0x08_write.inc` change, with cited rationale in the `.inc` header comment.
**Warning signs:** `git diff` touches more than the 0x08 trace.

### Pitfall 3: `CTRL_VPP_VPE_DROP_ENABLE` (0x100) is invisible in the golden trace
**What goes wrong:** A change that affects only the 0x100 bit won't show in the 8-bit trace; conversely, you may expect a trace delta that never appears.
**Why it happens:** `rurp_write_to_register` stores `(uint8_t)data`; traces pin the low byte only (`golden_trace.h:19-24`).
**How to avoid:** Rely on the complementary INV-01/INV-03 bit-level assertions (`test_val_eprom.cpp`) for the 0x100 bit, not the trace.

### Pitfall 4: `configure_memory` overwrites `firestarter_get_data` (test-authoring trap)
**What goes wrong:** A scripted mock assigned before `configure_memory` is clobbered.
**Why it happens:** `configure_memory` sets `handle->firestarter_get_data = memory_get_data` (`memory.cpp:91`).
**How to avoid:** Re-assign the mock AFTER `configure_memory()` (the documented Pitfall 3 in `test_val_eprom.cpp:479`, used by `test_golden_eprom_chip_id` and the WR-02 tests).

### Pitfall 5: py3.12 masks py3.11 CI (SAFE-02)
**What goes wrong:** Devcontainer default `python3` is 3.12.13 (`/usr/local/bin/python3`); CI runs on **3.11** (`ci.yml:29-32`). ruff/format/mypy can pass on 3.12 and fail on 3.11.
**Why it happens:** f-string backslash rules + ruff version pins differ across interpreters (see memory `reference_devcontainer_py312_masks_ci_py39`).
**How to avoid:** Validate against a 3.11 interpreter explicitly before claiming green (see Environment Availability — no 3.11 binary is present in this devcontainer; the planner must provision one or run the gate in a 3.11 venv). `mypy` already pins `python_version = "3.9"` in `pyproject.toml:111` (config-file, not CLI).
**Warning signs:** "passes locally, fails CI" on ruff format or f-strings.

### Pitfall 6: Voltage-low is a WARNING, not an error (silent under-program — Phase 99 residual)
**What goes wrong:** A blind fix can look correct in the trace yet still flip 0 bits on silicon if VPP is under-spec — `vpp_check_window` only WARNs on low VPP (`primitives.cpp:129-146`).
**Why it happens:** The shield VPP magnitude is a manual potentiometer (not firmware-set); RC-1 is an architectural mismodel, not a measured wrong-level. The pinout redirect alone may not move the physical pin-31 signal (verifier caveat).
**How to avoid:** This is **the Phase-99 residual** — do NOT over-claim a fix. The D-01 belt (deliberate PGM assert) maximizes the single-bench-trip chance; the actual write→verify is Phase 99. Consider the Claude's-discretion held-rail-checkable control-register diagnostic so Phase 99 can separate "path correct but chip OTP/dead" from "still broken."

### Pitfall 7: `chip_database.json` is generated — don't hand-edit blindly
**What goes wrong:** Hand-editing the AM27C020 row diverges from `build_db.py` output and `diff_db.py` flags it (or a future regen reverts it).
**How to avoid:** Prefer expressing the pinout assignment in `build_db.py` (key off size/protocol) and regenerate; if the pipeline cannot, document the override and update the `diff_db.py` baseline with a cited rule. A1 **CONFIRMED** (PATTERNS): `resolve_pinout_key:281-296` can assign `DIP32_27C020` to ≤256K 0x08 chips at generation time — no override required.

## Code Examples

### The existing P1-hold across the program window (already implemented — extend, don't rebuild)
```cpp
// firestarter/src/proms/eprom.cpp:168-180  — program_mismatched_bytes
static void program_mismatched_bytes(firestarter_handle_t* handle, const uint8_t* mismatch_bitmask) {
     rurp_register_t programming_bits = CTRL_VPE_ENABLE;
    handle->firestarter_set_control_register(handle, programming_bits, 1);   // ← P1 asserted (after rewrite)
    delay(10);
    for (uint32_t i = 0; i < handle->data_size; i++) {
        if (mismatch_bitmask[i / 8] & (1 << (i % 8))) {
            handle->firestarter_set_data(handle, handle->address + i, handle->data_buffer[i]);  // CE pulse
        }
    }
    handle->firestarter_set_control_register(handle, programming_bits, 0);   // ← P1 cleared after loop
}
```
```cpp
// firestarter/src/proms/eprom.cpp:320-326  — the existing CTRL_VPE_ENABLE → CTRL_VPP_P1_ENABLE rewrite
void eprom_internal_set_control_register(firestarter_handle_t* handle, rurp_register_t bit, bool state) {
    if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle)) {
        bit &= ~CTRL_VPE_ENABLE;
        bit |= CTRL_VPP_P1_ENABLE;     // 0x08 — held across program_mismatched_bytes
    }
    ep_set_control_register(handle, bit, state);
}
```

### The CE-only program pulse (the PGM-assert seam — memory.cpp:346)
```cpp
// firestarter/src/proms/memory.cpp:346-356  — memory_set_data: strobes CE only today
void memory_set_data(firestarter_handle_t* handle, uint32_t address, uint8_t data) {
    rurp_chip_input();
    address = mem_util_remap_address_bus(handle, address, WRITE_FLAG);  // pin 31 = line 22 from address bit
    handle->firestarter_set_address(handle, address);
    rurp_write_data_buffer(data);
    delayMicroseconds(3);
    rurp_chip_enable();                       // CE low
    delayMicroseconds(handle->pulse_delay);   // 100µs for 0x08
    rurp_chip_disable();                       // CE high
}
// FIX SEAM (D-01 deliberate PGM assert): for protocol==0x08 && pins==32 && mem_size<=262144,
// drive pin-31's bus line (now OFF the address bus via DIP32_27C020) to PGM=VIL (hold LOW —
// Q1 RESOLVED) and hold it across the CE pulse window. This is a firmware hold-LOW branch,
// NOT a static_high_mask entry (static_high_mask drives HIGH; PGM is active-LOW).
```

### Why static_high_mask is the WRONG vehicle for PGM=VIL (Q1 evidence)
```cpp
// firestarter/src/proms/memory.cpp:402  — mem_util_remap_address_bus
    reorg_address |= config.static_high_mask;   // ← ORs a 1 (HIGH) into the line; never clears
// → bit 22 of reorg_address = CONTROL register bit 6 (mem_util_calculate_top_address_register, :184-185)
// → rurp_write_to_register(CONTROL_REGISTER, ...) → rurp_internal_write_to_register (rurp_register_utils.h:63-89)
//   → rurp_write_data_buffer(data): each bit mapped straight to a port pin, NO inversion
//   (leonardo_rurp_shield.cpp:80-99) → a 1 bit = physical HIGH at pin 31.
// PGM program-active = VIL (LOW) per AM27C020.pdf. HIGH ≠ VIL → static-high CANNOT express PGM-assert.
```

### Failure-case / mismatch test pattern (D-05 mandatory, P89 CR-01 lesson)
```cpp
// firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp:621-655  (WR-02a) — the reusable mismatch pattern
// Script get_data to return a non-matching byte → assert the path yields the CORRECT fork.
// Phase-98 analog: a 0x08-32-pin write where verify never matches must (a) still ERROR after 20 retries,
//   and (b) the corrected-path test must assert pin-31/PGM line was driven program-active in the recording
//   (e.g. recording_has_vpp_enable(CTRL_VPP_P1_ENABLE) AND a pin-31 line assertion), NOT just happy-path.
```

### How the host wire-emit currently builds the AM27C020 command (verified live, RCA brief)
```
algorithm=8  type=1  pin-count=32  memory-size=262144  vpp_mv=13000  pulse-delay=100  flags=0
bus-config = { 'bus':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,22], 'vpp-pin':21 }
```
Line 22 is the last `bus` entry — that is pin 31 mapped as the 19th address line. The `DIP32_27C020` fix removes 22 from `bus` (pin 31 off the address bus); the program-active PGM=VIL hold is then the firmware branch's responsibility (Plan 02).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pin 31 = 19th address line for all DIP32 (`DIP32_STD`) | Scoped per-family pinout variants (`DIP32_SST39SF040` for 5V flash; `DIP32_27C020` proposed for ≤256K 0x08) | SST39SF040 variant predates v1.18; 27C020 variant is THIS phase | Pin-31 role becomes family-correct, not one-size-fits-all |
| CE-only program pulse with VPE bit | `CTRL_VPE_ENABLE`→`CTRL_VPP_P1_ENABLE` rewrite for 32-pin P1-VPP parts, held across program window | Pre-existing (INV-03) | P1/VPP routing already correct; pin-31 PGM still the gap |
| Golden traces happy-path only | Golden traces + explicit mismatch/failure-case tests | v1.16 Phase 89 (CR-01) | Behavior-preserving changes need a failure-fork test (D-05) |

**Deprecated/outdated:**
- Treating RC-1 as "pin 31 left floating": **corrected** — pin 31 is *driven* (as an address line, line 22 = CONTROL bit 6), and at addr 0 it sits at the program-active level. The defect is architectural mismodeling, not a floating pin (Phase-97 verifier caveat). Do not write the fix as if pin 31 were floating.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `build_db.py` can assign `DIP32_27C020` to ≤256K 0x08 chips at generation time (else a documented post-process override is needed) | Don't Hand-Roll / Pitfall 7 | **CONFIRMED** by PATTERNS (`resolve_pinout_key:281-296` is a pure fn of mem_size) — no override needed |
| A2 | The AM27C020 program-active level for PGM (pin 31) is VIL (LOW) during the program pulse, per datasheet ("CE and PGM at VIL") | Code Examples / Q1 | **CONFIRMED via firmware**: `static_high_mask` HIGH-drive cannot express VIL → PGM-assert is a firmware hold-LOW (Q1 RESOLVED) |
| A3 | Pin 31 (line 22) physically lands at CONTROL register bit 6 = `CTRL_READ_WRITE` (0x40) on Rev 2.0 | Summary / bus-line mapping | **CONFIRMED**: `mem_util_calculate_top_address_register:184-185` masks bit 22→CONTROL bit 6; host-pinout fix holds regardless (it removes pin 31 from the bus) |
| A4 | "A18 unused" ⟺ `mem_size <= 262144` (A18 = address bit 18 = mask 0x40000) | Pattern 2 gate predicate | If a ≤256K chip legitimately needed A18, the size gate would be wrong — but 256K = exactly A0..A17, so A18 is genuinely unused (datasheet-confirmed) |
| A5 | The `0x08` 32-pin golden trace will legitimately change (so it must be re-blessed + re-pinned) while 0x07/0x0B stay byte-identical | Pitfall 2 / FIX-02 | If the firmware change is fully data-driven via bus-config, the *register* trace might not change at all (only the address/bus bits, which the trace does capture in CONTROL writes) — the planner must check the actual diff and re-pin only if it changes |

## Open Questions (RESOLVED)

1. **PGM program-active level (LOW) vs `static_high_mask` (drives HIGH).**
   - What we know: AM27C020 programs with CE=VIL **and PGM=VIL**; `static_high_mask` drives a bus line HIGH (`memory.cpp:402`).
   - What's unclear: whether the RURP socket inverts pin 31's sense, so that "static-high on line 22" yields PGM=VIL at the socket, or whether a deliberate firmware clear/hold-low of line 22 is required.
   - **RESOLVED (2026-06-30, verified against live firmware):** There is **NO inversion** anywhere in the line-22 → pin-31 path. `static_high_mask` ORs a `1` into `reorg_address` (`memory.cpp:402`, set-only, never clears); bit 22 of `reorg_address` lands in CONTROL register bit 6 via `mem_util_calculate_top_address_register` (`memory.cpp:184-185`); `rurp_write_to_register(CONTROL_REGISTER, ...)` → `rurp_internal_write_to_register` (`rurp_register_utils.h:54,63-89`) → `rurp_write_data_buffer(data)` maps each CONTROL-byte bit straight to a physical port pin (`leonardo_rurp_shield.cpp:80-99`), so a `1` bit yields a physical **HIGH** at pin 31. PGM program-active is **VIL (LOW)** (AM27C020.pdf). Therefore **static-high on line 22 yields HIGH, NOT PGM=VIL** — the `static-high-pins:[31]` route CANNOT express the program-active assert and is RULED OUT as the PGM vehicle. **Decision:** `DIP32_27C020`'s pin-31 job is only to take pin 31 OFF the address bus (so it is no longer driven as A18); the deliberate program-active PGM=VIL hold-LOW is delivered by Plan 02's gated `0x08` firmware branch in `memory_set_data`, held across the CE pulse. Document this polarity + datasheet citation in both the pinout `comment` and the firmware comment.

2. **Whether the firmware gate needs a new bus-config datum or can reuse `static_high_mask` + size/protocol.**
   - What we know: `static_high_mask` and `pins`/`protocol`/`mem_size` are all already in the wire struct (no new field).
   - What's unclear: if the PGM-assert needs a *distinct* "this line is PGM, hold it across the pulse" signal that `static_high_mask` (a static OR) cannot express (because it must be timed to the CE window).
   - **RESOLVED (2026-06-30):** `static_high_mask` is a **static unconditional OR** applied on every `mem_util_remap_address_bus` call (`memory.cpp:402`) and drives HIGH, not the timed per-CE-pulse hold-LOW that PGM=VIL requires (Q1). It cannot express the assert on two counts (polarity AND timing). The PGM-assert is therefore a **firmware-internal gated branch** in `memory_set_data`, keyed on the **existing** `handle->protocol`, `handle->pins`, `handle->mem_size`, and `handle->bus_config` (line-22 line index) struct fields. **No new wire field is needed** (D-03 honored — the pinout+protocol-gate route succeeded; no `firestarter.h` ↔ `constants.py` lockstep escalation). The `DIP32_27C020` pinout (Q1) supplies the data-driven "pin 31 is no longer an address line" signal; the firmware reads protocol/size/pins to gate the hold-LOW.

3. **Claude's-discretion diagnostic hook.**
   - What we know: Phase 99 needs to separate "path correct but chip OTP/dead" from "still broken"; the held-rail proxy is DTR-reset-fragile (use `hold_rail.py`, port held open — memory `reference_held_rail_dtr_reset_hold_script`).
   - **RESOLVED (deferred to executor discretion, per CONTEXT Claude's-Discretion):** a low-cost win is to make the program-window control-register value statically inspectable (e.g. a documented `dev reg ... -f` value that reproduces the program-window pin-31 + P1 state), rather than new firmware logging. Plan 02 Task 2 carries this as an explicit optional ("add only if low-surface; otherwise record the decision and rely on Phase 99's DMM + write→verify + held-rail proxy"). Not a blocker for any plan.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO + `pio test -e native` | Firmware native tests (FIX-02) | **[ASSUMED]** present (used by all prior phases) | — | Planner verifies `pio` on PATH |
| python3.11 | py3.11 CI parity (SAFE-02) | ✗ | — | **No 3.11 binary in devcontainer.** Present: 3.12.13 (`/usr/local/bin/python3`) + 3.13 (`/usr/bin/python3.13`). Provision a 3.11 venv (e.g. `uv`/`pyenv`) OR run the gate in CI and treat local 3.12 as advisory-only |
| ruff / mypy / pytest | Host CI gate (SAFE-02) | **[ASSUMED]** installable via `pip install -e '.[test]'` / `.[dev]` | — | Restore wiped toolchain via the `[test]` extra (memory `reference_firestarter_app_python_test_env`); use `/usr/local` python |
| AM27C020 silicon + Leonardo + Rev 2.0 | NOT this phase | n/a (Phase 99) | — | Phase 98 is blind/no-bench by design |

**Missing dependencies with no fallback:** none that block Phase 98 (it is code/config only).
**Missing dependencies with fallback:** python3.11 — the planner must provision a 3.11 interpreter to validate SAFE-02 locally, or rely on CI (the py3.12 default WILL mask 3.11 differences — Pitfall 5).

## Validation Architecture

> `workflow.nyquist_validation` was not found explicitly disabled in `.planning/config.json` — treat as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Firmware framework | Unity via PlatformIO `[env:native]` (ArduinoFake/fakeit for `delay`/`Serial`) |
| Firmware config file | `firestarter/platformio.ini` (`[env:native]`: `platform=native`, `test_framework=unity`, `src_filter=+<proms/>`, `test_build_src=yes`) |
| Firmware quick run | `pio test -e native -f "*test_val_eprom*"` |
| Firmware full suite | `pio test -e native` |
| Golden re-bless | `pio test -e native -f "*test_val_eprom*"` with `-DGOLDEN_BLESS` (redirect rows into the `.inc`) |
| Host framework | pytest (`firestarter_app`) |
| Host quick run | `pytest -q` (from `firestarter_app/`) |
| Host gate scripts | `python tools/check_dispatch.py` ; `python tools/diff_db.py` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIX-01 | 0x08-32-pin write drives PGM (pin 31) program-active + holds across CE pulse | unit (native) | `pio test -e native -f "*test_val_eprom*"` (new corrected-path test) | ❌ Wave 0 (extend `test_val_eprom.cpp`) |
| FIX-01 | 0x07/0x0B unaffected | unit (native) | `pio test -e native -f "*test_val_eprom*"` (golden 0x07/0x0B) | ✅ |
| FIX-02 | golden 0x07/0x0B/chip-id byte-identical | unit (native) | `pio test -e native -f "*test_val_eprom*"` | ✅ |
| FIX-02 | corrected 0x08 trace re-pinned + failure-case/mismatch test | unit (native) | `pio test -e native -f "*test_val_eprom*"` (new mismatch test) | ❌ Wave 0 |
| FIX-02 | dispatch-mirror guard | host | `python tools/check_dispatch.py` | ✅ |
| FIX-03 | DB pinout reassignment limited to intended rows | host | `python tools/diff_db.py` | ✅ (baseline may need a cited-rule update) |
| FIX-03 | constants↔firestarter.h parity (only if wire field added) | host | constants-parity test (`pytest`) | ✅ (parity test exists; NO wire field added — Q2 RESOLVED) |
| SAFE-02 | over-voltage stays ERROR-blocked | unit (native) | existing `vpp_check_window` coverage + `test_val_eprom` | ✅ |
| SAFE-02 | ruff + format + mypy + diff_db + check_dispatch on py3.11 | host CI | see Sampling Rate | ✅ (gate exists; py3.11 provisioning is the gap) |

### Sampling Rate
- **Per task commit:** `pio test -e native -f "*test_val_eprom*"` (firmware) ; `python tools/check_dispatch.py && python tools/diff_db.py` (host, after any DB/pinout change).
- **Per wave merge:** `pio test -e native` (full firmware native suite) ; `pytest -q` (full host suite).
- **Phase gate:** full firmware native suite green + host `ruff check`, `ruff format --check`, `mypy`, `diff_db`, `check_dispatch` green **on py3.11** before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `test/native/avr/test_val_eprom/test_val_eprom.cpp` — add a corrected-0x08-32-pin write test asserting pin-31/PGM line driven program-active (recording-based, mirroring `test_inv03`).
- [ ] `test/native/avr/test_val_eprom/test_val_eprom.cpp` — add ≥1 failure-case/mismatch test for the corrected 0x08 path (D-05 / P89 CR-01; mirror WR-02a/b/c).
- [ ] `test/native/avr/test_val_eprom/golden_eprom_0x08_write.inc` — re-bless ONLY if the corrected path legitimately changes the low-byte trace; cite rationale in the header comment.
- [ ] Provision a python3.11 interpreter for local SAFE-02 validation (no 3.11 in devcontainer).

## Security Domain

> `security_enforcement` not found disabled in config — included. This is firmware/embedded + a host CLI; web-app ASVS categories mostly N/A. The load-bearing safety invariant here is the over-voltage hardware-damage guard (SAFE-02), which is treated as the security control.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | local CLI + serial; no auth surface |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | yes | `vpp_check_window` over-voltage clamp (`primitives.cpp:106` HIGH→ERROR); host `chip_resolver.resolve_chip` guard; DB-derived `vpp_mv`/`pin-count`/`mem_size` validated before the firmware asserts any rail |
| V6 Cryptography | no | — |

### Known Threat Patterns for this stack (hardware-safety framing)
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Over-voltage on socket (>13.5V abs-max → chip damage) | Denial of Service / Tampering | `vpp_check_window` HIGH→ERROR, NO `FLAG_FORCE` relaxation in the path (D-06); never widen pulse beyond datasheet |
| 12V P1/VPP asserted on a 5V or A18 pin (D-04 alias) | Tampering (hardware damage) | Size/protocol-gated PGM/P1-hold; host pinout scoping; `check_dispatch.py` no-vpp-pin structural guard |
| Test-only escape hatch bypassing the guard | Elevation/Tampering | D-06: no escape hatch; AM27C020 flows through normal 0x08 dispatch |
| Mis-built DB row routing a 512K part to the 256K PGM path | Tampering | Firmware `mem_size <= 262144` belt + `diff_db.py` review |

## Sources

### Primary (HIGH confidence — read direct this session, file:line)
- `firestarter/src/proms/eprom.cpp` — `configure_eprom`, `eprom_write_init/execute`, `program_mismatched_bytes` (:168), `eprom_internal_set_control_register` (:320-326), `eprom_check_vpp` (:263). [VERIFIED]
- `firestarter/src/proms/memory.cpp` — `configure_memory` dispatch (:121), `mem_util_calculate_top_address_register` (:184-185, bit 22→CONTROL bit 6), `mem_util_set_address` (:200-211), `memory_set_data` (:274), `mem_util_remap_address_bus` (:309-332, static_high_mask OR at :330). [VERIFIED — Q1 polarity re-confirmed this revision]
- `firestarter/include/rurp_register_utils.h` — `rurp_write_to_register` (:24, LSB/MSB/CONTROL→bus-line composition), `rurp_internal_write_to_register` (:63-89, bit-for-bit latch, NO inversion). [VERIFIED — Q1 polarity]
- `firestarter/src/boards/leonardo_rurp_shield.cpp` — `rurp_write_data_buffer` (:80-99, data bit → port pin straight, no complement). [VERIFIED — Q1 polarity]
- `firestarter/src/proms/primitives.cpp` — `vpp_check_window` (:93, HIGH→ERROR :106, FLAG_FORCE→WARN :121). [VERIFIED]
- `firestarter/include/rurp_pinout.h` — CTRL_* defs; `CTRL_READ_WRITE==0x40` (:82/:94); `CTRL_VPP_P1_ENABLE_REV2==CTRL_ADDRESS_LINE_18_REV2==0x08` alias (:122,:128). [VERIFIED]
- `firestarter/include/rurp_shield.h` — `VPP_P1_32_DIP=0x15` (:40), `CHIP_ENABLE`/`CONTROL_REGISTER` (:56-57). [VERIFIED]
- `firestarter/include/memory_utils.h` — `using_p1_as_vpp` (:24-28). [VERIFIED]
- `firestarter/include/firestarter.h` — `bus_config_t.static_high_mask` (:81), `rw_line` (:79), handle `protocol`/`pins`/`mem_size`, `page_size` wire-field precedent (:97). [VERIFIED]
- `firestarter/test/native/avr/test_val_eprom/test_val_eprom.cpp` + `golden_eprom_0x0{7,8,B}_write.inc` + `_shared/golden_trace.h` — harness, INV-03 P1 test, WR-02 mismatch pattern, bless mode. [VERIFIED]
- `firestarter_app/firestarter/database.py` — `pin_conversions[32]` (:119-142, pin 31→22), `get_bus_config` (:278-334), `convert_to_programmer` (:569-632), `_ALGO_MEM_TYPE`/`PROTOCOL_MAP`. [VERIFIED]
- `firestarter_app/firestarter/data/pinouts.json` — `DIP32_STD`, `DIP32_SST39SF040` (the scoped-variant precedent). [VERIFIED]
- `firestarter_app/firestarter/data/chip_database.json` — AM27C020 (:277, `DIP32_STD`, algo 8, 262144) + AM27C040 (:297, `DIP32_STD`, algo 8, 524288); DB scan: 127 chips on 0x08/DIP32_STD across 128K/256K/512K/1M. [VERIFIED]
- `firestarter_app/firestarter/constants.py` — `CTRL_*` mirror block (:109-112), `JSON_KEY_PAGE_SIZE` (:100, lockstep precedent). [VERIFIED]
- `firestarter_app/tools/check_dispatch.py` — dispatch mirror, `_FAMILY_VPP_INVARIANTS` (configure_eprom 0–25000), no-vpp-pin structural guard, WARNING-5 guard, `KNOWN_PROTOCOLS`. [VERIFIED]
- `firestarter_app/tools/diff_db.py` — GATE-02 baseline diff (`tools/baseline/chip_database.baseline.json`). [VERIFIED]
- `firestarter_app/pyproject.toml` + `.github/workflows/ci.yml` — CI python 3.11 (`ci.yml:29-32`); mypy `python_version="3.9"` (`pyproject.toml:111`). [VERIFIED]
- `.planning/phases/97-.../evidence/97-RCA-FINDINGS.md` — RC-1 verdict, differential matrix, Pitfall-6 alias caveat, held-rail `0x188`/`0x180`. [CITED]
- `.planning/research/v1.18-AM27C020-27C-EPROM.md` — datasheet facts (VPP 12.75V, Flashrite 100µs, CE+PGM=VIL), current-path file:line. [CITED]
- `.planning/REQUIREMENTS.md` / `.planning/ROADMAP.md` §Phase 98 — FIX-01/02/03, SAFE-02 bodies + success criteria. [CITED]

### Secondary (MEDIUM confidence)
- Auto-memory: `reference_devcontainer_py312_masks_ci_py39`, `reference_firestarter_app_python_test_env`, `reference_held_rail_dtr_reset_hold_script`, `reference_codegen_ruff_clean_emitter` — devcontainer/CI traps + held-rail tooling. [CITED]

### Tertiary (LOW confidence / to confirm)
- `build_db.py` ability to emit `DIP32_27C020` for ≤256K 0x08 chips — A1 **CONFIRMED** by PATTERNS (`resolve_pinout_key:281-296`). [RESOLVED]
- Pin-31/line-22 socket polarity (PGM-VIL vs static-high HIGH) — Q1 **RESOLVED via firmware** (no inversion; static-high = HIGH; PGM-assert = firmware hold-LOW). [RESOLVED]

## Metadata

**Confidence breakdown:**
- Code seams / file:line: HIGH — every cited line read direct this session.
- Mechanism (pin 31 = line 22 = CONTROL bit 6; P1-hold already present): HIGH — confirmed against `rurp_register_utils.h` + `eprom.cpp`.
- Fix shape (host pinout removes pin 31 from address bus + size-gated firmware PGM hold-LOW): HIGH — Q1/Q2 RESOLVED against live firmware (no inversion; static-high ruled out; no new wire field).
- Whether the fix moves the physical signal: LOW/MEDIUM — explicitly the Phase-99 residual (verifier caveat); Phase 98 must not over-claim.
- D-04 alias-collision scope: HIGH — 127 chips / size spread verified; gate predicate derived.

**Research date:** 2026-06-30
**Valid until:** 2026-07-30 (stable in-repo code; re-confirm if firmware tip advances past `bccd995`/v1.17 substrate)
