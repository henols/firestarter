---
phase: 190-endpoints-that-do-not-depend-on-a-redirect
verified: 2026-09-13T18:25:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-01-PLAN.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-01-SUMMARY.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-02-PLAN.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-02-SUMMARY.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-03-PLAN.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-03-SUMMARY.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-04-PLAN.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-04-SUMMARY.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-CONTEXT.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/190-REVIEW.md"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/endpoint-contract-fixture.sh"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-slug-sweep.txt"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-01-ci-equivalent.txt"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-03-pin-falsification.txt"
  - ".planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-url-04-endpoint-contract.txt"
  - "firestarter_app/.planning/codebase/INTEGRATIONS.md"
  - "firestarter_app/firestarter/cli_handlers.py"
  - "firestarter_app/firestarter/constants.py"
  - "firestarter_app/firestarter/firmware.py"
  - "firestarter_app/firestarter/submit.py"
  - "firestarter_app/tests/test_endpoint_constants.py"
  - "firestarter_app/tests/test_firmware_install.py"
  - "firestarter_app/tests/test_fw_list_failure_vs_empty.py"
  - "firestarter_app/tests/test_fw_update_dead_endpoint.py"
  - "firestarter_app/tests/test_py32_pyusb_absent.py"
covered_digest: "v1:sha256:f5ae3812a37bfec6fb3f01d52ec8b28707a4eafbde33fdae097636f10288addd"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 190: Endpoints That Do Not Depend on a Redirect — Verification Report

**Phase Goal:** On `beta`, nothing in the host application reaches the firmware repository through a
redirect, and a broken endpoint is distinguishable in the output from an up-to-date firmware.
**Verified:** 2026-09-13
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All three `FIRESTARTER_*_URL` constants address `henols/firestarter_fw`; no test, fixture or docstring names the bare `henols/firestarter` endpoint | ✓ VERIFIED | `constants.py` reads all three URLs with `_fw`. Independently re-ran the boundary-aware sweep: `git grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- .` → 0, paired with the non-vacuity control `henols/firestarter_prom` → 8 (matches evidence). |
| 2 | The two hardcoded URLs in `test_firmware_install.py` are derived from the constants, so changing a constant alone fails a test — proved by demonstration | ✓ VERIFIED | Both `next_url` sites interpolate `FIRESTARTER_RELEASES_URL` (lines confirmed). The pin `tests/test_endpoint_constants.py` is a **hardcoded** expected-slug comparison (non-circular). I independently reverted `FIRESTARTER_RELEASES_URL` to the bare slug in place, ran the pin: 1 failed / 2 passed, failure named the exact constant; restored the file, confirmed `git diff --quiet` clean, re-ran: 3 passed. Matches the committed falsification transcript exactly. |
| 3 | `fw` against an unreachable or asset-less endpoint produces a message naming the failure, distinguishable from "already up to date" | ✓ VERIFIED (with a narrow, disclosed accuracy gap — see WR-02 below) | Independently drove `fw --list` with `list_releases` stubbed to `None`: exit 1, stderr names board + `henols/firestarter_fw` endpoint, **no** stdout output at all (stronger than required); `--json` variant: exit 1, stdout does not parse as JSON. Empty-result paths (`[]`) still exit 0 with header row / empty JSON array. Ran the committed `test_fw_update_dead_endpoint.py` suite (6/6 pass): bare-check unresolvable → `False`, exactly 1 ERROR record naming board + endpoint, message does not contain "already up to date"; `--install`/`--force` unresolvable → exactly 1 ERROR each (different, pre-existing guard); up-to-date path unchanged (`True`, 0 ERROR records); pinned channel names the by-tag endpoint with the tag rendered in. |
| 4 | Host CI is green on the milestone branch, and `fw` resolves a real firmware release end-to-end against the renamed repository | ✓ VERIFIED | Independently re-ran `endpoint-contract-fixture.sh` live: both API endpoints show `redirects: 0` and `resolved == requested`; real `firestarter_uno.hex` (60768 bytes) downloaded and confirmed Intel HEX; both URL-04 failure modes shown exiting 1 with distinct messages; app repo left clean, download removed by explicit path. Independently re-ran `ruff check`, `ruff format --check` (both clean) and the **full** `pytest tests/ --cov=firestarter --cov-fail-under=70` suite on `.venv311` (Python 3.11.16): **2145 passed, 84.91% coverage** — exact match to the committed CI-equivalent transcript. Confirmed this is documented as the local equivalent, not a real Actions run (milestone branch not on origin; push is operator-gated). |

**Score:** 4/4 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/constants.py` | Three constants addressing `firestarter_fw` | ✓ VERIFIED | Confirmed by reading the file; diff confined to the three URL strings only |
| `firestarter_app/firestarter/firmware.py` | `list_releases` two-state contract; `_endpoint_for_channel`; dead-endpoint guard | ✓ VERIFIED | Read in full; `is None` identity guard present at `list_releases`'s except arm; `_endpoint_for_channel` present and correct for stable/pre/pinned; guard immediately before final `return True`, condition `not latest_version or not download_url`, no flag inspection |
| `firestarter_app/firestarter/cli_handlers.py` | `fw --list` identity guard, stderr routing, exit codes | ✓ VERIFIED | Behaviorally exercised directly (see truth 3 evidence) |
| `firestarter_app/tests/test_endpoint_constants.py` | URL-03 pin | ✓ VERIFIED | Read in full; positive-only, per-constant, no negative/prefix assertion (`grep -cE 'not in|!=|startswith'` → 0); falsified myself |
| `firestarter_app/tests/test_fw_list_failure_vs_empty.py` | D-09/D-11/D-12 behavior tests | ✓ VERIFIED | 7 tests, ran green (16 passed across the four new/adapted modules together) |
| `firestarter_app/tests/test_fw_update_dead_endpoint.py` | D-06 guard tests | ✓ VERIFIED | 6 tests read in full and run green independently |
| `firestarter_app/tests/test_py32_pyusb_absent.py` | Adapted HTTP stub | ✓ VERIFIED | Ran green as part of the full suite (2145 passed) |
| `firestarter_app/firestarter/submit.py` | Repo-list slug corrected, `SUBMIT_REPO` untouched | ✓ VERIFIED | `SUBMIT_REPO = "henols/firestarter_prom"` byte-unchanged; one-word comment edit confirmed via diff |
| `firestarter_app/.planning/codebase/INTEGRATIONS.md` | Endpoint line corrected | ✓ VERIFIED | Diff confirmed: endpoint line now `firestarter_fw`, `FIRESTARTER_RELEASE_URL` cross-reference untouched |
| `.planning/phases/.../endpoint-contract-fixture.sh` | Re-runnable D-14 evidence script | ✓ VERIFIED | Re-ran it myself; reproduced the committed transcript's readings exactly |
| Evidence transcripts (4 files) | Captured, honest, re-derivable | ✓ VERIFIED | All four cross-checked against independent re-runs; contents match claims (redirect counts, pytest counts, coverage %, sweep counts) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `constants.py` | `api.github.com/repos/henols/firestarter_fw` | by-name import in `firmware.py` | ✓ WIRED | Live GET on both API constants: `redirects: 0`, `resolved == requested` |
| `firmware.py list_releases` | `cli_handlers.py fw --list` | `is None` identity guard | ✓ WIRED | Behaviorally reproduced: `None` → exit 1 stderr-only; `[]` → exit 0 with header/JSON `[]` |
| `manage_firmware_update` fall-through | `fw`'s process exit code | `return False` → `sys.exit(0 if ok else 1)` | ✓ WIRED | Reproduced via committed test suite: unresolvable release → `False` → exit 1 (evidenced end-to-end in the live fixture's check 4a) |
| channel selection | endpoint named in failure message | `_endpoint_for_channel` | ✓ WIRED for `stable`/`pinned`; ⚠️ **inaccurate for `pre`'s stable-fallback sub-path** | See WR-02 below |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|-----------------|--------------|--------|----------|
| URL-01 | 190-01, 190-02, 190-04 | Constants address `firestarter_fw`, no redirect dependency | ✓ SATISFIED | Truths 1 and 4 above |
| URL-03 | 190-02, 190-04 | Test fixtures derived + independently-falsifiable pin | ✓ SATISFIED | Truth 2 above |
| URL-04 | 190-01, 190-03, 190-04 | `fw` reports clear, actionable, distinguishable errors | ✓ SATISFIED | Truth 3 above (with WR-02 caveat, non-blocking) |

No orphaned requirements: `REQUIREMENTS.md` maps only URL-01/URL-03/URL-04 to Phase 190, and all three appear in at least one plan's `requirements:` frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` swept across every file this phase touched | none found | — |
| `firestarter/firmware.py` | 155-163, 955-956 (WR-02, from `190-REVIEW.md`, confirmed independently) | `_endpoint_for_channel("pre", ...)` unconditionally returns `FIRESTARTER_RELEASES_URL`, but `fetch_release_info(channel="pre")` silently falls back to `fetch_latest_release_info` (which hits `FIRESTARTER_RELEASE_URL`) when no prerelease candidate is found. If *that* fallback fetch is what fails, the guard's message names the wrong (but still correctly-slugged) endpoint. No test exercises `channel="pre"` through this guard — confirmed by reading `test_fw_update_dead_endpoint.py` in full: only bare/`--install`/`--force`/up-to-date/`pinned` cases exist. | ℹ️ Info / narrow | Does not violate ROADMAP criterion 3's literal wording (a failure message is still produced, still names *a* real endpoint under `henols/firestarter_fw`, still distinguishable from "already up to date"). It does blunt the phase's own stated intent that the message name "the endpoint actually addressed" in this one sub-path. Already surfaced by code review (WR-01/WR-02) and assessed by the orchestrator as real, narrow, and explicitly deferred as "a candidate for the phase verifier, or a follow-up alongside Phase 191." I concur with that disposition: not a blocker for this phase's four success criteria. Recorded here for a human decision on whether to fix now or track as a follow-up. |

No debt markers, no stub returns, no hardcoded empty fixtures found in any file this phase modified.

### Human Verification Required

None. Every truth was independently reproduced through direct code reading, self-run tests, a self-performed falsification of the URL-03 pin, an independent re-run of the committed live-network evidence fixture, and an independent full-suite + lint/format run matching the committed CI-equivalent transcript exactly.

### Gaps Summary

No gaps. All four ROADMAP success criteria are independently verified against the actual codebase (not merely against SUMMARY.md claims). One narrow, non-blocking accuracy defect (WR-02, `_endpoint_for_channel`'s handling of the `pre` channel's stable-fallback failure path) was confirmed to be real and is noted above for a human decision on timing of the fix — it does not cause any of the four success criteria to fail and was already disclosed and assessed by the code-review gate and the orchestrator.

---

_Verified: 2026-09-13_
_Verifier: Claude (gsd-verifier)_
