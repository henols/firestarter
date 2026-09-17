---
title: Partial-write refusal record — protocol 0x05, milestone v1.39 Phase 195
phase: 195-partial-writes-stop-destroying-the-page
measured: 2026-09-16
status: AUTHORITATIVE — the citable record of the fix shape chosen, the two measurements that forced it, the SST39SF020 scope correction, and the capability the refusal costs. Not authoritative for any silicon behavior; see §6. That evidence is the bench transcript this record pairs with.
pairs_with: .planning/v1.39/195-w29c020-partial-write-bench-transcript.md
requirements: [WRITE-01, WRITE-02, WRITE-03 (software half only — silicon leg held OPEN, pairs_with bench transcript)]
---

# Partial-write refusal record — Phase 195

Every figure below carries the command, the source, or the plan that produced it. Nothing is
carried forward from `195-RESEARCH.md` without an attribution to it or to the plan that
re-measured it.

---

## 1. The defect, and why the two clauses exist

`[CITED: 195-RESEARCH.md §1a, firestarter_fw/src/proms/flash_5v_page.cpp:80-112]` — the firmware's
`flash_5v_page_write_execute` writes a protocol `0x05` chunk byte by byte, but the underlying part
does not commit byte by byte. The part's own datasheet states the mechanism precisely
`[CITED: W29C020 datasheet, Winbond, Revision A3, February 1998, § "Page Write Mode"]`, verbatim:

> "The W29C020 is written (erased/programmed) on a page basis. Every page contains 128 bytes of
> data. If a byte of data within a page is to be changed, data for the entire page must be loaded
> into the device. **Any byte that is not loaded will be erased to "FF hex" during the write
> operation of the page.**"

The erase is implicit, whole-page, and unconditional — the firmware never issues an erase; the
part erases the page as part of committing it, 200 microseconds after the last byte load closes
the load window. There is no way to abort a page cycle once bytes are loaded into it.

Two source clauses turn a partial chunk into a complete page cycle: `|| is_first_byte` at line 98
(opens the SDP unlock mid-page on the first byte of any chunk) and `|| is_last_byte` at line 106
(closes the page commit on the last byte of any chunk, even mid-page). Per D-09 these clauses are
**deliberately kept, not removed**. The device commits the page by itself 200 microseconds after
the last load regardless of what the firmware does next; deleting the clauses would remove the SDP
unlock and the verify poll that observe that commit, not the commit itself, turning a loud
corruption (an unlock or poll failure the firmware can detect) into a silent one (a commit the
firmware never observed at all). Under the guard this record documents (§3), both clauses become
provably redundant for any chunk that passes — never wrong.

---

## 2. The three loss directions

`[CITED: 195-RESEARCH.md §1c]`. Let `P` = page size, `S` = start address, `L` = payload length,
`C` = chunk size (512 bytes on `uno`, 1024 on `leonardo`).

| # | Direction | Predicate | Evidence class |
|---|---|---|---|
| 1 | Leading loss — bytes before `S` erase | `S % P != 0` | **Reported with silicon evidence** on the originating issue (gh#68, `henols/firestarter_prom` issue #68): `write w29c020 probe2.bin -a 0x40` erased `0x000-0x03F`. |
| 2 | Trailing loss — bytes after `S+L` erase | `(S + L) % P != 0` | **Reported with silicon evidence** on the same issue: a 64-byte file at `-a 0x0` erased `0x040-0x07F`. |
| 3 | Interior loss at a chunk boundary — a page inside the requested range is destroyed when the next chunk re-opens it | `S % P != 0` **and** `L > C` | **Derived from source and a datasheet quotation and never observed.** It has never been run against real silicon. |

Direction 3's classification is the point of this section, not a footnote to it: it is a derived
prediction, modelled end to end in the native suite (plan 02) and attempted on the bench (plan 05),
with its bench result recorded either way — including "not attempted, with the reason" — but at no
point does this record, or any record downstream of it, present direction 3 as reproduced or
confirmed on silicon.

---

## 3. The fix shape, and the two measurements that decided it

`[CITED: 195-RESEARCH.md §3]`. The fix shape is a two-layer **refusal** (D-01): a host pre-flight
predicate `S % P == 0 && L % P == 0` that runs before the serial port opens, plus a firmware
per-chunk guard that refuses any chunk whose address or length is not a whole multiple of the
page. Read-modify-write is not built. The milestone's own decision D-2 explicitly permits refusal
and states the preference order: "losing the operation is strictly better than losing the chip" —
this phase's fix shape takes exactly that preference.

Two measured facts decided this, not a preference:

1. **A 512-byte firmware staging buffer was measured to leave 142 bytes of RAM on `uno` and 213
   bytes on `leonardo` for the entire remaining call stack.** `[CITED: 195-RESEARCH.md §3a
   measurement table]` — a reversible in-session experiment added a `static uint8_t[512]` staging
   buffer to `flash_5v_page.cpp`, rebuilt both AVR environments, and restored the file with an
   `md5sum` and an empty `git status --porcelain` re-check afterward. Result: `uno` RAM used rose
   from 1394 B (68.1%, 654 B free) to 1906 B (93.1%, **142 B free**); `leonardo` rose from 1835 B
   (71.7%, 725 B free) to 2347 B (91.7%, **213 B free**). That remaining headroom must carry the
   JSON parser, the COBS framer, the serial buffers, and every stack frame between them — a stack
   overflow waiting to happen, not a tight fit. A firmware read-modify-write is therefore not
   viable as a general fix; it is viable only as a per-part split (RMW where the page fits in RAM,
   refusal otherwise), which means shipping two behaviours for one protocol and a bench matrix
   that would have to prove both.
2. **The firmware never receives the total payload length.** `[CITED: 195-RESEARCH.md §3b,
   firestarter_app/firestarter/eprom_operations.py:480-497,
   firestarter_fw/src/json_parser.c:56,130]` — only `address` is injected into the write command
   dict; there is no length key anywhere in the wire protocol. A firmware-only refusal therefore
   fires on the **last** chunk, by which point every earlier chunk has already been programmed
   onto the device. That satisfies "no byte outside the requested range was erased" but not
   "leaves the device unchanged" — only a **host pre-connect** refusal can honestly make that
   second claim, because it runs before any byte reaches the wire at all.

Together these two facts are why the shape is a two-layer refusal rather than a firmware
read-modify-write: the buffer the RMW needs is a stack overflow on the smaller board, and even a
firmware-only refusal could not by itself claim the device stays unchanged.

---

## 4. What it cost, and what would restore it

The measured blast radius, caller by caller `[CITED: 195-RESEARCH.md §3b "measured, not
estimated" table]`:

- A full-chip write of a power-of-two-sized image is **unaffected** — the overwhelmingly common
  case, since ROM images are almost always power-of-two sized and every chunk boundary is then
  also a page boundary.
- An odd-sized image (a payload whose length is not a whole multiple of the page) is **refused**
  where it previously silently erased the tail of the last page.
- An unaligned patch write (`-a <address not a multiple of the page size>`) is **refused** where it
  previously silently erased up to `P-1` neighbouring bytes in both directions — this is the
  originating issue's headline use case, "the normal way to patch part of a ROM image."

This is a real, measured usability regression, not a hypothetical one, and it is deliberately not
silently absorbed: the deferred strand that would restore it is filed at
`.planning/todos/pending/host-side-page-alignment-splicing.md`. Its shape: read the head page and
the tail page host-side through the existing region-read primitive, splice the payload over them,
and issue a page-aligned write, with the firmware guard staying in place as the backstop. It needs
no firmware RAM and no firmware change, so it can land later without reopening WRITE-01 or
WRITE-02 — the refusal in this phase makes the chip safe; that strand would make the operation
convenient again, sequenced second because sequencing it first would have meant shipping bench
evidence for a shape this phase did not choose.

A second deferred strand, the override-flag output contract, is filed at
`.planning/todos/pending/protocol-0x05-write-override-flag-output-contract.md` (D-03): an override
that proceeds and then prints the plain success line violates WRITE-02 literally, because that
requirement is unconditional, so no override ships in this phase and what would close the todo is
a decided output contract for an override path, not the flag itself.

---

## 5. Criterion 4, as measured

`[CITED: 195-RESEARCH.md §7, /workspaces/VALIDATED-EPROMS.md]`. The four parts the ROADMAP
criterion and the originating issue both name, and the route each actually needs:

| Part | Algorithm | Page size | Chip ID | Route |
|---|---|---|---|---|
| W29C020 | 5 (`PROTO_FLASH_5V_PAGE`) | 128 | `0xDA45` | Bench — the reproduction part, already on the rig |
| AE29F2008 | 5 (`PROTO_FLASH_5V_PAGE`) | 128 | `0xDA45` | Database identity — same silicon as W29C020 under two names; every field but `part_number` is identical, including the chip id, so a finding on one applies to the other |
| W29C040 | 5 (`PROTO_FLASH_5V_PAGE`) | 256 | `0xDA46` | Native + database check — `P = 256` is covered by construction in the 7-geometry native boundary suite |
| SST39SF020 | **6 (`PROTO_FLASH_NOR_UNLOCK`)** | none recorded | `0xBFB6` | **Neither.** It is `algorithm 6`, not protocol `0x05`; it never traverses `flash_5v_page.cpp` and cannot regress from this phase's change at all. This is a scope correction on the ROADMAP criterion and the originating issue's own claim, not a bench finding. |

This is the scope correction per D-07: of the four validated parts named, one — `SST39SF020` — is
outside this phase's blast radius entirely, so success criterion 4 reduces to one bench part
(W29C020) plus a database-identity check (AE29F2008) plus a native/database check (W29C040), and
the correction is recorded here rather than covered by a vacuous bench pass on a part the change
cannot reach.

**The `dev test` consequence (D-12), with its exact partition:** `dev test`'s write region is 256
bytes at address 0 for every non-UV part. Measured directly from `chip_database.json`'s 27
protocol-`0x05` rows: **25 of 27 rows are unaffected** (page size in `{64, 128, 256}`, a whole
number of pages at 256 bytes), and **2 of 27 rows become a refused partial page** (both recording
page size 512: `AT29BV040,AT29LV040` and `AT29C040`). Neither of the two affected parts has ever
been tested on silicon, and no validated part is among them — so no validated part's `dev test` run
changes under this phase's refusal shape.

---

## 6. What this record proves and what it does not

This record proves the software behaviour on both layers, backed by the native and host suites
named throughout it: the firmware per-chunk guard (plan 01, extended by plan 02's rejection
matrix and chunk-boundary modelling), and the host pre-connect predicate plus its full alignment
matrix (plan 01, extended by plan 03's page-size-validity and regression-surface measurements).

**It does not prove anything on silicon.** That is the bench transcript's job
(`.planning/v1.39/195-w29c020-partial-write-bench-transcript.md`, this record's `pairs_with`
target), and per the milestone's own decision D-4 a green native test is explicitly not sufficient
for a defect that was found on a bench — silicon evidence answers a different question than a
native or host test can. The loss-reproduction leg of that bench evidence can only be produced by a
pre-fix firmware build, because once this phase's fix lands the loss it demonstrates can no longer
be reproduced at all; that is why the bench plan flashes the rig twice, once on a firmware build
made by reverting exactly one source file to its pre-195 blob, and once on the fixed build.

---
*Phase: 195-partial-writes-stop-destroying-the-page*
*Record measured and committed: 2026-09-16*
