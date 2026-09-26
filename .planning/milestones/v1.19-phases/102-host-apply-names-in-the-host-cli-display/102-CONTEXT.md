# Phase 102: HOST — Apply Names in the Host CLI Display - Context

**Gathered:** 2026-07-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Consolidate the two divergent host protocol vocabularies (`ic_layout.proto_display`
and `protocol_info_data`) onto the Phase-100 canonical display names so
`firestarter info` / `list` / `search` render **one consistent name per protocol**.

Display-only change: the CLI grammar, the dispatch/lookup keys, and every
`chip_database.json` value stay untouched (GATE-03 primary, GATE-01/GATE-02
re-verified). No `PROTO_<NAME>` constants enter the host — Phase 101 D-02 keeps
those firmware-only.

</domain>

<decisions>
## Implementation Decisions

### Consolidation structure
- **D-01:** Extract a **single canonical `{protocol_id: display_name}` map** in the
  host (mirroring `firestarter/doc/PROTOCOLS.md` col-2), and have BOTH
  `proto_display` (in `get_chip_type_string`) and `protocol_info_data`'s name/type
  field draw from it. One edit point; structurally prevents future info-vs-list
  re-divergence (the recurring IN-01 class of bug). This is the code embodiment of
  HOST-01 "consolidate".

### Name string form
- **D-02:** Render the canonical names **ASCII-normalized** — the strings are the
  approved PROTOCOLS.md col-2 names, but em-dash `—` and en-dash `–` are normalized
  to ASCII `-` in the host source (e.g. `"Flash - 5V page-write (EEPROM-like)"`,
  `"EPROM - 24-pin legacy, 12-25V direct-VPE"`). Safest for any terminal / pipe /
  grep. This is a **defined, documented punctuation deviation** from col-2 — record
  it so Phase 103's divergence-record work is aware the host uses ASCII dashes.

### Description prose scope (102 vs 103 boundary)
- **D-03:** **Name-only.** Phase 102 fixes only the protocol NAME/type field.
  The 3 minipro-heritage `description_points` bullets in `protocol_info_data`
  (e.g. "Standard SRAM access protocols") are **left untouched** — prose
  reconciliation is Phase 103's job (DOC-01). Tightest scope, lowest risk. HOST-01
  is explicitly "one consistent *name*", not prose.

### Coverage reconciliation
- **D-04:** **Full reconcile** the host maps to the canonical 12-protocol DB set:
  - **Add `0x34`** (`PROTO_EEPROM_8051BUS` → "EEPROM - XICOR 8051-bus"), currently
    absent from BOTH maps though it has 1 DB chip (X88C64) that can surface in `info`.
  - **Drop `0x11`** from `protocol_info_data` — FWH, an infeasible bucket with zero
    chips in `chip_database.json`, minipro-heritage cruft.
  - **Keep phantoms `0x35`/`0x39` excluded** — host already routes them to
    `not_implemented` (excluded from `KNOWN_PROTOCOLS`, Phase 57 DEC-05); do NOT
    surface them as displayable protocols.

### Claude's Discretion
- The exact wording/placement of the canonical map (new module-level dict vs. a
  method) and whether the `Protocol: {type}` line shows the full canonical name or
  the name is just fed through the existing `type` slot — planner/executor's call,
  as long as D-01 (single source) and the canonical strings hold.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source of truth — canonical names (Phase 100, operator-approved)
- `firestarter/doc/PROTOCOLS.md` — the authoritative 3-field name set. **Col-2
  display names** are what this phase applies (table at lines ~30–45; per-bucket
  "Canonical name (col 2)" call-outs in §1.1–1.12). Operator-approved 2026-07-01.
  The host uses ASCII-normalized copies of these strings (D-02).

### Prior-phase decisions this phase conforms to
- `.planning/phases/101-fw-apply-names-in-firmware/101-CONTEXT.md` — D-02:
  `PROTO_<NAME>` constants stay **firmware-only**; host `constants.py` carries no
  protocol constants (parity + py3.11-CI trap). This phase does NOT change that.
- `firestarter/include/proto_constants.h` — the firmware token↔number pairing
  (reference for which number maps to which canonical family; do NOT mirror into host).

### Work surface (host sub-repo `firestarter_app/`)
- `firestarter_app/firestarter/ic_layout.py` — `proto_display` (~L216–234, inside
  `get_chip_type_string`) + `protocol_info_data` (~L261–370, inside
  `_get_protocol_info_structured`). Also `resolve_type_label` (~L483) and
  `_ELECTRICAL_TYPE_LABEL` for how the fallback path is wired.
- `firestarter_app/firestarter/eprom_info.py` — the presenter: `info` "Type:" line
  (~L253) and "Protocol: {type} (ID: …)" line + bullets (~L294–300); `list`/`search`
  table `type_str` column clamped to 12 chars (~L419).

### Gate / regression guards to keep green
- `firestarter_app/tools/diff_db.py` — chip_database.json identity (GATE-02).
- `firestarter_app/tools/check_dispatch.py` — dispatch mirror (GATE-01).
- `firestarter_app/tests/test_dispatch_mirror.py` — dispatch-mirror guard.
- `firestarter_app/tests/test_ic_layout.py` + `tests/__snapshots__/test_characterization.ambr`
  — string-coupled tests that will need updating for the new names.
- Host CI on the **py3.11** target (`ruff check` + `ruff format --check` + `mypy` +
  `pytest`) — validate against py3.11, not the devcontainer's py3.12.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `resolve_type_label` (ic_layout.py:480) is already the **single shared helper**
  for the info "Type:" line and the list/search Type column (the IN-01 fix). The new
  canonical map plugs into its `get_chip_type_string` fallback path cleanly.
- `_ELECTRICAL_TYPE_LABEL` — the electrical-type axis. It wins FIRST in
  `resolve_type_label`; `proto_display` is only the **fallback** for legacy
  user-override entries lacking `electrical.type`. So the canonical protocol NAME
  is most visible on the `info` command's `Protocol:` line, not the Type column.

### Established Patterns
- Two proto-keyed structures today diverge by construction; D-01's single map is the
  same anti-divergence pattern already applied to `resolve_type_label` (IN-01).
- Phantom exclusion is an established host convention (Phase 57 DEC-05, database.py:60):
  `0x35`/`0x39` are excluded from `KNOWN_PROTOCOLS` → `not_implemented`.

### Integration Points
- **12-char clamp interaction (eprom_info.py:419):** the list/search Type column
  truncates to 12 chars. Long canonical names only reach that column via the rare
  legacy-fallback path (entries without `electrical.type`); when they do they'll be
  truncated. Pre-existing behavior — no fix required, but planner should be aware and
  NOT widen the column (that would be a display-layout change beyond HOST-01).
- The `info` `Protocol:` line is unclamped, so full canonical names render fine there.

</code_context>

<specifics>
## Specific Ideas

- Canonical strings come verbatim from PROTOCOLS.md col-2 with only `—`/`–` → `-`
  (D-02). Examples of the applied set:
  - `0x05` → "Flash - 5V page-write (EEPROM-like)"
  - `0x06` → "Flash - AMD/SST unlock-sequence NOR"
  - `0x07` → "EPROM - 28-pin UV/EE, 13V VPP"
  - `0x08` → "EPROM - 32-pin UV/EE, 13V VPP"
  - `0x0B` → "EPROM - 24-pin legacy, 12-25V direct-VPE"
  - `0x0D` → "EEPROM - 5V parallel, SDP + DQ7 poll"
  - `0x0E` → "SRAM - 32-pin battery-backed NVRAM"
  - `0x10` → "Flash - Intel 28F command-register, 12V VPP mandatory"
  - `0x27` → "SRAM - 24-pin async, 5V"
  - `0x28` → "SRAM/FRAM - 28-pin"
  - `0x29` → "SRAM - 32-pin large battery-backed NVRAM, 512K-1M"
  - `0x34` → "EEPROM - XICOR 8051-bus" (newly added)

</specifics>

<deferred>
## Deferred Ideas

- **Description-bullet prose reconciliation** → Phase 103 (DOC-01). The stale
  `protocol_info_data` bullets stay as-is this phase (D-03).
- **Accept protocol name/alias as CLI input** → out of scope, NAME-F2 (v1.19 keeps
  chip selection by part number, GATE-03).

### Reviewed Todos (not folded)
- "Skip VPP error/warning checks when VPP is unused (reads/blank-checks)"
  (firmware, score 0.6) — firmware VPP behavior, unrelated to host display naming.
- "avrdude MCU-detection fallback for blank-chip / wrong-firmware recovery"
  (general, score 0.6) — recovery flow, unrelated to protocol naming.

</deferred>

---

*Phase: 102-host-apply-names-in-the-host-cli-display*
*Context gathered: 2026-07-01*
