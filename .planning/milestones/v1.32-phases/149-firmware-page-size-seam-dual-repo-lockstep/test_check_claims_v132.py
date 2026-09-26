"""Tests for 149-check-claims.py (Phase 149 Plan 02, PGSZ-05, D-19 first proof).

This is the MANDATORY anti-hollow pairing for the v1.32 page-size claim gate: a
checker with no negative-fixture test is exactly this project's v1.12
hollow-GATE-03 failure mode -- a declared-empty detector that could never
fail, because nothing concrete was ever asserted against it. Every
planted-violation leg below invokes the gate as a real subprocess against a
committed fixture file through the `FIRESTARTER_CLAIMSCAN_TARGETS_149` env
seam -- never an in-process import -- so a passing suite proves the *gate*
(not the test) fails the build on a real violation.

**Analog and deviations.** Source: `test_check_claims_v131.py` in
`.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/`,
read in full -- the subprocess runner, the by-path importer and the PASS-line
helper are transcribed unchanged in mechanism (renamed to this phase's own
env seam and module path). The donor's 15 legs are transcribed here, renamed,
with one substantive adaptation each:

  * Leg 9 (`test_armed_against_the_real_149_artifacts`) is not a pre-authored
    RED: D-19's target list at this plan's authoring time is the single
    `149-PAGE-SIZE.md` artifact plan 01 already wrote, so this leg is
    observed GREEN from the moment this suite is committed, not three plans
    later.
  * Legs 14/15 (the caveat-exempt basename pair) exercise
    `149-CLAIM-GATE-TRANSCRIPTS.md` -- the gate's own `_CAVEAT_RULES` maps
    that basename to the empty set, mirroring the donor's own D-11 exemption
    for `146-CORRECTIONS.md` (an evidence register, not a claim body). The
    files these two legs write are throwaway `tmp_path` fixtures carrying
    that basename; they are never the real committed transcript.

Five legs are new, covering this phase's own measured defect
(`149-RESEARCH.md` §X-2, the `\\bproven\\b`-after-a-hyphen collision with
PGSZ-05's own mandated phrase) and this phase's own exclusion list:

  16. `test_the_required_phrase_alone_does_not_trip_the_narrowed_proven_pattern`
      -- the X-2 forward direction: a document whose only occurrence of the
      word "proven" is inside the mandated compound passes clean.
  17. `test_an_unqualified_proven_still_trips_the_narrowed_pattern` -- the X-2
      negative control. SEEN to fail the gate, not merely asserted to.
  18. `test_the_transcript_file_is_not_a_gate_target` -- the transcript file
      (which necessarily quotes forbidden vocabulary as evidence) is absent
      from `_DEFAULT_TARGETS`.
  19. `test_context_research_and_discussion_log_are_not_gate_targets` -- the
      three upstream discussion artifacts (which also carry the rejected
      vocabulary in prose) are absent from `_DEFAULT_TARGETS`.
  20. `test_every_forbidden_pattern_has_a_planted_fixture` -- every label this
      phase added or modified has its own isolated planted fixture.

Every planted fixture's label set was probed against the gate's own
`scan_text` before being committed -- see `149-02-SUMMARY.md` for the
transcript. This discipline is not ceremonial: several candidate fixture
wordings during authoring tripped an UNINTENDED second label (writing out a
forbidden label's own name in a fixture's HTML comment, for instance, can
itself contain a forbidden substring) and were rewritten before being
committed, precisely so no leg below asserts a coincidence.

Filename note: `test_check_claims_v132.py`, deliberately distinct from every
sibling phase's same-shaped suite, for the same reason the donor's own
filename note gives -- pytest's default `prepend` import mode collides on a
repeated basename run from `/workspaces`. The gate's own filename,
`149-check-claims.py`, is not a valid Python identifier -- harmless for
`spec_from_file_location` (the module *name* argument is arbitrary) and for
`subprocess`, and one more reason the behavioural legs stay subprocess-driven.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_SCANNER = _HERE / "149-check-claims.py"

# The one required-caveat needle, as a literal string rather than an imported
# regex: legs 14 and 15 must build their input WITHOUT importing the gate, so
# the behavioural legs stay honestly subprocess-only.
_CAVEAT_NEEDLE = "software-proven and unvalidated on silicon"


def _run_scanner(targets=None, argv=None):
    """Invoke the gate as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_CLAIMSCAN_TARGETS_149 to that
    exact string (so the empty string is reachable, per leg 6) -- when None,
    the variable is removed from the child's environment entirely, reaching
    the gate's "variable absent -> use real defaults" path. The seam name is
    this phase's own; no other phase's seam is ever touched here.

    Fixture arguments are relative paths, which resolve because `cwd` is this
    phase directory.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_149"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_149", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


def _import_scanner_module():
    """Import `149-check-claims.py` by file path (never as a package) solely
    to introspect its module-level constants -- used only by legs 10-13 and
    18-19, which must inspect the real objects the running process would use
    rather than a re-derived copy. The module name argument is arbitrary,
    which is what lets a filename that is not a valid Python identifier be
    loaded at all."""
    spec = importlib.util.spec_from_file_location(
        "check_claims_149_introspect", str(_SCANNER)
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
    control's required caveat is recognised (the control carries it, because
    a fixture basename is absent from `_CAVEAT_RULES` and therefore held to
    the fail-closed FULL caveat set)."""
    result = _run_scanner(targets="fixtures/clean_control.md")
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on a clean control.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 2: planted overclaim, asserted on its probed label
# ---------------------------------------------------------------------------


def test_planted_overclaim_flips_the_gate_to_failure():
    """`fixtures/planted_forbidden_claim.md` MUST fail the gate, attributed to
    the `confirmed-working` label -- the label the probe actually returned,
    not a label this leg assumed. The fixture carries the required caveat, so
    this is a single-reason failure: a caveat bucket in the output would mean
    the fixture drifted."""
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
        f"the fixture lost its caveat:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 3: planted missing caveat, asserted on the bucket the gate prints
# ---------------------------------------------------------------------------


def test_planted_missing_caveat_flips_the_gate_to_failure():
    """`fixtures/planted_missing_caveat.md` MUST fail the gate, naming the
    caveat bucket the gate actually emits and the one required label. The
    bucket string asserted here is read from the gate's own source."""
    result = _run_scanner(targets="fixtures/planted_missing_caveat.md")
    assert result.returncode != 0, (
        f"gate exited 0 on a planted missing-caveat violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert (
        "missing a required software-proven-unvalidated caveat" in result.stdout
    ), f"Expected the caveat bucket label in output but got:\n{result.stdout}"
    assert (
        "missing required caveat [software-proven-unvalidated]" in result.stdout
    ), (
        "Expected the one required caveat label in output but got:\n"
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
    `proven-unqualified` label via its narrowed pattern -- the plant carries a
    bare `bench-proven` compound, which is NOT the `software-proven` compound
    the lookbehind permits. This leg replaces the donor suite's relational
    `self-verifying` leg: this gate has no relational rule, and D-14 forbids
    adding one."""
    result = _run_scanner(targets="fixtures/planted_proven_unqualified.md")
    assert result.returncode != 0, (
        f"gate exited 0 on a planted bare-claim-word violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
    assert "forbidden phrase match [proven-unqualified]" in result.stdout, (
        f"Expected the probed proven-unqualified label in output but got:\n"
        f"{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        "This plant must fail for exactly ONE reason; a caveat bucket means "
        f"the fixture lost its caveat:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 5: fail-closed on a nonexistent scan target
# ---------------------------------------------------------------------------


def test_fail_closed_on_a_nonexistent_scan_target():
    """A scan target that does not exist on disk MUST fail closed (exit
    non-zero), never vacuously pass with the target silently skipped."""
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
    """FIRESTARTER_CLAIMSCAN_TARGETS_149 explicitly set to the empty string
    MUST resolve to zero targets and exit non-zero, and MUST NOT silently
    fall back to the real defaults. This gate deliberately has NO
    unarmed/exit-0-on-nothing-scanned branch (Phase 137's escape hatch was
    not ported), and the second assertion pins that absence."""
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
    skipped."""
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
    """Positional argv must win over FIRESTARTER_CLAIMSCAN_TARGETS_149. The
    seam is pointed at a plant while argv passes a clean control -- the run
    must succeed, pinning the documented precedence so a future edit cannot
    silently invert it."""
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
# Leg 9: armed against the real 149 artifact
#
# Unlike the donor's own leg 9, this one is observed GREEN from the moment
# this suite is committed: D-19's target list at this plan's authoring time
# is the single `149-PAGE-SIZE.md` artifact plan 01 already wrote (per
# `149-RESEARCH.md` §R9e option 1 -- arm the gate early, extend the list in
# plan 08). There is no pre-authored-RED state to distinguish here.
# ---------------------------------------------------------------------------


def test_armed_against_the_real_149_artifacts():
    """Invoked with no argv and no seam (the real defaults), the gate MUST
    exit 0 with a `PASS:` line naming the real `149-PAGE-SIZE.md` artifact.
    This is the literal mechanical discharge of "armed against the real
    files" for this plan's scope."""
    result = _run_scanner(targets=None, argv=None)
    assert result.returncode == 0, (
        f"gate exited {result.returncode} against the real default target -- "
        f"expected PASS + exit 0.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )
    assert "149-PAGE-SIZE.md" in result.stdout, (
        f"Expected '149-PAGE-SIZE.md' named in the PASS: message but got:\n"
        f"{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 10 (introspection): default targets resolve inside THIS phase directory
# ---------------------------------------------------------------------------


def test_default_targets_resolve_inside_this_phase_directory():
    """The gate's own `_DEFAULT_TARGETS` must resolve strictly INSIDE this
    phase's own directory (`_HERE`, computed fresh from `__file__`), never a
    sibling phase directory named by a string constant."""
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
    `149-` prefix. A copy carrying a stale sibling-phase prefix goes red
    immediately here."""
    module = _import_scanner_module()
    assert module._DEFAULT_TARGETS, "_DEFAULT_TARGETS must not be empty"
    for entry in module._DEFAULT_TARGETS:
        basename = os.path.basename(entry)
        assert basename.startswith("149-"), (
            f"_DEFAULT_TARGETS basename {basename!r} does not carry this "
            "phase's own '149-' prefix -- this is the exact stale-name "
            "defect this test exists to catch"
        )


# ---------------------------------------------------------------------------
# Leg 12 (introspection): every default target has a caveat-rule entry
# ---------------------------------------------------------------------------


def test_every_default_targets_basename_has_a_caveat_rule_entry():
    """Every `_DEFAULT_TARGETS` basename must have an explicit `_CAVEAT_RULES`
    entry. The gate's `_required_caveats_for()` fails closed on an unknown
    basename (leg 13), so a missing entry would not weaken the gate -- but it
    would silently hold a file to a rule its author never chose."""
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
    future rename of a real artifact disable its caveat check silently, with
    the gate still reporting PASS. Also asserts the full set is non-empty and
    is derived from the pattern table rather than restated."""
    module = _import_scanner_module()
    assert module._ALL_CAVEAT_LABELS, "_ALL_CAVEAT_LABELS must not be empty"
    assert module._ALL_CAVEAT_LABELS == frozenset(
        label for label, _prose, _pattern in module.REQUIRED_CAVEAT_PATTERNS
    ), (
        "_ALL_CAVEAT_LABELS must be derived from REQUIRED_CAVEAT_PATTERNS, "
        "not restated"
    )
    for unknown in (
        "149-NO-SUCH-ARTIFACT.md",
        "clean_control.md",
        "149-PAGE-SIZE.md.bak",
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
            "full caveat set -- a renamed real artifact could then pass "
            "with no caveat at all"
        )


# ---------------------------------------------------------------------------
# Leg 14 (behavioural): the caveat-exempt basename passes with NO caveat
# ---------------------------------------------------------------------------


def test_caveat_exempt_basename_passes_without_either_caveat(tmp_path):
    """The gate's `_CAVEAT_RULES` exempts `149-CLAIM-GATE-TRANSCRIPTS.md`,
    mirroring the donor's own D-11 exemption for `146-CORRECTIONS.md`: it is
    a committed evidence register of gate runs, not a claim about the change,
    and must not be failed by a rule written for a document that makes
    claims. This leg proves that exemption BEHAVIOURALLY -- a document
    written under that exact basename, carrying NO required caveat and no
    forbidden phrase, exits 0. Introspecting `_CAVEAT_RULES` (leg 12's
    sibling check) would only prove the map's contents, not that `main()`
    consumes it. The file this leg writes is a throwaway `tmp_path` fixture,
    never the real committed transcript."""
    doc = tmp_path / "149-CLAIM-GATE-TRANSCRIPTS.md"
    doc.write_text(
        "# Behavioural fixture for the exempt basename (not the real transcript)\n"
        "\n"
        "This document deliberately carries no required caveat: an evidence\n"
        "register of gate runs is not itself a claim about the change, so it\n"
        "is not held to the rule that governs claim-making documents.\n",
        encoding="utf-8",
    )
    assert _CAVEAT_NEEDLE not in doc.read_text(encoding="utf-8").lower(), (
        "this leg's document must carry NO caveat, but the caveat phrase is "
        "present -- it would then pass for the wrong reason"
    )
    result = _run_scanner(targets=str(doc))
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on the caveat-exempt basename with "
        f"no caveat present -- the exemption is not being consumed by "
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
    phrase alone -- so the exemption is caveat-only and is not a blanket skip
    of the file. Either leg alone would be insufficient: leg 14 without this
    one would be consistent with the gate skipping the exempt file entirely.

    The document is derived from the already-probed
    `planted_forbidden_claim.md` fixture with its one caveat line filtered
    out, so this leg introduces no new forbidden literal of its own."""
    source = (_HERE / "fixtures" / "planted_forbidden_claim.md").read_text(
        encoding="utf-8"
    )
    filtered = "\n".join(
        line
        for line in source.splitlines()
        if _CAVEAT_NEEDLE not in line.lower()
    )
    assert "The planted sentence:" in filtered, (
        "the plant line was filtered away along with the caveat -- the "
        "fixture's layout changed and this leg would test nothing"
    )
    assert _CAVEAT_NEEDLE not in filtered.lower(), (
        "the caveat phrase survived filtering; this leg must present the "
        "exempt basename with NO caveat so the only possible failure is the "
        "forbidden phrase"
    )
    doc = tmp_path / "149-CLAIM-GATE-TRANSCRIPTS.md"
    doc.write_text(filtered, encoding="utf-8")
    result = _run_scanner(targets=str(doc))
    assert result.returncode != 0, (
        f"gate exited 0 on the caveat-exempt basename carrying a forbidden "
        f"phrase -- the exemption has become a blanket skip.\n"
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


# ---------------------------------------------------------------------------
# Leg 16: X-2 forward direction -- the required phrase alone does not trip
# the narrowed proven-unqualified pattern
# ---------------------------------------------------------------------------


def test_the_required_phrase_alone_does_not_trip_the_narrowed_proven_pattern(
    tmp_path,
):
    """A document whose ONLY occurrence of the word "proven" is inside the
    mandated PGSZ-05 compound must pass clean -- this is the whole point of
    the negative lookbehind (`149-RESEARCH.md` §X-2). If this leg failed, the
    narrowing would be insufficient and the gate would still be unsatisfiable
    by the phrase it is required to demand."""
    doc = tmp_path / "x2-forward.md"
    doc.write_text(
        "This document makes exactly one claim about the page-size seam: it "
        "is software-proven and unvalidated on silicon, and nothing else "
        "here uses that word.\n",
        encoding="utf-8",
    )
    result = _run_scanner(targets=str(doc))
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on a document whose only 'proven' "
        f"occurrence is the mandated compound -- the X-2 narrowing is "
        f"insufficient.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
    assert "proven-unqualified" not in result.stdout, (
        f"The mandated compound must not itself be reported as a violation:"
        f"\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 17: X-2 negative control -- an unqualified "proven" still trips
# ---------------------------------------------------------------------------


def test_an_unqualified_proven_still_trips_the_narrowed_pattern(tmp_path):
    """The negative control that makes the X-2 narrowing honest rather than a
    quiet loosening of the whole table: a bare "proven", not preceded by
    "software-", MUST still fail the gate. This is the leg that must be SEEN
    to fail, not merely asserted to -- a lookbehind that silently swallowed
    every spelling of the word would pass this document too, and only a real
    subprocess run against real text can catch that."""
    doc = tmp_path / "x2-negative-control.md"
    doc.write_text("The write path is proven, full stop.\n", encoding="utf-8")
    result = _run_scanner(targets=str(doc))
    assert result.returncode != 0, (
        f"gate exited 0 on a bare, unqualified 'proven' -- the narrowing has "
        f"gone too far and the X-2 negative control has failed to fire.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "forbidden phrase match [proven-unqualified]" in result.stdout, (
        f"Expected the proven-unqualified label in output but got:\n"
        f"{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 18: the transcript file is not a gate target
# ---------------------------------------------------------------------------


def test_the_transcript_file_is_not_a_gate_target():
    """`149-CLAIM-GATE-TRANSCRIPTS.md` must be absent from `_DEFAULT_TARGETS`
    -- it contains planted overclaim text by construction (the RED blocks
    quote forbidden phrases as evidence), so adding it to the target list
    would make the gate permanently RED against its own evidence."""
    module = _import_scanner_module()
    basenames = {os.path.basename(e) for e in module._DEFAULT_TARGETS}
    assert "149-CLAIM-GATE-TRANSCRIPTS.md" not in basenames, (
        "the transcript file must never be a gate target -- it necessarily "
        "quotes forbidden vocabulary as evidence"
    )


# ---------------------------------------------------------------------------
# Leg 19: the upstream discussion artifacts are not gate targets
# ---------------------------------------------------------------------------


def test_context_research_and_discussion_log_are_not_gate_targets():
    """`149-CONTEXT.md`, `149-RESEARCH.md` and `149-DISCUSSION-LOG.md` must
    all be absent from `_DEFAULT_TARGETS` -- each carries the forbidden
    vocabulary as discussion prose (this very research citing the words it
    forbids), so a future "just glob the phase directory" edit would sweep
    them in and make the gate permanently RED against its own planning
    record. This leg is what stops that edit from landing unnoticed."""
    module = _import_scanner_module()
    basenames = {os.path.basename(e) for e in module._DEFAULT_TARGETS}
    for excluded in (
        "149-CONTEXT.md",
        "149-RESEARCH.md",
        "149-DISCUSSION-LOG.md",
    ):
        assert excluded not in basenames, (
            f"{excluded} must not be a gate target -- it carries the "
            "forbidden vocabulary as discussion prose"
        )


# ---------------------------------------------------------------------------
# Leg 20: every forbidden pattern this phase added or modified has its own
# isolated planted fixture
# ---------------------------------------------------------------------------


def test_every_forbidden_pattern_has_a_planted_fixture():
    """Every label this phase ADDED or MODIFIED to `FORBIDDEN_PATTERNS` must
    have its own committed fixture that trips exactly that label and no
    other -- leg isolation, so a plant's failure is attributable to its own
    rule and not to a neighbour's. Non-vacuity: the fixture set must be
    non-empty before any per-label assertion runs."""
    module = _import_scanner_module()
    fixtures_dir = _HERE / "fixtures"
    fixture_files = sorted(p.name for p in fixtures_dir.iterdir() if p.is_file())
    assert fixture_files, "fixtures/ must not be empty"

    label_to_fixture = {
        "proven-unqualified": "planted_proven_unqualified.md",
        "page-size-proven": "planted_page_size_proven.md",
        "graduation": "planted_graduation.md",
        "support-status-change": "planted_support_status_change.md",
        "issue-closed": "planted_issue_closed.md",
        "at28c256-fixed": "planted_at28c256_fixed.md",
    }
    all_labels = {label for label, _pattern in module.FORBIDDEN_PATTERNS}
    for label, fixture_name in label_to_fixture.items():
        assert label in all_labels, (
            f"{label!r} is not in FORBIDDEN_PATTERNS -- this test's own "
            "mapping is stale"
        )
        assert fixture_name in fixture_files, (
            f"expected fixture {fixture_name!r} for label {label!r} is "
            f"missing from fixtures/: {fixture_files}"
        )
        result = _run_scanner(targets=f"fixtures/{fixture_name}")
        assert result.returncode != 0, (
            f"gate exited 0 on {fixture_name}, expected to trip {label!r}.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
        assert f"forbidden phrase match [{label}]" in result.stdout, (
            f"expected {fixture_name} to trip exactly [{label}] but got:\n"
            f"{result.stdout}"
        )
        other_labels = all_labels - {label}
        for other in other_labels:
            assert f"forbidden phrase match [{other}]" not in result.stdout, (
                f"{fixture_name} unexpectedly also tripped [{other}] -- leg "
                f"isolation is broken:\n{result.stdout}"
            )
        assert "missing required caveat" not in result.stdout, (
            f"{fixture_name} must fail for exactly the forbidden phrase, not "
            f"a missing caveat:\n{result.stdout}"
        )
