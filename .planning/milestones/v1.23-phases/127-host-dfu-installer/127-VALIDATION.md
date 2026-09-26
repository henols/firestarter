---
phase: 127
slug: host-dfu-installer
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-01
updated: 2026-08-01
---

# Phase 127 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
>
> **Repo:** all commands run in `firestarter_app/`, which MUST sit in the sibling layout
> (`<root>/firestarter_app` next to `<root>/firestarter`). `test_sdp_bus_config_drift.py:22`
> and `test_gen_validation_header.py:21` hardcode `_REPO_ROOT / "firestarter_app"` — a
> wrongly-named working directory produces 6 spurious failures. See `127-RESEARCH.md` §Q1.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (existing; `.[test]` extra) |
| **Config file** | `firestarter_app/pyproject.toml` |
| **Quick run command** | `python -m pytest tests/test_py32_dfu.py -q` |
| **Full suite command** | `python -m pytest -q` |
| **Estimated runtime** | ~60 s full suite; ~3 s for the py32 subset |
| **Pre-merge baseline** | 1158 collected · 1158 passed · **0 skipped** · 0 failed (MEASURED in the real checkout during planning) |
| **Post-merge expectation** | 1216 collected · 1216 passed · **0 skipped** · 0 failed · coverage ≥70% (1158 + 58 from `test_py32_dfu.py`) |
| **Why not research's 1213/3-skipped** | `127-RESEARCH.md` §Q1 measured **1216 collected · 1213 passed · 3 skipped** in a *scratch worktree*. Those 3 skips are a worktree artifact — they fire only when `.planning/` is unreachable. In the real sibling checkout `.planning/` resolves, so those tests **run** rather than skip. Expect **0 skipped**; a non-zero skip count in the evidence run means the layout is wrong, not that the suite regressed. |
| **Second leg** | `ci-py32` — `pip install -e .[test,py32]`, runs the pyusb-API-surface tests only (D-02) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_py32_dfu.py -q` (plus the new
  test module the task touched)
- **After every plan wave:** Run `python -m pytest -q` — full suite, 0 failures
- **Before `/gsd-verify-work`:** Full suite green **in the sibling layout**, and the collected
  count recorded verbatim (D-04 — recorded, never asserted)
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

Filled by the planner from the twelve PLAN.md files. Every task carries an `<automated>` verify;
none is manual-only. Commands are run from `/workspaces/firestarter_app` in the sibling layout unless
stated otherwise.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 127-01-01 | 01 | 1 | HOST-01 | T-127-01-01/02 | Merge strategy pinned; layout asserted before any count | integration | `git log -1 --format=%P \| grep 4ee64a14a8933b60896c8b168bb1c7e34d788fa4` + `pytest tests/ -q` | ✅ | ⬜ pending |
| 127-01-02 | 01 | 1 | HOST-01 | T-127-01-05 | Comment-only diff; `asset_candidates()` untouched | source scan | `grep -c 'accepted deviation' firestarter/firmware.py` + `pytest tests/test_firmware_install.py -q` | ✅ | ⬜ pending |
| 127-02-01 | 02 | 2 | HOST-07 | T-127-02-01 | Exact floor incl. upper bound; `pyusb` absent from `test` | textual | `grep -c 'pyusb>=1.3.1,<2' pyproject.toml` | ✅ | ⬜ pending |
| 127-02-02 | 02 | 2 | HOST-07, HOST-01 | T-127-02-02/03/04 | Non-vacuity + planted-file RED on both gates | unit | `pytest tests/test_py32_packaging.py -q` | ❌ new | ⬜ pending |
| 127-03-01 | 03 | 2 | HOST-06 | T-127-03-02 | C-2 re-derived; blob SHA pinned before any edit | evidence | `git rev-parse HEAD:tests/test_py32_dfu.py` | ✅ | ⬜ pending |
| 127-03-02 | 03 | 2 | HOST-06 | T-127-03-01/04 | Independent oracle; forward-holding scan w/ non-vacuity | unit | `pytest tests/test_dfu_opcode_anchors.py -q` | ❌ new | ⬜ pending |
| 127-04-01 | 04 | 2 | HOST-02 | T-127-04-01/02 | One refusal code path; exit 2 on simulated stable | subprocess | inline `-c` preamble probe (in-task) + `pytest tests/test_cli_handlers.py -q` | ✅ | ⬜ pending |
| 127-04-02 | 04 | 2 | HOST-02, HOST-08 | T-127-04-04/05/06 | One subprocess per version; child pre-asserts import order | subprocess | `pytest tests/test_py32_channel_gating.py -q` | ❌ new | ⬜ pending |
| 127-04-03 | 04 | 2 | HOST-08 | T-127-04-02/04 | Criterion 5's explicit import-time assertion; one-code-path guard | subprocess+unit | `pytest tests/test_py32_channel_gating.py -v` | ❌ new | ⬜ pending |
| 127-05-01 | 05 | 2 | (D-13, no HOST id) | T-127-05-01/06/07 | Envelope bounded on `APP_REGION_END`; non-overridable | unit | inline constant probe (in-task) + `pytest tests/test_py32_dfu.py -q` | ✅ | ⬜ pending |
| 127-05-02 | 05 | 2 | (D-13, no HOST id) | T-127-05-01 | Both boundaries + rogue-128-KiB regression pin | unit | `pytest tests/test_py32_flash_map_host.py -q` | ❌ new | ⬜ pending |
| 127-05-03 | 05 | 2 | (D-14, no HOST id) | T-127-05-02/03/04/05/08 | Fail-CLOSED cross-repo gate; non-vacuity; planted-copy RED | cross-repo | `pytest tests/test_py32_flash_map_host.py -v` + `pytest tests/test_skip_census.py -q` | ❌ new | ⬜ pending |
| 127-06-01 | 06 | 2 | HOST-04 | T-127-06-03/07 | `collect_ignore` armed correctly; entries exist; ast call-site scan | unit | `pytest tests/test_pyusb_gating.py -q` + `pytest tests/ -q` | ❌ new | ⬜ pending |
| 127-06-02 | 06 | 2 | HOST-04 | T-127-06-01/02/06 | Real `usb.core.find` either/or; narrow except; signature pinned | integration | throwaway venv `.[test,py32]` → `pytest tests/test_pyusb_api_surface.py -q` | ❌ new | ⬜ pending |
| 127-06-03 | 06 | 2 | HOST-04 | T-127-06-04/08 | `workflow_dispatch:` only; no branch literal in `push:` | config | ci.yml structural probe (in-task) + `pytest tests/test_pyusb_gating.py -q` | ✅ | ⬜ pending |
| 127-07-01 | 07 | 3 | HOST-05 | T-127-07-03/04/05 | Pragma count 2; message substrings; `__cause__` chain | unit+coverage | `pytest tests/test_py32_pyusb_absent.py -q` + `pytest tests/ --cov-fail-under=70` | ❌ new | ⬜ pending |
| 127-07-02 | 07 | 3 | HOST-05 | T-127-07-01/02/06/07 | Blocker raises; `usb` never in child `sys.modules` | subprocess | `pytest tests/test_py32_pyusb_absent.py -v` in **both** envs | ❌ new | ⬜ pending |
| 127-08-01 | 08 | 4 | HOST-03 | T-127-08-01/02 | One `_finish()` site; `device.calls` identical before/after | unit | `grep -c 'self._finish(' firestarter/py32_dfu.py` + `pytest tests/test_py32_dfu.py -q` (58) | ✅ | ⬜ pending |
| 127-08-02 | 08 | 4 | HOST-03 | T-127-08-04/05 | UPLOAD arm address-derived; `attributes=` defaulted | unit | inline fake probe (in-task) + `pytest tests/test_py32_dfu.py -q` | ✅ | ⬜ pending |
| 127-08-03 | 08 | 4 | HOST-03, HOST-04 | T-127-08-03/06 | Fake vs real `ctrl_transfer` signature, non-vacuous | integration | throwaway venv → `pytest tests/test_pyusb_api_surface.py -q` | ❌ new | ⬜ pending |
| 127-09-01 | 09 | 5 | HOST-03 | T-127-09-01/03/05/09 | `download → readback → _finish`; mismatch raises pre-`_finish` | unit | inline `VerifyResult` probe (in-task) + `pytest tests/test_dfu_opcode_anchors.py -q` | ✅ | ⬜ pending |
| 127-09-02 | 09 | 5 | HOST-03 | T-127-09-01/02/04/05/07 | All four outcomes; ordering on `device.calls` indices | unit | `pytest tests/test_py32_dfu.py -v` | ✅ | ⬜ pending |
| 127-09-03 | 09 | 5 | HOST-03 | T-127-09-01/06/08 | *written but NOT verified*; `asset_candidates()` byte-identical | unit+coverage | `grep -c 'written but NOT verified' firestarter/firmware.py` + `pytest tests/ --cov-fail-under=70` | ✅ | ⬜ pending |
| 127-10-01 | 10 | 6 | (D-15) HOST-03, HOST-07 | T-127-10-01/02/03/04 | Scoped diff; no heading added or removed | textual | doc grep set (in-task) + `pytest tests/ -q` | ✅ | ⬜ pending |
| 127-10-02 | 10 | 6 | (D-15) HOST-03, HOST-07 | T-127-10-05/06 | Expectations derived from `APP_REGION_END`, not literals | unit | `pytest tests/test_py32_packaging.py -q` | ✅ | ⬜ pending |
| 127-11-01 | 11 | 7 | HOST-04 | T-127-11-01/06 | Commands printed, not executed; trigger safety re-derived | evidence | local gate sweep (in-task); `git ls-remote --heads origin` read-only | ✅ | ⬜ pending |
| 127-11-02 | 11 | 7 | HOST-04 | T-127-11-01 | **Structural** operator gate — no task may push or dispatch | checkpoint | *(none — `checkpoint:human-action`; resumes on a run id datum)* | n/a | ⬜ pending |
| 127-11-03 | 11 | 7 | HOST-04 | T-127-11-02/03/04/05/08 | Every field re-derived read-only; pushed ref verified | evidence | `gh run view` (read-only) + `git show origin/…:.github/workflows/ci.yml` | ✅ | ⬜ pending |
| 127-12-01 | 12 | 8 | HOST-01…08 | T-127-12-01/04 | Layout precondition first; every row re-executed in-session | sweep | full gate sweep (in-task) | ✅ | ⬜ pending |
| 127-12-02 | 12 | 8 | HOST-01…08 | T-127-12-06/07 | Claim gate with an explicit target; quotable ceiling | doc gate | `python3 .planning/phases/123-…/check_permitted_claims.py <artifact>` | ✅ | ⬜ pending |
| 127-12-03 | 12 | 8 | HOST-01…08 | T-127-12-01/02/03/09 | HOST-03 cited to 127-08/09 only; HOST-04 gated on the run URL | ledger | `grep -n 'HOST-0' .planning/REQUIREMENTS.md` + both sub-repos' porcelain | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky. `File Exists` = whether the automated command's target
module exists **before** the task runs; `❌ new` means the task creates it.*

**Sampling continuity:** no three consecutive tasks lack an automated verify — every task has one except
`127-11-02`, which is the structural operator gate and is bracketed by `127-11-01`'s local sweep and
`127-11-03`'s read-only re-derivation.

**The one deliberate non-gate:** D-04's collected-test count is **recorded, never asserted**. Phase 123
D-10 rejected a pinned count for measured flakiness and `test_skip_census.py::test_no_pinned_skip_count`
enforces that rejection. This is a reasoned exception to the standing operator preference for an exit
code over a human reading output — `127-NONREGRESSION.md` §2 must say so explicitly.

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements — pytest, `tests/fw_presence.py`'s
`@requires_fw`, `tests/test_skip_census.py`'s subprocess harness, and `_FakeUsbDevice` are all
already present and are the sanctioned mechanisms for HOST-03/04/05/08 (see `127-RESEARCH.md`
§Q4, §Q5). No framework install and no new fixtures directory are needed.

The one genuinely new local capability is a **pyusb-present environment**, which is created by
the `ci-py32` CI leg (D-02) rather than by a Wave 0 task — `pyusb` must NOT be installed into
the devcontainer's shared environment, because the pyusb-**absent** tests characterise that
environment.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The `ci-py32` leg actually runs green on GitHub Actions | HOST-04 | D-01: evidence requires `git push` + `gh workflow run`, and **no task in any plan may execute either command**. The structural separation is the gate, not the checkpoint type. | Operator personally runs `git push` then `gh workflow run ci.yml --ref v1.23-py32f071-integration`; records the run URL and conclusion in `127-NONREGRESSION.md`. Pushing this branch fires no release workflow (verified: `beta-release.yml` is `beta`-only, `release.yml`/`ci.yml` push are `main`-only, `publish.yml` is `release: published`). |
| Real DFU install against PY32F071 silicon | HOST-03 | **No PCB exists.** The permitted ceiling is mock/descriptor-level only. | NOT PERFORMED, and must not be claimed. Phase 130 CLOSE-02 cites "the mock-only ceiling on HOST-03" — this phase must produce that non-claim in citable form. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies — 30 of 31 tasks carry one; the exception is `127-11-02`, the structural operator gate, which is bracketed by automated tasks on both sides
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references — no framework install and no new fixtures are needed; the only new local capability (a pyusb-present environment) is created by a throwaway venv for rehearsal and by the `ci-py32` leg for evidence, never by installing pyusb into the shared devcontainer
- [x] No watch-mode flags
- [x] Feedback latency < 60s — the per-task commands are single modules (~3 s); only the full-suite sweeps run to ~150 s and those are per-wave, not per-task
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** planner, 2026-08-01. Twelve plans, eight waves; the Per-Task Verification Map above is
derived from the task IDs in `127-01-PLAN.md` … `127-12-PLAN.md`.
