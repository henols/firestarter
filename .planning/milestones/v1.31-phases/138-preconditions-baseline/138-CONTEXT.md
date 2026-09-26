# Phase 138: Preconditions & Baseline - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Before any v1.31 code moves, all three repos sit on verified branch bases and the pre-change state is
captured as a citable baseline: frozen golden register traces, per-target flash/RAM, native + host
suite counts, and the live per-protocol pulse-width distribution.

**Requirements:** PREP-01, PREP-02, PREP-03, PREP-04.

**This phase measures. It does not change programming behaviour.** No edit to
`firestarter/src/proms/eprom.cpp` — or to any file on the EPROM write path — belongs in Phase 138.
The one exception the discussion deliberately authorised is the *trace-capture instrumentation*
(D-01/D-02/D-04): new opt-in test-stub layers and a frozen fixture, which exist precisely so that
"before" has a meaning. Instrumentation is not behaviour.

</domain>

<decisions>
## Implementation Decisions

### Golden-trace freeze (PREP-03)

The scout found that the roadmap's phrase "the existing golden register traces" has **no referent for
the 27C write path**. The only standalone frozen trace fixture in the repo is
`firestarter/test/native/avr/_shared/sdp_expected.h`, which covers 28C SDP — a different protocol
family, untouched by v1.31. The 27C write path's register assertions live *inline* inside
`test_val_eprom.cpp` via the `HOST_STUBS_RECORD_BUS` stub. There is nothing to freeze. Phase 138
therefore **creates** the artifact rather than freezing an existing one.

- **D-01:** Phase 138 **captures a real write-path trace fixture**, it does not merely record blob
  SHAs. Run the *current* (pre-change) program loop under the recording stub, dump the ordered
  register-write sequence, and commit it. This is the only option under which Phase 144's TEST-06
  criterion — "every changed strobe attributable to a named decision" — is reachable at all; a
  blob-SHA inventory proves file identity and would have left TEST-06 with nothing to diff.
  *Rejected:* blob-SHA inventory only; deferring capture to Phase 144 (the "old" trace would then be
  captured from a tree that already carries the new loop — the baseline would be lost).

- **D-02:** The capture **adds a timing layer**. A third opt-in stub layer intercepts `delay()` /
  `delayMicroseconds()` and interleaves timing entries into the ordered strobe stream.
  **Rationale — this is the crux of the phase.** Neither existing recorder can see time:
  `HOST_STUBS_RECORD_BUS` records `(reg, data)` pairs; `HOST_STUBS_REAL_REGISTER_UTILS` records
  ordered `(kind, pin, value)` strobes; `delay()` / `delayMicroseconds()` are not stubbed at all in
  `host_stubs_common.inc`. v1.31 changes pulse **width** and pulse **count** and adds an overprogram
  pulse — a register/strobe-only trace is blind to every one of those. Without the timing layer the
  frozen trace would diff only the loop's address-stepping restructure, and TEST-06 would cover far
  less than its wording implies.
  *Rejected:* strobes-only with cadence proven solely by TEST-01 unit tests.

- **D-03:** The trace covers a **small synthetic block, all three protocols** (`0x07`, `0x08`,
  `0x0B`). The recorders cap at 256 (`RECORD_BUS`) / 512 (`REAL_REGISTER_UTILS`) entries, so a real
  512-byte block would overflow both immediately — the fixture must be a deliberately-chosen 4–8
  byte block. The bytes are **chosen, not arbitrary**: exercise an already-matching byte, an `0xFF`
  byte, and a byte needing multiple pulses. Per-protocol capture gives Phases 140/141 a per-table-row
  diff, and keeps `0x08`'s overprogram rule and `0x0B`'s energy cap — the two rows with the weakest
  datasheet grounding — from landing with no trace evidence.
  *Rejected:* `0x07`-only.

- **D-04:** The fixture is **immutable + gated by an inventory**. It lands under
  `firestarter/test/native/avr/_shared/` as a v1.31-frozen fixture, pinned by a committed inventory
  JSON under `firestarter/tests/golden/` read by a python gate — the exact
  `sdp_expected.h` + `sdp_expected_inventory.json` + `test_golden_trace_identity.py` triple already
  proven in this repo. Two independent mechanisms read the fixture, so a change to either alone is
  visible. *Rejected:* planning-artifact-only (nothing would enforce it, and Phase 144 would have to
  re-import it to diff).

- **Hard constraint carried into planning:** the new stub layer must be **opt-IN** and flag-off must
  leave all pre-existing native suites **byte-exact**, per the Phase 116 D-05/D-07 precedent already
  documented in `host_stubs_common.inc`. `HOST_STUBS_REAL_REGISTER_UTILS`'s own header comment states
  the rule ("no existing suite may define it — flag off is byte-exact") and is the pattern to copy.

### Baseline form (PREP-03)

- **D-05:** **Frozen JSON + planning record.** Re-measure **cold** at `beta` @ `3085084` and commit an
  immutable `firestarter/scripts/baseline/size_baseline_v131.json` alongside the existing BASE-01 —
  **never rewriting the live `size_baseline.json`**, whose pre-change figures TEST-08 must compare
  against. Pair it with a `.planning/` narrative artifact in the style of
  `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md`. Machine-checkable *and*
  human-citable. *Rejected:* rewriting the live baseline in place (Phase 124 Plan 10's precedent —
  correct there, destructive here); planning-record-only (TEST-08's delta would be prose-vs-prose).

- **D-06:** Evidence is **local cold measurement AND an operator-dispatched CI run** per repo. The
  agent takes cold local measurements and reads the CI runs **read-only**, recording run ids as
  `131-CI-BASELINE.md` did. Two reasons this is not optional: `gh workflow run` is blocked by the
  auto-mode classifier, so a dispatch is inherently an operator action; and the devcontainer's
  Python 3.12 masks the app's py39/3.11 CI, which has burned this project before — TEST-03's later
  CI-scoped claim would otherwise rest on an unmeasured base.
  **Cold-measurement procedure is not optional either:** `rm -rf .pio/build/<env>` then a *single*
  `pio` invocation with an extended timeout. A default 2-minute Bash timeout truncates the toolchain
  build mid-compile and silently contaminates the figure — recorded as a live trap in
  `size_baseline.json`'s own `meta.note`, and the mechanism behind BASE-01's warm-vs-cold 360-vs-456
  correction. Never guess a figure down from prose or from a warm re-run.

- **D-07:** If re-measurement shows `check_size_baseline.py` is **already RED** at `beta` @ `3085084`
  — plausible, since the live baseline was measured at Phase 124's tree (`2bd7187`) and v1.23 phases
  125–130 landed afterwards — **record it, do not fix it.** Capture the discrepancy as a named
  finding with an explicit owner and carry it as inherited v1.23-era debt. Repairing a load-bearing
  gate inside the phase that exists to define "before" would corrupt the measurement.
  *Rejected:* fixing it in Phase 138.

### Branch bases (PREP-01, PREP-02)

- **D-08:** **PREP-01 runs as agent-opens-PR, operator-merges.** An agent opens the PR from the
  staged `.planning/v1.30-PR-BODY.md`; the operator reviews and merges; the phase then verifies with
  `git merge-base --is-ancestor`. This honours v1.30's recorded "close via a PR to beta, not a direct
  merge" decision and keeps the outward-facing merge under the operator's hand.
  **Known and accepted consequence:** `firestarter_app/.github/workflows/beta-release.yml` fires on
  **every** push to `beta` with no paths-ignore filter, so this merge **will cut a new app
  pre-release**. That is expected, not a surprise to be discovered mid-phase. Planning must not treat
  the resulting version bump as an anomaly.
  *Rejected:* operator does both steps (stalls the phase twice); agent merges directly (breaks the
  v1.30 decision and silently publishes a beta).

- **D-09:** All three repos use the **identical branch slug**:
  `gsd/v1.31-27c-programming-algorithm-fidelity` in meta, `firestarter`, and `firestarter_app` alike.
  In v1.30 the meta and submodule names diverged and that divergence caused a real dispatch error.
  One name, read the same way by every executor dispatch and by PREP-02's verification.
  *Rejected:* a shorter sub-repo slug.

- **Verified during this discussion, not assumed** (re-verify at execution, do not restate from here):
  - `firestarter_app`'s `gsd/v1.30-sdp-surface-retirement` is **NOT** an ancestor of `origin/beta` —
    `git merge-base --is-ancestor` exits 1, **85 commits unmerged**. PREP-01 is genuinely open.
  - `firestarter`'s `origin/beta` tip **is exactly `3085084`** ("Apply automatic changes"), so the
    roadmap's stated firmware base is current with no drift. There is no local `beta` branch in the
    firmware repo — only `origin/beta`.
  - Meta is already on `gsd/v1.31-27c-programming-algorithm-fidelity`. Neither sub-repo has a v1.31
    branch yet.
  - The app's post-merge fork base is the beta tip **after** `beta-release.yml`'s auto-commit version
    bump — name that commit, do not fork from the pre-bump tip.

### Pulse distribution (PREP-04)

- **D-10:** PREP-04 ships as a **committed reproducible script** plus its committed output, following
  136.1's reproducible fetch-based re-derivation pattern — not a one-off measurement pasted into
  markdown. C2 is the correction being **posted publicly to gh#15** in Phase 139; a number a stranger
  cannot re-run is the weakest link in that comment.
  *Rejected:* one-off measurement into a markdown artifact.

- **D-11:** The artifact must state **which layer it counts**. The database field is
  `pulse_duration` — a *string* like `"100 us"` — parsed into the integer-µs wire field `pulse-delay`
  by `_parse_pulse_duration` at `firestarter_app/firestarter/database.py:128`. REQUIREMENTS.md says
  `pulse_duration` and PROJECT.md says `pulse_delay`; **both are correct at different layers** — this
  is not a defect and needs no reconciliation, but the artifact must not be ambiguous about it.
  Absent / unparseable / zero values get their own explicit bucket rather than being silently dropped
  from the denominator.

### Claude's Discretion

- Where the PREP-04 script lives (`firestarter_app/tools/` vs the phase directory) — planner's call,
  subject to the project's "skills must own their scripts" rule where applicable.
- The exact synthetic byte pattern and block length for the trace fixture, within the 256/512 entry
  caps and D-03's three required cases.
- Plan sequencing and wave structure. Note the real dependency shape: PREP-01 gates only the **app**
  half of PREP-02; the firmware/meta halves of PREP-02, all of PREP-03's firmware measurement, and
  all of PREP-04 are independent of it and need not wait on the operator merge.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone decision record (locked — do not re-litigate)
- `.planning/PROJECT.md` §"Current Milestone: v1.31 27C Programming-Algorithm Fidelity (gh#15)" —
  the C1/C2/C3 correction table, D-01 (protocol owns shape, DB owns pulse), D-02 (`0x0B` energy
  cap), the 6.25 V evidence ceiling, asymmetric bench coverage, and the branch model.
- `.planning/ROADMAP.md` §"v1.31 — 27C Programming-Algorithm Fidelity (gh#15)" and §"Phase 138:
  Preconditions & Baseline" — phase goal, the four success criteria, the sequencing spine, locked
  decisions D-04…D-08, and the binding must-not-do list.
- `.planning/REQUIREMENTS.md` §"Preconditions & Baseline" — PREP-01…PREP-04 verbatim.
- `.planning/seeds/27c-algorithm-fidelity-param-table-refactor.md` — the `/gsd-explore` correction
  pass (commit `c60543c5`) this milestone is derived from.
- `.planning/MILESTONES.md` §v1.30 — the shipped record PREP-01 makes true.
- https://github.com/henols/firestarter_prom/issues/15 — gh#15, scoped **as corrected**, not as filed.

### Baseline machinery (reuse, do not reinvent)
- `firestarter/scripts/baseline/size_baseline.json` — the LIVE, load-bearing baseline. Read
  `meta.note` and `meta.warm_vs_cold_correction` **before measuring anything**: they record the cold
  vs warm trap and the exact measurement sequence. Do not rewrite this file (D-05).
- `firestarter/scripts/baseline/size_baseline_base01.json` — immutable BASE-01; the freeze pattern
  `size_baseline_v131.json` should copy.
- `firestarter/scripts/check_size_baseline.py` — consumes the baseline via the
  `FIRESTARTER_SIZE_BASELINE` env seam; the gate D-07 may find already RED.
- `firestarter/scripts/check_build_warnings.py` — the native warning watermark gate, same seam.
- `.planning/phases/131-gate-hardening-ci-parity/131-CI-BASELINE.md` — the narrative-artifact
  precedent for D-05/D-06, including the fail-closed run-id preconditions and the
  `outcome`-vs-`conclusion` distinction.

### Trace machinery (the fixture pattern to copy)
- `firestarter/test/native/avr/_shared/host_stubs_common.inc` — both recorder layers.
  `HOST_STUBS_RECORD_BUS` (`(reg, data)`, cap 256) and `HOST_STUBS_REAL_REGISTER_UTILS`
  (ordered `(kind, pin, value)` strobes, cap 512, Phase 116 TRACE-01 / D-05 / D-07). Its own comments
  state the opt-IN + flag-off-byte-exact contract the new timing layer must satisfy.
- `firestarter/test/native/avr/_shared/sdp_expected.h` — the frozen-fixture form to copy.
- `firestarter/tests/golden/sdp_expected_inventory.json` — the committed inventory to copy.
- `firestarter/tests/test_golden_trace_identity.py` — the two-independent-mechanisms gate to copy,
  including its fail-closed "git is required, not optional" discipline.
- `firestarter/test/native/avr/test_val_eprom/` — where the 27C write path's register assertions live
  today (`host_stubs.cpp` + `test_val_eprom.cpp`), and the suite the new fixture sits beside.
- `firestarter/test/native/avr/_shared/validation_matrix.h` — generated; confirms `0x07`/`0x08`/`0x0B`
  all route to `configure_eprom`.

### The code being baselined (read-only in this phase)
- `firestarter/src/proms/eprom.cpp` — the write path v1.31 replaces. Cited lines verified live this
  session: `:20` `NUMBER_OF_RETRIES`, `:69-77` the `pulse_delay == 0` protocol fallback, `:118`
  `delay(10)` VPE settle, `:177` the adaptive pulse-growth formula, `:283`
  `delayMicroseconds(handle->pulse_delay)`. **Phase 138 must not edit this file.**

### Host-side field semantics (PREP-04)
- `firestarter_app/firestarter/database.py:128` — `_parse_pulse_duration`, the `pulse_duration`
  string → `pulse-delay` int-µs conversion at the heart of D-11.
- `firestarter_app/firestarter/data/chip_database.json` — the shipped DB PREP-04 measures.
  **Generated — never hand-edit.**
- `firestarter_app/doc/infoic-field-dictionary.md:210-217` — where C1's 500 µs adjudication lives.

### Operator-gated actions
- `.planning/v1.30-PR-BODY.md` — the staged, never-opened PR body PREP-01 opens.
- `firestarter_app/.github/workflows/beta-release.yml` — read its header comment: fires on every push
  to `beta`, paths-ignore deliberately removed. This is why PREP-01 cuts a pre-release.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`scripts/baseline/size_baseline*.json` + `check_size_baseline.py` + `check_build_warnings.py`** —
  a mature, load-bearing baseline system with an `FIRESTARTER_SIZE_BASELINE` env seam and an
  established immutable-freeze convention (BASE-01). PREP-03 extends it; it does not build anything
  new.
- **`sdp_expected.h` / `sdp_expected_inventory.json` / `test_golden_trace_identity.py`** — a complete,
  proven three-part frozen-fixture pattern (blob-SHA identity + per-array inventory + non-vacuity +
  load-bearing-consumer check). D-04 copies it wholesale for the trace fixture.
- **`HOST_STUBS_REAL_REGISTER_UTILS`** — an existing opt-in strobe recorder that already drives
  production's real cache-compare elision rather than a drift-prone replica. The timing layer (D-02)
  composes with it, mirroring how that layer composes with `HOST_STUBS_RECORD_BUS`.
- **`131-CI-BASELINE.md`** — a worked example of the narrative baseline artifact D-05 wants, with
  fail-closed run-id preconditions already written out.

### Established Patterns
- **Opt-IN stub guards with a byte-exact flag-off contract.** Every recorder layer in
  `host_stubs_common.inc` is opt-in and documents that no pre-existing suite may define it. The
  timing layer must follow this or it breaks 14 suites.
- **Two independent mechanisms per frozen artifact.** The file and its recorded expectation are read
  by separate readers and compared, so a change to either alone is visible. Applies to both the trace
  fixture and the size baseline.
- **Cold-vs-warm measurement discipline.** `rm -rf` + a single extended-timeout invocation; warm
  figures are contamination. Documented in-repo with a worked correction.
- **Operator-gated outward actions.** CI dispatches, PR merges, and issue posts are operator actions;
  agents read results read-only and record run ids.

### Integration Points
- The new timing layer plugs into `test/native/avr/_shared/host_stubs_common.inc` alongside the two
  existing recorders.
- The new fixture + inventory plug into the `tests/` python gate suite, which already runs
  `test_golden_trace_identity.py`, `test_check_size_baseline.py`, and `test_check_build_warnings.py`.
- `size_baseline_v131.json` sits beside BASE-01 under `scripts/baseline/`, read through the existing
  env seam rather than a new one.

</code_context>

<specifics>
## Specific Ideas

- The trace fixture's byte pattern is **deliberate**: an already-matching byte, an `0xFF` byte, and a
  byte requiring multiple pulses — the three cases LOOP-04 and TEST-01 later assert on. It is a
  designed probe, not a sample of real data.
- The baseline artifact should read like `131-CI-BASELINE.md`: every figure attributed to the exact
  command that produced it, run ids named, and any discrepancy against a prior record stated as a
  finding rather than silently reconciled.
- PREP-04's output is written to be **quoted verbatim into a public GitHub comment** in Phase 139.
  Format it for that audience — a stranger who cannot run the repo should still be able to follow it,
  and one who can should be able to reproduce it exactly.

</specifics>

<deferred>
## Deferred Ideas

- **Repairing the (possibly RED) live `size_baseline.json`** — per D-07 this phase records the
  discrepancy and names an owner rather than fixing it. It is v1.23-era inherited debt, not v1.31's.
- **Authoring the *new*-cadence trace** — Phase 138 freezes only the pre-change trace. TEST-06 in
  Phase 144 authors the new one and reviews the diff.

### Reviewed Todos (not folded)

All four keyword matches were reviewed and **deliberately not folded**. They matched on shared
vocabulary (`firmware`, `phase`, `cpp`, `firestarter`), not on scope; folding firmware behaviour
changes into the phase whose purpose is to measure the pre-change state would contaminate the very
measurement it exists to take.

- **"Prove the PlatformIO dev-tools build flag fails CLOSED"** (`prove-pio-dev-flag-fails-closed.md`,
  score 0.9) — genuinely adjacent, since Phase 138 already builds every target cold. Still deferred:
  it is a new *gate*, not a *measurement*.
- **"Skip VPP error/warning checks when VPP is unused (reads/blank-checks)"**
  (`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`, score 0.9) — a
  firmware behaviour change in VPP territory. Overlaps **Phase 142**, not 138.
- **"AT28C256 write-path failure (gh#20)"** (`at28c256-write-path-failure-gh20.md`, score 0.6) — a
  live defect on a 28C part, protocol `0x0D`. Different family, different milestone's problem.
- **"Skill: triage `dev test` issues"** (`2026-08-05-dev-test-issue-triage-diagnosis-skill.md`,
  score 0.6) — tooling, unrelated to this milestone.

</deferred>

---

*Phase: 138-Preconditions & Baseline*
*Context gathered: 2026-08-08*
