---
phase: 128
slug: release-asset-fold
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-01
---

# Phase 128 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `128-RESEARCH.md` § Validation Architecture. This phase is **dual-repo**
> (D-08): firmware `firestarter/` plus one commit in `firestarter_app/`.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (both repos). Firmware: `firestarter/tests/` — **no `conftest.py` anywhere** (recorded house rule). App: `firestarter_app/tests/` with `tests/conftest.py` (`collect_ignore`) |
| **Config file** | Firmware: none for `tests/` (`platformio.ini` governs only `test/`, invisible to these). App: `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | Firmware: `cd firestarter && python3 -m pytest tests/test_check_release_assets.py tests/test_checker_convention.py -q` (~1 s)<br>App: `cd firestarter_app && python3 -m pytest tests/test_py32_asset_name_host.py -q -rs` (~1 s) |
| **Full suite command** | Firmware: `cd firestarter && python3 -m pytest tests/ -v` (what `beta-build.yml:66` runs) **plus** `pio test -e native` and `pio test -e native_nodevtools`<br>App: `cd firestarter_app && python3 -m pytest tests/ -q` |
| **Estimated runtime** | ~1–2 s per quick run; firmware full suite seconds + `pio test` native envs |

---

## Sampling Rate

- **After every task commit:** firmware — `python3 -m pytest tests/ -q`; app — `python3 -m pytest tests/ -q`. Both are seconds.
- **After every plan wave:** firmware — `python3 -m pytest tests/ -v` plus `pio test -e native` and `pio test -e native_nodevtools` (unchanged by this phase; a regression there means something unrelated broke). App — full `python3 -m pytest tests/ -q`.
- **Before `/gsd-verify-work`:** both full suites green; `test_checker_convention.py` green with the raised floors; `git ls-files tests/fixtures/` shows every new fixture; the app cross-repo module observed **PASS not SKIP** under `-rs`; and both dispatch runs recorded with run URL + commit SHA in `128-NONREGRESSION.md`.
- **Max feedback latency:** ~5 seconds for the local pytest loop. **CI-only claims are exempt** — no ARM toolchain exists locally, so every ARM/release assertion is discharged by a workflow run URL + SHA, never a local measurement.

---

## Per-Task Verification Map

Task IDs are assigned at plan time; the rows below are the requirement-level contract every plan must satisfy. `Plan`/`Task ID` fill in during execution.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | REL-01 | — | ARM steps positioned after the version-bump auto-commit, same job | static (YAML order) | Read `beta-build.yml` step order (optionally a pytest asserting ARM step line index > `git-auto-commit-action` line index) | ❌ W0 (optional) | ⬜ pending |
| TBD | TBD | TBD | REL-01 | — | Published image carries `steps.version.outputs.version` | CI assertion | in-workflow `strings` gate over the built image; observed in dispatch run A | ❌ W0 (CI-only) | ⬜ pending |
| TBD | TBD | TBD | REL-02 | T-rehearsal-publish | `firestarter_py32f071.hex` present as a release **asset** | CI + API evidence | `gh release view <rehearsal-tag> --json assets` on run A's draft | ❌ W0 (evidence) | ⬜ pending |
| TBD | TBD | TBD | REL-02 | — | `fail_on_unmatched_files` is never set (glob must warn, not fail) | unit | `cd firestarter && python3 -m pytest tests/test_check_release_assets.py -k unmatched -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | REL-03 | T-incomplete-release | Checker exits non-zero on a planted missing/empty hex | unit (subprocess + fixture) | `cd firestarter && python3 -m pytest tests/test_check_release_assets.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | REL-03 | — | Required set derived from `avr_targets`; **empty key set fails** (non-vacuity) | unit | same module, dedicated test | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | REL-03 | — | The build-root seam is genuinely read (seam precedence) | unit | same module, dedicated test | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | REL-03 | T-incomplete-release | A broken ARM build still publishes three AVR assets | CI evidence | run B's asset list via `gh release view --json assets` | ❌ W0 (evidence) | ⬜ pending |
| TBD | TBD | TBD | REL-04 | — | Emitted basename == the workflow literal | CI assertion | in-workflow string-equality step; observed in run A | ❌ W0 (CI-only) | ⬜ pending |
| TBD | TBD | TBD | REL-04 | — | Three-way filename equality (CMakeLists ↔ workflow literal ↔ `asset_candidates("py32f071")[0]`), **one non-vacuity assertion per parse** | unit (cross-repo) | `cd firestarter_app && python3 -m pytest tests/test_py32_asset_name_host.py -q -rs` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | REL-04 | T-sdk-substitution | Resolved SDK SHA == `GIT_TAG`, both 40-hex | CI assertion | in-workflow `git -C <fetchcontent-src> rev-parse HEAD` equality gate; observed in run A | ❌ W0 (CI-only) | ⬜ pending |
| TBD | TBD | TBD | BASE-08 | — | New checker satisfies the convention triple with raised floors | meta | `cd firestarter && python3 -m pytest tests/test_checker_convention.py -q` | ✅ exists — must stay green after the floor bump | ⬜ pending |
| TBD | TBD | TBD | D-09 | — | No new `ALLOWED_SKIP_REASONS` entry is needed | regression | `cd firestarter_app && python3 -m pytest tests/test_skip_census.py -q` | ✅ exists — **confirm by running**, do not read | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/scripts/check_release_assets.py` — covers REL-03
- [ ] `firestarter/tests/test_check_release_assets.py` — covers REL-03 + REL-02's `fail_on_unmatched_files` grep + the build-root seam precedence
- [ ] `firestarter/tests/fixtures/planted_release_assets_*/pio_build/…` — **non-dotted directory name** (F-6); at least a missing-hex plant and a zero-byte plant
- [ ] `firestarter/tests/fixtures/clean_release_assets_all_three/pio_build/…` — the control
- [ ] `firestarter/tests/test_checker_convention.py` — `FLOOR` 5→6, `FIXTURE_FLOOR` 10→actual
- [ ] `firestarter/.github/actions/build-py32f071/action.yml` — new; `shell:` required on every step
- [ ] `firestarter_app/tests/test_py32_asset_name_host.py` — the three-way binding, D-08(b)/D-09; copy the shape of `tests/test_py32_flash_map_host.py`
- [ ] Framework install: **none needed** — pytest already present in both repos

*No new shared fixture module is needed: the firmware side has no `conftest.py` by house rule and resolves paths self-containedly; the app side reuses `tests/fw_presence.py`.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rehearsal dispatch run A (healthy) | REL-01, REL-02, REL-04 | **Outward-facing** — D-04 makes `git push` / `gh workflow run` operator-gated; no task may run them. No ARM toolchain exists locally | Operator pushes the throwaway branch, dispatches `beta-build.yml` with `rehearsal: true`, records run URL + commit SHA, then `gh release view <rehearsal-tag> --json assets` |
| Rehearsal dispatch run B (planted CMake-configure break) | REL-03 | Same operator gate; the containment cascade is only observable on a real run | Operator commits the renamed-source break on the throwaway branch, dispatches again, records run URL + SHA, confirms three AVR assets still publish and the py32 asset is absent |
| `softprops/action-gh-release` creates no git tag for a draft | D-01 (load-bearing, unverified) | Asserted in discussion, not measured — must be confirmed **before** the first dispatch | Read the action's source/docs; if a tag *is* created, D-03's distinct `tag_name` is the fix |
| FetchContent SDK source path | D-10 (⚠ VERIFY) | Expected `build/py32f071/_deps/py32f071_sdk-src`, never observed — no local ARM toolchain | Read it off run A's log rather than hardcoding the guess |
| PY32F071 image runs / boots / installs | — | **No PCB exists. No fallback.** | **Not verifiable this milestone.** The permitted claim ceiling is exactly *the asset publishes* — `128-NONREGRESSION.md` (D-18) must carry that non-claim explicitly for Phase 130's CLOSE-02 ledger |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies (CI-only rows discharge via run URL + SHA)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s for the local loop
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
