# Phase 103: DOCS — Reconcile Prose + Divergence Record - Context

**Gathered:** 2026-07-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Reconcile `firestarter/doc/PROTOCOLS.md` to the operator-approved canonical name set (Phase
100), applied in firmware (Phase 101) and host display (Phase 102), and close the v1.19
milestone. Two deliverables:

- **DOC-01** — reconcile the §1 four-facet bucket prose + the INV-01..09 native-test
  traceability matrix to the new names/tokens, with no dangling minipro-heritage jargon
  (`AMD`/`QUICK`/`ALT`/raw-hex-only bucket labels) *except* where an occurrence is locked or
  frozen by an earlier phase (see D-02).
- **DOC-02** — explicitly record the name↔`datasheets/<hex>-<NAME>/` slug divergence; the
  frozen slug column is retained verbatim and the `datasheets/` folder slugs are **NOT**
  renamed (NAME-F1 deferred).

This is a **docs-only closing phase**. GATE-01/GATE-02/GATE-03 are re-verified at close but no
firmware, host code, `chip_database.json`, wire, or lockstep-constant value changes here.

**In scope:** `firestarter/doc/PROTOCOLS.md` §1 headings + facet prose, the §3 INV matrix, the
§3→§1 cross-links + document TOC anchors, and a new divergence callout. Milestone-close
housekeeping (GATE re-verification, STATE/PROJECT/MILESTONES updates).
**Out of scope:** renaming `datasheets/` folder slugs (NAME-F1), re-opening any Phase-100
approved name, accepting names as CLI input (NAME-F2), any DB/wire/lockstep value change
(GATE-02), the lockstep beta cut + gitlink bump (operator-gated).

</domain>

<decisions>
## Implementation Decisions

### §1 section-heading treatment (DOC-01)
- **D-01:** **Rename all 12 §1 section headings** from the slug-jargon form
  (`### 1.1 — 0x05 FLASH-AMD-STD: …`, `EPROM-QUICK`, `FLASH-AMD-ALT`, `SRAM-STD`, …) to the
  new canonical display name / token form (e.g. `### 1.1 — 0x05 PROTO_FLASH_5V_PAGE: 5V
  Page-Write Flash (EEPROM-like)`). **Then update every anchor that points at the old
  heading slugs** — the document TOC and the §3 "Cross-links to per-bucket sections" list
  (`#11----0x05-flash-amd-std-…` → the new anchor). The frozen slug stays visible via the
  existing per-section **"Folder slug (col 1):"** line, so the divergence record is preserved
  without keeping jargon in the heading. **No broken anchors** is a hard completeness
  constraint — grep the doc for `#1` fragment links after the rename and confirm each
  resolves.

### Jargon-purge boundary (DOC-01)
- **D-02:** **Aggressive purge everywhere EXCEPT three locked/frozen retentions.** Scrub
  minipro/`AMD`/`QUICK`/`ALT` bucket-label jargon from all headings and facet prose —
  including behavior-prose mentions like "Unlike AMD flash …" (rephrase to a neutral
  descriptor) and any raw-hex-only bucket labels. **Retain verbatim, do NOT touch:**
  1. **The approved 0x06 display name** `Flash — AMD/SST unlock-sequence NOR` — it is the
     Phase-100 operator-approved canonical name; changing it re-opens the naming gate.
  2. **The frozen slug column strings** (`0x05-FLASH-AMD-STD`, `0x06-FLASH-AMD-ALT`,
     `0x08-EPROM-QUICK`, …) — DOC-02 requires them retained unchanged; scrubbing them =
     NAME-F1 slug rename (deferred). This includes the `datasheets/<slug>/*.pdf` citation
     paths, which reference the frozen folder names.
  3. **§2 minipro-provenance prose** (e.g. "`IC2_ALG_ITE` is an ITE EC label in minipro, NOT
     a memory algorithm") — this IS the honest-non-protocols heritage record, not stray
     jargon. Leave §2's phantom/infeasible explanations intact.
  Datasheet-accurate terms that happen to contain "AMD" (e.g. "AMD unlock command addresses
  0x5555/0x2AAA") are behavior-correct facts, not bucket jargon — keep them; only the
  *minipro bucket-label heritage* is the target.

### INV-01..09 matrix reconciliation (DOC-01)
- **D-03:** **Add the PROTO_ token/name alongside the raw hex** in each INV row's one-line
  behavior text (e.g. "0x0B uses `FLAG_VPE_AS_VPP`…" → "`PROTO_EPROM_24PIN` (0x0B) uses
  `FLAG_VPE_AS_VPP`…"). The hex stays — it is the precise invariant/dispatch key — the name
  is added for legibility. The `INV-0N` ids, owning-handler-file names, and native-test
  function names stay **byte-identical** (SAFE-02 grep-intact handoff — a `grep -rn INV-04`
  must still hit the doc row + native test). Also update the §3 cross-link anchor text to the
  renamed §1 headings (paired with D-01).

### Divergence record form (DOC-02)
- **D-04:** **Add a dedicated "Name ↔ Slug Divergence" callout** (short subsection) that
  states plainly: (a) the top bucket-set table's frozen-slug column is the canonical
  old-slug↔new-name map; (b) the `datasheets/` folder slugs are intentionally frozen and NOT
  renamed (NAME-F1 deferred, avoids provenance churn); and (c) the **host uses
  ASCII-normalized dashes** (`—`/`–` → `-`) in its display strings — a documented punctuation
  deviation from the em-dash PROTOCOLS.md col-2 names (Phase 102 D-02). This makes DOC-02
  unambiguous in one place, on top of the existing per-section slug lines.

### Milestone close + GATE re-verification (SC3)
- **D-05:** At close, re-verify GATE-01/02/03 and record the result: golden register traces +
  dispatch-mirror guard green (GATE-01); `diff_db.py` identity + `check_dispatch.py` +
  constants-parity green, no DB/wire value change (GATE-02); CLI grammar unchanged (GATE-03).
  **Dispatch-mirror guard note:** `test_dispatch_mirror.py`'s parser was fixed in Phase 101
  (D-03) against the top bucket-set *table* — Phase 103 only touches §1 headings/prose, the
  INV matrix, and adds a callout, NOT that table — but the executor MUST re-run the guard
  after edits to confirm the heading/anchor churn didn't break it.

### Claude's Discretion
- Exact heading wording (token-first vs. display-name-first vs. both), the precise placement
  and heading level of the D-04 divergence callout (near the top table vs. its own §), and the
  exact rephrasing of purged behavior-prose sentences — as long as D-01–D-04 hold and no
  anchor breaks. Plan/wave decomposition and milestone-close sequencing are the planner's call.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The single source of truth (the approved names — NOT re-opened here)
- `firestarter/doc/PROTOCOLS.md` — **the primary work surface.** §Canonical bucket set (the
  hex | slug | `PROTO_` token | display name | handler-family table, already revised in Phase
  100), §1.1–§1.12 (four-facet prose + per-section "Folder slug (col 1)" / "Canonical name
  (col 2)" lines — the headings + prose Phase 103 reconciles), §2 (phantom/infeasible
  non-protocols — provenance prose RETAINED per D-02), §3 (INV-01..09 matrix + §3→§1
  cross-links + document TOC anchors).
- `.planning/phases/100-name-canonical-protocol-name-set-operator-approval/100-CONTEXT.md` —
  D-07 (frozen slug column = DOC-02 divergence record; slugs NOT renamed) and the full 3-field
  name schema. The approved name set is authoritative; Phase 103 conforms, does not re-open it.
- `.planning/phases/102-host-apply-names-in-the-host-cli-display/102-CONTEXT.md` — D-02 (host
  ASCII-dash normalization) is the deviation the D-04 callout must record.

### Requirements & roadmap
- `.planning/REQUIREMENTS.md` — DOC-01, DOC-02 (this phase); GATE-01/02/03 (re-verified at
  close); §Out of Scope (NAME-F1 slug rename, NAME-F2 CLI-alias — both deferred).
- `.planning/ROADMAP.md` §Phase 103 — goal + 3 success criteria; §v1.19 milestone header for
  the non-regression invariant + close expectations.

### Gate / regression guards to keep green (GATE re-verification — D-05)
- `firestarter_app/tests/test_dispatch_mirror.py` — dispatch-mirror guard (parser fixed in
  Phase 101 D-03; re-run after heading/anchor edits).
- `firestarter_app/tools/check_dispatch.py` — dispatch mirror check (GATE-01).
- `firestarter_app/tools/diff_db.py` — `chip_database.json` identity (GATE-02).
- constants-parity pytest (`constants.py` ↔ `firestarter.h`) — GATE-02.
- v1.16 golden register traces + `pio test -e native` — GATE-01 dispatch-behavior unchanged.

### Provenance (do NOT treat as a work target — read-only context)
- `datasheets/<hex>-<NAME>/` (top-level) folder slugs — **frozen**; the col-1 divergence
  anchor and the citation-path source in §1 prose. Do NOT rename (NAME-F1).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **The §Canonical bucket set table** (PROTOCOLS.md ~L30–57) already carries the new `PROTO_`
  tokens, display names, and the frozen-slug column — Phase 100 built it. It doubles as the
  old-slug↔new-name map the D-04 callout points to; Phase 103 does NOT edit this table.
- **Per-section "Folder slug (col 1)" / "Canonical name (col 2)" lines** already exist in each
  §1.x — the slug half is the divergence record that lets D-01 drop the slug from the heading
  without losing it.
- **`INV-0N` ids + native-test function names** are already grep-stable (SAFE-02) — D-03 keeps
  them byte-identical and only augments the human-readable behavior column.

### Established Patterns
- **Names are a legibility layer only** — numbers stay the dispatch key end to end
  (GATE-01/02/03). Doc reconciliation changes prose/anchors, never a dispatch/lookup key.
- **Frozen-slug convention (DOC-02 / NAME-F1)** — `datasheets/` slugs are provenance and stay
  put; divergence is documented, never silently applied.
- **Anchor discipline** — GitHub auto-generates heading anchors from heading text; renaming a
  heading changes its anchor, so every in-doc `#…` link to it must be updated in lockstep.

### Integration Points
- Phase 103 is the terminal consumer of the Phase-100 name set — no downstream phase reads its
  output; the milestone closes here. The doc is the last surface where the applied names
  (firmware tokens + host display strings) are reconciled into one coherent human reference.

</code_context>

<specifics>
## Specific Ideas

- Heading rename direction (illustrative): `### 1.1 — 0x05 FLASH-AMD-STD: 5V Page-Write Flash
  (EEPROM-like)` → `### 1.1 — 0x05 PROTO_FLASH_5V_PAGE: 5V Page-Write Flash (EEPROM-like)`;
  `### 1.4 — 0x08 EPROM-QUICK: …` → `### 1.4 — 0x08 PROTO_EPROM_32PIN: …`.
- INV row augmentation (illustrative): `INV-01 | 0x0B uses FLAG_VPE_AS_VPP direct-VPE rail …`
  → `INV-01 | PROTO_EPROM_24PIN (0x0B) uses FLAG_VPE_AS_VPP direct-VPE rail …`.
- The three locked retentions (D-02) are the traps a naive find/replace would hit — the
  approved `AMD/SST unlock-sequence` name, the frozen `…-AMD-…`/`…-QUICK`/`…-ALT` slug strings
  (incl. citation paths), and the §2 minipro-heritage explanations.

</specifics>

<deferred>
## Deferred Ideas

- **NAME-F1** — renaming the `datasheets/<hex>-<NAME>/` folder slugs to match the new
  vocabulary. Deferred (avoids folder/provenance churn); Phase 103 records the divergence, it
  does not resolve it.
- **NAME-F2** — accepting a protocol name/alias as CLI input. Out of scope for v1.19; chip
  selection stays by part number (GATE-03).
- **Lockstep beta cut `3.0.0b11` + gitlink bump** — operator-gated standing policy; gitlinks
  remain PINNED. Not triggered by this docs-only phase.

</deferred>

---

*Phase: 103-docs-reconcile-prose-divergence-record*
*Context gathered: 2026-07-01*
