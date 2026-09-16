#!/usr/bin/env python3
r"""
Pre-sweep citation-manifest generator -- milestone v1.33, Phase 154 plan 04
(SWEEP-09, SWEEP-10, D-07, D-08, D-09, Ruling F).

WHAT THIS PRODUCES AND WHY IT CANNOT BE REBUILT LATER
------------------------------------------------------
`.planning/milestones/v1.33-artifacts/sweep-citation-manifest.jsonl` is the ONLY interface between
Phase 154 and Phase 159. Phase 159's round-trip oracle is: *for every
non-retarget record, the text at `target_file_resolved:target_line` after the
remap equals the manifest's `source_text`.* After the sweep lands, the
pre-sweep (line, text) pairs exist nowhere on disk, so the manifest is
NOT reconstructible. If its schema is wrong, REMAP-02's oracle has no input.

D-07 records EVERY citation that targets a candidate swept file, not only the
subset predicted to shift, so Phase 159 can PROVE the others did not move
instead of assuming it.

THE ORDERING PROBLEM, AND HOW IT IS RESOLVED
---------------------------------------------
The manifest is a PRE-sweep deliverable, but "targets a swept file" is only
knowable AFTER the sweep. The two are satisfiable because they are answered by
two different sets:

  * CANDIDATE set (knowable pre-sweep, and what this tool uses): every file
    under the sweep globs carrying at least one provenance hit, as measured by
    `survey_provenance.py` (plan 02) -- called, never re-implemented.
  * ACTUAL swept set (post-sweep): the files with a non-empty diff.

The manifest is generated over the CANDIDATE set, so "targets a swept file" is
interpreted as "targets a CANDIDATE swept file". That is a deliberate
over-approximation and it is strictly better for Phase 159: recording a
citation into a file that turns out untouched is harmless, because its
`source_text` still matches at its recorded line and the fixed-point check
makes the row a no-op. The resolution is restated in the manifest's own header
record so a Phase 159 reader is not left to guess.

THE FOUR LIVE SYNTAX VARIANTS (research R2)
--------------------------------------------
  colon_single  `eeprom_28c.cpp:199`         6,253 total / 4,949 swept-targeting
  colon_range   `database.py:580-630`        6,068 / 4,771  -- 48% of the corpus
  anchor_L      `[x](notes/f.py#L42-L51)`      407 / 75
  colon_list    `hardware.py:39,153`           274 / 194

A BACKTICKED form is a WRAPPER, not a fifth variant -- the inner text matches
the colon form, so the wrapper needs no separate handling. `colon_list` is two
independent POINT citations sharing one path, never a range, so it yields one
record per element. The `anchor_L` variant is emitted under two variant labels,
`anchor_L` (point) and `anchor_L_range` (range), so that a consumer can test
"is this a range record?" on the variant alone; their sum is the 407 figure.

SCHEMA -- D-07's field list plus five stated ADDITIONS
------------------------------------------------------
D-07 named: planning_file, planning_line, target_file, target_line,
target_line_end, source_text, source_text_end, retarget.

Additions, each treated as a schema addition rather than a silent change:
  1. `target_file_cited` + `target_file_resolved` (replacing D-07's single
     `target_file`) -- 56% of citations are bare basenames, so Phase 159 cannot
     open the file from the as-cited string alone, and it needs the as-cited
     string to find the text to rewrite. Both are required.
  2. `resolution` -- which of the five-step rule's classes bound the row.
     Without it an ambiguous or unresolved row is indistinguishable from a
     resolved one, and a generator that silently dropped them would be
     indistinguishable from one that is broken (T-154-14).
  3. `resolution_reason` -- HOW that class was reached, so an ambiguous
     basename's decision is recorded per row and not just per count.
  4. `variant` -- which syntax form produced the row.
  5. `text_status` / `text_status_end` -- REQUIRED because `source_text` cannot
     be null. Phase 159's range half asserts every range record carries both
     `source_text` and `source_text_end`, so an unresolved or past-EOF endpoint
     must still carry a STRING. It carries the declared sentinel
     `<UNREADABLE>`, and `text_status` says authoritatively why. A row whose
     `text_status` is not `read` is skipped by the oracle BY NAME rather than
     failing open on it.

JSONL CONVENTION -- STATED, NOT INHERITED
------------------------------------------
No JSONL file exists anywhere in the three repos, so there is no in-repo
convention to inherit. This tool's convention, restated in the header record:
one JSON object per line; LF terminators; UTF-8 with `ensure_ascii=False`; keys
emitted in the fixed declared order (never sorted); the FIRST line a header
record under the single key `_schema`; `source_text` stored WITHOUT its line
terminator, to be compared against `splitlines()` output. No timestamp is
recorded anywhere, so regeneration over an unchanged tree is byte-identical.
The file is written atomically (temp file plus `os.replace`), per ASVS V12, so
an interrupted run cannot leave a partial manifest in place.

EXPLICIT ROOTS (D-09)
----------------------
The meta-repo root is a REQUIRED POSITIONAL argument and both sub-repo roots
are required options. Nothing here is derived from `__file__`. A root derived
from a tool's own location scans nothing and exits 0 when the tool is moved --
the fail-open shape this whole phase's controls exist to avoid. `--out` has no
default: an absent `--out` is an error, not a guess.

EXIT CODES (house 0/1/2 convention)
------------------------------------
  0 -- manifest written and its serialize-then-scan self-check passed.
  1 -- a real violation: the written manifest failed its own self-check (a
       missing required key, a range record missing an endpoint or an endpoint
       text, an unhandled variant, or a `retarget: true` row in what must be an
       all-false pre-sweep manifest).
  2 -- infrastructure: a root or scan directory does not exist, the candidate
       set came back empty, zero files were scanned, or ZERO RECORDS were
       produced. A PASS naming zero rows is visibly wrong, so zero rows is an
       error and never a success.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import citation_paths

SCHEMA_VERSION = "1.0.0"

#: The text stored in `source_text` / `source_text_end` when the line could not
#: be read. Never null, because a range record must carry both texts.
UNREADABLE = "<UNREADABLE>"

TEXT_STATUS_READ = "read"
TEXT_STATUS_UNRESOLVED = "unresolved_target"
TEXT_STATUS_AMBIGUOUS = "ambiguous_target"
TEXT_STATUS_REJECTED = "rejected_target"
TEXT_STATUS_OUT_OF_RANGE = "line_out_of_range"
TEXT_STATUS_READ_ERROR = "read_error"

#: Extensions scanned inside the meta repo's planning tree. Research's own
#: census scanned exactly these, which is why this tool's totals are
#: comparable to its 13,002 figure.
SCAN_EXTENSIONS = (".md", ".py", ".json", ".txt", ".sh", ".csv")

#: Directory names never descended into. Build, virtualenv and cache trees are
#: excluded because a `.venv` carries 2,395 vendored `.py` files and a `.pio`
#: carries 606 vendored `.c`/`.h` files, all of which would otherwise pollute
#: the --stats full-repo diagnostic index and let an unresolved citation be
#: mis-classified as naming "a real repo file" when it in fact matched a
#: vendored dependency copy.
SKIP_DIRS = (
    "__pycache__",
    ".git",
    "node_modules",
    ".pio",
    ".venv",
    "venv",
    "build",
    "dist",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".eggs",
    "htmlcov",
)

#: Source extensions a citation can target (research restricted its census to
#: these, plus `.hpp` which `survey_provenance.py` already scans).
TARGET_EXTENSIONS = (".cpp", ".hpp", ".ino", ".py", ".c", ".h")

#: Meta-relative prefixes excluded from the scan BY DESIGN, with the reason.
#: The v1.33 tool directory holds this generator, the shared resolver, the
#: remapper and their unit tests. Their sources and fixtures contain
#: citation-shaped literals BY CONSTRUCTION, and a Phase 159 remapper that
#: rewrote its own test fixtures would break the tools that produce the
#: manifest. Measured at generation time: 12 citation-shaped literals live
#: under this prefix and ALL 12 are illustrative or unit-test-fixture strings
#: inside these tools -- none is a real citation into swept source. Without the
#: exclusion all 12 would become manifest rows, and Phase 159 would then try to
#: rewrite the very fixtures this generator's tests assert on.
SELF_EXCLUDE_PREFIXES = (".planning/milestones/v1.33-artifacts/tools/",)

VARIANT_COLON_SINGLE = "colon_single"
VARIANT_COLON_RANGE = "colon_range"
VARIANT_COLON_LIST = "colon_list"
VARIANT_ANCHOR = "anchor_L"
VARIANT_ANCHOR_RANGE = "anchor_L_range"
VARIANTS = (
    VARIANT_COLON_SINGLE,
    VARIANT_COLON_RANGE,
    VARIANT_COLON_LIST,
    VARIANT_ANCHOR,
    VARIANT_ANCHOR_RANGE,
)
RANGE_VARIANTS = (VARIANT_COLON_RANGE, VARIANT_ANCHOR_RANGE)

#: The fixed record key order. Emitted in this order on every line; never
#: sorted, so the file is diffable and regeneration is byte-identical.
RECORD_KEYS = (
    "planning_file",
    "planning_line",
    "variant",
    "target_file_cited",
    "target_file_resolved",
    "resolution",
    "resolution_reason",
    "target_line",
    "target_line_end",
    "source_text",
    "source_text_end",
    "text_status",
    "text_status_end",
    "retarget",
)

_EXT_ALT = "|".join(e.lstrip(".") for e in TARGET_EXTENSIONS)
#: A path-shaped token ending in a target extension. The lookbehind pins the
#: match to the true START of the token, so a `../`-relative or `/`-absolute
#: citation is captured WHOLE and can therefore be rejected on its real shape
#: instead of being silently truncated into a plausible-looking relative path.
_PATH_TOKEN = r"[A-Za-z0-9_./+-]*[A-Za-z0-9_+-]\.(?:" + _EXT_ALT + r")"
_CITATION_RE = re.compile(
    r"(?<![A-Za-z0-9_./+~-])"
    r"(?P<path>" + _PATH_TOKEN + r")"
    r"(?:"
    r"\#L(?P<a_start>\d+)(?:-L?(?P<a_end>\d+))?"
    r"|:(?P<l_first>\d+)(?P<l_rest>(?:,\d+)+)"
    r"|:(?P<r_start>\d+)-(?P<r_end>\d+)"
    r"|:(?P<s_line>\d+)"
    r")"
)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
def _spans_from_match(m: re.Match[str]) -> list[tuple[str, int, int | None]]:
    """(variant, start_line, end_line_or_None) tuples produced by one match.

    Only `colon_list` yields more than one -- it is N independent POINT
    citations sharing a path, never a range.
    """
    if m.group("a_start"):
        start = int(m.group("a_start"))
        end = m.group("a_end")
        if end:
            return [(VARIANT_ANCHOR_RANGE, start, int(end))]
        return [(VARIANT_ANCHOR, start, None)]
    if m.group("l_first"):
        elements = [int(m.group("l_first"))]
        elements += [int(x) for x in m.group("l_rest").split(",") if x]
        return [(VARIANT_COLON_LIST, n, None) for n in elements]
    if m.group("r_start"):
        return [(VARIANT_COLON_RANGE, int(m.group("r_start")), int(m.group("r_end")))]
    return [(VARIANT_COLON_SINGLE, int(m.group("s_line")), None)]


def _scan_planning_files(
    meta_root: Path, scan_subdir: str, excluded_prefixes: tuple[str, ...]
) -> list[str]:
    """Meta-relative posix paths of every scannable planning document."""
    base = meta_root / scan_subdir
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if os.path.splitext(name)[1] not in SCAN_EXTENSIONS:
                continue
            abs_path = Path(dirpath) / name
            rel = abs_path.relative_to(meta_root).as_posix()
            if any(
                rel == prefix or rel.startswith(prefix) for prefix in excluded_prefixes
            ):
                continue
            found.append(rel)
    return sorted(found)


class _TargetTextCache:
    """Lazily-read line lists for resolved target files."""

    def __init__(self, index: citation_paths.CandidateIndex) -> None:
        self._index = index
        self._lines: dict[str, list[str] | None] = {}

    def lines(self, rel: str) -> list[str] | None:
        if rel not in self._lines:
            try:
                text = self._index.real_path(rel).read_text(
                    encoding="utf-8", errors="replace"
                )
            except (OSError, ValueError):
                self._lines[rel] = None
            else:
                self._lines[rel] = text.splitlines()
        return self._lines[rel]

    def at(self, rel: str, lineno: int) -> tuple[str, str]:
        lines = self.lines(rel)
        if lines is None:
            return UNREADABLE, TEXT_STATUS_READ_ERROR
        if lineno < 1 or lineno > len(lines):
            return UNREADABLE, TEXT_STATUS_OUT_OF_RANGE
        return lines[lineno - 1], TEXT_STATUS_READ


_UNREADABLE_STATUS_FOR = {
    citation_paths.UNRESOLVED: TEXT_STATUS_UNRESOLVED,
    citation_paths.AMBIGUOUS: TEXT_STATUS_AMBIGUOUS,
    citation_paths.REJECTED: TEXT_STATUS_REJECTED,
}


def build_records(
    meta_root: Path,
    planning_files: list[str],
    index: citation_paths.CandidateIndex,
) -> list[dict]:
    cache = _TargetTextCache(index)
    resolutions: dict[str, citation_paths.Resolution] = {}
    records: list[dict] = []
    occurrences: Counter[str] = Counter()

    for rel in planning_files:
        try:
            text = (meta_root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"ERROR: cannot read {rel}: {exc}", file=sys.stderr)
            sys.exit(2)
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in _CITATION_RE.finditer(line):
                cited = match.group("path")
                if cited not in resolutions:
                    resolutions[cited] = index.resolve(cited)
                res = resolutions[cited]
                spans = _spans_from_match(match)
                # One MATCH is one citation occurrence, even when it expands to
                # several records: `hardware.py:39,153` is one occurrence and
                # two records.
                occurrences[spans[0][0]] += 1
                for variant, start, end in spans:
                    if res.is_resolved and res.path is not None:
                        s_text, s_status = cache.at(res.path, start)
                        if end is None:
                            e_text, e_status = None, None
                        else:
                            e_text, e_status = cache.at(res.path, end)
                    else:
                        status = _UNREADABLE_STATUS_FOR[res.resolution]
                        s_text, s_status = UNREADABLE, status
                        e_text, e_status = (
                            (None, None) if end is None else (UNREADABLE, status)
                        )
                    records.append(
                        {
                            "planning_file": rel,
                            "planning_line": lineno,
                            "variant": variant,
                            "target_file_cited": cited,
                            "target_file_resolved": res.path,
                            "resolution": res.resolution,
                            "resolution_reason": res.reason,
                            "target_line": start,
                            "target_line_end": end,
                            "source_text": s_text,
                            "source_text_end": e_text,
                            "text_status": s_status,
                            "text_status_end": e_status,
                            "retarget": False,
                        }
                    )
    return records, occurrences


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------
def _git_head(root: Path) -> str | None:
    try:
        done = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip() or None


def _ordered(record: dict) -> dict:
    return {key: record[key] for key in RECORD_KEYS}


def _dump(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def build_header(
    *,
    records: list[dict],
    occurrences: Counter[str],
    candidate_count: int,
    planning_file_count: int,
    excluded_prefixes: tuple[str, ...],
    fw_sha: str | None,
    app_sha: str | None,
    generating_command: str,
) -> dict:
    by_variant = Counter(r["variant"] for r in records)
    by_resolution = Counter(r["resolution"] for r in records)
    by_text_status = Counter(r["text_status"] for r in records)
    return {
        "_schema": {
            "schema_version": SCHEMA_VERSION,
            "purpose": (
                "Pre-sweep citation manifest for milestone v1.33 Phase 154 "
                "(SWEEP-09/SWEEP-10, D-07). The ONLY interface between Phase "
                "154's comment sweep and Phase 159's citation remap "
                "(REMAP-01..05). Not reconstructible after the sweep: the "
                "pre-sweep (line, text) pairs exist nowhere on disk once the "
                "sweep lands."
            ),
            "record_keys": list(RECORD_KEYS),
            "jsonl_convention": (
                "One JSON object per line; LF line terminators; UTF-8 with "
                "ensure_ascii=False; keys emitted in the fixed RECORD_KEYS "
                "order and never sorted; this header object is line 1 and is "
                "the only line carrying the key '_schema'. No timestamp is "
                "recorded anywhere, so regeneration over an unchanged tree is "
                "byte-identical. Stated rather than inherited: no JSONL file "
                "existed anywhere in the three repos before this one."
            ),
            "source_text_convention": (
                "Stored EXACTLY as read but WITHOUT its line terminator, i.e. "
                "as produced by str.splitlines(). Phase 159's oracle must "
                "compare against splitlines() output, not against a "
                "newline-terminated read."
            ),
            "source_text_unreadable_sentinel": UNREADABLE,
            "text_status_values": {
                TEXT_STATUS_READ: "the cited line was read from the resolved file",
                TEXT_STATUS_UNRESOLVED: "no candidate file matched the cited path",
                TEXT_STATUS_AMBIGUOUS: "the cited path matched more than one candidate",
                TEXT_STATUS_REJECTED: "the cited path escapes the explicit repo roots",
                TEXT_STATUS_OUT_OF_RANGE: "the cited line is past the resolved file's EOF",
                TEXT_STATUS_READ_ERROR: "the resolved file could not be read",
            },
            "why_source_text_is_never_null": (
                "Phase 159 asserts that every range record carries BOTH "
                "source_text and source_text_end. A null would fail that "
                "assertion for every unresolved or past-EOF range, so an "
                "unreadable text carries the declared sentinel and "
                "text_status/text_status_end say authoritatively why. The "
                "oracle skips a non-'read' row BY NAME instead of failing "
                "open on it."
            ),
            "variants": {
                VARIANT_COLON_SINGLE: "path:N",
                VARIANT_COLON_RANGE: "path:N-M (both endpoints recorded)",
                VARIANT_COLON_LIST: (
                    "path:N,M[,...] -- N independent POINT records, never a "
                    "range; one record per element"
                ),
                VARIANT_ANCHOR: "markdown path#LN",
                VARIANT_ANCHOR_RANGE: "markdown path#LN-LM / path#LN-M",
                "_backticked_wrapper": (
                    "a backticked `path:N` is a WRAPPER, not a fifth variant: "
                    "the inner text matches the colon form and is recorded as "
                    "such, with the backticks absent from target_file_cited"
                ),
            },
            "candidate_set": {
                "definition": (
                    "Every file under the sweep globs "
                    "(firestarter/{src,include,test,lib}, "
                    "firestarter_app/{firestarter,tests,tools}) carrying at "
                    "least one provenance hit, as measured by "
                    ".planning/milestones/v1.33-artifacts/tools/survey_provenance.py (plan 02) -- "
                    "called as the single corpus authority, never "
                    "re-implemented."
                ),
                "count": candidate_count,
            },
            "ordering_resolution": (
                "This manifest is a PRE-sweep deliverable, but 'targets a "
                "swept file' is only knowable AFTER the sweep. It is "
                "therefore generated over the CANDIDATE swept-file set, and "
                "'targets a swept file' is interpreted as 'targets a "
                "CANDIDATE swept file'. This is a deliberate "
                "over-approximation and it is strictly better for Phase 159: "
                "recording a citation into a file that turns out untouched is "
                "harmless, because its source_text still matches at its "
                "recorded line and the fixed-point check makes the row a "
                "no-op. The difference between the candidate set and the "
                "ACTUAL swept set is recorded post-sweep in the staleness "
                "marker (SWEEP-12)."
            ),
            "resolution_rule": {
                "0_rejected": (
                    "an absolute path, a '..'-carrying path or a '~'-rooted "
                    "path escapes the explicit roots: RECORDED, never opened, "
                    "never raised"
                ),
                "1_exact": "exact repo-relative path in the candidate set",
                "2_suffix": (
                    "unique path suffix on a segment boundary; a tie is broken "
                    "toward the non-fixture candidate"
                ),
                "3_basename": (
                    "bare basename against an index built from the candidate "
                    "set with the declared fixture-exclusion globs applied, so "
                    "a citation can never bind to a planted or fake fixture "
                    "copy of a real file; a basename carried ONLY by a fixture "
                    "resolves via an explicitly-labelled fixture-inclusive "
                    "fallback"
                ),
                "4_ambiguous": (
                    "still more than one candidate: no resolved path, excluded "
                    "from the oracle, COUNTED"
                ),
                "5_unresolved": "no candidate at all: COUNTED, never dropped",
                "implemented_by": ".planning/milestones/v1.33-artifacts/tools/citation_paths.py",
                "shared_with": (
                    ".planning/milestones/v1.33-artifacts/tools/remap_citations.py -- one resolver "
                    "for both tools, so the same citation cannot resolve two "
                    "different ways"
                ),
            },
            "retarget": (
                "false for EVERY record in this pre-sweep manifest. A citation "
                "pointing AT a comment line the sweep deletes becomes "
                "retarget:true with its original cited text preserved (D-08), "
                "but that subset cannot exist until the sweep's diff exists. "
                "It is settled, and its count reported, in Phase 154 plan 12 "
                "-- D-08's only manual work in the whole repair. The field's "
                "presence here with the value false is what makes plan 12's "
                "update a FIELD FLIP rather than a schema change."
            ),
            "scan": {
                "extensions": list(SCAN_EXTENSIONS),
                "skipped_directories": list(SKIP_DIRS),
                "target_extensions": list(TARGET_EXTENSIONS),
                "planning_files_scanned": planning_file_count,
                "excluded_prefixes": list(excluded_prefixes),
                "exclusion_reason": (
                    "The v1.33 tool directory and this generator's own two "
                    "output artifacts are excluded. The tools' sources and "
                    "unit-test fixtures contain citation-shaped literals BY "
                    "CONSTRUCTION, and a manifest that cites itself grows on "
                    "every run while a remapper that rewrote its own test "
                    "fixtures would break the tools that produce the "
                    "manifest. Measured at generation time: 12 "
                    "citation-shaped literals live under the excluded tool "
                    "prefix and all 12 are illustrative or unit-test-fixture "
                    "strings inside these tools -- none is a real citation "
                    "into swept source."
                ),
            },
            "pre_sweep_shas": {
                "firestarter": fw_sha,
                "firestarter_app": app_sha,
                "note": (
                    "git rev-parse HEAD in each sub-repo at generation time, "
                    "recorded so the pre-sweep side is provably identified. "
                    "The meta repo's own HEAD is deliberately NOT recorded: it "
                    "advances with this very commit and would break "
                    "byte-identical regeneration."
                ),
            },
            "generating_command": generating_command,
            "counts": {
                "records": len(records),
                "citation_occurrences": sum(occurrences.values()),
                "occurrences_note": (
                    "A citation OCCURRENCE is one matched citation in a "
                    "planning document; a RECORD is one (target_file, "
                    "target_line) pair. They differ for colon_list only, "
                    "where one occurrence yields one record per element. "
                    "Research's per-variant census counted occurrences, so "
                    "by_variant_occurrences is the figure comparable to it."
                ),
                "by_variant_occurrences": {
                    v: occurrences.get(v, 0) for v in VARIANTS
                },
                "by_variant": {v: by_variant.get(v, 0) for v in VARIANTS},
                "by_resolution": {
                    r: by_resolution.get(r, 0) for r in citation_paths.RESOLUTIONS
                },
                "by_text_status": dict(sorted(by_text_status.items())),
            },
        }
    }


def write_manifest(out_path: Path, header: dict, records: list[dict]) -> None:
    """Atomic write: temp file plus os.replace (ASVS V12)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(_dump(header) + "\n")
        for record in records:
            fh.write(_dump(_ordered(record)) + "\n")
    os.replace(tmp_path, out_path)


# ---------------------------------------------------------------------------
# Serialize-then-scan self-check (the check_ledger.py idiom)
# ---------------------------------------------------------------------------
REQUIRED_KEYS = frozenset(RECORD_KEYS)


def self_check(out_path: Path) -> tuple[list[str], list[dict]]:
    violations: list[str] = []
    records: list[dict] = []
    with open(out_path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                violations.append(f"line {lineno}: blank line in a JSONL file")
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                violations.append(f"line {lineno}: not valid JSON: {exc}")
                continue
            if lineno == 1:
                if "_schema" not in obj:
                    violations.append("line 1: missing the '_schema' header record")
                continue
            records.append(obj)
            missing = REQUIRED_KEYS - set(obj)
            if missing:
                violations.append(f"line {lineno}: missing keys {sorted(missing)}")
                continue
            if obj["variant"] not in VARIANTS:
                violations.append(
                    f"line {lineno}: unhandled variant {obj['variant']!r}"
                )
            if obj["variant"] in RANGE_VARIANTS:
                if obj["target_line_end"] is None:
                    violations.append(f"line {lineno}: range record has no end line")
                if obj["source_text_end"] is None:
                    violations.append(f"line {lineno}: range record has no end text")
            if obj["retarget"] is not False:
                violations.append(
                    f"line {lineno}: retarget must be false in a pre-sweep manifest"
                )
            if obj["resolution"] not in citation_paths.RESOLUTIONS:
                violations.append(
                    f"line {lineno}: unknown resolution {obj['resolution']!r}"
                )
            if (obj["resolution"] in citation_paths.RESOLVED_CLASSES) != (
                obj["target_file_resolved"] is not None
            ):
                violations.append(
                    f"line {lineno}: resolution {obj['resolution']!r} disagrees with "
                    f"target_file_resolved={obj['target_file_resolved']!r}"
                )
    return violations, records


# ---------------------------------------------------------------------------
# --stats: everything the SWEEP-09 reconciliation report has to quote
# ---------------------------------------------------------------------------
def _full_repo_paths(fw_root: Path, app_root: Path) -> list[str]:
    out: list[str] = []
    for name, root in (("firestarter", fw_root), ("firestarter_app", app_root)):
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                if os.path.splitext(fname)[1] not in TARGET_EXTENSIONS:
                    continue
                rel = (Path(dirpath) / fname).relative_to(root).as_posix()
                out.append(f"{name}/{rel}")
    return out


def print_stats(
    records: list[dict],
    occurrences: Counter[str],
    candidates: dict[str, list[tuple[int, str]]],
    fw_root: Path,
    app_root: Path,
) -> None:
    first_hit = {rel: min(l for l, _ in hits) for rel, hits in candidates.items() if hits}

    print("\n--- STATS ---")
    print(f"records: {len(records)}")
    print(f"citation occurrences (matches): {sum(occurrences.values())}")

    print("\nby variant (OCCURRENCES -- comparable to research's census):")
    for v in VARIANTS:
        print(f"  {v:<16} {occurrences.get(v, 0)}")
    print(
        f"  {'anchor_L (both)':<16} "
        f"{occurrences.get(VARIANT_ANCHOR, 0) + occurrences.get(VARIANT_ANCHOR_RANGE, 0)}"
    )

    print("\nby variant (RECORDS):")
    by_variant = Counter(r["variant"] for r in records)
    for v in VARIANTS:
        print(f"  {v:<16} {by_variant.get(v, 0)}")
    print(
        f"  {'anchor_L (both)':<16} "
        f"{by_variant.get(VARIANT_ANCHOR, 0) + by_variant.get(VARIANT_ANCHOR_RANGE, 0)}"
    )

    print("\nby resolution:")
    by_res = Counter(r["resolution"] for r in records)
    for r in citation_paths.RESOLUTIONS:
        print(f"  {r:<12} {by_res.get(r, 0)}")
    resolved = [r for r in records if r["resolution"] in citation_paths.RESOLVED_CLASSES]
    print(f"  {'RESOLVED':<12} {len(resolved)}  (exact + suffix + basename)")

    print("\nby text_status:")
    for status, n in sorted(Counter(r["text_status"] for r in records).items()):
        print(f"  {status:<20} {n}")

    shifting = [
        r
        for r in resolved
        if r["target_line"] >= first_hit.get(r["target_file_resolved"], 1 << 30)
    ]
    print(
        f"\nshifting subset (resolved rows at or below their target file's FIRST "
        f"provenance hit line): {len(shifting)}"
    )
    print(f"non-shifting resolved rows (above the first hit): {len(resolved) - len(shifting)}")

    print("\nresolved rows by resolution_reason:")
    for reason, n in Counter(r["resolution_reason"] for r in resolved).most_common():
        print(f"  {n:>6}  {reason}")

    print("\nambiguous rows by cited target (every ambiguity RECORDED, not dropped):")
    amb = Counter(
        r["target_file_cited"]
        for r in records
        if r["resolution"] == citation_paths.AMBIGUOUS
    )
    for cited, n in amb.most_common():
        print(f"  {n:>6}  {cited}")
    print(f"  ambiguous total: {sum(amb.values())} rows over {len(amb)} distinct targets")

    print("\nrejected rows by cited target:")
    rej = Counter(
        r["target_file_cited"]
        for r in records
        if r["resolution"] == citation_paths.REJECTED
    )
    for cited, n in rej.most_common(10):
        print(f"  {n:>6}  {cited}")
    print(f"  rejected total: {sum(rej.values())} rows over {len(rej)} distinct targets")

    unresolved = [r for r in records if r["resolution"] == citation_paths.UNRESOLVED]
    unres_by_target = Counter(r["target_file_cited"] for r in unresolved)
    print(f"\ntop 20 unresolved targets ({len(unresolved)} rows, {len(unres_by_target)} distinct):")
    for cited, n in unres_by_target.most_common(20):
        print(f"  {n:>6}  {cited}")

    # Reconciliation diagnostic: how many `unresolved` rows name a REAL file in
    # one of the two repos that simply is not a candidate (no provenance hit),
    # versus naming nothing in either repo at all. Research's 1,351 figure was
    # measured against a whole-tree index, so this is the bridge between the
    # two numbers.
    full = citation_paths.CandidateIndex(
        {"firestarter": fw_root, "firestarter_app": app_root},
        _full_repo_paths(fw_root, app_root),
    )
    in_repo = 0
    not_in_repo = 0
    for cited, n in unres_by_target.items():
        try:
            got = full.resolve(cited)
        except citation_paths.FixtureResolutionError:
            got = None
        if got is not None and got.is_resolved:
            in_repo += n
        else:
            not_in_repo += n
    print(f"\nfull-repo index size: {len(full)} source files")
    print(f"  unresolved rows naming a REAL repo file that is not a candidate: {in_repo}")
    print(f"  unresolved rows naming nothing in either repo:                   {not_in_repo}")

    print("\ntop 15 resolved target files by row count:")
    for target, n in Counter(r["target_file_resolved"] for r in resolved).most_common(15):
        print(f"  {n:>6}  {target}")

    eprom = [r for r in resolved if r["target_file_resolved"] == "firestarter/src/proms/eprom.cpp"]
    eprom_shift = [r for r in eprom if r in shifting]
    print(
        f"\nRuling B follow-on: firestarter/src/proms/eprom.cpp rows = {len(eprom)} "
        f"(of which shifting = {len(eprom_shift)})"
    )

    print("\nrows by planning subtree:")
    subtree_rows: Counter[str] = Counter()
    subtree_shift: Counter[str] = Counter()
    shifting_ids = {id(r) for r in shifting}
    for r in records:
        parts = r["planning_file"].split("/")
        key = "/".join(parts[:2]) if len(parts) > 2 else r["planning_file"]
        subtree_rows[key] += 1
        if id(r) in shifting_ids:
            subtree_shift[key] += 1
    for key, n in subtree_rows.most_common(20):
        print(f"  {n:>6}  (shifting {subtree_shift.get(key, 0):>5})  {key}")

    selfref = [r for r in records if r["planning_file"].startswith(".planning/milestones/v1.33-artifacts/")]
    print(f"\nrows citing FROM .planning/milestones/v1.33-artifacts/ (this milestone's own documents): {len(selfref)}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Generate the pre-sweep citation manifest. The meta-repo root is a "
            "required POSITIONAL argument and both sub-repo roots are required "
            "options; nothing is derived from this file's own location (D-09)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("meta_root", help="meta-repo root -- explicit, NEVER derived")
    ap.add_argument("--fw-root", required=True, help="firestarter (firmware) repo root")
    ap.add_argument("--app-root", required=True, help="firestarter_app (host) repo root")
    ap.add_argument(
        "--out",
        required=True,
        help="manifest output path; there is deliberately NO default",
    )
    ap.add_argument(
        "--scan-subdir",
        default=".planning",
        help="meta-relative directory scanned for citations (default: .planning)",
    )
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="METAREL_PREFIX",
        help="additional meta-relative path or prefix to exclude (repeatable)",
    )
    ap.add_argument(
        "--stats",
        action="store_true",
        help="print the full reconciliation statistics block after writing",
    )
    args = ap.parse_args(argv)

    meta_root = Path(args.meta_root)
    fw_root = Path(args.fw_root)
    app_root = Path(args.app_root)
    for label, root in (
        ("meta_root", meta_root),
        ("--fw-root", fw_root),
        ("--app-root", app_root),
    ):
        if not root.is_dir():
            print(
                f"ERROR: {label} does not exist or is not a directory: {root}",
                file=sys.stderr,
            )
            sys.exit(2)
    meta_root = meta_root.resolve()
    fw_root = fw_root.resolve()
    app_root = app_root.resolve()

    if not (meta_root / args.scan_subdir).is_dir():
        print(
            f"ERROR: scan directory does not exist: {meta_root / args.scan_subdir}",
            file=sys.stderr,
        )
        sys.exit(2)

    out_path = Path(args.out).resolve()
    excluded = list(SELF_EXCLUDE_PREFIXES)
    try:
        excluded.append(out_path.relative_to(meta_root).as_posix())
    except ValueError:
        pass
    excluded.extend(args.exclude)
    excluded_prefixes = tuple(sorted(set(excluded)))

    candidates = citation_paths.survey_candidates(fw_root, app_root)
    if not candidates:
        print(
            "ERROR: the candidate swept-file set is EMPTY -- silence is never "
            "success (D-09: exit non-zero on an empty input set).",
            file=sys.stderr,
        )
        sys.exit(2)
    index = citation_paths.CandidateIndex(
        {"firestarter": fw_root, "firestarter_app": app_root}, candidates.keys()
    )

    planning_files = _scan_planning_files(
        meta_root, args.scan_subdir, excluded_prefixes
    )
    if not planning_files:
        print(
            f"ERROR: zero scannable files found under "
            f"{meta_root / args.scan_subdir} -- silence is never success.",
            file=sys.stderr,
        )
        sys.exit(2)

    records, occurrences = build_records(meta_root, planning_files, index)
    if not records:
        print(
            "ERROR: the generator produced ZERO records. A PASS naming zero "
            "rows is visibly wrong, so zero rows is an infrastructure error "
            "and never a success. Exit 2.",
            file=sys.stderr,
        )
        sys.exit(2)

    generating_command = " ".join(
        ["python3", "build_citation_manifest.py"] + list(argv or sys.argv[1:])
    )
    header = build_header(
        records=records,
        occurrences=occurrences,
        candidate_count=len(index),
        planning_file_count=len(planning_files),
        excluded_prefixes=excluded_prefixes,
        fw_sha=_git_head(fw_root),
        app_sha=_git_head(app_root),
        generating_command=generating_command,
    )
    write_manifest(out_path, header, records)

    violations, reread = self_check(out_path)
    if violations:
        print(
            f"FAIL: the written manifest failed its own self-check with "
            f"{len(violations)} violation(s):",
            file=sys.stderr,
        )
        for v in violations[:20]:
            print(f"  {v}", file=sys.stderr)
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more", file=sys.stderr)
        print(f"Total: {len(violations)} violation(s). Exit 1 (BLOCK).", file=sys.stderr)
        sys.exit(1)

    by_variant = Counter(r["variant"] for r in reread)
    by_res = Counter(r["resolution"] for r in reread)
    print(f"wrote {out_path}")
    print(
        "PASS: "
        f"{len(reread)} records over {len(planning_files)} planning files, "
        f"{len(index)} candidate swept files; "
        "variants "
        + ", ".join(f"{v}={by_variant.get(v, 0)}" for v in VARIANTS)
        + "; resolutions "
        + ", ".join(f"{r}={by_res.get(r, 0)}" for r in citation_paths.RESOLUTIONS)
        + "; every range record carries both endpoints and both texts; every "
        "record retarget=false."
    )

    if args.stats:
        print_stats(reread, occurrences, candidates, fw_root, app_root)

    sys.exit(0)


if __name__ == "__main__":
    main()
