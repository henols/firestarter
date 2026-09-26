---
title: PY32F071 port — actual branch state (2026-07-28) + host FW-install seams
date: 2026-07-28
context: Captured during /gsd-explore 2026-07-28. Corrects the stale prior-art paragraph in the v1.28 ROADMAP entry and records the four host-side seams a fourth board target has to pass through. Companion to seed py32f071-no-external-tool-fw-install.md.
---

# PY32F071 port — what is actually on the branches

The v1.28 ROADMAP entry ([`ROADMAP.md`](../ROADMAP.md) line 33, written at the
2026-07-27 backlog review) says the work is **"not in flight"**, cites
`henols/firestarter` **PR #46 as closed unmerged**, and describes the surviving
prior art as `feature/py32f071-toolchain` @ `2c2ed10` — *603 additions across 8
files*. All three claims are out of date. Verified against `origin` on
2026-07-28.

## Real inventory (firmware repo, all forked off `beta`)

| Branch | PR | State | vs `beta` | Substance |
|---|---|---|---|---|
| `agent/py32f071-toolchain` | **#48** | **OPEN (draft)** | **52 ahead / 27 behind** | The live attempt. Base is `agent/portability-macros`, so it's a stacked PR. |
| `feature/py32f071-full-support` | #47 | CLOSED | 45 ahead / 27 behind | Superseded — see the weak-stub trap below. |
| `feature/py32f071-toolchain` | #46 | CLOSED | 11 ahead / 27 behind | The one the ROADMAP cites. Smallest of the set. |
| `agent/portability-macros` | — | (base of #48) | 5 ahead / 27 behind | The gh#16 HAL-prep half, on its own. |
| `feature/common-vpp-calibration` | #45 | CLOSED | 10 ahead / 27 behind | DAC/VPP calibration abstraction. |

`agent/rp2040-portability-macros` shares `agent/portability-macros`' head
(`52d6c1f`) — same content, different name.

**Every branch is 27 commits behind `beta`**, not stale-by-hundreds. The
"1 ahead / 2xx behind `main`" reading that suggests otherwise is an artifact of
`main` lagging `beta` by 224 commits (stable is operator-gated —
`feedback_stable_release_operator_gated`). Compare against `beta`, not `main`.

## PR #48 is much further along than the ROADMAP assumes

**PY32F071 CI is green** (`PY32F071 firmware` workflow, `agent/py32f071-toolchain`,
2026-07-21, three consecutive successes after four earlier failures). That build
is not a smoke test — `platform/py32f071/CMakeLists.txt` compiles the **shared**
Firestarter command processor, framing and PROM algorithms for Cortex-M0+:

- **Pinned official SDK** via CMake `FetchContent`:
  `https://github.com/OpenPuya/PY32F071_Firmware.git` @ `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`
- **CherryUSB CDC** transport; 48 MHz PLL clock for native USB
- SysTick milliseconds + TIM3 microseconds
- VREFINT-compensated 12-bit ADC
- Contiguous 8-bit GPIO bus: one-snapshot `IDR` read, atomic `BSRR` write
- CI emits ELF / BIN / HEX / map / size report / SHA-256 checksums

The **"does this architecture even build"** risk is therefore retired. That was
the ROADMAP's implicit main unknown; it is not the unknown any more.

Firmware identity is already correct for the host: `RURP_BOARD_NAME = "py32f071"`,
`DATA_BUFFER_SIZE = 1024`.

## What is NOT done (per PR #48's own status + the code)

- **Pin map is an explicitly provisional placeholder** — PB0–PB7 data, PA0–PA5
  control, VPP on PA4/ADC ch4. It exists so the target compiles before a
  schematic. Must not be trusted near a PROM.
- **Config storage is runtime-only**, not flash-persistent. The part has no
  EEPROM, so the CRC-validated dual-slot flash scheme `PORTING.md` specifies is
  still unwritten.
- **Closed-loop DAC VPP** is on the *closed* PR #45, not on #48.
- **Zero hardware validation.** Nothing has run on silicon; no PCB exists
  (confirmed by operator, 2026-07-28).

## Trap: PR #47 looks complete and is not

`feature/py32f071-full-support` has a 24-file `platform/py32f071/` tree and a
CMake list that pulls in every common source — it reads as the most finished
branch. But its `src/usb.c` (141 lines) is a ring buffer over
`__attribute__((weak))` **no-op** low-level hooks:

```c
/* Official Puya CherryUSB glue overrides these low-level hooks. */
__attribute__((weak)) void py32_usb_ll_init(void) {}
__attribute__((weak)) bool py32_usb_ll_can_transmit(void) { return false; }
```

It links, and a board flashed with it would be **silent on USB**. `vpp_target.c`
is 13 lines. It also carries no SDK fetch. PR #48 is the one with a real stack —
start from #48, not #47.

## Host-side FW-install seams (firestarter_app)

A fourth board target touches exactly four places. `manage_firmware_update`
(version compare, channel selection, download, prompt, cleanup) is
board-agnostic and needs no change; the only line that cares is the single
flasher call at `firmware.py:640`.

| # | Seam | Today | Needs |
|---|---|---|---|
| 1 | Board identity | `firmware.py:113` parses `<version>:<board>[:<buf>[:<maxchunk>]]` | Nothing — `py32f071` flows through free |
| 2 | Release asset | `firestarter_{board}.hex`, hardcoded at `firmware.py:155`, `:237`, `:336` | Publish `firestarter_py32f071.hex` (or `.bin`) as a **release asset**. PY32 CI currently emits an *Actions artifact* named `firestarter-py32f071.hex` — hyphen, wrong prefix, wrong publication channel. Note the extension is baked into the pattern too. |
| 3 | Flasher | `_install_with_avrdude` (`firmware.py:420`) — if/elif ladder resolving `(partno, programmer_id, baud)` | avrdude cannot touch a Cortex-M0+. Extract a `FirmwareFlasher` strategy; `AvrdudeFlasher` keeps the ladder verbatim (uno / uno328pb-urclock / leonardo-avr109 are bench-earned, per `project_bench_findings_v15`). |
| 4 | CLI surface | `click.Choice(["uno","uno328pb","leonardo"])` at `cli_handlers.py:821`; `--avrdude-path` / `--avrdude-config-path` + the `avrdude-path` / `avrdude-config-path` config keys | Add the board; the avrdude-specific options and config keys need a per-flasher equivalent rather than a second hardcoded pair. |

**Reusable shape already present:** the Leonardo `avr109` path does a 1200-baud
touch in `avr_tool.py:115` (`_trigger_reset`) to drop the board into its
bootloader, then flashes what reappears. The install flow already tolerates the
port vanishing and coming back as a different USB device — which is precisely
what any bootloader-based PY32 path needs.

## Update 2026-07-28 — the host half is built

Seam 3 (the flasher) and seam 4 (CLI surface) are implemented on `firestarter_app`
branch `feature/py32f071-fw-install` @ `311eacf`, queued as milestone **v1.29**
in [`ROADMAP.md`](../ROADMAP.md) — see that entry for scope, gate results and the
remaining blockers. Seam 2 (release-asset publication) is the one that still
blocks an end-to-end install, and it lives in the **firmware** repo's CI, not
here.

Two safety defects surfaced only when the code met a real USB bus and a real
board, neither of which a unit test would have caught:

- DFU **runtime** interfaces are common on unrelated peripherals (this
  devcontainer's webcam, `04f2:b751`, advertises one). Selecting `interfaces[0]`
  would have sent it `DFU_DETACH` and flashed Firestarter firmware into it.
- `board_to_use = current_board or board_override` lets a detected board silently
  beat a typed `--board`. With a Leonardo attached, `fw --install --board
  py32f071` flashed the **Leonardo** (`3.0.0b11` → `3.0.0b13`). Harmless as it
  happened — the entire b11→b13 firmware delta is `include/version.h`, so b12/b13
  are the spurious auto-fired beta builds that
  [[reference_beta_merge_push_autofires_ci_new_beta]] predicts — but the
  wrong-target path was real.

## Sizing

Host-side is **one phase**. The complexity is all firmware- and bench-side: real
pin map on a real PCB, flash-persistent config, DAC VPP, and the fourth-board
bench-cost multiplier the ROADMAP already flags. With no PCB, the honest
closeable scope is: land the portability + py32 stack onto `beta` (27 commits
behind), the host flasher seam, flash config, and the install-path design — all
software-testable.

## Update 2026-08-02 — Supersession Section (Phase 130 Plan 09, CLOSE-01)

**⚠ SUPERSEDED (2026-08-02, Phase 130 Plan 09, CLOSE-01)** — this note is a
`2026-07-28` `/gsd-explore` capture. The body above (lines 1–134) is preserved
verbatim, byte-for-byte, as the record of what was believed on that day;
nothing above this heading was edited to produce this section. The rows below
supersede specific claims in that body as of Phase 130 (v1.23 PY32F071
Integration), requirement CLOSE-01. Each row pairs the superseded claim with
its corrected value and its evidence, so this section is never itself a new
stale source.

| Site (line, as of 2026-07-28) | Superseded claim | Corrected value | Evidence |
|---|---|---|---|
| Opening paragraph, line 12 | Cites `2c2ed10` / "603 additions across 8 files" as the surviving prior art (quoting the ROADMAP's own since-corrected claim) | The real inventory is five branches (below); `2c2ed10` (`feature/py32f071-toolchain`, PR #46) is the smallest of the five, not the sole survivor — the live attempt is `agent/py32f071-toolchain` (PR #48, 52 ahead) | This note's own `## Real inventory` table (lines 16–33); `130-RESEARCH.md` R-14 |
| Real-inventory table, lines 20–24 | Every branch listed "27 behind" `beta` | Both firmware and app sub-repos are now measured **0 behind** `origin/beta` — the milestone branches are ahead only (Phase 124 landed the merge) | `PROJECT.md` "Research corrections" C-11/R-3: branch tips `5a89ee7`/`cc9452f`, 83/0 and 37/0 ahead of `origin/beta`; `130-RESEARCH.md` R-3 |
| Prose, line 29 | "Every branch is 27 commits behind `beta`, not stale-by-hundreds" | Same correction as above — 0 behind, not 27 | Same evidence as the table row above |
| "PR #48 is much further along" section, line 53 | `DATA_BUFFER_SIZE = 1024` | py32's `DATA_BUFFER_SIZE` is **512**, not 1024 (`CMakeLists.txt:113`), deliberately not bumped to match Leonardo's 1024 because it is wire-visible via v1.10 CAP-01 and a bump would be a behaviour change needing its own justification | `130-RESEARCH.md` R-2; `REQUIREMENTS.md` §"Out of Scope" |
| "What is NOT done" section, line 61 | "the CRC-validated dual-slot flash scheme `PORTING.md` specifies is still unwritten" | `PORTING.md` exists only on the two CLOSED PRs (#46/#47, blob `4b1a441`) and its prescribed layout does not match what PR #48 built — never an existing, live specification. The dual-slot design was instead authored in-milestone (Phase 126, CFG-01/CFG-05) as dual-slot CRC32 flash-persistent config, and it landed | `130-RESEARCH.md` R-8/A-6; `PROJECT.md` Phase 126 entry |
| Host-side seams table, line 94 | "the extension is baked into the pattern too" (the hardcoded `firestarter_{board}.hex` extension seam) | Already fixed on the branch: `asset_candidates()` / `_pick_asset()` cover all four call sites, and `.bin` is accepted | `130-RESEARCH.md` R-7; `PROJECT.md` Phase 127/128 entries |
| Host-side seams table, line 96 | `cli_handlers.py:819` | The board list moved to `cli_handlers.py:930` | `130-RESEARCH.md` R-6 |
| "Update 2026-07-28" section, line 107 | `feature/py32f071-fw-install` @ `311eacf`, "queued as milestone v1.29" | That branch landed as a real merge commit at `4ee64a1` (`firestarter_app@63ce44e`); the v1.29 slot was retired into v1.23 by CLOSE-03, not carried forward as a separate milestone | `PROJECT.md` Phase 127 entry ("`feature/py32f071-fw-install` @ `4ee64a1` landed as a **real merge commit**"); `130-RESEARCH.md` R-11 |
| "Sizing" section, lines 131–134 (checker miss: "27 commits" / "behind" split across two physical lines by the markdown wrap, so this site is not machine-flagged; addressed here for completeness per this plan's truths, not because the gate requires it) | "the honest closeable scope is: land the portability + py32 stack onto `beta` (27 commits behind), the host flasher seam, flash config, and the install-path design — all software-testable" | That scope did not merely stay closeable — it **closed**: the port stack landed (Phase 124), the host installer landed (Phase 127), flash config landed (Phase 126), and the install-path design is recorded (Phase 129, PCB-01…05). The branches are 0 behind, not 27 | `PROJECT.md` "Phase progress — 6 of 8 complete" (Phases 124/126/127/129 entries) |

Still useful, unmoved by anything above: the four host-side FW-install seams
this note identified (board identity, release asset, flasher, CLI surface),
the PR #47 weak-stub trap (`__attribute__((weak))` no-op USB hooks), and the
PR #48-versus-#46 distinction (#48 is the one with a real stack). Only the
figures and locations superseded above have moved; the qualitative findings
stand.

Machine-readable exemption index for `check_record_corrections.py` (Plan
130-09, mechanism 3 — each marker names one needle label and the exact
1-based line number(s) in the body above it retroactively covers; see
`check_record_corrections.py`'s module docstring, "Why a fourth mechanism
exists"):

<!-- recordscan:supersedes needle=third-stack-2c2ed10 lines=12 reason: opening paragraph line 12 quotes the ROADMAP's own since-corrected 2c2ed10/603-additions citation; corrected value and evidence are in the table row above -->
<!-- recordscan:supersedes needle=branches-27-behind lines=20,21,22,23,24,29 reason: both sub-repos are now 0 behind origin/beta per Phase 124; corrected value and evidence are in the table rows above -->
<!-- recordscan:supersedes needle=py32-buffer-1024 lines=53 reason: py32 DATA_BUFFER_SIZE is 512, not 1024, per R-2; corrected value and evidence are in the table row above -->
<!-- recordscan:supersedes needle=porting-md-dual-slot lines=61 reason: PORTING.md is stranded on two closed PRs and the dual-slot design landed in-milestone instead, per R-8/A-6; corrected value and evidence are in the table row above -->
<!-- recordscan:supersedes needle=hex-extension-hardcoded lines=94 reason: the extension hardcoding is already fixed on the branch per R-7; corrected value and evidence are in the table row above -->
<!-- recordscan:supersedes needle=cli-handlers-821 lines=96 reason: the board list moved to cli_handlers.py:930 per R-6; corrected value and evidence are in the table row above -->
<!-- recordscan:supersedes needle=host-head-311eacf lines=107 reason: the branch landed at 4ee64a1 as a real merge commit per R-11; corrected value and evidence are in the table row above -->

