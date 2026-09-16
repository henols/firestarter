#!/usr/bin/env python3
"""Read and write VALIDATED-EPROMS.md. The file is generated — never hand-edited.

The ledger records chips whose community `dev test` sweep passed every applicable
step on real hardware. This script owns its format, so every run produces the same
shape and a hand edit is normalised away on the next write.

Two kinds of content:

  authored   one record per validated chip: host, firmware, issues, date, and an
             optional per-chip note. Held in the Validated chips table and read
             back from it.
  derived    aliases, families, and family variation. Computed from the authored
             records plus firestarter_app/firestarter/data/chip_database.json.

A Notes section, when present, is preserved verbatim across a rewrite. Put there
anything a table cannot carry.

Self-contained: stdlib only. Reads chip_database.json as data; imports nothing
from firestarter_app.

    eprom_ledger.py list
    eprom_ledger.py add --chip W29C040 --host 3.0.0b33 --firmware 3.0.0b22 \\
                        --issues '#48' --date 2026-08-31
    eprom_ledger.py write          # regenerate the file from its own records
    eprom_ledger.py check          # exit 1 if the file differs from a fresh render
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

Key = tuple[int, str, int]

NOT_REPORTED = "not reported"

# Protocol names, transcribed from firestarter_fw/include/proto_constants.h.
# Held here rather than read from the firmware, because that submodule may be
# absent from a clone and the ledger's content must not depend on whether it is
# checked out. A stale entry costs a label, never a behaviour: an algorithm with
# no name here renders as its own hex value.
PROTO_NAMES = {
    0x05: "FLASH_5V_PAGE",
    0x06: "FLASH_NOR_UNLOCK",
    0x07: "EPROM_28PIN",
    0x08: "EPROM_32PIN",
    0x0B: "EPROM_24PIN",
    0x0D: "EEPROM_PARALLEL",
    0x0E: "SRAM_32PIN",
    0x10: "FLASH_INTEL",
    0x27: "SRAM_24PIN",
    0x28: "SRAM_28PIN",
    0x29: "SRAM_32PIN_NVRAM",
    0x34: "EEPROM_8051BUS",
}


def family_names(keys: list[Key]) -> dict[Key, str]:
    """Name each family after its protocol, disambiguated only where it must be.

    The name is a function of the key alone, so adding a chip never renames a
    family that was already present.
    """
    by_proto: dict[str, list[Key]] = collections.defaultdict(list)
    for k in keys:
        name = PROTO_NAMES.get(k[0])
        by_proto["PROTO_" + name if name else f"0x{k[0]:02X}"].append(k)
    names: dict[Key, str] = {}
    for proto, group in by_proto.items():
        if len(group) == 1:
            names[group[0]] = proto
            continue
        # Same protocol, several pinouts or rails: qualify with the pinout, and
        # with the rail too when the pinout still does not separate them.
        by_pinout: dict[str, list[Key]] = collections.defaultdict(list)
        for k in group:
            by_pinout[k[1]].append(k)
        for pinout, sub in by_pinout.items():
            for k in sub:
                names[k] = (
                    f"{proto}/{pinout}"
                    if len(sub) == 1
                    else f"{proto}/{pinout}/{k[2] / 1000:g}V"
                )
    return names
H_CHIPS = "## Validated chips"
H_ALIASES = "## Alternative part numbers"
H_FAMILIES = "## Families"
H_VARIATION = "## Family variation"
H_NOTES = "## Notes"

ROW_RE = re.compile(
    r"^\|\s*(?P<chip>[A-Za-z0-9_+.-]+)\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|"
    r"\s*(?P<host>[^|]+?)\s*\|\s*(?P<firmware>[^|]+?)\s*\|\s*(?P<issues>[^|]+?)\s*\|"
    r"\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*$",
    re.M,
)


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, *[os.pardir] * 4))
    return root if os.path.isdir(os.path.join(root, ".claude")) else os.getcwd()


ROOT = _repo_root()
DEFAULT_LEDGER = os.path.join(ROOT, "VALIDATED-EPROMS.md")
DEFAULT_DB = os.path.join(
    ROOT, "firestarter_app", "firestarter", "data", "chip_database.json"
)


def load_db(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def index(db: dict):
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


def read_records(ledger: str) -> list[dict]:
    """Parse the authored records out of the Validated chips table.

    The table is located by its own header row, not by a section heading, so a
    renamed or renumbered heading cannot silently yield zero records.
    """
    if not os.path.exists(ledger):
        return []
    with open(ledger, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    start = next(
        (
            i
            for i, l in enumerate(lines)
            if l.startswith("| Chip ") and "Validated" in l and "Host" in l
        ),
        None,
    )
    if start is None:
        return []
    body_lines = []
    for l in lines[start + 1 :]:
        if l.startswith("|"):
            body_lines.append(l)
        elif body_lines:
            break
    body = "\n".join(body_lines)
    out = []
    for m in ROW_RE.finditer(body):
        d = m.groupdict()
        if d["chip"].lower() in ("chip", "---"):
            continue
        out.append(
            {
                "chip": d["chip"].strip().upper(),
                "host": d["host"].strip(),
                "firmware": d["firmware"].strip(),
                "issues": d["issues"].strip(),
                "date": d["date"].strip(),
            }
        )
    return out


def read_notes(ledger: str) -> str:
    """Return the Notes section body verbatim, or ''."""
    if not os.path.exists(ledger):
        return ""
    with open(ledger, encoding="utf-8") as f:
        text = f.read()
    if H_NOTES not in text:
        return ""
    return text.split(H_NOTES, 1)[1].split("\n## ", 1)[0].strip("\n")


def render(records: list[dict], db_path: str, notes: str) -> str:
    db = load_db(db_path)
    parts, vendors, entry = index(db)
    known = [r for r in records if r["chip"] in entry]
    for r in records:
        if r["chip"] not in entry:
            print(f"WARN: not in the database, dropped: {r['chip']}", file=sys.stderr)

    keys = sorted({entry[r["chip"]][2] for r in known})
    fam_of: dict[Key, str] = family_names(keys)
    known.sort(key=lambda r: (fam_of[entry[r["chip"]][2]], r["chip"]))
    valset = {r["chip"] for r in known}

    L: list[str] = []
    L.append("# Validated EPROMs")
    L.append("")

    L.append(H_CHIPS)
    L.append("")
    L.append("| Chip | Vendor | Family | Size | VCC | Chip ID | Host | Firmware | Issues | Validated |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in known:
        vendor, e, k = entry[r["chip"]]
        el, pr = e["electrical"], e["programming"]
        cid = (
            "none"
            if not pr.get("chip_id_check")
            else f"`0x{int(pr['chip_id_value'], 16):04X}`"
        )
        L.append(
            f"| {r['chip']} | {vendor} | {fam_of[k]} | {el['size_bytes'] // 1024} KiB | "
            f"{el['vcc_mv'] / 1000:g} V | {cid} | {r['host']} | {r['firmware']} | "
            f"{r['issues']} | {r['date']} |"
        )
    L.append("")

    L.append(H_ALIASES)
    L.append("")
    L.append("| Chip | Same database entry |")
    L.append("|---|---|")
    any_alias = False
    for r in known:
        _, e, _ = entry[r["chip"]]
        grp = [p.strip() for p in e["part_number"].split(",")]
        others = [p for p in grp if p.upper() != r["chip"]]
        if others:
            any_alias = True
            L.append(f"| {r['chip']} | {', '.join(others)} |")
    if not any_alias:
        L.append("| — | — |")
    L.append("")

    L.append(H_FAMILIES)
    L.append("")
    L.append("| Family | Algorithm | Pinout | VPP | Parts | Vendors | Validated members |")
    L.append("|---|---|---|---|---|---|---|")
    for k, fid in sorted(fam_of.items(), key=lambda kv: kv[1]):
        algo, pinout, vpp = k
        members = sorted(r["chip"] for r in known if entry[r["chip"]][2] == k)
        L.append(
            f"| {fid} | `0x{algo:02X}` | `{pinout}` | {vpp / 1000:g} V | "
            f"{len(parts[k])} | {len(vendors[k])} | {', '.join(members)} |"
        )
    L.append("")

    L.append(H_VARIATION)
    L.append("")
    L.append("| Family | Size range | Page sizes | Validated | Untested siblings |")
    L.append("|---|---|---|---|---|")
    for k, fid in sorted(fam_of.items(), key=lambda kv: kv[1]):
        members = [
            e
            for _, cs in db.items()
            for e in cs
            if (
                e["programming"]["algorithm"],
                e["pinout"],
                e["electrical"]["vpp_mv"],
            )
            == k
        ]
        sizes = sorted({e["electrical"]["size_bytes"] for e in members})
        pages = sorted(
            {e["programming"].get("page_size") for e in members},
            key=lambda x: (x is None, x),
        )
        lo, hi = sizes[0] // 1024, sizes[-1] // 1024
        srange = f"{lo} KiB" if lo == hi else f"{lo}–{hi} KiB"
        prange = (
            "not used"
            if pages == [None]
            else ", ".join(str(p) for p in pages if p is not None)
        )
        nval = len([r for r in known if entry[r["chip"]][2] == k])
        untested = len({p for p in parts[k] if p.upper() not in valset})
        L.append(f"| {fid} | {srange} | {prange} | {nval} | {untested} |")
    L.append("")

    L.append(H_NOTES)
    L.append("")
    L.append(notes.strip("\n") if notes.strip() else "- None.")
    L.append("")
    return "\n".join(L)


def cmd_list(args) -> int:
    for r in read_records(args.ledger):
        print(
            f"{r['chip']:<12} host={r['host']:<10} fw={r['firmware']:<14} "
            f"issues={r['issues']:<10} {r['date']}"
        )
    return 0


def cmd_write(args) -> int:
    records = read_records(args.ledger)
    notes = read_notes(args.ledger)
    text = render(records, args.db, notes)
    with open(args.ledger, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {args.ledger} — {len(records)} chip(s)")
    return 0


def cmd_add(args) -> int:
    records = read_records(args.ledger)
    chip = args.chip.strip().upper()
    _, _, entry = index(load_db(args.db))
    if chip not in entry:
        print(
            f"ERROR: {chip} is not in the chip database. The ledger records chips this "
            f"project can program, so a name it cannot resolve is a typo or an "
            f"unsupported part.",
            file=sys.stderr,
        )
        return 1
    if any(r["chip"] == chip for r in records) and not args.force:
        print(f"ERROR: {chip} is already recorded. Use --force to replace.", file=sys.stderr)
        return 1
    records = [r for r in records if r["chip"] != chip]
    records.append(
        {
            "chip": chip,
            "host": args.host.strip(),
            "firmware": (args.firmware or NOT_REPORTED).strip(),
            "issues": args.issues.strip(),
            "date": args.date.strip(),
        }
    )
    notes = read_notes(args.ledger)
    text = render(records, args.db, notes)
    with open(args.ledger, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"added {chip} — {len(records)} chip(s) in {args.ledger}")
    return 0


def cmd_check(args) -> int:
    if not os.path.exists(args.ledger):
        print(f"ERROR: no ledger at {args.ledger}", file=sys.stderr)
        return 2
    with open(args.ledger, encoding="utf-8") as f:
        on_disk = f.read()
    fresh = render(read_records(args.ledger), args.db, read_notes(args.ledger))
    if on_disk == fresh:
        print(f"ok: {os.path.basename(args.ledger)} matches a fresh render")
        return 0
    import difflib

    diff = list(
        difflib.unified_diff(
            on_disk.split("\n"), fresh.split("\n"),
            fromfile="on disk", tofile="expected", lineterm="", n=1,
        )
    )
    print("DRIFT: the ledger differs from a fresh render.")
    for line in diff[:40]:
        print("  " + line)
    if len(diff) > 40:
        print(f"  … {len(diff) - 40} more line(s)")
    print("\nRegenerate with: eprom_ledger.py write")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--db", default=DEFAULT_DB)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="print the authored records")
    sub.add_parser("write", help="regenerate the ledger from its own records")
    sub.add_parser("check", help="exit 1 if the ledger differs from a fresh render")

    a = sub.add_parser("add", help="record a validated chip")
    a.add_argument("--chip", required=True)
    a.add_argument("--host", required=True)
    a.add_argument("--firmware", default=NOT_REPORTED)
    a.add_argument("--issues", required=True)
    a.add_argument("--date", required=True)
    a.add_argument("--force", action="store_true", help="replace an existing row")

    args = ap.parse_args()
    if not os.path.exists(args.db):
        print(f"ERROR: database not found: {args.db}", file=sys.stderr)
        return 2
    return {"list": cmd_list, "write": cmd_write, "check": cmd_check, "add": cmd_add}[
        args.cmd
    ](args)


if __name__ == "__main__":
    sys.exit(main())
