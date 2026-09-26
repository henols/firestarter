# Phase 103: DOCS — Reconcile Prose + Divergence Record - Research

**Researched:** 2026-07-01
**Domain:** Technical documentation reconciliation (Markdown prose + traceability matrix + GitHub-anchor discipline) over a single frozen work surface; milestone-close gate re-verification.
**Confidence:** HIGH

## Summary

Phase 103 is the **terminal, docs-only closing phase** of the v1.19 protocol-naming milestone. All upstream work is landed and verified: Phase 100 authored + operator-approved the 3-field name set (`PROTO_` token + display name + facet prose) and recorded it in `firestarter/doc/PROTOCOLS.md`; Phase 101 applied the tokens in firmware; Phase 102 consolidated the host display strings. Phase 103's job is to make the **prose** of PROTOCOLS.md (§1 four-facet bucket descriptions + §3 INV-01..09 matrix) coherent with the already-applied names, purge the residual minipro bucket-label jargon from the headings/prose (with three explicit locked retentions), record the name↔slug divergence in one place, and re-verify GATE-01/02/03 at close. There is **no firmware, host, DB, wire, or lockstep-constant change** in this phase — it is prose, anchors, and one new callout.

The single work surface is `firestarter/doc/PROTOCOLS.md` (425 lines, verified read in full). The canonical bucket-set table (§0, ~L30–57) and the handler-family table are **already** in final Phase-100 form and are NOT edited here — critically, the dispatch-mirror guard parses exactly those two tables and never reads the §1 headings or the §3 INV matrix, so the heading/anchor churn Phase 103 performs cannot break the guard (verified against the actual `_BUCKET_ROW_RE` regex). The one real completeness hazard is **anchor breakage**: renaming the twelve §1.x headings changes their GitHub auto-generated anchors, and eight `#1.x` fragment links in the §3 "Cross-links to per-bucket sections" list (lines 410–417) point at those anchors and must be regenerated in lockstep.

**Primary recommendation:** Edit PROTOCOLS.md in place with three grouped passes — (1) rename the twelve §1.x headings to the `PROTO_` token form and regenerate the eight §3 cross-link anchors in the same pass; (2) purge bucket-label jargon from facet prose respecting the three D-02 locked retentions (approved 0x06 name, frozen slug strings incl. citation paths, §2 minipro-provenance prose); (3) augment each INV row's behavior text with the `PROTO_` token beside the raw hex while keeping INV ids + handler-file names + native-test function names byte-identical. Then re-run the three gate checks (unchanged tools) and the dispatch-mirror guard, and do milestone-close housekeeping. No new packages, no external dependencies, no test framework work.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| §1 heading rename + facet-prose jargon purge (DOC-01) | Documentation (`firestarter/doc/PROTOCOLS.md`) | — | Pure prose/anchor edit; no code tier involved |
| §3 INV matrix token augmentation (DOC-01) | Documentation (same file) | — | Human-readable column only; INV ids / test names are a grep-contract, not code |
| Name↔slug divergence callout (DOC-02) | Documentation (same file) | — | New prose subsection; references frozen `datasheets/` slugs (read-only) |
| GATE-01 re-verify (dispatch behavior) | Firmware test (`pio test -e native`, golden traces) | Host guard (`test_dispatch_mirror.py`) | Verification only — Phase 103 asserts these stay green, does not modify them |
| GATE-02 re-verify (DB/wire identity) | Host tooling (`diff_db.py`, `check_dispatch.py`, constants-parity) | — | Verification only — no value change made |
| GATE-03 re-verify (CLI grammar) | Host CLI | — | Verification only — no grammar change made |
| Milestone close housekeeping | Planning (`STATE.md` / `PROJECT.md` / `MILESTONES.md`) | — | GSD close artifacts, not the sub-repo |

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01 — Rename all 12 §1 section headings** from the slug-jargon form (`### 1.1 — 0x05 FLASH-AMD-STD: …`, `EPROM-QUICK`, `FLASH-AMD-ALT`, `SRAM-STD`, …) to the new canonical display-name/token form (e.g. `### 1.1 — 0x05 PROTO_FLASH_5V_PAGE: 5V Page-Write Flash (EEPROM-like)`). **Then update every anchor that points at the old heading slugs** — the §3 "Cross-links to per-bucket sections" list. The frozen slug stays visible via the existing per-section "Folder slug (col 1):" line. **No broken anchors** is a hard completeness constraint — grep the doc for `#1` fragment links after the rename and confirm each resolves.

- **D-02 — Aggressive purge everywhere EXCEPT three locked/frozen retentions.** Scrub minipro/`AMD`/`QUICK`/`ALT` bucket-label jargon from all headings and facet prose — including behavior-prose mentions like "Unlike AMD flash …" (rephrase to a neutral descriptor) and any raw-hex-only bucket labels. **Retain verbatim, do NOT touch:**
  1. The approved 0x06 display name `Flash — AMD/SST unlock-sequence NOR` — Phase-100 operator-approved canonical name; changing it re-opens the naming gate.
  2. The frozen slug column strings (`0x05-FLASH-AMD-STD`, `0x06-FLASH-AMD-ALT`, `0x08-EPROM-QUICK`, …) — DOC-02 requires them retained; scrubbing them = NAME-F1 slug rename (deferred). This includes the `datasheets/<slug>/*.pdf` citation paths.
  3. §2 minipro-provenance prose (e.g. "`IC2_ALG_ITE` is an ITE EC label in minipro, NOT a memory algorithm") — this IS the honest-non-protocols heritage record. Leave §2's phantom/infeasible explanations intact.
  Datasheet-accurate terms that happen to contain "AMD" (e.g. "AMD unlock command addresses 0x5555/0x2AAA") are behavior-correct facts, not bucket jargon — keep them; only the *minipro bucket-label heritage* is the target.

- **D-03 — Add the PROTO_ token/name alongside the raw hex** in each INV row's one-line behavior text (e.g. "0x0B uses `FLAG_VPE_AS_VPP`…" → "`PROTO_EPROM_24PIN` (0x0B) uses `FLAG_VPE_AS_VPP`…"). The hex stays — it is the precise invariant/dispatch key. The `INV-0N` ids, owning-handler-file names, and native-test function names stay **byte-identical** (SAFE-02 grep-intact handoff). Also update the §3 cross-link anchor text to the renamed §1 headings (paired with D-01).

- **D-04 — Add a dedicated "Name ↔ Slug Divergence" callout** (short subsection) that states plainly: (a) the top bucket-set table's frozen-slug column is the canonical old-slug↔new-name map; (b) the `datasheets/` folder slugs are intentionally frozen and NOT renamed (NAME-F1 deferred); and (c) the **host uses ASCII-normalized dashes** (`—`/`–` → `-`) in its display strings — a documented punctuation deviation from the em-dash PROTOCOLS.md col-2 names (Phase 102 D-02).

- **D-05 — At close, re-verify GATE-01/02/03 and record the result:** golden register traces + dispatch-mirror guard green (GATE-01); `diff_db.py` identity + `check_dispatch.py` + constants-parity green, no DB/wire value change (GATE-02); CLI grammar unchanged (GATE-03). Re-run the dispatch-mirror guard after edits to confirm heading/anchor churn didn't break it.

### Claude's Discretion

- Exact heading wording (token-first vs. display-name-first vs. both), the precise placement and heading level of the D-04 divergence callout (near the top table vs. its own §), and the exact rephrasing of purged behavior-prose sentences — as long as D-01–D-04 hold and no anchor breaks.
- Plan/wave decomposition and milestone-close sequencing are the planner's call.

### Deferred Ideas (OUT OF SCOPE)

- **NAME-F1** — renaming the `datasheets/<hex>-<NAME>/` folder slugs to match the new vocabulary. Deferred (avoids folder/provenance churn); Phase 103 records the divergence, it does not resolve it.
- **NAME-F2** — accepting a protocol name/alias as CLI input. Out of scope for v1.19; chip selection stays by part number (GATE-03).
- **Lockstep beta cut `3.0.0b11` + gitlink bump** — operator-gated standing policy; gitlinks remain PINNED. Not triggered by this docs-only phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DOC-01 | `firestarter/doc/PROTOCOLS.md` prose (§1 four-facet bucket descriptions) and the INV-01..09 native-test traceability matrix reconciled to new names/tokens, no dangling minipro-heritage jargon | Full jargon inventory below (Common Pitfalls + State of the Art); heading-anchor map; INV-row augmentation pattern; the three D-02 locked retentions enumerated exactly |
| DOC-02 | Name↔`datasheets/<hex>-<NAME>/` slug divergence explicitly recorded (frozen slug column retained alongside new name); `datasheets/` folder slugs NOT renamed | Divergence-callout content (three facts a/b/c) grounded in the verified col-3 slug set + Phase-102 D-02 ASCII-dash deviation; frozen-slug preservation constraint enumerated |
| GATE-01 | Protocol numbers remain dispatch key; algorithm-first dispatch unchanged (golden traces + dispatch-mirror guard green) | Verified: dispatch-mirror parser reads only §0 two tables (not §1 headings/§3 matrix) → heading/anchor churn is provably guard-safe. Re-run commands below |
| GATE-02 | No `chip_database.json` / wire / lockstep-constant value change; `diff_db.py` identity, `check_dispatch.py`, constants-parity green | Verified: no code/DB touched this phase. Re-run commands below (identity expected) |
| GATE-03 | CLI grammar unchanged — chip selection stays by part number | Verified: no CLI code touched. No name/alias accepted as input |
</phase_requirements>

## Standard Stack

This is a documentation-editing phase over one Markdown file plus verification of existing Python/PlatformIO tooling. **No new libraries, no installs.** The "stack" is the existing toolchain used only for gate re-verification:

### Core (verification tooling — already present, not modified)
| Tool | Location | Purpose | Why Standard |
|------|----------|---------|--------------|
| `pytest` | `firestarter_app/tests/` | Runs `test_dispatch_mirror.py` + constants-parity | Existing project test framework [VERIFIED: files present] |
| `check_dispatch.py` | `firestarter_app/tools/check_dispatch.py` | GATE-01 dispatch-mirror check (host leg) | Existing v1.16 gate tool [VERIFIED: file present] |
| `diff_db.py` | `firestarter_app/tools/diff_db.py` | GATE-02 `chip_database.json` identity | Existing v1.16 gate tool [VERIFIED: file present] |
| `pio test -e native` | `firestarter/` | GATE-01 golden register traces + native dispatch suite | Existing native test env [CITED: firestarter/CLAUDE.md] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| In-place edit of PROTOCOLS.md | Rewrite the file wholesale | Rewrite risks touching the frozen §0 tables and losing byte-identity on the SAFE-02 grep contract; in-place grouped edits are safer and reviewable via git diff |

**Installation:** None. No package installs in this phase.

**Version verification:** N/A — no packages recommended.

## Package Legitimacy Audit

> Not applicable. This phase installs **no external packages** — it edits one Markdown file and re-runs existing tooling. No registry lookups performed.

## Architecture Patterns

### System Architecture Diagram — the v1.19 name-layer data flow (context, unchanged by Phase 103)

```
minipro protocol_id (upstream XML)
        │
        ▼
  chip_database.json (algorithm field)   ◄── GATE-02: value-frozen (diff_db.py identity)
        │
        ▼
   wire JSON  { "algorithm": <hex> }
        │
        ▼
  firmware dispatch  handle->protocol == PROTO_<NAME>   ◄── GATE-01: number is dispatch key
        │                                                    (PROTO_ token == raw hex value)
        ▼
   configure_*() handler  (eprom / sram / flash3 / flash4 / eeprom28c / flash_intel / not_implemented)

  Legibility layer (v1.19, applied — Phase 103 reconciles its DOCS face):
     PROTO_ token  ──► firmware constants (Phase 101, DONE)
     display name  ──► host CLI strings   (Phase 102, DONE, ASCII-dashed)
     facet prose   ──► PROTOCOLS.md §1     (Phase 103 — THIS PHASE)
     INV matrix    ──► PROTOCOLS.md §3     (Phase 103 — THIS PHASE)
     name↔slug     ──► PROTOCOLS.md callout (Phase 103 — THIS PHASE)
```

Phase 103 touches only the three bottom "PROTOCOLS.md" boxes. Everything above (DB, wire, firmware, host code) is frozen; the gates verify that freeze holds.

### Work-surface structure (the one file)

```
firestarter/doc/PROTOCOLS.md  (425 lines)
├── Header + reader-router          (L1–20)   #1/#2/#3 anchors → section headings NOT renamed (safe)
├── §0 Canonical bucket set table   (L22–45)  FROZEN — Phase 100 final; dispatch-mirror parses THIS. DO NOT EDIT
├── §0 Handler-family layer table   (L47–57)  FROZEN — dispatch-mirror parses THIS. DO NOT EDIT
├── §1 Real protocol buckets        (L61–333)
│   ├── §1.1 … §1.12 headings       ← D-01 RENAME (12 headings)
│   ├── per-section "Folder slug (col 1)" lines   ← D-02 RETAIN VERBATIM (frozen slug)
│   ├── per-section "Canonical name (col 2)" lines ← already PROTO_/display-name form
│   ├── four-facet prose            ← D-02 PURGE jargon (respect retentions)
│   └── Citation: datasheets/<slug>/*.pdf paths    ← D-02 RETAIN VERBATIM (frozen slug in path)
├── §2 Honest non-protocols         (L335–373) ← D-02 RETAIN §2 provenance prose (minipro heritage record)
└── §3 Invariant traceability matrix (L377–425)
    ├── INV-01..09 table            ← D-03 augment behavior col; INV ids + test names BYTE-IDENTICAL
    └── Cross-links to per-bucket sections (L410–417) ← D-01/D-03 REGENERATE 8 anchors
```

### Pattern 1: GitHub heading-anchor regeneration
**What:** GitHub auto-generates a heading fragment anchor by lowercasing the heading text, stripping punctuation that isn't alphanumeric/`-`/space, replacing spaces with `-`, and collapsing/preserving runs per its slugger. Renaming a heading changes its anchor.
**When to use:** Any time a §1.x heading text changes (all twelve, per D-01).
**Example (current → post-rename, illustrative):**
```
Heading:  ### 1.1 — 0x05 FLASH-AMD-STD: 5V Page-Write Flash (EEPROM-like)
Anchor:   #11----0x05-flash-amd-std-5v-page-write-flash-eeprom-like

Heading:  ### 1.1 — 0x05 PROTO_FLASH_5V_PAGE: 5V Page-Write Flash (EEPROM-like)
Anchor:   #11----0x05-proto_flash_5v_page-5v-page-write-flash-eeprom-like
```
Note: GitHub's slugger **keeps underscores** (they are word characters), lowercases letters, and drops the `#`/`:`/`(`/`)`. The em-dash `—` and the `.` in `1.1` are dropped; consecutive dropped chars leave the multi-hyphen runs seen in the current anchors. The planner/executor MUST regenerate each of the 8 cross-link anchors from the *actual final heading text* and grep-verify, not hand-guess. [VERIFIED: current anchors in doc match GitHub slugger output for current headings]

### Pattern 2: INV-row augmentation (token beside hex, ids frozen)
**What:** Prepend the `PROTO_` token (with hex in parens) to the human behavior text; leave the `INV id`, `Owning handler file`, `Planned native test function name`, and `Suite path` columns untouched.
**When to use:** All 9 INV rows.
**Example (D-03, illustrative):**
```
| INV-01 | 0x0B uses `FLAG_VPE_AS_VPP` direct-VPE rail … | eprom.cpp | test_inv01_eprom_0x0B_direct_vpe_rail | … |
                     ↓ augment behavior column only ↓
| INV-01 | `PROTO_EPROM_24PIN` (0x0B) uses `FLAG_VPE_AS_VPP` direct-VPE rail … | eprom.cpp | test_inv01_eprom_0x0B_direct_vpe_rail | … |
```

### Anti-Patterns to Avoid
- **Blind find/replace of `AMD`/`QUICK`/`ALT`:** hits the three locked retentions (approved 0x06 name, frozen slug strings incl. citation paths, §2 provenance). Use targeted, section-scoped edits.
- **Editing the §0 canonical bucket table or handler-family table:** these are Phase-100-final and are what the dispatch-mirror guard parses. Any edit here risks GATE-01. Phase 103 does not touch them.
- **Renaming or "fixing" a `datasheets/<slug>/` citation path:** that IS the NAME-F1 slug rename (deferred). The slug in the path is the provenance anchor.
- **Changing an INV id or native-test function name:** breaks the SAFE-02 grep contract (`grep -rn INV-04` must still hit the doc row + native test).
- **Guessing regenerated anchors:** always grep the doc for `](#1` after the rename and confirm each fragment resolves against a real heading.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Verifying dispatch didn't regress | A new ad-hoc doc-parse check | Existing `test_dispatch_mirror.py` + `check_dispatch.py` | They already parse the §0 tables and cross-check the firmware dispatch; re-run them |
| Verifying DB unchanged | Manual JSON diff | `diff_db.py` (identity check) | Purpose-built GATE-02 tool; expects byte-identity |
| Verifying anchor integrity | Eyeballing links | `grep -n "](#1" doc/PROTOCOLS.md` + confirm each target heading exists | Deterministic; the 8 cross-links are the only `#1.x` fragment links in the doc |

**Key insight:** every verification this phase needs already exists as a committed tool from v1.16/Phase 100/101. Phase 103 is a *consumer* of those gates, not an author of new ones.

## Runtime State Inventory

> This is a docs-refactor phase (heading rename + prose reconcile). The rename target is **documentation prose**, not stored/live/OS state, but the inventory is completed explicitly per protocol.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — the renamed strings are §1 heading text and facet prose in a Markdown file; no datastore keys/collections/user_ids reference §1 heading slugs. The `PROTO_` tokens are already applied in firmware constants (Phase 101) and are not stored as data. | None |
| Live service config | None — no external service (n8n/Datadog/etc.) references PROTOCOLS.md §1 headings. This is a firmware sub-repo doc. | None |
| OS-registered state | None — no OS task/service embeds a §1 heading string. | None |
| Secrets/env vars | None — no secret/env-var name references a protocol heading. | None |
| Build artifacts / cross-references | **In-doc anchors:** 8 `#1.x` fragment cross-links in §3 (L410–417) point at the §1.x heading anchors and go stale on heading rename → must regenerate (D-01). **Dispatch-mirror guard:** parses §0 tables only (verified `_BUCKET_ROW_RE` matches cols 6–7, treats slug col 3 + token col 4 as opaque `[^|]*`) → NOT affected by §1/§3 edits, but MUST be re-run to confirm (D-05). **`grep -rn INV-0N` contract:** external native-test function names must stay byte-identical (D-03). **`datasheets/<slug>/*.pdf` citation paths:** reference frozen folder names — retain verbatim (D-02). | Regenerate 8 anchors; re-run guard; keep INV ids + test names + slug paths byte-identical |

**The canonical question — "after the doc is updated, what still references the old strings?"** Answer: only the 8 in-doc §3 cross-link anchors (which this phase regenerates in lockstep), and — deliberately, by design — the frozen `datasheets/` slug strings + citation paths + §2 provenance prose, which are RETAINED verbatim (they are the divergence record, not stale references). The dispatch-mirror guard and the `grep INV-0N` contract are verified NOT to depend on any string this phase changes.

## Common Pitfalls

### Pitfall 1: Blind jargon find/replace hits a locked retention
**What goes wrong:** A `sed s/AMD//` or global replace of `QUICK`/`ALT` mutates (a) the operator-approved 0x06 display name `Flash — AMD/SST unlock-sequence NOR`, (b) frozen slug strings like `0x08-EPROM-QUICK` / `0x06-FLASH-AMD-ALT` including inside `datasheets/.../` citation paths, or (c) §2's `IC2_ALG_ITE`/minipro-heritage explanations.
**Why it happens:** The jargon-purge target ("minipro bucket-label heritage") shares substrings with three legitimate, must-keep strings.
**How to avoid:** Section-scoped, reviewed edits only. Before editing, enumerate the exact retention strings (see the verified inventory below) and confirm the diff does not touch them. Datasheet-accurate "AMD unlock command addresses 0x5555/0x2AAA" (§1.2 pin roles) is a KEEP.
**Warning signs:** A git diff that shows a change on any line containing a `datasheets/` path, the string `Flash — AMD/SST unlock-sequence NOR`, or any line in §2.

### Pitfall 2: Stale anchor after heading rename
**What goes wrong:** §1.x heading renamed but the §3 cross-link still points at the old anchor → dead in-page link on GitHub. D-01 makes "no broken anchors" a hard completeness constraint.
**Why it happens:** GitHub anchors are derived from heading text; the 8 cross-links (L410–417) hard-code the old derived anchors.
**How to avoid:** Rename heading + regenerate its cross-link anchor in the same edit pass; then `grep -n "](#1" doc/PROTOCOLS.md` and confirm each of the 8 fragments matches a real heading. The reader-router `#1`/`#2`/`#3` anchors (L16/18/19) point at the top-level section headings (`## 1. Real Protocol Buckets`, etc.) which are NOT renamed — leave them.
**Warning signs:** A cross-link fragment that no longer appears as a derivable anchor of any heading in the file.

### Pitfall 3: Accidentally editing the §0 tables and tripping the dispatch-mirror guard
**What goes wrong:** A well-meaning "consistency" edit to the §0 bucket table's slug or token column changes what `_BUCKET_ROW_RE` / `parse_protocols_md()` reads, failing `test_dispatch_mirror.py`.
**Why it happens:** The §0 table visually resembles the per-section col-1/col-2 lines, but only the §0 table is machine-parsed.
**How to avoid:** Treat §0 (both tables, L22–57) as read-only in Phase 103. The divergence-callout (D-04) *points at* the §0 slug column but does not edit it.
**Warning signs:** `test_dispatch_mirror.py` fails after edits, or a git diff shows changes between L22 and L57.

### Pitfall 4: Breaking the SAFE-02 grep contract in the INV matrix
**What goes wrong:** Augmenting INV rows accidentally rewrites an `INV-0N` id or a `test_invNN_*` function name → `grep -rn INV-04` no longer hits both the doc row and the native test.
**Why it happens:** D-03 augments the *behavior column*; the temptation is to "modernize" the whole row.
**How to avoid:** Only the one-line behavior text changes; the other four columns stay byte-identical. Confirm with `grep -rn INV-04 firestarter/` hitting doc + native test after the edit.
**Warning signs:** A diff touching the "Owning handler file", "Planned native test function name", or "Suite path" columns.

## Code Examples

### GATE re-verification commands (D-05) — run at close
```bash
# GATE-01 (host leg) + constants-parity, from firestarter_app/
cd firestarter_app
python -m pytest tests/test_dispatch_mirror.py -q      # dispatch-mirror guard (parses §0 tables)
python tools/check_dispatch.py                          # host dispatch mirror check
python -m pytest tests/ -k "parity" -q                  # constants.py <-> firestarter.h parity

# GATE-02 identity, from firestarter_app/
python tools/diff_db.py                                 # chip_database.json identity (expect no diff)

# GATE-01 (firmware leg) golden traces + native dispatch, from firestarter/
cd ../firestarter
pio test -e native                                      # native dispatch suite + golden register traces

# DOC-01 anchor integrity (from firestarter/)
grep -n "](#1" doc/PROTOCOLS.md                         # list all in-doc #1.x fragment links
# then confirm each fragment resolves to a real heading (regenerate any stale ones)

# DOC-02 / D-02 retention guard — confirm frozen strings untouched (from firestarter/)
grep -n "datasheets/0x" doc/PROTOCOLS.md                # citation paths must retain frozen slugs
grep -n "Flash — AMD/SST unlock-sequence NOR" doc/PROTOCOLS.md   # approved 0x06 name intact (1 hit expected in §1.2 col-2)
```
Source: commands assembled from `firestarter/CLAUDE.md` (pio test), CONTEXT.md canonical-refs, and verified tool locations. [VERIFIED: tool files present; commands mirror the gate surface named in CONTEXT.md]

## State of the Art — jargon inventory (what to reconcile vs. what to keep)

The following was **verified by grep** against the current PROTOCOLS.md. It is the authoritative purge-vs-retain map for DOC-01.

### PURGE (minipro bucket-label heritage in §1 headings + prose)
| Location | Current (old jargon) | Reconcile to |
|----------|----------------------|--------------|
| §1.1 heading (L67) | `### 1.1 — 0x05 FLASH-AMD-STD: 5V Page-Write Flash …` | `PROTO_FLASH_5V_PAGE` form |
| §1.2 heading (L87) | `### 1.2 — 0x06 FLASH-AMD-ALT: AMD/SST Unlock-Sequence NOR Flash` | `PROTO_FLASH_NOR_UNLOCK` form (keep approved display name in col-2 line) |
| §1.3 heading (L107) | `### 1.3 — 0x07 EPROM-STD: …` | `PROTO_EPROM_28PIN` form |
| §1.4 heading (L127) | `### 1.4 — 0x08 EPROM-QUICK: …` | `PROTO_EPROM_32PIN` form |
| §1.5 heading (L146) | `### 1.5 — 0x0B EPROM-LEGACY: …` | `PROTO_EPROM_24PIN` form |
| §1.6 heading (L165) | `### 1.6 — 0x0D EEPROM-POLL: …` | `PROTO_EEPROM_PARALLEL` form |
| §1.7 heading (L184) | `### 1.7 — 0x0E SRAM-32PIN: …` | `PROTO_SRAM_32PIN` form |
| §1.8 heading (L203) | `### 1.8 — 0x10 FLASH-INTEL: …` | `PROTO_FLASH_INTEL` form |
| §1.9 heading (L223) | `### 1.9 — 0x27 SRAM-24PIN: …` | `PROTO_SRAM_24PIN` form |
| §1.10 heading (L242) | `### 1.10 — 0x28 SRAM-STD: …` | `PROTO_SRAM_28PIN` form |
| §1.11 heading (L280) | `### 1.11 — 0x29 SRAM-512K-1M: …` | `PROTO_SRAM_32PIN_NVRAM` form |
| §1.12 heading (L298) | `### 1.12 — 0x34 EEPROM-X88C64: …` | `PROTO_EEPROM_8051BUS` form |
| §1.8 pin-roles prose (L219) | "**Unlike AMD flash**, there is no address-based unlock…" | Rephrase to neutral descriptor (e.g. "Unlike the unlock-sequence NOR path (0x06), …") — this is the explicit D-02 example |
| §2.1 prose (L352) | "These are not **FLASH-AMD-STD** variants, EPROM variants, …" | Rephrase — old raw bucket label in prose |
| §3 cross-links (L410–417) | 8 links with old heading anchors + old bucket-label link text | Regenerate anchor + update link text to renamed headings |
| §3 INV rows (L398–406) | Behavior text has raw hex only ("0x0B uses…", "0x08 routes…") | Prepend `PROTO_` token per D-03 |

### RETAIN VERBATIM (the three D-02 locked retentions — do NOT touch)
| Kind | Verified strings (grep-confirmed) |
|------|-----------------------------------|
| (1) Approved 0x06 display name | `Flash — AMD/SST unlock-sequence NOR` (§0 table L33 + §1.2 col-2 line L90) — em-dash, keep |
| (2) Frozen slug strings (col-1 lines + §0 table col-3 + citation paths) | `0x05-FLASH-AMD-STD`, `0x06-FLASH-AMD-ALT`, `0x07-EPROM-STD`, `0x08-EPROM-QUICK`, `0x0B-EPROM-LEGACY`, `0x0D-EEPROM-POLL`, `0x0E-SRAM-32PIN`, `0x10-FLASH-INTEL`, `0x27-SRAM-24PIN`, `0x28-SRAM-STD`, `0x29-SRAM-512K-1M`, `0x34-EEPROM-X88C64` — appear in each §1.x "Folder slug (col 1):" line AND inside every `datasheets/<slug>/*.pdf` citation path. All frozen. |
| (3) §2 minipro-provenance prose | `IC2_ALG_ITE` ITE-EC explanation (L349), `IC2_ALG_GAL*` rows (L367–369), the whole §2.1/§2.2 phantom+infeasible provenance text — retain. |

### KEEP (datasheet-accurate, not bucket jargon — verified)
| Location | String | Why keep |
|----------|--------|----------|
| §1.2 pin roles (L103) | "AMD unlock command addresses (0x5555/0x2AAA)" | Behavior-correct datasheet fact about the unlock cycle, not a bucket label |
| §1.4 write-algo (L135) | "AM27C020.pdf … §Quick-Pulse Programming" | "Quick-Pulse" is the datasheet's algorithm name, inside a citation |

**Deprecated/outdated:**
- The raw-hex-slug heading form (`0x05 FLASH-AMD-STD`) → replaced by `PROTO_` token form (this phase).
- Old `.planning/research/PROTOCOLS.md` speculation ("0x35 = AT29C series") is already retired in §2.1 (L353–355) — no action.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub's heading slugger keeps underscores (`_`) as word chars in the regenerated `PROTO_*` anchors | Architecture Pattern 1 | LOW — planner/executor is instructed to grep-verify each regenerated anchor against the real rendered heading, which catches any slugger nuance regardless of this assumption |
| A2 | The 0x34 host `description_points` bullet (`"XICOR 8051-multiplexed bus; not implemented on RURP (FUT-01)"`, flagged Phase-103-DOC-01-owned in Phase 102) is a **host-code** artifact in `ic_layout.py`, NOT part of the PROTOCOLS.md work surface | (informational) | LOW — DOC-01 scope is explicitly PROTOCOLS.md §1/§3 per CONTEXT.md; the host bullet is already reconciled prose that lives in code (GATE-03 surface). The planner may note it but it is not a required Phase-103 edit unless the operator scopes it in. Flagging so it is not silently dropped. |

**Note:** Both assumptions are LOW-risk and self-checking. No compliance/security/retention assumptions in this phase.

## Open Questions

1. **Is the 0x34 host `description_points` bullet in scope for Phase 103?**
   - What we know: Phase 102 chose a placeholder bullet in `ic_layout.py` and explicitly flagged it "Phase-103-DOC-01-owned" (verified in 102-01-SUMMARY.md L32/L137).
   - What's unclear: CONTEXT.md scopes DOC-01 to PROTOCOLS.md §1/§3 only; the host bullet lives in host code (a GATE-03 surface), not the doc.
   - Recommendation: Treat as out-of-scope for the PROTOCOLS.md deliverable (the bullet is already jargon-clean and honest). If the planner wants to honor the Phase-102 handoff, add it as a small optional task — but any edit to `ic_layout.py` must re-verify GATE-03 (no CLI-grammar change; this is a display string, so safe) and is NOT a DB/wire change. Flagging rather than silently dropping.

2. **Heading wording form (Claude's Discretion):** token-first (`PROTO_FLASH_5V_PAGE: 5V Page-Write Flash`) vs. display-name-first vs. both.
   - Recommendation: token-first matches the CONTEXT.md illustrative example (`### 1.1 — 0x05 PROTO_FLASH_5V_PAGE: 5V Page-Write Flash (EEPROM-like)`) and keeps the anchor grep-stable to the token. Planner's call.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `python` / `pytest` | GATE-01/02 host-leg re-verify | ✓ | 3.12 (devcontainer; CI target py3.11) | Record CI-PENDING/structurally-green per Phase-98 precedent if py3.11 absent |
| `pio` (PlatformIO) | GATE-01 firmware-leg golden traces (`pio test -e native`) | Assumed ✓ (used every firmware phase) | — | If native env unavailable in this session, record trace re-verify as deferred-to-CI with the last-known-green reference (v1.16 P89 golden traces) |
| `grep` | anchor + retention integrity checks | ✓ | — | — |
| `git` | diff review, milestone-close commits | ✓ | — | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** py3.11 (devcontainer is 3.12) — established precedent: run all CI-scoped checks under 3.12 and record py3.11 as CI-PENDING/structurally-green (Phase 98 precedent, per STATE.md). Note this is a docs-only phase, so no *new* code executes under either interpreter — the gates are pure re-verification of unchanged code.

## Validation Architecture

> `workflow.nyquist_validation` is **absent** from `.planning/config.json` → treated as enabled. However, this is a **docs-only phase**: it ships no new executable behavior. The "requirements → test map" therefore maps DOC/GATE requirements to *verification commands* (existing gates + grep integrity checks), not new unit tests. **No new test files are needed.**

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (host, `firestarter_app/tests/`) + PlatformIO Unity native (`firestarter/test/native/`) |
| Config file | `firestarter_app/` pytest config (existing); `firestarter/platformio.ini` `[env:native]` |
| Quick run command | `cd firestarter_app && python -m pytest tests/test_dispatch_mirror.py -q` |
| Full suite command | `cd firestarter_app && python -m pytest tests/ -q` ; `cd firestarter && pio test -e native` |

### Phase Requirements → Verification Map
| Req ID | Behavior | Verification Type | Automated Command | Exists? |
|--------|----------|-------------------|-------------------|---------|
| DOC-01 | No dangling minipro jargon; anchors resolve | doc integrity (grep) | `grep -n "](#1" doc/PROTOCOLS.md` + retention greps above | ✅ (grep) |
| DOC-02 | Divergence callout present; frozen slugs intact | doc integrity (grep + read) | `grep -n "datasheets/0x" doc/PROTOCOLS.md` (unchanged) | ✅ (grep) |
| GATE-01 | Dispatch behavior unchanged | existing gate | `pytest tests/test_dispatch_mirror.py -q`; `pio test -e native` | ✅ existing |
| GATE-02 | DB/wire/constants identity | existing gate | `python tools/diff_db.py`; `pytest -k parity` | ✅ existing |
| GATE-03 | CLI grammar unchanged | existing gate / no-op | (no CLI code touched) existing CLI grammar tests | ✅ existing |

### Sampling Rate
- **Per doc-edit commit:** targeted grep integrity checks on the edited section (anchors + retentions).
- **At close (phase gate):** full GATE-01/02/03 command set green + all 8 anchors resolve.

### Wave 0 Gaps
- None — existing test/gate infrastructure fully covers this docs-only phase. No new test files, no framework install.

## Security Domain

> `security_enforcement` is **absent** from `.planning/config.json` (treated as enabled by default), but this phase has **no security surface**: it edits Markdown prose and re-runs existing verification tooling. No auth, no input handling, no crypto, no data flow, no network. There is no attacker-reachable change.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | no | Phase adds no input path (GATE-03: no name accepted as CLI input) |
| V6 Cryptography | no | — |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| (none — docs-only, no runtime surface) | — | The v1.19 safety invariant (host `support_status` fail-closed + firmware `configure_not_implemented` 0xBB for unknown/PCB-blocked protocols) is UNCHANGED by this phase and re-verified via GATE-01. |

## Sources

### Primary (HIGH confidence)
- `firestarter/doc/PROTOCOLS.md` (read in full, 425 lines) — the work surface; §0 tables, §1.1–1.12 headings + facet prose, §2 provenance, §3 INV matrix + cross-links. [VERIFIED: Read tool]
- `firestarter_app/tests/test_dispatch_mirror.py` (`_BUCKET_ROW_RE`, `parse_protocols_md`) — confirmed parser reads §0 two tables only; §1/§3 edits are guard-safe. [VERIFIED: grep + sed]
- `firestarter/CLAUDE.md` — dispatch order, `PROTO_` token table, native test invocation. [VERIFIED: system context]
- `firestarter_app/firestarter/ic_layout.py` (`_PROTOCOL_DISPLAY_NAME`, L472–479) — ASCII-hyphen host display strings confirming the Phase-102 D-02 em-dash→ASCII deviation. [VERIFIED: grep]
- `.planning/phases/103-.../103-CONTEXT.md` — locked decisions D-01..D-05, retentions, deferrals. [VERIFIED: Read]
- `.planning/REQUIREMENTS.md` — DOC-01/DOC-02/GATE-01/02/03, NAME-F1/F2 deferrals. [VERIFIED: Read]
- `.planning/phases/102-.../102-01-SUMMARY.md` — 0x34 bullet Phase-103-DOC-01-owned handoff; D-02 dash deviation. [VERIFIED: grep]

### Secondary (MEDIUM confidence)
- GitHub heading-anchor slugger behavior — inferred from the current in-doc anchors matching current headings; planner instructed to grep-verify regenerated anchors regardless.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Work-surface state (what to edit / retain): HIGH — full file read + targeted greps confirm every heading, slug, citation path, and INV row.
- Gate safety (heading/anchor churn cannot break dispatch-mirror): HIGH — verified against the actual `_BUCKET_ROW_RE` regex and `parse_protocols_md` docstring (parses §0 tables, not §1/§3).
- Anchor regeneration mechanics: MEDIUM-HIGH — deterministic but slugger nuance handled by mandatory grep-verify step.
- Verification tooling: HIGH — all four gate tools confirmed present; commands mirror the CONTEXT.md gate surface.

**Research date:** 2026-07-01
**Valid until:** 2026-07-31 (stable — a frozen doc + existing tooling; only invalidated if the §0 tables or gate tools change, which nothing in this milestone will do)
