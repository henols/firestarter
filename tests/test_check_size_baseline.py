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
     the baseline figure (27002, the post-route-assert-fix figure the debug session
     w27c512-program-fail-byte0 re-anchored the live default to) and the observed
     figure (27514).
  4. Planted unparseable log exits exactly 2 (the literal return code, not just
     non-zero) and does NOT print PASS:.
  5. Planted errored-suites log exits non-zero naming ERRORED — proving the gate
     asserts per-suite statuses, not merely the suite count (A-4's failure mode).
  6. Never-vacuous: invoking the checker with no logs and no --rebuild exits non-zero,
     prints the never-vacuous message, and prints no PASS:.
  7. Baseline-seam precedence: pointing FIRESTARTER_SIZE_BASELINE at a temp JSON whose
     Leonardo flash figure differs makes the previously-clean captured_build_leonardo.log
     FAIL — proving the checker genuinely reads the seam rather than embedding numbers.
  8. --policy merge05 permits the re-anchored figures (EXACT ZERO delta on all three
     targets, read from the frozen merge05_base01_anchor_*.log trio) against
     BASE-01 — Phase 144 Plan 05 (D-11) re-anchored BASE-01 in place to the same v1.31
     tip, so a PASS here means the anchor moved, not that growth stayed inside v1.24's
     original band (D-14).
  8b. --policy merge05 ADMITS the current tree's +96 B against BASE-01 under the named
      defect-fix exemption (MERGE05_DEFECT_FIX_EXEMPTION_BYTES) with the +96 still
      visible in the PASS text, AND still FAILS one byte past it (planted +97 B on
      leonardo) — the adjudication and its negative control in one leg. Replaces
      test_policy_merge05_fires_on_the_current_tree, which asserted the un-adjudicated
      breach and which the adjudication was designed to turn RED.
  9. --policy merge05 fires on a planted +161 B Uno-class flash growth (one byte outside
     the EFFECTIVE 160 B allowance = unchanged 64 B band + 96 B exemption), naming the
     computed delta, the allowance, and the allowance's decomposition.
  10. --policy merge05 fires on a planted +97 B Leonardo flash growth (leonardo's base
      band stays 0 B, so its effective allowance is exactly the 96 B exemption),
      naming the env and the computed delta.
  11. --policy merge05 fires on a planted +1 B RAM move (RAM equality holds under the
      band mode too), naming ram_used.
  12. The default (no --policy) mode is unchanged by the new flag: all three captured
      logs still exit 0 and the output never contains the band-mode `<=64` substring.

Derivation of each planted fixture from its named captured_ source (single stated edit,
diffable against the source so a reviewer can see exactly what was planted):

  planted_size_baseline_flash_regression.log
    = captured_build_leonardo.log with the Flash: line's `used` figure raised from
      27002 to 27514 (+512 B, the same offset every prior version of this fixture has
      used since Phase 123, now applied to the v1.31-tip figure Phase 144 Plan 05
      re-captured -- see below). The percentage/bar-graph columns are left exactly as
      captured (now inconsistent with the new `used` figure) -- a free proof that the
      parser anchors on the `(used N bytes from M bytes)` tail and never reads the bar.

  Phase 124 Plan 10 (W-1 half (b)) re-captured captured_build_{uno,uno328pb,leonardo}.log
  and captured_test_native{,_nodevtools}_summary.log from the post-landing tree (all five
  code-bearing plans 124-01..09 applied): uno 23954/1573, uno328pb 24004/1579, leonardo
  26016/2014, both native envs still 141 cases/17 suites. planted_size_baseline_flash_
  regression.log above was re-derived from the new leonardo capture in the same commit,
  keeping the same +512 B offset. The three `policy_*` planted fixtures below were NOT
  re-derived -- they are asserted exclusively against the FROZEN
  scripts/baseline/size_baseline_base01.json (pre-landing figures), which Plan 124-10
  never modifies, so their pre-landing numbers (23932/23997, 26072/26073) remain correct
  and unchanged. The pre-landing `captured_*` fixtures this plan superseded are preserved
  in git history; their numbers are also preserved permanently in
  scripts/baseline/size_baseline_base01.json.

  Phase 144 Plan 05 (D-10, D-11, D-13) re-captured captured_build_{uno,uno328pb,leonardo}
  .log AGAIN, from the v1.31 tip (uno 24824/1573, uno328pb 24874/1579, leonardo
  26906/2014, both native envs still 141 cases/17 suites) -- three more phases (140-143)
  had landed src/ changes since Phase 124. Unlike Phase 124 Plan 10, this time the three
  `policy_*` planted fixtures below WERE re-derived, because D-11 re-anchored
  scripts/baseline/size_baseline_base01.json itself to the same v1.31 tip -- it no longer
  holds the v1.24 figures (23932/23976/26072) the paragraph above describes. Each was
  re-derived preserving its single cause and its asserted delta (+65 B / +1 B / +1 B),
  never its absolute figure, per D-18: a re-derived plant is a NEW plant and needs its
  own proof that it still fires. The pre-re-anchor `policy_*` fixtures and BASE-01's
  v1.24 content are preserved in git history, never kept in-tree (D-12).

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
    = captured_build_uno.log AS IT READ AT BASE-01'S ANCHOR with the Flash: line's
      `used` figure raised from 24824 to 25195 (+371 B — one byte outside the
      EFFECTIVE uno-class allowance of 370 B: the unchanged 64 B band plus the 96 B
      defect-fix exemption plus the 210 B Phase 149 page-size-seam exemption). This
      and the two other policy-mode planted logs are compared against BASE-01, which
      no adjudication to date has moved, so they stay at the anchor figures while the
      captured_build_*.log trio sits +96 B ahead with the tree as it read before Phase
      149. Everything else, including the now-stale percentage/bar columns, is left
      exactly as captured.
      Re-derived THREE times now, each time preserving the single cause and the
      one-byte-past-the-ceiling role, never the absolute figure (D-18): by Phase 144
      Plan 05 from 23932/23997 when the anchor moved, by the v1.31 Phase 145
      adjudication from 24889 (+65 B) when the enforced ceiling moved from 64 B to
      160 B, and by Phase 149 (D-12) from 24985 (+161 B) when the ceiling moved again
      from 160 B to 370 B on landing the page-size-seam exemption. Without this third
      re-derivation this plant would sit INSIDE the new allowance and its leg would
      have gone falsely green while still claiming to prove a firing.

  planted_size_baseline_policy_leonardo_growth.log
    = captured_build_leonardo.log with the Flash: line's `used` figure raised from
      26906 to 27213 (+307 B — leonardo's base band stays 0 B must-not-grow, so its
      effective allowance is exactly the 96 B defect-fix exemption plus the 210 B
      Phase 149 page-size-seam exemption, and this is one byte past it). Left at the
      BASE-01 anchor for the reason given under the uno-class entry above. Re-derived
      by Phase 144 Plan 05 from 26072/26073, by the v1.31 Phase 145 adjudication from
      26907 (+1 B), and now by Phase 149 (D-12) from 27003 (+97 B) — same D-18
      reasoning as the uno-class entry: a +97 B plant now sits inside the new
      allowance. This single fixture backs two legs (Coverage 10 and the
      negative-control arm of test_policy_merge05_admits_the_documented_defect_fix),
      deliberately shared rather than committed twice byte-identically.

  planted_size_baseline_policy_ram_moved.log
    = captured_build_uno.log with the RAM: line's `used` figure raised from 1573 to
      1576 (+3 B — one byte past the Phase 149 page-size-seam RAM exemption of 2 B;
      before Phase 149, RAM equality was enforced exactly under the band mode too, on
      all three envs, with zero tolerance). Re-derived by Phase 144 Plan 05 from the
      same 1573/1574 pair (D-18) when only the source capture's Flash: line moved
      underneath it, and now by Phase 149 (D-12) from 1574 (+1 B) to 1576 (+3 B) --
      the RAM clause gained its own named exemption for the first time (the single
      `uint16_t page_size` handle field, measured +2 B on all three targets), so a
      +1 B plant now sits inside the new tolerance and would have gone falsely green.

Self-contained path resolution below — NOT in conftest.py (firestarter/tests/ has no
conftest.py anywhere in the repo; this is a recorded house-rule pattern decision, per
test_update_version.py's own comment, not an omission). Stdlib and pytest only.
"""

import json
import os
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
    both the baseline (27002, the figure the w27c512-program-fail-byte0 debug session
    re-anchored the live default to) and observed (27514) figures -- the message must name both
    numbers, not merely fail."""
    result = _run_checker(
        ["--avr-log", f"leonardo={_FIXTURES / 'planted_size_baseline_flash_regression.log'}"]
    )
    assert result.returncode != 0, (
        f"expected non-zero exit on a planted flash regression.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, f"Expected FAIL: in output. Got:\n{result.stdout}"
    assert "27002" in result.stdout, f"Expected baseline figure 27002. Got:\n{result.stdout}"
    assert "27514" in result.stdout, f"Expected observed figure 27514. Got:\n{result.stdout}"


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


def test_policy_merge05_permits_the_measured_landing_deltas():
    """Coverage 8 — --policy merge05 PASSES on the re-anchored figures, read against
    BASE-01 (scripts/baseline/size_baseline_base01.json), never the live default
    baseline.

    Before Phase 124 Plan 10, this test synthesized RESEARCH's *predicted* post-landing
    deltas (Leonardo -56, Uno +22, uno328pb +28, RAM unchanged) onto tmp_path copies of
    the then-still-pre-landing captured_build_*.log fixtures, because the real landing
    had not happened yet. Plan 124-10 re-captured captured_build_{uno,uno328pb,leonardo}
    .log directly from the real, now-landed tree (uno 23954/1573, uno328pb 24004/1579,
    leonardo 26016/2014) -- so this test fed those committed fixtures straight to
    the checker with no synthesis step, and the assertion was no longer a *prediction*
    but a direct measurement of the real MERGE-05 outcome.

    Phase 144 Plan 05 (D-10, D-11, D-14): the fixtures were re-captured again, from the
    real, now-landed v1.31 tree (uno 24824/1573, uno328pb 24874/1579, leonardo
    26906/2014) — and BASE-01 itself was re-anchored in place to those identical
    figures. This leg therefore now asserts EXACT IDENTITY at ZERO delta on all three
    targets, not growth staying inside a band. It reads PASS because the anchor moved
    to v1.31, not because growth stayed inside v1.24's original band.

    Debug session w27c512-program-fail-byte0 (Phase 145 Gate 2 root-cause fix)
    SEVERED this leg from captured_build_*.log and gave it its own frozen inputs,
    merge05_base01_anchor_*.log, which hold BASE-01's own anchor figures verbatim
    (uno 24824, uno328pb 24874, leonardo 26906). Reason, stated plainly: that fix
    added 96 B of flash to all three targets, and the captured_build_*.log fixtures
    have to track the LIVE tree because five other legs feed them to the default
    byte-identity mode. Continuing to feed them here would have quietly converted
    this leg from "the comparator passes at zero delta" into a false claim that the
    current tree is inside MERGE-05's original band -- it is NOT.

    v1.31 Phase 145 adjudicated that breach: the live tree's +96 B is now ADMITTED
    under a named, SHA-attributed exemption, and
    test_policy_merge05_admits_the_documented_defect_fix immediately below is the
    machine-checked record of the admission AND of the re-armed tripwire one byte
    past it (it replaced test_policy_merge05_fires_on_the_current_tree, which
    recorded the un-adjudicated breach). This leg's split from the live logs still
    earns its keep: frozen inputs mean neither a future re-anchor nor a future
    exemption change can move this leg's premise underneath it. So it keeps proving
    exactly the comparator property it was written for -- zero delta against the
    anchor passes -- and never doubles as a measurement of a tree that has moved.

    Phase 149 (D-12) added a second flash exemption
    (MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES, 210 B) and a RAM exemption
    (MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES, 2 B) alongside the existing
    defect-fix exemption -- this leg's own arithmetic did not need re-deriving:
    zero delta against the anchor sits inside ANY non-negative allowance, however
    many terms compose it, so the widened allowance changes nothing this leg
    asserts. Its frozen inputs (`merge05_base01_anchor_*.log`) are, correctly,
    untouched by this phase."""
    argv = ["--policy", "merge05", "--baseline", str(_BASE01_BASELINE)]
    for env, fixture in (
        ("leonardo", "merge05_base01_anchor_leonardo.log"),
        ("uno", "merge05_base01_anchor_uno.log"),
        ("uno328pb", "merge05_base01_anchor_uno328pb.log"),
    ):
        argv += ["--avr-log", f"{env}={_FIXTURES / fixture}"]

    result = _run_checker(argv)
    assert result.returncode == 0, (
        f"expected --policy merge05 to permit the measured post-landing deltas "
        f"against the frozen BASE-01 record.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, f"Expected PASS: in stdout. Got:\n{result.stdout}"


def test_policy_merge05_admits_the_documented_defect_fix():
    """Coverage 8b — the adjudication leg (v1.31 Phase 145), extended by Phase 149
    (PGSZ-04, D-12) to admit a SECOND named exemption without disturbing the first.
    Two arms, and the second one is the whole point of the first.

    History, so nobody re-litigates this by accident. Debug session
    w27c512-program-fail-byte0 added +96 B of flash to all three AVR targets
    (eprom_internal_program_pulse plus its two VPP settle constants, commits
    eb563d2 and ebe9cb3 — a defect fix restoring behaviour the pre-v1.31 firmware
    had, not new feature surface). MERGE-05's base bands are 0 B on leonardo and
    64 B uno-class, so the tripwire fired, exactly as designed. The predecessor of
    this leg, `test_policy_merge05_fires_on_the_current_tree`, asserted that breach
    so it could not rot into a JSON prose field, and said in as many words that the
    day someone adjudicated it this leg would go RED and force the decision to be
    written down. That day was v1.31 Phase 145: the +96 B was ADMITTED as a named,
    SHA-attributed exemption (MERGE05_DEFECT_FIX_EXEMPTION_BYTES in
    scripts/check_size_baseline.py, where the full rationale lives), NOT by
    re-anchoring BASE-01 a third time, NOT by widening either band literal, and NOT
    by shrinking the fix.

    Phase 149 repeats the shape one level up: the page-size wire seam
    (PGSZ-01/PGSZ-02) added a further +210 B of flash and +2 B of RAM on all three
    targets. Rather than folding that growth into the existing 96 B constant --
    which would launder Phase 149's cost into Phase 145's already-adjudicated
    number -- it is admitted as a SECOND, separately-named exemption,
    MERGE05_PAGE_SIZE_SEAM_EXEMPTION_BYTES (flash) plus
    MERGE05_PAGE_SIZE_SEAM_RAM_EXEMPTION_BYTES (RAM, the first time the RAM clause
    has admitted anything beyond exact equality). BASE-01's avr_targets are still
    byte-unchanged (uno 24824, uno328pb 24874, leonardo 26906) and so are both
    flash band literals -- captured here, not merely stated, by
    test_base01_is_not_re_anchored_by_the_new_exemption below.

    Arm 1 — the tree as captured before Phase 149 (captured_build_*.log, still at
    +96 B flash / +0 B RAM against BASE-01) PASSES, and BOTH admitted figures are
    still VISIBLE in the PASS text with their full decomposition -- the +96 B
    inherited from Phase 145 and the +210 B / seam-RAM-tolerance headroom Phase 149
    adds alongside it. A pass whose output hid either delta would be laundering,
    not adjudication, so the visibility is asserted, not assumed.

    Arm 2 — the NEGATIVE CONTROL, and the reason arm 1 is not a blank cheque: one
    byte beyond the NEW effective allowance (a planted +307 B on leonardo, whose
    effective allowance is now 0 + 96 + 210 = 306) still exits 1. Without this arm
    the exemption would be untested and could silently widen to admit anything. The
    tripwire is re-armed at the new floor, not removed. It shares its fixture with
    test_policy_merge05_fires_on_leonardo_growth (Coverage 10) rather than
    committing a second byte-identical plant; the two legs assert different
    properties of the same firing — that one names the env and the delta, this one
    names the effective allowance and pairs the failure with arm 1's pass."""
    # Arm 1: the pre-Phase-149 tree is admitted, at exactly +96 flash / +0 RAM on
    # every target -- both comfortably inside the NEW allowance too.
    argv = ["--policy", "merge05", "--baseline", str(_BASE01_BASELINE)]
    for env, fixture in (
        ("leonardo", "captured_build_leonardo.log"),
        ("uno", "captured_build_uno.log"),
        ("uno328pb", "captured_build_uno328pb.log"),
    ):
        argv += ["--avr-log", f"{env}={_FIXTURES / fixture}"]

    result = _run_checker(argv)
    assert result.returncode == 0, (
        "expected --policy merge05 to PASS (exit 0) against the pre-Phase-149 tree "
        "under the adjudicated defect-fix exemption, still comfortably inside the "
        "new page-size-seam allowance.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, f"Expected PASS: in stdout. Got:\n{result.stdout}"
    assert result.stdout.count("+96<=") == 3, (
        "expected all three targets to report their flash delta as exactly +96 B "
        "IN THE PASS TEXT -- an exemption that makes the admitted growth invisible "
        "in the report is laundering. If this number moved, the fix's flash cost "
        "moved with it and MERGE05_DEFECT_FIX_EXEMPTION_BYTES, this leg and "
        "scripts/baseline/size_baseline.json's merge05_clause all need re-deriving.\n"
        f"Got:\n{result.stdout}"
    )
    assert (
        "band0+exempt96+seam210" in result.stdout
        and "band64+exempt96+seam210" in result.stdout
    ), (
        "expected the PASS text to show the flash allowance DECOMPOSED into THREE "
        "terms -- the unchanged band literal, the Phase 145 defect-fix exemption "
        "and the Phase 149 page-size-seam exemption -- on both the leonardo (0 B) "
        f"and the uno-class (64 B) targets. Got:\n{result.stdout}"
    )
    assert "ram=1573/2048[+0<=2=seam2]" in result.stdout, (
        "expected uno's RAM figure to show the new RAM allowance's decomposition "
        f"even at zero delta. Got:\n{result.stdout}"
    )

    # Arm 2 (negative control): one byte past the NEW allowance still fails.
    over = _run_checker(
        [
            "--policy",
            "merge05",
            "--baseline",
            str(_BASE01_BASELINE),
            "--avr-log",
            f"leonardo={_FIXTURES / 'planted_size_baseline_policy_leonardo_growth.log'}",
        ]
    )
    assert over.returncode == 1, (
        "NEGATIVE CONTROL: expected exit 1 on a planted +307 B leonardo growth — one "
        "byte beyond the new 306 B allowance (96 B defect-fix + 210 B page-size-seam "
        "exemptions). If this passes, the exemption has become a blank cheque and "
        "the forward tripwire is gone.\n"
        f"stdout:\n{over.stdout}\nstderr:\n{over.stderr}"
    )
    assert "delta=+307" in over.stdout, (
        f"Expected the one-past-the-exemption delta named. Got:\n{over.stdout}"
    )
    assert "allowance of 306 B" in over.stdout, (
        f"Expected the leonardo effective allowance named. Got:\n{over.stdout}"
    )
    assert "band 0 B + defect-fix exemption 96 B + page-size-seam exemption 210 B" in over.stdout, (
        f"Expected the FAIL line to decompose the allowance into all three terms. "
        f"Got:\n{over.stdout}"
    )


def test_base01_is_not_re_anchored_by_the_new_exemption():
    """Phase 149 (D-12, PGSZ-04) binding precondition, captured as a leg rather
    than only stated in prose: BASE-01's avr_targets are byte-unchanged and both
    flash band literals are byte-unchanged after the page-size-seam exemption
    landed. A green --policy merge05 run after a re-anchor would mean the anchor
    moved, not that growth stayed inside the band -- BASE-01's own re_anchor_note
    says exactly this."""
    with open(_BASE01_BASELINE) as f:
        base01 = json.load(f)
    assert base01["avr_targets"]["uno"]["flash_used"] == 24824
    assert base01["avr_targets"]["uno328pb"]["flash_used"] == 24874
    assert base01["avr_targets"]["leonardo"]["flash_used"] == 26906
    assert base01["avr_targets"]["uno"]["ram_used"] == 1573
    assert base01["avr_targets"]["uno328pb"]["ram_used"] == 1579
    assert base01["avr_targets"]["leonardo"]["ram_used"] == 2014

    checker_src = (_REPO_ROOT / "scripts" / "check_size_baseline.py").read_text()
    assert "MERGE05_UNO_CLASS_FLASH_BAND = 64" in checker_src, (
        "the uno-class flash band must stay exactly 64 -- widening it would "
        "silently admit unrelated future growth"
    )
    assert "MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96" in checker_src, (
        "the Phase 145 defect-fix exemption must stay exactly 96 -- it is not "
        "this phase's number to change"
    )


def test_policy_merge05_fires_on_uno_class_over_band():
    """Coverage 9 — the planted +371 B Uno-class flash growth (one byte outside the
    EFFECTIVE 370 B allowance: the unchanged 64 B band plus the 96 B defect-fix
    exemption plus the Phase 149 210 B page-size-seam exemption) must fail --policy
    merge05, naming the computed delta, the allowance it exceeds, and the
    allowance's full three-term decomposition.

    Re-derived from +161 B by Phase 149 (D-12), for the same D-18 reason Phase 144
    Plan 05 and the v1.31 Phase 145 adjudication each re-derived it before: once
    the new exemption exists, a +161 B plant is INSIDE the allowance and this leg
    would have gone falsely green while still claiming to prove a firing. The
    plant's single cause (a raised uno `used` figure) and its role (exactly one
    byte outside the enforced ceiling) are unchanged; only the number moved, and
    only because the ceiling moved."""
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
        f"expected non-zero exit on a planted +371 B uno-class flash growth.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "delta=+371" in result.stdout, f"Expected 'delta=+371'. Got:\n{result.stdout}"
    assert "allowance of 370 B" in result.stdout, (
        f"Expected 'allowance of 370 B'. Got:\n{result.stdout}"
    )
    assert (
        "band 64 B + defect-fix exemption 96 B + page-size-seam exemption 210 B"
        in result.stdout
    ), (
        "Expected the allowance decomposed into all three terms: the unchanged "
        "64 B band, the 96 B defect-fix exemption and the 210 B page-size-seam "
        f"exemption. Got:\n{result.stdout}"
    )


def test_policy_merge05_fires_on_leonardo_growth():
    """Coverage 10 — the planted +307 B Leonardo flash growth must fail --policy
    merge05 (Leonardo's base band is still 0 B must-not-grow, so its effective
    allowance is exactly the 96 B defect-fix exemption plus the 210 B page-size-
    seam exemption = 306 B, and +307 is one byte past it), naming the env and the
    delta.

    Re-derived from +97 B by Phase 149 (D-12) for the same reason as Coverage 9
    above: a +97 B plant now sits inside the new exemption and this leg would have
    gone falsely green. The plant's single cause and its one-byte-past-the-ceiling
    role are unchanged. This is the same fixture
    test_policy_merge05_admits_the_documented_defect_fix uses as its negative
    control — deliberately shared rather than duplicated byte-identically; see that
    leg's docstring for the division of labour."""
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
        f"expected non-zero exit on a planted +307 B Leonardo flash growth.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "leonardo" in result.stdout, f"Expected 'leonardo'. Got:\n{result.stdout}"
    assert "delta=+307" in result.stdout, f"Expected 'delta=+307'. Got:\n{result.stdout}"


def test_policy_merge05_fires_on_ram_move():
    """Coverage 11 — the planted +3 B RAM move (one byte past the Phase 149
    page-size-seam RAM exemption of 2 B) must fail --policy merge05, naming
    ram_used and the RAM allowance's own decomposition.

    Before Phase 149, RAM equality was enforced with zero tolerance under the
    band mode, and a +1 B plant fired. Phase 149 (D-12) measured RAM moving by
    +2 B on all three AVR targets (the single `uint16_t page_size` handle field)
    and funded it with a named RAM exemption -- so the old +1 B plant now sits
    INSIDE the tolerance and would go falsely green. Re-derived to +3 B, one byte
    past the new 2 B tolerance, preserving the plant's single cause and its
    one-byte-past-the-ceiling role."""
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
        f"expected non-zero exit on a planted +3 B RAM move.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "ram_used" in result.stdout, f"Expected 'ram_used'. Got:\n{result.stdout}"
    assert "delta=+3" in result.stdout, f"Expected 'delta=+3'. Got:\n{result.stdout}"
    assert "ram allowance of 2 B" in result.stdout, (
        f"Expected 'ram allowance of 2 B'. Got:\n{result.stdout}"
    )
    assert "page-size-seam exemption 2 B" in result.stdout, (
        f"Expected the RAM allowance's own decomposition named. Got:\n{result.stdout}"
    )


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
