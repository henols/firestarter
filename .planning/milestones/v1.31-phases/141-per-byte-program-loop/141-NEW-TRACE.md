# Phase 141 — Post-Change Trace Dump (141-NEW-TRACE.md)

**Purpose (D-10):** `native_trace_v131`'s frozen fixture (`test/native/avr/_shared/eprom_v131_expected.h`)
is the **pre-change** side of the diff and is deliberately **not** re-frozen by this phase — Phase 144 /
TEST-06 owns the freeze and the diff. This document is the **post-change** side: the merged
strobe+timing stream the rewritten `eprom_write_execute` (plan 141-04) actually produces against the
identical synthetic fixture, captured verbatim from the built binary. `_shared/eprom_v131_expected.h`
was **not** modified, touched, or re-frozen to produce this document — confirmed by
`git status --porcelain` being empty in `/workspaces/firestarter` both before and after every command
below.

## 1. Exact build and run commands

Every `pio` invocation must run with cwd `/workspaces/firestarter` — the gitignored root
`platformio.ini` carries two `[platformio]` sections and `pio -d <dir>` does not work around it.

**Build** (the dump machinery is permanently behind `#ifdef EPROM_V131_TRACE_DUMP`; no env defines
it, so the flag is passed through the environment rather than by editing `platformio.ini`):

```bash
cd /workspaces/firestarter && PLATFORMIO_BUILD_FLAGS="-D EPROM_V131_TRACE_DUMP" pio test -e native_trace_v131 --without-testing
```

**Run** (`pio test` swallows `printf`, per the harness's own comment at
`test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:346` — the dump must be produced
by invoking the built binary directly):

```bash
cd /workspaces/firestarter && .pio/build/native_trace_v131/firestarter_native
```

**Confirm the RED's shape via the normal (no-dump) invocation** (assumption A7, the one thing
RESEARCH flagged for early verification):

```bash
cd /workspaces/firestarter && pio test -e native_trace_v131
```

Both the dump binary's own Unity summary line and the normal `pio test -e native_trace_v131`
invocation report the identical result: **6 test cases: 3 failed, 2 succeeded** (the dump build
registers one extra case, `test_dump_v131_traces`, behind the same `#ifdef`, which itself always
passes — see §3).

## 2. Per-protocol banners

```
##### EPROM_V131_TRACE_PROTO_07 total=91 strobe_overflow=0 timing_overflow=0
##### EPROM_V131_TRACE_PROTO_08 total=119 strobe_overflow=0 timing_overflow=0
##### EPROM_V131_TRACE_PROTO_0B total=59 strobe_overflow=0 timing_overflow=0
```

All three `strobe_overflow=0` and `timing_overflow=0` — the recorders never wrapped, so the shorter
post-change streams below are the genuine merged capture, not a truncated one (T-138-14's exact
concern). No banner reports a non-zero overflow; nothing was shortened to force a zero.

## 3. Confirming the RED's shape (assumption A7)

Running `pio test -e native_trace_v131` (no dump flag) produces:

```
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:383: test_smoke_setup_leaves_both_recorders_clean	[PASSED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:384: test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds	[PASSED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176: test_protocol_0x07_am27c512_capture_is_sound_and_deterministic: Expected 198 Was 91. 0x07 AM27C512 DIP28_27512	[FAILED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176: test_protocol_0x08_am27c020_capture_is_sound_and_deterministic: Expected 221 Was 119. 0x08 AM27C020 DIP32_27C020	[FAILED]
test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:176: test_protocol_0x0B_am2716_capture_is_sound_and_deterministic: Expected 201 Was 59. 0x0B AM2716 DIP24_2716	[FAILED]
6 test cases: 3 failed, 2 succeeded
```

Read against `assert_v131_protocol_case` (`test_trace_eprom_v131.cpp:288-321`) and
`v131_assert_stream_equals` (`test/native/avr/_shared/eprom_v131_expected.h:173-197`), in the order
they actually execute:

- **The suite compiled.** No build error, on either the dump build or the normal build.
- **`strobe_overflowed()`/`timing_overflowed()` both pass** for every case (asserted first inside
  `v131_assert_stream_equals`, and independently confirmed in the banners above).
- **`RESPONSE_CODE_OK` passes** for every case, confirmed two ways: (a) it is asserted at
  `test_trace_eprom_v131.cpp:297`, strictly before the length check, and Unity's failure message
  format for a numeric mismatch is `Expected <expected> Was <actual>` — the three observed messages
  (`Expected 198 Was 91`, `Expected 221 Was 119`, `Expected 201 Was 59`) are exactly the frozen
  `EPROM_V131_TRACE_PROTO_0{7,8,B}_LEN` values versus the freshly-measured `v131_merged_length()`,
  not the response-code values, so the response-code assertion did not fire; (b) if it had failed,
  Unity would have aborted before ever reaching the length check, and no case would report a
  length-mismatch message at all.
- **The sole failure is the length-equality assertion, not an element-wise divergence.** The failing
  line is `eprom_v131_expected.h:176` — `TEST_ASSERT_EQUAL_MESSAGE(expected_len, v131_merged_length(),
  ctx);` — the *first* statement inside `v131_assert_stream_equals`, evaluated before
  `v131_first_divergence()` is ever called. **Naming a "first divergent index" is not possible for
  this RED**, and this document does not invent one: Unity aborts the test case (`longjmp`) on the
  first failing assertion, which is this length check, so the element-by-element comparison loop that
  would compute and name a divergent index is never reached on any of the three protocol cases. The
  only thing correctly nameable is the length mismatch itself (198→91, 221→119, 201→59), which is
  recorded verbatim above.
- **The determinism assertion is structurally unreachable, not passing — corrected against this
  plan's own must_have wording.** `assert_v131_protocol_case`'s second half (lines 312-320: a second
  `drive_v131_write()` call, then `v131_first_divergence(snap1, n1)` against the first run's
  snapshot) sits **after** the `v131_assert_stream_equals(...)` call that fails on the length check.
  Unity's abort on that first failure means the function returns immediately; the second drive and
  the positional determinism comparison never execute, for any of the three protocol cases. This
  plan does **not** claim "the determinism leg still passes" — that leg is never reached. The only
  two cases that do pass are `test_smoke_setup_leaves_both_recorders_clean` and
  `test_smoke_timing_hook_fires_for_delay_and_delaymicroseconds` (lines 383-384), which are recorder-
  liveness smoke checks, not determinism checks on the write loop itself.
- **Independent (weaker-form) evidence the new cadence is nonetheless deterministic:** the dump
  binary was run twice as two fully independent process invocations (`.pio/build/native_trace_v131/
  firestarter_native`, once for §2/§4's capture and once again immediately after), and `diff` on the
  two full stdout captures reported **zero differences** — every banner total and every entry, for
  all three protocols, was byte-identical across the two independent runs. This is real evidence
  against a non-reproducible cadence, but it is a *cross-process* rerun, not the *intra-process*
  drive-twice-on-the-same-handle form the helper itself performs and that the plan's must_haves
  originally expected to observe passing. `eprom_write_execute` has no `static` locals, no RNG, and
  no time-dependent branching (confirmed by source read, 141-04-SUMMARY), which is consistent with —
  but not a formal proof equivalent to — the helper's own unreached check.

## 4. Cadence walk against the synthetic fixture

The fixture block is unchanged: `V131_SYNTHETIC_BLOCK[4] = {0x3C, 0xFF, 0x55, 0xAA}` with
`converge_after = {0, 0, 2, 1}` (`test_trace_eprom_v131.cpp:241,258-261`). `host_stubs.cpp`'s
`rurp_read_data_buffer()` returns `0xFF` while `read_count < converge_after`, then the seeded
`target` forever after, incrementing `read_count` on every call — the byte-level cadence below is
derived directly from that contract, not from decoding the raw strobe stream.

| Byte | Target | converge_after | Old loop (frozen, pre-141-04) | New loop (per-byte, this phase) |
|---|---|---|---|---|
| 0 | `0x3C` | 0 | 1 pulse, 1 read — pulsed on pass 1 anyway (mismatch mask starts all-`0xFF`), converges immediately | **already-matching skip**: 1 read (matches on the very first check), **0 pulses** |
| 1 | `0xFF` | 0 | 1 pulse, 1 read — the old loop had no `0xFF`-awareness, so an already-erased byte still took a wasted pulse | **`0xFF` skip**: **0 pulses, 0 reads** — the check is against the source `data_buffer[i]`, never against a chip read, so this byte is never touched at all |
| 2 | `0x55` | 2 | 3 pulses, 3 reads across 3 passes (the worst-case byte — this is why the old loop ran exactly 3 passes) | 1 already-matching check (miss) + 2 pulse→verify rounds = **2 pulses, 3 reads total** |
| 3 | `0xAA` | 1 | 2 pulses, 2 reads across 2 passes | 1 already-matching check (miss) + 1 pulse→verify round = **1 pulse, 2 reads total** |
| **Block total (`0x0B`, no final pass)** | | | old: 7 pulses, 7 reads, 3 passes over the whole block | **new: 3 pulses, 6 reads, 0 "passes" (byte-indexed, single traversal)** |

On `0x0B` (`VERIFY_PER_PULSE`, no final pass) this is the whole story. On `0x07`/`0x08`
(`VERIFY_PER_PULSE_PLUS_FINAL`) every one of the four bytes gets exactly **one more** unconditional
read after the byte loop finishes — including byte 1, which the byte loop itself never touched. That
final pass is why the fixture's own pre-existing `0xFF` byte is a pleasant accident: it is the one
byte whose *entire* second-pass read is attributable only to the final pass, making the shrinkage
(and the final pass's own unconditional nature) legible directly in the entry list in §5, not just
asserted in prose. This matches the frozen-fixture comment's own framing of byte 2 as "the worst-case
byte" and confirms the plan's own predicted shape (0-pulse/0-pulse/2-pulse/1-pulse, old loop pulsing
all four bytes on pass 1 and running three passes) exactly.

Total merged-stream entries collapsed from the frozen (pre-change) capture to the measured
(post-change) one on every protocol — the single most legible proof that LOOP-01/LOOP-02/LOOP-06
actually did what they claim:

| Protocol | Frozen (pre-change) total | Measured (post-change) total | Shrinkage |
|---|---|---|---|
| `0x07` | 198 | 91 | −107 (−54%) |
| `0x08` | 221 | 119 | −102 (−46%) |
| `0x0B` | 201 | 59 | −142 (−71%) |

`0x0B` shrinks the most because it both skips the same two bytes the other two protocols skip *and*
carries no final full-block pass to partially offset that shrinkage — consistent with the byte-level
table above.

## 5. Full per-protocol entry list (post-change, verbatim from the built binary)

Format: `{kind, 0xPP pin, 0xVV value, NUL us}` — the exact `dump_v131_merged_ready_to_paste` output,
unmodified, one block per protocol.

### `EPROM_V131_TRACE_PROTO_07` (total=91, strobe_overflow=0, timing_overflow=0)

```
{1, 0x00, 0x81, 0UL}, /* 0 */    {2, 0x08, 0x01, 0UL}, /* 1 */    {3, 0x00, 0x00, 1UL}, /* 2 */
{2, 0x08, 0x00, 0UL}, /* 3 */    {4, 0x00, 0x00, 500UL}, /* 4 */  {2, 0x04, 0x00, 0UL}, /* 5 */
{1, 0x00, 0x91, 0UL}, /* 6 */    {2, 0x08, 0x01, 0UL}, /* 7 */    {3, 0x00, 0x00, 1UL}, /* 8 */
{2, 0x08, 0x00, 0UL}, /* 9 */    {2, 0x20, 0x00, 0UL}, /* 10 */   {3, 0x00, 0x00, 3UL}, /* 11 */
{2, 0x20, 0x01, 0UL}, /* 12 */   {2, 0x04, 0x00, 0UL}, /* 13 */   {1, 0x00, 0x02, 0UL}, /* 14 */
{2, 0x01, 0x01, 0UL}, /* 15 */   {3, 0x00, 0x00, 1UL}, /* 16 */   {2, 0x01, 0x00, 0UL}, /* 17 */
{2, 0x20, 0x00, 0UL}, /* 18 */   {3, 0x00, 0x00, 3UL}, /* 19 */   {2, 0x20, 0x01, 0UL}, /* 20 */
{2, 0x04, 0x01, 0UL}, /* 21 */   {1, 0x00, 0x55, 0UL}, /* 22 */   {3, 0x00, 0x00, 3UL}, /* 23 */
{2, 0x20, 0x00, 0UL}, /* 24 */   {3, 0x00, 0x00, 100UL}, /* 25 */ {2, 0x20, 0x01, 0UL}, /* 26 */
{2, 0x04, 0x00, 0UL}, /* 27 */   {2, 0x20, 0x00, 0UL}, /* 28 */   {3, 0x00, 0x00, 3UL}, /* 29 */
{2, 0x20, 0x01, 0UL}, /* 30 */   {2, 0x04, 0x01, 0UL}, /* 31 */   {1, 0x00, 0x55, 0UL}, /* 32 */
{3, 0x00, 0x00, 3UL}, /* 33 */   {2, 0x20, 0x00, 0UL}, /* 34 */   {3, 0x00, 0x00, 100UL}, /* 35 */
{2, 0x20, 0x01, 0UL}, /* 36 */   {2, 0x04, 0x00, 0UL}, /* 37 */   {2, 0x20, 0x00, 0UL}, /* 38 */
{3, 0x00, 0x00, 3UL}, /* 39 */   {2, 0x20, 0x01, 0UL}, /* 40 */   {2, 0x04, 0x00, 0UL}, /* 41 */
{1, 0x00, 0x03, 0UL}, /* 42 */   {2, 0x01, 0x01, 0UL}, /* 43 */   {3, 0x00, 0x00, 1UL}, /* 44 */
{2, 0x01, 0x00, 0UL}, /* 45 */   {2, 0x20, 0x00, 0UL}, /* 46 */   {3, 0x00, 0x00, 3UL}, /* 47 */
{2, 0x20, 0x01, 0UL}, /* 48 */   {2, 0x04, 0x01, 0UL}, /* 49 */   {1, 0x00, 0xAA, 0UL}, /* 50 */
{3, 0x00, 0x00, 3UL}, /* 51 */   {2, 0x20, 0x00, 0UL}, /* 52 */   {3, 0x00, 0x00, 100UL}, /* 53 */
{2, 0x20, 0x01, 0UL}, /* 54 */   {2, 0x04, 0x00, 0UL}, /* 55 */   {2, 0x20, 0x00, 0UL}, /* 56 */
{3, 0x00, 0x00, 3UL}, /* 57 */   {2, 0x20, 0x01, 0UL}, /* 58 */   {2, 0x04, 0x00, 0UL}, /* 59 */
{1, 0x00, 0x00, 0UL}, /* 60 */   {2, 0x01, 0x01, 0UL}, /* 61 */   {3, 0x00, 0x00, 1UL}, /* 62 */
{2, 0x01, 0x00, 0UL}, /* 63 */   {2, 0x20, 0x00, 0UL}, /* 64 */   {3, 0x00, 0x00, 3UL}, /* 65 */
{2, 0x20, 0x01, 0UL}, /* 66 */   {2, 0x04, 0x00, 0UL}, /* 67 */   {1, 0x00, 0x01, 0UL}, /* 68 */
{2, 0x01, 0x01, 0UL}, /* 69 */   {3, 0x00, 0x00, 1UL}, /* 70 */   {2, 0x01, 0x00, 0UL}, /* 71 */
{2, 0x20, 0x00, 0UL}, /* 72 */   {3, 0x00, 0x00, 3UL}, /* 73 */   {2, 0x20, 0x01, 0UL}, /* 74 */
{2, 0x04, 0x00, 0UL}, /* 75 */   {1, 0x00, 0x02, 0UL}, /* 76 */   {2, 0x01, 0x01, 0UL}, /* 77 */
{3, 0x00, 0x00, 1UL}, /* 78 */   {2, 0x01, 0x00, 0UL}, /* 79 */   {2, 0x20, 0x00, 0UL}, /* 80 */
{3, 0x00, 0x00, 3UL}, /* 81 */   {2, 0x20, 0x01, 0UL}, /* 82 */   {2, 0x04, 0x00, 0UL}, /* 83 */
{1, 0x00, 0x03, 0UL}, /* 84 */   {2, 0x01, 0x01, 0UL}, /* 85 */   {3, 0x00, 0x00, 1UL}, /* 86 */
{2, 0x01, 0x00, 0UL}, /* 87 */   {2, 0x20, 0x00, 0UL}, /* 88 */   {3, 0x00, 0x00, 3UL}, /* 89 */
{2, 0x20, 0x01, 0UL}, /* 90 */
```

### `EPROM_V131_TRACE_PROTO_08` (total=119, strobe_overflow=0, timing_overflow=0)

```
{1, 0x00, 0x81, 0UL}, /* 0 */    {2, 0x08, 0x01, 0UL}, /* 1 */    {3, 0x00, 0x00, 1UL}, /* 2 */
{2, 0x08, 0x00, 0UL}, /* 3 */    {4, 0x00, 0x00, 500UL}, /* 4 */  {1, 0x00, 0x80, 0UL}, /* 5 */
{2, 0x08, 0x01, 0UL}, /* 6 */    {3, 0x00, 0x00, 1UL}, /* 7 */    {2, 0x08, 0x00, 0UL}, /* 8 */
{2, 0x04, 0x00, 0UL}, /* 9 */    {1, 0x00, 0xC0, 0UL}, /* 10 */   {2, 0x08, 0x01, 0UL}, /* 11 */
{3, 0x00, 0x00, 1UL}, /* 12 */   {2, 0x08, 0x00, 0UL}, /* 13 */   {2, 0x20, 0x00, 0UL}, /* 14 */
{3, 0x00, 0x00, 3UL}, /* 15 */   {2, 0x20, 0x01, 0UL}, /* 16 */   {2, 0x04, 0x00, 0UL}, /* 17 */
{1, 0x00, 0x02, 0UL}, /* 18 */   {2, 0x01, 0x01, 0UL}, /* 19 */   {3, 0x00, 0x00, 1UL}, /* 20 */
{2, 0x01, 0x00, 0UL}, /* 21 */   {2, 0x20, 0x00, 0UL}, /* 22 */   {3, 0x00, 0x00, 3UL}, /* 23 */
{2, 0x20, 0x01, 0UL}, /* 24 */   {2, 0x04, 0x01, 0UL}, /* 25 */   {1, 0x00, 0x80, 0UL}, /* 26 */
{2, 0x08, 0x01, 0UL}, /* 27 */   {3, 0x00, 0x00, 1UL}, /* 28 */   {2, 0x08, 0x00, 0UL}, /* 29 */
{1, 0x00, 0x55, 0UL}, /* 30 */   {3, 0x00, 0x00, 3UL}, /* 31 */   {2, 0x20, 0x00, 0UL}, /* 32 */
{3, 0x00, 0x00, 100UL}, /* 33 */ {2, 0x20, 0x01, 0UL}, /* 34 */   {2, 0x04, 0x00, 0UL}, /* 35 */
{1, 0x00, 0xC0, 0UL}, /* 36 */   {2, 0x08, 0x01, 0UL}, /* 37 */   {3, 0x00, 0x00, 1UL}, /* 38 */
{2, 0x08, 0x00, 0UL}, /* 39 */   {2, 0x20, 0x00, 0UL}, /* 40 */   {3, 0x00, 0x00, 3UL}, /* 41 */
{2, 0x20, 0x01, 0UL}, /* 42 */   {2, 0x04, 0x01, 0UL}, /* 43 */   {1, 0x00, 0x80, 0UL}, /* 44 */
{2, 0x08, 0x01, 0UL}, /* 45 */   {3, 0x00, 0x00, 1UL}, /* 46 */   {2, 0x08, 0x00, 0UL}, /* 47 */
{1, 0x00, 0x55, 0UL}, /* 48 */   {3, 0x00, 0x00, 3UL}, /* 49 */   {2, 0x20, 0x00, 0UL}, /* 50 */
{3, 0x00, 0x00, 100UL}, /* 51 */ {2, 0x20, 0x01, 0UL}, /* 52 */   {2, 0x04, 0x00, 0UL}, /* 53 */
{1, 0x00, 0xC0, 0UL}, /* 54 */   {2, 0x08, 0x01, 0UL}, /* 55 */   {3, 0x00, 0x00, 1UL}, /* 56 */
{2, 0x08, 0x00, 0UL}, /* 57 */   {2, 0x20, 0x00, 0UL}, /* 58 */   {3, 0x00, 0x00, 3UL}, /* 59 */
{2, 0x20, 0x01, 0UL}, /* 60 */   {2, 0x04, 0x00, 0UL}, /* 61 */   {1, 0x00, 0x03, 0UL}, /* 62 */
{2, 0x01, 0x01, 0UL}, /* 63 */   {3, 0x00, 0x00, 1UL}, /* 64 */   {2, 0x01, 0x00, 0UL}, /* 65 */
{2, 0x20, 0x00, 0UL}, /* 66 */   {3, 0x00, 0x00, 3UL}, /* 67 */   {2, 0x20, 0x01, 0UL}, /* 68 */
{2, 0x04, 0x01, 0UL}, /* 69 */   {1, 0x00, 0x80, 0UL}, /* 70 */   {2, 0x08, 0x01, 0UL}, /* 71 */
{3, 0x00, 0x00, 1UL}, /* 72 */   {2, 0x08, 0x00, 0UL}, /* 73 */   {1, 0x00, 0xAA, 0UL}, /* 74 */
{3, 0x00, 0x00, 3UL}, /* 75 */   {2, 0x20, 0x00, 0UL}, /* 76 */   {3, 0x00, 0x00, 100UL}, /* 77 */
{2, 0x20, 0x01, 0UL}, /* 78 */   {2, 0x04, 0x00, 0UL}, /* 79 */   {1, 0x00, 0xC0, 0UL}, /* 80 */
{2, 0x08, 0x01, 0UL}, /* 81 */   {3, 0x00, 0x00, 1UL}, /* 82 */   {2, 0x08, 0x00, 0UL}, /* 83 */
{2, 0x20, 0x00, 0UL}, /* 84 */   {3, 0x00, 0x00, 3UL}, /* 85 */   {2, 0x20, 0x01, 0UL}, /* 86 */
{2, 0x04, 0x00, 0UL}, /* 87 */   {1, 0x00, 0x00, 0UL}, /* 88 */   {2, 0x01, 0x01, 0UL}, /* 89 */
{3, 0x00, 0x00, 1UL}, /* 90 */   {2, 0x01, 0x00, 0UL}, /* 91 */   {2, 0x20, 0x00, 0UL}, /* 92 */
{3, 0x00, 0x00, 3UL}, /* 93 */   {2, 0x20, 0x01, 0UL}, /* 94 */   {2, 0x04, 0x00, 0UL}, /* 95 */
{1, 0x00, 0x01, 0UL}, /* 96 */   {2, 0x01, 0x01, 0UL}, /* 97 */   {3, 0x00, 0x00, 1UL}, /* 98 */
{2, 0x01, 0x00, 0UL}, /* 99 */   {2, 0x20, 0x00, 0UL}, /* 100 */  {3, 0x00, 0x00, 3UL}, /* 101 */
{2, 0x20, 0x01, 0UL}, /* 102 */  {2, 0x04, 0x00, 0UL}, /* 103 */  {1, 0x00, 0x02, 0UL}, /* 104 */
{2, 0x01, 0x01, 0UL}, /* 105 */  {3, 0x00, 0x00, 1UL}, /* 106 */  {2, 0x01, 0x00, 0UL}, /* 107 */
{2, 0x20, 0x00, 0UL}, /* 108 */  {3, 0x00, 0x00, 3UL}, /* 109 */  {2, 0x20, 0x01, 0UL}, /* 110 */
{2, 0x04, 0x00, 0UL}, /* 111 */  {1, 0x00, 0x03, 0UL}, /* 112 */  {2, 0x01, 0x01, 0UL}, /* 113 */
{3, 0x00, 0x00, 1UL}, /* 114 */  {2, 0x01, 0x00, 0UL}, /* 115 */  {2, 0x20, 0x00, 0UL}, /* 116 */
{3, 0x00, 0x00, 3UL}, /* 117 */  {2, 0x20, 0x01, 0UL}, /* 118 */
```

### `EPROM_V131_TRACE_PROTO_0B` (total=59, strobe_overflow=0, timing_overflow=0)

```
{1, 0x00, 0x80, 0UL}, /* 0 */    {2, 0x08, 0x01, 0UL}, /* 1 */    {3, 0x00, 0x00, 1UL}, /* 2 */
{2, 0x08, 0x00, 0UL}, /* 3 */    {4, 0x00, 0x00, 500UL}, /* 4 */  {2, 0x04, 0x00, 0UL}, /* 5 */
{1, 0x00, 0x20, 0UL}, /* 6 */    {2, 0x02, 0x01, 0UL}, /* 7 */    {3, 0x00, 0x00, 1UL}, /* 8 */
{2, 0x02, 0x00, 0UL}, /* 9 */    {2, 0x20, 0x00, 0UL}, /* 10 */   {3, 0x00, 0x00, 3UL}, /* 11 */
{2, 0x20, 0x01, 0UL}, /* 12 */   {2, 0x04, 0x00, 0UL}, /* 13 */   {1, 0x00, 0x02, 0UL}, /* 14 */
{2, 0x01, 0x01, 0UL}, /* 15 */   {3, 0x00, 0x00, 1UL}, /* 16 */   {2, 0x01, 0x00, 0UL}, /* 17 */
{2, 0x20, 0x00, 0UL}, /* 18 */   {3, 0x00, 0x00, 3UL}, /* 19 */   {2, 0x20, 0x01, 0UL}, /* 20 */
{2, 0x04, 0x01, 0UL}, /* 21 */   {1, 0x00, 0x55, 0UL}, /* 22 */   {3, 0x00, 0x00, 3UL}, /* 23 */
{2, 0x20, 0x00, 0UL}, /* 24 */   {3, 0x00, 0x00, 500UL}, /* 25 */ {2, 0x20, 0x01, 0UL}, /* 26 */
{2, 0x04, 0x00, 0UL}, /* 27 */   {2, 0x20, 0x00, 0UL}, /* 28 */   {3, 0x00, 0x00, 3UL}, /* 29 */
{2, 0x20, 0x01, 0UL}, /* 30 */   {2, 0x04, 0x01, 0UL}, /* 31 */   {1, 0x00, 0x55, 0UL}, /* 32 */
{3, 0x00, 0x00, 3UL}, /* 33 */   {2, 0x20, 0x00, 0UL}, /* 34 */   {3, 0x00, 0x00, 500UL}, /* 35 */
{2, 0x20, 0x01, 0UL}, /* 36 */   {2, 0x04, 0x00, 0UL}, /* 37 */   {2, 0x20, 0x00, 0UL}, /* 38 */
{3, 0x00, 0x00, 3UL}, /* 39 */   {2, 0x20, 0x01, 0UL}, /* 40 */   {2, 0x04, 0x00, 0UL}, /* 41 */
{1, 0x00, 0x03, 0UL}, /* 42 */   {2, 0x01, 0x01, 0UL}, /* 43 */   {3, 0x00, 0x00, 1UL}, /* 44 */
{2, 0x01, 0x00, 0UL}, /* 45 */   {2, 0x20, 0x00, 0UL}, /* 46 */   {3, 0x00, 0x00, 3UL}, /* 47 */
{2, 0x20, 0x01, 0UL}, /* 48 */   {2, 0x04, 0x01, 0UL}, /* 49 */   {1, 0x00, 0xAA, 0UL}, /* 50 */
{3, 0x00, 0x00, 3UL}, /* 51 */   {2, 0x20, 0x00, 0UL}, /* 52 */   {3, 0x00, 0x00, 500UL}, /* 53 */
{2, 0x20, 0x01, 0UL}, /* 54 */   {2, 0x04, 0x00, 0UL}, /* 55 */   {2, 0x20, 0x00, 0UL}, /* 56 */
{3, 0x00, 0x00, 3UL}, /* 57 */   {2, 0x20, 0x01, 0UL}, /* 58 */
```

## 6. Native env run-by-name counts (prose only — never in a baseline JSON)

These three envs run in **no CI leg** of either repository (neither `build.yml` nor
`beta-build.yml` invokes any `pio test` env beyond the two pinned ones, `native` and
`native_nodevtools`). Their pass counts below are a **run-by-name obligation** recorded here in
prose, never implied as CI-covered, and never passed to `check_size_baseline.py` or
`check_build_warnings.py` (an unrecognized env name raises an uncaught `KeyError`/exits non-zero —
F-138-05, inherited, accepted, not fixed by this phase):

- **`native_trace_v131`** (this document's own suite): **5 cases / 1 suite (5/1)** on the normal
  (no-dump) invocation — 2 smoke passes + 3 protocol failures, exactly as §3 states. (The dump
  build's own binary additionally registers a sixth, always-passing `test_dump_v131_traces` case
  behind the `#ifdef`, giving the "6 test cases: 3 failed, 2 succeeded" figure quoted in §1/§3; that
  sixth case is dump-only machinery, not part of the suite's normal 5/1 shape.)
- **`native_params_v131`** (Phase 140's table-accessor suite, unaffected by this phase): **9 cases /
  1 suite (9/1)**, all passing — `pio test -e native_params_v131` → `9 test cases: 9 succeeded`.
- **`native_loop_v131`** (this phase's own oracle, D-10, since the frozen trace fixture cannot verify
  the rewrite): **39 cases / 1 suite**, all passing — `pio test -e native_loop_v131` →
  `39 test cases: 39 succeeded` (6 harness self-checks from plan 141-03 + 14 from plan 141-07 +
  19 from plan 141-08).

## 7. What this document is not

This document does **not** re-freeze, repair, or diff against `_shared/eprom_v131_expected.h`. That
fixture's blob SHA remains pinned exactly as plan 141-04 and 141-05 left it; freezing the new golden
array from the entries in §5, and performing the formal before/after diff, is Phase 144 / TEST-06's
job. This document exists so that work has both sides of the diff available without needing to
re-derive the post-change side from scratch.
