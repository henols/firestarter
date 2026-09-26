# Phase 129: Flash-Path Decision & PCB Requirements Record — Research

**Researched:** 2026-08-02
**Domain:** Decision-record authoring; PY32F071 boot/flash/USB silicon facts; USB VID/PID allocation; cross-repo documentation gates
**Confidence:** HIGH on the silicon and provenance findings (all traced to the pinned SDK commit, the official datasheet, or a local build); MEDIUM on the bootloader size budget (derived from measurement, not from a built bootloader); HIGH on the VID/PID route.

> **Read `## Corrections to CONTEXT.md` first.** This phase's premise contains four factual
> errors that are load-bearing for PCB-03, PCB-04 and D-13. Two of them are repeated verbatim
> in `REQUIREMENTS.md`, `ROADMAP.md` and the linker script itself. Planning around them without
> correcting them would put a false statement into the milestone's most durable artifact —
> a document whose entire purpose is citability by a future schematic author.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Where the record lives**

- **D-01:** **Two-layered.** The authoritative record lives in the meta repo at `.planning/`; a **subset** lives in the firmware repo under `platform/py32f071/`. Precedent: `.planning/v1.7-SHIELD-REVS.md` + its sub-repo subset. Rejected: meta-only (a schematic author working in the firmware repo would never find it) and firmware-only (loses the meta decision trail).
- **D-02:** **Milestone-prefixed decision doc**, following this repo's actual precedent — `.planning/v1.9-COBS-DECISION.md`, `.planning/v1.10-FRAMING-DECISION.md`, `.planning/v1.13-PROTOCOL-ENUMERATION.md`. **Do not introduce an ADR numbering scheme** — none exists in this repo and the ROADMAP's phrase "ADR-style" means the shape, not a numbered series. Filename is the planner's call within that convention.
- **D-03:** The **firmware layer is a subset**, not a mirror: PCB checklist, flash budget, VID/PID decision, socket-empty warning. The meta layer additionally carries the full rationale and the rejected-route table. A **fail-closed sync gate** asserts the shared sections match between the two copies. That gate **must ship with a planted-violation fixture** — this milestone has repeatedly measured that source-scanning cross-repo gates fail OPEN (Phase 123 BASE-08; research finding A-7; the four gate breakages in Phase 117).
- **D-04:** **`firestarter_app` is not touched.** Two repos only. PCB-05 lands in the firmware layer and the meta record; propagating it to `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` is left to Phase 130 or a later host phase.
- **D-05:** **Meta gitlinks are bumped in-phase**, matching what Phase 125 actually did (`4bb038e`) and Phase 128 after execution — not deferred to milestone close.

**USB VID/PID (PCB-04)**

- **D-06:** **Record only — `platform/py32f071/src/usb_cdc.c` is NOT edited.** Lines 20 and 24 keep `FIRESTARTER_USB_VID 0x36B7U` / `FIRESTARTER_USB_PID 0xFFFFU`. PCB-04's wording ("replaces the placeholder") is satisfied by a recorded decision plus a tracked obligation, not by a code change. This is what keeps the phase free of an ARM rebuild.
- **D-07:** **The decision is pid.codes — VID `0x1209`**, the established free registry for open-source hardware. Research must confirm the current request process, its conditions, and whether anything about it has changed. Rejected: keeping the squat (leaves PCB-04 as an obligation rather than a decision), and a USB-IF vendor ID (four-figure cost for a project with no board).
- **D-08:** **The phase decides the route; it does not request the PID.** Allocation is a public pull request against `pidcodes.github.com` filed under the operator's name — outward-facing, and **no agent files it**. Tracked as an operator follow-up.
- **D-09:** The record states a **hard ship gate**: `0x36B7`/`0xFFFF` is unallocated and squatted; **no PY32F071 board ships and no release advertises a USB identity until a real PID is allocated.** PCB-04's "liability" clause becomes a checkable condition, not a warning.

**Flash budget & bootloader region (PCB-03)**

- **D-10:** The record names a **sector-quantised bootloader figure** — whole 8 KiB sectors, research-sized against a CDC + COBS bootloader — and **every appearance of that figure carries its migration cost**. The linker comment forbids a number *that looks already paid for*; it does not forbid a number.
- **D-11:** **The linker script gets a comment-only cross-reference.** `BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0` stands unchanged. The existing comment already says "for Phase 129 (PCB-03/FUT-N05) to cite" — add the record's actual filename so the reference closes in both directions. **Giving BOOTLOADER a real length is explicitly rejected** (it moves the application ORIGIN — Phase 126 D-13).
- **D-12:** **Vector relocation: state the cost, then enumerate candidates.** The cost is that with no VTOR, every previously flashed unit's vector-table address changes. The record lists the candidate mitigations research surfaces (SYSCFG `MEM_MODE` remap, RAM vector copy, linker-relocated app with a trampoline) **each tagged with its confidence** — none is a plan; FUT-N04 already deferred the software half as unvalidatable without silicon.
- **D-13:** **No operator-gated ARM CI run this phase.** The only firmware edits are a new `.md` and a linker comment; neither can change emitted output. Prove it locally instead — a byte-identical-artifact or comment-stripped-diff argument recorded in the non-regression doc. Phases 125/126/128 each needed CI because they added translation units; this one adds none. **The standing rule still holds: no task may run `git push` or `gh workflow run`.**

**PCB requirements list (PCB-02)**

- **D-14:** **The four named items plus what this milestone surfaced.** Named by PCB-02: BOOT0/nBOOT1 strap reachability, exposed SWD pads, a contiguous 8-bit GPIO port for the data bus, a depopulated HSE footprint. Additionally in scope because they are equally unrecoverable after layout: VPP sense on PA4 / ADC ch4, data-bus test points, USB connector and D+ pullup. The phase goal is "every PCB decision free today and unrecoverable after layout" — broader than the four, and the record should match the goal.
- **D-15:** **Seed item 5 — reboot-into-bootloader as a protocol command vs strap-only — is recorded as an open question with its board cost stated on both sides**, not decided. Strap-only means the BOOT0 jumper must stay reachable forever; a protocol command could relax that. FUT-N04 owns the software half.
- **D-16:** **Each checklist row is: checkbox + one line of rationale + one line of what breaks if the board ships without it.** A schematic author can work straight off it, and Phase 130's honesty ledger (CLOSE-02) can cite specific rows.

**Seed disposition (PCB-01)**

- **D-17:** `.planning/seeds/py32f071-no-external-tool-fw-install.md` has its `trigger_condition` **already fired** (v1.28 was activated as v1.23) while `status:` still reads `dormant`. Update the frontmatter to reflect reality — the DFU runner-up landed in v1.23, the primary self-flash route did not — and record that **the seed remains live for FUT-N05**. This is what PCB-01's "does not retire the seed" points at concretely.
- **D-18:** **The new record is canonical** for the flash-path decision. The seed and FUT-N05 both point at it. It is the only document that cites Phase 126's actually-reserved addresses, which is the entire reason the phase exists.

### Claude's Discretion

Two areas the operator explicitly delegated:

- **PCB-05 placement and strength.** Where the socket-empty-before-install instruction lands within the two in-scope repos, and whether it stays documentation or becomes an installer-time prompt. Note the constraint from D-04: `firestarter_app` is out of scope, so an installer-time prompt is **not** available this phase. Also note `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` currently says **nothing** about the socket (measured 2026-08-02), and `platform/py32f071/README.md` §"Hardware validation still required" is the nearest existing text.
- **Sourcing / confidence discipline.** Whether every claim carries a per-claim sourcing tag and an "unverified until silicon" marker, or one blanket caveat suffices. Resolve from the project's existing honesty conventions; CLOSE-02's honesty ledger is the downstream consumer.

Also at planner discretion: exact filenames, section ordering, and the mechanism of the D-03 sync gate.

### Deferred Ideas (OUT OF SCOPE)

- **Editing `usb_cdc.c` to the allocated VID/PID** — follows the pid.codes allocation, which follows an operator-filed public PR. A later phase or milestone; it will need an ARM build to stay honest.
- **Filing the pid.codes request** — outward-facing operator action, tracked as a follow-up from this record (D-08).
- **Propagating PCB-05 into `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md`** — Phase 130 or a later host phase (D-04).
- **An installer-time socket-empty prompt** — HOST scope, and unavailable this phase since the app repo is untouched.
- **Giving BOOTLOADER a real length** — a flash-map migration on a part with no VTOR; FUT-N05 owns it (D-11).
- **Software reboot-into-bootloader** — already deferred as FUT-N04; this phase only records its PCB consequence (D-15).
- **Introducing an ADR numbering scheme / `adr/` directory** — a repo-wide convention change that should not ride on a single document (D-02).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `REQUIREMENTS.md` lines 94–98) | Research Support |
|----|-------------|------------------|
| **PCB-01** | The three-tier flash path is recorded as a decision — self-flash bootloader over the existing CDC + COBS transport as intended primary, factory USB DFU as maintainer/manufacturing recovery, SWD as last resort — stating explicitly that landing the DFU path **does not retire** the self-flash seed | §"Three-Tier Flash Path — Verified Substrate"; the seed's own §"Status" already states the non-retirement in the author's words (F-11); SWD pin facts F-9 |
| **PCB-02** | PCB requirements are recorded before the first schematic: BOOT0/nBOOT1 strapping reachable, SWD pads exposed, a contiguous 8-bit GPIO port for the data bus, and a depopulated HSE footprint as a crystal-less-USB hedge | F-5 (BOOT0 = PF8, internal pull-down, boot table), F-9 (SWD = PA13/PA14), **F-10 (the contiguous PB0–PB7 bus does not exist on two of seven packages — a package-selection constraint absent from CONTEXT.md)**, F-8 (CTC/USBD_SOF makes crystal-less USB architecturally supported; the port already runs `HSE_OFF`) |
| **PCB-03** | The flash budget is recorded **as actually reserved** by CFG-06, including the bootloader region and its vector-relocation implication on a part with no VTOR | F-1 verbatim linker regions; **C-1 — the part HAS VTOR and the shipped firmware already writes it**; F-3 measured bootloader size budget with a sector-quantised figure |
| **PCB-04** | A real USB VID/PID decision replaces `usb_cdc.c`'s undocumented `0x36B7`/`0xFFFF` placeholder, noting that squatting becomes a liability the moment a board ships | **C-2 — `0x36B7` is allocated to Puya Semiconductor and the pair is copied verbatim from the pinned SDK's own CDC example**; F-6 pid.codes process, conditions, reserved ranges, `1209:0001` test PID; F-7 allocation-latency measurement |
| **PCB-05** | The socket-empty-before-any-py32-firmware-install safety instruction is documented, the provisional pin map being the reason it is stronger here than the comparable warning in other projects | F-12 (install doc says nothing about the socket — confirmed); F-13 (the provisional map's specific hazard, and the AVR comparable); §"PCB-05 Placement — Recommendation" |

</phase_requirements>

---

## Summary

This phase writes a document, so the research value is concentrated in two places: making the
document's factual claims citable, and making the D-03 sync gate genuinely fail-closed. Both
were pursued, and both produced results that change the plan.

**The premise contains four factual errors.** The most serious is that PY32F071 **has a VTOR**
— `__VTOR_PRESENT 1` in the pinned SDK's own CMSIS device header, and the firmware currently on
this branch already executes `SCB->VTOR = FLASH_BASE` at every boot, because it compiles the SDK
`system_py32f071.c` that does it. "A part with no VTOR" appears in the linker script comment,
`REQUIREMENTS.md` PCB-03, `ROADMAP.md` criterion 3, `FUT-N04` and CONTEXT.md D-12. The second is
that `0x36B7` is **not** unallocated: it belongs to Puya Semiconductor (Shanghai) Co., Ltd., and
the exact pair `0x36B7`/`0xFFFF` is copied verbatim out of the pinned SDK's own USB CDC example.
That is a materially worse liability than squatting an empty slot, and it changes what PCB-04's
record has to say. The third is that the ARM toolchain is **not** absent from this devcontainer —
it installs from the same apt packages CI uses, and the phase's D-13 non-regression argument was
executed end-to-end during this research and came out byte-identical. The fourth is smaller: the
seed's "a small bootloader in the first few KB" is measurably optimistic.

**The silicon facts PCB-02 needs are now sourced**, from the official PY32F071 datasheet Rev 0.7
and the pinned SDK rather than from web lore. BOOT0 is `PF8`, defaults to input with pull-down
enabled, and the three-way boot table is identical in the datasheet §2.3 and Puya UM1504 §3. SWD
is PA13/PA14 with internal pull-up/pull-down after reset. Crystal-less USB is architecturally
supported (CTC accepts `USBD_SOF` as a reference) and the port already runs `HSE_OFF`. And one
requirement that CONTEXT.md does not contain surfaced: **the provisional PB0–PB7 contiguous data
bus is physically impossible on two of the part's seven packages**, which makes PCB-02's third
item a package-selection decision, not just a pin-assignment one.

**Primary recommendation:** Plan the record around the corrected facts, not the CONTEXT.md ones.
Escalate C-1 and C-2 to the operator before the record is written — both change what the document
must *say*, not merely how it is worded, and C-1 additionally requires a one-line correction to
the linker script comment that D-11 is already opening. Use the local ARM build (now proven) as
D-13's evidence. Site the D-03 gate in the firmware repo, keyed on a meta-repo presence marker,
and record honestly that it runs locally only — the same disposition Phase 126 took for the
directly analogous `test_config_storage_design_vendored.py`.

---

## Corrections to CONTEXT.md

Four locked positions are contradicted by evidence. Two are decisive.

### C-1 — The PY32F071 **has** a VTOR, and the shipped firmware already uses it. *(HIGH confidence — three independent in-tree proofs)*

**What CONTEXT.md / REQUIREMENTS.md / ROADMAP.md / the linker script assert:**

- D-12: *"The cost is that with **no VTOR**, every previously flashed unit's vector-table address changes."*
- `REQUIREMENTS.md` PCB-03: *"its vector-relocation implication **on a part with no VTOR**"*
- `ROADMAP.md` criterion 3: *"a stated vector-relocation implication **for a part with no VTOR**"*
- `REQUIREMENTS.md` FUT-N04: *"deferred because **Cortex-M0+ has no VTOR**, the `SYSCFG MEM_MODE` remap is reported to have no effect on some sibling F0 parts…"*
- `platform/py32f071/linker/PY32F071xB_FLASH.ld:16`: *"…every previously flashed unit's vector table address changes, **on a part with no VTOR**."*

**What is actually true:**

1. The pinned SDK's CMSIS device header declares VTOR present:
   ```c
   #define __CM0PLUS_REV             0 /*!< Core Revision r0p0                            */
   #define __MPU_PRESENT             0 /*!< PY32F071 do not provide MPU                   */
   #define __VTOR_PRESENT            1 /*!< Vector  Table  Register supported             */
   #define __NVIC_PRIO_BITS          2 /*!< PY32F071 uses 2 Bits for the Priority Levels  */
   ```
   `Drivers/CMSIS/Device/PY32F071/Include/py32f071xB.h:56-59` at the exact `GIT_TAG` this port
   fetches (`platform/py32f071/CMakeLists.txt:16` → `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`).
   Fetched 2026-08-02; `sha256 = 08de8dbc4087557934ef85d538a33dd5b5a254ad94ee529fea02489d1cac6dd0`.
   [VERIFIED: pinned SDK blob, SHA-checked against a local copy]

2. The SDK file **this target compiles** writes VTOR unconditionally at boot:
   ```c
   void SystemInit(void)
   {
     RCC->ICSCR = ...;
     /* Configure the Vector Table location add offset address ------------------*/
   #ifdef VECT_TAB_SRAM
     SCB->VTOR = SRAM_BASE | VECT_TAB_OFFSET;  /* Vector Table Relocation in Internal SRAM */
   #else
     SCB->VTOR = FLASH_BASE | VECT_TAB_OFFSET; /* Vector Table Relocation in Internal FLASH */
   #endif
   }
   ```
   `Templates/PY32F071xx_Templates/Src/system_py32f071.c:139-152` — named explicitly in
   `platform/py32f071/CMakeLists.txt`'s `PY32_SDK_SOURCES`, and reached by
   `startup_py32f071.s`'s `bl SystemInit`. [VERIFIED: pinned SDK blob + in-tree CMake manifest + startup source]

3. The file also ships a `VECT_TAB_OFFSET` knob (`system_py32f071.c:55`) and a
   `FORBID_VECT_TAB_MIGRATION` guard (`:53`) — the vendor's own vector-relocation seam.
   [VERIFIED: pinned SDK blob]

**Why it matters — this is not a pedantic correction.** The whole shape of D-12 collapses. With
VTOR present, the standard mitigation is one register write in the bootloader before it branches
to the application; the three candidates D-12 asks research to enumerate (SYSCFG `MEM_MODE`
remap, RAM vector copy, linker-relocated app with a trampoline) are the **no-VTOR** workarounds
used on true Cortex-M0 parts such as STM32F0. Enumerating them here as if they were live
candidates would write a page of irrelevant engineering into the milestone's most durable
document, and would leave a future FUT-N05 implementer solving a problem this part does not have.

FUT-N04's deferral reasoning inherits the same error twice over: it says "Cortex-M0+ has no
VTOR" (VTOR is an *implementation option* on Cortex-M0+, and this implementation has it), and it
leans on the `SYSCFG MEM_MODE` unreliability report, which is about sibling **F0** parts and is
moot once VTOR exists. **The deferral itself may still be correct** — it cannot be validated
without silicon, and FUT-N05 obsoletes it for the normal path — but its stated *reason* is wrong.
That distinction matters for CLOSE-02's honesty ledger.

**What the migration cost actually is** (the corrected framing D-10/D-11 should carry): giving
`BOOTLOADER` a non-zero length moves the application's `ORIGIN`, so a new application image is
not loadable by any mechanism that assumes the old origin, and every already-flashed unit needs a
full re-flash through DFU or SWD rather than an in-place update — precisely the recovery paths a
self-flash bootloader exists to avoid. The vector table moving is real but **cheap**, because
VTOR handles it. The expensive part is the one-time fleet migration, and it must be paid before
the self-flash path can ever be used to pay for itself. That is a *stronger* argument for
reserving the region deliberately rather than a weaker one — the linker comment's instinct is
right even though its stated reason is wrong.

**Recommended disposition:** D-11 is already opening the linker comment to add a filename. Fix
the "on a part with no VTOR" clause in the same edit — it is one line, in a file the phase is
already touching, and leaving a known-false statement in a comment that explicitly instructs
future readers is the worst available outcome. Correct PCB-03/criterion-3/FUT-N04 wording via
Phase 130's CLOSE-01 correction sweep (they are ROADMAP/REQUIREMENTS prose, which CLOSE-01 owns),
and record the correction in this phase's record so CLOSE-02 can cite it. **This is an operator
decision, not a planner one** — PCB-03 and ROADMAP criterion 3 are the phase's own acceptance
wording, and satisfying them literally now requires writing something false.

---

### C-2 — `0x36B7` is **allocated to Puya Semiconductor**, and the placeholder pair is copied verbatim from the pinned SDK's own CDC example. *(HIGH confidence)*

**What CONTEXT.md asserts (D-09):** *"`0x36B7`/`0xFFFF` is **unallocated and squatted**."*
**What REQUIREMENTS.md PCB-04 asserts:** *"`usb_cdc.c`'s **undocumented** `0x36B7`/`0xFFFF` placeholder."*

**What is actually true:**

1. **VID `0x36B7` is registered to "Puya Semiconductor (Shanghai) Co., Ltd."**
   [CITED: https://the-sz.com/products/usbid/index.php?v=0x36B7 — accessed 2026-08-02]
   It is **not** present in `linux-usb.org/usb.ids` (25705 lines, fetched 2026-08-02) — that
   file is community-maintained and incomplete, so its silence is not evidence of non-allocation.
   The nearest neighbour it does carry is `3636 InVibro`, i.e. the `0x36xx` block is in active
   USB-IF allocation. [VERIFIED: local fetch of usb.ids]

2. **The exact pair is Puya's own example.** In the pinned SDK, at the identical `GIT_TAG`:
   ```c
   #define USBD_VID           0x36b7
   #define USBD_PID           0xFFFF
   ```
   `Projects/PY32F071-STK/Applications/USB_Device/USBD_Virtual_COM_Port/Src/usbd_cdc_if.c:9-10`.
   The same example ships a Windows driver INF matching it:
   `pycdc.inf:28,31` → `%DESCRIPTION%=DriverInstall,USB\VID_36B7&PID_FFFF`.
   [VERIFIED: pinned SDK blobs, fetched 2026-08-02]

**Why it matters.** Three consequences, all of which change what the record says:

- **The liability is different and worse.** Squatting an unallocated ID is a collision risk.
  Shipping `0x36B7` presents a *third party's registered vendor identity* — the silicon vendor's,
  on a product they did not make. That is not merely untidy; it is the kind of thing that makes a
  board un-shippable rather than merely inadvisable. D-09's ship gate is *correct*, and this
  finding makes it more defensible, not less — but its stated premise must be rewritten.
- **"Undocumented" is half right.** The values are undocumented *in this tree* (no comment in
  `usb_cdc.c` says where they came from), but they are fully traceable to a specific upstream
  file. The record should say so — it converts an unexplained magic number into a known-provenance
  copy, which is exactly the kind of thing the milestone's honesty conventions reward.
- **Collision is near-certain, not hypothetical.** Every PY32 project that starts from Puya's CDC
  example and does not change the descriptor presents the same `36B7:FFFF`. Two such devices on
  one host is a real, common failure mode.

**Recommended disposition:** rewrite D-09's premise to "allocated to the silicon vendor and
copied from their SDK example — presenting another company's vendor identity", keep the ship gate
verbatim, and add the provenance citation (`usbd_cdc_if.c:9-10` at the pinned SDK SHA) to the
record so the next reader does not have to re-derive it. Also see **F-6/F-7** — there is a
documented interim option (`1209:0001`) that CONTEXT.md does not consider, and a measured
allocation latency that makes D-09's gate riskier than it looks.

---

### C-3 — The ARM toolchain is **not** absent from this devcontainer; the D-13 proof was executed successfully during this research. *(HIGH confidence — executed, not reasoned)*

**What the milestone asserts:** `REQUIREMENTS.md` §"Validation Ceiling" (as quoted by
`platform/py32f071/CONFIG-STORAGE.md` §"Claim ceiling", `126-04-SUMMARY.md`, `123-CONTEXT.md:274`
and `123-RESEARCH.md:168`): *"Any ARM build evidence this milestone produces is a CI workflow run
URL plus a head SHA, never a local build — `arm-none-eabi-gcc`, `cmake` and `ninja` are absent
from this environment."*

**What is actually true:** they are absent *as shipped*, and **installable**. Executed 2026-08-02
in this devcontainer:

```bash
sudo apt-get install -y --no-install-recommends \
    gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib
pip install cmake ninja
```

- `arm-none-eabi-gcc 14.2.1 20241119` (Debian `15:14.2.rel1-1`), `cmake 4.4.0`, `ninja 1.13.0`.
- `cmake -S platform/py32f071 -B <build> -G Ninja -DCMAKE_BUILD_TYPE=Release` configured cleanly;
  `FetchContent` cloned the pinned SDK at the recorded `GIT_TAG` without incident.
- `cmake --build` → **exit 0**, 41/41 objects, linked.
  `text=27260  data=112  bss=5888  dec=33260  hex=81ec`.

Note the two extra packages: the CI composite action (`.github/actions/build-py32f071/action.yml:43-48`)
installs only `cmake ninja-build gcc-arm-none-eabi binutils-arm-none-eabi`. Debian's
`gcc-arm-none-eabi` does **not** pull newlib, so `<string.h>` is missing and every C++ TU fails;
`ubuntu-latest` evidently satisfies it another way. Anyone reproducing this locally needs
`libnewlib-arm-none-eabi` and `libstdc++-arm-none-eabi-newlib` in addition.

**The D-13 argument was then executed, not argued.** Baseline artifacts hashed; the D-11 edit
simulated (three added comment lines in the `BOOTLOADER` block naming a record filename);
rebuilt — the link step re-ran, since `LINK_DEPENDS` binds the target to the linker script:

| Artifact | Before | After |
|---|---|---|
| `firestarter_py32f071.bin` | `66b6a8dc…5b495e` | `66b6a8dc…5b495e` |
| `firestarter_py32f071.hex` | `9599a625…5913dc` | `9599a625…5913dc` |
| `arm-none-eabi-size` | `27260 / 112 / 5888` | `27260 / 112 / 5888` |

Byte-identical. The linker script was restored (`git status --porcelain` → 0 entries) and the
firmware tree is clean at `7a0a375de7e71ed3e9108b9531fffb59d8d95cd8`.

**Why it matters.** D-13 asks for "a byte-identical-artifact **or** comment-stripped-diff
argument". The stronger of the two is available and cheap. The planner should specify the
byte-identical form, with the exact commands, rather than settling for a diff-shape argument.

**Two honesty constraints the record must carry.** (a) A *local* build is not a *CI* build — the
local GCC 14.2.1 produces `text=27260` where CI's Phase 126 run produced `text=27344`, so **no
absolute size figure from a local build may be compared against a CI figure**. The D-13 claim is
a **delta** claim — same toolchain, same tree, two builds — and deltas are unaffected by the
version difference. (b) This does not license any *behavioural* claim: the build proves the image
is unchanged, never that it runs. **The Validation Ceiling wording should be narrowed by Phase 130
(CLOSE-01)** from "absent from this environment" to something like "not installed by default;
locally installable, and local builds may support delta claims only, never absolute-size or
behavioural ones." Left as-is, it is a ceiling this phase would be violating by obeying D-13.

---

### C-4 — The seed's "a small bootloader in the first few KB" is measurably optimistic. *(MEDIUM-HIGH confidence — measured components, unbuilt bootloader)*

`.planning/seeds/py32f071-no-external-tool-fw-install.md:24`: *"A small bootloader in the **first
few KB** of the 128 KiB flash."*

Measured against the real objects (see **F-3**), the components a CDC + COBS self-flash
bootloader would have to carry already total ≈ **14.6 KiB** before any bootloader logic exists.
"A few KB" is off by roughly a factor of five, and one 8 KiB sector is not a viable reservation.
This matters because D-10 asks for a *sector-quantised* figure and the seed is the document a
reader would otherwise anchor on. The record supersedes it (D-18); it should say so explicitly
for this number.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Authoritative flash-path decision + rationale + rejected routes | **Meta `.planning/`** | — | D-01/D-02; decision trail belongs with the planning record, not with code |
| PCB checklist, flash budget, VID/PID, socket warning (subset) | **Firmware `platform/py32f071/`** | Meta (full copy) | D-01/D-03; a schematic author works in the firmware repo |
| Cross-copy section-parity assertion | **Firmware `tests/`** | — | Only repo with a test runner; meta has none (F-14) |
| Linker cross-reference to the record | **Firmware `linker/*.ld`** (comment) | — | D-11; closes the reference in both directions |
| Seed frontmatter status | **Meta `.planning/seeds/`** | — | D-17 |
| Socket-empty safety instruction | **Firmware `platform/py32f071/`** | Meta record | D-04 puts the host doc out of reach; F-13 |
| Installer-time socket prompt | *(none this phase)* | — | Would be `firestarter_app`; D-04 forbids it |
| Non-regression evidence for the firmware edits | **Firmware, local build** | — | C-3; delta claim only |
| Meta gitlink bump | **Meta** | — | D-05 |

---

## Verified Substrate — Findings

Every claim below carries its source. Silicon-behaviour claims are tagged
`[UNVERIFIED-UNTIL-SILICON]` regardless of documentation quality — no PY32F071 board exists.

### F-1 — The reserved flash map, verbatim *(HIGH — read from the file)*

`firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` at HEAD `7a0a375`:

| Region / symbol | ORIGIN | LENGTH | Note |
|---|---|---|---|
| `BOOTLOADER (rx)` | `0x08000000` | **0** | named seam only |
| `FLASH (rx)` | `0x08000000` | **120K** (`0x1E000`) | app occupies `0x08000000`–`0x0801DFFF`, sectors 0–14 |
| `CONFIG (r)` | `0x0801E000` | **8K** | sector 15, pages 480–511 |
| `RAM (xrw)` | `0x20000000` | **16K** | |
| `__config_page_size` | — | `256` | |
| `__config_slot_a_start` | `0x0801E000` | 256 B | page 480 |
| `__config_slot_b_start` | `0x0801E100` | 256 B | page 481, different erase unit |
| `__config_region_end` | `0x08020000` | — | |

CONTEXT.md's canonical-refs table reproduces these correctly. Two structural `ASSERT`s exist
(app/config overlap; slot spacing). Flash geometry — page 256 B, sector 8192 B, main flash
`0x08000000`–`0x0801FFFF` — is recorded in `CONFIG-STORAGE.md` §"Flash geometry" and sourced to
Puya PY32F07X RM V0.2 §4.1/§4.2.1/Table 4-1, corroborated against the pinned SDK header
(`FLASH_PAGE_SIZE 0x100`, `FLASH_SECTOR_SIZE 0x2000`) — I re-confirmed both against the fetched
blob. CONTEXT.md's description of this is accurate.

### F-2 — The `BOOTLOADER` comment, verbatim *(HIGH — D-11 needs this exact text)*

Lines 11–20 of the linker script, which D-11 edits:

```
    /* D-13 -- NAMED SEAM ONLY, ZERO LENGTH, for Phase 129 (PCB-03/FUT-N05) to cite.
     *
     * READ THIS BEFORE GIVING IT A SIZE. Unlike the CONFIG region below -- which
     * sits at the TOP of flash and can grow downward without moving anything --
     * giving BOOTLOADER a non-zero length MOVES the application's ORIGIN. That is
     * a flash-map MIGRATION, not a resize: every previously flashed unit's vector
     * table address changes, on a part with no VTOR. Phase 129 must record the
     * bootloader budget as an INTENT WITH THAT COST ATTACHED, never as a number
     * that looks already paid for.
     */
```

The clause **"on a part with no VTOR"** is false (C-1). The near-identical paragraph in
`CONFIG-STORAGE.md` §"Reserved flash map" (§"D-13's bootloader seam carries its cost honestly")
does **not** contain that clause — it stops at "every previously flashed unit's vector-table
address changes". So only the linker script needs the correction; the design record's wording is
already survivable, though it would benefit from the corrected framing.

### F-3 — Bootloader size budget, measured *(MEDIUM-HIGH — measured components; the bootloader itself is unbuilt)*

Two independent anchors.

**Anchor A — Puya's own factory bootloader.** UM1504 Table 1-1 gives PY32F071's system memory as
`0x1FFF0000`–`0x1FFF2F00` = **12,032 bytes**, and that image serves **USART, I2C *and* USB DFU**.
[CITED: Puya UM1503/UM1504 *PY32 DFU Application Software* V1.0 EN, §1.1 Table 1-1 —
https://download.py32.org/Tool/en/PY32_DfuTool_V1.0.0/UM1503_PY32DfuTool_User%20Manual%20V1.0_EN.pdf,
accessed 2026-08-02]. Note that Puya achieves this without a HAL.

**Anchor B — this tree's own objects,** measured from the local build (C-3),
`arm-none-eabi-size` per object, `text + data`:

| Object | Bytes | Needed by a CDC+COBS bootloader? |
|---|---:|---|
| `py32f071_hal_rcc.c` | 2612 | yes (48 MHz PLL for USB) |
| `py32f071_hal_flash.c` | 2424 | yes (page erase/program) |
| `usb_dc_py32.c` | 1728 | yes (CherryUSB PY32 port) |
| `usbd_core.c` | 1620 | yes |
| `rurp_serial_utils.cpp` | 1310 | yes (COBS + CRC framing) |
| `usb_cdc.c` | 1012 | yes (descriptors + glue) |
| `py32f071_hal_rcc_ex.c` | 992 | yes |
| `py32f071_hal.c` | 744 | yes |
| `py32f071_hal_gpio.c` | 658 | yes |
| `py32f071_hal_cortex.c` | 398 | yes (NVIC) |
| `system_py32f071.c` | 340 | yes (incl. the `SCB->VTOR` write) |
| `timing.cpp` | 284 | yes (timeouts) |
| `startup_py32f071.s` | 266 | yes (incl. 192 B vector table) |
| `usbd_cdc.c` | 220 | yes |
| **Subtotal** | **≈ 14,608** | before any bootloader logic |

Not counted: the bootloader's own receive/validate/program state machine, a 256 B page staging
buffer's code, image CRC, jump-to-application, `.rodata` for descriptors and strings, and newlib
fragments (`memcpy` etc.). A realistic total is **≈ 17–20 KiB**.

The vector table is exactly **192 B** (`.isr_vector`, `0xC0`, 48 entries) — measured from both
`arm-none-eabi-size -A` and the linker map.

**Sector-quantised conclusion**, in the 8 KiB sectors the part actually erases:

| Reservation | Verdict |
|---|---|
| 1 sector = 8 KiB | **Infeasible.** The USB + flash + clock objects alone exceed it. |
| 2 sectors = 16 KiB | **Tight; requires dropping the HAL** for direct register access, as Puya's own 12,032 B bootloader evidently does. Not a safe planning figure. |
| **3 sectors = 24 KiB** | **The defensible reservation.** ≈ 17–20 KiB measured-plus-estimated with headroom, and it leaves `FLASH` at 96 KiB against a current application of 27,372 B (`text+data`) — 28% used. |

Every appearance of this figure must carry D-10's migration cost, and the cost's *corrected*
statement (C-1): the fleet re-flash, not the vector-table address.

### F-4 — Current ARM footprint *(HIGH — measured locally; delta-usable only, per C-3)*

Local build at firmware HEAD `7a0a375`: `text=27260  data=112  bss=5888  dec=33260`.
Application flash consumed = `text + data` = **27,372 B** of the 122,880 B `FLASH` region
(22.3%). RAM: `bss` 5888 B + `.data` 112 B + 1024 B `_user_heap_stack` = 7,024 B of 16 KiB (42.9%).

For comparison, the CI figures recorded in the planning record — **not** comparable in absolute
terms (different GCC): Phase 124 Plan 11 `text=25796 data=112 bss=5888`; Phase 126 Plan 11
`text=27344 data=112 bss=5888`.

### F-5 — BOOT0 / nBOOT1: the authoritative boot table *(HIGH on documentation; [UNVERIFIED-UNTIL-SILICON] on behaviour)*

Two independent official sources agree exactly.

**PY32F071 Datasheet Rev 0.7 EN §2.3 "Boot modes", Table 2-1 (p.12):**

> At startup, the BOOT0 pin and boot selector option bit nBOOT are used to select one of the three boot options in the following table:

| nBOOT1 bit | BOOT0 pin | Mode |
|---|---|---|
| X | 0 | Main Flash as the boot area |
| 1 | 1 | System memory as the boot area |
| 0 | 1 | SRAM as the boot area |

[CITED: https://download.py32.org/Datasheet/en/PY32F071_Datasheet_Rev0.7_EN.pdf — accessed 2026-08-02, 78 pp.]

**Puya UM1504 §3 "Hardware Connection", Table 3-1** carries the identical table, prefaced by:
> "Before hardware connection, please make sure the MCU's BOOT0 pin is connected high, nBOOT1 is 1, and select System memory as boot area."

`firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` §2 already reproduces this correctly and cites
"Puya UM1504, table 3-1". **CONTEXT.md's framing is sound; the table needs no correction.**

**The PCB facts the record needs:**

| Fact | Value | Source | Confidence |
|---|---|---|---|
| BOOT0 pin name | **`PF8-BOOT0`** (a shared-function pin, also `SEG30`) | Datasheet Figs. 3-1/3-2/3-5/3-6, pin table | HIGH |
| Default state | *"BOOT0 defaults to digital input mode and pull-down is enable."* | Datasheet p.44 note 3 | HIGH |
| PCB consequence | An **internal** pull-down exists, so a bare board boots main flash by default. To reach DFU the strap must actively pull PF8 **high** — jumper, button or test point to VDD. **No external pull-down is required**, but an external one is cheap insurance against a floating strap net. | derived from the above | MEDIUM |
| nBOOT1 | An **option bit**, not a pin. Its factory value is not stated in the datasheet §2.3 or UM1504. | — | **LOW — unresolved, see Open Question 1** |
| Package availability | Bonded on LQFP64/CSP64/QFN64/LQFP48/QFN48/QFN32; **absent on QFN56 (P1)** | Datasheet pin table, PF8/BOOT row: `60 F1 44 60 - 44 30` against header `LQFP64 R1 · CSP64 R1 · LQFP48 C1 · QFN64 R1 · QFN56 P1 · QFN48 C1 · QFN32 K1` | HIGH |

**The unrecoverable-without-SWD question (raised by the research brief):** if `nBOOT1` is
programmed to `0`, then `BOOT0 = 1` selects **SRAM**, not system memory — so the DFU recovery
path is gone and the strap reaches a boot area with nothing in it. Whether that state can be
entered accidentally, and whether the factory default is `1`, are **not** answerable from the
datasheet or UM1504. Both are answerable from the PY32F07X Reference Manual's option-byte chapter,
which is already cited in this tree (RM V0.2) but which I could not obtain in this session. The
record should state the hazard and mark the default unresolved — this is exactly the kind of edge
CONTEXT.md §Specifics asks the document to name rather than pass over in silence. **This is also
the single strongest argument for PCB-02's SWD-pads item**, and the record should make that link
explicit rather than listing the two requirements independently.

### F-6 — pid.codes: the process, verbatim *(HIGH — primary source)*

[CITED: https://pid.codes/howto/ and its repo source `howto.md`; https://pid.codes/faq/;
https://pid.codes/1209/ source `1209/index.md`; all accessed 2026-08-02]

**Who owns `0x1209`.** From `1209/index.md`: *"0x1209 is the Vendor ID originally assigned to
pid.codes for allocation to open source hardware projects."* The FAQ adds: *"The VID we were
gifted was procured from USB-IF by a company that has since ceased trading, and they did so
before USB-IF's terms prohibited sublicense or transferring of VIDs or PIDs."* PIDs `0x1000`–`0x1FFF`
are reserved for **InterBiometrics**, *"the original owner of this VID"* — which answers the
brief's InterBiometrics question directly. `0x0000`–`0x0FFF` are reserved for common tasks.

**USB-IF relationship.** FAQ, verbatim: *"No, pid.codes is in no way supported, endorsed by, or
associated with USB-IF."* No certification, no logo rights, and an explicitly contested legal
position (*"It is our belief that USB-IF has no legitimate right to prohibit this activity"*).
The record's rejected-route table should state this plainly — it is the honest cost of the route.

**Prerequisites — and Firestarter does not meet them yet.** From `howto.md` §0, verbatim:

> If your project does not meet the following criteria, your pull request **will** be rejected:
> - Publicly available source code repository…
> - Containing modifiable PCB design files (schematics and layout) and/or source code for a device with a USB interface…
> - Licensed under a recognized open source or open source hardware license. … Your source code repository must contain a LICENSE file attesting to this fact.
>
> If your project involves both hardware and software, both need to be licensed under recognised OSS and OSHW licenses.

**This is a sequencing finding D-08 does not account for.** Firestarter's firmware is public and
MIT-licensed, so the software leg is satisfiable. The hardware leg is not: no schematic exists,
which is the phase's entire premise. `howto.md` says *"If your project doesn't yet meet these
requirements, please hold off requesting a PID until it does."* Read strictly, the operator
follow-up D-08 tracks **cannot be filed until a schematic exists** — putting the PID allocation
downstream of the very board the ship gate is meant to protect. The record must state this
ordering; otherwise D-09's gate reads as satisfiable-any-time when it is not.

(A softening: the FAQ says *"My project isn't out yet, can I still get a PID? Yes, absolutely.
You need to have created a repository for your source code somewhere, with your work so far."*
The howto's PCB-files clause and the FAQ's softer line are in mild tension; the maintainers
resolve it case by case. Confidence that a firmware-only request would be accepted: **LOW**.)

**Mechanics.** Fork `pidcodes/pidcodes.github.com`; add `org/<name>/index.md`
(`layout: org`, `title`, optional `site`); pick an unused PID outside the reserved ranges; add
`1209/<pid>/index.md` with `layout: pid`, `title`, `owner`, `license`, `site`, `source`.
*"For license, you must name a valid open-source license; pull requests that do not have this
field filled out correctly will be rejected."* Then open a PR. *"PIDs are allocated in the order
pull requests are submitted."*

**The interim option CONTEXT.md does not consider — `1209:0001`.** `1209/0001/index.md`, verbatim:

> This PID is reserved for use in private testing. Anyone may assign it to their device while
> they're testing in-house, but it MUST NOT be used on any device that will be redistributed,
> sold, or manufactured. Source code and configuration that references this VID/PID should warn
> users that the PID is not universally unique and should not be used outside test environments.

This maps onto Firestarter's situation exactly, and it is strictly better than the status quo:
it replaces *another company's registered identity* with *an identity explicitly sanctioned for
this use*, and it comes with a warning obligation the record can adopt verbatim. It does **not**
weaken D-09's ship gate — the test PID's own terms forbid shipping — so the gate survives intact
while the placeholder stops impersonating Puya. **Recommended: the record should name
`1209:0001` as the interim identity and `1209:<allocated>` as the target.** Adopting it in
`usb_cdc.c` remains out of scope (D-06); this is a recorded decision plus an obligation, same as
D-06 already prescribes for the real PID.

**Rejected-route table material** (FAQ §"My project isn't OSH-licensed"): vendor PID programs at
Espressif, NXP, Microchip, Nordic, Silabs, FTDI — none applicable to a Puya part, which is itself
a finding for the table. USB-IF's own price is quoted on pid.codes' front page as **$6000** for a
unique Vendor ID.

### F-7 — pid.codes allocation latency: measured, and it undercuts D-09 *(HIGH — GitHub API, 2026-08-02)*

| Measurement | Value |
|---|---|
| Open PRs | **64** |
| Oldest open PR | **#1156, opened 2026-01-20** (194 days) |
| Most recent commit to `master` | **2026-04-29** |
| Time since last merge | **95 days** |
| Merge activity by month | 2026-01: 25 · 2026-02: 52 · 2026-03: 5 · 2026-04: 18 · 2026-05 → 2026-08: **0** |

The registry merges in bursts and is currently in a long quiet period. **D-09's gate — "no board
ships until a real PID is allocated" — is therefore gated on a volunteer review queue with no SLA
and no merge in three months.** That is not a reason to abandon the gate; it *is* a reason the
record must (a) state the latency, (b) name `1209:0001` as the interim identity so the project is
never blocked on the queue merely to test, and (c) tell the operator to file early. The record
should treat "file the PR" and "receive the PID" as two separately-tracked events.

### F-8 — Crystal-less USB and the HSE footprint *(HIGH on documentation and on the in-tree config; [UNVERIFIED-UNTIL-SILICON] on operation)*

PCB-02's fourth item ("a depopulated HSE footprint as a crystal-less-USB hedge") is **not** in the
seed's five PCB requirements — it originates in `ROADMAP.md` criterion 2. It is nonetheless
well-founded:

1. **The port already runs crystal-less.** `platform/py32f071/src/main.cpp:28` sets
   `oscillator.HSEState = RCC_HSE_OFF`, and derives the USB-required 48 MHz from
   `HSI @ 24 MHz × PLL_MUL2` with `PLLSource = RCC_PLLSOURCE_HSI`. [VERIFIED: in-tree source]
2. **Puya's own factory bootloader does the same.** UM1504 Table 1-1: `RCC(MHz) = PLL_48 (HSI_24 x 2)`.
   So the DFU recovery path also needs no crystal. [CITED: UM1504 §1.1]
3. **The silicon has a trim mechanism for it.** Datasheet §2.19 "Clock check system (CTC)":
   *"The CTC module calibrates the HSI clock frequency … as the clock source of the USBD module"*,
   with *"Three external reference sources: GPIO, LSE clock, USBD_SOF."* Trimming HSI against USB
   Start-of-Frame is the standard crystal-less-USB mechanism. [CITED: Datasheet Rev 0.7 EN §2.19, p.23]
4. The SDK ships a working CTC example (`Example/CTC/CTC_Autotrim`), though it demonstrates the
   **LSE** reference, not `USBD_SOF`. So `USBD_SOF` trimming is documented but not exemplified.
   **Confidence that untrimmed HSI meets USB full-speed tolerance: LOW.** The hedge is correct.

**PCB consequence to record:** the footprint is a hedge, so lay out the HSE crystal + its two load
capacitors and leave them **depopulated**, with the HSE pins otherwise unused. Retrofitting a
crystal to a board with no footprint is a respin; depopulating one costs two unplaced parts.
Note the HSE pins are also GPIO — assigning them to anything else forecloses the hedge, which is
the actual unrecoverable decision here.

### F-9 — SWD pads *(HIGH — datasheet)*

PA13 = `SWDIO`, PA14 = `SWCLK`. Datasheet p.44 note 2: *"After reset, PA13 and PA14 are configured
as SWDIO and SWCLK AF functions, the former has an internal pull-up resistor and the latter has an
internal pull-down."* Both carry alternate functions (PA13: `USART1_RX`, `COMP3_OUT`, `PVD_OUT`,
`IROUT`; PA14: `USART2_TX`, `USART1_TX`, `PVD_OUT`) — so **reassigning them is possible and would
foreclose the last-resort recovery path**, which is precisely the unrecoverable-after-layout
decision PCB-02's second item guards. `nRST` is a dedicated pin *"with internal weak pull-up"*
(datasheet p.31). A usable SWD header needs SWDIO, SWCLK, GND, VDD-sense, and — given F-5's
nBOOT1 hazard — **nRST**, which is what makes recovery from a bad option-byte state possible.

### F-10 — **NEW REQUIREMENT: the contiguous PB0–PB7 data bus is a package-selection constraint** *(HIGH — datasheet pin table)*

This is not in CONTEXT.md, the seed, or the ROADMAP, and it is unrecoverable after layout in the
strongest possible sense — it is unrecoverable after *part selection*.

Datasheet pin-definition table, package columns in order
`LQFP64 R1 · CSP64 R1 · LQFP48 C1 · QFN64 R1 · QFN56 P1 · QFN48 C1 · QFN32 K1`
(`-` = not bonded):

| Pin | LQFP64 | CSP64 | LQFP48 | QFN64 | QFN56 | QFN48 | QFN32 |
|---|---|---|---|---|---|---|---|
| PB0 | 26 | D6 | 18 | 26 | 22 | 18 | 14 |
| PB1 | 27 | C7 | 19 | 27 | 23 | 19 | 15 |
| PB2 | 28 | D7 | 20 | 28 | 24 | 20 | **–** |
| PB3 | 55 | D1 | 39 | 55 | **–** | 39 | **–** |
| PB4 | 56 | D3 | 40 | 56 | **–** | 40 | 26 |
| PB5 | 57 | E1 | 41 | 57 | **–** | 41 | 27 |
| PB6 | 58 | E3 | 42 | 58 | **–** | 42 | 28 |
| PB7 | 59 | E2 | 43 | 59 | **–** | 43 | 29 |

**QFN56 (P1) and QFN32 (K1) cannot carry a PB0–PB7 contiguous bus at all.** QFN56 additionally
lacks `PF8-BOOT0` (F-5). Combined with the control pins (PA0–PA5, all present on all seven
packages) and USB (PA11/PA12, F-11):

> **Viable packages for this design: LQFP64, CSP64, QFN64, LQFP48, QFN48. Ruled out: QFN56, QFN32.**

The one-snapshot `IDR` read and atomic `BSRR` write design that `platform/py32f071/README.md`
describes depends on the eight data lines sharing one port in one contiguous nibble-aligned run;
losing PB2 or PB3 forces either a split-port bus (two reads, two writes — no longer atomic) or a
non-contiguous shift-and-mask. **PCB-02's third line item should therefore be written as a
package-selection row, not only a pin-assignment row**, with the ruled-out packages named.
This is exactly the D-16 shape: one line of rationale, one line of what breaks.

### F-11 — USB pins and the connector *(HIGH — datasheet + UM1504)*

`PA11 = USB_DM`, `PA12 = USB_DP`, both typed `COM_U` = *"GPIO 5V tolerant with USB PHY function"*
(datasheet p.31). Present on all seven packages (PA11: `44 A3 32 44 39 32 21`; PA12:
`45 B3 33 45 40 33 22`). UM1504 Table 1-1 independently confirms `USB_DM: PA11 / USB_DP: PA12`
for the factory bootloader — so **the DFU recovery path and the application path use the same two
pins**, and there is no remap to consider.

**On D-14's "USB connector and D+ pullup":** I could **not** determine from the datasheet, the
CMSIS device header (`USBD_TypeDef` exposes `CR/INTR/INTRE/FRAME/EP0CSR/INEPxCSR/OUTEPxCSR/OUTCOUNT/FIFODATA[16]`
— no obviously-named pull-up control), or the CherryUSB `usb_dc_py32.c` port whether the part has
an **internal, software-controlled D+ pull-up** (the `BCDR.DPPU` equivalent). This is answerable
only from the PY32F07X RM's USB chapter, which I could not obtain. **Confidence: LOW / unresolved.**
The record should list "confirm whether a discrete 1.5 kΩ D+ pull-up to 3V3 is required, or
whether the PHY provides it" as an explicit open item — a board that needs one and omits it does
not enumerate at all, and a board that fits one where the PHY already has one enumerates as
low-speed or not at all. This is a textbook unrecoverable-after-layout item and it deserves a
checklist row of its own with the uncertainty stated. See Open Question 2.

### F-12 — PCB-05's factual premises, all confirmed *(HIGH — measured in the files)*

| CONTEXT.md claim | Verdict | Evidence |
|---|---|---|
| `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` says **nothing** about the socket | **TRUE** | 299 lines; the only `socket`/`remove`/`chip` matches are lines 128, 150, 296, all about removing the *button dance*, none about a seated device |
| `py32_dfu.py:441` — discovery is by interface class `0xFE/0x01`, not VID/PID | **TRUE, exact line** | `find_dfu_interfaces` docstring at line 441: *"Discovery is by **interface class** (0xFE/0x01), not by VID/PID, because the USB ID the Puya bootloader presents is not confirmed yet."* Worth recording in the VID/PID section as CONTEXT.md asks — nobody should read PCB-04 as a host bug |
| `usb_cdc.c` placeholder at lines 20 and 24 | **TRUE, exact lines** | `:19 #ifndef` / `:20 #define FIRESTARTER_USB_VID 0x36B7U` / `:23 #ifndef` / `:24 #define FIRESTARTER_USB_PID 0xFFFFU`; consumed at `:35`/`:36` inside `USB_DEVICE_DESCRIPTOR_INIT`. (CONTEXT.md's canonical-ref cites the span as `19-36`, which is right.) |
| Seed frontmatter | **TRUE** | `status: dormant`; `trigger_condition: v1.28 PY32F071 Port is activated, OR the first PY32F071 PCB/schematic is specified — whichever comes first, because this decision imposes PCB requirements`; `planted_date: 2026-07-28`. D-17's premise holds: the first disjunct has fired. |
| `README.md` §"Provisional example pin map" and §"Hardware validation still required" exist | **TRUE** | Both present; the map is PB0–PB7 data, PA0/PA1 latch strobes, PA2 `/OE`, PA3 control-latch, PA4 VPP/ADC ch4, PA5 `/CE`, no button; guarded by `RURP_PY32F071_PINMAP_PROVISIONAL 1` |

### F-13 — Why the socket warning is stronger here *(HIGH — derived from in-tree facts)*

PCB-05 requires the record to state *why*. The materials:

- **The pin map is provisional by declaration.** `README.md`: *"All other assignments are
  placeholders selected for a simple contiguous bus and must not be treated as verified PCB
  wiring."* The board header defines `RURP_PY32F071_PINMAP_PROVISIONAL 1` as a marker.
- **The specific hazard is direction, not just identity.** A provisional map can assign a signal
  the wrong *direction*. If a pin the real board wires to a PROM output is configured as a
  push-pull output by the firmware, seating a chip creates a driver-fight through the PROM's
  output stage — which destroys parts, silently, on first power-up. This is qualitatively worse
  than the AVR comparable, where the pin map has been bench-validated across three board
  revisions since v1.0.
- **The startup levels are asserted but unproven.** `README.md` lists *"safe active-low `/CE` and
  `/OE` startup levels"* as implemented and then, three sections later, lists validating those
  same startup levels as *"still required"*. The record should note that tension rather than pick
  a side: the code intends safety; nothing has measured it.
- **The firmware-install path makes it acute.** DFU flashing power-cycles and re-enumerates the
  board with `BOOT0` strapped high — a state in which the application's GPIO initialisation never
  runs at all, so whatever the factory bootloader leaves the pins in is what a seated chip sees.
  Neither the application's "safe startup levels" nor any Firestarter code is in control during
  a DFU install.
- **The comparable text** is `README.md` §"Hardware validation still required" (*"Before
  connecting a PROM or applying programming voltage, validate…"*), which is a validation
  instruction, not an install-time safety instruction. It is the nearest existing text and the
  natural anchor.

### F-14 — Where a D-03 gate can live, and how it fails open *(HIGH — measured)*

**The meta repo has no test runner.** It tracks `.devcontainer`, `.github`, `.planning`, `CLAUDE.md`,
`tools/` and the two gitlinks. `.planning/` contains ad-hoc per-phase Python checkers
(`123-…/check_permitted_claims.py`, `120-…/check_note_append_only.py`,
`.planning/v1.16/ledger/tools/check_ledger.py`) but no suite and no CI that runs them.
**So the gate must live in the firmware repo**, which has 21 pytest modules under `tests/`.

**The firmware suite does not run on this branch.** `pytest tests/ -v` appears only in
`build.yml` (push/PR to `main`) and `beta-build.yml` (push to `beta`). `py32f071.yml` — the only
workflow that fires on this milestone branch — has **no pytest step**. `test_config_storage_design_vendored.py`
records this in its own docstring: *"This module executes in NO CI leg on this branch … The local
run recorded in this phase's evidence artifact is the only evidence this module's assertions were
ever exercised."* Phase 126 accepted that disposition for the directly analogous gate; Phase 129
should too, **and say so in the same words** rather than implying CI coverage.

**The specific fail-open exposure, which is worse than the app↔firmware case.** The app and
firmware repos are *siblings*, so `fw_presence.py` can key on `../firestarter/.git` — a marker no
in-repo rename can move. Here the relationship is different: `.planning/` lives in the **superproject**
that contains `firestarter` as a submodule. From the firmware repo root the meta record is at
`../.planning/…`, which resolves in this devcontainer and **does not exist** under
`actions/checkout` of `henols/firestarter` — where `../` is the runner work directory. A gate
written the obvious way therefore reports "meta repo absent → skip" at exit 0 in any CI leg that
ever does run it, which is A-7's measured failure shape exactly.

**Failure modes a planted-violation fixture must actually prove.** Not one RED, but five:

| # | Failure mode | What the fixture must show |
|---|---|---|
| 1 | Section content diverges between the two copies | RED on a mutated copy — the classic case |
| 2 | A regex/parse returns empty and the comparison passes on two empty strings | A **separate** non-vacuity assertion per parse (the 128-09 `D-09` pattern) |
| 3 | Meta repo absent → SKIP at exit 0 with a false reason | Presence keyed on a marker that cannot be renamed away (`../.planning/REQUIREMENTS.md` is a *file* and is renameable; prefer the meta `.git` directory or a `FIRESTARTER_META_ROOT` env seam mirroring `FIRESTARTER_FW_ROOT`), **and** a present-repo-but-missing-target case that raises rather than skips |
| 4 | Section heading renamed on one side → the extractor finds nothing → vacuous pass | Covered by #2, but needs its own RED because the empty string arrives from a different path |
| 5 | Dirty sibling tree makes the gate red for an unrelated reason | Assert `git status --porcelain` clean on the sibling before trusting a parse (the 128-09 / F-16 pattern) |

Failure mode 3 is the one this milestone has paid for repeatedly and the one a naive
implementation will reproduce. `firestarter_app/tests/fw_presence.py` is the template: **repo
presence decided once from an unrenameable marker; a missing scan target under a present repo is
a hard `MissingScanTargetError`, never a skip.** Its docstring also records a trap the planner
must not step in: `FW_ROOT`/`requires_fw` bind at import and at collection, so `monkeypatch.setenv`
has no effect — a test that needs a different root must invoke pytest in a **subprocess**.

**Recommended siting:** `firestarter/tests/test_flash_path_record_sync.py`, with a
`firestarter/tests/meta_presence.py` helper mirroring `fw_presence.py`. Note there is no
`conftest.py` anywhere in the firmware repo and no `pytest.ini`/`pyproject.toml`/`setup.cfg`/`tox.ini`
— path resolution is done per-module by house convention, stdlib + pytest only, no third-party
import and nothing under `.pio/` (a `.pio/libdeps` dependency passes warm and fails cold — the
A-7 shape again).

### F-15 — Document-shape precedent *(HIGH — read from the files)*

**Naming.** Existing milestone-prefixed decision docs: `v1.9-COBS-DECISION.md`,
`v1.10-FRAMING-DECISION.md`, `v1.13-PROTOCOL-ENUMERATION.md`, `v1.7-SHIELD-REVS.md`. All are
`SCREAMING-KEBAB`, at `.planning/` root, no numbering. Under this convention a Phase 129 file
would be **`.planning/v1.23-FLASH-PATH-DECISION.md`** (or `…-PCB-REQUIREMENTS.md`; the flash-path
half is the one the seed and FUT-N05 point at, so the former reads better as canonical).

**Section skeleton — `v1.9-COBS-DECISION.md`** (the closest ADR-shaped precedent):
`1. Context` (with numbered sub-findings, each carrying an inline confidence tag) →
`2. Decision` (incl. a `Revision Note` recording a changed position, and a `Rationale summary`) →
`3. Consequences` (`What stays the same` / `Future path if…`) → `4. Candidate Survey` (per-option
subsections + a `Comparative Verdict Table`) → `5. Open Questions for Future Milestone`.
That maps onto Phase 129 almost one-to-one: Context → the flash map and silicon facts; Decision →
the three tiers; Consequences → the PCB checklist; Candidate Survey → the rejected-route table;
Open Questions → D-15 and the unresolved items here.

**`v1.7-SHIELD-REVS.md`** (the two-layered precedent) is instead an inventory shape:
`Summary` → numbered inventory/difference/matrix sections → per-topic tables. Its value to D-01 is
the *layering* pattern, not its section list.

**The firmware-layer shape is already established one phase ago:**
`platform/py32f071/CONFIG-STORAGE.md` — a single-file commit in exactly the directory D-01
specifies, opening with `# <Title> — Design Record` / `**Phase N Plan NN. Requirements: X, Y.**`,
then topic sections, and closing with a `## Claim ceiling` section that defers to
`REQUIREMENTS.md` §"Validation Ceiling" **by reference rather than restating it**. Phase 129's
firmware subset should reuse that opening and that closing verbatim in form.

**Confidence discipline — the Claude's-Discretion question is already answered by precedent.**
`v1.9-COBS-DECISION.md` uses **per-claim inline tags**, in section headings and mid-sentence:
`[VERIFIED]`, `[VERIFIED: <specific evidence>]`, `[CITED: <path>]`, `[ASSUMED — <reason>]`.
Measured across the four precedent docs: 12 `[VERIFIED…]`, 1 `[CITED: …]`, 1 `[ASSUMED — …]`.
**Recommendation: adopt that vocabulary, add `[UNVERIFIED-UNTIL-SILICON]` as a fifth tag**, and
keep the blanket `## Claim ceiling` section as well — per-claim tags and a blanket ceiling are
complements, not alternatives, and `CONFIG-STORAGE.md` already carries the blanket half.
CLOSE-02's honesty ledger consumes per-claim pairs, so per-claim tagging is what makes Phase 130
cheap.

### F-16 — The seed's five PCB requirements vs PCB-02's four *(HIGH — read from the files)*

They are not the same list, and the planner should not assume they are:

| Seed item | Maps to |
|---|---|
| 1. BOOT0/nBOOT1 strapping reachable | PCB-02 item 1 |
| 2. SWD pads exposed | PCB-02 item 2 |
| 3. Contiguous 8-bit GPIO port (PB0–PB7; *"confirm against the final package and pin multiplexing"*) | PCB-02 item 3 — **and the seed already anticipated F-10** |
| 4. Flash budget fits 128 KiB | **PCB-03**, not PCB-02 |
| 5. Reboot-into-bootloader: protocol command vs strap-only | **D-15's open question** |
| *(absent)* | PCB-02 item 4, the depopulated HSE footprint — originates in `ROADMAP.md` criterion 2 (F-8) |

The seed's item 3 parenthetical — *"confirm against the final package and pin multiplexing"* — is
the exact instruction F-10 discharges. The record should close that loop by name.

### F-17 — Datasheet §2.3 undersells the bootloader *(MEDIUM — a documentation inconsistency worth noting)*

Datasheet Rev 0.7 §2.3: *"The Boot loader is located in the System memory and is used to download
the Flash program through the **USART** interface."* UM1504 documents USB DFU for PY32F071/F072/F403
and the whole host DFU path depends on it. The datasheet is incomplete here; **UM1504 is the
authority for the USB DFU capability.** Worth one line in the record so a future reader who checks
the datasheet first does not conclude the DFU path is imaginary.

Relatedly, UM1504 Table 1-1's `PID` column (`0x0448` for PY32F071/F072) is a **bootstrap-program
device ID**, sitting alongside a separate `BL ID` (`0xA0`) column — it is not a USB `idProduct`.
`REQUIREMENTS.md` §"Out of Scope" already says exactly this (*"`0x0448` is a bootloader-table
device ID, **not** a confirmed USB PID"*), and this research **confirms that note is correct**
against the primary source.

---

## Standard Stack

No libraries are introduced. The phase's "stack" is the toolchain used to produce evidence.

### Core

| Tool | Version | Purpose | Why |
|---|---|---|---|
| `arm-none-eabi-gcc` | 14.2.1 (Debian `15:14.2.rel1-1`) | Local ARM build for D-13's byte-identity proof | Same apt package CI uses; **proven working in this devcontainer** (C-3) |
| `libnewlib-arm-none-eabi` + `libstdc++-arm-none-eabi-newlib` | 4.5.0 / 15:14.2.rel1-1+29 | C/C++ headers for the ARM target | **Not in the CI action's install list**; without them every C++ TU fails on `<string.h>` |
| `cmake` | 4.4.0 (pip) | Configure the py32f071 target | `platform/py32f071/CMakeLists.txt` requires ≥ 3.20 |
| `ninja` | 1.13.0 (pip) | Build generator | The documented generator |
| `pytest` | repo default (stdlib + pytest only) | D-03 sync gate | The firmware repo's 21 existing test modules use no other dependency |

### Supporting

| Tool | Purpose | When |
|---|---|---|
| `sha256sum` | Byte-identity evidence for D-13 | Before and after the linker edit |
| `arm-none-eabi-size` | Size delta evidence | Same |
| `git status --porcelain` | Sibling-tree-clean guard in the gate | Failure mode 5 (F-14) |

**Installation (reproduces C-3 exactly):**
```bash
sudo apt-get install -y --no-install-recommends \
    gcc-arm-none-eabi binutils-arm-none-eabi \
    libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib
pip install cmake ninja
cmake -S platform/py32f071 -B build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build/py32f071
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Local ARM build (C-3) | Comment-stripped-diff argument, no build | D-13 permits it, but it is strictly weaker and the strong option now costs one apt install |
| Local ARM build | Operator-gated CI run | **Forbidden by D-13** and by the standing no-`gh workflow run` rule |
| pytest gate in firmware repo | Ad-hoc checker script under `.planning/phases/129-…/` | Precedent exists (Phases 120/122/123) but nothing ever re-runs it; the firmware `tests/` module is at least discoverable by `pytest tests/` |
| `1209:0001` interim identity (F-6) | Keep `36B7:FFFF` | Keeping it means shipping Puya's registered identity (C-2) |

---

## Package Legitimacy Audit

**Not applicable — this phase installs no packages into either repository.** No dependency is
added to `platform/py32f071/CMakeLists.txt`, `platformio.ini`, or any `requirements`/`pyproject`
file. The toolchain packages in §"Standard Stack" are **developer-environment** installs from
Debian's official archive and the pinned SDK is unchanged
(`GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2`, re-verified by SHA this session).

Packages removed due to `[SLOP]` verdict: **none**.
Packages flagged `[SUS]`: **none**.

---

## Architecture Patterns

### Document topology

```
                       .planning/v1.23-FLASH-PATH-DECISION.md          [meta, AUTHORITATIVE]
                       ├── Context: flash map (F-1), silicon facts (F-5/8/9/10/11)
                       ├── Decision: three tiers (PCB-01)
                       ├── PCB checklist (PCB-02, D-14/D-16)        ─┐
                       ├── Flash budget + migration cost (PCB-03)   ─┤ SHARED
                       ├── VID/PID decision + ship gate (PCB-04)    ─┤ SECTIONS
                       ├── Socket-empty instruction (PCB-05)        ─┘
                       ├── Rejected-route table            [meta only]
                       ├── Full rationale                  [meta only]
                       └── Open questions + claim ceiling
                                    │
                          fail-closed sync gate (D-03)
                          firestarter/tests/test_flash_path_record_sync.py
                          + tests/meta_presence.py   ← unrenameable marker (F-14 mode 3)
                                    │
    firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md              [firmware, SUBSET]
                       └── the four SHARED sections only
                                    ▲
                                    │ comment cross-reference (D-11)
                       linker/PY32F071xB_FLASH.ld  BOOTLOADER block
                                    │
                                    └── also: fix "on a part with no VTOR" (C-1)

    .planning/seeds/py32f071-no-external-tool-fw-install.md
                       └── frontmatter status → points at the record (D-17/D-18)
```

### Pattern 1 — Subset-parity gate with per-parse non-vacuity

**What:** extract the shared sections from both copies by heading span; assert each extraction is
non-empty *in its own test*; then assert equality; then a planted-mutation RED.
**When:** D-03.
**Example** (shape from `firestarter_app/tests/test_py32_asset_name_host.py`, Phase 128 `cc9452f`):

```python
# Source: firestarter_app/tests/test_py32_asset_name_host.py (Phase 128 Plan 09, D-09)
def test_meta_extract_is_non_vacuous():          # separate test, no comparison
    assert _sections(META_DOC.read_text())       # one non-vacuity assertion per parse

def test_fw_extract_is_non_vacuous():
    assert _sections(FW_DOC.read_text())

def test_shared_sections_match():
    assert _sections(META_DOC.read_text()) == _sections(FW_DOC.read_text())

def test_planted_mutation_is_detected(tmp_path):  # the RED
    mutated = tmp_path / "m.md"
    mutated.write_text(FW_DOC.read_text().replace("24 KiB", "8 KiB"))
    assert _sections(mutated.read_text()) != _sections(META_DOC.read_text())
    assert _git_porcelain(FW_ROOT) == ""          # real tree untouched
```

### Pattern 2 — Presence keyed on an unrenameable marker

```python
# Source: firestarter_app/tests/fw_presence.py (Phase 123 Plan 07, BASE-02/D-09/D-11/D-12)
# 1. Repo presence decided ONCE, from a marker no in-repo rename can move.
# 2. A missing scan target under a PRESENT repo is a hard error, never a skip.
META_ROOT = Path(os.environ.get("FIRESTARTER_META_ROOT", _default_meta_root()))
META_MARKER = META_ROOT / ".git"          # not a file that a rename can move
META_PRESENT = META_MARKER.exists()

def meta_file(rel: str) -> Path:
    p = META_ROOT / rel
    if not p.exists():
        raise MissingScanTargetError(f"meta repo present but {p} missing")
    return p
```
**Trap:** these bind at import/collection. `monkeypatch.setenv` has no effect — a test needing a
different root must run pytest in a **subprocess** with the env var set.

### Pattern 3 — Local byte-identity evidence (D-13)

```bash
cmake --build "$B" && sha256sum "$B"/firestarter_py32f071.{bin,hex} > before.txt
# apply the comment-only edit
cmake --build "$B" && sha256sum "$B"/firestarter_py32f071.{bin,hex} > after.txt
diff before.txt after.txt      # must be empty
```
`LINK_DEPENDS` on the linker script guarantees the relink actually happens — otherwise the
comparison is vacuous. Verified during this research (C-3).

### Anti-Patterns to Avoid

- **Enumerating the no-VTOR mitigations as live candidates.** C-1. Writing a SYSCFG `MEM_MODE` /
  RAM-vector-copy / trampoline survey into the record would document a problem this part does not
  have and mislead FUT-N05's implementer.
- **Calling `0x36B7` unallocated.** C-2. It is Puya's.
- **A gate that skips when the meta repo is absent.** F-14 mode 3 — the measured A-7 shape.
- **Comparing a local ARM size figure to a CI one.** C-3(a). Delta claims only.
- **A bootloader figure without its migration cost.** D-10, and the linker comment's own standard.
- **Ticking PCB-0x from any plan but the last.** The Phase 116 4× premature-tick guard, restated
  in Phases 125 and 126; every non-closing plan must be told explicitly.
- **Quoting a forbidden phrase inside a compliance paragraph.** The Phase 125 self-reference trap —
  a `NONREGRESSION.md` that quotes the claim-ceiling's forbidden phrases trips the claim gate when
  scanned directly.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Sibling-repo presence detection | A bespoke `if not (root/"X.md").exists(): skip` | The `fw_presence.py` pattern (unrenameable marker + hard error on missing target) | A-7 measured five legs flipping PASS→SKIP at exit 0 with a false reason |
| Doc-section content gate | A fresh regex-and-compare module | `tests/test_config_storage_design_vendored.py`'s single-helper shape — one module-level `_find_violations(text)` driven by both the positive tests and the RED | Two parallel implementations drift; the RED then stops proving anything about the positive path |
| Three-way string binding | Ad-hoc equality | `test_py32_asset_name_host.py`'s per-parse non-vacuity + planted mutation + porcelain guard | Phases 118 and 124 each shipped a gate that passed without observing anything and had to be unwound |
| A USB vendor identity | Picking an unused-looking VID | pid.codes `0x1209` (F-6), with `1209:0001` in the interim | C-2 is what picking-something-plausible already produced once |
| Vector relocation on this part | A remap/trampoline scheme | `SCB->VTOR` — already written every boot by the compiled `SystemInit` | C-1 |
| Boot-mode facts | STM32F0 lore | Datasheet Rev 0.7 §2.3 Table 2-1 + UM1504 §3 Table 3-1 | The parts are similar, not identical; this project has been burned by sibling-part assumptions before |

**Key insight:** every gate this milestone has had to unwind failed the same way — it never
observed anything, and nothing proved that it could. The planted-violation fixture is not
ceremony; it is the only thing separating a gate from a comment.

---

## Common Pitfalls

### Pitfall 1 — Writing "no VTOR" into the record because four upstream documents say it
**What goes wrong:** the record — the most durable artifact this milestone produces, aimed at a
future schematic author and a future bootloader implementer — states a falsehood about the part.
**Why:** CONTEXT.md D-12, `REQUIREMENTS.md` PCB-03, `ROADMAP.md` criterion 3, `FUT-N04` and the
linker comment all repeat it, so it reads as settled.
**Avoid:** C-1's three in-tree proofs. Escalate before writing; correct the linker comment in the
edit D-11 already opens.
**Warning sign:** a draft section enumerating `SYSCFG MEM_MODE`.

### Pitfall 2 — The sync gate that skips
**What goes wrong:** `../.planning` does not exist under `actions/checkout`; the gate reports
"meta absent", skips, exits 0, and the two copies drift silently.
**Avoid:** F-14's five failure modes, all fixtured. Prefer an env seam (`FIRESTARTER_META_ROOT`)
exercised in a **subprocess**.
**Warning sign:** any `pytest.skip` whose reason mentions the meta repo, with no corresponding
hard-error path for present-repo-missing-target.

### Pitfall 3 — Claiming CI coverage the branch does not have
**What goes wrong:** the record implies the gate runs in CI. It does not: `py32f071.yml` is the
only workflow firing on this branch and it has no pytest step (F-14).
**Avoid:** copy `test_config_storage_design_vendored.py`'s docstring disposition verbatim in form.

### Pitfall 4 — A vacuous byte-identity proof
**What goes wrong:** the "rebuild" no-ops, so identical hashes prove nothing.
**Avoid:** confirm the link step re-ran (`LINK_DEPENDS` does bind the linker script — verified),
and record the build log line, not just the hashes.

### Pitfall 5 — The Phase 125 self-reference trap
**What goes wrong:** `129-NONREGRESSION.md` quotes the claim-ceiling's forbidden phrases inside
its own compliance paragraph and the claim gate, scanning directly, trips.
**Avoid:** refer to forbidden phrases by reference; do not reproduce them. `CONFIG-STORAGE.md`
§"Claim ceiling" models this (*"defers to that list by reference rather than restating its wording"*).

### Pitfall 6 — Premature requirement ticks
**What goes wrong:** four occurrences in Phase 116 alone; restated as a standing guard in 125/126.
**Avoid:** name the allowed IDs when dispatching each plan; only the closing plan may tick
PCB-01…PCB-05, and every other plan is told so explicitly.

### Pitfall 7 — `gsd-tools query commit` switching branches
**What goes wrong:** an unanchored `##…vX.Y` regex scrapes ROADMAP prose and the commit lands on
another branch.
**Avoid:** check `git rev-parse --abbrev-ref HEAD` in all three repos before and after any commit
step. Relevant here because D-05 bumps gitlinks in-phase.

### Pitfall 8 — Believing `--auto`/`--chain` respects an outward-facing gate
**What goes wrong:** they auto-approve human-verify checkpoints. `autonomous: false` is not
self-protecting.
**Avoid:** structural separation — D-08's pid.codes PR and any push stay entirely outside the
plan graph, not behind a checkpoint task.

---

## Runtime State Inventory

Not a rename/refactor/migration phase in the runtime sense, but the categories are answered
because the phase does mutate persistent planning state.

| Category | Items Found | Action Required |
|---|---|---|
| Stored data | **None.** No database, no device state, no `~/.firestarter/` interaction. Verified: the phase writes only `.md` files and one linker comment. | none |
| Live service config | **None.** No CI workflow, no external service. `py32f071.yml`/`beta-build.yml`/`build.yml` are untouched — and note none of them would fire on this branch for a `.md` change anyway (`build.yml`/`beta-build.yml` carry `paths-ignore: ['**.md', …]`). | none |
| OS-registered state | **None.** | none |
| Secrets / env vars | **None** added. If the D-03 gate takes an env seam, `FIRESTARTER_META_ROOT` is a **new name** that must be documented alongside the existing `FIRESTARTER_FW_ROOT` and `FIRESTARTER_SIZE_BASELINE`. | document the new seam |
| Build artifacts | **None invalidated.** C-3 proves the emitted image is byte-identical across the linker-comment edit. The devcontainer now carries an ARM toolchain that was absent before — a *developer-environment* change, not a repo one, and one the Validation Ceiling's wording should be updated to reflect (C-3, Phase 130 CLOSE-01). | note in the record |
| Planning state | `.planning/seeds/py32f071-no-external-tool-fw-install.md` frontmatter `status: dormant` (D-17); meta gitlink for `firestarter` (D-05); `STATE.md` `current_phase`/`last_activity_desc` are hand-edit-only. | D-17 edit; gitlink bump; explicit STATE.md diff |

---

## State of the Art

| Old / recorded | Actual | Impact |
|---|---|---|
| "a part with no VTOR" | `__VTOR_PRESENT 1`; `SCB->VTOR` written every boot by the compiled `SystemInit` | C-1 — rewrites PCB-03's technical content |
| "`0x36B7`/`0xFFFF` unallocated and squatted" | `0x36B7` = Puya Semiconductor; the pair is the pinned SDK's own CDC example | C-2 — rewrites PCB-04's premise, strengthens the gate |
| "`arm-none-eabi-gcc`, `cmake`, `ninja` absent from this environment" | Installable from the same apt packages CI uses; build + byte-identity proof executed | C-3 — upgrades D-13's evidence |
| "a small bootloader in the first few KB" (seed) | ≈ 14.6 KiB of components before any bootloader logic; **3 sectors / 24 KiB** is the defensible reservation | C-4 — supplies D-10's figure |
| pid.codes assumed as a simple free registry | Free and appropriate, **but** requires public PCB design files, and has 64 open PRs with no merge since 2026-04-29 | F-6/F-7 — D-08 sequencing and D-09 risk |
| Data bus "confirm against the final package" (seed item 3, open) | PB0–PB7 impossible on QFN56 and QFN32; five viable packages | F-10 — a new PCB-02 row |

**Superseded by this research:** the seed's "first few KB" figure (C-4) and its open item 3
(discharged by F-10).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | A CDC + COBS self-flash bootloader needs ≈ 17–20 KiB, so **3 sectors / 24 KiB** | F-3 | Over- or under-reserving the bootloader region. Mitigated: the component measurements are real; only the bootloader's own logic is estimated. Puya's 12,032 B HAL-free bootloader is the counter-anchor showing 2 sectors is reachable with effort. |
| A2 | An external pull-down on `PF8-BOOT0` is optional, since the internal one is enabled by default | F-5 | A floating strap net; cheap to fit anyway. Recommend fitting one regardless. |
| A3 | `nBOOT1`'s factory default is `1` (so a virgin part reaches DFU with BOOT0 high) | F-5 | If `0`, `BOOT0 = 1` selects SRAM and DFU is unreachable without SWD. **Unresolved — see Open Question 1.** |
| A4 | The USB PHY may or may not provide the D+ pull-up | F-11 | A board that omits a needed 1.5 kΩ pull-up does not enumerate at all. **Unresolved — see Open Question 2.** |
| A5 | A firmware-only pid.codes request (no PCB files) would likely be declined | F-6 | If accepted, D-08 could be filed immediately and D-09's risk shrinks. Low cost to test — the operator can simply ask. |
| A6 | `1209:0001` is an acceptable interim identity for Firestarter's case | F-6 | Its own terms permit exactly this use, so risk is low; it is a recommendation, not a locked decision. |
| A7 | `.planning/` will be reachable at `../.planning` from the firmware repo whenever the gate runs | F-14 | The gate's whole premise. Mitigated by keying presence on an unrenameable marker + an env seam + a hard error rather than a skip. |
| A8 | CI's `ubuntu-latest` image supplies newlib without the two extra packages | C-3 | Only affects local reproduction instructions; CI demonstrably builds today. |

---

## Open Questions

1. **What is `nBOOT1`'s factory default, and can a bad option-byte value strand a board without SWD?**
   - *Known:* `nBOOT1 = 0` + `BOOT0 = 1` selects SRAM (F-5). `nBOOT1` is an option bit.
   - *Unclear:* the erased/factory value, and whether the DFU tool's own "Option Bytes" write
     (UM1504 §4.3) can set it to `0` and lock the part out of its own recovery path.
   - *Recommendation:* record the hazard, mark the default unresolved, and cite it as the
     strongest justification for PCB-02's SWD-pads row. Answerable from the PY32F07X RM's
     option-byte chapter — already cited in this tree (RM V0.2) but not obtainable this session.

2. **Does PY32F071's USB PHY provide an internal, software-controlled D+ pull-up?**
   - *Known:* PA11/PA12 are typed `COM_U`, *"GPIO 5V tolerant with USB PHY function"*. The CMSIS
     `USBD_TypeDef` exposes no obviously-named pull-up control; the CherryUSB port shows none.
   - *Unclear:* whether a discrete 1.5 kΩ D+ → 3V3 resistor is required on the PCB.
   - *Recommendation:* a checklist row of its own, with the uncertainty stated and "confirm from
     the RM USB chapter before the first schematic" as the action. Do not guess.

3. **Should the record name `1209:0001` as the interim identity (F-6)?**
   - *Known:* it exists precisely for this case and forbids shipping, so D-09's gate survives.
   - *Unclear:* whether the operator wants `usb_cdc.c` touched at all this phase — D-06 says no.
   - *Recommendation:* record the decision, defer the code edit alongside the real PID's (already
     in Deferred Ideas). This is an operator call.

4. **Can the pid.codes PR be filed before a schematic exists (F-6)?**
   - *Known:* `howto.md` requires modifiable PCB design files; the FAQ is softer.
   - *Recommendation:* the record should state the ordering constraint; the operator can email
     `admin@pid.codes` to resolve it cheaply.

5. **Does PCB-03's and criterion 3's literal wording get satisfied, or corrected (C-1)?**
   - Satisfying them literally now requires writing something false. **Operator decision.**
   - *Recommendation:* the record states the corrected fact and explicitly notes that it
     supersedes the requirement's wording; Phase 130's CLOSE-01 sweep amends `REQUIREMENTS.md`
     and `ROADMAP.md`. This keeps the correction visible rather than silent.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| `arm-none-eabi-gcc` | D-13 byte-identity proof | ✓ *(after apt install)* | 14.2.1 | Comment-stripped-diff argument |
| `libnewlib-arm-none-eabi` / `libstdc++-arm-none-eabi-newlib` | ARM C++ compilation | ✓ *(after apt install)* | 4.5.0 / 14.2.1 | none — required |
| `cmake` | ARM configure | ✓ *(pip)* | 4.4.0 | — |
| `ninja` | ARM build | ✓ *(pip)* | 1.13.0 | — |
| `python3` + `pytest` | D-03 gate | ✓ | 3.12 / repo default | — |
| Network to `github.com` | `FetchContent` SDK clone | ✓ | — | Pre-seeded `_deps` |
| Network to `download.py32.org` | Datasheet/UM citations | ✓ | — | Already extracted here |
| `arm-none-eabi-gdb` / debugger | — | ✗ | — | Not needed |
| PY32F071 hardware | Any behavioural claim | ✗ | — | **No fallback — the milestone ceiling** |
| `gh workflow run` | — | **forbidden** | — | Local build (C-3) |

**Missing with no fallback:** PY32F071 silicon. Every behavioural claim stays
`[UNVERIFIED-UNTIL-SILICON]`.
**Missing with fallback:** none blocking.
**Note:** the toolchain packages were installed *during this research*. If executors run in a
fresh container they must re-install them; the plan should carry the command.

---

## Validation Architecture

Test framework and sampling for a documentation phase.

### Test Framework

| Property | Value |
|---|---|
| Framework | `pytest` (firmware repo, `tests/`), stdlib + pytest only |
| Config file | **none** — no `conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg` or `tox.ini` anywhere in the firmware repo. Per-module path resolution is the house convention, recorded in `tests/test_vpp_seam_manual_on_every_board.py`'s docstring. |
| Quick run | `python -m pytest tests/test_flash_path_record_sync.py -v` |
| Full suite | `python -m pytest tests/ -v` |
| CI status | **This module will run in NO CI leg on this branch.** `pytest tests/ -v` exists only in `build.yml` (main) and `beta-build.yml` (beta); `py32f071.yml` — the only workflow firing here — has no pytest step. The local run is the evidence. Same disposition as Phase 126's `test_config_storage_design_vendored.py`, and it must be stated in the module docstring. |

### Phase Requirements → Test Map

| Req | Behavior | Type | Automated command | Exists? |
|---|---|---|---|---|
| PCB-01 | Both copies name all three tiers and the non-retirement sentence | content gate | `pytest tests/test_flash_path_record_sync.py::test_three_tiers_and_non_retirement -x` | ❌ Wave 0 |
| PCB-02 | Every checklist row is a `- [ ]` item with a rationale line and a breaks-if line (D-16); all named items present incl. F-10's package row | structural gate | `…::test_pcb_checklist_rows_are_wellformed -x` | ❌ Wave 0 |
| PCB-03 | The record contains the literal reserved addresses (`0x08000000`, `0x0801E000`, `120K`, `8K`, `256`, `8192`) **and** the bootloader figure never appears without its migration cost within N lines | content + proximity gate | `…::test_flash_budget_cites_reserved_map -x`, `…::test_bootloader_figure_carries_its_cost -x` | ❌ Wave 0 |
| PCB-03 | The linker comment names the record's filename (D-11) and no longer says "no VTOR" (C-1) | cross-file gate | `…::test_linker_comment_cross_references_record -x` | ❌ Wave 0 |
| PCB-03 | The linker-comment edit changes no emitted byte (D-13) | build delta | the `sha256sum` before/after sequence in §Pattern 3 | ✅ proven in C-3 |
| PCB-04 | The record names `0x1209`, the ship gate, and cites `0x36B7`'s Puya provenance | content gate | `…::test_vid_pid_decision_and_ship_gate -x` | ❌ Wave 0 |
| PCB-05 | The socket-empty instruction is present in the firmware copy and states the provisional-pin-map reason | content gate | `…::test_socket_empty_instruction_present -x` | ❌ Wave 0 |
| D-03 | Shared sections are byte-identical between the two copies | parity gate + planted RED | `…::test_shared_sections_match`, `…::test_planted_mutation_is_detected` | ❌ Wave 0 |
| D-03 | The gate cannot pass vacuously or skip silently | 5 REDs (F-14) | `…::test_*_non_vacuous`, `…::test_absent_meta_is_not_a_silent_skip`, `…::test_missing_target_raises` | ❌ Wave 0 |
| D-17 | Seed frontmatter `status:` is no longer `dormant` and points at the record | content gate | grep assertion — **must live meta-side or inside the same firmware module via the meta-presence helper** | ❌ Wave 0 |

**Inherently a human read** (no gate can judge these; they belong in UAT, and CLOSE-02 consumes them):
whether the rationale lines are *useful to a schematic author*; whether the rejected-route table
is *fair*; whether the record's stated edges (connector choice, socket/ZIF, power budget) are the
*right* edges; whether the corrected C-1 framing reads as an honest correction rather than a
retcon.

### Sampling Rate

- **Per task commit:** `python -m pytest tests/test_flash_path_record_sync.py -v`
- **Per wave merge:** `python -m pytest tests/ -v` (21 existing modules + the new one)
- **Phase gate:** full suite green **plus** the C-3 byte-identity sequence re-run on the final
  tree, both recorded in `129-NONREGRESSION.md`, before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `firestarter/tests/test_flash_path_record_sync.py` — the D-03 gate, covering PCB-01…PCB-05 content and the five F-14 failure modes
- [ ] `firestarter/tests/meta_presence.py` — meta-repo presence helper mirroring `firestarter_app/tests/fw_presence.py` (unrenameable marker, `FIRESTARTER_META_ROOT` seam, `MissingScanTargetError`)
- [ ] Toolchain install step for D-13's evidence (§Standard Stack), if executors run in a fresh container
- [ ] No framework install needed — pytest is already used by 21 modules

---

## Security Domain

`security_enforcement` is not disabled in `.planning/config.json`, so this section is included.
The phase adds no runtime code, no network surface, no parser and no data path.

### Applicable ASVS Categories

| Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No auth surface; the phase writes documents |
| V3 Session Management | no | — |
| V4 Access Control | **partially** | D-08's pid.codes PR is an outward-facing, identity-bearing action. Structural separation (no agent files it, no agent pushes) is the control — **not** a checkpoint, because `--auto`/`--chain` auto-approve checkpoints |
| V5 Input Validation | **yes (test-side)** | The D-03 gate parses two documents. Per-parse non-vacuity assertions are the control against a vacuous pass; a parse returning empty must fail, never compare-equal |
| V6 Cryptography | no | `sha256sum` is used for build identity, not as a security primitive. The record must not describe it as one — the same discipline `CONFIG-STORAGE.md` §"CRC32 is not a security primitive" already applies |

### Known Threat Patterns

| Pattern | STRIDE | Mitigation |
|---|---|---|
| **Shipping another company's USB vendor identity** (`0x36B7` = Puya) | **Spoofing** | C-2 + D-09's ship gate; `1209:0001` as the interim identity (F-6) |
| USB PID collision with every other unmodified Puya CDC example | Spoofing / DoS | Same |
| A gate that passes without observing anything | Tampering (undetected) | Planted-violation fixture + per-parse non-vacuity (F-14) |
| An agent performing an outward-facing publish action | Elevation of Privilege | Structural separation; no `git push`, no `gh workflow run`, no PR filing |
| A future reader trusting a false silicon claim in a durable record | Repudiation / Information Disclosure | Per-claim `[…]` tags + `[UNVERIFIED-UNTIL-SILICON]` + the `## Claim ceiling` section |
| Bricking a board via option bytes with no SWD | DoS (physical) | PCB-02's SWD-pads row, justified by Open Question 1 |

---

## Sources

### Primary (HIGH confidence)

- **Pinned PY32F071 SDK** — `OpenPuya/PY32F071_Firmware` @ `0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (the exact `GIT_TAG` in `platform/py32f071/CMakeLists.txt:16`), fetched 2026-08-02:
  - `Drivers/CMSIS/Device/PY32F071/Include/py32f071xB.h:56-59` — `__VTOR_PRESENT 1` (sha256 `08de8dbc…6dd0`, matched against a local copy)
  - `Templates/PY32F071xx_Templates/Src/system_py32f071.c:53-55,139-152` — the `SCB->VTOR` write and `VECT_TAB_OFFSET`
  - `Projects/PY32F071-STK/Applications/USB_Device/USBD_Virtual_COM_Port/Src/usbd_cdc_if.c:9-10` and `pycdc.inf:28,31` — the `0x36b7`/`0xFFFF` origin
  - `Projects/PY32F071-STK/Example/CTC/CTC_Autotrim/readme.txt` — CTC autotrim example
- **Puya, *PY32F071 Datasheet* Rev 0.7 EN**, 78 pp. — §2.3 Table 2-1 (boot modes, p.12), §2.19 (CTC, p.23), §2.25 (USB, p.26), Figs. 3-1/3-2/3-5/3-6 (`PF8-BOOT0`), pin-definition table (pp. 33–44), p.44 notes 2–3 (BOOT0 pull-down; SWD after reset) — https://download.py32.org/Datasheet/en/PY32F071_Datasheet_Rev0.7_EN.pdf, accessed 2026-08-02
- **Puya, *UM1503/UM1504 PY32 DFU Application Software* V1.0 EN**, 9 pp. — §1.1 Table 1-1 (system memory `0x1FFF0000`–`0x1FFF2F00`, USB PA11/PA12, `PLL_48 (HSI_24 x 2)`, `PID 0x0448`, `BL ID 0xA0`), §3 Table 3-1 (boot configuration), §4.3 (option-byte write) — https://download.py32.org/Tool/en/PY32_DfuTool_V1.0.0/UM1503_PY32DfuTool_User%20Manual%20V1.0_EN.pdf, accessed 2026-08-02
- **pid.codes** — https://pid.codes/howto/, https://pid.codes/faq/, https://pid.codes/1209/, and repo sources `howto.md`, `faq.md`, `1209/index.md`, `1209/0001/index.md` at `pidcodes/pidcodes.github.com@master`; PR/commit metadata via the GitHub API — all accessed 2026-08-02
- **Local execution, this session** — ARM build at firmware HEAD `7a0a375` (`text=27260 data=112 bss=5888`); per-object `arm-none-eabi-size`; the D-13 byte-identity before/after sequence
- **In-tree files** at firmware `7a0a375`, app `cc9452f`, meta `33ed9ad` — `linker/PY32F071xB_FLASH.ld`, `CONFIG-STORAGE.md`, `README.md`, `CMakeLists.txt`, `src/main.cpp`, `src/usb_cdc.c`, `.github/actions/build-py32f071/action.yml`, `.github/workflows/*.yml`, `tests/test_config_storage_design_vendored.py`, `firestarter_app/firestarter/py32_dfu.py`, `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md`, `firestarter_app/tests/fw_presence.py`, `firestarter_app/tests/test_py32_asset_name_host.py`, `.planning/v1.7-SHIELD-REVS.md`, `.planning/v1.9-COBS-DECISION.md`, `.planning/seeds/py32f071-no-external-tool-fw-install.md`

### Secondary (MEDIUM confidence)

- **the-sz.com USB ID Database** — https://the-sz.com/products/usbid/index.php?v=0x36B7 → "Puya Semiconductor (Shanghai) Co., Ltd.", accessed 2026-08-02. *Single-source for the allocation holder; corroborated circumstantially by the SDK-example provenance and by `0x36B7`'s absence from `usb.ids`.*
- **linux-usb.org `usb.ids`** — fetched 2026-08-02, 25705 lines. `0x36B7` absent; `0x1209` listed as "Generic". *Community-maintained and incomplete — its silence is not evidence.*

### Tertiary (LOW confidence — flagged, not relied upon)

- WebSearch results on PY32F0 BOOT0 behaviour. **Superseded** by the datasheet and UM1504; one result asserted BOOT0 = PF4, which is correct for PY32F002/003/030 and **wrong for PY32F071** (PF8). Recorded as a caution: sibling-part lore was actively misleading here.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| C-1 (VTOR) | **HIGH** | Three independent in-tree proofs, one SHA-verified against the pinned commit |
| C-2 (VID provenance) | **HIGH** | Exact byte match to a pinned SDK blob + an INF file; allocation holder is single-source (MEDIUM on that leg alone) |
| C-3 (local build) | **HIGH** | Executed, not reasoned; hashes recorded; tree restored clean |
| Flash map (F-1/F-2) | **HIGH** | Read from the files at a named SHA |
| Bootloader budget (F-3) | **MEDIUM-HIGH** | Components measured; the bootloader's own logic estimated; two independent anchors |
| Boot/BOOT0/SWD/USB pins (F-5/9/11) | **HIGH** on documentation; **[UNVERIFIED-UNTIL-SILICON]** on behaviour | Two agreeing official sources; no board exists |
| `nBOOT1` default (A3) | **LOW** | Not in the datasheet or UM1504; needs the RM |
| USB D+ pull-up (A4) | **LOW** | Not resolvable from the datasheet, CMSIS header or CherryUSB port |
| Package constraint (F-10) | **HIGH** | Read directly from the datasheet pin table with the column header verified |
| pid.codes process (F-6) | **HIGH** | Primary source, both rendered and repo-source |
| pid.codes latency (F-7) | **HIGH** | GitHub API, measured 2026-08-02 |
| Gate mechanism (F-14) | **HIGH** | Workflow triggers and existing modules read directly |
| Doc-shape precedent (F-15) | **HIGH** | Section skeletons and tag counts extracted from the files |

**Research date:** 2026-08-02
**Valid until:** 2026-09-01 for the silicon and in-tree findings (stable — pinned SDK, published
datasheet). **7 days** for F-7's pid.codes queue measurement, which is a moving figure and should
be re-read before the record states it.
