# Phase 100: NAME — Canonical Protocol Name Set + Operator Approval - Pattern Map

**Mapped:** 2026-07-01
**Files analyzed:** 1 modified (`firestarter/doc/PROTOCOLS.md`) + 0 created
**Analogs found:** 1 / 1 (self-analog: revise-in-place)

> **Read this first.** Phase 100 is a naming/decision phase, **not** a code phase. There are
> **no new-code analogs to map** — no controllers, services, models, or handlers are created or
> edited. The single artifact modified is a Markdown document (`firestarter/doc/PROTOCOLS.md`),
> revised in place. The "pattern to copy from" is therefore **the document's own existing
> structure** — the operator approves a doc whose sections already exist and whose shape must be
> preserved. The code touchpoints below (`memory.cpp`, `ic_layout.py`) are **read-only grounding
> references** the executor consults to sanity-check names — they are NOT edited in Phase 100
> (that is Phases 101/102). This file is honest about that: it maps the doc-internal analog and
> the reference touchpoints rather than inventing code patterns that do not apply.

## File Classification

| Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---------------|------|-----------|----------------|---------------|
| `firestarter/doc/PROTOCOLS.md` | documentation (canonical vocabulary) | transform (relabel name columns in place) | **itself** — the existing §Canonical-bucket-set table + §1.x per-bucket headers | exact (self, revise-in-place per D-06) |

**No source-code files are created or modified in this phase.** The rows below under
"Reference Touchpoints (read-only)" are consulted for grounding only.

## Pattern Assignments

### `firestarter/doc/PROTOCOLS.md` (documentation, revise-in-place transform)

**Analog:** `firestarter/doc/PROTOCOLS.md` itself — the existing structure is the pattern the
in-place revision must conform to. The planner should have the executor **edit the existing
table/section rows, preserving everything not on the name axis**, rather than re-authoring the
doc.

The doc has four structural regions the revision touches differently. Copy each region's
existing shape:

**Region A — Canonical bucket set table (PRIMARY WORK SURFACE + the approval artifact).**
Existing shape (lines 22–35): a 5-column Markdown table
`hex | DB chip count | handler | datasheets folder (col 1) | algorithm-axis name (col 2)`.
Existing rows read like:

```markdown
| hex | DB chip count | handler | datasheets folder (col 1) | algorithm-axis name (col 2) |
|-----|--------------|---------|---------------------------|----------------------------|
| 0x05 | 27 | `flash_type_4.cpp` | `0x05-FLASH-AMD-STD` | FLASH-AMD-STD — 5V page-write flash (EEPROM-like) |
| 0x07 | 170 | `eprom.cpp` | `0x07-EPROM-STD` | EPROM-STD — 28-pin UV-EPROM / EE-EPROM, 13 V VPP |
```

**Pattern to apply (D-06/D-07/D-09):** expand the single "algorithm-axis name (col 2)" column
into the new 3-field set + handler-family, **keeping the frozen slug column verbatim** (the
DOC-02 divergence anchor) and keeping hex + chip count. Add two flagged phantom rows
(0x35/0x39, D-08). The revised table is the single reviewable operator-approval artifact — it
must render as one scannable Markdown table (all 12 real + 2 phantom = 14 rows). Illustrative
target shape (final strings settled at the gate):

```markdown
| hex | frozen slug (DOC-02 anchor) | PROTO_ token | display name | handler-family | phantom? |
|-----|----------------------------|--------------|--------------|----------------|----------|
| 0x05 | 0x05-FLASH-AMD-STD | PROTO_FLASH_5V_PAGE | Flash 5V page-write | flash4 (0x05) | no |
| 0x07 | 0x07-EPROM-STD | PROTO_EPROM_28PIN | UV/EE-EPROM 28-pin | eprom (0x07/08/0B) | no |
```

**Region B — §1.1–§1.12 per-bucket sections (PARTIAL CHANGE — name line only).**
Existing shape per bucket (e.g. lines 45–61 for §1.1): a header, then four labeled lines
(`**Folder slug (col 1):**`, `**Algorithm-axis name (col 2):**`, `**Handler:**`,
`**DB chip count:**`), then the four datasheet-cited facet paragraphs
(`**Write algorithm:**` / `**Erase model:**` / `**VPP behavior:**` / `**Pin roles:**`), each
with a `Citation:` line.

**Pattern to apply:** change ONLY the `**Algorithm-axis name (col 2):**` line per bucket to the
new `PROTO_` token + display name. **Preserve the four-facet prose verbatim** — it is field 3,
it is datasheet-cited, and re-organizing it is Phase 103 (DOC-01), not this phase. Preserve the
NAME-04 call-out blocks in §1.10 (FM1608, lines 236–254) and §1.12 (X88C64, lines 292–309)
exactly — carry the identity corrections forward, do not re-litigate.

**Region C — §2 Honest non-protocols (MOSTLY PRESERVE).**
Existing shape: §2.1 phantom table (lines 325–328) names 0x35 `FLASH_EEPROM` / 0x39
`FLASH_EEPROM2`; §2.2 infeasible table (lines 344–347) covers 0x11/0x2A/0x2B/0x2C.

**Pattern to apply:** give 0x35/0x39 their flagged `PROTO_PHANTOM_*` tokens (D-08) so §2.1 and
the new Region-A table agree; **leave §2.2 infeasible buckets unchanged** (out of scope — not in
the DB). Do NOT alias phantoms to the 0x05 family name.

**Region D — §3 INV-01..09 matrix + footer (PRESERVE UNCHANGED / footer CHANGE).**
Existing shape: the INV matrix (lines 374–384) plus its SAFE-02 handoff prose and per-INV suite
paths, then the cross-links (lines 388–395) and the footer provenance block (lines 399–402).

**Pattern to apply:** **PRESERVE the INV matrix verbatim** — reconciling it to new names is
Phase 103 (DOC-01), and touching it here risks the grep-intact SAFE-02 contract. Update only
the footer: add a Phase-100 revision line mirroring the existing provenance-line style
(`*Phase 87 — Naming + Documentation Pass | Authored 2026-06-26*`) noting the name-set revision
+ operator-approval date.

---

## Shared Patterns

Cross-cutting patterns that apply across the whole revision.

### Frozen-slug divergence record (DOC-02)
**Source (pattern-in-doc):** the `datasheets folder (col 1)` column, `firestarter/doc/PROTOCOLS.md`
lines 22–35 (table) and the per-bucket `**Folder slug (col 1):**` lines in §1.x.
**Apply to:** Region A table + every §1.x header.
**Rule:** the frozen `0x<hex>-<NAME>/` slug column stays **verbatim** next to the new name. The
mismatch between old-slug and new-name IS the DOC-02 record (D-07). Never `git mv` under
`datasheets/` (NAME-F1 deferred). All 12 slug folders verified present under `/workspaces/datasheets/`.

### Datasheet-cited facet prose is field 3 (preserve verbatim)
**Source:** the `**Write algorithm:** … Citation: datasheets/<slug>/<file>.pdf p.N §…` blocks
throughout §1 (e.g. lines 52–61).
**Apply to:** all §1.x buckets.
**Rule:** field 3 (facet prose) is a **re-org/relabel of existing content, not new research**
(~80% of the phase content already exists). Do not rewrite the facets; do not drop hazard
signals (12V-VPP for 0x07/0x08/0x10 lives in the VPP-behavior facet and must survive).

### Blocking human-verify approval gate (NAME-02 — no silent auto-approval)
**Source (process pattern, not a doc region):** RESEARCH.md §Pattern 2 + the requirement text.
**Apply to:** the plan itself — a `checkpoint:human-verify` task that BLOCKS commit-as-authoritative
until the operator explicitly approves the rendered Region-A table AND resolves the 0x0E/0x29
tiebreak. This mirrors the operator-gate convention used across this project's milestones
(operator has final say; nothing is auto-approved). No code excerpt — it is a plan structure.

---

## Reference Touchpoints (read-only — NOT edited in Phase 100)

These are the downstream consumers the name set must serve. The executor **reads** them to
sanity-check that the proposed names are feasible/complete; **no edits happen here in Phase 100**
(that is Phases 101/102). Exact locations for citation:

### Firmware dispatch chain (name feasibility — Phase 101 consumer, FW-01/02/03)
**File:** `firestarter/src/proms/memory.cpp`, `configure_memory()` dispatch, lines **107–167**.
The many-to-one groupings that fix the handler-family layer (D-09) are literally these raw-hex
`if` arms:
- line 122 — `handle->protocol == 0x05 || handle->protocol == 0x35 || handle->protocol == 0x39` → `configure_flash4()` (the phantom arm D-08 relabels honestly in Phase 101).
- line 127 — `0x07 || 0x08 || 0x0B` → `configure_eprom()` (one EPROM handler).
- lines 132–133 — `0x0E || 0x27 || 0x28 || 0x29` → `configure_sram()` (one SRAM handler; the 0x0E/0x29 D-05 collision lives here).
- lines 107/112/117 — single-protocol arms `0x10`/`0x0D`/`0x06`.
**Feasibility fact (verified):** NO `PROTO_<NAME>` token or protocol-id enum exists in the
firmware today — protocol ids are raw hex literals. The proposed `PROTO_` tokens are greenfield
and collide with nothing. `messages.h` `DBG_CONFIGURING_*` codes are a separate namespace.

### Host display maps (display-name reconciliation — Phase 102 consumer, HOST-01)
**File:** `firestarter_app/firestarter/ic_layout.py`.
- `proto_display` dict — lines **216–232** (inside `get_chip_type_string`): 11 entries, **MISSING 0x34**; phantoms intentionally removed (Phase 57 DEC-05).
- `_get_protocol_info_structured.protocol_info_data` list — starts line **261**: 12 entries but includes **0x11 (infeasible non-protocol)** and also **MISSING 0x34**.
**Implication for the name set:** the canonical display names authored here MUST include **0x34**
(so Phase 102 can add it) and MUST NOT introduce a real display name for 0x11 (it belongs in
§2.2). `firestarter_app/firestarter/eprom_info.py` is the presenter consuming these specs
(Phase 102 touch point, not Phase 100).

### Datasheet slugs (frozen provenance anchor)
**Dir:** `/workspaces/datasheets/` — all 12 `0x<hex>-<NAME>/` folders present (verified). Frozen
(NAME-F1). This is the col-1 divergence anchor, never renamed.

## No Analog Found

No new-code files are created in this phase, so there is nothing in the "file with no codebase
analog" sense. The one modified file is its own analog (revise-in-place). For completeness:

| Item | Role | Data Flow | Reason no code-analog applies |
|------|------|-----------|-------------------------------|
| The `PROTO_<NAME>` C tokens | (firmware constants) | n/a | Greenfield — defined in Phase 101, not here. Phase 100 only fixes the token *strings* in the doc; no `#define` exists to copy from. |
| Handler-family name layer | (doc column) | n/a | Names existing `configure_*` groupings from `memory.cpp` dispatch (read-only grounding); no code pattern to copy — the doc records the names for Phase 101's FW-03 renames. |

## Metadata

**Analog search scope:** `firestarter/doc/PROTOCOLS.md` (full read); grounding reads of
`firestarter/src/proms/memory.cpp` (dispatch chain), `firestarter_app/firestarter/ic_layout.py`
(two host maps), `firestarter/CLAUDE.md` (dispatch-order + handler table), `/workspaces/datasheets/`.
**Files scanned:** 4 read + 1 dir listing (from RESEARCH.md `[VERIFIED]` set).
**Pattern extraction date:** 2026-07-01
