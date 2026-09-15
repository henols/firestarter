---
phase: 159-citation-remap-milestone-close
plan: "05"
title: Sole Production Citation Remap -- Authoritative Apply Record
status: APPLIED
production_apply_events: 1
event_id: 04390458f8ee4776bd75c2656a62a809
generated: 2026-08-24
citations_stale_marker: "PRESENT -- Plan 159-06 close-blocks on removal"
milestone_completion_claimed: false
---

# Phase 159 Plan 05: Sole Production Citation Remap -- Authoritative Record

This is the measured, authoritative evidence record for the ONE authorized
production citation-remap transaction. Every number below was captured from
the real `/workspaces` corpus, not a rehearsal or disposable copy, except
where explicitly labeled disposable. This record does not claim milestone
completion; `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md` remains present and
Plan 159-06 owns its removal.

## Blocker clearance (prerequisite to this apply)

Two general engine fixes were required and proven before this apply ran
(committed separately: `a2b2795f`):

1. **`recordscan:supersedes` line protection** (operator ruling in
   `159-05-PLAN.md`). `remap_citations.py` now parses `recordscan:supersedes`
   markers directly from each citing document and treats any citation on a
   protected line as a terminal RETIRED no-op
   (`retire_cause=deliberately_superseded_record`), independent of the
   closed `159-remap-exceptions.jsonl` ledger. Measured: exactly 2 records
   excluded, both in `.planning/notes/py32f071-port-branch-state.md`
   (line 94, needle `hex-extension-hardcoded`; line 96, needle
   `cli-handlers-821`).
2. **Gitignored citing-document exclusion** (discovered during this task's
   own preflight index-plan validation, not a 159-03 checkpoint item): 2
   `requires_authorization` index entries had no corpus-overlay row --
   `.planning/graphs/graph.json` and `.planning/graphs/.last-build-snapshot
   .json`, both `.gitignore`d regenerable graphify build caches (~23 MB
   each). `remap_citations.py` now excludes any `git check-ignore`-matched
   citing document from remap entirely (terminal RETIRED,
   `retire_cause=citing_document_is_gitignored_generated_artifact`, 203
   records). Both fixes are general, marker/predicate-driven rules, each
   covered by new regression tests (`test_remap_citations.py`).

## Inputs (frozen, verified unchanged from `159-rehearsal-record.json`)

| Input | Value |
|---|---|
| Original manifest sha256 | `ecdd0fc84be1627f893e30f6369c0b9eedf2a69ce3ec351064828d82e72d992e` (13693 lines) |
| Late/supplemental manifest sha256 | `307d74355cc332680050bb34f739abce69b89782384175d50c9b68787b16fd01` (904 records: 855 added, 49 modified_global; 127/184/225/106 = 642 across phases 155-158) |
| Exceptions ledger sha256 | `0362b94e8edee833702240387742960116219b899b854ee845b28a87415973f1` (515 records: 339 reviewed, 176 retired; 0 needs_review) |
| Corpus overlay sha256 | `ba50c1a2e9d07f9e863a7f8861d26ee37abf5e915b2c3f6c6898fd89d49a3794` (2/2 approved) |
| firestarter HEAD | `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` (tracked worktree+index clean) |
| firestarter_app HEAD | `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2` (tracked worktree+index clean) |
| corpus_fingerprint | `95c5f522872da2e774008104b32974acc5df5cc8cd7306804715c65611333fed` (matches rehearsal exactly) |
| topology_digest | `0d7c095d109f37dba5f3375a7644153ade4abe4e5f5862eb64b91ed85d56932e` (matches rehearsal exactly) |

Review-count floors (159-03 key-decisions state these are FLOORS, not exact
targets -- same correction 159-04-SUMMARY.md deviation #1 already applied):
measured `known_post154_non_survivor=18` (floor 5), `ordinary_original_non_survivor=267`
(floor 105), both comfortably above floor.

## The sole production apply command

```
python3 .planning/milestones/v1.33-artifacts/tools/remap_citations.py /workspaces \
  --manifest .planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl \
  --manifest .planning/milestones/v1.33-artifacts/159-late-citation-manifest.jsonl \
  --exceptions .planning/milestones/v1.33-artifacts/159-remap-exceptions.jsonl \
  --corpus-overlay .planning/milestones/v1.33-artifacts/159-corpus-overlay.json \
  --planning-base-sha 9a78bc6dc8b31087265f13c684ae850223806772 \
  --pre-sweep-sha firestarter=8695ee52c27a4bee4387c5c489afd5f3d7275e8a \
  --pre-sweep-sha firestarter_app=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a \
  --report-json /tmp/gsd-159-production-apply-report.json \
  --index-plan /tmp/gsd-159-production-index-confirm.json \
  --production-receipt .planning/milestones/v1.33-artifacts/159-production-apply.json \
  --recovery-bundle .planning/milestones/v1.33-artifacts/159-production-recovery.tar \
  --apply --quiet-notes
```

Ran exactly once. Exit 0. Output:

```
PASS [APPLIED]: 14391 record(s) examined across 1291 document(s) and 220 target
file(s); 2706 rewritten, 7277 already at their fixed point, 783 flagged
retarget, 0 not at their recorded line, 3446 skipped as unreadable, 0
unmatched in their document, 381 retired (no rewrite target), 0 pending
human review (needs_review); 9 record(s) legitimately cite a planted
fixture by name; 562 document(s) changed.
```

### Receipt (`159-production-apply.json`)

- `status`: `APPLIED`
- `production_apply_events`: `1`
- `event_id`: `04390458f8ee4776bd75c2656a62a809`
- `failure`: `null`
- `rollback_status`: `null` (never needed -- no failure occurred)
- `planned_documents` / `replaced_documents`: 562 each
- `preimage_hashes[".planning/STATE.md"]`: `e866ab7ad7840e69931b4af62709c33ce9e5a69537c6c5abd24eda14bba8d71f`
- `recovery_bundle_sha256`: `da07262fbc99276397e7849bb29570dd766eee531fb679a41d173344d9b8fa1a`

No failure path was exercised on the real production apply (it succeeded
on the first and only attempt). Failure/recovery semantics were already
proven against the exact approved live corpus by the disposable rehearsal
(`159-rehearsal-record.json`'s `recovery` section, and re-confirmed by this
task's own re-run of that rehearsal after the blocker fixes -- see below).

### Totals

| Metric | Count |
|---|---|
| Records examined | 14391 |
| Rewritten | 2706 |
| Already at fixed point | 7277 |
| Flagged retarget (D-08 hand-chosen, left as written) | 783 |
| Not at recorded line | 0 |
| Skipped as unreadable | 3446 |
| Unmatched in document | 0 |
| Retired (no rewrite target) | 381 |
| Duplicate shared member | 3 |
| Documents changed | 562 |
| Actionable/open (retarget/not_at_recorded_line/no_match/unreviewed_retarget/violation/needs_review) | 0 (all) |

### Retired, by cause (381 total)

| retire_cause | Count |
|---|---|
| `citation_absent_from_citing_document` | 149 |
| `citing_document_is_gitignored_generated_artifact` | 203 |
| `could_not_be_relocated` | 12 |
| `target_file_never_resolved` | 9 |
| `citation_already_correct_verbatim_survivor` | 2 |
| `deliberately_superseded_record` | 2 |
| `moved_with_semantic_change` | 1 |
| `ambiguous_generic_text` | 1 |
| `citing_document_line_drifted` | 1 |
| `collapse_would_corrupt_adjacent_citation_grammar` | 1 |
| **Total** | **381** |

The 176 ledger-approved retirements plus 2 new `deliberately_superseded_
record` plus 203 new `citing_document_is_gitignored_generated_artifact`
account for all 381 (176 + 2 + 203 = 381).

## Second dry run (idempotency / no-op proof)

Ran the identical transaction, no `--apply`/`--production-receipt`/
`--recovery-bundle`, fresh `--report-json` (`/tmp/gsd-159-post-apply-dry.json`):

```
PASS [DRY RUN (no bytes written; pass --apply)]: 14391 record(s) examined
across 1291 document(s) and 220 target file(s); 0 rewritten, 9983 already
at their fixed point, 783 flagged retarget, 0 not at their recorded line,
3446 skipped as unreadable, 0 unmatched in their document, 381 retired (no
rewrite target), 0 pending human review (needs_review); 9 record(s)
legitimately cite a planted fixture by name; 0 document(s) would change.
```

- Exit 0. `planned_rewrites: 0`, `planned_documents: 0`.
- `actionable_counts`: all zero. `open_ids`: all empty.
- `corpus_fingerprint`: `95c5f522872da2e774008104b32974acc5df5cc8cd7306804715c65611333fed` (unchanged)
- `topology_digest`: `0d7c095d109f37dba5f3375a7644153ade4abe4e5f5862eb64b91ed85d56932e` (unchanged)

**Note on `.planning/STATE.md` at the moment of this second dry run:** its
disk content was temporarily set to the verified postimage
(`61fb2b610c1aa958b7795eafbe741cfdf04e12be464f8b003a1e27763a3daff0`) so
this proof covers the true post-apply corpus, matching every other
affected document's disk state at the same moment. STATE.md's disk bytes
were restored to the preserved dirty preimage
(`e866ab7ad7840e69931b4af62709c33ce9e5a69537c6c5abd24eda14bba8d71f`)
**after** the commit below (see "Dirty-overlap disposition"), per the
`preserve_unstaged`/index-object-surgery design: only a citation-only INDEX
OBJECT is ever staged for STATE.md; its working-tree bytes must read
exactly as they did before this plan ran, for the remainder of the phase.
The postimage used here was independently re-derived via a disposable
corpus materialization (`rehearse_citation_remap.materialize_live_corpus`
+ `run_remap` with `--apply`, on a throwaway copy) and measured
byte-identical (same sha256) to what the real production `--apply` wrote
to disk in the first place -- not re-invented, re-verified.

## Range proof (ROADMAP criterion 3, real diff)

`json_parser.c` old lines **128-131** (span 4) -> new lines **316-318**
(span 3), confirmed for all 10 citing records sharing this coordinate
(`orig-fe6697dd74c7a30b`, `orig-78190232a530ea0a`, `orig-d302cd3887f7ca18`,
`orig-8fe8be47b348e764`, `orig-8d5383d6307fd3db`, `orig-73b390e3a8c6c728`,
`orig-5d167cda4397a22d`, `orig-08006b0a00fb71ce`, `orig-75d346d157867dbd`,
`orig-1060058b80d1edee`). Exact endpoints, shrunk not translated.

## Archive gate (Phase 130 `check_record_corrections.py`)

| Run | Result |
|---|---|
| Before this apply (pre-existing live state) | `PASS`, exit 0, `superseded: 12` |
| After this apply (real corpus, this task) | `PASS`, exit 0, `superseded: 12` |
| Disposable rehearsal re-run post-blocker-fix (this task, before the real apply) | `PASS`/`PASS`, `superseded: 12`/`12`, `superseded_unchanged: true` |

The pre-blocker-fix rehearsal recorded in `159-rehearsal-record.json`
measured a `12 -> 11` drift (the `cli-handlers-821` needle no longer
matching after remap renumbered `notes/py32f071-port-branch-state.md:96`
from `:821` to `:819`). The `recordscan:supersedes` exclusion fix in this
plan makes that drift impossible by construction: both the disposable
rehearsal and the real production apply now measure `12/12` stable. This
supersedes (in the plain English sense) the `159-04-SUMMARY.md` "Issues
Encountered" note about the 12->11 drift -- that finding is resolved, not
merely explained.

## Dirty-overlap authorization table

| Authorization ID | Path | Decision | Staging strategy | Disposition |
|---|---|---|---|---|
| `auth-cobs-relocation` | `.planning/milestones/v1.33-artifacts/v1.9-COBS-DECISION.md` (relocated from `.planning/v1.9-COBS-DECISION.md`) | `authorize_include` | `authorized_include` | Full relocation (delete old tracked path, add new path) staged; content legitimately rewritten by this same remap pass (4 ordinary citations); `expected_postapply_sha256` `f1b0e540855bc9d13705505c43d0108ed157169dce24eb10b83dac4b6291d3a4` measured exactly, matching the corrected 159-04 overlay value |
| `auth-state-md-dirty` | `.planning/STATE.md` | `preserve_unstaged` | `citation_only_blob` | Index object staged from committed base (`b118a33976762d9e9808b6a3ab02bfde226b52e2`) plus citation edits only (`351d77746e348bbb6ae5efed528ac8e0743be3a7`, predicted content sha256 `bb80d52cbbec9991689bb45d2745fe4009319d2c0fc67735975670e41d366bb1`); working-tree bytes restored to the preserved dirty preimage `e866ab7ad7840e69931b4af62709c33ce9e5a69537c6c5abd24eda14bba8d71f` after commit |

## Index staging proof

`159-index-stage-plan.json` (frozen at Task 1, re-validated unchanged at
Task 2): 562 documents -- 561 `citation_only_blob` (clean tracked paths,
index object equals the predicted postimage exactly) + 1
`authorized_include` (the COBS relocation, scope exactly one relocation).
Zero `preexisting_index_paths`. The real git index held zero staged paths
immediately before staging began (verified both at Task 1 freeze and
immediately before staging in Task 2).

## `.planning/v1.9-COBS-DECISION.md` gitlinks / source repos / app-untracked inventory

Unchanged from the Task 1 freeze: `firestarter` gitlink drift
(`2ad5b322a37ba4a88afd09cc946f5c4114e51483` committed vs
`2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` current HEAD) is pre-existing
per `158-07-SUMMARY.md` and never staged. `firestarter_app`'s 7 pre-existing
untracked files (`.planning/config.json`, `SECURITY.md`, 4 datasheet PDFs,
`write_test_port.sh`) are untouched. Neither gitlink is staged in the meta
index.

## Note for Plan 159-06: the post-restore dry-run shape (STATE.md is a permanent, expected exception)

After the post-commit restore of `.planning/STATE.md` to its preserved dirty
preimage (above), a **fresh** dry run over the live corpus reports:

```
1 rewritten ... 1 document(s) would change
```

with `affected_documents: [".planning/STATE.md"]` and **all** actionable /
open counts still zero. This is the disk-based (not staged-content-based)
view: `remap_document()` has no concept of `preserve_unstaged` -- it only
ever reads the file's current disk bytes and compares against its own
target-file citation oracle. Since STATE.md's disk bytes are, by design,
permanently pinned at the pre-existing dirty preimage rather than the
citation-fixed postimage, a disk-only dry run will **always** report this
same "1 rewritten, 1 document" residual, forever, for as long as
`auth-state-md-dirty`'s `preserve_unstaged` decision holds -- it is not a
transient artifact of this task's own sequencing, and it is not a defect.

The true, corpus-wide, byte-stable fixed-point proof (the "second dry run"
section above, `0 rewritten / 0 documents`) was captured **before** this
restore, with STATE.md's disk bytes still holding the verified real
postimage (`61fb2b61...`) -- proving the remap LOGIC itself has reached a
true fixed point across the entire real corpus. The residual "1 document"
a post-restore dry run reports is solely a reflection of the deliberate
`preserve_unstaged` gap between STATE.md's disk bytes (`e866ab7a...`,
frozen) and its committed citation-only blob (`351d777...`) -- a gap that
is proven correct separately, by exact blob/content-hash comparison against
`159-index-stage-plan.json`'s prediction (done above), not by a disk-level
dry run.

**Actionable guidance for 159-06's own "dry no-op still 0/0" gate:** run the
same dry command and treat a residual limited to exactly `affected_documents
== [".planning/STATE.md"]` with `planned_rewrites <= 1` and all
actionable/open counts zero as the expected, permanent PASS shape -- not a
regression. A dry run reporting any OTHER document, or any nonzero
actionable/open count, would be a genuine regression.

## Marker state

`.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md`: **PRESENT** -- Plan 159-06 close-blocks
on its removal. This plan makes no milestone-completion claim.

## Scoped closure readiness and final marker transition (Plan 159-06)

This section is append-only: no production fact recorded above is rewritten.

**Readiness commands re-run, all green** (frozen in
`.planning/milestones/v1.33-artifacts/159-close-readiness.json`, `status: READY_TO_REMOVE_MARKER`):

- `pytest -q test_remap_citations.py test_prepare_citation_remap.py
  test_rehearse_citation_remap.py` -- 98/98 passing.
- The production-shaped dry run against the real corpus -- disk-based
  residual limited to exactly `affected_documents == [".planning/STATE.md"]`,
  1 rewritten / 1 document, all actionable/open counts zero -- the expected,
  permanent `preserve_unstaged` shape this record's own prior section
  predicted for this exact gate, confirmed not a regression.
- Phase 130's archive gate (`check_record_corrections.py`) -- `PASS`,
  `superseded: 12`, unchanged.
- `firestarter` HEAD `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` and
  `firestarter_app` HEAD `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2` both match
  the production receipt's recorded source heads; both worktrees clean; the
  app repo's 7 pre-existing untracked entries still `??`.
- The real meta git index held zero staged paths immediately before this
  plan's own staging began.

**Scoped-diff expectations, verified against `git diff --stat`:** exactly
two hand-authored files touched by this closure --
`.planning/REQUIREMENTS.md` (five REMAP checkboxes ticked, five discharge
sentences appended, five traceability rows changed to `Complete`, line count
unchanged at 158, bullet count unchanged at 43) and `.planning/ROADMAP.md`
(six Phase-159 plan checkboxes ticked, measured-fact sentences appended to
the five existing Success Criteria, Goal/Depends on/Requirements lines
byte-identical, line count unchanged at 4593, `### Phase ` heading count
unchanged at 100) -- plus this record's own append and the marker's final
deletion. Both files' post-edit sha256 match the digests frozen in
`159-close-readiness.json`'s `replacement_payload_sha256`
(`00bcd91e...9ea4f` / `f570c6d1...a7f2684`) exactly.

**Preserved-dirty hashes, re-verified unchanged from the Plan-05 baseline**
(all 13 paths in `159-close-readiness.json`'s `preserved_dirty_hashes`,
`.planning/STATE.md` foremost at `e866ab7a...bba71f`): identical before and
after this plan's own edits. None of these paths were staged.

**Marker-present precondition:** `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md`
(sha256 `405d2477...becc0`) was read last, immediately before deletion, and
was present for every gate re-run above. Its deletion is this plan's final
implementation-file mutation; no file edit or generator run follows it.

**SWEEP-13 note:** its one-meta-commit clause remains exactly as
154-12/159-01..05 left it -- intentionally open, unticked, and not
rewritten by this closure. This plan adds its own commit under
`.planning/milestones/v1.33-artifacts` on top of that already-recorded count; the honest
count is not re-derived or asserted to have changed shape.

**No archive, release, push, PR, merge, or milestone-completion action
occurred in this plan.** v1.33 is not described as archived, released,
shipped, or completed anywhere in this closure.

**Next action:** `/gsd-complete-milestone` -- a separate, operator-gated
workflow. This record and `159-close-readiness.json` are its inputs, not
its execution.
