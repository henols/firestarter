#!/usr/bin/env python3
"""probe_board.py -- board identity by avrdude signature probe (D-14), never by handshake.

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo. `firestarter_app/firestarter/
avr_tool.py` is read-only invocation-shape reference only; the mechanism below is reused in
this phase-owned tool, never folded into product code (D-14, Out-of-Scope table).

Known-good signature mapping on this bench (measured 2026-08-19, direct signature read):
    0x1e950f = ATmega328P  (uno)
    0x1e9516 = ATmega328PB (uno328pb)
    0x1e9587 = ATmega32U4  (leonardo)
A v1.7 bench note once labeled the /dev/ttyUSB0 board's silicon a plain Uno; that label was
stale and was corrected only by direct signature measurement -- which is exactly why this
tool identifies a board by signature and never by a recorded label or a firmware handshake.

Two independently bench-verified parse routes
(.planning/todos/pending/avrdude-mcu-detection-fallback.md, confirmed live 2026-05-21 on the
operator's 328PB-Uno, re-confirmed 2026-08-19):

  Route 1 -- deliberately WRONG -p, no -U: avrdude's stderr reads
      "avrdude error: connected part ATmega328PB differs in signature from -p ATmega328P"
    and the part name is parsed off the "connected part" anchor.

  Route 2 -- verbose, correct -p: avrdude's stderr reads
      "avrdude: device signature = 0x1e9516 (probably m328pb)"
    and both the hex device signature and the parenthesised "probably" part guess are parsed.

Route 1 is tried first; Route 2 is the fallback. Neither route ever issues a memory
operation (-U) -- both use -n (no write) only, and Route 2 additionally passes -v. If
neither route parses, this tool exits non-zero and quotes the captured stderr: RIG-02
needs a hard failure here, not the null identity the closest analog (the pending todo's
sketch) would return.

Note recorded for completeness: `-c arduino` against the 328PB board fails "unable to open
programmer" -- itself a signal that the board is not a plain ATmega328P, worth recording
rather than discarding.

avrdude is resolved from rig-pins.json ONLY -- never from PATH. Three avrdude installations
exist in this container (system 7.1, PlatformIO 8.1, a stale 6.3 that predates the urclock
programmer entirely); an unpinned PATH resolution would be an invisible cross-cell variable.
A binary listed in rig-pins.json's `forbidden_binaries` is refused outright.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_PINS = _HERE.parent / "rig-pins.json"

# Deliberately wrong -p for Route 1: guaranteed to differ from all three bench targets
# (atmega328p / atmega328pb / atmega32u4), so the "connected part ... differs in signature"
# message fires no matter which of the three boards is actually attached.
_ROUTE1_WRONG_PARTNO = "m2560"

_ROUTE1_RE = re.compile(r"connected part (\w+)")
_ROUTE2_SIG_RE = re.compile(r"device signature = (0x[0-9a-fA-F]+)")
_ROUTE2_GUESS_RE = re.compile(r"\(probably (\w+)\)")

# avrdude 8.1's ACTUAL message format (measured live on this rig's pinned binary,
# 2026-08-27, on the operator's Uno) -- differs from the wording the docstring's
# 2026-05-21/2026-08-19 bench notes recorded (that mechanism was bench-verified against
# a different avrdude build). 8.1 prints one line, on BOTH the deliberately-wrong -p
# route and the correct -p route, regardless of match:
#     "Device signature = 1E 95 0F (ATmega328P, ATA6614Q, LGT8F328P)"
# and, only on a mismatch, an additional line naming the expected signature for the
# wrong part supplied (ignored here -- the signature line alone is sufficient). Neither
# _ROUTE1_RE nor the old _ROUTE2_SIG_RE/_ROUTE2_GUESS_RE pair matches this wording at
# all, which would have made this tool a hard rig failure on its very first live
# invocation (Rule 1 bug, fixed in-phase per PROCEDURE.md P-H1).
_SIG81_RE = re.compile(
    r"Device signature = ([0-9A-Fa-f]{2}) ([0-9A-Fa-f]{2}) ([0-9A-Fa-f]{2})"
    r"(?:\s*\(([^)]*)\))?"
)

_SIGNATURE_TO_MCU = {
    "0x1e950f": "atmega328p",
    "0x1e9516": "atmega328pb",
    "0x1e9587": "atmega32u4",
}
_MCU_TO_SIGNATURE = {v: k for k, v in _SIGNATURE_TO_MCU.items()}

# Rule 1 fix (found live, 160-09 bring-up on the real ATmega328PB board): the option
# below was originally "-xshowbootsize", copied from 160-RESEARCH.md's own speculative
# Code Example 5 (recorded there as "NOT RUN -- no board attached"). avrdude's REAL
# urclock extended-option name is "showboot" (measured live: "-xshowbootsize" fails with
# "Error: invalid extended parameter -x showbootsize", and the printed -x help menu lists
# only "showboot  Show bootloader size and exit" -- no "showbootsize" variant exists at
# all). Corrected here so the boot-size query in --show-urclock's four-probe set actually
# returns data instead of an option-parse error on every future invocation of this mode.
_URCLOCK_PROBES = ["-xshowall", "-xshowvector", "-xshowboot", "-xshowversion"]


# ---------------------------------------------------------------------------
# Pure parsing / decision logic -- no subprocess, no device. Exercised
# directly by --selftest.
# ---------------------------------------------------------------------------


def _parse_sig81(stderr_text: str) -> tuple[str | None, str | None]:
    """Parse avrdude 8.1's 'Device signature = XX XX XX (Name1, Name2, ...)' line.

    Returns (part_guess, signature_hex). part_guess is the first parenthesised name
    when present, else looked up from the measured hex triplet via _SIGNATURE_TO_MCU.
    """
    m = _SIG81_RE.search(stderr_text)
    if not m:
        return None, None
    b1, b2, b3, paren = m.group(1), m.group(2), m.group(3), m.group(4)
    sig_hex = f"0x{b1.lower()}{b2.lower()}{b3.lower()}"
    part_guess = None
    if paren:
        names = [n.strip() for n in paren.split(",") if n.strip()]
        if names:
            part_guess = names[0]
    if part_guess is None:
        part_guess = _SIGNATURE_TO_MCU.get(sig_hex)
    return part_guess, sig_hex


def parse_route1(stderr_text: str) -> tuple[str | None, str | None]:
    """Returns (connected_part_raw, signature_hex). signature_hex is None under the
    older 'connected part ... differs in signature' wording (which carries no hex
    triplet of its own); it is populated directly from a live measurement under
    avrdude 8.1's wording, which does."""
    m = _ROUTE1_RE.search(stderr_text)
    if m:
        return m.group(1), None
    return _parse_sig81(stderr_text)


def parse_route2(stderr_text: str) -> tuple[str | None, str | None]:
    sig_m = _ROUTE2_SIG_RE.search(stderr_text)
    guess_m = _ROUTE2_GUESS_RE.search(stderr_text)
    if sig_m or guess_m:
        return (
            sig_m.group(1).lower() if sig_m else None,
            guess_m.group(1) if guess_m else None,
        )
    part_guess, sig_hex = _parse_sig81(stderr_text)
    return sig_hex, part_guess


def normalize_mcu_name(name: str) -> str:
    """'ATmega328PB' -> 'atmega328pb'; 'm328pb' -> 'atmega328pb'; 'm32u4' -> 'atmega32u4'."""
    name = name.strip().lower()
    if name.startswith("atmega") or name.startswith("attiny"):
        return name
    if name.startswith("m") and len(name) > 1:
        return "atmega" + name[1:]
    return name


def decide_identity(
    stderr1: str, stderr2: str | None
) -> tuple[bool, str | None, str | None, str | None, str]:
    """Decide route / connected_part_raw / signature_hex from raw stderr text(s) alone.

    Returns (ok, route, connected_part_raw, signature_hex, detail). ok=False means
    neither route parsed -- a hard failure, never a null identity.
    """
    part_raw, sig_hex1 = parse_route1(stderr1)
    if part_raw:
        return True, "route1", part_raw, sig_hex1, ""
    if stderr2:
        sig_hex, guess = parse_route2(stderr2)
        if sig_hex or guess:
            return True, "route2", guess, sig_hex, ""
    combined = (stderr1 or "") + "\n" + (stderr2 or "")
    return False, None, None, None, f"neither parse route matched avrdude stderr: {combined.strip()[:800]!r}"


def compute_mcu_match(connected_part_raw: str, mcu_expected: str) -> tuple[str, bool]:
    connected_part = normalize_mcu_name(connected_part_raw)
    return connected_part, connected_part == mcu_expected.strip().lower()


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


# ---------------------------------------------------------------------------
# Subprocess-invoking helpers -- real device I/O. Never used by --selftest.
# ---------------------------------------------------------------------------


def run_avrdude(binary: str, conf: str, extra_args: list[str]) -> tuple[int, str, str]:
    cmd = [binary, "-C", conf, *extra_args]
    try:
        # Rule 1 fix (found live, 160-10 leonardo bring-up): text=True alone decodes
        # stdout/stderr with the strict 'utf-8' error handler, and a Leonardo running its
        # APPLICATION firmware (not yet touched into the Caterina bootloader) answers an
        # avr109 handshake attempt with raw, non-protocol serial bytes that are not valid
        # UTF-8 -- avrdude echoes some of that into its own diagnostic text, which crashed
        # this tool with UnicodeDecodeError before any FAIL: line could be printed. errors=
        # "replace" preserves this function's contract (str stdout/stderr, never bytes) while
        # never crashing on whatever raw bytes the device actually sends back.
        done = subprocess.run(
            cmd, capture_output=True, text=True, errors="replace", check=False, shell=False
        )
    except OSError as exc:
        return 1, "", f"avrdude failed to execute: {exc}"
    return done.returncode, done.stdout, done.stderr


def run_urclock_probes(binary: str, conf: str, target_cfg: dict, port: str) -> dict:
    """Run all four urclock bootloader-interrogation probes and record each one's raw
    output, even when a probe itself errors -- "the bootloader does not support this
    option" IS the answer (Pitfall 3), so nothing here aborts the whole mode."""
    probes: dict[str, dict] = {}
    for opt in _URCLOCK_PROBES:
        rc, out, err = run_avrdude(
            binary,
            conf,
            [
                "-c", target_cfg["programmer"],
                "-p", target_cfg["mcu"],
                "-b", str(target_cfg["baud"]),
                "-P", port,
                "-n",
                opt,
            ],
        )
        probes[opt] = {"returncode": rc, "stdout": out, "stderr": err}
    return probes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", help="serial port, e.g. /dev/ttyACM0")
    ap.add_argument("--target", choices=["uno", "uno328pb", "leonardo"])
    ap.add_argument("--pins", default=str(_DEFAULT_PINS), help="path to rig-pins.json")
    ap.add_argument(
        "--show-urclock",
        action="store_true",
        help="run the uno328pb urclock bootloader interrogation (valid only with --target uno328pb)",
    )
    ap.add_argument("--out", help="write the identification result JSON here")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    if args.show_urclock and args.target != "uno328pb":
        print(
            "FAIL: --show-urclock is only valid with --target uno328pb "
            f"(got --target {args.target!r})",
            file=sys.stderr,
        )
        return 2

    if not args.port or not args.target:
        print("FAIL: --port and --target are required outside --selftest", file=sys.stderr)
        return 2

    try:
        pins = json.loads(Path(args.pins).read_text())
    except OSError as exc:
        print(f"FAIL: could not read pins file {args.pins}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: pins file {args.pins} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    ok, binary, conf, detail = resolve_avrdude(pins)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    target_cfg = pins["targets"][args.target]
    out_path = Path(args.out) if args.out else Path.cwd() / f"probe_board.{args.target}.json"
    stderr_log_path = out_path.with_name(out_path.name + ".stderr.log")
    sections: list[str] = []

    rc1, _out1, err1 = run_avrdude(
        binary,
        conf,
        [
            "-c", target_cfg["programmer"],
            "-p", _ROUTE1_WRONG_PARTNO,
            "-b", str(target_cfg["baud"]),
            "-P", args.port,
            "-n",
        ],
    )
    sections.append(f"=== route1 (rc={rc1}) ===\n{err1}\n")

    ok, route, part_raw, sig_hex, detail = decide_identity(err1, None)
    if not ok:
        rc2, _out2, err2 = run_avrdude(
            binary,
            conf,
            [
                "-c", target_cfg["programmer"],
                "-p", target_cfg["mcu"],
                "-b", str(target_cfg["baud"]),
                "-P", args.port,
                "-n", "-v",
            ],
        )
        sections.append(f"=== route2 (rc={rc2}) ===\n{err2}\n")
        ok, route, part_raw, sig_hex, detail = decide_identity(err1, err2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_log_path.write_text("".join(sections), encoding="utf-8")

    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    connected_part, mcu_matches = compute_mcu_match(part_raw, target_cfg["mcu"])
    if not sig_hex:
        sig_hex = _MCU_TO_SIGNATURE.get(connected_part, f"unknown-signature-for-{connected_part}")

    result = {
        "board_signature": sig_hex,
        "signature_route": route,
        "connected_part": connected_part,
        "mcu_expected": target_cfg["mcu"],
        "mcu_matches": mcu_matches,
        "avrdude_binary": binary,
        "avrdude_conf": conf,
        "avrdude_version": pins.get("avrdude", {}).get("version"),
        "raw_stderr_path": str(stderr_log_path),
        "urclock_probes": {},
    }

    if args.show_urclock:
        result["urclock_probes"] = run_urclock_probes(binary, conf, target_cfg, args.port)

    tmp_path = out_path.with_name(out_path.name + ".tmp")
    tmp_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    tmp_path.replace(out_path)

    if not mcu_matches:
        print(
            f"FAIL: connected part {connected_part!r} does not match expected mcu "
            f"{target_cfg['mcu']!r} for target {args.target!r}",
            file=sys.stderr,
        )
        return 1

    print(f"OK: board identified as {connected_part} via {route} (signature {sig_hex})")
    return 0


# ---------------------------------------------------------------------------
# --selftest: fabricated stderr fixtures, no device. Positive and negative
# legs per this tool's plan-mandated acceptance criteria.
# ---------------------------------------------------------------------------

_FIXTURE_ROUTE1 = "avrdude error: connected part ATmega328PB differs in signature from -p ATmega328P\n"
_FIXTURE_ROUTE2 = "avrdude: device signature = 0x1e9516 (probably m328pb)\n"
_FIXTURE_GARBAGE = "avrdude: some unrelated diagnostic text with no signature information\n"

# Real avrdude 8.1 wording (verbatim capture, this rig's pinned binary, 2026-08-27, live
# Uno on /dev/ttyACM0) -- the wording _ROUTE1_RE/_ROUTE2_SIG_RE/_ROUTE2_GUESS_RE never
# match, which is exactly the bug this plan's bring-up found and fixed in-phase.
_FIXTURE_SIG81_MISMATCH = (
    "Device signature = 1E 95 0F (ATmega328P, ATA6614Q, LGT8F328P)\n"
    "Error: expected signature for ATmega2560 is 1E 98 01\n"
    "  - double check chip or use -F to carry on regardless\n"
)
_FIXTURE_SIG81_MATCH = (
    "AVR device initialized and ready to accept instructions\n"
    "Device signature = 1E 95 0F (ATmega328P, ATA6614Q, LGT8F328P)\n"
)


def _run_selftest() -> int:
    ok_overall = True

    def report(name: str, passed: bool, detail: str = "") -> None:
        nonlocal ok_overall
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok_overall = False
        suffix = f" -- {detail}" if detail else ""
        print(f"{status}: {name}{suffix}")

    # --- positive 1: route 1 parses a connected-part line ---
    ok, route, part_raw, sig_hex, detail = decide_identity(_FIXTURE_ROUTE1, None)
    report(
        "positive: route1 parses connected-part line",
        ok and route == "route1" and part_raw == "ATmega328PB",
        detail,
    )

    # --- positive 2: route 2 parses signature line and part guess ---
    ok, route, part_raw, sig_hex, detail = decide_identity(_FIXTURE_GARBAGE, _FIXTURE_ROUTE2)
    report(
        "positive: route2 parses signature line and part guess",
        ok and route == "route2" and part_raw == "m328pb" and sig_hex == "0x1e9516",
        detail,
    )

    # --- positive 2b: route1 on avrdude 8.1's REAL wording (the deliberately-wrong -p
    # attempt), which carries the signature triplet AND a parenthesised name list, no
    # "connected part" phrase at all ---
    ok, route, part_raw, sig_hex, detail = decide_identity(_FIXTURE_SIG81_MISMATCH, None)
    report(
        "positive: route1 parses avrdude 8.1's real 'Device signature = ... (Name, ...)' "
        "wording on the wrong-partno attempt (the actual live-device bug this bring-up found)",
        ok and route == "route1" and part_raw == "ATmega328P" and sig_hex == "0x1e950f",
        detail,
    )

    # --- positive 2c: the same avrdude 8.1 wording also appears on the MATCHING -p
    # attempt (no "Error: expected signature" line at all) and parses identically ---
    ok, route, part_raw, sig_hex, detail = decide_identity(_FIXTURE_SIG81_MATCH, None)
    report(
        "positive: route1 parses avrdude 8.1's real wording on a matching -p attempt too",
        ok and route == "route1" and part_raw == "ATmega328P" and sig_hex == "0x1e950f",
        detail,
    )

    # --- positive 3: a --target whose expected mcu matches sets mcu_matches true ---
    connected_part, matches = compute_mcu_match("ATmega328PB", "atmega328pb")
    report(
        "positive: matching target sets mcu_matches true",
        matches and connected_part == "atmega328pb",
    )

    # --- negative 1: stderr from which neither route parses ---
    ok, route, part_raw, sig_hex, detail = decide_identity(_FIXTURE_GARBAGE, _FIXTURE_GARBAGE)
    report("negative 1: unparseable stderr is a hard failure, not a null identity", not ok, detail)

    # --- negative 2: parsed part does not match the expected mcu ---
    connected_part, matches = compute_mcu_match("ATmega328PB", "atmega328p")
    report(
        "negative 2: mcu mismatch is caught",
        not matches,
        f"connected={connected_part} expected=atmega328p",
    )

    # --- negative 3: a resolved binary listed in forbidden_binaries is refused ---
    fake_pins = {
        "avrdude": {"binary": "/fake/avrdude-6.3", "conf": "/fake/avrdude.conf", "version": "6.3"},
        "forbidden_binaries": [
            {"path": "/fake/avrdude-6.3", "version": "6.3", "reason": "selftest fixture"}
        ],
    }
    ok, binp, confp, detail = resolve_avrdude(fake_pins)
    report("negative 3: forbidden avrdude binary is rejected", not ok, detail)

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
