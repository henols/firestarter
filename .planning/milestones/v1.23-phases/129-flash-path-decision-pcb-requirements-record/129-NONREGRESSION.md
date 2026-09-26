# Phase 129 Non-Regression Sweep — closing plan (129-09)

**Written:** 2026-08-02
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`5a89ee76dc4681abe18db259e57bb92f519520f4`
**Meta branch:** `gsd/v1.23-py32f071-integration` · **HEAD at this sweep (before this plan's own
commits):** `ef721c83770da7ec625f24f08460f6b7f04734fa`

`firestarter_app` was **not touched** this phase (D-04). It carries unrelated, pre-existing
uncommitted local dirt (`.gitignore` modified; `.coverage`, `.planning/config.json`,
`SECURITY.md`, `write_test_port.sh` untracked) that predates this phase, and its gitlink is
**deliberately not bumped** by this plan or any other plan in Phase 129.

> **No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon, and
> nothing in it can. This phase's claim is a written decision record, a mechanically enforced
> parity between its two copies, and a comment-only firmware edit proven to change no emitted
> byte. None of that says the image runs, boots, or installs.

**Re-execution pledge.** Every row in §2 was executed in **this session** (Plan 129-09's Task 1),
against the trees exactly as they now stand — nothing is copied from any of this phase's eight
prior plans' (129-01 through 129-08) SUMMARY files without an independent re-check. Where a prior
SUMMARY made a claim (an exit code, a count, a digest, a literal), this document re-checked it
against the live tree and says so below, including one deliberate divergence from a prior
SUMMARY's evidence path: the D-13 byte-identity sequence was **re-run from scratch in a fresh
scratch directory** in this session, rather than transcribed from 129-07's retained
`/tmp/firestarter-py32f071-d13` evidence — the digests agree, and that agreement is itself part
of the evidence, not an assumption.

---

## 1. The claim, as precise statements

1. `.planning/v1.23-FLASH-PATH-DECISION.md` exists, is anchored to a named firmware HEAD and SDK
   tag, and carries eleven `## ` headings including five `[SHARED:Sn]`-marked sections, a
   `### Deliberately undecided` subsection, and a closing `## Claim ceiling`.
2. `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`'s five shared bodies are byte-identical
   to the meta record's §2–§6 — mechanically verified, not eyeballed.
3. The D-03 sync-gate module (`firestarter/tests/test_flash_path_record_sync.py`) is at 41 of 41,
   with ten named fail-closed legs proving the gate can genuinely fail.
4. The linker script's `BOOTLOADER` comment names both record layers and no longer carries the
   false "on a part with no VTOR" clause.
5. The comment-only linker edit (`5a89ee7`) changed no emitted byte across two independent local
   builds, with a confirmed real relink (not a vacuous no-op) in both directions of the sequence.
6. The `py32f071-no-external-tool-fw-install` seed's `status:` frontmatter reflects that its
   trigger fired, without adding a new frontmatter key.
7. The milestone claim gate (`check_permitted_claims.py`) passes on all three durable artifacts
   named explicitly on its command line: the meta record, the firmware subset, and this document.

Each statement above is checkable and is checked, individually, in §2 below.

---

## 2. Locally provable, executed now

### Firmware repo (`/workspaces/firestarter`)

| # | Command | Expected | Observed |
|---|---|---|---|
| F1 | `git rev-parse --abbrev-ref HEAD` | `v1.23-py32f071-integration` | **`v1.23-py32f071-integration`** |
| F2 | `git rev-parse HEAD` | matches 129-07's recorded HEAD `5a89ee7...` | **`5a89ee76dc4681abe18db259e57bb92f519520f4`** — string-equal to 129-07's SUMMARY and 129-08's unchanged HEAD |
| F3 | `git status --porcelain` | 0 lines (before and after the D-13 re-run) | **0 lines**, confirmed both before this plan's work and again after the throwaway linker edit was reverted |
| F4 | `python -m pytest tests/ -q -rs` | `221 passed`, 0 failed, 0 skipped | **`221 passed` in 6.92s** — confirms 129-08's claim independently; re-confirmed again after the D-13 sequence (`221 passed` in 6.82s) |
| F5 | `python -m pytest tests/test_flash_path_record_sync.py -v` | `41 passed` | **`41 passed` in 0.60s** — all ten `TestFlashPathRecordSyncFailsClosed` legs plus all 31 `TestFlashPathRecordSync` legs listed individually below (§ "Ten fail-closed legs, named") |
| F6 | Subprocess re-run, `test_absent_meta_root_skip_is_auditable_not_silent`, `FIRESTARTER_META_ROOT` pointed at an empty tmp dir | exit 0, output contains `skipped`, names the resolved absent marker path, no `failed` | **exit 0**; output: `SKIPPED [1] tests/test_flash_path_record_sync.py:641: meta repo checkout absent (no /tmp/tmpx2eb7pio/.git marker)` — the resolved absent marker path is named verbatim |
| F7 | `meta_path(".planning", "__definitely_not_a_real_file__.md")` under the real, present meta root | raises `MissingScanTargetError` naming the resolved path and instructing "update" | **Raised.** Message: `/workspaces/.planning/__definitely_not_a_real_file__.md does not exist, but the meta repo IS present (marker found at /workspaces/.git). This scan target was renamed or moved -- update this path (...) rather than removing or bypassing this gate.` |
| F8 | `grep -c "^## " .planning/v1.23-FLASH-PATH-DECISION.md` | non-zero, matching the record's own heading count | **11** |
| F9 | `grep -cE '^- \[ \] \*\*R[1-7] — ' .planning/v1.23-FLASH-PATH-DECISION.md` | `7` | **7** |
| F10 | `grep -cE '^\s+- \*Why:\*'` / `'^\s+- \*Breaks if omitted:\*'` (meta record) | `7` each | **7** / **7** |
| F11 | `grep -c "### Deliberately undecided"` (meta record) | `1` | **1** |
| F12 | Each of the three exact literals (`_L1_NON_RETIREMENT`, `_L2_SHIP_GATE`, `_L3_SOCKET_EMPTY`), grepped verbatim against both the meta record and the firmware subset | `1` each, on each file | **1/1/1** on the meta record; **1/1/1** on the firmware subset — 6 total, all exactly once |
| F13 | `grep -ciE 'MEM_MODE\|trampoline\|RAM vector copy'` on both records | `0`, `0` | **0**, **0** |
| F14 | `grep -ciE` the eight claim-gate forbidden-phrase patterns (unqualified/py32-scoped forms) on both records | `0`, `0` | **0**, **0** |
| F15 | `grep -ciE 'no[[:space:]]+VTOR'` on the linker script | `0` | **0** |
| F16 | `grep -cF 'BOOTLOADER (rx) : ORIGIN = 0x08000000, LENGTH = 0'` on the linker script | `1` | **1** |
| F17 | `grep -cE '^## [0-9]'` on the firmware subset (must carry zero numbered headings) | `0` | **0** |
| F18 | `grep -c "## Claim ceiling"` on the firmware subset | `1` | **1** |
| F19 | Claim gate, explicit argv, meta record + firmware subset only (Task 1, before this document existed) | exit 0, `PASS:` naming both files | **exit 0** — `PASS: scanned ../../v1.23-FLASH-PATH-DECISION.md, ../../../firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md; 2 file(s) carry the required silicon caveat (...)` |
| F20 | `2ef7b57` diff scope (the locator-fix deviation, re-check a) | touches only the brace-detection loop; no needle set, no `_LINKER_FORBIDDEN_RE`, no `_assert_non_vacuous` span changed | **Confirmed** — `git show 2ef7b57` touches only `test_linker_comment_cross_references_record`'s brace-tracking loop (adds `memory_idx`, changes the brace-detection condition); the needle-miss assert, the forbidden-clause assert, and the non-vacuity assert immediately following are byte-unchanged in the diff |
| F21 | Pre-edit linker content (`5a89ee7^` = `2ef7b57`) lacks the four needles (re-check b, part 1) | `0` for each of `FLASH-PATH-AND-PCB.md`, `v1.23-FLASH-PATH-DECISION.md`, `__VTOR_PRESENT`, `SCB->VTOR` | **`0`, `0`, `0`, `0`** — all four absent from `git show 5a89ee7^:platform/py32f071/linker/PY32F071xB_FLASH.ld` |
| F22 | Pre-edit linker content carries the false clause (re-check b, part 2) | at least one match for `no VTOR` (case-insensitive) | **1 match**: `"...table address changes, on a part with no VTOR. Phase 129 must record the..."` — confirms the RED-preserving proof was sound: the pre-edit leg failed on a genuine needle-miss against real, uncorrected prose, not on a fabricated fixture |
| F23 | `5a89ee7` diff scope (the D-11 comment edit, re-check c) | comment-only; no `ORIGIN`/`LENGTH`/`PROVIDE`/`ASSERT`/`_estack`/`_Min_` line changed | **Confirmed** — `git show 5a89ee7 -- platform/py32f071/linker/PY32F071xB_FLASH.ld \| grep -E '^[+-]' \| grep -E 'ORIGIN\|LENGTH\|PROVIDE\|ASSERT\|_estack\|_Min_'` returns **zero lines**; the diff touches only comment text inside the `BOOTLOADER` block |
| F24 | Seed frontmatter re-read | `status:` reflects the fired trigger, four-field schema unchanged | **Confirmed** — `status: partially realised — the factory-USB-DFU runner-up shipped in v1.23 (the trigger fired); the self-flash primary route has not, and the seed stays live for FUT-N05`; frontmatter keys still exactly `title`, `trigger_condition`, `planted_date`, `status` |

**Ten fail-closed legs, named** (all re-run green in this session, part of F5's 41):
`test_absent_meta_root_skip_is_auditable_not_silent`, `test_absent_meta_claim_can_never_be_false`,
`test_present_root_with_missing_target_raises_not_skips`, `test_marker_name_is_not_overridable`,
`test_empty_extraction_is_not_a_vacuous_pass`, `test_renamed_marker_yields_a_refusal_not_a_guess`,
`test_duplicate_marker_refuses_to_guess`, `test_planted_divergence_in_synthetic_copies_is_detected`,
`test_dirty_tree_is_detected`, `test_git_binary_is_required_not_optional`.

### Meta repo (`/workspaces`)

| # | Command | Expected | Observed |
|---|---|---|---|
| M1 | `git rev-parse --abbrev-ref HEAD` | `gsd/v1.23-py32f071-integration` | **`gsd/v1.23-py32f071-integration`** |
| M2 | `git status --porcelain` | ` M firestarter`, ` M firestarter_app` (pre-existing, unrelated) | ** M firestarter** (gitlink awaiting this plan's bump), ** M firestarter_app** (pre-existing dirty gitlink from unrelated local changes in that submodule) |
| M3 | `git diff --submodule=short -- firestarter` | shows the pending bump to `5a89ee7` | **`7a0a375 → 5a89ee7`** — matches 129-07's recorded firmware HEAD exactly |
| M4 | `grep -cE '^- \[ \] \*\*PCB-0[1-5]\*\*' .planning/REQUIREMENTS.md` (before this plan's Task 3) | `5` (none ticked yet) | **5** — confirms no prior plan ticked any of PCB-01…PCB-05 |
| M5 | `git log --oneline -- .planning/REQUIREMENTS.md` / `.planning/ROADMAP.md`, scanned for any Phase-129 plan commit other than the phase-plan-creation commit | none | **None found** — the only Phase 129 commit touching either file is `c9fd3a6` ("create phase plan"), which added the plan files, not a tick |

### ARM byte-identity row (executed locally in this session)

**Toolchain versions**, re-confirmed in this session (already present in this devcontainer — no
install needed): `arm-none-eabi-gcc (15:14.2.rel1-1) 14.2.1 20241119`; `GNU size (2.44-3+23+b1)
2.44`; `cmake version 4.4.0`; `ninja 1.13.0.git.kitware.jobserver-pipe-1`.

**Resolved SDK commit**, from the fresh scratch build's FetchContent source directory:
`0ed2f4b4d3391eccfd4491006a30295fd78e32c2` — string-equal to the pinned `GIT_TAG` in
`platform/py32f071/CMakeLists.txt`.

**Scratch build path (this session, distinct from 129-07's retained path)**:
`/tmp/claude-1000/-workspaces/86849fd7-9545-494f-9bd5-e6c07c0c1a8a/scratchpad/py32f071-d13-129-09`
— a fresh `cmake -G Ninja` configure against the final tree at HEAD `5a89ee7`, never reusing
129-07's cached build.

**Baseline build** (`before.txt`, HEAD `5a89ee7`, no edits):
```
66b6a8dca982d6c6a6fb8bf19a99a0b9197b261950be1f118f1677753c5b495e  firestarter_py32f071.bin
9599a625b1bc7357ec512952f76ee27c6897fabd1c7a1eb4645068c1935913dc  firestarter_py32f071.hex
   text	   data	    bss	    dec	    hex	filename
  27260	    112	   5888	  33260	   81ec	firestarter_py32f071.elf
```
`before-build.log` ends `[42/42] Linking CXX executable firestarter_py32f071.elf` — 41 `Building`
lines + 1 `Linking` line, 42/42 objects built from a cold configure, exit 0.

**Throwaway comment-only edit applied to the real linker script** (one line added inside the
`BOOTLOADER` comment block, immediately reverted after the rebuild below), then an **incremental
rebuild, no reconfigure**:
```
66b6a8dca982d6c6a6fb8bf19a99a0b9197b261950be1f118f1677753c5b495e  firestarter_py32f071.bin
9599a625b1bc7357ec512952f76ee27c6897fabd1c7a1eb4645068c1935913dc  firestarter_py32f071.hex
   text	   data	    bss	    dec	    hex	filename
  27260	    112	   5888	  33260	   81ec	firestarter_py32f071.elf
```
`after-build.log`: `[1/1] Linking CXX executable firestarter_py32f071.elf` — **zero objects
recompiled** (`grep -c "Building" after-build.log` → `0`), confirming `LINK_DEPENDS` forced a real
relink of the changed source, not a vacuous no-op. `diff before.txt after.txt` → empty, exit 0.
**Both digest pairs are byte-identical.**

These digests match the values 129-07 recorded from its own (separately built, retained) scratch
directory — an independent confirmation from a fresh configure and a fresh build tree, not a
re-read of the same files.

**Revert and clean-tree confirmation:** `git checkout -- platform/py32f071/linker/PY32F071xB_FLASH.ld`
followed by `git status --porcelain` → **0 lines**, and `git diff HEAD -- platform/py32f071/linker/PY32F071xB_FLASH.ld`
→ **0 lines**. The firmware working tree is clean at HEAD `5a89ee7` after the D-13 re-run.

**The two honesty ceilings, restated as their own sentences:** (a) these are delta-comparable
figures only — same local tree, same local toolchain, two builds in one session — and must never
be set beside a CI figure, because no CI run exists for this ARM target this phase and the local
GCC would in any case differ from a CI GCC. (b) A byte-identical image proves the emitted output
did not change; it proves nothing about whether the image runs, boots, or installs, and no
PY32F071 hardware exists on which to find out.

---

## 3. Deliberately empty — no CI dispatch, no operator gate

The two analogs this document otherwise follows (`128-NONREGRESSION.md`, `126-NONREGRESSION.md`)
each carry a §3 of CI-only evidence discharged by an operator-authorised dispatch, and a §4
operator dispatch procedure. This document has neither, on purpose: D-13 forbids an ARM CI run
this phase — the only firmware edits are a new `.md` file and a linker comment, neither of which
can change emitted output in a way that needs CI to observe. The byte-identity evidence that would
otherwise live in a CI-only section instead moved **into §2** as a locally executed row (the "ARM
byte-identity row" above), because it is fully dischargeable locally and CI would add nothing to
it. This is a deliberate structural deviation from the two analogs, recorded here rather than left
for a reader to notice as an omission.

---

## 4. Success criteria

Quoted verbatim from `.planning/ROADMAP.md` §"Phase 129: Flash-Path Decision & PCB Requirements
Record".

### Criterion 1

> *"A committed ADR-style record names the three-tier flash path — self-flash bootloader over
> CDC+COBS as intended primary, factory USB DFU as maintainer/manufacturing recovery, SWD as last
> resort — and states explicitly, in the same document, that landing the DFU path this milestone
> does **not** retire the self-flash seed."*

Discharged as written. §2 of `.planning/v1.23-FLASH-PATH-DECISION.md` (`[SHARED:S1]`) fixes the
three tiers in priority order with the exact roles named, and carries `_L1_NON_RETIREMENT`
verbatim (F12 above: 1 match in each copy). `test_three_tiers_and_non_retirement[meta]`/`[fw]`
both pass (F5).

### Criterion 2

> *"The record lists PCB requirements as distinct, checkable line items — BOOT0/nBOOT1 strap
> reachability, exposed SWD pads, a contiguous 8-bit GPIO port for the data bus, and a depopulated
> HSE footprint — not prose paragraphs."*

Discharged as written. §3 (`[SHARED:S2]`) carries seven checkbox rows (R1–R7), each with exactly
one `*Why:*` and one `*Breaks if omitted:*` line (F9/F10), covering all four named items (R1, R2,
R3, R4) plus three additional items this milestone surfaced (R5 VPP sense, R6 test points, R7 USB
connector/D+ pull-up), per D-14. `test_pcb_checklist_rows_are_wellformed[meta]`/`[fw]` both pass.

### Criterion 3 — vector-relocation implication on a part with no VTOR (AMENDED — read this carefully)

> *"The record's flash-budget section cites the actual reserved addresses/sizes from Phase 126's
> linker symbols (not a pre-Phase-126 estimate), including the bootloader region and a stated
> vector-relocation implication for a part with no VTOR."*

**This criterion's premise is false, and satisfying its literal wording would require writing a
false statement into the record.** Research finding C-1 (independently re-verified in this
session, §2 F21/F22) establishes that the PY32F071 **has** a VTOR (`__VTOR_PRESENT 1` in the
pinned SDK's CMSIS device header; `SCB->VTOR` written unconditionally by the compiled `SystemInit`
at every boot) — the "for a part with no VTOR" premise in this criterion, in `REQUIREMENTS.md`
PCB-03, and in the linker script's own comment (before `5a89ee7`) were all wrong on the same
point, traced to the same unverified assumption.

**What the record states instead:** §1.6 Correction 1 and §4(d) of
`.planning/v1.23-FLASH-PATH-DECISION.md` (mirrored in the firmware subset's §"Flash budget, as
actually reserved") state the corrected implication precisely: the vector table relocation itself
is the **cheap** half (the hardware register handles it in one write); the **expensive** half is
the one-time fleet re-flash every already-flashed unit needs over DFU or SWD, because reserving
`BOOTLOADER` moves the application's `ORIGIN` — a flash-map migration, not a resize. This is a
stronger, more precisely-costed migration implication than the criterion's own wording asked for,
not a weaker one — it replaces a wrong reason with the correct one while keeping the same
practical conclusion (reserve the region, cost it explicitly, never present the figure as already
paid for).

**Disposition:** the operator was consulted during planning (research corrections C-1 and C-2 were
both escalated) and chose to correct the record's own prose and the linker comment (`5a89ee7`)
while explicitly leaving `REQUIREMENTS.md` PCB-03, `ROADMAP.md` Phase 129 criterion 3 (this
criterion), and `REQUIREMENTS.md` FUT-N04's deferral reason **unamended this phase** — §1.6 and §8
of the meta record name **Phase 130's CLOSE-01** sweep as the owner of that prose correction by
design, so the correction stays visible until CLOSE-01 lands it rather than being silently folded
away here. The substantive intent of the criterion — a stated migration implication attached to
the bootloader region — is discharged in full by §4's flash-budget section; only the "no VTOR"
premise is corrected, and that correction is recorded, not hidden.

### Criterion 4

> *"The record names a specific USB VID/PID decision (replacing the undocumented `0x36B7`/`0xFFFF`
> placeholder) with its sourcing basis and an explicit statement that squatting becomes a liability
> the moment a board ships."*

**Partial amendment, recorded as such.** The criterion's premise describes the placeholder as
*undocumented*; §5(a) of the record establishes its exact upstream provenance instead (allocated to
Puya Semiconductor; the exact `36B7:FFFF` pair copied verbatim from the pinned SDK's own USB CDC
example, `usbd_cdc_if.c:9-10`, corroborated by `pycdc.inf:28,31` — F12 above confirms the needle
set including `Puya Semiconductor`, `usbd_cdc_if.c`, `pycdc.inf` is present in both copies via
`test_vid_pid_decision_and_ship_gate`). The criterion's verb *"replaces"* is satisfied by a
**recorded decision plus a tracked obligation** (§5(b)/(f) and §8: pid.codes VID `0x1209`, interim
`1209:0001`, the operator-filed pull request as the tracked next step), **not by a code change** —
`platform/py32f071/src/usb_cdc.c` is deliberately untouched this phase (D-06), which is what keeps
this phase free of an ARM rebuild for that reason. The obligation is named in §8's table: **"Edit
`usb_cdc.c` to the allocated identity"**, owner **a later phase or milestone**, trigger **the
allocation landing**.

### Criterion 5

> *"The socket-empty-before-any-py32-firmware-install safety instruction is documented somewhere a
> future installer/tester will read it, with an explicit statement of why it is stronger here than
> the comparable warning in other projects (the provisional pin map)."*

Discharged as written. §6 (`[SHARED:S5]`) carries `_L3_SOCKET_EMPTY` verbatim (F12) plus four
named reasons it is stronger here, mirrored in the firmware subset and pointed to from
`platform/py32f071/README.md` §"Hardware validation still required" (`test_socket_empty_instruction_present[meta]`/`[fw]`/`[readme]`, all pass, F5).

---

## 5. Decision coverage — D-01…D-18

| Decision | One line | Discharged in | Verified by |
|---|---|---|---|
| **D-01** | Two-layered record: meta authoritative + firmware subset | 129-03 (meta header), 129-06 (subset) | §2 F1/F17/F18; `test_shared_sections_match` (F5) |
| **D-02** | Milestone-prefixed decision doc at `.planning/` root, no ADR scheme | 129-03 | Filename `v1.23-FLASH-PATH-DECISION.md`, no `adr/` directory anywhere in the tree |
| **D-03** | Firmware layer is a subset, not a mirror; fail-closed sync gate with a planted-violation fixture | 129-01 (fail-closed half), 129-02 (parity/content half) | §2 F5/F6/F7; ten named fail-closed legs; `test_planted_mutation_of_the_real_subset_is_detected` |
| **D-04** | `firestarter_app` untouched this phase | every plan | §2 M2; header's explicit statement above |
| **D-05** | Meta gitlink bumped in-phase, not deferred | 129-09 (this plan, Task 3) | §2 M3 (pending-bump diff observed pre-Task-3); Task 3's commit |
| **D-06** | `usb_cdc.c` not edited; PCB-04 satisfied by decision + obligation | 129-05 | §4 Criterion 4 above; §8's tracked obligation row |
| **D-07** | pid.codes VID `0x1209` chosen | 129-05 | Record §5(b), needle `0x1209`/`pid.codes` (F12/`test_vid_pid_decision_and_ship_gate`) |
| **D-08** | Phase decides the route, does not request the PID; no agent files it | 129-05 | Record §5(f)/§8; this plan's own commit body states no registry request was filed |
| **D-09** | Hard ship gate: no board ships, no release advertises a USB identity, until a real PID exists | 129-05 | `_L2_SHIP_GATE` verbatim, F12 |
| **D-10** | Bootloader figure sector-quantised, every appearance carries its migration cost (proximity rule) | 129-04 | `test_bootloader_figure_carries_its_cost[meta]`/`[fw]` (F5) |
| **D-11** | Linker comment gets a comment-only cross-reference; `BOOTLOADER` region unchanged | 129-07 | §2 F16/F20/F23; `test_linker_comment_cross_references_record` (F5) |
| **D-12** | Vector relocation: state the cost, then enumerate candidates, each tagged with confidence | 129-04 (§4(d)), 129-03 (§1.6) | Record §4(d); §1.6 Correction 1 |
| **D-13** | No operator-gated ARM CI run this phase; prove locally instead | 129-07 (first proof), 129-09 (re-proof on final tree) | §2 "ARM byte-identity row" above |
| **D-14** | Four named PCB items plus what this milestone surfaced (VPP sense, test points, USB connector/pull-up) | 129-04 | Record §3 rows R1–R7; F9 |
| **D-15** | Reboot-into-bootloader recorded as an open question, board cost stated on both sides | 129-05 | Record §9 Open Question 3 |
| **D-16** | Each checklist row: checkbox + one rationale line + one consequence line | 129-04 | `_checklist_rows` parser + F9/F10 |
| **D-17** | Seed's `status:` updated to reflect the fired trigger, within its unchanged four-field schema | 129-08 | §2 F24; `test_seed_status_is_no_longer_dormant` (F5) |
| **D-18** | The new record is canonical for the flash-path decision; the seed points at it | 129-08 | Seed body contains `../v1.23-FLASH-PATH-DECISION.md` and `FUT-N05` (§2 F24) |

**Four further rows — the research corrections and operator escalations that arrived during
planning:**

| Correction | One line | Disposition |
|---|---|---|
| C-1 (VTOR) | The part **has** a VTOR; `SCB->VTOR` is written at every boot by the compiled `SystemInit` | **Escalated to the operator during planning.** Chosen: correct the record's own prose and the linker comment (`5a89ee7`); leave `REQUIREMENTS.md`/`ROADMAP.md`/FUT-N04 prose to Phase 130 CLOSE-01. See §4 Criterion 3 above for the full account. |
| C-2 (vendor identity) | `0x36B7` is allocated to Puya Semiconductor, not an unallocated squat; the pair is copied verbatim from the pinned SDK's own CDC example | **Escalated to the operator during planning.** Chosen: pid.codes `0x1209` with interim `1209:0001`, recorded as a decision plus a tracked obligation (D-06/D-07/D-09), `usb_cdc.c` left unedited. See §4 Criterion 4 above. |
| C-3 (toolchain) | The ARM toolchain is installable from the same packages CI uses, not absent from this devcontainer; the D-13 proof was executed successfully during research | This upgraded D-13's evidence from an argument to an executed proof — first run in 129-07, independently re-run on the final tree in this plan (§2 "ARM byte-identity row"). The record's Claim ceiling states the corrected, narrower "delta claims only" wording; `REQUIREMENTS.md` §"Validation Ceiling" still carries the older "absent from this environment" wording, tracked as an obligation for Phase 130 CLOSE-01 (record §8). |
| C-4 (size figure) | The seed's "a small bootloader in the first few KB" is measurably optimistic — this tree's own measured objects already total roughly `14.6 KiB` before any bootloader logic exists | Supplied the corrected reservation figure (3 sectors / 24 KiB) that the record's §4(c) sector-quantised verdict table and D-10's proximity rule are built around; superseded the seed's own figure specifically (record §4(e), seed's own dated status block per D-17/129-08). |

---

## 6. Precedent and prior art

- **The two-layered document pattern and its sub-repo subset** (D-01) mirrors
  `.planning/v1.7-SHIELD-REVS.md` + its firmware-repo subset, and the more recent
  `platform/py32f071/CONFIG-STORAGE.md` precedent Phase 126 established one phase earlier — same
  directory, same shape.
- **The milestone-prefixed decision-doc convention**, deliberately without an ADR numbering
  scheme (D-02): `.planning/v1.9-COBS-DECISION.md`, `.planning/v1.10-FRAMING-DECISION.md`,
  `.planning/v1.13-PROTOCOL-ENUMERATION.md` are the established precedents this record's filename
  follows; no `adr/` directory exists anywhere in this repository.
- **The presence-probe pattern this phase mirrored from the host repository:**
  `firestarter/tests/meta_presence.py` mirrors `firestarter_app/tests/fw_presence.py` part for
  part, adjusted for the parent-not-sibling (submodule) direction rather than the sibling-checkout
  direction the host-repo analog uses.
- **The planted-fixture doctrine** (BASE-08, Phase 123): every checker this milestone ships must
  demonstrate it can genuinely fail. This module's ten `TestFlashPathRecordSyncFailsClosed` legs
  and the `test_planted_mutation_of_the_real_subset_is_detected` leg against the real artifact are
  this phase's instance of that doctrine.
- **The premature-tick guard:** eight of this phase's nine plans (129-01 through 129-08) were told
  explicitly, in their own plan text, not to tick any requirement — a restatement of the Phase 116
  4× premature-tick guard this project has now applied in Phases 125, 126, 128 and 129.

---

## 7. What this phase does NOT claim

- **No claim about how the silicon behaves.** No PY32F071 PCB exists; every claim in this document
  and in the record it verifies about *behaviour* — as opposed to what a document says or what this
  tree's source contains — carries `[UNVERIFIED-UNTIL-SILICON]` in the record itself. Bounds:
  Criterion 3's corrected vector-relocation cost, and every §1 subsection's confidence tag.
- **No claim that the pin assignments match any board.** The provisional pin map (`platform/py32f071/README.md`,
  `RURP_PY32F071_PINMAP_PROVISIONAL`) describes no existing PCB — this is precisely why §6's
  socket-empty instruction is stronger here than the AVR comparable. Bounds: Criterion 5 and §2 F12
  (`_S5_NEEDLES` including `provisional`, `RURP_PY32F071_PINMAP_PROVISIONAL`).
- **No claim that the bootloader reservation figure is anything but an estimate with a stated
  method.** §4(c)'s "roughly 17 to 20 KiB" figure is measured-plus-estimated, explicitly tagged
  `[ASSUMED]`, never presented as a final number. Bounds: §4's sector-quantised verdict table and
  D-10's proximity rule (every appearance of the figure carries its migration cost, F9/F10-style
  proximity checks via `test_bootloader_figure_carries_its_cost`).
- **No claim that a vendor identity has been allocated.** The interim `1209:0001` is a sanctioned
  private-testing id, not an allocation; the hard ship gate (`_L2_SHIP_GATE`) exists precisely so no
  board ships and no release advertises a USB identity until a real PID is allocated. Bounds:
  Criterion 4 above and §8's tracked-obligation row ("File the pid.codes pull request").
- **No claim that the sync gate runs in CI on this branch.** `tests/test_flash_path_record_sync.py`
  executes in **no CI leg** on `v1.23-py32f071-integration` — `pytest tests/` runs only in
  `build.yml` (push/PR to `main`) and `beta-build.yml` (push to `beta`), neither of which fires on
  this milestone branch, and `py32f071.yml` has no pytest step at all. The local run recorded in §2
  is the only evidence this module's assertions were ever exercised. Bounds: every F5/F6/F7 row
  above, all executed as a **local** run in this session, never implied as CI-covered.
- **No claim that the byte-identical image runs.** §2's ARM byte-identity row proves the emitted
  output is unchanged across two local builds; it says nothing about whether the image boots or
  installs on real silicon. Bounds: the two honesty ceilings restated as their own sentences at the
  end of §2.
- **No claim that any absolute size figure here is comparable to a CI figure.** Every ARM number in
  this document (`27,372` B application footprint, `14.6 KiB` measured bootloader components, the
  `text`/`data`/`bss` triple) is a **local**, delta-comparable figure only — this milestone has no
  ARM CI run to compare it against, and even if one existed, the local and CI compilers differ.
  Bounds: §2's ARM byte-identity row and its closing two-sentence ceiling.

---

## 8. Deviations recorded during planning and execution

**The fully serial wave structure (9 waves for 9 plans), and why.** Every plan in this phase either
writes into one of the two copies of the record or discharges legs of the one shared gate module,
so parallelism would have made every expected-count criterion (RED ledgers dropping from 31 to 29
to 24 to 20 to 0, gate totals climbing from 10 to 41) order-dependent and therefore
non-reproducible. Determinism was worth more than wall-clock time here, given this milestone has
already paid four times for cross-repo gates that passed without observing anything (research
finding A-7).

**The fifth shared section beyond D-03's original four, and why PCB-01 required it.** D-03 named
PCB checklist, flash budget, VID/PID decision, and socket-empty warning as the firmware layer's
subset content. PCB-01's three-tier flash-path decision (`[SHARED:S1]`) is a fifth shared section
this record added, because PCB-01's "does not retire the seed" statement needs to be checkable from
the firmware subset too, not only from the meta record — a schematic author working in the firmware
repo should be able to find the whole flash-path decision, not four of its five load-bearing pieces.

**The wholesale replacement of the linker comment block rather than a clause-level edit, and why.**
D-11's fix (`5a89ee7`) replaced the entire `BOOTLOADER` comment block rather than deleting only the
two-word "no VTOR" clause, because the corrected cost statement needed room to name both record
layers and restate the corrected migration cost in the same breath — a surgical two-word deletion
would have left a comment that named nothing to consult and stated a truncated cost with no
attribution. The scope was still comment-only: no `MEMORY`/`FLASH`/`CONFIG`/`RAM` region line,
`PROVIDE`, `ASSERT`, or symbol changed (§2 F23).

**The gate module committed RED before either record existed, and why.** Plan 129-01 committed the
fail-closed half and Plan 129-02 committed the 31-leg parity/content class before
`.planning/v1.23-FLASH-PATH-DECISION.md` or the firmware subset existed — Phase 123's
authored-after-the-content-it-judges doctrine, so a bisector encountering the RED commits can read
the commit message and tell deliberate RED from a regression, rather than a gate written after the
fact that can only bless what already happened.

**The three discretion resolutions the operator delegated, each with its resolution and
rationale:**

1. **The socket-empty instruction's placement and strength.** CONTEXT.md left open where PCB-05's
   instruction should land and whether it should stay documentation or become an installer-time
   prompt. Resolved: it stays documentation, repeated verbatim in both copies of the record plus a
   pointer-and-one-sentence addition to `platform/py32f071/README.md` §"Hardware validation still
   required" (the nearest existing text a bring-up reader already opens) — an installer-time
   prompt was never available this phase because `firestarter_app` is out of scope (D-04), and
   propagating the instruction into the host installer documentation is tracked as an obligation
   for Phase 130 or a later host phase (record §8).
2. **The per-claim sourcing discipline.** CONTEXT.md left open whether every claim should carry a
   sourcing tag and an "unverified until silicon" marker, or whether one blanket caveat would
   suffice. Resolved: both — five per-claim confidence tags (`[VERIFIED]`, `[CITED]`, `[ASSUMED]`,
   `[UNVERIFIED-UNTIL-SILICON]`, plus their qualified forms) appear in headings and mid-sentence
   throughout §1 and the shared sections, **and** a blanket closing `## Claim ceiling` states the
   ceiling once for a reader who wants the short version — the record's own "Confidence tags used
   in this document" paragraph states these are complements, not alternatives, because Phase 130's
   CLOSE-02 honesty ledger consumes the per-claim pairs while a casual reader needs the one-section
   summary.
3. **The mechanism of the D-03 sync gate.** CONTEXT.md left the gate's mechanism to planner
   discretion. Resolved: a fail-closed pytest module built on a single shared-section extractor
   (`_extract_shared_section`/`_shared_sections`), a hard-failure (`MissingScanTargetError`, never
   a skip) for a present meta repo with a missing scan target, a subprocess re-invocation to test
   import-time-bound module constants under a different `FIRESTARTER_META_ROOT`, and a
   planted-mutation ceremony run against the real firmware subset file (not only a synthetic
   fixture) — the shape this milestone has settled on since Phase 123's BASE-08 doctrine, chosen
   specifically because plain lockstep discipline has already failed to catch four gate breakages
   this milestone (research finding A-7).

**Every deviation the executors recorded in their own SUMMARY files, cross-referenced here rather
than restated:**

- 129-01/129-02: two wording adjustments to satisfy the plans' own literal grep acceptance criteria
  (no behaviour change) — recorded in those SUMMARYs' "Issues Encountered"/"Decisions Made"
  sections.
- 129-06: a CLAUDE.md line-wrap self-correction, caught by the plan's own acceptance grep before
  any commit.
- **129-07 (the phase's substantive deviation): a genuine, pre-existing defect in the frozen gate
  test `test_linker_comment_cross_references_record`, found, escalated to the operator, and fixed
  under an explicit RED-preserving proof, rather than worked around.** The defect: the leg's
  brace-detection loop required `"MEMORY"` and `"{"` to co-occur on one source line, which the
  linker script's real two-line GNU-ld `MEMORY`/`{` convention never satisfies — the leg was
  unreachable since it was authored in Plan 129-02, independent of any comment content. The
  operator authorized a narrow, locator-only fix (`2ef7b57`) conditioned on a RED-preserving proof:
  revert the D-11 comment edit, confirm the single leg still fails — on a needle-miss, not the
  former "could not locate" error — then restore the edit and confirm green. This plan
  independently re-verified all three legs of that proof in this session (§2 F20/F21/F22/F23) and
  found them sound: the locator diff touches only the brace-tracking loop; the pre-edit content
  genuinely lacked all four needles and genuinely carried the false "no VTOR" clause; and the D-11
  edit itself is comment-only.

---

## Claim ceiling

`no PY32F071 hardware exists` — stated in the exact form the milestone claim gate matches. This
document defers to `.planning/REQUIREMENTS.md` §"Validation Ceiling" for the full, authoritative
list of permitted and forbidden claims **by reference rather than by restating its wording** — the
gate's own forbidden-phrase table (eight patterns) and required-caveat pattern are named here only
by count and by file path
(`.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py`), never
quoted, per the Phase 125 self-reference trap this phase's own PATTERNS.md and RESEARCH.md warn
against: three of that checker's own phrase-table labels are themselves matches for their own
patterns, so quoting them inside a compliance paragraph is exactly what tripped all six of Phase
125's own SUMMARY files.

**Claim gate, run against all three durable artifacts, explicit argv:**

```
$ python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py \
    .planning/v1.23-FLASH-PATH-DECISION.md \
    firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md \
    .planning/phases/129-flash-path-decision-pcb-requirements-record/129-NONREGRESSION.md
```
Result recorded in this plan's SUMMARY (run after this document was written and its self-scan
could be meaningful) — see `129-09-SUMMARY.md` for the verbatim `PASS:`/exit-code capture, per this
phase's own discipline that the artifact itself must be scanned after it exists, not predicted in
advance.

---

## Sweep Summary

| Gate | Result |
|---|---|
| Firmware `git rev-parse --abbrev-ref HEAD` / `HEAD` / porcelain | `v1.23-py32f071-integration` / `5a89ee76dc4681abe18db259e57bb92f519520f4` / 0 lines |
| `pytest tests/ -q` (whole firmware suite) | **221 passed**, 0 failed, 0 skipped (re-confirmed twice: before and after the D-13 re-run) |
| Gate module `tests/test_flash_path_record_sync.py` | **41 passed** — 10 fail-closed legs + 31 parity/content legs |
| Fail-closed re-demonstrations | absent-meta-root skip names the resolved marker path; present-root-missing-target raises `MissingScanTargetError` |
| Meta record structure | 11 `## ` headings, 5 `[SHARED:Sn]` markers, 7 R1–R7 rows with 7 Why/7 Breaks lines each, 1 `### Deliberately undecided`, 3 exact literals each present once |
| Firmware subset structure | 0 numbered `## ` headings, 1 `## Claim ceiling`, 5 `[SHARED:Sn]` markers, 3 exact literals each present once |
| Negative greps (no-VTOR-workaround terms, claim-gate forbidden phrases) | 0 on both records |
| Linker script | 0 false-"no VTOR" matches, 1 unchanged `BOOTLOADER` region line |
| Claim gate, meta + subset (Task 1, pre-this-document) | exit 0, `PASS:` naming both files |
| D-13 re-run, fresh scratch dir on the final tree | byte-identical digests, confirmed real relink both directions, firmware tree clean afterwards |
| Wave-7 deviation re-check (a/b/c) | all three confirmed sound: locator-only diff, genuine pre-edit needle-miss + false clause, comment-only D-11 edit |
| Meta gitlink pending bump | `7a0a375 → 5a89ee7`, string-equal to 129-07's recorded firmware HEAD |
| `firestarter_app` | untouched, confirmed via pre-existing dirt unchanged |
| REQUIREMENTS.md / ROADMAP.md prior state | PCB-01…PCB-05 all still `[ ]` before this plan's Task 3; no other Phase 129 plan touched either file |

**This phase's entire verification surface is green.** The one substantive deviation (the wave-7
gate-defect escalation) is recorded honestly in §8, independently re-verified in §2, and does not
weaken any claim this document makes. This plan ticks PCB-01…PCB-05 in `.planning/REQUIREMENTS.md`,
each citing the section above that discharges it.
