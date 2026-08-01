"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 128 Plan 01 — the BASE-08 anti-hollow pairing for
scripts/check_release_assets.py.

Requirements: REL-03, REL-02
Decisions covered: D-11, D-12

This is the MANDATORY anti-hollow pairing for the REL-03/REL-02 AVR-assets-
present gate: a checker with no negative-fixture test is exactly this
project's v1.12 hollow-GATE-03 failure mode -- a gate that could never fail
because nothing concrete was asserted against it. Every planted-violation test
below invokes scripts/check_release_assets.py as a real subprocess (list-form
argv, never shell=True, never an in-process import) against a committed
fixture under tests/fixtures/, so a passing suite here proves the checker
itself -- not this test module -- fails the build on a real missing or
zero-byte AVR asset.

No `pio` invocation happens anywhere in this module: every fixture is a
committed pio_build/ tree (clean_release_assets_all_three for the control,
planted_release_assets_missing_uno328pb and planted_release_assets_zero_byte_
leonardo for the two planted violations). The checker never mentions,
requires, or looks for the py32f071 image -- REL-03's whole point is that its
absence must not block the three AVR assets, and the clean control fixture
deliberately contains no py32 image anywhere.

Coverage:
  1. Clean control tree exits 0, stdout starts with PASS: and names all three
     envs (uno, uno328pb, leonardo).
  2. Planted missing-hex tree (uno328pb absent) exits 1, stdout contains
     FAIL: and the substring uno328pb and the expected path; stdout never
     contains PASS:.
  3. Planted zero-byte tree (leonardo truncated to 0 bytes) exits 1, stdout
     contains FAIL: and names leonardo and the observed size 0.
  4. A baseline whose avr_targets is an empty object exits 1 (the
     never-vacuous guard) and never prints PASS:.
  5. A baseline that is not valid JSON, has no avr_targets key, or whose
     avr_targets is not an object each exit exactly 2.
  6. An unknown argv flag, or a flag missing its required value, each exit 2.
  7. FIRESTARTER_PIO_BUILD_ROOT set in the child environment to the planted
     missing-hex tree flips a would-be-clean invocation (no --build-root
     given) to exit 1 -- proving the seam is genuinely read, not embedded.
  8. FIRESTARTER_SIZE_BASELINE set in the child environment to a tampered
     baseline carrying a fourth avr_targets key flips the clean tree to
     exit 1, naming that fourth env -- proving this seam is genuinely read
     too.
  9. The clean tree contains no py32 image anywhere and the checker still
     exits 0 and never mentions "py32" in its output (REL-03's tolerance).
  10. beta-build.yml, with comment lines stripped, contains no line setting
      the release action's unmatched-files failure input as a YAML key
      (the REL-02 invariant this plan closes the slice of).

Derivation of each fixture (single stated edit, diffable against the named
source):

  planted_release_assets_missing_uno328pb/
    = clean_release_assets_all_three/ with uno328pb/firestarter_uno328pb.hex
      (and the now-empty uno328pb/ directory) removed entirely.

  planted_release_assets_zero_byte_leonardo/
    = clean_release_assets_all_three/ with
      leonardo/firestarter_leonardo.hex truncated to zero bytes.

Self-contained path resolution below -- NOT in conftest.py (firestarter/tests/
has no conftest.py anywhere in the repo; this is a recorded house-rule pattern
decision, per test_update_version.py's own comment, not an omission). Stdlib
and pytest only.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_CHECKER = _REPO_ROOT / "scripts" / "check_release_assets.py"
_FIXTURES = _HERE / "fixtures"
_BASELINE = _REPO_ROOT / "scripts" / "baseline" / "size_baseline.json"
_BETA_BUILD = _REPO_ROOT / ".github" / "workflows" / "beta-build.yml"

_CLEAN_BUILD_ROOT = _FIXTURES / "clean_release_assets_all_three" / "pio_build"
_MISSING_BUILD_ROOT = _FIXTURES / "planted_release_assets_missing_uno328pb" / "pio_build"
_ZERO_BYTE_BUILD_ROOT = _FIXTURES / "planted_release_assets_zero_byte_leonardo" / "pio_build"


def _run_checker(argv=None, env_overrides=None):
    """Invoke check_release_assets.py as a real subprocess (list argv, never
    shell=True).

    `env_overrides`, when given, is merged into the child's environment on
    top of the current process environment -- used by the seam-precedence
    tests to set FIRESTARTER_PIO_BUILD_ROOT / FIRESTARTER_SIZE_BASELINE
    without mutating this process's own environment.
    """
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, str(_CHECKER), *(argv or [])],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def test_clean_control_all_three_envs_pass():
    """Coverage 1 -- the clean control tree exits 0, stdout starts with
    PASS: and names all three envs."""
    result = _run_checker(["--build-root", str(_CLEAN_BUILD_ROOT)])
    assert result.returncode == 0, (
        f"expected exit 0 on the clean control tree.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert result.stdout.startswith("PASS:"), (
        f"expected stdout to start with 'PASS:'. Got:\n{result.stdout}"
    )
    for env_name in ("uno", "uno328pb", "leonardo"):
        assert env_name in result.stdout, (
            f"expected {env_name!r} named in the PASS: line. Got:\n{result.stdout}"
        )


def test_planted_missing_uno328pb_flips_checker_to_failure():
    """Coverage 2 -- the planted missing-hex tree (uno328pb absent) exits 1,
    stdout contains FAIL: and names uno328pb and the expected path; stdout
    never contains PASS:."""
    result = _run_checker(["--build-root", str(_MISSING_BUILD_ROOT)])
    assert result.returncode != 0, (
        f"expected non-zero exit on the planted missing-uno328pb tree.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert result.returncode == 1, (
        f"expected the literal exit code 1 (missing asset), got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, f"expected FAIL: in output. Got:\n{result.stdout}"
    assert "uno328pb" in result.stdout, (
        f"expected 'uno328pb' named in the FAIL output. Got:\n{result.stdout}"
    )
    assert "firestarter_uno328pb.hex" in result.stdout, (
        f"expected the expected path named in the FAIL output. Got:\n{result.stdout}"
    )
    assert "PASS:" not in result.stdout, (
        f"a failing run must never print PASS:. Got:\n{result.stdout}"
    )


def test_planted_zero_byte_leonardo_flips_checker_to_failure():
    """Coverage 3 -- the planted zero-byte tree (leonardo truncated to 0
    bytes) exits 1, stdout contains FAIL: and names leonardo and the
    observed size 0."""
    result = _run_checker(["--build-root", str(_ZERO_BYTE_BUILD_ROOT)])
    assert result.returncode == 1, (
        f"expected the literal exit code 1 (zero-byte asset), got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, f"expected FAIL: in output. Got:\n{result.stdout}"
    assert "leonardo" in result.stdout, (
        f"expected 'leonardo' named in the FAIL output. Got:\n{result.stdout}"
    )
    assert "0 bytes" in result.stdout, (
        f"expected the observed size '0 bytes' named in the FAIL output. Got:\n{result.stdout}"
    )
    assert "PASS:" not in result.stdout, (
        f"a failing run must never print PASS:. Got:\n{result.stdout}"
    )


def test_empty_avr_targets_never_vacuous(tmp_path):
    """Coverage 4 -- a baseline whose avr_targets parses as an empty object
    must exit 1 (the never-vacuous guard) and never print PASS:. A gate that
    requires nothing must not report success."""
    empty_baseline = tmp_path / "empty_avr_targets.json"
    empty_baseline.write_text(json.dumps({"avr_targets": {}}))

    result = _run_checker(
        ["--baseline", str(empty_baseline), "--build-root", str(_CLEAN_BUILD_ROOT)]
    )
    assert result.returncode == 1, (
        f"expected the literal exit code 1 (never-vacuous guard), got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout, (
        f"a vacuous run must never print PASS:. Got:\n{result.stdout}"
    )


def test_malformed_baseline_forms_exit_exactly_2(tmp_path):
    """Coverage 5 -- a baseline that is not valid JSON, has no avr_targets
    key, or whose avr_targets is not an object, must each exit exactly 2 --
    a tool/format failure, categorically distinct from a missing asset."""
    not_json = tmp_path / "not_json.json"
    not_json.write_text("{not valid json")
    result = _run_checker(["--baseline", str(not_json), "--build-root", str(_CLEAN_BUILD_ROOT)])
    assert result.returncode == 2, (
        f"invalid JSON: expected the literal exit code 2, got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout

    no_key = tmp_path / "no_avr_targets_key.json"
    no_key.write_text(json.dumps({"native_envs": {}}))
    result = _run_checker(["--baseline", str(no_key), "--build-root", str(_CLEAN_BUILD_ROOT)])
    assert result.returncode == 2, (
        f"missing avr_targets key: expected the literal exit code 2, got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout

    not_object = tmp_path / "avr_targets_not_object.json"
    not_object.write_text(json.dumps({"avr_targets": ["uno", "uno328pb", "leonardo"]}))
    result = _run_checker(
        ["--baseline", str(not_object), "--build-root", str(_CLEAN_BUILD_ROOT)]
    )
    assert result.returncode == 2, (
        f"avr_targets not an object: expected the literal exit code 2, got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout


def test_malformed_argv_exits_2():
    """Coverage 6 -- an unknown argv flag, or a flag missing its required
    value, must each exit 2."""
    result = _run_checker(["--nonexistent-flag"])
    assert result.returncode == 2, (
        f"unknown flag: expected the literal exit code 2, got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    result = _run_checker(["--build-root"])
    assert result.returncode == 2, (
        f"flag missing its value: expected the literal exit code 2, got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_pio_build_root_seam_precedence_flips_clean_invocation_to_fail():
    """Coverage 7 -- pointing FIRESTARTER_PIO_BUILD_ROOT at the planted
    missing-hex tree (with no --build-root argv given) must flip an
    otherwise-clean invocation to exit 1 -- proving the checker genuinely
    reads the seam rather than embedding a hardcoded build root."""
    result = _run_checker(
        [],
        env_overrides={"FIRESTARTER_PIO_BUILD_ROOT": str(_MISSING_BUILD_ROOT)},
    )
    assert result.returncode != 0, (
        f"expected the FIRESTARTER_PIO_BUILD_ROOT seam to be read and flip the run "
        f"to failure.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "uno328pb" in result.stdout, f"expected 'uno328pb' named. Got:\n{result.stdout}"


def test_size_baseline_seam_precedence_flips_clean_tree_to_fail(tmp_path):
    """Coverage 8 -- pointing FIRESTARTER_SIZE_BASELINE at a tampered copy of
    the real baseline carrying a fourth avr_targets key (mega2560) must flip
    the clean tree to exit 1, naming that fourth env -- proving the checker
    genuinely reads this seam too rather than embedding the real keys."""
    real_baseline = json.loads(_BASELINE.read_text())
    real_baseline["avr_targets"]["mega2560"] = dict(real_baseline["avr_targets"]["uno"])
    tampered = tmp_path / "tampered_size_baseline.json"
    tampered.write_text(json.dumps(real_baseline))

    result = _run_checker(
        ["--build-root", str(_CLEAN_BUILD_ROOT)],
        env_overrides={"FIRESTARTER_SIZE_BASELINE": str(tampered)},
    )
    assert result.returncode != 0, (
        f"expected the FIRESTARTER_SIZE_BASELINE seam to be read and flip the clean "
        f"tree to failure once a fourth avr_targets key is present.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "mega2560" in result.stdout, f"expected 'mega2560' named. Got:\n{result.stdout}"


def test_clean_tree_tolerates_absent_py32_image():
    """Coverage 9 -- the clean control tree contains no py32 image anywhere,
    and the checker still exits 0 and never mentions "py32" in its output.
    This is REL-03's whole tolerance: the AVR-assets-present gate must never
    require, or even reference, the py32f071 image."""
    result = _run_checker(["--build-root", str(_CLEAN_BUILD_ROOT)])
    assert result.returncode == 0, (
        f"expected exit 0 with no py32 image present.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "py32" not in result.stdout.lower(), (
        f"the checker must never mention py32 anywhere in its output. Got:\n{result.stdout}"
    )


def test_beta_build_yml_never_sets_fail_on_unmatched_files_key():
    """Coverage 10 -- beta-build.yml, with comment lines stripped, must
    contain no line setting the release action's unmatched-files failure
    input as a YAML key. This is REL-02's real invariant (research finding
    F-1): softprops/action-gh-release treats a literal path exactly like a
    glob and only fails on an unmatched pattern when fail_on_unmatched_files
    is set true, which defaults to false. The comment-stripping is required,
    not cosmetic: Plan 128-07 adds a comment on the Release step that names
    this input BY NAME in order to explain why it is deliberately unset, and
    a naive whole-file grep would make that very explanation
    self-invalidating. Non-vacuity is asserted first, so a file that failed
    to load or was wholesale rewritten fails this test rather than passing it
    vacuously on an empty line list.
    """
    text = _BETA_BUILD.read_text()
    surviving_lines = [
        line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")
    ]

    assert surviving_lines, f"expected {_BETA_BUILD} to contain non-comment lines"
    assert any("softprops/action-gh-release@v2" in line for line in surviving_lines), (
        f"expected {_BETA_BUILD} to still reference softprops/action-gh-release@v2 -- "
        f"a file that failed to load or was rewritten must fail this test, not pass it "
        f"vacuously"
    )

    unmatched_files_key_re = re.compile(r"fail_on_unmatched_files\s*:")
    violations = [line for line in surviving_lines if unmatched_files_key_re.search(line)]
    assert not violations, (
        f"expected no surviving (non-comment) line in {_BETA_BUILD} to set "
        f"fail_on_unmatched_files as a YAML key. Found:\n" + "\n".join(violations)
    )
