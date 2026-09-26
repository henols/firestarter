# Phase 102: HOST — Apply Names in the Host CLI Display - Research

**Researched:** 2026-07-01
**Domain:** Python host CLI display-layer refactor (protocol-name consolidation) — `firestarter_app/`
**Confidence:** HIGH (all findings verified against live source in this session)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Extract a **single canonical `{protocol_id: display_name}` map** in the host (mirroring `firestarter/doc/PROTOCOLS.md` col-2). BOTH `proto_display` (in `get_chip_type_string`) and `protocol_info_data`'s name/type field draw from it. One edit point; structurally prevents future info-vs-list re-divergence (IN-01 class). Code embodiment of HOST-01 "consolidate".
- **D-02:** Render canonical names **ASCII-normalized** — the approved PROTOCOLS.md col-2 names, but em-dash `—` and en-dash `–` normalized to ASCII `-` in host source (e.g. `"Flash - 5V page-write (EEPROM-like)"`, `"EPROM - 24-pin legacy, 12-25V direct-VPE"`). A **defined, documented punctuation deviation** from col-2 — Phase 103 must record that the host uses ASCII dashes.
- **D-03:** **Name-only.** Phase 102 fixes only the protocol NAME/type field. The 3 minipro-heritage `description_points` bullets in `protocol_info_data` are **left untouched** — prose reconciliation is Phase 103 (DOC-01).
- **D-04:** **Full reconcile** the host maps to the canonical 12-protocol DB set:
  - **Add `0x34`** (`PROTO_EEPROM_8051BUS` → "EEPROM - XICOR 8051-bus") — currently absent from BOTH maps though it has 1 DB chip (X88C64) that can surface in `info`.
  - **Drop `0x11`** from `protocol_info_data` — FWH, infeasible, zero DB chips, minipro-heritage cruft.
  - **Keep phantoms `0x35`/`0x39` excluded** — host already routes them to `not_implemented` (excluded from `KNOWN_PROTOCOLS`, Phase 57 DEC-05); do NOT surface them as displayable protocols.

### Claude's Discretion
- The exact wording/placement of the canonical map (new module-level dict vs. a method) and whether the `Protocol: {type}` line shows the full canonical name or the name is fed through the existing `type` slot — planner/executor's call, as long as D-01 (single source) and the canonical strings hold.

### Deferred Ideas (OUT OF SCOPE)
- **Description-bullet prose reconciliation** → Phase 103 (DOC-01). The stale `protocol_info_data` bullets stay as-is this phase (D-03).
- **Accept protocol name/alias as CLI input** → out of scope, NAME-F2 (v1.19 keeps chip selection by part number, GATE-03).
- Reviewed-not-folded todos: "Skip VPP checks when VPP unused" (firmware); "avrdude MCU-detection fallback" (recovery flow). Both unrelated to host display naming.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HOST-01 | Consolidate `ic_layout.proto_display` + `protocol_info_data` onto canonical display names so `info`/`list`/`search` render one consistent name per protocol. | §1 (current-state inventory of both maps + divergence proof), §2 (canonical strings cross-checked vs PROTOCOLS.md col-2), §3 (presenter consumption — only `info` Protocol line changes). |
| GATE-03 (primary) | CLI grammar unchanged — chip selection by part number; no protocol name/alias accepted as CLI input. | §4 (no CLI-parser/grammar surface touched — change is confined to display maps in `ic_layout.py`). |
| GATE-01 (re-verify) | Numbers stay the dispatch key; no name/token becomes a lookup/dispatch key. | §4 (`check_dispatch.py` + `test_dispatch_mirror.py` operate on numeric dispatch — display-only change cannot affect them; how to run). |
| GATE-02 (re-verify) | No `chip_database.json` value change. | §4 (`diff_db.py` identity gate; display maps are Python source, not DB — how to run). |
</phase_requirements>

## Summary

This is a tightly-scoped, low-risk display-layer edit inside a single file. All the hard decisions are locked in a highly detailed CONTEXT.md; the implementation surface is small and I verified every line against live source.

**The two divergent vocabularies both live in `firestarter_app/firestarter/ic_layout.py`:** `proto_display` (a dict literal inside `get_chip_type_string`, lines **216–232**) and `protocol_info_data` (a list-of-tuples inside `_get_protocol_info_structured`, lines **261–370**). They diverge by construction — e.g. protocol `0x07` is `"UV-EPROM / MTP-Flash (12V VPP)"` in the first map and `"EPROM/EEPROM"` in the second. D-01 replaces both value sources with one canonical `{protocol_id: display_name}` map.

**Crucially, the two maps have very different *display reach*, and this determines the blast radius.** `proto_display` is only the **fallback** path of `resolve_type_label` (ic_layout.py:480) — it fires only for legacy user-override DB entries that lack `electrical.type`. I verified **every chip in `chip_database.json` (746 chips, all 12 protocols) carries `electrical.type`**, so in normal operation the `proto_display` map's strings **never render** in the `Type:` line, the `list` Type column, or the `search` Type column — those all resolve via `_ELECTRICAL_TYPE_LABEL` (EEPROM/UV-EPROM/Flash/EEPROM/SRAM/FRAM). The **only rendered CLI surface that changes** is the `info` command's `Protocol: {type} (ID: …)` line (eprom_info.py:297), which is fed by `protocol_info_data`'s `type` field. This means exactly **one** string-coupled test breaks: the syrupy snapshot `test_info_known_chip` (W27C512, protocol 0x07, currently renders `Protocol: EPROM/EEPROM (ID: 0x07)`).

**Primary recommendation:** Add one module-level canonical `{int: str}` dict in `ic_layout.py` with the 12 ASCII-normalized D-01/D-02 strings; make `proto_display` (fallback path) and `protocol_info_data`'s `type` field both read from it; add `0x34`, drop `0x11`, keep `0x35`/`0x39` excluded (D-04); regenerate the single `test_info_known_chip` snapshot; re-run the three non-regression gates (they are numeric/DB-level and structurally cannot be affected by a display-only change). Validate ruff/mypy/pytest with the py3.9-target ruff config and py3.9 mypy config — the devcontainer only has python3.12, so treat CI sign-off as structurally-green per the established Phase 98 precedent.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Canonical protocol display-name storage | Host presentation-model (`ic_layout.py` `EpromSpecBuilder`) | — | Display names are host-only (Phase 101 D-02 keeps `PROTO_<NAME>` firmware-only); the spec-builder is where display strings are already curated. |
| Type-label resolution (info Type / list / search) | Host presentation-model (`resolve_type_label`) | electrical-type ground truth (DB) | Already the IN-01 single-source helper; electrical-type wins first, proto map is fallback only. |
| Rendering to console | Host presenter (`eprom_info.py` `EpromConsolePresenter` + `print_eprom_list_table`) | — | Presenter consumes the structured dict; only the `Protocol:` line reflects the changed field. |
| Dispatch / lookup keys | Firmware + host DB layer (numeric `algorithm`/`protocol-id`) | — | Untouched by this phase (GATE-01/03); numbers stay the dispatch key. |

## Standard Stack

No new packages. This is an in-repo edit of existing modules. Existing tooling only:

| Tool | Version (from pyproject.toml) | Purpose |
|------|-------------------------------|---------|
| ruff | `>=0.15.14` (target-version `py39`) | lint + format gate `[CITED: firestarter_app/pyproject.toml:65,92]` |
| mypy | `>=2.1.0` (python_version `3.9`) | type gate via `tools/check_mypy_watermark.py` `[CITED: pyproject.toml:66,111]` |
| pytest + syrupy | pytest (testpaths `tests`), `syrupy>=5.0` | test + snapshot gate `[CITED: pyproject.toml:63,88]` |

**No `## Package Legitimacy Audit` required** — this phase installs no external packages.

## Current State of the Two Vocabularies (VERIFIED — live source)

> All line numbers below read directly from `firestarter_app/firestarter/ic_layout.py` this session. **CONTEXT.md estimates were accurate; minor corrections noted.**

### Map A — `proto_display` (fallback path only)

Location: **`get_chip_type_string`, lines 216–232** (CONTEXT said ~216–234; the dict literal is 216–232, the `if protocol_id in proto_display` check is 233). `[VERIFIED: ic_layout.py:216-234]`

| protocol_id | Current string in `proto_display` |
|-------------|-----------------------------------|
| `0x05` | `Flash/EEPROM (5V, AMD-std)` |
| `0x06` | `Flash/EEPROM (5V, AMD-alt sector-erase)` |
| `0x07` | `UV-EPROM / MTP-Flash (12V VPP)` |
| `0x08` | `UV-EPROM (12V VPP, quick pulse)` |
| `0x0B` | `UV-EPROM (legacy 24-pin)` |
| `0x0D` | `EEPROM (5V parallel, 28C-family)` |
| `0x0E` | `SRAM (32-pin)` |
| `0x10` | `Flash (Intel 28F, 12V VPP)` |
| `0x27` | `SRAM (24-pin)` |
| `0x28` | `SRAM (28-pin)` |
| `0x29` | `SRAM/NVRAM (32-pin)` |
| `0x34` | **ABSENT** (D-04 adds it) |
| `0x35`/`0x39` | **ABSENT** (comment at 228–231 documents removal — keep excluded, D-04) |

Data shape: `dict[int, str]`. Non-match falls through to `type_map` (mem_type int → generic label) at line 235.

### Map B — `protocol_info_data` (the `info` `Protocol:` line source)

Location: **`_get_protocol_info_structured`, lines 261–370** (list literal); the lookup loop is 371–378. CONTEXT said ~261–370 — exact. `[VERIFIED: ic_layout.py:261-376]`

Data shape: `list[tuple[int, str, tuple[str,str,str]]]` — `(protocol_id, type_name, (bullet1, bullet2, bullet3))`. Returns `{"id_hex", "type", "description_points"}`.

| protocol_id | Current `type` (the field this phase changes) | 3 bullets (D-03: LEAVE UNTOUCHED) |
|-------------|----------------------------------------------|-----------------------------------|
| `0x05` | `EEPROM/Flash` | write-enable-sequence prose |
| `0x06` | `Flash Memory` | standard flash prose |
| `0x07` | `EPROM/EEPROM` | JEDEC 28-pin prose |
| `0x08` | `Large EPROM` | high-voltage 32-pin prose |
| `0x0B` | `Legacy EPROM/EEPROM` | older 24-pin prose |
| `0x0D` | `EEPROM` | large-EEPROM prose |
| `0x0E` | `SRAM` | battery-backup prose |
| `0x10` | `Flash Memory` | Intel-compatible prose |
| `0x11` | `Flash Memory` | **FWH prose — D-04: DROP this entire tuple** |
| `0x27` | `SRAM` | 24-pin SRAM prose |
| `0x28` | `SRAM` | 28-pin SRAM prose |
| `0x29` | `SRAM` | 32-pin SRAM prose |
| `0x34` | **ABSENT** (D-04 adds it) | — (D-03: name-only; add a name; leave bullets minimal or Phase-103-owned — see Open Question 1) |

### Divergence proof (why HOST-01 exists)

Same protocol, two different names — verified by reading both maps:

| protocol | Map A (`proto_display`) | Map B (`protocol_info_data.type`) | Canonical target (D-01) |
|----------|-------------------------|-----------------------------------|-------------------------|
| `0x05` | `Flash/EEPROM (5V, AMD-std)` | `EEPROM/Flash` | `Flash - 5V page-write (EEPROM-like)` |
| `0x07` | `UV-EPROM / MTP-Flash (12V VPP)` | `EPROM/EEPROM` | `EPROM - 28-pin UV/EE, 13V VPP` |
| `0x08` | `UV-EPROM (12V VPP, quick pulse)` | `Large EPROM` | `EPROM - 32-pin UV/EE, 13V VPP` |
| `0x0B` | `UV-EPROM (legacy 24-pin)` | `Legacy EPROM/EEPROM` | `EPROM - 24-pin legacy, 12-25V direct-VPE` |
| `0x0D` | `EEPROM (5V parallel, 28C-family)` | `EEPROM` | `EEPROM - 5V parallel, SDP + DQ7 poll` |
| `0x10` | `Flash (Intel 28F, 12V VPP)` | `Flash Memory` | `Flash - Intel 28F command-register, 12V VPP mandatory` |

### The shared helper the canonical map plugs into

- `resolve_type_label(electrical_type, type_int, protocol_id)` — **ic_layout.py:480** `[VERIFIED]`. Logic (lines 512–515): if `electrical_type` is in `_ELECTRICAL_TYPE_LABEL` → return that; **else** fall back to `get_chip_type_string(type_int, protocol_id)` (which consults `proto_display`).
- `_ELECTRICAL_TYPE_LABEL` — **ic_layout.py:472–481** `[VERIFIED]`. Keys: `EEPROM`, `Flash/EEPROM`, `FRAM`, `SRAM`, `UV-EPROM`. **This wins first.** So `proto_display` (Map A) is reached ONLY by legacy user-override entries lacking `electrical.type`.
- **Which path the canonical map must plug into for D-01's single source:** Both. Map A (`get_chip_type_string`/`proto_display`) and Map B (`_get_protocol_info_structured`/`protocol_info_data`) must read the same new canonical dict. `resolve_type_label` needs no signature change — it already routes to `get_chip_type_string`, which is where the D-01 map lands for the fallback path.

## Canonical Name Set (cross-checked vs PROTOCOLS.md col-2)

`firestarter/doc/PROTOCOLS.md` §1.1–1.12 + the header table (lines 32–43) are operator-approved 2026-07-01. I cross-checked all 12. The ASCII-normalized strings the planner should hard-code (D-02: `—`/`–` → `-`): `[VERIFIED: firestarter/doc/PROTOCOLS.md:32-43]`

| protocol_id | PROTOCOLS.md col-2 (verbatim) | ASCII-normalized host string (D-02) | CONTEXT §specifics match? |
|-------------|-------------------------------|-------------------------------------|---------------------------|
| `0x05` | Flash — 5V page-write (EEPROM-like) | `Flash - 5V page-write (EEPROM-like)` | ✅ |
| `0x06` | Flash — AMD/SST unlock-sequence NOR | `Flash - AMD/SST unlock-sequence NOR` | ✅ |
| `0x07` | EPROM — 28-pin UV/EE, 13V VPP | `EPROM - 28-pin UV/EE, 13V VPP` | ✅ |
| `0x08` | EPROM — 32-pin UV/EE, 13V VPP | `EPROM - 32-pin UV/EE, 13V VPP` | ✅ |
| `0x0B` | EPROM — 24-pin legacy, 12–25V direct-VPE | `EPROM - 24-pin legacy, 12-25V direct-VPE` | ✅ (note both `—` and `–` → `-`) |
| `0x0D` | EEPROM — 5V parallel, SDP + DQ7 poll | `EEPROM - 5V parallel, SDP + DQ7 poll` | ✅ |
| `0x0E` | SRAM — 32-pin battery-backed NVRAM | `SRAM - 32-pin battery-backed NVRAM` | ✅ |
| `0x10` | Flash — Intel 28F command-register, 12V VPP mandatory | `Flash - Intel 28F command-register, 12V VPP mandatory` | ✅ |
| `0x27` | SRAM — 24-pin async, 5V | `SRAM - 24-pin async, 5V` | ✅ |
| `0x28` | SRAM/FRAM — 28-pin | `SRAM/FRAM - 28-pin` | ✅ |
| `0x29` | SRAM — 32-pin large battery-backed NVRAM, 512K–1M | `SRAM - 32-pin large battery-backed NVRAM, 512K-1M` | ✅ (`–` → `-`) |
| `0x34` | EEPROM — XICOR 8051-bus … | `EEPROM - XICOR 8051-bus` | ✅ (newly added, D-04) |

**⚠ Divergence flags the planner must resolve (col-2 header table vs §1 per-bucket call-outs vs CONTEXT §specifics):** PROTOCOLS.md is internally inconsistent for a few buckets between its header table (lines 32–43) and its §1 per-bucket "Canonical name (col 2)" lines. CONTEXT §specifics picked the **header-table** form each time. Recommend the planner use the **header-table (lines 32–43) + CONTEXT §specifics** as authoritative (they agree), and note the §1 extra qualifiers are prose the host omits:
- `0x0E` §1.7 line 187 adds `, optional 12V write-protect bypass`; header/CONTEXT do not. → use header form.
- `0x0D` §1.6 line 168 says `DQ7 page poll`; header line 37 + CONTEXT say `DQ7 poll`. → use `DQ7 poll` (CONTEXT §specifics).
- `0x0B` header line 36 says `12–25V direct-VPE`; §1.5 line 149 says `12–25V direct-VPE rail`. CONTEXT §specifics = `12-25V direct-VPE`. → use CONTEXT form (no "rail").
- `0x34` header line 43 says `EEPROM — XICOR 8051-bus, PCB-blocked (FUT-01) …`; §1.12 line 301 says `EEPROM — XICOR 8051-bus (PCB-blocked, document-only)`; CONTEXT §specifics = `EEPROM - XICOR 8051-bus`. → use the short CONTEXT form (`EEPROM - XICOR 8051-bus`) for the display name; the PCB-blocked status is already surfaced via `support_status: protocol-not-implemented`, so the display name should stay short.

### Coverage reconciliation confirmed against the live DB (D-04)

I enumerated `chip_database.json` algorithm counts this session `[VERIFIED: chip_database.json]`:

- Present (all 12 canonical): `0x05`(27), `0x06`(190), `0x07`(170), `0x08`(127), `0x0B`(32), `0x0D`(84), `0x0E`(20), `0x10`(39), `0x27`(2), `0x28`(34), `0x29`(20), `0x34`(1 — X88C64).
- **Absent from DB:** `0x11`, `0x35`, `0x39`. → confirms D-04: `0x34` must be added (it has a real chip that can reach `info`), `0x11` is safe to drop (zero chips), phantoms stay excluded.
- `KNOWN_PROTOCOLS`/`_ALGO_MEM_TYPE` in `database.py:33-65` `[VERIFIED]` already omits `0x35`/`0x39` (Phase 57 DEC-05, comment lines 60–64) and includes `0x34` in the abbreviation map at line ~ (SRAM_STD etc.). Phantom exclusion is an established host convention (`database.py:60`).

## Presenter Consumption (VERIFIED — `eprom_info.py`)

> All line numbers read live this session. **CONTEXT estimates were slightly off; corrected below.**

| Rendered line | Source field | Location | Changes this phase? |
|---------------|--------------|----------|---------------------|
| `Type: {type_str}` (info) | `resolve_type_label` → `_ELECTRICAL_TYPE_LABEL` first, `proto_display` fallback | **eprom_info.py:253** (CONTEXT ~253 ✅) | **NO** in practice — every DB chip has `electrical.type`, so it renders EEPROM/UV-EPROM/etc. Only a legacy user-override entry lacking `electrical.type` would reach the changed `proto_display` strings. |
| `Protocol: {type} (ID: {id_hex})` + 3 bullets | `protocol_info_data.type` + `description_points` | **eprom_info.py:294–300** (CONTEXT ~294–300 ✅) | **YES — this is the one visible change.** The `type` slot renders the canonical name; bullets stay stale (D-03). |
| `list`/`search` Type column (`type_str_display`, 12-char clamp) | `resolve_type_label` → electrical-type | **eprom_info.py:406–419** (CONTEXT said ~419 for the clamp — the `resolve_type_label` call is 406–410, the `[:12]` clamp is **419**) | **NO** — electrical-type path only; canonical `proto_display` strings are unreachable here for DB chips. |

**Confirmed reach:** The `list` and `search` snapshots (`test_list`, `test_search_w27`) render Type-column values exclusively from `_ELECTRICAL_TYPE_LABEL` (verified: 746 Type cells across the `test_list` snapshot are all EEPROM/UV-EPROM/Flash/EEPROM/SRAM/FRAM). **They will NOT change.**

**12-char clamp interaction (eprom_info.py:411–419):** The canonical names are 20–52 chars, far exceeding the 12-char Type column. But they only reach that column via the legacy-fallback path (no `electrical.type`), which no DB chip triggers. CONTEXT is correct: do NOT widen the column (that would be a layout change beyond HOST-01). The `info` `Protocol:` line is unclamped (free-form `logger.info` at eprom_info.py:297), so full canonical names render fine there. `[VERIFIED: eprom_info.py]`

## Test / Gate Impact

### The ONE string-coupled test that breaks

**`tests/__snapshots__/test_characterization.ambr` → `test_info_known_chip` (W27C512).** `[VERIFIED]` Current snapshot line **364**: `Protocol: EPROM/EEPROM (ID: 0x07)`. After the change this becomes `Protocol: EPROM - 28-pin UV/EE, 13V VPP (ID: 0x07)`. The 3 bullet lines (365–367) stay unchanged (D-03). Line **331** `Type: EEPROM` is electrical-type → **unchanged**.

- Regenerate with: `pytest tests/test_characterization.py::test_info_known_chip --snapshot-update` (syrupy). Then eyeball the diff to confirm ONLY the `Protocol:` line changed and the bullets/Type/VPP/etc. are byte-identical.
- ⚠ The `.ambr` is committed and characterization snapshots are byte-exact (GATE-1.8b lineage). Do not blanket `--snapshot-update` the whole file — scope to the one test, then diff.

### Tests that do NOT break (verified — no proto-display string coupling)

- `tests/test_ic_layout.py` `[VERIFIED — read in full]`: tests `_generate_pin_names_for_display` (crash class), `build_specifications` happy-path, and `_ELECTRICAL_TYPE_LABEL["FRAM"]`/`resolve_type_label("FRAM")`. **None assert on `proto_display` or `protocol_info_data` string values.** CONTEXT listed it as "will need updating" — **correction: it will NOT need updating** unless the planner adds new assertions (recommended: add a positive test — see below).
- `tests/test_list`, `test_search_w27` snapshots — electrical-type Type column only; unaffected.
- Grep for the current proto strings (`EEPROM/Flash`, `Large EPROM`, `EPROM/EEPROM`, `Standard SRAM access`, etc.) across `firestarter/`, `tests/`, `tools/`: the only *display-string* hits are `ic_layout.py` (source) and the `.ambr` snapshot. Other matches (`test_eprom_operations.py:980`, `test_database_conversion.py:226`, CLAUDE.md) are **prose/comments**, not assertions. `[VERIFIED via grep]`

**Recommended NEW test (D-01 anti-regression):** add a test asserting that for a representative protocol, `get_chip_type_string(_, pid)` (or the canonical map) and `_get_protocol_info_structured(pid)["type"]` return the **same** string — this pins the single-source invariant so the two maps can never re-diverge (the recurring IN-01 class). This is the code proof of HOST-01 "one consistent name".

### Non-regression gates (must stay green — display-only change cannot affect them)

| Gate | Tool / test | How to run | Why unaffected |
|------|-------------|-----------|----------------|
| GATE-02 | `tools/diff_db.py` + `tests/test_diff_db_gate.py` | `python3 tools/diff_db.py` (expect exit 0 + stdout `PASS: all`); or `pytest tests/test_diff_db_gate.py` | Operates on `chip_database.json` bytes; this phase edits Python source only. `[VERIFIED: test_diff_db_gate.py:52-61]` |
| GATE-01 | `tools/check_dispatch.py` + `tests/test_dispatch_mirror.py` + `tests/test_check_dispatch_invariants.py` | `python3 tools/check_dispatch.py`; `pytest tests/test_dispatch_mirror.py tests/test_check_dispatch_invariants.py` | Asserts numeric dispatch/routing invariants; display strings are not a dispatch or lookup key. |
| GATE-03 | (no dedicated tool — structural) | Verify no edit touches `main.py`/`cli_handlers.py` argument grammar | Change is confined to `ic_layout.py` display maps; no CLI-input parsing added (that would be NAME-F2, deferred). |

## CI Reality (py3.11 target vs devcontainer py3.12)

`[VERIFIED: .github/workflows/ci.yml, pyproject.toml]`

- **CI runs on Python 3.11** (`.github/workflows/ci.yml:29-32`, `python-version: '3.11'`). Gate step order: codegen drift `--check` (irrelevant here) → `ruff check firestarter/ tests/` → `ruff format --check firestarter/ tests/` → `python tools/check_mypy_watermark.py` → `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`.
- **ruff targets py39** (`pyproject.toml:92 target-version = "py39"`); **mypy targets 3.9** (`pyproject.toml:111 python_version = "3.9"`). So the *language-level* target is 3.9, executed on the 3.11 runner.
- **This devcontainer only has `python3` = 3.12.13** — no `python3.11` or `python3.9` binary (verified `which python3.11 python3.9` → none). Same environment as Phases 98/99.
- **Established precedent (Phase 98 Plan 03/05, STATE.md):** run all CI-scoped commands under 3.12 and treat sign-off as **CI-PENDING / structurally-green** — ruff/mypy-watermark/diff_db/check_dispatch/pytest all pass under 3.12.13; the real py3.11 gate runs in GitHub Actions on PR.
- **Verified this session:** `ruff check firestarter/ic_layout.py firestarter/eprom_info.py` → "All checks passed!" (clean baseline before edit).

### Known py3.12-masks-py3.11 traps (from prior-milestone memory)

- **f-string backslashes:** py3.12 relaxed the "no backslash in f-string expression" rule; py3.11 still rejects it. The canonical strings here contain **no backslashes** (only ASCII `-`, `/`, `+`, `,`, spaces) — safe. Do not introduce any `\` in an f-string.
- **ruff format stability:** the strings are plain dict/list literals; run `ruff format --check` locally after editing. A dict of 12 short string values formats deterministically.
- **`from __future__` / typing:** no new imports needed; the file already uses `Dict`/`List`/`Optional` with the `# noqa: UP035/UP006` markers ruff expects at py39 target — do not "modernize" them (that would trip the py39-target ruff rules).

## Recommended Implementation Shape (fits Claude's Discretion)

1. Add a module-level constant in `ic_layout.py` (near `_ELECTRICAL_TYPE_LABEL`), e.g.:
   ```python
   # Canonical protocol display names (D-01 single source). ASCII-normalized (D-02):
   # em/en dashes from firestarter/doc/PROTOCOLS.md col-2 rendered as '-'.
   _PROTOCOL_DISPLAY_NAME = {
       0x05: "Flash - 5V page-write (EEPROM-like)",
       0x06: "Flash - AMD/SST unlock-sequence NOR",
       0x07: "EPROM - 28-pin UV/EE, 13V VPP",
       0x08: "EPROM - 32-pin UV/EE, 13V VPP",
       0x0B: "EPROM - 24-pin legacy, 12-25V direct-VPE",
       0x0D: "EEPROM - 5V parallel, SDP + DQ7 poll",
       0x0E: "SRAM - 32-pin battery-backed NVRAM",
       0x10: "Flash - Intel 28F command-register, 12V VPP mandatory",
       0x27: "SRAM - 24-pin async, 5V",
       0x28: "SRAM/FRAM - 28-pin",
       0x29: "SRAM - 32-pin large battery-backed NVRAM, 512K-1M",
       0x34: "EEPROM - XICOR 8051-bus",
   }
   ```
2. In `get_chip_type_string`: replace the `proto_display` dict literal with a lookup into `_PROTOCOL_DISPLAY_NAME` (keep the `type_map` mem_type fallback and the `0x35`/`0x39` exclusion comment).
3. In `_get_protocol_info_structured`: change the tuple `type` field to read `_PROTOCOL_DISPLAY_NAME.get(pid, <old>)` (or restructure the list so the `type` is sourced from the map while the bullets stay literal per D-03). **Drop the `0x11` tuple. Add a `0x34` tuple** (name from map; for bullets, see Open Question 1).
4. Regenerate the single snapshot; add the D-01 same-name assertion test.
5. Run gates + CI-scoped commands under py3.12; record CI-PENDING per Phase 98 precedent.

## Common Pitfalls

### Pitfall 1: Blanket `--snapshot-update`
**What goes wrong:** Running `pytest --snapshot-update` across the whole suite silently rewrites unrelated snapshots (help text, list, search) if any incidental drift exists, masking real regressions and inflating the diff.
**How to avoid:** Scope to `test_characterization.py::test_info_known_chip`, then `git diff` the `.ambr` to confirm ONLY the `Protocol:` line changed.

### Pitfall 2: Assuming `list`/`search` render the canonical names
**What goes wrong:** Expecting the canonical names to appear in the Type column, then "fixing" the 12-char clamp or widening the column.
**How to avoid:** The Type column is fed by electrical-type (`_ELECTRICAL_TYPE_LABEL`), not the proto map. Every DB chip has `electrical.type`, so the canonical names only surface on the `info` `Protocol:` line. Do NOT touch the clamp or column widths (that exceeds HOST-01 and would break `test_list`/`test_search_w27`).

### Pitfall 3: Re-diverging the two maps
**What goes wrong:** Editing only `protocol_info_data` (the visible one) and leaving `proto_display` with old strings — re-creating the IN-01 divergence HOST-01 exists to kill.
**How to avoid:** D-01 mandates a single source. Add the same-name invariant test.

### Pitfall 4: Modernizing typing / introducing py3.12-only syntax
**What goes wrong:** ruff-target is py39 and CI is py3.11; py3.12-only constructs (relaxed f-string, `type` statement, etc.) pass locally on 3.12 but fail on 3.11.
**How to avoid:** No new syntax needed. Keep plain dict literals; run `ruff check` + `ruff format --check` locally; leave existing `# noqa: UP035/UP006` markers alone.

### Pitfall 5: Adding a `0x11`/phantom display entry "for completeness"
**What goes wrong:** Surfacing `0x11`/`0x35`/`0x39` as displayable protocols contradicts D-04 and the host's not-implemented routing.
**How to avoid:** Drop `0x11`; do not add `0x35`/`0x39`. Keep the exclusion comment.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| python3 | run tests/ruff/mypy | ✓ | 3.12.13 | — |
| python3.11 | exact CI-parity run | ✗ | — | Run under 3.12; treat as CI-PENDING/structurally-green (Phase 98 precedent) |
| python3.9 | ruff/mypy target-parity run | ✗ | — | ruff/mypy read target from pyproject; run under 3.12 |
| ruff | lint/format gate | ✓ (installed, checks pass) | `>=0.15.14` per pyproject | — |
| mypy | type gate | assumed installed via `.[test]` | `>=2.1.0` | watermark gate prints OK even if mypy missing — verify mypy is actually present (memory: hardened gate can mask absence) |
| pytest + syrupy | test/snapshot gate | assumed via `.[test]` | syrupy `>=5.0` | `pip install -e '.[test]'` from `/usr/local` python if toolchain wiped (memory) |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** py3.11/py3.9 binaries — use the established CI-PENDING sign-off.

## Validation Architecture

> `.planning/config.json` — `workflow.nyquist_validation` not confirmed disabled; section included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + syrupy (snapshot) `[CITED: pyproject.toml:63,88]` |
| Config file | `firestarter_app/pyproject.toml` (`[tool.pytest] testpaths = ["tests"]`) |
| Quick run command | `pytest tests/test_ic_layout.py tests/test_characterization.py::test_info_known_chip -x` |
| Full suite command | `pytest tests/ --cov=firestarter --cov-fail-under=70` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HOST-01 | `info` Protocol line renders canonical name for a known chip | snapshot | `pytest tests/test_characterization.py::test_info_known_chip -x` | ✅ (regenerate) |
| HOST-01 | Both maps return the SAME name per protocol (single source) | unit | new test in `tests/test_ic_layout.py` | ❌ Wave 0 (add) |
| HOST-01 | `0x34` renders a name; `0x11` no longer present | unit | new assertion in `tests/test_ic_layout.py` | ❌ Wave 0 (add) |
| GATE-02 | DB unchanged | integration | `pytest tests/test_diff_db_gate.py` | ✅ |
| GATE-01 | Dispatch mirror unchanged | integration | `pytest tests/test_dispatch_mirror.py tests/test_check_dispatch_invariants.py` | ✅ |
| GATE-03 | list/search Type column unchanged (no grammar/layout change) | snapshot | `pytest tests/test_characterization.py::test_list tests/test_characterization.py::test_search_w27` | ✅ (must stay byte-identical) |

### Sampling Rate
- **Per task commit:** `pytest tests/test_ic_layout.py tests/test_characterization.py -x`
- **Per wave merge:** `pytest tests/ --cov-fail-under=70` + `python3 tools/diff_db.py` + `python3 tools/check_dispatch.py`
- **Phase gate:** full suite green + ruff check + ruff format --check + mypy watermark, all under available python (CI-PENDING for py3.11).

### Wave 0 Gaps
- [ ] Add single-source invariant test to `tests/test_ic_layout.py` (same name from both maps).
- [ ] Add `0x34`-present / `0x11`-absent assertion to `tests/test_ic_layout.py`.
- [ ] (No framework install needed — pytest/syrupy already wired.)

## Security Domain

`security_enforcement` not explicitly disabled; assessed. This is a display-string change to a CLI that reads a local JSON DB and prints to a terminal.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | marginal | Canonical strings are hard-coded constants (not user/DB-derived); no injection surface. D-02 ASCII-normalization also removes non-ASCII terminal-rendering ambiguity — a mild robustness win. |
| V2/V3/V4/V6 | no | No auth/session/access-control/crypto surface in a display refactor. |

### Known Threat Patterns for host CLI display
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Terminal control-char injection via display strings | Tampering | Strings are static ASCII literals (D-02); no dynamic/user content in the name field. No mitigation work needed. |

**No security tasks required** — the change introduces no new trust boundary.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Two divergent proto-name maps (minipro heritage) | Single canonical `{id: name}` source (D-01) | Phase 102 (this) | Ends info-vs-list divergence (IN-01 class) |
| Non-ASCII em/en dashes in doc | ASCII-normalized in host (D-02) | Phase 102 | Terminal/pipe/grep safe; recorded for Phase 103 divergence log |

**Deprecated/outdated:**
- `protocol_info_data` `0x11` tuple (FWH) — zero DB chips, minipro cruft → dropped (D-04).
- `proto_display` strings (`"Large EPROM"`, `"EPROM/EEPROM"`, etc.) → superseded by canonical names.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Exact canonical wording for `0x0B`/`0x0D`/`0x34` follows CONTEXT §specifics + PROTOCOLS.md header table (not the §1 per-bucket variants which add qualifiers) | Canonical Name Set | Low — operator approved the set; if a variant is preferred, it's a one-string edit. Flagged as Open Question 2. |
| A2 | mypy is actually installed in this devcontainer (the watermark gate prints OK even when mypy is absent — prior-milestone memory) | Environment Availability | Low — verify `mypy --version` before trusting the type gate. |
| A3 | `nyquist_validation` is enabled (config not read in this session) | Validation Architecture | Low — section is additive; if disabled it's simply extra guidance. |

## Open Questions (RESOLVED)

> All three questions are resolved in PLAN `102-01` (see the plan's `<open_decision_for_executor>` block and constraint notes). Markers added post-plan-check (Dimension 11 hygiene).

1. **(RESOLVED — PLAN 102-01, D-05 / `<open_decision_for_executor>`)** **`0x34` (X88C64) `description_points` bullets.** D-03 says name-only, and D-04 adds `0x34` to `protocol_info_data`. A new tuple needs *a* bullet payload. PROTOCOLS.md §1.12 has rich prose, but D-03 defers prose to Phase 103.
   - What we know: name comes from the canonical map; X88C64 is `support_status: protocol-not-implemented` (surfaced separately in `info`).
   - What's unclear: whether to add empty/minimal bullets now or a placeholder.
   - Recommendation: add the `0x34` tuple with the canonical name and **minimal, non-minipro-heritage** bullets (e.g. a single "XICOR 8051-multiplexed bus; not implemented on RURP (FUT-01)") OR an empty bullet tuple — since Phase 103 owns prose reconciliation, minimize prose here. Planner should pick one and note it for Phase 103 (DOC-01).

2. **(RESOLVED — PLAN 102-01: "CONTEXT §specifics wins")** **Exact string form for `0x0B`/`0x0D`/`0x34`** where PROTOCOLS.md header table, §1 call-out, and CONTEXT §specifics differ slightly (see Canonical Name Set ⚠ block). Recommendation: use the CONTEXT §specifics forms verbatim (they are the operator-facing examples and agree with the header table modulo dashes).

3. **(RESOLVED — PLAN 102-01: leave the `[:12]` clamp untouched)** **Should `resolve_type_label`'s legacy fallback now render the long canonical name in the 12-char Type column** for user-override entries lacking `electrical.type`? Recommendation: leave the existing `[:12]` clamp untouched (pre-existing behavior, CONTEXT-confirmed). No DB chip triggers this path.

## Sources

### Primary (HIGH confidence)
- `firestarter_app/firestarter/ic_layout.py` (read in full) — both maps, `resolve_type_label`, `_ELECTRICAL_TYPE_LABEL`, exact line numbers.
- `firestarter_app/firestarter/eprom_info.py` (read in full) — presenter lines 253, 294–300, 406–419.
- `firestarter/doc/PROTOCOLS.md` (read in full) — canonical col-2 names, header table 32–43, §1.1–1.12.
- `firestarter_app/tests/__snapshots__/test_characterization.ambr` (relevant blocks) — `test_info_known_chip` line 364, `test_list`/`test_search_w27` Type columns.
- `firestarter_app/tests/test_ic_layout.py` (read in full), `tests/test_characterization.py` (structure), `tests/test_diff_db_gate.py`.
- `firestarter_app/firestarter/database.py:33-65` — `KNOWN_PROTOCOLS`/`_ALGO_MEM_TYPE`, phantom exclusion.
- `firestarter_app/.github/workflows/ci.yml`, `pyproject.toml` — CI py3.11, ruff py39, mypy 3.9.
- `chip_database.json` algorithm enumeration (this session) — 12 protocols present, 0x11/0x35/0x39 absent, all chips carry electrical.type.

### Secondary (MEDIUM confidence)
- CONTEXT.md, REQUIREMENTS.md, STATE.md (upstream decisions — treated as authoritative constraints).
- Prior-milestone MEMORY.md — py3.12-masks-py3.11 traps, mypy-watermark masking, `.[test]` restore.

### Tertiary (LOW confidence)
- None — no WebSearch used; entirely codebase-verified.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new deps; existing tooling read from pyproject/CI.
- Current-state inventory / divergence: HIGH — both maps read line-by-line from live source.
- Canonical name set: HIGH — cross-checked all 12 vs PROTOCOLS.md + CONTEXT; internal doc inconsistencies flagged with a recommended resolution.
- Presenter reach / blast radius: HIGH — verified via snapshot content + DB electrical.type coverage that only the `info` Protocol line changes.
- Test/gate impact: HIGH — grepped all display strings; confirmed exactly one snapshot breaks; gates are numeric/DB-level.

**Research date:** 2026-07-01
**Valid until:** 2026-07-31 (stable in-repo surface; re-verify line numbers if `ic_layout.py`/`eprom_info.py` change before planning)
