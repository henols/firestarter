# Phase 149: Firmware Page-Size Seam (dual-repo lockstep) - Pattern Map

**Mapped:** 2026-08-19
**Files analyzed:** 14 (6 new, 8 modified)
**Analogs found:** 13 / 14 (1 NO ANALOG — novel shape)

All paths below are **repo-relative from `/workspaces`** (the meta repo root). `firestarter/` = firmware
submodule, `firestarter_app/` = host CLI submodule. Every excerpt in this file was read from disk this
session at firmware tip `6992271` / app branch `gsd/v1.32-at28c-write-path-root-cause-report-provenance`,
except where marked as transcribed from `149-RESEARCH.md` (which itself carries `file:line` citations).

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `firestarter_app/tests/test_page_size_invariants.py` | test (whole-DB invariant) | batch / transform | `firestarter_app/tests/test_sdp_db_invariant.py` | exact |
| `firestarter_app/tests/test_json_key_parity.py` | test (cross-repo source scan) | file-I/O | `firestarter_app/tests/test_cap03_ack_layout_parity.py` | exact |
| `firestarter_app/tests/fixtures/planted_json_parser_*.c` | test fixture (planted violation) | file-I/O | `firestarter_app/tests/fixtures/planted_cap03_literal_index.cpp` | exact |
| `firestarter_app/tests/golden/wire_dict_expected_deltas_149.json` | test fixture (golden delta) | batch | `firestarter_app/tests/golden/wire_dict_baseline.json` + `tests/test_wire_dict_equivalence.py:54-55` | role-match |
| `.planning/phases/149-*/149-check-claims.py` + `test_check_claims_v132.py` + `fixtures/` | gate script + paired suite | file-I/O / request-response (argv+env) | `.planning/phases/146-*/146-check-claims.py` + `test_check_claims_v131.py` + `fixtures/` | exact (donor) |
| `.planning/phases/149-*/149-PAGE-SIZE.md` | doc artifact | — | `.planning/phases/148-*/148-DB-DIFF.md` | exact |
| `firestarter/src/json_parser.c` | parser (wire→handle) | request-response | the Phase 44 `read-settling-delay` / `read-strobe-us` knobs, same file | exact |
| `firestarter/include/firestarter.h` | model (struct) | — | `read_settling_us` / `chip_id` fields, same struct | exact |
| `firestarter/src/proms/eeprom_28c.cpp` | protocol handler | streaming (per-block write) | itself (`:634` flush test, `:189` `configure_eeprom28c`, `:448` `write_init`) | in-file |
| `firestarter_app/tools/build_db.py` | codegen / emitter | transform (XML→JSON) | the existing `_PAGE_SIZE_BY_PART` conditional dict-splat at `:786-795` | exact |
| `firestarter/scripts/check_size_baseline.py` | gate script | batch | `_merge05_flash_allowance()` + `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` comment block, same file | in-file |
| `firestarter/tests/fixtures/planted_size_baseline_policy_*.log` | test fixture (captured log) | file-I/O | themselves (re-plant) + `merge05_base01_anchor_leonardo.log` | exact |
| `firestarter_app/tests/scan_paths.py` | config inventory | — | `CROSS_REPO_TEST_PATHS`'s 7 existing entries, same file | exact |
| `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` (flush-count cases) | test (native Unity) | streaming | `test_fix06_page_boundary_window_readback` (same file) — but **the flush COUNTER does not exist** | **NO ANALOG — novel shape** |
| `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` (parse cases) | test (native Unity) | request-response | `test_read_settling_us_parsed_from_json` / `..._default_zero_when_absent` (same file) | exact |

---

## Pattern Assignments

### 1. `firestarter_app/tests/test_page_size_invariants.py` (NEW — test, batch)

**Analog: `firestarter_app/tests/test_sdp_db_invariant.py`.** This is the repo's canonical
whole-DB-over-raw-JSON invariant module. It reads `chip_database.json` **directly, not through
`EpromDatabase`** — which is what D-07's "every emitted `page_size` across all 746 chips" needs.

**Path/selection pattern** (`test_sdp_db_invariant.py:72-98`):
```python
_FA_DIR = Path(__file__).parent.parent
_DB_FILE = _FA_DIR / "firestarter" / "data" / "chip_database.json"
_ALGORITHM_0X0D = 13

def _select_0x0d_chips(db: dict) -> list[tuple[str, dict]]:
    """... The DB shape is {manufacturer: [chip, ...]}, and the fields live in a
    nested "programming" object. A top-level scan on db (rather than this
    nested per-chip access) finds nothing and would make every downstream
    assertion pass vacuously."""
    selected = []
    for _mfr, chips in db.items():
        for chip in chips:
            if chip["programming"]["algorithm"] == _ALGORITHM_0X0D:
                selected.append((_mfr, chip))
    return selected
```

**Offenders-list-then-assert-empty pattern** (`:308-332`) — copy this shape for the power-of-two,
range, provenance and AT28C256-non-change legs:
```python
    offenders = [
        f"{mfr}/{chip.get('part_number', '?')}"
        for mfr, chip in selected
        if chip["programming"]["chip_id_value"] != "0x00000000"
    ]
    assert not offenders, (
        "TRACE-05: every algorithm==13 (0x0D) chip must carry "
        "chip_id_value: '0x00000000' -- firmware only skips the identity "
        "branch when handle->chip_id > 0 (eeprom_28c.cpp:eeprom28c_write_init). "
        f"Offending chips: {offenders}"
    )
```

**Exact-count leg pattern** (`:267-285`) — the shape for "exactly 18 rows carry `page_size` on
algorithm 13":
```python
def test_exactly_84_algorithm_0x0d_entries() -> None:
    db = json.loads(_DB_FILE.read_text(encoding="utf-8"))
    selected = _select_0x0d_chips(db)
    assert len(selected) == 84, (
        "TRACE-05/CLOSE-01: expected exactly 84 chip_database.json entries "
        f"with programming.algorithm == 13, found {len(selected)}. A count "
        "change means a chip was added to or removed from the 0x0D bucket ..."
    )
```

**Non-vacuity leg**: this module carries a **synthetic in-memory DB** leg
(`test_synthetic_chip_id_check_true_is_flagged_non_vacuous`, `:337-375`) that feeds a one-chip dict to
the *same shared helper* the real test calls, and asserts it raises. Its own docstring calls a check
without this "a vacuous always-pass check". **Copy this**: a synthetic chip with `page_size: 96`
(not a power of two) must make the shared assert-helper raise.

**Skip-marker note** (`test_sdp_db_invariant.py:60-66`, docstring): *"This module intentionally carries
NO FW_ABSENT-style skip marker: it reads only the packaged chip_database.json, which is always present
in host-only CI."* The page-size invariant module must inherit that property — **no `requires_fw`**.

**The `tools/extra_chips.json` back door leg — analog `firestarter_app/tests/test_extra_chips_supplement.py`:**
```python
# tests/test_extra_chips_supplement.py:40-56
_HERE = os.path.dirname(__file__)
_DB_FILE = os.environ.get("FIRESTARTER_DB_FILE",
    os.path.join(_HERE, "..", "firestarter", "data", "chip_database.json"))
_EXTRA_CHIPS_FILE = os.environ.get("FIRESTARTER_EXTRA_CHIPS_FILE",
    os.path.join(_HERE, "..", "tools", "extra_chips.json"))
_SUPPLEMENT_SOURCE = "non-upstream-supplement"

# :153-167  the "every record satisfies X, and the record set is non-empty" shape
        records = [c for chips in extra.values() if isinstance(chips, list) for c in chips]
        assert records, "extra_chips.json has no records"
        for c in records:
            pn = c.get("part_number", "<unknown>")
            assert c.get("source") == _SUPPLEMENT_SOURCE, (...)
```
The back-door assertion is one leg on `_EXTRA_CHIPS_FILE`: no authored record may carry a
`programming.page_size` (today neither does), because that row bypasses `classify()` and the emitter
and therefore bypasses D-01. Reuse `_all_chips(db)` (`:63-68`) as the generator idiom.

---

### 2. `firestarter_app/tests/test_json_key_parity.py` (NEW — test, cross-repo scan)

**Analog: `firestarter_app/tests/test_cap03_ack_layout_parity.py` (Phase 147).** Closest of the
`requires_fw` family: it scans a firmware **source file with regexes**, it is the newest, and it already
carries the two-population split (live firmware leg vs. committed-fixture planted legs) that D-18 needs.

**Import-time binding + module-scope resolution** (the exact seam; `:78-98`, and
`fw_presence.py:77-102` for why `monkeypatch.setenv` cannot work):
```python
from tests.fw_presence import FW_REPO_PRESENT, FW_ROOT, fw_path, requires_fw
_HERE = Path(__file__).resolve().parent
FIRMWARE_ACK_SOURCE = fw_path("src", "firestarter.cpp")   # module scope
_FIXTURES_DIR = _HERE / "fixtures"
_FIXTURE_LITERAL_INDEX = _FIXTURES_DIR / "planted_cap03_literal_index.cpp"
```
```python
# firestarter_app/tests/fw_presence.py:77-102 — binding happens at IMPORT
FW_ROOT: Path = Path(os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT)))
FW_REPO_PRESENT: bool = (FW_ROOT / ".git").exists()
requires_fw = pytest.mark.skipif(not FW_REPO_PRESENT, reason=FW_ABSENT_REASON)
# :117-140  fw_path() raises MissingScanTargetError — a HARD failure, never a skip,
#           when the repo is present but the target is not (rename detection)
```
Consequence the planner must state in the plan: the skip leg is proved by a **subprocess** with
`FIRESTARTER_FW_ROOT` pointed at an empty dir. It is already scripted —
`firestarter_app/tools/ci_parity.sh:69,86-88` leg 1 — and must be run with `-rs` added, because the
script's bare `-q` hides skips.

**The two-population split** (`test_cap03_ack_layout_parity.py:34-47`, module docstring — copy this
paragraph's logic verbatim in intent):
> "`requires_fw` … is the ONLY skip marker this module uses… Those two legs deliberately carry NO
> `requires_fw` decorator: they read committed fixtures under `tests/fixtures/`, which are always
> present regardless of whether the sibling firmware checkout exists, so they stay live and exercise
> the gate's failure modes even in an absent-firmware run."

**The planted leg body, with the V12 ceremony** (`:711-750`) — the executor must copy all four parts:
shared-helper reuse, `monkeypatch.setattr` on the module-scope path constant, leg isolation, and the
blob-hash + porcelain proof that the plant never touched the real firmware:
```python
def test_planted_literal_index_is_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    """... Calls the SAME `_check_budget_offset_is_computed` helper the live leg
    ... calls, never a parallel reimplementation."""
    assert _FIXTURE_LITERAL_INDEX.is_file(), f"committed fixture missing: {_FIXTURE_LITERAL_INDEX}"
    # V12 ceremony: capture the REAL firmware source (never the fixture)
    # BEFORE any monkeypatch, so the "after" comparison below proves this
    # plant never touched it.
    real_ack_source = FIRMWARE_ACK_SOURCE
    before_sha = _git_hash_object(real_ack_source) if FW_REPO_PRESENT else None

    monkeypatch.setattr(sys.modules[__name__], "FIRMWARE_ACK_SOURCE", _FIXTURE_LITERAL_INDEX)
    with pytest.raises(AssertionError) as excinfo:
        _check_budget_offset_is_computed()
    message = str(excinfo.value)
    assert "13" in message
    assert "4 + _vlen" in message
    # Leg isolation: the OTHER plant's distinguishing phrase must be absent.
    assert "capability loss" not in message

    if FW_REPO_PRESENT:
        after_sha = _git_hash_object(real_ack_source)
        assert before_sha == after_sha, ("the real firmware ack source's git blob hash changed ...")
        assert _git_porcelain(FW_ROOT) == "", ("the sibling firmware repo is not clean ...")
```
Also copy the fail-closed and anti-skip legs at `:604-630` (`test_gate_fails_closed_on_an_unreadable_firmware_path`,
`test_this_module_cannot_be_silently_skipped`) and `:563` (`test_scan_targets_are_non_vacuous`).

**The two regexes and the non-vacuity guard** are already drafted in `149-RESEARCH.md` §"Code Examples /
The parity-scan module skeleton". The source side they must match, read verbatim this session:
```c
// firestarter/src/json_parser.c:67
const char key_mem_size[] PROGMEM = "memory-size";
const char key_address[] PROGMEM = "address";
const char key_flags[] PROGMEM = "flags";
const char key_chip_id[] PROGMEM = "chip-id";
const char key_pin_count[] PROGMEM = "pin-count";
const char key_pulse_delay[] PROGMEM = "pulse-delay";
const char key_vpp_mv[] PROGMEM = "vpp_mv";
const char key_algorithm[] PROGMEM = "algorithm";
/* Phase 44 — host-tunable read-timing knobs (D-04 sweep params) */
const char key_read_settling[] PROGMEM = "read-settling-delay";
const char key_read_strobe[]   PROGMEM = "read-strobe-us";
```
Note `key_read_strobe[]` has **aligned extra spaces** before `PROGMEM` — the regex must tolerate
arbitrary whitespace (`\s*\[\s*\]\s+PROGMEM\s*=`), and the 10-key set above is the exemption-list
population for the firmware→Python direction.

---

### 3. `firestarter_app/tests/fixtures/planted_json_parser_*.c` (NEW — planted fixtures)

**Analog: `firestarter_app/tests/fixtures/planted_cap03_literal_index.cpp`** (there are 13 planted
fixtures in that dir; this one is the newest C/C++ one). Its header comment is the required shape —
copy all five clauses (never-compiled, not in any build filter, injected via `monkeypatch.setattr`
only, faithful copy of the real region with **exactly one** planted change, and what defect shape the
plant reproduces):
```c
/*
 * DELIBERATELY-VIOLATING fixture for
 * tests/test_cap03_ack_layout_parity.py (Phase 144 Plan 02, TEST-07, ...).
 *
 * This file is a minimal, standalone, never-compiled C++ snippet. It is not
 * built by platformio.ini and is not referenced from any firmware target or
 * build_src_filter in either repository. It exists ONLY so the paired
 * pytest can point test_cap03_ack_layout_parity.py's module-level
 * FIRMWARE_ACK_SOURCE path constant at it (via `monkeypatch.setattr` on
 * FIRMWARE_ACK_SOURCE, never an edit to the real
 * firestarter/src/firestarter.cpp) and prove the gate actually fails on a
 * real firmware/host wire-layout disagreement.
 *
 * It is a faithful copy of firestarter/src/firestarter.cpp's `_ready` pack
 * region (... firestarter.cpp:166-208), with exactly ONE planted change: ...
 */
```
Naming convention: `planted_<subject>_<defect>.c`. Two plants are needed, one per RED leg the
research names: `planted_json_parser_key_string_drift.c` (PROGMEM string spelled `page_size`, not
`page-size`) and `planted_json_parser_undispatched_key.c` (string declared, absent from
`key_parsers[]`). Each is a faithful copy of the `:56-79` region above with exactly one change.

---

### 4. `firestarter_app/tests/golden/wire_dict_expected_deltas_149.json` (NEW — golden delta fixture)

**Analog: `firestarter_app/tests/golden/wire_dict_baseline.json` + its loader in
`tests/test_wire_dict_equivalence.py`.** Loader pattern (`:54-55`, `:153-165`) — plain `json.loads` on
a `_HERE`-relative path, whole-dict equality, self-documenting RED message via `_describe_record_diff`:
```python
_HERE = Path(__file__).resolve().parent
_GOLDEN = _HERE / "golden" / "wire_dict_baseline.json"
...
def test_live_capture_matches_golden() -> None:
    doc = json.loads(_GOLDEN.read_text(encoding="utf-8"))
    recorded = doc["records"]
    live = _capture_wire_dicts(_REAL_DB)
    assert recorded == live, (
        "live 746-chip wire-dict capture drifted from tests/golden/wire_dict_baseline.json; ..."
        f"Diff: {_describe_record_diff(recorded, live)}"
    )
```
File shape to mirror: `{"meta": {...}, "records": {"<mfg>|<part_number>|<i>": {<wire dict>}}}`;
the delta file uses `{"meta": {...}, "deltas": {...}}`. The 18 record keys, the recommended `meta`
block and the four-assertion replacement test are already resolved verbatim in `149-RESEARCH.md`
§R6(c) and §R6(d) — **hand them to the executor as-is**, with the research's own instruction that the
fixture be *generated from the golden programmatically, never transcribed* (the `|<i>` suffix is a
positional index). `_REAL_DB = EpromDatabase(skip_local_override=True)` at `:79` is mandatory.

---

### 5. `.planning/phases/149-*/149-check-claims.py` + `test_check_claims_v132.py` + `fixtures/` (NEW — phase gate)

**Analog (donor, explicit): `.planning/phases/146-close-honesty-ledger-*/146-check-claims.py`** (451
lines), its paired `test_check_claims_v131.py` (15 legs, 30,928 B) and its `fixtures/` (5 files:
`clean_control.md`, `clean_control_second.md`, `planted_forbidden_claim.md`,
`planted_missing_caveat.md`, `planted_proven_unqualified.md`).

**Module skeleton (defs in order):** `_HERE` → `_DEFAULT_TARGETS` → `FIRESTARTER_CLAIMSCAN_TARGETS_146`
→ `FORBIDDEN_PATTERNS` → `REQUIRED_CAVEAT_PATTERNS` → `_ALL_CAVEAT_LABELS` → `_CAVEAT_RULES` →
`_required_caveats_for()` → `_assert_default_targets_are_local()` → `resolve_targets(argv)` →
`scan_text()` → `_print_bucket()` → `main(argv)`.

**The `_HERE` trap — the exact lines that must be hard-coded** (`146-check-claims.py:102-120`, read
verbatim). Line 108 is the one line that must stay a `__file__`-derived expression and never a
sibling-directory string; the `149-` prefix literal must change in **three** places (`_DEFAULT_TARGETS`,
the prefix comparison at `:262`, and its printed message):
```python
# Module-top path constant. This is the ONLY directory `_DEFAULT_TARGETS`
# below is ever built from -- never a sibling-directory string constant.
# This construction is what stops the cross-phase-copy defect where a
# checker's defaults silently resolved to a stale sibling phase directory
# and passed vacuously with nothing actually scanned.
# Source: `139-check-claims.py:73`, copied verbatim.
_HERE = os.path.dirname(os.path.abspath(__file__))

_DEFAULT_TARGETS = [
    os.path.join(_HERE, "146-LEDGER.md"),
    os.path.join(_HERE, "146-CORRECTIONS.md"),
    ...
]
```
**The runtime self-check** (`:235-269`) — both legs (directory-locality AND phase-number prefix):
```python
def _assert_default_targets_are_local():
    """Startup self-check -- called first thing in main(), before target
    resolution or any scanning. ... a future copy of this file into another
    phase's directory fails loudly the first time it is run, rather than
    silently scanning nothing and reporting success."""
    all_local = True
    for entry in _DEFAULT_TARGETS:
        if os.path.dirname(entry) != _HERE:
            print(f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not resolve inside this phase's own directory ...")
            all_local = False
        if not os.path.basename(entry).startswith("146-"):     # <- becomes "149-"
            print(f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry this phase's own 146- prefix ...")
            all_local = False
    return all_local
```

**Pattern-table shape** (`:136-172`) — a list of `(label, compiled_regex)` 2-tuples, all
`re.IGNORECASE`, no proximity window:
```python
FORBIDDEN_PATTERNS = [
    ("datasheet-conformant", re.compile(r"datasheet[-\s]conformant", re.IGNORECASE)),
    ...
    ("proven-unqualified", re.compile(r"\bproven\b", re.IGNORECASE)),
    ("now-works", re.compile(r"now\s+works?\b", re.IGNORECASE)),
]
```
**The `proven-unqualified` row is the one that must NOT be copied verbatim** — see `149-RESEARCH.md`
§X-2: `\bproven\b` makes PGSZ-05's own required phrase a violation. The research's fix is
`r"(?<!software-)\bproven\b"`.

**Required-caveat table** is a **3**-tuple `(label, prose, regex)` (`:178-189`), consumed through the
per-basename `_CAVEAT_RULES` map (`:209-217`) and `_required_caveats_for()` (`:220-232`), which
**fails CLOSED** — an unmapped basename gets the FULL caveat set:
```python
REQUIRED_CAVEAT_PATTERNS = [
    ("ceiling-voltage", "the ~6.25 V program-VCC ceiling", re.compile(r"6\.25\s*V")),
    ("ceiling-narrowing", "the silicon-margin narrowing that ceiling implies",
     re.compile(r"silicon[-\s]margin", re.IGNORECASE)),
]
_ALL_CAVEAT_LABELS = frozenset(label for label, _prose, _pattern in REQUIRED_CAVEAT_PATTERNS)
_CAVEAT_RULES = {"146-LEDGER.md": frozenset({"ceiling-voltage", "ceiling-narrowing"}), ...,
                 "146-CORRECTIONS.md": frozenset()}

def _required_caveats_for(path):
    """... Fails CLOSED on an unknown basename: a target with no `_CAVEAT_RULES` entry
    gets the FULL caveat set, never the empty set."""
    return _CAVEAT_RULES.get(os.path.basename(path), _ALL_CAVEAT_LABELS)
```
For 149 the required caveat is PGSZ-05's phrase: `("software-proven-unvalidated", "the
software-proven / unvalidated-on-silicon qualifier", re.compile(r"software[-\s]proven\s+and\s+unvalidated\s+on\s+silicon", re.IGNORECASE))`.

**Env seam name must be `FIRESTARTER_CLAIMSCAN_TARGETS_149`** (`:122-134`: a bare/duplicated suffix
"would let one phase's seam silently retarget another phase's gate"), with `os.environ.get` and **no
default** so present-but-empty is distinguishable from absent.

**Paired suite: `test_check_claims_v131.py`.** Subprocess runner + by-path importer + PASS-line helper
(`:100-155`) — copy all three:
```python
def _run_scanner(targets=None, argv=None):
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_146"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_146", None)
    return subprocess.run([sys.executable, str(_SCANNER), *(argv or [])],
                          cwd=str(_HERE), capture_output=True, text=True, env=env)

def _import_scanner_module():
    """Import `146-check-claims.py` by file path (never as a package) solely to
    introspect its module-level constants ... The module name argument is arbitrary,
    which is what lets a filename that is not a valid Python identifier be loaded at all."""
    spec = importlib.util.spec_from_file_location("check_claims_146_introspect", str(_SCANNER))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
```
**The 15 legs to transcribe** (names are the specification; renumber to `_149`/`v132`):
`test_gate_exits_zero_on_the_clean_control`, `..._planted_overclaim_flips_the_gate_to_failure`,
`..._planted_missing_caveat_...`, `..._planted_bare_claim_word_...`,
`test_fail_closed_on_a_nonexistent_scan_target`, `test_never_vacuous_on_an_explicitly_empty_target_list`,
`test_pass_line_names_every_scanned_file`, `test_positional_argv_precedence_beats_the_env_seam`,
`test_armed_against_the_five_real_closing_artifacts`,
`test_default_targets_resolve_inside_this_phase_directory`,
`test_default_targets_basenames_carry_this_phases_prefix`,
`test_every_default_targets_basename_has_a_caveat_rule_entry`,
`test_unrecognised_basename_resolves_to_the_full_caveat_set`,
`test_caveat_exempt_basename_passes_without_either_caveat`,
`test_caveat_exempt_basename_still_fails_on_a_forbidden_phrase`.

**Fixture layout:** `149-*/fixtures/` with the donor's 5-file shape — two clean controls (so the
PASS-line-names-every-file leg is non-trivial) plus one plant per forbidden/required rule the phase
adds. Every windowed (`{0,3}`/`{0,4}`) pattern the research proposes needs **its own** plant
(`146-check-claims.py:59-62` records that Phase 139 measured a windowed scanner passing four planted
overclaims).

**Two ordering facts the planner must encode:** (a) exit codes — there is deliberately **no** branch
that exits 0 when nothing was scanned (`:67-85`), so the target list cannot name a SUMMARY that does
not yet exist; (b) the changelog target lives in `firestarter_app/README.md`, **outside `_HERE`**, so
it must be passed via **argv**, not `_DEFAULT_TARGETS` (which the locality self-check would reject).

---

### 6. `.planning/phases/149-*/149-PAGE-SIZE.md` (NEW — review artifact)

**Analog: `.planning/phases/148-numeric-database-values-the-at28c-vcc-decode/148-DB-DIFF.md`** (567
lines). Section skeleton read from disk:
```
# 148-DB-DIFF.md — Phase 148 D-12 review artifact
## Before
### `python3 tools/diff_db.py ; echo EXIT=$?`                 <- pasted command + output + EXIT=
### `python3 tools/check_dispatch.py ; echo EXIT=$?`
### `python3 -m pytest tests/test_chip_database_field_inventory.py -o addopts="" -q`
### `firestarter info AT28C256` (with FIRESTARTER_CONFIG_DIR pointed at an empty scratch dir)
## Wire equivalence (D-14 / D-06)
### `python3 -m pytest tests/test_wire_dict_equivalence.py -o addopts="" -q`
### `git diff --stat tests/__snapshots__/test_characterization.ambr`
**Claim for the record:** ...
**Correction to the record (RESEARCH F-3):** ...
## Plan 06 — the VCC margin-rail substitution (D-01/D-02/D-03)
### RED — `... ; echo EXIT=$?` (before the rule)
**Correction to the plan's predicted mechanism.** ...
### GREEN — `... ; echo EXIT=$?` (after RULE_VCC_MARGIN_RAIL landed)
**Measured distribution (exactly as predicted by 148-CONTEXT.md D-11's corrected mechanism):**
### The 56-chip mover list (D-12) — by manufacturer
**ATMEL — 20 — all algorithm `0x0D`:**  ... (one bold heading per manufacturer, with counts)
### Justification (D-03, restated with its citation)
### Explicit non-claim: ...
**Correction (Plan 08 / RESEARCH F-6):** ...
## The 56 movers
## Why this condition
```
**The five reusable conventions:** every `###` is a **pasted command with `; echo EXIT=$?`** and its
literal output; the mover list is grouped by manufacturer with per-group counts and algorithm
attribution; justification is restated **with its citation**; explicit non-claims get their own
`###`; and later-plan corrections are appended in-place as bold **Correction (…)** paragraphs rather
than by rewriting the earlier text. The 149 analogue's required sections are enumerated in
`149-CONTEXT.md` D-16 (provenance table, 15/3 lists, three measured non-claims, cold flash/RAM for
three targets with leonardo headroom **as a number**, MERGE-05 breach **named**).

---

### 7. `firestarter/src/json_parser.c` (MODIFIED — parser, request-response)

**Analog: the Phase 44 `read-settling-delay` / `read-strobe-us` knobs, in this same file.**
**FIVE edit points — plus a sixth Phase 44 skipped.** All read verbatim this session:

**(i) PROGMEM key string** — append after `:66`:
```c
// firestarter/src/json_parser.c:74-77
const char key_algorithm[] PROGMEM = "algorithm";
/* Phase 44 — host-tunable read-timing knobs (D-04 sweep params) */
const char key_read_settling[] PROGMEM = "read-settling-delay";
const char key_read_strobe[]   PROGMEM = "read-strobe-us";
```

**(ii) `key_parsers[]` row** — the table is **self-sizing** (dispatch loop at `:113` is
`sizeof(key_parsers)/sizeof(key_parsers[0])`); no count constant anywhere:
```c
// firestarter/src/json_parser.c:91
typedef struct {
    PGM_P key;
    bool (*parser_func)(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle);
} key_parser_t;

static const key_parser_t key_parsers[] PROGMEM = {
    {key_mem_size, get_memory_size}, {key_address, get_address},         {key_flags, get_flags},
    {key_chip_id, get_chip_id},      {key_pin_count, get_pin_count},     {key_pulse_delay, get_delay},
    {key_vpp_mv, get_vpp_mv},        {key_algorithm, get_algorithm},
    /* Phase 44 — read-timing sweep knobs (RCA-01 causal proof, D-04) */
    {key_read_settling, get_read_settling},                              {key_read_strobe, get_read_strobe},
};
```

**(iii) forward declaration** at `:25-26` (alongside 8 siblings), same signature as every getter.

**(iv) the getter — use the ONE-LINE `extract_int` form, not the Phase 44 clamp form.** D-07 puts
validation in the handler, so the parse-time clamp idiom is wrong here. `get_chip_id` at `:296-298` is
the precise model (and it stores into the `uint16_t` field, exactly as `page_size` will):
```c
// firestarter/src/json_parser.c:466-497
#define extract_long(element, register) \
    extract_num(element, register, simple_strtoul)

#define extract_int(element, register) extract_long(element, register)
...
bool get_chip_id(const char* json, jsmntok_t* tokens, int pos, firestarter_handle_t* handle) {
    extract_int("chip-id", handle->chip_id);
}
```

**(v) the optional-key reset in `json_parse` — D-05's exact precedent is line 89:**
```c
// firestarter/src/json_parser.c:164-278
int json_parse(const char* json, jsmntok_t* tokens, int token_count, firestarter_handle_t* handle) {
    handle->address = 0;
    handle->ctrl_flags = 0;
    handle->bus_config.rw_line = 0xFF;
    handle->bus_config.vpp_line = 0xFF;
    handle->bus_config.address_lines[0] = 0xFF;
    handle->bus_config.address_mask = 0;
    handle->bus_config.static_high_mask = 0;
    handle->chip_id = 0;                      // <- :89  D-05's precedent; add page_size beside it
```
Note `read_settling_us` / `read_strobe_us` are **absent** from this block — Phase 44 skipped point (v).
Do not copy that omission.

**(vi) the unknown-key skip D-11 pins — do not change it, test it:**
```c
// firestarter/src/json_parser.c:319-321
        } else {
            // Unknown field — skip key + value token (forward-compatible with new Python fields)
            token_idx += 2;
        }
```

**Also in this file (folded todo):** delete `json_init()` (`:50-54`) and its declaration in
`include/json_parser.h:19`. Do **not** count any flash saving toward D-12's exemption.

---

### 8. `firestarter/include/firestarter.h` (MODIFIED — struct field)

**Analog: the neighbouring optional-knob fields in the same struct.** Field-width precedent for the
discretionary choice: `vpp_mv` (`:196`) and `chip_id` (`:201`) are both `uint16_t`; the Phase 44 knobs
are `uint32_t`. Comment convention: trailing `/* … ; 0 = <default meaning> */`.
```c
// firestarter/include/firestarter.h:188-224 (excerpt :192-204)
    uint32_t protocol;
    uint8_t pins;
    uint32_t mem_size;
    uint32_t address;              // <- the flush test's operand, uint32_t
    uint16_t vpp_mv;
    uint32_t pulse_delay;
    uint32_t read_settling_us;   /* address-settling delay before /CE assert (µs; 0 = no settling delay) */
    uint32_t read_strobe_us;     /* /CE read-strobe pulse width (µs; 0 = use default 3µs) */
    uint32_t ctrl_flags;
    uint16_t chip_id;
    char data_buffer[DATA_BUFFER_SIZE];
```
The struct closes at `:219`. `DATA_BUFFER_SIZE` is at `:16-17` and is the validation range's upper bound.

---

### 9. `firestarter/src/proms/eeprom_28c.cpp` (MODIFIED — handler, streaming)

**Analog: itself.** Three edit sites, all read verbatim.

**(a) The flush expression at `:634` — the ONLY code use of `PAGE_SIZE` in all of `src/`:**
```c
// firestarter/src/proms/eeprom_28c.cpp:622-652 (loop body)
    for (uint32_t i = 0; i < handle->data_size; i++) {
        uint32_t address = handle->address + i;          // :623  ABSOLUTE address
        uint8_t data = handle->data_buffer[i];
        handle->firestarter_set_data(handle, address, data);
        ... (page_load_worst_us instrumentation) ...
        bool page_end = ((address + 1) % PAGE_SIZE) == 0;   // :634  <- becomes & (mask)
        bool last_byte = (i == handle->data_size - 1);
        if (page_end || last_byte) {
            if (!eeprom28c_wait_for_page_write(handle, address, data)) { ... break; }   // :644
            if (!eeprom28c_verify_page_readback(handle, window_start, i)) { ... break; } // :648
            window_start = i + 1;                                                        // :652
        }
    }
```

**(b) The two candidate resolve sites — BOTH extracted so the planner can choose with the code in
front of it.** `write_init`'s early return:
```c
// firestarter/src/proms/eeprom_28c.cpp:420-428
void eeprom28c_write_init(firestarter_handle_t* handle) {
    if (handle->chip_id > 0) {
        eeprom28c_check_chip_id(handle);
        if (handle->response_code == RESPONSE_CODE_ERROR) {
            return;                                     // :454  EARLY RETURN
        }
    }
```
`configure_eeprom28c` is `:189-221`, runs exactly once per command via `configure_memory`
(`firestarter.cpp:93`), and already sets `handle->pulse_delay = 0` at `:192` — i.e. it is already the
"resolve this protocol's parameters" function.

**Decision-forcing fact the planner must carry into the plan text:** the existing native cases call
`configure_memory(&h)` then `h.firestarter_operation_main(&h)` and **never**
`firestarter_operation_init` (`test_val_eeprom28c.cpp:218,249,269` — verified below in §14). So a mask
resolved in `write_init` leaves every existing case at mask 0 (flush every byte), which would change
`test_fix06_page_boundary_window_readback`'s two-window behaviour. `configure_eeprom28c` avoids that
with zero test edits. If `write_init` is chosen anyway, the mask must be resolved as its **first
statement, above the `chip_id` block**, and the consumer must treat `mask == 0` as "use the fallback".

**(c) The comment D-04 rewrites and D-10 renames** — `:19-33`, quoted in full in `149-RESEARCH.md`
§R3(a). Clause `:26-28` ("64 errs SAFE … can never overrun a page") → **unproven** for the 11 promoted
16/32 rows; clause `:30-32` ("delivered by a separate, DEFERRED phase … not yet inserted into
ROADMAP.md") → statement of fact with the software-proven/unvalidated qualifier. The `:22-25` density
argument (AT28MC010 64 vs AT28C010 128) **stays true** and is re-verified by D-01.

---

### 10. `firestarter_app/tools/build_db.py` (MODIFIED — emitter, transform)

**Analog: the existing `_PAGE_SIZE_BY_PART` conditional dict-splat in the same emit dict.**
Provenance is in scope at the emit site — both are plain locals in the same `for ic in
mfg.findall(".//ic")` body (`:455`), so **no plumbing is needed**:
```python
# firestarter_app/tools/build_db.py:477-490
                variant = int(ic.get("variant"), 16)
                proto_id = int(ic.get("protocol_id"), 16)              # :478  <- IN SCOPE at :786
                flags = int(ic.get("flags"), 16)
                # PROV-01 (136.1-01): raw, un-curated upstream page_size attribute
                # off this SAME <ic> element. ... it is not consulted by any
                # ALLOW/REFUSE decision anywhere in this codebase.
                raw_page_size = int(ic.get("page_size", "0x0"), 16)     # :490  <- IN SCOPE at :786
```
The `:485-486` "not consulted by any ALLOW/REFUSE decision" clause **becomes false** the moment D-01
lands and must be corrected in the same diff, or the file self-contradicts.

**The emit arm to extend** (`:779-796`), with the `_canon` expression currently computed **twice**
(`:789` and `:792` — hoisting is a free win in a line being edited anyway):
```python
                        "infoic_page_size_raw": raw_page_size,
                        # PGSZ-01 / CR-01: datasheet-sourced per-chip page size. ...
                        # so they ride the firmware flash4_page_size() heuristic.   <- STALE, fix
                        **(
                            {"page_size": _PAGE_SIZE_BY_PART[
                                name.split(",")[0].split("@")[0].strip()]}
                            if name.split(",")[0].split("@")[0].strip() in _PAGE_SIZE_BY_PART
                            else {}
                        ),
```
The full replacement (with the D-01 comment block) is drafted in `149-RESEARCH.md` §"Code Examples /
The provenance-keyed emit arm". Guard-rail to restate in the plan: the arm must **not** filter on
`raw_page_size != 64` (D-03's rejected direction) nor on `raw_page_size in (64, 128)`.
`_PAGE_SIZE_BY_PART` (`:121-140`, 2 entries, both upstream `0x05`) is **not extended**, and the two
populations are disjoint so arm ordering is legibility-only.

---

### 11. `firestarter/scripts/check_size_baseline.py` (MODIFIED — gate script)

**Analog: `MERGE05_DEFECT_FIX_EXEMPTION_BYTES` and its comment block, in the same file.**

**The function, verbatim (`:274-296`) — note the docstring makes decomposition load-bearing, which is
why the honest new shape is a 5-tuple, not a summed 4-tuple:**
```python
def _merge05_flash_allowance(env):
    """Resolve `env`'s MERGE-05 flash-growth figures. Returns
    (band, exemption, allowance, band_label).

    Sole consumer of BOTH MERGE05_UNO_CLASS_FLASH_BAND and
    MERGE05_DEFECT_FIX_EXEMPTION_BYTES -- compare_avr_policy_merge05 (the FAIL
    arm) and main()'s PASS-line builder both call this rather than each
    recomputing the band, so neither literal is ever read in two places...

    `allowance` is the effective ceiling actually enforced: base band plus the
    named defect-fix exemption. `band` and `exemption` are returned separately
    so every message can show the decomposition instead of only the sum -- the
    +96 B stays visible in the output rather than being absorbed into one
    widened number.
    """
    band = 0 if env == "leonardo" else MERGE05_UNO_CLASS_FLASH_BAND
    band_label = "leonardo" if env == "leonardo" else "uno-class"
    exemption = MERGE05_DEFECT_FIX_EXEMPTION_BYTES
    return band, exemption, band + exemption, band_label
```

**Call site 1 — the FAIL arm (`:334-341`):**
```python
    band, exemption, allowance, band_label = _merge05_flash_allowance(env)
    flash_delta = flash_used - rec["flash_used"]
    if flash_delta > allowance:
        failures.append(
            f"{env}: flash_used baseline={rec['flash_used']} observed={flash_used} "
            f"delta={flash_delta:+d} exceeds MERGE-05 {band_label} allowance of "
            f"{allowance} B (band {band} B + defect-fix exemption {exemption} B)"
```
**Call site 2 — `main()`'s PASS-line builder (`:525-541`), read verbatim:**
```python
            if policy == "merge05":
                rec = baseline["avr_targets"][env]
                band, exemption, allowance, _label = _merge05_flash_allowance(env)
                flash_delta = u - rec["flash_used"]
                compared.append(
                    f"{env}(flash={u}/{t}"
                    f"[{flash_delta:+d}<={allowance}=band{band}+exempt{exemption}],"
                    f"ram={ru}/{rt}[=])"
                )
```
Both unpack a 4-tuple positionally — **a 5-tuple breaks both** unless updated.

**The constant's comment block is the template for the new one (`:125-167`).** Required sections, in
order: what the bytes ARE with commit SHAs and the per-target measurement; "WHY an exemption" with the
three named rejected alternatives (re-anchor / widen the band / shrink the fix); the "NAMED here, so
the growth is admitted in one visible, attributable place rather than laundered into a moved reference
point" sentence; the ARMED-tripwire paragraph naming its own negative-control test; and a `SCOPE:
flash only` clause (RAM keeps zero tolerance and is deliberately not widened):
```python
# What the 96 bytes ARE: eprom_internal_program_pulse() plus its two VPP settle
# constants, from firmware commits eb563d2 (...) and ebe9cb3 (...). Measured at
# exactly +96 B on all three AVR targets against BASE-01; RAM did not move ...
# WHY an exemption. All three alternatives were considered and rejected ...
#   - NOT a third re-anchor of scripts/baseline/size_baseline_base01.json. ...
#   - NOT a widening of MERGE05_UNO_CLASS_FLASH_BAND, and NOT a widening of the
#     leonardo 0 B band. ...
#   - NOT shrinking the fix. ...
# The tripwire stays ARMED at the new floor: a delta of one byte beyond the
# effective allowance still FAILS. That is a machine-checked negative control,
# not a claim -- tests/test_check_size_baseline.py's
# test_policy_merge05_admits_the_documented_defect_fix feeds a planted +97 B
# leonardo log and asserts exit 1.
# SCOPE: flash only. compare_avr_policy_merge05's ram_used clause keeps its
# zero tolerance and is deliberately NOT widened by this constant ...
MERGE05_DEFECT_FIX_EXEMPTION_BYTES = 96
```

**The four `firestarter/tests/test_check_size_baseline.py` legs keyed on strings** (from
`149-RESEARCH.md` §R8(d), verified line refs): `:458` `"allowance of 96 B"`; `:449`
`over.returncode == 1` on a `delta=+97` leonardo plant (**this one inverts** — +97 becomes inside the
new allowance); `:455` `"delta=+97"`; `:490` `"allowance of 160 B"`; `:433` the PASS-decomposition
string; `:316` the landing-deltas arithmetic. These tests **do** run in firmware CI
(`build.yml:161 pytest tests/ -v`) even though the script itself runs in no CI leg.

---

### 12. `firestarter/tests/fixtures/planted_size_baseline_policy_*.log` (MODIFIED — re-plant)

**Analog: themselves.** They are **full captured `pio run` transcripts**, not snippets. Format, read
verbatim:
```
Processing leonardo (platform: atmelavr; board: leonardo; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/leonardo.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Leonardo
HARDWARE: ATMEGA32U4 16MHz, 2.50KB RAM, 28KB Flash
...
Linking .pio/build/leonardo/firestarter_leonardo.elf
Checking size .pio/build/leonardo/firestarter_leonardo.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [========  ]  78.7% (used 2014 bytes from 2560 bytes)
Flash: [========= ]  93.8% (used 27003 bytes from 28672 bytes)
Building .pio/build/leonardo/firestarter_leonardo.hex
========================= [SUCCESS] Took 2.49 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
leonardo       SUCCESS   00:00:02.494
```
**The only lines that must change are the two `RAM:` / `Flash:` report lines** (the script's regex is
"anchored at column 0, multiline… does NOT capture the percentage or the bar-graph",
`check_size_baseline.py:169-171`) — so the percentage and bar graph are cosmetic, but should be kept
plausible. Today `27003 = 26906 + 97`, i.e. **allowance + 1**; the re-plant must become
`26906 + 96 + N + 1`. Same arithmetic for `planted_size_baseline_policy_uno_over_band.log` against
uno's 24824 + 64 + 96. Clean counterparts to keep consistent live in the same dir:
`merge05_base01_anchor_{leonardo,uno,uno328pb}.log`, `captured_build_{leonardo,uno,uno328pb}.log`.

---

### 13. `firestarter_app/tests/scan_paths.py` (MODIFIED — inventory)

**Analog: the 7 existing `CROSS_REPO_TEST_PATHS` entries.** The addition is one `ScanPathEntry(path,
(consumer_module, ...))` tuple:
```python
# firestarter_app/tests/scan_paths.py:94-129
CROSS_REPO_TEST_PATHS: tuple[ScanPathEntry, ...] = (
    ScanPathEntry("include/firestarter.h",
                  ("test_revision_constants_parity.py", "test_check_is_memory_cmd_no_ifdef.py")),
    ScanPathEntry("src/proms/eeprom_28c.cpp",
                  ("test_check_no_log_in_sdp_window.py", "test_sdp_table_parity.py")),
    ...
    ScanPathEntry("src/firestarter.cpp", ("test_cap03_ack_layout_parity.py",)),
)
# + ScanPathEntry("src/json_parser.c", ("test_json_key_parity.py",)),
```
**The name-collision trap documented at the file head (`:20-49`) — the load-bearing paragraphs:**
```
**Deliberately explicit, never derived.** No wildcard pattern matching and
no directory walk of any kind. Deriving this list mechanically (e.g. "any
path containing the string `firestarter`") would silently re-create the
exact name-collision trap this module documents below ...
  - CROSS_REPO_TOOL_RESOLVERS -- ... 7 of the 11 files construct their default
    path with a SINGLE ".." from `tools/` (os.path.join(_HERE, "..",
    "firestarter", ...)), which resolves into `firestarter_app/firestarter/` --
    this project's OWN Python PACKAGE, not the sibling repo. Only a path built
    with TWO ".." segments ... reaches the sibling.
```
`FW_ROOT / "src/json_parser.c"` = `/workspaces/firestarter/src/json_parser.c`, outside
`/workspaces/firestarter_app` — so `test_scan_paths_resolve.py:127`'s
`not resolved.is_relative_to(_APP_REPO_ROOT)` guard is satisfied. No count assertion breaks: the two
guards are **floors** (`_FLOOR = 6` at `test_scan_paths_resolve.py:47,98,103`) and
`ALL_CROSS_REPO_PATHS` is derived (`scan_paths.py:265-274`); the only exact count is on the *tool*
population (`== 11`, `:247`), untouched. **Two stale prose counts to fix while there:** `:30` says "6
paths resolved from the 7 proxy-carrying modules" and `:259` says "the same 6 paths" — both are 7
today and become 8.

---

### 14a. `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` — flush-count cases

**NO ANALOG — novel shape.** The suite has **no call counter of any kind**. Its only observability
seams are (i) the bus recorder — **wrong seam**, see below — and (ii) `h.response_code`. The flush
COUNT is not observed by any existing case.

**The RIGHT seam, extracted so the planner cannot pick the wrong one.** Every flush-path read goes
through `handle->firestarter_get_data`, which the suite already replaces with a test-local mock:
```cpp
// firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp:54-57, 90-102
#define EEPROM28C_PLANTED_SENTINEL 0xFFFFFFFFUL
static uint32_t s_planted_base_address;
static uint32_t s_planted_stale_address;
static uint8_t  s_planted_stale_value;
...
/* Address-keyed planted get_data mock. ... Dispatch is on ADDRESS only, never on call order. */
static uint8_t mock_get_data_planted(firestarter_handle_t*, uint32_t address) {
    if (s_planted_stale_address != EEPROM28C_PLANTED_SENTINEL && address == s_planted_stale_address) {
        return s_planted_stale_value;
    }
    return (uint8_t)(0x10 + (address - s_planted_base_address));
}
```
```c
// firestarter/src/proms/eeprom_28c.cpp:672-675 (comment) — the production guarantee
// Every read goes through handle->firestarter_get_data (memory_get_data) --
// never a direct rurp_* read, never fu_flash_data_poll() ...
```
**What the executor must invent:** a `static uint32_t s_get_data_calls;` (reset in `setUp` beside the
existing sentinel resets at `:83`/`:243`/`:292`) incremented inside the mock — or a second mock
wrapping it. **The arithmetic that makes the count a flush oracle, derived from the two production
readers:**
```c
// eeprom_28c.cpp:676-688  wait_for_page_write — 2 reads per flush on a clean poll (double-read idiom)
        observed = handle->firestarter_get_data(handle, address);
        if ((observed & AT28C_DQ7_MASK) == (expected & AT28C_DQ7_MASK)) {
            uint8_t confirm = handle->firestarter_get_data(handle, address);
// eeprom_28c.cpp:722-726  verify_page_readback — exactly 1 read per buffer byte, windows disjoint
    for (uint32_t k = first_index; k <= last_index; k++) {
        uint8_t observed = handle->firestarter_get_data(handle, addr);
```
So for a clean write: **`total_get_data_calls == 2 * flushes + data_size`**. On the recommended
geometry (base 0, `data_size` 128): page 64 → `2*2+128 = 132`; page 128 → `2*1+128 = 130`; field
absent → 132 (identical to the 64 case, PGSZ-02's fallback leg). Three distinct, non-timing numbers.

**The WRONG seam, named so the plan can forbid it:** `clear_bus_recording()` /
`bus_recording_count()` / `recorded_reg()` / `recorded_data()` (`test_val_eeprom28c.cpp:44-48`)
capture `(reg, data)` pairs from `rurp_write_to_register` — **register writes, never reads** — and cap
at 256 entries (`:208`). `host_stubs.cpp:28` defines only `HOST_STUBS_RECORD_BUS`, not
`HOST_STUBS_REAL_REGISTER_UTILS`, so there is no elision either. Do not count flushes there.

**Handle factory to reuse unchanged** (`h = {}` zero-inits, so a new field defaults to 0 = the
"absent" state with no factory edit):
```cpp
// test_val_eeprom28c.cpp:111-125
static firestarter_handle_t make_write_handle(uint32_t address, uint32_t data_size) {
    firestarter_handle_t h = {};
    h.protocol = 0x0D;
    h.cmd = CMD_WRITE;
    h.response_code = RESPONSE_CODE_OK;
    h.chip_id = 0;
    h.mem_size = SDP_BUS_CONFIGS[0].mem_size;      // AT28C256 / DIP28_28C256, 32768
    h.bus_config = SDP_BUS_CONFIGS[0].bus_config;
    h.address = address;
    h.data_size = data_size;
    for (uint32_t k = 0; k < data_size; k++) {
        h.data_buffer[k] = (char)(0x10 + k);
    }
    return h;
}
```
**Case shape to copy — the multi-drive, fresh-handle-per-drive, isolation-control pattern**
(`test_fix06_page_boundary_window_readback`, `:255-303`), which is also the case whose flush geometry
a badly-placed mask would silently change:
```cpp
/* Page-boundary window reset. Geometry: base address 56, data_size 16, so
 * with PAGE_SIZE 64 the write flushes twice -- once at address 63 on
 * page_end (buffer window 0..7, addresses 56..63) and once at the last
 * byte (window 8..15, addresses 64..71). Driven three times with a fresh
 * handle and freshly reset mock state each time. */
void test_fix06_page_boundary_window_readback(void) {
    /* Drive 1: plant a stale byte inside the FIRST window (address 59). */
    s_planted_base_address = 56;
    s_planted_stale_address = 59;
    s_planted_stale_value = 0xFF;
    {
        firestarter_handle_t h = make_write_handle(56, 16);
        configure_memory(&h);                        // <- NOTE: configure_memory, then
        h.firestarter_get_data = mock_get_data_planted;
        h.firestarter_operation_main(&h);            // <- operation_MAIN. NEVER operation_init.
        TEST_ASSERT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
            "a stale byte inside the first flush window (address 59) must be caught");
    }
    ... Drive 2 (second window, address 65) ...
    /* Drive 3: plant nothing, so the two-window geometry itself is shown
     * not to be the cause of the ERROR asserted above. */
```
The `configure_memory` → `operation_main` pair, with **no `operation_init`**, is repeated at `:218`,
`:249` and `:269`. This is the measurement behind §9(b)'s resolve-site decision. Each new case also
needs a `RUN_TEST` line in `main()` (`:305+`).

**Timing stubs are already handled** (`:69-79` mocks `delayMicroseconds`, `delay`, `millis`, `micros`
with `AlwaysReturn(0)`), and D-09 asserts counts, not time — so the "native stubs record no time"
trap does not weaken it.

**D-10's mechanical `PAGE_SIZE` comment refs in this file:** `:204`, `:256` (and
`test_eeprom28c_sdp.cpp:1532,1543,1603`).

### 14b. `firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp` — parse cases

**Analog: exact, same file.** The `json_parse` harness already exists (`:53-73`):
```cpp
/* Build a zero-initialized handle suitable for JSON parse tests. */
static firestarter_handle_t make_handle(uint8_t cmd) {
    firestarter_handle_t h = {};   /* zero-init: ensures new fields default 0 */
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

/* Helper: parse a JSON string into a handle, return the json_parse result.
 * Note: json_init() uses sizeof(tokens)/sizeof(tokens[0]) which is wrong when
 * tokens is a pointer arg ... Call jsmn_parse directly with NUMBER_JSNM_TOKENS ... */
static int parse_json(const char* json_str, firestarter_handle_t* handle) {
    jsmntok_t tokens[NUMBER_JSNM_TOKENS];
    jsmn_parser parser;
    jsmn_init(&parser);
    int token_count = jsmn_parse(&parser, json_str, strlen(json_str), tokens, NUMBER_JSNM_TOKENS);
    if (token_count < 0) return token_count;
    return json_parse(json_str, tokens, token_count, handle);
}
```
Three existing cases map 1:1 onto the three new ones: `test_read_settling_us_parsed_from_json`
(`:76-82`) → `{"cmd":2,"page-size":128}` stores 128; `test_read_timing_fields_default_zero_when_absent`
(`:94-101`) → absent key leaves 0 (D-05's reset leg);
`test_read_settling_us_capped_at_max` (`:105-114`) → **not** copied (D-07 validates in the handler).
D-11's unknown-key case is new but trivial: place an unknown key **before** a known one and assert the
known one still lands, because the skip's failure mode is token-walk desynchronisation
(`json_parser.c:319-321`), not a crash. The stale `json_init` comment at `:62-64` is corrected by the
folded todo's deletion.

---

## Shared Patterns

### S1. Non-vacuity is mandatory on every gate
**Sources:** `test_sdp_db_invariant.py:31-53` (synthetic-flip legs 7 and 9),
`test_cap03_ack_layout_parity.py:563,711` (planted-fixture legs),
`146-check-claims.py:59-62` (Phase 139 measured a windowed scanner passing four planted overclaims),
`149-RESEARCH.md` "assert keys, ... the regex drifted, not the source".
**Apply to:** every new test module and both gate scripts. Shape: extract/select first, `assert
<non-empty>` on the extraction, then assert the property; and for every property, one committed plant
or synthetic that makes the *same shared helper* raise.

### S2. Offenders list, then assert empty, naming every offender
**Source:** `test_sdp_db_invariant.py:100-113` and `:321-332`.
**Apply to:** `test_page_size_invariants.py`, `test_json_key_parity.py`'s two-way legs.
Never `assert all(...)` — the message must name the chips/keys.

### S3. `requires_fw` + `fw_path` for anything reading the firmware tree; never a bespoke proxy
**Source:** `firestarter_app/tests/fw_presence.py:10-17,77-140`, inventoried in `tests/scan_paths.py`.
**Apply to:** `test_json_key_parity.py` (live leg only — planted legs stay undecorated).
`fw_path` raises `MissingScanTargetError` (hard failure) when the repo is present but the path is not,
which is the rename detector. Env binding is at **import**, so `monkeypatch.setenv` is inert; use a
subprocess (`tests/test_fw_presence.py:80,100`) or `tools/ci_parity.sh` leg 1.

### S4. Goldens are delta-listed or re-derived with a seen-to-fail transcript, never re-baselined
**Sources:** `tests/test_wire_dict_equivalence.py:153-165`'s RED message;
`firestarter/scripts/baseline/size_baseline_base01.json`'s `re_anchor_note` (*"a green `--policy
merge05` run after this commit means the anchor moved, not that flash growth stayed inside the
original v1.24 band"*).
**Apply to:** the wire-delta fixture (D-17) and the MERGE-05 exemption (D-12). Both need a committed
RED transcript and a committed GREEN transcript.

### S5. One named, single-consumer constant carrying its own justification
**Source:** `check_size_baseline.py:125-167` (comment block + `_merge05_flash_allowance` as the sole
reader).
**Apply to:** the new MERGE-05 exemption, the renamed `AT28C_PAGE_SIZE_FALLBACK` (D-10), and the
handle field/mask (D-06). Keep each single-sourced; the fallback's 4 refs are `eeprom_28c.cpp:33`,
`:634` plus comment refs in 3 native test files.

### S6. Artifacts paste commands with `; echo EXIT=$?` and their literal output
**Source:** `148-DB-DIFF.md` (every `###` heading).
**Apply to:** `149-PAGE-SIZE.md` and every `149-NN-SUMMARY.md`. Corrections are appended as bold
**Correction (…)** paragraphs, never by rewriting earlier text.

---

## No Analog Found

| File | Role | Data Flow | What the executor must invent |
|---|---|---|---|
| flush-count observability in `firestarter/test/native/avr/test_val_eeprom28c/test_val_eeprom28c.cpp` | test | streaming | A suite-local call counter inside `mock_get_data_planted` (reset in `setUp` beside the existing sentinel resets), plus the `2*flushes + data_size` arithmetic above. The existing suite has **no** counter and its bus recorder is the wrong seam (register writes, capped at 256). Everything else — handle factory, mock, drive/isolation-control case shape — is copied. |

---

## Metadata

**Analog search scope:** `firestarter_app/tests/`, `firestarter_app/tests/{fixtures,golden}/`,
`firestarter_app/tools/`, `firestarter_app/firestarter/`, `firestarter/src/`, `firestarter/include/`,
`firestarter/test/native/avr/`, `firestarter/scripts/`, `firestarter/tests/{,fixtures}/`,
`.planning/phases/{146,148}-*/`.
**Files read this session:** 18 (plus `149-CONTEXT.md` and `149-RESEARCH.md` in full).
**Read-only:** no source file, submodule branch, or generated artifact was modified; `build_db.py` was
never invoked.
**Pattern extraction date:** 2026-08-19
