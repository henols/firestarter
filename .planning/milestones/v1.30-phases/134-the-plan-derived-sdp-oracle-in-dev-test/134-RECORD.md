# Phase 134 Record — The Plan-Derived SDP Oracle in `dev test`

**Closing record for Phase 134.** Seven mandatory sections: requirement accounting, decision
coverage for D-01…D-20, the five ROADMAP success criteria discharged with named evidence,
corrections carried forward with both readings, the seven non-vacuity obligations, residuals, and
the Evidence Ceiling stated plainly. Every measured figure below is traced to a named plan SUMMARY,
`134-CI-PARITY.md`, or `134-GH20-TRIAGE.md` — nothing here was measured for the first time in this
document, except the byte-identical-regression re-checks in §1, which were re-run live at this
plan's execution time and are recorded as such.

---

## 1. Requirement accounting

Fourteen requirements are this phase's own — LEG-01, 02, 03, 04, 05, 06, 07, 08, 12, 13, 14, 16, 17,
18 — spread across eight of the phase's eleven plans (`134-04`, `134-06`, `134-08` tick nothing, by
their own explicit dispatch scope). This plan (`134-11`) is the only plan permitted to tick LEG-18.

| Requirement | Ticked by | Evidence |
|---|---|---|
| LEG-01 | 134-03 | `test_derive_plan_allow_population_emits_six_supported_ops`, `test_derive_plan_allow_dev_test_exposes_zero_cli_options`, `test_derive_plan_allow_flips_supported_when_sdp_capability_patched` (commits `fcb3b28`/`f2f280c`) |
| LEG-02 | 134-03 | `test_derive_plan_refuse_population_emits_six_na_steps_with_reason`, `test_derive_plan_refuse_run_plan_reports_na_with_no_operator_call`, `test_refuse_write_scope_none_is_byte_identical_to_pre_phase134` (commits `fcb3b28`/`f2f280c`) |
| LEG-03 | 134-01 | `TestInhibitedPattern` (5 tests), non-vacuity obligation #1 (commit `4395c8a`) |
| LEG-04 | 134-03 | `test_derive_plan_baseline_transition_ordering` (commit `f2f280c`) |
| LEG-05 | 134-02 | D-03's full 2×2: `test_oracle_readback_true_a_produces_ok`/`_true_b_produces_bad`/`_false_a_produces_marginal`/`_false_b_produces_marginal` (commit `7284c7d`) |
| LEG-06 | 134-05 | Engine half (134-02, `test_lock_leaked_write_ok_true_b_readback_is_bad`, commit `4ac946a`) + exit-code half (134-05, `test_leaked_lock_exits_1`, `test_mixed_bad_and_marginal_exits_1_not_2`, commits `d9b14ef`/`c56fc32`) |
| LEG-07 | 134-02 | `test_partial_readback_reports_bad` (commit `4ac946a`) |
| LEG-08 | 134-02 | `test_degenerate_readback_empty_is_bad`/`_short_is_bad`/`_all_zero_is_marginal`/`_all_ff_is_marginal_blank_contact` (commit `2699579`) |
| LEG-09 | *(Phase 133, not re-ticked)* | Re-verified byte-identically green at this plan's execution: `pytest -k "test_unlock_exempt_from_destructive or test_gate_closed_from_start or test_lock_ran_then_gate_closes"` → 3 passed |
| LEG-10 | *(Phase 133, not re-ticked)* | Re-verified: the six named LEG-10 drain/registry tests, unmodified |
| LEG-11 | *(Phase 133, not re-ticked)* | Re-verified: the four named LEG-11 degrade/escape tests, unmodified |
| LEG-12 | 134-07 | Carriage (134-06: field, `to_dict()` key, console row, `SCHEMA_VERSION` 1.3) + assignment at the seam (134-07: `TestHoldStateLeg12`, 3 tests, commit `361aafe`) |
| LEG-13 | 134-10 | `test_count_applicable_sdp_gated_allow_chip_ratio_drops` (`m_applicable=10`, `n_ran=6`) + 3 companion pins (commit `2b7a702`) |
| LEG-14 | 134-09 | Wording (134-08) + the committed scoped gate `tests/test_sdp_recovery_wording.py` (8 tests, commits `f246a7e`/`2895516`) |
| LEG-15 | *(Phase 133, not re-ticked)* | Re-verified: `pytest tests/test_op_registration_parity.py` → 7 passed, unmodified |
| LEG-16 | 134-02 | `_dead_write_path_operator` + `test_dead_write_path_baseline_b_is_bad`, non-vacuity obligation #3 (commit `2699579`) |
| LEG-17 | 134-10 | R1–R6, each pairing `sdp_lock.assert_not_called()` with a rendered `NOT-RUN` reason (commits `2f75cb9`/`2072105`) |
| LEG-18 | **134-11 (this plan)** | `134-GH20-TRIAGE.md` + `at28c256-write-path-failure-gh20.md` (Owner: henols) |

**LEG-09/10/11/15 were NOT re-ticked and their named Phase-133 proofs were verified
byte-identically green**, re-run live at this plan's execution time (not merely inherited from an
earlier plan's own claim):

```
$ .venv/ci-replica/bin/python -m pytest tests/test_chip_test_sdp_leg.py -k \
  "test_unlock_exempt_from_destructive or test_gate_closed_from_start or \
   test_lock_ran_then_gate_closes or test_finally_drains_on_exception or \
   test_keyboard_interrupt_drains_and_propagates or test_system_exit_drains_and_propagates or \
   test_empty_registry_noop or test_drain_continues_after_failure or \
   test_drain_does_not_mutate_results or test_serial_timeout_degrades_one_step or \
   test_hardware_error_degrades_one_step or test_run_fatal_escapes or \
   test_assertion_error_propagates" -o addopts="" -q
14 passed, 65 deselected in 0.06s

$ .venv/ci-replica/bin/python -m pytest tests/test_op_registration_parity.py -o addopts="" -q
7 passed in 0.17s
```

`git diff -U0 57e8eb5..HEAD -- tests/test_chip_test_sdp_leg.py tests/test_op_registration_parity.py`
confirms zero deletions inside any of these named Phase-133 test bodies across the whole phase (this
is restated from `134-04-SUMMARY.md`'s own identical check, re-confirmed here).

**Eighteen `[x]` LEG rows in total** across the two phases —
`grep -c '^- \[x\] \*\*LEG-' .planning/REQUIREMENTS.md` returns **18**, matching the fourteen this
phase ticked plus the four Phase 133 ticked. No `RELOCK-*`, `CHAN-*`, or `CLOSE-*` row changed —
`grep -c '^- \[ \] \*\*RELOCK-\|^- \[ \] \*\*CHAN-\|^- \[ \] \*\*CLOSE-'` returns **14**, unchanged
from before this plan's edit.

---

## 2. Decisions honoured, D-01 … D-20

| ID | Honoured how | Evidence |
|---|---|---|
| D-01 | **Literal.** `write_eprom`'s bool is a precondition signal only; `True` proves the experiment ran as designed, `False` routes to `marginal`, never `BAD`. **Research's truth-table branch 5** ("the ack readable as a *separate* signal") was **not implementable as written and is recorded as overturned** — `_disconnect_programmer()` clears `comm.seen_message_ids` before `write_eprom` returns, so the ack is unobservable from `chip_test.py` and is already folded into the bool. | 134-02 (`_dispatch_sdp_leg`); `134-CONTEXT.md` correction 1. |
| D-02 | **Literal.** `write_eprom` False + read-back == B ⇒ `marginal`, not BAD — the opt-out-not-honoured cause is more likely than a chip fault. | 134-02, `test_oracle_readback_false_b_produces_marginal`. |
| D-03 | **Literal.** The full 2×2 cross product proven, holding the bool constant across the first two legs (a strictly stronger proof than a bool-driven implementation could pass). | 134-02, four named `test_oracle_readback_*` tests. |
| D-04 | **Literal.** Degenerate read-backs split by cause: LENGTH ⇒ BAD (length gate, before any `classify_fingerprint` call — P-02's trap), CONTENT ⇒ marginal (routed through `classify_fingerprint`). | 134-02, `test_degenerate_readback_*` (4 tests). |
| D-05 | **Literal.** The non-laundering obligation is a committed TEST (not an argument): B's `ff_ratio` measured ~0.0039 against the live `_FF_RATIO_THRESHOLD = 0.98`, asserted against the live generators for the real region, never a literal. | 134-01 (`TestInhibitedPattern`'s D-05 leg), 134-02 (dispatcher-level, `test_inhibited_full_b_readback_does_not_launder_as_blank_contact`). |
| D-06 | **Literal, and the record states both readings** (see §3 Criterion 1 and §4 Correction 1). SIX steps: `write-baseline-b` · `write-baseline-a` · `sdp-lock` · `write-inhibited` · `sdp-unlock` · `write-restored`, single-sourced via `_SDP_LEG_STEP_ORDER`. | 134-03. |
| D-07 | **Literal.** Two baseline ops, not one folded `sdp-baseline` — because `render()`'s console table shows only `op`/`verdict`/`error_code`/`fingerprint`, never `reason`, so the failing direction must be legible in the op string itself. | 134-01 (op vocabulary), 134-03 (`derive_plan` emission). |
| D-08 | **Honoured non-literally — its own clause is measured-wrong and superseded by D-20, recorded plainly, not smoothed over.** The dedicated baseline gate (`_baseline_closes_sdp_gate`, wider than `_id_step_closes_gate`'s `(BAD, SKIPPED)` tuple — closes on BAD/marginal/SKIPPED/NA) landed exactly as decided. But D-08's own literal clause *"`sdp-unlock` is never attempted because nothing was locked"* is **false as written**: `OP_SDP_UNLOCK` is deliberately absent from `_DESTRUCTIVE_OPS` (LEG-09), so as D-08 is literally written the unlock step **would run** and report a false `OK` at a part that was never locked (the P-06 emission-claim shape). **D-20 supersedes this clause**: `sdp-unlock` joins the baseline-gate's *gated-outputs* set (`_SDP_LEG_GATED_OPS`) and renders SKIPPED when the gate closed. **This does NOT weaken LEG-09** — LEG-09 is scoped to the *destructive* gate (`_DESTRUCTIVE_OPS` membership), a structurally different mechanism from the new baseline gate; a dedicated test (`test_leg09_destructive_gate_never_skips_the_explicit_unlock_step`) proves a closed *destructive* gate still never skips the unlock, keeping Phase 133's LEG-09 proof byte-identically green. | 134-04, `test_baseline_gate_closes_dead_write_path_allow_chip_full_leg`, `test_leg09_destructive_gate_never_skips_the_explicit_unlock_step`; `134-CONTEXT.md` D-08/D-20. |
| D-09 | **Literal.** `_ALWAYS_WRITES_NOTICE`'s write-pass count is single-sourced (`_ALWAYS_WRITES_PASS_COUNT = 6`) and pinned by a test that *derives* the count from a live `derive_plan` call rather than restating the literal `6` (P-08 prevention 2). | 134-08, `test_pass_count_is_derived_from_a_live_plan_never_a_literal`. |
| D-10 | **Literal, never a boolean (P-06 prevention 3).** `DiagnosticReport.sdp_hold_state: str` is the eleventh `to_dict()` key — **a measured correction of this decision's own inherited count**: `134-CONTEXT.md`/134-06's own plan text read the prior key count as nine; the live count was already **ten** (`schema_version`, `generated`, `auto_capture`, `transport_health`, `steps`, `banner`, `voltage`, `is_submittable`, `dedup_fingerprint`, `db_diff`) before this field landed — `sdp_hold_state` is the **eleventh**, not the tenth. Recorded in the `SCHEMA_VERSION` 1.3 comment ladder and in `134-06-SUMMARY.md`. `SCHEMA_VERSION` bumped 1.2 → 1.3. | 134-06, `test_hold_state_no_boolean_under_lock_or_protect_key_anywhere_in_to_dict`, `test_schema_version_1_3_single_sourced`. |
| D-11 | **Literal, cost accepted and recorded, not fixed.** `dedup_fingerprint`'s body is byte-unchanged; a comment records the re-key cost without spelling out the six op strings (an early draft did and tripped the plan's own op-vocabulary grep — corrected). gh#20's own orphaned id, `00e121446ceb`, is named explicitly inside the LEG-18 finding (`134-GH20-TRIAGE.md` §4) — the concrete instance this cost produces on a real community report. | 134-06 (comment + `test_dedup_fingerprint_sensitive_to_sdp_step_verdict_change`), 134-11 (`134-GH20-TRIAGE.md` §4). |
| D-12 | **Literal.** Two named recovery forms (`_SDP_RECOVERY_LOUD`/`_SDP_RECOVERY_NEUTRAL`); a line prints on the happy path too (silence is not a statement). The Ctrl-C residual (inherited from 133 D-07) is recorded as open, not closed, mitigated by D-09's up-front notice rather than a `finally` handler — see §6. | 134-08, `TestSdpRecoveryFormsD12` (4 tests), `TestCtrlCResidualNotClosedD12`. |
| D-13 | **Literal, and the hand-off is explicit.** LEG-14's gate is a SCOPED pytest (`SDP_RECOVERY_CONSTANT_NAMES`), never a whole-report grep — measured that `_ALWAYS_WRITES_NOTICE` and `derive_plan`'s own 0x0D NA reason legitimately contain "erase", so a whole-report grep would go RED on correct text (the 133 D-14 `_sample` shape). `_ALWAYS_WRITES_NOTICE` is scanned SEPARATELY, for rule 1 only, never rules 2/3, for the identical reason. Phase 137's CLOSE-03 is named as the extension point, not duplicated here. | 134-08 (constants), 134-09 (`tests/test_sdp_recovery_wording.py`, 8 tests). |
| D-14 | **Literal.** Explicit exit-code precedence (`_EXIT_CODE_PRECEDENCE = (1, 2, 0)`, `_overall_exit_code`) replaces the naive `max()`, restoring what the source comment and `dev_test`'s own docstring already claimed. A live audit at plan `134-05`'s execution re-confirmed RESEARCH's finding directly (12 `exit_code == 2` sites, zero mixing BAD and marginal) rather than inheriting it. | 134-05, `test_mixed_bad_and_marginal_exits_1_not_2`; non-vacuity obligation #5. |
| D-15 | **Literal, cost pinned mechanically.** A NOT-RUN oracle on an ALLOW chip keeps verdict `SKIPPED` (stays out of `_RAN_VERDICTS`) and the exit code gains a floor of 2, composed as a precedence *candidate* (never `max(code, 2)`, which would re-launder a BAD run). Stated cost — the exit code stops being a pure function of step verdicts — pinned by a direct unit test holding the identical `results` list constant while varying only `sdp_oracle_not_run`. **Corrects 133 D-15's own inverted reading**: `MIN_CHECKED_SOURCE_FILES` is a FLOOR, not a spent budget (see §4 Correction 3). | 134-07, `TestExitFloorD15` (5 tests). |
| D-16 | **Literal.** gh#20's finding is recorded in THIS phase (`134-GH20-TRIAGE.md`); the public reply is Phase 137's, behind CLOSE-06's blocking operator wording review. The underlying AT28C256 write failure is filed as a backlog item with a named owner (`Owner: henols`) so it does not become another unowned acknowledgement. | 134-11 (this plan), Task 1. |
| D-17 | **Literal.** All six laundering routes R1–R6 tested; R1/R2 driven through a synthetic nonzero-`chip-id` `EpromDatabase` fixture (`tests/fixtures/synthetic_nonzero_chip_id.py`) so the full id-step → gate → refusal causal chain is genuinely exercised, labelled unreachable in production today (all 43 SDP-ALLOW chips have `chip-id == 0`, re-measured live) and never described as "the leg is gated by chip ID" (`grep -ci` returns 0 tree-wide). | 134-10, `TestLaunderingRoutesR1R2SyntheticChipId`, `test_all_sdp_allow_chips_have_zero_chip_id_measured_live`. |
| D-18 | **Honoured with a Claude's-Discretion refinement, taken on four measurements and recorded plainly.** The SDP leg is gated on `write_execute`; on an ALLOW chip, `write_scope="none"` locks all six SDP-leg steps into `locked_destructive` (matching D-18's own text). On a **REFUSE** chip, the refinement: `write_scope="none"` emits **nothing at all** — neither a `Step` nor a `locked_destructive` entry — rather than D-18's literal implication of four fabricated NA steps. Reason (four measurements, not one): (1) LEG-10's named `test_empty_registry_noop` and (2) three shipped exact-equality `locked_destructive`/`locked_ops` assertions on M8720/AM2716 would both go RED under a literal reading; (3) the house rule that an unsupported step must never be fabricated as a locked/runnable one; (4) `write_scope="none"` is unreachable from a real `dev test` run since Phase 121's `_resolve_write_scope` reversal, so this is library/test surface only, never a live gate. | 134-03, `test_allow_write_scope_none_locks_six_sdp_leg_steps_and_moves_the_banner`, `test_refuse_write_scope_none_is_byte_identical_to_pre_phase134`. |
| D-19 | **Literal.** The inhibited-write payload has its own named generator (`generate_inhibited_pattern`), calling `generate_pattern` exactly once and bitwise-complementing it — never a second call over the same region (P-01's headline trap). P-01's five assertions (equal length, differ at every byte, neither degenerate, non-laundering) proven against the live generators for the real region. | 134-01, `TestInhibitedPattern` (5 tests), non-vacuity obligation #1. |
| D-20 | **Literal.** `sdp-unlock` joins the baseline-gate's gated-outputs set and renders SKIPPED when that gate closed — resolving research §4.1's OQ-1 and correcting D-08's own measured-wrong clause (see D-08 above). Measured consequence for gh#20's shape: the banner reads **6 of 10**, not the design record's stated **5 of 10** (see §3 Criterion 1 and §4 Correction 1 for both readings). | 134-04, `test_leg09_destructive_gate_never_skips_the_explicit_unlock_step`; non-vacuity obligation #6. |

**P-03 prevention 4, named for the record as its own item (not a D-NN decision, but load-bearing to
D-01/D-03):** research's P-03 prevention 4 proposed `(write_eprom False, read-back A) ⇒ OK`. **This
is recorded as OVERTURNED** by correction 1 (D-01) and D-03's own 2×2 design — the shipped behaviour
is `(False, A) ⇒ marginal`, not OK, because a failed precondition should never be silently treated as
success regardless of which read-back direction happened to result. Not implemented as P-03 wrote
it.

---

## 3. The five ROADMAP success criteria, discharged with named evidence

Quoted from `.planning/ROADMAP.md` §"Phase 134: The Plan-Derived SDP Oracle in `dev test`".

### Criterion 1

> Running `dev test` against any of the 43 SDP-capable ALLOW chips derives, with **no new
> command-line option**, a **four-step** leg (baseline transition write, lock, inhibited write +
> read-back, unlock) from `sdp_capability()`; running it against any of the 41 REFUSE chips instead
> produces four NA/SKIPPED steps each carrying the refusal reason.

**Evidence:** `derive_plan` derives the leg for all 43 measured ALLOW chips
(`test_derive_plan_allow_population_emits_six_supported_ops`) and six NA steps for all 41 measured
REFUSE chips (`test_derive_plan_refuse_population_emits_six_na_steps_with_reason`), with **zero new
CLI options** (asserted structurally against the real `dev_test` Click command's `params`).

**Mandatory correction, stated plainly (D-06, both readings):** the criterion's own "four-step"
wording is **measured-wrong**. The leg that ships is **SIX** steps:
`write-baseline-b` · `write-baseline-a` · `sdp-lock` · `write-inhibited` · `sdp-unlock` ·
`write-restored`. Why the inherited "four" is wrong: it predates LEG-04's own two-transition-
direction mandate, and the ROADMAP's own enumeration omits `write-restored` — the *only* step
producing evidence the part was left writable, on a family whose protection state cannot be read
back. `REQUIREMENTS.md`'s own LEG-01/LEG-02 text already carries this correction in-line ("The
inherited 'four' predates LEG-04's..."). This record states both readings rather than silently
picking one: the criterion's original words say four; the shipped, tested, and requirement-corrected
count is six.

### Criterion 2

> A write that unexpectedly succeeds after the lock is applied is reported **BAD** with exit code
> 1 — never SKIPPED, NA, or OK; a read-back that only partially changed is also reported BAD (gh#11's
> exact symptom); and a degenerate read-back (empty, short, all-`0x00`, or all-`0xFF`) never reads as
> equality.

**Evidence:** the engine-level BAD arm (`test_lock_leaked_write_ok_true_b_readback_is_bad`, 134-02)
plus the end-to-end exit-1 proof (`test_leaked_lock_exits_1`, 134-05) — both required, since an
exit-code-only test could pass on a route that produces exit 1 via an unrelated BAD step while the
leaked write itself reports something else. The partial-change case (`test_partial_readback_reports_bad`)
and all four degenerate fixtures (`test_degenerate_readback_*`) are proven in 134-02.

**Mandatory caveat, stated plainly (D-14, correction 2):** the criterion's own "exit code 1" clause
was **provably unreachable on any marginal-bearing run until D-14 landed**. Before 134-05's fix,
`_VERDICT_EXIT_CODES` mapped `marginal → 2`, `BAD → 1`, and the naive `code = max(...)` meant
`max(1, 2) == 2` — a run containing both a leaked lock (BAD) and any marginal step would exit **2**,
not 1, silently laundering the milestone's headline finding into the inconclusive code. D-14's
explicit precedence tuple `(1, 2, 0)` fixes this; `test_mixed_bad_and_marginal_exits_1_not_2` pins
it, and non-vacuity obligation #5 proved the fix is load-bearing (reverting to the naive `max()`
reproduces the exact wrong exit code).

### Criterion 3

> Before any lock is applied, the leg proves the write path is genuinely live by writing one
> pattern, verifying it, writing its bitwise complement, and verifying that too — so a chip whose
> write path is dead, but which already carries the expected bytes from an earlier run, cannot pass
> the leg on that basis alone (proven by a committed fixture whose write is a no-op and whose
> baseline step therefore reports BAD).

**Evidence:** the committed `_dead_write_path_operator` fixture (`write_eprom` claims success,
`read_eprom` always yields pattern A regardless of what was written) makes `write-baseline-b` report
BAD (`test_dead_write_path_baseline_b_is_bad`, 134-02) — D-07's own reasoning made concrete: the B
direction is the leg's entire discriminating power, since the shipped write/verify pair (A-only)
could never detect a dead write path on a chip already holding A. `_baseline_closes_sdp_gate`
(134-04) then makes this baseline BAD close the gate before any lock is emitted — proven live
against gh#20's exact shape by this plan's own triage (`134-GH20-TRIAGE.md` §2) and by 134-04's
non-vacuity obligation #6 (a lock genuinely emitted once the gate membership was removed, restored
byte-identically).

### Criterion 4

> Every run against an ALLOW chip renders a `HELD`/`NOT-HELD`/`NOT-RUN(reason)` field in both the
> human report and the JSON artifact, and an NA/SKIPPED oracle step visibly drops the report's
> headline N-of-M applicable-step count rather than leaving it looking perfect; each of the six known
> exit-code-laundering routes is covered by a test asserting both that `sdp_lock` was never called and
> that a visible `NOT-RUN` reason is rendered.

**Evidence:** `report.sdp_hold_state` reaches both `to_dict()` and `render()` (`TestHoldStateLeg12`,
134-07) — `HELD`/`NOT-HELD`/`NOT-RUN(reason)` each proven in both surfaces, never a boolean anywhere
in `to_dict()` (the recursive gate, 134-06). The N-of-M drop is proven for a real gated ALLOW chip
(`test_count_applicable_sdp_gated_allow_chip_ratio_drops`, 134-10 — `m_applicable=10`, `n_ran=6`).
All six laundering routes R1–R6 each pair `operator.sdp_lock.assert_not_called()` with a rendered
`NOT-RUN` reason (134-10).

### Criterion 5

> The report's recovery guidance for a chip left locked says **"rewrite,"** never "erase" (enforced
> by a committed grep — protocol `0x0D` has no erase operation at all), and gh#20 (the AT28C256
> `dev test` FAIL open since 2026-07-30) has been triaged against the new baseline-transition gate,
> with the finding recorded.

**Evidence:** `tests/test_sdp_recovery_wording.py`'s scoped, fail-closed gate (134-09) scans exactly
`SDP_RECOVERY_CONSTANT_NAMES` for "rewrite" present / "erase" absent / no hyphenated op literal, with
a positive control, two fail-closed legs, two target-resolution legs, two committed planted-violation
non-vacuity legs, and a one-time observed-RED proof against the real `_SDP_RECOVERY_LOUD` constant.
gh#20 is triaged against the baseline-transition gate in this plan's own `134-GH20-TRIAGE.md` — the
finding is recorded, not posted; the public reply is Phase 137's (CLOSE-06).

---

## 4. Corrections, with both readings

| # | Artifact measured wrong | Measured truth | How measured |
|---|---|---|---|
| 1 | ROADMAP Criterion 1 / `134-CONTEXT.md`'s own inherited "four-step leg" wording (LEG-01/LEG-02's requirement text carries the same "four", corrected in-line) | The leg is **SIX** steps (D-06): `write-baseline-b` · `write-baseline-a` · `sdp-lock` · `write-inhibited` · `sdp-unlock` · `write-restored`. The inherited "four" predates LEG-04's two-transition-direction mandate and the ROADMAP's own enumeration omits `write-restored`, the only step producing evidence the part was left writable. | `134-03-SUMMARY.md`; `_SDP_LEG_STEP_ORDER`'s single-sourced tuple, count-pinned by a derived (never literal) test. |
| 2 | `cli_handlers.py:1885-1887`'s own comment ("BAD beats marginal via `max`") and `dev_test`'s docstring ("2 if any step is marginal (and none BAD), 1 if any step is BAD") | Both were **false** before this phase: the naive `code = max(_verdict_code(r.verdict) for r in results)` let `marginal` (2) numerically outrank `BAD` (1). D-14's explicit `_EXIT_CODE_PRECEDENCE = (1, 2, 0)` restores the behaviour the comment and docstring already claimed, rather than changing a designed contract. | `134-05-SUMMARY.md`; live audit of 12 `exit_code == 2` sites, zero pre-existing mixed-BAD-marginal cases; non-vacuity obligation #5. |
| 3 | 133 D-15's own reading, inherited into this phase's initial budget framing | `MIN_CHECKED_SOURCE_FILES = 120` is a **FLOOR**, not a spent budget — `checked < 120` fails, so adding source/test files moves `checked` further **above** the floor (124 → 126 across this phase), never spending anything. Phase 134 was free to add test modules throughout; the real, spendable budget was the mypy headroom (2, unmoved the entire phase — see `134-CI-PARITY.md` §After). | `134-CONTEXT.md` correction 4; `134-CI-PARITY.md`'s Before/After sections (124→126 checked, both above the 120 floor). |
| 4 | `133-CONTEXT.md` D-12's own prediction of "**five** Phase-134 exemption rows" pending discharge, and a plan-level assumption of a constant named `_DECLARED_REGISTRY_COUNT` | `_DECLARED_REGISTRY_COUNT` **does not exist** as a name in `test_op_registration_parity.py` — the real names are `_POLICED_REGISTRY_COUNT = 7` and `_DECLARED_NON_REGISTRY_COUNT = 6`. And of the seven Phase-133-authored `OP_SDP_LOCK`/`OP_SDP_UNLOCK` exemption rows standing at Phase 133's close (`_DESTRUCTIVE_OPS`×1, `_MULTI_RUN_OPS`×2, `derive_plan`×2, `_dispatch_multi_run`×2), only the **two `derive_plan` rows were dischargeable** by this phase (removed once `derive_plan` legitimately began emitting these ops) — the other five remain permanent, valid exemptions unrelated to Phase 134's `derive_plan` wiring, not five rows this phase discharged. | Live diff, this plan's execution: `git show 57e8eb5:tests/test_op_registration_parity.py` vs the current file — confirms exactly the two `derive_plan` rows vanished; the other five persist unchanged. |
| 5 | An implicit assumption that the stale-row guard (`test_stale_row_fails`) would itself catch a TEMPORARY row that had become redundant | It does not — the guard fails closed on a **non-existent** op or registry name, but a row referencing a real, still-existing op/registry that has simply become logically redundant passes the guard silently. Discharging the 8 TEMPORARY rows (4 for `_dispatch_step`, 4 for `derive_plan`) was therefore a **discipline obligation enforced by a grep-able `TEMPORARY — discharged by plan N` marker**, not an automatic gate outcome — each owning plan (134-02, 134-03) had to remove its own marked rows in the same commit that made them redundant. | `134-01-SUMMARY.md`'s own stated pattern ("TEMPORARY exemption rows... let a later plan prove its own discharge mechanically rather than by inspection"); confirmed live — zero `TEMPORARY` strings remain in the shipped file. |
| 6 | The two shipped `tests/test_chip_test.py` AT28C256 `0x0D` sweep tests, as they stood before `derive_plan`'s emission changed | `derive_plan`'s emission necessarily changed both tests (the mock operator lacked `sdp_lock`/`sdp_unlock`, and a file-less read-back made every leg step BAD via the length gate). **Repaired**, not weakened: a new stateful, SDP-lock-aware `_sdp_leg_readback_operator` double (tracking a real in-memory chip image, honouring genuine lock/unlock semantics) makes a genuinely-all-OK twelve-step sweep genuinely all-OK — no skip, no xfail, no narrowed assertion. | `134-03-SUMMARY.md`, Deviation #3. |
| 7 | Research's / the requirement text's implicit framing that the chip-ID destructive gate meaningfully protects the SDP-ALLOW population | **Structurally vacuous for the whole population**: all 43 measured SDP-ALLOW chips have `chip-id == 0`, re-measured live (`test_all_sdp_allow_chips_have_zero_chip_id_measured_live`, never a hardcoded count). R1/R2 are driven through a synthetic nonzero-`chip-id` fixture specifically because the real gate is unreachable in production today; no artifact claims "the leg is gated by chip ID" (`grep -ci` returns 0 tree-wide). | `134-10-SUMMARY.md`; D-17. |

| 8 | This record's own row 1 and `REQUIREMENTS.md`'s LEG-02 evidence clause, both citing the LEG-02 test as covering "all 41 measured REFUSE chips" | The test's actual population is **703 chips** — every non-ALLOW entry in the database, a SUPERSET of the 41 protocol-`0x0D` REFUSE chips the ROADMAP names. The behavior is therefore proven **more** broadly than claimed, not less; but the numeral was wrong, in a phase that polices exactly this class of discrepancy in seven other places. Found only because an independent verifier recomputed the population rather than reading the citation. | Phase verifier, 2026-08-04, `134-VERIFICATION.md` finding F-01 — independently recomputed from the live database, then corrected in `REQUIREMENTS.md` in place. |

**Additional measured discrepancies carried forward from earlier plans' own summaries, not
re-derived here but restated so a later reader does not encounter the stale numeral and assume a
test is wrong:**

- **`n_ran=6`, not the design record's stated `5`** for a gated ALLOW chip's banner (D-20,
  `134-CONTEXT.md`) — measured independently by `134-04`, `134-07`, and `134-10`. Root cause:
  `write-baseline-a` is never itself gated (only the four `_SDP_LEG_GATED_OPS` members are skipped
  once the gate closes) and reports OK against a dead-write-path double (its own expected read-back
  is pattern A, which the double always returns) — 6 ran (4 shipped + both baseline directions), 4
  SKIPPED, out of 10 applicable. This is the true minimum achievable ran-count for this shape, not a
  fixture quirk.
- **Non-vacuity obligation #2's planted swap produced THREE red tests, not the two `134-VALIDATION.md`
  stated** (134-02) — `test_lock_leaked_write_ok_true_b_readback_is_bad` independently duplicates one
  arm of the `oracle_readback` pair, so the same OK/BAD-arm swap trips both. The underlying mechanism
  (D-03's polarity pin) is intact and *stronger* for it, not weaker.
- **`to_dict()` already had TEN keys, not the nine `134-CONTEXT.md`/134-06's plan text stated** —
  `sdp_hold_state` is the eleventh key, not the tenth (134-06; see §2 D-10 above).

---

## 5. The seven non-vacuity obligations

A pre-authored gate proves nothing until it is seen to pass. Each was observed **RED once**, then
restored **byte-identically**:

| # | Planted break | What went RED | Restored |
|---|---|---|---|
| 1 | **P-01:** made `generate_inhibited_pattern` return `generate_pattern(start, length)` (B == A) | Both the every-byte assertion and the anti-tautology assertion failed | Yes — `git diff --stat` empty before commit (134-01) |
| 2 | **LEG-06:** swapped `_dispatch_sdp_leg`'s `write-inhibited` OK/BAD arms | **THREE** tests failed — `test_oracle_readback_true_a_produces_ok`, `test_oracle_readback_true_b_produces_bad`, and `test_lock_leaked_write_ok_true_b_readback_is_bad` (not two, see §4) | Yes — `git diff firestarter/chip_test.py` confirmed empty (134-02) |
| 3 | **LEG-16:** made `_dead_write_path_operator`'s write real (persists the last write's actual bytes) | `test_dead_write_path_baseline_b_is_bad` failed — the baseline step went OK instead of BAD | Yes — restoration confirmed line-for-line identical (134-02) |
| 4 | **LEG-14:** planted the bulk-clear word into the REAL, live `_SDP_RECOVERY_LOUD` constant | `test_positive_control_real_constants_do_not_raise` failed, naming exactly `_SDP_RECOVERY_LOUD` | Yes — `git diff firestarter/cli_handlers.py` confirmed empty before commit (134-09) |
| 5 | **D-14:** reverted the exit computation to the naive `max()` | `test_mixed_bad_and_marginal_exits_1_not_2` failed: `assert 2 == 1` | Yes — `git diff` confirmed empty before commit (134-05) |
| 6 | **D-08/D-20:** removed `OP_SDP_LOCK` from `_SDP_LEG_GATED_OPS` | `test_baseline_gate_closes_dead_write_path_allow_chip_full_leg` failed — `operator.sdp_lock` was observed genuinely CALLED against the dead-write-path fixture (gh#20's exact hazard, reproduced live) | Yes — `git diff --stat` empty; full quick set re-run green (134-04) |
| 7 | **Parity gate:** confirmed `test_altered_registry_copy_fails_parity_non_vacuous` still passes after `_ALL_OPS` grows from 9 to 13 | No new leg needed — this obligation is a *confirmation*, not a fresh plant; it stayed green throughout, proving the existing non-vacuity leg is not sensitive to `_ALL_OPS`'s size | N/A — nothing to restore (134-01) |

**The seventh route to a non-running oracle** — beyond research's own R1–R6 — is the baseline gate
itself (D-08/D-20), named explicitly in a module comment beside the R1–R6 test family (134-04,
restated by 134-10) so a later reader does not mistake "six laundering-route tests" for exhaustive
coverage. It fails closed under D-08 + D-15 (exit 1 from the baseline's own BAD, or ≥2 via the
NOT-RUN floor), and non-vacuity obligation #6 above is its own proof of failing-closed-ness.

---

## 6. Residuals, carried not closed

1. **133 D-07's forfeited report on Ctrl-C — still not closed.** After an interrupt mid-leg,
   `run_plan` never returns (`cli_handlers.py`'s `results = run_plan(...)` assignment never
   completes), so neither recovery form prints and there is no report at all. Mitigated by D-09's
   up-front, unconditional notice (printed before anything energises) — **not** a `finally` handler.
   Measured precisely at 134-08: Click's `BaseCommand.main` (standalone mode) catches
   `KeyboardInterrupt` itself and converts it to `sys.exit(1)` before it ever propagates out of
   `CliRunner.invoke()`, so the residual test asserts "no report file, no recovery constant in
   output" rather than a propagating exception the real CLI runner does not produce. Fixing the
   underlying gap would need `run_plan`'s signature and all its call sites changed — real blast
   radius against criterion 4's byte-identical-behaviour claim for shipped ops. **No owner.**
2. **The mypy watermark ratchet — still unowned** (133-RECORD residual 4, Phase 132 residual 2
   before that). Headroom is unchanged at **2** across this entire phase (33/35, measured
   identically at every wave and at this plan's own `134-CI-PARITY.md` §After) — the phase's budgeted
   spend was never actually drawn on.
3. **D-11's `dedup_fingerprint` discontinuity — accepted here, outward description handed to Phase
   137 CLOSE-05.** gh#20's own `dedup_fingerprint` `00e121446ceb` is the concrete, named instance
   this phase's own triage (`134-GH20-TRIAGE.md` §4) hands forward.
4. **`build_db_diff`'s `ladder_state` no longer reaches `community-reported` for a genuinely-passing
   ALLOW chip — a real, previously-undocumented finding, still unowned.** Discovered at 134-03: once
   the SDP leg is genuinely reachable end to end, an all-OK run attaches an `"indeterminate"`-
   classified `Fingerprint` on `write-baseline-b`/`-a` and `write-restored` (134-02's own "attach in
   every arm" design meeting `classify_fingerprint`'s four-bucket design, which has no dedicated
   "perfect match" bucket). This routes `build_db_diff`'s `ladder_state` to `_LADDER_NONE` rather than
   `_LADDER_COMMUNITY_REPORTED` for every genuinely-passing ALLOW chip going forward — a real,
   chip-content-independent consequence of two already-shipped mechanisms (Phase 114, Phase 133-02)
   meeting for the first time via this phase's wiring, not an artifact of any one plan's fixture
   choice. `diagnostic_report.py`/`classify_fingerprint` are outside every Phase 134 plan's declared
   file scope, so it was documented (the one shipped test this surfaces in was repaired to assert the
   newly-measured correct value) rather than fixed. **This plan's own Task 1 scope was limited to the
   AT28C256 write-path defect (gh#20) — it did not extend to filing this separate ladder_state finding
   as its own backlog item.** Flagged here, again, for Phase 137's ledger or a future backlog item
   with a named owner — carried forward from `134-03-SUMMARY.md`/`134-06-SUMMARY.md`, still open, no
   owner.
5. **`.planning/codebase/TESTING.md` remains severely stale** — asserts "the project has no Python
   unit tests" and references a foreign filesystem path, against a tree that now has 91 test files
   plus a fixtures module. **Owner:** `/gsd-map-codebase`, a map-refresh task, not this milestone's.
6. **gh#20's underlying AT28C256 defect — now owned, still open.** Filed by this plan's Task 1 as
   `.planning/todos/pending/at28c256-write-path-failure-gh20.md` with `Owner: henols`. The triage
   (`134-GH20-TRIAGE.md`) explains what the tool would now correctly *do* on this bench; it does not
   diagnose the chip.

---

## 7. The Evidence Ceiling — the honest claim, stated plainly

Restated verbatim from `133-RECORD.md` §6, because it governs this phase's proofs identically:

**This phase proves that the mechanism cannot strand a chip or lose a report to a transport error,
and that the op registries fail closed. It proves NOTHING about SDP behaviour on silicon.**

- **A locked die is unrepresentable in either repo's stubs.** Both the host repo's fixtures and the
  firmware repo's native test harness model the *bus*, never the die's *protection state* — no
  fixture in this phase, or in Phase 133, can simulate real SDP inhibition. Fixtures pin the host's
  *response* to a scripted read-back, never the die's actual state.
- **The causal claim "the lock inhibited the write" is NOT provable this milestone.** Reachable only
  on real silicon — i.e. only from a community `dev test` report, which by design does not gate this
  milestone's close.
- **Protection state is not readable on this family** — exactly why D-03 excludes both SDP ops from
  `_MULTI_RUN_OPS`'s marginal-on-disagreement policy.
- **`0x0D` stays `UNVERIFIED`** at the database level, unmoved by any plan in this phase.
- **No AT28C part has ever been in operator inventory.** Nothing this phase built has ever run
  against real SDP-capable silicon.

Applied specifically to this phase's headline artifact, `134-GH20-TRIAGE.md`: that document explains
what the tool would now correctly **do** on gh#20's bench (close the gate, skip the lock, render the
drop) — it does **not** diagnose the reporter's chip, and it does **not** establish that any lock
ever inhibited any write on that hardware (no lock was ever attempted against gh#20's bench in the
first place; the reporter's own failure is entirely in the pre-lock baseline write path). Any
artifact — this record included, if it strayed — claiming more than the mechanism-only proof above
is the **v1.22 C-5 overclaim class**.

---

*Phase: 134-the-plan-derived-sdp-oracle-in-dev-test*
*Recorded: 2026-08-04, plan 134-11, against the phase's final engine + test source at commit
`2b7a702` (submodule `firestarter_app`, branch `gsd/v1.30-sdp-surface-retirement`).*
