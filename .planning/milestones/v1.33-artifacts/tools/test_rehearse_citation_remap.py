#!/usr/bin/env python3
"""
pytest coverage for `rehearse_citation_remap.py` -- Phase 159-04 Task 2.

Scope: this module's OWN harness-safety and materialization properties.
The full disposable rehearsal (a real registered worktree of the actual
`/workspaces` meta repo plus `firestarter`/`firestarter_app` submodule
worktrees, one disposable apply, one idempotent dry run, an injected-failure
recovery leg, and the archive gate) is exercised directly via the CLI against
the real corpus -- documented in `159-rehearsal-record.json` -- because that
leg legitimately takes ~90s and depends on this specific repository's real
git history; it is not re-run inside this fast unit suite. What IS proven
here, against small throwaway git fixtures (the SAME `Harness`-style pattern
`test_remap_citations.py` uses):

  1. `refuse_live_apply_root()` refuses `/workspaces` (and its resolved
     equivalent) as a disposable apply target.
  2. `materialize_live_corpus()` builds a real registered worktree, mounts
     independent submodule worktrees at exact SHAs, and reproduces an
     approved `relocated` overlay's topology (old path ABSENT, new path
     present with the live bytes) -- not merely a clean checkout.
  3. `snapshot_hashes()` is a deterministic path->sha256 map, `None` for a
     missing path, never silently dropped.
  4. `simulate_index_stage()` flags a `preserve_unstaged` path staged as a
     whole blob, accepts a citation-only strategy, and accepts a
     `requires_authorization` entry for an `authorize_include` path.
  5. `find_range_proof()` finds the exact recorded old/new tuple and misses
     a near-but-wrong one (anti-vacuity).
  6. `Worktree.cleanup()` actually removes what `.add()` created.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import rehearse_citation_remap as rr  # noqa: E402
import remap_citations as rc  # noqa: E402


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.email=t@t.invalid", "-c", "user.name=t", *args],
        capture_output=True, text=True, check=False,
    )


# ---------------------------------------------------------------------------
# 1. refuse_live_apply_root
# ---------------------------------------------------------------------------
def test_refuse_live_apply_root_rejects_workspaces():
    from pathlib import Path

    with pytest.raises(SystemExit):
        rr.refuse_live_apply_root(Path("/workspaces"))


def test_refuse_live_apply_root_rejects_dot_relative_to_workspaces(monkeypatch):
    """A relative path that RESOLVES to /workspaces must also be refused,
    not only the literal string '/workspaces' -- the same class of
    resolve()-before-compare bug `remap_citations.py`'s own
    `--inject-write-failure-after` guard avoids."""
    from pathlib import Path

    monkeypatch.chdir("/workspaces")
    with pytest.raises(SystemExit):
        rr.refuse_live_apply_root(Path("."))


def test_refuse_live_apply_root_allows_a_disposable_path(tmp_path):
    rr.refuse_live_apply_root(tmp_path / "disposable-corpus")  # must not raise


# ---------------------------------------------------------------------------
# 2. materialize_live_corpus -- real worktrees, approved relocation topology
# ---------------------------------------------------------------------------
@pytest.fixture
def fake_repo_pair(tmp_path):
    """A throwaway meta repo with a throwaway `firestarter`-shaped submodule
    REPO (a real, independent git repo, not an actual gitlink -- this
    harness only ever needs `git worktree add` to succeed against it, which
    does not require a real submodule relationship)."""
    meta = tmp_path / "meta"
    fw = tmp_path / "meta" / "firestarter"
    app = tmp_path / "meta" / "firestarter_app"
    (meta / ".planning" / "v1.33").mkdir(parents=True)
    (meta / ".planning" / "old-doc.md").write_text("cites firestarter/x.c:1\n", encoding="utf-8")
    assert _git(meta, "init", "-q").returncode == 0
    assert _git(meta, "add", "-A").returncode == 0
    assert _git(meta, "commit", "-qm", "meta initial").returncode == 0

    fw.mkdir()
    (fw / "x.c").write_text("int x;\n", encoding="utf-8")
    assert _git(fw, "init", "-q").returncode == 0
    assert _git(fw, "add", "-A").returncode == 0
    assert _git(fw, "commit", "-qm", "fw initial").returncode == 0
    fw_sha = _git(fw, "rev-parse", "HEAD").stdout.strip()

    app.mkdir()
    (app / "y.py").write_text("y = 1\n", encoding="utf-8")
    assert _git(app, "init", "-q").returncode == 0
    assert _git(app, "add", "-A").returncode == 0
    assert _git(app, "commit", "-qm", "app initial").returncode == 0
    app_sha = _git(app, "rev-parse", "HEAD").stdout.strip()

    return meta, fw_sha, app_sha


def _minimal_manifest(tmp_path):
    header = {"_schema": {"schema_version": "1.0.0"}}
    manifest_path = tmp_path / "manifest.jsonl"
    with open(manifest_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(header) + "\n")
        fh.write(
            json.dumps(
                {
                    "planning_file": ".planning/old-doc.md",
                    "planning_line": 1,
                    "variant": "colon_single",
                    "target_file_cited": "firestarter/x.c",
                    "target_file_resolved": "firestarter/x.c",
                    "resolution": "exact",
                    "resolution_reason": "test",
                    "target_line": 1,
                    "target_line_end": None,
                    "source_text": "int x;",
                    "source_text_end": None,
                    "text_status": "read",
                    "text_status_end": None,
                    "retarget": False,
                }
            )
            + "\n"
        )
    return manifest_path


def test_materialize_live_corpus_builds_registered_worktrees(fake_repo_pair, tmp_path):
    meta, fw_sha, app_sha = fake_repo_pair
    dest = tmp_path / "corpus"
    manifest_path = _minimal_manifest(tmp_path)

    mat = rr.materialize_live_corpus(meta, dest, [manifest_path], [], fw_sha, app_sha)
    try:
        assert dest.is_dir()
        assert (dest / "firestarter" / "x.c").is_file()
        assert (dest / "firestarter_app" / "y.py").is_file()
        # A real, REGISTERED worktree -- `git -C dest rev-parse HEAD` must
        # work, exactly like the real `/workspaces` root does.
        head = subprocess.run(
            ["git", "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True
        )
        assert head.returncode == 0
        fw_head = subprocess.run(
            ["git", "-C", str(dest / "firestarter"), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        assert fw_head.stdout.strip() == fw_sha
        assert ".planning/old-doc.md" in mat["affected_documents"]
    finally:
        for wt in mat["worktrees"]:
            wt.cleanup()
    assert not dest.exists(), "cleanup() must remove the registered worktree directory"


def test_materialize_live_corpus_reproduces_relocation_topology(fake_repo_pair, tmp_path):
    """The approved-untracked-relocation case (mirrors the real COBS
    relocation): the OLD tracked path must be ABSENT in the disposable
    corpus, and the NEW untracked path must carry the live bytes -- a plain
    `git worktree add` at HEAD alone would get this wrong (HEAD still
    tracks the old path; the untracked new path does not exist at any
    commit at all)."""
    meta, fw_sha, app_sha = fake_repo_pair
    old_path = meta / ".planning" / "relocatable.md"
    new_path = meta / ".planning" / "v1.33" / "relocatable.md"
    old_path.write_text("original content\n", encoding="utf-8")
    assert _git(meta, "add", "-A").returncode == 0
    assert _git(meta, "commit", "-qm", "add relocatable doc").returncode == 0
    # The live relocation: delete tracked old path, add untracked new path --
    # exactly like the real `.planning/v1.9-COBS-DECISION.md` -> `.planning/milestones/v1.33-artifacts/...`.
    old_path.unlink()
    new_path.write_text("original content\n", encoding="utf-8")

    overlay_path = tmp_path / "overlay.jsonl"
    overlay_path.write_text(
        json.dumps({"_schema": {"role": "test"}}) + "\n"
        + json.dumps(
            {
                "path": ".planning/relocatable.md",
                "current_path": ".planning/milestones/v1.33-artifacts/relocatable.md",
                "topology_action": "relocated (deleted old path, added untracked new path)",
                "dirty_overlap": True,
                "decision": "authorize_include",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    manifest_path = _minimal_manifest(tmp_path)
    dest = tmp_path / "corpus2"

    mat = rr.materialize_live_corpus(meta, dest, [manifest_path], [overlay_path], fw_sha, app_sha)
    try:
        assert not (dest / ".planning" / "relocatable.md").exists(), "old path must be absent"
        assert (dest / ".planning" / "v1.33" / "relocatable.md").is_file()
        assert (dest / ".planning" / "v1.33" / "relocatable.md").read_text() == "original content\n"
    finally:
        for wt in mat["worktrees"]:
            wt.cleanup()


# ---------------------------------------------------------------------------
# 3. snapshot_hashes
# ---------------------------------------------------------------------------
def test_snapshot_hashes_is_deterministic_and_never_drops_a_missing_path(tmp_path):
    (tmp_path / "a.txt").write_text("hello\n", encoding="utf-8")
    result = rr.snapshot_hashes(tmp_path, ["a.txt", "does-not-exist.txt"])
    assert result["a.txt"] == rc.hashlib.sha256(b"hello\n").hexdigest()
    assert result["does-not-exist.txt"] is None
    assert set(result) == {"a.txt", "does-not-exist.txt"}


# ---------------------------------------------------------------------------
# 4. simulate_index_stage
# ---------------------------------------------------------------------------
def test_simulate_index_stage_flags_preserve_unstaged_staged_as_whole_blob():
    overlay_rows = [
        {"path": ".planning/STATE.md", "decision": "preserve_unstaged"},
    ]
    index_plan = [
        {"path": ".planning/STATE.md", "staging_strategy": "requires_authorization"},
    ]
    result = rr.simulate_index_stage(index_plan, overlay_rows)
    assert result["ok"] is False
    assert any("staged as" in f for f in result["findings"])


def test_simulate_index_stage_accepts_citation_only_strategy_for_preserve_unstaged():
    overlay_rows = [{"path": ".planning/STATE.md", "decision": "preserve_unstaged"}]
    index_plan = [{"path": ".planning/STATE.md", "staging_strategy": "citation_only_index_object"}]
    result = rr.simulate_index_stage(index_plan, overlay_rows)
    assert result["ok"] is True


def test_simulate_index_stage_accepts_requires_authorization_for_authorize_include():
    overlay_rows = [
        {
            "path": ".planning/v1.9-COBS-DECISION.md",
            "current_path": ".planning/milestones/v1.33-artifacts/v1.9-COBS-DECISION.md",
            "decision": "authorize_include",
        }
    ]
    index_plan = [
        {"path": ".planning/milestones/v1.33-artifacts/v1.9-COBS-DECISION.md", "staging_strategy": "requires_authorization"}
    ]
    result = rr.simulate_index_stage(index_plan, overlay_rows)
    assert result["ok"] is True
    assert any("correctly scoped" in f for f in result["findings"])


def test_simulate_index_stage_flags_authorize_include_missing_its_own_authorization():
    overlay_rows = [
        {
            "path": ".planning/v1.9-COBS-DECISION.md",
            "current_path": ".planning/milestones/v1.33-artifacts/v1.9-COBS-DECISION.md",
            "decision": "authorize_include",
        }
    ]
    index_plan = [
        {"path": ".planning/milestones/v1.33-artifacts/v1.9-COBS-DECISION.md", "staging_strategy": "citation_only_index_object"}
    ]
    result = rr.simulate_index_stage(index_plan, overlay_rows)
    assert result["ok"] is False


# ---------------------------------------------------------------------------
# 5. find_range_proof -- anti-vacuity included
# ---------------------------------------------------------------------------
def test_find_range_proof_finds_the_exact_recorded_case():
    report = {
        "range_proofs": [
            {"old_start": 1, "old_end": 5, "new_start": 10, "new_end": 12},
            {
                "old_start": rr.RANGE_PROOF_OLD[0],
                "old_end": rr.RANGE_PROOF_OLD[1],
                "new_start": rr.RANGE_PROOF_NEW[0],
                "new_end": rr.RANGE_PROOF_NEW[1],
                "record_id": "orig-test",
            },
        ]
    }
    found = rr.find_range_proof(report)
    assert found is not None
    assert found["record_id"] == "orig-test"


def test_find_range_proof_is_not_vacuous_against_a_near_miss():
    """A range_proofs list that does NOT contain the exact recorded
    old/new tuple must return None -- proves the match is exact, not a
    loose containment check that would pass against any range proof."""
    report = {
        "range_proofs": [
            {"old_start": 128, "old_end": 131, "new_start": 316, "new_end": 319},  # off by one
        ]
    }
    assert rr.find_range_proof(report) is None
    assert rr.find_range_proof({"range_proofs": []}) is None


# ---------------------------------------------------------------------------
# 6. Worktree lifecycle
# ---------------------------------------------------------------------------
def test_worktree_cleanup_removes_what_add_created(fake_repo_pair, tmp_path):
    meta, _fw_sha, _app_sha = fake_repo_pair
    dest = tmp_path / "standalone-wt"
    wt = rr.Worktree(meta, dest, "HEAD")
    wt.add()
    assert dest.is_dir()
    listed = subprocess.run(["git", "-C", str(meta), "worktree", "list"], capture_output=True, text=True)
    assert str(dest) in listed.stdout
    wt.cleanup()
    assert not dest.exists()
    listed_after = subprocess.run(
        ["git", "-C", str(meta), "worktree", "list"], capture_output=True, text=True
    )
    assert str(dest) not in listed_after.stdout
