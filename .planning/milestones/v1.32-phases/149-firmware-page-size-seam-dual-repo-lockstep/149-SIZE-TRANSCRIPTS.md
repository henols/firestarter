# Phase 149 Plan 06 — Size Gate Transcripts

Cold post-change measurement, the MERGE-05 gate seen to FAIL before any exemption existed,
then seen to PASS after it, then the re-armed tripwire seen to FAIL again one byte past the
new allowance. Every command below is pasted verbatim with its literal output.

## Cold post-change measurement (Task 1)

Procedure, identical to plan 01's pre-edit capture: `rm -rf .pio/build/<env>` then one
uninterrupted `pio run -e <env>`, for `uno`, `uno328pb`, `leonardo`. All three ended
`[SUCCESS]` with zero `warning:` lines.

| env | pre-edit cold flash | post-change cold flash | Δ vs pre-edit | BASE-01 flash | Δ vs BASE-01 | pre-edit cold RAM | post-change cold RAM | Δ vs pre-edit | BASE-01 RAM | Δ vs BASE-01 |
|---|---|---|---|---|---|---|---|---|---|---|
| uno | 24920 | 25130 | +210 | 24824 | +306 | 1573 | 1575 | +2 | 1573 | +2 |
| uno328pb | 24970 | 25180 | +210 | 24874 | +306 | 1579 | 1581 | +2 | 1579 | +2 |
| leonardo | 27002 | 27212 | +210 | 26906 | +306 | 2014 | 2016 | +2 | 2014 | +2 |

`flash_total` / `ram_total` are unchanged on all three envs (32256/2048, 32384/2048, 28672/2560)
— the board/framework did not move.

**Seam flash cost `N` (BASE-01 delta minus the already-admitted 96 B defect-fix exemption):
`306 - 96 = 210` B, uniform on all three AVR targets.**

**Seam RAM cost `M` (BASE-01 delta; the pre-edit capture's RAM already equalled BASE-01's on
all three targets, so "vs pre-edit" and "vs BASE-01" are the same number here): `+2` B, uniform
on all three AVR targets — matching the predicted cost of the one `uint16_t page_size` field
added to the single file-scope `firestarter_handle_t` global (AVR aligns scalars to 1 byte, so
there is no padding to absorb it).**

## Cold warning run (Task 1)

Both native build directories plus `native_pinmap_provisional`'s were removed by hand first
(`_rebuild_native` does not clean; the recorded watermarks are cold figures, and the warm
figures read as headroom that does not exist):

```
$ rm -rf .pio/build/native .pio/build/native_nodevtools .pio/build/native_pinmap_provisional
$ python3 scripts/check_build_warnings.py --rebuild ; echo EXIT=$?
...
PASS: uno: macro_redefinition=0 (== 0), uno328pb: macro_redefinition=0 (== 0), leonardo: macro_redefinition=0 (== 0), native: total warnings=1166 (== watermark 1166), native_nodevtools: total warnings=1166 (== watermark 1166)
EXIT=0
```

AVR macro-redefinition counts are 0/0/0 (the `== 0` rule, not `<= 0`). Both pinned native
watermarks (`native`, `native_nodevtools`) hold at exactly **1166**, measured cold — no
watermark is lowered by this plan. (`--rebuild`'s `NATIVE_ENVS` tuple covers `native` and
`native_nodevtools` only; `native_pinmap_provisional` is not part of that rebuild set and was
not re-measured here — its build directory was still removed for cleanliness before the run,
and its recorded baseline watermark of 138 is untouched.)

## RED — MERGE-05 before the page-size-seam exemption

```
$ python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno.log \
  --avr-log uno328pb=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno328pb.log \
  --avr-log leonardo=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-leonardo.log ; echo EXIT=$?
FAIL:
  uno: flash_used baseline=24824 observed=25130 delta=+306 exceeds MERGE-05 uno-class allowance of 160 B (band 64 B + defect-fix exemption 96 B)
  uno: ram_used baseline=1573 observed=1575 delta=+2 (MERGE-05 requires ram_used unchanged)
  uno328pb: flash_used baseline=24874 observed=25180 delta=+306 exceeds MERGE-05 uno-class allowance of 160 B (band 64 B + defect-fix exemption 96 B)
  uno328pb: ram_used baseline=1579 observed=1581 delta=+2 (MERGE-05 requires ram_used unchanged)
  leonardo: flash_used baseline=26906 observed=27212 delta=+306 exceeds MERGE-05 leonardo allowance of 96 B (band 0 B + defect-fix exemption 96 B)
  leonardo: ram_used baseline=2014 observed=2016 delta=+2 (MERGE-05 requires ram_used unchanged)
EXIT=1
```

This confirms the exemption is necessary, not convenient — both a flash exemption (the
leonardo line names `allowance of 96 B`, the pre-existing figure) and a RAM exemption (every
env's `ram_used` line fires, `M=2` moved on all three targets) are required before this gate
can pass. Recorded before any constant was authored.

## The named exemptions (Task 2)

`MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210` (flash) and
`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` (RAM) added to
`firestarter/scripts/check_size_baseline.py`, funding exactly `N=210` and `M=2` as measured
above. `MERGE05_UNO_CLASS_FLASH_BAND` stays 64, `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` stays 96,
and `scripts/baseline/size_baseline_base01.json` is byte-unchanged. `_merge05_flash_allowance`
is now a 5-tuple `(band, defect_exemption, seam_exemption, allowance, band_label)`; a new
`_merge05_ram_allowance(env)` resolves the RAM tolerance. New effective allowances:
leonardo `0 + 96 + 210 = 306` B, uno-class `64 + 96 + 210 = 370` B; RAM tolerance `2` B on all
three targets.

## GREEN — MERGE-05 with the page-size-seam exemption

```
$ python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno.log \
  --avr-log uno328pb=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno328pb.log \
  --avr-log leonardo=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-leonardo.log ; echo EXIT=$?
PASS: uno(flash=25130/32256[+306<=370=band64+exempt96+seam210],ram=1575/2048[+2<=2=seam2]), uno328pb(flash=25180/32384[+306<=370=band64+exempt96+seam210],ram=1581/2048[+2<=2=seam2]), leonardo(flash=27212/28672[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2])
EXIT=0
```

Every env's PASS text names the full three-term flash decomposition (`band` + `exempt` +
`seam`) and the RAM decomposition (`seam2`), on the real cold post-change logs. Leonardo's
delta (`+306`) exactly equals its allowance (`306`) — its MERGE-05 headroom after this
exemption is exactly **0 bytes**, same shape as the Phase 145 admission it sits alongside: the
exemption funds exactly what was measured, with no spare margin.

## The tripwire is still ARMED

Full suite, with the three fixtures re-planted at exactly one byte past the new allowances:

```
$ python3 -m pytest tests/test_check_size_baseline.py -q
..............
14 passed in 0.70s
```

Direct gate runs against each re-planted fixture, showing the tripwire fires one byte past the
new allowance in all three dimensions (leonardo flash, uno-class flash, RAM):

```
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log leonardo=tests/fixtures/planted_size_baseline_policy_leonardo_growth.log ; echo EXIT=$?
FAIL:
  leonardo: flash_used baseline=26906 observed=27213 delta=+307 exceeds MERGE-05 leonardo allowance of 306 B (band 0 B + defect-fix exemption 96 B + page-size-seam exemption 210 B)
EXIT=1

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=tests/fixtures/planted_size_baseline_policy_uno_over_band.log ; echo EXIT=$?
FAIL:
  uno: flash_used baseline=24824 observed=25195 delta=+371 exceeds MERGE-05 uno-class allowance of 370 B (band 64 B + defect-fix exemption 96 B + page-size-seam exemption 210 B)
EXIT=1

$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=tests/fixtures/planted_size_baseline_policy_ram_moved.log ; echo EXIT=$?
FAIL:
  uno: ram_used baseline=1573 observed=1576 delta=+3 exceeds MERGE-05 ram allowance of 2 B (page-size-seam exemption 2 B) (MERGE-05 requires ram_used within the admitted allowance)
EXIT=1
```

Each fixture was re-derived from `allowance + 1` using the new allowances above (leonardo
`306+1=307` → flash `26906+307=27213`; uno-class `370+1=371` → flash `24824+371=25195`; RAM
`2+1=3` → RAM `1573+3=1576`) and observed to fail, not merely asserted to fail — the tripwire
is a machine-checked negative control at the new floor, not a claim.

## Firmware repo pytest and native suites (Task 2, run after committing)

```
$ python3 -m pytest tests/ -o addopts="" -q
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 68%]
........................................................................ [ 91%]
...........................                                              [100%]
315 passed in 9.75s
```

314 (Phase 149 pre-existing count, per plan 04's SUMMARY) + 1 new leg
(`test_base01_is_not_re_anchored_by_the_new_exemption`) = 315. This plan added zero new native
cases.

```
$ pio test -e native
================ 151 test cases: 151 succeeded in 00:00:20.434 ================
$ pio test -e native_nodevtools
================ 151 test cases: 151 succeeded in 00:00:22.194 ================
```

Both pinned native envs agree at 151/151 cases, 17 suites, unmoved from plan 04's landing
(baseline 141 + 10 new native cases added by plan 04).

## Plan 07 — size_baseline.json becomes the live default baseline again (D-14, X-3)

Every figure below is **transcribed** from the cold logs already committed above
(`149-postchange-cold-{uno,uno328pb,leonardo}.log`) and from this file's own Task-2 native run
(151/151, 17 suites, both pinned envs agreeing). No `pio run`, no `pio test` and no
`check_build_warnings.py --rebuild` ran in this plan.

**AVR figures transcribed into `avr_targets`** (free figures recomputed, totals unchanged):

| env | flash_used | flash_total | flash_free | ram_used | ram_total | ram_free |
|---|---|---|---|---|---|---|
| uno | 25130 | 32256 | 7126 | 1575 | 2048 | 473 |
| uno328pb | 25180 | 32384 | 7204 | 1581 | 2048 | 467 |
| leonardo | 27212 | 28672 | 1460 | 2016 | 2560 | 544 |

**`native_envs`:** `native` and `native_nodevtools` both bumped `cases`/`succeeded` 141 -> 151
(the number plan 06 recorded), `suites` unchanged at 17 on both, `envs_agree` stays true,
`envs_agree_note`'s quoted figures updated to match. `native_pinmap_provisional` byte-unchanged.

**X-3 correction — `meta.firmware_tree_sha`.** The stale value
`3d8ec4913913f5db4e636d88d5180172f83776f9` (the root tree of commit `6cc4795`, a **Phase 144**
commit that predates the +96 B this file's own figures already recorded) is replaced with the
root tree of the firmware commit the plan 06 cold measurement was actually taken at:

```
$ git -C /workspaces/firestarter rev-parse HEAD
581cff68657a740c1fee0ec54a282734b0533e01
$ git -C /workspaces/firestarter rev-parse HEAD^{tree}
c6349d22bb15a0e2a3f1e95af946bfe28a8582ad
$ git cat-file -t c6349d22bb15a0e2a3f1e95af946bfe28a8582ad
tree
```

`meta.host_app_tree_sha` refreshed the same way from `firestarter_app` (commit `0744348`, tree
`623e71bd10e793afaaeb2fe8855c083566d777cc`). `meta.generated_by` gained a superseding sentence
naming `6cc4795` and the correction, scoped to exactly the three `avr_targets` figures and the
two pinned `native_envs` case counts, per D-14. `platformio_core`/`platform_atmelavr`/
`toolchain_atmelavr`/`avr_gcc`/`framework_arduino_avr`/`framework_arduino_avr_minicore` were
re-confirmed unchanged from the live installation (6.1.19 / 5.2.0 / 1.70300.191015 / 7.3.0 /
5.3.0 / 3.1.2).

**`meta.deltas_vs_base01`.** All three `flash_used_delta` moved 96 -> 306 and `ram_used_delta`
moved 0 -> 2 (the first RAM movement this file has ever recorded). Each `merge05_clause` now
names both admitted exemptions — the pre-existing `MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96`
(Phase 145) and the new `MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES = 210` /
`MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES = 2` (Phase 149) — with the "ADJUDICATED AND
ADMITTED, not laundered" framing preserved, and states that BASE-01 was **not** re-anchored a
third time. `meta.roadmap_cross_check` re-derived for the new deltas.

No watermark was lowered; the whole `warnings` block, `check_size_baseline.py`,
`scripts/baseline/size_baseline_base01.json`, `src/`, `include/` and `tests/` are byte-unchanged
by this plan (`git diff --quiet` on each exits 0).

## GREEN — default-mode byte identity against the updated baseline (D-14)

```
$ python3 scripts/check_size_baseline.py --baseline scripts/baseline/size_baseline.json \
  --avr-log uno=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno.log \
  --avr-log uno328pb=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno328pb.log \
  --avr-log leonardo=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-leonardo.log ; echo EXIT=$?
PASS: uno(flash=25130/32256,ram=1575/2048), uno328pb(flash=25180/32384,ram=1581/2048), leonardo(flash=27212/28672,ram=2016/2560)
EXIT=0
```

## GREEN — MERGE-05 re-confirmed after the baseline update

```
$ python3 scripts/check_size_baseline.py --policy merge05 \
  --baseline scripts/baseline/size_baseline_base01.json \
  --avr-log uno=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno.log \
  --avr-log uno328pb=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-uno328pb.log \
  --avr-log leonardo=/workspaces/.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-postchange-cold-leonardo.log ; echo EXIT=$?
PASS: leonardo(flash=27212/28672[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2]), uno(flash=25130/32256[+306<=370=band64+exempt96+seam210],ram=1575/2048[+2<=2=seam2]), uno328pb(flash=25180/32384[+306<=370=band64+exempt96+seam210],ram=1581/2048[+2<=2=seam2])
EXIT=0
```

Both gates green simultaneously: the default gate proves the new figures are recorded exactly,
the band gate proves the growth is admitted rather than absorbed.

## RESOLVED (orchestrator-directed override, supersedes the "known, accepted fallout" note below)

The orchestrator overrode this plan's `git diff --quiet ... tests` verification criterion:
updating the live default baseline (D-14) necessarily invalidates any fixture that asserts
default-mode output against it, so a byte-identity criterion on `tests/` was the wrong shape for
a plan whose entire job is to re-anchor that baseline. "Stale legs, documented and left red" was
not an acceptable close for a phase whose theme is honest measurement.

**Resolution: SEVERANCE**, following the exact precedent already established in this same file by
the Phase 145 debug session, which severed `test_policy_merge05_permits_the_measured_landing_deltas`
off `captured_build_*.log` onto its own frozen `merge05_base01_anchor_*.log` trio for the same
reason (a leg needing frozen inputs while the live tree keeps moving). Firmware commit `6e3f90a`:

- **New fixture family**, `tests/fixtures/captured_build_v132_{uno,uno328pb,leonardo}.log`,
  transcribed byte-for-byte from the same committed cold post-change logs D-14 used (uno
  25130/1575, uno328pb 25180/1581, leonardo 27212/2016) — never re-derived warm — plus
  `planted_size_baseline_flash_regression_v132.log` (leonardo +512 B -> 27212/27724, the same
  offset every prior version of this plant has used since Phase 123).
- **Three legs severed onto the new family**: `test_clean_avr_all_three_envs_pass`,
  `test_default_mode_is_unchanged_by_the_new_flag`, and
  `test_planted_flash_regression_flips_checker_to_failure` — each docstring now records why it
  moved and what still depends on the old family, in the same voice as the existing Phase 145
  severance note.
- **`captured_build_{uno,uno328pb,leonardo}.log` and `merge05_base01_anchor_*.log` stay
  byte-unchanged** — `test_baseline_seam_precedence_flips_clean_log_to_fail` and
  `test_policy_merge05_admits_the_documented_defect_fix`'s Arm 1 both still need the pre-149 trio
  frozen at its original figures.
- **`captured_test_native{,_nodevtools}_summary.log` updated IN PLACE**, 141 -> 151
  cases/succeeded (suites unchanged at 17) — no severance needed, since
  `test_clean_native_both_envs_pass` is the only leg in the module reading either native summary
  fixture at test time, and nothing depends on 141 staying frozen.
- **`scripts/check_size_baseline.py`, `size_baseline_base01.json`, every band/exemption constant
  and every watermark are byte-unchanged.** No `PGSZ-0N` checkbox or traceability row touched.

```
$ python3 -m pytest tests/ -o addopts="" -q
315 passed in 9.70s
```

Both size gates re-confirmed green after the severance commit:

```
$ python3 scripts/check_size_baseline.py --baseline scripts/baseline/size_baseline.json --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... ; echo EXIT=$?
PASS: uno(flash=25130/32256,ram=1575/2048), uno328pb(flash=25180/32384,ram=1581/2048), leonardo(flash=27212/28672,ram=2016/2560)
EXIT=0
$ python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log uno=... --avr-log uno328pb=... --avr-log leonardo=... ; echo EXIT=$?
PASS: uno(flash=25130/32256[+306<=370=band64+exempt96+seam210],ram=1575/2048[+2<=2=seam2]), uno328pb(flash=25180/32384[+306<=370=band64+exempt96+seam210],ram=1581/2048[+2<=2=seam2]), leonardo(flash=27212/28672[+306<=306=band0+exempt96+seam210],ram=2016/2560[+2<=2=seam2])
EXIT=0
```

The section below is preserved verbatim as the historical record of the investigation that led
to this resolution (the reasoning about why a blanket re-capture would break
`test_policy_merge05_admits_the_documented_defect_fix`'s Arm 1 was correct; the conclusion to
leave the suite red was overridden by the orchestrator in favor of severance).

## Known, accepted fallout — four `tests/test_check_size_baseline.py` legs now stale (not fixed here)

`tests/` is byte-unchanged by this plan (a hard constraint of this plan's own `<verification>`
block: `git diff --quiet src include tests`), and Task 1 explicitly forbids touching
`check_size_baseline.py`, `size_baseline_base01.json`, any fixture, or firmware source. Updating
the live default baseline's `avr_targets`/`native_envs` figures (required by D-14) therefore puts
four pre-existing default-mode legs out of sync with `tests/fixtures/captured_build_*.log` and
`captured_test_native*.log`, which are frozen at the **pre-Phase-149** figures on purpose —
`test_policy_merge05_admits_the_documented_defect_fix` (authored at 149-06) explicitly relies on
that freeze for its Arm 1 ("the tree as captured before Phase 149... PASSES" against BASE-01), so
re-capturing those fixtures to the new figures would fix the four legs below but break that
already-passing, deliberately-designed test instead — a worse trade, and one this plan's own
constraint forbids either way:

```
$ python3 -m pytest tests/test_check_size_baseline.py -q
FAILED tests/test_check_size_baseline.py::test_clean_avr_all_three_envs_pass
FAILED tests/test_check_size_baseline.py::test_clean_native_both_envs_pass
FAILED tests/test_check_size_baseline.py::test_planted_flash_regression_flips_checker_to_failure
FAILED tests/test_check_size_baseline.py::test_default_mode_is_unchanged_by_the_new_flag
4 failed, 10 passed
```

All four fail for the same single reason: they invoke the checker in **default mode** (no
`--baseline` flag), which now reads the just-updated `scripts/baseline/size_baseline.json`
(25130/25180/27212 flash, 1575/1581/2016 RAM, 151 native cases), against `captured_build_*.log`
/ `captured_test_native*.log` fixtures still reading the pre-149 figures (24920/24970/27002
flash, 1573/1579/2014 RAM, 141 native cases). This is a real, direct, and fully understood
consequence of this plan's own required change — not a mystery, not silently swept — and is
recorded here rather than fixed, per this plan's explicit fixture/tests-directory constraints.
Re-capturing these fixtures (and updating the corresponding literals in
`test_check_size_baseline.py`) is left for whichever future plan next touches this file's
`avr_targets`/`native_envs`, at which point all of `captured_build_*.log`,
`captured_test_native*.log`, `planted_size_baseline_flash_regression.log` and the moved
literals in `test_check_size_baseline.py` should be re-derived together, in one commit, matching
the precedent of `test(144-05): re-anchor all three size baselines to the v1.31 tip`.
