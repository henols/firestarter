# Phase 114: Disposition / No-Auto-Graduate Lock + Graduation Ladder + Inbox Reconciliation - Context

**Gathered:** 2026-07-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Close the community-validation trust loop **safely**: a community-submitted `dev test`
report must make chip-support triage *easier* for the maintainer without ever being
trusted enough, on its own, to change what the project claims a chip can do. This is the
milestone's closing **feature** phase (Phase 115 is the separate hardware-gated
release/onboarding capstone). Three requirements:

- **DISP-01** — Lock the "flag-only, human-gated" disposition: no code path writes a
  chip's `support_status` as a result of parsing a community report. Grep/AST-auditable.
- **GRAD-01** — The `support_status` taxonomy gains community graduation-ladder states
  (`community-reported` / `community-confirmed` / `community-fail`); a report can be
  *tagged* with one automatically, but promotion into `community-confirmed`/`supported`
  requires an explicit human step and is only reachable once **N≥2 independent reports
  agree** — a single report can never trigger a state transition.
- **INBOX-01** — `gsd-inbox` triage auto-parses a `dev test` issue's fenced JSON block and
  surfaces its DB-diff (current `support_status` vs. the report's proposed change) so the
  maintainer sees the actionable diff without re-deriving it by hand.

**Non-regression invariant (SAFE-01/02/03, milestone-wide):** every op still routes
through `chip_resolver.resolve_chip` / the existing serial path; zero new VPP-set call
sites; zero new firmware dispatch entries. Re-affirmed at this close. `dev test` remains
a pure orchestrator; **firmware is untouched by Phase 114** (host + planning/tooling only).

**Explicitly NOT in this phase:** any auto-promotion code; any maintainer promotion
CLI/tool; writing community-* values into the generated `chip_database.json`; the Phase-115
beta-publish/onboarding work.

</domain>

<decisions>
## Implementation Decisions

### GRAD-01 — graduation-ladder mechanism
- **D-01 (mechanism depth — Docs + auto-tag only):** No new promotion tool/CLI. The ladder
  is (a) a *documented* taxonomy vocabulary and (b) an *automatic report-side tag*
  (`community-reported` / `community-fail`) derived from the sweep verdicts via the existing
  `DbDiff`/`build_db_diff` (Phase 110). Human promotion into `community-confirmed`/`supported`
  is a **manual maintainer action**, made actionable by INBOX-01's triage surfacing (which
  shows the N-agreeing count). SC2's "explicit human step" = that manual action; "reachable
  once N≥2 agree" = triage exposes the agreement count and the human decides — nothing in
  code performs or gates a state write.

### GRAD-01 / DISP-01 boundary — where community-* states live
- **D-02 (Report-side only):** `community-reported` / `community-confirmed` / `community-fail`
  exist **only** on the report / `DbDiff` as a ladder-state label. `chip_database.json`'s
  `support_status` **never** carries a community-* value; a chip reaches the existing
  `supported` state only via the unchanged human-authored `build_db.py` path. Rationale:
  (a) makes DISP-01's grep/AST audit trivially true (the only `support_status` write locus
  stays `build_db.py`); (b) avoids a footgun — every read guard treats `support_status !=
  "supported"` as non-dispatchable, so a community-* value in a DB would silently disable a
  chip.

### GRAD-01 — "N≥2 independent reports agree" rule
- **D-03 (dedup_fingerprint match):** Two reports "agree" iff their existing Phase-113
  `dedup_fingerprint` (chip + per-op verdict signature) matches. Triage counts matching
  fingerprints across issues and surfaces "N agreeing." Reuses shipped code; deterministic.
  This cross-report N≥2 is **explicitly distinct** from the sweep's *internal* per-run N≥2
  (Phase 108 multi-run of the same op on one bench) — the two Ns must not be conflated.

### INBOX-01 — parser home
- **D-04 (firestarter_app `tools/` parser):** A stdlib parser in `firestarter_app/tools/`
  (e.g. `tools/parse_devtest_issue.py`) reads an issue body and emits the DB-diff (current
  `support_status` vs. the report's advisory proposed-disposition) + the N-agreeing count.
  It owns/mirrors the report schema (co-located with `diagnostic_report.py`'s
  `schema_version`), is stdlib-only + unit-testable via the established seams, and survives
  `gsd update` (it lives in the app repo, not the installed gsd-core workflow). `gsd-inbox` /
  the maintainer *invokes* it during triage — **do not edit the installed
  `.claude/gsd-core/workflows/inbox.md` in place** (fragile; overwritten on update).
  - **Target repo:** `henols/firestarter_app` (the `SUBMIT_REPO` reports are filed against).
  - **Detection markers:** the `[dev test]` issue-title marker + the fenced-JSON
    `schema_version` — **not** GitHub labels (community testers lack write access, so the
    submit path can't reliably self-label; see `submit.py` `build_issue_url`).

### DISP-01 — the lock itself (locked, not a gray area)
- **D-05 (AST audit test, anti-hollow):** Add an AST-based audit test that asserts no code
  writes `support_status` as a result of parsing a community report — the only write sites
  remain the human-authored `build_db.py` path. Mirror the established SAFE-03 pattern
  (`tests/test_check_devtest_orchestrator.py`): AST scan (not raw substring grep) + a
  paired anti-hollow test with planted-violation fixtures so the gate can't silently pass.
  D-02 (report-side only) is what makes this a clean, provable invariant.

### Claude's Discretion
- Exact AST-checker scope for D-05 (which modules to scan; extend the existing SAFE-03
  checker vs. a sibling checker) — follow SAFE-03 conventions.
- The precise `tools/parse_devtest_issue.py` CLI shape (stdin vs. file/`--issue` arg; how the
  N-agreeing count is gathered — e.g. scan multiple saved JSON bodies vs. a `gh`-fetched
  list) — planner's call, must reuse `dedup_fingerprint` per D-03.
- The exact report-side ladder-state representation (a derived `ladder_state` field vs.
  formalizing the current advisory prose into an enum) — honor D-02 (report-side only).
- Where the ladder taxonomy is documented (app `README` / `CLAUDE.md` / a `doc/`) — use the
  established doc location.
- Whether to pick up the maintainer-side auto-labeling `submit.py:183` hands to this phase
  (see Specific Ideas) — discretionary; if done it is a maintainer-side `gh` action during
  triage, never a community-side capability.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements & roadmap
- `.planning/ROADMAP.md` §v1.21 → "Phase 114" — goal, depends-on (110 + 113), and the 3
  success criteria (verbatim SC text the plan must satisfy).
- `.planning/REQUIREMENTS.md` — DISP-01 / GRAD-01 / INBOX-01 exact text + status matrix.

### Design & research (the "why" — no-auto-graduate rationale)
- `.planning/notes/dev-test-design-decisions.md` — two-tier diagnostic contract + submission
  tiers; the auto-capture `support_status`/DB-entry field the DB-diff keys on.
- `.planning/research/SUMMARY.md` — HIGH-confidence, 4-stream-convergent research; the
  no-auto-graduate + N≥2 trust model.
- `.planning/research/questions.md` §"Community chip-validation command" Q2 — the resolved
  "Community PASS → support_status graduation" question (flag-only / human-gated).
- `.planning/seeds/community-chip-validation-command.md` — origin seed.

### Host code — report, submission, gates
- `firestarter_app/firestarter/diagnostic_report.py` — `DbDiff` + `build_db_diff`
  (advisory-only by construction, Phase 110); the three ladder-state names already appear
  here as advisory prose; `schema_version` + `to_dict()` fenced-JSON shape the parser reads.
- `firestarter_app/firestarter/submit.py` — `dedup_fingerprint` (the D-03 agreement key);
  `SUBMIT_REPO = henols/firestarter_app`; `build_issue_url` (labels deliberately omitted);
  **line ~183 explicitly hands "server-side template-based labeling" to Phase 114.**
- `firestarter_app/tests/test_check_devtest_orchestrator.py` — the SAFE-03 AST-checker +
  anti-hollow planted-fixture pattern to mirror for the DISP-01 lock (D-05).
- `firestarter_app/firestarter/chip_resolver.py` (≈L54) — the `support_status` read site;
  guard fires on `!= "supported"` (why D-02 keeps community-* off the DB).
- `firestarter_app/tools/build_db.py` — the **only** `support_status` write sites
  (human-authored; unchanged by this phase — the DISP-01 audit's allowed-write locus).
- `firestarter_app/tools/check_dispatch.py` — CI gate that iterates `support_status`; must
  stay green. Unaffected by D-02 (community-* never enters `chip_database.json`).

### Inbox triage
- `.claude/gsd-core/workflows/inbox.md` — the gsd-inbox triage workflow the new `tools/`
  parser feeds. **Do NOT edit in place** (installed gsd-core, overwritten on update).
- `.claude/commands/gsd-inbox.md` — the command entry point.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`DbDiff` / `build_db_diff`** (`diagnostic_report.py`, Phase 110): advisory-only,
  read-only-by-construction; already emits the three community-* names as prose. Extend to a
  report-side ladder-state label — never a DB write (D-01/D-02).
- **`dedup_fingerprint`** (`submit.py` + `diagnostic_report.py`, Phase 113): the D-03
  agreement key for "N≥2 reports agree."
- **SAFE-03 AST-checker + planted-fixture pattern** (`tests/test_check_devtest_orchestrator.py`):
  the DISP-01 lock-test template (D-05).
- **`schema_version` + `to_dict()` fenced JSON** (`diagnostic_report.py`): exactly what the
  `tools/` parser consumes; `schema_version` is a detection marker (D-04).
- **`EpromDatabase(skip_local_override=True)` + mock-operator seam**: keeps all Phase-114
  software work unit-testable without a bench (milestone-wide discipline).

### Established Patterns
- **Single `support_status` write locus.** Values are set only in `build_db.py`; every read
  path guards on `support_status != "supported"` (→ non-dispatchable). Adding community-* to
  `chip_database.json` would silently disable chips — hence D-02 (report-side only).
- **Anti-hollow gates.** Every AST/grep gate ships with planted-violation fixtures
  (SAFE-02/03, Phases 109/112). D-05 follows suit.
- **`dev test` issue detection = `[dev test]` title marker + fenced-JSON `schema_version`,
  NOT labels** (community testers lack write access to add labels).

### Integration Points
- **`tools/parse_devtest_issue.py` (new)** ← issue body / saved JSON → DB-diff (current
  `support_status` vs. advisory disposition) + N-agreeing count (via `dedup_fingerprint`).
  Invoked by gsd-inbox triage / the maintainer.
- **DISP-01 audit test (new, `tests/`)** ← AST-scans `firestarter/` (+ the new `tools/`
  parser) → asserts no `support_status` write results from report parsing.
- **Ladder taxonomy doc (new/updated)** ← documents the four states + the N≥2 human-gated
  promotion process.

</code_context>

<specifics>
## Specific Ideas

- **Target repo is `henols/firestarter_app`.** Detection markers for a `dev test` report
  issue: the `[dev test]` title marker + the fenced-JSON `schema_version`.
- **`submit.py` (~L183) explicitly names Phase 114 the owner of "server-side
  template-based labeling."** The browser-URL submit path cannot self-label, so triage keys
  on the title marker + `schema_version`. Any auto-labeling (e.g. the maintainer's `gsd-inbox`
  adding a `community-reported` label during triage) is a **maintainer-side `gh` action**,
  never a community-side capability — consistent with the no-auto-graduate lock.
- The three ladder-state names are already present verbatim in `diagnostic_report.py`
  (`_DISPOSITION_*` prose) — Phase 114 formalizes them, it does not invent them.

</specifics>

<deferred>
## Deferred Ideas

- **Maintainer promotion CLI/tool** (the rejected D-01 alternative): a helper that ingests
  ≥2 agreeing reports and *prints* a proposed status change. If triage load ever justifies
  it, revisit — explicitly out of scope now (close phase, over-build risk).
- **Human-written community-* in a user-override DB** (the rejected D-02 alternative): would
  require read-path handling of community-* as a state distinct from "non-supported." Deferred.

### Reviewed Todos (not folded)
Reviewed all 9 `todo.match-phase 114` hits — every match is a generic-keyword false positive
(score ≤0.6 on words like "status" / "phase" / "milestone"); none touch disposition,
graduation, or inbox reconciliation. Not folded:
- `dev-test-hard-fail-unknown-chip.md` — closest topically, but it's a **pre-sweep guard**
  for the sweep engine (Phase 108/112), not disposition. Belongs elsewhere.
- `avrdude-mcu-detection-fallback.md`, `cobs-decoder-framelevel-deadline-wr01.md`,
  `fix-jp4-labels-and-rev2-revision-block.md`, `photograph-modified-rev-0.md`,
  `remove-dead-json-init-sizeof-pointer-bug.md`, `write-modifications-md-rework-trace.md`,
  `spike-databuffer-size-speed-delta.md`,
  `2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` — unrelated
  carry-forwards (firmware/hardware/COBS/docs); keyword-only matches.

</deferred>

---

*Phase: 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-reconciliation*
*Context gathered: 2026-07-03*
