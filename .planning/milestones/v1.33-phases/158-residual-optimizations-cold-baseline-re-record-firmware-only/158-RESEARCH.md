# Phase 158: Residual Optimizations + Cold Baseline Re-Record (firmware-only) — Research

**Researched:** 2026-08-24
**Domain:** AVR firmware size/RAM measurement, local-run gate mechanics, `jsmn` token layout, AVR integer-division codegen, honest record authoring
**Confidence:** HIGH (every figure below was built and run this session on all three AVR targets plus both native envs, in a throwaway worktree at `firestarter` `785e644`, which was then removed and pruned)

## Summary

This phase has almost no unknowns left after this session. **Both "genuinely unknown" candidates were measured**, and both answers differ from the ROADMAP/REQUIREMENTS prediction — one dramatically in the project's favour:

- **LAND-05 (`jsmntok_t` 8 → 6 B) is a flash WIN, not a flash cost.** Measured `−138 / −138 / −136 B` flash and `−128 B` RAM on `uno` / `uno328pb` / `leonardo`, cold, with **184/184 native on both envs** and zero new failures in `pytest tests/`. REQUIREMENTS' `+30 B flash` is not reproducible; the "breaks the suite" reading is refuted at this tree position. `start`/`end` stay signed; `type` and `size` become `uint8_t`.
- **LAND-06 (mask instead of modulo) is a size cost of `+22 / +24 / +22 B`** — the REQUIREMENTS' `+22 B` is right on two targets and 2 B low on `uno328pb`. The two `call __udivmodsi4` instructions inside `flash_5v_page_write_execute` are confirmed by disassembly and confirmed gone after the mask; the helper itself stays linked (9 other call sites). The runtime half is still unquantified and the page-boundary path has **no behavioural native coverage today**.

The mechanical half carries one hazard the criteria do not state, and it is the single most important planning constraint in this document: **re-recording `size_baseline.json` reddens exactly four legs of `tests/test_check_size_baseline.py`, and that suite runs in CI.** `check_size_baseline.py` is invoked as a *size gate* by no workflow — LAND-04 is true as written — but the checker is *executed* in CI as a subprocess by its own paired pytest under `pytest tests/ -v` (`build.yml:161`), and `build.yml` triggers on `push: branches: ['**', '!beta']`, i.e. on this milestone branch. So LAND-01 without LAND-02's fixture severance in the same commit is a red CI run, not a local-only inconvenience.

**Primary recommendation:** land LAND-05 (it is a measured win on every axis), decline or defer LAND-06 unless a page-boundary native test is written in the same phase (its only justification is an unmeasured runtime win on a path with zero behavioural coverage), then re-record `size_baseline.json` **last**, in one commit that also severs the fixtures onto a new `*_v158*` family — which needs only **4 new fixture files plus 2 updated in place**, not the 13 every prior generation used, because no new MERGE-05 exemption is authored for a reduction.

---

<user_constraints>
## User Constraints

**There is no CONTEXT.md for this phase** (`has_context: false` from `init.phase-op`), the same as Phases 155, 156 and 157. Per the orchestrator's instruction, the hand-authored ROADMAP §Phase 158 entry and REQUIREMENTS LAND-01…LAND-08 **are** the locked decisions. Nothing below invents a decision they do not state.

### Locked Decisions (from ROADMAP §v1.33 and REQUIREMENTS §5)

- **D-01 (milestone):** Phase 154 sweeps source and **builds** the remap tool; **Phase 159 applies it once** over the composite pre-154 → post-158 diff. **Phase 158 must not run the remap tool and must not repair citations** — but it *will* create newly-stale citations, and that is Phase 159's job. `.planning/v1.33/CITATIONS-STALE.md` must stay in place (REMAP-04 makes it close-blocking).
- **D-02 (milestone):** **No success criterion in this milestone requires a physical board.** REQUIREMENTS "Out of Scope" reaffirms this for LAND-06 by name: *"neither needs silicon to be correct"*. **No plan may author a bench criterion.** LAND-06's runtime half therefore stays unquantified by construction, not by omission.
- **D-03 (milestone):** MERGE-05 is one-sided (`check_size_baseline.py:697` is `if flash_delta > allowance`, `:709` is `if ram_delta > ram_tolerance`), so a shrink passes with **no exemption authored**. The pass must be **recorded as one-sided** so no future reader mistakes green for "nothing moved".
- **D-04 (milestone):** **The native suite is load-flaky.** No plan may attribute a suite failure to its own change on N=1.
- **D-05 (milestone):** the citation staleness window is temporary, marked, and close-blocking.
- **LAND-01:** BASE-01 (`scripts/baseline/size_baseline_base01.json`) is **NOT re-anchored** on its growth axis. Re-anchoring would erase the reduction the same way it would erase a growth.
- **LAND-02:** if re-anchoring reddens the known legs, **fixtures are severed onto a NEW fixture family** rather than the criterion being softened.
- **LAND-06:** if the mask is taken, it is labelled as affecting the **algorithm-5 flash-page path only** and explicitly **not** connected to the w27c512-write-slow-3x work.
- **Firmware-only (REQUIREMENTS "Out of Scope"):** *"Host-side changes in Phases 155–158. Those four phases are firmware-only: no host file moves, no wire change, no `chip_database.json` change, no protocol-parity constant moves."* Verified compatible — see F-9. Reading `firestarter_app/firestarter/data/pinouts.json` for LAND-07's arithmetic is a read, not a change.
- **Binary command protocol is OUT of scope** (operator decision 2026-08-22). LAND-07 must point at v1.28 / Backlog 999.35 rather than propose a step toward it.

### Claude's Discretion

- Whether LAND-05 lands or is rejected — the criterion licenses either, **with the outcome named**. (Research recommendation: land. See F-5.)
- Whether LAND-06 is taken or declined — the criterion licenses either, **with the measurement cited**. (Research recommendation: decline, or take only with a new page-boundary native test. See F-6.)
- Whether LAND-03 is fixed or carried — the criterion licenses either, **with the cause named**. (Research recommendation: fix; measured to cost zero gate legs. See F-3.)
- The shape and location of the LAND-02/04/07/08 records. (Recommendation: `.planning/v1.33/158-before-figures.md` + `158-after-figures.md`, the convention Phases 155–157 all used. See F-10.)
- The new fixture family's name and membership.
- Plan/wave decomposition.
- Whether to close the named `test_checker_convention.py` FLOOR carry-forward (F-11) — it names Phase 158 explicitly but appears in no LAND requirement.

### Deferred Ideas (OUT OF SCOPE)

- Replacing JSON with a binary command protocol (v1.28 / Backlog 999.35).
- Citation repair / running the remap tool (Phase 159, REMAP-01…05).
- Any bench criterion (D-02).
- Restructuring `eprom_write_execute`; a shared skeleton across the five write paths (both leads closed during scoping, REQUIREMENTS "Out of Scope").
- Re-anchoring BASE-01's growth axis (`flash_used` / `ram_used`).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (abridged) | Research support |
|----|------------------------|------------------|
| **LAND-01** | `size_baseline.json` re-recorded from cold builds, three AVR targets + native blocks, per the file's own convention; BASE-01 not re-anchored | **Recipe located and reproduced**: convention is `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, figures **transcribed not computed** (`size_baseline.json` `meta.generated_by`). All three cold figures re-measured this session, byte-identical to `157-after-figures.md` §2. `native_envs.cases` must move **172 → 184**, not 172 → 172 (F-1) |
| **LAND-02** | MERGE-05 policy run green **and** its one-sidedness recorded; fixtures severed onto a new family if legs redden | **Green run reproduced this session, exit 0**, with the negative deltas printed in the PASS line. **Exactly four legs redden** on re-record — named and observed (F-2). Minimal severance is 4 new fixtures + 2 updated in place, not 13 (F-2) |
| **LAND-03** | BASE-01 native case-count mismatch fixed or carried, with its cause named | `baseline=141` confirmed at `size_baseline_base01.json`; **observed is 184, not 172** — the criterion's figure is stale (F-3). Exit-1-suppresses-the-flash-report mechanism located in `main()`. Fix measured to redden **zero** legs |
| **LAND-04** | Recorded that `check_size_baseline.py` runs in no CI workflow at all | **Proven** — `grep -rn check_size_baseline .github/` returns nothing in all three repos, exit 1. But the claim needs a second clause: the checker **is executed in CI** by its own pytest (F-4). Of 8 `scripts/check_*.py`, exactly **one** is invoked by any workflow |
| **LAND-05** | `jsmntok_t` 8 → 6 B re-tested on an idle machine; landed or rejected with the failure named | **MEASURED AND GREEN**: `−138/−138/−136 B` flash, `−128 B` RAM, 184/184 on both native envs, no new pytest failure. `sizeof` 8 → 6 confirmed with real `avr-gcc`. Twelve `-1` sentinel field references located; `start`/`end` stay `int` (F-5) |
| **LAND-06** | `flash_5v_page` per-byte modulo replaced with a mask or declined, with the measurement cited | **MEASURED**: `+22/+24/+22 B` flash, 0 B RAM. Both `call __udivmodsi4` sites confirmed by disassembly and confirmed removed. Page-boundary path has **zero behavioural native coverage** (F-6) |
| **LAND-07** | `NUMBER_JSNM_TOKENS` recorded as not reducible, with the arithmetic | **Arithmetic re-derived from `pinouts.json` and the real chip DB**: real maximum is **51 tokens** (13 headroom), field-wise-maximum synthetic bound is **55** (9 headroom). The `57` / `7` figures are **not reproducible** (F-7) |
| **LAND-08** | Native suite load-flakiness recorded with its evidence | Primary source located (`155-RESEARCH.md:846`). **Three new same-tree data points added this session**: 22.2 s, 54.0 s, 61.3 s — all 184/184 (F-8) |
</phase_requirements>

---

## Criterion classification — which criteria branch, which only record

The orchestrator asked for this explicitly. It drives wave decomposition.

| # | Criterion | Class | Why |
|---|-----------|-------|-----|
| 1 | Cold re-record of `size_baseline.json` | **Mechanical** | Recipe is documented in the file itself; figures already measured twice (this session and `157-after-figures.md` §2). Only the *final* figures depend on criteria 5/6 |
| 2 | MERGE-05 green + one-sidedness recorded + severance | **Mechanical**, with one measured hazard | Green run reproduced; the four red legs are enumerated and observed, not predicted |
| 3 | BASE-01 native case-count mismatch | **Record-only OR one-line fix** — plan chooses | Both branches measured. Fixing costs 4 JSON integers and reddens zero legs |
| 4 | `check_size_baseline.py` in no CI workflow | **Record-only** | Proven by grep; needs the second clause about the paired pytest to be honest |
| 5 | `jsmntok_t` 8 → 6 B | **Measurement/decision — RESOLVED by this research** | Was genuinely unknown; now measured green on every axis. The plan can land it with a known target, not a hope |
| 6 | `flash_5v_page` modulo → mask | **Measurement/decision — measured, but the DECISION is still open** | Size cost is known (`+22/+24/+22`); the runtime benefit is unmeasurable without silicon (D-02) and the path is uncovered natively. This is the one criterion whose plan must genuinely branch |
| 7 | `NUMBER_JSNM_TOKENS` not reducible | **Record-only**, but the arithmetic in the criterion is wrong | The record must carry the *derived* numbers, not the criterion's |
| 8 | Native load-flakiness recorded | **Record-only** | Evidence exists in `155-RESEARCH.md`; this session adds three more points |

**Sequencing consequence:** criteria 5 and 6 must be decided and landed **before** criterion 1 runs, because they move the very figures criterion 1 records. Criterion 2's severance must be in the **same commit** as criterion 1's re-record, or CI is red at that commit (F-4).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| JSON token storage layout | AVR firmware — `lib/jsmn/src/jsmn.h` | ARM port (`platform/py32f071/CMakeLists.txt:70` compiles `jsmn.c`) | The struct is the RAM object; only the vendored header owns it. It is a **cross-architecture** edit: the ARM build compiles the same file, so the py32 workflow is a live consumer |
| Page-boundary arithmetic (algorithm 5) | AVR firmware — `src/proms/flash_5v_page.cpp:106-125` | — | Derived from `handle->mem_size` inside the handler; no host or wire involvement. Deliberately **not** the same owner as algorithm 13's mask, which comes from a host-delivered `page_size` and needs validation (`src/proms/eeprom_28c.cpp:628`) |
| Recorded size/RAM truth | Build/tooling tier — `scripts/baseline/size_baseline.json` | — | A committed measurement record, read by three consumers via the `FIRESTARTER_SIZE_BASELINE` seam. Only a linked ELF can witness image size, so no test tier can own this |
| Gate-behaviour proof | Host test tier — `tests/test_check_size_baseline.py` (CI leg 3) | — | Proves the checker fails on a real violation by running it as a subprocess against committed fixtures. This is the tier that **breaks** when the baseline moves without severance |
| Token-budget arithmetic (LAND-07) | Record tier — `.planning/v1.33/` | Host DB (`pinouts.json`, `chip_database.json`) as the *input* | The conclusion is a record, not code. The inputs are host data files, read-only |
| Load-flakiness characterisation | Record tier — `.planning/v1.33/` | — | A property of the machine and the suite, not of the tree; it can only be recorded, never gated |

---

## Standard Stack

**No new package is introduced by this phase, in any ecosystem.** Every tool it needs is already in the tree or on the machine.

### Core (all pre-existing)
| Tool | Version | Purpose | Why standard |
|------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 `[VERIFIED: pio in $PATH, matches size_baseline.json meta.platformio_core]` | Cold AVR builds, native Unity runs | The project's only build system |
| `avr-gcc` | 7.3.0 `[VERIFIED: ~/.platformio/packages/toolchain-atmelavr]` | Compiles the image; `sizeof` oracle for LAND-05 | Bundled by `platform-atmelavr` 5.2.0 |
| `avr-nm` / `avr-objdump` | same toolchain `[VERIFIED: run this session]` | Symbol sizes and `__udivmodsi4` call-site counting for LAND-06 | Only the linked ELF can witness a call site |
| Unity + ArduinoFake 0.4.0 | via `platformio.ini` | The 17-suite native test tier | Established |
| pytest | 9.1.1 `[VERIFIED: python3 -m pytest]` | `tests/` — the checker's own gate suite | CI leg 3 |
| `python3` | 3.12 (system) `[VERIFIED]` | Runs `scripts/check_*.py` | Note: `pio`'s bundled python has **no** pytest — use system `python3 -m pytest` (`155-RESEARCH.md:1022`) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `rm -rf .pio/build/<env>` + one `pio run -e <env>` | `check_size_baseline.py --rebuild` | **Do not.** `_rebuild_avr` (`scripts/check_size_baseline.py:753`) runs `pio run -t clean -e <env>`, **not** `rm -rf`. LAND-01 mandates the `rm -rf` recipe, so `--rebuild`'s log cannot be the transcription source for the re-record. `--rebuild` is fine for *checking*, never for *recording* |
| A trace-diff oracle for LAND-05/LAND-06 | the existing register-recording harness in `test_val_5v_page` | Viable for LAND-06 **only**, and only for register writes. Native trace stubs record **no time**, so no trace diff can attest LAND-06's runtime claim; and stubs can miss register-write elision unless `rurp_register_utils.h` is included in `host_stubs` |
| Editing `jsmn.h`'s live struct only | also editing the dead second implementation copy at `jsmn.h:117-486` | The header carries a full duplicate of the implementation, guarded by `#ifndef JSMN_HEADER` while `#define JSMN_HEADER` sits at `jsmn.h:34` — so it compiles in **no** TU. Its 11 `-1` sentinel lines are dead. Consistency is a judgement call; correctness does not require it |

**Installation:** none. `[VERIFIED: no package install is required — this phase adds zero dependencies]`

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages in any ecosystem.** No `npm`, `pip`, `cargo` or PlatformIO library dependency is added, removed or moved. `lib/jsmn/` is already vendored in-tree (single commit `155b02f`, "Change json parser to jsmn and protocol fixes") and is already locally modified relative to upstream (`JSMN_HEADER`/`JSMN_STRICT` are `#define`d inside the header; `jsmn.c` carries a hand-added `/* to quiet a warning from gcc*/` comment). `[VERIFIED: git log --oneline -- lib/jsmn/ returns exactly one commit]`

**Packages removed due to [SLOP] verdict:** none — no package was proposed.
**Packages flagged as suspicious [SUS]:** none.

---

## Findings

### F-1 — LAND-01: the cold recipe, the three envs, the native blocks, and the figures

**The convention lives inside the file it governs.** `scripts/baseline/size_baseline.json`:

- `meta.generated_by` — *"each `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` invocation … The figures below are **TRANSCRIBED, not computed**, from the three cold-rebuild logs"* `[VERIFIED: read this session]`
- `meta.note` — the Phase-144 generation used `pio run -t clean -e <env>` instead. **Both forms appear in the file's own history**; LAND-01's criterion mandates the `rm -rf` form, which is also the most recent (quick task 260820-a7w).
- `meta.warm_vs_cold_correction` — *"A future reader who wants to LOWER any of these three watermarks must re-measure cold first, in this exact `rm -rf` + single-invocation sequence, and never guess a new figure down from prose or from a warm re-run."*

**The three AVR envs:** `uno`, `uno328pb`, `leonardo` — `AVR_ENVS` at `scripts/check_size_baseline.py:148`. `[VERIFIED]`

**The "native blocks" — there are two, and they are not the same set:**

| Block | Envs recorded | Consumer |
|-------|---------------|----------|
| `native_envs` | `native`, `native_nodevtools`, `native_pinmap_provisional` | `check_size_baseline.py`'s `compare_native`. `NATIVE_ENVS` at `:149` is only the **two** pinned envs — the third is recorded *"only so `compare_native` and `check_build_warnings.py`'s `check_env` do not raise on that env name, never to widen MERGE-06's own two-env scope"* (`envs_agree_note`) |
| `warnings.native` | same three | `check_build_warnings.py` |

`platformio.ini` defines **six** native envs (`native`, `native_nodevtools`, `native_params_v131`, `native_loop_v131`, `native_trace_v131`, `native_pinmap_provisional`); only three appear in the baseline. **Do not add the three `*_v131` envs** — the `envs_agree_note` is explicit that the recorded set is deliberate.

**Measured cold position at `785e644`, this session** (throwaway worktree, `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, worktree removed and pruned afterwards):

| Target | Flash | RAM | `warning:` lines |
|--------|-------|-----|------------------|
| `uno` | **23090** | **1562** | 0 |
| `uno328pb` | **23138** | **1568** | 0 |
| `leonardo` | **25234** | **2003** | 0 |

`[VERIFIED: byte-identical to 157-after-figures.md §2, independently re-measured]`

**Native, measured this session on the same tree:** `native` **184/184, 17 suites**; `native_nodevtools` **184/184, 17 suites**. `[VERIFIED]`

**What must move in the file, per block:**

| Field | Recorded today | Must become (if no further code change lands) |
|-------|----------------|-----------------------------------------------|
| `avr_targets.uno.flash_used` / `.flash_free` | 25548 / 7220 | 23090 / 9678 |
| `avr_targets.uno.ram_used` / `.ram_free` | 1575 / 473 | 1562 / 486 |
| `avr_targets.uno328pb.flash_used` / `.flash_free` | 25598 / 7170 | 23138 / 9630 |
| `avr_targets.uno328pb.ram_used` / `.ram_free` | 1581 / 467 | 1568 / 480 |
| `avr_targets.leonardo.flash_used` / `.flash_free` | 27630 / 5138 | 25234 / 7534 |
| `avr_targets.leonardo.ram_used` / `.ram_free` | 2016 / 544 | 2003 / 557 |
| `native_envs.native.cases` / `.succeeded` | 172 / 172 | **184 / 184** |
| `native_envs.native_nodevtools.cases` / `.succeeded` | 172 / 172 | **184 / 184** |

`flash_total` (32768 ×3), `ram_total` (2048/2048/2560), `suites` (17), `native_pinmap_provisional` (11/11/1) and the **entire `warnings` block** stay untouched. `[VERIFIED: warnings measured PASS at this position by 157-after-figures.md leg 4 — `native`/`native_nodevtools` at 998 warnings against a 1166 watermark, INFO not FAIL]`

**Cold builds are cheap on this machine — measured 1.1–1.3 s per env, wall clock.** `[VERIFIED: `time` around a `rm -rf .pio` + `pio run -e uno`]` There is no cost argument for skipping the cold recipe.

**Two stale prose fields the re-record could honestly repair (discretionary):**
- `meta.consumed_by` names **two** consumers. There are **three**: `check_release_assets.py` derives its required asset set from `avr_targets`' **keys** (`scripts/check_release_assets.py:5,15-17`) and **runs in CI** at `beta-build.yml:327`. It reads keys, never values, so the re-record is safe for it — but the field is wrong.
- `envs_agree_note` still quotes a stale `{cases: 151, suites: 17}` pair, already flagged as *"Pre-existing and NOT fixed here"* by `meta.native_case_count_revision_260822`.

---

### F-2 — LAND-02: the green run, the one-sidedness, and exactly four red legs

**The one-sidedness, in source** `[VERIFIED: sed -n '697p;709p']`:

```
697:    if flash_delta > allowance:
709:    if ram_delta > ram_tolerance:
```

Both are strict, growth-only comparisons inside `compare_avr_policy_merge05` (`scripts/check_size_baseline.py:640-724`). A reduction of any magnitude passes. `[VERIFIED]`

**The canonical invocation, run this session on the real cold logs — exit 0:**

```
PASS: uno(flash=23090/32768[-1734<=788=band64+exempt96+seam210+lock288+erase130],ram=1562/2048[-11<=2=seam2]),
      uno328pb(flash=23138/32768[-1736<=788=band64+exempt96+seam210+lock288+erase130],ram=1568/2048[-11<=2=seam2]),
      leonardo(flash=25234/32768[-1672<=724=band0+exempt96+seam210+lock288+erase130],ram=2003/2560[-11<=2=seam2])
```

`[VERIFIED: python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…, exit 0]`

**This PASS line IS the one-sidedness evidence and should be quoted verbatim in the record.** It prints `-1734`, `-1736`, `-1672` against positive allowances of 788/788/724 — a reader can see with their own eyes that the comparison admitted a negative delta without any exemption being authored for it. That is strictly better than restating D-03 in prose.

**No new exemption is authored** (D-03). The five MERGE-05 literals stay exactly as they are: `MERGE05_UNO_CLASS_FLASH_BAND = 64` (`:155`), `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96` (`:199`), `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210` (`:257`), `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES = 288` (`:331`), `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130` (`:421`), plus `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` (`:465`). All six are pinned by `test_base01_is_not_re_anchored_by_the_new_exemption` (`tests/test_check_size_baseline.py:1106`), which reads BASE-01 and the checker's own source and **never a fixture**.

#### The four legs — observed, not predicted

Simulated in the throwaway worktree by re-recording `size_baseline.json` to the figures in F-1 and committing (so the porcelain legs stayed quiet), then running the suite:

```
FAILED tests/test_check_size_baseline.py::test_clean_avr_all_three_envs_pass
FAILED tests/test_check_size_baseline.py::test_clean_native_both_envs_pass
FAILED tests/test_check_size_baseline.py::test_planted_flash_regression_flips_checker_to_failure
FAILED tests/test_check_size_baseline.py::test_default_mode_is_unchanged_by_the_new_flag
4 failed, 10 passed
```

`[VERIFIED: run this session]` — `tests/test_check_build_warnings.py` stayed fully green (the warnings block did not move).

| Leg | `file:line` | Why it reddens | Remedy |
|-----|-------------|----------------|--------|
| `test_clean_avr_all_three_envs_pass` | `tests/test_check_size_baseline.py:523` | Reads `captured_build_v153_{uno,uno328pb,leonardo}.log` (25548/25598/27630) against the **live** baseline in default = byte-identity mode | 3 new cold captures |
| `test_default_mode_is_unchanged_by_the_new_flag` | `:1362` | Same three fixtures, same reason | reuses the same 3 captures |
| `test_planted_flash_regression_flips_checker_to_failure` | `:612` | Asserts both the baseline figure (27630) and the observed figure (28142) appear in the FAIL text | 1 new plant at `new_leonardo + 512`, and the leg's asserted figures updated |
| `test_clean_native_both_envs_pass` | `:562` | Reads `captured_test_native{,_nodevtools}_summary.log` (172) against `native_envs.cases` | **update the two native summary fixtures IN PLACE** — the established convention for that pair (`:575-576`) |

**Legs that did NOT redden, and why that matters:** `test_policy_merge05_fires_on_uno_class_over_band` (`:1202`), `test_policy_merge05_fires_on_leonardo_growth` (`:1257`), `test_policy_merge05_fires_on_ram_move` (`:1298`), `test_policy_merge05_permits_the_measured_landing_deltas` (`:757`), all four arms of `test_policy_merge05_admits_the_documented_defect_fix` (`:837`), `test_baseline_seam_precedence_flips_clean_log_to_fail` (`:702`), and `test_base01_is_not_re_anchored_by_the_new_exemption` (`:1108`). Every one of them reads **BASE-01**, which does not move, or tampers with its own baseline copy. `[VERIFIED]`

**Therefore the severance is much smaller than every prior generation's.** `*_fullflash*` → `*_v151*` → `*_v153*` each replanted **thirteen** files, because each of those phases *widened the allowance* and every policy plant was derived as `allowance + 1`. This phase authors **no exemption**, so the allowance is unchanged and the policy plants remain valid.

**Minimal `*_v158*` family — 4 new files:**
- `captured_build_v158_{uno,uno328pb,leonardo}.log` — Group 1, the three cold captures, transcribed byte-for-byte (these are the *same* logs LAND-01 transcribes; capture once, use twice)
- `planted_size_baseline_flash_regression_v158.log` — Group 4, derived from the new `leonardo` capture with the standing `+512 B` offset every generation since Phase 123 has used

**Plus 2 updated in place:** `captured_test_native_summary.log`, `captured_test_native_nodevtools_summary.log` (172 → 184).

**Group 2 (`merge05_base01_anchor_v158_*`) and Group 3 (an exemption-admission trio) are not needed** — Group 2 exists only as the derivation source for Group 4's *policy* plants (none of which move), and Group 3 exists only to prove a new exemption's admission (none is authored). **Say this explicitly in the severance record**, because every prior generation's docstring documents "the same four groups", and a reader will otherwise think two groups were forgotten. The `*_v153*` family is **retired in place and KEPT**, never deleted — the standing disposition since the 260820-a7w severance.

---

### F-3 — LAND-03: the BASE-01 native case-count mismatch

**Confirmed, and the criterion's figure is stale.**

- `scripts/baseline/size_baseline_base01.json` → `native_envs.native.cases = 141`, `native_envs.native_nodevtools.cases = 141`, `suites = 17`, `succeeded = 141`. `[VERIFIED]`
- Observed today is **184**, not the 172 the ROADMAP criterion and REQUIREMENTS LAND-03 both state. The trajectory is `141 (Phase 124) → … → 172 → 177 → 184`, the last two hops added by Phase 157 plans 04 and 05 (`157-after-figures.md` §16, and `STATE.md:2460`). `[VERIFIED]`
- `size_baseline_base01.json` has **no `native_pinmap_provisional` key** — a `--native-log native_pinmap_provisional=…` against BASE-01 would `KeyError`. Not currently reachable, worth knowing.

**The exit-1 mechanism, precisely.** The criterion says the invocation *"exit 1 … before it ever reports flash"*. The literal mechanism is subtler and the record should state it correctly:

- `compare_native` (`scripts/check_size_baseline.py:726-749`) is **not policy-aware** — it is strict equality in both modes. `--policy merge05` changes only the AVR comparison.
- In `main()`, the AVR loop runs **first** (`:882`) and the AVR comparison **passes**; its decomposition string is appended to `compared`. Then the native loop runs (`:922`) and appends two failures. Then `if all_failures: _print_fail(...); return 1` (`:939`) — and `_print_pass` is never reached (`:947`).
- So the flash figures **are** compared and **do** pass; it is the **PASS: report line that carries them** that is suppressed. "Before it ever reports flash" is true of the *report*, not of the *comparison*.

**Reproduced this session** with `--policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild`:

```
FAIL:
  native: cases baseline=141 observed=184
  native_nodevtools: cases baseline=141 observed=184
```

**Exactly two lines, both native; no AVR flash or RAM line.** `[VERIFIED]`

**Not caused by this milestone.** The size-reduction diff of Phases 155–157 touches `test/` only at `test/native/avr/test_val_5v_page`, `test_eeprom28c_sdp` (DEAD-06, assertion removal — no case-count change) and the new cases Phase 157 deliberately added. `[CITED: 155-RESEARCH.md:857, 157-after-figures.md §16]`

#### Fix vs carry — the costs, measured

| Branch | What it costs | Gate consequence | Doctrinal risk |
|--------|---------------|------------------|----------------|
| **FIX** — set BASE-01 `native_envs.{native,native_nodevtools}.{cases,succeeded}` 141 → 184 | 4 JSON integers + a `meta` note | **Zero legs redden.** `test_base01_is_not_re_anchored_by_the_new_exemption` pins only `flash_used`, `ram_used` and `flash_total`; it never reads `native_envs`. **Verified in the probe by making this exact edit** — the red-leg list did not grow | Touching a file whose own `meta` once claimed immutability. **But the precedent is established and machine-checked**: quick task 260820-a7w already moved BASE-01's `flash_total` on the grounds that *board identity* is a licensed axis while *growth* is not, and the leg's docstring (`:1108-1127`) records that split in so many words. Test-case count is a third axis — a *test-inventory* axis — and a frozen inventory count is monotonically invalid, since tests only accumulate |
| **CARRY** — record it and use the `--avr-log` form for LAND-02's green run | 0 code | The `--rebuild` form stays red forever. Every future reader re-derives the confusion | None, but the phase ships a permanently-red canonical invocation into a *landing* phase whose stated purpose is *"leave the gate story unambiguous for whoever moves sizes next"* |

**Recommendation: FIX, on the axis-split argument, and record the axis split explicitly** (that a frozen case count is an inventory floor, not a growth anchor). If the operator prefers CARRY, LAND-02 is still satisfiable today via the `--avr-log` form — F-2's green run used exactly that.

**A third option exists and is worth naming for completeness:** make `compare_native` treat the case count as a **floor** (`observed < baseline` fails) under `--policy merge05` only. That is the most semantically honest fix, but it changes gate behaviour, needs a new fixture pair and a planted negative, and widens the phase. **Not recommended for a landing phase.**

---

### F-4 — LAND-04: proven, but the honest statement has two clauses

**Clause 1 — proven as written.**

```
$ grep -rn "check_size_baseline" .github/          # firestarter
(no output, exit 1)
$ grep -rn "check_size_baseline" .github/          # meta repo /workspaces
(no output, exit 1)
$ grep -rn "check_size_baseline" firestarter_app/.github/
(no output)
$ grep -rn "check_size_baseline" --include="*.yml" --include="Makefile" --include="*.sh" .
(no output)
```

`[VERIFIED: run this session across all three repos]`

Same for `check_build_warnings.py` and `check_no_heap_or_64bit_symbols.py`. **Of the eight `scripts/check_*.py` in the firmware repo, exactly one is invoked by any workflow:** `check_release_assets.py` at `beta-build.yml:327`. The other seven — `check_build_warnings.py`, `check_cmake_manifest.py`, `check_erase_no_vpp.py`, `check_landing_range.py`, `check_no_heap_or_64bit_symbols.py`, `check_orphan_provisional.py`, `check_size_baseline.py` — are **local-run obligations**. `[VERIFIED]`

**Clause 2 — the checker IS executed in CI, and this phase depends on it.**

`tests/test_check_size_baseline.py` invokes `scripts/check_size_baseline.py` as a real subprocess against committed fixtures, and that suite runs in CI:

- `build.yml:161` — `run: pytest tests/ -v` (step name is the legacy *"Run update_version.py tests"*, but it runs the whole directory). **Ungated by any `if:`** — it sits above the publish boundary at `:164`.
- `build.yml:16-34` — `on: push: branches: ['**', '!beta']`, plus `pull_request`. **This fires on the v1.33 milestone branch.**
- `beta-build.yml:134` — the same leg on `beta`.

**Consequence, and this is the phase's central planning constraint:** re-recording `size_baseline.json` without severing the fixtures **turns CI red**. The local-run obligation is about the *measurement* (nothing compares the real tree's build output to the baseline automatically) — it is **not** about the checker's own tests, which are automated and will notice.

**Two in-tree claims that contradict this and are candidates for correction (discretionary, and squarely on LAND-04's own subject):**
1. `tests/test_check_size_baseline.py:459` — *"Neither repository's CI runs this suite — no CI leg exercises it in either repository."* **False** as of `build.yml:161`.
2. `tests/meta_presence.py:56-58` — *"This module executes in NO CI leg on this branch: `pytest tests/ -v` runs only in `build.yml` (push/PR to `main`) … neither fires on this firmware milestone branch."* **False** — `build.yml`'s branch filter was widened to `['**', '!beta']`, and the widening is documented in that same workflow's own comment at `:4-14`.

Correcting these is not required by LAND-04, but leaving a phase whose headline criterion is *"never implied to be automated"* shipping two in-source claims that get the automation boundary backwards is worth a decision rather than an omission.

**CI legs, exhaustively, on this branch:** `pio test -e native` (`build.yml:142`), `pio test -e native_nodevtools` (`:155`), `pytest tests/ -v` (`:161`), `pio run` (`:193`), plus the separate `py32f071.yml` ARM build (`on: push: branches: ['**']`). **Nothing else.**

---

### F-5 — LAND-05: MEASURED, GREEN, and a flash win

#### Where the type lives

- `lib/jsmn/src/jsmn.h:74-92` — the live definition:
  ```c
  typedef struct jsmntok {
    jsmntype_t type;
    int start;
    int end;
    int size;
  #ifdef JSMN_PARENT_LINKS
    int parent;
  #endif
  } jsmntok_t;
  ```
  `JSMN_PARENT_LINKS` is **not** defined anywhere in the tree, so `parent` does not exist in the shipped struct. `[VERIFIED]`
- `include/json_parser.h:17` — `#define NUMBER_JSNM_TOKENS 64`
- `src/firestarter.cpp:54` — `static jsmntok_t tokens[NUMBER_JSNM_TOKENS];` — the only instance; `512 B` on AVR today
- `test/native/avr/test_read_timing/test_read_timing_params.cpp:84` — a second, stack-local `jsmntok_t tokens[NUMBER_JSNM_TOKENS]`, the only test that allocates the real budget
- `platform/py32f071/CMakeLists.txt:70` — the ARM port compiles the same `lib/jsmn/src/jsmn.c`

#### The `-1` sentinels — twelve, with a reproducible counting rule

REQUIREMENTS says *"`jsmn.c` uses `-1` sentinels in twelve places"*. The claim is correct under exactly one counting rule, and the record should state the rule so the number is auditable:

**Twelve = the number of `start`/`end` **field references** compared or assigned against `-1`, across six lines of `lib/jsmn/src/jsmn.c`:**

| `jsmn.c` line | Text | Field refs |
|---------------|------|-----------|
| `:15` | `tok->start = tok->end = -1;` | 2 |
| `:222` | `if (token->start != -1 && token->end == -1) {` | 2 |
| `:241` | `if (token->start != -1 && token->end == -1) {` | 2 |
| `:256` | `if (token->start != -1 && token->end == -1) {` | 2 |
| `:290` | `if (tokens[i].start != -1 && tokens[i].end == -1) {` | 2 |
| `:348` | `if (tokens[i].start != -1 && tokens[i].end == -1) {` | 2 |
| | **total** | **12** |

`[VERIFIED: grep -n -- "-1" lib/jsmn/src/jsmn.c, 17 matching lines, 22 textual "-1" occurrences]`

The other eleven `-1` occurrences (`:18` `parent`, `:193`, `:230`, `:231`, `:245`, `:251`, `:269`, `:282`, `:316`, `:332`, `:364`) are on `parser->toksuper`, `token->parent` (dead) and the loop index `i` — **none of them is a token-array field**, so none is affected by narrowing the struct. `parser` is a single stack local (`src/firestarter.cpp:53`); narrowing it would save 0 bytes of the array.

The dead implementation copy at `jsmn.h:117-486` carries the same eleven textual sentinel lines. It compiles in no TU (`#define JSMN_HEADER` at `:33` precedes `#ifndef JSMN_HEADER` at `:106`). `[VERIFIED]`

#### The 6-byte layout, with `start`/`end` still signed

```c
typedef struct jsmntok {
  uint8_t type;   /* was jsmntype_t (enum -> 16-bit int on AVR); values 0,1,2,4,8 */
  uint8_t size;   /* was int; max observed is an object's pair count (~13) or an array's length (<=19) */
  int start;      /* UNCHANGED, signed -- carries the -1 sentinel */
  int end;        /* UNCHANGED, signed -- carries the -1 sentinel */
} jsmntok_t;
```
plus `#include <stdint.h>` at the top of `jsmn.h`.

**`sizeof` measured with the real toolchain**, `avr-gcc -mmcu=atmega328p -Os`, via `avr-nm -S` on a common-symbol probe:

| Layout | AVR `sizeof` | Host (`int` = 32-bit) `sizeof` |
|--------|--------------|--------------------------------|
| current (`jsmntype_t, int, int, int`) | **8** | **16** |
| `uint8_t type; uint8_t size; int start; int end;` | **6** | **12** |
| `int start; int end; uint8_t type; uint8_t size;` | **6** | **12** |

`[VERIFIED: compiled and measured this session]` — AVR gives every type 1-byte alignment, so field order is irrelevant there; on the host both orders happen to give 12. `64 × (8 − 6) = 128 B` RAM. **The `−128 B` figure is exact.**

#### The measured result — and it contradicts REQUIREMENTS' `+30 B flash`

Cold builds, throwaway worktree at `785e644`, `rm -rf .pio/build/<env>` + one `pio run -e <env>`:

| Target | Flash before | Flash after | Δ flash | RAM before | RAM after | Δ RAM |
|--------|-------------|-------------|---------|-----------|----------|-------|
| `uno` | 23090 | **22952** | **−138 B** | 1562 | **1434** | **−128 B** |
| `uno328pb` | 23138 | **23000** | **−138 B** | 1568 | **1440** | **−128 B** |
| `leonardo` | 25234 | **25098** | **−136 B** | 2003 | **1875** | **−128 B** |

`[VERIFIED: measured this session]`

**REQUIREMENTS LAND-05's `+30 B flash` is not reproducible.** The narrowing is a flash win of `136–138 B` as well as the predicted `−128 B` RAM — plausibly because 8-bit loads, stores and compares on `type`/`size` are cheaper than 16-bit on an 8-bit MCU, so the smaller struct also shortens the access code. The `+30 B` figure was presumably measured on a different layout (e.g. one that kept `jsmntype_t type` and narrowed only `size`, or used bitfields).

#### The suite result — the "breaks the suite" reading is refuted at this position

| Leg | Result | Duration |
|-----|--------|----------|
| `pio test -e native` | **184 test cases: 184 succeeded**, 17 suites | 53.97 s |
| `pio test -e native_nodevtools` | **184 test cases: 184 succeeded**, 17 suites | 61.26 s |
| `python3 -m pytest tests/ -q` | 4 failed / 319 passed / 32 skipped — **all four failures are the porcelain-assertion artefact of a dirty tree** (`assert ' M lib/jsmn/src/jsmn.h\n' == ''`), and the 32 skips are the worktree artefact of F-12 | 12.20 s |

`[VERIFIED: run this session]`

**Nothing broke.** The four pytest failures are `test_requirement_case_mapping_v131.py::test_planted_renamed_case_is_detected`, `::test_planted_emptied_scan_root_fails_the_non_vacuity_leg`, `test_trace_segment_exhaustiveness_v131.py::test_planted_unclassifiable_entry_is_located` and `::test_planted_delete_and_duplicate_defeats_a_count_only_check` — four legs that assert `git status --porcelain` is empty after their own planted mutation. **They redden for any uncommitted edit, of any file.** Do not conflate these four with F-2's four size-baseline legs; the plan should name both sets separately so nobody mistakes one for the other.

#### How to distinguish a real failure from D-04's load flakiness

The recipe, stated so the plan can write it as an action rather than a hope:

1. Run the suite **on the committed tree, before the edit**, three times, recording case count *and* wall time each run. The pre-edit baseline is `184/184` (this session: 22.2 s, 54.0 s, 61.3 s — see F-8).
2. Apply the edit and **commit it** — then run. Committing first keeps the four porcelain legs quiet and makes `pytest tests/` interpretable.
3. On any red run, **re-run before concluding anything** (D-04). A count that is `184` on the re-run is a flake; a count that is stably below `184`, or a *named* suite that fails deterministically across runs, is real.
4. If it fails, the criterion requires the failure be **named** — quote the failing suite, the failing case, and the assertion text, not "the suite broke".

**The plan may skip step 1's third run only if it states that it did.** Three of this session's own runs sat at 22 s, 54 s and 61 s with identical results, so wall time carries no signal on its own.

#### The one open risk: the ARM build

`platform/py32f071/CMakeLists.txt:70` compiles `lib/jsmn/src/jsmn.c`, and `py32f071.yml` is the **LOUD ARM gate** (`on: push: branches: ['**']`, no `continue-on-error`, with `pull_request` path-filtered on `lib/jsmn/**` at `:33`). Nothing is pushed during phase execution, so **the ARM build is not verified locally** — `arm-none-eabi-gcc` and `cmake` are both absent from this machine `[VERIFIED: which returns nothing]`. On ARM the narrowed struct is 12 B (host measurement above is the same ILP32/LP64 alignment story) and `<stdint.h>` is available in newlib, so a break is unlikely — but "unlikely" is not "verified". Options, in cost order:
1. Install the ARM toolchain locally (known to work with two extra newlib packages CI omits) and build once.
2. Accept the `py32f071.yml` run at merge time as the verification, and **record the ceiling explicitly** in the phase record: *"the ARM half of LAND-05 is unverified locally; the loud ARM gate fires on push."*

Option 2 is defensible for a firmware-only phase that pushes nothing, **provided the ceiling is stated rather than left implicit.**

---

### F-6 — LAND-06: the two divisions, the mask, and the measurement

#### Exact locations

`src/proms/flash_5v_page.cpp`:

- `:27-31` — `static uint32_t flash_5v_page_page_size(uint32_t mem_size)`; three literal returns: `64` if `mem_size <= 65536`, `128` if `<= 262144`, else `256`. **Every return is a power of two, provable by inspection of three lines.** `[VERIFIED]`
- `:105` — `void flash_5v_page_write_execute(firestarter_handle_t* handle) {`
- `:106` — `uint32_t page_size = flash_5v_page_page_size(handle->mem_size);` (hoisted above the loop already)
- `:107` — `for (uint32_t i = 0; i < handle->data_size; i++) {`
- **`:116` — `bool is_page_start = (address % page_size) == 0;`** ← division 1, per byte
- **`:124` — `bool reached_page_end = ((address + 1) % page_size) == 0;`** ← division 2, per byte

#### The two `__udivmodsi4` calls, confirmed in the linked image

```
$ avr-nm --print-size .pio/build/uno/firestarter_uno.elf | grep write_execute
00002d68 000001d4 t _Z27flash_5v_page_write_executeP18firestarter_handle    # 468 B

$ avr-objdump -d --start-address=0x2d68 --stop-address=0x2f3c … | grep call
2e44:  0e 94 40 2c   call 0x5880 ; <__udivmodsi4>
2e64:  0e 94 ef 15   call 0x2bde ; <flash_util_byte_flipping>
2e8a:  0e 94 40 2c   call 0x5880 ; <__udivmodsi4>
2ef4:  0e 94 67 07   call 0xece  ; <rurp_log_id>
```

**Exactly two `__udivmodsi4` calls, both inside the loop body.** `flash_5v_page_page_size` and `flash_5v_page_wait_for_page_write` are both fully inlined (no symbols). `[VERIFIED: run this session on all three ELFs; identical shape on `uno328pb` and `leonardo`]`

`__udivmodsi4` itself is `0x44` = **68 B** and has **11 call sites** across the `uno` image. Removing these two leaves **9** — so the helper stays linked and there is **no linkage saving to be had**. `src/proms/eprom_budget.cpp:109` (`per_byte_us % 1000000UL`) is one of the remaining users. `[VERIFIED]`

#### The mask rewrite, and the in-tree precedent

The tree **already contains** the mask form, on algorithm 13:

- `src/proms/eeprom_28c.cpp:628-636` — `static uint32_t eeprom28c_page_mask(uint16_t requested)`, which validates power-of-two-ness and range before returning `requested - 1`
- `src/proms/eeprom_28c.cpp:658` — `const uint32_t page_mask = eeprom28c_page_mask(handle->page_size);` resolved **once, above** the per-byte loop
- `src/proms/eeprom_28c.cpp:737` — `bool page_end = ((address + 1) & page_mask) == 0;`

`[VERIFIED]` **The two cases are not the same problem and the record must not blur them.** Algorithm 13's page size arrives **from the host wire** and could be anything, so it needs a validating resolver. Algorithm 5's page size is derived **internally** from `mem_size` by a three-line function whose every return is a literal power of two, so a bare `page_size - 1` is sufficient and a validating resolver would be dead code. `src/proms/eeprom_28c.cpp:21` already labels `flash_5v_page_page_size()` a *"READ-ONLY ANALOG, byte-frozen, NOT adopted here"* — the non-adoption runs in both directions.

The rewrite measured:

```c
    uint32_t page_size = flash_5v_page_page_size(handle->mem_size);
    const uint32_t page_mask = page_size - 1;          /* every return is 64/128/256 */
    ...
        bool is_page_start = (address & page_mask) == 0;
    ...
        bool reached_page_end = ((address + 1) & page_mask) == 0;
```

#### The measurement — cited either way, as the criterion requires

Cold builds, same worktree, same recipe:

| Target | Flash before | Flash after | Δ flash | Δ RAM |
|--------|-------------|-------------|---------|-------|
| `uno` | 23090 | **23112** | **+22 B** | 0 |
| `uno328pb` | 23138 | **23162** | **+24 B** | 0 |
| `leonardo` | 25234 | **25256** | **+22 B** | 0 |

`[VERIFIED: measured this session]`

**REQUIREMENTS LAND-06's `+22 B (measured)` holds on `uno` and `leonardo` and is 2 B low on `uno328pb`.** Post-mask, `flash_5v_page_write_execute` grows `468 B → 490 B` (`0x1d4 → 0x1ea`) on `uno`, contains **zero** `__udivmodsi4` calls, and the image total drops `11 → 9` call sites. `[VERIFIED]`

**The cost is fully additive with LAND-05**, measured directly rather than assumed — both changes together: `uno` **22974**, `uno328pb` **23024**, `leonardo` **25120**; RAM `1434 / 1440 / 1875`; `native` **184/184** in 22.2 s. `23090 − 138 + 22 = 22974` ✓, `23138 − 138 + 24 = 23024` ✓, `25234 − 136 + 22 = 25120` ✓. `[VERIFIED]`

#### The honest case against taking it

1. **It is a size cost with an unquantified benefit.** D-02 forbids a bench criterion, so the runtime win cannot be measured in this milestone at all. The phase would be trading `22–24 B` of a shrink-only milestone for a number nobody may produce.
2. **The path has no behavioural native coverage.** `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` has 14 `RUN_TEST` cases (`:506-529`); the only one that executes `write_execute` is `test_5v_page_write_execute_emits_sdp` (`:281`), which drives a **4-byte** write via `make_write_handle_with_data` and asserts the SDP signature appears **at all**. A 4-byte write never crosses a 64-byte boundary. **So neither `%` site's boundary behaviour is exercised by any test today**, and a mask rewrite would be landed on inspection alone.
3. Two of the three targets' figures came out as predicted and one did not, which is a reminder that the phase should measure at its own final position rather than quote these.

#### If it is taken — the oracle that makes it honest

A boundary test is cheap and time-free, so a trace-stub timing gap does not bite:

- `mem_size = 32768` → `page_size = 64`; `address = 0`; `data_size = 128`
- Expect **exactly 2** SDP `FLASH_ENABLE_WRITE` signatures (page starts at 0 and 64) and **exactly 2** page-end poll windows (at 63 and 127)
- The existing register-recording harness (`recording_contains_sdp_signature`, `:259`) already provides the mechanism; it needs a *counting* variant rather than a boolean one
- Run it **RED against a deliberately wrong mask** (e.g. `page_size` instead of `page_size - 1`) before trusting it — the house rule, and the only way to know the leg is not vacuous

**Adding it moves the native case count `184 → 185` (or `→ 186` for a start-count and an end-count leg), which feeds straight back into LAND-01's `native_envs` figures and the two `captured_test_native*_summary.log` fixtures.** Sequence accordingly.

#### The disconnection the criterion demands

**This is the algorithm-5 flash-page write path only.** `configure_flash_5v_page` (`src/proms/flash_5v_page.cpp:39`) is reached from `configure_memory`'s dispatch for protocols `0x05` / `0x35` / `0x39` (per the suite's own `test_5v_page_0x05/0x35/0x39_*` cases at `:506-515`). The **w27c512-write-slow-3x** work rewrote `eprom_write_execute` in `src/proms/eprom.cpp` — a different file, a different handler, a different protocol family, and a per-byte VPE-settle problem rather than a division problem. **The two share no code and no cause.** REQUIREMENTS "Out of Scope" separately rules `eprom_write_execute` untouchable for this milestone. Any record that mentions both must say this in the same breath.

---

### F-7 — LAND-07: the token arithmetic, re-derived — and the criterion's numbers are not reproducible

#### The budget and its consumer

- `include/json_parser.h:17` — `#define NUMBER_JSNM_TOKENS 64`
- `src/firestarter.cpp:54` — `static jsmntok_t tokens[NUMBER_JSNM_TOKENS];` → `64 × 8 = 512 B` today, `64 × 6 = 384 B` if LAND-05 lands
- `src/firestarter.cpp:57` — `jsmn_parse(&parser, handle->data_buffer, handle->data_size, tokens, NUMBER_JSNM_TOKENS)`
- Overflow behaviour: `jsmn_alloc_token` returns `NULL` when `toknext >= num_tokens` (`lib/jsmn/src/jsmn.c:11-13`), which becomes `JSMN_ERROR_NOMEM` (`-1`) — the whole command is rejected. **A budget overflow is a silent command failure, not a partial parse.**

#### The wire keys the firmware accepts

Eleven table rows (`src/json_parser.c:73-92` PROGMEM strings, `:134-166` the `key_parsers[]` table): `memory-size`, `address`, `flags`, `chip-id`, `pin-count`, `pulse-delay`, `vpp_mv`, `algorithm`, `read-settling-delay`, `read-strobe-us`, `page-size`. Plus `cmd` / `state` (alternates, `src/json_parser.c:503`, `:391`) and the `bus-config` object (`:329`, `:397`). Unknown keys are **skipped, two tokens at a time** (`:340`) — deliberate forward compatibility, and load-bearing per Backlog 999.35. `[VERIFIED]`

`parse_bus_config` accepts exactly four inner keys: `bus` (array), `static-high` (array), `rw-pin` (`:506`), `vpp-pin` (`:510`). `[VERIFIED]`

#### What the host can actually emit

`firestarter_app/firestarter/database.py:529` `convert_to_programmer` builds the wire dict: `memory-size`, `algorithm`, `pin-count`, `vpp_mv`, `pulse-delay`, optional `chip-id`, optional `bus-config`, optional `page-size`. `chip_resolver.py:74` is the caller. `eprom_operations.py:551-558` then adds `cmd`, `flags` and optional `address`; `:1108-1114` merges optional `read-settling-delay` / `read-strobe-us`. **`serial_comm.py:878` sends that dict with no further keys added.** `[VERIFIED]`

**Maximum 13 top-level keys**, of which 12 are scalars and one is `bus-config`. `get_bus_config` (`database.py:253`) emits at most the four inner keys, and drops `vpp-pin` entirely when it resolves to `ROM_CE`/`ROM_OE` (`:289`).

#### The arithmetic

jsmn's own counting rule (`jsmn_parse`'s `count`): one token per `{`, per `[`, per string, per primitive.

```
root object                                     1
12 scalar pairs (key + value)               12×2 = 24
"bus-config" key + its object                   2
  "bus" key + array token + N elements     2 + N
  "static-high" key + array + M elements   2 + M   (only when non-empty)
  "rw-pin" key + value                         2   (when present)
  "vpp-pin" key + value                        2   (when present)
```

**From `pinouts.json` — 15 pin-map records, largest `address-bus-pins` = 19, largest `static-high-pins` = 1** `[VERIFIED: derived programmatically from firestarter_app/firestarter/data/pinouts.json this session]`. Per record:

| pin map | `address-bus-pins` | `static-high-pins` | `rw-pin` | `vpp-pin` | total tokens |
|---------|-----|----|----|-----|------|
| `DIP32_27C020` | 18 | 0 | ✓ | ✓ | **51** ← maximum |
| `DIP32_STD` | 19 | 0 | — | ✓ | 50 |
| `DIP32_SST39SF040` | 19 | 0 | ✓ | — | 50 |
| `DIP32_28C512_EEPROM` | 16 | 0 | ✓ | — | 47 |
| `DIP28_27512` | 16 | 0 | — | ✓ | 47 |
| `DIP24_2732` / `DIP24_2532` / `DIP28_27256` / `DIP28_28C256` | 12–15 | 0–1 | mixed | mixed | 46 |
| `DIP24_2716` / `DIP28_2764` | 11–14 | 0–1 | mixed | mixed | 45 |
| `DIP28_JEDEC_SRAM_8K` / `DIP28_28C64` | 13 | 0 | ✓ | — | 44 |
| `DIP24_6116` / `DIP24_2816` | 11 | 0 | ✓ | — | 42 |

**Three numbers, each with its own scope, and the record must keep them apart:**

| Bound | Value | Headroom vs 64 | Derivation |
|-------|-------|----------------|------------|
| **Observed maximum over the real chip database** | **50** | **14** | Swept every entry of `chip_database.json` through `convert_to_programmer` and added the runtime keys; maximum hit by the `W29C020, W29C020C, W29C022` family (282 wire bytes) `[VERIFIED: computed this session]` |
| **Maximum over any real pin map, with every optional scalar present** | **51** | **13** | `DIP32_27C020` (18 bus pins + `rw-pin` + `vpp-pin`) + all 12 scalars |
| **Field-wise-maximum synthetic bound** (each field at its own maximum, ignoring that no real record combines them) | **55** | **9** | 19 bus pins **and** a `static-high` **and** `rw-pin` **and** `vpp-pin` — a combination that exists in no pin map |

**The criterion's `57 tokens` / `7 tokens of headroom` is not reproducible by any of the three rules.** Even the loosest synthetic composition — which is exactly the "largest `address-bus-pins` = 19 and `static-high-pins` = 1, plus every optional wire key" recipe the criterion names — yields **55**, not 57. The record must carry the derived numbers with their derivation, and note the 2-token gap it cannot account for. (The most likely origin is counting `state` alongside `cmd`, which the firmware treats as alternates and the host never sends together.)

#### The conclusion still holds — but on a different argument than the criterion assumes

A 13-token headroom does not by itself say "not reducible". `64 → 56` would save `64 B` of RAM today (or `48 B` after LAND-05) and still clear the real maximum by 5. **So the record must not claim arithmetic impossibility; it must claim the headroom is a load-bearing forward-compatibility budget:**

1. `json_parse` **silently skips unknown keys, two tokens at a time** (`src/json_parser.c:517`). That is the mechanism by which the host can add a wire field without a firmware release — the property Backlog 999.35 explicitly names as *"load-bearing forward-compatibility"* that a packed binary frame would destroy. **Today's 13 tokens of headroom is 6 future host-added scalar keys.** Cutting to 56 leaves 2.
2. Overflow is a **silent whole-command rejection** (`JSMN_ERROR_NOMEM`), not a graceful degradation. A budget sized to the current corpus fails closed on the first chip whose pin map is one entry longer.
3. **`pinouts.json` is host data and grows.** A future 40-pin map, or a pin map with both 19 address lines and a `static-high` entry, reaches the synthetic 55 immediately.
4. The array can therefore only shrink meaningfully via **LAND-05** (`8 → 6 B`, a real `−128 B` with no budget change) or via **v1.28 / Backlog 999.35** (delete the tokenizer entirely, `−512 B` RAM), exactly as the criterion states.

**Recommended record wording:** *not reducible without spending the forward-compatibility budget the unknown-key skip depends on* — with all three bounds, the derivation, and the `57` discrepancy stated.

---

### F-8 — LAND-08: the flakiness evidence, plus three new data points

**The primary source is `155-RESEARCH.md:846`** (Pitfall 5 — the native suite is load-flaky, D-04):

> measured 172/172 at ~35 s (×5), 171/172 once at 1:13, 158-cases-with-2-ERRORED once at 1:44 — failure correlates with **run duration**, not tree content. The scoping session fell into this trap itself.

Supporting records: `REQUIREMENTS.md` LAND-08 restates the same three data points; `STATE.md:65` carries them; `157-before-figures.md:247-250` adds *"`157-RESEARCH.md`'s own session recorded three `native` runs at 19.8 s, 25.3 s and 54.6 s — duration varied 2.8× while the 172/172 result did not"*; `156-07-SUMMARY.md:110` adds three runs at 21.6 s, 31.6 s and 32.6 s, all 172/172.

**Three new same-tree data points, measured this session at the post-157 position:**

| Tree state | Env | Result | Duration |
|-----------|-----|--------|----------|
| `785e644` + narrowed `jsmntok_t` | `native` | 184/184, 17 suites | **53.97 s** |
| `785e644` + narrowed `jsmntok_t` | `native_nodevtools` | 184/184, 17 suites | **61.26 s** |
| `785e644` + narrowed `jsmntok_t` + mask | `native` | 184/184, 17 suites | **22.18 s** |

`[VERIFIED]` — **a 2.8× spread in wall time with an identical result**, on trees that differ only by an edit that cannot affect the case count. This directly extends the recorded evidence and, importantly, shows the *converse* of the original observation: a long run is not itself a failure. The honest statement is **duration is a necessary-but-not-sufficient correlate of the observed failures**, not a predictor.

**What the record must forbid, in plain words:** attributing any suite failure to the tree on N=1; quoting a wall time as evidence of anything; and treating a single case-count mismatch as a regression without a re-run.

---

### F-9 — Firmware-only compatibility, verified

Nothing this phase can do touches the host. Specifically:

- **LAND-05** edits `lib/jsmn/src/jsmn.h` only. No host file reads `jsmntok_t`; no wire byte changes; `jsmn_parse`'s API is unchanged. **No protocol-parity constant is involved** — `jsmntok_t` has no counterpart in `firestarter_app/firestarter/constants.py`.
- **LAND-06** edits `src/proms/flash_5v_page.cpp` only, and changes no observable behaviour (`x % 2^n == x & (2^n - 1)` for unsigned `x`).
- **LAND-07** *reads* `firestarter_app/firestarter/data/pinouts.json` and `chip_database.json`. Reading is not changing.
- **LAND-01/02/03/04/08** touch `scripts/baseline/*.json`, `tests/fixtures/*`, `tests/test_check_size_baseline.py` and `.planning/` only.

`[VERIFIED: no `firestarter_app` file is a candidate for edit under any branch of this phase]`

---

### F-10 — Where the records go

Every LAND criterion that is a *record* has a settled home. `.planning/v1.33/` holds this milestone's measurement records, and all three sibling phases used the same pair:

```
.planning/v1.33/155-before-figures.md   155-after-figures.md
.planning/v1.33/156-before-figures.md   156-after-figures.md
.planning/v1.33/157-before-figures.md   157-after-figures.md
```

The `-before-figures.md` files carry YAML frontmatter with `title`, `phase`, `plan`, `measured`, `status: AUTHORITATIVE`, `supersedes` and `requirements`, then numbered `##` sections each carrying **the verbatim command that produced every number**. `157-before-figures.md:1-21` is the template. **Confirmed convention, not invented.** `[VERIFIED]`

Notably, `157-before-figures.md`'s own frontmatter already anticipates this phase:

> *"Phase 158 invalidates the AVR image figures captured here (it re-anchors `size_baseline.json` and cold-rebuilds all three targets), so no later plan can re-derive them from this position."*

**Recommendation:** `158-before-figures.md` (the pre-phase position, the four red legs enumerated, the LAND-03/04/07/08 records) and `158-after-figures.md` (the final cold position, the quoted PASS line, the severance inventory, the LAND-05/06 outcomes). Corrections to ROADMAP/REQUIREMENTS prose go **in the record**, per the Phase 155/156/157 convention — neither document is edited by the phase.

**`.planning/v1.33/CITATIONS-STALE.md` must not be removed or edited** — REMAP-04 makes it close-blocking and Phase 159 owns its removal.

---

### F-11 — An unrequiremented carry-forward that names Phase 158 by name

`tests/test_checker_convention.py` carries a drift that Phase 155 explicitly declined to close and handed to this phase:

- `:145` — `FLOOR = 7`; the tree ships **8** `scripts/check_*.py` `[VERIFIED: ls]`
- `:146` — `FIXTURE_FLOOR = 16`; the tree ships **30** `planted_*` fixtures `[VERIFIED: ls tests/fixtures | grep -c '^planted_']`
- `:76-78` — *"means `FLOOR`'s own 'the number actually shipped' wording is presently false by one, a carry-forward candidate for Phase 158 to close by raising `FLOOR` to 8 and `FIXTURE_FLOOR` to match the fixture count actually shipped"*
- `155-VERIFICATION.md:120` and `155-02-SUMMARY.md:35,124,235` all record it as *"a named, unremediated Phase 158 carry-forward"*

Both assertions are `>=`, so the suite passes regardless — the gate is *loose*, not broken. **This is in no LAND requirement.** The plan must either close it (a two-integer edit plus a comment repair) or re-carry it with a reason; silently ignoring a carry-forward that names this phase in three artifacts is the one outcome that should not happen in a landing phase.

---

### F-12 — A worktree measurement silently skips 32 legs of `pytest tests/`

Discovered by measurement, not inspection, and it invalidates a naive comparison of suite counts across locations:

| Location | `pytest tests/ -q` |
|----------|--------------------|
| `/workspaces/firestarter` (the canonical checkout) | **355 passed, 0 skipped** |
| `/tmp/158-research-probe/firestarter` (throwaway worktree, clean) | **323 passed, 32 skipped** |

`[VERIFIED: both run this session]`

**Mechanism:** `tests/meta_presence.py:77-97` computes `META_ROOT` as the **parent of the firmware repo root** and probes for a `.git` marker there; `requires_meta` skips when absent. In `/workspaces/firestarter` the parent is the meta repo (`.git` present); in `/tmp/<anything>/firestarter` it is not. `tests/test_flash_path_record_sync.py` is the only consumer, and it carries all 32 legs. There is a seam: `FIRESTARTER_META_ROOT`, read **at import time only** — `monkeypatch.setenv` cannot move it, so it must be set in the child process's environment.

**Consequence for the plan:** every prior phase's worktree measurement (including `157-cold-probe`) skipped these 32 legs, and none of them said so. Any plan that measures `pytest tests/` in a worktree must either set `FIRESTARTER_META_ROOT=/workspaces` or state that 32 cross-repo legs were skipped. **`pytest tests/` for gate purposes should be run from `/workspaces/firestarter` on a committed tree.**

---

## Architecture Patterns

### The measurement and gate pipeline this phase operates

```
                        ┌──────────────────────────────┐
  source edits ────────►│ firestarter working tree      │
  (LAND-05 jsmn.h,      │ @ gsd/v1.33-…  HEAD 785e644   │
   LAND-06 flash_5v)    └──────────────┬───────────────┘
                                       │
             rm -rf .pio/build/<env>   │   one `pio run -e <env>` per env
                                       ▼
                 ┌──────────────────────────────────────────┐
                 │ 3 cold build logs (uno, uno328pb, leo)   │──┐
                 │  "RAM: … used N"  "Flash: … used N"      │  │ transcribed
                 └──────────────┬───────────────────────────┘  │ (never computed)
                                │                              │
       pio test -e native       │                              ▼
       pio test -e native_… ────┤              ┌───────────────────────────────────┐
                                │              │ scripts/baseline/                 │
                                │              │   size_baseline.json  (LIVE)      │◄─┐
                                │              │   size_baseline_base01.json (FROZEN)│ │
                                │              └───────┬──────────┬────────────────┘ │
                                │                      │          │                  │
                     ┌──────────▼──────────┐   default │          │ --policy merge05  │
                     │ check_size_baseline │◄──────────┘          │ (one-sided, :697) │
                     │  .py                │◄──── LAND-02 ────────┘                  │
                     └──────┬──────────────┘                                          │
                            │ exit 0/1/2                                              │
              ┌─────────────┴───────────────┐                                          │
              │                             │                                          │
   LOCAL ONLY │                             │ subprocess, against FIXTURES             │
   (LAND-04)  │                             ▼                                          │
              │                 ┌────────────────────────────────┐                     │
              │                 │ tests/test_check_size_baseline │─── reads ───────────┘
              │                 │  .py  (14 legs)                │
              │                 └──────────────┬─────────────────┘
              │                                │  RUNS IN CI
              │                                ▼
              │              build.yml:161  `pytest tests/ -v`
              │              on: push branches ['**','!beta']
              ▼
   nothing in .github/ ever compares
   the real tree to the baseline
```

**The load-bearing insight the diagram encodes:** the *left* arm (measurement) is local-only, which is what LAND-04 records. The *right* arm (the checker's own gate suite reading the same baseline file) is automated. LAND-01 moves the file both arms read.

### Pattern 1 — Fixture severance, never re-anchoring

**What:** when the live baseline moves, add a **new** fixture generation and repoint the affected legs at it; leave the old generation in `tests/fixtures/` unmodified and unread.
**When to use:** every time `size_baseline.json`'s `avr_targets` or `native_envs` figures move.
**Why:** re-anchoring or repointing an existing family reddens legs that assert at sub-allowance deltas — *"the standing lesson this module has already paid for once"* (`tests/test_check_size_baseline.py:377-380`). Three prior generations exist: `*_fullflash*` → `*_v151*` → `*_v153*`.
**Exception this generation:** the two `captured_test_native*_summary.log` files are updated **in place**, not severed — the established convention for that pair (`:575-576`).

### Pattern 2 — Transcribe, never compute, a recorded figure

`size_baseline.json` `meta.generated_by`: *"The figures below are TRANSCRIBED, not computed, from the three cold-rebuild logs this quick task committed."* A figure typed from a `Flash:` line in a captured log is auditable; a figure arrived at by arithmetic on another record is not.

### Pattern 3 — One measurement, two consumers

The three cold build logs LAND-01 transcribes are the **same** logs that become `captured_build_v158_*.log` for LAND-02's severance. Capture once. A second capture invites two figures that disagree by a rebuild.

### Pattern 4 — A record that supersedes prose lives in the record, not in the prose

Phases 155, 156 and 157 all corrected ROADMAP/REQUIREMENTS figures **inside their own `*-figures.md`** with an explicit `supersedes:` frontmatter block, and edited neither source document. `157-before-figures.md:11-20` is the model. This phase has at least four such corrections (F-3, F-5, F-6, F-7).

### Anti-Patterns to Avoid

- **Producing LAND-01's re-record from `--rebuild`'s output.** `_rebuild_avr` (`:753`) uses `pio run -t clean`, not `rm -rf .pio/build/<env>`. Different recipe from the one the criterion mandates.
- **Re-recording the baseline and severing the fixtures in different commits.** The intermediate commit is CI-red (F-4).
- **Quoting a wall time as evidence.** D-04.
- **Asserting `sizeof(jsmntok_t)` in a native test without a target guard.** Native is 12 B, AVR is 6 B. `src/json_parser.c:164-275` carries the same warning verbatim for `field_desc_t`: *"NO ASSERTION ON sizeof(field_desc_t) MAY BE AUTHORED WITHOUT A TARGET GUARD"*.
- **Using a trace diff as LAND-06's oracle for the runtime claim.** Native trace stubs record no time; `delay()` is unstubbed. A trace diff can attest register-write *sequence*, never duration.
- **Conflating the four size-baseline legs with the four porcelain legs.** Different causes, different remedies (F-2 vs F-5).
- **Blurring algorithm 5's mask with algorithm 13's mask resolver**, or with the w27c512-write-slow-3x work (F-6).

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Deciding whether the size delta is admissible | a fresh comparison script or a hand-computed delta table | `scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json` | It already resolves all six band/exemption literals in one place (`_merge05_flash_allowance`, `_merge05_ram_allowance`) and prints the full decomposition. A hand-computed delta cannot produce the quotable PASS line LAND-02 needs |
| Proving `__udivmodsi4` is gone | reading the C and reasoning about codegen | `avr-nm --print-size` for the symbol range + `avr-objdump -d --start-address --stop-address` | Only the linked image witnesses a call site. gcc inlines `flash_5v_page_page_size` and `wait_for_page_write`, so source-level reasoning about the loop body is unreliable |
| Proving `sizeof(jsmntok_t)` is 6 | counting bytes by hand or trusting the host compiler | `avr-gcc -mmcu=atmega328p -Os` on a common-symbol probe + `avr-nm -S` | AVR uses 1-byte struct alignment and 16-bit `int`; host reasoning gives 12, not 6 |
| A page-boundary oracle for LAND-06 | a new recording harness | the existing `bus_recording_*` / `recorded_reg` / `recorded_data` helpers in `test/native/avr/test_val_5v_page/test_val_5v_page.cpp:258-277` | Already there, already proven, already in a CI-run env |
| A "warnings did not move" check | grepping build logs by hand | `python3 scripts/check_build_warnings.py --rebuild` | Reads the same `FIRESTARTER_SIZE_BASELINE` seam and applies the recorded `== 0` (AVR) / `<= total_watermark` (native) policy |
| A release-asset consistency check after the re-record | anything | `scripts/check_release_assets.py` | Already derives its required set from `avr_targets`' **keys**; the re-record cannot affect it, which is worth *verifying* rather than assuming |

**Key insight:** this phase's entire toolchain already exists and is already paired with its own pytest. The temptation to hand-roll comes from the checker's canonical invocation being red for an unrelated reason (F-3) — the fix for that is four JSON integers, not a new tool.

---

## Runtime State Inventory

This phase re-records a committed measurement file and may change firmware source. It is a re-record, so the question "what still holds the old value after every file is updated?" is live.

| Category | Items found | Action required |
|----------|-------------|-----------------|
| **Stored data** | **None.** No database, datastore or collection name is keyed on any figure this phase moves. Arduino EEPROM holds only `rurp_configuration_t` (R1/R2/rev), which neither LAND-05 nor LAND-06 reads or writes. `[VERIFIED: neither candidate touches `rurp_configuration_t` or `config_storage`]` | none |
| **Live service config** | **None.** No n8n workflow, Datadog service, Tailscale ACL or Cloudflare tunnel references a firmware size figure. `[VERIFIED: this phase's outputs are a JSON file, log fixtures and `.planning/` records]` | none |
| **OS-registered state** | **None.** No Task Scheduler task, pm2 process or systemd unit is involved. | none |
| **Secrets / env vars** | **`FIRESTARTER_SIZE_BASELINE`** — the seam three scripts read (`check_size_baseline.py:145`, `check_build_warnings.py:82`, `check_release_assets.py:34`). Not a secret and not set in any workflow; the default resolves to the committed file. **`FIRESTARTER_META_ROOT`** — read at import time by `tests/meta_presence.py:77`; governs the 32-leg skip (F-12). | none — but a plan that measures in a worktree must set `FIRESTARTER_META_ROOT`, or record the skip |
| **Build artefacts / installed packages** | **`.pio/build/<env>/` in the primary checkout is WARM** (last written 2026-08-23 22:13, containing the post-157 objects). LAND-01's recipe requires `rm -rf .pio/build/<env>` per env, so the stale warm tree is destroyed by the recipe itself. **No `.hex` is published and no package is installed by this phase.** The three ELFs under `.pio/build/` are the only artefacts carrying the pre-change image, and they are rebuilt. `[VERIFIED: ls -la .pio/build/uno]` | the recipe handles it; nothing to migrate |
| **Committed fixtures that cache the OLD figures** | **This is the one real item.** `tests/fixtures/captured_build_v153_{uno,uno328pb,leonardo}.log` (25548/25598/27630), `planted_size_baseline_flash_regression_v153.log` (28142), `captured_test_native{,_nodevtools}_summary.log` (172 cases) all hold pre-phase figures **and are read by live legs against the LIVE baseline**. This is exactly the "runtime state that still holds the old string" category — in committed-fixture form. | **code edit** (sever onto `*_v158*`) **plus data update in place** (the two native summaries) — both, in the same commit as the re-record |

**The canonical question, answered:** after every source file is edited and the baseline re-recorded, the only thing still holding the pre-change figures is the **committed fixture corpus** and the two `size_baseline*.json` files themselves. Nothing outside git caches a figure. **Nothing requires a data migration in the datastore sense**; the fixture severance is the migration.

---

## Common Pitfalls

### Pitfall 1 — Re-recording the baseline without severing the fixtures (turns CI red)
**What goes wrong:** `size_baseline.json` moves; four legs of `tests/test_check_size_baseline.py` fail; `pytest tests/ -v` at `build.yml:161` goes red on this branch.
**Why:** those legs read committed fixtures against the **live** baseline in byte-identity mode.
**How to avoid:** one commit containing the re-record, the three new captures, the new flash-regression plant, the two in-place native summary updates, and leg 3's updated assertions. Run `python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""` before committing.
**Warning signs:** `FAIL: uno: flash_used baseline=… observed=25548` in a test's stdout — the *fixture* is the observed side, so a fixture-vs-baseline mismatch reads exactly like a real regression.

### Pitfall 2 — Reading the pre-existing BASE-01 red as this phase's regression
**What goes wrong:** the canonical `--policy merge05 --rebuild` invocation exits 1 and a plan attributes it to its own edit.
**Why:** `compare_native` is strict-equality in both modes and BASE-01 is frozen at Phase 124's 141 cases against today's 184.
**How to avoid:** F-3. Expect **exactly two** failure lines, both `cases baseline=141 observed=184`, and **no** AVR flash or RAM line. Any third line is new.
**Warning signs:** more than two FAIL lines, or a FAIL line naming `flash_used` / `ram_used`.

### Pitfall 3 — Attributing a suite failure to your change on N=1 (D-04)
**What goes wrong:** a red run gets blamed on the edit; the edit gets reverted; the win is lost.
**Why:** measured 172/172 at ~35 s ×5, 171/172 once at 1:13, 158-cases-2-ERRORED once at 1:44 — plus this session's 22 s / 54 s / 61 s all at 184/184.
**How to avoid:** three pre-edit runs recorded; re-run every red; name the failing case, never "the suite".
**Warning signs:** a run over ~60 s; a case count that is *near* 184 rather than a clean deterministic failure.

### Pitfall 4 — Confusing the four porcelain legs with the four size-baseline legs
**What goes wrong:** an uncommitted edit reddens four *different* legs and a plan starts severing fixtures that were never the problem.
**Why:** `test_requirement_case_mapping_v131.py` (×2) and `test_trace_segment_exhaustiveness_v131.py` (×2) assert `git status --porcelain` is empty after their own planted mutation, so they fail for **any** dirty file.
**How to avoid:** commit before running `pytest tests/`. The assertion text names the dirty path (`assert ' M lib/jsmn/src/jsmn.h\n' == ''`) — read it.
**Warning signs:** the failure message contains a path you just edited.

### Pitfall 5 — Asserting `sizeof(jsmntok_t)` without a target guard
**What goes wrong:** a native test asserts 6 and fails, or asserts 12 and proves nothing about AVR.
**Why:** AVR `int` is 16-bit with 1-byte struct alignment (6 B); host `int` is 32-bit with 4-byte alignment (12 B).
**How to avoid:** the RAM saving is witnessed by the linker's `RAM: used N` line and by `avr-nm`, not by a native `sizeof`. `src/json_parser.c:164-275` carries this exact warning for a sibling struct.

### Pitfall 6 — Using `--rebuild` as the recording source for LAND-01
**What goes wrong:** the figures are transcribed from a `pio run -t clean` build, not the mandated `rm -rf .pio/build/<env>` build.
**Why:** `_rebuild_avr` at `scripts/check_size_baseline.py:753`.
**How to avoid:** capture the three logs explicitly, keep them, transcribe from them, and reuse them as the `*_v158*` Group 1 fixtures.

### Pitfall 7 — Measuring `pytest tests/` in a worktree and reporting the count as the suite
**What goes wrong:** 355 becomes 323 + 32 skipped and nobody notices 32 cross-repo legs never ran.
**Why:** F-12 — `META_ROOT` is the parent of the repo root.
**How to avoid:** run gate-purpose `pytest tests/` from `/workspaces/firestarter`, or export `FIRESTARTER_META_ROOT=/workspaces` in the child environment.

### Pitfall 8 — Treating the ARM half of LAND-05 as verified
**What goes wrong:** `lib/jsmn/src/jsmn.c` is compiled by `platform/py32f071/CMakeLists.txt:70` and gated by the loud `py32f071.yml` on every push — but no ARM toolchain exists on this machine.
**How to avoid:** install `arm-none-eabi-gcc` + `cmake` and build once, or state the ceiling explicitly in the record.

### Pitfall 9 — Letting the `native_envs` re-record drift from the actual final case count
**What goes wrong:** LAND-06's optional boundary test moves 184 → 185/186; the baseline records 184; the next `--rebuild` is red.
**How to avoid:** re-record **last**, after every code and test commit has landed, and re-measure rather than reuse this document's 184.

---

## Code Examples

### The cold recipe, exactly as the baseline file documents it
```bash
# Source: scripts/baseline/size_baseline.json meta.generated_by
cd /workspaces/firestarter
for e in uno uno328pb leonardo; do
  rm -rf ".pio/build/$e"
  pio run -e "$e" 2>&1 | tee "/tmp/gsd-158/cold-$e.log"
done
grep -E '^(RAM|Flash):' /tmp/gsd-158/cold-*.log   # transcribe these, never compute them
grep -c 'warning:' /tmp/gsd-158/cold-*.log        # AVR policy is == 0
```
Measured this session: **1.1–1.3 s per env**, flash `23090 / 23138 / 25234`, RAM `1562 / 1568 / 2003`, zero `warning:` lines.

### The canonical MERGE-05 invocation, and its one-sided PASS line
```bash
# Source: scripts/check_size_baseline.py:121-125 (the Usage block's own canonical form)
python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=/tmp/gsd-158/cold-uno.log \
  --avr-log uno328pb=/tmp/gsd-158/cold-uno328pb.log \
  --avr-log leonardo=/tmp/gsd-158/cold-leonardo.log
# exit 0
# PASS: uno(flash=23090/32768[-1734<=788=band64+exempt96+seam210+lock288+erase130],ram=1562/2048[-11<=2=seam2]), …
```
The negative deltas printed against positive allowances **are** the one-sidedness record.

### The one-sidedness, quoted from source
```bash
sed -n '697p;709p' scripts/check_size_baseline.py
#   697:    if flash_delta > allowance:
#   709:    if ram_delta > ram_tolerance:
```

### LAND-04's proof
```bash
grep -rn "check_size_baseline" .github/ ; echo "exit=$?"        # (no output) exit=1
grep -rn "scripts/check_" .github/workflows/*.yml | grep 'run:'
#   beta-build.yml:327:  run: python3 scripts/check_release_assets.py   <-- the only one
grep -n "pytest tests/" .github/workflows/build.yml               # :161  (runs the checker's OWN suite)
sed -n '16,34p' .github/workflows/build.yml                       # on: push: branches: ['**','!beta']
```

### LAND-05's narrowing
```c
/* lib/jsmn/src/jsmn.h — add near the top: */
#include <stdint.h>

/* lib/jsmn/src/jsmn.h:74-92 — replace: */
typedef struct jsmntok {
  uint8_t type;   /* was jsmntype_t: an enum, 16-bit int on AVR. Values 0,1,2,4,8. */
  uint8_t size;   /* was int. Max real value: an object's pair count (<=13) or an
                   * array's element count (<=19 from pinouts.json). */
  int start;      /* UNCHANGED and SIGNED — carries the -1 sentinel (jsmn.c:15,222,241,256,290,348) */
  int end;        /* UNCHANGED and SIGNED — same */
#ifdef JSMN_PARENT_LINKS
  int parent;
#endif
} jsmntok_t;
```
AVR `sizeof`: **8 → 6**. `static jsmntok_t tokens[64]` (`src/firestarter.cpp:54`): **512 → 384 B**. Measured whole-image: `−138 / −138 / −136 B` flash, `−128 B` RAM, 184/184 native on both envs.

### The `sizeof` oracle (reproducible in 5 seconds)
```bash
cat > /tmp/jt.c <<'EOF'
#include <stdint.h>
typedef enum { A=0,B=1,C=2,D=4,E=8 } t_t;
typedef struct { t_t type; int start; int end; int size; } old_t;
typedef struct { uint8_t type; uint8_t size; int start; int end; } new_t;
char o[sizeof(old_t)]; char n[sizeof(new_t)];
int main(void){ return 0; }
EOF
~/.platformio/packages/toolchain-atmelavr/bin/avr-gcc -mmcu=atmega328p -Os -c /tmp/jt.c -o /tmp/jt.o
~/.platformio/packages/toolchain-atmelavr/bin/avr-nm -S /tmp/jt.o | grep -E ' [on] $| [on]$'
#   00000006 00000006 C n
#   00000008 00000008 C o
```

### LAND-06's mask, and the two-call proof
```c
/* src/proms/flash_5v_page.cpp:106 — add: */
    const uint32_t page_mask = page_size - 1;   /* :27-31 returns only 64/128/256 */
/* :116 */  bool is_page_start   = (address & page_mask) == 0;
/* :124 */  bool reached_page_end = ((address + 1) & page_mask) == 0;
```
```bash
NM=~/.platformio/packages/toolchain-atmelavr/bin/avr-nm
OD=~/.platformio/packages/toolchain-atmelavr/bin/avr-objdump
read A S _ _ <<<"$($NM --print-size .pio/build/uno/firestarter_uno.elf | grep write_executeP)"
$OD -d --start-address=0x$A --stop-address=$(printf '0x%x' $((0x$A + 0x$S))) \
    .pio/build/uno/firestarter_uno.elf | grep -c __udivmodsi4
# 2  before the mask   /   0  after
$OD -d .pio/build/uno/firestarter_uno.elf | grep -c 'call.*__udivmodsi4'
# 11 before           /   9  after   -- the 68 B helper stays linked either way
```

### LAND-07's arithmetic, reproducibly
```python
# Source: written and run for this research. jsmn's own counting rule --
# one token per '{', per '[', per string, per primitive (lib/jsmn/src/jsmn.c:170-355).
def jsmn_count(js):
    n = i = 0
    while i < len(js):
        c = js[i]
        if c in '{[':          n += 1; i += 1
        elif c == '"':
            n += 1; i += 1
            while js[i] != '"': i += 2 if js[i] == '\\' else 1
            i += 1
        elif c in ' \t\r\n:,]}': i += 1
        else:
            n += 1
            while i < len(js) and js[i] not in ' \t\r\n,]}': i += 1
    return n
# root + 12 scalar pairs + bus-config{bus[18], rw-pin, vpp-pin}  (DIP32_27C020)
#   -> 51 tokens, the maximum over every real pin map
# sweeping the whole chip DB through convert_to_programmer() -> 50 (W29C020 family)
# field-wise-maximum synthetic (19 bus pins AND static-high AND rw-pin AND vpp-pin) -> 55
# NUMBER_JSNM_TOKENS = 64  (include/json_parser.h:17)
```

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|--------------|------------------|--------------|----------------------|
| `pio run -t clean -e <env>` as the cold recipe | `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` | quick task 260820-a7w, 2026-08-20 | LAND-01 mandates the newer form; `--rebuild` still uses the older one (`:753`) |
| BASE-01 asserted immutable in all respects | **axis split**: growth axis (`flash_used`/`ram_used`) frozen; board-identity axis (`flash_total`) licensed to move with cause | quick task 260820-a7w; machine-checked at `tests/test_check_size_baseline.py:1106-1158` | The doctrinal basis for LAND-03's "fix" branch |
| `build.yml` triggered on `main` only | `on: push: branches: ['**', '!beta']` | documented in `build.yml:4-14` | **`pytest tests/ -v` now runs on this milestone branch.** Two in-tree docstrings still assert the old behaviour (F-4) |
| Growth admitted by widening a band | growth admitted by a **named, SHA-attributed exemption** stacked on an unchanged band | v1.31 Phase 145 onward; four now stacked | A *reduction* needs no exemption at all (D-03) — the first in the project's history |
| `%` on a runtime page size | `& (page_size - 1)` with a validating resolver | Phase 149/153, algorithm 13 only (`src/proms/eeprom_28c.cpp:628`) | LAND-06 would extend the *idiom* to algorithm 5, without the resolver (which would be dead code there) |

**Superseded figures a reader must not quote:**
- `size_baseline.json`'s `avr_targets` (25548 / 25598 / 27630) — stale since Phase 155.
- `size_baseline.json`'s `native_envs.cases = 172` — stale since Phase 157 plan 04.
- ROADMAP §Phase 158 criterion 3 and REQUIREMENTS LAND-03's `observed=172` — **observed is 184**.
- REQUIREMENTS LAND-05's `+30 B flash` — **measured `−138 / −138 / −136`**.
- REQUIREMENTS LAND-06's flat `+22 B` — **measured `+22 / +24 / +22`**.
- REQUIREMENTS LAND-07's `57 tokens` / `7 tokens of headroom` — **51 / 13** against the real corpus.
- `size_baseline.json` `meta.consumed_by`'s "two consumers" — **three**.
- `size_baseline.json` `envs_agree_note`'s `{cases: 151}` — already flagged stale in the same file.
- `tests/test_check_size_baseline.py:459` and `tests/meta_presence.py:56-58` on CI coverage — both false.
- `157-after-figures.md` §2's Caterina headroom `3438 B` — correct at 785e644, moves if LAND-05/06 land (see below).

**Leonardo Caterina headroom against the 28672 B cliff, per outcome** (all measured this session):

| Outcome | `leonardo` flash | Headroom |
|---------|------------------|----------|
| no further change | 25234 | **3438 B** |
| LAND-05 only | 25098 | **3574 B** |
| LAND-06 only | 25256 | **3416 B** |
| both | 25120 | **3552 B** |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The ARM (`py32f071`) build compiles cleanly with the narrowed `jsmntok_t`. Reasoned from the host `sizeof` measurement (12 B, no packing issue) and `<stdint.h>` availability in newlib — **not built** (no `arm-none-eabi-gcc` on this machine). | F-5 | The loud ARM gate goes red on the next push. Mitigation: install the toolchain, or record the ceiling |
| A2 | `size` never exceeds 255 for any real command, so `uint8_t size` cannot truncate. Reasoned from the maxima in F-7 (largest object 13 pairs, largest array 19 elements) — no adversarial-input test was run. | F-5 | A pathological command could truncate `size` and mis-parse. A malformed command already fails; the practical exposure is a future host emitting a >255-element array, which `ADDRESS_LINES_SIZE` already bounds |
| A3 | `type` never exceeds 255. From `jsmntype_t`'s five enumerators (0,1,2,4,8) at `jsmn.h:51-57`. Structurally certain unless jsmn is upgraded. | F-5 | none in practice |
| A4 | The 2-token gap between my derived 55 and REQUIREMENTS' 57 originates in counting `state` alongside `cmd`. **Unverified** — the scoping session's own derivation was not located. | F-7 | Only the *explanation* is at risk; the derived bounds stand on their own |
| A5 | No `.planning/` record outside `.planning/v1.33/` needs to change for LAND-02/04/07/08. Based on the Phase 155/156/157 convention, not on an exhaustive scan of `.planning/`. | F-10 | A record lands in the wrong place; cheap to move |
| A6 | The `*_v153*` fixture family should be **retired in place and kept**, not deleted. Following the stated disposition of the two prior severances. | F-2 | none — the alternative (deletion) is what the precedent explicitly rejects |

---

## Open Questions (ALL RESOLVED)

**RESOLVED 2026-08-24, before planning.** All five were decided by the orchestrator (Q1 by the
operator; Q2-Q5 on precedent and cost basis) and carried into the plans as locked decisions
OD-1, OD-3, OD-4, OD-5 and OD-7. Each question's resolution is stated inline below. No question
in this section reaches execution unresolved.

1. **RESOLVED — Does LAND-06 get taken?** → **DECLINED by the operator.** No mask rewrite;
   `src/proms/flash_5v_page.cpp` is not edited and no `test_val_5v_page` cases are added. The
   criterion is discharged by recording the `+22 / +24 / +22 B` measurement, the two confirmed
   `call __udivmodsi4` sites and the zero-coverage gap as the stated reason. Native case count
   does not move for LAND-06's sake. Planned as `158-03`.
   - What we know: `+22 / +24 / +22 B` flash, 0 B RAM, two `__udivmodsi4` calls per byte removed, the in-tree mask idiom already exists on algorithm 13, and the boundary path has **zero** behavioural native coverage.
   - What's unclear: the runtime win — unquantifiable in this milestone by D-02.
   - Recommendation: **decline, and record the measurement plus the coverage gap as the reason** — a shrink-only milestone paying 22–24 B for an unmeasurable benefit on an untested path is the weaker trade. If the operator wants it, take it **with** the two-case boundary test from F-6 and accept the `184 → 186` case-count move.

2. **RESOLVED — Fix or carry LAND-03?** → **FIX.** Four integers, measured to redden zero legs; the axis-split precedent is machine-checked at `tests/test_check_size_baseline.py:1106`. Planned as `158-05`.
   - What we know: fixing is 4 integers and reddens zero legs (measured); the axis-split precedent exists and is machine-checked.
   - What's unclear: whether the operator reads BASE-01's `native_envs` as part of the frozen anchor.
   - Recommendation: **fix**, recording the axis split explicitly. Carry is still viable and LAND-02 is green either way.

3. **RESOLVED — Are the two false CI-coverage docstrings corrected here?** → **YES, corrected.** Comment-only edits at `tests/test_check_size_baseline.py:459` and `tests/meta_presence.py:56-58`; no assertion changes. Same claim LAND-04 records. Planned as `158-05`.
   - What we know: both are false; both are about exactly the automation boundary LAND-04 exists to state honestly.
   - What's unclear: whether editing test docstrings is in scope for a landing phase.
   - Recommendation: correct them — a one-hunk comment edit in each, no assertion change, and it is the same claim LAND-04 records.

4. **RESOLVED — Is the `test_checker_convention.py` FLOOR carry-forward closed?** → **CLOSED.** `FLOOR` 7 → 8 and `FIXTURE_FLOOR` 16 → the count shipped at this phase's final commit (re-counted, not transcribed), plus the `:76-78` comment repair. Three artifacts named Phase 158 as its owner. In no LAND requirement by design. Planned as `158-05`.
   - What we know: three artifacts name Phase 158 as its owner; it is in no LAND requirement; the fix is two integers plus a comment.
   - Recommendation: **close it**, or re-carry it with a named reason and a new owner. Do not leave it silent.

5. **RESOLVED — Does the ARM build get verified locally?** → **ATTEMPT ONCE, RECORD THE CEILING ON FAILURE.** The toolchain is known installable in this devcontainer (it needs two newlib packages CI omits). If the install fails, the ceiling is recorded in `158-after-figures.md` and `py32f071.yml` witnesses it at push time. ARM coverage is never claimed unless it was built. Planned as `158-02`.
   - Recommendation: attempt the toolchain install once; if it fails, record the ceiling in `158-after-figures.md` rather than implying ARM coverage.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `pio` (PlatformIO Core) | LAND-01 cold builds; native suites | ✓ | 6.1.19 | — |
| `avr-gcc` / `avr-nm` / `avr-objdump` | LAND-05 `sizeof`; LAND-06 call-site proof | ✓ | 7.3.0 (`~/.platformio/packages/toolchain-atmelavr/bin`, **not on `$PATH`** — use the full path) | — |
| `python3` | all `scripts/check_*.py` | ✓ | 3.12 (system) | ⚠ `pio`'s bundled python has no pytest — always use system `python3` |
| `pytest` | `tests/` gate suite | ✓ | 9.1.1 | — |
| `git worktree` | throwaway measurement probes | ✓ | — | ⚠ a `/tmp` worktree skips 32 legs of `pytest tests/` (F-12) |
| `arm-none-eabi-gcc` | LAND-05 ARM verification | **✗** | — | the `py32f071.yml` workflow at push time, **with the ceiling recorded** |
| `cmake` | LAND-05 ARM verification | **✗** | — | same |
| Physical RURP board | nothing | n/a | — | **D-02 forbids a bench criterion.** Not required by any criterion |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** the ARM toolchain (fallback: CI at push time, ceiling recorded). See Open Question 5.

---

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json` → treated as **enabled**.

### Test Framework
| Property | Value |
|----------|-------|
| **Framework** | **Unity** via PlatformIO `test_framework = unity`, plus **ArduinoFake 0.4.0** for Arduino stubs; **pytest 9.1.1** for the `scripts/` gate suite |
| **Config file** | `firestarter/platformio.ini` — `[env:native]` and `[env:native_nodevtools]`, each with a 17-entry `test_filter` and a matching `-I` list that **must stay in lockstep** |
| **Quick run command** | `pio test -e native -f "*test_val_5v_page*"` (LAND-06's suite) · `python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""` (LAND-01/02's suite, 0.8 s) |
| **Full suite command** | `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q -o addopts=""` |
| **Build gate** | `for e in uno uno328pb leonardo; do rm -rf .pio/build/$e; pio run -e $e; done` — AVR `warning:` policy is `== 0` |
| **Size gates** | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log …` (green, F-2) · `python3 scripts/check_build_warnings.py --rebuild` · `python3 scripts/check_no_heap_or_64bit_symbols.py` — **all three in NO CI workflow** |
| **CI legs, exhaustively, on this branch** | `pio test -e native` (`build.yml:142`) · `pio test -e native_nodevtools` (`:155`) · `pytest tests/ -v` (`:161`) · `pio run` (`:193`) · `py32f071.yml` ARM build. **Nothing else.** |

**Measured baseline at `785e644`, clean tree, executed this session:**

| Leg | Baseline |
|-----|----------|
| `pio test -e native` | **184 cases / 17 suites / 184 succeeded** |
| `pio test -e native_nodevtools` | **184 / 17 / 184** |
| `python3 -m pytest tests/ -q` (from `/workspaces/firestarter`) | **355 passed, 0 failed, 0 skipped** (11.5 s) |
| `python3 -m pytest tests/test_check_size_baseline.py -q` | **14 passed** (0.76 s) |
| Cold `pio run` | flash **23090 / 23138 / 25234**, RAM **1562 / 1568 / 2003**, **0** warnings |
| `size_baseline.json` `native.cases` | **172** (stale) |
| `size_baseline_base01.json` `native.cases` | **141** (frozen at Phase 124 — the pre-existing RED) |

### Phase Requirements → Test Map

| Req | Behaviour | Test type | Automated command | File exists? |
|-----|-----------|-----------|-------------------|-------------|
| **LAND-01** | the re-recorded file matches a cold measurement of the committed tree | build + gate | `for e in uno uno328pb leonardo; do rm -rf .pio/build/$e; pio run -e $e; done` then `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` (default mode = byte identity) | ✅ existing — **local only** |
| **LAND-01** | BASE-01's growth axis is unmoved | source contract | `python3 -m pytest tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption -q -o addopts=""` | ✅ existing (`:1108`) — **runs in CI** |
| **LAND-02** | the policy run is green and prints negative deltas | gate | the canonical `--policy merge05 --avr-log ×3` invocation, exit 0 | ✅ existing — **local only** |
| **LAND-02** | the severance is complete — no leg reads a stale figure | gate | `python3 -m pytest tests/test_check_size_baseline.py tests/test_check_build_warnings.py -q -o addopts=""` → **24 passed** | ✅ existing — **runs in CI**. This is the leg that catches an incomplete severance |
| **LAND-02** | the tripwire is still armed above the (unchanged) allowance | planted negative | the three surviving `planted_size_baseline_policy_*_v153.log` legs (`:1202`, `:1257`, `:1298`) — **measured to stay green**, so they need no re-plant; assert that fact rather than re-planting | ✅ existing |
| **LAND-03** | the mismatch is resolved or reproduced verbatim | gate | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` → exit 0 if fixed; **exactly two** `cases baseline=141 observed=184` lines if carried | ✅ existing — **local only** |
| **LAND-04** | the grep claim holds | record + command | `grep -rn "check_size_baseline" .github/; echo $?` → `1`; plus `grep -n "pytest tests/" .github/workflows/build.yml` → `:161` for the second clause | ✅ existing |
| **LAND-05** | narrowing does not change parse behaviour | unit | `pio test -e native -f "*test_read_timing*"` (the only suite allocating the real 64-token budget) then the full `pio test -e native && pio test -e native_nodevtools` → **184/184 both** | ✅ existing (`test_read_timing_params.cpp:84`) — **runs in CI** |
| **LAND-05** | the RAM saving is real | build | `pio run -e uno` `RAM: used 1434` (from 1562) — the linker is the witness | ✅ existing |
| **LAND-05** | `start`/`end` remain signed | source contract | ❌ **Wave 0 candidate** — a `grep`/AST leg asserting `int start;` and `int end;` are still `int` in `jsmn.h`, so a future "tidy-up" to `uint16_t` cannot silently break the twelve `-1` sentinels | ❌ **Wave 0** |
| **LAND-06** *(only if taken)* | page-start SDP count and page-end poll count are correct across a real boundary | unit | ❌ `pio test -e native -f "*test_val_5v_page*"` with **new** cases; `mem_size=32768` → `page_size=64`, `data_size=128`, expect exactly 2 page starts and 2 page ends; proven RED against a deliberately wrong mask first | ❌ **Wave 0** |
| **LAND-06** *(either way)* | the measurement is cited | build + disassembly | `pio run -e uno` flash delta + `avr-objdump` call-site count inside `flash_5v_page_write_execute` | ✅ existing tooling |
| **LAND-07** | the arithmetic is reproducible by a reader | record | the `jsmn_count` snippet in Code Examples, run against `pinouts.json` | ✅ (script inlined in the record; no committed test needed for a record-only criterion) |
| **LAND-08** | the flakiness record carries its evidence | record | three timed `pio test -e native` runs on the committed tree, case count + wall time each | ✅ existing |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""` (0.8 s) for any baseline/fixture task; `pio test -e native -f "*<suite>*"` for any source task.
- **Per wave merge:** `pio run` all three cold + `pio test -e native` + `pio test -e native_nodevtools` + `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter`.
- **Phase gate:** the full eight-leg ledger the sibling phases used — cold `pio run` ×3, `pio test -e native`, `pio test -e native_nodevtools`, `pytest tests/`, `check_build_warnings.py --rebuild`, `check_no_heap_or_64bit_symbols.py`, `check_size_baseline.py --policy merge05` (both the `--avr-log` and `--rebuild` forms, with their expected shapes stated in advance), `check_size_baseline.py` default mode (must now be **green**, since LAND-01 re-records it), and the host suite from `firestarter_app`.

**One gate flips polarity in this phase and the plan must say so up front:** `check_size_baseline.py` **default mode** has been RED since Phase 155 (`157-after-figures.md` leg 7 records six failing lines). After LAND-01 it must be **GREEN**. That flip is LAND-01's own discharge evidence.

### Wave 0 Gaps
- [ ] A source-contract leg pinning `int start;` / `int end;` in `lib/jsmn/src/jsmn.h` — covers **LAND-05**'s signedness clause. Cheap; a `grep`-style assertion in a new or existing `tests/*.py`. **Note:** adding a `tests/` file does not move native case counts, so it does not interact with LAND-01.
- [ ] *(Conditional on LAND-06 being taken)* page-boundary cases in `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` with a counting variant of `recording_contains_sdp_signature` — covers **LAND-06**. **Moves the native case count `184 → 185/186`**, which must land before LAND-01's re-record.
- [ ] `captured_build_v158_{uno,uno328pb,leonardo}.log` + `planted_size_baseline_flash_regression_v158.log` — the `*_v158*` family, covers **LAND-02**.

*(No framework install is needed — Unity, ArduinoFake and pytest are all present.)*

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as enabled. This phase changes no authentication, session, access-control, cryptographic or network surface, but two ASVS categories are genuinely live and one of them is the reason a clause of LAND-05 exists at all.

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---------------|---------|-----------------|
| V2 Authentication | no | No principal exists; the serial link is physical-access-only |
| V3 Session Management | no | The three-phase INIT/MAIN/END state machine is unchanged by every candidate |
| V4 Access Control | no | No permission model; `DEV_TOOLS` gating is untouched |
| **V5 Input Validation** | **yes** | The JSON command decoder is the firmware's **only** untrusted-input surface. Two candidates touch it: **LAND-05** narrows the token type the decoder writes into, and **LAND-07** reasons about the token budget whose overflow is the decoder's fail-closed path (`JSMN_ERROR_NOMEM`). Existing controls: Phase 157's `store_field` saturation/mask (DECODE-05, `src/json_parser.c`), the `READ_TIMING_MAX_US` clamp column, `eeprom28c_page_mask`'s power-of-two + range validation, and `ADDRESS_LINES_SIZE` bounding on the bus array |
| V6 Cryptography | no | None involved. Nothing is hand-rolled |
| **V14 Configuration** (build/supply chain) | **yes** | LAND-05 edits a **vendored** library (`lib/jsmn/`) that is compiled by two architectures. No new dependency is added; no package is installed. The supply-chain control is that the library is in-tree, single-commit, and already locally modified — there is no upstream drift check to break |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard mitigation | Status under this phase |
|---------|--------|---------------------|-------------------------|
| Out-of-range wire value truncating into a valid dispatch target | Tampering | saturate-for-ordinals / mask-for-bitmasks in `store_field` | **Discharged by Phase 157 (DECODE-05)**; unaffected by any LAND candidate |
| Token-budget exhaustion on a crafted or oversized command | Denial of Service | `jsmn_alloc_token` returns `NULL` → `JSMN_ERROR_NOMEM` → whole command rejected (fail-closed) | **Unchanged.** LAND-07's record must keep this framing: the headroom is a fail-closed safety margin, not slack |
| Field truncation from narrowing a decoder type | Tampering | keep every field wide enough for its real maximum; keep sentinel-bearing fields signed | **LAND-05's constraint**, and why `start`/`end` stay `int`. `type` (max 8) and `size` (max 19) are proven to fit `uint8_t` (F-7). **A1/A2 in the Assumptions Log are the residual** |
| Off-by-one in a boundary predicate on a write path | Tampering / Integrity | `x % 2^n == x & (2^n - 1)` for unsigned `x`; page size proven power-of-two at its three literal returns | **LAND-06's correctness argument.** The residual risk is not the identity (it is exact) but the **absence of any test** that would catch a botched edit (F-6) — which is the strongest reason to pair the change with the boundary test or decline it |
| A gate that passes vacuously after a refactor | Repudiation | every planted negative observed RED before being trusted | House rule. Applies to both Wave 0 legs |
| A recorded figure laundered rather than measured | Repudiation | transcribe from a captured log; never compute; keep the log | Pattern 2. Applies to LAND-01 and to the `*_v158*` captures |

**Nothing in this phase touches VPP/VPE control, high-voltage routing, or the erase policy.** `flash_5v_page_write_execute` is a 5 V path and `test_5v_page_write_execute_no_vpp` (`test_val_5v_page.cpp:297`) already pins that it writes no VPP control bit — **that leg must stay green through any LAND-06 edit**, and it is the one existing safety assertion over the function being modified.

---

## Sources

### Primary (HIGH confidence — built, run or read this session)
- `firestarter` @ `785e644` (branch `gsd/v1.33-source-hygiene-firmware-size-reduction`) — clean tree, verified before and after every probe
- Cold `pio run -e {uno,uno328pb,leonardo}` ×4 configurations (baseline, LAND-05, LAND-06, both) in a throwaway `git worktree add --detach`, removed and pruned
- `pio test -e native` ×3, `pio test -e native_nodevtools` ×1
- `avr-gcc 7.3.0` / `avr-nm` / `avr-objdump` — `sizeof` oracle and `__udivmodsi4` call-site counts on all three ELFs
- `python3 -m pytest tests/…` — 14-leg checker suite, full 355-leg suite, and the simulated re-record that enumerated the four red legs
- `scripts/check_size_baseline.py` (961 lines, read in full), `scripts/baseline/size_baseline.json`, `scripts/baseline/size_baseline_base01.json`
- `.github/workflows/build.yml`, `beta-build.yml`, `py32f071.yml`
- `src/proms/flash_5v_page.cpp`, `src/proms/eeprom_28c.cpp`, `src/json_parser.c`, `include/json_parser.h`, `src/firestarter.cpp`, `lib/jsmn/src/jsmn.{h,c}`
- `tests/test_check_size_baseline.py` (1400+ lines incl. the four-generation severance record), `tests/test_checker_convention.py`, `tests/meta_presence.py`
- `firestarter_app/firestarter/{database,eprom_operations,serial_comm,chip_resolver}.py` and `data/pinouts.json` — read only, for LAND-07's arithmetic

### Secondary (HIGH confidence — project records, cross-checked against the tree)
- `.planning/ROADMAP.md` §v1.33 and §Phase 158 (`:409-431`)
- `.planning/REQUIREMENTS.md` §5 LAND-01…08, §Traceability, §Out of Scope
- `.planning/v1.33/157-after-figures.md` §2 (cold ledger), §10 (eight-leg gate ledger), §11 (one-sidedness), §16 (handoffs to 158)
- `.planning/v1.33/157-before-figures.md` (`:1-21` frontmatter template; `:240-250` local-run obligation + flakiness)
- `.planning/v1.33/156-before-figures.md` (`:353` LAND-04 confirmation)
- `.planning/phases/155-*/155-RESEARCH.md` (`:34` D-04; `:843-860` Pitfalls 5/6/7), `155-VERIFICATION.md:120`, `155-02-SUMMARY.md`
- `.planning/phases/156-*/156-07-SUMMARY.md:110`, `.planning/phases/157-*/157-VALIDATION.md`
- `.planning/STATE.md` (`:65`, `:2422`, `:2457`, `:2460`, `:2828`)

### Tertiary (LOW confidence — noted, not relied on)
- `.planning/graphs/graph.json` — queried per protocol; **stale (1286 h old, 1806 commits behind) and returned zero nodes** for every term tried. Contributed nothing; no claim in this document rests on it.
- No external web source was consulted. Nothing in this phase depends on ecosystem knowledge; every question was answerable from the tree by measurement, which is why the research-plan seam was not exercised for web providers.

---

## Metadata

**Confidence breakdown:**
- **Standard stack:** HIGH — no new dependency; every tool's presence and version verified by invocation.
- **LAND-01 recipe and figures:** HIGH — cold-measured this session on all three targets, byte-identical to an independent prior record.
- **LAND-02 green run and the four red legs:** HIGH — both reproduced by execution, not inference; the red-leg list is an observed pytest output, not a prediction.
- **LAND-03:** HIGH on the facts (141 vs 184, the suppression mechanism, zero legs reddened by the fix); the *choice* is the plan's.
- **LAND-04:** HIGH — grep-proven, and the second clause (CI runs the checker's own suite) verified from the workflow triggers and step lines.
- **LAND-05:** HIGH on size, RAM, `sizeof` and both native suites; **MEDIUM on the ARM half** (A1 — reasoned, not built).
- **LAND-06:** HIGH on the measurement, the call-site proof and the coverage gap; the runtime half is **unmeasurable in this milestone by D-02**, stated rather than estimated.
- **LAND-07:** HIGH on the three derived bounds (computed from `pinouts.json` and the real chip DB); **the criterion's own 57/7 is not reproducible** and the discrepancy's origin is MEDIUM (A4).
- **LAND-08:** HIGH — three new same-tree data points measured, extending an existing record.
- **Architecture / patterns / pitfalls:** HIGH — every pattern is quoted from an in-tree docstring or a prior phase record, and every pitfall was either observed this session or is recorded in a sibling phase's artifacts.

**Research date:** 2026-08-24
**Measured at:** `firestarter` `785e644bacbe128de813407f0e6e357c71164836`, clean tree, verified clean afterwards (`git status --porcelain` empty; `git worktree list` matched its pre-probe output)
**Valid until:** **the next commit to `firestarter`.** Every flash/RAM figure, every native case count, and the four-red-leg list are position-dependent. Re-measure before quoting; do not carry these numbers forward past a code change.
