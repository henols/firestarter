# Phase 185: Records and Checks That Are Current — Research

**Researched:** 2026-09-11
**Domain:** In-repo record hygiene — firmware size-baseline re-record by fixture severance, docstring
citation repair, dead-symbol removal across a three-repo tree, CI workflow retirement, shell-script
tautology repair
**Confidence:** HIGH (every load-bearing claim below was read from the live file or executed in this
session; the three predicted byte figures are explicitly marked as predictions to falsify, not facts)

---

## Summary

This phase touches no behaviour. Everything in it is a record that has drifted away from the tree it
describes, plus one shell verification that has never been capable of failing. CONTEXT.md already
carries the measurements (51 `_off_tty()` sites, the 8-run CI history, `_AT28C_DIP24_NAMES` at
`build_db.py:538`, the D-03 byte/sha table, the six orphaned fixtures); this research does not
re-derive them. It answers the five open mechanical questions the orchestrator named, and it found
**four things CONTEXT.md did not have** — each of which would have cost the executor a failed run:

1. **The shrink deltas do not apply to the live baseline.** Phase 183 measured −234 / −238 / −284 B
   against `183-01`'s **pre-deletion** figures (22968 / 23016 / 25114), *not* against
   `size_baseline.json`'s live figures (22952 / 23000 / 25098). The live baseline was already
   **+16 B stale on all three targets** before Phase 183 began. Subtracting the shrink from the live
   baseline yields 22718 / 22762 / 24814 — **wrong by 16 B on every target**. The correct post-change
   figures are **22734 / 22778 / 24830**, which is what 183-05's own `FAIL:` transcript shows as
   `observed=`.
2. **`--rebuild` writes nothing.** It captures `pio` output in memory and compares. It produces
   neither the baseline JSON nor any fixture log. The four fixture logs are a separate, manual
   capture, and D-11's "same cold rebuild" discipline is therefore an *ordering* obligation on the
   executor, not something the tool enforces.
3. **A fifth `_is_interactive` patch site exists** that CONTEXT.md's D-06 does not name:
   `test_non_uv_part_is_still_written_in_full_without_a_prompt` (`test_dev_test_cmd.py:871`) also
   patches `_is_interactive`, and its docstring claims *"TTY or not"*. And
   `tools/check_devtest_orchestrator.py` names `_is_interactive` at **line 66** (module docstring
   prose) as well as at line 163 — D-07.1 names only 163.
4. **`catalog-sync-check.yml` is the meta-repo's only workflow.** Deleting it leaves
   `.github/workflows/` empty and the meta repo with zero CI. D-03's note should say so plainly.

**Primary recommendation:** Sequence the firmware work as *capture → transcribe → sever → prove*, in
that order, with the AVR logs and the two native logs taken from one uninterrupted cold pass, and
`--rebuild` run **last** as criterion 1's independent confirmation (it is a second full cold build
and will take ~10-15 min — longer than a single 600 s tool call, so it must be backgrounded). Run the
app work as a parallel wave; it is file-disjoint and needs only the py3.11 venv.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** `.github/workflows/catalog-sync-check.yml` is RETIRED OUTRIGHT — the file is deleted.
  Operator decision, taken against the orchestrator's recommendation. Grounds, in the operator's own
  terms: the catalog *"has no value to the main branch and shall not be executed by the CI — it's a
  tool that is used when a new message is created while developing and must be generated there and
  then. If it's not executed before fw is committed the fw will not compile."*
- **D-02:** CLAIM-08 and ROADMAP criterion 5 are AMENDED in this phase, with the reason on the
  record. Amended form: *the check is retired, and the cause of its standing failure is recorded.*
  Do NOT satisfy the original wording by some other route.
- **D-03:** A `.planning/notes/` verdict document carries CLAIM-08's record, carrying all five of:
  (1) the cause; (2) why the 2026-08-18 fix did not fix it; (3) that the workflow's own comment is
  now false; (4) that a naive `beta` fallback would not have worked either; (5) the residual gap,
  named explicitly.
- **D-04:** No successor guard and no backlog item are filed — deliberate, not an oversight. A
  planner or executor must NOT file a "cross-repo catalog identity" guard item.
- **D-05:** `_off_tty()` is deleted and all 51 call sites are unwrapped. Behaviour-neutral; the suite
  passing unchanged is the proof.
- **D-06:** The two `..._on_a_tty` tests are renamed and the redundant pair merged.
- **D-07:** `_is_interactive` is deleted, and its three dependents are carried deliberately:
  (1) remove `"_is_interactive"` from `_HANDLER_FUNCTION_NAMES`
  (`tools/check_devtest_orchestrator.py:163`); (2) repair `test_check_devtest_orchestrator.py:585`'s
  subset-vs-equality rationale; (3) update `test_dev_test_cmd.py`'s module docstring.
- **D-08:** A new phase-numbered fixture family, `captured_build_v185_{uno,uno328pb,leonardo}.log`
  plus `planted_size_baseline_flash_regression_v185.log`. `captured_build_v158_*` left
  byte-unchanged.
- **D-09:** The two native summary fixtures are updated IN PLACE, not severed.
- **D-10:** `size_baseline_base01.json` is NOT re-anchored, and the `merge05_*` policy fixtures are
  NOT touched.
- **D-11:** The baseline JSON and the fixture logs must come from the SAME cold rebuild. Two failure
  modes to design against: re-recording flash but not native; transcribing the figures in
  `REQUIREMENTS.md`.
- **D-12:** The six orphaned build fixtures are deleted (`captured_build_fullflash_{uno,uno328pb}`,
  `captured_build_v132_{uno,uno328pb}`, `captured_build_v151_{uno,uno328pb}`).
- **D-13:** The CLAIM-06 citation is replaced with the symbol-and-scope form the same file already
  uses correctly at line 129. A planner must not transcribe either 594 or 545.
- **D-14:** `tools/catalog/sync_to_subrepos.sh`'s two self-comparing verifications (lines 84-86 and
  97-99) are repaired in this phase, copying the shape at lines 65-70, with an `else` and a non-zero
  exit, and **proven by mutating a committed artifact, watching it go red, then restoring**.

### Claude's Discretion

The operator answered "All sounds good" to four recommendations and delegated six mechanical calls to
precedent. A planner may revisit these on evidence: **D-05, D-06** (the `_off_tty` disposition and the
test rename/merge); **D-12** (deleting the six orphans); **D-14** (folding the sync-script todo);
**D-08, D-09, D-10, D-13** and **D-03's location**.

The decisions the operator made directly, which must NOT be revisited without asking them:
**D-01** (retire the workflow outright) and **D-04** (name the gap, file nothing).

### Deferred Ideas (OUT OF SCOPE)

- **A successor guard for cross-repo vendored-catalog identity.** The operator explicitly declined to
  file this (D-04). Recorded as a rejected option, **not** a backlog candidate. Do not file it.
- **`test_configure_memory.cpp:9` cites `build_db.py:89`** where `KNOWN_PROTOCOLS` lives at 137.
  CLAIM-06's defect class, firmware repo, outside this phase's requirements.
- **A mechanical guard against line-number citations in docstrings.** Not filed — a new capability,
  belongs in its own phase.
- **The retired-generation fixtures that survive D-12** (`captured_build_v132_leonardo.log`,
  `v151_leonardo`, `v153_*`, the bare/`_fullflash` families). Named, not filed.
- The REPLY strand (Phase 187) and the FLOOR strand (Phase 186).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim from REQUIREMENTS.md) | Research Support |
|----|---------------------------------------------|------------------|
| CLAIM-04 | `firestarter/scripts/baseline/size_baseline.json` records the current cold-build figures (uno 22968, uno328pb 23016, leonardo 25114 — **to be re-measured, not transcribed from this line**), and the default byte-identity gate is green again. | § A.1–A.4 (the +16 B staleness trap, the exact JSON fields the gate reads, the cold-capture recipe) |
| CLAIM-05 | CLAIM-04 is achieved by fixture severance: a new version-named fixture family at the post-change figures, with the existing frozen `captured_build_v158_*` family left byte-unchanged — proven by an empty `git diff` over those paths. No new MERGE-05 exemption is authored. (D-7) | § A.5 (the exhaustive red-leg enumeration and per-leg disposition), § A.6 (the merge05 no-new-exemption re-proof and its `--rebuild` trap) |
| CLAIM-06 | `tests/test_numeric_schema_source_scan.py`'s docstring stops citing `build_db.py:594` for a symbol that lives at 545, and cites the symbol and its enclosing scope instead of a line number. | § C (one-site change, verified; the correct form is already in the same file at line 129) |
| CLAIM-07 | `_is_interactive` is removed, and the two tests named `..._on_a_tty` either gate real TTY behaviour or are renamed and rewritten to assert what they actually cover. No test claims coverage that does not exist. | § B (the 51-site unwrap shapes, the **five** patch sites, the exact `TestUVWriteHasNoPrompt` members, the ruff-format gate) |
| CLAIM-08 | `Catalog sync check` completes with conclusion `success` on `firestarter_prom`'s `main`, and the cause of the failure that has stood since 2026-08-31 is recorded rather than merely cleared. **— AMENDED by D-02** to: *the check is retired, and the cause of its standing failure is recorded.* | § D (the workflow is the meta repo's only one; what survives it; the amendment's two file edits) |

</phase_requirements>

---

## Project Constraints (from CLAUDE.md)

Extracted from `/workspaces/CLAUDE.md`. These bind every recommendation below.

| Directive | Binding effect on this phase |
|-----------|------------------------------|
| **"Write no comments into product source"** — absolute, not overridable by a plan, task, skill or subagent instruction. Covers everything under `firestarter/` and `firestarter_app/`. | Directly binds D-07.2 and D-07.3. The permitted operations are *deleting a false clause* and *deleting a symbol*. If a repair cannot be made without authoring replacement commentary in sub-repo source, leave it and record the deviation in the plan's `SUMMARY.md`. **`tools/catalog/sync_to_subrepos.sh` is in the META repo, not a sub-repo, so D-14's repair is NOT bound by this rule** — but keep new prose minimal anyway. |
| **Docstrings are a separate question.** Click docstrings are user-facing `--help` text. | CLAIM-06 and most of CLAIM-07 are docstring work and are in scope. `test_*.py` docstrings may be freely edited. |
| **`main` is protected in all three repos; `git.base_branch` is `beta`.** | No push to `main`. Criterion 5's original wording (a `success` run on `main`) is unreachable for two independent reasons — the workflow is deleted (D-01) *and* nothing may land on `main` here. |
| **Constants/flag bits duplicated between `constants.py` and `firestarter.h` must change together.** | Not engaged — this phase changes no constants. |
| **Serial protocol changes must be kept in sync.** | Not engaged — explicitly out of scope per CONTEXT.md § Phase Boundary. |
| **Milestone close is hand-archived; `git clean -Xdf` destroys GSD state.** | Any D-14 cleanup must be **by explicit path** (`git -C <repo> checkout -- <path>`). Never `git clean`. |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cold AVR/native measurement | Firmware repo, local `pio` | — | `check_size_baseline.py` is invoked by **no** workflow in either repo; the cold rebuild is a local-run obligation. CI only compares committed artifacts. |
| Size-baseline record + fixture family | Firmware repo `scripts/baseline/` + `tests/fixtures/` | Firmware CI (`build.yml:161 pytest tests/ -v`) | CI catches a baseline move that was not accompanied by severance — it is the safety net, not the producer. |
| Dead-symbol removal | App repo `firestarter/` | App repo `tools/` (allow-list) + `tests/` | The allow-list gate (`_HANDLER_FUNCTION_NAMES`) and two test modules are hard dependents; all three must move in the same commit. |
| Docstring citation repair | App repo `tests/` | — | Pure record; no runtime surface. |
| Cross-repo catalog identity | Meta repo `tools/catalog/sync_to_subrepos.sh` | Each sub-repo's own CI drift gate | After D-01 the sync script is the *only* mechanism asserting cross-sub-repo identity; each sub-repo's gate proves only *its own* toml → *its own* artifact. |
| CLAIM-08's record | Meta repo `.planning/notes/` | `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` | Precedent set by 182/183/184; the amendment lands in the two tracking documents. |

---

## A. The v158 severance transfer (D-08 / D-09 / D-10) — highest-value finding

### A.1 The +16 B trap: the shrink deltas do NOT apply to the live baseline

This is the single most expensive mistake available in this phase.

| Target | `size_baseline.json` live `flash_used` | 183-01 **pre-deletion** measurement | 183-05 **post-deletion** measurement | 183-05's published shrink |
|---|---|---|---|---|
| uno | **22952** | 22968 | **22734** | −234 B |
| uno328pb | **23000** | 23016 | **22778** | −238 B |
| leonardo | **25098** | 25114 | **24830** | −284 B |

`[VERIFIED: firestarter/scripts/baseline/size_baseline.json` read this session — `"flash_used": 22952`
(uno), `23000` (uno328pb), `25098` (leonardo); `"flash_total": 32768` on all three; `"ram_used": 1434`
/ `1440` / `1875`; `"ram_total": 2048` / `2048` / `2560`]
`[VERIFIED: .planning/phases/183-*/183-05-SUMMARY.md` read this session — the shrink table reads
`| uno | 22734 | 22968 | **−234 B** | 1434 | 1434 | +0 B |`, `| uno328pb | 22778 | 23016 | **−238 B**
| 1440 | 1440 | +0 B |`, `| leonardo | 24830 | 25114 | **−284 B** | 1875 | 1875 | +0 B |`, and the
default-mode transcript reads `uno: flash_used baseline=22952 observed=22734`, `uno328pb: flash_used
baseline=23000 observed=22778`, `leonardo: flash_used baseline=25098 observed=24830`]

**The shrink is measured against 183-01's own pre-deletion cold build, not against the live
baseline.** The live baseline was already 16 B stale on every target before Phase 183 began (something
landed between Phase 158's re-record and Phase 183-01 without a re-record — the same staleness class
this whole strand exists to close).

- Naive arithmetic `22952 − 234` gives **22718**. That is wrong.
- The `ROADMAP.md` dependency paragraph quotes only the *deltas*, so a planner reading the ROADMAP
  alone will make exactly this error.
- `REQUIREMENTS.md` CLAIM-04's parenthetical (22968 / 23016 / 25114) is the **183-01 pre-deletion**
  figure — i.e. the pre-shrink tree, wrong by construction, exactly as D-11.2 warns.

**Predicted post-change baseline** (derived, for falsification — D-11 forbids transcription; the
executor's own cold capture is authoritative):

| Field | uno | uno328pb | leonardo |
|---|---|---|---|
| `flash_used` | 22734 | 22778 | 24830 |
| `flash_total` | 32768 | 32768 | 32768 (unchanged) |
| `flash_free` (= total − used) | 10034 | 9990 | 7938 |
| `ram_used` | 1434 | 1440 | 1875 (all unchanged, +0 B) |
| `ram_total` | 2048 | 2048 | 2560 (unchanged) |
| `ram_free` | 614 | 608 | 685 (all unchanged) |

`native_envs.native.cases` and `native_envs.native_nodevtools.cases`/`.succeeded` → **185**; `suites`
stays **17**. `native_pinmap_provisional` (11/11/1) is untouched — it is not in the checker's
`NATIVE_ENVS` tuple and `--rebuild` never visits it.
`[VERIFIED: firestarter/scripts/check_size_baseline.py:146` — `NATIVE_ENVS = ("native",
"native_nodevtools")`]

**If the executor's cold capture disagrees with the predictions above, the capture wins** and the
disagreement must be recorded (183-05's own reconciliation discipline). No firmware `src/` change has
landed since `d8cf708` (183-04), so exact reproduction is expected.
`[VERIFIED: git log/diff --stat d8cf708^..HEAD` in `firestarter/` — the only changed paths are
`CLAUDE.md`, `PROTOCOLS.md`, `scripts/check_erase_no_vpp.py`, `src/proms/flash_5v_page.cpp` (the
183-04 deletion itself), two `tests/avr/**` files and one fixture. Nothing in `src/` after 183-04.]

### A.2 What the gate actually reads (so the JSON edit is minimal and correct)

`compare_avr` reads exactly four fields per target: `flash_used`, `flash_total`, `ram_used`,
`ram_total`. `compare_native` reads exactly `cases`, `suites` and `all_passed`.
`[VERIFIED: firestarter/scripts/check_size_baseline.py:541-571` and `:730-752` — `compare_avr` builds
its failure list from `rec["flash_used"]`, `rec["flash_total"]`, `rec["ram_used"]`, `rec["ram_total"]`
only; `compare_native` from `rec["cases"]`, `rec["suites"]` and `parsed["all_passed"]` only]

**Consequence:** `flash_free`, `ram_free` and the whole `meta` block are **record-keeping, not
gate-bearing** — a wrong `flash_free` is caught by nothing. Every prior generation updated them
anyway; do the same, and treat them as a review item rather than a gate item.

### A.3 Which legs go red when the live baseline moves — the exhaustive set is FOUR

Verified by reading every test body in `firestarter/tests/test_check_size_baseline.py` (1403 lines,
15 test functions).

| # | Leg | Reads | Red on a baseline move? | Disposition this phase |
|---|-----|-------|------------------------|------------------------|
| 1 | `test_clean_avr_all_three_envs_pass` (:523) | `captured_build_v158_{uno,uno328pb,leonardo}.log` vs **live** baseline | **YES** | **SEVER** → `captured_build_v185_*` |
| 2 | `test_clean_native_both_envs_pass` (:565) | `captured_test_native{,_nodevtools}_summary.log` vs **live** baseline; asserts the literal `"184"` in stdout | **YES** (both the fixture and the `184` literal) | **UPDATE IN PLACE** (D-09) + change the two assertions `184` → `185` |
| 3 | `test_planted_flash_regression_flips_checker_to_failure` (:610) | `planted_size_baseline_flash_regression_v158.log`; asserts the literals `"25098"` (baseline) and `"25610"` (observed) | **YES** — and it would fail for *two* reasons, the false-cause pattern severance exists to avoid | **SEVER** → `planted_size_baseline_flash_regression_v185.log`; update both literals |
| 4 | `test_default_mode_is_unchanged_by_the_new_flag` (:1360) | `captured_build_v158_*` vs **live** baseline | **YES** | **SEVER** → `captured_build_v185_*` |
| 5 | `test_baseline_seam_precedence_flips_clean_log_to_fail` (:700) | `captured_build_v153_leonardo.log` + a tampered temp baseline | **NO** | **LEAVE ALONE** — see A.4 |
| 6 | `test_planted_unparseable_log_exits_exactly_2` (:646) | `planted_size_baseline_unparseable.log` | No — parse-failure arm, baseline-independent | untouched |
| 7 | `test_planted_suites_errored_flips_checker_to_failure` (:667) | `planted_size_baseline_suites_errored.log` | No — asserts non-zero + `ERRORED`, not a count | untouched |
| 8 | `test_never_vacuous_with_no_logs_and_no_rebuild` (:683) | nothing | No | untouched |
| 9 | `test_policy_merge05_permits_the_measured_landing_deltas` (:755) | `merge05_base01_anchor_fullflash_*` vs **BASE-01** | No — fixed sub-allowance delta (+0) | **LEAVE ALONE** (D-10) |
| 10 | `test_policy_merge05_admits_the_documented_defect_fix` (:835, 4 arms) | `merge05_defect_fix_fullflash_*`, `planted_..._leonardo_growth_v153`, `merge05_lock_status_v151_*`, `merge05_erase_standalone_v153_*` vs **BASE-01** | No — all BASE-01-anchored at fixed deltas | **LEAVE ALONE** (D-10) |
| 11 | `test_base01_is_not_re_anchored_by_the_new_exemption` (:1106) | BASE-01 JSON + the checker's own source text | No — reads no fixture, by design | **LEAVE ALONE**; authoring no new exemption keeps it green (see A.6) |
| 12-14 | `test_policy_merge05_fires_on_{uno_class_over_band,leonardo_growth,ram_move}` (:1200/:1255/:1296) | `planted_..._v153` plants vs **BASE-01** | No — allowance+1 against a frozen anchor | **LEAVE ALONE** (D-10) |
| 15 | `test_handler…` — n/a | — | — | — |

**The v158 severance's own recorded count is FOUR, and it was anticipated rather than discovered.**
`[VERIFIED: firestarter/tests/test_check_size_baseline.py:545-547` — *"this leg was correctly
anticipated as reddening by `158-before-figures.md` §6 before the re-record happened -- the four legs
named there (this one, the native leg, the planted-regression leg and the default-mode leg below) are
the exhaustive set that couples to a baseline value move, and no fifth leg was found red at this
generation's start."*]

**This phase's expected red-leg count is the same FOUR** — the coupling structure has not changed
since v158. A planner should write that number into the plan as a prediction and require the executor
to reconcile the observed count against it (the house discipline: 153-15 predicted 3 and observed 7,
and recorded the disagreement honestly rather than absorbing it).

### A.4 The leg that is stale but green — do not "helpfully" re-sever it

`test_baseline_seam_precedence_flips_clean_log_to_fail` still reads `captured_build_v153_leonardo.log`
— Plan 158-04 did **not** re-sever it, and the v158 docstring's four-leg enumeration deliberately
excludes it.
`[VERIFIED: firestarter/tests/test_check_size_baseline.py:749-753` — the body reads
`["--avr-log", f"leonardo={_FIXTURES / 'captured_build_v153_leonardo.log'}"]` with
`env_overrides={"FIRESTARTER_SIZE_BASELINE": str(tampered)}`]

It asserts only `returncode != 0` and `"FAIL:" in result.stdout`, so a fixture that is stale against
the live baseline still produces the required red — the staleness rides along invisibly. The leg's own
docstring is candid that this has happened repeatedly and that each prior repointing was a **repair of
the leg's premise**, not a gate requirement.

**Recommendation:** leave it on `v153`, matching what v158 chose, and state the choice in the plan so
it reads as a decision rather than an omission. Re-pointing it onto `v185` is defensible (it restores
the leg's stated premise: *the only failure this run should produce is the one this test plants*) but
it is **not required** by any criterion and it is a fifth touched leg that will not appear in the
predicted red-leg count. If a planner chooses to re-point it, say so up front so the reconciliation
reads 4 red + 1 pre-emptive repair, not 5 red.

### A.5 Fixture-family inventory for the severance

| New file | Derivation | Read by |
|---|---|---|
| `captured_build_v185_uno.log` | cold `rm -rf .pio/build/uno` + one `pio run -e uno`, byte-for-byte | legs 1, 4 |
| `captured_build_v185_uno328pb.log` | same, `uno328pb` | legs 1, 4 |
| `captured_build_v185_leonardo.log` | same, `leonardo` | legs 1, 4 |
| `planted_size_baseline_flash_regression_v185.log` | `captured_build_v185_leonardo.log` with the `Flash:` line's `used` raised by the standing **+512 B** offset (predicted 24830 → 25342); **one changed line**, `RAM:` and every other byte identical; percentage/bar columns left as captured (the parser anchors on the `(used N bytes from M bytes)` tail and never reads the bar) | leg 3 |

| Updated in place (D-09) | Change |
|---|---|
| `captured_test_native_summary.log` | genuinely **re-captured** from a real `pio test -e native`; the summary line moves `184 test cases: 184 succeeded` → `185 … 185 …`; duration is re-captured, never edited |
| `captured_test_native_nodevtools_summary.log` | same for `pio test -e native_nodevtools` |

| Deleted (D-12) — all six confirmed present on disk this session | |
|---|---|
| `captured_build_fullflash_uno.log`, `captured_build_fullflash_uno328pb.log`, `captured_build_v132_uno.log`, `captured_build_v132_uno328pb.log`, `captured_build_v151_uno.log`, `captured_build_v151_uno328pb.log` | `[VERIFIED: ls tests/fixtures/` this session — all six exist] |

| Frozen — criterion 2's `git diff` must be empty over these | |
|---|---|
| `tests/fixtures/captured_build_v158_uno.log`, `…_uno328pb.log`, `…_leonardo.log` | The literal scope of CLAIM-05's *"frozen `captured_build_v158_*` family"* |
| `tests/fixtures/planted_size_baseline_flash_regression_v158.log` | **Not** matched by the `captured_build_v158_*` glob, but it is the v158 generation's planted sibling and retired-in-place by the same convention. Leave it byte-unchanged too; say so explicitly so a reviewer does not read its survival as an oversight. |

**`tests/fixtures/README.md` needs NO new section.** It carries per-family sections for `_fullflash`
and `_v151` only — the `v153` and `v158` generations added none, so the convention lapsed two
generations ago.
`[VERIFIED: firestarter/tests/fixtures/README.md` — its `^## ` headings are exactly: *"Why
`firestarter/tests/` cannot reach a real build"*, *"Verifying fixture presence"*, *"Per-file inventory
is mechanical, not prose"*, *"Files in this directory (as of Plan 01)"*, *"`_fullflash` fixture
families (quick task 260820-a7w)"*, *"`_v151` fixture family (Plan 151-10, LOCK-02)"*, *"Release-asset
fixture trees (Phase 128 Plan 01)"*] Do not make a README section an acceptance criterion; if the
executor deletes the six orphans, check whether any of them is *named* in that README (the `_fullflash`
and `_v151` sections do name them in prose) and repair those prose lines rather than leaving dangling
names — that is this milestone's own defect class.

### A.6 The MERGE-05 no-new-exemption clause, and the `--rebuild` trap that fakes a breach

CLAIM-05's no-new-exemption clause is already satisfied by measurement: 183-05 ran `--policy merge05`
against BASE-01 and got `rc=0` with headroom on all three targets (uno −2090 ≤ 788, uno328pb −2096 ≤
788, leonardo −2076 ≤ 724). A shrink can never need an exemption. `[VERIFIED:
183-05-SUMMARY.md`'s transcript block, read this session]

If the executor re-proves it, **use the canonical invocation — `--avr-log` only, never `--rebuild`:**

```bash
python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=tests/fixtures/captured_build_v185_uno.log \
  --avr-log uno328pb=tests/fixtures/captured_build_v185_uno328pb.log \
  --avr-log leonardo=tests/fixtures/captured_build_v185_leonardo.log
```

**Trap:** `--rebuild` unconditionally also runs both native envs and compares them against whatever
baseline was passed. `size_baseline_base01.json` records `native_envs.native.cases = 184`, and D-10
forbids touching BASE-01. So `--rebuild --policy merge05 --baseline …base01.json` would report a
native `cases baseline=184 observed=185` failure — a **false red produced by a mode mismatch**, not by
any real breach, and one a hurried executor might "fix" by editing BASE-01, which is exactly what D-10
forbids and what `test_base01_is_not_re_anchored_by_the_new_exemption` exists to catch.
`[VERIFIED: firestarter/scripts/baseline/size_baseline_base01.json` — its `native_envs` block reads
`"native": {"cases": 184, "succeeded": 184, "suites": 17, "all_passed": true}` and the same for
`native_nodevtools`] `[VERIFIED: check_size_baseline.py:879-884` — `if rebuild:` loops over `AVR_ENVS`
*and* `NATIVE_ENVS` unconditionally, independent of `policy`]

### A.7 CI consequence — the same-commit rule

`build.yml` runs `pytest tests/ -v` ungated on `push: branches: ['**', '!beta']`; `beta-build.yml`
covers `beta`. Moving `size_baseline.json` without severing the fixtures **in the same commit** turns
the firmware suite red in CI.
`[VERIFIED: firestarter/.github/workflows/build.yml` — trigger `branches: ['**', '!beta']` read this
session; `pytest tests/ -v` step present] `check_size_baseline.py` itself is invoked by **no**
workflow in either repo — the cold rebuild is a local-run obligation.

---

## B. The 51-site unwrap and the dead symbol (D-05 / D-06 / D-07)

### B.1 Call-site shapes — the unwrap is NOT a pure line-delete

Measured with `/usr/bin/grep` on `firestarter_app/tests/test_dev_test_cmd.py`:

| Shape | Count | Unwrap operation |
|---|---|---|
| `with _off_tty():` — **sole** context manager | **46** | Delete the `with` line **and dedent the entire block body by 4 spaces** |
| bare `_off_tty(),` inside a parenthesized multi-context `with (...)` | **5** | Delete that one line; body indentation unchanged |
| the helper definition itself (`:518-520`) | 1 | Delete |

`[VERIFIED: /usr/bin/grep -c '_off_tty()' tests/test_dev_test_cmd.py` = 52 (51 uses + the `def` line);
`/usr/bin/grep -c 'with _off_tty():'` = 46; `/usr/bin/grep -cE '^\s+_off_tty\(\),'` = 5. 46 + 5 = 51,
matching CONTEXT.md's measured figure exactly.]

**This is the mechanical risk of the phase.** 46 block dedents is not a `sed` substitution — it is a
re-indentation of 46 suites, and a single mis-dedent silently moves an assertion out of (or into) a
block. Recommended approach: a scripted transform (tokenize/`ast`-aware or a careful line-range
script) followed by **`ruff format` + the full module run**, never hand editing 46 sites.

The 5 multi-context sites, with their siblings — no decorator form and no nesting exists:

| Line | Siblings in the same `with (...)` | After removal |
|---|---|---|
| 950 | `patch.dict(os.environ, {"FIRESTARTER_CONFIG_DIR": …})` | 1 remaining → collapses to a single-CM `with` |
| 1275 | `patch("firestarter.submit.submit_report")` (as `mock_submit_report`) | 1 remaining → collapses |
| 1302 | `patch("…webbrowser.open", …)`, `patch("…subprocess.run", …)` | 2 remaining → keep the parenthesized form |
| 1966 | `patch("firestarter.cli_handlers.run_plan", side_effect=KeyboardInterrupt)` (`_off_tty()` is **second**) | 1 remaining → collapses |
| 2183 | a multi-line `patch("firestarter.chip_test.resolve_chip", side_effect=…)` (`_off_tty()` is **last**) | 1 remaining → collapses |

`[VERIFIED: firestarter_app/tests/test_dev_test_cmd.py` — all five sites read this session at their
surrounding ±18 lines]

**Formatting gate:** app CI runs `ruff check firestarter/ tests/` **and** `ruff format --check
firestarter/ tests/`, both on Python 3.11. A residual single-item `with (X,):` is valid Python but
will be reformatted by `ruff format`, so `--check` goes red. Run `ruff format` then re-run
`ruff format --check` before committing.
`[VERIFIED: firestarter_app/.github/workflows/ci.yml` — `ruff lint` → `ruff check firestarter/ tests/`;
`ruff format check` → `ruff format --check firestarter/ tests/`; `python-version: '3.11'`]
`[VERIFIED: firestarter_app/pyproject.toml:109-136` — `target-version = "py39"`, `line-length = 88`,
`select = ["E", "F", "I", "UP"]`, `extend-ignore = ["E501"]`, `extend-exclude = ["tests/golden",
"tests/fixtures"]` — `tests/` itself is **not** excluded]

### B.2 Baseline for the behaviour-neutrality proof

```
$ .venv311/bin/python -m pytest tests/test_dev_test_cmd.py -o addopts="" -q
64 passed in 66.61s
```
`[VERIFIED: executed this session in /workspaces/firestarter_app]`

After D-06's merge the expected count is **63 passed**. D-05's proof is "the suite passes unchanged";
make the criterion `63 passed` with the −1 attributed to the merge, not a bare "suite green" (which a
silently-skipped module would also satisfy).

### B.3 `TestUVWriteHasNoPrompt` — FOUR members, not three, and the fifth patch site

The class at `:797` has four members. CONTEXT.md's D-06 names two; the fourth also patches
`_is_interactive` and its docstring carries a TTY claim.

| Member | Line | What it actually does | Disposition |
|---|---|---|---|
| `test_no_prompt_on_a_uv_part_even_on_a_tty` | 823 | `assert not hasattr(cli_handlers_mod, "Confirm")` and `assert not hasattr(…, "_default_uv_write_confirm")` — **zero TTY work** | **RENAME** (D-06). The name is a pure misnomer. Suggested: `test_no_uv_write_prompt_surface_exists`. Body unchanged. |
| `test_uv_part_writes_one_slot_on_a_tty` | 836 | `with patch("firestarter.cli_handlers._is_interactive", return_value=True):` → invoke → `assert "write-partial" in {s["op"] for s in data["steps"]}` | **MERGE** into the next (D-06) — identical assertion, no TTY difference once the patch is inert |
| `test_uv_part_writes_one_slot_off_a_tty_too` | 850 | `with _off_tty():` → invoke → **identical** assertion | **SURVIVOR** of the merge, renamed to carry no TTY claim. Suggested: `test_uv_part_writes_one_slot`. |
| `test_non_uv_part_is_still_written_in_full_without_a_prompt` | 864 | `with patch("firestarter.cli_handlers._is_interactive", return_value=True):` → invoke → asserts `"write" in ops` and `"write-partial" not in ops`. Docstring: *"every non-UV family is written in full, unprompted, **TTY or not**"* | **NOT named by D-06, but must change**: the patch must go (the symbol is being deleted), and the *"TTY or not"* clause becomes a claim nothing tests. The name carries no TTY claim, so **no rename** — drop the patch and the clause. |

`[VERIFIED: firestarter_app/tests/test_dev_test_cmd.py:797-880` read verbatim this session]

The **class docstring** narrates the retired prompt in the past tense (*"on a TTY the operator was
asked…"*). That is a historical account of a removed feature, not a live claim; keep it.

### B.4 Every `_is_interactive` reference, tracked-files-only

```
$ git grep -ln "_is_interactive"      # run inside firestarter_app
firestarter/cli_handlers.py
tests/test_check_devtest_orchestrator.py
tests/test_dev_test_cmd.py
tools/check_devtest_orchestrator.py
```
`[VERIFIED: executed this session — 10 matching lines across those 4 files]`

| File:line | What it is | Action |
|---|---|---|
| `firestarter/cli_handlers.py:2328-2336` | `def _is_interactive() -> bool:` + its docstring + `return sys.stdin.isatty()`. **Zero call sites in live source.** | **DELETE** the function and its docstring |
| `tools/check_devtest_orchestrator.py:163` | `"_is_interactive",` inside the `_HANDLER_FUNCTION_NAMES` frozenset | **DELETE** the entry (D-07.1) |
| `tools/check_devtest_orchestrator.py:66` | module-docstring prose enumerating the allow-list: *"`_chip_id_fields`, `_is_interactive`, `_make_sampler` -- `_HANDLER_FUNCTION_NAMES` below"* | **DELETE the name from the list.** **NOT named in D-07** — a planner must add it, or the phase leaves behind a docstring naming a symbol that no longer exists, i.e. this milestone's own defect class. `tools/` is meta-adjacent app tooling and outside every CI gate, so nothing catches it. |
| `tests/test_check_devtest_orchestrator.py:585` | the subset-vs-equality rationale | **REPAIR** (D-07.2) — see B.5 |
| `tests/test_dev_test_cmd.py:10, 14` | module docstring claiming TTY-gating is controlled by patching `_is_interactive` | **DELETE the false clause** (D-07.3). Under the no-comments rule the permitted operation is deletion, not replacement prose. |
| `tests/test_dev_test_cmd.py:518-520` | the `_off_tty()` helper | **DELETE** (D-05) |
| `tests/test_dev_test_cmd.py:843, 871` | the two direct `patch(…, return_value=True)` calls | **DELETE** (see B.3) |

**Gitignored decoy — do not chase:** `firestarter_app/build/lib/firestarter/cli_handlers.py` contains
3 `_is_interactive` occurrences and is a stale, untracked build artifact.
`[VERIFIED: git check-ignore -v build/lib/firestarter/cli_handlers.py` → `.gitignore:3:build/`;
`/usr/bin/grep -c "_is_interactive" build/lib/firestarter/cli_handlers.py` → `3`]
**`git grep` is the correct evidence tool here** — it scans tracked files only, so it is immune to
*both* devcontainer traps at once: ugrep's `.gitignore`-honouring under-scan and the `build/lib/`
false positive. Use `git grep -n "_is_interactive"` as the "no references remain" gate, never plain
`grep`.

### B.5 D-07.2 — the subset-vs-equality rationale has a ready live replacement

The docstring at `tests/test_check_devtest_orchestrator.py:585` justifies a SUBSET assertion with:
*"`_is_interactive` is legitimately listed but not referenced from `dev_test`'s body -- an equality
assertion would be red for the opposite reason on day one."*

Computed this session from the two live literals:

- `_HANDLER_FUNCTION_NAMES` (11): `dev_test`, `_verdict_code`, `_overall_exit_code`,
  `_dev_test_exit_code`, `_sanitize_chip_token`, `_canonical_part_number`, `_cli_start_time`,
  `_is_uv_eprom`, `_chip_id_fields`, `_is_interactive`, `_make_sampler`
- `_EXPECTED_DEV_TEST_REFERENCED_HELPERS` (7): `_canonical_part_number`, `_chip_id_fields`,
  `_cli_start_time`, `_dev_test_exit_code`, `_is_uv_eprom`, `_make_sampler`, `_sanitize_chip_token`
- listed-but-not-body-referenced **today**: `_is_interactive`, `_overall_exit_code`, `_verdict_code`,
  `dev_test`
- listed-but-not-body-referenced **after the deletion**: `_overall_exit_code`, `_verdict_code`,
  `dev_test`

`[VERIFIED: firestarter_app/tools/check_devtest_orchestrator.py:152-166` and
`tests/test_check_devtest_orchestrator.py:558-566`, both parsed this session]`

**The rationale survives with a different live example and needs no invention.** `_verdict_code` and
`_overall_exit_code` are both listed and both called only *indirectly* (from `_dev_test_exit_code`,
per the same file's own recorded history at `:541-552`), so the subset is still the correct direction.
Repair by swapping the named example — a deletion plus a name substitution inside an existing
docstring, which is the minimal-edit shape the no-comments rule permits.

**Also check:** `test_handler_function_names_contains_the_uv_scope_helper` (`:515`) asserts only
`_is_uv_eprom` and `_canonical_part_number` are in the allow-list — no `_is_interactive` assertion
anywhere, so no additional leg breaks.
`test_handler_function_names_all_resolve_to_real_callables` (`:494`) is the leg that *would* go red if
the symbol were deleted without the allow-list edit — that is the D-07.1 dependency, confirmed live.

---

## C. CLAIM-06 — the stale citation (D-13)

One site, confirmed:

```
$ /usr/bin/grep -nE "\.py:[0-9]+" tests/test_numeric_schema_source_scan.py
40:     on `_AT28C_DIP24_NAMES` (build_db.py:594) -- that set literal (not
```
`[VERIFIED: executed this session — line 40 is the only `.py:NNN` citation in the file]`

The symbol's true location and scope:

```
$ /usr/bin/grep -n "_AT28C_DIP24_NAMES" tools/build_db.py
538:                _AT28C_DIP24_NAMES = {
557:                if _chip_aliases & _AT28C_DIP24_NAMES:
$ /usr/bin/grep -n "^def " tools/build_db.py
…
398:def main():
```
`[VERIFIED: executed this session]` — a **set literal** (not a dict), a **local** variable at 16-space
indentation inside `main()`, nested in a `for` loop. 538, not 594, not 545.

The correct form to copy is already in the same file, at the `_top_level_dict_constant_names` helper
docstring:

> *"that scoping is exactly what keeps this helper from firing on `_AT28C_DIP24_NAMES`, a local
> variable nested inside a `for` loop deep in `main()`, addressing an unrelated pre-existing Phase
> 76/D-03 physical-adapter classification."*

`[VERIFIED: firestarter_app/tests/test_numeric_schema_source_scan.py:127-134` read verbatim this
session]

**Recommendation:** rewrite line 40's parenthetical to the identical symbol-and-scope form — *"a local
variable nested inside a `for` loop deep in `main()`"* — with no line number. The surrounding sentence
already says *"that set literal (not even a Dict) is a LOCAL variable nested inside a `for` loop
several indent levels deep"*, so after the repair line 40 and line 129 read consistently and the file
has zero `.py:NNN` citations. A post-edit `/usr/bin/grep -cE "\.py:[0-9]+"` returning `0` is the
criterion.

---

## D. CLAIM-08 — the retired check (D-01 / D-02 / D-03)

### D.1 What deleting the file actually removes

`.github/workflows/catalog-sync-check.yml` is the **only** workflow in the meta repo.
`[VERIFIED: ls /workspaces/.github/workflows/` → a single entry, `catalog-sync-check.yml`]
After the deletion, `.github/workflows/` is empty (git will drop the directory) and the meta repo has
**no CI at all**. D-03's note should state this in its own terms — it sharpens bullet 5's residual-gap
disclosure from "nothing checks cross-repo identity" to "nothing in this repository runs at all".

The workflow's own "Resolve sub-repo ref" comment — a primary source for D-03 bullets 1-3 — reads
verbatim:

> *"`ref: main` could never work: `tools/catalog/**` has NEVER existed on either sub-repo's `main`
> branch -- the vendored catalog landed on `beta`, and `main` lags `beta` by ~224 commits in the
> firmware repo. The step below used to fail with `cmp: firestarter/tools/catalog/messages.toml: No
> such file or directory`, and this workflow had never once succeeded (5 runs, 5 failures, 2026-07-11
> through 2026-08-18) -- so it has never actually asserted the authority property it exists to
> assert."*

`[VERIFIED: /workspaces/.github/workflows/catalog-sync-check.yml:37-43` read this session]` — read it
into the note **before** deleting; it is the only copy of the false claim D-03 bullet 3 must correct.

The two assertion steps, verbatim, for D-03 bullet 1:
- `:83-87` — `Assert cross-sub-repo vendored catalog identity`:
  `cmp firestarter/tools/catalog/messages.toml firestarter_app/tools/catalog/messages.toml`
- `:89-95` — `Assert vendored catalog matches meta-repo authoritative copy`: four `cmp`/`diff` calls
  against `meta/tools/catalog/messages.toml`

### D.2 What survives the retirement

| Gate | Location | Property proved | Runs on |
|---|---|---|---|
| Catalog validity | `firestarter/.github/workflows/build.yml` → `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | my vendored toml is well-formed | every branch but `beta` (plus `beta-build.yml`) |
| Codegen drift (`messages.h`) | same file → regenerate then `git diff --exit-code include/messages.h` | my toml generates my committed artifact | same |
| Catalog validity | `firestarter_app/.github/workflows/ci.yml` → same `--check` | as above, host side | every branch |
| Codegen drift (`messages.py`) | same file → regenerate then `git diff --exit-code firestarter/messages.py` | as above, host side | every branch |

`[VERIFIED: both workflow files read this session — the steps are named `Catalog validity check` and
`Codegen drift gate (messages.h)` / `(messages.py)`, each preceded by `Set up Python 3.11 for codegen`
/ `Set up Python 3.11`]`

Neither proves the two vendored copies match **each other** or match meta. That is D-03 bullet 5's
residual gap, exactly as CONTEXT.md states it.

### D.3 Current cross-repo state (supports D-03 bullet 4's framing)

| Path (working tree, this milestone branch) | Size | sha256 (first 16) |
|---|---|---|
| `tools/catalog/messages.toml` (meta) | 28658 | `260066039d07ab5c` |
| `firestarter/tools/catalog/messages.toml` | 28658 | `260066039d07ab5c` |
| `firestarter_app/tools/catalog/messages.toml` | 28658 | `260066039d07ab5c` |

`[VERIFIED: sha256sum` executed this session on all three paths]` All three are in lockstep **on this
branch** — which is precisely the operator's point in D-01: the property is real on development
branches and vacuous on `main`. CONTEXT.md's `meta@main` figure (27867 B, `cd5a0bb9…`) is the `main`
snapshot and is 791 B behind; nothing in the working tree contradicts it.

### D.4 The amendment's mechanical scope (D-02)

Two files, both meta-repo `.planning/`:

- `REQUIREMENTS.md:143-144` — CLAIM-08's text. Current: *"`Catalog sync check` completes with
  conclusion `success` on `firestarter_prom`'s `main`, and the cause of the failure that has stood
  since 2026-08-31 is recorded rather than merely cleared."* Amend to the D-02 form, with the reason
  and the precedent (183 D-08, 184 D-03) stated inline.
- `ROADMAP.md` § Phase 185 (heading at `:402`) — success criterion 5.

Both are hand edits. **Do not** use `gsd-tools query requirements`/`roadmap` verbs: they reformat the
whole file, and this project's ROADMAP is hand-authored.

---

## E. D-14 — the sync-script tautologies, and how to see the red

### E.1 What the script does, exactly

`[VERIFIED: /workspaces/tools/catalog/sync_to_subrepos.sh` read in full (101 lines) this session]`

1. `set -euo pipefail`. Resolves both sub-repo `tools/catalog/` targets **by relative path** from the
   script's own directory — it does **not** use git, does not require any particular ref, and does
   not care what branch either sub-repo is on. It only needs both sub-repo directories to exist on
   disk.
2. **Step 1** `cp`s `messages.toml` and `codegen.py` into both sub-repos, each copy verified by
   `diff -q "$src" "$dst"` — **two distinct operands; this is already correct** (`:47-53`).
3. **Lines 65-70** — the one correct cross-sub-repo assertion, with an `else` that prints to stderr
   and `exit 1`. **This is the shape D-14 copies.**
4. **Step 2 (`:78-86`)** regenerates `firestarter/include/messages.h` **directly onto the committed
   path**, then `if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h"` — the same
   path twice. Always true. No `else`. Prints *"OK: … regenerated."* for a property never tested.
5. **Step 3 (`:91-99`)** does the identical thing for `firestarter_app/firestarter/messages.py`.

Because the tautology sits inside an `if` condition, `set -e` never fires on it. The success line is
unconditional in effect.

### E.2 Is running it safe here? Yes — measured

Executed this session from `/workspaces`:

```
$ bash tools/catalog/sync_to_subrepos.sh
  copied: messages.toml -> …/firestarter/tools/catalog
  copied: codegen.py -> …/firestarter/tools/catalog
  copied: messages.toml -> …/firestarter_app/tools/catalog
  copied: codegen.py -> …/firestarter_app/tools/catalog
OK: sub-repo catalogs are byte-identical.
Regenerating firestarter/include/messages.h ...
OK: wrote …/firestarter/include/messages.h (cpp, 77 messages).
  OK: firestarter/include/messages.h regenerated.
Regenerating firestarter_app/firestarter/messages.py ...
OK: wrote …/firestarter_app/firestarter/messages.py (python, 77 messages).
  OK: catalog synced to both sub-repos.
rc=0
```

`git status --porcelain` in both sub-repos afterwards showed **zero tracked modifications** (only two
pre-existing untracked `datasheets/*.pdf`). **The script is a genuine no-op on the current tree**, so
the executor can run it freely; it does mutate files in place, but the content it writes is identical
to what is committed. `[VERIFIED: executed and verified this session]`

### E.3 The repair shape — and why the obvious fix breaks the script

The todo's phrasing ("regenerate into a temp path and diff the committed artifact against that copy…
add the missing `else` with a non-zero exit") has a hazard: taken literally as **drift detection**, a
legitimate catalog edit — the exact situation the script exists to handle — would make the script
`exit 1` instead of updating the artifact, destroying its purpose (`# Idempotent: re-running with no
upstream change is a no-op. Run after every catalog or codegen edit.`, `:15-16`).

**Recommended shape — generate-to-temp, install, verify the install landed.** It mirrors Step 1's own
already-correct `cp` + `diff -q "$src" "$dst"` idiom (`:47-53`) and lines 65-70's `else`/`exit 1`:

```bash
tmp_h="$(mktemp)"
python3 "$META_REPO_CATALOG/codegen.py" \
    --catalog "$META_REPO_CATALOG/messages.toml" \
    --language cpp \
    --target "$tmp_h"
cp "$tmp_h" "$FS_ROOT/include/messages.h" || true
if diff -q "$tmp_h" "$FS_ROOT/include/messages.h" >/dev/null; then
    echo "  OK: firestarter/include/messages.h regenerated."
else
    echo "ERROR: regenerated messages.h did not land at $FS_ROOT/include/messages.h" >&2
    exit 1
fi
rm -f "$tmp_h"
```

Two traceably distinct operands; an `else` with a non-zero exit; the script still performs its update
job; idempotency preserved. The `|| true` on the `cp` is load-bearing — without it `set -e` kills the
script before the verification can report, which is how the failure would be attributed to `cp`
rather than to the assertion.

**Recommended RED-first proof (reproducible, restorable, no `git clean`):**

```bash
# 1. Make the destination unwritable so cp fails and the old bytes survive
chmod 0444 firestarter/include/messages.h
# 2. Plant a divergence so the surviving bytes differ from a fresh generation
#    (do this BEFORE chmod if the file must be edited)
# 3. Run — expect the else branch, the ERROR line and rc=1
bash tools/catalog/sync_to_subrepos.sh; echo "rc=$?"
# 4. Restore, by explicit path only
chmod 0644 firestarter/include/messages.h
git -C firestarter checkout -- include/messages.h
git -C firestarter status --porcelain   # must be empty
```

Transcribe the verbatim `ERROR:` line and `rc=1` into the plan's `SUMMARY.md`. A verification whose
red state has never been seen proves nothing — and note that plain `cp` (not `cp -f`) is required:
GNU `cp -f` unlinks and recreates a read-only destination, which would silently succeed and defeat
the proof.

**Ordering note:** the script's own header comment (`:9`) says *"3. Verifies byte-identical copies and
asserts sub-repo catalog invariant."* — currently two-thirds false. Repairing the code makes the
header true; no new commentary is needed.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| "No references to `_is_interactive` remain" | a `grep -r` sweep | `git grep -n "_is_interactive"` | Immune to both devcontainer traps at once — ugrep's silent `.gitignore` under-scan, and the untracked `build/lib/` false positive |
| Deriving the new baseline figures | subtracting 183's published deltas from `size_baseline.json` | a fresh cold `pio run` capture per env, transcribed | The deltas are anchored to 183-01's pre-deletion figures, not to the live baseline (§ A.1) — the arithmetic is off by 16 B on every target |
| Producing the fixture logs | `check_size_baseline.py --rebuild` | `pio run -e <env> 2>&1 \| tee <fixture>` | `--rebuild` writes **nothing**; it compares in memory (§ F.1) |
| Re-proving MERGE-05 | `--rebuild --policy merge05 --baseline …base01.json` | `--policy merge05` with three explicit `--avr-log`s | `--rebuild` drags in the native comparison against BASE-01's frozen `cases: 184` and manufactures a false red (§ A.6) |
| Unwrapping 46 `with` blocks | 46 hand edits | one scripted transform + `ruff format` + the full module run | A single mis-dedent silently relocates an assertion |
| Amending REQUIREMENTS/ROADMAP | `gsd-tools query requirements/roadmap` verbs | hand edits | Those verbs reformat the whole file; this project's ROADMAP is hand-authored |
| A "byte-unchanged tests" criterion | any such criterion | `git diff --exit-code` over the **named frozen fixture paths** only | REQUIREMENTS.md § "Decisions taken at activation" D-7: *"no acceptance criterion may say 'tests byte-unchanged' — it is unsatisfiable by construction"* |

**Key insight:** every failure mode in this phase is a *record that was updated from another record*
instead of from the tree. The discipline is the same in all five workstreams — read the source of
truth this session, quote it, and never transcribe a number from a prose document.

---

## Common Pitfalls

### Pitfall 1: Deriving the baseline from the published shrink
**What goes wrong:** `22952 − 234 = 22718`, committed, and the default gate stays red by 16 B on every
target — the phase's own criterion 1 fails.
**Why it happens:** the ROADMAP's dependency paragraph quotes deltas; `REQUIREMENTS.md` quotes the
pre-deletion absolutes; neither quotes the post-deletion absolutes, which live only in 183-05's
transcript.
**How to avoid:** transcribe from the executor's own cold capture; use 22734 / 22778 / 24830 only as a
prediction to falsify.
**Warning sign:** a `FAIL:` line whose `observed=` differs from `baseline=` by exactly 16.

### Pitfall 2: Re-recording flash but not native
**What goes wrong:** `compare_native` asserts `cases` exactly; the live baseline still says 184 while
the tree runs 185 → gate red, CI red.
**Why it happens:** the flash figures are the visible half of the change; the native case count moved
in a *different* plan (183-04).
**How to avoid:** the JSON edit touches `avr_targets` **and** `native_envs` in the same commit; the
native summary fixtures are re-captured in the same pass.
**Warning sign:** `native: cases baseline=184 observed=185`.

### Pitfall 3: Mutating the v158 family instead of severing
**What goes wrong:** criterion 2's `git diff` is non-empty; six generations of measurement record are
destroyed.
**Why it happens:** editing three existing logs is less work than committing four new ones.
**How to avoid:** create `captured_build_v185_*` and repoint the legs; never touch `v158`.
**Warning sign:** `git diff --stat tests/fixtures/*v158*` showing any change at all.

### Pitfall 4: Editing BASE-01 to clear a false native red
**What goes wrong:** `test_base01_is_not_re_anchored_by_the_new_exemption` goes red and the frozen
pre-landing anchor — rejected for re-anchoring three times — is destroyed.
**Why it happens:** running `--rebuild` with `--baseline …base01.json` (§ A.6).
**How to avoid:** never pass `--rebuild` and `--baseline …base01.json` together.

### Pitfall 5: A mis-dedent in the 46-site unwrap
**What goes wrong:** an assertion moves outside the block it belonged to and the test passes
vacuously, or a `runner.invoke` result is referenced before assignment.
**How to avoid:** scripted transform; then `ruff check`, `ruff format --check`, and a **63 passed**
count, not a bare green.

### Pitfall 6: Leaving `check_devtest_orchestrator.py:66` naming the deleted symbol
**What goes wrong:** the phase closes having created a fresh instance of its own defect class, in a
file no CI gate reads (`firestarter_app/tools/` has no mypy, no ruff).
**How to avoid:** treat `git grep -n "_is_interactive"` returning **zero tracked matches** as the
criterion — not "the two files D-07 names are edited".

### Pitfall 7: Running the D-14 red-proof with `cp -f`, or cleaning up with `git clean`
**What goes wrong:** `cp -f` unlinks and recreates a read-only destination, so the planted failure
never occurs and the "observed red" is fictional. `git clean -Xdf` destroys GSD state and ignored
bench artifacts.
**How to avoid:** plain `cp` in the repaired script; restore by explicit path with
`git -C <repo> checkout -- <path>`.

### Pitfall 8: `pio test` output has no `Compiling` lines
**What goes wrong:** a reviewer reads a native summary fixture as an incomplete capture.
**Why it happens:** `Compiling .pio/build/...` is `pio run` framing; `pio test` emits `Processing
<suite> in native environment` instead. Recorded in `tests/fixtures/README.md` and `123-01-SUMMARY.md`
as a known, deliberate difference. `[VERIFIED: firestarter/tests/fixtures/README.md`, "Known, recorded
gap (D-14)" paragraph]

---

## F. Cold-rebuild mechanics (D-11) — exact commands

### F.1 `--rebuild` writes nothing

```python
def _rebuild_avr(env):
    subprocess.run(["pio", "run", "-t", "clean", "-e", env], cwd=str(REPO_ROOT), check=True)
    result = subprocess.run(["pio", "run", "-e", env], cwd=str(REPO_ROOT),
                            capture_output=True, text=True)
    return result.stdout + result.stderr

def _rebuild_native(env):
    result = subprocess.run(["pio", "test", "-e", env], cwd=str(REPO_ROOT),
                            capture_output=True, text=True)
    return result.stdout + result.stderr
```
`[VERIFIED: firestarter/scripts/check_size_baseline.py:754-769` quoted verbatim]

It returns the text to `main()`, which parses and compares it. **No file is written** — not the
baseline JSON, not any log. `--rebuild` also has no per-env selector: it always does all three AVR
envs **and** both native envs.

Note the recipe difference: `--rebuild` uses `pio run -t clean -e <env>`, while every committed fixture
generation used `rm -rf .pio/build/<env>` + `pio run -e <env>`. Keep the fixture convention for the
captures (six generations of precedent, and 183-05 used it), and let `--rebuild` be the independent
second opinion.

### F.2 The recommended sequence

```bash
cd /workspaces/firestarter

# 1. Three cold AVR captures — the fixture convention, one env at a time
for e in uno uno328pb leonardo; do
  rm -rf ".pio/build/$e"
  pio run -e "$e" 2>&1 | tee "tests/fixtures/captured_build_v185_$e.log"
done

# 2. Two native re-captures, same pass
pio test -e native            2>&1 | tee tests/fixtures/captured_test_native_summary.log
pio test -e native_nodevtools 2>&1 | tee tests/fixtures/captured_test_native_nodevtools_summary.log

# 3. Transcribe the RAM:/Flash: figures and the `N test cases` line into
#    scripts/baseline/size_baseline.json  (avr_targets + native_envs + meta)

# 4. Derive the planted sibling: leonardo capture, Flash: `used` + 512, one changed line
# 5. Repoint legs 1/3/4, update leg 2's two numeric assertions, extend the docstrings

# 6. Prove — the firmware suite first (fast), the cold rebuild last (slow)
python3 -m pytest tests/ -q
python3 scripts/check_size_baseline.py --rebuild          # criterion 1  — BACKGROUND THIS
```

**`tee` caveat:** the fixture must be byte-for-byte what `pio` emitted. `pio run` detects a non-TTY
stdout and drops ANSI colour, which is what every committed fixture shows, so `| tee` is consistent
with precedent — but diff the new capture's shape against `captured_build_v158_uno.log` before
committing, and re-capture with plain redirection if they differ structurally.

**Timing / tool-call budget.** 183-05 measured `pio test -e native` at **176 s** and
`-e native_nodevtools` at **195 s** in this devcontainer; three cold AVR builds add several minutes.
Step 6's `--rebuild` is a *second* full cold pass (3 clean AVR builds + 2 native runs) and will
plausibly run **10-15 minutes** — **longer than the 600 s maximum for a single Bash tool call.** Plan
it as a backgrounded run with polling, or the executor will hit a `rc=124` that reads like a gate
failure. (Known project trap: a timeout `rc=124` misreads as a RED.)

### F.3 Is the cold rebuild feasible here? YES

| Check | Result |
|---|---|
| `pio` on PATH | `/usr/local/bin/pio`, PlatformIO Core **6.1.19** |
| AVR toolchain | `~/.platformio/packages/toolchain-atmelavr` present |
| Uno / Leonardo framework | `framework-arduino-avr` present |
| uno328pb framework | `framework-arduino-avr-minicore` present |
| Envs declared | `platformio.ini` `[env:uno]:31`, `[env:uno328pb]:43`, `[env:leonardo]:60`, `[env:native]:83`, `[env:native_nodevtools]:142` |
| Precedent | 183-05 executed all three cold AVR builds **and** both native runs locally in this devcontainer |

`[VERIFIED: all rows executed/read this session]` **No operator step is required** and no network
download is expected — every needed package is already in `~/.platformio/packages`.

---

## Runtime State Inventory

This is a record-repair phase with deletions; the inventory is still required.

| Category | Items Found | Action Required |
|---|---|---|
| Stored data | **None** — no database, collection, key or user_id carries any renamed string. `_is_interactive` is a private Python symbol; the fixture family names are file names only. | none |
| Live service config | **GitHub Actions is the one live registration.** Deleting `catalog-sync-check.yml` removes the meta repo's only workflow; GitHub de-registers it when the deletion reaches the default branch. Until then, `gh workflow list` still shows it and `workflow_dispatch` remains invocable from `main`. **No `main` branch in any of the three repos has required status checks** (measured during discussion), so the deletion cannot leave a PR permanently pending. | none beyond the file deletion; note the de-registration lag in D-03's record |
| OS-registered state | **None** — no scheduled task, service or daemon references anything this phase changes. | none |
| Secrets / env vars | **None.** `FIRESTARTER_SIZE_BASELINE` and `FIRESTARTER_DEVTEST_HANDLER` are read-seams whose *names* are unchanged; no secret is involved. | none |
| Build artifacts / installed packages | **Two, both benign.** (1) `firestarter_app/build/lib/firestarter/cli_handlers.py` — gitignored stale sdist artifact still containing `_is_interactive`; do **not** delete it as part of this phase and do not report it as a surviving reference. (2) `firestarter/.pio/build/` — cleaned per-env by the capture recipe; that is the intent, not a side effect. | none |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| `pio` (PlatformIO Core) | criterion 1, the four fixture captures | ✓ | 6.1.19 | — |
| AVR toolchain + 2 frameworks | the three cold AVR builds | ✓ | `toolchain-atmelavr`, `framework-arduino-avr`, `framework-arduino-avr-minicore` | — |
| `python3` (firmware-side) | `check_size_baseline.py`, firmware `pytest tests/` | ✓ | devcontainer default | — |
| `firestarter_app/.venv311` | every app-side check (CI is 3.11-only) | ✓ | Python 3.11.16 | none — the devcontainer's 3.12 masks app CI and has PROVEN to break beta CI |
| `ruff` in `.venv311` | `ruff check` + `ruff format --check` | ✓ | in `.venv311/bin` | — |
| `mypy`, `pytest` in `.venv311` | watermark gate, suites | ✓ | in `.venv311/bin` | — |
| `gh` (authenticated) | CLAIM-08 run-history citation | ✓ | 2.98.0, logged in as `henols` | — |
| `bash`, `cp`, `diff`, `mktemp` | D-14 | ✓ | — | — |
| Network to GitHub | `gh run list` for the D-03 record | ✓ | — | CONTEXT.md already carries the full 8-run table, so a network outage is not blocking |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none.

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** No `npm install`, `pip install` or
`cargo add` appears anywhere in its scope: the work is file edits, fixture captures, one file
deletion and one shell-script repair. The package-legitimacy seam was therefore not run, and no
`[SLOP]`/`[SUS]` dispositions exist to report.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json`, so it is treated as enabled. The phase's
attack surface is nil — no new input parsing, no network, no credential handling, no persisted data.

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | no auth surface is touched |
| V3 Session Management | no | no sessions |
| V4 Access Control | no | no access decision changes; the deleted `_is_interactive` gated nothing (zero call sites) |
| V5 Input Validation | no | no parser changes; `check_size_baseline.py` is not modified |
| V6 Cryptography | no | none involved |
| V12 File / Resource | **marginal** | D-14's repair introduces a `mktemp` temp file. Use `mktemp` (not a fixed `/tmp` path) and `rm -f` it — the sketch in § E.3 does both. |
| V14 Configuration | **yes, weakly** | D-01 removes a CI check. Mitigation is the D-03 record itself, plus the four surviving per-sub-repo gates in § D.2 — the residual gap is disclosed, not silently accepted. |

| Threat pattern | STRIDE | Mitigation in this phase |
|---|---|---|
| A hand-edited vendored `messages.toml` diverging silently between sub-repos | Tampering / Repudiation | D-14's repaired assertion at sync time + D-03 bullet 5's explicit disclosure. **Not** a new guard — D-04 forbids filing one. |
| A temp-file race in the repaired sync script | Tampering | `mktemp`, single-user devcontainer, removed on completion |

---

## Verification Reachability

Every criterion in its operative form, with a concrete command and an explicit FAIL signature.

### Criterion 1 — `check_size_baseline.py` default mode exits 0 against a fresh cold rebuild

```bash
cd /workspaces/firestarter && python3 scripts/check_size_baseline.py --rebuild; echo "rc=$?"
```
**PASS:** `rc=0` and a single `PASS:` line naming all five envs, e.g.
`uno(flash=…/32768,ram=…/2048), uno328pb(…), leonardo(…), native(cases=185,suites=17),
native_nodevtools(cases=185,suites=17)`.
**FAIL:** `rc=1` with `FAIL:` and per-env `flash_used baseline=… observed=…` lines (a divergence);
`rc=1` with *"no envs compared"* (vacuous — impossible with `--rebuild`, but distinguish it);
`rc=2` with `ERROR: … could not parse` (a tool/format failure, **not** a size finding);
`rc=124` — a **timeout**, not a gate result (see § F.2).
**Reachable from this devcontainer:** YES, but **must be backgrounded** (10-15 min).

### Criterion 2 — the frozen v158 fixtures are byte-unchanged, and no new MERGE-05 exemption

```bash
cd /workspaces/firestarter
git diff --exit-code -- tests/fixtures/captured_build_v158_uno.log \
                        tests/fixtures/captured_build_v158_uno328pb.log \
                        tests/fixtures/captured_build_v158_leonardo.log \
                        tests/fixtures/planted_size_baseline_flash_regression_v158.log; echo "rc=$?"
git diff --exit-code -- scripts/check_size_baseline.py; echo "checker-untouched rc=$?"
/usr/bin/grep -c "^MERGE05_.*_EXEMPTION_BYTES" scripts/check_size_baseline.py   # must stay 4
```
**PASS:** first `rc=0` (empty diff); the exemption-constant count unchanged at 4
(`DEFECT_FIX`, `PAGE_SIZE_SEAM`, `LOCK_STATUS_READ`, `ERASE_STANDALONE`) plus the unchanged
`PAGE_SIZE_SEAM_RAM` — i.e. `test_base01_is_not_re_anchored_by_the_new_exemption` stays green.
**FAIL:** any non-empty diff over those four paths; any new `MERGE05_*_EXEMPTION_BYTES` constant.
**Note:** run `git diff` **against the phase's base commit**, not just the worktree, so a
commit-then-revert cannot hide a mutation: `git diff --exit-code <base-sha> -- <paths>`.
**Reachable:** YES.

### Criterion 3 — the docstring citation names symbol and scope, no line number

```bash
cd /workspaces/firestarter_app
/usr/bin/grep -cE "\.py:[0-9]+" tests/test_numeric_schema_source_scan.py     # must be 0
/usr/bin/grep -n "_AT28C_DIP24_NAMES" tests/test_numeric_schema_source_scan.py
/usr/bin/grep -n "_AT28C_DIP24_NAMES" tools/build_db.py                      # 538, 557
```
**PASS:** count `0`, and the line-40 region names `_AT28C_DIP24_NAMES` with its enclosing scope
(`main()`, inside a `for` loop) and no digits after a `.py`.
**FAIL:** count ≥ 1; or any occurrence of the literals `594` or `545` near the symbol.
**Reachable:** YES.

### Criterion 4 — `_is_interactive` is gone; no test name claims TTY gating it does not perform

```bash
cd /workspaces/firestarter_app
git grep -n "_is_interactive" ; echo "tracked-refs rc=$?"      # rc=1 (no matches) is PASS
git grep -n "_off_tty"        ; echo "helper rc=$?"            # rc=1 is PASS
git grep -nE "def test_.*_(on|off)_a_tty" tests/                # must return nothing
.venv311/bin/python -m pytest tests/test_dev_test_cmd.py -o addopts="" -q       # expect 63 passed
.venv311/bin/python -m pytest tests/test_check_devtest_orchestrator.py -o addopts="" -q
.venv311/bin/ruff check firestarter/ tests/
.venv311/bin/ruff format --check firestarter/ tests/
.venv311/bin/python tools/check_mypy_watermark.py
```
**PASS:** both `git grep`s exit 1 with no output; no `_on_a_tty`/`_off_a_tty` test names; `63 passed`;
the orchestrator-gate module green; ruff and the watermark clean.
**FAIL:** any tracked `_is_interactive` match (**ignore** `build/lib/…` — `git grep` already excludes
it); `64 passed` (the merge did not happen) or `< 63` (a test was lost, not merged);
`test_handler_function_names_all_resolve_to_real_callables` red (the allow-list edit was missed);
`ruff format --check` red (a residual single-item `with (X,):`).
**Reachable:** YES. **Note:** `mypy` prints OK when it is missing — confirm `.venv311/bin/mypy` exists
before trusting the watermark gate.

### Criterion 5 (AMENDED per D-02) — the check is retired, and the cause is recorded

```bash
cd /workspaces
test ! -e .github/workflows/catalog-sync-check.yml && echo "workflow deleted"
ls .github/workflows/ 2>/dev/null || echo "workflows dir gone (it was the only one)"
git grep -n "catalog-sync-check" -- . ':!.planning'            # must return nothing outside .planning/
ls .planning/notes/*catalog*                                    # the D-03 verdict note exists
/usr/bin/grep -c "33447867312" .planning/notes/<note>.md        # the failing run is cited
/usr/bin/grep -n "CLAIM-08" .planning/REQUIREMENTS.md           # amended wording present
gh run list --repo henols/firestarter_prom --workflow 'Catalog sync check' --limit 10
```
**PASS:** file absent; no non-`.planning/` references remain; the note exists and carries **all five**
D-03 contents (cause / why the 2026-08-18 fix missed / the workflow comment now false / the naive-beta
counterfactual / the residual gap); REQUIREMENTS.md and ROADMAP.md both carry the amended wording with
the reason.
**FAIL:** the file still present; a dangling reference outside `.planning/`; a note missing any of the
five; the original *"conclusion `success` on `main`"* wording left unamended anywhere.
**Reachable from this devcontainer:** **PARTIALLY.** The filesystem and note checks are fully
reachable. `gh run list` is reachable and authenticated, but it is **not a proof of anything in the
amended form** — the workflow's registration only disappears once the deletion reaches the default
branch, which is a post-merge, operator-gated event on protected `main`. A planner must **not** write
a criterion that depends on GitHub's view of the workflow. Use it only to confirm no *new* run
appeared (the last remains `33447867312`, 2026-08-31, failure). **The 87 `.planning/` files citing the
workflow are historical-by-intent and must NOT be repaired.**

### Folded scope (D-14) — the sync script's repaired verifications

```bash
cd /workspaces
bash tools/catalog/sync_to_subrepos.sh; echo "green rc=$?"        # expect rc=0, tree unchanged
git -C firestarter status --porcelain; git -C firestarter_app status --porcelain
/usr/bin/grep -n 'diff -q "\$\([A-Z_]*\)[^"]*" "\$\1' tools/catalog/sync_to_subrepos.sh  # no same-operand diff
# then the RED proof of § E.3, transcribed verbatim, then restore by explicit path
```
**PASS:** green run `rc=0` with clean sub-repo trees; zero self-comparing `diff` invocations remain;
the planted red observed with an `ERROR:` line and `rc=1`; both sub-repos clean again afterwards.
**FAIL:** any surviving `diff -q "$X" "$X"`; a "success" line printed on a path with no `else`; a red
proof that was asserted but not transcribed; a dirty sub-repo tree left behind.
**Reachable:** YES — verified by executing the script this session (§ E.2).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The post-change AVR figures will reproduce as 22734 / 22778 / 24830 and the native count as 185 | A.1 | Low — no `src/` change since 183-04 (verified). If the capture disagrees, the capture wins; the plan must require reconciliation, never transcription. |
| A2 | The expected red-leg count is exactly 4, as at v158 | A.3 | Medium — the enumeration was derived by reading all 15 test bodies, but only observation settles it. Record the prediction and reconcile, as 153-15 did when it predicted 3 and saw 7. |
| A3 | `pio run \| tee` produces a fixture structurally identical to the committed v158 captures | F.2 | Low-medium — diff the shape against `captured_build_v158_uno.log` before committing; re-capture with plain redirection if it differs. |
| A4 | Renaming to `test_no_uv_write_prompt_surface_exists` / `test_uv_part_writes_one_slot` satisfies D-06 | B.3 | Low — names are the planner's call; the binding property is that no surviving name claims TTY gating. |
| A5 | `--rebuild` takes 10-15 min | F.2 | Low — extrapolated from 183-05's measured 176 s + 195 s native runs plus three cold AVR builds. Wrong only in magnitude; the mitigation (background it) is correct either way. |
| A6 | Plain `cp` fails on a read-only destination while `cp -f` succeeds, making the § E.3 red proof work | E.3 | Medium — GNU coreutils behaviour, not verified by execution this session. The executor must **observe** the red, not assume it; if this recipe does not go red, find another that does before trusting the repair. |
| A7 | The `.planning/notes/` filename is the planner's choice (precedent gives the pattern, not the name) | D | Nil |

---

## Open Questions (RESOLVED)

1. **Re-point `test_baseline_seam_precedence_flips_clean_log_to_fail` onto `v185`, or leave it on
   `v153`?**
   - What we know: v158 left it alone; it asserts only `rc != 0` and `FAIL:`, so it rides along green
     while its fixture is stale against the live baseline; its own docstring records three prior
     repointings, each framed as restoring the leg's premise.
   - What's unclear: whether this phase wants to pay a fifth touched leg for a premise repair no
     criterion demands.
   - Recommendation: **leave it on `v153`**, matching v158, and say so explicitly in the plan so the
     reconciliation reads *4 red, 1 known-stale-but-green, deliberately untouched*.
   - **RESOLVED — leave it on `v153`; recommendation adopted verbatim by plan 185-01.** Task 1 Step 6
     requires the reconciliation paragraph to read *4 red + 1 deliberately untouched*, naming
     `test_baseline_seam_precedence_flips_clean_log_to_fail` explicitly, and 185-01's
     `<flagged_assumptions>` records the non-repointing as a decision rather than an omission.

2. **Does the D-12 deletion orphan any prose in `tests/fixtures/README.md`?**
   - What we know: the README's `_fullflash` and `_v151` sections name files by name; four of the six
     deletion targets belong to those two families.
   - What's unclear: whether every mention is a family-level plural or a per-file name.
   - Recommendation: after deleting, `/usr/bin/grep -n` each deleted filename across the firmware repo
     (excluding `.git`/`.pio`) and repair any prose that now names a non-existent file — otherwise the
     phase authors a fresh instance of its own defect class in its own evidence directory.
   - **RESOLVED — by plan 185-02 Task 2, in a stronger form than this recommendation.** The
     exact-filename search the recommendation assumes is the same form that produced D-12's premise, so
     185-02 Task 2 re-measures brace-aware FIRST — from the tree, both search forms recorded — and lets
     the disposition follow D-12's own criterion that a prose citation counts as a live reference. The
     prose repair is then required only under a DELETE disposition. A brace-aware search run at planning
     time found all three candidate families cited in `tests/fixtures/README.md` and in
     `test_check_size_baseline.py`'s module docstring, so the expected disposition is KEEP and the
     expected prose repair is none; the executor still measures rather than inherits that.

3. **Where exactly does the `185-` fixture generation's severance account go?**
   - What we know: v151 and v153 wrote long module-docstring sections; v158 wrote **per-test**
     docstring paragraphs only and added no module-docstring section (verified: the module docstring
     ends at the Plan 153-15 account).
   - Recommendation: follow **v158** — per-leg docstring paragraphs on the four severed/updated legs,
     no new module-docstring section, no README section. Smallest diff, most recent precedent, and it
     keeps the record next to the assertion it explains.
   - **RESOLVED — follow `v158`; recommendation adopted verbatim by plan 185-01.** Task 1 Step 6 mandates
     per-leg docstring paragraphs on the four severed/updated legs, and an acceptance criterion asserts
     that no new module-docstring section and no new `tests/fixtures/README.md` section was added.

---

## State of the Art

| Old approach | Current approach | When changed | Impact |
|---|---|---|---|
| Re-anchor the baseline and mutate the existing fixtures | Sever onto a new phase-numbered family; retire the old one in place and keep it | Phase 149 Plan 07, six generations ago | Legs asserting at fixed sub-allowance deltas stay green; the measurement record stays legible without a git dig |
| Delete retired fixtures | Keep them (`git ls-files` + the mechanical inventory already exclude anything no checker names) | quick task 260820-a7w | **Exception, deliberate:** D-12 deletes six fixtures that are named *nowhere at all* — not even in prose. That is a different category from "retired but still cited". |
| Document each family in `tests/fixtures/README.md` | Lapsed — `v153` and `v158` added no section | Plan 153-15 onward | Do not make a README section an acceptance criterion |
| A cross-repo catalog check as a meta-repo workflow | Per-sub-repo validity + drift gates only | this phase (D-01) | Cross-sub-repo identity is asserted only at sync time, by `sync_to_subrepos.sh`; the gap is recorded, not guarded (D-04) |
| Cite a symbol by `file.py:NNN` | Cite symbol + enclosing scope, never a line number | this phase (D-13); the correct form already exists at `test_numeric_schema_source_scan.py:129` | The citation has staled three times; the requirement's own figure staled within a day of being written |

**Deprecated / outdated in the inputs to this phase:**
- `REQUIREMENTS.md` CLAIM-04's parenthetical (22968 / 23016 / 25114) — the **pre-deletion** tree.
- `REQUIREMENTS.md` CLAIM-06's "lives at 545" — it is at 538 since `529d6e1` (Phase 182-02).
- `REQUIREMENTS.md` CLAIM-08 / ROADMAP criterion 5 — unsatisfiable as written once D-01 lands.
- `catalog-sync-check.yml:41-43`'s *"never once succeeded (5 runs, 5 failures)"* — overtaken hours
  later by two successes on 2026-08-18.
- `test_dev_test_cmd.py:8-14`'s TTY-gating claim — false today.
- `tools/catalog/sync_to_subrepos.sh:9`'s *"Verifies byte-identical copies"* — two-thirds false until
  D-14 lands.

---

## Sources

### Primary (HIGH confidence) — read or executed in this session
- `firestarter/tests/test_check_size_baseline.py` (all 1403 lines: module docstring + 15 test bodies)
- `firestarter/scripts/check_size_baseline.py` (`parse_sizes`, `compare_avr`, `compare_native`,
  `_rebuild_avr`, `_rebuild_native`, `main`, the argv parser, the exemption constants)
- `firestarter/scripts/baseline/size_baseline.json`, `…/size_baseline_base01.json` (parsed)
- `firestarter/tests/fixtures/` (directory listing; `README.md` headings and the `pio test` framing gap)
- `firestarter/.github/workflows/build.yml`; `firestarter_app/.github/workflows/ci.yml`
- `firestarter/platformio.ini` (env declarations)
- `firestarter_app/tests/test_dev_test_cmd.py` (docstring, `_off_tty`, all 51 sites' shapes,
  `TestUVWriteHasNoPrompt` in full)
- `firestarter_app/firestarter/cli_handlers.py:2328-2336`
- `firestarter_app/tools/check_devtest_orchestrator.py:55-80, 140-185`
- `firestarter_app/tests/test_check_devtest_orchestrator.py:486-566, 565-625`
- `firestarter_app/tests/test_numeric_schema_source_scan.py:1-60, 122-140`
- `firestarter_app/tools/build_db.py` (symbol + scope locations)
- `firestarter_app/pyproject.toml` (ruff/mypy config)
- `/workspaces/.github/workflows/catalog-sync-check.yml` (full)
- `/workspaces/tools/catalog/sync_to_subrepos.sh` (full, **and executed**)
- `/workspaces/.planning/phases/183-*/183-05-SUMMARY.md` (measured figures and gate transcripts)
- `/workspaces/.planning/REQUIREMENTS.md` § CLAIM; `/workspaces/.planning/ROADMAP.md` § Phase 185
- `/workspaces/CLAUDE.md`; `/workspaces/.planning/config.json`
- Executed: `pytest tests/test_dev_test_cmd.py` (64 passed), `sha256sum` on three catalog copies,
  `git grep`, `git check-ignore`, `pio --version`, `gh auth status`, `git log/diff --stat`

### Secondary (MEDIUM confidence)
- `firestarter_app/tests/fixtures`-adjacent prose and prior-generation severance accounts quoted
  inside the module docstring (they are primary about the *past*, secondary about the present tree)

### Tertiary (LOW confidence)
- None. No web search was performed — this phase has no external technology domain; every question was
  answerable from the live tree.

---

## Metadata

**Confidence breakdown:**
- Severance transfer / red-leg enumeration: **HIGH** — every test body read; the v158 account states
  its own expected count and the coupling structure is unchanged.
- Cold-rebuild mechanics: **HIGH** — `--rebuild` semantics read from source; the toolchain probed;
  183-05 proves the same builds ran locally in this container.
- The +16 B trap: **HIGH** — three independent figures (live JSON, 183-05's table, 183-05's `FAIL:`
  transcript) agree on the arithmetic.
- 51-site unwrap: **HIGH** — counts measured with `/usr/bin/grep`; all five multi-context shapes read.
- `_is_interactive` dependents: **HIGH** — `git grep` enumerated all 10 tracked lines; the
  subset/equality set difference computed from the live literals.
- D-14 mechanics: **HIGH** for the script's behaviour (executed); **MEDIUM** for the proposed red-proof
  recipe (A6 — `cp` vs `cp -f` not executed).
- Predicted post-change figures: **MEDIUM by design** — predictions to falsify, per D-11.

**Research date:** 2026-09-11
**Valid until:** 2026-10-11 for the structural findings; the predicted byte figures are valid only
while no firmware `src/` change lands — they must be re-measured, never transcribed.
