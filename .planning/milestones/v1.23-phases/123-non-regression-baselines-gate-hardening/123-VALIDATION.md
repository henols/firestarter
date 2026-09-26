---
phase: 123
slug: non-regression-baselines-gate-hardening
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-30
---

# Phase 123 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `123-RESEARCH.md` §"Validation Architecture" — every command below was run
> and timed in the research session.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` (both sub-repos) |
| **Config file** | firmware: **none** — no `pytest.ini`/`conftest.py`; the no-conftest house rule is recorded at `firestarter/tests/test_update_version.py:28`. host: `firestarter_app/pyproject.toml` + `tests/conftest.py` |
| **Quick run command** | firmware: `cd firestarter && python3 -m pytest tests/ -q` (~0.04 s, 8 tests) · host 7-module set: `cd firestarter_app && python3 -m pytest tests/test_revision_constants_parity.py tests/test_dispatch_mirror.py tests/test_sdp_bus_config_drift.py tests/test_check_no_log_in_sdp_window.py tests/test_sdp_table_parity.py tests/test_check_is_memory_cmd_no_ifdef.py tests/test_gen_validation_header.py -q` (49 tests, sub-second) |
| **Full suite command** | host: `cd firestarter_app && python3 -m pytest tests/ -q` (1134 tests) · firmware native: `cd firestarter && pio test -e native && pio test -e native_nodevtools` (~38 s combined) |
| **Estimated runtime** | quick < 1 s · full host ~40 s · full firmware native ~38 s |

---

## Sampling Rate

- **After every task commit:** the quick run for the repo touched (firmware `pytest tests/ -q`, or the
  host 7-module set).
- **After every plan wave:** full host suite (expect **1134 passed, 0 skipped**) plus the host gate trio
  (`ruff check`, `ruff format --check`, `python tools/check_mypy_watermark.py`) if any host `.py`
  changed; firmware `pytest tests/ -q` plus **both** native envs if any firmware file changed.
- **Before `/gsd-verify-work`:** both native envs at **141 cases / 17 suites, all PASSED**; all three
  AVR clean builds at the recorded flash/RAM; host suite 1134/0-skipped; every planted-fixture test
  green; and the D-05 verbatim-evidence artifact (the `122-NONREGRESSION.md` shape) recorded.
- **Max feedback latency:** ~40 s (worst case: full host suite).

---

## Per-Task Verification Map

Task IDs are assigned when plans are written; this map is the requirement→test contract the plans
must satisfy. Status column is updated during execution.

| Req | Behavior | Test Type | Automated Command | File Exists | Status |
|-----|----------|-----------|-------------------|-------------|--------|
| BASE-01 | Baseline JSON records 6 AVR numbers + 2 native pairs + warning watermarks | unit | `pytest firestarter/tests/ -q` | ❌ W0 | ⬜ pending |
| BASE-01 | Parser extracts used/total from both `RAM:` and `Flash:` lines | unit (captured-output fixture) | same | ❌ W0 | ⬜ pending |
| BASE-01 | Comparator exits non-zero on an inflated flash figure | unit (planted) | same | ❌ W0 | ⬜ pending |
| BASE-01 | Comparator exits **2** on unparseable input | unit (planted) | same | ❌ W0 | ⬜ pending |
| BASE-02 | Present repo + missing scan target ⇒ **hard failure**, not skip | integration (subprocess + committed fake sibling) | `pytest firestarter_app/tests/ -q` | ❌ W0 | ⬜ pending |
| BASE-02 | Absent repo (no `.git`) ⇒ honest skip | integration (subprocess) | same | ❌ W0 | ⬜ pending |
| BASE-02 | All 7 modules key on `.git`, none on a single file | unit (recurrence lint) | same | ❌ W0 | ⬜ pending |
| BASE-03 | Skip reason "firmware absent" while `.git` exists ⇒ suite fails | integration (subprocess) | same | ❌ W0 | ⬜ pending |
| BASE-03 | Unrecognised skip reason ⇒ fails | unit | same | ❌ W0 | ⬜ pending |
| BASE-04 | Mismatched source path ⇒ exit non-zero | unit (planted) | `pytest firestarter/tests/ -q` | ❌ W0 | ⬜ pending |
| BASE-04 | Omission listed in `PY32_EXCLUDED` ⇒ exit 0 | unit (planted) | same | ❌ W0 | ⬜ pending |
| BASE-04 | `platform/py32f071/` absent ⇒ UNARMED, exit 0 | unit | same | ❌ W0 | ⬜ pending |
| BASE-05 | `RURP_*_PROVISIONAL` with zero consumers ⇒ exit non-zero | unit (planted) | same | ❌ W0 | ⬜ pending |
| BASE-05 | Same macro with ≥1 consumer ⇒ exit 0 | unit (planted control) | same | ❌ W0 | ⬜ pending |
| BASE-06 | One macro redefinition in real compiled output ⇒ exit non-zero | unit (planted, host `g++`) | same | ❌ W0 | ⬜ pending |
| BASE-06 | AVR envs hold at **zero**; native envs hold at the **360** watermark | unit (captured-log fixture) | same | ❌ W0 | ⬜ pending |
| BASE-06 | Parser survives pio's surrounding framing | unit (captured real-output fixture) | same | ❌ W0 | ⬜ pending |
| BASE-07 | Forbidden phrase near a py32 token ⇒ exit non-zero | unit (planted) | `pytest .planning/phases/123-*/ -q` | ❌ W0 | ⬜ pending |
| BASE-07 | Same phrase with **no** py32 token nearby ⇒ exit 0 (D-16 both directions) | unit (clean AVR control) | same | ❌ W0 | ⬜ pending |
| BASE-07 | Empty target list ⇒ exit non-zero, never falls back to defaults | unit | same | ❌ W0 | ⬜ pending |
| BASE-07 | Missing required caveat ⇒ exit non-zero | unit (planted) | same | ❌ W0 | ⬜ pending |
| BASE-07 | Zero named targets exist ⇒ UNARMED exit 0; any one exists ⇒ all must (D-15) | unit | same | ❌ W0 | ⬜ pending |
| BASE-08 | Every `firestarter/scripts/check_*.py` has a paired test + planted fixture | meta-test | `pytest firestarter/tests/ -q` | ❌ W0 | ⬜ pending |
| BASE-08 | Zero-match glob fails (hardcoded floor count) | meta-test | same | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Sampling subtlety specific to this phase (load-bearing).** Most tests above *prove a failure* —
their green state means "the checker correctly exited non-zero". A task reporting "all tests pass"
without naming which assertion fired is indistinguishable from a checker that silently passed
everything (the v1.12 hollow-GATE-03 mode). **Every planted-fixture test must assert both the
non-zero exit AND a distinctive substring of the failure message**, exactly as v1.22's tests assert
`"should-now-work"` and `"missing required silicon caveat"` by name.

---

## Wave 0 Requirements

- [ ] `firestarter/tests/fixtures/` — directory does not exist; every firmware-side planted fixture needs it
- [ ] `firestarter/scripts/*.py` — no Python checker exists there yet (only `check_uno_ram.sh`)
- [ ] Committed captured-pio-output fixtures (size lines, test summary line, a real macro-redefinition excerpt) — measured during research; capture verbatim rather than re-measuring later
- [ ] `firestarter_app/tests/fixtures/fake_firestarter/` — the committed incomplete sibling tree
- [ ] Shared FW-presence helper module in `firestarter_app/tests/` — does not exist; 7 modules each roll their own
- [ ] D-11 central scan-path inventory — does not exist
- [ ] `.planning/phases/123-…/fixtures/` — the claim-gate fixtures, including the D-16 clean-AVR control that has no v1.22 analogue
- [ ] **No framework install needed** — pytest present in both repos

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The nine cross-repo gates **run rather than skip** | BASE-02 / BASE-03 (consumed by Phase 124's MERGE-07) | D-05: no CI leg is added, and host CI never checks out the firmware sibling. Proof is a local run with recorded output. | From `/workspaces/firestarter_app` with the `firestarter` sibling present, run the 7-module quick set plus the skip census; record command + verbatim output in the phase's non-regression artifact (`122-NONREGRESSION.md` shape) |
| AVR flash/RAM baseline figures | BASE-01 | Requires a local `pio` clean build; no CI job publishes these numbers | `cd firestarter && pio run -t clean -e {uno,uno328pb,leonardo} && pio run -e …`, capture the `Flash:`/`RAM:` lines |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 40 s
- [ ] Every planted-fixture test asserts non-zero exit **and** a distinctive failure substring
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
