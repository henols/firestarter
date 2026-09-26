# Phase 147: Report Provenance — every `dev test` report names its firmware - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-18
**Phase:** 147-Report Provenance — every `dev test` report names its firmware
**Areas discussed:** Capture seam, PROV-03 stale premise, Unknown rendering, Triage attribution

**Area selection:** all four offered areas selected.

---

## Capture seam

### Q1 — Where should `fw_board_identity` be captured from?

| Option | Description | Selected |
|--------|-------------|----------|
| Piggyback the hw-revision read | `read_hardware_revision_value()` already opens one SAFE-02-clean connection, and `_probe_port` sets `comm.firmware_identity` on it before the revision ack. Zero extra connections, no new firmware command, gate never sees new code. | ✓ |
| Dedicated sibling read in hardware.py | New `read_firmware_identity_value()` mirroring the handshake. Clean separation, but a second connection to read a string the first already had. | |
| Latch it on EpromOperator | Operator records the identity during the plan's own operations. Zero extra connections and closest to PROV-01's literal intent, but adds mutable state to a class every command shares. | |

**User's choice:** Piggyback the hw-revision read.
**Notes:** Scout established that the CAP-02 ack tail carries the full identity on every connect, so this needs no new command and no firmware change.

### Q2 — How should the method hand back two values from one connection?

| Option | Description | Selected |
|--------|-------------|----------|
| New pair-returning method, old one kept | Add a sibling returning both; old method byte-unchanged for other callers. Cost: two methods sharing a handshake shape. | |
| Widen the existing method's return | One method, no duplication; the only production call site is the one being edited anyway. Cost: a signature change plus test-mock updates. | ✓ |
| Stash identity on the HardwareManager | Keep the signature; record the identity on the instance. Smallest diff, but a side-channel invisible at the call site. | |

**User's choice:** Widen the existing method's return.
**Notes:** `read_hardware_revision_value` has exactly one production caller (`cli_handlers.py:2501`), so the churn is test mocks rather than production code.

### Q3 — What should the widened method be named and return?

| Option | Description | Selected |
|--------|-------------|----------|
| Rename + NamedTuple | `read_programmer_identity() -> ProgrammerIdentity(hw_revision, fw_board_identity)`. Named fields stop a silent swap from type-checking clean. `hardware.py` is scanned by no AST gate. | ✓ |
| Rename + plain tuple | Honest name, least machinery. Cost: positional unpacking of two `str \| None` values. | |
| Keep the name, return a tuple | Smallest diff; docstrings stay valid. Cost: a drifted name this project keeps paying to correct later. | |

**User's choice:** Rename + NamedTuple.

### Q4 — On a not-OK revision ack, when the identity is already captured, what is returned?

| Option | Description | Selected |
|--------|-------------|----------|
| Return the identity anyway | The two values fail independently — identity from the connect ack, revision from the command ack. A board without `HARDWARE_REVISION` still yields an attributable report. | ✓ |
| Both None on any failure | One failure posture, one test. Cost: discards a value already in hand, exactly for the odd boards where attribution matters most. | |
| You decide | Defer to the planner. | |

**User's choice:** Return the identity anyway.

---

## PROV-03 stale premise

### Q1 — Does Phase 147 touch the `[\d.x]+` version gate?

| Option | Description | Selected |
|--------|-------------|----------|
| Leave the gate alone | Record `comm.firmware_identity` verbatim; the ring-fenced version-capture path is untouched. PROV-03's criterion is about the recorded string, which is already suffix-preserving. | ✓ |
| Widen the gate too | Make `_validate_firmware_version` suffix-aware. Cost: edits a ring-fenced path, re-baselines two guard test files, delivers a capability no v1.32 requirement asks for. | |
| Leave it, and file the gate widening as a todo | Same, plus a standing todo. | |

**User's choice:** Leave the gate alone.
**Notes:** The gate widening was captured as a deferred idea in CONTEXT.md rather than as a todo file.

### Q2 — How is PROV-03's / criterion #2's false premise reconciled?

| Option | Description | Selected |
|--------|-------------|----------|
| Correct REQUIREMENTS.md + ROADMAP.md now | Hand-edit before planning to state the measured finding. Precedent: this milestone's own HEAD commit corrects a charter claim. | ✓ |
| Record it in CONTEXT.md only | Least churn on tracked artifacts. Cost: the roadmap keeps asserting something false; a verifier without CONTEXT.md can produce a false RED. | |
| CONTEXT.md now, correct at close | Stable artifacts during execution. Cost: the false premise stays live through the phase — exactly when it can do damage. | |

**User's choice:** Correct REQUIREMENTS.md + ROADMAP.md now.
**Notes:** Flagged the `_normalizeMd` whole-file reformat hazard — hand edits, snapshot and diff.

### Q3 — Posture on a corrupt / mangled identity string?

| Option | Description | Selected |
|--------|-------------|----------|
| Verbatim, but scrub non-printables | Follows the `_sanitize_chip_token` precedent; a mangled identity stays visible as transport-fault evidence and is safe in a public issue body. | ✓ |
| Verbatim, no processing at all | Absolute honesty, zero new code. Cost: control characters can reach a public issue body. | |
| Plausibility-clamp to unknown | Mirrors CAP-01/CAP-03's "implausible → absent" convention. Cost: discards fault evidence; would reject a legitimate future format. | |

**User's choice:** Verbatim, but scrub non-printables.

### Q4 — What oracle proves PROV-03?

| Option | Description | Selected |
|--------|-------------|----------|
| Differing-pair discrimination test | Two identities differing only in prerelease suffix must land as two different recorded values — the actual b11-vs-b12 discrimination. | ✓ |
| Single round-trip assertion | Simple. Cost: passes vacuously if suffixes are later normalised away. | |
| Structural test that the regex isn't on the path | Catches the feared regression. Cost: couples to an implementation detail, not observable behaviour. | |

**User's choice:** Differing-pair discrimination test.

---

## Unknown rendering

### Q1 — Does the fenced JSON carry a sentinel instead of `null`?

| Option | Description | Selected |
|--------|-------------|----------|
| JSON stays `null`, tighten PROV-05's wording | Typed absence for machines; marker in the two human surfaces; PROV-04's compat story stays one case. | ✓ |
| Sentinel string in the JSON too | Most literal reading of PROV-05 as written. Cost: the field becomes str-always, `is None` consumers break, old-null vs new-sentinel become two parser cases. | |
| You decide | Defer to the planner. | |

**User's choice:** JSON stays `null`, tighten PROV-05's wording.

### Q2 — What should the explicit-unknown marker say?

| Option | Description | Selected |
|--------|-------------|----------|
| New identity-specific constant | e.g. `NOT_REPORTED = "not reported"` beside `NOT_MEASURED`, single-sourced, reused by both human surfaces. | ✓ |
| Reuse NOT_MEASURED ("not measured") | One constant, already gate-covered. Cost: wrong verb for an identity; conflates "asked and got nothing" with "never asked". | |
| Reason-bearing marker | Follows `sdp_hold_state`'s `NOT-RUN: <reason>`. Cost: needs a reason threaded through the NamedTuple, and the realistic reason space is nearly empty. | |

**User's choice:** New identity-specific constant.

### Q3 — How far does the None-rendering fix reach in the rich table?

| Option | Description | Selected |
|--------|-------------|----------|
| Both identity fields | `fw_board_identity` and `hw_revision` — shared origin, shared semantics, adjacent rows. `protocol` / `chip_id` left alone. | ✓ |
| Only fw_board_identity | Strictly PROV-05's scope. Cost: ships a visibly inconsistent table with an identical defect one line away. | |
| Every None-rendering row | Full consistency. Cost: `chip_id`'s None is informative and `protocol` can't be None on a submittable report. | |

**User's choice:** Both identity fields.

### Q4 — Where is the unknown leg proven?

| Option | Description | Selected |
|--------|-------------|----------|
| Render-level + handler-level via the mock seam | `AutoCapture(None)` asserting the marker in both the rich table and `render_diff`, plus a handler test with the `HardwareManager` mock returning `(None, None)`. | ✓ |
| Render-level only | Fast, no mock plumbing. Cost: doesn't prove the handler threads None rather than crashing. | |
| Handler-level only | Proves the real path. Cost: doesn't independently pin `render_diff`. | |

**User's choice:** Render-level + handler-level via the mock seam.
**Notes:** Framed against the finding that `_probe_port` refuses identity-less firmware, so the leg is defensive rather than a field scenario — it must still be seen to pass.

---

## Triage attribution

### Q1 — Plain line, or a not-attributable call-out in `render_diff`?

| Option | Description | Selected |
|--------|-------------|----------|
| Labelled line + explicit not-attributable call-out | Normal case shows the value; unknown case adds a clause saying the report cannot carry a firmware claim. Mirrors the existing "maintainer decision input" labelling style. | ✓ |
| Plain labelled line only | Minimal and uniform. Cost: the triager must infer the implication. | |
| Line + a machine-readable attributable flag | Enables downstream filtering. Cost: dead data — the same shape as `protect_on_after`. | |

**User's choice:** Labelled line + explicit not-attributable call-out.

### Q2 — Which provenance fields does the triage render carry?

| Option | Description | Selected |
|--------|-------------|----------|
| Firmware identity + host_version | Both halves of the version pair on one screen; "host 3.0.0b15 against unknown firmware" is the half-answer that made gh#21 undiagnosable. | ✓ |
| Firmware identity only | Strictly PROV-06's scope. Cost: the triager reads one version from the parser and hunts the other by hand. | |
| All three — firmware, host, hw_revision | Complete block. Cost: `hw_revision` cannot distinguish the operator's three boards — authoritative-looking and uninformative. | |

**User's choice:** Firmware identity + host_version.

### Q3 — Which `[dev test]` parser gets the field?

| Option | Description | Selected |
|--------|-------------|----------|
| Both | The app tool is PROV-06's named surface; the devtest-triage skill's `show` is what triage actually uses (and prints `hw None` today). Skills own their scripts — two deliberate edits, not a shared import. | ✓ |
| App tool only | Single repo, single test file. Cost: requirement met on paper, not in practice. | |
| Skill only | Fixes the used surface. Cost: leaves the named surface untouched, and the app tool is the one with committed CI tests. | |

**User's choice:** Both.
**Notes:** Surfaced during scouting — PROV-06 names one parser but two exist. `.claude/skills/` is un-ignored and therefore committable, but not yet committed.

### Q4 — Does the render distinguish an old-report null from a post-bump capture failure?

| Option | Description | Selected |
|--------|-------------|----------|
| One action-oriented clause, no version logic | A single clause true under either reading, pointing at the action. Preserves both parsers' "schema_version by presence only" posture and survives the live `"9.9-future"` fixture. | ✓ |
| Schema-aware clause | Sharpest triage signal. Cost: introduces version ordering into parsers that never compare schema values. | |
| Single clause in code, distinction as skill prose | No version logic anywhere. Cost: guidance sits one hop from the output. | |

**User's choice:** One action-oriented clause, no version logic.

---

## Claude's Discretion

- Exact constant name and marker wording (`NOT_REPORTED` / `"not reported"` is a suggestion).
- Exact `ProgrammerIdentity` NamedTuple name and field order (fields must be named).
- Exact phrasing of the not-attributable clause, subject to the claim gate.
- Whether the capture moves relative to `run_plan` — default is to keep it where it is today.
- `SCHEMA_VERSION` 1.3 → 1.4 was decided without a question: precedent-settled by the 1.3 note's
  explicit rejection of an unbumped artifact change.

## Deferred Ideas

- Suffix-aware firmware version gating (`packaging.version` in `_validate_firmware_version`) — no
  v1.32 requirement needs it; prefer detect-over-gate when one does.
- A reason-bearing unknown marker for the identity field.
- A machine-readable `attributable` flag in the report.
- Extending explicit-unknown rendering to `protocol` / `chip_id`.

## Todos reviewed, none folded

20 pending todos matched Phase 147 on keyword noise only. Full list with per-item reasons is in
CONTEXT.md `<deferred>` §"Reviewed Todos (not folded)". The two genuinely relevant items already map
to Phase 152 (gh#12 reply) and Phase 150 (`write --sdp-relock`).
