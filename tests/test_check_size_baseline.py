"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 123 Plan 02 — the BASE-08 anti-hollow pairing for scripts/check_size_baseline.py.

Requirements: BASE-01, BASE-08
Decisions covered: D-01, D-02, D-03, D-04, D-13

This is the MANDATORY anti-hollow pairing for the BASE-01 comparator: a checker with
no negative-fixture test is exactly this project's v1.12 hollow-GATE-03 failure mode --
a gate that could never fail because nothing concrete was asserted against it. Every
planted-violation test below invokes scripts/check_size_baseline.py as a real subprocess
(list-form argv, never shell=True, never an in-process import) against a committed
fixture under tests/fixtures/, so a passing suite here proves the checker itself -- not
this test module -- fails the build on a real violation.

No `pio` invocation happens anywhere in this module: every log parsed is a committed
fixture (captured_* for the clean-control arms, planted_size_baseline_* for one
deliberate violation per exit-taxonomy arm). Paying a cold-toolchain `pio` cost inside
pytest would make this suite non-hermetic and slow.

Coverage:
  1. Clean AVR control — each of the three captured_build_*.log files exits 0 and its
     PASS: line names the env.
  2. Clean native control — both captured_test_native*.log files exit 0 with 141 and 17
     in the PASS: line.
  3. Planted flash regression exits non-zero, prints FAIL:, and the output names both
     the baseline figure (26072) and the observed figure (26584).
  4. Planted unparseable log exits exactly 2 (the literal return code, not just
     non-zero) and does NOT print PASS:.
  5. Planted errored-suites log exits non-zero naming ERRORED — proving the gate
     asserts per-suite statuses, not merely the suite count (A-4's failure mode).
  6. Never-vacuous: invoking the checker with no logs and no --rebuild exits non-zero,
     prints the never-vacuous message, and prints no PASS:.
  7. Baseline-seam precedence: pointing FIRESTARTER_SIZE_BASELINE at a temp JSON whose
     Leonardo flash figure differs makes the previously-clean captured_build_leonardo.log
     FAIL — proving the checker genuinely reads the seam rather than embedding numbers.
  8. --policy merge05 permits the RESEARCH-measured post-landing deltas (Leonardo -56,
     Uno +22, uno328pb +28, RAM unchanged) against the frozen BASE-01 record — the
     pre-landing proof that the band mode will pass once the real landing happens.
  9. --policy merge05 fires on a planted +65 B Uno-class flash growth (one byte outside
     the 64 B band), naming both the computed delta and the band.
  10. --policy merge05 fires on a planted +1 B Leonardo flash growth (Leonardo must not
      grow at all), naming the env and the computed delta.
  11. --policy merge05 fires on a planted +1 B RAM move (RAM equality holds under the
      band mode too), naming ram_used.
  12. The default (no --policy) mode is unchanged by the new flag: all three captured
      logs still exit 0 and the output never contains the band-mode `<=64` substring.

Derivation of each planted fixture from its named captured_ source (single stated edit,
diffable against the source so a reviewer can see exactly what was planted):

  planted_size_baseline_flash_regression.log
    = captured_build_leonardo.log with the Flash: line's `used` figure raised from
      26072 to 26584 (+512 B). The percentage/bar-graph columns are left exactly as
      captured (now inconsistent with the new `used` figure) -- a free proof that the
      parser anchors on the `(used N bytes from M bytes)` tail and never reads the bar.

  planted_size_baseline_unparseable.log
    = captured_build_uno.log with BOTH the `RAM:` and `Flash:` report lines deleted
      (lines 85-86 of the source) and everything else intact.

  planted_size_baseline_suites_errored.log
    = captured_test_native_summary.log with every per-suite status word changed from
      PASSED to ERRORED (all 17 rows, `s/PASSED/ERRORED/g`) and the
      `141 test cases: 141 succeeded` line's succeeded count changed to 0, leaving the
      total (141) and all 17 rows present -- A-4's exact failure mode: the suite count
      still reads 17, so a gate asserting only the count would incorrectly pass.

  planted_size_baseline_policy_uno_over_band.log
    = captured_build_uno.log with the Flash: line's `used` figure raised from 23932 to
      23997 (+65 B — one byte outside MERGE-05's 64 B uno-class band). Everything else,
      including the now-stale percentage/bar columns, is left exactly as captured.

  planted_size_baseline_policy_leonardo_growth.log
    = captured_build_leonardo.log with the Flash: line's `used` figure raised from
      26072 to 26073 (+1 B — Leonardo must not grow at all under MERGE-05).

  planted_size_baseline_policy_ram_moved.log
    = captured_build_uno.log with the RAM: line's `used` figure raised from 1573 to
      1574 (+1 B — RAM equality is enforced under the band mode too, on all three envs).

Self-contained path resolution below — NOT in conftest.py (firestarter/tests/ has no
conftest.py anywhere in the repo; this is a recorded house-rule pattern decision, per
test_update_version.py's own comment, not an omission). Stdlib and pytest only.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_CHECKER = _REPO_ROOT / "scripts" / "check_size_baseline.py"
_FIXTURES = _HERE / "fixtures"
_BASELINE = _REPO_ROOT / "scripts" / "baseline" / "size_baseline.json"
_BASE01_BASELINE = _REPO_ROOT / "scripts" / "baseline" / "size_baseline_base01.json"


def _run_checker(argv=None, env_overrides=None):
    """Invoke check_size_baseline.py as a real subprocess (list argv, never shell=True).

    `env_overrides`, when given, is merged into the child's environment on top of
    the current process environment -- used by the baseline-seam-precedence test to
    set FIRESTARTER_SIZE_BASELINE without mutating this process's own environment.
    """
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, str(_CHECKER), *(argv or [])],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def test_clean_avr_all_three_envs_pass():
    """Coverage 1 — each captured_build_*.log exits 0 and its PASS: line names the env."""
    for env_name, fixture in (
        ("uno", "captured_build_uno.log"),
        ("uno328pb", "captured_build_uno328pb.log"),
        ("leonardo", "captured_build_leonardo.log"),
    ):
        result = _run_checker(["--avr-log", f"{env_name}={_FIXTURES / fixture}"])
        assert result.returncode == 0, (
            f"{env_name}: expected exit 0 on a clean captured log.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "PASS:" in result.stdout, (
            f"{env_name}: expected PASS: in stdout. Got:\n{result.stdout}"
        )
        assert env_name in result.stdout, (
            f"{env_name}: expected the env name in the PASS: line. Got:\n{result.stdout}"
        )


def test_clean_native_both_envs_pass():
    """Coverage 2 — both captured_test_native*.log files exit 0 with 141 and 17 in PASS:."""
    for env_name, fixture in (
        ("native", "captured_test_native_summary.log"),
        ("native_nodevtools", "captured_test_native_nodevtools_summary.log"),
    ):
        result = _run_checker(["--native-log", f"{env_name}={_FIXTURES / fixture}"])
        assert result.returncode == 0, (
            f"{env_name}: expected exit 0 on a clean captured native log.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "PASS:" in result.stdout
        assert "141" in result.stdout, f"Expected '141' in output. Got:\n{result.stdout}"
        assert "17" in result.stdout, f"Expected '17' in output. Got:\n{result.stdout}"


def test_planted_flash_regression_flips_checker_to_failure():
    """Coverage 3 — the planted +512 B Leonardo flash figure exits non-zero and names
    both the baseline (26072) and observed (26584) figures -- the message must name
    both numbers, not merely fail."""
    result = _run_checker(
        ["--avr-log", f"leonardo={_FIXTURES / 'planted_size_baseline_flash_regression.log'}"]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit on a planted flash regression.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, f"Expected FAIL: in output. Got:\n{result.stdout}"
    assert "26072" in result.stdout, f"Expected baseline figure 26072. Got:\n{result.stdout}"
    assert "26584" in result.stdout, f"Expected observed figure 26584. Got:\n{result.stdout}"


def test_planted_unparseable_log_exits_exactly_2():
    """Coverage 4 — a build log missing both RAM:/Flash: report lines is a parse
    failure, categorically distinct from a size regression: exit code must be the
    literal 2, not merely non-zero, and PASS: must never appear."""
    result = _run_checker(
        ["--avr-log", f"uno={_FIXTURES / 'planted_size_baseline_unparseable.log'}"]
    )
    assert result.returncode == 2, (
        f"expected the literal exit code 2 (parse failure), got {result.returncode}.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    combined = result.stdout + result.stderr
    assert "RAM" in combined or "Flash" in combined, (
        f"Expected the missing RAM:/Flash: report named in the error output. "
        f"Got:\n{combined}"
    )
    assert "PASS:" not in result.stdout, (
        f"A parse failure must never print PASS:. Got:\n{result.stdout}"
    )


def test_planted_suites_errored_flips_checker_to_failure():
    """Coverage 5 — A-4's exact failure mode: 17 suites present but all ERRORED must
    exit non-zero, naming the ERRORED status -- proving the gate asserts statuses,
    not only the suite count."""
    result = _run_checker(
        ["--native-log", f"native={_FIXTURES / 'planted_size_baseline_suites_errored.log'}"]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit when all 17 suites report ERRORED.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "ERRORED" in result.stdout, (
        f"Expected the failing ERRORED status named in output. Got:\n{result.stdout}"
    )


def test_never_vacuous_with_no_logs_and_no_rebuild():
    """Coverage 6 — invoking the checker with no logs and no --rebuild must exit
    non-zero, print the never-vacuous message, and print no PASS: -- a comparator
    that compares nothing must not report success."""
    result = _run_checker([])
    assert result.returncode != 0, (
        f"expected non-zero exit with zero envs supplied.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout, (
        f"A vacuous run must never print PASS:. Got:\n{result.stdout}"
    )
    assert "no" in result.stdout.lower() and "compared" in result.stdout.lower(), (
        f"Expected the never-vacuous message naming 'no ... compared'. Got:\n{result.stdout}"
    )


def test_baseline_seam_precedence_flips_clean_log_to_fail(tmp_path):
    """Coverage 7 — pointing FIRESTARTER_SIZE_BASELINE at a temp JSON whose Leonardo
    flash figure differs must make the previously-clean captured_build_leonardo.log
    FAIL. Proves the checker genuinely reads its baseline through the env seam rather
    than embedding the recorded numbers in the script itself."""
    real_baseline = json.loads(_BASELINE.read_text())
    real_baseline["avr_targets"]["leonardo"]["flash_used"] = 1
    tampered = tmp_path / "tampered_size_baseline.json"
    tampered.write_text(json.dumps(real_baseline))

    result = _run_checker(
        ["--avr-log", f"leonardo={_FIXTURES / 'captured_build_leonardo.log'}"],
        env_overrides={"FIRESTARTER_SIZE_BASELINE": str(tampered)},
    )
    assert result.returncode != 0, (
        f"expected the checker to read the tampered baseline via the env seam and "
        f"FAIL, proving it does not embed the real numbers.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, f"Expected FAIL: in output. Got:\n{result.stdout}"


def _rewrite_flash_used(text, old_used, new_used, total):
    """Rewrite a captured log's `Flash: ... (used OLD bytes from TOTAL bytes)` tail
    to NEW, leaving the percentage/bar-graph columns exactly as captured (the parser
    anchors on the `(used N bytes from M bytes)` tail and never reads the bar)."""
    pattern = re.compile(
        rf"\(used {old_used} bytes from {total} bytes\)"
    )
    new_text, count = pattern.subn(f"(used {new_used} bytes from {total} bytes)", text)
    assert count == 1, (
        f"expected exactly one Flash 'used {old_used} bytes from {total} bytes' "
        f"occurrence to rewrite, found {count}"
    )
    return new_text


def test_policy_merge05_permits_the_measured_landing_deltas(tmp_path):
    """Coverage 8 — the pre-landing proof that --policy merge05 will PASS on the exact
    post-landing figures RESEARCH measured on the merged tree (Leonardo -56, Uno +22,
    uno328pb +28, RAM unchanged in all three), read against the frozen BASE-01 record
    (scripts/baseline/size_baseline_base01.json), never the live default baseline."""
    synthesized = {
        "leonardo": ("captured_build_leonardo.log", 26072, 26016, 28672),
        "uno": ("captured_build_uno.log", 23932, 23954, 32256),
        "uno328pb": ("captured_build_uno328pb.log", 23976, 24004, 32384),
    }
    argv = ["--policy", "merge05", "--baseline", str(_BASE01_BASELINE)]
    for env, (fixture, old_used, new_used, total) in synthesized.items():
        text = (_FIXTURES / fixture).read_text()
        rewritten = _rewrite_flash_used(text, old_used, new_used, total)
        dest = tmp_path / f"post_landing_{env}.log"
        dest.write_text(rewritten)
        argv += ["--avr-log", f"{env}={dest}"]

    result = _run_checker(argv)
    assert result.returncode == 0, (
        f"expected --policy merge05 to permit the measured post-landing deltas "
        f"against the frozen BASE-01 record.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, f"Expected PASS: in stdout. Got:\n{result.stdout}"


def test_policy_merge05_fires_on_uno_class_over_band():
    """Coverage 9 — the planted +65 B Uno-class flash growth (one byte outside the
    64 B band) must fail --policy merge05, naming both the computed delta and the
    band it exceeds."""
    result = _run_checker(
        [
            "--policy",
            "merge05",
            "--baseline",
            str(_BASE01_BASELINE),
            "--avr-log",
            f"uno={_FIXTURES / 'planted_size_baseline_policy_uno_over_band.log'}",
        ]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit on a planted +65 B uno-class flash growth.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "delta=+65" in result.stdout, f"Expected 'delta=+65'. Got:\n{result.stdout}"
    assert "band of 64" in result.stdout, f"Expected 'band of 64'. Got:\n{result.stdout}"


def test_policy_merge05_fires_on_leonardo_growth():
    """Coverage 10 — the planted +1 B Leonardo flash growth must fail --policy
    merge05 (Leonardo must not grow at all), naming the env and the delta."""
    result = _run_checker(
        [
            "--policy",
            "merge05",
            "--baseline",
            str(_BASE01_BASELINE),
            "--avr-log",
            f"leonardo={_FIXTURES / 'planted_size_baseline_policy_leonardo_growth.log'}",
        ]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit on a planted +1 B Leonardo flash growth.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "leonardo" in result.stdout, f"Expected 'leonardo'. Got:\n{result.stdout}"
    assert "delta=+1" in result.stdout, f"Expected 'delta=+1'. Got:\n{result.stdout}"


def test_policy_merge05_fires_on_ram_move():
    """Coverage 11 — the planted +1 B RAM move must fail --policy merge05 (RAM
    equality holds under the band mode too), naming ram_used."""
    result = _run_checker(
        [
            "--policy",
            "merge05",
            "--baseline",
            str(_BASE01_BASELINE),
            "--avr-log",
            f"uno={_FIXTURES / 'planted_size_baseline_policy_ram_moved.log'}",
        ]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit on a planted +1 B RAM move.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "ram_used" in result.stdout, f"Expected 'ram_used'. Got:\n{result.stdout}"


def test_default_mode_is_unchanged_by_the_new_flag():
    """Coverage 12 — T-124-08: the default (no --policy) mode must be textually
    unchanged by the new flag's addition. All three captured logs still exit 0 and
    the output never contains the band-mode `<=64` substring."""
    for env_name, fixture in (
        ("uno", "captured_build_uno.log"),
        ("uno328pb", "captured_build_uno328pb.log"),
        ("leonardo", "captured_build_leonardo.log"),
    ):
        result = _run_checker(["--avr-log", f"{env_name}={_FIXTURES / fixture}"])
        assert result.returncode == 0, (
            f"{env_name}: expected exit 0 on a clean captured log in default mode.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert "<=64" not in result.stdout, (
            f"{env_name}: default mode must never emit the band-mode '<=64' "
            f"substring. Got:\n{result.stdout}"
        )
