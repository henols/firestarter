#!/usr/bin/env python3
"""judge_wrv.py -- the full-device write->read->verify judge (D-10/D-11/RIG-04).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo. Nothing here shells out to
avrdude, pio, or the app -- it judges artifacts `dev consistency-check` (an ARM under test)
already produced, and it is itself the independent code path that judges them (Phase 145
D-06 / RIG-04's "the thing under test and the thing judging it must not be the same code
path" -- which bites harder here than in v1.31, because the host app is itself the arm
variable).

This tool judges a POSITION, never a command. `--written` is the image that was written
(D-12's distinct, address-attributable image per cell x chip x arm); `--reads` is the
directory `dev consistency-check --keep-files` filled with `run_NN.bin` files; `--app-verdict`
is the exit code (0/1/2) that command returned, recorded here but NEVER treated as the
verdict.

Pitfall 6 -- the false green this tool exists to prevent: `dev consistency-check`'s own
`Consistency check: PASS` means `len({sha per run}) == 1`
(`firestarter_app/firestarter/eprom_operations.py:1084-1086` on both arms) -- it compares the
N reads to EACH OTHER, never to the written image. A chip that reliably returns the WRONG
bytes still reports PASS. This is the exact false green D-12's distinct-image-per-position
insures against on the arm whose entire premise is "nothing changed" (standing memory
reference_devtest_write_repeat_emits_no_pulses_27c: a second write can be a near-no-op on
329/746 parts, LOOP-06 skipping already-correct bytes). This tool computes SHA-256 over the
full `--expect-size` bytes of EVERY read file and of the written image; the judged verdict is
`match` only when every one of them equals the written image's SHA. The app's own 0/1/2 is
recorded beside it as `app_verdict_unjudged` and NEVER substituted for the judged verdict --
`verdict_disagreement` is set whenever the app's claimed direction (0 == "the app itself is
happy") and the judged direction (`match` == "the judge itself is happy") disagree, and that
disagreement is itself the finding, reported and exited non-zero rather than resolved
(the same shape as `.planning/milestones/v1.18-artifacts/bench/check_signature.py`'s
`bits_flipped==0 XOR pre!=post` cross-check).

Note recorded for completeness: the app's printed verdict block carries a hardcoded literal
`Board: unknown-board` (`eprom_operations.py:1093`) -- not a lookup -- so nothing in that
printed block, including that field, may ever be used for board provenance.

D-11 / RIG-04's "never an exit code, never assume N": this tool globs `run_*.bin` in
`--reads` and COUNTS the files rather than assuming any N. On a hardware or serial error the
app returns exit code 2 EARLY, from inside its own run loop, before writing every file it was
asked for -- when `--app-verdict` is 2, or when zero read files are present at all, the
judged verdict is `incomplete-read-set`: reported with the actual file count, and NEVER a
retry trigger. When two or more DISTINCT SHAs appear among the read files themselves, the
judged verdict is `disagreement` -- also emitted as a recorded outcome, with every individual
read SHA listed, and never retried away (RIG-04's own wording; `n3_disagreement` is set for a
machine-readable arbitration trigger per D-11).

A read file whose size does not equal `--expect-size` (65536 for W27C512, 262144 for
W29C020 -- `rig-pins.json` chips.*.size_bytes) is recorded in `size_violations` and the
overall judged verdict is never `match` while any exist -- a short read compared by raw SHA
would otherwise look like a plain content mismatch and hide its own (size) cause.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_PINS = _HERE.parent / "rig-pins.json"
_VALID_SIZES = (65536, 262144)


# ---------------------------------------------------------------------------
# Pure judging logic -- no subprocess, no device, no app invocation.
# Exercised directly by --selftest.
# ---------------------------------------------------------------------------


def validate_expect_size(expect_size: int) -> tuple[bool, str]:
    if expect_size not in _VALID_SIZES:
        return False, (
            f"--expect-size must be one of {_VALID_SIZES} (rig-pins.json chips.*.size_bytes), "
            f"got {expect_size}"
        )
    return True, ""


def judge_position(
    written_bytes: bytes,
    read_files: list[tuple[Path, bytes]],
    expect_size: int,
    app_verdict: int,
    position_id: str,
) -> dict:
    """Judge one W->R->V position. Pure function over already-read bytes and a file list --
    no filesystem globbing, no I/O beyond what the caller already did. `read_files` order is
    whatever the caller passed; this function does not assume it encodes anything."""
    read_count = len(read_files)
    size_violations: list[dict] = []
    read_shas: list[str] = []
    read_file_strs: list[str] = []

    for rf_path, rf_bytes in read_files:
        read_file_strs.append(str(rf_path))
        if len(rf_bytes) != expect_size:
            size_violations.append({"file": str(rf_path), "size_bytes": len(rf_bytes)})
        read_shas.append(hashlib.sha256(rf_bytes).hexdigest())

    written_sha = hashlib.sha256(written_bytes).hexdigest()
    distinct_shas = sorted(set(read_shas))
    distinct_read_shas = len(distinct_shas)

    if app_verdict == 2 or read_count == 0:
        sha_verdict_judged = "incomplete-read-set"
    elif distinct_read_shas > 1:
        sha_verdict_judged = "disagreement"
    elif size_violations:
        sha_verdict_judged = "mismatch"
    elif distinct_shas[0] == written_sha:
        sha_verdict_judged = "match"
    else:
        sha_verdict_judged = "mismatch"

    judged_ok = sha_verdict_judged == "match"
    app_says_ok = app_verdict == 0
    # A disagreement between the app's own unjudged verdict and the judged SHA verdict is
    # itself the finding (Pitfall 6 / the check_signature.py precedent) -- never resolved here.
    verdict_disagreement = judged_ok != app_says_ok
    n3_disagreement = sha_verdict_judged == "disagreement"

    return {
        "position_id": position_id,
        "written_sha": written_sha,
        "expect_size": expect_size,
        "read_files": read_file_strs,
        "read_count": read_count,
        "read_shas": read_shas,
        "distinct_read_shas": distinct_read_shas,
        "sha_verdict_judged": sha_verdict_judged,
        "app_verdict_unjudged": app_verdict,
        "verdict_disagreement": verdict_disagreement,
        "n3_disagreement": n3_disagreement,
        "size_violations": size_violations,
        # No subprocess is ever invoked by this judge -- it reads pre-existing artifacts
        # only, never spawns avrdude/pio/the app itself.
        "commands": [],
    }


def load_reads(reads_dir: Path) -> list[tuple[Path, bytes]]:
    """Glob run_*.bin and COUNT the files -- never assume N (D-11/RIG-04)."""
    files = sorted(reads_dir.glob("run_*.bin"))
    return [(p, p.read_bytes()) for p in files]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--written", help="path to the image that was written")
    ap.add_argument("--reads", help="directory dev consistency-check --keep-files filled")
    ap.add_argument("--expect-size", type=int, help="65536 (W27C512) or 262144 (W29C020)")
    ap.add_argument(
        "--app-verdict", type=int, help="the exit code dev consistency-check returned (0/1/2)"
    )
    ap.add_argument("--position-id", help="cell x arm x chip identifier for this position")
    ap.add_argument("--pins", default=str(_DEFAULT_PINS), help="path to rig-pins.json")
    ap.add_argument("--out", help="write the verdict JSON here")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    required = [
        ("--written", args.written),
        ("--reads", args.reads),
        ("--expect-size", args.expect_size),
        ("--app-verdict", args.app_verdict),
        ("--position-id", args.position_id),
    ]
    missing = [name for name, val in required if val is None]
    if missing:
        print(f"FAIL: missing required argument(s): {missing}", file=sys.stderr)
        return 2

    ok, detail = validate_expect_size(args.expect_size)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 2

    written_path = Path(args.written)
    if not written_path.is_file():
        print(f"FAIL: --written file does not exist: {written_path}", file=sys.stderr)
        return 1

    reads_dir = Path(args.reads)
    if not reads_dir.is_dir():
        print(f"FAIL: --reads directory does not exist: {reads_dir}", file=sys.stderr)
        return 1

    read_files = load_reads(reads_dir)
    result = judge_position(
        written_path.read_bytes(), read_files, args.expect_size, args.app_verdict, args.position_id
    )

    out_path = Path(args.out) if args.out else Path.cwd() / f"judge_wrv.{args.position_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    tmp_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(out_path)

    success = (
        result["sha_verdict_judged"] == "match"
        and not result["size_violations"]
        and not result["verdict_disagreement"]
    )

    if not success:
        print(
            f"FAIL: position {args.position_id} judged "
            f"sha_verdict_judged={result['sha_verdict_judged']!r} "
            f"read_count={result['read_count']} distinct_read_shas={result['distinct_read_shas']} "
            f"verdict_disagreement={result['verdict_disagreement']} "
            f"size_violations={result['size_violations']}",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: position {args.position_id} judged match "
        f"read_count={result['read_count']} distinct_read_shas={result['distinct_read_shas']}"
    )
    return 0


# ---------------------------------------------------------------------------
# --selftest: synthetic fixtures in a temp directory, no device, no app.
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

    tmp = Path(tempfile.mkdtemp(prefix="judge_wrv_selftest_"))
    try:
        expect_size = 65536
        written = bytes((i % 251) for i in range(expect_size))
        other = bytes((i * 3 + 7) % 256 for i in range(expect_size))

        def reads_of(*datas: bytes) -> list[tuple[Path, bytes]]:
            return [(tmp / f"run_{i+1:02d}.bin", d) for i, d in enumerate(datas)]

        # --- positive: three reads all equal to written, app verdict 0 -> match ---
        r = judge_position(written, reads_of(written, written, written), expect_size, 0, "POS-1")
        report(
            "positive: three matching reads + app verdict 0 -> match, distinct=1, no disagreement",
            r["sha_verdict_judged"] == "match"
            and r["distinct_read_shas"] == 1
            and r["verdict_disagreement"] is False,
            str(r),
        )

        # --- negative 1: Pitfall 6 false green -- three IDENTICAL reads, all WRONG, app=0 ---
        r = judge_position(written, reads_of(other, other, other), expect_size, 0, "POS-2")
        report(
            "negative 1 (Pitfall 6): three self-consistent but wrong reads with app_verdict=0 "
            "-> mismatch AND verdict_disagreement true (the false green the app's own PASS "
            "would otherwise hide)",
            r["sha_verdict_judged"] == "mismatch" and r["verdict_disagreement"] is True,
            str(r),
        )

        # --- negative 2: two of three reads differ -> disagreement, all three SHAs listed ---
        third = bytes((b ^ 0x01) for b in written)
        r = judge_position(written, reads_of(written, written, third), expect_size, 1, "POS-3")
        report(
            "negative 2: two-of-three-differ -> disagreement, n3_disagreement true, "
            "all three read_shas present, no retry performed",
            r["sha_verdict_judged"] == "disagreement"
            and r["n3_disagreement"] is True
            and len(r["read_shas"]) == 3,
            str(r),
        )

        # --- negative 3: incomplete read set -- app signaled hw error (exit 2) ---
        r = judge_position(written, reads_of(written, written), expect_size, 2, "POS-4")
        report(
            "negative 3: app_verdict=2 (hardware/serial error) -> incomplete-read-set "
            "regardless of file count, not a retry trigger",
            r["sha_verdict_judged"] == "incomplete-read-set" and r["read_count"] == 2,
            str(r),
        )

        # --- negative 4: a read file of the wrong size ---
        short_read = written[:-1]
        r = judge_position(written, reads_of(written, written, short_read), expect_size, 1, "POS-5")
        report(
            "negative 4: a wrong-sized read file is recorded in size_violations",
            len(r["size_violations"]) == 1 and r["size_violations"][0]["size_bytes"] == expect_size - 1,
            str(r["size_violations"]),
        )

        # --- negative 5: --expect-size neither 65536 nor 262144 ---
        ok, detail = validate_expect_size(65535)
        report("negative 5: --expect-size outside {65536,262144} is rejected", not ok, detail)

        # --- negative 6: empty --reads directory -> incomplete-read-set ---
        r = judge_position(written, [], expect_size, 0, "POS-6")
        report(
            "negative 6: empty reads directory -> incomplete-read-set (read_count=0)",
            r["sha_verdict_judged"] == "incomplete-read-set" and r["read_count"] == 0,
            str(r),
        )

        # --- negative 7: missing --written file (checked at the CLI layer, not judge_position) ---
        missing_written = tmp / "does-not-exist.bin"
        report(
            "negative 7: missing --written path does not exist (CLI-layer precondition)",
            not missing_written.exists(),
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
