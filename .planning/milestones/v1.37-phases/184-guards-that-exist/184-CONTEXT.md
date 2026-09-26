# Phase 184: Guards That Exist - Context

**Gathered:** 2026-09-11
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers four things and nothing else:

1. **Two live references to a deleted checker removed** — `firestarter/PROTOCOLS.md:11` and
   `firestarter_app/tests/scan_paths.py:114` stop naming `tools/wiki/dispatch_mirror.py`, deleted
   2026-09-02 by `5426d7ef` (CLAIM-01).
2. **The two orphaned `planted_dispatch_*` fixtures disposed** — their consumer
   `tests/test_dispatch_mirror.py` was deleted 2026-08-31 by `39ea3e8` (CLAIM-02).
3. **A recorded verdict on the three-way dispatch invariant** — retire or re-guard, decided and written
   down (CLAIM-03).
4. **A fail-closed check that a `ScanPathEntry` cannot name a guard file that does not exist** — the
   strand exists because nothing detected any of the above (CLAIM-09).

**Not in this phase:**
- **Building a replacement dispatch guard.** `REQUIREMENTS.md` § Out of Scope: "Building the guard is a
  separate milestone's work if the answer is yes." D-13 answers "no" anyway.
- Any firmware protocol or behaviour change (milestone-wide Out of Scope). The two firmware-repo edits
  this phase makes are prose-only: a paragraph in `PROTOCOLS.md` and a false clause in a test comment.
- Adjudicating the three protocol-list divergences (D-16).
- The other four CLAIM requirements — CLAIM-04…07 are Phase 185, CLAIM-08 is Phase 185.

</domain>

<decisions>
## Implementation Decisions

### CLAIM-01 — the two live claims, and the grep that finds them

- **D-01:** The sweep is complete at `dispatch_mirror` — no broader retired-checker sweep is needed.
  Measured during discussion: of the eight files `5426d7ef` deleted (`wiki.py`, `honest01_claims.py`,
  `honest02_truth.py`, `provenance_footers.py`, `selftest.sh`, `claim-allowlist.json`,
  `claim-vocabulary.json`, `dispatch_mirror.py`), only `dispatch_mirror.py` is still named outside
  `.planning/` in any of the three repositories. The other seven are clean. A planner must not widen
  CLAIM-01 into a general retired-checker hunt on the theory that more will turn up.

- **D-02:** The two surviving provenance citations are **re-dated, not deleted and not ignored.**
  `firestarter_app/tools/check_no_exists_proxy.py:19` and
  `firestarter_app/tests/fixtures/planted_no_exists_proxy.py:20,41` cite `tests/test_dispatch_mirror.py`
  as the origin of the compound `not (a.exists() and b.exists())` shape their lint catches. That
  provenance is load-bearing — it is the only record of why the compound arm exists in a live checker —
  so it is kept and made recoverable: the citation states the module was deleted 2026-08-31 in `39ea3e8`.
  Stripping the name would protect the grep while inviting a future "why do we guard the compound shape
  at all?" deletion; leaving it untouched fixes nothing, since the citation stays unverifiable, which is
  the CLAIM strand's own complaint.
  — **Reversibility:** reversible — prose in two docstrings.

- **D-03:** **Success criterion 1 is amended** to exclude a citation that names its own deletion.
  The criterion's literal command — `git grep -n 'dispatch_mirror' -- . ':(exclude).planning'` — is a
  bare substring and collides across two unrelated deletions: `tools/wiki/dispatch_mirror.py` (meta,
  deleted 2026-09-02) and `tests/test_dispatch_mirror.py` (app, deleted 2026-08-31). CLAIM-01's own words
  are narrower — "names `tools/wiki/dispatch_mirror.py` as a **live guard**." Precedent for amending a
  criterion with the reason on the record: Phase 182's criterion-4 note (a literal grep answering the
  wrong question) and Phase 183's D-08 (criterion amended alongside the code). The amendment lands in the
  same phase as the work, per 183's D-08 discipline.
  — **Reversibility:** reversible.

- **D-04:** **Meta's `CLAUDE.md:12` is folded in.** It states that of `tools/wiki/` "only
  `MIGRATION-TABLE.md` survives there" — false since 2026-09-08, when that file moved to
  `.planning/v1.35/MIGRATION-TABLE.md` and `tools/wiki/` was removed entirely (`tools/` now holds
  `catalog/` alone). Found by this phase's own D-01 sweep, same category as CLAIM-01 ("things the repo
  says that are not true"), a one-line repair, not a new capability. It names `tools/wiki/`, not
  `dispatch_mirror`, so criterion 1's grep does not catch it — a planner must carry it deliberately.
  — **Reversibility:** reversible.

### CLAIM-02 / CLAIM-03 — the invariant and its artifacts

- **D-05:** **CLAIM-03's verdict is RETIRE OUTRIGHT.** No successor guard, no backlog item, no
  follow-on filing. Operator decision, taken against the orchestrator's recommendation (which was to
  retire the three-way and backlog the narrower two-way successor). A future need re-opens the question
  from scratch.
  — **Reversibility:** reversible in principle — but nothing will be watching, so re-opening depends on
  someone noticing unaided, which is what this milestone exists to correct. Recorded as the operator's
  informed call.

- **D-06:** **No successor backlog item is filed — this is deliberate, not an oversight.** A planner or
  executor must NOT helpfully file a `KNOWN_PROTOCOLS` ↔ `kAllProtocolFamilies` guard item, nor an
  "unverified drift" item, on the grounds that the evidence below obviously warrants one. The operator
  chose the branch that files nothing; an open-question item would quietly reinstate what was closed.
  This phase files zero backlog items on the CLAIM-03 axis. (Contrast 182's 999.55–999.59 and 183's
  999.63–999.66 — that pattern does not apply here.)

- **D-07:** **The two fixtures are deleted**, not re-pointed. CLAIM-02 permits "re-pointed at a consumer
  that exists", but under D-05 no consumer will ever exist. Deleted:
  `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp` and
  `planted_dispatch_missing_hex.cpp`. Their deletion also clears two of the five app-repo
  `dispatch_mirror` grep hits.
  — **Reversibility:** reversible — recoverable from git; D-08 preserves the knowledge separately.

- **D-08:** **A `.planning/notes/` verdict document carries CLAIM-03's record**, following 182
  (`jumper-display-ground-truth.md`) and 183 (`ae29f2008-classification-verdict.md`). It must carry all
  four of:
  1. **The verdict and its grounds** — retired outright; two of the three legs never guarded anything.
  2. **The two-deletion history** — `39ea3e8` (2026-08-31) deleted `test_dispatch_mirror.py` because its
     module-scope `fw_path("doc", "PROTOCOLS.md")` aborted the whole app suite at collection once
     `firestarter/doc/` was deleted, and deliberately re-pointed the surviving `ScanPathEntry` at
     `tools/wiki/dispatch_mirror.py` "(meta repo; relocated by 168-10)". Two days later `5426d7ef`
     (2026-09-02) retired every `tools/wiki/` checker, demolishing the receiving end of a handoff that
     had just been written. Neither commit intended to retire the invariant.
  3. **The fail-open regex finding** the deleted fixtures proved — the C++ leg extracted every
     `0x[0-9A-Fa-f]+` token from whole file text with no comment-awareness, so a comment-only mention of
     a protocol satisfied the gate exactly as well as a real dispatch case. `planted_dispatch_comment_only_hex.cpp`'s
     paired leg asserted GREEN, and the GREEN **was** the finding. This is the knowledge the fixtures
     encoded; it must survive their deletion.
  4. **The drift table** — per D-16, recorded as measured and explicitly not adjudicated.
  — **Reversibility:** reversible.

- **D-09:** **`firestarter/PROTOCOLS.md:11-13` loses the paragraph and gains one honest line** stating
  that no tool machine-reads this document and the dispatch table is maintained for human readers.
  Measured during discussion: nothing machine-reads `PROTOCOLS.md` in any repository, and the file
  contains no claims-region delimiter at all — so the paragraph's instruction "Keep its table shape
  intact when editing" guards a shape no tool reads and no marker bounds. Stating the absence rather than
  silently erasing it mirrors meta `CLAUDE.md`'s "**no automated wiki guard exists now**" precedent.
  Markdown, so the source-comment rule does not apply.
  — **Reversibility:** reversible.

- **D-10:** **`firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:201` loses only its
  false clause.** The comment claims "one row per `KNOWN_PROTOCOLS` entry", which is false in three
  places (D-15). The remainder of that sentence — that the table is table-driven so adding a protocol is
  one row, not one function — is true and stays.
  — **HARD CONSTRAINT:** `CLAUDE.md`'s source-comment rule is absolute and not overridable by this plan.
  The permitted operation is **deleting a false clause**. Writing a corrected or replacement comment is
  NOT available to an executor. If the clause cannot be removed without authoring replacement prose,
  leave it and record the deviation in the plan's `SUMMARY.md`.
  — **Reversibility:** reversible.

### CLAIM-09 — the guard that stops it recurring

- **D-11:** **`resolved_by` is restricted to bare filenames resolving to `tests/<name>`.** The check
  asserts every entry is a bare filename that `is_file()` under `firestarter_app/tests/`; a cross-repo
  path, or any annotated string, fails the test where it is written. Fail-closed by construction — the
  defect becomes *unwritable* rather than undetectable. Rejected alternatives: typed cross-repo entries
  (the meta repo is never checked out in app CI, so a meta-repo resolver degrades to a skip — the exact
  fail-open mode CLAIM-09 exists to stop) and convention-parsing of the prose (the string handling is
  itself unguarded, and a new annotation shape slips through silently). If a genuine cross-repo handoff
  is ever needed, the author must extend the type and state how it gets checked — precisely what 168-04
  was never forced to do.
  — **Reversibility:** costly — widening it later means re-deciding the fail-open question this decision
  closes, and the type change touches every entry.

- **D-12:** **The guard is a fifth test in `firestarter_app/tests/test_scan_paths_resolve.py`**, beside
  the four that already iterate this inventory, and mirrors `test_all_eleven_tool_resolvers_exist`'s
  shape (that test is Population B's existing precedent for exactly this check;
  `ScanPathEntry.resolved_by` is the Population A gap). NOT a `tools/check_*.py` — `firestarter_app/tools/`
  sits outside every CI gate (no mypy, no `ruff check`, no `ruff format`), for no gain when the data is
  already a Python module the suite imports.
  — **Reversibility:** reversible.

- **D-13:** **The guard's RED on the real stale entry is what removes it — no hand-delete first.** Build
  the check, observe it go red against the *actual* rotted entry
  (`test/native/avr/test_dispatch/test_configure_memory.cpp` → `tools/wiki/dispatch_mirror.py …`), then
  remove the entry and observe green. That proves the guard catches the defect that motivated it rather
  than only a synthetic. Criterion 2's **planted** entry then runs as a second control afterward, proving
  the guard stays fail-closed once the real defect is gone: plant, observe red, remove, observe green.
  Both halves are required — the real one is the stronger evidence, the planted one is the criterion's
  literal wording. Same RED-first discipline as 183-04.
  — **Reversibility:** n/a — an execution-order requirement.

- **D-14:** **The `ScanPathEntry` is removed, not re-pointed or marked.** Measured during discussion:
  `scan_paths.py:113` is the only place in the app repo that names `test_configure_memory.cpp`, so
  nothing resolves it. By the inventory's own definition — "every path this repo **resolves** into the
  sibling `firestarter` firmware repo" — an entry nothing resolves does not belong, regardless of the
  firmware file still existing and still being built by `pio test`. A "no live consumer" marker was
  rejected: it would require a sanctioned escape hatch in D-11's check, reintroducing the silent-claim
  failure mode.
  — **Reversibility:** reversible.

- **D-15:** **`_FLOOR` is re-anchored to a reason, not a census; the stale docstring figure is corrected
  in the same pass.** The number stays **6**, but its justification stops being "measured at plan time"
  — a census goes stale on every legitimate removal, and it already has twice (168-04 dropped an entry
  without updating the prose; D-14 drops another). Re-anchored to why the inventory cannot be doing its
  job below that count, with a note that a deliberate removal must move the floor deliberately rather
  than reflexively to match. Both floor assertions are in scope: `test_inventory_is_non_vacuous` asserts
  `len(ALL_CROSS_REPO_PATHS) >= _FLOOR` **and** `len(CROSS_REPO_TEST_PATHS) >= _FLOOR`; both are 7 today
  and both land on 6 after D-14. The module docstring still claims **8** — correct it to the real count.
  — **Reversibility:** reversible.

- **D-16:** **The drift is recorded as measured and explicitly NOT adjudicated.** The note states the
  three divergences, names the reason each side already carries, and says in its own words that this
  phase did not verify those reasons — so no reader mistakes the record for a clean bill of health.
  Adjudicating would mean reopening v1.11's DEC-05 and the X88C64P not-implemented decision, which is
  protocol-domain work the milestone's Out of Scope bars, and a defect surfaced there would have no room
  to be fixed in this milestone.
  — **Reversibility:** reversible.

### Claude's Discretion

The operator deferred four decisions with "You decide" / "No preference". These are Claude's calls,
recorded above with their reasoning, and a planner may revisit them on evidence:

- D-02 + D-03 (what happens to the surviving provenance citations, and the criterion amendment)
- D-13 + D-15 (guard-removes-the-entry, and the floor re-anchor — the operator's "you decide"
  covered the floor question; D-13 was offered as one of its options and composes with D-15)
- D-11 (answered "No preference"; the orchestrator's recommendation was taken)
- D-16 (record-don't-adjudicate)
- D-04 and D-07/D-08 were decided by the orchestrator as mechanical consequences of
  operator choices, not offered as questions.

The two decisions the operator made directly and which must NOT be revisited without asking them:
**D-05** (retire outright — chosen over the recommended retire-plus-backlog) and **D-09**/**D-10**
(delete and state the absence — chosen over plain deletion).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/REQUIREMENTS.md` § CLAIM — CLAIM-01, CLAIM-02, CLAIM-03, CLAIM-09 verbatim; also the
  **Out of Scope** table, whose "Re-guarding the three-way dispatch invariant" row bounds D-05.
- `.planning/ROADMAP.md` § Phase 184 — the four success criteria. **Criterion 1 is amended by D-03**;
  criterion 2's plant-observe-red-remove wording drives D-13's second half.

### The guard and its data (CLAIM-09, CLAIM-01)
- `firestarter_app/tests/scan_paths.py` — `ScanPathEntry` (the `resolved_by` field is the rot site, at
  line 114), `CROSS_REPO_TEST_PATHS`, `ALL_CROSS_REPO_PATHS`. The module docstring's "8 paths" figure is
  stale (D-15).
- `firestarter_app/tests/test_scan_paths_resolve.py` — the four existing tests.
  `test_all_eleven_tool_resolvers_exist` is the Population B precedent D-12 mirrors; `_FLOOR` and
  `test_inventory_is_non_vacuous` are D-15's subject.
- `firestarter_app/tools/check_no_exists_proxy.py` and
  `firestarter_app/tests/fixtures/planted_no_exists_proxy.py` — the two provenance citations D-02
  re-dates. Do not confuse this live lint with the deleted `test_dispatch_mirror.py` it cites.

### The retired invariant (CLAIM-02, CLAIM-03)
- `firestarter/PROTOCOLS.md` lines 11–13 — the paragraph D-09 replaces.
- `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` — `kAllProtocolFamilies` at
  line 203 (13 rows); the false clause D-10 deletes is in the comment at line 201.
- `firestarter_app/tools/build_db.py` line 137 — `KNOWN_PROTOCOLS` (12 entries), the other side of the
  drift.
- `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp` and
  `planted_dispatch_missing_hex.cpp` — read both **before** deleting them (D-07); their headers are the
  source for D-08's fail-open finding.

### Precedent and history
- `.planning/todos/completed/migration-table-relocated-out-of-tools.md` — records `5426d7ef`'s eight
  deletions, and the ~1,150 `.planning/` citations to them deliberately preserved as retirement
  evidence. Establishes that historical-by-intent citations are not repaired; D-02's re-dating applies
  to **source**, a category that precedent does not cover.
- `.planning/phases/183-.../183-CONTEXT.md` D-08 — criterion amended in the same phase as the code.
- `.planning/ROADMAP.md` § Phase 182 "Criterion 4 note" — a literal grep command answering the wrong
  question, satisfied through scoped tool-independent forms instead. Direct precedent for D-03.

### Project rules that constrain execution
- `/workspaces/CLAUDE.md` § "Source code comments — hard rule" — binds D-10. Not overridable by a plan,
  task, skill, or subagent instruction.
- `/workspaces/CLAUDE.md` § "Milestone close and branch protection" — `git.base_branch` is `beta`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`test_all_eleven_tool_resolvers_exist`** (`tests/test_scan_paths_resolve.py:143`) — the exact shape
  D-12's new test copies: a list comprehension filtering `not (_DIR / name).is_file()`, then one
  assertion naming every missing file at once rather than failing on the first. Its
  `assert len(...) == 11` census arm is the anti-pattern D-15 corrects; do not copy that part.
- **`_resolvers_for`** (same file, line 53) — already walks `entry.resolved_by`, so the iteration the
  new test needs exists and is proven.
- **The `.planning/notes/` verdict pattern** — `jumper-display-ground-truth.md` (182) and
  `ae29f2008-classification-verdict.md` (183) are the two templates for D-08.

### Established Patterns
- **RED-first proof** — 183-04 landed a guard, watched it go red, then made the change. D-13 requires
  the same, twice (real defect, then planted control).
- **Fail-closed over fail-open** — the repo has been bitten repeatedly by gates that skip when their
  scan target is absent. D-11 exists to make the fail-open shape unrepresentable rather than merely
  discouraged.
- **Fixture severance / deliberate controls** — `planted_*` fixtures are a committed convention here.
  Two of them die in D-07; `planted_no_exists_proxy.py` stays and is edited by D-02.

### Integration Points
- **Three repositories are touched.** Meta (`CLAUDE.md`, `.planning/notes/`, `.planning/ROADMAP.md`,
  `.planning/REQUIREMENTS.md`), firmware (`PROTOCOLS.md`, `test_configure_memory.cpp` — prose only), app
  (`scan_paths.py`, `test_scan_paths_resolve.py`, `check_no_exists_proxy.py`,
  `planted_no_exists_proxy.py`, two fixture deletions).
- **The firmware and app edits are file-disjoint** and share no dependency, so they can run in parallel
  waves; only the meta record close-out depends on both.
- **Gitlink:** per standing practice since v1.36, the submodule gitlink is advanced per-phase by name —
  both sub-repos are written here, so both advance.
- **No CI gate reads any file this phase edits for behaviour** — the firmware edits are comment/prose
  only and cannot move flash figures, so Phase 185's `check_size_baseline.py` re-record is unaffected by
  this phase.

</code_context>

<specifics>
## Specific Ideas

- The drift measured during discussion, for D-08's table and D-16's wording:

  | Protocol | `KNOWN_PROTOCOLS` (`build_db.py:137`) | `kAllProtocolFamilies` (`test_configure_memory.cpp:203`) | Reason each side carries |
  |---|---|---|---|
  | `0x34` | present | **absent** | "XICOR X88C64P — included as protocol-not-implemented" |
  | `0x35` | **absent** | present | "NOT 0x35 or 0x39 — removed by v1.11 DEC-05" |
  | `0x39` | **absent** | present | same |

  Totals: 12 host-side vs 13 firmware-side. Neither figure is verified by anything.

- The exact stale entry D-13/D-14 removes, verbatim from `tests/scan_paths.py:111-114`:
  ```python
  ScanPathEntry(
      "test/native/avr/test_dispatch/test_configure_memory.cpp",
      ("tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)",),
  ),
  ```

- The six `resolved_by` values that remain after D-14, all bare `tests/` filenames — the uniformity D-11
  relies on: `test_revision_constants_parity.py`, `test_check_is_memory_cmd_no_ifdef.py`,
  `test_check_no_log_in_sdp_window.py`, `test_sdp_table_parity.py`, `test_sdp_bus_config_drift.py`,
  `test_gen_validation_header.py`, `test_cap03_ack_layout_parity.py`, `test_json_key_parity.py`.

</specifics>

<deferred>
## Deferred Ideas

- **The two-way `KNOWN_PROTOCOLS` ↔ `kAllProtocolFamilies` successor guard.** Both sides are structured
  and machine-readable (a Python set literal and a C array), so it could be checked properly rather than
  through the comment-blind regex that made the deleted leg fail open — and the rule would be "every
  difference is accounted for", not "the lists are equal". **The operator explicitly declined to file
  this** (D-05, D-06). Recorded here as a rejected option so a later reader knows it was considered, NOT
  as a backlog candidate. Do not file it.

- **`test_configure_memory.cpp:9` cites `build_db.py:89` by line number.** `KNOWN_PROTOCOLS` actually
  lives at line 137. Same defect class as CLAIM-06 (which fixes a `build_db.py:594`→545 citation in the
  app repo), but in the firmware repo and outside this phase's four requirements. Not filed — flagged
  for whoever scopes the next citation sweep.

- **The three unadjudicated divergences** (D-16). Named in the verdict note as an open question with no
  tracker, by the operator's choice.

### Reviewed Todos (not folded)

`todo.match-phase 184` returned 35 matches, all scoring 0.4–0.6 on generic keyword overlap ("phase",
"test", "gsd", "plan"). None concern scan paths, dispatch, guard claims, or any CLAIM requirement — the
matcher has no semantic signal here. A targeted search for `scan_paths` / `dispatch_mirror` /
`ScanPathEntry` across `.planning/todos/` returned only two **completed** todos, both already consulted
(`migration-table-relocated-out-of-tools.md`, cited above). **Zero todos folded, deliberately.**

</deferred>

---

*Phase: 184-guards-that-exist*
*Context gathered: 2026-09-11*
