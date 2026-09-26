#!/usr/bin/env python3
"""Forbidden-overclaim / required-caveat scanner over Phase 146's five closing
artifacts -- `146-LEDGER.md`, `146-CORRECTIONS.md`, `146-GH15-RECONCILIATION.md`,
`146-RELEASE-NOTES-fw.md` and `146-RELEASE-NOTES-app.md`.

**This module IS the build of CLOSE-01.** CLOSE-01 asks for a machine gate armed
against the real closing files and seen to fail on a planted violation; this
script is that gate's scanning half, and the fixture suite plus the recorded
plant-and-revert transcript are its two proofs (D-12).

It is a Phase-146-scoped **sibling** of Phase 139's gate, not a copy, fork,
subclass or env-seam of it. Source: `139-check-claims.py` in
`.planning/phases/139-gh-15-correction-outward/`, read in full. The pure
mechanics adapted from it are the `_HERE` construction (`139-check-claims.py:73`),
`resolve_targets`'s argv/env/defaults precedence with its load-bearing
`is not None` env check (`:184-202`), the hoisted never-vacuous guard and the
fail-closed missing-target branch (`:266-282`), `_print_bucket`'s 20-entry
display cap (`:241-246`), and the twelve forbidden patterns plus the two
required-caveat patterns themselves (`:98-145`), transcribed unchanged.

**Four mandatory renames distinguish this sibling from its donor.** A bare copy
of the donor "works" -- it exits 0 against nothing -- which is why each of these
is recorded rather than assumed:

1. `_DEFAULT_TARGETS` is this phase's own five closing artifacts, replacing the
   donor's two Phase 139 outward artifacts. An explicit five-element list, never
   a wildcard expansion and never a recursive directory traversal: a `146-*.md`
   default set would sweep in `146-CONTEXT.md`, which carries six
   `proven-unqualified` hits of its own, and the fixtures directory, whose
   planted files exist precisely to be violations.
2. The self-check's phase-number prefix literal is `"146-"` in **both** places --
   the `startswith` call and the failure message it prints. The donor carries its
   own prefix in both (`:174`, `:177`); changing only the call leaves a message
   that names the wrong phase, which is a silent documentation defect no fixture
   leg can observe.
3. The env-override seam is `FIRESTARTER_CLAIMSCAN_TARGETS_146`. The donor's
   suffixed name is already live in Phase 139 -- the *same* milestone -- so
   reusing it would let one test suite aim two live checkers at once.
4. This docstring and its explicit non-claim are retargeted at CLOSE-01 and at
   plan `146-12`'s blocking operator wording review. The donor's own two
   non-claims (`:49-61`) name Phase 139's requirement ids, its plan `139-05`, and
   -- in the second -- assert that the donor is *not* a build of CLOSE-01. That
   second paragraph is deliberately absent here: this script **is** that build,
   and copying it would assert the opposite of this phase's deliverable.

**Per D-11 the gate arms all-or-nothing on five files, with per-file caveat
rules.** Forbidden phrases are scanned in all five. The required caveats are
demanded only where they belong -- the ledger, the reconciliation and both
release bodies -- because `146-CORRECTIONS.md` is a register of factual
corrections and must not be failed by a rule written for a release body.
Producing four of five is a hard failure with no extra code: a partial default
set lands in the fail-closed missing-target branch. `_required_caveats_for()`
returns the **full** label set for any basename absent from `_CAVEAT_RULES`, so
the rule fails closed and a future rename cannot silently disable the caveat
check for a real artifact.

**Per D-14 this scan carries no window and no exclusion mechanism.** No
proximity window, no context condition, no exclusion-by-heading quarantine, no
inline allow-marker: every match anywhere in a scanned file's text is a
violation. Phase 139 measured why -- a windowed scanner keyed on tokens absent
from this milestone's vocabulary passed a file carrying four planted overclaims.
That measurement is Phase 139's, cited here rather than re-made. The consequence
this phase's authors carry is that the pattern table is a **writing constraint**:
`\bproven\b` is forbidden unqualified and matches after a hyphen, so the closing
artifacts are written around the word rather than the pattern loosened.

Exit codes:
  0 -- every resolved target exists on disk, contains zero forbidden-phrase
       matches anywhere in its text, and carries every caveat its own per-file
       rule requires (a `PASS:` line naming every scanned file, by path relative
       to this module's own directory, is printed).
  1 -- the default-targets self-check fails (a `_DEFAULT_TARGETS` entry is not
       local to this module's own directory, or does not carry this phase's own
       "146-" prefix), OR zero targets resolved (never-vacuous), OR a resolved
       target is missing from disk (fail-closed), OR at least one
       forbidden-phrase match was found anywhere in a scanned file, OR a scanned
       file is missing a caveat its own rule requires. A bucketed `FAIL:` summary
       is printed for every failure case except the self-check, which prints its
       own `FAIL:` line per offending entry.

There is deliberately **no branch that exits 0 when nothing was scanned.** Phase
137's checker carried one (`137-…/check_permitted_claims.py:299-319`) to protect
a window before its own targets were authored; it is not ported here, because an
exit-0-on-nothing-scanned path is a green that proves nothing, and because this
gate's whole purpose is to be armed against files that must exist.

**Explicit non-claim (load-bearing):** a green run of this gate, at any point in
this phase, is compliance with the forbidden-phrase table and the per-file caveat
rules **only**. It cannot detect an implied overclaim, a misleading omission, a
wrong tone, or a true statement placed where it misleads. That is the blocking
operator wording review in plan `146-12`, which covers both release bodies and
precedes the gh#15 post. A green run of this gate must never be reported, in any
SUMMARY, citation register or Phase 146 artifact, as by itself discharging that
review or as by itself discharging CLOSE-01 -- CLOSE-01 also requires the fixture
suite and the real-file plant transcript (D-12).
"""

import os
import re
import sys

# Module-top path constant. This is the ONLY directory `_DEFAULT_TARGETS`
# below is ever built from -- never a sibling-directory string constant.
# This construction is what stops the cross-phase-copy defect where a
# checker's defaults silently resolved to a stale sibling phase directory
# and passed vacuously with nothing actually scanned.
# Source: `139-check-claims.py:73`, copied verbatim.
_HERE = os.path.dirname(os.path.abspath(__file__))

# Explicit five-element default target list -- this phase's own five closing
# artifacts (D-11). Never a wildcard expansion, never a recursive directory
# traversal of any kind: a `146-*.md` default set would sweep in
# `146-CONTEXT.md` (six `proven-unqualified` hits) and the fixtures directory.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "146-LEDGER.md"),
    os.path.join(_HERE, "146-CORRECTIONS.md"),
    os.path.join(_HERE, "146-GH15-RECONCILIATION.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-fw.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-app.md"),
]

# Env-override seam, SUFFIXED `_146`: four prior checkers in this project
# already use the bare, `_V130`- or `_V131`-suffixed names, and the
# `_V131`-suffixed one is live in Phase 139 -- this same milestone -- so a
# collision would let one phase's seam silently retarget another phase's gate,
# or let one test suite aim two live checkers at once. The suffix is the phase
# number rather than the milestone for exactly that reason.
# `os.environ.get(...)` with NO default is deliberate: it must return None
# when the variable is absent from the environment so resolve_targets()
# below can tell "absent -> use defaults" apart from "present but empty ->
# zero targets, never a silent fall-back to defaults".
FIRESTARTER_CLAIMSCAN_TARGETS_146 = os.environ.get(
    "FIRESTARTER_CLAIMSCAN_TARGETS_146"
)

# Twelve forbidden-phrase labels/patterns, all case-insensitive, carrying
# this milestone's own vocabulary. Transcribed unchanged from
# `139-check-claims.py:98-128`; D-14 forbids loosening, narrowing or
# re-deriving any of them. No proximity window and no relational rule of any
# kind gates any of these -- every match anywhere in a scanned file's text is
# a violation, full stop.
FORBIDDEN_PATTERNS = [
    ("datasheet-conformant", re.compile(r"datasheet[-\s]conformant", re.IGNORECASE)),
    ("datasheet-correct", re.compile(r"datasheet[-\s]correct", re.IGNORECASE)),
    ("algorithm-accurate", re.compile(r"algorithm[-\s]accurate", re.IGNORECASE)),
    (
        "datasheet-compound-unqualified",
        re.compile(
            r"datasheet[-\s](?:conforming|compliant|faithful|exact|perfect|true)",
            re.IGNORECASE,
        ),
    ),
    (
        "verified-on-silicon",
        re.compile(
            r"verified\s+(?:on|against)\s+(?:real\s+)?silicon", re.IGNORECASE
        ),
    ),
    ("silicon-verified", re.compile(r"silicon[-\s]verified", re.IGNORECASE)),
    ("confirmed-working", re.compile(r"confirmed\s+working", re.IGNORECASE)),
    (
        "works-on-silicon",
        re.compile(r"works?\s+on\s+(?:\w+\s+){0,2}silicon", re.IGNORECASE),
    ),
    (
        "proven-on-silicon",
        re.compile(r"proven\s+on\s+(?:\w+\s+){0,2}silicon", re.IGNORECASE),
    ),
    ("proven-unqualified", re.compile(r"\bproven\b", re.IGNORECASE)),
    ("now-works", re.compile(r"now\s+works?\b", re.IGNORECASE)),
    ("should-now-work", re.compile(r"should\s+now\s+work", re.IGNORECASE)),
]

# Two required-caveat labels, transcribed unchanged from
# `139-check-claims.py:134-145`. Unlike the donor, which required both in EVERY
# scanned file, these are consumed through the per-file `_CAVEAT_RULES` map
# below (D-11).
REQUIRED_CAVEAT_PATTERNS = [
    (
        "ceiling-voltage",
        "the ~6.25 V program-VCC ceiling",
        re.compile(r"6\.25\s*V"),
    ),
    (
        "ceiling-narrowing",
        "the silicon-margin narrowing that ceiling implies",
        re.compile(r"silicon[-\s]margin", re.IGNORECASE),
    ),
]

# The full label set, derived from the table above rather than restated, so a
# thirteenth caveat pattern cannot be added without the fail-closed default
# below picking it up.
_ALL_CAVEAT_LABELS = frozenset(
    label for label, _prose, _pattern in REQUIRED_CAVEAT_PATTERNS
)

# D-11's per-file caveat map -- the one genuinely new mechanism in this gate;
# Phase 139, 137, 123 and 122 all apply their caveats uniformly and have no
# analog. Keys are BASENAMES so the map cannot drift from `_DEFAULT_TARGETS`'
# `_HERE`-relative directory construction.
#
# `146-CORRECTIONS.md` maps to the empty set per D-11: it is a register of
# factual corrections, each row citing a false statement by `file:line` and
# giving its corrected text, and it must not be failed by a rule written for a
# release body. That is a policy decision recorded here, not an oversight --
# the fail-closed default in `_required_caveats_for()` below means an omitted
# entry would demand BOTH caveats, so silence could never produce this.
_CAVEAT_RULES = {
    "146-LEDGER.md": frozenset({"ceiling-voltage", "ceiling-narrowing"}),
    "146-GH15-RECONCILIATION.md": frozenset(
        {"ceiling-voltage", "ceiling-narrowing"}
    ),
    "146-RELEASE-NOTES-fw.md": frozenset({"ceiling-voltage", "ceiling-narrowing"}),
    "146-RELEASE-NOTES-app.md": frozenset({"ceiling-voltage", "ceiling-narrowing"}),
    "146-CORRECTIONS.md": frozenset(),
}


def _required_caveats_for(path):
    """Return the set of required-caveat labels that `path` must satisfy.

    Keyed on `os.path.basename(path)`, so an argv- or env-supplied absolute
    path resolves to the same rule as the `_DEFAULT_TARGETS` entry for the same
    artifact.

    Fails CLOSED on an unknown basename: a target with no `_CAVEAT_RULES` entry
    gets the FULL caveat set, never the empty set. An empty-set default would
    let a future edit disable the caveat check for a real closing artifact by
    renaming it -- silently, and with the gate still reporting PASS.
    """
    return _CAVEAT_RULES.get(os.path.basename(path), _ALL_CAVEAT_LABELS)


def _assert_default_targets_are_local():
    """Startup self-check -- called first thing in main(), before target
    resolution or any scanning. Fails loudly, naming the offending entry
    and the exact defect, for every `_DEFAULT_TARGETS` entry that either
    does not resolve inside this module's own directory (`_HERE`) or does
    not carry this phase's own "146-" prefix.

    This is the run-time equivalent of a paired-test suite's mandatory
    cross-phase-copy legs, moved inside the script itself so a future copy
    of this file into another phase's directory fails loudly the first
    time it is run, rather than silently scanning nothing and reporting
    success. Source: `139-check-claims.py:148-181`; the prefix literal is
    this phase's own in both the comparison and the printed message.

    Returns True iff every `_DEFAULT_TARGETS` entry passes both checks;
    every failing entry is printed (not just the first) before this
    returns False.
    """
    all_local = True
    for entry in _DEFAULT_TARGETS:
        if os.path.dirname(entry) != _HERE:
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not resolve "
                "inside this phase's own directory -- this is the exact "
                "cross-phase-copy defect this self-check exists to catch"
            )
            all_local = False
        if not os.path.basename(entry).startswith("146-"):
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                "this phase's own 146- prefix -- this is the exact "
                "stale-name defect this self-check exists to catch"
            )
            all_local = False
    return all_local


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS_146 env seam if the variable is present
    in os.environ (checked via `is not None`, not truthiness -- an
    explicitly empty value must resolve to zero targets, never a silent
    fall-back to defaults); else `_DEFAULT_TARGETS`.

    Returns (targets, used_defaults): `used_defaults` is True only when
    neither argv nor the env seam was used.
    """
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_146 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_146.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True


def scan_text(text, path, required_caveats):
    """Scan `text` (the full contents of the file at `path`) for forbidden-
    phrase matches and for the presence of the caveats `required_caveats`
    demands of this particular file.

    Carries NO proximity window and NO context condition of any kind:
    every regex match in FORBIDDEN_PATTERNS anywhere in `text` is recorded
    as a violation, full stop -- see the module docstring for the measured
    reason (Phase 139's, cited not re-made) why a proximity window is
    exactly what this milestone must not repeat. There is likewise no
    exclusion-by-heading quarantine and no inline allow-marker: D-14 forbids
    every one of them, because every exclusion is a hole.

    `path` is accepted so each call site threads the file it is scanning
    through explicitly and self-descriptively; the return shape below does
    not otherwise require it.

    `required_caveats` is the resolved per-file rule set (D-11), passed in
    rather than looked up here so the caller owns rule resolution and this
    function stays a pure scan. A label absent from `required_caveats` is not
    demanded of this file and can never appear in the returned missing set.
    The forbidden-pattern loop below is untouched by any of this -- the
    per-file rule governs caveats only.

    Returns (forbidden_hits, missing_caveat_labels):
      forbidden_hits -- list of (label, matched_text, lineno) tuples, one
        per match, 1-based lineno.
      missing_caveat_labels -- set of the labels this file was REQUIRED to
        carry whose regex did not match anywhere in `text` -- the caveats
        this file is missing, not the ones it has, and never a caveat its own
        rule did not ask for.
    """
    lines = text.splitlines()
    forbidden_hits = []
    for label, pattern in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(lines, start=1):
            for m in pattern.finditer(line):
                forbidden_hits.append((label, m.group(0), lineno))

    missing_caveat_labels = {
        label
        for label, _prose, pattern in REQUIRED_CAVEAT_PATTERNS
        if label in required_caveats and not pattern.search(text)
    }

    return forbidden_hits, missing_caveat_labels


def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")


def main(argv):
    """Entry point.

    Order of operations, from `139-check-claims.py:249-326`: the
    default-targets self-check FIRST, before any target resolution; resolve
    targets; the hoisted never-vacuous guard; partition into
    existing/missing; the fail-closed missing-target branch; then scan every
    existing target against its own per-file caveat rule and report.

    A PARTIAL default set -- one to four of the five closing artifacts
    present -- therefore lands in the fail-closed missing-target branch and is
    a hard failure, naming the absent paths, with no extra code. That is
    exactly D-11's all-or-nothing arming contract.

    Deliberately absent: any early-return branch that reports readiness when
    every default target is missing. An exit-0-on-nothing-scanned path costs
    real detection for no benefit, and this gate exists to be armed against
    files that must exist.
    """
    if not _assert_default_targets_are_local():
        return 1

    targets, _used_defaults = resolve_targets(argv)

    if not targets:
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    missing = [t for t in targets if not os.path.isfile(t)]

    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- the gate cannot "
            f"vacuously pass with a target silently skipped: {missing}"
        )
        return 1

    forbidden_violations = []
    caveat_violations = []
    scanned = []
    caveat_required_count = 0
    caveat_satisfied_count = 0
    caveat_exempt_count = 0
    caveat_prose_by_label = {
        label: prose for label, prose, _pattern in REQUIRED_CAVEAT_PATTERNS
    }

    for t in targets:
        with open(t, encoding="utf-8") as f:
            text = f.read()
        scanned.append(t)
        required = _required_caveats_for(t)
        hits, missing_labels = scan_text(text, t, required)
        for label, matched_text, lineno in hits:
            forbidden_violations.append(
                f"{t}:{lineno}: forbidden phrase match [{label}]: {matched_text!r}"
            )
        if required:
            caveat_required_count += 1
        else:
            caveat_exempt_count += 1
        if missing_labels:
            for label in sorted(missing_labels):
                caveat_violations.append(
                    f"{t}: missing required caveat [{label}]: expected a "
                    f"phrase matching {caveat_prose_by_label[label]!r}"
                )
        elif required:
            caveat_satisfied_count += 1

    if forbidden_violations or caveat_violations:
        if forbidden_violations:
            _print_bucket("forbidden phrase match(es)", forbidden_violations)
        if caveat_violations:
            _print_bucket(
                "file(s) missing a required 6.25 V ceiling caveat",
                caveat_violations,
            )
        return 1

    # The caveat count is reported as satisfied-of-required plus an explicit
    # exempt count, because under D-11 one target legitimately carries no
    # caveat requirement at all. The donor's "N file(s) carry both required
    # caveats" sentence would misreport that file either as a pass it did not
    # earn or as a gap it does not have.
    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_satisfied_count} of {caveat_required_count} caveat-required "
        f"file(s) carry every caveat their own rule demands; "
        f"{caveat_exempt_count} file(s) carry no caveat requirement under D-11 "
        "(this PASS is compliance with the forbidden-phrase table and the "
        "per-file caveat rules only -- see the module docstring's explicit "
        "non-claim, and note that CLOSE-01 also requires the fixture suite "
        "and the real-file plant transcript)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
