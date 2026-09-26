---
phase: 127-host-dfu-installer
verified: 2026-08-01T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 127: Host DFU Installer Verification Report

**Phase Goal:** `firestarter_app` gains a working, tested, channel-gated py32 DFU install path with the
eight remaining gaps closed — landed independently of the firmware seams, in parallel with Phases
125–126.

**Verified:** 2026-08-01
**Status:** passed
**Re-verification:** No — initial verification

All checks below were re-executed independently in this session against the live trees (not copied
from any 127-*-SUMMARY.md or from `127-NONREGRESSION.md`'s own numbers, though every figure obtained
here was then cross-checked against that document's claims). Every command was run from
`/workspaces/firestarter_app` in the real sibling layout (`basename $PWD` = `firestarter_app`,
`../firestarter/.git` present).

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria 1–5)

| # | Truth (ROADMAP Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | `4ee64a1` is a literal parent of the merge commit; `--usb-id` rejected on simulated stable exactly like `--dfu-probe`; full suite passes at its exact collected count, 0 failures | VERIFIED | `git log -1 --format=%P 63ce44e` → `ccbc401e1... 4ee64a14a8933b60896c8b168bb1c7e34d788fa4` (contains it, independently re-run). Live subprocess with `firestarter.__version__` patched to `3.0.0` before import: `firestarter --board py32f071 fw --usb-id 1234:5678` raises `click.exceptions.UsageError: no such option: --usb-id`, same code path (`_reject_py32_only_option`, `grep -c 'no such option' firestarter/cli_handlers.py` = 1) `--dfu-probe` uses. `pytest tests/ --collect-only -q` → **1293 tests collected**; `pytest tests/ -q --no-cov` → **1293 passed, 0 failed, 0 skipped**, 30 snapshots passed (independently run this session, ~165–182s) |
| 2 | A CI leg installs `.[test,py32]` distinct from `.[test]`-only, and a test genuinely imports `pyusb` and exercises real `usb.core.find`/`ctrl_transfer` | VERIFIED | `.github/workflows/ci.yml` has a second `ci-py32` job (distinct from `ci`'s `.[test]`-only install), triggered additionally by `workflow_dispatch:`. `gh run view 30708836339 --json headSha,conclusion,jobs` (re-queried live, this session): `headSha` = `a62ca7647aed22d8c82ecf3aac3db4a81780260f` (string-equal to current local HEAD), `ci-py32` job **success** (all 6 steps, including "Prove pyusb genuinely imports" and "Run the real-pyusb API surface tests"), primary `ci` job **failure** at the mypy watermark step only (see Criterion-adjacent finding below — pre-existing, not this phase's regression) |
| 3 | `PyusbMissingError`'s `# pragma: no cover` removed and covered directly; `fw --list`/`fw --help` proven exit 0 with pyusb genuinely uninstalled | VERIFIED | `grep -n 'pragma: no cover' firestarter/py32_dfu.py` → only lines 754/760 (the unrelated `_dev`/`_index` property guards); the `_require_usb()` `except ImportError` clause carries none. `tests/test_py32_pyusb_absent.py` (11 tests, run individually this session, 11 passed) uses a genuine `sys.meta_path.MetaPathFinder` that raises `ModuleNotFoundError` for `usb`/`usb.*`, proving `fw --help`, `fw --list`, `firestarter --help` all exit 0 with `usb` truly unreachable |
| 4 | `DFU_UPLOAD` readback fails soft on `bitCanUpload=0`; one test anchors DFU opcodes to UM1504/DFU 1.1 values independent of the module | VERIFIED | Read `tests/test_py32_dfu.py::TestReadbackVerification` directly (8 tests): `test_bit_can_upload_unset_fails_soft` and `test_plain_dfu11_fails_soft_with_cause_named` assert `ok is True`, no exception, `verify_result` set to a named `SKIPPED_*` member with a `verify_reason` string — soft-fail confirmed by reading the assertions, not just running them. `test_differing_readback_is_a_hard_failure` / `test_truncated_readback_is_a_hard_failure_too` both assert `pytest.raises(DfuProtocolError)` and `verify_result is MISMATCH` — hard-fail confirmed. `test_mismatch_never_manifests` confirms zero `_finish()` calls on the MISMATCH path. `tests/test_dfu_opcode_anchors.py` (7 tests, run this session, 7 passed) defines its own literal opcode constants independent of `firestarter/py32_dfu.py`'s definitions (confirmed by reading the file: it hardcodes `0x00`-style DFU 1.1 request codes and asserts equality against the imported module's constants, not the reverse) |
| 5 | `pyusb>=1.3.1,<2` in packaging metadata; channel gating proven both ways with import-time-not-cached assertion | VERIFIED | `grep -n pyusb pyproject.toml` → `"pyusb>=1.3.1,<2"` in `[py32]` extra. `tests/test_py32_channel_gating.py::test_board_choices_are_computed_at_import_not_cached_across_a_version_change` exists and asserts on two separate subprocesses with `firestarter.__version__` patched before `firestarter.cli_handlers` is ever imported (read directly). 14 tests in that module, run this session, 14 passed |

**Score:** 5/5 truths verified, 0 present-but-behavior-unverified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter/py32_dfu.py` | `VerifyResult` enum, readback/verify sequence, hoisted `_finish()` | VERIFIED | `VerifyResult` enum present (`VERIFIED`/`SKIPPED_NO_UPLOAD`/`SKIPPED_PLAIN_DFU`/`MISMATCH`); `grep -c 'self\._finish(' firestarter/py32_dfu.py` = 1, single call site inside `flash()` at line 726 |
| `firestarter/cli_handlers.py` | Shared `_reject_py32_only_option()`, import-time `_BOARD_CHOICES` | VERIFIED | `grep -c 'no such option'` = 1; `_BOARD_CHOICES`/`_PY32_ENABLED` computed at module scope (lines 143–144), confirmed by reading the file |
| `.github/workflows/ci.yml` | `workflow_dispatch:` + isolated `ci-py32` job | VERIFIED | Both present, read directly; job installs `.[test,py32]`, runs real-pyusb steps |
| `pyproject.toml` | `pyusb>=1.3.1,<2` floor | VERIFIED | Confirmed via grep |
| `tests/test_py32_dfu.py` | 69 tests (58 pre-existing + 11 new: `TestReadbackVerification` 8 + `TestInstallWithDfuVerifyLogging` 3) | VERIFIED | Ran module, 69 passed |
| `tests/test_dfu_opcode_anchors.py` | 7 tests anchoring opcodes independently | VERIFIED | Ran module, 7 passed |
| `tests/test_py32_channel_gating.py` | 14 tests, both-ways gating | VERIFIED | Ran module, 14 passed |
| `tests/test_py32_flash_map_host.py` | 16 tests incl. linker-script parity | VERIFIED | Ran module, 16 passed; parity confirmed against live `/workspaces/firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` (`APP_REGION_END` = `0x0801E000` string-equals `ORIGIN(CONFIG)`) |
| `tests/test_py32_pyusb_absent.py` | 11 tests, genuine import blocker | VERIFIED | Ran module, 11 passed |
| `tests/test_py32_packaging.py` | 12 tests incl. doc-parity gate | VERIFIED | Ran module, 12 passed |
| `tests/test_pyusb_gating.py` | 6 tests | VERIFIED | Ran module, 6 passed |
| `doc/PY32F071-FIRMWARE-INSTALL.md` | Updated for 120K/8K map, readback step, raised floor | VERIFIED | Contains "120 KiB above `0x08000000`" and the three-outcome readback description (`VERIFIED`, soft-skip, hard MISMATCH) |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `cli_handlers.py` `--usb-id`/`--dfu-probe` | `_reject_py32_only_option()` | shared function, one call site each | WIRED | `grep -c` confirms single implementation path |
| `py32_dfu.py flash()` | `_finish()` | single hoisted call site | WIRED | `grep -n` shows exactly one call, inside `flash()`, after readback (confirmed by reading surrounding lines and the ordering tests) |
| `firmware.py` install path | `flasher.verify_result` | `if flasher.verify_result is VerifyResult.VERIFIED` / "written but NOT verified" message | WIRED | Both lines present in `firestarter/firmware.py`, read directly |
| `ci.yml` `ci-py32` job | `usb.core.find`/`ctrl_transfer` | `tests/test_pyusb_api_surface.py` | WIRED (proven on CI, not locally — pyusb absent in this devcontainer) | CI Run `30708836339` shows the job green with the real-pyusb steps executed; independently re-queried this session |
| `py32_dfu.py` flash-map constants | `/workspaces/firestarter/platform/py32f071/linker/PY32F071xB_FLASH.ld` | `tests/test_py32_flash_map_host.py::TestLinkerScriptParity` | WIRED | Both sides read directly this session; values match exactly |

### Requirements Coverage

| Requirement | Source Plan(s) | Status | Evidence |
|---|---|---|---|
| HOST-01 | 127-01, 127-02 | SATISFIED | Merge parent confirmed (`git log -1 --format=%P`); `flash_method()` router + accepted-deviation record confirmed present in `tests/test_py32_packaging.py::test_d17_...` |
| HOST-02 | 127-04 | SATISFIED | Live `--usb-id` refusal reproduced this session on simulated stable channel |
| HOST-03 | 127-08, 127-09 (127-05, 127-10 list it for traceability only, do not discharge it — confirmed by reading their `must_haves.truths` frontmatter, which explicitly states this) | SATISFIED (mock-only ceiling explicitly carried, matches REQUIREMENTS.md wording) | `VerifyResult` enum + soft/hard fail tests read and run; explicit non-claim confirmed in REQUIREMENTS.md itself |
| HOST-04 | 127-06, 127-11 | SATISFIED | CI run re-queried live this session; `ci-py32` green, head SHA matches current HEAD exactly |
| HOST-05 | 127-07 | SATISFIED | Pragma-count and subprocess-blocker tests confirmed |
| HOST-06 | 127-03 (127-09 closes the `bitCanUpload` handoff) | SATISFIED (UM1504 residual explicitly carried as open, not claimed resolved — matches REQUIREMENTS.md wording) | `test_dfu_opcode_anchors.py` read and run |
| HOST-07 | 127-02 | SATISFIED | `pyproject.toml` floor confirmed |
| HOST-08 | 127-04 | SATISFIED | `test_board_choices_are_computed_at_import_not_cached...` confirmed present and passing |

**Orphaned requirements check:** `.planning/REQUIREMENTS.md`'s "Phase 127" traceability row cites only
HOST-01…HOST-08 — no additional IDs mapped to Phase 127 that are absent from the 12 plans' frontmatter.
None found.

### Anti-Patterns Found

Scanned all files touched by this phase (`firestarter/py32_dfu.py`, `firestarter/cli_handlers.py`,
`firestarter/firmware.py`, `pyproject.toml`, `.github/workflows/ci.yml`, and all 8 new/modified test
modules) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and empty-implementation patterns. **None
found.** No debt markers in any phase-127-touched file.

### Behavioral Spot-Checks / Full-Suite Execution

| Check | Command | Result | Status |
|---|---|---|---|
| Full suite collection | `pytest tests/ --collect-only -q` | 1293 tests collected | PASS |
| Full suite run (once, this session) | `pytest tests/ -q --no-cov` | 1293 passed, 0 failed, 0 skipped, 30 snapshots passed | PASS |
| Coverage gate | `pytest tests/ --cov=firestarter --cov-fail-under=70` | 81.88% total (exit 0); `py32_dfu.py` 79% | PASS |
| ruff lint | `ruff check firestarter/ tests/` | All checks passed! | PASS |
| ruff format | `ruff format --check firestarter/ tests/` | 114 files already formatted | PASS |
| mypy watermark (local, known fail-open) | `python tools/check_mypy_watermark.py` | `mypy errors: 1 (watermark: 35)` — reproduces the documented fail-open bug exactly | PASS (as a reproduction; see finding below) |
| mypy honest count, independent venv (python3.11, `.[test]`) | `python -m mypy firestarter/ tests/` | **69 errors** on current HEAD `a62ca76` | Matches CI Run 2's step log (`69 errors (watermark: 35)`) and the claimed 69→72→69 zero-net-debt narrative — independently reproduced in a fresh throwaway venv this session, not copied from any SUMMARY |
| Per-module test counts | 7 named modules run individually | 12/7/14/16/6/11/69 = matches; combined run of the first 6 modules + `TestReadbackVerification` = 74 passed | PASS |
| `asset_candidates("py32f071")` | direct call | `['firestarter_py32f071.hex', 'firestarter_py32f071.bin']` | PASS |
| Firmware repo untouched | `git status --porcelain \| wc -l` in `/workspaces/firestarter` | 0 | PASS |
| Host repo porcelain | `git status --porcelain` | 5 lines, exactly the known pre-existing set (`.gitignore` modified, 4 untracked) | PASS |
| CI evidence, re-queried live | `gh run view 30708836339 --json ...` | `ci-py32` success, `ci` failure at mypy step only, headSha = current local HEAD | PASS |

### Claim-Ceiling Check

Ran `check_permitted_claims.py` against `127-NONREGRESSION.md` this session:

```
PASS: scanned ../127-host-dfu-installer/127-NONREGRESSION.md; 1 file(s) carry the required silicon
caveat
```

Scanned all 12 SUMMARY.md files, all 12 PLAN.md files, `127-CONTEXT.md`, and `127-NONREGRESSION.md` for
forbidden-claim phrasing. Every match found (`127-11-PLAN.md`, `127-01-SUMMARY.md`, `127-09-SUMMARY.md`,
`127-12-PLAN.md`, `127-12-SUMMARY.md`, `127-CONTEXT.md`, `127-04-SUMMARY.md`) is a **non-claim
statement** — each explicitly states what is NOT claimed, in the same sentence or surrounding
paragraph, rather than asserting the forbidden claim itself. No document in this phase asserts that
firmware runs on PY32F071 silicon, that the DFU install works end to end, or that any part of the
sequence is bench-/hardware-/silicon-validated. HOST-03 is explicitly and correctly qualified as
"asserted against a mock only" in both `REQUIREMENTS.md` and every artifact that discusses it.

### Findings Carried Forward (not scored as phase gaps, per verification instructions)

1. **Primary `ci` job is RED on a pre-existing mypy-debt finding, not a Phase 127 regression.**
   Independently reproduced this session in a fresh Python 3.11 venv: mypy error count on the
   pre-127 baseline (`ccbc401`) = 69; on this phase's tree before the fix (`84cdd86`) = 72; on the
   final tree (`a62ca76`, current HEAD) = 69. Zero net debt contributed by this phase, matching CI
   Run 2's own step log exactly (`mypy errors: 69 (watermark: 35)`). The local
   `tools/check_mypy_watermark.py` gate is confirmed fail-open in this devcontainer (reports 1 error,
   passes) — a separate, already-recorded defect, not fixed by this phase per explicit operator scope
   decision ("fix my 3, record the rest").
2. **Attribution of the 127-11 push/dispatch is recorded honestly.** `127-11-SUMMARY.md` explicitly
   states the orchestrator (not the operator personally, and differing from Plans 124-11/125-05/126-11)
   ran `git push` and `gh workflow run` under explicit operator authorization, and that no task inside
   Plan 127-11 executed either command. Confirmed by reading the SUMMARY directly — not overclaimed as
   "the operator pushed."
3. **Minor citation drift in `127-NONREGRESSION.md` §4 Criterion 4** — it names
   `test_differing_readback_is_a_hard_failure_too`, but the actual test name in
   `tests/test_py32_dfu.py` is `test_differing_readback_is_a_hard_failure` (the `_too` suffix belongs
   to the adjacent `test_truncated_readback_is_a_hard_failure_too`). Cosmetic citation error only —
   both tests exist, both pass, both assert the claimed hard-fail behavior. Not scored as a gap.
4. **Known, already-recorded findings confirmed present in the artifacts** (not re-reported as new):
   C-1 disproof and 127-04 fix; A1's UM1504 residual (network-unreachable, USB DFU 1.1 half
   independently fetched); Plan 127-05's three commits carrying `(py32)` not `(127-05)` in their
   subjects (confirmed via `git log --grep="127-05"` returning nothing, and by SHA `921f9eb`,
   `1843962`, `ee6c5af` existing with the correct D-13/D-14 content); 127-02's `extend-exclude` count
   of 2 (pre-existing, not a defect).

### Human Verification Required

None. All five ROADMAP success criteria, all eight HOST requirements, and the claim ceiling were
verifiable programmatically against the codebase, CI, and the sibling firmware repo. No visual,
real-time, or hardware-dependent behavior is claimed by this phase that would require human judgment —
the phase's own explicit ceiling (mock-only DFU verification, no PCB) is the same ceiling this
verification operates under, and it is honestly reflected everywhere checked.

### Gaps Summary

No gaps found. All five ROADMAP success criteria hold with direct evidence obtained independently in
this session (not merely re-stated from `127-NONREGRESSION.md`). All eight HOST requirements are
discharged by the plans that actually claim to discharge them, with the 127-05/127-10 traceability-only
distinction correctly recorded in those plans' own frontmatter. No overclaiming was found anywhere in
the phase's artifacts — every place a forbidden-sounding phrase appears, it appears as an explicit
non-claim. The two items flagged in the task prompt as "must not be scored as failures" (pre-existing
mypy debt, operator-authorized gate removal) were independently confirmed to be accurately recorded
and are not scored as gaps.

---

_Verified: 2026-08-01_
_Verifier: Claude (gsd-verifier)_
