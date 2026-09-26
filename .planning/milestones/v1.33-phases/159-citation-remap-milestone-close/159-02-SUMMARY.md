---
phase: 159-citation-remap-milestone-close
plan: "02"
subsystem: infra
tags: [citation-remap, difflib, git-plumbing, whole-window-census, jsonl, gitlink-anchoring]

requires:
  - phase: 159-citation-remap-milestone-close
    provides: "159-01's hardened remap_citations.py engine: stable_record_id, LocationResolver, resolve_with_review, multi-anchor record_source_sha, BatchTransaction, build_index_stage_plan, --report-json"
provides:
  - "prepare_citation_remap.py: whole-window census (git diff --name-status between the manifest commit and the Phase-158 completion boundary), gitlink-at-authoring-commit historical anchoring, and measured (not assumed) review-population detection"
  - "159-late-citation-manifest.jsonl: 904 measured supplemental citation records (exact 642/127/184/225/106 four-phase-directory subtotal; >= the verified 881 lower bound)"
  - "159-remap-exceptions.jsonl: 515 status=needs_review records across four classifications, none approved"
  - "159-retarget-review.md: one evidence section per pending record/overlay row"
  - "159-corpus-overlay.json: the two live dirty/topology rows (COBS relocation, STATE.md) research found, both approval_status: pending"
  - "remap_citations.py additive extension: PENDING_REVIEW outcome / open_ids['needs_review'] / actionable_counts['needs_review'], so a tracked-but-undecided ledger entry is reported (report-json still written) instead of hard-blocking, while a genuinely undocumented actionable record still hard-blocks"
affects: [159-03, 159-04, 159-05, 159-06]

tech-stack:
  added: []
  patterns:
    - "Gitlink-at-authoring-commit anchoring: for each added/modified planning document, the meta repo's own git history (the commit that introduced/last-touched the citing file) names the exact firestarter/firestarter_app gitlink SHA live at that moment -- a historically justified source_sha with zero guessing, verified readable before being trusted, with the final head only as a same-precedence fallback (never a competing candidate that manufactures false ambiguity)"
    - "Reuse the production engine to MEASURE the review population: rather than re-deriving a second notion of 'does this citation survive', prepare_citation_remap.py runs the actual (non-strict) remap_citations.py over the merged original+late manifests plus the live corpus overlay and tracked-rename resolution, and harvests its own open_ids"
    - "Globally-unique-within-line citation ordinal: extract_spans()'s ordinal is match_index*1000 + element_index, not a per-match-reset counter, because the real corpus contains a line that cites the exact same target twice (REQUIREMENTS.md:15's eprom_params.cpp:61) which a per-match ordinal would silently collide"

key-files:
  created:
    - .planning/v1.33/tools/prepare_citation_remap.py
    - .planning/v1.33/tools/test_prepare_citation_remap.py
    - .planning/v1.33/159-late-citation-manifest.jsonl
    - .planning/v1.33/159-remap-exceptions.jsonl
    - .planning/v1.33/159-retarget-review.md
    - .planning/v1.33/159-corpus-overlay.json
  modified:
    - .planning/v1.33/tools/remap_citations.py
    - .planning/v1.33/tools/test_remap_citations.py

key-decisions:
  - "Two of this plan's own <acceptance_criteria>/<verify> numbers (exactly 5 known_post154_non_survivor, exactly 105 ordinary_original_non_survivor) are treated as FLOORS, not exact targets, once measured: running the real LineMap/build_map machinery against the actual repository found 18 and 268 respectively, both far above research's MEDIUM-confidence estimates. 159-RESEARCH.md itself states these two figures are provisional pending exactly this reconciliation ('Final review count: MEDIUM until the complete supplement/location ledger is built'), and the plan's own prose repeatedly frames them as 'known floor'/'minimum', not exact totals. Fabricating a manifest that stopped at 5/105 to satisfy a literal '==' in the verify script would mean silently dropping 276 genuine review-needed records from the ledger -- the opposite of REMAP-02's fail-closed contract. All downstream floor checks (>=5, >=105, >=110, >=881) hold with the honestly measured values."
  - "The 'v1.33 evidence records' count is measured as 88, not research's stated 77. The gap is exactly baseline-pre-sweep.md's 11 colon_list citations into firestarter_app test files, which research's prose total appears to have omitted; every other added-file bucket (154_post_manifest=125, 155-158=642 exactly) matches research precisely, corroborating the measurement method rather than a tool defect."
  - "remap_citations.py was extended beyond this plan's declared files_modified (Rule 1/3 deviation, documented below): Task 2's own <automated> verify script requires a --report-json shape (open_ids as a category-keyed dict with a 'needs_review' key, actionable_counts['needs_review'], totals.examined_records/examined_documents/planned_rewrites/planned_documents) and a control-flow property (the dry run must reach and WRITE the report before exiting 1, when every actionable outcome is tracked-but-pending) that the Plan-159-01 engine did not yet support. Extending the shared engine was the only way to satisfy Task 2's own verification contract without inventing a second, parallel remap tool."
  - "citation_paths.survey_candidates() (the Phase-154 provenance-hit candidate set) is unsuitable for resolving supplemental citations post-sweep: it now returns 75 files (down from the original manifest's 171) because the sweep itself removed most provenance comments. The preparer instead builds its CandidateIndex over build_citation_manifest._full_repo_paths() -- the whole current source tree -- exactly the index build_citation_manifest.py --stats already uses for its own reconciliation diagnostic."

requirements-completed: [REMAP-01, REMAP-02]

duration: not reliably measurable (extensive interactive verification against the live corpus; no wall-clock instrumentation)
completed: 2026-08-24
status: complete
---

# Phase 159 Plan 02: Whole-Window Census, Exception Ledger, Review Packet, and Corpus Overlay Summary

**Built a deterministic preparer that measures (never assumes) the complete bounded-window supplemental citation corpus and the full non-survivor review population by running the actual hardened remap engine against the live repository, exposing 904 supplemental records and 515 pending human-review rows -- both substantially larger than research's provisional estimates -- with zero approvals and zero corpus mutation.**

## Performance

- **Duration:** not reliably measurable (see frontmatter)
- **Tasks:** 2 completed
- **Files modified:** 8 (2 created + 2 extended for Task 1; 4 created for Task 2)

## Accomplishments

- **Whole-window census, measured exactly and honestly.** `prepare_citation_remap.py` scans `git diff --name-status -M50%` between the manifest commit (`9a78bc6d`) and the Phase-158 completion boundary (`048a0394`) under `.planning`, in-scope-filters (shared `SCAN_EXTENSIONS`/`SELF_EXCLUDE_PREFIXES` from `build_citation_manifest.py`), and classifies every added file by phase directory. The four-phase-directory subtotal reproduces research's exact figures: **642 = 127/184/225/106** across 155/156/157/158. Added-file classes: **125** post-manifest Phase-154 artifacts (exact match to research), **642** Phase-155-158 (exact), **88** v1.33 evidence records (measured; supersedes research's 77 -- see key-decisions). **49** genuinely new records surface inside the six pre-existing modified global documents (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, Phase-154 `deferred-items.md`, the read-timing todo) via `difflib.SequenceMatcher` positional reconciliation against the original manifest's own rows for each file. **Total: 904 records**, comfortably above the verified 881 lower bound, reported as a measured result rather than hard-coded at 881 or 642.
- **Gitlink-at-authoring-commit historical anchoring -- no guessing, no final-tree self-snapshot.** For every added file, the commit that introduced it (found via `git log --diff-filter=A` within the window) names the exact `firestarter`/`firestarter_app` gitlink SHA the meta repo pointed to at that moment (`git rev-parse <commit>:<submodule>`); for modified global documents, the last commit that touched the file in-window is used the same way. That anchor is tried FIRST and trusted directly the instant its blob reads successfully at the cited line -- proven NOT to manufacture false ambiguity even when the final head would read different text (a Phase-154 post-manifest SUMMARY describing pre-sweep code is *supposed* to disagree with final HEAD; that disagreement is exactly what the later remap resolves, not evidence of ambiguity). The final head is tried only as a same-precedence fallback when the primary anchor is unavailable or unreadable; when NEITHER anchor reads, the record degrades to a `source_sha_candidates` list (never silently dropped) and is routed to the exceptions ledger.
- **Review population measured by running the real engine, not re-derived.** `known_post154_non_survivors()` uses the exact `LineMap`/`build_map` machinery from `remap_citations.py` to check whether each of the 815 `retarget: true` rows' Phase-154 hand-chosen target still maps WITHOUT a clamp from its Phase-154 anchor commit (`2ad5b322`/`bc9d592`) to the real final tree -- measured: **18** genuinely do not (vs. research's provisional 5). `non_surviving_actionable_records()` runs the actual hardened `remap_citations.py` (subprocess, non-strict) over the ORIGINAL and newly-built LATE manifests merged together -- exactly the corpus the real Task-2 dry run sees -- with the live corpus overlay and tracked-rename resolution engaged, and harvests its own `open_ids` for every readable/resolved/`retarget:false` row landing in RETARGET, NOT_AT_RECORDED_LINE, or NO_MATCH_IN_DOCUMENT: measured **268** ordinary original-manifest non-survivors (vs. research's provisional 105) plus **225** supplemental non-survivors and **4** ambiguous historical anchors. **Total review floor: 515**, far above the known minimum of 110.
- **Deterministic, self-checking artifacts.** `159-late-citation-manifest.jsonl` and `159-remap-exceptions.jsonl` follow the same JSONL convention as the original manifest (one `_schema` header, compact fixed-key-order objects, LF, UTF-8, atomic write). `--check-existing` snapshots pre-existing output bytes and asserts the freshly-regenerated bytes are byte-identical; two independent runs over the same corpus were verified byte-for-byte identical for all four artifacts. A duplicate-`record_id` refusal was added and then genuinely EXERCISED: the real corpus contains one line (`REQUIREMENTS.md:15`) that cites `eprom_params.cpp:61` twice, which an ordinal reset per regex match would have silently collided onto one ID -- fixed by making the ordinal globally unique within its line (`match_index*1000 + element_index`) and covered by a dedicated hashing test plus a monkeypatched-collision integration test.
- **The production-shaped dry run now reaches "pending review" cleanly.** `python3 remap_citations.py /workspaces --manifest sweep-citation-manifest.jsonl --manifest 159-late-citation-manifest.jsonl --exceptions 159-remap-exceptions.jsonl --corpus-overlay 159-corpus-overlay.json --planning-base-sha 9a78bc6d ... --report-json ...` gets past the tracked pending->completed todo rename AND the untracked COBS relocation (via the corpus overlay), examines 14,417 records across 1,291 documents and 220 target files, and exits 1 **solely** because `open_ids["needs_review"]` is nonempty (496 pending): every other actionable class (`retarget`, `not_at_recorded_line`, `no_match_in_document`, `unreviewed_retarget`, `violation`) is exactly zero, and `examined_records`/`examined_documents`/`planned_rewrites`/`planned_documents` are all nonzero. This demonstrates the raw renamed-document/untracked-relocation blockers are genuinely reconciled, not merely notes.
- **Original manifest untouched.** `sweep-citation-manifest.jsonl` SHA-256 remains `ecdd0fc84be1627f893e30f6369c0b9eedf2a69ce3ec351064828d82e72d992e` (13,693 physical lines) throughout every run, verified both by the preparer's own self-check and independently after every commit.
- **All 102 tests pass** (19 new in `test_prepare_citation_remap.py`, 4 new + 1 updated in `test_remap_citations.py`, 26 unchanged in `test_build_citation_manifest.py`, 53 unchanged pre-existing in `test_remap_citations.py`).

## Task Commits

1. **Task 1: Implement and test the whole-window historical preparer** - `a6bd6c69` (feat) -- also carries the additive `remap_citations.py`/`test_remap_citations.py` extension (deviation, see below)
2. **Task 2: Materialize the dynamic supplemental corpus, ledger, review packet, and live overlay inventory** - `78198190` (docs)

## Files Created/Modified

- `.planning/v1.33/tools/prepare_citation_remap.py` (new) - Whole-window census, gitlink-at-authoring anchoring, review-population measurement, deterministic JSONL/Markdown writers.
- `.planning/v1.33/tools/test_prepare_citation_remap.py` (new) - 19 tests: extraction/classification units, anchor precedence/fallback, non-survivor detection, duplicate-ID refusal, final-tree-oracle rejection, end-to-end determinism on a synthetic multi-repo corpus, coverage-gate anti-vacuity.
- `.planning/v1.33/tools/remap_citations.py` (extended) - Additive `PENDING_REVIEW` outcome, category-keyed `open_ids`, `actionable_counts["needs_review"]`, `totals` aliases, pending corpus-overlay authorization surfacing, `--apply` refusal while any decision is pending.
- `.planning/v1.33/tools/test_remap_citations.py` (extended) - 4 new tests for the pending-review mechanism; 1 existing test's `open_ids` assertion updated to the new dict shape.
- `.planning/v1.33/159-late-citation-manifest.jsonl` (new) - 904 measured supplemental records.
- `.planning/v1.33/159-remap-exceptions.jsonl` (new) - 515 `status: needs_review` records across 4 classifications.
- `.planning/v1.33/159-retarget-review.md` (new) - Evidence packet, one section per pending record/overlay.
- `.planning/v1.33/159-corpus-overlay.json` (new) - 2 pending dirty/topology rows (COBS relocation, STATE.md).

## Decisions Made

See `key-decisions` in frontmatter. Most consequential: research's two exact non-survivor figures (5, 105) are honored as FLOORS, not literal targets, because measuring them for real against the actual repository (rather than research's earlier sampling) finds substantially larger true populations (18, 268) -- and silently truncating the ledger to match a stale estimate would violate REMAP-02's fail-closed contract far more than a documented, evidence-backed deviation does.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1/3 - Blocking + engine gap] Extended `remap_citations.py`'s `--report-json` to support tracked-but-pending review**
- **Found during:** Task 2, running the exact `<automated>` dry-run command
- **Issue:** The verify script requires `report['open_ids']['needs_review']` (a dict), `report['actionable_counts']['needs_review']`, and `report['totals']['examined_records'/'examined_documents'/'planned_rewrites'/'planned_documents']` -- none of which existed after Plan 159-01. Worse, the Plan-159-01 engine's `_associate()` puts ANY strict-mode mismatch (including one covered by a `needs_review` ledger row) into the hard `violations` list, which exits 1 BEFORE `--report-json` is written -- so a fully-populated ledger would make the dry run fail with no report at all, contradicting the plan's own required outcome ("gets past the tracked rename and exits 1 solely for the exact review/authorization set").
- **Fix:** Added an additive `PENDING_REVIEW` outcome: an actionable record (RETARGET/NOT_AT_RECORDED_LINE/NO_MATCH_IN_DOCUMENT) whose stable ID has ANY exceptions-ledger entry (even `status: needs_review`, not yet `reviewed`) is now reported softly under `open_ids["needs_review"]`/`actionable_counts["needs_review"]` and does NOT enter the hard `violations` list; a record with NO ledger entry at all still hard-blocks exactly as before (fail-closed default preserved). `open_ids` changed from a flat list to a category-keyed dict (all pre-existing categories retained; the one Plan-159-01 test asserting the old shape was updated). Pending corpus-overlay rows (`dirty_overlap: true`, `approval_status` not `authorize_include`/`approved`) also surface into `needs_review`. `--apply` now refuses (exit 1, nothing written) while `needs_review` is nonzero.
- **Files modified:** `.planning/v1.33/tools/remap_citations.py`, `.planning/v1.33/tools/test_remap_citations.py`
- **Verification:** All 53 pre-existing tests pass unchanged in behavior (only the one shape-dependent assertion updated); 4 new tests cover the pending-vs-undocumented distinction, the corpus-overlay surfacing, and the `--apply` refusal; the exact production dry run over the real corpus was manually re-verified to still reproduce its raw diagnostic numbers unchanged when `--exceptions` is absent.
- **Committed in:** `a6bd6c69` (Task 1 commit)

**2. [Rule 1 - Bug] Citation ordinal collision on a line citing the same target twice**
- **Found during:** Task 2, first real-corpus run of the preparer (hard duplicate-`record_id` refusal fired on `.planning/REQUIREMENTS.md:15`)
- **Issue:** `extract_spans()`'s per-span ordinal reset to 0 for every regex match on a line; `REQUIREMENTS.md:15` genuinely cites `eprom_params.cpp:61` twice (once inline, once in a parenthetical list), producing two records with identical `(planning_file, planning_line, variant, target_file_cited, target_line, target_line_end)` and therefore the same minted `record_id` -- silently conflating two distinct citation occurrences.
- **Fix:** Made the ordinal globally unique within its line (`match_index * 1000 + element_index`) and included `citation_ordinal` in `mint_record_id`'s hash basis.
- **Files modified:** `.planning/v1.33/tools/prepare_citation_remap.py`
- **Verification:** A dedicated duplicate-ID-refusal test (monkeypatched collision) plus a deterministic-ID unit test; the real corpus run now completes without a duplicate-ID refusal and the two `eprom_params.cpp:61` occurrences on `REQUIREMENTS.md:15` are present as two distinct ledger-eligible records.
- **Committed in:** `a6bd6c69` (Task 1 commit, discovered before Task 2's artifacts were finalized)

---

**Total deviations:** 2 auto-fixed (1 Rule 1/3 blocking engine gap, 1 Rule 1 bug)
**Impact on plan:** Both were necessary for Task 2's own verify script to be satisfiable at all and for the ledger to be correct; no scope creep beyond what REMAP-01/02's fail-closed contract already required.

## Issues Encountered

- `citation_paths.survey_candidates()` (the Phase-154 provenance-hit candidate set) returns 75 files post-sweep, not the original manifest's 171, because the sweep itself removed most provenance comments -- using it here would have misclassified hundreds of legitimately-resolvable Phase 155-158 citations as `unresolved`. Resolved by building the preparer's `CandidateIndex` over `build_citation_manifest._full_repo_paths()` (the whole current source tree) instead, matching what `build_citation_manifest.py --stats` already uses for its own diagnostic.
- Multiple `anchor_record()` design iterations were needed: an early version that treated the gitlink anchor and the final head as CO-EQUAL candidates (picking one only when they agreed) manufactured 385 false "ambiguous" rows out of legitimate Phase-154-era before/after disagreement; switching to strict precedence (gitlink first, final head only as an unavailability fallback) reduced this to 4 genuine ambiguities.
- The non-survivor census initially ran the diagnostic engine against the ORIGINAL manifest alone, missing IDs whose match/mismatch dynamics only change once the LATE manifest's records join the same citation group; fixed by writing the late manifest first (provisionally) and running the diagnostic against BOTH manifests merged, exactly matching what the real Task-2 dry run does.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 159-03 has a complete, evidence-backed `159-remap-exceptions.jsonl` (515 pending rows) and `159-retarget-review.md` to run its human review checkpoint against -- every row's `status` is `needs_review` and every `chosen_*` field is `null`; nothing has been pre-decided.
- Plan 159-03/04 still needs to resolve the two pending `159-corpus-overlay.json` rows (`auth-cobs-relocation`, `auth-state-md-dirty`) -- both remain `approval_status: pending`; this plan performed no staging or inclusion of either.
- The whole-window supplemental manifest (`159-late-citation-manifest.jsonl`, 904 records) and the hardened `remap_citations.py` (now with pending-review reporting) are ready for Plan 159-04's rehearsal and Plan 159-05's single production apply, once Plan 159-03's review resolves the 515 pending records.
- `.planning/v1.33/CITATIONS-STALE.md` remains present, as required until Plan 159-06's close gate.
- `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` were not written by this plan (byte-identical to their pre-existing dirty state); the pre-existing dirty/untracked baseline (STATE.md, config.json, the six 159-0N-PLAN.md files, 159-RESEARCH.md, 159-VALIDATION.md, the COBS relocation delete+untracked-add, package.json/package-lock.json) is unchanged.

---
*Phase: 159-citation-remap-milestone-close*
*Completed: 2026-08-24*

## Self-Check: PASSED
