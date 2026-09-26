---
artifact: 97-RCA-FINDINGS
phase: 97-pre-rca-tier-0-pre-flight-root-cause-the-0x08-0-bits-program
milestone: v1.18 — AM27C020 0x08 Write-Path RCA & Fix
requirements: [PRE-01, RCA-01, RCA-02, RCA-03, SAFE-01]
status: COMPLETE — RCA closed; root cause RC-1 named + classified; Phase-98 hand-off set
recorded: 2026-06-30
operator_witnessed: true (Plans 02/03 bench session, Leonardo + Rev 2.0, 2026-06-30)
branch_base: firmware bccd995 (v1.17 tip) · host e0bdea4
---

# AM27C020 `0x08` 0-Bits-Programmed Fault — Root-Cause Findings

> **RCA scope:** AM27C020 (AMD 256K×8 CMOS UV-EPROM, 32-pin DIP, protocol `0x08`
> "EPROM-QUICK") programs **0 bits** on the current path — `write` fails
> deterministically at `0x000000` (`bad bytes 15/16, retries 20`, v1.15 Phase
> 83/84) while its `0x07` sibling W27C512 wrote clean the same session. This
> document accumulates bench + code evidence across Plans 02–03 and culminates in
> a named root cause (or ranked disconfirmed hypotheses) classified
> firmware-algorithm / host-pinout / VPP-routing / addressing / silicon —
> sufficient for **Phase 98** to design the fix without further RCA.
>
> **Branch base:** firmware `bccd995` (v1.17 tip) · host `e0bdea4`.
> **Differential control:** W27C512 (`0x07`, same `configure_eprom()`, same
> session/bench) — exonerates the unchanged axes.
> **SAFE-01:** confirmed non-invasively in [SAFE-01-PREFLIGHT.md](SAFE-01-PREFLIGHT.md)
> (over-voltage ERROR path intact, host guard never bypassed; read-only).
>
> **STATUS: COMPLETE (Plans 02–03, 2026-06-30).** All bench data below is filled
> from real captures; per **D-02** nothing here is fabricated (tooling-blocked
> measurements are recorded "not measured", never guessed).

---

## Bench Discipline Log (D-08)

All bench tasks (Plans 02–03) record their session identity here before any chip
operation. Standing discipline from CONTEXT.md D-08.

| Plan | Timestamp | Controller identity (`firestarter --version`) | Port | R1 | R2 | Board | Shield | JP4 position + silkscreen meaning | fw commit | Notes |
|------|-----------|-----------------------------------------------|------|----|----|-------|--------|-----------------------------------|-----------|-------|
| 02 | 2026-06-30 ~07:29Z | leonardo (fw 3.0.0b10) | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0 | **open** (operator-stated); meaning PENDING (D-08) — fw `info` says 32-pin=**Closed**, **discrepancy flagged** | bccd995 | R1 in-band (203k–338k); VPP adjusted 12.0→13.0V before Task-3 |
| 03 | 2026-06-30 ~09:40Z | leonardo (fw 3.0.0b10) | /dev/ttyACM0 | 270000 | 44000 | Leonardo | Rev 2.0 | **open** (28-pin position for W27C512) | bccd995 | 0x07 control. VPP 12.0V (W27C512 target). First seated ST M27C512 (0x203d/13V/UV) → swapped to Winbond W27C512 (0xda08/12V/EEPROM) |

R1 expected ≈ 270000 ± 25% (Leonardo). `controller:` re-verified per task (ACM ports shuffle). Leonardo is chip-OUT-sideload-EXEMPT. Every program on this UV part is irreversible (no eraser on hand).

---

## PRE-01 — Tier-0 Writability Pre-Flight

> **Deliverable (D-02):** "writability **INDETERMINATE** pre-fix" — NOT a
> pass/fail blocker. The phase does not stall on a definitive writability verdict;
> the true writable/dead gate is the post-fix Phase 99 bench (D-04/D-06).

| Item | Method | Result |
|------|--------|--------|
| Read oracle stable (N≥3 byte-identical) | `firestarter dev consistency-check AM27C020 --runs 3` | **PASS** — 3/3 byte-identical, distinct SHAs = 1 (each run 262144 B, ~43s) |
| Blank-state SHA256 | consistency-check (known NOT-BLANK `0x02 @ 0x0000`) | `90cd45f5343cd938006f20635de39479159c51b9d56c1b6f1fb23075ed567297` |
| Identity / protocol decode confirmed | `firestarter info AM27C020` | **CONFIRMED** — UV-EPROM, DIP32, 0x40000, VPP 13.0V, protocol **0x08**, chip-id **0x197**. ⚠ pinout shows **pin 31 = A18** (RC-1 premise); fw jumper guidance **32-pin = JP4 Closed** (operator has open) |
| Blank check | `firestarter blank AM27C020` | **NOT-BLANK** @ `0x000000` = `0x02` (matches v1.15) |
| Baseline rails (RCA-01 instrumentation) | `firestarter vpp` / `vpe` | as-found VPP **12.0V** (below 12.5–13.0V band) → operator set **13.0V**; VPE 13.8V→**15.1V** (shares regulator) |
| Micro-probe attempt result | combined Tier-0 probe = RCA-01 program attempt at `0x000000` (ONE attempt, D-01) | **DONE** — `write -b` (blank-check skip only; chip non-blank), 0 bits flipped, chip pristine → **writability INDETERMINATE pre-fix** (NOT OTP; no deferral). Exactly one irreversible attempt spent; SAFE-01 held (flags=0x08, no FLAG_FORCE) |

**Framing (D-01/D-02):** the Tier-0 micro-probe and the RCA-01 reproduction are
the **same single bench action** — one `1→0` program attempt at `0x000000` on the
current (unfixed) path. On the broken path a **0-bit-flip is INDETERMINATE**
(consistent with both "our path is broken" AND "chip is OTP") — it does **not**
prove OTP and a **0-flip NEVER triggers deferral**. The chip stays pristine. Any
bit flipping ⇒ RC-5 total-silicon-block is OUT and writability is partially proven
(signature recorded as "partial").

---

## RCA-01 — Reproduction & Signature

Failure Signature Capture Schema (filled by Plan 02 into `EVIDENCE.{md,json}` Cell A):

| Field | Value |
|-------|-------|
| failing address(es) / bytes | **0x000000** (byte stays `0x02`, target `0x00`) |
| bad bytes / retries | **1/1, retries 20** (`ERROR: Failed to write memory, 0x000000, retries: 20, bad bytes: 1`; retries matches v1.15 seed) |
| bits flipped | **0** → writability INDETERMINATE pre-fix (D-01/D-02; NOT OTP, no deferral) |
| VPP ADC readback | **13.0V** (operator-set; confirmed immediately pre-attempt) |
| DMM pin 1 (held proxy) | **not measured** — held-rail proxy blocked by DTR-reset-on-close tooling bug ([debug: held-rail-dev-reg-timeout](../../../debug/resolved/held-rail-dev-reg-timeout.md), H1 confirmed). Routing **confirmed by code RCA** instead: `-f 0x188` → physical `CTRL 0x89`, P1-route asserted on Rev 2.0 (H2 disproven) — VPP **does** reach pin 1 |
| DMM pin 31 (held proxy) | **not measured** — same tooling block; pin 31 = **A18** confirmed by `firestarter info` pinout decode (RC-1 premise) |
| pre/post read SHA256 | `90cd45f5…ed567297` **== identical → chip pristine** (N=3 both before and after) |
| controller / port / R1R2 / fw commit | leonardo / /dev/ttyACM0 / R1 270000 R2 44000 / bccd995 |
| JP4 position + silkscreen meaning | **closed** for the attempt (operator moved open→closed, matching fw `info` 32-pin=Closed); silkscreen meaning still PENDING (D-08) |

> A3 (MEDIUM risk): the v1.15 `bad bytes 15/16, retries 20` signature is re-captured
> on the current fw tip `bccd995` rather than cited as current; the write path is
> believed untouched but the exact retry count is re-verified at the bench.

---

## RCA-02 — `0x07`-vs-`0x08` Differential Matrix

> Method: same bench, same session, same `configure_eprom()` handler; vary only the
> named axis; the passing W27C512 (`0x07`) exonerates the unchanged axes (v1.17
> 2×N method). Verdicts recorded below (W27C512 0x07 control = PASS).

| Axis | 0x07 W27C512 (PASS) | 0x08 AM27C020 (0-bits) | Differs? | How 0x07 exonerates | Verified anchor |
|------|---------------------|------------------------|----------|---------------------|-----------------|
| Handler | `configure_eprom()` | `configure_eprom()` | NO | same path passes ⇒ not handler-selection | `memory.cpp:122` |
| Pulse width | 100µs | 100µs | NO | identical ⇒ not pulse width | `eprom.cpp` pulse_delay |
| Program pulse model | CE-only strobe | CE-only strobe | NO (same) | 0x07's PGM tied OK by 28-pin layout; 0x08 needs pin-31 PGM | `memory.cpp:346` |
| **VPP routing** | `vpp_line=0xFF` ⇒ VPE-drop bus line, NOT P1 | `vpp_line=21` (VPP_P1_32_DIP=0x15) ⇒ **P1 / socket pin 1** | **YES** | 0x07 proves regulator+drop network; only the **P1 leg** is unproven on a UV part | `eprom.cpp:319-326`; `memory_utils.h:24` |
| **Program-enable bit** | `CTRL_VPE_ENABLE` reaches VPE/PGM line | rewritten to `CTRL_VPP_P1_ENABLE` | **YES** | 0x07 proves CTRL_VPE_ENABLE path; the rewrite is 0x08-only | `eprom.cpp:319-326` |
| **Pin 31 role** | 28-pin: no pin 31 issue | 32-pin: **pin 31 = bus line 22 (address-driven), not PGM** | **YES** | 0x07 has no 32-pin pin-31 mapping ⇒ exonerates all but the 32-pin axis | `database.py:141`; `pinouts.json DIP32_STD` |
| Pin 1 role | VPP on a different bus line | VPP on socket pin 1 (P1) | YES | 32-pin VPP geometry | — |
| FLAG_CAN_ERASE | set (EEPROM auto-erase) | 0 (UV — correct) | minor | not erase-related | — |

**Two-axis collapse:** the matrix collapses to **P1-VPP-delivery** + **pin-31-as-address** — both in the 32-pin/`0x08` region, both absent on the passing `0x07` part. **W27C512 differential verdict: PASS** — byte-exact `0x07` write→verify→readback (image SHA `d9471636…` matched; write 6.52s, verify 0.64s) on the seated Winbond W27C512 (12.0V VPP, JP4 open, same session/handler). The passing sibling **exonerates every shared axis**; only the two 32-pin axes remain. (Note: operator first seated an ST M27C512 (id `0x203d`, UV, 13V) — chip-ID check aborted the write so it stayed pristine — then swapped to the intended electrically-erasable Winbond W27C512 for a clean reversible control.)

---

## RCA-03 — RC-1..RC-5 Disconfirmation Table

> **D-03 callout:** **RC-1 AND RC-2 must EACH carry an individual verdict**
> (confirm-or-exonerate) before Phase-98 handoff — they may compound (a one-axis
> fix could still flip 0 bits). **RC-3 (JP4) and RC-4 (addressing collision) are
> pursued ONLY IF** RC-1+RC-2 do not fully account for the 0-bits symptom. RC-5 is
> handled via the Tier-0 path and **never triggers deferral pre-fix** (D-01/D-06).

| RC | Hypothesis | CONFIRM if… | EXONERATE (OUT) if… | Method | Gating? | Verdict |
|----|-----------|-------------|---------------------|--------|---------|---------|
| **RC-1** | PGM pin 31 modeled as address line, not held program-active | pin 31 DMM reads VIH/floats during held proxy | pin 31 DMM reads ~0V (VIL) AND code shows it driven low at addr0 | Held-rail static proxy (`0x188`) + code-analysis (`memory.cpp:346` + `database.py:141` + `pinouts.json`) | **YES (D-03)** | **CONFIRMED (leading)** — code + differential + elimination. `database.py:141` `pin_conversions[32][31]=22` → pin 31 modeled as bus-line-22 **address (A18)**, not a held PGM; `memory.cpp:346` strobes **CE only**. The passing 0x07 28-pin sibling (no pin-31 mapping) + **RC-2 exonerated** (VPP reaches pin 1) ⇒ by elimination the 0-bits cause is **pin 31 never asserted program-active**. Direct pin-31 DMM was tooling-blocked ([debug](../../../debug/resolved/held-rail-dev-reg-timeout.md)); verdict rests on code + the 0x07/0x08 differential. |
| **RC-2** | VPP not reaching pin 1 at 12.5–13.0V during pulse | pin 1 DMM ≈0V/floats while ADC≈13V (routing), OR pin1 <12.5V (pot/level) | pin 1 DMM = 12.5–13.0V steady AND ADC agrees | Held-rail proxy (`0x188`) + DMM pin1 + `firestarter vpp` ADC cross-check | **YES (D-03)** | **EXONERATED** — code + level. `-f 0x188` → physical `CTRL 0x89`, **P1-route asserted** (H2 disproven, [debug](../../../debug/resolved/held-rail-dev-reg-timeout.md)) ⇒ VPP routed to pin 1; level set 13.0V, ADC-confirmed, for the 0x08 attempt. The 0x07 sibling PASS proves regulator+VPE-drop+pulse. (Bench pin-1 DMM tooling-blocked → routing is **code-confirmed, not DMM-confirmed** — the one residual link.) |
| **RC-3** | JP4 (`JMP_VPP_P1_BYPASS`) position wrong for 32-pin VPP-to-pin-1 | toggling JP4 changes pin-1 VPP delivery decisively | neither JP4 position delivers 12.5–13.0V to pin 1 | [OP] toggle JP4 open↔closed, re-DMM pin 1 — **ASK silkscreen meaning first (D-08)** | only if RC-1+RC-2 incomplete | **Not pursued** — D-03 trigger not met (RC-1 accounts for the symptom). JP4 was set **closed = 32-pin** for the 0x08 attempt per fw `info` guidance, so position was correct. |
| **RC-4** | 32-pin high-address / control-bit collision corrupts target | high-address write behaves differently than addr0 | addr0 still 0-bits with pin1=13V AND pin31=VIL | code-analysis (`memory.cpp:187-202` alias `A18==P1_ENABLE` 0x08) + optional high-addr inspect (NOT a second destructive spend) | only if RC-1+RC-2 incomplete | **Not pursued** — D-03 trigger not met. The 0x08 firmware alias (`CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2 == 0x08`, `rurp_pinout.h:127`) is **dormant at A18=0** (address 0); flagged as a **Phase-98 fix-design** concern, not a separate Phase-97 cause. |
| **RC-5** | Chip OTP/dead (total silicon block) | (cannot be confirmed pre-fix — D-01 INDETERMINATE) | any bit flips in the Tier-0 micro-probe | the combined micro-probe (PRE-01/RCA-01) | handled via Tier-0; **never triggers deferral pre-fix** | **INDETERMINATE pre-fix** — the one attempt flipped 0 bits (consistent with both broken-path AND OTP). Per D-01/D-06 this **never triggers deferral** (deferral is a Phase-99 verdict only). |

**Conditional trigger (D-03):** pursue RC-3/RC-4 only if, after RC-1 and RC-2 each
carry a verdict, the resolved pair does **not** fully account for 0-bits. If both
RC-1 (pin 31 = VIL OK) and RC-2 (pin 1 = 13V OK) come back EXONERATED yet the chip
still flipped 0 bits, the symptom is unexplained → escalate to RC-3 (JP4) and RC-4
(addressing collision); the alias-collision finding (`0x08` = A18 == P1_ENABLE in
the firmware physical layout) becomes the leading RC-4 lead.

### Named Root Cause / Classification

**Named root cause (RC-1, CONFIRMED leading):** On the `0x08` EPROM-QUICK 32-pin
write path, **socket pin 31 is modeled as address line A18** (`DIP32_STD`
`pin_conversions[32][31]=22`, `database.py:141`) rather than as a **held
program-active (PGM/control) pin**. The program engine strobes **CE only**
(`memory.cpp:346`), so the seated AM27C020 receives **VPP correctly at pin 1**
(RC-2 exonerated: `-f 0x188` → physical `0x89`, P1 asserted; level 13.0V) yet
**never sees a program-enable on pin 31** → the cell is never programmed →
**0 bits flipped**. The passing `0x07` 28-pin sibling (no 32-pin pin-31 mapping)
writes byte-exact in the same session, exonerating every shared axis.

**Classification: `host-pinout` (primary) + `firmware-algorithm` (secondary).**
The pin-31 mapping lives in the host pinout/DB (`DIP32_STD` + `database.py`); the
CE-only program-pulse model that assumes no separate PGM assertion is the
firmware-algorithm half. NOT `vpp-routing` (RC-2 exonerated), NOT `silicon`
(RC-5 INDETERMINATE, never deferral), NOT `addressing-collision` (RC-4 dormant at
A18=0).

**Residual (one unmeasured link):** the direct pin-31 DMM was tooling-blocked
(held-rail proxy DTR-reset bug, [debug](../../../debug/resolved/held-rail-dev-reg-timeout.md));
RC-1 rests on code + the 0x07/0x08 differential + RC-2 elimination. Phase-98 fix
validation (byte-exact write after redirecting pin 31) closes it empirically.

---

## Held-Rail Static-Proxy Control Values (RC-1/RC-2/RC-4 decisive experiment, D-05)

> Pinned against the **live host `dev reg -f` bit map** (re-read this session):
> `firestarter_app/firestarter/cli_handlers.py:1010-1018`. In the host `-f`
> (hardware-revision-remapped) namespace the bits are **DISTINCT**:

| Host `-f` bit | Name (cli_handlers.py:1010-1018) |
|---------------|----------------------------------|
| `0x100` | CTRL_VPP_VPE_DROP_ENABLE |
| `0x080` | CTRL_VPP_REGULATOR_ENABLE |
| `0x040` | CTRL_READ_WRITE |
| `0x020` | CTRL_ADDRESS_LINE_18 |
| `0x010` | CTRL_ADDRESS_LINE_17 |
| `0x008` | CTRL_VPP_P1_ENABLE |
| `0x004` | CTRL_VPE_ENABLE |
| `0x002` | CTRL_VPP_A9_ENABLE |
| `0x001` | CTRL_ADDRESS_LINE_16 |

**Program-window held value** (P1 route ON, A18/pin-31 bit clear, address 0):

```
CTRL = 0x080 | 0x100 | 0x008 = 0x188   (regulator + VPE-drop + P1-route)
firestarter dev reg 0 0 0x188 -f       [A1 RESOLVED by code RCA — see note below]
```

> **A1 RESOLVED (2026-06-30, NOT by bench reading — by code decode).** The bench
> held-rail DMM read was **blocked** by a tooling bug: `dev reg … -f` sets the rail
> but `expect_ack()` times out (firmware busy-waits on the user button, UART down)
> and the host `finally: _disconnect_programmer()` closes the port → pyserial
> de-asserts DTR → **resets the Leonardo** → the `74HC573` latch zeroes → pin 1
> drops to ~0V before it can be measured. Full RCA + non-invasive `hold_rail.py`
> workaround + Phase-98 fix in
> [debug/resolved/held-rail-dev-reg-timeout.md](../../../debug/resolved/held-rail-dev-reg-timeout.md).
> The decisive question the proxy was for — *does `0x188` route VPP to pin 1?* — was
> instead answered by code: `0x188` → `rurp_map_ctrl_reg_for_hardware_revision`
> (REVISION_2_0) → physical **`CTRL 0x89` = REGULATOR + P1 + VPE_DROP_REV2**; the
> `CTRL_VPP_P1_ENABLE_REV2 == CTRL_ADDRESS_LINE_18_REV2` alias is NOT triggered (A18
> input bit `0x20` unset). **P1-route IS asserted → VPP reaches pin 1** (RC-2-routing
> exonerated by code; H2 disproven).

- `MSB=0 LSB=0` → address `0x0000` (all address lines low, matching the failing
  address; pin 31 = bus line 22 = A18 = 0).
- `-f` applies the Firestarter hw-rev-remapped bit definitions.

**Alias-probe pair** (moves ONLY the host `0x008` P1_ENABLE bit):

```
firestarter dev reg 0 0 0x180 -f       (P1 route OFF: regulator + VPE-drop only)
firestarter dev reg 0 0 0x188 -f       (P1 route ON: + CTRL_VPP_P1_ENABLE)
```

This single `0x180`-vs-`0x188` experiment touches RC-1, RC-2 and RC-4
simultaneously — it reveals whether pin 31 and pin 1 move together.

### Host-vs-firmware bit-alias caveat (CRITICAL — Pitfall 6)

In the **firmware physical Rev2 layout** (`firestarter/include/rurp_pinout.h:121,127`)
`CTRL_VPP_P1_ENABLE_REV2` and `CTRL_ADDRESS_LINE_18_REV2` are the **SAME control
bit (0x08)**:

```
#define CTRL_VPP_P1_ENABLE_REV2     0x08      // rurp_pinout.h:121
#define CTRL_ADDRESS_LINE_18_REV2   CTRL_VPP_P1_ENABLE_REV2   // rurp_pinout.h:127  (== 0x08)
```

But the host `dev reg -f` remap **presents them as distinct host bits**
(`0x008` = P1_ENABLE, `0x020` = ADDRESS_LINE_18). Therefore the operator/Claude
**MUST use the host `-f` values above** (`0x188` / `0x180`), NOT the firmware
physical bit numbers. The held value **`0x188` is marked [ASSUMED — confirm at
first bench reading]** per RESEARCH assumption A1 (derived from the verified
program-time bits; the bench settles whether it faithfully reproduces the
program-window state).

For a 256K AM27C020, A18 is never set, so the firmware-side alias is dormant at
the addresses in play — but it is directly relevant to the RC-1/RC-4 boundary and
to any Phase-98 fix.

---

## SAFE-01 Close-Out

SAFE-01 confirmed non-invasively in
[SAFE-01-PREFLIGHT.md](SAFE-01-PREFLIGHT.md): over-voltage `vpp_check_window`
HIGH→ERROR path intact (relaxes to WARNING only under FLAG_FORCE, which the
procedure never passes); host `resolve_chip` guard never bypassed; normal `0x08`
dispatch; zero code edits. Recurs as a standing precondition through Phases 98–99.

---

## Phase-98 Hand-Off

> The named root cause (RCA-03) governs the Phase-98 fix surface. **Verdict: RC-1
> (host-pinout + firmware-algorithm) — pin 31 modeled as address line A18, not a
> held PGM.** Fix surfaces below.

Fix surfaces per the confirmed RC-1 verdict (for Phase-98 planning, not a Phase-97
finding):

- **RC-1 (host-pinout, leading):** a dedicated `DIP32_27C020` pinout entry
  redirecting pin 31 from the address bus to a held PGM control, scoped to the
  `0x08`-UV-32-pin class so existing 27C040/SST39SF040-family DIP32 users
  (pin 31 = A18/WE) are not broken (`pinouts.json` + `database.py`).
- **RC-2 (vpp-routing):** hold `CTRL_VPP_P1_ENABLE` (P1 route) across the full
  program pulse window rather than only the per-byte data-write window
  (`eprom.cpp`).
- Possible new wire field (`firestarter.h` ↔ `constants.py` lockstep) if a new
  control-pin concept is needed (precedent: v1.17 per-chip `page_size`).
