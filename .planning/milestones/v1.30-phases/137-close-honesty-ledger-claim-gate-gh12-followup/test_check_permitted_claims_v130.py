"""Tests for check_permitted_claims.py (Phase 137 Plan 01, CLOSE-02).

This is the MANDATORY anti-hollow pairing for the v1.30 claim gate: a
checker with no negative-fixture test is exactly this project's v1.12
hollow-GATE-03 failure mode -- a declared-empty detector that could never
fail because nothing concrete was asserted against it. Every planted-
violation test below invokes the checker as a real subprocess against a
committed fixture file via the FIRESTARTER_CLAIMSCAN_TARGETS_V130 env seam
-- never an in-process import -- so a passing test suite proves the checker
itself (not the test) fails the build on a real violation. The scanner is
never imported directly for the subprocess-driven legs (tests 1-9); tests
10-11 introspect the module's own `_DEFAULT_TARGETS` list by file-path
import, per PITFALLS.md P-11's own prescription for the two mandatory new
legs, without ever importing it as a package.

Renamed from `test_check_permitted_claims.py` to
`test_check_permitted_claims_v130.py` (PITFALLS P-11 point 5) -- a THIRD
file literally named `test_check_permitted_claims.py`, alongside the v1.22
and v1.23 copies already on disk in sibling phase directories, would
collide under pytest's default `prepend` import mode for anyone running
pytest from `/workspaces`.

Coverage:
  1. Clean-pass baseline via the seam: exits 0, PASS: in stdout.
  2. Planted forbidden-phrase violation (planted_forbidden_claim.md) flips
     the checker to a non-zero exit with FAIL: and the
     lock-inhibited-the-write label -- the real Evidence Ceiling overclaim
     this milestone is built to prevent.
  3. Planted missing-caveat violation (planted_missing_caveat.md) flips the
     checker to a non-zero exit naming the missing-caveat bucket.
  4. Planted self-verifying violation (planted_self_verifying_unqualified.md)
     flips the checker to a non-zero exit naming the self-verifying label.
  5. Fail-closed on a nonexistent scan target.
  6. Never-vacuous on an explicitly empty FIRESTARTER_CLAIMSCAN_TARGETS_V130
     -- and explicitly does NOT fall back to the real default targets.
  7. PASS-line names both scanned files at once (anti-skip).
  8. Positional argv overrides the env seam (documented precedence, pinned
     against a future silent inversion).
  9. ARMED and GREEN against the four real default targets -- invoked with
     no argv and no env override (the real defaults), all four of Phase
     137's own closing artifacts now exist on disk (137-LEDGER.md,
     137-DECISION.md, 137-RELEASE-NOTES-app.md, 137-GH12-COMMENT.md,
     authored by plans 137-03/04/05), and the scanner exits 0 with a
     PASS: line naming all four basenames. This is the literal, first-ever
     real-defaults run of this gate in this milestone -- the mechanical
     discharge of CLOSE-01. Supersedes the prior UNARMED-expecting leg this
     test replaces (its own docstring anticipated exactly this edit: "stays
     green until 137-06 makes all four exist").
  10. (MANDATORY P-11 leg 1) The scanner's own `_DEFAULT_TARGETS` resolve
      strictly INSIDE this phase's own directory -- the assertion that makes
      a future naive copy into another phase directory fail loudly instead
      of silently resolving elsewhere (the exact v1.23 defect).
  11. (MANDATORY P-11 leg 2) Every `_DEFAULT_TARGETS` basename carries this
      phase's own "137-" number prefix -- a copy carrying stale "130-*" or
      "122-*" names goes red immediately here.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_SCANNER = _HERE / "check_permitted_claims.py"


def _run_scanner(targets=None, argv=None):
    """Invoke the scanner as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_CLAIMSCAN_TARGETS_V130 to
    that exact string (so the empty string is reachable, per test 6) --
    when None, the env var is left absent from the child's environment
    entirely, reaching the "variable absent -> use real defaults" path.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_V130"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_V130", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


def _import_scanner_module():
    """Import check_permitted_claims.py by file path (never as a package)
    solely to introspect its module-level `_DEFAULT_TARGETS` constant --
    used only by legs 10 and 11, which must inspect the real list the
    running process would use, not a re-derived copy."""
    spec = importlib.util.spec_from_file_location(
        "check_permitted_claims_v130_introspect", str(_SCANNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Test 1: clean-pass baseline via the seam
# ---------------------------------------------------------------------------


def test_scanner_exits_zero_on_clean_fixture():
    """A clean fixture injected via the env seam must exit 0 with PASS: --
    proves the seam itself introduces no false positive."""
    result = _run_scanner(targets="fixtures/clean_control.md")
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} on a clean fixture.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 2: planted forbidden-phrase violation (anti-hollow)
# ---------------------------------------------------------------------------


def test_planted_forbidden_phrase_flips_checker_to_failure():
    """The committed planted_forbidden_claim.md fixture MUST fail the gate,
    attributed to the lock-inhibited-the-write label -- the real Evidence
    Ceiling overclaim ('the lock inhibited the write')."""
    result = _run_scanner(targets="fixtures/planted_forbidden_claim.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted forbidden-phrase violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "lock-inhibited-the-write" in result.stdout, (
        f"Expected the lock-inhibited-the-write label in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 3: planted missing-caveat violation
# ---------------------------------------------------------------------------


def test_planted_missing_caveat_flips_checker_to_failure():
    """The committed planted_missing_caveat.md fixture MUST fail the gate,
    naming the missing required-caveat bucket."""
    result = _run_scanner(targets="fixtures/planted_missing_caveat.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted missing-caveat violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "missing required silicon caveat" in result.stdout, (
        f"Expected the missing-caveat bucket label in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 4: planted self-verifying violation (relational rule)
# ---------------------------------------------------------------------------


def test_planted_self_verifying_unqualified_flips_checker_to_failure():
    """The committed planted_self_verifying_unqualified.md fixture MUST fail
    the gate, naming the self-verifying label -- the qualifying caveat sits
    far enough away in that fixture that the relational rule's window does
    not see it."""
    result = _run_scanner(targets="fixtures/planted_self_verifying_unqualified.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted self-verifying violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "self-verifying" in result.stdout, (
        f"Expected the self-verifying label in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 5: fail-closed on a nonexistent scan target
# ---------------------------------------------------------------------------


def test_fail_closed_on_nonexistent_target():
    """A scan target that does not exist on disk MUST fail closed (exit
    non-zero), never vacuously pass with the target silently skipped."""
    result = _run_scanner(targets="fixtures/does-not-exist.md")
    assert result.returncode != 0, (
        f"scanner exited 0 with a missing scan target.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "not found on disk" in result.stdout, (
        f"Expected a not-found message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 6: never-vacuous on an explicitly empty target list
# ---------------------------------------------------------------------------


def test_never_vacuous_on_explicitly_empty_target_list():
    """FIRESTARTER_CLAIMSCAN_TARGETS_V130 explicitly set to the empty string
    MUST resolve to zero targets and exit non-zero -- and must NOT silently
    fall back to the real default targets (which are currently all absent,
    so a fall-back would ALSO exit 0 via the UNARMED branch -- this test
    asserts the never-vacuous message specifically, isolating the correct
    failure mode from that coincidental one)."""
    result = _run_scanner(targets="")
    assert result.returncode != 0, (
        f"scanner exited 0 with an explicitly empty target list.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout
    assert "UNARMED:" not in result.stdout
    assert "no scan targets resolved" in result.stdout, (
        f"Expected the never-vacuous message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 7: PASS line names every scanned file (anti-skip)
# ---------------------------------------------------------------------------


def test_pass_line_names_every_scanned_file():
    """Pointing the scanner at both clean controls at once must produce a
    single PASS: line naming BOTH basenames -- proves neither file was
    silently skipped."""
    result = _run_scanner(
        targets=os.pathsep.join(
            ["fixtures/clean_control.md", "fixtures/clean_control_second.md"]
        )
    )
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} on two clean controls.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "clean_control.md" in result.stdout
    assert "clean_control_second.md" in result.stdout, (
        f"Expected both basenames in the PASS: line but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 8: positional argv overrides the env seam (precedence pin)
# ---------------------------------------------------------------------------


def test_positional_argv_overrides_the_env_seam():
    """Positional argv must win over FIRESTARTER_CLAIMSCAN_TARGETS_V130. The
    env seam is pointed at the planted violation while argv passes the
    clean control -- the run must succeed, pinning the documented
    precedence so a future change cannot silently invert it."""
    result = _run_scanner(
        targets="fixtures/planted_forbidden_claim.md",
        argv=["fixtures/clean_control.md"],
    )
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} even though argv should have "
        f"overridden the env seam.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Test 9: ARMED and GREEN against the four real default targets
# ---------------------------------------------------------------------------


def test_armed_and_green_against_the_four_real_artifacts():
    """Invoked with no argv and no env var set (the real defaults), the
    scanner MUST exit 0 with a PASS: line naming all four real 137-prefixed
    closing artifacts. All four now exist on disk (137-LEDGER.md from
    137-03, 137-DECISION.md and 137-RELEASE-NOTES-app.md from 137-04,
    137-GH12-COMMENT.md from 137-05), so the all-or-nothing arming branch's
    UNARMED: case no longer applies -- this is the literal, first-ever
    real-defaults run of this gate in this milestone, the mechanical
    discharge of CLOSE-01. A regression here means either the arming
    mechanism broke, or one of the four real artifacts now fails the
    forbidden-phrase/caveat scan -- in neither case should this test be
    weakened to pass; the flagged artifact must be fixed instead."""
    result = _run_scanner(targets=None, argv=None)
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} against the four real default "
        f"targets -- expected PASS + exit 0.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )
    for name in (
        "137-LEDGER.md",
        "137-DECISION.md",
        "137-RELEASE-NOTES-app.md",
        "137-GH12-COMMENT.md",
    ):
        assert name in result.stdout, (
            f"Expected {name!r} named in the PASS: message but got:\n{result.stdout}"
        )


# ---------------------------------------------------------------------------
# Test 10 (MANDATORY P-11 leg 1): default targets resolve inside this
# phase's own directory
# ---------------------------------------------------------------------------


def test_default_targets_resolve_inside_this_phase_directory():
    """The scanner's own `_DEFAULT_TARGETS` must resolve strictly INSIDE
    this phase's own directory (`_HERE`, computed fresh from `__file__`),
    never a sibling phase directory named by a string constant. This is the
    one assertion that makes a future naive copy into another phase
    directory fail loudly (a stale sibling-dir string constant, the v1.23
    P-11 defect) instead of silently resolving elsewhere and passing
    vacuously."""
    module = _import_scanner_module()
    expected_dir = str(_HERE.resolve())
    for entry in module._DEFAULT_TARGETS:
        assert os.path.dirname(entry) == expected_dir, (
            f"_DEFAULT_TARGETS entry {entry!r} does not resolve inside this "
            f"phase's own directory {expected_dir!r} -- this is the exact "
            "cross-phase-copy defect this test exists to catch"
        )


# ---------------------------------------------------------------------------
# Test 11 (MANDATORY P-11 leg 2): default target basenames carry this
# milestone's own number prefix
# ---------------------------------------------------------------------------


def test_default_target_basenames_are_this_milestones():
    """Every `_DEFAULT_TARGETS` basename must start with this phase's own
    "137-" prefix. A copy carrying stale "130-*" or "122-*" names would go
    red immediately here."""
    module = _import_scanner_module()
    for entry in module._DEFAULT_TARGETS:
        basename = os.path.basename(entry)
        assert basename.startswith("137-"), (
            f"_DEFAULT_TARGETS basename {basename!r} does not carry this "
            "milestone's own '137-' prefix -- this is the exact stale-name "
            "defect this test exists to catch"
        )
