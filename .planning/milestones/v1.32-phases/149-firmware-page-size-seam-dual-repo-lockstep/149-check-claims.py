#!/usr/bin/env python3
"""Forbidden-overclaim / required-caveat scanner over Phase 149's own review
artifact, `149-PAGE-SIZE.md`, and (once plan 08 extends the list) every
`149-*-SUMMARY.md`.

**This module IS D-19's phase-local claim gate.** D-19 asks for a machine gate
armed against the real artifacts this phase writes and seen to fail on a
planted violation; this script is that gate's scanning half, and the paired
suite plus the committed plant-and-revert transcript
(`149-CLAIM-GATE-TRANSCRIPTS.md`) are its two proofs.

It is a Phase-149-scoped **sibling** of Phase 146's gate, not a copy, fork,
subclass or env-seam of it. Source: `146-check-claims.py` in
`.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/`,
read in full. The pure mechanics adapted from it are the module-top
`__file__`-derived directory constant (`146-check-claims.py:108`),
`resolve_targets`'s argv/env/defaults precedence
with its load-bearing `is not None` env check (`:272-290`), the hoisted
never-vacuous guard and the fail-closed missing-target branch (`:373-387`),
`_print_bucket`'s 20-entry display cap (`:341-346`), and eleven of its twelve
forbidden patterns plus the module skeleton itself, transcribed unchanged.

**Mandatory renames distinguish this sibling from its donor**, exactly as the
donor itself required of Phase 139's gate before it:

1. `_DEFAULT_TARGETS` is this phase's own review artifact, `149-PAGE-SIZE.md`,
   plus all eight `149-01-SUMMARY.md`..`149-08-SUMMARY.md` (extended by
   plan 08 once every one of them existed, `149-08-SUMMARY.md` itself added
   only once it was written -- see this plan's own SUMMARY for the ordering
   this required) -- nine entries, enumerated one by one, never a wildcard
   expansion and never a recursive directory traversal: a wildcard
   `149-`-prefixed default
   set would sweep in `149-CONTEXT.md`, `149-RESEARCH.md` and
   `149-DISCUSSION-LOG.md` (each carrying the forbidden vocabulary as
   discussion prose), the fixtures directory (whose planted files exist
   precisely to be violations), and `149-CLAIM-GATE-TRANSCRIPTS.md` itself
   (whose RED blocks necessarily quote forbidden text as evidence). All of
   those stay permanently out of `_DEFAULT_TARGETS` by design, not by
   oversight.
2. The self-check's phase-number prefix literal is `"149-"` in **both**
   places -- the `startswith` call and the failure message it prints. The
   donor carries its own prefix in both (`146-check-claims.py:262`, `:265`);
   changing only the call leaves a message that names the wrong phase, which
   is a silent documentation defect no fixture leg can observe.
3. The env-override seam is `FIRESTARTER_CLAIMSCAN_TARGETS_149`. The donor's
   `_146`-suffixed name is a distinct live checker in a sibling phase
   directory -- reusing either it or a bare/milestone-suffixed name would let
   one phase's seam retarget another phase's gate, or let one test suite aim
   two live checkers at once.
4. This docstring and its explicit non-claim are retargeted at PGSZ-05 and at
   this plan's own blocking operator wording review (task 3). The donor's own
   closing paragraph names Phase 146's requirement id and plan; this one names
   PGSZ-05 and the checkpoint that reviews the `proven-unqualified` narrowing
   below.

**The `proven-unqualified` row is NOT transcribed unchanged -- this is the one
deliberate, measured deviation from "the pure mechanics carry across
unchanged" claim above.** Every prior claim gate in this project (Phase 139,
146) carries `("proven-unqualified", re.compile(r"\\bproven\\b",
re.IGNORECASE))`, and Phase 146's own docstring already records that `\\b`
matches after a hyphen (`146-check-claims.py:63-65`). PGSZ-05 mandates the
literal phrase "software-proven and unvalidated on silicon" -- copied
verbatim, the unqualified pattern would forbid the exact phrase D-19 requires
the required-caveat table to demand, making this gate unsatisfiable by its own
protected artifact. `149-RESEARCH.md` §X-2 measured this collision and its
resolution: a negative lookbehind naming exactly the "software-" prefix,
attached ahead of the same `\\bproven\\b` body, permits *only* the exact
PGSZ-05 compound and continues to reject every other spelling of the word --
a bare "proven", "proven on silicon", "the write path is proven",
"bench-proven", "silicon-verified" is unaffected because it is a different
pattern. This is a **narrowing of one pattern's reach**, not a loosening of
the table's intent; the required-caveat row below still forces the exact
phrase to be present, so the phrase cannot be silently dropped either.
Widening the lookbehind past exactly that one prefix (to bare-hyphen, for
instance) would silently also permit "bench-proven", "datasheet-proven" and
"silicon-proven" -- task 3's operator checkpoint exists to catch that specific
failure mode before this gate is relied on for the rest of the phase. The
compiled pattern itself, below, is the single source of truth for its own
exact spelling.

**This scan carries no window and no exclusion mechanism**, per the donor's
own D-14 precedent. No proximity window, no context condition, no
exclusion-by-heading quarantine, no inline allow-marker: every match anywhere
in a scanned file's text is a violation. Phase 139 measured why -- a windowed
scanner keyed on tokens absent from this milestone's vocabulary passed a file
carrying four planted overclaims. That measurement is Phase 139's, cited here
rather than re-made.

Exit codes:
  0 -- every resolved target exists on disk, contains zero forbidden-phrase
       matches anywhere in its text, and carries the required caveat this
       phase's own per-file rule demands (a `PASS:` line naming every scanned
       file, by path relative to this module's own directory, is printed).
  1 -- the default-targets self-check fails (a `_DEFAULT_TARGETS` entry is not
       local to this module's own directory, or does not carry this phase's
       own "149-" prefix), OR zero targets resolved (never-vacuous), OR a
       resolved target is missing from disk (fail-closed), OR at least one
       forbidden-phrase match was found anywhere in a scanned file, OR a
       scanned file is missing a caveat its own rule requires. A bucketed
       `FAIL:` summary is printed for every failure case except the
       self-check, which prints its own `FAIL:` line per offending entry.

There is deliberately **no branch that exits 0 when nothing was scanned.**
Phase 137's checker carried one (`check_permitted_claims.py:299-319`) to
protect a window before its own targets were authored; it is not ported here,
because an exit-0-on-nothing-scanned path is a green that proves nothing, and
because this gate's whole purpose is to be armed against files that must
exist.

**Explicit non-claim (load-bearing, transcribed from the donor):** a green run
of this gate, at any point in this phase, is compliance with the
forbidden-phrase table and the per-file caveat rule **only**. It cannot detect
an implied overclaim, a misleading omission, a wrong tone, or a true statement
placed where it misleads. That non-claim is why plan 08's human wording review
is not optional and is not discharged by a green run of this script alone.
"""

import os
import re
import sys

# Module-top path constant. This is the ONLY directory `_DEFAULT_TARGETS`
# below is ever built from -- never a sibling-directory string constant.
# This construction is what stops the cross-phase-copy defect where a
# checker's defaults silently resolved to a stale sibling phase directory
# and passed vacuously with nothing actually scanned.
# Source: `146-check-claims.py:108`, copied verbatim.
_HERE = os.path.dirname(os.path.abspath(__file__))

# Extended at plan 08 to every artifact this phase produces (D-19's closing
# extension): this phase's own review artifact plus all seven prior plans'
# SUMMARYs. `149-08-SUMMARY.md` is deliberately NOT included -- it does not
# exist while this task runs, and this gate's fail-closed missing-target
# branch (below) has no exit-0-on-nothing-scanned escape hatch to protect a
# target named before it exists. It is scanned instead via the argv form,
# after it is written (see `149-CLAIM-GATE-TRANSCRIPTS.md` §"Extended target
# list (plan 08)" and this plan's own SUMMARY).
#
# Never a wildcard expansion, never a recursive directory traversal: a
# wildcard `149-`-prefixed default set would sweep in `149-CONTEXT.md`,
# `149-RESEARCH.md` and `149-DISCUSSION-LOG.md` (each carrying the forbidden
# vocabulary as discussion prose), the fixtures directory (whose planted
# files exist precisely to be violations), and `149-CLAIM-GATE-TRANSCRIPTS.md`
# (whose RED blocks quote forbidden text as evidence by design). All of those
# stay permanently out of this list, by design, not by oversight.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "149-PAGE-SIZE.md"),
    os.path.join(_HERE, "149-01-SUMMARY.md"),
    os.path.join(_HERE, "149-02-SUMMARY.md"),
    os.path.join(_HERE, "149-03-SUMMARY.md"),
    os.path.join(_HERE, "149-04-SUMMARY.md"),
    os.path.join(_HERE, "149-05-SUMMARY.md"),
    os.path.join(_HERE, "149-06-SUMMARY.md"),
    os.path.join(_HERE, "149-07-SUMMARY.md"),
    os.path.join(_HERE, "149-08-SUMMARY.md"),
]

# Env-override seam, SUFFIXED `_149`: the donor's `_146` name is a distinct
# live checker in a sibling phase directory, and bare/milestone-suffixed names
# are already live in yet other phases of this project -- a collision would
# let one phase's seam silently retarget another phase's gate, or let one test
# suite aim two live checkers at once. The suffix is the phase number rather
# than the milestone for exactly that reason.
# `os.environ.get(...)` with NO default is deliberate: it must return None
# when the variable is absent from the environment so resolve_targets() below
# can tell "absent -> use defaults" apart from "present but empty -> zero
# targets, never a silent fall-back to defaults".
FIRESTARTER_CLAIMSCAN_TARGETS_149 = os.environ.get(
    "FIRESTARTER_CLAIMSCAN_TARGETS_149"
)

# Seventeen forbidden-phrase labels/patterns, all case-insensitive, carrying
# this milestone's own vocabulary. The first twelve rows are the donor's
# table transcribed unchanged EXCEPT for the tenth row (`proven-unqualified`,
# see the module docstring and `149-RESEARCH.md` §X-2); the final five rows
# are this phase's own additions. No proximity window and no relational rule
# of any kind gates any of these -- every match anywhere in a scanned file's
# text is a violation, full stop.
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
    # MODIFIED (149-RESEARCH.md §X-2): narrowed with a negative lookbehind so
    # PGSZ-05's mandated compound "software-proven" is the ONLY spelling of
    # the word this row permits. Still fires on a bare "proven", on "proven
    # on silicon", on "the write path is proven", on "bench-proven", on
    # "silicon-proven" -- every one of those is a DIFFERENT sequence of
    # characters immediately before the word than "software-", so the
    # lookbehind does not suppress them. Do not widen this past exactly the
    # "software-" prefix below -- a bare-hyphen form would silently also
    # permit "bench-proven" and "silicon-proven", which is exactly the
    # failure mode the plan's operator checkpoint reviews for.
    ("proven-unqualified", re.compile(r"(?<!software-)\bproven\b", re.IGNORECASE)),
    ("now-works", re.compile(r"now\s+works?\b", re.IGNORECASE)),
    ("should-now-work", re.compile(r"should\s+now\s+work", re.IGNORECASE)),
    # ADDED -- this phase's own vocabulary, per `149-RESEARCH.md` §R9(d).
    (
        "page-size-proven",
        re.compile(
            r"page[-\s]size\s+(?:is\s+)?(?:proven|verified|validated)",
            re.IGNORECASE,
        ),
    ),
    (
        "graduation",
        re.compile(
            r"(?:graduat\w+|promot\w+)\s+(?:\w+\s+){0,3}(?:0x0[Dd]|protocol\s+13)",
            re.IGNORECASE,
        ),
    ),
    (
        "support-status-change",
        re.compile(
            r"support_status\s*(?:[:=]|changed|updated|now)", re.IGNORECASE
        ),
    ),
    (
        "issue-closed",
        re.compile(
            r"gh#(?:21|32|11|12)\b(?:\s+\w+){0,3}\s+(?:closed|resolved|fixed)",
            re.IGNORECASE,
        ),
    ),
    (
        "at28c256-fixed",
        re.compile(
            r"AT28C256\b(?:\s+\w+){0,4}\s+(?:fixed|works|now)", re.IGNORECASE
        ),
    ),
]

# One required-caveat label -- PGSZ-05's literal mandated phrase. Unlike the
# donor's two-caveat table (this milestone's 6.25 V ceiling vocabulary has no
# bearing here), this phase has exactly one qualifier every scanned target
# must carry.
REQUIRED_CAVEAT_PATTERNS = [
    (
        "software-proven-unvalidated",
        "the software-proven / unvalidated-on-silicon qualifier",
        re.compile(
            r"software[-\s]proven\s+and\s+unvalidated\s+on\s+silicon",
            re.IGNORECASE,
        ),
    ),
]

# The full label set, derived from the table above rather than restated, so a
# second required-caveat pattern cannot be added without the fail-closed
# default below picking it up.
_ALL_CAVEAT_LABELS = frozenset(
    label for label, _prose, _pattern in REQUIRED_CAVEAT_PATTERNS
)

# Per-basename caveat map. Keys are BASENAMES so the map cannot drift from
# `_DEFAULT_TARGETS`' `_HERE`-relative directory construction. Plan 08 adds
# the SUMMARY basenames when it extends `_DEFAULT_TARGETS`; the fail-closed
# default in `_required_caveats_for()` below means an omitted entry demands
# the caveat anyway, so silence can never produce a silent exemption.
#
# `149-CLAIM-GATE-TRANSCRIPTS.md` maps to the empty set, mirroring the
# donor's own D-11 exemption for `146-CORRECTIONS.md`: it is a committed
# evidence register of RED/GREEN gate runs, each block a literal command plus
# its literal output, not a claim about the change itself -- and it must not
# be held to a caveat rule written for a document that makes claims. This
# entry is inert in normal operation (the transcript file is never a member
# of `_DEFAULT_TARGETS` and is never passed via argv or the env seam by any
# real invocation of this gate -- see the module docstring and
# `test_the_transcript_file_is_not_a_gate_target`); it exists so the
# exemption mechanism itself stays behaviourally proven rather than only
# introspected, exactly as D-11 required of its own donor.
_CAVEAT_RULES = {
    "149-PAGE-SIZE.md": frozenset({"software-proven-unvalidated"}),
    "149-01-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-02-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-03-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-04-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-05-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-06-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-07-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-08-SUMMARY.md": frozenset({"software-proven-unvalidated"}),
    "149-CLAIM-GATE-TRANSCRIPTS.md": frozenset(),
}


def _required_caveats_for(path):
    """Return the set of required-caveat labels that `path` must satisfy.

    Keyed on `os.path.basename(path)`, so an argv- or env-supplied absolute
    path resolves to the same rule as the `_DEFAULT_TARGETS` entry for the
    same artifact.

    Fails CLOSED on an unknown basename: a target with no `_CAVEAT_RULES`
    entry gets the FULL caveat set, never the empty set. An empty-set default
    would let a future edit disable the caveat check for a real artifact by
    renaming it -- silently, and with the gate still reporting PASS.
    """
    return _CAVEAT_RULES.get(os.path.basename(path), _ALL_CAVEAT_LABELS)


def _assert_default_targets_are_local():
    """Startup self-check -- called first thing in main(), before target
    resolution or any scanning. Fails loudly, naming the offending entry
    and the exact defect, for every `_DEFAULT_TARGETS` entry that either
    does not resolve inside this module's own directory (`_HERE`) or does
    not carry this phase's own "149-" prefix.

    This is the run-time equivalent of a paired-test suite's mandatory
    cross-phase-copy legs, moved inside the script itself so a future copy
    of this file into another phase's directory fails loudly the first
    time it is run, rather than silently scanning nothing and reporting
    success. Source: `146-check-claims.py:235-269`; the prefix literal is
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
        if not os.path.basename(entry).startswith("149-"):
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                "this phase's own 149- prefix -- this is the exact "
                "stale-name defect this self-check exists to catch"
            )
            all_local = False
    return all_local


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS_149 env seam if the variable is present
    in os.environ (checked via `is not None`, not truthiness -- an
    explicitly empty value must resolve to zero targets, never a silent
    fall-back to defaults); else `_DEFAULT_TARGETS`.

    Returns (targets, used_defaults): `used_defaults` is True only when
    neither argv nor the env seam was used.
    """
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_149 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_149.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True


def scan_text(text, path, required_caveats):
    """Scan `text` (the full contents of the file at `path`) for forbidden-
    phrase matches and for the presence of the caveats `required_caveats`
    demands of this particular file.

    Carries NO proximity window and NO context condition of any kind: every
    regex match in FORBIDDEN_PATTERNS anywhere in `text` is recorded as a
    violation, full stop -- see the module docstring for the measured reason
    (Phase 139's, cited not re-made) why a proximity window is exactly what
    this milestone must not repeat. There is likewise no exclusion-by-heading
    quarantine and no inline allow-marker.

    `path` is accepted so each call site threads the file it is scanning
    through explicitly and self-descriptively; the return shape below does
    not otherwise require it.

    `required_caveats` is the resolved per-file rule set, passed in rather
    than looked up here so the caller owns rule resolution and this function
    stays a pure scan. A label absent from `required_caveats` is not demanded
    of this file and can never appear in the returned missing set.

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

    Order of operations, from `146-check-claims.py:349-356`: the
    default-targets self-check FIRST, before any target resolution; resolve
    targets; the hoisted never-vacuous guard; partition into
    existing/missing; the fail-closed missing-target branch; then scan every
    existing target against its own per-file caveat rule and report.

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
                "file(s) missing a required software-proven-unvalidated caveat",
                caveat_violations,
            )
        return 1

    # The caveat count is reported as satisfied-of-required plus an explicit
    # exempt count, mirroring the donor: under a future `_CAVEAT_RULES`
    # extension a target could legitimately carry no caveat requirement at
    # all, and this shape reports that honestly rather than as an
    # unearned pass or an unexplained gap.
    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_satisfied_count} of {caveat_required_count} caveat-required "
        f"file(s) carry every caveat their own rule demands; "
        f"{caveat_exempt_count} file(s) carry no caveat requirement "
        "(this PASS is compliance with the forbidden-phrase table and the "
        "per-file caveat rule only -- see the module docstring's explicit "
        "non-claim, and note that a green run alone does not discharge plan "
        "08's human wording review)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
