#!/usr/bin/env python3
"""check_rebuild.py -- SC#1's reproduce-or-record-the-cause gate (RIG-01).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo. Pure standard library.

WHAT THIS TOOL DOES
--------------------
For each (arm, env) pair in scope it re-hashes `firestarter_<env>.<arm>.hex` found under
`--images DIR` and compares that hash against the recorded hash for the SAME filename in
`--expect FILE` (a plain `sha256sum`-format manifest, e.g. SHA256SUMS.txt). Two invocation
shapes:

  1. Self-check (both flags default to the same committed `images/` directory): confirms the
     six committed artifacts still match their own recorded manifest -- a bit-rot / silent-
     overwrite detector, re-runnable at any time.
  2. Cold-rebuild verification (`--images` points at a directory of freshly rebuilt `.hex`
     files, `--expect` still names the ORIGINAL manifest): confirms a fresh `pio run` produces
     byte-identical output to the committed image. On a mismatch, the ORIGINAL reference file
     is located as a sibling of `--expect` (its parent directory) and a `cmp`-style byte-level
     diff (first 20 differing offsets) is produced against it, so the divergence is
     investigable rather than a bare hash inequality.

No SHA-256 value is ever hardcoded in this file -- every expected hash is read from
`--expect` at runtime, and every actual hash is recomputed fresh from the file on disk.

FAIL-CLOSED ON ABSENCE
-----------------------
This project has already shipped a gate that scanned nothing and exited 0. This tool never
does: a missing `--images` directory, an empty one, or one holding fewer than the expected
number of `.hex` files (`len(--arms) * len(--envs)`) is a `FAIL:` line naming exactly what
was missing, with a non-zero exit -- never a silent pass.

SC#1's OWN PERMISSION
----------------------
A divergence with a measured `divergence_cause` is a legitimate SC#1 outcome; a SILENT one
is not. This tool's non-zero exit on mismatch is the mechanism that forces the cause to be
written down (into the JSON `results` entry's `divergence_cause` field) rather than glossed
over.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_IMAGES = _HERE.parent / "images"

_DEFAULT_ARMS = ("control", "v133")
_DEFAULT_ENVS = ("uno", "uno328pb", "leonardo")

_SHA256SUMS_LINE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+)$")


# ---------------------------------------------------------------------------
# Pure logic -- no filesystem I/O beyond what callers hand in as bytes/text.
# Exercised directly by --selftest.
# ---------------------------------------------------------------------------


def parse_sha256sums(text: str) -> dict[str, str]:
    """Parse plain `sha256sum` output into {filename: lowercase_hex_hash}."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = _SHA256SUMS_LINE.match(line)
        if not m:
            continue
        digest, filename = m.group(1).lower(), m.group(2).strip()
        out[filename] = digest
    return out


def cmp_style_diff(expected: bytes, actual: bytes, limit: int = 20) -> tuple[int, str]:
    """Return (total_diff_count, human report of the first `limit` differing byte
    positions), cmp(1)-style. A length mismatch is reported as a MISSING byte on the
    shorter side rather than silently truncating the comparison."""
    n = max(len(expected), len(actual))
    diffs: list[tuple[int, int, int]] = []
    total = 0
    for i in range(n):
        eb = expected[i] if i < len(expected) else -1
        ab = actual[i] if i < len(actual) else -1
        if eb != ab:
            total += 1
            if len(diffs) < limit:
                diffs.append((i, eb, ab))
    if not diffs:
        return 0, ""
    parts = []
    for off, eb, ab in diffs:
        e_str = f"0x{eb:02X}" if eb >= 0 else "MISSING"
        a_str = f"0x{ab:02X}" if ab >= 0 else "MISSING"
        parts.append(f"offset=0x{off:05X} expected={e_str} actual={a_str}")
    report = (
        f"{total} differing byte(s), first {len(diffs)} shown: " + "; ".join(parts)
    )
    return total, report


def image_filename(env: str, arm: str) -> str:
    return f"firestarter_{env}.{arm}.hex"


def expected_pairs(arms: list[str], envs: list[str]) -> list[tuple[str, str]]:
    return [(arm, env) for arm in arms for env in envs]


# ---------------------------------------------------------------------------
# Filesystem-touching verification
# ---------------------------------------------------------------------------


def verify(
    images_dir: Path, expect_path: Path, arms: list[str], envs: list[str]
) -> tuple[list[str], list[dict], list[str]]:
    """Returns (fatal_errors, results, missing_files).

    `fatal_errors` non-empty means the fail-closed path fired (bad/missing/empty
    `--images`, unreadable/empty `--expect`) and no per-pair verification ran at all.
    """
    fatal: list[str] = []

    if not images_dir.exists():
        fatal.append(f"--images directory does not exist: {images_dir}")
        return fatal, [], []
    if not images_dir.is_dir():
        fatal.append(f"--images path is not a directory: {images_dir}")
        return fatal, [], []

    hex_files = sorted(p for p in images_dir.iterdir() if p.suffix == ".hex")
    if not hex_files:
        fatal.append(f"--images directory contains no .hex files: {images_dir}")
        return fatal, [], []

    pairs = expected_pairs(arms, envs)
    expected_names = {image_filename(env, arm) for arm, env in pairs}
    present_names = {p.name for p in hex_files}
    missing_expected = sorted(expected_names - present_names)
    if len(hex_files) < len(pairs):
        fatal.append(
            f"--images directory holds {len(hex_files)} .hex file(s), fewer than the "
            f"{len(pairs)} expected for {len(arms)} arm(s) x {len(envs)} env(s); missing: "
            f"{missing_expected}"
        )
        return fatal, [], missing_expected

    if not expect_path.exists():
        fatal.append(f"--expect file does not exist: {expect_path}")
        return fatal, [], []
    expect_text = expect_path.read_text(encoding="utf-8")
    if not expect_text.strip():
        fatal.append(f"--expect file is empty: {expect_path}")
        return fatal, [], []
    expected_hashes = parse_sha256sums(expect_text)
    if not expected_hashes:
        fatal.append(f"--expect file has no parseable sha256sum-format lines: {expect_path}")
        return fatal, [], []

    reference_dir = expect_path.parent
    results: list[dict] = []
    missing: list[str] = list(missing_expected)

    for arm, env in pairs:
        filename = image_filename(env, arm)
        candidate_path = images_dir / filename
        entry = {"arm": arm, "env": env, "file": filename}

        if not candidate_path.exists():
            entry.update(
                expected_sha256=expected_hashes.get(filename),
                actual_sha256=None,
                match=False,
                divergence_cause=f"candidate file missing: {candidate_path}",
            )
            results.append(entry)
            if filename not in missing:
                missing.append(filename)
            continue

        actual_bytes = candidate_path.read_bytes()
        actual_sha = hashlib.sha256(actual_bytes).hexdigest()
        expected_sha = expected_hashes.get(filename)

        if expected_sha is None:
            entry.update(
                actual_sha256=actual_sha,
                expected_sha256=None,
                match=False,
                divergence_cause=f"{filename!r} is not present in manifest {expect_path}",
            )
            results.append(entry)
            continue

        match = actual_sha == expected_sha
        divergence_cause = None
        if not match:
            reference_path = reference_dir / filename
            same_file = False
            try:
                same_file = reference_path.resolve() == candidate_path.resolve()
            except OSError:
                same_file = False
            if reference_path.exists() and not same_file:
                ref_bytes = reference_path.read_bytes()
                _total, report = cmp_style_diff(ref_bytes, actual_bytes)
                divergence_cause = (
                    f"sha256 mismatch against manifest (expected {expected_sha}, got "
                    f"{actual_sha}); byte-level diff against reference {reference_path}: "
                    f"{report}"
                )
            else:
                divergence_cause = (
                    f"sha256 mismatch against manifest (expected {expected_sha}, got "
                    f"{actual_sha}); no separate reference file available for a "
                    "byte-level diff"
                )
        entry.update(
            actual_sha256=actual_sha,
            expected_sha256=expected_sha,
            match=match,
            divergence_cause=divergence_cause,
        )
        results.append(entry)

    return fatal, results, missing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--images", default=str(_DEFAULT_IMAGES), help="directory holding .hex files to verify")
    ap.add_argument(
        "--expect",
        default=None,
        help="sha256sum-format manifest to check against (default: <images>/SHA256SUMS.txt)",
    )
    ap.add_argument("--arms", nargs="+", default=list(_DEFAULT_ARMS))
    ap.add_argument("--envs", nargs="+", default=list(_DEFAULT_ENVS))
    ap.add_argument("--out", default=None, help="write the JSON result here")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    images_dir = Path(args.images)
    expect_path = Path(args.expect) if args.expect else images_dir / "SHA256SUMS.txt"

    fatal, results, missing = verify(images_dir, expect_path, list(args.arms), list(args.envs))

    if fatal:
        for f in fatal:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1

    all_match = all(r["match"] for r in results) and not missing

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "images_dir": str(images_dir),
            "expect_file": str(expect_path),
            "arms": list(args.arms),
            "envs": list(args.envs),
            "results": results,
            "missing": missing,
            "all_match": all_match,
        }
        tmp = out_path.with_name(out_path.name + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(out_path)

    if not all_match:
        for r in results:
            if not r["match"]:
                print(f"FAIL: {r['file']} (arm={r['arm']} env={r['env']}): {r['divergence_cause']}", file=sys.stderr)
        if missing:
            print(f"FAIL: missing image(s): {missing}", file=sys.stderr)
        return 1

    print(
        f"OK: check_rebuild -- {len(results)} (arm, env) pair(s) verified against "
        f"{expect_path}, all hashes match"
    )
    return 0


# ---------------------------------------------------------------------------
# --selftest: on-disk fixtures in a temp directory. No device, no pio, no
# network. Three positive/negative legs, each named.
# ---------------------------------------------------------------------------


def _run_selftest() -> int:
    import shutil
    import tempfile

    ok_overall = True

    def report(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok_overall
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok_overall = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    tmp = Path(tempfile.mkdtemp(prefix="check_rebuild_selftest_"))
    try:
        arms = ["armA"]
        envs = ["envA", "envB"]

        # --- positive fixture: a small synthetic committed image set whose
        # hashes match its own manifest ---
        committed = tmp / "committed"
        committed.mkdir()
        contents = {}
        for arm, env in expected_pairs(arms, envs):
            fname = image_filename(env, arm)
            data = f"synthetic-{env}-{arm}".encode() * 8
            (committed / fname).write_bytes(data)
            contents[fname] = data
        lines = [f"{hashlib.sha256(d).hexdigest()}  {n}" for n, d in contents.items()]
        (committed / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

        fatal, results, missing = verify(committed, committed / "SHA256SUMS.txt", arms, envs)
        report(
            "positive: matching committed image set passes",
            not fatal and not missing and all(r["match"] for r in results),
            f"fatal={fatal} missing={missing}",
        )

        # --- negative fixture 1: one byte flipped in a "rebuilt" copy,
        # checked against the ORIGINAL manifest -- must fail, name the file,
        # and report differing byte positions ---
        rebuilt = tmp / "rebuilt"
        rebuilt.mkdir()
        flipped_name = image_filename("envA", "armA")
        for name, data in contents.items():
            if name == flipped_name:
                data = bytearray(data)
                data[3] = (data[3] + 1) % 256
                data = bytes(data)
            (rebuilt / name).write_bytes(data)

        fatal2, results2, missing2 = verify(rebuilt, committed / "SHA256SUMS.txt", arms, envs)
        flipped_entry = next((r for r in results2 if r["file"] == flipped_name), None)
        report(
            "negative 1: one-byte-flipped rebuild is caught, names the file and offset",
            (not fatal2)
            and flipped_entry is not None
            and not flipped_entry["match"]
            and "offset=0x00003" in (flipped_entry["divergence_cause"] or ""),
            f"entry={flipped_entry}",
        )
        other_name = image_filename("envB", "armA")
        other_entry = next((r for r in results2 if r["file"] == other_name), None)
        report(
            "negative 1b: the untouched sibling image still matches",
            other_entry is not None and other_entry["match"],
            f"entry={other_entry}",
        )

        # --- negative fixture 2: fail-closed on an empty images directory --
        # must produce a non-zero exit, not a pass ---
        empty_dir = tmp / "empty"
        empty_dir.mkdir()
        fatal3, results3, missing3 = verify(empty_dir, empty_dir / "SHA256SUMS.txt", arms, envs)
        report(
            "negative 2: empty images directory fails closed (no silent pass)",
            bool(fatal3) and not results3,
            f"fatal={fatal3}",
        )

        # --- negative fixture 3: --images path does not exist at all ---
        fatal4, results4, missing4 = verify(
            tmp / "does-not-exist", committed / "SHA256SUMS.txt", arms, envs
        )
        report(
            "negative 3: nonexistent --images directory fails closed",
            bool(fatal4) and not results4,
            f"fatal={fatal4}",
        )

        # --- negative fixture 4: fewer images present than (arms x envs) expects ---
        partial = tmp / "partial"
        partial.mkdir()
        only_name = image_filename("envA", "armA")
        (partial / only_name).write_bytes(contents[only_name])
        fatal5, results5, missing5 = verify(partial, committed / "SHA256SUMS.txt", arms, envs)
        report(
            "negative 4: fewer .hex files than arms x envs expects fails closed",
            bool(fatal5),
            f"fatal={fatal5}",
        )

        # --- cmp_style_diff / parse_sha256sums unit checks ---
        total, rep = cmp_style_diff(b"\x00\x01\x02", b"\x00\x99\x02")
        report("unit: cmp_style_diff finds exactly one differing byte", total == 1 and "offset=0x00001" in rep, rep)
        parsed = parse_sha256sums(f"{'a' * 64}  some_file.hex\n")
        report("unit: parse_sha256sums parses a well-formed line", parsed == {"some_file.hex": "a" * 64}, str(parsed))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
