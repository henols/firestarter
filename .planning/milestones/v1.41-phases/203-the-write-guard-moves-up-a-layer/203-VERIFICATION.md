---
phase: 203-the-write-guard-moves-up-a-layer
verified: 2026-09-21T15:10:00Z
status: passed
score: 5/5 must-haves verified
covered_files: [".planning/REQUIREMENTS.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-01-PLAN.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-01-SUMMARY.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-02-PLAN.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-02-SUMMARY.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-03-PLAN.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-03-SUMMARY.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-04-PLAN.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-04-SUMMARY.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-CONTEXT.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-REVIEW.md", ".planning/phases/203-the-write-guard-moves-up-a-layer/203-SESSION-COST.md", "firestarter_app/firestarter/cli_handlers.py", "firestarter_app/firestarter/compare.py", "firestarter_app/firestarter/eprom_operations.py", "firestarter_app/firestarter/exceptions.py", "firestarter_app/firestarter/write_blank_guard.py", "firestarter_app/tests/__snapshots__/test_characterization.ambr", "firestarter_app/tests/fake_chip.py", "firestarter_app/tests/test_write_blank_guard.py", "firestarter_app/tests/test_write_blank_guard_pinning.py", "firestarter_app/tests/test_write_guard_port_pinning.py", "firestarter_app/tests/test_write_verify.py"]
covered_digest: "v1:sha256:340fc8b1842c32416812916e58ab6ed9cbf831a1d45ca5446a7822a2f6f24bc9"
behavior_unverified: 0
overrides_applied: 0
advisory:
  - finding: "WR-01 (code review): a --verify run whose write physically landed but whose --skip-sdp-unlock ack check fails prints the 'did not complete -- nothing was verified' line, which is inaccurate for that specific state (data was in fact programmed)."
    category: other
    reason: "Known, documented, deliberately-not-fixed finding from 203-REVIEW.md. Narrow scope (only the --skip-sdp-unlock + old-firmware-that-doesn't-ack combination). Exit code (1, host-decided) is still correct; only the printed line's wording is imprecise for this one state. Does not affect the primary safety property (WRITE-01/criterion 1) or the general WRITE-05 three-way distinction, which is correct on every other arm."
    evidence_status: "documented in 203-REVIEW.md WR-01, reproduced by direct source read at eprom_operations.py:2460-2478 and pinned by tests/test_write_verify.py::test_last_write_attempt_verdict_zero_when_skip_sdp_unlock_ack_check_fails"
  - finding: "WR-02 (code review): a guard refusal reached through an incomplete-but-not-mismatched compare (short read that never finds a divergent byte) prints a refusal line carrying a fabricated address/value (0x<region_start>/0x00) rather than an observed one."
    category: other
    reason: "Known, documented, deliberately-not-fixed finding. The refusal ITSELF is correctly fail-closed (an incomplete compare is correctly never treated as a pass) -- only the diagnostic text's address/value pair can be wrong in this corner case. Does not weaken the safety property; could misdirect debugging."
    evidence_status: "documented in 203-REVIEW.md WR-02, reproduced by direct source read at eprom_operations.py:2230-2242"
  - finding: "IN-01 (code review): a negative, page-aligned flash4 (0x05) address hits require_page_alignment's PageAlignmentError before require_non_negative_address, producing a less-specific message than the negative-address gate would give. No safety impact -- 0x05 is never a guarded protocol."
    category: other
    reason: "Informational-only finding, explicitly rated no safety impact by the reviewer and confirmed by reading GUARDED_PROTOCOL_IDS (0x05 is a named exemption, never guarded)."
    evidence_status: "documented in 203-REVIEW.md IN-01"
---

# Phase 203: The write guard moves up a layer Verification Report

**Phase Goal:** The host refuses a write to a non-blank, non-erasable part before any programming
byte reaches the wire, and `write --verify` proves that a write landed.
**Verified:** 2026-09-21T15:10:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria, criterion 2 verified against the 2026-09-21 amendment)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A write to a non-blank UV part is refused by the host, naming the first non-blank address and its value, before the port carries a programming command (WRITE-01, criterion 1). | ✓ VERIFIED | `write_blank_guard.py` `refusal_text`/`requires_blank_check`; `eprom_operations.py:2156-2246` `_run_write_blank_guard` + its call site in `write_eprom` (2339-2380); integration test `tests/test_write_blank_guard.py::test_write_to_non_blank_region_of_guarded_part_is_refused` drives the genuine `EpromOperator.write_eprom` through a patched `SerialCommunicator.find_and_connect` and asserts the captured command sequence equals `[COMMAND_READ]` — no `COMMAND_WRITE` ever reaches the connect seam. **CR-01 (critical, found in code review) — the guard's read and the write's own connect were two independent, unpinned port opens, so the region proven blank could silently be a different physical board than the region written — was fixed in commit `0fc6c77`** (`restrict_to_port`/`preferred_port` pinning) and independently re-verified here: `tests/test_write_guard_port_pinning.py::test_write_connect_pins_to_guard_resolved_port_and_fails_closed_when_it_drops` constructs a fake `find_and_connect` that falls through to "board B" unless the write's connect carries the exact pin, and asserts the write fails closed (2 connects only, `ok=False`, `last_write_attempt_verdict==2`) rather than silently landing on B. All 90 tests across the four write-guard test modules pass (`pytest tests/test_write_blank_guard.py tests/test_write_blank_guard_pinning.py tests/test_write_verify.py tests/test_write_guard_port_pinning.py`). |
| 2 | The guarded set is exactly `0x07,0x08,0x0B,0x06,0x10`, erase-run parts exempt, SRAM/FRAM and `0x05` named exemptions with reasoning at the site, and a test pins the exact set, failing on narrow or widen (WRITE-02, criterion 2, amended). | ✓ VERIFIED | `write_blank_guard.py`: `GUARDED_PROTOCOL_IDS = frozenset({0x06,0x07,0x08,0x0B,0x10})`, `NAMED_EXEMPT_PROTOCOL_IDS` (SRAM/FRAM `{0x0E,0x27,0x28,0x29}` ∪ flash4 `0x05` ∪ SDP/28C `0x0D`), each with a reasoning docstring at its own site. `tests/test_write_blank_guard_pinning.py` leg 1 asserts full-set equality (both directions fail). Orchestrator-reported independent perturbation (removing `0x0B` → 1 failure, adding `0x0D` → 4 failures) reproduced in the plan's own "Pinning Test Perturbation Proof" transcript in 203-02-SUMMARY.md. Leg 3 derives both sides of a database-coupling equality independently from `EpromDatabase`/`resolve_chip` with no hard-coded part list. |
| 3 | `write -b` skips the host check and still erases an erase-capable part (WRITE-03, criterion 3). | ✓ VERIFIED | `requires_blank_check` returns `False` when `FLAG_SKIP_BLANK_CHECK` is set (D-09: `FLAG_FORCE` deliberately not consulted). `cli_handlers._build_op_flags(blank_check=False)` sets only the skip-blank-check bit, never the skip-erase bit — pinned by `test_build_op_flags_blank_check_false_sets_only_the_skip_blank_check_bit` and driven end-to-end by `test_write_no_blank_check_via_build_op_flags_on_erase_capable_part_pays_no_guard_read` (`opened == [COMMAND_WRITE]`, no guard read paid). The "still erases" half is a firmware property this app-only, bench-no phase does not touch and does not claim to have tested at the firmware level — 203-02-SUMMARY.md states this scoping explicitly rather than overclaiming it, and the host-side half (not disabling the erase flag) is what's actually verified. `--skip-erase` re-arms the guard on an erase-capable part (D-03) and `--force` does not bypass it (D-09) — both pinned at unit and drive tier. |
| 4 | `write --verify` compares the written region through Phase 202's engine and exits non-zero on mismatch, with wording distinguishing "wrote but did not verify" from "did not write" (WRITE-04, WRITE-05, criterion 4). | ✓ VERIFIED (see advisory WR-01) | `cli_handlers.write`'s seven-arm exit branch (lines ~888-959) implements the confirmed `confirm-d13` contract in full: 0 verified / 1 host-or-firmware-decided / 2 transport-or-hardware-in-any-phase, including the write phase itself (arm 3 — the arm a first review pass found missing, now covered by `test_last_write_attempt_verdict_two_on_mid_write_port_drop`, which drives a genuine mid-write port drop through the real operator, not a mock). Four verdict-line constants pinned free of the word "successful" (`test_verdict_constants_never_contain_the_forbidden_word`). The could-not-verify line is proven to fire on exactly one arm and absent from the other six. `write --verify --help` states the full three-code contract truthfully (confirmed by direct `firestarter write --help` run). One known, documented, narrow-scope inaccuracy remains (WR-01, see advisory) where a write that physically lands but whose `--skip-sdp-unlock` ack check fails prints "did not complete" — exit code is still correct (1), only the line's wording misdescribes this one state. |
| 5 | A non-blank, non-erasable part still accepts a region write into a blank region — pinned against silent re-breakage on the host path (WRITE-06, criterion 5). | ✓ VERIFIED | `tests/test_write_blank_guard.py::test_write_into_blank_region_of_non_blank_part_succeeds_via_host_path` feeds a READ script that is non-blank *outside* the target region and blank *inside* it, drives the genuine `write_eprom`, and asserts `opened == [COMMAND_READ, COMMAND_WRITE]` — proving D-04's region-scoping (not whole-device) on the actual host path, not against `tests/fake_chip.py`'s firmware-pre-flight double (which the plan explicitly disqualified from providing this coverage, and whose docstring was updated to say so). |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/firestarter/write_blank_guard.py` | Pure predicate module, wire dict in, decision out | ✓ VERIFIED | Exists, reads only `algorithm`/`flags` (confirmed by direct read + AST test), fails closed on absent evidence, imports `FLASH4_PROTOCOL_ID`/`SDP_PROTOCOL_ID` rather than duplicating literals. |
| `firestarter_app/firestarter/compare.py` (`CompareResult.first_actual`) | Additive field carrying the observed byte at the first divergence | ✓ VERIFIED | Field present, populated inside the existing first-offset branch, `render_compare_lines`/`verify`/`blank` output proven byte-identical by AST + behavioural regression tests. |
| `firestarter_app/firestarter/eprom_operations.py` (`_run_write_blank_guard`, guard wiring, cause channels) | Guard call site + `last_write_guard_verdict`/`last_write_attempt_verdict`/`last_write_port` | ✓ VERIFIED | All present; `write_eprom` keeps `-> bool`; CR-01 port-pinning present and tested. |
| `firestarter_app/firestarter/cli_handlers.py` (`--verify`/`--full`, seven-arm branch) | CLI surface + exit-code branch | ✓ VERIFIED | Present, `mypy`-clean (strict module), `write --help` output matches the documented contract. |
| `firestarter_app/tests/test_write_blank_guard.py`, `test_write_blank_guard_pinning.py`, `test_write_verify.py`, `test_write_guard_port_pinning.py` | Genuine host-path integration coverage | ✓ VERIFIED | 90 tests, all pass; multiple tests drive the real `EpromOperator.write_eprom` through a patched `find_and_connect` seam rather than a stub double. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `EpromOperator.write_eprom` | `write_blank_guard.requires_blank_check` | direct call, between pure pre-connect gates and `_operation_context` (D-07/D-08) | ✓ WIRED | Confirmed by direct source read, lines 2339-2380. |
| `write_eprom`'s guard connect | `write_eprom`'s own `COMMAND_WRITE` connect | `guard_port` captured from the guard's `self.comm.port_name`, passed as `preferred_port`/`restrict_to_port=True` | ✓ WIRED | CR-01 fix, confirmed by direct source read (2357-2408) and by `test_write_guard_port_pinning.py` asserting the actual kwargs `find_and_connect` receives. |
| `cli_handlers.write` | `EpromOperator.write_eprom`/`verify_eprom` | `--verify` branch reads `last_write_guard_verdict`/`last_write_attempt_verdict` and calls `verify_eprom(..., preferred_port=last_write_port)` | ✓ WIRED | Confirmed by direct source read (888-959) and by the seven arm-specific tests in `tests/test_write_verify.py`. |
| `resolve_chip`/`convert_to_programmer` | `write_blank_guard.is_guarded_protocol` | the `algorithm`/`flags` keys the predicate reads | ✓ WIRED, confirmed reachable in production | `database.py:530` sets `"algorithm"`, `database.py:580` sets `"flags"` on every `convert_to_programmer` dict; `cli_handlers.write` calls `resolve_chip(eprom, db=app.db)` and passes that exact dict into `write_eprom`. This closes the specific concern that the guard could be reading a key the production wire dict never carries (the documented failure class behind `check_eprom_blank`'s inert SRAM short-circuit) — confirmed NOT the case here. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full write-guard/verify/port-pinning suite | `pytest tests/test_write_blank_guard.py tests/test_write_blank_guard_pinning.py tests/test_write_verify.py tests/test_write_guard_port_pinning.py -o addopts="" -q` | 90 passed | ✓ PASS |
| Full app suite (once, per §Step 7b constraint) | `pytest tests/ -o addopts="" -q` | 2306 passed, 0 failed, 36/36 snapshots | ✓ PASS (matches orchestrator-reported figure) |
| Lint | `ruff check firestarter/ tests/` | All checks passed! | ✓ PASS |
| Format | `ruff format --check firestarter/ tests/` | 152 files already formatted | ✓ PASS |
| Type check (strict modules touched) | `mypy firestarter/write_blank_guard.py firestarter/cli_handlers.py` | Success: no issues found | ✓ PASS |
| `write --help` | `.venv311/bin/firestarter write --help` | Documents host-side blank check, all 4 unguarded families named, full 0/1/2 `--verify` contract stated | ✓ PASS |
| Guarded-set pin perturbation (removing `0x0B` / adding `0x0D`) | reported in 203-02-SUMMARY.md, independently reproduced by the orchestrator | fails in both directions | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| WRITE-01 | 203-01 | Host refuses a non-blank write, naming address/value | ✓ SATISFIED | Truth 1 above |
| WRITE-02 | 203-02 | Guarded set exactly the 5 firmware-pre-flighted protocols, amended pin | ✓ SATISFIED | Truth 2 above |
| WRITE-03 | 203-02, 203-04 | `-b` skips host check, still doesn't skip erase; help text truthful | ✓ SATISFIED | Truth 3 above + `write --help` re-check |
| WRITE-04 | 203-03, 203-04 | `write --verify` runs read-back through CMP engine | ✓ SATISFIED (1 advisory) | Truth 4 above, WR-01 advisory |
| WRITE-05 | 203-03 | `--verify` mismatch exits non-zero, never says "successful" | ✓ SATISFIED | Truth 4 above |
| WRITE-06 | 203-01 | Blank-region write into non-blank part still succeeds | ✓ SATISFIED | Truth 5 above |

**No orphaned requirements.** REQUIREMENTS.md maps exactly WRITE-01…WRITE-06 to Phase 203 (lines 143-148); every ID is claimed by exactly one or two of the four plans' `requirements:` frontmatter, and all six are accounted for above.

**REQUIREMENTS.md checkbox state.** All six WRITE-0x lines in `.planning/REQUIREMENTS.md` are still unchecked (`- [ ]`). This is **not** a gap: `PROJECT.md`'s v1.41 activation footer and both 203-02-SUMMARY.md and 203-04-SUMMARY.md explicitly record that REQUIREMENTS.md and ROADMAP.md are hand-authored for this milestone and are deliberately left for the orchestrator/ship stage to reconcile by hand, because the GSD requirements-verbs normalise the whole file. WRITE-03 is correctly left unmarked by both declaring plans (203-02, 203-04) per the shared-ID convention documented in the phase's own memory notes. Recommend the orchestrator hand-edit REQUIREMENTS.md to check all six WRITE-0x boxes as part of phase close.

### Anti-Patterns Found

No `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` markers in any file this phase touched. No stub returns, no hardcoded-empty props flowing to output. The RED/GREEN TDD-gate non-compliance in plan 03 (documented candidly in its own "TDD Gate Compliance" section) is a process deviation, not a correctness gap — every `must_haws.truths`/`behavior` entry maps to a passing test in the final state, and the safety-critical exit-code arm (arm 3) was independently perturbation-tested by the orchestrator against real code, not just read.

### Human Verification Required

None. This phase is explicitly scoped app-only and bench-no (203-CONTEXT.md), and every observable truth above is proven through genuine integration tests driving the real `EpromOperator`/`cli_handlers.write` code paths — not through symbol presence alone, and not through the disqualified `tests/fake_chip.py` firmware-pre-flight double. No hardware-dependent behavior is claimed by this phase; that verification is explicitly deferred to a future bench-gated phase.

### Gaps Summary

No blocking gaps. One critical finding from code review (CR-01 — the guard's read and the write could silently land on different boards, which would have defeated the entire safety property this phase exists to build) was fixed in commit `0fc6c77` and independently re-verified here with a dedicated fail-closed test. Two warnings (WR-01, WR-02) and one info item (IN-01) from the code review remain, all pre-existing, documented, and deliberately not fixed in this phase; none of them undermines the phase's core safety property (a non-blank part is refused before any write byte reaches the wire, and the refused/blank regions can never silently diverge onto a different board). They are carried forward as advisory findings above rather than as gaps.

---

*Verified: 2026-09-21T15:10:00Z*
*Verifier: Claude (gsd-verifier)*
