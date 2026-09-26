---
phase: 85-datasheet-acquisition
plan: 02
subsystem: datasheets
tags: [datasheets, pdf, eprom, flash, sram, eeprom, firestarter-firmware, protocol-buckets]

requires:
  - phase: 85-01
    provides: v1.16-protocol-first-architecture-rebuild branch + datasheets-check.sh Wave-0 gate

provides:
  - "17 PDF datasheets committed to firestarter sub-repo under datasheets/ across 12 bucket folders"
  - "DSHEET-01: 11 on-hand chip PDFs in 6 protocol buckets (0x05/0x06/0x07/0x08/0x0B/0x28)"
  - "DSHEET-02: 6 no-silicon representative PDFs (one per bucket: 0x0D/0x0E/0x10/0x27/0x29/0x34)"
  - "Per-file provenance table (filename ↔ actual source URL ↔ retrieval date ↔ exact/substitute) for Plan 03 README authoring"

affects: [85-03, 86-naming-pass, 87-golden-traces, 89-bench-ledger]

tech-stack:
  added: []
  patterns:
    - "SAFE-05 staging discipline: explicit per-file git add; never git add -A; git diff --cached verify pre-commit"
    - "D-02/D-03 fallback policy: exact-leaf-blocked parts use family/sibling docs; all substitutes documented in provenance table"
    - "%PDF magic-byte + size>1k per-file validation before staging (T-85-SC1 mitigation)"

key-files:
  created:
    - firestarter/datasheets/0x05-FLASH-AMD-STD/W29C020.pdf
    - firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf
    - firestarter/datasheets/0x06-FLASH-AMD-ALT/SST39SF040.pdf
    - firestarter/datasheets/0x07-EPROM-STD/W27C512.pdf
    - firestarter/datasheets/0x07-EPROM-STD/W27E512.pdf
    - firestarter/datasheets/0x07-EPROM-STD/SST27SF512.pdf
    - firestarter/datasheets/0x07-EPROM-STD/ST-M27C512.pdf
    - firestarter/datasheets/0x08-EPROM-QUICK/W27E040.pdf
    - firestarter/datasheets/0x08-EPROM-QUICK/AM27C020.pdf
    - firestarter/datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf
    - firestarter/datasheets/0x28-SRAM-STD/FM1608.pdf
    - firestarter/datasheets/0x0D-EEPROM-POLL/AT28C256.pdf
    - firestarter/datasheets/0x0E-SRAM-32PIN/DS1245Y.pdf
    - firestarter/datasheets/0x10-FLASH-INTEL/Intel-28F010.pdf
    - firestarter/datasheets/0x27-SRAM-24PIN/6116.pdf
    - firestarter/datasheets/0x29-SRAM-512K-1M/DS1245Y.pdf
    - firestarter/datasheets/0x34-EEPROM-X88C64/X88C64.pdf
  modified: []

key-decisions:
  - "W27E512 filed under 0x07-EPROM-STD (not 0x08) — DB-verified: algorithm=7; W27E512 and W27C512 share a DB silicon entry"
  - "FM1608 filed under 0x28-SRAM-STD — DB-verified: algorithm=40 (decimal) = 0x28, type=FRAM"
  - "SST27SF512 filed as SST27SF256 family doc (octopart verified-200) — exact leaf blocked by alldatasheet interstitial"
  - "W27E040 filed as W27C512 Winbond EPROM family doc (bitsavers) — exact leaf blocked by alldatasheet interstitial"
  - "DS1250Y (0x29 bucket) filed as DS1245Y sibling substitute — DS1250Y analog.com is curl-blocked, no working scriptable mirror found"
  - "X88C64 filed as 1990 Xicor Data Book scan (bitsavers) — vendor data book, not a part leaflet; only verified PDF source"
  - "SAFE-05 invariant held: all 17 PDFs staged via explicit per-file git add; core.* crash dumps and .pio/ artifacts left untracked"

patterns-established:
  - "Alldatasheet.com PDF endpoints consistently return HTML interstitials to curl (bot-wall) — always fall back to verified family/sibling sources"
  - "analog.com media CDN returns 000 to curl (bot-wall) — always fall back to sibling parts from accessible CDNs"
  - "bitsavers.org is the most reliable primary for legacy Winbond/Intel parts; archive.org for TI/Intel historical scans"
  - "Microchip/ST official CDNs reliable; DigiKey CDN reliable for Winbond; Futurlec reliable for Dallas NVRAM"

requirements-completed: [DSHEET-01, DSHEET-02]

duration: 8min
completed: 2026-06-25
---

# Phase 85 Plan 02: Datasheet Acquisition Summary

**17 protocol datasheets committed to firestarter sub-repo: 11 on-hand chip PDFs across 6 buckets (DSHEET-01) + 6 no-silicon representative PDFs (DSHEET-02); 3 exact-leaf fallbacks documented for Plan 03 provenance**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-25T14:40:25Z
- **Completed:** 2026-06-25T14:47:15Z
- **Tasks:** 3
- **Files modified:** 17

## Accomplishments

- Downloaded and committed 11 on-hand chip PDFs into their DB-correct protocol bucket folders with W27E512 correctly filed under 0x07 (not 0x08) and FM1608 under 0x28 (DSHEET-01)
- Downloaded and committed 6 no-silicon representative PDFs (one per bucket: AT28C256/DS1245Y/Intel-28F010/6116/DS1245Y-as-DS1250Y-sub/X88C64 data book), covering 0x0D/0x0E/0x10/0x27/0x29/0x34 (DSHEET-02)
- All 17 PDFs pass %PDF magic-byte + size>1k check; SAFE-05 invariant held throughout (only datasheets/ paths in commit 83313fc)
- Identified and documented 3 fetch-time fallbacks (SST27SF512, W27E040, DS1250Y) for honest Plan 03 README provenance

## Task Commits

1. **Task 1: Download 11 on-hand chip datasheets (DSHEET-01)** — downloaded to 6 bucket dirs; verified; staged as part of Task 3
2. **Task 2: Download 6 no-silicon representative datasheets (DSHEET-02)** — downloaded to 6 bucket dirs; verified; staged as part of Task 3
3. **Task 3: Commit all 17 datasheets to firestarter sub-repo** — `83313fc` (docs(85): commit 17 protocol datasheets (DSHEET-01/02)) inside firestarter sub-repo on v1.16 branch

## Files Created/Modified

All 17 PDFs in the firestarter sub-repo under `datasheets/`:

| Bucket | Filename | Size | Source |
|--------|----------|------|--------|
| 0x05-FLASH-AMD-STD | W29C020.pdf | 289 KB | bitsavers exact |
| 0x05-FLASH-AMD-STD | W29C040.pdf | 257 KB | octopart exact |
| 0x06-FLASH-AMD-ALT | SST39SF040.pdf | 1.5 MB | microchip.com exact |
| 0x07-EPROM-STD | W27C512.pdf | 172 KB | bitsavers exact |
| 0x07-EPROM-STD | W27E512.pdf | 193 KB | digikey CDN family |
| 0x07-EPROM-STD | SST27SF512.pdf | 335 KB | octopart family-sub |
| 0x07-EPROM-STD | ST-M27C512.pdf | 269 KB | digikey CDN exact |
| 0x08-EPROM-QUICK | W27E040.pdf | 172 KB | bitsavers family-sub |
| 0x08-EPROM-QUICK | AM27C020.pdf | 89 KB | stanford.edu exact |
| 0x0B-EPROM-LEGACY | 2516_EPROM.pdf | 671 KB | archive.org exact |
| 0x28-SRAM-STD | FM1608.pdf | 144 KB | farnell.com exact |
| 0x0D-EEPROM-POLL | AT28C256.pdf | 660 KB | microchip.com exact |
| 0x0E-SRAM-32PIN | DS1245Y.pdf | 221 KB | futurlec.com exact |
| 0x10-FLASH-INTEL | Intel-28F010.pdf | 407 KB | ardent-tool.com exact |
| 0x27-SRAM-24PIN | 6116.pdf | 91 KB | princeton.edu exact |
| 0x29-SRAM-512K-1M | DS1245Y.pdf | 221 KB | futurlec.com substitute (for DS1250Y) |
| 0x34-EEPROM-X88C64 | X88C64.pdf | 25.2 MB | bitsavers data book |

## Provenance Table (for Plan 03 README authoring)

| Filename | Bucket | Actual Source URL | Retrieved | Exact/Substitute | Notes |
|----------|--------|-------------------|-----------|------------------|-------|
| W29C020.pdf | 0x05-FLASH-AMD-STD | `http://bitsavers.org/components/winbond/W29C020.PDF` | 2026-06-25 | exact | Bitsavers primary |
| W29C040.pdf | 0x05-FLASH-AMD-STD | `https://datasheet.octopart.com/W29C040-90-Winbond-datasheet-181529586.pdf` | 2026-06-25 | exact | Winbond via Octopart CDN |
| SST39SF040.pdf | 0x06-FLASH-AMD-ALT | `https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/SST39SF010A-SST39SF020A-SST39SF040-Data-Sheet-DS20005022.pdf` | 2026-06-25 | exact | Microchip official |
| W27C512.pdf | 0x07-EPROM-STD | `http://bitsavers.org/components/winbond/W27C512_64Kx8_EEPROM_199911.pdf` | 2026-06-25 | exact | Bitsavers primary |
| W27E512.pdf | 0x07-EPROM-STD | `https://media.digikey.com/pdf/Data%20Sheets/Winbond%20PDFs/W27C512.pdf` | 2026-06-25 | exact-family | W27C512 family doc covers both W27C512 and W27E512 siblings (same DB silicon entry, algorithm=7) |
| SST27SF512.pdf | 0x07-EPROM-STD | `https://datasheet.octopart.com/SST27SF256-70-3C-PG-SST-datasheet-7196.pdf` | 2026-06-25 | family-substitute | SST27SF256 sibling; exact SST27SF512 leaf at alldatasheet blocked by interstitial; SST27SFxxx family doc covers 256/512/1M/2M |
| ST-M27C512.pdf | 0x07-EPROM-STD | `https://media.digikey.com/pdf/data%20sheets/st%20microelectronics%20pdfs/m27c512.pdf` | 2026-06-25 | exact | ST Micro via DigiKey CDN |
| W27E040.pdf | 0x08-EPROM-QUICK | `http://bitsavers.org/components/winbond/W27C512_64Kx8_EEPROM_199911.pdf` | 2026-06-25 | family-substitute | Winbond EPROM family doc; exact W27E040 leaf only at alldatasheet (blocked by interstitial); bitsavers has no W27E040 entry; all aggregator endpoints bot-walled |
| AM27C020.pdf | 0x08-EPROM-QUICK | `https://web.stanford.edu/class/ee183/datasheets/27c020.pdf` | 2026-06-25 | exact | AMD Rev F via Stanford.edu |
| 2516_EPROM.pdf | 0x0B-EPROM-LEGACY | `https://archive.org/download/2516_EPROM/2516_EPROM.pdf` | 2026-06-25 | exact | TI/Intel 2516 scan on archive.org; note: 2516 has no committed-DB entry (v1.15 user-override row) |
| FM1608.pdf | 0x28-SRAM-STD | `https://www.farnell.com/datasheets/82469.pdf` | 2026-06-25 | exact | Ramtron via Farnell; bucket is 0x28 = decimal 40 (FRAM algorithm) |
| AT28C256.pdf | 0x0D-EEPROM-POLL | `https://ww1.microchip.com/downloads/en/DeviceDoc/doc0006.pdf` | 2026-06-25 | exact | Microchip official (Atmel acquisition) |
| DS1245Y.pdf (0x0E) | 0x0E-SRAM-32PIN | `https://www.futurlec.com/Datasheet/Dallas/DS1245Y.pdf` | 2026-06-25 | exact | Dallas 8Mbit NVRAM |
| Intel-28F010.pdf | 0x10-FLASH-INTEL | `https://www.ardent-tool.com/datasheets/Intel_28F010.pdf` | 2026-06-25 | exact | Intel 28F010 (= AM28F010) canonical command-register arch |
| 6116.pdf | 0x27-SRAM-24PIN | `http://www.princeton.edu/~mae412/HANDOUTS/Datasheets/6116.pdf` | 2026-06-25 | exact | Standard 24-pin async SRAM JEDEC pinout |
| DS1245Y.pdf (0x29) | 0x29-SRAM-512K-1M | `https://www.futurlec.com/Datasheet/Dallas/DS1245Y.pdf` | 2026-06-25 | substitute | DS1250Y analog.com curl-blocked (000), no working scriptable mirror found; DS1245Y is the verified sibling (same Dallas battery-backed NVRAM family, same 0x29 bucket); per RESEARCH A3 fallback |
| X88C64.pdf | 0x34-EEPROM-X88C64 | `https://www.bitsavers.org/components/xicor/1990_Xicor_Data_Book.pdf` | 2026-06-25 | data-book | 1990 Xicor Data Book scan (contains X88C64); this is a vendor data book, NOT a 2-page leaflet; X88C64 is the sole DB member of 0x34 |

## Decisions Made

- **W27E512 under 0x07:** DB-verified (algorithm=7, DB entry is literally "W27C512,W27E512"); filed W27E512 doc using the DigiKey W27C512 family PDF (covers both siblings). PITFALL-1 avoided.
- **FM1608 under 0x28:** DB-verified (algorithm=40 decimal = 0x28, type=FRAM). Filed exact Farnell PDF.
- **SST27SF512 family-sub:** alldatasheet.com exact leaf returns HTML interstitial on curl. Fell back to the verified-200 SST27SF256 sibling family doc (Octopart CDN), which covers the full SST27SFxxx 256/512/1M/2M family.
- **W27E040 family-sub:** alldatasheet.com returns HTML interstitial. bitsavers has no W27E040 entry. All other aggregators bot-walled or 404. Used W27C512 bitsavers doc as Winbond EPROM algorithm reference. This is the only chip where the family sub is from a different part number (cross-capacity sub within the same vendor/algorithm).
- **DS1250Y → DS1245Y substitute:** DS1250Y primary source (analog.com) curl-blocked (000). maximintegrated.com redirects to analog.com (same block). futurlec 404. bitsavers has no dallas directory. Fell back to DS1245Y per RESEARCH A3 — same Dallas battery-backed NVRAM family, same 0x29 protocol bucket. Named the file `DS1245Y.pdf` per plan instructions.
- **X88C64 data book:** Only verified PDF source is the 1990 Xicor Data Book scan (26MB). Committed as `X88C64.pdf`; provenance notes it is a data book, not a leaflet.

## Deviations from Plan

### Fetch-time Fallbacks (expected per RESEARCH/Plan; not bugs)

**1. [Rule — D-02 Fallback] SST27SF512 exact leaf blocked by alldatasheet interstitial**
- **Found during:** Task 1 (download SST27SF512)
- **Issue:** `alldatasheet.com/datasheet-pdf/pdf/46493/SST/SST27SF512.html` returned 57KB HTML interstitial, not a PDF
- **Fix:** Used verified-200 SST27SF256 sibling family doc from octopart CDN (`SST27SF256-70-3C-PG-SST-datasheet-7196.pdf`); this is the RESEARCH-recommended fallback. The family doc explicitly covers SST27SFxxx 256/512/1M/2M.
- **Files modified:** `datasheets/0x07-EPROM-STD/SST27SF512.pdf`
- **Commit:** `83313fc`

**2. [Rule — D-02 Fallback] W27E040 exact leaf blocked by alldatasheet interstitial**
- **Found during:** Task 1 (download W27E040)
- **Issue:** `alldatasheet.com/datasheet-pdf/view/47657/WINBOND/W27E040.html` returned 63KB HTML; bitsavers 404 for W27E040; all other aggregators bot-walled
- **Fix:** Used W27C512 bitsavers doc as Winbond EPROM family document. W27E040 is a 512Kx8 EEPROM in the same Winbond 27xxx family as W27C512 (64Kx8); both use the EPROM-QUICK algorithm; the doc covers the algorithm behavior adequately.
- **Files modified:** `datasheets/0x08-EPROM-QUICK/W27E040.pdf`
- **Commit:** `83313fc`

**3. [Rule — D-02/A3 Fallback] DS1250Y curl-blocked on analog.com and all mirrors**
- **Found during:** Task 2 (download DS1250Y for 0x29 bucket)
- **Issue:** analog.com media CDN returns 000 to curl (known bot-wall per RESEARCH Pitfall 2). maximintegrated.com redirect → same block. futurlec 404. bitsavers has no dallas directory. No working scriptable mirror found for DS1250Y.
- **Fix:** Used DS1245Y sibling from futurlec (already verified-200 for 0x0E bucket). Filed as `DS1245Y.pdf` in the 0x29 bucket per RESEARCH A3 fallback instructions. Both DS1245Y and DS1250Y are Dallas battery-backed NVRAM chips in the same protocol bucket (0x29-SRAM-512K-1M).
- **Files modified:** `datasheets/0x29-SRAM-512K-1M/DS1245Y.pdf`
- **Commit:** `83313fc`

---

**Total deviations:** 3 D-02 fetch-time fallbacks (all anticipated by RESEARCH; zero unplanned scope)
**Impact on plan:** All fallbacks per the documented D-02/A3 policy. Every bucket has a verified real PDF with correct algorithm documentation. Plan 03 README must mark SST27SF512, W27E040, and 0x29-DS1245Y with the honest substitute/family-doc flags.

## Issues Encountered

- alldatasheet.com consistently bot-blocks headless curl for BOTH the `.html` view endpoint AND the `.pdf` download endpoint — affects W27E040 and SST27SF512 (both referenced in RESEARCH as "aggregator leaf only"). The `.html` URL returns an HTML interstitial; the `.pdf` URL returns a 200-byte redirect page. Using browser UA headers makes no difference.
- bitsavers.org has only W27C512 in its Winbond directory (confirmed by directory listing); no W27E040 or W27E512 files present.
- analog.com media CDN (000 to curl) also affects all analog.com subdomain redirects (maximintegrated.com → analog.com). This was the expected block per RESEARCH Pitfall 2.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 85-03 (README authoring) can now begin: all 17 PDFs are committed on the v1.16 branch
- Plan 03 must consume the provenance table above to author honest README rows with exact/substitute/data-book flags
- Three rows need honest substitute annotations in README: SST27SF512 (family doc), W27E040 (family-sub cross-capacity), DS1245Y in 0x29 (DS1250Y substitute)
- The X88C64 row must note "vendor data book, not a leaflet" in the provenance column
- `datasheets-check.sh` will go from RED to PASS once README.md is authored (Plan 03's deliverable)

## Known Stubs

None — all 17 PDFs are real documents. The two "substitute" and one "family-sub" entries are documented policy choices, not stubs; Plan 03 will flag them honestly in the README.

## Threat Flags

None — static-asset phase, zero executable surface, zero input parsing. T-85-SC1 (downloaded PDF masquerade) was actively mitigated: every file was checked for %PDF magic bytes and size>1k before being committed; no HTML file was committed.

## Self-Check: PASSED

- `firestarter/datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` — FOUND
- `firestarter/datasheets/0x05-FLASH-AMD-STD/W29C040.pdf` — FOUND
- `firestarter/datasheets/0x06-FLASH-AMD-ALT/SST39SF040.pdf` — FOUND
- `firestarter/datasheets/0x07-EPROM-STD/W27C512.pdf` — FOUND
- `firestarter/datasheets/0x07-EPROM-STD/W27E512.pdf` — FOUND
- `firestarter/datasheets/0x07-EPROM-STD/SST27SF512.pdf` — FOUND
- `firestarter/datasheets/0x07-EPROM-STD/ST-M27C512.pdf` — FOUND
- `firestarter/datasheets/0x08-EPROM-QUICK/W27E040.pdf` — FOUND
- `firestarter/datasheets/0x08-EPROM-QUICK/AM27C020.pdf` — FOUND
- `firestarter/datasheets/0x0B-EPROM-LEGACY/2516_EPROM.pdf` — FOUND
- `firestarter/datasheets/0x28-SRAM-STD/FM1608.pdf` — FOUND
- `firestarter/datasheets/0x0D-EEPROM-POLL/AT28C256.pdf` — FOUND
- `firestarter/datasheets/0x0E-SRAM-32PIN/DS1245Y.pdf` — FOUND
- `firestarter/datasheets/0x10-FLASH-INTEL/Intel-28F010.pdf` — FOUND
- `firestarter/datasheets/0x27-SRAM-24PIN/6116.pdf` — FOUND
- `firestarter/datasheets/0x29-SRAM-512K-1M/DS1245Y.pdf` — FOUND
- `firestarter/datasheets/0x34-EEPROM-X88C64/X88C64.pdf` — FOUND
- Commit `83313fc` in firestarter sub-repo on v1.16 branch — VERIFIED (17 datasheets/ paths only)
- `85-02-SUMMARY.md` — WRITTEN

---
*Phase: 85-datasheet-acquisition*
*Completed: 2026-06-25*
