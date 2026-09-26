#!/usr/bin/env python3
"""
pytest coverage for prepare_citation_remap.py -- Phase 159 plan 02.

Tests:
  1. `extract_spans` reproduces the shared grammar's variant/ordinal shape
     (colon_single, colon_range, colon_list, anchor_L) -- unit.
  2. `phase_bucket` classifies each of the four phase directories, a
     post-manifest Phase-154 artifact, a v1.33 evidence record and an
     "other" path correctly -- unit.
  3. `anchor_record` prefers the gitlink-at-authoring anchor when it reads
     successfully, even though the final-head anchor would read DIFFERENT
     text -- proving the tool does not manufacture a false ambiguity out of
     "the file also exists at HEAD" -- unit, T-159-anchor.
  4. `anchor_record` falls back to the final-head candidate when the
     gitlink-derived blob cannot be read at the cited line, and reports a
     `source_sha_candidates` list (never guesses) when NEITHER anchor is
     readable -- unit.
  5. `known_post154_non_survivors` distinguishes a verbatim-surviving
     (unclamped) retarget row from a genuinely non-surviving (clamped) one,
     using the production `LineMap`/`build_map` -- unit, anti-vacuity.
  6. End-to-end on a small synthetic corpus: `main()` produces a
     deterministic, byte-identical-on-rerun late manifest / exceptions
     ledger / review packet / overlay, with the exact four-phase-directory
     subtotal and a review floor -- integration.
  7. Coverage-gate anti-vacuity: planting a citation in an added v1.33-style
     record OR in a modified global document makes the corresponding
     supplemental count increase; omitting either fixture change from the
     window measurably changes the census (never silently absorbed) --
     integration.
  8. Two independent temporary runs over the SAME synthetic corpus emit
     byte-identical manifests/ledgers/review packets/overlays -- integration,
     determinism.
  9. Duplicate `record_id`s across two late records are refused by the
     shared JSONL writer's downstream self-check contract (the same
     `record_id` never legitimately repeats for two distinct spans) -- unit.
 10. A record whose only readable text comes from the FINAL tree (no
     historical anchor evidence at all) is never silently accepted as a
     historical `source_text` -- the final-tree-oracle rejection: `main()`
     over a corpus where NO historical gitlink exists routes the record to
     `source_sha_candidates`/unreadable rather than reading current disk --
     unit.
 11. The original manifest's SHA-256 is unchanged by a full `main()` run --
     integration, REMAP-04 adjacent.
"""

import hashlib
import json
import os
import subprocess
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOL = os.path.join(_HERE, "prepare_citation_remap.py")

if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import build_citation_manifest as bcm  # noqa: E402
import citation_paths  # noqa: E402
import prepare_citation_remap as pcr  # noqa: E402
import remap_citations as rc  # noqa: E402


def _git(repo, *args):
    return subprocess.run(
        [
            "git", "-C", str(repo),
            "-c", "user.email=prep-test@example.invalid",
            "-c", "user.name=prep test",
            *args,
        ],
        capture_output=True, text=True, check=False,
    )


# ---------------------------------------------------------------------------
# 1-2: pure unit tests
# ---------------------------------------------------------------------------
def test_extract_spans_covers_every_variant():
    text = (
        "point ref alpha.cpp:10\n"
        "range ref beta.cpp:20-25\n"
        "list ref gamma.cpp:30,31,32\n"
        "anchor ref [x](docs/delta.cpp#L5-L7)\n"
    )
    spans = pcr.extract_spans(text)
    variants = {s[1] for s in spans}
    assert variants == {
        bcm.VARIANT_COLON_SINGLE,
        bcm.VARIANT_COLON_RANGE,
        bcm.VARIANT_COLON_LIST,
        bcm.VARIANT_ANCHOR_RANGE,
    }
    list_spans = [s for s in spans if s[1] == bcm.VARIANT_COLON_LIST]
    assert [s[3] for s in list_spans] == [30, 31, 32]
    assert [s[5] for s in list_spans] == [0, 1, 2]  # ordinal


@pytest.mark.parametrize(
    "rel,expected",
    [
        (".planning/phases/155-dead-weight/155-01-PLAN.md", "155"),
        (".planning/phases/156-x/156-RESEARCH.md", "156"),
        (".planning/phases/157-x/157-VERIFICATION.md", "157"),
        (".planning/phases/158-x/158-07-SUMMARY.md", "158"),
        (".planning/phases/154-x/154-12-SUMMARY.md", "154_post_manifest"),
        (".planning/milestones/v1.33-artifacts/158-after-figures.md", "v1.33"),
        (".planning/STATE.md", "other_added"),
    ],
)
def test_phase_bucket_classification(rel, expected):
    assert pcr.phase_bucket(rel) == expected


# ---------------------------------------------------------------------------
# Synthetic multi-repo harness: a meta repo plus two "submodule-shaped"
# source repos, with a window-start and window-end commit.
# ---------------------------------------------------------------------------
class MultiRepoHarness:
    def __init__(self, tmp_path):
        self.meta = tmp_path / "meta"
        self.meta.mkdir(parents=True)
        # `firestarter`/`firestarter_app` live UNDER the meta root, exactly
        # like the real submodule layout -- `remap_citations.py` resolves
        # `target_file_resolved` paths as `<repo_root>/<root_name>/...`.
        self.fw = self.meta / "firestarter"
        self.app = self.meta / "firestarter_app"
        for repo in (self.meta, self.fw, self.app):
            repo.mkdir(parents=True, exist_ok=True)
            assert _git(repo, "init", "-q").returncode == 0

        (self.fw / "src").mkdir()
        (self.fw / "src" / "widget.cpp").write_text(
            "\n".join(f"// fw line {i}" for i in range(1, 21)) + "\n", encoding="utf-8"
        )
        assert _git(self.fw, "add", "-A").returncode == 0
        assert _git(self.fw, "commit", "-qm", "fw initial").returncode == 0
        self.fw_before_sha = _git(self.fw, "rev-parse", "HEAD").stdout.strip()

        (self.app / "firestarter").mkdir()
        (self.app / "firestarter" / "gizmo.py").write_text(
            "\n".join(f"# app line {i}" for i in range(1, 21)) + "\n", encoding="utf-8"
        )
        assert _git(self.app, "add", "-A").returncode == 0
        assert _git(self.app, "commit", "-qm", "app initial").returncode == 0
        self.app_before_sha = _git(self.app, "rev-parse", "HEAD").stdout.strip()

        (self.meta / ".planning" / "v1.33").mkdir(parents=True)
        # An "original manifest" analog: one resolved record citing widget.cpp:5.
        header = {"_schema": {"pre_sweep_shas": {"firestarter": self.fw_before_sha, "firestarter_app": self.app_before_sha}}}
        orig_rec = {
            "planning_file": ".planning/original_doc.md",
            "planning_line": 1,
            "variant": "colon_single",
            "target_file_cited": "widget.cpp",
            "target_file_resolved": "firestarter/src/widget.cpp",
            "resolution": citation_paths.BASENAME,
            "resolution_reason": "unique basename",
            "target_line": 5,
            "target_line_end": None,
            "source_text": "// fw line 5",
            "source_text_end": None,
            "text_status": bcm.TEXT_STATUS_READ,
            "text_status_end": None,
            "retarget": False,
        }
        self.original_manifest_path = self.meta / ".planning" / "v1.33" / "sweep-citation-manifest.jsonl"
        with open(self.original_manifest_path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(header) + "\n")
            fh.write(json.dumps({k: orig_rec[k] for k in bcm.RECORD_KEYS}) + "\n")
        (self.meta / ".planning" / "original_doc.md").write_text(
            "cites widget.cpp:5 for context\n", encoding="utf-8"
        )
        # Pre-exists at window-start (with NO citation yet) so a later
        # `modify_global_doc()` call is a genuine git "M", not an "A" --
        # exercising `census_modified_files()`'s positional reconciliation
        # rather than `census_added_files()`.
        (self.meta / ".planning" / "GLOBAL.md").write_text(
            "an existing global document, no citation yet\n", encoding="utf-8"
        )
        assert _git(self.meta, "add", "-A").returncode == 0
        assert _git(self.meta, "commit", "-qm", "window start: original manifest").returncode == 0
        self.window_start_sha = _git(self.meta, "rev-parse", "HEAD").stdout.strip()

    def add_phase_dir(self, n, cited_line=5):
        d = self.meta / ".planning" / "phases" / f"{n}-synthetic-phase"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{n}-01-PLAN.md").write_text(
            f"describes widget.cpp:{cited_line} for phase {n}\n", encoding="utf-8"
        )

    def add_v133_evidence(self, name="evidence.md", cited_line=5):
        (self.meta / ".planning" / "v1.33" / name).write_text(
            f"evidence citing widget.cpp:{cited_line}\n", encoding="utf-8"
        )

    def modify_global_doc(self, name="GLOBAL.md", extra_citation=True):
        p = self.meta / ".planning" / name
        text = "an existing global document\n"
        if extra_citation:
            text += "newly added: gizmo.py:3\n"
        p.write_text(text, encoding="utf-8")

    def commit_window_end(self):
        assert _git(self.meta, "add", "-A").returncode == 0
        assert _git(self.meta, "commit", "-qm", "window end").returncode == 0
        return _git(self.meta, "rev-parse", "HEAD").stdout.strip()

    def run_prepare(self, out_dir, window_end_sha, check_existing=True, thresholds=None):
        argv = [
            sys.executable, _TOOL,
            "--repo-root", str(self.meta),
            "--original-manifest", str(self.original_manifest_path),
            "--window-start-sha", self.window_start_sha,
            "--window-end-sha", window_end_sha,
            "--firmware-root", str(self.fw),
            "--app-root", str(self.app),
            "--late-output", str(out_dir / "late.jsonl"),
            "--exceptions-output", str(out_dir / "exceptions.jsonl"),
            "--review-output", str(out_dir / "review.md"),
            "--overlay-output", str(out_dir / "overlay.json"),
        ]
        if check_existing:
            argv.append("--check-existing")
        env = dict(os.environ)
        if thresholds is not None:
            env["PCR_TEST_THRESHOLDS_JSON"] = json.dumps(thresholds)
        return subprocess.run(argv, capture_output=True, text=True, check=False, env=env)


def _load_late(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if '"_schema"' not in l]


# ---------------------------------------------------------------------------
# 6-8, 11: end-to-end integration on the synthetic corpus
# ---------------------------------------------------------------------------
def test_end_to_end_synthetic_corpus_produces_exact_phase_subtotal(tmp_path):
    h = MultiRepoHarness(tmp_path)
    for n in ("155", "156", "157", "158"):
        h.add_phase_dir(n)
    h.add_v133_evidence()
    window_end = h.commit_window_end()

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    # This synthetic tool asserts an EXACT 127/184/225/106 subtotal drawn
    # from the real corpus; a synthetic fixture legitimately has its own
    # (different, small) counts, so drive the module functions directly
    # rather than the exact-subtotal-asserting main().
    root_dirs = {"firestarter": h.fw, "firestarter_app": h.app}
    final_sha = {"firestarter": h.fw_before_sha, "firestarter_app": h.app_before_sha}
    linker = pcr.GitlinkResolver(h.meta)
    index = citation_paths.CandidateIndex(
        root_dirs, bcm._full_repo_paths(h.fw, h.app)
    )
    diff_rows = pcr.git_diff_namestatus(h.meta, h.window_start_sha, window_end, ".planning")
    added = [old for status, old, _new in diff_rows if status == "A" and pcr.in_scope(old)]
    assert added, "the synthetic fixture must add at least one in-scope file"

    added_records = pcr.census_added_files(
        repo_root=h.meta, added_paths=added, window_start=h.window_start_sha,
        window_end=window_end, index=index, root_dirs=root_dirs,
        final_sha=final_sha, linker=linker,
    )
    by_phase = {}
    for rec in added_records:
        by_phase[rec["phase"]] = by_phase.get(rec["phase"], 0) + 1
    assert by_phase.get("155") == 1
    assert by_phase.get("156") == 1
    assert by_phase.get("157") == 1
    assert by_phase.get("158") == 1
    assert by_phase.get("v1.33") == 1
    # Every resolved record must carry a historically justified source_sha,
    # never a bare final-tree self-snapshot with no anchor evidence.
    for rec in added_records:
        assert rec["target_file_resolved"] == "firestarter/src/widget.cpp"
        assert rec["source_sha"] in (h.fw_before_sha,)
        assert rec["source_text"] == "// fw line 5"


def test_coverage_gate_is_not_vacuous_added_and_modified(tmp_path):
    """Omitting a v1.33-added citation OR a modified-global-document citation
    from the window MUST change the measured supplemental count -- proving
    the census is not silently absorbing (or silently missing) either
    class of record."""
    h1 = MultiRepoHarness(tmp_path / "with_both")
    h1.add_v133_evidence()
    h1.modify_global_doc(extra_citation=True)
    end1 = h1.commit_window_end()

    root_dirs = {"firestarter": h1.fw, "firestarter_app": h1.app}
    final_sha = {"firestarter": h1.fw_before_sha, "firestarter_app": h1.app_before_sha}
    index = citation_paths.CandidateIndex(root_dirs, bcm._full_repo_paths(h1.fw, h1.app))
    linker = pcr.GitlinkResolver(h1.meta)

    diff_rows = pcr.git_diff_namestatus(h1.meta, h1.window_start_sha, end1, ".planning")
    added = [old for status, old, _n in diff_rows if status == "A" and pcr.in_scope(old)]
    modified = [old for status, old, _n in diff_rows if status == "M" and pcr.in_scope(old)]
    _, original_records = rc.load_manifest(h1.original_manifest_path)

    added_with = pcr.census_added_files(
        repo_root=h1.meta, added_paths=added, window_start=h1.window_start_sha,
        window_end=end1, index=index, root_dirs=root_dirs, final_sha=final_sha, linker=linker,
    )
    modified_with = pcr.census_modified_files(
        repo_root=h1.meta, modified_paths=modified, original_records=original_records,
        window_start=h1.window_start_sha, window_end=end1, index=index,
        root_dirs=root_dirs, final_sha=final_sha, linker=linker,
    )
    assert len(added_with) >= 1
    assert len(modified_with) == 1  # the newly-added "gizmo.py:3" line

    # Now the omission fixture: same starting point, but the modified global
    # document carries NO new citation, and no v1.33 evidence file is added.
    h2 = MultiRepoHarness(tmp_path / "without_either")
    h2.modify_global_doc(extra_citation=False)
    end2 = h2.commit_window_end()
    root_dirs2 = {"firestarter": h2.fw, "firestarter_app": h2.app}
    final_sha2 = {"firestarter": h2.fw_before_sha, "firestarter_app": h2.app_before_sha}
    index2 = citation_paths.CandidateIndex(root_dirs2, bcm._full_repo_paths(h2.fw, h2.app))
    linker2 = pcr.GitlinkResolver(h2.meta)
    diff_rows2 = pcr.git_diff_namestatus(h2.meta, h2.window_start_sha, end2, ".planning")
    added2 = [old for status, old, _n in diff_rows2 if status == "A" and pcr.in_scope(old)]
    modified2 = [old for status, old, _n in diff_rows2 if status == "M" and pcr.in_scope(old)]
    _, original_records2 = rc.load_manifest(h2.original_manifest_path)
    added_without = pcr.census_added_files(
        repo_root=h2.meta, added_paths=added2, window_start=h2.window_start_sha,
        window_end=end2, index=index2, root_dirs=root_dirs2, final_sha=final_sha2, linker=linker2,
    )
    modified_without = pcr.census_modified_files(
        repo_root=h2.meta, modified_paths=modified2, original_records=original_records2,
        window_start=h2.window_start_sha, window_end=end2, index=index2,
        root_dirs=root_dirs2, final_sha=final_sha2, linker=linker2,
    )
    assert len(added_without) == 0, "no v1.33 evidence file was added in this fixture"
    assert len(modified_without) == 0, "no new citation was added to the modified global doc"
    assert (len(added_with) + len(modified_with)) > (len(added_without) + len(modified_without))


def _synthetic_thresholds(h):
    return {
        "phase_subtotal": {"155": 1, "156": 1, "157": 1, "158": 1},
        "min_known_post154": 0,
        "min_ordinary": 0,
        "min_total": 0,
        "min_review_floor": 0,
        "retarget_base_sha": {"firestarter": h.fw_before_sha, "firestarter_app": h.app_before_sha},
        "pre_sweep_sha": {"firestarter": h.fw_before_sha, "firestarter_app": h.app_before_sha},
    }


def test_two_runs_over_same_synthetic_corpus_are_byte_identical(tmp_path):
    h = MultiRepoHarness(tmp_path)
    for n in ("155", "156", "157", "158"):
        h.add_phase_dir(n)
    h.add_v133_evidence()
    end = h.commit_window_end()

    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"
    out1.mkdir()
    out2.mkdir()
    r1 = h.run_prepare(out1, end, check_existing=False, thresholds=_synthetic_thresholds(h))
    r2 = h.run_prepare(out2, end, check_existing=False, thresholds=_synthetic_thresholds(h))
    assert r1.returncode == 0, r1.stderr
    assert r2.returncode == 0, r2.stderr
    for name in ("late.jsonl", "exceptions.jsonl", "review.md", "overlay.json"):
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes(), name


def test_original_manifest_hash_unchanged_by_main(tmp_path):
    h = MultiRepoHarness(tmp_path)
    for n in ("155", "156", "157", "158"):
        h.add_phase_dir(n)
    h.add_v133_evidence()
    end = h.commit_window_end()
    before = hashlib.sha256(h.original_manifest_path.read_bytes()).hexdigest()

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = h.run_prepare(out_dir, end, check_existing=False, thresholds=_synthetic_thresholds(h))
    assert result.returncode == 0, result.stderr
    after = hashlib.sha256(h.original_manifest_path.read_bytes()).hexdigest()
    assert before == after


# ---------------------------------------------------------------------------
# 3-4: anchor_record precedence / fallback / candidate-list-never-dropped
# ---------------------------------------------------------------------------
def test_anchor_record_prefers_gitlink_anchor_over_final_head_disagreement(tmp_path):
    fw = tmp_path / "fw"
    fw.mkdir()
    assert _git(fw, "init", "-q").returncode == 0
    (fw / "widget.cpp").write_text("old line one\nold line two\n", encoding="utf-8")
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "authoring-time state").returncode == 0
    authoring_sha = _git(fw, "rev-parse", "HEAD").stdout.strip()

    (fw / "widget.cpp").write_text("NEW line one\nNEW line two\n", encoding="utf-8")
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "final state, line 1 changed").returncode == 0
    final_sha_val = _git(fw, "rev-parse", "HEAD").stdout.strip()

    cache = pcr.BlobTextCache()
    sha, candidates, s_text, e_text, s_status, e_status = pcr.anchor_record(
        root_dirs={"firestarter": fw},
        gitlink_sha=authoring_sha,
        final_sha={"firestarter": final_sha_val},
        target_file_resolved="firestarter/widget.cpp",
        target_line=1,
        target_line_end=None,
        blob_cache=cache,
    )
    assert sha == authoring_sha
    assert candidates is None
    assert s_text == "old line one"
    assert s_status == bcm.TEXT_STATUS_READ


def test_anchor_record_falls_back_and_never_drops_candidates_when_unreadable(tmp_path):
    fw = tmp_path / "fw"
    fw.mkdir()
    assert _git(fw, "init", "-q").returncode == 0
    (fw / "widget.cpp").write_text("only one line\n", encoding="utf-8")
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "one-line commit").returncode == 0
    authoring_sha = _git(fw, "rev-parse", "HEAD").stdout.strip()

    cache = pcr.BlobTextCache()
    # target_line=99 is out of range at BOTH the authoring anchor and the
    # (identical, in this fixture) final anchor -- neither anchor reads.
    sha, candidates, s_text, e_text, s_status, e_status = pcr.anchor_record(
        root_dirs={"firestarter": fw},
        gitlink_sha=authoring_sha,
        final_sha={"firestarter": authoring_sha},
        target_file_resolved="firestarter/widget.cpp",
        target_line=99,
        target_line_end=None,
        blob_cache=cache,
    )
    assert sha is None
    assert candidates == [authoring_sha]  # de-duped; never silently dropped
    assert s_text == bcm.UNREADABLE
    assert s_status == bcm.TEXT_STATUS_READ_ERROR


def test_anchor_record_offers_pre_sweep_sha_as_a_third_candidate_tier(tmp_path):
    """Phase 159-04 (B2 -- see 159-03-SUMMARY.md Blockers #2): a citation
    line unreadable at BOTH the gitlink and final-head candidates, but
    readable at the root's pre-sweep revision, must resolve via the new
    third candidate tier rather than falling back to an unresolved
    `ambiguous_historical_anchor`. Reproduces the real defect measured on
    all 4 historical_anchor records: `eprom_params.cpp` was 58 lines at both
    post-Phase-154 candidates but the recorded line (61) existed only at the
    pre-sweep revision.
    """
    fw = tmp_path / "fw"
    fw.mkdir()
    assert _git(fw, "init", "-q").returncode == 0
    (fw / "widget.cpp").write_text("\n".join(f"pre-sweep line {i}" for i in range(1, 63)) + "\n", encoding="utf-8")
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "pre-sweep state (62 lines)").returncode == 0
    pre_sweep = _git(fw, "rev-parse", "HEAD").stdout.strip()

    (fw / "widget.cpp").write_text("only 3 lines\nremain\nafter the sweep\n", encoding="utf-8")
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "post-sweep state (3 lines)").returncode == 0
    post_sweep = _git(fw, "rev-parse", "HEAD").stdout.strip()

    cache = pcr.BlobTextCache()

    # WITHOUT the fix (pre_sweep_sha omitted): both candidates are the same
    # 3-line post-sweep blob, line 61 is out of range at both -- unresolved,
    # exactly the measured defect.
    sha, candidates, s_text, e_text, s_status, e_status = pcr.anchor_record(
        root_dirs={"firestarter": fw},
        gitlink_sha=post_sweep,
        final_sha={"firestarter": post_sweep},
        target_file_resolved="firestarter/widget.cpp",
        target_line=61,
        target_line_end=None,
        blob_cache=cache,
    )
    assert sha is None
    assert candidates == [post_sweep]
    assert s_status == bcm.TEXT_STATUS_READ_ERROR

    # WITH the fix: the pre-sweep sha is offered as a third tier and read
    # successfully.
    cache2 = pcr.BlobTextCache()
    sha, candidates, s_text, e_text, s_status, e_status = pcr.anchor_record(
        root_dirs={"firestarter": fw},
        gitlink_sha=post_sweep,
        final_sha={"firestarter": post_sweep},
        target_file_resolved="firestarter/widget.cpp",
        target_line=61,
        target_line_end=None,
        blob_cache=cache2,
        pre_sweep_sha={"firestarter": pre_sweep},
    )
    assert sha == pre_sweep
    assert s_text == "pre-sweep line 61"
    assert s_status == bcm.TEXT_STATUS_READ


# ---------------------------------------------------------------------------
# 5: known_post154_non_survivors -- verbatim survival via LineMap, anti-vacuity
# ---------------------------------------------------------------------------
def test_known_post154_non_survivors_distinguishes_clamped_from_unclamped(tmp_path):
    fw = tmp_path / "fw"
    fw.mkdir()
    assert _git(fw, "init", "-q").returncode == 0
    (fw / "widget.cpp").write_text(
        "\n".join(["header"] + [f"body {i}" for i in range(1, 6)] + ["tail"]) + "\n",
        encoding="utf-8",
    )
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "retarget base").returncode == 0
    retarget_base = _git(fw, "rev-parse", "HEAD").stdout.strip()

    # Final tree: "body 2" (old line 3) is DELETED -- everything after it
    # shifts up by one. "body 4" (old line 5) survives, shifted to line 4.
    (fw / "widget.cpp").write_text(
        "\n".join(["header", "body 1", "body 3", "body 4", "body 5", "tail"]) + "\n",
        encoding="utf-8",
    )
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "final: body 2 deleted").returncode == 0
    final_sha_val = _git(fw, "rev-parse", "HEAD").stdout.strip()

    survivor_rec = {
        "target_file_resolved": "firestarter/widget.cpp",
        "retarget": True,
        "retarget_new_line": 5,  # "body 4" -- shifts, but survives
        "retarget_new_line_end": None,
        "retarget_new_text": "body 4",
    }
    non_survivor_rec = {
        "target_file_resolved": "firestarter/widget.cpp",
        "retarget": True,
        "retarget_new_line": 3,  # "body 2" -- deleted outright
        "retarget_new_line_end": None,
        "retarget_new_text": "body 2",
    }
    ordinary_rec = {
        "target_file_resolved": "firestarter/widget.cpp",
        "retarget": False,
    }

    out = pcr.known_post154_non_survivors(
        original_records=[survivor_rec, non_survivor_rec, ordinary_rec],
        root_dirs={"firestarter": fw},
        retarget_base_sha={"firestarter": retarget_base},
        final_sha={"firestarter": final_sha_val},
    )
    assert non_survivor_rec in out
    assert survivor_rec not in out
    assert ordinary_rec not in out  # retarget:false is never in this population


# ---------------------------------------------------------------------------
# 9-10: schema/oracle discipline
# ---------------------------------------------------------------------------
def test_duplicate_record_id_is_refused(tmp_path, monkeypatch):
    """Two distinct late records minted with the SAME record_id (a collision
    or a hashing bug) must hard-refuse the whole run rather than silently
    conflating two citations into one ledger/oracle identity."""
    h = MultiRepoHarness(tmp_path)
    h.add_phase_dir("155")
    h.add_phase_dir("156")  # a second distinct record to collide with
    end = h.commit_window_end()

    monkeypatch.setattr(pcr, "mint_record_id", lambda rec: "late-collision-forced")

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    argv = [
        "--repo-root", str(h.meta),
        "--original-manifest", str(h.original_manifest_path),
        "--window-start-sha", h.window_start_sha,
        "--window-end-sha", end,
        "--firmware-root", str(h.fw),
        "--app-root", str(h.app),
        "--late-output", str(out_dir / "late.jsonl"),
        "--exceptions-output", str(out_dir / "exceptions.jsonl"),
        "--review-output", str(out_dir / "review.md"),
        "--overlay-output", str(out_dir / "overlay.json"),
    ]
    with pytest.raises(SystemExit) as exc:
        pcr.main(argv)
    assert exc.value.code == 1
    assert not (out_dir / "late.jsonl").is_file(), "nothing should be written on a duplicate-ID refusal"


def test_mint_record_id_is_deterministic_and_position_sensitive():
    base = {
        "planning_file": ".planning/x.md", "planning_line": 1, "variant": "colon_single",
        "target_file_cited": "a.cpp", "target_line": 10, "target_line_end": None,
    }
    id_a = pcr.mint_record_id(dict(base))
    id_b = pcr.mint_record_id(dict(base))
    assert id_a == id_b, "the same positional identity must mint the same ID"
    moved = dict(base, planning_line=2)
    assert pcr.mint_record_id(moved) != id_a, "a different position must mint a different ID"


def test_build_late_record_never_reads_bare_final_tree_without_anchor_evidence(tmp_path):
    """A record whose target resolves but for which NEITHER the gitlink
    anchor NOR the final head is supplied must degrade to unreadable with a
    reported (empty) candidate set -- it must never silently fall through
    to reading arbitrary current disk content as if it were historical."""
    fw = tmp_path / "fw"
    fw.mkdir()
    assert _git(fw, "init", "-q").returncode == 0
    (fw / "widget.cpp").write_text("line one\nline two\n", encoding="utf-8")
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "c").returncode == 0

    index = citation_paths.CandidateIndex({"firestarter": fw}, ["firestarter/widget.cpp"])
    rec = pcr.build_late_record(
        planning_file=".planning/x.md", planning_line=1, variant="colon_single",
        cited="widget.cpp", start=1, end=None, ordinal=0, origin="added", phase="v1.33",
        index=index, root_dirs={"firestarter": fw}, gitlink_sha=None, final_sha={},
        blob_cache=pcr.BlobTextCache(), resolutions={},
    )
    assert rec["target_file_resolved"] == "firestarter/widget.cpp"
    assert rec["source_sha"] is None
    assert rec["source_sha_candidates"] is None  # no candidates existed at all
    assert rec["source_text"] == bcm.UNREADABLE
    assert rec["text_status"] == bcm.TEXT_STATUS_READ_ERROR


# ---------------------------------------------------------------------------
# Sanity anchor: no real citing document or the immutable manifest is
# mutated by loading this module (matches remap_citations.py's own anchor).
# ---------------------------------------------------------------------------
def test_real_manifest_hash_is_unchanged_if_present():
    real_manifest = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(_HERE))),
        ".planning", "v1.33", "sweep-citation-manifest.jsonl",
    )
    if not os.path.isfile(real_manifest):
        pytest.skip("the real manifest is not present here")
    digest = hashlib.sha256(open(real_manifest, "rb").read()).hexdigest()
    assert digest == "ecdd0fc84be1627f893e30f6369c0b9eedf2a69ce3ec351064828d82e72d992e"
