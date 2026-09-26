# Quick Task 260821-wna: dev test full-size write with UV bit-masked slot selection - Context

**Gathered:** 2026-08-21
**Status:** Ready for planning

<domain>
## Task Boundary

`firestarter dev test` currently writes only 256 bytes to every chip, in every
mode. Make it write the full device where that is physically possible, and on
UV-erasable EPROMs write into whatever cells are still writable — selecting the
next usable slot when the current one is saturated — so UV parts stay testable
without a UV eraser.

Host-only (`firestarter_app/`). No firmware change: full-device write and
arbitrary-region write already exist in the firmware protocol.

</domain>

<measured_baseline>
## Measured starting state (verify these before changing them)

Measured this session by calling `derive_plan` against the live database:

| chip | `write_scope="full"` | `write_scope="partial"` |
|---|---|---|
| M27C512 (UV-EPROM, 65536 B) | `write` @ (65280, 256) | `write-partial` @ (65280, 256) |
| AT28C256 (EEPROM, 32768 B) | `write` @ (0, 256) | `write-partial` @ (32512, 256) |
| W27C512 (EEPROM, 65536 B) | `write` @ (0, 256) | `write-partial` @ (65280, 256) |

Two facts follow, both load-bearing for this task:

1. **No scope ever writes more than 256 bytes.** `write_scope="full"` means
   "the full *step list*" (write + verify + erase), never "the full device".
   `_WRITE_REGION_LENGTH` and `_UV_WRITE_REGION_LENGTH` are both `256`
   (`chip_test.py` ~line 1550-1563).
2. **The UV consent prompt in `_resolve_write_scope` is inert.** It asks
   "Write the WHOLE device now? Yes writes the entire chip" — but for a UV part
   `full` and `partial` both resolve to `_top_anchored_or_default(full)`, the
   same 256-byte top-anchored window. Only the op label differs
   (`write` vs `write-partial`). Fixing this prompt to mean what it says is in
   scope; deleting the prompt is not.

</measured_baseline>

<decisions>
## Implementation Decisions

These were decided by the operator this session. They are LOCKED — do not
re-open, re-derive, or "improve" them during planning.

### D-A: UV bit-masking is the core mechanism

On a UV EPROM, programming only clears bits (1 -> 0). Writing value `P` into a
cell currently holding `C` yields `C & P`. Therefore a partially-used slot is
**not** unusable — it still holds whatever `1` bits remain.

The write pattern must be masked by what is actually on the chip:

- read the slot's current content `C`
- take the existing address-derived pattern `D` (`PATT-01`, unchanged)
- write `P = C & D`
- verify read-back `== P`

Requiring an all-`0xFF` slot is explicitly REJECTED: on a used chip such slots
mostly do not exist, which is exactly why UV parts are currently one-shot.

### D-B: Slot selection, and the vacuous-pass guard

Slot granularity stays a fixed 256 B window (a module constant, see D-E).

A slot is only usable if the masked write will actually **clear** a meaningful
number of bits. Bits cleared by the write = `popcount(C & ~D)`.

- If that count is below a threshold, the slot is saturated under this
  pattern — advance to the next slot.
- A slot already at `0x00` yields `P = 0` and verify passes trivially. This is
  a VACUOUS PASS and is the same failure family as the absent-chip false-green
  trap. It MUST be structurally impossible to report as a pass, not merely
  unlikely.

Slot selection is **stateless** — the chip's own content is the state. Do NOT
persist a slot cursor in `~/.firestarter`, the config dir, or anywhere else.
Probe candidate slots by reading them.

Because `D` is address-derived, it differs per slot, so slots saturate one at a
time and the cursor advances naturally. A 64 KiB UV part therefore yields on
the order of 256 write tests instead of one.

### D-C: Virgin (fully blank) UV EPROM gets a full-device write

A UV part reading all-`0xFF` gets a full-device masked write (`P = 0xFF & D`
= `D`, i.e. the plain address-derived pattern over the whole device).

This does not consume the part: `D` leaves roughly half of all bits still `1`,
so the chip remains testable slot-by-slot afterwards under D-A/D-B.

The `_resolve_write_scope` prompt must become truthful about which of these two
outcomes the operator is consenting to.

### D-D: Non-UV chips — full size, with a cap

- The **primary write/verify pass** covers the full device.
- The **SDP legs** (`write-baseline-b`, `write-baseline-a`, `sdp-lock`,
  `write-inhibited`, `sdp-unlock`, `write-restored`) stay on a small region.
  They prove the lock mechanism works; they are not coverage. Note
  `AT28C256`'s plan currently carries 8 region-sized write ops — putting all 8
  at full device size would mean 8 x 32 KiB per run at 250000 baud.
- Parts where full write -> verify is **structurally impossible** must be
  excluded with a stated, visible reason rather than reported as a FAIL. The
  known case is `W29C040`'s permanently locked 16 KiB boot block. Find the
  general rule if one exists in the DB; if it does not, a named-part exclusion
  carrying the reason is acceptable — a silent pass is not.
- `_ALWAYS_WRITES_PASS_COUNT = 6` is derived from a live `derive_plan` result
  by `tests/test_dev_test_cmd.py`. If the pass count changes, change the
  CONSTANT, never the test.

### D-E: SC4 / D-01 are being deliberately narrowed — say so

`_UV_WRITE_REGION_LENGTH` is currently a module constant *specifically* so a
malicious or misconfigured DB entry cannot widen the write window; `is_uv_eprom`
carries the note "a guess here is a chip-destroying bug, not a coverage gap".

This task makes the write width depend on `memory-size` for the full-device
cases, which **reverses that threat model** for those paths. That reversal must
be:

- explicit in the code comments at the point where the width is now DB-derived,
  naming SC4 and D-01 and why the narrowing is acceptable here;
- bounded — the *slot* width (D-B) stays a module constant. Only the
  full-device paths take their width from `memory-size`, and only after
  `memory-size` is sanity-checked.

Do not quietly delete the SC4 comments. Amend them.

### D-F: Warning presentation

A short warning is presented when the write was not the full device — i.e. when
a UV part got a slot-sized masked write instead. It names what was written and
why (which slot, how many bits were clearable).

Constraint: `dev_test`'s console output is triple-gated — two exact-equality
gates scrape the `dev_test` function body, plus one syrupy `--help` snapshot.
Any console string change must update those gates in the same commit. Quick
task 260821-spg deliberately trimmed this console output; do not re-add prose
that task removed. Keep the warning to a single short line.

### Claude's Discretion

- The exact bit-clearing threshold in D-B, and whether it is per-byte or
  per-slot. Pick one, justify it in a comment, and make it a named constant.
- Whether the masked-write region and bit counts are added to the JSON report /
  `diagnostic_report.py`. Recommended yes — reports must stay comparable across
  runs, and "which slot did this run use" is provenance. Do not break the
  existing report schema's consumers.
- Where the masking logic lives. `derive_plan` is a pure, DB-only function with
  no chip access, so the mask cannot be computed there — `Step.write_region`
  is decided by `derive_plan` and downstream code "may only READ" it. Resolve
  this cleanly: the *region* may still be decided by `derive_plan`, but the
  *mask* is necessarily execution-time. Do not smuggle chip reads into
  `derive_plan`.

</decisions>

<specifics>
## Specific Ideas

- The address-derived pattern generator (`addr ^ (addr >> 8) ^ (addr >> 16) ^
  (addr >> 24)) & 0xFF`, `chip_test.py` ~line 74) is unchanged. Masking wraps
  it; it does not replace it.
- `classify_fingerprint`'s `_FF_RATIO_THRESHOLD = 0.98` blank/contact detector
  keys on read-back being near-all-`0xFF`. Check that masked expectations do
  not make a genuine blank/contact fault classify as something else.

</specifics>

<canonical_refs>
## Canonical References

- `firestarter_app/firestarter/chip_test.py` — `derive_plan`, `Plan`, `Step`,
  `is_uv_eprom`, `_top_anchored_or_default`, `_write_region_for`,
  `classify_fingerprint`, region constants.
- `firestarter_app/firestarter/cli_handlers.py` — `_resolve_write_scope`
  (~2427), `_ALWAYS_WRITES_PASS_COUNT`, `dev_test`.
- `firestarter_app/tests/test_dev_test_cmd.py` — derives the write-pass count
  from a live `derive_plan`; the console-output gates.

</canonical_refs>
