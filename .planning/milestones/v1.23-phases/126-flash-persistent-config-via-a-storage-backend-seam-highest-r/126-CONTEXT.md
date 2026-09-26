# Phase 126: Flash-Persistent Config via a Storage-Backend Seam - Context

**Gathered:** 2026-07-31
**Amended:** 2026-07-31 — research complete (`126-RESEARCH.md`, commit `2fb4dfa`); two escalated
decisions answered by the operator and locked as **D-18** (flash shrink quantum = Sector 15 whole)
and **D-19** (`CONFIG_MAGIC` = `0x52555250`). Research also lodges 14 corrections C-1…C-14, three of
which amend locked decisions — **D-08** (three edits → four: `py32f071_hal_flash.c` is absent from
`CMakeLists.txt`), **D-10/D-11** (refined by D-18), **D-16** (its "program the header/CRC word LAST"
step is **not implementable** on this part — one 256 B program primitive, no partial-word write).
**Read `126-RESEARCH.md` before planning; where it and this file disagree, RESEARCH.md wins on
verified facts.**
**Status:** Ready for planning — research done; run `/gsd-plan-phase 126`

> **⚠ This phase is flagged ⚠ highest-risk in the ROADMAP for two independent reasons.**
> It is the **only** phase in v1.23 that edits a file compiled into **all three AVR targets**
> (`src/rurp_config_utils.cpp`), and per research A-6/R-8 it is **partly design work** — the
> document PROJECT.md and STATE.md both cite as its specification
> (`platform/py32f071/PORTING.md`) **does not exist on the live branch**. It survives only as
> blob `4b1a441` on the two CLOSED PRs #46/#47, and its prescribed module layout does **not**
> match what PR #48 actually built.
>
> **Verified during this discussion:** blob `4b1a441` **is** readable from the local
> `firestarter` clone (`git cat-file -p 4b1a441`, 195 lines). Its §"Configuration storage" is
> the in-scope subset and is the part PR #48 did **not** supersede. Its module names
> (`storage.cpp`, `gpio.cpp`, `board.cpp`, `adc.cpp`, `dac.cpp`, `py32f071_board.h`,
> `py32f071_pins.h`) are all superseded, as are its DAC-VPP and calibration sections
> (out of scope — FUT-VPP / FUT-CAL).

<domain>
## Phase Boundary

This phase splits configuration persistence into a **common policy layer plus a two-function
per-platform byte-blob backend**, gives the py32 a CRC-protected dual-slot flash backend, and
proves the AVR side moved without changing behaviour:

1. `src/rurp_config_utils.cpp` becomes policy-only; the AVR EEPROM code moves to its own TU as
   a **pure move** (CFG-03, CFG-04).
2. A new `include/rurp_config_storage.h` declares exactly two functions (CFG-03).
3. The py32 gains a dual-slot CRC32 flash backend covered by six distinctly named native
   tests: blank, newest-wins, CRC rejection, both-slots-corrupt, interrupted write, slot
   alternation (CFG-05).
4. `PY32F071xB_FLASH.ld` reserves two config pages in **different erase units**, exposed as
   linker symbols, after the real page/erase-unit size is **read from the Puya reference
   manual and recorded in a commit that precedes the linker edit** (CFG-02, CFG-06).
5. The in-scope design is **vendored** onto the milestone branch citing blob `4b1a441`, with
   every superseded part marked as superseded (CFG-01).
6. PR #48's `platform/py32f071/src/config.cpp` policy drift — including a `rurp_save_config()`
   that persists nothing — is **deleted**, and `rurp_configuration_t` + `CONFIG_VERSION
   "VER06"` are unchanged (CFG-07).

**Ordering inside the phase is load-bearing (ROADMAP, not preference):** the **AVR move lands
and is proven first**, *then* the ARM backend. Otherwise a failing test cannot be attributed.

**Explicitly NOT in this phase:**
- Any `rurp_configuration_t` field addition or `CONFIG_VERSION` bump (CFG-07 forbids it; it is
  also the exact thing Phase 125 VPP-03 pinned this file against).
- VPP calibration fields or the DAC closed loop — blob `4b1a441` prescribes both; both are
  out of scope (FUT-VPP / FUT-CAL, owned by the queued v1.26 calibration milestone).
- Reserving real flash for the self-flash bootloader (FUT-N05) — see D-13.
- Editing `firestarter_app` (Phase 127 owns the host half, and runs in **parallel** with this
  phase) — see D-12.
- Any claim about PY32F071 silicon. No PCB exists. ARM evidence is a **CI workflow run URL +
  head SHA**, never a local build (`arm-none-eabi-gcc`/`cmake`/`ninja` are absent here).
- Any push to `beta`, tag, release, or public comment (Phase 130).

</domain>

<decisions>
## Implementation Decisions

### Test venue, and what is actually under test (CFG-04, CFG-05; Criteria 3 & 4)

- **D-01:** The six dual-slot tests are **six pytest functions under `firestarter/tests/`,
  driving host `g++`** — Phase 125's shape (`test_vpp_seam_manual_on_every_board.py`,
  `test_pinmap_guard_fires.py`). **Not** a new PIO `test/native/` suite. The reason is
  arithmetic, not taste: a new Unity suite moves the pinned **141 cases / 17 suites** that
  BASE-01, MERGE-06 and every non-regression gate in this milestone cite, inside the one phase
  whose premise is that nothing else moved. **Checked facts:** the native envs'
  `build_src_filter` (`+<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
  +<operation_utils.cpp>`, `platformio.ini:163/252/290`) does **not** compile
  `src/rurp_config_utils.cpp` today, so no native count moves either way; and
  `tests/test_checker_convention.py`'s `FLOOR = 5` / `FIXTURE_FLOOR = 10` are scoped to
  `scripts/check_*.py`, so pytest files under `tests/` need **no** bump.
  **Accepted cost, state it:** this harness runs in **zero CI legs on this branch** —
  `py32f071.yml` has no pytest step — so it is discharged by an in-phase **local** run whose
  verbatim output lands in the evidence artifact. Do not claim CI coverage this branch lacks.
- **D-02:** The dual-slot algorithm is a **HAL-free core with injected flash primitives**
  (read / erase / program), compiled by **both** the py32 backend (real PY32 HAL primitives)
  and the host test (a RAM fake). **The tested code is the shipped code.** Rejected: an
  independent fake reimplementation in the test (proves a copy behaves — the hollow-gate shape
  Phases 118 and 124 each had to unwind); rejected: compiling the py32 `.cpp` against a
  hand-written stub `py32f071_hal_flash.h` (the stub becomes an unversioned mirror of a pinned
  FetchContent SDK the test cannot see).
- **D-03:** That core lives under **`platform/py32f071/src/`** (e.g.
  `config_storage_dualslot.cpp` + a local header), ARM-only by construction; the host test
  compiles it **by explicit path**, exactly as Phase 125's harness compiles `src/rurp_vpp.cpp`.
  Consequence, and it is the point: **zero new bytes reach any AVR build from the dual-slot
  code** — nothing to measure, nothing to defend against Leonardo's 2600 B headroom. Rejected:
  `src/` (would compile into all three AVR targets and require a three-target measurement in
  the phase that already has one); rejected: header-only in `include/` (invisible to
  `check_cmake_manifest.py`'s reverse check, which only sees `src/*.cpp`).
- **D-04:** Criterion 3's *"empty `git diff` on the test file itself"* is discharged as
  **two commits + a blob-SHA re-hash**: the AVR regression test is written against the
  **pre-refactor** `src/rurp_config_utils.cpp`, proven green, and its blob SHA recorded; the
  split lands in a later commit; the proof is that the recorded SHA **re-hashes identical**
  and the test is **still green**. A path-scoped `git diff` is **corroboration only** — Phase
  125's C-15 and `124-VERIFICATION.md`'s live finding both document that shape passing
  vacuously on a wrong path. Rejected: writing the test after the refactor (it could only
  prove the new code is self-consistent — it never observed the behaviour it claims to match).
- **D-05:** The CRC32 implementation is anchored to an **independent known-answer vector**
  written in the test file (the standard `CRC32("123456789") == 0xCBF43926`), **not** to the
  module under test. Same discipline HOST-06 applies to the DFU opcodes: an implementation
  asserted against itself proves nothing.

### The storage seam's contract (CFG-03, CFG-07)

- **D-06:** The seam is **two bool-returning functions** over a byte blob —
  `bool rurp_config_storage_load(void* blob, size_t len)` /
  `bool rurp_config_storage_save(const void* blob, size_t len)`. The py32 can then report
  *"no valid record"* **honestly** instead of returning zeroed bytes and relying on a
  version-string accident. **AVR behaviour is unchanged**: its implementation returns `true`
  unconditionally after `EEPROM.get`, and policy calls `rurp_validate_config` either way — the
  signature is new, the behaviour is byte-identical, which is what CFG-04 requires. Rejected:
  `void`/`void` (makes py32's "both slots blank" indistinguishable from "loaded zeros",
  handled only by the version-string accident — the same inference style as v1.22's inverted
  `0x5555` check); rejected: a richer status enum (invents vocabulary with no consumer, the
  pattern Phase 124 D-01 and Phase 125 D-09 both deleted).
- **D-07:** **All four public functions stay in the common policy layer** — `rurp_get_config`,
  `rurp_load_config`, `rurp_save_config`, `rurp_validate_config`, plus the `rurp_config`
  global — in `src/rurp_config_utils.cpp`. Only the two byte-blob calls cross the seam. This
  is CFG-03 verbatim, and it means PR #48's `platform/py32f071/src/config.cpp` is **deleted,
  not reconciled** (CFG-07). **Follow-on, recorded so it is not rediscovered mid-plan:**
  `#define CONFIG_START 48` is an *EEPROM address*, meaningless on py32, so it moves **into
  the AVR backend TU** — and CFG-04's regression test asserts it there.
- **D-08:** The AVR backend TU is **`src/boards/rurp_config_storage_eeprom.cpp`** with a new
  `# PY32_EXCLUDED:` line. That directory already hosts `uno_rurp_shield.cpp`,
  `leonardo_rurp_shield.cpp` and `rurp_common.cpp` — all three excluded for exactly this
  reason. The ARM manifest churn is therefore **three edits**: delete the existing
  `# PY32_EXCLUDED: src/rurp_config_utils.cpp` line (whose own comment already says *"THIS
  EXCLUSION WILL NEED REVISITING in Phase 126, it is not a permanent exclusion"*), **add**
  `src/rurp_config_utils.cpp` to `FIRESTARTER_COMMON_SOURCES`, and **add** the new exclusion
  for the EEPROM backend. `check_cmake_manifest.py`'s reverse check makes all three
  non-optional. Rejected: `#ifdef __AVR__` inside the policy file (makes "per-platform
  backend" true only because the file says so, and leaves py32 sharing a TU with `EEPROM.h`).
- **D-09:** **`include/rurp_shield.h` is NOT touched.** `include/rurp_config_storage.h` is
  included by exactly three TUs: the policy layer and the two backends. The four public config
  declarations stay where they already are (`rurp_shield.h:61`, `:150–152`). This is Phase
  125's C-1 lesson applied **before** the fact — one `#include` line in that header was
  measured to take `pio test -e native` from **141 cases / 141 succeeded to 17 suites / 0
  succeeded**, because it reaches 46 TUs including 14 native `host_stubs.cpp` files.

### The py32 flash map (CFG-06; Criterion 5)

- **D-10:** The two config pages sit at the **top of flash**, and `MEMORY`'s `FLASH` `LENGTH`
  **shrinks** by two erase units so `.text` physically cannot grow into them. Two independent
  reasons: the host's DFU erase is **payload-length-scoped**
  (`erase_addresses(layout, base, len(payload), …)`, `py32_dfu.py:750`), so an install whose
  image does not reach the top preserves config for free; and Phase 129's bootloader wants the
  **bottom** (vector table at `0x08000000` on a part with no VTOR), so top-of-flash config
  never has to move when that lands. Rejected: fixed addresses without shrinking `LENGTH`
  (overlap becomes a convention, and the first violation is a corrupted config at runtime on
  silicon nobody can debug).
- **D-11:** Expressed as a **second `MEMORY` region plus `PROVIDE` symbols** — a
  `CONFIG (r)` region alongside the shrunk `FLASH`, and `PROVIDE`d
  `__config_slot_a_start` / `__config_slot_b_start` / `__config_page_size` for the C code. The
  linker structurally enforces non-overlap and the *two-slots-in-different-erase-units*
  property is readable in one place. Rejected: compile-time `-D` defines from CMake
  (Criterion 5 says "linker symbols", and it splits the flash map across two files that can
  silently disagree).
- **D-12:** **This phase stays firmware-only.** Criterion 5's host consistency is discharged by
  (a) **recording the contract** — `FLASH_BASE` unchanged at `0x08000000`; `FLASH_SIZE` stays
  the **physical 128 KiB** because it is a *refusal envelope* (`py32_dfu.py:648`), not an erase
  bound, and shrinking it would make the host unable to flash the part it describes; plus the
  reserved config base as a named constant — and (b) a **firmware-side gate** asserting the
  reserved region parses out of the linker script and lies inside `0x08000000 + 128 KiB`.
  **Phase 127 owns the cross-repo half** and must satisfy it. Rejected: editing
  `firestarter_app` here (the two phases run in parallel, and `py32_dfu.py` exists only on the
  unmerged `feature/py32f071-fw-install` @ `4ee64a1` — this phase would be editing something
  Phase 127 then merges over).
  **Two checked facts for whoever writes Phase 127's half:** `firestarter_app/tests/scan_paths.py`'s
  `CROSS_REPO_TEST_PATHS` inventory contains **no** entry for the linker script or any config
  file today, so a host test that reads firmware source text **must add one**; and per BASE-02
  it must key repo-presence on `../firestarter/.git` via `tests/fw_presence.py`, never on a
  single scanned file (A-7: that idiom flips gate legs PASS→SKIP at exit 0 with a false
  "firmware absent" reason).
- **D-13:** A **zero-length `BOOTLOADER` region** at `0x08000000` lands as a **named seam**, so
  Phase 129's PCB-03 cites a real symbol rather than prose. **Operator decision, taken over the
  recommendation to omit it** — and it carries a mandatory honest comment, because the factual
  wrinkle was surfaced and accepted: a top-of-flash config region grows *downward* without
  moving anything, but a bottom-of-flash bootloader placeholder does **not** have that
  property. Giving it non-zero length later **moves the app's `ORIGIN`**, which is a flash-map
  **migration**, not a resize. The linker comment must say so plainly, and Phase 129 must
  record the bootloader budget as an *intent with that cost attached* — never as a number that
  looks already paid for. Rejected: picking a real size now (a guess about code that does not
  exist — precisely what CFG-02 exists to prevent for the config pages).
- **D-18:** The shrink quantum is **one whole 8 KiB sector (Sector 15), not two 256 B pages** —
  `FLASH` `LENGTH` goes `128K → 120K`, `CONFIG` is `0x0801E000` + `8K`, slots at `0x0801E000`
  (page 480) and `0x0801E100` (page 481). **Operator decision taken 2026-07-31 after research
  C-5, amending D-10's "shrinks by two erase units" wording.** This refines D-10's *quantum*
  only — top-of-flash placement, the shrunk `LENGTH`, the second `MEMORY` region and the
  `PROVIDE`d symbols (D-11) are all untouched. Reason it is not the literal 512 B: page erase
  *is* a first-class primitive here (`FLASH_TYPEERASE_PAGEERASE`, no sector alignment required),
  so 512 B does satisfy CFG-06's letter — but at `0x0801FE00` the app region ends at
  `0x0801FDFF`, **inside Sector 15**, so a sector-granular DFU erase of the app's last block is
  exactly the block holding config. D-10 was chosen to avoid needing that hazard; the
  sector-aligned reservation removes it rather than stating it. **Accepted cost:** 7680 B of the
  8192 B is slack (6.25% of flash) — claimable later by FUT-N05 or additional slots **without
  moving any address**. Rejected: 512 B at `0x0801FE00` (see above).

### Record format and recovery (CFG-01, CFG-05, CFG-07)

- **D-14:** On a virgin py32, **policy is unchanged**: `rurp_validate_config`'s existing
  write-back fires exactly as it does on AVR (`rurp_config_utils.cpp:38`), so defaults land in
  slot A during startup. One policy, one behaviour, both platforms — which is why CFG-03 keeps
  validate common. **Accepted cost, stated as a non-claim:** this means a flash erase+program
  during startup on first boot, stalling a Cortex-M0+; with no PCB that cost is
  **unmeasurable**, so it is recorded as *not measured*, never as *acceptable*. Rejected:
  RAM-only-until-explicit-save (forks `rurp_validate_config` by platform — the exact drift
  CFG-07 requires **deleted** from PR #48's `config.cpp` — and silently reverts to defaults
  every power cycle); rejected: deferring the flush until after USB enumerates (invents a
  lifecycle hook no other platform has, on hardware nobody can test against).
- **D-15:** **Blank and both-slots-corrupt both return `false`**, and policy cannot tell them
  apart — it applies defaults and persists, identically. One recovery path to test, not two.
  The two CFG-05 tests stay **separately named** (`blank` and `both-slots-corrupt`) and assert
  the same outcome from different inputs, which is what makes the equivalence a **proven
  claim** rather than an assumption. Rejected: distinguishing them for logging (needs the
  declined status enum plus a `messages.toml` codegen round-trip in the phase whose premise is
  that nothing else moved); rejected: treating two bad CRCs as fatal (would brick a unit on the
  first flash-wear event, and MERGE-04 already refuses every PROM-energising operation on py32).
- **D-16:** The write order the real backend commits to, and the one the fake models, is
  **erase the INACTIVE slot → program the record body → program the header/CRC word LAST**.
  The active slot is never touched until the new one is complete, so any interruption leaves
  the previous record intact and valid — the property blob `4b1a441` states verbatim (*"a
  failed or interrupted write must leave the previous record usable"*). The fake models
  interruption by aborting the primitive sequence **at each step boundary** and asserting
  `load()` still returns the **old** record. Rejected: torn-writes at arbitrary byte offsets,
  and random post-interrupt fill patterns — both assert robustness against a flash-controller
  behaviour nobody can observe on this part without silicon, so a pass would prove the model,
  not the part.
- **D-17:** `StoredConfiguration` is **vendored verbatim** from blob `4b1a441` —
  `magic / version(u16) / length(u16) / rurp_configuration_t / sequence(u32) / crc32` — with
  `rurp_configuration_t` embedded **byte-for-byte**, which is what makes CFG-07's
  *"schema unchanged"* structurally true rather than merely asserted. Every field earns its
  place: `magic` separates *never written* from *garbage*, `length` gives forward-compat if the
  schema ever grows, `sequence` drives newest-wins and slot alternation, `crc32` validates.
  **Record explicitly, so nobody later "reconciles" them:** the wrapper's `version` (u16) is
  **not** `CONFIG_VERSION` (the `char[6]` `"VER06"` inside `rurp_configuration_t`). Rejected:
  narrowing it (deviates from the one design this phase is chartered to vendor, and turns
  blank-rejection into a CRC-collision inference); rejected: redesigning it (CFG-01 asks for
  the closed-PR design vendored with superseded parts **marked**, and storage is precisely the
  part PR #48 did not supersede).
- **D-19:** `CONFIG_MAGIC` is **`0x52555250`** — the ASCII four-CC `'R','U','R','P'`, tying the
  record to the shield name already used throughout the firmware (`rurp_configuration_t`,
  `rurp_config_utils.cpp`), and readable as `RURP` in a hex dump. Defined **once** in D-03's
  HAL-free core local header. **Operator decision taken 2026-07-31 after research open-question
  3.** It must be recorded in `CONFIG-STORAGE.md` as a **this-milestone choice, explicitly NOT
  vendored** — blob `4b1a441` specifies the *field* but supplies no value, so calling the
  constant vendored would be exactly the overclaim Phase 122's C-5 had to correct. Satisfies the
  two hard constraints: it is neither `0xFFFFFFFF` (blank flash) nor `0x00000000`. Rejected:
  `'FSC1'` = `0x46534331` (the research recommendation — a format-version digit the `version`
  u16 in D-17 already carries, so the digit would be a second, competing version axis).

### Claude's Discretion

Locked defaults on areas the operator did not elect to discuss. Recorded so downstream agents
do not re-ask. Reverse any of them *before* planning if wrong — that is the cheap moment.

- **CRC32 implementation.** Bitwise reflected CRC-32 (poly `0xEDB88320`), **no lookup table**,
  living in D-03's HAL-free core TU. There is no CRC32 in the tree today — only the CRC8-CCITT
  `PROGMEM` table in `src/boards/rurp_serial_utils.cpp:378`, which is AVR-shaped and wrong to
  reuse. A 1 KiB table for an operation that runs at boot and on rare config writes is not
  worth the flash. Anchored by D-05's known-answer vector.
- **Sequence-number wraparound.** `uint32_t`, monotonically incremented, **no wraparound
  handling** — with a comment stating why: flash endurance (~10⁴ erase cycles) bounds the
  write count many orders of magnitude below 2³². Do not "complete" this with a rollover
  branch that can never execute and can never be tested.
- **Where CFG-01's vendored design lives.** A **focused** `firestarter/platform/py32f071/CONFIG-STORAGE.md`
  containing the in-scope §"Configuration storage" subset, citing blob `4b1a441` **by SHA** and
  naming its closed-PR home (`feature/py32f071-toolchain`/PR #46 and
  `feature/py32f071-full-support`/PR #47), with an explicit **SUPERSEDED** block mapping the
  document's module names (`storage.cpp`, `gpio.cpp`, `board.cpp`, `adc.cpp`, `dac.cpp`,
  `py32f071_board.h`, `py32f071_pins.h`) to what PR #48 actually built, and marking its DAC-VPP
  and calibration sections out of scope. **Not** a restoration of `PORTING.md` under its own
  name: the full 195-line document prescribes the DAC closed loop and the calibration model,
  both explicitly deferred (FUT-VPP / FUT-CAL), and 4 of its 15 acceptance items are out of
  scope — restoring it whole would re-strand out-of-scope prescriptions in-tree as if they were
  the contract.
- **How CFG-02 is recorded and its ordering proven.** A `## Flash geometry` section in that
  same doc, citing the Puya reference-manual document number, section and table, landing in a
  commit that **precedes** any commit touching `PY32F071xB_FLASH.ld` — proven with
  `git rev-list --is-ancestor` / `git log --oneline --` over the two paths, as an exit code.
- **Evidence artifact.** `126-NONREGRESSION.md`, in the same command / expected / observed row
  shape as `123-`, `124-` and `125-NONREGRESSION.md`, re-executed in the closing plan rather
  than copied from earlier plans' SUMMARY files.
- **The CFG-04 test's compile target must be stable across the refactor.** The test file
  cannot name only the pre-refactor TU, or D-04's empty-diff proof is unsatisfiable. Default:
  the test names **both** paths (`src/rurp_config_utils.cpp` and
  `src/boards/rurp_config_storage_eeprom.cpp`) from the start, compiles whichever exist, and
  carries a non-vacuity assertion (at least one path resolved **and** the fake `EEPROM.h`
  recorded at least one call). This is legitimate because D-08 locks the post-refactor path in
  advance. **Verify this survives contact** — if it cannot, the fallback is a single named,
  justified line change with both blob SHAs recorded, never a silent edit.
- Plan/wave decomposition and commit granularity, subject to the ROADMAP's forced internal
  ordering (AVR move proven **first**, ARM backend second) and to the push gate below.
- **Push gate.** Any `git push` / `gh workflow run` for ARM CI evidence is an outward-facing
  action requiring an **explicit operator gate at execute time, structurally separated from any
  autonomous flag** — `--auto`/`--chain` auto-approve human-verify checkpoints regardless of
  `autonomous: false`. Follow Plan 124-11 / 125-05 exactly: **no task runs the command**; the
  plan prints it and stops.

### Known risks the planner must budget for

- **The AVR flash constraint is the sharp edge of this phase.** The A-5 rule is *"Leonardo
  flash must not grow; Uno-class growth ≤ 64 B, recorded"*, live headroom is **2600 B**, and
  `scripts/check_size_baseline.py`'s `compare_avr()` is **strict equality and already armed**.
  Splitting one TU into two and adding a `bool` return can move bytes even under `-flto` +
  `--gc-sections`. **Measure early** — right after the AVR move, before the ARM work — so a
  delta is attributable. If it fires: measure, record the delta and its cause, then re-baseline
  `size_baseline.json` in **its own commit whose message states why the bytes are legitimate**
  (Plan 124-10's shape). **Never** widen a tolerance; never re-baseline silently.
  `size_baseline_base01.json` is Phase 124's frozen MERGE-05 reference and is **not** touched.
  Record **RAM alongside flash** for all three targets (R-12).
- **The nine cross-repo gates must be shown to RUN, not skip** (A-7) — this phase moves
  firmware files, which is exactly the condition the fail-open proxy was blind to.
- **Native counts must not move:** 141 cases / 17 suites on both pinned native envs.
- **Golden register traces byte-identical**, per-array for `_shared/sdp_expected.h`.

### Reviewed Todos

None folded — see `<deferred>`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone contract (read first)

- `.planning/REQUIREMENTS.md` — **CFG-01…CFG-07 verbatim (lines 62–68)**; §"Validation Ceiling"
  (lines 8–22) is the forbidden-claim list every artifact this phase writes is scanned against;
  §"Operator Decisions Locked at Definition" item **5** (line 186) is the standing instruction
  that the flash-config design is authored **in-milestone** by vendoring blob `4b1a441`;
  §"Out of Scope" (lines 136–151) and §"Future Requirements" FUT-N05 / FUT-VPP / FUT-CAL.
- `.planning/ROADMAP.md` §"Phase 126" (**lines 2197–2212**) — the five success criteria;
  §"v1.23 — PY32F071 Integration" (from line 1957) for the non-regression invariant, the
  structural-verification discipline (*assert counts, never "tests pass"*; *never prove
  untouched with a path-scoped `git diff`*), the **125 → 126** and **126 → 129** ordering
  rationale, and the release hazard.
- `.planning/PROJECT.md` §"Current Milestone: v1.23" (from line 36) — the research corrections
  and the software-only validation ceiling. Note its flash-config bullet (line 45) carries the
  ⚠ *"This is DESIGN work, not integration"* marker.
- `.planning/research/SUMMARY.md` — **§A-6 (lines 161–170)** is the load-bearing finding for
  this phase (`PORTING.md` absent from the live branch, partly superseded, and the flash
  page/erase-unit size stated nowhere in-tree); **§"Phase 126" (lines 277–281)** for the
  delivers/verify/ordering breakdown; **§"Gaps to Address"** (~line 346) for the *"two slots in
  one erase unit destroys the atomicity property that is the entire point"* warning; R-8, R-10
  (2600 B, not 2992 B), R-12 (record RAM), R-13 (SRAM is 16 K).

### Phase 123/124/125 output this phase consumes

- `.planning/phases/125-vpp-control-seam/125-CONTEXT.md` — **C-1** (the `rurp_shield.h`
  `#include` that collapsed native from 141/141 to 17 suites / 0) is the direct ancestor of
  D-09; **C-15** (blob-SHA re-hash primary, `git status --porcelain` corroboration only, never
  a path-scoped diff) is the ancestor of D-04; **D-15/D-16** (measure and record; re-baseline
  in its own justified commit, never widen a tolerance); **D-13/D-14** (the push gate shape).
- `.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md` — the row-shape template for
  `126-NONREGRESSION.md`, and the measured *0 B flash / 0 B RAM* precedent (`-flto` +
  `--gc-sections` is why).
- `.planning/phases/124-firmware-integration-merge/124-CONTEXT.md` — **D-01** (a declaration
  with no implementation and no consumer does not land) governs the Discretion defaults above;
  **D-14** (a guard that supplies the answer it tests is structurally dead).
- `.planning/phases/124-firmware-integration-merge/124-VERIFICATION.md` — the live finding on a
  `git diff --stat | grep` pipeline reported as "(empty)" when a trailer survived the grep.
  Read before writing any "untouched" proof.
- `.planning/phases/123-non-regression-baselines-gate-hardening/123-CONTEXT.md` — the
  `<specifics>` tie-breakers (*prefer the shape that produces an exit code*; *prefer the shape
  that cannot be silently forgotten*).

### Firmware sources this phase creates, edits, deletes or measures

- `firestarter/src/rurp_config_utils.cpp` — becomes **policy-only** (D-07). Currently 40 lines;
  `CONFIG_START 48` at `:11`, the write-back at `:38`.
- `firestarter/include/rurp_config_storage.h` — **NEW**, two declarations (D-06, D-09).
- `firestarter/src/boards/rurp_config_storage_eeprom.cpp` — **NEW**, pure move (D-08).
- `firestarter/platform/py32f071/src/config_storage_dualslot.cpp` (+ local header) — **NEW**,
  the HAL-free core (D-02, D-03).
- `firestarter/platform/py32f071/src/config_storage_flash.cpp` — **NEW**, the PY32 HAL
  primitives (D-02).
- `firestarter/platform/py32f071/src/config.cpp` — **DELETED** (CFG-07, D-07). 47 lines; its
  `rurp_save_config()` at `:38–47` assigns to a static and **persists nothing**, and its
  `rurp_validate_config` at `:15–30` is a *second*, drifted copy of the common policy
  (`memset` + `r2 == 0` check that the AVR version does not have).
- `firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` — `MEMORY` at `:3–7`
  (`FLASH 128K` / `RAM 16K`), edited by D-10/D-11/D-13. **CFG-02's page-size commit must
  precede any commit touching this file.**
- `firestarter/platform/py32f071/CMakeLists.txt` — the `# PY32_EXCLUDED:` block at **`:30–34`**
  (the `src/rurp_config_utils.cpp` line at `:34` carries its own *"WILL NEED REVISITING in
  Phase 126"* note) and `FIRESTARTER_COMMON_SOURCES` at **`:35–52`**. Three edits per D-08.
- `firestarter/include/rurp_types.h` — `rurp_configuration_t` at `:19–24`
  (`char version[6]; long r1; long r2; uint8_t hardware_revision;`). **Unchanged** (CFG-07).
- `firestarter/include/rurp_shield.h` — `CONFIG_VERSION "VER06"` at `:46`, `VALUE_R1`/`VALUE_R2`
  at `:49–50`, the four config declarations at `:61` and `:150–152`. **Not touched** (D-09).
- `firestarter/platformio.ini` — AVR envs at `:31–68` have **no** `build_src_filter` (so `src/`
  is compiled wholesale and D-08's new TU is picked up automatically); the three native envs'
  filters are at `:163/:252/:290`.
- `firestarter/scripts/check_cmake_manifest.py` — **read the module docstring in full**; its
  reverse check is what makes D-08's three edits non-optional, and it documents the mandatory
  `# PY32_EXCLUDED: <path> -- <reason>` format and the 0/1/2 exit taxonomy.
- `firestarter/scripts/check_size_baseline.py` + `firestarter/scripts/baseline/size_baseline.json`
  — strict-equality `compare_avr()`, armed. `size_baseline_base01.json` is the **frozen**
  MERGE-05 reference and is not this phase's comparison point.
- `firestarter/tests/test_checker_convention.py` — `FLOOR = 5` / `FIXTURE_FLOOR = 10`, scoped to
  `scripts/check_*.py`. A new `scripts/check_*.py` costs four artifacts plus both floor bumps
  (Phase 125 C-11 measured it) — prefer `tests/test_*.py` unless a checker is genuinely needed.
- `firestarter/tests/test_vpp_seam_manual_on_every_board.py`,
  `firestarter/tests/test_pinmap_guard_fires.py` — the in-tree precedents D-01's harness follows.
- `firestarter/src/boards/rurp_serial_utils.cpp:378` — the existing CRC8-CCITT `PROGMEM`
  accessor. Read to confirm it is **not** a reusable CRC32 source (it is AVR-shaped).

### Design reference — vendor the in-scope subset, follow nothing else

- **Blob `4b1a441`** (`platform/py32f071/PORTING.md`, 195 lines) — read with
  `git cat-file -p 4b1a441` from `/workspaces/firestarter` (**verified readable
  2026-07-31**). In scope: §"Configuration storage" (the `StoredConfiguration` wrapper and the
  *"a failed or interrupted write must leave the previous record usable"* property). Superseded:
  the entire §"PY32F071 backend modules" tree. Out of scope: §"ADC measurement" steps 5–6,
  §"DAC VPP control", and the acceptance items covering calibration, closed-loop DAC and real
  hardware.
- `origin/feature/py32f071-full-support` (PR #47, **closed**) — where the blob also lives.
  Nothing else from this branch may be used (`Out of Scope`: its `src/usb.c` is a ring buffer
  over weak no-op hooks).

### Host repo — Phase 127's obligation, recorded here (D-12)

- `firestarter_app_py32/firestarter/py32_dfu.py` (on the unmerged
  `feature/py32f071-fw-install` @ `4ee64a1`) — `FLASH_BASE = 0x08000000` / `FLASH_SIZE =
  128 * 1024` at `:107–108`; the envelope refusal at `:648`; payload-scoped erase at `:748–750`.
- `firestarter_app/tests/scan_paths.py` — `CROSS_REPO_TEST_PATHS` at `:94`. **No** config or
  linker-script entry today; one is required if Phase 127 adds a host test reading firmware text.
- `firestarter_app/tests/fw_presence.py` — the BASE-02 single cross-repo presence probe keyed on
  `../firestarter/.git`. Note its documented **import-time binding** caveat.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`firestarter/tests/test_vpp_seam_manual_on_every_board.py`** (Phase 125) — a pytest that
  compiles a firmware `.cpp` with host `g++` by explicit path, links a shim, runs it and
  asserts the result. D-01/D-02's harness is this pattern with a RAM-fake backend injected.
- **`firestarter/tests/test_pinmap_guard_fires.py`** (Phase 124 D-14) — the compile-must-fail
  leg pattern, if any non-vacuity guard here needs one.
- **`platform/py32f071/CMakeLists.txt`'s `PY32_EXCLUDED` block and `FIRESTARTER_COMMON_SOURCES`**
  — this phase adds and removes lines in machinery that already exists; the exclusion it
  removes was written *for this phase* and says so.
- **`scripts/check_size_baseline.py` + the post-124 `size_baseline.json`** — the measurement
  machinery is armed; this phase reads figures, it does not build a comparator.
- **`123-/124-/125-NONREGRESSION.md`** — the evidence-artifact template, reused in structure.
- **`src/boards/rurp_common.cpp`** — the existing precedent for "AVR-only common code in
  `src/boards/`, excluded from the ARM manifest", which D-08 follows exactly.

### Established Patterns

- **A declaration with no implementation and no consumer does not land** (Phase 124 D-01,
  Phase 125 D-09). Governs the status-enum and wraparound-branch rejections.
- **A guard that supplies the answer it checks is dead** (Phase 124's `RURP_PY32F071_PINMAP_CONFIGURED`).
- **Never prove "untouched" with a path-scoped `git diff`** — blob SHAs, or empty
  `git status --porcelain` scoped to the **firmware** repo by name.
- **Assert counts, never "tests pass"** — 141 cases / 17 suites on both pinned native envs.
- **Cross-repo gates scan firmware source *text*.** A firmware rename silently broke a host
  gate four times in Phase 117 and the fail-**open** form was reproduced in A-7. This phase
  moves firmware files, so the nine-gate sweep must be shown to **run**.
- **`firestarter/tests/` is PIO-invisible; `firestarter/test/` is globbed into builds.** D-01's
  harness must live in `tests/`.
- **`include/messages.h` is codegen-generated** from the meta repo's canonical `messages.toml`.
  D-15's refusal to distinguish blank-from-corrupt on the wire is partly the refusal to pay
  that cost here.

### Integration Points

- **`src/rurp_config_utils.cpp`** was pinned byte-identical by Phase 125 VPP-03 precisely so
  that any regression here is attributable to this phase alone. That pin is now spent — this is
  the phase that touches it.
- **`platform/py32f071/CMakeLists.txt`** was edited by Phase 125 (two lines) and is edited again
  here (three edits) and by Phase 128 (release fold). Keep this phase's diff to D-08's three.
- **Phase 129 (PCB record) depends on this phase's *actual* reserved addresses** — PCB-03 cites
  the flash budget "as actually reserved by CFG-06", plus D-13's bootloader seam and its
  migration caveat. Whatever `126-NONREGRESSION.md` records is what Phase 129 quotes.
- **Phase 127 (host DFU) runs in PARALLEL** and owns the cross-repo half of Criterion 5 (D-12).
  Different repo, disjoint files, no shared gate — but a shared **contract**.
- **All three repos are on their milestone branches** — firmware and host on
  `v1.23-py32f071-integration`, meta on `gsd/v1.23-py32f071-integration`. Verify with `git` at
  execute time regardless; `gsd-tools query commit` has been observed switching branches.
- **The two gitignored py32 worktrees** (`firestarter_py32_ci/`, `firestarter_app_py32/`) are
  checkouts of the same repos, never gitlinked. Read from them; do not write into them.

</code_context>

<specifics>
## Specific Ideas

- **The operator overrode one recommendation, deliberately: D-13's bootloader placeholder.** The
  recommendation was config-pages-only, on the standing rule that a reservation with no consumer
  does not land. The operator chose the zero-length named seam so Phase 129 can cite a symbol
  rather than prose. When the factual wrinkle was surfaced — that a bottom-of-flash placeholder
  does **not** resize for free, unlike the top-of-flash config region — the operator took the
  option that keeps the seam **and** writes the cost down. The planner must implement it as
  chosen, and must not quietly upgrade it to a real reservation or quietly drop it.
- **Where an option makes a hazard *stated* and another leaves it *implied*, choose stated.**
  That principle (Phase 125 `<specifics>`) was applied four times in this discussion and each
  time the operator took the stated form: the bool return over the trusting void (D-06), the
  linker-enforced region over the convention (D-11), the KAT-anchored CRC over self-assertion
  (D-05), the honest placeholder comment over a silent one (D-13).
- **Where one option makes a target special-cased and another makes the mechanism uniform,
  choose uniform, and pay for it with a measurement rather than an assurance.** D-14 (one
  validate policy on both platforms, with its unmeasurable first-boot flash write recorded as a
  non-claim) and D-07 (all four functions common) are both that choice. It is also why the
  `#ifdef __AVR__`-in-one-file option was rejected outright.
- **The tested code must be the shipped code.** D-02 is the single most consequential decision
  in this phase. This project has twice spent a whole phase unwinding a gate that tested a copy
  or supplied its own answer; D-02 pays a small structural cost up front to avoid a third.
- Fifteen of the seventeen decisions above are recorded as **locked** so downstream agents do
  not re-ask. The two most consequential to reverse cheaply, if either is wrong, are **D-03**
  (the core under `platform/py32f071/` rather than `src/` — it is what keeps the AVR flash delta
  attributable to the policy split alone) and **D-10** (top-of-flash placement — changing it
  after Phase 129 cites it is a flash-map migration).

</specifics>

<deferred>
## Deferred Ideas

- **Distinguishing "blank" from "both slots corrupt" on the wire** (D-15) — real diagnostic
  value on a board that has been running, but needs the declined status enum plus a
  `messages.toml` codegen round-trip and host constants parity. Revisit when a host consumer
  exists.
- **A richer backend status enum** (`OK / BLANK / CRC_FAIL / IO_ERROR`) (D-06) — returns with a
  consumer attached, or not at all.
- **Reserving real flash for the self-flash bootloader** (D-13) — **FUT-N05**, the seed's
  *primary* install route and its own milestone. D-13 leaves a named zero-length seam and an
  explicit statement that giving it size is a flash-map migration.
- **Torn-write-at-arbitrary-byte-offset and random-fill power-loss test matrices** (D-16) —
  stronger properties that assert robustness against flash-controller behaviour unobservable
  without silicon.
- **Deferring the first-boot config flush until after USB enumerates** (D-14) — a lifecycle hook
  no other platform has; revisit if silicon ever shows enumeration disturbed by a flash stall.
- **Proving that a DFU firmware install preserves config** (D-10) — the placement makes it the
  *intended* behaviour, but verifying it needs a board. Carry as an explicit non-claim to
  Phase 130's honesty ledger.
- **Shrinking the host's `FLASH_SIZE` to the app region** so the envelope guard refuses any
  image that would reach config (D-12) — stronger refusal, but it would make the host unable to
  flash the full part it describes. Revisit alongside FUT-N05.
- **A native no-op storage backend** so the *policy* layer itself could be exercised by
  `pio test -e native` — would need a `build_src_filter` change and moves the pinned 141/17
  counts. Revisit in a phase that owns a re-baseline.
- **`FUT-ARMSIZE`** — checking ARM flash/RAM into a baseline with a RAM ceiling. CI already runs
  `arm-none-eabi-size`, but only into the job log where a 3 KiB regression would pass unnoticed.

### Reviewed Todos (not folded)

14 todos matched, all on generic keyword overlap ("config", "flash", "phase", "src", "cpp").
**None folded** — none intersects this phase's scope:

- **`correct-v128-py32-roadmap-prior-art.md`** (0.6) — the ROADMAP slot renumber and stale
  prior-art correction are **Phase 130's** explicit scope (CLOSE-03). Reviewed-not-folded for
  the third time (Phases 124 and 125 did the same).
- **`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`** (0.6) — the VPP
  *measurement gate*, not config storage. Already reviewed-not-folded twice.
- **`delete-jp5-dead-renderer.md`** (0.6) — matched on the word "config"; it concerns a host-side
  Rev 2.2 jumper renderer, unrelated to configuration persistence.
- **`prove-pio-dev-flag-fails-closed.md`** (0.6) — a `DEV_TOOLS` build-flag proof; adjacent to
  MERGE-08's ARM `DEV_TOOLS` decision but already closed there.
- **`spike-databuffer-size-speed-delta.md`** (0.6) — `DATA_BUFFER_SIZE` is explicitly Out of
  Scope for v1.23 (wire-visible via CAP-01).
- **`avrdude-mcu-detection-fallback.md`**, **`cobs-decoder-framelevel-deadline-wr01.md`**,
  **`fold-response-code-into-log-macro.md`**, **`photograph-modified-rev-0.md`**,
  **`write-modifications-md-rework-trace.md`**,
  **`remove-dead-json-init-sizeof-pointer-bug.md`** (all 0.6),
  **`decode-infoic-flags-bits-14-15-protect-metadata.md`**,
  **`gh12-followup-after-dev-sdp-retirement.md`** (0.4) — keyword matches only.

</deferred>

---

*Phase: 126-flash-persistent-config-via-a-storage-backend-seam-highest-r*
*Context gathered: 2026-07-31*
