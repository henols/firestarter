# Phase 97: PRE + RCA — Tier-0 Pre-Flight & Root-Cause the 0x08 0-Bits-Programmed Fault - Research

**Researched:** 2026-06-29
**Domain:** Hardware-RCA / bench-measurement procedure design (firmware C++ + host Python code-analysis; no code change in this phase)
**Confidence:** HIGH on datasheet facts, current-code behavior (read direct, file:line, verified against live tree), and procedure design; MEDIUM on which root cause is *solely* causal (the bench disconfirmation is the point of the phase)

> This is a **diagnostic** phase. There is no Standard Stack / Package Legitimacy section in the usual sense — no external packages are installed, no web research applies. The "stack" is the existing Firestarter firmware + host CLI on a fixed bench (Leonardo + RURP Rev 2.0). All claims below are tagged `[VERIFIED: <file:line>]` (read against the live tree this session), `[CITED: <doc>]` (in-repo datasheet / shield doc), or `[ASSUMED]`. The authoritative substrate is `.planning/research/v1.18-AM27C020-27C-EPROM.md` (the RCA brief); this RESEARCH.md **operationalizes** it into plannable procedure rather than repeating it.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** The Tier-0 writability micro-probe and the RCA-01 failure reproduction are **the same bench action** — a single program attempt at `0x000000` on the *current (unfixed)* path. No separate destructive spend. On the broken path a 0-bit-flip is **INDETERMINATE** (consistent with both "our path is broken" AND "chip is OTP") — it does **not** prove OTP and does **not** trigger deferral. The chip stays pristine. Any bit flips ⇒ RC-5 total-silicon-block is OUT and writability is partially proven (signature recorded as "partial").
- **D-02:** PRE-01's Phase-97 deliverable is **"writability indeterminate pre-fix"** — NOT a pass/fail blocker. The phase does not stall on a definitive writability verdict; the true writable/dead gate is post-fix Phase 99. PRE-01 here = read oracle stable (N≥3 byte-identical) + blank-state SHA recorded + identity/protocol decode confirmed + micro-probe attempt documented (never fabricated). The planner must NOT treat PRE-01 as a Phase-97 gate that can fail the phase.
- **D-03:** RCA exit bar = **resolve the converging pair**. RC-1 (PGM pin 31 modeled as an address line) and RC-2 (P1 VPP routing/level at pin 1) must EACH be individually confirmed-or-exonerated with bench/code evidence before Phase 98 (they may compound — a one-axis fix could still flip 0 bits). RC-3 (JP4) and RC-4 (32-pin addressing collision) pursued **only if** RC-1+RC-2 do not fully account for the symptom. RC-5 handled via the Tier-0 path. RCA-03 may name one cause OR ranked hypotheses, but both pair members must carry a verdict.
- **D-05:** Primary pin-31 evidence = **held-rail static proxy + code-analysis**. A handheld DMM cannot resolve the ~100µs pulse — freeze the program-time control register via `firestarter dev reg … -f` so pin 31 sits statically at its program-pulse level; operator DMMs pin 31 & pin 1 steady-state. Back with file:line code-analysis of bus-line-22 → address-bit-18 mapping. (A 256K chip never sets A18, so pin 31 *may* idle low — bench confirms.) Logic analyzer is OPTIONAL, not gating.
- **D-06:** The "OTP/dead → defer BENCH to FUT, re-scope to software-fix-only" disposition is a **Phase 99 verdict**, reached only after the resolved converging-pair fixes are applied (Phase 98) AND bench-confirmed correct (pin 1 = 12.5–13.0V steady AND pin 31 confirmed VIL during the pulse) and the chip *still* flips 0 bits. A 0-flip *before* the path is fixed never triggers deferral.
- **D-07 / SAFE-01:** Over-voltage stays ERROR-blocked (`vpp_check_window` HIGH→ERROR, no `FLAG_FORCE` relaxation); host `chip_resolver.resolve_chip` guard never bypassed; AM27C020 flows through normal `0x08` dispatch with NO test-only escape hatch. VPP-low is only a WARNING (firmware proceeds) — which is precisely why an under-voltage rail produces "0 bits, no error". Shield VPP magnitude is a **manual potentiometer**: firmware enables/measures but cannot set the level — confirm physically each session.
- **D-08:** `controller:` identity verified per task (ACM ports shuffle); live R1/R2 readback first (Leonardo, R1=270000); N≥3 byte-identical reads gate every write verdict (v1.15 saw a localized 12-byte read glitch at 0x008004–0x00800f). Operator owns Rev 2.0 — **ASK exact silkscreen / JP4 (`JMP_VPP_P1_BYPASS`) open-vs-closed meaning before measuring/toggling JP4**. Every program on this UV part is irreversible (no eraser on hand).

### Claude's Discretion
- Within the locked RC ranking and the 5-step Tier-0 protocol, Claude/planner choose the concrete command sequencing, the cheapest-first disconfirmation ordering, and the held-rail control-register value(s) for the pin-31 static proxy.

### Deferred Ideas (OUT OF SCOPE)
- The **Phase 98 fix itself** (PGM-pin assertion concept, P1 routing held across the full pulse, a dedicated `DIP32_27C020` pinout) — diagnostic only this phase; governed by RCA-03. Pin-31 changes must be scoped to the `0x08`-UV-32-pin class so 27C040/SST39SF040-family DIP32 users (pin 31 = A18/WE) are not broken.
- **FUT-05** (REWR-02 `0x08` rewritable write proof, W27E040 stuck-bit) — separate deferred requirement, not v1.18 scope.
- None of the 5 pending todos fold into this phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **PRE-01** | Tier-0 silicon-writability pre-flight (read oracle N≥3 + blank-state SHA + single `1→0` micro-probe) determines writability pre-fix; if OTP/dead, BENCH defers to FUT (Phase 99 verdict, not here) | §"Tier-0 + RCA-01 Combined Bench Procedure" (the 6-step sequence), §"Pitfalls" (irreversible spend, read-glitch) — note D-01/D-02: micro-probe = RCA-01 program attempt, result is INDETERMINATE on the broken path |
| **RCA-01** | Reproduce the `0x08` 0-bits-programmed failure on the seated chip with a captured signature (failing bytes, VPP ADC readback, DMM pin 1 & pin 31, PGM state) | §"Tier-0 + RCA-01 Combined Bench Procedure", §"VPP / Pin-1 / Pin-31 Measurement Method", §"Failure Signature Capture Schema" |
| **RCA-02** | Differential vs passing `0x07` W27C512 across the candidate axes; isolate the differing variable(s), exonerate the unchanged axes | §"0x07-vs-0x08 Differential Matrix (single-session)", §"2×N isolation method" |
| **RCA-03** | Named root cause or ranked hypotheses each with disconfirming evidence; classified firmware-algorithm / host-pinout / VPP-routing / addressing / silicon | §"RC-1..RC-5 Disconfirmation Logic (as plannable steps)", §"RCA Verdict Doc schema" |
| **SAFE-01** | Over-voltage stays ERROR-blocked; host `resolve_chip` guard never bypassed; normal `0x08` dispatch, no escape hatch | §"SAFE-01 Non-Invasive Verification Steps" |
</phase_requirements>

---

## Summary

The seated AM27C020 (256K×8 CMOS UV-EPROM, 32-pin DIP, `0x08` EPROM-QUICK) programs **0 bits** on the current path — `write` fails deterministically at `0x000000` (`bad bytes 15/16, retries 20`, v1.15 Phase 83/84) while its `0x07` sibling W27C512 wrote clean the same session. Phase 97 does NOT fix this; it produces four diagnostic artifacts on the bench (Leonardo + RURP Rev 2.0, operator DMM at socket pin 1 = VPP and pin 31 = PGM): a Tier-0 writability pre-flight result (PRE-01), a reproduced failure signature (RCA-01), a differential against `0x07` (RCA-02), and a named root cause / ranked hypotheses with disconfirming evidence (RCA-03). SAFE-01 is a standing non-bypass invariant throughout.

Code analysis this session **confirms the RC-1 mechanism at file:line precision** (and sharpens it past the brief). `DIP32_STD` lists DIP **pin 31 as the 19th address-bus pin** [VERIFIED: firestarter_app/firestarter/data/pinouts.json `DIP32_STD.address-bus-pins[18]=31`]; the host maps `pin_conversions[32][31] = 22` [VERIFIED: firestarter_app/firestarter/database.py:141]; the firmware program pulse `memory_set_data` strobes **only CE** with no PGM concept [VERIFIED: firestarter/src/proms/memory.cpp:346-356]; and the top-address register derives bus-line-22's bit from `address>>16` (bit 22 = `CTRL_READ_WRITE` = 0x40) [VERIFIED: memory.cpp:187-202]. At `address 0x000000` (A18=0) pin 31's bus line is **0** — i.e. pin 31 idles low, which *may coincidentally be VIL = program-active*, but that is unverified at the socket and is exactly what the held-rail static proxy (D-05) settles. RC-2 is the converging axis: VPP for the 32-pin part routes to socket **pin 1** via the `CTRL_VPE_ENABLE → CTRL_VPP_P1_ENABLE` rewrite [VERIFIED: firestarter/src/proms/eprom.cpp:319-326], a delivery path never bench-proven on a `0x08` UV chip, and the magnitude is set by a manual pot the firmware cannot control (VPP-low = WARNING-only [VERIFIED: firestarter/src/proms/primitives.cpp:144-145]).

**Primary recommendation:** Plan ONE bench session, cheapest-first, that (a) runs the combined Tier-0 micro-probe + RCA-01 reproduction as a single program attempt at `0x000000` with full instrumentation, (b) holds the program-time control register static via `dev reg … -f` for the pin-31/pin-1 DMM proxy, (c) runs the `0x07` W27C512 differential control in the same session, then (d) writes an RCA verdict resolving RC-1 AND RC-2 each individually. Pair every bench measurement with a code-analysis finding so the verdict survives even if a measurement is ambiguous.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Tier-0 writability micro-probe (the `1→0` program attempt) | Firmware (program pulse on RURP bus) | Host CLI (`write` orchestration) | The program pulse is physically asserted by `memory_set_data` on the Arduino; the host only sequences it |
| Failure-signature capture (failing bytes, retries) | Host CLI (parses `bad bytes`/`retries` from fw frames) | Firmware (emits `MSG_ERR_VERIFY`) | The host CLI surfaces the per-byte mismatch; firmware reports it |
| VPP rail magnitude at the socket | Hardware (manual potentiometer + P1 routing) | Firmware (enable + ADC measure only) | D-07: firmware cannot set VPP level — it enables the regulator and measures the ADC node only |
| Pin-31 (PGM) program-window state | Hardware (bus wiring) ← driven by Host bus-config + Firmware top-address register | — | Host `pin_conversions`/`bus_config` decides pin 31 = bus line 22; firmware drives line 22 from address bit 18 |
| Over-voltage block / host guard | Firmware (`vpp_check_window`) + Host (`chip_resolver.resolve_chip`) | — | SAFE-01 owns both tiers; neither may be bypassed |
| RCA verdict synthesis | Planning/docs (RCA-FINDINGS) | — | Pure analysis artifact, no tier |

**Why this matters here:** the 0-bits fault sits at the **firmware-program-pulse ↔ host-bus-config seam** (pin 31 routing) and the **hardware-VPP ↔ firmware-measure seam** (pin 1 level). RCA-02 deliberately holds the host handler (`configure_eprom`) and transport constant and varies only the 32-pin/P1/PGM axes — so the differential isolates exactly these two seams.

---

## Standard Stack (bench tooling — already installed, verified present)

> No packages to install. These are the existing host CLI commands the procedure drives, all verified against the live `firestarter_app` tree this session.

| Command | Purpose | Verified |
|---------|---------|----------|
| `firestarter info <chip>` | identity + decode confirm (type/pins/size/VPP/protocol/chip-id) | `cli` group present |
| `firestarter read <chip> -o <file>` | read oracle (one run) | present |
| `firestarter dev consistency-check <chip> --runs N` | N×byte-identical read oracle (the N≥3 gate) | [VERIFIED: firestarter_app/firestarter/cli_handlers.py:1080] |
| `firestarter blank <chip>` | blank-check (read path; VPP-skip keeps VPP off) | present |
| `firestarter write <chip> <file> [-b]` | the program attempt (Tier-0 micro-probe = RCA-01) | present |
| `firestarter verify <chip> <file>` | negative-control verify after the attempt | present |
| `firestarter vpp` | continuous VPP ADC monitor (measure-only, no socket routing) | [VERIFIED: cli_handlers.py:659] |
| `firestarter vpe` | VPE rail monitor (un-dropped regulator output) | [VERIFIED: cli_handlers.py:671] |
| `firestarter dev reg <MSB> <LSB> <CTRL> -f` | direct control-register write, `-f` = Firestarter (hw-rev-remapped) bit definitions — the held-rail static proxy | [VERIFIED: cli_handlers.py:981-1029] |
| `firestarter hw` | live R1/R2 readback (D-08 discipline) | present |

**Window-capture idiom (continuous monitors):** `timeout -s INT 15 stdbuf -oL firestarter vpp` [CITED: RCA brief §VPP Measurement; reference_v114_bench_erase_rail_and_test_artifact].

**`dev reg -f` control-register bit map** (from the CLI help text, Rev2/HARDWARE_REVISION layout) [VERIFIED: cli_handlers.py:1005-1022 + firestarter/include/rurp_pinout.h:118-127]:

```
0x100  CTRL_VPP_VPE_DROP_ENABLE
0x080  CTRL_VPP_REGULATOR_ENABLE
0x040  CTRL_READ_WRITE
0x020  CTRL_ADDRESS_LINE_18   (== CTRL_VPP_P1_ENABLE alias on Rev2? NO — see note)
0x010  CTRL_ADDRESS_LINE_17
0x008  CTRL_VPP_P1_ENABLE
0x004  CTRL_VPE_ENABLE
0x002  CTRL_VPP_A9_ENABLE
0x001  CTRL_ADDRESS_LINE_16
```

> **Correction vs the brief (HIGH confidence):** the brief said "line 22 corresponds to `CTRL_READ_WRITE` (0x40) territory" — that is the *top-address* derivation. Separately note the Rev2 layout defines `CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2` (both 0x08) [VERIFIED: rurp_pinout.h:127]. This is an **alias collision the planner must flag**: on Rev2, address bit 18 and the P1-VPP-enable bit are the *same control-register bit* (0x08). For a 256K AM27C020, A18 is never set, so this collision is dormant at the addresses in play — but it is directly relevant to the RC-1/RC-4 boundary and to any Phase-98 fix. See §RC-1 and §RC-4.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Held-rail static DMM proxy (D-05) | Logic analyzer on the live ~100µs pulse | LA resolves the real pulse but is OPTIONAL (operator may not have one); static proxy is the gating method |
| `dev consistency-check --runs 3` | 3× manual `read` + `sha256sum` diff | consistency-check is the established N≥3 oracle and already writes per-run binaries |

---

## Architecture Patterns

### System Architecture Diagram (the 0x08 program data flow being diagnosed)

```
 host: firestarter write AM27C020 <img>
        │  (resolve_chip guard: SAFE-01 — must pass, never bypassed)
        ▼
 EpromDatabase.get_bus_config()         [database.py]
   pinout=DIP32_STD → bus=[..,20,22], vpp-pin=21 (VPP_P1_32_DIP=0x15)
   pin_conversions[32][31]=22  ◄── pin 31 (PGM) becomes bus line 22  [database.py:141]
        │  JSON command over COBS serial @250000
        ▼
 firmware dispatch (protocol 0x08) → configure_eprom()      [memory.cpp:122]
        │
        ├─ eprom_write_init → eprom_check_vpp                [eprom.cpp:134,263]
        │     assert CTRL_VPP_REGULATOR_ENABLE|CTRL_VPP_VPE_DROP_ENABLE, settle 100ms
        │     vpp_check_window:  LOW→WARN(proceed)   HIGH→ERROR(block)  [primitives.cpp:93]
        │
        └─ eprom_write_execute → program_mismatched_bytes    [eprom.cpp:197,168]
              programming_bits = CTRL_VPE_ENABLE               [eprom.cpp:169]
              set_control_register(...)                        [eprom.cpp:171]
                 └► eprom_internal_set_control_register:       [eprom.cpp:319-326]
                      using_p1_as_vpp(handle)==true  ⇒  strip CTRL_VPE_ENABLE,
                                                        set  CTRL_VPP_P1_ENABLE  (route VPP→pin1)
              for each mismatched byte:  memory_set_data()      [memory.cpp:346]
                 set address (remap: A18→bus line 22→pin 31)
                 rurp_write_data_buffer(data)
                 delayMicroseconds(3)
                 rurp_chip_enable()      ◄── ONLY CE strobed, NO PGM pulse  [memory.cpp:353]
                 delayMicroseconds(pulse_delay=100µs)
                 rurp_chip_disable()
        ▼
 RURP shield bus → socket:  pin1=VPP (via P1)   pin31=PGM (=bus line 22 = A18 state = 0 @ addr0)
        ▼
 AM27C020 (datasheet): program needs CE=VIL AND PGM=VIL AND VPP=12.75V±0.25 simultaneously
        ▼
 verify-after-pulse mismatch → retry (up to 20×, adaptive pulse) → bad bytes 15/16 → 0 bits
```

### Pattern 1: Combined micro-probe = reproduction (D-01)
**What:** One `write` of a single `1→0` value at `0x000000` serves as BOTH the Tier-0 writability probe AND the RCA-01 reproduction. **When:** always — never spend two separate program attempts. **Why:** the chip is UV (irreversible, no eraser); a 0-flip is INDETERMINATE pre-fix so a second probe gains nothing.

### Pattern 2: Held-rail static proxy (D-05, v1.14 reusable)
**What:** Freeze the program-active control-register state via `dev reg … -f` so the operator can DMM pin 1 and pin 31 at steady-state (a handheld meter cannot catch the 100µs pulse). **When:** for any program-window voltage/level measurement. **Source:** [CITED: reference_v114_bench_erase_rail_and_test_artifact — `firestarter dev reg 0 0 0x86 -f` held the VPP rail for the DMM].

### Pattern 3: 2×N differential isolation (RCA-02, v1.17 reusable)
**What:** Hold everything constant except the named axis; the passing `0x07` W27C512 sibling (same `configure_eprom()`, same session/bench) exonerates the unchanged axes. **Source:** [CITED: v1.17 W29C040-vs-W29C020 method; RCA brief §Differential].

### Anti-Patterns to Avoid
- **Trusting N=1 reads** — v1.15 saw a localized 12-byte read glitch at 0x008004–0x00800f on *this* chip; an unstable oracle makes "0 bits" un-attributable. N≥3 byte-identical gates every verdict (D-08).
- **Reading "0 bits" as proof of OTP** — pre-fix it is INDETERMINATE (D-01). Never let it trigger Phase-99 deferral.
- **Bypassing the host guard or relaxing over-voltage to "make a write succeed"** — SAFE-01 violation (D-07).
- **DMMing the live pulse and concluding from a needle that can't settle in 100µs** — use the static proxy.
- **A second destructive program attempt** — irreversible UV part.

---

## Tier-0 + RCA-01 Combined Bench Procedure (cheapest-first, single session)

> Drives PRE-01 + RCA-01 in one operator-witnessed session over USB passthrough. Operator-only actions are tagged **[OP]**; everything else is Claude-driven from the devcontainer **[CLAUDE]**. The chip stays pristine (only one `1→0` attempt; D-01).

**Step 0 — Bench identity (D-08, every task):**
1. [CLAUDE] `firestarter hw` → record live R1/R2 (expect R1≈270000 Leonardo). Confirm `controller:` line = Leonardo (ACM ports shuffle — re-verify per task).
2. [OP] Confirm seated chip = AM27C020; confirm JP4 (`JMP_VPP_P1_BYPASS`) physical position and **state the Rev 2.0 silkscreen meaning** (ASK first — D-08; the EEPROM hw byte cannot distinguish revs).
3. [OP] Confirm the VPP potentiometer is at its established setting (firmware cannot set it — D-07).

**Step 1 — Identity + decode confirm (PRE-01):**
- [CLAUDE] `firestarter info AM27C020` → expect: type UV-EPROM, DIP32, size 0x40000 (262144), VPP 13.0V, protocol 0x08, chip-id 0x00000197 [VERIFIED: chip_database.json AM27C020 entry]. Record verbatim.

**Step 2 — Stable read oracle, N≥3 (PRE-01):**
- [CLAUDE] `firestarter dev consistency-check AM27C020 --runs 3` (writes per-run binaries) [VERIFIED: cli_handlers.py:1080]. Must be byte-identical. If any byte differs (the 0x008004–0x00800f glitch region especially), re-run and treat the oracle as suspect before trusting any write verdict.
- Record the blank-state **SHA256** of the consistent read (PRE-01 deliverable). Known NOT-BLANK: `0x02 @ 0x0000` [CITED: v1.15 EVIDENCE].

**Step 3 — Blank-state note (PRE-01):**
- [CLAUDE] `firestarter blank AM27C020` → expect NOT-BLANK. Record. (VPP-skip keeps VPP off on this read path — Phase 84 T-84-14.)

**Step 4 — Pre-attempt VPP rail baseline (RCA-01 instrumentation):**
- [CLAUDE] `timeout -s INT 15 stdbuf -oL firestarter vpp` and `… firestarter vpe` → record the ADC-node rail level (measure-only, no socket routing — safe with chip seated) [CITED: reference_vpp_vpe_no_socket_routing].

**Step 5 — The combined micro-probe = RCA-01 reproduction (D-01, ONE attempt):**
- Prepare a 1-byte (or minimal) image that clears exactly one currently-set bit at `0x000000` — e.g. write `0x00` over the existing `0x02` (a legal `1→0`).
- [CLAUDE] run the program attempt: `firestarter write AM27C020 <probe.img>` (normal `0x08` dispatch — **no `-b` skip, no escape hatch**, SAFE-01). Capture full stdout/stderr (the `bad bytes X/Y`, `retries N`, any `MSG_ERR_VERIFY` frames, response codes).
- [OP] **during the attempt**, DMM is not fast enough for the pulse — so the decisive pin-1/pin-31 measurement uses the held-rail proxy in the next sub-procedure. During the live attempt, note only gross behavior (LED/regulator audible click, if any).
- [CLAUDE] immediately after: `firestarter dev consistency-check AM27C020 --runs 3` → did the target byte change?
  - **0 bits flipped** (expected) → RCA-01 reproduced; writability INDETERMINATE (D-01/D-02). Record signature.
  - **Any bit flipped** → RC-5 total-block OUT; record signature as "partial"; writability partially proven.

**Step 6 — Held-rail static proxy for pin 1 + pin 31 (RC-1 + RC-2 decisive measurement; see next section).**

**Operator-vs-Claude split summary:**
| Action | Owner |
|--------|-------|
| All `firestarter` invocations, log capture, SHA computation, command sequencing | [CLAUDE] |
| DMM probing at socket pin 1 / pin 31; JP4 position + silkscreen meaning; VPP pot setting; chip seating; reading the static-rail voltage | [OP] |

---

## Held-Rail Static-Proxy Procedure for Pin 31 + Pin 1 (D-05, the decisive RC-1/RC-2 measurement)

**Goal:** put the control register into the **program-active steady state** so the operator can DMM pin 1 (VPP reaches the chip?) and pin 31 (PGM at VIL?) without chasing a 100µs pulse.

**The control-register value to freeze** (Claude's-discretion per D-05; derived from the verified bit map and the actual program-time bits):

During `program_mismatched_bytes`, the bits asserted around the data write are [VERIFIED: eprom.cpp:169-171, 197-204, 319-326]:
- `CTRL_VPP_REGULATOR_ENABLE` (0x080) — regulator on
- `CTRL_VPP_VPE_DROP_ENABLE` (0x100 on Rev2) — drop VPE to ~13V
- `CTRL_VPP_P1_ENABLE` (0x008) — route VPP to socket **pin 1** (the rewrite of `CTRL_VPE_ENABLE`)
- top-address bits for `address 0x000000` = **0** (no A16/A17/A18, no `CTRL_READ_WRITE`) — so bus line 22 / pin 31 = **0** [VERIFIED: memory.cpp:187-202]

So the held value that reproduces the program-window control state at `address 0` is:
```
CTRL = 0x080 | 0x100 | 0x008 = 0x188   (regulator + VPE-drop + P1-route; A18/pin31 bit clear)
firestarter dev reg 0 0 0x188 -f       [CLAUDE]
```
- **MSB=0 LSB=0** → address 0x0000 (all address lines low, matching the failing address; pin 31 = bus line 22 = A18 = 0).
- `-f` applies the Firestarter (hw-rev-remapped) bit definitions [VERIFIED: cli_handlers.py:1005].

> **Planner note — bit-collision caveat (HIGH confidence, flag for the plan):** On Rev2, `CTRL_VPP_P1_ENABLE` and `CTRL_ADDRESS_LINE_18` are **the same bit 0x008** [VERIFIED: rurp_pinout.h:121,127]. So asserting 0x008 to route VPP→pin1 *also* drives the A18/pin-31 line. The plan must (a) measure pin 31 with 0x188, and (b) cross-check with `dev reg 0 0 0x180 -f` (P1 route OFF) to see whether pin 31 / pin 1 change — this directly probes the alias collision and is part of the RC-1/RC-4 boundary. Whether this collision is causal or dormant for a 256K part is a verdict the bench must reach.

**What pin 31 should read (RC-1 disconfirmation):**
- AM27C020 program requires **PGM = VIL (~0V)** during the CE pulse [CITED: AM27C020.pdf].
- If [OP] DMM at pin 31 reads **~0V (VIL)** with the rail held → pin 31 is coincidentally program-active → **RC-1 is OUT** (pin 31 not the cause). Code-analysis confirms: at addr 0, bus line 22 = 0, so the firmware drives pin 31 low — *consistent* with VIL.
- If pin 31 reads **VIH (~5V)** or floats → **RC-1 CONFIRMED** — the chip never sees PGM-active.

**What pin 1 should read (RC-2 disconfirmation):**
- Expected pass band: **12.5–13.0V steady** (DB ships `vpp_mv=13000`; firmware HIGH threshold = vpp_mv + 500mV ⇒ tolerates ~13.5V before over-voltage ERROR, matching the chip's 13.5V abs-max) [CITED: AM27C020.pdf; primitives.cpp:122-126].
- If pin 1 reads **12.5–13.0V** → **RC-2 (level/routing) OUT**. Cross-check with `firestarter vpp` ADC node — if both agree, the rail reaches the chip.
- If pin 1 reads **~0V / floating** while the ADC node reads ~13V → rail reaches the monitor but NOT pin 1 → **RC-2 CONFIRMED** (P1 routing defect / JP4). The ADC-node-vs-pin-1 divergence is the single most decisive measurement.

**Back-it-with-code (RC-1):** read-first anchors — `pin_conversions[32][31]=22` [database.py:141]; `DIP32_STD.address-bus-pins` last element = 31 [pinouts.json]; `memory_set_data` strobes only CE [memory.cpp:346-356]; `mem_util_calculate_top_address_register` masks `address>>16` to A16/17/18/RW [memory.cpp:187]. These together prove pin 31 is *modeled as an address line, never as a held program pulse* — the code half of the RC-1 verdict, independent of the DMM.

**Cleanup:** [CLAUDE] after measurement, reset the register (`firestarter dev reg 0 0 0 -f` or power-cycle) so the rail is not left held.

---

## RC-1..RC-5 Disconfirmation Logic (as plannable verification steps)

> D-03: RC-1 and RC-2 each MUST get an individual verdict. RC-3/RC-4 only if the pair doesn't fully explain 0-bits. RC-5 via Tier-0.

| RC | Hypothesis | CONFIRM if… | EXONERATE (OUT) if… | Method | Gating? |
|----|-----------|-------------|---------------------|--------|---------|
| **RC-1** | PGM pin 31 modeled as address line, not held program-active | pin 31 DMM reads VIH/floats during held proxy | pin 31 DMM reads ~0V (VIL) AND code shows it driven low at addr0 | Held-rail static proxy (0x188) + code-analysis (memory.cpp:346 + database.py:141 + pinouts.json) | **YES (D-03)** |
| **RC-2** | VPP not reaching pin 1 at 12.5–13.0V during pulse | pin 1 DMM ≈0V/floats while ADC≈13V (routing), OR pin1 <12.5V (pot/level) | pin 1 DMM = 12.5–13.0V steady AND ADC agrees | Held-rail proxy (0x188) + DMM pin1 + `firestarter vpp` ADC cross-check | **YES (D-03)** |
| **RC-3** | JP4 (`JMP_VPP_P1_BYPASS`) position wrong for 32-pin VPP-to-pin-1 | toggling JP4 changes pin-1 VPP delivery decisively | neither JP4 position delivers 12.5–13.0V to pin 1 (⇒ not the lone cause) | [OP] toggle JP4 open↔closed, re-DMM pin 1 — **ASK silkscreen meaning first (D-08)** | only if RC-1+RC-2 incomplete |
| **RC-4** | 32-pin high-address / control-bit collision corrupts target | writing at a high address (e.g. 0x010000, A16=1) behaves differently than addr0 | addr0 still 0-bits with pin1=13V AND pin31=VIL | code-analysis (memory.cpp:187-202 alias `A18==P1_ENABLE` 0x08) + optional high-addr probe (NOT a second destructive spend at addr0 — use read/dev addr to inspect) | only if RC-1+RC-2 incomplete |
| **RC-5** | Chip OTP/dead (total silicon block) | (cannot be confirmed pre-fix — D-01 INDETERMINATE) | any bit flips in the Tier-0 micro-probe | the combined micro-probe (Step 5) | handled via Tier-0; **never triggers deferral pre-fix** |

**Conditional trigger for RC-3/RC-4 (D-03):** pursue only if, after RC-1 and RC-2 each carry a verdict, the resolved pair does **not** fully account for 0-bits — e.g. if both RC-1 (pin 31 = VIL, OK) and RC-2 (pin 1 = 13V, OK) come back EXONERATED yet the chip still flipped 0 bits, then the symptom is unexplained → escalate to RC-3 (JP4) and RC-4 (addressing collision), and the alias-collision finding (0x08 = A18 == P1_ENABLE) becomes the leading RC-4 lead.

**Important RC-1/RC-4 interaction (new this session):** because `CTRL_VPP_P1_ENABLE == CTRL_ADDRESS_LINE_18` (0x08 on Rev2), the act of routing VPP to pin 1 *also* asserts the A18/pin-31 line. The plan should explicitly test the `0x180` (P1 OFF) vs `0x188` (P1 ON) pair to see whether pin 31 and pin 1 move together — this single experiment touches RC-1, RC-2, and RC-4 simultaneously.

---

## 0x07-vs-0x08 Differential Matrix (single-session, RCA-02)

> Method: same bench, same session, same `configure_eprom()` handler; vary only the named axis; the passing W27C512 (`0x07`) exonerates the unchanged axes [CITED: v1.17 method]. Run the `0x07` control write right after the `0x08` attempt while bench identity is fixed.

| Axis | 0x07 W27C512 (PASS) | 0x08 AM27C020 (0-bits) | Differs? | How 0x07 exonerates | Verified anchor |
|------|---------------------|------------------------|----------|---------------------|-----------------|
| Handler | `configure_eprom()` | `configure_eprom()` | NO | same code path passes ⇒ not handler-selection | memory.cpp:122 |
| Pulse width | 100µs | 100µs | NO | identical ⇒ not pulse width | eprom.cpp pulse_delay |
| Program pulse model | CE-only strobe | CE-only strobe | NO (same) | but 0x07's PGM(pin27) is tied OK by 28-pin layout; 0x08 needs pin-31 PGM | memory.cpp:346 |
| **VPP routing** | `vpp_line=0xFF` ⇒ VPE-drop bus line, NOT P1 | `vpp_line=21` (VPP_P1_32_DIP=0x15) ⇒ **P1 / socket pin 1** | **YES** | 0x07 proves the regulator+drop network works; only the **P1 leg** is unproven on a UV part | eprom.cpp:319-326; using_p1_as_vpp memory_utils.h:24 |
| **Program-enable bit** | `CTRL_VPE_ENABLE` reaches VPE/PGM line | rewritten to `CTRL_VPP_P1_ENABLE` | **YES** | 0x07 proves CTRL_VPE_ENABLE path; the rewrite is 0x08-only | eprom.cpp:321-323 |
| **Pin 31 role** | 28-pin: no pin 31 issue | 32-pin: **pin 31 = bus line 22 (address-driven), not PGM** | **YES** | 0x07 has no 32-pin pin-31 mapping ⇒ exonerates everything except the 32-pin axis | database.py:141; pinouts.json DIP32_STD |
| Pin 1 role | VPP on a different bus line | VPP on socket pin 1 (P1) | YES | 32-pin VPP geometry | — |
| FLAG_CAN_ERASE | set (EEPROM auto-erase) | 0 (UV — correct) | minor | not erase-related | — |

**Single-session sequence:** with Leonardo + Rev 2.0 fixed, run: (1) `0x08` AM27C020 probe + signature (Steps 1–6), (2) seat W27C512 [OP], (3) `0x07` write→read→verify (expect PASS), (4) record both rows in one EVIDENCE entry. **The matrix collapses to two converging differing axes: P1-VPP-delivery and pin-31-as-address** — both in the 32-pin/0x08 region, both absent on the passing 0x07 part.

---

## SAFE-01 Non-Invasive Verification Steps (no bypass)

> Confirm the guards EXIST and the over-voltage ERROR path is INTACT, by code-reading + observed behavior — never by triggering or relaxing anything.

1. **Over-voltage stays ERROR (firmware):** code-read `vpp_check_window` — HIGH branch sets `RESPONSE_CODE_ERROR` with no `FLAG_FORCE` relaxation [VERIFIED: primitives.cpp:122-126]; LOW branch is WARNING-only [VERIFIED: primitives.cpp:144-145]. Record file:line as the SAFE-01 evidence. Do **not** drive VPP high to test it.
2. **Host guard never bypassed:** code-read `chip_resolver.resolve_chip` is in the live `write` path and the procedure uses the plain `firestarter write` (no test-only flag, no `-b` skip-erase abuse, no escape hatch). Confirm by grep that no Phase-97 task adds a bypass argument.
3. **Normal dispatch:** the AM27C020 program flows through protocol `0x08` → `configure_eprom()` [VERIFIED: memory.cpp:122] with no special-case. Record that the procedure introduces no firmware/host edit (diagnostic phase).
4. **Manual-pot caveat (D-07):** record that VPP magnitude is operator-set; the firmware enable/measure-only role means a low pot silently under-programs — which is *why* the pin-1 DMM is mandatory before trusting any verdict.

SAFE-01 here is a **confirmation artifact**, not an action — it recurs as a precondition through Phases 98–99.

---

## Failure Signature Capture Schema (RCA-01 deliverable)

Capture these fields verbatim into the EVIDENCE row (consistent with v1.15/v1.16 format):

| Field | Source | Example (pre-fix expected) |
|-------|--------|----------------------------|
| failing address(es) / bytes | `firestarter write` stderr (`MSG_ERR_VERIFY` frames) | `0x000000` |
| bad bytes / retries | write output | `bad bytes 15/16, retries 20` (v1.15 seed) |
| bits flipped | post-attempt consistency-check vs pre SHA | `0` (INDETERMINATE) |
| VPP ADC readback | `firestarter vpp` | record V |
| DMM pin 1 (held proxy) | [OP] | record V (pass band 12.5–13.0) |
| DMM pin 31 (held proxy) | [OP] | record V (VIL≈0 expected by code) |
| pre/post read SHA256 | consistency-check | identical (chip pristine) |
| controller / port / R1R2 / fw commit | `firestarter hw` + `git -C firestarter rev-parse HEAD` | Leonardo, ACMx, R1=270000, `bccd995…` |
| JP4 position + silkscreen meaning | [OP] | record (ASK first) |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| N≥3 read oracle | manual loop + diff | `firestarter dev consistency-check --runs 3` | established, writes per-run binaries, used in v1.6/v1.15 [VERIFIED: cli_handlers.py:1080] |
| Hold the program rail for DMM | custom firmware sketch | `firestarter dev reg <m> <l> <ctrl> -f` | v1.14 reusable held-rail technique [CITED: reference_v114] |
| VPP window capture | parsing serial by hand | `timeout -s INT 15 stdbuf -oL firestarter vpp` | measure-only, safe with chip seated [CITED: reference_vpp_vpe_no_socket_routing] |
| EVIDENCE format | new schema | the v1.15 `EVIDENCE.{md,json}` row shape | LEDGER/Phase-99 consume it; consistency matters |

**Key insight:** Phase 97 invents no tooling — every measurement maps to an existing command. The only "new" artifacts are the captured data and the RCA verdict doc.

---

## Runtime State Inventory

> Not a rename/refactor/migration phase — but this is a diagnostic phase touching live hardware + saved config, so the analogous "what state must I confirm before measuring" inventory:

| Category | Items | Action |
|----------|-------|--------|
| Seated silicon | AM27C020, NOT-BLANK (`0x02 @ 0x0000`), UV, irreversible | [OP] confirm seated; never spend a 2nd program (D-01) |
| Live board config | Leonardo R1=270000, R2; `controller:` port (ACM shuffles) | [CLAUDE] `firestarter hw` per task (D-08) |
| Shield jumper state | JP4 = `JMP_VPP_P1_BYPASS`, Rev 2.0 = P1_VPP_JMP 1x2 header | [OP] confirm position + **ASK silkscreen meaning before toggling** (D-08) |
| Manual potentiometer | VPP magnitude (firmware can't set) | [OP] confirm pot setting each session (D-07) |
| Firmware commit | fw tip `bccd995…` (v1.17), app tip `e0bdea4…` | [CLAUDE] record per EVIDENCE row; this phase makes NO code change |
| Saved-config / port artifacts | none expected | [CLAUDE] verify no stale `FIRESTARTER_CONFIG_DIR` test seam in play (v1.15 gotcha) |

**Nothing found needing migration** — diagnostic phase, no code/data edit.

---

## Common Pitfalls

### Pitfall 1: "0 bits" misread as OTP
**What goes wrong:** treating the expected 0-flip as proof the chip is dead → spurious deferral. **Why:** on the broken path a 0-flip is consistent with both broken-path and OTP. **Avoid:** D-01 — INDETERMINATE pre-fix; deferral is a Phase-99 verdict only. **Warning sign:** any plan task that branches "if 0 bits → defer."

### Pitfall 2: Silent under-program (VPP-low WARNING-only)
**What:** a low VPP rail produces "0 bits, no error" with no block. **Why:** `vpp_check_window` LOW = WARNING/proceed [VERIFIED: primitives.cpp:144]; magnitude is a manual pot. **Avoid:** DMM pin 1 (12.5–13.0V) mandatory before trusting any verdict (D-07).

### Pitfall 3: DMM too slow for the 100µs pulse
**What:** probing the live pulse gives a meaningless averaged reading. **Avoid:** held-rail static proxy (`dev reg 0 0 0x188 -f`, D-05). **Warning sign:** "measure pin 31 during write" without the held rail.

### Pitfall 4: ADC node ≠ socket pin 1
**What:** the `firestarter vpp` ADC reads `PIN_VPP_VOLTAGE_ADC=A2` (the monitor node), not the chip socket. **Why it matters:** a divergence (ADC=13V, pin1=0V) localizes a P1/JP4 *routing* fault vs a pot *magnitude* fault — the most decisive single measurement. **Avoid:** always cross-check both.

### Pitfall 5: localized read glitch (N=1 untrustworthy)
**What:** v1.15 saw 12 bytes differ at 0x008004–0x00800f on this chip. **Avoid:** N≥3 byte-identical (consistency-check); an unstable oracle makes "0 bits" un-attributable (D-08).

### Pitfall 6: bit-alias collision (0x08 = P1_ENABLE == A18 on Rev2)
**What:** routing VPP to pin 1 also drives the A18/pin-31 line on Rev2 [VERIFIED: rurp_pinout.h:127]. **Why it matters:** confounds RC-1/RC-2/RC-4 — pin 31 and pin 1 may move together. **Avoid:** test the `0x180`-vs-`0x188` pair explicitly; document the collision in the verdict.

### Pitfall 7: irreversible UV spend
**What:** every program is permanent (no eraser). **Avoid:** exactly ONE micro-probe at `0x000000` (D-01); no full-image spend until Phase 98/99 with a fix in place. **Warning sign:** any task that writes a multi-byte image in Phase 97.

### Pitfall 8: toggling JP4 without knowing the silkscreen
**What:** flipping JP4 the wrong way could mis-route 12–13V. **Avoid:** ASK the operator the Rev 2.0 silkscreen open-vs-closed meaning first (D-08); the EEPROM hw byte cannot distinguish revs.

---

## State of the Art

| Old (brief's framing) | Sharpened (this session, code-verified) | Impact |
|-----------------------|------------------------------------------|--------|
| "pin 31 → line 22 corresponds to CTRL_READ_WRITE territory" | line 22's bit derives from `address>>16` bit 6 = 0x40; but the *control-register collision* that matters is `CTRL_VPP_P1_ENABLE == CTRL_ADDRESS_LINE_18 == 0x08` on Rev2 | RC-1/RC-4 boundary now has a concrete, testable bit-alias experiment (0x180 vs 0x188) |
| "DIP32_STD maps pin 31 as the 19th bus line" | confirmed: `DIP32_STD.address-bus-pins` ends `…30, 31` (index 18 = A18), `pin_conversions[32][31]=22` | RC-1 code-half verdict is airtight independent of the DMM |
| held-rail value unspecified (Claude's discretion) | `dev reg 0 0 0x188 -f` = regulator+VPE-drop+P1-route at addr 0 | concrete plannable command |

---

## Validation Architecture

> `workflow.nyquist_validation` is **absent** in `.planning/config.json` → treated as enabled. But this phase's "tests" are **bench measurements and code-analysis findings**, not unit tests. No code changes here, so no native/host suites run in Phase 97 (those gate Phases 98–99). Validation = the disconfirmation logic above + artifact completeness.

### "Test" Framework (bench/code-analysis framing)
| Property | Value |
|----------|-------|
| Framework | Bench measurement (held-rail DMM + ADC) + file:line code-analysis |
| Config | n/a (no test harness invoked this phase) |
| Quick run | `firestarter dev consistency-check AM27C020 --runs 3` (the read-oracle gate) |
| Full "suite" | the 6-step combined procedure + the differential + the SAFE-01 code-read |

### Phase Requirements → Validation Map
| Req | Behavior to validate | "Test" type | Command / method | Exists? |
|-----|----------------------|-------------|------------------|---------|
| PRE-01 | read oracle stable, blank SHA, micro-probe documented | bench | `info` + `consistency-check --runs 3` + `blank` + `write` (1 attempt) | ✅ commands exist |
| RCA-01 | failure reproduces with full signature | bench | Steps 1–6 + signature schema | ✅ |
| RCA-02 | differential isolates 32-pin/P1/PGM axes | bench | `0x07` W27C512 control write same session | ✅ |
| RCA-03 | RC-1 + RC-2 each carry a verdict; classified | analysis | disconfirmation table + verdict doc | ✅ (analysis) |
| SAFE-01 | guards intact, no bypass | code-read | grep/file:line confirm `vpp_check_window` ERROR + `resolve_chip` in path | ✅ verified |

### Sampling / gates
- **Per bench task:** re-confirm `controller:` identity + R1/R2 (`firestarter hw`) (D-08).
- **Read verdict gate:** N≥3 byte-identical before trusting any write outcome.
- **Phase gate:** RC-1 AND RC-2 each have a recorded verdict (D-03) + EVIDENCE row complete + RCA-FINDINGS doc written.

### Wave 0 Gaps
- None — no test infrastructure to build; all commands exist. The only "scaffold" is the EVIDENCE/RCA-FINDINGS artifact files (see Artifacts below).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `firestarter` host CLI | every bench/code step | ✓ (devcontainer; use /usr/local python; `pip install -e '.[test]'` if toolchain wiped) | app `e0bdea4` | — |
| Leonardo + RURP Rev 2.0 over USB passthrough | all bench steps | ✓ (operator bench, USB passthrough) | fw `bccd995` | — (bench-locked, no substitute) |
| Operator DMM at socket pin 1 & pin 31 | RC-1/RC-2 decisive measurement | ✓ (operator) | — | code-analysis alone is partial; DMM is the bench half |
| Seated AM27C020 | PRE-01/RCA-01 | ✓ (operator seats) | — | — |
| Logic analyzer | live-pulse pin-31 confirmation | OPTIONAL | — | held-rail static proxy (D-05) is the gating method |

**Missing with no fallback:** none.
**Caveat:** firestarter_app devcontainer Python is 3.12 which masks CI (py3.9/3.11) — irrelevant this phase (no code change) but note for Phase 98.

---

## Artifacts the Phase Should Emit (for the planner to make task deliverables)

1. **EVIDENCE row** (extend `.planning/v1.15/bench/EVIDENCE.{md,json}` shape, or a v1.18 bench dir) — one row for the `0x08` AM27C020 attempt + one for the `0x07` W27C512 differential control, with the Failure Signature Capture Schema fields.
2. **RCA-FINDINGS doc** (mirror v1.17 Phase-93 `evidence/93-RCA-FINDINGS.md`) — containing: reproduced signature, the differential matrix, the RC-1..RC-5 disconfirmation table each with its bench/code verdict, the named root cause (or ranked hypotheses), classification (firmware-algorithm / host-pinout / VPP-routing / addressing / silicon), and the Phase-98 hand-off (which fix surfaces the verdict implicates). RC-1 AND RC-2 must each carry a verdict (D-03).
3. **SAFE-01 confirmation note** — file:line evidence the over-voltage ERROR + host guard are intact and unbypassed.
4. **PRE-01 result line** — "writability indeterminate pre-fix" (or "partial — N bits flipped"), blank-state SHA, identity/decode confirmation (D-02).

The PROTOCOL-LEDGER `0x08` entry stays `open-defect-carried (FUT-06)` this phase; Phase 99 updates it.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Held value `0x188` (regulator+VPE-drop+P1-route, addr 0) faithfully reproduces the program-window control state for the static proxy | Held-Rail Procedure | LOW — derived from verified program-time bits; if the firmware also toggles other bits transiently the proxy under-represents, but pin1/pin31 steady-state is still informative. Operator/bench will reveal. Marked `[ASSUMED]` pending the first bench reading. |
| A2 | At `address 0x000000` pin 31 idles VIL (program-active) because A18=0 | RC-1 logic | LOW — code-verified that bus line 22 = 0 at addr0; the *socket* level is the open question the DMM settles (which is the point). |
| A3 | The v1.15 `bad bytes 15/16, retries 20` signature reproduces on the current fw tip `bccd995` | RCA-01 | MEDIUM — fw changed since v1.15 (VPP-skip on reads, recompose); write path believed untouched, but re-verify the exact retry count on the current tip. |
| A4 | JP4 closed = 32-pin VPP-to-pin-1 engaged on Rev 2.0 | RC-3 | MEDIUM — operator must confirm silkscreen meaning (D-08); do not assume. |

**These are the items discuss-phase / the operator should confirm at the bench before the verdict is locked.**

---

## Open Questions

1. **Does the `0x08 = P1_ENABLE == A18` bit-alias (Rev2) confound the measurement?**
   - Known: the two are the same control bit (0x08) [VERIFIED: rurp_pinout.h:127].
   - Unclear: whether asserting P1-route inadvertently sets pin-31/A18 high in a way that matters at addr0.
   - Recommendation: test the `0x180`-vs-`0x188` pair explicitly (a single experiment covering RC-1/RC-2/RC-4).

2. **Exact retry/bad-byte count on the current fw tip vs the v1.15 seed.**
   - Recommendation: re-capture rather than cite v1.15 numbers as current.

3. **Does pin 1 (DMM) match the ADC node, or diverge?**
   - The decisive RC-2 measurement; cannot be predicted from code — bench answers it.

---

## Sources

### Primary (HIGH confidence — read direct this session, live tree)
- `firestarter/src/proms/eprom.cpp` — `program_mismatched_bytes` (:168-179), `eprom_write_execute` (:197-204), `eprom_check_vpp` (:263-281), `eprom_internal_set_control_register` CTRL_VPE_ENABLE→CTRL_VPP_P1_ENABLE rewrite (:319-326).
- `firestarter/src/proms/memory.cpp` — dispatch→configure_eprom (:122), `mem_util_calculate_top_address_register` (:184-198), `memory_set_data` CE-only pulse (:274-284), `mem_util_remap_address_bus` (:309).
- `firestarter/src/proms/primitives.cpp` — `vpp_check_window` LOW=WARN (:144), HIGH=ERROR (:122-126).
- `firestarter/include/rurp_pinout.h` — CTRL_* bits (:75-96), Rev2 `CTRL_ADDRESS_LINE_18_REV2 == CTRL_VPP_P1_ENABLE_REV2` alias (:122,128).
- `firestarter/include/memory_utils.h` — `using_p1_as_vpp` (:24-28).
- `firestarter/include/rurp_shield.h` — `VPP_P1_32_DIP=0x15` (:40), `CHIP_ENABLE` / `rurp_chip_enable` (:57,104-110).
- `firestarter_app/firestarter/database.py` — `pin_conversions[32][31]=22` (:141), PROTOCOL_MAP 0x08=EPROM_QUICK.
- `firestarter_app/firestarter/data/pinouts.json` — `DIP32_STD` (pin 31 = 19th address-bus pin; comment flags PGM-vs-A18 ambiguity), `DIP32_SST39SF040` (pin 31 = WE — the must-not-break family).
- `firestarter_app/firestarter/data/chip_database.json` — AM27C020 entry: protocol 8, DIP32_STD, vpp_mv 13000, chip-id 0x197, 100µs.
- `firestarter_app/firestarter/cli_handlers.py` — `vpp` (:659), `vpe` (:671), `dev reg -f` + bit map (:983-1031), `dev consistency-check` (:1082).

### Curated substrate (HIGH — in-repo / authoritative)
- `.planning/research/v1.18-AM27C020-27C-EPROM.md` — the RCA brief (datasheet facts, RC-1..RC-5, Tier-0, VPP method).
- `firestarter/datasheets/0x08-EPROM-QUICK/AM27C020.pdf` — VPP 12.75V±0.25, Flashrite 100µs CE+PGM=VIL, 32-pin pinout, 13.5V abs-max.
- `firestarter/doc/SHIELD-REVISIONS.md` §7 + `.planning/v1.7-SHIELD-REVS.md` §3/§4 — JP4 = JMP_VPP_P1_BYPASS, Rev 2.0 = P1_VPP_JMP 1x2 header.
- `.planning/v1.15/bench/EVIDENCE.{md,json}` — pre-fix seed signature.
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.{md,json}` — 0x08 = open-defect FUT-06; 0x07 PASS.

### Memory (HIGH — operator-attested)
- `reference_v114_bench_erase_rail_and_test_artifact` (held-rail `dev reg … -f`), `reference_vpp_vpe_no_socket_routing` (monitors measure-only), `project_v117_w29c040_locked_bootblock` (Tier-0 / clean-deferral lesson), `user_shield_revisions` (ASK Rev), `project_phase83_shipped` (AM27C020 0x08 fail seed, FIRESTARTER_CONFIG_DIR seam).

---

## Metadata

**Confidence breakdown:**
- Bench procedure / command sequencing: HIGH — every command verified present in the live CLI.
- RC-1 mechanism (pin 31 as address line): HIGH — code-verified end-to-end (pinouts.json → database.py:141 → memory.cpp:346/184). Whether it is *solely* causal: MEDIUM (bench decides).
- RC-2 mechanism (P1 VPP routing/level): HIGH on the code path (eprom.cpp:319-326); MEDIUM on whether the rail actually fails at pin 1 (bench/DMM decides).
- Held-rail value `0x188`: MEDIUM — derived from verified bits, marked `[ASSUMED]` pending first bench reading (A1).
- SAFE-01 intact: HIGH — verified file:line.

**Research date:** 2026-06-29
**Valid until:** ~2026-07-29 (stable internal codebase; re-verify file:line if the firmware tip advances past `bccd995` before Phase 97 executes).
