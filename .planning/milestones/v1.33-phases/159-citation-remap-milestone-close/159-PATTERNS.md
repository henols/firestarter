# Phase 159: Citation Remap + Milestone Close - Pattern Map

**Mapped:** 2026-08-24
**Files analyzed:** 10 implementation/artifact classes (including the manifest-selected planning corpus)
**Analogs found:** 10 / 10

## Scope and Naming Assumptions

There is no `159-CONTEXT.md`, so this map takes the file surface from `159-RESEARCH.md`, `159-VALIDATION.md`, `ROADMAP.md`, and `REQUIREMENTS.md`. Research explicitly names five files and implies three more artifacts whose final filenames the planner must lock. The conventional names used below are:

- `.planning/v1.33/159-remap-exceptions.jsonl` for the machine-readable reviewed-retarget/exception ledger.
- `.planning/v1.33/tools/rehearse_citation_remap.py` for the disposable-corpus apply/no-op/hash harness.
- `.planning/v1.33/159-remap-record.md` for the authoritative production and closeout record.

If planning chooses different names, preserve the assigned analog and data contract. The 13,692-row original `.planning/v1.33/sweep-citation-manifest.jsonl` is immutable input, not a file to regenerate or edit.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.planning/v1.33/tools/remap_citations.py` | utility / migration transaction engine | batch transform + Git/file I/O | itself, especially `LineMap`, `decide`, `remap_document`, and `main` | exact extension |
| `.planning/v1.33/tools/test_remap_citations.py` | test | subprocess integration + file I/O | itself (`Harness` and fail-closed/idempotency tests) | exact extension |
| `.planning/v1.33/tools/fixtures/*` (real-range metadata and any new synthetic fixtures) | test fixture | deterministic file I/O | existing `tools/fixtures/*` plus `_record()` in `test_remap_citations.py` | exact |
| `.planning/v1.33/159-late-citation-manifest.jsonl` | migration manifest / model | scan-to-JSONL batch | `sweep-citation-manifest.jsonl` produced by `build_citation_manifest.py` | exact, schema extension |
| `.planning/v1.33/159-remap-exceptions.jsonl` (name to lock) | reviewed decision ledger / model | batch reconciliation | `build_citation_manifest.py` JSONL ordering/self-check + `sweep-gate-dispositions.md` exhaustive disposition rule | role/data-flow match |
| `.planning/v1.33/tools/rehearse_citation_remap.py` (name to lock) | validation harness / utility | disposable copy, subprocess, hash comparison | `Harness` in `test_remap_citations.py` + `sweep-outcome-record.md` command/evidence style | strong composite |
| Manifest-selected `.planning/**/*.md` citing documents | migrated stored data | all-or-nothing batch transform | `remap_citations.py:944-990` whole-run plan then atomic write | exact |
| `.planning/v1.33/159-remap-record.md` | authoritative evidence record | append-only measured report | `.planning/v1.33/sweep-outcome-record.md` | exact role |
| `.planning/v1.33/CITATIONS-STALE.md` | close-blocking marker | delete after gated state transition | its own sections 4-6 | exact |
| `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` | config / milestone records | scoped status update | Phase 158 closure in `158-07-PLAN.md` | exact |

## Pattern Assignments

### `.planning/v1.33/tools/remap_citations.py` (utility, batch transform + Git/file I/O)

**Analog:** existing `.planning/v1.33/tools/remap_citations.py`.

Extend this engine; do not add a second citation parser or writer. Keep stdlib imports and the shared grammar/resolver import pattern (`remap_citations.py:183-205`):

```python
import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import build_citation_manifest as bcm
import citation_paths

CITATION_RE = bcm._CITATION_RE
spans_from_match = bcm._spans_from_match
TEXT_STATUS_READ = bcm.TEXT_STATUS_READ
```

**Mapping pattern** (`remap_citations.py:234-249,281-314`): retain `SequenceMatcher(..., autojunk=False)`, treat `replace` as non-surviving, and map range endpoints independently.

```python
sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            m[i1 + k + 1] = j1 + k + 1
    elif tag in ("delete", "replace"):
        for k in range(i1, i2):
            m[k + 1] = None

def map_range(m, a, b, n_old, survivors=None):
    a2, ra = map_point(m, a, n_old, "fwd", survivors)
    b2, rb = map_point(m, b, n_old, "back", survivors)
    return a2, b2, (ra or rb)
```

Phase 159 should change the map cache key from target path alone to `(target_file_resolved, source_sha)` while leaving `LineMap` itself intact. Original rows get the fixed pre-154 SHA; reviewed old retarget choices use their post-154 anchor; mechanically settled late records carry their own historical SHA. A late row with multiple viable anchors preserves `source_sha_candidates`, joins a blocking `historical_anchor` review row, and enters the cache only after review selects one SHA.

**Oracle/write predicate** (`remap_citations.py:397-466`): fixed-point first, then recorded identity, then mapping, then destination-text oracle. Reviewed retargets need a parallel current-target-text oracle, not an oracle bypass.

```python
if lm.text_at(cur_start) != record["source_text"]:
    return False
if cur_end is not None and lm.text_at(cur_end) != record["source_text_end"]:
    return False

if cur_start != record["target_line"] or cur_end != record["target_line_end"]:
    return Outcome(NOT_AT_RECORDED_LINE, cur_start, cur_end, ...)

if lm.text_at(new_start) != src:
    return Outcome(VIOLATION, new_start, new_end, ...)
```

**Association pattern** (`remap_citations.py:516-550`): bind positionally within `(cited path, variant)` groups. Never bind by the integer currently in the document. A cardinality mismatch remains explicit and becomes blocking in Phase 159.

```python
for rec in records:
    record_groups[(rec["target_file_cited"], rec["variant"])].append(rec)

for key, recs in record_groups.items():
    spans = span_groups.get(key, [])
    if len(spans) != len(recs):
        counts[NO_MATCH_IN_DOCUMENT] += len(recs)
        ...
        continue
    for span, rec in zip(spans, recs):
        assigned[(span[0], span[1])] = rec
```

Planning-location reconciliation should occur before this association and preserve each record's source fields. Resolve the moved document and shifted `planning_line` from the original manifest commit; ambiguity must enter the blocking exception ledger.

**Transaction/error pattern** (`remap_citations.py:944-990`): plan every document before any write. Phase 159 must broaden the `violations` condition so actionable unmatched, not-at-recorded, unreviewed retarget, missing/ambiguous location, and oracle failures all exit non-zero before the write loop.

```python
planned: dict[Path, str] = {}
for rel in sorted(by_doc):
    original = doc_path.read_text(encoding="utf-8")
    updated = remap_document(...)
    if updated != original:
        planned[doc_path] = updated

if violations:
    print("FAIL: ... nothing was written", file=sys.stderr)
    sys.exit(1)

if args.apply:
    for path, text in planned.items():
        atomic_write(path, text)
```

**File safety pattern** (`remap_citations.py:691-723`): retain relative-path/traversal checks, containment checks, symlink refusal, same-directory temporary files, and `os.replace`.

### `.planning/v1.33/tools/test_remap_citations.py` and fixtures (test, subprocess integration)

**Analog:** the existing test module's throwaway Git `Harness` (`test_remap_citations.py:135-209`). It commits the historical side, overwrites only the working-tree target, and invokes the real CLI with explicit paths and SHA.

```python
class Harness:
    def __init__(self, tmp_path, old_lines=None, new_lines=None, doc_text=None):
        self.root = tmp_path / "repo"
        ...
        assert _git(self.root, "init", "-q").returncode == 0
        assert _git(self.root, "add", "-A").returncode == 0
        assert _git(self.root, "commit", "-qm", "pre-sweep").returncode == 0
        self.sha = _git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.target.write_text("\n".join(new) + "\n", encoding="utf-8")

    def run(self, *extra, manifest=None):
        return subprocess.run(
            [sys.executable, _TOOL, str(self.root), "--manifest",
             str(manifest or self.manifest), "--pre-sweep-sha", self.sha, *extra],
            capture_output=True, text=True, check=False,
        )
```

Add Phase 159 legs to this module rather than creating a parallel test framework. Follow these existing assertion shapes:

- Real shrink: model on `test_range_spanning_deleted_block_shrinks` (`:322-333`), but use committed metadata for `json_parser.c:128-131 -> 316-318` and assert old span 4, new span 3, both endpoint texts.
- Idempotency: model on `test_idempotent_on_chained_map` (`:386-405`), but run the second real-corpus check without `--apply` and compare bytes/hashes.
- Whole-run rollback: model on `test_oracle_violation_exits_1_and_writes_nothing` (`:650-664`). Seed many successful planned edits plus one late failure, then assert every document remains unchanged.
- Fail-closed semantics: follow exit codes already established at `:450-464,650-703`: `1` for contract/oracle violations, `2` for infrastructure/schema failures.
- Wrong/correct app anchor, moved document, shifted line ambiguity, reviewed-retarget fixed point, two old SHAs for one target, and post-154 re-deletion should all use the same harness and `_record()` factory (`:291-307`).

The existing real-tree non-application guard at `:724-758` is Phase-154-specific. Replace or retire it deliberately when the production apply becomes authorized; do not let an obsolete guard fail after a correct Phase 159 migration.

### `.planning/v1.33/159-late-citation-manifest.jsonl` (manifest/model, scan-to-JSONL)

**Analog:** `.planning/v1.33/sweep-citation-manifest.jsonl` and `build_citation_manifest.py`.

Keep one self-describing `_schema` header first, one compact JSON object per record, deterministic record/key order, and no blank lines. The existing fixed ordering is at `build_citation_manifest.py:193-210`; serialization and atomic write are at `:389-394,594-602`:

```python
RECORD_KEYS = (
    "planning_file", "planning_line", "variant",
    "target_file_cited", "target_file_resolved",
    "resolution", "resolution_reason", "target_line", "target_line_end",
    "source_text", "source_text_end", "text_status", "text_status_end",
    "retarget",
)

def _dump(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(_dump(header) + "\n")
    for record in records:
        fh.write(_dump(_ordered(record)) + "\n")
os.replace(tmp_path, out_path)
```

Extend the late-record schema with a stable record ID and either explicit `source_sha` or nonempty `source_sha_candidates` (plus root when not safely derivable). Preserve both endpoint texts/statuses for ranges and candidate anchors. Derive records through `bcm._CITATION_RE`, `bcm._spans_from_match`, and `citation_paths.CandidateIndex`; do not rescan the final tree as the historical oracle. Add a serialize-then-read self-check matching `build_citation_manifest.py:611-657` and byte-identical regeneration matching `test_build_citation_manifest.py:384-393`.

### `.planning/v1.33/159-remap-exceptions.jsonl` (review ledger, reconciliation batch)

**Analogs:** the manifest JSONL machinery above for machine readability and `.planning/v1.33/sweep-gate-dispositions.md:12-16,28-37` for completeness: an item absent from the ledger is an unrecorded exception, and every row carries a disposition and cause.

Use stable record IDs that join back to original/late records. Each row should preserve historical identity, classification, candidate/current coordinates, chosen final endpoint(s), chosen current text(s), reviewer rationale, and status. Deterministic order and self-check are required. Keep unresolved rows in the file; never drop them from serialization. The production gate requires zero rows whose status is unreviewed/ambiguous.

### `.planning/v1.33/tools/rehearse_citation_remap.py` (validation harness, disposable copy + hashes)

**Composite analogs:** test `Harness` for historical Git/subprocess isolation and `sweep-outcome-record.md:13-16,34-55` for evidence capture.

The harness should call the production parser/writer CLI, not import a second rewrite implementation. It should:

1. Materialize a disposable copy/worktree of the citing corpus while leaving `firestarter/` and `firestarter_app/` read-only inputs at asserted SHAs.
2. Snapshot a deterministic path-to-SHA256 map of every affected planning document.
3. Run one rehearsal `--apply` and require success/zero actionable exceptions.
4. Snapshot the resulting corpus, run the second pass dry (no `--apply`), require `0 rewritten` and `0 documents would change`, then compare bytes/hashes unchanged.
5. Run the archive-record correction gate before and after and preserve its verdict/count.
6. Print non-vacuous counts; zero discovered records/documents is infrastructure failure, never PASS.

Use explicit argv lists with `subprocess.run(..., capture_output=True, text=True, check=False)`, as in the test harness. Refuse to operate on `/workspaces` as the disposable apply target. Production application remains a separate, single recorded invocation.

### Manifest-selected `.planning/**/*.md` (stored data, all-or-nothing batch transform)

**Analog:** `remap_citations.py:949-970,988-990`.

The file list must come from reconciled manifest records, not a broad regex rewrite. Read each document once, preserve all bytes except rendered citation spans, store changed full-text results in `planned`, and write only after every record has passed. Archives under `.planning/milestones/` are in scope. Do not globally normalize Markdown or rewrite ROADMAP/REQUIREMENTS as part of this batch beyond the citation spans selected by the manifest.

### `.planning/v1.33/159-remap-record.md` (authoritative evidence record)

**Analog:** `.planning/v1.33/sweep-outcome-record.md:1-16` for frontmatter and authority language, and `:20-60` for command + before/after table + explicit conclusion.

```markdown
---
title: ...
phase: 159-citation-remap-milestone-close
plan: "..."
measured: 2026-08-24
status: AUTHORITATIVE — ...
requirements: [REMAP-01, REMAP-02, REMAP-03, REMAP-04, REMAP-05]
---

# ...

Every number below carries the command that produced it, measured on this machine ...
```

Record exact repository SHAs, manifests and row counts by class, reconciliation totals, the sole production `--apply` command, changed-document count, oracle totals, the real range shrink with endpoint texts, second-pass dry-run output and corpus hashes, archive gate before/after, marker absence, and closure edits. Distinguish measured output from research estimates. The record should make “exactly one apply” auditable by listing a single production apply event; rehearsal applies are explicitly labeled disposable.

### `.planning/v1.33/CITATIONS-STALE.md` (close-blocking marker, deletion)

**Analog:** its own close contract at `CITATIONS-STALE.md:234-241`:

```markdown
**Phase 159 / REMAP-04** closes this window. Removing this file is **REMAP-04's own
deliverable**, and that removal is **close-blocking**: **milestone v1.33 cannot close while
this file exists.**
```

Delete only after the production oracle, no-op/hash, real-range, archive-record, and evidence-record gates pass. Final validation is a negative existence check: `test ! -e .planning/v1.33/CITATIONS-STALE.md`. The marker's older suggestion to regenerate the original manifest is superseded by Phase 159 research; preserve the original historical oracle.

### `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` (milestone config, scoped update)

**Analog:** `.planning/phases/158-.../158-07-PLAN.md:15-35,149-219`.

Use scoped replacements only. In REQUIREMENTS, tick REMAP-01..05, append discharge/evidence text, and change exactly their traceability rows from `Pending` to `Complete (..., closed 159-XX)`. In ROADMAP, fill Phase 159's `**Plans:**`/plan list and append measured closure text to its five criteria. Preserve heading count, require line count not to fall (except for the separately deleted marker file), and diff against snapshots to prove no other phase/requirement moved. Do not use a whole-file generator or a GSD mutation helper on these hand-authored files.

## Shared Patterns

### Single grammar and resolver authority

All record generation and application imports citation syntax from `build_citation_manifest` and resolution from `citation_paths` (`remap_citations.py:194-205,852-899`). Fixture-collision handling must continue to use shared constants, not copied strings or basename guessing.

### Explicit historical identity

Git blobs are the old-side truth (`remap_citations.py:365-383`). Every map lookup must be determined by explicit target plus SHA. CLI anchors may cover homogeneous original rows; supplemental and retarget rows need per-record anchors. Never infer old content from the current filesystem.

### Fail closed, with distinct exit classes

- Exit `0`: every applicable record classified, every oracle held, and non-vacuous totals printed.
- Exit `1`: data/contract violation such as ambiguity, unmatched actionable row, unreviewed retarget, oracle mismatch, missing target, traversal, or collision.
- Exit `2`: infrastructure/schema/argv failure.

No writes may precede the complete violation check. Counts alone are insufficient if an actionable exception class is nonzero.

### Determinism and fixed point

Sort documents, preserve record order within positional groups, emit ordered compact JSONL, write UTF-8 with explicit newlines, and compare bytes on repeat execution. Idempotency is recognized from destination text before interpreting a current integer as an old coordinate.

### No auth or external service pattern

This phase is a local Git/filesystem migration. There is no authentication, network service, database transaction, or package dependency to copy. Path containment, symlink refusal, explicit roots/SHAs, and atomic replacement are the relevant guards.

### Closure sequencing

The required state transition is: hardened zero-exception dry run -> disposable apply/no-op rehearsal -> one production apply -> dry no-op/hash proof -> archived-record gate -> authoritative record -> marker deletion -> scoped requirement/roadmap close. Marker deletion or REMAP closure before the preceding evidence is a contract violation.

## Anti-Patterns to Reject in Planning

- Regenerating or editing `sweep-citation-manifest.jsonl` against the final tree.
- Using `bc9d592` as the original app old-side SHA; original app rows use `6bfa6453`.
- Leaving `retarget: true` rows numerically untouched merely because the old oracle is skipped.
- Treating unmatched/not-at-recorded/ambiguous rows as notes while exiting 0.
- Applying a second time to production to prove idempotency.
- Building a new citation regex, resolver, line mapper, or per-record in-place writer.
- Using constant-offset range translation.
- Applying broadly to all Markdown by regex rather than the reconciled manifest-selected corpus.
- Whole-file rewrites of ROADMAP.md or REQUIREMENTS.md.
- Deleting `CITATIONS-STALE.md` before all close gates pass.
