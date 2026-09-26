# Phase 126: Flash-Persistent Config via a Storage-Backend Seam — Research

**Researched:** 2026-07-31
**Domain:** ARM Cortex-M0+ internal-flash configuration persistence (PY32F071xB) behind a per-platform storage seam; AVR EEPROM path preserved byte-identical
**Confidence:** HIGH on the flash geometry, the HAL contract and every in-tree fact (all measured or read from primary sources this session); LOW on anything about PY32F071 silicon behaviour, which no source can supply

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Seventeen decisions are locked in `126-CONTEXT.md` §`<decisions>`. Read that file for the full
text — reproduced here in operative form so the planner does not have to hold two documents open.
**Three of them are corrected by this research (D-08, D-10/D-11, D-16); see §Corrections. Nothing
else below is disturbed.**

- **D-01:** The six dual-slot tests are **six pytest functions under `firestarter/tests/`, driving
  host `g++`** — Phase 125's shape. **Not** a new PIO `test/native/` suite (a Unity suite would move
  the pinned 141 cases / 17 suites that BASE-01, MERGE-06 and every non-regression gate cite, inside
  the one phase whose premise is that nothing else moved). Accepted cost, stated: this harness runs
  in **zero CI legs on this branch**; it is discharged by an in-phase **local** run whose verbatim
  output lands in the evidence artifact. Do not claim CI coverage this branch lacks.
- **D-02:** The dual-slot algorithm is a **HAL-free core with injected flash primitives** (read /
  erase / program), compiled by **both** the py32 backend (real PY32 HAL primitives) and the host
  test (a RAM fake). **The tested code is the shipped code.** Rejected: an independent fake
  reimplementation in the test; rejected: a hand-written stub `py32f071_hal_flash.h`.
- **D-03:** That core lives under **`platform/py32f071/src/`** (e.g. `config_storage_dualslot.cpp` +
  a local header), ARM-only by construction; the host test compiles it **by explicit path**. Zero
  new bytes reach any AVR build from the dual-slot code. Rejected: `src/`; rejected: header-only in
  `include/`.
- **D-04:** Criterion 3's *"empty `git diff` on the test file itself"* is discharged as **two
  commits + a blob-SHA re-hash**: the AVR regression test is written against the **pre-refactor**
  `src/rurp_config_utils.cpp`, proven green, and its blob SHA recorded; the split lands in a later
  commit; the proof is that the recorded SHA **re-hashes identical** and the test is **still green**.
  A path-scoped `git diff` is **corroboration only**.
- **D-05:** The CRC32 implementation is anchored to an **independent known-answer vector** written in
  the test file (`CRC32("123456789") == 0xCBF43926`), **not** to the module under test.
- **D-06:** The seam is **two bool-returning functions** over a byte blob —
  `bool rurp_config_storage_load(void* blob, size_t len)` /
  `bool rurp_config_storage_save(const void* blob, size_t len)`. AVR returns `true`
  unconditionally after `EEPROM.get`; policy calls `rurp_validate_config` either way. Rejected:
  `void`/`void`; rejected: a richer status enum.
- **D-07:** **All four public functions stay in the common policy layer** — `rurp_get_config`,
  `rurp_load_config`, `rurp_save_config`, `rurp_validate_config`, plus the `rurp_config` global — in
  `src/rurp_config_utils.cpp`. Only the two byte-blob calls cross the seam. PR #48's
  `platform/py32f071/src/config.cpp` is **deleted, not reconciled**. `#define CONFIG_START 48` moves
  **into the AVR backend TU**, and CFG-04's regression test asserts it there.
- **D-08:** The AVR backend TU is **`src/boards/rurp_config_storage_eeprom.cpp`** with a new
  `# PY32_EXCLUDED:` line. ARM manifest churn is **three edits**: delete the existing
  `# PY32_EXCLUDED: src/rurp_config_utils.cpp` line, **add** `src/rurp_config_utils.cpp` to
  `FIRESTARTER_COMMON_SOURCES`, **add** the new exclusion for the EEPROM backend. Rejected:
  `#ifdef __AVR__` inside the policy file. → **CORRECTED by C-3: it is four edits, not three.**
- **D-09:** **`include/rurp_shield.h` is NOT touched.** `include/rurp_config_storage.h` is included
  by exactly three TUs: the policy layer and the two backends. (Phase 125's C-1: one `#include` line
  in that header took `pio test -e native` from 141 cases / 141 succeeded to 17 suites / 0.)
- **D-10:** The two config pages sit at the **top of flash**, and `MEMORY`'s `FLASH` `LENGTH`
  **shrinks** by two erase units so `.text` physically cannot grow into them. Reasons: the host's DFU
  erase is **payload-length-scoped**, so an install whose image does not reach the top preserves
  config for free; and Phase 129's bootloader wants the **bottom**. Rejected: fixed addresses without
  shrinking `LENGTH`. → **REFINED by C-5: keep top-of-flash and keep the shrink; make the shrink one
  8 KiB sector rather than two 256 B pages.**
- **D-11:** Expressed as a **second `MEMORY` region plus `PROVIDE` symbols** — a `CONFIG (r)` region
  alongside the shrunk `FLASH`, and `PROVIDE`d `__config_slot_a_start` / `__config_slot_b_start` /
  `__config_page_size`. Rejected: compile-time `-D` defines from CMake.
- **D-12:** **This phase stays firmware-only.** Criterion 5's host consistency is discharged by (a)
  **recording the contract** — `FLASH_BASE` unchanged at `0x08000000`; `FLASH_SIZE` stays the
  **physical 128 KiB** because it is a *refusal envelope*, not an erase bound; plus the reserved
  config base as a named constant — and (b) a **firmware-side gate** asserting the reserved region
  parses out of the linker script and lies inside `0x08000000 + 128 KiB`. **Phase 127 owns the
  cross-repo half.** Rejected: editing `firestarter_app` here.
- **D-13:** A **zero-length `BOOTLOADER` region** at `0x08000000` lands as a **named seam**, so Phase
  129's PCB-03 cites a real symbol rather than prose. **Operator decision, taken over the
  recommendation to omit it** — and it carries a mandatory honest comment: a top-of-flash config
  region grows *downward* without moving anything, but a bottom-of-flash bootloader placeholder does
  **not** have that property; giving it non-zero length later **moves the app's `ORIGIN`**, which is a
  flash-map **migration**, not a resize. The planner must implement it as chosen, and must not
  quietly upgrade it to a real reservation or quietly drop it.
- **D-14:** On a virgin py32, **policy is unchanged**: `rurp_validate_config`'s existing write-back
  fires exactly as it does on AVR, so defaults land in slot A during startup. **Accepted cost,
  stated as a non-claim:** a flash erase+program during startup on first boot, stalling a
  Cortex-M0+; with no PCB that cost is **unmeasurable**, so it is recorded as *not measured*, never
  as *acceptable*. Rejected: RAM-only-until-explicit-save; rejected: deferring the flush until after
  USB enumerates.
- **D-15:** **Blank and both-slots-corrupt both return `false`**, and policy cannot tell them apart —
  it applies defaults and persists, identically. The two CFG-05 tests stay **separately named** and
  assert the same outcome from different inputs. Rejected: distinguishing them for logging; rejected:
  treating two bad CRCs as fatal.
- **D-16:** The write order the real backend commits to, and the one the fake models, is **erase the
  INACTIVE slot → program the record body → program the header/CRC word LAST**. The active slot is
  never touched until the new one is complete. The fake models interruption by aborting the primitive
  sequence **at each step boundary** and asserting `load()` still returns the **old** record.
  Rejected: torn-writes at arbitrary byte offsets and random post-interrupt fill patterns. →
  **CORRECTED by C-2: "program the header/CRC word LAST" is not expressible on this part; the
  property it protects is preserved by a different mechanism.**
- **D-17:** `StoredConfiguration` is **vendored verbatim** from blob `4b1a441` —
  `magic / version(u16) / length(u16) / rurp_configuration_t / sequence(u32) / crc32` — with
  `rurp_configuration_t` embedded **byte-for-byte**. The wrapper's `version` (u16) is **not**
  `CONFIG_VERSION` (the `char[6]` `"VER06"` inside `rurp_configuration_t`). Rejected: narrowing it;
  rejected: redesigning it.

### Claude's Discretion

- **CRC32 implementation.** Bitwise reflected CRC-32 (poly `0xEDB88320`), **no lookup table**, living
  in D-03's HAL-free core TU. Anchored by D-05's known-answer vector.
- **Sequence-number wraparound.** `uint32_t`, monotonically incremented, **no wraparound handling** —
  with a comment stating why (flash endurance bounds the write count far below 2³²). Do not
  "complete" this with a rollover branch that can never execute and can never be tested.
- **Where CFG-01's vendored design lives.** A **focused**
  `firestarter/platform/py32f071/CONFIG-STORAGE.md` containing the in-scope §"Configuration storage"
  subset, citing blob `4b1a441` **by SHA** and naming its closed-PR home (PR #46
  `feature/py32f071-toolchain` / PR #47 `feature/py32f071-full-support`), with an explicit
  **SUPERSEDED** block mapping the document's module names (`storage.cpp`, `gpio.cpp`, `board.cpp`,
  `adc.cpp`, `dac.cpp`, `py32f071_board.h`, `py32f071_pins.h`) to what PR #48 actually built, and
  marking its DAC-VPP and calibration sections out of scope. **Not** a restoration of `PORTING.md`
  under its own name.
- **How CFG-02 is recorded and its ordering proven.** A `## Flash geometry` section in that same doc,
  citing the Puya reference-manual document number, section and table, landing in a commit that
  **precedes** any commit touching `PY32F071xB_FLASH.ld` — proven with `git rev-list --is-ancestor` /
  `git log --oneline --` over the two paths, as an exit code.
- **Evidence artifact.** `126-NONREGRESSION.md`, in the same command / expected / observed row shape
  as `123-`, `124-` and `125-NONREGRESSION.md`, re-executed in the closing plan rather than copied
  from earlier plans' SUMMARY files.
- **The CFG-04 test's compile target must be stable across the refactor.** Default: the test names
  **both** paths (`src/rurp_config_utils.cpp` and `src/boards/rurp_config_storage_eeprom.cpp`) from
  the start, compiles whichever exist, and carries a non-vacuity assertion (at least one path
  resolved **and** the fake `EEPROM.h` recorded at least one call). **Verify this survives contact** —
  if it cannot, the fallback is a single named, justified line change with both blob SHAs recorded.
- Plan/wave decomposition and commit granularity, subject to the ROADMAP's forced internal ordering
  (**AVR move proven first, ARM backend second**) and to the push gate below.
- **Push gate.** Any `git push` / `gh workflow run` for ARM CI evidence is an outward-facing action
  requiring an **explicit operator gate at execute time, structurally separated from any autonomous
  flag** — `--auto`/`--chain` auto-approve human-verify checkpoints regardless of
  `autonomous: false`. Follow Plan 124-11 / 125-05 exactly: **no task runs the command**; the plan
  prints it and stops.

### Deferred Ideas (OUT OF SCOPE)

- Distinguishing "blank" from "both slots corrupt" on the wire (D-15).
- A richer backend status enum (`OK / BLANK / CRC_FAIL / IO_ERROR`) (D-06).
- Reserving real flash for the self-flash bootloader (D-13) — **FUT-N05**.
- Torn-write-at-arbitrary-byte-offset and random-fill power-loss test matrices (D-16).
- Deferring the first-boot config flush until after USB enumerates (D-14).
- Proving that a DFU firmware install preserves config (D-10) — needs a board; carry as an explicit
  non-claim to Phase 130's honesty ledger.
- Shrinking the host's `FLASH_SIZE` to the app region (D-12).
- A native no-op storage backend so the *policy* layer could be exercised by `pio test -e native`.
- **`FUT-ARMSIZE`** — checking ARM flash/RAM into a baseline with a RAM ceiling.
- Any `rurp_configuration_t` field addition or `CONFIG_VERSION` bump (CFG-07 forbids it).
- VPP calibration fields / the DAC closed loop (FUT-VPP / FUT-CAL, v1.26).
- Editing `firestarter_app` (Phase 127 owns the host half, running in parallel).
- Any claim about PY32F071 silicon. Any push to `beta`, tag, release, or public comment (Phase 130).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (REQUIREMENTS.md lines 62–68) | Research Support |
|----|-------------|------------------|
| **CFG-01** | The in-scope design is vendored onto the milestone branch from blob `4b1a441` so the contract is not stranded on closed PRs #46/#47, with the closed branch cited as its origin and the parts superseded by PR #48 marked as such | §Vendoring Source of Truth — blob re-read verbatim this session (195 lines); the in-scope §"Configuration storage" text and the exact `StoredConfiguration` field list are quoted in §Code Examples; the superseded module list is enumerated |
| **CFG-02** | The PY32F071xB flash page/erase-unit size is read from the Puya reference manual and recorded **before** the linker script is edited | §Flash Geometry — **PAGE = 256 B, SECTOR = 8192 B**, from *PY32F07X Reference Manual V0.2* §4.1 / §4.2.1 / Table 4-1, corroborated byte-for-byte by the pinned SDK's `py32f071xB.h:578,580`. C-1 documents the stale HAL header comment that would mislead a reader to 128 B |
| **CFG-03** | `src/rurp_config_utils.cpp` is split by concern — policy stays common, and only a two-function byte-blob backend goes per platform | §Pattern 1 (the seam) + C-11 (C linkage) + C-14 (the seven consumers, none of which move) |
| **CFG-04** | The AVR EEPROM backend is a pure move, proven by a regression test asserting `EEPROM.get`/`put` at offset 48 with `sizeof(rurp_configuration_t)` and byte-identical behaviour to pre-refactor | §Pattern 3 + C-6 (measured sizeofs: AVR 15) + C-12 (the real `EEPROM.get`/`put` template signatures and why the ArduinoFake path must not be used) |
| **CFG-05** | The py32 backend implements dual-slot CRC32 storage, covered by a native fake backend across blank, newest-wins, CRC rejection, both-slots-corrupt, interrupted write, and slot alternation | §Pattern 2 (algorithm) + §Primitive Set (what the fake injects) + C-2 (how "interrupted write" must be modelled given a whole-page program) + §Validation Architecture (six named test functions) |
| **CFG-06** | Two config pages are reserved in `PY32F071xB_FLASH.ld` in **different erase units**, exposed as linker symbols, with the host's `FLASH_BASE`/`FLASH_SIZE` kept consistent | §Recommended Flash Map + C-5 (two adjacent 256 B pages *are* different erase units) + C-10 (the host constants are already exactly right and must not change) |
| **CFG-07** | The `rurp_configuration_t` schema and `CONFIG_VERSION` are unchanged, and PR #48's `config.cpp` policy drift — including a `rurp_save_config()` that persists nothing — is deleted | §The Drift Being Deleted — the four drift points read from `config.cpp` this session; schema pinned by embedding it byte-for-byte per D-17 |

</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` is a meta-repo file. Directives that bind this phase:

| Directive | Bearing on Phase 126 |
|-----------|----------------------|
| The meta repo tracks only `.planning/` and `.claude/`; the sub-repos are **not committed here** | Every firmware edit is committed **inside** `/workspaces/firestarter` on `v1.23-py32f071-integration`; only `126-*.md` artifacts are committed in the meta repo |
| **Constants/flag bits are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` — change both together** | **Does not fire.** This phase adds no wire-visible constant. The two config-storage functions are internal; `CONFIG_VERSION` is unchanged by CFG-07. Nothing crosses the serial protocol |
| **Serial-protocol changes must be kept in sync between `serial_comm.py` and `firestarter.cpp`** | **Does not fire** — D-15's refusal to distinguish blank-from-corrupt on the wire is precisely what keeps it from firing |
| Hardware calibration (R1/R2, board revision) is persisted in Arduino EEPROM via `rurp_configuration_t` | This is the struct the phase moves *behind* a seam without changing. The AVR persistence path must remain byte-identical (CFG-04) |
| Firmware built with `pio run -e uno` / `-e leonardo`; `pio test` for unit tests | The three AVR builds are the size-measurement mechanism; `pio test -e native` / `-e native_nodevtools` are the pinned 141/17 counts |

---

## Summary

The one genuine unknown this phase was flagged for — the PY32F071xB flash page and erase-unit size,
"stated nowhere in-tree" per A-6/R-8 — is now answered from primary sources and corroborated twice:
**the page is 256 bytes and the sector is 8192 bytes.** Both figures come from *PY32F07X Reference
Manual V0.2* §4.1/§4.2.1 and Table 4-1, and independently from the pinned SDK's own part header
`py32f071xB.h:578,580` at the exact FetchContent commit the build compiles. This matters more than a
number: the widely repeated PY32 figures (128 B page / 4 KiB sector) are true for PY32F030/F003 and
**wrong here**, and the SDK's own `py32f071_hal_flash.h:268` still carries the stale comment
*"Program 128bytes at a specified address"* while the code beneath it writes 256. CFG-02's insistence
on reading the manual before touching the linker script is not ceremony — there are two plausible
wrong answers sitting in the two documents a hurried reader would reach for first.

Reading the manual then invalidates a prescription the CONTEXT locked. **The only programming
primitive on this part is a full 256-byte page write** — `IS_FLASH_TYPEPROGRAM` accepts exactly one
value, `FLASH_Program_Page` writes 64 words unconditionally, and RM §4.2.3.2 states a non-32-bit
write raises a hard fault. D-16's "program the record body → program the header/CRC word **LAST**"
therefore cannot be executed as written: there is no primitive that writes one word. The *property*
D-16 exists to protect — blob `4b1a441`'s *"a failed or interrupted write must leave the previous
record usable"* — survives intact through a different mechanism (the active slot is never touched,
and a CRC over a partially-programmed page rejects it), and the interrupted-write test becomes
*stronger*, not weaker, because the fake can abort mid-burst at word granularity, faithfully
modelling what `FLASH_Program_Page` actually does. Two further discoveries are pure omissions that
would surface as an ARM link failure and a silicon-only failure respectively:
`py32f071_hal_flash.c` **is not in the ARM build's source list**, and the flash timing registers RM
§4.2.3.6 says the operation *"will fail"* without are configured **inside** the HAL entry points —
so the backend must call `HAL_FLASH_Program`/`HAL_FLASH_Erase` and must not poke registers directly.

Everything else the CONTEXT asserts about the tree was re-verified and holds: the native envs do not
compile `rurp_config_utils.cpp`, so the pinned 141/17 counts cannot move; the four config functions
have C linkage via `rurp_shield.h:11–12`; the seven call sites of the config API all sit above the
seam and none of them changes; Leonardo's headroom is **2656 B** (23954/32256 uno, 24004/32384
uno328pb, 26016/28672 leonardo). One measurement the phase must not trip over: `long` is **8 bytes**
on this host, so `sizeof(rurp_configuration_t)` is **32 on the host, 15 on AVR** (both measured this
session) and 20 on ARM — three different on-flash record sizes across the three compilers, with
`-m32` unavailable in this devcontainer. No test may hardcode a size or an offset.

**Primary recommendation:** Land CFG-02 as a documentation commit citing *PY32F07X RM V0.2 §4.1 /
§4.2.1 / Table 4-1* **and** `py32f071xB.h:578,580` (two independent anchors, one of which is
machine-checkable in-tree after a `cmake` configure), then reserve **Sector 15 in its entirety**
(`0x0801E000`–`0x0801FFFF`, `FLASH` `LENGTH` 128K → 120K) with slot A at `0x0801E000` and slot B at
`0x0801E100` — two different *page* erase units inside one sector-aligned reservation, which is the
only placement that keeps the atomicity property under **either** erase granularity and cannot be
clipped by a sector-granular DFU erase. Build the dual-slot core against three injected primitives
(`read`, `erase_page`, `program_page(256 B)`) so the shipped code is the tested code, and correct
D-16's commit step to "the page program completing **is** the commit".

---

## Corrections to CONTEXT.md / ROADMAP.md

Ordered by consequence. Each is sourced; C-2, C-3 and C-5 change what the plans must contain.

### C-1 — The flash geometry, and the two wrong numbers a reader would otherwise find [VERIFIED]

**PAGE = 256 bytes. SECTOR = 8192 bytes (8 KBytes). Main flash = 128 KBytes = 16 sectors = 512
pages, `0x08000000`–`0x0801FFFF`.**

Two independent authoritative sources agree exactly:

- *PY32F07X Reference Manual V0.2*, **§4.1 "Key features"** (p.34), verbatim: *"Page size: 256
  Bytes"*, *"Sector size: 8 KBytes"*, *"Main flash block: maximum 128 KBytes"*. **§4.2.1 "Flash
  structure"** (p.34): *"Page size is 256 Bytes, Sector size is 8 KBytes."* **Table 4-1 "Flash
  structure and boundary addresses"** gives the sector map, including `Sector 14 | Page 448-479 |
  0x0801C000-0x0801DFFF | 8 KBytes` and `Sector 15 | Page 480-511 | 0x0801E000-0x0801FFFF | 8
  KBytes`. [VERIFIED: PDF downloaded from puyasemi.com and text-extracted locally, 913 pages]
- Pinned SDK `OpenPuya/PY32F071_Firmware` @ `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (the exact
  `GIT_TAG` in `platform/py32f071/CMakeLists.txt:16`),
  `Drivers/CMSIS/Device/PY32F071/Include/py32f071xB.h`:
  ```c
  #define FLASH_BASE            (0x08000000UL)   /*!< FLASH base address */
  #define FLASH_END             (0x0801FFFFUL)   /*!< FLASH end address */
  #define FLASH_SIZE            (FLASH_END - FLASH_BASE + 1)
  #define FLASH_PAGE_SIZE       0x00000100U      /*!< FLASH Page Size, 256 Bytes */
  #define FLASH_PAGE_NB         (FLASH_SIZE / FLASH_PAGE_SIZE)
  #define FLASH_SECTOR_SIZE     0x00002000U      /*!< FLASH Sector Size, 8192 Bytes */
  #define FLASH_SECTOR_NB       (FLASH_SIZE / FLASH_SECTOR_SIZE)
  ```
  [VERIFIED: `gh api` on the pinned commit, lines 575–581]

**The two traps.** (a) The widely circulated PY32 figures are **128 B page / 4 KiB sector** — correct
for PY32F030/PY32F003, wrong for PY32F071. A WebSearch this session returned exactly that wrong pair
as an assertion about PY32F071xB; it is contradicted by both primary sources above. (b) Worse,
because it is *inside the pinned SDK*: `py32f071_hal_flash.h:268` reads
`#define FLASH_TYPEPROGRAM_PAGE (FLASH_CR_PG) /*!<Program 128bytes at a specified address.*/` — a
stale comment carried over from the smaller part, sitting directly above code that writes 256 bytes.
A reader who trusted either would reserve half the space needed. **Cite the RM and the part header;
never the HAL header comment.**

### C-2 — D-16's "program the header/CRC word LAST" is not implementable on this part [VERIFIED]

There is exactly one programming primitive, and it writes a whole page.

- `py32f071_hal_flash.h:631`: `#define IS_FLASH_TYPEPROGRAM(__VALUE__) ((__VALUE__) == FLASH_TYPEPROGRAM_PAGE)`
  — one accepted value, no word/halfword/byte variant. [VERIFIED: pinned SDK]
- `py32f071_hal_flash.c` `FLASH_Program_Page()` writes **64 uint32 words unconditionally**:
  `while(index<64U) { *(uint32_t *)dest = *src; src += 1U; dest += 4U; index++; if(index==63) { SET_BIT(FLASH->CR, FLASH_CR_PGSTRT); } }`,
  the whole burst wrapped in `__disable_irq()` / `__set_PRIMASK()`. [VERIFIED: pinned SDK]
- RM §4.2.3.2 (p.36): *"The Flash memory can be programmed the entire page in units of 32 bits each
  time (hardfault will be generated when the half word or byte operation is performed)… Any non
  32-bit write will cause a hard fault interrupt."* §4.2.3.2's sequence (p.37) confirms the shape:
  *"Programming to the target address from the 1st to 63rd word… Set the PGSTRT in FLASH_CR
  register… Write the 64th word."* [VERIFIED: RM]

**Consequences the planner must absorb:**

1. **The record cannot be committed by a trailing word write.** Recommended correction, minimal and
   property-preserving: **the completion of the page program *is* the commit.** The active slot is
   still never touched (D-16's actual guarantee), and a page interrupted mid-burst fails CRC on the
   next `load()` and is rejected — which is what makes the previous record still usable. Record this
   as an explicit amendment to D-16 with the RM citation, not as a silent reinterpretation.
   *Alternative if a distinct commit step is wanted:* give each slot **two** pages (body page, then
   commit page holding `sequence`+`crc32`). It costs two more pages and a second erase, and it is
   the only way to keep D-16's literal wording. Recommend against — it adds a failure mode (body
   valid, commit page torn) for no gain over CRC rejection.
2. **The interrupted-write test gets *better*, not weaker.** Because `FLASH_Program_Page` is 64
   discrete word stores, the RAM fake can abort after *N* words for `N` in `{0, 1, 32, 63, 64}` and
   assert `load()` still returns the **old** record. That is a faithful model of the real primitive's
   internals, not a synthetic torn-write matrix — so it does **not** fall foul of D-16's rejection of
   "torn-writes at arbitrary byte offsets" (which was about arbitrary *byte* offsets against
   unobservable controller behaviour; word-store boundaries are observable in the SDK source).
3. **A 256-byte, 4-byte-aligned staging buffer is mandatory.** `HAL_FLASH_Program` reads 64 words
   from `DataAddr` regardless of how big the caller's object is. Passing `&record` (36 bytes on ARM)
   would program 220 bytes of adjacent RAM into flash — a live buffer-over-read. The backend must
   build the page in a `uint32_t page[64]` (or `alignas(4) uint8_t page[256]`), zero/`0xFF`-fill the
   tail, and pass that.

### C-3 — `py32f071_hal_flash.c` is NOT in the ARM build; D-08's "three edits" is four [VERIFIED]

`grep -c "hal_flash" platform/py32f071/CMakeLists.txt` returns **0**. `PY32_SDK_SOURCES`
(`CMakeLists.txt:65–80`) names `py32f071_hal.c`, `_rcc.c`, `_rcc_ex.c`, `_gpio.c`, `_cortex.c`,
`_pwr.c`, `_dma.c`, `_adc.c`, `_adc_ex.c`, `_tim.c` and three CherryUSB files — **no flash driver**.
`platform/py32f071/include/py32f071_hal_conf.h:10` already sets `HAL_FLASH_MODULE_ENABLED` and `:53`
already includes `py32f071_hal_flash.h`, so the *header* is in scope today and the code compiles;
the first call to `HAL_FLASH_Unlock`/`Program`/`Erase` will fail at **link** with undefined
references. [VERIFIED: local grep + `gh api` on the pinned SDK]

So `platform/py32f071/CMakeLists.txt` takes **four** edits, not D-08's three:

1. delete `# PY32_EXCLUDED: src/rurp_config_utils.cpp` (line 34)
2. add `"${REPOSITORY_ROOT}/src/rurp_config_utils.cpp"` to `FIRESTARTER_COMMON_SOURCES`
3. add `# PY32_EXCLUDED: src/boards/rurp_config_storage_eeprom.cpp -- AVR EEPROM backend, no ARM analogue`
4. **add `"${PY32_SDK_ROOT}/Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_flash.c"` to `PY32_SDK_SOURCES`**
   — plus the two new `PY32_PLATFORM_SOURCES` entries and the `src/config.cpp` deletion, which D-08
   did not count as manifest churn but which are the same file.

**`check_cmake_manifest.py` cannot catch the omission.** Its own docstring states `PY32_SDK_SOURCES`
is *"STRUCTURALLY EXEMPT from resolution — a property of FetchContent"*, and its reverse check only
inspects `src/*.cpp`. Nothing in this repo will tell you edit 4 is missing; only a `cmake` build
will, and `cmake`/`ninja`/`arm-none-eabi-gcc` are **absent from this devcontainer**. This is
therefore a **CI-only** failure mode discoverable solely via the gated `py32f071.yml` workflow run.
The planner should treat edit 4 as a named, separately-verified checklist item in the plan that
touches `CMakeLists.txt`, and the ARM-evidence push gate as the only place it can be confirmed.

### C-4 — The backend must go through the HAL, never raw FLASH registers [VERIFIED]

RM **§4.2.3.6 "Program and erase time configuration"** (p.39), verbatim: *"Flash write and erase
times need to be tightly controlled, otherwise the operation will fail. If you need to write and
erase the Flash, you need to FLASH_PERTPE, FLASH_SMERTPE, FLASH_PRGTPE, FLASH_PRETPE to configure the
Flash Write and Erase time control registers according to the HSI output frequency."*

Those registers are set by `__HAL_FLASH_TIMMING_SEQUENCE_CONFIG()` (`py32f071_hal_flash.h:497–505`),
which reads `RCC->ICSCR & RCC_ICSCR_HSI_FS` to index a factory `_FlashTimmingParam` table and loads
`TS0/TS1/TS3/TS2P/TPS3/PERTPE/SMERTPE/PRGTPE/PRETPE`. Critically, it is invoked **inside** the HAL
entry points — `py32f071_hal_flash.c:416` (`HAL_FLASH_Erase`), `:526` (`Erase_IT`), `:605`
(`HAL_FLASH_Program`), `:674` (`Program_IT`), `:905` (OB). [VERIFIED: pinned SDK]

A hand-rolled `FLASH->CR` sequence would look textbook-correct, pass review, compile, and **fail on
silicon** with no local way to detect it. D-02's "real PY32 HAL primitives" must mean literally
`HAL_FLASH_Unlock` / `HAL_FLASH_Erase` / `HAL_FLASH_Program` / `HAL_FLASH_Lock`. Worth a one-line
comment in `config_storage_flash.cpp` citing RM §4.2.3.6, because the reason is invisible from the
call site.

**Related prerequisite, already satisfied:** RM §4.2.3 (p.35) — *"For program and erase operations,
the HSI must be turned on."* `platform/py32f071/src/main.cpp:25–27` sets
`oscillator.HSIState = RCC_HSI_ON`, `HSIDiv = RCC_HSI_DIV1`,
`HSICalibrationValue = RCC_HSICALIBRATION_24MHz`, and `:32` makes HSI the PLL source. No change
needed — but record it, because a future clock refactor that turns HSI off silently breaks config
persistence.

### C-5 — "Different erase units" is cheap here; the reservation should be sector-aligned anyway [VERIFIED + reasoned]

The research SUMMARY's warning — *"two slots in one erase unit destroys the atomicity property that
is the entire point"* — is satisfied by **two adjacent 256-byte pages**, because page erase is a
first-class primitive on this part: `FLASH_TYPEERASE_PAGEERASE` with `PageAddress`/`NbPages`
(`hal_flash.h:146`), implemented by `FLASH_PageErase(address)` stepping `FLASH_PAGE_SIZE`
(`hal_flash.c:451`), and RM **§4.2.3.3 "Page erase"** (p.37) documents the register sequence. The only
constraint the HAL imposes is range (`IS_FLASH_NB_PAGES` checks `>= FLASH_BASE` and `<= FLASH_BASE +
FLASH_SIZE - 1`) — **no sector alignment is required for a page erase.** [VERIFIED: pinned SDK + RM]

So CFG-06 is literally satisfiable by 512 bytes. But D-10's own justification argues against the
minimal form. D-10 relies on the host's payload-scoped DFU erase to preserve config; DFU erase
granularity is **device-published** (`parse_dfuse_layout(interface.name)`), and if the bootloader
publishes 8 KiB blocks then erasing the app's last block wipes anything sharing that sector. With a
512 B reservation at `0x0801FE00`, the app region ends at `0x0801FDFF` — *inside Sector 15* — so a
large image's final erase block is exactly the block holding config. That is a live hazard, and D-10
was chosen to avoid needing one.

**Recommended flash map — reserve Sector 15 whole:**

| Symbol / region | Address | Size | Note |
|---|---|---|---|
| `BOOTLOADER` (D-13 seam) | `0x08000000` | **0** | zero-length named seam; giving it size later **moves `ORIGIN`** = migration, not resize |
| `FLASH` (app) | `0x08000000` | **120K** (`0x1E000`) | shrunk from 128K so `.text` cannot reach config |
| `CONFIG` | `0x0801E000` | **8K** (Sector 15, pages 480–511) | sector-aligned ⇒ immune to a sector-granular erase of the app region |
| `__config_slot_a_start` | `0x0801E000` | 256 B | page 480 |
| `__config_slot_b_start` | `0x0801E100` | 256 B | page 481 — a **different page erase unit** |
| `__config_page_size` | `256` | — | matches `FLASH_PAGE_SIZE`, assertable against the RM figure |

This keeps every locked element of D-10 and D-11 (top of flash, `LENGTH` shrunk, second `MEMORY`
region, `PROVIDE`d symbols) and changes only the *quantum* of the shrink: one 8 KiB sector rather
than two 256 B pages. Cost: 7680 B of the reserved 8192 B is slack — 6.25% of flash, and slack that
FUT-N05 or additional slots can later claim without moving any address. **Flag to the operator as a
one-line confirmation**, since D-10's text says "shrinks by two erase units"; both readings are
defensible and this one removes a hazard rather than stating it (the `<specifics>` tie-breaker).

### C-6 — `long` is 8 bytes on the host: three different record sizes, and `-m32` is unavailable [VERIFIED, measured]

Measured this session:

| Compiler | `sizeof(long)` | `sizeof(rurp_configuration_t)` | `sizeof(StoredConfiguration)` | `offsetof(…, crc32)` |
|---|---|---|---|---|
| host `g++ 14.2.0` (x86-64) | 8 | **32** (r1@8, r2@16, hw@24) | **48** | 44 |
| `avr-g++ 7.3.0` (atmega328p) | 4 | **15** | **31** | 27 |
| `arm-none-eabi-gcc` (AAPCS, ILP32) | 4 | **20** *(computed)* | **36** *(computed)* | 32 *(computed)* |

[VERIFIED for host and AVR by compilation; the ARM row is [ASSUMED] from AAPCS ILP32 alignment rules
— it cannot be measured in this devcontainer, and it is deliberately **not load-bearing**: all three
fit comfortably inside one 256-byte page, which is the only property any test needs.]

`g++ -m32` **fails** here (`bits/libc-header-start.h: No such file or directory` — no multilib), so
the host test cannot be coerced into the target layout.

**What this forbids:** any test asserting a literal record size, a literal field offset, or a
literal `EEPROM.get` length. **What it requires:** assert symbolically (`sizeof(rurp_configuration_t)`,
`offsetof(...)`) and add one relational assertion — `sizeof(StoredConfiguration) <=
__config_page_size` — which is the claim that actually matters and is true on all three. It also
vindicates D-17's `length` field: the record is self-describing, so a cross-width read is detectable
rather than silently misparsed.

**Reconciling this with D-17 and D-02.** Keep the vendored `StoredConfiguration` exactly as D-17
locks it (it is the ARM on-flash format), but have the HAL-free core operate on the D-06 seam's
`(void* blob, size_t len)` plus the header fields — the core then exercises the *algorithm*
(scan/validate/select/alternate) without any dependency on host `sizeof(long)`. The shipped code is
still the tested code; only the payload width differs between the two compilations, and `length`
records it.

### C-7 — The bus stalls during erase/program; RM gives D-14's non-claim a mechanism [VERIFIED]

RM §4.2.3 (p.35), verbatim:

- *"If a reset occurs during Flash program and erase operations, the contents of the Flash memory are
  not protected."* — the exact hazard dual-slot + CRC exists for. Quote it in `CONFIG-STORAGE.md`.
- *"During a program and erase operations to the Flash memory, any attempt to read the Flash memory
  will stall the bus. The read operation will proceed correctly once the program and erase operations
  has completed. This means that code or data fetches cannot be made while programming and erasing
  operations are in progress."*

So the Cortex-M0+ **cannot fetch instructions** while flash is busy — no RWW. Combined with the HAL's
`__disable_irq()` across the 64-word burst, **no interrupt is serviced for the duration of an erase
or a program**, USB CDC included. This is in direct tension with blob `4b1a441`'s own architectural
requirement *"no long global interrupt masking because USB must continue to run"*. The RM gives no
erase/program timing figures (§4.2.3.6 only points at the timing registers; endurance and timing live
in the datasheet, not this manual — **searched pp.29–60, not found**).

D-14's framing is therefore exactly right and should be strengthened, not softened: keep the
write-back on first boot (one policy, both platforms), and record the cost as **not measured** with
this mechanism cited. Do **not** convert it into a numeric claim; do not schedule work against it.
The Validation Ceiling's forbidden-claim list applies.

### C-8 — Always erase before programming; the HAL skips a step the RM requires [VERIFIED]

RM §4.2.3.2's programming sequence (p.37), step 2: *"If no Flash memory erase or program operation is
ongoing, the software reads out the 64 words of the page (if the page already has data stored,
perform this step, otherwise skip this step)."*

`FLASH_Program_Page` does **not** perform that read-out. The HAL is therefore only safe on a **blank**
page. This turns "erase the inactive slot first" from a design preference into a hard correctness
requirement, and it means the backend must never program over a slot it has not just erased. Assert
it in the fake: `program_page` on a non-erased page is a **test failure**, not a silent overwrite —
that makes the constraint enforced rather than remembered.

### C-9 — The host's DFU fallback erase grid (2048) matches neither the page nor the sector [VERIFIED]

`firestarter_app_py32/firestarter/py32_dfu.py:109`: `DEFAULT_ERASE_PAGE_SIZE = 2048  # fallback when
the device publishes no layout`, under a comment block citing *"Puya UM1504 +
PY32F071xB_FLASH.ld on the firmware branch"*. 2048 is neither 256 (page) nor 8192 (sector). It is
only used when `parse_dfuse_layout()` returns nothing, and `erase_addresses(layout, base,
len(payload), self.erase_page_size)` prefers the device-published layout — so it is not a defect this
phase must fix. **Record it in the contract for Phase 127** (D-12 explicitly makes recording the
contract this phase's job): if the fallback ever fires, a 2048-byte grid straddles neither boundary
cleanly. Do not edit the host here.

### C-10 — The host's `FLASH_BASE`/`FLASH_SIZE` are already exactly right [VERIFIED]

`py32_dfu.py:107–108`: `FLASH_BASE = 0x08000000`, `FLASH_SIZE = 128 * 1024`. The part header gives
`FLASH_BASE 0x08000000` and `FLASH_END 0x0801FFFF` ⇒ 131072 bytes. **They agree exactly.** Criterion
5's *"the host's `FLASH_BASE`/`FLASH_SIZE` stay consistent with"* the linker symbols is discharged by
**not changing either**, which is what D-12 already decided — now with a primary source behind it
rather than an inference. Note the asymmetry explicitly in the contract: the linker's `FLASH`
`LENGTH` becomes 120K while the host's `FLASH_SIZE` stays 128K, and that is **correct, not drift** —
one is an app-region bound, the other a physical refusal envelope (`_check_envelope`, `:648`).

### C-11 — The config API has C linkage; the seam header must match [VERIFIED]

`include/rurp_shield.h:11–12` opens `#ifdef __cplusplus / extern "C" {` and closes at `:161–162`. All
four config declarations (`:61`, `:150–152`) are therefore **`extern "C"`**. `platform/py32f071/src/config.cpp`
spells `extern "C"` explicitly on each definition; `src/rurp_config_utils.cpp` does not need to
because it includes the header first. The new `include/rurp_config_storage.h` must use the same
`#ifdef __cplusplus / extern "C" {` wrapper — free, and it prevents a mangled-vs-unmangled link
failure that would only appear on the ARM target. `rurp_shield.h:17` already provides `<string.h>`,
so the policy TU keeps `strcmp`/`strcpy` after the split with no new include.

### C-12 — ArduinoFake *does* ship `EEPROM.h`, but not at a path a pytest harness may use [VERIFIED]

`.pio/libdeps/native/ArduinoFake/src/EEPROM.h` and `EEPROMFake.{h,cpp}` exist — but only under
`.pio/libdeps/<env>/`, a gitignored PlatformIO artifact that exists solely after a native build. A
`tests/` pytest+g++ harness must **not** depend on it (it would pass on a warm tree and fail on a
clean checkout — the fail-open shape A-7 is about). Hand-write a minimal fake `EEPROM.h` alongside
the test, per Phase 125's shim pattern.

The real signatures the fake must mirror, from
`framework-arduino-avr/libraries/EEPROM/src/EEPROM.h:130–142`:

```cpp
template< typename T > T &get( int idx, T &t );            // byte loop, sizeof(T) bytes
template< typename T > const T &put( int idx, const T &t ); // byte loop, per-byte .update()
```

Note `put` uses **`update()` semantics** (read-then-write-only-if-changed) per byte. The regression
test asserts the *(offset, size)* pair — `48` and `sizeof(rurp_configuration_t)` — so the fake should
record `(idx, sizeof(T))` per call and the test should assert on that recording, which is exactly the
non-vacuity hook the Discretion section asks for ("the fake `EEPROM.h` recorded at least one call").

### C-13 — The pinned native counts structurally cannot move [VERIFIED]

`platformio.ini:163/252/290` — all three native envs use
`build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c> +<operation_utils.cpp>`.
`src/rurp_config_utils.cpp` is not in that set today and neither new backend TU will be. Further,
`test/native/avr/test_data_input/host_stubs.cpp:62–71` already defines a stub
`extern "C" rurp_configuration_t* rurp_get_config()` for the header-inlined consumer in
`include/rurp_hw_rev_utils.h:95,101` — so the native link does not reach the policy layer either way.
**141 cases / 17 suites cannot move from this phase's edits.** Confirms D-01's arithmetic; still
measure it, per "assert counts, never 'tests pass'".

### C-14 — Seven consumers of the config API, none of which changes [VERIFIED]

`src/firestarter.cpp:40` (`rurp_load_config()`), `:103` (`rurp_get_config()`), `:109`
(`rurp_save_config(config)`); `src/boards/rurp_common.cpp:53`; `include/rurp_hw_rev_utils.h:95,101`;
`src/hardware_operations.cpp:106,118`; `platform/py32f071/src/py32f071_rurp_shield.cpp:297`. Every one
sits **above** the seam and calls only the four public functions. The split is invisible to all of
them — which is the structural argument that CFG-04's "byte-identical behaviour" is achievable, and
the reason no golden trace can move.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Config schema (`rurp_configuration_t`, `CONFIG_VERSION`) | Common headers (`include/rurp_types.h`, `include/rurp_shield.h`) | — | CFG-07 pins both unchanged; embedding the struct byte-for-byte (D-17) makes "unchanged" structural rather than asserted |
| Config **policy** (get / load / save / validate + defaults write-back) | Common firmware (`src/rurp_config_utils.cpp`) | — | CFG-03 verbatim; D-07 keeps all four functions common so there is one validate policy on both platforms (D-14) |
| Config **byte-blob persistence** | Per-platform backend (`include/rurp_config_storage.h`, two impls) | — | The seam is exactly two bool functions (D-06); it is the *only* thing that varies by platform |
| AVR persistence mechanism | AVR board layer (`src/boards/rurp_config_storage_eeprom.cpp`) | — | `EEPROM.get`/`put` at offset 48; `CONFIG_START` is an EEPROM address and is meaningless above the seam (D-07) |
| py32 dual-slot **algorithm** (scan, CRC, newest-wins, alternate) | ARM platform, HAL-free core (`platform/py32f071/src/config_storage_dualslot.cpp`) | Host test compiles it by path | D-02/D-03: the tested code is the shipped code, at zero AVR byte cost |
| py32 flash **primitives** (unlock, page erase, page program, lock) | ARM platform, HAL glue (`platform/py32f071/src/config_storage_flash.cpp`) | Puya HAL (`py32f071_hal_flash.c`) | C-4: must route through the HAL, which owns the §4.2.3.6 timing-register configuration |
| Flash **address map** | Linker script (`PY32F071xB_FLASH.ld`) | CFG-02 doc | D-11: the linker structurally enforces non-overlap; a `-D` define would split the map across two files that can disagree |
| Install-time flash envelope | Host (`firestarter_app`, Phase 127) | Contract recorded here | D-12: parallel phase, disjoint files, shared contract |

---

## Standard Stack

### Core

**No new external dependency is introduced by this phase.** Everything needed is already pinned.

| Component | Version / pin | Purpose | Why standard |
|-----------|---------------|---------|--------------|
| Puya PY32F071 SDK (`OpenPuya/PY32F071_Firmware`) | `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (`CMakeLists.txt:16`) | `HAL_FLASH_Unlock/Lock/Program/Erase` — the only sanctioned flash access path | Vendor HAL; owns the §4.2.3.6 timing-register sequence a hand-rolled driver would skip (C-4) |
| `py32f071_hal_flash.c` | same pin | The flash driver TU | **Must be added to `PY32_SDK_SOURCES` — it is absent today (C-3)** |
| `pytest` | 9.1.1 (installed) | The six CFG-05 tests + the CFG-04 regression test | D-01; Phase 125's precedent, and `tests/` is PIO-invisible so counts don't move |
| host `g++` | Debian 14.2.0 | Compiles the HAL-free core and the policy layer under test | D-02/D-03; Phase 125's `test_vpp_seam_manual_on_every_board.py` shape |
| `avr-g++` | 7.3.0 (`~/.platformio/packages/toolchain-atmelavr/bin/`) | AVR size measurement via `pio run` | The A-5 flash constraint is measured, not asserted |
| PlatformIO Core | 6.1.19 | `pio run -e {uno,uno328pb,leonardo}`, `pio test -e native{,_nodevtools}` | Existing gates; `check_size_baseline.py` reads their output |

### Supporting

| Component | Purpose | When to use |
|-----------|---------|-------------|
| `scripts/check_size_baseline.py` + `scripts/baseline/size_baseline.json` | Strict-equality AVR flash/RAM comparison, **already armed** | Immediately after the AVR move, before any ARM work — so a delta is attributable |
| `scripts/check_cmake_manifest.py` | `PY32_EXCLUDED` / `FIRESTARTER_COMMON_SOURCES` reverse check | Makes D-08 edits 1–3 non-optional. **Blind to edit 4** (C-3) |
| `scripts/check_build_warnings.py` | Native warning watermark (reads the same baseline via `FIRESTARTER_SIZE_BASELINE`) | Part of the non-regression sweep |
| `pypdf` | Extracted the RM text **for this research only** | Not a project dependency; do **not** add it to any manifest |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| HAL `HAL_FLASH_Program` | Direct `FLASH->CR` register sequence | **Rejected** — skips `__HAL_FLASH_TIMMING_SEQUENCE_CONFIG()`; RM §4.2.3.6 says the operation *"will fail"* (C-4). Would pass review and fail on silicon |
| Bitwise CRC-32 (`0xEDB88320`) | 256-entry table | Locked as Discretion: ~1 KiB of flash for an operation that runs at boot and on rare writes. Also: reusing `rurp_serial_utils.cpp:378`'s CRC8-CCITT `PROGMEM` table is wrong — it is CRC8 and AVR-shaped |
| Two 256 B config pages (512 B reservation) | One whole 8 KiB sector (C-5) | Sector-aligned costs 7680 B of slack but is immune to a sector-granular DFU erase; the 512 B form leaves a stated hazard instead of removing one |
| Single-page slot, commit = program completion (C-2) | Two-page slot with a separate commit page | Two pages keeps D-16's literal wording but adds a "body valid / commit torn" failure mode CRC already covers |
| `pytest` + `g++` in `tests/` | New PIO `test/native/` Unity suite | **Rejected by D-01** — would move the pinned 141/17 counts inside the phase whose premise is that nothing else moved |

**Installation:** none. No `npm`, `pip`, `cargo` or PlatformIO library is added.

---

## Package Legitimacy Audit

**This phase installs no external packages.** All firmware dependencies are already pinned in-tree
(the Puya SDK by `GIT_TAG` at a full 40-char SHA; `lib/jsmn` vendored; `ArduinoFake@^0.4.0` already in
`platformio.ini` for native envs). All host-side tooling (`pytest`, `g++`, `avr-g++`, `pio`) is
already installed in the devcontainer.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| — | — | — | — | — | — | No package installs in this phase |

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

**Supply-chain note that does apply.** The one external artifact this phase newly *compiles* is
`py32f071_hal_flash.c` from the FetchContent SDK (C-3). It is pinned to a full commit SHA
(`0ed2f4b4d3391eccfd4491006a30295fd78e32c2`), not a tag or branch, so it is immutable; the file was
read at that SHA during this research and matches the HAL contract documented above. `GIT_SHALLOW
FALSE` means the SHA is verifiable. **No new fetch source, no new pin, no version bump** — the phase
enables a file already inside an already-pinned dependency. If the planner is tempted to bump the SDK
pin for any reason, that is a separate decision with its own blast radius (it would move every ARM
size figure) and does not belong in this phase.

---

## Architecture Patterns

### System Architecture Diagram

```
                    ┌──────────────────────────────────────────────┐
   command layer    │ firestarter.cpp:40 rurp_load_config()        │
   (7 call sites,   │ firestarter.cpp:99/109 get/save             │
    C-14, unchanged)│ hardware_operations.cpp:106/119              │
                    │ rurp_hw_rev_utils.h:95/101 (header-inlined)  │
                    │ rurp_common.cpp:53  py32..shield.cpp:297     │
                    └───────────────────────┬──────────────────────┘
                                            │  4 public fns, extern "C" (C-11)
                                            │  declared rurp_shield.h:61,145-152  (NOT TOUCHED, D-09)
                    ┌───────────────────────▼──────────────────────┐
   COMMON POLICY    │  src/rurp_config_utils.cpp        (CFG-03)   │
   one policy,      │  rurp_config global · get · load · save      │
   both platforms   │  validate  ──► version mismatch? write back  │
   (D-07, D-14)     │                        (line 38 behaviour)   │
                    └───────────────────────┬──────────────────────┘
                                            │
                       ══════ THE SEAM ══════│══════ include/rurp_config_storage.h (NEW, D-06)
                       2 bool fns over a byte blob; 3 including TUs only (D-09)
                       load(void* blob, size_t len) / save(const void*, size_t)
                                            │
                 ┌──────────────────────────┴───────────────────────┐
                 │                                                  │
      ┌──────────▼───────────┐                    ┌─────────────────▼──────────────────┐
      │ AVR BACKEND (NEW)    │                    │ ARM BACKEND (NEW, 2 TUs)           │
      │ src/boards/          │                    │ platform/py32f071/src/             │
      │  rurp_config_storage │                    │                                    │
      │  _eeprom.cpp         │                    │  config_storage_dualslot.cpp       │
      │                      │                    │   ── HAL-FREE CORE (D-02/D-03) ──  │
      │ CONFIG_START 48      │                    │   scan A+B → magic? CRC32? →       │
      │ EEPROM.get / .put    │                    │   highest sequence wins            │
      │ returns true always  │                    │   save: erase INACTIVE → build     │
      │ (behaviour identical │                    │   256B page → program → done=commit│
      │  to pre-refactor,    │                    │              │  3 injected prims   │
      │  CFG-04)             │                    │              │  read/erase/program │
      └──────────┬───────────┘                    └──────┬───────┴─────────┬───────────┘
                 │                                       │                 │
        ┌────────▼─────────┐                   ┌─────────▼────────┐  ┌─────▼──────────────┐
        │ ATmega EEPROM    │                   │ config_storage_  │  │ RAM FAKE           │
        │ 3 AVR targets    │                   │ flash.cpp        │  │ tests/ (pytest+g++)│
        │ size gate armed  │                   │ HAL_FLASH_*      │  │ abort-after-N-words│
        └──────────────────┘                   │ (C-4: never raw  │  │ ⇒ interrupted write│
                                               │  registers)      │  │ 6 named tests      │
                                               └─────────┬────────┘  └────────────────────┘
                                                         │
                                    ┌────────────────────▼─────────────────────┐
                                    │ PY32F071xB FLASH  (RM V0.2 Table 4-1)    │
                                    │ page 256 B · sector 8 KiB · 128 KiB total│
                                    │ ┌──────────────────────────────────────┐ │
                                    │ │ FLASH app 0x08000000 .. 0x0801DFFF   │ │
                                    │ │        (LENGTH 120K, shrunk, D-10)   │ │
                                    │ ├──────────────────────────────────────┤ │
                                    │ │ CONFIG = Sector 15  0x0801E000..FFFF │ │
                                    │ │   slot A 0x0801E000  page 480        │ │
                                    │ │   slot B 0x0801E100  page 481        │ │
                                    │ │   (different page erase units, C-5)  │ │
                                    │ └──────────────────────────────────────┘ │
                                    └──────────────────────────────────────────┘
                                                         ▲
                                 payload-scoped DFU erase │ contract only (D-12)
                                 FLASH_BASE/SIZE unchanged │ Phase 127, parallel repo
```

### Component Responsibilities

| File | New / Changed / Deleted | Responsibility |
|------|------------------------|----------------|
| `include/rurp_config_storage.h` | **NEW** | Exactly two `extern "C"` bool declarations (D-06); included by exactly three TUs (D-09) |
| `src/rurp_config_utils.cpp` | **CHANGED** → policy-only | Keeps the global + all four public functions; loses `#include <EEPROM.h>` and `CONFIG_START` |
| `src/boards/rurp_config_storage_eeprom.cpp` | **NEW** (pure move) | `CONFIG_START 48`, `EEPROM.get`/`put`, returns `true` unconditionally |
| `platform/py32f071/src/config_storage_dualslot.cpp` (+ local header) | **NEW** | HAL-free dual-slot core over three injected primitives; CRC32; `StoredConfiguration` per D-17 |
| `platform/py32f071/src/config_storage_flash.cpp` | **NEW** | The three primitives via `HAL_FLASH_*`; 256 B aligned staging buffer; linker-symbol addresses |
| `platform/py32f071/src/config.cpp` | **DELETED** | CFG-07 — four drift points, see below |
| `platform/py32f071/linker/PY32F071xB_FLASH.ld` | **CHANGED** | `MEMORY` at `:3–7`; shrink `FLASH`, add `CONFIG`, add zero-length `BOOTLOADER`, `PROVIDE` three symbols |
| `platform/py32f071/CMakeLists.txt` | **CHANGED** | **Four** edits (C-3), not three, plus two new platform sources and one deletion |
| `platform/py32f071/CONFIG-STORAGE.md` | **NEW** | CFG-01 vendored design + CFG-02 `## Flash geometry`, landing **before** any `.ld` commit |
| `tests/test_*.py` (2–3 files) | **NEW** | CFG-04 regression + the six CFG-05 functions + the linker/flash-map gate (D-12b) |

### Recommended Project Structure

```
firestarter/
├── include/
│   └── rurp_config_storage.h           # NEW — the seam, 2 fns, extern "C"
├── src/
│   ├── rurp_config_utils.cpp           # policy only (was policy + EEPROM)
│   └── boards/
│       └── rurp_config_storage_eeprom.cpp   # NEW — pure move, PY32_EXCLUDED
├── platform/py32f071/
│   ├── CONFIG-STORAGE.md               # NEW — CFG-01 vendored + CFG-02 geometry
│   ├── linker/PY32F071xB_FLASH.ld      # CHANGED — after the CFG-02 commit
│   ├── CMakeLists.txt                  # CHANGED — 4 edits (C-3)
│   └── src/
│       ├── config.cpp                  # DELETED (CFG-07)
│       ├── config_storage_dualslot.cpp # NEW — HAL-free core (tested by host)
│       └── config_storage_flash.cpp    # NEW — HAL primitives only
└── tests/
    ├── test_config_storage_eeprom_regression.py  # CFG-04
    ├── test_config_storage_dualslot.py           # CFG-05 — six named fns
    └── test_py32_flash_map.py                    # D-12(b) linker gate
```

### Pattern 1: The two-function byte-blob seam (CFG-03, D-06)

**What:** Policy above, bytes below. The backend knows nothing about versions, defaults or
validation; the policy knows nothing about EEPROM addresses or flash pages.
**When to use:** Exactly here — it is CFG-03 verbatim.

```cpp
// include/rurp_config_storage.h  — NEW. Note the extern "C" wrapper (C-11).
#ifndef __RURP_CONFIG_STORAGE_H__
#define __RURP_CONFIG_STORAGE_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

/* Load `len` bytes of previously-saved configuration into `blob`.
 * Returns false when no valid record exists (py32: both slots blank or both
 * CRC-invalid -- D-15 deliberately does not distinguish them). AVR returns
 * true unconditionally: EEPROM always yields bytes, valid or not, which is
 * byte-identical to the pre-refactor behaviour CFG-04 pins. */
bool rurp_config_storage_load(void* blob, size_t len);

/* Persist `len` bytes. Returns false if the bytes did not reach storage. */
bool rurp_config_storage_save(const void* blob, size_t len);

#ifdef __cplusplus
}
#endif
#endif
```

The policy layer keeps its shape, so `rurp_validate_config`'s write-back at the current `:38` still
fires identically on both platforms (D-14):

```cpp
// src/rurp_config_utils.cpp — policy only. No <EEPROM.h>, no CONFIG_START.
void rurp_load_config() {
    rurp_configuration_t* config = rurp_get_config();
    (void)rurp_config_storage_load(config, sizeof(*config)); // bool ignored: validate decides
    rurp_validate_config(config);                            // unchanged -> writes back defaults
}

void rurp_save_config(rurp_configuration_t* config) {
    (void)rurp_config_storage_save(config, sizeof(*config));
}
```

### Pattern 2: Dual-slot with injected primitives (CFG-05, D-02)

**What:** The algorithm is compiled twice — once against the HAL, once against a RAM fake — from one
source file. **When to use:** whenever "the tested code must be the shipped code" and the real
dependency cannot be linked in the test venue.

```cpp
// platform/py32f071/src/config_storage_dualslot.h  (local header, ARM-only by placement)
// Three primitives. Deliberately NOT a HAL type in sight.
typedef struct {
    // Read `len` bytes from slot `slot` (0 = A, 1 = B) into `dst`.
    bool (*read)(void* ctx, uint8_t slot, void* dst, size_t len);
    // Erase the whole 256-byte page backing slot `slot`.
    bool (*erase_page)(void* ctx, uint8_t slot);
    // Program the whole 256-byte page backing slot `slot` from 64 words.
    // C-2: this is the ONLY program granularity the part offers.
    bool (*program_page)(void* ctx, uint8_t slot, const uint32_t words[64]);
    void* ctx;
} rurp_flash_primitives_t;
```

Save, with D-16's property preserved and its wording corrected per C-2:

```
save(record):
  active   = the slot that load() selected (or none)
  inactive = the other slot
  record.sequence = (active ? active.sequence + 1 : 1)      # D-17, no wraparound branch
  record.crc32    = crc32_reflected(record, offsetof(crc32))

  erase_page(inactive)                 # C-8: HAL is only safe on a blank page
  page[64] = 0xFF-filled               # C-2: 256B staging buffer, 4-byte aligned
  memcpy(page, &record, sizeof(record))
  program_page(inactive, page)         # <-- completion of THIS call is the commit

  # The active slot was never touched. An abort anywhere above leaves it
  # loadable; an aborted program_page leaves `inactive` CRC-invalid, so
  # load() rejects it and returns the previous record. This is exactly
  # blob 4b1a441's "a failed or interrupted write must leave the previous
  # record usable" -- reached without a trailing-word commit, which this
  # part cannot express (RM V0.2 §4.2.3.2).
```

Load:

```
load(blob, len):
  best = none
  for slot in (A, B):
      read(slot, &rec, sizeof(rec))
      if rec.magic != CONFIG_MAGIC:                  continue   # never written, or garbage
      if rec.length  > len:                          continue   # C-6 + SECURITY: bound BEFORE use
      if rec.crc32 != crc32_reflected(&rec, offsetof(crc32)): continue
      if best == none or rec.sequence > best.sequence: best = rec
  if best == none: return false                                 # D-15: blank == both-corrupt
  memcpy(blob, &best.configuration, min(best.length, len))
  return true
```

### Pattern 3: Prove the move before making it (CFG-04, D-04)

**What:** Write the regression test against the **pre-refactor** file, prove it green, record the
blob SHA; split in a later commit; prove the SHA **re-hashes identical** and the test is **still
green**. **Why:** a test written after the refactor can only prove the new code is self-consistent —
it never observed the behaviour it claims to match.

```bash
# Commit N   — test only, against the untouched policy+EEPROM file
git hash-object tests/test_config_storage_eeprom_regression.py   # RECORD this
python3 -m pytest tests/test_config_storage_eeprom_regression.py -v   # must be green

# Commit N+k — the split lands

# Proof (primary): the recorded SHA re-hashes identical
test "$(git hash-object tests/test_config_storage_eeprom_regression.py)" = "<RECORDED>"   # exit code
python3 -m pytest tests/test_config_storage_eeprom_regression.py -v   # still green
# Corroboration ONLY (124-VERIFICATION.md: this shape has passed vacuously here):
git diff --stat -- tests/test_config_storage_eeprom_regression.py
```

### Anti-Patterns to Avoid

- **`#ifdef __AVR__` inside `src/rurp_config_utils.cpp`** — explicitly rejected by D-08. Makes
  "per-platform backend" true only because the file says so, and leaves py32 sharing a TU with
  `EEPROM.h`.
- **Raw `FLASH->CR` register sequences** — C-4. Skips the §4.2.3.6 timing registers; fails only on
  silicon nobody can debug.
- **Passing `&record` to `HAL_FLASH_Program`** — C-2. Programs 220 bytes of adjacent RAM into flash.
- **Programming a slot without erasing it first** — C-8. The HAL omits the RM's read-out step, so it
  is only correct on a blank page.
- **`magic` = `0xFFFFFFFF` or `0x00000000`** — erased NOR flash reads `0xFF`, so `0xFFFFFFFF` would
  make a blank slot look valid and collapse D-15's blank test into a CRC accident. Pick a fixed
  non-degenerate 32-bit constant and record it.
- **Hardcoding a record size or field offset in any test** — C-6. Three compilers, three answers.
- **Adding a `tests/`-visible dependency on `.pio/libdeps/`** — C-12. Passes warm, fails clean.
- **A rollover branch for `sequence`** — Discretion: it can never execute and can never be tested
  (the Phase 124 D-01 rule).
- **Distinguishing blank from corrupt in a return value** — D-15/D-06. No consumer exists; it needs
  the declined status enum plus a `messages.toml` codegen round-trip.
- **Proving "untouched" with a path-scoped `git diff`** — the documented vacuous shape (Phase 125
  C-15, `124-VERIFICATION.md`). Blob SHAs, or `git status --porcelain` scoped by repo name.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PY32 flash unlock / erase / program | A `FLASH->KEYR`/`CR` register driver | `HAL_FLASH_Unlock` / `HAL_FLASH_Erase` / `HAL_FLASH_Program` / `HAL_FLASH_Lock` | The HAL entry points carry `__HAL_FLASH_TIMMING_SEQUENCE_CONFIG()` (9 timing registers, indexed by HSI frequency off a factory table). RM §4.2.3.6: without them the operation *"will fail"*. Invisible from the call site (C-4) |
| Page/sector geometry constants | Guessed or reverse-derived numbers | `FLASH_PAGE_SIZE` / `FLASH_SECTOR_SIZE` from `py32f071xB.h`, cross-cited to RM Table 4-1 | Two wrong answers are in easy reach — the 128 B/4 KiB PY32F030 figures, and the SDK's own stale header comment (C-1). This is what CFG-02 exists to prevent |
| Non-overlap of app `.text` and config | A comment, or a convention, or `-D` addresses from CMake | A second `MEMORY` region + `PROVIDE` symbols in the `.ld` (D-11) | The linker enforces it structurally; the first violation of a convention is a corrupted config at runtime on silicon nobody can debug |
| Whole-page staging | Writing the record struct directly | An explicit `uint32_t page[64]` | The HAL reads 64 words regardless of your object's size (C-2) |
| A fake EEPROM for the host test | Depending on `.pio/libdeps/…/EEPROM.h` | A hand-written shim beside the test | The libdeps path is a gitignored build artifact — a fail-open dependency (C-12) |
| A CRC32 | Adapting `rurp_serial_utils.cpp:378` | A fresh bitwise reflected CRC-32 in the HAL-free core | That accessor is **CRC8**-CCITT and `PROGMEM`/AVR-shaped. Wrong algorithm and wrong platform |
| Confidence that the CRC is right | Asserting the module against itself | The KAT `CRC32("123456789") == 0xCBF43926` (D-05) | An implementation asserted against itself proves nothing (the HOST-06 discipline) |
| AVR size judgement | Eyeballing build output | `scripts/check_size_baseline.py` (armed, strict equality) | Already built; this phase reads figures, it does not build a comparator |

**Key insight:** every hand-rolled option in this domain fails in a venue this project cannot
observe. There is no PY32F071 PCB, `arm-none-eabi-gcc` is not installed, and there is no ARM
bus-trace oracle. A custom flash driver, a guessed page size, or an address-overlap convention would
all compile, review cleanly, and be wrong with nothing able to notice. Delegating to the pinned HAL
and to the linker converts *unobservable runtime correctness* into *observable build-time
correctness* — which is the only kind this milestone can actually verify.

---

## Runtime State Inventory

This phase changes where configuration is *persisted*, so the rename/refactor discipline applies.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| **Stored data** | **AVR EEPROM offset 48**, holding a live `rurp_configuration_t` (`"VER06"`, R1=270000, R2=44000, `hardware_revision`) on the operator's three physical boards. CFG-04 makes the move byte-identical and CFG-07 forbids a schema change, so existing boards keep working with **no migration**. **py32 flash: nothing exists** — no PCB, no device has ever stored a record; the first record will be written by `rurp_validate_config`'s write-back on first boot (D-14) | **None — verified by** CFG-04's offset/size assertion + CFG-07's unchanged schema. Code edit only, no data migration |
| **Live service config** | **None.** Nothing in this phase is registered with n8n, Datadog, Tailscale, Cloudflare or any external service. The config lives only in on-device EEPROM/flash | None — verified by grep: the only persistence call sites are the seven in C-14, all in firmware |
| **OS-registered state** | **None.** No Task Scheduler entry, pm2 process, launchd plist or systemd unit references config storage. CI is `py32f071.yml` (ARM build) which registers nothing | None — verified: no scheduled task or service touches these files |
| **Secrets / env vars** | `FIRESTARTER_SIZE_BASELINE` — the env seam by which `check_size_baseline.py` and `check_build_warnings.py` locate the baseline JSON. **Name unchanged**; only the JSON's *contents* may change, and only via a re-baseline in its own justified commit. `FIRESTARTER_CONFIG_DIR` (host-side) is untouched. No secret is involved | None for the seam name. **If the AVR delta fires:** re-baseline `size_baseline.json` in its own commit whose message states why the bytes are legitimate. `size_baseline_base01.json` is Phase 124's frozen MERGE-05 reference and **must not be touched** |
| **Build artifacts** | `.pio/build/{uno,uno328pb,leonardo,native,native_nodevtools,native_pinmap_provisional}/` contain objects for the pre-split `rurp_config_utils.o`. Splitting one TU into two leaves a **stale `.o` for a file that still exists**, so PIO's dependency scan handles it — but the size measurement will not be trustworthy from a warm tree. `.pio/libdeps/*/ArduinoFake/` is a gitignored artifact the tests must not depend on (C-12) | **Measure cold**: `pio run -t clean -e <env>` then `pio run -e <env>`, one uninterrupted invocation per env — the exact procedure `size_baseline.json`'s `meta.note` records, including its documented trap that a default 2-minute Bash timeout truncates the build and silently contaminates the figure. Use an extended timeout |

**The canonical question — after every file in the repo is updated, what runtime systems still have
the old arrangement cached, stored or registered?** Answer: only the operator's three AVR boards,
whose EEPROM content at offset 48 is *deliberately* preserved bit-for-bit (that is what CFG-04
means). Nothing else. There is no py32 device in existence to hold stale state.

---

## Common Pitfalls

### Pitfall 1: Reserving 128 bytes because the SDK header said so

**What goes wrong:** The config region is half the page size; slot B overlaps slot A, or the page
program runs off the end of the reservation into `.text`.
**Why it happens:** `py32f071_hal_flash.h:268` literally says *"Program 128bytes at a specified
address"* — inside the pinned SDK, above code that writes 256 (C-1).
**How to avoid:** Cite RM V0.2 §4.1/§4.2.1/Table 4-1 **and** `py32f071xB.h:578,580`. Make
`__config_page_size` a linker symbol and assert it equals 256 in the D-12(b) gate.
**Warning signs:** any 128, 0x80, 2048 or 4096 appearing near a config address.

### Pitfall 2: Writing D-16 literally and discovering the primitive does not exist

**What goes wrong:** The plan contains a task like "program the CRC word last", which has no
implementation, and the executor invents one — most likely a raw register write (which then also
trips C-4).
**Why it happens:** D-16 is locked and reads as an implementation instruction; the constraint that
invalidates it is three levels down in a vendor HAL.
**How to avoid:** Amend D-16 in the plan **explicitly**, citing RM §4.2.3.2 and
`IS_FLASH_TYPEPROGRAM`, and state that the property is preserved by "active slot untouched + CRC
rejects a torn page". Never silently reinterpret a locked decision.
**Warning signs:** a task naming a "commit word", "header write" or "final word" as a separate step.

### Pitfall 3: The ARM link fails on a gated push, hours after the code was written

**What goes wrong:** `undefined reference to HAL_FLASH_Unlock` — because `py32f071_hal_flash.c` was
never added to `PY32_SDK_SOURCES` (C-3).
**Why it happens:** `py32f071_hal_conf.h` already enables the module and includes the header, so
everything **compiles**; and `check_cmake_manifest.py` is structurally exempt from checking
`PY32_SDK_SOURCES`. `cmake`/`ninja`/`arm-none-eabi-gcc` are absent locally, so nothing here can
fail.
**How to avoid:** Make edit 4 a named line item with its own verification (`grep -c hal_flash
platform/py32f071/CMakeLists.txt` must be ≥ 1), and a `tests/` assertion that the manifest names the
flash driver whenever the tree contains a `HAL_FLASH_` call. That converts a CI-only failure into a
local one.
**Warning signs:** a plan that quotes D-08's "three edits" without amending it.

### Pitfall 4: A test asserts `sizeof(...) == 15` (or 20, or 32) and is wrong on two of three compilers

**What goes wrong:** Green locally, red under `avr-g++`, or a false pass that hides a real layout
change.
**Why it happens:** host `long` is 8 bytes, AVR/ARM `long` is 4, and `g++ -m32` is unavailable here
(C-6).
**How to avoid:** Assert `sizeof(rurp_configuration_t)` and `offsetof()` **symbolically**; add the
one absolute assertion that is true everywhere — `sizeof(StoredConfiguration) <= 256`.
**Warning signs:** any integer literal in a size or offset assertion.

### Pitfall 5: The AVR flash delta fires and gets absorbed instead of recorded

**What goes wrong:** A tolerance is widened, or `size_baseline.json` is re-baselined in a commit that
also contains code.
**Why it happens:** Splitting one TU into two and adding a `bool` return can move bytes even under
`-flto` + `--gc-sections`; `compare_avr()` is strict equality and armed. Live headroom: **leonardo
26016/28672 = 2656 B**, uno 23954/32256 = 8302 B, uno328pb 24004/32384 = 8380 B. The rule is
*Leonardo must not grow; Uno-class ≤ 64 B, recorded.*
**How to avoid:** Measure **immediately after the AVR move, before any ARM work**, cold, one env per
uninterrupted invocation with an extended timeout. If it fires: record the delta and its cause, then
re-baseline in **its own commit whose message states why the bytes are legitimate** (Plan 124-10's
shape). Record **RAM alongside flash** for all three targets (R-12). Never touch
`size_baseline_base01.json`.
**Warning signs:** a plan that measures AVR size after the ARM backend lands — the delta is then
unattributable, which is the exact reason the ROADMAP made the internal ordering load-bearing.

### Pitfall 6: A cross-repo gate silently SKIPs because a firmware file moved

**What goes wrong:** Host gates report exit 0 with the reason *"firestarter firmware checkout
absent"* when in fact the repo is present and a scanned file simply moved. A-7 measured **5 gate legs
flipping PASS→SKIP** from a single firmware rename.
**Why it happens:** Six host modules key "repo absent" on a single file's existence. **This phase
moves firmware files** — precisely the condition the fail-open proxy was blind to.
**How to avoid:** Run the nine-row cross-repo sweep and show each gate **RAN**, not skipped; assert
the skip census (fail if any skip reason mentions firmware absence while `../firestarter/.git`
exists). Re-run at **every wave** (the Phase-118 discipline).
**Warning signs:** a green host suite with a skip count above 3 in the sibling layout.

### Pitfall 7: `gsd-tools query commit` moves HEAD to another branch

**What goes wrong:** Firmware commits land on the wrong branch; gitlinks revert.
**Why it happens:** An unanchored `##…vX.Y` regex scrapes ROADMAP prose; observed live on
2026-07-30.
**How to avoid:** `git rev-parse --abbrev-ref HEAD` in **both** repos after every `gsd-tools query
commit`. Expect `v1.23-py32f071-integration` (firmware) and `gsd/v1.23-py32f071-integration` (meta).
**Warning signs:** a gitlink change appearing in an unrelated diff.

### Pitfall 8: Treating the two gitignored py32 worktrees as writable

**What goes wrong:** Edits land in `firestarter_py32_ci/` or `firestarter_app_py32/`, which are never
gitlinked, and are silently lost.
**How to avoid:** Read from them; write only to `/workspaces/firestarter`. `py32_dfu.py` lives on the
unmerged `feature/py32f071-fw-install` @ `4ee64a1` and belongs to Phase 127 (D-12).

---

## Code Examples

### The vendored in-scope design (CFG-01) — blob `4b1a441` §"Configuration storage", verbatim

Re-read this session with `git cat-file -p 4b1a441` from `/workspaces/firestarter` (195 lines,
readable, confirmed):

> ### Configuration storage
>
> AVR continues to use EEPROM. PY32F071 uses internal flash with two independently validated records:
>
> ```cpp
> struct StoredConfiguration {
>     uint32_t magic;
>     uint16_t version;
>     uint16_t length;
>     rurp_configuration_t configuration;
>     uint32_t sequence;
>     uint32_t crc32;
> };
> ```
>
> The newest valid sequence is loaded. A failed or interrupted write must leave the previous record
> usable.

That is the entire in-scope subset — three sentences and a struct. Also in scope from the acceptance
checklist: *"[ ] Flash-backed configuration survives interrupted writes."*

**SUPERSEDED by PR #48's actual layout** (mark, do not follow): the whole §"PY32F071 backend modules"
tree — `py32f071_board.h`, `py32f071_pins.h`, `board.cpp`, `gpio.cpp`, `usb.cpp`, `adc.cpp`,
`dac.cpp`, `storage.cpp` → actually built as `py32f071_rurp_shield.cpp`, `timing.cpp`, `usb_cdc.c`,
`config.cpp`, `platform_compat.cpp`, `main.cpp`. **OUT OF SCOPE:** §"ADC measurement" steps 5–6,
§"DAC VPP control" in full, and the acceptance items for calibration, closed-loop DAC and real
hardware (FUT-VPP / FUT-CAL).

### The CFG-02 geometry record

```markdown
## Flash geometry

Source of record: **Puya, *PY32F07X Series Reference Manual*, V0.2** —
§4.1 "Key features" (p.34), §4.2.1 "Flash structure" (p.34),
**Table 4-1 "Flash structure and boundary addresses"** (p.34).

| Property | Value | Citation |
|---|---|---|
| Page size (smallest erase + program unit) | **256 bytes** | RM V0.2 §4.1, §4.2.1 |
| Sector size | **8192 bytes (8 KBytes)** | RM V0.2 §4.1, §4.2.1; §4.2.3.5 |
| Main flash | 128 KBytes, 0x08000000–0x0801FFFF = 16 sectors / 512 pages | RM V0.2 Table 4-1 |
| Sector 15 | pages 480–511, 0x0801E000–0x0801FFFF | RM V0.2 Table 4-1 |
| Program granularity | one full page, as 64 × 32-bit words; non-32-bit writes hard-fault | RM V0.2 §4.2.3.2 |
| Erase granularities | page (PER, 256 B), sector (SER, 8 KB), mass (MER) | RM V0.2 §4.2.3.3/.4/.5 |

Corroborated byte-for-byte by the pinned SDK
(`OpenPuya/PY32F071_Firmware` @ `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`,
`Drivers/CMSIS/Device/PY32F071/Include/py32f071xB.h:575–581`):
`FLASH_PAGE_SIZE 0x00000100U` · `FLASH_SECTOR_SIZE 0x00002000U` ·
`FLASH_BASE 0x08000000UL` · `FLASH_END 0x0801FFFFUL`.

**Do NOT use** `py32f071_hal_flash.h:268`, whose comment reads
"Program 128bytes at a specified address" — a stale carry-over from the smaller
PY32F030 part, contradicted by `FLASH_Program_Page`'s own `while(index<64U)`
loop immediately beneath it and by RM §4.2.3.2. The commonly cited
"128-byte page / 4 KiB sector" PY32 figures are PY32F030/F003 values.
```

Prove the ordering as an exit code (Discretion):

```bash
CFG=$(git log -1 --format=%H -- platform/py32f071/CONFIG-STORAGE.md)
LD=$(git log -1  --format=%H -- platform/py32f071/linker/PY32F071xB_FLASH.ld)
git rev-list --is-ancestor "$CFG" "$LD"   # exit 0 == the geometry was recorded first
```

### The linker script `MEMORY` block (CFG-06, D-10/D-11/D-13, refined by C-5)

```ld
/* Flash map. Geometry is NOT guessed here -- see platform/py32f071/CONFIG-STORAGE.md
 * §"Flash geometry": Puya PY32F07X Reference Manual V0.2 §4.1/§4.2.1/Table 4-1,
 * page = 256 B, sector = 8192 B, main flash 0x08000000..0x0801FFFF (128 KiB).
 * That record landed in a commit PRECEDING this file's first edit (CFG-02).
 */
MEMORY
{
    /* D-13 -- NAMED SEAM ONLY, ZERO LENGTH, for Phase 129 (PCB-03/FUT-N05) to cite.
     *
     * READ THIS BEFORE GIVING IT A SIZE. Unlike the CONFIG region below -- which
     * sits at the TOP of flash and can grow downward without moving anything --
     * giving BOOTLOADER a non-zero length MOVES the application's ORIGIN. That is
     * a flash-map MIGRATION, not a resize: every previously flashed unit's vector
     * table address changes. Phase 129 must record the bootloader budget as an
     * INTENT WITH THAT COST ATTACHED, never as a number that looks already paid for.
     */
    BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0

    /* Shrunk from 128K so .text/.rodata physically CANNOT reach CONFIG (D-10).
     * 0x1E000 = 120K -> app occupies 0x08000000..0x0801DFFF (sectors 0..14). */
    FLASH  (rx)  : ORIGIN = 0x08000000, LENGTH = 120K

    /* Sector 15 (RM Table 4-1: pages 480-511). Sector-ALIGNED on purpose:
     * the two slots below are different PAGE erase units, which is what CFG-06
     * requires, and aligning the region to a whole sector additionally means no
     * sector-granular erase of the app region can ever clip it. 7680 B of this
     * reservation is deliberate slack. */
    CONFIG (r)   : ORIGIN = 0x0801E000, LENGTH = 8K

    RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 16K
}

/* Consumed by platform/py32f071/src/config_storage_flash.cpp. Two slots, one page
 * each, in DIFFERENT page erase units (CFG-06) -- so erasing one cannot disturb
 * the other, which is the whole atomicity property. */
PROVIDE(__config_page_size    = 256);
PROVIDE(__config_slot_a_start = ORIGIN(CONFIG));                          /* 0x0801E000, page 480 */
PROVIDE(__config_slot_b_start = ORIGIN(CONFIG) + 256);                    /* 0x0801E100, page 481 */
PROVIDE(__config_region_end   = ORIGIN(CONFIG) + LENGTH(CONFIG));        /* 0x08020000 */

/* Structural guards -- a violation is a LINK failure, not a runtime surprise. */
ASSERT(ORIGIN(FLASH) + LENGTH(FLASH) <= ORIGIN(CONFIG),
       "app region overlaps the reserved config region")
ASSERT(__config_slot_b_start - __config_slot_a_start == __config_page_size,
       "config slots must be exactly one page apart (different erase units)")
ASSERT(ORIGIN(CONFIG) % 8192 == 0, "CONFIG must start on an 8 KiB sector boundary")
```

### The HAL primitive layer (C-2, C-4, C-8)

```cpp
// platform/py32f071/src/config_storage_flash.cpp -- the ONLY file that knows the HAL exists.
#include "py32f071_hal.h"
#include "config_storage_dualslot.h"

extern "C" { extern uint32_t __config_slot_a_start, __config_slot_b_start, __config_page_size; }

static uint32_t slot_addr(uint8_t slot) {
    return slot == 0 ? (uint32_t)&__config_slot_a_start : (uint32_t)&__config_slot_b_start;
}

static bool hal_erase_page(void*, uint8_t slot) {
    FLASH_EraseInitTypeDef e = {};
    e.TypeErase   = FLASH_TYPEERASE_PAGEERASE;   // 256 B unit -- RM V0.2 §4.2.3.3
    e.PageAddress = slot_addr(slot);
    e.NbPages     = 1;
    uint32_t err = 0;
    if (HAL_FLASH_Unlock() != HAL_OK) return false;
    // HAL_FLASH_Erase internally runs __HAL_FLASH_TIMMING_SEQUENCE_CONFIG()
    // (py32f071_hal_flash.c:416). RM V0.2 §4.2.3.6: without those timing
    // registers the operation FAILS. This is exactly why we do not poke
    // FLASH->CR directly.
    const bool ok = (HAL_FLASH_Erase(&e, &err) == HAL_OK);
    HAL_FLASH_Lock();
    return ok;
}

static bool hal_program_page(void*, uint8_t slot, const uint32_t words[64]) {
    // C-2: FLASH_Program_Page writes 64 words UNCONDITIONALLY from this pointer.
    // The caller MUST hand over a full 64-word buffer or the HAL reads past it.
    // C-8: the page must already be erased -- RM §4.2.3.2 requires reading out
    // the 64 words of a non-blank page first, which this HAL does not do.
    if (HAL_FLASH_Unlock() != HAL_OK) return false;
    const bool ok = (HAL_FLASH_Program(FLASH_TYPEPROGRAM_PAGE, slot_addr(slot),
                                       (uint32_t*)words) == HAL_OK);
    HAL_FLASH_Lock();
    return ok;
}

static bool hal_read(void*, uint8_t slot, void* dst, size_t len) {
    memcpy(dst, (const void*)slot_addr(slot), len);   // flash is memory-mapped for reads
    return true;
}
```

### The CRC32 known-answer anchor (D-05)

```python
# In tests/test_config_storage_dualslot.py -- an INDEPENDENT vector, written here,
# never derived from the module under test (the HOST-06 discipline).
CRC32_KAT_INPUT    = b"123456789"
CRC32_KAT_EXPECTED = 0xCBF43926   # standard reflected CRC-32, poly 0xEDB88320
```

### The AVR backend (CFG-04, pure move)

```cpp
// src/boards/rurp_config_storage_eeprom.cpp -- NEW. A MOVE, not a rewrite.
#include "rurp_config_storage.h"
#include "rurp_shield.h"
#include <EEPROM.h>

// Moved verbatim from src/rurp_config_utils.cpp:11. This is an EEPROM ADDRESS and
// is meaningless on py32, which is precisely why it belongs below the seam (D-07).
#define CONFIG_START 48

bool rurp_config_storage_load(void* blob, size_t len) {
    (void)len;   // EEPROM.get is a template over sizeof(T); see the note below
    EEPROM.get(CONFIG_START, *(rurp_configuration_t*)blob);
    return true; // byte-identical to pre-refactor: EEPROM always yields bytes,
                 // and rurp_validate_config decides whether they are usable
}

bool rurp_config_storage_save(const void* blob, size_t len) {
    (void)len;
    EEPROM.put(CONFIG_START, *(const rurp_configuration_t*)blob);
    return true;
}
```

> **Note for the planner.** `EEPROM.get/put` are templates whose length comes from `sizeof(T)`, so the
> cast above is what makes the moved code emit the *identical* `(48, sizeof(rurp_configuration_t))`
> access the pre-refactor code emitted — which is exactly what CFG-04's test asserts. If the executor
> instead reaches for a byte-loop over `len`, the behaviour is arguably equivalent but the emitted
> code is not a *move*, and `put`'s per-byte `update()` semantics (C-12) would have to be reproduced
> by hand. Keep the typed call.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Config spec cited as `platform/py32f071/PORTING.md` by PROJECT.md and STATE.md | The file **does not exist on any live branch**; it survives only as blob `4b1a441` on closed PRs #46/#47, and is partly superseded | Discovered by research A-6/R-8 (2026-07-30) | CFG-01 makes this phase *design* work: vendor the in-scope subset, mark the superseded parts |
| "PY32 flash: 128 B page, 4 KiB sector" | **PY32F071: 256 B page, 8 KiB sector** | Established this session from RM V0.2 + the pinned part header | The 128/4K figures are PY32F030/F003 values. The SDK's own HAL header comment still says 128 (C-1) |
| D-16: "program the header/CRC word LAST" | Commit = completion of the single 256-byte page program; CRC rejects a torn page | Established this session (C-2) | No word-level program primitive exists on this part; the guarantee is preserved by a different mechanism |
| `src/rurp_config_utils.cpp` excluded from the ARM build | Compiled by ARM as the common policy layer; a new EEPROM backend takes the exclusion | This phase (D-08) | The exclusion comment already says *"WILL NEED REVISITING in Phase 126, it is not a permanent exclusion"* |
| PR #48's `platform/py32f071/src/config.cpp` | **Deleted** (CFG-07) | This phase | It is a second, drifted copy of the policy whose `rurp_save_config()` persists nothing |
| `PY32F071xB_FLASH.ld` claims the entire 128 K with no reservation | `FLASH` 120K + `CONFIG` (Sector 15) + zero-length `BOOTLOADER` seam | This phase (CFG-06, D-10/D-11/D-13) | Changing an address after Phase 129 cites it is a flash-map **migration** — which is why the reservation lands here |

**Deprecated / outdated:**

- **`platform/py32f071/PORTING.md` as a citation.** Never cite it as a live path again. Cite blob
  `4b1a441` by SHA, name its closed-PR home, and point at the vendored `CONFIG-STORAGE.md`.
- **`py32f071_hal_flash.h:268`'s "128bytes" comment.** Stale. Contradicted by the code beneath it.
- **The whole-file blob-SHA shorthand for golden traces.** Retired in Phase 119 — golden register
  traces are compared **per-array** for `_shared/sdp_expected.h`.
- **`_EEPROM_28C_CPP.exists()`-style single-file repo-presence proxies.** Fail-open (A-7). Key repo
  presence on `../firestarter/.git` via `tests/fw_presence.py`.

---

## Validation Architecture

`workflow.nyquist_validation` is **absent** from `.planning/config.json` → treated as **enabled**.

### Test Framework

| Property | Value |
|----------|-------|
| Framework (new tests) | `pytest` **9.1.1**, driving host `g++` **14.2.0** by subprocess |
| Framework (existing native) | PlatformIO + Unity — **pinned at 141 cases / 17 suites, not moved** (C-13) |
| Config file | **none** — `firestarter/tests/` has no `conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg` or `tox.ini`. Self-contained path resolution per file is the recorded house pattern (Phase 125), not an omission |
| Quick run command | `cd /workspaces/firestarter && python3 -m pytest tests/ -q` |
| Full suite command | `python3 -m pytest tests/ -v` **+** `pio test -e native` **+** `pio test -e native_nodevtools` **+** `pio run -e uno` / `-e uno328pb` / `-e leonardo` **+** `python3 scripts/check_size_baseline.py` **+** `python3 scripts/check_cmake_manifest.py` **+** `python3 scripts/check_build_warnings.py` |
| CI coverage of the new tests | **ZERO legs on this branch.** `pytest tests/` appears only in `build.yml` (push/PR to `main`) and `beta-build.yml` (push to `beta`); `py32f071.yml` has no pytest step. Discharged by an in-phase **local** run whose verbatim output lands in `126-NONREGRESSION.md`. **Do not claim CI coverage this branch lacks** (D-01) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CFG-01 | The vendored doc exists, cites blob `4b1a441` by SHA, names PRs #46/#47, and carries a SUPERSEDED block naming all seven superseded modules | unit (text) | `pytest tests/test_config_storage_design_vendored.py -x` | ❌ Wave 0 |
| CFG-02 | The geometry doc records 256 B / 8192 B with the RM citation, **and** its commit precedes the first `.ld` commit | unit + git | `pytest tests/test_flash_geometry_recorded_before_linker.py -x` (wraps `git rev-list --is-ancestor`) | ❌ Wave 0 |
| CFG-03 | The seam header declares exactly two functions; it is included by exactly three TUs; `rurp_shield.h` is unchanged | unit (source scan) | `pytest tests/test_config_storage_seam_shape.py -x` | ❌ Wave 0 |
| CFG-04 | `EEPROM.get`/`put` at offset **48** with `sizeof(rurp_configuration_t)`, byte-identical pre/post refactor; fake recorded ≥1 call | integration (g++ compile+run) | `pytest tests/test_config_storage_eeprom_regression.py -v` | ❌ Wave 0 |
| CFG-04 | AVR flash/RAM delta inside the A-5 band on all three targets | integration (build) | `pio run -t clean -e leonardo && pio run -e leonardo` (×3 envs, cold, extended timeout) then `python3 scripts/check_size_baseline.py` | ✅ exists (armed) |
| CFG-05 | `test_blank_slots_report_no_valid_record` | integration (g++) | `pytest tests/test_config_storage_dualslot.py::test_blank_slots_report_no_valid_record -x` | ❌ Wave 0 |
| CFG-05 | `test_newest_sequence_wins_when_both_slots_valid` | integration (g++) | `…::test_newest_sequence_wins_when_both_slots_valid -x` | ❌ Wave 0 |
| CFG-05 | `test_slot_with_bad_crc_is_rejected_in_favour_of_the_other` | integration (g++) | `…::test_slot_with_bad_crc_is_rejected_in_favour_of_the_other -x` | ❌ Wave 0 |
| CFG-05 | `test_both_slots_corrupt_reports_no_valid_record` (D-15: same outcome as blank, different input) | integration (g++) | `…::test_both_slots_corrupt_reports_no_valid_record -x` | ❌ Wave 0 |
| CFG-05 | `test_interrupted_write_leaves_the_previous_record_loadable` (abort after N ∈ {0,1,32,63,64} words, C-2) | integration (g++) | `…::test_interrupted_write_leaves_the_previous_record_loadable -x` | ❌ Wave 0 |
| CFG-05 | `test_successive_saves_alternate_slots` | integration (g++) | `…::test_successive_saves_alternate_slots -x` | ❌ Wave 0 |
| CFG-05 | CRC32 known-answer anchor `CRC32("123456789") == 0xCBF43926` (D-05) — a **seventh** function, non-vacuity for the six | integration (g++) | `…::test_crc32_matches_the_independent_known_answer_vector -x` | ❌ Wave 0 |
| CFG-06 | The `.ld` reserves two pages in different erase units, page size == 256, region inside `0x08000000 + 128 KiB`, sector-aligned, symbols `PROVIDE`d | unit (parse) | `pytest tests/test_py32_flash_map.py -x` | ❌ Wave 0 |
| CFG-06 | `CMakeLists.txt` names `py32f071_hal_flash.c` whenever any TU calls `HAL_FLASH_` (C-3, turns a CI-only link failure into a local one) | unit (source scan) | `pytest tests/test_py32_flash_map.py::test_manifest_names_the_flash_driver -x` | ❌ Wave 0 |
| CFG-07 | `rurp_configuration_t` and `CONFIG_VERSION "VER06"` unchanged (blob SHA / literal), and `platform/py32f071/src/config.cpp` **absent from the tree** | unit | `pytest tests/test_config_schema_pinned.py -x` | ❌ Wave 0 |
| all | Native counts unmoved: **141 cases / 17 suites** on both pinned envs | integration | `pio test -e native` ; `pio test -e native_nodevtools` (assert the two counts, never "tests pass") | ✅ exists |
| all | Golden register traces byte-identical, **per-array** for `_shared/sdp_expected.h` | integration | via `pio test -e native` | ✅ exists |
| all | The nine cross-repo gates **RAN**, not skipped (A-7) | integration | host-suite sweep in the sibling layout, re-run **every wave** | ✅ exists |

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/ -q` (seconds; the new tests are compile-and-run)
- **Per wave merge:** full `pytest tests/ -v` + both pinned `pio test` envs with counts asserted +
  the nine-row cross-repo sweep (A-7 discipline) + `check_cmake_manifest.py`
- **After the AVR move specifically, before any ARM work:** the three cold AVR builds +
  `check_size_baseline.py` — this is the *only* point at which a flash delta is attributable
- **Phase gate:** full suite green, all counts asserted, `126-NONREGRESSION.md` re-executed in the
  closing plan, before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_config_storage_eeprom_regression.py` — covers CFG-04; **must be authored against
      the pre-refactor file and its blob SHA recorded** (D-04). Needs a hand-written fake `EEPROM.h`
      (C-12), not `.pio/libdeps`
- [ ] `tests/test_config_storage_dualslot.py` — covers CFG-05; six named functions + the CRC KAT;
      needs the RAM fake with an abort-after-N-words hook (C-2) and a "program on a non-erased page
      is a test failure" assertion (C-8)
- [ ] `tests/test_py32_flash_map.py` — covers CFG-06 + D-12(b); parses the `.ld`, asserts the erase-unit
      property against the CFG-02 figure, and asserts the manifest names the flash driver (C-3)
- [ ] `tests/test_config_storage_seam_shape.py` — covers CFG-03; two declarations, three including
      TUs, `rurp_shield.h` unchanged (D-09)
- [ ] `tests/test_config_schema_pinned.py` — covers CFG-07; schema + `CONFIG_VERSION` + `config.cpp`
      absence
- [ ] `tests/test_config_storage_design_vendored.py` + `tests/test_flash_geometry_recorded_before_linker.py`
      — cover CFG-01 / CFG-02
- [ ] Framework install: **none needed** — `pytest 9.1.1` and `g++ 14.2.0` are present
- [ ] **No new `scripts/check_*.py`.** Phase 125's C-11 measured the cost: a new checker costs four
      artifacts plus bumps to `test_checker_convention.py`'s `FLOOR = 5` **and**
      `FIXTURE_FLOOR = 10`. Those floors are scoped to `scripts/check_*.py`, so `tests/test_*.py`
      files cost **zero** bumps

---

## Security Domain

`security_enforcement` is **absent** from `.planning/config.json` → treated as **enabled**.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | **no** | No principal, no credential. Firmware over USB CDC on a bench programmer |
| V3 Session Management | **no** | No sessions |
| V4 Access Control | **partial** | The only access decision is the flash **write-protection** option byte: RM §4.5.3 / §4.2.3.3 — if WRP covers the config pages, page erase is silently skipped and `WRPERR` is set. The backend must treat a HAL non-`HAL_OK` as `save() == false` and must not report success |
| **V5 Input Validation** | **YES — the load-bearing one** | Every byte read from flash slots A and B is **untrusted input**: it may be blank (`0xFF`), garbage from a partial write, or left over from an unrelated firmware image. `magic`, then `length`, then `crc32` must each be validated **before** any of them is used, and `length` must be bounds-checked **before** it reaches a `memcpy` |
| V6 Cryptography | **no — and say so explicitly** | **CRC32 is not a security primitive.** It detects accidental corruption. It provides **no** tamper resistance: anyone who can write flash can recompute the CRC. Do not let "CRC-protected" drift into "authenticated" in any artifact this phase writes |
| V7 Error Handling / Logging | **partial** | D-15 deliberately declines to distinguish blank from corrupt on the wire. That is a scope decision, not a security control; nothing sensitive is logged either way |
| V10 Malicious Code | **partial** | The SDK is pinned to a full 40-char commit SHA with `GIT_SHALLOW FALSE`. This phase adds no new fetch source and no new pin (§Package Legitimacy Audit) |

### Known Threat Patterns for this stack (firmware / on-device persistence)

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| **`length` from flash used as a copy bound** — the single most dangerous field in `StoredConfiguration`. A corrupt or hostile `length` larger than the caller's buffer becomes a RAM overflow on a Cortex-M0+ with no MPU configured and a 16 KiB SRAM | **Tampering / Elevation** | **Reject the record if `rec.length > len` *before* using it**, and copy `min(rec.length, len)`. Note the CRC does **not** save you: the check must be ordered before the copy, and a hostile writer can produce a valid CRC. Make this an explicit assertion in the CRC-rejection test |
| Blank flash (`0xFF`) mistaken for a valid record | Tampering (accidental) | `magic` must not be `0xFFFFFFFF` (nor `0x00000000`). This is what makes D-15's `blank` test meaningful rather than a CRC-collision inference |
| Torn write leaving neither slot loadable | **Denial of Service** | Dual-slot + erase-inactive-first + CRC (D-16 as corrected by C-2). RM §4.2.3 states outright that *"if a reset occurs during Flash program and erase operations, the contents of the Flash memory are not protected"* |
| Two bad CRCs treated as fatal → bricked unit | Denial of Service | D-15: fall back to defaults and persist. MERGE-04 already refuses every PROM-energising operation on py32, so a defaulted config cannot drive hardware |
| Buffer over-read into flash: `HAL_FLASH_Program` reading 64 words from a 36-byte object | **Information Disclosure** | C-2's mandatory 256-byte staging buffer. Without it, ~220 bytes of adjacent RAM are written into flash and become readable via `DFU_UPLOAD` |
| Unbounded flash wear as a wear-out attack | Denial of Service | Out of reach here: `rurp_save_config` is host-command-driven and the write count is bounded by operator actions. The `uint32_t` sequence deliberately has no rollover branch (Discretion) |
| Config write during a PROM programming pulse | Tampering | RM §4.2.3 — the bus stalls and interrupts are masked during erase/program (C-7). Not exercisable today (MERGE-04 refuses PROM operations on py32); carry as an explicit **non-claim**, do not schedule work against it |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `python3` + `pytest` | CFG-01…CFG-07 test harnesses | ✓ | pytest 9.1.1 | — |
| `g++` (host) | Compiling the HAL-free core and policy layer under test (D-02/D-03) | ✓ | Debian 14.2.0 | — |
| `g++ -m32` | Reproducing the ARM/AVR `long` width on the host | **✗** | — | **None.** No multilib (`bits/libc-header-start.h` missing). Mitigation: assert symbolically, never on literals (C-6) |
| `avr-g++` | AVR struct sizes; the three AVR builds | ✓ | 7.3.0 (`~/.platformio/packages/toolchain-atmelavr/bin/`) | — |
| PlatformIO Core | `pio run` ×3 AVR, `pio test` ×2 native | ✓ | 6.1.19 | — |
| `git` | Blob SHAs, `rev-list --is-ancestor` ordering proof | ✓ | present | — |
| `gh` | Reading the pinned SDK at its exact SHA; the gated CI-evidence workflow run | ✓ | present, authenticated | — |
| **`arm-none-eabi-gcc`** | Building the ARM target; measuring ARM flash/RAM | **✗** | — | **None.** ARM evidence is a **CI workflow run URL + head SHA**, never a local build. Gated per the push gate |
| **`cmake`** | Configuring the ARM build; resolving `PY32_SDK_ROOT` via FetchContent | **✗** | — | **None.** C-3's missing-source-list defect is therefore **CI-detectable only**; mitigate with the `tests/` manifest assertion |
| **`ninja`** | ARM build backend | **✗** | — | None (same as above) |
| Puya PY32F071 SDK working copy | Reading `py32f071xB.h`, `py32f071_hal_flash.{h,c}` | ✗ locally (FetchContent, not vendored) | pinned `0ed2f4b4…` | **Used successfully this session:** `gh api repos/OpenPuya/PY32F071_Firmware/contents/<path>?ref=0ed2f4b4…` — authoritative and reproducible without `cmake` |
| *PY32F07X Reference Manual V0.2* | CFG-02's citation | ✓ (downloaded) | V0.2, 913 pp., 22.6 MB | Direct URL recorded in §Sources; exceeds `WebFetch`'s 10 MB limit, so download + extract locally |
| `pypdf` | Extracting RM text **for research only** | ✓ (pip-installed this session) | — | **Not a project dependency.** Do not add it to any manifest |
| **PY32F071xB PCB** | Any claim about silicon behaviour | **✗ — does not exist** | — | **None, and none is possible.** Every silicon statement is a recorded non-claim per the Validation Ceiling |

**Missing dependencies with no fallback (blocking a claim, not the work):**

- `arm-none-eabi-gcc` / `cmake` / `ninja` — ARM flash/RAM are **unmeasurable locally by anyone**.
  Every ARM size or build claim cites a workflow run URL + commit SHA. **Consequence for C-3:** the
  missing `py32f071_hal_flash.c` can only be *proven* fixed by a CI run, which is gated. Add the
  local `tests/` manifest assertion so the defect is at least *detectable* here.
- `g++ -m32` — the host cannot be made to match the target's `long` width. Handled by C-6's
  discipline rather than by tooling.
- A PY32F071 PCB — D-14's first-boot flash stall, DFU config preservation, and every "it works"
  statement remain non-claims.

**Missing dependencies with fallback:**

- The SDK working copy → `gh api` at the pinned SHA (used throughout this research; fully
  reproducible).
- The RM via `WebFetch` → `curl` + `pypdf` locally (the PDF is 22.6 MB, over the fetch limit).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `sizeof(rurp_configuration_t) == 20` and `sizeof(StoredConfiguration) == 36` under `arm-none-eabi-gcc` (AAPCS ILP32, `long` = 4 B, 4-byte alignment) | C-6 | **Low, by construction.** Deliberately not load-bearing: no test asserts it, and every plausible layout fits inside one 256-byte page — which is the only property asserted. Unverifiable locally (no ARM toolchain) |
| A2 | Erased PY32F071 flash reads `0xFF` in every byte | Anti-Patterns, D-15 | **Low.** Standard for NOR flash and implied by RM §4.2.3's erase model, but not stated as a byte value in the RM chapter read. Only affects the choice of `magic` and the blank fixture; if it were `0x00`, the same rule (magic must be neither all-ones nor all-zeros) still holds |
| A3 | Flash endurance is ~10⁴ erase cycles, the figure the "no sequence wraparound" comment cites | Discretion | **Low.** Searched RM V0.2 pp.29–60 and **did not find** an endurance figure — it lives in the PY32F071 datasheet, not this manual. It supports only a code comment, never a gate. If the comment needs a citation, take it from *PY32F071 Datasheet* (V0.8 or Rev 0.4), not the RM |
| A4 | The DFU bootloader publishes a DfuSe memory layout, so `DEFAULT_ERASE_PAGE_SIZE = 2048` never fires | C-9 | **Low for this phase** (host-side, Phase 127 owns it). Unverifiable without a board. Recorded in the contract rather than acted on |
| A5 | Page erase is genuinely independent on silicon — erasing page 481 cannot disturb page 480 | C-5 | **Mitigated to near-zero** by the recommendation: the reservation is sector-aligned, so the property holds under **either** page or sector granularity. Unverifiable without a board. This is exactly why the sector-aligned variant is recommended over the 512 B one |
| A6 | The `PROVIDE` + `ASSERT` linker syntax in §Code Examples assembles as written under `arm-none-eabi-ld` | Code Examples | **Medium-low.** Standard GNU ld, but untested here (no ARM toolchain). Treat the block as a design sketch the executor must compile in CI, not as verbatim final text. `ASSERT` with `%` on region origins is the likeliest thing to need adjustment |
| A7 | The two `MEMORY` regions `BOOTLOADER` (LENGTH 0) and `FLASH` sharing `ORIGIN = 0x08000000` is accepted by `arm-none-eabi-ld` | Code Examples, D-13 | **Medium-low.** Legal in GNU ld for a zero-length region, but the exact diagnostic behaviour is untested here. If it is rejected, D-13's seam can be expressed as a `PROVIDE(__bootloader_region_start = 0x08000000); PROVIDE(__bootloader_region_size = 0);` pair instead — which keeps the named seam and the honest comment, and is what to fall back to. **Do not drop D-13** (operator decision) |

**Everything else in this document is `[VERIFIED]` or `[CITED]`** — read from primary sources this
session (the pinned SDK via `gh api`, the RM PDF, the live repo, the `4b1a441` blob) or measured with
a compiler. Notably `[VERIFIED]`, not assumed: the 256 B / 8192 B geometry (two independent sources),
the single page-program primitive, the absent `hal_flash.c`, the in-HAL timing-register
configuration, HSI already on, host and AVR struct sizes, the native `build_src_filter` set, the
AVR size headroom, C linkage, and all seven config-API call sites.

---

## Open Questions

1. **Reserve one 8 KiB sector, or 512 bytes? (needs a one-line operator confirmation)**
   - *What we know:* CFG-06's letter is satisfied by two adjacent 256 B pages, because page erase is
     a real primitive (C-5). D-10's text says `LENGTH` "shrinks by two erase units", which reads as
     512 B.
   - *What's unclear:* whether the operator intends the minimal reservation or accepts a
     sector-aligned one. The DFU bootloader's published erase granularity is unknown (no board), so a
     512 B reservation at `0x0801FE00` leaves config inside the app's last 8 KiB sector — a stated
     hazard rather than an eliminated one.
   - *Recommendation:* **reserve Sector 15 whole** (`FLASH` → 120K). It removes the hazard instead of
     documenting it (the `<specifics>` tie-breaker), keeps every locked element of D-10/D-11, costs
     7680 B of slack that FUT-N05 can later claim, and — because it changes the *quantum* of a shrink
     D-10 already mandates — is a refinement, not a reversal. Confirm before planning; this is the
     cheap moment (and D-10 is one of the two decisions CONTEXT itself flags as expensive to reverse
     later, since Phase 129 will cite the addresses).

2. **D-16's amendment: single-page commit, or two-page slots? (planner decision, recommendation given)**
   - *What we know:* "program the header/CRC word LAST" is unimplementable — one program primitive,
     256 B (C-2).
   - *What's unclear:* nothing factual; only which correction to adopt.
   - *Recommendation:* single page per slot, commit = program completion, CRC rejects a torn page.
     Record the amendment **explicitly** with the RM citation in both `CONFIG-STORAGE.md` and the
     plan. Two-page slots add a failure mode CRC already covers.

3. **What is `CONFIG_MAGIC`?**
   - *What we know:* blob `4b1a441` specifies the field but not its value. It must be neither
     `0xFFFFFFFF` (blank flash) nor `0x00000000`.
   - *Recommendation:* pick one fixed 32-bit constant (e.g. an ASCII four-CC such as `'F','S','C','1'`),
     define it once in the core's local header, and record it in `CONFIG-STORAGE.md` as a
     *this-milestone* choice rather than a vendored one — since the blob does not supply it, claiming
     it was vendored would be an overclaim of the kind Phase 122's C-5 had to correct.

4. **Does the `StoredConfiguration.version` (u16) get a value, and does anything read it?**
   - *What we know:* D-17 pins it as **not** `CONFIG_VERSION`, and explicitly warns against
     "reconciling" them. No consumer exists.
   - *What's unclear:* whether writing a constant `1` and never branching on it violates the "a
     declaration with no consumer does not land" rule (Phase 124 D-01).
   - *Recommendation:* it does **not** violate it — the field is part of a vendored on-flash format
     (D-17) whose whole point is forward-compatibility, and it is *written*, not merely declared.
     Set it to `1`, comment that no reader branches on it yet, and do **not** add a version-dispatch
     branch that can never execute.

5. **Can the CFG-04 test really name both TU paths from the start? (Discretion flags it "verify this
   survives contact")**
   - *What we know:* D-08 locks the post-refactor path in advance, so naming both is legitimate.
   - *What's unclear:* whether a `g++` invocation naming a not-yet-existing path can be made to
     compile cleanly pre-refactor without a skip.
   - *Recommendation:* filter the path list to existing files **at collection time** and assert
     non-vacuity two ways (≥1 path resolved **and** the fake `EEPROM.h` recorded ≥1 call) — never a
     `pytest.skip`, which is the fail-open shape A-7 is about. If it cannot be made to work, take the
     documented fallback: one named, justified line change with **both** blob SHAs recorded.

6. **How is the ARM link failure from C-3 actually proven fixed?**
   - *What we know:* only a CI run can build ARM, and any push is behind the operator gate.
   - *Recommendation:* land the local `tests/` manifest assertion (detects the omission here), and
     structure the plan so the gated `gh workflow run` / `git push` command is **printed and the plan
     stops** — no task executes it (Plans 124-11 / 125-05 shape). Treat the resulting run URL + head
     SHA as the sole ARM evidence, recorded in `126-NONREGRESSION.md`.

---

## Sources

### Primary (HIGH confidence — read or measured this session)

- **Puya, *PY32F07X Series Reference Manual*, V0.2** — 913 pp., downloaded and text-extracted
  locally. §4.1 "Key features" (p.34) · §4.2.1 "Flash structure" + **Table 4-1 "Flash structure and
  boundary addresses"** (p.34) · §4.2.2 (p.35) · §4.2.3 (p.35) · §4.2.3.1–.2 (pp.36–37) · §4.2.3.3
  Page erase (p.37) · §4.2.3.4 Mass erase (p.38) · §4.2.3.5 Sector erase (p.38) · §4.2.3.6 Program
  and erase time configuration (p.39) · §4.5.3 Flash write protection (p.52, TOC).
  `https://www.puyasemi.com/download_path/用户手册/MCU 微处理器/PY32F07X_Reference_Manual_V0.2.pdf`
- **Pinned SDK `OpenPuya/PY32F071_Firmware` @ `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`** (read via
  `gh api`, the exact `GIT_TAG` in `platform/py32f071/CMakeLists.txt:16`) —
  `Drivers/CMSIS/Device/PY32F071/Include/py32f071xB.h:575–581` (geometry) ·
  `Drivers/PY32F071_HAL_Driver/Inc/py32f071_hal_flash.h:145–147, 268, 474–505, 615–631` (erase/program
  types, timing macros, validation macros) ·
  `Drivers/PY32F071_HAL_Driver/Src/py32f071_hal_flash.c:340–369, 416, 430–500, 526, 585, 597–608, 674, 905`
  (`FLASH_Program_Page`, page/sector erase loops, timing-config call sites) ·
  `Drivers/PY32F071_HAL_Driver/Src/py32f071_hal.c:147, 163` (HSI as the default clock).
- **Live firmware tree** `/workspaces/firestarter` @ `v1.23-py32f071-integration` `2b5e8c8` —
  `src/rurp_config_utils.cpp` (40 lines, `CONFIG_START` at `:11`, write-back at `:38`) ·
  `platform/py32f071/src/config.cpp` (47 lines; the four drift points) ·
  `platform/py32f071/linker/PY32F071xB_FLASH.ld:3–7` · `platform/py32f071/CMakeLists.txt:16, 30–34,
  35–53, 55–63, 65–80` · `platform/py32f071/include/py32f071_hal_conf.h:8, 10, 53` ·
  `platform/py32f071/src/main.cpp:21–35` · `include/rurp_types.h:19–24` ·
  `include/rurp_shield.h:11–12, 17, 46, 49–50, 61, 150–152, 161–162` · `platformio.ini:163, 252, 290` ·
  `scripts/check_cmake_manifest.py` (docstring) · `scripts/baseline/size_baseline.json` ·
  `tests/test_vpp_seam_manual_on_every_board.py:1–130` ·
  `test/native/avr/test_data_input/host_stubs.cpp:62–71`.
- **Blob `4b1a441`** (`platform/py32f071/PORTING.md`, 195 lines) — read verbatim via
  `git cat-file -p 4b1a441`; **confirmed readable** from the local clone. §"Configuration storage"
  (in scope) · §"PY32F071 backend modules" (superseded) · §"ADC measurement" / §"DAC VPP control"
  (out of scope) · the 15-item acceptance checklist.
- **Compiler measurements** — `g++ 14.2.0` and `avr-g++ 7.3.0` (`-mmcu=atmega328p`): `sizeof(long)`,
  `sizeof(rurp_configuration_t)`, `sizeof(StoredConfiguration)`, `offsetof(…, crc32)`, and the
  `-m32` unavailability.
- `framework-arduino-avr/libraries/EEPROM/src/EEPROM.h:130–142` — the real `get`/`put` template
  signatures and `put`'s per-byte `update()` semantics.
- **Host repo** `/workspaces/firestarter_app_py32` @ `feature/py32f071-fw-install` —
  `firestarter/py32_dfu.py:100–115` (`FLASH_BASE`, `FLASH_SIZE`, `DEFAULT_ERASE_PAGE_SIZE`), `:648`
  (`_check_envelope`), `:740–760` (payload-scoped `erase_addresses`).
- **Planning contract** — `.planning/REQUIREMENTS.md` (Validation Ceiling lines 8–22; CFG-01…07 lines
  62–68; Out of Scope 136–151; Operator Decisions item 5) · `.planning/ROADMAP.md` §Phase 126 (lines
  2197–2212) · `.planning/research/SUMMARY.md` §A-6, §A-7, §"Phase 126", §"Gaps to Address" ·
  `126-CONTEXT.md` in full · `/workspaces/CLAUDE.md`.

### Secondary (MEDIUM confidence)

- The dual-slot / A-B CRC config-record pattern as general embedded practice — corroborated against
  blob `4b1a441`'s own specification and the RM's stated reset-during-write hazard, which is what
  raises it above a bare web claim.

### Tertiary (LOW confidence — recorded because it was **disproved**, not relied on)

- A WebSearch result asserting *"128-byte page size and 4KB sector erase information for the
  PY32F071xB variant"*. **Wrong** — those are PY32F030/F003 figures, contradicted by both primary
  sources (C-1). Retained here so no later reader re-imports it. The same search *was* useful for
  one thing: identifying that the correct document is the **PY32F07X** Series Reference Manual (not a
  PY32F071-specific RM, which does not exist) and its download URL.

### Not found (stated so it is not re-searched)

- Flash **endurance** (erase-cycle count) and **erase/program timing** figures — absent from RM V0.2
  §4 (searched pp.29–60). They belong to the *PY32F071 Datasheet* (V0.8 / Rev 0.4). Only needed if
  the sequence-wraparound comment or D-14's stall cost is ever made a numeric claim — and D-14 is
  explicitly a non-claim.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| Flash geometry (CFG-02) | **HIGH** | Two independent authoritative sources agreeing exactly: the vendor RM (§4.1/§4.2.1/Table 4-1) and the pinned SDK part header (`py32f071xB.h:578,580`). Also identified and disproved two competing wrong values |
| HAL flash contract (program granularity, erase units, timing registers, `hal_flash.c` absence) | **HIGH** | Read from the pinned SDK at its exact commit SHA and cross-checked against the RM's register sequences |
| In-tree facts (sizes, filters, linkage, call sites, headroom, native counts) | **HIGH** | Every one measured or grepped this session in the live tree; nothing recalled from prose |
| Struct layout | **HIGH** for host and AVR (compiled); **LOW** for ARM (computed, and deliberately not load-bearing) | `-m32` unavailable; no ARM toolchain |
| Architecture / seam design (CFG-03, CFG-04) | **HIGH** | The seam is CFG-03 verbatim plus D-06/D-07; all seven consumers enumerated and shown to sit above it |
| Dual-slot algorithm (CFG-05) | **HIGH** on the design; **MEDIUM** on the exact test-fake ergonomics | The algorithm follows the vendored spec and the verified primitive set; the abort-after-N-words hook is a design recommendation not yet compiled |
| Linker script text (CFG-06) | **MEDIUM** | Addresses and the erase-unit property are HIGH (RM Table 4-1); the exact `MEMORY`/`PROVIDE`/`ASSERT` syntax is untested here — no `arm-none-eabi-ld` (A6, A7) |
| Pitfalls | **HIGH** | Each is either measured this session (C-1…C-14) or a documented in-project recurrence (A-7, the vacuous `git diff`, the cold/warm size trap, the branch-switching `gsd-tools query commit`) |
| **Anything about PY32F071 silicon behaviour** | **NONE — structurally unavailable** | No PCB exists. No source can supply it. Every such statement in this document is marked a non-claim |

**Research date:** 2026-07-31
**Valid until:** the flash-geometry and HAL findings are **stable indefinitely** — they are pinned to
an immutable SDK commit and a published manual revision. Re-verify only if `GIT_TAG` in
`platform/py32f071/CMakeLists.txt:16` changes. The in-tree measurements (AVR sizes, native counts,
`build_src_filter`) are valid until the next commit touching AVR-compiled surface — **re-measure at
execute time regardless**, per the milestone's "measure, never predict" rule (v1.22 predicted a
saving and measured +204 B).
