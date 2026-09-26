#!/usr/bin/env python3
"""Planning-record staleness scanner for the five files that carry v1.23's
research corrections: `.planning/PROJECT.md`, `.planning/STATE.md`,
`.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` and
`.planning/notes/py32f071-port-branch-state.md`.

Distilled from `.planning/research/SUMMARY.md` §"Corrections to the Planning
Record" (the R-1...R-18 work list) and `130-RESEARCH.md`'s per-needle
live-site table. Twelve of the eighteen corrections have a live, falsifiable
subject in at least one of the five files (a superseded figure or claim that
actually still appears in prose); those twelve become the `_NEEDLES` table
below. The other six (R-4, R-12, R-13, R-16, R-17, R-18) have zero live
occurrences and are deliberately NOT needles here -- an unfalsifiable needle
is an unprovable leg, and they are instead recorded as discharged-with-
evidence in `130-NONREGRESSION.md`.

Exit codes:
  0 -- every resolved target exists on disk and every needle hit on every
       target is exempt (a `PASS:` line naming every scanned file, plus the
       exempt-hit tally by verdict, is printed), OR `--explain` mode was
       used (a diagnostic run always exits 0).
  1 -- zero targets resolved (never-vacuous), OR a resolved target is
       missing from disk (fail-closed), OR at least one needle hit on a
       resolved target is `unlabeled` (a bucketed `FAIL:` summary naming
       every unlabeled hit's file:line and needle label is printed).

**Explicit non-claim (load-bearing):** a green run of this gate proves that
each of the twelve *named* superseded figures/claims is either absent from
the five scanned files or explicitly exempted with a stated reason. It
proves nothing about staleness this table does not name -- the six R-Ns
with zero live occurrences, and any correction this milestone's research did
not surface, are outside this gate's reach by construction.

**Why three exemption mechanisms, not one:** `130-RESEARCH.md` C-7 found that
all six live `2992 B` hits in the current tree are either labeled correction
blocks or historically-correct v1.22-archive/decision-log prose that was
true when it was written and is preserved deliberately. A single "labeled
block" mechanism cannot express "this was true when written, on purpose" --
that is a different claim from "this has been corrected in place" -- so this
checker carries a **block/line label** mechanism (`⚠ CORRECTION`,
`⚠ SUPERSEDED`, ...) for corrected-in-place text, and a separate **inline
history marker** (`<!-- recordscan:history ... -->`) for historically-
accurate text that must not be swept away. RESEARCH C-8 adds a third case:
`ROADMAP.md:2468` is Phase 130's own success criterion 1, and it quotes
several of this checker's own needles verbatim because it *defines* them --
that is neither a correction nor history, it is the table describing itself,
so a third inline marker (`<!-- recordscan:allow ... -->`) exists for that
self-reference case alone.

**Why a fourth mechanism exists (Plan 130-09, mechanism 3 in the code below):**
`.planning/notes/py32f071-port-branch-state.md` is a dated (`2026-07-28`)
`/gsd-explore` capture. D-05 assigns it an **append-only SUPERSEDED section**
rather than in-place correction, specifically so the "what did we once
believe" trail survives byte-for-byte. Mechanisms 1 and 2 are both *forward*
or *same-line*: `exempt_regions()` only extends a block forward from an
opener, and the two inline markers must sit on the same physical line as the
needle they exempt. Neither can retroactively cover a stale line that sits
*above* an appended section without editing that line -- which is exactly
what D-05 forbids for this file. Plan 130-09 therefore adds a narrowly-scoped
**retroactive supersession marker**,
`<!-- recordscan:supersedes needle=<label> lines=<n,n,...> reason: <text> -->`,
which may appear anywhere in the file (in practice: inside the appended
SUPERSEDED section, itself already exempt via mechanism 1) and declares that
one specific needle *label*, on specific 1-based line *numbers* elsewhere in
the SAME file, is retroactively covered. This is deliberately NOT "the whole
file is superseded" or "any line near the word SUPERSEDED is exempt": (a) the
needle label must be one of the twelve real labels in `_NEEDLE_LABELS` --
an unrecognised or misspelled label exempts nothing; (b) the line numbers are
an explicit enumerated list, not a range or "the rest of the file" -- a line
not named stays `unlabeled`; (c) a reason is mandatory, exactly as mechanisms
2's markers require (`_marker_has_reason`); and (d) the trigger is the exact
`recordscan:supersedes` marker syntax, never the English word "superseded"
appearing in a heading or prose. Merely titling a section "## SUPERSEDED"
with no marker exempts nothing under this mechanism (mechanism 1 may still
apply to lines physically inside that section, but that is unchanged,
already-existing behaviour, not this new path). See
`test_check_record_corrections.py`'s "mechanism 3" test group for the
positive, narrow-scoping-negative, and reachability proofs.

**Why the target list is resolved from a repo root, not from this file's
directory:** RESEARCH C-2 reproduced exactly this defect in the sibling
claim gate (`123-non-regression-baselines-gate-hardening/check_permitted_claims.py`)
-- its `_DEFAULT_TARGETS` resolved against *that module's own* directory, so
a default-mode run scanned four paths that could never exist there, printed
`UNARMED:` and exited 0: a green run that scanned nothing. This checker's
five targets live under `.planning/` at the repo root, nowhere near this
module's own Phase 130 directory, so `_find_repo_root()` below walks upward
from this file to the first ancestor holding a `.planning` subdirectory and
raises rather than silently falling back to this file's own directory if
none is found.

**Why there is no all-or-nothing arming branch:** unlike the sibling claim
gate's four closing artifacts (which do not exist until Phase 130 writes
them), all five of this checker's default targets are pre-existing planning
records that always exist once a project is initialized. There is no
"has the close started yet" question to ask, so the ordinary fail-closed
missing-target guard is the only guard this checker needs.

**RESEARCH note on `130-RESEARCH.md`'s own prose:** that document's "six
target files" sentence is an off-by-one against its own five-entry
enumeration; the enumeration is authoritative here. `.planning/research/
SUMMARY.md` itself is a research input, not a planning record this gate
maintains, and is deliberately not a scan target.
"""

import collections
import os
import re
import sys

# ---------------------------------------------------------------------------
# Target resolution -- from a discovered repo root, NEVER from this module's
# own directory (RESEARCH C-2; see the module docstring's "Why the target
# list is resolved from a repo root" paragraph).
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root():
    """Walk upward from `_HERE` and return the first ancestor directory that
    contains a `.planning` subdirectory. Raises `RuntimeError` -- never
    silently falls back to `_HERE` -- if no such ancestor exists, because a
    silent fallback here is exactly the C-2 defect this checker exists to
    avoid."""
    d = _HERE
    while True:
        if os.path.isdir(os.path.join(d, ".planning")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(
                "check_record_corrections.py: could not find a repo root "
                f"(no ancestor of {_HERE!r} contains a .planning directory) "
                "-- refusing to silently fall back to this module's own "
                "directory, which is exactly the C-2 defect this checker "
                "exists to avoid"
            )
        d = parent


_REPO_ROOT = _find_repo_root()

# Exactly five entries, in this order. `130-RESEARCH.md`'s prose says "six
# target files" while enumerating five -- the enumeration above is
# authoritative and the count in that sentence is an off-by-one;
# `research/SUMMARY.md` itself is a research input, not a record this gate
# maintains, and is deliberately not a sixth target.
#
# LOCATOR REPOINT at the v1.23 milestone close (2026-08-03), same class as
# Plan 130-01's `_DEFAULT_TARGETS` repoint of the sibling claim gate (recorded
# as mechanism correction #3 in `130-LEDGER.md`): `/gsd-complete-milestone`
# archives `.planning/REQUIREMENTS.md` to
# `.planning/milestones/v1.23-REQUIREMENTS.md` and then removes the original
# via `git rm`, so the live path no longer exists. This gate fails CLOSED on a
# missing target -- correctly -- so leaving the stale path here would have made
# it permanently RED for a reason that is bookkeeping, not a record defect.
# The subject did not disappear, it MOVED: the pointer follows it to the
# archived copy (same content plus an archive header). This is a locator-only
# change -- the twelve-needle table, every exemption mechanism and the
# fail-closed missing-target behaviour are all untouched, verified by the
# gate still failing on a planted violation in the repointed file.
_DEFAULT_TARGETS = [
    os.path.join(_REPO_ROOT, ".planning", "PROJECT.md"),
    os.path.join(_REPO_ROOT, ".planning", "STATE.md"),
    os.path.join(_REPO_ROOT, ".planning", "ROADMAP.md"),
    os.path.join(
        _REPO_ROOT, ".planning", "milestones", "v1.23-REQUIREMENTS.md"
    ),
    os.path.join(_REPO_ROOT, ".planning", "notes", "py32f071-port-branch-state.md"),
]

# Env-override seam. A NEW name, distinct from the sibling claim gate's own
# env var (its name is `FIRESTARTER_` + `CLAIMSCAN_TARGETS`, deliberately not
# spelled out verbatim here so a literal grep for it finds zero hits in this
# module -- RESEARCH A3 says reuse is safe only while the two checkers never
# coexist in one process, and after this plan they do, since both live
# checkers now exist side by side in this phase directory).
# `os.environ.get(...)` with NO default is deliberate -- it must return None
# when the variable is absent from the environment, and the (possibly empty)
# raw string when present, so `resolve_targets` below can tell "absent -> use
# defaults" apart from "present-but-empty -> zero targets, never a silent
# fall-back to defaults". Values are split on os.pathsep; empty segments are
# dropped.
FIRESTARTER_RECORDSCAN_TARGETS = os.environ.get("FIRESTARTER_RECORDSCAN_TARGETS")


# ---------------------------------------------------------------------------
# The needle table -- twelve superseded figures/claims with a live,
# falsifiable subject in the current tree (RESEARCH's per-needle live-site
# table). Six further R-Ns (R-4, R-12, R-13, R-16, R-17, R-18) have zero live
# occurrences and are deliberately NOT needles -- see the module docstring.
# All case-insensitive. Where a needle is a two-token collocation, both
# tokens are required on the SAME physical line -- these records are written
# as long single-line bullets and table rows, so a line is the right scoping
# unit, not a sentence (these files have no reliable sentence terminators
# either -- version numbers, file names and decimals all contain periods).
# ---------------------------------------------------------------------------

_NEEDLES = [
    # R-2: py32's DATA_BUFFER_SIZE is 512, not 1024 (CMakeLists.txt:113).
    (
        "py32-buffer-1024",
        re.compile(r"(?=.*\bDATA_BUFFER_SIZE\b)(?=.*\b1024\b)", re.IGNORECASE),
    ),
    # R-3: every py32 branch is measured 27 [commits] behind `beta` in the
    # notes file -- superseded by later phases landing the merge.
    (
        "branches-27-behind",
        re.compile(r"27\s+commits\s+behind|27\s+behind", re.IGNORECASE),
    ),
    # R-11: firestarter_app's feature/py32f071-fw-install head was 311eacf;
    # corrected head is 4ee64a1 (the branch that actually landed in P127).
    ("host-head-311eacf", re.compile(r"311eacf", re.IGNORECASE)),
    # R-10: the Leonardo headroom figure quoted as "2992 B" predates Phase
    # 119's own +392 B; word-bounded so it cannot match a longer number.
    ("leonardo-headroom-2992", re.compile(r"\b2992\b(?:\s*B)?", re.IGNORECASE)),
    # R-8/A-6: PORTING.md's dual-slot/CRC-validated design is stranded on
    # closed PRs and does not match what PR #48 actually built.
    (
        "porting-md-dual-slot",
        re.compile(
            r"(?=.*PORTING\.md)(?=.*(?:dual-slot|CRC-validated))", re.IGNORECASE
        ),
    ),
    # R-1: portability-macros does no pin-map work and provides no timing
    # consumers; the real portability mechanism is a fake Arduino core.
    (
        "portability-macros-provides",
        re.compile(
            r"(?=.*portability-macros)(?=.*(?:normalized platform ID|capability macros))",
            re.IGNORECASE,
        ),
    ),
    # R-5: the host branch's test-count claim (44 new unit tests) predates
    # the merged tree's own count (58 tests passing, per STATE.md).
    (
        "host-44-unit-tests",
        re.compile(r"44\s+new\s+unit\s+tests|44\s+unit\s+tests", re.IGNORECASE),
    ),
    # R-6: the CLI-surface line number is stale; corrected line is :932.
    ("cli-handlers-821", re.compile(r"cli_handlers\.py:821", re.IGNORECASE)),
    # R-7: the firestarter_{board}.hex extension hardcoding is ALREADY FIXED
    # on the branch (asset_candidates()/`_pick_asset()`) -- do not re-plan.
    (
        "hex-extension-hardcoded",
        re.compile(
            r"(?=.*hardcoded)(?=.*" + re.escape("firestarter_{board}.hex") + r")",
            re.IGNORECASE,
        ),
    ),
    # R-14: the third-stack branch state (2c2ed10, 603 additions) is the
    # smallest/stalest of five branches, corrected by 130-RESEARCH's table.
    (
        "third-stack-2c2ed10",
        re.compile(r"2c2ed10|603\s+additions", re.IGNORECASE),
    ),
    # R-15 toolchain half (D-07's target): the ARM toolchain IS installable
    # in the devcontainer (needs 2 newlib pkgs CI omits) -- "absent" is stale.
    (
        "arm-toolchain-absent",
        re.compile(r"(?=.*arm-none-eabi-gcc)(?=.*absent)", re.IGNORECASE),
    ),
    # 129-RESEARCH C-1 / this phase's C-9: the PY32F071 HAS a VTOR
    # (__VTOR_PRESENT 1) and the firmware already writes SCB->VTOR at boot.
    ("part-with-no-vtor", re.compile(r"no\s+VTOR", re.IGNORECASE)),
]

_NEEDLE_LABELS = frozenset(label for label, _ in _NEEDLES)
assert len(_NEEDLES) == 12, len(_NEEDLES)
assert len(_NEEDLE_LABELS) == 12, "duplicate needle label"


# ---------------------------------------------------------------------------
# Exemption mechanism 1 -- labeled blocks and labeled lines.
# ---------------------------------------------------------------------------

# A line that OPENS a multi-line labeled block: an optional list marker,
# then **, then the warning glyph, at line start. Covers PROJECT.md's
# paragraph-style corrections (e.g. lines 55, 61, 63, 65, 67) and doubles as
# the single-line case for STATE.md's `- **⚠ ...` bullets, which close again
# one line later because the very next line is an ordinary bullet (see
# `_BLOCK_CLOSER_RE` below).
_LABEL_OPENER_RE = re.compile(r"^\s*(?:[-*]\s+)?\*\*⚠")

# A label token anywhere on the hit line itself -- covers STATE.md's
# single-bullet labels and ROADMAP.md's inline mid-line supersession marker
# (e.g. line 34's "**⚠ SUPERSEDED — ..."), neither of which opens a
# multi-line block.
_LINE_LABEL_RE = re.compile(
    r"⚠\s*(?:CORRECTION|RESEARCH CORRECTIONS|SUPERSEDED|DESIGN)\b|^SUPERSEDED\b",
    re.IGNORECASE,
)

# Closes an open block at the first subsequent line matching any of: a
# markdown heading, a horizontal rule, a bold-led line that is not itself a
# new label opener (that case is checked separately, before this pattern, so
# a new opener starts a fresh block rather than merely closing the old one),
# or a top-level list bullet that is not itself a label opener (checked the
# same way). This last clause is what keeps STATE.md's labeled bullets one
# line wide while letting PROJECT.md's numbered-item bodies (which use `1.`,
# not `-`) stay inside their block.
_BLOCK_CLOSER_RE = re.compile(r"^#{1,6}\s|^---\s*$|^\*\*(?!⚠)|^\s*-\s+")

# Exemption mechanism 2 -- inline markers, invisible in rendered markdown.
# Matched in two steps (see `_verdict_for_line`): first find the marker and
# its keyword, then separately require the captured span between the
# keyword and the closing `-->` to contain real reason text once stripped --
# a bare marker with no stated reason does NOT exempt (an exemption with no
# reason is the fail-open shape this milestone keeps finding).
_INLINE_MARKER_RE = re.compile(r"<!--\s*recordscan:(history|allow)(.*?)-->")


def _marker_has_reason(raw_reason_span):
    """True iff `raw_reason_span` (the text between the recordscan: keyword
    and the closing `-->`) contains at least one non-whitespace character
    once stripped -- i.e. the marker carries a stated reason rather than
    being bare."""
    return bool(raw_reason_span.strip())


# Exemption mechanism 3 -- retroactive supersession (Plan 130-09). See the
# module docstring's "Why a fourth mechanism exists" paragraph. Deliberately
# a DIFFERENT marker keyword (`supersedes`, not `history`/`allow`) so a
# grep for the mechanism-2 keywords never accidentally matches this one, and
# deliberately requires BOTH a known needle label AND an explicit line-number
# list -- there is no spelling of this marker that exempts "the whole file"
# or "every line near this word".
_SUPERSEDE_MARKER_RE = re.compile(
    r"<!--\s*recordscan:supersedes\s+needle=([a-zA-Z0-9-]+)\s+lines=([0-9,\s]+?)\s+(.*?)-->",
    re.DOTALL,
)


def _collect_superseded_targets(lines):
    """Scan all `lines` of one file for `recordscan:supersedes` markers and
    return a dict of `{needle_label: {line_number, ...}}` -- the set of
    1-based line numbers that marker declares retroactively covered for that
    needle label.

    Fails closed on both axes: a label not present in `_NEEDLE_LABELS` (a
    typo, or a label for a needle that does not exist) contributes NOTHING
    -- it does not raise, and it does not exempt anything, so a mistyped
    label leaves the real hit `unlabeled` rather than silently passing. A
    marker whose reason span is blank once stripped (`_marker_has_reason`)
    is likewise ignored entirely, matching mechanism 2's requirement that an
    exemption always carries a stated reason."""
    targets = collections.defaultdict(set)
    for line in lines:
        for m in _SUPERSEDE_MARKER_RE.finditer(line):
            label, line_csv, reason = m.group(1), m.group(2), m.group(3)
            if label not in _NEEDLE_LABELS:
                continue
            if not _marker_has_reason(reason):
                continue
            for tok in line_csv.split(","):
                tok = tok.strip()
                if tok.isdigit():
                    targets[label].add(int(tok))
    return targets


def exempt_regions(lines):
    """Return the set of zero-based line indices covered by an open labeled
    block, so `scan_text` can ask one question per needle hit."""
    exempt = set()
    open_block = False
    for i, line in enumerate(lines):
        if open_block:
            if _LABEL_OPENER_RE.match(line):
                # A new label opener implicitly closes the previous block
                # and immediately opens a new one on this same line.
                exempt.add(i)
                continue
            if _BLOCK_CLOSER_RE.match(line):
                open_block = False
                continue
            exempt.add(i)
            continue
        if _LABEL_OPENER_RE.match(line):
            exempt.add(i)
            open_block = True
    return exempt


Record = collections.namedtuple("Record", ["path", "lineno", "label", "verdict"])


def _verdict_for_line(i, line, exempt_line_indices, label, superseded_targets):
    """Return the verdict for a needle hit on zero-based line index `i` /
    text `line` / needle `label`: `inline-history` or `inline-allow`
    (mechanism 2, reason required), `line-label` or `block` (mechanism 1),
    `superseded` (mechanism 3, Plan 130-09 -- a `recordscan:supersedes`
    marker elsewhere in the file names this exact label and this exact
    1-based line number), else `unlabeled`."""
    m = _INLINE_MARKER_RE.search(line)
    if m and _marker_has_reason(m.group(2)):
        keyword = m.group(1)
        return "inline-history" if keyword == "history" else "inline-allow"
    if _LINE_LABEL_RE.search(line):
        return "line-label"
    if i in exempt_line_indices:
        return "block"
    if (i + 1) in superseded_targets.get(label, ()):
        return "superseded"
    return "unlabeled"


def scan_text(text, path):
    """Scan `text` (the contents of `path`) for every needle hit.

    Returns the full list of `Record(path, lineno, label, verdict)` tuples,
    one per matching line per needle -- both exempt and unlabeled hits are
    included; `main` filters. `lineno` is one-based."""
    lines = text.splitlines()
    exempt = exempt_regions(lines)
    superseded_targets = _collect_superseded_targets(lines)
    records = []
    for label, pattern in _NEEDLES:
        for i, line in enumerate(lines):
            if pattern.search(line):
                verdict = _verdict_for_line(i, line, exempt, label, superseded_targets)
                records.append(Record(path, i + 1, label, verdict))
    return records


def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_RECORDSCAN_TARGETS env seam if the variable is present in
    os.environ (checked via `is not None`, not truthiness -- an explicitly
    empty value must resolve to zero targets, never a silent fall-back to
    defaults); else `_DEFAULT_TARGETS`."""
    if argv:
        return list(argv)
    if FIRESTARTER_RECORDSCAN_TARGETS is not None:
        return [p for p in FIRESTARTER_RECORDSCAN_TARGETS.split(os.pathsep) if p]
    return list(_DEFAULT_TARGETS)


def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")


def main(argv):
    """Entry point: strip an optional leading `--explain` flag, resolve
    targets, scan each, and either print a diagnostic (`--explain`, always
    exits 0) or exit non-zero on any `unlabeled` hit.

    Never-vacuous guard first, then the ordinary fail-closed missing-target
    guard -- there is no D-15-style arming branch here, because all five
    default targets always exist (see the module docstring's "Why there is
    no all-or-nothing arming branch" paragraph)."""
    argv = list(argv)
    explain = False
    if argv and argv[0] == "--explain":
        argv = argv[1:]
        explain = True

    targets = resolve_targets(argv)

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

    all_records = []
    for t in targets:
        with open(t, encoding="utf-8") as f:
            text = f.read()
        all_records.extend(scan_text(text, t))

    if explain:
        tally = {}
        for rec in all_records:
            tally[rec.verdict] = tally.get(rec.verdict, 0) + 1
            print(f"{rec.path}:{rec.lineno}  {rec.label}  {rec.verdict}")
        print(f"Tally: {tally}")
        return 0

    violations = [r for r in all_records if r.verdict == "unlabeled"]
    if violations:
        by_label = {}
        for r in violations:
            by_label.setdefault(r.label, []).append(f"{r.path}:{r.lineno}")
        for label in sorted(by_label):
            _print_bucket(label, by_label[label])
        return 1

    exempt_tally = {}
    for r in all_records:
        if r.verdict != "unlabeled":
            exempt_tally[r.verdict] = exempt_tally.get(r.verdict, 0) + 1
    print(
        f"PASS: scanned {', '.join(os.path.relpath(t, _REPO_ROOT) for t in targets)}; "
        f"exempt hits by verdict: {exempt_tally}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
