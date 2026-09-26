---
phase: 182-jp5-destructive-operation-gate
verified: 2026-09-10T21:30:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - .planning/REQUIREMENTS.md
  - .planning/ROADMAP.md
  - .planning/notes/jumper-display-ground-truth.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-01-PLAN.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-01-SUMMARY.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-02-PLAN.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-02-SUMMARY.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-03-PLAN.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-03-SUMMARY.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-04-PLAN.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-04-SUMMARY.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-05-PLAN.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-05-SUMMARY.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-06-PLAN.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-06-SUMMARY.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-07-PLAN.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-07-SUMMARY.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-CONTEXT.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-DISCUSSION-LOG.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-PATTERNS.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-RESEARCH.md
  - .planning/phases/182-jp5-destructive-operation-gate/182-REVIEW.md
  - .planning/phases/182-jp5-destructive-operation-gate/deferred-items.md
  - .planning/phases/182-jp5-destructive-operation-gate/evidence/182-06-bench-readings.md
  - .planning/todos/pending/fix-jp4-labels-and-rev2-revision-block.md
  - .planning/v1.7-SHIELD-REVS.md
  - firestarter_app/firestarter/cli_handlers.py
  - firestarter_app/firestarter/constants.py
  - firestarter_app/firestarter/data/chip_database.json
  - firestarter_app/firestarter/data/pinouts.json
  - firestarter_app/firestarter/eprom_operations.py
  - firestarter_app/firestarter/exceptions.py
  - firestarter_app/firestarter/ic_layout.py
  - firestarter_app/firestarter/jp5_gate.py
  - firestarter_app/tests/golden/wire_dict_expected_deltas_182.json
  - firestarter_app/tests/test_build_db_inclusion.py
  - firestarter_app/tests/test_diff_db_gate.py
  - firestarter_app/tests/test_ic_layout.py
  - firestarter_app/tests/test_jp5_gate.py
  - firestarter_app/tests/test_revision_constants_parity.py
  - firestarter_app/tests/test_wire_dict_equivalence.py
  - firestarter_app/tools/DECODE-NOTES.md
  - firestarter_app/tools/build_db.py
  - firestarter_app/tools/diff_db.py
covered_digest: "v1:sha256:11944868878d90bf2e9c94d1d03ad9ff5d5d7170bc95da82de9e442c47cdff9e"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 182: JP5 Destructive-Operation Gate Verification Report

**Phase Goal:** An operator cannot begin an operation that would put VPP onto socket pin 1 of a
part that expects A19 there without being told, in the terminal, that JP5 must be cut — and no code
path can describe JP5 as something it is not.

**Verified:** 2026-09-10T21:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth (Roadmap SC) | Status | Evidence |
|---|---|---|---|
| 1 | An affected operation on an affected part stops before touching the bus and states the hazard; declining aborts with no operation performed | ✓ VERIFIED | `jp5_gate.require_acknowledged` raises `Pin1HazardRefusedError` *before* `with self._operation_context(...)` in both `write_eprom` (`eprom_operations.py:2003`) and `erase_eprom` (`:2147`), confirmed by line-order in source. `cli_handlers.py:753`/`873` call `confirm_or_refuse` before the operator call and `sys.exit(1)` on a false answer. Directly ran `pytest tests/test_jp5_gate.py -o addopts="" -q` myself: **40 passed**, including integration legs patching `_operation_context` to a `Mock` and asserting it was never called. |
| 2 | The affected-part set is computed from the database's pin maps — a test adds a part carrying an affected pin map and it appears in the set with no source edit | ✓ VERIFIED | `jp5_gate.py` uses `pin_conversions[32][1]` + list-index lookup, no part-number list (`git grep` for the 8 part numbers inside `jp5_gate.py` — none). Ran `pytest tests/test_jp5_gate.py -k synthetic -v` myself: `test_synthetic_pin_map_with_pin1_at_index19_appears_in_the_affected_set` and its index-18 negative sibling both **pass**, injecting a pin map through `_merge_pin_maps` under a synthetic key with zero edits to `jp5_gate.py`/`pinouts.json`. |
| 3 | A non-interactive invocation does not proceed by default on an affected part; whatever acknowledgement exists is explicit and separate | ✓ VERIFIED | `confirm_or_refuse` checks `isatty_fn()` and returns `False` **before** `confirm_fn` is ever reached (traced in source); `require_acknowledged` defaults `acknowledged: bool = False` on both operator methods, so any caller (CLI or not) that omits the kwarg is refused. `git grep -n force -- firestarter/jp5_gate.py` returns nothing — `-f/--force` is never read by the gate, confirmed by direct source read. |
| 4 | `grep -rn '_get_rev2_2_jumper_settings_data' firestarter_app/` returns nothing | ✓ VERIFIED (by intent) | The **environment-flagged caveat is real and was reproduced**: PATH `grep` (ugrep, honours `.gitignore`) returns only the 2 test-file hits; `/usr/bin/grep` (bypasses `.gitignore`) additionally surfaces 2 hits in `build/lib/firestarter/ic_layout.py` — a stale, gitignored build artifact, not source. Checked `firestarter/ic_layout.py` directly: only `_get_rev2_jumper_settings_data` (the live sibling) remains; `_get_rev2_2_jumper_settings_data` and its commented call site are gone. No production code path can reference the deleted symbol. The literal grep as worded can also never return clean because `tests/test_ic_layout.py` necessarily contains the symbol name as an assertion string — judged on intent per the task's environment notes. |
| 5 | The phase record answers the reporter's own question — which operations energize pin 1 — citing the schematic and the firmware VPP path rather than inferring it | ✓ VERIFIED | `.planning/notes/jumper-display-ground-truth.md` § "Which operations energize socket pin 1 — the answer to gh#60" names the exact firmware sites (`eprom.cpp:453/462` write pulse, `eprom.cpp:547` erase) and states `id` asserts `CTRL_VPP_A9_ENABLE` (socket pin 26, not pin 1) instead. Spot-checked against the (read-only, unmodified) firmware repo directly: `eprom_get_chip_id` in `src/proms/eprom.cpp` does call `firestarter_set_control_register(handle, CTRL_VPP_A9_ENABLE, 1)`, confirming the citation's content (line numbers may drift slightly from a `beta`-vs-checkout skew but the cited functions and control bits are real). `git -C /workspaces/firestarter status --short` is empty — firmware repo confirmed unmodified. |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified).

### Requirements Coverage (SAFE-01..05)

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| SAFE-01 | 182-01, 182-02, 182-03 | ✓ SATISFIED | `DIP32_27C801` pinout landed with `address-bus-pins` index 19 = pin 1 (confirmed by direct `get_bus_config` call: `bus[19] == pin_conversions[32][1]`, no `vpp-pin` key). `resolve_pinout_key`'s 32-pin arm forks on `variant_lo` inside `proto_id == 0x08`, no per-part table (`git grep` for the 8 part numbers in `build_db.py` — none). `tools/diff_db.py` exits 0 (ran myself), attributing exactly 8 rows to `RULE_PHASE182_A19_PINOUT`. REQUIREMENTS.md wording matches what shipped (pin-map correction, not a synthetic predicate). |
| SAFE-02 | 182-01, 182-07 | ✓ SATISFIED | D-05 resolved against the operator's expectation (gate confirmed required, not retired) — recorded in REQUIREMENTS.md with the `CTRL_ADDRESS_LINE_18`/`CTRL_VPP_P1_ENABLE` bit-0x08 mechanism cited. `confirm_or_refuse` prints `hazard_text` before any prompt; verified by direct read of `jp5_gate.py`. |
| SAFE-03 | 182-05, 182-06 | ✓ SATISFIED | Trace recorded in `jumper-display-ground-truth.md` with per-claim citations to schematic coordinates and firmware line numbers. Assumption A1 (the one load-bearing unmeasured link the `{write, erase}` scope rested on) was operator-measured at 4.9 V — decisively in the confirming band — per `evidence/182-06-bench-readings.md`. The two remaining PROBE-PENDING cells (Rev 2.0/2.1 JP4 destination, Rev 0/1 JP3 routing) are outside SAFE-03's own scope (they belong to D-11's broader VPP-destination table, explicitly not required to be exhaustive per D-11/D-12) and are recorded as open with reasons, not asserted — consistent with D-12's prohibition against quietly asserting an unsettled cell. Marking SAFE-03 Complete is justified: the requirement's literal text ("which operations the gate covers... recorded with its evidence") is fully met. |
| SAFE-04 | 182-01, 182-07 | ✓ SATISFIED | Non-TTY refusal happens before `confirm_fn` (traced in source, confirmed by test `test_confirm_or_refuse_off_tty_returns_false_and_never_calls_confirm_fn`-class assertions in the 40-test run). `dev test` (`chip_test.py`) and `dev write-cycle` (`eprom_operations.py:write_cycle_eprom`) both call `write_eprom`/`erase_eprom` without passing `pin1_hazard_acknowledged`, so both inherit the `False` default and are unconditionally refused on the 8 gated parts — see Anti-Patterns/Gaps Summary below for the `dev write-cycle` caveat. `--auto`/`--chain` have no firestarter CLI counterpart (confirmed: no match in `firestarter_app/firestarter/`). |
| SAFE-05 | 182-04 | ✓ SATISFIED | `_get_rev2_2_jumper_settings_data` and its commented call site are gone from `firestarter/ic_layout.py` (confirmed by direct read — only the live `_get_rev2_jumper_settings_data` sibling remains). `test_ic_layout.py` carries an `hasattr`-negative guard. |

No orphaned requirements: all five SAFE-01..05 IDs the task named are declared across the seven plans' `requirements:` frontmatter, and REQUIREMENTS.md's Traceability table has a row for each, all "Phase 182 / Complete".

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `firestarter_app/firestarter/jp5_gate.py` | New pure-policy module | ✓ VERIFIED | Exists, read in full; no I/O, no comments (CLAUDE.md rule honored), `SOCKET_PIN_1_BUS_LINE`/`GATED_ADDRESS_BIT`/`DAMAGE_CAPABLE_OPERATIONS` all present, wired into both CLI and operator layers. |
| `firestarter_app/firestarter/data/pinouts.json` (`DIP32_27C801`) | New layout | ✓ VERIFIED | Confirmed content and `get_bus_config` resolution directly. |
| `firestarter_app/firestarter/data/chip_database.json` | Regenerated, 8 rows moved | ✓ VERIFIED | `tools/diff_db.py` exits 0, attributes exactly 8 rows to the new rule. |
| `firestarter_app/tests/test_jp5_gate.py` | End-to-end proof suite | ✓ VERIFIED | 40 tests, ran directly, all pass. |
| `firestarter_app/firestarter/exceptions.py` (`Pin1HazardRefusedError`) | Typed refusal | ✓ VERIFIED | Present, wired into `map_typed_errors`. |
| `firestarter_app/tools/build_db.py` (`_PGM_ON_PIN31_MAX_SIZE`) | Dispatch fork | ✓ VERIFIED | Confirmed via direct dispatch calls and `test_build_db_inclusion.py` (part of the 71-test run). |
| `firestarter_app/tools/DECODE-NOTES.md` | Section 1 current | ✓ VERIFIED | `DIP32_27C801` and `0x600C` correction both present via grep. |

### Key Link Verification

| From | To | Via | Status |
|---|---|---|---|
| `pinouts.json DIP32_27C801` | `jp5_gate.socket_pin1_address_bit` | `EpromDatabase.get_bus_config` | ✓ WIRED — confirmed by direct call, bus index 19 matches `pin_conversions[32][1]`. |
| `cli_handlers.write/erase` | `eprom_operations.require_acknowledged` | `jp5_gate.confirm_or_refuse` → `pin1_hazard_acknowledged` kwarg | ✓ WIRED — traced by line-order and by the `Mock`-patched integration tests. |
| `exceptions.Pin1HazardRefusedError` | operator-visible refusal text | `map_typed_errors` verbatim arm | ✓ WIRED — confirmed via `git grep` on both files. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Gate test suite | `pytest tests/test_jp5_gate.py -o addopts="" -q` | `40 passed in 0.56s` | ✓ PASS |
| Synthetic-injection legs (SC2) | `pytest tests/test_jp5_gate.py -k synthetic -v` | `2 passed` | ✓ PASS |
| Directly-affected regression files | `pytest tests/test_build_db_inclusion.py tests/test_revision_constants_parity.py tests/test_ic_layout.py tests/test_diff_db_gate.py tests/test_wire_dict_equivalence.py -o addopts="" -q` | `71 passed in 3.82s` | ✓ PASS |
| Generator regen self-check | `python tools/diff_db.py` | `PASS: all 744 changed chips explained ... EXIT 0` | ✓ PASS |
| `DIP32_27C801` bus resolution | direct `get_bus_config(32, "DIP32_27C801")` call | `bus=[0..16,20,22,21]`, no `vpp-pin` | ✓ PASS |
| Lint/type | `ruff check` (7 files), `mypy jp5_gate.py --no-error-summary` | `All checks passed!`; no errors | ✓ PASS |
| Debt markers | `grep -nE 'TBD\|FIXME\|XXX'` over all phase-modified source/test files | no matches | ✓ PASS (no blocker) |

Full 2337-test app suite and gitlink-consistency were already established earlier this session (Python 3.11, exit 0, app HEAD `4adf719` unchanged since) and were not re-run in full per the single-full-run guidance; the above are the fresh, phase-scoped re-runs this verification pass performed itself.

### Anti-Patterns Found / Known Open Findings (from 182-REVIEW.md)

| Finding | File | Severity | Disposition |
|---|---|---|---|
| WR-01: `confirm_or_refuse` (`is_affected`→`None` on falsy `bus_config`) and `require_acknowledged` (fail-closed on falsy `bus_config`) disagree on the same input, so a hypothetical chip with an unresolvable `bus-config` would get an unescapable, JP5-mislabeled refusal | `jp5_gate.py:41-66` vs `:83-106` | ⚠️ Warning | Confirmed present in code as REVIEW.md describes. **Not reachable by any of the 746 currently-shipped rows** (independently confirmed: every `pinout` value resolves). Latent design inconsistency, not a live safety gap — does not violate any must-have truth or roadmap success criterion. Recommend filing as a backlog item before `/gsd-ship`; not a phase-goal blocker. |
| WR-02: `write_cycle_eprom` (`dev write-cycle`) calls `erase_eprom`/`write_eprom` without passing `pin1_hazard_acknowledged`, and `cli_handlers.dev_write_cycle` never calls `confirm_or_refuse` — so `dev write-cycle` is now **permanently refused, with no escape**, on the 8 gated parts | `eprom_operations.py:1185/1190`, `cli_handlers.py:1575-1597` | ⚠️ Warning | Confirmed present in code (traced myself: `write_cycle_eprom` calls both operator methods with no `pin1_hazard_acknowledged` argument; no `confirm_or_refuse` call anywhere in `dev_write_cycle`). **My own call on the "phase-goal defect vs. acceptable follow-up" question posed by the task:** this is an **acceptable, separately-tracked follow-up, not a phase-goal defect**. Reasoning: (1) the effect is fail-*safe* — the 8 hazard chips are refused, never silently written, which is the direction every SAFE-0x requirement points; (2) the unconditional operator-layer guard firing for every caller of `write_eprom`/`erase_eprom` (not just the two top-level CLI commands) is the **explicit, planned** design — SAFE-04's own text names `dev test` as a command that must refuse in exactly this way, and `dev test` (`chip_test.py`) hits the identical unescapable refusal for the identical reason, which is required, not a bug; (3) no roadmap success criterion or PLAN must-have truth asserts that every caller of `write_eprom`/`erase_eprom` must have its own confirm/refuse UX — only the top-level `write`/`erase` CLI commands were in the D-06-scoped task list, and both got it. The **gap** is narrower than "over-reach": `dev write-cycle` specifically was not named in SAFE-04 the way `dev test` was, so its permanent-refusal-with-no-escape was an unplanned (if directionally safe) side effect, untested and unfiled. Recommend filing a backlog item (parallel to 999.55-999.60) to either wire `confirm_or_refuse` into `dev_write_cycle` or explicitly document the permanent-block as intended — but this does not block phase 182's goal, which concerned exactly the CLI surface that got it right. |

Neither finding is a debt marker (no `TBD`/`FIXME`/`XXX`), neither is reachable by shipped data in WR-01's case, and neither creates a path where VPP reaches socket pin 1 without the operator being told — the phase's stated goal is about exactly that path, and it holds. Both are recorded here because they are real, currently **unfiled** (checked `ROADMAP.md`'s backlog section and `REQUIREMENTS.md` — no 999.6x stub or note references either finding), and a human should decide whether to file them now or accept the risk as documented.

### Human Verification Required

None. All five roadmap success criteria and all five SAFE-0x requirements were independently verified against the actual codebase (not merely SUMMARY claims), with direct command execution rather than trust in prior claims for every check above. The one item the task asked this verifier to render its own judgment on (the `dev write-cycle` interaction) has been resolved with reasoning above rather than deferred.

### Gaps Summary

No gaps block phase-goal achievement. Two code-review warnings (WR-01, WR-02) remain unfiled in the project's backlog/requirements record as of this verification — see Anti-Patterns table above for full reasoning and recommendation. Recommend the human orchestrator file these (e.g., alongside the 999.55-999.60 stubs 182-07 already filed) before running `/gsd-ship`, but they do not gate phase closure: no must-have truth failed, no artifact is missing or a stub, no key link is unwired, and the safety direction in both cases is fail-closed rather than fail-open.

---

_Verified: 2026-09-10T21:30:00Z_
_Verifier: Claude (gsd-verifier)_
