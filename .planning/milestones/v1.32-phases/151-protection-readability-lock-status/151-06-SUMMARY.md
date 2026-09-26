---
phase: 151-protection-readability-lock-status
plan: 06
subsystem: host-cli
tags: [protection-readability, lock-status, pure-function, fail-closed, python, firestarter_app]

# Dependency graph
requires:
  - phase: 151-protection-readability-lock-status (plan 02)
    provides: "protection_readability.py's curated frozensets, readability_for_token(), AMBIGUOUS_DOC_CITATIONS"
provides:
  - "firestarter_app/firestarter/protection_readability.py — protection_gate_for_entry(entry, display_name) -> (class_token, reason), protection_gate(chip_name, db)"
  - "Four protocol-id frozensets: NO_MECHANISM_PROTOCOL_IDS, NOT_IMPLEMENTED_PROTOCOL_IDS, NOT_READABLE_PROTOCOL_IDS, CURATION_PROTOCOL_IDS"
  - "Four new gate-token constants: GATE_TOKEN_NO_MECHANISM, GATE_TOKEN_NOT_IMPLEMENTED, GATE_TOKEN_NOT_READABLE, GATE_TOKEN_UNDOCUMENTED_ALIAS"
  - "firestarter_app/tests/test_protection_resolution.py — 23-leg proof suite"
affects: [151-09, 151-11, 151-12, 151-13]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure (entry, display_name) -> (class_token, reason) resolution function, structurally incapable of returning protected/unprotected (no response parameter in the signature — D-12 leg 4's mechanism, not a convention)"
    - "Guard cascade with one early return per outcome, no single exit (mirrors sdp_capability_for_entry)"
    - "Hard KeyError/ValueError on malformed or unclassed input — no default branch, no silent fallback"

key-files:
  created:
    - firestarter_app/tests/test_protection_resolution.py
  modified:
    - firestarter_app/firestarter/protection_readability.py

key-decisions:
  - "OD-2 applied exactly: protocol-id 52 (0x34, XICOR/X88C64P,X88C64S) resolves not_implemented, not no_mechanism, because it carries protect_off_before: true. NOT_IMPLEMENTED_PROTOCOL_IDS = {16, 52}, making that census 40 (supersedes VALIDATION.md's 39)."
  - "Both raise controls (None entry, missing protocol-id) diverge deliberately from sdp_capability_for_entry's analogous guards: neither returns a refusal for an unknown/malformed entry, because none of D-09's eight classes means 'chip unknown' or 'malformed dict', and inventing one would be a fabricated value."
  - "The described-alias list for a curated (0x05/0x06) entry always lists every offending token (not just the ones matching the final decided state), so the C-6 alias-set leg and the mixed-entry legs are satisfied by one comprehension, matching sdp_capability.py's own idiom."
  - "AMBIGUOUS_DOC_CITATIONS notes are appended inline to the offending token's annotation (bracketed), so a C-17 disagreement is visible in the composed refusal reason, not just in the module's static data."

patterns-established:
  - "protection_gate_for_entry never touches entry['programming'] fields (protect_on_after/protect_off_before) — classification is entirely by protocol-id membership or curated alias token. Stated explicitly in the function docstring as discipline for future edits, since two of 746 rows (protocol 11) carry neither field at all."

requirements-completed: []  # advances LOCK-03, LOCK-04; both flip at 151-13 per phase convention

# Metrics
duration: ~50min
completed: 2026-08-20
status: complete
---

# Phase 151 Plan 06: `protection_gate_for_entry` — the Pure Resolution Function Summary

**Authored the pure `(entry, display_name) -> (class_token, reason)` classifier in `protection_readability.py`, structurally incapable of returning `protected`/`unprotected`, plus a 23-leg proof suite covering both measured worked examples and all three raise controls.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-20T13:43:00Z (approx, from context load)
- **Completed:** 2026-08-20T14:33:22Z
- **Tasks:** 2 (both `type="auto"`, Task 1 `tdd="true"`)
- **Files modified:** 2 (1 extended, 1 created)

## Accomplishments

- Extended `firestarter_app/firestarter/protection_readability.py` with:
  - The one admitted new import, `split_part_number_tokens` from `sdp_capability.py`.
  - Four gate-token constants (`GATE_TOKEN_NO_MECHANISM`, `GATE_TOKEN_NOT_IMPLEMENTED`, `GATE_TOKEN_NOT_READABLE`, `GATE_TOKEN_UNDOCUMENTED_ALIAS`), joining the pre-existing `GATE_TOKEN_READ_PERMITTED` — the five tokens this module can ever return.
  - Four protocol-id frozensets (`NO_MECHANISM_PROTOCOL_IDS` = {7,8,11,14,39,40,41} / 405 rows; `NOT_IMPLEMENTED_PROTOCOL_IDS` = {16,52} / 40 rows; `NOT_READABLE_PROTOCOL_IDS` = {13} / 84 rows; `CURATION_PROTOCOL_IDS` = {5,6} / 217 rows), each carrying a measured-row-count comment. Verified the counts directly against `chip_database.json`'s `programming.algorithm` field: 405+40+84+217 = 746, the full row count.
  - `protection_gate_for_entry(entry, display_name) -> tuple[str, str]` — the 7-step guard cascade specified by the plan, with the `0x10`/`0x34` reason distinguished and every 0x05/0x06 refusal naming every offending alias plus its state (and the `AMBIGUOUS_DOC_CITATIONS` note where applicable).
  - `protection_gate(chip_name, db)` — the thin name-keyed wrapper.
- Created `firestarter_app/tests/test_protection_resolution.py` — 23 test functions across the 10 required legs (table-driven algorithm classes, the OD-2 `0x34` leg, the `W29C022` named leg, the C-6 alias-set leg, the mixed third Winbond entry, unanimity in both directions with fixture-setup controls, the single-2-tuple invariant, all three raise controls, purity, and the C-17 live-surfacing proof).

## Task Commits

1. **Task 1: `protection_gate_for_entry` pure classifier** - `e36b72e` (feat, firestarter_app repo)
2. **Task 2: `test_protection_resolution.py`** - `b46bb95` (test, firestarter_app repo)

**Plan metadata:** (this commit, meta repo)

## Files Created/Modified

- `firestarter_app/firestarter/protection_readability.py` — added `protection_gate_for_entry`, `protection_gate`, four gate-token constants, four protocol-id frozensets, and the `sdp_capability` import.
- `firestarter_app/tests/test_protection_resolution.py` — new, 23-leg proof suite.

## Decisions Made

- **OD-2's `0x34` resolution, applied exactly as `151-DESIGN.md` §4 specifies.** `NOT_IMPLEMENTED_PROTOCOL_IDS = {16, 52}`, with the reason distinguishing the two members (0x10: documented-readable-but-unimplemented; 0x34: no handler at all). This makes the `not_implemented` census 40, not VALIDATION.md's 39 — stated explicitly in both the module comment and the test docstring.
- **The `None`/missing-`protocol-id` raise controls diverge from `sdp_capability_for_entry`'s analogous guards by design**, per the plan's explicit instruction: a capability question about an unknown chip has a sensible negative answer, but none of D-09's eight classes means "chip unknown" or "malformed dict" — inventing one would be exactly the fabricated value LOCK-03/LOCK-04 forbid.
- **The `described` list always names every offending alias**, regardless of which state ultimately decides the returned token — this is what makes the C-6 leg (`W29C040,W29C042`, both offending, different states) and the mixed-entry leg (naming both undocumented and not-readable aliases in the same reason) provable from one code path.
- **`AMBIGUOUS_DOC_CITATIONS` notes are appended inline** to the offending token's own annotation, in brackets, so the C-17 disagreement is legible in the actual refusal string a user or test would see — not merely present in the module's static data structure.

## Observed Non-Vacuity Evidence

Per the plan's `<output>` requirement, both required non-vacuity observations, captured directly:

**Leg 6's fixture-setup control**, observed to fail when the readable token is swapped for a non-curated one:
```
Fixture setup error: expected AM29F010,AM29F010B to be read_permitted before the mutation, measured 'undocumented_alias'
```

**Leg 8's unclassed-protocol-id control**, observed raising and naming the synthetic row:
```
protection_gate_for_entry: protocol-id 999 for 'SYNTHETIC_UNCLASSED_ROW' is not classed by this module. Every protocol id must land in NO_MECHANISM_PROTOCOL_IDS, NOT_IMPLEMENTED_PROTOCOL_IDS, NOT_READABLE_PROTOCOL_IDS or CURATION_PROTOCOL_IDS -- a synthetic or newly-added algorithm must be classed there before this row can be answered. No default branch exists; a silent fallback would make D-12 leg 6's exhaustiveness walk unwritable.
```

## Gate-Token Distribution Over the 217 `0x05`+`0x06` Entries

Computed by walking every `chip_database.json` entry with `programming.algorithm` in `{5, 6}` through `protection_gate_for_entry`. `151-12` pins these as literals:

| gate token | count |
|---|---|
| `read_permitted` | 81 |
| `not_readable` | 24 |
| `undocumented_alias` | 112 |
| **total** | **217** |

No `0x05`/`0x06` entry resolved `no_mechanism` or `not_implemented` (those tokens are reachable only from the algorithm-derived sets, never from the curation set) — consistent with the function's step ordering (steps 3-5 short-circuit before step 6 is ever reached for a `0x05`/`0x06` row, since those protocol ids are not members of `NO_MECHANISM_PROTOCOL_IDS`/`NOT_IMPLEMENTED_PROTOCOL_IDS`/`NOT_READABLE_PROTOCOL_IDS`).

## Verification

- `pytest tests/test_protection_resolution.py -x -o addopts=""` — **23 passed**.
- `pytest tests/test_protection_resolution.py -o addopts="" --collect-only -q` — **23 tests collected**.
- `pytest tests/test_protection_resolution.py tests/test_protection_table_citations.py tests/test_sdp_capability.py -o addopts="-ra"` — **41 passed** (6 + 12 sibling legs unaffected).
- Full app suite (`pytest -o addopts="" -q`, Python 3.11 venv, count line visible): **1736 passed** in 222.11s — baseline was 1713 (per orchestrator note); delta of exactly 23 matches the new test file, confirming zero regressions elsewhere.
- `ruff check firestarter/protection_readability.py tests/test_protection_resolution.py` — clean.
- `ruff format --check firestarter/protection_readability.py tests/test_protection_resolution.py` — clean (both files were reformatted once during authoring and re-verified clean).
- `python tools/check_mypy_watermark.py` — **34 errors, watermark 35** (1 below watermark; confirmed via `grep -i protection_readability` on full mypy output that none of the 34 errors are in the touched file).
- Neither `"protected"` nor `"unprotected"` appears as a string literal in `protection_readability.py`, in any quoting style (checked both `"`- and `'`-quoted forms via script, matching `151-09`'s planned AST-gate scope).
- No `except Exception:` and no bare `except:` anywhere in the module.

Python environment used: the pre-provisioned py3.11 venv at
`/tmp/claude-1000/-workspaces/f3ebf666-a01b-4de4-9860-8a006054ba0c/scratchpad/p151/venv311`
(per orchestrator constraint 7 — the devcontainer default `/usr/local` python is 3.12, and app CI is 3.11 only).

## Deviations from Plan

None — plan executed exactly as written. Both tasks landed as specified: Task 1's module extension in one commit, Task 2's new test file in a second commit, matching the plan's `files_modified` list exactly.

## Requirement Flips

**None.** This plan advances `LOCK-03` and `LOCK-04` per its frontmatter, but per the phase's convention both flip at `151-13`. No requirement checkbox or traceability row was touched in `.planning/REQUIREMENTS.md`.

## Issues Encountered

None beyond routine `ruff format` reformatting (applied and re-verified clean; not a deviation from the plan's specified behavior, just whitespace/line-wrap normalization ruff's formatter chose).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- `protection_gate_for_entry` and `protection_gate` are committed, importable with no loader, and ready for `151-11`'s `lock_status.py` to compose the eight D-09 output classes on top of this module's five gate tokens (the pure half is complete; `lock_status.py` is the impure half that accepts a device response and can reach `protected`/`unprotected`).
- `151-09`'s planned AST gate has a concrete target: the module contains no `"protected"`/`"unprotected"` literal in any quoting style, verified by source-text scan here; the AST gate can now assert this structurally.
- `151-12`'s planned literal-pinning test has the exact gate-token distribution over the 217 `0x05`+`0x06` entries recorded above (81 / 24 / 112).
- `151-13` still owns the `LOCK-03`/`LOCK-04` requirement-checkbox flips; no blockers for it from this plan.

## Self-Check: PASSED

- FOUND: firestarter_app/firestarter/protection_readability.py
- FOUND: firestarter_app/tests/test_protection_resolution.py
- FOUND commit: e36b72e
- FOUND commit: b46bb95

---
*Phase: 151-protection-readability-lock-status*
*Completed: 2026-08-20*
