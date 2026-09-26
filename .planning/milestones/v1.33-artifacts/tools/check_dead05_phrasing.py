#!/usr/bin/env python3
"""
DEAD-05 phrasing gate -- a negative scan for forbidden coverage phrasings
about `rurp_read_voltage_mv`, plus a positive assertion that the mandated
correct phrasing is present in every required target.

Requirements: DEAD-05
Decisions covered: OQ-5, D-02

WHAT IT DOES
------------
Resolves a fixed corpus (see CORPUS_GLOBS) of meta-repo and firestarter-repo
files, splits each into blank-line-delimited paragraphs, and scans every
paragraph that names `rurp_read_voltage_mv` (the sole entry in
TRIGGER_TOKENS) for one of six forbidden coverage phrasings -- enumerated,
with reasons, in `.planning/milestones/v1.33-artifacts/155-dead05-phrasing-corpus.md` and in
`155-VALIDATION.md`'s "The Honest Coverage Ceiling" item 5. That is the
NEGATIVE half. Separately, the POSITIVE half asserts that the mandated
correct phrasing (CORRECT_PHRASING) is present, whitespace-normalised, in
each of REQUIRED_POSITIVE_TARGETS. Both halves must clear for exit 0 -- an
absence-only gate would pass vacuously on an empty, renamed, or emptied
corpus, which is exactly what PARAGRAPH_FLOOR and the positive half both
exist to rule out.

This module's own scope constants (CORPUS_GLOBS, NAMED_EXCLUSIONS,
TRIGGER_TOKENS, PARAGRAPH_FLOOR, REQUIRED_POSITIVE_TARGETS) mirror
`.planning/milestones/v1.33-artifacts/155-dead05-phrasing-corpus.md` item for item and must not
drift from it. `.planning/milestones/v1.33-artifacts/tools/` -- this module's own directory -- is
never descended into by any corpus glob, so this module's own source, its
pytest and its planted fixture cannot enter the corpus they judge.

NOT AUTOMATED
-------------
This tool runs in NO CI workflow of either the meta repo or the firestarter
repo. Running it is a local, by-hand obligation, exactly like
`firestarter/scripts/check_size_baseline.py`'s own standing disclosure.

Exit codes:
  0 -- no forbidden-phrasing violation was found in any in-scope paragraph,
       the total in-scope paragraph count meets PARAGRAPH_FLOOR, AND every
       required-positive target carries the mandated phrasing (PASS:,
       naming every file scanned with its in-scope paragraph count, and
       every required target confirmed).
  1 -- at least one forbidden-phrasing violation was found (FAIL:, one
       indented line per violation naming the file, the paragraph's start
       line, the needle matched and the offending paragraph), OR a
       required-positive target exists on disk but does not carry the
       mandated phrasing (FAIL:).
  2 -- fail-closed / cannot render a verdict: malformed command-line
       arguments, the total in-scope paragraph count is below
       PARAGRAPH_FLOOR (ERROR:, naming the count, the floor, and the
       per-file breakdown), or a required-positive target is missing from
       disk entirely (ERROR:).

Usage:
    python3 .planning/milestones/v1.33-artifacts/tools/check_dead05_phrasing.py
    python3 .planning/milestones/v1.33-artifacts/tools/check_dead05_phrasing.py \\
        --corpus-root /path/to/meta-repo --fw-root /path/to/firestarter

Non-claim: a green run proves that no in-scope paragraph in the scanned
corpus carries a forbidden coverage phrasing about `rurp_read_voltage_mv`,
and that the mandated phrasing is present in every required target. It
proves NOTHING about whether the surrounding prose is COMPLETE -- a
paragraph that should have been written, but never was, cannot be scanned.
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants -- mirror .planning/milestones/v1.33-artifacts/155-dead05-phrasing-corpus.md item for
# item. A drift between this list and that document's corpus / exclusion /
# floor / required-target sections is a defect in one or the other.
# ---------------------------------------------------------------------------

#: The twelve corpus globs, in the same order and the same "firestarter/"
#: prefix convention as 155-dead05-phrasing-corpus.md section 5. A pattern
#: with the "firestarter/" prefix resolves against --fw-root; every other
#: pattern resolves against --corpus-root (the meta repo).
CORPUS_GLOBS = (
    ".planning/phases/155-*/155-*-PLAN.md",
    ".planning/phases/155-*/155-*-SUMMARY.md",
    ".planning/phases/155-*/155-VERIFICATION.md",
    ".planning/milestones/v1.33-artifacts/155-*.md",
    "firestarter/src/boards/rurp_common.cpp",
    "firestarter/src/proms/memory.cpp",
    "firestarter/include/firestarter.h",
    "firestarter/test/native/avr/test_val_5v_page/test_val_5v_page.cpp",
    "firestarter/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp",
    "firestarter/tests/test_voltage_reformulation_oracle.py",
    "firestarter/scripts/check_no_heap_or_64bit_symbols.py",
)

#: This directory (relative to --corpus-root) is never descended into by any
#: corpus glob -- this module, its pytest and its planted fixture all live
#: here, outside the corpus they judge.
TOOLS_DIR_REL = ".planning/milestones/v1.33-artifacts/tools"

#: Exactly three named exclusions, each with its one-line reason. Excluded
#: from the NEGATIVE half only (by basename) -- the positive half reads
#: 155-VALIDATION.md directly as a required target regardless of this
#: exclusion. No fourth exclusion may be added to make a red run green.
NAMED_EXCLUSIONS = {
    "155-RESEARCH.md": (
        "researcher-authored input enumerating the forbidden phrasings in "
        "order to forbid them, and quoting the defective preserved-"
        "reference comment as evidence"
    ),
    "155-PATTERNS.md": (
        "same reason as 155-RESEARCH.md, plus it quotes the defective "
        "comment verbatim as the text to rewrite"
    ),
    "155-VALIDATION.md": (
        "the file that DEFINES the forbidden list and carries the "
        "mandated correct phrasing; excluded from the negative half for "
        "that reason and no other"
    ),
}

#: A paragraph is in scope for the negative scan iff it names this token.
TRIGGER_TOKENS = ("rurp_read_voltage_mv",)

#: Non-vacuity floor -- see 155-dead05-phrasing-corpus.md section 7 for the
#: by-construction justification of this exact number.
PARAGRAPH_FLOOR = 6

#: The four required-positive targets, same "firestarter/" prefix
#: convention as CORPUS_GLOBS. Each must carry CORRECT_PHRASING.
REQUIRED_POSITIVE_TARGETS = (
    ".planning/phases/"
    "155-dead-weight-removal-the-heap-allocator-and-the-64-bit-runtim/"
    "155-VALIDATION.md",
    ".planning/milestones/v1.33-artifacts/155-after-figures.md",
    "firestarter/src/boards/rurp_common.cpp",
    "firestarter/tests/test_voltage_reformulation_oracle.py",
)

#: The mandated correct phrasing (155-VALIDATION.md item 5), stored already
#: whitespace-normalised (single spaces, one line) so it can be compared
#: directly against a normalised target file's text.
CORRECT_PHRASING = (
    "proven by a committed host-side numerical oracle over a stated input "
    "grid, bound to the shipped C by a source-contract scan; no native and "
    "no bench coverage exists."
)

_PARA_SPLIT_RE = re.compile(r"(\n{2,})")


# ---------------------------------------------------------------------------
# The six forbidden phrasings, built by concatenation
# ---------------------------------------------------------------------------
def _forbidden_needles():
    """Build each of the six forbidden phrasings (155-VALIDATION.md item 5)
    from concatenated fragments, so this module's own source text cannot
    literally contain a needle it exists to detect. `.planning/milestones/v1.33-artifacts/tools/`
    is outside the corpus by construction (TOOLS_DIR_REL, never descended
    into), so this is belt-and-braces rather than strictly required -- but
    it also means the pytest and the planted fixture can reference these
    needles through this same function instead of each hard-coding a second
    literal copy that could silently drift from the first."""
    return (
        "test" + "ed",
        "unit-" + "test" + "ed",
        "covered" + " by native",
        "verified" + " on hardware",
        "bench-" + "verified",
        "proven" + " at runtime",
    )


# ---------------------------------------------------------------------------
# Text normalisation and paragraph splitting
# ---------------------------------------------------------------------------
def _normalise(text):
    """Collapse whitespace runs to a single space, and strip a single
    leading C/Python comment leader (`*`, `//` or `#`) from each line before
    joining -- required because the mandated phrasing must be readable
    whether it appears inside a C block comment, a `//`-commented block, a
    Python docstring or plain Markdown prose, and because a sentence wrapped
    across several comment lines must still read as one contiguous
    sentence."""
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            stripped = stripped[2:].strip()
        elif stripped.startswith("*"):
            stripped = stripped[1:].strip()
        elif stripped.startswith("#"):
            stripped = stripped[1:].strip()
        cleaned_lines.append(stripped)
    joined = "\n".join(cleaned_lines)
    return re.sub(r"\s+", " ", joined).strip()


def _paragraphs(text):
    """Split on runs of two or more newlines. Returns a list of
    (start_line, raw_paragraph_text) pairs, where start_line is the 1-based
    line number of the paragraph's first line in the ORIGINAL (unstripped)
    text, so a reported violation can be anchored precisely."""
    result = []
    pos = 0
    for token in _PARA_SPLIT_RE.split(text):
        if _PARA_SPLIT_RE.fullmatch(token):
            pos += len(token)
            continue
        if token.strip() != "":
            start_line = text.count("\n", 0, pos) + 1
            result.append((start_line, token))
        pos += len(token)
    return result


# ---------------------------------------------------------------------------
# Corpus resolution
# ---------------------------------------------------------------------------
def _split_root(pattern, corpus_root, fw_root):
    """Return (root, relative_glob_or_path) for a CORPUS_GLOBS /
    REQUIRED_POSITIVE_TARGETS entry, using the "firestarter/" prefix
    convention -- present means --fw-root, absent means --corpus-root."""
    prefix = "firestarter/"
    if pattern.startswith(prefix):
        return fw_root, pattern[len(prefix):]
    return corpus_root, pattern


def _under_tools_dir(path, corpus_root):
    tools_dir = (corpus_root / TOOLS_DIR_REL).resolve()
    try:
        path.resolve().relative_to(tools_dir)
        return True
    except ValueError:
        return False


def _resolve_corpus_files(corpus_root, fw_root):
    """Expand every CORPUS_GLOBS entry, dropping the three NAMED_EXCLUSIONS
    by basename and dropping anything under TOOLS_DIR_REL, so this module's
    own source, its pytest and its planted fixture can never enter the
    corpus they judge. A glob that currently matches nothing (a corpus
    member not yet authored -- see 155-dead05-phrasing-corpus.md section 8's
    "not yet exist" note) contributes zero files, silently, which is
    distinct from a required-positive target missing from disk."""
    resolved = []
    for pattern in CORPUS_GLOBS:
        root, rel_pattern = _split_root(pattern, corpus_root, fw_root)
        for candidate in sorted(root.glob(rel_pattern)):
            if not candidate.is_file():
                continue
            if candidate.name in NAMED_EXCLUSIONS:
                continue
            if _under_tools_dir(candidate, corpus_root):
                continue
            resolved.append(candidate)
    seen = set()
    unique = []
    for candidate in resolved:
        key = str(candidate.resolve())
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------
def _scan_file(path, needles, patterns):
    """Scan one file's paragraphs. Returns (in_scope_count, violations),
    where each violation is a dict naming file, start line, the needle
    matched, and the offending normalised paragraph."""
    text = path.read_text(encoding="utf-8")
    in_scope = 0
    violations = []
    for start_line, raw_paragraph in _paragraphs(text):
        normalised = _normalise(raw_paragraph)
        if not any(token in normalised for token in TRIGGER_TOKENS):
            continue
        in_scope += 1
        for needle, pattern in zip(needles, patterns):
            if pattern.search(normalised):
                violations.append(
                    {
                        "file": str(path),
                        "line": start_line,
                        "needle": needle,
                        "paragraph": normalised,
                    }
                )
    return in_scope, violations


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def _print_pass(file_counts, total_in_scope, target_paths):
    print(
        f"PASS: {len(file_counts)} file(s) scanned, {total_in_scope} "
        f"in-scope paragraph(s) found (floor {PARAGRAPH_FLOOR})"
    )
    for path, count in file_counts:
        print(f"  {path}: {count} in-scope paragraph(s)")
    for target_path in target_paths:
        print(f"  required target OK (mandated phrasing present): {target_path}")


def _print_fail(header, lines):
    print(f"FAIL: {header}")
    for line in lines:
        print(f"  {line}")


# ---------------------------------------------------------------------------
# Argument parsing -- manual, no argparse
# ---------------------------------------------------------------------------
def _argv_error(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def _parse_argv(argv):
    """Manual parser (no argparse). Recognises --corpus-root PATH (default:
    the meta repo root derived from this file's own location, never from
    the caller's cwd) and --fw-root PATH (default: <corpus-root>/
    firestarter). Any unknown flag, or a recognised flag missing its value,
    is a malformed invocation -- exit 2."""
    corpus_root = None
    fw_root = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--corpus-root":
            if i + 1 >= len(argv):
                _argv_error(f"{arg} requires a value")
            corpus_root = argv[i + 1]
            i += 2
            continue
        if arg == "--fw-root":
            if i + 1 >= len(argv):
                _argv_error(f"{arg} requires a value")
            fw_root = argv[i + 1]
            i += 2
            continue
        _argv_error(f"unrecognized argument: {arg}")
    return corpus_root, fw_root


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
#: Three parents up from this file's own directory (tools -> v1.33 ->
#: .planning -> meta repo root). Never derived from the caller's cwd.
_DEFAULT_CORPUS_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    corpus_root_arg, fw_root_arg = _parse_argv(argv)

    corpus_root = (
        Path(corpus_root_arg).resolve() if corpus_root_arg else _DEFAULT_CORPUS_ROOT
    )
    fw_root = Path(fw_root_arg).resolve() if fw_root_arg else (corpus_root / "firestarter")

    resolved = _resolve_corpus_files(corpus_root, fw_root)
    print(f"Resolved corpus ({len(resolved)} file(s)):")
    for candidate in resolved:
        print(f"  {candidate}")

    needles = _forbidden_needles()
    patterns = [re.compile(r"\b" + re.escape(needle) + r"\b", re.IGNORECASE) for needle in needles]

    total_in_scope = 0
    file_counts = []
    all_violations = []
    for candidate in resolved:
        in_scope, violations = _scan_file(candidate, needles, patterns)
        total_in_scope += in_scope
        file_counts.append((str(candidate), in_scope))
        all_violations.extend(violations)

    if all_violations:
        lines = [
            f"{v['file']}:{v['line']} -- needle {v['needle']!r} in "
            f"paragraph: {v['paragraph']}"
            for v in all_violations
        ]
        _print_fail(
            f"{len(all_violations)} forbidden-phrasing violation(s) found",
            lines,
        )
        return 1

    if total_in_scope < PARAGRAPH_FLOOR:
        print(
            f"ERROR: only {total_in_scope} in-scope paragraph(s) found "
            f"(< PARAGRAPH_FLOOR={PARAGRAPH_FLOOR}) -- cannot render a "
            "verdict; a shrunken or renamed corpus must fail closed, not "
            "report success"
        )
        for path, count in file_counts:
            print(f"  {path}: {count}")
        return 2

    target_ok = []
    for target_pattern in REQUIRED_POSITIVE_TARGETS:
        root, rel_path = _split_root(target_pattern, corpus_root, fw_root)
        target_path = root / rel_path
        if not target_path.is_file():
            print(
                f"ERROR: required positive target missing from disk: "
                f"{target_path}"
            )
            return 2
        target_text = _normalise(target_path.read_text(encoding="utf-8"))
        if CORRECT_PHRASING not in target_text:
            _print_fail(
                "required positive target does not contain the mandated "
                "phrasing",
                [str(target_path)],
            )
            return 1
        target_ok.append(str(target_path))

    _print_pass(file_counts, total_in_scope, target_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
