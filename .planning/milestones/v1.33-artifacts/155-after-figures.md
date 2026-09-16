---
title: After-figures record -- milestone v1.33, Phase 155 (Dead-Weight Removal)
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "06"
measured: 2026-08-23
status: AUTHORITATIVE -- the phase record. Every figure below was re-measured this session
  against the committed `.planning/milestones/v1.33-artifacts/155-before-figures.md` (the only valid denominator
  for this phase's saving), never against `scripts/baseline/size_baseline.json`, which is
  +478/+476/+540 B stale by its own admission (see section 12).
requirements: [DEAD-01, DEAD-02, DEAD-03, DEAD-04, DEAD-05, DEAD-06]
---

# After-figures record -- v1.33 Phase 155

This is the landing record: the after position measured against
`155-before-figures.md`, both directions of the symbol-gate proof, all eight phase-gate
legs, and the five public corrections this phase owes the ROADMAP and REQUIREMENTS. Every
number below is labelled WARM and carries the verbatim command that produced it, re-measured
this session rather than transcribed from an earlier plan's SUMMARY.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_PRE_SHA` | `2ad5b322a37ba4a88afd09cc946f5c4114e51483` (155-01's before-figures anchor) |
| `FW_POST_SHA` | `adf1a31` (`adf1a31...`, HEAD of `gsd/v1.33-source-hygiene-firmware-size-reduction`, this plan's own commit landed) |
| `firestarter` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` |
| Commit count `FW_PRE_SHA..FW_POST_SHA` | **5** -- `076abc2` (155-02), `e26e9ab` (155-04 RED), `46dd574` (155-04 GREEN), `98e70af` (155-05), `adf1a31` (155-06) |
| `git -C firestarter status --porcelain` | empty (asserted before and after this plan's work) |
| `git -C firestarter worktree list` | one entry (`firestarter` itself) plus one pre-existing, unrelated worktree (`firestarter_py32_ci`, present before this session started, untouched by this plan) -- the throwaway worktree this plan created for the planted-negative proof (section 3 below) was fully removed and pruned before this record was written |

**Nothing is pushed.** Pushing `gsd/v1.33-source-hygiene-firmware-size-reduction` to any
remote is the operator's call, not this plan's -- per house convention, a milestone branch
is never pushed by an executor.

Commands run:
```bash
git -C firestarter rev-parse HEAD
git -C firestarter status --porcelain
git -C firestarter rev-list --count 2ad5b322a37ba4a88afd09cc946f5c4114e51483..adf1a31
git -C firestarter worktree list
```

---

## 2. The measured result -- all three targets, before vs after, WARM

| Target | Flash before | Flash after | Δ flash | RAM before | RAM after | Δ RAM |
|---|---|---|---|---|---|---|
| `uno` | 26026 | **24660** | **-1366** | 1575 | **1567** | **-8** |
| `uno328pb` | 26074 | **24708** | **-1366** | 1581 | **1573** | **-8** |
| `leonardo` | 28170 | **26804** | **-1366** | 2016 | **2008** | **-8** |

Command per target: `pio run -e uno`, `pio run -e uno328pb`, `pio run -e leonardo`, run this
session against a warm `.pio/build/`, on a tree asserted clean before and after. All six
after-figures matched the values plans 04 and 05 had already measured, reproduced
independently this session rather than transcribed. **These figures are deliberately WARM,
not cold** -- LAND-01 / Phase 158 owns the cold re-record; re-recording cold here would
duplicate that plan's job.

**The per-target delta is -1366 B flash and -8 B RAM, computed as before-minus-after on the
same tree against `155-before-figures.md` §2 -- never against the stale baseline file (see
section 12).**

---

## 3. OQ-1, stated not buried -- the shipped guard constant and its 2 B delta

The shipped guard constant is `k > 4194303UL` -- `4194303` is `0x3FFFFF`, so the comparison
compiles to a shift/mask test, is the **tighter** of the two candidate bounds, and is **2 B
cheaper** than `4000000UL`, the decimal alternative the preserved reference (`a6b46f8`)
shipped. Consequently the measured saving is **-1366 B**, which is **2 B more** than the
ROADMAP's `**Measured: -1364 B**` header states.

**The 2 B delta and its cause:** the guard constant. `k <= 4194303` is REQUIREMENTS DEAD-04's
own locked figure, quoted literally in its criterion text (`Both uint32 overflow guards
(R1+R2 <= 3900000, k <= 4194303)`); the ROADMAP's `-1364 B` header, by contrast, is
consistent only with the `4000000UL` guard the preserved reference shipped. **The ROADMAP's
header and its own success criterion could not both be true, and the criterion won:**
`4194303UL` was shipped (plan 04, `46dd574`) because it is what DEAD-04 names, not because it
is cheaper -- the 2 B saving is a side effect of the correct choice, not the reason for it.
The cheaper-looking constant was not chosen to make the header's `-1364 B` figure come out;
the header is the thing that is wrong here, and this section corrects it.

---

## 4. OQ-2 -- both 64-bit figures

- The **eight** symbols DEAD-03's requirement text names (`__muldi3`, `__muldi3_6`,
  `__umoddi3`, `__udivdi3`, `__udivdi3_umoddi3`, `__udivmod64`, `__lshrdi3`, `__adddi3`) sum
  to **exactly 438 B**.
- The **full eleven-symbol contiguous blob** (`155-before-figures.md` §4) sums to **exactly
  528 B** -- the three the requirement text omits are `__umulsidi3` (2 B),
  `__umulsidi3_helper` (84 B) and `__ashrdi3` (4 B), 90 B total.

**Why the gate asserts all eleven, not eight:** `scripts/check_no_heap_or_64bit_symbols.py`'s
`DI64_SYMBOLS` frozenset (plan 02) names all eleven. A gate over only the eight named symbols
could PASS while 90 B of 64-bit runtime remained linked, if some future caller pulled
`__umulsidi3`/`__umulsidi3_helper`/`__ashrdi3` back in through a different call site -- the
eight-name gate would never see it. This phase's gate is proven, this session, to find zero of
all eleven on all three post-change ELFs (section 13, leg 5).

---

## 5. C-2 -- the per-half flash split is UNVERIFIED

ROADMAP/REQUIREMENTS state the phase's flash saving splits **-650 B** (heap removal) /
**-714 B** (64-bit runtime removal). `155-before-figures.md` §10 already marked this split
UNVERIFIED before either half of the source change existed; this section closes it now that
both halves have landed and can be measured directly.

| Item | Before | After | Δ |
|---|---|---|---|
| Heap blob (`malloc` 312 + `free` 274), contiguous | 586 | 0 | -586 |
| 64-bit runtime blob (11 symbols), contiguous | 528 | 0 | -528 |
| `rurp_read_voltage_mv` body | 434 (`0x1b2`) | **230** (`0x000000e6`) | -204 |
| `mem_util_blank_check` body | 510 (`0x1fe`) | **452** (`0x000001c4`) | -58 |

Under the natural attribution (each blob plus the function body that pulled it in): heap
`-586 + -58 = -644`; 64-bit runtime `-528 + -204 = -732`. **Neither matches -650 / -714.** The
natural-attribution total is `-644 + -732 = -1376`, which is **10 B more reduction** than the
measured whole-image delta of **-1366 B** (section 2) -- see section 6 for the residual. **The
TOTAL, -1366 B, is the reliable figure; the per-half split (-650/-714) is an artefact of how
the original survey attributed shared bytes between the two removals and remains UNVERIFIED.**
Quote the total, never the split.

---

## 6. The RAM and flash ledgers, item by item

### RAM ledger (sums to exactly -8, all three targets)

| Item | Δ RAM |
|---|---|
| Five allocator globals removed (`__brkval` 2, `__flp` 2, `__malloc_heap_end` 2, `__malloc_heap_start` 2, `__malloc_margin` 2) | **-10** |
| `handle` shrinks (603 B -> **601 B** on `uno`/`uno328pb`; 1115 B -> **1113 B** on `leonardo`) | **-2** |
| New file-scope static `blank_check_saved_address` (`uint32_t`) | **+4** |
| **Net** | **-8** |

`-10 + -2 + +4 = -8`, exactly matching the measured `ram_used` delta on all three targets
(section 2). Verified this session: `avr-nm --print-size --size-sort -C` on all three
post-change ELFs shows `handle` at `00000259` (601 B, `uno`/`uno328pb`) and `00000459`
(**1113** B, `leonardo`), and `blank_check_saved_address` at `00000004` (4 B) on all three.

### Flash ledger -- the residual, recorded not absorbed

Natural-attribution total (section 5): **-1376 B**. Measured whole-image delta (section 2):
**-1366 B**. Residual: `-1376 - (-1366) = -10`, i.e. **+10 B of unattributed growth
elsewhere** -- the natural per-component sum implies 10 B more reduction than what the linked
image actually shows. This residual is recorded here as unattributed, not folded into either
component to make the arithmetic look clean; it is most plausibly call-site register
allocation and inlining shifting slightly once both removals compound, and this record does
not claim to localise it further. This matches `155-RESEARCH.md`'s own measured +10 B
residual figure (quoted in `155-before-figures.md` §10) -- re-derived independently this
session from the after-figures rather than merely re-quoted.

---

## 7. DEAD-02 -- recorded as a latent defect CLOSED

**The defect.** `src/proms/memory.cpp` pre-change (quoted with today's line numbers in
`155-before-figures.md` §8): `mem_util_blank_check` called
`malloc(sizeof(blank_check_progress_data_t))` (a 4-byte `uint32_t`-holding struct) and, with
**no NULL test and no intervening check**, immediately dereferenced the result:
`progress_data->address = handle->address`. This is a genuine unchecked-allocation
dereference, present since the blank-check feature landed, on a part with under **473 B** of
**shared heap-and-stack headroom** (OQ-4, below) -- not a contrived example.

**Closed by removing the allocation entirely, not by adding a null check.** `src/proms/memory.cpp`
(commit `98e70af`, plan 05) replaces the `malloc`/cast/deref/`free` sequence with a
file-scope `static uint32_t blank_check_saved_address`, direct-assigned and direct-read. The
allocation had no reason to exist -- a single `uint32_t` living across two calls of one
function does not need heap indirection -- so removing it is the correct fix, not merely an
incidental optimisation. This is recorded here as a **latent defect closed**, per DEAD-02's
own instruction, not as incidental cleanup.

**OQ-4 -- the corrected per-target RAM derivation.** REQUIREMENTS DEAD-02 and ROADMAP
criterion 2 both say "roughly 470 B of free RAM once `handle` (1115 B) and the jsmn token
array (512 B) are accounted for." This double-counts: on `uno`, `handle` measures 603 B (pre-
change), not 1115 B -- 1115 B is `handle` (603 B) **plus** `tokens` (512 B) together, so the
sentence as written adds the 512 B a second time (`1115 + 512 = 1627`, matching no measured
figure). Corrected, per-target, at `FW_PRE_SHA` (before this phase's own RAM shrink, since
this is what a caller reasoned about at the time the allocation existed):

| Target | SRAM | `handle` | jsmn `tokens` | `handle`+`tokens` | `ram_used` | Free (shared heap-and-stack headroom) |
|---|---|---|---|---|---|---|
| `uno` | 2048 | 603 B | 512 B | 1115 B | 1575 | **473 B** |
| `uno328pb` | 2048 | 603 B | 512 B | 1115 B | 1581 | **467 B** |
| `leonardo` | 2560 | 1115 B | 512 B | 1627 B | 2016 | **544 B** |

**The ~470 B conclusion survives; its derivation does not.** Use the phrase "**shared
heap-and-stack headroom**", never "free RAM available to the allocator": `ram_used` counts
`.data`/`.bss` only, and the AVR call stack grows *down* into that same free region during
every operation, so the true margin available at the allocation site was smaller than 473 B
(or 467 B / 544 B) on every target -- never present those figures as available to the
allocator specifically.

---

## 8. DEAD-06 -- both suites updated, the count verified not assumed

Both native suites -- `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (ERASE-02) and
`test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (Case 30 / ERASE-01) -- had their
`TEST_ASSERT_NULL_MESSAGE(h.progress_data, ...)` assertions deleted and replaced with
explanatory comments, in the **same commit** (`98e70af`) as the header edit that removes
`firestarter_handle_t::progress_data` -- this is compiler-forced (both suites fail to
*build* without the matching edit). The surviving `is_operation_in_progress` assertion in
each suite still pins the observable behaviour.

**Native case count: verified at 172 across 17 suites, not assumed** -- this session's own
leg 1/2 runs (section 13) reproduce `172 test cases: 172 succeeded, 17 suites` on both
`pio test -e native` and `pio test -e native_nodevtools`, unchanged from `155-before-figures.md`
§12's pre-change baseline. This is the exact input `check_size_baseline.py:compare_native`
holds by equality (section 12).

**C-5, the "same statement" correction.** REQUIREMENTS DEAD-06 and ROADMAP criterion 6 both
say the surviving `is_operation_in_progress` assertion is set by "the same statement" as the
removed allocation. `memory.cpp`'s pre-change `:408`/`:409` (`set_operation_in_progress(handle);`
then `handle->progress_data = malloc(...)`) are **two distinct statements** -- "the same
statement" is factually false. **Corrected, stronger, true formulation:** the two statements
are **unconditionally adjacent statements in the same `then`-branch of the same `if`, with no
intervening control flow, early return or condition** -- so `is_operation_in_progress == false`
strictly implies the branch never executed, which strictly implies the allocation never
executed. The surviving assertion is therefore exactly as strong a witness as the deleted one
would have been. This corrected formulation now appears in three comment blocks across the
two native suites (all corrected in plan 05's single commit, `98e70af`).

**The rejected alternative, recorded with its measured cost.** Retaining a permanently-NULL
`void* progress_data` member solely so the two `TEST_ASSERT_NULL_MESSAGE` assertions kept
compiling was considered and rejected. Measured this session: `handle` drops from 603 B to
**601 B** (`uno`/`uno328pb`) and from 1115 B to **1113 B** (`leonardo`) -- exactly **2 B per
target**. The alternative is rejected because a permanently-NULL, never-written field would
make both assertions vacuous (`NULL == NULL` on a field nothing writes) -- this project's own
named hollow-gate failure mode (`tests/test_check_size_baseline.py`'s docstring precedent) --
for a saving of only 2 B, which is not worth manufacturing a vacuous gate.

---

## 9. DEAD-04 -- the oracle's readings, each with its measured value

All readings re-run this session directly against `tests/test_voltage_reformulation_oracle.py`'s
model functions (`_v64`/`_v32`), reading the calibration from `include/rurp_shield.h`
(`VALUE_R1` 270000, `VALUE_R2` 44000), never hardcoded.

- **Exact scale factor at the shipped calibration:** `k = (1100 * (270000 + 44000)) // 44000
  = 7850` exactly -- `1100 * 314000 = 345,400,000`, divided by `44000` with **zero
  remainder** (lossless folding).
- **Named single reading agreeing in both forms:** ADC 1023, bandgap 225 -> **35691 mV** in
  both the 64-bit and the 32-bit form, at the shipped calibration.
- **Bit-identity counts:** 0 mismatches over bandgap 200-250 x ADC 0-1023 (51,200 evals) at
  the shipped calibration; 0 mismatches over the **full** plausible bandgap range 1-1023 x ADC
  0-1023 -- **1,047,552 evaluations, 0 mismatches** (re-measured this session; this
  supersedes plan 04's SUMMARY figure of "1,046,529", which does not reproduce from
  `range(1, 1024)` x `range(0, 1024)` = `1023 * 1024 = 1,047,552` -- the SUMMARY's number is
  itself corrected here rather than propagated).
- **Worst deviation over the stated grid (R2 39000-47000 step 1000, bandgap 200-250, ADC
  0-1023, 470,016 evaluations, one pass):** exactly **5 mV**, argmax `(adc=893, bg=200,
  r2=41000, v64=37256, v32=37251)`.
- **One-directional result:** 0 over-reads across all 470,016 evaluations -- the 32-bit form
  is never greater than the 64-bit form; it can only ever under-read.
- **Guard A boundary pair (sum <= 3900000):** `r1=3856000, r2=44000` (sum **exactly
  3900000**, AT the guard) returns non-zero; `r1=3856001, r2=44000` (sum 3900001, one past)
  returns 0.
- **Guard B boundary pair (k <= 4194303):** `r1=3812003, r2=1000` gives `k = **4194303**
  exactly` (AT the guard) and returns non-zero; `r1=3812004, r2=1000` gives `k = 4194304`
  (one past) and returns 0. Both guard-B pairs keep their sum at or below 3900000, so guard A
  is provably not what fires there. At `k=4194303`, ADC 1023, the product `1023 * 4194303 =
  4,290,771,969` stays below the 32-bit ceiling `4,294,967,295` -- confirming guard B's bound
  is exactly right, not merely close.
- **Both zero sentinels:** `r2 == 0` and `bg == 0` both return 0, preserved unchanged from the
  pre-existing 64-bit form's own zero-sentinel behaviour.

**The nominal grid reaches NEITHER guard** -- at R2 39k-47k, `k` maxes at 8715 and `r1+r2`
maxes at 317000, both three-plus orders of magnitude below their guards. This is why the four
dedicated boundary cases exist: without them, both guards would be entirely unexercised by any
plausible reading.

---

## 10. OQ-3 -- the corrected, asymmetric tolerance statement

REQUIREMENTS DEAD-04 and ROADMAP criterion 4 both describe the consumer window as `+/-5 %`
(symmetric). The real window is **asymmetric**: the low edge is a **-5 % relative** bound
(`-600 mV` at 12 V), and the high edge is a **fixed +500 mV absolute** bound
(`src/proms/eprom.cpp:713`, `src/proms/flash_intel.cpp:39`). So the 5 mV worst-case deviation
(section 9) is **1.0 %** of the tighter 500 mV window and **0.83 %** of the 600 mV edge --
either way comfortably inside both, but the two edges are not the same kind of bound and must
not be described as if they were.

**The directional argument, corrected and stronger than the symmetric claim:** because the
reformulation only ever **under-reads** (0 over-reads across 470,016 evaluations, section 9),
it can **never suppress the high-side error** (`MSG_ERR_VPP_HIGH`, which fires on an
*over*-read condition) -- an under-read can only ever push a true voltage that is already
within 5 mV of the *low* edge into a spurious low-side warning. This is a materially stronger,
one-directional claim than the symmetric `+/-5 %` framing in the ROADMAP and REQUIREMENTS,
both of which are corrected here.

---

## 11. DEAD-05 -- the coverage ceiling, mandated wording

`src/boards/rurp_common.cpp` is compiled by **no native environment** -- `[env:native]`'s and
`[env:native_nodevtools]`'s shared `build_src_filter` (`platformio.ini:227`, `:307`) admits
only `+<proms/>`, `+<boards/rurp_serial_utils.cpp>`, `+<json_parser.c>` and
`+<operation_utils.cpp>`. `rurp_read_voltage_mv` is therefore:

*"proven by a committed host-side numerical oracle over a stated input grid, bound to
the shipped C by a source-contract scan; no native and no bench coverage exists."*

**Named residual risk, stated as unmitigated:** avr-gcc miscompiling the 32-bit
multiply/divide in `rurp_read_voltage_mv`. **Unmitigated by any artefact of this phase.**
Mitigated only by that being AVR's most-exercised code-generation path, and by this phase's
change *reducing* rather than increasing codegen complexity (removing the 64-bit runtime
helpers and their call sites, not adding a new one).

**The phrasing gate's verdict, re-run over the real corpus with this file now present**
(`python3 .planning/milestones/v1.33-artifacts/tools/check_dead05_phrasing.py`, run from `/workspaces`, exit 0):

```
PASS: 21 file(s) scanned, 75 in-scope paragraph(s) found (floor 6)
  ... (per-file in-scope paragraph counts; 155-05-SUMMARY.md, memory.cpp, firestarter.h and
      both native test files each carry 0 -- no paragraph in them names rurp_read_voltage_mv,
      which is expected: DEAD-06's edits are about progress_data, not the voltage function)
  required target OK (mandated phrasing present): .../155-VALIDATION.md
  required target OK (mandated phrasing present): .../155-after-figures.md
  required target OK (mandated phrasing present): firestarter/src/boards/rurp_common.cpp
  required target OK (mandated phrasing present): firestarter/tests/test_voltage_reformulation_oracle.py
```

**21 files scanned (up from plan 05's 19 -- this file and, once it exists, `155-06-SUMMARY.md`
add two more), 75 in-scope paragraphs found (well above the `PARAGRAPH_FLOOR = 6` non-vacuity
floor), 0 forbidden-phrasing violations, all four required-positive targets confirmed carrying
the mandated phrasing verbatim (whitespace-normalised).** This run was performed with this
file's own content still being finalised (self-referential: editing this file changes its own
in-scope paragraph count); the plan's own `<verification>` re-run obligation (see the closing
section below) governs the true final run, performed once `155-06-SUMMARY.md` also exists.

**Correction recorded (constraint 3): the SUMMARY class is not exempt.** Five forbidden-
phrasing violations had accumulated across plan 03's and plan 04's own SUMMARY files (four
paragraphs in `155-03-SUMMARY.md`, one in `155-04-SUMMARY.md`) -- prose describing the gate's
own matching behaviour by quoting its needles, not a coverage claim about the firmware
function. These were corrected at meta commit `b73679aa` by rewording them to cite
`155-VALIDATION.md` item 5 by pointer instead of quoting the needle verbatim -- the same fix
plan 03's own executor applied mid-task to the corpus doc itself. **The three named
exclusions stay at exactly three** (`155-RESEARCH.md`, `155-PATTERNS.md`, `155-VALIDATION.md`);
exempting the SUMMARY file class would have gutted the gate on precisely the file class where
a false coverage claim matters most -- SUMMARY files are the artefact most likely to be read
by a future auditor without also reading the source.

---

## 12. D-03 -- the size-baseline policy, one-sided, no exemption, baseline untouched

`scripts/baseline/size_baseline.json` is **byte-unchanged** by this phase -- confirmed:
`git -C firestarter diff --quiet -- scripts/baseline/size_baseline.json` exits 0. No
`--rebuild` flag was ever passed to `check_size_baseline.py` in this phase.

**The default (no `--policy`) run is strict byte-identity and fails, as expected, on a
+478/+476/+540-B-stale baseline** -- this is not a policy failure attributable to this
phase, it is what a strict-equality comparator against an admittedly-stale file always does
once the tree moves:

```
FAIL:
  uno: flash_used baseline=25548 observed=24660
  uno: ram_used baseline=1575 observed=1567
  uno328pb: flash_used baseline=25598 observed=24708
  uno328pb: ram_used baseline=1581 observed=1573
  leonardo: flash_used baseline=27630 observed=26804
  leonardo: ram_used baseline=2016 observed=2008
```

**The `--policy merge05` band comparison is the ONE-SIDED one, and it PASSES with no
exemption authored.** `check_size_baseline.py:697` is `if flash_delta > allowance:` and its
RAM counterpart is `if ram_delta > ram_tolerance:` -- both fire only on **growth** past an
allowance; a **shrink** always passes with room to spare. Run against the frozen
`size_baseline_base01.json` record with real build logs from this session:

```
PASS: leonardo(flash=26804/32768[-102<=724=band0+exempt96+seam210+lock288+erase130],ram=2008/2560[-6<=2=seam2]),
uno(flash=24660/32768[-164<=788=band64+exempt96+seam210+lock288+erase130],ram=1567/2048[-6<=2=seam2]),
uno328pb(flash=24708/32768[-166<=788=band64+exempt96+seam210+lock288+erase130],ram=1573/2048[-6<=2=seam2])
```

**This is recorded AS one-sided, and no exemption was authored** -- unlike the four flash
exemptions (v1.31-v1.32) and one RAM exemption already stacked in this comparator's own
constants, this phase's negative delta needed none. This is the **first size movement in this
project's history that does not need one**, and it is recorded that way so a future reader
never mistakes this green run for "nothing moved."

**The only exact-equality comparisons in this script are the two capacity figures**
(`flash_total`, `ram_total`), and both are **unchanged**: 32768 flash on all three targets;
2048 / 2048 / 2560 RAM. A reduction of this size trips no exact-equality assertion anywhere in
this script.

**The canonical policy invocation, run and recorded, its non-zero exit attributed correctly.**
The script's own `Usage:` block names the canonical MERGE-05 invocation. Run with real
sequential native logs from this session added:

```
FAIL:
  native: cases baseline=141 observed=172
  native_nodevtools: cases baseline=141 observed=172
```

Exit 1, **and it exits before it ever reports flash** -- `compare_native`'s exact-equality
case-count assertion runs ahead of the AVR flash/RAM comparison in `main()`. This is
**pre-existing** -- `size_baseline_base01.json` is frozen at Phase 124's native case count
(141); every native suite added since (through Phase 155) grew that count to 172 without
BASE-01 ever being re-anchored. **It is not caused by this phase**: the size-reduction diff
touches zero files under `test/` except the two native suites DEAD-06 edits, and DEAD-06's
edit removes an assertion, not a case -- the count itself is unmoved (172 before and after,
verified this session, section 8). This is **REQUIREMENTS LAND-03 / Phase 158's item**,
carried forward here, not resolved here.

**The size script runs in NO CI workflow of either repository.** Every leg-7 figure above is
a **local-run obligation** for anyone who wants it re-confirmed -- stated plainly rather than
implying automated coverage.

---

## 13. The eight phase-gate verdicts

| # | Leg | Command | Result |
|---|---|---|---|
| 1 | `pio test -e native` | `pio test -e native` | **172 test cases: 172 succeeded**, 17 suites, 21.7 s |
| 2 | `pio test -e native_nodevtools` | `pio test -e native_nodevtools` (run sequentially, after leg 1) | **172 test cases: 172 succeeded**, 17 suites, 30.6 s |
| 3 | `python3 -m pytest tests/ -q` | run on a clean, committed tree (after the plan's own firmware commit `adf1a31` landed) | **348 passed**, 0 failed, 11.9 s (323 pre-change baseline + 9 plan-02 legs + 15 plan-04 legs + 1 plan-06 leg = 348) |
| 4 | Heap gate | `python3 scripts/check_no_heap_or_64bit_symbols.py` | **0** heap-set matches on all three ELFs |
| 5 | 64-bit gate (all 11) | (same invocation, same run) | **0** of all eleven 64-bit-set matches on all three ELFs; `PASS: leonardo(heap=0,64bit=0,anchors=2/2), uno(heap=0,64bit=0,anchors=2/2), uno328pb(heap=0,64bit=0,anchors=2/2)` |
| 6 | `pio run` all three targets | `pio run -e {uno,uno328pb,leonardo}` | flash/RAM as section 2; delta **-1366 B flash / -8 B RAM** on all three, computed against `155-before-figures.md` |
| 7 | `check_size_baseline.py` | see section 12 | **one-sided PASS** under `--policy merge05` against BASE-01, no exemption authored; the canonical invocation's pre-existing native-case-count FAIL is Phase 158 / LAND-03's item; baseline file byte-unchanged |
| 8 | `check_build_warnings.py` | `--log uno=<clean uno rebuild log>` (forced clean recompile via `pio run -t clean -e uno` so the log reflects a real compile of both edited files) | `PASS: uno: macro_redefinition=0 (== 0)` -- no new warning attributable to `memory.cpp`, `rurp_common.cpp` or `firestarter.h` |

**Gate proven from both directions.**
- **Pre-change negative (real, committed since plan 02):**
  `tests/fixtures/planted_no_heap_or_64bit_symbols_prechange_uno/avr-nm-uno.txt` -- exit 1, 18
  violations (7 heap + 11 sixty-four-bit).
- **Post-change positive (real, committed this plan):**
  `tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/avr-nm-uno.txt` -- exit 0,
  `PASS:`, both counts 0, both anchors found. Paired with a new leg,
  `test_real_postchange_listing_exits_zero`, in `tests/test_check_no_heap_or_64bit_symbols.py`
  (commit `adf1a31`).
- **Post-change planted negative (throwaway worktree, NOT committed):** a throwaway `git
  worktree` was created off `FW_POST_SHA` under the session scratch directory. Inside it, one
  allocation call was reinstated in `mem_util_blank_check` -- `malloc`ing a `uint32_t`, storing
  through it, reading it back later, then `free`ing it (mirroring the pre-change shape closely
  enough that the compiler cannot prove the pair has no observable effect and elide it; a
  naive unused-malloc+immediate-free WAS elided by the compiler on the first attempt and had
  to be corrected to this shape). `pio run -e uno` inside that worktree relinked the allocator
  (flash 24660 -> 25292, RAM 1567 -> 1575). Running the gate against that worktree's build root
  with `--build-root`:
  ```
  FAIL: 7 forbidden symbol(s) found:
    uno: __brkval (heap, type B, 2 B)
    uno: __flp (heap, type B, 2 B)
    uno: __malloc_heap_end (heap, type D, 2 B)
    uno: __malloc_heap_start (heap, type D, 2 B)
    uno: __malloc_margin (heap, type D, 2 B)
    uno: free (heap, type T, 274 B)
    uno: malloc (heap, type T, 312 B)
  ```
  Exit **1**, naming the allocator entry points `malloc` and `free` by name alongside their
  five supporting globals -- proving the gate still fires against an otherwise-shipped
  post-change tree. The worktree was then removed (`git worktree remove --force`) and pruned;
  `git -C firestarter worktree list` shows only the main tree plus the pre-existing, unrelated
  `firestarter_py32_ci` worktree (present before this session, untouched); `git -C firestarter
  status --porcelain` is empty; no branch was created for the throwaway worktree; and
  `git -C firestarter rev-parse --verify wip/v1.33-size-reduction-survey-preserved` still
  resolves to `a6b46f8b12e81c62d9958945eb0bdbb8c16ae699`, unchanged.

  **Both directions plus a real positive control together close the hollow-gate question:** a
  real pre-change negative, a real post-change positive, and a planted post-change negative --
  the gate can fail, the gate can pass, and the gate can be made to fail again on demand
  against the shipped tree.

---

## 14. Phase 159's input -- source lines shifted, zero citations remapped

This phase shifted lines in **five** pre-existing source files:

1. `firestarter/src/boards/rurp_common.cpp` (plan 04 -- the 32-bit reformulation)
2. `firestarter/src/proms/memory.cpp` (plan 05 -- the heap removal)
3. `firestarter/include/firestarter.h` (plan 05 -- `progress_data` member removed)
4. `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (plan 05 -- assertion + comments)
5. `firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (plan 05 -- assertion + comments)

**Zero `.planning/` citations were remapped, by D-01.** Phase 154's remap tool
(`remap_citations.py`) exists and is proven idempotent, but is explicitly **not applied** in
Phases 154-158 -- application is Phase 159 / REMAP-01...05's job, running exactly once over
the **composite pre-154 -> post-158 diff**, per `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md` (the
close-blocking staleness marker Phase 154 planted). This phase adds its five files to that
marker's already-knowingly-stale set; it does not touch the marker file itself (that is
Phase 159 / REMAP-04's job, removing the marker once the repair lands).

---

## 15. Scope fence honoured

**`include/memory_utils.h` was NOT touched.** `155-PATTERNS.md` verified it holds no
reference to `progress_data` or the removed allocation; its own hunk in the preserved
reference (`a6b46f8`) belongs to Phase 156 (DEDUP), not this phase. Confirmed this session:
`git -C firestarter diff 2ad5b322a37ba4a88afd09cc946f5c4114e51483..adf1a31 --name-only`
does not list `include/memory_utils.h`.

**The preserved reference (`a6b46f8`, `wip/v1.33-size-reduction-survey-preserved`) was used
semantically and never applied as a patch.** Four defects in its in-scope hunks were
corrected rather than carried across, all recorded across plans 04/05 and restated here:

1. The false coverage claim on `rurp_read_voltage_mv` naming the first forbidden phrasing
   enumerated in `155-VALIDATION.md` item 5 (corrected to the mandated DEAD-05 phrasing,
   section 11).
2. The `4000000UL` guard constant (shipped `4194303UL` instead, OQ-1, section 3).
3. The symmetric `+/-5 %` tolerance claim (corrected to the asymmetric window, OQ-3, section 10).
4. The undercounted 438 B 64-bit symbol figure (corrected to record both 438 B and the true
   528 B full-blob total, OQ-2, section 4).

`firestarter/tests/fixtures/clean_no_heap_or_64bit_symbols_postchange_uno/`,
`firestarter/tests/test_check_no_heap_or_64bit_symbols.py`'s new leg, and this file are the
only artefacts this plan adds; no file under `scripts/baseline/`, `src/`, `include/` (other
than the two already-landed plan-04/05 edits, both pre-existing before this plan started) was
touched by this plan.

---

## Deviations recorded from predecessor plans, reconciled here

Per this plan's constraint 8, three predecessor deviations are reconciled rather than
dropped:

1. **Plan 02** reverted a premature `requirements mark-complete DEAD-01 DEAD-03` after
   recognising the gate existed but the source removal (this phase's whole point) had not yet
   landed -- REQUIREMENTS.md was left unchanged (`git checkout --`) and both requirements
   stayed `Pending` until this plan (section 16, below) closes them against real evidence.
2. **Plan 04** hit a `pytest -k` filter substring collision: the plan's own verify command's
   `-k "not shipped_c and not sixty_four_bit and not model_constants"` unintentionally
   deselected three mandated numeric legs too (`shipped_c` is a substring of
   `test_scale_factor_is_exact_at_the_shipped_calibration` and both
   `..._shipped_calibration_...` legs), so the literal command collected 9/12, not 12+. Plan
   04's executor did not rename the mandated test names (out of scope for an auto-fix);
   instead it verified the RED/GREEN split via explicit `--deselect`/node-id selection,
   reaching the same proof by a collision-free path. No commit was affected.
3. **Plan 05** reworded comments across all four edited files to avoid the literal string
   `progress_data`, because the plan's own acceptance criterion required a summed grep count
   of exactly 0 for that string across the four files -- which meant the surviving comments
   (including the reference-quoted replacement text in `155-PATTERNS.md`) could not name the
   removed field by its old identifier. Both replacement comments describe "the removed
   heap-allocated handle field" instead.

---

## 16. Requirement closure -- ticked only where evidence ran green this session

- **DEAD-01** (no `malloc`/`free`/`realloc`/`calloc`/`__brkval` symbol): CLOSED. Leg 4/5 this
  session, section 13, `heap=0` on all three ELFs; the allocator's sole caller
  (`mem_util_blank_check`) now uses a file-scope static (section 6/7).
- **DEAD-02** (unchecked dereference closed, recorded as a latent defect): CLOSED. Section 7,
  the defect quoted, the closure mechanism stated, OQ-4's corrected derivation given.
- **DEAD-03** (no 64-bit runtime helper, all eleven, `rurp_read_voltage_mv` body shrunk):
  CLOSED. Leg 4/5 this session, `64bit=0` on all three ELFs, both totals (438/528 B) recorded
  (section 4), body confirmed at `230 B` (`0x000000e6`) this session (section 5).
- **DEAD-04** (32-bit reformulation proven equivalent by committed oracle): CLOSED. Section 9,
  every required reading re-run this session and confirmed: `k=7850` exact, the named reading
  `35691 mV` both forms, bit-identical over the stated and the full bandgap ranges, 5 mV worst
  deviation one-directional, both guard boundaries at their exact pairs, both zero sentinels.
- **DEAD-05** (coverage ceiling stated, not implied): CLOSED. Section 11, mandated phrasing
  quoted verbatim, residual risk named as unmitigated, phrasing gate run clean over the real
  corpus this session (PASS, 0 violations, all four required targets confirmed).
- **DEAD-06** (both native suites updated, behaviour pinned, alternative recorded with cost):
  CLOSED. Section 8, both suites' comments corrected (adjacency formulation), native case
  count verified 172/17 this session, rejected alternative's 2 B-per-target cost measured this
  session.

All six requirements' proofs ran green in this session, on this tree, at `FW_POST_SHA`
`adf1a31`. `.planning/REQUIREMENTS.md`'s DEAD-01...DEAD-06 checkboxes are ticked by this
plan's state-update step against exactly this evidence.

---

## Re-run obligation (verification, not optional)

This record's own DEAD-05 phrasing-gate run in section 11 was performed with
`155-06-SUMMARY.md` **not yet existing** (SUMMARY files are themselves in the corpus, per
`155-dead05-phrasing-corpus.md` glob 2). Per this plan's `<verification>` block, the phrasing
gate (`python3 .planning/milestones/v1.33-artifacts/tools/check_dead05_phrasing.py`, run from `/workspaces`) MUST
be re-run once more after `155-06-SUMMARY.md` is written and committed, and the phase is not
complete until that re-run is also green. This is not an optional extra -- it is the final
verification step of this plan.
