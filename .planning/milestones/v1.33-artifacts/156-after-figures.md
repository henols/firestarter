---
title: After-figures record -- milestone v1.33, Phase 156 (Duplicated-Report Extraction + Boolean-Convention Repair)
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "07"
measured: 2026-08-23
status: AUTHORITATIVE -- this file is the phase's outcome record, re-measured against the
  committed tree at `firestarter` `1151dc4`, never merely transcribed from an earlier plan's
  SUMMARY. Phases 157 and 158 each invalidate the size figures captured here (157 edits
  `json_parser.c`/`firestarter.h`; 158 re-anchors `size_baseline.json` and cold-rebuilds), so
  no later plan can re-derive them from this position.
supersedes: >
  ROADMAP.md Phase 156 success criteria 1, 2 and 4, and REQUIREMENTS.md DEDUP-01 through
  DEDUP-04 prose, wherever they state a figure this file corrects -- C-1 through C-7, the
  planner-found `src/operation_utils.cpp:58` location, and the discrepancy-beyond-the-seven
  pytest baseline, all first identified in `.planning/milestones/v1.33-artifacts/156-before-figures.md` and closed
  out here against the shipped code.
requirements: [DEDUP-01, DEDUP-02, DEDUP-03, DEDUP-04]
---

# After-figures record -- v1.33 Phase 156

This is the phase's landing record: the eight-leg phase gate run and recorded on the final
tree, the four DEDUP-03 planted transpositions re-proven against the shipped (post-refactor)
code rather than the pre-refactor code plan 02 wrote them against, the resolved -268/-158
split, the mechanical `__udivmodhi4` ledger, DEDUP-02's six-divergence resolution, the seven
coverage ceilings in their final form, and the corrections index closed out. Every figure
below carries the verbatim command that produced it, measured this session against
`firestarter` `1151dc4` on `gsd/v1.33-source-hygiene-firmware-size-reduction`.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_PRE_SHA` | `adf1a312804b6d1cfc7a6a8aa054d58bdf3188cd` (`adf1a31`) -- 156-01's before-figures anchor |
| `FW_POST_SHA` | `1151dc497254ea7dc5dd6395d10cb76791236938` (`1151dc4`) -- HEAD of `gsd/v1.33-source-hygiene-firmware-size-reduction`, this phase's last landed commit (156-06) |
| `firestarter` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` (unchanged by this plan) |
| Commit count `FW_PRE_SHA..FW_POST_SHA` | **6**, derived: `git rev-list --count adf1a31..HEAD` |
| `git -C firestarter status --porcelain` | empty, asserted before and after every measurement step in this session |
| `git -C firestarter worktree list` | `/workspaces/firestarter` (primary) + `/workspaces/firestarter_py32_ci` (pre-existing, unrelated, untouched) -- this plan's own throwaway worktree (§6) was removed and pruned before this record was written |
| meta repo HEAD (before this plan's own commit) | `e442e1f8e6722cde855a1e5743cff8cc4ee7ef56` |

Commands:
```bash
git -C firestarter rev-parse HEAD
git -C firestarter status --porcelain
git -C firestarter rev-list --count adf1a31..HEAD
git -C firestarter log --oneline adf1a31..HEAD
git -C firestarter worktree list
```

**Commits, listed by subject, reconciled against the per-plan record (not asserted):**

| # | Hash | Subject | Plan |
|---|---|---|---|
| 1 | `c764e27` | test(156-02): pin the under-voltage severity pairing that nothing asserted | 02 (task 1) |
| 2 | `3d0b73d` | test(156-02): pin the chip-ID mismatch message id in both fork directions | 02 (task 2) |
| 3 | `6bc3ed3` | refactor(156-03): one shared VPP-mismatch report replaces four copy-pasted blocks | 03 |
| 4 | `2065559` | refactor(156-04): one shared chip-ID mismatch report replaces four drifted copies | 04 |
| 5 | `735aff5` | refactor(156-05): the op layer returns true when finished, so nine wrappers stop negating it | 05 |
| 6 | `1151dc4` | test(156-06): pin the boolean convention with a non-vacuous source contract | 06 |

**Reconciliation:** this plan's own task text anticipated "5 -- two from plan 02, one each from
plans 03, 04, 05, and one from plan 06, which is 6". The measured count is **6**, matching that
reconciled arithmetic exactly (plan 02 alone contributed 2 commits, one per task, per its own
SUMMARY) -- not the naive "5" a reader might assume from "one commit per plan". No count in this
file is asserted without being derived from the log above.

**`firestarter_app` gitlink note:** meta's `git status --porcelain` shows `firestarter_app` as
modified. `git diff --stat -- firestarter_app` is **empty** -- there is no gitlink SHA change;
the submodule's own working tree carries pre-existing, untracked content (Phase 154 drift,
operator-gated). Not touched, staged or re-pinned by this plan.

**`firestarter` gitlink:** shows a genuine one-line SHA change (to `1151dc4`), reflecting this
phase's own six landed commits. Re-pinning it into a meta commit is **out of scope for this
plan** -- this plan's own commit (§Task 3) stages `.planning/` paths only, per the repo topology
instructions governing this execution.

---

## 2. The phase ledger -- flash and RAM, before vs after, per target

| Target | Flash before | Flash after | Delta | RAM before | RAM after | Delta |
|---|---|---|---|---|---|---|
| `uno` | 24660 | **24234** | **-426** | 1567 | **1567** | 0 |
| `uno328pb` | 24708 | **24282** | **-426** | 1573 | **1573** | 0 |
| `leonardo` | 26804 | **26378** | **-426** | 2008 | **2008** | 0 |

Command: `pio run -e uno -e uno328pb -e leonardo`, read via each target's `RAM:` / `Flash:`
summary line, this session against the real committed tree at `1151dc4`.

**Leonardo Caterina headroom against the 28672 B cliff:** before `28672 - 26804 = 1868` B;
after `28672 - 26378 = 2294` B. Computed from the flash figures above, not independently
re-measured by a separate command.

**Per-requirement split -- C-3, resolved:**

| Requirement | Plan | Own measured delta (all 3 targets) |
|---|---|---|
| DEDUP-01 | 03 | **-268 B** |
| DEDUP-02 | 04 | **-158 B** |
| **Sum** | | **-426 B**, matching the phase total in the table above exactly |

`.planning/milestones/v1.33-artifacts/156-before-figures.md` C-3 recorded this split as **UNVERIFIED** at the
phase's start -- only the combined `-426 B` was measured then. Plans 03 and 04 each measured
their own half independently, in their own commits, against the position immediately
preceding their own edit. The two halves **CONFIRM** the split ROADMAP's Phase 156 entry
carried (`-268` / `-158`) exactly -- this is not a case where the measured values supersede
the inherited split; they match it. State this as CONFIRMED, not SUPERSEDED, and cite the
measured values (`-268`, `-158`) rather than presenting the inherited figures as measured on
their own.

---

## 3. DEDUP-04's size-identity result

Plan 05's own measurement, re-confirmed this session against the currently committed tree
(§2's `uno` 24234/1567, `uno328pb` 24282/1573, `leonardo` 26378/2008 are byte-for-byte the
same six numbers plan 04 committed immediately before plan 05's flip landed) -- **size-identical
on all three AVR targets, flash and RAM both.**

`.hex` SHA-256 pairs, **plan 05's own measurement** (not research's), pre-flip (`2065559`,
throwaway worktree) vs post-flip (`735aff5`, the real commit):

| Target | Pre-flip `.hex` SHA-256 | Post-flip `.hex` SHA-256 |
|---|---|---|
| `uno` | `853dabb4...` | `8f5e9169...` |
| `uno328pb` | `bf226ea0...` | `ec768c16...` |
| `leonardo` | `e5d52522...` | `099b8c75...` |

All three `.hex` files **differ**. Cause: a uniform two-byte relocation plus branch-polarity
(`brne`/`breq`) swaps, on a build proven reproducible first (`156-05-SUMMARY.md`; the
5450-line `avr-objdump` diff figure is research's own measurement, not independently
re-diffed this session). The claim that may be made is **size-identity on all three AVR
targets** -- an oracle asserting image identity would go RED, because the SHA pairs above
show it does.

**The nine-to-one negation reduction:** the nine `return !op_execute_*_operation(...)`
call sites in `src/eprom_operations.cpp` are now nine plain forwarding returns
(`grep -cE '^\s*return op_execute_(stateful|simple)_operation' src/eprom_operations.cpp` ->
`9`; `grep -c 'return !op_execute_' src/eprom_operations.cpp` -> `0`, re-confirmed this
session). Exactly **one** negation survives in the engine itself:
`return !callback(handle);` at `src/operation_utils.cpp:92` (`grep -n 'return !callback'` ->
one match, this line), the MAIN-phase delegation to `_process_incoming_data` /
`_process_outgoing_data`. **Site 4 keeps its negation because those two callbacks keep their
own, independent true-on-success convention** -- flipping them too would cascade into
`set_operation_to_done` and was never measured, so it stays explicitly out of scope
(`156-05-SUMMARY.md`). This is a 9-to-1 reduction, not an elimination, and is stated that way
here.

---

## 4. The mechanical criteria

`__udivmodhi4` call sites, `uno`, this session:
```bash
OBJDUMP=~/.platformio/packages/toolchain-atmelavr/bin/avr-objdump
$OBJDUMP -d .pio/build/uno/firestarter_uno.elf | grep -cE '(r?call|jmp).*__udivmodhi4'
```
Result: **13** (before, per `156-before-figures.md` §4: **31**, measured at `adf1a31`).

**Derived arithmetic, restated:** `31 - 13 = 18` net sites removed. The one new helper that
performs division (`mem_util_report_voltage`) disassembles to exactly 6 `__udivmodhi4` call
sites of its own (confirmed by plan 03; `mem_util_report_chip_id` performs integer-equality
comparison only and carries none, confirmed by plan 04's own observation that the count held
at 13 across DEDUP-02's landing). So the four original packing blocks held `18 + 6 = 24`
sites -- the before-figures record's "24 of them" derived claim is unaffected by the C-2
correction (31, not 30) and is restated here against the corrected baseline.

`__udivmodsi4`: **0** newly introduced by either helper; **12** pre-existing, unrelated sites
remain (unchanged before and after, per plans 03/04's own throwaway-worktree cross-checks
against the pristine pre-edit tree; re-confirmed this session:
`$OBJDUMP -d .pio/build/uno/firestarter_uno.elf | grep -cE '(r?call|jmp).*__udivmodsi4'` -> `12`).

**Per-symbol ledger, `uno`**, this session (`avr-nm --print-size --size-sort -C
.pio/build/uno/firestarter_uno.elf`):

| Symbol | Before | After | Delta |
|---|---|---|---|
| `eprom_check_vpp` | 524 | 280 (`0x118`) | -244 |
| `flash_intel_write_init` | 562 | 348 (`0x15c`) | -214 |
| `flash_util_check_chip_id_execute` | 192 | 118 (`0x76`) | -74 |
| `flash_intel_check_chip_id` | 220 | 146 (`0x92`) | -74 |
| `eeprom28c_write_init` | 430 | 374 (`0x176`) | -56 |
| `eprom_internal_check_chip_id` | 260 | ABSENT (fully inlined) | -260 |
| `eprom_check_chip_id_execute` | 6 | 24 (`0x18`) | +18 |
| `mem_util_report_voltage` (new) | -- | 190 (`0xbe`) | +190 |
| `mem_util_report_chip_id` (new) | -- | 90 (`0x5a`) | +90 |
| **Sum** | | | **-624** |

`eprom_internal_check_chip_id` confirmed **ABSENT** from `avr-nm -C` output this session
(`grep eprom_internal_check_chip_id` on the symbol dump returns nothing).

**The ledger does NOT close: -624 B of symbol deltas against a measured -426 B image delta.**
This is recorded, not fudged, and the cause is named: LTO redistributes the inlined helper's
bytes into `main` and the surviving call sites rather than summing cleanly. Per-requirement,
this is not a uniform gap -- DEDUP-01's own symbol sum (`-244 - 214 + 190 = -268`) **closes
exactly** against its own measured -268 B image delta (plan 03). DEDUP-02's own symbol sum
(`-74 - 74 - 56 - 260 + 18 + 90 = -356`) does **not** close against its measured -158 B image
delta (plan 04) -- the entire -198 B non-closure is attributable to the chip-ID half, where the
larger `eprom_internal_check_chip_id` inlining redistributes further than the VPP half's.

---

## 5. The gate ledger -- all eight legs

| # | Leg | Result | Wall time | In CI? |
|---|---|---|---|---|
| 1 | `pio test -e native` (run 1) | 172 test cases: 172 succeeded, 17 suites | 21.6 s | yes |
| 1 | `pio test -e native` (run 2) | 172 test cases: 172 succeeded, 17 suites | 31.6 s | yes |
| 1 | `pio test -e native` (run 3) | 172 test cases: 172 succeeded, 17 suites | 32.6 s | yes |
| 2 | `pio test -e native_nodevtools` | 172 test cases: 172 succeeded, 17 suites | 32.6 s | yes |
| 3 | `python3 -m pytest tests/ -q` | **355 passed, 0 failed** | 12.67 s | yes |
| 4 | `pio test -e native_loop_v131` | **82 test cases: 82 succeeded**, 2 suites | 1.2 s | **no CI workflow invokes this env** |
| 5 | `pio run -e uno -e uno328pb -e leonardo` | flash 24234/24282/26378, RAM 1567/1573/2008 (see §2) | 1.6 s | yes (build) |
| 6 | DEDUP-03 both-directions evidence | see §6 below | -- | n/a |
| 7 | `python3 scripts/check_size_baseline.py --policy merge05 --rebuild` | **PASS** (see below) | 71 s | **no CI workflow invokes this script at all** |
| 8 | `python3 scripts/check_build_warnings.py --rebuild` | **PASS**, `macro_redefinition=0` on all three AVR targets | -- | n/a (local-run) |

**Leg 1's three runs, listed individually (D-04):** 21.6 s, 31.6 s, 32.6 s -- all three report
`172 test cases: 172 succeeded` over 17 suites, no variance in the count across repeated runs
this session.

**Leg 3's floor, stated as this plan's own task instruction phrased it:** "at least 314 passed
(313 pre-phase baseline plus plan 06's module)". Measured: **355 passed, 0 failed** -- the
canonical-checkout pre-06 baseline of 348 (`156-before-figures.md` §5) plus the 7 new legs
`tests/test_boolean_convention_source_contract_v133.py` added (`156-06-SUMMARY.md`), which
clears both the plan's stated 314 floor and the original ≥313 phase-gate floor comfortably.
No other test count moved.

**Leg 4:** `native_loop_v131` reports **82 test cases: 82 succeeded** over 2 suites
(`test_loop_eprom_v131` unchanged at 47, `test_vpp_eprom_v131` grown from 33 to 35 by plan
02's two new cases -- `47 + 35 = 82`). **No CI workflow invokes this environment** (its own
`platformio.ini` comment states "NO CI COVERAGE"); this leg is a local-run obligation.

**Leg 7 -- the one-sided policy, quoted from source, not from the ROADMAP:**
```bash
grep -n 'flash_delta > allowance\|ram_delta > ram_tolerance' scripts/check_size_baseline.py
```
`:697 if flash_delta > allowance:` and `:709 if ram_delta > ram_tolerance:` -- both are
strict-inequality, growth-only comparisons, confirmed this session by reading the source
directly. A **reduction** in flash or RAM therefore passes with **no named exemption** (D-03)
-- the first size movement in this project's history that needs none. Result:
```
PASS: uno(flash=24234/32768[-1314<=788=...]), uno328pb(flash=24282/32768[-1316<=788=...]),
leonardo(flash=26378/32768[-1252<=724=...]), native(cases=172,suites=17),
native_nodevtools(cases=172,suites=17)
```
`git diff --quiet -- scripts/baseline/size_baseline.json` exits **0** -- the baseline is
**byte-unchanged**. The re-anchor is Phase 158 / LAND-01's job, not this plan's.

Also run, the canonical form:
```bash
python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild
```
Exits **1**, cause: `native: cases baseline=141 observed=172` (and the identical cause for
`native_nodevtools`). This is the **pre-existing** BASE-01 native case-count mismatch, frozen
at Phase 124's count, reproduced again this session exactly as `156-before-figures.md` §8
predicted. **Owner: Phase 158 / LAND-03.** Stated plainly as pre-existing and **not** this
phase's failure -- the size-reduction diff touches zero files under `test/`.

**Both leg 4 and leg 7 run in no CI workflow at all** (confirmed by the same `grep -n` sweep
over `.github/build.yml` and `.github/beta-build.yml` that `156-before-figures.md` §5
performed; nothing new found this session). Every size and non-CI-native gate this milestone
leans on is a **local-run obligation** (LAND-04).

**Leg 8:**
```bash
python3 scripts/check_build_warnings.py --rebuild
```
`PASS: uno: macro_redefinition=0, uno328pb: macro_redefinition=0, leonardo:
macro_redefinition=0, native: total warnings observed=998 is 168 below watermark 1166
(INFO only), native_nodevtools: total warnings observed=998 is 168 below watermark 1166
(INFO only)`. No new warning recorded on any of the seven files this phase edited:
`src/proms/eprom.cpp`, `src/proms/flash_intel.cpp`, `src/proms/flash_utils.cpp`,
`src/proms/eeprom_28c.cpp`, `src/proms/memory.cpp`, `src/eprom_operations.cpp`,
`src/operation_utils.cpp`.

---

## 6. DEDUP-03's evidence -- the four-probe before-and-after table

All four probes planted in a single throwaway `git worktree add /tmp/probe156g/firestarter
1151dc4` (path ends `/firestarter`, per the worktree-naming requirement this tree's own
`tests/test_checker_convention.py::test_scope_is_firmware_only` enforces). Each substitution
reverted with `git checkout -- <file>` before the next was planted; the worktree was removed
(`git worktree remove --force`) and pruned (`git worktree prune`) after all four, and
`git -C firestarter worktree list` confirmed only the primary tree and the untouched
`firestarter_py32_ci` sibling remained.

| Probe | Substitution (post-refactor location) | Research's pre-plan-02 measurement | This session's result, against the shipped code |
|---|---|---|---|
| **A** | `src/proms/eprom.cpp`, over-voltage severity ternary: `force ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR` -> reversed | RED in `native_loop_v131` (3 cases), BLIND in `native` | **RED** in `native_loop_v131`: `83 test cases: 3 failed, 79 succeeded` (`test_vpp02_e1_write_init_error_exit_leaves_no_route_asserted` among the failures). **BLIND** in `native`: `172 test cases: 172 succeeded`, unchanged. Blindness attributed to **coverage ceiling 2**, not a regression. |
| **B** | `src/proms/eprom.cpp` AND `src/proms/flash_intel.cpp`, under-voltage pairing: `MSG_WARN_VPP_LOW, RESPONSE_CODE_WARNING` -> `..., RESPONSE_CODE_ERROR` | **BLIND EVERYWHERE** (blind spot 1) | **RED** in `native_loop_v131`: `83 test cases: 2 failed, 80 succeeded` -- `test_vpp04_e_undervoltage_warning_pairing_fires_by_id_with_payload_shape: Expected 2 Was 0` and `test_vpp04_f_flash_intel_undervoltage_warning_pairing: Expected 2 Was 0`. `native` unaffected (`172/172`). **This is blind spot 1's closure, re-proven against the shipped code** -- the mutation point now lives inside the shared `mem_util_report_voltage` helper and reaches both call sites (eprom.cpp and flash_intel.cpp) from one edit. |
| **C** | `src/proms/memory.cpp`, `mem_util_report_chip_id`'s response-code ternary: `warn_only ? RESPONSE_CODE_WARNING : RESPONSE_CODE_ERROR` -> reversed | RED in `native` (2 cases) | **RED** in `native`: `174 test cases: 2 failed, 170 succeeded` -- `test_migrated_mismatching_chip_id_errors` and `test_case7_mismatching_chip_id_with_force_warns` both fail. The mutation point has **moved**: pre-refactor it lived in four separate blocks; now one edit to the shared helper reaches all four call sites at once -- itself a property of the de-duplication, recorded here rather than left implicit. |
| **D** | `src/proms/memory.cpp`, `mem_util_report_chip_id`'s message-id ternary (response_code left correct): `warn_only ? MSG_WARN_CHIP_ID_MISMATCH : MSG_ERR_CHIP_ID_MISMATCH` -> reversed | **BLIND EVERYWHERE** (blind spot 2) | **RED** in `native`: `173 test cases: 1 failed, 171 succeeded` -- `test_case7_mismatching_chip_id_with_force_warns: Case 7 (chip-ID severity fork, WARN direction): MSG_WARN_CHIP_ID_MISMATCH must appear in the captured frame ids under FLAG_FORCE`. **This is blind spot 2's closure, in CI, re-proven against the shipped code.** |

**GREEN control** -- the real, committed, unedited tree at `FW_POST_SHA` `1151dc4`, not a
synthetic derivative, re-confirmed after every probe was reverted and again after the
worktree's removal: `pio test -e native` **172/172** (17 suites), `pio test -e
native_loop_v131` **82/82** (2 suites).

**The mechanism sentence:** severity rides entirely in the message id because every
`LOG_{WARN,ERROR}_ID_BYTES` macro is the same alias of `LOG_ID_BYTES`
(`include/logging_id.h:110` `#define LOG_ERROR_ID_BYTES(id, b, n) LOG_ID_BYTES((id), (b),
(n))`; `:119` the identical form for `LOG_WARN_ID_BYTES`, re-confirmed this session) -- so a
`response_code` assertion cannot see a transposed id (probe D's exact shape) and an id
assertion cannot see a swapped `response_code` (probe B's exact shape, before plan 02's own
id/pairing assertions existed). **Both halves are required, per path**, which is exactly why
DEDUP-03 needed both a `response_code` assertion and a message-id assertion at every fork
rather than either alone.

The two blind-to-red flips (**B** and **D**) are DEDUP-03's discharge evidence: both were
BLIND everywhere before plan 02, and both are still RED against the shipped, post-refactor
code, where two of the four mutation points have moved into shared helpers.

---

## 7. DEDUP-02's resolved single semantic -- the six-divergence table

| # | Sites affected | Resolution | Reasoning |
|---|---|---|---|
| 1 | severity keyed on `is_flag_set(FLAG_FORCE)` inline (sites A/B/C) vs. an `error_code` parameter (site D) | `bool warn_only` parameter -- A/B/C pass `is_flag_set(FLAG_FORCE)` directly, D passes `error_code == RESPONSE_CODE_WARNING` | **Must NOT be collapsed.** `eprom.cpp`'s two callers of site D disagree on policy by design: the standalone `CMD_CHECK_CHIP_ID` path (`eprom_check_chip_id_execute`) refuses unconditionally; `eprom_generic_init` honours `--force`. Folding `is_flag_set(FLAG_FORCE)` into the helper would silently make the standalone command start honouring `--force`, which it must not. |
| 2 | redundant `(uint16_t)` casts (site C only) | Dropped | Provable no-ops on already-`uint16_t` operands. Zero behaviour and zero size delta. |
| 3 | superfluous extra brace level (site C only) | Dropped | Lexical only, no behaviour change. |
| 4 | the mismatch guard living at the call site (all four) | Moved into the helper's early return | Byte-identical logic at all four sites; tracked in the golden as a **relocation** into `memory.cpp`, not a deletion. |
| 5 | linkage (site C `static`, A/B/D external) | UNCHANGED | Out of scope; unaffected by the collapse. |
| 6 | `#include "memory_utils.h"` absent from site A (`flash_utils.cpp`) | One include added | The declaration is required. This single line shifts all 97 of `flash_utils.cpp`'s `.planning/` citations -- staleness expected, close-blocked by Phase 159 / REMAP-04, not remapped here. |

**No divergence required a behaviour change to resolve:** 1 is preserved by parameterisation,
2 and 3 are provable no-ops, 4 is a pure relocation, 5 is untouched, 6 is additive.

**The named gap:** there is **no oracle anywhere** for the claim that the standalone chip-ID
check (`eprom_check_chip_id_execute`, the `CMD_CHECK_CHIP_ID` command) still refuses
regardless of `--force`. `test_case7_mismatching_chip_id_with_force_warns` exercises the
mismatch fork through `eprom_generic_init`'s write-path caller, never through the standalone
command. The evidence for this specific claim is **source-level only**, re-confirmed this
session: `eprom_check_chip_id_execute` is byte-unchanged (still passes `RESPONSE_CODE_ERROR`
unconditionally) and `mem_util_report_chip_id` contains zero `is_flag_set(FLAG_FORCE)`
references (`grep -c` -> `0`). Stated plainly, per plan 04's own recorded ceiling -- not
implied covered by a test that does not exist.

---

## 8. The seven coverage ceilings -- final form

1. **`src/eprom_operations.cpp` compiles in NO native environment.** All native envs share
   `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
   +<operation_utils.cpp>`. The nine forwarding wrapper returns have **no behavioural oracle**
   -- only the size-identity build (§3) and source inspection (§3's grep counts). The **six**
   flipped `op_execute_stateful_operation` returns, by contrast, **are** covered -- by Cases
   24 and 25 in `test_eeprom28c_sdp.cpp`, and nothing else.
2. **`test_vpp_eprom_v131` and `test_flash_intel_vpp` are in no CI leg -- final form.** Plan
   02's `flash_intel.cpp` reachability attempt **succeeded**:
   `test_vpp04_f_flash_intel_undervoltage_warning_pairing` reached the under-voltage arm and
   passed on first attempt. Ceiling 2 is therefore **NARROWED, not removed**: the
   `flash_intel.cpp` under-voltage arm now has one executing case, in `native_loop_v131`
   (still not invoked by any CI workflow), while the over-voltage arm and the rest of
   `flash_intel.cpp`'s VPP path remain uncovered, and `native_loop_v131` itself still carries
   no CI coverage at all.
3. **The AVR 16-bit promotion is unobservable natively.** Native `int` is 32-bit; identical
   before and after; not a regression; not covered.
4. **The 8-byte payload's byte VALUES have no oracle anywhere.** `test_vpp04_a` asserts the
   payload LENGTH is 8. "The emitted 8-byte payload is unchanged" rests on source-level
   identity of the arithmetic plus that length assertion -- no value oracle exists.
5. **`scripts/check_size_baseline.py` runs in no CI workflow at all** (confirmed again this
   session, §5). Every size gate in this phase is a local-run obligation.
6. **No bench claim** (D-02). Nothing in this phase is attested on silicon.
7. **DEDUP-04's size-identity result is a SIZE claim, not an IMAGE claim -- final form,
   plan 05's own `.hex` SHA pairs** (§3): `uno` `853dabb4...` -> `8f5e9169...`, `uno328pb`
   `bf226ea0...` -> `ec768c16...`, `leonardo` `e5d52522...` -> `099b8c75...`. Size-identical
   on all three AVR targets; an oracle asserting image identity would go RED.

---

## 9. The corrections ledger -- every row closed out

| # | ROADMAP / REQUIREMENTS says | Measured | Corrected figure now lives |
|---|---|---|---|
| C-1 | The two `flash_intel.cpp` VPP blocks sit "inside `flash_intel_write_init`" | They sit inside `static void flash_intel_check_vpp` (`:26`), fully inlined; `flash_intel_write_init` (`:106`) is the symbol-table billing, not the lexical location | `156-before-figures.md` §3; `156-03-SUMMARY.md`; this file §1/§9 |
| C-2 | `__udivmodhi4` call sites: 30 -> 13 | **31 -> 13**; the "24 of them" derived claim restated and unaffected (§4) | `156-before-figures.md` §4; this file §4 |
| C-3 | (implicit) a -268/-158 split for DEDUP-01/DEDUP-02 | **CONFIRMED**: plan 03 measured -268 B, plan 04 measured -158 B, summing to the measured -426 B total | this file §2 |
| C-4 | The DEDUP-04 flip is "byte-for-byte zero" (implying image identity) | Size-identical on all three targets (one more than the original survey claimed); `.hex` SHA differs on all three | `156-before-figures.md` §10; this file §3/§8 |
| C-5 | The shared clone is `op_execute_stateful_operation.constprop.44` | Exactly one clone, suffix `.constprop.42`, unchanged by the boolean-convention flip; no gate pins a clone suffix | `156-before-figures.md` §3; re-confirmed this session |
| C-6 | A "ten-line comment at `eprom_operations.cpp:57-63`" exists solely to explain the `!` | Only the final 2-3 lines (`:65-67`) concerned the `!`; the rest is LOCK-01/LOCK-02 rationale, which survives unedited | `156-before-figures.md` §10; `156-05-SUMMARY.md` |
| C-7 | DEAD-06: "the only requirement in Phases 155-158 that touches a test file" | **FALSE** -- DEDUP-04 (plan 05) touched `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`. **Consequence:** DEAD-06's uniqueness claim in `REQUIREMENTS.md` §2 no longer holds and is corrected there by this plan's Task 3, not merely noted here | `REQUIREMENTS.md` §2 (DEAD-06 entry, appended by this plan) |
| planner-found 8th | RESEARCH's six-location comment blast-radius list for DEDUP-04 | `src/operation_utils.cpp:58` carries the identical `@return` doxygen wording as `include/operation_utils.h:73` -- a seventh location, found by plan 01, corrected by plan 05 in the same commit as the other six (`grep -c 'still ongoing'` over both files is `0`, re-confirmed this session) | `156-before-figures.md` §10; `156-05-SUMMARY.md` |
| found beyond the seven | RESEARCH/VALIDATION's pytest baseline: 313 passed / 0 failed / 32 skipped | Canonical checkout: 348/0/0 (`156-before-figures.md` §5, `META_PRESENT` seam). This plan's own measurement: **355 passed, 0 failed** (348 + plan 06's 7 new legs) -- the 348 baseline held steady through DEDUP-01/02/04, growing by exactly 7 for the new gate, no other count moved | `156-before-figures.md` §5; this file §5 |

---

## 10. Handoffs

- **`scripts/baseline/size_baseline.json`'s cold re-anchor and the pre-existing BASE-01 native
  case-count mismatch** (`cases baseline=141 observed=172`) -> **Phase 158 / LAND-01 and
  LAND-03.** This session confirmed the baseline is byte-unchanged
  (`git diff --quiet -- scripts/baseline/size_baseline.json` exits 0) and reproduced the
  canonical invocation's pre-existing failure again (§5); neither is touched by this plan.
- **`json_parser.c`'s missing `algorithm` range check** -> **Phase 157 / DECODE-05.** Not
  touched.
- **The citation staleness this phase created** -> **Phase 159 / REMAP-01 through REMAP-05**,
  close-blocked by **REMAP-04**. Named: the one added `#include "memory_utils.h"` in
  `src/proms/flash_utils.cpp` (plan 04) shifts all 97 of that file's `.planning/` citations;
  plans 03 and 04's edits additionally shift citations in `src/proms/eprom.cpp`,
  `src/proms/flash_intel.cpp`, `src/proms/eeprom_28c.cpp` and `src/proms/memory.cpp` (which
  gained two new functions). `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md` was **not** touched by this
  plan -- byte-unchanged, confirmed by `git status --porcelain` showing no change to it.
- **The one in-source citation this phase's plans did repair, recorded separately as
  incidental:** `src/proms/eeprom_28c.cpp:265` (plan 04) -- the stale comment pointing at
  `flash_intel.cpp:112-121` was repaired to name the symbol `flash_intel_check_chip_id`
  instead of a line range, since Phases 157/158 will move that file again. This is an
  incidental fix inside a comment plan 04 touched anyway, not `.planning/` remap work, and is
  not counted toward Phase 159's REMAP scope.

---

## Self-verification of this record

`git -C firestarter status --porcelain` is empty and `git -C firestarter rev-parse HEAD`
equals `1151dc4` at the end of this task -- this plan's own measurement work (Task 1 and this
record) edited nothing under `firestarter/`; every probe planted in §6 was planted in a
throwaway worktree, reverted, and the worktree removed and pruned.
