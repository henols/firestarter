---
phase: 205-the-pre-flights-leave-the-firmware
verified: 2026-09-22T22:10:00Z
status: passed
score: 9/9 must-haves verified
covered_files:
  - .planning/REQUIREMENTS.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-01-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-01-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-02-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-02-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-03-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-03-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-04-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-04-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-05-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-05-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-06-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-06-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-07-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-07-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-08-PLAN.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-08-SUMMARY.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-BENCH-MATRIX.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-CONTEXT.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-CR-01-DECISION.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-FLASH-RAM.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-REVIEW.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/205-SESSION-COST.md
  - .planning/phases/205-the-pre-flights-leave-the-firmware/deferred-items.md
  - firestarter_app/firestarter/chip_test.py
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/serial_comm.py
  - firestarter_app/firestarter/write_blank_guard.py
  - firestarter_app/tests/test_write_blank_guard.py
  - firestarter_app/tests/test_write_blank_guard_pinning.py
  - firestarter_fw/CLAUDE.md
  - firestarter_fw/include/firestarter.h
  - firestarter_fw/include/memory_utils.h
  - firestarter_fw/src/firestarter.cpp
  - firestarter_fw/src/json_parser.c
  - firestarter_fw/src/proms/eeprom_28c.cpp
  - firestarter_fw/src/proms/eprom.cpp
  - firestarter_fw/src/proms/flash_5v_page.cpp
  - firestarter_fw/src/proms/flash_intel.cpp
  - firestarter_fw/src/proms/flash_nor_unlock.cpp
  - firestarter_fw/src/proms/memory.cpp
  - tools/catalog/messages.toml
covered_digest: "v1:sha256:d42f4aa882e7b428668cb702927b2306f1adfd3b0c5a667a3e9c0935a5f60128"
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 8/9
  gaps_closed:
    - "The host-side write guard fully owns the safety property the removed firmware write-init blank check used to provide, for every protocol family the guard claims to cover (truth 9 / CR-01)."
  gaps_remaining: []
  regressions: []
advisory:
  - finding: "firestarter_fw/CLAUDE.md states the tests/ tree was 'measured at 320 collected tests on 2026-09-22', written by commit a4e002f2 (plan 205-02, 15:26:45Z that day). The phase's own later commits changed that count twice more the same day: 9061dd1 (plan 205-04, 17:00:40Z) states in its own commit message 'pytest tests/ (315/315)', and the tree now collects 316 (confirmed live in this verification). The documented '320' figure appears to have been already stale by the time plan 205-04 landed, and no later commit updated the CLAUDE.md prose to match."
    category: other
    reason: "Cosmetic documentation drift in a repo-guidance file, not a functional defect. It does not touch any of the 9 must-have truths: none of them assert a tests/ collection count. FWBLANK-05 (the measured-flash/RAM requirement) is unaffected — its own record (205-FLASH-RAM.md) is a build-size measurement, not a test count, and was independently re-verified as correct. Recorded per the verification brief's explicit instruction to adjudicate this discrepancy; not elevated to a gap because it carries no safety or requirement consequence."
    evidence_status: "confirmed stale by live re-collection (316) and by 9061dd1's own commit message (315 at that point in the phase)"
---

# Phase 205: The pre-flights leave the firmware — Verification Report

**Phase Goal:** The write-init and erase-end blank checks, their shared machinery and the
`FLAG_SKIP_BLANK_CHECK` bit leave the firmware, and the flash that frees is a measured number
rather than an estimate.
**Verified:** 2026-09-22
**Status:** passed
**Re-verification:** Yes — after gap closure (plan 205-08, closing CR-01)

## Goal Achievement

### Observable Truths

Truths 1–8 are carried forward from the initial verification (2026-09-22T20:00:00Z), each
regression-checked below rather than re-derived from scratch, since plan 205-08 touched only
`firestarter_app` (confirmed: `git -C firestarter_fw log` shows no commit after `6e11d05` (205-05),
and `git -C firestarter_fw status --porcelain` is clean — no firmware file was touched by 205-08).

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | No caller of `mem_util_blank_check` or `mem_util_blank_check_region` remains, and both functions plus `blank_check_saved_address` and `BLANK_CHECK_CHUNK_SIZE` are deleted (SC1 / FWBLANK-03). | ✓ VERIFIED (regression-checked) | Re-run: `git grep -n "mem_util_blank_check\b\|mem_util_blank_check_region\|blank_check_saved_address\|BLANK_CHECK_CHUNK_SIZE\|FLAG_SKIP_BLANK_CHECK" -- 'src/*' 'include/*' 'test/*'` in `firestarter_fw` → 0 hits, same as prior verification. Firmware untouched since 205-05. |
| 2 | `FLAG_SKIP_BLANK_CHECK` is gone from `firestarter.h` and `constants.py`, with `0x08` recorded as reserved on both sides (SC2 / FWBLANK-04). | ✓ VERIFIED (regression-checked) | Same grep census as truth 1 covers both firmware files; `constants.py` unmodified by 205-08 (not in its file list) and re-read directly still carries the reserved-gap comment. |
| 3 | A write to a non-blank UV part reaches the firmware unrefused and programs the region it was given — confirmed on silicon (SC3). | ✓ VERIFIED (carried forward, no new evidence needed) | `205-BENCH-MATRIX.md` B5, unchanged by 205-08 (protocol `0x07`, outside `NOR_UNLOCK_PROTOCOL_ID`'s scope). |
| 4 | Flash and RAM deltas are reported per AVR target as measured numbers for uno, uno328pb and leonardo (SC4 / FWBLANK-05). | ✓ VERIFIED (carried forward) | `205-FLASH-RAM.md` unchanged; 205-08 modified no firmware file, so no rebuild was required or claimed. |
| 5 | A bench regression across at least one UV part and one erasable part shows no behaviour change other than where the refusal now comes from (SC5). | ✓ VERIFIED (carried forward) | `205-BENCH-MATRIX.md` B6/B5, unaffected — the erasable leg (B6) is a `FLAG_CAN_ERASE` exemption at address 0, which 205-08's fix explicitly leaves unchanged (`205-CR-01-DECISION.md` §3 table). |
| 6 | `write -init` bodies in `eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp` no longer call a blank check, and `configure_eprom`'s `CMD_ERASE` arm assigns no `firestarter_operation_end` (FWBLANK-01/02). | ✓ VERIFIED (regression-checked) | Firmware untouched since 205-05; diff-confirmed state from initial verification still holds (git log unchanged for these files). |
| 7 | `mem_util_operation_end` survives with exactly two callers and the `region-end` wire key stays live for `CMD_WRITE` (D-7 / OQ-2). | ✓ VERIFIED (carried forward) | Firmware untouched since 205-05; unchanged. |
| 8 | `erase -b` is re-implemented host-side through `check_eprom_blank`, existing *before* the firmware sweep lands, with the 0/1/2 exit contract and `erase -s -b` refused pre-wire (Plan 01 / FWBLANK-02's host half). | ✓ VERIFIED (carried forward) | `cli_handlers.py` not in 205-08's file list; unchanged from initial verification. |
| 9 | The host-side write guard fully owns the safety property the removed firmware write-init blank check used to provide, for every protocol family the guard claims to cover. | ✓ VERIFIED | **Gap CR-01 closed by plan 205-08.** `is_erase_exempt`/`requires_blank_check` (`write_blank_guard.py`) gained a keyword-only `address: int = 0` parameter; for `NOR_UNLOCK_PROTOCOL_ID` (`0x06`) at a non-zero address the exemption is withdrawn and the write falls back to the region-scoped host blank-check read. Verified independently in this pass: (a) source read confirms the `address != 0` branch exists exactly as claimed and is threaded from `write_eprom`'s `guard_address = parse_address(address_str) or 0` through the single call site (`eprom_operations.py:2403-2408`); (b) all three cited firmware functions re-read directly — `flash_nor_unlock_erase_execute` (`flash_nor_unlock.cpp:111-119`) branches on `handle->address != 0` exactly as claimed, `flash_intel_erase_execute` (`flash_intel.cpp:105-114`) writes to hard-coded address `0` and never reads `handle->address` for scope, `eprom_internal_erase` (`eprom.cpp:558-576`) hard-codes `firestarter_set_address(handle, 0x0000)` and never reads `handle->address` either — confirming the `0x06`-only narrowing is correct and the other three guarded protocols are genuinely unaffected at any address; (c) all 7 named regression tests + the full `test_write_blank_guard*.py` suite re-run live in this verification, on the CI-pinned Python 3.11.16 venv: **69 passed**, matching the SUMMARY's claimed count exactly; (d) `ruff check` and `ruff format --check` on all 4 modified/created files: clean. |

**Score:** 9/9 truths verified.

### Deferred Items

None.

### Advisory (New Scope, Unevidenced)

| # | Finding | Category | Why Advisory |
|---|---|---|---|
| 1 | `firestarter_fw/CLAUDE.md`'s "320 collected tests" claim is stale (live count is 316; the phase's own commit `9061dd1` reported 315 at the time it landed). | other | New-scope documentation drift discovered during this verification pass, not a carried-forward gap from the previous VERIFICATION.md and not touching any must-have truth (no truth asserts a `tests/` collection count; FWBLANK-05's flash/RAM figures are independently confirmed correct). No deterministic safety or requirement consequence — reported, not blocking. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_fw/src/proms/memory.cpp` | Blank-check machinery deleted, `mem_util_operation_end` and its comment intact | ✓ VERIFIED | Unchanged since prior verification; firmware untouched by 205-08 |
| `firestarter_fw/include/memory_utils.h` | Declarations removed, `mem_util_operation_end` declaration intact | ✓ VERIFIED | Grep census clean (re-run) |
| `firestarter_fw/src/proms/eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp` | No write-init blank-check call, no `CMD_ERASE` end-op assignment | ✓ VERIFIED | Unchanged; also re-read directly for erase-scope confirmation (truth 9) |
| `firestarter_fw/include/firestarter.h` | `FLAG_SKIP_BLANK_CHECK` gone, reserved-gap comment present | ✓ VERIFIED | Grep census clean |
| `firestarter_app/firestarter/constants.py` | `FLAG_SKIP_BLANK_CHECK` gone, reserved-gap comment present | ✓ VERIFIED | Unmodified by 205-08, unchanged from prior verification |
| `firestarter_app/firestarter/write_blank_guard.py` | `-b` reaches the guard as an explicit keyword-only signal; erase exemption is safe for every guarded protocol | ✓ VERIFIED (CR-01 closed) | `NOR_UNLOCK_PROTOCOL_ID` constant added; `is_erase_exempt`/`requires_blank_check` gain address-aware narrowing for protocol `0x06`; source-read confirmed against firmware, not just docstring |
| `firestarter_app/firestarter/eprom_operations.py` | `write_eprom` resolves and threads the write's own start address into the guard call | ✓ VERIFIED | `guard_address = parse_address(address_str) or 0` (lines ~2396-2398), threaded at `requires_blank_check(..., address=guard_address)` (line ~2407) |
| `firestarter_app/tests/test_write_blank_guard.py`, `test_write_blank_guard_pinning.py` | Regression matrix pinning the address dimension, incl. a live-database census | ✓ VERIFIED | 69 tests re-run live, all pass; named tests individually re-run and pass; census test (`test_every_shipped_nor_unlock_row_resolves_erase_capable`) confirmed passing |
| `.planning/phases/.../205-CR-01-DECISION.md` | Recorded decision: fix lands in-phase, not deferred, with displaced alternative and reversibility ratings | ✓ VERIFIED | Read in full; contains the decision, the displaced D-04-shaped alternative and why it was declined, a behaviour-delta table, provenance (`1cf1b22`), and four design decisions each rated for reversibility |
| `.planning/phases/.../205-REVIEW.md` | Fresh code review of 205-08's change, independently tracing the firmware claims | ✓ VERIFIED | Read in full; 0 critical, 0 warning, 1 info (IN-01, exception-narrowing nit, non-blocking); reviewer independently traced all three firmware citations and confirmed the tautology-test check by reverting the fix and observing exactly the 5 CR-01-relevant tests go red |
| `.planning/phases/.../205-FLASH-RAM.md` | Complete FWBLANK-05 record | ✓ VERIFIED | Carried forward, unaffected by 205-08 |
| `.planning/phases/.../205-BENCH-MATRIX.md` | Executed bench matrix, criteria 3/5, D-07 skew | ✓ VERIFIED | Carried forward, unaffected by 205-08 |
| `tools/catalog/messages.toml` | `MSG_ERR_NOT_BLANK` and `DBG_FLAG_SKIP_BLANK` kept + annotated | ✓ VERIFIED (carried forward) | Not modified by 205-08; consistent with prior verification |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `erase -b` (CLI) | `check_eprom_blank` (`eprom_operations.py`) | direct call, `sys.exit(verdict)` | ✓ WIRED | Unchanged, carried forward |
| `write -b` (CLI) | `write_blank_guard.requires_blank_check` | `blank_check_requested` keyword | ✓ WIRED | Unchanged, carried forward; re-confirmed still short-circuits FIRST, ahead of the exemption test, so `-b` bypasses even at a non-zero address (`requires_blank_check` docstring + source order) |
| `write -a <addr>` on protocol `0x06` | `write_blank_guard.is_erase_exempt` → host blank-check read | address-aware predicate, `address` param threaded from `write_eprom`'s own resolved start address | ✓ WIRED (CR-01 closed) | The predicate now consults the one input that determines whether the exemption is safe. Traced end to end: `_setup_operation`'s `addr` and `write_eprom`'s `guard_address` compute from the identical `parse_address(address_str) or 0` expression against the identical input, confirmed by direct read of both call sites and independently by `205-REVIEW.md`. |
| `mem_util_operation_end` | `eprom_operations.cpp:85`, `eprom.cpp:317` | direct calls | ✓ WIRED | Unchanged, carried forward |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| CR-01 headline fix: `0x06` at non-zero address is no longer exempt | `pytest tests/test_write_blank_guard.py::test_is_erase_exempt_is_false_for_nor_unlock_at_a_non_zero_address` (CI-pinned 3.11.16 venv) | 1 passed | ✓ PASS |
| `0x06` at address 0 is still exempt (control) | `pytest tests/test_write_blank_guard.py::test_write_at_address_zero_on_an_erase_capable_nor_unlock_part_still_pays_no_guard_read` | 1 passed | ✓ PASS |
| `0x10` (Intel flash) exemption unaffected at every address | `pytest tests/test_write_blank_guard.py::test_is_erase_exempt_is_true_for_intel_flash_at_every_address` | 1 passed | ✓ PASS |
| Non-blank `0x06` region at non-zero address is refused | `pytest tests/test_write_blank_guard.py::test_write_at_a_non_zero_address_on_a_non_blank_nor_unlock_region_is_refused` | 1 passed | ✓ PASS |
| `-b`/`--no-blank-check` still bypasses at a non-zero `0x06` address | `pytest tests/test_write_blank_guard.py::test_requires_blank_check_blank_check_requested_false_still_bypasses_at_a_non_zero_nor_unlock_address` | 1 passed | ✓ PASS |
| End-to-end: a genuine `write_eprom` against a fake serial port pays the extra guard read | `pytest tests/test_write_blank_guard.py::test_write_at_a_non_zero_address_on_an_erase_capable_nor_unlock_part_pays_a_guard_read` | 1 passed | ✓ PASS |
| Live-database census: every shipped protocol-`0x06` row resolves erase-capable | `pytest tests/test_write_blank_guard_pinning.py::test_every_shipped_nor_unlock_row_resolves_erase_capable` | 1 passed | ✓ PASS |
| Full closure-relevant module suite | `pytest tests/test_write_blank_guard.py tests/test_write_blank_guard_pinning.py -o addopts=""` | 69 passed | ✓ PASS |
| Lint/format on all 4 touched files | `ruff check` + `ruff format --check` | clean, "4 files already formatted" | ✓ PASS |
| `firestarter_fw` untouched by 205-08 | `git -C firestarter_fw status --porcelain` | empty | ✓ PASS |
| `firestarter_fw/tests/` live collection count | `pytest tests/ --collect-only -q` | 316 tests collected | ✓ PASS (confirms orchestrator's pre-measured 316; CLAUDE.md's "320" is stale, see Advisory) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| FWBLANK-01 | 205-03, 205-01, 205-08 | Write-init blank check removed from `eprom.cpp`, `flash_intel.cpp`, `flash_nor_unlock.cpp`; host guard fully owns the safety property this removal depends on | ✓ SATISFIED | Removal confirmed (carried forward); CR-01 gap closed by 205-08 and independently re-verified in this pass — truth 9 is now VERIFIED, not FAILED |
| FWBLANK-02 | 205-03, 205-01 | Erase-end blank check removed from `eprom.cpp` | ✓ SATISFIED | Carried forward, unaffected by 205-08 |
| FWBLANK-03 | 205-03 | `mem_util_blank_check`, `mem_util_blank_check_region`, `blank_check_saved_address`, `BLANK_CHECK_CHUNK_SIZE` deleted, no caller remains | ✓ SATISFIED | Grep census re-run clean |
| FWBLANK-04 | 205-04 | `FLAG_SKIP_BLANK_CHECK` retired from firmware and `constants.py`, recorded as reserved on both sides | ✓ SATISFIED | Carried forward, unaffected by 205-08 |
| FWBLANK-05 | 205-02, 205-06 | Flash/RAM freed measured per AVR target, reported as a number | ✓ SATISFIED | Carried forward; unaffected by 205-08 (no firmware file touched, no rebuild required) |

**No orphaned requirements** — REQUIREMENTS.md maps exactly FWBLANK-01..05 to Phase 205, and all five appear in at least one plan's `requirements:` frontmatter field (confirmed: `205-08-SUMMARY.md`'s `requirements-completed: [FWBLANK-01]`, and the other four confirmed against 205-01/02/03/04/06's frontmatter as in the prior verification). REQUIREMENTS.md itself still shows all five as "Pending" in its status table — this verifier does not mark requirements complete; that is a separate, deliberate step per this agent's operating rules.

### Anti-Patterns Found

No debt markers (`TBD`/`FIXME`/`XXX`) or unreferenced `TODO`/`HACK`/`PLACEHOLDER` found in any of the four files 205-08 modified or created (`write_blank_guard.py`, `eprom_operations.py`, `test_write_blank_guard.py`, `test_write_blank_guard_pinning.py`) — re-scanned directly in this pass. `ruff check`/`ruff format --check` clean on all four. One out-of-scope, pre-existing condition noted in `205-08-SUMMARY.md`'s Deviations section (an untracked, unrelated datasheet PDF present in the `firestarter_app` submodule before this plan began) was checked and confirmed genuinely pre-existing and out of scope — it predates 205-08's first commit and is neither committed nor deleted by it.

**One new-scope, non-blocking finding surfaced in this re-verification pass** (documentation staleness in `firestarter_fw/CLAUDE.md`'s test-count claim) — recorded under Advisory above, per the evidence-gate rule for re-verification: a genuine finding, not a carried-forward gap, with concrete deterministic evidence (live re-collection + the phase's own commit message), but no consequence for any must-have truth, so it does not block `passed`.

### Human Verification Required

None. Every truth — including the previously-failed truth 9 — resolves to VERIFIED on code, git, and live-test evidence; no item requires subjective judgment, visual inspection, or hardware access beyond what the bench matrix already captured on silicon in the initial verification pass.

### Gaps Summary

**No gaps remain.** The phase's mechanical work (FWBLANK-01 through FWBLANK-05) was already confirmed complete and well-evidenced in the initial verification. The single blocking gap from that pass — CR-01, `write_blank_guard.is_erase_exempt`'s address-blindness silently exempting a non-zero-address protocol-`0x06` write from any blank check — is now closed by plan 205-08, and this re-verification independently confirms the closure rather than trusting the SUMMARY's claim:

- The three firmware citations underpinning the fix (`flash_nor_unlock.cpp:111-119`, `flash_intel.cpp:105-114`, `eprom.cpp:558-576`) were each re-read directly in this pass and match exactly what the code, docstrings, `205-CR-01-DECISION.md`, and `205-REVIEW.md` claim.
- The regression matrix (69 tests) was re-run live in this verification on the CI-pinned Python 3.11.16 venv and passes in full; the 7 tests most directly relevant to CR-01 were also run individually and pass.
- `ruff check`/`ruff format --check` are clean.
- `firestarter_fw` was confirmed untouched by 205-08 (`git status --porcelain` empty, no commits since `6e11d05`), so none of the 8 previously-verified truths were put at regression risk by this plan, and none show any sign of regression on re-check.
- The decision record (`205-CR-01-DECISION.md`) explicitly states why the fix landed in-phase rather than being deferred (an irreversible, silent, no-flag-required hazard on 190/190 shipped rows does not fit the "accepted-risk window" shape the phase used elsewhere for a reversible, flag-gated skew), and correctly identifies that no later phase's stated scope covers this gap.

One advisory, non-blocking finding was surfaced independently during this pass (see Advisory section): `firestarter_fw/CLAUDE.md`'s "320 collected tests" claim is stale by the phase's own later commits (currently 316, and the phase's own `205-04` commit message already recorded 315 at the point it landed). This does not affect any must-have truth or requirement and is reported, not gapped.

---

_Verified: 2026-09-22_
_Verifier: Claude (gsd-verifier)_
