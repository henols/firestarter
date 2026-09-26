#!/usr/bin/env python3
r"""
Shared citation path-resolution rule for milestone v1.33.

WHY THIS IS A SEPARATE MODULE
------------------------------
It is imported by BOTH `build_citation_manifest.py` (Phase 154 plan 04) and
`remap_citations.py` (Phase 154 plan 05, applied in Phase 159). Factoring the
rule into one module is what prevents the same ambiguous citation resolving two
different ways in the two tools -- research F5 measured 665 ambiguous citations
against a whole-tree index, and the three highest-cited of them
(`eeprom_28c.cpp`, `firestarter.cpp`, `firestarter.h`) are exactly this phase's
hottest files. A generator that bound them one way and a remapper that bound
them another would corrupt the manifest silently.

THE FIVE-STEP RULE (research F5), applied in order, outcome recorded per record
-------------------------------------------------------------------------------
  0. REJECT first: an absolute path, or any path carrying a `..` segment, or a
     `~`-rooted path, escapes the explicit roots. It is RECORDED as
     `rejected` -- never opened, never raised. Research counted 29 citations
     that are literally `../firestarter/include/rurp_shield.h`; those are
     out-of-scope by design, not a reason to relax the rule.
  1. EXACT   -- the cited string is an exact repo-relative path in the
                candidate set.
  2. SUFFIX  -- the cited string is a path suffix (on a segment boundary) of
                exactly one candidate. On a tie the fixture-excluded subset is
                retried, so `src/proms/eeprom_28c.cpp` breaks toward the real
                firmware file and never toward the planted-CMake-manifest
                fixture copy that shares that suffix.
  3. BASENAME -- a bare basename, resolved against an index built from the
                candidate set with the fixture globs EXCLUDED. This alone is
                what disambiguates `eeprom_28c.cpp`, `firestarter.cpp`,
                `firestarter.h` and `uno_rurp_shield.cpp` on a whole-tree
                index, because every colliding alternate there is a planted or
                fake fixture. If (and only if) no non-fixture candidate carries
                the basename at all, an explicitly-labelled fixture-inclusive
                fallback runs, so a citation whose target genuinely IS a
                fixture file resolves instead of being lost as a false
                `unresolved`.
  4. AMBIGUOUS -- still more than one candidate. No resolved path, excluded
                from Phase 159's oracle, COUNTED.
  5. UNRESOLVED -- no candidate at all. COUNTED. Research measured 1,351
                against a whole-tree index and showed they are mostly
                legitimate (`database.c` is infoic's external decompiled
                source; `primitives.cpp` is the v1.16 layer that was never
                merged). A generator that silently discarded them would be
                indistinguishable from one that is broken.

NEVER RESOLVE A FIXTURE PATH AS IF IT WERE THE REAL FILE (T-154-13)
--------------------------------------------------------------------
A citation remapped onto
`firestarter/tests/fixtures/planted_cmake_manifest_missing_source/src/proms/eeprom_28c.cpp`
would round-trip GREEN against the wrong file -- a silent-correctness failure of
the same family as the fail-open source-scanning gates this phase's controls
exist for. So the basename step carries an explicit guard: if the
fixture-EXCLUDED index ever yields a path that looks like a fixture, the index
was built wrong, and that is a bug rather than a result -- it raises
`FixtureResolutionError`.

EXPLICIT ROOTS (D-09)
----------------------
Roots are explicit arguments. Nothing in this module derives a scan root from
`__file__` or from its own location. The named house analog
`.planning/milestones/v1.16-artifacts/ledger/tools/check_ledger.py` hard-codes four `..` segments
from its own location, which is the exact shape D-09 forbids and which
`reference_check_permitted_claims_here_resolves_wrong_phase_dir` records as
scanning nothing and exiting 0. The shape is therefore INTRODUCED here, not
copied.

PATH SAFETY (ASVS V5/V12)
--------------------------
Every candidate path handed to the index is validated by string normalisation
only -- relative, no parent-traversal segment, first segment a declared root
name, and the normalised join still under that root. No filesystem access
happens during indexing or resolution, so a symlink cannot walk the resolution
outside the two explicit roots and a non-existent synthetic path is indexable
in a unit test.

EXIT CODES (house 0/1/2 convention; applies to the --self-check entry point)
-----------------------------------------------------------------------------
  0 -- every probe resolved to its expected class; index size and the
       per-resolution breakdown printed.
  1 -- a real violation: at least one probe resolved to the wrong class, or the
       fixture guard fired against the real candidate index.
  2 -- infrastructure: a root argument does not exist / is not a directory, or
       the candidate set came back empty. Silence is never success.
"""

from __future__ import annotations

import argparse
import posixpath
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

# ---------------------------------------------------------------------------
# The closed resolution enum. Six values: the five-step rule's five outcomes
# plus `rejected`, which is kept DISTINCT from `unresolved` so a reader can
# tell "this citation escapes the roots" from "this citation names nothing in
# the candidate set". The rejection is recorded, which is the whole point.
# ---------------------------------------------------------------------------
EXACT = "exact"
SUFFIX = "suffix"
BASENAME = "basename"
AMBIGUOUS = "ambiguous"
UNRESOLVED = "unresolved"
REJECTED = "rejected"

RESOLUTIONS = (EXACT, SUFFIX, BASENAME, AMBIGUOUS, UNRESOLVED, REJECTED)
#: The classes that yield a usable `path` and therefore a remappable row.
RESOLVED_CLASSES = (EXACT, SUFFIX, BASENAME)

# ---------------------------------------------------------------------------
# The declared fixture-exclusion globs (research F5 step 3). They are stated as
# globs because that is how the rule reads, and interpreted by path SEGMENT
# because that is what the rule means: a `fixtures` or `fixture` directory
# anywhere in the path excludes the file from the basename index.
# ---------------------------------------------------------------------------
FIXTURE_EXCLUDE_GLOBS = ("**/fixtures/**", "**/fixture/**")

#: Substrings that make a resolved path "fixture-shaped". Wider than the globs
#: on purpose -- the guard must also catch `fake_` / `planted_` names that do
#: not happen to sit under a `fixtures/` directory.
FIXTURE_GUARD_SUBSTRINGS = ("fixtures/", "fixture/", "fake_", "planted_")

#: The `Resolution.reason` emitted by step 3b, the EXPLICITLY-LABELLED
#: fixture-inclusive fallback. Named as a constant rather than written inline
#: because `remap_citations.py` (plan 05) needs it to tell a LEGITIMATE
#: fixture binding -- a citation whose target genuinely IS a planted fixture,
#: measured at 6 records in the v1.33 manifest -- from a COLLIDING one, where a
#: real file's bare basename bound to a fixture copy (T-154-13). A string match
#: written inline in the remapper would fail OPEN the day this reason is
#: reworded; one constant, two importers, cannot.
FIXTURE_INCLUSIVE_FALLBACK_REASON = (
    "unique basename via the fixture-inclusive fallback (no non-fixture "
    "candidate carries this basename)"
)


class FixtureResolutionError(RuntimeError):
    """The fixture-excluded index yielded a fixture path -- the index is wrong."""


def _fixture_dir_segments() -> tuple[str, ...]:
    """The directory segment each declared glob selects (`fixtures`, `fixture`)."""
    segments = []
    for glob in FIXTURE_EXCLUDE_GLOBS:
        for part in glob.split("/"):
            if part not in ("**", "*", ""):
                segments.append(part)
                break
    return tuple(segments)


def looks_like_fixture(rel_posix: str) -> bool:
    """True if this repo-relative path is fixture-shaped (guard predicate)."""
    return any(token in rel_posix for token in FIXTURE_GUARD_SUBSTRINGS)


def matches_fixture_exclude_glob(rel_posix: str) -> bool:
    """True if a declared FIXTURE_EXCLUDE_GLOBS pattern selects this path."""
    dirs = rel_posix.split("/")[:-1]
    return any(seg in dirs for seg in _fixture_dir_segments())


@dataclass(frozen=True)
class Resolution:
    """One resolution outcome. `resolution` is always one of RESOLUTIONS."""

    resolution: str
    path: str | None
    reason: str
    candidates: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_resolved(self) -> bool:
        return self.resolution in RESOLVED_CLASSES


class CandidateIndex:
    """An index over an explicit list of repo-relative candidate paths.

    `roots` maps a root NAME (the first path segment, e.g. `firestarter`) to an
    existing directory. `paths` are repo-relative posix strings whose first
    segment is one of those names. Nothing is read from disk here.

    `_exclude_fixtures=False` is TEST-ONLY: it deliberately builds the WRONG
    index (fixtures included in the basename map) so that the T-154-13 guard
    can be PROVEN to raise rather than merely promised to.
    """

    def __init__(
        self,
        roots: Mapping[str, str | Path],
        paths: Iterable[str],
        *,
        _exclude_fixtures: bool = True,
    ) -> None:
        self.roots: dict[str, Path] = {}
        for name, root in roots.items():
            root_path = Path(root)
            if not root_path.is_dir():
                raise NotADirectoryError(
                    f"root {name!r} does not exist or is not a directory: {root_path}"
                )
            self.roots[name] = root_path.resolve()

        self._exclude_fixtures = _exclude_fixtures
        self.paths: tuple[str, ...] = tuple(
            sorted({self._validate(p) for p in paths})
        )
        self._by_basename: dict[str, list[str]] = {}
        self._by_basename_nonfixture: dict[str, list[str]] = {}
        for rel in self.paths:
            base = posixpath.basename(rel)
            self._by_basename.setdefault(base, []).append(rel)
            if _exclude_fixtures and matches_fixture_exclude_glob(rel):
                continue
            self._by_basename_nonfixture.setdefault(base, []).append(rel)
        self._nonfixture_paths: tuple[str, ...] = tuple(
            p
            for p in self.paths
            if not (_exclude_fixtures and matches_fixture_exclude_glob(p))
        )

    # -- indexing -----------------------------------------------------------
    def _validate(self, rel: str) -> str:
        """String-only path-safety validation of a candidate path (ASVS V5)."""
        rel = rel.replace("\\", "/").strip()
        if not rel:
            raise ValueError("empty candidate path")
        if rel.startswith("/") or rel.startswith("~"):
            raise ValueError(f"candidate path is not repo-relative: {rel!r}")
        parts = rel.split("/")
        if any(p in ("..", "") for p in parts):
            raise ValueError(f"candidate path carries a traversal segment: {rel!r}")
        root_name = parts[0]
        if root_name not in self.roots:
            raise ValueError(
                f"candidate path {rel!r} does not start with a declared root "
                f"name (declared: {sorted(self.roots)})"
            )
        normalised = posixpath.normpath(rel)
        if normalised != rel or not normalised.startswith(root_name + "/"):
            raise ValueError(f"candidate path does not normalise to itself: {rel!r}")
        return rel

    def __len__(self) -> int:
        return len(self.paths)

    def real_path(self, rel: str) -> Path:
        """Absolute on-disk path for an indexed repo-relative path.

        Asserts containment under the declared root AFTER resolution, so a
        symlinked candidate cannot walk the read outside its root.
        """
        parts = rel.split("/")
        root = self.roots[parts[0]]
        target = (root / "/".join(parts[1:])).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"resolved path escapes its root: {rel} -> {target}")
        return target

    # -- resolution ---------------------------------------------------------
    def resolve(self, cited: str) -> Resolution:
        cited = cited.strip().strip("`").strip()
        if not cited:
            return Resolution(UNRESOLVED, None, "empty cited string")

        # Step 0 -- reject anything escaping the explicit roots. Recorded,
        # never opened, never raised.
        normalised = cited.replace("\\", "/")
        parts = normalised.split("/")
        if normalised.startswith("/") or (len(normalised) > 1 and normalised[1] == ":"):
            return Resolution(
                REJECTED, None, "rejected: absolute path escapes the explicit roots"
            )
        if normalised.startswith("~"):
            return Resolution(
                REJECTED, None, "rejected: home-relative path escapes the explicit roots"
            )
        if ".." in parts:
            return Resolution(
                REJECTED,
                None,
                "rejected: parent-traversal segment escapes the explicit roots",
            )

        # Step 1 -- exact repo-relative path in the candidate set.
        if normalised in self.paths:
            return Resolution(EXACT, normalised, "exact repo-relative candidate path")

        if "/" in normalised:
            # Step 2 -- unique path suffix, on a segment boundary.
            needle = "/" + normalised
            hits = [p for p in self.paths if p.endswith(needle)]
            if len(hits) == 1:
                return Resolution(SUFFIX, hits[0], "unique path-suffix candidate")
            if len(hits) > 1:
                narrowed = [p for p in hits if not matches_fixture_exclude_glob(p)]
                if len(narrowed) == 1:
                    return Resolution(
                        SUFFIX,
                        narrowed[0],
                        "path-suffix tie broken by the fixture-exclusion globs",
                    )
                return Resolution(
                    AMBIGUOUS,
                    None,
                    f"path suffix matches {len(hits)} candidates",
                    tuple(sorted(hits)),
                )
            return Resolution(
                UNRESOLVED, None, "path suffix matches no candidate", ()
            )

        # Step 3 -- bare basename against the fixture-EXCLUDED index.
        base = normalised
        hits = self._by_basename_nonfixture.get(base, [])
        if len(hits) == 1:
            resolved = hits[0]
            if looks_like_fixture(resolved):
                raise FixtureResolutionError(
                    "the fixture-excluded basename index yielded a fixture path "
                    f"for {cited!r}: {resolved!r}. That is a bug in the index, "
                    "not a result -- a citation bound to a planted fixture would "
                    "round-trip GREEN against the wrong file (T-154-13)."
                )
            return Resolution(
                BASENAME, resolved, "unique basename in the fixture-excluded index"
            )
        if len(hits) > 1:
            return Resolution(
                AMBIGUOUS,
                None,
                f"basename matches {len(hits)} non-fixture candidates",
                tuple(sorted(hits)),
            )

        # Step 3b -- explicitly-labelled fixture-inclusive fallback. Runs only
        # when NO non-fixture candidate carries this basename at all, so a
        # citation whose target genuinely IS a fixture file resolves rather
        # than becoming a false `unresolved`.
        all_hits = self._by_basename.get(base, [])
        if len(all_hits) == 1:
            return Resolution(
                BASENAME, all_hits[0], FIXTURE_INCLUSIVE_FALLBACK_REASON
            )
        if len(all_hits) > 1:
            return Resolution(
                AMBIGUOUS,
                None,
                f"basename matches {len(all_hits)} candidates (fixture-inclusive)",
                tuple(sorted(all_hits)),
            )

        # Step 4/5 -- nothing in the candidate set.
        return Resolution(UNRESOLVED, None, "basename matches no candidate")


# ---------------------------------------------------------------------------
# Candidate-set construction -- the ONE place the corpus authority is called.
# `survey_provenance.py` (plan 02) owns the provenance regex and the seven
# group definitions; this function reuses that module rather than
# re-implementing either.
# ---------------------------------------------------------------------------
#: Group name -> the root NAME its paths are relative to.
GROUP_ROOT_NAME = {
    "fw-src": "firestarter",
    "fw-include": "firestarter",
    "fw-test": "firestarter",
    "fw-lib": "firestarter",
    "app-pkg": "firestarter_app",
    "app-tests": "firestarter_app",
    "app-tools": "firestarter_app",
}


def survey_candidates(fw_root: Path, app_root: Path) -> dict[str, list[tuple[int, str]]]:
    """The candidate swept-file set, keyed by workspace-relative path.

    Value is the list of (lineno, text) provenance hit lines in that file, so
    callers get both the candidate set AND each file's FIRST hit line (the
    "shifting citation" boundary) from one authority.
    """
    import survey_provenance  # noqa: PLC0415 -- deliberate: sibling authority

    out: dict[str, list[tuple[int, str]]] = {}
    for group, (kind, subdir) in survey_provenance._GROUPS.items():
        root = fw_root if kind == "fw" else app_root
        files = survey_provenance._scan_candidate_files(root / subdir, root)
        if not files:
            continue
        scanned = survey_provenance._scan_hits(files, root)
        prefix = GROUP_ROOT_NAME[group]
        for rel, hits in scanned["file_hit_lines"].items():
            out[f"{prefix}/{rel}"] = list(hits)
    return out


# ---------------------------------------------------------------------------
# --self-check: resolve a fixed probe set against the REAL candidate index and
# assert each probe lands in its expected class. Prints the index size and a
# per-resolution breakdown, so a PASS naming zero candidates is visibly wrong.
# ---------------------------------------------------------------------------
_PROBES: Sequence[tuple[str, str]] = (
    ("firestarter/src/proms/eeprom_28c.cpp", EXACT),
    ("src/proms/eeprom_28c.cpp", SUFFIX),
    ("eeprom_28c.cpp", BASENAME),
    ("firestarter.h", BASENAME),
    ("host_stubs.cpp", AMBIGUOUS),
    ("database.c", UNRESOLVED),
    ("../firestarter/include/rurp_shield.h", REJECTED),
    ("/workspaces/firestarter/src/firestarter.cpp", REJECTED),
)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description="Shared citation path-resolution rule (v1.33). "
        "Roots are explicit arguments and are never derived from the module's "
        "own location.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--fw-root", required=True, help="firestarter (firmware) repo root")
    ap.add_argument("--app-root", required=True, help="firestarter_app (host) repo root")
    ap.add_argument(
        "--self-check",
        action="store_true",
        help="resolve the built-in probe set against the real candidate index",
    )
    args = ap.parse_args(argv)

    fw_root = Path(args.fw_root)
    app_root = Path(args.app_root)
    for label, root in (("--fw-root", fw_root), ("--app-root", app_root)):
        if not root.is_dir():
            print(
                f"ERROR: {label} does not exist or is not a directory: {root}",
                file=sys.stderr,
            )
            sys.exit(2)

    candidates = survey_candidates(fw_root.resolve(), app_root.resolve())
    if not candidates:
        print(
            "ERROR: the candidate swept-file set is EMPTY -- silence is never "
            "success (D-09: exit non-zero on an empty input set).",
            file=sys.stderr,
        )
        sys.exit(2)

    index = CandidateIndex(
        {"firestarter": fw_root, "firestarter_app": app_root}, candidates.keys()
    )

    if not args.self_check:
        print(f"index size: {len(index)} candidate swept files")
        sys.exit(0)

    counts: Counter[str] = Counter()
    failures: list[str] = []
    print(f"index size: {len(index)} candidate swept files")
    print(f"{'probe':<52} {'expected':<11} {'actual':<11} verdict")
    for cited, expected in _PROBES:
        try:
            got = index.resolve(cited)
        except FixtureResolutionError as exc:
            failures.append(f"{cited}: fixture guard fired: {exc}")
            counts["<guard-raised>"] += 1
            print(f"{cited:<52} {expected:<11} {'RAISED':<11} FAIL")
            continue
        counts[got.resolution] += 1
        ok = got.resolution == expected
        if not ok:
            failures.append(
                f"{cited}: expected {expected}, got {got.resolution} "
                f"(path={got.path!r}, reason={got.reason})"
            )
        print(
            f"{cited:<52} {expected:<11} {got.resolution:<11} "
            f"{'ok' if ok else 'FAIL'}"
        )

    print()
    print("per-resolution counts over the probe set:")
    for name in RESOLUTIONS:
        print(f"  {name:<12} {counts.get(name, 0)}")

    if failures:
        print(f"\nFAIL: {len(failures)} probe(s) resolved to the wrong class:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        print(f"Total: {len(failures)} violation(s). Exit 1 (BLOCK).", file=sys.stderr)
        sys.exit(1)

    print(
        f"\nPASS: {len(_PROBES)} probes, all resolved to their expected class "
        f"against an index of {len(index)} candidate swept files."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
