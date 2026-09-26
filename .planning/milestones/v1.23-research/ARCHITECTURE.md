# Architecture Research

**Domain:** Embedded two-repo firmware + host-CLI system — landing a fourth MCU board target (PY32F071xB, Cortex-M0+) and a host USB-DFU install path into a mature AVR-only architecture
**Researched:** 2026-07-30
**Confidence:** HIGH for the merge/conflict surface, the HAL boundary and the host seams (all read in the tree and empirically built/tested). MEDIUM for the flash-config design (a design proposal, not existing code). LOW-by-construction for anything about PY32F071 silicon — no PCB exists and none is claimed.

**Evidence labelling used throughout:** every structural claim is tagged **PROVEN** (read in a live tree, or measured by a build/test run performed during this research) or **PREDICTED** (inference from what was read). Commands and SHAs are given so each PROVEN claim is re-runnable.

---

## 0. Executive summary — the five findings that should shape the roadmap

1. **The rebase is not the risk. There are ZERO textual merge conflicts between `beta` and the py32 stack.** PROVEN: `git merge-tree --write-tree --messages beta feature/py32f071-release-assets` exits 0 with an empty conflict list, and the two branches' changed-file sets since the merge base are **completely disjoint** (46 files on `beta`, 22 on the py32 stack, intersection = ∅). A real `git merge` in a scratch worktree succeeded with no conflict markers.

2. **The real collision is semantic and invisible to git: `platform/py32f071/CMakeLists.txt` lines 46–47 name two files that no longer exist.** The merge base `a1953c2` (2026-06-18) predates v1.19 Phase 104's rename. The py32 CMake compiles `src/proms/flash_type_3.cpp` and `src/proms/flash_type_4.cpp`; `beta` has `src/proms/flash_nor_unlock.cpp` and `src/proms/flash_5v_page.cpp`. Git merges the CMake file cleanly (only one side touched it) and produces a tree whose ARM build **fails at CMake configure time**. PROVEN by path-validating the merged tree. This is the single highest-value item in the whole analysis, and it is a two-line fix.

3. **The hard acceptance constraint is already satisfied — measured, not argued.** PROVEN by building and testing the merged tree: Leonardo flash **26072 → 26016 B (−56 B)**, native suite **141/141** on both `native` and `native_nodevtools`, and with a correct merged sibling layout the **entire host suite is green (0 failures, 29 snapshots)** with all nine cross-repo source-scanning gates *running* (not skipped) plus 7 `tools/check_*`/`diff_db` gates passing. The one nuance: Uno **+22 B** and ATmega328PB **+28 B** — the constraint "flash budget must not grow" is technically violated on the two roomiest targets (≈8 KB headroom each) while the *tight* target improves.

4. **The only merge conflict anywhere in the five-branch inventory is `include/rurp_shield.h`, and it is between the py32 stack and PR #45 — not against `beta`.** PROVEN: `git merge-tree` of `agent/portability-macros` × `feature/common-vpp-calibration` reports `CONFLICT (content): include/rurp_shield.h`. This independently vindicates the "seam only, hand-authored" resolution: **do not merge PR #45 at all**. Hand-write a reduced `include/rurp_vpp.h` and add one `#include` line to the already-portability-modified header.

5. **Four documented premises are wrong in the tree and must be corrected before requirements are written** (details in §7): `agent/portability-macros` does **not** contain `rurp_platform.h`, `rurp_millis()`, board pin maps, or capability macros; `platform/py32f071/PORTING.md` does **not exist** on the live branch (it is only on the two CLOSED branches); `DATA_BUFFER_SIZE` is **512**, not 1024; and the live Leonardo headroom is **2656 B**, not 2992 B.

---

## 1. Standard Architecture — where the fourth target attaches

### System Overview (post-integration, as the tree actually resolves)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HOST  (firestarter_app, Python)                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  ┌─────────────┐  │
│  │cli_handlers  │  │ firmware.py  │  │  channel.py   │  │ database.py │  │
│  │ _BOARD_      │  │ flash_method │  │ BETA_ONLY_    │  │ DIP pin →   │  │
│  │ CHOICES      │  │ () dispatch  │  │ BOARDS gate   │  │ bus_config  │  │
│  └──────┬───────┘  └──┬────────┬──┘  └───────┬───────┘  └──────┬──────┘  │
│         │             │        │             │                 │         │
│         │      ┌──────┘        └──────┐      │                 │         │
│         │      ▼                      ▼      │                 │         │
│         │ _install_with_        _install_    │                 │         │
│         │ avrdude (VERBATIM)    with_dfu ────┘                 │         │
│         │      │                      │                        │         │
│         │      ▼                      ▼                        ▼         │
│         │  avr_tool.py          py32_dfu.py            serial_comm.py     │
│         │  (avrdude ladder)     (pyusb DFU 1.1/DfuSe)  (COBS + CRC8)      │
└─────────┼──────┼──────────────────────┼───────────────────────┼──────────┘
          │      │ serial bootloader    │ USB DFU               │ CDC/UART
══════════╪══════╪══════════════════════╪═══════════════════════╪══════════
          │      ▼                      ▼                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  FIRMWARE  (firestarter)                                                  │
│  ── PROTOCOL / ALGORITHM LAYER  (platform-independent, UNTOUCHED) ──────  │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ firestarter.cpp  eprom_operations  operation_utils  json_parser     │  │
│  │ proms/: memory.cpp (configure_memory ← handle->protocol)             │  │
│  │         eprom  eeprom_28c  flash_nor_unlock  flash_5v_page          │  │
│  │         flash_intel  sram  flash_utils  not_implemented             │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│  ── COMPAT / SEAM LAYER  (what this milestone lands) ───────────────────  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌────────────────────────┐   │
│  │rurp_platform_    │ │include/avr/      │ │ include/rurp_platform.h │   │
│  │compat.h  PROGMEM │ │pgmspace.h        │ │ RURP_DELAY_US/MS,       │   │
│  │pgm_read_* shims  │ │(#include_next    │ │ RURP_MILLIS/MICROS      │   │
│  │                  │ │ shadow, AVR)     │ │ per-platform            │   │
│  └──────────────────┘ └──────────────────┘ └────────────────────────┘   │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ include/rurp_shield.h — the LOGICAL HAL contract (40 rurp_* fns)    │  │
│  │  + NEW: include/rurp_vpp.h  (SEAM ONLY: caps, enums, MANUAL)        │  │
│  │  + NEW: config-storage backend hooks  (proposed, §4)                │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│  ── BOARD BACKENDS ────────────────────────────────────────────────────  │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────────────────┐   │
│  │ boards/uno_  │ │ boards/      │ │ platform/py32f071/             │   │
│  │ rurp_shield  │ │ leonardo_    │ │  include/Arduino.h  ← THE SHIM │   │
│  │ boards/rurp_ │ │ rurp_shield  │ │  src/py32f071_rurp_shield.cpp  │   │
│  │ common.cpp   │ │              │ │  timing.cpp usb_cdc.c config   │   │
│  │ EEPROM.h     │ │              │ │  CMakeLists (own source list!) │   │
│  └──────────────┘ └──────────────┘ └────────────────────────────────┘   │
│      PlatformIO / avr-gcc                    CMake / arm-none-eabi-gcc    │
└──────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Status after this milestone |
|-----------|----------------|------------------------------|
| `src/proms/*`, `src/*.cpp` (protocol layer) | PROM algorithms, command dispatch on `handle->protocol` | **UNMODIFIED.** PROVEN: the py32 stack changes zero files under `src/`. |
| `include/rurp_shield.h` | The logical HAL contract — 40 `rurp_*` declarations + logical control identifiers (`LEAST_SIGNIFICANT_BYTE 0x01`, `OUTPUT_ENABLE 0x04`, `CONTROL_REGISTER 0x08`, `CHIP_ENABLE 0x20`) | **MODIFIED** (portability branch: 4 macros → `static inline`, `<avr/pgmspace.h>` → `rurp_platform_compat.h`, typed no-op `rurp_set_programmer_mode`). |
| `include/rurp_platform_compat.h` | AVR program-memory vocabulary (`PROGMEM`, `PGM_P`, `PSTR`, `pgm_read_*`, `*_P` string fns) neutralised on unified-address-space targets | **NEW** (71 lines on the portability branch, 86 after the py32 branch adds `pgm_read_ptr`, `strncpy_P`, `strncmp_P`, `sprintf_P`). |
| `include/avr/pgmspace.h` | `#include_next` shadow so headers that still say `#include <avr/pgmspace.h>` resolve on ARM | **NEW**, 15 lines. Empirically verified to chain correctly on AVR (§3.3). |
| `include/rurp_platform.h` | Platform identification + `RURP_DELAY_US/MS`, `RURP_MILLIS/MICROS` | **NEW** — but on the **py32 branch**, not the portability branch, and with **zero common-code consumers** (§3.1). |
| `platform/py32f071/include/Arduino.h` | The load-bearing seam: a fake Arduino core (`delay`, `delayMicroseconds`, `millis`, `micros`, `byte`, `HIGH`/`LOW`, `Serial`) | **NEW.** This — not `rurp_platform.h` — is how common code compiles for ARM. |
| `platform/py32f071/src/py32f071_rurp_shield.cpp` | The ARM board backend: GPIO bus, control pins, ADC | **NEW**, 317 lines. Implements 11 `rurp_*` functions incl. `rurp_read_vcc_mv`/`rurp_read_voltage_mv` (which on AVR live in the *excluded* `src/boards/rurp_common.cpp`). |
| `platform/py32f071/src/config.cpp` | Runtime-only config; **duplicates** `rurp_validate_config` policy | **NEW** — and the thing §4 replaces with a backend seam. |
| `platform/py32f071/CMakeLists.txt` | Second, independent build system with its **own hand-maintained source list** | **NEW.** This is the structural liability (§3.4). |
| `firestarter_app/firestarter/py32_dfu.py` | Pure-Python DFU 1.1 + DfuSe over pyusb; Intel-HEX/bin loader; flash-envelope guard | **NEW**, 832 lines + 654 lines of tests. |
| `firestarter_app/firestarter/channel.py` | Release-channel gate; `BETA_ONLY_BOARDS = ("py32f071",)` | **NEW**, 81 lines. |
| `firestarter_app/firestarter/firmware.py` | `flash_method()` board→flasher dispatch, `asset_candidates()`, `_install_firmware()`, `board_explicit` conflict refusal | **MODIFIED**, +246/−33. `_install_with_avrdude` body **untouched**. |

---

## 2. THE REBASE / MERGE SURFACE — the central question, answered with evidence

### 2.1 Branch inventory, re-measured 2026-07-30

All six branches share **one** merge base: `a1953c2` — *"Apply automatic changes"*, **2026-06-18** (v1.13-close era).

| Branch | PR | Head | ahead | behind | Verdict |
|---|---|---|---|---|---|
| `agent/portability-macros` | — (base of #48) | `52d6c1f` | 5 | 72 | LAND FIRST |
| `agent/py32f071-toolchain` | **#48 open draft** | `e5abb51` | 52 | 72 | LAND SECOND |
| `feature/py32f071-release-assets` | — | `ad47c3b` | **53** | 72 | **the actual integration source** — #48 + the asset-naming commit |
| `feature/common-vpp-calibration` | #45 closed | `a47228d` | 10 | 72 | CHERRY-PICK NOTHING; hand-author the seam (§5) |
| `feature/py32f071-full-support` | #47 closed | `cc4a815` | 45 | 72 | DO NOT USE (weak-stub USB) — but it holds `PORTING.md` |
| `feature/py32f071-toolchain` | #46 closed | `2c2ed10` | 11 | 72 | superseded; also holds `PORTING.md` |

PROVEN via `git merge-base` + `git rev-list --count` in `/workspaces/firestarter`. The "72 behind" figure is confirmed (the branch-state note's "27 behind" is stale by 45 commits — that note was written 2026-07-28, before v1.22 Phases 119–122 landed).

**Scope correction worth carrying into requirements:** those 72 commits are **not** "the whole v1.22 milestone". The merge base is 2026-06-18, so the beta side spans **v1.14 through v1.22** — eight milestones, including v1.19's Phase-104 handler renames (which cause finding #2) and v1.20's `mem_type`-axis removal.

### 2.2 Textual conflicts: none

```
$ git merge-tree --write-tree --messages beta feature/py32f071-release-assets
0367a54853f5828e5452f489a8fd7714994c74b8
                                            ← empty conflict list, exit 0
$ git merge-tree --write-tree --messages beta origin/agent/portability-macros
39ee91a06f07655c67385453c8b739ad025f3fb3    ← exit 0
```

**PROVEN.** Confirmed by executing the merge for real in a scratch worktree (`git merge feature/py32f071-release-assets` onto `beta` — clean).

**Why:** the changed-file sets are disjoint.

```
$ comm -12 <(git diff --name-only a1953c2..beta | sort) \
           <(git diff --name-only a1953c2..feature/py32f071-release-assets | sort)
(empty)
```

The py32 stack's 22 files are: `.github/workflows/py32f071.yml`; 6 headers (`include/avr/pgmspace.h`, `include/boards/py32f071_rurp_shield.h`, `include/rurp_platform.h`, `include/rurp_platform_compat.h` — all new — plus edits to `include/rurp_serial_utils.h` and `include/rurp_shield.h`); and 15 files under `platform/py32f071/`. **`beta` touched none of them** — critically, `include/rurp_shield.h` and `include/rurp_serial_utils.h` are byte-identical between `a1953c2` and `beta` (PROVEN: `git diff --quiet` returns 0).

Corollary: the v1.22 hot files named in the brief — `src/proms/eeprom_28c.cpp` (+619), `include/flash_utils.h`, `src/proms/flash_utils.cpp`, `src/operation_utils.cpp` (+81), `include/firestarter.h` (+80), `include/messages.h` (+12), `src/proms/memory.cpp` (+57) — are all **beta-side-only**. Zero conflict exposure.

### 2.3 Ranked real collisions

| # | Rank | Collision | Class | Detection | Evidence |
|---|------|-----------|-------|-----------|----------|
| **C-1** | **BLOCKER** | `platform/py32f071/CMakeLists.txt:46-47` names `src/proms/flash_type_3.cpp` / `flash_type_4.cpp`; `beta` has `flash_nor_unlock.cpp` / `flash_5v_page.cpp` | Stale source list — git-invisible | ARM CMake **configure** failure | **PROVEN**: path-validated the merged tree; 2 of 16 paths MISSING, 14 OK |
| **C-2** | **HIGH** | `include/rurp_shield.h` — the **only** textual conflict in the inventory, and it is py32-stack × **PR #45** | Content conflict | `git merge-tree` CONFLICT | **PROVEN**: `git merge-tree --messages origin/agent/portability-macros origin/feature/common-vpp-calibration` → `CONFLICT (content)`, exit 1 |
| **C-3** | **MEDIUM** | `.github/workflows/py32f071.yml` triggers only on `pull_request` + `workflow_dispatch`. Once merged to `beta`, **nothing validates the ARM build on a `beta` push** | Silent coverage loss | none — fails open | **PROVEN**: read lines 19–27 of the workflow |
| **C-4** | **MEDIUM** | `beta-build.yml:92` releases `files: .pio/build/**/firestarter_*.hex`. The CMake image lands in `build/py32f071/`, outside that glob | Release-asset gap | Missing release asset (silent) | **PROVEN**: read `beta-build.yml:90-92` |
| **C-5** | **LOW-MED** | Uno **+22 B**, ATmega328PB **+28 B** flash growth from the macro→`static inline` change | Budget-constraint breach (nominal) | size report | **PROVEN**: measured, §3.5 |
| **C-6** | **LOW** | The py32 CMake omits `src/dev_tools.cpp` and does not define `DEV_TOOLS` or `HARDWARE_REVISION`, so `CMD_DEV_*` and `CMD_HW_VERSION` return `MSG_ERR_UNKNOWN_CMD` on py32 | Capability asymmetry, not a build break | Host `dev`/`hw` command failure | **PROVEN**: all four call-site families verified `#ifdef`-guarded (`firestarter.cpp:38-40,266-278`; `hardware_operations.cpp:19`; `eprom.cpp:211`; `flash_intel.cpp:28`; `rurp_register_utils.h:47`) |
| **C-7** | **INFO** | `include/avr/pgmspace.h` becomes an 8th copy of a shim that already exists 7× under `test/native/avr/*/avr/pgmspace.h` | Duplication / future drift | none | **PROVEN**: 7 copies enumerated on `beta`, contents read |

**Nothing else collides.** Specifically checked and cleared:

- **Symbol completeness.** All 40 `rurp_*` declarations in the merged `rurp_shield.h` resolve: 11 in `py32f071_rurp_shield.cpp`, 4 in `config.cpp`, 6+ log/comm fns in the compiled `src/boards/rurp_serial_utils.cpp`, 8 as new `static inline` in the header itself, 2 in `rurp_register_utils.h`, and 4 `#ifdef HARDWARE_REVISION`-guarded out. PROVEN by declaration/definition extraction.
- **No new common source files.** `src/` at `a1953c2` and at `beta` have identical membership *except* the two renames — so C-1 is the complete source-list delta. PROVEN.
- **`src/boards/rurp_common.cpp`, `src/rurp_config_utils.cpp`, `include/rurp_types.h`** are all **byte-identical** between `a1953c2` and `beta`. PROVEN (`git diff --stat` empty). The PR #45 / White-Box-Calibration collision documented in PROJECT.md is therefore a **future-milestone** collision, **not** a rebase collision.
- **Host-side gates.** The merge modifies only `rurp_shield.h` and `rurp_serial_utils.h`. `test_revision_constants_parity.py` keys on `firestarter/include/rurp_shield.h:25-31` — PROVEN byte-identical at lines 20–40 after the merge. Every other gate scans `eeprom_28c.cpp`, `memory.cpp`, `firestarter.h`, `json_parser.c`, `rurp_pinout.h`, `logging_id.h` — all untouched.
- **Host repo merge.** `git merge-tree --messages beta feature/py32f071-fw-install` → exit 0; auto-merges `cli_handlers.py` and `pyproject.toml`, no conflicts. Merge base `1bb5599` (2026-07-28); 3 ahead / 79 behind. PROVEN.

### 2.4 Merge vs rebase

**Recommendation: `--no-ff` merge, not rebase.** Rationale, in order of weight:

1. A merge is PROVEN clean end-to-end. A 53-commit rebase replays each commit against a tree eight milestones newer; commits `04fd9b3`-era intermediate states may reference `flash_type_3.cpp` and will trip C-1 **53 times instead of once**.
2. `feature/py32f071-release-assets` is `agent/py32f071-toolchain` + one commit, and PR #48 is stacked on `agent/portability-macros`. Rebasing rewrites the SHAs of an **open PR's** base, orphaning #48's review history.
3. Two merges in sequence (`agent/portability-macros`, then `feature/py32f071-release-assets`) give the roadmap two natural phase boundaries with independent verification gates. PROVEN: the portability half merges cleanly on its own and the AVR builds are green after it.

**Load-bearing ordering inside the merge:** the C-1 CMake fix must be a **task in the same phase as the merge**, committed as a follow-up on the milestone branch. Merging without it leaves `beta`'s ARM target un-buildable — and because `py32f071.yml` does not run on push (C-3), nothing would tell you.

---

## 3. The HAL boundary as it actually exists

### 3.1 What `agent/portability-macros` really contains (4 files, 123 insertions)

**PROVEN by reading the full diff `a1953c2..origin/agent/portability-macros`.** It contains exactly:

1. `include/rurp_platform_compat.h` (new, 71 lines) — `PROGMEM`/`PGM_P`/`PSTR`/`pgm_read_{byte,word,dword}`/`memcpy_P`/`strcpy_P`/`strlen_P`/`strcmp_P`/`F()` neutralised on non-AVR.
2. `include/avr/pgmspace.h` (new, 15 lines) — `#include_next` on AVR, forward to the compat header otherwise.
3. `include/rurp_serial_utils.h` — `<avr/pgmspace.h>` → `"rurp_platform_compat.h"`; removes a duplicate `#include "firestarter.h"`; adds a trailing newline.
4. `include/rurp_shield.h` — same include swap; converts `rurp_chip_{enable,disable,output,input}` and `rurp_set_chip_{enable,output}` from function-like macros to `static inline` functions; converts the non-`SERIAL_ON_IO` `rurp_set_{programmer,communication}_mode` from `((void)0)` macros to typed inline no-ops; moves the `rurp_set_control_pin` declaration above its users.

**It does NOT contain** — and the roadmap/PROJECT.md description must be corrected:

| Claimed on the branch | Reality |
|---|---|
| `include/rurp_platform.h` with normalized platform identifiers | **Not present.** It is added by the **py32 toolchain** branch (51 lines). |
| `rurp_millis()` / `rurp_delay_ms()` / `rurp_delay_us()` so common code never calls Arduino timing APIs | **Not present, and the strategy is the opposite** (§3.2). |
| Board-local physical pin maps behind platform-independent logical identifiers | **Not present.** `include/rurp_pinout.h` is untouched by *both* branches; the logical identifiers (`LEAST_SIGNIFICANT_BYTE`, `OUTPUT_ENABLE`, `CONTROL_REGISTER`, `CHIP_ENABLE`) pre-date the branch. |
| Compile-time capability macros to exclude facilities small AVR builds lack | **Not present.** The only capability-style macros in the inventory are `RURP_HAS_VPP_DAC`/`RURP_VPP_DAC_BITS` on PR #45. |

### 3.2 Is the boundary sound? — Yes in effect, no in name

**PROVEN: `include/rurp_platform.h` has zero common-code consumers.** Its only includers are `include/boards/py32f071_rurp_shield.h:7`, `platform/py32f071/include/Arduino.h:9`, and `platform/py32f071/src/usb_cdc.c:7` — all py32-local. `RURP_DELAY_US`/`RURP_MILLIS` appear nowhere in `src/` or the common headers.

The actual mechanism is an **Arduino-compatibility shim**: `platform/py32f071/include/Arduino.h` (76 lines) supplies `delay()`, `delayMicroseconds()`, `millis()`, `micros()`, `byte`, `HIGH`/`LOW`, and a `Py32SerialPort Serial` object, implemented over `RURP_*`. The ten common TUs that `#include <Arduino.h>` keep doing so and resolve to the shim via `-I platform/py32f071/include`.

**This is the right trade for THIS milestone and the wrong long-term boundary.**

- *Right now:* zero churn in the protocol layer ⇒ golden register traces, the dispatch-mirror guard and the AVR flash budget are structurally protected. That is exactly why finding #3 came out green.
- *Long-term:* the seam is "a fake Arduino", not a named HAL. `PORTING.md`'s acceptance item *"Arduino timing calls are removed from common code"* is **UNSATISFIED**, and the branch chose a different strategy rather than failing to finish. The roadmap should record that as a **deliberate deviation**, not a defect — and should NOT schedule the call-site sweep this milestone (it would touch every `src/proms/*.cpp`, i.e. every golden trace, for zero functional gain).

### 3.3 What still leaks across the boundary

PROVEN by grepping `beta`'s common `src/` + `include/` (excluding `boards/uno*`, `boards/leonardo*`):

| Leak | Location | Absorbed by | Residual risk |
|---|---|---|---|
| `#include <Arduino.h>` in **10 common TUs** | `firestarter.cpp:10`, `hardware_operations.cpp:3`, `operation_utils.cpp:10`, `dev_tools.cpp:11`, `proms/{eeprom_28c,eprom,flash_5v_page,flash_intel,flash_nor_unlock,flash_utils,memory}.cpp:9-10` | the py32 `Arduino.h` shim | Any new Arduino API used in common code silently breaks the ARM build until added to the shim |
| `#include <avr/pgmspace.h>` still **unconditional in 4 headers** | `frame_vectors.h:24`, `messages.h:25`, `rurp_serial_utils.h:5`, `rurp_shield.h:18` | `include/avr/pgmspace.h` shadow. *Note:* the portability branch fixed only the latter two; `frame_vectors.h` and the **codegen-generated** `messages.h` still say `<avr/pgmspace.h>` and survive **only** because of the shadow | If the shadow is ever removed, ARM breaks. `messages.h` cannot be hand-fixed — it is generated from `tools/catalog/messages.toml` in the meta repo |
| `#include <Arduino.h>` in `include/rurp_hw_rev_utils.h:9` | header | shim + `#ifdef HARDWARE_REVISION` | none today |
| **Raw AVR register write in a common header**: `PORTD = 0;` | `include/rurp_register_utils.h:79` | `#if defined(ARDUINO_AVR_UNO) \|\| defined(ARDUINO_AVR_ATmega328PB)` | none — correctly guarded (PROVEN) |
| **Arduino pin macro in a common header**: `#define PIN_VPP_VOLTAGE_ADC A2` | `include/rurp_pinout.h:43` (also `PIN_HW_REVISION_DETECT_ADC A3`) | nothing. `A2`/`A3` are **not** defined by the py32 shim | **The sharpest latent leak.** It survives only because every referencing TU (`boards/rurp_common.cpp`, `rurp_hw_rev_utils.h`) is excluded or `HARDWARE_REVISION`-guarded on py32. The moment a common TU references `PIN_VPP_VOLTAGE_ADC`, the ARM build breaks. **PREDICTED** consequence; **PROVEN** premise (macro is unguarded; referencing TUs are excluded) |
| `#include <EEPROM.h>` + `EEPROM.get/put` | `src/rurp_config_utils.cpp:9,24,29` | whole-TU exclusion + reimplementation in `platform/py32f071/src/config.cpp` | This is the §4 problem |

**The `#include_next` shadow works — empirically verified, not assumed.** Direct preprocessor trace with `avr-g++ -E -H -I include`:

```
. include/avr/pgmspace.h
.. /home/vscode/.platformio/packages/toolchain-atmelavr/avr/include/avr/pgmspace.h
```

**PROVEN**: the project header shadows the toolchain header on AVR *and* correctly chains to it. This changes every AVR TU's include graph, which is why §3.5's size measurement is load-bearing rather than a formality. It is fragile in one specific way: `#include_next` is a GNU extension whose behaviour depends on `-I` ordering; a future PlatformIO/toolchain change that emitted `-isystem` for `include/` could break it. Worth a one-line comment in the file, not a phase.

### 3.4 Is the boundary complete? — One structural gap: the second source list

`platform/py32f071/CMakeLists.txt:36-53` hand-maintains `FIRESTARTER_COMMON_SOURCES`. PlatformIO globs `src/`; CMake enumerates. **Every future add/rename/delete under `src/` must be mirrored by hand, and only the ARM job notices — and per C-3 that job does not run on `beta` pushes.** C-1 is the first instance; it will not be the last.

**Recommended mitigation (cheap, and it belongs in this milestone):** a `tools/check_py32_sources.py`-style gate that parses `FIRESTARTER_COMMON_SOURCES` and asserts (a) every listed path exists, and (b) the listed set equals `src/**/*.{cpp,c}` minus an explicit, commented `PY32_EXCLUDED` allow-list (`src/dev_tools.cpp`, `src/rurp_config_utils.cpp`, `src/boards/uno_rurp_shield.cpp`, `src/boards/leonardo_rurp_shield.cpp`, `src/boards/rurp_common.cpp`). This converts a class of silent ARM breakage into a fast, hardware-free failure — and it is the same fail-closed pattern the nine existing cross-repo gates already use.

### 3.5 The hard acceptance constraint — measured

Executed during this research on the merged scratch worktree.

| Target | `beta` baseline | Merged | Δ | Verdict |
|---|---|---|---|---|
| **leonardo** flash | 26072 B (90.9 %) | **26016 B (90.7 %)** | **−56 B** | PASS — headroom **2600 → 2656 B** |
| leonardo RAM | — | 2014 / 2560 B (78.7 %) | — | unchanged |
| **uno** flash | 23932 B (74.2 %) | 23954 B (74.3 %) | **+22 B** | nominal breach; 8302 B headroom |
| **uno328pb** flash | 23976 B (74.0 %) | 24004 B (74.1 %) | **+28 B** | nominal breach; 8380 B headroom |
| `pio test -e native` | — | **141/141 PASSED** | — | PASS |
| `pio test -e native_nodevtools` | — | **141/141 PASSED** | — | PASS |
| host suite (merged sibling layout, both repos merged) | 0 failures | **0 failures, 29 snapshots**, all firmware gates *ran* | — | PASS |
| `check_dispatch` · `check_is_memory_cmd_no_ifdef` · `check_no_log_in_sdp_window` · `check_sdp_capability_invariants` · `check_devtest_orchestrator` · `check_no_community_support_status_write` · `diff_db` | — | **7/7 PASS** | — | PASS |

**All PROVEN.** Two methodological notes the roadmap should reuse:

- **The sibling layout matters.** Run from a scratch path, 11 firmware-scanning host tests **SKIP** with *"firestarter firmware checkout absent"* — a false green. The verification gate must place the merged app at a directory literally named `firestarter_app` with a merged `firestarter` sibling. Only then do the nine gates actually execute.
- **Two host failures are path artifacts, not merge breakage.** `test_gen_validation_header.py::test_validate_spec_called_before_emission` and `test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing` hardcode a `firestarter_app`-named directory. PROVEN identical on a **pristine `beta`** worktree at the same scratch path. Do not chase them.

**Constraint wording correction for requirements:** "the AVR flash budget must not grow" is violated by +22/+28 B on the two Uno-class targets. Either restate as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B"*, or accept and record. Do **not** write an acceptance criterion that the measured tree already fails — and note the headroom figure is **2656 B**, not 2992 B (that number pre-dates Phase 119's +392 B).

---

## 4. Flash-persistent config for a part with no EEPROM

### 4.1 What exists today

**AVR** — `src/rurp_config_utils.cpp` (40 lines) conflates three concerns:

```c
#define CONFIG_START 48
rurp_configuration_t rurp_config;                 // (1) singleton storage
rurp_configuration_t* rurp_get_config()       { return &rurp_config; }
void rurp_load_config()  { EEPROM.get(CONFIG_START, *config);         // (3) BACKEND
                           rurp_validate_config(config); }            // (2) POLICY
void rurp_save_config(c) { EEPROM.put(CONFIG_START, *c); }            // (3) BACKEND
void rurp_validate_config(c) { if (strcmp(c->version, CONFIG_VERSION)) { ... } }  // (2)
```

**PY32 (PR #48)** — `platform/py32f071/src/config.cpp` (47 lines) **re-implements all three**, and has already **drifted from AVR policy**: it adds an `|| value->r2 == 0` condition, `memset`s the whole struct, sets `hardware_revision = 0xFFU` (vs AVR's `0xFF`), and its `rurp_save_config()` writes to a RAM global and **persists nothing**. PROVEN by reading both files.

That drift is the argument for the design below: duplicating policy per platform means the AVR and ARM defaults diverge silently, and there is no test that would notice.

### 4.2 Where the seam should sit

**Split by concern, not by platform. Policy stays common; only the byte-blob backend is per-platform.**

```
include/rurp_config_storage.h              NEW — the backend contract, 2 functions
    bool rurp_config_storage_read (void* dst, size_t len);   // false = no valid record
    bool rurp_config_storage_write(const void* src, size_t len);

src/rurp_config_utils.cpp                  MODIFIED — keeps the singleton + policy;
                                           EEPROM.h/EEPROM.get/put REPLACED by the
                                           two hooks. rurp_validate_config UNCHANGED.

src/boards/rurp_config_storage_eeprom.cpp  NEW (AVR) — pure MOVE of EEPROM.get/put
                                           at CONFIG_START 48. Zero behaviour change.

platform/py32f071/src/config_storage_flash.cpp
                                           NEW (ARM) — dual-slot CRC32 records.
                                           config.cpp shrinks to nothing / is deleted.

test/native/.../config_storage_fake.cpp    NEW — RAM/array-backed backend for the
                                           native suite.
```

**Why the SCHEMA stays untouched — the key architectural point.** `PORTING.md`'s record wrapper **embeds** `rurp_configuration_t`; it does not extend it:

```c
struct StoredConfiguration {
    uint32_t magic;  uint16_t version;  uint16_t length;
    rurp_configuration_t configuration;      /* ← embedded verbatim */
    uint32_t sequence;  uint32_t crc32;
};
```

Magic / record-version / length / sequence / CRC are **storage-layer** metadata living outside the struct. Therefore: **no `rurp_configuration_t` field is added, no `CONFIG_VERSION` bump, no EEPROM migration** — all of which belong to the queued White-Box Voltage Calibration milestone and must not be pre-empted. PROVEN safe: the AVR record layout at `CONFIG_START 48` is unaffected because the AVR backend keeps using raw `EEPROM.get/put` on the bare struct; only the *py32* backend wraps it. (If a future milestone wants the wrapper on AVR too, that is a `CONFIG_VERSION` bump and it is that milestone's call.)

**Deliberately excluded from this milestone:** the `int32_t vpp_gain_ppm` / `vpp_offset_mv` / four `vpp_cal_*` fields that PR #45 commit `768580f` adds to `rurp_configuration_t` (+16 B of the 2048/2560 B AVR RAM) together with its `CONFIG_VERSION "VER06" → "VER07"` bump. PROVEN read; PROVEN out of scope.

### 4.3 Wear and atomicity with two slots

Design (PREDICTED — proposal, not existing code):

- **Two records in two distinct erase units.** Slot A and slot B must be in **different flash pages**, because erase granularity is a page. *The PY32F071xB page/sector size is a datasheet parameter that must be read from the Puya reference manual before the linker script is edited — the branch states it nowhere (PROVEN: no `FLASH_PAGE`/`SECTOR`/`erase` token anywhere under `platform/py32f071/`).* Do not guess it.
- **Load:** read both; validate `magic` + `length` + `crc32`; take the valid record with the **highest `sequence`**; if neither is valid, fall through to `rurp_validate_config`'s defaults.
- **Save:** write into the slot **not** currently holding the winner, with `sequence = winner.sequence + 1`. Erase-then-program that slot only.
- **Atomicity:** an interrupted write leaves the *other* slot untouched and still highest-valid-but-one ⇒ the previous configuration remains usable. This satisfies `PORTING.md`'s *"A failed or interrupted write must leave the previous record usable."*
- **Wear:** config writes are operator-initiated calibration events (single digits per board lifetime), so a monotonic `sequence` with alternating slots is ample; ping-pong halves per-page cycles. No wear-levelling ring is warranted — recommend explicitly declining one.
- **Wraparound:** `uint32_t sequence` will not wrap in practice; still, compare with signed subtraction (`(int32_t)(a - b) > 0`) so it degrades gracefully rather than inverting.

**Linker-script consequence (PROVEN gap):** `platform/py32f071/linker/PY32F071xB_FLASH.ld:5` declares `FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 128K` — the **entire** flash, with **no reservation** for config slots and **none for a bootloader**. Two carve-outs are needed and they are cheap now / expensive after layout:

1. Two config pages at the **top** of flash, with symbols the backend links against, and `LENGTH` reduced accordingly.
2. A bootloader region at the **base** if the self-flash route (the seed's primary choice) is taken — which also means the application's vector table must be relocated. **Record this in the flash-budget/PCB decision this milestone even though the bootloader is not built here.** `py32_dfu.py` already hardcodes `FLASH_BASE = 0x08000000` / `FLASH_SIZE = 128 * 1024` as its envelope guard, so both host and linker must move together.

### 4.4 Native testability with no hardware

The backend-as-linker-seam makes the whole thing testable in the existing `pio test -e native` harness — no ARM, no board:

| Test | Setup | Assert |
|---|---|---|
| fresh/blank flash | both slots `0xFF` | `rurp_load_config()` yields `CONFIG_VERSION`, `VALUE_R1`, `VALUE_R2`, `hardware_revision = 0xFF` |
| newest wins | A.seq=7 valid, B.seq=8 valid | B's payload loaded |
| CRC rejection | A.seq=9 with a flipped payload byte, B.seq=8 valid | B loaded, **not** A |
| both corrupt | both bad CRC | defaults, no crash |
| interrupted write | fake backend truncates the target slot mid-write | the *other* slot still loads, values intact |
| slot alternation | 3 consecutive saves | writes land in B, A, B — never the same slot twice |
| **AVR non-regression** | real AVR backend under ArduinoFake | `EEPROM.get/put` still called at offset **48** with `sizeof(rurp_configuration_t)`; byte-for-byte identical to pre-refactor |

The last row is the load-bearing one: it is what proves the AVR refactor is a pure move. Model it on the v1.22 Phase-117 pattern — the proof that the RED→GREEN flip came from production code was `git diff` on the test file being **empty**.

---

## 5. The VPP control seam — exactly what to take, exactly what to leave

Scope is settled: seam only. This section reports the split, names commits, and adjudicates the operator's read.

### 5.1 PR #45's ten commits, classified

| Commit | Files | Verdict |
|---|---|---|
| `04fd9b3` Add common VPP calibration and control API | `+include/rurp_vpp.h` | **PARTIAL — the seam's origin.** Take the reduced subset in §5.2, not the file. |
| `fc0b2c7` Add common VPP calibration and DAC feedback control | `+src/rurp_vpp.cpp` | **PARTIAL** — only `rurp_vpp_control_mode()` returning `MANUAL` and the `#if !RURP_HAS_VPP_DAC` early-return arm of `rurp_set_vpp_target_mv()`. |
| `86f351a` Complete common VPP calibration and DAC feedback control | `M src/rurp_vpp.cpp` | **LEAVE** — the closed loop. |
| `768580f` Persist common VPP calibration in board configuration | `M include/rurp_types.h` | **LEAVE — hard-blocked.** Adds 6 fields to `rurp_configuration_t`. `CONFIG_VERSION` territory; White-Box Calibration owns it. |
| `05f4a77` Expose common VPP calibration and control API | `M include/rurp_shield.h` | **LEAVE — this is C-2.** Not a one-line include: it strips all Phase-33/34/06/08/09 provenance comments, bumps `CONFIG_VERSION "VER06"→"VER07"`, and **removes** `rurp_read_voltage_mv()` from `rurp_shield.h`. **Hand-author** the single `#include "rurp_vpp.h"` line instead. |
| `b964ee6` Initialize shared VPP calibration defaults | `M src/rurp_config_utils.cpp` | **LEAVE** — default-fill for the 6 new fields. Also where Backlog 999.1's stale-`r1` fix lives. |
| `9134f2a` Route AVR voltage measurement through common calibration layer | `M src/boards/rurp_common.cpp` | **LEAVE — explicitly forbidden.** Renames the AVR `rurp_read_voltage_mv()` → `rurp_read_voltage_uncalibrated_mv()` **and** adds 16× ADC oversampling with a discarded first sample. That is a behaviour change to the v1.21 Phase-111 measured-voltage sampler and a flash cost. This file is White-Box Calibration's exact Stage-1 target. |
| `d285b83` Keep common VPP layer independent of Arduino timing | `M src/rurp_vpp.cpp` | **LEAVE** — refines loop timing; only meaningful with the loop. |
| `71278d0` Use compile-time VPP capabilities | `M include/rurp_vpp.h` | **TAKE (the capability-macro half).** `RURP_HAS_VPP_DAC` / `RURP_VPP_DAC_BITS` defaults + the `#error` consistency guard. |
| `a47228d` Compile DAC control only on capable boards | `M src/rurp_vpp.cpp` | **TAKE (the guard shape only)** — `#if RURP_HAS_VPP_DAC` bracketing, so nothing DAC-related compiles on any board this milestone. |

**Net recommendation: cherry-pick nothing.** Two commits are partially wanted, and one wanted commit (`05f4a77`) is the sole conflicting file in the inventory. Hand-authoring a ~40-line `include/rurp_vpp.h` plus a ~15-line `src/rurp_vpp.cpp` is smaller, conflict-free, and leaves no dead calibration API on `beta` for a later milestone to trip over.

### 5.2 The seam to land

```c
/* include/rurp_vpp.h — SEAM ONLY. No closed loop, no calibration. */
#ifndef RURP_HAS_VPP_DAC
#define RURP_HAS_VPP_DAC 0
#endif
#ifndef RURP_VPP_DAC_BITS
#define RURP_VPP_DAC_BITS 0
#endif
#if RURP_HAS_VPP_DAC && (RURP_VPP_DAC_BITS == 0)
#error "RURP_VPP_DAC_BITS must be defined for DAC-capable boards"
#endif

typedef enum rurp_vpp_control_mode {
    RURP_VPP_CONTROL_MANUAL = 0,
    RURP_VPP_CONTROL_DAC    = 1
} rurp_vpp_control_mode_t;

typedef enum rurp_vpp_result {
    RURP_VPP_OK                          = 0,
    RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED  = 1,
    RURP_VPP_INVALID_ARGUMENT            = 2,
    RURP_VPP_TIMEOUT                     = 3,
    RURP_VPP_OUT_OF_RANGE                = 4
} rurp_vpp_result_t;

rurp_vpp_control_mode_t rurp_vpp_control_mode(void);          /* → MANUAL, all boards */
rurp_vpp_result_t rurp_set_vpp_target_mv(uint16_t target_mv,
                                         uint16_t tolerance_mv,
                                         uint16_t timeout_ms); /* → MANUAL_ADJUSTMENT_REQUIRED */
void rurp_disable_vpp_control(void);                           /* no-op this milestone */
```

**Deliberately NOT declared** (so no dead API ships): `rurp_read_voltage_uncalibrated_mv`, `rurp_apply_vpp_calibration`, `rurp_calibrate_vpp_two_point`, `rurp_reset_vpp_calibration`, `rurp_vpp_calibration_valid`, `rurp_vpp_dac_write`, `rurp_vpp_control_enable`, `rurp_vpp_delay_ms`. `rurp_read_voltage_mv()` **stays exactly where it is** — declared in `rurp_shield.h`, defined in `src/boards/rurp_common.cpp` (AVR) and `py32f071_rurp_shield.cpp` (ARM).

Flash cost: `rurp_set_vpp_target_mv` has **zero callers**, so with `-ffunction-sections -Wl,--gc-sections` (already set on both build systems) the expected AVR delta is **0 B**. Verify by measurement, not assertion.

### 5.3 The operator's read — CONFIRMED, and here is the proof

> *"`rurp_set_vpp_target_mv()` closes its loop on the CALIBRATED `rurp_read_voltage_mv()`, which is why the loop cannot be taken without the calibration layer."*

**CONFIRMED. PROVEN, two independent ways:**

1. `src/rurp_vpp.cpp:141` inside `rurp_set_vpp_target_mv`'s `#else` (DAC-capable) arm reads:
   `const uint16_t measured_mv = rurp_read_voltage_mv();` — the feedback variable of the loop. Line 142 also compares it against `MAX_VPP_MV` for the overvoltage abort, so the *safety* interlock depends on it too.
2. Commit `9134f2a` **redefines what that name means**: it renames the AVR raw read to `rurp_read_voltage_uncalibrated_mv()`, and PR #45 moves `rurp_read_voltage_mv()` into `src/rurp_vpp.cpp` as `rurp_apply_vpp_calibration(rurp_read_voltage_uncalibrated_mv())` — reading `vpp_gain_ppm`/`vpp_offset_mv` out of `rurp_configuration_t`. So taking the loop pulls in, transitively: `9134f2a` (AVR measurement reroute + 16× oversampling), `768580f` (schema +6 fields), `b964ee6` (`CONFIG_VERSION` bump path). There is no seam between them.

**One refinement to the PROJECT.md framing, in the milestone's favour:** the claim that PR #45's three commits "reach into files that milestone owns" is true of *ownership*, but those three files (`src/boards/rurp_common.cpp`, `include/rurp_types.h`, `src/rurp_config_utils.cpp`) are **byte-identical between the merge base and `beta`** (PROVEN). So the collision is with the **future** milestone, not with today's rebase — which is one more reason the seam-only resolution costs this milestone nothing.

---

## 6. Host-side integration points — how the four seams were actually resolved

All PROVEN by reading `feature/py32f071-fw-install` @ `4ee64a1` (3 commits ahead of merge base `1bb5599`; +2125/−33 across 8 files) and diffing against `beta`.

| Seam | Predicted need | What the branch did | Assessment |
|---|---|---|---|
| **1. Board identity** | Nothing — `py32f071` flows through free | Nothing. `firmware.py:118` still `payload.split(":")`. | **Confirmed.** Zero change, as predicted. |
| **2. Release asset** | Publish `firestarter_py32f071.hex`; extension baked into the pattern at `firmware.py:155`, `:237`, `:336` | Replaced all three literals with `asset_candidates(board)` + `_pick_asset(assets, board)`. AVR → `["firestarter_<b>.hex"]`; DFU → `["…​.hex", "…​.bin"]`, hex preferred **because Intel HEX carries its own load address** which `load_image()` reads and the envelope guard validates, whereas a raw `.bin` can only be *assumed* to start at `FLASH_BASE`. | **Better than the prediction.** Line refs confirmed exact on `beta`. Solves the extension problem generically rather than adding a second hardcoded pair. |
| **3. Flasher** | Extract a `FirmwareFlasher` strategy; `AvrdudeFlasher` keeps the ladder verbatim | **Did NOT extract a strategy.** Added `_BOARD_FLASH_METHODS` dict + `flash_method(board)` (defaulting **unknown → avrdude**, so a fifth AVR variant needs no change) + a thin `_install_firmware()` router calling either `_install_with_avrdude` or the new `_install_with_dfu`. | **Deviation, and the right one.** The constraint was *"keep the bench-earned ladder verbatim"*; the branch achieves it by **not touching `_install_with_avrdude` at all** (`firmware.py:420-500`, incl. the `atmega32u4/avr109/57600` and `atmega328pb/urclock/115200` arms). A strategy extraction would have moved that code — strictly more risk for zero benefit. Record the deviation; do not "fix" it. |
| **4. CLI surface** | Add the board; avrdude-specific options/config keys need a per-flasher equivalent | Added `py32f071` to `_ALL_BOARDS`, filtered through `channel.available_boards()`. Added `--usb-id VID:PID` and `--dfu-probe`, both `hidden=not _PY32_ENABLED`. `--avrdude-path`/`--avrdude-config-path` left as-is. | **Partially deferred.** Board + py32 options: done. The *generalisation* of avrdude-specific options/config keys into a per-flasher registry: **not done.** Acceptable — with exactly two flashers, a registry is speculative. Note the CLI line reference has moved: `click.Choice` is at **`cli_handlers.py:930`** on `beta`, not `:821`. |

### 6.1 The import-time channel gate — confirmed, and correctly reasoned

`cli_handlers.py` computes at **module import**:

```python
_ALL_BOARDS: tuple[str, ...] = ("uno", "uno328pb", "leonardo", "py32f071")
_BOARD_CHOICES: list[str] = available_boards(_ALL_BOARDS)
_PY32_ENABLED: bool = "py32f071" in _BOARD_CHOICES
```

with an in-code justification: a wheel's `__version__` is fixed at build time, so the choice list rendered in `fw --help` is decided once and decided correctly. **This is sound**, and the two properties that make it safe are both present:

- **`channel.py` reads no environment.** Its docstring cites the firmware lesson that `-D X=${sysenv.VAR}` **fails OPEN**. `is_prerelease_build()` derives the channel from `firestarter.__version__` via `packaging.Version(...).is_prerelease` and treats `InvalidVersion` as **stable** — i.e. **fails closed**, hiding the gated feature. PROVEN by reading `channel.py:37-57`.
- **Double gating.** The CLI hides it (`_BOARD_CHOICES`), *and* the service layer refuses it: `_install_with_dfu()` raises `FirmwareOperationError(beta_only_message(board))` before importing pyusb, and `probe_dfu()` re-checks `is_prerelease_build()`. So library callers that never touch Click are also gated. PROVEN.
- `--dfu-probe` on a stable build raises `click.UsageError("no such option: --dfu-probe")` rather than silently running a py32-only diagnostic — because `hidden=` suppresses help text but does **not** reject the option. PROVEN, and a nice touch.

**One residual, worth a single line in requirements:** `--usb-id` has the same `hidden=` treatment but **no** matching `_PY32_ENABLED` rejection, so on a stable build it is accepted and silently ignored. Cosmetic, fail-safe direction, cheap to close.

### 6.2 The two safety fixes are on the branch and verified present

1. **DFU runtime-interface mis-selection.** `py32_dfu.py` distinguishes `DFU_PROTOCOL_RUNTIME = 0x01` from `DFU_PROTOCOL_DFU_MODE = 0x02` and routes through `find_dfu_interfaces()` / `select_interface()` rather than `interfaces[0]`. This is what stops `DFU_DETACH` going to an unrelated peripheral that advertises a DFU runtime interface (the devcontainer webcam `04f2:b751` being the discovered instance). PROVEN present.
2. **Detected board silently beating a typed `--board`.** `cli_handlers.py` computes `board_explicit = ctx.get_parameter_source("board") != ParameterSource.DEFAULT` and `manage_firmware_update` refuses the conflict outright — logging *"…unplug the {current_board} board, or drop --board to target it"* and returning `False` — instead of picking a side. PROVEN present. It also reorders `board_to_use` resolution **before** the port check, and adds `_PORTLESS_FLASH_METHODS = {dfu}` so a board in its bootloader (no CDC port) is not rejected for having no port, plus a `_hint_dfu_board()` nudge on the generic "cannot determine port" path.

### 6.3 Release-asset plumbing — two corrections to the documented plan

- **PROVEN gap:** `beta-build.yml:92` is `files: .pio/build/**/firestarter_*.hex`. The CMake image lands at `build/py32f071/firestarter_py32f071.hex` — outside that glob. The fold genuinely needs the extra `files:` entry (C-4).
- **The README's own snippet contradicts its own advice.** `platform/py32f071/README.md` §"Release integration" correctly argues for a **glob** (because `softprops/action-gh-release` *warns* on an unmatched glob but *fails* on a missing literal, so a broken ARM build must never block the AVR beta) — then supplies the **literal** `build/py32f071/firestarter_py32f071.hex`. Use `build/py32f071/firestarter_*.hex`. It also suggests `continue-on-error: true` on the three ARM steps until silicon validation; with no PCB this milestone, **take that suggestion**.
- **C-3 must be fixed in the same phase.** `py32f071.yml` runs on `pull_request` + `workflow_dispatch` only. Add `push: { branches: [beta] }`, or accept that the `beta-build.yml` fold becomes the sole ARM validation on `beta` — but then a broken ARM build carrying `continue-on-error: true` is *invisible*. Pick one deliberately: **recommend adding the push trigger**, so ARM breakage is loud in its own workflow while staying non-blocking in the release workflow.

---

## 7. Corrections to the documented premises

Every one of these is PROVEN against a live tree on 2026-07-30 and should be applied before requirements are written.

| # | Document claim | Reality |
|---|---|---|
| **X-1** | `agent/portability-macros` contains `include/rurp_platform.h`, `rurp_millis()`/`rurp_delay_ms()`/`rurp_delay_us()`, board-local pin maps behind logical identifiers, and capability macros | It contains **4 files / 123 insertions**: `rurp_platform_compat.h`, `include/avr/pgmspace.h`, and include-swaps + macro→inline in `rurp_serial_utils.h` / `rurp_shield.h`. `rurp_platform.h` is on the **py32** branch. The timing functions exist but **no common code calls them** — the mechanism is the `platform/py32f071/include/Arduino.h` shim. No pin-map work; `rurp_pinout.h` is untouched by every branch. |
| **X-2** | *"`platform/py32f071/PORTING.md` on the py32 branch is a 195-line combined HAL + native-backend contract — scope from it"* | **It does not exist on the live branch.** `git ls-tree` finds it only on `feature/py32f071-toolchain` (#46, closed) and `feature/py32f071-full-support` (#47, closed) — identical blob `4b1a441`, 195 lines. It is a **specification**, and it is partly superseded: its prescribed module layout (`py32f071_board.h`, `gpio.cpp`, `board.cpp`, `adc.cpp`, `dac.cpp`, `storage.cpp`) does not match what PR #48 built (`py32f071_rurp_shield.cpp`, `timing.cpp`, `usb_cdc.c`, `config.cpp`, `platform_compat.cpp`, `main.cpp`), and 4 of its 15 acceptance items are out of scope here (#191 common calibration, #192 closed-loop DAC, #195 real hardware, #189 removing Arduino timing calls). **Scope from it selectively, and cite the closed branch as its home.** Consider vendoring the in-scope subset onto the milestone branch so the contract is not stranded on a closed PR. |
| **X-3** | `DATA_BUFFER_SIZE = 1024` (PROJECT.md, STATE.md, branch-state note) | **`DATA_BUFFER_SIZE=512`** on **both** py32 branches (`platform/py32f071/CMakeLists.txt:113`). `RURP_BOARD_NAME="py32f071"` and `MONITOR_SPEED=250000` are correct. With 16 KiB SRAM, 512 is a conservative placeholder — but the host's v1.10 CAP-01 negotiation will advertise 512, so either raise it deliberately or record 512 as intended. |
| **X-4** | Leonardo headroom ≈ 2992 B | **2600 B** on `beta` (26072 / 28672), **2656 B** after the merge. The 2992 figure pre-dates Phase 119's measured +392 B. |
| **X-5** | Branches are 27 commits behind `beta` (branch-state note) | **72 behind** as of 2026-07-30. PROJECT.md and STATE.md already say 72; the note is stale. |
| **X-6** | The 72 beta commits "include the whole v1.22 milestone" | True but understated: merge base is **2026-06-18**, so they span **v1.14 → v1.22**, including v1.19's handler renames (the cause of C-1) and v1.20's `mem_type` removal. |
| **X-7** | `cli_handlers.py:819` is the `click.Choice` board list | **`cli_handlers.py:930`** on `beta`. (`firmware.py:113`, `:155`, `:237`, `:336`, `:420`, `:640` all verified **correct**.) |
| **X-8** | Host install branch head `311eacf` (branch-state note) | **`4ee64a1`** (PROJECT.md and the worktree agree); 3 commits ahead of merge base `1bb5599`, 79 behind `beta`. |

---

## 8. Architectural patterns worth naming

### Pattern 1: Compat shim at the platform edge, not a rewrite at the call site

**What:** Rather than sweeping ~10 common TUs to replace `delay()`/`millis()` with `rurp_*` calls, the new platform supplies a header named `Arduino.h` that implements the Arduino subset the common code actually uses, on top of its own primitives.

**When to use:** When the common layer is guarded by golden traces / byte-exact register-trace tests, and the port must prove *"the shared algorithms compile unchanged"*.

**Trade-offs:** ✅ Zero protocol-layer churn ⇒ golden traces, dispatch-mirror guard and flash budget structurally protected (this is *why* §3.5 came out green). ❌ The boundary is a fake Arduino, not a named HAL; the shim's coverage is implicit and only the ARM build discovers a gap. ❌ `PORTING.md`'s *"Arduino timing calls are removed from common code"* stays unsatisfied.

```c
/* platform/py32f071/include/Arduino.h */
static inline void delayMicroseconds(uint32_t v) { RURP_DELAY_US(v); }
static inline void delay(uint32_t v)             { RURP_DELAY_MS(v); }
static inline unsigned long millis(void)         { return (unsigned long)RURP_MILLIS(); }
```

### Pattern 2: `#include_next` shadow for a platform-specific header name

**What:** Place `include/avr/pgmspace.h` on the project include path. On AVR it `#include_next`-chains to the toolchain header; elsewhere it forwards to a neutralising compat header. Headers that still say `#include <avr/pgmspace.h>` — including the **codegen-generated** `messages.h`, which cannot be hand-edited — port for free.

**When to use:** When the offending include lives in generated or otherwise un-editable code.

**Trade-offs:** ✅ No edits to generated files; ✅ empirically verified to chain correctly (§3.3); ✅ net **−56 B** on Leonardo alongside the inline conversion. ❌ Every AVR TU's include graph now routes through a project file; ❌ depends on `-I` (not `-isystem`) ordering, a GNU extension; ❌ becomes an 8th copy of a shim that exists 7× under `test/native/avr/*/avr/pgmspace.h`.

### Pattern 3: Backend seam under a common policy layer (recommended, §4)

**What:** Split a platform-entangled module by **concern** — keep singleton + validation policy common, push only the byte-blob read/write behind a two-function contract.

**When to use:** Whenever the second platform's implementation currently *duplicates* the first's policy. PR #48's `config.cpp` has already drifted (extra `r2 == 0` check, `memset`, `0xFFU`), which is the symptom this pattern removes.

**Trade-offs:** ✅ The `rurp_configuration_t` schema is untouched, so no `CONFIG_VERSION` bump and no encroachment on White-Box Calibration. ✅ A fake backend makes the whole thing native-testable. ❌ Touches `src/rurp_config_utils.cpp`, an AVR-shared file — needs the byte-identical-EEPROM-call regression test as its safety net.

### Pattern 4: Capability macro + refusing default (the VPP seam, §5)

**What:** Land the *shape* of an unimplemented facility — capability macros, result enum, and a function that returns `MANUAL_ADJUSTMENT_REQUIRED` on every board — so a later milestone adds behaviour without re-architecting, and nothing today can silently half-work.

**When to use:** When a facility cannot be validated at all (here: no PCB ⇒ a closed loop cannot be tested), but a downstream port needs to compile against its final shape.

**Trade-offs:** ✅ Costs ~0 B with `--gc-sections` (no callers). ✅ Makes the non-claim structural: the function *refuses*, so no code path can pretend the loop works. ❌ Declares an API nobody calls — mitigated by declaring **only** the 4 seam functions, not PR #45's full 11.

---

## 9. Anti-patterns to avoid in this milestone

### AP-1: Treating `git merge-tree`'s clean exit as "the rebase is done"

**What people do:** Merge, see no conflicts, ship.
**Why it's wrong:** The single blocking collision (C-1) is a *stale hand-maintained source list* in a file only one side touched. Git merges it perfectly into a broken tree, and per C-3 nothing on `beta` builds ARM to tell you.
**Do this instead:** Make "validate every path in `FIRESTARTER_COMMON_SOURCES` exists, and equals `src/**` minus a commented exclusion list" a **gate**, not a task.

### AP-2: Cherry-picking from PR #45

**What people do:** `git cherry-pick 04fd9b3 71278d0 a47228d 05f4a77` to "just get the seam".
**Why it's wrong:** `05f4a77` is the only conflicting file in the whole inventory (C-2), and it smuggles a `CONFIG_VERSION` bump plus the deletion of Phase-33/34 provenance comments. `04fd9b3`/`fc0b2c7` carry the full 11-function calibration API.
**Do this instead:** Hand-author ~40 lines of `rurp_vpp.h` + ~15 lines of `rurp_vpp.cpp`, and add one `#include "rurp_vpp.h"` line to the already-portability-modified `rurp_shield.h`.

### AP-3: Verifying the host suite from a scratch path

**What people do:** Clone/worktree the app somewhere convenient and run `pytest`.
**Why it's wrong:** PROVEN — 11 firmware-scanning tests **SKIP** with *"firestarter firmware checkout absent"*. The nine cross-repo gates that broke 4+ times in v1.22 are exactly the ones that go quiet. That is a false green.
**Do this instead:** Verify in a directory literally named `firestarter_app` with a **merged** `firestarter` sibling. PROVEN: with that layout the suite is fully green and every gate runs.

### AP-4: Starting from PR #47 because it looks finished

**What people do:** Pick the 24-file branch.
**Why it's wrong:** PROVEN by contrast — #47's `src/usb.c` is a ring buffer over `__attribute__((weak))` no-op hooks; a flashed board is silent on USB. PR #48's `usb_cdc.c` is real CherryUSB (`usbd_desc_register`, `usbd_add_interface`, `usbd_add_endpoint`, `usbd_initialize`, `NVIC_EnableIRQ(USBD_IRQn)`, `USBD_IRQHandler`).
**Do this instead:** Integrate `feature/py32f071-release-assets`. Harvest **only** `PORTING.md` from the closed branches, as a spec.

### AP-5: Letting the provisional pin map leak into any success criterion

**What people do:** Write "verify the data bus" or "confirm VPP reads correctly".
**Why it's wrong:** `include/boards/py32f071_rurp_shield.h:13-38` self-declares `RURP_PY32F071_PINMAP_PROVISIONAL 1` and states it *"describes no existing PCB"* (PB0–PB7 data, PA0–PA5 control, VPP PA4/ADC ch4; PA4 chosen only because it matches the Puya ADC example; user button **not fitted**). No PCB exists.
**Do this instead:** Permitted claims only — the target **builds clean**, the native and host suites **pass**, and the DFU sequence is exercised against **device descriptors and mocks**. Never *"the firmware runs on a PY32F071"* or *"the install works end to end."*

### AP-6: Deferring the PCB/flash-budget decisions because the bootloader is not being built

**What people do:** Ship the DFU path, leave the linker script as full-128K.
**Why it's wrong:** PROVEN — the linker script reserves **nothing** for either the two config pages or a base-of-flash bootloader, and `py32_dfu.py` hardcodes `FLASH_BASE 0x08000000` / `FLASH_SIZE 128 KiB`. BOOT0/nBOOT1 strapping, SWD pads and a contiguous 8-bit port are free before layout and expensive after.
**Do this instead:** Land the flash-map reservation and the PCB-consequence record as first-class deliverables even though the bootloader itself is out of scope.

---

## 10. Data-flow changes

### 10.1 Firmware install (the one genuinely new flow)

```
firestarter fw --install --board py32f071
        │
        ▼
cli_handlers.fw                       ← _BOARD_CHOICES (import-time channel gate)
        │  board_explicit = ctx.get_parameter_source("board") != DEFAULT
        ▼
firmware.manage_firmware_update
        │  ① find_and_check_programmer  → (connected_port, current_board)
        │  ② board_to_use = current_board or board_override        ← moved EARLIER
        │  ③ if board_explicit and detected != requested → REFUSE  ← NEW
        │  ④ method = flash_method(board_to_use)
        │     if not port and method not in _PORTLESS_FLASH_METHODS → error + hint
        │  ⑤ fetch_release_info → _pick_asset(assets, board)       ← asset_candidates()
        │  ⑥ download
        ▼
firmware._install_firmware                                          ← NEW router
        ├── avrdude ──► _install_with_avrdude  (UNCHANGED, ladder verbatim)
        └── dfu ──────► _install_with_dfu                            ← NEW
                            │  channel gate: is_board_available()
                            │  lazy import pyusb
                            ▼
                        py32_dfu.Py32DfuFlasher
                            select_interface()   ← runtime vs DFU-mode discrimination
                            load_image()         ← Intel HEX carries its load address
                            _check_envelope()    ← FLASH_BASE / FLASH_SIZE guard
                            _download_dfuse() | _download_plain()
```

**Key structural change:** board resolution now happens **before** the port requirement, because a DFU board in bootloader mode exposes no CDC port at all. That reordering is load-bearing, not cosmetic.

### 10.2 Firmware boot and config (unchanged shape, new backend)

```
ARM: startup_py32f071.s → main() → HAL_Init() → configure_system_clock() (48 MHz PLL)
                                 → rurp_timing_init() (SysTick 1 kHz + TIM3 µs)
                                 → setup()                       ← COMMON firestarter.cpp
                                       rurp_load_config()        ← policy (common)
                                         └─ rurp_config_storage_read()  ← NEW SEAM
                                              AVR: EEPROM.get(48)
                                              ARM: dual-slot CRC32 flash record
                                       [rurp_detect_hardware_revision()]  ← #ifdef, off on ARM
                                       rurp_board_setup()        ← per-board
                                       Serial.begin() → rurp_communication_begin()
                                 → loop()                        ← COMMON
```

Note the ordering divergence from `PORTING.md` (which prescribes ADC/DAC init **before** loading config): the common `setup()` loads config **first**, then calls `rurp_board_setup()`. Harmless on ARM because `main()` has already run `HAL_Init()` + clocks before `setup()`, so flash reads are valid. Worth a comment so a future reader does not "fix" it toward `PORTING.md`.

### 10.3 Protocol data flow: unchanged

The `algorithm` → `handle->protocol` → `configure_memory` dispatch chain is **byte-identical** — PROVEN by zero py32 changes under `src/`, by `check_dispatch.py` PASS on the merged tree, and by 141/141 native tests including `test_dispatch` and the dispatch-mirror guard.

---

## 11. Resource envelope (the embedded analogue of "scaling")

| Target | Flash used / total (merged) | Headroom | Constraint status |
|---|---|---|---|
| **leonardo** (ATmega32U4) | 26016 / 28672 B — 90.7 % | **2656 B** | The binding constraint. Merge **improves** it by 56 B. Any phase that grows flash must measure here. |
| uno (ATmega328P) | 23954 / 32256 B — 74.3 % | 8302 B | +22 B from the merge. Comfortable. |
| uno328pb (ATmega328PB) | 24004 / 32384 B — 74.1 % | 8380 B | +28 B. Comfortable. |
| leonardo RAM | 2014 / 2560 B — 78.7 % | 546 B | Why PR #45's `768580f` (+16 B in `rurp_configuration_t`) is a real cost, not a rounding error. |
| **py32f071** (PY32F071xB) | not measurable here — no ARM toolchain in this devcontainer | 128 KiB flash / 16 KiB SRAM | Effectively unconstrained for firmware; the **contended** resource is flash *layout*: 2 config pages + a bootloader region, both currently unreserved. |

**Where pressure appears first, in order:**

1. **Leonardo flash.** 2656 B. Everything AVR-touching is judged here.
2. **Leonardo RAM.** 546 B. Schema growth is the mechanism.
3. **py32 flash layout** (not size). The linker script claims all 128 K; config slots and a bootloader region must be carved out before layout is frozen.
4. **PY32 timing fidelity — unmeasurable this milestone.** `rurp_delay_us` busy-polls TIM3 while USB interrupts run (`PORTING.md:61` explicitly requires *"no long global interrupt masking because USB must continue to run"*). PROM pulse widths — e.g. v1.22 Phase 118's measured 572 µs against a 600 µs `t_WC` budget, 4.7 % headroom — could be stretched by USB ISR latency. **PREDICTED risk; unvalidatable without a board.** Record it as an explicit non-claim; do not schedule work against it.

---

## 12. Suggested build order

Dependencies are marked **LOAD-BEARING** (reordering breaks something provable) or *convenience* (ordering is merely tidy).

### Phase 123 — Land the portability half + the py32 stack onto the milestone branch

**Deliver:** `--no-ff` merge `agent/portability-macros`, then `feature/py32f071-release-assets`; fix **C-1** (`flash_type_3/4` → `flash_nor_unlock`/`flash_5v_page` in `platform/py32f071/CMakeLists.txt:46-47`); add the source-list gate (§3.4); fix **C-3** (`push: branches: [beta]` in `py32f071.yml`).

**Verify:** Leonardo/uno/uno328pb build with recorded sizes; `pio test -e native` and `-e native_nodevtools` 141/141; ARM CMake **configures and builds** in CI; full host suite green in the **sibling layout** with all nine gates *running*.

**Ordering:**
- **LOAD-BEARING — C-1 must land in this phase.** Without it `beta`'s ARM target does not configure, and (pre-C-3) nothing reports it. Every later phase would build on a broken target.
- **LOAD-BEARING — portability before py32.** PR #48 is stacked on `agent/portability-macros`; the py32 branch's `rurp_platform_compat.h` is a 19-line *delta* on the portability version. Merging py32 first is a needless conflict.
- **LOAD-BEARING — this phase before the VPP seam.** The seam adds `#include "rurp_vpp.h"` to `rurp_shield.h`, the one file with any conflict exposure (C-2). Doing it after the merge means editing a settled file instead of resolving a three-way.
- *Convenience:* the source-list gate could come later, but writing it here is what makes C-1 provably non-recurring.

### Phase 124 — VPP control seam (firmware, seam only)

**Deliver:** hand-authored `include/rurp_vpp.h` (§5.2) + minimal `src/rurp_vpp.cpp`; one `#include` line in `rurp_shield.h`; `RURP_VPP_CONTROL_MANUAL` on all four boards; `rurp_set_vpp_target_mv()` → `MANUAL_ADJUSTMENT_REQUIRED` everywhere; add `rurp_vpp.cpp` to both build systems.

**Verify:** AVR flash delta **0 B** (expected, `--gc-sections`, no callers) — measured, not asserted; native test asserting `rurp_vpp_control_mode() == RURP_VPP_CONTROL_MANUAL` and `rurp_set_vpp_target_mv(...) == RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED` on every board macro-set; `git diff` proves `src/boards/rurp_common.cpp`, `include/rurp_types.h`, `src/rurp_config_utils.cpp` **untouched** (the anti-encroachment gate) and `CONFIG_VERSION` still `"VER06"`.

**Ordering:**
- **LOAD-BEARING — after Phase 123** (needs the merged `rurp_shield.h`).
- **LOAD-BEARING — before Phase 125.** Phase 125 also edits `src/rurp_config_utils.cpp`; landing the VPP seam first, with a gate proving that file untouched, keeps the "no `CONFIG_VERSION` bump" non-claim clean and attributable.
- *Convenience:* could swap with 126 (host) — they are independent.

### Phase 125 — Flash-persistent config via a storage-backend seam

**Deliver:** `include/rurp_config_storage.h`; refactor `src/rurp_config_utils.cpp` to policy-only; `src/boards/rurp_config_storage_eeprom.cpp` (pure move); `platform/py32f071/src/config_storage_flash.cpp` (dual-slot CRC32, `StoredConfiguration` wrapper per `PORTING.md`); delete/shrink `platform/py32f071/src/config.cpp`; **reserve two config pages in `PY32F071xB_FLASH.ld`** with linker symbols; native fake backend + the 7 tests of §4.4.

**Verify:** AVR EEPROM regression test asserts `EEPROM.get/put` at offset **48** with `sizeof(rurp_configuration_t)`, byte-identical to pre-refactor; `rurp_configuration_t` and `CONFIG_VERSION` **unchanged** (diff gate); Leonardo flash delta recorded; ARM builds; interrupted-write test green.

**Ordering:**
- **LOAD-BEARING — after Phase 123** (the py32 tree must exist).
- **LOAD-BEARING — the AVR backend extraction must be a *pure move*, verified by test, before the ARM backend is written.** Doing both at once means a failing test cannot be attributed.
- **LOAD-BEARING — the linker-script reservation must land with this phase, not later.** Once the ARM backend has an address, changing it is a flash-map migration.
- **LOAD-BEARING — before Phase 128 (PCB/flash-path record).** The record must document the *actual* reserved map, not an intended one.
- ⚠ **Highest-risk phase for the AVR non-regression constraint** — the only phase that edits a file compiled into all three AVR targets. Budget the regression test as a first-class deliverable.

### Phase 126 — Host DFU installer

**Deliver:** merge `firestarter_app` `feature/py32f071-fw-install` (@ `4ee64a1`) — PROVEN clean; close the `--usb-id`-on-stable residual (§6.1); reconcile `doc/PY32F071-FIRMWARE-INSTALL.md` with the final flash map; confirm the `[py32]` extra is genuinely optional (AVR install must not require pyusb).

**Verify:** full host suite in the **sibling layout**, 0 failures; 44+ `test_py32_dfu.py` tests green; mypy watermark; `firestarter fw --help` on a simulated **stable** `__version__` shows **no** `py32f071` and rejects `--dfu-probe`; on a **pre-release** `__version__` shows both. Never run `fw --install` against attached hardware in verification — it flashes the attached board and ignores `--board`.

**Ordering:**
- *Convenience only* relative to 124/125 — independent, different repo, and it merges clean today.
- **LOAD-BEARING — before Phase 127.** The release-asset fold must publish the name the host actually resolves. The host defines that contract (`asset_candidates()` → `firestarter_<board>.hex`, `.bin` fallback), so land the host first and make the CI assert against it.

### Phase 127 — Release-asset fold into `beta-build.yml`

**Deliver:** three ARM steps after `Build PlatformIO Project` (per `README.md` §"Release integration"), plus the release `files:` entry as a **glob** `build/py32f071/firestarter_*.hex`; `continue-on-error: true` on the ARM steps while unvalidated; a CI assertion that the emitted filename matches the host's `asset_candidates("py32f071")[0]`.

**Verify:** dry-run/`workflow_dispatch` produces `firestarter_py32f071.hex`; the three AVR assets are still produced; a deliberately broken ARM build does **not** block the AVR release.

**Ordering:**
- **LOAD-BEARING — after Phase 123** (must not fold a target that does not configure).
- **LOAD-BEARING — the ARM build must run AFTER `update_version.py`.** `beta-build.yml` rewrites `include/version.h` and auto-commits *before* building; an image built in any other job carries a stale `VERSION`, and the host's entire update decision is that string compared against the release tag. **This is why `py32f071.yml` must not cut releases** — it is the whole reason the fold exists.
- **LOAD-BEARING — after Phase 126** (asset-name contract, above).
- ⚠ Pushing `beta` auto-fires CI and cuts a beta. Keep the cut a deliberate, separately gated step — and note that `--auto`/`--chain` auto-approves human-verify checkpoints, so gate any push/PyPI/public-comment step explicitly.

### Phase 128 — Flash-path decision + PCB requirements record (docs)

**Deliver:** ADR-style record — self-flash bootloader over the existing CDC + COBS transport as the intended **primary** route, factory USB DFU (Puya UM1504) as the maintainer/manufacturing **recovery** route; BOOT0/nBOOT1 strapping; SWD pads; contiguous 8-bit port requirement (already encoded as `#if RURP_PY32F071_DATA_SHIFT > 8` → `#error`); the flash-budget reservation as actually implemented in Phase 125 plus the bootloader region and vector-table relocation implication; explicit statement that landing the DFU path **does not retire** `.planning/seeds/py32f071-no-external-tool-fw-install.md`.

**Ordering:** **LOAD-BEARING — after Phase 125** (must record the real reserved map). Otherwise convenience.

### Phase 129 — Honesty/close capstone

**Deliver:** correct all eight X-1…X-8 premise errors (§7) in PROJECT.md / STATE.md / ROADMAP / the branch-state note, including the pending todo `correct-v128-py32-roadmap-prior-art`; a claim ledger in the v1.22 Phase-122 style pairing each permitted wording with its explicit non-claim (builds clean / suites pass / DFU exercised against descriptors and mocks — **never** "runs on a PY32F071" or "install works end to end"); record the provisional pin map as provisional in every artifact; record the unvalidatable USB-ISR-vs-PROM-timing risk (§11.4); record the Uno/uno328pb +22/+28 B constraint nuance and the corrected 2656 B headroom.

**Ordering:** last by definition.

### Ordering summary

```
123 (merge + C-1 + gate + C-3)   ← LOAD-BEARING first; everything depends on a configurable ARM target
 ├─► 124 (VPP seam)              ← LB after 123 (rurp_shield.h); LB before 125 (config-file attribution)
 │      └─► 125 (flash config)   ← LB after 124; LB internal order: AVR move THEN ARM backend
 │             └─► 128 (PCB rec) ← LB after 125 (real flash map)
 ├─► 126 (host DFU merge)        ← independent of 124/125
 │      └─► 127 (release fold)   ← LB after 126 (asset-name contract) AND after 123
 └───────────────────► 129 (honesty close)
```

**Genuinely parallelisable:** {124, 125} ∥ {126}. Different repos, disjoint files, no shared gate.
**Not parallelisable:** 124 → 125 (both edit AVR-shared config/HAL files; serial ordering is what makes a regression attributable), 126 → 127 (contract direction), 125 → 128 (record the real map).

---

## 13. Integration Points reference

### Firmware — new vs modified

| Component | New / Modified | Path | Notes |
|---|---|---|---|
| Platform compat vocabulary | **NEW** | `include/rurp_platform_compat.h` | 86 lines final |
| `avr/pgmspace.h` shadow | **NEW** | `include/avr/pgmspace.h` | `#include_next`; verified to chain |
| Platform ID + timing macros | **NEW** | `include/rurp_platform.h` | **zero common-code consumers** |
| Logical HAL contract | **MODIFIED** | `include/rurp_shield.h` | 4 macros → `static inline`; +1 `#include` in Phase 124 |
| Serial utils header | **MODIFIED** | `include/rurp_serial_utils.h` | include swap only |
| VPP seam | **NEW** | `include/rurp_vpp.h`, `src/rurp_vpp.cpp` | Phase 124, hand-authored |
| Config policy | **MODIFIED** | `src/rurp_config_utils.cpp` | Phase 125; backend hooks replace `EEPROM.*` |
| Config storage contract | **NEW** | `include/rurp_config_storage.h` | Phase 125 |
| AVR config backend | **NEW (pure move)** | `src/boards/rurp_config_storage_eeprom.cpp` | Phase 125 |
| ARM board backend | **NEW** | `platform/py32f071/src/py32f071_rurp_shield.cpp` (317 L) | 11 `rurp_*` fns |
| Arduino shim | **NEW** | `platform/py32f071/include/Arduino.h` (76 L) | the load-bearing seam |
| ARM timing | **NEW** | `platform/py32f071/src/timing.cpp` (115 L) | SysTick ms + TIM3 µs |
| ARM USB CDC | **NEW** | `platform/py32f071/src/usb_cdc.c` (306 L) | real CherryUSB |
| ARM config storage | **NEW** | `platform/py32f071/src/config_storage_flash.cpp` | Phase 125; replaces `config.cpp` |
| ARM build | **NEW** | `platform/py32f071/CMakeLists.txt` | **fix lines 46-47**; second source list |
| ARM link map | **MODIFIED** | `platform/py32f071/linker/PY32F071xB_FLASH.ld` | Phase 125: reserve config pages |
| ARM CI | **MODIFIED** | `.github/workflows/py32f071.yml` | add `push: [beta]` |
| Release CI | **MODIFIED** | `.github/workflows/beta-build.yml` | 3 ARM steps + glob `files:` entry |
| Source-list gate | **NEW** | `tools/check_py32_sources.py` (proposed) | closes the C-1 class |
| **Untouched** | — | `src/proms/*`, `src/firestarter.cpp`, `src/eprom_operations.cpp`, `src/operation_utils.cpp`, `src/json_parser.c`, `include/firestarter.h`, `include/messages.h`, `include/rurp_pinout.h`, `include/rurp_register_utils.h`, `src/boards/{uno,leonardo}_rurp_shield.cpp`, `src/boards/rurp_common.cpp` | The non-regression surface |

### Host — new vs modified

| Component | New / Modified | Path | Notes |
|---|---|---|---|
| DFU backend | **NEW** | `firestarter/py32_dfu.py` (832 L) | DFU 1.1 + DfuSe, Intel-HEX loader, envelope guard |
| Channel gate | **NEW** | `firestarter/channel.py` (81 L) | `BETA_ONLY_BOARDS`; reads no env; fails closed |
| Flasher dispatch | **MODIFIED** | `firestarter/firmware.py` +246/−33 | `flash_method`, `asset_candidates`, `_pick_asset`, `_install_firmware`, `_install_with_dfu`, `probe_dfu`, `_hint_dfu_board`, `board_explicit` refusal. `_install_with_avrdude` **body untouched** (`:420-500`) |
| CLI | **MODIFIED** | `firestarter/cli_handlers.py` +64 | `_BOARD_CHOICES` at `:~140` (import-time); `click.Choice` at `:932`; `--usb-id`, `--dfu-probe`; `FirmwareOperationError` mapping |
| Optional dep | **MODIFIED** | `pyproject.toml` | `[py32] pyusb>=1.2.1` |
| Docs | **NEW** | `doc/PY32F071-FIRMWARE-INSTALL.md` (273 L) | bootloader-entry routes |
| Tests | **NEW** | `tests/test_py32_dfu.py` (654 L) | |
| **Untouched** | — | `serial_comm.py`, `database.py`, `constants.py`, `avr_tool.py`, all nine source-scanning gates | |

### Internal boundaries

| Boundary | Communication | Notes |
|---|---|---|
| protocol layer ↔ HAL | direct C calls, `rurp_*` in `rurp_shield.h` | 40 declarations; unchanged semantics |
| protocol layer ↔ Arduino API | direct (`delay`, `millis`, `Serial`) | **the real portability seam** — absorbed by the py32 `Arduino.h` shim, not removed |
| HAL ↔ config persistence | `rurp_load_config`/`rurp_save_config` today; **two backend hooks** after Phase 125 | the only clean place to put per-platform storage without touching the schema |
| HAL ↔ VPP control | `rurp_vpp.h` seam | refuses on every board this milestone |
| host ↔ firmware (wire) | COBS + CRC8 over CDC/UART, 250000 baud | unchanged. `DATA_BUFFER_SIZE=512` on py32 (**not** 1024 — X-3) |
| host ↔ firmware (source text) | nine `tools/check_*` / `tests/test_{sdp,check,revision}_*` gates scanning firmware source | **PROVEN unaffected** by the merge; must be re-run in a **sibling layout** |
| host ↔ board (install) | avrdude/serial OR pyusb/USB-DFU, chosen by `flash_method(board)` | unknown boards default to avrdude |
| meta ↔ firmware (codegen) | `tools/catalog/messages.toml` → `include/messages.h` | never hand-edit `messages.h`; note it still `#include <avr/pgmspace.h>` and depends on the shadow |

---

## 14. Reproducing every PROVEN claim

```bash
# Branch geometry
cd /workspaces/firestarter
git merge-base beta origin/agent/py32f071-toolchain            # → a1953c2
git rev-list --count a1953c2..feature/py32f071-release-assets   # → 53
git rev-list --count a1953c2..beta                              # → 72

# No textual conflicts (empty list + exit 0)
git merge-tree --write-tree --messages beta feature/py32f071-release-assets

# Disjoint file sets (empty output)
comm -12 <(git diff --name-only a1953c2..beta | sort) \
         <(git diff --name-only a1953c2..feature/py32f071-release-assets | sort)

# The ONE conflict in the inventory: py32 stack x PR #45
git merge-tree --write-tree --messages origin/agent/portability-macros \
                                      origin/feature/common-vpp-calibration

# C-1: merge, then path-validate the CMake source list
git worktree add --detach /tmp/mt beta && cd /tmp/mt
git merge --no-edit feature/py32f071-release-assets
grep -o '\${REPOSITORY_ROOT}/[^"]*' platform/py32f071/CMakeLists.txt \
  | sed 's|${REPOSITORY_ROOT}/||' | while read f; do
      [ -e "$f" ] && echo "OK $f" || echo "MISSING $f"; done
# → MISSING src/proms/flash_type_3.cpp ; MISSING src/proms/flash_type_4.cpp

# AVR + native non-regression
pio run -e leonardo -e uno -e uno328pb     # 26016 / 23954 / 24004 B
pio test -e native                          # 141/141
pio test -e native_nodevtools               # 141/141

# #include_next shadow chains correctly on AVR
~/.platformio/packages/toolchain-atmelavr/bin/avr-g++ -mmcu=atmega32u4 \
  -DF_CPU=16000000L -DARDUINO_AVR_LEONARDO -I include \
  -I ~/.platformio/packages/framework-arduino-avr/cores/arduino \
  -I ~/.platformio/packages/framework-arduino-avr/variants/leonardo \
  -E -H -x c++ - <<<'#include <avr/pgmspace.h>' 2>&1 >/dev/null | grep pgmspace

# Host gates — the SIBLING LAYOUT is mandatory
mkdir -p /tmp/ws
cd /workspaces/firestarter_app && git worktree add --detach /tmp/ws/firestarter_app beta
cd /tmp/ws/firestarter_app     && git merge --no-edit feature/py32f071-fw-install
cd /workspaces/firestarter     && git worktree add --detach /tmp/ws/firestarter beta
cd /tmp/ws/firestarter         && git merge --no-edit feature/py32f071-release-assets
cd /tmp/ws/firestarter_app && python -m pytest -q        # 0 failures, 29 snapshots
for t in check_dispatch check_is_memory_cmd_no_ifdef check_no_log_in_sdp_window \
         check_sdp_capability_invariants check_devtest_orchestrator \
         check_no_community_support_status_write diff_db; do
    python tools/$t.py >/dev/null && echo "$t PASS"; done     # 7/7 PASS
```

---

## Sources

- **Live trees, 2026-07-30:** `/workspaces/firestarter` @ `beta` `5c9160a`; `/workspaces/firestarter_py32_ci` @ `feature/py32f071-release-assets` `ad47c3b`; `/workspaces/firestarter_app` @ `beta` `e7d3ee8`; `/workspaces/firestarter_app_py32` @ `feature/py32f071-fw-install` `4ee64a1`.
- **Origin refs read:** `origin/agent/portability-macros` `52d6c1f`; `origin/agent/py32f071-toolchain` `e5abb51`; `origin/feature/common-vpp-calibration` `a47228d` (all 10 commits individually); `origin/feature/py32f071-toolchain` `2c2ed10`; `origin/feature/py32f071-full-support` `cc4a815`.
- **`PORTING.md`** — blob `4b1a441`, 195 lines, identical on the two CLOSED branches; **absent** from the live branch.
- **Builds and test runs executed during this research** (not cited from CI): `pio run -e leonardo|uno|uno328pb` on `beta` and on the merged tree; `pio test -e native` and `-e native_nodevtools` on the merged tree; `python -m pytest -q` on `beta`, on the install branch, on a scratch-path merged tree, and on the merged **sibling** layout; the seven `tools/check_*` + `diff_db` gates; a direct `avr-g++ -E -H` include-path trace.
- **Meta-repo:** `.planning/PROJECT.md` §"Current Milestone: v1.23"; `.planning/STATE.md` §"Milestone Context (v1.23)"; `.planning/notes/py32f071-port-branch-state.md`; `firestarter/CLAUDE.md`; `firestarter_app/CLAUDE.md`.
- **Not consulted, deliberately:** no PY32F071 datasheet or reference-manual claim is made. Flash page/sector geometry is flagged as *must be read before editing the linker script*, not asserted.

---
*Architecture research for: PY32F071 fourth-board-target integration into the Firestarter two-repo system*
*Researched: 2026-07-30*
