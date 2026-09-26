# Phase 159: Citation Remap + Milestone Close - Research

**Researched:** 2026-08-24 (forced refresh against the live Phase-159 execution tree)
**Domain:** Git-anchored source-line citation migration over a multi-repository composite diff
**Confidence:** HIGH for current commands, Git objects, tool behavior, and measured inventories; MEDIUM for the final supplemental/review cardinalities until the hardened reconciler materializes them

<phase_requirements>
## Phase Requirements

| ID | What planning must guarantee | Verified planning implication |
|---|---|---|
| REMAP-01 | One production apply over the composite pre-154-to-post-158 source diff | Preserve the 13,692-row Phase-154 manifest, add every citation record authored during the bounded window (not only the 642 in four phase directories), rehearse the exact production corpus, and issue one production `--apply` command guarded by a receipt and a recovery record. |
| REMAP-02 | Recorded source text equals destination text after remap | Keep the existing destination-text oracle, extend it to per-record historical anchors and reviewed targets, and make unmatched, ambiguous-location, ordinary dynamic-retarget, unreviewed-retarget, missing-target, and oracle outcomes blocking before writes. |
| REMAP-03 | Both range endpoints map and a real deleted-block range shrinks | Retain independent endpoint mapping and commit the real `json_parser.c:128-131 -> 316-318` assertion: span 4 becomes 3 and both endpoint texts match. |
| REMAP-04 | The Phase-154 staleness marker is absent at close | Keep `.planning/v1.33/CITATIONS-STALE.md` until every production/no-op/range/archive/closure gate passes; delete it as the last implementation-file mutation and require `test ! -e`. |
| REMAP-05 | Run two is a real-corpus no-op | After the sole production apply, invoke the transaction without `--apply`, require zero rewrites/documents/actionable exceptions, and byte-compare the complete affected corpus. Do not demonstrate this with a second production apply. |

</phase_requirements>

## Executive Answer

Phase 159 needs a hardened migration and a wider inventory before the one-shot apply is safe. The existing remapper has the correct core primitives—Git old blobs, `SequenceMatcher(..., autojunk=False)`, independent range endpoints, positional association, fixed-point-first decisions, pre-write oracle checks, all-document planning, and per-file atomic replacement—but the current CLI is neither corpus-complete nor fail-closed enough for REMAP-01/02/05.

The live raw dry run does not produce the previously quoted corpus report. It exits 1 immediately because the original manifest names the tracked path `.planning/todos/pending/2026-08-22-sweep-gsd-provenance-comments-from-firmware-and-host-source.md`, renamed at meta commit `25651cbc` to `todos/completed/`. In a disposable corpus with that tracked rename and the current uncommitted COBS-document relocation restored to their recorded paths, the prior diagnostic reproduces exactly:

```text
PASS [DRY RUN ...]: 13536 record(s) examined across 1228 document(s)
and 128 target file(s); 2238 rewritten, 6908 fixed point,
904 flagged retarget, 0 not at recorded line, 3486 unreadable,
156 unmatched; 508 document(s) would change.
```

That diagnostic is evidence of gaps, not readiness. The tool exits 0 with 156 unmatched records and 904 flagged outcomes. More importantly, the review population in the existing research/plans is too small: the 904 consists of Phase-154 flagged rows that successfully associated plus **103 ordinary original rows newly classified as dynamic retargets**. A direct map audit finds **105** ordinary readable original rows whose endpoint no longer survives the full composite diff; two more are currently hidden inside unmatched duplicate citation groups in REQUIREMENTS/ROADMAP. All 105 must be reconciled. Combined with the five Phase-154 hand choices whose selected post-154 text disappeared again, the known review floor is **110 stable records before any supplemental-record or location/anchor ambiguity is counted**, not five.

The fixed 642-row supplemental plan is also incomplete for the bounded staleness window. The shared grammar does reproduce exactly 127/184/225/106 = 642 records under the four Phase 155-158 directories, but those directories are only a subset of planning records written after the manifest. Against the manifest commit `9a78bc6d` through the Phase-158 completion/evolution commit `048a0394`, newly added non-tool planning files absent from the original manifest contain **844 grammar records**: 125 in post-manifest Phase-154 artifacts, 642 in Phase 155-158 directories, and 77 in `.planning/v1.33/` records. Six pre-existing global documents modified in the same window have a net **+37** records, so the complete post-manifest population is at least **881** before historical positional reconciliation determines the exact total. The preparer must census the whole temporal planning delta and classify every row; 642 remains a verified subset, not the supplemental manifest's final cardinality.

**Primary recommendation:** retain the six sequential waves, but correct Plans 159-01 through 159-05 before execution. Harden one engine, reconcile the entire window, review a dynamically measured set with a current known floor of 110, rehearse the exact live corpus including approved dirty overlays, protect unrelated user changes at staging time, then run one production apply and a dry byte-no-op proof. Delete the marker only afterward.

## Findings Changed by This Forced Refresh

1. **Review floor corrected from five to 110.** The verified 717/93/5 partition covers only the 815 Phase-154 hand choices. Separately, 105 ordinary readable original-manifest records now have non-surviving endpoints under the composite diff (103 currently emitted as dynamic retarget; two masked by unmatched groups). Plans 159-02/03 currently omit this entire class from `review_ids`.
2. **The 642 late-row count is a subset, not full window coverage.** It is exact for the four Phase 155-158 directories. It omits 125 records in post-manifest Phase-154 artifacts, 77 in added non-tool v1.33 records, and new occurrences in modified PROJECT/REQUIREMENTS/ROADMAP/STATE/deferred-item/todo documents (net +37 records).
3. **A viable pytest interpreter already exists outside the checked-in app venvs.** Bare `python3 -m pytest` fails (`No module named pytest`), and both checked-in app interpreter symlinks are broken, but `/usr/local/py-utils/venvs/pytest/bin/python -m pytest` and `/usr/local/py-utils/bin/pytest` run pytest 9.1.1 on Python 3.12.13. The current suite result is 20 passed / 1 failed.
4. **The one legacy failure now names two unrelated planning changes.** `test_the_tool_is_not_applied_to_any_real_planning_document` rejects both `.planning/STATE.md` and the deleted old path `.planning/v1.9-COBS-DECISION.md`, not STATE alone. The new untracked copy at `.planning/v1.33/v1.9-COBS-DECISION.md` is byte-identical to the HEAD version and carries four original-manifest records.
5. **The existing raw dry-run statement remains false as a current command result.** The committed CLI stops on the tracked pending-to-completed todo rename. The 2238/6908/904/3486/156/508 figures are now directly reproduced, but only in a disposable location-restored diagnostic.
6. **The original app old-side SHA is conclusively `6bfa6453`, despite the Phase-154 handoff text.** The location-restored diagnostic is oracle-clean with `6bfa6453`; using `bc9d592` yields 787 oracle violations. `bc9d592` remains valid only as the base for advancing Phase-154 hand-retarget choices.
7. **Whole-run atomicity was overstated.** The tool validates every document before writing and each `atomic_write` is atomic for one file, but the sequence of hundreds of replacements is not a cross-document filesystem transaction. A mid-write I/O/process failure can leave a partial corpus. The production receipt prevents replay; it does not itself provide rollback or completion recovery.
8. **The real REMAP-03 case remains exact.** Pre-sweep `json_parser.c:128-131` maps to final `:316-318`; the old indirect load/call collapses to one `store_field` call while the two endpoint lines survive verbatim.

## Verified Current State

### Repositories and anchors

| Purpose | Repository / value | Verified state |
|---|---|---|
| Meta HEAD | `/workspaces` `4a6616b77a290f677de781a19e8f2a7c54d91ceb` | Branch `gsd/v1.33-source-hygiene-firmware-size-reduction`; dirty working tree. |
| Manifest planning base | meta `9a78bc6dc8b31087265f13c684ae850223806772` | Exists; commit that added the original manifest/report. |
| Phase-158 planning cutoff | meta `048a0394` | Phase-158 completion/evolution point; use a full history audit to pin the exact cutoff in the preparer. |
| Firmware original old side | `8695ee52c27a4bee4387c5c489afd5f3d7275e8a` | Exists; original homogeneous-manifest anchor. |
| Firmware Phase-154 retarget base | `2ad5b322a37ba4a88afd09cc946f5c4114e51483` | Exists; Phase-154 swept firmware commit. |
| Firmware phase boundaries | `adf1a312` (155), `1151dc497` (156), `785e644b` (157), `2ccda8d43` (158/final) | Exist; useful candidate anchors, but per-artifact evidence must choose the actual authoring state. |
| Firmware final HEAD | `2ccda8d43c8161a34fb5f83b9ab12c37a443bf22` | Tracked-clean. Reassert immediately before rehearsal/apply. |
| App original old side | `6bfa6453d1bac232eb81ab35fa7f14b50b0b291a` | Exists; correct original-row old side. |
| App Phase-154 retarget base | `bc9d59293b9a08b16d6d7eb16eaf6c6f53e88e65` | Exists; sibling Phase-154 commit used when the 815 choices were made. |
| App final HEAD | `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2` | Tracked-clean; differs from `bc9d592` by one import line in `tests/test_dispatch_mirror.py`. |
| Original manifest | SHA-256 `ecdd0fc84be1627f893e30f6369c0b9eedf2a69ce3ec351064828d82e72d992e` | 13,693 physical lines: one schema + 13,692 records. Preserve byte-identically. |

The meta gitlink is not a reliable late-record source anchor. At current meta HEAD it records firmware `2ad5b322` while the firmware worktree is at `2ccda8d`; the Phase 155-158 meta artifacts frequently carry their exact source commits in prose/summaries instead. Anchor supplemental rows from artifact history and source evidence, not from the meta gitlink alone.

### Current dirty state and preservation obligations

The source repositories are tracked-clean. The app contains pre-existing untracked files (`.planning/config.json`, `SECURITY.md`, four datasheet PDFs, and `write_test_port.sh`); inventory them and do not delete or stage them. The meta tree contains unrelated/execution changes:

- `.planning/STATE.md` modified; it contains 17 original-manifest records on 15 recorded lines.
- `.planning/v1.9-COBS-DECISION.md` deleted and `.planning/v1.33/v1.9-COBS-DECISION.md` untracked; the new file is byte-identical to HEAD and the old manifest path carries four records.
- `.planning/config.json`, Phase-159 research/validation files, `package.json`, and `package-lock.json` are changed/untracked but are not original-manifest citing documents.
- The firmware gitlink appears modified because the index still records `2ad5b322` and the worktree is intentionally at `2ccda8d`; it must remain unstaged.

The COBS relocation is not visible to `git diff --find-renames` because its destination is untracked. It therefore needs an explicit current-worktree location overlay or a production preflight stop. A detached-HEAD rehearsal will otherwise restore the old path and fail to exercise the live production topology.

### Original-manifest inventory

| Measure | Verified value | Planning meaning |
|---|---:|---|
| Records / occurrences | 13,692 / 13,290 | Colon lists expand one occurrence into multiple records. |
| Planning files scanned / files with records | 2,947 / 1,228 | Do not confuse the header's scanned-file count with the affected citing-document count. |
| `retarget: true` | 815 | All carry hand-chosen post-154 target fields. |
| Retarget choices at final tree | 717 same coordinate / 93 moved verbatim / 5 no longer verbatim | Reproduced against `2ad5b322` or `bc9d592` to current final source. |
| Readable ordinary rows | 9,363 | Current homogeneous map candidates before planning association. |
| Ordinary composite non-survivors | 105 rows / 46 docs / 10 firmware targets | 103 appear in current diagnostic; 2 are hidden by later duplicate citation groups. Must be ledgered/reviewed. |
| Current diagnostic unmatched | 156 | Must become zero after location/ordinal reconciliation; current tool incorrectly exits 0 on this class. |
| Marker | `.planning/v1.33/CITATIONS-STALE.md` present | Correct until Plan 159-06. |

### Post-manifest inventory

The shared citation grammar reproduces the four requested phase-directory counts exactly:

| Phase directory | Occurrences | Records |
|---|---:|---:|
| 155 | 123 | 127 |
| 156 | 176 | 184 |
| 157 | 214 | 225 |
| 158 | 99 | 106 |
| **Subtotal** | **612** | **642** |

However, a full added-file comparison from the manifest commit through Phase 158 finds:

| Added non-tool planning class absent from original manifest | Records |
|---|---:|
| Post-manifest Phase-154 summaries/verification | 125 |
| Phase 155-158 directories | 642 |
| Added `.planning/v1.33/` evidence records | 77 |
| **Added-file subtotal** | **844** |

The modified global documents have record-count deltas: PROJECT +1, REQUIREMENTS +7, ROADMAP +16, STATE +7, Phase-154 `deferred-items.md` +5, and the read-timing todo +1, for net +37. Net growth is only a lower bound on newly authored rows because replacement can remove one historical occurrence while adding more than one. Therefore the preparer must perform a positional history reconciliation rather than set a fixed supplemental count of 881.

### Real range proof

The original manifest row at `.planning/milestones/v1.0-phases/02-firmware-json/02-VERIFICATION.md:65` records:

```text
old 128: if (jsoneq_(json, key_token, key) == 0) {
old 131:     token_idx += 2; // Skip key and simple value
```

At firmware final `2ccda8d`, `LineMap.span(128, 131)` returns `(316, 318, False)` and the destination endpoints are byte-identical:

```text
new 316: if (jsoneq_(json, key_token, key) == 0) {
new 318:     token_idx += 2; // Skip key and simple value
```

The interior old `parser_func` load/call becomes one `store_field(...)` line, so the inclusive span shrinks 4 -> 3 without either endpoint needing a semantic retarget.

## Exact Current Commands

### Raw committed dry run (currently exits 1 before reporting)

```bash
python3 .planning/v1.33/tools/remap_citations.py /workspaces \
  --manifest .planning/v1.33/sweep-citation-manifest.jsonl \
  --pre-sweep-sha firestarter=8695ee52c27a4bee4387c5c489afd5f3d7275e8a \
  --pre-sweep-sha firestarter_app=6bfa6453d1bac232eb81ab35fa7f14b50b0b291a \
  --quiet-notes
```

Current result:

```text
ERROR: citing document does not exist: .planning/todos/pending/2026-08-22-sweep-gsd-provenance-comments-from-firmware-and-host-source.md
```

### Viable focused pytest command

```bash
/usr/local/py-utils/venvs/pytest/bin/python -m pytest -q \
  .planning/v1.33/tools/test_remap_citations.py
```

Current result is `20 passed, 1 failed`; the only failure is the obsolete Phase-154 real-tree non-application guard, which reports `.planning/STATE.md` and `.planning/v1.9-COBS-DECISION.md`. Bare `python3 -m pytest` is an infrastructure failure and must not be accepted as a RED test. The `PYTHONPATH=/workspaces/firestarter_app/.venv/ci-replica/lib/python3.11/site-packages python3 ...` command in `159-VALIDATION.md` also runs pytest 9.1.1, but the dedicated py-utils interpreter is cleaner than loading Python-3.11 site packages into Python 3.12.

### Archive correction baseline

```bash
python3 .planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py
```

Current result is PASS with verdict counts including `superseded: 12`. The run takes about one minute in this container, so allow more than a 30-second command yield and keep the user informed while it runs.

## Required Architecture

```text
original manifest (immutable 13,692) ───────────────┐
whole bounded-window planning delta ───────────────┤
Phase-154 hand choices (post-154 anchor) ──────────┤
live worktree location/dirty overlay ──────────────┘
                         |
              stable positional identities
                         |
       per-record (source path, historical SHA) maps
                         |
          ┌──────────────┴──────────────┐
          |                             |
 verbatim/fixed-point             non-survivor or ambiguity
 destination-text oracle          evidence-backed review ledger
          |                             |
          └──────────────┬──────────────┘
                         |
   zero unmatched / dynamic-retarget / open-review / oracle errors
                         |
 exact-corpus disposable rehearsal (including approved dirty overlay)
                         |
 preimages + exclusive receipt -> one production --apply
                         |
 dry run two + full affected-corpus byte equality
                         |
 archive gate -> scoped closure -> marker deletion last
```

### Record identity and anchors

- Preserve the original manifest byte-for-byte. Assign deterministic stable IDs externally or during normalization from immutable record identity plus positional ordinal; do not rewrite the file to add IDs.
- Cache line maps by `(target_file_resolved, source_sha)`, not path alone.
- Original homogeneous rows use firmware `8695ee52` and app `6bfa6453`.
- Phase-154 hand choices advance from firmware `2ad5b322` or app `bc9d592`; their selected current text gets its own oracle.
- Every supplemental record must carry a historically justified `source_sha`, or a nonempty candidate set that remains blocking until reviewed. A final-tree self-snapshot is not a historical oracle.
- Reconcile current document path, line, citation group, and ordinal before applying the source map. Current duplicate occurrences in REQUIREMENTS/ROADMAP prove that line/path alone is insufficient.

### Complete exception set

Define the review IDs as the exact union of:

1. the five Phase-154 hand choices whose selected text disappeared again;
2. all 105 currently measured ordinary original-record composite non-survivors, including the two hidden by unmatched duplicate groups;
3. every supplemental record whose endpoint does not survive from its authoring anchor;
4. every non-unique historical source anchor;
5. every ambiguous planning path/line/ordinal reconciliation, including any unresolved live-worktree relocation.

This makes 110 the known minimum, not the final count. Some records may share one semantic decision, but each stable record ID still needs an explicit ledger disposition and oracle.

### Production write safety

`atomic_write()` protects one document, not the batch. Before the only apply, the phase needs:

- complete preimage hashes and recoverable bytes/patches for every affected file, including untracked or renamed affected documents;
- all final output rendered to temporary files before the first replacement;
- a receipt state machine (`PREPARED`, `APPLYING`, `APPLIED`, `FAILED`) with exact replaced-file progress and preimages;
- an injected mid-write failure test proving the documented recovery/rollback behavior;
- no automatic retry that could be mistaken for a second production event.

The safest plan is to make one invocation finish or roll back within that invocation. If that cannot be proven, a `FAILED` receipt must stop execution and present an explicit recovery procedure rather than claiming transaction atomicity.

### Preserve unrelated user changes

Production preflight must compute `affected_documents ∩ preexisting_dirty_paths`. For each overlap, either:

- stop for user direction;
- carry the live bytes into rehearsal, prove only citation spans change, and stage only the remap hunks/index objects while leaving unrelated worktree changes unstaged; or
- obtain explicit authorization to include the pre-existing change.

Staging entire receipt-listed paths is not sufficient. On the current tree it would absorb Phase-159 STATE bookkeeping and the user's COBS relocation if those files receive remap edits. The rehearsal must use the same live bytes/topology chosen for production; a clean detached HEAD alone is not equivalent.

## Validation Architecture

### Required test legs

1. Interpreter preflight proves the exact pytest executable/interpreter and version; RED runs assert successful collection and named failing behaviors, never merely nonzero exit.
2. Wrong original app anchor `bc9d592` fails; correct `6bfa6453` passes. The current location-restored wrong-anchor run yields 787 violations.
3. Tracked rename, shifted line, duplicate same-path/variant occurrence, and untracked relocation each reconcile deterministically or produce a blocking stable ID.
4. Every actionable unmatched/not-at-recorded/dynamic-retarget/open-review/missing-target/oracle class exits 1 with zero writes.
5. All 815 hand-retarget rows preserve the 717/93/5 partition and reviewed rows become fixed points.
6. All 105 ordinary original composite non-survivors are represented; none can hide behind an unmatched group.
7. The supplemental census proves full bounded-window coverage and separately reports the verified 642 phase-directory subset; a deliberately added citation outside those directories must make the coverage gate RED.
8. Two records for one target with different source SHAs use different maps.
9. Real `json_parser.c:128-131 -> 316-318` checks coordinates, span 4 -> 3, and endpoint text.
10. A late validation failure after hundreds of planned edits writes zero documents.
11. An injected write failure after at least one successful replacement exercises the batch recovery/receipt contract.
12. Rehearsal uses the exact production corpus bytes/topology, applies once in a disposable root, then dry-runs to 0 rewrites/documents with full hash equality.
13. A dirty affected-document fixture proves unrelated hunks are preserved and excluded from the Phase-159 commit.
14. Archive correction output remains PASS/`superseded: 12`; marker remains until closure and is absent afterward.

### Phase gate

Before production apply, require all of the following in one READY record:

- exact current source HEADs and tracked-clean source trees;
- original manifest hash and complete supplemental/ledger hashes;
- complete current planning topology and affected-document preimages;
- zero actionable/open rows, with nonzero examined/planned totals;
- exact rehearsal input hashes/topology matching production;
- real range proof and archive PASS/12;
- marker present;
- receipt absent and production apply event count zero;
- explicit disposition for every pre-existing dirty affected path.

After the sole apply: receipt event count 1, dry second run 0/0, affected-corpus byte equality, archive PASS/12, source/gitlink invariance, then scoped REMAP/ROADMAP closure and marker deletion last.

## Audit of the Existing Six Plans

| Plan | Shape to keep | Correction required before execution |
|---|---|---|
| 159-01 | Harden existing engine/test harness; add per-record anchors, location reconciliation, blocking outcomes, reports, receipt | Its premise that the 21-test suite passes and raw dry run exits 0 is stale. Pin the py-utils pytest interpreter. Its RED verifier currently accepts `python3 -m pytest` import failure as success. Add the 105 ordinary dynamic-retarget class, full-window coverage control, and mid-write recovery test. If a real-range fixture file is created, add it to `files_modified`. |
| 159-02 | Deterministic preparer, supplemental manifest, exception ledger, review packet | Do not fix the late manifest at 642. Scan the whole bounded temporal planning delta; report 642 as a required subset and compute the exact total. Define `review_ids` to include all 105 ordinary original non-survivors, making the known floor 110. Explicitly handle the live COBS relocation and every dirty/current location overlay. |
| 159-03 | Blocking evidence-backed human checkpoint is legitimate despite no CONTEXT.md | Present the dynamically measured set with known floor 110, not five. `files_modified: []` conflicts with its promised `159-03-SUMMARY.md`; declare the summary output. Batch repeated semantic decisions only if every stable ID remains individually recorded. |
| 159-04 | Zero-open dry run plus disposable apply/no-op/hash/range/archive rehearsal | A detached meta worktree at HEAD does not contain the current uncommitted COBS move or STATE bytes. Materialize the approved live corpus overlay in rehearsal and hash it, or stop until overlaps are resolved. Pin the viable pytest interpreter and include mid-write recovery in rehearsal tests. |
| 159-05 | Exact SHA/hash preflight, one literal apply command, dry second run, authoritative record | Add a mandatory dirty-overlap gate and index-safe staging proof; staging whole changed paths would absorb unrelated changes. Match production document bytes/topology to rehearsal, not only tool/manifest/source hashes. Capture preimages and a failure-recovery receipt before relying on “exactly once.” The planned stdlib remapper command itself is correctly rooted and uses the correct original SHAs. |
| 159-06 | Scoped REQUIREMENTS/ROADMAP edits, archive gate, marker deletion last, no milestone/push/release action | Sequence is sound. Re-run the corrected interpreter/corpus gates, preserve STATE and SWEEP-13, and verify the close commit contains no unrelated dirty paths. |

The dependency order remains strictly sequential: harden -> inventory -> review -> settle/rehearse -> apply/prove -> close.

## Common Failure Modes

- **Treating 642 as corpus completeness:** it ignores at least 202 added non-tool records outside Phase 155-158 directories plus new global-document occurrences.
- **Treating five as the review set:** it ignores 105 ordinary original rows whose cited endpoints disappear in the composite diff.
- **Calling a missing pytest module “RED”:** Plan 159-01's current shell shape can pass without collecting any test.
- **Using `bc9d592` for original app rows:** reproduced 787 oracle violations; reserve it for hand-retarget advancement.
- **Accepting unmatched/retarget notes with exit 0:** this is the current location-restored behavior and is incompatible with REMAP-02.
- **Rehearsing only committed HEAD:** misses current worktree topology and dirty affected bytes.
- **Staging whole affected files:** can commit user/orchestrator changes along with remapped citations.
- **Calling per-file `os.replace` a batch transaction:** a process/I/O failure can occur between documents.
- **Regenerating the original manifest:** destroys the pre-sweep oracle and makes the proof tautological.
- **Applying twice for idempotency:** violates the one-shot production contract; run two is dry.
- **Deleting the marker before closure evidence:** removes the structural close block while exceptions may remain.

## Resolved Planning Decisions

1. **No separate discussion phase is required, but semantic review is.** “No CONTEXT.md” means there are no discretionary scope choices to inherit. It does not authorize guessed targets for deleted/reflowed lines.
2. **Supplemental cardinality is dynamic.** The phase must prove complete bounded-window coverage. The 642 phase-directory count remains a required reconciliation subtotal, not the final total.
3. **Review cardinality is dynamic with a known minimum of 110.** This is the five re-deleted hand choices plus 105 ordinary original composite non-survivors, before supplemental and location/anchor cases.
4. **Current unrelated changes are not authorized for inclusion.** If the COBS relocation or another affected dirty path remains at production preflight, pause for direction unless the implementation can prove overlay-preserving, hunk-isolated staging.
5. **Milestone boundary:** Phase 159 closes REMAP-01..05 and leaves v1.33 ready for `/gsd-complete-milestone`; it does not archive, release, push, open/merge a PR, or run milestone completion.

## Sources

### Primary

- `.planning/REQUIREMENTS.md` REMAP-01..05 and traceability.
- `.planning/ROADMAP.md` Phase 159 success criteria and six-plan sequence.
- `.planning/STATE.md` Phase 154-158 handoffs, anchors, manifest invariants, and current execution state.
- `.planning/v1.33/sweep-citation-manifest.jsonl`, `sweep-outcome-record.md`, `baseline-pre-sweep.md`, and `CITATIONS-STALE.md`.
- `.planning/v1.33/tools/remap_citations.py`, `test_remap_citations.py`, `build_citation_manifest.py`, and `citation_paths.py`.
- Phase 154-158 plans, research, summaries, validation, verification, and v1.33 before/after records.
- Direct executions on 2026-08-24: raw dry run; disposable location-restored correct/wrong-anchor runs; original/late/whole-window censuses; 815 retarget advancement audit; 105 ordinary non-survivor audit; pytest interpreter/suite checks; Git object/head/diff checks; real range mapping; and archive correction gate.

### Secondary

None. This is a repository-local migration; no web source is needed to plan it.

## Metadata

**Confidence breakdown:**

- Commands, SHAs, manifest hash/counts, current Git state, pytest viability, raw/diagnostic behavior, 815 partition, 105 ordinary non-survivors, 642 subset, added-file 844 count, range proof, and archive baseline: HIGH.
- Exact whole-window supplemental row count: MEDIUM until positional history reconciliation completes; verified lower bound is 881 grammar records absent/new relative to the original snapshot, with 642 as an exact subset.
- Final review count: MEDIUM until the complete supplement/location ledger is built; verified minimum is 110.

**Research date:** 2026-08-24
**Valid until:** any of the three repository HEADs, the meta dirty topology, or the original manifest hash changes. Re-run every inventory and preflight immediately before rehearsal and production apply.
