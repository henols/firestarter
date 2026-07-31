"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 125 Plan 03 -- ROADMAP Criterion 1's exit-code-producing proof that no
commit from PR #45 (feature/common-vpp-calibration, closed) is an ancestor of
this firmware integration branch.

Requirements: VPP-01
Decisions covered: the Criterion-1 discretion default (a scripted check
producing an exit code, never a prose assertion).

Defect class this replaces. ROADMAP Criterion 1's own named mechanism
(`git log --all --grep`/SHA lookup) is wrong in two independent ways, both
measured rather than assumed:

  1. `--grep` searches commit MESSAGES, not commit objects. `git log --all
     --grep=<sha> --oneline` returns zero rows today, and would still return
     zero rows after a cherry-pick whose message was rewritten -- which is
     precisely the evasion Criterion 1 exists to catch. A gate built on it
     passes vacuously forever.
  2. Any reachability question asked against the WHOLE object graph
     (`--all`) gets the wrong answer, because
     origin/feature/common-vpp-calibration is a fetched local
     remote-tracking ref: research measured all ten of PR #45's commits
     reachable that way, and none of them reachable from HEAD. Every
     reachability question in this module therefore names HEAD as its
     scope, never `--all`.

This module asserts directly against the live tree via `git` subprocess
calls, invoked in list form without a shell -- it imports no check_*.py
machinery.

Self-contained path resolution below -- NOT in conftest.py (firestarter/
tests/ has no conftest.py anywhere in the repo, and none of pytest.ini,
pyproject.toml, setup.cfg or tox.ini exist either; a recorded house-rule
pattern decision, not an omission). Stdlib and pytest only.

Coverage:
  1. test_pr45_commit_list_is_never_vacuous -- before any ancestry question
     is asked anywhere in this module: the module-level commit tuple has
     exactly ten entries, the ten entries are distinct, and each entry's
     commit object resolves locally (`git cat-file -e <sha>^{commit}` exits
     0). A non-zero exit here is a TOOL-ERROR class, never read as "not an
     ancestor" -- research recorded this as a real fresh-clone hazard: the
     objects resolve here only because
     origin/feature/common-vpp-calibration is fetched.
  2. test_no_pr45_commit_is_an_ancestor_of_head -- for each of the ten,
     `git merge-base --is-ancestor <sha> HEAD` is classified into exactly
     three buckets: exit 0 means the commit IS an ancestor (collected as a
     violation), exit 1 means clean, any other exit is a loud tool-error
     failure quoting the captured stderr. The number of commits actually
     examined is asserted to equal ten, so a loop that silently skipped
     entries cannot pass; the collected violation list is asserted empty,
     naming every offending commit on failure.
"""

import shutil
import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent

# Exactly the ten commits `git rev-list origin/beta..origin/feature/common-vpp-calibration`
# enumerates, in chronological order (RESEARCH C-3). Merge base with
# origin/beta is a1953c22862ac3fb1e0111985946644a568aee36; PR #45's branch
# tip is a47228d862b9b53e6d936d1d0993bee9fc74940e.
PR45_SHAS = (
    "04fd9b3",
    "fc0b2c7",
    "86f351a",
    "768580f",
    "05f4a77",
    "b964ee6",
    "9134f2a",
    "d285b83",
    "71278d0",
    "a47228d",
)


def _resolve_git():
    """Resolve the `git` binary, fail-closed.

    Deliberately never bypassed via any decorator or runtime call that would
    mark this outcome as skipped, anywhere in this module: doing so would
    recreate the exact BASE-02/BASE-03 absence-proxy failure class this
    milestone's Phase 123 removed. If `git` cannot be resolved via
    shutil.which, this raises via a plain assert, which the test runner
    reports as a FAILURE, never a skipped outcome.
    """
    git_bin = shutil.which("git")
    assert git_bin is not None, (
        "`git` binary not found on PATH. This must FAIL the suite, never be "
        "silently skipped -- every reachability assertion in this module "
        "depends on it."
    )
    return git_bin


def _git(*args):
    """Run `git` against this repository, with an explicit -C repository
    root argument, taking the remaining arguments as a list. List argv
    only, never a shell, never a composed command string. Returns the
    CompletedProcess with both streams captured as text."""
    git_bin = _resolve_git()
    argv = [git_bin, "-C", str(_REPO_ROOT), *args]
    return subprocess.run(argv, capture_output=True, text=True)


def test_pr45_commit_list_is_never_vacuous():
    """Coverage 1 -- before any ancestry question is asked anywhere in this
    module: the commit tuple has exactly ten entries, the ten entries are
    distinct, and each entry's commit object resolves locally. A non-zero
    exit from the object-existence query here is the TOOL-ERROR class: the
    failure message names origin/feature/common-vpp-calibration as the ref
    to fetch and states explicitly that an absent object must NOT read as
    "not an ancestor". RESEARCH recorded this as a real fresh-clone hazard
    -- the objects resolve here only because that ref is fetched."""
    assert len(PR45_SHAS) == 10, (
        f"never-vacuous: expected exactly 10 PR #45 commit SHAs, got "
        f"{len(PR45_SHAS)}: {PR45_SHAS!r}"
    )
    assert len(set(PR45_SHAS)) == 10, (
        f"never-vacuous: expected all 10 PR #45 commit SHAs to be distinct, "
        f"got duplicates in {PR45_SHAS!r}"
    )
    for sha in PR45_SHAS:
        result = _git("cat-file", "-e", f"{sha}^{{commit}}")
        assert result.returncode == 0, (
            f"{sha} did not resolve as a local commit object (exit "
            f"{result.returncode}). This is a TOOL-ERROR, never a silent "
            f"'not an ancestor' pass -- fetch "
            f"origin/feature/common-vpp-calibration first, then re-run.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def test_no_pr45_commit_is_an_ancestor_of_head():
    """Coverage 2 -- for each of the ten PR #45 commits, classify
    `git merge-base --is-ancestor <sha> HEAD`'s exit code into exactly
    three buckets: 0 means the commit IS an ancestor of HEAD (collected as
    a violation), 1 means clean, anything else is a loud tool-error failure
    quoting the captured stderr. Never a negated single call -- RESEARCH
    measured a fabricated reference producing exit 128 with a fatal
    message, which a naive negation reads as clean. The examined count is
    asserted to equal ten, so a loop that silently skipped entries cannot
    pass. A green run here means: ten commits examined, each object
    present, each not reachable from HEAD. Every reachability query in this
    module names HEAD as its scope -- never `--all`, which would find all
    ten commits reachable via the fetched
    origin/feature/common-vpp-calibration ref regardless of HEAD."""
    checked = 0
    ancestors = []
    for sha in PR45_SHAS:
        result = _git("merge-base", "--is-ancestor", sha, "HEAD")
        if result.returncode == 0:
            ancestors.append(sha)
        elif result.returncode == 1:
            pass
        else:
            raise AssertionError(
                f"git merge-base --is-ancestor {sha} HEAD failed "
                f"unexpectedly with exit {result.returncode} (expected 0 "
                f"or 1) -- treat this as a tool error, never as clean.\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        checked += 1
    assert checked == 10, (
        f"never-vacuous: expected exactly 10 commits examined, got "
        f"{checked} -- a loop that silently skipped entries must not pass."
    )
    assert not ancestors, (
        f"PR #45 commit(s) reachable from HEAD, which must never happen: "
        f"{ancestors}. VPP-01 requires nothing be cherry-picked from PR #45."
    )
