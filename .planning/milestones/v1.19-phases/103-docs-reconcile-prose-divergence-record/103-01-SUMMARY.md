---
phase: 103-docs-reconcile-prose-divergence-record
plan: 01
subsystem: docs
tags: [markdown, protocol-naming, github-slugger, dispatch-docs]

# Dependency graph
requires:
  - phase: 100-name-author-approve-canonical-protocol-name-set
    provides: The operator-approved PROTO_ token / display-name / handler-family schema (§0 canonical bucket table in PROTOCOLS.md)
  - phase: 101-fw-define-proto-constants-relabel-dispatch
    provides: firmware PROTO_<NAME> constants + memory.cpp dispatch relabel, CLAUDE.md handler table sync
  - phase: 102-host-apply-names-in-the-host-cli-display
    provides: host `_PROTOCOL_DISPLAY_NAME` map with ASCII-normalized dashes (the divergence this plan documents)
provides:
  - All 12 §1.x PROTOCOLS.md headings renamed to PROTO_ token form
  - 8 regenerated §3 cross-link anchors (GitHub slugger), all resolving
  - 9 INV-01..09 rows augmented with PROTO_ token beside hex, grep-contract columns untouched
  - Two bucket-label jargon prose sentences rephrased
  - New "Name <-> Slug Divergence" callout recording the three D-04 facts
affects: [104, milestone-close-v1.19]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "GitHub slugger anchor regeneration: lowercase, keep underscores, drop punctuation except hyphen/underscore, em-dash -> '--', en-dash -> '-', spaces -> '-'"

key-files:
  created: []
  modified:
    - firestarter/doc/PROTOCOLS.md

key-decisions:
  - "Heading token substitution copied verbatim from the §0 canonical bucket table (PROTO_ token column) — no invented tokens"
  - "Cross-link anchors regenerated and grep-verified against actual rendered headings rather than hand-derived, to avoid silent stale-anchor drift"
  - "INV row augmentation prepends the PROTO_ token beside the existing hex in the behavior column only, leaving the four SAFE-02 grep-contract columns (id/handler/test-name/suite-path) byte-identical"
  - "D-04 callout placed immediately before the §0 bucket table, reusing the existing operator-approved blockquote style, without editing the table itself"

requirements-completed: [DOC-01, DOC-02]

coverage:
  - id: D1
    description: "All 12 §1.x headings renamed to PROTO_ token form; hex + description kept verbatim"
    requirement: "DOC-01"
    verification:
      - kind: unit
        ref: "grep -c '^### 1\\.[0-9]* — 0x[0-9A-Fa-f]* PROTO_' firestarter/doc/PROTOCOLS.md (== 12)"
        status: pass
    human_judgment: false
  - id: D2
    description: "8 §3 cross-link anchors regenerated from renamed headings and resolve correctly"
    requirement: "DOC-01"
    verification:
      - kind: unit
        ref: "python anchor-vs-fragment cross-check script embedded in 103-01-PLAN.md Task 1 verify block (ANCHORS_OK)"
        status: pass
    human_judgment: false
  - id: D3
    description: "9 INV-01..09 rows name their PROTO_ token beside the hex; id/handler/test-name/suite-path columns byte-identical"
    requirement: "DOC-01"
    verification:
      - kind: unit
        ref: "per-INV grep loop (INV_TOKENS_OK) + git diff column-preservation check in 103-01-PLAN.md Task 2 verify block"
        status: pass
    human_judgment: false
  - id: D4
    description: "Two bucket-label jargon prose sentences rephrased (§1.8 pin-roles, §2.1); §2 provenance + datasheet KEEPs untouched"
    requirement: "DOC-01"
    verification:
      - kind: unit
        ref: "PROSE_PURGED / PROVENANCE_RETAINED grep checks in 103-01-PLAN.md Task 2 verify block"
        status: pass
    human_judgment: false
  - id: D5
    description: "New 'Name <-> Slug Divergence' callout records the three D-04 facts (frozen-slug map, NAME-F1 deferral, host ASCII-dash deviation)"
    requirement: "DOC-02"
    verification:
      - kind: unit
        ref: "CALLOUT_PRESENT / THREE_FACTS_PRESENT / TABLE_UNTOUCHED grep checks in 103-01-PLAN.md Task 3 verify block"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-07-01
status: complete
---

# Phase 103 Plan 01: Reconcile PROTOCOLS.md Prose + Add Divergence Record Summary

**Renamed all 12 `firestarter/doc/PROTOCOLS.md` §1.x headings to `PROTO_` token form, regenerated the 8 dependent cross-link anchors, augmented the 9 INV-matrix rows with their tokens, purged residual bucket-label jargon from two prose sentences, and added a "Name ↔ Slug Divergence" callout recording the frozen-slug/NAME-F1/host-ASCII-dash facts — closing the v1.19 naming milestone's documentation leg.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-07-01T21:52:50Z
- **Completed:** 2026-07-01T21:56:24Z
- **Tasks:** 3
- **Files modified:** 1 (`firestarter/doc/PROTOCOLS.md`, inside the `firestarter` submodule)

## Accomplishments
- All 12 `### 1.N — 0xNN` headings now carry the operator-approved `PROTO_` token (copied verbatim from the §0 canonical bucket table) instead of the old minipro-inherited slug jargon (`FLASH-AMD-STD`, `EPROM-QUICK`, etc.); hex + trailing description preserved verbatim
- Regenerated all 8 §3 "Cross-links to per-bucket sections" anchors from the renamed headings using the GitHub slugger rules already proven against this file (em-dash → `--`, en-dash → `-`, underscores kept) — every `](#1...)` fragment resolves, verified programmatically against the actual rendered heading set
- Augmented all 9 INV-01..INV-09 rows in the §3 traceability matrix to name their `PROTO_` token beside the existing raw hex in the "One-line behavior" column, while keeping the SAFE-02 grep-contract columns (INV id, owning handler file, planned native test function name, suite path) byte-identical
- Rephrased the two remaining bucket-label jargon prose sentences (§1.8 pin-roles "Unlike AMD flash..." and §2.1 "not FLASH-AMD-STD variants...") to name the new tokens instead, while leaving the §2 minipro-provenance prose (`IC2_ALG_ITE`) and datasheet-accurate KEEPs untouched
- Added a new "Name ↔ Slug Divergence" callout (blockquote, matching the existing §0 operator-approved callout style) immediately above the §0 bucket table, recording the three D-04 facts: the frozen-slug column is the canonical old-slug↔new-name map; `datasheets/` folder slugs are intentionally frozen (NAME-F1 deferred); the host CLI ASCII-normalizes dashes in its display strings (Phase 102 D-02), a punctuation-only deviation from this doc's em-dash names

## Task Commits

Each task was committed atomically inside the `firestarter` submodule:

1. **Task 1: Rename 12 §1.x headings + regenerate 8 §3 cross-link anchors (D-01)** - `14491e9` (docs)
2. **Task 2: Augment 9 INV rows with PROTO_ tokens + purge 2 prose jargon sentences (D-02/D-03)** - `6395a7e` (docs)
3. **Task 3: Add "Name ↔ Slug Divergence" callout (D-04)** - `2d93379` (docs)

**Meta-repo gitlink bump:** staged (`firestarter` submodule pointer advanced `89e9e56` → `2d93379`); committed as part of this plan's metadata commit below.

_Note: this is a docs-only plan — every commit type is `docs`, no `feat`/`fix` commits were needed._

## Files Created/Modified
- `firestarter/doc/PROTOCOLS.md` - 12 §1.x headings renamed to `PROTO_` token form; 8 §3 cross-link anchors regenerated; 9 INV rows augmented with tokens; 2 prose sentences rephrased; new "Name ↔ Slug Divergence" callout added

## Decisions Made
- Heading token substitutions were copied verbatim from the §0 canonical bucket table's `PROTO_ token` column — no token was invented or hand-derived, per plan instruction.
- Cross-link anchors were regenerated and then grep-verified against the actual rendered heading set (not hand-guessed), catching any slugger-rule mismatch before commit.
- INV row edits touched only the "One-line behavior" column; the four SAFE-02 grep-contract columns were left byte-identical, confirmed via `git diff` column inspection.
- The D-04 callout was placed directly above the §0 bucket table (reusing the existing operator-approved blockquote style) rather than as its own top-level section, since it directly annotates that table's frozen-slug column.

## Deviations from Plan

None - plan executed exactly as written. All three tasks' automated verify blocks passed on the first attempt; no auto-fixes, no blocking issues, no architectural questions arose.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required. This was a documentation-only change to a single Markdown file.

## Next Phase Readiness
- `firestarter/doc/PROTOCOLS.md` is now fully coherent with the `PROTO_` tokens applied in firmware (Phase 101) and host display (Phase 102); the name↔slug divergence is recorded in one authoritative place.
- Plan 103-02 (GATE re-verification / milestone close) is unblocked — no code, DB, or wire changes were made, so `diff_db.py` / `check_dispatch.py` / dispatch-mirror / native golden-trace gates are expected to remain green (docs-only diff, single file changed).
- The meta-repo `firestarter` gitlink is staged for the plan-completion commit, advancing to `2d93379`.

## Self-Check: PASSED

- FOUND: `firestarter/doc/PROTOCOLS.md`
- FOUND: `.planning/phases/103-docs-reconcile-prose-divergence-record/103-01-SUMMARY.md`
- FOUND commit `14491e9` (Task 1, firestarter submodule)
- FOUND commit `6395a7e` (Task 2, firestarter submodule)
- FOUND commit `2d93379` (Task 3, firestarter submodule)
- FOUND commit `6054fed` (plan-completion, meta repo)
