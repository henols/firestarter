---
phase: "206"
slug: "dev-test-keeps-its-fidelity-on-one-session"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-09-23"
---

# Phase 206 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `206-RESEARCH.md` § Validation Architecture. The Per-Task
> Verification Map is filled once PLAN.md task IDs exist.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `firestarter_app/pyproject.toml` (`addopts = "-ra -q"`) |
| **Interpreter** | `firestarter_app/.venv311/bin/python` (3.11.16) — CI parity is mandatory; never bare `python3` (3.12) |
| **Quick run command** | `cd firestarter_app && .venv311/bin/python -m pytest tests/test_chip_test.py tests/test_blast_radius_invariance.py tests/test_diagnostic_report.py -o addopts="" -q` |
| **Full suite command** | `cd firestarter_app && .venv311/bin/python -m pytest tests/ -o addopts="" --cov=firestarter --cov-report=term-missing --cov-fail-under=70` |
| **Estimated runtime** | ~20 s quick · ~120 s full |
| **Baseline** | 2333 tests collected. ⚠ With a board on `/dev/ttyACM0`, `test_no_programmer_found_*` are expected RED — record the pre-change failing-id set before touching anything and diff against it, never against "all green". |

---

## Sampling Rate

- **After every task commit:** Run the quick run command
- **After every plan wave:** Run the full suite on `.venv311`, diffed against the pre-phase failing-id set
- **Before `/gsd-verify-work`:** Full suite + `ruff check firestarter/ tests/` + `ruff format --check firestarter/ tests/` green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| *(filled by `/gsd-validate-phase` once PLAN.md task IDs exist)* | | | | | | | | | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Requirement → behaviour map (from research, pre-task-ID)

| Req | Behaviour | Type | Automated Command | Exists? |
|---|---|---|---|---|
| DEVTEST-01 | blank-check step carries compare evidence | unit | `pytest tests/test_chip_test.py -k blank_check -o addopts=""` | ⚠️ module exists; new cases → Wave 0 |
| DEVTEST-01 | verify step's fingerprint is no less informative | unit | `pytest tests/test_chip_test.py -k fingerprint -o addopts=""` | ✅ partial |
| DEVTEST-01 | the 2922-case behavioural corpus still shows zero differences | integration | `pytest tests/test_compare.py -o addopts=""` | ✅ |
| DEVTEST-02 | all 19 frozen literals unmoved | unit | `pytest tests/test_blast_radius_invariance.py::test_dedup_fingerprint_is_frozen -o addopts=""` | ✅ **the gate** |
| DEVTEST-02 | the new tag is reachable and actually re-keys when present | unit | new — planted-mutation non-vacuity leg | ❌ Wave 0 |
| DEVTEST-02 | a legacy/default `StepResult` takes the untagged branch | unit | new | ❌ Wave 0 |
| DEVTEST-03 | verdict 1 vs verdict 2 land on distinct outcomes | unit | `pytest tests/test_chip_test.py tests/test_devtest_firmware_error_propagation.py -o addopts=""` | ⚠️ new cases |
| DEVTEST-03 | a transport failure in a cycle-block step exits 2, not 0 | unit | new — **must be seen RED first** | ❌ Wave 0 |
| DEVTEST-03 | exit-code precedence unchanged | unit | `pytest tests/test_dev_test_cmd.py -o addopts=""` | ✅ |
| SESS-01 | a leased plan opens one link; a cold plan is byte-identical | unit | new — connect count on a fake transport, **both** paths | ❌ Wave 0 |
| SESS-01 | a mid-plan `SerialError` drops the lease and the plan continues | unit | new | ❌ Wave 0 |
| SESS-02 | measured wall clock, before vs after | **manual / bench** | `checkpoint:human-verify` — NOT automatable | ❌ operator |

---

## Wave 0 Requirements

- [ ] A test that a `StepResult` with the new discriminator field at its default produces an **untagged** `dedup_fingerprint` — covers DEVTEST-02
- [ ] A planted-mutation leg proving the new tag is **capable** of moving the hash (non-vacuity; `test_the_197_delta_layer_is_capable_of_failing` precedent)
- [ ] A cycle-block transport-failure → exit-2 regression test — **must be seen RED before the fix**
- [ ] Lease tests asserting **both** the leased and the cold path, so reverting the lease commit cannot redden the suite
- [ ] The pre-phase failing-id set, recorded (live-board reds)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Wall-clock saving of the leased link, measured on a real `dev test` plan | SESS-02 | `dev test` writes to the chip and energizes VPP/VPE; needs a real board and a real socketed part. Cannot be simulated. | Operator-initiated. Leonardo on `/dev/ttyACM0`. Time a full `dev test` plan before and after the lease, same chip, same run count (`_DEFAULT_RUNS = 3`). **Never pass `--submit`** on a measurement run. Record both numbers in `206-SESSION-COST.md`. |
| Confirm the socket is occupied and by which part | SESS-02 | Operator-owned; cannot be determined without energizing the rail. | Ask the operator before any bench leg. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
