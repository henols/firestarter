---
title: Before-figures record — milestone v1.33, Phase 157 (Command-Decode Table + Handle Type Narrowing, firmware-only)
phase: 157-command-decode-table-handle-type-narrowing-firmware-only
plan: "01"
measured: 2026-08-23
status: AUTHORITATIVE — this file is the ONLY source for Phase 157's before-half figures. Phase 158
  invalidates the AVR image figures captured here (it re-anchors `size_baseline.json` and
  cold-rebuilds all three targets), so no later plan can re-derive them from this position.
  Supersedes ROADMAP.md §Phase 157 success criteria 1 through 7 and REQUIREMENTS.md DECODE-01
  through DECODE-07 prose, wherever they state a figure this file corrects — C-1 through C-19.
supersedes: >
  ROADMAP.md §Phase 157 criteria 1 ("86–110 B each"), 2 ("Ten of eleven were stored twice",
  "`json_parse_config` calls it directly at two sites"), 3 ("a compile-time assertion prevents a
  future struct reorder"), 4 ("19 protocol comparisons", "45 `is_flag_set` call sites"), 7
  ("25696 vs 25678"), and the milestone-level "−1148 B flash (field table −976, narrowing +
  saturation −172)" split; REQUIREMENTS.md DECODE-01 ("Measured: −976 B"), DECODE-02 ("Ten of
  eleven … `json_parse_config` calls it directly at two sites"), DECODE-04 ("19 protocol
  comparisons and 45 `is_flag_set` call sites"), and DECODE-07 ("`uno` 25696 vs 25678") prose,
  wherever they state a figure this file corrects (C-1 through C-19). Neither document is edited
  by this plan; the correction lives here per the Phase 155/156 convention.
requirements: [DECODE-01, DECODE-02, DECODE-03, DECODE-04, DECODE-05, DECODE-06, DECODE-07]
---

# Before-figures record — v1.33 Phase 157

Every number in this file was measured on a **clean, unedited** `firestarter` working tree during
this plan's session, run from `/workspaces/firestarter` (the canonical checkout). Each number
carries the verbatim command that produced it. Every flash/RAM figure is labelled **WARM**. This
task edited no tracked file; the tree was proven clean before AND after every step (§1).

This document's own `file:LINE` citations were measured against the current post-Phase-154 tree
and will themselves be remapped by Phase 159 (REMAP-01…04). Plan 02 adds two `#include` lines
(`<stddef.h>`, `<string.h>`) to `src/json_parser.c`, which shifts every citation in that file by
+2 from plan 02 onward — expected, accounted for by milestone decision D-01, and not a defect.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_PRE_SHA` | `1151dc497254ea7dc5dd6395d10cb76791236938` (abbreviates `1151dc4`) |
| `firestarter` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` |
| `git -C firestarter status --porcelain` | empty (asserted before AND after this plan's measurement work) |
| `git -C firestarter diff --name-only HEAD` | empty |
| meta HEAD sha (before this plan's own commit) | `7be9835e0c35fb55f953139f5bff08355811c217` |
| `git -C firestarter worktree list` | `/workspaces/firestarter` (primary, `1151dc4`, this branch) + `/workspaces/firestarter_py32_ci` (pre-existing, unrelated sibling checkout, `ad47c3b` on `feature/py32f071-release-assets`) — no throwaway worktree was created by this plan |

**`firestarter_app` gitlink note:** the meta repo shows `firestarter_app` as modified
(`git status --porcelain` in `/workspaces`). This is **pre-existing Phase 154 drift,
operator-gated** — not touched, staged or re-pinned by this plan or any plan in this phase.

Commands run:
```bash
git -C firestarter rev-parse HEAD
git -C firestarter rev-parse --short HEAD
git -C firestarter branch --show-current
git -C firestarter status --porcelain
git -C firestarter diff --name-only HEAD
git rev-parse HEAD   # meta repo
git -C firestarter worktree list
```

---

## 2. AVR image figures, WARM

| Target | Flash used | Flash total | RAM used | RAM total | Label |
|---|---|---|---|---|---|
| `uno` | **24234** | 32768 | **1567** | 2048 | **WARM** |
| `uno328pb` | **24282** | 32768 | **1573** | 2048 | **WARM** |
| `leonardo` | **26378** | 32768 | **2008** | 2560 | **WARM** |

All six figures matched the plan's stated expectation exactly, reproduced **twice** this session
(once before the size-gate's `--rebuild` cold-cleaned all three `.pio/build/<env>` directories,
once after, to confirm the rebuild changed nothing) — see §8.

**Leonardo Caterina headroom against the 28672 B cliff: `28672 − 26378 = 2294 B`.**

Command per target: `pio run -e uno`, `pio run -e uno328pb`, `pio run -e leonardo` (also run
combined as `pio run -e uno -e uno328pb -e leonardo`), each read via its `RAM:` / `Flash:` summary
line, run from `/workspaces/firestarter`.

**These figures are deliberately WARM, not cold.** LAND-01 / Phase 158 owns the cold re-record
(`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` per env, per
`size_baseline.json`'s own documented convention); re-recording cold here would duplicate that
plan's job.

---

## 3. The eleven-stub ledger, `uno`

`avr-nm --print-size --size-sort --radix=d .pio/build/uno/firestarter_uno.elf`, resolved at
`$HOME/.platformio/packages/toolchain-atmelavr/bin/avr-nm` (confirmed executable this session;
**not on `PATH`** — Pitfall 9).

| Symbol | Size (B) |
|---|---|
| `get_read_settling` | **110** |
| `get_read_strobe` | **110** |
| `get_address` | 90 |
| `get_algorithm` | 90 |
| `get_delay` | 90 |
| `get_flags` | 90 |
| `get_memory_size` | 90 |
| `get_chip_id` | 86 |
| `get_page_size` | 86 |
| `get_vpp_mv` | 86 |
| `get_pin_count` | **84** |
| **eleven-stub sum** | **1012** ✅ |

Sum command (this session's own aggregation, not a hand-add):
```bash
avr-nm --print-size --size-sort --radix=d .pio/build/uno/firestarter_uno.elf \
  | awk '$4 ~ /^get_(flags|memory_size|address|chip_id|pin_count|delay|vpp_mv|algorithm|read_settling|read_strobe|page_size)$/ {s+=$2} END {print s+0}'
# => 1012
```

Also recorded from the same dump: `key_parsers` (the PROGMEM table) **44 B** (11 × 4 B function
pointers), `jsoneq_` **108 B**, `simple_strtoul` **68 B**, and the dispatch-loop clone
`get_cmd.constprop.31` **102 B** — its numeric `.constprop` suffix is **explicitly not pinned**
(Pitfall 13: research's own `.31` moved to `.32` between its before and after trees).

**The load-bearing negative**, same ELF, same tool:
```bash
avr-nm --print-size --radix=d .pio/build/uno/firestarter_uno.elf \
  | grep -cE ' (get_r1|get_r2|get_rev|get_rw_pin|get_vpp_pin)$'
# => 0
```
`get_r1`, `get_r2`, `get_rev`, `get_rw_pin` and `get_vpp_pin` are **ABSENT** from the symbol
table — five structurally identical bodies, each called directly with a literal key, costing
**zero** because `extract_num` expands at the call site and gcc fully inlines them.

**C-2, re-confirmed this session:** the per-stub range is **84–110 B**, not the ROADMAP's
**86–110 B** — `get_pin_count` measures 84 B, below the stated floor. Every other figure in
ROADMAP criterion 1 is confirmed exactly: total 1012 B, ceiling 110 B
(`get_read_settling`/`get_read_strobe`), five siblings at zero.

**Why, so a later reader does not have to re-derive it:** `key_parsers[j].parser_func` is a
PROGMEM function pointer read with `pgm_read_ptr` and called through indirectly. gcc can neither
inline the callee nor constant-propagate the literal wire key into `jsoneq_` across that
indirection, so it must emit each stub with a full four-argument AVR ABI prologue for one
`simple_strtoul` call and one store — the opacity of the indirect call, not the logic inside the
stub, is what costs 84–110 B eleven times over.

---

## 4. The key-string duplication ledger

Uses the **offset-resolved block form**, never an exact-string count (C-3's own trap). `.text`
begins at file offset `0x94` = `148`, so `vaddr = fileoff − 148`.

```bash
strings -a -n 2 -t d .pio/build/uno/firestarter_uno.elf \
  | awk '{fo=$1; va=fo-148; if (va>=90 && va<=360) printf "fileoff=%d vaddr=%d %s\n", fo, va, $0}'
```

Two blocks, `uno`, each **118 B**:

| Block | vaddr range | Contents |
|---|---|---|
| 1 | **104–221** | the eleven named `key_*` PROGMEM arrays: `key_page_size` 104, `key_read_strobe` 114, `key_read_settling` 129, `key_algorithm` 149, `key_vpp_mv` 159, `key_pulse_delay` 166, `key_pin_count` 178, `key_chip_id` 188, **`key_flags` 196**, `key_address` 202, `key_mem_size` 210 |
| 2 | **226–343** | the anonymous `PSTR` duplicates emitted inside the eleven stubs — measured at vaddr 225 as `Uflags` (see below), 232 `memory-size`, 244 `address`, 252 `chip-id`, 260 `pin-count`, 270 `pulse-delay`, 282 `vpp_mv`, 289 `algorithm`, 299 `read-settling-delay`, 319 `read-strobe-us`, 334 `page-size` |

Cross-keyed against the symbol table (same session):
```bash
avr-nm --print-size --radix=d .pio/build/uno/firestarter_uno.elf | grep -E ' key_' | sort -n
# key_page_size 104 (10B), key_read_strobe 114 (15B), key_read_settling 129 (20B),
# key_algorithm 149 (10B), key_vpp_mv 159 (7B), key_pulse_delay 166 (12B),
# key_pin_count 178 (10B), key_chip_id 188 (8B), key_flags 196 (6B),
# key_address 202 (8B), key_mem_size 210 (12B) — all eleven present, block 1 confirmed
```

Repeated on `leonardo` — same two-block structure, offset by the different `.text` layout:
block 1 vaddr 172–278 (`page-size` 172 … `memory-size` 278), block 2 vaddr 293–357+
(`Uflags` at 293, `memory-size` 300, `address` 312, `chip-id` 320, `pin-count` 328,
`pulse-delay` 338, `vpp_mv` 350, `algorithm` 357).

**C-3, re-confirmed this session: eleven of eleven wire keys are stored twice today, not ten of
eleven.** `flags` is duplicated exactly like the other ten. The reason a naive count misses it is
a `strings` artifact: the byte immediately before the second copy is `0x55` (`'U'`), so `strings`
reports the token as **`Uflags`**, not `flags`.

**Both forbidden oracle forms, named with the numbers they wrongly report (measured this
session, not merely cited):**
```bash
strings -a -t d .pio/build/uno/firestarter_uno.elf | awk '$2=="flags"' | wc -l
# => 1   (truth is 2 — an exact-match filter drops the "Uflags"-mangled second copy)
strings -a .pio/build/leonardo/firestarter_leonardo.elf | grep -c flags
# => 4   (a substring grep over-reports — it also matches unrelated tokens containing "flags")
```
Both are **forbidden oracles for DECODE-02**. The only valid oracle is the offset-resolved block
dump above, cross-keyed against the symbol table, repeated per target — this is a **link-time
property**, not a source property, until plan 02's OD-3 (`get_flags` → `key_flags`) makes it one.

---

## 5. Test and gate baselines, on the clean committed tree

| Leg | Result | Wall time |
|---|---|---|
| `pio test -e native` | **172 test cases: 172 succeeded**, 17 suites | 54.57 s (this session's single run) |
| `pio test -e native_nodevtools` | **172 test cases: 172 succeeded**, 17 suites | 34.32 s (this session's single run) |
| `python3 -m pytest tests/ -q -o addopts=""` (`/workspaces/firestarter_app`, system `python3`) | **1976 passed, 0 failed, 0 skipped**, 32 syrupy snapshots | 237.56 s |
| `pio test -e native -f "*test_read_timing*"` | **9 test cases: 9 succeeded** | 3.01 s |

`test_read_timing`'s own case count is **9** — `RUN_TEST` entries at
`test/native/avr/test_read_timing/test_read_timing_params.cpp:544-553`, confirmed line-for-line
this session (`:185` through `:193`, one `RUN_TEST` per line).

**The lexical trap, reproduced exactly (Pitfall 7):**
```bash
grep -ro "RUN_TEST(" test/native/avr/{test_dispatch,test_not_implemented,test_messages,test_data_input,test_read_timing,test_cobs_data_frame,test_cobs_cmd_frame,test_frame_vectors,test_val_eprom,test_val_eeprom28c,test_val_nor_unlock,test_val_5v_page,test_val_flash_intel,test_val_sram,test_sdp_harness,test_eeprom28c_sdp,test_cmd_admission} | wc -l
# => 173, while the runner reports 172 for the identical 17-suite set
```
**Trust the runner, never the grep.**

**AVR build warnings and the size-gate rebuild** (via `scripts/check_build_warnings.py --rebuild`,
which cold-cleans all three AVR envs itself):
```
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0),
      leonardo: macro_redefinition=0 (== 0),
      native: total warnings observed=998 is 168 below watermark 1166 (INFO only),
      native_nodevtools: total warnings observed=998 is 168 below watermark 1166 (INFO only)
```
`macro_redefinition == 0` on all three AVR targets is this project's AVR warnings policy — **no
slack**. All three targets were rebuilt after this cold-clean and re-measured at the exact §2
figures (24234/1567, 24282/1573, 26378/2008) with `git status --porcelain` empty throughout.

**The four CI legs, exhaustively, re-verified this session:**
```bash
grep -rn 'pio test' .github/workflows/
#   build.yml:142       pio test -e native
#   build.yml:155       pio test -e native_nodevtools
#   beta-build.yml:122  pio test -e native
#   beta-build.yml:128  pio test -e native_nodevtools
grep -rn 'pytest tests' .github/workflows/
#   build.yml:161       pytest tests/ -v
#   beta-build.yml:134  pytest tests/ -v
grep -rn 'pio run' .github/workflows/ | grep -v '#'
#   build.yml:193       pio run
#   beta-build.yml:145  pio run
grep -rn check_size_baseline .github/
#   (no output)
```
`check_size_baseline.py` and `check_build_warnings.py` run in **NO CI workflow**. Every gate in
this phase beyond the four CI legs above is a **local-run obligation** (D-04's confirmation,
C-16).

**Native-suite flakiness (D-04):** this session's own runs (54.57 s for `native`, 34.32 s for
`native_nodevtools`) are single-run (N=1) figures. `157-RESEARCH.md`'s own session recorded three
`native` runs at 19.8 s, 25.3 s and 54.6 s — duration varied 2.8× while the 172/172 result did
not. Never treat a single run's exact wall time, or a future single-run count mismatch, as
evidence of a regression on its own.

---

## 6. Struct offsets, both architectures, and OD-7

Method: a generated TU of `char off_<m>[offsetof(firestarter_handle_t, m)+1];` for each member
plus `char total[sizeof(firestarter_handle_t)];`, compiled once with `avr-gcc -mmcu=atmega328p`
and once with host `gcc`/`g++`, offsets and the struct size read back from `nm --print-size`.

| member | AVR (this session) | native (this session) |
|---|---|---|
| `cmd` | 0 | 0 |
| `operation_state` | 1 | 1 |
| `response_code` | 2 | 2 |
| `protocol` | **3** | 4 |
| `pins` | 7 | 8 |
| `mem_size` | 8 | 12 |
| `address` | 12 | 16 |
| `vpp_mv` | 16 | 20 |
| `pulse_delay` | 18 | 24 |
| `read_settling_us` | 22 | 28 |
| `read_strobe_us` | 26 | 32 |
| `ctrl_flags` | **30** | 36 |
| `chip_id` | 34 | 40 |
| `page_size` | **36** | 42 |
| `data_buffer` | **38** | 44 |
| `data_size` | 550 | 556 |
| `bus_config` | 554 | 560 |

**Confirmed exactly:** the ROADMAP's "all eleven fields currently sit at offsets 3–37, below
`data_buffer` at 38" holds precisely on AVR — the eleven fields from `protocol` (3) through
`page_size` (36) are all below `data_buffer` (38). The native table differs at **every** field
from `protocol` down — a hand-written offset column would be correct on one architecture and
wrong on the other; the `offsetof`-derived table is DECODE-03's real value.

### OD-7 — the `sizeof(firestarter_handle_t)` discrepancy, discharged

**The real AVR compiler invocation for `src/json_parser.c`**, captured from `pio run -v -e uno`
after a targeted `pio run -t clean -e uno` to force recompilation:
```
avr-gcc -o .pio/build/uno/src/json_parser.c.o -c -std=gnu11 -fno-fat-lto-objects \
  -mmcu=atmega328p -Os -Wall -ffunction-sections -fdata-sections -flto \
  -DPLATFORMIO=60119 -DARDUINO_AVR_UNO -DMONITOR_SPEED=250000 -DHARDWARE_REVISION -DDEV_TOOLS \
  -DRURP_BOARD_NAME=\"uno\" -DSERIAL_ON_IO -DF_CPU=16000000L -DARDUINO_ARCH_AVR -DARDUINO=10808 \
  -Iinclude -Isrc -Ilib/jsmn/src \
  -I$HOME/.platformio/packages/framework-arduino-avr/libraries/EEPROM/src \
  -I$HOME/.platformio/packages/framework-arduino-avr/cores/arduino \
  -I$HOME/.platformio/packages/framework-arduino-avr/variants/standard \
  src/json_parser.c
```
Notably, **`DATA_BUFFER_SIZE` is not passed on `uno`** — `include/firestarter.h:16-17`'s
`#ifndef DATA_BUFFER_SIZE / #define DATA_BUFFER_SIZE 512` default applies (only `leonardo`
overrides it to 1024, per `platformio.ini:87`).

Re-deriving `sizeof(firestarter_handle_t)` with exactly the layout-affecting subset of those
flags (`-std=gnu11 -mmcu=atmega328p -Os` plus every `-D` and `-Iinclude`) against a
`char total[sizeof(firestarter_handle_t)];` probe:
```bash
$AVR_GCC -std=gnu11 -mmcu=atmega328p -Os -DPLATFORMIO=60119 -DARDUINO_AVR_UNO \
  -DMONITOR_SPEED=250000 -DHARDWARE_REVISION -DDEV_TOOLS -DRURP_BOARD_NAME=\"uno\" \
  -DSERIAL_ON_IO -DF_CPU=16000000L -DARDUINO_ARCH_AVR -DARDUINO=10808 -Iinclude -c off.c -o off.o
avr-nm --print-size --radix=d off.o | grep ' total$'
# => 00000601 00000601 C total
```

**Result: `sizeof(firestarter_handle_t)` is `601` B on AVR at this position — ONE number.**

**The discrepancy this closes:** `157-RESEARCH.md`'s own probe (a narrower flag set, without the
real `pio run -v` command as its source) measured **600** B; `155-after-figures.md` records
**601** B for the post-DEAD-01 handle. This session's re-derivation, using the actual captured
compiler invocation rather than a hand-assembled flag guess, measures **601** — matching
`155-after-figures.md` exactly, not `157-RESEARCH.md`'s 600. **601 B is the number this record
carries forward; 600 B is superseded.**

`157-RESEARCH.md`'s own Measured Figures section states the −5 B RAM delta is independently
confirmed by `ram_used` (`1567 → 1562` on `uno`, after the composed reference change) — that
figure is **cited from RESEARCH, not independently re-measured by this task**, because this
before-only plan makes no narrowing edit to test against. It is recorded here only to state that
the −5 B delta does not depend on which of 600/601 is correct.

**A further discrepancy found this session, beyond OD-7's scope (native, not AVR):**
`157-RESEARCH.md`'s Measured Figures table states `sizeof(firestarter_handle_t)` is **655** B on
native, before and after. This session measures **656** B, confirmed two independent ways:
```bash
gcc/g++ -std=gnu++17 -DMONITOR_SPEED=250000 -DHARDWARE_REVISION -DDEV_TOOLS \
  -DRURP_BOARD_NAME=\"native\" -Iinclude -c off.c -o off.o && nm --print-size --radix=d off.o | grep ' total$'
# => 0000000000001664 0000000000000656 B total
# and directly:
g++ ... sizecheck.cpp -o sizecheck && ./sizecheck
# => sizeof=656
```
**656 is the only value consistent with the struct's own layout.** `firestarter_handle_t` ends
with seven function-pointer members (`firestarter_operation_init` etc., `include/firestarter.h`
past `bus_config`), each 8-byte-aligned and 8 bytes wide on x86-64 — so the struct's alignment
requirement is 8, and its `sizeof` **must** be a multiple of 8. `656 = 82 × 8`; `655` is not
divisible by 8 and cannot be a valid `sizeof` for this struct under the standard x86-64 System V
ABI. This is recorded as an additional measured correction to `157-RESEARCH.md`'s own figures,
found at execution time (not one of the plan's pre-identified C-17/C-18/C-19), and does not
change AVR's OD-7 resolution or the −5 B RAM ceiling (which is stated as AVR-only regardless of
the native `sizeof` value).

---

## 7. Reference carriers

```bash
git rev-parse wip/v1.33-size-reduction-survey-preserved
```
`a6b46f8b12e81c62d9958945eb0bdbb8c16ae699` (abbreviates `a6b46f8`).

Extracted this phase's two subsets from `.planning/notes/firmware-size-reduction-measured.patch`
(705 lines total) per `157-RESEARCH.md`'s Code Examples:
- `sed -n '1,30p'` → `include/firestarter.h` subset (hunks 1 and 2 are Phase 157's; hunk 3 is
  Phase 155's and already landed)
- `sed -n '98,311p'` → `src/json_parser.c` subset

```bash
for c in 0 1 2 3; do git apply --check -C$c /tmp/157-json.patch; done
```
**All four FAIL**, identically:
```
error: patch failed: src/json_parser.c:76
error: src/json_parser.c: patch does not apply
```

```bash
patch -p1 --dry-run -F3 < /tmp/157-json.patch
```
```
checking file src/json_parser.c
Hunk #3 FAILED at 58.
Hunk #4 succeeded at 115 (offset -1 lines).
Hunk #5 succeeded at 290 (offset -1 lines).
Hunk #6 succeeded at 329 with fuzz 1 (offset -1 lines).
Hunk #7 succeeded at 341 with fuzz 2.
1 out of 7 hunks FAILED
```
Hunk **#3 alone** fails; #4–#7 succeed with offsets and (for #7) fuzz. **Nothing was applied** —
only `--check` and `--dry-run` were run — and `git -C firestarter status --porcelain` was
re-asserted empty immediately afterward, with no `.rej`/`.orig` file left anywhere under
`/workspaces/firestarter`.

**Why hunk #3 fails:** its removal lines include two provenance comments Phase 154's sweep
deleted from `src/json_parser.c` — a `-` line that no longer exists cannot be reconciled by
reducing context (`-C`), which is exactly Pitfall 1's shape.

**`157-RESEARCH.md`'s Phase 156 precedent does not generalise here (C-11):** Phase 156's own
subset applied clean with `git apply -C1`; Phase 157's subset fails at every `-C` level because
Phase 154's sweep rewrote `json_parser.c`'s comments (198 of 198 of that file's citations moved)
while leaving `eprom.cpp`/`flash_intel.cpp` byte-unchanged.

**Conclusion: plan 02's implementation is a hand-port. The patch is evidence that a reference
implementation exists and was built and measured, not a shortcut that can be applied.**

---

## 8. The one-sided size gate, and the pre-existing red

```bash
grep -n 'flash_delta > allowance\|ram_delta > ram_tolerance' scripts/check_size_baseline.py
```
`:697 if flash_delta > allowance:` and `:709 if ram_delta > ram_tolerance:` — both
strict-inequality, growth-only comparisons (D-03). A **reduction** in flash or RAM passes with
**no named exemption**. This phase's reduction is not yet a fact of the tree (this plan makes no
edit), but the policy's one-sidedness is recorded here so a later green run cannot be misread as
"nothing moved".

```bash
python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild
```
Output, verbatim (after the three per-env `pio run -t clean` steps the script runs itself):
```
FAIL:
  native: cases baseline=141 observed=172
  native_nodevtools: cases baseline=141 observed=172
```
**Exactly two lines, both native case counts — no AVR flash or RAM leg fails.** This is the
measured proof that the pre-existing BASE-01 red masks nothing (F-6): every AVR target still
passed its flash/RAM comparison; only the case-count leg, frozen at Phase 124's `141` against the
current `172`, fails.

```bash
grep -n '"cases"' scripts/baseline/size_baseline.json scripts/baseline/size_baseline_base01.json
```
`size_baseline.json`: `native_envs.native.cases` = **172**, `native_nodevtools.cases` = **172**.
`size_baseline_base01.json`: both = **141** (frozen at Phase 124).

**Handed forward, neither fixed here:** the cold re-anchor of `size_baseline.json` and the
BASE-01 native case-count mismatch both belong to **Phase 158 / LAND-01 and LAND-03**. This
plan's own new native cases (Wave 0 of plans 04/05) will move the `172` further before Phase 158
re-anchors — record the count at hand-off time, not here.

---

## 9. The honest coverage ceilings — stated, not implied

All ten appear in every plan of this phase, in every SUMMARY, and in the phase record.

1. **`src/json_parser.c` IS natively covered** (F-3) — `build_src_filter` includes
   `+<json_parser.c>`, and `test_read_timing` already drives `json_parse` against a real
   `jsmn_parse`. Every behavioural criterion in this phase is reachable by a native test **that
   CI runs**. **This phase has no coverage gap of Phase 155's kind, and this record must NOT
   borrow that phrasing** — the opposite is true of `src/json_parser.c` compared to
   `rurp_common.cpp`'s situation.
2. **`src/firestarter.cpp` and `src/eprom_operations.cpp` are OUTSIDE the native `src_filter`.**
   Between them they hold 8 of the 40 `is_flag_set` uses and the `eprom_block_budget_s` call.
   The narrowing's effect there is proven **only by compilation**, never by execution.
3. **`src/dev_tools.cpp` is outside too** — 9 `is_flag_set` uses plus 7 `LOG_INFO_ID*`
   expansions, the single largest concentration. Compile-only coverage.
4. **DECODE-01 and DECODE-02 have NO automated gate.** They are measurements recorded in
   `157-after-figures.md`. No test asserts that the ten deleted stubs stayed deleted or that a
   key is stored once. A future phase could silently reintroduce either. **Do not describe them
   as gated.**
5. **The −5 B RAM saving is unobservable natively** (`sizeof` is a fixed value either way on
   native — see §6's own found discrepancy: measured 656 B, not 655 B, but unchanged before vs.
   after regardless). AVR-only.
6. **Saturation-as-fail-closed is CONTINGENT on `0xFF` being unmapped** in `configure_memory`'s
   dispatch chain. That is a property of the **dispatch table**, not of `store_field`, it is
   true only today, and it is pinned by **no** test unless case S2 is written. Record it as
   contingent.
7. **`_Static_assert` proves the offsets fit `uint8_t` at build time — it does NOT prove the
   table writes the right member.** Only the native parse tests do that, and only for the fields
   they exercise (today `read_settling_us`, `read_strobe_us`, `page_size`; after this phase also
   `protocol`, `ctrl_flags` and the six round-trip fields OD-5 takes).
8. **No bench coverage, by design** (D-02). No criterion needs silicon; nothing here is claimed
   of real hardware.
9. **`check_size_baseline.py` and `check_build_warnings.py` are in NO CI workflow.** Every gate
   in this phase beyond the four CI legs (`pio test -e native`, `pio test -e native_nodevtools`,
   `pytest tests/`, `pio run`) is a **local-run obligation**. A green CI run is not evidence
   that the size gate passed.
10. **The reference patch does not apply cleanly** (C-11): hunk #3 fails at every `-C` level
    because Phase 154's sweep changed its context. The implementation is a hand-port, and the
    patch is evidence, not a shortcut.

---

## 10. The corrections index

| # | ROADMAP / REQUIREMENTS says | Measured this session (or at research time, carried here) | Carried forward by |
|---|---|---|---|
| C-1 | `json_parse_config` calls `get_flags` "directly at two sites" | `get_flags` is called once in `json_parse_config` (`:160`) and once in `json_get_cmd` (`:191`) — **two different functions**, not two sites in one | 02, 07 |
| C-2 | Per-stub cost is "86–110 B each" | **84–110 B** — `get_pin_count` measures 84 B, below the stated floor (§3, re-confirmed this session) | 01 (this file), 07 |
| C-3 | "Ten of eleven were stored twice" | **Eleven** of eleven, including `flags` (mangled to `Uflags` by a preceding `0x55` byte, which is why an exact-match filter misses it) (§4, re-confirmed this session) | 01 (this file), 02, 07 |
| C-4 | ROADMAP's split is "field table −976, narrowing + saturation −172" | Measured (research session, reference implementation built): **−890 B** (field table + saturation) / **−258 B** (narrowing) / **−5 B RAM**. The **total −1148 B is exact**; the attribution is not | 02, 03, 07 |
| C-5 | "19 protocol comparisons" and "45 `is_flag_set` call sites" | **18** protocol-keyed sites (17 `handle->protocol ==` + 1 `switch`), **20** total `->protocol` reads; **40** textual `is_flag_set` uses, **59** post-preprocessor uses (with `LOG_INFO_ID*` expansions). Neither 19 nor 45 is correct | 03, 07 |
| C-6 | DECODE-05's per-stub form "could not" saturate `pins`/`chip_id`/`vpp_mv`/`page_size` | Those four are already narrow today and already silently truncated by `extract_int`/`extract_long`; only `protocol` gains a genuinely new hole from narrowing, and `ctrl_flags` gains one too (C-7) that criterion 5 omits | 04, 07 |
| C-7 | (omission) | ⚠ **SAFETY DEFECT in the reference patch:** saturating `ctrl_flags` (a bitmask) to `0xFFFF` sets `FLAG_FORCE`/`FLAG_SKIP_ERASE`/`FLAG_SKIP_BLANK_CHECK` — fail-**open** in the phase whose headline is fail-closed. `ctrl_flags` must **mask**, not saturate (OD-1) | 02, 03, 04, 07 |
| C-8 | DECODE-06 "proven by a test" | `read-settling-delay`'s clamp IS tested today (`test_read_settling_us_capped_at_max`); **no** `read-strobe-us` cap test exists, and both existing assertions are `<=` not `==` | 05, 07 |
| C-9 | (implicit — the `#define` must move) | The `#define READ_TIMING_MAX_US` hoist above the table **is required** — confirmed by the reference build. **C-17 corrects its cited line: the `#define` sits at `:360`, not `:352`** (re-measured this session, see below) | 02, 07 |
| C-10 | DECODE-07 cites `uno` 25696 (switch) vs 25678 (if-chain) | Those absolutes are stale by **1444 B** at this position (`uno` is 24234 before this phase); the `switch` variant's delta at this position is **UNVERIFIED** — no one has built it here yet | 06, 07 |
| C-11 | (implicit — patch applies like Phase 156's) | The reference patch does **NOT** apply cleanly at this position: hunk #3 fails at every `-C` level (§7, re-confirmed this session); Phase 156's own precedent (`-C1` succeeded) does **not** generalise | 01 (this file), 02 |
| C-12 | (implicit — phase is firmware-only) | ⚠ With the reference change applied, one host gate (`test_page_size_key_string_matches_constants_py`) goes RED and a sibling (`test_every_dispatched_identifier_...`) goes silently **fail-open** (vacuous pass) — unless `key_parsers`'s identifier is **kept** (OD-2), which keeps the phase firmware-only with zero `firestarter_app` commits | 02, 07 |
| C-13 | Leonardo Caterina headroom after the phase is "3440 B" | **3442 B** (`28672 − 25230`, per the reference measurement) | 06, 07 |
| C-14 | Criterion 3's compile-time assertion "prevents a future struct reorder from silently truncating an offset" | The reference patch's single `_Static_assert` guards **`page_size` only** — a reorder moving e.g. `mem_size` below `data_buffer` would still pass it. **All eleven fields need their own guard** | 02, 07 |
| C-15 | (implicit — case count stays 172) | Adding native cases (DECODE-05/06, this phase's Wave 0) moves the count off 172, reddening both baseline gates' count legs — expected, a handoff to **LAND-01**, not a defect | 04, 05, 07 |
| C-16 | (implicit — some CI leg might run the size gate) | `check_size_baseline.py` runs in **NO CI workflow** — confirmed again this session (§5/§8) | 01 (this file), 07 |
| C-17 | RESEARCH cites `#define READ_TIMING_MAX_US` at `src/json_parser.c:47`, and its DECODE-01 table lists the first seven `key_*` PROGMEM lines one line high | Measured this session: `#define READ_TIMING_MAX_US` is at **`:360`**; `grep -n 'PROGMEM = "' src/json_parser.c` confirms `memory-size` `:51`, `address` `:52`, `flags` `:53`, `chip-id` `:54`, `pin-count` `:55`, `pulse-delay` `:56`, `vpp_mv` `:57`, `algorithm` `:58`, `read-settling-delay` `:60`, `read-strobe-us` `:61`, `page-size` `:66` — the DECODE-06 hoist requirement (C-9) is unaffected; only its source line moves | 02, 07 |
| C-18 | `157-VALIDATION.md`'s Wave-0 row says the RED-first capture is "narrowing applied with saturation/mask deleted → S1/S2/**S4** FAIL" | Wrong for S4: against that probe (narrowed `ctrl_flags`, no saturation) a wire `flags: 65536` truncates to `0`, so S4's `ctrl_flags == 0` assertion **passes vacuously**. S4's only non-vacuous negative is a **saturating** `ctrl_flags` tree (the reference patch verbatim), which stores `0xFFFF`. Two distinct probes are required; on today's un-narrowed tree (`uint32_t`), S4 is RED too (`flags: 65536` stores `0x10000`, no defined bit set) | 04 |
| C-19 | (implicit — the −890/−1148 figures apply unconditionally) | Those figures were measured on a reference table with **no per-row policy column**. OD-1 adds one (mask-vs-saturate per row), which costs bytes. A post-change figure that still reads **exactly** −1148 is the **suspicious** outcome, not the target — plans 02/03 must record what they actually measure | 02, 03 |

---

## 11. The seven settled decisions — OD-1 through OD-7

Each with what was decided, what was declined, and the declined alternative's cost.

- **OD-1 — out-of-range policy: saturate for ordinals, MASK for bitmasks, reject for nothing.**
  `ctrl_flags` masks (`v &= max`, preserving today's truncation), never saturates — saturating it
  to `0xFFFF` would set `FLAG_FORCE`, `FLAG_SKIP_ERASE` and `FLAG_SKIP_BLANK_CHECK` simultaneously
  (C-7), a fail-open regression in the phase whose headline criterion is fail-closed.
  **Declined: `reject`.** Rejecting an out-of-range command needs a **new message id**, which
  means editing `tools/catalog/messages.toml` in the **meta** repo and regenerating
  `include/messages.h` — codegen-generated, never hand-edited (`reference_firmware_messages_h`
  precedent). That is a **cross-repo codegen step**, which would break this phase's firmware-only
  property. The alternative's cost is recorded, not silently dropped.
- **OD-2 — the identifier `key_parsers` is KEPT.** Renaming it turns
  `firestarter_app/tests/test_json_key_parity.py::test_page_size_key_string_matches_constants_py`
  RED and makes its sibling leg (`test_every_dispatched_identifier_has_a_declared_key_string`)
  pass **vacuously** (an empty regex match is fail-open) — measured (research session): **3
  failures against a 24-passed baseline** (C-12/F-2). **Declined: renaming to something more
  accurate, e.g. `field_table`.** That costs a `firestarter_app` commit to fix the host-side
  regex and an explicit ROADMAP correction abandoning the "firmware-only" claim for this phase.
  Keeping the name costs nothing at build time, keeps the cross-repo gate honest, and keeps
  Phase 157 firmware-only with **zero** `firestarter_app` commits. **The record must state the
  identifier is now slightly stale** — after plan 02 it becomes a data table of
  `{key, clamp, offset, width}`, not a table of parsers — and this paragraph is why it was kept
  anyway.
- **OD-3 — `get_flags` is pointed at `key_flags` directly (~3 lines), making single-key-storage a
  source property.** Without this, `157-RESEARCH.md`'s own A6 records the `flags` string-dedup
  as a **toolchain outcome** it could not explain (moderate confidence risk). **Declined:
  depending on the toolchain to keep deduplicating `flags` indefinitely.** That leaves DECODE-02's
  single-storage claim un-provable by source inspection — this record's own §4 measured it as a
  link-time property, exactly the gap OD-3 closes.
- **OD-4 — DECODE-07's `switch` alternative is re-measured at this phase's final position, not
  quoted from the stale survey absolutes.** The ROADMAP's `25696` vs `25678` figures predate
  Phases 155 and 156 (which together moved `uno` by roughly 1444 B) — see C-10. **Declined:
  quoting the original absolutes as current.** That would misstate the delta's magnitude even if
  its sign were still correct; the record must carry both the original figure with its
  provenance **and** a fresh one built at this phase's position (plan 06's job).
- **OD-5 — take six additional store-round-trip cases** (`mem_size`, `address`, `pulse_delay`,
  `chip_id`, `vpp_mv`, `pins`), closing coverage ceiling 9 (a wrong `offsetof` in one row is the
  refactor's most plausible silent defect). **Declined: leaving those six fields with no native
  round-trip oracle.** The case count already moves for DECODE-05/06 (C-15), so six more cost
  nothing additional in gate terms — only the marginal authoring cost, which was judged worth
  paying.
- **OD-6 — run both `check_build_warnings.py` and `check_no_heap_or_64bit_symbols.py` explicitly,
  rather than assuming they stay green.** Confirmed this session: `check_build_warnings.py
  --rebuild` PASSes with `macro_redefinition=0` on all three AVR targets (§5). **Declined:
  inferring from the raw AVR `warning:` grep count (0) that both scripts would also pass.** The
  native macro-redefinition watermark (1166) has near-zero headroom (998 observed, 168 below);
  assuming rather than running risks silently crossing it.
- **OD-7 — `sizeof(firestarter_handle_t)` is re-derived from the real `pio run -v` compiler
  flags, yielding ONE number: `601` B on AVR** (§6). **Declined: quoting either the research
  probe's 600 B or `155-after-figures.md`'s 601 B without re-deriving.** Re-deriving from the
  captured invocation resolves the discrepancy in `155-after-figures.md`'s favor and additionally
  surfaced a second, previously-unflagged discrepancy on native (656 B measured vs. 655 B
  claimed) — see §6's closing paragraph.

---

## 12. The 999.35 / v1.28 non-additivity warning

`REQUIREMENTS.md`'s Backlog 999.35 entry states DECODE-01's field table is **superseded** if the
binary command protocol (v1.28) ever lands — the field table is the JSON-decode surface the
binary protocol would replace outright. **This phase's −1148 B and 999.35's own `leonardo`
figures (−3728 B / −512 B, cited from that backlog entry) are NOT additive.** If 999.35 is ever
taken, it must be **re-measured from the post-v1.33 position** before anyone quotes a combined
saving — quoting `−1148 − 3728` as a single number would double-count whatever this phase's field
table already removed. The operator ruled the binary command protocol **out of v1.33 scope** on
2026-08-22; this phase proposes no step toward it (a standing prohibition, see this plan's
frontmatter). Stated here because a reader of the figures records will not necessarily reach the
backlog entry that carries this caveat.

---

## Summary of what this record proves

- The tree was proven clean **before and after every measurement** (§1); no tracked file was
  edited; no throwaway worktree was created.
- All three AVR targets reproduce Phase 157's stated baseline exactly, **twice** in the same
  session (§2, §8): `uno` 24234/1567, `uno328pb` 24282/1573, `leonardo` 26378/2008; Leonardo
  headroom 2294 B.
- The eleven-stub ledger closes at **exactly 1012 B**, and the five zero-cost siblings are
  confirmed **absent** from the symbol table (§3) — DECODE-01's entire proof, measured directly.
- The key-string duplication is recorded as **two 118 B offset-resolved blocks** on both `uno`
  and `leonardo`, with both forbidden `strings` oracles named and their wrong numbers reproduced
  (§4) — DECODE-02's oracle, established correctly.
- Both architectures' struct offsets are **compiler-derived**, confirming the ROADMAP's AVR claim
  exactly and showing the native table diverges at every field from `protocol` down (§6).
- **OD-7 is discharged**: `sizeof(firestarter_handle_t)` is `601` B on AVR, re-derived from the
  real `pio run -v -e uno` compiler invocation, matching `155-after-figures.md` and superseding
  `157-RESEARCH.md`'s `600`. A further, previously unflagged discrepancy was found and recorded
  on native (656 B measured, not 655 B) — mathematically required by the struct's 8-byte
  alignment from its trailing function-pointer members.
- The pre-existing BASE-01 size-gate red is proven to **mask nothing**: the canonical
  `--policy merge05` invocation fails with exactly two lines, both native case counts, and no
  AVR flash or RAM leg (§8).
- The reference patch is proven **not to apply**: all four `git apply --check -C{0,1,2,3}` runs
  fail identically at `src/json_parser.c:76`, and `patch --dry-run -F3` fails hunk #3 alone while
  #4–#7 succeed with offsets (§7) — plan 02's implementation is a hand-port, confirmed.
- All nineteen corrections (C-1 through C-19) and all seven OD decisions are recorded here with
  their declined alternatives and those alternatives' costs (§10, §11), each stated as
  superseding the ROADMAP/REQUIREMENTS prose it corrects.
- This record — not `157-RESEARCH.md` or `157-VALIDATION.md` in isolation — is the authoritative
  before-position every Phase 157 delta from plans 02–07 must compute against.
