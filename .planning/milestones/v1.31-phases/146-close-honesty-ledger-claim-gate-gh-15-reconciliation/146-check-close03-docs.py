#!/usr/bin/env python3
"""CLOSE-03 documentation checker (D-13): five required topics plus zero
forbidden overclaim phrases, over the four sub-repo documentation files
CLOSE-03 names.

This module is a **second, separately shaped** checker, deliberately not a
mode, flag, subclass or env-seam of the sibling `146-check-claims.py` in this
same directory. D-11 kept that gate's rule set aimed at this phase's five
closing artifacts -- outward-facing release and reconciliation prose whose
honesty discipline includes a required qualifying statement. D-13 rejected
pushing that same required-qualifier rule into a public README and an
agent-facing reference: those documents owe **topic coverage**, not a release
body's qualifying sentence. So this module declares no required-qualifier rule
of any kind (grep this file for that word and the count is zero, on purpose --
a non-zero count means someone folded D-11's design back in here). What the
two modules do share is the twelve forbidden-phrase patterns, transcribed
unchanged from `139-check-claims.py:98-128`, and the fail-closed /
never-vacuous mechanics.

Why this checker is hosted in `.planning/phases/146-.../` and NOT inside
either sub-repo
---------------------------------------------------------------------------
Every path it scans lives in `firestarter/` or `firestarter_app/`, so the
obvious home would be one of those repositories' test suites. That is exactly
the shape this project has recorded failing. A gate hosted in the host
application which scans firmware source breaks silently when the firmware
renames a file, and it breaks by failing **OPEN**: it reports success having
scanned nothing. That happened four times in Phase 117, and the live instance
is `firestarter_app/tests/test_py32_flash_map_host.py`'s firmware-presence
gate, which `.planning/PROJECT.md:1181` disclosure 4 states fails open across
the repository boundary **by design**. Hosting this checker in the phase
directory means nothing about it is conditional on the other repository being
checked out, present, or on any particular commit: a target that is absent is
a hard failure here (see the exit-code contract), never a skip.

Four named mitigations for that fail-open pattern, all of them present:

  1. Phase-local hosting, as argued above -- no presence gate anywhere.
  2. The fail-closed missing-target branch (`139-check-claims.py:275-282`,
     reused unchanged): any resolved path that is not a file on disk is
     non-zero, naming the path.
  3. The hoisted never-vacuous guard (`:268-273`, reused unchanged): an empty
     resolved target list is non-zero, and says so in those terms.
  4. A startup self-check, run first in `main()`.

The self-check, and why one of its legs is SUBSTITUTED rather than dropped
---------------------------------------------------------------------------
The sibling gate's self-check has two legs: every default target resolves
inside the phase's own directory, and every default target's basename carries
the phase's own `146-` prefix. The prefix leg **cannot** apply here, because
these targets are sub-repo documents with names this phase does not own. The
fail-open shape would be to delete that leg and substitute nothing, leaving a
self-check that no longer constrains the target list's shape at all. So it is
substituted, not dropped, by two legs that assert the list's *shape*:

  * every `_DEFAULT_TARGETS` entry resolves under the walked `_REPO_ROOT`; and
  * every entry's repo-relative path is a member of the literal four-element
    `_DOC_TARGET_ALLOWLIST` declared below.

A third leg asserts that the union of `_REQUIRED_TOPICS_BY_FILE`'s per-file
sets equals the full five-topic id set, so a future edit cannot quietly drop a
topic from every file at once and leave the module looking healthy. CLOSE-03
asks for five topics across the documentation; that assertion is what keeps
this module's per-file split honest about covering all five somewhere.

Target resolution walks upward to a repo root
---------------------------------------------------------------------------
`_find_repo_root()` is copied from
`.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py:120-137`
-- the only in-tree checker whose targets live outside its own phase
directory. It walks upward from this module's own directory and returns the
first ancestor containing a `.planning` subdirectory, and it **raises** rather
than falling back to this module's own directory, because a silent fallback is
precisely the defect that makes a copied checker scan nothing and pass. There
is deliberately no fixed count of `..` hops and no wildcard or directory
traversal anywhere in the target construction.

Exit codes
---------------------------------------------------------------------------
  0 -- every resolved target exists on disk, carries zero forbidden-phrase
       matches anywhere in its text, and satisfies every required topic in its
       own required set. A `PASS:` line naming **every** scanned file is
       printed.
  1 -- the startup self-check failed (a `_DEFAULT_TARGETS` entry resolves
       outside `_REPO_ROOT`, or is not in `_DOC_TARGET_ALLOWLIST`, or the
       per-file topic map's union is not the full topic set), OR zero targets
       resolved (never-vacuous), OR a resolved target is missing from disk
       (fail-closed), OR at least one forbidden-phrase match was found, OR a
       scanned file is missing at least one of its required topics. Every
       failure prints a `FAIL:` line; the report names, per file, each
       unsatisfied topic id and each forbidden-phrase hit with its 1-based
       line number.

There is no code path that returns 0 having scanned nothing.

**Explicit non-claim (load-bearing).** A green run of this checker means the
five topics are **present** in the documents that owe them. It does not mean
the prose is correct, complete, well-placed, or well-worded. A regex cannot
tell a correct sentence about the per-byte loop from a wrong one. That
judgement is the blocking operator wording review in plan `146-12`, and a
green run here must never be reported -- in any SUMMARY, register, or phase
artifact -- as having discharged it.
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Target resolution -- from a walked repo root, never from this module's own
# directory, because every target lives outside it.
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root():
    """Walk upward from `_HERE` and return the first ancestor directory that
    contains a `.planning` subdirectory. Raises `RuntimeError` -- never
    silently falls back to `_HERE` -- if no such ancestor exists, because a
    silent fallback is exactly the defect that lets a copied checker resolve
    nothing and report success.

    Copied from `check_record_corrections.py:120-137` (Phase 130), the only
    in-tree checker whose targets live outside its own phase directory. No
    fixed number of `..` hops, no wildcard.
    """
    d = _HERE
    while True:
        if os.path.isdir(os.path.join(d, ".planning")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(
                "146-check-close03-docs.py: could not find a repo root (no "
                f"ancestor of {_HERE!r} contains a .planning directory) -- "
                "refusing to silently fall back to this module's own "
                "directory, which is the fail-open defect this checker "
                "exists to avoid"
            )
        d = parent


_REPO_ROOT = _find_repo_root()

# The literal four-element allowlist the self-check's substituted shape leg
# asserts membership in. Repo-relative, POSIX-separated, so it is directly
# comparable with `_REQUIRED_TOPICS_BY_FILE`'s keys and with the relative form
# of anything handed in through argv or the env seam.
_DOC_TARGET_ALLOWLIST = [
    "firestarter/doc/PROTOCOLS.md",
    "firestarter/CLAUDE.md",
    "firestarter/README.md",
    "firestarter_app/README.md",
]

# Exactly four entries, in this order -- the CLOSE-03 documentation targets.
# Built one `os.path.join(_REPO_ROOT, ...)` at a time: never a wildcard
# expansion, never a recursive directory walk, never a `..`-hop chain.
_DEFAULT_TARGETS = [
    os.path.join(_REPO_ROOT, "firestarter", "doc", "PROTOCOLS.md"),
    os.path.join(_REPO_ROOT, "firestarter", "CLAUDE.md"),
    os.path.join(_REPO_ROOT, "firestarter", "README.md"),
    os.path.join(_REPO_ROOT, "firestarter_app", "README.md"),
]

# Env-override seam, with its OWN name. The sibling claim gate in this same
# directory owns `FIRESTARTER_` + `CLAIMSCAN_TARGETS_146`; three earlier
# checkers own the bare, `_V130`- and `_V131`-suffixed spellings of that same
# stem. Reusing any of them would let one test run silently retarget two live
# checkers at once, so this module takes `DOCSCAN` instead.
# `os.environ.get(...)` with NO default is deliberate: it must return None
# when the variable is absent, and the (possibly empty) raw string when
# present, so `resolve_targets()` can tell "absent -> use defaults" apart from
# "present but empty -> zero targets, never a silent fall-back to defaults".
# Values are split on os.pathsep; empty segments are dropped.
FIRESTARTER_DOCSCAN_TARGETS_146 = os.environ.get("FIRESTARTER_DOCSCAN_TARGETS_146")


# ---------------------------------------------------------------------------
# Rule sets
# ---------------------------------------------------------------------------

# The twelve forbidden-phrase labels/patterns, all case-insensitive,
# transcribed unchanged from `139-check-claims.py:98-128` and identical to the
# sibling gate's table. Applied to EVERY scanned file. There is no proximity
# window, no context condition, no exclusion marker and no heading quarantine
# of any kind -- a scoped proximity window is exactly what let a file carrying
# four planted overclaims measure clean under the v1.30 checker, and D-14
# forbids loosening, narrowing or re-deriving any of these.
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
        re.compile(r"verified\s+(?:on|against)\s+(?:real\s+)?silicon", re.IGNORECASE),
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

# The five CLOSE-03 topics, as (topic_id, prose, regex). These are PRESENCE
# tests, not correctness tests -- see the module docstring's explicit
# non-claim. This is the structural difference from the sibling claim gate:
# where that gate requires a qualifying sentence in a release body, this one
# requires that each document mentions the subjects CLOSE-03 promises it
# mentions.
REQUIRED_TOPIC_PATTERNS = [
    (
        "per-byte-algorithm",
        "the shipped per-byte pulse-to-verify loop",
        # Hyphenated, underscored and space-separated spellings all count.
        re.compile(r"per[-_\s]byte", re.IGNORECASE),
    ),
    (
        "parameter-table",
        "the protocol-keyed parameter table",
        # The table's own source-file stem -- `include/eprom_params.h`,
        # `src/proms/eprom_params.cpp`,
        # `tests/golden/eprom_params_citations.json`.
        re.compile(r"eprom_params"),
    ),
    (
        "database-supplied-pulse",
        "the program-pulse width as a database datum, not a firmware constant",
        # The database field name, in both its spellings: the JSON wire/DB
        # field is hyphenated, the firmware handle member is underscored.
        re.compile(r"pulse[-_]delay", re.IGNORECASE),
    ),
    (
        "pulse-override-flag",
        "the host's per-run program-pulse override flag",
        # The literal long-option spelling shipped by `write` since Phase 143.
        re.compile(r"--pulse-us"),
    ),
    (
        "program-vcc-ceiling",
        "the ~6.25 V program-VCC accepted debt",
        re.compile(r"6\.25\s*V"),
    ),
]

# Per-file required-topic sets, keyed by REPO-RELATIVE path so the map cannot
# drift from `_DEFAULT_TARGETS`' `os.path.join` construction (an absolute key
# would encode one machine's checkout path). Each set is chosen from what the
# document is for:
#
#   * `firestarter/doc/PROTOCOLS.md` -- all five. It is the per-protocol
#     reference a firmware developer reads, and it is the document that went
#     stale.
#   * `firestarter/CLAUDE.md` -- all five. It is the living agent-facing
#     reference and already carries four of them.
#   * `firestarter/README.md` -- the algorithm and the ceiling only. It is the
#     user-facing firmware surface; a parameter-table or DB-field-name mention
#     there would be noise, not documentation.
#   * `firestarter_app/README.md` -- the DB field, the override flag and the
#     ceiling. It is where a CLI user meets the flag; the firmware's internal
#     table is not that reader's concern.
#
# The union is all five, which is what CLOSE-03 asks for, and the self-check
# asserts that union so a future edit cannot drop a topic from every file at
# once.
_REQUIRED_TOPICS_BY_FILE = {
    "firestarter/doc/PROTOCOLS.md": (
        "per-byte-algorithm",
        "parameter-table",
        "database-supplied-pulse",
        "pulse-override-flag",
        "program-vcc-ceiling",
    ),
    "firestarter/CLAUDE.md": (
        "per-byte-algorithm",
        "parameter-table",
        "database-supplied-pulse",
        "pulse-override-flag",
        "program-vcc-ceiling",
    ),
    "firestarter/README.md": (
        "per-byte-algorithm",
        "program-vcc-ceiling",
    ),
    "firestarter_app/README.md": (
        "database-supplied-pulse",
        "pulse-override-flag",
        "program-vcc-ceiling",
    ),
}


def _all_topic_ids():
    """The full five-topic id set, derived from `REQUIRED_TOPIC_PATTERNS`
    rather than restated, so the two can never disagree."""
    return {topic_id for topic_id, _prose, _pattern in REQUIRED_TOPIC_PATTERNS}


def _repo_relative(path):
    """Return `path` as a POSIX-separated repo-relative key.

    An absolute path is made relative to `_REPO_ROOT`; a path already relative
    is normalised as given. A path outside the repo root produces a `..`-led
    key, which is in neither the allowlist nor the topic map -- so it fails
    closed at both, which is the intended behaviour rather than an accident.
    """
    if os.path.isabs(path):
        rel = os.path.relpath(os.path.abspath(path), _REPO_ROOT)
    else:
        rel = os.path.normpath(path)
    return rel.replace(os.sep, "/")


def _required_topics_for(path):
    """Return the required-topic id set for `path`.

    An **unrecognised or renamed** path returns the FULL five-topic set, not
    the empty set. This mirrors the sibling gate's per-file rule resolution
    and is the fail-closed direction: a target this module has never heard of
    is held to every topic, so a renamed or newly added document is loudly
    red rather than quietly waved through with nothing required of it.
    """
    key = _repo_relative(path)
    if key in _REQUIRED_TOPICS_BY_FILE:
        return set(_REQUIRED_TOPICS_BY_FILE[key])
    return _all_topic_ids()


def _assert_default_targets_are_allowlisted():
    """Startup self-check -- called first thing in `main()`, before target
    resolution and before any scanning. Fails loudly, naming the offending
    entry and the exact defect, and prints every failing entry rather than
    just the first.

    Three legs. The first two are the SUBSTITUTE for the sibling gate's
    basename-prefix leg, which cannot apply to sub-repo documents: every
    default target must resolve under `_REPO_ROOT`, and every default target's
    repo-relative path must be in `_DOC_TARGET_ALLOWLIST`. The third asserts
    that the per-file topic map's union is the full topic set. Dropping any of
    the three without substituting an equivalent is the fail-open shape this
    module exists to avoid.

    Returns True iff every leg passes.
    """
    ok = True
    root_prefix = os.path.abspath(_REPO_ROOT) + os.sep

    for entry in _DEFAULT_TARGETS:
        if not os.path.abspath(entry).startswith(root_prefix):
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not resolve "
                f"under the walked repo root {_REPO_ROOT!r} -- a target "
                "outside the repo root means the upward walk or the join "
                "construction has drifted"
            )
            ok = False
        rel = _repo_relative(entry)
        if rel not in _DOC_TARGET_ALLOWLIST:
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} (repo-relative "
                f"{rel!r}) is not a member of the four-element "
                "_DOC_TARGET_ALLOWLIST -- this is the shape assertion that "
                "substitutes for the sibling gate's basename-prefix leg, and "
                "removing it rather than substituting is the fail-open shape"
            )
            ok = False

    union = set()
    for topics in _REQUIRED_TOPICS_BY_FILE.values():
        union |= set(topics)
    full = _all_topic_ids()
    if union != full:
        print(
            "FAIL: the union of _REQUIRED_TOPICS_BY_FILE's per-file sets is "
            f"{sorted(union)}, not the full topic set {sorted(full)} -- "
            "CLOSE-03 asks for all five topics somewhere in the "
            "documentation, so a topic required of no file at all is a "
            "silently dropped requirement"
        )
        ok = False

    return ok


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    `FIRESTARTER_DOCSCAN_TARGETS_146` env seam if the variable is present in
    `os.environ` (checked via `is not None`, not truthiness -- an explicitly
    empty value must resolve to zero targets, never a silent fall-back to
    defaults); else `_DEFAULT_TARGETS`.

    Returns (targets, used_defaults); `used_defaults` is True only when
    neither argv nor the env seam was used.
    """
    if argv:
        return list(argv), False
    if FIRESTARTER_DOCSCAN_TARGETS_146 is not None:
        return [
            p for p in FIRESTARTER_DOCSCAN_TARGETS_146.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True


def scan_text(text, path, required_topics):
    """Scan `text` (the full contents of the file at `path`).

    Carries NO proximity window and NO context condition: every
    `FORBIDDEN_PATTERNS` match anywhere in `text` is recorded as a violation,
    full stop.

    Returns (forbidden_hits, missing_topic_ids):
      forbidden_hits -- list of (label, matched_text, lineno) tuples, one per
        match, 1-based lineno.
      missing_topic_ids -- the subset of `required_topics` whose regex did not
        match anywhere in `text`: the topics this file is MISSING, not the
        ones it has.
    """
    lines = text.splitlines()
    forbidden_hits = []
    for label, pattern in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(lines, start=1):
            for m in pattern.finditer(line):
                forbidden_hits.append((label, m.group(0), lineno))

    missing_topic_ids = {
        topic_id
        for topic_id, _prose, pattern in REQUIRED_TOPIC_PATTERNS
        if topic_id in required_topics and not pattern.search(text)
    }

    return forbidden_hits, missing_topic_ids


def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:40]:
        print(f"  {v}")
    if len(violations) > 40:
        print(f"  ... and {len(violations) - 40} more")


def main(argv):
    """Entry point.

    Order of operations, copied from `139-check-claims.py:249-326`: the
    startup self-check FIRST, before any target resolution; resolve targets;
    the hoisted never-vacuous guard; the fail-closed missing-target branch;
    then scan every target and report.

    Deliberately absent: any early-return branch that reports readiness when
    the targets are missing. All four targets are documents that already exist
    in the tree, so there is no pre-authored window to protect, and an
    exit-0-on-nothing-scanned path would cost real detection for no benefit.
    """
    if not _assert_default_targets_are_allowlisted():
        return 1

    targets, _used_defaults = resolve_targets(argv)

    if not targets:
        print(
            "FAIL: no scan targets resolved -- this checker cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    missing = [t for t in targets if not os.path.isfile(t)]
    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- this checker cannot "
            "vacuously pass with a target silently skipped (a renamed or "
            f"moved document is a hard failure, never a skip): {missing}"
        )
        return 1

    topic_prose_by_id = {
        topic_id: prose for topic_id, prose, _pattern in REQUIRED_TOPIC_PATTERNS
    }

    forbidden_violations = []
    topic_violations = []
    scanned = []

    for t in targets:
        with open(t, encoding="utf-8") as f:
            text = f.read()
        scanned.append(t)
        required = _required_topics_for(t)
        hits, missing_topics = scan_text(text, t, required)
        for label, matched_text, lineno in hits:
            forbidden_violations.append(
                f"{t}:{lineno}: forbidden phrase match [{label}]: {matched_text!r}"
            )
        for topic_id in sorted(missing_topics):
            topic_violations.append(
                f"{t}: missing required topic [{topic_id}]: expected text "
                f"describing {topic_prose_by_id[topic_id]!r}"
            )

    if forbidden_violations or topic_violations:
        if forbidden_violations:
            _print_bucket("forbidden phrase match(es)", forbidden_violations)
        if topic_violations:
            _print_bucket(
                "unsatisfied required CLOSE-03 topic(s)", topic_violations
            )
        print(
            "FAIL: scanned "
            f"{', '.join(_repo_relative(s) for s in scanned)} "
            f"({len(scanned)} file(s)); see the buckets above"
        )
        return 1

    print(
        f"PASS: scanned {', '.join(_repo_relative(s) for s in scanned)}; "
        f"{len(scanned)} file(s), zero forbidden-phrase matches, every "
        "required CLOSE-03 topic present in the file that owes it (this PASS "
        "means the topics are PRESENT, not that the prose is correct -- see "
        "the module docstring's explicit non-claim; correctness is the "
        "blocking operator wording review in plan 146-12)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
