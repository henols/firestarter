---
phase: 158
slug: residual-optimizations-cold-baseline-re-record-firmware-only
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-24
---

# Phase 158 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `158-RESEARCH.md` § Validation Architecture. Every baseline figure below
> was measured this session at `firestarter` `785e644` on a clean tree.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **Unity** via PlatformIO `test_framework = unity` + **ArduinoFake 0.4.0** for Arduino stubs; **pytest 9.1.1** for the `scripts/` gate suite |
| **Config file** | `firestarter/platformio.ini` — `[env:native]` and `[env:native_nodevtools]`, each with a 17-entry `test_filter` and a matching `-I` list that **must stay in lockstep** |
| **Quick run command** | `python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""` (0.8 s, 14 cases) for baseline/fixture tasks · `pio test -e native -f "*<suite>*"` for source tasks |
| **Full suite command** | `pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q -o addopts=""` |
| **Estimated runtime** | ~35 s native (per env) · 11.5 s `pytest tests/` · ~90 s for three cold AVR builds |

**Run location matters.** `pytest tests/` must be run from `/workspaces/firestarter`, not a `/tmp`
worktree — `tests/meta_presence.py:77-97` probes for a `.git` marker in the firmware repo's *parent*
and silently skips **32 cross-repo legs** when it is absent (355 vs 323+32, both measured this
session — RESEARCH F-12). Every prior phase's worktree measurement under-ran the suite without
saying so.

**Measured baseline at `785e644`, clean tree:**

| Leg | Baseline |
|-----|----------|
| `pio test -e native` | **184 cases / 17 suites / 184 succeeded** |
| `pio test -e native_nodevtools` | **184 / 17 / 184** |
| `python3 -m pytest tests/ -q` (from `/workspaces/firestarter`) | **355 passed, 0 failed, 0 skipped** (11.5 s) |
| `python3 -m pytest tests/test_check_size_baseline.py -q` | **14 passed** (0.76 s) |
| Cold `pio run` | flash **23090 / 23138 / 25234**, RAM **1562 / 1568 / 2003**, **0** warnings |
| `size_baseline.json` `native.cases` | **172** (stale — LAND-01 moves it to the final count) |
| `size_baseline_base01.json` `native.cases` | **141** (frozen at Phase 124 — the pre-existing RED, LAND-03) |

**CI legs, exhaustively, on this branch:** `pio test -e native` (`build.yml:142`) ·
`pio test -e native_nodevtools` (`:155`) · `pytest tests/ -v` (`:161`) · `pio run` (`:193`) ·
`py32f071.yml` ARM build. **Nothing else.** Every `scripts/check_*.py` gate this phase leans on
is a **local-run obligation** — that is LAND-04's whole content.

---

## Sampling Rate

- **After every task commit:** `python3 -m pytest tests/test_check_size_baseline.py -q -o addopts=""` (0.8 s) for any baseline/fixture task; `pio test -e native -f "*<suite>*"` for any source task.
- **After every plan wave:** three cold `pio run` + `pio test -e native` + `pio test -e native_nodevtools` + `python3 -m pytest tests/ -q -o addopts=""` from `/workspaces/firestarter`.
- **Before `/gsd-verify-work`:** the full eight-leg phase ledger the sibling phases used — cold `pio run` ×3, both native envs, `pytest tests/`, `check_build_warnings.py --rebuild`, `check_no_heap_or_64bit_symbols.py`, `check_size_baseline.py --policy merge05` (both `--avr-log` and `--rebuild` forms), `check_size_baseline.py` default mode, and the host suite from `firestarter_app`.
- **Max feedback latency:** 35 s (one native env) for source tasks; 1 s for baseline/fixture tasks.

**One gate flips polarity in this phase, and the plan must say so up front.**
`check_size_baseline.py` **default mode** has been RED since Phase 155 (`157-after-figures.md`
leg 7 records six failing lines). After LAND-01 it must be **GREEN**. That flip is LAND-01's own
discharge evidence — not an incidental side effect.

---

## Per-Task Verification Map

| Req | Behaviour | Test type | Automated command | File exists |
|-----|-----------|-----------|-------------------|-------------|
| **LAND-01** | re-recorded file matches a cold measurement of the committed tree | build + gate | `for e in uno uno328pb leonardo; do rm -rf .pio/build/$e; pio run -e $e; done` then `python3 scripts/check_size_baseline.py --avr-log uno=… --avr-log uno328pb=… --avr-log leonardo=…` (default mode = byte identity) | ✅ existing — **local only** |
| **LAND-01** | BASE-01's growth axis is unmoved | source contract | `python3 -m pytest tests/test_check_size_baseline.py::test_base01_is_not_re_anchored_by_the_new_exemption -q -o addopts=""` | ✅ existing (`:1108`) — **runs in CI** |
| **LAND-02** | policy run is green and prints negative deltas | gate | canonical `--policy merge05 --baseline scripts/baseline/size_baseline_base01.json --avr-log ×3`, exit 0 | ✅ existing — **local only** |
| **LAND-02** | severance is complete — no leg reads a stale figure | gate | `python3 -m pytest tests/test_check_size_baseline.py tests/test_check_build_warnings.py -q -o addopts=""` → **24 passed** | ✅ existing — **runs in CI**. This is the leg that catches an incomplete severance |
| **LAND-02** | the tripwire is still armed above the (unchanged) allowance | planted negative | the three surviving `planted_size_baseline_policy_*_v153.log` legs (`:1202`, `:1257`, `:1298`) — **measured to stay green**, so assert that fact rather than re-planting | ✅ existing |
| **LAND-03** | the mismatch is resolved | gate | `python3 scripts/check_size_baseline.py --policy merge05 --baseline scripts/baseline/size_baseline_base01.json --rebuild` → exit 0 | ✅ existing — **local only** |
| **LAND-04** | the grep claim holds, with its second clause | record + command | `grep -rn "check_size_baseline" .github/; echo $?` → `1`; plus `grep -n "pytest tests/" .github/workflows/build.yml` → `:161` | ✅ existing |
| **LAND-05** | narrowing does not change parse behaviour | unit | `pio test -e native -f "*test_read_timing*"` (the only suite allocating the real 64-token budget) then full `pio test -e native && pio test -e native_nodevtools` → **184/184 both** | ✅ existing (`test_read_timing_params.cpp:84`) — **runs in CI** |
| **LAND-05** | the RAM saving is real | build | `pio run -e uno` → `RAM: used 1434` (from 1562) — the linker is the witness | ✅ existing |
| **LAND-05** | `start`/`end` remain signed | source contract | **Wave 0** — a leg asserting `int start;` / `int end;` in `jsmn.h`, so a future tidy-up to `uint16_t` cannot silently break the twelve `-1` sentinels | ❌ **Wave 0** |
| **LAND-06** | the measurement is cited (declined branch) | build + disassembly | `pio run -e uno` flash delta + `avr-objdump -d` call-site count inside `flash_5v_page_write_execute` — reproduces `+22/+24/+22 B` and the two `__udivmodsi4` sites | ✅ existing tooling |
| **LAND-07** | the arithmetic is reproducible by a reader | record | the `jsmn_count` snippet in RESEARCH § Code Examples, run against `pinouts.json` | ✅ script inlined in the record; no committed test needed for a record-only criterion |
| **LAND-08** | the flakiness record carries its evidence | record | three timed `pio test -e native` runs on the committed tree, case count + wall time each | ✅ existing |

*Status legend: ✅ existing · ❌ Wave 0 · **local only** = in no CI workflow (LAND-04)*

---

## Wave 0 Requirements

- [ ] A source-contract leg pinning `int start;` / `int end;` in `lib/jsmn/src/jsmn.h` — covers **LAND-05**'s signedness clause. A `grep`-style assertion in `tests/`. **Adding a `tests/` file does not move native case counts**, so it does not interact with LAND-01's re-record.
- [ ] `captured_build_v158_{uno,uno328pb,leonardo}.log` + `planted_size_baseline_flash_regression_v158.log` — the **new `*_v158*` fixture family** required by LAND-02's severance. 4 new fixtures + 2 updated in place (not the 13 every prior generation used: because no MERGE-05 exemption is authored for a *reduction*, all three policy plants stay valid — measured).

*LAND-06's conditional page-boundary Wave 0 gap is **dropped** — the operator declined the mask
rewrite, so no `test_val_5v_page` cases are added and the native count does not move for its sake.*

*No framework install is needed — Unity, ArduinoFake and pytest are all present.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ARM (`py32f071`) build with the narrowed `jsmntok_t` | LAND-05 | `arm-none-eabi-gcc` and `cmake` are **absent** from this devcontainer; `platform/py32f071/CMakeLists.txt:70` compiles the same `jsmn.c`, so the narrowing is a cross-architecture edit | Attempt the toolchain install once (it is known installable — needs two newlib packages CI omits). If it succeeds, build and record. If it fails, **record the ceiling** in `158-after-figures.md` rather than implying ARM coverage, and let `py32f071.yml` witness it at push time |
| Runtime win from LAND-06's mask | LAND-06 | D-02 forbids a bench criterion for this milestone; only silicon could measure it | **Not performed.** The decline is recorded with its size measurement and the zero-coverage gap as the stated reason |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (LAND-05 signedness leg; `*_v158*` fixture family)
- [ ] No watch-mode flags
- [ ] Feedback latency < 35s
- [ ] `pytest tests/` measured from `/workspaces/firestarter`, never a `/tmp` worktree
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
