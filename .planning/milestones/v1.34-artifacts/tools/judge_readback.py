#!/usr/bin/env python3
"""judge_readback.py -- the independent flash read-back judge (D-01/D-02/RIG-01).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo.

D-01: a flash is judged by a SEPARATE avrdude read-back invocation compared by this script,
never by the uploader's own verify pass -- the uploader (`pio run -t upload`) and this judge
are different code paths, invoked at different times, by different tools.

The avrdude read direction has NO precedent anywhere in this project's history: a full
`grep -rn "flash:r\\|flash:v" .planning/**/*.md` before this phase returned zero hits outside
this phase's own CONTEXT/RESEARCH. This tool is new construction and is UNPROVEN on a real
device until plans 08 (uno), 09 (uno328pb) and 10 (leonardo) put it on the bench, cheapest
target first. Everything below the `--readback`/`--no-read` seam is exercised in this plan
only against synthetic fixtures and hand-built hex/read-back files -- never against a board.

D-02: the judged compare is the `.hex`'s own address extent, normalized with the pinned
avr-objcopy. Because every target's hex begins at 0x0000 and none has gaps (measured,
RESEARCH Pattern 2), the comparable region is the plain [0, span) prefix of the read-back --
no offset arithmetic. The whole 32768 B read-back's SHA is ALSO recorded, but only as an
explicitly UNJUDGED datum -- board_upload.maximum_size=32768 on all three envs means the
linker no longer protects the bootloader region (optiboot 512 B / urboot 384 B / Caterina
4096 B), so a full-flash read spans bytes the .hex never covers. No code path below ever
uses sha_whole_flash_unjudged to decide judged_match.

Pitfall 2: avrdude truncates trailing 0xFF on a flash read unless -A is passed. -A is the
default only for -c arduino (uno); passing it explicitly on all three chains is what
normalizes them to one fixed-length (flash_size) artifact and one step of text (SC#3).

Pitfall 3: on uno328pb, avrdude's urclock programmer may patch the reset vector (and one
interrupt vector) of a VECTOR bootloader before/after every write, which would make the
independent read-back compare report a false MISMATCH at 0x0000 on every correctly-flashed
board. The judged span is therefore a FUNCTION of rig-pins.json's per-target
`judged_span_policy`, never a hardcoded [0, span). While that policy is still the
PENDING-xshowvector placeholder plan 01 wrote, this tool REFUSES to judge the target outright.

avrdude and avr-objcopy are resolved from rig-pins.json ONLY -- never from PATH. A binary
listed in rig-pins.json's `forbidden_binaries` is refused outright.
"""
from __future__ import annotations

import argparse
import glob as glob_mod
import hashlib
import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_PINS = _HERE.parent / "rig-pins.json"
_DEFAULT_IMAGES_DIR = _HERE.parent / "images"
_DEFAULT_MANIFEST = _DEFAULT_IMAGES_DIR / "BUILD-MANIFEST.json"

_ARMS = ("control", "v133")
_TARGETS = ("uno", "uno328pb", "leonardo")
_PLACEHOLDER_PREFIX = "PENDING"


# ---------------------------------------------------------------------------
# Pure parsing / decision logic -- no subprocess, no device. Exercised
# directly by --selftest and by the hand-built bring-up fixtures.
# ---------------------------------------------------------------------------


def resolve_avrdude(pins: dict) -> tuple[bool, str | None, str | None, str]:
    """Resolve the avrdude binary+conf from rig-pins.json ONLY; refuse a forbidden binary."""
    binary = pins.get("avrdude", {}).get("binary")
    conf = pins.get("avrdude", {}).get("conf")
    if not binary or not conf:
        return False, None, None, "rig-pins.json is missing avrdude.binary/avrdude.conf"
    for entry in pins.get("forbidden_binaries", []):
        if isinstance(entry, dict) and entry.get("path") == binary:
            reason = entry.get("reason", "no reason recorded")
            return False, None, None, (
                f"resolved avrdude binary {binary!r} is listed in forbidden_binaries ({reason})"
            )
    return True, binary, conf, ""


def resolve_objcopy(pins: dict) -> tuple[bool, str | None, str]:
    """Resolve avr-objcopy from rig-pins.json ONLY; never a bare PATH lookup."""
    objcopy = pins.get("objcopy")
    if not objcopy:
        return False, None, "rig-pins.json is missing 'objcopy'"
    return True, objcopy, ""


def resolve_hex_path(pins: dict, target: str, expect_arm: str) -> tuple[bool, Path | None, str]:
    """Resolve the reference .hex path from rig-pins.json's image_naming pattern.

    Pattern (rig-pins.json image_naming.pattern): "firestarter_<env>.<arm>.hex", relative to
    .planning/milestones/v1.34-artifacts/images/ (this file's parent directory's sibling).
    """
    target_cfg = pins.get("targets", {}).get(target)
    if not target_cfg:
        return False, None, f"rig-pins.json has no targets.{target} entry"
    env = target_cfg.get("env", target)
    images_dir = Path(pins.get("images_dir", str(_DEFAULT_IMAGES_DIR)))
    hex_path = images_dir / f"firestarter_{env}.{expect_arm}.hex"
    return True, hex_path, ""


def resolve_judged_policy(target_cfg: dict) -> tuple[bool, str | None, list, str]:
    """Return (ok, policy, vector_exclusions, detail). ok=False means REFUSE to judge --
    the policy is still the placeholder a later plan's bootloader interrogation must resolve.
    """
    policy = target_cfg.get("judged_span_policy")
    if not policy or str(policy).upper().startswith(_PLACEHOLDER_PREFIX):
        return False, policy, [], (
            f"judged_span_policy is still the placeholder value {policy!r} -- the bootloader "
            "interrogation (-xshowvector) has not yet been recorded for this target; judging "
            "now would risk a false mismatch at 0x0000 on every correctly-flashed board"
        )
    return True, policy, target_cfg.get("vector_exclusions", []) or [], ""


def compute_excluded_positions(vector_exclusions: list) -> set[int]:
    excluded: set[int] = set()
    for excl in vector_exclusions:
        offset = int(excl["offset"])
        length = int(excl["length"])
        excluded.update(range(offset, offset + length))
    return excluded


def judge_span_bytes(
    expected: bytes, actual: bytes, excluded: set[int]
) -> tuple[bool, int, list[tuple[int, int, int]]]:
    """Compare `expected` against the same-length prefix of `actual`, skipping any offset in
    `excluded` on both sides. Returns (match, diff_count, first_20_diffs) where each diff is
    (offset, expected_byte, actual_byte)."""
    n = len(expected)
    diffs: list[tuple[int, int, int]] = []
    diff_count = 0
    for i in range(n):
        if i in excluded:
            continue
        eb = expected[i]
        ab = actual[i] if i < len(actual) else -1
        if eb != ab:
            diff_count += 1
            if len(diffs) < 20:
                diffs.append((i, eb, ab))
    return diff_count == 0, diff_count, diffs


def cross_check_hex_span(
    span: int, target_cfg: dict, manifest: dict, hex_path: Path, expect_arm: str | None = None
) -> tuple[bool, str]:
    """Cross-check the objcopy output size against rig-pins.json's hex_span_expected and
    BUILD-MANIFEST.json's per-image hex_span (when a manifest entry exists for this hex).

    hex_span is genuinely arm-dependent (measured, BUILD-MANIFEST.json
    measured_divergence_finding: the control and v133 arms diverge by ~3 KB per target).
    rig-pins.json's `hex_span_expected` is kept as a legacy flat scalar (documented as
    stale for the control arm) for any reader that still consults it; the authoritative,
    arm-aware value is `hex_span_expected_by_arm`, consulted here first when `expect_arm`
    is given and the map has an entry for it.
    """
    per_arm = target_cfg.get("hex_span_expected_by_arm")
    if isinstance(per_arm, dict) and expect_arm is not None and expect_arm in per_arm:
        expected_span = per_arm[expect_arm]
    else:
        expected_span = target_cfg.get("hex_span_expected")
    if expected_span is not None and span != expected_span:
        return False, (
            f"objcopy output is {span} B but the expected span for arm {expect_arm!r} is "
            f"{expected_span} B for this target -- the image is not the artifact the "
            "manifest describes"
        )
    images = manifest.get("images", {}) if isinstance(manifest, dict) else {}
    if isinstance(images, list):
        # Real BUILD-MANIFEST.json's "images" is a LIST of per-image dicts keyed by their
        # own "file" field, not a dict keyed by filename -- normalize here rather than
        # crash on .get() against a list. (Bug: the original selftest fixture only ever
        # exercised the dict shape, so this never surfaced until run against the real file.)
        images = {
            entry.get("file"): entry
            for entry in images
            if isinstance(entry, dict) and entry.get("file")
        }
    entry = images.get(hex_path.name)
    if entry is not None:
        manifest_span = entry.get("hex_span")
        if manifest_span is not None and span != manifest_span:
            return False, (
                f"objcopy output is {span} B but BUILD-MANIFEST.json records hex_span="
                f"{manifest_span} B for {hex_path.name!r} -- the image is not the artifact "
                "the manifest describes"
            )
    return True, ""


# ---------------------------------------------------------------------------
# Subprocess-invoking helpers -- real device I/O / real toolchain calls.
# Never used by --selftest; the bring-up proof exercises these directly.
# ---------------------------------------------------------------------------


def run_avrdude_read(
    binary: str, conf: str, target_cfg: dict, port: str, out_bin: Path
) -> tuple[int, str, str, list]:
    """-A on EVERY target (Pitfall 2), -C with the pinned conf, a single flash:r:...:r."""
    argv = [
        binary,
        "-C", conf,
        "-c", target_cfg["programmer"],
        "-p", target_cfg["mcu"],
        "-b", str(target_cfg["baud"]),
        "-P", port,
        "-A",
        "-U", f"flash:r:{out_bin}:r",
    ]
    # cwd is recorded as the ACTUAL invocation cwd (Path.cwd(), not a hardcoded None) --
    # a Rule 1 bug fixed during 160-08's live bring-up: "the literal argv plus working
    # directory of each is recorded" (PROCEDURE.md Recording discipline) cannot hold
    # against a field that is always null regardless of where the process actually ran.
    cwd = str(Path.cwd())
    try:
        # Rule 1 fix (found live, 160-10 leonardo bring-up, same defect as probe_board.py's
        # run_avrdude): errors="replace" so a device that answers with non-UTF-8 bytes (e.g.
        # a Leonardo not yet in its Caterina bootloader) cannot crash this function with a
        # raw UnicodeDecodeError instead of a reported avrdude failure.
        done = subprocess.run(
            argv, capture_output=True, text=True, errors="replace", check=False, shell=False
        )
    except OSError as exc:
        return 1, "", f"avrdude failed to execute: {exc}", [{"argv": argv, "cwd": cwd}]
    return done.returncode, done.stdout, done.stderr, [{"argv": argv, "cwd": cwd}]


def run_objcopy_normalize(objcopy: str, hex_path: Path, out_bin: Path) -> tuple[int, str, str, list]:
    argv = [objcopy, "-I", "ihex", "-O", "binary", str(hex_path), str(out_bin)]
    cwd = str(Path.cwd())
    try:
        done = subprocess.run(
            argv, capture_output=True, text=True, errors="replace", check=False, shell=False
        )
    except OSError as exc:
        return 1, "", f"avr-objcopy failed to execute: {exc}", [{"argv": argv, "cwd": cwd}]
    return done.returncode, done.stdout, done.stderr, [{"argv": argv, "cwd": cwd}]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", choices=list(_TARGETS))
    ap.add_argument("--port", help="serial port, e.g. /dev/ttyACM0")
    ap.add_argument("--flashed-arm", choices=list(_ARMS), help="the arm that was actually flashed")
    ap.add_argument("--expect-arm", choices=list(_ARMS), help="the arm to judge the read-back against")
    ap.add_argument("--out-dir", help="directory to write artifacts into")
    ap.add_argument("--pins", default=str(_DEFAULT_PINS), help="path to rig-pins.json")
    ap.add_argument("--manifest", default=str(_DEFAULT_MANIFEST), help="path to BUILD-MANIFEST.json")
    ap.add_argument("--readback", help="judge an EXISTING read-back file without touching a device")
    ap.add_argument(
        "--no-read",
        action="store_true",
        help="explicit companion to --readback: no avrdude read will run in this invocation",
    )
    ap.add_argument("--selftest", action="store_true")
    return ap


def _load_json(path: str | Path, default: dict | None = None) -> dict:
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        raise FileNotFoundError(str(p))
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    if args.readback and not args.no_read:
        print(
            "FAIL: --readback requires the explicit --no-read companion flag, so a re-judge "
            "of a committed artifact can never be mistaken for a live device read",
            file=sys.stderr,
        )
        return 2
    if args.no_read and not args.readback:
        print("FAIL: --no-read has nothing to judge without --readback", file=sys.stderr)
        return 2

    required_pairs = [
        ("--target", args.target),
        ("--flashed-arm", args.flashed_arm),
        ("--expect-arm", args.expect_arm),
        ("--out-dir", args.out_dir),
    ]
    if not args.readback:
        required_pairs.append(("--port", args.port))
    missing = [name for name, val in required_pairs if not val]
    if missing:
        print(f"FAIL: missing required argument(s): {missing}", file=sys.stderr)
        return 2

    try:
        pins = _load_json(args.pins)
    except OSError as exc:
        print(f"FAIL: could not read pins file {args.pins}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: pins file {args.pins} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    manifest = _load_json(args.manifest, default={})

    ok, binary, conf, detail = resolve_avrdude(pins)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1
    ok, objcopy, detail = resolve_objcopy(pins)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    target_cfg = pins.get("targets", {}).get(args.target)
    if not target_cfg:
        print(f"FAIL: rig-pins.json has no targets.{args.target} entry", file=sys.stderr)
        return 1

    ok, policy, vector_exclusions, detail = resolve_judged_policy(target_cfg)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    ok, hex_path, detail = resolve_hex_path(pins, args.target, args.expect_arm)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1
    if not hex_path.exists():
        print(f"FAIL: reference hex not found: {hex_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    commands: list = []

    # --- the read (or re-judge an existing file) ---
    stderr_log_path = out_dir / "avrdude_read.stderr.log"
    if args.readback:
        readback_path = Path(args.readback)
        if not readback_path.exists():
            print(f"FAIL: --readback file does not exist: {readback_path}", file=sys.stderr)
            return 1
        stderr_log_path.write_text("(--no-read: avrdude was not invoked)\n", encoding="utf-8")
    else:
        readback_path = out_dir / "flash_readback.bin"
        rc, _out, err, cmds = run_avrdude_read(binary, conf, target_cfg, args.port, readback_path)
        commands.extend(cmds)
        stderr_log_path.write_text(err, encoding="utf-8")
        if rc != 0 and not readback_path.exists():
            print(f"FAIL: avrdude read failed (rc={rc}): {err.strip()[:800]}", file=sys.stderr)
            return 1

    readback_bytes = readback_path.read_bytes()
    if len(readback_bytes) != target_cfg["flash_size"]:
        print(
            f"FAIL: read-back file is {len(readback_bytes)} B, expected exactly "
            f"{target_cfg['flash_size']} B -- this is the truncation symptom -A exists to "
            "prevent (Pitfall 2)",
            file=sys.stderr,
        )
        return 1

    # --- the normalize ---
    expected_bin_path = out_dir / "expected_span.bin"
    rc, _out, err, cmds = run_objcopy_normalize(objcopy, hex_path, expected_bin_path)
    commands.extend(cmds)
    if rc != 0:
        print(f"FAIL: avr-objcopy failed (rc={rc}): {err.strip()[:800]}", file=sys.stderr)
        return 1
    expected_bytes = expected_bin_path.read_bytes()
    span = len(expected_bytes)

    ok, detail = cross_check_hex_span(span, target_cfg, manifest, hex_path, args.expect_arm)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    # --- the judge ---
    excluded = compute_excluded_positions(vector_exclusions) if policy != "hex-extent" else set()
    actual_span = readback_bytes[:span]
    match, diff_count, diffs = judge_span_bytes(expected_bytes, actual_span, excluded)

    sha_expected = hashlib.sha256(expected_bytes).hexdigest()
    sha_actual = hashlib.sha256(actual_span).hexdigest()
    sha_whole = hashlib.sha256(readback_bytes).hexdigest()

    verdict = {
        "target": args.target,
        "port": args.port,
        "flashed_arm": args.flashed_arm,
        "expect_arm": args.expect_arm,
        "hex_path": str(hex_path),
        "judged_span_bytes": span,
        "judged_span_policy": policy,
        "vector_exclusions_applied": vector_exclusions if policy != "hex-extent" else [],
        "sha_expected_judged": sha_expected,
        "sha_actual_judged": sha_actual,
        "judged_match": match,
        "sha_whole_flash_unjudged": sha_whole,
        "readback_size_bytes": len(readback_bytes),
        "avrdude_binary": binary,
        "avrdude_conf": conf,
        "avrdude_version": pins.get("avrdude", {}).get("version"),
        "objcopy": objcopy,
        "commands": commands,
        "raw_stderr_path": str(stderr_log_path),
    }
    if not match:
        verdict["diff_count"] = diff_count
        verdict["first_diffs"] = [
            {"offset": o, "expected": f"0x{e:02X}", "actual": ("0x%02X" % a) if a >= 0 else "MISSING"}
            for o, e, a in diffs
        ]

    out_json = out_dir / "READBACK-VERDICT.json"
    tmp_json = out_json.with_name(out_json.name + ".tmp")
    tmp_json.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
    tmp_json.replace(out_json)

    # judged_span.bin is written to disk as a REAL file (Rule 1 bug fix, found live at
    # 160-08 bring-up): the prior version of SHA256SUMS.txt named a file that was never
    # written, and put an explanatory annotation inside the whole-flash line's filename
    # column -- both of which make `sha256sum -c` fail outright rather than verify. The
    # annotation is preserved as a '#' comment line (sha256sum -c ignores '#' lines);
    # the two data lines below name only real, already-present files.
    judged_span_path = out_dir / "judged_span.bin"
    judged_span_path.write_bytes(actual_span)
    sums_path = out_dir / "SHA256SUMS.txt"
    sums_path.write_text(
        "# judged_span.bin -- the judged [0, judged_span_bytes) prefix of the read-back,\n"
        "# compared against the flashed arm's own hex extent (D-02).\n"
        f"{sha_actual}  judged_span.bin\n"
        "# flash_readback.bin -- the full read-back; UNJUDGED whole-flash datum, never\n"
        "# consumed in the judged_match decision (D-02).\n"
        f"{sha_whole}  flash_readback.bin\n",
        encoding="utf-8",
    )

    if not match:
        diff_text = "; ".join(
            f"offset=0x{o:05X} expected=0x{e:02X} actual={('0x%02X' % a) if a >= 0 else 'MISSING'}"
            for o, e, a in diffs
        )
        print(
            f"FAIL: judged span mismatch -- {diff_count} differing byte(s), first "
            f"{len(diffs)} shown: {diff_text}",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: judged_match=True target={args.target} flashed_arm={args.flashed_arm} "
        f"expect_arm={args.expect_arm} judged_span_bytes={span} "
        f"sha_whole_flash_unjudged={sha_whole[:12]}..."
    )
    return 0


# ---------------------------------------------------------------------------
# --selftest: entirely device-free, synthetic Intel-hex fixtures and
# synthetic read-backs, in a temp directory.
# ---------------------------------------------------------------------------


def _write_ihex(path: Path, data: bytes) -> None:
    """Write a minimal, valid Intel HEX file for `data`, starting at address 0, no gaps."""
    lines = []
    addr = 0
    for i in range(0, len(data), 16):
        chunk = data[i : i + 16]
        rec = _ihex_data_record(addr, chunk)
        lines.append(rec)
        addr += len(chunk)
    lines.append(":00000001FF")  # EOF record
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ihex_data_record(addr: int, chunk: bytes) -> str:
    count = len(chunk)
    rectype = 0x00
    body = [count, (addr >> 8) & 0xFF, addr & 0xFF, rectype, *chunk]
    checksum = (-sum(body)) & 0xFF
    return ":" + "".join(f"{b:02X}" for b in body) + f"{checksum:02X}"


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

    tmp = Path(tempfile.mkdtemp(prefix="judge_readback_selftest_"))
    try:
        objcopy_real = "/home/vscode/.platformio/packages/toolchain-atmelavr/bin/avr-objcopy"
        objcopy_bin = objcopy_real if Path(objcopy_real).exists() else None

        span_len = 100
        expected_data = bytes((i % 251) for i in range(span_len))
        flash_size = 200
        full_flash = expected_data + b"\xff" * (flash_size - span_len)

        target_cfg_hexextent = {
            "flash_size": flash_size,
            "hex_span_expected": span_len,
            "judged_span_policy": "hex-extent",
            "vector_exclusions": [],
        }

        # --- positive 1: read-back prefix equals hex extent -> match ---
        match, diff_count, diffs = judge_span_bytes(expected_data, full_flash[:span_len], set())
        report("positive: matching read-back prefix judges as a match", match and diff_count == 0)

        # --- positive 2: whole-flash SHA differs from judged SHA (distinct data) ---
        sha_judged = hashlib.sha256(full_flash[:span_len]).hexdigest()
        sha_whole = hashlib.sha256(full_flash).hexdigest()
        report(
            "positive: whole-flash SHA differs from judged-span SHA (two distinct data)",
            sha_judged != sha_whole,
        )

        # --- negative 1: short read-back (truncation symptom -A prevents) ---
        short_flash = full_flash[: flash_size - 1]
        report(
            "negative 1: read-back shorter than flash_size is caught",
            len(short_flash) != flash_size,
            f"len={len(short_flash)} expected={flash_size}",
        )

        # --- negative 2: prefix differs from hex extent -> mismatch, with diff report ---
        corrupted = bytearray(full_flash)
        corrupted[5] = (corrupted[5] + 1) % 256
        match2, diff_count2, diffs2 = judge_span_bytes(expected_data, bytes(corrupted)[:span_len], set())
        report(
            "negative 2: corrupted prefix produces a mismatch with a differing-offset report",
            (not match2) and diff_count2 == 1 and diffs2[0][0] == 5,
            f"diffs={diffs2}",
        )

        # --- negative 3: --expect-arm pointing at the other arm's hex (cross-flash shape) ---
        other_arm_data = bytes((i * 7 + 3) % 256 for i in range(span_len))
        match3, diff_count3, _ = judge_span_bytes(other_arm_data, full_flash[:span_len], set())
        report(
            "negative 3: cross-arm expectation (other arm's hex) against this arm's read-back is a mismatch",
            (not match3) and diff_count3 > 0,
            f"diff_count={diff_count3}",
        )

        # --- negative 4: judged_span_policy still the placeholder value ---
        placeholder_target = {"judged_span_policy": "PENDING-xshowvector", "vector_exclusions": []}
        ok4, policy4, _excl4, detail4 = resolve_judged_policy(placeholder_target)
        report(
            "negative 4: placeholder judged_span_policy is refused",
            not ok4,
            detail4,
        )

        # --- negative 5: objcopy output size disagrees with the recorded hex_span ---
        if objcopy_bin:
            hex_path = tmp / "fixture.hex"
            _write_ihex(hex_path, expected_data)
            out_bin = tmp / "fixture_normalized.bin"
            rc, _out, err, _cmds = run_objcopy_normalize(objcopy_bin, hex_path, out_bin)
            report("objcopy invocation on the synthetic fixture succeeds", rc == 0, err)
            normalized = out_bin.read_bytes() if out_bin.exists() else b""
            report(
                "objcopy output matches the synthetic hex's own data (bring-up proof of the normalize step)",
                normalized == expected_data,
            )
            wrong_manifest = {"images": {hex_path.name: {"hex_span": span_len + 1}}}
            ok5, detail5 = cross_check_hex_span(
                len(normalized), target_cfg_hexextent, wrong_manifest, hex_path
            )
            report(
                "negative 5: objcopy output size disagreeing with BUILD-MANIFEST.json hex_span is caught",
                not ok5,
                detail5,
            )

            # --- positive 4: manifest "images" is a LIST (real BUILD-MANIFEST.json's actual
            # shape), keyed by each entry's own "file" field -- not a dict. This is the shape
            # the original fixture (a dict) never exercised, and .get() against a bare list
            # would raise AttributeError rather than return a controlled FAIL. ---
            list_shaped_manifest = {
                "images": [
                    {"file": hex_path.name, "hex_span": span_len},
                    {"file": "unrelated_other.hex", "hex_span": 999},
                ]
            }
            ok6, detail6 = cross_check_hex_span(
                len(normalized), target_cfg_hexextent, list_shaped_manifest, hex_path
            )
            report(
                "positive: list-shaped BUILD-MANIFEST.json 'images' (the real file's actual "
                "shape) is normalized and matched by 'file', not crashed on",
                ok6,
                detail6,
            )

            # --- positive 5: hex_span_expected_by_arm is consulted per expect_arm, overriding
            # a stale flat hex_span_expected (the arm-dependence defect this tool must not
            # silently paper over: control and v133 hex spans differ by ~3 KB per target) ---
            per_arm_target_cfg = {
                "flash_size": flash_size,
                "hex_span_expected": span_len + 1,  # deliberately WRONG flat legacy value
                "hex_span_expected_by_arm": {"control": span_len, "v133": span_len + 1},
                "judged_span_policy": "hex-extent",
                "vector_exclusions": [],
            }
            ok7, detail7 = cross_check_hex_span(
                len(normalized), per_arm_target_cfg, {}, hex_path, expect_arm="control"
            )
            report(
                "positive: hex_span_expected_by_arm[expect_arm] overrides a stale flat "
                "hex_span_expected for the arm actually being judged",
                ok7,
                detail7,
            )
            ok8, detail8 = cross_check_hex_span(
                len(normalized), per_arm_target_cfg, {}, hex_path, expect_arm="v133"
            )
            report(
                "negative 7: hex_span_expected_by_arm still catches a genuine mismatch for "
                "the OTHER arm's expected span",
                not ok8,
                detail8,
            )
        else:
            report(
                "objcopy bring-up leg",
                False,
                f"pinned avr-objcopy not found at {objcopy_real} in this environment",
            )

        # --- negative 6: missing read-back file ---
        missing_path = tmp / "does-not-exist.bin"
        report("negative 6: missing read-back file path does not exist (precondition)", not missing_path.exists())

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
