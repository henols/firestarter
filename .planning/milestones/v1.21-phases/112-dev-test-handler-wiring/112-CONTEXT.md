# Phase 112: `dev test` Handler Wiring - Context

**Gathered:** 2026-07-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire the pieces built in Phases 108–111 into a single runnable
`firestarter dev test <chip>` Click subcommand — a **sibling of
`dev validate-family`** in `cli_handlers.py`. This phase is **pure
orchestration**: it composes existing services in one flow —

```
prompt_provenance(is_uv)  →  derive_plan(name, db, destructive)
    →  run_plan(plan, operator, db, runs=2)  [sampler hook brackets the write]
    →  build AutoCapture / TransportHealth / BannerCounts / DbDiff
    →  DiagnosticReport(...)  →  render() + write artifacts  →  exit code
```

There is **no existing top-level orchestrator** tying these together — Phase 112
builds that glue and the `@dev.command("test")` CLI surface (flag parsing,
prompt invocation, exit-code semantics, terminal render, `--output-dir` write).

**Host-only. Zero new logic.** No new firmware dispatch entry, no new VPP-set
call site, no `--force`, no raw wire-dict — the milestone's SAFE-01/02/03
non-regression invariant holds. The Phase-109 SAFE-03 AST checker
(`tools/check_devtest_orchestrator.py`) scans *this* handler (see planner note
below). Must stay fully unit-testable via `EpromDatabase(skip_local_override=True)`
+ mock operator + injectable prompts (the `dev validate-family` seam) — SC4
requires the wiring itself needs no bench access.

**Flags (from ROADMAP SC1):** chip identifier (positional), `--destructive`,
`--output-dir`. No `--runs` flag (use `run_plan`'s default `runs=2`).

**Explicitly NOT this phase:** `--submit` / issue-body upload = Phase 113;
`support_status` taxonomy transitions + no-auto-graduate grep/AST lock = Phase
114. The report *model*, provenance *component*, sampler *API*, and gate *logic*
already exist (108–111) — this phase only *invokes and renders* them.

</domain>

<decisions>
## Implementation Decisions

### Exit-code contract (SC3 — the scriptability backbone)
- **D-01 (LOCKED): 3-way exit code, mirroring the sibling `dev` commands.**
  - `0` = clean run — only `OK`/`NA`/`SKIPPED` verdicts, no `BAD`, no `marginal`.
  - `1` = any `BAD` verdict (fail signal — **includes a chip-ID mismatch**, since
    the id step is recorded `BAD`/gate-closing).
  - `2` = any `marginal` or `indeterminate` outcome (inconclusive — needs N≥2
    agreement), when there is no `BAD`.
  - A non-destructive default run where write/erase are absent (N < M) still
    exits `0` — it ran cleanly, it just ran fewer tests (the banner reports the
    N-of-M gap; it is not a failure).
  - Rationale: matches `dev consistency-check` / `dev write-cycle` /
    `dev validate-family`, which all `sys.exit(verdict_int)` preserving 0/1/2,
    and matches the report's own `build_db_diff` disposition tiers
    (BAD→community-fail, marginal/indeterminate→inconclusive, OK-only→candidate).
    Precedence when multiple verdicts co-occur: **`1` (BAD) beats `2` (marginal)**
    (compute as `max` over the per-verdict codes, exactly like validate-family's
    `overall_verdict`).

### Interactive vs. scriptable behavior (reconciling RPT-04 with SC3)
- **D-02 (LOCKED): TTY-aware.** On a real terminal (`sys.stdin.isatty()`):
  prompt provenance via `prompt_provenance` **before** the sweep (RPT-04) and
  show a one-line `--destructive` "this sacrifices the chip" confirm. Off-TTY
  (piped / CI / the mock-operator unit seam): **skip both prompts**, run with a
  blank `Provenance` (report is still produced; `is_submittable` computes
  `False` and the report is flagged not-submittable), and treat the
  `--destructive` **flag itself as consent** (no confirm). Humans get RPT-04's
  prompts; scripts never hang on stdin (SC3).
- **D-03 (LOCKED): `-y/--yes` bypasses the destructive confirm on a TTY too.**
  For an operator who *is* interactive but wants no confirm gate. It does **not**
  suppress provenance prompts (those are informational, not a safety gate) —
  only the destructive "are you sure" confirm. (Naming — `--yes` vs `--assume-yes`
  vs `--non-interactive` — is planner's call; the *behavior* is locked.)
- **Note:** Phase 112 only *collects* provenance and stores it + `is_submittable`
  in the report. Nothing acts on submittability here — `--submit` is Phase 113.
  A blank-provenance CI run producing a non-submittable report is the intended,
  correct outcome, not a gap.

### Sampler bracketing topology (the deferred Phase-111 UAT item)
- **D-04 (LOCKED): Optional `sampler` callback threaded into `run_plan`, invoked immediately before and after the write step.** Add an optional
  parameter to `run_plan` (e.g. `sampler=None`); when present, `run_plan` calls
  it right before and right after the `OP_WRITE` step to fill
  `vpp_before_mv`/`vpp_after_mv`/`vpe_before_mv`/`vpe_after_mv`. This tightly
  brackets the write pulse — faithful to Phase-111 D-03's "two independent
  energizations bracketing the write" (so the report shows e.g. rail sagged
  20.9V→17.4V *across the write*, not across the whole sweep).
  - **Decoupling constraint:** the handler passes a **thunk/closure** over
    `sample_vpp_mv()`/`sample_vpe_mv()` — `run_plan`/`chip_test.py` must **not**
    import `hardware.py`. The engine stays sampler-agnostic; `sampler=None` (or a
    mock) keeps every existing `run_plan` unit test unchanged and bench-free.
  - **SAFE-02 clean:** the sampler reuses the existing `COMMAND_READ_VPP` (11) /
    `COMMAND_READ_VPE` (12) monitor path — energize-regulator-and-measure only,
    no socket routing, no VPP-set, no new dispatch. The SAFE-03 AST checker still
    passes.
  - **Non-destructive standalone read** (Phase-111 D-04) stays in the handler:
    take a single standalone VPP+VPE read filling `vpp_mv`/`vpe_mv`, with
    before/after = `NOT_MEASURED`. Rejected: coarse before/after sampling around
    the *whole* `run_plan` call (ambiguous — can't tell a write droop from a read
    droop).

### Output & rendering (the "one run → two artifacts" contract)
- **D-05 (LOCKED): Rich table to stdout on every run; file artifacts only when `--output-dir` is given.** `report.render(console)` prints the human summary
  table to the terminal always. When (and only when) `--output-dir` is passed,
  write two files there: `dev-test-<chip>.json` (the canonical `to_dict()`
  machine report) and `dev-test-<chip>.md` (the **self-contained issue body** —
  human results table on top, fenced ` ```json ` block beneath, i.e. what Phase
  113 uploads). No `--output-dir` → terminal only, cwd stays clean (a casual
  community run is not littered with files).
  - **Filename convention:** hyphenated `dev-test-<chip>.{json,md}`, mirroring
    `validate-family`'s hyphenated `validation-matrix.{json,md}` (Pitfall 4 —
    hyphens keep artifacts distinct from any authored/underscored file). Sanitize
    the chip token for filesystem safety (planner's call on the exact scheme).
  - Rejected: defaulting `--output-dir` to `.` and always writing (what
    `validate-family` does) — that sibling is a maintainer bench tool; `dev test`
    is a casual community command that should not dump files by default.
  - Rejected: echoing the full fenced-JSON block to stdout by default (noisy);
    the `.md` artifact already carries the copy-pasteable self-contained body for
    the URL/submission case (Phase 113).

### Claude's Discretion (grounded defaults for research/planner)
- **`AutoCapture` sourcing:** FW+board identity (`version:board` from the MSG_OK
  identity), host `firestarter.__version__`, chip-ID expected-vs-actual, and the
  protocol path taken — assembled host-side in the handler from the
  operator/serial handle + DB entry. Exact plumbing is planner's call within the
  no-new-dispatch / no-VPP-set constraint.
- **`is_uv` derivation for `prompt_provenance(is_uv)`:** derived host-side from
  the DB entry before the sweep — protocol `0x0B` (UV-EPROM-exclusive across the
  DB) or the `electrical-type` field when present (same signal
  `chip_test._write_region_for` uses). The handler passes it as a plain bool;
  `prompt_provenance` never fetches hardware itself (Phase-110 D-05).
- **`TransportHealth` capture:** best-effort from whatever the serial/COBS layer
  already exposes; expect little/none reachable → honest `NOT_MEASURED`
  (Phase-110 D-03). Not a gap if it reads "not measured".
- **Flag naming** (`-y/--yes` vs `--assume-yes`), the exact chip-token filename
  sanitizer, and internal helper decomposition — planner's call, constrained by
  D-01..D-05.

### Note for the planner (must-do integration tasks, not open decisions)
- **Extend the SAFE-03 AST checker to cover this handler.** Phase 109 scoped
  `tools/check_devtest_orchestrator.py` to *tolerate the handler's absence* and
  left "cover it when added" to Phase 112. Now that the `@dev.command("test")`
  handler exists, the checker (and its paired negative-fixture pytest,
  `tests/test_...`) MUST scan it — denying VPP-set / raw-wire-dict / `--force`
  in the handler + sampler thunk. A checker that silently skips the new handler
  is the hollow-gate failure mode Phase 109 D-02/D-03 forbid.
- **Re-verify the deferred Phase-111 SC2 (bench, hardware-gated):** once the
  sampler is wired around the write step, a destructive run on an
  electrically-erasable chip (W27C512 / W29C020) on Leonardo + Rev 2.0 should
  show `vpp_before/after`/`vpe_before/after` tracking real rail behavior. This is
  the deferred `111-UAT` re-verify item — a **bench/UAT** check, safe to defer
  again if no bench session; the software wiring itself is unit-testable now.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (this phase)
- `.planning/ROADMAP.md` — Phase 112 section (goal, depends-on 108–111, 4 success
  criteria; "pure integration") + the §v1.21 "Non-regression invariant
  (SAFE-01/02/03)" line (holds here) + the "delivers the user-facing entry point
  for SWEEP-01..05, PATT-01..03, RPT-01..05, VOLT-01, XPORT-01" framing.
- `.planning/REQUIREMENTS.md` — no new REQ-ID; this phase makes SWEEP/PATT/RPT/
  VOLT/XPORT reachable from one CLI invocation.

### Design intent (the "why" — read before planning)
- `.planning/notes/dev-test-design-decisions.md` — the "one run → two artifacts"
  shape, the self-contained-issue-body (human table + fenced JSON) contract, the
  provenance-before-the-sweep ordering, and the technology-aware destructiveness
  default this handler surfaces.
- `.planning/seeds/community-chip-validation-command.md` — original `/gsd-explore` seed.
- `.planning/research/SUMMARY.md` — HIGH-confidence research (address-derived
  pattern; no-auto-graduate).

### Upstream phase decisions this handler consumes (read all four)
- `.planning/phases/108-test-plan-engine-address-derived-pattern-fingerprint/108-CONTEXT.md`
  — verdict vocabulary (`OK/BAD/NA/SKIPPED/marginal`), `Plan`/`Step`/`StepResult`/
  `Fingerprint` shapes, `error_code` seam, id-first + chip-ID-mismatch gate.
- `.planning/phases/109-destructiveness-gate-safety/109-CONTEXT.md`
  — `--destructive` from CLI-only, non-destructive default, `Plan.locked_destructive`
  advisory field, N-of-M banner (applicable-only), the SAFE-03 AST-checker
  contract (D-02/D-03) this phase must extend.
- `.planning/phases/110-diagnostic-report-model-dual-output-provenance-prompts/110-CONTEXT.md`
  — `DiagnosticReport` single-source `render()`/`to_dict()`/`to_json_block()`,
  `schema_version`, `NOT_MEASURED`, `prompt_provenance`/`is_submittable`
  (RPT-04, D-04/05/06 — "not sure" is filled), read-only `build_db_diff` (D-07).
- `.planning/phases/111-measured-voltage-sampler-hardware-gated/111-CONTEXT.md`
  + `.planning/phases/111-.../deferred-items.md` (§111-UAT) — sampler both-rails /
  median-of-N / before-after-on-write / standalone-on-non-destructive; the
  before/after write-step wiring **deferred to Phase 112** (this phase).

### Reusable code (firestarter_app/)
- `firestarter/cli_handlers.py:1450` — `dev_validate_family` (**the sibling to
  model**: `@dev.command`, `@click.option --output-dir`, `@click.pass_obj`,
  `@map_typed_errors`, `EpromDatabase(skip_local_override=True)` + mock-operator
  seam, `sys.exit(overall_verdict)` 3-way) and `:1373` `_write_artifact` /
  `:1400` `_render_markdown` (the json+md dual-artifact shape to mirror).
- `firestarter/chip_test.py` — `derive_plan(name, db, *, destructive)` (`:318`),
  `run_plan(plan, operator, db, *, runs=2)` (`:501` — add the optional `sampler`
  hook around `OP_WRITE` here), `compute_banner`/`BannerCounts` (`:909`+),
  verdict constants (`:434`), `OP_WRITE` (`:276`), `_DESTRUCTIVE_OPS` (`:442`).
- `firestarter/diagnostic_report.py` — `DiagnosticReport` (`:283`; fields incl.
  the split voltage slots `:309-314`), `to_dict()` (`:413`), `render()` (`:437`),
  `to_json_block()` (`:515`), `prompt_provenance(is_uv, *, ask, confirm)` (`:151`),
  `is_submittable` (`:207`), `build_db_diff(name, db, results)` (`:245`),
  `AutoCapture` (`:57`), `TransportHealth` (`:84`), `SCHEMA_VERSION`/`NOT_MEASURED`
  (`:42-43`).
- `firestarter/hardware.py:339/344` — `sample_vpp_mv(n=3)` / `sample_vpe_mv(n=3)`
  (the sampler API the handler wraps in a thunk for the `run_plan` hook).
- `firestarter/chip_resolver.py:16` — `resolve_chip` (guard-honoring path every
  executed op routes through; SAFE-02). `firestarter/__init__.py` — `__version__`.
- `tools/check_devtest_orchestrator.py` + its paired negative-fixture pytest
  (Phase 109) — **extend to scan the new handler** (planner note above).
- `.github/workflows/ci.yml` — `Run pytest with coverage` is the enforcement
  point (py3.11 target; watch the py3.12-masks-CI ruff/codegen trap).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`dev_validate_family`** — near-exact structural template: same decorators,
  same `--output-dir` handling, same `skip_local_override` + mock-operator test
  seam, same 3-way `sys.exit`. The Phase-112 handler is its conceptual twin.
- **All 108–111 building blocks exist and are unit-tested** — `derive_plan`,
  `run_plan`, `compute_banner`, `DiagnosticReport`, `prompt_provenance`,
  `is_submittable`, `build_db_diff`, `sample_vpp_mv`/`sample_vpe_mv`. Phase 112
  writes glue, not logic.

### Established Patterns
- **3-way verdict `sys.exit`** — `dev consistency-check`/`write-cycle`/
  `validate-family` preserve 0/1/2 via `sys.exit(verdict_int)` (D-01 follows this).
- **json+md dual artifact** — `_write_artifact` writes `<name>.{json,md}` to
  `output_dir`; D-05 mirrors the shape (with a self-contained `.md`).
- **Injectable prompts** — `prompt_provenance(ask=, confirm=)` and the
  mock-operator seam keep the handler bench-free/TTY-free in tests (SC4, D-02).
- **`rich.prompt` precedent** — `firmware.py` already uses `Confirm.ask(...,
  default=...)`; the `--destructive` confirm follows it.
- **Orchestrator-only (SAFE-02/03)** — every executed op routes through
  `resolve_chip`; handler sets no VPP, builds no wire dict, passes no `--force`.

### Integration Points
- **`run_plan` gains an optional `sampler` param** (D-04) — the one engine-side
  change; still `sampler=None`-default so existing tests/callers are unaffected.
- **Handler composes** provenance → plan → sweep(+sampler) → AutoCapture/
  TransportHealth/banner/db-diff → `DiagnosticReport` → render/write → exit.
- **Feeds Phase 113** — the `.md` self-contained body + `schema_version` JSON are
  what `--submit`/`gsd-inbox` consume.

</code_context>

<specifics>
## Specific Ideas

- The whole point of the exit-code + report is scriptability with signal: a
  community member (or CI) runs `firestarter dev test <chip>`, gets `0`/`1`/`2`,
  and a self-contained `.md` they can paste into an issue. The 3-way code
  distinguishes "it failed" (`1`) from "inconclusive, run it again" (`2`) —
  grounded in this project's own N=1-is-a-lie history (AM27C020 write#1 60/64 vs
  write#2 0/64 → `marginal`).
- The tight write-step bracket (D-04) exists so a maintainer reading a submitted
  report can tell "the rail sagged across the write" from "the regulator never
  reached target" — two different RCAs, the exact distinction the whole
  diagnostic contract was built to surface.

</specifics>

<deferred>
## Deferred Ideas

None from the discussion — it stayed within phase scope. Adjacent concerns are
owned by other phases: `--submit` / issue-body upload / PII-path sanitization =
Phase 113; `support_status` taxonomy + N≥2 promotion + no-auto-graduate
grep/AST lock = Phase 114. The deferred Phase-111 bench SC2 re-verify is a
tracked UAT item (planner note above), not new scope.

### Reviewed Todos (not folded)
The todo matcher surfaced 8 matches (5 @ 0.6, 3 @ 0.2) — the **same off-axis set
Phases 109/110/111 each reviewed and rejected**. Phase 112 is host-only Python
CLI integration (no firmware change, sets no VPP); every match is on the
firmware / hardware / bench / docs axis and collided only on generic keywords
(`skip`, `blank`, `read`, `phase`, `type`, `write`, `chip`). **None folded**
(scope guardrail overrides any auto-fold):
- `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`
  (0.6, firmware) — a firmware VPP-check behavior change; opposite axis.
- `avrdude-mcu-detection-fallback.md`, `cobs-decoder-framelevel-deadline-wr01.md`,
  `photograph-modified-rev-0.md`, `write-modifications-md-rework-trace.md`
  (0.6) — firmware / hardware / bench / docs work; generic-keyword collisions only.
- `fix-jp4-labels-and-rev2-revision-block.md`,
  `remove-dead-json-init-sizeof-pointer-bug.md`,
  `spike-databuffer-size-speed-delta.md` (0.2) — firmware/hardware; single-keyword
  false positives.

</deferred>

---

*Phase: 112-`dev test` Handler Wiring*
*Context gathered: 2026-07-03*
