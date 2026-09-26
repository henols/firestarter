# Phase 177 Scope Decisions

Recorded by the operator (all four RECOMMENDED options taken) before plan `177-01` proceeds past
Task 1. Each decision names the option taken and a one-line reason. Downstream tasks in this plan
and in `177-02` / `177-03` implement the option recorded here.

## D-177-1

**Option A** — Close PRUNE-04 as measured-empty within the `dev test` engine (`chip_test.py`).
Reason: the exhaustive call-site inventory finds exactly two `operator.read_eprom` sites in
`chip_test.py` (`:2642`, `:2728`), both name-and-excluded (the fingerprint read-back by D-1, the
SDP leg because its read-back IS the verdict), so the in-engine population is measured zero;
`eprom_operations.write_cycle_eprom` is the only genuine read-to-compare site in the package but
is not the `dev test` engine and its read-back is the uno328pb read-repeatability oracle, not a
candidate for conversion — converting it would repeat the exact error D-1 corrected one layer
down.

## D-177-2

**Option A** — Add both `_synthesized_match_fingerprint` on the zero-I/O path AND a `bad == 0 ->
FP_MATCH` bucket inside `classify_fingerprint`. Reason: `ff_ratio` can never be `None` inside
`classify_fingerprint` (it is always a computed float), so the honest-`None` synthesized path
requires a separate constructor regardless; and `RK-174-05-p177-match-bucket-d4d6` names its
mechanism as "add a `match` bucket to the classifier" and its shape `at28c256-full-all-ok-sdp`
(an SDP-leg shape this phase's read-back gate does not touch) only moves if the classifier itself
gains the bucket. The bucket is placed AFTER the `ff_ratio >= _FF_RATIO_THRESHOLD` test and AFTER
the address-line test, before the `repeat_divergent is True` test — placing it above the
`ff_ratio` test would silently re-key the whole `blank/contact` population, which this phase
prohibits; `gh23-w27e257-fail` (the only frozen `blank/contact` shape) stays frozen at
`7a89fcea856a` as the pin proving the placement is correct.

## D-177-3

**Option A** — Keep both shape ids, re-point each. `sst27sf512-six-step`'s `write`/`verify`
`step_specs` move from `indeterminate` to `match` — this IS `RK-174-01`'s declared re-key.
`sst27sf512-six-step-readback-gated` re-points to the gate's OTHER branch: a step that FAILED and
therefore kept its real read-back, verdict `marginal` (never `BAD`, which would land on the
community-fail arm). Reason: this re-populates the INCONCLUSIVE arm of `LADDER_PINS` so
`test_ladder_pins_cover_all_four_build_db_diff_arms` still covers exactly four distinct
`(proposed_disposition, ladder_state)` pairs, and neither builder is deleted — the gated shape
stays as the evidence that the original R2 projection (fingerprint dropped on a pass) was
falsified by PRUNE-03.

## D-177-4

**Option A** — Publish the full old-to-new `dedup_fingerprint` mapping as a committed meta-repo
artifact and declare the MEASURED count in `MILESTONES.md`. Reason: GATE-06 requires the re-key
recorded with before/after hashes, and D-4/D-6 says the re-key is "stated publicly"; the 18-row
figure from RESEARCH.md is a projection, not a value to transcribe — plan `177-01` Task 3 measures
the actual re-key count from the committed 26-row corpus, and if it disagrees with 18 that
disagreement is itself a finding to record in `MILESTONES.md`'s corrections table (plan `177-02`
Task 3), not an error to reconcile away. Editing or closing no GitHub issue is in scope for this
milestone.

## D-177-5

**Option A** — Proceed with the measured values as declared, re-measured independently in
`firestarter_app/.venv311` (not transcribed from `evidence/177-01-red-capture.txt`) before this
line was written. Measured moved set: `at28c256-full-all-ok-sdp` `52fb759dc48c` → `050ad3830704`,
`sst27sf512-full-all-ok` `4b3e52cab987` → `14d306256076`, `w27e257-full-all-ok` `22908e2954c3` →
`3a9f95aba65e` — all three agree exactly with `177-RESEARCH.md`'s projections and with
`evidence/177-01-red-capture.txt`. `unmoved_count=13` confirmed, `gh23-w27e257-fail` stays frozen
at exactly `7a89fcea856a`, and `distinct_arms` measures `4` (not the projected 3 — disagreement
named below). The measured filed-corpus re-key count is `18`, agreeing exactly with the inherited
projection of 18 and with the same issue list (`22,24,25,26,27,29,31,39,40,42,45,46,47,48,49,50,51,52`).
None of the plan's Option-B halt conditions hold: the moved set matches the expected list exactly,
`gh23-w27e257-fail` did not move, the four-arm invariant is restorable (per D-177-3), and the
corpus count matches the projection exactly (not merely "close"). Disagreements found and recorded
for `MILESTONES.md`'s corrections table (Task 4): (1) `distinct_arms` measured `4`, not the
`177-RESEARCH.md`-projected `3` — two of the three INCONCLUSIVE-arm members
(`gh47-sst27sf512-pass`, `sst27sf512-six-step`) are hand-specified fixtures whose literal
classification strings `classify_fingerprint` never recomputes, so only `at28c256-full-all-ok-sdp`
(the one real-path builder in that arm) moved automatically; (2) `sst27sf512-six-step-readback-gated`'s
inherited projection `60a031573aab` is falsified — applying the PRUNE-03 rule to both that shape's
fingerprint-dropped `step_specs` and `sst27sf512-six-step`'s `indeterminate` `step_specs` converges
on the SAME value `7fb88e0b07d6`, collapsing the gated shape onto the tracer rather than producing
a distinct one (D-177-3 Option A's re-point to a `marginal`/failed branch is the remedy, executed in
Task 2); (3) `gh47-sst27sf512-pass` projects to `1f812aae49ca` under the corpus-level PRUNE-03
transform, but per D-177-6 below its `report_shapes.py` builder is not edited and its `FROZEN_HASHES`
entry does not move.

## D-177-6

**`gh47-sst27sf512-pass` is NOT re-pointed.** Confirmed by fresh measurement: `FROZEN_HASHES['gh47-sst27sf512-pass']`
stays `f9dbc31dcd27` (its hand-specified `step_specs` in `_build_gh47_sst27sf512_pass` are untouched;
`178-6` deliberately does not edit them). `D-177-3` named only the two `sst27sf512-six-step*`
builders in scope for re-pointing; the operator has ruled `gh47-sst27sf512-pass` stays inside that
stated scope for the same hand-specified-fixture reason as those two shapes. Reason: this keeps the
number of undeclared movements at zero (no shape moves that D-177-3 did not name), and the
four-arm `LADDER_PINS` invariant is satisfied without moving it — `gh47-sst27sf512-pass` keeping its
`indeterminate` literal (unchanged `('inconclusive -- needs N>=2 agreement (advisory)', '')` ladder
pin) leaves the INCONCLUSIVE arm populated regardless, once `sst27sf512-six-step-readback-gated`
re-populates the other slot per D-177-3. The falsified `1f812aae49ca` projection (both the
`177-RESEARCH.md` shape-level projection and the corpus-level projection for filed issue gh#47) is
written into `MILESTONES.md`'s corrections table (Task 4) as a superseded claim, not silently
absorbed.
