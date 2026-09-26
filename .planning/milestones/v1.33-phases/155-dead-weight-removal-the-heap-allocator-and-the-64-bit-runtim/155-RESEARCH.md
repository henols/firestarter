# Phase 155: Dead-Weight Removal — the heap allocator and the 64-bit runtime — Research

**Researched:** 2026-08-23
**Domain:** AVR firmware size reduction (avr-gcc 7.3.0 / avr-libc), integer-arithmetic reformulation, symbol-level image verification
**Confidence:** HIGH — every load-bearing figure in this document was **measured on this tree at `firestarter` `2ad5b32`**, not carried from the ROADMAP. Four ROADMAP/REQUIREMENTS figures are **corrected** below.
**Research method note:** the change was applied in a throwaway `git worktree` (since removed; `git status --porcelain` re-verified empty) and all three AVR targets were built before and after. This document therefore reports *post-change* figures as measured, not as predicted.

---

## Summary

This phase deletes two entire library blobs from the AVR image, each dragged in by exactly one call site. Both claims are now **mechanically confirmed** at the disassembly level, not assumed:

- `malloc` and `free` are called from **`mem_util_blank_check` and nowhere else** in the whole image (verified by parsing `avr-objdump -d` for every `call`/`jmp` reference to either symbol). They occupy a **contiguous 586 B block** at `0x6246–0x6490` on `uno`.
- The 64-bit runtime is called from **`rurp_read_voltage_mv` and nowhere else** — five helpers (`__muldi3`, `__adddi3`, `__lshrdi3`, `__udivdi3`, `__umulsidi3`) are referenced directly from that function, and the remaining six are internal fall-through entry points of the same blob. It is a **contiguous 528 B block** at `0x6036–0x6246`, immediately adjacent to the heap block. Together: **1114 B of library code in one unbroken 0x6036–0x6490 span.**

The measured saving is **−1366 B flash and −8 B RAM, identical on all three AVR targets.** The ROADMAP's `−1364 B` is off by 2 B, and the cause is precisely identifiable (see Correction C-1). The `−8 B RAM` figure is **exactly right** and its ledger reconciles to the byte.

The hard part of this phase is **verification, not implementation**, for two reasons. First, `src/boards/rurp_common.cpp` compiles in **no** native environment (`build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`, `platformio.ini:227`), so the voltage arithmetic has no unit-test path — and every workaround for that (widen `src_filter`, add a suite to `[env:native]`, add a new env) is either impossible or reddens a live gate. Second, the phase's own success criteria contain four measurable errors that must be corrected rather than restated.

**Primary recommendation:** land the change semantically from the preserved reference (do **not** cherry-pick `a6b46f8` — it will not apply), assert DEAD-01/DEAD-03 with `avr-nm` over all **eleven** 64-bit symbols (not the eight the requirement lists) on all three ELFs, and site DEAD-04's oracle as a **pytest file in `firestarter/tests/`** carrying a numerical grid sweep *plus* a comment-stripped source-contract scan of `rurp_common.cpp`, so the Python model cannot drift from the shipped C. That is the only option that lands inside a CI leg without moving the `172/17` native counts a live gate asserts by exact equality.

---

## User Constraints

**There is no CONTEXT.md for this phase.** Per the orchestrator's instruction, the hand-authored ROADMAP Phase 155 entry and REQUIREMENTS DEAD-01…DEAD-06 **are** the locked decisions. Nothing below invents a decision they do not state.

### Locked Decisions (from ROADMAP §v1.33 and REQUIREMENTS §2)

- **D-01 (milestone):** Phase 154 sweeps source and **builds** the remap tool; **Phase 159 applies it once** over the composite diff. Phase 155 therefore runs *after* 154 for source-text-ordering reasons only. **Phase 155 must not run the remap tool and must not repair citations** — but see Finding F-6: it will *create* four newly-stale citations, and that is Phase 159's job to fix, not this phase's.
- **D-02 (milestone):** **No success criterion in this milestone requires a physical board.** Explicitly reaffirmed for DEAD-04 in REQUIREMENTS "Out of Scope": *"neither needs silicon to be correct, and DEAD-04's numerical oracle bounds the voltage change at 5 mV."* **No plan may author a bench criterion.**
- **D-03 (milestone):** MERGE-05 is one-sided (`check_size_baseline.py:697` is `if flash_delta > allowance`), so a shrink passes with **no exemption authored**. The pass must be **recorded as one-sided** so no future reader mistakes green for "nothing moved".
- **D-04 (milestone):** **The native suite is load-flaky.** No plan may attribute a suite failure to its own change on N=1.
- **Firmware-only (REQUIREMENTS "Out of Scope"):** *"Host-side changes in Phases 155–158. Those four phases are firmware-only: no host file moves, no wire change, no `chip_database.json` change, no protocol-parity constant moves."* **Verified compatible** — see Finding F-5: zero host-side test in either repo reads any symbol this phase touches.
- **LAND-01 (Phase 158) owns the cold baseline re-record.** Phase 155 **must not** re-anchor `scripts/baseline/size_baseline.json`.
- **DEAD-06:** this is *"the only requirement in Phases 155–158 that touches a test file"*, and the rejected alternative (retaining a dead `void* progress_data` field for 2 B of RAM) must be **recorded as considered and rejected, with its cost**.

### Claude's Discretion

- The *shape* of the DEAD-04 oracle (file, language, grid step) — the requirement mandates only "a committed oracle over a stated input grid". Recommendation and trade-offs in **Validation Architecture** below.
- The `k` overflow-guard constant. The ROADMAP says `4194303`; the preserved reference uses `4000000`. This is a live 2-byte decision — see Correction C-1.
- Plan/wave decomposition.

### Deferred Ideas (OUT OF SCOPE)

- Anything belonging to Phases 156, 157, 158, 159 — the preserved reference branch is a **composite of all four** phases. Exact per-phase attribution in **Prior Art: Scope Fence** below.
- Re-anchoring `size_baseline.json` (LAND-01 / Phase 158).
- Citation repair (REMAP-* / Phase 159).
- Any bench criterion (D-02).

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **DEAD-01** | No `malloc`/`free`/`realloc`/`calloc`/`__brkval` symbol; `mem_util_blank_check` was the allocator's only caller; saved address moves to a file-scope static. Measured −650 B flash, −8 B RAM. | **Call-graph confirmed** (only caller). Concrete `avr-nm` assertion command given. Symbol sizes measured: `malloc` 312 B, `free` 274 B. The `−650 B` split is **corrected** (C-2); the `−8 B` RAM is **confirmed** with a byte-exact ledger. |
| **DEAD-02** | The unchecked dereference is closed and recorded as a **latent defect**, on a part with ~470 B free RAM given `handle` (1115 B) and jsmn tokens (512 B). | Current code quoted; the unchecked `progress_data->address = handle->address` at `memory.cpp:502` immediately after `malloc` at `:409` is **confirmed**. The RAM arithmetic is **corrected** (C-3): `1115 B` is not `handle`'s size on `uno`. The `~470 B` free-RAM conclusion is **confirmed** (473 B measured). |
| **DEAD-03** | No 64-bit runtime helper — 8 named symbols totalling 438 B; `rurp_read_voltage_mv` alone pulled them in; its body drops 434 → ~232 B. Measured −714 B. | 438 B for those 8 **confirmed exactly**. But the image holds **11** such symbols totalling **528 B** — the list is **undercounted by 90 B** (C-4). Body measured 434 → **230 B**. Sole-caller status confirmed by call graph. |
| **DEAD-04** | Committed oracle over a stated grid: bit-identity at `k=7850`; ≤5 mV over R2 39k–47k × bandgap 200–250 × full ADC; both guards exercised; implausible calibration returns 0. | **Every number independently reproduced.** `k = 7850` exactly; ADC 1023 / bg 225 → **35691 both ways**; worst deviation over the grid **exactly 5 mV**; bit-identity at the shipped calibration is *total* (0 mismatches over bg 1–1023, stronger than claimed). **Neither guard fires anywhere in the grid** — dedicated cases required. Grid runs in **0.44 s**. |
| **DEAD-05** | Coverage ceiling stated, not implied: `rurp_common.cpp` compiles in no native env. | **Confirmed** at `platformio.ini:227` (and identically at `:307` for `native_nodevtools`). Full list of what native *does* compile, plus all four workaround options with evidence for why three are unavailable. |
| **DEAD-06** | Two native suites' `h.progress_data == NULL` assertions updated with their comments plus a third stale comment at `test_val_5v_page.cpp:240`; behaviour stays pinned by `is_operation_in_progress`, set by the **same statement**; rejected alternative recorded with cost. | Assertions quoted at `test_val_5v_page.cpp:351` and `test_eeprom28c_sdp.cpp:1862`. **Proven compiler-forced** (two hard `error:` lines, suites fail to build, 172 → 127 cases). The **"same statement" claim is FALSE** (C-5) — two adjacent statements; the correct, still-sufficient formulation is given. Rejected-alternative cost measured: **2 B RAM**. |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Blank-check cross-call state | AVR firmware — `src/proms/memory.cpp` | — | The state is a single `uint32_t` local to one function's multi-call lifetime; a file-scope static in that TU is the correct owner. It is *not* handle state: nothing outside `mem_util_blank_check` ever read `handle->progress_data` (verified — the only other references in the tree are the two test assertions). |
| VPP/VPE voltage conversion | AVR firmware — `src/boards/rurp_common.cpp` | — | Board-layer ADC arithmetic. Deliberately **not** moved host-side: the milestone forbids host changes, and the host already receives pre-rounded integer/tenths pairs. |
| Voltage-conversion **correctness proof** | Host test tier — `firestarter/tests/*.py` (CI leg 3) | — | The firmware tier cannot host it: the TU compiles in no native env, and adding a native suite moves counts a live gate pins. The arithmetic is pure integer math with no hardware dependency, so a host-tier numerical oracle is a faithful model **provided** it is paired with a source-contract scan binding the model to the shipped C. |
| Image-symbol absence proof | Build/tooling tier — `avr-nm` over the three `.elf` files | — | Symbol absence is a link-time property; only the linked ELF can witness it. No native or host test can. |
| Blank-check behaviour proof | Native test tier — `test_eeprom28c_sdp`, `test_val_5v_page` | — | Already owned there; this phase only narrows the observable set (removes a redundant probe). |

---

## Prior Art: the preserved reference branch, and the scope fence

`wip/v1.33-size-reduction-survey-preserved` @ **`a6b46f8`**, merge-base **`8695ee5`**. `git merge-base 8695ee5 a6b46f8` returns `8695ee5`, so the diff is a clean forward range. STATE.md forbids deleting or force-updating this ref. `[VERIFIED: git]`

### ⚠ It will not apply as a patch

`a6b46f8` forks `8695ee5`. This tree is at **`2ad5b32`** — Phase 154's provenance sweep — which **rewrote comments inside the same hunks**. Confirmed concretely: in `memory.cpp` the `blank_check_progress_data_t` typedef sat at line 386 in the reference and sits at **line 393** here; `mem_util_blank_check` moved to **405**. The reference is a **semantic reference, not a cherry-pick source.** `[VERIFIED: git diff + line inspection]`

### Scope fence — what belongs to 155, and what does not

The reference is a composite of Phases 155–158. Attribution verified against the ROADMAP entries for 156/157/158:

| Reference file | Hunk | Phase | Requirement |
|---|---|---|---|
| `include/firestarter.h` | `uint32_t protocol` → `uint8_t`, `uint32_t ctrl_flags` → `uint16_t` | **157** | DECODE-04 |
| `include/firestarter.h` | delete `void* progress_data;` (`:226` today) | **155** | DEAD-01 |
| `include/memory_utils.h` | declare `mem_util_report_voltage` / `mem_util_report_chip_id` | **156** | DEDUP-01/02 |
| `src/boards/rurp_common.cpp` | all 41 lines | **155** | DEAD-03, DEAD-04 |
| `src/proms/memory.cpp` | `mem_util_report_voltage` + `mem_util_report_chip_id` definitions (+46 lines) | **156** | DEDUP-01/02 |
| `src/proms/memory.cpp` | `blank_check_saved_address` static + rewritten `mem_util_blank_check` head | **155** | DEAD-01, DEAD-02 |
| `src/json_parser.c` (152 lines) | field table, `store_field` saturation | **157** | DECODE-01/02/03/05 |
| `src/proms/eprom.cpp` (56) | VPP + chip-ID report call sites | **156** | DEDUP-01/02 |
| `src/proms/flash_intel.cpp` (56) | VPP + chip-ID report call sites | **156** | DEDUP-01/02 |
| `src/proms/flash_utils.cpp` (16) | chip-ID report call site | **156** | DEDUP-02 |
| `src/proms/eeprom_28c.cpp` (17) | chip-ID report call site | **156** | DEDUP-02 |
| `test/native/avr/test_eeprom28c_sdp/…` (11) | replace the `progress_data` assertion with a comment | **155** | DEAD-06 |
| `test/native/avr/test_val_5v_page/…` (33) | same, ×1 assertion + 2 comment blocks | **155** | DEAD-06 |

**Confirmed as instructed:** `json_parser.c`, `eprom.cpp`, `flash_intel.cpp`, `flash_utils.cpp` and `eeprom_28c.cpp` carry **no Phase 155 content whatsoever**. `include/firestarter.h` and `src/proms/memory.cpp` are **split files** — the planner must import only the rows marked 155.

> **Path note:** the orchestrator's brief listed the test paths as `test/avr/…`. The real paths are **`test/native/avr/…`**; a `git diff` restricted to `test/avr/…` silently returns nothing. `[VERIFIED: git diff --stat]`

### The Phase 155 rows of the reference, quoted

`src/boards/rurp_common.cpp` — replaces `rurp_common.cpp:64-64`:

```c
    uint32_t sum = r1 + r2;
    if (sum > 3900000UL) {
        return 0;
    }
    uint32_t k = (1100UL * sum) / r2;
    if (k > 4000000UL) {          /* ← ROADMAP criterion 4 says 4194303; see C-1 */
        return 0;
    }
    uint32_t bg = (uint32_t)bandgap_adc_reading;
    return (uint16_t)((voltage_adc_reading * k + bg / 2) / bg);
```

`src/proms/memory.cpp` — replaces the typedef at `:393-395` and the head of `mem_util_blank_check` at `:406-422`:

```c
static uint32_t blank_check_saved_address;
...
void mem_util_blank_check(firestarter_handle_t* handle) {
    if (!is_operation_in_progress(handle)) {
        set_operation_in_progress(handle);
        blank_check_saved_address = handle->address;
        handle->address = 0;
    } else {
        if (handle->address >= handle->mem_size) {
            clear_operation_in_progress(handle);
            handle->address = blank_check_saved_address;
            return;
        }
    }
```

`include/firestarter.h` — delete `:226` (`    void* progress_data;`).

The two test-file hunks replace each `TEST_ASSERT_NULL_MESSAGE(h.progress_data, …)` with an explanatory comment block. **Note for DEAD-06:** the reference's own replacement comment says *"is_operation_in_progress above is set by the same statement of the same function that used to do the malloc"* — that phrasing is the source of the ROADMAP's error C-5 and **must not be copied verbatim**.

---

## Measured Figures — before and after, all three targets

Built at `2ad5b32` (before) and with the Phase 155 change applied in a throwaway worktree (after). `k` guard = `4194303UL`. `[VERIFIED: pio run]`

| Target | Flash before | Flash after | Δ flash | RAM before | RAM after | Δ RAM |
|---|---|---|---|---|---|---|
| `uno` | 26026 | 24660 | **−1366** | 1575 | 1567 | **−8** |
| `uno328pb` | 26074 | 24708 | **−1366** | 1581 | 1573 | **−8** |
| `leonardo` | 28170 | 26804 | **−1366** | 2016 | 2008 | **−8** |

Function and object sizes (`avr-nm --print-size`, `uno`; hex sizes converted):

| Symbol | Before | After | Δ |
|---|---|---|---|
| `rurp_read_voltage_mv` | **434 B** (`0x1b2`) | **230 B** (`0xe6`) | −204 |
| `mem_util_blank_check` | **510 B** (`0x1fe`) | **452 B** (`0x1c4`) | −58 |
| `handle` (.bss) | **603 B** (`0x25b`) | **601 B** (`0x259`) | −2 |
| `blank_check_saved_address` (.bss) | — | **4 B** | +4 |
| `parse_json(...)::tokens` (.bss) | 512 B (`0x200`) | 512 B | 0 |

### RAM ledger — reconciles exactly to −8 B

| Item | Section | Δ |
|---|---|---|
| `__brkval` | .bss | −2 |
| `__flp` | .bss | −2 |
| `__malloc_heap_end` | .data | −2 |
| `__malloc_heap_start` | .data | −2 |
| `__malloc_margin` | .data | −2 |
| `handle.progress_data` | .bss (inside `handle`) | −2 |
| `blank_check_saved_address` | .bss | **+4** |
| **Net** | | **−8** ✅ |

The static costs 4 B where the pointer cost 2 B — and still nets −8 because it eliminates five allocator globals. This is the exact argument for the rejected alternative's cost (below).

### Flash ledger — 10 B unattributed, stated rather than fudged

| Item | Δ |
|---|---|
| Heap blob (`malloc` 312 + `free` 274), contiguous `0x6246–0x6490` | −586 |
| 64-bit runtime blob (11 symbols), contiguous `0x6036–0x6246` | −528 |
| `rurp_read_voltage_mv` body | −204 |
| `mem_util_blank_check` body | −58 |
| **Sum of measured components** | **−1376** |
| **Measured whole-image Δ** | **−1366** |
| **Residual (growth elsewhere)** | **+10, unattributed** |

The +10 B is most likely call-site register-allocation and inlining effects at `rurp_common.cpp` / `memory.cpp`. It is recorded as unattributed rather than absorbed into a component. A plan may attribute it with `avr-nm` diffing if desired; it is not required by any criterion.

---

## Corrections to ROADMAP / REQUIREMENTS figures

This project's convention is that corrected figures are recorded publicly. Five corrections, in descending importance.

### C-1 — `−1364 B flash` is off by 2 B, and the cause is the `k` guard constant

Measured **−1366 B** on all three targets with `k > 4194303UL`. Rebuilding the *same* tree with `k > 4000000UL` — the constant the preserved reference actually uses — yields `uno` **24662**, i.e. exactly **−1364**. `[VERIFIED: two builds]`

So the ROADMAP is internally inconsistent: **criterion 4's stated guard (`k <= 4194303`) and criterion/Measured header's `−1364 B` cannot both be true.** `−1364` is the `4000000` figure; `4194303` measures `−1366`.

**Recommendation: keep `4194303` and record `−1366`.** `4194303 = 0x3FFFFF`, so `k > 4194303` is `(k >> 22) != 0` — which is both **2 B cheaper** and a **tighter, better-reasoned bound** than the arbitrary decimal `4000000`. The requirement text already names `4194303`, so this also removes the inconsistency rather than entrenching it. The plan must state the 2 B and its cause.

### C-2 — the `−650 / −714` split does not decompose from measured symbol sizes

Measured: heap blob **586 B**, 64-bit blob **528 B**, `rurp_read_voltage_mv` −204, `mem_util_blank_check` −58. Under the natural attribution (each blob plus the body that pulled it in) the split is **−644 heap / −732 runtime**, not −650 / −714. The **total** is the reliable figure; the split is an artefact of how the survey attributed shared bytes. Mark the per-half figures **UNVERIFIED** and quote the total.

### C-3 — the RAM sentence mixes two targets and double-counts

DEAD-02 / criterion 2 say: *"roughly 470 B of free RAM once `handle` (1115 B) and the jsmn token array (512 B) are accounted for."* Measured:

- `uno` / `uno328pb`: `handle` = **603 B**, `tokens` = **512 B**. `603 + 512 = 1115`. **The `1115 B` figure is `handle` + tokens *together*, not `handle` alone** — so the sentence adds the 512 B twice.
- `leonardo`: `handle` = **1115 B** (`0x45b`) — because `DATA_BUFFER_SIZE` is 1024 there instead of 512. So `1115` is *also* leonardo's handle size, by coincidence.
- Free RAM (from `size_baseline.json`, matching today's builds): `uno` **473 B**, `uno328pb` **467 B**, `leonardo` **544 B**.

**The `~470 B` conclusion is correct and is the `uno`/`uno328pb` figure.** The arithmetic that gets there is not. Correct statement: *on `uno`, `handle` (603 B) and the jsmn token array (512 B) together consume 1115 B of the 2048 B SRAM, leaving 473 B free.* `[VERIFIED: avr-nm, size_baseline.json, pio run]`

### C-4 — the 64-bit symbol list is undercounted by 90 B

The eight symbols the requirement names total **exactly 438 B** — that figure is confirmed. But the image contains **three more** in the same contiguous blob, which the list omits:

| Symbol | Size | Referenced by |
|---|---|---|
| `__umulsidi3` | 2 B | **`rurp_read_voltage_mv` directly** |
| `__umulsidi3_helper` | 84 B | fall-through / `__muldi3_6` |
| `__ashrdi3` | 4 B | fall-through entry point |
| | **90 B** | |

All three disappear with the change (verified: post-change symbol count is **0** across an 11-symbol regex on all three ELFs). The true 64-bit runtime footprint is **528 B**, not 438 B.

**Consequence for DEAD-03's assertion:** an absence check listing only the eight named symbols could pass while leaving 90 B of 64-bit runtime linked, if a future caller pulled `__umulsidi3_helper` alone. **Assert on all eleven**, or on a family regex. The requirement's "438 B" may stand as the named-subset figure provided the 528 B total is recorded alongside it.

### C-5 — "the same statement" is factually wrong

Criterion 6 says the surviving `is_operation_in_progress` assertion is set by *"the same statement"* as `progress_data`. It is not. `memory.cpp:408-411`:

```c
        set_operation_in_progress(handle);                                    // :408
        handle->progress_data = malloc(sizeof(blank_check_progress_data_t));  // :409
        progress_data = (blank_check_progress_data_t*)handle->progress_data;  // :410
        progress_data->address = handle->address;                             // :411
```

`set_operation_in_progress` is `handle->operation_state |= OPERATION_IN_PROGRESS` (`include/operation_utils.h:41-43`) and touches nothing else. These are **two distinct statements**.

**The coverage claim still holds, on a stronger and true formulation:** they are **unconditionally adjacent statements in the same `then`-branch of the same `if`, with no intervening control flow, early return, or condition.** So `is_operation_in_progress == false` strictly implies the branch never executed, which strictly implies the `malloc` never executed. The surviving assertion is therefore exactly as strong a witness for "the blank check did not run" as the deleted one was. The plan should state it this way and record the ROADMAP wording as corrected.

---

## DEAD-01 / DEAD-03: the mechanical symbol-absence check

### Toolchain availability — confirmed

`~/.platformio/packages/toolchain-atmelavr/bin/` ships **`avr-nm`, `avr-objdump`, `avr-size`, `avr-readelf`** (avr-gcc 7.3.0, package `1.70300.191015`). `[VERIFIED: ls]`

**There is no `.map` file.** `platformio.ini` passes no `-Wl,-Map`, and `find .pio/build/uno -name '*.map'` returns nothing. Any symbol assertion must read the **`.elf`**, not a map. `[VERIFIED]`

**No existing test or script parses build output for symbols.** `check_size_baseline.py` and `check_build_warnings.py` parse `pio run` / `pio test` *text logs* (`SIZE_RE` on the `RAM:`/`Flash:` lines, `CASES_RE` on `N test cases:`). Symbol-level assertion is **new capability for this repo** — there is no precedent to follow, and no gate that would collide with one.

> Note: `.planning/todos/prove-pio-dev-flag-fails-closed.md` items 1–3 (which include *"avr-nm symbol capture"*) are filed against backlog 999.15 / gh#8 and were explicitly **not attempted** by Phase 119 (`platformio.ini:281-286`). Phase 155's `avr-nm` work is a narrower, unrelated use and should not be presented as discharging that todo.

### The three AVR targets — confirmed

`platformio.ini:16`: `default_envs = uno, uno328pb, leonardo`. ELF names are `firestarter_<env>.elf` (set by `name_firmware.py`). `[VERIFIED]`

### Concrete commands

```bash
NM="$HOME/.platformio/packages/toolchain-atmelavr/bin/avr-nm"

# DEAD-01 — heap absence. Must print 0 for each env.
for e in uno uno328pb leonardo; do
  ELF=$(ls .pio/build/$e/firestarter_$e.elf)
  echo -n "$e heap: "
  "$NM" "$ELF" | grep -cE ' (T|t|B|b|D|d) (malloc|free|realloc|calloc|__brkval|__flp|__malloc_heap_start|__malloc_heap_end|__malloc_margin)$'
done

# DEAD-03 — 64-bit runtime absence, ALL ELEVEN symbols (see C-4). Must print 0.
for e in uno uno328pb leonardo; do
  ELF=$(ls .pio/build/$e/firestarter_$e.elf)
  echo -n "$e 64bit: "
  "$NM" "$ELF" | grep -cE '__(muldi3|muldi3_6|udivmod64|lshrdi3|udivdi3|udivdi3_umoddi3|umoddi3|adddi3|umulsidi3|umulsidi3_helper|ashrdi3)$'
done
```

`grep -c` with no matches exits 1, so wrap in `|| true` or compare the printed count — **do not** let a non-zero grep exit status be read as the assertion failing when it in fact means the assertion *passed*. This is a real fail-open/fail-closed inversion hazard for this gate.

### Measured before-figures — current symbol presence

**Heap block, `uno`, contiguous `0x6246–0x6490` = 586 B:**

| Symbol | Addr | Size | Section |
|---|---|---|---|
| `malloc` | `0x6246` | **312 B** | .text |
| `free` | `0x637e` | **274 B** | .text |
| `__brkval` | `0x800723` | 2 B | .bss |
| `__flp` | `0x800725` | 2 B | .bss |
| `__malloc_heap_end` | `0x800107` | 2 B | .data |
| `__malloc_heap_start` | `0x800109` | 2 B | .data |
| `__malloc_margin` | `0x80010b` | 2 B | .data |

**64-bit runtime block, `uno`, contiguous `0x6036–0x6246` = 528 B:**

| Symbol | Addr | Size | Direct caller (from `avr-objdump -d`) |
|---|---|---|---|
| `__muldi3` | `0x6036` | 158 B | **`rurp_read_voltage_mv`** |
| `__muldi3_6` | `0x60d4` | 18 B | `__muldi3`, `__umulsidi3_helper` |
| `__umulsidi3` | `0x60e6` | 2 B | **`rurp_read_voltage_mv`** |
| `__umulsidi3_helper` | `0x60e8` | 84 B | fall-through |
| `__umoddi3` | `0x613c` | 4 B | fall-through |
| `__udivdi3` | `0x6140` | 2 B | **`rurp_read_voltage_mv`** |
| `__udivdi3_umoddi3` | `0x6142` | 22 B | `__umoddi3` |
| `__udivmod64` | `0x6158` | 162 B | `__udivdi3_umoddi3` |
| `__ashrdi3` | `0x61fa` | 4 B | fall-through |
| `__lshrdi3` | `0x61fe` | 54 B | **`rurp_read_voltage_mv`** |
| `__adddi3` | `0x6234` | 18 B | **`rurp_read_voltage_mv`** |

**Sole-caller status — mechanically confirmed, not assumed.** A script over `avr-objdump -d .pio/build/uno/firestarter_uno.elf` that attributes every `call`/`jmp` reference to its enclosing function found:

- `malloc` ← `{mem_util_blank_check}` — **exactly one caller**
- `free` ← `{mem_util_blank_check}` — **exactly one caller**
- `__muldi3`, `__adddi3`, `__lshrdi3`, `__udivdi3`, `__umulsidi3` ← `{rurp_read_voltage_mv}` — **exactly one user-code caller each**
- the remaining six are reached only from inside the blob

This is the strongest available evidence for criteria 1 and 3 and should be re-run as a plan verification step. `[VERIFIED: avr-objdump + call-graph attribution script]`

---

## DEAD-04: the voltage reformulation and its oracle

### The current implementation, quoted verbatim

`src/boards/rurp_common.cpp:52-122`:

```c
uint16_t rurp_read_voltage_mv() {
    rurp_configuration_t* rurp_config = rurp_get_config();
    uint32_t r1 = rurp_config->r1;
    uint32_t r2 = rurp_config->r2;

    // Set analog reference to default (VCC) for the measurement
    analogReference(DEFAULT);
    uint32_t voltage_adc_reading = analogRead(PIN_VPP_VOLTAGE_ADC);

    long bandgap_adc_reading = rurp_get_bandgap_adc_reading();
    if (bandgap_adc_reading == 0 || r2 == 0) return 0; // Avoid division by zero

    // For higher precision, we use the raw bandgap ADC reading directly.
    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)
    uint64_t numerator = (uint64_t)voltage_adc_reading * 1100UL * (r1 + r2);
    uint64_t denominator = (uint64_t)bandgap_adc_reading * r2;

    // Add half of the divisor to the numerator to round the result
    return (numerator + (denominator / 2)) / denominator;
}
```

The whole file is wrapped in `#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB) || defined(ARDUINO_AVR_LEONARDO)` (`:12`) — relevant to why option (c) below fails.

### Exact formula the current code computes

With `adc = voltage_adc_reading` (0…1023), `bg = bandgap_adc_reading`, all integer, truncating division, single 64-bit division:

```
V64(adc, bg, r1, r2) = floor( (adc · 1100 · (r1 + r2) + floor(bg · r2 / 2)) / (bg · r2) )
```

### The 32-bit reformulation

Fold the divider into one scale factor **before** dividing:

```
k    = floor( 1100 · (r1 + r2) / r2 )
V32  = floor( (adc · k + floor(bg / 2)) / bg )
```

Two guards keep both products inside `uint32`:
- `1100 · (r1 + r2) ≤ 2³²−1` ⟹ `r1 + r2 ≤ 3904515`. Guard at **3900000** (conservative). `[VERIFIED: arithmetic]`
- `adc · k ≤ 2³²−1` with `adc ≤ 1023` ⟹ `k ≤ 4198404`. Guard at **4194303** = `0x3FFFFF` (conservative, and cheaper to test — see C-1). `[VERIFIED: arithmetic]`

An out-of-range calibration returns **0**, mirroring the existing `r2 == 0` behaviour.

**The single source of deviation** is the truncation in `k`. It is one-directional: `V32 ≤ V64` always. Confirmed over the whole grid — `new` is **never** greater than `old`. So the reformulation can only ever **under**-read, never over-read.

### Where `k = 7850` comes from

`include/rurp_shield.h:49-50`: `#define VALUE_R1 270000`, `#define VALUE_R2 44000` (installed by `rurp_config_utils.cpp:38-39`). Therefore:

```
1100 · (270000 + 44000) = 1100 · 314000 = 345,400,000
345,400,000 / 44,000     = 7850.0        ← EXACT, no truncation
```

Because 44000 divides 345,400,000 exactly, **`k` is lossless at the shipped calibration** — which is why bit-identity there is total rather than approximate. And `345,400,000 < 2³²−1`, so the intermediate fits. `[VERIFIED: computed]`

### Independently reproduced oracle results

| Reading required by DEAD-04 | Result | Status |
|---|---|---|
| `k = 7850` exactly at shipped calibration | `1100·314000/44000 = 7850.0` | ✅ |
| ADC 1023 / bandgap 225 → 35691 mV **both ways** | `V64 = 35691`, `V32 = 35691` | ✅ |
| Bit-identity at shipped calibration over bandgap 200–250 × ADC 0–1023 | **0 mismatches / 52,224 evals** | ✅ |
| *Bonus, stronger than claimed:* bit-identity over bandgap **1–1023** × ADC 0–1023 | **0 mismatches / 1,046,529 evals** | ✅ |
| Worst deviation, R2 39k–47k × bandgap 200–250 × ADC 0–1023 (R2 step 1000) | **exactly 5 mV** (470,016 evals; worst at R2 41000, bg 200, adc 893: 37256 vs 37251) | ✅ |
| Same grid at R2 step 100 (4,230,144 evals) | **still exactly 5 mV** (worst at R2 39100, bg 200, adc 902: 39219 vs 39214) | ✅ |
| Deviation direction | `V32 ≤ V64` universally — under-reads only | ✅ |
| Grid runtime | **0.44 s** for 470,016 evals in plain CPython | ✅ tractable |

`[VERIFIED: independent Python reimplementation of both formulas]`

### ⚠ Neither overflow guard fires anywhere in the nominal grid

With `R1 = 270000` held fixed and `R2 ∈ [39000, 47000]`:
- `r1 + r2 ∈ [309000, 317000]` — two orders of magnitude below the 3,900,000 guard.
- `k ∈ [7419, 8715]` (max at `R2 = 39000`, min at `R2 = 47000`) — three orders of magnitude below the 4,194,303 guard.

So **criterion 4's "both uint32 overflow guards are exercised" cannot be discharged by the grid.** It needs **four dedicated cases** outside the grid:

1. `r1 + r2 = 3900000` → **must not** return 0 (boundary, guard does not fire)
2. `r1 + r2 = 3900001` → **must** return 0 (guard fires)
3. a calibration giving `k = 4194303` → **must not** return 0
4. a calibration giving `k = 4194304` → **must** return 0

Plus the pre-existing sentinel: `r2 == 0` → 0, and `bandgap == 0` → 0 (both must be preserved unchanged — they sit *above* the new guards at `:62`).

For case 3/4: `k = floor(1100·(r1+r2)/r2)`, so `r2` small relative to `r1+r2` drives `k` up. E.g. `r1 = 3899900, r2 = 100` → `k = floor(1100·3900000/100) = 42,900,000` (guard fires); tuning `r2` upward walks `k` down through the boundary. The plan should compute the exact pair rather than search at runtime.

### What consumes the value — and the tolerance is **not** ±5 %

Three call sites: `src/proms/eprom.cpp:711` (`eprom_check_vpp`), `src/proms/flash_intel.cpp:37` (`flash_intel_check_vpp`), `src/hardware_operations.cpp:70` (the `CMD_READ_VPP` / `CMD_READ_VPE` reporting path — **no** validation window, it just reports integer/tenths).

Both validation windows are **byte-identical and asymmetric** — `eprom.cpp:713,718` and `flash_intel.cpp:39,44`:

```c
    if (vpp_mv > (uint32_t)handle->vpp_mv + 500) {          /* HIGH: +500 mV ABSOLUTE */
        ... FLAG_FORCE ? MSG_WARN_VPP_HIGH : MSG_ERR_VPP_HIGH
    } else if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100) { /* LOW: −5 % relative */
        ... MSG_WARN_VPP_LOW
    }
```

> **Correction (part of C-series, evidence-level):** the ROADMAP/REQUIREMENTS phrase *"±5 % VPP validation windows (±600 mV at 12 V)"* is **half wrong**. The **low** edge is `−5 %`, which is `−600 mV` at 12 V ✅. The **high** edge is a **fixed `+500 mV` absolute**, not `+5 %` / `+600 mV`. `[VERIFIED: source]`

**The correct framing for the 5 mV bound is therefore:**
- vs. the tighter (high) edge: **5 mV of 500 mV = 1.0 %** of the window.
- vs. the low edge: **5 mV of 600 mV = 0.83 %** of the window.
- Because the reformulation only ever **under**-reads, it can never manufacture a spurious `VPP_HIGH` **error** — the safety-relevant direction. Its only possible behavioural effect is a spurious `MSG_WARN_VPP_LOW` **warning** for a true voltage within 5 mV of the −5 % edge, i.e. within 0.83 % of a boundary that is itself a warning, not an error. **State this asymmetry** — it is a stronger safety argument than a symmetric ±600 mV claim, and it is true.

---

## DEAD-05: the coverage ceiling, and every option for the oracle

### The ceiling, confirmed

`platformio.ini:227` (`[env:native]`) and `:307` (`[env:native_nodevtools]`), byte-identical and required by the file's own comment to stay in lockstep:

```ini
build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>
```

**What native compiles:** every `src/proms/*.cpp`, plus `src/boards/rurp_serial_utils.cpp`, `src/json_parser.c`, `src/operation_utils.cpp`. **Nothing else.** So `src/boards/rurp_common.cpp` — and with it `rurp_read_voltage_mv`, `rurp_read_vcc_mv`, `rurp_get_bandgap_adc_reading` — compiles in **no** native environment. All six native envs (`native`, `native_nodevtools`, `native_pinmap_provisional`, `native_trace_v131`, `native_params_v131`, `native_loop_v131`) carry the **same** `build_src_filter`. `[VERIFIED: platformio.ini]`

Instead, `rurp_read_voltage_mv` is **stubbed** in eight native locations — `test/native/avr/_shared/host_stubs_common.inc:275` (default, returns 0) and per-suite overrides in `test_flash_intel_vpp`, `test_val_flash_intel`, `test_vpp_eprom_v131`, `test_data_input`. So every native suite that touches VPP validation is testing *the consumer against a mock*, never this arithmetic. **The criterion is exactly right: there is no native coverage of this function today and this phase does not create any.**

### The four options, with evidence

| # | Option | Verdict | Evidence |
|---|---|---|---|
| **a** | **pytest file in `firestarter/tests/`** — numerical grid sweep + comment-stripped source-contract scan of `rurp_common.cpp` | ✅ **RECOMMENDED** | Runs in **CI leg 3** (`.github/workflows/build.yml:161`, `beta-build.yml:134`: `pytest tests/ -v`). Adds zero AVR bytes, zero native cases, touches no gated count. Grid runs in 0.44 s. The repo already has 8+ precedents for comment-stripped firmware-source scanning from a pytest file (`test_write_path_source_contract_v131.py`, `test_progress_emission_is_leonardo_only.py`, `test_hv_routing_source_contract_v142.py`, `test_check_is_memory_cmd_no_ifdef.py` in the app repo). |
| **b** | Widen `build_src_filter` to include `boards/rurp_common.cpp` | ❌ **Do not** | The TU `#include <Arduino.h>` and its body writes `ADMUX`, `ADCSRA`, uses `_BV(REFS0)`, `bit_is_set`, and is gated on `ARDUINO_AVR_*` (`:8-12, 24-30`) with an `#error "Unsupported board"` fall-through. On native none of it compiles; forcing a board macro drags in AVR register headers. **And** widening the filter would have to be mirrored into `native_nodevtools` (the file mandates lockstep) and would change the compiled TU set for all 17 suites. |
| **c** | Native test that `#include`s the `.cpp` behind a macro | ❌ **Do not** | Same `#if defined(ARDUINO_AVR_…)` wrapper problem as (b), plus it would need `PIN_VPP_VOLTAGE_ADC`, `analogRead`, `analogReference`, `rurp_get_config` — i.e. an ArduinoFake harness for hardware this arithmetic does not depend on. High cost, and the AVR-register mocking becomes the thing under test. |
| **d** | New native `[env:…]` for a voltage suite | ❌ **Do not** | `platformio.ini` establishes this four times (`:281-286`, `:449-462`, `:509-520`, `:560-570`): a new env has **NO CI COVERAGE** — *"neither build.yml nor beta-build.yml runs any `pio test` env beyond native and native_nodevtools"* — and its name **must never** be fed to `check_size_baseline.py`, which hardcodes `NATIVE_ENVS = ("native", "native_nodevtools")` (`:146`) and raises an **uncaught KeyError → exit 1** on an unknown env (finding F-138-05). It would also still need option (b)/(c) to compile the TU. |

### ⚠ Why a suite cannot simply be added to `[env:native]`

`check_size_baseline.py`'s `compare_native` asserts `cases`, `suites` **and** `all_passed` against `size_baseline.json`, which records `native: {cases: 172, suites: 17}` and `native_nodevtools: {cases: 172, suites: 17}`. `platformio.ini` states the constraint four separate times as a **HARD CONSTRAINT**: adding a case to either env turns a live gate RED. Since **LAND-01 / Phase 158 owns the baseline re-record**, Phase 155 must not move those counts. Option (a) is the only one that respects this. `[VERIFIED: check_size_baseline.py:146,730-740; size_baseline.json; platformio.ini]`

### Keeping criterion 5 honest

Option (a) is a **host-tier numerical model plus a source-text contract**, and every artefact must say exactly that. Concretely, no plan artefact may write "tested", "covered by native", or "verified on hardware" about this arithmetic. The honest wording is:

> `rurp_read_voltage_mv` compiles in no native environment. Its arithmetic is proven by a host-side numerical oracle over a stated grid, bound to the shipped C by a comment-stripped source-contract scan. It has **no native unit-test coverage and no bench coverage**, and this phase creates neither.

**The source-contract half is not optional.** Without it, the oracle proves a Python function equals another Python function — the shipped C could drift silently. With it, a change to `rurp_common.cpp`'s formula that does not match the model's transcription fails CI leg 3. This is the same construction the repo already uses for eight other firmware-source claims.

---

## DEAD-06: the two test suites

### It is compiler-forced, not a judgement call

Building `pio test -e native` with `progress_data` removed but the tests untouched produces exactly two hard errors and **both suites fail to build**:

```
test/native/avr/test_val_5v_page/test_val_5v_page.cpp:351:32: error: ‘firestarter_handle_t’
    {aka ‘struct firestarter_handle’} has no member named ‘progress_data’
  339 |     TEST_ASSERT_NULL_MESSAGE(h.progress_data,

test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1862:32: error: ‘firestarter_handle_t’
    {aka ‘struct firestarter_handle’} has no member named ‘progress_data’
 1788 |     TEST_ASSERT_NULL_MESSAGE(h.progress_data,
```

Result: `172 test cases` → **`127 test cases: 125 succeeded`** — the two suites drop out entirely (45 cases lost), plus 2 build failures. `[VERIFIED: pio test in worktree]`

**Planning consequence:** the test edit **cannot be forgotten and cannot silently pass**. This removes the usual "did the assertion go vacuous?" risk for DEAD-06 — but it also means the test edit and the header edit **must land in the same commit**, or any intermediate commit leaves both native CI legs red. The plan should make this a same-task, same-commit constraint, not two tasks.

### The exact current assertions

`test/native/avr/test_val_5v_page/test_val_5v_page.cpp:351-339`:
```c
    TEST_ASSERT_NULL_MESSAGE(h.progress_data,
        "ERASE-02: h.progress_data must be NULL -- a non-NULL value means "
        "mem_util_blank_check allocated a blank_check_progress_data_t block, "
        "i.e. the pre-write blank check still ran");
```
Surviving sibling at `:333-338` — `TEST_ASSERT_FALSE_MESSAGE(is_operation_in_progress(&h), …)`. Also surviving at `:343` (`TEST_ASSERT_NOT_EQUAL` on `RESPONSE_CODE_ERROR`) and `:346` (`assert_no_vpp_in_recording`).

`test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:1862-1850`:
```c
    TEST_ASSERT_NULL_MESSAGE(h.progress_data,
        "Case 30 (ERASE-01): h.progress_data must be NULL -- a non-NULL value means "
        "mem_util_blank_check allocated a blank_check_progress_data_t block, i.e. the "
        "pre-write blank check still ran");
```
Surviving siblings at `:1783-1787` (`TEST_ASSERT_FALSE_MESSAGE(is_operation_in_progress(&h), …)`) and `:1792` (`sdp_assert_stream_equals` against `SDP_FIXED_DIP28_28C256`).

### The comments requiring update — there are FOUR, not three

The ROADMAP names two assertion comments plus "a third stale comment at `test_val_5v_page.cpp:240`". Measured, there are **four** comment sites in these two files that reference the removed machinery or carry a **stale `memory.cpp:NNN` pin**:

| # | Site | Text | Problem |
|---|---|---|---|
| 1 | `test_val_5v_page.cpp:240-236` | *"BLANK_CHECK_CHUNK_SIZE (**memory.cpp:489**) -- because mem_util_blank_check sets is_operation_in_progress and **mallocs progress_data** on its FIRST call"* | Describes the malloc **and** the pin is **already stale**: `BLANK_CHECK_CHUNK_SIZE` is at **`memory.cpp:490`** today (line 393 is now the `typedef` this phase deletes). This is the ROADMAP's "line 238" comment — the block spans 237-240. |
| 2 | `test_val_5v_page.cpp:316-318` | *"must leave is_operation_in_progress FALSE and **progress_data NULL**. mem_util_blank_check is the ONLY setter of either observable on this path (**memory.cpp:494-498**)"* | Describes the removed observable **and** the pin is **already stale**: `mem_util_blank_check` spans **`memory.cpp:498-548`**; lines 401-405 are the tail of `uint32_to_bytes` plus the function's opening brace. |
| 3 | `test_val_5v_page.cpp:351-339` | the assertion's own message | Assertion deleted with it. |
| 4 | `test_eeprom28c_sdp.cpp:1833-1839` | *"no blank-check **progress allocation**… `mem_util_blank_check` is the ONLY setter of is_operation_in_progress on this path (**memory.cpp:494-512**)"* | Describes the allocation **and** the pin is **already stale** (same reason as #2). |
| 5 | `test_eeprom28c_sdp.cpp:1862-1850` | the assertion's own message | Assertion deleted with it. |

**Also already stale, and NOT in this phase's scope:** `test_eeprom28c_sdp.cpp:97` cites *"`mem_util_set_address(handle, 0)`, **memory.cpp:68**"* — the call is at `memory.cpp:97` and the function at `memory.cpp:327`. Line 68 is unrelated comment text. This one does not mention `progress_data` and is a **pre-existing Phase-154 casualty for Phase 159**, not a Phase 155 obligation. Recorded so the planner does not either miss it or over-scope it.

**Guidance:** the plan should either (a) update the four in-scope pins to correct post-change line numbers, or (b) **delete the line numbers and name the symbol instead** — which is strictly more robust given Phases 156/157/158 will move `memory.cpp` again, and Phase 159 remaps the composite diff. Option (b) is recommended and consistent with Phase 154's own reflow-vs-delete precedent (10.7:1 reflow-to-delete ratio, 117/143 files pure 1-for-1). This is a mechanical grey area with a settled precedent — decide it, do not ask.

### The rejected alternative and its measured cost

**Alternative:** keep `void* progress_data;` in `firestarter_handle_t` as a dead field, permanently `NULL`, purely so the two assertions compile unchanged.

**Cost, measured:** `handle` is 603 B on `uno`/`uno328pb` and 1115 B on `leonardo`; removing the field takes it to 601 B / 1113 B. So the field costs **2 B of RAM on every target, forever** — and on `uno` that is 2 B of the **473 B** that remain free. Flash cost is ~0.

**Why rejected:** the field would be a permanently-`NULL` member of the firmware's single largest object, retained solely to keep two assertions compiling — and those assertions would then be **vacuous**: they would assert `NULL == NULL` on a field nothing writes, which is precisely this project's own documented "hollow gate" failure mode (`tests/test_check_size_baseline.py:13` cites the v1.12 hollow-GATE-03 precedent by name). The surviving `is_operation_in_progress` assertion is set in the same unconditional branch (see C-5) and is a **strictly non-weaker** witness. Record this as considered and rejected, with the 2 B.

---

## DEAD-02: the latent defect

`src/proms/memory.cpp:498-509` today:

```c
void mem_util_blank_check(firestarter_handle_t* handle) {
    blank_check_progress_data_t* progress_data;                                  // 406
    if (!is_operation_in_progress(handle)) {                                     // 407
        set_operation_in_progress(handle);                                       // 408
        handle->progress_data = malloc(sizeof(blank_check_progress_data_t));     // 409  <-- 4-byte alloc
        progress_data = (blank_check_progress_data_t*)handle->progress_data;     // 410
        progress_data->address = handle->address;                                // 411  <-- UNCHECKED DEREF
        handle->address = 0;                                                     // 412
    } else {
        progress_data = (blank_check_progress_data_t*)handle->progress_data;     // 414
        if (handle->address >= handle->mem_size) {                               // 415
            clear_operation_in_progress(handle);                                 // 416
            handle->address = progress_data->address;                            // 417
            free(handle->progress_data);                                         // 418
            handle->progress_data = NULL;                                        // 419
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

**The defect is confirmed exactly as claimed.** `:409` calls `malloc`, `:411` writes through the result with **no NULL test** and no intervening check. `sizeof(blank_check_progress_data_t)` is **4 bytes** — one `uint32_t` — so a 586 B allocator was linked, and a null-deref hazard accepted, to hold four bytes across two calls of one function.

**RAM headroom at the moment of that `malloc`, measured** (see also C-3):

| Target | SRAM | `handle` | jsmn `tokens` | `ram_used` (all statics) | free |
|---|---|---|---|---|---|
| `uno` | 2048 | **603 B** | 512 B | 1575 | **473 B** |
| `uno328pb` | 2048 | **603 B** | 512 B | 1581 | **467 B** |
| `leonardo` | 2560 | **1115 B** | 512 B | 2016 | **544 B** |

`NUMBER_JSNM_TOKENS` is 64 (`include/json_parser.h:17`) × 8 B per `jsmntok_t` = the measured 512 B `parse_json(firestarter_handle*)::tokens`. `handle` is a file-scope global (`src/firestarter.cpp:33`). `[VERIFIED: avr-nm]`

**Framing for the phase record:** the 473 B is not the AVR *stack* headroom — `ram_used` counts `.data`+`.bss` only, and the stack grows down into that 473 B during every operation. So the true margin at the `malloc` call site is **less than 473 B**, and the plan should say "less than 473 B of combined heap-and-stack headroom" rather than implying 473 B were available to the allocator. The defect classification is unaffected and arguably strengthened.

**Record as a latent defect closed, not incidental cleanup** (DEAD-02's explicit demand). Suggested wording basis: an unchecked-allocation dereference on a part with under 473 B of shared heap/stack headroom, present since the blank-check feature landed, closed by removing the allocation entirely rather than by adding a NULL test — because the allocation had no reason to exist.

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md`:
- Meta-repo tracks only `.planning/` and `.claude/`. Firmware is a **separate git repo** at `/workspaces/firestarter`; host CLI at `/workspaces/firestarter_app`. Both sub-repos are on branch `gsd/v1.33-source-hygiene-firmware-size-reduction`; both have local, unpushed commits (`firestarter` `2ad5b32`, `firestarter_app` `38f0d83`). **Executors commit INSIDE the firmware repo.**
- *"**Serial protocol changes** must be kept in sync between `firestarter_app/firestarter/serial_comm.py` and `firestarter/src/firestarter.cpp`."* — **N/A**: this phase changes no wire byte. `mem_util_blank_check`'s emitted `MSG_DATA_PROGRESS` payload and `MSG_ERR_NOT_BLANK` 4-byte payload are untouched.
- *"**Constants/flag bits** are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h`. Change both together."* — **N/A**: the only `firestarter.h` edit is deleting a struct *member*, not a constant or flag bit. `progress_data` appears in no host file. Verified by grep across `firestarter_app/{tests,firestarter,tools}`: **zero hits**.
- *"**Board differences**: Uno has a 512-byte data buffer; Leonardo has 1024."* — **directly relevant**: it is why `handle` is 603 B on Uno and 1115 B on Leonardo, and the source of correction C-3.

From `/workspaces/firestarter/CLAUDE.md`:
- Dispatch order in `memory.cpp:configure_memory` is *"source-of-truth — must match `firestarter/src/proms/memory.cpp` line-for-line"*. This phase edits `memory.cpp` but **only below** `configure_memory`; no dispatch arm moves. **No `CLAUDE.md` table update is required.** The plan should verify this rather than assume it.
- Build commands: `pio run -e uno` / `-e leonardo`; `pio test -e native`.

### `include/messages.h` — do not touch

`messages.h` is **codegen-generated and ID-only** from the meta-repo's `messages.toml`. **This phase needs no new message ID:** it adds no emit, removes no emit, and changes no payload. Confirmed by inspection — the four `LOG_*` sites inside `mem_util_blank_check` (`MSG_ERR_NOT_BLANK`, `MSG_DATA_PROGRESS`) are outside every edited hunk, and `rurp_read_voltage_mv` emits nothing. `[VERIFIED]`

### Project skills

`/workspaces/.claude/skills/` holds `devtest-rootcause`, `devtest-triage`, `find-skills`, `skill-creator`. **None applies** — this is not a chip-validation or datasheet task. `/workspaces/firestarter/.claude/skills` does not exist.

---

## Standard Stack

No new dependency. Everything needed is already installed.

### Core

| Tool | Version | Purpose | Why standard |
|---|---|---|---|
| PlatformIO Core | **6.1.19** | build/test driver | already the repo's only build entry point |
| `platform-atmelavr` | **5.2.0** | AVR platform | pinned in `size_baseline.json` meta |
| `toolchain-atmelavr` (avr-gcc) | **1.70300.191015 / 7.3.0** | compiler + binutils | ships `avr-nm`, `avr-objdump`, `avr-size` |
| `framework-arduino-avr` | 5.3.0 | Arduino core | as-built |
| Unity | via `test_framework = unity` | native suites | existing |
| ArduinoFake | `fabiobatsilva/ArduinoFake@^0.4.0` | native mocks | existing |
| pytest | (CI: `pip install pytest`) | CI leg 3, and DEAD-04's oracle host | existing; **`pytest tests/ -v`** at `build.yml:161` |
| CPython | 3.x, stdlib only | the oracle's arithmetic | grid runs in 0.44 s with no third-party library |

### Supporting

| Tool | Purpose | When to use |
|---|---|---|
| `avr-nm --print-size --size-sort -C` | symbol presence + sizes | DEAD-01, DEAD-03 assertions and before/after figures |
| `avr-objdump -d` | call-graph attribution | proving sole-caller status |
| `scripts/check_size_baseline.py` | MERGE-05 policy run | D-03's one-sided pass; **local-run only, no CI** |
| `scripts/check_build_warnings.py` | warnings baseline | regression guard on the edited TUs |

### Alternatives considered

| Instead of | Could use | Trade-off |
|---|---|---|
| `avr-nm` on the ELF | a linker `.map` (`-Wl,-Map`) | No `.map` is produced today and adding one means editing `platformio.ini` build flags on all three envs — needless churn in a milestone whose premise is byte-level attribution. `avr-nm` needs no build change. |
| pytest oracle | native Unity oracle | See DEAD-05 options table: impossible without widening `src_filter` or moving gated counts. |
| pure-Python model | model + source-contract scan | Model alone can silently drift from the shipped C. **Use both.** |
| `k <= 4000000` | `k <= 4194303` | `4194303` is 2 B cheaper (power-of-two boundary → shift test) and a tighter bound. Recommended; see C-1. |

**Installation:** none. No `npm`/`pip`/`cargo` package is added by this phase.

---

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.**

The change is confined to three existing firmware source files plus two existing test files plus (recommended) one new stdlib-only pytest file. No `platformio.ini` `lib_deps` entry is added, no `requirements.txt` / `pyproject.toml` is touched, no npm/PyPI/crates dependency is introduced. `[VERIFIED: the measured worktree change touched only src/, include/, test/]`

**Packages removed due to `[SLOP]` verdict:** none — none proposed.
**Packages flagged as suspicious `[SUS]`:** none — none proposed.

---

## Architecture Patterns

### System architecture — how a VPP reading and a blank check flow today

```
                    ┌──────────────────────── HOST (firestarter_app, UNCHANGED) ─────┐
                    │  JSON command  ──►  serial @250000  ──►                        │
                    └───────────────────────────────────────────────────────────────┬─┘
                                                                                   │
  ┌────────────────────────────────────────────────────────────────────────────────▼──────┐
  │ FIRMWARE                                                                              │
  │                                                                                       │
  │  json_parser.c ──► handle (603 B .bss on uno / 1115 B on leonardo)                     │
  │        │                     ▲                                                        │
  │        │        tokens 512 B ─┘ (jsmn, 64 × 8 B)                                       │
  │        ▼                                                                              │
  │  configure_memory (memory.cpp) ──► protocol dispatch ──► per-family handler            │
  │                                                            │                          │
  │        ┌───────────────────────────────────────────────────┴──────────┐               │
  │        ▼                                                              ▼               │
  │  ═══ PATH A: blank check ══════════════            ═══ PATH B: VPP validation ════    │
  │  mem_util_blank_check (memory.cpp:498)             eprom_check_vpp (eprom.cpp:695)     │
  │        │                                           flash_intel_check_vpp (:26)        │
  │  first call?                                              │                           │
  │   ├─yes─► set_operation_in_progress          set_control_register(hv_route_mask)      │
  │   │       ██ malloc(4) ──────────► [heap 586 B: malloc 312 + free 274]                │
  │   │       ██ deref UNCHECKED                       delay(100)                          │
  │   │       address = 0                                     │                            │
  │   └─no──► address >= mem_size?                            ▼                            │
  │             └─yes─► restore addr; ██ free()      rurp_read_voltage_mv                  │
  │                     ██ progress_data = NULL      (rurp_common.cpp:52, 434 B)           │
  │        │                                                  │                            │
  │        ▼                                          ██ uint64 mul + uint64 div           │
  │  scan 2048-byte chunk; on !=0xFF:                         │                            │
  │    cmd==CMD_BLANK_CHECK ? stash in data_buffer      ┌──────▼──────────────────────┐    │
  │                         : LOG_ERROR(MSG_ERR_NOT_BLANK)│ 64-bit runtime blob 528 B │    │
  │    else LOG_DATA(MSG_DATA_PROGRESS, addr, mem_size)   │ __muldi3 __udivmod64 ...  │    │
  │                                                      └──────┬──────────────────────┘    │
  │                                                             ▼                          │
  │                                        vpp_mv > target+500 ?  ──► ERR/WARN_VPP_HIGH    │
  │                                        vpp_mv < target*95/100? ──► WARN_VPP_LOW        │
  │                                        (asymmetric window — NOT ±5 %)                  │
  └───────────────────────────────────────────────────────────────────────────────────────┘

  ██ = deleted or replaced by this phase.  The two library blobs are CONTIGUOUS
       at 0x6036–0x6490 on uno: 64-bit runtime immediately followed by the heap.
```

### Pattern 1 — cross-call state as a file-scope static in the owning TU

**What:** replace a heap block whose lifetime is exactly one command with a `static` in the TU that owns the state.
**When:** the firmware runs strictly one command at a time (single-threaded, no reentrancy, no nesting), and no other TU reads the state.
**Verified preconditions in this tree:** `handle` is a single global (`firestarter.cpp:33`); nothing outside `mem_util_blank_check` ever read `handle->progress_data` (the only other tree references are the two test assertions).
**Cost:** the static is 4 B of permanent `.bss` where the pointer was 2 B — but it still nets −8 B RAM because it retires five allocator globals (see the RAM ledger).

```c
/* Source: preserved reference a6b46f8, src/proms/memory.cpp */
static uint32_t blank_check_saved_address;

void mem_util_blank_check(firestarter_handle_t* handle) {
    if (!is_operation_in_progress(handle)) {
        set_operation_in_progress(handle);
        blank_check_saved_address = handle->address;
        handle->address = 0;
    } else {
        if (handle->address >= handle->mem_size) {
            clear_operation_in_progress(handle);
            handle->address = blank_check_saved_address;
            return;
        }
    }
    /* ... unchanged ... */
```

### Pattern 2 — fold the constant divider before dividing, to stay in 32 bits

**What:** `(a·b·c)/(d·e)` where `b`, `c`, `e` are calibration constants → precompute `k = b·c/e` once, then `(a·k)/d`.
**When:** on an 8-bit MCU where a single `uint64_t` expression links 500+ B of runtime helpers, and the folded constant divides exactly (or near-exactly) at the shipped calibration.
**Requires:** an explicit guard per intermediate product, and a bound on the truncation error stated against the consumer's tolerance.

```c
/* Source: preserved reference a6b46f8, with the ROADMAP's 4194303 guard (C-1) */
uint32_t sum = r1 + r2;
if (sum > 3900000UL) return 0;          /* 1100*(r1+r2) must fit uint32: <= 3904515 */
uint32_t k = (1100UL * sum) / r2;       /* = 7850 EXACTLY at VALUE_R1/VALUE_R2      */
if (k > 4194303UL) return 0;            /* adc*k must fit uint32: k <= 4198404      */
uint32_t bg = (uint32_t)bandgap_adc_reading;
return (uint16_t)((voltage_adc_reading * k + bg / 2) / bg);
```

### Pattern 3 — the source-contract scan (this repo's established idiom)

**What:** a pytest test that reads a firmware source file, strips comments **preserving line shape**, and asserts a regex/structural property of the code.
**Why it matters here:** it is the only mechanism that binds a host-side numerical model to the shipped C when the C compiles in no test environment.
**Precedents to copy:** `tests/test_write_path_source_contract_v131.py` (its `_strip_comments` at `:223-225` replaces each stripped span with whitespace *of the same shape*, so line numbers survive), `tests/test_hv_routing_source_contract_v142.py`, `tests/test_progress_emission_is_leonardo_only.py`, `tests/test_ack_layout_source_contract_v143.py`.

### Anti-patterns to avoid

- **Adding a native suite to `[env:native]` or `[env:native_nodevtools]`.** Moves `cases`/`suites`, which `check_size_baseline.py:compare_native` asserts by exact equality; `platformio.ini` calls this a HARD CONSTRAINT four times. LAND-01 owns the re-anchor.
- **Re-anchoring `size_baseline.json`.** Phase 158's job. Re-anchoring is documented to strand fixture legs across `tests/test_check_size_baseline.py` unless the fixtures are **severed onto a new family** — that file's docstring records this happening at least four times (Phase 123/124/149, the `_fullflash` and `_v132` families).
- **Cherry-picking `a6b46f8`.** Will not apply; Phase 154 rewrote comments in the same hunks.
- **Importing 156/157/158 hunks from the reference.** Destroys the milestone's per-phase attribution, which is D-01's whole point and the reason 155 is sequenced after 154 at all.
- **Retaining a dead `void* progress_data` field.** Creates a vacuous `NULL == NULL` assertion — this repo's own named "hollow gate" failure mode.
- **`grep -c` as a bare boolean.** Zero matches exits 1. A gate written as `grep -cE '…' && fail` inverts. Compare the printed count.
- **Running `pytest tests/` before committing.** `tests/test_flash_path_record_sync.py:1247` asserts whole-repo porcelain.
- **Claiming timing or bench coverage of the new arithmetic.** Native trace stubs record **no** time (`delay()` unstubbed) and this TU is not compiled natively at all. D-02 forbids a bench criterion.
- **Attributing a native suite failure to this change on N=1.** D-04: the native suite is load-flaky.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Prove a symbol is absent from the image | a source-text grep for `malloc(` | `avr-nm` over the `.elf` | A source grep cannot see the linker. It would pass while `malloc` was pulled in by any other TU — and would also fail-open on an inlined or renamed call. |
| Prove sole-caller status | reading the source and reasoning | `avr-objdump -d` + call-attribution | Reasoning missed 3 of the 11 64-bit symbols (C-4). The disassembly did not. |
| Compare two integer formulas | eyeballing / a comment claiming equivalence | exhaustive grid sweep in Python | 470,016 evaluations in **0.44 s**. There is no reason to sample or argue. |
| Parse `pio run` size output | a new parser | `scripts/check_size_baseline.py`'s `SIZE_RE` / `CASES_RE` | Already exists, already tested by `tests/test_check_size_baseline.py` with planted negative fixtures. |
| Strip C comments for a source scan | a naive regex | copy `_strip_comments` from `tests/test_write_path_source_contract_v131.py:223` | It preserves line shape, so reported line numbers stay meaningful — a property a naive strip silently loses. |
| Keep a Python model honest against C | a comment saying "keep in sync" | a source-contract scan (Pattern 3) | Eight existing tests in this repo do exactly this. A comment is not a gate. |

**Key insight:** every DEAD requirement in this phase is a **link-time or numeric** property, and both classes have exact mechanical oracles already available in the installed toolchain. The temptation in a size-reduction phase is to assert on source text, which fails open on precisely the transformations (inlining, renaming, alternate call sites) that size reduction performs.

---

## Common Pitfalls

### Pitfall 1 — the size baseline is already stale by +478 B, so "delta vs baseline" is not "delta from this phase"

**What goes wrong:** a plan quotes `check_size_baseline.py`'s reported delta as Phase 155's saving.
**Why:** `size_baseline.json` records `uno flash_used 25548`, but the tree at `2ad5b32` builds **26026** — `+478 B` stale. The file's own `meta` block says so explicitly: *"the avr_targets flash_used/ram_used figures below still record the PRE-change position (uno 25548, uno328pb 25598, leonardo 27630) **deliberately**"*, referring to the w27c512-write-slow debug session's **+478/+476/+540** growth that was never re-recorded.
**How to avoid:** measure Phase 155's delta as **`before-this-phase` minus `after-this-phase` on the same tree** (26026 → 24660). Post-change, `check_size_baseline.py` will report `uno` as `−888` vs baseline; that number is **correct for MERGE-05 and wrong as this phase's saving**. Both must appear, labelled.
**Warning sign:** any figure between −880 and −890 being called "the phase's saving".

### Pitfall 2 — `flash_total` and `ram_total` **are** asserted for exact equality

**What goes wrong:** assuming `check_size_baseline.py` is one-sided about everything.
**Why:** it is one-sided only about `flash_used` (`:697` `flash_delta > allowance`) and `ram_used` (`:709`). `flash_total` (`:717`) and `ram_total` (`:722`) are **exact-equality** checks — *"(board or framework moved)"*.
**How to avoid:** confirm the phase does not touch `platformio.ini`'s `board_upload.maximum_size` or `zero_bootloader_reserve.py`. **Verified: it does not** — measured `flash_total` is 32768 on all three targets before and after, and `ram_total` 2048/2048/2560 unchanged. **A −1364/−1366 B change trips no exact-size assertion anywhere.**
**Answer to the brief's question:** the only exact-size assertions are `check_size_baseline.py:717` and `:722`, and neither is affected.

### Pitfall 3 — running the host suite before committing

**What goes wrong:** `pytest tests/` goes red for reasons unrelated to the change.
**Why:** `tests/test_flash_path_record_sync.py:1247` — `assert _git_porcelain(_FW_REPO_ROOT) == ""`, *"the firmware repo's working tree is no longer clean after the planted-copy test"*. **Confirmed still present.** `_git_porcelain` is defined at `:252-263` and shells `git -C <path> status --porcelain`; two more legs at `:874` and `:880` exercise it.
**How to avoid:** commit the firmware change **first**, then run `pytest tests/`. Baseline confirmed: **323 passed in 11.88 s** on the committed clean tree.
**Warning sign:** exactly one failure, in `test_flash_path_record_sync.py`, naming porcelain.

### Pitfall 4 — the two native suites fail to **build**, not to assert

**What goes wrong:** an intermediate commit removes the header field without the test edit; both native CI legs go red with a *compile* error, and the case count drops 172 → 127 which also looks like a `compare_native` regression.
**How to avoid:** header edit + test edit in the **same commit**. Do not split DEAD-01 and DEAD-06 across tasks that commit separately.
**Warning sign:** `has no member named 'progress_data'`.

### Pitfall 5 — the native suite is load-flaky (D-04)

**What goes wrong:** a single red run gets attributed to this change.
**Why:** measured 172/172 at ~35 s (×5), 171/172 once at 1:13, 158-cases-with-2-ERRORED once at 1:44 — failure correlates with **run duration**, not tree content. The scoping session fell into this trap itself.
**How to avoid:** never conclude from N=1. Baselines for this phase, measured today on an idle machine: `native` **172/172 in 23.9 s**, `native_nodevtools` **172/172 in 37.1 s**.

### Pitfall 6 — `check_size_baseline.py` runs in **no** CI workflow

**What goes wrong:** treating the size gate as automated.
**Why:** `grep -rn "check_size_baseline" .github/` returns **nothing**. CI runs exactly three firmware legs: `pio test -e native` (`build.yml:142`, `beta-build.yml:122`), `pio test -e native_nodevtools` (`:155` / `:128`), `pytest tests/ -v` (`:161` / `:134`).
**How to avoid:** state every size figure as a **local-run obligation**. Phase 158's LAND-04 owns making this explicit, but Phase 155 must not imply otherwise.

### Pitfall 7 — the canonical `--policy merge05` invocation is **already red on `beta`**

**What goes wrong:** a plan reads the pre-existing red as caused by this change.
**Why:** `--policy merge05 --baseline .../size_baseline_base01.json` fails on `native: cases baseline=141 observed=172` — BASE-01 frozen at Phase 124's count — and exits 1 on case counts **before it ever reports flash**. Phase 158's LAND-03 owns this. **The size-reduction diff touches zero files under `test/`… except** `test/native/avr/{test_val_5v_page,test_eeprom28c_sdp}` for DEAD-06 — which do **not** change the case count (an assertion is removed, not a case), so 172 stays 172. **Verify that** rather than assume it.

### Pitfall 8 — a `grep -c` gate that inverts on zero matches

**What goes wrong:** the DEAD-01/DEAD-03 assertion passes when the symbols are *present* and fails when absent, or vice versa.
**Why:** `grep -c` prints `0` and **exits 1** when nothing matches — which is the success case here.
**How to avoid:** capture the count and compare it (`[ "$H" -eq 0 ]`), with `|| true` on the grep. Author a **planted negative**: temporarily reinstate one `malloc` call and confirm the gate goes RED. This repo's convention (`tests/test_check_size_baseline.py:13`) is explicit that a gate with no negative fixture is the v1.12 hollow-GATE-03 failure mode.

### Pitfall 9 — the oracle grid does not exercise either overflow guard

Already covered under DEAD-04. Restated as a pitfall because it is the single most likely way criterion 4 gets ticked while a clause is unmet: **within R2 39k–47k, `k` maxes at 8715 and `r1+r2` maxes at 317000.** Both guards are three-plus orders of magnitude away. Four dedicated boundary cases are mandatory.

---

## Code Examples

### Symbol-absence assertion, fail-closed

```bash
# Source: derived from the installed toolchain; no repo precedent exists (see DEAD-01)
NM="$HOME/.platformio/packages/toolchain-atmelavr/bin/avr-nm"
HEAP_RE=' (T|t|B|b|D|d) (malloc|free|realloc|calloc|__brkval|__flp|__malloc_heap_start|__malloc_heap_end|__malloc_margin)$'
DI_RE='__(muldi3|muldi3_6|udivmod64|lshrdi3|udivdi3|udivdi3_umoddi3|umoddi3|adddi3|umulsidi3|umulsidi3_helper|ashrdi3)$'

rc=0
for e in uno uno328pb leonardo; do
  ELF=".pio/build/$e/firestarter_$e.elf"
  [ -f "$ELF" ] || { echo "MISSING $ELF"; rc=1; continue; }   # fail CLOSED on a missing build
  h=$("$NM" "$ELF" | grep -cE "$HEAP_RE" || true)
  d=$("$NM" "$ELF" | grep -cE "$DI_RE"   || true)
  echo "$e: heap=$h 64bit=$d"
  [ "$h" -eq 0 ] || rc=1
  [ "$d" -eq 0 ] || rc=1
done
exit $rc
```

### Sole-caller attribution from the disassembly

```python
# Source: written and run for this research; reproduces criteria 1 and 3's
# "was the allocator's ONLY caller anywhere" / "rurp_read_voltage_mv alone
# pulled in" claims mechanically. Output quoted in DEAD-01/DEAD-03 above.
import re, sys
func_re = re.compile(r'^[0-9a-f]{8} <(.+)>:')
ref_re  = re.compile(r'<([A-Za-z_][A-Za-z0-9_]*)(?:\+0x[0-9a-f]+)?>')
want = set("malloc free __muldi3 __udivmod64 __lshrdi3 __udivdi3 __umoddi3 "
           "__adddi3 __muldi3_6 __udivdi3_umoddi3 __umulsidi3 "
           "__umulsidi3_helper __ashrdi3".split())
cur, callers = None, {}
for line in open(sys.argv[1]):            # avr-objdump -d <elf> > file
    m = func_re.match(line)
    if m:
        cur = m.group(1); continue
    if 'call' in line or 'jmp' in line:
        for t in (c.group(1) for c in ref_re.finditer(line)):
            if t in want and t != cur:
                callers.setdefault(t, set()).add(cur)
for t in sorted(want):
    print(f"{t:22s} <- {sorted(callers.get(t, [])) or '(internal only)'}")
```

### The DEAD-04 oracle — numeric half

```python
# Source: written and run for this research. Reproduces every reading DEAD-04
# demands. 470,016 evaluations in 0.44 s, stdlib only.
VALUE_R1, VALUE_R2 = 270000, 44000          # include/rurp_shield.h:49-50

def v64(adc, bg, r1, r2):
    """Transcription of rurp_common.cpp:122-64 (the uint64 form being replaced)."""
    num = adc * 1100 * (r1 + r2)
    den = bg * r2
    return (num + den // 2) // den

def v32(adc, bg, r1, r2):
    """Transcription of the 32-bit reformulation, guards included."""
    s = r1 + r2
    if s > 3900000:      return 0           # 1100*(r1+r2) must fit uint32 (<= 3904515)
    k = (1100 * s) // r2
    if k > 4194303:      return 0           # adc*k must fit uint32 (<= 4198404)
    return (adc * k + bg // 2) // bg

# (a) bit-identity at the shipped calibration
assert (1100 * (VALUE_R1 + VALUE_R2)) // VALUE_R2 == 7850
assert v64(1023, 225, VALUE_R1, VALUE_R2) == v32(1023, 225, VALUE_R1, VALUE_R2) == 35691
assert all(v64(a, b, VALUE_R1, VALUE_R2) == v32(a, b, VALUE_R1, VALUE_R2)
           for b in range(200, 251) for a in range(1024))

# (b) bounded deviation over the STATED grid
worst = max(abs(v64(a, b, VALUE_R1, r2) - v32(a, b, VALUE_R1, r2))
            for r2 in range(39000, 47001, 1000)
            for b  in range(200, 251)
            for a  in range(1024))
assert worst == 5, worst                    # measured: exactly 5 mV

# (c) direction: the reformulation can only UNDER-read
assert not any(v32(a, b, VALUE_R1, r2) > v64(a, b, VALUE_R1, r2)
               for r2 in range(39000, 47001, 1000)
               for b  in range(200, 251) for a in range(1024))

# (d) BOTH guards, which the grid above never reaches
assert v32(1023, 225, 3900000 - 44000, 44000) != 0     # r1+r2 == 3900000: no fire
assert v32(1023, 225, 3900001 - 44000, 44000) == 0     # r1+r2 == 3900001: fires
# k boundary: choose (r1, r2) so floor(1100*(r1+r2)/r2) straddles 4194303
# (compute the exact pair at plan time; do not search at runtime)

# (e) pre-existing sentinels, unchanged
assert v32(1023, 225, VALUE_R1, 0) == 0                # r2 == 0  (rurp_common.cpp:62)
```

### The DEAD-04 oracle — source-contract half (the part that stops model drift)

```python
# Source: pattern copied from tests/test_write_path_source_contract_v131.py:223
# Purpose: bind the Python transcriptions above to the SHIPPED C, so a future
# edit to rurp_common.cpp that does not match the model fails CI leg 3.
def test_shipped_c_matches_the_transcribed_formula():
    body = _strip_comments(_RURP_COMMON.read_text())   # line-shape-preserving
    fn   = _extract_function(body, "rurp_read_voltage_mv")
    for needle in (
        "uint32_t sum = r1 + r2",
        "if (sum > 3900000UL)",
        "uint32_t k = (1100UL * sum) / r2",
        "if (k > 4194303UL)",
        "(voltage_adc_reading * k + bg / 2) / bg",
    ):
        assert needle in fn, f"transcription drift: {needle!r} not in shipped C"
    assert "uint64_t" not in fn, "a uint64_t reappeared -- the 64-bit runtime will relink"
```

The last assertion is worth highlighting: `assert "uint64_t" not in fn` is a **cheap, CI-resident second oracle for DEAD-03** that catches a regression at source level even when nobody re-runs `avr-nm`.

---

## Runtime State Inventory

> Included because DEAD-01 is a **field removal from a shared struct** and DEAD-03 changes a **calibration-consuming computation** — both are the shapes that carry hidden runtime state. This is not a rename phase, but the checklist applies.

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | **`rurp_configuration_t` in Arduino EEPROM** holds `r1` / `r2` (the calibration this phase's arithmetic consumes) plus `hw_revision`. **Not touched, and must not be.** The reformulation reads the *same* `r1`/`r2` from the *same* store — no schema change, no migration, no re-calibration. `config_version` unchanged. Verified: `rurp_config_utils.cpp:38-39` still defaults to `VALUE_R1`/`VALUE_R2`; `hardware_operations.cpp:124-131` still serialises `r1`/`r2` as 4 bytes each. **`progress_data` was never persisted anywhere** — it was heap-only, per-command. | **None.** No data migration. Code-only change. |
| **Live service config** | **None.** No n8n workflow, Datadog service, Tailscale ACL or Cloudflare tunnel references any symbol here — this is MCU-local arithmetic and MCU-local heap. Verified by scope: the change is confined to three firmware source files. | None. |
| **OS-registered state** | **None.** No Task Scheduler task, pm2 process, launchd plist or systemd unit names anything in this phase. Verified by scope. | None. |
| **Secrets / env vars** | **None.** No secret, `.env` key, SOPS key or CI variable references `progress_data`, `blank_check_progress_data_t`, `malloc`, or any 64-bit helper. Verified: `grep` over `firestarter_app/{tests,firestarter,tools}` for all of these returns **zero hits**. | None. |
| **Build artifacts** | **Stale `.pio/build/{uno,uno328pb,leonardo,native,native_nodevtools,…}` object trees** exist and are warm. A *warm* rebuild is sufficient for flash/RAM figures (deterministic), but **LAND-01/Phase 158 requires COLD builds** (`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`) for the baseline re-record. **Phase 155 must not perform the cold re-record**, but its own before/after figures should note whether they are warm or cold. The figures in this document are **warm**. Also: **flashed boards** carry the old firmware — irrelevant, since D-02 forbids any bench criterion. | **Note warm-vs-cold on every figure.** Do not re-anchor. |

**The canonical question, answered:** after every source file is edited, the only runtime system holding pre-change state is the **Arduino EEPROM calibration** (`r1`/`r2`) — and it is read identically by both the old and the new arithmetic, which is exactly what DEAD-04's bit-identity-at-shipped-calibration clause proves. **Nothing requires a data migration.**

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| PlatformIO Core | all builds/tests | ✅ | 6.1.19 | — |
| `platform-atmelavr` | 3 AVR builds | ✅ | 5.2.0 | — |
| `toolchain-atmelavr` (`avr-gcc`) | AVR compile | ✅ | 1.70300.191015 / 7.3.0 | — |
| **`avr-nm`** | **DEAD-01, DEAD-03** | ✅ | binutils in toolchain-atmelavr | none needed |
| **`avr-objdump`** | sole-caller proof | ✅ | same | `avr-nm` alone gives presence but not callers |
| `avr-size` | size figures | ✅ | same | `pio run` prints RAM/Flash directly |
| `framework-arduino-avr` | AVR builds | ✅ | 5.3.0 | — |
| `framework-arduino-avr-minicore` | `uno328pb` | ✅ | installed | — |
| ArduinoFake | native suites | ✅ | 0.4.0 via `lib_deps` | — |
| **pytest** | CI leg 3 + DEAD-04 oracle host | ✅ | system python3 (`323 passed`) | ⚠ **not** in the PlatformIO penv — `pio`'s python has no pytest. Use system `python3 -m pytest`. |
| CPython 3.x stdlib | the oracle grid | ✅ | — | none needed (0.44 s, no third-party lib) |
| `git` | worktree, porcelain gates | ✅ | — | — |
| **Linker `.map` file** | an alternative symbol oracle | ❌ | — | ✅ **`avr-nm` on the `.elf`** — use this; do not add `-Wl,-Map` |
| Physical RURP board | — | n/a | — | ✅ **Forbidden by D-02.** No bench criterion. |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** the `.map` file (use `avr-nm`); pytest inside the pio penv (use system `python3 -m pytest`).

**⚠ Devcontainer caveat carried forward:** the devcontainer's default Python is 3.12 while the *app* repo's CI pins 3.11. **Not relevant to this phase** — `firestarter/tests/` runs under whatever `pip install pytest` provides in `build.yml:158` with no version pin, and Phase 155 touches no app file. Recorded so the planner does not import the app-repo `uv venv --python 3.11` ceremony needlessly.

---

## Validation Architecture

### Test framework

| Property | Value |
|---|---|
| Frameworks | **Unity** (native, via PlatformIO `test_framework = unity`) + **pytest** (host-side script/source gates) |
| Config file | `/workspaces/firestarter/platformio.ini` |
| CI legs (exactly three) | `pio test -e native` (`build.yml:142`, `beta-build.yml:122`); `pio test -e native_nodevtools` (`:155` / `:128`); `pytest tests/ -v` (`:161` / `:134`) |
| Quick run command | `pio test -e native` |
| Full suite command | `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q` |
| Non-CI local gates | `python3 scripts/check_size_baseline.py …`, `check_build_warnings.py` — **invoked by no workflow** (`grep -rn check_size_baseline .github/` → nothing) |

### Measured baselines, today, at `2ad5b32` on a clean tree

| Leg | Result |
|---|---|
| `pio test -e native` | **172 cases / 172 succeeded**, 17 suites, 23.9 s |
| `pio test -e native_nodevtools` | **172 cases / 172 succeeded**, 17 suites, 37.1 s |
| `python3 -m pytest tests/` | **323 passed**, 11.9 s |
| `pio run -e uno` | flash **26026**, RAM **1575** |
| `pio run -e uno328pb` | flash **26074**, RAM **1581** |
| `pio run -e leonardo` | flash **28170**, RAM **2016** |
| `git status --porcelain` (firestarter) | **empty** |

### Phase requirements → test map

| Req | Behaviour to prove | Test type | Automated command | Exists? | Ceiling |
|---|---|---|---|---|---|
| **DEAD-01** | no heap symbol in any of the 3 images | image/link assertion | `avr-nm` gate over 3 ELFs (script in Code Examples) — must print `heap=0` ×3 | ❌ **Wave 0** — no symbol gate exists in this repo | Link-time truth. **Complete** for this claim. |
| **DEAD-01** | `mem_util_blank_check` was the only caller | disassembly attribution | `avr-objdump -d` + attribution script, run against the **pre-change** ELF | ❌ **Wave 0** (before-figure capture) | Must be captured **before** the change; unrecoverable after. |
| **DEAD-01** | −650 B / −8 B RAM claim | size measurement | `pio run -e {uno,uno328pb,leonardo}`, diff vs pre-change | ✅ existing command | **−8 B RAM confirmed exactly.** Flash split **corrected** (C-2); quote the −1366 total. |
| **DEAD-02** | the unchecked deref is gone; recorded as a latent defect | source diff + phase record | `git diff` shows `memory.cpp:502-500` removed; no `malloc` remains | ✅ (subsumed by DEAD-01's gate) | **Documentation obligation, not a test.** The *record* is the deliverable. RAM figures must use the corrected C-3 arithmetic. |
| **DEAD-03** | no 64-bit runtime symbol in any of the 3 images | image/link assertion | `avr-nm` gate, **11 symbols** not 8 (C-4) — must print `64bit=0` ×3 | ❌ **Wave 0** | Link-time truth. **Complete.** |
| **DEAD-03** | `rurp_read_voltage_mv` alone pulled them in; body 434 → ~232 B | disassembly + `avr-nm --print-size` | pre-change attribution + `avr-nm --print-size \| grep read_voltage_mv` | ❌ **Wave 0** | Measured **434 → 230 B**. |
| **DEAD-03** | no `uint64_t` reappears in that function | source contract | pytest assertion `"uint64_t" not in fn` | ❌ **Wave 0** | Cheap CI-resident regression guard; complements the ELF gate. |
| **DEAD-04** | bit-identity at shipped calibration; ≤5 mV over the grid; both guards; `r2==0` → 0 | **numerical oracle**, pytest | `python3 -m pytest tests/test_voltage_reformulation_oracle.py -q` (name illustrative) | ❌ **Wave 0** | ⚠ **See ceiling below.** Grid: 470,016 evals / 0.44 s. **Guards need 4 cases outside the grid.** |
| **DEAD-04** | the shipped C **is** the formula the oracle models | **source contract**, pytest | same file, comment-stripped scan of `rurp_common.cpp` | ❌ **Wave 0** | **Mandatory.** Without it the oracle proves Python == Python. |
| **DEAD-05** | the ceiling is stated in every artefact | documentation + a negative assertion | assert no phase artefact claims native/bench coverage of `rurp_read_voltage_mv` | ❌ **Wave 0** | ⚠ **This requirement is itself about honesty of wording.** See ceiling. |
| **DEAD-06** | both suites updated; behaviour still pinned; alternative recorded with cost | native suites (regression) | `pio test -e native` and `-e native_nodevtools` → **172/172, 17 suites** | ✅ suites exist | **Compiler-forced** — cannot be skipped or go vacuous. Case count must stay **172** (a `compare_native` input). |

### ⚠ The honest coverage ceiling — DEAD-04 and DEAD-05

**This must appear, in these terms, in VALIDATION.md, every plan, every SUMMARY and the phase record.**

`src/boards/rurp_common.cpp` is compiled by **no** PlatformIO environment except the three AVR targets. All six native envs share `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>` (`platformio.ini:227`, `:307`, and the four single-suite envs). Consequently:

1. **`rurp_read_voltage_mv` has ZERO native unit-test coverage, before and after this phase.** In native builds it is a **stub** — `test/native/avr/_shared/host_stubs_common.inc:275` returns 0 by default, and four suites override it with `set_mock_vpp_mv`. Every native VPP test exercises the *consumer* against a mock, never this arithmetic.
2. **DEAD-04's oracle is a HOST-SIDE NUMERICAL MODEL, not a test of compiled firmware.** It proves that two integer formulas agree over a stated grid, and — via the source-contract scan — that the shipped C is textually the formula modelled. It does **not** execute the AVR code. It does not prove avr-gcc's codegen for `(voltage_adc_reading * k + bg / 2) / bg` is correct, only that the algorithm is.
3. **There is NO bench coverage, and none will be created.** D-02 forbids it. Native trace stubs additionally record **no time** (`delay()` is unstubbed), so no trace diff could contribute here even if the TU compiled.
4. **The residual risk, named:** avr-gcc miscompiling 32-bit `uint32_t` multiply/divide. This is not mitigated by any artefact of this phase. It is mitigated only by the arithmetic being 32-bit AVR's most exercised path, and by the change **reducing** rather than increasing codegen complexity (it deletes the 64-bit path). Say this; do not imply it is covered.
5. **Forbidden phrasings** in any Phase 155 artefact, about this function: "tested", "unit-tested", "covered by native", "verified on hardware", "bench-verified", "proven at runtime".
   **Correct phrasing:** *"proven by a committed host-side numerical oracle over a stated input grid, bound to the shipped C by a source-contract scan; no native and no bench coverage exists."*
6. ⚠ **The preserved reference's own comment gets this wrong.** `a6b46f8`'s `rurp_common.cpp` comment reads: *"NOT covered by any native test: this TU is outside [env:native]'s src_filter (+<proms/>), so this arithmetic is **bench-verified only**."* **"bench-verified only" is false and directly violates DEAD-05 and D-02.** If the reference's comment is carried across, **this clause must be rewritten**, e.g. *"…so this arithmetic is covered only by the host-side numerical oracle in `tests/`; there is no native and no bench coverage."*

### Sampling rate

- **Per task commit:** `pio test -e native` (23.9 s) — catches the DEAD-06 build break immediately.
- **Per wave merge:** `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q` — **after commits land** (Pitfall 3).
- **Phase gate (all green before `/gsd-verify-work`):**
  1. `pio test -e native` → **172/172, 17 suites**
  2. `pio test -e native_nodevtools` → **172/172, 17 suites**
  3. `python3 -m pytest tests/ -q` → **≥323 passed** (323 + the new oracle file's cases), 0 failed — run **only after** the firmware commit lands
  4. `avr-nm` heap gate → `0` on all three ELFs
  5. `avr-nm` 64-bit gate (11 symbols) → `0` on all three ELFs
  6. `pio run -e {uno,uno328pb,leonardo}` → flash/RAM recorded, delta computed against the **pre-change same-tree** figures (26026 / 26074 / 28170 and 1575 / 1581 / 2016)
  7. `scripts/check_size_baseline.py` MERGE-05 policy run → green, **recorded as one-sided per D-03**, and **not** re-anchored (LAND-01)
  8. `scripts/check_build_warnings.py` → no new warning on `memory.cpp`, `rurp_common.cpp`, `firestarter.h`

### Wave 0 gaps

- [ ] **Pre-change before-figures, captured and committed before any edit** — covers DEAD-01, DEAD-03. Irrecoverable afterwards: the `avr-nm` symbol table, the `avr-objdump` sole-caller attribution, the three flash/RAM pairs, `rurp_read_voltage_mv` = 434 B, `mem_util_blank_check` = 510 B, `handle` = 603/603/1115 B.
- [ ] **`scripts/check_no_heap_or_64bit_symbols.py`** (or a shell gate) — covers DEAD-01, DEAD-03. Must be **fail-closed** on a missing ELF and must **not** rely on `grep`'s exit status (Pitfall 8).
- [ ] **A planted negative for that gate** — reinstate one `malloc` call in a throwaway worktree, confirm the gate goes RED, record it. Without this the gate is a hollow gate by this repo's own named standard.
- [ ] **`tests/test_voltage_reformulation_oracle.py`** — covers DEAD-04, DEAD-05. Two halves: numerical grid (grid + 4 guard-boundary cases + 2 sentinel cases) **and** the comment-stripped source-contract scan. Lands in CI leg 3. `_strip_comments` copied from `tests/test_write_path_source_contract_v131.py:223`.
- [ ] **Exact `(r1, r2)` pair straddling `k = 4194303`** — computed at plan time, not searched at runtime.
- [ ] **Nothing needed for DEAD-06** — both suites exist and the change is compiler-forced.
- [ ] **Framework install:** none. All frameworks present. (Use system `python3 -m pytest`, not the pio penv.)

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as enabled.

### Applicable ASVS categories

| ASVS category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No auth surface; local USB serial, no identity. |
| V3 Session Management | no | No sessions. The `operation_state` bit is a single-command state machine, not a session. |
| V4 Access Control | no | Unchanged. Command admission (`rurp_pinmap_refuses`, `is_memory_cmd`) is untouched. |
| **V5 Input Validation** | **yes** | **Directly relevant and improved.** `r1`/`r2` arrive over the wire (`json_parser.c:514,518` `extract_long("r1"/"r2")`) into EEPROM, then feed this arithmetic. Today an adversarial or corrupt calibration produces a 64-bit product that cannot overflow but *can* truncate the `uint16_t` return silently. The reformulation adds **two explicit range guards** (`r1+r2 <= 3900000`, `k <= 4194303`) that **fail closed to 0** — the same sentinel the existing `r2 == 0` / `bandgap == 0` check already uses at `rurp_common.cpp:62`. **This is a net input-validation improvement, and should be recorded as one.** |
| **V6 Cryptography** | no | None involved. **Never hand-roll** — not applicable, nothing cryptographic here. |
| **V7 Error handling / logging** | **yes** | Unchanged, and must stay so: `MSG_ERR_NOT_BLANK`, `MSG_DATA_PROGRESS`, `MSG_WARN_VPP_LOW`, `MSG_ERR_VPP_HIGH` payloads and severities are all outside the edited hunks. A plan must verify no `LOG_*` line moves. |
| **V10 Malicious code** | **yes** (low) | Zero new dependencies; nothing downloaded; nothing generated. See Package Legitimacy Audit. |

### Known threat patterns for this stack

| Pattern | STRIDE | Standard mitigation | Status in this phase |
|---|---|---|---|
| **Unchecked allocation dereference** | Denial of Service (MCU reset / silent corruption) | check the allocation, or don't allocate | ✅ **Closed by removing the allocation.** This is DEAD-02 and the phase's security headline. On a part with under 473 B of shared heap/stack headroom, a failed 4-byte `malloc` wrote through NULL. |
| **Heap fragmentation / exhaustion on a 2 KiB MCU** | Denial of Service | eliminate the heap | ✅ **Firmware becomes heap-free.** `__brkval`, `__flp` and the three `__malloc_*` globals all leave the image. This is a categorical elimination, not a mitigation. |
| **Integer overflow in a wire-driven computation** | Tampering | explicit range guards, fail closed | ✅ **Two new guards added**, both returning the existing 0 sentinel. Both must be **exercised by a test** (DEAD-04 clause) — and the nominal grid does not reach them. |
| **Silent truncation into a valid-looking value** | Tampering | saturate or refuse | ⚠ **Partially.** The `uint16_t` return can still truncate for an absurd-but-guard-passing calibration. **Unchanged from today's behaviour** — not a regression, and out of DEAD-04's stated scope. Record as unchanged rather than claim it fixed. (The analogous *narrowing*-truncation hazard is Phase 157's DECODE-05, a different field and a different phase.) |
| **Under-reporting a safety voltage** | Tampering / Repudiation | bound the error against the consumer's tolerance, in the safe direction | ✅ **Bounded and directionally safe.** The reformulation only ever **under**-reads, by ≤5 mV. So it can never suppress a `MSG_ERR_VPP_HIGH` (which fires on `vpp_mv > target + 500`, an over-read condition). Its only possible effect is a spurious `MSG_WARN_VPP_LOW` **warning** within 0.83 % of the `−5 %` edge. **This is the correct security framing and it is stronger than the ROADMAP's symmetric "±5 %" claim** — which is itself wrong (the high edge is `+500 mV` absolute). |
| Test coverage regression laundered as cleanup | Repudiation | keep an equally strong witness; record the loss | ✅ DEAD-06. The surviving `is_operation_in_progress` assertion is set in the same unconditional branch (C-5) and is non-weaker. |

---

## State of the Art

| Old approach | Current approach | When changed | Impact |
|---|---|---|---|
| `malloc`/`free` for per-command scratch on an 8-bit MCU | file-scope static, or a caller-owned buffer | long-settled AVR practice (`avr-libc` docs warn the allocator is unsuitable for small-SRAM parts) | Eliminates 586 B of code and the entire null-deref class. `[ASSUMED]` — the practice is standard; the 586 B is `[VERIFIED]`. |
| `uint64_t` intermediates on AVR | fold constants to stay in `uint32_t`, guard explicitly | long-settled; avr-gcc has no hardware 64-bit path and links soft helpers per use | 528 B of linked helpers for one 7-line expression, measured. `[VERIFIED: avr-nm]` |
| Asserting on source text | asserting on the linked ELF | — | A source grep for `malloc(` fails open on any other TU; `avr-nm` cannot. |

**Deprecated / outdated in this repo's own history:**
- `messages.c` (a 256-byte PROGMEM table with no firmware callers) was **deleted post-Phase-7** to reclaim Leonardo flash (`platformio.ini:239-241`). Same class of change as this phase; useful precedent for the record's framing.
- `size_baseline.json`'s `envs_agree_note` still quotes a stale `{cases: 151, suites: 17}` pair *"which no consumer reads"* (recorded in its own `meta`). Pre-existing; **not** this phase's to fix.
- BASE-01's native case count is frozen at Phase 124's 141 vs today's 172 — **Phase 158 / LAND-03**, not this phase.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| **A1** | The `+10 B` residual in the flash ledger is call-site register-allocation / inlining effects. | Measured Figures | **Low.** The whole-image delta (−1366) is measured directly and is what every criterion needs. The attribution is explanatory only, and is labelled unattributed. |
| **A2** | Avoiding the heap is standard practice on 2 KiB AVR parts (as general engineering guidance). | State of the Art | **None.** The 586 B saving is measured; the "standard practice" framing is background colour. |
| **A3** | The oracle-file name `tests/test_voltage_reformulation_oracle.py` and its exact assertion shapes. | Validation Architecture, Code Examples | **None.** Illustrative; the planner chooses. The *placement* (`firestarter/tests/`, CI leg 3) is `[VERIFIED]` from the workflow files. |
| **A4** | avr-gcc 7.3.0 correctly compiles the 32-bit multiply/divide the reformulation emits. | Security Domain, Validation ceiling | **Named as residual risk, explicitly unmitigated.** Not presented as covered. |
| **A5** | The `172` native case count is unchanged by DEAD-06 (an assertion is removed, not a case). | Pitfall 7, Validation | **Low, and it is a gate not an assumption** — the phase gate measures it. Flagged for explicit verification rather than assumption. |
| **A6** | Removing the four in-scope stale `memory.cpp:NNN` pins (rather than renumbering them) is the right call. | DEAD-06 | **Low.** A mechanical grey area with a settled precedent (Phase 154's 10.7:1 reflow ratio; 156/157/158 will move the file again; 159 remaps). Recorded as decided, not asked. |

**Everything else in this document is `[VERIFIED]` by a tool run in this session** — `pio run` / `pio test`, `avr-nm`, `avr-objdump`, `git diff`, `grep`, or an independent Python reimplementation. No claim rests on training knowledge about this codebase.

---

## Open Questions (RESOLVED 2026-08-23 by the /gsd-plan-phase orchestrator as OQ-1…OQ-5; OQ-6 added from 155-PATTERNS.md. Each recommendation below was taken as written. The plans implement the locked value, not the question.)

1. **RESOLVED (OQ-1) — take `4194303`, record −1366 B.** — original question: **`k` guard: `4194303` or `4000000`?**
   - Known: `4194303` measures **−1366 B**; `4000000` measures **−1364 B** — same tree, same everything else. `4194303 = 0x3FFFFF`, so the test compiles to a shift; it is also the tighter bound (exact ceiling 4198404). REQUIREMENTS/ROADMAP criterion 4 names `4194303`; the preserved reference uses `4000000`; the "Measured: −1364 B" header matches `4000000`.
   - Unclear: whether the operator regards the `−1364` header or the `4194303` criterion as the binding statement.
   - **Recommendation: take `4194303` and record `−1366 B`.** It satisfies the criterion as literally written, is 2 B cheaper, and is the better-reasoned bound. State the 2 B delta and its cause in the phase record. Do not silently ship `4000000` to make `−1364` come out.

2. **RESOLVED (OQ-2) — yes, assert all 11 and record both 438 B / 528 B.** — original question: **Does DEAD-03's assertion list get corrected to 11 symbols?**
   - Known: the 8 named symbols total exactly 438 B (the requirement's figure is right); 3 more (`__umulsidi3` 2 B, `__umulsidi3_helper` 84 B, `__ashrdi3` 4 B) total 90 B and also leave; the real blob is 528 B contiguous.
   - Unclear: whether "the image contains no 64-bit runtime helper" is to be read as the 8-item list or as the class.
   - **Recommendation: assert all 11 and record both figures** — "438 B across the 8 named symbols, 528 B across the full contiguous blob". A gate over 8 could pass with 90 B still linked; a gate over 11 cannot. Costs nothing.

3. **RESOLVED (OQ-3) — yes, correct it; the asymmetric window makes the bound stronger.** — original question: **Does the phase record correct the "±5 % / ±600 mV" tolerance statement?**
   - Known: the low edge **is** `−5 %` = `−600 mV` at 12 V; the high edge is a **fixed `+500 mV`**, not `+5 %` (`eprom.cpp:713`, `flash_intel.cpp:39`).
   - **Recommendation: yes, correct it.** The 5 mV bound is then 1.0 % of the tighter (500 mV) window, and the directional argument — under-reads only, so no `VPP_HIGH` error can ever be suppressed — is materially stronger than the symmetric claim. Corrected figures are recorded publicly in this project.

4. **RESOLVED (OQ-4) — carry both per-target figures, with "shared heap-and-stack headroom".** — original question: **Is `handle` = 603 B (uno) or 1115 B (leonardo) the number the phase record should carry for DEAD-02?**
   - **Recommendation: both, per target, plus the corrected framing** — on `uno`, `handle` 603 B + tokens 512 B = 1115 B of 2048 B, leaving 473 B; on `leonardo`, `handle` 1115 B + tokens 512 B = 1627 B of 2560 B, leaving 544 B. And say "shared heap-and-stack headroom", since `ram_used` excludes the stack. The `~470 B` conclusion survives; its derivation does not.

5. **RESOLVED (OQ-5) — a two-halved phrasing gate: negative scan AND positive assertion.** — original question: **How is DEAD-05 mechanically checked, given it is a requirement about wording?**
   - Known: it demands that "no phase artifact may imply native or bench coverage". That is a property of `.planning/` prose, not of code.
   - **Recommendation:** a small pytest or plan-gate leg that greps this phase's artefacts for the forbidden phrasings (list in the ceiling section) applied to `rurp_read_voltage_mv`, and asserts the correct phrasing is present in VALIDATION.md. **And note explicitly that the preserved reference's own comment says "bench-verified only"** — the single most likely source of a DEAD-05 violation is copying that comment across unedited.

---

## Sources

### Primary (HIGH confidence — measured in this session)

- `pio run -e {uno,uno328pb,leonardo}` at `2ad5b32` and with the change applied in a throwaway worktree — all flash/RAM figures.
- `avr-nm --print-size --size-sort -C` on all three `.elf` files, before and after — every symbol size and the absence proof.
- `avr-objdump -d` + a call-attribution script over `firestarter_uno.elf` — sole-caller proof for `malloc`, `free` and the five directly-referenced 64-bit helpers.
- `pio test -e native` (172/172, 23.9 s), `pio test -e native_nodevtools` (172/172, 37.1 s), `python3 -m pytest tests/` (323 passed, 11.9 s).
- `pio test -e native` with `progress_data` removed and tests untouched — the two `error:` lines and the 172 → 127 case drop.
- Independent Python reimplementation of both voltage formulas — `k = 7850`, 35691 both ways, 0 mismatches over 1,046,529 evals at the shipped calibration, worst deviation exactly 5 mV over 470,016 and 4,230,144 evals, direction one-sided, 0.44 s runtime.
- `git diff 8695ee5 a6b46f8` (with corrected `test/native/avr/…` paths) — the preserved reference, quoted.

### Primary (HIGH confidence — read in this session)

- `firestarter/platformio.ini` — `:16` default_envs; `:227`, `:307` build_src_filter; `:239-241` messages.c precedent; `:281-286`, `:449-462`, `:509-520`, `:560-570` the no-CI-coverage and F-138-05 KeyError constraints.
- `firestarter/src/boards/rurp_common.cpp:1-123` — the function, quoted in full.
- `firestarter/src/proms/memory.cpp:458-547` — the typedef and `mem_util_blank_check`, quoted.
- `firestarter/include/firestarter.h:206-234` — the handle struct.
- `firestarter/include/operation_utils.h:41-51` — `set_/clear_/is_operation_in_progress` (the C-5 evidence).
- `firestarter/include/rurp_shield.h:49-50` — `VALUE_R1` / `VALUE_R2`; `firestarter/src/rurp_config_utils.cpp:38-39`.
- `firestarter/include/json_parser.h:17` — `NUMBER_JSNM_TOKENS 64`; `firestarter/src/firestarter.cpp:33` — `handle` is a global.
- `firestarter/src/proms/eprom.cpp:695-722`, `firestarter/src/proms/flash_intel.cpp:26-44`, `firestarter/src/hardware_operations.cpp:55-90` — the three consumers and both validation windows.
- `firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp:225-358`; `…/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp:97, 1745-1797`.
- `firestarter/scripts/check_size_baseline.py:146, 476-477, 680-745`; `firestarter/scripts/baseline/size_baseline.json` (meta, avr_targets, native_envs).
- `firestarter/tests/test_flash_path_record_sync.py:252-263, 874-882, 1205-1250`; `firestarter/tests/test_check_size_baseline.py:13-135, 190-280`; `firestarter/tests/test_write_path_source_contract_v131.py:149-300`.
- `firestarter/.github/workflows/build.yml:142,155,157-161`; `beta-build.yml:122,128,130-134` — the three CI legs.
- `/workspaces/CLAUDE.md`, `/workspaces/firestarter/CLAUDE.md`.
- `.planning/{ROADMAP.md,REQUIREMENTS.md,STATE.md,PROJECT.md,config.json}`.

### Secondary (MEDIUM confidence)

- `git branch -a` / `git merge-base` — the preserved ref's topology. Verified, but STATE.md is the authority on its protected status.
- `size_baseline.json`'s `meta` prose for the `+478/+476/+540` growth figures — transcribed from that file's own record, cross-checked against my measured `26026` vs recorded `25548` (`+478` ✅ confirmed on `uno`).

### Tertiary (LOW confidence — flagged, not relied upon)

- General AVR "avoid the heap" and "avoid `uint64_t`" guidance — background framing only. Every quantitative claim in this document comes from a tool run above, not from this.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Standard stack | **HIGH** | No new dependency. Every tool version read from the installed toolchain and `size_baseline.json` meta. |
| Symbol-level facts (DEAD-01, DEAD-03) | **HIGH** | `avr-nm` and `avr-objdump` on all three ELFs before **and** after. Sole-caller status mechanically derived, and it corrected the requirement's own symbol list. |
| Size and RAM deltas | **HIGH** | Six builds (3 before, 3 after) plus a seventh for the `k`-constant variant. Identical delta on all three targets. RAM ledger reconciles to the byte. |
| Voltage arithmetic (DEAD-04) | **HIGH** | Every stated reading independently reproduced; grid swept twice at two resolutions; the guard-coverage gap and the tolerance-window error found by measurement, not inference. |
| Coverage ceiling (DEAD-05) | **HIGH** | `build_src_filter` read directly; the stub sites enumerated; all four workaround options evidenced against `platformio.ini`'s own HARD CONSTRAINT comments and `check_size_baseline.py:146`. |
| Test-file impact (DEAD-06) | **HIGH** | The build break was **executed**, not predicted; assertions and comments quoted with line numbers; the rejected alternative's 2 B cost measured. |
| Gate/CI hazards | **HIGH** | All eight hazards in the brief checked individually against source. Two turned out different from the brief's framing (the "watermark 1166 / zero headroom" gate is not what constrains this phase — the `172/17` native case count is; and `check_size_baseline.py` has no exact flash assertion at all). |
| ROADMAP figure fidelity | **HIGH** | Five corrections, each with a reproduction command. |
| Prior-art scope fence | **MEDIUM-HIGH** | Attribution derived by matching each hunk to a named requirement in the 156/157/158 ROADMAP entries. Unambiguous for 9 of 11 files; the two split files (`firestarter.h`, `memory.cpp`) are separated hunk-by-hunk and stated as such. |

**Research date:** 2026-08-23
**Tree measured:** `firestarter` `2ad5b322a37ba4a88afd09cc946f5c4114e51483` (branch `gsd/v1.33-source-hygiene-firmware-size-reduction`), working tree clean.
**Valid until:** invalidated by any commit to `firestarter` that changes `src/`, `include/`, `test/` or `platformio.ini`. In particular, **Phases 156, 157 and 158 will each invalidate the flash/RAM figures**, so Phase 155 must capture its own before-figures immediately before it edits — the numbers in this document are correct **only** for a Phase 155 that runs first, from `2ad5b32`.
