#!/usr/bin/env python3
r"""
Provenance-comment corpus survey — the SWEEP-03 post-sweep oracle and the
SWEEP-06 hit-count oracle for Phase 154 (dual-repo provenance comment sweep).

Given the two sub-repo roots as explicit positional arguments (`fw_root` for
`firestarter`, `app_root` for `firestarter_app` — NEVER derived from
`__file__`, per D-09 / reference_check_permitted_claims_here_resolves_wrong_phase_dir),
this tool counts every comment/preprocessor line across both repos that opens
with a GSD provenance token, grouped into seven named corpus groups, and
reports the counts on demand so every hit-count criterion in this phase
resolves to one committed command instead of an assertion.

THE REGEX (research's reconstruction, stated verbatim so a future reader can
see exactly what "a hit" means):

    (//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)

Two of the eleven alternations, `P\d{3}` and `REQ-`, match **nothing** on
`beta` (research measured 0 each) — their presence is historical and no
triage effort is budgeted for them.

CORPUS DEFINITION — what is NOT a hit
--------------------------------------
The regex requires the provenance token to sit **immediately after** a
comment opener (`//`, `/*`, a `*`-continuation line, or `#`). Consequences:

  (a) Python **docstrings** are outside the corpus entirely — a docstring
      line does not open with `#`, so no docstring line can ever match,
      regardless of how dense its prose is with provenance tokens.
  (b) A token sitting deeper inside a comment line (not immediately after
      the opener) is not itself a hit on that occurrence.

Measured consequence: `firestarter_app/tests/scan_paths.py` carries **zero**
regex hits even though its module docstring is dense with `D-11` / `A-7` /
`C-8` / `BASE-02` / `Phase 123 Plan 08` labels — a token-anywhere scan over
the app's `.py` files finds about 2,657 further token lines across ~173
files. Extending the sweep there is deliberately NOT done: no measurement
backs a corpus that size, D-03 retains exactly those IDs in test files where
they are the case's traceability key, and several gates assert docstring
content. Consequence for D-04's named keep-in-full case:
`scan_paths.py` is kept in full by **not being edited at all** — recorded
here rather than silently skipped.

GROUPS
------
  fw-src      firestarter/src
  fw-include  firestarter/include
  fw-test     firestarter/test
  fw-lib      firestarter/lib            (measured: 0 files / 0 hits)
  app-pkg     firestarter_app/firestarter
  app-tests   firestarter_app/tests
  app-tools   firestarter_app/tools

Source extensions scanned: .cpp .c .h .hpp .ino .py

EXIT CODES (house 0/1/2 convention)
------------------------------------
  0 — measured and reported (or, under --assert-tokens-zero, no violation).
  1 — a real violation: --assert-tokens-zero found at least one hit line for
      the given token class still present in the selected scope.
  2 — infrastructure: a root argument does not exist / is not a directory;
      an EXPLICITLY selected --group's directory carries zero candidate
      source files (a legitimately empty group like fw-lib is only "0" when
      it is scanned as part of the full, unfiltered corpus — requesting it
      BY NAME and finding nothing is an infrastructure problem, not a
      measurement); or the corpus scanned this run produced zero hit lines
      in total. Silence is never success.

PATH SAFETY (ASVS V5)
----------------------
`--group` only accepts one of the seven fixed group names above (enforced by
argparse `choices`), so no filesystem path, `..` segment, or absolute path
can ever reach this tool through that argument. Every candidate file found
under a group's directory is independently resolved and asserted to still
live under its repo root before being counted, so a symlink cannot walk the
scan outside the two explicit root arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixed group -> (which root, relative subdirectory) map. Deliberately a
# closed set: --group's argparse `choices` is drawn from this dict's keys,
# so no path-shaped value can ever be accepted here.
# ---------------------------------------------------------------------------
_GROUPS: dict[str, tuple[str, str]] = {
    "fw-src": ("fw", "src"),
    "fw-include": ("fw", "include"),
    "fw-test": ("fw", "test"),
    "fw-lib": ("fw", "lib"),
    "app-pkg": ("app", "firestarter"),
    "app-tests": ("app", "tests"),
    "app-tools": ("app", "tools"),
}

_EXTENSIONS = {".cpp", ".c", ".h", ".hpp", ".ino", ".py"}

# The corpus regex, verbatim per research's reconstruction (see module
# docstring). re.MULTILINE is irrelevant here since matching is done
# per-line, but ^ is kept anchored to line start via per-line application.
_REGEX_ANCHORED = re.compile(
    r"(//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)"
)

# Backwards-compatible alias: every pre-2026-08-24 caller and every figure
# recorded in `.planning/` was produced by this pattern. Kept so those numbers
# stay reproducible via --legacy-anchored; NOT the default any more.
_REGEX = _REGEX_ANCHORED

# ---------------------------------------------------------------------------
# CORRECTED DETECTOR (2026-08-24, post-v1.33-close finding)
#
# _REGEX_ANCHORED requires the provenance token to sit immediately after the
# comment opener. Measured consequence: it reports 43 hit lines in shipped
# source where a comment-context-aware scan finds 466, and it reproduces
# SWEEP-03's "34 -> 4 across 1 file" D-# claim only because a mid-line `D-02`
# is invisible to it (mid-line aware: 87 across 21 files).
#
# The fix separates the two questions the old regex conflated:
#   1. Is this text COMMENT-or-DOCSTRING context?  (structural, per language)
#   2. Does that text contain a provenance token?  (anywhere within it)
#
# REQUIREMENT FAMILIES ARE DERIVED, NEVER INVENTED. The list below is
# generated from `.planning/milestones/*REQUIREMENTS*.md` -- the project's own
# authoritative requirement records -- not hand-guessed. The old fixed list
# named 5 families (REQ-, CAP-0, D-#, WR-#, LOOP-#); the project has 96.
# ---------------------------------------------------------------------------

_REQUIREMENT_FAMILIES: tuple[str, ...] = (
    "ADPT", "ALIAS", "BASE", "BENCH", "CAP", "CAPS",
    "CFG", "CHAN", "CLI", "CLOSE", "CRC", "DATA",
    "DB", "DEAD", "DEC", "DECODE", "DEDUP", "DEVTEST",
    "DIFF", "DISP", "DOC", "DSHEET", "E2E", "ERASE",
    "ERR", "EVEN", "EVID", "FIX", "FRAME", "FUT",
    "FW", "GAP", "GATE", "GRAD", "HARD", "HARN",
    "HOST", "INBOX", "INST", "ISSUE", "LAND", "LCAT",
    "LCI", "LEDGER", "LEG", "LEGACY", "LFW", "LHOST",
    "LMIG", "LOCK", "LOOP", "MERGE", "MS", "NAME",
    "NMOS", "OBS", "ONBOARD", "OUT", "PATT", "PCB",
    "PGSZ", "PIN", "PRE", "PREP", "PRIM", "PROV",
    "RCA", "REL", "RELOCK", "REMAP", "REPRO", "RETIRE",
    "REWR", "RPT", "RSCH", "SAFE", "SERIAL", "SILK",
    "STRUCT", "SUB", "SWEEP", "TABLE", "TEST", "TOOL",
    "TRACE", "UV", "VAL", "VAR", "VER", "VERIFY",
    "VOLT", "VPP", "WIRE", "XACT", "XIC", "XPORT",
)

# `-\d{2}` (never `-\d`) is load-bearing: it keeps ordinary hyphenated prose
# and domain tokens (`CRC-8`, `RS-232`) out of the corpus.
_FAMILY_ALT = "|".join(_REQUIREMENT_FAMILIES)

_INLINE_TOKEN_SRC = (
    r"\b(?:Task\s+\d+|Phase\s+\d+|Plan\s+\d{2}|P\d{3}\b|REQ-\d+"
    # `D-A`..`D-F` exist alongside `D-01`..`D-25`: letter-suffixed decision ids.
    r"|D-(?:\d{1,2}|[A-Z])\b|\d{3}-(?:CONTEXT|RESEARCH|PLAN|SUMMARY|VERIFICATION)"
    # Bare phase-plan references: `154-12`, `119-07`, `157-03`. Found by the
    # stripper's own RED test -- `(157-03, DECODE-04)` was only ever detected
    # via DECODE-04, so a plan reference standing alone was invisible.
    # Plan/task references. Deliberately NOT a bare `\d{2,3}-\d{2}`: sampling
    # showed that shape swallows dates (`2026-05-26` -> `05-26`), numeric
    # ranges (`~20-60 us`, `occupy 11-15`) and file line ranges
    # (`rurp_shield.h:25-94`). So the bare form is restricted to a THREE-digit
    # phase, which no date or range in this corpus produces, and the two-digit
    # phases are reachable only through their explicit `T-` / `plan ` prefixes.
    r"|T-\d{2,3}-\d{2}\b"
    # Tag shapes found in the app package's prose during the 2026-08-25 sweep:
    # a quick-task id, a milestone tag, and a bare RESEARCH/ROADMAP pointer.
    r"|quick[- ]task\s+\d{6}-[a-z0-9]+"
    r"|\bv\d+\.\d{2}\b"
    r"|\b(?:RESEARCH|ROADMAP|CONTEXT|PATTERNS)\.md\b"
    r"|\b(?:RESEARCH|ROADMAP)\s*§"
    r"|\b[Pp]lans?\s+\d{2,3}-\d{2}\b"
    r"|(?<!\d-)(?<![:\d.])\b\d{3}-\d{2}\b"
    r"|(?:" + _FAMILY_ALT + r")-\d{2}\b)"
)
_REGEX_INLINE = re.compile(_INLINE_TOKEN_SRC)


def _c_comment_text(text: str) -> dict[int, str]:
    """Map 1-based line number -> the COMMENT-ONLY text on that line.

    A hand-rolled scanner rather than a regex, because `//` inside a string
    literal is not a comment and `"SWEEP-01"` in code must never count. Tracks
    string, char and block-comment state across lines.
    """
    out: dict[int, list[str]] = {}
    in_block = False
    in_str: str | None = None
    lineno = 1
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\n":
            lineno += 1
            i += 1
            in_str = None if in_str in ('"', "'") else in_str
            continue
        if in_block:
            if text.startswith("*/", i):
                in_block = False
                i += 2
            else:
                out.setdefault(lineno, []).append(ch)
                i += 1
            continue
        if in_str is not None:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = ch
            i += 1
            continue
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j == -1 else j
            out.setdefault(lineno, []).append(text[i:j])
            i = j
            continue
        if text.startswith("/*", i):
            in_block = True
            i += 2
            continue
        i += 1
    return {k: "".join(v) for k, v in out.items()}


def _py_comment_text(text: str) -> dict[int, str]:
    """Map 1-based line number -> comment/docstring text for Python.

    Uses `tokenize`, so `LABEL = "SWEEP-01"` (a value) is excluded while a
    docstring (`\"\"\"... (SWEEP-01).\"\"\"`) is included -- shipped prose either
    way. Falls back to a `#`-only scan if the file does not tokenize.
    """
    import io as _io
    import tokenize as _tok

    out: dict[int, list[str]] = {}
    try:
        toks = list(_tok.generate_tokens(_io.StringIO(text).readline))
    except (_tok.TokenError, IndentationError, SyntaxError):
        for ln, line in enumerate(text.splitlines(), start=1):
            h = line.find("#")
            if h != -1:
                out.setdefault(ln, []).append(line[h:])
        return {k: "".join(v) for k, v in out.items()}

    at_stmt_start = True
    for t in toks:
        if t.type == _tok.COMMENT:
            out.setdefault(t.start[0], []).append(t.string)
            continue
        if t.type == _tok.STRING and at_stmt_start:
            for off, piece in enumerate(t.string.splitlines()):
                out.setdefault(t.start[0] + off, []).append(piece)
        # NL (non-logical newline) is deliberately NOT here: inside brackets
        # tokenize emits NL for every physical line break, so treating it as a
        # statement start would classify each fragment of an implicitly
        # concatenated string literal as a docstring -- which wrongly counted
        # `diff_db.py:175` and `chip_test.py:3827`, both live code.
        if t.type in (_tok.NEWLINE, _tok.INDENT, _tok.DEDENT, _tok.ENCODING):
            at_stmt_start = True
        elif t.type != _tok.COMMENT:
            at_stmt_start = False
    return {k: "".join(v) for k, v in out.items()}


def _comment_lines(path: Path, text: str) -> dict[int, str]:
    if path.suffix == ".py":
        return _py_comment_text(text)
    return _c_comment_text(text)

# Named token classes for --assert-tokens-zero, each mapped to the single
# alternation it represents (same comment-opener prefix as _REGEX).
_TOKEN_CLASSES: dict[str, str] = {
    "Task": r"Task",
    "Phase": r"Phase",
    "Plan": r"Plan",
    "P###": r"P\d{3}",
    "Req": r"Req",
    "REQ-": r"REQ-",
    "CAP-0": r"CAP-0",
    "D-#": r"D-\d",
    "WR-#": r"WR-\d",
    "LOOP-#": r"LOOP-\d",
    "###-CONTEXT": r"\d{3}-CONTEXT",
}


_TOKEN_CLASSES["REQ-FAMILY"] = r"(?:" + _FAMILY_ALT + r")-\d{2}"


def _token_regex(label: str, legacy: bool = False) -> re.Pattern[str]:
    """Regex for one --assert-tokens-zero class.

    In the default (corrected) mode the token is matched ANYWHERE inside
    already-extracted comment/docstring text, so a mid-line `(D-02)` is a
    violation. In --legacy-anchored mode the historical comment-opener
    anchoring is reproduced exactly.
    """
    fragment = _TOKEN_CLASSES[label]
    if legacy:
        return re.compile(rf"(//|/\*|^\s*\*|#)\s*({fragment})")
    return re.compile(fragment)


def _scan_candidate_files(base: Path, repo_root: Path) -> list[Path]:
    """Every file under `base` with a scanned extension, resolved and
    asserted to still live under `repo_root` (ASVS V5 path-safety check).
    Returns an empty list if `base` does not exist -- that is a legitimate
    zero for an unfiltered run and an infrastructure error for an explicit
    one; the caller decides which."""
    if not base.is_dir():
        return []
    files: list[Path] = []
    for candidate in sorted(base.rglob("*")):
        if not candidate.is_file() or candidate.suffix not in _EXTENSIONS:
            continue
        resolved = candidate.resolve()
        try:
            resolved.relative_to(repo_root)
        except ValueError:
            print(
                f"ERROR: candidate path escapes its repo root, refusing: "
                f"{candidate} -> {resolved} (not under {repo_root})",
                file=sys.stderr,
            )
            sys.exit(2)
        files.append(candidate)
    return files


def _scan_hits(files: list[Path], repo_root: Path, legacy: bool = False) -> dict:
    """Per-file hit-line counts (and the raw (lineno, text) pairs, kept only
    in-process for --assert-tokens-zero -- never serialized to JSON)."""
    file_hits: dict[str, int] = {}
    file_hit_lines: dict[str, list[tuple[int, str]]] = {}
    total_hits = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"ERROR: cannot read {f}: {e}", file=sys.stderr)
            sys.exit(2)
        hits: list[tuple[int, str]] = []
        if legacy:
            for lineno, line in enumerate(text.splitlines(), start=1):
                if _REGEX_ANCHORED.search(line):
                    hits.append((lineno, line))
        else:
            # Two separate questions: is this comment/docstring context, and
            # does that context carry a provenance token. The scanned text
            # handed downstream is the COMMENT ONLY, so --assert-tokens-zero
            # can never fire on a token that lives in code.
            for lineno, ctext in sorted(_comment_lines(f, text).items()):
                if _REGEX_INLINE.search(ctext):
                    hits.append((lineno, ctext))
        if hits:
            rel = str(f.resolve().relative_to(repo_root))
            file_hits[rel] = len(hits)
            file_hit_lines[rel] = hits
            total_hits += len(hits)
    return {
        "candidate_files": len(files),
        "files": len(file_hits),
        "hits": total_hits,
        "file_hits": file_hits,
        "file_hit_lines": file_hit_lines,
    }


def _root_for(kind: str, fw_root: Path, app_root: Path) -> Path:
    return fw_root if kind == "fw" else app_root


def _print_group_table(per_group: dict[str, dict]) -> None:
    print(f"{'group':<12} {'candidate_files':>15} {'files_with_hits':>16} {'hits':>8}")
    for name in sorted(per_group):
        g = per_group[name]
        print(f"{name:<12} {g['candidate_files']:>15} {g['files']:>16} {g['hits']:>8}")


def _print_file_table(per_group: dict[str, dict]) -> None:
    print()
    print(f"{'group':<12} {'hits':>6}  file")
    for name in sorted(per_group):
        for rel, count in sorted(per_group[name]["file_hits"].items()):
            print(f"{name:<12} {count:>6}  {rel}")


def _json_group(g: dict) -> dict:
    return {
        "candidate_files": g["candidate_files"],
        "files": g["files"],
        "hits": g["hits"],
        "file_hits": g["file_hits"],
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "fw_root",
        help="firestarter (firmware) repo root -- explicit argument, NEVER derived from __file__",
    )
    ap.add_argument(
        "app_root",
        help="firestarter_app (host) repo root -- explicit argument, NEVER derived from __file__",
    )
    ap.add_argument(
        "--group",
        action="append",
        choices=sorted(_GROUPS),
        default=None,
        help="restrict to one or more named groups (repeatable); default is all seven groups",
    )
    ap.add_argument("--json", action="store_true", help="emit machine-readable per-group/per-file JSON")
    ap.add_argument(
        "--file-table", action="store_true", help="also print a per-file hit-count table"
    )
    ap.add_argument(
        "--legacy-anchored",
        action="store_true",
        help=(
            "reproduce the pre-2026-08-24 comment-opener-anchored detector exactly, "
            "so figures already recorded in .planning/ stay reproducible. It "
            "UNDERCOUNTS: it cannot see a mid-line token or any requirement family "
            "outside its fixed 5-name list."
        ),
    )
    ap.add_argument(
        "--assert-tokens-zero",
        metavar="TOKENCLASS",
        choices=sorted(_TOKEN_CLASSES),
        help="exit 1 if any hit line in the selected scope matches this token class, else 0",
    )
    args = ap.parse_args(argv)

    fw_root_arg = Path(args.fw_root)
    app_root_arg = Path(args.app_root)
    for label, root in (("fw_root", fw_root_arg), ("app_root", app_root_arg)):
        if not root.is_dir():
            print(
                f"ERROR: {label} does not exist or is not a directory: {root}",
                file=sys.stderr,
            )
            sys.exit(2)
    fw_root = fw_root_arg.resolve()
    app_root = app_root_arg.resolve()

    explicit_groups = args.group is not None and len(args.group) > 0
    selected = args.group if explicit_groups else sorted(_GROUPS)

    per_group: dict[str, dict] = {}
    for name in selected:
        kind, rel_subdir = _GROUPS[name]
        repo_root = _root_for(kind, fw_root, app_root)
        base = repo_root / rel_subdir
        candidates = _scan_candidate_files(base, repo_root)
        if explicit_groups and len(candidates) == 0:
            print(
                f"ERROR: group {name!r} matched 0 candidate source files under {base} "
                f"(explicit --group selection; an empty group found BY NAME is an "
                f"infrastructure problem, not a measurement).",
                file=sys.stderr,
            )
            sys.exit(2)
        per_group[name] = _scan_hits(candidates, repo_root, legacy=args.legacy_anchored)

    total_files = sum(g["candidate_files"] for g in per_group.values())
    total_hits = sum(g["hits"] for g in per_group.values())

    if total_hits == 0:
        print(
            "ERROR: the scanned corpus produced zero hit lines across all selected "
            "groups -- silence is never success.",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.assert_tokens_zero:
        token_re = _token_regex(args.assert_tokens_zero, legacy=args.legacy_anchored)
        violations: list[tuple[str, str, int, str]] = []
        for name in selected:
            for rel, lines in per_group[name]["file_hit_lines"].items():
                for lineno, text in lines:
                    if token_re.search(text):
                        violations.append((name, rel, lineno, text))
        if violations:
            print(
                f"FAIL: --assert-tokens-zero {args.assert_tokens_zero!r} found "
                f"{len(violations)} hit line(s) in scope {selected}:",
                file=sys.stderr,
            )
            for name, rel, lineno, text in violations[:20]:
                print(f"  {name}:{rel}:{lineno}: {text.strip()}", file=sys.stderr)
            if len(violations) > 20:
                print(f"  ... and {len(violations) - 20} more", file=sys.stderr)
            print(f"Total: {len(violations)} violation(s). Exit 1 (BLOCK).", file=sys.stderr)
            sys.exit(1)
        print(
            f"PASS: --assert-tokens-zero {args.assert_tokens_zero!r} -- 0 hit lines in "
            f"scope {selected} ({total_files} candidate files, {total_hits} total corpus "
            f"hit lines examined)."
        )
        sys.exit(0)

    if args.json:
        out = {name: _json_group(g) for name, g in per_group.items()}
        out["summary"] = {
            "candidate_files": total_files,
            "hits": total_hits,
            "groups_selected": selected,
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        sys.exit(0)

    _print_group_table(per_group)
    if args.file_table:
        _print_file_table(per_group)
    print()
    print(
        f"PASS: measured {total_files} candidate files, {total_hits} hit lines "
        f"across {len(selected)} group(s)."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
