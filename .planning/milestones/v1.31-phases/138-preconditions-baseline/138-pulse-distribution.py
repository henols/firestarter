#!/usr/bin/env python3
"""138-02 pulse-distribution: re-derives the live, per-protocol `pulse_duration`
distribution for algorithms 0x07 / 0x08 / 0x0B from the shipped
chip_database.json (PREP-04), as C2's committed evidence for the gh#15
correction Phase 139 posts publicly ("pulse width is DATA, not a
per-protocol constant"). This is a MEASUREMENT script: it re-derives the
figures from the live database rather than restating them from the seed or
from 138-RESEARCH.md, and it treats any divergence from either as a finding,
never a silent reconciliation.

Numbered assertions. Assertions 1-4 and 6 each produce a `violations` entry
(or entries) on failure; assertion 5 is a reporting obligation only (it has
nothing to fail -- it exists so a reader can independently pin the exact
input this run measured):

  1. Denominator completeness -- for each of 0x07/0x08/0x0B, the sum of all
     bucket counts plus all histogram counts equals the number of scanned
     entries carrying that algorithm. No chip is dropped from the count.
  2. Whole-database closure -- the count of entries on the three target
     protocols plus the count on every other protocol equals the total
     number of chip entries scanned, with the crossover in both directions
     (a target id leaking into the "other" bucket, and an entry misfiled
     into the wrong target bucket) reported as a number whether zero or
     not -- only a broken partition is a violation.
  3. C2's claim is testable, not assumed -- for each target protocol with at
     least one scanned chip, report the modal parsed value (count + share)
     and the number of DISTINCT parsed values. A protocol with zero or one
     distinct numeric value would make C2 ("pulse width is DATA, not a
     per-protocol constant") untestable or falsified for that protocol --
     that outcome is a violation, reported as one, never silently narrated.
     gh#15's own three constants are deliberately NOT hardcoded here --
     Phase 139 sources those from the issue itself.
  4. The imported parser is the production one -- live-assert
     `_parse_pulse_duration('100 us') == 100`, `('100us') == 0`,
     `('100 US') == 0` and `('') == 0`, and print the resolved
     `firestarter.database.__file__` so the artifact records exactly which
     copy on disk was imported.
  5. Blob identity -- print the git blob SHA (40 hex chars) of the database
     path actually read, or of the `DB_REF` blob when that seam is used, so
     the committed artifact pins the exact input byte-for-byte.
  6. Synthetic self-test, run BEFORE the real scan -- a small in-script
     synthetic database exercises every bucket kind at least once (a
     missing key, an empty string, "Algorithm Controlled", a non-string
     integer, "100us" as unparseable, "0 us" as explicit zero, and two
     numeric values) and the bucketing routine's output is compared
     against hand-counted expectations. This is the script's own
     non-vacuity obligation: on the REAL shipped data every one of the
     five collision buckets measures zero (138-RESEARCH.md), so without
     this synthetic leg a bucketing bug would be silently invisible --
     every other assertion would still pass vacuously. If this self-test
     fails, the script prints RESULT: FAIL and returns 1 WITHOUT printing
     any real distribution -- an untrusted bucketing routine must not be
     allowed to produce publishable numbers.

This script's own non-vacuity obligation (distinct from assertion 6's,
which is only about bucketing correctness) is that IT must be capable of
FAILING, not merely of passing: it was observed to fail live, for an
attributable reason, against a deliberately planted `DB_PATH` input before
this script's PASS was ever relied on -- see 138-02-PULSE-DISTRIBUTION.md
for the verbatim failing run and the two verbatim passing runs.

Exit-code contract: exits 0 and prints a line exactly `RESULT: PASS` when
`VIOLATIONS: 0`; exits 1 and prints a line exactly `RESULT: FAIL` when one
or more violations are found (including a self-test failure, in which case
no distribution is printed at all).

Env-var seams (no argparse -- this stays a standing, re-runnable regression
proof, not a one-shot with hardcoded paths), each read at most once:

  SUBMODULE_DIR -- the firestarter_app git checkout to read from and to run
                   `git` against (default: /workspaces/firestarter_app).
  DB_PATH       -- if set, read the database from this file path instead of
                   the default SUBMODULE_DIR/firestarter/data/chip_database.json.
                   Read directly with `open()` -- never by constructing an
                   `EpromDatabase` instance, which would merge in a
                   `~/.firestarter/database.json` local override and skew
                   the very figure this script exists to measure (T-138-06).
  DB_REF        -- if set (and DB_PATH is not), read the database via
                   `git -C SUBMODULE_DIR show REF:firestarter/data/chip_database.json`
                   instead of from a path -- e.g. DB_REF=origin/beta proves
                   the figure is a property of the shipped database, not of
                   whatever happens to be checked out in the worktree right now.

Never eval, never exec, never follows a path outside the three seams above.
A non-string `pulse_duration` is routed to the `non-string` bucket and
reported -- it is never passed into `_parse_pulse_duration`, which raises
`AttributeError` on a non-string argument (T-138-09).
"""

import collections
import json
import os
import subprocess
import sys

_TARGET_PROTOCOLS = (0x07, 0x08, 0x0B)  # NOT gh#15's own constants -- Phase 139 sources those from the issue
_BUCKET_KINDS = (
    "absent",
    "non-string",
    "empty",
    "algorithm-controlled",
    "unparseable",
    "explicit-zero",
)

_SUBMODULE_DIR = os.environ.get("SUBMODULE_DIR", "/workspaces/firestarter_app")
_DB_REL_PATH = "firestarter/data/chip_database.json"
_DEFAULT_DB_PATH = os.path.join(_SUBMODULE_DIR, "firestarter", "data", "chip_database.json")

# Insert at position 0 (never append): this must win immediately over any
# same-named namespace-package portion the path-based finder could
# otherwise assemble from an unrelated sys.path entry. Concretely: a
# cwd-relative `firestarter` directory -- the SIBLING FIRMWARE SUBMODULE has
# exactly this name and no __init__.py -- was observed, this session, to be
# picked up as a bogus namespace-package portion for `import firestarter`
# under some invocation styles (e.g. `python3 -c`, where cwd joins
# sys.path). Inserting the real package's parent directory first makes
# resolution correct regardless of cwd or invocation style.
sys.path.insert(0, _SUBMODULE_DIR)
from firestarter.database import _parse_pulse_duration  # noqa: E402 -- the production parser, D-11, never reimplemented
import firestarter.database as _database_module  # noqa: E402 -- only to report __file__ (assertion 4)


def _classify_one(programming: dict, parse_fn) -> tuple:
    """Classify one chip's `programming` dict by its RAW `pulse_duration`
    string, never by the parsed integer (D-11): the parsed 0 is a four-way
    collision across "0 us", "", "Algorithm Controlled" and malformed input,
    so branching on the parsed value alone would conflate all four.

    Returns (kind, detail, parsed_us_or_None). `kind` is one of
    _BUCKET_KINDS, or "numeric" for a genuine, non-collision parsed value.
    `detail` is a human-readable sub-label, reporting-only.
    """
    if "pulse_duration" not in programming:
        return "absent", "pulse_duration key missing", None
    raw = programming["pulse_duration"]
    if not isinstance(raw, str):
        return "non-string", f"non-string:{type(raw).__name__}", None
    if raw == "":
        return "empty", "empty string", None
    if raw == "Algorithm Controlled":
        return "algorithm-controlled", raw, None
    if raw == "0 us":
        return "explicit-zero", raw, None
    parsed = parse_fn(raw)
    if parsed == 0:
        # Not one of the three named zero-producing shapes above, yet the
        # parser still returned 0 -- malformed/unrecognised input (e.g.
        # "100us", "100 US", "1 ms"). Never folded into a different bucket.
        return "unparseable", f"unparseable:{raw!r}", None
    return "numeric", None, parsed


def _bucket_protocol_entries(programming_list, parse_fn):
    """Bucket every `programming` dict in `programming_list` (all sharing
    one protocol). Returns (bucket_counts, bucket_detail, histogram)."""
    bucket_counts = {k: 0 for k in _BUCKET_KINDS}
    bucket_detail = {k: collections.Counter() for k in _BUCKET_KINDS}
    histogram: collections.Counter = collections.Counter()
    for programming in programming_list:
        kind, detail, parsed = _classify_one(programming, parse_fn)
        if kind == "numeric":
            histogram[parsed] += 1
        else:
            bucket_counts[kind] += 1
            bucket_detail[kind][detail] += 1
    return bucket_counts, bucket_detail, histogram


def _run_selftest() -> list:
    """Assertion 6. Runs BEFORE the real scan, on a small in-script
    synthetic database -- never on repository or submodule data."""
    synthetic_programmings = [
        {"algorithm": 0x07},                                             # absent
        {"algorithm": 0x07, "pulse_duration": ""},                       # empty
        {"algorithm": 0x07, "pulse_duration": "Algorithm Controlled"},   # algorithm-controlled
        {"algorithm": 0x07, "pulse_duration": 100},                      # non-string
        {"algorithm": 0x07, "pulse_duration": "100us"},                  # unparseable (no space)
        {"algorithm": 0x07, "pulse_duration": "0 us"},                   # explicit-zero
        {"algorithm": 0x07, "pulse_duration": "100 us"},                 # numeric #1
        {"algorithm": 0x07, "pulse_duration": "200 us"},                 # numeric #2
    ]
    expected_bucket_counts = {
        "absent": 1,
        "non-string": 1,
        "empty": 1,
        "algorithm-controlled": 1,
        "unparseable": 1,
        "explicit-zero": 1,
    }
    expected_histogram = {100: 1, 200: 1}

    violations = []
    total_hand_counted = sum(expected_bucket_counts.values()) + sum(expected_histogram.values())
    if total_hand_counted != len(synthetic_programmings):
        violations.append(
            f"assertion 6 (self-test): the hand-counted expectations sum to "
            f"{total_hand_counted}, not {len(synthetic_programmings)} -- fix the self-test itself"
        )

    bucket_counts, _detail, histogram = _bucket_protocol_entries(synthetic_programmings, _parse_pulse_duration)

    for kind, expected_count in expected_bucket_counts.items():
        if bucket_counts[kind] != expected_count:
            violations.append(
                f"assertion 6 (self-test): bucket '{kind}' expected {expected_count}, "
                f"got {bucket_counts[kind]} -- the bucketing routine is broken"
            )
    if dict(histogram) != expected_histogram:
        violations.append(
            f"assertion 6 (self-test): numeric histogram expected {expected_histogram}, "
            f"got {dict(histogram)} -- the bucketing routine is broken"
        )
    return violations


def _verify_parser_identity(parse_fn) -> list:
    """Assertion 4: prove the imported callable behaves like the real,
    documented production `_parse_pulse_duration` -- not a stale copy, not
    a monkeypatch, not an accidentally-shadowed same-named function."""
    violations = []
    checks = (
        ("100 us", 100),
        ("100us", 0),
        ("100 US", 0),
        ("", 0),
    )
    for raw, expected in checks:
        actual = parse_fn(raw)
        if actual != expected:
            violations.append(
                f"assertion 4 (parser identity): _parse_pulse_duration({raw!r}) "
                f"returned {actual!r}, expected {expected!r} -- the imported callable "
                f"does not match the documented production shape"
            )
    return violations


def _hex(protocol: int) -> str:
    return "0x%02X" % protocol


def _git_hash_object(path: str) -> str:
    result = subprocess.run(
        ["git", "-C", _SUBMODULE_DIR, "hash-object", path],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _git_blob_sha_for_ref(ref: str) -> str:
    result = subprocess.run(
        ["git", "-C", _SUBMODULE_DIR, "rev-parse", f"{ref}:{_DB_REL_PATH}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _load_database():
    """Load chip_database.json per the three documented env-var seams.
    Returns (db, provenance, blob_sha)."""
    db_path_override = os.environ.get("DB_PATH")
    db_ref = os.environ.get("DB_REF")

    if db_path_override:
        with open(db_path_override) as f:
            db = json.load(f)
        blob_sha = _git_hash_object(db_path_override)
        provenance = f"DB_PATH={db_path_override}"
        return db, provenance, blob_sha

    if db_ref:
        result = subprocess.run(
            ["git", "-C", _SUBMODULE_DIR, "show", f"{db_ref}:{_DB_REL_PATH}"],
            capture_output=True,
            text=True,
            check=True,
        )
        db = json.loads(result.stdout)
        blob_sha = _git_blob_sha_for_ref(db_ref)
        provenance = f"DB_REF={db_ref} (git -C {_SUBMODULE_DIR} show {db_ref}:{_DB_REL_PATH})"
        return db, provenance, blob_sha

    with open(_DEFAULT_DB_PATH) as f:
        db = json.load(f)
    blob_sha = _git_hash_object(_DEFAULT_DB_PATH)
    provenance = f"default path {_DEFAULT_DB_PATH}"
    return db, provenance, blob_sha


def _scan_whole_database(db):
    """One full pass over every chip entry in every manufacturer's list.
    Returns (total_scanned, target_counts, other_algo_counts, entries_by_protocol)."""
    total_scanned = 0
    target_counts = {p: 0 for p in _TARGET_PROTOCOLS}
    other_algo_counts: collections.Counter = collections.Counter()
    entries_by_protocol: dict = {p: [] for p in _TARGET_PROTOCOLS}

    for _mfr, chips in db.items():
        if not isinstance(chips, list):
            continue
        for entry in chips:
            total_scanned += 1
            programming = entry.get("programming") if isinstance(entry, dict) else None
            if not isinstance(programming, dict):
                programming = {}
            algorithm = programming.get("algorithm")
            if algorithm in _TARGET_PROTOCOLS:
                target_counts[algorithm] += 1
                entries_by_protocol[algorithm].append(programming)
            else:
                other_algo_counts[algorithm] += 1

    return total_scanned, target_counts, other_algo_counts, entries_by_protocol


def main() -> int:
    # Assertion 6 -- must run first, and gate everything else.
    selftest_violations = _run_selftest()
    if selftest_violations:
        print("=" * 78)
        print("Phase 138 Plan 02 -- PREP-04: pulse-width distribution -- SELF-TEST FAILED")
        print("=" * 78)
        print()
        print("The synthetic self-test (assertion 6) did not bucket every hand-counted")
        print("case as expected. On the real shipped database every collision bucket")
        print("measures zero (138-RESEARCH.md), so a broken bucketing routine would")
        print("otherwise be invisible -- every other assertion would pass vacuously.")
        print("No real distribution is printed while this fails; it cannot be trusted.")
        print()
        print(f"VIOLATIONS: {len(selftest_violations)}")
        for v in selftest_violations:
            print(f"  - {v}")
        print()
        print("RESULT: FAIL")
        return 1

    violations: list = []
    violations.extend(_verify_parser_identity(_parse_pulse_duration))

    db, provenance, blob_sha = _load_database()
    total_scanned, target_counts, other_algo_counts, entries_by_protocol = _scan_whole_database(db)

    target_total = sum(target_counts.values())
    other_total = sum(other_algo_counts.values())
    leaked_target_ids_in_other = sorted(a for a in other_algo_counts if a in _TARGET_PROTOCOLS)
    misfiled = [
        (p, programming.get("algorithm"))
        for p in _TARGET_PROTOCOLS
        for programming in entries_by_protocol[p]
        if programming.get("algorithm") != p
    ]

    if target_total + other_total != total_scanned:
        violations.append(
            f"assertion 2 (whole-database closure): target_total({target_total}) + "
            f"other_total({other_total}) != total_scanned({total_scanned})"
        )
    if leaked_target_ids_in_other:
        violations.append(
            f"assertion 2 (whole-database closure): target-protocol id(s) "
            f"{leaked_target_ids_in_other} found inside the 'other' bucket -- broken partition"
        )
    if misfiled:
        violations.append(
            f"assertion 2 (whole-database closure): {len(misfiled)} entry(ies) misfiled "
            f"into the wrong target bucket: {misfiled[:5]}"
        )

    per_protocol = {}
    for p in _TARGET_PROTOCOLS:
        n = target_counts[p]
        bucket_counts, bucket_detail, histogram = _bucket_protocol_entries(
            entries_by_protocol[p], _parse_pulse_duration
        )
        accounted = sum(bucket_counts.values()) + sum(histogram.values())
        if accounted != n:
            violations.append(
                f"assertion 1 (denominator completeness) protocol {_hex(p)}: "
                f"bucket+histogram total {accounted} != scanned n {n} "
                f"({n - accounted} chip(s) unaccounted for)"
            )

        distinct_count = len(histogram)
        if histogram:
            modal_value, modal_count = max(histogram.items(), key=lambda kv: (kv[1], -kv[0]))
            share = (modal_count / n * 100.0) if n else 0.0
        else:
            modal_value, modal_count, share = None, 0, 0.0

        if n > 0 and distinct_count == 0:
            violations.append(
                f"assertion 3 (C2 testability) protocol {_hex(p)}: {n} chip(s) scanned but "
                f"ZERO carry a numeric parsed value -- C2 cannot be tested at all for this protocol"
            )
        elif n > 0 and distinct_count == 1:
            violations.append(
                f"assertion 3 (C2 testability) protocol {_hex(p)}: only 1 distinct parsed "
                f"value among {n} chip(s) -- this FALSIFIES C2 ('pulse width is DATA, not a "
                f"per-protocol constant') for this protocol"
            )

        per_protocol[p] = {
            "n": n,
            "bucket_counts": bucket_counts,
            "bucket_detail": bucket_detail,
            "histogram": histogram,
            "distinct_count": distinct_count,
            "modal_value": modal_value,
            "modal_count": modal_count,
            "share": share,
        }

    # ---------------------------------------------------------------- output
    print("=" * 78)
    print("Phase 138 Plan 02 -- PREP-04: live per-protocol pulse-width distribution")
    print("(0x07 / 0x08 / 0x0B), re-derived this milestone from the shipped")
    print("chip_database.json -- C2's committed evidence for the gh#15 correction.")
    print("=" * 78)
    print()
    print("LAYER: chip_database.json carries `pulse_duration` as a STRING, e.g.")
    print('"100 us". firestarter/database.py:128 (`_parse_pulse_duration`) converts')
    print("that string into the integer-microsecond wire field `pulse-delay` that is")
    print("actually sent to the firmware. REQUIREMENTS.md's wording (`pulse_duration`)")
    print("and PROJECT.md's wording (`pulse_delay`) are both correct at different layers")
    print("-- the database layer and the wire layer, respectively -- and need no")
    print("reconciliation.")
    print()

    for p in _TARGET_PROTOCOLS:
        r = per_protocol[p]
        print(f"Protocol {_hex(p)} (n = {r['n']}):")
        ordered = sorted(r["histogram"].items(), key=lambda kv: (-kv[1], kv[0]))
        if ordered:
            hist_str = ", ".join(f"{us}us x{c}" for us, c in ordered)
        else:
            hist_str = "(no numeric values recorded)"
        print(f"  histogram (parsed us x count, descending by count): {hist_str}")
        if r["modal_value"] is not None:
            print(
                f"  modal value: {r['modal_value']}us, count {r['modal_count']}, "
                f"share {r['share']:.1f}% of n={r['n']}"
            )
        else:
            print("  modal value: UNDEFINED (no numeric values recorded for this protocol)")
        print(f"  distinct parsed values: {r['distinct_count']}")
        print()

    print("Bucket table (buckets from the RAW string, never the parsed int -- D-11.")
    print("All six kinds are named below even where they measure zero):")
    col_w = 8
    header = "  {:<22}".format("bucket") + "".join(f"{_hex(p):>{col_w}}" for p in _TARGET_PROTOCOLS)
    print(header)
    print("  " + "-" * (22 + col_w * len(_TARGET_PROTOCOLS)))
    for kind in _BUCKET_KINDS:
        row = "  {:<22}".format(kind) + "".join(
            f"{per_protocol[p]['bucket_counts'][kind]:>{col_w}}" for p in _TARGET_PROTOCOLS
        )
        print(row)
    print()

    print(
        f"Whole-database partition: {target_total} chips on {{0x07,0x08,0x0B}} + "
        f"{other_total} chips on every other protocol = {total_scanned} total chips scanned"
    )
    print(
        f"  crossover (target-protocol id found inside the 'other' bucket): "
        f"{len(leaked_target_ids_in_other)}"
        + (f" {leaked_target_ids_in_other}" if leaked_target_ids_in_other else "")
    )
    print(f"  crossover (entry misfiled into the wrong target bucket): {len(misfiled)}")
    print()

    print(f"Resolved parser module (firestarter.database.__file__): {_database_module.__file__}")
    print(f"Database read from: {provenance}")
    print(f"Database blob SHA (git blob object id, 40 hex chars): {blob_sha}")
    print()

    print(f"VIOLATIONS: {len(violations)}")
    if violations:
        for v in violations:
            print(f"  - {v}")
    print("RESULT: " + ("PASS" if not violations else "FAIL"))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
