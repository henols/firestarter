---
title: Before-figures record — milestone v1.33, Phase 158 (Residual Optimizations + Cold Baseline Re-Record, firmware-only)
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "01"
measured: 2026-08-24
status: AUTHORITATIVE — this file is the ONLY source for Phase 158's before-half figures. Every AVR
  figure below is COLD (`rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, never
  `--rebuild`). This plan's own plan 04 re-records `scripts/baseline/size_baseline.json` to the
  post-change cold figures, which invalidates the AVR figures captured here as a source of the
  live baseline's post-158 content — no later plan of this phase re-derives its pre-phase position
  from anywhere but this file.
supersedes: >
  ROADMAP.md §Phase 158 criteria 3 ("cases baseline=141 observed=172"), 5 ("−128 B RAM for +30 B
  flash"), 6 ("masking costs +22 B flash (flat)") and 7 ("57 tokens", "7 tokens of headroom");
  REQUIREMENTS.md LAND-03 ("observed=172"), LAND-05 ("+30 B flash"), LAND-06 ("+22 B flash (flat)")
  and LAND-07 ("57 tokens", "7 tokens of headroom") prose, wherever they state a figure this file
  corrects (C-1 through C-13; C-2, C-3 and C-13 remain open here, closed in
  `158-after-figures.md`, since their replacement values are only measurable after LAND-05/06 land
  and after the final cold rebuild). Neither ROADMAP.md nor REQUIREMENTS.md is edited by this
  plan or by any plan of this phase except plan 07, which alone applies scoped `Edit` replacements
  (OD-9 as amended); the correction lives here per the Phase 155/156/157 convention.
requirements: [LAND-01, LAND-02, LAND-03, LAND-04, LAND-05, LAND-06, LAND-07, LAND-08]
---

# Before-figures record — v1.33 Phase 158

Every number in this file was measured on a **clean, unedited** `firestarter` working tree during
this plan's session, run from `/workspaces/firestarter` (the canonical checkout). Each number
carries the verbatim command that produced it. Every AVR flash/RAM figure is labelled **COLD** —
produced by `rm -rf .pio/build/<env>` followed by exactly one `pio run -e <env>`, never
`pio run -t clean` and never `check_size_baseline.py --rebuild` (Pitfall 6: `_rebuild_avr` uses
the older, non-mandated recipe). This task edited no tracked file under `firestarter/`; the tree
was proven clean before AND after every step (§1). No file under `firestarter_app/` was modified
either — LAND-07's derivation only *reads* that repo's data files.

This document's own `file:LINE` citations were measured against the current post-Phase-157 tree
(HEAD `785e644`) and will themselves be remapped exactly once by Phase 159 over the composite diff
(REMAP-01…04, D-01/D-05). No citation in this record is repaired here.

---

## 1. Git anchors

| Field | Value |
|---|---|
| `FW_PRE_SHA` (full) | `785e644bacbe128de813407f0e6e357c71164836` |
| `FW_PRE_SHA` (abbrev) | `785e644` |
| Subject | `test(157-05): cap read-strobe-us, tighten both cap assertions, round-trip every table row` |
| Branch (firmware + meta) | `gsd/v1.33-source-hygiene-firmware-size-reduction` |
| Meta HEAD | `6000b2ff90e173d424b50b1e0948a18c7244acba` |
| `git -C /workspaces/firestarter status --porcelain` before | empty (verified) |
| `git -C /workspaces/firestarter status --porcelain` after | empty (verified) |
| `firestarter` gitlink in meta | `2ad5b322a37ba4a88afd09cc946f5c4114e51483` — **drifted** against the actual submodule HEAD (`785e644`); pre-existing since Phase 154, operator-gated, **not re-pinned by this phase** (OD-10, ceiling 12) |
| `firestarter_app` gitlink in meta | `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2` — matches the actual submodule HEAD at measurement time; not touched by this phase |

Commands: `git -C /workspaces/firestarter rev-parse HEAD`; `git -C /workspaces/firestarter log -1
--format=%s`; `git -C /workspaces/firestarter status --porcelain`; `git -C /workspaces rev-parse
HEAD`; `git -C /workspaces ls-tree HEAD firestarter firestarter_app`; `git -C /workspaces/firestarter
rev-parse HEAD` again for the gitlink comparison.

---

## 2. The pre-phase cold ledger

Recipe per env: `rm -rf .pio/build/<env>` then exactly one `pio run -e <env>`, teed to
`/tmp/gsd-158/pre-cold-<env>.log`. Every figure below is **COLD**.

| Env | Flash used (COLD) | Flash total | RAM used (COLD) | RAM total | `warning:` count |
|---|---|---|---|---|---|
| `uno` | **23090 B** | 32768 B | **1562 B** | 2048 B | 0 |
| `uno328pb` | **23138 B** | 32768 B | **1568 B** | 2048 B | 0 |
| `leonardo` | **25234 B** | 32768 B | **2003 B** | 2560 B | 0 |

The **recorded, stale** `size_baseline.json` `avr_targets` values, for contrast (unchanged since
Phase 155, now superseded by the row above):

| Env | Flash used (stale, recorded) | RAM used (stale, recorded) |
|---|---|---|
| `uno` | 25548 B | 1575 B |
| `uno328pb` | 25598 B | 1581 B |
| `leonardo` | 27630 B | 2016 B |

The staleness is attributed to Phases 155–157 (each landed a source-shrinking change without
re-recording `size_baseline.json`'s live `avr_targets`; `157-before-figures.md`'s own frontmatter
names this file, `158-before-figures.md`, as the plan that would re-anchor it — LAND-01 does so in
plan 04).

**Leonardo's Caterina headroom against the `28672` B bootloader cliff:** `28672 − 25234 = 3438 B`.
This is **byte-identical** to `157-after-figures.md` §2's own recorded `3438 B` figure at this same
commit (`785e644`) — it **confirms**, not supersedes, that figure (C-13 stays open pending plan
06's final measurement, since LAND-05/06 will move `leonardo`'s flash figure and therefore this
headroom).

Commands: `rm -rf .pio/build/uno && pio run -e uno > /tmp/gsd-158/pre-cold-uno.log 2>&1` (and the
`uno328pb` / `leonardo` analogues); `grep -E 'Flash:|RAM:' /tmp/gsd-158/pre-cold-<env>.log`;
`grep -c 'warning:' /tmp/gsd-158/pre-cold-<env>.log`.

---

## 3. The native position and LAND-08's evidence

**This plan's four new same-tree timed runs, all at `785e644`:**

| Run | Env | Cases | Succeeded | Suites | Duration |
|---|---|---|---|---|---|
| 1 | `native` | 184 | 184 | 17 | **55.035 s** |
| 2 | `native` | 184 | 184 | 17 | **40.820 s** |
| 3 | `native` | 184 | 184 | 17 | **38.763 s** |
| 4 | `native_nodevtools` | 184 | 184 | 17 | **50.987 s** |

All four runs report the **same** case/succeeded/suite triple (184/184/17). No case-count mismatch
occurred this session, so no re-run-for-a-flake was needed — but the duration still spread
**1.42×** (38.763 s to 55.035 s) across three identical-tree `native` runs, which is itself the
D-04 evidence: an unchanged tree produces a materially different wall time from run to run.

**Prior recorded data points, carried forward from this milestone's own records** (not
re-measured here, cited for continuity):

- `155-RESEARCH.md:846` (Pitfall 5): 172/172 at ~35 s (×5), 171/172 once at 1:13, a
  158-cases-with-2-ERRORED result once at 1:44 — the original observation that failure correlates
  with run duration, not tree content.
- `157-before-figures.md:247-250`: three `native` runs at 19.8 s, 25.3 s, 54.6 s — 2.8× spread,
  172/172 unchanged.
- `156-07-SUMMARY.md:110`: three runs at 21.6 s, 31.6 s, 32.6 s, all 172/172.
- `158-RESEARCH.md` F-8: three new same-tree data points at the post-157 position — `native`
  53.97 s and 22.18 s (both 184/184/17), `native_nodevtools` 61.26 s (184/184/17) — a 2.8× spread
  with an identical result, demonstrating the *converse*: a long run is not itself a failure.

**The three prohibitions, stated in plain words, as this record's own rule:**

1. **No suite failure may ever be attributed to a tree change on N=1.** A single divergent run is
   an observation, not a verdict; only a re-run against the identical tree can distinguish a flake
   from a regression.
2. **No wall-clock time may be quoted as evidence of anything** — not of correctness, not of
   regression, not of improvement. Duration is measured and recorded here only because LAND-08
   itself is a record about duration's *unreliability* as a signal.
3. **A single case-count mismatch is never a regression without a re-run.** A count that returns
   to the majority value on re-run is a flake, and the record must say so in those words (none
   occurred this session; the rule is stated for the benefit of any future re-run that does see
   one).

**Honest form:** duration is a **necessary-but-not-sufficient correlate** of the observed failure
class, never a predictor. Long runs have failed before (155-RESEARCH.md's 1:44 case); long runs
have also passed cleanly (this session's 55.035 s run, and F-8's 53.97 s/61.26 s runs). A short run
is no guarantee either — F-8's 22.18 s run was also clean, but so were three of this session's four
runs at 38–55 s. No duration threshold separates pass from fail in the corpus assembled so far.

Commands: `pio test -e native > /tmp/gsd-158/pre-native-run{1,2,3}.log 2>&1`;
`pio test -e native_nodevtools > /tmp/gsd-158/pre-native-nodevtools.log 2>&1`; the case/succeeded/duration
triple is read from each log's own trailing `================ N test cases: N succeeded in
HH:MM:SS.mmm ================` line; the suite count is `grep -oE 'test/native/avr/[a-zA-Z0-9_]+'
<log> | sort -u | wc -l`.

---

## 4. The gate ledger at this position, all legs

| Leg | Command | Exit | Salient output | CI-invoked? |
|---|---|---|---|---|
| `check_build_warnings.py` (bare, no args) | `python3 scripts/check_build_warnings.py` | **1** | `FAIL: no envs examined -- supply --log ENV=PATH or --rebuild (never-vacuous guard: a warning gate that examined nothing must not pass)` | No — local-run obligation |
| `check_build_warnings.py` (`--log` against the three cold AVR logs) | `python3 scripts/check_build_warnings.py --log uno=... --log uno328pb=... --log leonardo=...` | **0** | `PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0)` | No — local-run obligation |
| `check_no_heap_or_64bit_symbols.py` | `python3 scripts/check_no_heap_or_64bit_symbols.py` | **0** | `PASS: leonardo(heap=0,64bit=0,anchors=2/2,...), uno(...), uno328pb(...)` | No — local-run obligation |
| MERGE-05 canonical `--avr-log` | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=...` | **0** | `PASS: uno(flash=23090/32768[-1734<=788=band64+exempt96+seam210+lock288+erase130],ram=1562/2048[-11<=2=seam2]), uno328pb(flash=23138/32768[-1736<=788=...],ram=1568/2048[-11<=2=seam2]), leonardo(flash=25234/32768[-1672<=724=band0+exempt96+seam210+lock288+erase130],ram=2003/2560[-11<=2=seam2])` | No — local-run obligation |
| MERGE-05 canonical `--rebuild` | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` | **1** | Exactly two failure lines, both `cases baseline=141 observed=`, **no** AVR `flash_used`/`ram_used` line:<br>`FAIL:`<br>`  native: cases baseline=141 observed=184`<br>`  native_nodevtools: cases baseline=141 observed=184` | No — local-run obligation |
| Default mode (no `--policy`) against `size_baseline.json`, fed this session's own cold AVR logs plus the native run-1/nodevtools logs | `python3 scripts/check_size_baseline.py --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... --native-log native=... --native-log native_nodevtools=...` | **1 — RED, exactly as expected** | Every failing line, verbatim:<br>`FAIL:`<br>`  uno: flash_used baseline=25548 observed=23090`<br>`  uno: ram_used baseline=1575 observed=1562`<br>`  uno328pb: flash_used baseline=25598 observed=23138`<br>`  uno328pb: ram_used baseline=1581 observed=1568`<br>`  leonardo: flash_used baseline=27630 observed=25234`<br>`  leonardo: ram_used baseline=2016 observed=2003`<br>`  native: cases baseline=172 observed=184`<br>`  native_nodevtools: cases baseline=172 observed=184` | No — local-run obligation. **Plan 04 must flip this exact leg to GREEN** by re-recording `size_baseline.json`'s `avr_targets` and `native_envs` to the cold figures in §2/§3 above. |
| `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter` | (as shown) | **0** | `355 passed in 15.50s` — the word `skipped` does **not** appear (`grep -c skipped` = `0`), proving the 32 cross-repo legs of `tests/test_flash_path_record_sync.py` actually ran (F-12) | **Yes** — `build.yml:161`, `pytest tests/ -v`, on `push: branches: ['**', '!beta']` |
| `python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""` | (as shown) | **0** | `14 passed in 0.97s` | Indirectly, as part of the `pytest tests/ -v` step above |

**A discrepancy this record states plainly, per this phase's own honesty convention:** the plan
task that authored this measurement expected the *bare* `check_build_warnings.py` invocation (no
`--log`/`--rebuild`) to exit `0`. It does not — the script's own documented never-vacuous guard
(mirroring `check_size_baseline.py`'s identical guard) refuses to report success when it examined
zero envs, and a bare invocation supplies neither `--log` nor `--rebuild`, so it examines zero
envs by construction. The row above records the **actual observed behaviour** (exit 1, "no envs
examined") alongside the **correct invocation's** actual behaviour (exit 0, all three AVR envs
clean) rather than silently forcing the plan's original expectation to appear true.

Commands are given verbatim in each row; every log path is under `/tmp/gsd-158/`.

---

## 5. The one-sidedness, quoted from source and from the gate

`scripts/check_size_baseline.py`, lines `697` and `709`, quoted verbatim:

```
697:    if flash_delta > allowance:
709:    if ram_delta > ram_tolerance:
```

Both are **growth-only** comparisons: a negative delta (a size *reduction*) can never fail either
clause, no matter how large the reduction. The canonical `--avr-log` invocation's verbatim
`PASS:` line (§4) is the **observed consequence**: all three targets report a **negative** flash
delta (`-1734`, `-1736`, `-1672`) against a **positive** allowance (`788`, `788`, `724`), and all
three report a negative RAM delta (`-11`) against a positive tolerance (`2`).

**No MERGE-05 exemption is authored or widened by this phase (D-03).** A reduction needs none. The
six MERGE-05 literals, read from the checker's source this session, that must stay byte-unchanged
at phase end:

| Literal | Value | Line |
|---|---|---|
| `MERGE05_UNO_CLASS_FLASH_BAND` | `64` | `:155` |
| `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` | `96` | `:199` |
| `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES` | `210` | `:257` |
| `MERGE05_LOCK_STATUS_READ_EXEMPTION_BYTES` | `288` | `:331` |
| `MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES` | `130` | `:421` |
| `MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES` | `2` | `:465` |

(The leonardo `band = 0` inline literal at `:607` is the unnamed sixth-in-spirit band value the
module's own docstring calls out separately; it is not itself one of the six *named* module-level
constants and stays `0` regardless.)

Commands: `sed -n '697p;709p' scripts/check_size_baseline.py`; `grep -n "MERGE05_" scripts/check_size_baseline.py`.

---

## 6. The four legs that redden, and the four that do not

**The four legs that redden on a re-record**, each located by reading `tests/test_check_size_baseline.py`
in this session (not copied from `158-RESEARCH.md`, whose own line numbers may have shifted):

| Test | Line (this session) | Fixture family it currently reads | Remedy |
|---|---|---|---|
| `test_clean_avr_all_three_envs_pass` | `:518` | `captured_build_v153_{uno,uno328pb,leonardo}.log` | Plan 04 authors `captured_build_v158_{uno,uno328pb,leonardo}.log` (this session's own three cold logs, committed byte-for-byte) and repoints this leg at the new family. |
| `test_clean_native_both_envs_pass` | `:562` | `captured_test_native_summary.log`, `captured_test_native_nodevtools_summary.log` | Plan 04 updates these two fixtures **in place** (the established convention for this pair — they are the sole readers, so no severance is needed), to the 184/184/17 figures in §3. |
| `test_planted_flash_regression_flips_checker_to_failure` | `:612` | `planted_size_baseline_flash_regression_v153.log` | Plan 04 authors `planted_size_baseline_flash_regression_v158.log`, derived from the new `captured_build_v158_leonardo.log` with the same `+512 B` offset every prior generation of this fixture has used since Phase 123, and repoints this leg. |
| `test_default_mode_is_unchanged_by_the_new_flag` | `:1362` | `captured_build_v153_{uno,uno328pb,leonardo}.log` | Plan 04 repoints this leg at the new `captured_build_v158_*.log` family; the `<=64` substring assertion itself is unchanged. |

**The legs that read BASE-01 or the checker's own source and therefore do NOT move:**
`test_base01_is_not_re_anchored_by_the_new_exemption` (`:1108`) reads only
`scripts/baseline/size_baseline_base01.json`'s own frozen figures and the checker's source text —
it is orthogonal to any `*_v158*` fixture and this phase authors no new MERGE-05 exemption, so it
stays green unmoved. The three surviving policy-plant legs (§ below) also stay green unmoved,
because they read `size_baseline_base01.json` (frozen) rather than the live `size_baseline.json`.

**The four porcelain legs — a different set, with a different cause, recorded separately:**
`tests/test_requirement_case_mapping_v131.py`'s `test_planted_renamed_case_is_detected` and
`test_planted_emptied_scan_root_fails_the_non_vacuity_leg` (both assert `git status --porcelain`
empty via `_git_porcelain(_REPO_ROOT)` after their own planted-and-restored mutation), and
`tests/test_trace_segment_exhaustiveness_v131.py`'s `test_planted_unclassifiable_entry_is_located`
and `test_planted_delete_and_duplicate_defeats_a_count_only_check` (same `_git_porcelain` pattern).
**These four redden for ANY dirty file in the firmware working tree**, regardless of whether
`size_baseline.json` moved — their cause is unrelated to LAND-01's re-record, and conflating the
two sets is named as **Pitfall 4** in this phase's own research. At this measurement position the
firmware tree is clean (`git -C /workspaces/firestarter status --porcelain` empty, §1), so all four
porcelain legs currently pass; they will only redden if a later plan of this phase leaves the
firmware tree dirty mid-task, which no plan does (every plan commits before its own verify step).

Commands: `grep -n "def test_clean_avr_all_three_envs_pass\|def test_clean_native_both_envs_pass\|def test_planted_flash_regression_flips_checker_to_failure\|def test_default_mode_is_unchanged_by_the_new_flag\|def test_base01_is_not_re_anchored_by_the_new_exemption" tests/test_check_size_baseline.py`;
`grep -n "porcelain" tests/test_requirement_case_mapping_v131.py tests/test_trace_segment_exhaustiveness_v131.py`.

---

## 7. The severance plan, and why it is 4 plus 2 rather than 13

**`*_v158*` membership (4 new files):**
- `captured_build_v158_uno.log`, `captured_build_v158_uno328pb.log`, `captured_build_v158_leonardo.log`
  (plan 04; this session's own three cold logs, committed byte-for-byte).
- `planted_size_baseline_flash_regression_v158.log` (plan 04; derived from the new leonardo cold
  log with the standing `+512 B` offset).

**Updated in place (2 files, not severed):** `captured_test_native_summary.log` and
`captured_test_native_nodevtools_summary.log` — the established convention for this specific pair
since Phase 149 Plan 07 and Plan 151-10, because `test_clean_native_both_envs_pass` is the **sole**
reader of either fixture, so nothing else depends on the old figures staying frozen. The licence
for this, quoted from the leg's own docstring (`tests/test_check_size_baseline.py:565-586`):
*"No severance needed here, unlike the AVR captured_build_*.log family: this is the ONLY leg in
this module that consumes either native summary fixture."*

**`*_v153*` disposition: retired in place, and KEPT.** The prior generation's three
`captured_build_v153_*.log` files and the one `planted_size_baseline_flash_regression_v153.log`
are left on disk, unmodified and unread by any leg once plan 04 repoints the four reddening legs
above — exactly Pattern 1 (fixture severance, never re-anchoring or deleting).

**Groups 2 and 3 (from prior generations' own severance dockets) are explicitly NOT needed this
generation**, because **no MERGE-05 exemption is authored for a reduction** (C-11, OD-8, D-03):
the three surviving `planted_size_baseline_policy_{uno_over_band,leonardo_growth,ram_moved}_v153.log`
plants derive their expected-failure position from `allowance + 1` against the SAME six MERGE-05
literals (§5), none of which moves this phase — so their derivation basis is untouched and they
need no re-plant. This generation is therefore **4 new files plus 2 updated in place**, not the
**13 files across 4 groups** every prior generation's docstring names.

Commands: `ls tests/fixtures/ | grep 'v153\|v158'`; `python3 -m pytest tests/test_check_size_baseline.py -k "fires_on_uno_class_over_band or fires_on_leonardo_growth or fires_on_ram_move" -q -o addopts=""` → `3 passed, 11 deselected`.

---

## 8. LAND-04, both clauses

**Clause 1 — no `.github/` workflow invokes `check_size_baseline.py` as a size gate.**

| Command | Output | Exit |
|---|---|---|
| `grep -rn "check_size_baseline" .github/` (in `/workspaces/firestarter`) | (none) | **1** |
| `grep -rn "check_size_baseline" .github/` (in `/workspaces`, meta) | (none) | **1** |
| `grep -rn "check_size_baseline" .github/` (in `/workspaces/firestarter_app`) | (none) | **1** |

`ls scripts/check_*.py` yields exactly **8** files: `check_build_warnings.py`,
`check_cmake_manifest.py`, `check_erase_no_vpp.py`, `check_landing_range.py`,
`check_no_heap_or_64bit_symbols.py`, `check_orphan_provisional.py`, `check_release_assets.py`,
`check_size_baseline.py`. Of these, **exactly one** — `check_release_assets.py` — is invoked by
any workflow (`beta-build.yml:327`, `run: python3 scripts/check_release_assets.py`). The other
**seven are local-run obligations**, invoked by no `.github/workflows/*.yml` step:
`check_build_warnings.py`, `check_cmake_manifest.py`, `check_erase_no_vpp.py`,
`check_landing_range.py`, `check_no_heap_or_64bit_symbols.py`, `check_orphan_provisional.py`,
`check_size_baseline.py`.

**Clause 2 — the checker IS nonetheless executed in CI by its own paired pytest.**
`build.yml:161` runs `pytest tests/ -v`, ungated by any `if:` (it sits above the "PUBLISH
BOUNDARY" comment at `build.yml`), and `build.yml`'s `on:` block (`:16-30`) filters
`push: branches: ['**', '!beta']` — `'**'` matches every branch including this milestone branch,
and only `beta` is excluded. `beta-build.yml:134` runs the sibling leg, `pytest tests/ -v`, on
`push: branches: [beta]` (that workflow's own trigger). **Consequence, stated in one sentence:**
re-recording `size_baseline.json` without severing the fixtures in the same commit turns CI red on
this branch, because `tests/test_check_size_baseline.py` runs as a subprocess inside that pytest
step and reads the moved live baseline against the old fixture logs.

**Exhaustive CI-leg enumeration for this branch** (`build.yml`, since `py32f071.yml`'s own
`push: branches: ['**']` also fires here): `pio test -e native` (`:122`), `pio test -e
native_nodevtools` (`:128`), `pytest tests/ -v` (`:161`), `pio run` (the full AVR build, after the
publish boundary but still unconditional), and the separate `py32f071.yml` ARM build workflow.
**There is nothing else** — no workflow on this branch runs `check_size_baseline.py`,
`check_build_warnings.py`, or any of the other six local-run-obligation checkers directly.

Commands: `grep -rn "check_size_baseline" .github/` (all three repos); `ls scripts/check_*.py |
wc -l`; `grep -n "pytest tests/" .github/workflows/build.yml .github/workflows/beta-build.yml`;
`grep -rln "check_release_assets" .github/workflows/`.

---

## 9. LAND-07, the token arithmetic

**The budget and its consumer:** `include/json_parser.h:17` —
`#define NUMBER_JSNM_TOKENS 64`; `src/firestarter.cpp:54` —
`static jsmntok_t tokens[NUMBER_JSNM_TOKENS];` (`64 × 8 = 512 B` today, `64 × 6 = 384 B` if
LAND-05 lands); `src/firestarter.cpp:57` — the `jsmn_parse` call site.

**Overflow path, from source, fail-closed:** `jsmn_alloc_token` (`lib/jsmn/src/jsmn.c:8-16`)
returns `NULL` when the token budget is exhausted (`if (parser->toknext >= num_tokens) return
NULL;` — checked at `:79-82` and `:113-116` and `:189-192`), which the caller converts to
`JSMN_ERROR_NOMEM` (`-1`). This rejects the **whole command** — a budget overflow is a silent
whole-command failure, never a partial parse.

**The unknown-key skip, the forward-compatibility mechanism:** `src/json_parser.c:510-511`
(top-level, inside the main command parser) —
```
333:            // Unknown field — skip key + value token (forward-compatible with new Python fields)
334:            token_idx += 2;
```
and its nested analogue for `bus-config`'s inner keys at `src/json_parser.c:455-458`. This is the
mechanism by which the host can add a wire field without a firmware release.

**Inputs, read this session:** `pinouts.json` record count = **15**; maximum
`address-bus-pins` across all records = **19** (`DIP32_STD`); maximum `static-high-pins` across
all records = **1** (several 24-pin records). Script: `/tmp/gsd-158/land07_tokens.py`, run via
`python3 /tmp/gsd-158/land07_tokens.py`, implementing jsmn's own counting rule (one token per `{`,
per `[`, per string, per primitive, per `lib/jsmn/src/jsmn.c:170-355`). Verbatim output:

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

**Three bounds, each with its own scope (matches this phase's C-4 exactly):**

| Bound | Value | Headroom vs 64 | Input that produces it |
|---|---|---|---|
| Observed maximum over the real chip database | **50** | **14** | The `W29C020, W29C020C, W29C022` family, swept through `database.py`'s `convert_to_programmer` plus every runtime key `eprom_operations.py` can merge (`cmd`, `flags`, `address`, `read-settling-delay`, `read-strobe-us`) |
| Maximum over any real pin map, with every optional scalar present | **51** | **13** | `DIP32_27C020` (18 address-bus-pins + `rw-pin` + `vpp-pin`) plus all 12 top-level scalars |
| Field-wise-maximum synthetic bound | **55** | **9** | 19 address-bus-pins **and** a `static-high` entry **and** `rw-pin` **and** `vpp-pin` — a combination that exists in **no real record** (no 19-bus-pin map in `pinouts.json` carries a `static-high-pins` entry) |

**The criterion's `57 tokens` / `7 tokens of headroom` is reproducible by none of the three
counting rules above.** Even the loosest synthetic composition — exactly the recipe the criterion
itself implies ("largest address-bus-pins and a static-high entry, plus every optional wire key")
— yields **55**, not 57. The `state`-alongside-`cmd` explanation for the 2-token gap
(`src/json_parser.c:503` treats `cmd`/`state` as alternates the host never sends together) is
flagged here as **unverified** — the scoping session that produced `57`/`7` was not located — and
its failure would not disturb any of the three derived bounds above.

**The conclusion, stated as the evidence supports — a budget argument, explicitly NOT arithmetic
impossibility:** `NUMBER_JSNM_TOKENS` is not reducible **without spending the forward-compatibility
budget the unknown-key skip depends on**. `64 → 56` **is** arithmetically available — it clears the
real chip-database maximum (50) by 6 and the real-pin-map maximum (51) by 5 — and would save
`64 B` of RAM today (`8 × 8`) or `48 B` after LAND-05 lands (`8 × 6`). Cutting to 56 leaves only 2
tokens of headroom against the real-pin-map bound (13 − 6 = 7 short of that bound's own 13, i.e.
`56 − 51 = 5` remaining, not the `13` today's `64` carries) — future host-added scalar keys cost 2
tokens each, so today's 13-token headroom (bound b) is **6 future host-added scalar keys**; cutting
to 56 leaves roughly 2. `pinouts.json` is host data and it grows: a future 40-pin map, or a pin map
combining 19 address lines with a `static-high` entry, reaches the synthetic 55 immediately. **The
array can only shrink meaningfully via two paths:** LAND-05 (`8 → 6 B` per token, a real `−128 B`
with no budget change — this phase's own decision, OD-1) or **v1.28 / Backlog 999.35** (delete the
tokenizer entirely, `−512 B` RAM) — and this record proposes no step toward the latter.

Commands: `python3 /tmp/gsd-158/land07_tokens.py`; `grep -n "NUMBER_JSNM_TOKENS" include/json_parser.h`;
`sed -n '8,16p;79,82p' lib/jsmn/src/jsmn.c`; `sed -n '305,335p;449,458p' src/json_parser.c`.

---

## 10. The coverage ceilings

All twelve, verbatim from this plan's own header, restated here per this phase's convention that
they appear in every plan, every SUMMARY and both phase records:

1. `check_size_baseline.py`, `check_build_warnings.py` and `check_no_heap_or_64bit_symbols.py` are
   invoked by NO CI workflow. Every size gate this phase leans on is a **local-run obligation**. A
   green CI run is not evidence that any of them passed. This is LAND-04's whole content.
2. But the checker IS executed in CI by its own paired pytest. `build.yml:161` runs `pytest
   tests/ -v`, ungated by any `if:`, and `build.yml`'s trigger is `push: branches: ['**','!beta']`
   — it fires on this milestone branch. LAND-04's honest statement has **two clauses**.
3. The ARM half of LAND-05 is unverified locally unless the toolchain install succeeds.
   `arm-none-eabi-gcc` and `cmake` are both absent from this devcontainer; `platform/py32f071/CMakeLists.txt`
   compiles the same `lib/jsmn/src/jsmn.c`, and `py32f071.yml` is the loud gate at push time. Never
   claim ARM coverage that was not built.
4. LAND-06's runtime half is unmeasurable in this milestone. D-02 forbids a bench criterion, so
   the decline rests on a size measurement plus a coverage gap and never on a runtime number.
5. The algorithm-5 page-boundary path has ZERO behavioural native coverage. The only case in
   `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` that executes
   `flash_5v_page_write_execute` drives a 4-byte write, which never crosses a 64-byte boundary.
6. `sizeof(jsmntok_t)` cannot be asserted in a native test. AVR gives 6 B, the host gives 12 B.
   The RAM saving is witnessed by the linker's `RAM: used N` line and by `avr-nm`, never by a
   native `sizeof`.
7. The native suite is load-flaky (D-04). No suite failure may be attributed to a tree change on
   N=1, and wall time carries no signal on its own.
8. A `/tmp` worktree run of `pytest tests/` silently skips 32 cross-repo legs (355 versus 323+32,
   both measured). Gate-purpose runs happen from `/workspaces/firestarter`.
9. `lib/jsmn/src/jsmn.h` carries a dead duplicate implementation under `#ifndef JSMN_HEADER` while
   `#define JSMN_HEADER` precedes it — it compiles in no translation unit but is live text to a
   naive grep.
10. LAND-07's conclusion is a budget argument, not an impossibility argument. The derived headroom
    is 13 tokens (real-pin-map bound), so `64 -> 56` is arithmetically available; it is declined
    because the unknown-key skip's forward-compatibility budget is load-bearing.
11. Every `file:LINE` citation this phase writes will be newly stale. Phase 159 remaps them
    exactly once over the composite diff (D-01, D-05). This phase runs no remap and repairs no
    citation.
12. The `firestarter` gitlink in the meta repo is drifted (meta tracks `2ad5b322`, the submodule
    HEAD is `785e644` or later) — pre-existing since Phase 154, operator-gated, and **not
    re-pinned by this phase**.

---

## 11. The decisions

- **OD-1 -- LAND-05 TAKEN.** `jsmntok_t` narrows 8 → 6 B, layout `uint8_t type; uint8_t size; int
  start; int end;`. **Declined:** narrowing `start`/`end` -- twelve `-1` sentinel field references
  on six lines of `jsmn.c` require signed.
- **OD-2 -- LAND-06 DECLINED.** Recorded via the measurement, the two `__udivmodsi4` call sites,
  and the zero behavioural native coverage. **Declined:** editing `src/proms/flash_5v_page.cpp` or
  adding a `test_val_5v_page` boundary case.
- **OD-3 -- LAND-03 FIXED, not carried**, on the axis-split argument (test-inventory as a third
  axis). **Declined:** leaving `observed=172` (or `141`) uncorrected.
- **OD-4 -- the two false CI-coverage docstrings are CORRECTED** (comment-only). **Declined:**
  leaving `tests/test_check_size_baseline.py` and `tests/meta_presence.py`'s stale CI claims in
  place.
- **OD-5 -- the `tests/test_checker_convention.py` FLOOR carry-forward is CLOSED**, in the same
  commit that reconciles it. **Declined:** re-carrying it a second time into Phase 159.
- **OD-6 -- `jsmn.h`'s dead duplicate implementation is LEFT UNEDITED.** **Declined:** removing
  the `#ifndef JSMN_HEADER` dead branch.
- **OD-7 -- the ARM half is verified locally if the toolchain installs once**, otherwise the
  ceiling is recorded. **Declined:** claiming ARM coverage without a build; skipping the install
  attempt entirely.
- **OD-8 -- the `*_v153*` fixture family is retired in place and KEPT.** Only 4 new plus 2
  in-place fixtures authored. **Declined:** authoring the full 13-file, 4-group severance docket
  every prior generation used.
- **OD-9 (as amended by the orchestrator, 2026-08-24) -- `ROADMAP.md` and `REQUIREMENTS.md` are
  never regenerated**, and are edited by exactly one plan (07), scoped `Edit` only. **Declined:**
  leaving both documents untouched for the whole phase; regenerating either with a GSD mutation
  verb.
- **OD-10 -- neither the `firestarter` nor the `firestarter_app` gitlink is re-pinned this
  phase.** The drift is recorded with both sha pairs and handed to Phase 159. **Declined:**
  re-pinning either gitlink now.

---

## 12. The corrections index

| ID | Source document's claim | What replaces it | Status |
|---|---|---|---|
| C-1 | ROADMAP criterion 3 / REQUIREMENTS LAND-03: `cases baseline=141 observed=172` | `observed` is the re-measured current count, **184** (17 suites, both native envs, §3), not 172 (stale since Phase 157 plan 04) nor 141 (BASE-01) | Closed here |
| C-2 | ROADMAP criterion 5 / REQUIREMENTS LAND-05: `−128 B RAM for +30 B flash` | Flash is a **win** once LAND-05 lands: `158-RESEARCH.md` cites measured `−138 / −138 / −136 B` on `uno` / `uno328pb` / `leonardo`, alongside the `−128 B` RAM. `+30 B` is reproducible on no layout tried | **Opened here, closed in `158-after-figures.md`** |
| C-3 | ROADMAP criterion 6 / REQUIREMENTS LAND-06: masking costs `+22 B flash` (flat) | `+22 / +24 / +22 B` — right on `uno` and `leonardo`, **2 B low on `uno328pb`**, per `158-RESEARCH.md` | **Opened here, closed in `158-after-figures.md`** |
| C-4 | ROADMAP criterion 7 / REQUIREMENTS LAND-07: `57 tokens`, `7 tokens of headroom` | Three bounds, each with its own scope: **50 / 14** observed over the real chip database, **51 / 13** over any real pin map with every optional scalar, **55 / 9** field-wise-maximum synthetic. `57` is reproducible by none of the three (§9) | Closed here |
| C-5 | LAND-07's implied argument that 64 is not reducible arithmetically | It **is** arithmetically reducible (`64 -> 56` clears the real maximum by 5-6). It is declined on the unknown-key forward-compatibility budget (§9) | Closed here |
| C-6 | LAND-04 as a single clause | Two clauses: no workflow invokes the checker as a size gate, **and** the checker is executed in CI by its own pytest at `build.yml:161` (§8) | Closed here |
| C-7 | `size_baseline.json` `meta.consumed_by` names two consumers | There are **three**: `check_size_baseline.py`, `check_build_warnings.py`, and `check_release_assets.py` (which derives its required asset set from `avr_targets`' keys and runs in CI at `beta-build.yml:327`) | Closed here |
| C-8 | `size_baseline.json` `envs_agree_note` quotes `{cases: 151, suites: 17}` | Stale; already flagged by `meta.native_case_count_revision_260822` in the same file | Closed here (pre-existing self-flag, restated) |
| C-9 | `tests/test_check_size_baseline.py` and `tests/meta_presence.py` both claim no CI leg runs `pytest tests/` on this branch | Both false since `build.yml`'s trigger widened to `push: branches: ['**','!beta']`, documented in that workflow's own header comment | **Opened here, closed in `158-after-figures.md`** (plan 05 corrects the docstrings) |
| C-10 | `tests/test_checker_convention.py`: `FLOOR = 7` described as "the number actually shipped"; `FIXTURE_FLOOR = 16` | 8 checkers ship (`ls scripts/check_*.py`); 30 `planted_*` fixtures ship (`ls tests/fixtures | grep -c '^planted_'`). Both floors are `>=`, so the gate is loose, not broken | **Opened here, closed in `158-after-figures.md`** (plan 05 raises both) |
| C-11 | Every prior generation's severance docstring documents "the same four groups", 13 files | This generation authors **4 new files plus 2 updated in place** (§7). Groups 2 and 3 are not needed because **no MERGE-05 exemption is authored for a reduction** | Closed here |
| C-12 | LAND-03: the canonical invocation exits 1 "before it ever reports flash" | True of the **report**, not of the comparison. The AVR loop runs first and **passes** (confirmed by §4's canonical `--rebuild` output showing zero AVR lines); the native loop then appends two failures and `_print_fail` returns 1, so `_print_pass` is never reached | Closed here |
| C-13 | `157-after-figures.md` §2's Leonardo Caterina headroom `3438 B` | Correct at `785e644` (confirmed, §2); moves once LAND-05/06 land | **Opened here, closed in `158-after-figures.md`** |

---

## 13. Handoffs

**To plan 02** (`jsmntok_t` narrowing): the pre-edit native baseline is 184/184/17 on both `native`
and `native_nodevtools` (§3); the D-04 re-run rule (§3's three prohibitions) applies to any run
plan 02 performs to confirm its own change did not regress the suite.

**To plan 04** (baseline re-record + severance): the cold recipe (§2, `rm -rf` + single `pio run`,
never `--rebuild`); the default-mode RED shape it must flip to GREEN, every failing line verbatim
(§4); the four reddening legs and their remedies (§6); the `*_v158*` membership (4 new files plus 2
updated in place, §7).

**To plan 05** (checker-convention close-out): BASE-01's four `141` integers
(`scripts/baseline/size_baseline_base01.json`'s `native_envs.native.cases`,
`.native.succeeded`, `.native_nodevtools.cases`, `.native_nodevtools.succeeded`, all `141`, suites
`17`); the two false CI-coverage paragraphs named in C-9; the current `FLOOR = 7` /
`FIXTURE_FLOOR = 16` values against the shipped counts of `8` checkers and `30` planted fixtures
(C-10).

**To plan 07** (ROADMAP/REQUIREMENTS scope-correction): the three figures it must correct in
place, named with the correction id that replaces each — ROADMAP criterion 3 / REQUIREMENTS
LAND-03 (C-1, `172` → `184`), ROADMAP criterion 7 / REQUIREMENTS LAND-07 (C-4/C-5, `57`/`7` →
the three derived bounds), and LAND-04's single-clause framing (C-6, → two clauses).

**To Phase 159:** every `file:LINE` citation in this record was measured against the tree at
`785e644` and will be remapped exactly once over the composite diff (D-01, D-05); the
`firestarter` gitlink drift (`2ad5b322` recorded vs `785e644` actual) is handed forward unre-pinned
(OD-10); `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md` was not read for resolution, only confirmed present
and untouched.

---

## 14. Self-verification of this record

Every figure in this file can be re-derived from `/workspaces/firestarter` at commit `785e644`
(or from a fresh `git checkout 785e644`, since no tracked file was edited by this plan):

- §2's cold AVR figures: `rm -rf .pio/build/<env> && pio run -e <env>` for each of `uno`,
  `uno328pb`, `leonardo`, reading the trailing `Flash:`/`RAM:` lines.
- §3's native figures: `pio test -e native` (×3) and `pio test -e native_nodevtools` (×1), reading
  each run's own trailing `N test cases: N succeeded in HH:MM:SS.mmm` line.
- §4's gate ledger: every command is given verbatim in its own row; each is runnable standalone
  against the logs this plan captured under `/tmp/gsd-158/` (not committed — scratch only).
- §5's source quotes: `sed -n '697p;709p' scripts/check_size_baseline.py`; `grep -n "MERGE05_"
  scripts/check_size_baseline.py`.
- §6's leg locations: `grep -n "def test_<name>" tests/test_check_size_baseline.py`.
- §9's token bounds: `python3 /tmp/gsd-158/land07_tokens.py` — the script imports only
  `firestarter_app`'s own `EpromDatabase` and reads `pinouts.json`/`chip_database.json`
  read-only; no file is modified by running it.
