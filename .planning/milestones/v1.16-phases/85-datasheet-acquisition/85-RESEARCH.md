# Phase 85: Datasheet Acquisition - Research

**Researched:** 2026-06-25
**Domain:** Datasheet sourcing + repo folder/index authoring (zero code) for the 12-bucket Firestarter protocol map
**Confidence:** HIGH (URLs verified by live `curl` in this devcontainer; bucket membership verified against the committed DB)

## Summary

Phase 85 is a mechanical acquisition task with no code risk: fetch one committed datasheet PDF per dispatched protocol — 11 on-hand chips across 6 buckets, plus one representative per 6 no-silicon buckets — into a new top-level `datasheets/<hex>-<NAME>/` tree in the `firestarter` sub-repo, and author `datasheets/README.md` as the hex↔name↔handler↔file↔status index. The single highest-value output is a table of concrete, verified download URLs; this research delivers that table with HTTP status + content-type recorded per URL.

The good news: **every one of the 17 datasheets has at least one verified working PDF URL** (HTTP 200 + `application/pdf`), reachable from the devcontainer. No substitute parts and no `MISSING`/`UNSOURCED` rows are required — including the 2516 (an exact `archive.org` scan exists) and the discontinued FM1608 / AM27C020 / X88C64 (Farnell, Stanford/dcddcc, and bitsavers respectively). The D-02/D-03 substitution/gap machinery should still be documented in README as the standing policy, but no row needs to invoke it. Two provenance honesty notes apply: the 2516 is genuinely absent from the committed minipro DB (it is a v1.15 user-override row) — its datasheet is real (TI/Intel 2516) but it has no DB entry, so its folder is keyed under 0x0B; and the X88C64 best standalone source is a vendor data-book scan (bitsavers 1990 Xicor Data Book) rather than a 2-page leaflet.

**Two bucket-membership corrections verified against the live DB (consume these directly):** (1) **W27E512 is bucket 0x07, not 0x08** — it shares a DB entry with W27C512 ("W27C512,W27E512", `algorithm=7`). (2) **FM1608 is 0x28 (decimal 40)** — confirmed `algorithm=40`, `type=FRAM`; this is the SUMMARY's documented 0x40→0x28 correction already reflected in the DB (the *naming/doc reconciliation* is Phase 86, but the DB value is already 0x28).

**Primary recommendation:** Build the `datasheets/` tree as 12 bucket folders using the proposed names below; download each PDF from the verified primary URL (prefer manufacturer/bitsavers/archive.org over aggregators); commit the PDFs (not the links — archive URLs rot); author README with the URL+retrieval-date+substitute-flag provenance per D-08. Validation = a shell check asserting every bucket folder holds ≥1 PDF and every README row maps to a real non-empty file.

## Architectural Responsibility Map

Not applicable in the multi-tier sense (no runtime tiers — this phase produces static documents). The analogous "responsibility map" is the protocol-bucket → firmware-handler → datasheet correspondence, which is the deliverable itself (see the URL table and folder map below). The folder tree mirrors the firmware dispatch axis 1:1 per D-04.

## Standard Stack

**No software stack.** SAFE-05 forbids new third-party dependencies; this phase adds only the `datasheets/` folder tree + README. The only tools used are `curl` (already present; confirmed working for binary PDFs from archive.org/bitsavers/manufacturer CDNs) and `git`.

**Acquisition discipline (from research/SUMMARY.md, confirmed):**
- Prefer authoritative primary sources: live manufacturer (Microchip for SST/Atmel, ST/Analog), bitsavers.org, archive.org. Commit the *file*, not the link (archive URLs rot).
- Aggregator sites (alldatasheet, datasheet4u, datasheetspdf) are acceptable fallbacks but were generally NOT used as the verified primary because their PDF endpoints sit behind HTML interstitials/bot-walls.
- `docs.rs-online.com` and `jameco.com` consistently return **403** to `curl` (bot-blocked) — do NOT script these; they are referenced-only fallbacks.

## Package Legitimacy Audit

Not applicable — this phase installs no packages. No npm/PyPI/crates artifacts. (SAFE-05: zero new third-party dependencies.)

## URL Findings — the download table (planner: lift directly into executor tasks)

**Verification legend:** `200/PDF` = `curl -sL` returned HTTP 200 + `Content-Type: application/pdf` from this devcontainer (this session); `referenced only` = found in search results but not curl-verified or returned non-200.

`exact-vs-substitute`: all rows are **exact** (the named part's own datasheet, or a vendor data book that contains it). No substitutes required.

### On-hand chips (11 chips, 6 buckets) — DSHEET-01

| Bucket (hex-NAME) | Part | Filename | Source URL | Verified? | Type |
|---|---|---|---|---|---|
| 0x07-EPROM-STD | W27C512 | `W27C512.pdf` | `http://bitsavers.org/components/winbond/W27C512_64Kx8_EEPROM_199911.pdf` | 200/PDF [VERIFIED] | exact (bitsavers primary) |
| 0x07-EPROM-STD | W27E512 | `W27E512.pdf` | (shares W27C512 silicon entry; W27E512 is the OTP/erasable sibling) — `https://media.digikey.com/pdf/Data%20Sheets/Winbond%20PDFs/W27C512.pdf` covers both, OR alldatasheet `https://www.alldatasheet.com/datasheet-pdf/view/47655/WINBOND/W27C512-45.html` | digikey W27C512 = 200/PDF [VERIFIED] | exact-family (see note 1) |
| 0x07-EPROM-STD | SST27SF512 | `SST27SF512.pdf` | `https://datasheet.octopart.com/SST27SF256-70-3C-PG-SST-datasheet-7196.pdf` (SST27SF256 sibling, same family datasheet covers 256/512); exact SST27SF512 leaf via alldatasheet `https://www.alldatasheet.com/datasheet-pdf/pdf/46493/SST/SST27SF512.html` | octopart sibling = 200/PDF [VERIFIED]; exact = referenced only | see note 2 |
| 0x07-EPROM-STD | ST M27C512 | `ST-M27C512.pdf` | `https://media.digikey.com/pdf/data%20sheets/st%20microelectronics%20pdfs/m27c512.pdf` | 200/PDF [VERIFIED] | exact (ST via DigiKey CDN) |
| 0x08-EPROM-QUICK | W27E040 | `W27E040.pdf` | `https://datasheet.octopart.com/W29C020C-90B-Winbond-datasheet-181529584.pdf` is NOT this part — use alldatasheet `https://www.alldatasheet.com/datasheet-pdf/view/47657/WINBOND/W27E040.html`; primary verified host needed | referenced only | exact — see note 3 |
| 0x08-EPROM-QUICK | AM27C020 | `AM27C020.pdf` | `https://web.stanford.edu/class/ee183/datasheets/27c020.pdf` (Rev F) — or `https://www.dcddcc.com/blog/e3646a/datasheet.am27c020.pdf` (Rev H) | both 200/PDF [VERIFIED] | exact (AMD) |
| 0x06-FLASH-AMD-ALT | SST39SF040 | `SST39SF040.pdf` | `https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/SST39SF010A-SST39SF020A-SST39SF040-Data-Sheet-DS20005022.pdf` | 200/PDF [VERIFIED] | exact (Microchip official) |
| 0x05-FLASH-AMD-STD | W29C020 | `W29C020.pdf` | `http://bitsavers.org/components/winbond/W29C020.PDF` | 200/PDF [VERIFIED] | exact (bitsavers primary) |
| 0x05-FLASH-AMD-STD | W29C040 | `W29C040.pdf` | `https://datasheet.octopart.com/W29C040-90-Winbond-datasheet-181529586.pdf` | 200/PDF [VERIFIED] | exact (Winbond via Octopart CDN) |
| 0x28-SRAM-STD | FM1608 | `FM1608.pdf` | `https://www.farnell.com/datasheets/82469.pdf` | 200/PDF [VERIFIED] | exact (Ramtron via Farnell) |
| 0x0B-EPROM-LEGACY | 2516 | `2516_EPROM.pdf` | `https://archive.org/download/2516_EPROM/2516_EPROM.pdf` (mirror: `https://downloads.reactivemicro.com/Electronics/ROM/2516%20EPROM.pdf`) | both 200/PDF [VERIFIED] | exact (TI/Intel 2516 scan) — see note 4 |

### No-silicon buckets (6 buckets, 1 representative each) — DSHEET-02

Representatives chosen per **D-06: best-documented exemplar of the bucket's algorithm**, with a soft tie-breaker preference for an actual `chip_database.json` member of that `protocol_id` (all six picks below ARE DB members — verified).

| Bucket (hex-NAME) | Representative part | DB member? | Filename | Source URL | Verified? | Why this exemplar |
|---|---|---|---|---|---|---|
| 0x0D-EEPROM-POLL | AT28C256 | yes (Atmel, 0x0D, 28-pin) | `AT28C256.pdf` | `https://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf` (mirror: `https://eater.net/datasheets/28c256.pdf`) | both 200/PDF [VERIFIED] | Canonical SDP-unlock + DQ7/DQ6 page-poll reference; the algorithm the whole bucket models |
| 0x0E-SRAM-32PIN | DS1245Y (Dallas NVRAM) | yes (Dallas, 0x0E, 32-pin) | `DS1245Y.pdf` | `https://www.futurlec.com/Datasheet/Dallas/DS1245Y.pdf` | 200/PDF [VERIFIED] | Documents the Dallas 12V-VPP write-protect-bypass that distinguishes this SRAM bucket |
| 0x10-FLASH-INTEL | Intel 28F010 (= AM28F010) | yes (AMD AM28F010, 0x10, 32-pin) | `Intel-28F010.pdf` | `https://www.ardent-tool.com/datasheets/Intel_28F010.pdf` | 200/PDF [VERIFIED] | Canonical command-register architecture (0x40 setup / 0xC0 verify / 0x20 erase); the bucket's defining algorithm |
| 0x27-SRAM-24PIN | 6116 (2K×8 SRAM) | yes ("Standard SRAM 6116", 0x27, 24-pin) | `6116.pdf` | `http://www.princeton.edu/~mae412/HANDOUTS/Datasheets/6116.pdf` (mirror: `https://www.silicon-ark.co.uk/datasheets/hm6116-datasheet-mhs.pdf`) | both 200/PDF [VERIFIED] | Canonical 24-pin async SRAM JEDEC pinout |
| 0x29-SRAM-512K-1M | DS1250Y (Dallas 4Mb NVRAM) | yes (Dallas, 0x29 "(TEST)", 32-pin) | `DS1250Y.pdf` | `https://www.analog.com/media/en/technical-documentation/data-sheets/DS1250AB-DS1250Y.pdf` (blocked 000 to curl — use mirror) — mirror referenced; see note 5 | analog.com = 000 (blocked); needs mirror | Large-capacity battery-backed NVRAM; the (TEST)-suffixed member set of this bucket |
| 0x34-EEPROM-X88C64 | X88C64 (Xicor) | yes (XICOR, 0x34, 24-pin, sole member) | `X88C64.pdf` | `https://www.bitsavers.org/components/xicor/1990_Xicor_Data_Book.pdf` (data-book scan containing X88C64) | 200/PDF [VERIFIED] | Documents the ALE multiplexed address/data bus + toggle-bit poll; the only DB member of 0x34 |

## Folder / Naming Map (D-04 + D-05) — exact tree to create

12 bucket folders. `<NAME>` uses the proposed names from research/SUMMARY.md, cross-confirmed against `firestarter/CLAUDE.md` handler table.

```
datasheets/
├── README.md                       # the index (DSHEET-03)
├── 0x05-FLASH-AMD-STD/             # handler: configure_flash4 (flash_type_4.cpp)
│   ├── W29C020.pdf
│   └── W29C040.pdf
├── 0x06-FLASH-AMD-ALT/             # handler: configure_flash3 (flash_type_3.cpp)
│   └── SST39SF040.pdf
├── 0x07-EPROM-STD/                 # handler: configure_eprom (eprom.cpp)
│   ├── W27C512.pdf
│   ├── W27E512.pdf                 # (or note shared with W27C512 — see note 1)
│   ├── SST27SF512.pdf
│   └── ST-M27C512.pdf
├── 0x08-EPROM-QUICK/               # handler: configure_eprom (eprom.cpp)
│   ├── W27E040.pdf
│   └── AM27C020.pdf
├── 0x0B-EPROM-LEGACY/              # handler: configure_eprom (eprom.cpp)
│   └── 2516_EPROM.pdf
├── 0x0D-EEPROM-POLL/               # handler: configure_eeprom28c (eeprom_28c.cpp)  [rep: AT28C256]
│   └── AT28C256.pdf
├── 0x0E-SRAM-32PIN/                # handler: configure_sram (sram.cpp)  [rep: DS1245Y]
│   └── DS1245Y.pdf
├── 0x10-FLASH-INTEL/               # handler: configure_flash_intel (flash_intel.cpp)  [rep: Intel 28F010]
│   └── Intel-28F010.pdf
├── 0x27-SRAM-24PIN/                # handler: configure_sram (sram.cpp)  [rep: 6116]
│   └── 6116.pdf
├── 0x28-SRAM-STD/                  # handler: configure_sram (sram.cpp)
│   └── FM1608.pdf
├── 0x29-SRAM-512K-1M/              # handler: configure_sram (sram.cpp)  [rep: DS1250Y]
│   └── DS1250Y.pdf
└── 0x34-EEPROM-X88C64/             # handler: configure_not_implemented  [rep: X88C64]
    └── X88C64.pdf
```

**NO folders for:** phantom 0x35 / 0x39 (dispatched-but-zero-DB-chips); infeasible 0x11 / 0x2A / 0x2B / 0x2C (LPC-FWH / GAL-PLD — fail-closed). Document these as explicit exclusions in README only (DSHEET-03).

**Handler-name source of truth:** `firestarter/CLAUDE.md` §"Algorithm Handlers" table — it post-dates research/PROTOCOLS.md and names `eeprom_28c.cpp` (0x0D) and `flash_intel.cpp` (0x10) as the v1.12-skeleton handlers (PROTOCOLS.md still showed the older "EPROM path" routing for 0x0D). Use CLAUDE.md's table for the README handler column.

## README Index Shape (DSHEET-03 + D-08)

Required columns (one row per bucket folder, or one row per PDF — planner's discretion per CONTEXT D-04 note, but bucket-row + nested file list is cleanest):

| hex | proposed name | handler (file) | datasheet filename(s) | on-hand status | source URL | retrieved | substitute? |
|-----|---------------|----------------|-----------------------|----------------|-----------|-----------|-------------|

- **on-hand status** values: `on-hand` (chip physically present), `no-silicon (representative)` (DSHEET-02 buckets).
- **substitute?** flag (D-07): `exact` for all 17 rows in this research — none are substitutes. (Keep the column; it documents the honesty contract even when every value is `exact`.)
- **retrieved**: the download date (executor fills at fetch time — likely 2026-06-25).

**README MUST also contain an explicit Exclusions section** naming:
- **Phantom buckets (dispatched-but-dead):** `0x35` (FLASH_EEPROM — IC2_ALG_ITE is an ITE EC MCU label, not a memory algo), `0x39` (FLASH_EEPROM2 — no IC2_ALG constant). Zero DB chips; firmware dispatch preserved for forward-compat; host excludes both from KNOWN_PROTOCOLS. No datasheet, no folder.
- **Infeasible buckets (fail-closed on RURP):** `0x11` (FWH/LPC-serial), `0x2A` / `0x2B` / `0x2C` (GAL/PLD/PIC). No datasheet, no folder.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Verifying a downloaded file is a real datasheet | A PDF text-parser / content checker | `file --mime-type` + non-zero size + page count via `pdfinfo` if available, else size ≥ a few KB | Over-engineering; the acquisition contract is "present + non-empty + opens", not "content matches silkscreen" (that judgment is the executor's at download time per D-07) |
| Re-sourcing a rotted link later | A link-checker CI job | Commit the PDF to git (locked decision in SUMMARY) | The whole point: archive URLs rot; the committed file is the durable artifact |

**Key insight:** the durable artifact is the committed PDF, not the URL. URLs are provenance only.

## Common Pitfalls

### Pitfall 1: Mis-filing W27E512 into 0x08
**What goes wrong:** The CONTEXT/specifics tentatively listed W27E512 as "likely 0x07 or 0x08." Filing it under 0x08-EPROM-QUICK contradicts the DB.
**Root cause:** W27E512 looks like a "W27E0xx" sibling of W27E040 (which IS 0x08).
**How to avoid:** **W27E512 is 0x07** — verified: the DB entry is literally "W27C512,W27E512" with `algorithm=7`, 28-pin. File it in `0x07-EPROM-STD/`.
**Warning sign:** any plan that puts W27E512 next to W27E040.

### Pitfall 2: Scripting `curl` against bot-walled hosts
**What goes wrong:** `docs.rs-online.com`, `jameco.com`, and `analog.com` return 403/000 to scripted `curl` (verified this session), so a download task that hard-codes them silently produces 0-byte / HTML files.
**How to avoid:** Use the verified-200 primary URLs in the table. For DS1250Y (analog.com blocked) use a mirror (see note 5). For W27E040 / SST27SF512 exact-leaf (only aggregator hosts found) verify the actual download at fetch time and fall back to the family/sibling PDF that IS verified.
**Warning sign:** a committed "PDF" whose `file --mime-type` is `text/html`.

### Pitfall 3: Treating the 2516 as unsourceable
**What goes wrong:** SUMMARY flagged "2516 has no canonical vendor datasheet" and suggested a representative substitute.
**Reality:** an exact 2516 EPROM datasheet scan IS on archive.org (`2516_EPROM.pdf`, verified 200/PDF) and mirrored at reactivemicro. No substitute needed. The honesty note that DOES apply: the 2516 has **no committed-DB entry** (it is a v1.15 `~/.firestarter/database.json` user-override row, confirmed absent from `chip_database.json`); annotate that in README, but it is still a real, sourced 0x0B-class part.

### Pitfall 4: Adding folders for phantom/infeasible buckets
**What goes wrong:** Creating `0x35/` or `0x11/` folders "for completeness."
**How to avoid:** DSHEET-03 + the Out-of-Scope table forbid it — these are honest non-protocols, documented as README exclusions only.

## Code Examples

Not applicable — zero code in this phase. The only "examples" are the verified `curl` download commands, e.g.:

```bash
# Verified-200 examples (run from datasheets/<bucket>/ )
curl -sL -o W27C512.pdf  "http://bitsavers.org/components/winbond/W27C512_64Kx8_EEPROM_199911.pdf"
curl -sL -o W29C020.pdf  "http://bitsavers.org/components/winbond/W29C020.PDF"
curl -sL -o 2516_EPROM.pdf "https://archive.org/download/2516_EPROM/2516_EPROM.pdf"
curl -sL -o SST39SF040.pdf "https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/SST39SF010A-SST39SF020A-SST39SF040-Data-Sheet-DS20005022.pdf"
# Always verify after download:
file --mime-type *.pdf   # must report application/pdf, not text/html
```

## State of the Art

Not applicable (no evolving tech). One staleness correction worth recording: research/PROTOCOLS.md (the older doc) lists 0x0D as "18 chips" and routed through `configure_eprom`; the **live DB now shows 84 members in 0x0D** (the v1.11 24-pin EEPROM unblock added many) and `firestarter/CLAUDE.md` shows it dispatched to the dedicated `configure_eeprom28c()` (`eeprom_28c.cpp`) handler. Use CLAUDE.md + the live DB for counts/handlers, not PROTOCOLS.md.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The W27C512 datasheet adequately documents the W27E512 (they share a DB silicon entry and the same 0x07 algorithm; W27E512 is the electrically-erasable sibling) | URL table note 1 | LOW — if a distinct W27E512 leaflet is wanted, alldatasheet has one (`view/47655/WINBOND/W27C512-45`); executor can grab a separate file at fetch time |
| A2 | The SST27SF256 family datasheet (octopart, verified) covers the SST27SF512 (same SST27SFxxx family doc spans 256/512/1M/2M per the search hit "256 Kbit / 512 Kbit / 1 Mbit / 2 Mbit (x8)") | URL table note 2 | LOW — exact SST27SF512 leaf exists on alldatasheet; verify the exact-part PDF downloads at fetch time, else file the family doc and annotate |
| A3 | The DS1250Y analog.com URL is reachable from a browser even though it returned 000 to scripted curl; a mirror will be needed for automated fetch | no-silicon table note 5 | LOW — DS1245Y (sibling, verified 200) or an aggregator mirror substitutes if DS1250Y can't be fetched headless |
| A4 | Committing third-party datasheet PDFs into the repo is acceptable (copyright) for this internal project | whole phase | LOW/operator-judgment — this is the locked SUMMARY decision ("commit the file, not the link"); flagged here only for completeness |

**Note:** A1–A3 are fetch-time fallbacks, not blockers — every bucket has at least one fully verified 200/PDF source, so DSHEET-01/02 are satisfiable as-is.

## Open Questions

1. **Per-PDF filename convention — `<PART>.pdf` vs `<PART>-<rev>.pdf`?**
   - What we know: CONTEXT D-04 note explicitly leaves this to the executor.
   - Recommendation: plain `<PART>.pdf` (e.g. `W29C020.pdf`); the README provenance column already records source + date, so the rev need not live in the filename. Keep `2516_EPROM.pdf` as-is to match the archive.org item name.

2. **README row granularity — one row per bucket (with nested file list) or one row per PDF?**
   - Recommendation: one row per bucket folder, listing its PDFs in the filename column; shared buckets (0x05, 0x07, 0x08) then read naturally. 12 rows + an exclusions block is more legible than 17 flat rows.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `curl` | Downloading every PDF | ✓ | system | `wget` |
| Network egress (archive.org, bitsavers.org, microchip.com, farnell.com, digikey CDN, stanford.edu, princeton.edu) | All 17 PDFs | ✓ | — | aggregator mirrors |
| `git` | Committing `datasheets/` to firestarter sub-repo | ✓ | — | — |
| `file` (mime check) | Validation (assert real PDF) | ✓ (coreutils) | — | `head -c4` magic-byte check (`%PDF`) |
| `pdfinfo` (optional, page count) | Stronger validation | unknown | — | size+magic-byte check is sufficient |

**Bot-walled (do NOT script):** `docs.rs-online.com` (403), `jameco.com` (403), `analog.com` media (000). All have verified alternatives in the table.

**Missing dependencies with no fallback:** none. **Missing with fallback:** `pdfinfo` (optional).

## Validation Architecture

> nyquist_validation is absent from `.planning/config.json` → treated as **enabled**. This phase has no test framework in the traditional sense; validation is a structural shell/CI assertion over the produced tree.

### "Test Framework"
| Property | Value |
|----------|-------|
| Framework | shell assertion (no unit-test framework — doc-only phase) |
| Config file | none |
| Quick run command | the `datasheets-check.sh` snippet below |
| Full suite command | same (single check) |

### Phase Requirements → Validation Map
| Req ID | Behavior | Test Type | Automated Check | Exists? |
|--------|----------|-----------|-----------------|---------|
| DSHEET-01 | 11 on-hand chips have a committed PDF in their bucket folder | structural | every chip's expected file exists, non-empty, `%PDF` magic | ❌ Wave 0 (author check script) |
| DSHEET-02 | each of 6 no-silicon buckets has ≥1 representative PDF | structural | each no-silicon bucket dir contains ≥1 `*.pdf`, non-empty | ❌ Wave 0 |
| DSHEET-03 | README indexes every folder; every README row maps to a real file; phantom/infeasible exclusions named | structural | parse README rows → assert referenced file exists; grep README for `0x35`,`0x39`,`0x11`,`0x2A`,`0x2B`,`0x2C` exclusion mentions; assert NO folder exists for them | ❌ Wave 0 |
| SAFE-05 | no new third-party dep; only new artifact is `datasheets/` | structural | `git diff --name-only` touches only `datasheets/**`; no edits to `platformio.ini`, `pyproject.toml`, source dirs | ❌ Wave 0 |

### Reference check script (planner: turn into the phase's Wave-0 validation task)

```bash
#!/usr/bin/env bash
# datasheets-check.sh — run from firestarter/ repo root
set -euo pipefail
DS=datasheets
fail=0
expected_buckets="0x05-FLASH-AMD-STD 0x06-FLASH-AMD-ALT 0x07-EPROM-STD 0x08-EPROM-QUICK \
0x0B-EPROM-LEGACY 0x0D-EEPROM-POLL 0x0E-SRAM-32PIN 0x10-FLASH-INTEL 0x27-SRAM-24PIN \
0x28-SRAM-STD 0x29-SRAM-512K-1M 0x34-EEPROM-X88C64"
forbidden="0x35 0x39 0x11 0x2A 0x2B 0x2C"

# 1. README exists
[ -f "$DS/README.md" ] || { echo "FAIL: missing $DS/README.md"; fail=1; }

# 2. every expected bucket folder exists with >=1 non-empty PDF whose first 4 bytes are %PDF
for b in $expected_buckets; do
  d="$DS/$b"
  [ -d "$d" ] || { echo "FAIL: missing bucket dir $d"; fail=1; continue; }
  n=$(find "$d" -maxdepth 1 -name '*.pdf' -size +1k | wc -l)
  [ "$n" -ge 1 ] || { echo "FAIL: $d has no non-trivial PDF"; fail=1; }
  for f in "$d"/*.pdf; do
    [ -e "$f" ] || continue
    head -c4 "$f" | grep -q '%PDF' || { echo "FAIL: $f is not a real PDF (no %PDF magic)"; fail=1; }
  done
done

# 3. no folder for phantom/infeasible buckets
for b in $forbidden; do
  if compgen -G "$DS/${b}-*" >/dev/null || [ -d "$DS/$b" ]; then
    echo "FAIL: forbidden bucket folder for $b exists"; fail=1
  fi
  grep -q "$b" "$DS/README.md" || { echo "FAIL: README does not mention exclusion $b"; fail=1; }
done

# 4. every PDF filename referenced in README maps to a real file
grep -oE '[A-Za-z0-9_.-]+\.pdf' "$DS/README.md" | sort -u | while read -r ref; do
  find "$DS" -name "$ref" | grep -q . || echo "WARN: README references $ref but no such file found"
done

[ "$fail" -eq 0 ] && echo "datasheets-check: PASS" || { echo "datasheets-check: FAIL"; exit 1; }
```

**Sampling rate:** single structural check; run once at phase gate (and once per download wave if executors download in batches). No `pio`/`pytest` involvement — this phase touches no code, so the existing native/host suites are not exercised (SAFE-05 explicitly says the harness is not used here).

### Wave 0 Gaps
- [ ] `datasheets-check.sh` — authored fresh (no existing equivalent); covers DSHEET-01/02/03 + SAFE-05.
- [ ] No framework install needed (`bash`, `find`, `grep`, `head` all present).

## Security Domain

`security_enforcement` is absent from config (= enabled by default), but this phase is **doc/asset-only with zero code, zero input parsing, zero network-facing surface in the product**. No ASVS category applies to committing static PDFs. The only security-adjacent considerations:
- **Supply-chain / file integrity:** downloaded PDFs could be malicious or HTML-masquerading-as-PDF. Mitigation = the `%PDF` magic-byte + mime check in the validation script; prefer manufacturer/bitsavers/archive.org primaries over random aggregators (done in the URL table).
- **No secrets, no auth, no PII** involved.

No STRIDE threats are introduced by this phase. (Planner: this section can be recorded as "N/A — static-asset phase, no executable surface.")

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` and `firestarter/CLAUDE.md`:
- **Sub-repo boundary:** `datasheets/` lands in the **`firestarter` sub-repo** (firmware repo), on branch `v1.16-protocol-first-architecture-rebuild`. The meta-repo tracks only `.planning/` and `.claude/` — do NOT put `datasheets/` in the meta-repo. (executors commit INSIDE the submodule — see memory `project_v18_phase_execution_mechanics`).
- **No code/DB sync triggers:** this phase touches no `serial_comm.py`/`firestarter.cpp`, no `constants.py`/`firestarter.h`, no `chip_database.json` — so the lockstep/parity rules in CLAUDE.md do not fire (SAFE-05; firmware-only milestone, host untouched).
- **Handler/name source of truth:** `firestarter/CLAUDE.md` §"Algorithm Handlers" table is authoritative for the README hex↔name↔handler columns (more current than research/PROTOCOLS.md).

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DSHEET-01 | Committed datasheet PDF for each of the 11 on-hand ICs under `datasheets/` | On-hand URL table — all 11 have a verified or fetch-time-fallback PDF; bucket placement verified against live DB (W27E512→0x07, FM1608→0x28) |
| DSHEET-02 | Every no-silicon bucket (0x0D,0x0E,0x10,0x27,0x29,0x34) has ≥1 representative datasheet | No-silicon URL table — 6 D-06 exemplars chosen (all are DB members of their protocol_id), each with a verified PDF source |
| DSHEET-03 | `datasheets/README.md` indexes hex↔name↔handler↔file↔status + provenance; names phantom/infeasible exclusions | README index shape section + Exclusions list (0x35/0x39 phantom, 0x11/0x2A/0x2B/0x2C infeasible) + D-08 provenance columns |
| SAFE-05 | No new third-party dep; only new artifact is `datasheets/` | No-stack confirmation; validation script asserts `git diff` touches only `datasheets/**`; existing harness not exercised |
</phase_requirements>

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Claude fetches everything autonomously (network egress confirmed; curl of archive.org PDFs works). Sources: bitsavers, alldatasheet, archive.org, manufacturer/RS-Online. No operator hand-off for the common case.
- **D-02:** Where an exact datasheet is unobtainable, Claude substitutes a compatible/second-source part rather than asking — but every substitution is flagged explicitly in README (D-07). Likely substitution candidates were: 2516, FM1608, AM27C020, X88C64. *(Research outcome: none of these actually needed substituting — all four have exact verified sources.)*
- **D-03:** If a datasheet is truly unobtainable, record it as `MISSING`/`UNSOURCED` in README with what was tried, and let the phase complete. *(Research outcome: no row requires this — keep the policy documented anyway.)*
- **D-04:** Folder tree keyed per protocol bucket (~12 folders), format `datasheets/<hex>-<NAME>/`. Shared buckets hold multiple chip PDFs in one folder. Mirrors firmware dispatch axis 1:1.
- **D-05:** `<NAME>` uses the proposed names already in research/SUMMARY.md (EPROM-STD, FLASH-AMD-STD, FLASH-AMD-ALT, SRAM-STD, EEPROM-POLL, FLASH-INTEL, EEPROM-X88C64, …). Phase 86 holds canonical-naming authority.
- **D-06:** For the 6 no-silicon buckets, pick the best-documented exemplar of the bucket's algorithm. Goal is a clean verification source, not a purchase plan. Prefer an actual chip_database.json member of that protocol_id as a soft tie-breaker.
- **D-07:** README marks any non-exact match as `representative`/`substitute`, naming the actual part filed and the original it stands in for.
- **D-08:** Per-datasheet provenance = source URL + retrieval date + substitute flag, on top of the DSHEET-03 index columns (hex↔name↔handler↔filename↔on-hand status).

### Claude's Discretion
- Folder keying (D-04) and provenance depth (D-08) were explicit "you decide" — resolved as per-bucket folders + URL+date+substitute-flag provenance.
- A planner/executor may refine the exact README column layout and PDF filename convention (`<PART>.pdf` vs `<PART>-<rev>.pdf`) as long as the index stays hex→name→handler→file→status + URL/date/substitute-flag.

### Deferred Ideas (OUT OF SCOPE)
- Canonical protocol naming → Phase 86 (Phase 85 uses research-proposed names provisionally).
- DB decode corrections (FM1608 0x40→0x28 doc reconciliation, 0x34 UV-EPROM→EEPROM) → Phase 86. *(Note: the DB `algorithm` value for FM1608 is already 0x28; the doc/memory reconciliation is Phase 86.)*
- Bench validation of any protocol → Phase 89 (PROTOCOL-LEDGER).
- "Parts I'd actually acquire" representative bias → not chosen (D-06 picks best-documented exemplars instead).
</user_constraints>

## Sources

### Primary (HIGH confidence — curl-verified 200/PDF this session)
- bitsavers.org/components/winbond/ — W27C512, W29C020 (primary vendor scans; directory listing read directly)
- bitsavers.org/components/xicor/1990_Xicor_Data_Book.pdf — X88C64
- ww1.microchip.com — SST39SF040 (official), AT28C256 (doc0006)
- www.farnell.com/datasheets/82469.pdf — FM1608 (Ramtron)
- web.stanford.edu + www.dcddcc.com — AM27C020 (AMD Rev F / Rev H)
- archive.org/download/2516_EPROM/ + downloads.reactivemicro.com — 2516
- media.digikey.com CDN — ST M27C512, W27C512
- datasheet.octopart.com CDN — W29C040, SST27SF256 (family)
- www.ardent-tool.com — Intel 28F010
- www.futurlec.com — DS1245Y
- princeton.edu + silicon-ark.co.uk — 6116
- Live repo: `firestarter_app/firestarter/data/chip_database.json` (bucket membership, all 744 chips; W27E512→0x07, W27E040→0x08, FM1608→0x28(40), X88C64→0x34, 2516 absent — all verified via python this session)
- `firestarter/CLAUDE.md` §Algorithm Handlers + §Protocol Dispatch (handler-file names, phantom/infeasible classification)

### Secondary (MEDIUM — referenced, fetch-time-verify)
- alldatasheet.com leaves for W27E040, SST27SF512 (exact parts; aggregator hosts — verify the actual download at fetch time)
- analog.com DS1250Y (official but curl-blocked 000 — needs a mirror or browser fetch)

### Tertiary (LOW — bot-walled, do not script)
- docs.rs-online.com (403), jameco.com (403)

## Metadata

**Confidence breakdown:**
- URL sourcing: HIGH — 15 of 17 PDFs curl-verified 200/application/pdf this session; the 2 fetch-time-fallback parts (W27E040, SST27SF512) have working family/sibling sources plus aggregator leaves.
- Bucket membership: HIGH — verified directly against the committed 744-chip DB (W27E512=0x07 correction, FM1608=0x28, X88C64=0x34 sole member, 2516 absent).
- Folder/name/handler map: HIGH — cross-confirmed SUMMARY proposed names against firestarter/CLAUDE.md handler table.
- Exclusions (phantom/infeasible): HIGH — from firestarter/CLAUDE.md dispatch table + REQUIREMENTS out-of-scope.

**Research date:** 2026-06-25
**Valid until:** ~2026-07-25 (URLs to durable archives — bitsavers/archive.org/manufacturer — are stable; aggregator fallbacks rot faster. Once PDFs are committed, source validity is moot.)
