# Project Research Summary

**Project:** Firestarter — v1.36 `dev test` Fidelity ("Only Run What Can Tell You Something, Report Only What You Know")
**Domain:** Host-only Python CLI change to a community-facing hardware validation harness that files public defect reports (`firestarter_app`)
**Researched:** 2026-09-02
**Confidence:** HIGH on everything measured against `firestarter_app @ 0a93999` in the py3.11 CI-replica venv; MEDIUM on external corroboration (OCP/flashrom/smartctl/Sentry precedent); one figure (per-connect cost in seconds) is **UNMEASURED** and is flagged as such everywhere it appears.

**Research files:** [STACK.md](STACK.md) · [FEATURES.md](FEATURES.md) · [ARCHITECTURE.md](ARCHITECTURE.md) · [PITFALLS.md](PITFALLS.md)

---

## Executive Summary

**The milestone's central safety claim is false as written, and the gate that was supposed to catch that does not exist.** PROJECT.md states the blast-radius gate as: *"`dedup_fingerprint` must stay byte-identical … Not one field being added, filled or deleted is in that hash today."* Three of the four researchers independently falsified it **by execution, not argument**, against the same tree. That sentence is true about *report fields* and irrelevant to what this milestone actually changes: the hash reads **values and plan shape**, not schema keys. Four distinct re-key paths were measured:

| # | Change | Measured effect on `dedup_fingerprint` |
|---|---|---|
| 1 | **R2 — gate the fingerprint read-back on failure** | A *passing* write/verify today carries `classification="indeterminate"` (a perfect match falls through `classify_fingerprint`'s four buckets to the fallback), and the hash contains `f"{op}={verdict}:{cls}"`. Gating it makes `cls` empty. **`4dc282a5d596` → `60a031573aab`** on a six-step SST27SF512 shape; `write=OK:indeterminate` → `write=OK:` structurally. |
| 2 | **Pruning unsupported SDP steps from `Plan.steps`** | `parts` gains one entry per `StepResult`. **`a00791f1c2b4` → `7d1cd4157cfa`** for m27c512/full. Affects **637 of 677** chips, which carry six `supported=False` SDP steps. |
| 3 | **Canonical `part_number` naming** | `ac.chip` is `parts[0]`. **`a00791f1c2b4` → `a6f6c6354047`**. 732 of 746 part numbers differ from their own lowercase form and every open issue title is lowercase — this re-keys essentially all project history. |
| 4 | **UV blank-check abort (Pitfall 5, second-order)** | A BAD standalone blank-check sets `error_code` → `hardware_refused` → cycle 2 never runs → `run_count` collapses to 1 → `repeat_policy_tag` emits the degraded `fast`-shaped discriminator on a run nobody asked to be fast. A fourth, independent re-key. |

And the same R2 change **flips the promotion ladder**: `disposition='inconclusive' ladder=''` → `'suggests: candidate for community-reported' ladder='community-reported'`, because `build_db_diff` routes on `has_indeterminate_fingerprint`. A performance change moves chips onto the promotion ladder, in Phase 114 GRAD-01's neighbourhood, as a side effect.

**Underneath all of it: THE GATE DOES NOT EXIST YET.** Every dedup test in `tests/test_diagnostic_report.py` is *relational* — `fp(a) == fp(b)`, computed at runtime — so a change to the hash algorithm passes all of them. There is exactly **one** frozen expected-hash literal in the entire suite (`tests/test_diagnostic_report.py:1377`, `"a0a50436ae3d"`), and the frozen schema-1.2 fixtures the gate is supposed to be "asserted against" carry hand-written placeholder tokens (`"deadnu11id00"`, `"aaaa11112222"`, `"shared0000ab"`) — they prove parsing and grouping, and cannot prove hash continuity. `count_agreeing` reads the **embedded** hash and never re-hashes, so any re-key is permanent for the historical corpus and unrecoverable except by publishing the old→new mapping.

**The recommended approach is therefore: build the oracle first, then change nothing that the oracle has not measured.** Phase 174 is a blast-radius invariance harness — a frozen `(report shape → 12-hex)` parametrize table computed against HEAD *before any change lands*, plus a pinned `build_db_diff` ladder output, plus the measured raw-token→`part_number` delta. Every later phase is measured against it, and every one of the four re-keys above becomes a **declared, dated, one-time decision recorded in `MILESTONES.md`** rather than a silent history fork. The stack answer is unusually clean: **add no library.** The input domain for the structural test is finite and tiny (677 chips × 3 scopes = 2,031 plans, 9 distinct classes, exhaustively sweepable in **4.22 s** against a **737 s** suite), the schema consumer already matches `schema_version` by presence, and `dedup_fingerprint` is an allow-list hash that is immune to schema evolution by construction. The **only** stack change is bounding an unbounded pin: `syrupy>=5.0,<7`.

**The second-largest risk is that the milestone's headline UV fix does not reach its headline outcome.** PROJECT.md says "UV parts stop failing for the tool's own blank check." `FLAG_SKIP_BLANK_CHECK` fixes the *firmware write-init* pre-flight; it does not touch the plan's own **standalone `blank-check` step**, which `derive_plan` puts in every UV plan. After the planned fix the write and verify go OK and the run **still reports FAIL, still aborts after one cycle, and still offers `[dev test] AM27C020 — FAIL`**. The success criterion must be `overall_verdict == "PASS"` with `run_count == 2`, not "the write step went OK."

---

## Key Findings

### Recommended Stack — add nothing, bound one pin

Three candidate additions were evaluated and all three are declined **on merit, not compatibility**. `hypothesis` samples a domain that enumerates in 4.22 s, makes this repo's reachability-evidence discipline probabilistic, and injects flake into a 737 s suite that runs on every branch push. `jsonschema` would be a *third* declaration of a shape that `to_dict()` and the frozen fixtures already pin twice, with no interop boundary (sole producer and sole consumer are in the same repo) and a compiled `rpds-py` surface this repo deliberately quarantines. `pydantic` would be a shipped **runtime** dependency with a compiled core, to validate data this program itself produced.

**Core technologies (all already installed, unchanged):**
- **CPython 3.11 via `.venv/ci-replica/`** — every measurement must be taken here, never the devcontainer's default 3.12, which is *proven* in this project to hide breakage that reddens beta CI.
- **pytest 9.1.1 + stdlib `hashlib`/`json`/`dataclasses`** — the whole-DB sweep idiom already ships three times (`test_erase_flag_invariants.py`, `test_sdp_db_invariant.py`, `test_page_size_invariants.py`); copy it rather than reinvent.
- **`syrupy>=5.0,<7`** — **the one real change.** The pin is currently unbounded, the CI replica holds 5.5.3, PyPI now serves 6.0.0 (2026-08-22) whose headline breaking change is native dataclass serialization by the Amber serializer. `Plan`, `Step`, `Fingerprint` and every report structure are `@dataclass`. Current exposure is zero (all 32 snapshots are CLI-output strings); v1.36 exposure is real. Belt-and-braces: snapshot `report.to_dict()` — a plain dict — never the dataclass.
- **`mypy` / `ruff` / `pytest-cov`** — `chip_test` and `diagnostic_report` are in neither strict-island override list, so new typed helpers there are watermark-only and trip no new gate. Note the standing trap: `ruff select = ["E","F","I","UP"]`, so every `# noqa: BLE001` in the tree is inert.

### Expected Features — an established two-axis taxonomy already exists

The headline feature finding is that **v1.36 should not invent a vocabulary**. The OCP Test & Validation output spec (`ocp-diag-core`) separates **TestStatus** (`COMPLETE`/`ERROR`/`SKIP` — *did the run execute validly?*) from **TestResult** (`PASS`/`FAIL`/`NOT_APPLICABLE` — *what is the verdict on the DUT?*) and locks the legal cross-product to four cells. `dev test` today has only the *result* axis, which is exactly why `chip_test.py:2461` is forced to spend `VERDICT_BAD` — a chip verdict — on a half-seated cable. flashrom's `enum test_state {OK, NT, BAD, DEP, NA}` corroborates independently, and `smartctl` has kept "the command didn't reach the device" (exit bits 1–2) structurally separate from "the device is failing" (bit 3) since 2002.

**Must have (table stakes):**
- **T1** run-status axis orthogonal to the chip verdict, OCP names, 4-cell legality asserted by test.
- **T2** transport/rig faults become status=`ERROR`/result=`NOT_APPLICABLE`, never `BAD` — one handler, `chip_test.py:2461`.
- **T3** an `ERROR`-bearing run is not offered as `[dev test] <chip> — FAIL`, gated at the **existing** choke point `is_submittable(ac)` (`diagnostic_report.py:150-162`) — do not build a second gate.
- **T4** a machine-readable *reason* for non-submittability in the JSON (ABRT `not-reportable` pattern).
- **T5** sticky run-validity flags reported even on a PASS (kernel-taint pattern) — this is the transport-counter wiring.
- **T7** no operation runs whose result is empty by construction, enforced by a structural test over `derive_plan`.
- **T8** canonical `part_number` in report and title — **but see the re-key hazard; this is not cosmetic.**
- **UV blank-check skip** (999.44 host half) with the regression test that does not exist today.
- **The blast-radius gate itself**, which must be *built*, not assumed.

**Should have (competitive):**
- **D4** measurements exported as additive siblings of the verdict (OCP `Measurement` vs `Diagnosis`) — this is RPT-A1…E3 almost exactly; keep them siblings, never let a measurement become the verdict.
- **D3** a flashrom-`DEP`-equivalent ("failed under a configuration this rig cannot satisfy") — the only way this milestone can be *honest* about the 999.44 firmware half it is knowingly not fixing.
- **D6** a deprecation window on the three deleted schema keys.

**Defer:**
- **D1 rig-sanity leg** — highest value against gh#23, but **blocked on physics**: the VPP/VPE monitors read the boost-regulator rail via ADC and set none of the socket-routing bits, so a rig with a disconnected VPP jumper reports a perfectly healthy `vpp_before_mv: 11800`. Deferring is honest; shipping an over-claiming version is not.
- **D2 escalating tiers** — real SMART precedent, but `coverage_tag` is already a `dedup_fingerprint` input, so a tier axis collides with the blast-radius gate.
- **R4 session reuse** — payoff unmeasured, blast radius largest, cheapest sub-step is firmware-side and out of scope.

**Anti-features to refuse explicitly:** a softened FAIL with confidence percentages (OCP models ignorance as flat `UNKNOWN`, not a graded belief); per-flag CLI overrides for every gate (minipro's model — a defeated gate leaves no trace in the report); auto-retry-until-pass (the mechanism that manufactures NTF/RTOK); a generic SARIF-style `properties` bag; and **adding `RIG_FAULT` as a sixth `verdict` value**, which is a cardinality change *inside the dedup input*.

### Architecture Approach

The engine has two invariants everything hangs off, and the recommended design preserves both. **I-1: `derive_plan` is pure** — DB fields only, never the operator, never the chip — which is precisely why it can be swept over all 746 rows with no hardware, and therefore why the entire structural-test strategy exists. **I-2: `plan.steps` and `results` are positionally aligned**, assumed by three consumers. The evidence-gated sequencing decision must be split along the pure/impure line that already exists: **`derive_plan` DECLARES** (a closed-vocabulary oracle field on `Step`, read-only downstream, with a fail-closed dispatch arm modelled on `_MULTI_RUN_OPS`), **the dispatch layer EVALUATES**, and the run-time evidence travels on the existing `WriteContext` — which is *named* for this job and already threads three run-time facts through the step loop. A bare `if not all(outcomes)` at `chip_test.py:3100` is rejected because it is invisible to the structural test and cannot express cycle-1-fail/cycle-2-pass; a new middle layer is rejected because it breaks I-2.

**Major components:**
1. **Relational plan predicate** (`chip_test.py`, beside `cycle_block_bounds:1236`) — pure, returns *violations* not a bool, consumed by a whole-DB sweep with three anti-vacuity legs (≥746 rows visited, non-zero executable write steps found, and a **planted counter-plan** that makes it fire).
2. **Run-level evidence ledger on `WriteContext`** — written inside the cycle loop beside the two assignments already made there; read by `_dispatch_multi_run`.
3. **Two re-sync counters on `SerialCommunicator`, drained at teardown** — the precedent to copy by name is `EpromOperator.last_firmware_error_code`, whose `__init__` comment states exactly the reasoning: the operation context's `finally` tears down `self.comm` but never the operator. `eprom_operations.py:547` is the **sole** `self.comm = None` assignment in the module, so drain-at-teardown is complete by construction and that completeness is itself testable. Zero new imports either direction.
4. **Report fixture corpus** (`firestarter_app/tests/fixtures/`) — does not exist today at all; it is RPT-E2/E3's oracle *and* the blast-radius gate's home.
5. **Operator session lease** (R4, conditional) — must be an *opaque operator-side context manager* held by `run_plan`'s existing bare `try/finally`; `chip_test.py` must not learn about transport (its docstring promises it and `tools/check_devtest_orchestrator.py` enforces it by AST).

Two recorded non-claims in the source become **false** if R4 lands (`chip_test.py:3232-3241` on the unobservable `0x86` ack, `cli_handlers.py:2369-2378` on `programmer_info`); they must be re-stated, not quietly deleted.

### Critical Pitfalls

1. **The four re-key paths and the missing gate** (measured; see Executive Summary). Build the pinned-hash harness first; declare each re-key deliberately in `MILESTONES.md`. Warning sign: any plan that says "dedup is unaffected because no *field* changed."
2. **The UV fix does not reach the UV outcome** (measured, falsifies PROJECT.md:78-83). The standalone `blank-check` step still returns `VERDICT_BAD` with `error_code`, which sets `hardware_refused` and kills cycle 2. Whatever verdict replaces it **must not set `error_code`**. Assert the title, not the write.
3. **The blank-check skip must be gated on the monotonicity *witness*, not the region policy string.** `if step.region_policy == REGION_POLICY_UV_SLOT: flags |= FLAG_SKIP_BLANK_CHECK` reads naturally and is the same line count as the safe form — but policy and monotonicity are only *currently* coextensive, and the docstring at `chip_test.py:2769-2772` shows they were not one design iteration ago. Derive from `target.masked and target.current is not None and target.current_source == "probe read"`. Recovery cost if wrong: **physically unrecoverable** — a UV part written with a non-monotone pattern needs a UV eraser or is scrapped.

   **FALSIFIED (Phase 179, `179-01-PLAN.md`/`179-03-SUMMARY.md`).** MEASURED: the staged tranche
   targets that actually reach `write_eprom` — the only path onto the report — carry
   `current_source` values that start `"probe read (tranche 1/2)"` / `"probe read (tranche 2/2)"`
   (`chip_test.py:1518`), never the bare string `"probe read"` this prescription names. A witness
   written as `target.current_source == "probe read"` would never match on a real run, would ship
   green, and would be silently inert — never actually gating anything. Phase 179 implemented the
   witness as a new structural boolean instead
   (`WriteTarget.current_is_probe_read`, set once at the UV probe arm, carried through unchanged),
   and
   `tests/test_chip_test_uv_slot_write.py::test_the_prescribed_probe_read_string_equality_would_never_match`
   pins the falsification so a future return to the string-equality form goes red rather than
   silently inert. See `179-MEASUREMENT.md` for the real-hardware run whose `write_current_source`
   reads `"probe read (tranche 2/2)"` exactly as measured here.
4. **Auto-classifying rig faults from a sensor that cannot see the rig fault.** The voltage sampler measures the boost rail, not the socket. A classifier built on `vpp_before_mv` reports "rig OK" on precisely the run (gh#23) that motivated the milestone. Enumerate, per cause label, the signal that carries it and what that signal *physically measures*; emit `unknown` where no honest signal exists; and **never let classification suppress the submit offer** — that converts a visible wrong verdict into an invisible missing one (the Firefox flaky-dismissal failure mode). The six open community issues (#21, #23, #28, #31, #45, #50) are a ready-made labelled evaluation set and should be used as one.
5. **Skipping a diagnostic silently removes it from the record.** After gating, `fingerprint: null` means three different things: skipped-because-everything-passed, ran-and-returned-`b""`-because-the-chip-was-absent, and never-had-one. Emit the *reason*, not the absence (`fingerprint_source: "skipped: all runs passed" | "read-back" | "unavailable: empty read"`). This one key also solves the re-key if the gate outcome is what gets hashed, and gives R3's sampling provenance the same idiom.
6. **R3 sampling has three traps and is blocked on an unmeasured number.** The read step's verdict source silently moves to the sample; a hole-padded region file compared whole-file against a full read reports catastrophic false divergence; and a ten-block sample is **ten connects** where the full read was one, because `EpromOperator.comm` is torn down after every call. **If a connect costs more than ~0.5 s, R3 is net-negative on a 64 KiB part.** Cutting R3 on that measurement is a success, not a failure.
7. **Deleting `voltage.vpp_mv` breaks a live prose consumer.** `.claude/skills/devtest-triage/SKILL.md:375` instructs the triager to compare the report's `vpp_mv` against the chip's program voltage. The predictable fallback is `chip_database.json`'s `electrical.vpp_mv`, which on 5V-only families encodes the **WP-pin voltage** — `tools/check_dispatch.py:60-94` says comparing it as programming VPP "would produce false positives on every AMD/SST flash chip." A deletion justified as "removing a dead field" converts a triage skill into a machine that mis-blames every AMD/SST flash part. The consumer sweep must cover `.claude/skills/**` markdown, not just `.py`.

---

## Implications for Roadmap

**Phases number from 174.** Three researchers proposed build orders that agree on the spine and differ at the edges. The reconciliation below is one order; where they agreed, the agreement is load-bearing and is marked; where they conflicted, the choice is justified.

**Unanimous, load-bearing agreements — do not reorder these:**
- **The invariance harness is Phase 174, before anything.** All three reached it independently, and it is load-bearing because the milestone's *first substantive change* violates the gate the milestone claims to be protected by. A gate authored after the content it guards is this project's own documented anti-pattern.
- **The structural sentinel must be RED first and green before the read-back gate lands.** The sentinel *is* the gate's safety argument; landing the gate first ships a change whose justification is unproven.
- **The report schema phase is last, after sampling.** Both ARCHITECTURE (§6.6) and PITFALLS (Pitfall 12) reached this: exporting `divergence`/`bad_pct` as exact whole-device numbers and then quietly making them sampled estimates two phases later is worse than either alone.
- **The connect-cost measurement gates R3, it does not merely inform it.** PROJECT.md already commits to this ("must be measured before it is scoped"). Hold the line under schedule pressure.

### Phase 174: Blast-radius invariance harness
**Rationale:** Unanimous. The oracle must exist and be green before any change that can move the hash. No report fixture corpus exists in `firestarter_app/tests/fixtures/` today.
**Delivers:** A frozen `pytest.mark.parametrize` table of `(report shape → expected 12-char hash)` computed against HEAD **before any change lands**, covering the three chip populations × three scopes, pass/fail/marginal, `--fast`, uv-slot, and both `repeat_policy_tag`/`coverage_tag` states; a pinned `build_db_diff` disposition+ladder output for the all-OK non-SDP shape; a committed sorted `to_dict()` key list asserted element-wise (the *one* genuinely missing schema gate); and the **measured** raw-token→`part_number` delta for every chip with a filed `[dev test]` issue.
**Addresses:** the blast-radius gate itself (currently a claim, not a check).
**Avoids:** Pitfalls 1, 2, 13 — all four re-key paths.
**Note:** the AT28C256 case is *not* affected by the ladder flip (its SDP leg attaches fingerprints in every arm), so a harness that only exercises AT28C256 will not see it.

### Phase 175: Structural sentinel over `derive_plan` (RED first)
**Rationale:** The licence for the read-back gate. Must be green before 177.
**Delivers:** the pure relational predicate returning violations; the whole-DB sweep over `"full"` and `"partial"` (`"none"` is library/test surface only) with all three anti-vacuity legs, including the planted counter-plan; and the closure sentinel derived from the module's own `OP_*` constants so a future tenth op cannot escape by omission. Copy `test_shipped_ops_never_reach_sdp_arm` (`tests/test_chip_test_sdp_leg.py:827`) and `test_erase_flag_invariants.py`'s anti-vacuity discipline verbatim.
**Uses:** stdlib + pytest, module-scoped fixture (pay the 4.22 s sweep **once**), `parametrize` over the 9 classes and a plain loop over the 2,031 plans.
**Avoids:** Pitfall 3 (the safety argument lives outside the code that benefits from it).

### Phase 176: Transport instrumentation + connect-cost measurement
**Rationale:** *This is my reconciliation of the two conflicting proposals.* ARCHITECTURE puts transport counters in parallel (P-D) and the connect measurement late (P-G); PITFALLS puts the connect measurement at 176. Both are transport-layer instrumentation, both gate later phases, and the measurement is the milestone's one non-UV bench leg with hardware-scheduling lead time. Merging them and sequencing them early buys slack on both. Also takes the "fold `sample_vpp_mv` + `sample_vpe_mv`" idea off the table explicitly — it needs a firmware command and is **out of scope**; its −2 connects must not be counted in any v1.36 saving.
**Delivers:** two re-sync counters on `SerialCommunicator`, drained at `eprom_operations.py:547`, surfaced onto `TransportHealth` in the handler; a stated basis for `_SUSPECT_THRESHOLD = 5` (chosen while the counters were dormant, never exercised against a real distribution — `transport_suspect` becomes reachable for the first time the moment real counts land); an explicit scope statement that the `HardwareManager` side channel's comms are **not** counted; and a **per-board-class** per-connect measurement in seconds (Uno-class DTR auto-reset is likely the dominant term).
**Avoids:** investigating a suspected transport fault with all four counters reading `"not measured"`.

### Phase 177: Evidence-gated read-back (R2, corrected)
**Rationale:** Depends on 174 (the oracle) and 175 (the licence). This is where the R1/R2 contradiction must be adjudicated and the seed amended.
**Delivers:** the declared-oracle field on `Step` + closed vocabulary + fail-closed dispatch arm; the run-level evidence ledger on `WriteContext`; the gate at `chip_test.py:3100` reading the ledger, not local `outcomes`; the **fault-mode table** as a named deliverable (rows = the four `classify_fingerprint` buckets + "false PASS via undriven bus"; columns = caught by verify / read-back / blank-check); and the `fingerprint_source` disclosure key.
**Avoids:** Pitfalls 3, 4. Must be structurally incapable of reaching `_dispatch_sdp_leg`, where the read-back **is** the oracle in every arm.

### Phase 178: Fault attribution — the two-axis vocabulary
**Rationale:** ARCHITECTURE treats UV as fully independent and schedulable early; PITFALLS (Pitfall 5, measured) shows the UV phase needs this phase's verdict vocabulary to stop `error_code` aborting cycle 2. **I take the measured constraint over the independence claim** and sequence 178 before 179. It also consumes the fingerprint the 177 gate controls (on a *failing* run the gate lets the read-back through — but only if the gate is `not all(outcomes)` and nothing narrower) and the counters from 176.
**Delivers:** T1/T2/T3/T4 — OCP `TestStatus` as an additive orthogonal field kept **out** of the dedup hash; `SerialError`/`HardwareOperationError` reclassified at `chip_test.py:2461`; a run-validity term added to the existing `is_submittable`; the machine-readable reason key; a mandatory `unknown` bucket; and per-label accuracy measured against the six open issues.
**Avoids:** Pitfall 10, anti-feature A5.

### Phase 179: UV slot `FLAG_SKIP_BLANK_CHECK` (bench-gated)
**Rationale:** The milestone's one irreducible hardware dependency. Start its bench scheduling early even though it lands here.
**Delivers:** the flag derived from the **monotonicity witness**, never the policy string; adjudication of what a non-blank UV part's `blank-check` step *means* (a finding, not a FAIL, and it must not set `error_code`); a product-divergence disclosure key stating that `dev test` set a flag `firestarter write` does not; and the regression test whose criterion is **`overall_verdict == "PASS"` with `run_count == 2`**, not "the write step went OK."
**Avoids:** Pitfalls 5, 6, 7.

### Phase 180: Read-step sampling (R3) — conditional
**Rationale:** Gated by 176's measurement. **Cutting this phase on the measurement is a legitimate, successful outcome** — R1+R2 already deliver roughly two thirds of the modelled saving.
**Delivers:** if it proceeds — a verdict source pinned to the full read by test; block-wise `(offset, block)` comparison, never whole-file (hole-padded region files put real bytes at absolute offsets); sampling provenance carried into the exported `divergence`.
**Avoids:** Pitfall 11.

### Phase 181: Report fidelity — schema 1.8, canonical naming, consumer sweep
**Rationale:** Last, unanimously, because it must know what it is describing.
**Delivers:** RPT-A1…E3; `SCHEMA_VERSION` decision (see open questions); `chip_id_actual` from a structured `detected_id` on `StepResult` rather than prose scraping; `duration_s` semantics decision; `elapsed`; the deletions **with** a consumer sweep covering `.claude/skills/**` markdown; canonical naming implemented per whichever resolution the operator picks; and the enumeration of **every** dedup re-key source shipped in this milestone, in one place in the record, so a future reader can attribute a group split to the right cause.
**Avoids:** Pitfalls 8, 9, 12, 13.

### Deferred: R4 session reuse
Payoff unmeasured; blast radius largest (it converts the harness's central non-fatal-step guarantee into a false one unless every `SerialError` invalidates the lease and the next step reconnects); does not help the sampler's connects at all; cheapest sub-step is firmware-side. If it proceeds it must be **additive** (fall back to `find_and_connect` when no lease is held) or it breaks ~20 test doubles that assign `operator.comm` directly.

### Phase Ordering Rationale

- **Oracle → licence → change → disclosure.** 174 builds what measures, 175 builds what permits, 177–180 change, 181 discloses. Every substantive change is bracketed by something that can prove it did or did not move the hash.
- **Instrumentation early (176) because it gates two later phases and carries bench lead time.** This is the one place I departed from ARCHITECTURE's parallel placement, and the reason is scheduling, not dependency.
- **Measured constraints beat structural-independence claims.** 178 before 179 because Pitfall 5 was measured; ARCHITECTURE's "P-I is fully independent" is true of the *code* and false of the *outcome*.
- **Parallelisable after 174:** 175 ∥ 176. 179's bench scheduling should be initiated as soon as 178's vocabulary is decided.

### Research Flags

**Needs deeper research during planning (`/gsd-plan-phase --research-phase N`):**
- **Phase 178** — the fault-attribution taxonomy is the one place this milestone is designing something new. The OCP mapping is well-sourced but the *labels* and their *evidence bindings* need per-label derivation against the six open issues, and PITFALLS flags the ABRT `not-reportable` mechanics as MEDIUM confidence (the libreport source was not read — copy the *concept*, not the mechanics).
- **Phase 180** — its existence is conditional on a measurement that does not exist yet; scope after 176 reports.

**Standard patterns — skip research:**
- **Phase 174, 175** — the whole-DB sweep, the element-wise committed comparison, and the frozen-hash parametrize are all shipped idioms in this tree with named precedents.
- **Phase 176** — `last_firmware_error_code` is an exact structural precedent, cited line-by-line.
- **Phase 181** — the schema mechanism (hand-written `to_dict()`, presence-matched consumer, frozen fixtures) already exists and already works; the work is decisions and a sweep, not discovery.

---

## Contradictions and Open Decisions — a human must settle these

These are **not** planner decisions. Each one changes what the community sees or what history means.

| # | Decision | The conflict | Notes |
|---|---|---|---|
| **D-1** | **R1 vs R2 contradict each other on the same call site.** | The seed's R1 says *"Any place the engine reads the whole device back to compare it against a buffer it already holds is a verify. **This applies to the fingerprint read-backs.**"* R2 says the read-back should *stay* a read-back, merely conditional. Read literally, R1 converts the diagnostic into an oracle and destroys the mismatch distribution `classify_fingerprint` exists to compute — the four-bucket diagnostic becomes one mismatch address. | The cost-model note resolves it correctly ("verify decides; a read-back diagnoses"); the **seed does not**. A planner working from the seed alone will implement the destructive reading. **Amend the seed's R1 sentence in Phase 177.** A rule that contradicts itself in the artifact the planner reads is a defect in the artifact. |
| **D-2** | **Canonical naming: new field, or a one-time global re-key?** | **R1 (STACK's recommendation):** add `auto_capture.canonical_part_number` for the title and body, leave `ac.chip` carrying the raw token — purely additive, zero re-key. **R2:** normalize `parts[0]` — re-keys essentially all history and resets every `count_agreeing` group. | 732/746 part numbers differ from their lowercase form; every open issue title is lowercase. **This is an operator decision, not a phase's.** Also: the DB `name` field is a comma-joined alias list (`at28c256` → `"AT28C256,AT28C256E,AT28HC256,…"`), so "the canonical name" means `part_number`, and a rule is needed for which alias a title shows. |
| **D-3** | **Schema 1.8-with-deletions, a deprecation window, or 2.0?** | Under the OCP major/minor rule, **field deletion is a major change**. v1.36 plans a *minor* bump while deleting three keys. Options: (a) deprecate — emit them as `null`/`NOT_MEASURED` for one generation, delete at 2.0; (b) call it **2.0** — honest, and cheap because the hash doesn't read `schema_version`; (c) ship 1.8 with deletions, defensible *only* because no code path assigns them — which should be a **test**, not a claim. | Note that the bump disambiguates nothing today: both parsers accept `schema_version` by **presence only** (a fixture carries `"9.9-future"`). Any version-gating decision belongs in Phase 181 and must not be deferred past it. |
| **D-4** | **Should an all-OK run reach `community-reported`?** | Today it structurally cannot, because a perfect match classifies as `indeterminate` and `build_db_diff` forces `_LADDER_NONE` on any indeterminate fingerprint. R2 flips this. | Answering "yes, and it always should have been" is **defensible** — `indeterminate` on a bit-perfect compare is noise, not a finding. But it must be **stated before implementation and made the assertion**, not discovered afterwards, and said publicly, because it changes what the triage skill and every human reader infer from a report. The warning sign is `tests/test_chip_test.py:2752` (`assert db_diff.ladder_state == ""`) turning RED and someone "fixing" the expectation. |
| **D-5** | **`vpp_mv` deletion has a live prose consumer.** | `.claude/skills/devtest-triage/SKILL.md:375` reads it. The fallback it will reach for — `chip_database.json`'s `electrical.vpp_mv` — encodes WP-pin voltage on 5V families and would **mis-blame every AMD/SST flash part**. The frozen schema-1.2 fixtures also carry *real* values (`vpp_mv: 11800`, `vpe_mv: 13700`), so the already-filed corpus contains meaningful readings under the key. | Update `SKILL.md` in the **same commit** as the schema change; replace the row with `vpp_before_mv`/`vpp_after_mv` and state in the same row what they do **not** prove (they are rail readings, never socket readings). Parsers stay tolerant forward *and* backward; a future absence must never read as a measured zero. |
| **D-6** | **`classify_fingerprint`'s fifth bucket.** | PITFALLS' preferred fix for the R2 re-key is a `match` bucket for `bad == 0`, emitted on the cheap path, and hash *that* — it removes the `indeterminate`-on-a-perfect-match absurdity but **still re-keys history once, for a defensible reason**. The alternative (substituting the historical string when the read-back is skipped) is the only genuinely byte-identical option and is ugly. | Whichever is chosen must be declared and dated. |
| **D-7** | **`Plan.locked_destructive` deletability** (RPT-B2's second half) — live tests depend on it and it feeds `count_applicable`'s `M`. Adjudicate in Phase 181. |
| **D-8** | **Whether the whole-DB sweep should cover user-override DB entries** (`~/.firestarter/database.json`) — `derive_plan` reads whatever `db.get_eprom` returns, and an override could emit a shape the shipped 746 never do. Plan-time decision in Phase 175. |

---

## Corrected line citations

**The backlog text this milestone was scoped from has drifted. Use these, not the ones in PROJECT.md:**

| PROJECT.md / backlog says | Actual at `firestarter_app @ 0a93999` |
|---|---|
| `serial_comm.py:520-526` and `:536-541` (the two re-sync sites) | **`serial_comm.py:485-490` and `:500-505`** — same two sites, ~35 lines earlier |
| `diagnostic_report.py:316-355` (`dedup_fingerprint`) | **`diagnostic_report.py:186-241`** — body at `:211-241`, the hashed triple at `:213-214`, `ac.chip` as `parts[0]` at `:211` |
| `_merge_cycle_results` | **`_aggregate_cycle_results`, `chip_test.py:1280`** — the function does not exist under the brief's name |

**Confirmed exactly as stated:** the gate at `chip_test.py:3100`; `classify_fingerprint` at `:162`; `mask_write_pattern` at `:2057`; `uv_slot_starts` at `:2171`; `REGION_POLICY_UV_SLOT` at `:382`; `SCHEMA_VERSION = "1.7"` at `diagnostic_report.py:48`; `NOT_MEASURED` at `:49`; `vpp_mv`/`vpe_mv` at `:571-572` and `:638-639`; `banner.locked_steps` at `:733` and `:737`; `build_flags`'s `FLAG_SKIP_BLANK_CHECK` map at `eprom_operations.py:279`; `self.comm = None` at `eprom_operations.py:547`; the sentinel at `tests/test_chip_test_sdp_leg.py:827`.

---

## What NOT to do

**Dependencies — add nothing:**
- **No new entry in `[project].dependencies`.** The shipped runtime set stays `pyserial, requests, tqdm, click, rich, packaging`. Nothing in v1.36 executes at user runtime that stdlib does not cover.
- **No `hypothesis`** — samples a domain that enumerates in 4.22 s, makes reachability evidence probabilistic, adds flake to a 737 s suite that runs on every branch push.
- **No `jsonschema`/`fastjsonschema`** — a third redeclaration of a shape declared twice, with no interop boundary and a compiled `rpds-py` surface.
- **No `pydantic`** — would be a *runtime* dependency with a compiled core, validating data this program produced.
- **No `jcs` / RFC 8785, and do not refactor `dedup_fingerprint` to hash `to_dict()`.** Canonical JSON is the right answer when the hash input *is* the document. Here it would make every additive 1.8 field re-key every historical report — **the precise failure the milestone forbids.** Record this as a decision, because it is the tempting refactor.
- **The only stack change is `syrupy>=5.0,<7`.**

**Design:**
- **Do not add `RIG_FAULT` as a sixth `verdict` value.** It is a cardinality change *inside* the dedup input (`op=verdict:cls`), it re-keys every group that hits it, and it makes the illegal states representable again. Second, additive, orthogonal field, kept out of the hash.
- **Do not drop unsupported steps from `Plan.steps`.** Keep the `StepResult` with an NA verdict and skip only the work — which is what `run_plan` already does ("NA steps are recorded without any operator call"). The 637 chips' six unsupported SDP steps are **hash ballast, not waste**.
- **Do not use `dataclasses.asdict()` wholesale in `to_dict()`** — `diagnostic_report.py:771` names this "Pitfall 3"; it is how an unreviewed internal field reaches a stranger's GitHub issue.
- **Do not gate `FLAG_SKIP_BLANK_CHECK` on `region_policy`.** Witness form, same line count.
- **Do not build a second submit gate** — extend `is_submittable`.
- **Do not let auto-classification suppress the submit prompt.** Change the title and disposition; never the offer to file.
- **Do not measure anything in the devcontainer's default py3.12.**
- **Do not quote the cost model's second-counts as acceptance criteria.** Every rate comes from one log, one Leonardo, one 64 KiB `0x07` part; read rate varies ~24% by protocol and the Uno's 512 B buffer is unmodelled. Success criteria in **operation counts** ("a passing run performs 0 fingerprint read-backs"), never in seconds.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | Every count, timing, hash and plan shape executed on `0a93999` in the py3.11 CI replica and transcribed verbatim. Package facts from the PyPI JSON registry API (Context7 MCP was not available in this runtime; PyPI is the canonical publisher of version metadata and is the stronger source for the question asked). syrupy 6.0.0's breaking-change list is MEDIUM (single vendor source) but its *consequence here* — 32 snapshots, none dataclass-shaped — was verified locally and is HIGH. |
| Features | **MEDIUM–HIGH, mixed** | The OCP spec, flashrom `include/flash.h` and `smartctl.8.in` were fetched and quoted **verbatim from canonical artifacts** — HIGH despite the classify-confidence seam's LOW floor for `webfetch`, because they are re-checkable at stable raw URLs. LTP/kselftest/kernel-taint/Sentry/SARIF are MEDIUM (search-derived, multiply corroborated). ABRT's `not-reportable` mechanics are **LOW–MEDIUM** — libreport source was not read; copy the concept, not the mechanics. |
| Architecture | **HIGH** | Every file:line opened on disk; two claims additionally **executed**, not merely read (the R2 re-key, and the detected-chip-ID prose scrape). Three of the brief's own line ranges were found stale and corrected. |
| Pitfalls | **HIGH where MEASURED, honestly separated** | The file labels every item MEASURED or REASONED. Pitfalls 1, 2, 5, 9, 10, 11, 13 are MEASURED (executed or read at HEAD with line cites). Pitfalls 3, 4, 6, 12 are REASONED from measured facts and say so. It also **tested the counter-argument put to it** rather than repeating it, and reported that the argument is sound but under-scoped in three named places. |

**Overall confidence: HIGH** on the findings that reorder the roadmap; the residual risk is concentrated in exactly one unmeasured number.

### MEASURED vs INFERRED — the honesty line

**MEASURED (executed against `0a93999`):** all four dedup re-key hashes; the ladder flip; 746 rows / 677 distinct part numbers / 2,031 plans / 9 classes / 4.22 s sweep / 737.37 s suite; 637-of-677 chips carrying six unsupported SDP steps; 732/746 part numbers differing from lowercase; `perfect-match classification -> 'indeterminate' bad=0 ff_ratio=0.0039`; the single frozen hash literal at `test_diagnostic_report.py:1377`; the placeholder tokens in the frozen fixtures; the standalone-blank-check → `hardware_refused` → cycle-2-abort trace; `eprom_operations.py:547` as the sole `self.comm = None`; `SKILL.md:375`'s `vpp_mv` instruction and `check_dispatch.py:60-94`'s WP-voltage collision; the `vpp_mv: 11800` / `vpe_mv: 13700` values in the frozen fixtures; every corrected line citation.

**INFERRED (reasoned from measured facts, labelled as such):** the fault-mode coverage argument for verify-vs-read-back; the three-meanings-of-`null` consequence; the policy-vs-witness divergence risk; the `divergence`-becomes-an-estimate interaction; the drift risk between a declared oracle and its dispatcher.

**UNMEASURED — do not carry the projection as fact:** **the per-connect cost in seconds.** `/dev/ttyACM0` was busy during the explore session; the cost model's own "what this note does not establish" section says the counts are structural and validated (13 predicted / 13 observed) and **the seconds are not measured at all**. The modelled **31.5%** saving and every derived second-count are therefore *directional*, not numeric. On Uno-class boards the DTR auto-reset and bootloader wait are likely the dominant term, so the measurement must be **per board class**, not one number. R3's *sign* — whether it saves time at all — depends on this.

### Gaps to Address

- **Per-connect cost, per board class** — bench leg in Phase 176. Blocks R3's scoping and R4's existence.
- **Basis for `_SUSPECT_THRESHOLD = 5`** — chosen while the counters were dormant, never exercised. Close in Phase 176 once counts exist, or it is a fabricated verdict the first time it fires.
- **Which of `retries`/`timeouts` are genuinely wireable** — named by RPT-C1 but not traced end-to-end. `NOT_MEASURED` must remain for anything not actually wired.
- **ABRT `not-reportable` file mechanics** — read libreport before writing a requirement that mimics it precisely; the *concept* (a machine-readable, reason-carrying suppression) is safe.
- **Whether canonical naming's blast radius is actually large** — the raw-token→`part_number` delta over chips with filed issues may be near-zero if testers copy names from `firestarter list`. That is a **measurement** (Phase 174), not an assumption, and it changes D-2's cost.
- **PROJECT.md's blast-radius gate sentence is wrong and needs correcting** — it should say the hash reads *values and plan shape*, enumerate the four re-key paths, and state that the gate is being **built** in Phase 174 rather than inherited.

## Sources

### Primary (HIGH confidence)
- **`firestarter_app` working tree @ `0a93999`**, meta @ `58bb8d80` — `chip_test.py` (3,539 lines), `diagnostic_report.py` (937 lines), `eprom_operations.py`, `serial_comm.py`, `cli_handlers.py`, `hardware.py`, `submit.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `tests/test_chip_test.py`, `tests/test_chip_test_sdp_leg.py`, `tests/test_diagnostic_report.py`, `tests/test_parse_devtest_issue.py`, `tests/test_erase_flag_invariants.py`, `tests/test_sdp_db_invariant.py`, `tools/check_devtest_orchestrator.py`, `tools/check_diagnostic_report_claims.py`, `tools/check_dispatch.py`, `tools/parse_devtest_issue.py`. All measurements taken in `.venv/ci-replica/` (CPython 3.11).
- **`firestarter` firmware** `src/proms/memory.cpp:377-396` (`memory_verify_execute` early-return).
- **Meta repo** — `.planning/PROJECT.md` §v1.36, `.planning/ROADMAP.md` §999.36, `.planning/seeds/dev-test-adaptive-sequencing.md`, `.planning/notes/dev-test-sequence-cost-model.md`, `.claude/skills/devtest-triage/SKILL.md` + fixtures, `.claude/skills/devtest-rootcause/`, three pending todos under `.planning/todos/pending/`.
- **OCP Test & Validation output spec** — `opencomputeproject/ocp-diag-core` `json_spec/README.md`, quoted verbatim.
- **flashrom** `include/flash.h` — `enum test_state`, `struct tested`, `TEST_OK_*` macros.
- **smartmontools** `smartctl.8.in` — `EXIT STATUS` bitmask, `-j` sub-flags.
- **PyPI JSON registry API** — hypothesis 6.167.1, jsonschema 4.26.0, syrupy 6.0.0, pytest 9.1.1, pydantic 2.13.5, and others (2026-09-02).

### Secondary (MEDIUM confidence)
- syrupy 6.0.0 release notes (single vendor source) — dataclass serialization change.
- Linux kernel `tainted-kernels.rst`; Linux Test Project `TCONF`/`TBROK`/`TWARN`; kselftest KTAP exit codes; pytest/JUnit failure-vs-error; SMART short/extended/conveyance/selective purposes; Sentry event grouping ("existing issues are not re-grouped" — independently confirmed by this project's own gh#20 orphan record); OASIS SARIF 2.1.0 property bags; Cranfield NFF/NTF/CND/RTOK taxonomy paper; minipro manpage.
- Community issues motivating the milestone — henols/firestarter_prom #21, #23, #28, #31, #45, #50.

### Tertiary (LOW confidence — flagged, not relied on)
- RFC 8785 / JCS — used only to establish that a standard canonicalizer exists and to explain why it does not apply; the conclusion rests on the locally-measured structure of `dedup_fingerprint`, not on the search.
- ABRT / libreport `not-reportable` element semantics — concept corroborated across sources, source not read. **Verify before writing a requirement that mimics it precisely.**

---
*Research completed: 2026-09-02*
*Ready for roadmap: yes*
