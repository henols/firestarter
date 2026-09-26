---
phase: 128-release-asset-fold
verified: 2026-08-01T23:40:00Z
status: passed
score: 4/4 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 128: Release-Asset Fold Verification Report

**Phase Goal:** `firestarter_py32f071.hex` publishes as a real GitHub release asset carrying
the correct release `VERSION`, and a broken ARM build can never block the three AVR assets
from publishing.
**Verified:** 2026-08-01T23:40:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Method note

This phase's evidence is unusual: its central claims can only be observed on a real GitHub
Actions dispatch (no ARM toolchain exists in this devcontainer), and `128-NONREGRESSION.md`
records two such dispatches (rehearsal runs A and B) plus their now-deleted draft releases.
Rather than trusting that transcript, this verification independently re-queried the GitHub
API (`gh run view`, `gh api .../check-runs/.../annotations`, `gh release list`) against the
same run IDs and repo, and independently re-ran every locally-runnable test suite named in
the transcript. Every value below marked "independently reconfirmed" was obtained by a fresh
tool call in this session, not copied from `128-NONREGRESSION.md`.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | REL-01: ARM build steps sit strictly after `update_version.py` + the auto-commit step, same job, so the image carries the release `VERSION` | ✓ VERIFIED | `beta-build.yml` read directly: `version` (step 12) → `git-auto-commit-action@v5` (13) → `Build PY32F071 firmware` (`id: arm`, 15) → `Release` (22). Independently re-queried run `30722352902` via `gh run view --json jobs`: steps in that exact order, all `success`; step 19 "Assert the py32 image carries the bumped VERSION (REL-01)" ran and was `success` (the actual PASS text, `PASS: image contains version string 3.0.0b99:py32f071`, is cited in `128-NONREGRESSION.md` §3.5 — logs are not re-fetchable after run retention/redaction, but the step's `success` conclusion and its position after steps 13/15 were independently confirmed). |
| 2 | REL-02: `firestarter_py32f071.hex` published as a GitHub release asset (not an Actions artifact), matched by a glob, verified via a real CI run URL + SHA | ✓ VERIFIED | `Release` step `files:` block read directly: two glob entries, `.pio/build/**/firestarter_*.hex` and `build/py32f071/firestarter_*.hex`. Run `30722352902` independently reconfirmed via `gh run view`: `conclusion: success`, `headSha: 7a0a375...` matching the firmware HEAD. `128-NONREGRESSION.md` §3.2 cites the asset list (4 assets incl. `firestarter_py32f071.hex`, 77284 B) from that run's now-deleted draft release — not independently re-inspectable (draft deleted by design, D-01/D-03), but the run's existence, conclusion, and head SHA are independently confirmed, and the draft-deletion is itself independently confirmed (see Anti-Overclaim Checks below: 0 draft releases, 0 rehearsal tags today). |
| 3 | REL-03: a deliberately-broken ARM build still publishes all three AVR assets, via an assertion step proven to demonstrably fail if any AVR asset is missing | ✓ VERIFIED (two-part, stated honestly) | **Half A (CI, "still publishes under a broken build"):** run `30722537152` independently re-queried via `gh run view --json jobs`: step 15 (ARM build) `success` at the job-step level (expected under `continue-on-error`), steps 17-19 (REL-01/REL-04 assertions, `if: outcome==success`) `skipped`, step 16 (missing-image report) `success` (ran, unlike run A where it was `skipped`), step 21 (AVR-assets assertion, unconditional) `success`, step 22 (Release) `success`. Independently pulled the check-run annotations for this run: `warning: "PY32F071 image not produced — this release carries no py32f071 asset."` and `failure: "Process completed with exit code 1."` — both present, confirming the ARM leg genuinely failed and was contained. **Half B (local, "assertion demonstrably fails on missing asset"):** re-ran `scripts/check_release_assets.py` against both planted fixtures in this session — `planted_release_assets_missing_uno328pb` → exit 1, names `uno328pb`; `planted_release_assets_zero_byte_leonardo` → exit 1, names `leonardo` and `0 bytes`. Re-ran the full paired pytest module, `tests/test_check_release_assets.py`: 10/10 passed. **Honestly scoped, per the phase's own documentation:** Half B was never exercised inside a real CI run this phase (the planted CI break was scoped to the ARM-only `timing.cpp`, not an AVR asset) — this is stated explicitly in `128-NONREGRESSION.md` §7 Criterion 3 and is not treated here as a newly-found gap. |
| 4 | REL-04: CI logs the resolved SDK commit SHA and asserts the emitted filename matches `asset_candidates("py32f071")[0]` via a mechanical check | ✓ VERIFIED | `CMakeLists.txt`'s `HEX_FILE` resolves to `firestarter_py32f071.hex`; `beta-build.yml` steps 17-18 assert this and the SDK SHA mechanically (`grep`-read directly, matching the transcript). Run `30722352902` independently reconfirmed: steps 17 and 18 both `success`. Host-side cross-repo binding test independently re-run in this session: `python3 -m pytest tests/test_py32_asset_name_host.py -v -rs` → **10 passed, 0 skipped**, no `firestarter firmware checkout absent` skip line — confirms the three-way equality (CMake-emitted name, workflow transcription, `asset_candidates("py32f071")[0]`) holds on the live tree, independent of the CI dispatch. **Honestly scoped:** this binding is local-only — `firestarter_app`'s `ci.yml` and `beta-release.yml` were independently grepped for `checkout` usage and confirmed as plain single-repo `actions/checkout@v4` steps with no `repository:`/`path:` args, so all six `@requires_fw` legs SKIP in app CI. `REQUIREMENTS.md` and `128-NONREGRESSION.md` state this ceiling explicitly rather than claiming CI enforcement. |

**Score:** 4/4 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/.github/actions/build-py32f071/action.yml` | Composite action: toolchain + configure + build, emits `hex_path`/`sdk_sha`, no `continue-on-error` anywhere | ✓ VERIFIED | Read directly. `grep -n "continue-on-error"` matches only the explanatory comment prose (not a YAML key) — independently confirmed no directive exists in the file. `outputs.hex_path`/`outputs.sdk_sha` wired to `steps.build.outputs.*`. |
| `firestarter/.github/workflows/beta-build.yml` | ARM call after auto-commit, `continue-on-error: true` at call site only, `rehearsal` input, D-07 report step keyed on `outcome`, REL-01/REL-04 assertion steps, unconditional AVR-assets step, two-entry `files:`, `draft`/`tag_name` wired to rehearsal | ✓ VERIFIED | Read directly, matches all named properties. Step ordering and conditions independently reconfirmed against two live CI runs. |
| `firestarter/.github/workflows/py32f071.yml` | LOUD gate, calls composite action with no `continue-on-error` | ✓ VERIFIED | Read directly. |
| `firestarter/platform/py32f071/CMakeLists.txt` | Underscore-named `TARGET_NAME`/`BIN_FILE`/`HEX_FILE`, `GIT_TAG` pin | ✓ VERIFIED | Read directly: `firestarter_py32f071.hex`/`.elf`/`.bin`; `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2` (40-hex). |
| `firestarter/scripts/check_release_assets.py` | D-11/D-12 checker, derives required set from `size_baseline.json`'s `avr_targets` | ✓ VERIFIED | Read directly; independently re-executed against clean and both planted fixtures with expected exit codes. |
| `firestarter/tests/test_check_release_assets.py` + fixtures | BASE-08 anti-hollow triple | ✓ VERIFIED | Independently re-ran: 10/10 passed. Fixture diffs independently confirmed to match the documented single-edit derivation (uno328pb hex removed; leonardo hex truncated to 0 bytes). |
| `firestarter/platform/py32f071/README.md` §"Release integration" | D-15 corrected glob-not-literal + trigger prose | ✓ VERIFIED | Read directly; glob (`build/py32f071/firestarter_*.hex`), not the literal R-16 flagged. |
| `firestarter_app/tests/test_py32_asset_name_host.py` | D-08(b)/D-09 three-way cross-repo binding, `@requires_fw` | ✓ VERIFIED | Independently re-ran: 10 passed, 0 skipped. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `beta-build.yml`'s ARM call site | `.github/actions/build-py32f071/action.yml` | `uses: ./.github/actions/build-py32f071`, `continue-on-error: true` at call site | ✓ WIRED | Confirmed by direct read; run A/B CI evidence confirms the containment fires as designed. |
| `beta-build.yml`'s REL-01/REL-04 assertion steps | `steps.arm.outputs.{hex_path,sdk_sha}` | `if: steps.arm.outcome == 'success'`, env vars reading the composite's outputs | ✓ WIRED | Confirmed by direct read and by run A (steps 17-19 success) / run B (steps 17-19 skipped, correctly gated) evidence. |
| `beta-build.yml`'s Release step | `check_release_assets.py`'s exit code | Unconditional prior step (no `if:`) | ✓ WIRED | Confirmed by direct read; run B independently confirms this step ran (`success`) and preceded a successful `Release` despite the contained ARM failure. |
| `firestarter_app/tests/test_py32_asset_name_host.py` | `firestarter/platform/py32f071/CMakeLists.txt` + `beta-build.yml` | `fw_path()` from `tests/fw_presence.py` | ✓ WIRED | Independently re-run, 10/10 passed against the live sibling checkout. |

### Behavioral Spot-Checks / Probe Execution

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Firmware pytest suite unaffected by this phase's non-firmware-compiled work | `python3 -m pytest tests/ -q` (firestarter) | 180 passed | ✓ PASS (independently re-run) |
| Native Unity suite unaffected | `pio test -e native` | 141/141 succeeded, 9 suites shown (17 total per baseline) | ✓ PASS (independently re-run) |
| Release-assets checker + BASE-08 convention gate | `pytest tests/test_check_release_assets.py tests/test_checker_convention.py -q` | 10 + 7 passed | ✓ PASS (independently re-run) |
| Host app full suite unaffected | `pytest tests/ -q` + `--collect-only -q` cross-check (firestarter_app) | exit 0, zero `F`/`E` progress chars, 30 snapshots passed; collect-only per-file sum == 1303 | ✓ PASS (independently re-run and summed) |
| Host cross-repo binding, pass-not-skip | `pytest tests/test_py32_asset_name_host.py -v -rs` | 10 passed, 0 skipped | ✓ PASS (independently re-run) |
| Real CI run A (healthy rehearsal) | `gh run view 30722352902 --json jobs/conclusion/headSha` | conclusion=success, headSha=7a0a375..., step order matches | ✓ PASS (independently re-queried) |
| Real CI run B (planted ARM break, contained) | `gh run view 30722537152 --json jobs`; `gh api .../check-runs/<id>/annotations` | conclusion=success (job-level), ARM step contained, D-07 warning + failure annotations present, exactly the documented step-skip pattern | ✓ PASS (independently re-queried) |
| Post-cleanup state | `gh release list`; `gh api .../releases -q 'select(.draft==true)'`; `gh api .../git/refs/tags` grepped for rehearsal/b99 | newest real release = `3.0.0b14`; 0 draft releases; 0 rehearsal/b99 tag refs | ✓ PASS (independently re-queried) |
| `size_baseline.json` avr_targets vs. a real published release | `gh release view 3.0.0b13 --json assets` | exactly `firestarter_{leonardo,uno,uno328pb}.hex`, matching `avr_targets` keys `uno`/`uno328pb`/`leonardo` | ✓ PASS (independently re-queried) |

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REL-01 | 128-02, 128-05, 128-06, 128-10 | ARM ordered after version-bump auto-commit, same job | ✓ SATISFIED | Truth 1 above |
| REL-02 | 128-01, 128-04, 128-07, 128-08, 128-10 | `firestarter_py32f071.hex` published as a real release asset, glob-matched | ✓ SATISFIED | Truth 2 above |
| REL-03 | 128-01, 128-04, 128-05, 128-07, 128-08, 128-10 | Broken ARM build still publishes all three AVR assets, proven | ✓ SATISFIED (Half B local-only, honestly stated) | Truth 3 above |
| REL-04 | 128-02, 128-03, 128-04, 128-06, 128-09, 128-10 | Emitted filename == host contract; SDK SHA logged and asserted | ✓ SATISFIED (cross-repo binding local-only, honestly stated) | Truth 4 above |

No orphaned requirements: `REQUIREMENTS.md`'s traceability table maps REL-01…REL-04 exclusively to Phase 128 with 0 unmapped requirements project-wide (47/47 mapped).

### Anti-Patterns Found

None. All nine files touched by this phase's firmware-side commits (`.github/actions/build-py32f071/action.yml`, `beta-build.yml`, `py32f071.yml`, `platform/py32f071/CMakeLists.txt`, `platform/py32f071/README.md`, `tests/fixtures/README.md`, `scripts/check_release_assets.py`, `tests/test_check_release_assets.py`, `tests/test_checker_convention.py`) and the one app-side file (`tests/test_py32_asset_name_host.py`) were grepped for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` — zero matches in every file.

### Anti-Overclaim Checks (adversarial hunt, per this task's brief)

Beyond the four documented, already-honest known limits (REL-03 Half B local-only, F-8 cross-repo binding local-only, the Run-B procedure substitution, the pre-dispatch fix of a premature "confirmed by observation" claim), this verification actively searched for any *additional* unresolved overclaim:

- Grepped all ten `*-SUMMARY.md` files for "confirmed by observation", "guarantee", "proven on hardware", "runs on"/"boots"/"installs on" — every hit found is either a correctly-hedged non-claim ("nothing here claims the image runs, boots, or installs") or documentation of the one premature claim that was already caught and fixed pre-dispatch (128-05, fixed in commit `7a0a375`, independently confirmed via `git show`).
- Independently confirmed the fix commit `7a0a375` is real, is the firmware HEAD, and the working tree is clean (`git status --porcelain` empty).
- Independently confirmed `firestarter-py32f071` (the pre-rename hyphenated form) has zero remaining occurrences repo-wide (`grep -rn` over `.yml/.txt/.md/.cmake`, exit code 1 = no matches).
- Independently confirmed the app repo's pre-existing dirty files (`.gitignore`, `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) are unrelated to this phase and match the NONREGRESSION transcript's own disclosure exactly.
- No new overclaim found.

### Human Verification Required

None. Every truth is either directly readable from committed source or was independently re-confirmed against real, live evidence (re-run test suites; re-queried GitHub Actions API for both rehearsal runs' step conclusions and annotations; re-queried the release list, draft-release count, and tag refs). The two known local-only ceilings (REL-03 Half B, REL-04's cross-repo binding) are accurately documented as permanent, structural scope limits — not claims requiring a human to adjudicate a disputed fact — and are not new findings.

### Gaps Summary

None. All four requirements (REL-01…REL-04) are satisfied by evidence this verification
independently reproduced or independently re-queried, not merely by trusting
`128-NONREGRESSION.md`'s transcript. The two honestly-scoped local-only ceilings were present
in the planning record before this verification began and are correctly stated there; they do
not block the phase goal as written (the roadmap's Criterion 3 already anticipates exactly
this split, and Criterion 4 asks only for the mechanical CI assertions plus a filename
contract that is proven to hold on the live tree).

---

_Verified: 2026-08-01T23:40:00Z_
_Verifier: Claude (gsd-verifier)_
