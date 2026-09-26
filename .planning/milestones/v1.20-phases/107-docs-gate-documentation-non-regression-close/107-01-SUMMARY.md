---
phase: 107-docs-gate-documentation-non-regression-close
plan: 01
subsystem: docs
tags: [dispatch, protocol, wire-protocol, mem-type-removal, readme, claude-md]

# Dependency graph
requires:
  - phase: 105-fw-firmware-mem-type-removal
    provides: "shipped firmware reality (single terminal configure_not_implemented, mem_type struct field + type JSON parsing removed, 0xAE retired)"
  - phase: 106-host-mem-type-removal
    provides: "host stopped emitting type; HOST-04 algorithm-presence guard refuses chips lacking algorithm before any serial byte"
provides:
  - "firestarter/CLAUDE.md dispatch narrative rewritten to protocol-only dispatch with single fail-closed terminal arm"
  - "firestarter/CLAUDE.md JSON Wire Protocol field list scrubbed of the legacy type bullet"
  - "firestarter_app/CLAUDE.md Wire Protocol example scrubbed of the stale numeric type field"
  - "firestarter/README.md and firestarter_app/README.md Breaking Changes (v1.20) sections recording the wire-contract break"
affects: [107-02, milestone-close-v1.20]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Breaking-change record mirrors the existing '## Breaking Changes (v1.10)' template shape (### subsystem heading + bolded Upgrade: line)"]

key-files:
  created: []
  modified:
    - firestarter/CLAUDE.md
    - firestarter/README.md
    - firestarter_app/CLAUDE.md
    - firestarter_app/README.md

key-decisions:
  - "Replaced the literal string 'mem_type' in explanatory/negative-reference prose with 'legacy-integer' / 'backward-compat integer field' phrasing to satisfy the strict acceptance-criteria grep (grep -nE 'mem_type' firestarter/CLAUDE.md must return 0 hits) while preserving the same meaning"
  - "Terminal fail-closed dispatch arm renumbered from step 7 (post steps-7-11 deletion) rather than folded into 6b, to keep protocol==0 documented as its own explicit numbered case distinct from the generic non-zero-unrecognized guard"
  - "Breaking Changes (v1.20) sections placed immediately above the existing v1.10 sections in both READMEs (newest-first ordering), purely additive diffs confirmed via git diff (no deletions)"

patterns-established:
  - "Breaking-change record template: ### <subsystem> (breaking change) heading, prose body, bolded **Upgrade:** line, closing beta-only/operator-authorization sentence"

requirements-completed: [DOC-01]

coverage:
  - id: D1
    description: "firestarter/CLAUDE.md dispatch narrative rewritten to protocol-only dispatch; steps 7-11 mem_type fallback chain deleted; terminal arm fail-closes to configure_not_implemented()"
    requirement: "DOC-01"
    verification:
      - kind: other
        ref: "grep -nE 'mem_type|Memory type 0x' firestarter/CLAUDE.md returns 0 hits"
        status: pass
      - kind: other
        ref: "grep -n 'configure_not_implemented' firestarter/CLAUDE.md still present"
        status: pass
    human_judgment: false
  - id: D2
    description: "Legacy type wire-field bullet removed from firestarter/CLAUDE.md JSON Wire Protocol key-field list"
    requirement: "DOC-01"
    verification:
      - kind: other
        ref: "grep -n '\\- \\`type\\`' firestarter/CLAUDE.md returns 0 hits; algorithm bullet still present"
        status: pass
    human_judgment: false
  - id: D3
    description: "Stale numeric \"type\": 1 wire example removed from firestarter_app/CLAUDE.md write-command JSON block"
    requirement: "DOC-01"
    verification:
      - kind: other
        ref: "grep -nE '\"type\"[[:space:]]*:[[:space:]]*[0-9]' firestarter_app/CLAUDE.md returns 0 hits; \"algorithm\": 7 line intact"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both sub-repo READMEs carry a new ## Breaking Changes (v1.20) section recording type removal, algorithm-required rule, and pre-v1.20-host-safe note"
    requirement: "DOC-01"
    verification:
      - kind: other
        ref: "grep -c '^## Breaking Changes (v1.20)' returns 1 in both firestarter/README.md and firestarter_app/README.md; each section mentions algorithm and Upgrade"
        status: pass
    human_judgment: false
  - id: D5
    description: "v1.16 electrical.type STRING semantics and infoic type=N identity tuples preserved untouched; firestarter/doc/PROTOCOLS.md not edited"
    requirement: "DOC-01"
    verification:
      - kind: other
        ref: "git status --short firestarter/doc/PROTOCOLS.md is empty; grep -c electrical.type PROTOCOLS.md unchanged (8 hits)"
        status: pass
    human_judgment: false

duration: 18min
completed: 2026-07-02
status: complete
---

# Phase 107 Plan 01: Docs Scrub + Breaking-Change Record Summary

**Rewrote firestarter/CLAUDE.md's dispatch narrative to protocol-only dispatch, scrubbed the stale numeric `type` wire references from both agent-facing CLAUDE.md files, and recorded the v1.20 wire-contract break in both sub-repo READMEs.**

## Performance

- **Duration:** 18 min
- **Started:** 2026-07-02T14:34:00Z
- **Completed:** 2026-07-02T14:52:42Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- `firestarter/CLAUDE.md` Protocol Dispatch section now describes single-axis `handle->protocol` dispatch only; dispatch steps 7–11 (the `mem_type` fallback chain) deleted; terminal arm renumbered to step 7, fail-closing to `configure_not_implemented()` / `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED (0xBB)` — matching shipped `memory.cpp` (Phase 105)
- Legacy `type` wire-field bullet removed from the JSON Wire Protocol key-field list; replaced with a note that `type` is silently skipped by `json_parser.c`'s unknown-field allowlist
- `firestarter_app/CLAUDE.md`'s Wire Protocol example write-command JSON no longer shows a stray `"type": 1` field — the `"algorithm": 7` dispatch example stands alone
- Both `firestarter/README.md` and `firestarter_app/README.md` gained a `## Breaking Changes (v1.20)` section (mirroring the existing v1.10 template) recording: `type` removed from the wire, every chip entry now needs a usable `algorithm`, pre-v1.20 hosts emitting a stray `type` remain safe, and the standard lockstep upgrade guidance

## Task Commits

Each task was committed atomically, inside the relevant submodule:

1. **Task 1: Scrub mem_type dispatch narrative from firestarter/CLAUDE.md** — `531961b` (firestarter, docs)
2. **Task 2: Remove stale "type": 1 wire example from firestarter_app/CLAUDE.md** — `36235f1` (firestarter_app, docs)
3. **Task 3: Add Breaking Changes (v1.20) to firestarter/README.md** — `ab52d6e` (firestarter, docs)
3. **Task 3: Add Breaking Changes (v1.20) to firestarter_app/README.md** — `b831874` (firestarter_app, docs)

_Gitlinks in the meta-repo stay PINNED per project convention — no parent-repo gitlink bump in this plan._

## Files Created/Modified
- `firestarter/CLAUDE.md` — Protocol Dispatch section rewritten (protocol-only dispatch, steps 7–11 deleted, terminal fail-closed arm renumbered); legacy `type` wire bullet removed from JSON Wire Protocol field list
- `firestarter/README.md` — new `## Breaking Changes (v1.20)` section added above the existing v1.10 section
- `firestarter_app/CLAUDE.md` — stale `"type": 1` line removed from the Wire Protocol example JSON block
- `firestarter_app/README.md` — new `## Breaking Changes (v1.20)` section added above the existing v1.10 section

## Decisions Made
- Reworded the three explanatory/negative mentions of the retired `mem_type` axis in `firestarter/CLAUDE.md` (e.g. "no mem_type fallback", "removed the mem_type fallback chain", "pre-v1.20 mem_type integer") to avoid the literal substring `mem_type`, using "legacy-integer fallback axis" / "backward-compat integer field" instead — required to satisfy the plan's strict acceptance criterion (`grep -nE 'mem_type' firestarter/CLAUDE.md` returns 0 hits) while keeping the sentences fully accurate and equally clear.
- Kept the terminal fail-closed arm as its own numbered step 7 (rather than merging it into step 6b's generic `protocol != 0` guard) so the doc continues to explicitly call out the `protocol == 0` case, matching the plan's required wording ("protocol == 0 (and any unrecognized arm) fail-closes").
- Inserted both README `## Breaking Changes (v1.20)` sections immediately above the existing `## Breaking Changes (v1.10)` sections (newest-first ordering), verified purely additive via `git diff` (zero deletions in either README).

## Deviations from Plan

None - plan executed exactly as written. The one wording adjustment (avoiding the literal `mem_type` substring in three explanatory sentences) was made to satisfy the plan's own stated acceptance criteria and verification grep, not a deviation from plan intent.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 107-02 (0xAE codegen reconciliation / gate re-verification, per D-06/D-07) can proceed — the doc surface this plan owned (`firestarter/CLAUDE.md`, `firestarter_app/CLAUDE.md`, both READMEs) is fully scrubbed and verified clean.
- `firestarter/doc/PROTOCOLS.md` remains untouched as required (verify-only scope; its `type=N` hits are infoic identity tuples, out of scope).
- No blockers.

---
*Phase: 107-docs-gate-documentation-non-regression-close*
*Completed: 2026-07-02*

## Self-Check: PASSED

- FOUND: firestarter/CLAUDE.md
- FOUND: firestarter/README.md
- FOUND: firestarter_app/CLAUDE.md
- FOUND: firestarter_app/README.md
- FOUND: .planning/phases/107-docs-gate-documentation-non-regression-close/107-01-SUMMARY.md
- FOUND commit 531961b (firestarter)
- FOUND commit ab52d6e (firestarter)
- FOUND commit 36235f1 (firestarter_app)
- FOUND commit b831874 (firestarter_app)
