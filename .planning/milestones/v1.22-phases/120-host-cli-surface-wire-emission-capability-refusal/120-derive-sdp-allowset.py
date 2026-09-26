#!/usr/bin/env python3
"""FINAL: derive the SDP-capability partition for the 84 algorithm==13 chips from
infoic.xml INFOIC2PLUS flags bit 15 (MP_PROTECT_AFTER), with page_size as an
independent corroborating axis.

Keying rule: EXACT token match, parentheticals NOT stripped (RESEARCH F-02 rule 1).
Paren-stripping is what produced the spurious MIXED verdict on ATMEL/AT28C64.
"""
import json
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

INFOIC = os.environ.get("INFOIC_XML", "infoic.xml")  # fetch: curl -sSL -o infoic.xml https://gitlab.com/DavidGriffith/minipro/-/raw/a8efaedc236c1d9718bd28299dfbb99536b010ff/infoic.xml
DB = "/workspaces/firestarter_app/firestarter/data/chip_database.json"
B14, B15 = 0x4000, 0x8000

root = ET.parse(INFOIC).getroot()
sect = root.findall(".//database[@type='INFOIC2PLUS']")[0]

# EXACT token (upper, package-suffix stripped only) -> set of (flags, page_size)
tok2 = defaultdict(set)
for mfr in sect.findall("manufacturer"):
    for ic in mfr.findall("ic"):
        fl = int(ic.get("flags", "0x0"), 16)
        pg = int(ic.get("page_size", "0x0"), 16)
        for t in ic.get("name", "").split(","):
            t = t.strip()
            if not t:
                continue
            tok2[t.split("@")[0].strip().upper()].add((fl, pg))

with open(DB) as f:
    db = json.load(f)

rows = []
for mfr_key, parts in db.items():
    if not isinstance(parts, list):
        continue
    for p in parts:
        if p.get("programming", {}).get("algorithm") != 13:
            continue
        raw = p.get("part_number", "")
        toks = [t.strip() for t in raw.split(",") if t.strip()]
        per = []
        for t in toks:
            per.append((t, tok2.get(t.upper(), set())))
        rows.append((mfr_key, raw, per, p))

allow, refuse, mixed, nomatch = [], [], [], []
disagree = []
for mfr_key, raw, per, p in rows:
    b15s, pgs, unmatched = set(), set(), []
    for t, hits in per:
        if not hits:
            unmatched.append(t)
            continue
        for fl, pg in hits:
            b15s.add(bool(fl & B15))
            pgs.add(pg)
    pinout = p.get("pinout", "?")
    rec = (mfr_key, raw, sorted(pgs), pinout, len(unmatched), len(per))
    if unmatched and not b15s:
        nomatch.append(rec)
    elif b15s == {True}:
        allow.append(rec)
    elif b15s == {False}:
        refuse.append(rec)
    else:
        mixed.append(rec)
    # cross-check: b15 should track page_size > 1
    if b15s and pgs:
        pg_says = {pg > 1 for pg in pgs}
        if pg_says != b15s:
            disagree.append((mfr_key, raw, sorted(b15s), sorted(pgs)))

W = 112
print("=" * W)
print("SDP-CAPABILITY PARTITION derived from infoic.xml INFOIC2PLUS flags bit 15 (MP_PROTECT_AFTER)")
print("minipro @ a8efaedc236c1d9718bd28299dfbb99536b010ff — exact-token keying, parens NOT stripped")
print("=" * W)
print()
print(f"ALLOW  (b15=1, SDP-capable) : {len(allow)}")
print(f"REFUSE (b15=0, no SDP)      : {len(refuse)}")
print(f"MIXED  (tokens disagree)    : {len(mixed)}")
print(f"NO INFOIC MATCH             : {len(nomatch)}")
print(f"TOTAL                       : {len(allow)+len(refuse)+len(mixed)+len(nomatch)}   (must be 84)")
print()
print("Independent cross-check — does bit 15 track page_size > 1 (page-write mode)?")
if not disagree:
    print("  ✓ PERFECT AGREEMENT on all 84. b15=1 <=> page_size>1, b15=0 <=> page_size==1.")
else:
    print(f"  ✗ {len(disagree)} disagreements:")
    for d in disagree:
        print(f"      {d[0]}/{d[1]}  b15={d[2]} page_size={d[3]}")
print()

for title, bucket in (("ALLOW — b15=1", allow), ("REFUSE — b15=0", refuse),
                      ("MIXED", mixed), ("NO MATCH", nomatch)):
    if not bucket:
        continue
    print("=" * W)
    print(f"{title}  ({len(bucket)} entries)")
    print("=" * W)
    for mfr_key, raw, pgs, pinout, unm, ntok in sorted(bucket):
        pgstr = ",".join(f"0x{x:02x}" for x in pgs)
        print(f"  {mfr_key:18.18s} {raw:52.52s} page={pgstr:12.12s} {pinout}")
    print()

# machine-readable output for the planner
out = {
    "source": "minipro infoic.xml @ a8efaedc236c1d9718bd28299dfbb99536b010ff",
    "section": "INFOIC2PLUS",
    "axis": "flags bit 15 (0x8000) MP_PROTECT_AFTER",
    "corroborating_axis": "page_size > 1",
    "allow": [{"mfr": r[0], "part_number": r[1]} for r in sorted(allow)],
    "refuse": [{"mfr": r[0], "part_number": r[1]} for r in sorted(refuse)],
    "counts": {"allow": len(allow), "refuse": len(refuse), "total": len(allow) + len(refuse)},
}
with open(os.environ.get("OUT", "sdp_partition.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"Machine-readable partition written to sdp_partition.json")
