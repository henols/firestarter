# Phase 85: Datasheet Acquisition - Context

**Gathered:** 2026-06-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Acquire and commit a datasheet PDF for every protocol Firestarter dispatches —
the **11 on-hand chip families** (spanning 6 protocol buckets) plus **one
representative per no-silicon bucket** (6 buckets) — under a new top-level
`datasheets/` folder, and author `datasheets/README.md` indexing every folder.
The datasheets are the **verification + rationale source** the Phase 86 naming
pass and future bench sessions will cite.

**Zero code risk.** The only new artifact is the `datasheets/` tree (SAFE-05).
No firmware/host code changes, no DB changes (the FM1608 0x40→0x28 and 0x34
type corrections belong to Phase 86, not here), no new third-party deps.

**In scope:** fetching PDFs, organizing the folder tree, writing the index.
**Out of scope:** authoring canonical protocol names (Phase 86), any code,
any `chip_database.json` change, bench validation (Phase 89).

</domain>

<decisions>
## Implementation Decisions

### Sourcing method
- **D-01:** Claude fetches **everything** autonomously (network egress confirmed
  in the devcontainer — `curl` of binary PDFs from archive.org works). Sources to
  try: bitsavers, alldatasheet, archive.org, manufacturer/RS-Online, per the
  candidates already named in `research/SUMMARY.md`. No operator hand-off for the
  common case.
- **D-02:** Where an **exact** datasheet is unobtainable, Claude substitutes a
  compatible / second-source part rather than asking — but **every substitution is
  flagged explicitly** in README (see D-07). Likely substitution candidates:
  2516, FM1608, AM27C020, X88C64 (discontinued / generic NMOS).
- **D-03:** If a datasheet is **truly unobtainable** (no exact part and no usable
  substitute), record it as a `MISSING`/`UNSOURCED` row in README with what was
  tried, and **let the phase complete** — a single documented gap does not block
  the naming pass for the rest. An honest documented gap beats a fake file.

### Folder structure
- **D-04:** Folder tree is keyed **per protocol bucket** (~12 folders: 6 on-hand +
  6 no-silicon), format `datasheets/<hex>-<NAME>/`. Shared buckets hold **multiple
  chip PDFs** inside one folder (e.g. `0x07-EPROM-STD/` → W27C512.pdf,
  SST27SF512.pdf, ST-M27C512.pdf). This mirrors the firmware dispatch axis 1:1, so
  the folder tree matches the Phase 86 vocabulary and the Phase 89 ledger.
  *(User said "you decide" on per-bucket vs per-chip; Claude chose per-bucket as the
  format the success criteria already imply.)*
- **D-05:** `<NAME>` uses the **proposed names already in `research/SUMMARY.md`**
  (EPROM-STD, FLASH-AMD-STD, FLASH-AMD-ALT, SRAM-STD, EEPROM-POLL, FLASH-INTEL,
  EEPROM-X88C64, …). Phase 86 holds canonical-naming authority — if it ratifies a
  different name, a folder rename is trivial. Avoids running the naming exercise twice.

### Representative selection (no-silicon buckets)
- **D-06:** For the 6 no-silicon buckets (0x0D, 0x0E, 0x10, 0x27, 0x29, 0x34),
  pick the **best-documented exemplar** of the bucket's algorithm — the part whose
  datasheet most clearly documents the write/erase/poll behavior (e.g. 0x34 →
  X88C64, 0x10 → Intel 28F-series). Goal is a clean verification source, **not** a
  purchase plan. Claude picks; operator reviews the picks in README. Prefer an
  actual `chip_database.json` member of that `protocol_id` as a soft tie-breaker
  when one is also well-documented.

### Provenance / README
- **D-07:** README marks any non-exact match as **`representative`/`substitute`**,
  naming the actual part filed and the original it stands in for, so Phase 86 knows
  when it is reading an exact datasheet vs a close cousin (honesty-first, matches the
  milestone's explicit-`UNVERIFIED` ethos).
- **D-08:** Per-datasheet provenance metadata = **source URL + retrieval date +
  substitute flag**, on top of the DSHEET-03 index columns (hex ↔ proposed name ↔
  handler ↔ filename ↔ on-hand status). Enough to re-source / audit without bloating
  17 rows. *(User said "you decide" between minimal / this / full-archival; Claude
  chose the middle URL+date option as it pairs with the explicit-substitution flag.)*

### Claude's Discretion
- **Folder keying (D-04)** and **provenance depth (D-08)** were both explicit
  "you decide" — Claude resolved them as recorded above. A planner/executor may
  refine the exact README column layout and PDF filename convention (e.g.
  `<PART>.pdf` vs `<PART>-<rev>.pdf`) as long as the index stays
  hex→name→handler→file→status + URL/date/substitute-flag.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase / milestone definition
- `.planning/ROADMAP.md` — Phase 85 detail (§"Phase 85: Datasheet Acquisition"):
  goal, the explicit chip + bucket lists, the phantom (0x35/0x39) and infeasible
  (0x11/0x2A/0x2B/0x2C) exclusions, success criteria.
- `.planning/REQUIREMENTS.md` — DSHEET-01, DSHEET-02, DSHEET-03, SAFE-05 (the four
  requirements this phase satisfies).

### Protocol bucket map + sourcing candidates (most important for this phase)
- `.planning/research/SUMMARY.md` — authoritative 12-bucket table (hex → proposed
  name → handler → on-hand chips → status), the FM1608 **0x40→0x28** correction
  rationale, and named datasheet sources (bitsavers / alldatasheet / RS-Online /
  archive.org). **This is the single best grounding doc — read it first.**
- `.planning/research/PROTOCOLS.md` — fuller per-protocol algorithm detail when
  the SUMMARY row is not enough to pick the best-documented exemplar.
- `.planning/seeds/protocol-first-architecture-rebuild.md` — locked milestone
  decisions (#1 minipro DB stays ground truth, #2 datasheets = verification layer,
  Leonardo+Rev2.0 bench combo).

### Ground-truth DB (for representative selection D-06)
- `firestarter_app/firestarter/data/chip_database.json` — the live `protocol_id`
  membership; use to find an actual member of each no-silicon bucket as the
  tie-breaker exemplar.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- No code is written or reused in this phase — it produces only `datasheets/` + its
  README. SAFE-05 forbids new third-party deps; existing harness
  (`check_dispatch.py`, `diff_db.py`, native `test_val_*`) is **not** exercised here
  (it becomes relevant from Phase 86 onward).

### Established Patterns
- `.planning/` already holds planning-time reference docs; `datasheets/` is a new
  **top-level repo folder** (not under `.planning/`), committed to the `firestarter`
  sub-repo on branch `v1.16-protocol-first-architecture-rebuild`.

### Integration Points
- Folder tree (D-04) is the structural contract Phase 86's vocabulary doc and Phase
  89's `PROTOCOL-LEDGER` both key off — keep the `<hex>-<NAME>` folder ↔ bucket
  correspondence exact.

</code_context>

<specifics>
## Specific Ideas

- Bucket map to realize (from `research/SUMMARY.md`):
  - **On-hand (6 buckets, 11 chips):** `0x05-FLASH-AMD-STD` (W29C020, W29C040) ·
    `0x06-FLASH-AMD-ALT` (SST39SF040) · `0x07-EPROM-STD` (W27C512, SST27SF512,
    ST M27C512) · `0x08-EPROM-QUICK` (W27E040, AM27C020) · `0x0B-EPROM-LEGACY`
    (2516) · `0x28-SRAM-STD` (FM1608/FRAM). *(W27E512 is also on-hand — confirm its
    bucket; likely 0x07 or 0x08 — researcher to verify against the DB.)*
  - **No-silicon (6 buckets, 1 rep each):** `0x0D-EEPROM-POLL`, `0x0E-SRAM-32PIN`,
    `0x10-FLASH-INTEL`, `0x27-SRAM-24PIN`, `0x29-SRAM-512K-1M`, `0x34-EEPROM-X88C64`.
- README must explicitly name the **phantom (0x35/0x39)** and **infeasible
  (0x11/0x2A/0x2B/0x2C)** buckets as non-protocols / exclusions (DSHEET-03).
- 11 on-hand chips per ROADMAP SC#1: W27C512, W27E512, SST27SF512, W27E040,
  SST39SF040, W29C020, W29C040, FM1608, ST M27C512, AM27C020, 2516.

</specifics>

<deferred>
## Deferred Ideas

- **Canonical protocol naming** — ratifying / finalizing the human names is Phase 86,
  not here. Phase 85 uses the research-proposed names provisionally (D-05).
- **DB decode corrections** (FM1608 0x40→0x28, 0x34 UV-EPROM→EEPROM) — Phase 86.
- **Bench validation of any protocol** — Phase 89 (`PROTOCOL-LEDGER`).
- "Parts I'd actually acquire" representative bias — considered and **not** chosen
  (D-06 picks best-documented exemplars instead); revisit only if a future milestone
  scopes acquiring no-silicon parts for bench.

None of these belong in Phase 85.

</deferred>

---

*Phase: 85-datasheet-acquisition*
*Context gathered: 2026-06-25*
