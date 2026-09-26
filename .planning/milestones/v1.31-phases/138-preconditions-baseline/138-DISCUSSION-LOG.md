# Phase 138: Preconditions & Baseline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-08
**Phase:** 138-Preconditions & Baseline
**Areas discussed:** Golden-trace freeze form, Baseline artifact form, PREP-01 execution split,
Todo folding, Trace timing content, Trace scope, CI evidence, Fixture home, Branch naming,
PREP-04 derivation, Stale-gate contingency

---

## Golden-trace freeze form

Framing: PREP-03 says "the existing golden register traces frozen as a historical artifact," but
scouting found the 27C write path has no trace artifact — its register assertions are inline in
`test_val_eprom.cpp`. TEST-06 later demands "every changed strobe attributable to a named decision."

| Option | Description | Selected |
|--------|-------------|----------|
| Capture a real trace fixture | Run the current loop under `HOST_STUBS_RECORD_BUS`, dump the ordered register-write sequence to a committed fixture + inventory JSON. Real engineering in a "no code moves" phase, but the only option making TEST-06's strobe-level diff reachable. | ✓ |
| Blob-SHA inventory only | Freeze EPROM-touching test files by blob SHA + per-array inventory, reusing `test_golden_trace_identity.py` verbatim. Cheap and precedented, but proves file identity, not strobe behavior — TEST-06 would have nothing to diff. | |
| Defer the capture to Phase 144 | Record only that no write-path trace exists; TEST-06 authors both traces later. Keeps 138 mechanical, but the "old" trace would come from a tree already carrying the new loop. | |

**User's choice:** Capture a real trace fixture
**Notes:** Drove the four follow-up questions below (timing content, scope, fixture home).

---

## Baseline artifact form

Framing: the live `size_baseline.json` was measured at Phase 124's tree (`2bd7187`); v1.23 phases
125–130 landed after it.

| Option | Description | Selected |
|--------|-------------|----------|
| Frozen JSON + planning record | Re-measure cold at `beta`@`3085084`, commit an immutable `size_baseline_v131.json` beside BASE-01 (never rewriting the live file), plus a `.planning/` narrative in `131-CI-BASELINE.md` style. | ✓ |
| Rewrite the live `size_baseline.json` in place | Phase 124 Plan 10's precedent — simplest, but destroys the pre-change figures TEST-08 must compare against. | |
| Planning-record only, no JSON | Markdown artifact only, both JSONs untouched. Zero gate risk, but TEST-08's delta becomes prose-vs-prose. | |

**User's choice:** Frozen JSON + planning record

---

## PREP-01 execution split

Framing: merging `gsd/v1.30-sdp-surface-retirement` (85 commits) into `origin/beta` will fire
`beta-release.yml` and cut a new `firestarter_app` pre-release.

| Option | Description | Selected |
|--------|-------------|----------|
| Agent opens PR, operator merges | Agent opens the PR from `.planning/v1.30-PR-BODY.md` and stops; operator merges; phase verifies with `git merge-base --is-ancestor`. Matches v1.30's "close via PR" decision and keeps the beta cut under the operator's hand. | ✓ |
| Operator does PR and merge entirely | Phase writes a handoff naming exact commands. Maximum control, but stalls the phase twice. | |
| Agent merges directly, no PR | Fastest, but breaks v1.30's recorded decision and silently publishes a beta. | |

**User's choice:** Agent opens PR, operator merges
**Notes:** The resulting pre-release is accepted as expected behaviour, recorded in CONTEXT.md so
planning does not treat the version bump as an anomaly.

---

## Todo folding

Framing: four pending todos matched Phase 138 by keyword; none looked in-scope for a phase whose
purpose is "no code moves yet."

| Option | Description | Selected |
|--------|-------------|----------|
| Fold none | Record all four as reviewed-but-deferred. They matched on shared vocabulary, not scope. | ✓ |
| Prove the PlatformIO dev-tools flag fails CLOSED | Adjacent — 138 already builds all targets cold — but a new gate, not a measurement. | |
| Skip VPP checks when VPP unused on reads | Firmware behaviour change; overlaps Phase 142. | |
| AT28C256 write-path failure (gh#20) | Live defect on a 28C part, protocol `0x0D`. Different family. | |

**User's choice:** Fold none

---

## Trace timing content

Framing (the pivotal finding): `HOST_STUBS_RECORD_BUS` records `(reg, data)` pairs;
`HOST_STUBS_REAL_REGISTER_UTILS` records ordered `(kind, pin, value)` strobes; **neither records
time** — `delay()` / `delayMicroseconds()` are not stubbed at all. v1.31 changes exactly pulse width
and pulse count.

| Option | Description | Selected |
|--------|-------------|----------|
| Add a timing layer | A third opt-in stub layer intercepts `delay()`/`delayMicroseconds()` and interleaves timing into the strobe stream, so the frozen trace encodes cadence. Most work; the only version where the trace is evidence for this milestone's claim. | ✓ |
| Strobes only, cadence proven by unit tests | Freeze the existing strobe trace unchanged; TEST-01 carries the cadence proof. Cheaper, no shared-stub edit — but the diff shows only loop restructuring. | |
| You decide | Let the researcher measure the cost in the shared `.inc` and recommend. | |

**User's choice:** Add a timing layer

---

## Trace scope

Framing: the recorders cap at 256/512 entries; a real 512-byte block write overflows both.

| Option | Description | Selected |
|--------|-------------|----------|
| Small synthetic block, all 3 protocols | 4–8 deliberately-chosen bytes (already-matching, `0xFF`, multi-pulse), captured once per `0x07`/`0x08`/`0x0B`. Fits the caps; gives Phases 140/141 a per-row diff. | ✓ |
| Small synthetic block, `0x07` only | Smallest artifact — but `0x08`'s overprogram rule and `0x0B`'s energy cap would land with no trace evidence, and those have the weakest datasheet grounding. | |
| You decide | Let the planner pick from what Phase 140's table rows need. | |

**User's choice:** Small synthetic block, all 3 protocols

---

## CI evidence

Framing: `gh workflow run` is blocked by the auto-mode classifier, so a dispatch is an operator
action; the devcontainer's py3.12 also masks the app's py39/3.11 CI.

| Option | Description | Selected |
|--------|-------------|----------|
| Local cold + operator CI dispatch | Agent measures cold locally AND operator dispatches one CI run per repo; agent reads read-only and records run ids, as `131-CI-BASELINE.md` did. Catches CI-only defects the devcontainer hides. | ✓ |
| Local cold measurements only | No operator action, faster — but the devcontainer/CI Python split has burned this project, and TEST-03's later CI-scoped claim would rest on an unmeasured base. | |
| You decide | Per-repo split, e.g. CI dispatch for the app, local-only for firmware. | |

**User's choice:** Local cold + operator CI dispatch

---

## Fixture home

| Option | Description | Selected |
|--------|-------------|----------|
| Immutable fixture + inventory gate | Fixture under `test/native/avr/_shared/`, pinned by a committed inventory JSON in `tests/golden/` read by a python gate — the proven `sdp_expected.h` triple. Two independent readers. | ✓ |
| Planning artifact only | Captured into the phase dir, never compiled. Zero risk, but nothing enforces it and Phase 144 would re-import to diff. | |
| You decide | Planner chooses based on the timing layer's cost. | |

**User's choice:** Immutable fixture + inventory gate

---

## Branch naming

Framing: meta is already on `gsd/v1.31-27c-programming-algorithm-fidelity`; in v1.30 the meta and
submodule names diverged and caused a dispatch mistake.

| Option | Description | Selected |
|--------|-------------|----------|
| Identical slug in all three | `gsd/v1.31-27c-programming-algorithm-fidelity` everywhere. Long, but this project's divergence has already caused a real error. | ✓ |
| Short slug in the sub-repos | Shorter to type at the bench — but reproduces the v1.30 divergence. | |
| You decide | Planner picks and records it once. | |

**User's choice:** Identical slug in all three

---

## PREP-04 derivation

Framing: PREP-04's distribution is quoted as C2's evidence in the Phase 139 gh#15 comment.

| Option | Description | Selected |
|--------|-------------|----------|
| Committed reproducible script | Script reads the shipped `chip_database.json` and emits the distribution; output committed alongside. Anyone reading gh#15 can re-run it. Follows 136.1's pattern. | ✓ |
| One-off measurement into markdown | Faster — but a number a stranger can't reproduce is the weakest link in a public correction. | |
| You decide | Planner chooses; if a script, decide where it lives. | |

**User's choice:** Committed reproducible script

---

## Stale-gate contingency

Framing: if re-measuring at `beta`@`3085084` shows `check_size_baseline.py` is already RED before
v1.31 touches anything.

| Option | Description | Selected |
|--------|-------------|----------|
| Record it, don't fix it | Capture as a named finding with an explicit owner; carry as inherited v1.23-era debt. 138's job is to measure. | ✓ |
| Fix it in Phase 138 | Re-point the live baseline so the gate is green before v1.31 starts. Clean tree, but expands a preconditions phase into a repair phase for someone else's debt. | |
| You decide | Planner decides once the delta is known. | |

**User's choice:** Record it, don't fix it

---

## Claude's Discretion

- Location of the PREP-04 script (`firestarter_app/tools/` vs the phase directory).
- The exact synthetic byte pattern and block length for the trace fixture, within the entry caps and
  the three required cases.
- Plan sequencing and wave structure — PREP-01 gates only the app half of PREP-02; the firmware/meta
  halves, PREP-03's firmware measurement, and all of PREP-04 are independent of the operator merge.

## Deferred Ideas

- Repairing the possibly-RED live `size_baseline.json` — recorded, not fixed (D-07); v1.23-era debt.
- Authoring the *new*-cadence trace — Phase 138 freezes only the pre-change trace; TEST-06 in
  Phase 144 authors the new one and reviews the diff.
- All four keyword-matched todos, deferred with reasons (see CONTEXT.md `<deferred>`).
