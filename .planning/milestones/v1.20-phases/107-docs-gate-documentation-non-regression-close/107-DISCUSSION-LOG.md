# Phase 107: DOCS + GATE — Documentation & Non-Regression Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-02
**Phase:** 107-docs-gate-documentation-non-regression-close
**Mode:** `--auto` (autonomous; recommended default selected for every area)
**Areas discussed:** Breaking-change record location, Doc-scrub surface & depth, Gate-failure disposition, Golden-trace/baseline handling

---

## Breaking-change record location

| Option | Description | Selected |
|--------|-------------|----------|
| README section (both sub-repos) + CLAUDE.md note | Add a dedicated breaking-change section to `firestarter/README.md` and `firestarter_app/README.md`; note in agent-facing CLAUDE.md files. No new CHANGELOG.md. | ✓ |
| New CHANGELOG.md files | Create CHANGELOG.md in each sub-repo | |
| Both README + CHANGELOG | Duplicate across both surfaces | |

**Auto-selected (recommended):** README section in both sub-repos + CLAUDE.md note.
**Notes:** Neither sub-repo has an existing CHANGELOG; roadmap wording is "sub-repo READMEs/changelog"; README is the established public surface → no new file created.

---

## Doc-scrub surface & depth

| Option | Description | Selected |
|--------|-------------|----------|
| firestarter/CLAUDE.md + PROTOCOLS.md only | Scrub the two firmware docs that actually carry `type`/`mem_type`; verify host docs clean | ✓ |
| Scrub all four doc surfaces | Also rewrite host CLAUDE.md/README wire sections | |

**Auto-selected (recommended):** CLAUDE.md + PROTOCOLS.md only.
**Notes:** Grep confirmed host docs and `firestarter/README.md` carry no `type`/`mem_type` wire references. Preserve v1.16 `electrical.type` STRING content (INV-08/09) — out of scope.

---

## Gate-failure disposition

| Option | Description | Selected |
|--------|-------------|----------|
| STOP and surface as blocker | Any real regression halts the close; no auto-fix, no baseline regen | ✓ |
| Auto-fix and continue | Attempt to patch and proceed | |

**Auto-selected (recommended):** STOP and surface.
**Notes:** The close phase exists to *prove* zero regressions; a red gate signals a Phase 105/106 defect that needs its own fix, not a paper-over.

---

## Golden-trace / baseline handling

| Option | Description | Selected |
|--------|-------------|----------|
| Run-only, never regenerate | Re-verify existing golden traces + dispatch-mirror as-is | ✓ |
| Regenerate baselines | Refresh the golden headers | |

**Auto-selected (recommended):** Run-only.
**Notes:** Regenerating would erase the non-regression signal GATE-01/SAFE-01 depend on.

---

## Claude's Discretion

- Exact prose/headings of doc edits.
- Ordering of gate runs.
- Meta-repo `/workspaces/CLAUDE.md` left untouched unless a dangling ref is found.

## Deferred Ideas

- Meta-repo CLAUDE.md scrub (out of scope; roadmap names only sub-repo docs).
- LEGACY-01 / LEGACY-02 (v2): `FLAG_VPE_AS_VPP (0x10)` removal, `EPROM_LEGACY` naming.
- Reviewed-not-folded todos: VPP-skip firmware change, avrdude fallback, COBS frame-deadline (WR-01) — all out of scope for a docs/gate close.
