# Phase 113: Submission Flow - Context

**Gathered:** 2026-07-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Add a tiered `--submit` path to the existing `firestarter dev test <chip>` command
(built in Phase 112) that files the run's `DiagnosticReport` to the maintainer's
GitHub issue tracker **safely, explicitly, and never by accident** (SUB-01/02/03).
A new host-side `submit.py` module, invoked from the `dev_test` handler on the
`--submit` flag, consuming **this run's in-memory report** — it does not re-run the
sweep.

**In scope:**
1. **SUB-01 — tiered submit.** `gh issue create --body-file -` (body piped over stdin,
   auto-labeled `gsd-inbox`) when `gh` is detected (`shutil.which`) **and** authenticated;
   otherwise a prefilled `github.com/.../issues/new?title=…&body=…&labels=…` browser URL,
   opened with `webbrowser`. Measure the *encoded* URL length and escalate/omit the fenced
   JSON block once the encoded body approaches GitHub's ~8 KB server cap (escalate past
   ~7.5 KB encoded). The **gist/attachment tier is RESERVED, not wired** (SUB-F1 → v2) —
   v1.21 only escalates *off* the URL tier.
2. **SUB-02 — sanitize + preview + explicit/interactive-only.** Before anything is sent,
   the body is sanitized (whitelisted field set; local filesystem paths / usernames / PII
   scrubbed; any raw byte dumps hex/base64-encoded), then the **final sanitized body is
   shown to the tester for an explicit `Confirm.ask`**. Submission requires the explicit
   `--submit` flag AND an interactive confirm — it never happens as a side effect of a bare
   `dev test` run.
3. **SUB-03 — dedup fingerprint.** Every submitted report carries a deterministic dedup
   fingerprint (short hash) so a maintainer triaging the `gsd-inbox` label recognizes
   repeat reports for the same chip at a glance.

**Host-only. Orchestrator-only (SAFE-02).** `submit.py` sets no VPP, builds no wire/protocol
command, adds zero firmware dispatch entries. Shelling out to `gh` / opening a browser is the
submission tier, not a hardware path. Fully unit-testable via injected seams
(`shutil.which`/`subprocess`/`webbrowser` monkeypatched) — no bench, no network in tests.

**Explicitly NOT this phase:**
- The `support_status` graduation-ladder taxonomy (`community-reported`/`-confirmed`/`-fail`),
  the N≥2 promotion rule, and the grep/AST-auditable "no code writes `support_status` from a
  parsed report" lock = **Phase 114**.
- `gsd-inbox` triage-side auto-parsing of the fenced JSON + DB-diff surfacing = **Phase 114**
  (INBOX-01). This phase only *produces* a submittable, parseable body; it does not consume it.
- The fully-wired gist/attachment tier for verbose failure logs = **v2 (SUB-F1)**.
</domain>

<decisions>
## Implementation Decisions

### Target repository (SUB-01)
- **D-01 (LOCKED): Reports land in `henols/firestarter_app`, hardcoded module constant.**
  Both submit tiers point there: `gh issue create --repo henols/firestarter_app` and the
  browser `https://github.com/henols/firestarter_app/issues/new`. **No cwd git-remote
  inference** — a community tester's fork must never receive their own report. Rationale:
  `firestarter_app` is the community-facing entry point where the ONBOARD-04 install/flash
  doc lives and where `gsd-inbox` triage runs. (Rejected: firmware repo `henols/firestarter`
  — chip support is firmware-rooted, but the tester's touchpoint and the onboarding doc are
  host-side; Rejected: configurable target — extra surface area that risks a misrouted report.)

### Dedup fingerprint (SUB-03)
- **D-02 (LOCKED): Fingerprint = deterministic short hash over `chip name + protocol + ordered per-step verdicts + byte-mismatch fingerprint classifications`.** Emitted as a
  field in the report JSON **and** surfaced in the issue **title** so a triager sees repeats
  at a glance. Volatile fields are EXCLUDED from the hash (`generated` timestamp, host
  version, measured VPP/VPE mV) so a clean re-test of the same chip with the same outcome
  dedups to the same id.
  - **Why fold in fingerprint classes:** two runs that fail *differently* (e.g. a blank/contact
    fault vs an address-line fault on the same chip) get **distinct** dedup ids — the finer
    grain is deliberate. Accepted consequence: a chip whose fault class flaps across runs
    reads as "new" each time, which is the correct triage signal (inconsistent failure mode).
  - **Graceful degradation:** verify-step `Fingerprint`s only exist on destructive runs; a
    non-destructive run (id + read + blank-check) carries none, so its dedup id collapses to
    `chip + protocol + verdicts` — stable and fine.
  - Hash impl is stdlib `hashlib` (no new dep); exact digest/length (e.g. first N hex chars of
    a sha256 over a canonical field join) is planner's call.

### Submit guardrails — the awkward cases (SUB-01/SUB-02)
- **D-03 (LOCKED): Refuse a non-submittable report.** If `is_submittable(auto_capture)` is
  `False` (auto-capture identity incomplete — post-112-04 this is `chip`/`protocol`/
  `host_version`, NOT provenance), `--submit` refuses and prints the failing field(s). It does
  not submit an un-actionable report.
- **D-04 (LOCKED): Interactive-only — off-TTY does not auto-send.** On a real terminal,
  `--submit` sanitizes → previews → `Confirm.ask` → sends (gh or browser). Off-TTY (piped /
  CI / the mock seam), `--submit` **prints the sanitized body + the issue URL but does NOT
  auto-open the browser or run `gh issue create`** — honoring SUB-02's "submission never as a
  side effect / interactive confirm required." (No silent CI submissions.)
- **D-05 (LOCKED): Oversize browser-URL body → drop JSON, then guide.** When the *encoded*
  URL body would approach the ~8 KB GitHub cap (escalate past ~7.5 KB encoded): **drop the
  fenced JSON block** from the URL body, keep the human results table, and append a note
  pointing the tester to the **always-saved `dev-test-<chip>.json`** (the handler persists it
  every run) and/or suggesting the `gh` tier for the full machine report. Hard-stop before
  ~8 KB. (`gh`'s stdin `--body-file -` path has no such cap, so it always carries the full body.)

### Claude's Discretion (grounded defaults for research/planner)
- **Sanitization mechanism (SUB-02).** Operator chose "you decide" within the SUB-02
  constraint. Recommended shape: the report's `to_dict()` is already a structural field
  **whitelist** (no paths) — treat that as the guarantee; then **scrub the free-text leak
  vectors** as a backstop: `StepResult.reason`, `AutoCapture.chip_id_mismatch_reason`, and the
  `.md` Reason column, for home-dir paths (`/home/…`, `/Users/…`, `C:\Users\…`), the current
  username, and serial device names (`/dev/ttyACM*`, `/dev/ttyUSB*`, `COM*`). Hex/base64-encode
  any raw byte dump (none exist in the report today — this is a forward-looking guard the
  whitelist already satisfies). Exact regex set + whether to sanitize the dict vs re-render is
  planner's call.
- **Issue title format** — surface the dedup short-hash (D-02) plus chip + overall verdict,
  e.g. `[dev test] <chip> — <PASS/FAIL/INCONCLUSIVE> (<shorthash>)`. Exact wording is planner's.
- **`gh` auth detection** — `shutil.which("gh")` present AND `gh auth status` exit 0. Treat any
  non-zero / missing as "fall back to browser tier." Injectable for tests.
- **Preview rendering** — reuse `rich`/`Confirm.ask` (already used in `firmware.py` and the
  `dev test` `--destructive` confirm). Show the exact bytes that will be sent.
- **`submit.py` internal decomposition + seam injection** — planner's call, constrained by
  SAFE-02 orchestrator-only and the mock-operator/injectable-subprocess test seam.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & scope (this phase)
- `.planning/ROADMAP.md` — Phase 113 section (goal, depends-on Phase 110 + 112, 3 success
  criteria) + the §v1.21 "Non-regression invariant (SAFE-01/02/03)" line (holds here) + the
  dependency-spine line ("submission (Phase 113) depends on the report existing").
- `.planning/REQUIREMENTS.md` — **SUB-01, SUB-02, SUB-03** (§Submission); the SUB-future
  block (SUB-F1 gist/attachment tier is v2, NOT this phase) and the "Silent / automatic issue
  submission" / "New Python third-party dependencies" Out-of-Scope rows.

### Design intent (the "why" — read before planning)
- `.planning/notes/dev-test-design-decisions.md` §"Output & submission" — the tiered `--submit`
  (`gh` → prefilled browser URL → reserved gist tier), the self-contained-issue-body shape
  (human table + fenced JSON), and the "a single-chip sweep is only a few KB, fits in a URL body".
- `.planning/seeds/community-chip-validation-command.md` — original `/gsd-explore` seed.
- `.planning/research/SUMMARY.md` — HIGH-confidence research (address-derived pattern;
  no-auto-graduate — the constraint Phase 113 stays clear of; graduation is Phase 114).

### Upstream phase decisions this handler consumes
- `.planning/phases/110-diagnostic-report-model-dual-output-provenance-prompts/110-CONTEXT.md`
  — the `DiagnosticReport` single-source `to_dict()`/`render()`/`to_json_block()`,
  `schema_version` (`gsd-inbox` parses this in Phase 114), `NOT_MEASURED`, `build_db_diff` (D-07
  read-only). **⚠ Superseded in part:** RPT-04 provenance (D-04/05/06) was later reversed.
- `.planning/phases/112-dev-test-handler-wiring/112-CONTEXT.md` + STATE.md Phase-112 decisions
  — the `@dev.command("test")` handler `--submit` lives on; the "one run → two artifacts"
  contract; **the 112-04 reversal** (`prompt_provenance`/`Provenance` DELETED; `is_submittable`
  now = auto-capture completeness only). D-03 above builds on this reversal.

### Reusable code (firestarter_app/)
- `firestarter/cli_handlers.py:1751` — `dev_test` handler (**wire `--submit` here**): already
  builds the `DiagnosticReport`, renders it, and **always persists** `dev-test-<chip>.{json,md}`
  to `<config dir>/reports` (or `--output-dir`). The `.md` (results table + `to_json_block()`) is
  the self-contained issue body; `_sanitize_chip_token` (filesystem-safe token) precedent at
  `:1882`.
- `firestarter/diagnostic_report.py` — `DiagnosticReport.to_dict()` (`:352`),
  `to_json_block()` (`:441`), `render()` (`:371`), `is_submittable(ac)` (`:153`, auto-capture-only
  post-112-04), `AutoCapture` (`:68`), `StepResult`-derived `_step_dict` incl. `reason`/`error_code`
  (`:323`). SUB-03 fingerprint is a NEW field/helper here or in `submit.py`; SUB-02 sanitization
  reads these fields.
- `firestarter/chip_test.py` — `StepResult.verdict` / `.reason` / `.fingerprint.classification`
  (the SUB-03 dedup inputs) and the `OK/BAD/NA/SKIPPED/marginal` verdict vocabulary.
- `firestarter/firmware.py:20` — `from rich.prompt import Confirm` (preview-confirm precedent);
  `firestarter/avr_tool.py:15` — `subprocess` (`Popen`/`PIPE`) usage precedent for the `gh` shell-out.
- `firestarter/constants.py` — `github.com/repos/henols/…` release-download refs (repo-owner
  precedent; the submit target constant D-01 is `henols/firestarter_app`).
- `tools/check_devtest_orchestrator.py` + its paired negative-fixture pytest — the SAFE-03 AST
  checker; confirm whether `submit.py` needs to be in its scan set (planner note: it sets no VPP /
  builds no wire dict, so it should pass, but shelling to `gh` must not trip a false positive).
- `.github/workflows/ci.yml` — pytest/ruff/mypy gate (py3.11 target; watch the
  py3.12-masks-CI-3.11 ruff/codegen trap).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The report already exists and is always persisted.** `dev_test` (Phase 112) builds the
  `DiagnosticReport`, renders it, and writes `dev-test-<chip>.{json,md}` on every run. `--submit`
  consumes the in-memory `report` object (and the saved JSON path is what D-05's oversize-guidance
  points to). No re-run, no re-derivation.
- **`is_submittable(ac)`** ([diagnostic_report.py:150](../../firestarter_app/firestarter/diagnostic_report.py#L153)) —
  the D-03 refuse-gate predicate; post-112-04 it is auto-capture completeness only (chip + protocol
  + host_version), no human/provenance field.
- **stdlib-only submission primitives** — `shutil.which` (gh detection), `subprocess` (gh
  create + `gh auth status`), `webbrowser.open` (URL tier), `urllib.parse.urlencode`/`quote`
  (prefilled URL + encoded-length measurement), `hashlib` (dedup hash). No new third-party dep.
- **`_sanitize_chip_token`** (cli_handlers.py:1879) — filename-safety precedent; the SUB-02
  body sanitizer is a sibling concern (content, not filename).

### Established Patterns
- **Injectable seams for bench-free tests** — mirror `dev_validate_family`'s
  `EpromDatabase(skip_local_override=True)` + mock-operator seam and the `prompt_provenance(ask=,
  confirm=)`-style injection so `submit.py` unit tests monkeypatch `which`/`subprocess`/`webbrowser`
  and never touch the network or a real terminal.
- **Orchestrator-only (SAFE-02)** — every `dev test` op routes through `resolve_chip`; `submit.py`
  adds no VPP, no wire dict, no `--force`. Keep the SAFE-03 AST checker green (the `gh` shell-out is
  a submission concern, not a hardware path — ensure the checker doesn't false-positive on it).
- **`rich.prompt.Confirm` preview-confirm** — the same interaction shape as the `--destructive`
  confirm already in `dev_test`.

### Integration Points
- **`--submit` flag added to `dev_test`** (cli_handlers.py:1751) → after render + persist, if
  `--submit`: `submit.py` sanitizes → previews → confirms → tiers (gh | browser | drop-JSON).
- **Feeds Phase 114** — the submitted body's `schema_version` fenced JSON + `gsd-inbox` label are
  what INBOX-01 triage parses; the dedup fingerprint (D-02) is what a maintainer keys repeat
  reports on. Phase 113 produces; Phase 114 consumes.

</code_context>

<specifics>
## Specific Ideas

- The whole submission tier exists to make a community report **land in triage without leaking
  the tester's machine** — hence D-02's PII/path scrub and D-01's fixed maintainer-repo target
  (never their fork). The dedup fingerprint (D-03/D-02) is the triage-side counterpart: a
  maintainer scanning `gsd-inbox` can tell "same chip, same outcome, seen it" from "same chip,
  new failure mode" at a glance — grounded in this project's own N=1-is-a-lie history
  (AM27C020 write#1 60/64 vs write#2 0/64).
- **Provenance is gone** (112-04 reversal). Do NOT resurrect shield-revision / chip-origin /
  pot-adjustment prompts or gate submittability on them. Submittability is machine-only.

</specifics>

<deferred>
## Deferred Ideas

- **Fully-wired gist/attachment tier for verbose failure logs** (byte dumps, raw serial traces
  that overflow the URL cap) → **v2, SUB-F1**. v1.21 only *reserves* it and escalates off the URL
  tier (D-05 drops the JSON block rather than attaching it).
- **Auto-merge/PR of community-confirmed DB entries** → v2, SUB-F2 (still human-gated).
- **`gsd-inbox` triage-side auto-parse + DB-diff surfacing** (INBOX-01) and the no-auto-graduate
  `support_status` taxonomy lock (DISP-01/GRAD-01) → **Phase 114** (this phase produces the body;
  Phase 114 consumes it).

### Reviewed Todos (not folded)
The pending-todo set (`avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01`,
`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`, `photograph-modified-rev-0`,
`write-modifications-md-rework-trace`) is the **same off-axis set Phases 109–112 each reviewed and
rejected** — all firmware / hardware / bench / docs work. Phase 113 is host-only Python CLI
submission wiring (no firmware change, sets no VPP); none apply. None folded.

</deferred>

---

*Phase: 113-submission-flow*
*Context gathered: 2026-07-03*
