---
title: Firmware size-reduction survey — measured evidence base for v1.33
date: 2026-08-22
context: /gsd-explore session 2026-08-22. Baseline measured at firmware 6d4d6bc and
        re-confirmed byte-identical at 8695ee5 after PR #55 merged upstream mid-session.
        Work implemented on firmware branch `size-reduction-survey`.
status: ROUTED — this is the evidence base for milestone v1.33 (Source Hygiene &
        Firmware Size Reduction), Phases 155-158. Read before planning any of them.
        The binary-protocol finding (§6) was ruled OUT of v1.33 by the operator and
        is filed as Backlog 999.35 / queued milestone v1.28.
routed_to:
  - .planning/ROADMAP.md '## v1.33 — Source Hygiene & Firmware Size Reduction'
  - .planning/REQUIREMENTS.md (SWEEP / DEAD / DEDUP / DECODE / LAND)
  - .planning/ROADMAP.md '### Phase 999.35' (binary protocol, backlog)
  - .planning/notes/firmware-size-reduction-measured.patch (applyable)
---

# Firmware size-reduction survey

Goal (operator's framing): **hunt byte size without making the code harder to
follow or unreadable.**

## Measurement baseline

All figures below are from the leonardo + uno builds of the firmware tree at
`6d4d6bc`, measured as `.text + .data` for flash and `.data + .bss` for RAM.

```
leonardo   flash=28170   ram=2016  (of 2560)
uno        flash=26026   ram=1575  (of 2048)
native test suite: 172 test cases, 172 succeeded
```

Leonardo Caterina cliff is 28672 B → **502 B of headroom on this branch**.
(This branch carries the +540 B debug-session growth over `size_baseline.json`'s
recorded 27630, which still needs a MERGE-05 adjudication.)

## Structural facts discovered (these shape everything else)

1. **LTO is ON.** PlatformIO's AVR builder enables `-flto`; every `.o` in
   `.pio/build/` has empty `.text` and 35 `.gnu.lto_*` sections. Consequence:
   per-object size attribution is impossible, `main` is 5358 B because it has
   swallowed `loop()` + `init_programmer_framed` + `parse_json` + `json_parse`
   + `json_parse_config` + the dispatch switch + all 9 `eprom_*` wrappers, and
   "extract a helper" does **not** automatically save bytes — gcc may re-inline
   it. Always measure, never estimate.

2. **Every logging severity macro is a pure alias.** `include/logging_id.h:105-119`
   — `LOG_ERROR_ID_BYTES`, `LOG_WARN_ID_BYTES` and `LOG_ID_BYTES` are the same
   macro. Severity is encoded **entirely in the message ID**. So every
   `if (force) { LOG_WARN(a); code=WARN; } else { LOG_ERROR(b); code=ERR; }`
   fork collapses to one call with a selected id:
   ```c
   bool force = is_flag_set(FLAG_FORCE);
   LOG_ID_BYTES(force ? MSG_WARN_X : MSG_ERR_X, _b, n);
   handle->response_code = force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR;
   ```
   This is the enabler that makes the duplicated-block extractions below cheap.
   ⚠ RISK: golden traces that match on message id alone **cannot see** this
   fork, so a consolidation could swap `response_code` invisibly. Needs a
   deliberate mismatch test, not just green goldens.

## Findings, ranked

### 1. Narrow `protocol` + `ctrl_flags` — MEASURED −348 B flash, −5 B RAM

`include/firestarter.h:211,223`. Two lines:
```c
uint32_t protocol;    →  uint8_t  protocol;    /* max value in use: 0x39 */
uint32_t ctrl_flags;  →  uint16_t ctrl_flags;  /* max flag: FLAG_SKIP_SDP_UNLOCK 0x100 */
```
`protocol` is compared 19×, `is_flag_set` fires 45× — all were 4-byte compares.

```
leonardo  28170 → 27822   (−348 B flash, −5 B RAM)
uno       26026 → 25678   (−348 B flash, −5 B RAM)
pio test -e native: 172/172 succeeded
```

⚠ **BUT it silently breaches the fail-closed invariant, and no test catches it.**
`src/json_parser.c:503` is `extract_long("algorithm", handle->protocol)` with no
range check. Today `algorithm: 261` reaches `configure_memory`'s generic
fail-closed guard and is refused. With `uint8_t` it truncates to `5` and
dispatches into `configure_flash_5v_page`. All 172 tests passed anyway.
Fix (~15 B), required if this lands:
```c
unsigned long v = simple_strtoul(json + tokens[pos + 1].start);
/* protocol is uint8_t; anything above 0xFF is not a known protocol, so map it
 * to 0 and let configure_memory's fail-closed tail refuse it rather than
 * silently truncating 0x105 into PROTO_FLASH_5V_PAGE. */
handle->protocol = (v > 0xFF) ? 0 : (uint8_t)v;
```

### 2. 64-bit math for one voltage read — 438 B of linked library

`src/boards/rurp_common.cpp:66-70` uses `uint64_t`, and is the **only user-code
caller** of the entire 64-bit runtime:
```
 158 __muldi3   162 __udivmod64   54 __lshrdi3
  22 __udivdi3_umoddi3   18 __adddi3   18 __muldi3_6
   4 __umoddi3    2 __udivdi3            = 438 B TOTAL
```
Restructure to stay in 32 bits: pre-scale the divider ratio, e.g.
`ratio_x256 = ((r1 + r2) << 8) / r2`, then multiply and shift back. Precision
loss lands under the 10-bit ADC's own noise, BUT it feeds the 95%/105% VPP
validation windows — needs a real comparison run, not a hand-wave.
Est. ~−400 B. One function, one file, no protocol change.

### 3. VPP report block copy-pasted 4× — MEASURED −268 B, 172/172 pass

**DONE AND MEASURED.** Extracted to `mem_util_report_voltage()` in `memory.cpp`
(declared in `memory_utils.h`, which both callers already include). Arithmetic
preserved byte-for-byte so it is pure de-duplication, not a behaviour change.

```
uno       26026 → 25758   (−268 B)
leonardo  28170 → 27902   (−268 B)
__udivmodhi4 call sites:  30 → 13   (the 24 duplicated sites became 6)
eprom_check_vpp:          524 → 280 B
flash_intel_write_init:   562 → 348 B
mem_util_report_voltage:        190 B   (new)
    −244 −214 +190 = −268  ✓ matches the image delta exactly
pio test -e native: 172/172 succeeded
```

Original analysis follows.

```
src/proms/eprom.cpp:718      and  :738    (both inside eprom_check_vpp)
src/proms/flash_intel.cpp:41 and  :64     (both inside flash_intel_write_init)
```
Each copy computes 4 scaled display values with `/1000`, `/100`, `%10`, then
hand-packs 8 bytes into `_b[]`.

| function | size | `__udivmodhi4` calls inside |
|---|---|---|
| `eprom_check_vpp` | 524 B | **12** |
| `flash_intel_write_init` | 562 B | **12** |

24 of the 30 `__udivmodhi4` call sites in the whole image live in these two
functions. Both are mostly this one block, twice. Est. ~−350 to −450 B.

Note: the firmware is pre-formatting **decimal display digits** to ship over the
wire (4 × uint16 BE). The host could do that division for free — shipping raw mV
would drop the divisions entirely, but that is a wire change (messages.toml +
host parity).

### 4. Chip-ID mismatch block copy-pasted 4× — MEASURED −158 B, 172/172 pass

**DONE AND MEASURED.** Extracted to `mem_util_report_chip_id(handle, actual,
warn_only)` in `memory.cpp`. The `if (chip_id != handle->chip_id)` test moved
into the helper as an early return, so each of the 4 call sites is now one line.

```
uno       25758 → 25600   (−158 B)
leonardo  27902 → 27744   (−158 B)
pio test -e native: 172/172 succeeded
```

Sites: `flash_utils.cpp:107`, `flash_intel.cpp:163`, `eeprom_28c.cpp:292`,
`eprom.cpp:735`. `flash_utils.cpp` needed a `memory_utils.h` include added; the
other three already had it.

The copies **had already drifted**: three tested `is_flag_set(FLAG_FORCE)`
inline while `eprom.cpp` took an `error_code` parameter. Callers now pass the
decision as `warn_only`, so the semantic is stated once. `eeprom_28c.cpp`'s copy
also carried redundant `(uint16_t)` casts the others did not.

### 5. json_parser.c — a half-finished refactor, ~900–1000 B

`key_parsers[]` (`src/json_parser.c:164-271`) matches the wire key, then calls a
`get_*` stub — **and each stub re-matches the same key** via `extract_num`'s
hidden `jsoneq(json, &tokens[pos], element)` (`:285-290`).

- **1012 B measured** in 11 `get_*` stubs (86–110 B each, for one `strtoul` +
  one store).
- ~112 B of duplicated PROGMEM key strings — 10 of 11 keys are in flash twice
  (`flags` appears once).
- A redundant `jsoneq_` call per field on every command.

Why these 11 are fat while 5 identical siblings (`get_r1/r2/rev/rw_pin/vpp_pin`)
cost **zero bytes**: the 5 are called directly with a literal key so gcc inlines
them away; the 11 are reached through a **PROGMEM function pointer**, so each
keeps a full 4-argument ABI prologue, its own `PSTR` copy, and a real
`call jsoneq_`. That opacity is the entire 1012 B.

Constraint found: **`get_flags` is dual-use** — in the table AND called directly
at `:161` and `:192` by the config parser. It must keep a key-matching form.
Split is: 10 table-only (free to delete) / 1 dual-use / 5 direct-only (leave alone).

Two shapes were written out in the session:
- **Option A** — split `extract_num` into a key-matching form (direct callers,
  unchanged) and a `store_num` form (table callers). Est. −260 to −360 B, full
  type safety, ~15-line diff.
- **Option B** — pure data table `{key, offsetof, sizeof(member), clamp}` plus
  one `store_field()` using `memcpy` of the low `width` bytes. ~−900 to −950 B,
  measured floor since the 1012 B is deleted outright. Trades compile-time field
  type-checking for `offsetof`/`memcpy`. Arguably MORE readable: the table
  becomes the single source of truth for key → field → clamp.
- A is a strict subset of B; doing A first costs nothing toward B later.

### 6. Drop JSON for a binary command frame — MEASURED −3.7 KB flash, −512 B RAM

Built a realistic replacement: packed 57-byte frame, 18 real field assignments +
`memcpy` for `address_lines`, length checks, config path, `configure_memory`
still invoked. Let LTO drop what became unreachable.

| | leonardo | uno |
|---|---|---|
| baseline | 28170 flash / 2016 RAM | 26026 / 1575 |
| binary frame | 24442 / 1504 | 22334 / 1063 |
| **delta** | **−3728 / −512** | **−3692 / −512** |

~13% of the image, 25% of RAM in use. Leonardo Caterina headroom 502 B → 4230 B.

The number is **conservative**, verified two ways:
- Symbol diff checked for accidental GC. The USB/serial functions that appeared
  to vanish were only clone-suffix renumbering (`.constprop.76` → `.61`).
- **`dt_decode_register` (370 B) survived and is still fully paid for** in the
  after-build, so the dev-tools string decode is included in the 24442. A real
  binary protocol would shrink that too.

**THE RAM FINDING IS THE HEADLINE:** `parse_json::tokens` is **512 B of `.bss`**
— second-largest RAM object in the firmware, behind only `handle` (1115 B).
`static jsmntok_t tokens[64]`, and on AVR `jsmntok_t` is 8 B (enum + 3 × 16-bit
int). On uno that is **32.5% of all RAM in use**, permanently resident.

```
  1115  b  handle
   512  b  parse_json(firestarter_handle*)::tokens
    80  b  Serial
```

Wire size also drops (57 B vs a ~250–400 B JSON write command), but that is a
minor bonus — data chunks dominate throughput.

**Costs, honestly:**
1. **Loss of graceful degradation — the serious one.** `json_parser.c:332`
   silently skips unknown fields. That is load-bearing: it is how a newer host
   talks to older firmware, and `README.md` documents the legacy `type` key being
   safely ignored because of it. A packed struct has no such property. The
   mitigation is already proven in this codebase in the *response* direction —
   `MSG_OK_READY` is a `[length]`-discriminated blob that absorbed
   CAP-01 → CAP-02 → CAP-03 with zero catalog edits. A command frame needs the
   same `[version][length]` prefix **designed in from day one**; it cannot be
   retrofitted.
2. Cross-repo break: `serial_comm.py`, `eprom_operations.py`, `constants.py` and
   every host test building a command dict. These must move in lockstep.
3. Bench debuggability: JSON commands are readable in a serial monitor; this
   project lives on the bench. Binary frames need a decode tool first.
4. Test churn: every native suite constructing a JSON command string, plus the
   trace goldens.
5. Two copies of jsmn: `firestarter/lib/jsmn` and `firestarter_py32_ci/lib/jsmn`.

### 7. The operator's original example: the `!` inversion is FREE

`src/eprom_operations.cpp` — all 9 `eprom_*` wrappers return
`!op_execute_*_operation(...)`. Flipped the convention for real (inverted the 6
return paths inside `op_execute_stateful_operation`, dropped all 9 `!`) and
rebuilt:

```
BASELINE   leonardo flash=28170 ram=2016   uno flash=26026 ram=1575
FLIPPED    leonardo flash=28170 ram=2016   uno flash=26026 ram=1575
```

**Byte-for-byte identical on both targets.** All 9 wrappers inline into `main`
and the switch collapses to a *single* shared call to
`op_execute_stateful_operation.constprop.44`; the `!` folds into the branch
polarity on `finished`. Flipping just moves the inversion from 9 call sites to 6
return sites.

→ Purely a **readability** decision, zero size cost either way. Worth doing on
its own merits: the two opposite boolean conventions currently need a 10-line
comment to defend the load-bearing `!` (`eprom_operations.cpp:57-63`).

## THE APPLYABLE RESULT — measured **−2938 B flash, −13 B RAM**, all three targets

Findings 1 + 2 + 3 + 4 + 5 + 8 composed. Saved as an applyable patch at
`.planning/notes/firmware-size-reduction-measured.patch` — `git apply` from the
`firestarter/` sub-repo root. 11 files, **+229 / −231 = net −2 lines**.

```
target       baseline      now    Δflash  |   baseline   now   ΔRAM
uno             26026    23088     −2938  |      1575   1562    −13
uno328pb        26074    23136     −2938  |      1581   1568    −13
leonardo        28170    25232     −2938  |      2016   2003    −13

leonardo Caterina headroom: 502 B  ->  3440 B   (6.9x)
pio test -e native             172/172, five separate runs
pio test -e native_nodevtools  172/172, two runs
```

**The firmware is now heap-free** — no `malloc`, `free`, or `__brkval` symbol
remains in the image (see finding 8).

All three baselines are MEASURED. (uno328pb's was initially derived as
25598+476 = 26074 from `size_baseline.json` plus the branch's recorded growth;
a later direct build confirmed 26074/1581 exactly, so the derivation is retired
in favour of the measurement.)

⚠ **THE TREE MOVED UNDER ME MID-SESSION — checked, and the numbers survive.**
PR #55 (`debug-w27c512-write-slow`) was merged upstream while this session was
running, a bot commit `8695ee5 "Apply automatic changes"` bumped
`include/version.h` from `3.0.0b21` to `3.0.0b22`, and **the local checkout was
left on `beta`** with these uncommitted changes sitting on it — against the
standing rule never to work on `beta`/`main`. Actions taken:
- The work was moved onto a topic branch, `size-reduction-survey`, with all 11
  modified files preserved (`git checkout -b` carries a dirty tree).
- The baseline was **re-measured at the new HEAD** (`8695ee5`) and is
  byte-identical to the one taken at `6d4d6bc`: uno 26026/1575,
  uno328pb 26074/1581, leonardo 28170/2016. The only tree change was the version
  string, and `"3.0.0b21"` and `"3.0.0b22"` are both 8 characters, so
  `FW_VERSION` occupies identical flash. Every delta in this file therefore
  stands unchanged.
- This is also the likely explanation for an anomaly earlier in the session: a
  `lib/jsmn/src/jsmn.h` revert that verified clean was later found modified again
  with nothing in between having touched it. An external checkout/merge acting on
  the repo mid-session accounts for it. Treat build measurements in a repo under
  external automation as needing a HEAD check, not just a `git status` check.

### Step-by-step, each measured against the step before it

| # | change | uno | leonardo |
|---|---|---|---|
| 2 | 64-bit voltage math → 32-bit | **−714** | −714 |
| 5 | json_parser function-pointer table → data table | **−976** | −968 |
| 1 | `store_field` saturation + `protocol`/`ctrl_flags` narrowing | −172 | −180 |
| 3+4 | VPP report ×4 and chip-ID report ×4 extracted | −426 | −426 |
| 8 | `mem_util_blank_check` 4-byte `malloc` → file-scope static | **−650** | −650 |
| | **total** | **−2938** | **−2938** |

### 8. `mem_util_blank_check` mallocs 4 bytes — MEASURED −650 B flash, −8 B RAM

The single biggest surprise of the session. `mem_util_blank_check` called
`malloc(sizeof(blank_check_progress_data_t))` where that struct is **one
`uint32_t`**. Four bytes on the heap — and it was the **only** caller of the
allocator anywhere in the image, so it pulled in `malloc` (312 B) + `free`
(274 B) = **586 B**, plus the call sites and `__brkval` state.

It also **dereferenced the result unchecked** — `progress_data->address =
handle->address` immediately after the malloc — on a part with roughly 470 B of
free RAM once `handle` (1115 B) and the jsmn token array (512 B) are accounted
for. So this was a latent NULL-deref, not only dead weight.

Replaced with a file-scope `static uint32_t`: identical lifetime (one command
runs at a time), no heap. `handle->progress_data` (the `void*` field) was removed
with it — nothing else ever read it. **The image is now heap-free.**

⚠ **This one touches tests, unlike every other change here.** Two suites asserted
`h.progress_data == NULL` as a second observable of "the pre-write blank check
did not run":
- `test_eeprom28c_sdp.cpp:1862` (Case 30 / ERASE-01)
- `test_val_5v_page.cpp:351` (ERASE-02)

Both already assert `is_operation_in_progress(&h) == false` for the same fact,
and their own comments name that as the primary. Since
`mem_util_blank_check` sets that flag on the *same statement* that used to do the
malloc, dropping the `progress_data` probe loses a redundant probe of a deleted
implementation detail, not behavioural coverage. Both assertions and their
comments were updated (a third stale comment at `test_val_5v_page.cpp:240` still
claimed the malloc and was corrected too). If a reviewer prefers zero test churn,
the alternative is to keep the now-dead `void* progress_data` field for 2 B of
RAM — but then those test comments assert a malloc that no longer happens.

**Composition is NOT additive, and the ordering matters.** Measured in isolation
these were −714, −976, −348 and −426 = −2464, but composed they give −2288. The
176 B gap is real: the json table refactor deleted the 11 `get_*` stubs whose
assignments to `uint32_t` fields were a large share of what the narrowing was
buying, so the narrowing's own contribution fell from −348 to −172 once the
table landed. Do not quote the isolated figures additively.

### Landing cost — both gate questions now answered

- **MERGE-05 policy: passes, no exemption needed.** `check_size_baseline.py:697`
  is `if flash_delta > allowance` and `:709` is `if ram_delta > ram_tolerance` —
  one-sided, growth-only. A shrink is `< allowance` and passes cleanly. This
  answers the open question from the start of the session: a size *reduction*
  needs no named exemption, unlike the four growth exemptions already stacked up.
- **Default byte-identity mode: will go RED and needs `size_baseline.json`
  re-recorded** with cold figures for all three AVR targets plus the native
  blocks. That is the normal procedure this file's own history documents.
- ⚠ **The canonical MERGE-05 invocation is ALREADY RED on this branch, for an
  unrelated pre-existing reason.**
  `check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild`
  exits 1 with `native: cases baseline=141 observed=172` — BASE-01 was frozen at
  Phase 124's 141 cases while the live tree has 172. It fails on case counts
  before ever reporting flash. Confirmed not caused by these changes: the diff
  touches zero files under `test/`.
- **`check_size_baseline.py` is invoked by NO CI workflow** (`grep` over
  `.github/` returns nothing) — it is a local-run obligation, so none of the
  above is caught by automation.

## Negative results — measured, do not retry

- **`configure_memory` if-chain → `switch`** (on top of the `uint8_t protocol`
  narrowing): **+18 B WORSE** than narrowing alone (uno 25696 vs 25678). gcc will
  not build a jump table because the protocol values are sparsely spread over
  0x05–0x39 (a table would span 53 entries), so it emits comparisons either way
  and the `switch` arrangement is slightly bulkier. **Keep the if-chain.**

- **`flash_5v_page` page-boundary `%` → `&` mask**: **+22 B flash**, RAM
  unchanged. Not a size win — `%` was two compact `call __udivmodsi4` sites,
  while the mask is inline 32-bit AND-ing. This is a **size-for-speed trade**,
  not a size reduction. See the speed finding below; it may still be worth 22 B.

- **Narrowing `jsmntok_t` 8 → 6 B** — ⚠ **CORRECTED, RESULT IS INCONCLUSIVE.**
  Measured −128 B RAM for +30 B flash. Was initially recorded here as "broke the
  native suite" (158 cases ran, 1 failed, 2 suites ERRORED). That conclusion is
  **retracted**: the native suite was later observed to be **load-flaky** — a
  run under load reported 171/172 on a tree that then passed 172/172 three times
  in a row. The jsmn run took 1:44 against a normal 0:34, and ERRORED suites are
  consistent with a timeout rather than an assertion failure. **Needs a clean
  re-run on an idle machine before being accepted or rejected.** If it does hold,
  it is −128 B RAM for +30 B flash with no protocol change. NOTE: `start`/`end`
  MUST stay signed — `jsmn.c` uses `-1` sentinels in 12 places.

## Speed findings (not size)

- **`flash_5v_page_write_execute` does TWO software 32-bit modulos PER BYTE.**
  `address % page_size` and `(address + 1) % page_size`, where
  `flash_5v_page_page_size()` returns **64, 128 or 256 — always a power of two**.
  Confirmed in the disassembly: 2 × `__udivmodsi4` inside the per-byte loop.
  Fix is `& (page_size - 1)`, costs +22 B flash (measured above).
  ⚠ This is on the **algorithm-5 flash-page path** (W29C040-class), NOT the 27C
  EPROM path this branch was debugging — do not conflate it with
  w27c512-write-slow-3x. Runtime win needs a bench measurement; the per-byte
  page-write wait may dominate. Not yet measured on hardware.

- **`mem_util_split_delay` is already correct** — it guards the division behind
  a `us <= 16383` fast path, and the modal pulse widths (100/500 µs) never reach
  the divide. No finding; noted so nobody "fixes" it.

- **The native test suite is load-flaky.** Observed 172/172 (×4 runs at ~35 s),
  171/172 once (at 1:13), and 158-cases-with-2-ERRORED once (at 1:44). Run
  duration correlates with failure. Never trust N=1 on this suite — and beware
  attributing a flake to whatever change is in the tree at the time (this
  session did exactly that once; see the jsmn correction above).

## Implementation notes for the landed changes

**Finding 2 — the 32-bit voltage reformulation** (`src/boards/rurp_common.cpp`).
Folds the divider into one scale factor BEFORE dividing, instead of forming a
64-bit numerator:
```
k   = 1100 * (R1 + R2) / R2                 <- 7850 exactly at 270k/44k
Vin = (adc * k + bandgap/2) / bandgap
```
Verified numerically before writing any code: **bit-identical** to the uint64
form at the shipped calibration (adc=1023, bandgap=225 → 35691 mV both ways),
and worst deviation **5 mV** across a sweep of R2 39k–47k × bandgap 200–250 ×
the full ADC range — against the ±5% VPP windows (±600 mV at 12 V) that consume
it. Guards keep both products inside uint32 (`R1+R2 <= 3900000`, `k <= 4000000`)
and return 0 on an implausible calibration, exactly as `r2 == 0` already did.
Result: all 438 B of 64-bit runtime GONE (verified: zero `__muldi3` /
`__udivmod64` / `__lshrdi3` / `__udivdi3` symbols remain), and
`rurp_read_voltage_mv` itself 434 → 232 B.
⚠ **No native coverage** — `src/boards/` is outside `[env:native]`'s
`src_filter = +<proms/>`, so this arithmetic is bench-verified only.

**Finding 5 — the field table** (`src/json_parser.c`). Went with Option B. Key
implementation facts:
- All 11 target fields sit at offsets **3–37**, safely below `data_buffer` at 38,
  so a `uint8_t` offset works. Guarded with a `_Static_assert` on `page_size`'s
  offset rather than assumed, because a struct reorder would silently write into
  the wrong member.
- `width` comes from `sizeof(((firestarter_handle_t*)0)->member)` so it can never
  drift from the field.
- `READ_TIMING_MAX_US` had to be **hoisted** above the table — it was defined
  further down the file, next to the now-deleted `get_read_settling`.
- `get_flags` is deliberately NOT in the table: `json_parse_config` calls it
  directly at two sites where it must still match its own key. It inlines there,
  so its remaining cost is 90 B of `constprop` clone.
- Verified after: `get_*` stubs 1012 B → **90 B**; every wire key now appears
  **once** in flash instead of twice.
- **The refactor made the safety fix cheaper and more general.** The per-stub
  range guard drafted earlier became one `if (width < sizeof(v))` saturation in
  `store_field`, covering `pins`, `chip_id`, `vpp_mv` and `page_size` too — not
  just `protocol`. Saturating an out-of-range `algorithm` sends it to the
  member's max, which is not a known protocol, so it still fail-closes.

**Findings 3+4 — the report helpers** live in `src/proms/memory.cpp`, declared in
`include/memory_utils.h`. `flash_utils.cpp` needed a `memory_utils.h` include
added; the other three callers already had it.

## Closed leads — measured, nothing there

- **`NUMBER_JSNM_TOKENS` cannot be reduced. 64 is well-chosen.** Computed the
  true maximum by walking `firestarter_app/firestarter/data/pinouts.json` for the
  largest `address-bus-pins` (**19**) and `static-high-pins` (**1**), then
  counting jsmn tokens (every object, array, key and value is one token) for a
  maximal command with every optional wire key present: **57 tokens**. That
  leaves **7 tokens = 56 B** of headroom in the 512 B array. So the array can only
  shrink via a narrower `jsmntok_t` (the inconclusive −128 B) or by dropping JSON
  entirely (−512 B). Useful by-product: that maximal command serialises to
  **314 bytes**, which firms up the earlier "~250–400 B" estimate and makes the
  binary-frame wire comparison 314 → 57 bytes, a 5.5x reduction.

- **The five write paths do not share a skeleton.** `flash_5v_page_write_execute`
  is page-buffered with boundary detection; `flash_nor_unlock_write_execute` is
  per-byte-with-verify. Genuinely different shapes — forcing a common helper would
  cost readability for little size. `eprom_write_execute` (1570 B, still the
  largest handler) was rewritten for speed in the w27c512-write-slow-3x debug
  session (pass-batched program loop) and is heavily documented; it is deliberately
  left alone. Lead closed.

## Still unmeasured (next up)

- The five write paths: `eprom_write_execute` 1572, `eeprom28c_write_execute` 700,
  `flash_5v_page_write_execute` 468, `flash_nor_unlock_write_execute` 350,
  `flash_intel_write_execute` 204 = **3294 B**. Inspected the two flash ones —
  they are genuinely different shapes (page-buffered vs per-byte-verify), so no
  cheap shared skeleton there. `eprom_write_execute` (1572 B, the single largest
  handler) is still unread.
- `NUMBER_JSNM_TOKENS` (64) actual maximum. A write command with a 20-entry bus
  array needs ~51+ tokens, so headroom is thin — needs the host's largest real
  command to size safely. Up to −256 B RAM if it can drop.
- `mem_util_remap_address_bus` 392 B, `op_get_message` 394 B,
  `_execute_operation` 366 B, `mem_util_blank_check` 510 B.
- `main` is still 5358 B — the biggest single object in the image.

## Running total

- **−2938 B flash / −13 B RAM: measured, tested (7 suite runs), patch saved.**
  Findings 1 + 2 + 3 + 4 + 5 + 8. Net −2 lines of source. Leonardo Caterina
  headroom 502 B → 3440 B. Firmware is heap-free.
- **−3.7 KB flash and −512 B RAM** *instead of* part of the above, if JSON is
  replaced by a binary frame (finding 6) — measured, but a cross-repo protocol
  milestone, and it must carry a `[version][length]` prefix from day one. NOTE:
  this partly OVERLAPS the −2938 already taken (the json_parser table refactor
  would be superseded), so the two are not additive. Re-measure from the new
  position before quoting a combined figure.
- Remaining candidates are small or closed — see the two sections above.

## Session hygiene

- The `firestarter/` tree was returned to a clean baseline after every
  exploratory measurement in this session, and the composed result was verified
  to reproduce the exact baseline figures (uno 26026/1575, leonardo 28170/2016)
  on revert each time.
- The working changes for the −2938 B result are LEFT APPLIED in
  `firestarter/` (uncommitted) and also captured in the patch file. Nothing was
  committed. Nothing was pushed.
- ⚠ Landing this needs `size_baseline.json` re-recorded from **cold** builds
  (`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` per env), per
  that file's own documented convention.
