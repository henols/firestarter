# Phase 114: Disposition / No-Auto-Graduate Lock + Graduation Ladder + Inbox Reconciliation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-03
**Phase:** 114-disposition-no-auto-graduate-lock-graduation-ladder-inbox-reconciliation
**Areas discussed:** Ladder mechanism depth, Where community states live, "N≥2 reports agree" rule, INBOX-01 home + repo

---

## Ladder mechanism depth (GRAD-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Docs + auto-tag only | Reports auto-tag community-reported/community-fail via the existing DbDiff; ladder is documented vocabulary; human promotion is a manual maintainer step, made actionable by INBOX-01 triage (N-agreeing count). No new promotion tool/CLI. | ✓ |
| Add a maintainer promotion helper | Plus a human-invoked helper (tools/ script or dev subcommand) that ingests ≥2 agreeing reports, checks agreement, and PRINTS a proposed status change. Never writes the DB itself. | |

**User's choice:** Docs + auto-tag only (recommended)
**Notes:** Avoids over-building a close phase. SC2's "explicit human step" is satisfied by the manual maintainer action; "reachable once N≥2 agree" is satisfied by triage surfacing the agreement count. → CONTEXT D-01.

---

## Where community states live (GRAD-01/DISP-01 boundary)

| Option | Description | Selected |
|--------|-------------|----------|
| Report-side only | community-* states live ONLY on the report/DbDiff as a ladder-state label; chip_database.json's support_status never carries a community-* value; a chip reaches "supported" only via the unchanged human-authored build_db path. | ✓ |
| Allow human-written community-* in user-override DB | A maintainer MAY hand-write a community-* status into ~/.firestarter/database.json (user-override only, never generated, never auto). | |

**User's choice:** Report-side only (recommended)
**Notes:** Makes the DISP-01 grep/AST audit trivially true (single write locus = build_db.py) and avoids the `support_status != "supported"` non-dispatch footgun. → CONTEXT D-02.

---

## "N≥2 reports agree" rule (GRAD-01)

| Option | Description | Selected |
|--------|-------------|----------|
| dedup_fingerprint match | Two reports agree iff their Phase-113 dedup_fingerprint (chip + per-op verdict signature) matches; triage counts matches → "N agreeing." Distinct from the sweep's internal per-run N≥2 (Phase 108). | ✓ |
| chip + overall verdict | Looser: agreement = same chip + same overall PASS/FAIL, ignoring per-op detail. | |
| Maintainer judgment only | No automated metric; triage surfaces each diff and the maintainer eyeballs agreement. | |

**User's choice:** dedup_fingerprint match (recommended)
**Notes:** Reuses shipped code; deterministic; explicitly separates cross-report N from the Phase-108 internal per-run N. → CONTEXT D-03.

---

## INBOX-01 home + repo

| Option | Description | Selected |
|--------|-------------|----------|
| firestarter_app tools/ parser | Stdlib tools/parse_devtest_issue.py reads an issue body → emits DB-diff + agreement count; owns the schema (schema_version), unit-testable, survives gsd update; gsd-inbox/maintainer invokes it. Triages henols/firestarter_app. | ✓ |
| Project-local .claude/ command | Committed .claude/ command wrapping triage, parsing JSON in-workflow; native to the Claude triage flow, survives gsd update, but NL-driven (harder to unit-test). | |
| Edit installed gsd-core inbox.md | Add a firestarter-specific parse step directly to the installed workflow. Fragile — overwritten on gsd update. | |

**User's choice:** firestarter_app tools/ parser (recommended)
**Notes:** Confirmed target repo = henols/firestarter_app (submit.py SUBMIT_REPO); detection markers = `[dev test]` title + fenced-JSON schema_version (labels unreliable — community testers lack write access). submit.py:183 already names Phase 114 the owner of "server-side template-based labeling." → CONTEXT D-04.

---

## Claude's Discretion

- Exact AST-checker scope for the DISP-01 lock test (extend the SAFE-03 checker vs. a sibling) — follow SAFE-03 conventions (D-05).
- Precise `tools/parse_devtest_issue.py` CLI shape and how the N-agreeing count is gathered — must reuse dedup_fingerprint.
- Report-side ladder-state representation (derived field vs. formalized enum) — honor report-side-only (D-02).
- Where the ladder taxonomy is documented (README / CLAUDE.md / doc/).
- Whether to pick up the maintainer-side auto-labeling submit.py:183 hands to this phase.

## Deferred Ideas

- Maintainer promotion CLI/tool (rejected D-01 alternative) — revisit only if triage load justifies it.
- Human-written community-* in a user-override DB (rejected D-02 alternative) — would need read-path handling of community-* as distinct from non-supported.
- Reviewed-but-not-folded todos: all 9 `todo.match-phase 114` hits are generic-keyword false positives; closest (`dev-test-hard-fail-unknown-chip`) is a sweep-engine pre-guard (Phase 108/112), not disposition.
