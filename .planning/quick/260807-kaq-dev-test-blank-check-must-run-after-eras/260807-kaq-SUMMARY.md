---
status: complete
phase: 260807-kaq
plan: 01
subsystem: firestarter_app
tags: [dev-test, chip_test, blank-check, erase, sdp-leg]
dependency-graph:
  requires: []
  provides:
    - "derive_plan: conditional blank-check placement (after erase / NA-by-family-fact / unchanged)"
  affects:
    - "firestarter/chip_test.py::derive_plan"
    - "count_applicable's M/N for protocol-0x0D chips (AT28C256, AT28C16, and 84 other 0x0D/0x05 chips)"
tech-stack:
  added: []
  patterns:
    - "single erase_is_executable boolean shared read-only between the erase arm and the blank-check placement decision"
key-files:
  created:
    - firestarter_app/tests/test_chip_test_blank_check_order.py
  modified:
    - firestarter_app/firestarter/chip_test.py
    - firestarter_app/tests/test_dev_test_cmd.py
    - firestarter_app/tests/test_chip_test.py
    - firestarter_app/tests/test_chip_test_sdp_leg.py
decisions:
  - "Narrow _AUTO_ERASE_ON_WRITE_PROTOCOLS = {0x05, 0x0D} predicate confirmed strictly safer than the broader 'non-UV, no erase step' predicate with zero measured cost (bucket D, the only place they could differ, is 100% SRAM/FRAM already routed to NA by an earlier, separate branch)"
metrics:
  duration: "~2.5 hours"
  completed: 2026-08-07
---

# Phase 260807-kaq Plan 01: dev test blank-check must run after erase Summary

`derive_plan`'s blank-check step now runs after the erase step (when one is executable), or is emitted NA for the two protocols whose write path auto-erases per page — so a `dev test` run on an erasable chip that merely holds data no longer scores a false BAD verdict and exit 1.

## What was built

**Task 1 (measurement, no commit):** wrote a throwaway script (`/tmp/.../scratchpad/kaq_buckets.py`, not committed) that partitioned the live 746-chip DB into the plan's four buckets and confirmed the verdict-path citations by reading the source.

**Task 2 (RED-first, TDD):** wrote `tests/test_chip_test_blank_check_order.py` (5 unit tests, 144 lines) and a new `TestBlankCheckAfterEraseKaq` class in `tests/test_dev_test_cmd.py` (2 end-to-end CliRunner tests). Observed both RED against the unmodified `chip_test.py`, then implemented the conditional placement rule in `derive_plan` via a single shared `erase_is_executable` boolean.

**Task 3 (reconciliation + gates):** ran the full suite, found and reconciled 4 moved assertions (3 predicted by the plan's category, 1 not named verbatim but a measured consequence — AT28C16), then committed with both ruff gates green.

## Task 1 — measured ground truth

Ran against the live DB (`EpromDatabase(skip_local_override=True)`, 746 chips):

| Bucket | Definition | Count |
|---|---|---|
| A | executable erase step present (`can_erase and protocol != 0x05`) | 258 |
| B | `is_uv` true | 301 |
| C | not A, not B, `protocol in {0x05, 0x0D}` (case 3 NA candidates) | 111 |
| D | residual (plan's literal A/B/C exclusion) | 76 |

Sum: 258+301+111+76 = 746 ✓ (asserted in-script).

Bucket C's distinct `(electrical-type, protocol, can_erase)` tuples:
- `EEPROM`, `0x0D`, `can_erase=False` — 66 chips (e.g. AM28C16A, AM28C17A, AM28C64A/AM28C64AE/AM28C64B/AM28C64BE, AT28BV64/AT28LV64)
- `Flash/EEPROM`, `0x0D`, `can_erase=False` — 18 chips (e.g. AT28C010/AT28C010E, AT28C040/AT28C040E, AT28LV010, AT28MC010, AT28MC020)
- `Flash/EEPROM`, `0x05`, `can_erase=False` — 27 chips (e.g. AE29F1008, AE29F2008, AE29F4008, AT29BV010A/AT29LV010A, AT29BV020/AT29LV020)

Bucket D's distinct tuples — **finding, refined from the plan's literal spec**: all 76 chips are `SRAM`/`FRAM` (1 FRAM protocol 0x28, 20 SRAM protocol 0x0E, 2 SRAM protocol 0x27, 33 SRAM protocol 0x28, 20 SRAM protocol 0x29). The plan's Task 1 spec computes bucket D as "not A, not B, not C" without first excluding SRAM/FRAM, so it doesn't match `derive_plan`'s real precedence order (case 1, SRAM/FRAM, fires *before* cases 2/3/4 are ever evaluated). Re-partitioning with the real precedence order applied (SRAM/FRAM excluded first) leaves **zero** residual chips reaching the real case 4 outside SRAM/FRAM. Conclusion, stated explicitly as the plan's Task 1 requires: **bucket D contains no OTP/PROM-like chip that would be swallowed differently by the narrow `{0x05,0x0D}` predicate vs. the broader "non-UV, no erase step" predicate** — the two predicates coincide, with zero measured cost, because every chip that would have differed is SRAM/FRAM and is already, separately, routed to NA by an earlier branch. This is a refinement of the plan's own prediction ("if the measurement shows the bucket is exactly {0x05, 0x0D}... the two rules coincide"), not a contradiction — recorded here rather than silently adapted, per this task's own instruction, since bucket D as literally defined by the plan's spec was non-empty (76, not 0) and required this extra step to interpret correctly.

**Verdict path confirmed by citation** (chip_test.py / cli_handlers.py line numbers matched the plan's `<measured_ground_truth>` almost exactly, off by a handful of lines due to intervening unrelated history):
- `chip_test.py:1601-1605`: `OP_BLANK_CHECK` dispatch maps `check_eprom_blank() is False` → `VERDICT_BAD`.
- `cli_handlers.py:2008-2014`: `_VERDICT_EXIT_CODES[VERDICT_BAD] = 1`.
- `cli_handlers.py:2026`: `_EXIT_CODE_PRECEDENCE = (1, 2, 0)` — BAD (1) is checked and returned first, ahead of marginal (2), confirming BAD is the **most severe** code the command can emit.
- `cli_handlers.py:2401-2403`: `dev_test`'s own docstring still says "computed as max over per-step exit codes" — confirmed stale (D-14 already corrected the mechanism to the explicit-precedence walk); out of this task's scope, not touched.

## Task 2 — RED-first proof (captured verbatim)

**Unit legs**, run against unmodified `chip_test.py`:
```
FAILED tests/test_chip_test_blank_check_order.py::test_m8720_full_blank_check_moves_after_erase_before_sdp_leg
AssertionError: blank-check (index 2) must run AFTER erase (index 5) on an erasable part
assert 2 > 5

FAILED tests/test_chip_test_blank_check_order.py::test_at28c256_blank_check_is_na_with_family_fact_reason
AssertionError: assert True is False
 +  where True = Step(op='blank-check', supported=True, reason='', destructive=False, write_region=None).supported
```
3 passed (write_scope="none" unchanged, UV unchanged, non-vacuity) — expected, since those legs assert behavior this fix does not touch.

**End-to-end legs**, run against unmodified `chip_test.py`:
```
FAILED tests/test_dev_test_cmd.py::TestBlankCheckAfterEraseKaq::test_erasable_chip_blank_only_after_erase_exits_0
AssertionError: dev test ALWAYS WRITES to the chip ...
  step: blank-check    BAD  (blank-check ran BEFORE erase; the honest-simulation
                              closure `operator.erase_eprom.called` was still False)
assert 1 == 0
 +  where 1 = <Result SystemExit(1)>.exit_code

FAILED tests/test_dev_test_cmd.py::TestBlankCheckAfterEraseKaq::test_auto_erase_on_write_chip_never_calls_blank_check_and_exits_0
  step: blank-check    BAD  (blank-check was a real supported=True step for
                              AT28C256, and check_eprom_blank.return_value=False
                              dispatched and reported BAD)
assert 1 == 0
```
Both failed for exactly the predicted reason. After implementing the fix (a single `erase_is_executable` boolean shared read-only between the erase arm and the blank-check placement decision), all 7 new tests went green — see commit `40af2ce` (RED tests) and `8180a0b` (implementation).

**Test-authoring correction found during GREEN (not a chip_test.py bug):** the first draft of the AT28C256 end-to-end test used `make_clean_operator()`, whose `check_eprom_blank` override worked correctly, but whose `write_eprom`/`read_eprom` are not read-back-capable — the SDP leg's baseline steps (unrelated to blank-check) reported BAD against that double, confounding the exit-0 assertion. Fixed by switching to `make_leaked_lock_operator()` then `make_held_lock_operator()` (the suite's own established clean-success ALLOW-chip double, per `TestHoldStateLeg12`'s precedent) before the AT28C256 leg went green for the right reason.

## Task 3 — full-suite reconciliation

Four assertions moved. Three were exactly the plan's named prediction category (M/N delta for 0x0D/0x05 ALLOW-chip fixtures); the fourth (AT28C16) was not named verbatim by the plan but is a measured, correctly-attributed consequence of the same rule:

| Test | What moved | Reason |
|---|---|---|
| `test_chip_test.py::test_derive_plan_destructive_flag_strips_not_annotates` | M8720 `write_scope="full"` op order: `[id,read,blank-check,write,verify,erase,...]` → `[id,read,write,verify,erase,blank-check,...]` | M8720 has an executable erase step; blank-check now follows it |
| `test_chip_test.py::test_count_applicable_sdp_gated_allow_chip_ratio_drops` | AT28C256 gated-ALLOW fixture: `m_applicable` 10→9, `n_ran` 6→5 | blank-check is now NA (protocol 0x0D, case 3) — removed from both M and N |
| `test_chip_test.py::test_count_applicable_sdp_banner_row_renders_the_dropped_ratio` | Same fixture, same M/N delta (10/6 → 9/5) | same |
| `test_chip_test_sdp_leg.py::test_baseline_gate_closes_dead_write_path_allow_chip_full_leg` | Same fixture (dead-write-path double), same M/N delta (10/6 → 9/5) | same |
| `test_dev_test_cmd.py::test_dev_test_present_but_unsupported_still_sweeps` | AT28C16 (protocol 0x0D, also not on this session's known list) blank-check verdict `SKIPPED`/adapter-reason → `NA`/family-fact-reason | blank-check is `supported=False` by construction for 0x0D chips, so `run_plan` never reaches `resolve_chip`'s adapter refusal for that step; the test's "guard doesn't swallow it" proof was re-pointed at the `write` step, which does still reach the refusal |

**M/N delta, recorded explicitly (not absorbed silently):** for every measured 0x0D/0x05 chip whose plan carries the SDP leg (AT28C256 being the only one exercised end-to-end here), `count_applicable`'s `m_applicable` drops by exactly 1 (blank-check leaves the applicable set) and `n_ran` drops by 1 in any fixture where blank-check previously ran and reported OK/BAD.

**Predicted-and-confirmed unchanged** (the plan named these explicitly as "predicted to stay green"): `test_chip_test.py:666` (`nd_ops == [OP_ID, OP_READ, OP_BLANK_CHECK]`, write_scope="none"), `test_chip_test.py:674-675` (verify-before-erase), `test_chip_test_sdp_leg.py:2103` (write_scope="none" op list) — all three at exactly the line numbers the plan's `<measured_ground_truth>` cited, all three still green, unmodified.

**Full-suite pass count:** 1532 passed before this task's own changes (measured by subtracting the 7 net-new tests from the final count, confirmed via `git diff` showing zero test-function deletions/renames across all four modified files) → **1539 passed** after. Both ruff gates (`ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`) exit 0.

**Honest limit:** this fix is verified only against mocked operators (`Mock(spec=EpromOperator)`) — no silicon was exercised. The erase-then-blank-check sequence (erase pulses, then a real blank-check read) is unproven on real hardware and is the natural next bench check.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in my own test draft, not chip_test.py] AT28C256 end-to-end test used the wrong operator double**
- **Found during:** Task 2 GREEN
- **Issue:** first draft used `make_clean_operator()`, which is not read-back-capable — the SDP leg's baseline steps reported BAD, confounding the exit-0 assertion with an unrelated failure
- **Fix:** switched to `make_held_lock_operator()`, this suite's established clean-success ALLOW-chip double
- **Files modified:** `tests/test_dev_test_cmd.py`
- **Commit:** `40af2ce`

**2. [Rule 1/refinement - measurement] Bucket D's literal partition doesn't match derive_plan's real precedence order**
- **Found during:** Task 1
- **Issue:** the plan's four-bucket spec computes bucket D as "not A, not B, not C" without excluding SRAM/FRAM first, so it doesn't mirror `derive_plan`'s actual case-1-fires-first order; a literal reading makes bucket D non-empty (76) when the real question ("does any OTP/PROM-like chip reach case 4 for real") has answer zero
- **Fix:** added a second measurement pass excluding SRAM/FRAM chips (matching the real precedence order), confirming bucket D's true residual (chips that would actually reach case 4 outside SRAM/FRAM) is empty
- **Files modified:** none (measurement script only, not committed)

**3. [Rule 3 - reconciliation, predicted by the plan's own Task 3 text] AT28C16 test assertion**
- **Found during:** Task 3
- **Issue:** `test_dev_test_present_but_unsupported_still_sweeps` asserted blank-check's SKIPPED/adapter-reason verdict, which no longer occurs once blank-check is NA-by-construction for 0x0D chips
- **Fix:** updated the assertion to NA/family-fact-reason and re-pointed the "guard doesn't swallow it" proof at the `write` step
- **Files modified:** `tests/test_dev_test_cmd.py`
- **Commit:** `7fe8dea`

Both other deviations (Task 3's three predicted M/N-delta reconciliations) are documented in the table above and were explicitly anticipated by the plan's own text, not surprises.

## Known Stubs

None — this task changes an existing decision function's behavior; no new UI/rendering surface, no placeholder data.

## Threat Flags

None. This task's own `<threat_model>` (T-kaq-01..04, T-kaq-SC) was fully discharged: `erase_is_executable` is the single boolean feeding both arms (T-kaq-01); UV-EPROM plans are unchanged and proven so (T-kaq-02); the NA reason names only a public protocol fact (T-kaq-03, accept); the M delta is measured and recorded, never absorbed silently (T-kaq-04); zero package installs occurred (T-kaq-SC). No new network endpoint, auth path, file access pattern, or schema change was introduced.

## Commits (inside `/workspaces/firestarter_app`, branch `fix/dev-test-blank-check-after-erase`)

- `40af2ce` — `test(260807-kaq): add failing RED tests for blank-check-after-erase ordering`
- `8180a0b` — `feat(260807-kaq): run blank-check after erase instead of before it`
- `7fe8dea` — `test(260807-kaq): reconcile expectations moved by blank-check-after-erase`

Confirmed via `git -C /workspaces status --short`: no submodule gitlink staged in the meta repo (only the meta repo's own pre-existing, unrelated working-tree state is present).

## TDD Gate Compliance

RED gate: `40af2ce` (`test(...)`). GREEN gate: `8180a0b` (`feat(...)`). Both present, in order, in `git log`. No REFACTOR-only commit was needed (the reconciliation commit `7fe8dea` is a distinct, plan-mandated Task 3 step, not a refactor of the GREEN commit).

## Self-Check: PASSED

Files:
- FOUND: `/workspaces/firestarter_app/tests/test_chip_test_blank_check_order.py`
- FOUND: `/workspaces/firestarter_app/firestarter/chip_test.py` (modified)
- FOUND: `/workspaces/firestarter_app/tests/test_dev_test_cmd.py` (modified)
- FOUND: `/workspaces/firestarter_app/tests/test_chip_test.py` (modified)
- FOUND: `/workspaces/firestarter_app/tests/test_chip_test_sdp_leg.py` (modified)

Commits:
- FOUND: `40af2ce`
- FOUND: `8180a0b`
- FOUND: `7fe8dea`

Gates (re-confirmed at self-check time): full suite 1539 passed; `ruff check firestarter/ tests/` → all checks passed; `ruff format --check firestarter/ tests/` → 129 files already formatted.
