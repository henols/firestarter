---
title: 27C programming-algorithm fidelity via a per-protocol parameter table
trigger_condition: a firmware-correctness/reliability milestone is prioritized, OR a 27C part programs unreliably and RCA points at pulse behavior, OR gh#15 is scheduled
planted_date: 2026-07-02
updated: 2026-08-08
status: promoted
promoted_to: v1.31 27C Programming-Algorithm Fidelity (gh#15), activated 2026-08-08
issue: https://github.com/henols/firestarter_prom/issues/15
---

> **PROMOTED 2026-08-08 → milestone v1.31.** This seed is the scoping source for the milestone,
> retiring ROADMAP Backlog **999.22** (which was queued as the `v1.27` slot). Its corrections C1/C2/C3
> and the `0x0B` energy-budget resolution were adopted as milestone decisions D-01/D-02; the open
> question below is settled as *design*, not left for the bench. Kept here unmodified as the record of
> what was known at activation.

# 27C programming-algorithm fidelity via a per-protocol parameter table

Make the 27Cxxx write algorithm datasheet-conformant by driving the *shared*
program→verify loop from a small `const` parameter table keyed by `protocol_id`,
instead of hardcoded `switch` defaults + a flat retry cap. The "regular / fast /
legacy" split described in the datasheets collapses to **rows in a table**, not
separate implementations.

> **2026-08-08 update.** gh#15 now specifies this work. Its architecture is sound
> but it carries **two wrong numbers and one inverted premise** — see
> "Corrections" below before implementing it as written. A `/gsd-explore` pass on
> 2026-08-08 also **falsified two claims in the original seed** (marked ~~struck~~).

## Corrections that must land before implementation (2026-08-08)

### C1 — The 50 ms legacy pulse is a fixed bug's artifact. Do not implement it.

Both this seed (original line: "legacy NMOS parts get a 500µs adaptive pulse, not
the fixed **50ms** single pulse those parts specify") and gh#15 (`pulse: 50000 us`)
assert a 50 ms `0x0B` pulse. **The true value is 500 µs.**

`firestarter_app/doc/infoic-field-dictionary.md:210-217` already adjudicated this:

| Chip | proto | raw | correct µs | pre-Phase-57 build_db.py output |
|---|---|---|---|---|
| AM2716 | `0x0B` | `0x1F4` | **500 µs** | **50000 µs (×100 wrong)** |
| AM27C64 | `0x07` | `0x64` | 100 µs | 10000 µs (×100 wrong) |

> **BUG-2:** raw `pulse_delay` is µs for ALL protocols; `interpret_timing()`
> applied `val * 100` for `0x07`/`0x0B`; 252 chips affected; fix deferred to Phase 57.

Phase 57 removed the multiplier (`tools/build_db.py:414` is now plain hex→decimal)
and the shipped DB reads `500 us` for AM2716. `50000 = 500 × 100` — the seed was
planted 2026-07-02 against the inflated database, and gh#15 inherited the figure.

Two independent cross-checks confirm units are µs with no multiplier:
`AT28C64B` → 10000 µs = 10 ms, exactly its datasheet byte-write; `DS1225` NVRAM
→ 1 µs, correct for an SRAM-speed write. A ×100 would make the 28C64 1 s/byte.

### C2 — Pulse width is DATA, not a per-protocol constant. (Inverts gh#15.)

gh#15 hardcodes `1000 / 100 / 50000 µs` into three handlers. minipro does the
opposite, and the DB disagrees with the constants:

| algorithm | shipped DB distribution | gh#15 constant |
|---|---|---|
| `0x07` STD | **100 µs ×113**, 200 ×27, 1000 ×22, 500 ×4, 50 ×4 | 1000 µs |
| `0x08` QUICK | **100 µs ×104**, 50 ×11, 10 ×7, 200 ×2, 1000 ×2, 20 ×1 | 100 µs |
| `0x0B` LEGACY | **500 µs ×21**, 1000 ×6, 200 ×5 | 50000 µs |

minipro ships `protocol_id` and `pulse_delay` as **two orthogonal wire fields**
into one closed state machine — `minipro/src/t48.c:250-267` (identical in
`tl866a.c:257`, `tl866iiplus.c:238`, `t56.c:193`, `t76.c:529`):

```c
msg[1] = device->protocol_id;
format_int(&(msg[12]), device->pulse_delay, 2, MP_LITTLE_ENDIAN);
```

`main.c:698` prints `"Default write pulse: %u us / Available write pulse[us]: 1-65535"`
and `-o pulse=N` overrides it per run — minipro treats the pulse as a per-chip
**tunable datum**. It is a uint16 on the wire (2-byte `format_int`; both override
paths reject `> 0xffff`), so 65535 µs is the hard ceiling.

**This adjudicates the seed-vs-gh#15 structural conflict in the seed's favour.**
Protocol owns *shape* (max_pulses, overprogram rule, vpp_path); the DB owns the
*pulse*. That is a parameter table, not three state machines. Keep
`handle->pulse_delay` on the write path; protocol constants remain fallbacks for
`pulse_delay == 0` only (`eprom.cpp:70-77`).

### C3 — The safe-long-delay helper is still needed, for a different reason.

gh#15 asks for a 32-bit-safe delay because of the 50 ms legacy pulse. With C1
applied, no *pulse* approaches `delayMicroseconds()`'s 16383 µs ceiling — but the
**overprogram pulse does**: `3 × 25 × 1000 µs = 75 ms`. Keep the helper; document
it as an overpulse concern.

## Enabler found 2026-08-08 — per-byte verify is affordable

gh#15's per-byte pulse→verify loop looks expensive because
`eprom_write_execute` pays a `delay(10)` VPE settle (`eprom.cpp:114`). Paid per
byte that would be 512 × 10 ms = **5.1 s of pure settling per block**.

It does not have to be. `rurp_chip_enable`/`rurp_chip_output` are **dedicated
pins** (`rurp_shield.h:109-129`), and `mem_util_calculate_top_address_register`
preserves the HV bits across *every* `set_address`, read path included
(`memory.cpp:163-166`):

```c
rurp_register_t mask = CTRL_VPP_A9_ENABLE | CTRL_VPE_ENABLE
                     | CTRL_VPP_P1_ENABLE | CTRL_VPP_REGULATOR_ENABLE;
```

**VPE survives a read**, so the settle stays amortized once per block. This
matches the datasheets, which verify with VPP still applied (CE high, OE low).

Caveat: for `pins < 32` the mask also preserves `CTRL_VPP_VPE_DROP_ENABLE`; on
DIP32 that bit *is* A16, so the drop path cannot be held across arbitrary
addresses there (DIP32 uses `CTRL_VPP_P1_ENABLE` instead).

## Resulting throughput (512-byte Uno block)

| | pulse | max pulses | overpulse | typical | worst case |
|---|---|---|---|---|---|
| `0x07` | `handle->pulse_delay` | 25 | `3 × N × pulse`, cap 75 ms | ~0.25 s @100 µs; ~2.05 s @1000 µs | ~51 s |
| `0x08` | `handle->pulse_delay` | 25 | `3 × N × pulse` | ~0.2 s | ~13 s |
| `0x0B` | `handle->pulse_delay` | see open question | none | ~0.8 s | ~25.6 s |

**Faster than today** in the typical case — the current code can make 20 full
block passes.

**Risk gh#15 does not mention:** worst-case blocks exceed
`DEFAULT_RESPONSE_TIMEOUT = 10` s (`firestarter_app/firestarter/serial_comm.py:66`).
Only reachable on failing silicon, but it converts "chip is marginal" into
"serial timeout", destroying the diagnostic. Precedent for the fix: the
blank-check progress/chunk pattern at `memory.cpp:379-384`.

## Open question — is `0x0B` one-shot or looped? (bench-only)

**Not answerable from source.** minipro never runs the algorithm: `pulse_delay`
is packed into a `BEGIN_TRANS` message and handed to closed TL866/T48/T56/T76
firmware. There is no pulse/verify loop anywhere in minipro's host code.

Reconciliation worth testing: `100 × 500 µs = 50 ms`, exactly the classic 2716
total programming time. **Cap accumulated program time per byte at 50 ms** rather
than fixing a pulse count, and both readings are satisfied — early-verifying
bytes exit fast, stubborn ones still receive the datasheet's full energy budget.

## The gap (datasheet vs. firmware today)

All three 27C `protocol_id`s (0x07/0x08/0x0B) already share ONE routine
`eprom_write_execute`; they differ only by a hardcoded pulse default and a
VPP-path branch. The divergences from datasheet-correct behavior:

1. **Escalating pulse width, not fixed pulse.** Firmware grows the pulse each
   retry (`pulse_delay = org + org*retries/20`, `eprom.cpp:177`). Quick-Pulse /
   Flashrite / PRESTO hold a **fixed** pulse and *count* pulses. Backwards.
2. **Flat retry cap of 20** for all parts (`NUMBER_OF_RETRIES`, `eprom.cpp:20`).
   Datasheets want **10** (Microchip) or **25** (Intel/AMD), failing hard at cap.
3. **No over-program / margin pulse.** Correct for PRESTO & Quick-Pulse; wrong
   for older Intel "Intelligent" 27C parts that apply **3× the pulses used**.
4. **Block-level, not per-byte.** Pulse count and over-program duration belong to
   the *individual byte*; the current mismatch-mask loop cannot express that.
   (This is gh#15's central and correct insight.)
5. ~~**Legacy NMOS parts** get a 500µs adaptive pulse, not the fixed **50ms**
   single pulse those parts specify.~~ **FALSIFIED 2026-08-08 — see C1.** 500 µs
   is the correct value; 50 ms was the ×100 BUG-2 artifact.
6. **VCC never raised to 6.25V.** All four vendor algorithms assume ~6.25V
   program-VCC for threshold margin. The shield has **no VCC-raise path** →
   *hardware-bound*, NOT closable in firmware (see ceiling below). **gh#15 omits
   this entirely** — its acceptance criteria imply a fidelity that cannot be
   reached on this hardware.

## Shape (rough)

- **Firmware:** replace the hardcoded pulse `switch` (`eprom.cpp:70-77`) + flat
  `NUMBER_OF_RETRIES` with a `const` table keyed by `protocol_id` carrying:
  `max_pulses`, `overprogram_factor` (0 | 3×), `overprogram_cap_us`, `verify_mode`,
  `vpp_path` (drop-resistor vs direct). **Pulse width is NOT a table column — it
  comes from `handle->pulse_delay` (C2).** Restructure the loop to per-byte
  pulse→verify with VPE held for the block, and apply the over-program pulse when
  `overprogram_factor > 0`.
- ~~Keep the `program_mismatched_bytes` / `verify_and_update_mask` loop verbatim.~~
  **SUPERSEDED 2026-08-08:** gh#15 is right that the block mismatch-mask loop must
  go — per-byte pulse counting cannot be expressed through it. The *primitives*
  (`handle->firestarter_set_data` / `_get_data`) stay verbatim; the block loop
  does not.
- **Reuse split:**

  | Varies per protocol (~15–20%) | Shared (~80–85%) |
  |---|---|
  | max_pulses, overprogram_rule, vpp_path, vpp_mv | program→verify loop, bus I/O primitives, address/control routing |

## Hardware ceiling (state plainly)

Firmware fidelity buys *timing / pulse-count / verify* correctness but **not**
full silicon-margin fidelity, because 6.25V program-VCC is unreachable on the
current shield. This is best-effort — the same shape as prior D-07 hardware-bound
graduations. Don't let the VCC gap block the (real, achievable) timing fixes.
gh#15's acceptance criteria should be amended to acknowledge it.

## Cost / risk

- Program-timing change → any golden traces / bench-verified write results that
  encode the current pulse cadence will legitimately shift; re-baseline needed.
- Behavior-preserving-*ish* but not byte-identical: this changes *how* bytes get
  programmed. Needs on-bench re-verification per family (Leonardo + on-hand 27C
  parts), not just native tests.
- Over-program (3×) path is only correct for specific Intel-Intelligent parts —
  don't apply it blanket. Gated by the research question below.
- Worst-case block time can exceed the host's 10 s response timeout (see above).

## Next steps when triggered

1. Post C1/C2/C3 to gh#15 before anyone implements it as written — in particular
   the 50000 µs figure, which is a fixed bug's fingerprint.
2. Resolve the research question (`questions.md`): confirm exact max-pulse counts
   per part and which on-hand parts (if any) actually need the 3× over-program.
3. Bench-settle the `0x0B` one-shot-vs-looped question on a real 2716/2732.
4. Draft the parameter table with datasheet-verified rows — **shape columns only,
   no pulse column**.
5. Rework the loop to per-byte fixed-pulse-and-count with VPE held per block;
   wire the table in; drop the escalation and the mismatch-mask block loop.
6. Address the 10 s timeout ceiling for worst-case blocks.
7. Re-baseline golden traces; on-bench re-verify each affected family on Leonardo.
8. Document the 6.25V-VCC ceiling as accepted hardware debt.

## Related

- Issue: [henols/firestarter_prom#15](https://github.com/henols/firestarter_prom/issues/15)
- Research: `research/questions.md` — "27C programming-algorithm fidelity"
- ~~Prior art: v1.16 primitives (P7/P4/P3/P5) — the loop/primitive layer this rides on~~
  **FALSIFIED 2026-08-08:** `src/proms/primitives.{h,cpp}` **do not exist** in the
  firmware tree — the P89 recompose was never merged. This work has no primitives
  layer beneath it; it rides directly on the `handle->firestarter_*` function
  pointers (`memory.cpp:88-95`).
- Decode authority: `firestarter_app/doc/infoic-field-dictionary.md:196-217`
  (`pulse_delay` — CONFIRMED µs, no multiplier; BUG-2 record)
- Code: `eprom_write_execute` + program loop (`firestarter/src/proms/eprom.cpp:70-77,110-193`),
  `NUMBER_OF_RETRIES` (`firestarter/src/proms/eprom.cpp:20`),
  pulse escalation (`firestarter/src/proms/eprom.cpp:177`),
  HV-bit preservation (`firestarter/src/proms/memory.cpp:163-166`),
  handle primitives (`firestarter/src/proms/memory.cpp:88-95`)
- Datasheets: ST M27C512 PRESTO IIB (farnell 1581208), AMD Am27C010 Flashrite,
  Intel 27C010 Quick-Pulse, Microchip 27C256 DS11001N
