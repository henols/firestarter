---
phase: 128-release-asset-fold
plan: 09
subsystem: infra
tags: [cross-repo-test, pytest, py32f071, release-assets, host-firmware-binding]

# Dependency graph
requires:
  - phase: 128-release-asset-fold (128-08, prior wave)
    provides: "clean firmware working tree at HEAD 0de57da3c9edfb40f86eee8b0964e0f1bcdd8559, the D-19/F-16 precondition this plan's planted-mutation test asserts before trusting its own parse"
  - phase: 127-host-dfu-installer
    provides: "the test_py32_flash_map_host.py structural analog (@requires_fw + fw_path + non-vacuity pattern) this module copies, and the frozen asset_candidates() contract"
provides:
  - "firestarter_app/tests/test_py32_asset_name_host.py -- the actual cross-repo binding for REL-04: a three-way equality between the name CMake emits, the name the firmware workflow transcribes, and asset_candidates('py32f071')[0], with a separate non-vacuity guard per parse"
  - "The phase's second and final commit (D-19) in the host repo"
affects: [128-10]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cross-repo binding test placed in the @requires_fw parity class rather than the no-marker RED class, when the test reads and hashes a real sibling-repo file (deviation from the 127 analog, documented below)"

key-files:
  created:
    - firestarter_app/tests/test_py32_asset_name_host.py
  modified: []

key-decisions:
  - "test_planted_mutated_cmake_name_is_detected carries @requires_fw, unlike its 127 analog (test_planted_mutated_config_origin_is_detected), which carries no marker -- stated deviation, see Deviations section"
  - "Did not mark REL-04 complete in REQUIREMENTS.md -- this plan closes only the cross-repo binding slice; Plan 128-06's in-workflow assertions and Plan 128-10's rehearsal-run evidence are the other two halves"
  - "No new ALLOWED_SKIP_REASONS entry added to tests/test_skip_census.py -- FW_ABSENT_REASON already covers this module's only skip marker (D-09, confirmed by running test_skip_census.py, not by reading it)"

patterns-established: []

requirements-completed: []  # REL-04 is a multi-plan requirement (128-06 + this plan + 128-10).
                            # This plan closes the cross-repo binding slice only, per its explicit
                            # scope boundary; Plan 128-10 is the sole owner of requirement closure.

coverage:
  - id: D1
    description: "Three-way equality: CMake-emitted HEX_FILE basename == beta-build.yml's REL-04 transcription == asset_candidates('py32f071')[0], each parse independently non-vacuity-guarded"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "pytest tests/test_py32_asset_name_host.py -q -rs -- 10 passed, 0 skipped, observed via -v (dot count matches collected count, no s/F/E markers)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Workflow parser refuses to guess between two distinct candidates; both parsers and the shape guard fail closed on empty/malformed input"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "TestPy32AssetNameFailsClosedOnBadInput (4 unmarked tests, all pass locally and are the only legs that run in app CI per F-8)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The planted-mutation test proves the parity check can actually fail, and never touches the read-only firmware sibling (blob SHA + porcelain status unchanged)"
    requirement: "REL-04"
    verification:
      - kind: unit
        ref: "test_planted_mutated_cmake_name_is_detected -- asserted _git_hash_object(real_path) unchanged and _git_porcelain(FW_ROOT) == '' after the test"
        status: pass
    human_judgment: false
  - id: D4
    description: "No new ALLOWED_SKIP_REASONS entry required; skip census confirmed green by running it"
    verification:
      - kind: unit
        ref: "python3 -m pytest tests/test_skip_census.py -q -v -- 5 passed"
        status: pass
    human_judgment: false
  - id: D5
    description: "Whether the cross-repo binding is enforced by app CI (it is not, per F-8) is a claim discipline item, not something this plan can fix"
    verification: []
    human_judgment: true
    rationale: "Neither firestarter_app CI workflow (ci.yml, beta-release.yml) checks out the firmware sibling -- verified by grep, both actions/checkout@v4 steps are plain single-repo checkouts with no repository:/path:. This is a pre-existing, accepted property (127 D-14 landed the same shape); this plan states the ceiling honestly rather than fixing something outside its scope."

# Metrics
duration: ~35min
completed: 2026-08-01
status: complete
---

# Phase 128 Plan 09: Cross-Repo Asset-Filename Binding (D-08(b) / D-09) Summary

**Added `firestarter_app/tests/test_py32_asset_name_host.py`, the app-repo half of Phase 128's dual-repo REL-04 binding: a three-way equality proving the name CMake emits, the literal the firmware workflow transcribes, and `asset_candidates("py32f071")[0]` are the same string, with a per-parse non-vacuity guard and fail-closed RED demonstrations -- the phase's second and final commit (D-19).**

## Performance

- **Duration:** ~35 min
- **Completed:** 2026-08-01
- **Tasks:** 3/3
- **Files modified:** 1 (`firestarter_app/tests/test_py32_asset_name_host.py`, new)

## Accomplishments

- **Task 1 -- Module scaffold.** Created the module with its seam imports (`asset_candidates` from `firestarter.firmware`, `FW_ROOT`/`fw_path`/`requires_fw` from `tests.fw_presence`), two module-scope path constants resolved through `fw_path()` (`_CMAKELISTS`, `_BETA_BUILD`), two guarded parsers (`_parse_emitted_hex_name`, `_parse_workflow_literal`), the shared non-vacuity guard (`_assert_non_vacuous_name`, whose message contains the load-bearing phrase `vacuously true`), and the fail-closed git helpers (`_git_hash_object`, `_git_porcelain`). Ran the plan's automated verify script by hand: both parsers returned `firestarter_py32f071.hex` against the real shipped files, the guard fired correctly on an empty synthetic value, and `_git_porcelain(FW_ROOT)` confirmed the D-19/F-16 precondition held.
- **Task 2 -- Parity class + RED demonstrations.** Added `TestPy32AssetNameParity` (6 methods, all `@requires_fw`: non-vacuity per parse (2), CMake-vs-workflow, workflow-vs-host, the explicit three-way, and the planted-mutation RED) and `TestPy32AssetNameFailsClosedOnBadInput` (4 unmarked methods: empty-input non-vacuity per parser, the two-distinct-candidates refusal, and the shape-guard whitespace/uppercase rejection). Observed locally: 10 passed, 0 skipped -- confirmed both via `-rs` (no `firestarter firmware checkout absent` skip line) and by counting progress-line dots against pytest's own `--collect-only` count (this environment's pytest 9.1.1 intermittently omits the trailing `"N passed"` summary line under `-q`, a quirk `tests/test_skip_census.py`'s own docstring already documents -- `-v` reliably shows the summary and confirmed `10 passed` directly).
- **Task 3 -- Full verification and the phase's second and final commit.** Ran, in order: (1) firmware tree porcelain check -- empty, HEAD `0de57da3c9edfb40f86eee8b0964e0f1bcdd8559`, matching Plan 128-08's recorded value; (2) the new module alone -- 10 passed, 0 skipped; (3) `tests/test_skip_census.py` -- 5 passed, confirming by running (not reading) that no new `ALLOWED_SKIP_REASONS` entry is needed; (4) the full host suite `tests/ -q` -- 1303 passed (dot count cross-checked against `--collect-only`'s per-file sum, also 1303; zero `s`/`F`/`E` characters found in any progress line), plus 30 snapshot assertions passed; (5) `ruff check` and `ruff format --check` scoped to the new file -- both clean; `tools/check_mypy_watermark.py` -- 1 pre-existing error (an unrelated numpy-stub syntax issue caused by this devcontainer's Python 3.12 vs the pinned 3.9 target, a known environment mismatch per project memory), 34 below the watermark of 35, and confirmed the new file contributes zero errors to that count. Committed inside `firestarter_app` on `v1.23-py32f071-integration`: commit `cc9452f`, touching exactly one file, citing D-19's ordering and the firmware HEAD SHA in the message.

## Task Commits

All three tasks land in a single commit, per the plan's own instruction (D-19: "the phase's second and final commit") -- Tasks 1 and 2 built the module incrementally with hand-run verification at each step; no commit was made until Task 3's full verification passed, matching the pattern Plan 128-08 already established (its own Task 2 was verification-only with no commit).

1. **Tasks 1-3 combined: add `tests/test_py32_asset_name_host.py`** - `cc9452f` (test) in `firestarter_app`

**Plan metadata:** committed in the meta-repo (`.planning/phases/128-release-asset-fold/128-09-SUMMARY.md`, `STATE.md`, `ROADMAP.md`).

## Files Created/Modified

- `firestarter_app/tests/test_py32_asset_name_host.py` -- new, 374 lines. Structurally the exact sibling of `tests/test_py32_flash_map_host.py` (127's cross-repo flash-map gate): module docstring with Requirements/Decisions-covered/Coverage/F-8-ceiling blocks, two guarded parsers, one shared non-vacuity guard, fail-closed git helpers, a `@requires_fw`-marked parity class (6 methods) and an unmarked RED class (4 methods).

## Verification Results (observed, not predicted)

| Check | Command | Result |
|---|---|---|
| Firmware tree clean | `git -C /workspaces/firestarter status --porcelain` | empty |
| Firmware HEAD | `git -C /workspaces/firestarter rev-parse HEAD` | `0de57da3c9edfb40f86eee8b0964e0f1bcdd8559` -- matches 128-08-SUMMARY.md |
| New module alone | `pytest tests/test_py32_asset_name_host.py -v -rs` | **10 passed, 0 skipped** (0.31s) |
| `@requires_fw` decorator count | `grep -c '^\s*@requires_fw\s*$'` | 6 (matches the 6 parity-class methods exactly) |
| Skip census | `pytest tests/test_skip_census.py -q -v` | **5 passed** (75.97s) -- no new `ALLOWED_SKIP_REASONS` entry required |
| Full host suite | `pytest tests/ -q` | **1303 passed** (dot count cross-checked against `--collect-only`'s 1303; zero non-dot progress characters), plus 30 snapshots passed |
| `ruff check` (scoped) | `ruff check tests/test_py32_asset_name_host.py` | clean |
| `ruff format --check` (scoped) | `ruff format --check tests/test_py32_asset_name_host.py` | already formatted |
| mypy watermark (scoped) | `python3 tools/check_mypy_watermark.py` | 1 pre-existing error (unrelated numpy-stub syntax issue, py3.12-vs-py3.9 devcontainer mismatch), 34 below watermark; new file contributes 0 |
| Firmware tree after run+commit | `git -C /workspaces/firestarter status --porcelain` | still empty, HEAD unchanged |

## Decisions Made

- Followed the plan's exact Task 1/2/3 structure: scaffold with hand-run verification first (no test functions), then the two test classes, then full verification and the single commit -- mirroring Plan 128-08's precedent of doing real verification work across tasks before committing once.
- **Deliberate, stated deviation from the 127 analog (flagged per plan instruction):** `test_planted_mutated_cmake_name_is_detected` carries `@requires_fw`, whereas its structural analog in `test_py32_flash_map_host.py` (`test_planted_mutated_config_origin_is_detected`) carries no marker at all, sitting in the no-marker RED class. This test reads the real firmware `CMakeLists.txt` and hashes it inside `FW_ROOT` before any monkeypatch runs, so without the sibling repo it would be a hard `AttributeError`/`FileNotFoundError`-class failure, not an honest skip -- and F-8 already records that the sibling is always absent in app CI. Marking it `@requires_fw` is the accurate classification and adds no new skip reason, since `FW_ABSENT_REASON` is already the sole allow-listed reason. **Surfaced as a finding for Phase 130 to note, not fixed here:** the 127 module's equivalent test, lacking any marker, would presumably error (not skip) under the same no-sibling condition in app CI -- worth a look when Phase 130 audits cross-repo test behavior, but out of this plan's scope (its own file is frozen except for this one).
- Did not mark REL-04 complete in `REQUIREMENTS.md`, per the plan's explicit scope boundary. It is a three-plan requirement: 128-06 (in-workflow assertions), this plan (the cross-repo binding), and 128-10 (rehearsal-run observed evidence).
- No `tests/test_skip_census.py` edit -- confirmed by running it (D-09's explicit instruction), not by reading it. `git diff --name-only` for this commit lists exactly one file.

## Deviations from Plan

**1. [Documented, plan-anticipated] `test_planted_mutated_cmake_name_is_detected` placed in the `@requires_fw` class.** See "Decisions Made" above -- this is the plan's own Task 2 instruction ("Deliberate, stated deviation from the 127 analog"), not an unplanned auto-fix. No Rule 1-4 applies; it is prescribed behavior.

No other deviations. Both parsers, the shared guard, and the git helpers matched the plan's `<action>` and `<verify>` blocks on first implementation; no auto-fixes were needed.

## Issues Encountered

- **Environment quirk (not a defect):** `pytest -q` in this devcontainer (pytest 9.1.1) intermittently omits the trailing `"N passed in Xs"` summary line from captured stdout, exactly as `tests/test_skip_census.py`'s own docstring already documents. Worked around by using `-v` (which reliably shows the summary) and by cross-checking progress-line dot counts against `--collect-only`'s per-file sum. Not a code issue; recorded here so a future reader is not confused by a `-q` run that appears to hang without a final count.
- **mypy 1 pre-existing error, unrelated to this plan's file:** running raw `mypy` directly (not through the watermark tool) surfaces a numpy-stub `Type statement is only supported in Python 3.12 and greater` syntax error, because this devcontainer runs Python 3.12 while `pyproject.toml` pins `python_version = "3.9"` for mypy's own analysis -- a known environment mismatch (see project memory: "Devcontainer py3.12 masks app CI"). `tools/check_mypy_watermark.py` is the correct scoped gate and it passes (1 error, 34 below the watermark of 35); grepping the tool's verbose output for the new file's name returns nothing, confirming this module contributes zero errors.

## Claim discipline (F-8 ceiling, stated verbatim per the plan's instruction)

**The cross-repo binding this module proves is enforced by a local run and by developer discipline, not by app CI.** Neither `firestarter_app` CI workflow (`ci.yml`, `beta-release.yml`) checks out the firmware sibling repository -- both `actions/checkout@v4` steps in both files are plain single-repo checkouts with no `repository:`/`path:` arguments, verified live by grep. With no `../firestarter/.git` marker present in that environment, `tests/fw_presence.py`'s `FW_REPO_PRESENT` is `False` at import, and all six `@requires_fw` legs of this module SKIP there -- only the four unmarked RED demonstrations (`TestPy32AssetNameFailsClosedOnBadInput`) actually run in app CI. This is a pre-existing, accepted property (Phase 127 D-14 landed the same shape). **Claiming CI enforcement would be false.** `.planning/phases/128-release-asset-fold/128-NONREGRESSION.md` (Plan 128-10) must repeat this ceiling. Nothing in this module says anything about whether the published image runs, boots, or installs -- it compares filenames only. No PY32F071 PCB exists.

## User Setup Required

None. No external service configuration required. No CI dispatch occurred in this plan (D-04 structurally excludes it; that is Plan 128-10's scope).

## Known Stubs

None. Every parser, guard, and helper in this module operates against real files (either the live shipped firmware files or fixtures constructed under `tmp_path` for the RED tests) -- no placeholder data, no hardcoded pass-through.

## Threat Flags

None new. This plan's own `<threat_model>` (T-128-12, T-128-17, T-128-23, T-128-24, T-128-25) are all mitigated exactly as designed: the three-way equality with per-parse non-vacuity guards (T-128-12, T-128-17); the local run observed PASS-not-SKIP via dot-count cross-check against `--collect-only` rather than trusting a possibly-truncated summary line, with the F-8 ceiling stated in both this SUMMARY and (pending) `128-NONREGRESSION.md` (T-128-23); the planted mutation written under `tmp_path` and reached only via `monkeypatch.setattr` on this module's own constant, with the real file's blob SHA and the firmware tree's porcelain status asserted unchanged (T-128-24); and every firmware path resolved through `fw_path()`, with `@requires_fw` as the only skip marker and no `.exists()` proxy or module-local `skipif` anywhere in the file (T-128-25, confirmed by grep during authoring).

## Firmware-tree status (D-19 / F-16 precondition, both before and after)

- **Before:** `git -C /workspaces/firestarter status --porcelain` -- empty. HEAD `0de57da3c9edfb40f86eee8b0964e0f1bcdd8559` (matches Plan 128-08's recorded value).
- **After this plan's test run and commit:** still empty, HEAD unchanged. `/workspaces/firestarter` was read-only for this plan and remains untouched.

## Next Phase Readiness

- Plan 128-10 (Wave 7, the phase's closing plan) can now write `128-NONREGRESSION.md` and own REL-01 through REL-04's requirement closure, citing this plan's local-only F-8 ceiling verbatim, the firmware HEAD `0de57da`, and this commit `cc9452f` as the host repo's contribution.
- The dual-repo commit sequence D-19 required is now complete: firmware commits 128-01 through 128-08 landed first; this is the single, final app-repo commit.
- No blockers.

---
*Phase: 128-release-asset-fold*
*Completed: 2026-08-01*
