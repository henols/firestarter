# Phase 2: Naming Cleanup (Wire Key + Minipro References) - Pattern Map

**Mapped:** 2026-05-12
**Files analyzed:** 13 modified, 0 new
**Analogs found:** 13 / 13 (every touched file is its own analog — this is a rename phase)

> **Important note for the planner:** Phase 2 creates **ZERO new files**. Every
> file touched already exists. There is no "scaffolding" to be done. The patterns
> below are extracted from the CURRENT state of each file and show exactly what
> the renamed/cleaned state should look like, using sibling code in the same file
> as the style anchor. Do not propose new modules, new test files, or new tooling
> — `check_dispatch.py` is augmented in place (D-15), not replaced.

---

## File Classification

| Modified File | Role | Data Flow | Closest Analog (in-file or sibling) | Match Quality |
|---------------|------|-----------|-------------------------------------|---------------|
| `firestarter_app/firestarter/database.py` | service (DB+emitter singleton) | transform (in-mem dict → wire JSON) | itself — `convert_to_programmer:501-540` for the emit; `_map_data:362-440` for the in-mem dict | exact (self-analog) |
| `firestarter_app/firestarter/eprom_info.py` | utility (formatted listing) | transform (mapped dict → text row) | line 271 itself; sibling `chip_id_str` ternary on the same line shows the style | exact (single-line touch) |
| `firestarter_app/firestarter/ic_layout.py` | utility (DIP layout renderer) | transform (mapped dict → output_data) | line 516 itself; sibling `output_data` assignments at `:510, :518` show the style | exact (single-line touch) |
| `firestarter_app/tools/build_db.py` | tool (DB regenerator) | file-I/O (XML → JSON) | itself — line 12 `OUTPUT_FILE` constant; sibling `PINOUT_FILE:13` shows the const-name style | exact (constant rename) |
| `firestarter_app/tools/check_dispatch.py` | tool (regression scanner) | batch (iterate DB, exit 0/1) | itself — existing `failures` lists + `sys.exit(1)` contract at `:123-150` | exact (in-place augmentation) |
| `firestarter_app/firestarter/data/minipro_complete_db.json` | data file (static DB) | file-I/O (loaded by `_read_config_file`) | Phase 11 precedent: `git mv parse_db_2.py build_db.py` | exact (precedent in repo) |
| `firestarter_app/pyproject.toml` | config (packaging) | static metadata | itself — lines 64-69 `[tool.setuptools.package-data]` | exact |
| `firestarter_app/MANIFEST.in` | config (sdist file list) | static metadata | itself — `include` directives at lines 1-2 | exact |
| `firestarter_app/CLAUDE.md` | docs | static prose + JSON example | itself — three sections to touch (data-flow diagram, wire example, pipeline) | exact |
| `firestarter/src/json_parser.c` | parser (firmware) | request-response (wire JSON → handle struct) | itself — siblings `get_chip_id:292-294`, `get_pin_count:296-298`, `get_type:300-302` show the EXACT pattern `extract_int("<wire-key>", handle-><field>);` where wire-key matches field name | exact (sibling-row in-table) |
| `firestarter/CLAUDE.md` | docs | static prose | itself — JSON wire protocol section + dispatch table | exact |
| `CLAUDE.md` (meta-repo) | docs | static prose | itself — line 44 path reference inside Repository Structure section | exact |

---

## Pattern Assignments

### 1. `firestarter_app/firestarter/database.py` — three concerns, three patterns

**Role:** service / Python singleton. **Data flow:** transform (in-memory dict → wire JSON dict).
**Analog:** itself — `_map_data` is the in-memory producer; `convert_to_programmer` is the wire emitter.

#### 1a. WIRE-01 wire emit (D-02) — pattern at `database.py:501-540`

**Current state (verified `:509-521`):**
```python
def convert_to_programmer(self, full_eprom_data: dict) -> dict:
    """
    Converts the full EPROM data structure (from get_eprom)
    into the concise format suitable for sending to the programmer.
    """
    if not full_eprom_data:
        return {}

    # Use vpp_mv directly when available (integer millivolts from build_db.py)
    vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp", 0) * 1000)

    # Keys to keep from the full data
    programmer_data = {
        "memory-size": full_eprom_data.get("memory-size", 0),
        "type": full_eprom_data.get("type", 0),
        "algorithm": full_eprom_data.get("protocol-id", 0),
        "pin-count": full_eprom_data.get("pin-count", 0),
        "vpp": vpp_mv,                                      # ← :518 — RENAME the key string
        "pulse-delay": full_eprom_data.get("pulse-delay", 0),
    }
```

**Pattern to copy from (the SAME function, just other rows):** every other key in
this dict is a `"kebab-case": full_eprom_data.get("kebab-case", 0)` or simple
local-variable assignment. The renamed key follows the exact same row shape — a
single `"vpp_mv": vpp_mv,` line, snake_case to match the new wire convention
already used by `vpp_mv` the local variable.

**Concrete edits:**
- `:510` — replace second `.get("vpp", 0)` arg with `.get("vpp_volts", 0)`. Only the second key flips; the `or` fallback shape is preserved (D-04 + Reusable Asset note in CONTEXT.md `<code_context>`).
- `:518` — replace `"vpp": vpp_mv,` with `"vpp_mv": vpp_mv,`. **This is a one-character-class swap on one line, NOT a line deletion** (per RESEARCH.md "Factual Correction").

#### 1b. WIRE-01 internal `_map_data` dict (D-04) — pattern at `database.py:411-426`

**Current state (verified `:411-426`):**
```python
data = {
    "name": ic.get("part_number"),
    "manufacturer": manufacturer,
    "memory-size": electrical.get("size_bytes", 0),
    "type": determined_type,
    "pin-count": pin_count,
    "vpp": vpp,           # ← :417 — float volts, RENAME key to "vpp_volts"
    "vpp_mv": vpp_mv,     # ← :418 — int millivolts (unchanged)
    "vcc": vcc,
    "pulse-delay": 0,  # Not directly available in new format, may need parsing from string
    "verified": bool(ic.get("verified", False)),
    "info-flags": info_flags,
    "flags": 0,
    "protocol-id": protocol_id,
    "pin-map": pinout_key,
}
```

**Pattern to copy from (the next line, `:418`):** `vpp_mv` shows the
target naming convention — `<basekey>_<unit>`. Apply the same shape to the
float-volts entry: `"vpp_volts": vpp,` (D-04 symmetric naming with `vpp_mv`).

**Distinction the planner MUST preserve (per RESEARCH.md "Common Pitfalls #2"):**
The UPSTREAM-SCHEMA READ at `:375` (`electrical.get("vpp", "0").replace("V", "")`)
is NOT renamed. That reads the on-disk DB string `"12V"` from
`build_db.py:255` — different concept, different layer, untouched by Phase 2.

**Concrete edit:**
- `:417` — `"vpp": vpp,` → `"vpp_volts": vpp,`

#### 1c. CLEAN-02 comment scrub (D-10) — pattern at `database.py:45, :389`

**Current state at `:45` (verified):**
```python
# Algorithm (minipro protocol_id) → firmware mem_type integer.
# Firmware dispatches on protocol first; mem_type is kept consistent for fallback paths.
_ALGO_MEM_TYPE = {
    0x05: 5,   # FLASH_AMD_STD     → TYPE_FLASH_TYPE_4
    ...
```

**Current state at `:389` (verified):**
```python
# Read algorithm integer directly — set by build_db.py as minipro protocol_id
protocol_id = programming.get("algorithm", 0)
```

**Pattern to copy from (sibling line `:46`):** terse single-line, ends with
period, uses `→` arrow for "maps to". The neutral-wording replacement in
CONTEXT.md D-10 follows this exact style — verified.

**Concrete edits (verbatim from CONTEXT.md D-10):**
- `:45` — `# Algorithm (minipro protocol_id) → firmware mem_type integer.` → `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.`
- `:389` — `# Read algorithm integer directly — set by build_db.py as minipro protocol_id` → `# Read algorithm integer directly — set by build_db.py from upstream protocol_id`

#### 1d. CLEAN-01 docstring + default path (D-07) — pattern at `database.py:189, :366`

**Current state at `:189` (path reference; not re-read — line confirmed by RESEARCH.md `Codebase entry points`):** `_read_config_file("minipro_complete_db.json")`.

**Current state at `:366` (verified in this read):**
```
    extracting voltages, and attaching the RURP-specific bus configuration. This now
    works with the new 'minipro_complete_db.json' format.
```

**Concrete edits:**
- `:189` — string literal `"minipro_complete_db.json"` → `"chip_database.json"`.
- `:366` — docstring `'minipro_complete_db.json'` → `'chip_database.json'`.

---

### 2. `firestarter_app/firestarter/eprom_info.py:271` — D-04 consumer

**Role:** utility (formatted output). **Data flow:** transform (mapped dict → text row).
**Analog:** in-file siblings on the same line.

**Current state (verified `:265-278`):**
```python
for ic in eproms_data:
    chip_id_str = f"0x{ic.get('chip-id', 0):04X}" if ic.get('chip-id') else ""
    vpp_str = f"{ic.get('vpp', '-')}v" if ic.get("type") == 1 else "- " # EPROM type
    type_str = spec_builder.get_chip_type_string(ic.get("type", 0))
```

**Pattern to copy from (the sibling `chip_id_str` line above):** `ic.get('<key>', <default>)`
single-call style. Only the key string changes; the `'v'` suffix, ternary, and
default-marker stay.

**Concrete edit:**
- `:271` — `ic.get('vpp', '-')` → `ic.get('vpp_volts', '-')`.

---

### 3. `firestarter_app/firestarter/ic_layout.py:513` — D-04 consumer

**Role:** utility (DIP layout renderer). **Data flow:** transform (mapped dict → output_data).
**Analog:** sibling `output_data` assignments in the same function.

**Current state (verified `:513-516`):**
```python
if (
    eprom_data.get("flags", 0) & 0x00000008
):  # Assumes this flag means VPP is relevant
    output_data["vpp_str"] = f"{eprom_data.get('vpp', 'N/A')}v"
```

**Pattern to copy:** identical to ic at `:516` — only the key string changes.

**Concrete edit:**
- `:516` — `eprom_data.get('vpp', 'N/A')` → `eprom_data.get('vpp_volts', 'N/A')`.

---

### 4. `firestarter_app/tools/build_db.py` — CLEAN-01 const + CLEAN-02 comment

**Role:** tool (DB regenerator). **Data flow:** file-I/O (XML fetch → JSON write).
**Analog:** itself — sibling `PINOUT_FILE` constant + sibling neutral comment style.

**Current state (verified `:10-13, :23-24`):**
```python
MINIPRO_XML_URL = "https://gitlab.com/DavidGriffith/minipro/-/raw/master/infoic.xml"
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
OUTPUT_FILE = os.path.join(_DATA_DIR, "minipro_complete_db.json")
PINOUT_FILE = os.path.join(_DATA_DIR, "pinouts.json")
...
# This map translates the numeric protocol ID from minipro's XML
# into a human-readable string that Firestarter's database uses.
PROTOCOL_MAP = {
```

**Pattern to copy from (sibling `PINOUT_FILE:13`):** consts in this file are
`UPPER_SNAKE_CASE`, value is `os.path.join(_DATA_DIR, "<filename>.json")`. Only
the filename string changes — `OUTPUT_FILE` keeps its variable name.

**Concrete edits:**
- `:12` — `"minipro_complete_db.json"` → `"chip_database.json"`. **Variable name `OUTPUT_FILE` unchanged.**
- `:10` — **NOT TOUCHED** (D-09: `MINIPRO_XML_URL` constant is the surviving attribution).
- `:23` — `# This map translates the numeric protocol ID from minipro's XML` → `# This map translates the numeric protocol ID from upstream's XML` (D-09 softened form).

---

### 5. `firestarter_app/tools/check_dispatch.py` — D-07 path + D-10 comment + D-15 augmentation

**Role:** tool (regression scanner). **Data flow:** batch iteration with exit-code contract.

**This is the most important pattern for the planner: the augmentation is IN-PLACE inside the existing 743-chip iteration. Do NOT propose a new file.**

**Current state — the iteration + failure-counter contract (verified `:82-156`):**
```python
def main():
    """Entry point: scan DB and exit non-zero if any chip lacks a dispatch path."""
    with open(DB_FILE, encoding="utf-8") as f:
        db = json.load(f)

    errors = []
    sram_in_eprom = []
    eeprom28c_in_eprom = []
    total = 0
    for mfg, chips in db.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            total += 1
            proto = chip.get("programming", {}).get("algorithm", 0) or 0
            mt = _ALGO_MEM_TYPE.get(proto)
            handler = dispatch(proto, mt)
            part = chip.get("part_number", "<unknown>")
            if handler == "ERROR":
                errors.append(
                    f"{mfg}/{part} proto=0x{proto:02X} mem_type={mt}"
                )
                continue
            # BLOCKER-2 safety: SRAM protocol must never resolve to configure_eprom
            if proto in _SRAM_PROTOCOLS and handler == "configure_eprom":
                sram_in_eprom.append(...)
            # WARNING-5 safety: DIP28_2764 + Flash/EEPROM ...
            if (
                pinout == _28C_EEPROM_HAZARD_PINOUT
                and etype == "Flash/EEPROM"
                and handler == "configure_eprom"
            ):
                eeprom28c_in_eprom.append(...)

    if errors or sram_in_eprom or eeprom28c_in_eprom:
        if errors:
            print(f"FAIL: {len(errors)} of {total} chips have no valid dispatch path:")
            for e in errors[:20]:
                print(f"  {e}")
            if len(errors) > 20:
                print(f"  ... and {len(errors) - 20} more")
        if sram_in_eprom:
            print(...)
        if eeprom28c_in_eprom:
            print(...)
        sys.exit(1)

    print(
        f"PASS: all {total} chips have a valid dispatch path; ..."
    )
```

**Pattern to copy from (the existing `sram_in_eprom` + `eeprom28c_in_eprom` block):**

1. Declare a new sibling failure-list before the loop: `wire_regressions = []`.
2. Append to it inside the same per-chip body — same indentation, same style as `sram_in_eprom.append(...)` and `eeprom28c_in_eprom.append(...)`.
3. Add `wire_regressions` to the union check at `:123` (`if errors or sram_in_eprom or eeprom28c_in_eprom or wire_regressions:`).
4. Add a `if wire_regressions:` block mirroring the existing `if sram_in_eprom:` block (header line + `:20` slice + `... and N more` overflow).
5. Final PASS print: add `"0 wire-key regressions"` to the trailing fragment.

**Per-chip body addition (Shape A — recommended by RESEARCH.md):**
```python
# WIRE-02 wire-key regression check (D-15)
part_name = chip.get("part_number")
mapped = db.get_eprom(part_name)
if mapped:
    wire = db.convert_to_programmer(mapped)
    if "vpp_mv" not in wire:
        wire_regressions.append(f"{mfg}/{part_name} — missing vpp_mv")
    if "vpp" in wire:
        wire_regressions.append(f"{mfg}/{part_name} — legacy vpp key still emitted")
```

**New top-of-file import (Shape A):**
```python
from firestarter.database import EpromDatabase
```
(stdlib `json`/`os`/`sys` retained; package-import added per RESEARCH.md "Don't Hand-Roll" Shape A recommendation).

**Other touches in same file:**
- `:2` (docstring) — `minipro_complete_db.json` → `chip_database.json` (CLEAN-01).
- `:27` (path constant default) — `"minipro_complete_db.json"` → `"chip_database.json"`.
- `:30` (comment) — `# Algorithm (minipro protocol_id) → firmware mem_type integer.` → `# Algorithm integer (upstream protocol_id from infoic.xml) → firmware mem_type integer.` (D-10).

**Existing `failures > 0 → exit 1` contract preserved:** the `sys.exit(1)` at `:150` already covers the union; just add `wire_regressions` to the precondition.

---

### 6. Data file rename — `git mv` precedent

**Action:** `git mv firestarter_app/firestarter/data/minipro_complete_db.json firestarter_app/firestarter/data/chip_database.json`

**Analog: Phase 11's `git mv parse_db_2.py build_db.py`.** Per CONTEXT.md
`<canonical_refs>` → `.planning/milestones/v1.0-phases/11-database-pipeline-cleanup/`,
that phase consolidated the parser scripts via `git mv` to preserve blame. Same
shape applies here:

```bash
cd firestarter_app
git mv firestarter/data/minipro_complete_db.json firestarter/data/chip_database.json
# Stage all 7 callsite updates (D-07) in the SAME commit so the file path is
# valid in every commit — no broken-state intermediate.
git add firestarter/database.py tools/build_db.py tools/check_dispatch.py \
        CLAUDE.md pyproject.toml MANIFEST.in firestarter/eprom_info.py firestarter/ic_layout.py
git commit -m "CLEAN-01: rename minipro_complete_db.json -> chip_database.json (git mv preserves blame)"
```

**Pattern: rename + every reader/writer reference in one commit.** Avoid an
intermediate commit where the file is renamed but a reader still references the
old path — would break `pip install -e .` and the CLI smoke between commits.

---

### 7. `firestarter/src/json_parser.c` — WIRE-01 three-site atomic flip (D-01)

**Role:** parser (firmware). **Data flow:** request-response (wire JSON → `handle->vpp_mv`).
**Analog:** itself — sibling rows in the same key-parser table show the EXACT pattern.

**This is the highest-risk edit in the phase. Three sites must flip in ONE commit (RESEARCH.md "Common Pitfalls #1").**

#### 7a. PROGMEM literal — pattern at `:56-64`

**Current state (verified):**
```c
const char key_mem_size[] PROGMEM = "memory-size";
const char key_address[] PROGMEM = "address";
const char key_flags[] PROGMEM = "flags";
const char key_chip_id[] PROGMEM = "chip-id";
const char key_pin_count[] PROGMEM = "pin-count";
const char key_pulse_delay[] PROGMEM = "pulse-delay";
const char key_vpp[] PROGMEM = "vpp";              // ← :62 — flip both literal AND var name
const char key_type[] PROGMEM = "type";
const char key_algorithm[] PROGMEM = "algorithm";
```

**Pattern to copy from (sibling `key_mem_size` at `:56`):** `const char key_<wire_key_underscored>[] PROGMEM = "<wire-key>";` — variable name matches the wire string (kebab-case → underscore in C identifier). New entry follows the same shape: `key_vpp_mv[] PROGMEM = "vpp_mv"`.

**Concrete edit `:62`:** `const char key_vpp[] PROGMEM = "vpp";` → `const char key_vpp_mv[] PROGMEM = "vpp_mv";`

#### 7b. Dispatch table row — pattern at `:71-75`

**Current state (verified):**
```c
static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address},       {key_flags, get_flags},
    {key_chip_id, get_chip_id},      {key_pin_count, get_pin_count},   {key_pulse_delay, get_delay},
    {key_vpp, get_vpp_mv},           {key_type, get_type},             {key_algorithm, get_algorithm},
};
```

**Pattern to copy from (every other row):** `{<PROGMEM_var>, <getter_fn>},` —
the var name in the row matches the var declared at the top of the file. The
`get_vpp_mv` function name does NOT change (it's already correct). Only the
PROGMEM var reference flips.

**Concrete edit `:74`:** `{key_vpp, get_vpp_mv},` → `{key_vpp_mv, get_vpp_mv},`

#### 7c. Macro arg in getter body — pattern at `:300-310`

**Current state (verified — siblings highlight the EXACT idiom):**
```c
bool get_type(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("type", handle->mem_type);
}

bool get_delay(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("pulse-delay", handle->pulse_delay);
}

bool get_vpp_mv(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("vpp", handle->vpp_mv);              // ← :309 — flip key string
}

bool get_algorithm(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_long("algorithm", handle->protocol);
}
```

**Pattern to copy from (sibling `get_type:300-302`, `get_delay:304-306`,
`get_algorithm:312-314`):** the first arg to `extract_int`/`extract_long` IS
the parse key (verified by macro semantics at `:268-273`); it always matches
the wire-side key string. After the rename: `extract_int("vpp_mv", handle->vpp_mv);`
— the macro arg matches the new wire key, and the C-struct field
`handle->vpp_mv` is unchanged (already correctly named per D-03).

**Concrete edit `:309`:** `extract_int("vpp", handle->vpp_mv);` → `extract_int("vpp_mv", handle->vpp_mv);`

**Single-commit verification:**
```bash
cd firestarter
grep -c 'key_vpp_mv' src/json_parser.c   # should be 2 (declaration + table row)
grep -c '"vpp_mv"'   src/json_parser.c   # should be ≥2 (literal + macro arg)
grep -c '"vpp"'      src/json_parser.c   # should be 0
git commit -am "WIRE-01: rename JSON key vpp -> vpp_mv (atomic three-site flip)"
```

---

### 8. `firestarter_app/pyproject.toml:64-69` — packaging fix (RESEARCH.md augmentation)

**Role:** config (setuptools metadata). **Data flow:** static.
**Analog:** none in this repo — setuptools docs are the spec. The CURRENT declaration is stale (pre-Phase-11), so the pattern is "match reality of `firestarter/data/` listing".

**Current state (verified `:61-69`):**
```toml
[tool.setuptools]
include-package-data = true
packages = ["firestarter"]
[tool.setuptools.package-data]
"firestarter" = [
    "data/database_generated.json",
    "data/database_overrides.json",
    "data/pin-maps.json",
]
```

**Reality check:** none of these three filenames exist in
`firestarter_app/firestarter/data/`. Actual files: `minipro_complete_db.json`
(→ rename target `chip_database.json`), `database_overrides.json`, `pinouts.json`.

**Pattern: list the actual shipping data files post-rename.** Concrete state after Phase 2:
```toml
[tool.setuptools.package-data]
"firestarter" = [
    "data/chip_database.json",
    "data/database_overrides.json",
    "data/pinouts.json",
]
```

**Why now:** SC#5 (`firestarter info W27C512` post-rename) passes in dev because
`include-package-data = true` reads from the source tree on editable install,
but a built wheel would `FileNotFoundError` on the renamed DB. The fix is a
3-line stanza change, ships with the same wave as CLEAN-01 per RESEARCH.md
"Don't Hand-Roll".

---

### 9. `firestarter_app/MANIFEST.in` — alignment with `pyproject.toml`

**Current state (verified, file is 11 lines):**
```
include firestarter/data/database.json
include firestarter/data/pin-maps.json
include firestarter/data/avrdude.conf
include firestarter/database.py
include firestarter/ic_layout.py
include firestarter/avr_tool.py
include firestarter/main.py
include firestarter/__init__.py
include README.md
include LICENSE
```

**Pattern:** one `include <relative-path>` per line; data files listed
explicitly. The current file lists `database.json` and `pin-maps.json` —
**neither exists**. Fix the same wave as `pyproject.toml`:

**Concrete state after Phase 2 (data file lines):**
```
include firestarter/data/chip_database.json
include firestarter/data/pinouts.json
include firestarter/data/avrdude.conf
```
(plus a discretionary `include firestarter/data/database_overrides.json` if the planner wants parity with `package-data`.)

---

### 10. `firestarter_app/CLAUDE.md` — three sections touched

**Role:** docs. **Analog:** itself — each of the three sections is its own pattern.

#### 10a. Data-flow diagram block (`:19-36`) — CLEAN-01 + CLEAN-02

**Current state (verified verbatim from system reminder of `firestarter_app/CLAUDE.md`):**
```
### Data Flow

infoic.xml → build_db.py → minipro_complete_db.json
                                        ↓
firestarter <chip> write/read/erase
     ↓
EpromDatabase.get_eprom(name)       # look up chip
     ↓
database._map_data()                # extract algorithm, vpp_mv, pinout
     ↓
database.convert_to_programmer()    # translate DIP pins to bus config
     ↓
eprom_operations.py                 # build JSON command
     ↓
serial_comm.py                      # send over serial, handle response
```

**Pattern to copy:** ASCII-arrow diagram inside a fenced code block. Only the
filename token flips: `minipro_complete_db.json` → `chip_database.json`. Rest
of the diagram unchanged.

#### 10b. Wire JSON example block (`:46-58`) — WIRE-01

**Current state (verified verbatim):**
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

**Pattern: delete the `"vpp": 12000,` line; keep `"vpp_mv": 12000,` exactly as-is.**
This is the CONTEXT.md `<specifics>` "After" block verbatim. Note the
CONTEXT.md "Before" block is the fictional dual-key version that appears here
in CLAUDE.md only — the actual wire today emits a single `"vpp": 12000`
(RESEARCH.md "Factual Correction"). Phase 2 makes CLAUDE.md match reality AND
flips the key name in one edit.

#### 10c. Database Pipeline section (`:69-92`) — CLEAN-01 + CLEAN-02

**Current state at `:69` (verified verbatim):**
`tools/build_db.py parses tools/infoic.xml (minipro chip database XML) and outputs firestarter/data/minipro_complete_db.json.`

**Pattern: replace filename + reduce "minipro" attribution.** Per D-12, ONE
attribution survives in this file. RESEARCH.md recommends keeping the
attribution near `infoic.xml` (e.g., at `:42` `"parses minipro `infoic.xml`"`)
since that's where readers naturally look for upstream provenance. The other
mentions become neutral wording.

**Other mentions in this file to neutralize (per D-12):**
- `:19` (data flow filename) — CLEAN-01.
- `:36` (Key Files bullet) — CLEAN-01.
- `:42` OR `:69` (planner picks one as the surviving attribution; the other becomes neutral).
- `:46-58` (wire example) — WIRE-01.
- `:72` (algorithm description) — CLEAN-02 neutralize.

---

### 11. `firestarter/CLAUDE.md` — zero minipro mentions, filename flip

**Role:** docs (firmware sub-repo).

**Current state (verified verbatim from system reminder):**
- `:30` block (within "Protocol Dispatch" section): `"the regenerated minipro_complete_db.json"` → `"the regenerated chip_database.json"` (CLEAN-01 + CLEAN-02 collapse).
- `:69` block (within "JSON Wire Protocol" / "Key fields"): `"vpp / vpp_mv — VPP voltage for ADC validation"` → collapse to `"vpp_mv — VPP voltage in millivolts (used by SAF-04 ADC validation)"` (D-11 + Claude's Discretion: drop `vpp` half since firmware no longer reads it).
- `:51-58` field-list block (Claude's Discretion item from CONTEXT.md): if the field list mentions `vpp / vpp_mv`, collapse to `vpp_mv` only.

**Pattern: zero minipro mentions in the firmware sub-repo (D-11).** Verify with
`grep -ci minipro firestarter/CLAUDE.md firestarter/src/ firestarter/include/` → 0.

---

### 12. Meta-repo `CLAUDE.md:44` — single-line path reference

**Role:** docs (meta-repo).

**Current state (verified verbatim from `claudeMd` in system reminder of project instructions):**
```
- **EPROM database** is in `firestarter_app/firestarter/data/minipro_complete_db.json`; user overrides go in `~/.firestarter/database.json`. `EpromDatabase` (singleton) translates generic DIP pin numbers to RURP bus config before sending to firmware.
```

**Pattern: single inline path edit.** Replace `minipro_complete_db.json` with
`chip_database.json` in this one line. No other meta-repo lines touched in
Phase 2.

---

## Shared Patterns

### Shared Pattern A: PROGMEM key-parser table (firmware)

**Source:** `firestarter/src/json_parser.c:67-92, :280-314`
**Apply to:** the WIRE-01 atomic flip only.

The firmware encodes "what JSON keys exist" in TWO places per field:
1. A PROGMEM literal at the top of the file (`const char key_*[] PROGMEM = "<wire-key>";`).
2. A row in the `key_parsers[]` dispatch table.
3. A macro-arg string inside the `get_*` function body.

**Rule:** when renaming a wire key, ALL THREE must flip in the same commit, or
the field silently drops (RESEARCH.md "Common Pitfalls #1"). The
`extract_int(<key>, handle-><field>)` macro's first argument IS the parse key;
it is re-checked inside the macro body via `jsoneq → strncmp_P`, so a stale
literal at site 3 causes a silent parse miss even if sites 1+2 are flipped.

Sibling getters show the steady-state pattern — every `get_*` body uses the
exact wire-key string as its first macro arg, where wire-key matches the field
name in `firestarter_handle_t`.

### Shared Pattern B: Python dict-emit + `or` fallback chain

**Source:** `firestarter_app/firestarter/database.py:510` and Reusable Asset note in CONTEXT.md `<code_context>`
**Apply to:** D-04 internal rename; preserves user-override compat.

The emit-time fallback chain `vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp", 0) * 1000)` is the established pattern. After D-04, only the SECOND key name flips: `... or int(full_eprom_data.get("vpp_volts", 0) * 1000)`. The chain shape (primary key, then `or`, then float-volts × 1000) is preserved — this is what keeps legacy user-override DBs compatible internally per D-08-compat.

### Shared Pattern C: Per-chip iteration with failure-list + `sys.exit(1)` contract

**Source:** `firestarter_app/tools/check_dispatch.py:82-156`
**Apply to:** D-15 augmentation only.

The scanner declares one Python list per failure-class (`errors`, `sram_in_eprom`, `eeprom28c_in_eprom`), appends inside the per-chip loop, then in the post-loop block uses `if <list>:` headers with `[:20]` slice + `... and N more` overflow, then `sys.exit(1)` if any list is non-empty. The WIRE-02 augmentation adds a FOURTH failure list (`wire_regressions`) following exactly this convention — no new infrastructure, no new function.

### Shared Pattern D: Terse single-line comment style (Python)

**Source:** `firestarter_app/firestarter/database.py:45` (sibling line of the renamed comment)
**Apply to:** D-10 comment scrub.

`# Algorithm (minipro protocol_id) → firmware mem_type integer.` — one
sentence, ends with period, uses `→` for "maps to", `()` for parenthetical
attribution. The neutral replacements in CONTEXT.md D-10 follow this style
verbatim — verified.

### Shared Pattern E: Three-CLAUDE.md doc-consistency contract

**Source:** meta `CLAUDE.md` + `firestarter_app/CLAUDE.md` + `firestarter/CLAUDE.md`
**Apply to:** all doc edits.

Three CLAUDE.md files describe the same wire shape, file paths, and dispatch
chain. After Phase 2:
- `chip_database.json` appears in all three (replacing `minipro_complete_db.json`).
- `"vpp": <mV>` wire example line removed from `firestarter_app/CLAUDE.md`.
- Mentions of "minipro": exactly 1 in `firestarter_app/CLAUDE.md` (+ `MINIPRO_XML_URL` constant in `build_db.py`); 0 in `firestarter/CLAUDE.md`; 0 in meta `CLAUDE.md`.

Verification grep (RESEARCH.md `Validation Architecture` section):
```bash
grep -rn minipro_complete_db firestarter_app/ firestarter/ CLAUDE.md   # → empty
grep -ci minipro firestarter/CLAUDE.md firestarter/src/                # → 0
grep -ci minipro firestarter_app/firestarter/ firestarter_app/tools/   # → ≤2 (MINIPRO_XML_URL line + one CLAUDE.md attribution)
```

---

## No Analog Found

Files with no close codebase analog (none in this phase — all are self-analog):

| File | Reason |
|------|--------|
| `firestarter_app/pyproject.toml` package-data | The current declaration is already stale; setuptools docs are the spec. The "pattern" is "list the actual shipping data files post-rename" — verifiable by `ls firestarter_app/firestarter/data/`. |
| `firestarter_app/MANIFEST.in` data-file lines | Same as pyproject.toml — current state is stale; align to reality. |

---

## Metadata

**Analog search scope:**
- `firestarter_app/firestarter/database.py` (lines 40-540 — targeted, non-overlapping reads)
- `firestarter_app/firestarter/eprom_info.py:265-278`
- `firestarter_app/firestarter/ic_layout.py:507-517`
- `firestarter_app/tools/build_db.py:1-35`
- `firestarter_app/tools/check_dispatch.py` (full, 161 lines)
- `firestarter/src/json_parser.c:66-92, :255-330` (non-overlapping)
- `firestarter_app/pyproject.toml:55-69`
- `firestarter_app/MANIFEST.in` (full, 11 lines)
- `firestarter_app/CLAUDE.md` (full, provided in system reminder)
- `firestarter/CLAUDE.md` (full, provided in system reminder)
- meta `CLAUDE.md` (full, provided in system reminder)

**Files scanned:** 11 source files + 3 doc files.
**Pattern extraction date:** 2026-05-12
**No new files introduced.**
