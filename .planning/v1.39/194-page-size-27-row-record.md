---
title: Page-size 27-row measurement record — protocol 0x05, milestone v1.39 Phase 194
phase: 194-real-page-size-reaches-the-firmware
plan: "06"
measured: 2026-09-15
status: AUTHORITATIVE — the citable record of PAGE-02's all-27 measurement and of PAGE-03's evidence-class split. Not authoritative for a silicon read-back on any of the 9 previously under-sized parts; see §5.
requirements: [PAGE-01, PAGE-02, PAGE-03 (software half only — hardware leg held OPEN per D-11)]
---

# Page-size 27-row measurement record — Phase 194

Every number below carries the command that produced it and the plan that ran it. Nothing here
is restated from research without either re-attribution to the plan that re-measured it, or an
explicit citation to `194-RESEARCH.md` where a plan measurement does not exist.

---

## 1. The 27-row table

Sort key: manufacturer name ascending, then the part-number alias string ascending
(lexicographic). This reproduces `194-RESEARCH.md` §R1's join-table order exactly, and matches
the per-manufacturer positional-index enumeration `194-04-SUMMARY.md` used for the wire-delta
layer. Real page and old-derivation values are in bytes. Verdict `UNDER 2×` marks the 9 parts
whose old capacity-bracket derivation produced exactly half the part's real page.

| Manufacturer | Part number | Capacity (B) | Real page (B) | Old derived page (B) | Verdict |
|---|---|---|---|---|---|
| ASD | AE29F1008 | 131072 | 128 | 128 | equal |
| ASD | AE29F2008 | 262144 | 128 | 128 | equal |
| ASD | AE29F4008 | 524288 | 256 | 256 | equal |
| ATMEL | AT29BV010A,AT29LV010A | 131072 | 128 | 128 | equal |
| ATMEL | AT29BV020,AT29LV020 | 262144 | 256 | 128 | **UNDER 2×** |
| ATMEL | AT29BV040,AT29LV040 | 524288 | 512 | 256 | **UNDER 2×** |
| ATMEL | AT29BV040A,AT29LV040A | 524288 | 256 | 256 | equal |
| ATMEL | AT29C010A | 131072 | 128 | 128 | equal |
| ATMEL | AT29C020 | 262144 | 256 | 128 | **UNDER 2×** |
| ATMEL | AT29C040 | 524288 | 512 | 256 | **UNDER 2×** |
| ATMEL | AT29C040A | 524288 | 256 | 256 | equal |
| ATMEL | AT29C256 | 32768 | 64 | 64 | equal |
| ATMEL | AT29C257 | 32768 | 64 | 64 | equal |
| ATMEL | AT29C512 | 65536 | 128 | 64 | **UNDER 2×** |
| ATMEL | AT29LV256 | 32768 | 64 | 64 | equal |
| ATMEL | AT29LV512 | 65536 | 128 | 64 | **UNDER 2×** |
| SST | SST29EE010 | 131072 | 128 | 128 | equal |
| SST | SST29EE020 | 262144 | 128 | 128 | equal |
| SST | SST29EE512 | 65536 | 128 | 64 | **UNDER 2×** |
| SST | SST29LE010,SST29VE010 | 131072 | 128 | 128 | equal |
| SST | SST29LE020,SST29VE020 | 262144 | 128 | 128 | equal |
| SST | SST29LE512,SST29VE512 | 65536 | 128 | 64 | **UNDER 2×** |
| WINBOND | W29C010,W29C011,W29C011A,W29EE010,W29EE012 | 131072 | 128 | 128 | equal |
| WINBOND | W29C020,W29C020C,W29C022 | 262144 | 128 | 128 | equal (already correct pre-Phase-194) |
| WINBOND | W29C040,W29C042 | 524288 | 256 | 256 | equal (already correct pre-Phase-194) |
| WINBOND | W29C512,W29EE512 | 65536 | 128 | 64 | **UNDER 2×** |
| WINBOND | W29EE011 | 131072 | 128 | 128 | equal |

**Command that produced this table (194-RESEARCH.md §R1):** an independent join of every
`algorithm: 5` row in `chip_database.json` against the pinned upstream minipro `infoic.xml`
(`a8efaedc236c1d9718bd28299dfbb99536b010ff`, fetched 17,861,009 B, `sha256 cdd21319…6b8a`,
11,481 `<ic>` records scanned), keyed on `(manufacturer, canonical_part_number)` with no
DIP/SMD/pin-count filter. Re-derived (not transcribed) by plan `194-03`'s host leg
(`test_all_27_algorithm_5_rows_carry_their_real_page_and_18_match_the_old_derivation`), which
independently re-implements the old capacity-bracket derivation inside the test and asserts,
against the live regenerated database, both halves of this table: all 27 real pages, and the 18
that matched the old derivation.

---

## 2. The evidence-class split (D-11, success criterion 4)

**The 9 previously under-sized parts, named explicitly:**

1. `AT29BV020,AT29LV020`
2. `AT29BV040,AT29LV040`
3. `AT29C020`
4. `AT29C040`
5. `AT29C512`
6. `AT29LV512`
7. `SST29EE512`
8. `SST29LE512,SST29VE512`
9. `W29C512,W29EE512`

**0 of 9 on hardware, 9 of 9 on the database comparison.**

No silicon has been read back for any of the 9 as of this record. The evidence for all 9 is the
database-comparison route in §1: the row's own upstream `protocol_id` (measured `0x5` for all 27,
194-RESEARCH.md §R1), joined against the pinned upstream XML, compared against the old
capacity-bracket derivation re-implemented inside `194-03`'s host test. This is **strong**
evidence that the generator now emits the correct value and that the firmware now consumes it
without falling back to the old derivation (194-01's `flash_5v_page_write_execute` refusal path
and 194-02's 7-geometry native boundary suite both prove firmware behavior against native/host
harnesses, not against real silicon). It is **not** evidence that a real `AT29C512` or
`W29C512` or any of the other 7 parts reads back byte-identical after a contiguous multi-page
write on an actual Arduino + RURP shield. That is what PAGE-03 asks for, and it stays OPEN.

Plan `194-07` (not yet executed as of this record) is scoped to run a no-regression bench write
on `W29C020` — row 24 above, one of the 18 **already-correct** parts, chosen because gh#67 and
gh#68 were both originally reproduced on it. A green `194-07` result proves the fix did not
regress an already-correct part. **It cannot and does not prove any of the 9 above were fixed**,
because `W29C020` was never wrong. The part ordered to close PAGE-03's hardware leg is a
`W29C512` (row 26, one of the 9), per D-10; until it arrives and is bench-tested, the split above
stays 0 of 9.

---

## 3. Every figure, with its command and its plan

| Figure | Value | Command | Plan |
|---|---|---|---|
| `algorithm: 5` rows in `chip_database.json` | 27 | in-session join against pinned minipro `a8efaedc236c1d9718bd28299dfbb99536b010ff` | 194-RESEARCH.md §R1 |
| `page_size` carriers across 746 rows, post-fix | 45 (18 upstream-native 0x0D + 27 upstream-native 0x05) | `python3 -c` DB-OK assertion: `rows=746 carriers=45 rawkey=744 alg5=27 values=[64,128,256,512]` | 194-01 |
| Rows that gained `page_size` relative to the prior database | 25 | same DB-OK assertion run | 194-01 |
| `W29C512,W29EE512` wire dict `page-size` value | 128 (previously absent entirely) | `EpromDatabase(skip_local_override=True).convert_to_programmer(...)` → `WIRE-OK page-size=128` | 194-01 |
| Native boundary case: real 128-byte page used, not a capacity-derived 64-byte one | 1 SDP signature per page over 128 B (not 64 B) | `test_5v_page_write_execute_page_starts_at_real_page_not_derived` | 194-01 |
| 7 distinct `(mem_size, page_size)` geometries the 27 parts reduce to | `(32768,64) (65536,128) (131072,128) (262144,128) (262144,256) (524288,256) (524288,512)` | in-session enumeration of the 27 rows' `(size_bytes, infoic_page_size_raw)` pairs | 194-RESEARCH.md §R5, measured against the real firmware in 194-02's 7 table-driven native cases |
| Of the 7, pairs where old derivation was wrong | `(65536,128,64) (262144,256,128) (524288,512,256)` | same enumeration | 194-RESEARCH.md §R5 / 194-02 |
| Native boundary + wrong-`mem_size` + refusal cases, both native envs | 208/208 succeeded (196 pre-existing after 194-01, +12 new: 8 boundary/wrong-mem_size + 4 refusal/positive-control) | `pio test -e native` and `pio test -e native_nodevtools` | 194-02 |
| `uno` flash, post-fix | 21616/32256 B (67.0%, 10640 B margin) | `pio run -e uno` (bootloader-guard line) | 194-01, re-confirmed byte-identical by 194-02 |
| `leonardo` flash, post-fix | 23734/28672 B (82.8%, 4938 B margin) | `pio run -e leonardo` (bootloader-guard line) | 194-01, re-confirmed byte-identical by 194-02 |
| `uno` / `leonardo` flash, pre-fix baseline | 21598/32256 B / 23716/28672 B | `pio run -e uno` / `-e leonardo` on the unmodified tree | 194-RESEARCH.md §R2 |
| Native envs, this plan's own re-run (194-06, comment-deletion only) | 208/208 succeeded, both envs, both byte-identical to 194-02's figures | `pio test -e native`, `pio test -e native_nodevtools` | 194-06 |
| `uno` / `leonardo` flash, this plan's own re-run (194-06, comment-only) | 21616/32256 B / 23734/28672 B — byte-identical to 194-01/194-02 | `pio run -e uno`, `pio run -e leonardo` | 194-06 |
| 27-row host two-halves table | all 27 carry `page_size == infoic_page_size_raw`; exactly 18 of 27 also match the old derivation; the other 9 differ by exactly 2× | `test_all_27_algorithm_5_rows_carry_their_real_page_and_18_match_the_old_derivation` | 194-03 |
| Provenance allow-list widened | 20 → 45 identities (18 native 0x0D + 27 native 0x05, imported from `test_lock_status_class_partition.py::_ALGORITHM_0X05_KEYS`) | `test_page_size_invariants.py` legs 4 + 6 | 194-03 |
| Wire-dict delta layer (25 rows newly emitting `page-size`) | 25 entries, values `{64, 128, 256, 512}` | `tests/golden/wire_dict_expected_deltas_194.json`, cross-checked against `programming.infoic_page_size_raw` | 194-04 |
| Host app suite, final state after this plan | 1896 passed, 0 failed | `.venv311/bin/python -m pytest tests/ -o addopts="" -q` | 194-06 |
| Firmware native envs, final state after this plan | 208/208 succeeded, both envs | `pio test -e native`, `pio test -e native_nodevtools` | 194-06 |

---

## 4. Corroborations

- **Independent datasheet agreement, no infoic involved.** The AT29C020 datasheet states
  reprogramming is sector-based with "256 bytes of data loaded into the device and then
  simultaneously programmed" — matching `infoic_page_size_raw: 256` for that part (row 9 above)
  by an entirely independent route (194-CONTEXT.md §Specific Ideas; re-confirmed reaching the
  same value in 194-RESEARCH.md §R1 by the upstream-XML join).
- **The `0x0D` side of the provenance rule was independently re-proven unmoved.** Joining all 84
  `algorithm: 13` rows to their own upstream `protocol_id` gives 18 native + 66 promoted — exactly
  Phase 149's split. Extending D-02's provenance rule to `0x05` changed nothing on the `0x0D` side
  (194-RESEARCH.md §R1 corroboration 1).
- **The 27-to-7 geometry collapse.** The 27 parts in §1 reduce to 7 distinct `(mem_size,
  page_size)` pairs (§3). After this phase, `flash_5v_page_write_execute` reads only
  `handle->page_size` for page arithmetic and never `handle->mem_size` — so the `mem_size` /
  capacity column in §1 is decorative to the firmware oracle. 194-02's own wrong-`mem_size` case
  (`test_5v_page_write_execute_ignores_mem_size_entirely`) proves this at runtime: a deliberately
  wrong `mem_size` (524288, whose old derivation would produce 256) with the real `page_size`
  (128) still produces boundaries on multiples of 128.

---

## 5. What this record does NOT prove

- **It does not prove any of the 9 previously under-sized parts reads back byte-identical on real
  silicon.** §2's split is 0 of 9 on hardware. PAGE-03 stays OPEN in `.planning/REQUIREMENTS.md`
  until the ordered `W29C512` arrives and a bench write is run and read back (D-10, D-11).
- **It does not prove the partial/unaligned-write defect (gh#68) is fixed.** That is Phase 195's
  subject. A correct page size does not by itself stop a partial write from erasing the rest of a
  page it was not asked to touch (194-CONTEXT.md §Phase Boundary).
- **It does not prove a new host is safe against old firmware.** A host carrying this phase's
  database sends `page-size` to firmware that predates this phase and ignores it, silently
  re-deriving the wrong value for the 9. This is filed as a pending backlog item
  (`.planning/todos/pending/new-host-old-firmware-0x05-page-size-skew.md`, D-12), not answered
  here.

---
*Phase: 194-real-page-size-reaches-the-firmware*
*Record measured and committed: 2026-09-15*
