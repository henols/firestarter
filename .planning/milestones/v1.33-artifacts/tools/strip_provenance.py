#!/usr/bin/env python3
"""Fail-closed provenance-token stripper for comment/docstring text.

WHY A TOOL AND NOT A REGEX SED
------------------------------
The v1.33 firmware sweep was done by hand, and two defects still slipped
through and were caught only by a block-level hygiene check: an opening paren
removed while its closing partner survived on the next line
(`include/rurp_vpp.h`), and a substitution that left a dangling `(157-03,`
(`include/firestarter.h`). Both are the same failure -- a strip that is not
aware of the punctuation it is dissolving.

So this tool refuses to be clever. It rewrites ONLY shapes it can prove safe,
counts everything it declines, and never edits a line it does not fully
understand. A residue it leaves is a reviewable list; a residue a sed leaves is
a broken comment.

SAFE SHAPES (the only ones rewritten)
-------------------------------------
1. A parenthetical whose ENTIRE content is provenance tokens plus separators:
       `... already PADDED (D-09). ...`   -> `... already PADDED. ...`
       `... wire (Phase 149, PGSZ-01/PGSZ-02); ...` -> `... wire; ...`
   The preceding whitespace goes with it. Requires the parenthetical to open
   and close on the SAME line -- a multi-line parenthetical is declined,
   because that is exactly the case that produced the rurp_vpp.h defect.

2. A provenance token inside a LARGER parenthetical, removed with its list
   separator only:
       `(FLAG_SKIP_SDP_UNLOCK, D-12)` -> `(FLAG_SKIP_SDP_UNLOCK)`
   Only when at least one non-provenance item remains.

3. A trailing `per <tokens>` / `see <tokens>` clause with nothing after it:
       `... sentinel per D-07.` -> `... sentinel.`

EVERYTHING ELSE IS DECLINED, including any line where a token is the subject of
a sentence ("Phase 141 rewrote eprom_write_execute as ..."), because removing it
changes what the sentence claims and only a human can judge the replacement.

EXEMPTIONS
----------
`CAP-0N` is never stripped: SWEEP-02 exempts it as live cross-repo
wire-protocol vocabulary referenced from both repos' shipped source.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load_survey():
    spec = importlib.util.spec_from_file_location("survey_provenance", _HERE / "survey_provenance.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_SP = _load_survey()

# CAP-0N is exempt (SWEEP-02); everything else the detector knows is fair game.
_EXEMPT = re.compile(r"\bCAP-0\d\b")
_TOKEN = _SP._REGEX_INLINE

# Separators that may appear BETWEEN provenance tokens inside a parenthetical
# without making that parenthetical "prose".
_SEP = r"[\s,;/&+]|and|as amended|amended|,|\.\.|--"
_ONLY_TOKENS = re.compile(rf"^(?:\s*(?:{_TOKEN.pattern})\s*(?:{_SEP})*)+$")


def _is_pure_provenance(inner: str) -> bool:
    """True when `inner` is provenance tokens and separators, nothing else."""
    if not inner.strip():
        return False
    if _EXEMPT.search(inner):
        return False
    stripped = _TOKEN.sub("", inner)
    stripped = re.sub(r"\b(and|as amended|amended|per|see)\b", "", stripped)
    return re.fullmatch(r"[\s,;/&+.\-]*", stripped) is not None


def transform_line(line: str) -> tuple[str, int, int]:
    """Return (new_line, n_removed, n_declined) for one comment-bearing line."""
    if not _TOKEN.search(line):
        return line, 0, 0
    removed = 0
    out = line

    # Shape 1: a same-line parenthetical that is entirely provenance.
    def _paren(m: re.Match) -> str:
        nonlocal removed
        if _is_pure_provenance(m.group(1)):
            removed += 1
            return ""
        return m.group(0)

    # `(?<=\S)` is load-bearing: a bare `\s*\(` swallows a line's LEADING
    # INDENTATION when the parenthetical starts the line, which turned a
    # docstring line in serial_comm.py into `. 0-byte param region ...` and
    # took the CAP-03 parity gate to 0-of-6 facts found. A parenthetical that
    # opens a line has no preceding non-space, so it is now declined instead.
    out = re.sub(r"(?<=\S)[ \t]*\(([^()]*)\)", _paren, out)

    # Shape 3: a trailing `per|see <tokens>` clause ending the sentence.
    def _per(m: re.Match) -> str:
        nonlocal removed
        if _is_pure_provenance(m.group(2)):
            removed += 1
            return m.group(3)
        return m.group(0)

    out = re.sub(rf"(\s+)\b(?:per|see)\s+((?:{_TOKEN.pattern}|[\s,/&+]|and)+?)([.;,]|\s*$)", _per, out)

    # Shape 2: a token inside a larger parenthetical, with its list separator.
    def _inner(m: re.Match) -> str:
        nonlocal removed
        inner = m.group(1)
        if _EXEMPT.search(inner) or not _TOKEN.search(inner):
            return m.group(0)
        new = re.sub(rf",\s*(?:{_TOKEN.pattern})(?=[,)]|$)", "", inner)
        new = re.sub(rf"^(?:{_TOKEN.pattern})\s*,\s*", "", new)
        if new != inner and new.strip() and _TOKEN.search(inner) and not _TOKEN.search(new):
            removed += 1
            return "(" + new + ")"
        return m.group(0)

    out = re.sub(r"\(([^()]*)\)", _inner, out)

    # Shape 4: a TRAILING comment fragment that is nothing but provenance,
    # e.g. `x = f()  # type: ignore[union-attr]  # Phase 42 D-06`. Only the
    # last `#`-introduced run is considered, and only when everything after it
    # is tokens and separators -- so a real trailing note is never lost.
    def _trailing(m: re.Match) -> str:
        nonlocal removed
        if _is_pure_provenance(m.group(2)):
            removed += 1
            return ""
        return m.group(0)

    out = re.sub(r"(\s+#\s*)([^#]*)$", _trailing, out)

    declined = 1 if _TOKEN.search(out) and not _EXEMPT.search(out) else 0
    return out, removed, declined


# Files pinned by a committed golden sidecar's `meta.blob_shas`, with no
# regeneration tool in-repo. `protocol_branch_inventory.json`'s `sites` array is
# additionally LINE-BEARING and extracted from eprom.cpp, so a comment-only edit
# there still invalidates it. Ruling B exempted these; editing one silently
# turns a gate RED for a reason a reader would misdiagnose as a sweep defect.
_BLOB_PINNED = frozenset({
    "src/proms/eprom.cpp",
    "include/eprom_params.h",
    "test/native/avr/_shared/eprom_v131_expected.h",
    "test/native/avr/_shared/sdp_expected.h",
})


def is_blob_pinned(path: Path) -> bool:
    parts = path.as_posix()
    return any(parts.endswith(p) for p in _BLOB_PINNED)


# A line carrying one of these markers sits inside a region whose BODY is
# SHA-pinned or otherwise frozen by protocol. `_read_and_parse_lines` in
# serial_comm.py is pinned by test_read_and_parse_lines_ringfence_unchanged,
# whose failure text says changes must be "flagged and deferred", NOT re-pinned
# -- so unlike the C-14 census this is a do-not-touch, and the tool must not
# quietly edit a comment inside it.
_RINGFENCE_MARKERS = ("ring-fenced", "ringfence", "RING-FENCED")


def ringfenced_lines(text: str) -> set[int]:
    """1-based line numbers inside a ring-fenced REGION, not merely the marker.

    A per-line marker check is not enough: the marker sits in the function's
    docstring, while the comments a sweep would edit are 60 lines further down
    with no marker of their own. Three such lines inside
    `_read_and_parse_lines` were edited and broke its pinned-SHA gate.

    So: find each marker, walk BACK to the enclosing `def` (the nearest
    preceding line at a shallower indent that starts a definition), then
    protect forward until the indentation returns to that def's level.
    """
    lines = text.split("\n")
    protected: set[int] = set()
    for i, line in enumerate(lines):
        if not any(mk in line for mk in _RINGFENCE_MARKERS):
            continue
        start = i
        for j in range(i, -1, -1):
            st = lines[j].lstrip()
            if st.startswith(("def ", "async def ", "class ")):
                start = j
                break
        base = len(lines[start]) - len(lines[start].lstrip())
        end = len(lines)
        for k in range(start + 1, len(lines)):
            st = lines[k].strip()
            if not st:
                continue
            indent = len(lines[k]) - len(lines[k].lstrip())
            if indent <= base:
                end = k
                break
        protected.update(range(start + 1, end + 1))
    return protected


def process(path: Path, apply: bool, allow_pinned: bool = False) -> tuple[int, int, list[tuple[int, str]]]:
    if is_blob_pinned(path) and not allow_pinned:
        return 0, 0, []
    text = path.read_text(encoding="utf-8")
    comment_lines = set(_SP._comment_lines(path, text))
    fenced = ringfenced_lines(text)
    lines = text.split("\n")
    removed = 0
    residue: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        ln = i + 1
        if ln not in comment_lines:
            continue
        if ln in fenced:
            # Declined, not silently edited: a frozen body's comment is frozen.
            if _TOKEN.search(line) and not _EXEMPT.search(line):
                residue.append((ln, line.strip()[:110]))
            continue
        new, n, dec = transform_line(line)
        # Never let a rewrite touch a line's code half: only accept the change
        # when everything removed came from inside comment text.
        if new != line:
            lines[i] = new
            removed += n
        if dec:
            residue.append((ln, lines[i].strip()[:110]))
    if apply and removed:
        path.write_text("\n".join(lines), encoding="utf-8")
    return removed, len(residue), residue


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--show-residue", action="store_true")
    ap.add_argument(
        "--allow-blob-pinned",
        action="store_true",
        help=(
            "DELIBERATE OVERRIDE: also edit the blob-SHA-pinned files. The caller "
            "then OWNS re-deriving every affected sidecar -- both meta.blob_shas "
            "and, for protocol_branch_inventory.json, the line-bearing sites[] "
            "array extracted from eprom.cpp. Without that follow-up this turns "
            "gates RED for a reason a reader would misdiagnose as a sweep defect."
        ),
    )
    args = ap.parse_args(argv)

    files: list[Path] = []
    for a in args.paths:
        p = Path(a)
        files.extend([p] if p.is_file() else sorted(q for q in p.rglob("*") if q.suffix in _SP._EXTENSIONS))
    files = [f for f in files if "__pycache__" not in f.parts]

    tot_r = tot_d = 0
    for f in files:
        r, d, residue = process(f, args.apply, allow_pinned=args.allow_blob_pinned)
        if r or d:
            print(f"{f}: removed {r}, declined {d}")
            if args.show_residue:
                for ln, txt in residue:
                    print(f"    {ln}: {txt}")
        tot_r += r
        tot_d += d
    print(f"\n{'APPLIED' if args.apply else 'DRY RUN'}: removed {tot_r}, declined {tot_d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
