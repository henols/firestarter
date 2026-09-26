---
phase: 153
slug: write-path-erase-policy
created: 2026-08-21
status: settled
---

# Phase 153 Decisions

This file is the settled-before-code-is-written record for Phase 153 (Write-Path Erase Policy).
Every later plan in this phase cites a `D-153-NN` id from here rather than re-deciding it.

## D-153-01 — Erase supply form and MERGE-05 funding

**Form (a):** the six-byte AT28C software chip-erase sequence is supplied as **six inline
`handle->firestarter_set_data(handle, address, byte)` calls**, preceded by one
`rurp_set_data_output()` call, inside `eeprom28c_erase_execute`. **No new `const byte_flip_t`
array is declared anywhere in `eeprom_28c.cpp`.**

Measured reason: a six-entry `byte_flip_t` table occupies `0x1e` = **30 bytes in section `d`
(`.data`, i.e. RAM)** — measured with `avr-nm -S --size-sort` on the committed leonardo ELF, where
the existing `EEPROM_SDP_DISABLE` table (also six entries) sits at `0x800127` and
`_ZL11FLASH_ERASE` sits at `0x800163`, both in section `d`. MERGE-05's RAM clause is **exact
equality plus one named 2 B exemption that is already fully consumed**
(`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2`, `+2<=2=seam2`, Phase 149). The inline form
costs **0 B RAM** because no `.data` object is created at all — every byte is a literal argument
to an existing function call, living in `.text`/`.progmem`, not in an initialized RAM section.

**Rejected forms, each named, with a distinct reason (b):**

1. **Referencing the existing `FLASH_ERASE` table from `flash_utils.h`** — rejected. It is **not**
   free: `flash_utils.h` declares its tables at namespace scope in a header, which in C++ gives
   internal linkage unless an external declaration is visible, so **each translation unit that
   includes the header gets its own copy**. The committed leonardo ELF carries **two** surviving
   copies of `FLASH_ENABLE_WRITE` — `_ZL18FLASH_ENABLE_WRITE.lto_priv.92` and
   `_ZL18FLASH_ENABLE_WRITE.lto_priv.93` — proving LTO does **not** merge them. Reusing
   `FLASH_ERASE` this way would silently duplicate the table into `eeprom_28c.cpp`'s translation
   unit, at the same +30 B RAM cost, while also colliding with FIX-04's byte-frozen
   `flash_utils.h` framing and with Phase 117 D-10 / Phase 119 D-09's deliberate
   keep-the-`0x0D`-tables-local precedent (the same precedent that keeps `EEPROM_SDP_DISABLE` and
   `EEPROM_SDP_ENABLE` local rather than sharing `flash_utils.h`'s byte-identical twins).
2. **A `PROGMEM` table plus a per-entry copy** — rejected. RAM-neutral in principle, but
   `eeprom28c_emit_command_sequence` dereferences `sequence[i].address` **directly** against a
   `const byte_flip_t*` in RAM-addressable space; a PROGMEM table would need either a second
   emitter (duplicating the shared-emitter guarantee this phase otherwise relies on) or a
   per-entry stack copy loop, and has **no in-tree precedent** for this family.
3. **A new `.data` table plus a fourth named RAM exemption** — rejected because the two RAM-
   neutral forms above make it unnecessary. Spending the milestone's fourth named MERGE-05
   exemption on RAM, when a form exists that needs none, is not funded.

**The retype hazard is acknowledged and gated, not waived (c):** writing the six address/byte
pairs inline necessarily retypes bytes that already exist in the tree (the SDP-disable and
chip-erase sequences differ by exactly one nibble in the terminal byte: `0x20` vs `0x10`), and
that one-nibble divergence is a recognised hazard class in this repository —
`test_eeprom28c_sdp` Case 19 exists specifically for it. **Binding on plan 04:** the inline
literals are permitted only because a native full-stream equality case compares the erase op's
emitted stream, positionally, against a composite built from the in-tree tables
`SDP_FIXED_DIP28_28C256` and a `FLASH_ERASE`-driven reference — so the bytes are pinned against
the tree, never against this plan's prose.

**Funding posture (d, L-01):** a **fourth, separately-named, SHA-attributed FLASH** exemption will
be added to `check_size_baseline.py`, named exactly `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES`,
sized from plan 14's **measured** cold figure and never from an estimate — following the same
single-consumer, module-docstring-enumerated pattern as
`MERGE05_DEFECT_FIX_EXEMPTION_BYTES` (96, Phase 145), `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES`
(210, Phase 149) and `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES` (288, Phase 151).

Four alternatives are rejected on the record, by name:

- **Widening a band literal** (e.g. `MERGE05_UNO_CLASS_FLASH_BAND` or leonardo's 0 B band) —
  rejected: would silently admit unrelated future growth and destroy the tripwire, the same
  reasoning `check_size_baseline.py`'s own docstring gives for the prior three exemptions.
- **Re-anchoring `size_baseline_base01.json`** — rejected: three prior phases already refused
  this on the record (the `merge05_clause`/`re_anchor_note` fields say so verbatim, three times);
  a green `--policy merge05` run after a re-anchor means the anchor moved, not that flash growth
  stayed inside the original band.
- **Folding the bytes into an existing exemption constant** — rejected: each of the three
  existing exemptions is scoped to one attributable commit set (defect fix / page-size seam /
  lock-status read); laundering the erase cost into one of them breaks that single-consumer,
  single-attribution property.
- **Shrinking the fix to fit** — rejected: the six-write sequence and its `t_EC` wait are the
  AN 0544B-required shape; trimming them to fit a pre-existing band is the wrong incentive and
  risks the feature, the same reasoning already on record for the page-size seam.
- **Byte-neutral offsetting is explicitly rejected** — it would require hunting savings in code
  this phase has no reason to touch, turning a one-feature phase into an unrelated refactor.
- **Compile-time gating the `CMD_ERASE` arm off on leonardo is explicitly rejected** — it would
  create a functional divergence on the board the operator actually writes with, which is worse
  than spending a named exemption.

**The two size figures, stated separately and never conflated (e):** MERGE-05 leonardo **flash**
headroom is **0 B** (currently at exactly `+594` against a `0 (band) + 96 + 210 + 288 = 594` B
allowance — the four addends being the leonardo flash band plus the three existing named
exemptions). The **Caterina** cliff headroom is a **different, separate, UNGUARDED** figure:
`28672 - 27500 = 1172` B. Quick task `260820-a7w` raised `board_upload.maximum_size` to the real
32768 B on all three AVR environments, so the linker no longer protects the USB bootloader —
past 28672 B the leonardo's Caterina bootloader is overwritten and the board is bricked, and no
gate catches it. These two numbers (0 B MERGE-05 flash headroom vs. 1172 B Caterina headroom) must
never be conflated in any later plan.

**Gate for the inline literals (binding on plan 04):** the inline literals are gated by a native
full-stream equality case comparing `eeprom28c_erase_execute`'s emitted stream, positionally,
against a composite reference built from the in-tree `SDP_FIXED_DIP28_28C256` table and a
`FLASH_ERASE`-driven reference sequence. This is named as binding on plan 04 so the erase bytes
are pinned against the tree, not against this document's prose.

**ERASE-09 closing statement (f):** the change this section funds is
**software-proven and unvalidated on silicon**.

---

## D-153-02 — The 0x0D chip erase emits an SDP-disable prefix

**Settled: yes — emit SDP-disable first.** The reasoning is an asymmetry argument, not an appeal
to the application note's silence:

- Atmel AN 0544B Rev. 0544B-10/98 (*Software Chip Erase*) is **silent** on whether the six-byte
  chip-erase code is decoded on a software-data-protected part. It states only that protection
  **remains enabled** *after* the erase, and that no byte loads are allowed *after* the six-byte
  code.
- If the code is **not** decoded while protected, the failure mode is an erase that reports OK
  having erased nothing. On protocol `0x0D` that failure is **undetectable**: Phase 151
  established that the SDP protection state is unreadable on this family, so no oracle exists
  that could ever catch a phantom erase. **Silence is not permission when the failure mode is
  invisible.**
- The cost of being wrong in the chosen direction is six extra bus writes and one `t_WC` wait on
  an already-unprotected part: harmless. The cost of being wrong in the other direction is a
  silent no-op destructive command — the exact phantom-erase class Phase 121 D-12 fought and the
  class Phase 119 D-06's op-layer guard exists for.
- Consistency: `eeprom28c_write_init` already SDP-disables before every page load, so an erase
  that did not would be the only bus-writing operation on this protocol that skips it.

**Mechanism:** reuse `eeprom28c_sdp_unlock_execute(handle)` verbatim as the prefix. It is already
the SDP-disable emit (`eeprom28c_emit_sdp_sequence_timed` over `EEPROM_SDP_DISABLE`) plus
`eeprom28c_wait_for_sdp_completion`. It reuses the existing `EEPROM_SDP_DISABLE` `.data` table, so
it costs **0 B additional RAM**, and it reuses the existing `MSG_INFO_SDP_UNLOCK` /
`MSG_INFO_SDP_UNLOCK_DONE_US` message ids, so **no new catalog id is minted**.

**Consequence binding on plan 03:** because `eeprom28c_wait_for_sdp_completion` ends in reads
through `handle->firestarter_get_data`, the data bus is left as an input after the prefix runs.
`rurp_set_data_output()` **must** be called after the prefix and before the first erase write.

**Resulting observable stream shape, binding on plan 04:** the SDP-disable six-write stream is
followed by the chip-erase six-write stream, so the **last** command payload written is the
chip-erase terminal byte (`0x10`) and the **sixth** payload overall is the SDP-disable terminal
byte (`0x20`). Do **not** assert a wall-clock property anywhere in a native test: native stubs do
not stub `delay()` and record no time, so no test may claim a timing relationship between the
prefix and the erase writes.

---

## D-153-03 — GATE-03: the stated mechanism does not hold; the real control is a negative source scan

Stated in writing, without softening, as L-03 requires:

- The roadmap's criterion 3 implies that `tools/check_dispatch.py` is what prevents the hardware
  12 V-on-OE path from being wired into `0x0D`. **It is not.** That checker is
  **database-and-dispatch-table** scoped: its GATE-03 guard fires only on a `handler ==
  "configure_eprom"` paired with a no-VPP-pin pinout (`no_vpp_pin_pinouts`, built from the pinout
  file). It **structurally cannot** observe a control-register write inside a handler body —
  `configure_eeprom28c` and `eeprom28c_erase_execute` are C++ source, entirely outside this
  Python checker's DB/dispatch-table scan.
- The hardware path already exists in this tree, at `flash_5v_page.cpp` lines 196-231
  (`flash_5v_page_erase_execute`, which asserts `CTRL_VPE_ENABLE` and the VPP boost regulator) —
  the very file an executor edits for ERASE-02. So **proximity, not absence, is the risk**.
- Therefore the **primary** GATE-03 control for this phase is a **brace-matched negative source
  scan** of `eeprom28c_erase_execute`'s body, asserting zero occurrences of the VPP/VPE
  control-register tokens (`CTRL_VPE`, `CTRL_VPP_REGULATOR_ENABLE`,
  `firestarter_set_control_register`), planned as a real gate in plan 05, with a
  planted-violation leg that is **observed to fail** before the gate is trusted.
- `check_dispatch.py` is nonetheless **not weakened, not exempted and not re-baselined**, and
  `git diff --quiet -- tools/check_dispatch.py` must hold at phase end. This is recorded as an
  **independently required invariant**, not the control that prevents the hardware path.
- **Honest statement for the record:** the software path is chosen because it is the correct
  engineering choice, and `check_dispatch.py` could not have stopped the wrong one even if it had
  been implemented.

---

## D-153-04 — erase -b does not get a post-erase blank check on 0x0D (L-05)

**Disposition: not wired.** Reasons:

- ERASE-05 keeps `blank` as its own independent step; wiring a post-erase blank check into
  `eeprom28c_erase_execute` or via an `operation_end` arm would duplicate that step implicitly.
- An `operation_end` arm costs flash against a leonardo target that is already at **0 B MERGE-05
  headroom** — there is no budget for a feature this phase does not require.
- Both closest sibling protocols decline it: `flash_5v_page` (`0x05`) has **no** `operation_end`
  arm at all, and `flash_nor_unlock` carries a **commented-out** one — this project's own written
  record of deliberately *not* wiring a post-erase blank check.

`erase -b` on `0x0D` is therefore a **documented no-op**, rather than a discovered one.

Per RESEARCH A7: the `0x0D` erase is a device-global **chip erase** by construction (the AN 0544B
sequence erases the whole part) and it **ignores** `erase --sector-address`, which exists for the
`0x06` sector-erase protocol and has no meaning on a chip-erase-only device.

---

## D-153-05 — erase stays out of write's auto-set path and out of write_init (L-06)

Two dispositions, both recorded:

- **No `FLAG_CAN_ERASE`-gated erase block is added to `eeprom28c_write_init`.** Restoring
  `FLAG_CAN_ERASE` must **not** cause `write` to start erasing implicitly. Both sibling handlers
  (`flash_5v_page_write_init`, `flash_nor_unlock_write_init`) have such a block, and an executor
  mirroring the sibling pattern will be tempted to add one here — this is explicitly rejected.
  D-07 asks for erase as a **standalone** step, not as part of `write`.
- **`erase` gains no `--skip-sdp-unlock` option** and stays out of `write`'s D-04
  `FLAG_SKIP_SDP_UNLOCK` auto-set path; that flag is scoped to `write` by D-17's reasoning. The
  auto-set behaviour is not silently extended to cover `erase`.

---

## Pre-change measured position (2026-08-21, cold)

Reproduced this session. For each of `uno`, `uno328pb`, `leonardo`, in that order, the build
directory was removed with `rm -rf firestarter/.pio/build/<env>` and exactly one
`pio run -e <env>` was then run, output teed to a scratch log under the session scratchpad
(`cold_uno.log`, `cold_uno328pb.log`, `cold_leonardo.log`). No file in `firestarter/` was modified
by this measurement step.

| Target | Flash used | Flash total | RAM used | RAM total | Byte-identical to `size_baseline.json`? |
|---|---|---|---|---|---|
| uno | 25418 | 32768 | 1575 | 2048 | yes |
| uno328pb | 25468 | 32768 | 1581 | 2048 | yes |
| leonardo | 27500 | 32768 | 2016 | 2560 | yes |

All three targets reproduced **byte-identical** to the committed `size_baseline.json`'s
`avr_targets` block. No target failed to reproduce, so there is no plan-14 blocker to flag from
this table.

**Delta against BASE-01** (`size_baseline_base01.json`: uno 24824, uno328pb 24874, leonardo
26906, all flash):

| Target | Flash delta vs BASE-01 | MERGE-05 allowance | Headroom |
|---|---|---|---|
| uno | +594 | uno-class allowance (`MERGE05_UNO_CLASS_FLASH_BAND` = 64 B plus the same three named exemptions) | not the binding case — leonardo is |
| uno328pb | +594 | same uno-class allowance as uno | not the binding case — leonardo is |
| leonardo | **+594** | `0 (leonardo band) + 96 (MERGE05_DEFECT_FIX_EXEMPTION_BYTES) + 210 (MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES) + 288 (MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES) = 594 B` | **0 B** — `+594 <= 594 = band0 + exempt96 + seam210 + lock288` |

The **Caterina** cliff headroom, stated as a separate figure and labelled **UNGUARDED**:
`28672 - 27500 (leonardo flash used) = 1172 B`. This is not a MERGE-05 quantity — `board_upload.
maximum_size` was raised to the real 32768 B on all three AVR envs by quick task `260820-a7w`, so
the linker's own protection of the Caterina USB bootloader boundary (28672 B) no longer exists;
nothing but this recorded figure stands between plan 14's delta and a bricked leonardo.

**Native test counts**, both environments run this session:

| Env | Cases | Suites |
|---|---|---|
| `native` | 163 | 17 |
| `native_nodevtools` | 163 | 17 |

Both agree with each other and with `size_baseline.json`'s `native_envs` block (163/17 each).

**Host suite**, run from `firestarter_app/` with `-o addopts=""` (repo `addopts` is `-ra -q`;
doubling `-q` would suppress the count line):
`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70 -o addopts=""`

Result: **1806 passed**, 1 warning, in 216.60 s. Coverage: **83.61%** (required 70%, reached).
32 snapshot-report cases passed within that total.

`git diff --quiet` in `firestarter/` succeeds: this measurement task changed no source file in
the firmware repo. `firestarter_app/` was not touched by this task either — the host run is a
read-only test invocation.

---

## Post-change measured position (cold)

Measured 2026-08-21, plan 14, task 1, on the firmware tree with all of this phase's byte-changing
commits landed (`0d90e5c` erase-init blank-check delete, `df09704` `AT28C_TEC_MAX_MS` +
forward decl, `d9a9993` `eeprom28c_erase_execute`, `8b7feac` the `CMD_ERASE` dispatch arm,
`dcb30fe` the 0x05 write-init blank-check delete; `1810db2`/`bf01e2b` are test-only and
`21a02c3`/`2a3bc65` are doc-only, contributing 0 B to any target). Same procedure as the
pre-change measurement above: for each of `uno`, `uno328pb`, `leonardo`, in that order,
`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, output teed to a scratch log
(`cold_uno.log`, `cold_uno328pb.log`, `cold_leonardo.log`). No file in `firestarter/` was
modified by this measurement step — verified by `git diff --quiet` below.

**(a) Constants lockstep.** ERASE-08's first clause. Recorded side by side, both files read this
session:

| Constant | `firestarter/include/firestarter.h` | `firestarter_app/firestarter/constants.py` |
|---|---|---|
| erase command id | `#define CMD_ERASE 3` (`:61`) | `COMMAND_ERASE = 3` (`:62`) |
| blank-check command id | `#define CMD_BLANK_CHECK 4` (`:62`) | `COMMAND_BLANK_CHECK = 4` (`:63`) |
| erase-capability flag | `#define FLAG_CAN_ERASE 0x02` (`:173`) | `FLAG_CAN_ERASE = 0x02` (`:120`) |
| erase-skip flag | `#define FLAG_SKIP_ERASE 0x04` (`:174`) | `FLAG_SKIP_ERASE = 0x04` (`:121`) |
| blank-check-skip flag | `#define FLAG_SKIP_BLANK_CHECK 0x08` (`:175`) | `FLAG_SKIP_BLANK_CHECK = 0x08` (`:122`) |

The host side names the command ladder `COMMAND_*` rather than `CMD_*` (constants.py's own
comment records this as "the default `CMD_X` -> `COMMAND_X` rule") — the *values* are the
lockstep property, not the identifier spelling, and every value above matches exactly.
`python3 -m pytest tests/test_revision_constants_parity.py -o addopts="" -q` (run from
`firestarter_app/`): **14 passed**. This phase minted no new constant on either side — nothing
moved. This is a measured fact: both files were read this session and diffed against the values
recorded in D-153-01's decisions, and no value differs.

**(b) Cold AVR figures.**

| Target | Flash used | Flash total | RAM used | RAM total |
|---|---|---|---|---|
| uno | 25548 | 32768 | 1575 | 2048 |
| uno328pb | 25598 | 32768 | 1581 | 2048 |
| leonardo | 27630 | 32768 | 2016 | 2560 |

**Delta against the plan-01 pre-change position** (uno 25418, uno328pb 25468, leonardo 27500,
all flash; RAM 1575/1581/2016 on all three):

| Target | Flash delta vs pre-change | RAM delta vs pre-change |
|---|---|---|
| uno | +130 | +0 |
| uno328pb | +130 | +0 |
| leonardo | +130 | +0 |

**Delta against BASE-01** (uno 24824, uno328pb 24874, leonardo 26906, all flash; RAM
1573/1579/2014):

| Target | Flash delta vs BASE-01 | RAM delta vs BASE-01 |
|---|---|---|
| uno | +724 | +2 |
| uno328pb | +724 | +2 |
| leonardo | +724 | +2 |

The RAM delta against BASE-01 (+2 on all three) is Phase 149's own page-size-seam RAM exemption
(`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2`, already fully consumed), unmoved by this
plan. **The RAM delta against the immediately-prior pre-change position is exactly 0 B on all
three targets** — `D-153-01`'s prediction holds and is verified, not asserted. This is not a
blocker; no stop-and-report is triggered.

**Leonardo exemption arithmetic** (the only figure Task 2 may use): BASE-01 delta minus the
existing 594 B allowance = `724 - 594 = 130`. Positive, so a fourth exemption is funded, sized at
exactly **130 B**. This is not rounded up for headroom.

**Caterina headroom**, a separate, distinctly labelled figure, marked **UNGUARDED**:
`28672 - 27630 (leonardo flash used) = 1042 B`. This is a different number from the MERGE-05
clause (leonardo's MERGE-05 flash headroom, computed below, is 0 B once the new exemption is
adopted) and neither may be computed from the other.

**Native case and suite counts**, both environments run cold this session:

| Env | Cases | Suites | All passed |
|---|---|---|---|
| `native` | 170 | 17 | yes |
| `native_nodevtools` | 170 | 17 | yes |

Both environments agree with each other. Delta against the committed `size_baseline.json`
(163 cases / 17 suites for both envs): **+7 cases, +0 suites**, on both environments — this
phase's plans 02, 04 and 06 added native cases without adding a new suite file. `envs_agree`
stays true.

**Build-warnings checker.** `python3 scripts/check_build_warnings.py --log uno=cold_uno.log
--log uno328pb=cold_uno328pb.log --log leonardo=cold_leonardo.log --log native=native.log --log
native_nodevtools=native_nodevtools.log` → **PASS, exit 0**: `uno: macro_redefinition=0 (== 0),
uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)`; native observed
872 (294 below the 1166 watermark, INFO not FAIL); native_nodevtools observed 998 (168 below).
The watermark still holds at 1166 — no new warning class appeared, and it was not raised.

`check_erase_no_vpp.py` (GATE-03's real control): **PASS, exit 0** —
`eeprom28c_erase_execute()` (lines 545-560, 16 lines scanned) contains no VPP/VPE
control-register, chip-enable/disable, or bus-config-bypassing hazard token.

`git diff --quiet` in `firestarter/` succeeds: this measurement task changed no source file in
the firmware repo. `firestarter_app/` carries no tracked-file diff either (`git diff --stat`
empty); its untracked files (`SECURITY.md`, `datasheets/*.pdf`, `write_test_port.sh`,
`.planning/config.json`) predate this task and are not touched by it.

**Neither repository's CI runs this size gate.** This local, cold run is the only evidence it
was ever exercised for this plan.
