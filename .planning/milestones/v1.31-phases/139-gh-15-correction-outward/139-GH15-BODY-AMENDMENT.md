⚠ **AMENDED 2026-08-09.** I filed this issue on 2026-07-12; on a closer look, two of its numbers are wrong and one of its premises is inverted, and I am correcting it myself, in place, before anyone implements it. The corrections and the evidence behind them are in the correction comment on this issue — read that first. Everything struck through below is wrong; a dated note beside each strikethrough states the corrected value. The acceptance criteria are replaced by a corrected table further down, with the original nine boxes preserved unchanged, byte for byte, in a collapsed section immediately below it.

---

## Problem

The beta firmware recognizes the three EPROM protocol IDs:

- `0x07` — `EPROM_STD`
- `0x08` — `EPROM_QUICK`
- `0x0B` — `EPROM_LEGACY`

However, all three currently use the same custom block-level programming loop in `firestarter/src/proms/eprom.cpp`:

1. Program every byte marked as mismatching.
2. Verify the full data chunk.
3. Retry up to 20 times.
4. Increase the shared pulse duration after each retry.

This is not equivalent to the actual programming algorithms represented by the protocol IDs. In particular, it does not track pulse count per byte, does not implement the standard intelligent-programming overpulse, and treats legacy programming as a short adaptive pulse sequence.

The protocol ID already determines the programming algorithm, so no additional database flags or algorithm selector should be introduced.

## Required design

Dispatch `CMD_WRITE` to separate handlers from `configure_eprom()`:

```text
0x07 -> eprom_regular_write_execute()
0x08 -> eprom_quick_write_execute()
0x0B -> eprom_legacy_write_execute()
```

~~The handlers may share low-level electrical primitives, but each protocol must own its programming state machine and timing constants.~~ **[AMENDED 2026-08-09]:** replaced — protocol owns *shape*, the database owns the *pulse*. One shared per-byte pulse-then-verify loop, driven by a `const` table keyed by `protocol_id` (columns `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path` — no pulse-width column at all), replaces three separate handlers that would otherwise duplicate most of their own body on a device with a hard AVR flash budget.

## Algorithm requirements

### `0x07` — EPROM_STD / regular intelligent programming

Implement programming per byte:

1. Apply one fixed 1 ms programming pulse.
2. Verify that byte.
3. Repeat fixed 1 ms pulses until the byte verifies or the maximum pulse count is reached.
4. Record the number of pulses required for that byte.
5. Apply the final overprogram pulse, nominally `3 × accumulated programming time`.
6. Perform a final verification.

Suggested defaults:

- pulse: `1000 us`
- maximum pulses: `25`
- overpulse multiplier: `3`
- maximum overpulse: `75000 us`

### `0x08` — EPROM_QUICK

Implement a separate quick-programming handler:

1. Apply one fixed 100 us pulse.
2. Verify the byte after every pulse.
3. Repeat until success or the quick-algorithm maximum is reached.
4. Apply the protocol-appropriate finishing/overprogram pulse.
5. Perform a final verification.

Keep this implementation isolated from the regular handler so manufacturer-specific quick/PRESTO behavior or margin verification can be added later without affecting `EPROM_STD`.

Initial suggested defaults:

- pulse: `100 us`
- maximum pulses: `25`
- finishing overpulse multiplier: `3`

Document that true PRESTO margin verification is not yet implemented if the RURP hardware/firmware cannot expose the required verify mode.

### `0x0B` — EPROM_LEGACY

Implement a separate long-pulse legacy handler:

1. Set address and data.
2. Apply a fixed long programming pulse.
3. Verify the byte.
4. Fail after the allowed fixed-pulse attempts.

Initial fallback values:

- ~~pulse: `50000 us`~~ **[AMENDED 2026-08-09]:** wrong — `50000 = 500 × 100` is the fingerprint of a ×100 multiplier `interpret_timing()` used to apply to protocols `0x07` and `0x0B`, inflating 252 chips' worth of `pulse_duration` entries, removed in Phase 57 (commits `8de307f`, `12286df`). The correct value is `500 us`; the shipped database's own modal `0x0B` value agrees, and so does this firmware's own fallback (`eprom.cpp:69-77`) before any of this issue's changes land.
- maximum attempts: `1`
- no intelligent-programming overpulse

~~Do not retain the current generic 500 us legacy default.~~ **[AMENDED 2026-08-09]:** reversed — read literally, this instruction is backwards. `500 us` *is* the legacy default, and it is correct; `50000 us` is the bug (see above). This was the single most dangerous sentence in the issue after the `pulse: 50000 us` default itself, because it pre-emptively forbade the right answer. The corrected design loops pulse-then-verify for `0x0B` with a 50 ms accumulated-energy cap per byte (`100 × 500 us`, the classic 2716 total programming time) instead of one long fixed pulse, and carries no overpulse row for this protocol.

## Shared implementation helpers

Introduce shared helpers for electrical operations only, for example:

- `eprom_enable_vpp()`
- `eprom_disable_vpp()`
- `eprom_program_pulse(handle, address, data, pulse_us)`
- `eprom_verify_byte(handle, address, expected)`
- `eprom_report_program_failure(...)`

The pulse helper must safely support long durations. Do not rely on a single `delayMicroseconds(50000)` call; split millisecond and microsecond portions or otherwise use a safe 32-bit delay implementation.

**[NOTE 2026-08-09]:** this helper is still required — not because of a single bare `50000 us` pulse (that number is wrong; see above), but because the *overprogram* pulse (`3 × 25 × 1000 us = 75 ms`, built entirely from this issue's own `0x07` defaults) exceeds `delayMicroseconds()`'s documented `16383 us` accurate-delay ceiling. On AVR, whose `delayMicroseconds()` takes a 16-bit `unsigned int`, `delayMicroseconds(75000)` does not just lose accuracy — it silently truncates to `9464 us` (`75000 - 65536`), a 12.5% pulse delivered with no error of any kind. Once the `0x0B` correction above is applied, no single *pulse* comes anywhere near this boundary; the overprogram step is the only place this helper's safety margin still matters. See the correction comment for the full argument.

## VPP handling

Preserve the existing protocol-specific VPP routing:

- `0x07` and `0x08`: regulator plus VPE-to-VPP dropping path
- `0x0B`: direct legacy VPE/VPP path

Extract the routing and cleanup into shared helpers so `eprom_check_vpp()` and all write/error paths use the same masks.

All exits, including verification failures, must disable every active high-voltage route.

## Remove the current custom algorithm

Remove or stop using:

- `program_mismatched_bytes()`
- `verify_and_update_mask()`
- the block-level `NUMBER_OF_RETRIES` loop
- adaptive growth of `handle->pulse_delay`

EPROM intelligent programming must operate byte-by-byte because pulse count and final overprogram duration belong to the individual byte.

## Compatibility

- Do not add a new algorithm field to the chip database.
- Do not add a second firmware algorithm selector.
- Continue using the existing protocol IDs as the single source of truth.
- Existing erase, blank-check, chip-ID, bus remapping, and VPP validation behavior should remain intact unless changes are required for safe shared cleanup.

## Tests

Add native/unit tests covering at least:

- protocol `0x07` dispatches to the regular handler
- protocol `0x08` dispatches to the quick handler
- protocol `0x0B` dispatches to the legacy handler
- regular programming verifies after each fixed 1 ms pulse
- regular overpulse duration is based on the successful byte's pulse count
- regular programming fails after the configured maximum
- quick programming uses fixed 100 us pulses and verifies per pulse
- legacy programming uses the long fixed pulse
- already-matching bytes and `0xFF` bytes are skipped safely
- VPP is disabled on success and every failure path
- final verification failure produces an error response

Build and test all supported firmware targets:

- `uno`
- `uno328pb`
- `leonardo`
- native test suite

## Acceptance criteria

*(Amended 2026-08-09.)* Pulse width is data, not a per-protocol constant: measured against the `chip_database.json` blob that ships, `0x07` (n = 170) spans five distinct widths from 50 to 1000 us (modal 100 us); `0x08` (n = 127) spans six distinct widths from 10 to 1000 us (modal 100 us); `0x0B` (n = 32) spans three widths from 200 to 1000 us (modal 500 us). Using this issue's original three per-protocol constants (`1000 us`, `100 us`, `50000 us`) as fixed values instead of a database lookup would mis-program 203 of 329 chips (61.7%) — full histograms and the runnable script that produced them are in the correction comment. The table below maps a disposition onto every one of this issue's original nine boxes; the boxes themselves are preserved unedited, byte for byte, in the collapsed section immediately after it.

| Original box (verbatim) | Disposition | Reason |
|---|---|---|
| `0x07`, `0x08`, and `0x0B` use separate write handlers. | Replaced | Protocol owns *shape*; the database owns the *pulse*. One shared per-byte pulse-then-verify loop, driven by a `const` table keyed by `protocol_id`, with columns `max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path` (no pulse-width column at all), replaces three handlers that would otherwise duplicate most of their own body on a device with a hard AVR flash budget. |
| No new database algorithm flags are introduced. | Kept | Unchanged. |
| `EPROM_STD` uses per-byte fixed 1 ms pulse/verify cycles and a final overprogram pulse. | Corrected | The per-byte loop and the final overprogram pulse are this issue's central, correct insight, and both are kept. The `1 ms` is wrong: `0x07`'s most common value is `100 us`, and it spans `50` to `1000 us` across the shipped database. |
| `EPROM_QUICK` uses its own fixed short-pulse handler. | Corrected | "Its own handler" falls with row 1. "Fixed" falls with the pulse-width evidence: `0x08` spans `10` to `1000 us` across 6 distinct values, and 23 of 127 chips are not `100 us`. |
| `EPROM_LEGACY` uses a long fixed programming pulse rather than the current adaptive loop. | Corrected | Dropping the adaptive loop is kept. "Long" is wrong — that is the `50000 us` x100 bug above; the true value is `500 us`, and the corrected design loops pulse-then-verify with a 50 ms accumulated-energy cap per byte instead of one long pulse. |
| The current block mismatch/adaptive pulse-growth algorithm is removed from EPROM writing. | Kept | This issue's core diagnosis, kept as originally stated. Pulse count and overprogram duration belong to the individual byte, which a block-level mismatch mask cannot express. |
| VPP routing remains protocol-correct and is disabled on all exits. | Kept | Unchanged. |
| Native tests cover dispatch, pulse behavior, verification, failure, and cleanup. | Kept | Kept, with "dispatch" now meaning table-row selection instead of handler selection. |
| All firmware targets build successfully. | Kept | Unchanged. |

<details>
<summary>Original acceptance criteria, as filed 2026-07-12 (preserved verbatim)</summary>

- [ ] `0x07`, `0x08`, and `0x0B` use separate write handlers.
- [ ] No new database algorithm flags are introduced.
- [ ] `EPROM_STD` uses per-byte fixed 1 ms pulse/verify cycles and a final overprogram pulse.
- [ ] `EPROM_QUICK` uses its own fixed short-pulse handler.
- [ ] `EPROM_LEGACY` uses a long fixed programming pulse rather than the current adaptive loop.
- [ ] The current block mismatch/adaptive pulse-growth algorithm is removed from EPROM writing.
- [ ] VPP routing remains protocol-correct and is disabled on all exits.
- [ ] Native tests cover dispatch, pulse behavior, verification, failure, and cleanup.
- [ ] All firmware targets build successfully.

</details>

## Evidence ceiling — the ~6.25 V program-VCC gap

*(New section, added 2026-08-09.)* All four vendor algorithms this database draws from assume something close to a ~6.25 V program-VCC rail for threshold margin during programming, and this shield has no path to raise VCC on any revision — there is no way to reach it here, full stop. The corrected design above buys timing, pulse-count and verify fidelity. It does not buy silicon-margin fidelity, and it cannot, on this hardware — that is a ceiling on what *any* implementation of this issue can honestly claim here, not a limitation specific to this implementation. It is exactly why boxes 3, 4 and 5 above, as originally written, imply a level of datasheet-algorithm fidelity that is not reachable on this shield; the corrected table above says so explicitly instead of leaving it implied. See the correction comment for the full argument.
