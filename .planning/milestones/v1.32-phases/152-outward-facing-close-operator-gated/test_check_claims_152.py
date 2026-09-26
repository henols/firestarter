"""Tests for 152-check-claims.py (Phase 152 Plan 02, OUT-05's paired suite).

This is the MANDATORY anti-hollow pairing for the outward-facing close's claim
gate: a checker with no negative-fixture test is exactly this project's v1.12
hollow-GATE-03 failure mode -- a declared-empty detector that could never
fail, because nothing concrete was ever asserted against it. Every
planted-violation leg below invokes the gate as a real subprocess against a
committed fixture file through the `FIRESTARTER_CLAIMSCAN_TARGETS_152` env
seam -- never an in-process import -- so a passing suite proves the *gate*
(not the test) fails the build on a real violation.

**Analog and deviations.** Source: the phase 149 donor's own paired suite for
`149-check-claims.py`, read in full -- the subprocess runner, the by-path
importer and the PASS-line helper are transcribed unchanged in mechanism
(renamed to this phase's own env seam and module path). The donor's 20 legs
are transcribed here, renamed, with these substantive adaptations:

  * Leg 9 (`test_armed_against_the_real_152_artifacts`) is written
    self-maintaining: it asserts `_DEFAULT_TARGETS` is non-empty, every entry
    exists on disk, every entry's dirname is `_HERE`, and every basename
    starts with `152-`, plus the no-argv no-seam subprocess run exits 0.
    Written this way it stays true as later plans extend the list, and it is
    observable GREEN today because Plan 152-01 wrote `152-CLAIM-CLASSES.md`.
  * Legs 2-4 (planted-overclaim / missing-caveat / bare-claim-word) point at
    this phase's own committed fixtures rather than the donor's, since this
    phase did not re-author single-purpose analogs of every donor fixture:
    leg 2 uses `planted_at28c256_fixed.md` (`at28c256-fixed`), leg 3 uses
    `planted_missing_caveat_software_proven.md` (`software-proven-unvalidated`),
    leg 4 uses `planted_proven_unqualified.md` (`proven-unqualified`) --
    unchanged from the donor.
  * Legs 14/15 (the caveat-exempt basename pair) exercise
    `152-CLAIM-GATE-TRANSCRIPTS.md` -- the gate's own `_CAVEAT_RULES` maps
    that basename to the empty set, mirroring the donor's own exemption for
    its own transcript file. The files these two legs write are throwaway
    `tmp_path` fixtures carrying that basename; they are never the real
    committed transcript.
  * Leg 19 (`test_context_research_and_discussion_log_are_not_gate_targets`)
    is extended to also cover `152-VALIDATION.md` and `152-PATTERNS.md` --
    both exist on disk today and both carry the forbidden vocabulary as
    discussion prose.
  * Leg 20 (the meta leg) maps only the THREE labels this phase ADDED or
    MODIFIED: `sdp-relock-as-shipped`, `sdp-relock-flag-as-shipped` and
    `issue-closed` -- not the donor-carried rows, which this phase did not
    change.

Six legs are new, covering this phase's own added/modified rows and the
D-05/criterion-4 word-order requirement:

  21. `test_planted_sdp_relock_is_rejected` -- the specified planted
      violation is RED, names `sdp-relock-as-shipped`, and does NOT name
      `sdp-relock-flag-as-shipped` nor a missing caveat.
  22. `test_planted_sdp_relock_bare_flag_is_rejected` -- the bare-flag plant
      is RED and names only `sdp-relock-flag-as-shipped`.
  23. `test_withdrawal_sentence_is_permitted` -- `clean_control.md`, carrying
      the mandated withdrawal word order, exits 0.
  24. `test_issue_closed_still_fires` -- parametrised over the three
      `planted_issue_closed_*.md` fixtures; each is RED and names
      `issue-closed`.
  25. `test_gh32_closure_statement_is_permitted` -- `clean_control.md` carries
      D-05's required statement about gh#32 in the natural past-tense
      phrasing and exits 0.
  26. `test_each_required_caveat_row_fails_independently` -- parametrised over
      the three `planted_missing_caveat_*.md` fixtures; each RED, each naming
      exactly one caveat label and no forbidden phrase.

Every planted fixture's label set was probed against the gate's own
`scan_text` before being committed -- see `152-02-SUMMARY.md` for the
transcript. This discipline is not ceremonial: writing a forbidden label's
own name out in a fixture's HTML comment can itself contain a forbidden
substring, and this phase's own contract document (`152-CLAIM-CLASSES.md`)
tripped exactly that trap during Plan 152-01.

Filename note: `test_check_claims_152.py`, deliberately distinct from every
sibling phase's same-shaped suite, for the same reason the donor suite's own
filename note gives -- pytest's default `prepend` import mode collides on a
repeated basename run from `/workspaces`. The gate's own filename,
`152-check-claims.py`, is not a valid Python identifier -- harmless for
`spec_from_file_location` (the module *name* argument is arbitrary) and for
`subprocess`, and one more reason the behavioural legs stay subprocess-driven.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).parent
_SCANNER = _HERE / "152-check-claims.py"
_NOT_AUTO_GUARD = _HERE / "152-check-not-auto.py"

# The three required-caveat needles, as literal strings rather than imported
# regexes: legs 14 and 15 must build their input WITHOUT importing the gate,
# so the behavioural legs stay honestly subprocess-only.
_CAVEAT_NEEDLES = (
    "software-proven and unvalidated on silicon",
    "no at28c part was tested",
    "stays unverified in protocol-ledger",
)


def _run_scanner(targets=None, argv=None):
    """Invoke the gate as a real subprocess.

    `targets`, when not None, sets the env seam to that exact string (so the
    empty string is reachable, per leg 6) -- when None, the variable is
    removed from the child's environment entirely, reaching the gate's
    "variable absent -> use real defaults" path. The seam name is this
    phase's own; no other phase's seam is ever touched here.

    Fixture arguments are relative paths, which resolve because `cwd` is this
    phase directory.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_152"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_152", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


def _import_scanner_module():
    """Import `152-check-claims.py` by file path (never as a package) solely
    to introspect its module-level constants -- used only by legs 9-13 and
    18-19, which must inspect the real objects the running process would use
    rather than a re-derived copy. The module name argument is arbitrary,
    which is what lets a filename that is not a valid Python identifier be
    loaded at all."""
    spec = importlib.util.spec_from_file_location(
        "check_claims_152_introspect", str(_SCANNER)
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
    control's required caveats are recognised (the control carries all
    three, because a fixture basename is absent from `_CAVEAT_RULES` and
    therefore held to the fail-closed FULL caveat set)."""
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
    """`fixtures/planted_at28c256_fixed.md` MUST fail the gate, attributed to
    the `at28c256-fixed` label -- the label the probe actually returned, not
    a label this leg assumed. The fixture carries all three required
    caveats, so this is a single-reason failure: a caveat bucket in the
    output would mean the fixture drifted."""
    result = _run_scanner(targets="fixtures/planted_at28c256_fixed.md")
    assert result.returncode != 0, (
        f"gate exited 0 on a planted forbidden-phrase violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "forbidden phrase match [at28c256-fixed]" in result.stdout, (
        "Expected the probed at28c256-fixed label in output but got:\n"
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
    """`fixtures/planted_missing_caveat_software_proven.md` MUST fail the
    gate, naming the caveat bucket the gate actually emits and the one
    required label. The bucket string asserted here is read from the gate's
    own source."""
    result = _run_scanner(
        targets="fixtures/planted_missing_caveat_software_proven.md"
    )
    assert result.returncode != 0, (
        f"gate exited 0 on a planted missing-caveat violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout
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
# Leg 4: planted bare claim word
# ---------------------------------------------------------------------------


def test_planted_bare_claim_word_flips_the_gate_to_failure():
    """`fixtures/planted_proven_unqualified.md` MUST fail the gate, naming the
    `proven-unqualified` label via its narrowed pattern -- the plant carries a
    bare `bench-proven` compound, which is NOT the `software-proven` compound
    the lookbehind permits. This gate has no relational rule, and D-14
    forbids adding one."""
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
        f"the fixture lost a caveat:\n{result.stdout}"
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
    """The env seam explicitly set to the empty string MUST resolve to zero
    targets and exit non-zero, and MUST NOT silently fall back to the real
    defaults. This gate deliberately has NO unarmed/exit-0-on-nothing-scanned
    branch, and the second assertion pins that absence."""
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
    """Positional argv must win over the env seam. The seam is pointed at a
    plant while argv passes a clean control -- the run must succeed, pinning
    the documented precedence so a future edit cannot silently invert it."""
    result = _run_scanner(
        targets="fixtures/planted_at28c256_fixed.md",
        argv=["fixtures/clean_control.md"],
    )
    assert result.returncode == 0, (
        f"gate exited {result.returncode} even though argv should have "
        f"overridden the env seam.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
    assert "planted_at28c256_fixed.md" not in result.stdout, (
        "The seam's plant must not have been scanned at all when argv is "
        f"supplied:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 9: armed against the real 152 artifacts
#
# Written self-maintaining rather than a pre-authored pin against a single
# named file: this stays true as later plans extend `_DEFAULT_TARGETS`, and
# it is observable GREEN today because Plan 152-01 wrote
# `152-CLAIM-CLASSES.md`, so there is no pre-authored-RED state here.
# ---------------------------------------------------------------------------


def test_armed_against_the_real_152_artifacts():
    """`_DEFAULT_TARGETS` must be non-empty, every entry must exist on disk,
    every entry's dirname must be `_HERE`, and every basename must start with
    `152-`. Invoked with no argv and no seam (the real defaults), the gate
    MUST also exit 0 with a `PASS:` line.

    Plan 152-13 strengthens this leg with a literal MEMBERSHIP assertion: the
    self-maintaining checks above would pass just as happily on a shorter
    list (e.g. if a later edit silently dropped one of the real artifacts),
    so this leg also names the expected basenames literally and asserts
    every one is present. A membership check is what catches a silent
    omission that the self-maintaining checks cannot. Plan 152-19 extends
    the expected set from seven to eight basenames, adding `152-LEDGER.md`."""
    module = _import_scanner_module()
    assert module._DEFAULT_TARGETS, "_DEFAULT_TARGETS must not be empty"
    for entry in module._DEFAULT_TARGETS:
        assert os.path.isfile(entry), (
            f"_DEFAULT_TARGETS entry {entry!r} does not exist on disk"
        )
        assert os.path.dirname(entry) == str(_HERE.resolve()), (
            f"_DEFAULT_TARGETS entry {entry!r} does not resolve inside this "
            "phase's own directory"
        )
        assert os.path.basename(entry).startswith("152-"), (
            f"_DEFAULT_TARGETS entry {entry!r} does not carry this phase's "
            "own '152-' prefix"
        )

    expected_basenames = {
        "152-CLAIM-CLASSES.md",
        "152-GH12-COMMENT.md",
        "152-GH21-COMMENT.md",
        "152-GH11-COMMENT.md",
        "152-RELEASE-NOTES-app.md",
        "152-RELEASE-NOTES-fw.md",
        "152-MERGE-RECORD.md",
        "152-LEDGER.md",
    }
    actual_basenames = {os.path.basename(e) for e in module._DEFAULT_TARGETS}
    assert expected_basenames <= actual_basenames, (
        "one or more of the eight expected outward artifacts is missing from "
        f"_DEFAULT_TARGETS: {expected_basenames - actual_basenames}"
    )
    # Plan 152-20 extended the list over every plan SUMMARY through 152-19.
    expected_summaries = {f"152-{n:02d}-SUMMARY.md" for n in range(1, 20)}
    actual_summaries = {b for b in actual_basenames if b.endswith("-SUMMARY.md")}
    assert actual_summaries == expected_summaries, (
        "the SUMMARY members of _DEFAULT_TARGETS must be exactly 152-01 "
        "through 152-19.\n"
        f"missing: {sorted(expected_summaries - actual_summaries)}\n"
        f"unexpected: {sorted(actual_summaries - expected_summaries)}"
    )

    # ORDERING TRAP -- do NOT "fix" this by adding a twentieth SUMMARY entry.
    # `152-20-SUMMARY.md` does not exist while Plan 152-20 runs, so adding it
    # would trip the gate's fail-closed missing-target branch and drive every
    # remaining run of this phase non-zero. It is scanned via positional argv
    # after 152-20's SUMMARY is written; see the transcript's "Final target
    # list" section for the exact command.
    assert "152-20-SUMMARY.md" not in actual_basenames, (
        "152-20-SUMMARY.md must NOT be a _DEFAULT_TARGETS member -- it does "
        "not exist while Plan 152-20 runs and the fail-closed missing-target "
        "branch would make the gate non-zero for the rest of the phase. It is "
        "scanned via positional argv instead."
    )

    assert len(module._DEFAULT_TARGETS) == 27, (
        "expected exactly 27 _DEFAULT_TARGETS entries as of Plan 152-20 "
        "(eight claim-bearing artifacts plus nineteen SUMMARY files), "
        f"got {len(module._DEFAULT_TARGETS)}: {module._DEFAULT_TARGETS}"
    )

    result = _run_scanner(targets=None, argv=None)
    assert result.returncode == 0, (
        f"gate exited {result.returncode} against the real default targets -- "
        f"expected PASS + exit 0.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout, (
        f"Expected 'PASS:' in output but got:\n{result.stdout}"
    )
    for basename in expected_basenames:
        assert basename in result.stdout, (
            f"expected {basename!r} named in the PASS: line but got:\n"
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
    `152-` prefix. A copy carrying a stale sibling-phase prefix goes red
    immediately here."""
    module = _import_scanner_module()
    assert module._DEFAULT_TARGETS, "_DEFAULT_TARGETS must not be empty"
    for entry in module._DEFAULT_TARGETS:
        basename = os.path.basename(entry)
        assert basename.startswith("152-"), (
            f"_DEFAULT_TARGETS basename {basename!r} does not carry this "
            "phase's own '152-' prefix -- this is the exact stale-name "
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
        "152-NO-SUCH-ARTIFACT.md",
        "clean_control.md",
        "152-CLAIM-CLASSES.md.bak",
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
    """The gate's `_CAVEAT_RULES` exempts `152-CLAIM-GATE-TRANSCRIPTS.md`,
    mirroring the donor's own exemption for its own transcript file: it is a
    committed evidence register of gate runs, not a claim about the change,
    and must not be failed by a rule written for a document that makes
    claims. This leg proves that exemption BEHAVIOURALLY -- a document
    written under that exact basename, carrying NO required caveat and no
    forbidden phrase, exits 0. Introspecting `_CAVEAT_RULES` (leg 12's
    sibling check) would only prove the map's contents, not that `main()`
    consumes it. The file this leg writes is a throwaway `tmp_path` fixture,
    never the real committed transcript."""
    doc = tmp_path / "152-CLAIM-GATE-TRANSCRIPTS.md"
    doc.write_text(
        "# Behavioural fixture for the exempt basename (not the real transcript)\n"
        "\n"
        "This document deliberately carries no required caveat: an evidence\n"
        "register of gate runs is not itself a claim about the change, so it\n"
        "is not held to the rule that governs claim-making documents.\n",
        encoding="utf-8",
    )
    text = doc.read_text(encoding="utf-8").lower()
    for needle in _CAVEAT_NEEDLES:
        assert needle not in text, (
            "this leg's document must carry NO caveat, but a caveat phrase "
            "is present -- it would then pass for the wrong reason"
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
    forbidden phrase and no caveat, must exit non-zero on the forbidden
    phrase alone -- so the exemption is caveat-only and is not a blanket skip
    of the file. Either leg alone would be insufficient: leg 14 without this
    one would be consistent with the gate skipping the exempt file entirely.

    The document is derived from the already-probed
    `planted_at28c256_fixed.md` fixture with its three caveat lines filtered
    out, so this leg introduces no new forbidden literal of its own."""
    source = (_HERE / "fixtures" / "planted_at28c256_fixed.md").read_text(
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
            "a caveat phrase survived filtering; this leg must present the "
            "exempt basename with NO caveat so the only possible failure is "
            "the forbidden phrase"
        )
    doc = tmp_path / "152-CLAIM-GATE-TRANSCRIPTS.md"
    doc.write_text(filtered, encoding="utf-8")
    result = _run_scanner(targets=str(doc))
    assert result.returncode != 0, (
        f"gate exited 0 on the caveat-exempt basename carrying a forbidden "
        f"phrase -- the exemption has become a blanket skip.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "forbidden phrase match [at28c256-fixed]" in result.stdout, (
        f"Expected the probed at28c256-fixed label in output but got:\n"
        f"{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        "The exempt basename must still not be held to any caveat; only the "
        f"forbidden phrase may be reported:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 16: the required phrase alone does not trip the narrowed
# proven-unqualified pattern
# ---------------------------------------------------------------------------


def test_the_required_phrase_alone_does_not_trip_the_narrowed_proven_pattern(
    tmp_path,
):
    """A document whose ONLY occurrence of the word "proven" is inside the
    mandated `software-proven-unvalidated` compound must pass clean -- this is
    the whole point of the negative lookbehind kept verbatim from the donor.
    If this leg failed, the narrowing would be insufficient and the gate
    would still be unsatisfiable by the phrase it is required to demand."""
    doc = tmp_path / "narrowing-forward.md"
    doc.write_text(
        "This document makes exactly one claim about phase 152's write-path "
        "close-out: it ships software-proven and unvalidated on silicon, "
        "and nothing else here uses that word.\n"
        "\n"
        "No AT28C part was tested at any point in v1.32.\n"
        "\n"
        "Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.\n",
        encoding="utf-8",
    )
    result = _run_scanner(targets=str(doc))
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on a document whose only 'proven' "
        f"occurrence is the mandated compound -- the narrowing is "
        f"insufficient.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
    assert "proven-unqualified" not in result.stdout, (
        f"The mandated compound must not itself be reported as a violation:"
        f"\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 17: negative control -- an unqualified "proven" still trips
# ---------------------------------------------------------------------------


def test_an_unqualified_proven_still_trips_the_narrowed_pattern(tmp_path):
    """The negative control that makes the narrowing honest rather than a
    quiet loosening of the whole table: a bare "proven", not preceded by
    "software-", MUST still fail the gate. This is the leg that must be SEEN
    to fail, not merely asserted to -- a lookbehind that silently swallowed
    every spelling of the word would pass this document too, and only a real
    subprocess run against real text can catch that."""
    doc = tmp_path / "narrowing-negative-control.md"
    doc.write_text("The write path is proven, full stop.\n", encoding="utf-8")
    result = _run_scanner(targets=str(doc))
    assert result.returncode != 0, (
        f"gate exited 0 on a bare, unqualified 'proven' -- the narrowing has "
        f"gone too far and the negative control has failed to fire.\n"
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
    """`152-CLAIM-GATE-TRANSCRIPTS.md` must be absent from `_DEFAULT_TARGETS`
    -- it contains planted overclaim text by construction (the RED blocks
    quote forbidden phrases as evidence), so adding it to the target list
    would make the gate permanently fail against its own evidence."""
    module = _import_scanner_module()
    basenames = {os.path.basename(e) for e in module._DEFAULT_TARGETS}
    assert "152-CLAIM-GATE-TRANSCRIPTS.md" not in basenames, (
        "the transcript file must never be a gate target -- it necessarily "
        "quotes forbidden vocabulary as evidence"
    )


# ---------------------------------------------------------------------------
# Leg 19: the upstream discussion artifacts are not gate targets
# ---------------------------------------------------------------------------


def test_context_research_and_discussion_log_are_not_gate_targets():
    """`152-CONTEXT.md`, `152-RESEARCH.md`, `152-DISCUSSION-LOG.md`,
    `152-VALIDATION.md` and `152-PATTERNS.md` must all be absent from
    `_DEFAULT_TARGETS` -- each carries the forbidden vocabulary as discussion
    prose (this very research citing the words it forbids), so a future
    "just glob the phase directory" edit would sweep them in and make the
    gate permanently fail against its own planning record. This leg is what
    stops that edit from landing unnoticed."""
    module = _import_scanner_module()
    basenames = {os.path.basename(e) for e in module._DEFAULT_TARGETS}
    for excluded in (
        "152-CONTEXT.md",
        "152-RESEARCH.md",
        "152-DISCUSSION-LOG.md",
        "152-VALIDATION.md",
        "152-PATTERNS.md",
    ):
        assert excluded not in basenames, (
            f"{excluded} must not be a gate target -- it carries the "
            "forbidden vocabulary as discussion prose"
        )


# ---------------------------------------------------------------------------
# Leg 20: every forbidden pattern this phase ADDED or MODIFIED has its own
# isolated planted fixture
# ---------------------------------------------------------------------------


def test_every_forbidden_pattern_has_a_planted_fixture():
    """Every label this phase ADDED or MODIFIED to `FORBIDDEN_PATTERNS` --
    `sdp-relock-as-shipped`, `sdp-relock-flag-as-shipped` and `issue-closed`
    -- must have its own committed fixture that trips exactly that label and
    no other -- leg isolation, so a plant's failure is attributable to its
    own rule and not to a neighbour's. Non-vacuity: the fixture set must be
    non-empty before any per-label assertion runs."""
    module = _import_scanner_module()
    fixtures_dir = _HERE / "fixtures"
    fixture_files = sorted(p.name for p in fixtures_dir.iterdir() if p.is_file())
    assert fixture_files, "fixtures/ must not be empty"

    label_to_fixture = {
        "sdp-relock-as-shipped": "planted_sdp_relock_as_shipped.md",
        "sdp-relock-flag-as-shipped": "planted_sdp_relock_bare_flag.md",
        "issue-closed": "planted_issue_closed_gh21.md",
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


# ---------------------------------------------------------------------------
# Leg 21 (NEW): the specified planted violation is rejected
# ---------------------------------------------------------------------------


def test_planted_sdp_relock_is_rejected():
    """`fixtures/planted_sdp_relock_as_shipped.md` (ROADMAP.md's
    pre-amendment criterion-1 wording, taken verbatim) MUST fail the gate,
    naming ONLY `sdp-relock-as-shipped` -- not its bare-flag companion (leg
    isolation via the fixed-width lookbehind) and not a missing caveat."""
    result = _run_scanner(targets="fixtures/planted_sdp_relock_as_shipped.md")
    assert result.returncode != 0, (
        f"gate exited 0 on the specified planted violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "forbidden phrase match [sdp-relock-as-shipped]" in result.stdout, (
        f"Expected the sdp-relock-as-shipped label in output but got:\n"
        f"{result.stdout}"
    )
    assert "forbidden phrase match [sdp-relock-flag-as-shipped]" not in result.stdout, (
        f"leg isolation broken -- the bare-flag companion also fired:\n"
        f"{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        f"This plant must fail for exactly ONE reason:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 22 (NEW): the bare-flag companion is rejected
# ---------------------------------------------------------------------------


def test_planted_sdp_relock_bare_flag_is_rejected():
    """`fixtures/planted_sdp_relock_bare_flag.md` MUST fail the gate, naming
    ONLY `sdp-relock-flag-as-shipped` -- proving leg isolation from the row
    above in the other direction."""
    result = _run_scanner(targets="fixtures/planted_sdp_relock_bare_flag.md")
    assert result.returncode != 0, (
        f"gate exited 0 on the bare-flag planted violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "forbidden phrase match [sdp-relock-flag-as-shipped]" in result.stdout, (
        f"Expected the sdp-relock-flag-as-shipped label in output but got:\n"
        f"{result.stdout}"
    )
    assert "forbidden phrase match [sdp-relock-as-shipped]" not in result.stdout, (
        f"leg isolation broken -- the command-first row also fired:\n"
        f"{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        f"This plant must fail for exactly ONE reason:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 23 (NEW): the mandated withdrawal word order survives the class
# ---------------------------------------------------------------------------


def test_withdrawal_sentence_is_permitted():
    """`fixtures/clean_control.md` carries the mandated withdrawal word order
    (`write --sdp-relock` immediately followed by a withdrawal predicate) and
    MUST exit 0 -- this is the leg that proves criterion 4's mandated
    sentence survives criterion 5's forbidden class."""
    result = _run_scanner(targets="fixtures/clean_control.md")
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on the mandated withdrawal "
        f"sentence -- criterion 4's own required wording would be "
        f"unsatisfiable.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout


# ---------------------------------------------------------------------------
# Leg 24 (NEW): the narrowed issue-closed row still fires on gh#21/#11/#12
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture_name,issue",
    [
        ("planted_issue_closed_gh21.md", "gh#21"),
        ("planted_issue_closed_gh11.md", "gh#11"),
        ("planted_issue_closed_gh12.md", "gh#12"),
    ],
)
def test_issue_closed_still_fires(fixture_name, issue):
    """The narrowed `issue-closed` row (with `32` dropped from the
    alternation) MUST still fire on gh#21, gh#11 and gh#12 -- the narrowing to
    D-05's true claim class is not a general loosening of the row."""
    result = _run_scanner(targets=f"fixtures/{fixture_name}")
    assert result.returncode != 0, (
        f"gate exited 0 on {fixture_name}, expected to trip issue-closed "
        f"for {issue}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "forbidden phrase match [issue-closed]" in result.stdout, (
        f"Expected the issue-closed label in output for {issue} but got:\n"
        f"{result.stdout}"
    )
    assert "missing required caveat" not in result.stdout, (
        f"{fixture_name} must fail for exactly the forbidden phrase:\n"
        f"{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 25 (NEW): D-05's gh#32 closure statement survives the narrowed row
# ---------------------------------------------------------------------------


def test_gh32_closure_statement_is_permitted():
    """`fixtures/clean_control.md` carries D-05's required statement that
    gh#32 was closed, in the natural past-tense phrasing, and MUST exit 0 --
    proving the narrowed `issue-closed` row (with `32` dropped) permits the
    one true measured fact this phase must state."""
    result = _run_scanner(targets="fixtures/clean_control.md")
    assert result.returncode == 0, (
        f"gate exited {result.returncode} on D-05's mandated gh#32 closure "
        f"statement -- the narrowed row is insufficiently narrow.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS:" in result.stdout
    source = (_HERE / "fixtures" / "clean_control.md").read_text(encoding="utf-8")
    assert "gh#32" in source and "closed" in source.lower(), (
        "the fixture this leg relies on no longer carries the gh#32 closure "
        f"statement -- this leg would test nothing:\n{source}"
    )


# ---------------------------------------------------------------------------
# Leg 26 (NEW): each required-caveat row fails independently
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture_name,label",
    [
        (
            "planted_missing_caveat_software_proven.md",
            "software-proven-unvalidated",
        ),
        ("planted_missing_caveat_no_at28c.md", "no-at28c-part-tested"),
        ("planted_missing_caveat_unverified.md", "zero-d-stays-unverified"),
    ],
)
def test_each_required_caveat_row_fails_independently(fixture_name, label):
    """Each of the three `planted_missing_caveat_*.md` fixtures MUST fail the
    gate, naming exactly ITS OWN caveat label and no forbidden phrase --
    proving the three required-caveat rows are independently enforced rather
    than one combined row."""
    result = _run_scanner(targets=f"fixtures/{fixture_name}")
    assert result.returncode != 0, (
        f"gate exited 0 on {fixture_name}, expected to trip a missing "
        f"caveat for {label!r}.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert f"missing required caveat [{label}]" in result.stdout, (
        f"Expected the {label!r} caveat label in output but got:\n"
        f"{result.stdout}"
    )
    other_labels = {
        "software-proven-unvalidated",
        "no-at28c-part-tested",
        "zero-d-stays-unverified",
    } - {label}
    for other in other_labels:
        assert f"missing required caveat [{other}]" not in result.stdout, (
            f"{fixture_name} unexpectedly also names {other!r} -- leg "
            f"isolation is broken:\n{result.stdout}"
        )
    assert "forbidden phrase match" not in result.stdout, (
        f"{fixture_name} must fail for exactly the missing caveat, not a "
        f"forbidden phrase:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Leg 27 (NEW, Plan 152-13): the verified-on-silicon row's word-boundary fix
#
# The donor's `verified-on-silicon` row had no leading word boundary, so it
# false-positived on the NON-claim "UNVERIFIED on silicon" -- reproduced
# empirically in Plan 152-13 and recorded in
# `152-CLAIM-GATE-TRANSCRIPTS.md`. Nothing shipped today hits this (the
# three canonical caveats all say "stays UNVERIFIED in PROTOCOL-LEDGER", not
# "...on silicon"), but any future outward text stating the non-claim in the
# most natural English would have tripped a forbidden-phrase failure for
# saying the OPPOSITE of the forbidden claim. Both directions are asserted
# in one leg so the fix cannot become a hole: permitting the non-claim
# without still rejecting the real claim would be a silent weakening of the
# whole row.
# ---------------------------------------------------------------------------


def test_verified_on_silicon_permits_unverified_but_still_rejects_verified(
    tmp_path,
):
    """The non-claim "UNVERIFIED on silicon" MUST be permitted (exit 0), and
    the actual forbidden claim "verified on silicon" MUST still be rejected
    (exit non-zero, naming `verified-on-silicon`) -- both against real
    subprocess invocations of the real gate, never asserted only against the
    compiled pattern in isolation."""
    allowed = tmp_path / "unverified-non-claim.md"
    allowed.write_text(
        "Protocol `0x0D` remains UNVERIFIED on silicon.\n"
        "\n"
        "This ships software-proven and unvalidated on silicon. No AT28C "
        "part was tested at any point in v1.32. Protocol `0x0D` stays "
        "UNVERIFIED in PROTOCOL-LEDGER.\n",
        encoding="utf-8",
    )
    allowed_result = _run_scanner(targets=str(allowed))
    assert allowed_result.returncode == 0, (
        f"gate exited {allowed_result.returncode} on the UNVERIFIED "
        f"non-claim -- the word-boundary fix is insufficient or absent.\n"
        f"stdout:\n{allowed_result.stdout}\nstderr:\n{allowed_result.stderr}"
    )
    assert "verified-on-silicon" not in allowed_result.stdout, (
        "the UNVERIFIED non-claim must not trip verified-on-silicon:\n"
        f"{allowed_result.stdout}"
    )

    rejected = tmp_path / "verified-real-claim.md"
    rejected.write_text(
        "Protocol `0x0D` was verified on silicon during this milestone.\n"
        "\n"
        "This ships software-proven and unvalidated on silicon. No AT28C "
        "part was tested at any point in v1.32. Protocol `0x0D` stays "
        "UNVERIFIED in PROTOCOL-LEDGER.\n",
        encoding="utf-8",
    )
    rejected_result = _run_scanner(targets=str(rejected))
    assert rejected_result.returncode != 0, (
        f"gate exited 0 on the real 'verified on silicon' claim -- the "
        f"word-boundary fix went too far and disarmed the row.\n"
        f"stdout:\n{rejected_result.stdout}\nstderr:\n{rejected_result.stderr}"
    )
    assert "forbidden phrase match [verified-on-silicon]" in rejected_result.stdout, (
        f"Expected the verified-on-silicon label in output but got:\n"
        f"{rejected_result.stdout}"
    )


# ---------------------------------------------------------------------------
# Legs 28-30 (NEW, Plan 152-13): 152-check-not-auto.py -- the fail-closed
# configuration guard against an auto/chained run reaching a public post.
# All three legs are selectable by `-k not_auto`.
# ---------------------------------------------------------------------------


def _run_not_auto_guard(config_path=None):
    """Invoke `152-check-not-auto.py` as a real subprocess, mirroring
    `_run_scanner`'s subprocess-only discipline above -- a guard whose whole
    job is a real read of a real (or fixture) file must be proven through a
    real process invocation, never an in-process import that could diverge
    from what `python3 152-check-not-auto.py` actually does on the command
    line."""
    argv = [sys.executable, str(_NOT_AUTO_GUARD)]
    if config_path is not None:
        argv.extend(["--config", str(config_path)])
    return subprocess.run(argv, cwd=str(_HERE), capture_output=True, text=True)


def test_not_auto_guard_fails_closed_on_the_truthy_fixture():
    """`fixtures/config_auto_active.json` carries `workflow._auto_chain_active:
    true`. The guard MUST exit non-zero and its output MUST name the
    configuration key -- an auto/chained run must never read as safe."""
    result = _run_not_auto_guard(_HERE / "fixtures" / "config_auto_active.json")
    assert result.returncode != 0, (
        f"guard exited 0 against the truthy auto-active fixture -- it must "
        f"fail closed on a set flag.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "_auto_chain_active" in result.stdout, (
        f"Expected the configuration key named in output but got:\n"
        f"{result.stdout}"
    )


def test_not_auto_guard_exits_zero_on_the_falsy_fixture():
    """`fixtures/config_auto_inactive.json` carries
    `workflow._auto_chain_active: false`. The guard MUST exit 0."""
    result = _run_not_auto_guard(_HERE / "fixtures" / "config_auto_inactive.json")
    assert result.returncode == 0, (
        f"guard exited {result.returncode} against the falsy auto-inactive "
        f"fixture -- expected 0.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_not_auto_guard_fails_closed_on_a_missing_config_file():
    """A `--config` path that does not exist on disk MUST make the guard
    exit non-zero -- an unknown state (here, unreadable) is not a safe
    state, mirroring the claim gate's own fail-closed-on-missing-target
    discipline."""
    result = _run_not_auto_guard("/nonexistent/config-for-152-13-tests.json")
    assert result.returncode != 0, (
        f"guard exited 0 against a nonexistent config path -- it must fail "
        f"closed on an unreadable/missing file.\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
