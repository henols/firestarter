---
phase: 124
slug: firmware-integration-merge
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-31
---

# Phase 124 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `124-RESEARCH.md` §"Validation Architecture". Where this file and
> `124-CONTEXT.md` disagree, RESEARCH.md's corrections table (C-1…C-18) wins.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PlatformIO + Unity (firmware native); pytest 9.1.1 (firmware scripts + host) |
| **Config file** | `firestarter/platformio.ini`; `firestarter_app/pyproject.toml` |
| **Quick run command** | `cd firestarter && pio test -e native` (~40 s warm, ~105 s cold) |
| **Full suite command** | `cd firestarter && pio test -e native && pio test -e native_nodevtools && python3 -m pytest tests/ -q` then `cd ../firestarter_app && python3 -m pytest` |
| **Estimated runtime** | ~6–8 min full sweep (both native envs + 3 AVR clean builds + both pytest suites) |
| **ARM** | CMake + Ninja via `py32f071.yml` — **CI only**; `arm-none-eabi-gcc`, `cmake`, `ninja` all absent locally |

---

## Sampling Rate

- **After every task commit:** run the touched gate only (`pio test -e native`, or the specific `pytest` module).
- **After every plan wave:** both native envs + all three AVR clean builds + `firestarter` pytest.
- **Before `/gsd-verify-work`:** the full `124-NONREGRESSION.md` sweep, re-executed (D-16), not copied from prior SUMMARY files.
- **Max feedback latency:** ~105 s (cold `pio test -e native`).

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | — | — | MERGE-01 | — | no commit carries the portability half without the py32 stack | git range check | new script — `git rev-list` loop over `<fork>..HEAD` | ❌ W0 | ⬜ pending |
| TBD | — | — | MERGE-02 | — | manifest names `flash_nor_unlock.cpp`/`flash_5v_page.cpp` | textual gate | `python3 scripts/check_cmake_manifest.py` | ✅ (self-arms on landing) | ⬜ pending |
| TBD | — | — | MERGE-02 | — | ARM configures **and** builds | CI | `gh workflow run py32f071.yml --ref v1.23-py32f071-integration` → run URL + SHA | ✅ workflow exists | ⬜ pending |
| TBD | — | — | MERGE-03 | — | `push: branches: [beta]` present | source read | `grep -A3 '^on:' .github/workflows/py32f071.yml` | ✅ | ⬜ pending |
| TBD | — | — | MERGE-04 | SAFE | eight bus-driving commands refused under the provisional flag | native suite | new suite at `configure_memory()` (RESEARCH §MERGE-04(a)) | ❌ W0 | ⬜ pending |
| TBD | — | — | MERGE-04 | SAFE | `#error` provably fires when the pinmap macro is unset | pytest + `g++ -E` | new test under `firestarter/tests/` | ❌ W0 | ⬜ pending |
| TBD | — | — | MERGE-04 | — | provisional flag has real consumers | gate | `python3 scripts/check_orphan_provisional.py` (SCAN_DIRS excludes `tests/` — C-12) | ✅ | ⬜ pending |
| TBD | — | — | MERGE-05 | — | Leonardo flash not growing; Uno-class ≤ 64 B; RAM unchanged | gate | `check_size_baseline.py` — **W-1: strict equality, not a policy band** | ⚠ policy gap | ⬜ pending |
| TBD | — | — | MERGE-06 | — | 141 cases / 17 suites, both native envs | gate | `check_size_baseline.py --native-log …` | ✅ measured green | ⬜ pending |
| TBD | — | — | MERGE-06 | — | golden traces byte-identical, per-array for `_shared/sdp_expected.h` | blob SHA + array inventory | RESEARCH §MERGE-06 | ❌ W0 | ⬜ pending |
| TBD | — | — | MERGE-07 | — | eleven gate rows **run** (never SKIP) and pass | tools + pytest | RESEARCH §MERGE-07 table | ✅ measured green | ⬜ pending |
| TBD | — | — | MERGE-08 | — | `FLASH_LATENCY_1` in use at 48 MHz | grep + CI build | `grep -n FLASH_ platform/py32f071/src/main.cpp` + run URL | ✅ | ⬜ pending |
| TBD | — | — | MERGE-08 | — | `write_checksums.cmake` deleted | tree read | `git ls-tree HEAD platform/py32f071/cmake/` | ✅ | ⬜ pending |
| TBD | — | — | MERGE-08 | — | ARM `DEV_TOOLS`-off explicit; uniform `#if DEV_TOOLS` (D-02) | CMake read + native counts | `grep DEV_TOOLS platform/py32f071/CMakeLists.txt`; both native envs still 141/17 | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task IDs are filled in by the planner; this table is the requirement→proof contract the plans must satisfy.*

---

## Wave 0 Requirements

- [ ] Criterion-1 range-check script (MERGE-01 / D-06) — asserts no commit in `<fork_point_firmware>..HEAD` carries the portability files without `platform/py32f071/`
- [ ] **W-1 resolution** — AVR size policy: `check_size_baseline.py`'s `compare_avr()` is strict equality and exits 1 on the *permitted* −56/+22/+28. Either add a policy mode or re-baseline with a recorded comparison. MERGE-05 has no exit code until this is settled.
- [ ] **W-2 resolution** — native warning watermark re-measured with build state pinned. Recorded 360 is a **warm-cache** number; the same unmerged tree measures **456** cold, and the landing takes it to **998**.
- [ ] **W-3** — rewrite the two Phase-123 pytests that assert `startswith("UNARMED:")` (`test_check_cmake_manifest.py`, `test_check_orphan_provisional.py`). They expire at this landing and do **not** recover once the gates are fixed.
- [ ] MERGE-04 native refusal suite + the `g++ -E` fire-proof pytest
- [ ] Golden-trace per-array inventory check for `_shared/sdp_expected.h`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ARM CMake configure + build | MERGE-02 | `arm-none-eabi-gcc`, `cmake`, `ninja` are absent from this devcontainer — no local ARM build is possible | Push `v1.23-py32f071-integration`, `gh workflow run py32f071.yml --ref v1.23-py32f071-integration`, capture the run URL + head SHA. Evidence is the run URL + SHA, never a local `pio` run. |
| Pushing the milestone branch to `origin` | MERGE-02 evidence | Outward-facing action (D-09). `--chain`/`--auto` auto-approve human-verify checkpoints, so this needs a gate the chain cannot wave through | Operator confirms before the push. Verified safe: no workflow triggers on this branch (C-14). |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (6 items above)
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
