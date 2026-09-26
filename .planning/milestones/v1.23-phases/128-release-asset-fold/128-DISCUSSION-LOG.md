# Phase 128: Release-Asset Fold - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-01
**Phase:** 128-Release-Asset Fold
**Areas discussed:** Release evidence route, Double ARM build + failure containment, Filename-contract binding (REL-04), AVR-assets assertion shape

All four offered gray areas were selected. No area was skipped.

---

## Release evidence route

### Q1 — How do we get real CI evidence for Criteria 2/3 without a third stray public beta?

| Option | Description | Selected |
|--------|-------------|----------|
| Draft-release rehearsal input | Permanent `rehearsal` dispatch input on `beta-build.yml` setting `draft: true`; operator dispatches from a throwaway branch. Draft ⇒ no tag created, so footprint is one Actions run + one deletable draft + one auto-commit on a deletable branch | ✓ |
| Temporary copy workflow | One-shot `beta-build-rehearsal.yml` deleted before close. Cost: proves a *copy* of the thing shipped | |
| Real dispatch, accept a stray beta | Truest evidence; cost is a third stray public prerelease and it pre-empts Phase 130's release decision | |
| Defer publication evidence to 130 | Structural verification only here. Cost: Criterion 2 undischarged; a wrong fold surfaces during the one release you least want to redo | |

**User's choice:** Draft-release rehearsal input (recommended).
**Notes:** Became D-01. The containment rests on draft releases creating no git tag — asserted during discussion, **not measured**, and flagged ⚠ VERIFY in CONTEXT.md.

### Q2 — How is the deliberately-broken ARM build planted, and how many dispatches?

| Option | Description | Selected |
|--------|-------------|----------|
| Break as a throwaway-branch commit, 2 runs | Run A healthy, run B after a commit breaking CMake configure (a renamed source path — the C-1 class from Phase 124). No break-me switch left in production | ✓ |
| Break via a dispatch input | One branch, both runs pure dispatches. Cost: a permanent sabotage switch on the production release workflow | |
| One run + local containment proof | Criterion 3 discharged by reading YAML + a local planted fixture. Cost: the containment is never observed | |

**User's choice:** Break as a throwaway-branch commit, 2 runs (recommended).
**Notes:** Became D-02. The cascade Configure→Build→glob-matches-nothing exercises every ARM step's containment in one run.

### Q3 — What does rehearsal mode leave behind, given `update_version.py` still computes a real-looking version?

| Option | Description | Selected |
|--------|-------------|----------|
| Permanent input + forced distinctive tag | `tag_name` overridden to `rehearsal-${{ github.run_id }}`; version bump still runs so REL-01 stays proven | ✓ |
| Permanent input, computed version | Simpler; a draft creates no tag. Cost: a draft in the release list looking exactly like the next real beta | |
| Remove the input at phase close | Workflow ends byte-clean. Cost: the next person has no way to rehearse and will test on `beta` | |

**User's choice:** Permanent input + forced distinctive tag (recommended).
**Notes:** Became D-03. Chosen to leave a reusable rehearsal mode rather than a one-off.

**Not asked (carried forward):** the operator-gate shape — no task runs `git push` or `gh workflow run`, plan is `autonomous: false`, structural separation is the gate rather than the checkpoint type. Unchanged from 124 D-08/D-09, 125 D-13, 127 D-01. Recorded as D-04. Verified during discussion that pushing a non-`beta`, non-`main` branch fires nothing in the firmware repo.

---

## Double ARM build + failure containment

### Q1 — After the fold a beta push builds ARM twice. 124 D-10 left this for Phase 128. How does it resolve?

| Option | Description | Selected |
|--------|-------------|----------|
| Keep both, distinct roles | `py32f071.yml` LOUD (hard-fails), `beta-build.yml`'s copy SOFT (`continue-on-error`). The pairing is what makes containment defensible | ✓ |
| Drop the push:beta trigger from py32f071.yml | Simplest CI graph. Cost: a broken ARM build on beta becomes fully silent | |
| Keep both, remove continue-on-error | Loud everywhere. Cost: contradicts REL-03 — a broken ARM build would block all three AVR assets | |

**User's choice:** Keep both, distinct roles (recommended).
**Notes:** Became D-05, discharging 124 D-10. `continue-on-error`'s removal trigger recorded as "validated on real silicon" — unreachable this milestone, so it stays.

### Q2 — Do we pay the "two places to keep the cmake invocation in sync" cost, or design it out?

| Option | Description | Selected |
|--------|-------------|----------|
| Composite action, used by both | `.github/actions/build-py32f071/action.yml`; runs *in* the calling job so REL-01 holds (a reusable `workflow_call` would not). Eliminates the drift class | ✓ |
| Duplicate + a parity checker | Matches the checker-with-fixture house style. Cost: detects drift instead of preventing it; a fifth checker | |
| Duplicate + cross-reference comments | Smallest diff. Cost: the `beta-build.yml` copy is `continue-on-error`, so drift there fails silently by construction | |

**User's choice:** Composite action, used by both (recommended).
**Notes:** Became D-06. Acknowledged as a new pattern — no `.github/actions/` exists in the repo today.

### Q3 — Is `py32f071.yml` going red a sufficient signal for a contained failure?

| Option | Description | Selected |
|--------|-------------|----------|
| Add an in-job outcome report | `if: always()` step reading the ARM step's `outcome`, emitting `::warning::` + a `$GITHUB_STEP_SUMMARY` line naming the missing asset | ✓ |
| The red py32f071.yml run is the signal | No extra step. Cost: the two runs correlate only by timestamp, and the release itself says nothing | |
| Also state it in the release body | Most visible. Cost: touches release-note content, outside REL-01…REL-04 | |

**User's choice:** Add an in-job outcome report (recommended).
**Notes:** Became D-07. Flagged ⚠ VERIFY that the condition must read `steps.<id>.outcome`, not `conclusion` — under `continue-on-error` the latter is `success` even on failure, which would make the report unable to fire.

---

## Filename-contract binding (REL-04)

### Q1 — Where does the binding to `asset_candidates("py32f071")[0]` actually live?

| Option | Description | Selected |
|--------|-------------|----------|
| Workflow literal + app-side cross-repo test | Workflow does the string-equality check Criterion 4 names; an app-repo test bound through `@requires_fw` does the real binding. Makes the phase dual-repo | ✓ |
| pip-install the host in the release job | Truest equality — the real function. Cost: PyPI network dependency in the firmware release job; installed version lags `beta` | |
| Firmware-only literal, binding deferred | No app commit. Cost: nothing mechanically connects the repos; the contract is a comment | |

**User's choice:** Workflow literal + app-side cross-repo test (recommended).
**Notes:** Became D-08. Accepted the dual-repo cost explicitly. `firestarter_app/tests/test_py32_flash_map_host.py` (from Phase 127) is the module shape to copy.

### Q2 — What does the app-side test parse on the firmware side?

| Option | Description | Selected |
|--------|-------------|----------|
| Three-way: CMake ↔ workflow ↔ asset_candidates | All three equal, with a separate non-vacuity assertion per parse. Catches drift in any of the three, in either direction | ✓ |
| CMake only | Simplest regex. Cost: the workflow literal is unbound and could rot to a stale name | |
| Workflow only | Binds the two things Criterion 4 names. Cost: a CMake rename is caught only when a release runs | |

**User's choice:** Three-way (recommended).
**Notes:** Became D-09. Non-vacuity is non-negotiable — A-7 is the measured in-milestone counter-example. Confirmed no new `ALLOWED_SKIP_REASONS` entry is needed (127 D-14 settled it).

### Q3 — Log the resolved SDK commit SHA, or also assert it against the pin?

| Option | Description | Selected |
|--------|-------------|----------|
| Log and assert against the pin | `rev-parse HEAD` echoed to the summary and asserted equal to CMake's `GIT_TAG`. Per-release proof the pin was honoured | ✓ |
| Log only | Exactly what REL-04 asks. Cost: a divergence written to a log nobody reads until already debugging | |
| Log, assert, and record in the release body | Traceability without opening Actions. Cost: release-note content, outside REL-01…REL-04 | |

**User's choice:** Log and assert against the pin (recommended).
**Notes:** Became D-10. Verified live that the SDK is already pinned to `0ed2f4b4d3391eccfd4491006a30295fd78e32c2`, so this proves the pin rather than creating it. The FetchContent source path is flagged ⚠ VERIFY — never observed in a real run.

---

## AVR-assets assertion shape

### Q1 — What shape is REL-03's "AVR assets present" assertion?

| Option | Description | Selected |
|--------|-------------|----------|
| `scripts/check_release_assets.py` + planted fixture | The repo's established checker shape; BASE-08's `test_checker_convention.py` requires the pairing anyway. Provable locally, exit code | ✓ |
| Inline shell in the YAML | Smallest diff. Cost: unprovable outside a dispatch, and "demonstrably fails" is the requirement's wording | |
| Checker also owns filename + count | One script for everything. Cost: bundles a must-hard-fail gate with a must-tolerate-absence one, forcing internal severity logic | |

**User's choice:** `scripts/check_release_assets.py` + planted fixture (recommended).
**Notes:** Became D-11. The BASE-08 pairing obligation was verified in `tests/test_checker_convention.py` before the question was asked.

### Q2 — Where does the checker get the required AVR asset list?

| Option | Description | Selected |
|--------|-------------|----------|
| Derive from `size_baseline.json`'s `avr_targets` | Same recorded-baseline file every other v1.23 gate cites; exact-set assertion plus non-vacuity on an empty key set | ✓ |
| Hardcode three names with a citing comment | Dead simple. Cost: a literal that rots, in a milestone whose premise is files moving | |
| Derive from `platformio.ini` env sections | Closest to what `pio run` builds. Cost: the AVR/native filter is already non-trivial (four native envs after Phase 124) | |

**User's choice:** Derive from `size_baseline.json` (recommended).
**Notes:** Became D-12. Verified live: `avr_targets` is keyed exactly `uno`/`uno328pb`/`leonardo`, matching what release `3.0.0b13` actually published.

### Q3 — Is `build.yml` (stable/`main`) in scope?

| Option | Description | Selected |
|--------|-------------|----------|
| Out of scope, recorded why | REL-01 names `beta-build.yml`; `py32f071` is in `BETA_ONLY_BOARDS`, so a stable release would advertise an image the stable CLI exits 2 on. Graduation trigger recorded | ✓ |
| Also add the AVR-assets check to build.yml | Defensible on merit. Cost: nothing in REL-01…REL-04 asks for it | |
| Fold ARM into build.yml too | Cost: contradicts the channel gating Phase 127 just hardened both ways | |

**User's choice:** Out of scope, recorded why (recommended).
**Notes:** Became D-13. The rejected middle option was preserved as a deferred idea rather than dropped.

---

## Claude's Discretion

Accepted as stated defaults at the close of discussion, without individual questions:

- **D-14** — `ad47c3b` re-applied by hand, not cherry-picked (its `py32f071.yml` rewrite predates 124's `push: branches: [beta]` and is superseded by D-06's composite action). Only the CMakeLists underscore rename and the README section carry over intact; `ad47c3b` cited in the commit message.
- **D-15** — correct R-16's literal-vs-glob slip in `platform/py32f071/README.md` while in the file.
- **D-16** — `py32f071.yml` keeps its single-file artifact upload (a PR build must stay downloadable for future board bring-up).
- **D-17** — composite action leaves the apt toolchain unpinned, matching today.
- **D-18** — evidence artifact is `128-NONREGRESSION.md`, matching Phases 124–127.
- **D-19** — firmware commits first, then the single app commit (the app test parses firmware files).

## Deferred Ideas

- Fold the ARM build into `build.yml` — graduation trigger: when `py32f071` leaves `BETA_ONLY_BOARDS`.
- Run `check_release_assets.py` in `build.yml` too — unscheduled; defensible but outside REL-01…REL-04.
- Pin the apt toolchain versions in the composite action — unscheduled.
- Record the SDK SHA / py32 asset status in the release body — Phase 130 or later; rejected twice as release-facing prose this phase does not own.
- The self-flash bootloader over CDC + COBS remains the intended primary install route; publishing a DFU-installable asset does not retire it (Phase 129 must say so).
