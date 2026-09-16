#!/usr/bin/env python3
"""Derive the family tables in VALIDATED-EPROMS.md from the chip database.

A family is every part sharing programming.algorithm, pinout and
electrical.vpp_mv -- the three fields that decide the programming procedure,
the socket wiring and the programming rail.

Section 1 of VALIDATED-EPROMS.md is authored: it records what a bench run
reported. Sections 2, 3 and 4 are derived from section 1 plus the database,
and this script is what derives them.

Self-contained: stdlib only. Reads chip_database.json as data; imports
nothing from firestarter_app.

    eprom_families.py                 # print the derived sections as markdown
    eprom_families.py --check         # exit 1 if the ledger disagrees with the database
    eprom_families.py --ledger PATH --db PATH
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

Key = tuple[int, str, int]


def _repo_root() -> str:
    """Locate the checkout from this file: <root>/.claude/skills/<s>/scripts/."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, *[os.pardir] * 4))
    return root if os.path.isdir(os.path.join(root, ".claude")) else os.getcwd()


ROOT = _repo_root()
DEFAULT_LEDGER = os.path.join(ROOT, "VALIDATED-EPROMS.md")
DEFAULT_DB = os.path.join(
    ROOT, "firestarter_app", "firestarter", "data", "chip_database.json"
)

# Section 1 row: | CHIP | VENDOR | Fn | 256 KiB | 5 V | `0x….` | host | fw | #n | date |
ROW_RE = re.compile(
    r"^\|\s*(?P<chip>[A-Z0-9]+)\s*\|\s*(?P<vendor>[A-Z0-9]+)\s*\|\s*"
    r"(?P<family>F\d+)\s*\|\s*(?P<size>\d+)\s*KiB\s*\|",
    re.M,
)


def load_db(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def index(db: dict) -> tuple[dict[Key, set], dict[Key, set], dict[str, tuple]]:
    """Return (parts by family, vendors by family, entry by upper-cased part)."""
    parts: dict[Key, set] = collections.defaultdict(set)
    vendors: dict[Key, set] = collections.defaultdict(set)
    entry: dict[str, tuple] = {}
    for vendor, chips in db.items():
        for e in chips:
            key: Key = (
                e["programming"]["algorithm"],
                e["pinout"],
                e["electrical"]["vpp_mv"],
            )
            vendors[key].add(vendor)
            for raw in e["part_number"].split(","):
                pn = raw.strip()
                parts[key].add(pn)
                entry.setdefault(pn.upper(), (vendor, e, key))
    return parts, vendors, entry


def validated_chips(ledger: str) -> list[str]:
    """Read section 1's Chip column. That table is the authored source."""
    with open(ledger, encoding="utf-8") as f:
        text = f.read()
    return [m.group("chip") for m in ROW_RE.finditer(text)]


def families_of(chips, entry) -> dict[str, Key]:
    """Assign stable F-numbers in first-appearance order of section 1."""
    seen: dict[Key, str] = {}
    for chip in chips:
        if chip.upper() not in entry:
            continue
        key = entry[chip.upper()][2]
        if key not in seen:
            seen[key] = f"F{len(seen) + 1}"
    return {fid: key for key, fid in seen.items()}


def render(ledger: str, db_path: str) -> str:
    db = load_db(db_path)
    parts, vendors, entry = index(db)
    chips = validated_chips(ledger)
    missing = [c for c in chips if c.upper() not in entry]
    if missing:
        print(f"WARN: not in the database: {', '.join(missing)}", file=sys.stderr)
    fams = families_of(chips, entry)
    valset = {c.upper() for c in chips}

    out: list[str] = []
    out.append("| Family | Algorithm | Pinout | VPP | Parts | Vendors | Validated members |")
    out.append("|---|---|---|---|---|---|---|")
    for fid, key in fams.items():
        algo, pinout, vpp = key
        members = sorted(c for c in chips if entry[c.upper()][2] == key)
        out.append(
            f"| {fid} | `0x{algo:02X}` | `{pinout}` | {vpp / 1000:g} V | "
            f"{len(parts[key])} | {len(vendors[key])} | {', '.join(members)} |"
        )

    total_parts = sum(len(s) for s in parts.values())
    covered = sum(len(parts[k]) for k in fams.values())
    rails = sorted({e["electrical"]["vpp_mv"] for _, cs in db.items() for e in cs})
    out.append("")
    out.append(
        f"The database holds {total_parts} distinct part numbers in {len(parts)} "
        f"families. These {len(fams)} cover {covered} of them."
    )
    out.append(
        "The database carries "
        f"{len(rails)} distinct programming rails: "
        + ", ".join(f"{v / 1000:g}" for v in rails)
        + " V."
    )

    out.append("")
    out.append("| Family | Size range | Page sizes in family | Untested siblings |")
    out.append("|---|---|---|---|")
    for fid, key in fams.items():
        sizes = sorted(
            {
                e["electrical"]["size_bytes"]
                for _, cs in db.items()
                for e in cs
                if (
                    e["programming"]["algorithm"],
                    e["pinout"],
                    e["electrical"]["vpp_mv"],
                )
                == key
            }
        )
        pages = sorted(
            {
                e["programming"].get("page_size")
                for _, cs in db.items()
                for e in cs
                if (
                    e["programming"]["algorithm"],
                    e["pinout"],
                    e["electrical"]["vpp_mv"],
                )
                == key
            },
            key=lambda x: (x is None, x),
        )
        lo, hi = sizes[0] // 1024, sizes[-1] // 1024
        srange = f"{lo} KiB only" if lo == hi else f"{lo}–{hi} KiB ({len(sizes)} distinct)"
        prange = (
            f"not used by `0x{key[0]:02X}`"
            if pages == [None]
            else ", ".join(str(p) for p in pages if p is not None)
        )
        untested = len({p for p in parts[key] if p.upper() not in valset})
        out.append(f"| {fid} | {srange} | {prange} | {untested} |")
    return "\n".join(out)


def check(ledger: str, db_path: str) -> int:
    """Confirm every derived number in the ledger matches the database."""
    generated = render(ledger, db_path)
    with open(ledger, encoding="utf-8") as f:
        text = f.read()
    bad = 0
    for line in generated.split("\n"):
        if not line.startswith("| F"):
            continue
        if line not in text:
            print(f"DRIFT: ledger is missing or disagrees with:\n  {line}")
            bad += 1
    if bad:
        print(
            f"\n{bad} derived row(s) disagree with {os.path.basename(db_path)}. "
            "Regenerate with: eprom_families.py"
        )
        return 1
    print(f"ok: every derived row in {os.path.basename(ledger)} matches the database")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the ledger's derived rows disagree with the database")
    args = ap.parse_args()

    for path, what in ((args.ledger, "ledger"), (args.db, "database")):
        if not os.path.exists(path):
            print(f"ERROR: {what} not found: {path}", file=sys.stderr)
            return 2

    if args.check:
        return check(args.ledger, args.db)
    print(render(args.ledger, args.db))
    return 0


if __name__ == "__main__":
    sys.exit(main())
