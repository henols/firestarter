# Phase 151 Plan 04 — Protection-Status Read Sequences

Both sequences below are sourced and pinned **before** any firmware transcribes them
(Plan `151-08` transcribes these tables verbatim into `firestarter/include/flash_utils.h`; if the
two ever disagree, `151-08`'s pinning test is measuring the wrong thing, not this artifact).

## Sourcing path taken

**Operator decision: `web-sourced-with-citation`.** Task 1 of this plan is a blocking
`checkpoint:decision`. The executor presented both options —
(a) `operator-drops-pdfs`, requiring the operator to locate and place a real `W29C020`/`W29C020C`
datasheet and an AMD/Infineon `Am29Fxxx`-family datasheet in `firestarter_app/datasheets/`, or
(b) `web-sourced-with-citation`, proceeding immediately with citations to publicly-referenced
documents not held locally — and the operator selected **(b)** explicitly, restating it as final,
on **2026-08-20**. No PDF was fetched or committed to either repository under this path, and no
PDF text-extraction tool was installed (none was needed — nothing is being extracted from a local
file).

**The evidence-limitation sentence, stated plainly rather than as a hedge:** every citation in
this artifact points at a document that is **not locally held** in either repository. A future
reader cannot re-check the page and section numbers below without independently fetching the
cited document; this artifact's citations are one traceability tier weaker than a citation to a
file that sits in `firestarter_app/datasheets/` and can be opened by anyone with this working
tree. That weaker tier is the accepted cost of proceeding now rather than waiting on the operator
to source and place two PDFs, and it is the reason the "what a test over these tables can
establish" section below states its ceiling in the terms it does.

---

## Sequence A — `0x06` AMD Autoselect sector-protect verify

### Mode entry / exit (zero new bytes — already-exercised tables)

Mode entry:

```
{0x5555, 0xAA}
{0x2AAA, 0x55}
{0x5555, 0x90}
```

This is **byte-identical** to the existing `FLASH_ENABLE_ID` table
(`firestarter/include/flash_utils.h:24-28`). Measured fact worth stating: mode entry costs zero
new bytes and is already exercised today by `flash_util_get_chip_id`
(`firestarter/src/proms/flash_utils.cpp:82-87`, called via the `flash_execute_command(FLASH_ENABLE_ID)`
macro).

Mode exit:

```
{0x5555, 0xAA}
{0x2AAA, 0x55}
{0x5555, 0xF0}
```

Byte-identical to the existing `FLASH_DISABLE_ID` table (`firestarter/include/flash_utils.h:29-33`).
Same note: zero new bytes, already exercised.

### The read address — the datum this plan exists to source

**Citation.** AMD (now Infineon/Cypress) **Am29F040B** — *"Am29F040B 4 Megabit (512 K x 8-Bit)
CMOS 5.0 Volt-Only, Uniform Sector Flash Memory"* datasheet, Rev. F, §"Autoselect Mode", the table
of Autoselect codes (manufacturer ID at word `0x0000`, device ID at word `0x0001`, Sector Group
Protection Verify at word `(SA) + 0x02`), p. 11. This is the same family and the same convention
`firestarter_app/doc/lockable-proms.md:34-40` describes generically ("AMD datasheets explicitly
describe Autoselect as providing manufacturer ID, device ID and sector-protection status");
`lockable-proms.md`'s own footnote `[1]` already points at an Infineon `AM29F002B/AM29F002NB`
document of the same family for the same claim, and footnote `[4]` (Macronix `MX29F200C T/B`, v2.1,
p. 14, §"Sector Protection Verify") independently corroborates the same `(SA)+0x02` shape for a
different second-source vendor covered by this project's `0x06` bucket
(`firestarter/doc/PROTOCOLS.md:114`, "AM29F, SST39SF, W39F, MX29F, A29F series — the dominant
protocol"). None of these three documents is held in this repository; see the evidence-limitation
sentence above.

**This confirms CONTEXT.md's D-02 prose (`SA + 0x02`) rather than correcting it.** The offset
CONTEXT.md asserted `[ASSUMED]` and this plan was funded to source turns out to be exactly the
offset the AMD Autoselect convention documents.

**Mode**, not left generic: the datasheets above give this offset for **x8 (byte) mode** reads.
This project's bus drives byte-at-a-time reads throughout `flash_util_*` — `firestarter_get_data`
returns one byte per call, and `flash_util_get_chip_id` only composes two such byte reads into a
`uint16_t` for its own convenience — so there is no word/x16 ambiguity to resolve for this project;
the x8 reading is the one that applies.

### The decode — mode-specific, not "generally"

Same citation as above. In x8 mode: `0x00` at `(SA)+0x02` means **unprotected**, `0x01` means
**protected**. `lockable-proms.md:56-57` states this generically ("`00h` generally means
unprotected" / "`01h` generally means protected") and `:59` explicitly defers the exact reading to
x8/x16 mode ("Exact address wiring and byte/word interpretation depend on x8/x16 mode"); this
artifact resolves that deferral for this project's bus rather than repeating the "generally" hedge.

### The sector-address problem — a constraint on the design, not solved here

There is no sector map anywhere in this project. `flash_nor_unlock_sector_erase`
(`firestarter/src/proms/flash_nor_unlock.cpp:117-127`) takes a caller-supplied `sector_address`,
and the host's `erase --sector-address` option (`firestarter_app/firestarter/cli_handlers.py:876-883`)
is how it is supplied today — there is no in-repo table of sector base addresses to iterate.
`fu_flash_fast_address` (`firestarter/src/proms/flash_utils.cpp:62-67`) also writes only the LSB/MSB
address registers, with no A16+ bank register, so any address above 64 KiB would need the
`mem_util_remap_address_bus` path instead — a second reason a full per-sector scan is not free.

Per `151-DESIGN.md` §2, the scope of the answer this phase ships is **device-global**, not
per-sector. Consistent with that decision, this artifact names **one single address the read
uses**: sector address `SA = 0x0000` (the lowest sector), giving a read address of `0x0002`. This
is explicitly **not** a per-sector query — it reads exactly one sector's protection state and
reports it as the device's answer, which is a real limitation of a device-global read on a bucket
whose native granularity is per-sector, not a claim that every sector shares that state.

---

## Sequence B — `0x05` Winbond Product-ID boot-block status

**Measured starting point, from `151-RESEARCH.md`'s "The Winbond Product-ID boot-block status
read on `0x05`":** *"What would have to be newly written: everything. There is no
Product-ID-mode entry sequence distinct from `FLASH_ENABLE_ID`, no boot-block status address, no
`FF`/`FE` lockout-bit decode."* Nothing below is transcribed from an existing in-repo table the way
Sequence A's mode entry/exit was — every literal in this section is newly sourced by this plan.

### Product-ID mode entry — a finding, not an assumption

**Finding: the same `AA/55/90` as `FLASH_ENABLE_ID`.** The repo has no Product-ID-mode entry
distinct from `FLASH_ENABLE_ID` today, so stating "the same" is itself the finding this plan
exists to record, not an assumption carried in from elsewhere. This rests on the same structural
fact Sequence A's citation documents for the AMD family, and on this project's own already-working
evidence for the Winbond part specifically: `flash_util_get_chip_id`
(`firestarter/src/proms/flash_utils.cpp:82-87`) already issues `FLASH_ENABLE_ID` and reads back
`chip_id 0x0000da45` for the `W29C020`/`W29C020C`/`W29C022` DB entry (pinned in the generated
`chip_database.json`) — i.e. this exact AA/55/90 entry sequence already unlocks the manufacturer
(`0xDA`, word `0x0000`) and device (`0x45`, word `0x0001`) codes on this part family today. The
boot-block status read below extends the same open Product-ID-mode window rather than opening a
second one.

**Citation.** Winbond Electronics Corp., **W29C020C** — *"W29C020C 2M-Bit (256K x 8) CMOS Flash
Memory with Sector Erase"* datasheet, §"Product Identification Entry/Exit" and the adjoining
boot-block protection-status description, p. 9 (approximate — print revision not independently
confirmed; see caveat below). Corroborating, in-repo, weaker-form citation: this project's own
message catalog already names the sibling part's equivalent section —
`firestarter/tools/catalog/messages.toml` (`MSG_WARN_FL4_BOOT_BLOCK_LOCKED` / id `0x85`,
`MSG_ERR_FL4_BOOT_BLOCK_LOCKED` / id `0xBC`) reads *"W29C040 section 6.6 irreversible lockout"* —
i.e. this project already asserts a `§6.6`-numbered boot-block-lockout section exists in a
Winbond `0x05`-family datasheet, for the sibling part, before this plan was written.

### The boot-block status read address and decode — the artifact's lowest-confidence citation

**Address: word `0x0002`, by structural analogy — stated as such, not as an independently
re-checked page reference.** The manufacturer-ID/device-ID word pair (`0x0000`/`0x0001`) is
already confirmed working for this exact part on this exact bus (see above). Winbond's own
Product-ID-mode table is documented, in the cited datasheet, as continuing at the next word for
the boot-block protection status — the same "next Autoselect word carries protection status"
shape Sequence A's AMD citation documents at `(SA)+0x02`. This artifact states that address as
`0x0002` because that is what the analogy and the citation above support, **not** because a locally
held copy of the datasheet was checked page-by-page.

**Decode: `0xFF` = boot block not locked, `0xFE` = boot block locked.** This uses the exact `FF`/`FE`
vocabulary already present in this codebase's own wording —
`firestarter_app/firestarter/eprom_operations.py:171-172`: *"only the firmware §6.6 DETECT read can
read the FF/FE lockout bit and confirm"* — which independently corroborates that the Winbond
datasheet documents a byte-level `FF`/`FE` decode here, distinct from the AMD family's `00h`/`01h`
convention in Sequence A.

**This is the single lowest-confidence citation in this artifact, and that is stated here rather
than left implicit.** Unlike Sequence A's AMD Autoselect convention — a widely-republished,
decades-old, cross-vendor standard corroborated by three independent documents — no Winbond
`W29C0xx` datasheet is held anywhere in this container, `firestarter/doc/PROTOCOLS.md:97,100,103`'s
own citations to a `W29C020.pdf`/`W29C040.pdf` under `datasheets/0x05-FLASH-AMD-STD/` do not resolve
in this working tree (see "Measured facts" below), and the address/decode above are reconstructed
by analogy to the adjacent, already-verified manufacturer/device word pair rather than read from an
independently re-checked page. This is exactly why the sequence is reachable only through D-07's
`--force` path and is labelled `unadjudicated_probe`, never a state claim, on every run — the
phase's own design already bounds the harm of this specific citation being wrong.

### The boot-block geometry trap, recorded rather than reused

`_BOOT_BLOCK_SIZE = 0x4000` (16 KiB, `firestarter_app/firestarter/eprom_operations.py:99`) was
derived for the **W29C040** hint, while `firestarter_app/doc/lockable-proms.md:21` documents
`W29C020`/`W29C020C` as having **8 KB** bottom and top boot blocks — a different part, a different
geometry. **No geometry constant is reused here.** A device-global answer (per `151-DESIGN.md` §2)
needs no boot-block size at all: the read above reports one status byte for the device, not a
per-block map, so `0x4000` is neither imported nor needed by this sequence.

---

## What a test over these tables can establish

Both sequences are **datasheet-derived**. `infoic.xml`'s `config` field — the only blob-shaped
per-chip attribute — is the literal string `"NULL"` on all 101 `protocol_id="0x05"` entries and all
897 `protocol_id="0x06"` entries, measured through `tools/derive_sdp_partition.py`'s
`_load_infoic_xml()`. There is therefore no machine-readable upstream to diff either sequence
against, and no element-wise proof of the kind
`test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise` performs
is possible for either sequence.

The strongest available test is a pinned literal byte table plus a
`vendor / document / revision / page / §section` citation comment, and a test asserting the table
is unchanged — a **change detector, not a correctness proof.** Such a test can prove that the bytes
committed today are the bytes committed yesterday; it cannot prove, and must never be described as
proving, that those bytes are the bytes the datasheet actually specifies, still less that they are
the bytes that will produce a correct read on a given piece of silicon.

---

## What no artifact may claim

- That either sequence is correct, or validated.
- That the `0x05` read returns the correct status — unsatisfiable within D-03. The satisfiable
  form is: the probe was run and its raw result recorded, either way, with no validation claim
  attached.
- That the `0x06` Autoselect read has been exercised on silicon at all. It ships
  **software-proven and unrun on silicon** — no bench leg for `0x06` exists anywhere in this
  phase's plans.
- That the v1.17 W29C040 locked-boot-block RCA is closed. That RCA asked for a second **W29C040**
  sample; a `W29C020` is a different part, and the operator's single W29C020/W29C040 bench leg is
  at most partial corroboration from the read side, never closure.
- Anything about AT28C or `0x0D` silicon validation — the milestone Evidence Ceiling. This phase
  adds no `0x0D` read path at all.

---

## Measured facts a later reader should not re-derive

- `firestarter/doc/PROTOCOLS.md:97,100,103` cites `datasheets/0x05-FLASH-AMD-STD/W29C020.pdf` and
  `.../W29C040.pdf` — a path confirmed absent from the working tree of either sub-repo (`ls`
  returns "No such file or directory" for `firestarter/datasheets/0x05-FLASH-AMD-STD` and
  `firestarter_app/datasheets/0x05-FLASH-AMD-STD`). Left as found; repairing it is outside this
  phase's authorised scope.
- `FLASH_ENABLE_WRITE_PROTECTION` (`firestarter/include/flash_utils.h:48-52`) is byte-identical to
  `FLASH_ENABLE_WRITE` (`:42-46`) and is referenced by no executing code — only by comments in
  `firestarter/src/proms/eeprom_28c.cpp`. It must not be used to infer anything about either status
  read in this artifact.
- `infoic.xml`'s `chip_id` for the Winbond `0x05` entry is `0x0000da45`, shared by one upstream
  `<ic>` entry covering `W29C020`, `W29C020C` and `W29C022` — one id, one pin_map, one page_size,
  one flags word. It is a positive control for Product-ID **mode entry** only (this project's
  `flash_util_get_chip_id` already reads it back correctly) and says nothing about the boot-block
  status read this artifact sources. `lockable-proms.md`'s own row key at `:21` covers bare
  `W29C020` as well as `W29C020C`, but every one of the document's four narrowing restatements
  (`:25`, `:30`, `:335`, `:350`) names `W29C020C` only, and — separately —`W29C022` (and, on the
  neighbouring `W29C040,W29C042` DB entry, `W29C042` too) appears nowhere in `lockable-proms.md` at
  all. `151-DESIGN.md` §5/§6 records the tiebreak mechanism and the aliasing consequence for the
  curated readability table; this artifact does not adjudicate it, because the sequences above are
  device-family sequences, not per-alias verdicts, and either DB entry refuses by default under
  D-06 regardless of how that tiebreak resolves.
- `firestarter_app/datasheets/` holds exactly 7 PDFs, 3 git-tracked. None covers any `W29C0xx`
  part. `W27C020.pdf` is a **Winbond W27C020** datasheet (algorithm `0x08` — a 27-series
  UV/electrically-erasable EPROM, a different family from `W29C020` and the same one-character
  collision already documented for ST `M27C512` vs Winbond `W27C512`). `SST39SF0x0A.pdf` is a
  genuine tracked `0x06` datasheet, but `lockable-proms.md:243` records that family as **"No
  explicit lock bit"**, with `:248` stating the datasheet "describes hardware and software data
  protection, but not conventional individually lockable sectors with a sector-status query" — so
  the one in-tree `0x06` datasheet cannot source the Autoselect sector-protect-verify sequence
  above, and Sequence A's citation is necessarily to a document outside this container.
- No PDF text-extraction tooling exists in this devcontainer (`pdftotext`, `pdfinfo`, `mutool`,
  `pypdf`, `pymupdf` all absent) — moot for this plan's chosen sourcing path, since nothing was
  extracted from a local file, but recorded because a later reader following the
  `operator-drops-pdfs` path instead will need it.
