---
status: complete
phase: 85-datasheet-acquisition
source: [85-VERIFICATION.md]
started: 2026-06-25T16:00:00Z
updated: 2026-08-09
---

## Current Test

[complete — both tests performed 2026-08-09 by reading the PDFs out of git]

## Tests

### 1. PDF Content Identity Spot-Check
expected: Each opened PDF shows a title page / first page identifying the chip matching its README row; substitute/representative flags are honest. Suggested candidates: `0x08-EPROM-QUICK/W27E040.pdf` (family-substitute — confirm it is a Winbond EPROM family doc, not an unrelated PDF) and `0x29-SRAM-512K-1M/DS1245Y.pdf` (substitute for DS1250Y — confirm it is a Dallas DS1245Y NVRAM datasheet). Note: `0x08-EPROM-QUICK/W27C020.pdf` is already content-verified (pypdf extraction) and is exempt.
result: PASS (2026-08-09)

### 2. No-Silicon Exemplar Quality Review
expected: Operator confirms the 6 no-silicon representatives (AT28C256/0x0D, DS1245Y/0x0E, Intel-28F010/0x10, 6116/0x27, DS1245Y-as-DS1250Y-sub/0x29, X88C64 data-book/0x34) are adequate algorithm references for their buckets, and the D-06 "best-documented exemplar" rationale holds.
result: PASS (2026-08-09)

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps

---

## Results — 2026-08-09

Performed during the v1.31 pre-close carry-over sweep. Full evidence table in
`85-VERIFICATION.md` § "Re-Verification 2026-08-09".

### Test 1 — PDF Content Identity Spot-Check: **PASS**

Six PDFs opened and read (page 1 each) — both substitutes this test specifically named,
plus four exact-leaf files. 6/6 title pages identify the part their README row claims.

- `0x08-EPROM-QUICK/W27E040.pdf` — **confirmed a Winbond EPROM family doc**, exactly as
  the `family-substitute` flag declares. Not an unrelated PDF. It is the Winbond
  **W27C512** family document (Nov 1999 Rev A4).
- `0x29-SRAM-512K-1M/DS1245Y.pdf` — **confirmed a Dallas Semiconductor DS1245Y/AB
  "1024k Nonvolatile SRAM" datasheet**, as declared for the DS1250Y substitution.
- Exact-leaf spot checks: `W27C512.pdf` (Winbond W27C512, Nov 1999 Rev A4 — matches the
  `…199911…` provenance URL), `ST-M27C512.pdf` (ST M27C512 UV/OTP EPROM, May 2007 Rev 3),
  `AM27C020.pdf` (AMD Am27C020, Pub 11507 **Rev F** — matches the "Rev F" provenance
  claim), `2516_EPROM.pdf` (TI TMS 2516, Dec 1979 rev May 1982).

Substitute flags are honest — neither substitute pretends to be the exact leaf.

**One limitation found and recorded (not a failure):** `W27E040.pdf` is the *same git
blob* as `0x07-EPROM-STD/W27C512.pdf` (`1a1c2800…`). The README declares the
substitution, so nothing is misrepresented, but the `0x08` bucket therefore holds no
W27E040-specific programming timing. Carried to
`.planning/v1.31-CARRYOVER-DISPOSITION.md` because v1.31 needs per-datasheet `0x08`
pulse evidence.

### Test 2 — No-Silicon Exemplar Quality Review: **PASS**

All six picks are canonical, well-documented exemplars of their bucket's algorithm —
AT28C256 (0x0D DQ7-polling EEPROM), DS1245Y (0x0E 32-pin NVRAM), Intel-28F010 (0x10
command-register flash), 6116 (0x27 canonical 2Kx8 24-pin SRAM), DS1245Y-as-DS1250Y
(0x29, same NVRAM family one size class up), X88C64 data book (0x34, the actual part).
D-06 "best-documented exemplar" holds for all six.

This is the technical-adequacy half of the question; the editorial preference remains
operator-overridable if a better exemplar is wanted for any bucket.

_Tested: 2026-08-09 · PDFs read from `v1.16-protocol-first-architecture-rebuild` via `git show` — no branch modified_
