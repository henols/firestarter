---
title: Before-figures record — milestone v1.33, Phase 155 (Dead-Weight Removal)
phase: 155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim
plan: "01"
measured: 2026-08-23
status: AUTHORITATIVE — this file is the ONLY source for Phase 155's before-half figures. Phases 156, 157 and 158 each invalidate the measurements captured here, so no later plan can re-derive them. Supersedes the "roughly 470 B" / "handle (1115 B)" / "the same statement" / "438 B" / "−650 / −714" figures quoted in ROADMAP.md and REQUIREMENTS.md for DEAD-01/DEAD-02/DEAD-03, per the corrections in §7-§10 below.
supersedes: >
  ROADMAP.md Phase 155 criteria 2, 4 and 6, and REQUIREMENTS.md DEAD-02/DEAD-03/DEAD-06 prose,
  wherever they state a figure or derivation this file corrects. `scripts/baseline/size_baseline.json`
  does not stand in for this file either -- it is +478/+476/+540 B stale against this tree by its
  own `meta` block's admission (quoted in §11).
requirements: [DEAD-01, DEAD-02, DEAD-03]
---

# Before-figures record — v1.33 Phase 155

Every number in this file was measured on a **clean, unedited** `firestarter` working tree
during this plan's session. Each number carries the verbatim command that produced it.
Nothing here is quoted from `155-RESEARCH.md` except where §10 explicitly says otherwise
and states why (that one component decomposition requires a post-change build, which this
before-only plan is prohibited from producing). Every flash/RAM figure is labelled **WARM**.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_PRE_SHA` | `2ad5b322a37ba4a88afd09cc946f5c4114e51483` |
| `firestarter` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` |
| `git -C firestarter status --porcelain` | empty (asserted before and after this plan's work) |
| `git -C firestarter diff --name-only HEAD` | empty |
| meta HEAD sha (before this plan's commit) | `018686758986df10c8df4390fe7cffb1a6858f86` |

**`firestarter_app` gitlink note:** the meta repo shows `firestarter_app` as modified
(`git status --porcelain` in `/workspaces`). This is **pre-existing Phase 154 drift, operator-gated**,
not touched, staged or re-pinned by this plan or any plan in this phase.

Commands run:
```bash
git -C firestarter rev-parse HEAD
git -C firestarter branch --show-current
git -C firestarter status --porcelain
git -C firestarter diff --name-only HEAD
git rev-parse HEAD   # meta repo
```

---

## 2. Flash and RAM, all three targets (WARM)

| Target | Flash used | Flash total | RAM used | RAM total | Label |
|---|---|---|---|---|---|
| `uno` | **26026** | 32768 | **1575** | 2048 | **WARM** |
| `uno328pb` | **26074** | 32768 | **1581** | 2048 | **WARM** |
| `leonardo` | **28170** | 32768 | **2016** | 2560 | **WARM** |

Command per target: `pio run -e uno`, `pio run -e uno328pb`, `pio run -e leonardo` (run from
`/workspaces/firestarter`; `.pio/build/` was warm going in). All six figures matched the
expected values exactly on the first run this session — no toolchain or tree drift found.

**These figures are deliberately WARM, not cold.** LAND-01 / Phase 158 owns the cold
re-record; re-recording cold here would duplicate that plan's job and risk a second,
inconsistent "before" position.

---

## 3. The heap set

**Contiguous span, `uno`: `0x6246`–`0x6490` = 586 B** (`malloc` end address `0x6246 + 0x138 = 0x637e`
is exactly `free`'s start address; `free` end address `0x637e + 0x112 = 0x6490`).

| Symbol | Addr (`uno`) | Size | Section |
|---|---|---|---|
| `malloc` | `0x6246` | **312 B** (`0x138`) | .text |
| `free` | `0x637e` | **274 B** (`0x112`) | .text |
| `__brkval` | `0x800723` | 2 B | .bss |
| `__flp` | `0x800725` | 2 B | .bss |
| `__malloc_heap_end` | `0x800107` | 2 B | .data |
| `__malloc_heap_start` | `0x800109` | 2 B | .data |
| `__malloc_margin` | `0x80010b` | 2 B | .data |

**`realloc` and `calloc` are ABSENT** from the linked image on all three ELFs (`uno`, `uno328pb`,
`leonardo`) — checked explicitly, not omitted by silence.

Heap-set match count (the two counts plan 02's gate will assert are zero after the change): **7**
on each of the three ELFs.

Command: `avr-nm --print-size --size-sort -C .pio/build/<env>/firestarter_<env>.elf`, resolved at
`$HOME/.platformio/packages/toolchain-atmelavr/bin/avr-nm` (confirmed executable). Absence check:
```bash
avr-nm ... | grep -cE ' (T|t|B|b|D|d) (malloc|free|realloc|calloc|__brkval|__flp|__malloc_heap_start|__malloc_heap_end|__malloc_margin)$'
```

---

## 4. The 64-bit runtime set — all ELEVEN symbols

**Contiguous span, `uno`: `0x6036`–`0x6246` = 528 B**, and it directly abuts the heap blob above
(`0x6246` is both the 64-bit blob's end and the heap blob's start — the two blobs are one
contiguous `0x6036`–`0x6490` = 1114 B region).

| Symbol | Addr (`uno`) | Size |
|---|---|---|
| `__muldi3` | `0x6036` | 158 B |
| `__muldi3_6` | `0x60d4` | 18 B |
| `__umulsidi3` | `0x60e6` | 2 B |
| `__umulsidi3_helper` | `0x60e8` | 84 B |
| `__umoddi3` | `0x613c` | 4 B |
| `__udivdi3` | `0x6140` | 2 B |
| `__udivdi3_umoddi3` | `0x6142` | 22 B |
| `__udivmod64` | `0x6158` | 162 B |
| `__ashrdi3` | `0x61fa` | 4 B |
| `__lshrdi3` | `0x61fe` | 54 B |
| `__adddi3` | `0x6234` | 18 B |

**Both totals, stated side by side:**
- The **eight** symbols DEAD-03's requirement text names (`__muldi3`, `__muldi3_6`, `__umoddi3`,
  `__udivdi3`, `__udivdi3_umoddi3`, `__udivmod64`, `__ashrdi3`... — see note below) sum to
  **exactly 438 B**: `158 + 18 + 4 + 2 + 22 + 162 + 54 + 18 = 438`. (The eight named are
  `__muldi3`, `__muldi3_6`, `__umoddi3`, `__udivdi3`, `__udivdi3_umoddi3`, `__udivmod64`,
  `__lshrdi3`, `__adddi3`.)
- The **full eleven-symbol contiguous blob** sums to **exactly 528 B**:
  `2 + 2 + 4 + 4 + 18 + 18 + 22 + 54 + 84 + 158 + 162 = 528`.

**Consequence:** an absence check over only the eight named symbols could pass while **90 B**
of 64-bit runtime is still linked, because `__umulsidi3` (2 B), `__umulsidi3_helper` (84 B) and
`__ashrdi3` (4 B) are omitted from the requirement's list (`2 + 84 + 4 = 90`). Plan 02's gate
therefore asserts on **all eleven**, not the named eight. The "438 B" figure stands as the
named-subset figure provided the 528 B total is recorded alongside it, as it is here.

64-bit-set match count: **11** on each of the three ELFs (`uno`, `uno328pb`, `leonardo`).

Command: `avr-nm --print-size --size-sort -C .pio/build/<env>/firestarter_<env>.elf`; absence
check:
```bash
avr-nm ... | grep -cE '__(muldi3|muldi3_6|udivmod64|lshrdi3|udivdi3|udivdi3_umoddi3|umoddi3|adddi3|umulsidi3|umulsidi3_helper|ashrdi3)$'
```

---

## 5. Sole-caller attribution — by disassembly, not by reading source

**Method:** `avr-objdump -d .pio/build/uno/firestarter_uno.elf` was captured in full, then a
throwaway Python script (session scratch only, not committed) walked the disassembly, tracked
the enclosing function from each `<name>:` header line, and attributed every `call`/`jmp`
reference to that enclosing function.

**Why not read source instead:** reading the eight symbols named in DEAD-03's requirement text
misses three of the eleven 64-bit symbols entirely (§4) — the disassembly attribution does not,
because it walks every symbol actually linked, not a hand-maintained list.

Verbatim attribution output:

```
__adddi3 <- {rurp_read_voltage_mv}  (n=1)
__ashrdi3 <- {}  (n=0)
__lshrdi3 <- {rurp_read_voltage_mv}  (n=1)
__muldi3 <- {rurp_read_voltage_mv}  (n=1)
__muldi3_6 <- {__muldi3, __umulsidi3_helper}  (n=2)
__udivdi3 <- {rurp_read_voltage_mv}  (n=1)
__udivdi3_umoddi3 <- {}  (n=0)
__udivmod64 <- {__udivdi3_umoddi3}  (n=1)
__umoddi3 <- {}  (n=0)
__umulsidi3 <- {rurp_read_voltage_mv}  (n=1)
__umulsidi3_helper <- {}  (n=0)
free <- {mem_util_blank_check}  (n=1)
malloc <- {mem_util_blank_check}  (n=1)
```

**Reading:** `malloc` and `free` each have **exactly one caller**, `mem_util_blank_check` — no
others. `__muldi3`, `__adddi3`, `__lshrdi3`, `__udivdi3` and `__umulsidi3` each have **exactly
one user-code caller**, `rurp_read_voltage_mv` — no others. The remaining four
(`__umoddi3`, `__udivdi3_umoddi3`, `__umulsidi3_helper`, `__ashrdi3`, `(n=0)` above) are reached
only by fall-through from the immediately preceding instruction inside the blob, so no explicit
`call`/`jmp` targets them — they are entered structurally, not called, and have no caller outside
the blob. `__muldi3_6` and `__udivmod64` are called only from inside the blob
(`__muldi3`/`__umulsidi3_helper` and `__udivdi3_umoddi3` respectively). This is the strongest
available evidence for DEAD-01 criterion 1 and DEAD-03's "alone pulled them in", and it cannot be
reproduced after plans 04/05 land.

---

## 6. Function and object sizes

| Symbol | Size | `uno` addr |
|---|---|---|
| `rurp_read_voltage_mv` | **434 B** (`0x1b2`) | `0x1fd6` |
| `mem_util_blank_check` | **510 B** (`0x1fe`) | `0x3376` |
| `handle` (.bss) | **603 B** (`0x25b`) on `uno`/`uno328pb`, **1115 B** (`0x45b`) on `leonardo` | `0x8004c8` (`uno`) |
| `parse_json(firestarter_handle*)::tokens` (.bss) | **512 B** (`0x200`) | `0x8002c8` (`uno`) |

Command: `avr-nm --print-size --size-sort -C .pio/build/<env>/firestarter_<env>.elf`.

---

## 7. DEAD-02's RAM headroom, derived not quoted

| Target | SRAM | `handle` | jsmn `tokens` | `handle`+`tokens` | `ram_used` (all statics) | free |
|---|---|---|---|---|---|---|
| `uno` | 2048 | 603 B | 512 B | **1115 B** | 1575 | **473 B** |
| `uno328pb` | 2048 | 603 B | 512 B | 1115 B | 1581 | **467 B** |
| `leonardo` | 2560 | 1115 B | 512 B | 1627 B | 2016 | **544 B** |

**Correction (was C-3):** REQUIREMENTS DEAD-02 and ROADMAP criterion 2 both say "roughly 470 B
of free RAM once `handle` (1115 B) and the jsmn token array (512 B) are accounted for." On `uno`,
`handle` measures **603 B**, not 1115 B — **1115 B is `handle` (603 B) plus `tokens` (512 B)
together**, so the sentence as written adds the 512 B a second time (`1115 + 512 = 1627`, which
does not match any measured figure). Separately, `leonardo`'s `handle` genuinely does measure
1115 B on its own (because `DATA_BUFFER_SIZE` is 1024 there instead of 512) — a coincidence of
magnitude, not the same quantity.

**The ~470 B conclusion survives; its derivation does not.** Corrected statement: on `uno`,
`handle` (603 B) and the jsmn token array (512 B) together consume 1115 B of the 2048 B SRAM,
leaving 473 B; `uno328pb` measures 467 B free by the same arithmetic; `leonardo` (`handle` 1115 B
+ tokens 512 B = 1627 B of 2560 B) leaves 544 B.

**Use the phrase "shared heap-and-stack headroom", not "free RAM":** `ram_used` counts `.data`
and `.bss` only. The AVR call stack grows *down* into that free region during every operation, so
the true margin available at the allocation site is **less than** 473 B (or 467 B / 544 B) — never
present 473 B as available *to the allocator specifically*. `NUMBER_JSNM_TOKENS` is 64
(`include/json_parser.h:17`) × 8 B per `jsmntok_t` = the measured 512 B
`parse_json(firestarter_handle*)::tokens`; `handle` is the file-scope global at
`src/firestarter.cpp:33`.

---

## 8. The pre-change defect (DEAD-02)

`src/proms/memory.cpp:498-509` today:

```c
void mem_util_blank_check(firestarter_handle_t* handle) {
    blank_check_progress_data_t* progress_data;                                  // 406
    if (!is_operation_in_progress(handle)) {                                      // 407
        set_operation_in_progress(handle);                                        // 408
        handle->progress_data = malloc(sizeof(blank_check_progress_data_t));      // 409  <- alloc
        progress_data = (blank_check_progress_data_t*)handle->progress_data;      // 410
        progress_data->address = handle->address;                                 // 411  <- unchecked deref
        handle->address = 0;                                                      // 412
    } else {
        progress_data = (blank_check_progress_data_t*)handle->progress_data;      // 414
        if (handle->address >= handle->mem_size) {                                // 415
            clear_operation_in_progress(handle);                                  // 416
            handle->address = progress_data->address;                            // 417
            free(handle->progress_data);                                          // 418
            handle->progress_data = NULL;                                         // 419
            return;
        }
    }
```

and the struct it allocates, `memory.cpp:489-460`:

```c
typedef struct {
    uint32_t address;
} blank_check_progress_data_t;
```

`:409` calls `malloc`; `:411` writes through the result with **no NULL test** and no intervening
check between the two lines. `sizeof(blank_check_progress_data_t)` is **4 bytes** — one
`uint32_t`. A 586 B allocator (§3) was linked, and a null-deref hazard accepted, to hold four
bytes across two calls of one function, on a target with under 473 B of shared heap-and-stack
headroom (§7). This is a latent defect present at `FW_PRE_SHA`, recorded here so plan 06 can
record its closure against this measured pre-state.

---

## 9. The "same statement" correction (was C-5, DEAD-06)

ROADMAP criterion 6 and REQUIREMENTS DEAD-06 both say the surviving `is_operation_in_progress`
assertion is set by *"the same statement"* as the allocation. `memory.cpp:500` and `:409`:

```c
        set_operation_in_progress(handle);                                    // :408
        handle->progress_data = malloc(sizeof(blank_check_progress_data_t));  // :409
```

`set_operation_in_progress` expands to `handle->operation_state |= OPERATION_IN_PROGRESS`
(`include/operation_utils.h`) and touches nothing else. **These are two distinct statements**,
so "the same statement" is factually wrong.

**Corrected, stronger and true formulation:** `:408` and `:409` are **unconditionally adjacent
statements in the same `then`-branch of the same `if`, with no intervening control flow, early
return or condition** — so `is_operation_in_progress == false` strictly implies the branch never
executed, which strictly implies the `malloc` never executed. The surviving assertion is
therefore exactly as strong a witness for "the blank check did not run" as the deleted allocation
would have been. Three comment blocks across the two native suites (`native/avr/test_dispatch`
and its siblings) carry the "same statement" wording; plan 05 corrects all three.

---

## 10. The −650 / −714 split — UNVERIFIED

ROADMAP/REQUIREMENTS state the phase's flash saving splits **−650 B** (heap removal) /
**−714 B** (64-bit runtime removal). This decomposition requires the **post-change** body sizes
of `rurp_read_voltage_mv` and `mem_util_blank_check`, which do not exist in isolated,
Phase-155-only form before plans 04/05 land — this before-only plan is prohibited from producing
that build (critical constraint: no source edit). The two function-body deltas below are
therefore the one pair of figures in this record **quoted from `155-RESEARCH.md`'s own
`[VERIFIED: pio run]` measurement** (built by the researcher against a throwaway Phase-155-only
worktree, not the multi-phase `wip/v1.33-size-reduction-survey-preserved` reference, which this
plan confirmed independently is NOT a clean Phase-155-only build — see the note below), rather
than independently re-measured this session:

| Item | Δ (from RESEARCH's post-change build) |
|---|---|
| Heap blob (`malloc` 312 + `free` 274), contiguous, measured this session (§3) | −586 |
| 64-bit runtime blob (11 symbols), contiguous, measured this session (§4) | −528 |
| `rurp_read_voltage_mv` body (RESEARCH-quoted) | −204 |
| `mem_util_blank_check` body (RESEARCH-quoted) | −58 |

Under the natural attribution (each blob plus the function body that pulled it in): heap
`−586 + −58 = −644`; 64-bit runtime `−528 + −204 = −732`. **Neither matches −650 / −714.** The
**total**, `−644 + −732 = −1376` (which reconciles to a measured whole-image delta of −1366 with
+10 B unattributed elsewhere, per RESEARCH's own ledger) **is the reliable figure**; the per-half
split is an artefact of how the original survey attributed shared bytes between the two removals,
and is marked **UNVERIFIED** here. Plan 06 should quote the total, not the split.

**Note on the multi-phase reference branch:** this plan built
`wip/v1.33-size-reduction-survey-preserved` (`a6b46f8`) in an isolated `git worktree` (not
touching the tracked `firestarter` tree) to check whether it could independently supply the
function-body deltas above. It measures `uno` flash at 23088 B against this record's 26026 B
baseline (a −2938 B delta), matching STATE.md's own "−2938 B flash / −13 B RAM ... net −2 lines"
figure for the **combined** Phases 155-158 work — confirming this branch bundles DEDUP/DECODE/LAND
reductions alongside Phase 155's, and so cannot isolate the two Phase-155-only deltas above
without contamination from later phases' changes. It was also confirmed to use the `k > 4000000UL`
guard rather than the resolved `k > 4194303UL` (see the guard-constant note below), consistent
with `155-RESEARCH.md` C-1. The worktree was removed after this check; the tracked `firestarter`
tree was never touched.

**Guard-constant note (was C-1):** `−1364 B` (ROADMAP) and `k <= 4194303` (a locked decision) are
mutually inconsistent per `155-RESEARCH.md` C-1: the `4000000` guard measures −1364, the
`4194303` guard measures −1366. This plan does not re-derive that 2 B figure independently (same
reasoning as above — it requires a post-change build); it is recorded here as context for plan 04,
which ships `4194303UL` and records the 2 B delta.

---

## 11. Baseline staleness — `scripts/baseline/size_baseline.json`

| Target | Baseline `flash_used` | Measured this session (§2) | Δ |
|---|---|---|---|
| `uno` | 25548 | 26026 | **+478** |
| `uno328pb` | 25598 | 26074 | **+476** |
| `leonardo` | 27630 | 28170 | **+540** |

RAM is unchanged against the baseline on all three targets (measured `ram_used` this session —
1575 / 1581 / 2016 — is byte-identical to the baseline's recorded `ram_used`).

Quoted `meta` block admission (`size_baseline.json`, key `native_case_count_revision_260822`):

> "NOTHING ELSE IN THIS FILE MOVED: the avr_targets flash_used/ram_used figures below still
> record the PRE-change position (uno 25548, uno328pb 25598, leonardo 27630) deliberately -- a
> native-only test adds no AVR bytes, and re-recording the AVR figures is the separate act
> whoever lands this branch must adjudicate along with the +478/+476/+540 flash growth."

**Consequence:** after Phase 155's change lands, `check_size_baseline.py` will report `uno` as
roughly `26026 − 1366 − 25548 = −888` B against this stale baseline. That `−888` figure is
correct as an input to the MERGE-05 policy run (which compares against this baseline), and
**wrong** as a statement of "this phase's saving" — this phase's saving is `−1366` B against the
`FW_PRE_SHA` position measured in §2, not against the +478 B-stale baseline. This record — not
`size_baseline.json` — is the before-position for every Phase 155 delta.

No command run by this plan wrote to `scripts/baseline/size_baseline.json`; confirmed via
`git -C firestarter diff --name-only -- scripts/baseline/` (empty).

---

## 12. Test and gate baselines, on the clean committed tree

| Suite | Result | Wall time |
|---|---|---|
| `pio test -e native` | **172 test cases: 172 succeeded**, 17 suites | 5m 36s |
| `pio test -e native_nodevtools` | **172 test cases: 172 succeeded**, 17 suites | 45s |
| `python3 -m pytest tests/ -q` (system python3, not the PlatformIO penv) | **323 passed**, 0 failed | 12.19s |
| `python3 scripts/check_build_warnings.py --log uno=<build log>` | `PASS: uno: macro_redefinition=0 (== 0)`, exit 0 | — |

The two native legs were run **sequentially, never concurrently** — `155-RESEARCH.md`'s D-04
pitfall records that this suite's failures correlate with run duration, not tree content.

Commands:
```bash
pio test -e native
pio test -e native_nodevtools
python3 -m pytest tests/ -q
python3 scripts/check_build_warnings.py --log uno=<uno build log>
```

---

## Summary of what this record proves

- The heap allocator (`malloc`/`free`, 586 B contiguous) has **exactly one caller anywhere in this
  image**: `mem_util_blank_check` — proven by disassembly attribution, not by reading source (§5).
- The full 64-bit runtime is **eleven** symbols totalling **528 B**, of which the requirement text
  names only eight totalling 438 B; the missing three (90 B: `__umulsidi3`, `__umulsidi3_helper`,
  `__ashrdi3`) are proven to exist and to be part of the same contiguous, single-purpose blob (§4).
- Five of those eleven symbols have **exactly one user-code caller**, `rurp_read_voltage_mv`,
  proven the same way (§5).
- The RAM headroom claim in REQUIREMENTS/ROADMAP double-counts 512 B; the corrected, derived
  figures are 473 B (`uno`), 467 B (`uno328pb`), 544 B (`leonardo`), all correctly framed as
  shared heap-and-stack headroom rather than allocator-available RAM (§7).
- The latent unchecked-allocation defect exists exactly as claimed, quoted with today's line
  numbers (§8).
- The "same statement" claim is false; the true, stronger formulation is recorded (§9).
- The −650/−714 split does not reproduce from measured components; the total (−1366, from
  `155-RESEARCH.md`, since this before-only plan cannot itself build the post-change tree) is
  the reliable figure (§10).
- This record — not `scripts/baseline/size_baseline.json` — is the correct before-position for
  every delta Phase 155 computes; the baseline is +478/+476/+540 B stale by its own admission
  (§11).
