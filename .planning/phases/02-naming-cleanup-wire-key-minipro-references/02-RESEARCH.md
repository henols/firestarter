# Phase 2: Naming Cleanup (Wire Key + Minipro References) - Research

**Researched:** 2026-05-12
**Domain:** Cross-sub-repo mechanical rename (Python host emitter ↔ Arduino firmware JSON parser + DB file rename + comment scrub)
**Confidence:** HIGH — every load-bearing claim in CONTEXT.md verified by direct inspection of the actual source files in the sub-repos (which ARE present in the working tree as git submodules).

## Summary

Phase 2 is a low-risk mechanical rename phase, but with one important factual correction to CONTEXT.md and three additional findings the planner must address.

**Primary recommendation:** Adopt CONTEXT.md's atomic-flip approach (D-01, D-02) and 3-plan split (D-13) with one correction (CONTEXT.md misdescribes today's wire emit; see User Constraints note below) and three augmentations identified during verification:

1. Add `ic_layout.py:513` and `eprom_info.py:271` to the D-04 `vpp_volts` consumer rename list — both were anticipated by D-04 but not enumerated; they read the `_map_data()` output dict's `"vpp"` float-volts key.
2. Add `pyproject.toml:64-69` package-data fix to Plan 02-02 — the rename will break `pip install -e .` (and SC#5 smoke) unless package-data references the renamed file; the existing entries are already stale (`database_generated.json` / `database_overrides.json` / `pin-maps.json`).
3. Resolve D-15 dependency: `check_dispatch.py` today imports only stdlib (`json`/`os`/`sys`); adding `db.convert_to_programmer(chip)` introduces a runtime dependency on the installed `firestarter` package. Two viable shapes — pick one explicitly.

**Confidence on D-08 (firmware parser semantics):** HIGH. The macro semantics are exactly as CONTEXT.md describes — single-key probe with early return, first arg is the parse key compared via `strncmp_P` against the JSON token. `extract_int("vpp_mv", handle->vpp_mv)` will parse correctly. The three-site atomic flip (`json_parser.c:62` PROGMEM literal, `:74` dispatch table row, `:309` macro arg) is necessary AND sufficient.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01 — Atomic wire-key flip.** Firmware parser registers ONLY `"vpp_mv"`; Python emits ONLY `"vpp_mv"`. No backward-compat fallback on either side. All three locations in `json_parser.c` (`:62` literal, `:74` dispatch row, `:309` macro arg) flip together as a single atomic unit.

**D-02 — `convert_to_programmer` emits only `"vpp_mv"`.** `firestarter_app/firestarter/database.py:518` flips from `"vpp": vpp_mv,` to `"vpp_mv": vpp_mv,`. CLAUDE.md wire example aligned. (Note: CONTEXT.md describes today's emitter as "BOTH `"vpp": <mV>` and `"vpp_mv": <mV>`". Verified incorrect — see "Factual Correction" below.)

**D-03 — No firmware C-struct rename.** `firestarter_handle_t.vpp_mv` at `firestarter/include/firestarter.h:85` stays as-is (already correctly named).

**D-04 — Rename internal `"vpp"` float-volts key to `"vpp_volts"` in `_map_data()` output dict.** Sites: `database.py:417` (the write), `database.py:510` (the fallback read). Plus consumer sweep — see "Missed callsites" below.

**D-05 — New filename: `chip_database.json`.**

**D-06 — Use `git mv` inside `firestarter_app/` sub-repo.** Preserves blame.

**D-07 — Sweep all reader/writer/doc sites in one plan boundary.** Seven file-path sites enumerated in CONTEXT.md (all verified).

**D-08-compat — Loader stays tolerant on internal read.** `_map_data()` upstream-schema chain at `database.py:373-381` preserved unchanged (handles legacy user-override DBs).

**D-08 (macro semantics) — `extract_num` is single-key probe with early return.** Verified by direct read of `json_parser.c:447-460`.

**D-09 — Single load-bearing attribution stays.** `tools/build_db.py:10` keeps `MINIPRO_XML_URL` constant. `:23` comment softened to "upstream's XML".

**D-10 — Neutral wording table** — four exact-text rewrites verified at the line numbers given.

**D-11 — `firestarter/CLAUDE.md` reduces to zero minipro mentions.** `:30` (filename) and `:69` (protocol_id phrasing) become neutral.

**D-12 — `firestarter_app/CLAUDE.md` reduces to exactly 1 mention.** Recommend `:69` (next to `infoic.xml`).

**D-13 — Split into 3 plans** (02-01 atomic wire flip / 02-02 file rename + `vpp_volts` rename / 02-03 attribution scrub + regression scan + CLI smoke).

**D-14 — "Atomic" = the four-rename batch landing before regression scan**, not a single git commit.

**D-15 — `check_dispatch.py` is the canonical regression scanner**, augmented with two wire-key asserts inside the existing 743-chip iteration.

**D-16 — DB regeneration via `build_db.py` is OPTIONAL.** Use committed DB as the regenerated artifact if network fails.

**D-17 — `firestarter info W27C512` smoke is the integration check.** Plus `firestarter --help`.

### Claude's Discretion (research-supported recommendations below)

- PROGMEM constant name → `key_vpp_mv` (natural symmetry with the wire key string)
- `build_db.py:23` neutralization → keep softened form per D-09
- Meta `CLAUDE.md:44` edit lands in 02-02 (with other doc updates)
- Whether `--adapter` flag augments info smoke → recommend yes (one extra command, exercises pinouts.json read path too)
- Python-side `test_convert_to_programmer.py` unit test → recommend NO for v1.1 (no Python test infra exists; `check_dispatch.py` augmentation covers the contract for 743 chips, which is stronger than a single-chip unit test would be)
- `firestarter/CLAUDE.md:51-58` field-list `vpp / vpp_mv` → collapse to `vpp_mv` only

### Deferred Ideas (OUT OF SCOPE)

- Remove the on-disk `"vpp"` (volts string) field from `build_db.py:255` and the DB schema.
- Drop `vpp_volts` field entirely (v1.2+).
- Test-script repair (`firestarter_test.sh` / `write_test.sh`) — owned by Phase 4 / HW-01.
- Python-side wire-emit unit test.
- `firestarter vpp` CLI subcommand rename.
- Replace minipro upstream.
- `pinouts.json` rename audit.
- `~/.firestarter/database.json` rename (would break user installations).
- `eprom_info.py` / `ic_layout.py` `vpp_volts` consumer refactor beyond the bare rename touch.
- Remove legacy `"vpp"` ANYTHING from firmware (Phase 2 atomic flip already deletes it).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WIRE-01 | Rename wire JSON `"vpp"` → `"vpp_mv"` in Python emitter, firmware parser, and `firestarter_app/CLAUDE.md` example. | Plan 02-01 atomic-flip is correct; macro semantics (D-08) verified — `extract_int("vpp_mv", handle->vpp_mv)` parses the renamed key. Three firmware sites (`:62`, `:74`, `:309`) all verified at exact line numbers. |
| WIRE-02 | `check_dispatch.py` (or equivalent) confirms all 743 chips parse end-to-end on Uno + Leonardo simulator after the rename. | D-15 augmentation feasible but requires resolving the stdlib-only-import constraint (see "Don't Hand-Roll" below). Two viable shapes documented. |
| CLEAN-01 | Rename `minipro_complete_db.json` → `chip_database.json` with atomic update of 7 reference sites. | Every reference site verified at the line numbers given by CONTEXT.md. One additional surface to fix: `pyproject.toml` package-data declaration (pre-existing v1.0 stale, but Phase 2 should fix while we're here — see Don't Hand-Roll). |
| CLEAN-02 | Reduce "minipro" mentions to 1 in `firestarter_app/`, 0 in `firestarter/`, plus `MINIPRO_XML_URL` constant. | Mechanical comment edits; D-10 neutral-wording table verified verbatim at each line number. |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Wire JSON emission | firestarter_app (Python) | — | `database.py::convert_to_programmer` is the sole serializer. Sub-repo boundary. |
| Wire JSON parsing | firestarter (Arduino firmware) | — | `json_parser.c` reads the JSON into `firestarter_handle_t`. Sub-repo boundary. |
| Chip database storage | firestarter_app (file under `firestarter/data/`) | — | Static JSON shipped with the Python package. Firmware never reads it. |
| Chip database regeneration | firestarter_app (`tools/build_db.py`) | upstream minipro XML | Network-dependent; reads infoic.xml from gitlab. |
| Internal `_map_data()` dict | firestarter_app (Python in-memory) | — | Lives entirely inside `EpromDatabase`. Never crosses sub-repo boundary. |
| Regression scan | firestarter_app (`tools/check_dispatch.py`) | — | Host-side static scan; simulates firmware dispatch without running it. |
| CLI smoke surface | firestarter_app (`firestarter` script via `pip install -e .`) | — | Loads DB, runs `convert_to_programmer`, never talks to a real Arduino. |
| Documentation | meta-repo `CLAUDE.md` + both sub-repo `CLAUDE.md` files | — | Three CLAUDE.md files describe the same wire shape and file paths; must stay consistent. |
| Hardware safety net (SAF-04) | firestarter (firmware, `flash_intel.cpp:25-50`) | — | Mismatched wire-key parse → `handle->vpp_mv = 0` → SAF-04 VPP HIGH check fires → write aborts. Safe-fail validated; see Common Pitfalls. |

## Factual Correction to CONTEXT.md

**CONTEXT.md says the host emitter currently emits BOTH `"vpp": <mV>` and `"vpp_mv": <mV>`** (Domain block, item 1: "database.py:518 + :510"). **This is wrong.**

Direct read of `firestarter_app/firestarter/database.py:501-540` shows `convert_to_programmer` emits exactly ONE VPP key: `"vpp": vpp_mv` at line 518. Line 510 (`vpp_mv = full_eprom_data.get("vpp_mv") or int(full_eprom_data.get("vpp", 0) * 1000)`) is a **local variable assignment**, not a dict write. There is no `"vpp_mv"` in the emitted wire dict today.

The `.planning/milestones/v1.0-MILESTONE-AUDIT.md` confirms: "firestarter_app/CLAUDE.md example shows both 'vpp' and 'vpp_mv' but only 'vpp' is emitted (WARNING-3)." The CLAUDE.md example is the phantom — the wire is single-key.

**Impact on the plan:**
- D-02's edit at `database.py:518` is a **rename** (`"vpp": vpp_mv,` → `"vpp_mv": vpp_mv,`), not a **delete** of "one of two keys". Diff is one character swap on one line, not a line deletion.
- The "before" diff in CONTEXT.md `<specifics>` Wire JSON section shows BOTH keys — this is the CLAUDE.md fictional example, not the current real wire. The "after" is correct.
- WARNING-3's actual scope is two-fold: (a) wire-key name overload (volts→mV) AND (b) CLAUDE.md drift from reality. The atomic flip closes both.

This correction does NOT change any of CONTEXT.md's other decisions, but the planner should describe the edit precisely: "rename the key string at `database.py:518` from `"vpp"` to `"vpp_mv"`" (not "delete the dual-key block").

[VERIFIED: direct read of firestarter_app/firestarter/database.py lines 501-540 and .planning/milestones/v1.0-MILESTONE-AUDIT.md WARNING-3 entry]

## Standard Stack

### Core (Phase 2 touches; all already established)

| Component | Version / Source | Purpose | Why Standard |
|-----------|------------------|---------|--------------|
| Python `EpromDatabase` (`firestarter_app/firestarter/database.py`) | repo HEAD | Singleton that loads DB + emits wire JSON | Sole producer of the wire dict per v1.0 architecture; sub-repo native. |
| Arduino `json_parser.c` (`firestarter/src/json_parser.c`) | repo HEAD | JSON → `firestarter_handle_t` field population | Sole consumer of the wire JSON in firmware; v1.0 contract. |
| `jsmn` JSON tokenizer | bundled in `firestarter/src/` | AVR-friendly streaming JSON parser | Hand-rolled by upstream firestarter pre-v1.0; do NOT replace. |
| `tools/check_dispatch.py` | repo HEAD (added Phase 12) | Static regression scanner over 743 DB entries | Established Phase 12 contract; current failure-counter shape preserved. |
| `git mv` (per `firestarter_app/` sub-repo) | git 2.x+ | Atomic rename with history preservation | Mirrors Phase 11's `git mv parse_db_2.py build_db.py`. |
| Click CLI (`firestarter_app/firestarter/main.py`) | per `pyproject.toml` deps | `firestarter info` / `firestarter --help` smoke surface | Already shipped; smoke commands exist. |

### Supporting (already wired; rename-touch only)

| Component | Purpose | Phase 2 touch |
|-----------|---------|---------------|
| `firestarter_app/pyproject.toml` | Python packaging spec | Update `[tool.setuptools.package-data]` — see "Don't Hand-Roll" |
| `firestarter_app/MANIFEST.in` | sdist file list | Verify rename doesn't drop the file from sdist (currently lists `database.json` — also stale) |
| `firestarter_app/firestarter/data/pinouts.json` | DIP pinout maps | Unchanged (per Deferred Ideas) |
| `~/.firestarter/database.json` (user-override path) | User overrides | Unchanged (per D-08-compat) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Atomic flip (D-01) | Firmware accepts both `"vpp"` and `"vpp_mv"` for one milestone | Rejected by user. Extends WARNING-3 lifetime; doubles parser-key table size for one row. CONTEXT.md analysis stands. |
| `git mv` (D-06) | Delete-and-add | Loses blame across the rename — rejected as inconsistent with Phase 11 precedent. |
| Augment `check_dispatch.py` for D-15 | New `tools/check_wire_emit.py` | Would isolate the new firestarter-package dependency, but doubles the regression-scan invocation. Reject — augment existing. |
| Use `db.convert_to_programmer(chip)` inside check_dispatch loop | Inline-check on raw DB row | The DB row carries `electrical.vpp_mv`; an inline check `chip.get("electrical", {}).get("vpp_mv") is not None` is simpler and avoids the package-import dependency. See "Don't Hand-Roll". |

## Architecture Patterns

### System Architecture Diagram

```
                  ┌──────────────────────────┐
                  │  upstream minipro XML    │ (gitlab.com — network)
                  │  infoic.xml              │
                  └─────────┬────────────────┘
                            │ build_db.py fetch
                            ▼
       ┌─────────────────────────────────────────┐
       │  firestarter_app/firestarter/data/      │
       │  chip_database.json   ← RENAMED here    │ (743 chips; static, in-repo)
       └─────────┬────────────────────────────────┘
                 │ _read_config_file at database.py:189
                 ▼
       ┌─────────────────────────────────────────┐
       │  EpromDatabase (Python singleton)       │
       │  _map_data() → in-memory dict:           │
       │    {                                    │
       │      "vpp_volts": <float>,  ← RENAMED   │
       │      "vpp_mv":    <int>,                │
       │      ...                                │
       │    }                                    │
       └─────────┬────────────────────────────────┘
                 │ convert_to_programmer at database.py:501
                 ▼
       ┌─────────────────────────────────────────┐
       │  Wire JSON (Python emit):               │
       │    {                                    │
       │      "vpp_mv": <int mV>,  ← RENAMED     │
       │      ...                                │
       │    }                                    │
       └─────────┬────────────────────────────────┘
                 │ serial 250000 baud (Python → Arduino)
                 ▼
       ┌─────────────────────────────────────────┐
       │  firestarter/src/json_parser.c          │
       │    key_parsers[]  ← entry for "vpp_mv"  │
       │    get_vpp_mv() → extract_int("vpp_mv", │
       │                     handle->vpp_mv)     │
       └─────────┬────────────────────────────────┘
                 ▼
       ┌─────────────────────────────────────────┐
       │  firestarter_handle_t.vpp_mv (uint16)   │ (struct field name UNCHANGED)
       └─────────┬────────────────────────────────┘
                 │
                 ▼
       ┌─────────────────────────────────────────┐
       │  SAF-04 VPP ADC compare                 │ (flash_intel.cpp:25-50)
       │  (and equivalent in eprom.cpp)          │
       └─────────────────────────────────────────┘

       ┌─────────────────────────────────────────┐
       │  check_dispatch.py (regression scan)    │ ← WIRE-02 augmentation
       │  Static iteration over chip_database    │   asserts vpp_mv present
       │  json — 743 chips per run               │   AND vpp absent for each chip
       └─────────────────────────────────────────┘
```

### Recommended Project Structure (no structural changes; tracking the rename)

```
firestarter_app/                            # sub-repo (git submodule of meta-repo)
├── firestarter/
│   ├── database.py            ← edited (D-02, D-04, D-07, D-10)
│   ├── eprom_info.py          ← edited (D-04 consumer rename)
│   ├── ic_layout.py           ← edited (D-04 consumer rename)
│   ├── data/
│   │   └── chip_database.json ← RENAMED via git mv (was minipro_complete_db.json)
│   └── ...
├── tools/
│   ├── build_db.py            ← edited (D-07, D-09)
│   └── check_dispatch.py      ← edited (D-07, D-10, D-15)
├── pyproject.toml             ← edited (package-data stale entries — see Don't Hand-Roll)
└── CLAUDE.md                  ← edited (D-12)

firestarter/                                # sub-repo
├── src/
│   └── json_parser.c          ← edited (D-01: lines 62, 74, 309)
└── CLAUDE.md                  ← edited (D-11)

CLAUDE.md                                   # meta-repo
                               ← edited (line 44 path reference)
```

### Pattern 1: Cross-Sub-Repo Atomic Flip

**What:** Phase 2 touches two sub-repos (`firestarter_app/` Python, `firestarter/` firmware) that have independent git histories. The meta-repo (`firestarter_prom`) tracks only `.planning/` and `.claude/` and sees each sub-repo as a submodule pointer.

**When to use:** Any rename that spans the wire-protocol boundary. Two precedents in v1.0:
- Phase 02 (v1.0): JSON protocol extension — added `algorithm` field; touched both sub-repos.
- Phase 12 (v1.0): protocol-prefix dispatch — touched both sub-repos.

**Execution pattern:**
1. Each sub-repo gets its own commit(s) inside that sub-repo's git history.
2. The meta-repo then sees each submodule pointer move; commit the pointer bumps in the meta-repo separately if desired (the `.planning/` artifacts evolve in the meta-repo independently).
3. Recommended commit order per D-01: firmware first, then Python. Rationale: today's Python emits `"vpp"`; if firmware ships first (now expects `"vpp_mv"`), then a user with the new firmware + old app trips SAF-04 (`handle->vpp_mv = 0` → VPP HIGH error). If Python ships first (now emits `"vpp_mv"`), then a user with new app + old firmware ALSO trips SAF-04. Both partial-upgrade states fail safely — see Common Pitfalls below.

**Example:**
```
Plan 02-01 commits inside the firestarter/ submodule:
  git -C firestarter commit -m "WIRE-01: rename JSON key vpp -> vpp_mv (atomic three-site flip)"

Plan 02-01 commits inside the firestarter_app/ submodule:
  git -C firestarter_app commit -m "WIRE-01: emit vpp_mv (rename from vpp) + update CLAUDE.md wire example"

Plan 02-01 commits in meta-repo:
  git commit -m "docs(02): record Plan 02-01 phase progress"
  (submodule pointer bumps land in a later commit per project convention)
```

### Pattern 2: `git mv` for blame-preserving rename (CLEAN-01)

**What:** Use `git mv` for the data file rename so blame survives the rename — same as Phase 11's `git mv parse_db_2.py build_db.py`.

**Execution:**
```bash
cd firestarter_app
git mv firestarter/data/minipro_complete_db.json firestarter/data/chip_database.json
# Stage all the reference-site updates in the same commit so the file path
# is valid in every commit (no broken-state intermediate).
git add firestarter/database.py tools/build_db.py tools/check_dispatch.py CLAUDE.md pyproject.toml
git commit -m "CLEAN-01: rename minipro_complete_db.json -> chip_database.json (git mv preserves blame)"
```

### Anti-Patterns to Avoid

- **Splitting the `json_parser.c` atomic flip across two commits.** A commit where line 62 says `"vpp_mv"` but line 309 still says `"vpp"` ships a firmware that silently fails parse and trips SAF-04 on every Intel-flash write. Three-line flip must be one commit.
- **`git rm` + `git add` for the DB rename.** Use `git mv` per D-06 to preserve blame. CONTEXT.md states this; do not reorder for "tidiness".
- **Updating `firestarter/CLAUDE.md` field-list `vpp / vpp_mv` (line 51-58) to keep both.** D-01 atomic-flip implies firmware no longer reads `"vpp"`; the documented field shouldn't suggest it does. Collapse to `vpp_mv` only.
- **Renaming `firestarter_handle_t.vpp_mv` (the C struct field).** D-03 says don't — already correctly named. Renaming would mean editing every algorithm handler in `firestarter/src/proms/`; out of scope and pointless.
- **Removing the `database.py:373-381` legacy `electrical.get("vpp", "0").replace("V", "")` upstream-schema fallback.** D-08-compat preserves it — it reads the on-disk DB string `"12V"` field (which `build_db.py:255` still emits). Removing breaks user-override DBs with the upstream schema.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wire-key regression assertion across 743 chips | New `tools/check_wire_emit.py` | Augment `tools/check_dispatch.py` per D-15 | Doubles regression-scan invocation; existing loop already iterates 743 chips. |
| Parse JSON in firmware | New custom token-walker | Existing `jsmn` + `key_parsers[]` table | Already shipped; rename is one row in the table. |
| Cross-sub-repo coordination | Custom git wrapper | Standard `git mv` + per-sub-repo commits | Phase 11 precedent; understood by `gh`, GitHub blame UI, etc. |
| Float-volts ↔ mV conversion in `convert_to_programmer` fallback | Inline `vpp / 1000.0` everywhere | Keep the `or int(full_eprom_data.get("vpp_volts", 0) * 1000)` fallback chain | Handles legacy user-override DBs without `vpp_mv`. |
| Test scripts for the rename (`firestarter_test.sh` etc.) | Edit them in Phase 2 | DEFERRED to Phase 4 / HW-01 | Out of scope; would conflict with Phase 4's broader script repair. |

**Key insight:** Phase 2 is a rename phase; the v1.0 architecture already established every contract this phase touches. Hand-rolling a new abstraction here would generate carry-over work for v1.2.

### Critical: `check_dispatch.py` augmentation shape (D-15 implementation)

CONTEXT.md D-15's sketch reads:
```python
wire = db.convert_to_programmer(chip)
if "vpp_mv" not in wire: ...
if "vpp" in wire: ...
```

**Problem:** `check_dispatch.py` today imports only `json` / `os` / `sys` (verified at the file head). Calling `db.convert_to_programmer(chip)` requires:
1. `from firestarter.database import EpromDatabase` (introduces a runtime dependency on the installed `firestarter` package; today the scanner runs standalone).
2. `db = EpromDatabase()` — loads `chip_database.json` AGAIN (the scanner already loaded it directly at line 84), plus `pinouts.json`.
3. `chip` is the raw DB entry (with nested `electrical` / `programming` keys). `convert_to_programmer` expects the `_map_data()` output. So the call must be `db.convert_to_programmer(db.get_eprom(chip["part_number"]))` — a name-based round-trip through the DB index.

**Two viable shapes (planner picks one):**

**Shape A — Add the package import** (matches CONTEXT.md D-15 sketch literally):
```python
from firestarter.database import EpromDatabase
# ... inside main(), after the existing DB load:
db = EpromDatabase()
# ... inside the 743-chip loop:
mapped = db.get_eprom(chip.get("part_number"))
if mapped:
    wire = db.convert_to_programmer(mapped)
    if "vpp_mv" not in wire:
        print(f"WIRE-REGRESSION: {chip.get('part_number')} — missing vpp_mv")
        failures += 1
    if "vpp" in wire:
        print(f"WIRE-REGRESSION: {chip.get('part_number')} — legacy vpp key still emitted")
        failures += 1
```
Pros: Tests the FULL host-side wire-emit path. Catches regressions in `_map_data` AND `convert_to_programmer`.
Cons: Adds a runtime dependency; `check_dispatch.py` no longer runs without `pip install -e .`.

**Shape B — Inline static check on the DB row** (avoids package import):
```python
# Inside the existing per-chip loop:
electrical = chip.get("electrical", {})
if electrical.get("vpp_mv") is None and not electrical.get("vpp"):
    # No VPP info in DB → skip wire-key assertion (5V-only chip)
    pass
else:
    # DB has VPP info → wire emit must produce vpp_mv. Replicate emit logic:
    vpp_mv_from_db = electrical.get("vpp_mv")
    if vpp_mv_from_db is None:
        print(f"WIRE-REGRESSION: {chip.get('part_number')} — DB row missing electrical.vpp_mv "
              f"(post-Phase-2 wire-emit relies on it)")
        failures += 1
```
Pros: Pure-stdlib; scanner stays standalone. Catches the v1.0 → v1.1 regression precisely (the DB row must carry `vpp_mv` for the wire emit to produce it).
Cons: Doesn't exercise `convert_to_programmer` — relies on the planner trusting that the one-line `database.py:518` rename does what it says.

**Recommendation: Shape A.** SC#4 says "regenerates the DB and confirms all 743 chips still parse end-to-end" — "end-to-end" includes the wire emit step, not just the DB row shape. Shape A tests the actual contract Phase 2 changes. The added package dependency is acceptable because `check_dispatch.py` runs from `firestarter_app/` after `pip install -e .` anyway (per `firestarter_app/CLAUDE.md` dev workflow), so the package is always available where the scanner runs.

### Critical: `pyproject.toml` package-data is stale

`firestarter_app/pyproject.toml:64-69`:
```toml
[tool.setuptools.package-data]
"firestarter" = [
    "data/database_generated.json",
    "data/database_overrides.json",
    "data/pin-maps.json",
]
```

**None of these filenames match the current `firestarter/data/` contents.** Actual files: `minipro_complete_db.json`, `database_overrides.json`, `pinouts.json`.

`MANIFEST.in` is also stale: lists `firestarter/data/database.json` and `firestarter/data/pin-maps.json`. Neither file exists.

This is **pre-existing v1.0 drift** (Phase 11 consolidated to `minipro_complete_db.json` + `pinouts.json` but didn't update packaging metadata). Phase 2 is renaming the same files; the planner should fix the packaging declaration in Plan 02-02 to:
```toml
[tool.setuptools.package-data]
"firestarter" = [
    "data/chip_database.json",
    "data/database_overrides.json",
    "data/pinouts.json",
]
```
And align `MANIFEST.in`.

**Why it matters for SC#5:** SC#5 requires `firestarter info W27C512` to succeed. With `include-package-data = true`, an editable install (`pip install -e .`) loads files from the source tree directly — so the stale package-data declaration doesn't bite. But a built wheel (`pip install .` or distributing on PyPI) would NOT include the data file under the new name → `FileNotFoundError` at runtime. If the smoke command tests only editable install, the stale entries hide the bug. The fix is small (one toml stanza); do it now.

[VERIFIED: direct read of firestarter_app/pyproject.toml lines 60-72, firestarter_app/MANIFEST.in, and ls firestarter_app/firestarter/data/]

## Runtime State Inventory

This is a refactor/rename phase. Each runtime-state category answered explicitly:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **One: the DB file itself** (`firestarter_app/firestarter/data/minipro_complete_db.json` — 743 chip records). `git mv` to `chip_database.json` keeps content byte-identical. No database key/value renames inside the JSON — internal field names like `electrical.vpp` / `electrical.vpp_mv` are unchanged (per Deferred Ideas — on-disk schema is upstream-owned). | `git mv` per D-06. No content-level data migration. |
| Live service config | **None.** Firestarter is a programmer CLI; there are no long-running daemons, dashboards, or external service registrations to update. No n8n / Datadog / Tailscale / Cloudflare equivalents in this project. | None. |
| OS-registered state | **None.** The `firestarter` CLI is invoked on demand via `pip install -e .` → console_scripts entry point; no Windows Task Scheduler / launchd / systemd / pm2 registrations carrying any name we're renaming. Verified by reading `pyproject.toml` — only `[project.scripts]` declares `firestarter = "firestarter.main:main"` (the CLI command name, unchanged in this phase per Deferred Ideas — `firestarter vpp` subcommand stays). | None. |
| Secrets/env vars | **One env var to verify:** `check_dispatch.py:25` reads `FIRESTARTER_DB_FILE` env var as an override for the DB path. If a user has this set to the old `minipro_complete_db.json` path, the scanner reads the wrong file (or fails). The variable name itself is unchanged; only the **default value** (the os.path.join argument) changes. Document for users in commit message; no code change needed beyond the default. | Update the default in `check_dispatch.py:27` (already in D-07's enumerated touch list — verified). No env-var rename. |
| Build artifacts | **Two stale artifacts to flag:** (1) `firestarter_app/firestarter.egg-info/SOURCES.txt` lists `firestarter/data/minipro_complete_db.json` — will be regenerated on next `pip install -e .` and pick up the new name automatically; no action needed. (2) `firestarter_app/build/lib/...` may exist if user previously ran `python setup.py build` — not in `.gitignore` (it's `build/`, which IS in .gitignore) so already excluded; will be regenerated. (3) `firestarter_app/firestarter/__pycache__/` — Python bytecode; regenerated on next interpreter run. | None actively required. Document in plan: "after rename, run `pip install -e .` to refresh egg-info; clean `build/` if it exists." |

**Crucially nothing found in:** databases that key on `"vpp"`, downstream services consuming the wire JSON beyond firmware, OS task registrations, named pipes, or any other runtime cache. Phase 2 is fundamentally a source-code + one-file rename with no out-of-band state.

[VERIFIED: ls firestarter_app/, ls firestarter_app/firestarter/data/, cat firestarter_app/pyproject.toml, cat firestarter_app/firestarter.egg-info/SOURCES.txt, cat firestarter_app/.gitignore]

## Missed Callsites (additions to CONTEXT.md)

CONTEXT.md is largely complete; the line numbers and exact strings verified against the source. Two callsites the CONTEXT.md anticipated but did not enumerate:

### D-04 internal `_map_data()` consumer sweep — verified callsites

The CONTEXT.md D-04 says: "Planner: grep for any callsite reading `full_eprom_data["vpp"]` / `.get("vpp")` (not `["vpp_mv"]`) — likely `eprom_info.py`, `ic_layout.py` — and update each."

Verified by direct grep — exactly two consumer sites:

1. **`firestarter_app/firestarter/eprom_info.py:271`**:
   ```python
   vpp_str = f"{ic.get('vpp', '-')}v" if ic.get("type") == 1 else "- " # EPROM type
   ```
   Context: `ic` is an element of `eproms_data` passed to `print_eprom_list_table()`. The caller chain is `main.py:451` → `db_instance.get_eproms(verified=args.verified)` (`database.py:438`) which returns a list of `_map_data()` outputs. **In scope for D-04 rename.**
   **Change required:** `ic.get('vpp', '-')` → `ic.get('vpp_volts', '-')`.

2. **`firestarter_app/firestarter/ic_layout.py:513`**:
   ```python
   output_data["vpp_str"] = f"{eprom_data.get('vpp', 'N/A')}v"
   ```
   Context: `eprom_data` per the docstring at `:482` is "the fully mapped data from `EpromDatabase.get_eprom(..., full=True)`" — i.e., the `_map_data()` output. **In scope for D-04 rename.**
   **Change required:** `eprom_data.get('vpp', 'N/A')` → `eprom_data.get('vpp_volts', 'N/A')`.

**Note:** `database.py:375` (`vpp_str = electrical.get("vpp", "0").replace("V", "")`) is the UPSTREAM-SCHEMA read path (`electrical.vpp` is the on-disk DB string like `"12V"`). Per D-04's explicit scope note, this is NOT renamed. The string read is separate from the dict-key write at `:417`.

### CLEAN-02 unenumerated additional touch — `firestarter_app/CLAUDE.md:42`

`firestarter_app/CLAUDE.md:42` says: `parses minipro `infoic.xml`, outputs JSON`.

CONTEXT.md D-12 lists `:42` as one option for the surviving attribution line — "planner picks one; `:69` recommended." If `:69` is picked, then `:42` needs neutralization too (CONTEXT.md captures this: "Other mentions at `:19, :36, :42 (or :69), :46-58 (wire example), :72` become either the new filename (CLEAN-01) or neutral wording"). **Verified — CONTEXT.md is complete on this point**, just worth flagging that the planner has a binary choice between `:42` and `:69` for the single surviving attribution and must enumerate the consequence for the other line.

### Pre-existing stale state (not Phase 2's job to fix, but flag for awareness)

- `firestarter_app/pyproject.toml:64-69` has STALE package-data filenames pre-dating Phase 11. Fix in Plan 02-02 (see Don't Hand-Roll for rationale).
- `firestarter_app/MANIFEST.in` lists `firestarter/data/database.json` and `firestarter/data/pin-maps.json` — neither file has existed since v1.0 Phase 11. Fix in same wave as pyproject.toml.
- `firestarter_app/firestarter/data/database_overrides.json` exists but is NOT loaded (`database.py:191` has it commented out: `override_proms = None  # //_read_config_file("database_overrides.json")`). It contains old-format `"voltages": {"vpp": "25"}` entries. Out of scope; do not touch.
- `firestarter_app/firestarter_test.sh:31` and `write_test.sh:17` reference `database_generated.json` (deleted in v1.0 Phase 11). Per CONTEXT.md "Out of scope" — explicitly owned by Phase 4 / HW-01.

[VERIFIED: grep -rn "vpp\|minipro" across both sub-repos; direct read of eprom_info.py, ic_layout.py, pyproject.toml, MANIFEST.in]

## Firmware Parser Semantics — D-08 Validation (HIGH confidence)

**Claim under test:** Renaming `key_vpp` PROGMEM literal at `json_parser.c:62` from `"vpp"` to `"vpp_mv"`, flipping the dispatch row at `:74`, AND flipping the macro arg at `:309` from `"vpp"` to `"vpp_mv"` correctly parses the new wire key.

**Direct read of `json_parser.c:447-460` (the macros):**
```c
static int jsoneq_(const char* json, jsmntok_t* tok, const char* s) {
    if (tok->type == JSMN_STRING && (int)strlen_P(s) == tok->end - tok->start &&
        strncmp_P(json + tok->start, s, tok->end - tok->start) == 0) {
        return 0;
    }
    return -1;
}

#define extract_num(element, register, type)           \
    if (jsoneq(json, &tokens[pos], element) == 0) {    \
        register = type(json + tokens[pos + 1].start); \
        return 1;                                      \
    }                                                  \
    return 0;
```

And from `:47-48`:
```c
#define jsoneq(json, tok, s) \
    jsoneq_(json, tok, PSTR(s))
```

**Analysis:**
1. `extract_int("vpp_mv", handle->vpp_mv)` expands to `if (jsoneq(json, &tokens[pos], "vpp_mv") == 0) { handle->vpp_mv = simple_strtoul(json + tokens[pos + 1].start); return 1; } return 0;`
2. `jsoneq` wraps the literal `"vpp_mv"` in `PSTR()` → places the string in PROGMEM at compile time.
3. `jsoneq_` then compares the JSON token via `strncmp_P` (PROGMEM-aware strncmp) — works correctly with the PSTR.
4. The first arg of `extract_num` IS the parse key — confirmed not a label, not a debug marker.

**Conclusion: D-08 is VERIFIED.** The macro will parse `"vpp_mv"` correctly when fed that literal.

**Additional finding — the dispatch table redundancy:**
The dispatch loop at `:109-118` ALSO performs a `jsoneq_(json, key_token, key)` check using `key_parsers[].key` (`:111`). If the token matches, it calls the parser function. The parser function (`get_vpp_mv`) then re-runs `jsoneq` inside its macro body (`:309`). This is double-checking the same key — a minor redundancy that's intentional (macro is reusable in code paths that don't go through the dispatch table). What this means for the atomic flip:

| Line | Today | Phase 2 |
|------|-------|---------|
| `:62` | `const char key_vpp[] PROGMEM = "vpp";` | `const char key_vpp_mv[] PROGMEM = "vpp_mv";` |
| `:74` | `{key_vpp, get_vpp_mv},` | `{key_vpp_mv, get_vpp_mv},` |
| `:309` | `extract_int("vpp", handle->vpp_mv);` | `extract_int("vpp_mv", handle->vpp_mv);` |

If `:62` and `:74` flip but `:309` is missed: the dispatch loop matches the token (line 62/74 say `"vpp_mv"`), calls `get_vpp_mv`, but the macro then re-checks the token against `"vpp"` (line 309 unchanged) — mismatch → macro returns 0 → register NOT written → `handle->vpp_mv` stays 0 → **silent parse failure** → SAF-04 trips.

Conversely, if `:309` flips but `:62` and `:74` stay: the dispatch loop never matches the new `"vpp_mv"` wire key against the old `"vpp"` table entry → `get_vpp_mv` is never called → same silent failure mode.

**Implication:** Three-site atomic flip in a single commit is essential. The planner should enforce this in the task structure (one task = three edits, not three tasks).

[VERIFIED: direct read of firestarter/src/json_parser.c lines 47-48, 62, 74, 109-118, 260-273, 308-310]

## Common Pitfalls

### Pitfall 1: Splitting the json_parser.c three-line flip across commits
**What goes wrong:** Intermediate commit has the wire field silently dropped on parse.
**Why it happens:** Each of the three sites is a one-line edit; tempting to commit them separately for granularity.
**How to avoid:** Plan 02-01 should specify the three sites as a single atomic action in one task. Commit message mentions all three.
**Warning signs:** Compile passes but `pio test -e native -f "*test_dispatch*"` would still pass (the dispatch suite doesn't exercise `json_parser.c` — it tests `configure_memory` only). The failure mode appears only when a wire command is processed end-to-end on real or simulated hardware. **Phase 2 has no native-test coverage of `json_parser.c`** — this is a contract risk to flag.

### Pitfall 2: Loading order — `EpromDatabase()` singleton caches at first instantiation
**What goes wrong:** If the rename ships but a developer's existing `~/.firestarter/database.json` user-override has a chip with `"voltages": {"vpp": "25"}` (old upstream-schema format), the `_map_data()` fallback at `:373-381` still reads `electrical.get("vpp", "0").replace("V", "")` — but what if a user override uses `"vpp_mv"` instead? The internal `_map_data()` output now renames its OUTPUT key, but the upstream-schema READ chain stays the same. This is correct behavior (D-08-compat), but easy to confuse during code review.
**Why it happens:** Three different `"vpp"` concepts in this codebase:
1. **Wire JSON key** (`database.py:518` output → firmware `json_parser.c:62/74/309`) — RENAMED to `"vpp_mv"`.
2. **Internal `_map_data()` output dict key** (`database.py:417`) — RENAMED to `"vpp_volts"`.
3. **Upstream-schema on-disk DB key** (`electrical.vpp` as a string like `"12V"`, emitted by `build_db.py:255`) — NOT RENAMED.
**How to avoid:** Plan 02-02 task description must explicitly distinguish "rename the OUTPUT dict key" (`:417`) from "preserve the INPUT schema read" (`:375`). Use the words "upstream schema" vs "internal dict" in the task action.
**Warning signs:** Code-review confusion ("why are we keeping `electrical.get("vpp", "0")`?"). Answer: it reads a different key from a different layer.

### Pitfall 3: Partial-upgrade safe-fail validation
**What goes wrong:** After Phase 2 ships, a user with mismatched firmware/app versions runs a write command. CONTEXT.md asserts SAF-04 catches both partial-upgrade combinations. Verify before relying.
**Verification:**
- **firmware-new + app-old** (today's app, post-Phase-2 firmware): app emits `"vpp": 12000`. Firmware-new dispatch loop iterates `key_parsers[]` — finds entry `{key_vpp_mv, get_vpp_mv}` only; `key_vpp_mv` is `"vpp_mv"`. The wire's `"vpp"` token doesn't match `"vpp_mv"` → no dispatch hit → `bus-config` check fails → falls into the unknown-field skip branch at `:128-131` (`token_idx += 2`). `handle->vpp_mv` was zero-initialized at command-handler reset, stays 0. SAF-04 (`flash_intel.cpp:25-50`) fires: `vpp_mv = rurp_read_voltage_mv()` returns real ~12V = 12000; `12000 > (uint32_t)0 + 500` → true → RESPONSE_CODE_ERROR (or WARNING if FLAG_FORCE) → write aborted. **Safe-fail.**
- **firmware-old + app-new** (today's firmware, post-Phase-2 app): app emits `"vpp_mv": 12000`. Firmware-old has `key_vpp = "vpp"` only. Same flow: dispatch loop never matches `"vpp_mv"` → unknown-field skip → `handle->vpp_mv = 0` → SAF-04 fires (same code path as above). **Safe-fail.**
- Both scenarios depend on SAF-04 having shipped (Phase 1 — already done per STATE.md "Resolved in v1.1"). **Cross-checked against `firestarter/src/proms/flash_intel.cpp:25-50` — `flash_intel_check_vpp` exists, is called from `flash_intel_write_init` at line 77, uses `handle->vpp_mv` as the setpoint. ✓**

**Caveat:** SAF-04 covers the Intel-flash path only. UV-EPROM path (`eprom_check_vpp` in `eprom.cpp:199-232`) and 28C-EEPROM path also use `handle->vpp_mv`:
- UV-EPROM: would similarly trip on VPP HIGH (12000 > 0+500) for the W27C512 / W29C040 family.
- 28C-EEPROM: `eeprom28c_write_init` doesn't engage the VPP regulator (5V-only), so the VPP-check is irrelevant. `handle->vpp_mv = 0` is benign on this path.
- AMD-flash (`flash_type_3.cpp` / `flash_type_4.cpp`): 5V-only too; no VPP regulator → `handle->vpp_mv = 0` is benign.

**Conclusion:** All VPP-using paths fail safely under a partial upgrade. The non-VPP paths (5V) don't care about `handle->vpp_mv`. **Phase 2 has a hard safety net from Phase 1.**

### Pitfall 4: `check_dispatch.py` environment expectations
**What goes wrong:** D-15 augmentation assumes `firestarter` package is importable. If a developer runs `python tools/check_dispatch.py` directly (not via `firestarter` CLI), they need `pip install -e .` first.
**Why it happens:** Today's `check_dispatch.py` is pure stdlib — no `firestarter` import. Augmentation breaks this.
**How to avoid:** Plan 02-03 task includes a comment line at the top of `check_dispatch.py` documenting the new prerequisite. Alternatively, adopt Shape B in "Don't Hand-Roll" (no new import).
**Warning signs:** `ModuleNotFoundError: No module named 'firestarter'` when running the scanner in a fresh venv without editable install. SC#4 should be invoked from a venv where `pip install -e .` has been run.

### Pitfall 5: Sub-repo git history vs meta-repo planning artifacts
**What goes wrong:** Meta-repo (`firestarter_prom`) tracks only `.planning/` + `.claude/`. Edits to `firestarter_app/` and `firestarter/` are commits in their respective sub-repo histories. The orchestrator/planner needs to know which repo each task commits into.
**Why it happens:** Cross-sub-repo phases (Phase 2, plus historical v1.0 Phase 02 and Phase 12) are the only ones with this shape. Most v1.0 phases were single-sub-repo.
**How to avoid:** Each task in each plan should explicitly identify the working directory (e.g., "Run inside `firestarter_app/`" or "Run inside `firestarter/`"). The meta-repo never has its source code touched in Phase 2 — only `.planning/` artifacts.
**Warning signs:** Confusion about whether to `cd firestarter_app/` before `git mv`, or `cd firestarter/` before editing `json_parser.c`. Both sub-repos appear in the working tree per `ls /workspaces/firestarter_prom/` — they're git submodules with their own `.git/` directories.
**Note:** From the meta-repo, `git status` will show `m firestarter_app` (lowercase 'm' = submodule has local changes, not just pointer drift). This is expected during the phase. The submodule pointer in the meta-repo only updates when you commit the sub-repo, then `git add firestarter_app` in the meta-repo.

## Code Examples

Verified patterns from the actual source:

### Wire JSON emit (after Phase 2)
```python
# Source: firestarter_app/firestarter/database.py:501-539 (after rename)
def convert_to_programmer(self, full_eprom_data: dict) -> dict:
    if not full_eprom_data:
        return {}

    # Use vpp_mv directly when available (integer millivolts from build_db.py)
    vpp_mv = (full_eprom_data.get("vpp_mv")
              or int(full_eprom_data.get("vpp_volts", 0) * 1000))  # was: "vpp" * 1000

    programmer_data = {
        "memory-size": full_eprom_data.get("memory-size", 0),
        "type": full_eprom_data.get("type", 0),
        "algorithm": full_eprom_data.get("protocol-id", 0),
        "pin-count": full_eprom_data.get("pin-count", 0),
        "vpp_mv": vpp_mv,                                          # was "vpp": vpp_mv
        "pulse-delay": full_eprom_data.get("pulse-delay", 0),
    }
    ...
```

### `_map_data()` output dict (after Phase 2)
```python
# Source: firestarter_app/firestarter/database.py:411-426 (after rename)
data = {
    "name": ic.get("part_number"),
    "manufacturer": manufacturer,
    "memory-size": electrical.get("size_bytes", 0),
    "type": determined_type,
    "pin-count": pin_count,
    "vpp_volts": vpp,             # was "vpp": vpp  — float volts (4.5, 12.0, 21.0)
    "vpp_mv": vpp_mv,             # int millivolts (4500, 12000, 21000) — unchanged
    "vcc": vcc,
    "pulse-delay": 0,
    ...
}
```

### Firmware parser atomic flip (after Phase 2)
```c
// Source: firestarter/src/json_parser.c (three-site flip)

// Line 62 — PROGMEM literal
const char key_vpp_mv[] PROGMEM = "vpp_mv";    // was: key_vpp[] = "vpp"

// Line 74 — dispatch table row
static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address},   {key_flags, get_flags},
    {key_chip_id, get_chip_id},      {key_pin_count, get_pin_count}, {key_pulse_delay, get_delay},
    {key_vpp_mv, get_vpp_mv},        {key_type, get_type},          {key_algorithm, get_algorithm},
    //   ^^^^^^^ was key_vpp
};

// Line 309 — macro arg
bool get_vpp_mv(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("vpp_mv", handle->vpp_mv);    // was: extract_int("vpp", handle->vpp_mv)
}
```

### check_dispatch.py D-15 augmentation (Shape A — recommended)
```python
# Source: firestarter_app/tools/check_dispatch.py augmentation in Plan 02-03

import json
import os
import sys
from firestarter.database import EpromDatabase   # NEW import

# ... existing module-top constants unchanged ...

def main():
    with open(DB_FILE, encoding="utf-8") as f:
        db_raw = json.load(f)

    db = EpromDatabase()   # NEW — loads chip_database.json + pinouts.json

    errors = []
    sram_in_eprom = []
    eeprom28c_in_eprom = []
    wire_regressions = []   # NEW
    total = 0
    for mfg, chips in db_raw.items():
        if not isinstance(chips, list):
            continue
        for chip in chips:
            total += 1
            # ... existing dispatch check unchanged ...

            # WIRE-02 augmentation
            part = chip.get("part_number")
            mapped = db.get_eprom(part)
            if mapped:
                wire = db.convert_to_programmer(mapped)
                if "vpp_mv" not in wire:
                    wire_regressions.append(f"{mfg}/{part} — missing vpp_mv on wire")
                if "vpp" in wire:
                    wire_regressions.append(f"{mfg}/{part} — legacy vpp key still emitted")

    if errors or sram_in_eprom or eeprom28c_in_eprom or wire_regressions:
        # ... existing failure-reporting unchanged ...
        if wire_regressions:
            print(f"FAIL: {len(wire_regressions)} wire-key regressions:")
            for e in wire_regressions[:20]:
                print(f"  {e}")
            if len(wire_regressions) > 20:
                print(f"  ... and {len(wire_regressions) - 20} more")
        sys.exit(1)

    print(
        f"PASS: all {total} chips have a valid dispatch path; "
        f"0 SRAM chips route to configure_eprom; "
        f"0 DIP28_2764 Flash/EEPROM chips route to configure_eprom; "
        f"0 wire-key regressions"
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Wire JSON `"vpp"` carries millivolts | Wire JSON `"vpp_mv"` carries millivolts | Phase 2 (this phase) | Removes semantic overload; closes WARNING-3. |
| DB file `minipro_complete_db.json` | DB file `chip_database.json` | Phase 2 (CLEAN-01) | File-rename only; content byte-identical. |
| `parse_db_2.py` / `parse_db.py` / `database_generated.json` | `build_db.py` / `minipro_complete_db.json` (now `chip_database.json`) | v1.0 Phase 11 | Phase 2 only renames the output. |
| `_map_data()` writes both `"vpp"` (float volts) and `"vpp_mv"` (int) | Same dict shape, but `"vpp"` → `"vpp_volts"` | Phase 2 (D-04) | Internal dict only; out-of-process consumers (firmware) never see it. |
| Comments / docs liberally cite "minipro" | Single attribution at `MINIPRO_XML_URL`; "upstream protocol_id" / "upstream chip XML" elsewhere | Phase 2 (CLEAN-02) | Reduces tooling confusion; minipro is a DB upstream, not a runtime dependency. |

**Deprecated/outdated (NOT in Phase 2 scope):**
- `database_overrides.json`: file exists in `firestarter/data/` but is not loaded (`database.py:191` has the call commented out). Future cleanup.
- `MANIFEST.in` lists `database.json` and `pin-maps.json` — neither file exists since v1.0 Phase 11. Should be aligned with `pyproject.toml` in this phase (see Don't Hand-Roll).
- `pyproject.toml` package-data — stale since Phase 11.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `firestarter_handle_t.vpp_mv` is zero on a fresh command (so SAF-04 trips under partial upgrade). | Common Pitfalls #3 | If the handle is reused across commands without reset, `vpp_mv` might carry over from a prior command. **[VERIFIED in part]** — `json_parser.c:164-274` resets `address`, `ctrl_flags`, bus_config fields, `chip_id` at parse start, but NOT `vpp_mv`. The reset happens in `eprom_operations.cpp` or `firestarter.cpp` (whichever calls `json_parse`). Need to confirm in the planner phase that the handle is zero-initialized per command. Low risk — Phase 1's SAF-04 tests presumably exercised this. |
| A2 | `pip install -e .` from `firestarter_app/` picks up the new filename despite the stale package-data declaration. | Don't Hand-Roll | If `include-package-data = true` (line 62) ALSO reads from the source tree on editable install (it does, per setuptools docs), the smoke command works in dev — but a built wheel would not. **[CITED: setuptools docs on editable installs]** — confirmed by setuptools behavior; risk is for downstream wheel consumers, not for SC#5 dev smoke. |
| A3 | Network access for `build_db.py` to fetch `infoic.xml` from `gitlab.com/DavidGriffith/minipro` is OPTIONAL — phase output byte-identical without regeneration. | "DB regeneration" below | If the committed `minipro_complete_db.json` is out of date vs upstream, "byte-identical after rename" is true but the DB content is also stale. Acceptable per D-16. **[ASSUMED]** based on D-16 text. |
| A4 | The user's `firestarter info W27C512` smoke (SC#5) runs from `firestarter_app/` with `pip install -e .` already done. | Don't Hand-Roll | If run from a fresh venv without install, `firestarter` CLI script isn't available. **[ASSUMED]** based on dev workflow documented in `firestarter_app/CLAUDE.md`. |
| A5 | The orphan `firestarter_app/firestarter/data/database_overrides.json` (not loaded) does not need touching despite containing legacy `"voltages": {"vpp": "25"}` entries. | "Pre-existing stale state" | If a future restore of the override loading mechanism re-enables this file, the legacy format would still parse (Pythonside D-08-compat path handles `electrical.vpp` strings). **[VERIFIED]** by direct read of `database.py:191` showing `override_proms = None`. |
| A6 | Phase 1 (SAF-04) shipped successfully; `flash_intel_check_vpp` is in production firmware. | Common Pitfalls #3 | If SAF-04 didn't ship, partial-upgrade safety story collapses to "user hopefully notices". **[VERIFIED]** by direct read of `firestarter/src/proms/flash_intel.cpp:25-50` AND STATE.md line 65: "WARNING-1 — CLOSED by Plan 01-01". |
| A7 | `eprom_info.py:271` and `ic_layout.py:513` are the ONLY two consumers of the `_map_data()` output's `"vpp"` key (besides the `convert_to_programmer` fallback at `:510`). | Missed Callsites | If there are more consumers (e.g., in a downstream tool or test), they would break silently. **[VERIFIED]** by exhaustive `grep -rn '"vpp"\|\.get\(.vpp.' firestarter_app/`. |

## Open Questions (RESOLVED)

1. **Should the `firestarter info --adapter W27C512` (richer smoke) replace or augment `firestarter info W27C512`?**
   - What we know: D-17 specifies the basic `firestarter info W27C512` and `firestarter --help`. CONTEXT.md "Claude's Discretion" mentions `--adapter` as optional augmentation.
   - What's unclear: `--adapter` additionally exercises the `pinouts.json` read path and the `get_adapter_table()` function — slightly more coverage. But also slightly more output to eyeball.
   - **RESOLVED:** Run both — `firestarter info W27C512` for the basic smoke; `firestarter info --adapter W27C512` as a second smoke immediately after. Two CLI invocations, both stdlib-fast. (Implemented in Plan 02-03 Task 02-03-03.)

2. **Should Plan 02-02 also fix `MANIFEST.in` (drift from v1.0 Phase 11)?**
   - What we know: `MANIFEST.in` lists `database.json` and `pin-maps.json` — neither file exists.
   - What's unclear: Is this in Phase 2 scope? CONTEXT.md is silent on `MANIFEST.in`.
   - **RESOLVED:** Yes — same wave as the `pyproject.toml` package-data fix. Documented as "tidy-up necessary for the renamed file to ship cleanly in wheels." Tiny scope creep, but the alternative is two phases touching the same file. (Implemented in Plan 02-02 Task 02-02-03.)

3. **What's the rollback story if a hardware test (Phase 4) discovers a regression?**
   - What we know: Three sub-repo commits (one per plan in Phase 2). Plan-level rollback works.
   - What's unclear: If SC#5 passes but Phase 4 hardware testing later reveals an issue with the renamed wire on a specific chip, do we roll back the whole Phase 2 or patch forward?
   - **RESOLVED:** Patch forward. The wire-key rename is binary correct or binary broken; if it works for one chip via `check_dispatch.py` + CLI smoke, it works for all (the wire shape is identical across all 743 chips). Phase 4 might reveal SAF-04 / SAF-05 issues unrelated to Phase 2 — those would be tracked separately. (No plan task; codified here as the operational disposition.)

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `git` (2.x+, supports `git mv`) | CLEAN-01 file rename | ✓ | (system git) | — |
| Python 3.9+ | `pip install -e .`, CLI smoke | ✓ | (`.venv` in firestarter_app/) | — |
| `pip install -e .` (editable install) | SC#5 CLI smoke | ✓ | (already done; `firestarter.egg-info/` exists) | Re-run `pip install -e .` after rename |
| Network access to `gitlab.com/DavidGriffith/minipro` | `build_db.py` regenerate DB | UNKNOWN (devcontainer outbound depends on host network policy) | — | Per D-16: use committed DB as the regenerated artifact if network fails. |
| PlatformIO (`pio run`, `pio test`) | Firmware build/test verify | UNKNOWN (firestarter sub-repo has `.pio/` — likely installed) | — | If unavailable, skip pio-based smoke; rely on `check_dispatch.py` + Python CLI smoke. Phase 4 / HW-* owns end-to-end firmware verification. |
| Arduino board / RURP shield | Real hardware E2E | ✗ (not in dev env) | — | Out of Phase 2 scope per CONTEXT.md "Out of scope" → Phase 4. |

**Missing dependencies with no fallback:** None for Phase 2 deliverables.
**Missing dependencies with fallback:** Network (D-16 handles); Arduino board (out of scope).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework (firmware) | PlatformIO + Unity (`pio test -e native`) |
| Framework (Python) | **None established yet** — Phase 2's regression coverage relies on `check_dispatch.py` static scan + CLI smoke. No `pytest` / `unittest` infra in `firestarter_app/`. |
| Config file (firmware) | `firestarter/platformio.ini` `[env:native]` |
| Config file (Python) | — (no Python test infra) |
| Quick run command (firmware) | `pio test -e native -f "*test_dispatch*"` |
| Quick run command (Python regression) | `cd firestarter_app && python tools/check_dispatch.py` |
| Full suite command (firmware) | `pio test -e native` |
| Full suite command (Python) | `cd firestarter_app && python tools/check_dispatch.py && firestarter --help && firestarter info W27C512 && firestarter info --adapter W27C512` |
| Phase gate | All four green before `/gsd-verify-work` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WIRE-01 | Python emits `"vpp_mv"` (not `"vpp"`) on wire for all 743 chips | static scan | `python tools/check_dispatch.py` (after D-15 augmentation) | ✓ (existing; needs aug in Plan 02-03) |
| WIRE-01 | Firmware parses `"vpp_mv"` into `handle->vpp_mv` | compile + (deferred to Phase 4 hardware) | `pio run -e uno && pio run -e leonardo` (compile check); no native test today | ✓ compile; ✗ native test for `json_parser.c` (gap; see below) |
| WIRE-01 | CLAUDE.md wire example shows only `"vpp_mv"` | manual + grep | `grep -c "vpp" firestarter_app/CLAUDE.md` should equal `grep -c "vpp_mv"` (only mentions are the renamed key) | N/A (doc check) |
| WIRE-02 | All 743 chips parse end-to-end on Uno + Leonardo simulator after rename | static scan | `python tools/check_dispatch.py` (with augmentation) | ✓ |
| CLEAN-01 | All 7 callsites updated atomically; old filename appears nowhere | grep | `grep -rn minipro_complete_db firestarter_app/ firestarter/ CLAUDE.md` → empty | N/A |
| CLEAN-01 | `firestarter info W27C512` loads the renamed file without `FileNotFoundError` | CLI smoke | `firestarter info W27C512` | ✓ (existing CLI) |
| CLEAN-01 | `pip install -e .` still works post-rename | smoke | `pip install -e .` exit 0 | ✓ |
| CLEAN-02 | "minipro" mentions reduced per D-09..D-12 (1 in firestarter_app + 1 attribution constant; 0 in firestarter) | grep | `grep -ci minipro firestarter_app/firestarter/ firestarter_app/tools/` and `firestarter/CLAUDE.md firestarter/src/` | N/A |

### Sampling Rate
- **Per task commit:** `python tools/check_dispatch.py` (≈1 second; 743-chip iteration is fast).
- **Per wave merge:** `pio test -e native` (firmware native tests, 15-20 seconds) + the Python smoke commands.
- **Phase gate:** Full suite + manual review of three CLAUDE.md files for consistency.

### Wave 0 Gaps

None of the existing tests cover `json_parser.c` on the native target. This is a pre-existing v1.0 gap — `test_dispatch/` exercises `configure_memory()` (post-parse) only. **Phase 2 does NOT need to close this gap** (the failure mode of a mismatched parse rename is safe-fail via SAF-04, plus `check_dispatch.py` Shape A catches it on the Python side).

If the planner wanted to add a native `test_json_parser` suite to harden the contract, the wave-0 file would be:
- [ ] `firestarter/test/native/avr/test_json_parser/test_json_parser.cpp` — covers `json_parse` correctly populates `handle->vpp_mv` from a sample wire JSON containing `"vpp_mv": 12000`.
- [ ] `firestarter/test/native/avr/test_json_parser/host_stubs.cpp` — shared with `test_dispatch/host_stubs.cpp` already exists; can be copied.

**Recommendation:** DEFER this gap to a future v1.2 hardening phase (not Phase 2). Adding native parser tests is desirable but unrelated to the rename; doing it here would scope-creep Phase 2 from "rename" to "rename + parser test coverage". The atomic-flip three-line edit is small enough that a careful code review + `check_dispatch.py` aug + Phase 4 hardware verification is sufficient.

## Security Domain

Phase 2 is a rename phase with no new authentication, authorization, input parsing, or cryptography. ASVS V5 (Input Validation) is the only category remotely applicable — but the change is structural (renaming a known JSON key), not behavioral (no new untrusted input surface).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | minimal | Existing jsmn token-bound validation in `json_parser.c`; unknown fields silently skip per `:128-131`. No change in Phase 2. |
| V6 Cryptography | no | — |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Stale wire-key parse → `handle->vpp_mv = 0` → over-voltage on chip | Tampering (data integrity at the wire-protocol layer) | SAF-04 VPP ADC compare (Phase 1 — already shipped); `eprom_check_vpp` (v1.0 Phase 3) |
| Mismatched firmware/app version → silent feature degradation | Repudiation (user thinks the write happened but it didn't) | Atomic-flip strategy (D-01) + clear failure messages (`"VPP is high"` from SAF-04) |
| Untrusted user-override DB content (`~/.firestarter/database.json`) | Tampering | `_map_data()` upstream-schema fallback (D-08-compat preserved); legacy schema validation via the `.replace("V", "")` strip |

No new threats introduced by Phase 2. All existing mitigations preserved.

## DB Regeneration Posture (D-16 challenge)

**Question:** Is "use the committed DB as the regenerated artifact if network fails" actually safe for SC#4?

**Analysis:**
SC#4 says: "regenerates the DB and confirms all 743 chips still parse end-to-end on Uno + Leonardo simulator with no algorithm regressing on the wire, after all four renames."

- **What "regenerates the DB" tests:** That `build_db.py` produces a JSON file with the SAME shape post-rename (filename change is the only Phase 2 touch to `build_db.py`; the JSON content schema is unchanged).
- **What "743 chips still parse end-to-end" tests:** That every chip resolves to a real dispatch path AND (after Plan 02-03's D-15 augmentation) emits `"vpp_mv"` on the wire.

**The key insight:** Phase 2 makes ZERO changes to the JSON content schema. `build_db.py:255-256` still emits `"electrical.vpp" = "12V"` (string) AND `"electrical.vpp_mv" = 12000` (int). The rename is purely:
1. The output filename (`minipro_complete_db.json` → `chip_database.json`).
2. The wire emit key (`"vpp"` → `"vpp_mv"`).
3. The firmware parse key.
4. The internal `_map_data()` dict key (`"vpp"` → `"vpp_volts"`).

None of these touch the on-disk DB content. So:
- **Re-running `build_db.py` post-rename:** produces a JSON identical in content to the committed `chip_database.json` (modulo any upstream `infoic.xml` drift unrelated to Phase 2).
- **Not re-running `build_db.py`:** the committed `chip_database.json` IS the artifact `build_db.py` would have produced (per v1.0 Phase 13 final regeneration).

**Conclusion: D-16 is safe.** "Use the committed DB" is byte-equivalent to "regenerate then use the regenerated DB" for the Phase 2 contract. The SC#4 language "regenerates the DB and confirms" is testing the end-to-end pipeline, not requiring a fresh network fetch. The fresh-fetch case is also tested implicitly because `build_db.py:255-256` still emits both `vpp` and `vpp_mv` fields — so even after regeneration, the database has the data the wire emitter expects (`electrical.vpp_mv`).

**Defensible posture:** Skip the network-dependent regeneration unless explicitly desired for upstream-drift detection. Use the committed `chip_database.json` directly. Document the choice in Plan 02-03's task description.

[VERIFIED: direct read of build_db.py:255-256 + database.py:387 (vpp_mv read source) + check_dispatch.py:84 (DB read path)]

## Plan Granularity (D-13 challenge)

**Question:** Is the 3-plan split optimal? Should the internal `vpp_volts` rename (D-04) live in Plan 02-01 or Plan 02-02?

**Two arguments:**

**Argument FOR D-04 in 02-01 (with WIRE-01 atomic flip):**
- Same WARNING-3 root cause (semantic overload of `"vpp"` carrying mV vs volts).
- Renames the SAME variable name (`"vpp"`) in two co-located places (`database.py:417` and `:518`).
- Code review benefits from seeing both renames in one diff.

**Argument FOR D-04 in 02-02 (with CLEAN-01 file rename) — CONTEXT.md's choice:**
- The wire flip (02-01) is across two sub-repos; adding a third file-edit to one sub-repo widens the blast radius unnecessarily.
- The internal `_map_data()` rename is a single sub-repo change (firestarter_app only); pairs naturally with CLEAN-01 which is also firestarter_app-only.
- 02-01's "atomic" claim (three firmware sites + one Python emit site) stays clean as a wire-protocol change; mixing in an internal-dict rename muddies that story.
- 02-02 already has the file rename + 7 callsite touches; adding `:417` + `:510` + 2 consumer-site touches doesn't materially increase the touch count.

**Recommendation: Keep CONTEXT.md's D-13 split as-is.** Argument FOR 02-02 wins on cleanliness of the wire-protocol commit story. The "same root cause" argument doesn't outweigh the cross-sub-repo coordination concern — Plan 02-01 should be the most reviewable commit of the phase precisely because it's the highest-risk one (wire-format change).

**Refinement suggested:** Document in Plan 02-02 task descriptions that the internal rename "addresses the same WARNING-3 semantic-overload root cause as Plan 02-01, scoped to the in-memory _map_data() dict only." This preserves the architectural traceability without merging the plans.

## Cross-Sub-Repo Coordination Pattern

**Constraint:** Meta-repo (`firestarter_prom`) tracks only `.planning/` and `.claude/`. The two sub-repos (`firestarter/` and `firestarter_app/`) are git submodules with independent histories.

**Implication for plan tasks:**
- Each task that edits code in a sub-repo runs commands inside that sub-repo's directory.
- Commits land in the sub-repo's git history, NOT the meta-repo's.
- The meta-repo only sees a submodule pointer change when explicitly bumped.

**Recommended task convention in plans:**
```markdown
## Task X: Update firmware JSON parser (atomic flip)
**Working directory:** `firestarter/` (sub-repo)
**Action:** Edit `src/json_parser.c` at three sites (lines 62, 74, 309) and commit in the firestarter sub-repo:
```bash
cd firestarter
# ... edits ...
git add src/json_parser.c
git commit -m "WIRE-01: rename JSON key vpp -> vpp_mv (atomic three-site flip)"
cd ..
```
**Verification:** `grep -c 'key_vpp_mv' firestarter/src/json_parser.c` returns 2; `grep -c '"vpp"' firestarter/src/json_parser.c` returns 0.
```

**For meta-repo .planning artifacts:** Tasks that update `.planning/phases/02-*/` files (RESEARCH.md, PLAN.md, SUMMARY.md, etc.) commit in the meta-repo's history directly. These commits sit alongside (not inside) the sub-repo commits.

**Order of operations per plan:**
1. (in the sub-repo) Make code edits → commit in sub-repo.
2. (in the meta-repo) Update `.planning/` artifacts (plan summaries etc.) → commit in meta-repo.
3. (optional, at phase end) Bump submodule pointers in meta-repo → `git add firestarter firestarter_app; git commit -m "build: bump sub-repo pointers post-Phase-2"`. This is per-project convention; the meta-repo's STATE.md and the `git status` output (`m firestarter_app`) suggest sub-repo changes happen often without immediate pointer bumps.

## Sources

### Primary (HIGH confidence)
- **Direct file reads:**
  - `firestarter_app/firestarter/database.py` (lines 1-645) — verifies all CONTEXT.md line numbers for the database module.
  - `firestarter/src/json_parser.c` (lines 1-334) — verifies the D-08 macro semantics + the three flip sites.
  - `firestarter_app/tools/check_dispatch.py` (lines 1-161) — confirms today's stdlib-only imports.
  - `firestarter_app/tools/build_db.py` (lines 1-60) — confirms `OUTPUT_FILE` at line 12, `MINIPRO_XML_URL` at line 10.
  - `firestarter_app/firestarter/eprom_info.py` (lines 180-280) — confirms the missed consumer site.
  - `firestarter_app/firestarter/ic_layout.py` (lines 475-530) — confirms the missed consumer site.
  - `firestarter_app/pyproject.toml` (lines 1-73) — uncovers the stale package-data declaration.
  - `firestarter_app/CLAUDE.md`, `firestarter/CLAUDE.md`, and meta `CLAUDE.md` — verifies all doc edit targets.
  - `firestarter/src/proms/flash_intel.cpp` (lines 25-90) — verifies SAF-04 is in production firmware.
  - `firestarter/include/firestarter.h` (lines 1-108) — verifies `vpp_mv` C-struct field at line 85.

### Secondary (MEDIUM confidence)
- `.planning/MILESTONES.md` v1.0 entry — WARNING-3 wording (cross-references the wire-key naming overload).
- `.planning/REQUIREMENTS.md` — WIRE-01 / WIRE-02 / CLEAN-01 / CLEAN-02 wording.
- `.planning/ROADMAP.md` Phase 2 — SC#1 through SC#5 wording.
- `.planning/STATE.md` line 65 — confirms Phase 1 SAF-04 closure shipped.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — WARNING-3 evidence text ("only 'vpp' is emitted").
- `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-CONTEXT.md` — confirms Phase 2 boundary at "Out of scope" of Phase 1.

### Tertiary (LOW confidence — none in this research)
- No web searches needed. The entire research scope is verifiable against the actual source code in the working tree.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all touched code is in the working tree and directly verified.
- Architecture: HIGH — sub-repo boundaries confirmed via `.gitmodules` and `ls`; meta-repo's tracking scope confirmed via CLAUDE.md.
- Pitfalls: HIGH — SAF-04 confirmed shipped; macro semantics directly read from source; partial-upgrade analysis cross-checked against `json_parser.c:164-274` (handle initialization) and SAF-04 source.
- CONTEXT.md verification: HIGH — every load-bearing claim verified except one (the "BOTH `"vpp"` and `"vpp_mv"` on the wire today" claim, which is WRONG and corrected above).
- D-15 augmentation: HIGH — the stdlib-only import constraint and proposed Shape A/B documented from direct inspection.
- D-04 consumer sweep: HIGH — exhaustive grep enumerated all two consumer sites and verified the read-context for each.
- Packaging concern: MEDIUM — stale `pyproject.toml` confirmed by direct read; impact on SC#5 reasoned from setuptools behavior (editable installs hide the bug; built wheels would not).

**Research date:** 2026-05-12
**Valid until:** 2026-06-12 (30 days — stable rename phase, no fast-moving external dependencies)

---

*Phase: 02-naming-cleanup-wire-key-minipro-references*
*Research gathered: 2026-05-12*
