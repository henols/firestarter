# Phase 110: Diagnostic Report Model + Dual Output + Provenance Prompts - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning
**Mode:** `--auto` (decisions auto-selected to the recommended default; see the per-decision `[auto]` log in `110-DISCUSSION-LOG.md`)

<domain>
## Phase Boundary

Build the **`DiagnosticReport` model** — the single source object that every
`dev test` run produces (whether or not it's ever submitted), rendered two ways
from one source with no duplicated logic, plus the human-only provenance prompt
component and the advisory DB-diff. Concretely:

1. **RPT-01 — one source, two renders + `schema_version`.** A `DiagnosticReport`
   dataclass composing the Phase-108 `Plan` / `StepResult` / `Fingerprint`
   objects + new auto-capture, provenance, transport-health, and DB-diff
   sub-objects. Rendered as a human `rich` results table AND a compact fenced
   ```` ```json ```` block — both derived from the **same** field accessors,
   never two parallel field lists. The JSON carries a `schema_version` key.
2. **RPT-02 — auto-capture (no tester input).** FW+board+host version
   (`version:board` from the MSG_OK identity; host = `firestarter.__version__`),
   chip-ID expected-vs-actual, protocol path taken, each step's exact firmware
   error code (via the Phase-108 `StepResult.error_code` seam), and the
   byte-mismatch `Fingerprint` classification.
3. **RPT-04 — provenance prompted before the sweep.** Shield revision (explicit
   **"not sure"**, never auto-derived from the ambiguous `hw_revision` byte),
   chip origin, pot adjustments — a `Provenance` model + a prompt component + an
   `is_submittable` predicate (any blank field ⇒ not submittable). **This phase
   builds the model/component/predicate; Phase 112 invokes it before the sweep.**
4. **RPT-05 — embedded DB-diff.** Current `support_status` (read at test time)
   beside an **advisory, read-only** proposed-disposition derived from the sweep
   verdicts — surfaced for maintainer triage, never written back.
5. **XPORT-01 — transport-health section.** COBS/CRC/retry/timeout counters
   captured best-effort during the sweep; `transport-suspect` flag when elevated;
   an explicit `"not measured"` sentinel (never a false `0`) when unavailable.

**Host-only. Bench-free. Fully unit-testable** via `EpromDatabase(skip_local_override=True)`
+ mock operator (the `dev validate-family` seam). No firmware change — the
milestone's non-regression invariant (`dev test` adds zero firmware dispatch
entries / zero new VPP-set call sites) holds here too.

**Explicitly NOT this phase:** the measured VPP/VPE mV *value* that fills a report
slot = Phase 111 (this phase leaves the slot); the `@dev.command("test")` CLI
surface that *invokes* the provenance prompts and *renders* the report to the
terminal / `--output-dir` = Phase 112; submission (`--submit`) = Phase 113; the
grep-auditable no-auto-graduate lock + `support_status` taxonomy transitions =
Phase 113/114.
</domain>

<decisions>
## Implementation Decisions

### Single-source dual-render (RPT-01)
- **D-01 (LOCKED): One composed `@dataclass`; JSON is canonical, the table is a derived view** — `DiagnosticReport` is a dataclass composing the existing
  Phase-108 `Plan`, `list[StepResult]`, and per-step `Fingerprint` objects plus
  new sub-dataclasses (`AutoCapture`/identity, `Provenance`, `TransportHealth`,
  `DbDiff`). A single `to_dict()` produces the serializable mapping →
  `json.dumps(..., indent=2)` rendered inside a fenced ```` ```json ```` block; a
  single `render()` builds the `rich` table/panels **from the same dataclass
  field accessors** — the table is NEVER built from a second hand-maintained
  field list and NEVER parsed back out of the JSON string. This is the "no
  duplicated logic" contract: add a field once, both renders pick it up.
  Rejected: assembling the JSON dict independently from the table rows (two
  lists that silently drift — the exact failure RPT-01 forbids).
- **D-02 (LOCKED): `schema_version` is a single-sourced module/class constant serialized into the dict** — A single source-of-truth constant (e.g. `SCHEMA_VERSION = "1.0"`)
  written into `to_dict()` output so consumers (`gsd-inbox` parsing in Phase 113)
  can detect format changes. Exact starting value/format string is discretion
  (see below), but it MUST be present in the JSON and single-sourced.
- Dual-output *file*-writing precedent to mirror for shape (not to copy verbatim):
  `_write_validation_matrix_artifact` (cli_handlers.py ~1377) already emits a
  `json.dumps(indent=2)` artifact alongside a human `.md` — same "one source,
  two serializations" spirit. `rich` (>=14.0) is already a dependency and
  `rich.prompt`/`rich.table` are available.

### Transport-health capture + honest fallback (XPORT-01)
- **D-03 (LOCKED): NO new transport instrumentation; best-effort capture + explicit `"not measured"` sentinel** — The report captures ONLY the
  COBS/CRC/retry/timeout counters the serial/COBS layer **already** exposes. It
  does **not** add new counters to `serial_comm.py` / the hot serial path — that
  would be scope creep and risks the milestone's zero-firmware-touch / SAFE-02
  non-regression posture. When a counter is unavailable the field renders the
  explicit `"not measured"` sentinel (per XPORT-01's "not a false zero" clause),
  and the `transport-suspect` flag can **only** trip from *present, elevated*
  counters — never inferred from absent ones. This mirrors Phase 108's
  honest-`indeterminate` fingerprint bucket: refuse to fabricate confidence from
  missing data. Rejected: instrumenting the transport layer this phase (touches
  the serial hot path, expands blast radius, off-scope for a report-model phase).
- **Note for researcher/planner:** the app has no first-class transport counters
  today (only a per-cell `retry_count` in the `validate-family` harness,
  frequently hardcoded `0`). Surveying what COBS/CRC/timeout signal is *actually*
  reachable from an `EpromOperator`/serial handle during a sweep is a research
  task; if the honest answer is "nothing reliable," the section legitimately
  reads `"not measured"` for now and the flag never trips — that is an ACCEPTED
  outcome, not a gap to paper over.

### Provenance component: model + submittable-gate here, invocation in Phase 112 (RPT-04)
- **D-04 (LOCKED): Build the `Provenance` model + prompt component + `is_submittable` predicate in THIS phase; Phase 112 only calls it** — Mirrors Phase 109's split
  (banner *data* in 109, banner *rendering* in 110/112): the report owns the
  provenance data model, the prompt-collecting function (returns a `Provenance`),
  and the predicate that decides submittability. Phase 112's handler invokes the
  prompt function before running the sweep. Rejected: deferring the whole
  provenance concern to Phase 112 — that would leave RPT-04 hollow here (the
  submittable predicate and model belong with the report object).
- **D-05 (LOCKED): "not sure" is a filled (submittable) answer; only a blank/unanswered field blocks submission** — Shield revision offers an explicit
  **"not sure"** option and NEVER auto-derives from the `hw_revision` byte
  (the byte cannot distinguish Rev 2.2 / 2.0 / modified Rev 0 — decisive lesson
  from Bug A). Choosing "not sure" is a valid, submittable answer; leaving a
  prompt entirely unanswered/empty is what fails `is_submittable`.
- **D-06 (LOCKED): Prompt field set** — (a) **shield revision**: enumerated set
  with a free-text/"other" escape + explicit "not sure" (labels drawn from the
  project's known revs — Rev 2.2 / Rev 2.0 / modified Rev 0 — but community-
  tolerant, not a closed hardware whitelist); (b) **chip origin**: new/blank vs
  pulled/used (+ "owns a UV eraser?" only when the chip is UV-EPROM, feeding the
  Phase-109 eraser-less retry story); (c) **pot adjustments**: touched vs
  not-touched (+ optional free-text note). Prompts use `rich.prompt`
  (`Prompt.ask`/`Confirm.ask`, already used in `firmware.py`) behind the same
  mock-operator seam so the component stays unit-testable without a human.

### DB-diff proposed-change without auto-graduating (RPT-05)
- **D-07 (LOCKED): Advisory, read-only proposed-disposition string; never a DB write, never the taxonomy state-machine** — The DB-diff shows the chip's
  **current `support_status`** (read via the existing `chip_resolver` /
  `get_eprom` path at test time) beside a plainly-labeled, human-readable
  **proposed disposition derived purely from the sweep verdicts** — e.g.
  PASS-only → "suggests: candidate for community-reported"; any `BAD` →
  "suggests: community-fail signal"; `marginal`/`indeterminate` → "inconclusive —
  needs N≥2 agreement". It is descriptive triage text computed read-only; it
  **never** writes any `support_status` field and **never** implements the
  taxonomy transitions themselves. The `community-reported`/`-confirmed`/`-fail`
  taxonomy, the N≥2 promotion rule, and the grep-auditable "no code writes
  `support_status` from a parsed report" lock are **Phase 113/114** — this phase
  only *surfaces the diff*, it does not decide it. Rejected: emitting a concrete
  target `support_status` value (reads as a decision, invites a future auto-write,
  blurs the Phase-114 human gate).

### Claude's Discretion (grounded defaults for the planner/researcher)
- **Exact dataclass/sub-object names and decomposition** (`AutoCapture`,
  `TransportHealth`, `DbDiff`, `Provenance`, field names) — planner's call,
  constrained by D-01's single-source-render contract.
- **`schema_version` starting value/format** — recommend `"1.0"` (simple
  semver-ish string); MUST be single-sourced and present in the JSON (D-02).
- **JSON representation of absent/NA fields** — recommend a stable sentinel:
  `null` for genuinely-absent scalars, and the string `"not measured"` for the
  transport-health-unavailable case so the human render and machine render agree
  on the honest-fallback signal (XPORT-01). Planner's call on the precise shape.
- **`transport-suspect` elevated-threshold numbers** and **which specific
  counters are reachable** — researcher/planner detail (grounded by D-03's
  best-effort + honest-fallback contract).
- **DB-diff proposed-disposition exact wording/branching** — planner's call
  within D-07's advisory/read-only constraint.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (this phase)
- `.planning/ROADMAP.md` — Phase 110 section (goal, depends-on Phase 108 + 109,
  5 success criteria) + the §v1.21 dependency-spine line ("provenance must be
  captured before the sweep, feeding the report") + the "Non-regression
  invariant" (zero new firmware dispatch / zero new VPP-set — holds here too)
- `.planning/REQUIREMENTS.md` — RPT-01, RPT-02, RPT-04, RPT-05, XPORT-01 (and
  RPT-03, the already-shipped Phase-108 `error_code` seam this report *consumes*)

### Design intent (the "why" — read before planning)
- `.planning/notes/dev-test-design-decisions.md` — the **two-tier diagnostic
  contract** (auto-captured vs must-ask-the-tester field lists), the exact
  provenance-before-the-sweep rationale, and the "one run → two artifacts" /
  self-contained-issue-body shape this report realizes
- `.planning/phases/108-test-plan-engine-address-derived-pattern-fingerprint/108-CONTEXT.md`
  — Phase-108 locked decisions the report builds on: the `Fingerprint`/`Step`/
  `Plan`/`StepResult` shapes, the `OK/BAD/NA/SKIPPED/marginal` verdict vocabulary,
  and D-07 (the `EpromOperationError.error_code` seam feeding per-step exact codes)
- `.planning/phases/109-destructiveness-gate-safety/109-CONTEXT.md`
  — the `Plan.locked_destructive` advisory field + the N-of-M (`tests_run`/
  `tests_total`) banner data the report must carry; the SAFE-02 orchestrator-only
  property this phase must not violate
- `.planning/seeds/community-chip-validation-command.md` — original `/gsd-explore` seed
- `.planning/research/SUMMARY.md` — HIGH-confidence research; the resolved open
  questions (address-derived-not-fixed pattern; FLAG-only / **no-auto-graduate** —
  the constraint D-07's read-only DB-diff honors)

### Reusable code (firestarter_app/)
- `firestarter/chip_test.py` — the Phase-108 engine the report wraps:
  `Fingerprint` (~L127), `Step`/`Plan` + `locked_destructive` (~L281–315),
  `StepResult` with `verdict`/`error_code`/`fingerprint` (~L453–472),
  `derive_plan()` (~L318), `run_plan() -> list[StepResult]` (~L501). The report
  is a NEW consumer of these — it adds no new dispatch and sets no VPP.
- `firestarter/cli_handlers.py:1375` — `_write_validation_matrix_artifact`
  (json+md dual-serialization precedent to mirror in *shape*) and
  `firestarter/cli_handlers.py:1474` — `dev_validate_family` (the sibling handler
  + `EpromDatabase(skip_local_override=True)` + mock-operator unit-test seam)
- `firestarter/serial_comm.py` — MSG_OK_READY identity decode (`version:board`
  source for RPT-02 auto-capture); survey here for any reachable transport
  counter (XPORT-01, D-03 — expect little/none, degrade to "not measured")
- `firestarter/__init__.py:1` — `__version__` (`3.0.0b10`; host-version auto-capture)
- `firestarter/chip_resolver.py:54` — `raw_config.get("support_status", "supported")`
  (the current-`support_status` read site for the RPT-05 DB-diff) +
  `firestarter/database.py:506/535` — `get_eprom`/`convert_to_programmer`
- `firestarter/firmware.py:20` — `from rich.prompt import Confirm` (existing
  `rich.prompt` usage precedent for the provenance prompt component, D-06)
- `pyproject.toml:51` — `rich>=14.0` already declared (table + prompt rendering)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase-108 dataclasses** (`Fingerprint`, `Step`, `Plan`, `StepResult`) — the
  report composes these directly; `StepResult.error_code`/`.fingerprint` are
  already the RPT-02 per-step auto-capture fields. No re-derivation needed.
- **`rich`** (already a dep) — `rich.table.Table`/`rich.console.Console` for the
  human render (D-01); `rich.prompt.Prompt`/`Confirm` for provenance (D-06,
  precedent in `firmware.py:20`).
- **`_write_validation_matrix_artifact` + `dev_validate_family`** — the
  json-dump-plus-human-artifact shape and the `skip_local_override` + mock-operator
  test seam to reuse for a bench-free `DiagnosticReport` unit test.

### Established Patterns
- **"Data here, rendering downstream" split** — Phase 109 put banner *data*
  (`locked_destructive`, N/M) in the engine and left *rendering* to 110/112.
  This phase follows it: build the report object + provenance model/predicate
  here; the terminal render + `--output-dir` write + prompt *invocation* are
  Phase 112.
- **Honest-fallback over fabricated confidence** — Phase 108's `indeterminate`
  fingerprint bucket; XPORT-01's `"not measured"` (D-03) is the same principle
  applied to transport counters.
- **Orchestrator-only (SAFE-02)** — the report is pure host-side data assembly;
  it reads DB + wraps engine results, sets no VPP, builds no wire command. The
  Phase-109 SAFE-03 AST checker will (in Phase 112) scan the handler that renders
  this — keep the report module clean of VPP-set / raw-command / `--force`.

### Integration Points
- **Consumes** Phase-108 `run_plan()` results + `Plan.locked_destructive` +
  Phase-109 `tests_run`/`tests_total` banner data.
- **Leaves a slot** for the Phase-111 measured VPP/VPE mV value (the report field
  exists; the sampler fills it later).
- **Feeds** Phase 112 (renders + writes the report; invokes the provenance
  prompts before the sweep) and Phase 113 (`gsd-inbox` parses the fenced JSON via
  `schema_version`); the RPT-05 DB-diff feeds Phase 114 disposition — as
  read-only advisory data, never a write.
</code_context>

<specifics>
## Specific Ideas

- The auto-capture field set is not arbitrary — every field is one that
  **repeatedly cracked a real RCA** in this project: FW+board+host version
  (FW/host desync, board-specific bugs), chip-ID expected-vs-actual (ST-vs-Winbond
  512 mixup), per-op exact error code (`0xA4`/`0xBB`/`0x303`), fingerprint
  (Rev-0 shield Bug A upper-address faults), transport health (uno328pb timeout
  signature). The report exists to make those signals legible on one screen.
- The provenance-before-the-sweep ordering is a **hard design consequence**: a
  beautiful auto-report is still un-actionable if the shield revision is unknown,
  so the prompts must run first and a blank field must block submission
  (`is_submittable`) — otherwise reports land un-triageable.
- D-07's read-only DB-diff is the report-model-side expression of the milestone's
  founding constraint (no-auto-graduate, grounded in this project's own false-PASS
  history). The diff *informs* a human; it never *is* the decision.
</specifics>

<deferred>
## Deferred Ideas

None from the discussion — it stayed within phase scope. Adjacent concerns are
already owned by other phases: measured VPP/VPE mV sampler = Phase 111; the
`@dev.command("test")` CLI surface (flag parsing, provenance-prompt *invocation*,
terminal/`--output-dir` render, exit-code semantics) = Phase 112; `--submit`
flow (prefilled-URL / `gh issue create`, path-leak/size guards) = Phase 113; the
`support_status` taxonomy (`community-reported`/`-confirmed`/`-fail`), the N≥2
promotion rule, and the grep/AST-auditable no-auto-write lock = Phase 113/114.

### Reviewed Todos (not folded)
The todo matcher surfaced 8 matches (1 @ 0.9, 7 @ 0.6) — the **same set Phase 109
already reviewed and rejected** as off-axis keyword false-positives. Phase 110 is
**host-only** (report model + provenance prompts) and adds **zero firmware
change**; every match is on the firmware / hardware / bench axis and matched only
on generic keywords (`captured`, `status`, `source`, `protocol`, `phase`, `read`).
`--auto`'s ≥0.4 auto-fold default is overridden by the CRITICAL scope guardrail —
none folded:
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`
  (0.9, firmware) — a firmware VPP-check behavior change; opposite axis (this
  phase touches no firmware, sets no VPP).
- `avrdude-mcu-detection-fallback.md`, `cobs-decoder-framelevel-deadline-wr01.md`,
  `fix-jp4-labels-and-rev2-revision-block.md`, `photograph-modified-rev-0.md`,
  `remove-dead-json-init-sizeof-pointer-bug.md`, `spike-databuffer-size-speed-delta.md`,
  `write-modifications-md-rework-trace.md` (all 0.6) — firmware/hardware/bench/docs
  work; generic-keyword collisions only, none describe report-model or provenance work.

</deferred>

---

*Phase: 110-Diagnostic Report Model + Dual Output + Provenance Prompts*
*Context gathered: 2026-07-02*
