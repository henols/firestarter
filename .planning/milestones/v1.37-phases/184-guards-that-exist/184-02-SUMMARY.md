---
phase: 184-guards-that-exist
plan: 02
subsystem: docs
tags: [firmware, protocols-doc, dispatch-comment, claim-hygiene]

# Dependency graph
requires: []
provides:
  - "`firestarter/PROTOCOLS.md` no longer claims a deleted checker machine-reads it"
  - "`test_configure_memory.cpp`'s dispatch-table comment no longer claims a false one-to-one correspondence with `KNOWN_PROTOCOLS`"
affects: [184-05]

# Actuals (#2632)
actuals:
  tokens: 453
  tasks: 2
  commits: 3
  plan_head_before: 0d818bb6

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Retirement-statement shape: name the retired thing (directory, not filename), its date, its sha in backticks, and a bolded statement of the current absence — mirrors meta CLAUDE.md:12"
    - "Comment repair by subtraction only: delete a false clause, add nothing, under the project's absolute no-source-comments rule"

key-files:
  created: []
  modified:
    - firestarter/PROTOCOLS.md
    - firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp

key-decisions:
  - "D-09: PROTOCOLS.md's three-line 'claims region... machine-read' paragraph replaced with one honest line stating no tool reads the document, naming the retired tools/wiki/ directory + 2026-09-02 + 5426d7ef, bolding the current absence, and stating the dispatch table is maintained for human readers. No 'claims region' language survives."
  - "D-10: deleted exactly the clause 'one row per KNOWN_PROTOCOLS entry -- ' from the comment above kAllProtocolFamilies. Nothing was added or reworded; the true remainder (table-driven, one row not one function) and the memory.cpp:70-113 citation survive verbatim."
  - "D-16 (record, not adjudicate): kAllProtocolFamilies' 13 rows are unchanged; the drift against KNOWN_PROTOCOLS (12 entries) is out of this plan's scope and is recorded, not fixed, per the phase's verdict note (184-03/04)."
  - "D-06: the three other KNOWN_PROTOCOLS mentions in this file were seen and deliberately left — no backlog item filed."

patterns-established:
  - "Retirement statements name the directory + date + sha, never the deleted filename, so the exact claim being removed does not re-enter through its own replacement."

requirements-completed: [CLAIM-01, CLAIM-03]

coverage:
  - id: D1
    description: "firestarter/PROTOCOLS.md no longer claims a deleted checker (tools/wiki/dispatch_mirror.py) machine-reads the document; replaced with an honest line naming the retirement"
    requirement: CLAIM-01
    verification:
      - kind: other
        ref: "git grep -c 'dispatch_mirror' PROTOCOLS.md == 0; grep -c '5426d7ef' == 1; grep -c '2026-09-02' == 1; grep -ci 'claims region|Keep its table shape intact' == 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "test_configure_memory.cpp's kAllProtocolFamilies comment no longer asserts a false one-row-per-KNOWN_PROTOCOLS correspondence; table itself (13 rows) untouched; native dispatch suite unchanged at 23/23"
    requirement: CLAIM-03
    verification:
      - kind: integration
        ref: "pio test -e native -f 'native/avr/test_dispatch' (23 test cases: 23 succeeded, before and after edit)"
        status: pass
      - kind: other
        ref: "grep -c 'one row per KNOWN_PROTOCOLS entry' == 0; grep -c KNOWN_PROTOCOLS == 3 (down from 4); grep -c 'table-driven so adding a protocol' == 1; grep -c 'memory.cpp:70-113' == 1; grep -c '^    {0x' == 13"
        status: pass
    human_judgment: false

# Metrics
duration: 18min
completed: 2026-09-11
status: complete
---

# Phase 184 Plan 02: Firmware Claim Hygiene Summary

**Replaced `PROTOCOLS.md`'s dead machine-read claim with an honest retirement statement, and deleted the one false clause in the dispatch-table comment — both prose-only edits, native suite unchanged at 23/23.**

## Performance

- **Duration:** 18 min
- **Completed:** 2026-09-11T13:07:46Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `firestarter/PROTOCOLS.md` no longer claims that a deleted checker (`tools/wiki/dispatch_mirror.py`, retired 2026-09-02 by `5426d7ef`) machine-reads the document — replaced with one line naming the retired `tools/wiki/` directory, its date and sha, a bolded statement of the current absence, and a statement that the dispatch table is maintained for human readers.
- The false clause `one row per KNOWN_PROTOCOLS entry -- ` was deleted from the comment above `kAllProtocolFamilies` in `test_configure_memory.cpp`; the true remainder of the sentence and the `memory.cpp:70-113` citation survive with no word added, removed, or reordered.
- `kAllProtocolFamilies` itself (13 rows) is byte-unchanged, and the native dispatch test suite (`pio test -e native -f 'native/avr/test_dispatch'`) reports the same 23/23 passing cases before and after the edit, proving both changes are prose-only.

## Task Commits

Each task was committed atomically, inside `/workspaces/firestarter` on `gsd/v1.37-operator-safety-answered-reports-claim-hygiene`:

1. **Task 1: Replace `PROTOCOLS.md`'s machine-read claim with one honest line (D-09, CLAIM-01)** - `8c341f0` (docs)
2. **Task 2: Delete the one false clause above `kAllProtocolFamilies`, and nothing else (D-10, D-16)** - `ec7c1bb` (docs)

**Meta metadata commit:** advances the `firestarter` gitlink and adds this SUMMARY.

## Files Created/Modified
- `firestarter/PROTOCOLS.md` - three-line "claims region... machine-read" paragraph replaced with one honest retirement line
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` - false `one row per KNOWN_PROTOCOLS entry` clause deleted from the comment above `kAllProtocolFamilies`

## Decisions Made

**Replacement paragraph (D-09), quoted verbatim** — all six required elements present, `dispatch_mirror` occurring zero times:

> No tool machine-reads this document — the `tools/wiki/` checkers in the meta repository that
> used to cross-check the dispatch table here, the host tool and the firmware were retired on
> 2026-09-02 (`5426d7ef`), and **no automated dispatch guard exists now** — so the table below is
> maintained for human readers only.

Verified against `must_haves`:
- (1) states no tool machine-reads the document — yes.
- (2) names `tools/wiki/` (the directory, not `dispatch_mirror.py`) — yes.
- (3) `2026-09-02` and `` `5426d7ef` `` in backticks — yes.
- (4) bolded statement of the current absence — `**no automated dispatch guard exists now**` — yes.
- (5) states the dispatch table is maintained for human readers — yes.
- (6) zero occurrences of `dispatch_mirror` — confirmed by grep.
- Does not contain "claims region" or "Keep its table shape intact" — confirmed by grep (count 0).
- Title, purpose paragraph, wiki cross-reference, and the body after the replaced paragraph are byte-unchanged — confirmed: `git diff --stat` against the phase merge-base shows only `PROTOCOLS.md`, 5 insertions / 4 deletions, all inside the one paragraph.

**Surviving comment (D-10), quoted verbatim** — exactly the original words minus the deleted clause, in original order:

> `/* Walks configure_memory's protocol chain (memory.cpp:70-113) literally,`
> ` * table-driven so adding a protocol is one row, not one function. */`

No word was added, substituted, or reordered — only the clause `one row per KNOWN_PROTOCOLS entry -- ` was removed. This was achievable cleanly (deletion only, no replacement prose needed), so D-10's leave-it-and-record fallback was **not** invoked.

**The three other `KNOWN_PROTOCOLS` mentions in `test_configure_memory.cpp` were seen and deliberately left, per D-10's narrow scope and D-06's zero-filings rule:**
1. Line 9 (module header) — `One test per protocol in KNOWN_PROTOCOLS (build_db.py:89)`. The `build_db.py:89` line citation is already wrong (the symbol lives at line 137); flagged as not-filed in `184-CONTEXT.md` § Deferred, and out of D-10's single-clause scope.
2. Line 65 — `/* Positive dispatch tests — one per protocol in KNOWN_PROTOCOLS.` — makes the same one-per-entry claim as the deleted clause, but is a distinct sentence at a distinct site; D-10 names one clause, not a sweep.
3. Line 426 — `/* 13 protocol-positive tests (one per KNOWN_PROTOCOLS entry) */` near `main` — same reasoning.

No backlog item was filed for any of the three, per D-06 (this phase files zero backlog items on the CLAIM-03 axis). This is a record of what was seen and left, not an oversight.

**`kAllProtocolFamilies`** is byte-unchanged: `git diff` for the test file shows only the two-line comment edit; the table's braces show no change. Its 13-row drift against `KNOWN_PROTOCOLS`'s 12 entries (`0x34` host-only; `0x35`/`0x39` firmware-only) is recorded elsewhere in the phase's verdict note (D-16) — not adjudicated here, per the milestone's Out of Scope bar on reopening v1.11's DEC-05 / X88C64P decision.

**Both edits are prose-only**, per the plan's flagged assumption (inherited from `184-CONTEXT.md`'s `<code_context>` measurement, not re-measured here): a markdown file is not compiled, and a C comment is discarded by the preprocessor. The native test suite's unchanged 23/23 case count is the direct evidence for the C-file half of that claim.

## Deviations from Plan

None - plan executed exactly as written. Both tasks completed with the primary (deletion-only / replacement-paragraph) approach; neither task's fallback path was needed.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `firestarter/PROTOCOLS.md` and `test_configure_memory.cpp` are clean of the `dispatch_mirror` claim and the false `KNOWN_PROTOCOLS` correspondence clause; both commits are on `gsd/v1.37-operator-safety-answered-reports-claim-hygiene` inside `/workspaces/firestarter`.
- The `firestarter` gitlink in the meta repo is advanced to `ec7c1bb` by this plan's metadata commit, so `184-05`'s phase-level CLAIM-01 criterion sees the fix.
- CLAIM-01's app-repo half (`firestarter_app/tests/scan_paths.py:114`) and CLAIM-02/CLAIM-09 work are separate plans in this phase (not this plan's scope).
- No blockers for downstream plans in this phase.

## Self-Check: PASSED

- `firestarter/PROTOCOLS.md` exists and contains the replacement paragraph — confirmed by direct read.
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` exists and contains the surviving two-line comment — confirmed by direct read.
- Commit `8c341f0` found in `firestarter`'s `git log --oneline`.
- Commit `ec7c1bb` found in `firestarter`'s `git log --oneline`.
- All plan-level `<verify>` commands re-run above (grep counts, diffstat, `pio test -e native -f 'native/avr/test_dispatch'`) — all PASS.
- All `<acceptance_criteria>` for both tasks re-checked above — all PASS.

## Post-Execution Correction — a must-have premise is false (recorded by the phase orchestrator)

Found while executing `184-03`, after this plan had already committed and returned. Recorded
here rather than silently, because a false claim left standing in a claim-hygiene phase's own
record is the exact failure mode this phase exists to close.

**The claim.** This plan's must-have truth 3 reads, in part:

> "...and none refers to a `claims region` — **the file carries no claims-region delimiter of
> any kind**, so such a reference would name a boundary that does not exist (D-09)."

**The bolded clause is false, and was false before this phase started.**
`firestarter/PROTOCOLS.md` carries a delimiter pair and still does:

```
$ /usr/bin/grep -n "firestarter-claims" /workspaces/firestarter/PROTOCOLS.md
53:<!-- firestarter-claims-begin -->
82:<!-- firestarter-claims-end -->
```

They predate the phase — `git show e44ba6f:PROTOCOLS.md` has them at lines 52 and 81, shifted by
one only because this plan's replacement paragraph is one line longer than the three lines it
replaced. The now-deleted `tools/wiki/dispatch_mirror.py` parsed that pair structurally; it is
recoverable with `git show 5426d7ef^:tools/wiki/dispatch_mirror.py` in the meta repository. The
error is inherited from `184-CONTEXT.md` D-08 item 1, which states the same thing; `184-03`
independently found it, declined to carry it forward, and corrected the ground in
`.planning/notes/dispatch-invariant-retirement-verdict.md`.

**What IS satisfied.** The must-have's two operative requirements both hold, and the executor
verified both:

- no surviving sentence instructs a reader to keep the table shape intact for a tool — the
  "Keep its table shape intact when editing." sentence was deleted with the paragraph;
- no surviving sentence refers to a "claims region" — `grep -ci 'claims region'` returns 0.

Only the trailing factual justification about the file's markup is wrong.

**Disposition: the delimiters are LEFT IN PLACE, deliberately.** Deleting them was considered
and rejected:

- They name no checker, so they are outside CLAIM-01, whose subject is a file *naming*
  `tools/wiki/dispatch_mirror.py`. `git grep -l "firestarter-claims"` outside `.planning/`
  returns `firestarter/PROTOCOLS.md` alone — no tool, in any of the three repositories, reads
  them.
- They declare no guard to a human reader — they are inert HTML comments carrying no prose
  claim — so they are outside the phase Goal's second half as well.
- `184-05`'s prohibitions bar widening CLAIM-01 into a general retired-checker sweep. Removing
  an orphaned marker because its consumer is gone is exactly that widening.

The honest statement of the end state, superseding the must-have's wording: *`PROTOCOLS.md` no
longer claims anything machine-reads it, and its orphaned `firestarter-claims-*` delimiter pair
is left standing as inert markup, outside this phase's scope.*

No source file was changed by this correction; it edits this SUMMARY only.

---
*Phase: 184-guards-that-exist*
*Completed: 2026-09-11*
