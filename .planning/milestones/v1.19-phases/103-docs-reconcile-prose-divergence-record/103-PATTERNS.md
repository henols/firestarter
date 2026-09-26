# Phase 103: DOCS — Reconcile Prose + Divergence Record - Pattern Map

**Mapped:** 2026-07-01
**Files analyzed:** 1 edited (`firestarter/doc/PROTOCOLS.md`) + 4 re-verified gate tools + 3 GSD close artifacts
**Analogs found:** 1 exact (Phase 100 revise-in-place) / 1 primary work file

## Scope note (docs-only phase)

This is a terminal, docs-only closing phase. There are **no new source-code files** and no
firmware/host/DB/wire changes. The single edited work surface is `firestarter/doc/PROTOCOLS.md`.
The remaining "files" are (a) gate tools re-run for verification (read-only) and (b) GSD
milestone-close artifacts. The closest analog is not a code file but the **prior revise-in-place
doc-edit pattern from Phase 100**, which authored the very sections Phase 103 now reconciles.
The illustrative code excerpts below are Markdown before/after pairs extracted directly from the
current work surface — copy these edit shapes, not abstract guidance.

## File Classification

| File | Role | Data Flow | Closest Analog | Match Quality |
|------|------|-----------|----------------|---------------|
| `firestarter/doc/PROTOCOLS.md` (§1 headings + facet prose, §3 INV matrix, new D-04 callout) | doc (Markdown reference) | transform (in-place prose/anchor rewrite over a frozen surface) | Phase 100 `100-01` revise-in-place edit of this same file | exact (same file, same edit discipline) |
| GATE re-verify: `firestarter_app/tests/test_dispatch_mirror.py` (re-run) | test (guard) | request-response (pytest assert) | Phase 101 D-03 guard re-run | verification-only |
| GATE re-verify: `firestarter_app/tools/check_dispatch.py`, `tools/diff_db.py` (re-run) | tooling (gate) | batch (parse + diff) | v1.16 / Phase 100 gate re-run | verification-only |
| GATE re-verify: `pio test -e native` (`firestarter/test/native/`) (re-run) | test (native dispatch) | batch (Unity suite) | v1.16 golden traces | verification-only |
| GSD close: `STATE.md` / `PROJECT.md` / `MILESTONES.md` | config (planning artifact) | transform (append close record) | Phase 100 `100-VERIFICATION.md` close pattern | role-match |

## Pattern Assignments

### `firestarter/doc/PROTOCOLS.md` — §1 heading rename (D-01) — 12 headings

**Analog:** Phase 100 `100-01-SUMMARY.md` — "Revise-in-place doc pattern: expand … while
preserving frozen slug column + facet prose verbatim." Same file, same in-place git-diff-reviewable
discipline. Phase 100 already added the `PROTO_` token to each §1.x **col-2 line** (L70, L90, L110,
L130, …); Phase 103 promotes that token into the **heading** and drops the slug from the heading.

**Heading form to copy** (the token already exists on the col-2 line one line below the heading —
lift it, keep the trailing description verbatim). Current → target for §1.1 (PROTOCOLS.md L67):
```markdown
### 1.1 — 0x05 FLASH-AMD-STD: 5V Page-Write Flash (EEPROM-like)
```
becomes (token-first, per Open-Question-2 recommendation matching CONTEXT.md illustrative):
```markdown
### 1.1 — 0x05 PROTO_FLASH_5V_PAGE: 5V Page-Write Flash (EEPROM-like)
```

**The 12 heading rewrites** (current text at the cited line → token to substitute; keep the `— 0x..`
hex and the trailing `: <description>` verbatim, replace only the `<SLUG>` segment):

| Line | Current slug segment in heading | Substitute token |
|------|--------------------------------|------------------|
| L67  | `FLASH-AMD-STD`   | `PROTO_FLASH_5V_PAGE` |
| L87  | `FLASH-AMD-ALT`   | `PROTO_FLASH_NOR_UNLOCK` |
| L107 | `EPROM-STD`       | `PROTO_EPROM_28PIN` |
| L127 | `EPROM-QUICK`     | `PROTO_EPROM_32PIN` |
| L146 | `EPROM-LEGACY`    | `PROTO_EPROM_24PIN` |
| L165 | `EEPROM-POLL`     | `PROTO_EEPROM_PARALLEL` |
| L184 | `SRAM-32PIN`      | `PROTO_SRAM_32PIN` |
| L203 | `FLASH-INTEL`     | `PROTO_FLASH_INTEL` |
| L223 | `SRAM-24PIN`      | `PROTO_SRAM_24PIN` |
| L242 | `SRAM-STD`        | `PROTO_SRAM_28PIN` |
| L280 | `SRAM-512K-1M`    | `PROTO_SRAM_32PIN_NVRAM` |
| L298 | `EEPROM-X88C64`   | `PROTO_EEPROM_8051BUS` |

Source-of-truth for every token is the §0 canonical bucket table (PROTOCOLS.md L32–43, col
`PROTO_ token`) — do NOT invent; copy the exact token string.

**RETAIN in the same section body (do NOT touch — D-02 retention #2):** the `**Folder slug (col
1):**` line immediately below each heading keeps the old slug verbatim (e.g. L69 `0x05-FLASH-AMD-STD`).
This is the divergence record that lets the slug drop out of the heading without loss.

---

### `firestarter/doc/PROTOCOLS.md` — §3 cross-link anchor regeneration (D-01, paired) — 8 links

**Analog:** the current L410–417 links are their own template — each already encodes the GitHub
slugger output for the *current* heading. Regenerate from the *new* heading text using the same
slugger rules (lowercase, drop `#`/`:`/`(`/`)`/`—`/`.`, spaces→`-`, **keep `_`**, dropped-char runs
leave multi-hyphens). Then `grep -n "](#1" doc/PROTOCOLS.md` and confirm each resolves.

**Current cross-link block** (PROTOCOLS.md L410–417) — the exact shape to rewrite:
```markdown
- INV-01, INV-02: [§1.5 (0x0B EPROM-LEGACY)](#15----0x0b-eprom-legacy-24-pin-uv-eprom-12-25-v-direct-vpe-rail)
- INV-03: [§1.4 (0x08 EPROM-QUICK)](#14----0x08-eprom-quick-32-pin-uv-eprom--ee-eprom-13-v-vpp)
- INV-04: [§1.1 (0x05 FLASH-AMD-STD)](#11----0x05-flash-amd-std-5v-page-write-flash-eeprom-like)
- INV-05: [§1.3 (0x07 EPROM-STD)](#13----0x07-eprom-std-28-pin-uv-eprom--ee-eprom-13-v-vpp)
- INV-06: [§1.4 (0x08 EPROM-QUICK)](#14...), [§1.5 (0x0B EPROM-LEGACY)](#15...)
- INV-07: [§1.10 (0x28 SRAM-STD)](#110----0x28-sram-std-28-pin-sram--fram-name-04-fm1608-sramfram-correction)
- INV-08: [§1.3 (0x07 EPROM-STD)](#13----0x07-eprom-std-28-pin-uv-eprom--ee-eprom-13-v-vpp)
- INV-09: [§1.2 (0x06 FLASH-AMD-ALT)](#12----0x06-flash-amd-alt-amdsst-unlock-sequence-nor-flash)
```
Two things change per link: (1) the visible link **text** `(0x.. SLUG)` → `(0x.. PROTO_TOKEN)`,
and (2) the `#...` **anchor** regenerated from the renamed heading. Illustrative for INV-04 →
renamed §1.1 heading `### 1.1 — 0x05 PROTO_FLASH_5V_PAGE: 5V Page-Write Flash (EEPROM-like)`:
```markdown
- INV-04: [§1.1 (0x05 PROTO_FLASH_5V_PAGE)](#11----0x05-proto_flash_5v_page-5v-page-write-flash-eeprom-like)
```
(underscores preserved, letters lowercased). Do NOT hand-guess — grep-verify each after edit.

**KEEP unchanged:** the reader-router link at L16 `[§1 (real protocol buckets)](#1-real-protocol-buckets)`
points at the top-level `## 1.` heading (not renamed) — leave it.

---

### `firestarter/doc/PROTOCOLS.md` — §3 INV-row augmentation (D-03) — 9 rows

**Analog:** the existing INV table (PROTOCOLS.md L398–406) is the template. Augment ONLY the
"One-line behavior" column; the other four columns (`INV id`, `Owning handler file`, `Planned
native test function name`, `Suite path`) stay **byte-identical** (SAFE-02 grep contract).

**Current row (INV-01, PROTOCOLS.md L398)** — exact shape:
```markdown
| INV-01 | 0x0B uses `FLAG_VPE_AS_VPP` direct-VPE rail (no `CTRL_VPP_VPE_DROP_ENABLE` drop) | `eprom.cpp` | `test_inv01_eprom_0x0B_direct_vpe_rail` | `test/native/avr/test_val_eprom/` |
```
augment behavior column only (prepend token beside the hex, per CONTEXT.md illustrative):
```markdown
| INV-01 | `PROTO_EPROM_24PIN` (0x0B) uses `FLAG_VPE_AS_VPP` direct-VPE rail (no `CTRL_VPP_VPE_DROP_ENABLE` drop) | `eprom.cpp` | `test_inv01_eprom_0x0B_direct_vpe_rail` | `test/native/avr/test_val_eprom/` |
```

**Per-row hex→token map** (from §0 table L32–43; the hex leading each behavior cell picks the token):

| Row | Hex in behavior cell | Token to prepend |
|-----|---------------------|------------------|
| INV-01, INV-02 | `0x0B` | `PROTO_EPROM_24PIN` |
| INV-03, INV-06(0x08 part) | `0x08` | `PROTO_EPROM_32PIN` |
| INV-04 | flash4 / `0x05` | `PROTO_FLASH_5V_PAGE` |
| INV-05, INV-08, INV-06(0x07 part) | `0x07` | `PROTO_EPROM_28PIN` |
| INV-06 (0x0B part) | `0x0B` | `PROTO_EPROM_24PIN` |
| INV-07 | `0x28` (FM1608 SRAM) | `PROTO_SRAM_28PIN` |
| INV-09 | `0x06` (SST39SF040) | `PROTO_FLASH_NOR_UNLOCK` |

Note INV-06 mentions three hexes (0x08/0x0B/0x07) — name ALL THREE tokens in-prose beside their raw
hexes (`PROTO_EPROM_32PIN` (0x08) / `PROTO_EPROM_24PIN` (0x0B) / `PROTO_EPROM_28PIN` (0x07)) without
changing the default-pulse µs facts. D-03 wants the token alongside the raw hex per row, so the
"0x07 default" hex in the INV-06 cell also gets its `PROTO_EPROM_28PIN` token. INV-08's `(dispatch-only scope)` prose and its `build_db.py` reference stay verbatim.

---

### `firestarter/doc/PROTOCOLS.md` — facet-prose jargon purge (D-02)

**Analog:** none needed beyond the RESEARCH.md verified purge inventory. Two prose rephrases plus
heading purge (already covered by D-01). Section-scoped edits only.

**§1.8 pin-roles (PROTOCOLS.md L219)** — the explicit D-02 example. Current:
```markdown
… any address suffices. Unlike AMD flash, there is no address-based unlock; commands go directly.
```
rephrase to a neutral descriptor (Claude's discretion on wording), e.g.:
```markdown
… any address suffices. Unlike the unlock-sequence NOR path (0x06 / PROTO_FLASH_NOR_UNLOCK), there is no address-based unlock; commands go directly.
```

**§2.1 prose (PROTOCOLS.md L353)** — raw bucket label in prose. Current:
```markdown
These are not FLASH-AMD-STD variants, EPROM variants, or any other real protocol. They are dead dispatch arms.
```
rephrase off the old bucket-label, e.g. "These are not 5V page-write flash (`PROTO_FLASH_5V_PAGE`)
variants, EPROM variants, …". NOTE: the surrounding §2.1 minipro-provenance rows at L349–350
(`IC2_ALG_ITE is an ITE EC microcontroller label in minipro …`) are **retention #3 — leave verbatim**.

---

### `firestarter/doc/PROTOCOLS.md` — D-04 "Name ↔ Slug Divergence" callout (new subsection)

**Analog:** the §0 approved-callout blockquote (PROTOCOLS.md L24–28) is the in-file style template
for an authoritative callout — reuse its blockquote form and placement discipline (near the §0
table it references). Placement/heading-level is Claude's discretion (near the top table vs. own §).

**Style template to copy** (PROTOCOLS.md L24–28):
```markdown
> **Operator-approved 2026-07-01 at the Phase-100 NAME-02 gate.** Every `PROTO_` token and
> display name below is final and authoritative; the frozen `datasheets/<hex>-<NAME>/` slug
> column (col 1) is retained verbatim as the DOC-02 divergence anchor and is NOT renamed
> (NAME-F1 deferred). …
```
The new callout states three facts (D-04 a/b/c): (a) the §0 frozen-slug column IS the canonical
old-slug↔new-name map; (b) `datasheets/` folder slugs are intentionally frozen, NOT renamed
(NAME-F1 deferred); (c) the host uses ASCII-normalized dashes (`—`/`–` → `-`) in display strings —
a documented punctuation deviation from the em-dash col-2 names (Phase 102 D-02).

---

### GATE re-verification (D-05) — read-only tool re-run, no edits

**Analog:** Phase 100 `100-VERIFICATION.md` close-verify pattern (`git diff --stat` = one file;
gates green). Commands are already assembled in RESEARCH.md §Code Examples and are the exact gate
surface; the executor runs them, records pass/CI-PENDING, and edits nothing:
```bash
cd firestarter_app
python -m pytest tests/test_dispatch_mirror.py -q     # GATE-01 host leg (parses §0 tables only)
python tools/check_dispatch.py                         # GATE-01 dispatch mirror
python -m pytest tests/ -k "parity" -q                 # GATE-02 constants.py <-> firestarter.h
python tools/diff_db.py                                # GATE-02 chip_database.json identity
cd ../firestarter && pio test -e native                # GATE-01 golden traces + native dispatch
```
Devcontainer is py3.12 (CI target py3.11) — record py3.11-scoped checks as CI-PENDING/structurally-green
per the established Phase-98 precedent if the target interpreter is absent.

## Shared Patterns

### Numbers stay the dispatch key (GATE-01/02/03 invariant)
**Source:** `firestarter/CLAUDE.md` §Protocol Dispatch — "every value equals the pre-existing
raw-hex dispatch key it names; numbers stay the dispatch key end to end (GATE-01)."
**Apply to:** every edit. Names are a legibility layer; the doc reconciles prose/anchors, never a
dispatch/lookup key. The hex stays beside every token in headings and INV rows.

### Frozen-slug retention (DOC-02 / NAME-F1 deferral)
**Source:** PROTOCOLS.md §0 table col-1 (L32–43) + each `**Folder slug (col 1):**` line + every
`datasheets/<slug>/*.pdf` citation path in §1 (e.g. L75, L95, L115).
**Apply to:** all §1 sections. The slug strings and citation paths are RETAINED VERBATIM — a git
diff touching any `datasheets/0x…` path or a `Folder slug (col 1)` line is a D-02 violation.

### Anchor discipline (GitHub slugger)
**Source:** RESEARCH.md Architecture Pattern 1 + the current L410–417 anchors (which match the
current headings' slugger output).
**Apply to:** the 8 §3 cross-links. Rename heading + regenerate anchor in the SAME pass; then
`grep -n "](#1" doc/PROTOCOLS.md` and confirm each of 8 fragments resolves. Never hand-guess.

### Three D-02 locked retentions (blind-find/replace trap)
**Source:** RESEARCH.md §State of the Art RETAIN table + verified line cites.
**Apply to:** any purge edit. RETAIN: (1) `Flash — AMD/SST unlock-sequence NOR` (approved 0x06
display name, §0 L33 + §1.2 col-2 L90, em-dash intact); (2) all frozen slug strings + citation
paths; (3) §2 minipro-provenance prose (L349–350 `IC2_ALG_ITE`, §2.1/§2.2 phantom+infeasible text).
Datasheet-accurate "AMD unlock command addresses (0x5555/0x2AAA)" (§1.2 L103) and datasheet "Quick-Pulse
Programming" citation (§1.4 L135) are KEEPS, not jargon.

## No Analog Found

None. Every edit shape has a template in the same file (Phase 87/100 authored it), and every
verification tool already exists (v1.16 / Phase 100/101). No RESEARCH.md-only fallback pattern is
required. The one nuance (GitHub slugger anchor regeneration) is self-checked by the mandatory
grep step, not by a code analog.

## Optional / Flagged (not required)

The 0x34 host `description_points` bullet in `firestarter_app/firestarter/ic_layout.py`
(`XICOR 8051-multiplexed bus; not implemented on RURP (FUT-01)`) was flagged Phase-103-DOC-01-owned
in Phase 102, but it lives in host code (a GATE-03 surface), NOT in PROTOCOLS.md. Per CONTEXT.md
scope (DOC-01 = PROTOCOLS.md §1/§3 only) treat as out-of-scope; if the planner honors the handoff
it is a display-string-only edit (GATE-03 safe, no DB/wire change). Analog if scoped in: Phase 102
`ic_layout.py` `_PROTOCOL_DISPLAY_NAME` / `description_points` edit pattern (`102-PATTERNS.md`).

## Metadata

**Analog search scope:** `firestarter/doc/PROTOCOLS.md` (full, 425 lines), `.planning/phases/100-*/`,
`.planning/phases/101-*/`, `.planning/phases/102-*/`, `firestarter/CLAUDE.md`, gate-tool locations.
**Files scanned:** 1 work surface + 3 prior-phase summary sets + 4 gate-tool references.
**Pattern extraction date:** 2026-07-01
