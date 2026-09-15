---
phase: 190-endpoints-that-do-not-depend-on-a-redirect
plan: 04
subsystem: firmware-release-management
tags: [requests, github-releases-api, click, ci, evidence-fixture]

requires:
  - phase: 190-01
    provides: "The three FIRESTARTER_*_URL constants addressing henols/firestarter_fw, and fw --list's failure-versus-empty split"
  - phase: 190-02
    provides: "The URL-03 pin (test_endpoint_constants.py) and the app repository's own slug-clean baseline"
  - phase: 190-03
    provides: "manage_firmware_update's dead-endpoint guard and _endpoint_for_channel, exercised live by this plan's check 4a"
provides:
  - "endpoint-contract-fixture.sh: a committed, re-runnable live demonstration of all four D-14 checks against henols/firestarter_fw, asserting redirects: 0 on both API endpoints (the one observable that distinguishes this from the pre-change transparent 301)"
  - "evidence/190-url-04-endpoint-contract.txt: the captured run -- both channels resolved, a real .hex downloaded and format-checked as Intel HEX, both URL-04 failure modes shown exiting 1 with distinct named messages"
  - "evidence/190-url-01-ci-equivalent.txt: the five ci.yml primary-job gate steps run verbatim on Python 3.11.16, plus the firestarter_app gitlink disposition"
  - "evidence/190-slug-sweep.txt: the boundary-aware bare-slug sweep across firestarter_app (0 matches) paired with its henols/firestarter_prom non-vacuity control (8, unchanged)"
  - "The meta repository's firestarter_app gitlink advanced to 560ec24523eb2f8c643c9db3dd302efecf57e2e1, the tip of all six 190-01/02/03 submodule commits"
affects: [191, 192, 193]

actuals:
  tokens: 11931
  tasks: 3
  commits: 4
plan_head_before: d8585fbac673091e2c8a846cad0387b8dec4aa2e

tech-stack:
  added: []
  patterns:
    - "PYTHONSAFEPATH (-P) on every child interpreter invocation, discovered necessary this session: running from /workspaces (the meta repo) with cwd on sys.path lets the sibling firestarter/ FIRMWARE submodule (a bare directory, no __init__.py) form a namespace package that shadows the real editable-installed firestarter HOST package before its finder is ever consulted -- -P stops Python from adding cwd to sys.path at all, independent of caller cwd"
    - "Rebinding an imported-by-name constant for a live-failure demonstration must rebind it on EVERY module that imported it by name, not just the one making the network call -- firestarter.firmware (the network call) and firestarter.cli_handlers (the printed message) each hold their own independent binding of FIRESTARTER_RELEASES_URL"
    - "A live-network evidence script distinguishes done from undone by asserting response.history, never by success alone -- success is compatible with both states when the old identifier still transparently redirects"

key-files:
  created:
    - .planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh
    - .planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-04-endpoint-contract.txt
    - .planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-01-ci-equivalent.txt
    - .planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-slug-sweep.txt
  modified:
    - firestarter_app (gitlink advance only, in the meta repository)

key-decisions:
  - "Every child Python invocation in the fixture uses `-P` (PYTHONSAFEPATH). Discovered empirically: the fixture failed with `ImportError: cannot import name '__version__' from 'firestarter' (unknown location)` on its first run from /workspaces, because the sibling firestarter/ (C++ firmware) submodule -- a directory named exactly 'firestarter' with no __init__.py -- won the namespace-package race over the real editable-installed package via PathFinder before the package's own meta-path finder was ever consulted. -P removes cwd from sys.path entirely, making every check correct regardless of the caller's working directory rather than requiring callers to `cd` into firestarter_app first."
  - "Check 4b (the unreachable endpoint) rebinds FIRESTARTER_RELEASES_URL on BOTH firestarter.firmware (which makes the network call) and firestarter.cli_handlers (which prints the failure message naming the endpoint). Rebinding only the former, as RESEARCH Pitfall 7 discusses in isolation, would leave the printed message naming the real, working endpoint rather than the nonexistent one -- the same by-name-import principle applies independently to both modules that hold their own binding of the constant."
  - "Used `.venv311/bin/python -m ensurepip --upgrade` to bootstrap pip 24.0 into .venv311 (created via `uv venv` with no seed packages), then ran the ci.yml steps against `.venv311/bin/pip3` -- functionally identical to a bare `pip` on PATH, recorded explicitly in the CI-equivalent transcript rather than silently substituting `uv pip`, since D-17's substance is the interpreter version and package resolution, not the literal binary name."
  - "Used unittest.mock.patch.object(FirmwareManager, \"check_current_firmware\", ...) at the class, matching 190-01's own CLI-level test pattern, since CliRunner().invoke(cli, argv) with no obj= constructs a real FirmwareManager with nothing to inject a mock into."

requirements-completed: [URL-01, URL-03, URL-04]

coverage:
  - id: D1
    description: "Both release channels (stable, pre) resolve live against henols/firestarter_fw with redirects: 0 on both API endpoints -- the only observable distinguishing this from the pre-change transparent 301"
    requirement: "URL-01"
    verification:
      - kind: other
        ref: "endpoint-contract-fixture.sh check 1/2, captured in evidence/190-url-04-endpoint-contract.txt (redirects: 0 x2, resolved == requested x2)"
        status: pass
    human_judgment: false
  - id: D2
    description: "A real firestarter_uno.hex (60768 bytes) downloaded through the package's own _download_firmware_file helper and confirmed Intel HEX (every non-empty line starts ':', final record ':00000001FF'); removed by explicit path afterward, directory and its config.json/reports/ left intact"
    requirement: "URL-01"
    verification:
      - kind: other
        ref: "endpoint-contract-fixture.sh check 3, captured in evidence/190-url-04-endpoint-contract.txt"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both URL-04 failure modes demonstrated live, each exiting 1 with a distinct named message: the asset-less case (fw --board uno328pb --stable, board identity simulated, release resolution live) and the unreachable case (fw --list against a genuinely nonexistent slug, a real 404)"
    requirement: "URL-04"
    verification:
      - kind: other
        ref: "endpoint-contract-fixture.sh check 4a/4b, captured in evidence/190-url-04-endpoint-contract.txt (exit_code: 1 x2, messages confirmed to differ, neither containing 'already up to date')"
        status: pass
    human_judgment: false
  - id: D4
    description: "The five ci.yml primary-job gate steps run verbatim on Python 3.11.16: ruff check, ruff format --check, pytest with coverage (2145 passed, 84.91% against the 70% floor), and the firestarter --help smoke test -- all green"
    requirement: "URL-01"
    verification:
      - kind: other
        ref: "evidence/190-url-01-ci-equivalent.txt, all five steps with raw output"
        status: pass
    human_judgment: false
  - id: D5
    description: "firestarter_app is proved slug-clean by a boundary-aware sweep (0 bare-slug matches) paired with its non-vacuity control (henols/firestarter_prom, 8 files, unchanged)"
    requirement: "URL-03"
    verification:
      - kind: other
        ref: "evidence/190-slug-sweep.txt; git -C firestarter_app grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- . (0), git -C firestarter_app grep -lE 'henols/firestarter_prom' -- . | wc -l (8)"
        status: pass
    human_judgment: false
  - id: D6
    description: "The meta repository's firestarter_app gitlink advanced to this phase's tip, as its own commit touching no other path, with the disposition (pinned sha, not on origin, resolves at milestone push) recorded in both the evidence transcript and this SUMMARY"
    verification:
      - kind: other
        ref: "git -C /workspaces ls-tree HEAD firestarter_app == git -C /workspaces/firestarter_app rev-parse HEAD (560ec24523eb2f8c643c9db3dd302efecf57e2e1); git -C /workspaces show --stat --format= HEAD~2 lists only firestarter_app"
        status: pass
    human_judgment: false

duration: ~20min
completed: 2026-09-13
status: complete
---

# Phase 190 Plan 04: Live Endpoint Contract, CI-Equivalent Run, and Gitlink Advance Summary

**A committed, re-runnable fixture proves `fw` resolves both firmware release channels against `henols/firestarter_fw` with zero redirect hops, downloads and format-checks a real firmware image, and demonstrates both URL-04 failure modes exiting 1 with distinct messages; the five Host CI gate steps run green on Python 3.11.16; the app repository is proved slug-clean; and the meta repository's `firestarter_app` gitlink now pins this phase's tip.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-09-13T17:58:21Z
- **Tasks:** 3 (all `type="auto"`)
- **Files created:** 4 (script + 3 evidence transcripts); 1 gitlink advanced

## Accomplishments

- Wrote `endpoint-contract-fixture.sh` (463 lines): a re-runnable, `--help`-documented, fail-closed live-network fixture covering all four D-14 checks in one coherent script, exactly mirroring `189-free-the-name/fresh-clone-fixture.sh`'s skeleton (header block, argument parsing, `SCRIPT_DIR`-derived paths, `mktemp` scratch bookkeeping with an `EXIT` trap, labelled-value emission before every verdict, bail-on-first-assertion with the expectation/pre-state/next-action named, and a single all-caps verdict token with a documented exit-code contract: 0 OK, 1 failure, 2 bad usage, 3 network unreachable via a real transport-level probe).
- Ran the fixture live against `henols/firestarter_fw`, capturing the full transcript: stable channel resolves to `2.0.6`, pre channel resolves to `3.0.0b29`, both API endpoints (`FIRESTARTER_RELEASE_URL`, `FIRESTARTER_RELEASES_URL`) read `redirects: 0` with `resolved == requested` — the one reading that distinguishes this from the pre-change state, where the bare slug answers with a transparent 301 and byte-identical data (RESEARCH Finding 1). A real `firestarter_uno.hex` (60768 bytes) was downloaded through `_download_firmware_file` and confirmed Intel HEX, then removed by explicit path.
- Demonstrated both URL-04 failure modes for real in the same script: the asset-less case (`fw --board uno328pb --stable`, with only `check_current_firmware` patched at the class to simulate an identified board — no programmer is attached and the milestone states `Bench: none` — while the release resolution ran live against the real, correctly-named endpoint, and stable `2.0.6` genuinely ships no `uno328pb` asset) and the unreachable case (a throwaway child process rebinding `FIRESTARTER_RELEASES_URL` to a real nonexistent slug, producing a genuine live 404). Both exit 1 with distinct, named messages; neither contains "already up to date".
- Discovered and fixed a namespace-package shadowing defect the first run surfaced: invoking Python from `/workspaces` let the sibling `firestarter/` (C++ firmware) submodule — a bare directory named exactly `firestarter` with no `__init__.py` — win the namespace-package resolution race ahead of the real, editable-installed `firestarter` host package's own meta-path finder, breaking every import with `ImportError: cannot import name '__version__' from 'firestarter' (unknown location)`. Fixed by invoking every child interpreter with `-P` (`PYTHONSAFEPATH`, Python 3.11+), which removes the caller's cwd from `sys.path` entirely — cwd-independent, not merely worked around by `cd`-ing into the app repo first.
- Ran the five `ci.yml` primary-job gate steps verbatim on Python 3.11.16 (`.venv311`, bootstrapped a `pip` via `ensurepip` since the `uv`-created venv shipped none): `ruff check` clean, `ruff format --check` clean (158 files), `pytest --cov` **2145 passed** at **84.91%** coverage against the 70% floor (up from the pre-phase baseline of 2129 passed / 84.74%), and a clean `firestarter --help` smoke test after `pip install -e .`. Recorded plainly that this is the local equivalent of an Actions run — the milestone branch is not on origin and every outward-facing step is operator-gated — and that `ci-py32`'s two further steps were not reproduced, though the one test this phase's earlier plans adapted (in the pyusb-absence family) sits inside the primary job's scope and ran as part of step 4.
- Captured the boundary-aware bare-slug sweep across `firestarter_app`: 0 matches, paired with the `henols/firestarter_prom` non-vacuity control (8 files, unchanged from 190-02's own reading) — stating explicitly that a zero paired with a zero control would be a failed gate, not a pass, and naming what the sweep deliberately excludes (the meta repository, Phase 192's; `.planning/milestones/`, historical-by-intent).
- Advanced the meta repository's `firestarter_app` gitlink to `560ec24523eb2f8c643c9db3dd302efecf57e2e1` — the tip of all six 190-01/02/03 submodule commits — as its own commit touching no other path, as the phase's deliberately last act. Recorded the disposition (pinned sha, not on origin, resolves at the operator-gated milestone push, both submodule gitlinks now in that state) in both the evidence transcript and here.

## Task Commits

All four commits are in the **meta** repository (`/workspaces`), on `v1.38-repository-rename`:

1. **Task 1: Write and run the live endpoint-contract fixture** - `23d6aa5e` (feat)
2. **Task 2: Reproduce Host CI verbatim on Python 3.11, and prove the repository is slug-clean** - `3eef0851` (docs)
3. **Task 3a: Advance the firestarter_app gitlink** - `59f67b5a` (feat)
4. **Task 3b: Record the gitlink disposition** - `af339f9a` (docs)

No commit was made inside the `firestarter_app` submodule by this plan — Tasks 1-3's app-repository consumption (running the fixture and the CI steps against it) was read-only; the app repository's own working tree is confirmed unchanged (`git -C firestarter_app status --porcelain` empty throughout, checked after every task).

## Files Created/Modified

- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh` (new, 463 lines, executable) — the D-14/D-16 evidence script
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-04-endpoint-contract.txt` (new) — the captured fixture run plus its "what this proves / does not prove" closing
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-01-ci-equivalent.txt` (new) — the five ci.yml gate steps' raw output plus the gitlink disposition
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-slug-sweep.txt` (new) — the D-05 boundary-aware sweep and its control
- `firestarter_app` (gitlink only, in the meta repository) — advanced from the pre-phase tip to `560ec24523eb2f8c643c9db3dd302efecf57e2e1`

## Decisions Made

- **`-P` (PYTHONSAFEPATH) on every child Python invocation in the fixture.** Not anticipated by the plan; discovered on the fixture's first live run. Documented as an inline explanation in the script itself (not a comment inside `firestarter_app/` — the script lives under `.planning/` and the no-comments rule does not reach it) and in this SUMMARY, since the failure mode is specific to this meta-repo layout (a sibling submodule literally named `firestarter`) and would otherwise silently break the fixture for the next person who runs it from a different cwd.
- **Both `firestarter.firmware.FIRESTARTER_RELEASES_URL` and `firestarter.cli_handlers.FIRESTARTER_RELEASES_URL` rebound for check 4b.** RESEARCH Pitfall 7 names only the former (the module making the network call); the latter holds its own independent by-name binding used solely for the printed failure message. Rebinding only the network-calling module would have produced a technically-live 404 whose printed message still named the real, correct endpoint — an accurate exit code with a misleading message, which fails the plan's own "the message names the nonexistent endpoint" requirement.
- **`ensurepip` to bootstrap `pip` into `.venv311`**, since the environment was created by `uv venv` (no seed packages) and had no `pip` binary. Ran the five gate steps against `.venv311/bin/pip3` and stated this substitution plainly in the transcript rather than silently using `uv pip`, since D-17's substance is proving the *interpreter version* is right, not the exact package-manager binary name.
- **Class-level `patch.object(FirmwareManager, "check_current_firmware", ...)`** for check 4a, matching 190-01's established CLI-level test pattern (`CliRunner().invoke(cli, argv)` with no `obj=` constructs its own real `FirmwareManager`, so there is nothing to inject an instance-level mock into).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed a namespace-package import failure in the fixture's first live run**
- **Found during:** Task 1, the fixture's first end-to-end run (before any commit).
- **Issue:** Every Python child invocation failed with `ImportError: cannot import name '__version__' from 'firestarter' (unknown location)` when the script was run with cwd at `/workspaces`. Root cause: `/workspaces/firestarter` (the firmware C++ submodule, a directory with no `__init__.py`) formed a namespace package that PathFinder resolved before the real editable-installed `firestarter` host package's own meta-path finder was consulted, because Python auto-prepends the caller's cwd to `sys.path` for `-c`/stdin scripts.
- **Fix:** Added `-P` (PYTHONSAFEPATH) to every `"$PYTHON_BIN"` invocation in the script, including the precondition import check. This is a Python 3.11+ flag that removes the cwd-prepend behaviour entirely, making the fixture correct regardless of the caller's working directory rather than merely working around the immediate symptom.
- **Files modified:** `endpoint-contract-fixture.sh` (all five child-interpreter invocations plus the precondition check)
- **Verification:** Re-ran the full fixture from `/workspaces`; all four checks passed with `ENDPOINT CONTRACT OK` and exit 0. Also confirmed the script still exits correctly under `--help` and `--nonsense`.
- **Committed in:** `23d6aa5e` (the fix was made and verified before the first commit, so no separate commit exists for it)

---

**Total deviations:** 1 auto-fixed (Rule 1 — a bug discovered by actually running the fixture, not a defect in the plan's design).
**Impact on plan:** The fix is entirely internal to the evidence script; none of the plan's required checks, assertions, or evidence content changed. All `<verify>` legs for all three tasks pass as specified.

## Issues Encountered

- The background `pytest tests/ --cov=...` run for Task 2 took longer than expected (346 seconds) because `tests/test_skip_census.py` itself spawns a full second `pytest` subprocess over nearly the entire suite to census skip markers — this is expected, pre-existing behaviour of that test module (confirmed by reading its docstring), not a regression, and the outer run's own timing (346s) already includes it. No action needed; the run was awaited to completion rather than interrupted.
- No other issues. Every `<automated>` verify command in the plan for all three tasks was run and read as specified.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 190's three requirements (URL-01, URL-03, URL-04) are now fully evidenced end-to-end: constants repointed and pinned (190-01/02), dead-endpoint behaviour on both the update path and the list path (190-01/03), and this plan's live proof that the endpoints resolve directly with zero redirects, plus Host CI green on py3.11 and the app repository slug-clean. **Per this plan's scope, `.planning/REQUIREMENTS.md` itself was NOT edited** — the orchestrator owns that write per this run's `<orchestrator_owned_artifacts>` instruction (which named STATE.md, ROADMAP.md and config.json explicitly; REQUIREMENTS.md checkbox-marking was treated as in the same "orchestrator writes planning artifacts centrally" category since this plan's tracking output is scoped to SUMMARY.md, evidence artifacts, and commits). The `requirements-completed` frontmatter field above carries all three IDs for the orchestrator to act on.
- Both submodule gitlinks (`firestarter` from Phase 189, `firestarter_app` from this plan) now name commits not present on origin. Phase 189's `fresh-clone-fixture.sh` is expected to report its documented exit-3 "gitlink commit not present on remote" case for both submodules until the milestone is pushed — this is expected, not a regression, and is stated in both `189`'s and this plan's evidence records.
- `endpoint-contract-fixture.sh` is ready for Phase 191 to re-run against the stable release it cuts, and for a post-claim milestone to re-run to watch `henols/firestarter`'s 404 arrive (per D-16's stated re-use).
- Phase 192's SWEEP-01/02 can cite this plan's `190-slug-sweep.txt` as the app repository's already-clean baseline and proceed directly to the meta repository's own sweep.
- No blockers.

---
*Phase: 190-endpoints-that-do-not-depend-on-a-redirect*
*Completed: 2026-09-13*

## Self-Check: PASSED

All claimed files and commits verified present:
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh` — found
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-04-endpoint-contract.txt` — found
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-01-ci-equivalent.txt` — found
- `.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-slug-sweep.txt` — found
- Meta-repo commits `23d6aa5e`, `3eef0851`, `59f67b5a`, `af339f9a` — found in `git log --oneline --all`
