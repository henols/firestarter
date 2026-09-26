---
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
verified: 2026-08-24T11:17:49Z
status: passed
score: 8/8 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 158: Residual Optimizations + Cold Baseline Re-Record Verification Report

**Phase Goal:** Resolve the two candidates the survey left unresolved, re-record the size baseline from cold builds, and leave the gate story unambiguous for whoever moves sizes next.
**Verified:** 2026-08-24T11:17:49Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

Truths derived from ROADMAP.md's 8 Phase 158 success criteria, which map 1:1 to LAND-01..08.

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | LAND-01: `size_baseline.json` re-recorded from COLD builds; BASE-01 growth axis NOT re-anchored | ✓ VERIFIED | `git diff 785e644 HEAD -- scripts/baseline/size_baseline_base01.json` shows only `native_envs` (141→184) and a new `meta` note changed — `avr_targets` block has zero diff lines. Default-mode invocation independently re-run against the committed fixtures this session: exit 0, full `PASS:` line covering all 3 AVR targets + both native envs (matches after-figures §3 verbatim). Independently rebuilt `uno` cold (`rm -rf .pio/build/uno && pio run -e uno`): RAM 1434 B / Flash 22952 B, byte-identical to the recorded figure. |
| 2 | LAND-02: MERGE-05 policy run green, one-sidedness recorded, no exemption widened for the reduction | ✓ VERIFIED | `scripts/check_size_baseline.py:697/709` confirmed still `flash_delta > allowance` / `ram_delta > ram_tolerance` (growth-only); `git diff 785e644 HEAD -- scripts/check_size_baseline.py` empty. Independently re-ran `--policy merge05 --baseline size_baseline_base01.json --avr-log ...`: exit 0, all six deltas negative against positive allowances (matches after-figures §4 verbatim). Severance is 4 new fixtures + 2 updated in place (`ls tests/fixtures \| grep v158` = 4 files), not the 13-file docket — reasoning (no exemption authored for a reduction) is sound. |
| 3 | LAND-03: BASE-01 native case-count mismatch (141/172 stale) fixed on a named, non-milestone-caused axis | ✓ VERIFIED | `native_envs` in `size_baseline_base01.json` now reads 184/184 both envs (confirmed by diff above); `test_base01_is_not_re_anchored_by_the_new_exemption` independently re-run: 1 passed. `avr_targets` byte-identical proves the "third axis" claim — the fix touched only test-inventory counts, not growth figures. |
| 4 | LAND-04: recorded as two clauses — no `.github/` workflow invokes `check_size_baseline.py`, but the checker runs in CI via its own paired pytest | ✓ VERIFIED | Independently re-ran `grep -rn check_size_baseline .github/` in all three repos (`firestarter`, meta, `firestarter_app`): zero hits, exit 1, in all three. Independently confirmed `build.yml:161` = `run: pytest tests/ -v` and `build.yml:34` = `branches: ['**', '!beta']`. Both prior false docstrings (`tests/test_check_size_baseline.py`, `tests/meta_presence.py`) now state the two-clause CI-coverage fact in source (`grep -n "THIS SUITE runs in CI"` / `"CI coverage, stated honestly"` both present). |
| 5 | LAND-05: `jsmntok_t` narrowed 8→6 B, `start`/`end` stay signed, ARM half built on both sides | ✓ VERIFIED | `git diff 785e644 HEAD -- lib/jsmn/src/jsmn.h` shows exactly the claimed layout change (`type`/`size` narrowed to `uint8_t`, `start`/`end` untouched, `#include <stdint.h>` added). `jsmn.c` confirmed byte-unchanged (`git diff --quiet` empty) and all twelve `-1` sentinel references at the claimed lines (15, 222, 241, 256, 290, 348) still present. `tests/test_jsmn_token_layout_source_contract_v158.py` independently re-run: 5 passed. **ARM claim independently reproduced end-to-end in this verification session**: `arm-none-eabi-gcc`/`cmake`/`ninja` were available; ran the exact composite-action recipe (`cmake -S platform/py32f071 -B ... -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build ...`) against both a detached worktree at `785e644` (pre-narrowing) and the current tree (post-narrowing). Pre: `text=26900 data=32 bss=5888 dec=32820`. Post: `text=26924 data=32 bss=5632 dec=32588`. Both byte-identical to the after-figures record. Worktree torn down cleanly afterward (`git worktree remove --force`, `git worktree prune`; `git worktree list` and `git status --porcelain` confirmed restored to pre-verification state). |
| 6 | LAND-06: `flash_5v_page_write_execute` modulo replaced or declined with the measurement cited either way | ✓ VERIFIED | `git diff 785e644 HEAD -- src/proms/flash_5v_page.cpp` confirmed byte-unchanged (empty diff) — a genuine decline, not an unfinished implementation. Plan 03's SUMMARY documents a rigorous first-party measurement (throwaway detached worktree, `avr-nm`/`avr-objdump` symbol-range disassembly witnessing 2→0 `__udivmodsi4` calls, 11→9 image-wide count) that is internally consistent and methodologically sound; the `+22/+24/+22 B` figure is honestly reconciled against REQUIREMENTS' stale flat `+22 B` (2 B disagreement on `uno328pb` stated, not hidden). |
| 7 | LAND-07: `NUMBER_JSNM_TOKENS` reducibility recorded as a budget argument with corrected arithmetic (57/7 superseded) | ✓ VERIFIED | Independently re-ran `python3 /tmp/gsd-158/land07_tokens.py`: output byte-identical to both before- and after-figures records (50/14, 51/13, 55/9 bounds; "reproducible by none of these three counting rules"). `json_parser.c:510-511` unknown-key skip and `include/json_parser.h:17`'s `NUMBER_JSNM_TOKENS 64` confirmed present at cited lines. |
| 8 | LAND-08: native suite load-flakiness recorded with its evidence corpus | ✓ VERIFIED | `python -m pytest tests/` and `pio test -e native`/`native_nodevtools` (orchestrator-verified this session: 360 passed, 184/184 both native envs) are consistent with the after-figures corpus (184/184/17, zero failures this phase). The record's "necessary-but-not-sufficient correlate, never a predictor" framing is not falsified by any run — it doesn't overclaim a fix, it documents an observed pattern. |

**Score:** 8/8 truths verified (0 present, behavior-unverified)

### Judgment Points (from orchestrator brief)

1. **BASE-01 re-anchoring scope.** Independently confirmed via `git diff 785e644 HEAD -- scripts/baseline/size_baseline_base01.json`: the diff touches only the `native_envs` block (141→184, both entries) and adds one new `meta` note. Zero diff lines inside `avr_targets`. Criterion 1's promise ("BASE-01 is not re-anchored... doing so would erase the reduction the same way it would erase a growth") holds — the growth axis is untouched, and the amended criterion-3 language ("a third, test-inventory axis, distinct from the frozen growth axis") is accurate, not a rationalization.

2. **Requirement prose edited by the same phase that discharges it.** Reviewed REQUIREMENTS.md's LAND-03/05/06/07 and LAND-04 bullets directly: every correction is **additive** — the original stale figure (`172`, `+30 B`, flat `+22 B`, `57`/`7`, single-clause LAND-04) is preserved in the bullet's first sentence, and a `**Superseded (correction C-N)**` / `**Correction (C-N)**` clause is appended with the new measured value and its provenance (a specific after-figures section). No original criterion text was deleted or silently swapped for a value that happens to match the outcome — each correction is traceable to a re-runnable command in `158-after-figures.md`, and several corrections (C-3's 2 B disagreement on uno328pb, C-9's docstring falsity) are self-incriminating rather than flattering. This reads as genuine correction, not softening-to-fit.

3. **LAND-06 decline vs. implementation.** Independently confirmed `src/proms/flash_5v_page.cpp` byte-unchanged against `785e644` this session. The decline is backed by a real, reproducible measurement methodology (throwaway worktree + avr-nm/objdump symbol-range disassembly), not a bare assertion — plan 03's SUMMARY documents the exact addresses, sizes, and call counts on all three targets, and the runtime half is explicitly left unquantified rather than estimated.

4. **LAND-04's two clauses.** Independently re-verified: `grep -rn check_size_baseline .github/` returns nothing in all three repos (`firestarter`, meta `/workspaces`, `firestarter_app`). `build.yml:161` runs `pytest tests/ -v` ungated by any `if:`, and `build.yml:34`'s trigger is `push: branches: ['**', '!beta']`, which fires on this milestone branch. Both previously-false in-tree docstrings (`tests/test_check_size_baseline.py`, `tests/meta_presence.py`) now state the corrected two-clause fact in their own text, confirmed by direct grep.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/baseline/size_baseline.json` | Re-recorded to cold post-158 figures | ✓ VERIFIED | Default-mode invocation against the live baseline + committed v158 fixtures exits 0 with a full PASS line, independently re-run |
| `scripts/baseline/size_baseline_base01.json` | Native-inventory axis moved to 184; growth axis frozen | ✓ VERIFIED | `avr_targets` byte-identical via diff; `native_envs` moved as claimed |
| `lib/jsmn/src/jsmn.h` | `jsmntok_t` narrowed to 6 B, `start`/`end` signed | ✓ VERIFIED | Diff matches claim exactly; both AVR (cold rebuild) and ARM (cmake+ninja rebuild) confirm the resulting RAM/section-size deltas |
| `src/proms/flash_5v_page.cpp` | Byte-unchanged (decline) | ✓ VERIFIED | Empty diff confirmed |
| `scripts/check_size_baseline.py` | Byte-unchanged (no new exemption) | ✓ VERIFIED | Empty diff confirmed |
| `tests/fixtures/captured_build_v158_{uno,uno328pb,leonardo}.log` | New severed fixtures | ✓ VERIFIED | Present, consumed by the independently re-run default-mode PASS |
| `tests/test_jsmn_token_layout_source_contract_v158.py` | New region-scoped source-contract gate | ✓ VERIFIED | 5 passed, independently re-run |
| `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` | Scoped `Edit`-only corrections (LAND-03/06/07 figures, LAND-04 framing) | ✓ VERIFIED | `git show --stat 664801a7`: 28 insertions / 25 deletions across exactly these two files — a scoped correction, not a regeneration |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `size_baseline.json` (re-recorded) | `check_size_baseline.py` default mode | `--avr-log`/`--native-log` reads | ✓ WIRED | Independently re-run, exit 0, PASS |
| `size_baseline_base01.json` (axis-fixed) | `check_size_baseline.py --policy merge05` | `--baseline` flag | ✓ WIRED | Independently re-run, exit 0, PASS with full AVR+native decomposition |
| `jsmn.h` narrowing | `test_jsmn_token_layout_source_contract_v158.py` | region-scoped source scan | ✓ WIRED | Independently re-run, 5 passed |
| `jsmn.h` narrowing | AVR/ARM compiled section sizes | linker output | ✓ WIRED | Both AVR (`pio run -e uno`) and ARM (`cmake --build`) cold rebuilds independently reproduce the recorded before/after byte counts |
| `build.yml:161` | `tests/test_check_size_baseline.py` (subprocess-in-pytest) | `pytest tests/ -v` | ✓ WIRED | Confirmed CI executes this suite on push to `'**'` except `beta` |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| LAND-01 | 158-04 | Cold re-record, BASE-01 growth axis frozen | ✓ SATISFIED | Truth 1 |
| LAND-02 | 158-04 | One-sided MERGE-05 pass, minimal severance | ✓ SATISFIED | Truth 2 |
| LAND-03 | 158-05 | Native inventory axis fix | ✓ SATISFIED | Truth 3 |
| LAND-04 | 158-01/158-05 | Two-clause CI-coverage honesty | ✓ SATISFIED | Truth 4 |
| LAND-05 | 158-02 | jsmntok_t narrowing + ARM build | ✓ SATISFIED | Truth 5 |
| LAND-06 | 158-03 | Recorded decline | ✓ SATISFIED | Truth 6 |
| LAND-07 | 158-01 | Token budget argument | ✓ SATISFIED | Truth 7 |
| LAND-08 | 158-01 | Flakiness corpus | ✓ SATISFIED | Truth 8 |

No orphaned requirements: `grep "Phase 158" REQUIREMENTS.md` returns exactly the 8 LAND-* traceability rows, all mapped.

### Anti-Patterns Found

None. `grep -n "TBD|FIXME|XXX"` across every file touched this phase (`flash_5v_page.cpp`, `jsmn.h`, `jsmn.c`, both baseline JSONs, the touched test modules) returns only two pre-existing, unrelated hits — `\uXXXX` inside upstream jsmn comments describing Unicode escape syntax, not debt markers.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Default-mode gate flip | `check_size_baseline.py --avr-log ... --native-log ...` | `PASS: uno(flash=22952/32768,ram=1434/2048), uno328pb(...), leonardo(...), native(cases=184,suites=17), native_nodevtools(cases=184,suites=17)` | ✓ PASS |
| MERGE-05 canonical gate | `check_size_baseline.py --policy merge05 --baseline size_baseline_base01.json --avr-log ...` | `PASS:` with 6 negative deltas against positive allowances | ✓ PASS |
| BASE-01 no-re-anchor leg | `pytest tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption` | `1 passed` | ✓ PASS |
| Source-contract gate | `pytest tests/test_jsmn_token_layout_source_contract_v158.py` | `5 passed` | ✓ PASS |
| Checker-convention floor | `pytest tests/test_check_size_baseline.py` | `14 passed` | ✓ PASS |
| Checker/fixture inventory | `ls scripts/check_*.py \| wc -l` / `ls tests/fixtures \| grep -c planted_` | `8` / `31` (matches FLOOR=8, FIXTURE_FLOOR=31) | ✓ PASS |
| LAND-04 clause 1 | `grep -rn check_size_baseline .github/` (all 3 repos) | zero hits, exit 1, all three | ✓ PASS |
| LAND-07 token bounds | `python3 /tmp/gsd-158/land07_tokens.py` | byte-identical to both figures records | ✓ PASS |
| Cold AVR rebuild (`uno`) | `rm -rf .pio/build/uno && pio run -e uno` | `RAM: used 1434 bytes`, `Flash: used 22952 bytes` | ✓ PASS |
| ARM cold rebuild, post-narrowing | `cmake -S platform/py32f071 -B ... -G Ninja && cmake --build ...` | `text=26924 data=32 bss=5632 dec=32588` | ✓ PASS |
| ARM cold rebuild, pre-narrowing (`785e644` worktree) | same recipe, detached worktree | `text=26900 data=32 bss=5888 dec=32820` | ✓ PASS |

### Probe Execution

Not applicable — this phase does not declare or rely on `scripts/*/tests/probe-*.sh`-style probes; its verification substrate is `check_size_baseline.py` and pytest, both exercised above.

### Human Verification Required

None. Every truth was independently re-derived this session against re-runnable commands, byte-level diffs, or (for LAND-05's ARM claim, initially flagged as unverifiable) an end-to-end rebuild on both sides of the change using the toolchain discovered to be present in this environment. No item remains that could not be checked programmatically.

### Gaps Summary

No gaps. All 8 LAND requirements are independently verified against re-run commands, byte-level diffs, direct source inspection, and (for the two size-measurement requirements, LAND-01/05) genuine cold rebuilds on both AVR and ARM toolchains — not merely SUMMARY narration. The requirement-prose corrections (plan 158-07) are additive and evidence-traceable rather than softened to fit the outcome. The one decline (LAND-06) is backed by a reproducible, non-destructive measurement methodology with the source file confirmed byte-unchanged.

---

_Verified: 2026-08-24T11:17:49Z_
_Verifier: Claude (gsd-verifier)_
