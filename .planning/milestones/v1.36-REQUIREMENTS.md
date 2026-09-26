# Requirements: Firestarter — v1.36 `dev test` Fidelity

**Defined:** 2026-09-02
**Milestone:** v1.36 — "Only Run What Can Tell You Something, Report Only What You Know"
**Core Value (this milestone):** `dev test` fails only for reasons that are actually the chip's, runs no
operation whose result is empty by construction, and reports only what the run already knows.

**Scope:** `firestarter_app` (host) only. No firmware change.

---

## Decisions taken at definition (operator, 2026-09-02)

These were surfaced as D-1…D-8 by the research synthesis and are settled here so no phase re-litigates them.

| ID | Decision | Consequence |
|---|---|---|
| **D-1** | The seed's R1 sentence — *"this applies to the fingerprint read-backs"* — is **amended**. | Read literally it converts the diagnostic into an oracle and destroys the mismatch distribution `classify_fingerprint` exists to compute. A rule that contradicts itself in the artifact a planner reads is a defect in the artifact. Owned by RPT/PRUNE phase that touches the seed. |
| **D-2** | Canonical naming is an **additive field** (`auto_capture.canonical_part_number`); `ac.chip` keeps the operator's raw token. | Zero re-key. Measured alternative: normalizing `parts[0]` gives `a00791f1c2b4` → `a6f6c6354047`, and 732/746 part numbers differ from their lowercase form while every open issue title is lowercase — it would re-key essentially all project history. |
| **D-3** | `schema_version` becomes **2.0**, not 1.8. | Three keys are deleted, the filed corpus carries real values under two of them (`vpp_mv: 11800`, `vpe_mv: 13700` in the frozen 1.2 fixtures), and `duration_s` keeps its name while changing meaning. A major number is the honest label. Costs nothing mechanically: both parsers accept `schema_version` by **presence only** (a live fixture carries `"9.9-future"`) and the dedup hash never reads it. **This reverses 999.36's RPT-E1, which said 1.8.** |
| **D-4 + D-6** | `classify_fingerprint` gains a **`match` bucket** for `bad == 0`, emitted on the cheap path; `build_db_diff` stops forcing `_LADDER_NONE` on it, so an **all-OK run becomes promotable to `community-reported`**. | Removes the `indeterminate`-on-a-bit-perfect-compare absurdity. **Re-keys dedup history once, deliberately** — declared and dated in `MILESTONES.md`, and stated publicly because it changes what a report implies to the triage skill and to every human reader. |
| **D-5** | `.claude/skills/devtest-triage/SKILL.md` is updated in the **same commit** as the `vpp_mv` deletion. | Its fallback — `chip_database.json`'s `electrical.vpp_mv` — encodes WP-pin voltage on 5V families and would **mis-blame every AMD/SST flash part**. Replaced by `vpp_before_mv`/`vpp_after_mv`, with the row stating what they do **not** prove: they are rail readings, never socket readings. **AMENDED by phase 181 plan 09 (discharged):** this row originally named `SKILL.md:375` as the line to rewrite. That anchor is wrong and acting on it would have introduced a defect — `:375` is the **database** `vpp_mv` in the datasheet-vs-`firestarter info` cross-check table, a different field that merely shares the name, and rewriting it as `vpp_before_mv`/`vpp_after_mv` would have turned a **correct** row false. The report-voltage sentence was extended instead (now `:337`) and the database row was deliberately left verbatim (now `:385`, moved only by the insertion above it). Discharged as a skill-first commit pair, `d2116df9` then app `c994849`. |
| **D-7** | `Plan.locked_destructive` deletability is adjudicated inside the report phase, not pre-decided. | Live tests depend on it and it feeds `count_applicable`'s `M`; the deletion is narrower than 999.36's RPT-B2 states. |
| **D-8** | Whether the whole-DB structural sweep covers user-override entries (`~/.firestarter/database.json`) is a plan-time decision in the sentinel phase. | `derive_plan` reads whatever `db.get_eprom` returns; an override could emit a shape the shipped 746 never do. |

---

## v1 Requirements

### Blast-Radius Oracle

The gate this milestone was scoped around **does not exist**. Every dedup test in
`firestarter_app/tests/test_diagnostic_report.py` is *relational* (`fp(a) == fp(b)`, computed at
runtime), so a change to the hash algorithm passes all of them. There is exactly **one** frozen
expected-hash literal in the entire suite (`tests/test_diagnostic_report.py:1377`, `"a0a50436ae3d"`),
and the frozen schema-1.2 fixtures carry hand-written placeholder tokens (`"deadnu11id00"`), not real
hashes. `count_agreeing` reads the **embedded** hash and never re-hashes, so any re-key is permanent.
**Nothing else in this milestone may land before this category is green.**

- [x] **GATE-01**: A frozen `(report shape → 12-hex `dedup_fingerprint`)` table exists, computed against HEAD **before** any behaviour change lands, covering at minimum the four measured re-key shapes (read-back gating, SDP-step pruning, canonical naming, UV `run_count` collapse).
- [x] **GATE-02**: The suite fails when `dedup_fingerprint` output changes for any frozen shape. The assertion is against an absolute expected value, never `fp(a) == fp(b)`.
- [x] **GATE-03**: `build_db_diff`'s ladder output is pinned for the same shapes, so a promotion-ladder change cannot land silently.
- [x] **GATE-04**: The raw-CLI-token → `part_number` delta across the shipped database is measured and recorded as an artifact, not assumed.
- [x] **GATE-05**: A report corpus lives in `firestarter_app/tests/fixtures/`. There is none today — the frozen fixtures are in the meta repo and cannot prove hash continuity.
- [x] **GATE-06**: Every deliberate re-key in this milestone is recorded in `MILESTONES.md` as a declared, dated, one-time decision with its before/after hashes.

### No-Information Operations

Success is stated in **operation counts, never in seconds**. Every timing figure available comes from
one log, one Leonardo, one 64 KiB `0x07` part; read rate varies ~24% by protocol and the Uno's 512 B
buffer is unmodelled.

- [x] **PRUNE-01**: A passing run performs **zero** fingerprint read-backs.
- [x] **PRUNE-02**: The read-back gate consults the step's outcomes **across all cycles**, not the final cycle alone. A cycle-1-fail / cycle-2-pass run keeps its fingerprint. (`not all(outcomes)` at `chip_test.py:3100` is insufficient at HEAD — under the cycle block `outcomes` is a one-element list for the final cycle only.)
- [x] **PRUNE-03**: A passing write/verify still reports a fingerprint, **synthesized** from what the operation already established (`bad=0`, `total=region_length`, `ff_ratio: None`) and classified `match` per D-4/D-6. The read-back is what costs; the classification is free.
- [x] **PRUNE-04**: Where the engine reads a whole device back only to compare it against a buffer it already holds, it uses the on-device verify instead. **The fingerprint read-back is explicitly excluded from this rule** (D-1). Closed as measured-empty within the engine: exactly two `operator.read_eprom` sites exist in `chip_test.py`, both excluded (the fingerprint read-back by D-1, the SDP leg by the seed's own carve-out); `eprom_operations.write_cycle_eprom` is named and excluded as the one genuine match in the package, outside the engine, the uno328pb read-repeatability oracle. Evidenced by `177-READBACK-INVENTORY.md`.
- [x] **PRUNE-05**: Unsupported steps keep their `StepResult` with an NA verdict; only the work is skipped. They are **not** dropped from `Plan.steps` — 637 of 677 chips carry six `supported=False` SDP steps and they are hash ballast, not waste.
- [x] **PRUNE-06**: A structural test over `derive_plan` output fails when a plan emits a write with no verify behind it. Expressed as a relational predicate over `Plan.steps`, not a self-declared per-step annotation, and carrying anti-vacuity legs including a planted counter-example.
- [x] **PRUNE-07**: The seed `.planning/seeds/dev-test-adaptive-sequencing.md` is amended so R1 no longer instructs a planner to destroy the diagnostic R2 preserves (D-1).
- [x] **PRUNE-08**: The read step's second full sweep is replaced by a bit-structured sample **only if** MEAS-01 shows the sample is cheaper on the measured board class. If it is not, this requirement closes as *measured, not worth doing*, with the measurement recorded — that is a success, not a miss.

### Fault Attribution

`chip_test.py:2567-2574` currently spends `VERDICT_BAD` — a chip verdict — on "a half-seated cable", and its
own comment says so. This is the gh#23 gap.

- [x] **ATTR-01**: A run carries a **status** axis (did the run execute validly) separate from the **result** axis (the verdict on the part), following the OCP Test & Validation two-axis model.
- [x] **ATTR-02**: A step that failed for a tool or transport reason is not reported as a chip verdict.
- [x] **ATTR-03**: The overall verdict and the filed issue title reflect the status axis — a run that did not execute validly does not file as `[dev test] <chip> — FAIL`.
- [x] **ATTR-04**: **No sixth `verdict` value is introduced.** The status axis is a separate additive field kept out of the dedup hash — a cardinality change inside `op=verdict:cls` would re-key every group that hits it.
- [x] **ATTR-05**: Auto-classification never suppresses the submit prompt. It changes the title and disposition only; the offer to file always stands.
- [x] **ATTR-06**: The report states what a rail reading does **not** prove. `sample_vpp_mv` → `hw_read_voltage`'s `CMD_READ_VPP` branch sets `CTRL_VPP_REGULATOR_ENABLE | CTRL_VPP_VPE_DROP_ENABLE` (the regulator drop divider — part of the HV rail composition, not a socket route) and no socket-routing bits, so a rig with VPP unhooked still reads a healthy `vpp_before_mv: 11800`. No requirement here may claim to detect that fault.

### UV Slot Writes

- [x] **UV-01**: A UV part holding data outside the target slot accepts a slot write.
- [x] **UV-02**: Such a run reports **`overall_verdict == "PASS"` with `run_count == 2`**. `FLAG_SKIP_BLANK_CHECK` fixes the firmware write-init pre-flight only; the plan's own standalone `blank-check` step also had to stop dominating the fold, so the write step going OK is **not** the criterion. (**Mechanism FALSIFIED, Phase 179** — the original wording of this requirement said the blank-check "trips `hardware_refused` and aborts cycle 2". MEASURED: the standalone blank-check sits at index 2, OUTSIDE a `cycle_block_bounds` that is `(3, 6)` for `m27c512`, `am27c020` and `tms27c512`, and `run_plan`'s per-step path has no `hardware_refused` mechanism at all — the cycle-2 abort came from the WRITE step's own firmware refusal. What the blank-check actually did was return `VERDICT_BAD` into a FAIL-dominant `submit.overall_verdict` (`submit.py:164-171`). The requirement's substance is unchanged — both defects still had to be closed for UV-02 to be reachable — but the named mechanism was wrong. Same falsification recorded at `.planning/research/PITFALLS.md` Pitfall 5 step 2 and `.planning/research/SUMMARY.md`.)
- [x] **UV-03**: The `FLAG_SKIP_BLANK_CHECK` pass is witness-form — not gated on `region_policy`.

### Report Fidelity

Reuses 999.36's drafted IDs. **RPT-E1 is changed** by D-3.

- [x] **RPT-A1**: `chip_id_actual` is populated with the verified id on a **passing** id check, not only on a mismatch. No companion provenance key, no qualifier string.
- [x] **RPT-A2**: `steps[].fingerprint` gains `total`, `bad`, `bad_pct` and `evidence` as **additive siblings**; `classification` keeps its existing key.
- [x] **RPT-A3**: `steps[].divergence` is exported — `None` only when no divergence was computed.
- [x] **RPT-A4**: `plan.is_uv` reaches the report as a top-level boolean, read off the single `derive_plan` decision, never re-derived.
- [x] **RPT-A5**: The detected chip ID becomes a `StepResult` field rather than being recovered by scraping prose (`cli_handlers.py:2172-2179`).
- [x] **RPT-B1**: `voltage.vpp_mv` and `voltage.vpe_mv` are deleted from the dataclass, `_voltage_dict()` and the schema. That no code path assigns them is proven by **test**, not asserted.
- [x] **RPT-B2**: `banner.locked_steps` is deleted; the N-of-M banner itself is kept. `Plan.locked_destructive` is adjudicated separately per D-7.
- [x] **RPT-C1**: The two re-sync events at `serial_comm.py:488-494` and `:504-510`, `_decode_id_frame` returning `None`, and `get_response`'s timeout each increment a real counter reachable by the report.
- [x] **RPT-C2**: `transport_health` reports those real counts. `NOT_MEASURED` remains **only** for a counter genuinely not wired, and `_is_transport_suspect`'s present-AND-elevated rule is unchanged — absent data still cannot fabricate suspicion.
- [x] **RPT-D1**: `duration_s` is the **per-operation** cost — `_aggregate_cycle_results` (`chip_test.py:1280`) stops summing across cycles. Its meaning must not vary with `run_count`, so a `--fast` value is directly comparable to a default run's.
- [x] **RPT-D2**: A real wall-clock `elapsed` for the whole command is added to `to_dict()`, and the render-only `steps total` sum-of-sums row is removed.
- [x] **RPT-E1**: `schema_version` becomes **`2.0`** (D-3).
- [x] **RPT-E2**: Deletions are forward-only — the frozen schema-1.2 fixtures keep parsing unchanged, asserted by test.
- [x] **RPT-E3**: `dedup_fingerprint` is byte-identical for every pre-existing report shape **except** the re-keys declared under GATE-06, each of which is asserted to be exactly the change it declared and nothing more.
- [x] **RPT-F1**: `auto_capture.canonical_part_number` carries the matched database `part_number` and is used for the issue title and body; `ac.chip` keeps the operator's raw token (D-2). A rule states which alias a title shows when `part_number` is a comma-joined list.
- [x] **RPT-F2**: `.claude/skills/devtest-triage/SKILL.md` is updated in the same commit as RPT-B1 (D-5).

### Measurement

- [x] **MEAS-01**: Per-connect cost is measured **per board class** (Uno 512 B, Leonardo 1024 B), not as one number. On Uno-class boards the DTR auto-reset and bootloader wait are likely the dominant term. This gates PRUNE-08 and the R4 deferral.
- [x] **MEAS-02**: `_SUSPECT_THRESHOLD = 5` is either justified against real counts or re-derived once RPT-C1's counters exist — it was chosen while the counters were dormant and has never been exercised.
- [x] **MEAS-03**: Which of `retries` / `timeouts` are genuinely wireable is traced end to end. Anything not actually wired keeps `NOT_MEASURED`.

### Hygiene

- [x] **HYG-01**: `syrupy` is bounded `>=5.0,<7`. It is pinned unbounded today; PyPI now serves 6.0.0, whose headline change is native Amber serialization of stdlib dataclasses — and `Plan`, `Step`, `Fingerprint` and the report classes are all dataclasses.
- [x] **HYG-02**: No new runtime dependency is added. The shipped set stays `pyserial, requests, tqdm, click, rich, packaging`.
- [x] **HYG-03**: A decision is recorded that `dedup_fingerprint` must **not** be refactored to hash `to_dict()`. It is the tempting cleanup and it would make every additive field re-key every historical report — the precise failure this milestone forbids.
- [x] **HYG-04**: Any new `dev_test` helper is registered in `tools/check_devtest_orchestrator.py:152-164`, which silently does not scan what is not listed.

---

## Future Requirements

Tracked, not in this roadmap.

### Session Reuse (R4)

- **R4-01**: `EpromOperator` leases one validated link per plan rather than tearing `self.comm` down after every call (32 connects for one at28c256 run). **Deferred**: its payoff is unmeasured, MEAS-01 gates whether it is worth scoping, and `run_plan`'s non-fatal-step guarantee means a shared link poisons every later step unless the lease is invalidated on any `SerialError`.
- **R4-02**: Folding the VPP and VPE sampler reads is **out of scope in a host-only milestone** — they are two distinct firmware commands (`hardware.py:400-448`), so the seed's −2 connects must not be counted toward any projection.

### Rig Conveyance Leg

- **RIG-01**: A rig-sanity leg that proves the socket is actually connected. Deferred because the only instrument available measures the rail, not the socket (ATTR-06), so such a leg would confirm a healthy rail and still miss the contact fault that motivated it — it would over-claim.

## Out of Scope

| Feature | Reason |
|---|---|
| 999.44 firmware half — region-scoped `mem_util_blank_check` | Host-only milestone. **The product-level bug stays open:** `firestarter write foo.bin -a 0x3FF00` remains refused on any non-erasable part holding data anywhere. Backlog. The backlog's own analysis rejected the host half *alone* on this ground; it is taken knowingly. |
| Replying to or closing gh#21, #23, #28, #31, #45, #50 | This milestone builds the fixes; it does not work the tracker. |
| `MSG_ERR_EMPTY_INPUT` (0xA4) overload — Backlog 999.40 | Firmware change. |
| 64 KiB `Empty input` investigation — Backlog 999.37 | Depends on RPT-C1's counters existing first; the investigation has no instrumentation to stand on until then. |
| `RIG_FAULT` as a sixth `verdict` value | Cardinality change inside the dedup input; re-keys every group that hits it and makes illegal states representable again. |
| Dropping unsupported steps from `Plan.steps` | Re-keys 637 of 677 chips for no serial-traffic saving. |
| `hypothesis`, `jsonschema`, `pydantic`, `jcs`/RFC 8785 | Measured unnecessary. The `derive_plan` domain is 9 behaviour classes exhaustively sweepable in 4.22 s; the schema consumer matches by presence; canonical JSON would make every additive field re-key every historical report. |
| Quoting the cost model's second-counts as acceptance criteria | One log, one Leonardo, one 64 KiB `0x07` part. Criteria are stated in operation counts. |

## Traceability

Populated by `/gsd-new-project` roadmap creation, 2026-09-02.

| Requirement | Phase | Status |
|-------------|-------|--------|
| GATE-01 | Phase 174 | Complete |
| GATE-02 | Phase 174 | Complete |
| GATE-03 | Phase 174 | Complete |
| GATE-04 | Phase 174 | Complete |
| GATE-05 | Phase 174 | Complete |
| GATE-06 | Phase 174 | Complete |
| PRUNE-05 | Phase 175 | Complete |
| PRUNE-06 | Phase 175 | Complete |
| RPT-C1 | Phase 176 | Complete |
| RPT-C2 | Phase 176 | Complete |
| MEAS-01 | Phase 176 | Complete |
| MEAS-02 | Phase 176 | Complete |
| MEAS-03 | Phase 176 | Complete |
| PRUNE-01 | Phase 177 | Complete |
| PRUNE-02 | Phase 177 | Complete |
| PRUNE-03 | Phase 177 | Complete |
| PRUNE-04 | Phase 177 | Complete |
| PRUNE-07 | Phase 177 | Complete |
| ATTR-01 | Phase 178 | Complete |
| ATTR-02 | Phase 178 | Complete |
| ATTR-03 | Phase 178 | Complete |
| ATTR-04 | Phase 178 | Complete |
| ATTR-05 | Phase 178 | Complete |
| ATTR-06 | Phase 178 | Complete |
| UV-01 | Phase 179 | Complete |
| UV-02 | Phase 179 | Complete |
| UV-03 | Phase 179 | Complete |
| PRUNE-08 | Phase 180 | Complete |
| RPT-A1 | Phase 181 | Complete |
| RPT-A2 | Phase 181 | Complete |
| RPT-A3 | Phase 181 | Complete |
| RPT-A4 | Phase 181 | Complete |
| RPT-A5 | Phase 181 | Complete |
| RPT-B1 | Phase 181 | Complete |
| RPT-B2 | Phase 181 | Complete |
| RPT-D1 | Phase 181 | Complete |
| RPT-D2 | Phase 181 | Complete |
| RPT-E1 | Phase 181 | Complete |
| RPT-E2 | Phase 181 | Complete |
| RPT-E3 | Phase 181 | Complete |
| RPT-F1 | Phase 181 | Complete |
| RPT-F2 | Phase 181 | Complete |
| HYG-01 | Phase 181 | Complete |
| HYG-02 | Phase 181 | Complete |
| HYG-03 | Phase 181 | Complete |
| HYG-04 | Phase 181 | Complete |

**Coverage:**

- v1 requirements: 46 total
- Mapped to phases: 46
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-02*
*Sources: `.planning/research/SUMMARY.md` (4 parallel researchers, findings measured against `firestarter_app @ 0a93999`), Backlog 999.36 / 999.43 / 999.44, `.planning/seeds/dev-test-adaptive-sequencing.md`, and community issues gh#21/#23/#28/#31/#45/#50.*
