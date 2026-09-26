---
title: After-figures record -- milestone v1.33, Phase 158 (Residual Optimizations + Cold Baseline Re-Record, firmware-only)
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "06"
measured: 2026-08-24
status: AUTHORITATIVE -- this file is the phase's outcome record, re-measured against the committed
  tree at `firestarter` `2ccda8d` this session, never merely transcribed from an earlier plan's
  SUMMARY. Every AVR figure below is COLD. Phase 159 remaps every `file:LINE` citation in this
  record exactly once, over the composite pre-154 -> post-158 diff (D-01, D-05) -- no citation here
  is repaired by this plan.
supersedes: >
  ROADMAP.md Phase 158's success criteria 3 (`cases baseline=141 observed=172`), 5 (`-128 B RAM for
  +30 B flash`), 6 (`masking costs +22 B flash (flat)`) and 7 (`57 tokens`, `7 tokens of headroom`);
  REQUIREMENTS.md LAND-03 (`observed=172`), LAND-05 (`+30 B flash`), LAND-06 (`+22 B flash (flat)`)
  and LAND-07 (`57 tokens`, `7 tokens of headroom`) prose, wherever they state a figure this file
  corrects -- corrections C-1 through C-13, all first identified in `158-before-figures.md` and
  closed out here against the shipped, final tree. Neither ROADMAP.md nor REQUIREMENTS.md is edited
  by this plan; plan 07 alone applies scoped `Edit` replacements (OD-9 as amended).
requirements: [LAND-01, LAND-02, LAND-03, LAND-04, LAND-05, LAND-06, LAND-07, LAND-08]
---

# After-figures record -- v1.33 Phase 158

This is the phase's landing record: all twelve phase-gate legs run and recorded on the final
committed tree at `firestarter` `2ccda8d`, with every headline AVR/native figure **COLD** and
re-measured this session, never transcribed from an earlier plan's SUMMARY except where the plan's
own prohibitions require it (LAND-06's mask cost, which exists only inside a torn-down worktree and
cannot be re-derived on this tree). Two gates flip polarity in this phase -- default mode and the
canonical `--policy merge05 --rebuild` invocation -- and both flips are recorded with their before
shape (quoted from `158-before-figures.md`) and their after shape (quoted from this session's own
run) side by side. LAND-04, LAND-06, LAND-07 and LAND-08 are discharged by this record alone, since
none of the four changes any code. All thirteen corrections (C-1 through C-13) and all ten decisions
(OD-1 through OD-10) are closed out below. Every figure carries the verbatim command that produced
it.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_POST_SHA` (full) | `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` |
| `FW_POST_SHA` (abbrev) | `2ccda8d` |
| Branch | `gsd/v1.33-source-hygiene-firmware-size-reduction` |
| `git -C /workspaces/firestarter status --porcelain` | empty, asserted before and after every measurement step this session |
| Meta HEAD (before this plan's own commit) | `0e1dbaa1ce65736412a05584f31715f645b0acfb` |
| `git worktree list` | `/workspaces/firestarter` (primary, `2ccda8d`) + `/workspaces/firestarter_py32_ci` (pre-existing, unrelated sibling, untouched by this plan) |

**Six firmware commits landed this phase**, exactly matching the distribution the plan predicted
(two from plan 02, one from plan 04, three from plan 05; none from plans 01, 03 or 06):

| # | Hash | Plan | Subject |
|---|---|---|---|
| 1 | `490c435` | 02 | `refactor(158-02): narrow jsmntok_t to 6 bytes, start/end stay signed` |
| 2 | `8e126f2` | 02 | `test(158-02): pin the jsmn token layout as a region-scoped source contract` |
| 3 | `e730068` | 04 | `test(158-04): re-record size_baseline.json from cold builds and sever fixtures onto v158` |
| 4 | `7894dec` | 05 | `fix(158-05): re-anchor BASE-01's native inventory axis to the measured count` |
| 5 | `5dca69d` | 05 | `test(158-05): close the named Phase 158 checker and fixture floor carry-forward` |
| 6 | `2ccda8d` | 05 | `docs(158-05): correct two false CI-coverage claims in the gate test modules` |

**Plans 01, 03 and 06 produced zero firmware commits**, confirmed this session: plan 01 wrote only
`.planning/milestones/v1.33-artifacts/158-before-figures.md` in the meta repo; plan 03 is a measure-and-record plan whose
own SUMMARY states "None" under Task Commits, with `git diff HEAD --name-only` over
`src/proms/flash_5v_page.cpp` empty throughout its session; this plan (06) writes only into
`.planning/` and edits no file under `firestarter/`.

**Gitlink drift, recorded and not touched (OD-10, ceiling 12):**

| Repo | Meta records | Actual HEAD | Status |
|---|---|---|---|
| `firestarter` | `2ad5b322a37ba4a88afd09cc946f5c4114e51483` | `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` | **drifted** -- pre-existing since Phase 154, operator-gated, **not re-pinned by this phase** |
| `firestarter_app` | `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2` | `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2` | matches; not touched by this phase |

Commands: `git -C /workspaces/firestarter rev-parse HEAD`; `git -C /workspaces/firestarter
status --porcelain`; `git -C /workspaces/firestarter log -6 --format='%h %s'`; `git -C /workspaces
rev-parse HEAD`; `git -C /workspaces ls-tree HEAD firestarter firestarter_app`; `git -C
/workspaces/firestarter worktree list`.

---

## 2. The phase ledger -- flash and RAM, before vs after, per target, COLD

Both sides are **COLD** (`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>` per env,
never `pio run -t clean`, never `check_size_baseline.py --rebuild`).

| Target | Before (COLD, `158-before-figures.md` S2, at `785e644`) | After (COLD, this session, at `2ccda8d`) | Flash delta | RAM before | RAM after | RAM delta |
|---|---|---|---|---|---|---|
| `uno` | 23090 / 1562 | 22952 / 1434 | **-138 B** | 1562 | 1434 | **-128 B** |
| `uno328pb` | 23138 / 1568 | 23000 / 1440 | **-138 B** | 1568 | 1440 | **-128 B** |
| `leonardo` | 25234 / 2003 | 25098 / 1875 | **-136 B** | 2003 | 1875 | **-128 B** |

**Attribution: the entire composed delta belongs to LAND-05 (plan 02).** LAND-06 was declined
(plan 03, zero source change, `src/proms/flash_5v_page.cpp` confirmed byte-unchanged against HEAD
throughout that plan's session). Plans 01, 04 and 05 touched zero files that affect a compiled
byte -- plan 04 rewrote only `scripts/baseline/size_baseline.json` and test fixtures, and plan 05
rewrote only `scripts/baseline/size_baseline_base01.json` and two test modules' docstrings/floors,
none of which are compiled into any firmware image.

**Byte-identity of the final builds against the committed captures, proven this session:**
```bash
rm -rf .pio/build/uno .pio/build/uno328pb .pio/build/leonardo
pio run -e uno > cold-uno.log; pio run -e uno328pb > cold-uno328pb.log; pio run -e leonardo > cold-leonardo.log
# zero 'warning:' lines on all three
python3 -c "... compares Flash:/RAM: used figures against tests/fixtures/captured_build_v158_*.log ..."
# => COLD-MATCHES-FIXTURES
```
All three cold rebuilds this session reproduced the committed `captured_build_v158_{uno,uno328pb,
leonardo}.log` fixtures byte-for-byte on the `Flash:`/`RAM:` used figures, with zero `warning:`
lines on every target -- the tree has not changed since plan 04 captured them, and this session's
independent rebuild proves it rather than assuming it.

**Leonardo's final Caterina headroom against the `28672` B bootloader cliff:**
`28672 - 25098 = 3574 B` (correction **C-13**, superseding both the ROADMAP's stale figure and
`158-before-figures.md` S2's own `3438 B`, which was correct only at the pre-LAND-05 position
`785e644` and explicitly left open pending this measurement). This is up from `3438 B`
pre-LAND-05 -- an improvement of `136 B` of headroom, exactly Leonardo's own flash delta above.

Commands: `rm -rf .pio/build/<env> && pio run -e <env>` for each of `uno`, `uno328pb`, `leonardo`,
this session; `grep -E 'Flash:|RAM:' <log>`; `28672 - 25098` (arithmetic).

---

## 3. LAND-01 -- the cold re-record

**The cold recipe, verbatim, unchanged since `158-before-figures.md` S2 and executed identically
by plan 04 and re-verified by this plan:** `rm -rf .pio/build/<env>` then exactly one
`pio run -e <env>` per env, teed to a log; `pio test -e native` and `pio test -e native_nodevtools`
run once each with no `-f` filter, reading the trailing `N test cases: N succeeded` line.

**All sixteen re-recorded fields, with their transcription source per field** (plan 04's own
commit `e730068`, re-confirmed present on the tree at `2ccda8d` this session):

| Field | Old value | New value | Transcription source |
|---|---|---|---|
| `avr_targets.uno.flash_used` | 25548 | 22952 | `tests/fixtures/captured_build_v158_uno.log` |
| `avr_targets.uno.flash_free` | 7220 | 9816 | `tests/fixtures/captured_build_v158_uno.log` (32768 - used) |
| `avr_targets.uno.ram_used` | 1575 | 1434 | `tests/fixtures/captured_build_v158_uno.log` |
| `avr_targets.uno.ram_free` | 473 | 614 | `tests/fixtures/captured_build_v158_uno.log` (2048 - used) |
| `avr_targets.uno328pb.flash_used` | 25598 | 23000 | `tests/fixtures/captured_build_v158_uno328pb.log` |
| `avr_targets.uno328pb.flash_free` | 7170 | 9768 | `tests/fixtures/captured_build_v158_uno328pb.log` |
| `avr_targets.uno328pb.ram_used` | 1581 | 1440 | `tests/fixtures/captured_build_v158_uno328pb.log` |
| `avr_targets.uno328pb.ram_free` | 467 | 608 | `tests/fixtures/captured_build_v158_uno328pb.log` |
| `avr_targets.leonardo.flash_used` | 27630 | 25098 | `tests/fixtures/captured_build_v158_leonardo.log` |
| `avr_targets.leonardo.flash_free` | 5138 | 7670 | `tests/fixtures/captured_build_v158_leonardo.log` |
| `avr_targets.leonardo.ram_used` | 2016 | 1875 | `tests/fixtures/captured_build_v158_leonardo.log` |
| `avr_targets.leonardo.ram_free` | 544 | 685 | `tests/fixtures/captured_build_v158_leonardo.log` |
| `native_envs.native.cases` | 172 | 184 | `tests/fixtures/captured_test_native_summary.log` |
| `native_envs.native.succeeded` | 172 | 184 | `tests/fixtures/captured_test_native_summary.log` |
| `native_envs.native_nodevtools.cases` | 172 | 184 | `tests/fixtures/captured_test_native_nodevtools_summary.log` |
| `native_envs.native_nodevtools.succeeded` | 172 | 184 | `tests/fixtures/captured_test_native_nodevtools_summary.log` |

**Untouched fields:** `flash_total` (32768 x3), `ram_total` (2048/2048/2560), `suites` (17 both
native envs), `native_pinmap_provisional`, `envs_agree`, and the whole `warnings` block.

**The new `meta` note key:** `meta.cold_rerecord_phase158`, appended following the established
precedent of adding a new dated note rather than rewriting an existing one (matching
`meta.native_case_count_revision_260822` and `meta.flash_ceiling_move_260820_a7w`'s own
convention).

**Two prose repairs (C-7, C-8), both closed by plan 04's commit `e730068`:**
- **C-7** -- `meta.consumed_by` named two consumers; corrected to name all **three**:
  `check_size_baseline.py`, `check_build_warnings.py`, and `check_release_assets.py` (which derives
  its required asset set from `avr_targets`' keys and runs in CI at `beta-build.yml:327`).
- **C-8** -- `envs_agree_note` quoted a stale `{cases: 151, suites: 17}`; repaired (a pre-existing
  self-flag already named by `meta.native_case_count_revision_260822` in the same file, now
  restated correctly).

**BASE-01's growth axis was NOT re-anchored, proven by a CI-invoked leg:**
```bash
python3 -m pytest "tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption" -q -o addopts=""
# => 1 passed in 0.01s
```
This leg runs in CI (it lives inside `tests/test_check_size_baseline.py`, which `build.yml:161`'s
`pytest tests/ -v` executes on every branch except `beta`). Confirmed directly this session:
`scripts/baseline/size_baseline_base01.json`'s `avr_targets` block is byte-identical to its value at
`785e644` (`{uno: 24824/1573, uno328pb: 24874/1579, leonardo: 26906/2014}`, all flash/ram figures
unchanged) -- only `native_envs` (the test-inventory axis, LAND-03) and the new `meta` note moved.

**The default-mode polarity flip -- LAND-01's own discharge evidence.**

Before (`158-before-figures.md` S4, quoted verbatim, at `785e644`, exit **1 -- RED**):
```
FAIL:
  uno: flash_used baseline=25548 observed=23090
  uno: ram_used baseline=1575 observed=1562
  uno328pb: flash_used baseline=25598 observed=23138
  uno328pb: ram_used baseline=1581 observed=1568
  leonardo: flash_used baseline=27630 observed=25234
  leonardo: ram_used baseline=2016 observed=2003
  native: cases baseline=172 observed=184
  native_nodevtools: cases baseline=172 observed=184
```

After (this session, at `2ccda8d`, exit **0 -- GREEN**):
```bash
python3 scripts/check_size_baseline.py --avr-log uno=tests/fixtures/captured_build_v158_uno.log \
  --avr-log uno328pb=tests/fixtures/captured_build_v158_uno328pb.log \
  --avr-log leonardo=tests/fixtures/captured_build_v158_leonardo.log \
  --native-log native=tests/fixtures/captured_test_native_summary.log \
  --native-log native_nodevtools=tests/fixtures/captured_test_native_nodevtools_summary.log
```
```
PASS: uno(flash=22952/32768,ram=1434/2048), uno328pb(flash=23000/32768,ram=1440/2048), leonardo(flash=25098/32768,ram=1875/2560), native(cases=184,suites=17), native_nodevtools(cases=184,suites=17)
```

**The flip is the discharge evidence for LAND-01.** The baseline is re-recorded from COLD builds
exactly as required, the AVR figures match the committed fixtures byte-for-byte, and default mode
moves from every-line-RED to a full `PASS:` covering all three AVR targets and both native envs.

---

## 4. LAND-02 -- the one-sidedness and the severance

**Both growth-only comparisons, quoted from source this session** (`scripts/check_size_baseline.py`,
byte-unchanged the whole phase -- confirmed: `git diff 785e644 HEAD -- scripts/check_size_baseline.py`
is empty):
```
697:    if flash_delta > allowance:
709:    if ram_delta > ram_tolerance:
```
Both are strict, growth-only inequalities: a negative delta (a reduction) can never fail either
clause, no matter how large.

**The verbatim `PASS:` line, three negative flash deltas against positive allowances, three
negative RAM deltas against a positive tolerance:**
```bash
python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=tests/fixtures/captured_build_v158_uno.log \
  --avr-log uno328pb=tests/fixtures/captured_build_v158_uno328pb.log \
  --avr-log leonardo=tests/fixtures/captured_build_v158_leonardo.log
```
```
PASS: uno(flash=22952/32768[-1872<=788=band64+exempt96+seam210+lock288+erase130],ram=1434/2048[-139<=2=seam2]), uno328pb(flash=23000/32768[-1874<=788=band64+exempt96+seam210+lock288+erase130],ram=1440/2048[-139<=2=seam2]), leonardo(flash=25098/32768[-1808<=724=band0+exempt96+seam210+lock288+erase130],ram=1875/2560[-139<=2=seam2])
```
Every one of the six flash/RAM comparisons is **negative** against a **positive** allowance/
tolerance -- this is a **ONE-SIDED** pass (D-03): it proves flash/RAM did not grow past the
allowance, never that "nothing changed". No MERGE-05 exemption was authored or widened; the six
literals (`band64`, `exempt96`, `seam210`, `lock288`, `erase130`, `seam2`) all read the same
unchanged constants confirmed by the empty checker-source diff above.

**Severance inventory: 4 new files plus 2 updated in place**, every file named:

| Disposition | File | Note |
|---|---|---|
| new | `tests/fixtures/captured_build_v158_uno.log` | plan 04, cold `pio run` capture |
| new | `tests/fixtures/captured_build_v158_uno328pb.log` | plan 04, cold `pio run` capture |
| new | `tests/fixtures/captured_build_v158_leonardo.log` | plan 04, cold `pio run` capture |
| new | `tests/fixtures/planted_size_baseline_flash_regression_v158.log` | plan 04, derived plant |
| updated in place | `tests/fixtures/captured_test_native_summary.log` | plan 04, genuine `pio test` capture |
| updated in place | `tests/fixtures/captured_test_native_nodevtools_summary.log` | plan 04, genuine `pio test` capture |

**The plant's single-line derivation:** `planted_size_baseline_flash_regression_v158.log` is a
byte-for-byte copy of `captured_build_v158_leonardo.log` with the `Flash:` used figure alone
advanced by the standing `+512 B` offset (`25098 + 512 = 25610`), matching every prior generation's
rule since Phase 123.

**The in-place licence, quoted from the leg's own docstring** (`tests/test_check_size_baseline.py`,
around `test_clean_native_both_envs_pass`): *"No severance needed here, unlike the AVR
captured_build_*.log family: this is the ONLY leg in this module that consumes either native
summary fixture."*

**`*_v153*` disposition: retired in place, and KEPT.** The prior generation's three
`captured_build_v153_*.log` files and the one `planted_size_baseline_flash_regression_v153.log` are
left on disk, unmodified, unread by any leg once plan 04 repointed the four reddening legs.

**Groups 2 and 3 were deliberately NOT authored this generation.** Every prior generation's
severance docstring documents four groups totalling 13 files; this generation authors only 4 new
files plus 2 updated in place. The reason: **no MERGE-05 exemption is authored for a reduction**
(D-03) -- Group 2 (a synthetic BASE-01-anchor trio) and Group 3 (an exemption-admission trio) exist
in prior generations only because those generations *widened* an exemption constant, which this
phase never does. All three surviving `planted_size_baseline_policy_{uno_over_band,leonardo_growth,
ram_moved}_v153.log` plants derive their expected-failure position from `allowance + 1` against the
same six MERGE-05 literals, none of which moved this phase, so their derivation basis is untouched
and they need no re-plant -- **asserted green rather than re-planted** (correction **C-11**).
Confirmed this session: those three legs remain green, unmoved, on the final committed tree.

---

## 5. LAND-03 -- the inventory axis

**The four integers, old and new:**

| Field | Old | New |
|---|---|---|
| `native_envs.native.cases` | 141 | 184 |
| `native_envs.native.succeeded` | 141 | 184 |
| `native_envs.native_nodevtools.cases` | 141 | 184 |
| `native_envs.native_nodevtools.succeeded` | 141 | 184 |

(`suites` stays `17` on both entries; `all_passed` stays `true`.)

**The axis-split argument, quoted from the leg's own docstring in `size_baseline_base01.json`'s
`meta.native_inventory_axis_phase158` note** (plan 05, commit `7894dec`):

> "This is a THIRD axis, distinct from the two already recorded above: the growth axis
> (`avr_targets.*.flash_used`, `avr_targets.*.ram_used`), which stays frozen and is untouched by
> this edit, and the board-identity axis (`avr_targets.*.flash_total`), already licensed to move
> with cause by `flash_ceiling_move_260820_a7w`. This is a test-inventory axis: a frozen inventory
> count is monotonically invalid, because tests only accumulate -- the firmware's native suite only
> ever gains cases across phases, it never loses one, so a count fixed at a past phase's figure is
> guaranteed to go stale, not merely liable to."

**Named cause:** BASE-01 was last touched for its `native_envs` block at its Phase 124 genesis
(`141` cases, `17` suites) and was never updated as later phases (through Phase 157) added native
cases to the live suite.

**Not caused by this milestone:** this milestone's own size-reduction diff (Phase 158 plans 02-04)
touches zero files under `test/native/avr/` -- the `141`-to-`184` gap accumulated entirely across
Phases 124 through 157, before v1.33 began.

**Correction C-12, the corrected exit-1 mechanism:** the AVR comparison inside `main()` always ran
**first** and **passed** -- confirmed this session by LEG 7's own output below, which now carries
the full AVR decomposition alongside the native figures. It is the **report line** (built inside the
AVR loop, printed only by `_print_pass`) that never got reached once the later native loop appended
a failure and the early `if all_failures: return 1` fired -- the comparison itself was never
suppressed, only its own successful report.

**Measured zero-legs-reddened result:** `test_base01_is_not_re_anchored_by_the_new_exemption` (S3
above) never reads `native_envs`, so this fix reddens zero legs -- confirmed this session by the
whole checker suite staying at 14 passed after the fix landed.

**The declined floor-semantics alternative, with its cost** (from the same `meta` note): "making
the case count a floor under `--policy merge05` (failing only when the observed count drops below
the recorded one) is more semantically honest but changes `compare_native`'s gate behaviour, needs
a new fixture pair plus a planted negative case, and widens this landing phase beyond its scope --
recorded as declined, not attempted."

**The `--rebuild` polarity flip, both shapes:**

Before (`158-before-figures.md` S4, quoted verbatim, exit **1**):
```
FAIL:
  native: cases baseline=141 observed=184
  native_nodevtools: cases baseline=141 observed=184
```
(zero AVR `flash_used`/`ram_used` lines -- the AVR comparison already passed, C-12)

After (this session, exit **0**):
```bash
python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild
```
```
PASS: uno(flash=22952/32768[-1872<=788=band64+exempt96+seam210+lock288+erase130],ram=1434/2048[-139<=2=seam2]), uno328pb(flash=23000/32768[-1874<=788=band64+exempt96+seam210+lock288+erase130],ram=1440/2048[-139<=2=seam2]), leonardo(flash=25098/32768[-1808<=724=band0+exempt96+seam210+lock288+erase130],ram=1875/2560[-139<=2=seam2]), native(cases=184,suites=17), native_nodevtools(cases=184,suites=17)
```
**This `--rebuild` run was used strictly as a check, per Pitfall 6 and this phase's own
convention -- no figure in this record is transcribed from it.** (`--rebuild`'s own `_rebuild_avr`
uses `pio run -t clean`, not the mandated `rm -rf .pio/build/<env>` cold recipe.)

---

## 6. LAND-04 -- both clauses

**Clause 1 -- no `.github/` workflow invokes `check_size_baseline.py` as a size gate**, re-confirmed
this session in all three repos:

| Repo | Command | Output | Exit |
|---|---|---|---|
| `firestarter` | `grep -rn "check_size_baseline" .github/` | (none) | **1** |
| meta (`/workspaces`) | `grep -rn "check_size_baseline" .github/` | (none) | **1** |
| `firestarter_app` | `grep -rn "check_size_baseline" .github/` | (none) | **1** |

`ls scripts/check_*.py | wc -l` -> **8** files: `check_build_warnings.py`,
`check_cmake_manifest.py`, `check_erase_no_vpp.py`, `check_landing_range.py`,
`check_no_heap_or_64bit_symbols.py`, `check_orphan_provisional.py`, `check_release_assets.py`,
`check_size_baseline.py`. **Exactly one** -- `check_release_assets.py` -- is invoked by any
workflow (`beta-build.yml:327`). The other **seven are local-run obligations**, individually named:
`check_build_warnings.py`, `check_cmake_manifest.py`, `check_erase_no_vpp.py`,
`check_landing_range.py`, `check_no_heap_or_64bit_symbols.py`, `check_orphan_provisional.py`,
`check_size_baseline.py`.

**Clause 2 -- the checker IS nonetheless executed in CI by its own paired pytest.**
`build.yml:161` runs `pytest tests/ -v`, ungated by any `if:`; `build.yml`'s trigger
(`build.yml:34`) is `push: branches: ['**', '!beta']` -- `'**'` matches this milestone branch, and
only `beta` is excluded. `beta-build.yml:134` runs the sibling leg on `push: branches: [beta]`.

**Consequence, stated in one sentence:** re-recording `size_baseline.json` without severing the
fixtures in the same commit turns CI red on this branch, because `tests/test_check_size_baseline.py`
runs as a subprocess inside that `pytest` step and reads the moved live baseline against the old
fixture logs -- exactly the reason the S-4 one-commit rule (`e730068`) was followed.

**Exhaustive CI-leg enumeration for this branch:** `pio test -e native` (`build.yml:122`),
`pio test -e native_nodevtools` (`:128`), `pytest tests/ -v` (`:161`), `pio run` (the full AVR
build, after the publish boundary), and the separate `py32f071.yml` ARM build workflow (its own
`push: branches: ['**']` trigger also fires on this branch). **There is nothing else.**

**The two docstring corrections landed in plan 05** (commit `2ccda8d`), recorded as the same claim
in source: `tests/test_check_size_baseline.py`'s and `tests/meta_presence.py`'s module docstrings
previously claimed "no CI leg exercises it in either repository" -- both false since `build.yml`'s
trigger widened. Both were corrected, comment-only, verified this session by an AST-diff with
docstrings stripped showing zero assertion/import/constant/function-definition changes in either
file (**correction C-9**, closed here). Correction **C-6** (LAND-04 stated as a single clause,
corrected to two clauses) was already closed in `158-before-figures.md` and is reconfirmed
unchanged on this final tree.

---

## 7. LAND-05 -- the narrowing

**Layout, before and after** (`lib/jsmn/src/jsmn.h`, at `785e644` vs `2ccda8d`):

```c
/* before, 8 B (with alignment) */
typedef struct jsmntok {
  jsmntype_t type;
  int start;
  int end;
  int size;
} jsmntok_t;

/* after, 6 B */
typedef struct jsmntok {
  uint8_t type;   /* was jsmntype_t (16-bit int on AVR); values 0,1,2,4,8 */
  uint8_t size;   /* was int; max is an object's pair count or array length */
  int start;      /* UNCHANGED, signed -- carries the -1 sentinel */
  int end;        /* UNCHANGED, signed -- carries the -1 sentinel */
} jsmntok_t;
```
`#include <stdint.h>` added beside the pre-existing `#include <stddef.h>`.

**The `sizeof` probe, 8 -> 6, re-derived this session against the real, shipped header:**
```bash
# old (785e644): avr-gcc -std=gnu11 -mmcu=atmega328p -Os -I... -c sizeof_old.c
avr-nm --print-size --radix=d sizeof_old.o | grep total   # => 00000008 00000008 C total
# new (2ccda8d), against lib/jsmn/src/jsmn.h directly:
avr-nm --print-size --radix=d sizeof_real.o | grep total  # => 00000006 00000006 C total
# native/host, for contrast (unaffected, always 12 B either side):
nm --print-size --radix=d sizeof_real_native.o | grep total  # => ...0000000000000012 B total
```
Toolchain: `avr-gcc` at `$HOME/.platformio/packages/toolchain-atmelavr/bin`, `-mmcu=atmega328p -Os`.

**The `-128 B` RAM saving, exactly derived and linker-witnessed:** `NUMBER_JSNM_TOKENS` = `64`
(`include/json_parser.h:17`); `64 tokens x 2 bytes-per-token-saved = 128 B`, matching the linker's
own `RAM: used N` line on all three targets (S2 above: `1562->1434`, `1568->1440`, `2003->1875`,
all exactly `-128 B`).

**Three flash deltas, `+30 B` named superseded (correction C-2):** `-138 / -138 / -136 B` on
`uno` / `uno328pb` / `leonardo` (S2 above) -- flash is a **reduction** on every target. REQUIREMENTS
LAND-05's stale prediction of `+30 B flash` is reproducible on no layout tried and is superseded by
this measured figure.

**Twelve sentinel field references, six `jsmn.c` line numbers, confirmed unedited:**
```bash
grep -n "start = -1\|end = -1\|== -1\|!= -1" lib/jsmn/src/jsmn.c
```
Lines `15, 222, 241, 256, 290, 348` each carry a `.start`/`.end` (or `tok->start`/`tok->end`) pair
referencing the `-1` sentinel, twelve field references across six lines. `jsmn.c` is byte-unedited:
`git diff 785e644 HEAD -- lib/jsmn/src/jsmn.c` is empty.

**The source-contract gate, `tests/test_jsmn_token_layout_source_contract_v158.py`, five legs, all
green this session** (`5 passed in 0.03s`): region-scoped to the text above the
`#ifndef JSMN_HEADER` marker (`jsmn.h:34` defines `JSMN_HEADER`, so the dead duplicate
implementation below is never compiled and is deliberately excluded from the scan); environment
seam `FIRESTARTER_JSMN_TOKEN_LAYOUT_SCAN_SOURCE`, binding at import time. All three probe outcomes,
verbatim from plan 02's own session (header restored between each, `git diff --quiet` verified):
- **Probe A** (load-bearing): narrowed the LIVE struct's `start` to `uint16_t` ->
  `test_token_start_and_end_remain_signed_int` **FAILED** (`any_start_count == 0`, required `1`).
- **Probe B** (dead-copy hazard): narrowed ONLY the dead duplicate implementation's local
  `int start;` (below the `#ifndef JSMN_HEADER` marker) to `uint16_t` -> all 5 legs stayed
  **GREEN**, proving the region scope excludes the dead copy by design.
- **Probe C** (non-vacuity): pointed the environment seam at a non-existent path in a genuine
  subprocess -> Coverage 1 and 2 **FAILED** with `FileNotFoundError`; Coverage 3/4/5 stayed passing
  since they never read the seam.

**The deliberate non-edit of the dead duplicate implementation (OD-6):** `jsmn.h`'s dead code below
`#ifndef JSMN_HEADER` (compiling in no translation unit, since `JSMN_HEADER` is `#define`d above
it) is left byte-unedited. A reader grepping `jsmn.h` for `int size;` will find the dead copy --
stated here so that grep is not mistaken for evidence of an incomplete narrowing.

**The `sizeof`-assertion prohibition (ceiling 6):** `sizeof(jsmntok_t)` cannot be asserted in a
native test -- AVR gives `6` B, the host gives `12` B (confirmed above). The linker's `RAM: used N`
line and `avr-nm` are the only valid witnesses.

**The ARM outcome -- BOTH SIDES BUILT.** `arm-none-eabi-gcc`, `cmake` and `ninja-build` installed
cleanly via `apt-get` on the first attempt in this devcontainer session (plan 02); both positions
were built using the exact `py32f071.yml` composite-action recipe:

| Position | Result | `text` | `data` | `bss` | `dec` |
|---|---|---|---|---|---|
| Pre-narrowing (`785e644`, throwaway detached worktree) | **SUCCESS** | 26900 | 32 | 5888 | 32820 |
| Post-narrowing (HEAD, `/workspaces/firestarter`) | **SUCCESS** | 26924 | 32 | 5632 | 32588 |

Both builds produced a non-empty `firestarter_py32f071.hex`. **LAND-05's ARM half is verified
locally, not merely ceiling-recorded** -- the toolchain install succeeded on the first attempt, so
no ceiling applies this session. No language in this section implies coverage beyond what was
actually built on both sides.

---

## 8. LAND-06 -- the recorded decline

**This section is what discharges LAND-06. No code changed to discharge it.** `src/proms/
flash_5v_page.cpp` is byte-unchanged against `HEAD` for the entire phase (`git diff 785e644 HEAD --
src/proms/flash_5v_page.cpp` empty, confirmed this session).

**Measured per-target flash cost, from plan 03's own throwaway-worktree measurement (the mask
exists in no committed tree and cannot be re-derived without re-running that discarded worktree,
per this plan's own prohibition):**

| Env | Flash (unmasked, shipped) | Flash (masked, probe only) | Delta | RAM delta |
|---|---|---|---|---|
| `uno` | 22952 B | 22974 B | **+22 B** | **0 B** |
| `uno328pb` | 23000 B | 23024 B | **+24 B** | **0 B** |
| `leonardo` | 25098 B | 25120 B | **+22 B** | **0 B** |

Command used inside the torn-down worktree: cold `pio run -e <env>` before and after hoisting
`const uint32_t page_mask = page_size - 1;` and rewriting both boundary predicates from
`% page_size` to `& page_mask`. **The flat `+22 B` REQUIREMENTS LAND-06 states is superseded
(correction C-3)** by this per-target measurement: right on `uno` and `leonardo`, **2 B low on
`uno328pb`** (`+24 B` observed vs `+22 B` claimed) -- the identical disagreement already opened in
`158-before-figures.md` and `158-RESEARCH.md` F-6, independently reproduced at a later tree position
(post-jsmntok_t-narrowing) than either source used.

**Two witnessed division sites, re-confirmed present on the shipped image this session:**
```bash
NM=~/.platformio/packages/toolchain-atmelavr/bin/avr-nm
OD=~/.platformio/packages/toolchain-atmelavr/bin/avr-objdump
$NM --print-size .pio/build/uno/firestarter_uno.elf | grep flash_5v_page_write_execute
# => 00002d68 000001d4 T flash_5v_page_write_execute   (address 0x2d68, size 0x1d4 = 468 B)
$OD -d --start-address=0x2d68 --stop-address=0x2f3c .pio/build/uno/firestarter_uno.elf \
  | grep -c __udivmodsi4
# => 2
```
**Exactly 2 `__udivmodsi4` calls inside `flash_5v_page_write_execute` on the final, shipped `uno`
ELF** -- confirming LAND-06 was declined in the shipped tree, since the same disassembly on the
masked probe (plan 03) showed exactly **0** calls in the identical symbol range after the mask.
Identical shape on `uno328pb` (`0x2df8`, `0x1d4`) and `leonardo` (`0x327a`, `0x1d4`), per plan 03's
own session.

**Image-wide call-site count, re-confirmed this session on the shipped `uno` image:**
```bash
$OD -d .pio/build/uno/firestarter_uno.elf | grep "call.*__udivmodsi4"| wc -l
# => 11
```
**11** call sites image-wide today (unmasked) -- matching plan 03's own "before" measurement exactly
(the mask never landed, so this IS the "after" state of LAND-06's decline: unchanged from
"before"). Plan 03's own masked-probe measurement (torn down, not re-derivable here) found the count
drops to **9** under the mask -- still non-zero, so **there is no linkage saving**: `__udivmodsi4`
(`0x44` = 68 B) stays linked either way. A surviving caller, named by file and line:
`src/proms/eprom_budget.cpp:109` (`uint32_t rem = per_byte_us % 1000000UL;` inside
`eprom_block_budget_s`).

**Enumerated zero behavioural native coverage, with the arithmetic** (plan 03, all 14 registered
`test/native/avr/test_val_5v_page/test_val_5v_page.cpp` cases read case-by-case): **2 of 14** cases
execute `flash_5v_page_write_execute` (`test_5v_page_write_execute_emits_sdp`,
`test_5v_page_write_execute_no_vpp`), both via the identical `make_write_handle_with_data()` helper
(`mem_size=524288`, `address=0`, `data_size=4`) -- `flash_5v_page_page_size(524288) = 256`. A 4-byte
write starting at address 0 against a 256-byte page: `is_page_start` is confounded with
`is_first_byte` at `i=0` and trivially false at `i=1,2,3`; `reached_page_end` is `(4) % 256 = 4 != 0`
for the last byte -- **never true**. **No case in the tree exercises either boundary predicate's
non-trivial (true, boundary-crossing) branch.** This corrects `158-RESEARCH.md` F-6's own
enumeration (which named only one write-path-executing case) to the accurate count of two; the
coverage-gap conclusion is unaffected by the correction since both cases drive the identical 4 bytes.

**The declined alternative's oracle and its native case-count cost** (from `158-RESEARCH.md` F-6,
restated, not re-derived, since D-02 forbids any bench addition and this oracle is source-level
counting): a counting variant of `recording_contains_sdp_signature`, driven by a handle spanning
exactly two 64-byte pages (`mem_size=32768`, `data_size=128`), asserting exactly 2 SDP signatures
and 2 page-end poll windows, proven RED against a deliberately wrong mask before being trusted.
Adding it would move the native case count from **184 to 185 or 186**, which would have had to land
**before** plan 04's re-record, not after -- this alternative is **declined**, its cost stated
rather than omitted.

**The runtime half, unquantified by construction, not by omission.** D-02 forbids a bench criterion
for this milestone; only silicon could measure the runtime win a mask would buy. Native trace stubs
record no time (`delay()`/`delayMicroseconds()` unstubbed in `test/native/avr/_shared/
host_stubs_common.inc`), so a native trace diff attests register-write sequence only, never
duration. **This section contains no numeric runtime estimate, no percentage, and no
comparative-speed claim anywhere.**

**The four-fact disconnection paragraph, verbatim from plan 03's own session:**

> This change is scoped to the **algorithm-5 flash-page write path only** --
> `configure_flash_5v_page` (`src/proms/flash_5v_page.cpp:41`), reached from `configure_memory`'s
> dispatch for protocols `PROTO_FLASH_5V_PAGE` (`0x05`), `PROTO_PHANTOM_0x35`, and
> `PROTO_PHANTOM_0x39`. It is **not** connected to the w27c512-write-slow-3x work, which rewrote
> `eprom_write_execute` in `src/proms/eprom.cpp` -- a different file, a different handler, a
> different protocol family (the `0x07`/`0x08`/`0x0B` UV-EPROM family), and a per-byte
> high-voltage (VPE) settle-time problem rather than a division-cost problem. REQUIREMENTS.md's
> "Out of Scope" section separately rules `eprom_write_execute` untouchable for this milestone.
> Separately, algorithm 13's masked page-end predicate in `src/proms/eeprom_28c.cpp:628-636,752`
> is a **different problem, kept distinct on purpose**: its page size arrives from the host wire
> and could be anything, so it needs the validating resolver it has (`eeprom28c_page_mask`);
> algorithm 5's page size is derived internally from three literal returns that are provably
> powers of two, so a bare mask would suffice there and a validator would be dead code.

**LAND-06 is discharged by this section, and by no code change** -- the measured cost, the two
witnessed division sites, the enumerated zero-coverage gap and the four-fact disconnection are, all
together, the stated reason for the decline.

---

## 9. LAND-07 -- the token arithmetic

**Three bounds, re-derived this session against the unchanged final tree** (`pinouts.json` and
`chip_database.json` are untouched by this phase, so this figure is unaffected by any code change --
re-run for confirmation rather than transcribed blind):

```bash
python3 /tmp/gsd-158/land07_tokens.py
```
```
pinouts.json record count: 15
maximum address-bus-pins across all records: 19
maximum static-high-pins across all records: 1

Bound (b) -- maximum over any real pin map with every optional scalar: 51 tokens, pin map = DIP32_27C020
Bound (a) -- observed maximum over the real chip database: 50 tokens, chip = W29C020,W29C020C,W29C022

Bound (c) -- field-wise-maximum synthetic (exists in no real record): 55 tokens

NUMBER_JSNM_TOKENS (include/json_parser.h): 64
Headroom, bound (a) chip-database max:  14
Headroom, bound (b) real-pin-map max:    13
Headroom, bound (c) synthetic max:        9

The criterion's 57 tokens / 7 tokens headroom is reproducible by none of these three counting rules.
```

| Bound | Value | Headroom vs 64 | Input |
|---|---|---|---|
| Observed maximum, real chip database | **50** | **14** | `W29C020,W29C020C,W29C022` swept through `convert_to_programmer` plus every optional runtime key |
| Maximum over any real pin map, every optional scalar | **51** | **13** | `DIP32_27C020` (18 address-bus-pins + `rw-pin` + `vpp-pin`) plus all 12 top-level scalars |
| Field-wise-maximum synthetic (no real record) | **55** | **9** | 19 address-bus-pins **and** `static-high` **and** `rw-pin` **and** `vpp-pin` -- exists in no real record |

**`57` / `7` refutation:** none of the three counting rules reproduces the criterion's `57`/`7`.
Even the loosest synthetic composition (the criterion's own implied recipe) yields **55**, not
`57`. The `state`-alongside-`cmd` explanation for the unaccounted **2-token gap**
(`src/json_parser.c:503` treats `cmd`/`state` as alternates the host never sends together) is
**flagged as unverified** -- the scoping session that produced `57`/`7` was not located.

**The fail-closed overflow path, from source:** `jsmn_alloc_token` (`lib/jsmn/src/jsmn.c:8-16`)
returns `NULL` when the token budget is exhausted (checked at `:79-82`, `:113-116`, `:189-192`),
which the caller converts to `JSMN_ERROR_NOMEM` (`-1`) -- a budget overflow is a silent
**whole-command** failure, never a partial parse.

**The unknown-key skip, the forward-compatibility mechanism, confirmed at the same line numbers as
`158-before-figures.md` (source unchanged by this phase):**
```
src/json_parser.c:510:            // Unknown field -- skip key + value token (forward-compatible with new Python fields)
src/json_parser.c:511:            token_idx += 2;
```

**The conclusion, a budget argument, explicitly NOT arithmetic impossibility:**
`NUMBER_JSNM_TOKENS` is not reducible **without spending the forward-compatibility budget** the
unknown-key skip depends on. `64 -> 56` **is** arithmetically available -- it clears the real
chip-database maximum (50) by 6 and the real-pin-map maximum (51) by 5 -- and would save **`48 B`**
of RAM at today's narrowed `6`-byte-per-token layout (`8 tokens x 6 B`), or would have saved `64 B`
(`8 x 8`) before LAND-05 landed. Cutting to 56 would leave roughly 2-5 tokens of headroom against
the real-pin-map bound, versus today's 13 -- future host-added scalar keys cost 2 tokens each, so
today's headroom is roughly 6 future keys; cutting to 56 would leave about 1.

**The array can only shrink meaningfully via two paths:** LAND-05 (`8 -> 6 B` per token, a real
`-128 B`, no budget change -- **taken this phase**, OD-1) or **v1.28 / Backlog 999.35** (delete the
tokenizer entirely, `-512 B` RAM). This record proposes no step toward the latter.

---

## 10. LAND-08 -- the flakiness record

**Every data point, as an (env, cases, succeeded, suites, duration) row, across the prior corpus
and this phase's own runs:**

| Source | Env | Cases | Succeeded | Suites | Duration |
|---|---|---|---|---|---|
| `155-RESEARCH.md:846` (Pitfall 5, x5 baseline) | `native` | 172 | 172 | -- | ~35 s (x5) |
| `155-RESEARCH.md:846` (flake) | `native` | 172 | 171 | -- | 1:13 |
| `155-RESEARCH.md:846` (flake) | `native` | 158 (2 ERRORED) | -- | -- | 1:44 |
| `156-07-SUMMARY.md:110` | `native` | 172 | 172 | -- | 21.6 s |
| `156-07-SUMMARY.md:110` | `native` | 172 | 172 | -- | 31.6 s |
| `156-07-SUMMARY.md:110` | `native` | 172 | 172 | -- | 32.6 s |
| `157-before-figures.md:247-250` | `native` | 172 | 172 | -- | 19.8 s |
| `157-before-figures.md:247-250` | `native` | 172 | 172 | -- | 25.3 s |
| `157-before-figures.md:247-250` | `native` | 172 | 172 | -- | 54.6 s |
| `158-RESEARCH.md` F-8 | `native` | 184 | 184 | 17 | 53.97 s |
| `158-RESEARCH.md` F-8 | `native` | 184 | 184 | 17 | 22.18 s |
| `158-RESEARCH.md` F-8 | `native_nodevtools` | 184 | 184 | 17 | 61.26 s |
| `158-before-figures.md` S3, run 1 | `native` | 184 | 184 | 17 | 55.035 s |
| `158-before-figures.md` S3, run 2 | `native` | 184 | 184 | 17 | 40.820 s |
| `158-before-figures.md` S3, run 3 | `native` | 184 | 184 | 17 | 38.763 s |
| `158-before-figures.md` S3, run 4 | `native_nodevtools` | 184 | 184 | 17 | 50.987 s |
| **this plan (06), run 1** | `native` | 184 | 184 | 17 | **40.858 s** |
| **this plan (06), run 2** | `native_nodevtools` | 184 | 184 | 17 | **45.317 s** |

**Honest statement:** duration is a **necessary-but-not-sufficient correlate** of the observed
failure class, never a predictor. Long runs have failed before (`155-RESEARCH.md`'s 1:44 case);
long runs have also passed cleanly (this plan's own 45.317 s run, and F-8's 53.97 s/61.26 s runs). A
short run is no guarantee either -- F-8's 22.18 s run was also clean, but so were several runs at
38-55 s. No duration threshold separates pass from fail in the corpus assembled so far. **This
plan's own two runs both reported 184/184/17 with no case-count mismatch, so no re-run for a flake
was needed.**

**The three prohibitions, stated in plain words:**
1. **No suite failure may ever be attributed to a tree change on N=1.** Only a re-run against the
   identical tree can distinguish a flake from a regression.
2. **No wall-clock time may be quoted as evidence of anything** -- not of correctness, not of
   regression, not of improvement.
3. **A single case-count mismatch is never a regression without a re-run.** A count that returns to
   the majority value on re-run is a flake, and the record must say so in those words.

---

## 11. The gate ledger -- all twelve legs

Every leg run this session on the final committed tree (`2ccda8d`), with its expected shape stated
in advance (per `158-VALIDATION.md` and this plan's own action text) before it was run.

| # | Leg | Command | Expected (stated in advance) | Result | CI-invoked? |
|---|---|---|---|---|---|
| 1 | Three cold AVR builds | `rm -rf .pio/build/<env>; pio run -e <env>` x3 | zero `warning:` each; byte-identical to committed `captured_build_v158_*` fixtures | zero warnings; `COLD-MATCHES-FIXTURES` confirmed | yes (`build.yml` `pio run`) |
| 2 | `pio test -e native` | (as shown) | 184/184, 17 suites | `184 test cases: 184 succeeded`, 17 suites (`00:00:40.858`, not evidence) | yes |
| 3 | `pio test -e native_nodevtools` | (as shown) | 184/184, 17 suites | `184 test cases: 184 succeeded`, 17 suites (`00:00:45.317`, not evidence) | yes |
| 4 | `check_build_warnings.py --log ...` | exit 0 | exit **0**, `PASS: uno/uno328pb/leonardo: macro_redefinition=0 (== 0)` | matched | **NO -- local-run** (bare invocation, no args, exits 1 by its own never-vacuous guard -- a pre-existing plan-authoring gap already named in `158-before-figures.md`, restated honestly rather than forced) |
| 5 | `check_no_heap_or_64bit_symbols.py` | exit 0 | exit **0**, `PASS: leonardo/uno/uno328pb(heap=0,64bit=0,anchors=2/2,...)` | matched | **NO -- local-run** |
| 6 | `--policy merge05 --avr-log` | exit 0, 3 negative deltas | exit **0** | `PASS: uno(...[-1872<=788=...]), uno328pb(...[-1874<=788=...]), leonardo(...[-1808<=724=...])` -- three negative flash deltas, three negative RAM deltas (`-139` each) | **NO -- local-run** |
| 7 | `--policy merge05 --rebuild` | exit **0** (LAND-03 flip) | exit **0** | full `PASS:` line, AVR + both native envs (S5 above quotes both shapes) | **NO -- local-run** |
| 8 | default mode | exit **0** (LAND-01 flip) | exit **0** | full `PASS:` line (S3 above quotes both shapes) | **NO -- local-run** |
| 9 | `pytest tests/ -q -o addopts=""` (from `/workspaces/firestarter`) | green, no skipped, count = pre-phase (355) + 5 | green | **360 passed in 19.17s**, `grep -c skipped` = `0` | yes (`build.yml:161`) |
| 10 | host suite (from `/workspaces/firestarter_app`) | green | green | **1976 passed, 1 warning, 32 snapshots, 249.17s**, 0 skipped | yes (host-side CI) |
| 11 | source-contract + convention modules | 5 + 7 green | 12 green | `test_jsmn_token_layout_source_contract_v158.py`: 5 passed; `test_checker_convention.py`: 7 passed | yes (part of `pytest tests/ -v`) |
| 12 | one-sidedness from source | lines 697/709 growth-only; checker byte-unchanged | matched | `697: if flash_delta > allowance:` / `709: if ram_delta > ram_tolerance:`; `git diff 785e644 HEAD -- scripts/check_size_baseline.py` empty | n/a (source read) |

**Legs 4, 5, 6, 7 and 8 are local-run obligations -- in NO CI workflow.** A green CI run on this
branch is not evidence any of them passed. **Both polarity flips (legs 7 and 8) are called out
explicitly above with their before shapes quoted alongside their after shapes** (S3, S5).

---

## 12. The coverage ceilings -- final form

All twelve, updated where this phase moved one:

1. `check_size_baseline.py`, `check_build_warnings.py` and `check_no_heap_or_64bit_symbols.py` are
   invoked by NO CI workflow. Every size gate this phase leans on is a **local-run obligation**.
2. But the checker IS executed in CI by its own paired pytest -- `build.yml:161`, `pytest
   tests/ -v`, on `push: branches: ['**','!beta']`.
3. **RESOLVED this phase: the ARM half of LAND-05 was built successfully on BOTH sides** (pre- and
   post-narrowing, `text`/`data`/`bss`/`dec` recorded in S7). No longer a bare ceiling.
4. LAND-06's runtime half is unmeasurable in this milestone (D-02) -- the decline rests on a size
   measurement plus a coverage gap, never a runtime number.
5. The algorithm-5 page-boundary path has ZERO behavioural native coverage -- established by
   enumeration of all 14 registered cases (S8), corrected from F-6's original one-case claim to two.
6. `sizeof(jsmntok_t)` cannot be asserted in a native test -- AVR gives 6 B, host gives 12 B,
   re-confirmed this session (S7).
7. The native suite is load-flaky (D-04) -- no failure this session, but the corpus (S10) shows
   duration is a necessary-but-not-sufficient correlate, never a predictor.
8. A `/tmp` worktree run of `pytest tests/` silently skips 32 cross-repo legs -- this session's
   `pytest tests/` and host-suite runs were both from their canonical checkouts, never a worktree.
9. `lib/jsmn/src/jsmn.h` carries a dead duplicate implementation, deliberately left unedited
   (OD-6), region-scoped out of the new source-contract gate by construction.
10. LAND-07's conclusion is a budget argument, not an impossibility argument -- `64 -> 56` is
    arithmetically available (S9) and declined on the forward-compatibility budget.
11. Every `file:LINE` citation this phase writes is newly stale. Phase 159 remaps them exactly once
    over the composite diff (D-01, D-05). This phase's own line shifts are itemised in S15.
12. The `firestarter` gitlink in the meta repo is drifted (meta records `2ad5b322`, actual HEAD
    `2ccda8d`) -- pre-existing since Phase 154, operator-gated, **not re-pinned by this phase**.

---

## 13. The corrections ledger -- every row closed out

| # | Source document's claim | What replaces it | Verdict |
|---|---|---|---|
| C-1 | ROADMAP criterion 3 / REQUIREMENTS LAND-03: `cases baseline=141 observed=172` | `observed` is the re-measured current count, **184** (17 suites, both native envs) | **CLOSED** (`158-before-figures.md` S1; re-confirmed on the final tree this session, S1/S3) |
| C-2 | ROADMAP criterion 5 / REQUIREMENTS LAND-05: `-128 B RAM for +30 B flash` | Flash is a **win**: measured `-138 / -138 / -136 B` on `uno` / `uno328pb` / `leonardo`, alongside the `-128 B` RAM | **CLOSED** here (S2, S7 -- plan 02's measurement, re-verified this session) |
| C-3 | ROADMAP criterion 6 / REQUIREMENTS LAND-06: masking costs `+22 B flash` (flat) | `+22 / +24 / +22 B` -- right on `uno`/`leonardo`, **2 B low on `uno328pb`** | **CLOSED** here (S8 -- plan 03's measurement, transcribed since the mask no longer exists in any tree) |
| C-4 | ROADMAP criterion 7 / REQUIREMENTS LAND-07: `57 tokens`, `7 tokens of headroom` | Three bounds: **50/14**, **51/13**, **55/9**. `57` is reproducible by none | **CLOSED** (`158-before-figures.md` S9; re-derived and reconfirmed this session, S9) |
| C-5 | LAND-07's implied argument that 64 is not reducible arithmetically | It **is** reducible (`64 -> 56` clears the real maximum by 5-6); declined on the forward-compatibility budget | **CLOSED** (S9) |
| C-6 | LAND-04 as a single clause | Two clauses: no workflow invokes the checker as a size gate, **and** the checker's own pytest runs in CI at `build.yml:161` | **CLOSED** (`158-before-figures.md` S8; re-confirmed this session, S6) |
| C-7 | `size_baseline.json` `meta.consumed_by` names two consumers | There are **three**: `check_size_baseline.py`, `check_build_warnings.py`, `check_release_assets.py` | **CLOSED** (plan 04, `e730068`, S3) |
| C-8 | `size_baseline.json` `envs_agree_note` quotes `{cases: 151, suites: 17}` | Repaired -- stale, already self-flagged by `meta.native_case_count_revision_260822` | **CLOSED** (plan 04, `e730068`, S3) |
| C-9 | `tests/test_check_size_baseline.py` and `tests/meta_presence.py` both claim no CI leg runs `pytest tests/` on this branch | Both corrected: `build.yml`'s trigger widened to `push: branches: ['**','!beta']` | **CLOSED** (plan 05, `2ccda8d`, S6) |
| C-10 | `tests/test_checker_convention.py`: `FLOOR = 7`; `FIXTURE_FLOOR = 16` | Raised to `FLOOR = 8` (8 checkers ship) and `FIXTURE_FLOOR = 31` (31 `planted_*` entries ship, one more than the pre-phase 30 because plan 04's own new plant landed first) | **CLOSED** (plan 05, `5dca69d`) |
| C-11 | Every prior generation's severance docstring documents "the same four groups", 13 files | This generation authors **4 new files plus 2 updated in place**; Groups 2 and 3 are not needed because no MERGE-05 exemption is authored for a reduction | **CLOSED** (`158-before-figures.md` S7; executed exactly as decided by plan 04, S4) |
| C-12 | LAND-03: the canonical invocation exits 1 "before it ever reports flash" | True of the **report**, not the comparison -- the AVR loop runs first and passes; the native loop appends failures and `_print_fail` returns 1 first | **CLOSED** (`158-before-figures.md` S12; re-confirmed this session by LEG 7's full AVR+native PASS line, S5) |
| C-13 | `157-after-figures.md` S2's / `158-before-figures.md` S2's Leonardo Caterina headroom `3438 B` | `28672 - 25098 = 3574 B` at the final Phase 158 position | **CLOSED** (S2) |

---

## 14. The decisions -- OD-1 through OD-10

- **OD-1 -- LAND-05 TAKEN.** `jsmntok_t` narrows 8 -> 6 B, layout `uint8_t type; uint8_t size; int
  start; int end;`. **Declined:** narrowing `start`/`end` -- twelve `-1` sentinel field references
  on six lines of `jsmn.c` require signed.
- **OD-2 -- LAND-06 DECLINED.** Recorded via the measurement, the two `__udivmodsi4` call sites,
  and the zero behavioural native coverage. **Declined:** editing `src/proms/flash_5v_page.cpp` or
  adding a `test_val_5v_page` boundary case.
- **OD-3 -- LAND-03 FIXED, not carried**, on the axis-split argument. **Declined:** leaving
  `observed=172` (or `141`) uncorrected, or making the count a monotonic floor (cost: gate-behaviour
  change, new fixture pair, planted negative, widened landing phase).
- **OD-4 -- the two false CI-coverage docstrings are CORRECTED** (comment-only, AST-diff verified
  zero assertion/import/constant/def changes). **Declined:** leaving the stale claims in place.
- **OD-5 -- the `tests/test_checker_convention.py` FLOOR carry-forward is CLOSED**, in the same
  commit that reconciles it, with a non-vacuity probe proving a `>=` gate can actually fail.
  **Declined:** re-carrying it a second time into Phase 159.
- **OD-6 -- `jsmn.h`'s dead duplicate implementation is LEFT UNEDITED.** The new gate's region
  slice is the machine-checked reason this is safe (Probe B). **Declined:** removing the
  `#ifndef JSMN_HEADER` dead branch.
- **OD-7 -- the ARM half is verified locally: the toolchain installed on the first attempt, and
  both sides built successfully.** **Declined:** claiming ARM coverage without a build; skipping
  the install attempt entirely.
- **OD-8 -- the `*_v153*` fixture family is retired in place and KEPT.** Only 4 new plus 2 in-place
  fixtures authored. **Declined:** authoring the full 13-file, 4-group severance docket every prior
  generation used.
- **OD-9 (as amended by the orchestrator) -- `ROADMAP.md` and `REQUIREMENTS.md` are never
  regenerated**, and are edited by exactly one plan (07), scoped `Edit` only. **Declined:** leaving
  both documents untouched for the whole phase; regenerating either with a GSD mutation verb. This
  plan (06) leaves both byte-unchanged.
- **OD-10 -- neither the `firestarter` nor the `firestarter_app` gitlink is re-pinned this
  phase.** The drift is recorded with both sha pairs (S1) and handed to Phase 159. **Declined:**
  re-pinning either gitlink now. **Trap named for whoever does re-pin:** `git commit --
  <path>` discards a gitlink `update-index`, so a re-pin must drop the pathspec.

---

## 15. Handoffs

### To Phase 159

- **Citation staleness with per-file line shifts, this phase's own contribution** (source files
  whose line counts moved, measured `wc -l` against `785e644`):

  | File | Old lines | New lines | Shift |
  |---|---|---|---|
  | `lib/jsmn/src/jsmn.h` | 475 | 486 | **+11** |
  | `tests/test_check_size_baseline.py` | 1397 | 1403 | **+6** |
  | `tests/test_checker_convention.py` | 326 | 334 | **+8** |
  | `tests/meta_presence.py` | 134 | 136 | **+2** |
  | `scripts/baseline/size_baseline.json` | 123 | 124 | **+1** |
  | `scripts/baseline/size_baseline_base01.json` | 95 | 96 | **+1** |

  Every `file:LINE` citation in this record and in `158-before-figures.md` was measured against the
  tree at the time of writing and will be remapped **once**, over the composite pre-154 -> post-158
  diff (D-01, D-05) -- not repaired here.
- **The untouched close-blocking staleness marker:** `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md` was read
  only, never edited, removed or treated as resolved by this plan. It remains close-blocking;
  Phase 159 / REMAP-04 owns its removal.
- **Both gitlink sha pairs**, with the pathspec trap: `firestarter` meta-recorded `2ad5b322` vs
  actual `2ccda8d` (drifted, pre-existing since Phase 154); `firestarter_app` meta-recorded
  `38f0d839` matching actual `38f0d839` (not drifted). Whoever re-pins either gitlink must remember
  that `git commit -- <path>` **discards** a gitlink `update-index` -- the commit must be made
  without a pathspec, or the re-pin silently vanishes.

### To plan 07 (the only plan of this phase that edits ROADMAP.md / REQUIREMENTS.md)

**Per-requirement discharge attribution**, each with the section of this record holding its
evidence:

| Requirement | Discharging plan(s) | Section here |
|---|---|---|
| LAND-01 | 04 (re-record), re-verified by 06 | S3 |
| LAND-02 | 04 (severance), re-verified by 06 | S4 |
| LAND-03 | 05 (axis fix), re-verified by 06 | S5 |
| LAND-04 | 01 (discovery), 05 (docstring fix), 06 (record) | S6 |
| LAND-05 | 02 (narrowing + ARM), re-verified by 06 | S7 |
| LAND-06 | 03 (decline), 06 (record -- discharges by record alone) | S8 |
| LAND-07 | 01 (derivation), 06 (record -- discharges by record alone) | S9 |
| LAND-08 | 01 (evidence), 06 (record -- discharges by record alone) | S10 |

**The three figures plan 07 must scope-correct in place, each with its correction id:**
1. ROADMAP criterion 3 / REQUIREMENTS LAND-03 -- the stale observed native count `172` -> `184`
   (**C-1**).
2. ROADMAP criterion 6 / REQUIREMENTS LAND-06 -- the flat mask cost `+22 B` -> `+22 / +24 / +22 B`
   (**C-3**).
3. ROADMAP criterion 7 / REQUIREMENTS LAND-07 -- the token count and headroom `57 tokens` /
   `7 tokens of headroom` -> the three derived bounds `50/14`, `51/13`, `55/9` (**C-4**, **C-5**).

**The `**Measured**` line's figures:** per-target cold-to-cold flash delta `-138 / -138 / -136 B`
(`uno` / `uno328pb` / `leonardo`), RAM saving `-128 B` on all three, entirely attributed to LAND-05
(S2).

**The ARM outcome, in this record's own words:** "LAND-05's ARM half is verified locally, not
merely ceiling-recorded -- the toolchain install succeeded on the first attempt, and both the
pre-narrowing and post-narrowing `py32f071` builds succeeded" (S7). Plan 07 must not imply the
other branch (a failed install / ceiling-only record) occurred.

**The floor carry-forward closure, as a trailing note:** the named `tests/
test_checker_convention.py` `FLOOR`/`FIXTURE_FLOOR` carry-forward (OD-5) is closed in this same
phase (plan 05) and must not be carried forward into Phase 159's own scope.

---

## 16. Self-verification of this record

Every figure in this file can be re-derived from `/workspaces/firestarter` at commit `2ccda8d`
(or from a fresh `git checkout 2ccda8d`, since this plan edited no tracked file under
`firestarter/`):

- S2/S3's cold AVR figures: `rm -rf .pio/build/<env> && pio run -e <env>` for each of `uno`,
  `uno328pb`, `leonardo`, reading the trailing `Flash:`/`RAM:` lines.
- S3's native figures: `pio test -e native` and `pio test -e native_nodevtools`, reading each run's
  own trailing `N test cases: N succeeded in HH:MM:SS.mmm` line.
- S4's one-sidedness and severance: `sed -n '697p;709p' scripts/check_size_baseline.py`; `git diff
  785e644 HEAD -- scripts/check_size_baseline.py` (empty); `ls tests/fixtures | grep 'v153\|v158'`.
- S5's axis-split licence: `python3 -c "import json; print(json.load(open('scripts/baseline/
  size_baseline_base01.json'))['meta']['native_inventory_axis_phase158'])"`.
- S6's LAND-04 clauses: `grep -rn check_size_baseline .github/` (all three repos); `grep -n
  "pytest tests/" .github/workflows/build.yml`.
- S7's `sizeof` probes: compile a one-line `char total[sizeof(jsmntok_t)];` translation unit
  against `lib/jsmn/src/jsmn.h` with both `avr-gcc -mmcu=atmega328p -Os` and host `gcc`, read back
  with `nm --print-size`.
- S7's `avr-nm`/`avr-objdump` division-site probes: `avr-nm --print-size .pio/build/uno/
  firestarter_uno.elf | grep flash_5v_page_write_execute`, then `avr-objdump -d
  --start-address=<addr> --stop-address=<addr+size> ... | grep -c __udivmodsi4`.
- S9's token bounds: `python3 /tmp/gsd-158/land07_tokens.py` -- reads only `firestarter_app`'s
  `EpromDatabase` and `pinouts.json`/`chip_database.json`, read-only, no file modified by running
  it.
- S11's gate ledger: every command is given verbatim in its own row.

`git -C /workspaces/firestarter status --porcelain` was empty before and after every measurement
step in this session, and remains empty at the time this record was written.
