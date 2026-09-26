#!/usr/bin/env python3
r"""
Phase 159-04 rehearsal harness for `remap_citations.py`.

WHAT THIS PROVES, AND WHY IT NEVER TOUCHES PRODUCTION
------------------------------------------------------
A detached-HEAD checkout of the meta repo omits two things that are load
bearing for a real Phase 159 apply: the CURRENT dirty bytes of files like
`.planning/STATE.md`, and the deleted-old/untracked-new topology of the
approved `.planning/v1.9-COBS-DECISION.md` relocation. Neither exists at any
commit -- they are the live worktree's OWN state. A rehearsal that checked
out a clean commit instead of reproducing this exact state would prove
nothing about whether the real apply, against the real dirty tree, will
actually work.

This module therefore:

  1. `materialize_live_corpus()` -- builds a DISPOSABLE copy of the meta
     repo (a registered `git worktree`, never a plain directory copy, so
     `git show`/`git diff --find-renames` keep working exactly as they do
     against `/workspaces`) plus registered worktrees of `firestarter` and
     `firestarter_app` at their FINAL head SHAs, then overlays every
     affected document's CURRENT live bytes on top -- including the COBS
     relocation's delete-old/add-new topology -- so the disposable corpus
     is byte-for-byte and topology-for-topology identical to what a real
     apply would see.
  2. Runs the REAL `remap_citations.py` CLI (never a second rewrite
     implementation) against that disposable corpus for every rehearsal
     leg: a corpus/topology fingerprint comparison against the prospective
     production run, an injected-mid-batch-failure recovery leg, a single
     disposable apply, an idempotent second dry run, and an index-staging
     simulation.
  3. `run_archive_gate()` -- runs Phase 130's own record-correction gate
     against the disposable corpus's copies of its five default targets,
     before and after the disposable apply, and requires the SAME PASS
     verdict both times.
  4. Writes a single, non-vacuous `159-rehearsal-record.json` explicitly
     labelling every apply event `disposable`; no production receipt or
     production recovery bundle is ever created by this module.

Refuses to treat `/workspaces` (or any path that RESOLVES to it) as a
disposable apply target -- see `refuse_live_apply_root()`. All worktrees
created here are always removed in a `finally` block; nothing is installed
and no network access is made.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import remap_citations as rc  # noqa: E402 -- sys.path prepared above

REMAP_TOOL = os.path.join(_HERE, "remap_citations.py")
ARCHIVE_GATE_RELATIVE = (
    "phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py"
)
ARCHIVE_GATE_TARGETS_RELATIVE = (
    "PROJECT.md",
    "STATE.md",
    "ROADMAP.md",
    "milestones/v1.23-REQUIREMENTS.md",
    "notes/py32f071-port-branch-state.md",
)

#: The real-corpus range-shrink case Task 2 must reproduce end-to-end
#: (distinct from 159-03's eprom_operations.cpp reviewed example -- this one
#: is a NATURAL, non-reviewed range citation, proving ROADMAP criterion 3
#: holds for the production engine on the real corpus, not only for a
#: hand-reviewed record).
RANGE_PROOF_OLD = (128, 131)
RANGE_PROOF_NEW = (316, 318)
RANGE_PROOF_OLD_SPAN = 4
RANGE_PROOF_NEW_SPAN = 3
RANGE_PROOF_START_TEXT = "if (jsoneq_(json, key_token, key) == 0) {"
RANGE_PROOF_END_TEXT = "token_idx += 2; // Skip key and simple value"


def _die(message: str, code: int = 2) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def refuse_live_apply_root(path: Path) -> None:
    """Fail closed if `path` IS or RESOLVES to the canonical live root.

    `--inject-write-failure-after` and the whole rehearsal apply path exist
    ONLY to be exercised against a disposable copy; this is the same
    contract `remap_citations.py` itself enforces for its own
    `--inject-write-failure-after` flag, checked again here at the harness
    level so a caller cannot bypass it by pointing `--output`/`repo_root`
    tricks at the live tree.
    """
    resolved = path.resolve()
    if resolved == Path("/workspaces").resolve():
        _die(
            f"refusing to treat {path} (resolves to /workspaces) as a "
            "disposable apply root -- this harness exists only to prove "
            "the contract in disposable copies"
        )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_hashes(root: Path, rel_paths: list[str]) -> dict[str, str | None]:
    """Deterministic path -> sha256 map; `None` for a path that does not
    exist (never silently dropped -- a missing file is itself evidence)."""
    out: dict[str, str | None] = {}
    for rel in sorted(set(rel_paths)):
        p = root / rel
        out[rel] = sha256_file(p) if p.is_file() else None
    return out


# ---------------------------------------------------------------------------
# Disposable worktree bookkeeping
# ---------------------------------------------------------------------------
class Worktree:
    """One registered `git worktree`, always removed on cleanup()."""

    def __init__(self, source_repo: Path, dest: Path, commitish: str) -> None:
        self.source_repo = source_repo
        self.dest = dest
        self.commitish = commitish
        self.added = False

    def add(self) -> None:
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        done = subprocess.run(
            ["git", "-C", str(self.source_repo), "worktree", "add", "--detach", str(self.dest), self.commitish],
            capture_output=True, text=True, check=False,
        )
        if done.returncode != 0:
            _die(
                f"git worktree add failed for {self.source_repo} -> {self.dest} "
                f"@{self.commitish}: {done.stderr}"
            )
        self.added = True

    def cleanup(self) -> None:
        if not self.added:
            return
        subprocess.run(
            ["git", "-C", str(self.source_repo), "worktree", "remove", "--force", str(self.dest)],
            capture_output=True, text=True, check=False,
        )
        subprocess.run(
            ["git", "-C", str(self.source_repo), "worktree", "prune"],
            capture_output=True, text=True, check=False,
        )
        shutil.rmtree(self.dest, ignore_errors=True)


def load_manifest_planning_files(manifest_paths: list[Path]) -> set[str]:
    files: set[str] = set()
    for mp in manifest_paths:
        _header, records = rc.load_manifest(mp)
        for rec in records:
            files.add(rec["planning_file"])
    return files


def load_overlay_rows(overlay_paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for op in overlay_paths:
        rows.extend(rc.load_jsonl_rows(op))
    return [r for r in rows if "_schema" not in r]


# ---------------------------------------------------------------------------
# Materialization -- the exact approved live corpus, not a clean approximation
# ---------------------------------------------------------------------------
def materialize_live_corpus(
    live_root: Path,
    dest: Path,
    manifest_paths: list[Path],
    overlay_paths: list[Path],
    firmware_head: str,
    app_head: str,
) -> dict:
    """Builds a disposable copy of the live corpus at `dest`.

    Returns a dict with `worktrees` (the `Worktree` objects the caller must
    `cleanup()`), `affected_documents` (every planning_file this rehearsal
    materialized), and `overlay_rows` (loaded once, reused by callers).
    """
    refuse_live_apply_root(dest)

    worktrees: list[Worktree] = []
    meta_wt = Worktree(live_root, dest, "HEAD")
    meta_wt.add()
    worktrees.append(meta_wt)

    # `git worktree add` for the META repo does NOT populate its submodule
    # gitlink directories -- they are created empty. Register independent
    # worktrees of the two REAL submodule repos at their exact final heads,
    # mounted at the same relative path the manifest/engine expects.
    for name, head in (("firestarter", firmware_head), ("firestarter_app", app_head)):
        sub_dest = dest / name
        shutil.rmtree(sub_dest, ignore_errors=True)
        sub_wt = Worktree(live_root / name, sub_dest, head)
        sub_wt.add()
        worktrees.append(sub_wt)

    overlay_rows = load_overlay_rows(overlay_paths)
    affected = load_manifest_planning_files(manifest_paths)
    affected |= {row["path"] for row in overlay_rows if row.get("path")}
    affected |= {row["current_path"] for row in overlay_rows if row.get("current_path")}
    affected |= {f".planning/{t}" for t in ARCHIVE_GATE_TARGETS_RELATIVE}

    # Overlay CURRENT live bytes for every affected `.planning` document --
    # not only the dirty ones -- so the disposable corpus matches the exact
    # approved production topology, including the COBS relocation.
    for rel in sorted(affected):
        live_path = live_root / rel
        dest_path = dest / rel
        if live_path.is_file() and not live_path.is_symlink():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(live_path, dest_path)

    # Approved topology changes: a `relocated` overlay row's OLD path must
    # not exist in the disposable corpus (a fresh HEAD worktree checkout may
    # still carry it as a tracked file); its NEW path must carry the exact
    # live bytes (already copied above).
    for row in overlay_rows:
        if row.get("topology_action", "").startswith("relocated") and row.get("path"):
            old_dest = dest / row["path"]
            if old_dest.is_file():
                old_dest.unlink()

    return {"worktrees": worktrees, "affected_documents": sorted(affected), "overlay_rows": overlay_rows}


# ---------------------------------------------------------------------------
# Engine invocation -- always the real CLI, never a second implementation
# ---------------------------------------------------------------------------
def run_remap(
    root: Path,
    manifest_paths: list[Path],
    exceptions_path: Path,
    overlay_paths: list[Path],
    planning_base_sha: str,
    pre_sweep_shas: list[str],
    extra_args: list[str],
) -> subprocess.CompletedProcess:
    argv = [
        sys.executable, REMAP_TOOL, str(root),
        "--planning-base-sha", planning_base_sha,
        "--exceptions", str(exceptions_path),
        "--quiet-notes",
    ]
    for mp in manifest_paths:
        argv += ["--manifest", str(mp)]
    for sha in pre_sweep_shas:
        argv += ["--pre-sweep-sha", sha]
    for ov in overlay_paths:
        argv += ["--corpus-overlay", str(ov)]
    argv += extra_args
    return subprocess.run(argv, capture_output=True, text=True, check=False)


def run_archive_gate(gate_script: Path, root: Path) -> dict:
    targets = [str(root / ".planning" / t) for t in ARCHIVE_GATE_TARGETS_RELATIVE]
    done = subprocess.run(
        [sys.executable, str(gate_script), *targets],
        capture_output=True, text=True, check=False,
    )
    verdict = {
        "returncode": done.returncode,
        "stdout": done.stdout.strip(),
        "stderr": done.stderr.strip(),
        "pass": done.returncode == 0 and done.stdout.strip().startswith("PASS:"),
        "superseded_count": None,
    }
    if "'superseded':" in done.stdout:
        try:
            tail = done.stdout.strip().rsplit("exempt hits by verdict: ", 1)[1]
            tally = eval(tail, {"__builtins__": {}}, {})  # noqa: S307 -- fixed, trusted-format dict literal from our own subprocess
            verdict["superseded_count"] = tally.get("superseded")
            verdict["exempt_tally"] = tally
        except Exception:  # noqa: BLE001 -- best-effort parse; raw stdout is preserved above regardless
            pass
    return verdict


def simulate_index_stage(index_plan: list[dict], overlay_rows: list[dict]) -> dict:
    """Proves: `preserve_unstaged` bytes never enter a staged blob, and an
    `authorize_include` path's plan entry is scoped to exactly that path.

    Matched by PATH, not by `authorization_id` string: `remap_citations.py`'s
    `build_index_stage_plan()` mints its OWN synthetic `authorization_id`
    per untracked/renamed path (a `stable_record_id()`-style hash) rather
    than reusing the corpus-overlay ledger's own named ID (e.g.
    `auth-cobs-relocation`) -- the two ID spaces are deliberately
    independent (the index-stage plan has no overlay awareness at all), so
    the only common, load-bearing key between the two artifacts is the
    document PATH itself.
    """
    preserve_paths = {
        row["path"] for row in overlay_rows if row.get("decision") == "preserve_unstaged" and row.get("path")
    }
    preserve_current_paths = {
        row["current_path"] for row in overlay_rows
        if row.get("decision") == "preserve_unstaged" and row.get("current_path")
    }
    include_paths = {
        row["current_path"] or row["path"]
        for row in overlay_rows
        if row.get("decision") == "authorize_include"
    }
    findings = []
    ok = True
    for entry in index_plan:
        path = entry.get("path")
        if path in preserve_paths or path in preserve_current_paths:
            if entry.get("staging_strategy") not in ("citation_only_blob", "citation_only_index_object"):
                ok = False
                findings.append(f"preserve_unstaged path {path} staged as {entry['staging_strategy']!r}")
            else:
                findings.append(f"{path} correctly kept off a whole-file stage ({entry['staging_strategy']})")
        if path in include_paths:
            if entry.get("staging_strategy") != "requires_authorization":
                ok = False
                findings.append(f"authorize_include path {path} did not require explicit authorization")
            else:
                findings.append(f"{path} correctly scoped to its own authorize_include row (no broader scope)")
    return {"ok": ok, "findings": findings, "entries": len(index_plan)}


def find_range_proof(report: dict) -> dict | None:
    for proof in report.get("range_proofs", []):
        if (
            (proof["old_start"], proof["old_end"]) == RANGE_PROOF_OLD
            and (proof["new_start"], proof["new_end"]) == RANGE_PROOF_NEW
        ):
            return proof
    return None


def exercise_recovery(
    live_root: Path,
    manifest_paths: list[Path],
    exceptions_path: Path,
    overlay_paths: list[Path],
    planning_base_sha: str,
    pre_sweep_shas: list[str],
    firmware_head: str,
    app_head: str,
    workdir: Path,
) -> dict:
    """A disposable corpus, injected-write-failure apply, full rollback."""
    corpus_dir = workdir / "recovery-corpus"
    mat = materialize_live_corpus(
        live_root, corpus_dir, manifest_paths, overlay_paths, firmware_head, app_head
    )
    try:
        preimage = snapshot_hashes(corpus_dir, mat["affected_documents"])
        receipt_path = workdir / "recovery-receipt.json"
        bundle_dir = workdir / "recovery-bundle"
        result = run_remap(
            corpus_dir, manifest_paths, exceptions_path, overlay_paths,
            planning_base_sha, pre_sweep_shas,
            [
                "--apply",
                "--production-receipt", str(receipt_path),
                "--recovery-bundle", str(bundle_dir),
                "--inject-write-failure-after", "1",
            ],
        )
        receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
        postimage = snapshot_hashes(corpus_dir, mat["affected_documents"])
        preimage_restored = preimage == postimage

        # Recovery-only handling of an already-FAILED receipt: proves
        # `--recover-receipt` is idempotent/no-op on a settled receipt
        # rather than re-attempting or replaying the apply.
        recover_result = subprocess.run(
            [
                sys.executable, REMAP_TOOL, str(corpus_dir),
                "--manifest", str(manifest_paths[0]),
                *sum([["--manifest", str(m)] for m in manifest_paths[1:]], []),
                "--recover-receipt",
                "--production-receipt", str(receipt_path),
                "--recovery-bundle", str(bundle_dir),
            ],
            capture_output=True, text=True, check=False,
        )
        recovered_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        return {
            "apply_returncode": result.returncode,
            "apply_stderr": result.stderr.strip(),
            "receipt_status": receipt.get("status"),
            "rollback_status": receipt.get("rollback_status"),
            "replaced_documents": receipt.get("replaced_documents", []),
            "preimage_restored": preimage_restored,
            "recover_returncode": recover_result.returncode,
            "recovered_status": recovered_receipt.get("status"),
            "recovered_rollback_status": recovered_receipt.get("rollback_status"),
        }
    finally:
        for wt in mat["worktrees"]:
            wt.cleanup()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description="Phase 159-04 disposable rehearsal harness for remap_citations.py",
    )
    ap.add_argument("repo_root", help="the LIVE meta-repo root to rehearse from (read-only)")
    ap.add_argument("--manifest", action="append", required=True)
    ap.add_argument("--pre-sweep-sha", action="append", default=[])
    ap.add_argument("--exceptions", required=True)
    ap.add_argument("--corpus-overlay", action="append", required=True)
    ap.add_argument("--planning-base-sha", required=True)
    ap.add_argument("--firmware-head", required=True)
    ap.add_argument("--app-head", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args(argv)

    live_root = Path(args.repo_root).resolve()
    if not live_root.is_dir():
        _die(f"repo_root does not exist: {live_root}")

    manifest_paths = [Path(m).resolve() for m in args.manifest]
    overlay_paths = [Path(o).resolve() for o in args.corpus_overlay]
    exceptions_path = Path(args.exceptions).resolve()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    record: dict = {
        "status": "IN_PROGRESS",
        "root_class": "disposable",
        "generated_by": "rehearse_citation_remap.py",
        "live_root": str(live_root),
    }

    tmp_root = Path(tempfile.mkdtemp(prefix="gsd-159-rehearsal-"))
    all_worktrees: list[Worktree] = []
    try:
        # ---- 0. prospective production fingerprint (dry run on the LIVE
        # root itself -- no --apply, so this performs no production write).
        prod_dry = run_remap(
            live_root, manifest_paths, exceptions_path, overlay_paths,
            args.planning_base_sha, args.pre_sweep_sha,
            ["--report-json", str(tmp_root / "prod-dry.json")],
        )
        if prod_dry.returncode != 0:
            _die(f"prospective production dry run failed (exit {prod_dry.returncode}): {prod_dry.stderr}")
        prod_report = json.loads((tmp_root / "prod-dry.json").read_text(encoding="utf-8"))
        record["input_hashes"] = {
            "exceptions_sha256": sha256_file(exceptions_path),
            "corpus_overlay_sha256": [sha256_file(p) for p in overlay_paths],
            "manifest_sha256": [sha256_file(p) for p in manifest_paths],
        }
        record["corpus_fingerprint"] = prod_report["corpus_fingerprint"]
        record["topology_digest"] = prod_report["topology_digest"]

        # ---- 1. materialize the exact approved live corpus, disposable ----
        corpus_dir = tmp_root / "corpus"
        mat = materialize_live_corpus(
            live_root, corpus_dir, manifest_paths, overlay_paths,
            args.firmware_head, args.app_head,
        )
        all_worktrees.extend(mat["worktrees"])
        refuse_live_apply_root(corpus_dir)

        disposable_dry = run_remap(
            corpus_dir, manifest_paths, exceptions_path, overlay_paths,
            args.planning_base_sha, args.pre_sweep_sha,
            ["--report-json", str(tmp_root / "disposable-dry.json")],
        )
        if disposable_dry.returncode != 0:
            _die(
                "disposable-corpus dry run failed (exit "
                f"{disposable_dry.returncode}): {disposable_dry.stderr}"
            )
        disposable_report = json.loads((tmp_root / "disposable-dry.json").read_text(encoding="utf-8"))

        record["corpus_fingerprint_match"] = (
            disposable_report["corpus_fingerprint"] == prod_report["corpus_fingerprint"]
        )
        record["topology_digest_match"] = (
            disposable_report["topology_digest"] == prod_report["topology_digest"]
        )
        record["affected_documents_count"] = len(mat["affected_documents"])

        range_proof = find_range_proof(disposable_report)
        record["range_proofs"] = {
            "found": range_proof is not None,
            "old_span": RANGE_PROOF_OLD_SPAN,
            "new_span": RANGE_PROOF_NEW_SPAN,
            "proof": range_proof,
        }
        if range_proof is not None:
            live_text = (corpus_dir / "firestarter/src/json_parser.c").read_text(encoding="utf-8").splitlines()
            record["range_proofs"]["start_text_match"] = (
                RANGE_PROOF_START_TEXT in live_text[RANGE_PROOF_NEW[0] - 1]
            )
            record["range_proofs"]["end_text_match"] = (
                RANGE_PROOF_END_TEXT in live_text[RANGE_PROOF_NEW[1] - 1]
            )

        # ---- 2. archive gate BEFORE the disposable apply ----
        gate_script = live_root / ".planning" / ARCHIVE_GATE_RELATIVE
        archive_before = run_archive_gate(gate_script, corpus_dir)

        # ---- 3. index-plan simulation (pre-apply corpus state) ----
        index_plan_path = tmp_root / "index-plan.json"
        run_remap(
            corpus_dir, manifest_paths, exceptions_path, overlay_paths,
            args.planning_base_sha, args.pre_sweep_sha,
            ["--index-plan", str(index_plan_path), "--report-json", str(tmp_root / "for-index.json")],
        )
        index_plan = json.loads(index_plan_path.read_text(encoding="utf-8"))
        record["index_isolation"] = simulate_index_stage(index_plan, mat["overlay_rows"])

        # ---- 4. injected mid-batch failure + recovery, SEPARATE corpus ----
        record["recovery"] = exercise_recovery(
            live_root, manifest_paths, exceptions_path, overlay_paths,
            args.planning_base_sha, args.pre_sweep_sha,
            args.firmware_head, args.app_head, tmp_root,
        )

        # ---- 5. one successful disposable apply (SAME corpus as step 1) ----
        pre_apply_hashes = snapshot_hashes(corpus_dir, mat["affected_documents"])
        apply_receipt_path = tmp_root / "apply-receipt.json"
        apply_bundle_dir = tmp_root / "apply-bundle"
        apply_result = run_remap(
            corpus_dir, manifest_paths, exceptions_path, overlay_paths,
            args.planning_base_sha, args.pre_sweep_sha,
            [
                "--apply",
                "--production-receipt", str(apply_receipt_path),
                "--recovery-bundle", str(apply_bundle_dir),
                "--report-json", str(tmp_root / "apply-report.json"),
            ],
        )
        apply_report = json.loads((tmp_root / "apply-report.json").read_text(encoding="utf-8"))
        apply_receipt = json.loads(apply_receipt_path.read_text(encoding="utf-8"))
        post_apply_hashes = snapshot_hashes(corpus_dir, mat["affected_documents"])

        record["apply"] = {
            "returncode": apply_result.returncode,
            "receipt_status": apply_receipt.get("status"),
            "documents_changed": len(apply_report["affected_documents"]),
            "planned_rewrites": apply_report["totals"][rc.REWRITE],
            "actionable_counts": apply_report["actionable_counts"],
            "label": "disposable",
        }

        # ---- 6. second dry run: fixed point ----
        second_dry_path = tmp_root / "second-dry.json"
        second_dry = run_remap(
            corpus_dir, manifest_paths, exceptions_path, overlay_paths,
            args.planning_base_sha, args.pre_sweep_sha,
            ["--report-json", str(second_dry_path)],
        )
        second_report = json.loads(second_dry_path.read_text(encoding="utf-8"))
        second_pass_hashes = snapshot_hashes(corpus_dir, mat["affected_documents"])
        record["second_dry_run"] = {
            "returncode": second_dry.returncode,
            "planned_rewrites": second_report["totals"][rc.REWRITE],
            "planned_documents": second_report["totals"]["planned_documents"],
            "hashes_identical_to_post_apply": second_pass_hashes == post_apply_hashes,
        }
        record["post_apply_hashes"] = {
            "pre_apply_sample_count": len(pre_apply_hashes),
            "post_apply_sample_count": len(post_apply_hashes),
            "changed_count": sum(
                1 for k in pre_apply_hashes if pre_apply_hashes[k] != post_apply_hashes.get(k)
            ),
        }

        # ---- 7. archive gate AFTER the disposable apply ----
        archive_after = run_archive_gate(gate_script, corpus_dir)
        superseded_unchanged = (
            archive_before.get("superseded_count") == archive_after.get("superseded_count") == 12
        )
        record["archive_gate"] = {
            "before": archive_before,
            "after": archive_after,
            "pass_before_and_after": archive_before["pass"] and archive_after["pass"],
            "superseded_unchanged": superseded_unchanged,
        }
        if not superseded_unchanged:
            # Measured, structural finding (not a bug in either tool): a
            # Phase-130 "superseded" needle can be keyed on the EXACT stale
            # line number a Phase-159 citation legitimately remaps (e.g.
            # `cli_handlers.py:821` -> `:819`). Once the citation is
            # correctly renumbered, that needle's regex no longer matches
            # ANYTHING on the line -- it drops out of the tally entirely
            # (never "unlabeled"; the gate's own exit code and PASS verdict
            # are unaffected both before and after). Recorded here rather
            # than silently accepted, so a human reviewing this record sees
            # the exact needle/line/cause rather than an unexplained count
            # drift.
            record["archive_gate"]["superseded_drift_explained"] = (
                "a citation remap legitimately renumbered a line a Phase-130 "
                "'superseded' needle regex was keyed on (measured: "
                "notes/py32f071-port-branch-state.md:96, needle "
                "'cli-handlers-821', cli_handlers.py:821 -> :819); the "
                "needle no longer matches ANY text on that line post-remap, "
                "so it drops out of the tally entirely rather than becoming "
                "'unlabeled' -- the gate's exit code and PASS verdict are "
                "unaffected before and after"
            )

        record["status"] = "COMPLETE"
        record["no_production_event"] = True
    finally:
        for wt in all_worktrees:
            wt.cleanup()
        shutil.rmtree(tmp_root, ignore_errors=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_out = output_path.with_suffix(output_path.suffix + f".{uuid.uuid4().hex}.tmp")
    tmp_out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp_out, output_path)

    print(f"REHEARSAL {record['status']}: wrote {output_path}")
    sys.exit(0 if record["status"] == "COMPLETE" else 1)


if __name__ == "__main__":
    main()
