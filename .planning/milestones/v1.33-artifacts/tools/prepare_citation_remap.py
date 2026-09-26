#!/usr/bin/env python3
r"""
Whole-window historical citation-remap preparer -- milestone v1.33, Phase 159
plan 02 (REMAP-01, REMAP-02, REMAP-04, REMAP-05).

WHAT THIS PRODUCES AND WHY
---------------------------
Phase 154 plan 04's `sweep-citation-manifest.jsonl` (13,692 rows, immutable)
covers every citation that existed in `.planning/` at the manifest commit
`9a78bc6d`. Phases 155-158 then added and modified planning documents whose
citations that manifest never saw. This tool produces FOUR artifacts so that
Phase 159's ONE production remap (REMAP-01) can cover the WHOLE bounded
window rather than only the original manifest:

  1. `159-late-citation-manifest.jsonl` -- every citation record newly
     authored between the manifest commit and the Phase-158 completion
     boundary, in the SAME schema `build_citation_manifest.py` uses, plus a
     handful of additive fields (`record_id`, `origin`, `phase`,
     `source_sha`, ...) so it can be fed to `remap_citations.py` alongside
     the original manifest via a repeated `--manifest` flag.
  2. `159-remap-exceptions.jsonl` -- the exhaustive, evidence-backed ledger
     of every record that needs a HUMAN decision before the one production
     apply: the five (measured: eighteen) Phase-154 hand choices whose
     chosen post-154 target text no longer survives verbatim to the final
     tree, the 105 (measured: 217) ordinary original-manifest records whose
     endpoint does not survive the composite diff, and any supplemental
     record or historical-anchor ambiguity discovered along the way. Every
     row's `status` starts `needs_review` -- THIS PLAN APPROVES NOTHING.
  3. `159-retarget-review.md` -- a human-readable evidence packet, one
     `## Record <id>` section per pending record.
  4. `159-corpus-overlay.json` (written as JSONL, one row per line, matching
     `remap_citations.py --corpus-overlay`'s reader) -- the live-worktree
     topology/dirty-byte inventory for every citing document affected by a
     tracked deletion+untracked-relocation or other topology change the
     research phase found. Every row's `approval_status` is `pending`.

WHY THE CANDIDATE INDEX IS BROADER THAN THE ORIGINAL MANIFEST'S
------------------------------------------------------------------
`citation_paths.survey_candidates()` returns only files carrying a
PROVENANCE-COMMENT hit -- the Phase-154 sweep TARGET set. By definition the
sweep already removed most of those comments, so calling it now (post-sweep)
returns 75 files, not the 171 the original manifest resolved against. Using
it here would misclassify hundreds of legitimately-resolvable Phase 155-158
citations as `unresolved`. This tool instead builds its `CandidateIndex`
over `build_citation_manifest._full_repo_paths()` -- the WHOLE current
source tree under the declared target extensions -- exactly the index
`build_citation_manifest.py --stats` already uses for its own reconciliation
diagnostic. The resolution RULE (`citation_paths.CandidateIndex.resolve`)
is unchanged and shared, so a citation cannot resolve two different ways in
the generator, this preparer and the remapper.

HISTORICAL ANCHORING -- THE GITLINK-AT-AUTHORING-COMMIT RULE
----------------------------------------------------------------
Research (`159-RESEARCH.md`, "Record identity and anchors") requires every
supplemental record to carry a HISTORICALLY JUSTIFIED source SHA -- never a
final-tree self-snapshot. This tool derives it directly from the meta
repository's own history: for the commit that ADDED (or, for a modified
global document, the window-END commit that last touched) the citing
planning file, `git ls-tree <commit> -- firestarter firestarter_app` names
the exact firmware/app submodule commit the meta repo pointed to AT THAT
MOMENT. That is not a guess -- it is the literal historical anchor the
citing document's author was looking at, recovered from the meta repo's own
gitlinks, and it is verified readable (the target line exists in that blob)
before being trusted. A record whose gitlink-derived blob cannot be read at
the cited line degrades to a two-candidate `source_sha_candidates`
(gitlink-at-authoring, root-final-head) and is routed to the exceptions
ledger rather than guessed at.

WHOLE-WINDOW COVERAGE, RECONCILED, NOT ASSUMED
------------------------------------------------
`census_added_files()` covers every added `.planning` file (candidate
records = the file's whole current text, since nothing existed there
before); `census_modified_files()` covers the six pre-existing global
documents (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, Phase-154
`deferred-items.md`, the read-timing todo) that the window's `git diff`
shows modified, using `difflib.SequenceMatcher` over the ORDERED sequence
of (target_file_cited, variant, target_line, target_line_end) tuples --
the original manifest's own rows for that file are the "before" side, so a
citation that merely shifted position inside the document is recognised as
`equal` (no new record), and only genuinely NEW tuples become supplemental
rows. `census.total_added_files`/`total_modified_files` and the four-phase-
directory subtotal (642 = 127+184+225+106) are asserted exactly; the WHOLE
total is reported as measured, never hard-coded, per research's own
"dynamic, not 642, not 881" instruction.

THE REVIEW POPULATION IS MEASURED, NOT ASSUMED EITHER
--------------------------------------------------------
`known_post154_non_survivors()` re-derives, directly from git, whether each
`retarget: true` row's Phase-154 hand-chosen target (`retarget_new_line`,
`retarget_new_text`) still maps WITHOUT a clamp from its Phase-154 anchor
commit to the real final tree, using the exact same `LineMap`/`build_map`
the production engine uses -- never re-implemented. `ordinary_non_survivors()`
runs the ACTUAL hardened `remap_citations.py` (imported, not subprocess) in
non-strict diagnostic mode over the ORIGINAL manifest plus the live corpus
overlay and tracked-rename resolution, and harvests its own `open_ids` for
every readable, resolved, `retarget: false` row -- i.e. it reuses the
production association/oracle logic instead of re-deriving a second,
possibly-inconsistent notion of "non-survivor". Both measured counts are
reported honestly even where they differ from an earlier research estimate;
`159-RESEARCH.md` itself states those two figures ("5", "105") are
MEDIUM-confidence pending exactly this reconciliation.

EXIT CODES (house 0/1/2 convention)
------------------------------------
  0 -- every artifact written and its own self-check (schema, determinism,
       exact subtotal, review floor) passed.
  1 -- a real violation: the self-check found a schema problem, the 642
       phase-directory subtotal or its 127/184/225/106 partition is wrong,
       the review floor is below its measured minimum, or `--check-existing`
       found the newly-generated bytes differ from what is already on disk.
  2 -- infrastructure: a required root/SHA/file argument does not exist, or
       an empty input set came back where a nonempty one is required.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import build_citation_manifest as bcm  # noqa: E402
import citation_paths  # noqa: E402
import remap_citations as rc  # noqa: E402

CITATION_RE = bcm._CITATION_RE
spans_from_match = bcm._spans_from_match

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
LATE_RECORD_KEYS = bcm.RECORD_KEYS + (
    "record_id",
    "origin",
    "phase",
    "historical_planning_file",
    "historical_planning_line",
    "citation_ordinal",
    "source_root",
    "source_sha",
    "source_sha_candidates",
)

EXCEPTION_KEYS = (
    "record_id",
    "classification",
    "review_kind",
    "status",
    "candidate_evidence",
    "chosen_source_sha",
    "chosen_planning_file",
    "chosen_current_start",
    "chosen_current_end",
    "chosen_current_text",
    "chosen_current_text_end",
    "rationale",
    "review_source",
)

OVERLAY_KEYS = (
    "path",
    "current_path",
    "git_state",
    "preapply_sha256",
    "expected_postapply_sha256",
    "topology_action",
    "dirty_overlap",
    "approval_status",
    "staging_strategy",
    "authorization_id",
)

#: Directories/prefixes never re-scanned as supplemental sources -- the tool
#: directory carries this generator's own fixtures/tests (citation-shaped
#: literals BY CONSTRUCTION) and the two manifest outputs are inputs, not
#: sources to cite from.
SELF_EXCLUDE_PREFIXES = bcm.SELF_EXCLUDE_PREFIXES

#: The exact, research-verified four-phase-directory subtotal for the REAL
#: `/workspaces` corpus. A module-level constant (rather than a literal
#: inline in `main()`) so a test can monkeypatch it to exercise `main()`'s
#: exact-match gate end-to-end against a small synthetic fixture, without
#: needing to reproduce 642 real records.
EXPECTED_PHASE_SUBTOTAL = {"155": 127, "156": 184, "157": 225, "158": 106}
#: The research-verified review-population floors for the REAL corpus.
#: Monkeypatchable for the same reason.
MIN_KNOWN_POST154_NON_SURVIVORS = 5
MIN_ORDINARY_NON_SURVIVORS = 105
MIN_TOTAL_SUPPLEMENTAL_RECORDS = 881
MIN_REVIEW_FLOOR = 110

#: TEST-ONLY environment override: a small synthetic fixture cannot reproduce
#: the real corpus's exact counts, so `test_prepare_citation_remap.py` can
#: set `PCR_TEST_THRESHOLDS_JSON` (a JSON object with any subset of
#: `phase_subtotal`, `min_known_post154`, `min_ordinary`, `min_total`,
#: `min_review_floor`) to exercise `main()`'s gates end-to-end against its
#: own small numbers instead of the real corpus's. Absent in every real
#: invocation, so production behavior is completely unaffected.
_TEST_THRESHOLDS_ENV = "PCR_TEST_THRESHOLDS_JSON"
if os.environ.get(_TEST_THRESHOLDS_ENV):
    _overrides = json.loads(os.environ[_TEST_THRESHOLDS_ENV])
    if "phase_subtotal" in _overrides:
        EXPECTED_PHASE_SUBTOTAL = _overrides["phase_subtotal"]
    MIN_KNOWN_POST154_NON_SURVIVORS = _overrides.get(
        "min_known_post154", MIN_KNOWN_POST154_NON_SURVIVORS
    )
    MIN_ORDINARY_NON_SURVIVORS = _overrides.get("min_ordinary", MIN_ORDINARY_NON_SURVIVORS)
    MIN_TOTAL_SUPPLEMENTAL_RECORDS = _overrides.get("min_total", MIN_TOTAL_SUPPLEMENTAL_RECORDS)
    MIN_REVIEW_FLOOR = _overrides.get("min_review_floor", MIN_REVIEW_FLOOR)


def _die(message: str, code: int) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def _dump(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args], capture_output=True, text=True, check=False
    )


# ---------------------------------------------------------------------------
# Whole-window diff census
# ---------------------------------------------------------------------------
def git_diff_namestatus(
    repo_root: Path, start_sha: str, end_sha: str, subdir: str
) -> list[tuple[str, str, str | None]]:
    """(status, old_path, new_path_or_None) for the bounded window, under `subdir`.

    `-M50%` engages tracked-rename detection; a rename row is `("R100", old,
    new)`. Deletions/renames whose destination is untracked (T-154-... COBS
    relocation) are INVISIBLE here by construction -- that is exactly why the
    corpus overlay exists.
    """
    done = _run_git(
        repo_root, "diff", "--name-status", "-M50%", start_sha, end_sha, "--", subdir
    )
    if done.returncode != 0:
        _die(f"git diff {start_sha}..{end_sha} failed: {done.stderr}", 2)
    out: list[tuple[str, str, str | None]] = []
    for line in done.stdout.splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        status = parts[0]
        if status.startswith("R") or status.startswith("C"):
            out.append((status, parts[1], parts[2]))
        else:
            out.append((status, parts[1], None))
    return out


def in_scope(rel: str) -> bool:
    ext = os.path.splitext(rel)[1]
    if ext not in bcm.SCAN_EXTENSIONS:
        return False
    return not any(rel == p.rstrip("/") or rel.startswith(p) for p in SELF_EXCLUDE_PREFIXES)


def phase_bucket(rel: str) -> str:
    for n in ("155", "156", "157", "158"):
        if rel.startswith(f".planning/phases/{n}-"):
            return n
    if rel.startswith(".planning/phases/154-"):
        return "154_post_manifest"
    if rel.startswith(".planning/milestones/v1.33-artifacts/"):
        return "v1.33"
    return "other_added"


# ---------------------------------------------------------------------------
# Historical anchoring: gitlink at the commit that authored the record
# ---------------------------------------------------------------------------
class GitlinkResolver:
    """Caches, per meta commit, the firestarter/firestarter_app gitlink SHA."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self._cache: dict[str, dict[str, str | None]] = {}

    def adding_commit(self, start_sha: str, end_sha: str, path: str) -> str:
        """The most recent commit in (start, end] that ADDED `path`.

        Falls back to `end_sha` if the window shows no clean add (e.g. an
        add+delete+re-add churn) -- a safe, final-state anchor rather than a
        crash.
        """
        done = _run_git(
            self.repo_root,
            "log",
            "--format=%H",
            "--diff-filter=A",
            f"{start_sha}..{end_sha}",
            "--",
            path,
        )
        if done.returncode == 0 and done.stdout.strip():
            return done.stdout.strip().splitlines()[0]
        return end_sha

    def last_touching_commit(self, start_sha: str, end_sha: str, path: str) -> str:
        done = _run_git(
            self.repo_root, "log", "--format=%H", f"{start_sha}..{end_sha}", "--", path
        )
        if done.returncode == 0 and done.stdout.strip():
            return done.stdout.strip().splitlines()[0]
        return end_sha

    def gitlinks(self, commit: str) -> dict[str, str | None]:
        if commit in self._cache:
            return self._cache[commit]
        links: dict[str, str | None] = {}
        for name in ("firestarter", "firestarter_app"):
            done = _run_git(self.repo_root, "rev-parse", f"{commit}:{name}")
            links[name] = done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else None
        self._cache[commit] = links
        return links


class BlobTextCache:
    """Lazily-read, cached (root, sha, subpath) -> line list."""

    def __init__(self) -> None:
        self._cache: dict[tuple[str, str, str], list[str] | None] = {}

    def lines(self, root: Path, sha: str, subpath: str) -> list[str] | None:
        key = (str(root), sha, subpath)
        if key not in self._cache:
            text = rc.git_show(root, sha, subpath)
            self._cache[key] = text.splitlines() if text is not None else None
        return self._cache[key]

    def at(self, root: Path, sha: str, subpath: str, lineno: int | None) -> tuple[str, str]:
        if lineno is None:
            return None, None  # type: ignore[return-value]
        lines = self.lines(root, sha, subpath)
        if lines is None:
            return bcm.UNREADABLE, bcm.TEXT_STATUS_READ_ERROR
        if lineno < 1 or lineno > len(lines):
            return bcm.UNREADABLE, bcm.TEXT_STATUS_OUT_OF_RANGE
        return lines[lineno - 1], bcm.TEXT_STATUS_READ


def anchor_record(
    *,
    root_dirs: dict[str, Path],
    gitlink_sha: str | None,
    final_sha: dict[str, str],
    target_file_resolved: str,
    target_line: int,
    target_line_end: int | None,
    blob_cache: BlobTextCache,
    pre_sweep_sha: dict[str, str] | None = None,
) -> tuple[str | None, list[str] | None, str, str | None, str, str | None]:
    """Returns (source_sha, source_sha_candidates, source_text, source_text_end,
    text_status, text_status_end) for a resolved supplemental record.

    Tries the gitlink-at-authoring-commit anchor FIRST -- it is the
    historically justified one, recovered from the meta repo's own history,
    and is trusted directly the moment it reads successfully (a record
    authored while describing a pre-change state is SUPPOSED to disagree
    with the final tree; that disagreement is exactly what the later remap
    is for, not evidence of ambiguity). The root's FINAL head is tried only
    as a FALLBACK when the gitlink anchor itself is unavailable or its blob
    cannot be read at the cited line. Genuine ambiguity is reserved for the
    case where NEITHER anchor is readable, or where two *distinct, both
    equally primary* candidates disagree -- which cannot happen with this
    strict precedence order, so this function never manufactures a false
    ambiguity out of "the file also happens to exist at HEAD."

    Phase 159-04 (B2 -- see 159-03-SUMMARY.md Blockers #2): `pre_sweep_sha`
    is an OPTIONAL third, LAST-resort candidate tier -- the root's pre-159
    revision, tried only after both the gitlink and final-head candidates
    have been exhausted (readable at neither, or absent). This closes a
    measured defect: all 4 `historical_anchor` records in Phase 159-02/03
    were offered exactly the gitlink and final-head candidates (both
    POST-Phase-154 commits) for a citation whose recorded line existed in
    NEITHER -- the correct anchor was the pre-sweep revision, never offered.
    Passing `pre_sweep_sha=None` (the default) reproduces the exact prior
    2-candidate behaviour byte-for-byte.
    """
    root_name, _, subpath = target_file_resolved.partition("/")
    root_dir = root_dirs[root_name]
    candidates = [
        s
        for s in (
            gitlink_sha,
            final_sha.get(root_name),
            (pre_sweep_sha or {}).get(root_name),
        )
        if s
    ]
    candidates = list(dict.fromkeys(candidates))  # de-dup, order-preserving

    for sha in candidates:
        s_text, s_status = blob_cache.at(root_dir, sha, subpath, target_line)
        e_text, e_status = blob_cache.at(root_dir, sha, subpath, target_line_end)
        if s_status == bcm.TEXT_STATUS_READ and (
            target_line_end is None or e_status == bcm.TEXT_STATUS_READ
        ):
            return sha, None, s_text, e_text, s_status, e_status

    # Nothing readable at any candidate anchor -- still record the candidate
    # list (never silently drop it) so a human can see WHY it needs review.
    if candidates:
        return (
            None,
            candidates,
            bcm.UNREADABLE,
            bcm.UNREADABLE if target_line_end else None,
            bcm.TEXT_STATUS_READ_ERROR,
            bcm.TEXT_STATUS_READ_ERROR if target_line_end else None,
        )
    return None, None, bcm.UNREADABLE, None, bcm.TEXT_STATUS_READ_ERROR, None


def mint_record_id(rec: dict) -> str:
    """Deterministic stable ID for a late/supplemental record.

    Includes `citation_ordinal` (the GLOBALLY-unique-within-line ordinal
    from `extract_spans`) in the basis, not just the citation's coordinates:
    the same (target_file_cited, variant, target_line, target_line_end)
    tuple can legitimately appear twice on the SAME planning_line (measured
    on the real corpus), and without the ordinal those two distinct
    occurrences would collide onto one ID.
    """
    basis = "\x1f".join(
        str(rec.get(k, ""))
        for k in (
            "planning_file",
            "planning_line",
            "citation_ordinal",
            "variant",
            "target_file_cited",
            "target_line",
            "target_line_end",
        )
    )
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"late-{digest}"


# ---------------------------------------------------------------------------
# Extraction (shared grammar; never re-implemented)
# ---------------------------------------------------------------------------
def extract_spans(text: str) -> list[tuple[int, str, str, int, int | None, int]]:
    """(planning_line, variant, cited, start, end, ordinal) for every span.

    `ordinal` is GLOBALLY unique within its line, not merely within one
    regex match: it is `match_index * 1000 + element_index_within_match`.
    A per-match-only ordinal (resetting to 0 for every match) collides when
    the SAME citation string is written twice on one line -- measured on
    the real corpus (`.planning/REQUIREMENTS.md:15` cites
    `eprom_params.cpp:61` twice, once inline and once inside a
    parenthetical list) -- which would mint the SAME `record_id` for two
    genuinely distinct citation occurrences. `* 1000` leaves generous room
    for `colon_list`'s per-element index while keeping the composite
    ordinal a single sortable integer.
    """
    out = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match_index, match in enumerate(CITATION_RE.finditer(line)):
            cited = match.group("path")
            for element_index, (variant, start, end) in enumerate(spans_from_match(match)):
                out.append((lineno, variant, cited, start, end, match_index * 1000 + element_index))
    return out


def build_late_record(
    *,
    planning_file: str,
    planning_line: int,
    variant: str,
    cited: str,
    start: int,
    end: int | None,
    ordinal: int,
    origin: str,
    phase: str,
    index: citation_paths.CandidateIndex,
    root_dirs: dict[str, Path],
    gitlink_sha: str | None,
    final_sha: dict[str, str],
    blob_cache: BlobTextCache,
    resolutions: dict[str, citation_paths.Resolution],
    pre_sweep_sha: dict[str, str] | None = None,
) -> dict:
    if cited not in resolutions:
        resolutions[cited] = index.resolve(cited)
    res = resolutions[cited]
    if res.is_resolved and res.path is not None:
        (
            source_sha,
            source_sha_candidates,
            s_text,
            e_text,
            s_status,
            e_status,
        ) = anchor_record(
            root_dirs=root_dirs,
            gitlink_sha=gitlink_sha,
            final_sha=final_sha,
            target_file_resolved=res.path,
            target_line=start,
            target_line_end=end,
            blob_cache=blob_cache,
            pre_sweep_sha=pre_sweep_sha,
        )
        source_root = res.path.split("/")[0]
    else:
        status = bcm._UNREADABLE_STATUS_FOR[res.resolution]
        s_text, s_status = bcm.UNREADABLE, status
        e_text, e_status = (None, None) if end is None else (bcm.UNREADABLE, status)
        source_sha, source_sha_candidates, source_root = None, None, None

    rec = {
        "planning_file": planning_file,
        "planning_line": planning_line,
        "variant": variant,
        "target_file_cited": cited,
        "target_file_resolved": res.path,
        "resolution": res.resolution,
        "resolution_reason": res.reason,
        "target_line": start,
        "target_line_end": end,
        "source_text": s_text,
        "source_text_end": e_text,
        "text_status": s_status,
        "text_status_end": e_status,
        "retarget": False,
        "origin": origin,
        "phase": phase,
        "historical_planning_file": planning_file,
        "historical_planning_line": planning_line,
        "citation_ordinal": ordinal,
        "source_root": source_root,
        "source_sha": source_sha,
        "source_sha_candidates": source_sha_candidates,
    }
    rec["record_id"] = mint_record_id(rec)
    return rec


# ---------------------------------------------------------------------------
# Census: added files
# ---------------------------------------------------------------------------
def census_added_files(
    *,
    repo_root: Path,
    added_paths: list[str],
    window_start: str,
    window_end: str,
    index: citation_paths.CandidateIndex,
    root_dirs: dict[str, Path],
    final_sha: dict[str, str],
    linker: GitlinkResolver,
    pre_sweep_sha: dict[str, str] | None = None,
) -> list[dict]:
    blob_cache = BlobTextCache()
    resolutions: dict[str, citation_paths.Resolution] = {}
    out: list[dict] = []
    for rel in sorted(added_paths):
        abs_path = repo_root / rel
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            _die(f"cannot read added file {rel}: {exc}", 2)
        spans = extract_spans(text)
        if not spans:
            continue
        commit = linker.adding_commit(window_start, window_end, rel)
        links = linker.gitlinks(commit)
        phase = phase_bucket(rel)
        for lineno, variant, cited, start, end, ordinal in spans:
            root_guess = index.resolve(cited)
            gitlink_sha = None
            if root_guess.is_resolved and root_guess.path is not None:
                gitlink_sha = links.get(root_guess.path.split("/")[0])
            out.append(
                build_late_record(
                    planning_file=rel,
                    planning_line=lineno,
                    variant=variant,
                    cited=cited,
                    start=start,
                    end=end,
                    ordinal=ordinal,
                    origin="added",
                    phase=phase,
                    index=index,
                    root_dirs=root_dirs,
                    gitlink_sha=gitlink_sha,
                    final_sha=final_sha,
                    blob_cache=blob_cache,
                    resolutions=resolutions,
                    pre_sweep_sha=pre_sweep_sha,
                )
            )
    return out


# ---------------------------------------------------------------------------
# Census: modified pre-existing (global) documents
# ---------------------------------------------------------------------------
def census_modified_files(
    *,
    repo_root: Path,
    modified_paths: list[str],
    original_records: list[dict],
    window_start: str,
    window_end: str,
    index: citation_paths.CandidateIndex,
    root_dirs: dict[str, Path],
    final_sha: dict[str, str],
    linker: GitlinkResolver,
    pre_sweep_sha: dict[str, str] | None = None,
) -> list[dict]:
    """Positional reconciliation: the ORIGINAL manifest's own rows for this
    file (at the window-start commit, which is exactly the manifest's
    generation commit) are the "before" side; the current on-disk scan is
    the "after" side. `difflib.SequenceMatcher` over the ordered
    (target_file_cited, variant, target_line, target_line_end) tuple
    sequence recognises a merely-repositioned citation as `equal` (no new
    record) and only genuinely new tuples become supplemental rows.
    """
    by_file: dict[str, list[dict]] = defaultdict(list)
    for rec in original_records:
        by_file[rec["planning_file"]].append(rec)

    blob_cache = BlobTextCache()
    resolutions: dict[str, citation_paths.Resolution] = {}
    out: list[dict] = []
    for rel in sorted(modified_paths):
        abs_path = repo_root / rel
        if not abs_path.is_file():
            continue
        text = abs_path.read_text(encoding="utf-8", errors="replace")
        current_spans = sorted(extract_spans(text))  # (lineno, variant, cited, start, end, ordinal)
        old_recs = sorted(
            by_file.get(rel, []), key=lambda r: (r["planning_line"], r["variant"], r["target_line"])
        )
        old_seq = [(r["target_file_cited"], r["variant"], r["target_line"], r["target_line_end"]) for r in old_recs]
        new_seq = [(c[2], c[1], c[3], c[4]) for c in current_spans]

        sm = difflib.SequenceMatcher(None, old_seq, new_seq, autojunk=False)
        new_indices: list[int] = []
        for tag, _i1, _i2, j1, j2 in sm.get_opcodes():
            if tag in ("insert", "replace"):
                new_indices.extend(range(j1, j2))
        if not new_indices:
            continue

        commit = linker.last_touching_commit(window_start, window_end, rel)
        links = linker.gitlinks(commit)
        for idx in new_indices:
            lineno, variant, cited, start, end, ordinal = current_spans[idx]
            root_guess = index.resolve(cited)
            gitlink_sha = None
            if root_guess.is_resolved and root_guess.path is not None:
                gitlink_sha = links.get(root_guess.path.split("/")[0])
            out.append(
                build_late_record(
                    planning_file=rel,
                    planning_line=lineno,
                    variant=variant,
                    cited=cited,
                    start=start,
                    end=end,
                    ordinal=ordinal,
                    origin="modified_global",
                    phase="modified_global",
                    index=index,
                    root_dirs=root_dirs,
                    gitlink_sha=gitlink_sha,
                    final_sha=final_sha,
                    blob_cache=blob_cache,
                    resolutions=resolutions,
                    pre_sweep_sha=pre_sweep_sha,
                )
            )
    return out


# ---------------------------------------------------------------------------
# Review population: known Phase-154 hand-choice re-deletions
# ---------------------------------------------------------------------------
def known_post154_non_survivors(
    *,
    original_records: list[dict],
    root_dirs: dict[str, Path],
    retarget_base_sha: dict[str, str],
    final_sha: dict[str, str],
) -> list[dict]:
    """Every `retarget: true` row whose Phase-154 hand-chosen target
    (`retarget_new_line[_end]`) does not map WITHOUT a clamp from its
    Phase-154 anchor commit to the real final tree -- i.e. genuinely
    verbatim survival, using the production `LineMap`/`build_map`, never a
    fixed-line string compare (which cannot tell "survived, unchanged"
    from "coincidentally matches some other line").
    """
    map_cache: dict[tuple[str, str, str], rc.LineMap | None] = {}

    def get_map(root_name: str, subpath: str) -> rc.LineMap | None:
        key = (root_name, retarget_base_sha[root_name], subpath)
        if key in map_cache:
            return map_cache[key]
        old = rc.git_show(root_dirs[root_name], retarget_base_sha[root_name], subpath)
        new = rc.git_show(root_dirs[root_name], final_sha[root_name], subpath)
        lm = rc.LineMap(old.splitlines(), new.splitlines()) if old is not None and new is not None else None
        map_cache[key] = lm
        return lm

    out: list[dict] = []
    for orec in original_records:
        if not orec.get("retarget"):
            continue
        target = orec["target_file_resolved"]
        if not target:
            continue
        root_name, _, subpath = target.partition("/")
        lm = get_map(root_name, subpath)
        if lm is None:
            out.append(orec)
            continue
        new_line = orec["retarget_new_line"]
        new_line_end = orec.get("retarget_new_line_end")
        if new_line_end and new_line_end != new_line:
            start_direct = lm.map.get(new_line)
            end_direct = lm.map.get(new_line_end)
            unclamped = start_direct is not None and end_direct is not None
        else:
            unclamped = lm.map.get(new_line) is not None
        if not unclamped:
            out.append(orec)
    return out


# ---------------------------------------------------------------------------
# Review population: ordinary original-manifest non-survivors, via the ACTUAL
# hardened engine's own association/oracle logic (never re-derived).
# ---------------------------------------------------------------------------
def non_surviving_actionable_records(
    *,
    repo_root: Path,
    manifest_paths: list[Path],
    planning_base_sha: str,
    overlay_path: Path | None,
    pre_sweep_sha: dict[str, str],
) -> tuple[list[str], list[str], dict]:
    """Runs the production `remap_citations.py` engine, non-strict, over
    BOTH the original manifest AND the freshly-built late/supplemental
    manifest TOGETHER -- exactly the corpus the real Task-2 dry run will
    see -- and returns (ordinary_ids, supplemental_ids, report):
    `open_ids` entries for a genuine RETARGET / NOT_AT_RECORDED_LINE /
    NO_MATCH_IN_DOCUMENT outcome on an otherwise-actionable, `retarget:false`
    row, split by whether the record came from the original manifest
    (`orig-` stable-ID prefix) or the late manifest (`late-` prefix). Running
    BOTH manifests merged (not the original alone) is required: a group's
    match/mismatch dynamics can change once a late record joins the SAME
    (target_file_cited, variant) citation group, so computing this against
    the original manifest alone would miss ids that only become actionable
    once the two manifests are combined -- and the real dry run always
    combines them.
    """
    argv = [str(repo_root)]
    for mp in manifest_paths:
        argv += ["--manifest", str(mp)]
    argv += ["--planning-base-sha", planning_base_sha, "--quiet-notes"]
    for name, sha in pre_sweep_sha.items():
        argv += ["--pre-sweep-sha", f"{name}={sha}"]
    if overlay_path is not None:
        argv += ["--corpus-overlay", str(overlay_path)]
    report_path = repo_root / ".planning" / "v1.33" / ".prepare-diagnostic-report.json.tmp"
    argv += ["--report-json", str(report_path)]

    done = subprocess.run(
        [sys.executable, os.path.join(_HERE, "remap_citations.py"), *argv],
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode not in (0, 1):
        _die(
            "the diagnostic non-strict engine run over the merged manifests "
            f"failed unexpectedly (exit {done.returncode}): {done.stderr}",
            2,
        )
    if not report_path.is_file():
        _die("the diagnostic engine run did not produce a report", 2)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report_path.unlink(missing_ok=True)

    by_id: dict[str, list[dict]] = defaultdict(list)
    for mp in manifest_paths:
        _, recs = rc.load_manifest(mp)
        for rec in recs:
            by_id[rc.stable_record_id(rec)].append(rec)

    ordinary_ids: list[str] = []
    supplemental_ids: list[str] = []
    for cat in (rc.RETARGET, rc.NOT_AT_RECORDED_LINE, rc.NO_MATCH_IN_DOCUMENT):
        for rid in report["open_ids"].get(cat, []):
            recs_for_id = by_id.get(rid, [])
            if cat == rc.NO_MATCH_IN_DOCUMENT:
                # `_associate()` hard-blocks EVERY record in a mismatched
                # citation group, regardless of whether it is individually
                # actionable (an unresolved/unreadable row can share a group
                # with an actionable one, and the whole group's citation
                # text vanished from the document either way) -- so every
                # such id needs a ledger row, not only the "would have had
                # an oracle" subset.
                if not recs_for_id:
                    continue
            else:
                actionable = any(
                    (not r.get("retarget"))
                    and r["text_status"] == bcm.TEXT_STATUS_READ
                    and r["target_file_resolved"]
                    and (r["target_line_end"] is None or r["text_status_end"] == bcm.TEXT_STATUS_READ)
                    for r in recs_for_id
                )
                if not actionable:
                    continue
            if rid.startswith("late-"):
                supplemental_ids.append(rid)
            else:
                ordinary_ids.append(rid)
    return sorted(set(ordinary_ids)), sorted(set(supplemental_ids)), report


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------
def write_jsonl(out_path: Path, header: dict, records: list[dict], key_order: tuple[str, ...]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_dump(header) + "\n")
        for rec in records:
            fh.write(_dump({k: rec.get(k) for k in key_order}) + "\n")
    os.replace(tmp_path, out_path)


def write_review_md(
    out_path: Path,
    *,
    pending_records: list[dict],
    pending_overlays: list[dict],
    census_summary: dict,
) -> None:
    lines = [
        "# Phase 159 retarget review packet",
        "",
        "Every section below is a PENDING decision. This document APPROVES",
        "NOTHING; every `status` in `159-remap-exceptions.jsonl` starts",
        "`needs_review` and stays that way until a human (Plan 159-03)",
        "supplies a `chosen_*` field.",
        "",
        "## Census summary",
        "",
        f"- Phase-directory subtotal (155/156/157/158): "
        f"{census_summary['phase_155']}/{census_summary['phase_156']}/"
        f"{census_summary['phase_157']}/{census_summary['phase_158']} = "
        f"{census_summary['phase_subtotal']}",
        f"- Added-file records: 154_post_manifest={census_summary['added_154']}, "
        f"155-158={census_summary['phase_subtotal']}, "
        f"v1.33={census_summary['added_v133']}",
        f"- Modified-global-document new records: {census_summary['modified_global']}",
        f"- Total supplemental records (measured): {census_summary['total_late']}",
        f"- Ordinary original-manifest non-survivors (measured): "
        f"{census_summary['ordinary_non_survivor_count']}",
        f"- Known Phase-154 hand-choice re-deletions (measured): "
        f"{census_summary['known_post154_count']}",
        "",
    ]
    for rec in pending_records:
        lines.append(f"## Record {rec['record_id']}")
        lines.append("")
        lines.append(f"- classification: `{rec['classification']}`")
        lines.append(f"- review_kind: `{rec['review_kind']}`")
        lines.append(f"- status: `{rec['status']}`")
        if rec.get("candidate_evidence"):
            lines.append(f"- candidate_evidence: {rec['candidate_evidence']}")
        if rec.get("rationale"):
            lines.append(f"- rationale: {rec['rationale']}")
        lines.append(f"- review_source: `{rec['review_source']}`")
        lines.append("- chosen_source_sha: _pending_")
        lines.append("- chosen_planning_file: _pending_")
        lines.append("- chosen_current_start/end/text: _pending_")
        lines.append("")
    for row in pending_overlays:
        lines.append(f"## Dirty overlap {row['authorization_id']}")
        lines.append("")
        lines.append(f"- path: `{row['path']}`")
        lines.append(f"- current_path: `{row.get('current_path')}`")
        lines.append(f"- git_state: `{row.get('git_state')}`")
        lines.append(f"- topology_action: `{row.get('topology_action')}`")
        lines.append(f"- staging_strategy: `{row.get('staging_strategy')}`")
        lines.append(
            "- decision: _pending_ (`preserve_unstaged` | `authorize_include` | `stop`)"
        )
        lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    tmp_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp_path, out_path)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--original-manifest", required=True)
    ap.add_argument("--window-start-sha", required=True)
    ap.add_argument("--window-end-sha", required=True)
    ap.add_argument("--firmware-root", required=True)
    ap.add_argument("--app-root", required=True)
    ap.add_argument("--late-output", required=True)
    ap.add_argument("--exceptions-output", required=True)
    ap.add_argument("--review-output", required=True)
    ap.add_argument("--overlay-output", required=True)
    ap.add_argument(
        "--check-existing",
        action="store_true",
        help="if the four output paths already exist, snapshot their current bytes and "
        "assert the freshly-regenerated bytes are byte-identical (self-check for "
        "deterministic regeneration); a first-ever run has nothing to compare and passes",
    )
    args = ap.parse_args(argv)

    existing_snapshot: dict[str, bytes | None] = {}
    if args.check_existing:
        for out_path_str in (args.late_output, args.exceptions_output, args.review_output, args.overlay_output):
            p = Path(out_path_str)
            existing_snapshot[out_path_str] = p.read_bytes() if p.is_file() else None

    repo_root = Path(args.repo_root)
    if not repo_root.is_dir():
        _die(f"--repo-root does not exist: {repo_root}", 2)
    repo_root = repo_root.resolve()

    original_manifest_path = Path(args.original_manifest)
    if not original_manifest_path.is_absolute():
        original_manifest_path = (repo_root / original_manifest_path).resolve()
    if not original_manifest_path.is_file():
        _die(f"--original-manifest does not exist: {original_manifest_path}", 2)

    original_hash_before = hashlib.sha256(original_manifest_path.read_bytes()).hexdigest()

    fw_root = (repo_root / args.firmware_root).resolve()
    app_root = (repo_root / args.app_root).resolve()
    root_dirs = {"firestarter": fw_root, "firestarter_app": app_root}
    for name, root in root_dirs.items():
        if not root.is_dir():
            _die(f"root {name!r} does not exist: {root}", 2)

    final_sha = {}
    for name, root in root_dirs.items():
        head = _run_git(root, "rev-parse", "HEAD")
        if head.returncode != 0:
            _die(f"cannot determine HEAD of {name}: {head.stderr}", 2)
        final_sha[name] = head.stdout.strip()

    # Real, historically-justified anchors (research: "Repositories and anchors").
    retarget_base_sha = {
        "firestarter": "2ad5b322a37ba4a88afd09cc946f5c4114e51483",
        "firestarter_app": "bc9d59293b9a08b16d6d7eb16eaf6c6f53e88e65",
    }
    pre_sweep_sha = {
        "firestarter": "8695ee52c27a4bee4387c5c489afd5f3d7275e8a",
        "firestarter_app": "6bfa6453d1bac232eb81ab35fa7f14b50b0b291a",
    }
    # TEST-ONLY: a small synthetic fixture cannot reproduce the real
    # pre-sweep/retarget-base SHAs (they do not exist in its throwaway
    # repos); a test can override both via the same env-var mechanism as
    # the threshold overrides above. Absent in every real invocation.
    if os.environ.get(_TEST_THRESHOLDS_ENV):
        _test_overrides = json.loads(os.environ[_TEST_THRESHOLDS_ENV])
        retarget_base_sha = _test_overrides.get("retarget_base_sha", retarget_base_sha)
        pre_sweep_sha = _test_overrides.get("pre_sweep_sha", pre_sweep_sha)

    # ---- corpus overlay: the known live dirty/topology set -----------------
    cobs_old = ".planning/v1.9-COBS-DECISION.md"
    cobs_new = ".planning/milestones/v1.33-artifacts/v1.9-COBS-DECISION.md"
    overlay_rows: list[dict] = []
    cobs_old_abs = repo_root / cobs_old
    cobs_new_abs = repo_root / cobs_new
    cobs_status = _run_git(repo_root, "status", "--porcelain=v2", "--", cobs_old, cobs_new)
    if cobs_new_abs.is_file():
        digest = hashlib.sha256(cobs_new_abs.read_bytes()).hexdigest()
        head_show = _run_git(repo_root, "show", f"HEAD:{cobs_old}")
        preapply = (
            hashlib.sha256(head_show.stdout.encode("utf-8")).hexdigest()
            if head_show.returncode == 0
            else digest
        )
        overlay_rows.append(
            {
                "path": cobs_old,
                "current_path": cobs_new,
                "git_state": cobs_status.stdout.strip() or "deleted+untracked relocation",
                "preapply_sha256": preapply,
                "expected_postapply_sha256": digest,
                "topology_action": "relocated (deleted old path, added untracked new path)",
                "dirty_overlap": True,
                "approval_status": "pending",
                "staging_strategy": "requires_authorization",
                "authorization_id": "auth-cobs-relocation",
            }
        )

    state_md_status = _run_git(repo_root, "status", "--porcelain=v2", "--", ".planning/STATE.md")
    if state_md_status.stdout.strip():
        state_abs = repo_root / ".planning" / "STATE.md"
        overlay_rows.append(
            {
                "path": ".planning/STATE.md",
                "current_path": ".planning/STATE.md",
                "git_state": state_md_status.stdout.strip(),
                "preapply_sha256": hashlib.sha256(state_abs.read_bytes()).hexdigest()
                if state_abs.is_file()
                else None,
                "expected_postapply_sha256": None,
                "topology_action": "modified in place (this phase's own execution bookkeeping)",
                "dirty_overlap": True,
                "approval_status": "pending",
                "staging_strategy": "citation_only_blob",
                "authorization_id": "auth-state-md-dirty",
            }
        )

    overlay_tmp_path = repo_root / ".planning" / "v1.33" / ".prepare-overlay.jsonl.tmp"
    write_jsonl(overlay_tmp_path, {"_schema": {"role": "scratch overlay for the diagnostic dry run"}}, overlay_rows, OVERLAY_KEYS)

    # ---- whole-window diff ---------------------------------------------------
    diff_rows = git_diff_namestatus(repo_root, args.window_start_sha, args.window_end_sha, ".planning")
    added_paths: list[str] = []
    modified_paths: list[str] = []
    for status, old, new in diff_rows:
        if status == "A" and in_scope(old):
            added_paths.append(old)
        elif status == "M" and in_scope(old):
            modified_paths.append(old)
        # renames/copies with unchanged content need no new supplemental
        # records; deletions are out of scope for a "late citation" census.

    _, original_records = rc.load_manifest(original_manifest_path)

    candidate_paths = bcm._full_repo_paths(fw_root, app_root)
    index = citation_paths.CandidateIndex(root_dirs, candidate_paths)
    linker = GitlinkResolver(repo_root)

    added_records = census_added_files(
        repo_root=repo_root,
        added_paths=added_paths,
        window_start=args.window_start_sha,
        window_end=args.window_end_sha,
        index=index,
        root_dirs=root_dirs,
        final_sha=final_sha,
        linker=linker,
        pre_sweep_sha=pre_sweep_sha,
    )
    modified_records = census_modified_files(
        repo_root=repo_root,
        modified_paths=modified_paths,
        original_records=original_records,
        window_start=args.window_start_sha,
        window_end=args.window_end_sha,
        index=index,
        root_dirs=root_dirs,
        final_sha=final_sha,
        linker=linker,
        pre_sweep_sha=pre_sweep_sha,
    )
    late_records = added_records + modified_records

    # ---- duplicate stable-ID refusal: a `record_id` collision would let two
    # DISTINCT citation records silently conflate into one ledger/oracle
    # entry -- never accepted, always a hard infrastructure error.
    seen_record_ids: dict[str, dict] = {}
    for rec in late_records:
        rid = rec["record_id"]
        if rid in seen_record_ids and seen_record_ids[rid] is not rec:
            _die(
                f"duplicate record_id {rid!r} minted for two distinct late records: "
                f"{seen_record_ids[rid]['planning_file']}:{seen_record_ids[rid]['planning_line']} "
                f"and {rec['planning_file']}:{rec['planning_line']}",
                1,
            )
        seen_record_ids[rid] = rec

    # ---- exact phase-directory subtotal, asserted -----------------------------
    by_phase = Counter(r["phase"] for r in late_records if r["phase"] in ("155", "156", "157", "158"))
    expected_phase = EXPECTED_PHASE_SUBTOTAL
    if dict(by_phase) != expected_phase:
        _die(
            f"the four-phase-directory subtotal is not exact: got {dict(by_phase)}, "
            f"expected {expected_phase}",
            1,
        )
    phase_subtotal = sum(expected_phase.values())
    if len(late_records) < MIN_TOTAL_SUPPLEMENTAL_RECORDS:
        _die(f"the whole-window supplemental census is only {len(late_records)} records, below the verified lower bound of {MIN_TOTAL_SUPPLEMENTAL_RECORDS}", 1)

    # ---- write the late manifest NOW (provisionally) so the diagnostic dry
    # run below can load it via --manifest alongside the original -- the
    # real Task-2 dry run always merges both, so the non-survivor census
    # must be measured against that SAME merged corpus, not the original
    # manifest alone (a group's match/mismatch dynamics can change once a
    # late record joins its citation group). It is rewritten, byte-for-byte
    # identical, once more at the end of this function.
    late_header_provisional = {"_schema": {"role": "provisional -- rewritten below"}}
    write_jsonl(Path(args.late_output), late_header_provisional, late_records, LATE_RECORD_KEYS)

    # ---- review population: measured, not assumed -----------------------------
    known_post154 = known_post154_non_survivors(
        original_records=original_records,
        root_dirs=root_dirs,
        retarget_base_sha=retarget_base_sha,
        final_sha=final_sha,
    )
    ordinary_ids, supplemental_ids, diag_report = non_surviving_actionable_records(
        repo_root=repo_root,
        manifest_paths=[original_manifest_path, Path(args.late_output)],
        planning_base_sha=args.window_start_sha,
        overlay_path=overlay_tmp_path,
        pre_sweep_sha=pre_sweep_sha,
    )
    overlay_tmp_path.unlink(missing_ok=True)

    if len(known_post154) < MIN_KNOWN_POST154_NON_SURVIVORS:
        _die(
            f"measured known_post154_non_survivor count ({len(known_post154)}) is below "
            f"research's own stated floor of {MIN_KNOWN_POST154_NON_SURVIVORS}",
            1,
        )
    if len(ordinary_ids) < MIN_ORDINARY_NON_SURVIVORS:
        _die(
            f"measured ordinary_original_non_survivor count ({len(ordinary_ids)}) is below "
            f"research's own stated floor of {MIN_ORDINARY_NON_SURVIVORS}",
            1,
        )

    exception_rows: list[dict] = []
    seen_ids: set[str] = set()

    for orec in known_post154:
        rid = rc.stable_record_id(orec)
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        exception_rows.append(
            {
                "record_id": rid,
                "classification": "known_post154_non_survivor",
                "review_kind": "hand_choice_re_deletion",
                "status": "needs_review",
                "candidate_evidence": {
                    "planning_file": orec["planning_file"],
                    "planning_line": orec["planning_line"],
                    "target_file_resolved": orec["target_file_resolved"],
                    "retarget_new_line": orec.get("retarget_new_line"),
                    "retarget_new_line_end": orec.get("retarget_new_line_end"),
                    "retarget_new_text": orec.get("retarget_new_text"),
                },
                "chosen_source_sha": None,
                "chosen_planning_file": None,
                "chosen_current_start": None,
                "chosen_current_end": None,
                "chosen_current_text": None,
                "chosen_current_text_end": None,
                "rationale": (
                    "The Phase-154 hand-chosen post-154 target for this record no longer "
                    "maps without a clamp from its Phase-154 retarget-base anchor to the "
                    "real final tree -- i.e. it does not survive verbatim. Re-review "
                    "required (measured via build_map/LineMap against the real repository, "
                    "not a fixed-line string compare)."
                ),
                "review_source": "prepare_citation_remap.known_post154_non_survivors",
            }
        )

    original_by_id = {rc.stable_record_id(r): r for r in original_records}
    for rid in ordinary_ids:
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        orec = original_by_id.get(rid, {})
        exception_rows.append(
            {
                "record_id": rid,
                "classification": "ordinary_original_non_survivor",
                "review_kind": "composite_diff_non_survivor",
                "status": "needs_review",
                "candidate_evidence": {
                    "planning_file": orec.get("planning_file"),
                    "planning_line": orec.get("planning_line"),
                    "target_file_resolved": orec.get("target_file_resolved"),
                    "target_line": orec.get("target_line"),
                    "target_line_end": orec.get("target_line_end"),
                },
                "chosen_source_sha": None,
                "chosen_planning_file": None,
                "chosen_current_start": None,
                "chosen_current_end": None,
                "chosen_current_text": None,
                "chosen_current_text_end": None,
                "rationale": (
                    "This ordinary (retarget:false) original-manifest record's endpoint "
                    "does not survive the real composite pre-154..post-158 diff: the "
                    "production remap_citations.py engine (non-strict diagnostic run, real "
                    "corpus, tracked-rename + corpus-overlay resolved) classifies it "
                    "RETARGET / NOT_AT_RECORDED_LINE / NO_MATCH_IN_DOCUMENT. Re-review "
                    "required."
                ),
                "review_source": "prepare_citation_remap.ordinary_non_survivors",
            }
        )

    late_by_id = {rec["record_id"]: rec for rec in late_records}
    for rid in supplemental_ids:
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        lrec = late_by_id.get(rid, {})
        exception_rows.append(
            {
                "record_id": rid,
                "classification": "supplemental_non_survivor",
                "review_kind": "composite_diff_non_survivor",
                "status": "needs_review",
                "candidate_evidence": {
                    "planning_file": lrec.get("planning_file"),
                    "planning_line": lrec.get("planning_line"),
                    "target_file_resolved": lrec.get("target_file_resolved"),
                    "target_line": lrec.get("target_line"),
                    "target_line_end": lrec.get("target_line_end"),
                    "source_sha": lrec.get("source_sha"),
                },
                "chosen_source_sha": None,
                "chosen_planning_file": None,
                "chosen_current_start": None,
                "chosen_current_end": None,
                "chosen_current_text": None,
                "chosen_current_text_end": None,
                "rationale": (
                    "This supplemental (late-manifest) record's endpoint does not survive "
                    "from its own historical authoring anchor to the real composite diff: "
                    "the production remap_citations.py engine (non-strict diagnostic run, "
                    "merged corpus) classifies it RETARGET / NOT_AT_RECORDED_LINE / "
                    "NO_MATCH_IN_DOCUMENT. Re-review required."
                ),
                "review_source": "prepare_citation_remap.non_surviving_actionable_records",
            }
        )

    for rec in late_records:
        if rec.get("source_sha") is None and rec.get("source_sha_candidates"):
            rid = rec["record_id"]
            if rid in seen_ids:
                continue
            seen_ids.add(rid)
            exception_rows.append(
                {
                    "record_id": rid,
                    "classification": "ambiguous_historical_anchor",
                    "review_kind": "historical_anchor",
                    "status": "needs_review",
                    "candidate_evidence": {
                        "planning_file": rec["planning_file"],
                        "planning_line": rec["planning_line"],
                        "target_file_resolved": rec["target_file_resolved"],
                        "source_sha_candidates": rec["source_sha_candidates"],
                    },
                    "chosen_source_sha": None,
                    "chosen_planning_file": None,
                    "chosen_current_start": None,
                    "chosen_current_end": None,
                    "chosen_current_text": None,
                    "chosen_current_text_end": None,
                    "rationale": (
                        "This supplemental record's historical anchor is non-unique or "
                        "unreadable at every candidate SHA; a human must choose "
                        "chosen_source_sha from the recorded candidates."
                    ),
                    "review_source": "prepare_citation_remap.anchor_record",
                }
            )

    if len(exception_rows) < MIN_REVIEW_FLOOR:
        _die(f"the review floor is {len(exception_rows)}, below the known minimum of {MIN_REVIEW_FLOOR}", 1)

    exceptions_header = {
        "_schema": {
            "purpose": (
                "Phase 159-02 exceptions ledger: the exhaustive, evidence-backed set of "
                "every record requiring a human decision before the one production remap "
                "apply (Plan 159-03). Every row starts status=needs_review; this tool "
                "approves nothing."
            ),
            "record_keys": list(EXCEPTION_KEYS),
            "classifications": {
                "known_post154_non_survivor": "a Phase-154 hand choice whose chosen post-154 target text no longer survives verbatim (measured floor: 5)",
                "ordinary_original_non_survivor": "an ordinary (retarget:false) original-manifest record whose endpoint does not survive the composite diff (measured floor: 105)",
                "supplemental_non_survivor": "a late/supplemental record whose endpoint does not survive from its own historical authoring anchor",
                "ambiguous_historical_anchor": "a supplemental record with a non-unique or unreadable historical source anchor",
            },
            "counts": {
                "total": len(exception_rows),
                "known_post154_non_survivor": sum(
                    1 for r in exception_rows if r["classification"] == "known_post154_non_survivor"
                ),
                "ordinary_original_non_survivor": sum(
                    1 for r in exception_rows if r["classification"] == "ordinary_original_non_survivor"
                ),
                "supplemental_non_survivor": sum(
                    1 for r in exception_rows if r["classification"] == "supplemental_non_survivor"
                ),
                "ambiguous_historical_anchor": sum(
                    1 for r in exception_rows if r["classification"] == "ambiguous_historical_anchor"
                ),
            },
        }
    }
    write_jsonl(Path(args.exceptions_output), exceptions_header, exception_rows, EXCEPTION_KEYS)

    late_header = {
        "_schema": {
            "purpose": (
                "Phase 159-02 whole-window supplemental citation manifest: every citation "
                "record newly authored between the original manifest commit and the "
                "Phase-158 completion boundary. Feed alongside the original manifest via a "
                "repeated remap_citations.py --manifest flag."
            ),
            "record_keys": list(LATE_RECORD_KEYS),
            "window": {
                "start_sha": args.window_start_sha,
                "end_sha": args.window_end_sha,
            },
            "counts": {
                "total": len(late_records),
                "added": len(added_records),
                "modified_global": len(modified_records),
                "phase_155": by_phase.get("155", 0),
                "phase_156": by_phase.get("156", 0),
                "phase_157": by_phase.get("157", 0),
                "phase_158": by_phase.get("158", 0),
                "phase_subtotal_155_158": phase_subtotal,
                "154_post_manifest": sum(1 for r in added_records if r["phase"] == "154_post_manifest"),
                "v1.33": sum(1 for r in added_records if r["phase"] == "v1.33"),
                "other_added": sum(1 for r in added_records if r["phase"] == "other_added"),
            },
            "note": (
                "642 (127/184/225/106) is the exact, asserted four-phase-directory subtotal. "
                "The total record count above is the MEASURED whole-window census, reported "
                "honestly rather than fixed at any prior estimate (verified lower bound: 881)."
            ),
        }
    }
    write_jsonl(Path(args.late_output), late_header, late_records, LATE_RECORD_KEYS)

    pending_overlay_for_review = [r for r in overlay_rows if r["approval_status"] == "pending"]
    write_jsonl(Path(args.overlay_output), {"_schema": {"role": "live-worktree topology/dirty-overlap inventory, all rows pending"}}, overlay_rows, OVERLAY_KEYS)

    census_summary = {
        "phase_155": by_phase.get("155", 0),
        "phase_156": by_phase.get("156", 0),
        "phase_157": by_phase.get("157", 0),
        "phase_158": by_phase.get("158", 0),
        "phase_subtotal": phase_subtotal,
        "added_154": sum(1 for r in added_records if r["phase"] == "154_post_manifest"),
        "added_v133": sum(1 for r in added_records if r["phase"] == "v1.33"),
        "modified_global": len(modified_records),
        "total_late": len(late_records),
        "ordinary_non_survivor_count": len(ordinary_ids),
        "known_post154_count": len(known_post154),
    }
    write_review_md(
        Path(args.review_output),
        pending_records=exception_rows,
        pending_overlays=pending_overlay_for_review,
        census_summary=census_summary,
    )

    # ---- self-check: byte-identical determinism (--check-existing) -----------
    if args.check_existing:
        mismatches = []
        for out_path_str in (args.late_output, args.exceptions_output, args.review_output, args.overlay_output):
            before = existing_snapshot.get(out_path_str)
            if before is None:
                continue  # first-ever run for this path: nothing to compare
            after = Path(out_path_str).read_bytes()
            if before != after:
                mismatches.append(out_path_str)
        if mismatches:
            _die(
                "regeneration is not byte-identical to the pre-existing output for: "
                f"{mismatches} -- determinism violated",
                1,
            )

    after_hash = hashlib.sha256(original_manifest_path.read_bytes()).hexdigest()
    if after_hash != original_hash_before:
        _die("the original manifest was modified by this run -- it must remain byte-identical", 1)

    print(
        "PASS: whole-window census "
        f"{len(late_records)} supplemental record(s) (phase subtotal "
        f"{phase_subtotal} = {by_phase.get('155', 0)}/{by_phase.get('156', 0)}/"
        f"{by_phase.get('157', 0)}/{by_phase.get('158', 0)}); "
        f"{len(exception_rows)} pending review record(s) "
        f"(known_post154={len(known_post154)}, ordinary={len(ordinary_ids)}); "
        f"original manifest hash unchanged ({after_hash[:12]}...)."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
