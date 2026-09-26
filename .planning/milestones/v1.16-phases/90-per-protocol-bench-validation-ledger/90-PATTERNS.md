# Phase 90: Per-Protocol Bench Validation + Ledger - Pattern Map

**Mapped:** 2026-06-26
**Files analyzed:** 5 new artifacts (doc + checker + bench evidence)
**Analogs found:** 5 / 5 (every new file has a strong in-repo analog)

> This is a **doc-authoring + bench-validation** phase (D-10 frozen world). NO firmware
> or host *source* file is created or modified. The only new code is one read-only
> ledger self-consistency checker (Wave-0 gap from RESEARCH §Validation Architecture).
> Everything else is data artifacts under the new `.planning/v1.16/ledger/` tree.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` | config/data artifact (cross-reference ledger) | transform (compose-by-key, no copy) | `firestarter_app/tools/validation_matrix_spec.json` (+ `.planning/v1.15/bench/EVIDENCE.json` cell schema) | exact (same family-row / cell-row JSON shape) |
| `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` | doc (human view of the JSON) | transform (render rows → table) | `.planning/v1.15/bench/EVIDENCE.md` | exact (same JSON→markdown-table companion convention) |
| `tools/check_ledger.py` (host or meta; planner discretion) | test/gate (self-consistency checker) | batch (load JSON → assert → exit-code) | `firestarter_app/tools/diff_db.py` + `firestarter_app/tools/check_dispatch.py` | role-match (frozen-world JSON-vs-rule gate; same 0/1/2 exit-code contract) |
| `.planning/v1.16/ledger/bench/<chip>-{read,wcA,wcB}/` (per-run binaries / SHAs) | bench evidence artifacts | file-I/O (consistency-check + write-cycle captures) | `.planning/v1.15/bench/` layout + `tools/gen_test_image.py` write-cycle convention | exact (reuses the v1.15 phase82 harness verbatim) |
| `.planning/v1.16/ledger/bench/BENCH-LOG.md` | doc (per-task evidence anchor) | event-driven (per-op log entry) | `.planning/v1.15/bench/EVIDENCE.md` SAFE-01 precondition blocks | role-match (per-task port/Rev/cmd/RC/SHA/operator-authorize log) |

> `.planning/v1.16/` does **not** exist yet — Phase 90 creates the whole tree. `[VERIFIED: ls — dir absent]`

## Pattern Assignments

### `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` (data artifact, transform)

**Analogs:** `firestarter_app/tools/validation_matrix_spec.json` (the by-family cross-ref target + its `families[]` row shape) and `.planning/v1.15/bench/EVIDENCE.json` (the by-chip cross-ref target + its `cells[]` / `locked_columns` shape).

**Cross-ref target 1 — `validation_matrix_spec.json` family row** (lines 4-27) — JOIN KEY is `family.id` + decimal-protocol membership:
```jsonc
{
  "id": "eprom",                          // ← ledger row references this via matrix_family
  "handler": "configure_eprom",
  "protocols": [7, 8, 11],                // DECIMAL (0x07/0x08/0x0B) — note for join
  "rep_chip": "W27C512",
  "tier1": { ... }, "tier2": { ... }, "tier3": { "boards": ["leonardo"], "skip_boards": ["uno328pb"] }
}
```
> Confirmed family ids the ledger joins to: `eprom`(7,8,11), `eeprom28c`(13), `flash3`(6), `flash4`(5), `flash_intel`(16), `sram`(14,39,40,41). **0x34 has NO family entry** → ledger row carries `matrix_family: null`. `[VERIFIED: validation_matrix_spec.json read]`

**Cross-ref target 2 — `EVIDENCE.json` cell** (read-cell lines 73-87; write-cycle-cell lines ~195-203) — JOIN KEY is `cell.chip` + `op`. Reference by key; **do NOT copy the `sha256`** (D-04):
```jsonc
// read cell (op "read+blank_check"):
{ "chip": "W27C512", "family": "0x07 (EPROM_STD / EEPROM)", "board": "leonardo", "shield": "Rev 2.0",
  "op": "read+blank_check", "sha256": "9376dcd8…97ad23c8", "verdict": "PASS", "read_count": 3 }
// write-cycle cell (op "write_A+verify_A → write_B+verify_B"):
{ "op": "write_A+verify_A → write_B+verify_B",
  "sha256_image_A": "604d9570…1645d637", "sha256_image_B": "e16b2a5b…dc326ab5", "cr01_risk": "none" }
```
> EVIDENCE labels FM1608 `family: "0x40 (SRAM_STD / FRAM)"` — `0x40` is **decimal-40 = hex 0x28** (NAME-04 conflation, retired). The ledger uses `0x28`; may footnote the EVIDENCE label. `[VERIFIED: PROTOCOLS.md §1.10]`

**Recommended row shape** (RESEARCH §"JSON Schema Proposal", lines 259-309 — this is the planner's authoritative starting shape; field names are D-04 discretion):
```jsonc
{
  "schema_version": 1, "milestone": "v1.16",
  "firmware_under_test": { "submodule_commit": "a296195", "flash_bytes": 25136, "flash_pct": 87.7,
                           "version_string_caveat": "reports 3.0.0b10; build is v1.16 recompose" },
  "oracle": "leonardo+Rev2.0",
  "composes_with": { "v1_13_matrix": "firestarter_app/tools/validation_matrix_spec.json",
                     "v1_15_evidence": ".planning/v1.15/bench/EVIDENCE.json" },
  "milestone_flash_impact": { "net_delta_bytes": -518, "baseline_bytes": 25654,
                              "per_primitive": { "P7": 0, "P4": -164, "P3": -402, "P5": 2, "CR01_fix": 46 } },
  "rows": [ {
      "bucket": "0x05", "proposed_name": "FLASH-AMD-STD",
      "handler": "configure_flash4()", "handler_file": "flash_type_4.cpp",
      "datasheet_slug": "0x05-FLASH-AMD-STD", "datasheet_citation": "datasheets/0x05-FLASH-AMD-STD/W29C020.pdf",
      "matrix_family": "flash4", "matrix_protocols_dec": [5],   // ← KEY into matrix_spec, not copied data
      "primitives_used": ["P4", "P5", "P7"],
      "verification_status": "PASS",                            // enum: PASS|UNVERIFIED|FAIL-INVESTIGATE|open-defect-carried
      "oracle": "leonardo+Rev2.0",                             // REQUIRED non-null for PASS (D-09)
      "on_hand_chip": "W29C020",
      "evidence": {
        "v1_15_read_cell": { "evidence_chip": "W29C020", "op": "read+blank_check" },        // KEY, not SHA
        "v1_15_writecycle_cell": { "evidence_chip": "W29C020", "op": "write_A+verify_A → write_B+verify_B" },
        "p90_artifacts": [".planning/v1.16/ledger/bench/W29C020-read/", ".planning/v1.16/ledger/bench/W29C020-wcB/"],
        "p90_read_sha_matches_v115": true, "p90_writecycle_sha_matches_v115": true } }
    // … one row per the 12 buckets …
  ],
  "open_defects": [ { "id": "CR-01", "chip": "W29C040", "bucket": "0x05",
      "disposition": "<verbatim from STATE.md>", "source_link": ".planning/STATE.md#deferred-items",
      "status_changed": false } ]
}
```

**Row identities (all 12 buckets — every row must be present):** see RESEARCH §"12-Bucket Row Identities" (lines 132-151) for the per-bucket handler/file/datasheet-slug/rep-chip table. PASS targets: 0x05/W29C020, 0x06/SST39SF040, 0x07/W27C512, 0x28/FM1608. UNVERIFIED (no-silicon, full rows): 0x0D/AT28C256, 0x0E/DS1245Y, 0x10/Intel-28F010, 0x27/6116, 0x29/DS1245Y, 0x34/X88C64. Open-defect carries: CR-01/W29C040 (0x05), FUT-06/AM27C020 (0x08), FUT-03/2516 (0x0B).

**Primitives-used column source:** RESEARCH §"Primitives Used Per Bucket" (lines 162-186), e.g. 0x05→`[P4,P5,P7]`, 0x07→`[P4,P3]`, SRAM buckets→`[]` (no primitive use).

---

### `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` (doc, transform)

**Analog:** `.planning/v1.15/bench/EVIDENCE.md` — the human-readable companion to `EVIDENCE.json`.

**Pattern — header block + markdown table mirroring the JSON rows** (EVIDENCE.md lines 1-3, then the sweep table at line 51+):
```markdown
# v1.15 Bench Evidence — Phase 81 Non-Destructive Read Sweep
**Harness version:** 81 · **Board:** leonardo · **Shield:** Rev 2.0 · **Generated:** 2026-06-23/24
...
| # | Chip | Family / Algorithm | Board+Shield | Op | Blank-state | Read N | SHA-256 | Verdict | Anomalies |
|---|------|--------------------|--------------|----|-------------|--------|---------|---------|-----------|
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | … | 3 | `9376dcd8…97ad23c8` | **PASS** | … |
```
**Apply:** render one markdown table row per ledger bucket (bucket, proposed name, handler, primitives used, on-hand chip, verification_status, evidence refs). The `.md` is the human view of the **same rows** as the `.json` — keep them in lockstep (same pattern as the EVIDENCE.json/.md pair, and the SHIELD-REVISIONS lockstep convention noted in firestarter_app/CLAUDE.md).

---

### `tools/check_ledger.py` (test/gate, batch) — Wave-0 gap

**Analogs:** `firestarter_app/tools/diff_db.py` and `firestarter_app/tools/check_dispatch.py` — the two existing read-only frozen-world JSON gates. Copy their module-docstring-exit-code-contract + load-or-fail-2 + main()-asserts-then-exits structure.

**Exit-code contract pattern** (`diff_db.py` lines 11-20 — the canonical 0/1/2 contract; reuse verbatim semantics):
```python
"""
Exit codes:
  0 — all changed chips explained …
  1 — at least one chip has an unexplained diff …  (the real BLOCK)
  2 — infrastructure error: a required input file could not be loaded or parsed
      … Distinct from 1 so a CI consumer does not confuse a missing input with a real diff BLOCK (WR-04).
"""
```
**Apply to check_ledger:** `0` = all LEDGER-01/02/03 assertions pass; `1` = a structural violation (join key unresolved, a PASS row missing oracle/evidence, a SHA copied verbatim, a defect row with `status_changed != false`, a missing bucket); `2` = a required input JSON (ledger, EVIDENCE.json, validation_matrix_spec.json) could not be loaded.

**Load-or-exit-2 helper** (`diff_db.py` lines 474-486 — copy this exactly):
```python
def _load_db(path, label):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot load {label} {path}: {e}", file=sys.stderr)
        sys.exit(2)
```

**Env-overridable path constants** (`diff_db.py` lines 29-39 / `check_dispatch.py` lines 24-33 — both repos use this seam for the FIRESTARTER_CONFIG_DIR test convention):
```python
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
DB_FILE = os.environ.get("FIRESTARTER_DB_FILE", os.path.join(_DATA_DIR, "chip_database.json"))
BASELINE_FILE = os.environ.get("FIRESTARTER_BASELINE_FILE", os.path.join(_BASELINE_DIR, "..."))
```
**Apply:** make the ledger path + the two upstream paths env-overridable (e.g. `FIRESTARTER_LEDGER_FILE`, `FIRESTARTER_EVIDENCE_FILE`, `FIRESTARTER_MATRIX_FILE`) so the checker is testable against fixtures.

**main()-collects-then-reports-then-exits pattern** (`diff_db.py` lines 489-682 / `check_dispatch.py` lines 174+ — collect violations into named lists, print a grouped report, `sys.exit(1)` iff any list is non-empty):
```python
def main():
    bl_db = _load_db(BASELINE_FILE, "baseline")   # → _load_db(LEDGER_FILE…) etc.
    ...
    failures = list(unexplained) + missing_chips
    if failures:
        print(f"FAIL: …"); sys.exit(1)
    print(f"PASS: …")
```
**The specific assertions to encode** (RESEARCH §Validation Architecture "Phase Requirements → Test Map", lines 503-507):
- LEDGER-01: every `rows[].matrix_family` ∈ `validation_matrix_spec families[].id` (or `null` for 0x34); every `evidence.*_cell.evidence_chip` ∈ `EVIDENCE.json cells[].chip`; no raw 64-hex SHA string appears anywhere in the ledger (the no-copy guard).
- LEDGER-02 / D-09: for every `verification_status == "PASS"` → `oracle == "leonardo+Rev2.0"` AND `evidence.p90_artifacts` non-empty AND both `p90_*_sha_matches_v115 == true`.
- LEDGER-03: exactly `{0x0D,0x0E,0x10,0x27,0x29,0x34}` carry `UNVERIFIED`; `open_defects[].status_changed == false`; all 12 buckets present.

> **Location decision (planner):** if placed in `firestarter_app/tools/`, mind the py3.11 CI gate (ruff check + ruff format --check + the strict-mypy modules) — see firestarter_app/CLAUDE.md "Tooling gate (v1.8)" and RESEARCH Pitfall 4. If placed under `.planning/v1.16/ledger/` (meta), it escapes the host CI gate. RESEARCH leaves this to planner discretion.

> **Anti-pattern to avoid (do NOT replicate diff_db's complexity):** `diff_db.py` carries a large `_RATIONALES` / `_classify_diff` root-cause engine — that is specific to per-chip DB diffing and is NOT needed here. Copy only the **structure** (docstring exit-code contract, `_load_db`, env paths, collect→report→exit). The ledger checker is a flat set of `jq`-style assertions.

---

### `.planning/v1.16/ledger/bench/<chip>-{read,wcA,wcB}/` + images (bench evidence, file-I/O)

**Analog:** the v1.15 `.planning/v1.15/bench/` layout + the `phase82` write-cycle convention encoded in `EVIDENCE.json` (lines 27-44) and `tools/gen_test_image.py`.

**Image generation pattern** (`gen_test_image.py` lines 9-21, 30-49 — the deterministic seed-1/seed-2 oracle; reuse verbatim):
```python
# CLI: python tools/gen_test_image.py <size_bytes> <seed> <output_path>   (prints SHA-256)
# seed=1 = image A, seed=2 = image B by convention
def generate_image(size_bytes: int, seed: int) -> bytes:
    rng = random.Random(seed)
    return bytes(rng.randint(0, 255) for _ in range(size_bytes))
```
> Chip sizes (RESEARCH line 227): W29C020=262144, SST39SF040=524288, W27C512=65536, FM1608=8192.
> Generator output is byte-stable across py3.9/3.11/3.12 (pure stdlib `random.Random`) — the printed SHA must equal the v1.15 baseline image-A/B SHA **before** any chip is touched. `[VERIFIED: gen_test_image.py source]`

**Read-SHA capture pattern** — `firestarter dev consistency-check` (handler `cli_handlers.py:1100-1134`; N reads → SHA divergence → exit 0/1/2):
```bash
firestarter dev consistency-check <CHIP> --runs 3 --output-dir .planning/v1.16/ledger/bench/<chip>-read/
# verdict: 0=PASS(1 distinct SHA) / 1=FAIL(divergent) / 2=hw-error  (sys.exit(verdict_int), NOT bool-wrap)
```

**Write-cycle A→B capture pattern** — `firestarter dev write-cycle` (handler `cli_handlers.py:1161-1187`; erase→write→readback N → SHA == source → exit 0/1/2). Two invocations = the A→B auto-erase proof:
```bash
firestarter dev write-cycle <CHIP> <img_A.bin> --runs 1 --output-dir .planning/v1.16/ledger/bench/<chip>-wcA/
firestarter dev write-cycle <CHIP> <img_B.bin> --runs 1 --output-dir .planning/v1.16/ledger/bench/<chip>-wcB/
# B over A with NO explicit erase; clean B verify == auto-erase proof; readback SHA must == v1.15 baseline wc-SHA
```
> **FM1608/FRAM exception** (RESEARCH Pitfall 1, lines 368-372): `dev write-cycle` erase is "Not supported" on FRAM → use the v1.15 method: `firestarter write FM1608 -b <img_A.bin>` then `write -b <img_B.bin>` then `dev consistency-check FM1608 --runs 3`.

**Verdict taxonomy + storage convention** (EVIDENCE.json `phase82` block, lines 27-44) — carry forward, swap `_p82` → `_p90`:
```jsonc
"verdict_taxonomy": { "PASS": "exits 0, B SHA-256 matches B source, no residual A-bits", "FAIL (genuine)": "…", "ANOMALY": "…" },
"storage_convention": "/tmp/firestarter_bench_p82/<chip>_img_A.bin (seed=1) and _img_B.bin (seed=2)"
```
> **D-01 PASS = byte-identical to the v1.15 baseline SHA** (hard-coded targets in RESEARCH lines 123-128). A mismatch → FAIL/INVESTIGATE, never auto-passed (D-03). **Sequencing (RESEARCH line 130): run the read regression BEFORE the write-cycle per chip** — the write overwrites the contents the read-SHA baseline measured.

---

### `.planning/v1.16/ledger/bench/BENCH-LOG.md` (doc, event-driven)

**Analog:** the `EVIDENCE.md` SAFE-01 / per-session precondition blocks (lines 5-50) — the per-task port/Rev/calibration/authorization log.

**Pattern — per-task precondition block** (EVIDENCE.md lines 36-41):
```markdown
### Phase 82 SAFE-01 Gate — Plan 82-02 write session (operator sign-off 2026-06-24)
- **`controller:`** leonardo on **/dev/ttyACM0** (firmware `firestarter fw`), firmware 3.0.0b8
- **Shield:** Rev 2.0 — **operator-confirmed silkscreen** this session
- **Calibration (live readback):** R1=270000, R2=44000 (NOT the 1000 default → VPP read trustworthy)
- **Authorization:** destructive A→B write session cleared; chips seated one at a time on Leonardo + Rev 2.0
```
**Apply:** one block per bench task with port identity (re-verify — ttyACM* shuffles), operator-confirmed Rev 2.0 silkscreen, the command run, RC, captured SHA, SHA-matches-v115 verdict, and the operator-authorize note. This IS the D-09 non-empty evidence reference.

## Shared Patterns

### Firmware-under-test identity (record the commit, NOT the version string)
**Source:** RESEARCH lines 195-199, 346.
**Apply to:** PROTOCOL-LEDGER.json `firmware_under_test`, BENCH-LOG.md every session block.
```bash
git -C firestarter rev-parse HEAD     # must == a296195 (Phase 89 HEAD)
cd firestarter && pio run -e leonardo # expect Flash 87.7% (25136 B / 28672 B)
```
> The VERSION STRING still reports `3.0.0b10` (Phase 84 did not bump FIRMWARE_VERSION). Record the **submodule commit a296195** as the build identity — never trust the version string.

### Compose-by-cross-reference, never copy (D-04)
**Source:** the `validation_matrix_spec.json` family ids + `EVIDENCE.json` cell `chip` keys are the SINGLE SOURCE OF TRUTH; the ledger holds only keys.
**Apply to:** every PASS row's `evidence` block (keys only) and `matrix_family`/`matrix_protocols_dec`. The `check_ledger.py` no-raw-SHA assertion enforces this mechanically.

### Frozen-world rerun-to-confirm gates (D-10 — no source change)
**Source:** `diff_db.py`, `check_dispatch.py`, `pio test -e native` (RESEARCH lines 431-438).
**Apply to:** the phase gate — rerun, confirm green, change nothing.
```bash
cd firestarter && pio test -e native            # expect 105/105 green
cd firestarter_app && python tools/check_dispatch.py && python tools/diff_db.py   # exit 0 each
git -C firestarter_app diff --quiet && echo HOST-CLEAN
git -C firestarter diff --quiet && echo FW-CLEAN
```

### SAFE-04 verify-present-only (D-08 — post-recompose locations)
**Source:** RESEARCH §"SAFE-04 Verification Targets" (lines 396-406). CONTEXT line numbers are PRE-recompose; verify these CURRENT locations (grep only, no edits):
- Over-voltage `+500` mV gate: `firestarter/src/proms/primitives.cpp:106` (moved into `vpp_check_window` in P3) — NOT the CONTEXT `eprom.cpp:282`.
- Host support-status guard: `firestarter_app/firestarter/chip_resolver.py` `resolve_chip()` (~line 55).
- 2516 stays `verification_status=UNVERIFIED` in `chip_database.json`.
```bash
grep -n "vpp_mv > (uint32_t)handle->vpp_mv + 500" firestarter/src/proms/primitives.cpp
grep -n "support_status" firestarter_app/firestarter/chip_resolver.py
```

### Bench preconditions per task (memory-anchored)
**Source:** `feedback_verify_port_identity_each_task`, `user_shield_revisions`, `feedback_chip_out_before_sideload`.
**Apply to:** every BENCH-LOG.md task block — re-verify `controller:` identity (ttyACM* shuffles on replug), operator-confirm Rev 2.0 silkscreen (EEPROM hw byte cannot distinguish revs), Leonardo is EXEMPT from chip-out-before-sideload (Uno-class only) but operator still authorizes each flash (D-05/D-06).

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| — | — | — | None. Every Phase-90 artifact maps to a strong in-repo analog (the v1.15 bench harness + the frozen-world gate scripts + the matrix/EVIDENCE schemas). |

## Metadata

**Analog search scope:** `firestarter_app/tools/` (gate scripts + matrix + image generator), `firestarter_app/firestarter/cli_handlers.py` (bench command handlers), `.planning/v1.15/bench/` (EVIDENCE schema + bench layout), `.planning/STATE.md` (deferred-items dispositions).
**Files scanned:** 9 (diff_db.py, check_dispatch.py, gen_test_image.py, validation_matrix_spec.json, EVIDENCE.json, EVIDENCE.md, cli_handlers.py, STATE.md, both CLAUDE.md files).
**Pattern extraction date:** 2026-06-26
