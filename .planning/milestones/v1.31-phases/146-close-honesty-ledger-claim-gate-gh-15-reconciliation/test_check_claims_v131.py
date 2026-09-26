"""Tests for 146-check-claims.py (Phase 146 Plan 04, CLOSE-01, D-12 first proof).

This is the MANDATORY anti-hollow pairing for the v1.31 claim gate: a checker
with no negative-fixture test is exactly this project's v1.12 hollow-GATE-03
failure mode -- a declared-empty detector that could never fail, because
nothing concrete was ever asserted against it. Every planted-violation leg
below invokes the gate as a real subprocess against a committed fixture file
through the `FIRESTARTER_CLAIMSCAN_TARGETS_146` env seam -- never an
in-process import -- so a passing suite proves the *gate* (not the test) fails
the build on a real violation.

**What this suite proves, and what it does not.** Per D-12 CLOSE-01 requires
two different proofs, and this file is only the first: it proves the pattern
table, the per-file caveat rules, the fail-closed branch, the never-vacuous
branch and the argv/env precedence each fire on a document authored to make
them fire. It does **not** prove the gate is wired to the files that actually
ship -- fixtures are, by construction, not the closing artifacts. That second
proof is plan 146-11's plant-and-revert transcript against a real, tracked
closing artifact, recorded in `146-CITATIONS.md`. A green run of this suite
must never be reported as by itself discharging CLOSE-01.

Filename note: `test_check_claims_v131.py`, deliberately distinct. Two files
literally named `test_check_permitted_claims.py` (v1.22, v1.23) plus
`test_check_permitted_claims_v130.py` (Phase 137) already sit in sibling phase
directories; a fourth same-named module would collide under pytest's default
`prepend` import mode for anyone running pytest from `/workspaces`. The gate's
own filename, `146-check-claims.py`, is **not a valid Python identifier** --
harmless for `spec_from_file_location` (the module *name* argument is
arbitrary) and for `subprocess`, and one more reason the behavioural legs stay
subprocess-driven.

Every planted fixture's label set was PROBED with the gate's own `scan_text`
before the assertion below was written -- see `146-04-SUMMARY.md` for the five
verbatim probe results. This discipline is not ceremonial: the recorded plant
candidate at `146-PATTERNS.md:357` fires the `confirmed-working` label but
**not** the `works-on-silicon` label, because the second pattern's verb form
does not match, and a plan that asserted both would have gone red for a reason
unrelated to the gate. Forbidden phrases are therefore cited here by label id
or by `file:line`, never reproduced -- the two label-id literals below that
must appear verbatim are the two the gate itself prints.

Coverage (15 legs):
   1. Clean control via the seam: exit 0, `PASS:` in stdout.
   2. Planted overclaim (`planted_forbidden_claim.md`) flips the gate to a
      non-zero exit with `FAIL:` and the **specific** probed label
      `confirmed-working` -- not merely a non-zero exit.
   3. Planted missing-caveat (`planted_missing_caveat.md`) flips the gate to a
      non-zero exit naming the caveat bucket the gate actually prints and the
      one absent label.
   4. Planted bare-claim-word (`planted_proven_unqualified.md`) flips the gate
      to a non-zero exit with its own probed label. This leg REPLACES the
      donor suite's relational-rule leg: this gate has no relational rule, no
      proximity window and no exclusion mechanism (D-14), and none is added.
   5. Fail-closed on a scan target that does not exist on disk.
   6. Never-vacuous on an explicitly empty seam -- and explicitly no fall-back
      to the real defaults.
   7. The `PASS:` line names BOTH clean controls in one run (anti-skip).
   8. Positional argv beats the seam (the documented precedence, pinned
      against a future silent inversion of the gate's `is not None` check).
   9. No argv and no seam -> exit 0 with a `PASS:` line naming all five real
      closing artifacts. This is the literal mechanical discharge of "armed
      against the real files" and it **cannot pass until plan 146-11's
      artifacts exist**; it is authored here, observed RED for the named
      reason (the five artifacts reported not found on disk), and plan 146-11
      records its GREEN. A pre-authored leg that has only ever been red is not
      evidence, which is why its expected red reason is verified rather than
      assumed.
  10. Introspection: every `_DEFAULT_TARGETS` entry resolves strictly INSIDE
      this phase's own directory -- the assertion that makes a future naive
      copy into another phase directory fail loudly instead of silently
      resolving elsewhere and passing vacuously.
  11. Introspection: every `_DEFAULT_TARGETS` basename carries this phase's
      own `146-` prefix.
  12. Introspection: every `_DEFAULT_TARGETS` basename has a `_CAVEAT_RULES`
      entry -- a missing entry is a typo, not a policy.
  13. Introspection: an unrecognised basename resolves to the FULL caveat set,
      so `_required_caveats_for()` fails closed.
  14. Behavioural: the caveat-exempt basename with NEITHER caveat exits 0 --
      D-11's per-file exemption demonstrated behaviourally, not only by
      introspection.
  15. Behavioural: the same exempt basename WITH a forbidden phrase still
      exits non-zero, and no caveat bucket is printed -- the exemption is
      caveat-only and is not a blanket skip. Legs 14 and 15 are a pair;
      either alone would be insufficient.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_SCANNER = _HERE / "146-check-claims.py"

# The two required-caveat needles, as literal strings rather than as imported
# regexes: legs 14 and 15 must build their input WITHOUT importing the gate,
# so the behavioural legs stay honestly subprocess-only.
_CAVEAT_NEEDLES = ("6.25", "silicon-margin")


def _run_scanner(targets=None, argv=None):
    """Invoke the gate as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_CLAIMSCAN_TARGETS_146 to that
    exact string (so the empty string is reachable, per leg 6) -- when None,
    the variable is removed from the child's environment entirely, reaching
    the gate's "variable absent -> use real defaults" path. The seam name is
    this phase's own; the donor's `_V130`/`_V131` names are deliberately never
    touched here, because the `_V131` one is live in Phase 139 of this same
    milestone and setting it would aim this suite at another phase's gate.

    Fixture arguments are relative paths, which resolve because `cwd` is this
    phase directory.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_146"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_146", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


def _import_scanner_module():
    """Import `146-check-claims.py` by file path (never as a package) solely
    to introspect its module-level constants -- used only by legs 10-13, which
    must inspect the real objects the running process would use rather than a
    re-derived copy. The module name argument is arbitrary, which is what lets
    a filename that is not a valid Python identifier be loaded at all."""
    spec = importlib.util.spec_from_file_location(
        "check_claims_146_introspect", str(_SCANNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pass_line(stdout):
    """Return the single line of `stdout` that opens the gate's PASS report,
    or None. Used by the anti-skip leg so 'both basenames appear' is asserted
    of ONE line rather than of the whole output."""
    for line in stdout.splitlines():
        if line.startswith("PASS:"):
            return line
    return None


# ---------------------------------------------------------------------------
# Leg 1: clean-pass baseline through the seam
# ---------------------------------------------------------------------------


def test_gate_exits_zero_on_the_clean_control():
    """A clean control injected through the env seam must exit 0 with `PASS:`
    -- proves the seam itself introduces no false positive, and that the
    control's two required caveats are recognised (the control carries both,
    because a fixture basename is absent from `_CAVEAT_RULES` and therefore
    held to the fail-closed FULL caveat set)."""
    result = _run_scanner(targets="fixtures/clean_control.md")
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on a clean control.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 2: planted overclaim, asserted on its PROBED label
# ---------------------------------------------------------------------------


def test_planted_overclaim_flips_the_gate_to_failure():
    """`fixtures/planted_forbidden_claim.md` MUST fail the gate, attributed to
    the `confirmed-working` label -- the label the probe actually returned
    (one hit, at fixture line 14), not a label this leg assumed. The fixture
    carries both required caveats, so this is a single-reason failure: any
    caveat bucket in the output would mean the fixture drifted."""
    result = _run_scanner(targets="fixtures/planted_forbidden_claim.md")
    assert result.returncode != 0, (
        f"gate exited 0 on a planted forbidden-phrase violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "forbidden phrase match [confirmed-working]" in result.stdout, (
        "Expected the probed confirmed-working label in output but got:\n"
        f"{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        "This plant must fail for exactly ONE reason; a caveat bucket means "
        f"the fixture lost a caveat:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 3: planted missing caveat, asserted on the bucket the gate prints
# ---------------------------------------------------------------------------


def test_planted_missing_caveat_flips_the_gate_to_failure():
    """`fixtures/planted_missing_caveat.md` MUST fail the gate, naming the
    caveat bucket the gate actually emits and the ONE absent label the probe
    returned (`ceiling-narrowing`; the voltage caveat is present). The bucket
    string asserted here is read from the gate's own source -- the donor
    suite's v1.30 bucket wording is deliberately not reused, because this gate
    never prints it."""
    result = _run_scanner(targets="fixtures/planted_missing_caveat.md")
    assert result.returncode != 0, (
        f"gate exited 0 on a planted missing-caveat violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "missing a required 6.25 V ceiling caveat" in result.stdout, (
        f"Expected the caveat bucket label in output but got:\n{result.stdout}"
    )
    assert "missing required caveat [ceiling-narrowing]" in result.stdout, (
        "Expected the one probed absent caveat label in output but got:\n"
        f"{result.stdout}"
    )
    assert "forbidden phrase match" not in result.stdout, (
        "This plant must fail for exactly ONE reason; a forbidden bucket "
        f"means the fixture drifted:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 4: planted bare claim word (replaces the donor's relational-rule leg)
# ---------------------------------------------------------------------------


def test_planted_bare_claim_word_flips_the_gate_to_failure():
    """`fixtures/planted_proven_unqualified.md` MUST fail the gate, naming the
    `proven-unqualified` label the probe returned (one hit, at fixture line
    12, after a hyphen -- a hyphen is a non-word character, so the pattern's
    trailing word boundary holds). This leg replaces the donor suite's
    relational `self-verifying` leg: this gate has no relational rule, and
    D-14 forbids adding one."""
    result = _run_scanner(targets="fixtures/planted_proven_unqualified.md")
    assert result.returncode != 0, (
        f"gate exited 0 on a planted bare-claim-word violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "forbidden phrase match [proven-unqualified]" in result.stdout, (
        f"Expected the probed pattern-10 label in output but got:\n{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        "This plant must fail for exactly ONE reason; a caveat bucket means "
        f"the fixture lost a caveat:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 5: fail-closed on a nonexistent scan target
# ---------------------------------------------------------------------------


def test_fail_closed_on_a_nonexistent_scan_target():
    """A scan target that does not exist on disk MUST fail closed (exit
    non-zero), never vacuously pass with the target silently skipped. This is
    also the branch a PARTIAL default set lands in, which is how D-11's
    all-or-nothing arming contract is achieved with no extra code."""
    result = _run_scanner(targets="fixtures/does-not-exist.md")
    assert result.returncode != 0, (
        f"gate exited 0 with a missing scan target.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "not found on disk" in result.stdout, (
        f"Expected a not-found message in output but got:\n{result.stdout}"
    )
    assert "fixtures/does-not-exist.md" in result.stdout, (
        "The not-found message must NAME the absent target, or this leg "
        f"cannot tell which target was skipped:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 6: never-vacuous on an explicitly empty target list
# ---------------------------------------------------------------------------


def test_never_vacuous_on_an_explicitly_empty_target_list():
    """FIRESTARTER_CLAIMSCAN_TARGETS_146 explicitly set to the empty string
    MUST resolve to zero targets and exit non-zero, and MUST NOT silently
    fall back to the real defaults -- which is what the gate's `is not None`
    env check buys. Both negative assertions are kept: `PASS:` absent, and
    `UNARMED:` absent. This gate deliberately has NO unarmed branch (Phase
    137's exit-0-on-nothing-scanned path was not ported), and the second
    assertion is what pins that absence rather than leaving it to a
    docstring."""
    result = _run_scanner(targets="")
    assert result.returncode != 0, (
        f"gate exited 0 with an explicitly empty target list.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" not in result.stdout
    assert "UNARMED:" not in result.stdout, (
        "An UNARMED line would mean an exit-0-on-nothing-scanned branch was "
        f"reintroduced:\n{result.stdout}"
    )
    assert "no scan targets resolved" in result.stdout, (
        f"Expected the never-vacuous message in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 7: the PASS line names every scanned file (anti-skip)
# ---------------------------------------------------------------------------


def test_pass_line_names_every_scanned_file():
    """Pointing the gate at both clean controls at once must produce a SINGLE
    `PASS:` line naming BOTH basenames -- proof that neither file was silently
    skipped. Asserted of the one PASS line rather than of the whole output, so
    a basename appearing in some other line cannot satisfy this leg."""
    result = _run_scanner(
        targets=os.pathsep.join(
            ["fixtures/clean_control.md", "fixtures/clean_control_second.md"]
        )
    )
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on two clean controls.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    line = _pass_line(result.stdout)
    assert line is not None, f"No PASS: line in output:\n{result.stdout}"
    assert "clean_control.md" in line, (
        f"Expected the first control named in the PASS: line but got:\n{line}"
    )
    assert "clean_control_second.md" in line, (
        f"Expected the second control named in the PASS: line but got:\n{line}"
    )


# ---------------------------------------------------------------------------
# Leg 8: positional argv precedence beats the env seam
# ---------------------------------------------------------------------------


def test_positional_argv_precedence_beats_the_env_seam():
    """Positional argv must win over FIRESTARTER_CLAIMSCAN_TARGETS_146. The
    seam is pointed at a plant while argv passes a clean control -- the run
    must succeed, pinning the documented precedence so a future edit cannot
    silently invert it. What this leg pins concretely is the ordering of the
    `if argv:` branch ahead of the `is not None` env branch in the gate's
    target resolution."""
    result = _run_scanner(
        targets="fixtures/planted_forbidden_claim.md",
        argv=["fixtures/clean_control.md"],
    )
    assert result.returncode == 0, (
        f"gate exited {result.returncode} even though argv should have "
        f"overridden the env seam.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
    assert "planted_forbidden_claim.md" not in result.stdout, (
        "The seam's plant must not have been scanned at all when argv is "
        f"supplied:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 9: armed against the five real closing artifacts
#
# ⚠ EXPECTED RED until plan 146-11. Authored here (plan 146-04) so that the
# arming contract is written down as an assertion rather than as prose, and
# observed RED for its NAMED reason: the gate reports the five closing
# artifacts as not found on disk. It is NOT a defect of plan 146-04, and it
# must NOT be weakened, xfail-marked or deselected in the file to make a suite
# run green -- plan 146-11 authors the artifacts and records the GREEN.
# ---------------------------------------------------------------------------


def test_armed_against_the_five_real_closing_artifacts():
    """Invoked with no argv and no seam (the real defaults), the gate MUST
    exit 0 with a `PASS:` line naming all five real `146-`-prefixed closing
    artifacts. This is the literal mechanical discharge of "armed against the
    real files".

    Two states this leg distinguishes, and only one of them is acceptable at
    any given time:

    * **RED with the five artifacts reported not found on disk** -- the
      correct state from plan 146-04 (which authors this leg) until plan
      146-11 authors the artifacts. The gate's fail-closed missing-target
      branch is doing exactly its job.
    * **GREEN** -- the state plan 146-11 records.

    Any other red -- a collection error, an import error, a missing fixture, a
    wrong basename, a seam-name typo -- is a defect in the SUITE, not the
    expected red, and the failure text is what tells the two apart. A
    regression from green back to red after 146-11 means either the arming
    mechanism broke or one of the five artifacts now fails the
    forbidden-phrase/caveat scan; in neither case may this leg be weakened,
    and the flagged artifact must be fixed instead."""
    result = _run_scanner(targets=None, argv=None)
    assert result.returncode == 0, (
        f"gate exited {result.returncode} against the five real default "
        "targets -- expected PASS + exit 0. If the output below reports the "
        "five closing artifacts as 'not found on disk', this is the EXPECTED "
        "pre-146-11 red and the arming contract is intact; any other message "
        "is a defect in this suite.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )
    for name in (
        "146-LEDGER.md",
        "146-CORRECTIONS.md",
        "146-GH15-RECONCILIATION.md",
        "146-RELEASE-NOTES-fw.md",
        "146-RELEASE-NOTES-app.md",
    ):
        assert name in result.stdout, (
            f"Expected {name!r} named in the PASS: message but got:\n"
            f"{result.stdout}"
        )


# ---------------------------------------------------------------------------
# Leg 10 (introspection): default targets resolve inside THIS phase directory
# ---------------------------------------------------------------------------


def test_default_targets_resolve_inside_this_phase_directory():
    """The gate's own `_DEFAULT_TARGETS` must resolve strictly INSIDE this
    phase's own directory (`_HERE`, computed fresh from `__file__`), never a
    sibling phase directory named by a string constant. This is the one
    assertion that makes a future naive copy into another phase directory fail
    loudly instead of silently resolving elsewhere and passing vacuously --
    the recorded cross-phase-copy defect where a reused checker's
    `_HERE`-relative defaults scanned nothing and exited 0."""
    module = _import_scanner_module()
    expected_dir = str(_HERE.resolve())
    assert module._DEFAULT_TARGETS, "_DEFAULT_TARGETS must not be empty"
    for entry in module._DEFAULT_TARGETS:
        assert os.path.dirname(entry) == expected_dir, (
            f"_DEFAULT_TARGETS entry {entry!r} does not resolve inside this "
            f"phase's own directory {expected_dir!r} -- this is the exact "
            "cross-phase-copy defect this test exists to catch"
        )


# ---------------------------------------------------------------------------
# Leg 11 (introspection): default target basenames carry this phase's prefix
# ---------------------------------------------------------------------------


def test_default_targets_basenames_carry_this_phases_prefix():
    """Every `_DEFAULT_TARGETS` basename must start with this phase's own
    `146-` prefix. A copy carrying stale `139-*`, `137-*` or `130-*` names
    goes red immediately here."""
    module = _import_scanner_module()
    assert module._DEFAULT_TARGETS, "_DEFAULT_TARGETS must not be empty"
    for entry in module._DEFAULT_TARGETS:
        basename = os.path.basename(entry)
        assert basename.startswith("146-"), (
            f"_DEFAULT_TARGETS basename {basename!r} does not carry this "
            "phase's own '146-' prefix -- this is the exact stale-name defect "
            "this test exists to catch"
        )


# ---------------------------------------------------------------------------
# Leg 12 (introspection): every default target has a caveat-rule entry
# ---------------------------------------------------------------------------


def test_every_default_targets_basename_has_a_caveat_rule_entry():
    """Every `_DEFAULT_TARGETS` basename must have an explicit `_CAVEAT_RULES`
    entry. The gate's `_required_caveats_for()` fails closed on an unknown
    basename (leg 13), so a missing entry would not weaken the gate -- but it
    would silently hold a file to a rule its author never chose, which is a
    typo, not a policy. This leg is the one that catches a rename of a closing
    artifact that updated `_DEFAULT_TARGETS` and forgot the rule map."""
    module = _import_scanner_module()
    assert module._DEFAULT_TARGETS, "_DEFAULT_TARGETS must not be empty"
    for entry in module._DEFAULT_TARGETS:
        basename = os.path.basename(entry)
        assert basename in module._CAVEAT_RULES, (
            f"_DEFAULT_TARGETS basename {basename!r} has no _CAVEAT_RULES "
            "entry -- an omitted entry is a typo, not a policy; state the "
            "rule explicitly (the empty frozenset is how an exemption is "
            "declared)"
        )


# ---------------------------------------------------------------------------
# Leg 13 (introspection): an unrecognised basename gets the FULL caveat set
# ---------------------------------------------------------------------------


def test_unrecognised_basename_resolves_to_the_full_caveat_set():
    """`_required_caveats_for()` must return the FULL caveat label set for a
    basename absent from `_CAVEAT_RULES`. An empty-set default would let a
    future rename of a real closing artifact disable its caveat check
    silently, with the gate still reporting PASS. Also asserts the full set is
    non-empty and is derived from the pattern table rather than restated, so a
    third caveat pattern cannot be added without this default picking it
    up."""
    module = _import_scanner_module()
    assert module._ALL_CAVEAT_LABELS, "_ALL_CAVEAT_LABELS must not be empty"
    assert module._ALL_CAVEAT_LABELS == frozenset(
        label for label, _prose, _pattern in module.REQUIRED_CAVEAT_PATTERNS
    ), (
        "_ALL_CAVEAT_LABELS must be derived from REQUIRED_CAVEAT_PATTERNS, "
        "not restated"
    )
    for unknown in (
        "146-NO-SUCH-ARTIFACT.md",
        "clean_control.md",
        "146-CORRECTIONS.md.bak",
    ):
        assert unknown not in module._CAVEAT_RULES, (
            f"{unknown!r} was chosen as an UNRECOGNISED basename for this "
            "leg but now has a rule entry -- pick another, do not weaken the "
            "assertion"
        )
        assert (
            module._required_caveats_for(unknown) == module._ALL_CAVEAT_LABELS
        ), (
            f"_required_caveats_for({unknown!r}) did not fail closed to the "
            "full caveat set -- a renamed closing artifact could then pass "
            "with no caveat at all"
        )


# ---------------------------------------------------------------------------
# Leg 14 (behavioural): the caveat-exempt basename passes with NO caveat
# ---------------------------------------------------------------------------


def test_caveat_exempt_basename_passes_without_either_caveat(tmp_path):
    """D-11 exempts `146-CORRECTIONS.md` from the caveat rule: it is a
    register of factual corrections, each row citing a false statement by
    `file:line` and giving its corrected text, and it must not be failed by a
    rule written for a release body. This leg proves that exemption
    BEHAVIOURALLY -- a document written under that exact basename, carrying
    NEITHER required caveat and no forbidden phrase, exits 0. Introspecting
    `_CAVEAT_RULES` (leg 12) would only prove the map's contents, not that
    `main()` consumes it."""
    doc = tmp_path / "146-CORRECTIONS.md"
    doc.write_text(
        "# Corrections register (behavioural fixture for the exempt basename)\n"
        "\n"
        "| # | Origin finding | Owning file:line | Corrected text |\n"
        "|---|---|---|---|\n"
        "| 1 | F-144-01 | example.md:277 | The measured tip is 47 + 32 = 79. |\n"
        "\n"
        "This document deliberately carries neither required caveat: the\n"
        "voltage figure and the margin phrase both belong in a release body,\n"
        "not in a register whose rows are citations by line number.\n",
        encoding="utf-8",
    )
    for needle in _CAVEAT_NEEDLES:
        assert needle not in doc.read_text(encoding="utf-8").lower(), (
            f"this leg's document must carry NO caveat, but {needle!r} is "
            "present -- it would then pass for the wrong reason"
        )
    result = _run_scanner(targets=str(doc))
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on the caveat-exempt basename with "
        f"neither caveat present -- D-11's exemption is not being consumed by "
        f"main().\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
    assert "missing required caveat" not in result.stdout, (
        f"No caveat may be demanded of the exempt basename:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 15 (behavioural): the exemption is caveat-only, not a blanket skip
# ---------------------------------------------------------------------------


def test_caveat_exempt_basename_still_fails_on_a_forbidden_phrase(tmp_path):
    """The other half of the pair. The SAME exempt basename, carrying a
    forbidden phrase and still no caveat, must exit non-zero on the forbidden
    phrase alone -- so the D-11 exemption is caveat-only and is not a blanket
    skip of the file. Either leg alone would be insufficient: leg 14 without
    this one would be consistent with the gate skipping the exempt file
    entirely.

    The document is derived from the already-probed plant fixture with its two
    caveat lines filtered out, so this leg introduces no new forbidden literal
    of its own and reuses the label the probe recorded."""
    source = (_HERE / "fixtures" / "planted_forbidden_claim.md").read_text(
        encoding="utf-8"
    )
    filtered = "\n".join(
        line
        for line in source.splitlines()
        if not any(needle in line.lower() for needle in _CAVEAT_NEEDLES)
    )
    assert "The planted sentence:" in filtered, (
        "the plant line was filtered away along with the caveats -- the "
        "fixture's layout changed and this leg would test nothing"
    )
    for needle in _CAVEAT_NEEDLES:
        assert needle not in filtered.lower(), (
            f"{needle!r} survived filtering; this leg must present the exempt "
            "basename with NO caveat so the only possible failure is the "
            "forbidden phrase"
        )
    doc = tmp_path / "146-CORRECTIONS.md"
    doc.write_text(filtered, encoding="utf-8")
    result = _run_scanner(targets=str(doc))
    assert result.returncode != 0, (
        f"gate exited 0 on the caveat-exempt basename carrying a forbidden "
        f"phrase -- the D-11 exemption has become a blanket skip.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "forbidden phrase match [confirmed-working]" in result.stdout, (
        f"Expected the probed confirmed-working label in output but got:\n"
        f"{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        "The exempt basename must still not be held to any caveat; only the "
        f"forbidden phrase may be reported:\n{result.stdout}"
    )
