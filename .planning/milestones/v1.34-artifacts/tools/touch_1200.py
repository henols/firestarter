#!/usr/bin/env python3
"""touch_1200.py -- Caterina bootloader entry via the 1200-baud touch, reporting its own
failure (RIG-01, Leonardo bring-up, Pitfall 5).

D-16 boundary: this is meta-repo BENCH TOOLING, not host source. It is authored and lives
only under .planning/milestones/v1.34-artifacts/tools/ in the meta repo. It must NEVER be copied into
firestarter/ or firestarter_app/ -- this phase changes no firmware and no host source.
Nothing here is imported by, or imports from, either sub-repo.

This is the one rig tool permitted a non-stdlib import: `pyserial` 3.5 is present
system-wide in this container and this tool runs from the SYSTEM interpreter (never from an
arm venv), so it cannot import `firestarter` and has no reason to. `serial` is the only
non-standard-library import anywhere in this file.

The mechanism (three lines: open at 1200 baud, close, sleep a settle interval) is copied from
`firestarter_app/firestarter/avr_tool.py:115-123`'s `_trigger_reset` -- READ-ONLY reference,
never modified, never imported. What is explicitly REJECTED from that analog is its
swallow-and-warn error handling (`except Exception: logger.warning(...); return False`): a
rig tool must never swallow a serial failure, because a warning that vanishes into a log
would leave the cell record showing a touch that silently never happened. Every failure path
in this file exits non-zero with a `FAIL:` line instead.

Pitfall 5 / the milestone's lowest-confidence mechanism: PlatformIO's own upload path expects
the board to re-enumerate on a *NEW* serial node after the touch
(`TouchSerialPort` + `WaitForNewSerialPort` in `~/.platformio/platforms/atmelavr/builder/
main.py:84-88`), while the host app's `_trigger_reset` reuses the SAME port and that has been
observed to work on this operator's bench (`.planning/debug/resolved/
fw-update-blocked-release-fw.md:283`: a 5.51s avr109 session on the same `/dev/ttyACM0` node).
Both behaviours are implemented here, selected by `--wait-new-port`, because which one holds
for the flash READ-BACK direction (as opposed to the upload direction both of those prior
observations were about) is a measurement plan 10's Leonardo bring-up makes, not an
assumption this tool bakes in. `flash:r` has never been invoked anywhere in this project's
history (RESEARCH Pitfall 5's decisive negative grep) -- if the window this tool opens proves
too short for the read-back chain, the milestone's own escape hatch is SC#2's named
alternative check with its limits stated, not forcing the read. `--selftest` cannot open a
real port and says so explicitly: the device-enumeration LOGIC is exercised against a stubbed
directory, but the actual re-enumeration behaviour on hardware is unproven here and is
proven only at Leonardo bring-up (plan 10).
"""
from __future__ import annotations

import argparse
import glob as glob_mod
import json
import sys
import time
from pathlib import Path

import serial

_DEFAULT_SETTLE_S = 2.0
_DEFAULT_TIMEOUT_S = 10.0
_DEFAULT_POLL_INTERVAL_S = 0.2
_DEFAULT_SEARCH_PATTERNS = ["/dev/ttyACM*", "/dev/ttyUSB*"]


# ---------------------------------------------------------------------------
# Pure / stubbable logic -- exercised directly by --selftest without a device.
# ---------------------------------------------------------------------------


def validate_port_exists(port: str) -> tuple[bool, str]:
    if not Path(port).exists():
        return False, f"port does not exist: {port}"
    return True, ""


def enumerate_serial_devices(patterns: list[str] | None = None) -> list[str]:
    """Glob every pattern and return the sorted, de-duplicated union. Stubbable: pass a
    tmpdir-scoped glob pattern in tests instead of the real /dev/tty* patterns."""
    pats = patterns if patterns is not None else _DEFAULT_SEARCH_PATTERNS
    found: set[str] = set()
    for pat in pats:
        found.update(glob_mod.glob(pat))
    return sorted(found)


def decide_new_port(before: list[str], after: list[str]) -> str | None:
    """Pure decision: which (if any) device in `after` was not in `before`. Returns the
    lexicographically-first new node, or None if there is no new node."""
    new_ports = sorted(set(after) - set(before))
    return new_ports[0] if new_ports else None


def wait_for_new_port(
    before: list[str],
    patterns: list[str] | None,
    timeout_s: float,
    poll_interval_s: float = _DEFAULT_POLL_INTERVAL_S,
    clock=time.monotonic,
    sleep=time.sleep,
    enumerate_fn=enumerate_serial_devices,
) -> tuple[bool, str | None, list[str]]:
    """Poll `enumerate_fn(patterns)` until a device not in `before` appears, or `timeout_s`
    elapses. Returns (ok, new_port_or_none, last_after_snapshot). Dependency-injected clock/
    sleep/enumerate_fn so --selftest can exercise the timeout path with zero wall-clock cost
    and no real device."""
    deadline = clock() + timeout_s
    after = enumerate_fn(patterns)
    while True:
        new_port = decide_new_port(before, after)
        if new_port is not None:
            return True, new_port, after
        if clock() >= deadline:
            return False, None, after
        sleep(poll_interval_s)
        after = enumerate_fn(patterns)


# ---------------------------------------------------------------------------
# Real serial I/O -- never used by --selftest.
# ---------------------------------------------------------------------------


def do_touch(port: str, settle_s: float) -> tuple[bool, str]:
    """Open `port` at 1200 baud, close it, sleep `settle_s`. Every failure is a hard,
    reported non-zero exit at the call site -- this function never swallows an exception
    the way the product-code analog's warn-and-return-False does; it returns the detail
    string so the caller can print a FAIL: line naming exactly what happened."""
    try:
        ser = serial.Serial(port=port, baudrate=1200)
        ser.close()
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: ANY serial failure must
        # surface as a hard non-zero exit, never a silently-narrowed exception class.
        return False, f"serial failure touching {port} at 1200 baud: {exc}"
    time.sleep(settle_s)
    return True, ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", help="serial port to touch, e.g. /dev/ttyACM0")
    ap.add_argument("--settle-s", type=float, default=_DEFAULT_SETTLE_S, help="settle sleep after the touch")
    ap.add_argument(
        "--wait-new-port",
        action="store_true",
        help="wait for a NEW port (PlatformIO's upload-path behaviour) instead of reusing --port "
        "(the product-code path's behaviour, observed to work on this bench)",
    )
    ap.add_argument("--timeout-s", type=float, default=_DEFAULT_TIMEOUT_S, help="--wait-new-port timeout")
    ap.add_argument("--out", help="write the outcome record here")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main() -> int:
    ap = build_argparser()
    args = ap.parse_args()

    if args.selftest:
        return _run_selftest()

    if not args.port:
        print("FAIL: --port is required outside --selftest", file=sys.stderr)
        return 2

    ok, detail = validate_port_exists(args.port)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    before_devices = enumerate_serial_devices()

    ok, detail = do_touch(args.port, args.settle_s)
    if not ok:
        print(f"FAIL: {detail}", file=sys.stderr)
        return 1

    if args.wait_new_port:
        success, new_port, after_devices = wait_for_new_port(
            before_devices, _DEFAULT_SEARCH_PATTERNS, args.timeout_s
        )
        if not success:
            print(
                f"FAIL: timed out after {args.timeout_s}s waiting for a NEW serial port "
                f"after the 1200-baud touch on {args.port} (before={before_devices} "
                f"after={after_devices})",
                file=sys.stderr,
            )
            return 1
        port_to_use = new_port
        changed = port_to_use != args.port
    else:
        after_devices = enumerate_serial_devices()
        port_to_use = args.port
        changed = False

    record = {
        "port_requested": args.port,
        "port_to_use": port_to_use,
        "changed": changed,
        "settle_s": args.settle_s,
        "wait_new_port": args.wait_new_port,
        "timeout_s": args.timeout_s if args.wait_new_port else None,
        "devices_before": before_devices,
        "devices_after": after_devices,
    }

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = out_path.with_name(out_path.name + ".tmp")
        tmp_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(out_path)

    print(f"OK: use port {port_to_use}")
    return 0


# ---------------------------------------------------------------------------
# --selftest: no real port is ever opened. States plainly which leg is unproven
# until Leonardo bring-up (plan 10).
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

    # --- argument parsing, including the mutually sensible defaults ---
    ap = build_argparser()
    parsed = ap.parse_args(["--port", "/dev/ttyACM0"])
    report(
        "argument parsing: --settle-s defaults to 2, --wait-new-port defaults to False",
        parsed.settle_s == 2.0 and parsed.wait_new_port is False and parsed.timeout_s == _DEFAULT_TIMEOUT_S,
        f"settle_s={parsed.settle_s} wait_new_port={parsed.wait_new_port} timeout_s={parsed.timeout_s}",
    )

    # --- negative: a non-existent port path produces a non-zero exit (checked at the
    # validate_port_exists layer -- exercised end-to-end via CLI outside --selftest too,
    # since --selftest itself must never call sys.exit) ---
    ok, detail = validate_port_exists("/dev/definitely-not-a-port")
    report("negative: non-existent port path is rejected", not ok, detail)

    # --- negative: --timeout-s 0 with --wait-new-port against a stubbed enumeration that
    # never changes -> non-zero timeout exit, with a fake clock so this costs no wall time ---
    fake_now = [0.0]

    def fake_clock() -> float:
        return fake_now[0]

    def fake_sleep(_s: float) -> None:
        fake_now[0] += _s

    def stub_enumerate(_patterns: list[str] | None) -> list[str]:
        return ["/dev/ttyACM0"]  # never changes -- simulates a board that never re-enumerates

    success, new_port, after = wait_for_new_port(
        before=["/dev/ttyACM0"],
        patterns=None,
        timeout_s=0.0,
        clock=fake_clock,
        sleep=fake_sleep,
        enumerate_fn=stub_enumerate,
    )
    report(
        "negative: --timeout-s 0 against an unchanging stubbed enumeration times out non-zero",
        (not success) and new_port is None,
        f"success={success} new_port={new_port} after={after}",
    )

    # --- positive (device-free): a new node IS present -> decide_new_port picks it ---
    success2, new_port2, _after2 = wait_for_new_port(
        before=["/dev/ttyACM0"],
        patterns=None,
        timeout_s=1.0,
        clock=fake_clock,
        sleep=fake_sleep,
        enumerate_fn=lambda _p: ["/dev/ttyACM0", "/dev/ttyACM1"],
    )
    report(
        "positive (device-free): a genuinely new node is detected and named",
        success2 and new_port2 == "/dev/ttyACM1",
    )

    # --- device-enumeration helper against a stubbed directory ---
    tmp = Path(tempfile.mkdtemp(prefix="touch_1200_selftest_"))
    try:
        (tmp / "ttyACM1").touch()
        (tmp / "ttyACM0").touch()
        (tmp / "not-a-tty").touch()
        found = enumerate_serial_devices([str(tmp / "ttyACM*")])
        report(
            "device-enumeration helper returns a sorted list against a stubbed directory",
            found == sorted([str(tmp / "ttyACM0"), str(tmp / "ttyACM1")]),
            str(found),
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(
        "NOTE: the device-enumeration LOGIC above is exercised against a stubbed directory "
        "only -- whether a real Leonardo re-enumerates on the SAME port or a NEW one after "
        "this touch, and whether the read-back chain fits inside the Caterina window at all, "
        "is UNPROVEN here and is proven only at Leonardo bring-up (plan 10)."
    )

    return 0 if ok_overall else 1


if __name__ == "__main__":
    sys.exit(main())
