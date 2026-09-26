---
phase: 125
slug: vpp-control-seam
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-31
---

# Phase 125 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `125-RESEARCH.md` §"Validation Architecture" (all figures measured, not estimated).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** (gates + new harness) | pytest 9.1.1 on Python 3.12.13 |
| **Config file** | **none** — no `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`, and **no `conftest.py` anywhere** in `firestarter/`. Path resolution is self-contained per module (house rule, `tests/test_pinmap_guard_fires.py:26–28`) |
| **Framework** (firmware unit) | Unity via PlatformIO — **not touched by this phase** |
| **Quick run command** | `cd firestarter && python3 -m pytest tests/ -q` (currently **72 passed**, ~3 s) |
| **Full suite command** | `cd firestarter && python3 -m pytest tests/ -q` **and** `pio test -e native` **and** `pio test -e native_nodevtools` (141 cases / 17 suites each) |
| **Host suite** (regression only) | `cd firestarter_app && python3 -m pytest -q` (**1158 passed, 0 skipped**, ~145 s) |
| **Estimated runtime** | quick ~3 s · each native env ~2 min cold · each AVR build ~30–60 s cold |
| **CI legs on this branch** | **none** for `pytest tests/` — `pytest tests/ -v` appears only in `build.yml` (push/PR to `main`) and `beta-build.yml` (push to `beta`); `py32f071.yml` has no pytest step (RESEARCH C-7). There is no CI oracle to fall back on — every row below is discharged locally and recorded verbatim. |

---

## Sampling Rate

- **After every task commit:** `cd firestarter && python3 -m pytest tests/ -q` (~3 s). Covers the new harness plus every existing gate's paired test.
- **After the file-authoring task, and after ANY edit to `include/rurp_shield.h` or `platformio.ini`:** `pio test -e native` (~2 min cold). **This is the C-1 tripwire — the single highest-value check in the phase. It must NOT be deferred to the closing plan.** Under the operator's Option A neither file is edited at all, so a non-empty diff on either is itself the alarm.
- **Per wave merge:** `pytest tests/ -q` + `pio test -e native` + `pio test -e native_nodevtools` + `python3 scripts/check_cmake_manifest.py`.
- **Phase gate (closing plan — every row re-executed, never copied from a SUMMARY):** the full map below, including three cold AVR builds with the `rm -rf .pio/build/<env>` + single-invocation + extended-timeout discipline, the `avr-nm` non-vacuity leg, the blob-SHA re-hash, the host suite, and the claim gate. Then `/gsd-verify-work`.
- **Max feedback latency:** 3 s (quick) / ~120 s (native tripwire).

---

## Per-Task Verification Map

| Requirement | Behavior | Test Type | Automated Command | File Exists | Status |
|-------------|----------|-----------|-------------------|-------------|--------|
| VPP-01 | No PR #45 commit is an ancestor of `HEAD`; the SHA list is the full ten; an unresolvable SHA is exit 2, never a silent pass | unit (git) | `python3 -m pytest tests/test_pr45_non_ancestry.py -q` | ❌ W0 | ⬜ pending |
| VPP-01 | The two new files' blob SHAs differ from PR #45's (`c982173813b38ec745b59d6e02817f2504d6c6b4`, `fcbe009dffcd46139802f8779865a1d7aa331880`) | unit | same module, second leg | ❌ W0 | ⬜ pending |
| VPP-02 | `rurp_set_vpp_target_mv()` → `MANUAL_ADJUSTMENT_REQUIRED` and `rurp_vpp_control_mode()` → `MANUAL` on all four board macro-sets, compiled **and run** | integration (compile+run) | `python3 -m pytest tests/test_vpp_seam_manual_on_every_board.py -q` | ❌ W0 | ⬜ pending |
| VPP-02 | Forced-capability leg: `-DRURP_HAS_VPP_DAC=1` → non-zero `g++` exit with the named `#error` **from `src/rurp_vpp.cpp`** (D-03 via RESEARCH C-4 — the header alone exits 0) | integration | same module | ❌ W0 | ⬜ pending |
| VPP-02 | Unset-and-non-AVR leg: no `__AVR__`, no `RURP_HAS_VPP_DAC` → non-zero exit with the named `#error` (D-08) | integration | same module | ❌ W0 | ⬜ pending |
| VPP-02 | Drift leg: each board's real anchor still present in its build config — `[env:<name>]` + `board = <uno\|ATmega328PB\|leonardo>`, and `RURP_PLATFORM_PY32F071=1` + `RURP_BOARD_NAME="py32f071"`. **NOT `ARDUINO_AVR_*`** (RESEARCH C-6: those appear nowhere in `platformio.ini` and the leg would fail on arrival) | unit | same module | ❌ W0 | ⬜ pending |
| VPP-02 | No-skip self-enforcement: the harness module's own source contains no `pytest.skip` / `mark.skipif` — a skip at exit 0 is how this project's gates failed OPEN before (A-7) | unit | same module (mirror `test_pinmap_guard_fires.py` coverage leg 6, including its string-concatenation self-avoidance) | ❌ W0 | ⬜ pending |
| VPP-03 | The three pinned files are byte-identical: `src/boards/rurp_common.cpp`, `include/rurp_types.h`, `src/rurp_config_utils.cpp` — blob-SHA re-hash, **never** a path-scoped diff | smoke | `git -C firestarter hash-object <3 paths>` vs the pre-phase table in `125-RESEARCH.md` | ✅ (git) | ⬜ pending |
| VPP-03 | `CONFIG_VERSION` still literally `"VER06"` | smoke | `grep -n 'define CONFIG_VERSION' firestarter/include/rurp_shield.h` | ✅ | ⬜ pending |
| VPP-03 | AVR flash **and** RAM measured for all three targets, non-vacuously | integration (build) | `rm -rf .pio; pio run -e {uno,uno328pb,leonardo}` + `ls .pio/build/$e/src/rurp_vpp.cpp.o` + `avr-nm … \| grep -cE 'rurp_vpp_control_mode\|rurp_set_vpp_target_mv\|rurp_disable_vpp_control'` (expect 0, against 5 unrelated pre-existing `vpp` symbols) | ✅ (tooling) | ⬜ pending |
| VPP-03 | Strict comparator green — or D-16's re-baseline path taken in a named commit stating why | integration | `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` | ✅ | ⬜ pending |
| non-regression | Both pinned native envs still **141 cases / 17 suites**, all PASSED | integration | `pio test -e native`; `pio test -e native_nodevtools` | ✅ | ⬜ **the C-1 tripwire; non-optional** |
| non-regression | Third native env still 10 cases / 1 suite | integration | `pio test -e native_pinmap_provisional` | ✅ | ⬜ pending |
| non-regression | ARM manifest reverse check green with the seam named (24 enforced sources, up from 23) | unit | `python3 scripts/check_cmake_manifest.py` | ✅ | ⬜ pending |
| non-regression | Existing firmware gates still green | unit | `python3 -m pytest tests/ -q` (expect > 72), `check_landing_range.py`, `check_orphan_provisional.py` | ✅ | ⬜ pending |
| non-regression | Host repo unmoved | unit | `cd firestarter_app && python3 -m pytest -q` (expect 1158, 0 skipped); `pytest tests/test_revision_constants_parity.py -q` (expect 13) | ✅ | ⬜ pending |
| claim gate | `125-NONREGRESSION.md` carries no forbidden phrase and does carry the canonical caveat | unit | `FIRESTARTER_CLAIMSCAN_TARGETS=<abs path to 125-NONREGRESSION.md> python3 .planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py` | ✅ (C-16: the target **must** be named explicitly — `_DEFAULT_TARGETS` are four Phase-130 files) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/tests/test_vpp_seam_manual_on_every_board.py` — VPP-02: four board legs + forced-DAC leg + unset-non-AVR leg + drift leg + no-skip meta leg
- [ ] `firestarter/tests/test_pr45_non_ancestry.py` — VPP-01: ten SHAs, `n_checked == 10` non-vacuity guard, explicit exit-128 handling, optional blob-divergence leg
- [ ] **No shared fixtures needed** — the project's house rule is self-contained per-module path resolution, and there is no `conftest.py` to extend. Do not add one.
- [ ] **No framework install needed** — pytest 9.1.1, `g++` 14.2.0, PIO 6.1.19 and the AVR toolchain (avr-gcc 7.3.0) are all present and were exercised during research.
- [ ] **If a `scripts/check_*.py` is chosen for VPP-01 instead of the pytest** (not recommended — RESEARCH C-11): the same commit additionally owes `tests/test_check_<X>.py`, a `tests/fixtures/planted_<X>*` entry, and `FLOOR 5→6` + `FIXTURE_FLOOR 10→11` in `tests/test_checker_convention.py`. Proven by planting one: 2 failed → remove → 7 passed. **Never lower a floor.**

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ARM configure + build of the tree carrying `src/rurp_vpp.cpp` in `FIRESTARTER_COMMON_SOURCES` | D-12 / D-13 | No ARM toolchain exists in this devcontainer (`arm-none-eabi-gcc`, `cmake`, `ninja` all absent), and **D-14 forbids any task from running `git push` or `gh workflow run`** | The plan prints the two commands and stops. The operator pushes `v1.23-py32f071-integration` and dispatches `py32f071.yml`; the phase records the **run URL + head SHA**. Push safety re-verified on the current tree (RESEARCH C-7): `py32f071.yml` fires on `push:[beta]` + `pull_request` + `workflow_dispatch`, `beta-build.yml` on `push:[beta]` + `workflow_dispatch` — pushing this branch matches neither and opens no PR, so **it cuts no beta prerelease**. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without an automated verify
- [ ] Wave 0 covers both MISSING harness modules
- [ ] No watch-mode flags
- [ ] Feedback latency < 3 s for the quick command; < 120 s for the C-1 native tripwire
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
