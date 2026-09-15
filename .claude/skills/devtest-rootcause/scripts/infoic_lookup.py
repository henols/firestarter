#!/usr/bin/env python3
"""Print the raw minipro infoic.xml record(s) for a part, plus the decode
build_db.py derives from them.

Self-contained: stdlib only. This skill OWNS its decode tables — it does not
import build_db.py, so it keeps working if firestarter_app moves or is absent.

Read-only: never writes the chip database, never invents a value.

    python3 infoic_lookup.py AT28C256
    python3 infoic_lookup.py W27E257 --raw
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# Owned decode tables. Transcribed from minipro's own constants. Keep them in
# step with build_db.py by hand. Do not "improve" a value from memory —
# an earlier draft guessed 0x80 as 18V when it is 13.5V, which would have
# fabricated a decode bug in W27E257 that does not exist.
# ---------------------------------------------------------------------------

# Pinned upstream catalog. Must match build_db.py:MINIPRO_XML_URL.
MINIPRO_XML_URL = (
    "https://gitlab.com/DavidGriffith/minipro/-/raw/"
    "a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml"
)

# Key is (voltages & 0xF0) — the HIGH nibble. Masking the full byte is the
# classic build_db.py bug: option bits in 3-0 push the lookup off the table
# and silently yield 0 mV.
#
# Values are MILLIVOLTS, deliberately the same unit as the generator's own
# table, so the two can be compared directly with no lossy string round-trip
# in the middle. Display formatting happens in `format_vpp()`.
VPP_MV = {
    0x00: 12000, 0x10: 9000, 0x20: 9500, 0x30: 10000,
    0x40: 11000, 0x50: 11500, 0x60: 12500, 0x70: 13000,
    0x80: 13500, 0x90: 14000, 0xA0: 14500, 0xB0: 15500,
    0xC0: 16000, 0xD0: 16500, 0xE0: 17000, 0xF0: 18000,
}



def format_vpp(mv: object) -> str:
    """Render a millivolt table value the way the old string table read.

    12000 -> "12V", 9500 -> "9.5V". `%g` drops the trailing ".0" so whole
    volts stay unadorned.
    """
    if not isinstance(mv, int):
        return "NOT IN TABLE"
    return f"{mv / 1000:g}V"


def fetch(path: str, url: str) -> str:
    """Download infoic.xml once and cache it (17.8 MB)."""
    if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
        return path
    print(f"fetching {url}\n     -> {path}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=120) as r:  # noqa: S310
        data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    return path


def split_pkg(token: str) -> tuple[str, str | None]:
    """Split an infoic name token into (part, package).

    Upstream qualifies most names with a package suffix — `W27E257@DIP28`.
    Some parts appear ONLY suffixed, so matching the whole token misses them
    outright. build_db.py strips the same suffix when it emits part_number.
    """
    part, _, pkg = token.strip().partition("@")
    return part, (pkg or None)


def norm(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", s).upper()


def as_int(v: str | None) -> int | None:
    if v is None:
        return None
    v = v.strip()
    try:
        return int(v, 16) if v.lower().startswith("0x") else int(v)
    except ValueError:
        return None


# From the infoic.xml header comment (the file documents its own `type` codes).
TYPE_NAMES = {1: "EEPROM", 2: "MCU/MPU", 3: "PLD/CPLD", 4: "SRAM",
              5: "LOGIC", 6: "NAND", 7: "EMMC", 8: "VGA/HDMI"}


def decode(ic: ET.Element) -> list[str]:
    """Report only what infoic.xml itself carries. Nothing here is invented."""
    out = []
    flags = as_int(ic.get("flags"))
    if flags is not None:
        erasable = bool(flags & 0x10)
        out.append(
            f"  flags & 0x10      = {'SET' if erasable else 'clear'}"
            f"   -> {'electrically erasable' if erasable else 'UV-EPROM'}"
            f"   (raw flags 0x{flags:X})"
        )
    volt = as_int(ic.get("voltages"))
    if volt is not None:
        idx = volt & 0xF0
        out.append(
            f"  voltages & 0xF0   = 0x{idx:02X}"
            f"  -> VPP {format_vpp(VPP_MV.get(idx))}"
            f"   (option bits 0x{volt & 0x0F:X})"
        )
    proto = as_int(ic.get("protocol_id"))
    if proto is not None:
        out.append(
            f"  protocol_id       = 0x{proto:02X}"
            "  -> programming.algorithm, before any safety flip"
        )
    var = as_int(ic.get("variant"))
    if var is not None:
        out.append(
            f"  variant           = 0x{var:04X}"
            f" (lo=0x{var & 0xFF:02X}, hi=0x{var >> 8:02X})  -> resolve_pinout_key()"
        )
    pm = as_int(ic.get("pin_map"))
    if pm is not None:
        out.append(
            f"  pin_map           = 0x{pm:04X}"
            f" (lo=0x{pm & 0xFF:02X} = pm_idx)  -> resolve_pinout_key()"
        )
    t = as_int(ic.get("type"))
    if t is not None:
        out.append(f"  type              = {t} ({TYPE_NAMES.get(t, '?')})")
    size = as_int(ic.get("code_memory_size"))
    if size is not None:
        out.append(f"  code_memory_size  = {size} (0x{size:X})  -> electrical.size_bytes")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part", nargs="?",
                    help="part number, e.g. AT28C256 (case/punctuation insensitive)")
    ap.add_argument("--xml", default=None, help="local infoic.xml cache path")
    ap.add_argument("--raw", action="store_true", help="dump every attribute verbatim")
    args = ap.parse_args()

    if not args.part:
        ap.error("a part number is required")

    url = MINIPRO_XML_URL
    sha = re.search(r"/raw/([0-9a-f]{8})", url)
    cache = args.xml or os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        f"infoic-{sha.group(1) if sha else 'unpinned'}.xml",
    )
    path = fetch(cache, url)
    want = norm(args.part)

    hits = 0
    mfg = dbtype = "?"
    for event, el in ET.iterparse(path, events=("start", "end")):
        if event == "start":
            if el.tag == "database":
                dbtype = el.get("type", "?")
            elif el.tag == "manufacturer":
                mfg = el.get("name", "?").strip()
            continue
        if el.tag != "ic":
            continue
        name = (el.get("name") or "").strip()
        matched = [tok for tok in name.split(",") if want == norm(split_pkg(tok)[0])]
        if matched:
            hits += 1
            pkgs = sorted({split_pkg(t)[1] or "(unqualified)" for t in matched})
            print(f"\n=== {name}   [{mfg}]   ({dbtype}) ===")
            print(f"  matched           : {', '.join(matched)}   packages: {', '.join(pkgs)}")
            if args.raw:
                for k, v in sorted(el.attrib.items()):
                    print(f"  {k:18} = {v}")
            else:
                for line in decode(el):
                    print(line)
        el.clear()

    if not hits:
        print(f"\nno <ic> record matches {args.part!r} in {os.path.basename(path)}.",
              file=sys.stderr)
        print("If the chip is physically real, this is tools/extra_chips.json "
              "territory — upstream genuinely lacks it.", file=sys.stderr)
        return 1
    print(f"\n{hits} record(s). DIP is the package this project programs; "
          "ignore PLCC/SOIC/TSOP rows unless an adapter is in play.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
