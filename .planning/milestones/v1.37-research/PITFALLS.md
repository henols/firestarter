# Pitfalls Research

**Domain:** Repair of an existing community-facing hardware test/diagnostic harness (`firestarter dev test <chip>`) — conditional diagnostics, a skipped safety pre-check, fault attribution, and a machine-readable report schema evolution, all in one host-only milestone.
**Researched:** 2026-09-02
**Confidence:** HIGH for everything measured against `firestarter_app` at `0a93999` (executed, not inferred); MEDIUM for the external schema-evolution and failure-triage corroboration.

## How to read this file

Every pitfall below is either **MEASURED** (I ran it or read it out of source at HEAD and cite the line) or **REASONED** (a consequence I derived from measured facts). Nothing here is generic advice dressed up in project vocabulary.

**Two of these pitfalls falsify claims the milestone currently makes about itself.** They are Pitfall 1 and Pitfall 5, and both were proven by execution, not argument. They are first because a roadmap that does not answer them will ship a regression the milestone's own blast-radius gate was written to prevent.

**The counter-argument put to me was tested, not repeated.** The milestone's answer to "the `ff_ratio` read-back is a false-PASS detector, so it must stay unconditional" is that a verify follows every write in the same cycle and a near-all-`0xFF` device cannot pass a verify against a generated pattern. **That reasoning is correct as far as it goes** — see Pitfall 3, where I test it against a real counter-case and find the argument sound but *under-scoped*: it holds for the write step, does not hold for the verify step's own read-back on a `--fast` run, and says nothing about the two consequences that actually bite (Pitfalls 1 and 2), which are not about diagnostic power at all.

---

## Critical Pitfalls

### Pitfall 1: Gating the fingerprint read-back re-keys `dedup_fingerprint` on every passing run — the milestone's own blast-radius gate, broken by the milestone's own feature

**MEASURED. This is the single most important finding in this document.**

**What goes wrong:**

`dedup_fingerprint` hashes, per step, the literal string `f"{result.op}={result.verdict}:{cls}"` where `cls = result.fingerprint.classification if result.fingerprint else ""` (`firestarter_app/firestarter/diagnostic_report.py:212-214`).

`classify_fingerprint` has exactly **four** buckets and **no "clean match" bucket** (`chip_test.py:138-141`, `:194-259`). A perfect read-back — `bad = 0`, `ff_ratio` far below the 0.98 threshold, no bit clustering, not divergent — falls all the way through to the `indeterminate` fallback. I ran it:

```
perfect-match classification -> 'indeterminate'  bad=0  ff_ratio=0.0039
```

So **today, on a passing full-device run, the write and verify steps each carry `classification="indeterminate"`, and that string is inside the hash.** Gating the read-back on `not all(outcomes)` makes `result.fingerprint` `None` on exactly those runs, so `cls` becomes `""`, so the canonical string changes, so the hash changes. Measured on a six-step SST27SF512-shaped result set:

```
dedup today (fingerprint attached on pass): 4dc282a5d596
dedup after R2 (no fingerprint on pass)  : 60a031573aab
BYTE-IDENTICAL? False
```

Every previously-filed *passing* report now sits in a different dedup group from every future passing report of the same chip. `count_agreeing` (`tools/parse_devtest_issue.py:164-183`) groups saved issue bodies by this embedded value and never re-hashes, so the N≥2 cross-report agreement signal is **reset to 1 for every chip that has ever passed**, silently, at the moment the change lands.

**Why it happens:**

The milestone inherited its blast-radius reasoning from Backlog 999.36, whose analysis is correct *for 999.36*: "Not one field in Class A, B or D is in that hash." That statement is about the **report schema** change. Backlog 999.43 (the sequencing work) is a **data** change to a field that *is* in the hash. Nobody re-ran the gate against R2 because the gate was written for a different feature and then quoted forward into a milestone that merged both. PROJECT.md:95-99 states the gate in the schema-work's terms ("Not one field being added, filled or deleted is in that hash today") — which is true and irrelevant to the change that breaks it.

**How to avoid:**

Decide the semantics explicitly, in a phase that lands *before* any sequencing change:

1. **Preferred:** give `classify_fingerprint` a fifth, honest bucket for `bad == 0` (call it `match`), emit it on the *cheap* path without any read-back — the verify already proved equality — and hash *that*. This costs nothing, keeps a non-empty `cls` on every passing run, and removes the `indeterminate`-on-a-perfect-match absurdity the project already recorded as MEASURED-SUPERSEDED in `tests/test_chip_test.py:2707-2733`. It still re-keys history once, but for a reason you can defend and describe in the issue tracker.
2. **Or:** keep the hash input stable by making `dedup_fingerprint` substitute the historical string when the read-back was skipped — i.e. the hash reads a *plan-shape* fact, not an *execution* artifact. Ugly, but it is the only option that is genuinely byte-identical.
3. **Never:** land R2 and discover this from a community report that two identical passes no longer agree.

Whichever is chosen, the phase must ship a **pinned-hash regression test**: a frozen list of `(result-shape, expected 12-hex)` pairs covering pass/fail/marginal/`--fast`/uv-slot/full-device, asserted byte-for-byte. The project has this discipline already (quick tasks 260821-wna and 260822-aq6 both reasoned about it) but it lives in prose, not in an assertion.

**Warning signs:**

- Any plan that says "dedup is unaffected because no *field* changed" — the hash reads a *value*, and R2 changes a value.
- A test suite that passes while no test constructs a **passing** run's dedup fingerprint. Grep: the existing dedup tests exercise failure shapes.
- `count_agreeing` returning all-1 counts on a corpus where it used to return 2s.

**Phase to address:** A **dedup/ladder invariance harness phase, sequenced FIRST (suggested 174)**, before any sequencing or schema change. It is the gate every later phase is measured against, and a gate authored after the content it guards is the project's own documented anti-pattern (`reference_gate_authored_before_content_can_be_unreachable`).

---

### Pitfall 2: The same gating silently flips the promotion ladder from "none" to "community-reported"

**MEASURED. Second-order consequence of Pitfall 1, in a different mechanism, with a different blast radius.**

**What goes wrong:**

`build_db_diff` routes disposition on `has_indeterminate_fingerprint` (`diagnostic_report.py:304-312`): any step carrying `classification == "indeterminate"` forces `inconclusive` / `_LADDER_NONE`. Because a perfect match *is* `indeterminate` (Pitfall 1), **today an all-OK non-SDP run can never reach `community-reported`.** Remove the read-back on pass and it can. Measured:

```
today (unconditional read-back)    disposition='inconclusive -- needs N>=2 agreement (advisory)' ladder=''
after R2 (gated)                   disposition='suggests: candidate for community-reported (advisory)' ladder='community-reported'
```

A performance change therefore moves chips onto the promotion ladder. That is squarely in Phase 114 GRAD-01's neighbourhood — the no-auto-graduate lock — and it is being made as a side effect of a change whose stated goal is "run no operation whose result is empty by construction."

**Why it happens:**

The `indeterminate`-on-a-perfect-match behaviour is an emergent property of two shipped mechanisms meeting, discovered and recorded during v1.30 Phase 134 (`tests/test_chip_test.py:2707-2733`, explicitly labelled "SECOND, DEEPER MEASURED FINDING" and "MEASURED-SUPERSEDED"). It is documented in a *test docstring*. Nobody planning a sequencing change reads that docstring, because the change is not about the ladder.

**How to avoid:**

- Treat the ladder outcome as a **first-class success criterion of the sequencing phase**, not a side effect: state, before implementation, whether an all-OK run *should* reach `community-reported`, and make that the assertion.
- If the answer is "yes, and it always should have been" (which is defensible — `indeterminate` on a bit-perfect compare is noise, not a finding), then say so publicly, because it changes what the triage skill and any human reader infer from a report.
- Pin `build_db_diff`'s output for the all-OK non-SDP shape in the same invariance harness as Pitfall 1. Note the AT28C256 case is *not* affected — its SDP leg attaches fingerprints in every arm and keeps forcing `_LADDER_NONE` — so a test that only exercises AT28C256 will not see this.

**Warning signs:**

- The ladder assertion at `tests/test_chip_test.py:2752` (`assert db_diff.ladder_state == ""`) turning RED, and someone "fixing" it by editing the expectation without adjudicating what it means.
- A chip appearing at `community-reported` in a report and nobody being able to say which change put it there.

**Phase to address:** Same invariance harness phase (suggested 174) for the pin; the adjudication belongs to the **conditional-diagnostics phase (suggested 175)** as a named decision, not a discovery.

---

### Pitfall 3: An oracle cheaper than the diagnostic it gates covers fewer fault modes than the diagnostic — and here the gap is narrow but real

**REASONED from measured code. This is where the milestone's counter-argument gets tested.**

**What goes wrong:**

The general shape: you gate an expensive diagnostic D on a cheap oracle O, on the argument that "O fails whenever D would have found something." The failure mode is that O's fault-mode set is a strict *subset* of D's, so faults in `D \ O` become invisible — and they become invisible **silently**, because the run reports PASS and nothing records that D did not execute. Functional-safety practice frames exactly this as diagnostic coverage against an enumerated failure-mode set; the enumeration is the work, and skipping the enumeration is the mistake.

For this project the specific question is: does `verify` cover everything the fingerprint read-back covers, on a passing run?

**The project's argument is sound for the write step.** `verify_eprom` streams the same expected buffer host→device and the firmware compares byte-for-byte. A near-all-`0xFF` device cannot pass a verify against `generate_pattern(start, length)`, so the `ff_ratio ≥ 0.98` blank/contact false-PASS bucket genuinely cannot fire on a run where verify passed. That is not hand-waving; it is arithmetic, and I could not construct a counter-case.

**But the argument is under-scoped in three places the milestone does not currently name:**

1. **The verify step's own read-back.** `_dispatch_multi_run` attaches a fingerprint for `OP_VERIFY` as well as `OP_WRITE` (`chip_test.py:3100`). For that step, "a verify follows in the same cycle" is *the step itself* — there is no second, independent oracle. Gating it on `not all(outcomes)` is still fine (a passing verify already proved equality on-device), but the justification is different: it is "the firmware already compared," not "a later step will catch it." Conflating the two justifications in one gate is how the SDP leg gets gated by accident later.
2. **`--fast` (`runs=1`, `allow_single_run=True`).** With one run, `repeat_divergent` is `None`, no read divergence is computed, and there is exactly one verify. The safety margin the project is relying on is thinner on the mode the community is most likely to run. This does not break the argument, but it means the structural test must cover `--fast` plans, not just the default policy.
3. **The `write-inhibited` SDP-leg arm.** `_dispatch_sdp_leg` attaches a fingerprint in *every* arm including the arm where a write is *expected* to be blocked — there, "OK" means "the write did not take," and the read-back *is* the oracle. R1/R2 must be structurally incapable of reaching that code path.

**Separately: R1 and R2 contradict each other on the same call site.** The seed's R1 says "Any place the engine reads the whole device back to compare it against a buffer it already holds is a verify. **This applies to the fingerprint read-backs.**" R2 says the fingerprint read-back should *stay a read-back*, merely conditional. Read literally, R1 converts the diagnostic into an oracle and destroys the mismatch distribution `classify_fingerprint` exists to compute. The cost-model note resolves the tension correctly ("Verify decides; a read-back diagnoses; the read-back only needs to run when verify says something is wrong") but the seed does not. A planner working from the seed alone will implement the destructive reading.

**How to avoid:**

- Write the **fault-mode table** before the code: rows = the four `classify_fingerprint` buckets plus "false PASS via undriven bus"; columns = "caught by verify?", "caught by read-back?", "caught by blank-check?". Any row where the read-back is the only Yes is a row the gate must not suppress. This is a half-page artifact and it is the difference between a defensible gate and a hopeful one.
- Make the structural test assert the **dependency**, as the milestone already intends: over `derive_plan` output, in the shape of `tests/test_chip_test_sdp_leg.py:827`'s `test_shipped_ops_never_reach_sdp_arm` — every `OP_WRITE`/`OP_WRITE_PARTIAL` step must be followed, in the same cycle, by an `OP_VERIFY` over the same region. Make it fail on a hand-built counter-plan (a plan with a write and no verify), or it proves nothing.
- Amend the seed's R1 sentence in the same phase. A rule that contradicts itself in the artifact the planner reads is a defect in the artifact.

**Warning signs:**

- A plan that cites "verify covers it" without naming *which* fault modes.
- The structural test passing on the shipped plans but never having been shown to fail on a counter-plan.
- Any diff that touches `_dispatch_sdp_leg` while implementing R1/R2.

**Phase to address:** **Conditional-diagnostics phase (suggested 175)**, with the fault-mode table as a named deliverable and the counter-plan test as a non-vacuity leg.

---

### Pitfall 4: Skipping the diagnostic silently removes it from the record — a PASS that skipped D looks identical to a PASS that ran D

**REASONED from measured code.**

**What goes wrong:**

Today every passing full-device run emits `fingerprint: "indeterminate"` — a value that at least proves the read-back happened. After gating, it emits `fingerprint: null`. But `null` is *also* what a step that never had a fingerprint emits (`id`, `read`, `erase`, `blank-check`, and any write whose read-back returned `b""` because the chip was absent). **Three very different situations collapse onto one JSON value**, and one of them is the project's own documented absent-chip false-green history (`_read_region` returns `b""` on any error and never raises, `chip_test.py:2739-2743`).

So after the change, a reviewer looking at a filed issue cannot distinguish: (a) the read-back was skipped because everything passed, (b) the read-back ran and produced nothing because the chip was not making contact, (c) this op never had a fingerprint.

**Why it happens:**

Skipping work is modelled as "produce nothing" rather than "produce a record that says the work was skipped and why." It is the cheapest implementation and it is the one that destroys the audit trail.

**How to avoid:**

Emit the *reason*, not the absence. Since the milestone is already bumping the schema and already adding fingerprint siblings (`total`/`bad`/`bad_pct`/`evidence`), add a sibling that states the gate outcome — e.g. `fingerprint_source: "skipped: all runs passed" | "read-back" | "unavailable: empty read"`. This is the same discipline the project applied to `run_count` in schema 1.7 ("the number reached NO consumer outside the test suite... it is now stated on every disclosure surface"), and it is the cheapest possible insurance against Pitfall 3 being wrong in a way nobody notices for six months.

Note the pleasing consequence: this key also solves Pitfall 1 if the gate outcome is what gets hashed, and it makes the R3 sampling provenance (Pitfall 6) representable in the same idiom.

**Warning signs:**

- A schema-1.8 report where you cannot answer "did this run do a read-back?" from the JSON alone.
- The word "skipped" appearing only in a code comment.

**Phase to address:** **Report schema phase (suggested 180)** owns the key; the **conditional-diagnostics phase (suggested 175)** owns populating it. They must not be separated by a release.

---

### Pitfall 5: The UV blank-check skip does not stop a UV part failing — the standalone blank-check step still reports BAD and still aborts the second cycle

**MEASURED from source. This falsifies a target-feature claim in PROJECT.md:78-83.**

**What goes wrong:**

PROJECT.md says "**UV parts stop failing for the tool's own blank check** ... Pass `FLAG_SKIP_BLANK_CHECK` on `uv-slot` writes." That fixes the *write-init* pre-flight inside the firmware. It does not touch the **plan's own standalone `blank-check` step**, which is a separate op that `derive_plan` puts in every UV plan (`chip_test.py:658-678`; confirmed in the cost model's per-chip table: `m27c512` → "blank-check before write").

Trace the second run of a used UV part through HEAD:

1. `_run_step` → `operator.check_eprom_blank(...)` → `False` → `StepResult(verdict=VERDICT_BAD, error_code=MSG_ERR_NOT_BLANK)` (`chip_test.py:2527-2542`).
2. In the cycle loop, `if result.error_code is not None: hardware_refused = True` → after the cycle, `break` (`chip_test.py:1568-1570`). **Cycle 2 never runs.**

   **FALSIFIED (Phase 179, `179-02-PLAN.md`).** MEASURED against the live tree: for a UV plan the
   `blank-check` step sits at index 2, OUTSIDE the cycle block — the cycle block is `(3, 6)` for
   `m27c512`, `am27c020` and `tms27c512` — and `run_plan`'s per-step dispatch path has no
   `hardware_refused` mechanism at all; that name does not exist anywhere in `chip_test.py`. The
   abort this step describes never happened via the blank-check step. The consequence for the plan
   was unchanged — both defects (the write-init pre-flight refusal AND the standalone blank-check's
   `BAD` verdict) still had to be fixed, and Phase 179 fixed both — but the *mechanism* named here is
   wrong: the pre-179-01 abort came from the WRITE step's own firmware refusal
   (`WriteInitPreflightChip`'s write-init pre-flight, `eprom.cpp:143-145`), not from this blank-check
   step tripping a cycle-abort flag that does not exist. See `179-MEASUREMENT.md` §5 for the
   full-run step table proving the blank-check step now adjudicates `SKIPPED` with its finding
   (`reason`, `error_code=176`) intact, and `179-01-SUMMARY.md` / `.planning/MILESTONES.md`'s
   `RK-174-04-p179-uv-blank-check-abort` row for the corrected provenance.
3. `run_count` for the destructive ops collapses to 1 → `repeat_policy_tag` returns the degraded tag (`chip_test.py:1094-1097`) → `dedup_fingerprint` gets a `fast`-shaped discriminator on a run the operator did not ask to be fast.
4. `overall_verdict` is FAIL-dominant on any BAD (`submit.py:140-152`) → the submit prompt still offers **`[dev test] AM27C020 — FAIL`**.

So after the planned host-half fix, the write and verify steps go OK — and the run still reports FAIL, still aborts after one cycle, and still files against the chip. **The milestone's stated outcome is not reached by its stated change.**

**Why it happens:**

Backlog 999.44's root-cause analysis is precise about the *firmware* call site (`eprom_internal_write_init_body` → `mem_util_blank_check`) and correct that the host flag suppresses it. It simply does not follow the *other* caller — the plan's own blank-check op — because that one is not a defect, it is working as designed. The design is what needs adjudicating.

**How to avoid:**

Decide, explicitly, what a non-blank UV part's `blank-check` step *means*, and make it stop being a chip verdict:

- The seed already gives the right frame: "blankness is an operator-actionable **finding**." A finding is not a FAIL. The natural shape is a distinct verdict or an `NA`-with-reason for the UV+non-blank case: *the part is not blank, this is expected on a re-tested UV part, the slot mechanism handles it*.
- Whatever verdict is chosen, it must **not** set `error_code`, or `hardware_refused` still aborts cycle 2 and the run silently degrades to single-run — which then re-keys the dedup hash for a second, independent reason.
- The regression test the backlog names ("a UV part holding data outside the target slot must accept a slot write") is necessary but **not sufficient**. The test that proves the milestone's claim is: *a UV part holding data outside the target slot completes a full two-cycle run with `overall_verdict == "PASS"`.* Assert the title, not the write.

**Warning signs:**

- A plan whose success criterion is "the write step reports OK" rather than "the run reports PASS."
- `run_count == 1` on a run invoked without `--fast`.
- Bench evidence showing write/verify green and blank-check red, being read as success.

**Phase to address:** **UV slot phase (suggested 178)**, whose success criterion must be the *overall verdict*, not the write step. It has a hard dependency on the **fault-attribution phase (suggested 179)** for the verdict vocabulary — sequence 179 before or with 178.

---

### Pitfall 6: Gating the skip on the region *policy* rather than on the monotonicity *witness*

**REASONED from measured code.**

**What goes wrong:**

The safety argument for `FLAG_SKIP_BLANK_CHECK` is that the write is monotone: `mask_write_pattern` computes `P = C & D` per byte (`chip_test.py:2057-2073`), which can only clear 1→0. That property comes from `C` being a **real probe read** of the exact target region. Today the uv-slot branch of `_resolve_write_target` guarantees it: the block read is checked for exact length and a short read `continue`s to the next block rather than assuming blank (`chip_test.py:2842-2846`), and the returned target carries `masked=True`, `current_source="probe read"`, and the actual `current` bytes.

The trap is implementing the flag as `if step.region_policy == REGION_POLICY_UV_SLOT: flags |= FLAG_SKIP_BLANK_CHECK`. Policy and monotonicity are **currently** coextensive, but they are not the same predicate — and the docstring at `chip_test.py:2769-2772` shows they were *not* coextensive one design iteration ago (the removed "chip reported blank AND `full_device_permitted` → mask taken as all-`0xFF`, the device is never read again" branch). That branch, if it ever returns, is a uv-slot write with an **assumed** current, and applying the skip to it means an unmasked-in-effect write with no blank check and no probe. On a UV part that is unrecoverable without a UV eraser.

**How to avoid:**

- Derive the flag from the **witness**: `target.masked and target.current is not None and target.current_source == "probe read"`. Never from the policy string, never from `is_uv`.
- Add the fail-closed assertion in the emitter: refuse to set the flag if the witness is absent, and make *that* a test with a hand-built unmasked uv-slot target.
- This mirrors a pattern the codebase already uses deliberately — `coverage_tag` "locates the write step STRUCTURALLY, via `result.write_target is not None`... must never compare `result.op` against an op-name constant" (`chip_test.py:1115-1117`).

**Warning signs:**

- The literal string `"uv-slot"` or `REGION_POLICY_UV_SLOT` appearing in the flag-computation expression.
- The flag being set anywhere other than the one function that already maps wire flags (`build_flags`, `eprom_operations.py:261-300`, whose own comment insists every wire flag bit stays mapped in one place).

**Phase to address:** **UV slot phase (suggested 178).**

---

### Pitfall 7: The host-only skip makes `dev test` validate a path the shipped product cannot use

**REASONED. This is the scope decision at PROJECT.md:104-108, stated as a consequence rather than a boundary.**

**What goes wrong:**

The milestone knowingly ships 999.44's host half without its firmware half. After that, `firestarter dev test m27c512` succeeds on a non-blank part by passing `FLAG_SKIP_BLANK_CHECK`, while `firestarter write foo.bin -a 0x3FF00` on the identical part is still refused by the identical firmware. The harness whose entire purpose is "validate that the firmware, host and database work for this chip type" now passes by using a flag the user-facing command does not set.

That is not merely incomplete — it inverts the harness's meaning for this class of part. A community `PASS` on a UV chip will no longer imply that a user can write that chip.

**Why it happens:**

The scope boundary was drawn on the *repository* axis (host only, no dual-repo lockstep) rather than the *semantic* axis (does the harness still represent the product?). The backlog itself rejected the host half alone on exactly this ground, and the milestone takes it knowingly — which is the right call for a host-only milestone, but only if the consequence is *disclosed in the artifact*, not just in the planning file.

**How to avoid:**

- Emit the divergence in the report. If the run set `FLAG_SKIP_BLANK_CHECK`, the report must say so — a `plan.flags` or `write_flags` key alongside the already-planned `plan.is_uv`. Otherwise a triager reading a UV PASS has no way to know the harness took a shortcut the product does not take.
- Keep the firmware half named and open in `MILESTONES.md` carry-forward with the literal product-level symptom (`firestarter write -a` on a non-erasable part holding data anywhere is refused), so it is findable by the symptom a user would report, not only by a backlog number.

**Warning signs:**

- A UV `PASS` report that contains no evidence that a flag was set.
- The phrase "host half is sufficient" in any plan.

**Phase to address:** **UV slot phase (suggested 178)** for the disclosure key; **report schema phase (suggested 180)** for its serialization. Both, or neither.

---

### Pitfall 8: Changing `duration_s`'s meaning in place, when the only version marker is accepted by presence

**MEASURED consumer surface + HIGH-confidence external consensus.**

**What goes wrong:**

External schema-evolution consensus is unambiguous and unanimous across the sources I checked: renaming a field, deleting a field, **and changing what an existing field means** are all breaking changes, and the standard mitigation is to *never redefine in place* — add a new key with the new semantics, populate both through a transition, migrate consumers, delete the old key later.

The milestone plans to redefine `duration_s` in place (sum-across-cycles → per-operation cost) and add `elapsed`. The version marker that would let a consumer disambiguate is `schema_version` — and both `[dev test]` parsers accept it **by presence only, never by value** (a live fixture carries `"9.9-future"`, `tests/test_parse_devtest_issue.py:138`). So there is no consumer anywhere that can tell a 1.7 `duration_s` from a 1.8 one. The two numbers land under the same key, in the same public issue tracker, and differ by a factor of the cycle count.

**It gets worse from an interaction.** `duration_s` is stamped around the *whole step* (`chip_test.py:2751-2782`), which today includes the fingerprint read-back. R2 removes that read-back from passing runs. So in this one milestone `duration_s` changes for **two independent reasons at once** — a semantics change and a workload change — and a reader comparing a 1.7 report to a 1.8 report cannot attribute the difference to either, let alone to the chip.

**A third defect in the same field, unaddressed:** "per-operation cost" is not well-defined by the current instrumentation. `_aggregate_cycle_results` sums per-cycle stamps, each of which covers one operator call; but on the non-cycle path a single stamp covers `runs` calls. Computing per-op as `total / run_count` averages a cold first call (which includes a serial connect, `find_and_connect`) with a warm second — and on a `marginal` step it averages a *fast failing* run with a *slow passing* one, producing a number that describes neither. The verify path makes this worse, not better, because verify early-returns on first mismatch: a failing verify is genuinely faster.

**How to avoid:**

- **Do not redefine `duration_s` in place.** Add `duration_op_s` (or `op_cost_s`) with the new meaning, leave `duration_s` carrying its historical sum, and delete `duration_s` in a later schema version once the tracker corpus has turned over. This costs one key and removes the entire class of problem. If the operator's rule ("a field that can carry real data gets populated with real data") is read as forbidding this, note that `duration_s` is not carrying *fake* data — it is carrying a real sum under a name a reader misreads. That is a naming defect, and the standard remedy for a naming defect is a new name.
- If it is redefined in place anyway, then **make at least one parser gate on the version**, so the ambiguity is detectable somewhere. A version field nobody checks is decoration.
- Instrument per-operation cost by **stamping inside the operator-call loop** and emitting the per-call list (or min/median), never by dividing a step total by a run count. State which statistic it is in the key name.

**Warning signs:**

- A plan that says "the schema bump documents the change" without naming the consumer that reads the bump.
- Any arithmetic of the form `total / run_count` in the timing path.
- A `duration_op_s`-shaped number that is smaller on a failing verify than a passing one, with nothing explaining why (it is correct — early return — but it will read as a bug forever if unstated).

**Phase to address:** **Report schema phase (suggested 180).** The version-gating decision must be made in that phase, not deferred.

---

### Pitfall 9: Deleting `voltage.vpp_mv` breaks a documented skill consumer, and the fallback it will reach for means something else entirely

**MEASURED. This is a genuine integration defect the field audit did not surface.**

**What goes wrong:**

Backlog 999.36 Class B justifies deleting `voltage.vpp_mv`/`vpe_mv` on the ground that "no assignment exists anywhere in the app." True at HEAD. But two things follow that the audit did not chase:

1. **The frozen schema-1.2 fixtures carry real values** — `"vpp_mv": 11800`, `"vpe_mv": 13700` (`.claude/skills/devtest-triage/fixtures/dev-test-at28c256-null-identity.md:87-88` and the populated-identity sibling). So the field was populated at some point and **the already-filed issue corpus contains real readings under it**. Deletion is a forward-only change over a corpus where the key is sometimes meaningful — the parsers must keep tolerating it (the note gets this right) *and* consumers must not read its future absence as a measurement of zero.
2. **There is a live documented consumer.** `.claude/skills/devtest-triage/SKILL.md:375` instructs the triager, in its datasheet-comparison table, to compare the report's `vpp_mv` against the chip's program voltage: *"`vpp_mv: 13500` | MISMATCH — neither the program nor the erase voltage."* That is an LLM-driven skill being told to read a key that is about to disappear. The predictable failure is that it falls back to the nearest key with the same name — `chip_database.json`'s `electrical.vpp_mv` — which on 5V-only families (`flash_nor_unlock`, `flash_5v_page`, `sram`, `eeprom28c`) encodes the **WP-pin voltage, not programming VPP**. `tools/check_dispatch.py:60-94` says so explicitly and says that comparing it as programming VPP "would produce false positives on every AMD/SST flash chip."

So a deletion justified as "removing a dead field" can convert a triage skill into a machine that mis-blames every 5 V flash part.

**How to avoid:**

- Treat the two skills (`devtest-triage`, `devtest-rootcause`) as **first-class consumers in the deletion phase**, with their prompt text updated in the same commit as the schema change. The project already knows skill/source drift is a real class (`feedback_skills_must_own_their_scripts`); this is the prose version of it.
- Grep the skills for **every** key being deleted or re-meant, not just the ones with Python readers. `chip_id_actual` is already known to have two script consumers that improve for free; `vpp_mv` has a *prose* consumer that breaks.
- In `SKILL.md`, replace the `vpp_mv` row with the keys that are actually populated — `vpp_before_mv` / `vpp_after_mv` — and state in the same row what they do and do not prove (see Pitfall 10).

**Warning signs:**

- A deletion plan whose consumer sweep covered `.py` files only.
- A triage comment quoting a VPP number on a report that has none.

**Phase to address:** **Report schema phase (suggested 180)**, with a named consumer-sweep task covering `.claude/skills/**` markdown as well as code.

---

### Pitfall 10: Auto-classifying rig faults from a sensor that cannot see the rig fault

**MEASURED against firmware behaviour recorded in project reference memory. This is the highest-stakes pitfall in change #3.**

**What goes wrong:**

The motivating community report is gh#23: *"the first one didn't have VPP correctly hooked up."* The obvious implementation of "never file a rig fault as a chip verdict" is to classify on the voltage sampler: if `vpp_before_mv` is low or absent, call it a rig fault.

**The sampler cannot see that fault.** `sample_vpp_mv` issues `COMMAND_READ_VPP` → `hw_read_voltage`, which sets `CTRL_VPP_REGULATOR_ENABLE` (and the drop-enable bit) and **none of the socket-routing bits** (`CTRL_VPP_A9_ENABLE`, `CTRL_VPE_ENABLE`, `CTRL_VPP_P1_ENABLE`). It measures the **boost-regulator rail via ADC**; the high voltage never reaches the socket pins. That is why the monitors are safe to run with a chip seated — and it is exactly why they are blind to "VPP not hooked up to the chip." A rig with a disconnected VPP jumper reports a perfectly healthy `vpp_before_mv: 11800`.

So a classifier built on that signal will report **"rig OK"** on precisely the run that motivated the milestone, and its confidence will be entirely fabricated. Worse, it will be *right* often enough elsewhere to be trusted.

**Why it happens:**

The field name says `vpp`, the value is plausible, and the physical distinction between "the rail is up" and "the rail reaches the socket" lives in firmware control-register bits nobody reads while writing a host-side classifier.

**How to avoid:**

- **Enumerate, per proposed cause label, the signal that carries it and what that signal physically measures.** For "VPP not connected," the honest available signal is *not* the sampler — it is the `blank/contact` fingerprint bucket (`ff_ratio ≥ 0.98`, an undriven bus reading all-`0xFF`) plus a floating chip-ID (the project's recorded `0x303` signature). Note the tension with Pitfall 3: the fingerprint bucket is the very diagnostic being made conditional, so **the fault-attribution feature depends on the read-back that the sequencing feature is gating away.** They must be planned as one thing. On a failing run the gate lets the read-back through, so this works — but only if the gate is `not all(outcomes)` and nothing narrower.
- Where no honest signal exists, emit **`unknown`**, not a guess. The external triage literature is consistent that classifiers need an explicit unknown bucket and per-class measured accuracy, and that the dangerous direction is labelling a real defect as environmental — the Firefox case, where developers dismissing flaky failures produced a documented rise in user-visible crashes. Applied here: a classifier eager to say "rig fault" will start hiding real chip and firmware defects from the community, which is the same disease as today's "blame the chip," pointed the other way.
- **Never let auto-classification silence the report.** The fix for "a tool fault is filed as a chip verdict" is to change the *title and disposition* (`[dev test] AM27C020 — INCONCLUSIVE (harness)`), never to suppress the submit prompt. Suppression converts a visible wrong verdict into an invisible missing one.
- Give every label a **human override path**. The project's existing shape for this is the advisory `db_diff` — "read-only advisory triage text, never a DB write." Follow it.

**Warning signs:**

- Any classifier reading `vpp_before_mv` / `vpe_before_mv` as evidence about the socket.
- A cause taxonomy with no `unknown` member.
- A `--submit` path that can decide, on its own, not to offer to file.
- A label whose accuracy has never been measured against the six open community issues (#21, #23, #28, #31, #45, #50) — which are a ready-made labelled evaluation set and should be used as one, even though replying to them is out of scope.

**Phase to address:** **Fault-attribution phase (suggested 179)**, sequenced **after** the conditional-diagnostics phase (it consumes the fingerprint the gate controls) and **before or with** the UV slot phase (which needs its verdict vocabulary — Pitfall 5).

---

### Pitfall 11: Bit-structured sampling changes the read step's own verdict source, and a hole-padded sample cannot be diffed against a full read

**MEASURED from source. Two concrete implementation traps in R3, plus one cost trap.**

**What goes wrong:**

Three separate things, all in `_dispatch_read` (`chip_test.py:2626-2671`):

1. **Verdict source.** `last_ok` is the return value of the **last** run, and the step's verdict is `OK if last_ok else BAD`. Replace run 2 with a 2560-byte sample and the step's pass/fail oracle is now a sample read, not a full-device read. A device that fails a full read only outside the sampled blocks now reports OK. The verdict must stay anchored to the full read — either keep run 1 as the verdict source explicitly, or `all()` the outcomes, and assert it.
2. **Hole padding.** A region/sample read produces a **hole-padded file whose real bytes sit at their absolute offsets** — `_read_region`'s own docstring records this ("`eprom_operations._write_to_file`'s `file_handle.seek(address)`... slicing anywhere else would silently read zero-padding"). Feeding such a file straight into `_diff_offsets(run_bytes[0], run_bytes[1])` compares the full read against zero padding everywhere outside the sample and reports catastrophic false divergence. The comparison must be assembled block-by-block against the matching slices of run 1.
3. **Cost.** A ten-block bit-structured sample is **ten separate `read_eprom` calls**, and `EpromOperator.comm` is torn down after every call (`eprom_operations.py:547`), so it is **ten connects** where the full read was one. The project's own honesty ledger states per-connect cost is **unmeasured**. If a connect costs more than ~0.5 s, R3 is *slower* than the full read it replaces on a 64 KiB part, and the milestone's headline saving is negative for this rule. **R3 is therefore blocked on the R4 measurement, not merely informed by it.**

**How to avoid:**

- Measure a connect **first**, as its own deliverable, before scoping R3 or R4. PROJECT.md:112-113 already commits to this ("must be measured before it is scoped") — hold that line even under schedule pressure, because R3's sign depends on it.
- Pin the read step's verdict source in a test that fails if it moves to the sample.
- Build the sample comparison from explicit `(offset, block)` pairs, never from whole-file bytes.
- Carry sampling provenance into the exported `divergence` metric (see Pitfall 12).

**Warning signs:**

- A `divergence` record with `cmp_len` far below `memory-size` and nothing saying why.
- A read step that goes green on a part that fails a plain `firestarter read`.
- Any R3 timing claim quoted from the model rather than measured — the model's rates come from **one** log, on **one** Leonardo, against **one** 64 KiB `0x07` part, and the note's own correction shows read rate varies ~24% by protocol.

**Phase to address:** A **connect-cost measurement phase (suggested 176, before sampling)**, then the **sampling phase (suggested 177)**. If the measurement says R3 is net-negative, cutting R3 is a success, not a failure.

---

### Pitfall 12: Exporting `divergence` and the fingerprint counts as exact numbers when the change also makes them estimates

**REASONED from the two features' interaction.**

**What goes wrong:**

999.36 exports the read step's `divergence` (`cmp_len`, `bad`, `pct`, `first_offset`) and the fingerprint's `total`/`bad`/`bad_pct` for the first time. 999.43 R3 simultaneously converts `cmp_len` on a passing run from a whole-device count into a **sampled-subset count**. Ship both in one milestone and the report gains, in the same release, a field that looks like an exact whole-device measurement and is not.

`bad_pct: 0.005%` over `total: 65536` and `bad_pct: 0.005%` over `total: 2560` are radically different statements about a chip, and the second one — an estimate over 3.9% of the device — will be read as the first by every human and every skill that consumes it.

**How to avoid:**

- Export the *scope* alongside the *number*, always: `total`, plus what `total` was drawn from. Pitfall 4's `fingerprint_source`-style key generalises here.
- Sequence the schema phase **after** the sampling phase so the schema knows what it is describing, or hold `divergence` export back until sampling is settled. Exporting an exact metric and then quietly making it an estimate two phases later is worse than either alone.
- State the estimator's blind spot in the report, not just in the seed: a fault confined entirely to unsampled bytes is missed on the first pass.

**Warning signs:**

- Two different `total` magnitudes for the same chip across two reports, with no key explaining the difference.
- A triage comment computing a bad-bytes count from `bad_pct × memory-size`.

**Phase to address:** **Report schema phase (suggested 180)**, sequenced after sampling (177).

---

### Pitfall 13: Canonical chip naming changes the issue title *and* the dedup input at the same time

**MEASURED.**

**What goes wrong:**

`dedup_fingerprint`'s first hash component is `ac.chip` (`diagnostic_report.py:211`), and `build_title` composes `[dev test] {chip} — {verdict} ({shorthash})` (`submit.py:155-165`). Switching from the operator's raw CLI token to the matched database `part_number` therefore changes **both** the title string and the hash — so every chip whose canonical name differs in case or punctuation from what testers have been typing gets a fresh dedup group *and* a title that no longer matches the tracker's existing issues for that part.

This is a third, independent re-keying path in the same milestone, alongside Pitfall 1 (fingerprint) and Pitfall 5 (`run_count`/`repeat_policy_tag`). Three re-keyings shipped together are indistinguishable from each other in the aftermath.

**How to avoid:**

- Measure the blast radius **before** implementing: for each chip with a filed `[dev test]` issue, compute `raw_token → part_number` and count how many actually differ. It may be near-zero (testers copy names from `firestarter list`), in which case this is free — but that is a measurement, not an assumption.
- Whatever the count, it belongs in the same invariance harness as Pitfall 1, and the three re-keying sources must be enumerated in one place in the milestone record so a future reader can attribute a group split to the right cause.

**Warning signs:**

- A plan treating canonical naming as a cosmetic title fix.
- Two open issues for the same physical part under different names after the release.

**Phase to address:** **Invariance harness phase (suggested 174)** for the measurement; **report schema phase (suggested 180)** for the change.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Gate the read-back on `not all(outcomes)` and accept the dedup re-key silently | R2 lands in a day; ~24% saving | Every chip's `count_agreeing` resets to 1 with no record of why; future group splits become unattributable | **Never silently.** Acceptable *only* as a declared, dated, one-time re-key with the cause named in `MILESTONES.md` |
| Gate the flag on `region_policy == "uv-slot"` instead of the mask witness | One line, reads naturally | A future unmasked uv-slot branch inherits a blank-check skip and can brick a UV part irrecoverably | Never — the witness form is the same line count |
| Redefine `duration_s` in place because "the schema bump documents it" | No new key; matches the operator's "no decoration" rule | Two incompatible meanings under one key in a public tracker, with no consumer able to tell them apart | Only if at least one parser is simultaneously made to gate on `schema_version` |
| Ship the sampled `divergence` export before the sampling design is settled | Both backlog items close in one milestone | An "exact" field silently becomes an estimate in a later phase of the same milestone | Never — order the phases instead; it costs nothing |
| Land the UV host half and call 999.44 done | Removes the loudest community complaint | The harness now passes on a path `firestarter write -a` still refuses; a UV PASS stops implying the product works | Acceptable **with** a `write_flags`-style disclosure key and the firmware half named as open |
| Take the seed's R1 literally and convert the fingerprint read-back into a verify | Biggest single saving in the model | Destroys `classify_fingerprint`'s input entirely; the four-bucket diagnostic becomes one mismatch address | Never — fix the seed's wording in the same phase |
| Quote the cost model's second-counts as expected outcomes | Clean-looking success criteria | Every rate is from one log, one Leonardo, one 64 KiB `0x07` part; read rate varies ~24% by protocol and Uno's 512 B buffer is unmodelled | Only as *directional* claims ("fewer ops"), never as numeric acceptance thresholds |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `.claude/skills/devtest-triage` (prompt-level consumer) | Sweeping only `.py` files for readers of a deleted key, missing `SKILL.md:375`'s instruction to compare the report's `vpp_mv` | Sweep `.claude/skills/**` markdown too; update the skill's table to `vpp_before_mv`/`vpp_after_mv` in the same commit, and state what those do *not* prove |
| `chip_database.json` `electrical.vpp_mv` | A triager falling back to the DB field after the report field is deleted — on 5V families it encodes **WP-pin voltage**, not programming VPP (`tools/check_dispatch.py:60-94`) | Name the collision explicitly in the skill text; forbid the substitution in prose the model will read |
| GitHub issue corpus (already-filed bodies) | Assuming a deleted key is absent everywhere — the frozen schema-1.2 fixtures carry real `vpp_mv: 11800` | Keep parsers tolerant forward AND backward; never read a future absence as a measured zero |
| `tools/parse_devtest_issue.py::count_agreeing` | Assuming it re-hashes and will self-heal after a dedup change — it reads the **embedded** value and never re-hashes | Any hash-input change is permanent for the historical corpus; plan for a one-time, declared split |
| `.claude/skills/devtest-rootcause/scripts/seed_debug_session.py` | Ignoring it because it only "improves for free" from `chip_id_actual` | Still re-run it against a 1.8 body; a key it iterates over changing shape is not free |
| Firmware (`FLAG_SKIP_BLANK_CHECK`) | Setting the bit outside `build_flags`, the one function that maps wire flags | Route through `build_flags`/`operation_flags`; `write_eprom`'s `operation_flags` is positional before `address_str` — pass it by keyword |
| The two `[dev test]` parsers | Relying on the 1.7→1.8 bump to disambiguate | They accept `schema_version` by **presence only** (a fixture carries `"9.9-future"`); the bump disambiguates nothing until someone gates on it |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Bit-structured sampling costs one connect per block | Read step gets *slower* on small parts despite reading 96% fewer bytes | Measure a connect first; batch blocks inside one session (R4) before enabling R3 | Immediately, on any part where 10 connects > 1 full read — i.e. plausibly at 64 KiB, certainly below it |
| Optimising the read path while `write` is 65% of a full-device run | Headline saving lands but operators still wait minutes | Keep the write path (per-byte VPE settle, firmware-side) explicitly out of scope and out of every claim | Already true today; the risk is a claim, not a regression |
| Model rates treated as acceptance criteria | Bench run misses the modelled figure; time spent explaining a model, not a defect | Success criteria in *operation counts* (a passing run performs 0 fingerprint read-backs), never in seconds | On the first non-`0x07` part, and on any Uno-class board |
| Verify's early return making failing runs faster than passing ones | A `duration_op_s` that is *smaller* on failure reads as an instrumentation bug forever | State it in the field's own description in the schema | The first time anyone compares a FAIL to a PASS |
| Folding `sample_vpp_mv` + `sample_vpe_mv` into one monitor read | −2 connects per write step, genuinely free | None — this is the safest item in the whole milestone | n/a; take it early as a confidence-builder |

## Security Mistakes

Not a security-sensitive domain in the usual sense; the analogous risk is **public disclosure quality**, because this tool files issues into a public tracker on a community member's behalf.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Filing `[dev test] <chip> — FAIL` when the fault is the tool's | Public, durable, wrong attribution against a manufacturer's part; the reputational failure mode the milestone exists to fix | Verdict vocabulary that can express "harness/rig" without suppressing the report (Pitfall 10) |
| Auto-classifier suppressing the submit prompt when it decides "rig fault" | A real chip or firmware defect never reaches the tracker — the Firefox flaky-dismissal failure mode | Classification changes the title and disposition, never the offer to file |
| New schema fields widening the PII surface | `evidence` dicts and per-op timings are new payload passing through the Phase-113 sanitizer | Re-run the sanitizer's tests against a 1.8 body; confirm every new key is sanitizer-visible |
| Report claiming a measured VPP the hardware never measured at the socket | A community member replaces a good chip on the strength of a fabricated voltage claim | Never present rail readings as socket readings; label them as rail measurements in the schema |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| A UV part still titled FAIL after the "UV parts stop failing" fix | The headline community complaint is unresolved while the milestone reports it as delivered | Success criterion is `overall_verdict == "PASS"` on a used UV part, not "the write step went OK" (Pitfall 5) |
| `fingerprint: null` meaning three different things | A reporter cannot tell "skipped, everything passed" from "chip not making contact" | Emit the reason, not the absence (Pitfall 4) |
| A faster run that quietly does less, with nothing saying so | Community trust in a validation tool depends on knowing what was validated | Every skipped operation is a stated, exported fact |
| `duration_s` meaning something different in two reports of the same chip | Reporters compare numbers and draw conclusions about their chip that are artifacts of a version bump | New key for new semantics (Pitfall 8) |
| Canonical naming splitting a part's issue history across two titles | Duplicate issues; a triager missing prior art | Measure the raw-token→`part_number` delta before shipping (Pitfall 13) |

## "Looks Done But Isn't" Checklist

- [ ] **Conditional read-back:** often missing the **passing-run dedup pin** — verify a frozen `(passing shape → 12-hex)` assertion exists and was seen to fail before it passed.
- [ ] **Conditional read-back:** often missing the **ladder assertion** — verify `build_db_diff` output for the all-OK non-SDP shape is pinned, and that `tests/test_chip_test.py:2752` was adjudicated rather than edited.
- [ ] **Structural write→verify test:** often missing **non-vacuity** — verify it fails on a hand-built plan with a write and no verify. The project has shipped an unreachable gate before; a RED that was never observed proves nothing.
- [ ] **Structural write→verify test:** often missing the **`--fast` / single-run plan** — verify it covers `allow_single_run=True`.
- [ ] **UV blank-check skip:** often missing the **standalone blank-check step** — verify a used UV part reaches `overall_verdict == "PASS"` and completes **two** cycles (`run_count == 2`, no `repeat_policy_tag`).
- [ ] **UV blank-check skip:** often missing the **witness gate** — verify the flag expression names `masked`/`current`, not `"uv-slot"`.
- [ ] **UV blank-check skip:** often missing the **product-divergence disclosure** — verify the report says a flag was set that `firestarter write` does not set.
- [ ] **Fault attribution:** often missing the **`unknown` bucket** and per-label accuracy against the six open issues used as a labelled set.
- [ ] **Fault attribution:** often missing the check that classification **never suppresses** the submit offer.
- [ ] **Fault attribution:** often missing the finding that the **voltage sampler reads the rail, not the socket** — verify no cause label is derived from `vpp_before_mv`/`vpe_before_mv` alone.
- [ ] **Sampling:** often missing the **verdict-source pin** — verify the read step's OK/BAD still derives from a full read.
- [ ] **Sampling:** often missing the **hole-padding** handling — verify the sample is compared block-wise, never whole-file.
- [ ] **Sampling:** often missing the **measured connect cost** that decides whether R3 is net-positive at all.
- [ ] **Schema 1.8:** often missing the **skill markdown sweep** — verify `SKILL.md:375`'s `vpp_mv` row was updated.
- [ ] **Schema 1.8:** often missing **backward parse of the frozen 1.2 fixtures** — verify both fixtures still parse and their `dedup_fingerprint` values are unchanged.
- [ ] **Schema 1.8:** often missing a **statement of scope** on `divergence`/`bad_pct` when sampling is on.
- [ ] **Milestone-wide:** often missing the **enumeration of every dedup re-keying source** shipped together (fingerprint gating, `run_count` collapse, canonical naming) in one place in the record.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Dedup re-keyed silently (P1) | **HIGH** — partly irreversible | Filed bodies carry the old hash forever and `count_agreeing` never re-hashes. Recovery is: publish the mapping (old shape → new hash) in the tracker, accept the one-time group split, and add the pin so it cannot recur. There is no way to retroactively merge groups. |
| Ladder flipped unnoticed (P2) | MEDIUM | `db_diff` is advisory and writes no DB, so nothing graduated. Re-adjudicate, correct the disposition text, re-triage the affected reports by hand. |
| Verify-only gate proved insufficient (P3) | MEDIUM | Revert the gate to unconditional for the affected op; the field is additive so no schema change is needed. Costs one release of speed. |
| UV part still FAILs after the fix (P5) | LOW if caught at bench, HIGH if caught by the community | Caught at bench: extend to the blank-check step's verdict. Caught publicly: a second wrong FAIL on the same part, on top of the one being apologised for. Bench-gate this one. |
| Blank check skipped on an unmasked write (P6) | **VERY HIGH** — physically unrecoverable | A UV part written with a non-monotone pattern needs a UV eraser and 20+ minutes, or is scrapped. Prevention only; there is no software recovery. |
| `duration_s` redefined in place (P8) | MEDIUM, permanent in the corpus | Add the correctly-named key retroactively in 1.9 and deprecate `duration_s`; the mixed-meaning bodies already in the tracker cannot be repaired. |
| `vpp_mv` deleted, skill mis-blames flash parts (P9) | LOW to fix, MEDIUM to undo | Correct `SKILL.md`, then re-triage every issue triaged in the window — the wrong comments are public. |
| Classifier mis-labels a real defect as rig fault (P10) | HIGH | Measure per-label accuracy against the six open issues *before* enabling; if it ships wrong, disable the label (keep `unknown`) rather than tuning it live. |
| R3 turns out net-negative on connects (P11) | LOW if measured first | Cut R3. The model already shows R1+R2 deliver roughly two thirds of the saving; dropping R3 is a legitimate outcome. |

## Pitfall-to-Phase Mapping

Phase numbers are **suggested** — v1.36 continues at 174 and the roadmap owns the numbering. What is not negotiable is the **ordering**, which is driven by real dependencies, not preference.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| P1 dedup re-key on pass | **174 — Invariance harness (FIRST)** | Frozen `(result-shape → 12-hex)` table covering pass/fail/marginal/`--fast`/uv-slot/full-device; each entry seen RED before green |
| P2 ladder flip | 174 (pin) + 175 (adjudication) | `build_db_diff` output pinned for the all-OK non-SDP shape; the decision written as a D-NN, single-line label (the coverage gate needs single-line bullets) |
| P13 canonical naming re-key | 174 (measure) + 180 (change) | Count of chips whose raw token differs from `part_number` across the filed corpus, stated as a number |
| P3 oracle coverage gap | **175 — Conditional diagnostics (R1/R2)** | Fault-mode table shipped as an artifact; `derive_plan` structural test proven to fail on a write-without-verify counter-plan; seed's R1 wording corrected |
| P4 skip is unrecorded | 175 (populate) + 180 (key) | A 1.8 report distinguishes skipped / ran / unavailable for every step |
| P11 sampling traps + connect cost | **176 — Connect-cost measurement**, then **177 — Sampling (R3/R4)** | A measured seconds-per-connect figure exists before 177 is scoped; read-step verdict source pinned; block-wise comparison asserted |
| P12 exact-vs-estimate export | 177 before 180 | `divergence`/`bad_pct` carry their scope; a sampled run's `total` is legible as sampled |
| P5 UV still FAILs | **178 — UV slot** (after/with 179) | A used UV part reaches `overall_verdict == "PASS"` with `run_count == 2` — bench leg, hardware-gated |
| P6 policy-vs-witness gate | 178 | Flag expression names the mask witness; test with a hand-built unmasked uv-slot target |
| P7 harness diverges from product | 178 (disclose) + 180 (serialize) | 1.8 report states the flag; firmware half named open in `MILESTONES.md` with the product symptom |
| P10 classification false confidence | **179 — Fault attribution** (before/with 178) | No label derives from the rail sampler; `unknown` bucket exists; accuracy measured against #21/#23/#28/#31/#45/#50; submit offer never suppressed |
| P8 `duration_s` semantics | **180 — Report schema 1.8** | Either a new key, or a parser that gates on `schema_version` — one of the two, named |
| P9 deleted-key consumers | 180 | `.claude/skills/**` markdown swept; `SKILL.md:375` updated in the same commit; both frozen 1.2 fixtures still parse with unchanged dedup values |

**Ordering rationale, stated as dependencies:**

- **174 first** because it is the gate everything else is measured against, and a gate written after its content is the project's own recorded failure (`reference_gate_authored_before_content_can_be_unreachable`).
- **175 before 179** because fault attribution consumes the fingerprint that 175 makes conditional.
- **179 before or with 178** because the UV fix needs a verdict that is not "chip FAIL," and that vocabulary is 179's deliverable.
- **176 before 177** because R3's *sign*, not just its size, depends on the connect measurement.
- **177 before 180** because the schema cannot honestly describe a metric whose scope is still being decided.
- **180 last** because it serializes decisions the four preceding phases make.

## Sources

**Primary — read or executed against `firestarter_app` at `0a93999` (HIGH confidence):**
- `firestarter/chip_test.py` — `classify_fingerprint` (`:162-259`), `_dispatch_read` (`:2626-2671`), `_read_region` (`:2710-2744`), `_resolve_write_target` (`:2747-2890`), `mask_write_pattern` (`:2057-2073`), `repeat_policy_tag`/`coverage_tag` (`:1081-1128`), `_aggregate_cycle_results` (`:1280-1332`), the cycle-abort path (`:1557-1571`), the fingerprint gate (`:3100`)
- `firestarter/diagnostic_report.py` — `dedup_fingerprint` (`:186-240`), `build_db_diff`/`has_indeterminate_fingerprint` (`:300-322`), `_step_dict` (`:667-729`), `_voltage_dict` (`:619-640`), `SCHEMA_VERSION` (`:48`)
- `firestarter/submit.py` — `overall_verdict` (`:140-152`), `build_title` (`:155-165`)
- `firestarter/eprom_operations.py` — `build_flags` (`:261-300`), `write_eprom` signature (`:1813-1821`)
- `firestarter/hardware.py` — `sample_vpp_mv`/`sample_vpe_mv` (`:440-448`)
- `tools/parse_devtest_issue.py` — `count_agreeing` (`:164-183`)
- `tools/check_dispatch.py:60-94` — the `electrical.vpp_mv` WP-pin-voltage collision
- `tests/test_chip_test.py:2695-2755` — the v1.30 Phase 134 MEASURED-SUPERSEDED ladder finding
- `.claude/skills/devtest-triage/SKILL.md:375` and both frozen schema-1.2 fixtures
- **Two executed experiments** (this session): perfect-match → `indeterminate`; dedup `4dc282a5d596` → `60a031573aab`; ladder `''` → `'community-reported'`

**Project record (HIGH confidence):**
- `.planning/seeds/dev-test-adaptive-sequencing.md`, `.planning/notes/dev-test-sequence-cost-model.md`, `.planning/notes/devtest-report-known-but-unstated-fields.md`
- `.planning/ROADMAP.md` §999.36, §999.43, §999.44
- Memory `reference_vpp_vpe_no_socket_routing` — `hw_read_voltage` sets no socket-routing bits; corroborated by that memory's own firmware review of 2026-06-03

**External (MEDIUM confidence, corroborating only):**
- Schema evolution: [Confluent — Schema Evolution & Compatibility Types](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html), [Conduktor — Schema Evolution Best Practices](https://www.conduktor.io/glossary/schema-evolution-best-practices), [JSON Schema Migration Strategy](https://jsonic.io/guides/json-migrations) — unanimous that changing a field's meaning is breaking and the mitigation is a new key
- Failure triage: [An Empirical Evaluation of Flaky Failure Classifiers (arXiv 2401.15788)](https://arxiv.org/pdf/2401.15788), [TestDino — Test Failure Analysis](https://testdino.com/blog/test-failure-analysis), [Harness — Flaky Tests](https://www.harness.io/blog/flaky-tests-the-quiet-killer-of-productivity-in-your-ci-pipeline) — the Firefox flaky-dismissal crash-rate case; classifiers need an explicit unknown bucket
- Diagnostic coverage: [Diagnostic Coverage overview (ScienceDirect)](https://www.sciencedirect.com/topics/engineering/diagnostic-coverage), [Microchip FMEDA](https://ww1.microchip.com/downloads/en/DeviceDoc/Failure-Mode-Effect-Diagnostics-Analysis-DS00003638A.pdf), [US6167545 — Self-adaptive test program](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6167545) — coverage is defined against an enumerated failure-mode set; skippable-test flows are an established ATE pattern with the same enumeration obligation

---
*Pitfalls research for: `dev test` fidelity — conditional diagnostics, skipped pre-check, fault attribution, report schema evolution*
*Researched: 2026-09-02*
