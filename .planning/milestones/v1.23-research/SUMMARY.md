# Project Research Summary

**Project:** Firestarter — v1.23 PY32F071 Integration
**Domain:** Two-repo embedded system (AVR firmware + Python host CLI) gaining a fourth MCU board target (Puya PY32F071xB, Cortex-M0+) plus a host USB-DFU firmware installer
**Researched:** 2026-07-30
**Confidence:** HIGH on in-tree/measured state · MEDIUM on ecosystem convention · **LOW-by-construction on anything about PY32F071 silicon (no PCB exists)**

> **Validation ceiling — non-negotiable, restated verbatim in every downstream artifact.**
> Permitted claims: **the target builds clean; the native and host suites pass; the DFU sequence is exercised against device descriptors and mocks.**
> Forbidden: *"the firmware runs on a PY32F071"*, *"the install works end to end"*, and any claim that the provisional pin map is correct.
> A successful firmware install would prove nothing about the programmer working — the pin map is a placeholder that describes no existing PCB. **Those two claims must stay strictly separate everywhere.**

> **Provenance discipline.** Every quantitative claim below is tagged **[MEASURED-A]** (built/run by the ARCHITECTURE researcher), **[MEASURED-P]** (built/run by the PITFALLS researcher), **[MEASURED-S]** (commands run by the STACK researcher), **[READ]** (read out of a live tree/ref), or **[PREDICTED]**. No PREDICTED figure is presented as measured.

---

## Executive Summary

This is an **integration milestone, not a build-it milestone**, and the research confirms that framing more strongly than the planning record did. Three of the four researchers did not reason about the branches — they merged, built and tested them. The result: **21 host-side capabilities already exist and need landing, not building; 8 items remain to be built**, and only one of those eight (the release-asset publication) gates any user-visible value at all. The firmware port compiles the *shared* command processor, framing layer and PROM algorithms for Cortex-M0+ with **zero changes under `src/`** [READ], which is why the project's historically dominant fear — AVR flash growth — turns out not to be where v1.23's risk lives.

**The rebase is not the risk.** Both repos merge with **zero textual conflicts**, independently confirmed by two researchers, and the changed-file sets since merge base `a1953c2` (2026-06-18) are **completely disjoint** [MEASURED-A]. The merged firmware tree builds Leonardo at **26016 B / −56 B**, keeps `pio test -e native` at **141/141**, and — in a correct sibling layout — leaves the entire host suite green with all nine cross-repo gates *running* [MEASURED-A]. The real risk is the class git cannot see: `platform/py32f071/CMakeLists.txt:46-47` names two source files that v1.19 Phase 104 renamed, so git merges the file perfectly into a tree whose ARM target **fails at CMake configure time** — and because `py32f071.yml` has no `push` trigger, nothing on `beta` would report it. That finding arrived independently from STACK, ARCHITECTURE and PITFALLS and is the milestone's highest-confidence item.

**The dangerous risks are all about verification integrity, not code.** PITFALLS *reproduced* a fail-open defect in the host gate suite: renaming one firmware file flipped **five gate legs from PASS to SKIP with a false reason and exit 0** — and v1.23 is the first milestone whose entire premise is moving firmware files. It also found a **hollow gate inside the branch being landed** (`RURP_PY32F071_PINMAP_CONFIGURED` defined `1` two lines above `#if !… #error`, structurally unable to fire) while the provisional pins are driven live with no consumer of the `PROVISIONAL` flag. And PROJECT.md's prescribed build order — land `portability-macros` first, then the port — is **actively wrong**: that branch alone takes the native suite from 141/141 to **0 passing / 17 suites ERRORED**, because its own repair commit lives on the branch stacked above it. The mitigation shape is settled house style: gates and baselines authored **before** anything moves, every checker shipped with a planted-violation pytest, and a claim gate copied from v1.22's Phase-122 original.

---

## Key Findings

### 1. Already built vs still to build — the countable split

Conflating these is the single biggest scope-inflation risk on an integration milestone.

| | Count | Notes |
|---|---|---|
| **Already implemented, needs landing** | **21** (E-01…E-21) | Verified by direct source read of the branch, not from branch notes. Includes the whole DFU client, class-based discovery, ambiguity refusal, envelope guard, dual dialect, portless install, channel gate, 46 tests, 273-line operator doc, and both `.hex`+`.bin` emission |
| **Still to build** | **8** (N-01…N-08) | Only **N-01** (release-asset publication) is load-bearing for v1.23. N-02/N-03 are differentiators; N-04/N-05 defer; N-06/N-07 are records/docs; N-08 is silicon-gated |

**Two things the planning record said needed work are already done** and must not be re-planned:
- **The `.hex`-extension hardcoding is closed.** `firmware.py:155/:237/:336` are now `asset_candidates()` / `_pick_asset()`, and **all four call sites** use them. Hex is preferred because Intel HEX carries its own load address, which `_check_envelope()` validates; a raw `.bin` can only be *assumed* to start at `FLASH_BASE`. Download naming round-trips correctly from the URL's last path segment. [READ, corroborated by STACK C-5 and ARCHITECTURE seam 2]
- **The flasher-strategy extraction was deliberately *not* done** — and that is the right deviation. The constraint was "keep the bench-earned avrdude ladder verbatim"; the branch achieves it by not touching `_install_with_avrdude` at all. Record the deviation; do not "fix" it.

### 2. Recommended stack (from STACK.md)

The ARM target is deliberately **orthogonal to PlatformIO** — it adds zero lines to `platformio.ini`, which is the single most important property for the hard acceptance constraint.

**Core technologies:**
- **`arm-none-eabi-gcc`** — Cortex-M0+ cross-compiler. Currently apt-installed on `ubuntu-latest`; **recommend pinning** `runs-on: ubuntu-24.04` + `carlosperate/arm-none-eabi-gcc-action@v1` with an explicit `release:`. An unpinned compiler under a published firmware binary is inconsistent with this project's byte-identity house standard.
- **CMake ≥ 3.20 + Ninja** — second, independent build system for the ARM target. Keeps AVR untouched; its cost is a **hand-maintained source list** (finding C-1's root cause). Note `FetchContent_Populate` is deprecated since CMake 3.30 and will start warning as runners drift [PREDICTED].
- **OpenPuya PY32F071 SDK, tag `1.1.1` = `0ed2f4b`** — the pin is simultaneously the latest release tag *and* `master` HEAD [READ via `git ls-remote`], and **all 15 SDK paths the CMakeLists names exist at the pin** [READ, verified per-path]. BSD-3-Clause, but 7 commits / 4 stars: a real bus-factor risk. Vendoring becomes the right answer the moment the ARM image is a published release asset.
- **CherryUSB (CDC-ACM), vendored inside the SDK, unversioned** — honestly characterised: this is **"Puya's CherryUSB fork"**, not CherryUSB. Upstream has **no `py32` port** [READ of upstream `port/`], so upstream releases cannot be adopted without re-porting. Track the SDK tag, not CherryUSB. CDC-only is safe with `_Min_Heap_Size = 0x000` because `usb_malloc` is called only from the printer/audio/vendor classes [READ, grep] — but adding any class is a NULL-deref-at-enumeration tripwire.
- **pyusb as an optional `[py32]` extra** — genuinely optional and **proven so**: the 58-test suite passes with `usb` not importable [MEASURED-S]. Recommend raising the floor from `>=1.2.1` to `>=1.3.1,<2` at zero cost. libusb is a system prerequisite; **Windows needs WinUSB via Zadig** — the honest residual, documented on the branch, and the reason the self-flash seed stays open.
- **No RTOS.** The SDK vendors FreeRTOS and it is deliberately not compiled. A scheduler would fork the execution model away from AVR inside PROM bus windows.

**One concrete stack defect worth a one-token fix:** the port passes `FLASH_ACR_LATENCY_1` (= two wait states) where Puya's own CDC reference passes `FLASH_LATENCY_1` (= one, correct for 48 MHz) [READ of both]. Safe but needlessly slow on a part servicing USB alongside microsecond PROM strobes — and a timing anomaly found after a PCB exists would be blamed on the board.

### 3. Architecture approach (from ARCHITECTURE.md)

The fourth target attaches **below** an unmodified protocol layer, via a compat shim at the platform edge rather than a call-site rewrite.

**Major components:**
1. **Protocol/algorithm layer** (`src/proms/*`, `firestarter.cpp`, `json_parser.c`) — **UNMODIFIED**, zero py32 changes under `src/` [READ]. This is why golden traces, the dispatch-mirror guard and the flash budget are structurally protected.
2. **`platform/py32f071/include/Arduino.h`** (76 lines) — the load-bearing seam. A fake Arduino core (`delay`, `delayMicroseconds`, `millis`, `micros`, `byte`, `HIGH`/`LOW`, `Serial`) over `RURP_*` primitives. The ten common TUs that `#include <Arduino.h>` keep doing so.
3. **`include/rurp_platform_compat.h` + `include/avr/pgmspace.h`** — PROGMEM vocabulary neutralised off-AVR, plus an `#include_next` shadow so even the **codegen-generated** `messages.h` (which cannot be hand-edited) ports for free. The shadow was **empirically verified to chain correctly on AVR** by a direct `avr-g++ -E -H` trace [MEASURED-A].
4. **`include/rurp_shield.h`** — the 40-declaration logical HAL contract; the portability branch converts six control macros to `static inline` and swaps the include. All 40 declarations resolve in the merged tree [MEASURED-A].
5. **`platform/py32f071/src/{py32f071_rurp_shield,timing,usb_cdc,config,platform_compat,main}`** — the ARM backend (317 L shield, real CherryUSB, SysTick ms + TIM3 µs).
6. **Host: `py32_dfu.py` (832 L) + `channel.py` (81 L) + `firmware.py` (+246/−33)** — DFU client, double-enforced beta-only gate that reads no environment and fails closed, and a `flash_method()` dispatch defaulting unknown boards to avrdude.

**Two named deviations to record rather than repair:** the boundary is "a fake Arduino, not a named HAL" (`PORTING.md`'s *"Arduino timing calls are removed from common code"* is **UNSATISFIED**, by choice — the sweep would touch every golden trace for zero functional gain), and the flasher strategy was not extracted (§1).

**The recommended new work is one seam, not a rewrite:** split `rurp_config_utils.cpp` by *concern* — policy stays common, only a two-function byte-blob backend goes per-platform. PR #48's `config.cpp` has **already drifted from AVR policy** (extra `r2 == 0` check, `memset`, `0xFFU`, and a `rurp_save_config()` that persists nothing) [READ], which is the symptom this pattern removes. Critically, the record wrapper **embeds** `rurp_configuration_t` rather than extending it ⇒ **no schema change, no `CONFIG_VERSION` bump, no EEPROM migration**, so the queued White-Box Voltage Calibration milestone is not pre-empted.

### 4. Expected features (from FEATURES.md)

**Must have (table stakes):**
- **N-01 published release asset `firestarter_py32f071.hex`** — today it is an *Actions artifact* (ZIP, different API, auth-gated, 90-day expiry) while `_pick_asset()` reads release *assets*. Until this lands, `fw --install --board py32f071` cannot resolve a URL and **the entire E-01…E-21 stack is unreachable**. LOW complexity, firmware-repo CI, and it must build in `beta-build.yml`'s job *after* `update_version.py` or the image carries a stale `VERSION` — which *is* the host's whole update decision.
- Discovery that **names what it found and refuses ambiguity** (done) — DFU runtime interfaces exist on unrelated peripherals; this devcontainer's webcam `04f2:b751` advertises one.
- **Actionable manual bootloader-entry text** (done) — the highest-value item in the ecosystem survey (esptool, tinyuf2, Katapult all do it).
- **Flash-envelope refusal before any byte is sent** (done), deliberately **not** overridable — contrast `dfu-util :force`.
- **A typed `--board` conflicting with the attached programmer is refused** (done) — found the hard way; it flashed a live Leonardo.
- **N-06 PCB requirements recorded before the first schematic** and **N-07 two-route documentation** including the **"socket empty before any py32 firmware install"** safety line. Klipper documents the analogous hazard (DFU mode energising outputs); the Firestarter version is stronger because the pin map is provisional.

**Should have (differentiators):**
- **`fw --dfu-probe`** (done) — no comparable tool ships a bus-truth reporter aimed at settling its own unknowns. It converts USB-ID and dialect from open questions into one command on first silicon.
- **Beta-only channel gate** (done) — nothing in the ecosystem survey does this. Graduates by deleting one tuple entry. **Must not be weakened to make anything demonstrable.**
- **N-03 `DFU_UPLOAD` readback verification** — the strongest build-it argument in FEATURES: avrdude verifies by default on all three AVR boards, so v1.23 as it stands would ship the project's **first firmware-install path that writes flash without reading it back**, on the one target whose dialect and geometry are unconfirmed. The constant is reserved and unused; the mock harness already exists. Must fail soft on `bitCanUpload = 0`. Claim ceiling: *"asserted against a mock"*.

**Defer:**
- **N-02 progress reporting** — reclassified from table stakes to polish, because avrdude's own progress is **swallowed** by `Popen(...PIPE) + communicate()` on all three shipped boards. Adding it only to py32 would give the unproven path the only live feedback. First thing to cut.
- **N-04 reboot-into-bootloader** — Cortex-M0+ has **no VTOR**; the `SYSCFG MEM_MODE` remap is reported to "have no effect" on some sibling F0 parts, plus a dual-repo gate tail. Unvalidatable, and **N-05 obsoletes it** for the normal path.
- **N-05 self-flash bootloader over CDC + COBS** — the seed's *primary* route, its own milestone. Landing DFU **does not retire the seed**; a phase artifact must say so or the seed gets closed by implication.
- **Published `.bin` asset** — host acceptance already exists; publication waits for N-05.

**Anti-features worth naming:** hardcoding `--usb-id 0448` (that is a *device ID in a bootloader-parameter table*, not a confirmed USB PID — a wrong default filter makes discovery fail to find the real board); a `--force` that overrides the envelope guard; bundling `dfu-util`/`PY32DfuTool`/`puyaisp`; letting the bootloader self-update (Katapult ships this; the seed's no-self-update rule is the stronger position); and **claiming the install works because 46 tests are green** — the milestone's central honesty risk.

### 5. Critical pitfalls (top 5 of 11)

1. **`agent/portability-macros` cannot land alone** — see Adjudication #4. Land the two branches **atomically**.
2. **A firmware rename turns cross-repo gates into silent SKIPs at exit 0** — see Adjudication #7. Split the proxy; assert the skip census.
3. **The conflict-free merge is semantically wrong** — see Adjudication #2. Ship a CMake-manifest drift gate with a planted fixture; it is the most durable artifact v1.23 can leave behind.
4. **A hollow gate inside the branch being landed** — `RURP_PY32F071_PINMAP_CONFIGURED` is `1` two lines above `#if !… #error`, so the guard is structurally incapable of firing; `RURP_PY32F071_PINMAP_PROVISIONAL` has **zero consumers** while `py32f071_rurp_shield.cpp` drives the provisional pins live [READ, grep]. v1.18 was an entire milestone caused by one mis-modelled pin, and PITFALLS rates "provisional pin map trusted near a PROM" as **potentially unrecoverable — prevention only**.
5. **Overclaiming, in five specific shapes each with an in-project precedent** — "CI is green"→"it works", "the DFU sequence is correct"→"the install works", "the pin map compiles"→"the pin map is right", "the VPP seam landed"→"VPP control works", and derived-number over-precision. Mitigation is mechanical *and* judgement: copy v1.22's `check_permitted_claims.py` (8 forbidden patterns, 1 required caveat, explicit target list, fail-closed on zero targets, 7 subprocess legs, 4 fixtures) **and** budget the blocking operator wording review, because the gate is explicitly *"the mechanizable half ONLY"*.

Also material: **58 additional macro-redefinition warnings per native suite** on the merged tree (138 vs 80 for `test_dispatch`), from `rurp_platform_compat.h` colliding with ArduinoFake [MEASURED-P]. Individually harmless; collectively they **bury the next real warning**. Fix, then gate `grep -c redefined` at 0.

---

## Adjudicated Conflicts

Seven findings arrived from more than one researcher. Each is resolved explicitly below — no averaging, no silent picks.

### A-1. Leonardo flash headroom: **2600 B on `beta`; 2656 B on the merged tree. Both researchers are right; 2992 B is stale.**

There is no real disagreement — the two figures describe **different trees**, and ARCHITECTURE says so itself (§7 X-4: *"2600 B on `beta`, 2656 B after the merge"*).

| Tree | Flash used / total | Headroom | Provenance |
|---|---|---|---|
| `beta` @ `5c9160a`, `-D DEV_TOOLS` (the binding config) | 26072 / 28672 (90.9 %) | **2600 B** | [MEASURED-P] and [MEASURED-A], agreeing exactly |
| Merged (portability + py32 stack) | 26016 / 28672 (90.7 %) | **2656 B** | [MEASURED-A] and [MEASURED-P], agreeing exactly (−56 B) |

**Arithmetic retiring 2992 B:** the recorded figure is 25680 / 28672 → 2992 B. Phase 119 added a **measured +392 B** SDP lock. 25680 + 392 = **26072**, which is byte-exactly what `beta` builds today. Both researchers reject 2992 for that same reason, independently.

**Ruling for requirements:** *budget* new work against **2600 B** (the pre-merge baseline every delta is judged from); state the *live post-merge* headroom as **2656 B**. Delete 2992 B from PROJECT.md and STATE.md. Note also that **Leonardo RAM — 2014 / 2560, 546 B free — has no historical figure at all** [MEASURED-P]; record RAM alongside flash from now on, because a `PROGMEM`→RAM regression is invisible in a flash number.

### A-2. The C-1 CMake source-list defect: **triple-corroborated; the milestone's highest-confidence finding.**

Found independently by **STACK** (Rebase Hazard H-1), **ARCHITECTURE** (collision C-1, ranked BLOCKER) and **PITFALLS** (Pitfall 3). `platform/py32f071/CMakeLists.txt:46-47` names `src/proms/flash_type_3.cpp` and `src/proms/flash_type_4.cpp`; **v1.19 Phase 104** renamed them to `flash_nor_unlock.cpp` and `flash_5v_page.cpp`.

- **When it bites: CMake *configure* time** — a missing explicit source is a hard configure failure, not a link error. Verified by path-validating the actually-merged tree: **2 of 16 paths MISSING, 14 OK** [MEASURED-A]; reproduced independently [MEASURED-P].
- **Why git is blind:** the merge base `a1953c2` (2026-06-18) predates the rename, and only the py32 side ever touched the CMake file. There is no hunk, so there is no conflict. Git produces a perfect merge of a broken tree.
- **Why no gate catches it today:** `py32f071.yml` triggers on **`pull_request` + `workflow_dispatch` only — there is no `push` trigger** [READ, three researchers]. Once this lands on `beta`, **nothing builds the ARM image on `beta` at all.** Compounding: the ARM build is also **unbuildable locally** — `arm-none-eabi-gcc`, `cmake` and `ninja` are all absent from this devcontainer [MEASURED-P, MEASURED-S].
- **Ruling:** the two-line fix is a **task inside the same phase as the merge**, not a follow-up; `push: branches: [beta]` lands in that same phase; and the **manifest-drift gate is authored before the merge** so the class is provably non-recurring. Note the list also omits four `beta` files, two deliberately (`dev_tools.cpp` is `DEV_TOOLS`-gated, `rurp_config_utils.cpp` is substituted) and two as rename damage — **and a reader cannot tell which is which from the file.** The gate needs an explicit, commented `PY32_EXCLUDED` allow-list.

### A-3. Merge conflict surface: **the two researchers agree — and the consequence is that the risk is the class git cannot see.**

- **ARCHITECTURE:** `git merge-tree --write-tree --messages beta feature/py32f071-release-assets` exits 0 with an empty conflict list; a real `git merge` in a scratch worktree succeeded; the changed-file sets since `a1953c2` are **completely disjoint** (46 files on `beta`, 22 on the py32 stack, intersection ∅); and the only two *existing* files the port modifies — `include/rurp_shield.h` and `include/rurp_serial_utils.h` — are **byte-identical between merge base and `beta`** (`git diff --quiet` → 0). Host repo likewise exits 0. [MEASURED-A]
- **PITFALLS:** independently reports zero conflicts for **both** the five-commit cherry-pick (`532997c c0c6695 b253092 adb133a 52d6c1f`) and the `--no-ff` merge, in both repos. [MEASURED-P]
- **Ruling: agreement confirmed, from two different mechanisms (merge-tree + real merge vs cherry-pick + real merge).** The consequence: **"the merge had no conflicts" must never be used as a quality statement.** The rebase risk is *not* hunk resolution — it is stale data references (A-2), silent gate skips (A-7), and non-self-sufficient intermediate states (A-4). Verification must be **structural**: every build-manifest path resolves; flash/RAM/native-case-count equal the recorded baseline; the nine cross-repo gates *run* (not skip) and pass; and anything claimed untouched is proven with `git -C … status --porcelain` empty or literal blob SHAs — **never** a path-scoped `git diff`, which passes vacuously on a wrong path (the v1.22 `src/flash_utils.h` trap).
- **Also settled, in the milestone's favour:** `src/boards/rurp_common.cpp`, `include/rurp_types.h` and `src/rurp_config_utils.cpp` are byte-identical between merge base and `beta`, so the documented PR #45 / White-Box-Calibration collision is a **future-milestone** collision, not a rebase collision. And the **only** textual conflict anywhere in the six-branch inventory is `include/rurp_shield.h` between the py32 stack and **PR #45** — which independently vindicates *"cherry-pick nothing from #45; hand-author the seam."*

### A-4. `agent/portability-macros` cannot land alone: **PROJECT.md's build order is a trap. Correction is unambiguous.**

- **PITFALLS measured it.** Cherry-picking the five `portability-macros` commits onto today's `beta` — exactly the "land the HAL prep first, then the port" sequence PROJECT.md describes — takes `pio test -e native` from **141 cases / 17 suites all passing to 0 passing / 17 suites ERRORED**. Hard compile failure: `implicit declaration of function 'pgm_read_ptr'` and `'strncmp_P'` in `src/json_parser.c`. Cause: the branch swaps `<avr/pgmspace.h>` for `rurp_platform_compat.h`, whose portability-branch version defines `pgm_read_byte/word/dword`, `memcpy_P`, `strcpy_P`, `strlen_P`, `strcmp_P` **and stops** — while the native env previously resolved to the seven `test/native/avr/*/avr/pgmspace.h` stubs, which **do** define the four missing helpers. The repair, commit **`780a3fb`**, lives on the **stacked** `agent/py32f071-toolchain` branch. [MEASURED-P]
- **ARCHITECTURE points the same way from a different angle:** that branch is **4 files / 123 insertions** and contains **no `rurp_platform.h`, no pin-map work, and no capability macros**; its timing functions have **zero common-code consumers**. There is nothing in it that constitutes independent HAL prep. [MEASURED-A / READ]
- **Ruling: they must land ATOMICALLY.** The gh#16-inherited *"HAL prep leads, then the port"* framing is a **trap** — the branch that reads as "the safe, small, board-agnostic half" is the one that is **not self-sufficient, and its own repair is on the branch stacked above it.** If two commits are wanted for reviewability, `780a3fb` must be reordered or cherry-picked into the first. **Never commit an intermediate state with `portability-macros` on the integration branch and the py32 stack not.** Gate `pio test -e native` per-plan, not per-phase — the failure surfaces in ~5 s. And assert the **count** (141 cases / 17 suites), not just "green": a suite that stops being collected also reports green.

### A-5. The AVR "must not grow" constraint is **nominally breached — a small breach on the two roomiest targets, needing an explicit operator-visible decision.**

Both researchers measured the same direction; ARCHITECTURE measured one target more.

| Target | `beta` | Merged | Δ | Headroom after | Provenance |
|---|---|---|---|---|---|
| leonardo flash | 26072 | 26016 | **−56 B** | 2656 B | [MEASURED-A] + [MEASURED-P], identical |
| uno flash | 23932 | 23954 | **+22 B** | 8302 B | [MEASURED-A] + [MEASURED-P], identical |
| uno328pb flash | 23976 | 24004 | **+28 B** | 8380 B | **[MEASURED-A] only** — PITFALLS did not build this env |
| uno / leonardo RAM | 1573 / 2014 | unchanged | 0 | 475 / 546 B | [MEASURED-A] + [MEASURED-P] |

**Ruling: no conflict — PITFALLS simply measured two of three AVR envs; ARCHITECTURE's +28 B on ATmega328PB is the sole source for that figure and should be re-measured in the integration phase to make it two-source.** Mechanism: the macro→`static inline` conversion lands on Leonardo and native but not Uno-class, since `SERIAL_ON_IO` is set for `uno`/`uno328pb` only.

State it honestly: **the constraint as written ("the AVR flash budget must not grow") is violated by +22 B and +28 B on the two targets with ~8 KB of headroom, while the *binding* target improves by 56 B.** Do **not** write an acceptance criterion the measured tree already fails, and do not silently pass it either. Restate as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B, recorded"* — **as an explicit, operator-visible decision.** Note separately that **size is not behaviour**: the golden register traces are what prove the macro→inline conversion behaviour-identical, per-array for `_shared/sdp_expected.h` (the whole-file blob-SHA shorthand was retired in Phase 119).

### A-6. `platform/py32f071/PORTING.md` **does not exist on the live branch** — so flash-persistent config is DESIGN work, not integration.

Found by **STACK** (H-8) and **ARCHITECTURE** (X-2), independently.

- `git ls-tree` finds it **only** on the two **CLOSED** branches — `feature/py32f071-toolchain` (PR #46) and `feature/py32f071-full-support` (PR #47) — identical blob **`4b1a441`**, 195 lines. It is absent from `agent/py32f071-toolchain` and `feature/py32f071-release-assets`, and `platform/py32f071/README.md` does not describe the scheme either. [READ, both researchers]
- **Both PROJECT.md and STATE.md cite it** as the specification for *"CRC-validated dual-slot flash records per `platform/py32f071/PORTING.md`."*
- **It is also partly superseded:** its prescribed module layout (`py32f071_board.h`, `gpio.cpp`, `board.cpp`, `adc.cpp`, `dac.cpp`, `storage.cpp`) **does not match what PR #48 actually built** (`py32f071_rurp_shield.cpp`, `timing.cpp`, `usb_cdc.c`, `config.cpp`, `platform_compat.cpp`, `main.cpp`), and 4 of its 15 acceptance items are out of scope here.
- **Scope consequence — state it plainly:** the flash-config requirement currently has **no in-tree design**. Either author the in-scope design **inside this milestone (real work, not integration)** or scope the requirement down. **Do not let a planning document's citation stand in for a spec that does not exist.** Recommended: vendor the in-scope subset of blob `4b1a441` onto the milestone branch so the contract is not stranded on a closed PR, and cite the closed branch as its home.
- **A hard prerequisite nobody can guess:** the **PY32F071xB flash page/erase-unit size is stated nowhere under `platform/py32f071/`** [READ, grep: no `FLASH_PAGE`/`SECTOR`/`erase` token]. Two slots must sit in **different erase units**. Read it from the Puya reference manual before editing the linker script — and note `PY32F071xB_FLASH.ld:5` currently claims the **entire** 128 K with **no reservation for config slots and none for a bootloader**, while `py32_dfu.py` hardcodes `FLASH_BASE 0x08000000` / `FLASH_SIZE 128 KiB`, so host and linker must move together.

### A-7. Gates failing open: **one finding, two angles. This is the defect that matters most, because moving firmware files is the milestone's premise.**

- **PITFALLS reproduced it.** The host suite detects "firmware absent" via a **single-file existence proxy**: `_FW_ABSENT = not _EEPROM_28C_CPP.exists()` (`tests/test_sdp_table_parity.py:54`), with the identical idiom in **six** modules keyed on `firestarter.h`, `eeprom_28c.cpp`, `validation_matrix.h`, `sdp_bus_config.h` and `PROTOCOLS.md`. Experiment: with a merged firmware sibling present, `mv src/proms/eeprom_28c.cpp src/proms/eeprom_28c_renamed.cpp` flipped **5 gate legs from PASS to SKIP**, with the **false** reason *"firestarter firmware checkout absent"*, at **exit 0**. Whole-suite census: **33 skips with no sibling repo (30 firmware-keyed), 3 with the merged sibling.** [MEASURED-P]
- **ARCHITECTURE hit the same defect from the verification side:** run from a scratch path, **11 firmware-scanning host tests SKIP** — a false green — and only in a directory literally named `firestarter_app` with a **merged** `firestarter` sibling do all nine cross-repo gates actually execute. In that layout the suite is fully green (0 failures, 29 snapshots) with 7/7 `tools/check_*`+`diff_db` gates passing. [MEASURED-A]
- **Ruling: one synthesized finding.** *"Repo absent"* and *"file moved"* are indistinguishable under a file-existence proxy, and the guard was written for a different problem (`beta-release.yml` checking out the app alone, `81fa53c`). This project has been bitten by the **fail-closed** form four times in Phase 117 and again in Phase 118 — CI caught those. **This form is fail-open and has never been triggered, because no prior milestone moved firmware files at scale.** Mitigations, all mechanical: (a) **split the proxy** — key "repo absent" on `../firestarter/.git`, and make "repo present but scan target missing" a **hard failure** (~30 lines, one shared helper, seven call sites — the single highest-value mechanical change available to v1.23); (b) **assert the skip census** — fail if any skip reason contains "firmware … absent" while `../firestarter/.git` exists, shipped with a planted-violation fixture; (c) **verify only in the sibling layout**, and treat `test_gen_validation_header.py::test_validate_spec_called_before_emission` and `test_sdp_bus_config_drift.py::test_bad_pinout_fails_closed_and_writes_nothing` as **known path artifacts** — PROVEN identical on a pristine `beta` worktree at the same scratch path, so do not chase them; (d) **re-run the nine-row sweep at every wave**, the Phase-118 discipline that produced zero host CI surprises.

---

## Corrections to the Planning Record

All PROVEN against live trees on 2026-07-30. **This numbered list is to be applied to both PROJECT.md and STATE.md** — both were written before this research.

| # | Recorded claim | Corrected | Found by |
|---|---|---|---|
| **R-1** | `agent/portability-macros` provides `include/rurp_platform.h`, normalized platform IDs, `rurp_millis()`/`rurp_delay_ms()`/`rurp_delay_us()` so common code never calls Arduino timing APIs, board-local pin maps behind logical identifiers, and capability macros | It is **4 files / 123 insertions**: `rurp_platform_compat.h`, `include/avr/pgmspace.h`, plus include-swaps + macro→inline in `rurp_serial_utils.h` / `rurp_shield.h`. **`rurp_platform.h` is on the py32 branch** (51 lines). The timing macros exist but have **zero shared-code call sites**; the mechanism is the fake `Arduino.h` shim. **No pin-map work** — `rurp_pinout.h` is untouched by every branch. **No capability macros.** Describe it as a **compat-shim layer, not a timing abstraction** | STACK C-1, ARCHITECTURE X-1, PITFALLS 11 |
| **R-2** | `DATA_BUFFER_SIZE = 1024` on py32 | **512** (`CMakeLists.txt:113`), on **both** py32 branches. This is **wire-visible**: v1.10 CAP-01 advertises it, so the host chunks to 510 not 1022. Any "py32 matches Leonardo throughput" expectation is wrong, and a later bump is a behaviour change, not a constant tweak. (The 1024 likely came from the two USB CDC ring buffers, which *are* 1024 each) | STACK C-2, ARCHITECTURE X-3, PITFALLS baseline |
| **R-3** | Branches are 27 commits behind `beta` (branch-state note) | **72 behind**, every py32 branch. PROJECT.md's 72 is right; the note is stale by 45 commits | STACK C-3, ARCHITECTURE X-5, PITFALLS |
| **R-4** | The 72 commits "include the whole v1.22 milestone" | Understated. Merge base `a1953c2` is **2026-06-18**, so the beta side spans **v1.14 → v1.22** — eight milestones, including v1.19's Phase-104 renames (the cause of A-2) and v1.20's `mem_type`-axis removal | ARCHITECTURE X-6 |
| **R-5** | Host branch has 44 unit tests | **58 passing** (46 `def test_` functions) — and they pass with `usb` not importable | STACK C-4, MEASURED-S |
| **R-6** | `cli_handlers.py:819` holds the `click.Choice` board list | **`cli_handlers.py:930`** on `beta`. (`firmware.py:113/:155/:237/:336/:420/:640` all verified **correct**) | ARCHITECTURE X-7 |
| **R-7** | The `.hex` extension is hardcoded at `firmware.py:155/:237/:336` and needs work; open seed question *"does the host asset pattern need `.bin` alongside `.hex`?"* | **Closed on the branch.** `asset_candidates()` + `_pick_asset()`, all four call sites. Host already accepts both; only *publication* is a choice, and the v1.23 answer is `.hex` only. **Do not re-plan** | FEATURES E-14, STACK C-5, ARCHITECTURE seam 2 |
| **R-8** | *"CRC-validated dual-slot flash records per `platform/py32f071/PORTING.md`"* | **That file does not exist on the live branch** — only on closed PRs #46/#47, blob `4b1a441`. See A-6: this is design work, and #48 did not build to that document's module layout | STACK H-8, ARCHITECTURE X-2 |
| **R-9** | Build order: land `portability-macros` first, then the py32 stack | **Wrong and measured wrong** — that intermediate state ERRORs all 17 native suites. They land **atomically**. See A-4 | PITFALLS 1, ARCHITECTURE |
| **R-10** | Leonardo headroom ≈ 2992 B | **2600 B** on `beta`, **2656 B** merged. See A-1 | PITFALLS, ARCHITECTURE X-4 |
| **R-11** | Host branch head `311eacf` (branch-state note) | **`4ee64a1`** — 3 commits ahead of merge base `1bb5599`, 79 behind `beta` | ARCHITECTURE X-8 |
| **R-12** | *(new)* Leonardo RAM was never recorded at all | **2014 / 2560 B, 546 B free (78.7 %)**. Record RAM alongside flash from now on — a `PROGMEM`→RAM regression is invisible in a flash number | PITFALLS |
| **R-13** | *(new)* PY32 SRAM sometimes assumed 20 K | **16 K** (`PY32F071xB_FLASH.ld:6`) | PITFALLS |
| **R-14** | *(new)* `feature/py32f071-release-assets` implied to be a third stack to reconcile | It is exactly `agent/py32f071-toolchain` **plus one commit** (`ad47c3b`). The asset-naming work is one cherry-pick | STACK C-6 |
| **R-15** | *(new)* `py32f071.yml` implied to cover the ARM target | **No `push` trigger** — after the merge, nothing builds ARM on `beta`. Plus the ARM target is **unbuildable in this devcontainer** (no `arm-none-eabi-gcc`, `cmake`, `ninja`) | all three |
| **R-16** | *(new)* `platform/py32f071/README.md` §"Release integration" advice | Its prose correctly argues for a **glob** (action-gh-release *warns* on an unmatched glob, *fails* on a missing literal) and then supplies the **literal** path. Also `beta-build.yml:92` is `files: .pio/build/**/firestarter_*.hex` — the CMake image at `build/py32f071/` is **outside that glob** | ARCHITECTURE C-4/§6.3, STACK §4, PITFALLS 5 |
| **R-17** | *(new)* `platform/py32f071/cmake/write_checksums.cmake` | **Orphaned** — zero references anywhere after `ad47c3b`. Delete or re-wire; do not leave dead build tooling in a first landing | STACK H-7 |
| **R-18** | *(new)* `DEV_TOOLS` absent on the ARM target reads as a decision | It is currently an **accident** of the CMake defines. `CMD_DEV_*` and `CMD_HW_VERSION` return `MSG_ERR_UNKNOWN_CMD` on py32. It aligns with the 999.15/gh#8 dev-tools channel split — make it explicit and commented | STACK H-3, ARCHITECTURE C-6 |

---

## Hollow-Verification Risks, Ranked

The standing discipline is that **every checker ships with a pytest proving it fails on a committed planted violation** (v1.21: 9 legs; v1.22: 7 legs). Ranked by how much false confidence each would buy:

1. **The provisional pin map has no mechanical enforcement — and its one guard is structurally dead.** `RURP_PY32F071_PINMAP_CONFIGURED` is `#define`d `1` two lines above `#if !RURP_PY32F071_PINMAP_CONFIGURED → #error`, so the guard **cannot fire**. `RURP_PY32F071_PINMAP_PROVISIONAL` appears at its own definition and in one README sentence — **zero code consumers** — while `py32f071_rurp_shield.cpp` drives `..._DATA_PORT`, `..._CE_PIN`, `..._OE_PIN` and reads `ADC_CHANNEL_4` live. This is a hollow gate **inside the branch being landed**, exactly the shape of v1.12's GATE-03 debt. Recovery if it is ever trusted near a PROM: **none — prevention only.**
   **The mechanical hook should be: while `RURP_PY32F071_PINMAP_PROVISIONAL` is 1, the target refuses every operation that can energise a PROM** — a fail-closed refusal at the command-admission layer (or in `configure_memory`'s programming paths), asserted by a native test on every compiled board, mirroring the shape `rurp_set_vpp_target_mv()` already uses to return `MANUAL_ADJUSTMENT_REQUIRED`. Plus: restructure so `CONFIGURED` is **required from the build system**, not defined in the same file, and ship a planted-violation proof that the `#error` can now fail. Plus a generalisable ~20-line **orphan-provisional-macro checker** asserting every `RURP_*_PROVISIONAL`-style flag has a consumer outside its own definition.
2. **The FW-absent proxy (A-7)** — a green suite that silently stopped checking. Recovery cost is LOW to find *once the split-proxy checker exists*, **HIGH if discovered after close**, because every artifact citing a green gate must be re-audited.
3. **The CMake manifest (A-2)** — missing files fail loudly at configure; **missing *additions* fail silently**, and the ARM target simply compiles a different program.
4. **No bus-trace oracle on ARM.** `HOST_STUBS_RECORD_BUS` (v1.22 Phase 116) records `rurp_write_to_register` calls and runs on **`native`, not ARM**. The ARM target could diverge from the AVR emitted sequences with **no oracle able to notice** [PREDICTED]. Do not schedule work against it this milestone; record it as an explicit non-claim.
5. **Weak/no-op stubs that link.** PR #47's `src/usb.c` is a ring buffer over `__attribute__((weak))` **no-op** hooks — it links, and a flashed board is **silent on USB**, while reading as the most finished branch. A ~20-line checker asserting no weak no-op body survives under `platform/py32f071/src/**` would make that trap unshippable. **Start from PR #48. Never #47.**
6. **Warning noise as a masking agent** — 138 vs 80 warnings per suite; gate at `grep -c redefined` = 0.
7. **Host DFU opcode literals are a source==source oracle.** `tests/test_py32_dfu.py` imports `DFUSE_ERASE_PAGE` / `DFUSE_SET_ADDRESS` / `FLASH_BASE` from the module and asserts against them — exactly the class v1.13 killed. The *sequencing* assertions are genuinely independent and good. Anchor the literals to UM1504 / DFU 1.1 in one test.
8. **The real pyusb API surface is never exercised anywhere** — not in CI (`pip install -e .[test]`, never `.[test,py32]`), not locally. `usb.core.find`, `ctrl_transfer` argument order, `extra_descriptors` availability are all unverified, and the `PyusbMissingError` branch that every plain-install user hits carries `# pragma: no cover` while being a 3-line monkeypatch to test.
9. **Assert counts, not statuses** — `141` native cases / 17 suites, and the app suite's collected total. A suite that stops being collected reports green.

---

## What Cannot Be Validated — carry this table forward verbatim

FEATURES' exhaustive silicon-blocked set. **Permitted ceiling everywhere below: builds clean, suites pass, DFU sequence exercised against descriptors and mocks.**

| Item | Cannot be validated | Why it matters |
|---|---|---|
| USB VID/PID of the Puya bootloader | `0x0448` is a **device ID** in UM1504's bootloader-parameter table, not a confirmed USB PID | Discovery is class-based *because* of this. A wrong default filter fails to find the real board |
| DfuSe vs plain DFU 1.1 dialect | No public evidence dfu-util has ever driven a PY32; Puya ships `PY32DfuTool` (Windows) and `PY32IspTool` | The whole `is_dfuse` fork is untested against reality; **one of the two branches has never been the right one** |
| Sector/erase geometry | Fallback is a uniform 2048 B grid nobody confirmed; the page size is stated nowhere in-tree | Wrong erase granularity = a partially-erased image |
| Flash-envelope bounds | `0x08000000` + 128 KiB come from the datasheet and linker script, never observed | The guard's bounds are **inherited, not measured** |
| Plain-DFU load address | The code's own warning admits it cannot know | A silent wrong-address write is the worst failure mode in the set |
| Leave / manifest starting the application | Untested | "Success" today means "the transfer completed", nothing more |
| `DFU_UPLOAD` support (`bitCanUpload`) | Unknown; `attributes` is captured at `py32_dfu.py:348` and never consulted | Argues for a fail-soft that skips readback when the device says it cannot upload |
| The `SYSCFG MEM_MODE` jump (N-04) | Documented for STM32F0/PY32F0 generally; **reported to "have no effect"** on some F0 parts; F0/L0 empty-check can defeat it | The reason to **defer** N-04, not merely descope it |
| Crystal-less HSI USB enumeration | Puya's own reference does it and CTC exists as a fallback — neither is proof | Cheap hedge now: keep a **depopulated HSE footprint** on the first schematic |
| USB ISR latency vs PROM pulse windows | `py32_usb_write` spins with IRQs toggled (`__disable_irq()` around the transmit kick), and `rurp_delay_us` busy-polls TIM3 while USB runs. v1.22 measured 572 µs against a 600 µs `t_WC` — **4.7 % headroom** | The phase landing this must state that USB flushes never occur inside a program-pulse window, or prove it. Otherwise an explicit non-claim |
| ARM flash / RAM figures | **`arm-none-eabi-gcc` and `cmake` are absent from this devcontainer** — the ARM image cannot be sized locally, by anyone, today | **Name the measurement seam:** CI already runs `arm-none-eabi-size`, but only into the job log — no artifact, no threshold, no gate. Make the size line a **checked-in baseline with a RAM ceiling**, and require a **workflow run URL + commit SHA** for every ARM claim. A local `pio` run is not evidence about ARM. RAM accounted so far is **~4.2–4.4 KiB of 16 KiB [PREDICTED]**, before `firestarter_handle_t`, the jsmn token array and HAL handles |
| **End-to-end install** | Never claim it | — |
| **The pin map** | PB0–PB7 data / PA0–PA5 control / VPP on PA4-ADC-ch4 is a placeholder that **describes no existing PCB** (PA4 chosen only because it matches the Puya ADC example; user button not fitted) | **A successful firmware install proves nothing about the programmer working.** Keep these two claims strictly separate in every requirement |
| VPP measurement | `rurp_read_voltage_mv()` reads an uncalibrated ADC on a provisional pin. Plausible integers are not evidence | No VPP claim without a DMM; there is no DMM path without a PCB. State **"not measured"** |

---

## Implications for Roadmap

### Reconciled phase spine — 8 phases, 123–130

PITFALLS proposed 7 (123–129) with **gates authored in 123 before any firmware moves**. ARCHITECTURE proposed a spine where **123 is the merge itself**, with VPP seam (124) and flash config (125) split and serialised, `{124,125} ∥ {126}` genuinely parallel, and 125 flagged highest-risk. **Where they disagreed, and how it is resolved:**

- **Does a gate phase precede the merge?** PITFALLS: yes, emphatically (*"the gates and baselines must exist before the merge, because their whole value is detecting what the merge changes"*). ARCHITECTURE: folds the source-list gate into the merge phase, calling it *convenience*. **Resolved in PITFALLS' favour**, and the evidence is decisive: A-7's fail-open proxy and A-4's ERRORed baseline are both things a *pre-existing* gate detects and a *co-landed* gate cannot. ARCHITECTURE itself concedes writing the gate early *"is what makes C-1 provably non-recurring."* → **new Phase 123 is gates + baselines, no firmware code moves.** This shifts everything down one and makes the spine 8 phases.
- **Are VPP seam and flash config one phase or two?** PITFALLS combines them (its 125); ARCHITECTURE splits and serialises them (124 → 125) with a load-bearing reason: **both edit `src/rurp_config_utils.cpp`**, and landing the VPP seam first *with a gate proving that file untouched* keeps the "no `CONFIG_VERSION` bump" non-claim clean and attributable. **Resolved in ARCHITECTURE's favour** — attributability of an AVR-shared-file regression outweighs one fewer phase.
- **Everything else the two agree on**, including: 123 before the merge, the merge atomic, host independent of the firmware seams, release fold after the merge and after the host, PCB record after the real flash map exists, close last with its push as its own gate.

---

#### Phase 123 — Non-regression baselines & gate hardening *(no firmware code moves)*
**Rationale:** Every gate authored here detects something a later phase changes; authored later, it can only bless what already happened. A-4 and A-7 are both invisible without a pre-recorded baseline.
**Delivers:** Recorded AVR flash **and RAM** baselines (Leonardo 26072/2014 → 2600 B/546 B free; Uno 23932/1573; uno328pb 23976) and the native count (**141 cases / 17 suites**); **split the FW-absent proxy** (repo presence via `../firestarter/.git`; missing scan target = hard failure; one helper, seven call sites) + a **skip-census** assertion; the **CMake manifest-drift gate** with a commented `PY32_EXCLUDED` allow-list; the **orphan-provisional-macro** checker; the **warning-count** gate; **`check_permitted_claims.py`** copied from `.planning/phases/122-close-…/` with a v1.23 phrase table (`runs on (a |the )?PY32`, `works end[- ]to[- ]end`, `silicon[- ]verified`, unqualified `bench[- ]validated`, `flashed (a|the) PY32`, `hardware[- ]validated`, `closed[- ]loop VPP (works|verified)`, `pin map (is )?(correct|verified|validated)`; required caveat *"no PY32F071 hardware exists"*). Every checker with a committed planted-violation fixture + a pytest proving non-zero exit.
**Avoids:** Pitfalls 2, 3, 8, 9 · **Corrects:** R-1, R-2, R-10, R-12, R-13 in the requirements before they become criteria nobody can satisfy.
**Ordering:** **LOAD-BEARING first.** Non-negotiable.

#### Phase 124 — Firmware integration merge *(atomic)*
**Rationale:** A-4 — the two branches are one landing. A-2 — the tree is broken until C-1 is fixed, and A-3/R-15 mean nothing would tell you.
**Delivers:** `--no-ff` merge of `agent/portability-macros` **and** `feature/py32f071-release-assets` as one atomic landing with `780a3fb` included; the **C-1 two-line fix** (`flash_type_3/4` → `flash_nor_unlock`/`flash_5v_page`); `push: branches: [beta]` on `py32f071.yml`; the **provisional-pinmap refusal** + a `#error` guard that can actually fire; eliminate the 58 macro-redefinition warnings; delete/re-wire `write_checksums.cmake` (R-17); make `DEV_TOOLS`-off an explicit commented decision (R-18); fix `FLASH_ACR_LATENCY_1` → `FLASH_LATENCY_1`.
**Verify:** Leonardo/uno/uno328pb flash **and RAM** recorded against the 123 baseline; `pio test -e native` and `-e native_nodevtools` = **141 cases / 17 suites** (count, not status); golden traces byte-identical (per-array for `_shared/sdp_expected.h`); every manifest path resolves; ARM configures **and builds in CI, cited by run URL + SHA**; nine cross-repo gates *run* and pass in the **sibling layout**.
**Avoids:** Pitfalls 1, 3, 7, 9.
**Ordering:** **LOAD-BEARING after 123** (baselines) and **before everything else** (a configurable ARM target is a precondition).

#### Phase 125 — VPP control seam *(firmware, seam only)*
**Rationale:** Settled scope; must precede 126 so the "`rurp_config_utils.cpp` untouched" gate is attributable.
**Delivers:** **Hand-authored** `include/rurp_vpp.h` (~40 lines: `RURP_HAS_VPP_DAC`/`RURP_VPP_DAC_BITS` + consistency `#error`, `rurp_vpp_control_mode_t`, `rurp_vpp_result_t`, 3 functions) + ~15-line `src/rurp_vpp.cpp`; one `#include` line in `rurp_shield.h`; `RURP_VPP_CONTROL_MANUAL` on all four boards; `rurp_set_vpp_target_mv()` → `MANUAL_ADJUSTMENT_REQUIRED` everywhere. **Cherry-pick nothing from PR #45** — `05f4a77` is the sole conflicting file in the inventory and smuggles a `CONFIG_VERSION` bump plus deletion of Phase-33/34 provenance comments; `9134f2a` reroutes AVR measurement and adds 16× oversampling.
**Verify:** AVR flash delta **0 B expected with `--gc-sections`/no callers — measured, not asserted**; native test asserting the refusal on every board macro-set; diff gate proving `src/boards/rurp_common.cpp`, `include/rurp_types.h`, `src/rurp_config_utils.cpp` untouched and `CONFIG_VERSION` still `"VER06"`.
**Ordering:** **LOAD-BEARING after 124** (merged `rurp_shield.h`) and **before 126** (attribution).

#### Phase 126 — Flash-persistent config via a storage-backend seam ⚠ **highest-risk phase**
**Rationale:** The only phase editing a file compiled into **all three AVR targets**. And per A-6 this is partly **design work** — decide before planning whether to author the in-scope design or scope down.
**Delivers:** `include/rurp_config_storage.h` (two functions); `src/rurp_config_utils.cpp` refactored to policy-only; `src/boards/rurp_config_storage_eeprom.cpp` as a **pure move**; `platform/py32f071/src/config_storage_flash.cpp` (dual-slot CRC32, `StoredConfiguration` wrapper embedding the struct verbatim); delete `platform/py32f071/src/config.cpp` and its policy drift; **reserve two config pages in `PY32F071xB_FLASH.ld`** with linker symbols — **after reading the real page size from the Puya reference manual**; native fake backend + 7 tests (blank, newest-wins, CRC rejection, both-corrupt, interrupted write, slot alternation, **AVR non-regression**).
**Verify:** the AVR regression test asserts `EEPROM.get/put` at offset **48** with `sizeof(rurp_configuration_t)`, byte-identical to pre-refactor — proven the Phase-117 way, with an **empty `git diff` on the test file**; schema and `CONFIG_VERSION` unchanged; Leonardo delta recorded against 2600 B.
**Ordering:** **LOAD-BEARING after 125**; **internal order load-bearing** (AVR move, proven, *then* the ARM backend — otherwise a failing test cannot be attributed); the linker reservation lands **here**, because changing an address later is a flash-map migration.

#### Phase 127 — Host DFU installer *(different repo — parallelisable)*
**Rationale:** Merges clean today [MEASURED-A]; 21 of 21 host capabilities already exist.
**Delivers:** Merge `firestarter_app` `feature/py32f071-fw-install` @ `4ee64a1`; close the `--usb-id`-accepted-on-stable residual; add a **CI leg installing `.[test,py32]`** with one real-`usb`-import API-surface test; delete the `pragma: no cover` and test `PyusbMissingError`; anchor DFU opcode literals to UM1504/DFU 1.1; a test that `fw --list`/`--help` works with pyusb **absent**; raise the pyusb floor to `>=1.3.1,<2`; reconcile `doc/PY32F071-FIRMWARE-INSTALL.md` with the final flash map. **Optionally N-03** readback verification, failing soft on `bitCanUpload = 0`, claim-ceiling "asserted against a mock".
**Verify:** full suite in the **sibling layout**, 0 failures, collected count asserted; `ruff` + `ruff format --check` + mypy watermark + `--cov-fail-under=70` (the gates a `beta` push does **not** run); simulated **stable** `__version__` → no `py32f071` in `fw --help` and `--dfu-probe` rejected; pre-release → both present, remembering `_BOARD_CHOICES` is computed at **import time**. **Never run `fw --install` against attached hardware — it flashes the attached board and ignores `--board`.**
**Ordering:** **Genuinely parallel with {125, 126}** — different repo, disjoint files, no shared gate. **LOAD-BEARING before 128** (the host defines the asset-name contract).

#### Phase 128 — Release-asset fold into `beta-build.yml`
**Rationale:** N-01 is the only new work that makes any of the 21 capabilities reachable.
**Delivers:** Three ARM steps **after** `update_version.py` + auto-commit, in the **same job** as the AVR images; a second `files:` entry as a **glob** `build/py32f071/firestarter_*.hex` (R-16); `continue-on-error: true` on the ARM steps while unvalidated; an **"AVR assets present" assertion before `Release`**; a CI assertion that the emitted filename matches `asset_candidates("py32f071")[0]`; log the resolved SDK SHA.
**Verify:** `workflow_dispatch` produces `firestarter_py32f071.hex` as a **release asset**; three AVR assets still publish; and a **deliberately broken ARM build still publishes all three AVR `.hex` assets** — planted-violation discipline applied to CI.
**Ordering:** **LOAD-BEARING after 124** (don't fold a target that doesn't configure) **and after 127** (asset-name contract) **and the ARM build must run after the version bump** — an image from any other job carries a stale `VERSION`, which *is* the host's update decision.

#### Phase 129 — Flash-path decision + PCB requirements record *(docs)*
**Rationale:** The board is paper. Every item here is free now and unrecoverable after layout — and per FEATURES the **recovery ladder only exists if the PCB allows it**.
**Delivers:** ADR-style record: self-flash bootloader over CDC + COBS as intended **primary**, factory USB DFU as maintainer/manufacturing **recovery**, SWD as last resort (the three-tier ladder Katapult/Klipper validates); BOOT0/nBOOT1 strapping; SWD pads; contiguous 8-bit port; **depopulated HSE footprint**; a real USB VID/PID decision (`usb_cdc.c:20`'s `0x36B7`/`0xFFFF` is an undocumented placeholder — `pid.codes` under VID `0x1209` is the standard hobby route, and squatting is a liability the moment a board ships); the flash budget **as actually reserved in Phase 126** plus the bootloader region and its vector-relocation implication; the socket-empty safety line; an explicit statement that **landing DFU does not retire the seed**; and the ROADMAP prior-art corrections + slot renumber.
**Ordering:** **LOAD-BEARING after 126** (record the real map, not an intended one).

#### Phase 130 — Close: honesty ledger, claim gate, release decision
**Delivers:** Apply **all of R-1…R-18** to PROJECT.md, STATE.md, ROADMAP and the branch-state note; a v1.22-Phase-122-style claim ledger pairing each permitted wording with its explicit non-claim; the provisional pin map recorded as provisional in **every** artifact; the unvalidatable USB-ISR-vs-PROM-timing and no-ARM-bus-trace-oracle non-claims; the **A-5 flash-constraint decision, operator-visible**; a `13X-DECISION.md` release-decision artifact committed **before any push**.
**Ordering:** Last. **Its push is its own gate** — pushing `beta` auto-fires CI and cuts a beta (it has happened **twice**; the repos are at `3.0.0b14` with stray public `b12` prereleases), and **`--auto`/`--chain` auto-approves human-verify checkpoints** while `autonomous: false` does not protect an outward-facing gate. Read the cut tag from `gh release list`, never compute it. Verify **PyPI resolution directly** — 6 of 13 published app betas never reached PyPI (46 % miss, PAT lacking `workflow` scope suppresses `release.published`); manual `publish.yml` dispatch is **the norm, not a contingency**. Decide up front whether v1.23 accepts *"the merge IS the cut"* as v1.22 did.

### Ordering summary

```
123 (gates + baselines, no code moves)      ← LOAD-BEARING first
 └─► 124 (atomic merge + C-1 + push trigger + pinmap refusal)
      ├─► 125 (VPP seam)  ─►  126 (flash config ⚠) ─► 129 (PCB/flash-path record)
      └─► 127 (host DFU)  ─►  128 (release fold)
                                     └────────────► 130 (close; push is its own gate)
```

**Genuinely parallel:** {125, 126} ∥ {127}. **Not parallel:** 123→124 (gates must predate the moves they detect), 124 atomic (A-4), 125→126 (attribution of an AVR-shared-file regression), 127→128 (contract direction), 126→129 (real map), 128 after the version bump.

### Research Flags

**Needs `--research-phase` during planning:**
- **Phase 126 (flash config)** — the highest-risk phase, and the *only* one with genuinely undesigned content (A-6/R-8: `PORTING.md` is absent from the live branch and partly superseded; the PY32F071xB flash page size is stated nowhere in-tree and must be read from the Puya reference manual before the linker script is edited).
- **Phase 129 (PCB record)** — needs the USB VID/PID route, BOOT0/nBOOT1 strap details from UM1503/UM1504, and the bootloader-region/vector-relocation implications pinned down; all currently LOW-confidence web sourcing.

**Standard patterns — skip research:**
- **Phase 123** — the checker+planted-fixture pattern is house style with two working precedents in-tree (v1.21's 9 legs, v1.22's 7 legs and 4 fixtures), and `check_permitted_claims.py` is a copy-and-replace-the-phrase-table job.
- **Phase 124** — fully characterised by three independent researchers; the fix list is enumerated and the verification instruments already exist.
- **Phase 125** — ARCHITECTURE supplies the seam's literal source text and the ten-commit classification of PR #45.
- **Phase 127** — the branch is written, green, and read end-to-end; the remaining work is enumerated test/packaging additions.
- **Phase 128** — the fold is spelled out in `platform/py32f071/README.md` and the two corrections (glob, post-version-bump job) are pinned.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** on in-tree state and the SDK pin (read from `origin`, from `git ls-remote`, and per-path at commit `0ed2f4b`; host gates run in-container). **MEDIUM** on ecosystem facts (pyusb release data is PyPI-authoritative; Ubuntu/GitHub-runner versions are web-sourced). **LOW** on anything needing silicon | The 15-of-15 SDK path verification and the "pin = tag 1.1.1 = master HEAD" identity are the strongest items |
| Features | **MEDIUM** overall — **HIGH** on the 21-item in-repo inventory (direct source reads of the branch, not branch notes), **LOW–MEDIUM** on ecosystem convention (websearch only; no authoritative cross-project asset-naming source exists), **structurally unvalidatable** on silicon behaviour | The `.hex`-vs-`.bin` verdict rests on a *technical* argument verifiable in this repo's own code, not on convention. `probe-rs --verify` was left out rather than guessed |
| Architecture | **HIGH** on the merge surface, the HAL boundary and the host seams — the researcher **built and tested the merged tree** and ran a direct `avr-g++ -E -H` include trace. **MEDIUM** on the flash-config design (a proposal, not existing code). **LOW-by-construction** on silicon | Every PROVEN claim ships with a re-runnable command; §14 is a complete reproduction script |
| Pitfalls | **HIGH** — nearly everything was **reproduced**, not reasoned: the 141→0 native break, the rename→SKIP experiment with its exit code, the skip census (33 → 3), both zero-conflict merges, the warning delta, and three corrected baseline figures | Also the only researcher to price prevention as **[MECHANICAL]** vs **[JUDGEMENT]**, which is what makes its recommendations actionable |

**Overall confidence: HIGH for planning purposes** — the software state of this milestone is unusually well characterised, because three researchers measured rather than reasoned. **The confidence is asymmetric by design: it says nothing about PY32F071 silicon, and no amount of it ever will.**

### Gaps to Address

- **ARM flash/RAM are unmeasurable locally.** `arm-none-eabi-gcc`, `cmake` and `ninja` are absent from this devcontainer [MEASURED-P/S]. → **Name the seam, do not guess:** every ARM claim cites a **workflow run URL + commit SHA**; make CI's existing `arm-none-eabi-size` output a **checked-in baseline with a RAM ceiling** (today it scrolls past in a job log and nobody would notice a 3 KiB regression). Optionally add the toolchain to `.devcontainer/Dockerfile`; otherwise state in the phase artifact that ARM verification is **CI-only**.
- **ATmega328PB's +28 B is single-sourced** [MEASURED-A only]. → Re-measure in Phase 124 so the A-5 decision rests on two independent builds.
- **PY32F071xB flash page/erase-unit size is unknown and stated nowhere in-tree.** → Read the Puya reference manual in Phase 126 *before* editing the linker script. Do not guess: two slots in one erase unit destroys the atomicity property that is the entire point.
- **`PORTING.md` is stranded on closed PRs and partly superseded** (A-6). → Decide **before planning** Phase 126: author the in-scope design in-milestone, or scope the requirement down. Vendor the in-scope subset of blob `4b1a441` onto the milestone branch either way.
- **Whether the portability half changes AVR *behaviour*** (as opposed to size) — `−56/+22/+28 B` is a size result, not a behaviour result. → Golden register traces byte-identical, **per-array** for `_shared/sdp_expected.h`. v1.22 predicted a saving and measured **+204 B**: measure, never predict.
- **The timing-call-site rewrite is unmeasured and out of scope.** The ~12 direct `delay`/`millis` call sites in shared code are still there; the measured deltas **do not cover** rewriting them. → Explicitly **out of v1.23 scope** unless a phase owns its measurement.
- **The real pyusb API surface is exercised nowhere.** → The `.[test,py32]` CI leg in Phase 127 is the whole fix; it catches an API break in ~3 seconds.
- **No ARM bus-trace oracle exists.** → Record as an explicit non-claim; do not schedule work against it.
- **`gsd-tools query commit` silently switched checkouts on 2026-07-30** and reverted gitlinks. → `git rev-parse --abbrev-ref HEAD` after every call.

---

## Sources

### Primary (HIGH — measured or read in live trees, 2026-07-30)
- `/workspaces/firestarter` @ `beta` `5c9160a` · `/workspaces/firestarter_py32_ci` @ `feature/py32f071-release-assets` `ad47c3b` · `/workspaces/firestarter_app` @ `beta` `e7d3ee8` · `/workspaces/firestarter_app_py32` @ `feature/py32f071-fw-install` `4ee64a1`
- Origin refs read: `origin/agent/portability-macros` `52d6c1f` · `origin/agent/py32f071-toolchain` `e5abb51` · `origin/feature/common-vpp-calibration` `a47228d` (all ten commits individually) · `origin/feature/py32f071-toolchain` `2c2ed10` · `origin/feature/py32f071-full-support` `cc4a815` · `PORTING.md` blob `4b1a441`
- **Builds and runs executed during research:** `pio run -e leonardo -e uno -e uno328pb` on `beta` and on the merged tree · `pio test -e native` and `-e native_nodevtools` on baseline, on the portability-only intermediate (0/17 ERRORED), and on the merged tree (141/141) · `git merge-tree` + real `git merge` in scratch worktrees, both repos · the `mv src/proms/eeprom_28c.cpp` rename→SKIP experiment · whole-suite skip census (33 → 3) · `python -m pytest -q` on four different layouts · seven `tools/check_*` + `diff_db` gates · a direct `avr-g++ -E -H` include-path trace · `pytest tests/test_py32_dfu.py -q` (58 passed, pyusb absent) · `ruff check`, `ruff format --check`, `check_mypy_watermark.py` (1/35) · `which arm-none-eabi-gcc cmake ninja` (all absent)
- `git ls-remote https://github.com/OpenPuya/PY32F071_Firmware.git` and a sparse clone at `0ed2f4b` — pin identity, tree layout, per-path existence of all 15 CMake references, `py32f071_hal_flash.h:133-135`, the CDC reference `main.c`, the `usb_malloc` call-site grep
- <https://pypi.org/pypi/pyusb/json> — pyusb 1.3.1 / 2025-01-08 / `>=3.9.0` / BSD

### Secondary (MEDIUM)
- The project's own post-mortem record: `.planning/PROJECT.md` v1.22 Archive (all eight ⚠ CORRECTION blocks) · `.planning/RETROSPECTIVE.md` (hollow GATE-03; `0052c42`'s "22 tests PASS (zero-diff)"; cross-repo gate coupling) · `.planning/phases/122-close-…/{check_permitted_claims.py,test_check_permitted_claims.py,fixtures/}` · `.planning/notes/py32f071-port-branch-state.md` · `.planning/seeds/py32f071-no-external-tool-fw-install.md`
- Ubuntu/Launchpad `gcc-arm-none-eabi` `15:13.2.rel1-2` · GitHub runner-image migration changelogs · `carlosperate/arm-none-eabi-gcc-action` README · libusb Windows wiki + pyusb discussions (WinUSB/Zadig, `NoBackendError`)

### Tertiary (LOW — needs validation)
- Puya UM1503/UM1504 tool manuals and the PY32F002A reference manual — `0x0448` as a **device ID not a confirmed USB PID**; BOOT0 high + nBOOT1 = 1; `SYSCFG MEM_MODE` exists on PY32F0
- ST community threads — Cortex-M0 has no VTOR; `SYSCFG->CFGR1` **reported unreliable** on some F0 parts; F0/L0 empty-check
- Ecosystem survey: dfu-util manpage (two renderings; the *no-verify* finding cross-checked to MEDIUM) · esptool docs · Katapult README · Klipper Bootloader Entry (the DFU-mode output-energising hazard) · tinyuf2 · probe-rs/cargo-flash · QMK — **no cross-project release-asset naming standard was found**
- Upstream CherryUSB repo/docs — no `py32` port upstream; docs at ~1.6.1

**Honest gaps in the sourcing itself:** no PY32-specific DFU evidence exists in public sources at all (neither VID/PID nor dialect) — which is *why* `fw --dfu-probe` was built; `probe-rs --verify` could not be confirmed and was left out rather than guessed; the release-asset "convention" is websearch-only weak evidence.

---
*Research completed: 2026-07-30*
*Ready for roadmap: yes — and the validation ceiling at the top of this document is not negotiable downstream.*
