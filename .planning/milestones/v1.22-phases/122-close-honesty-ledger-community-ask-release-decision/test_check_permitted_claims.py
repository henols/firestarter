"""Tests for check_permitted_claims.py (Phase 122 Plan 01, Wave 0).

This is the MANDATORY anti-hollow pairing for the claim gate (GATE-01): a
checker with no negative-fixture test is exactly this project's v1.12
hollow-GATE-03 failure mode -- a declared-empty detector that could never
fail because nothing concrete was asserted against it. Every planted-
violation test below invokes the checker as a real subprocess against a
committed fixture file via the FIRESTARTER_CLAIMSCAN_TARGETS env seam --
never an in-process import -- so a passing test suite proves the checker
itself (not the test) fails the build on a real violation. The scanner is
never imported directly in this module.

Coverage:
  1. Clean-pass baseline via the seam: exits 0, PASS: in stdout. Also the
     control leg proving the injection seam itself is innocent.
  2. Planted forbidden-phrase violation (planted_forbidden_claim.md) flips
     the checker to a non-zero exit with FAIL: and the should-now-work
     label -- the real C-5/D-14 near-miss wording.
  3. Planted missing-caveat violation (planted_missing_caveat.md) flips the
     checker to a non-zero exit naming the missing-caveat bucket.
  4. Fail-closed on a nonexistent scan target.
  5. Never-vacuous on an explicitly empty FIRESTARTER_CLAIMSCAN_TARGETS --
     and explicitly does NOT fall back to the real default targets.
  6. PASS-line names both scanned files at once (anti-skip).
  7. Positional argv overrides the env seam (documented precedence, pinned
     against a future silent inversion).
"""

import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_SCANNER = _HERE / "check_permitted_claims.py"


def _run_scanner(targets=None, argv=None):
    """Invoke the scanner as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_CLAIMSCAN_TARGETS to that
    exact string (so the empty string is reachable, per test 5) -- when
    None, the env var is left absent from the child's environment entirely,
    reaching the "variable absent -> use real defaults" path.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# Test 1: clean-pass baseline via the seam (also the seam-innocence control)
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
# Test 2: planted forbidden-phrase violation (anti-hollow, GATE-01)
# ---------------------------------------------------------------------------


def test_planted_forbidden_phrase_flips_checker_to_failure():
    """The committed planted_forbidden_claim.md fixture MUST fail the gate,
    attributed to the should-now-work label -- the real C-5/D-14 near-miss
    wording ('AT28C parts should now work')."""
    result = _run_scanner(targets="fixtures/planted_forbidden_claim.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted forbidden-phrase violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "should-now-work" in result.stdout, (
        f"Expected the should-now-work label in output but got:\n{result.stdout}"
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
# Test 4: fail-closed on a nonexistent scan target
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
# Test 5: never-vacuous on an explicitly empty target list
# ---------------------------------------------------------------------------


def test_never_vacuous_on_explicitly_empty_target_list():
    """FIRESTARTER_CLAIMSCAN_TARGETS explicitly set to the empty string MUST
    resolve to zero targets and exit non-zero -- and must NOT silently fall
    back to the real default targets (which do not exist yet at this wave,
    so a fall-back would ALSO exit 1, but for the wrong reason and without
    a PASS:; this test asserts the never-vacuous message specifically,
    isolating the correct failure mode from that coincidental one)."""
    result = _run_scanner(targets="")
    assert result.returncode != 0, (
        f"scanner exited 0 with an explicitly empty target list.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout
    assert "no scan targets resolved" in result.stdout, (
        f"Expected the never-vacuous message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Test 6: PASS line names every scanned file (anti-skip)
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
# Test 7: positional argv overrides the env seam (precedence pin)
# ---------------------------------------------------------------------------


def test_positional_argv_overrides_the_env_seam():
    """Positional argv must win over FIRESTARTER_CLAIMSCAN_TARGETS. The env
    seam is pointed at the planted violation while argv passes the clean
    control -- the run must succeed, pinning the documented precedence so a
    future change cannot silently invert it."""
    result = _run_scanner(
        targets="fixtures/planted_forbidden_claim.md",
        argv=["fixtures/clean_control.md"],
    )
    assert result.returncode == 0, (
        f"scanner exited {result.returncode} even though argv should have "
        f"overridden the env seam.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
