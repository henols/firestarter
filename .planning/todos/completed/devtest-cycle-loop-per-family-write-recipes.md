---
title: "`dev test` cycle-loop executor + per-family write recipes (fixes a write repeat that emits no pulses on 44% of chips)"
date: 2026-08-22
priority: high
size: milestone-sized (not a quick task)
needs_bench: yes
origin: design discussion with the operator, 2026-08-22, fully aligned
status: DONE — implemented and merged to beta 2026-08-22
implemented_in: firestarter_app 27021b3..b95f52a, merged as bf1fdc9
---

> ## ✅ DONE, 2026-08-22 — implemented in the same session it was scoped
>
> The operator said "do the work and merge and push to beta", so this never
> became a milestone. Four commits on `quick-devtest-runcount-fast`, merged to
> `firestarter_app`'s `beta` as `bf1fdc9`:
>
> | Commit | Decisions |
> | --- | --- |
> | `27021b3` | D-1, D-3 — cycle-block executor and aggregation |
> | `9028721` | D-2, D-6, D-8 — per-family payloads, UV tranches, cycle-aware slot floor |
> | `2b42dac` | D-4, D-9 — full-device UV write and prompt retired, rig life reported; **D-5 DECLINED** |
> | `b95f52a` | D-10, D-11 — rig-health reframing in help and docs |
>
> **Three deviations from the decisions below, all recorded in the commits
> rather than smoothed over:**
>
> 1. **D-3's cycle order was not adopted.** D-3 specified `erase → blank-check
>    → write → verify`, which would have reordered `derive_plan`'s emission and
>    every step-order assertion in the suite. The shipped cycle keeps today's
>    `write → verify → erase → blank-check` and repeats it, which achieves the
>    same property from cycle 2 on. Only cycle 1's write can start from an
>    unknown state.
> 2. **D-6's premise was wrong, in our favour.** It assumed staging would cost
>    extra bits and sized tranches at a 128-bit floor to limit the damage. It
>    costs *nothing*: the final staged image equals `current & desired`, so the
>    part ends exactly where one unstaged write leaves it. Tranches are sized
>    by splitting the existing expenditure instead.
> 3. **D-5 was DECLINED.** Its premise did not survive contact with the code
>    and the operator asked to be told if it did not. `uv_slot_starts` is
>    already TOP-DOWN, so the first slot chosen is the highest address and
>    high-address write coverage existed from run 1 — the problem D-5 solved
>    was never there. It also could not have round-robined: a run saturates its
>    whole slot, so every unused slot ties on remaining bits.
>
> **Still not done: any hardware.** Nothing here has touched a real chip. The
> bench obligation below stands, and is now the only outstanding item.

# `dev test` cycle-loop executor + per-family write recipes

**Status: design AGREED with the operator on 2026-08-22.** Every open question
below was put to them and resolved; the resolutions are recorded as decisions,
not options. Nothing here needs re-litigating — it needs planning, research on
the mechanics, and a bench session.

## The defect

`run_plan`'s N≥2 repeat policy (v1.21 Phase 121, D-05/D-06) sends the **same
payload to the same address** on every run. That is deliberate — two runs'
outcomes are only comparable with the input held constant — but the consequence
was never traced through the firmware:

- Firmware `src/proms/eprom.cpp` **LOOP-06** (Phase 141, 2026-08-10, commit
  `3504e50`) skips a byte *before any pulse* when `expected == 0xFF` or the byte
  already reads back as expected. After a successful write #1 **every** byte
  qualifies, so **write #2 emits zero programming pulses.** On 0x07/0x08 it then
  does a final full-block read-compare, so write #2 is functionally a *verify*.
- Reached by `PROTO_EPROM_28PIN` / `32PIN` / `24PIN` only
  (`src/proms/memory.cpp:119-122`) = **329 of 746 rows**: 301 UV-EPROM + 28
  27-series EEPROMs.
- So `write, write, verify, verify` on those chips is really *write, verify,
  verify, verify*.
- `marginal` on such a write is reachable ONLY as "attempt 1 failed, attempt 2
  recovered" (write #1 aborts at the first byte to exhaust `max_pulses`, so
  write #2 does pulse from there on). It **cannot** catch a path that works once
  and then degrades.
- The AM27C020 write#1/write#2 divergence this policy is usually credited with
  (v1.18 Phase 99) **predates** LOOP-06, so it was measured against a different
  loop. Do not cite it as evidence about today's behaviour.

The same *class* of hazard reaches the other 417 rows by a different mechanism:
they write unconditionally, so pulses do go out, but if those pulses had no
**effect** the read-back verify still passes because the data was already
correct. Precedent: gh#11 was exactly this — recorded in `eeprom_28c.cpp` as
*"a whole-byte equality compare that passed spuriously whenever the old byte
already equalled the new one."*

**The principle:** a verify only proves the write worked if the write had to
change something.

**The codebase already argued this once, and scoped the fix too narrowly.**
`chip_test.py:418`, the SDP leg's LEG-04 rationale for needing two baseline
writes in opposite directions: *"a single baseline write cannot discriminate a
dead write path from a chip already holding the target pattern."* The main write
step never inherited it.

## Framing that governs every decision below

**`dev test` validates the firmware, host and database for a chip TYPE. It is
not a chip qualification tool.** (Operator, 2026-08-22: *"we are not here to
test EPROMs, it's about testing the firmware."*) Consequences:

- Cell-coverage tests are out of scope. An all-zeros UV pass was proposed and
  **rejected** on these grounds — it is cell qualification, and it permanently
  saturates the region.
- Bits consumed on a UV part are **runs lost**. A part that survives hundreds of
  runs against successive firmware revisions is worth far more than one
  maximally-characterised run.
- A cycle needs only enough real work to prove the algorithm *fired*.

## Finding that shrinks the UV problem

`eprom_params.cpp` is keyed on `protocol_id` alone. `handle->vpp_mv` is used
**only** as a comparison target in `eprom_check_vpp`
(`src/proms/eprom.cpp:584-609`): the firmware reads the actual rail and checks
`[expected × 0.95, expected + 500]`. It never branches into different write code
by voltage — and VPP is set by the operator's pot, permanently (no board will
ever carry a DAC, v1.23 P125).

**Therefore an erasable part is a full firmware-path proxy for a UV part on the
same protocol.**

| Path | UV rows | Erasable proxies | Consequence |
|---|---|---|---|
| 0x07 | 163 | **7** — W27C512, W27E257, W27C257, SST27SF/VF 256/512 | rewrite indefinitely; operator owns W27C512 + W27E257 |
| 0x08 | 106 | **21** — MX26C/PT28C/LG28C/SST27 010–040 | rewrite indefinitely |
| 0x0B | 32 | **NONE** | only exercisable on a consumable |

UV rail spread: 0x07 = 12/13/18 kV·10⁻³; 0x08 = 12/12.5/13; 0x0B =
12/13/18/21/**25**. No erasable part on any protocol covers 18/21/25 V.

So UV bits are genuinely scarce for **0x0B (32 rows)** and the high-rail groups
only. For 0x07/0x08 the workhorse regression rig should be an **erasable** part;
UV parts become occasional confirmation.

## Agreed decisions

**D-1 — Cycle loop, not per-step inner loop.** The executor repeats
`write → verify` as a cycle instead of `write, write, verify, verify`. Operator's
call, chosen over both "keep as-is" and "drop the second verify".

**D-2 — Per-family cycle recipes.** Each cycle must present a target state that
differs from the device's current state. Four groups, keyed on facts
`derive_plan` already computes:

| Group | Rows | Cycle, ×N |
|---|---|---|
| Self-erasing on write (0x0D, 0x05 — `_AUTO_ERASE_ON_WRITE_PROTOCOLS`) | 111 | `write P → verify P`, same P. Page auto-erase means real work every cycle. |
| Erasable, not self-erasing (0x06, 0x10, 0x07/0x08-EEPROM, 0x34) | 258 | `erase → blank-check → write P → verify P`, same P. Endurance 10k+, consumption a non-issue. |
| Freely rewritable (SRAM 75 / FRAM 1) | 76 | `write P → verify P`, then `write ~P → verify ~P`. Free, and the complement proves both data-line directions. |
| UV-EPROM (monotonic) | 301 | N small equal tranches, address-spread, at the minimum non-vacuous size. |

Erasable counts verified by running `derive_plan(write_scope="full")` over all
746 rows: **342** emit an executable erase step, 404 do not (301 UV + 76
SRAM/FRAM + 27 flash4). Note flash4 is *not* "unerasable" — it auto-erases per
page, which is why it lands in the first group.

**D-3 — Blank-check moves INSIDE the erasable cycle.** A failed erase turns the
write back into a partial no-op — the same bug one level up — and blank-check is
the only thing that catches it. Strictly improves on quick task 260807-kaq's
placement (blank-check after erase, once).

**D-4 — Retire the full-device UV write.** Reverses D-C from quick task
260821-wna (2026-08-21), with the operator's explicit agreement. Rationale: it
consumes ~half the chip and, once the goal is firmware rather than cells, buys
nothing a small window can't. **But** the reason it *seemed* valuable is real and
must be preserved another way — a 256-byte slot at offset 0 only asserts A0–A7,
so it never tests the upper address lines' **write** path, and a wrong pin map on
A8+ is exactly what `dev test` exists to catch. (Reads are unaffected: the read
step reads the whole device.) See D-5.

**D-5 — Slot selection: pick the slot with the MOST remaining `1` bits.**
Tie-broken deterministically. Stays **stateless** (the chip's content is the
state — 260821-wna's design intent preserved, no cursor, no file). After a run
partially consumes slot *k*, some untouched slot has more bits, so the next run
lands elsewhere: it round-robins across the whole address space on its own,
giving high-address **write** coverage early instead of after ~200 sequential
runs. This is what replaces D-4's full-device write.

*Operator flagged the risk to check:* if slots are not uniform in practice, the
round-robin may not behave as claimed. Verify against a real used part before
relying on it.

**D-6 — Tranche size: N=2 × the existing 64-bit floor = 128 bits per run.**
~16 runs per 256-byte slot, ~4000 runs on a 64 KiB part. The reason small is
sufficient: **the verify reads and compares the whole region regardless of how
few bits the write cleared**, so address- and data-path coverage come from the
verify, not from the programming. The tranche only has to prove pulses fired.
Tranches must be disjoint subsets of the currently-`1` bits (monotonic by
construction, no impossible `0→1` request) and **interleaved** — tranche *n*
takes every *N*th still-`1` bit — so each spans the address range and all eight
bit positions rather than one corner.

**D-7 — Rail droop is measured on the erasable proxies, not on UV parts.** A
rail that sags only under load will not show at 64 bits, and the counter-argument
"use bigger tranches" would spend scarce UV bits on a *programmer* property. Do
unlimited full-device writes on an erasable part instead. The sampler already
brackets each write with VPP/VPE readings.

**D-8 — Pre-flight feasibility, never a mid-run slot change.** Choose the slot
once per run (both cycles must target the **same** slot, or the comparison stops
isolating the path) using a `popcount` that requires N tranches' worth of `1`
bits. If no slot qualifies → `SKIPPED` with a stated reason and a "this part
needs UV erasing" message. Replaces today's post-hoc `_UV_MIN_CLEARED_BITS`
check at `chip_test.py:2027`, so a vacuous cycle never runs.

**D-9 — Report the rig's remaining life.** Remaining `1` bits in the region and
an estimated run count. `write_coverage` is already the provenance home, so it is
cheap. Turns "I have a UV part somewhere" into a managed resource.

**D-10 — Reframe the repeat as a RIG-HEALTH check in all user-facing wording.**
Firmware is deterministic; a second identical cycle cannot disagree unless
something analog moved. The repeat catches rail droop, marginal timing and socket
contact — worth having, because a flaky rig manufactures false firmware verdicts,
but it is not extra firmware coverage. This also settles sizing: cycles want equal
*stress*, not equal coverage.

**D-11 — `--fast` (N=1) is the sensible habit for UV parts** when iterating on
firmware against a known-good rig: it halves consumption and loses only the
rig-health comparison. Guidance, not a default change.

**D-12 — 0x0B and the high-rail groups get a dedicated consumable.** No proxy
exists and none can. Check against the Phase 79 finding that the 25 V path
programs through **VPE**, not VPP (`firestarter vpe`) — that group may need its
own bench procedure regardless.

## Implementation notes that keep the blast radius small

- **Keep ONE `StepResult` per op** with `run_count = N` aggregating the cycles;
  make only the *execution order* cyclic. The report shape, the schema-1.7
  `run_count` disclosure, banner counts, `dedup_fingerprint` keying and
  `parse_devtest_issue` all stay untouched, and `marginal` keeps its meaning.
  Per-cycle rows would re-open every one of those.
- `write_coverage` must report the **union** across cycles, not one region.
- `--fast` becomes much more clearly the weaker mode: one cycle, no comparison
  at all. Its help text may want a sentence about that.

## Provability — read before planning

- **The firmware's native tests cannot see pulse elision** (see the note on
  native trace stubs missing register-write elision). So "a cycle actually
  programs" is **not** provable in the native suite as it stands. Either add a
  firmware-side pulse counter, or accept that this claim needs hardware.
- Host-side, everything about *plan shape*, tranche arithmetic, slot selection
  and report content is fully testable without hardware.
- **Bench session required**, with the operator's own parts: M27C512 (UV, 13 V)
  and W27C512 (EEPROM, 12 V) — do not confuse them, confirm by chip-ID. The
  W27C512 doubles as the reusable 0x07 rig for D-7.

## Next step

`/gsd-new-milestone` — v1.32 closed 2026-08-21 and `REQUIREMENTS.md` was removed
at that close, so this needs fresh requirements. Filed as a TODO rather than a
seed deliberately: `/gsd-new-milestone` globs `SEED-*.md` and skips
`{slug}.md` seeds **silently**.
