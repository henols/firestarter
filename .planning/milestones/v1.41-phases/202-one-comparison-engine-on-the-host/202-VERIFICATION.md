---
phase: 202-one-comparison-engine-on-the-host
verified: 2026-09-20T21:45:00Z
status: passed
score: 8/8 must-haves verified (5 roadmap success criteria + 8 requirement IDs, no gaps)
covered_files: [".planning/REQUIREMENTS.md", ".planning/ROADMAP.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-01-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-01-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-02-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-02-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-03-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-03-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-04-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-04-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-05-PLAN.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-05-SUMMARY.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-CONTEXT.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-READ-ABORT-ANSWER.md", ".planning/phases/202-one-comparison-engine-on-the-host/202-REVIEW.md", "firestarter_app/firestarter/chip_test.py", "firestarter_app/firestarter/cli_handlers.py", "firestarter_app/firestarter/compare.py", "firestarter_app/firestarter/eprom_operations.py", "firestarter_app/pyproject.toml", "firestarter_app/tests/test_chip_test.py", "firestarter_app/tests/test_cli_handlers.py", "firestarter_app/tests/test_compare.py", "firestarter_app/tests/test_eprom_operations.py"]
covered_digest: "v1:sha256:9a1ea102cfec51f2f2140a1aac892e1947fa081f3cb4ea14edaa93bc8f3708b6"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 202: One comparison engine, on the host — Verification Report

**Phase Goal:** `firestarter verify` and `firestarter blank` compare by reading the chip and comparing on the host, through one streamed implementation that names why a compare failed instead of reporting a single address.
**Verified:** 2026-09-20T21:45:00Z
**Status:** passed
**Re-verification:** No — initial verification (a `202-VERIFICATION.md` was already present, untracked, before this run; it was not trusted and this report is the product of an independent re-derivation against the live `firestarter_app` submodule at commit `a0855b9`, not a copy of it)

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `verify`/`blank` complete correctly against firmware that still carries `CMD_VERIFY`(6)/`CMD_BLANK_CHECK`(4), never sending either | ✓ VERIFIED | `constants.py:52,54` still define `COMMAND_BLANK_CHECK=4`/`COMMAND_VERIFY=6`, unremoved. I ran `TestOrdinalsNeverSentByVerifyOrBlank::test_no_run_composes_either_retired_ordinal` myself (1 passed) — it drives all four cases (clean/mismatch verify, clean/non-blank blank) through a fake serial port and asserts no captured `command_dict.cmd` is 4 or 6 across any of them. `verify_eprom`/`check_eprom_blank`/`_drive_region_compare` all pass `COMMAND_READ` to `_operation_context` (source-read confirmed). |
| 2 | Mismatch found on a 512 KB part, peak host memory bounded independently of device size | ✓ VERIFIED | `TestCompareAccumulatorPeakAllocation` traces all four fault patterns at 128 KiB (a disclosed, justified deviation from the literal 512 KiB wording — 512 KiB tracing pushed `tracemalloc` overhead past the file's own 10s-per-test budget) plus a direct 128 KiB→512 KiB flatness assertion on the cheap single-byte pattern (`peak_512k <= peak_128k * 2`). I re-ran `tests/test_compare.py` in full (70 passed) and judge the composition — bounded-ceiling proof at 128 KiB + directly measured non-growth to 512 KiB — satisfies "bounded independently of device size" as written; the orchestrator's independent 512 KiB four-pattern measurement (776 B–17,597 B, all «1 MiB) corroborates. |
| 3 | Default run names first mismatching range `start–end` + byte count, no byte values; `--full` names every span | ✓ VERIFIED | `compare.py:504-541` `render_compare_lines` emits only `Mismatch 0x{start:06X}-0x{end:06X} ({count} bytes)` lines, a D-16 tail line, and a D-14 bucket line — no expected/actual byte anywhere in the function body (source-read confirmed). Default retention is `max_ranges=1` (`_drive_region_compare`), `--full` is `MAX_RETAINED_RANGES=64`. `TestRenderCompareLines` (7 tests, including `test_no_expected_or_actual_value_ever_printed`) passes. |
| 4 | Failed compare carries a `classify_fingerprint` bucket with total/bad counts, from streamed accumulation | ✓ VERIFIED | `chip_test.classify_fingerprint` (chip_test.py:146-177) delegates to a single `CompareAccumulator.feed()`/`compare.classify_streamed()` call — no offset list materialised. `_diff_offsets` no longer exists in `chip_test.py` (grep confirms only a retirement comment remains). `TestClassifyFingerprintCorpus` compares the streamed path against an **independently hand-transcribed** batch reference (not a self-comparison — verified by reading the reference implementation) over 12 corpus rows spanning all 5 buckets; I re-ran it (part of the 70-test `test_compare.py` run) — passes. |
| 5 | Read-abort question answered in writing, not assumed | ✓ VERIFIED | `202-READ-ABORT-ANSWER.md` (135 lines) gives an affirmative, mechanism-level answer (D-06 through D-09) grounded in cited firmware source. This is also a **behavior-dependent claim** (a state transition: the host stops acking, the port stays clean, a second operation on the same operator succeeds), and it is not merely asserted — `TestVerifyEpromReadAbort::test_default_abort_stops_acking_after_the_mismatching_chunk` proves the abort by ack-count (exactly 3 "OK" writes, not 4) and chunk-callback count (exactly 2 calls), then drives a **second, independent operation on the same operator** to prove the port was left clean. I ran the whole `TestVerifyEpromReadAbort` class myself (10 passed), including three negative controls for the D-08 discrimination (non-timeout error, `--full` path with no abort requested, timeout outside the acceptance window). This clears the behavior-dependent bar in Step 3 — VERIFIED, not merely present-and-wired. |

### Requirement-Level Truths (CMP-01 through CMP-08)

| # | Req | Status | Evidence |
|---|-----|--------|----------|
| 6 | CMP-01 — `verify` reads, compares on host, no `CMD_VERIFY` on wire | ✓ VERIFIED | See #1; `REQUIREMENTS.md:54` marked `[x]` Complete, `:135` table row Complete |
| 7 | CMP-02 — `blank` compares against constant `0xFF`, no `CMD_BLANK_CHECK` on wire | ✓ VERIFIED | `_blank_expected_bytes` (eprom_operations.py:332) returns `b"\xff" * length`, never device-sized; `check_eprom_blank` composes `COMMAND_READ` (source-read); same wire-level test as #1 covers `blank` too. `REQUIREMENTS.md:55,136` Complete |
| 8 | CMP-03 — chunked compare, peak memory bounded independently of device size | ✓ VERIFIED | See #2; also `TestCompareAccumulatorRuntime`/`TestCompareAccumulatorFastPathStructure` guard the T-202-05 runtime trap (an AST-based test pins the equality-fast-path-before-per-offset-loop shape, per the review's own confirmation it traced this by hand). `REQUIREMENTS.md:56,137` Complete |
| 9 | CMP-04 — default stops at first mismatch, one `start–end` range + byte count, no byte values (amended D-13) | ✓ VERIFIED | `_drive_region_compare`'s default path passes `accumulator.has_mismatch` as the abort predicate (source-read); `render_compare_lines` output format confirmed in #3; zero-length/empty-region edge explicitly guarded (`result.total > 0` check, with its own passing test `test_incomplete_compare_never_reports_a_match`, re-run by me). `REQUIREMENTS.md:57,138` Complete |
| 10 | CMP-05 — `--full` reports every mismatching span as coalesced `start–end` + byte count | ✓ VERIFIED | `max_ranges = MAX_RETAINED_RANGES if full else 1` (`_drive_region_compare`); coalescing/adjacency/ordering covered by `TestCompareAccumulatorAdjacencyAndOverlap`, `TestCompareAccumulatorOrdering` (all passing in my `test_compare.py` run). `REQUIREMENTS.md:58,139` Complete |
| 11 | CMP-06 — failed compare classified via `classify_fingerprint`, streamed, honest buckets | ✓ VERIFIED | See #4. `REQUIREMENTS.md:59,140` Complete |
| 12 | CMP-07 — 0/1 match/mismatch exit codes, transport/hardware failure distinguishable | ✓ VERIFIED | D-10 exit codes (0/1/2) implemented uniformly in `_drive_region_compare`'s `is_ok`/`aborted` logic and both CLI docstrings; `dev test`'s `== 0` adapter at the multi-run dispatch site keeps its own bool semantics stable (source-read, `chip_test.py`). `REQUIREMENTS.md:60,141` Complete |
| 13 | CMP-08 — both accept `--address`/`--size`, region-scoped compare reads only that region | ✓ VERIFIED | `cli_handlers.verify`/`blank` both carry `-a/--address` and `-s/--size` options (source-read, cli_handlers.py:909-923, 970-986); D-17 region resolution and its two pre-wire refusals live in `_region_refusal_exit_code`, shared by both commands. `REQUIREMENTS.md:61,142` Complete |

### Code-Review Follow-Up (CR-01, re-verified live)

CR-01 (the review's sole Critical finding: `blank -a <past-chip-end>` without `--size` was not refused) is fixed. I drove the exact repro from `202-REVIEW.md` directly against the live tree:

```
_region_refusal_exit_code(eprom="X", eprom_data={"memory-size": 0x4000}, address="0x8000", size=None)
→ "X: refused -- the start address 0x8000 is at or past this chip's declared size (0x4000)." / returns 2
```

This matches the documented fix (an unconditional `start >= mem_size` guard ahead of length resolution). The paired boundary test (`test_address_alone_exactly_at_chip_end_is_refused`) and its negative control (`test_blank_address_alone_at_last_valid_byte_is_not_refused`) both exist in `tests/test_cli_handlers.py`.

### Adversarial check: bool→int mock inversion risk

Both `verify_eprom` and `check_eprom_blank` changed return type from `bool` to `int` this phase. Since `True == 1` and `False == 0`, a stale bool-valued mock would silently invert every comparison against the new `== 0` adapter sites rather than fail loudly. I grepped the whole `tests/` tree for `verify_eprom`/`check_eprom_blank` mocks configured with a literal `True`/`False` on `return_value` or `side_effect` — **zero matches**. Every mock across `fake_chip.py`, `fixtures/report_shapes.py`, `plan_corpus.py`, and all `test_chip_test*.py` files now uses `0`/`1` (spot-checked `test_chip_test.py:1797` — `side_effect = [0, 1]`). This is corroborated by 202-01's own Deviations section, which records that this exact inversion bug was caught by a full-suite run (41 failures) during execution and fixed before commit — the failure mode this adversarial check screens for was not just theoretically avoided, it was hit and fixed once already.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/firestarter/compare.py` | The one streaming engine (541 lines) | ✓ VERIFIED | Exists, exports `MismatchRange`/`CompareResult`/`CompareAccumulator`/`MAX_RETAINED_RANGES`/`render_compare_lines`/`Fingerprint`/`FP_*`/`DiffSummary`/`diff_summary`/`classify_streamed` — all confirmed present by source read |
| `firestarter_app/tests/test_compare.py` | Engine unit tests | ✓ VERIFIED | 70 tests, all passing (re-run by me) |
| `firestarter_app/pyproject.toml` | mypy strict-island membership | ✓ VERIFIED | `firestarter.compare` present in `disallow_untyped_defs=true` list (line 176), confirmed by grep |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `eprom_operations.py` | `compare.py` | `CompareAccumulator`/`render_compare_lines` import and drive | ✓ WIRED | `verify_eprom`/`check_eprom_blank` both route through `_drive_region_compare`, which constructs and feeds the accumulator (source-read) |
| `eprom_operations.py` | `constants.py` | `COMMAND_READ` passed to `_operation_context`, not `COMMAND_VERIFY`/`COMMAND_BLANK_CHECK` | ✓ WIRED | Confirmed by source read and by the wire-level test (#1) |
| `cli_handlers.py` | `eprom_operations.py` | `sys.exit(verdict)` on the int return | ✓ WIRED | `verify`/`blank` commands both `sys.exit()` the service's int verdict directly (source-read, lines 956-965, 1014-1022) |
| `chip_test.py` | `compare.py` | `classify_fingerprint` delegates to `classify_streamed` | ✓ WIRED | Confirmed by source read; `_diff_offsets` retired |
| `cli_handlers.py` | `_region_refusal_exit_code` | Pre-wire region refusal, before `_operation_context`/serial port opens | ✓ WIRED | Both commands call the shared refusal function before invoking `EpromOperator` methods (source-read) |

### Import-Purity Invariant (D-01)

Re-ran the AST check myself (not trusting the plan's own `<verify>` block): `compare.py`'s whole-tree import set is exactly `{__future__, dataclasses}` (plus the `annotations`/`dataclass`/`field` names those pull in) — no `click`, `eprom_operations`, `chip_test`, or `serial_comm` anywhere, including no function-local imports. Matches the orchestrator's independent measurement.

### Behavioral Spot-Checks (run by this verifier)

| Behavior | Command | Result | Status |
|---|---|---|---|
| Wire-ordinal proof (criterion 1) | `pytest tests/test_eprom_operations.py::TestOrdinalsNeverSentByVerifyOrBlank -q` | 1 passed | ✓ PASS |
| Abort mechanism + D-08 discrimination + port-clean-after-abort (criterion 5) | `pytest tests/test_eprom_operations.py::TestVerifyEpromReadAbort -q` | 10 passed | ✓ PASS |
| Streaming engine full suite | `pytest tests/test_compare.py -q` | 70 passed | ✓ PASS |
| `dev test`/`chip_test`/CLI regression | `pytest tests/test_chip_test.py tests/test_dev_test_cmd.py tests/test_cli_handlers.py -q` | 318 passed | ✓ PASS |
| mypy on the three named modules | `mypy firestarter/compare.py firestarter/cli_handlers.py firestarter/main.py` | "Success: no issues found in 3 source files" | ✓ PASS |
| ruff | `ruff check firestarter/ tests/` + `ruff format --check` | clean | ✓ PASS |
| CR-01 live repro | direct call to `_region_refusal_exit_code` | returns 2, refused | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| CMP-01 | 202-01, 202-05 | ✓ SATISFIED | See #6 |
| CMP-02 | 202-05 | ✓ SATISFIED | See #7 |
| CMP-03 | 202-02 | ✓ SATISFIED | See #8 |
| CMP-04 | 202-04 | ✓ SATISFIED | See #9 |
| CMP-05 | 202-01, 202-02 | ✓ SATISFIED | See #10 |
| CMP-06 | 202-03 | ✓ SATISFIED | See #11 |
| CMP-07 | 202-01, 202-05 | ✓ SATISFIED | See #12 |
| CMP-08 | 202-05 | ✓ SATISFIED | See #13 |

No orphaned requirements: `REQUIREMENTS.md`'s Phase 202 rows (CMP-01..08) all appear in at least one plan's `requirements:` frontmatter field, and the union across the five plans covers exactly this set with no leftover.

### Anti-Patterns Found

None blocking. Scanned `compare.py`, `eprom_operations.py`, `cli_handlers.py`, `chip_test.py` for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`/empty-return stubs — none found in the phase's changed regions. The one dead-code finding (IN-01, an unreachable `if not offs:` guard in `CompareAccumulator.feed()`) is Info-severity, explicitly reasoned as deliberate defensive redundancy in the review, and does not affect behavior — not a blocker.

### Open Items Carried Forward (not blocking this phase's goal)

- **WR-01** — `READ_ABORT_ACCEPTANCE_WINDOW_S` is a fixed 3.0 s reasoned from firmware timing alone; host-side scheduling/USB jitter is not bounded by that reasoning, and the boundary itself (an abort landing just inside vs. just outside the window under injected delay) is untested. Under sustained host load this could misreport a deliberate abort as exit 2. This is a real, currently-untested edge in a phase whose own stated goal is to make abort-vs-fault discrimination trustworthy — worth a human decision on whether to accept the risk as documented or harden it before the milestone closes further phases that build on this seam (203/206). Not a phase-202 goal blocker: criterion 5 asks the question be answered in writing, not that every timing edge be closed, and three of the four discrimination conditions do have negative tests.
- **WR-02** — `chip_test._dispatch_step`'s `OP_BLANK_CHECK` arm folds `check_eprom_blank`'s new refusal verdict (2, which can now include a genuine transport failure, not just the proven-unreachable SRAM/FRAM case) into `VERDICT_BAD`. The code's own comment defers the real fix to phase 206. Confirmed present in code exactly as described, not a regression — a hardware fault can still surface as a chip finding in `dev test` until then.
- **IN-01** — dead `if not offs:` branch in `feed()`. Harmless, documented.
- **CMP-F2 / dead `transport` bucket** — `classify_streamed`'s transport path requires `repeat_divergent is True`, and the only production call site never sets it; confirmed dead-but-covered-by-direct-construction in the corpus. Deliberately deferred, not a phase-202 defect.
- **202-01 SUMMARY `requirements-completed` overlap** — 202-01 and 202-05 both list CMP-01/CMP-07 in `requirements-completed`. Checked against `REQUIREMENTS.md`: both requirements legitimately span both plans (202-01 does `verify`, 202-05 does `blank` + the exit-code consolidation), and REQUIREMENTS.md correctly held them Pending until 202-05 landed — all 8 are Complete now, verified on disk, not merely claimed.

None of these five items block the phase goal as stated. WR-01 and WR-02 are the closest to a genuine open risk and are surfaced above for a human call rather than silently accepted — hence `human_needed` is NOT selected, because neither is a truth this phase's success criteria assert (the roadmap does not require the abort window to be jitter-proof, only that the question be "answered in writing," which it is); they are reported as residual risk for the operator's awareness heading into phases 203/206, not as unresolved verification items.

## Gaps Summary

None. All 5 roadmap success criteria and all 8 requirement IDs (CMP-01 through CMP-08) are verified against the live code and test suite, not merely against SUMMARY.md claims — every claim in this report was either read directly from source or re-run by this verifier. The one Critical code-review finding (CR-01) is confirmed fixed with a live repro. Two Warnings (WR-01, WR-02) and one Info (IN-01) remain, all explicitly scoped as deferred or accepted risk in the phase's own review, not as this phase's unmet goal.

---

*Verified: 2026-09-20T21:45:00Z*
*Verifier: Claude (gsd-verifier)*
