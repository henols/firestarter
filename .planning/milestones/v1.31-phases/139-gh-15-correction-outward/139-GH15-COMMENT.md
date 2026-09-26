I filed this issue, and on a closer look, two of its numbers are wrong and one of its premises is inverted. Correcting all three here, before any of this gets implemented, so nobody builds against the version I filed instead of this one.

**`0x0B`'s pulse is 500 microseconds, not `50000 us`**

The `pulse: 50000 us` default above is the fingerprint of a bug, not a datasheet value. `interpret_timing()` used to apply a ×100 multiplier to protocols `0x07` and `0x0B`, inflating 252 chips' worth of `pulse_duration` entries. It was removed in Phase 57: [8de307f](https://github.com/henols/firestarter_app/commit/8de307f278370c07bfd3328aa9020248e66d0649) (`feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts (DEC-03)`) and [12286df](https://github.com/henols/firestarter_app/commit/12286df86abaf02be1d8e719818b7ca76a4c00e9) (`feat(57-03): regenerate chip_database.json from corrected build_db.py`). `50000 = 500 × 100` — that arithmetic is the bug, not a coincidence. The adjudication is here: [`doc/infoic-field-dictionary.md#L210-L217`](https://github.com/henols/firestarter_app/blob/4d18b645ab18a2d2465f0f623062e9249eb24132/doc/infoic-field-dictionary.md#L210-L217).

Two cross-checks, from the same table: `AT28C64B` reads `10000 us` = 10 ms, which is its datasheet byte-write time — a ×100 multiplier applied there would mean one second per byte, which nobody would ship and no one did. `DS1225` NVRAM reads `1 us`. Both numbers only make sense un-multiplied, and 500 us is the one that survives that check for `0x0B`.

And the firmware this issue asks me to change already agrees with the correction, not with the `50000 us` default: [`eprom.cpp` lines 69-77](https://github.com/henols/firestarter/blob/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L69-L77) falls back to `500` for `0x0B` today, not `50000`.

**Pulse width is data, not a per-protocol constant**

No protocol in the database that actually ships has one pulse width. Measured against the `chip_database.json` blob that ships, not a synthetic one (the full dump and the script that produced it are both linked below, so this is checkable, not asserted):

- `0x07`: n = 170, histogram `100 us ×113, 200×27, 1000×22, 500×4, 50×4`
- `0x08`: n = 127, histogram `100 us ×104, 50×11, 10×7, 200×2, 1000×2, 20×1`
- `0x0B`: n = 32, histogram `500 us ×21, 1000×6, 200×5`

`0x07` takes 5 distinct values, `0x08` takes 6, `0x0B` takes 3. Using the three constants proposed above as fixed values, **203 of 329 chips (61.7%) would be programmed at the wrong width** — 148/170 on `0x07`, 23/127 on `0x08`, 32/32 on `0x0B` (and even the corrected 500 us, used as a constant instead of a lookup, would still mis-program 11 of those 32). `0x08`'s proposed `100 us` happens to land on that protocol's own most common value, and that's worth naming directly: getting the right answer on one protocol by coincidence is not a defense of hardcoding a value on any of them, including that one.

Full distribution: [`138-02-PULSE-DISTRIBUTION.md`](https://github.com/henols/firestarter_prom/blob/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md#L237-L249). Script it came from, runnable and re-checkable against the same database: [`138-pulse-distribution.py`](https://github.com/henols/firestarter_prom/blob/b6aa1dcb23ef9931105752ed6dd6badccf6719de/.planning/phases/138-preconditions-baseline/138-pulse-distribution.py).

The string-to-microseconds parsing already lives in one place, and this correction does not touch it: [`_parse_pulse_duration`](https://github.com/henols/firestarter_app/blob/4d18b645ab18a2d2465f0f623062e9249eb24132/firestarter/database.py#L128). This is also not a novel model — minipro ships `protocol_id` and `pulse_delay` as two independent fields on the same wire message: [`t48.c` line 255](https://gitlab.com/DavidGriffith/minipro/-/blob/cae74c0607077d6260b24995f5e4c0d0b66a6a2e/src/t48.c#L255) packs `protocol_id`, [lines 266-267](https://gitlab.com/DavidGriffith/minipro/-/blob/cae74c0607077d6260b24995f5e4c0d0b66a6a2e/src/t48.c#L266-L267) pack `pulse_delay` right alongside it. minipro also exposes a per-run `-o pulse=N` override, a uint16 field, so `65535` us is minipro's own hard ceiling: [`main.c` line 698](https://gitlab.com/DavidGriffith/minipro/-/blob/cae74c0607077d6260b24995f5e4c0d0b66a6a2e/src/main.c#L698).

**The 32-bit-safe delay helper is real — it's just not for the pulse**

Using this issue's own defaults (`maximum pulses: 25`, `overpulse multiplier: 3`, `maximum overpulse: 75000 us`): `3 × 25 × 1000 us = 75 ms`. `delayMicroseconds()`'s documented accurate ceiling is `16383 us`, and on AVR its argument is a 16-bit `unsigned int` — so `delayMicroseconds(75000)` does not just lose accuracy, it cannot represent `75000` at all. It silently truncates to `75000 - 65536 = 9464 us`: a 12.5% pulse delivered with no error of any kind. That is the real argument for a safer delay path, and it is about the *overprogram* step, built entirely from numbers already in this issue — not about any single bare pulse, and it has nothing to do with `50000 us`. Once the correction above is applied, no single pulse comes anywhere near the 16-bit boundary.

The program pulse itself lives here: [`memory.cpp`, inside `memory_set_data()`, lines 249-258](https://github.com/henols/firestarter/blob/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/memory.cpp#L249-L258) — `rurp_chip_enable(); delayMicroseconds(handle->pulse_delay); rurp_chip_disable();`. Worth naming plainly, since it is a real wrinkle independent of this correction: `handle->pulse_delay` currently does double duty as both the program pulse in that function and the erase pulse in a different function inside `eprom.cpp`. The retry bound ([`NUMBER_OF_RETRIES`, `eprom.cpp` line 20](https://github.com/henols/firestarter/blob/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L20)) and the adaptive pulse-growth formula it feeds ([`eprom.cpp` line 177](https://github.com/henols/firestarter/blob/6fab4eafdcd0981d24fddc3ff177abc5c74e313c/src/proms/eprom.cpp#L177)) are what row 6 of the table below removes.

**One more thing this issue does not mention at all: program-VCC**

All four vendor algorithms this database draws from assume something close to a ~6.25 V program-VCC rail for threshold margin during programming, and this shield has no path to raise VCC on any revision — there is no way to reach it here, full stop. What the corrected design buys is timing, pulse-count and verify fidelity. It does not buy silicon-margin fidelity, and it cannot, on this hardware. That is not a caveat specific to my implementation — it is a ceiling on what *any* implementation of this issue can honestly claim on this shield, and this issue does not mention it at all. It is also exactly why boxes 3, 4 and 5 below, as originally written, imply a level of datasheet-algorithm fidelity that is not reachable here; the amendment below says so explicitly instead of leaving it implied.

**The shape of the corrected design — every number below is proposed, not datasheet-cited**

- One shared per-byte pulse-then-verify loop, driven by a `const` table keyed by `protocol_id`, with columns `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path` — no pulse-width column in that table at all.
- `handle->pulse_delay` stays on every write path exactly as it does today. The per-protocol constants this issue proposes survive only as `pulse_delay == 0` fallbacks, never as the primary source.
- `0x0B` loops pulse-then-verify with a 50 ms accumulated-energy cap per byte (`100 × 500 us`, which is the classic 2716 total programming time) and no overpulse row at all. Early-verifying bytes exit before spending the whole budget; stubborn bytes still get the full 50 ms.
- A byte that exhausts `max_pulses` hard-fails the block outright. The failure reports the address and the pulse count it took to get there, not a silent partial success.

Every number in this section is **proposed**. None of it is datasheet-cited yet — that is separate, later work, still in progress, and I am not claiming it here before it exists.

**The acceptance criteria need the same correction, not just the numbers**

Half-correcting a public spec is worse than not correcting it, because it looks complete. Here is every original box, and what happens to it:

| Original box | Disposition | Why |
|---|---|---|
| `0x07`, `0x08`, and `0x0B` use separate write handlers. | **Replaced** | Protocol owns *shape*; the database owns the *pulse*. One shared per-byte loop, driven by a `const` table keyed by `protocol_id`, replaces three handlers that would otherwise duplicate most of their own body — on a device with a hard AVR flash budget. |
| No new database algorithm flags are introduced. | **Kept** | Unchanged. |
| `EPROM_STD` uses per-byte fixed 1 ms pulse/verify cycles and a final overprogram pulse. | **Corrected** | The per-byte loop and the final overprogram pulse are this issue's central, correct insight, and both are kept. The `1 ms` is wrong: `0x07`'s most common value is `100 us`, and it spans `50` to `1000 us` across the shipped database. |
| `EPROM_QUICK` uses its own fixed short-pulse handler. | **Corrected** | "Its own handler" falls with the row above. "Fixed" falls with the pulse-width evidence above: `0x08` spans `10` to `1000 us` across 6 distinct values, and 23 of 127 chips are not `100 us`. |
| `EPROM_LEGACY` uses a long fixed programming pulse rather than the current adaptive loop. | **Corrected** | Dropping the adaptive loop is kept. "Long" is wrong — that is the `50000 us` ×100 bug above; the true value is `500 us`. |
| The current block mismatch/adaptive pulse-growth algorithm is removed from EPROM writing. | **Kept** | This issue's core diagnosis, and I still agree with it. Pulse count and overprogram duration belong to the individual byte, which a block-level mismatch mask cannot express. |
| VPP routing remains protocol-correct and is disabled on all exits. | **Kept** | Unchanged. |
| Native tests cover dispatch, pulse behavior, verification, failure, and cleanup. | **Kept** | Kept, with "dispatch" now meaning table-row selection instead of handler selection. |
| All firmware targets build successfully. | **Kept** | Unchanged. |

Two more sentences in the body, outside the checkbox list, need the same correction and would otherwise mislead a reader who never gets past the top of the issue:

- "each protocol must own its programming state machine and timing constants" — **replaced**, for the same reason as row 1: protocol owns shape, the database owns the pulse.
- "Do not retain the current generic 500 us legacy default." — this one is **reversed**. Read literally, it is backwards: 500 us *is* the legacy default, and it is correct. `50000 us` is the bug. This is the single most dangerous sentence in the issue after the `pulse: 50000 us` default itself, because it pre-emptively forbids the right answer — a reader implementing straight from the body would obey it exactly as readily as any checkbox above.

**One thing I can't answer from source, and could use help with**

Whether `0x0B` should be one-shot or looped is not something I can derive from any code I have access to — minipro never runs this algorithm itself, it just packs `pulse_delay` into a `BEGIN_TRANS` message and hands it to closed TL866/T48/T56/T76 firmware. So the 50 ms accumulated cap above is **reasoned**, not derived, and I would rather say that plainly than imply otherwise. A datasheet page or a logic-analyzer capture off real hardware would turn that reasoned guess into a checked fact — if you have either, I would like to see it. I also cannot guarantee bench coverage this milestone for `M2716`/`M2732` (`0x0B`) or `AM27C020` (`0x08`) — that is evidence I lack, not something anyone reading this owes me. A per-run `--pulse-us` override is proposed (not yet built) for exactly this case: if you have a logic analyzer and one of these parts, it would let you feed in a measured value and report back what you saw.
