# Phase 2: Naming Cleanup (Wire Key + Minipro References) - Context

**Gathered:** 2026-05-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Mechanical naming cleanup across both sub-repos that removes two long-standing
semantic overloads from the v1.0 wire / data layer plus reduces minipro-tool
attribution to one load-bearing site:

1. **WIRE-01 — Atomic wire-key flip.** The host emitter
   (`firestarter_app/firestarter/database.py::convert_to_programmer`) currently
   emits BOTH `"vpp": <mV>` and `"vpp_mv": <mV>` (database.py:518 + :510). The
   firmware parser (`firestarter/src/json_parser.c:62, :74, :308-310`) reads
   ONLY `"vpp"`. After Phase 2: Python emits ONLY `"vpp_mv"`; firmware parses
   ONLY `"vpp_mv"`. No legacy fallback on either side. `firestarter_app/CLAUDE.md`
   wire example rewritten to drop `"vpp": 12000,`. Closes MILESTONES.md WARNING-3.

2. **WIRE-01 (internal twin) — `_map_data()` float-volts rename.** The internal
   dict produced by `database.py::_map_data` carries `"vpp": <float volts>` next
   to `"vpp_mv": <int mV>` (database.py:373-381, :387, :417-418, :510). The
   float-volts key is renamed to `"vpp_volts"` for symmetric naming with
   `vpp_mv` — same WARNING-3 root cause, internal-dict scope. The on-disk DB
   schema (`build_db.py:255-256` emits `"vpp": "12V"` string + `"vpp_mv": int`)
   is OUT OF SCOPE for the rename — see Deferred Ideas.

3. **WIRE-02 — Regression scan.** `firestarter_app/tools/check_dispatch.py`
   (Phase 12-built host-side scanner) runs end-to-end against the renamed DB
   on both Uno + Leonardo simulator path and confirms no `algorithm` regressing
   on the wire. Augmented with two new asserts per chip (`"vpp_mv" in wire` and
   `"vpp" not in wire`) — single-file change folded into the existing 743-chip
   iteration. Plus a `firestarter --help` + `firestarter info W27C512` CLI smoke
   (SC#5).

4. **CLEAN-01 — Data file rename.**
   `firestarter_app/firestarter/data/minipro_complete_db.json` →
   `firestarter_app/firestarter/data/chip_database.json` via `git mv` (preserves
   blame across the rename, mirrors Phase 11's `parse_db_2.py → build_db.py`
   pattern). All four reference sites flipped atomically: `tools/build_db.py:12`
   (`OUTPUT_FILE`), `firestarter/database.py:189` (default path) + `:366`
   (docstring), `tools/check_dispatch.py:2` (docstring) + `:27` (data-dir glob),
   plus the meta `CLAUDE.md:44` + `firestarter_app/CLAUDE.md:19,36,69` +
   `firestarter/CLAUDE.md:30` path references.

5. **CLEAN-02 — "minipro" attribution scrub.** Single attribution survives at
   `tools/build_db.py` (where `MINIPRO_XML_URL` is defined — the load-bearing
   upstream constant) plus one line in `firestarter_app/CLAUDE.md` naming the
   upstream source. All other mentions become neutral wording. `firestarter`
   firmware sub-repo drops to ZERO minipro mentions (it never sees the upstream
   tool).

**In scope:**
- Python emitter wire-key change: `database.py:518` (delete `"vpp": vpp_mv,`).
- Internal `_map_data()` dict rename: `database.py:373-387,417` (rename `"vpp"`
  float-volts key to `"vpp_volts"`); plus the consumer fallback at `:510`.
- Firmware parser key change: `firestarter/src/json_parser.c:62` PROGMEM literal
  + `:74` dispatch row + `:308-310` `get_vpp_mv` body. ALL THREE locations must
  flip together — see D-08 below.
- DB file rename via `git mv` + flip all 7 callsite paths and docstrings.
- `check_dispatch.py` augmentation: two new asserts inside the existing
  743-chip iteration.
- Doc updates: `firestarter_app/CLAUDE.md`, `firestarter/CLAUDE.md`, meta
  `CLAUDE.md`. Wire-JSON example drops the dual-key block to `vpp_mv` only.
- Comment scrub on `database.py:45,389`, `check_dispatch.py:30`,
  `firestarter/CLAUDE.md:30,69`, and 5 of 6 `firestarter_app/CLAUDE.md` mentions.

**Out of scope:**
- Backward-compat parsing of legacy `"vpp"` wire key in firmware (explicitly
  rejected — atomic flip per D-01). The legacy key is deleted from
  `json_parser.c` entirely.
- On-disk DB schema rename: `tools/build_db.py:255` emits `electrical.vpp = "12V"`
  (string) + `electrical.vpp_mv = 12000` (int). The on-disk schema is OUT of
  scope; only the in-memory `_map_data()` output dict is renamed. See Deferred
  Ideas for the on-disk drop candidate.
- Test-script fixes for `firestarter_test.sh:31` / `write_test.sh:17`
  `database_generated.json` references — explicitly owned by Phase 4 / HW-01.
- `~/.firestarter/database.json` user-override schema migration — handled
  organically by the retained `_map_data()` fallback at `database.py:373-387`
  (`electrical.get("vpp", "0").replace("V", "")` for legacy user-override
  upstream-schema strings). See D-07.
- Renaming `~/.firestarter/database.json` to `chip_database.json` — would break
  user installations silently. The user-override file keeps its name.
- Renaming `tools/infoic.xml` — that IS the minipro source file; the upstream
  filename is the load-bearing attribution.
- Renaming the firmware C struct field `firestarter_handle_t.vpp_mv`
  (`firestarter/include/firestarter.h:85`) — already correctly named since
  v1.0. Wire-key rename is parse-layer only.
- The `firestarter vpp` CLI subcommand (`firestarter_app/firestarter/main.py:185,626`)
  — same prefix, different concept (a CLI command name, not a wire key). Defer.
- Retroactive VERIFICATION.md artifacts for v1.0 phases 01-10 (Phase 3).
- Hardware validation on the renamed DB (Phase 4 / HW-02..05).

</domain>

<decisions>
## Implementation Decisions

### Wire-key transition policy

- **D-01:** **Atomic flip — firmware parser registers ONLY `"vpp_mv"`; Python
  emits ONLY `"vpp_mv"`.** No backward-compat fallback on either side.
  Rationale: the audit text and milestone goal call for closure, not a
  sustained dual-key window; Phase 4 hardware-test scripts will use the new
  key only — simpler test surface. User flashes matching firmware + app
  together; this is the documented upgrade path. The const
  `key_vpp[] PROGMEM = "vpp"` at `firestarter/src/json_parser.c:62` is renamed
  (literal AND variable) to `key_vpp_mv[] PROGMEM = "vpp_mv"`. The
  `key_parsers[]` row at `:74` flips to `{key_vpp_mv, get_vpp_mv}`. The
  `get_vpp_mv` body at `:308-310` flips its `extract_int("vpp", handle->vpp_mv)`
  arg to `extract_int("vpp_mv", handle->vpp_mv)`. **All three locations are a
  single atomic-flip unit — mismatch at any one of them silently breaks the
  parse (the field is dropped, `handle->vpp_mv` stays 0, the new SAF-04 VPP
  ADC compare then trips on every Intel-flash write).** See D-08 for macro
  semantics.

- **D-02:** **`convert_to_programmer` emits only `"vpp_mv"`.**
  `firestarter_app/firestarter/database.py:518` (`"vpp": vpp_mv,`) is **deleted**
  — the wire dict ships with `"vpp_mv": vpp_mv` only. Wire JSON shrinks by one
  key per command. The CLAUDE.md example wire JSON in
  `firestarter_app/CLAUDE.md:46-58` is rewritten to drop `"vpp": 12000,`
  (keeping `"vpp_mv": 12000,`).

- **D-03:** **No firmware C-struct rename.** `firestarter_handle_t.vpp_mv` at
  `firestarter/include/firestarter.h:85` already has the correct name. Out of
  scope. `bus_config.vpp_line` (different concept — pinout, not voltage) is
  also untouched. `get_vpp_pin` (`json_parser.c:503-497`) keys on `"vpp-pin"`
  — a separate field, not affected.

### Internal `_map_data()` rename

- **D-04:** **Rename internal `"vpp"` float-volts key to `"vpp_volts"` in
  `_map_data()` output dict.** Symmetric naming with `vpp_mv` removes the same
  WARNING-3 semantic overload internally. Touched lines:
  - `database.py:417` — `"vpp": vpp,` → `"vpp_volts": vpp,`
  - `database.py:510` — fallback `int(full_eprom_data.get("vpp", 0) * 1000)`
    → `int(full_eprom_data.get("vpp_volts", 0) * 1000)`
  - **Planner: grep for any callsite reading `full_eprom_data["vpp"]` /
    `.get("vpp")` (not `["vpp_mv"]`) — likely `eprom_info.py`, `ic_layout.py`
    — and update each.**

  **Distinction from upstream-schema read:** `database.py:373-381` reads
  `electrical.get("vpp", "0").replace("V", "")` from the on-disk DB / user
  override. That `electrical.vpp` field is upstream-schema-owned (the on-disk
  string `"12V"` shape produced by `build_db.py:255` and by legacy user
  overrides) — NOT renamed in this phase. The rename is purely the internal
  dict KEY `_map_data()` produces, not the upstream field it reads.

### Data file rename

- **D-05:** **New filename: `chip_database.json`.** Verbatim from REQUIREMENTS.md
  CLEAN-01 suggestion. Rhymes with `~/.firestarter/database.json` (user override)
  — reinforces the base + override symmetry. Rejected alternatives:
  - `chip_db.json` — less self-describing.
  - `firestarter_db.json` — redundant inside `firestarter/data/`.
  - `chips.json` — too generic; could collide with future per-family files.

- **D-06:** **Use `git mv` for the file rename inside the `firestarter_app/`
  sub-repo.** Preserves blame. Mirrors Phase 11's `git mv parse_db_2.py
  build_db.py`. The sub-repo is a separate git history from the meta-repo —
  the rename commit lands inside `firestarter_app/`; the meta-repo only sees a
  pointer-bump. Coordinate with the constant flip in `tools/build_db.py:12`
  and the reader in `database.py:189` so the file path is valid in every commit
  (stage all rename-related edits together; one commit).

- **D-07:** **Sweep all reader / writer / doc sites in one atomic plan
  boundary** (planner discretion to split into smaller commits within the plan):
  - `firestarter_app/tools/build_db.py:12` (`OUTPUT_FILE`)
  - `firestarter_app/firestarter/database.py:189` (default path) + `:366`
    (docstring `the new 'minipro_complete_db.json' format` → `the
    'chip_database.json' format`)
  - `firestarter_app/tools/check_dispatch.py:2` (docstring) + `:27` (data-dir
    glob list)
  - meta `CLAUDE.md:44`
  - `firestarter_app/CLAUDE.md:19` (data-flow diagram) + `:36` (Key Files
    bullet) + `:69` (Database Pipeline)
  - `firestarter/CLAUDE.md:30` (`regenerated minipro_complete_db.json`
    reference)

### User-override compatibility

- **D-08-compat:** **Loader stays tolerant on internal READ; wire is atomic.**
  `_map_data()`'s existing read chain
  (`electrical.get("vpp_mv", 0)` → `electrical.get("vpp", "0").replace("V", "")`)
  at `database.py:373-387` is **preserved unchanged** — this is the
  upstream-schema read path that also handles legacy user-override DBs at
  `~/.firestarter/database.json`. Net effect: users with legacy user-override
  DBs keep working internally; users with old firmware do not (because the
  wire is atomic). Acceptable — the upgrade story is "flash firmware + update
  app together" per D-01.

### Minipro attribution scrub

- **D-09:** **Single load-bearing attribution stays.** `tools/build_db.py:10`
  keeps the `MINIPRO_XML_URL` constant verbatim (it IS the upstream URL).
  `tools/build_db.py:23` (`# This map translates the numeric protocol ID from
  minipro's XML`) is reworded to `# This map translates the numeric protocol
  ID from upstream's XML` — one inline attribution near the URL is allowed
  per REQUIREMENTS.md CLEAN-02 (the variable name + comment together are one
  attribution).

- **D-10:** **Neutral wording table for the comment scrub** (verbatim diff
  targets for the planner; line numbers verified at planning time):

  | File:Line | Replace this exact string | With |
  |---|---|---|
  | `firestarter_app/firestarter/database.py:45` | `# Algorithm (minipro protocol_id) → firmware mem_type integer.` | `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.` |
  | `firestarter_app/firestarter/database.py:389` | `# Read algorithm integer directly — set by build_db.py as minipro protocol_id` | `# Read algorithm integer directly — set by build_db.py from upstream protocol_id` |
  | `firestarter_app/tools/check_dispatch.py:30` | `# Algorithm (minipro protocol_id) → firmware mem_type integer.` | `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.` |
  | `firestarter_app/tools/check_dispatch.py:2` (docstring) | `Regression scan: assert every chip in minipro_complete_db.json reaches a real …` | `Regression scan: assert every chip in chip_database.json reaches a real …` |

- **D-11:** **`firestarter/CLAUDE.md` reduces to zero minipro mentions.** The
  firmware never touches minipro. The two mentions at
  `firestarter/CLAUDE.md:30` (`minipro_complete_db.json` filename) and `:69`
  (`minipro protocol_id`) become `chip_database.json` and `upstream
  protocol_id` respectively.

- **D-12:** **`firestarter_app/CLAUDE.md` reduces to exactly 1 mention.** The
  attribution line at `:42` or `:69` (planner picks one; `:69` recommended
  since it is co-located with `infoic.xml` — the actual upstream file) keeps
  the word "minipro" since it's where readers naturally look for upstream
  provenance. Other mentions at `:19, :36, :42 (or :69), :46-58 (wire example),
  :72` become either the new filename (CLEAN-01) or neutral wording ("upstream
  chip XML" / "upstream protocol_id"). Net mentions: 6 → 1.

### Firmware parser semantics

- **D-08 (macro semantics):** **`extract_num` has implicit early returns.**
  `firestarter/src/json_parser.c:455-460`:

  ```c
  #define extract_num(element, register, type)           \
      if (jsoneq(json, &tokens[pos], element) == 0) {    \
          register = type(json + tokens[pos + 1].start); \
          return 1;                                      \
      }                                                  \
      return 0;
  ```

  The macro returns `1` on match (and writes the register) or `0` on no-match
  (without writing). It is a single-key probe. The first arg IS the parse key
  — confirmed against `jsoneq_` body at `:260-266` which compares the JSON
  token against the literal via `strncmp_P`. Two back-to-back `extract_int`
  calls in the same function body do NOT chain — the first one always returns.
  **Implication for D-01:** since we only need ONE key (`"vpp_mv"`), the
  single-line `extract_int("vpp_mv", handle->vpp_mv);` body is correct as-is.
  No macro change, no body refactor.

### Plan granularity

- **D-13:** **Split into 3 plans (planner's discretion to merge if friction):**
  - **Plan 02-01** — WIRE-01 atomic flip. Python emitter
    (`database.py::convert_to_programmer` delete `"vpp"` key) + firmware
    parser (`json_parser.c` literal + dispatch row + body) + wire-example
    update in `firestarter_app/CLAUDE.md`. Single conceptually-atomic change
    spanning both sub-repos. Recommended commit order: firmware first
    (existing wire still works with new firmware because Python is the only
    sender that emits this key, and the host-side hasn't shipped yet), then
    Python.
  - **Plan 02-02** — CLEAN-01 file rename (`git mv` + 7 callsite touches per
    D-07) plus internal `vpp_volts` rename (D-04). Larger blast radius but
    naturally atomic.
  - **Plan 02-03** — CLEAN-02 minipro attribution scrub (D-09/D-10/D-11/D-12)
    + WIRE-02 regression scan (D-15) + SC#5 CLI smoke (D-17). Doc / comment
    edits + the final regression evidence.

- **D-14:** **The audit text "atomic" refers to the four-rename batch landing
  before regression scan — not to a single git commit.** A 3-plan split with
  sequential commits inside the milestone slot is consistent with the
  requirement; Phase 1 used 2 plans, this phase has more file touches but
  mechanically simpler edits.

### Regression test approach

- **D-15:** **`check_dispatch.py` is the canonical regression scanner (SC#4),
  augmented with wire-key asserts.** Inside the existing 743-chip iteration
  loop, two new asserts after the dispatch resolution:

  ```python
  wire = db.convert_to_programmer(chip)
  if "vpp_mv" not in wire:
      print(f"WIRE-REGRESSION: {chip.get('part_number')} — missing vpp_mv")
      failures += 1
  if "vpp" in wire:
      print(f"WIRE-REGRESSION: {chip.get('part_number')} — legacy vpp key still emitted")
      failures += 1
  ```

  Existing `failures > 0 → exit 1` contract preserved. Both Uno + Leonardo
  simulator paths covered through the existing buffer-size fork in
  `check_dispatch.py`.

- **D-16:** **DB regeneration via `tools/build_db.py` is OPTIONAL.** SC#4 says
  "regenerates the DB and confirms all 743 chips still parse end-to-end" — the
  existing committed `minipro_complete_db.json` IS the regenerated artifact
  (last regenerated post-v1.0 / Phase 13). After the `git mv` it becomes the
  committed `chip_database.json`. Re-running `build_db.py` requires network
  access to fetch `infoic.xml` from upstream. The planner should fall back to
  "use the committed DB as the regenerated artifact" if the network call fails
  — phase output is byte-identical modulo the filename.

- **D-17:** **`firestarter info W27C512` smoke is the integration check (SC#5).**
  Loading the renamed DB via `EpromDatabase` and emitting `convert_to_programmer`
  JSON for one canonical chip (W27C512 — UV-EPROM 0x07) confirms:
  - The new filename loads (no `FileNotFoundError`).
  - The new wire emits `"vpp_mv"` only.
  - No stale-path warning.

  Plus a `firestarter --help` smoke (no DB load) to confirm the package still
  installs cleanly.

### Claude's Discretion

- Exact PROGMEM constant name (`key_vpp_mv` is the natural choice).
- Whether to neutralize `build_db.py:23` (`# This map translates the numeric
  protocol ID from minipro's XML`) further. D-09 keeps a softened form.
- Whether the meta `CLAUDE.md:44` edit lands in Plan 02-02 or Plan 02-03
  (both reasonable).
- Final wording of replacement comments (D-10 suggests one option; alternates
  like `upstream chip database protocol_id` are fine).
- Whether `firestarter info --adapter W27C512` (richer smoke) augments the
  basic `firestarter info W27C512`.
- Whether to add a Python-side `test_convert_to_programmer.py` unit test
  asserting the emitted wire dict — OPTIONAL; `check_dispatch.py` is the
  contract.
- Whether to update `firestarter/CLAUDE.md:51-58` field-list block to drop
  the `vpp /` legacy mention (implied by D-01 — recommended).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements + roadmap
- `.planning/REQUIREMENTS.md` §"Naming Cleanup" (lines 39-42) — WIRE-01 /
  WIRE-02 / CLEAN-01 / CLEAN-02 — the authoritative spec with verbatim
  file:line edit targets.
- `.planning/ROADMAP.md` §"Phase 2: Naming Cleanup (Wire Key + Minipro
  References)" — 5 success criteria; depends on nothing, ordered before
  Phase 4 so hardware scripts use the final wire format and DB filename.
- `.planning/MILESTONES.md` §"Known Gaps" — WARNING-3 (vpp wire-key semantic
  overload) — this phase closes it.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — WARNING-3 + WARNING-4
  full context (volts/mV overload origin).
- `.planning/PROJECT.md` "Key Decisions" — 2026-05-11 row on the `"vpp"` key
  carrying mV (status: ⚠ Revisit) — this phase resolves it.

### Codebase entry points — Python host (firestarter_app)
- `firestarter_app/firestarter/database.py:175-210` — `_initialize_database_core`
  (the DB filename reader; `_read_config_file("minipro_complete_db.json")` at
  `:189`).
- `firestarter_app/firestarter/database.py:362-440` — `_map_data` (internal
  `"vpp"` float-volts producer; `:373-381` parses `electrical.vpp` upstream
  string, `:387` reads `electrical.vpp_mv`, `:417-418` writes both `"vpp"`
  and `"vpp_mv"` into output dict).
- `firestarter_app/firestarter/database.py:501-540` — `convert_to_programmer`
  (WIRE emitter; `:510` fallback chain, `:518` `"vpp": vpp_mv` line to delete).
- `firestarter_app/firestarter/database.py:45` — `_ALGO_MEM_TYPE` header
  comment (CLEAN-02 D-10 edit).
- `firestarter_app/firestarter/database.py:366` — `_map_data` docstring
  referencing old filename (CLEAN-01 D-07 edit).
- `firestarter_app/firestarter/database.py:389` — algorithm-read comment
  (CLEAN-02 D-10 edit).
- `firestarter_app/tools/build_db.py:10` — `MINIPRO_XML_URL` constant —
  CLEAN-02 KEEPS this (load-bearing attribution).
- `firestarter_app/tools/build_db.py:12` — `OUTPUT_FILE` constant (CLEAN-01
  D-07 edit).
- `firestarter_app/tools/build_db.py:23` — minipro comment near the URL
  (D-09 soft-neutralize: "upstream's XML").
- `firestarter_app/tools/build_db.py:255-256` — on-disk DB emit: BOTH
  `"vpp": "12V"` (string) AND `"vpp_mv": int`. **NOT renamed in this phase**
  — the on-disk schema is upstream-owned; only the wire and the in-memory
  `_map_data()` output dict are renamed. See Deferred Ideas.
- `firestarter_app/tools/check_dispatch.py:2` — docstring referencing old
  DB name (CLEAN-01 + CLEAN-02 edits).
- `firestarter_app/tools/check_dispatch.py:27` — `_DATA_DIR` glob entry
  `"minipro_complete_db.json"` (CLEAN-01 D-07 edit).
- `firestarter_app/tools/check_dispatch.py:30` — `# Algorithm (minipro
  protocol_id) → …` comment (CLEAN-02 D-10 edit).

### Codebase entry points — Firmware (firestarter sub-repo)
- `firestarter/src/json_parser.c:20-21` — forward decls for `get_vpp_mv` /
  `get_vpp_pin`.
- `firestarter/src/json_parser.c:62` — `const char key_vpp[] PROGMEM = "vpp"`
  → rename to `key_vpp_mv[] PROGMEM = "vpp_mv"` (D-01).
- `firestarter/src/json_parser.c:164` — `key_parsers[]` dispatch row
  `{key_vpp, get_vpp_mv}` → `{key_vpp_mv, get_vpp_mv}` (D-01).
- `firestarter/src/json_parser.c:447-460` — `jsoneq_` + `extract_num` /
  `extract_long` / `extract_int` macros. **First arg IS the parse key (not a
  debug label).** Single-key probe with early return — see D-08.
- `firestarter/src/json_parser.c:503-497` — `get_vpp_mv` body:
  `extract_int("vpp", handle->vpp_mv);` → `extract_int("vpp_mv",
  handle->vpp_mv);` (D-01).
- `firestarter/src/json_parser.c:503-497` — `get_vpp_pin` keys on `"vpp-pin"`
  (separate field; **NOT in scope**).
- `firestarter/include/firestarter.h:85` — `uint16_t vpp_mv;` (C-struct field
  name; already correct, NOT renamed).

### Documentation entry points (all three CLAUDE.md files)
- `CLAUDE.md:44` (meta) — `minipro_complete_db.json` path reference (CLEAN-01).
- `firestarter_app/CLAUDE.md:19` — data-flow diagram (`infoic.xml → build_db.py
  → minipro_complete_db.json`); CLEAN-01 + CLEAN-02.
- `firestarter_app/CLAUDE.md:36` — Key Files list entry; CLEAN-01.
- `firestarter_app/CLAUDE.md:42` — build_db.py description ("parses minipro
  `infoic.xml`"); CLEAN-02 (one attribution survives — recommend this OR :69).
- `firestarter_app/CLAUDE.md:46-58` — wire JSON example with both `"vpp"` and
  `"vpp_mv"`; WIRE-01 drops `"vpp": 12000,`.
- `firestarter_app/CLAUDE.md:69` — database pipeline section; CLEAN-01 +
  CLEAN-02 (one attribution survives — recommend this OR :42).
- `firestarter_app/CLAUDE.md:72` — algorithm description with minipro mention;
  CLEAN-02.
- `firestarter/CLAUDE.md:30` — `regenerated minipro_complete_db.json` —
  CLEAN-01 (filename) + CLEAN-02 (zero firmware-side mentions per D-11).
- `firestarter/CLAUDE.md:51-58` — wire-protocol field list mentions `vpp /
  vpp_mv` — collapse to `vpp_mv` only (Claude's-discretion, implied by D-01).
- `firestarter/CLAUDE.md:69` — `minipro protocol_id` mention; CLEAN-02 → zero.

### Data file rename target
- `firestarter_app/firestarter/data/minipro_complete_db.json` → `git mv` →
  `firestarter_app/firestarter/data/chip_database.json` (743 entries; history
  preserved).

### Prior context
- `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-CONTEXT.md`
  §Out of scope — confirms "Replacing the v1.0 vpp JSON wire key with vpp_mv
  is Phase 2 / WIRE-01" — phase boundary locked at milestone start.
- `.planning/milestones/v1.0-phases/01-database-pipeline-fix/` — phase that
  established the `convert_to_programmer` emission shape.
- `.planning/milestones/v1.0-phases/02-firmware-json-protocol-extension/` —
  phase that built `json_parser.c` + the PROGMEM key table convention.
- `.planning/milestones/v1.0-phases/11-database-pipeline-cleanup/` — phase
  that consolidated `parse_db_2.py → build_db.py` but deliberately did NOT
  rename the output JSON (deferred to Phase 2 / CLEAN-01) and established the
  `git mv` history-preserving rename pattern.
- `.planning/milestones/v1.0-phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/`
  — phase that built `tools/check_dispatch.py` (the scanner extended in D-15).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`convert_to_programmer` fallback chain (database.py:510):** `vpp_mv or
  vpp*1000` — already handles user-override DBs that pre-date `vpp_mv`. After
  D-04 this becomes `vpp_mv or vpp_volts*1000`. KEEP the chain shape; only
  the second key name flips.
- **`check_dispatch.py` 743-chip iteration:** existing regression-scan loop
  with `failures` counter + exit-code 0/1 contract. Two new asserts inside the
  loop cover WIRE-02 without a new file. Reuse the existing buffer-size fork
  (covers Uno + Leonardo simulator paths).
- **`key_parsers[]` table (json_parser.c:164):** `{PROGMEM_key, fn_ptr}` array.
  Single-row edit for the atomic flip — no new row needed (atomic flip per
  D-01, not dual-key per the rejected soft-retention option).
- **`git mv` for the DB file rename:** mirrors Phase 11's `git mv parse_db_2.py
  build_db.py` — history-preserving rename pattern is established in this repo.
- **`extract_int(key, target)` macro:** PROGMEM-key-aware extractor; first arg
  is the parse key. Single-line edit at `:309` for the atomic flip.

### Established Patterns

- **`extract_num` is a single-key probe with early return** (json_parser.c:455-460).
  The macro returns 1 on match (writes target), 0 on no-match (no write). It
  does NOT chain — back-to-back invocations don't OR together because each
  one returns unconditionally. For an atomic-flip wire-key rename, we only
  need ONE invocation with the new key string.
- **Parse keys live in TWO places per field in `json_parser.c`** — once as a
  `PROGMEM` literal at the top of the file (used by the dispatch table), and
  once inline inside the `get_*` function body as the macro argument (used by
  `jsoneq` inside `extract_num`). Atomic rename: BOTH must flip together.
- **`build_db.py` emits BOTH `"vpp"` (string with "V") AND `"vpp_mv"` (int) to
  the on-disk DB schema** at `tools/build_db.py:255-256`. This phase does NOT
  drop the on-disk `"vpp"` string field (out of scope per Domain block).
  Future cleanup is tracked in Deferred Ideas.
- **`convert_to_programmer` emits the wire dict** — the dict's keys ARE the
  wire-format names. Adding/renaming a wire field is one-line in this function
  plus one-line each at three sites in `json_parser.c`. No protocol-version
  bump.
- **Three-repo doc consistency** — meta `CLAUDE.md`, `firestarter_app/CLAUDE.md`,
  `firestarter/CLAUDE.md` are authored independently but reference the same
  file paths and wire shape. After Phase 2: `chip_database.json` everywhere;
  "minipro" appears in exactly one app `CLAUDE.md` line + the
  `MINIPRO_XML_URL` constant.
- **Comment style for minipro neutralization** — terse, function-relevant:
  `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware
  mem_type integer.` matches the existing single-line comment style.

### Integration Points

- **No dispatch / handler change.** All five `configure_*` handlers in
  `firestarter/src/proms/` read `handle->vpp_mv` (the C-struct field, already
  correctly named) — they don't care what JSON key fed it. Phase 2 is below
  the dispatch layer.
- **No serial-protocol version bump.** One key name flip; INIT/MAIN/END state
  machine and response prefixes (`OK:`, `DATA:`, etc.) unchanged.
- **No firmware C-struct change.** `firestarter_handle_t.vpp_mv`
  (`include/firestarter.h:85`) is the only consumer of the parsed mV value in
  firmware. Already correctly named.
- **User-override DB path unchanged.** `~/.firestarter/database.json` schema
  is upstream-owned (matches what `_map_data` reads from `electrical.*`). The
  loader's existing fallback chain at `database.py:373-381` handles legacy
  user-override files unchanged.
- **Cross-sub-repo coordination:** both sub-repos change. With atomic flip
  (no firmware fallback per D-01), the order matters for a partial-upgrade:
  - Python-new + firmware-old → `handle->vpp_mv` stays 0 → SAF-04 VPP ADC
    compare trips on every Intel-flash write (safe-fail).
  - Python-old + firmware-new → firmware drops the `"vpp"` key silently →
    `handle->vpp_mv` stays 0 → same fail mode.

  Recommendation: ship firmware first (the firmware-new + Python-old combo at
  least has the old wire still emitting `"vpp"` from existing installs — but
  firmware-new ignores it). Pragmatically, users flash + update together.
  Plan-phase commits Python and firmware close in time; both are documented
  in the milestone close (DOC-01).

</code_context>

<specifics>
## Specific Ideas

### Wire JSON before/after (concrete diff for firestarter_app/CLAUDE.md:46-58)

**Before:**
```json
{
  "cmd": 2,
  "type": 1,
  "algorithm": 7,
  "memory-size": 65536,
  "vpp": 12000,
  "vpp_mv": 12000,
  "pulse-delay": 0,
  "pin-count": 28,
  "chip-id": 42495,
  "flags": 10,
  "bus-config": { ... }
}
```

**After Phase 2:**
```json
{
  "cmd": 2,
  "type": 1,
  "algorithm": 7,
  "memory-size": 65536,
  "vpp_mv": 12000,
  "pulse-delay": 0,
  "pin-count": 28,
  "chip-id": 42495,
  "flags": 10,
  "bus-config": { ... }
}
```

One key removed; firmware parser no longer matches the deleted name.

### `_map_data()` internal dict diff (database.py:417-418)

**Before:**
```python
"vpp": vpp,        # float volts (4.5, 12.0, 21.0)
"vpp_mv": vpp_mv,  # int millivolts (4500, 12000, 21000)
```

**After (D-04):**
```python
"vpp_volts": vpp,  # float volts (4.5, 12.0, 21.0)
"vpp_mv": vpp_mv,  # int millivolts (4500, 12000, 21000)
```

Plus the consumer fallback at `database.py:510`:
```python
# Before:
vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp", 0) * 1000)
# After:
vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp_volts", 0) * 1000)
```

### `json_parser.c` after-state (atomic flip per D-01)

**Before (firestarter/src/json_parser.c:62, :74, :308-310):**
```c
const char key_vpp[] PROGMEM = "vpp";
// ...
static const key_parser_t key_parsers[] PROGMEM = {
    // ...
    {key_vpp, get_vpp_mv},  ...
};
// ...
bool get_vpp_mv(const char* json, jsmntok_t* tokens, int pos,
                firestarter_handle_t* handle) {
    extract_int("vpp", handle->vpp_mv);
}
```

**After:**
```c
const char key_vpp_mv[] PROGMEM = "vpp_mv";
// ...
static const key_parser_t key_parsers[] PROGMEM = {
    // ...
    {key_vpp_mv, get_vpp_mv},  ...
};
// ...
bool get_vpp_mv(const char* json, jsmntok_t* tokens, int pos,
                firestarter_handle_t* handle) {
    extract_int("vpp_mv", handle->vpp_mv);
}
```

(Three locations, one atomic flip. `extract_int` macro returns 1 on match /
0 on no-match — single-key probe; no behavior change beyond the key string.)

### Filename rename (verbatim path)

```
firestarter_app/firestarter/data/minipro_complete_db.json
→
firestarter_app/firestarter/data/chip_database.json
```

(`git mv` inside the `firestarter_app/` sub-repo to preserve blame.)

### `check_dispatch.py` augmentation sketch (D-15)

After the existing per-chip dispatch resolution loop:

```python
# WIRE-02 wire-key regression check
wire = db.convert_to_programmer(chip)
if "vpp_mv" not in wire:
    print(f"WIRE-REGRESSION: {chip.get('part_number')} — missing vpp_mv")
    failures += 1
if "vpp" in wire:
    print(f"WIRE-REGRESSION: {chip.get('part_number')} — legacy vpp key still emitted")
    failures += 1
```

Existing `failures > 0 → exit 1` contract preserved.

### Acceptance smoke commands (SC#5)

```bash
# Inside firestarter_app/ working tree, after the rename:
pip install -e .                 # picks up the new package data
firestarter --help               # CLI loads (no FileNotFoundError on the renamed DB)
firestarter info W27C512         # DB resolves the canonical UV-EPROM chip
```

### Comment scrub table (verbatim diff targets)

See D-10. Three exact-text rewrites — line numbers verified at planning time.

</specifics>

<deferred>
## Deferred Ideas

- **Remove the on-disk `"vpp"` (volts string) field from `build_db.py:255` and
  the DB schema.** `tools/build_db.py:255` currently emits both `"vpp": "12V"`
  (legacy string-with-unit) AND `"vpp_mv": 12000` (canonical int millivolts).
  After Phase 2, the wire and the internal `_map_data()` output both use
  `vpp_mv` / `vpp_volts`; the on-disk `"vpp"` string field is only read by
  `_map_data()`'s upstream-schema fallback (database.py:373-381). Dropping it
  in a future cleanup phase (v1.2) would simplify the schema. Out of v1.1
  scope — the on-disk schema is upstream-owned and changing it risks user
  overrides.

- **Drop `vpp_volts` field entirely** (v1.2+ cleanup). After Phase 2 the float
  volts field is kept renamed; a future cleanup could compute float volts on
  demand from `vpp_mv` (`vpp_mv / 1000.0`) and delete the redundant field.
  Would touch `eprom_info.py` and `ic_layout.py` consumers.

- **Test-script repair** (`firestarter_test.sh:31` / `write_test.sh:17`
  `database_generated.json` reference). Phase 4 / HW-01 owns this; the
  hardware-validation phase fixes its own scripts.

- **Python-side wire-emit unit test** (`test_convert_to_programmer.py`
  asserting `"vpp_mv" in wire and "vpp" not in wire`). Nice-to-have. Phase 2
  leans on `check_dispatch.py` for regression coverage. If a Python test infra
  arrives in v1.2, this is a candidate.

- **`firestarter vpp` CLI subcommand** (`firestarter_app/firestarter/main.py:185,626`).
  Same prefix, different concept (CLI command name, not wire key). Renaming
  would break user muscle memory. Defer indefinitely.

- **Replace minipro upstream — out of scope for v1.1** (REQUIREMENTS.md "Out
  of Scope": `infoic.xml` is authoritative; one override is sufficient).

- **`firestarter_app/firestarter/data/pinouts.json` rename audit.** No naming
  overload (pinouts ≠ minipro). Keep as-is.

- **`~/.firestarter/database.json` rename to `chip_database.json`.** Explicitly
  rejected per D-08-compat — would break user installations silently. The
  user-override file keeps its name.

- **Add `vpp_volts` consumers** — refactor `eprom_info.py` / `ic_layout.py` to
  consume `vpp_volts` consistently instead of recomputing `vpp_mv / 1000`.
  Touch-light v1.2 cleanup.

- **Remove the legacy `"vpp"` ANYTHING from firmware** — Phase 2 atomic flip
  already deletes it from `json_parser.c`. No follow-up needed.

</deferred>

---

*Phase: 02-naming-cleanup-wire-key-minipro-references*
*Context gathered: 2026-05-12*
