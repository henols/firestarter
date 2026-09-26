---
title: Before-figures record — milestone v1.33, Phase 156 (Duplicated-Report Extraction + Boolean-Convention Repair)
phase: 156-duplicated-report-extraction-boolean-convention-repair-firmw
plan: "01"
measured: 2026-08-23
status: AUTHORITATIVE — this file is the ONLY source for Phase 156's before-half figures. Phases 157 and 158 each invalidate the measurements captured here (157 edits `json_parser.c`/`firestarter.h`, 158 re-anchors `size_baseline.json` and cold-rebuilds), so no later plan can re-derive them. Supersedes ROADMAP.md §Phase 156 criteria 1 and 4 and REQUIREMENTS.md DEDUP-01/DEDUP-04 prose wherever they state a figure this file corrects (C-1 through C-7, the planner-found eighth comment location, and two further measured discrepancies this plan found beyond the seven ROADMAP already lists).
supersedes: >
  ROADMAP.md Phase 156 criteria 1 ("`__udivmodhi4` call sites fall from 30 to 13"; "inside
  `flash_intel_write_init`") and 4 ("byte-for-byte zero"; "op_execute_stateful_operation.constprop.44");
  REQUIREMENTS.md DEDUP-01 ("`__udivmodhi4` call sites fall 30 -> 13"; "inside `flash_intel_write_init`")
  and DEDUP-04 ("byte-for-byte zero"; "constprop.44") prose, wherever they state a figure this file
  corrects. ROADMAP.md §Phase 156 already carries a corrections paragraph (line 347) naming C-1..C-7
  and pointing at this file as authoritative -- this file is that authority, independently re-measured,
  not merely copied from the paragraph that cites it.
requirements: [DEDUP-01, DEDUP-02, DEDUP-03, DEDUP-04]
---

# Before-figures record — v1.33 Phase 156

Every number in this file was measured on a **clean, unedited** `firestarter` working tree during
this plan's session, run from `/workspaces/firestarter` (the canonical checkout, not a throwaway
worktree, except where a step below explicitly says otherwise and names the worktree it used).
Each number carries the verbatim command that produced it. Every flash/RAM figure is labelled
**WARM**. This task edited no tracked file; the tree was proven clean before AND after every step.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_PRE_SHA` | `adf1a312804b6d1cfc7a6a8aa054d58bdf3188cd` (abbreviates `adf1a31`) |
| `firestarter` branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` |
| `git -C firestarter status --porcelain` | empty (asserted before AND after this plan's measurement work) |
| `git -C firestarter diff --name-only HEAD` | empty |
| meta HEAD sha (before this plan's commit) | `fad3437ba143191e41ed923d7ba305ae8205fe02` |
| `git -C firestarter worktree list` | only `/workspaces/firestarter` at `adf1a31` on this branch (plus an unrelated sibling checkout `firestarter_py32_ci`); this task's own throwaway worktrees (below) were removed and pruned before this record was written |

**`firestarter_app` gitlink note:** the meta repo shows `firestarter_app` as untracked/modified
(`git status --porcelain` in `/workspaces`). This is **pre-existing Phase 154 drift, operator-gated**
— not touched, staged or re-pinned by this plan or any plan in this phase.

Commands run:
```bash
git -C firestarter rev-parse HEAD
git -C firestarter branch --show-current
git -C firestarter status --porcelain
git -C firestarter diff --name-only HEAD
git rev-parse HEAD   # meta repo
```

---

## 2. AVR image figures, WARM

| Target | Flash used | Flash total | RAM used | RAM total | Label |
|---|---|---|---|---|---|
| `uno` | **24660** | 32768 | **1567** | 2048 | **WARM** |
| `uno328pb` | **24708** | 32768 | **1573** | 2048 | **WARM** |
| `leonardo` | **26804** | 32768 | **2008** | 2560 | **WARM** |

All six figures matched `155-after-figures.md` §2's post-Phase-155 position exactly, on the first
run this session, against an already-warm `.pio/build/`.

**Leonardo Caterina headroom against the 28672 B cliff: `28672 − 26804 = 1868 B`.**

Command per target: `pio run -e uno`, `pio run -e uno328pb`, `pio run -e leonardo`, each read via
its `RAM:` / `Flash:` summary line (run from `/workspaces/firestarter`).

**These figures are deliberately WARM, not cold.** LAND-01 / Phase 158 owns the cold re-record;
re-recording cold here would duplicate that plan's job and risk a second, inconsistent "before"
position.

---

## 3. Per-symbol ledger, `uno`

`avr-nm --print-size --size-sort -C .pio/build/uno/firestarter_uno.elf`, resolved at
`~/.platformio/packages/toolchain-atmelavr/bin/avr-nm` (confirmed executable; not on `PATH`).

| Symbol | Size | Hex |
|---|---|---|
| `eprom_check_vpp` | **524** | `0x20c` |
| `flash_intel_write_init` | **562** | `0x232` |
| `flash_util_check_chip_id_execute` | **192** | `0xc0` |
| `flash_intel_check_chip_id` | **220** | `0xdc` |
| `eeprom28c_write_init` | **430** | `0x1ae` |
| `eprom_internal_check_chip_id` | **260** | `0x104` |
| `eprom_check_chip_id_execute` | **6** | `0x6` |
| `op_execute_stateful_operation.constprop.42` | **214** (measured) | `0xd6` (measured) |

**C-1, re-verified independently this session:** `flash_intel_check_vpp` (`grep -c` over
`avr-nm -C`'s full output) is **ABSENT** from the symbol table — `grep` exits 1. Read at
`src/proms/flash_intel.cpp:26`, it is `static void flash_intel_check_vpp(firestarter_handle_t*)`,
fully inlined into its caller. `flash_intel_write_init` begins at `src/proms/flash_intel.cpp:72`.
The two `flash_intel.cpp` VPP blocks are **lexically inside** `flash_intel_check_vpp` (line 26),
**not** inside `flash_intel_write_init` (line 106) as ROADMAP criterion 1 and DEDUP-01 both say —
the `flash_intel_write_init` attribution is a *symbol-table billing* fact (the static function's
bytes are billed to its caller because it has no symbol of its own), not a lexical one. Both
statements are true of different things; the requirement's wording conflates them. A plan that
greps `flash_intel_write_init` for the blocks will not find them.

**C-5, re-verified independently this session:** exactly **one** `op_execute_stateful_operation`
clone is linked (`avr-nm -C | grep -c` confirms count `1`), and its suffix is **`.constprop.42`**,
not `.constprop.44` as DEDUP-04 and ROADMAP criterion 4 both say. No gate in this phase pins a
clone suffix.

**Measured discrepancy beyond C-5 (found this session, not in `156-RESEARCH.md`):** the clone's
byte size measures **214 B (`0xd6`)** here, not the **216 B (`0xd8`)** `156-RESEARCH.md`'s own C-5
section states. Cross-checked two ways on the same warm `uno` ELF — `avr-nm --print-size
--size-sort -C` and `avr-objdump -t`, both report `0xd6` — so this is not a tool-disagreement
artefact. No cause is claimed (toolchain patch level, a since-landed unrelated commit inside
Phase 155, or a stale figure in the research session are all consistent with a 2 B drift and none
is measured here). Record the measured **214 B / `0xd6`** as this plan's figure for the clone's
size; the suffix identity `.constprop.42` (not `.44`) is the load-bearing part of C-5 and is
unaffected.

**The LTO ledger will NOT close after DEDUP-01/02 land** (research measured −624 B of symbol
deltas against a −426 B image delta, because `eprom_internal_check_chip_id` stops existing as a
symbol and is inlined into `main`). The image figure in §2 is the phase total; this ledger is
corroboration only, not a component sum.

---

## 4. `__udivmodhi4` call sites, `uno`

```bash
OBJDUMP=~/.platformio/packages/toolchain-atmelavr/bin/avr-objdump
$OBJDUMP -d .pio/build/uno/firestarter_uno.elf | grep -cE '(r?call|jmp).*__udivmodhi4'
```

| Position | Sites |
|---|---|
| Before, at `adf1a31` (this plan's position) | **31** |
| Target after DEDUP-01 + DEDUP-02 (cited from `156-RESEARCH.md`; NOT independently measured by this before-only plan, which edits no source) | 13 |

**C-2:** ROADMAP criterion 1 and REQUIREMENTS DEDUP-01 both say **30**. Measured at `adf1a31`:
**31**. This record supersedes both. The **derived** claim ("those four blocks held 24 of them")
is unaffected: `31 − 13 = 18` net, the helper adds 6 sites, so `18 + 6 = 24` removed by the four
blocks — restate the total as 31, keep the 24.

**A1 cause-attribution — measured, not assumed, and the measurement is a negative result:**
research's own assumption A1 attributes the 31st site to Phase 155's 32-bit voltage reformulation
(`46dd574`). This plan measured it directly rather than repeating the inference: built `uno` in a
throwaway `git worktree` named `firestarter` (per the project's own worktree-naming pitfall) at
`e26e9ab` (the commit immediately BEFORE `46dd574`) and again at `46dd574` itself, then ran the
identical `avr-objdump | grep -c` command against each ELF.

| Commit | `__udivmodhi4` sites |
|---|---|
| `e26e9ab` (parent of `46dd574`) | **31** |
| `46dd574` (Phase 155's 32-bit voltage reformulation) | **31** |

**The count did not change across `46dd574`.** A1's inference is measured **false** for this
specific commit: whatever introduced the 31st site (relative to the ROADMAP's stale "30"), it was
not `46dd574`. No alternative cause is asserted here — finding it would require bisecting the rest
of Phase 155's commits, which is out of this plan's scope (measurement only, no source edit, and
the plan's own prohibitions forbid claiming an unmeasured cause). Both throwaway worktrees were
removed and pruned (`git worktree remove --force` + `git worktree prune`) before this file was
written; `git -C firestarter worktree list` (§1) confirms only the tracked checkout remains.

---

## 5. Test and gate baselines, on the clean committed tree

| Leg | Result | Wall time |
|---|---|---|
| `pio test -e native` | **172 test cases: 172 succeeded**, 17 suites | 21.6 s |
| `pio test -e native_nodevtools` | **172 test cases: 172 succeeded**, 17 suites | 31.7 s |
| `pio test -e native_loop_v131` (**NOT in CI** — its own `platformio.ini` comment says so) | **80 test cases: 80 succeeded**, 2 suites — `test_loop_eprom_v131` **47** + `test_vpp_eprom_v131` **33** (`47 + 33 = 80`, exact split confirmed by per-suite grep) | 7.6 s |
| `python3 -m pytest tests/ -q` (system `python3`, canonical checkout `/workspaces/firestarter`, meta repo sibling PRESENT) | **348 passed, 0 failed, 0 skipped** | 12.08 s |

**Measured discrepancy beyond the seven ROADMAP corrections (found this session):**
`156-RESEARCH.md` and `156-VALIDATION.md` both record the pytest baseline as **313 passed / 0
failed / 32 skipped**. Measured here, in the canonical `/workspaces/firestarter` checkout, on the
identical `adf1a31` tree: **348 passed / 0 failed / 0 skipped**. This is not a code-state
difference — it is an **environment** difference, and it is fully explained and reproduced:

- `tests/meta_presence.py` defines `META_PRESENT` (used by the `requires_meta` skip-marker applied
  to 12 test functions, several parametrized, inside `test_flash_path_record_sync.py`), which is
  `True` when a `.git` marker is discoverable at the resolved meta-repo root. Confirmed this
  session: `python3 -c "import meta_presence; print(meta_presence.META_PRESENT)"` (run with
  `tests/` on `sys.path`) prints `True` in `/workspaces/firestarter`, because `/workspaces/.git`
  genuinely exists there (the canonical layout this whole phase runs inside).
- `156-RESEARCH.md` states its own pytest baseline was "Measured in `git worktree` `/tmp/fw156`" —
  an isolated worktree that has no `/workspaces` meta-repo sibling above it, so `META_PRESENT`
  resolves `False` there and all `requires_meta`-marked tests skip instead of running.
- Reproduced directly this session: `FIRESTARTER_META_ROOT=/tmp/nonexistent-meta-root python3 -m
  pytest tests/ -ra` (forcing meta-absence via the documented override seam, without needing a
  second worktree) yields **316 passed, 32 skipped** — the same **348**-item collection total
  (`316 + 32 = 348`), with the 32 skips landing on exactly the `requires_meta`-marked cases, all
  citing `"meta repo checkout absent"`. `348` is thus the correct total collection count for this
  code position however it is run; only the pass/skip split moves with meta-repo presence.
- **The 316 vs. research's quoted 313 does not fully reconcile** (a 3-item drift). Not chased
  further — reconciling it would mean re-deriving research's exact worktree state, which is out of
  this plan's scope (measurement of the CURRENT position only, no source edit). Recorded honestly
  rather than silently substituted.

**Consequence for later plans:** the phase gate's pytest leg (item 3 of the eight-item gate in
`156-VALIDATION.md`) is `≥313 passed, 0 failed` — a floor, so 348 (meta present) or 316 (meta
absent) both clear it; the two counts are not in tension with the gate, only with each other's
apparent precision, and this record is the reconciliation.

**The four CI legs, exhaustively** (re-verified this session, not merely quoted): `pio test -e
native` (`.github/workflows/build.yml:142`, `.github/workflows/beta-build.yml:122`), `pio test -e
native_nodevtools` (`build.yml:155`, `beta-build.yml:128`), `pytest tests/ -v`
(`build.yml:161`, `beta-build.yml:134`), `pio run` (`build.yml:193`, `beta-build.yml:145`).
`native_loop_v131` appears in **neither** workflow file — confirmed by the same `grep -n` pass —
and its own `platformio.ini` comment (`; NO CI COVERAGE (F-140-11, D-11)`) says so explicitly.

**Native-suite flakiness (D-04):** these are single-run (N=1) figures. Phase 155 observed 172/172
inconsistently across seven runs; never treat a single run's exact wall time or a future single-run
count mismatch as evidence of a regression from this plan's edits (there are none — this plan edits
no source).

---

## 6. The golden's arrival state

```bash
git hash-object src/proms/eprom.cpp
```
Live: `838aca47986103969be4caca3cef71a033bac069`
Recorded (`tests/golden/protocol_branch_inventory.json`, key `meta.blob_shas['src/proms/eprom.cpp']`):
`838aca47986103969be4caca3cef71a033bac069`

**They match exactly — the golden is GREEN on arrival.** This is what proves that Phase 156's own
edits (plans 03/04), not some earlier drift, are the cause of the golden's two expected RED legs.

Recorded `counts`: `total_sites` **23**, `protocol_keyed_sites` **1**, `other_sites` **22**.

Live extraction, using the golden module's own `_extract_predicates` (imported by file location,
never hand-counted), against the current `src/proms/eprom.cpp`: **23 sites**, matching the
recorded count exactly. Every site's line and predicate:

| Line | Predicate | Keyed on | Tier |
|---|---|---|---|
| 45 | `switch (handle->cmd)` | `cmd` | other |
| 52 | `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))` | `ctrl_flags` | other |
| 69 | `if (handle->pulse_delay == 0)` | `pulse_delay` | other |
| 70 | `switch (handle->protocol)` | `protocol` | **protocol** |
| 106 | `if (energy_cap_us > 0 && handle->pulse_delay > energy_cap_us)` | `pulse_delay` | other |
| 144 | `if (!is_operation_in_progress(handle))` | `operation_state` | other |
| 146 | `if (handle->response_code == RESPONSE_CODE_ERROR)` | `response_code` | other |
| 150 | `if (is_flag_set(FLAG_CAN_ERASE))` | `ctrl_flags` | other |
| 151 | `if (!is_flag_set(FLAG_SKIP_ERASE))` | `ctrl_flags` | other |
| 158 | `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK))` | `ctrl_flags` | other |
| 177 | `if (handle->response_code == RESPONSE_CODE_ERROR)` | `response_code` | other |
| 294 | `if (is_flag_set(FLAG_VPE_AS_VPP))` | `ctrl_flags` | other |
| 323 | `if (handle->firestarter_get_control_register(handle, CTRL_VPP_REGULATOR_ENABLE) == 0)` | `firestarter_get_control_register` | other |
| 547 | `if (handle->firestarter_get_data(handle, addr) == expected)` | `firestarter_get_data` | other |
| 676 | `if (handle->response_code == RESPONSE_CODE_ERROR)` | `response_code` | other |
| 713 | `if (vpp_mv > (uint32_t)handle->vpp_mv + 500)` | `vpp_mv` | other |
| 728 | `if (is_flag_set(FLAG_FORCE))` | `ctrl_flags` | other |
| 736 | `if (vpp_mv < (uint32_t)handle->vpp_mv * 95 / 100)` | `vpp_mv` | other |
| 787 | `if (handle->response_code == RESPONSE_CODE_ERROR)` | `response_code` | other |
| 790 | `if (handle->chip_id > 0)` | `chip_id` | other |
| 791 | `is_flag_set(FLAG_FORCE)` | `ctrl_flags` | other |
| 798 | `if (chip_id != handle->chip_id)` | `chip_id` | other |
| 815 | `if (bit & CTRL_VPE_ENABLE && using_p1_as_vpp(handle))` | `pins+bus_config.vpp_line` | other |

This is the pre-change inventory plans 03 and 04 will each re-derive one site out of.

**The one-commit property, and the plan-level resolution:** the golden's own `meta.recorded_by`
history (four prior entries, each naming a phase/plan and stating the source-change-plus-golden
one-commit rule) documents that this golden must land in the SAME commit as the `eprom.cpp` change
it describes. Because DEDUP-01 (plan 03) removes exactly one site and DEDUP-02 (plan 04) removes
exactly one other, each plan re-derives the golden inside its own commit — so the gate reads GREEN
at every commit boundary, AND each requirement's own measured site-count movement is independently
attributable rather than blurred into a single two-requirement diff.

---

## 7. Reference carriers

```bash
git rev-parse wip/v1.33-size-reduction-survey-preserved
```
`a6b46f8b12e81c62d9958945eb0bdbb8c16ae699` (abbreviates `a6b46f8`).

```bash
git diff HEAD size-reduction-survey -- src/proms/eprom.cpp src/proms/flash_intel.cpp include/memory_utils.h
```
Output: **empty**. The branch named in ROADMAP §v1.33 and in the original survey's own
front-matter (`size-reduction-survey`) does **NOT** carry this work — the survey left its changes
uncommitted. `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` is the ref that preserved them.

**Independently re-verified this session (not in `156-RESEARCH.md`):**
```bash
git merge-base HEAD wip/v1.33-size-reduction-survey-preserved   # 8695ee52c27a4bee4387c5c489afd5f3d7275e8a
git merge-base HEAD size-reduction-survey                        # 8695ee52c27a4bee4387c5c489afd5f3d7275e8a
```
Both carriers fork `8695ee5`, before Phase 154's comment sweep — confirming neither can be
cherry-picked onto today's tree, so both are semantic references only. Neither carrier holds
DEDUP-04 — it exists nowhere yet; plan 05 authors it fresh.

**Applying the rebuilt six-file Phase-156 subset patch** (extracted from
`.planning/notes/firmware-size-reduction-measured.patch` per `156-RESEARCH.md`'s extraction
script, keeping `include/memory_utils.h`, `src/proms/eeprom_28c.cpp`, `src/proms/eprom.cpp`,
`src/proms/flash_intel.cpp`, `src/proms/flash_utils.cpp`, and only the `@@ -230,6 +230,52 @@` hunk
of `src/proms/memory.cpp`):

| Check | Result |
|---|---|
| `git apply --check` (full subset) | **FAILS**, naming `src/proms/eeprom_28c.cpp` only, at line `:300` (a swept trailing-context comment line — Phase 154's sweep rewrote `"FIX-01: a 0x0D-local…"` to `"A 0x0D-local…"`) |
| `git apply --check -C1` (full subset) | **exit 0** (clean; context reduced to apply the `eeprom_28c.cpp` fragment at line 289) |

Neither `--check` invocation applied anything; `git status --porcelain` was re-asserted empty
immediately afterward (confirmed, §1). The patch was NOT applied in this plan.

---

## 8. The one-sided size gate, and the pre-existing red

Re-verified this session directly against `scripts/check_size_baseline.py`:

- `:697` — `if flash_delta > allowance:` (confirmed by `grep -n`)
- `:709` — `if ram_delta > ram_tolerance:` (confirmed by `grep -n`)

Both are strict-inequality, one-directional checks (D-03): a **reduction** in flash or RAM needs
**no named exemption** to pass either leg.

The canonical invocation `python3 scripts/check_size_baseline.py --policy merge05 --baseline
scripts/baseline/size_baseline_base01.json` is **already exiting non-zero on `beta`** for an
unrelated, pre-existing reason: `scripts/baseline/size_baseline_base01.json` records
`"cases": 141` (confirmed by `grep -n '"cases"' scripts/baseline/size_baseline_base01.json`)
against the measured `native`/`native_nodevtools` case count of **172** (§5) — the frozen BASE-01
mismatch from Phase 124. This is **Phase 158 / LAND-03's problem**, not this phase's, and it is not
"fixed" here; this plan did not run the canonical invocation as a phase gate, only confirmed the
two source lines and the baseline figure that together explain the pre-existing red.

---

## 9. The seven honest coverage ceilings — stated, not implied

These appear in every plan of this phase and in the phase record, in these terms:

1. **`src/eprom_operations.cpp` compiles in NO native environment.** All native envs share
   `build_src_filter = +<proms/> +<boards/rurp_serial_utils.cpp> +<json_parser.c>
   +<operation_utils.cpp>`. The nine dropped `!` wrappers have **no behavioural oracle** — only the
   size-identity build and source inspection. `src/operation_utils.cpp` **is** in the filter, so
   the six flipped engine returns are covered — by Cases 24 and 25 and nothing else.
2. **`test_vpp_eprom_v131` and `test_flash_intel_vpp` are in no CI leg.** The former runs only
   under `native_loop_v131` (NO CI COVERAGE, §5). The latter is in no env's `test_filter` at all.
   So `flash_intel.cpp`'s VPP path — two of DEDUP-01's four blocks — has zero executing coverage
   today; its regression evidence is the `eprom.cpp` twin's plus source-level identity.
3. **The AVR 16-bit promotion is unobservable natively.** Native `int` is 32-bit, so no native test
   can attest the AVR arithmetic or its wrap above 65485 mV. Identical before and after; not a
   regression; not covered.
4. **The 8-byte payload's byte VALUES have no oracle anywhere.** `test_vpp04_a` asserts the payload
   LENGTH is 8. "The emitted 8-byte payload is unchanged" is established by source-level identity
   of the arithmetic plus that length assertion — never by a value comparison.
5. **`scripts/check_size_baseline.py` runs in no CI workflow at all** (LAND-04, confirmed by the
   same `grep -n` pass over both workflow files, §5). Every size gate in this phase is a
   local-run obligation.
6. **No bench claim** (D-02). Nothing in this phase is attested on silicon.
7. **DEDUP-04's zero-byte result is a SIZE claim, not an IMAGE claim.** The `.hex` SHA changes on
   all three targets (per `156-RESEARCH.md`'s measurement, not independently re-measured by this
   before-only plan, which makes no post-flip build) and `avr-objdump` differs on 5450 lines. An
   oracle asserting image identity would go RED. The claim that may be made is size-identity on all
   three targets.

---

## 10. The corrections index

| # | ROADMAP / REQUIREMENTS says | Measured this session | Carried forward by |
|---|---|---|---|
| C-1 | The two `flash_intel.cpp` VPP blocks sit "inside `flash_intel_write_init`" | They sit inside `static void flash_intel_check_vpp` (`flash_intel.cpp:26`), fully inlined; `flash_intel_write_init` (`:106`) is the symbol-table billing, not the lexical location. `flash_intel_check_vpp` confirmed absent from the symbol table this session (§3) | 03 |
| C-2 | `__udivmodhi4` call sites: **30 → 13** | **31 → 13** measured at `adf1a31`; the "24 of them" derived claim is unaffected (§4). A1's inferred cause (Phase 155's `46dd574`) is measured FALSE this session — the count is 31 both immediately before and immediately after that commit (§4) | 01 (this file), 03, 07 |
| C-3 | (implicit) a `−268 / −158` split for DEDUP-01/DEDUP-02 | UNVERIFIED at this position — only `−426` total is measured (per `156-RESEARCH.md`); plans 03/04 each measure their own half in their own commit | 03, 04, 07 |
| C-4 | The DEDUP-04 flip is "byte-for-byte zero" | Size-identical on all three targets, `.hex` SHA differs on all three, `avr-objdump` differs on 5450 lines (per `156-RESEARCH.md`; build proven reproducible first) | 05, 07 |
| C-5 | The shared clone is `op_execute_stateful_operation.constprop.44` | Exactly one clone exists, suffix `.constprop.42` (confirmed this session, §3). Its byte size also measures 214 B / `0xd6` here, not the 216 B / `0xd8` `156-RESEARCH.md`'s own C-5 states — an additional, unclaimed-cause discrepancy found this session (§3) | 05, 06 |
| C-6 | A "ten-line comment at `eprom_operations.cpp:57-63`" exists solely to explain the `!` | `:57-67` is the LOCK-01/LOCK-02 rationale block; only `:65-67` (the final 2–3 lines) concerns the `!` (re-read this session, §3-adjacent) | 05 |
| C-7 | DEAD-06: "the only requirement in Phases 155–158 that touches a test file" | False — DEDUP-04 turns `test_eeprom28c_sdp.cpp:1487` RED and `:1524-1534` vacuous; both require edits (per `156-RESEARCH.md`) | 05, 07 |
| planner-found 8th | DEDUP-04's comment blast radius is six locations | `src/operation_utils.cpp:58` carries the identical `@return true if the operation is still ongoing (e.g., waiting for ACKs), false when fully completed.` doxygen text as `include/operation_utils.h:73` (confirmed this session by `grep -n '@return'` over both files) — the blast radius is **seven** locations | 05 |
| found this session (beyond the seven) | `156-RESEARCH.md`/`156-VALIDATION.md`: pytest baseline is 313 passed / 0 failed / 32 skipped | In the canonical `/workspaces/firestarter` checkout (meta repo sibling present), it is **348 passed / 0 failed / 0 skipped** — explained by `tests/meta_presence.py`'s `META_PRESENT` seam; forcing meta-absence reproduces 316 passed / 32 skipped (348 total either way), a 3-item drift from the quoted 313 not chased further (§5) | 01 (this file); relevant to any later plan quoting this baseline |

---

## Summary of what this record proves

- The tree was proven clean before and after every measurement (§1); nothing was edited.
- All three AVR targets reproduce the exact post-Phase-155 position (§2): `uno` 24660/1567,
  `uno328pb` 24708/1573, `leonardo` 26804/2008, Leonardo headroom 1868 B.
- `flash_intel_check_vpp` is confirmed absent from the symbol table, proving C-1's lexical/billing
  distinction directly rather than by inference (§3).
- `__udivmodhi4` measures **31**, not 30, superseding ROADMAP/REQUIREMENTS (C-2); and A1's inferred
  cause is measured FALSE at the specific commit it names — a stronger, more honest posture than
  "unclaimed" (§4).
- The golden (`protocol_branch_inventory.json`) is proven GREEN on arrival, both by blob-SHA match
  and by an independent live re-extraction yielding the identical 23 sites (§6) — so any RED this
  golden shows after plans 03/04 land is attributable to those plans' own edits, not prior drift.
- The reference carrier is independently re-proven: `size-reduction-survey` does not carry this
  work (empty diff), `wip/v1.33-size-reduction-survey-preserved` @ `a6b46f8` does, and both fork
  `8695ee5` (independently re-derived via `git merge-base`, not merely quoted) — so neither is
  cherry-pickable (§7).
- The rebuilt six-file subset patch applies with `-C1` and fails `--check` on exactly one file, one
  line — confirmed, not applied (§7).
- Two additional measured discrepancies beyond the seven ROADMAP corrections were found this
  session and are recorded rather than silently absorbed: the `constprop.42` clone's byte size
  (214 B measured vs. 216 B quoted) and the pytest skip-count's dependency on meta-repo presence
  (348/0/0 here vs. 313/0/32 quoted, explained and reproduced) (§3, §5, §10).
- This record — not `156-RESEARCH.md` or `156-VALIDATION.md` in isolation — is the authoritative
  before-position for every Phase 156 delta plans 03-07 compute.
