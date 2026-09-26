# Phase 99: BENCH + LEDGER — Graduation Gate, Evidence & Ledger Update - Pattern Map

**Mapped:** 2026-07-01
**Files analyzed:** 8 (2 code, 4 data/doc, 2 new-artifact-dir)
**Analogs found:** 8 / 8 (every deliverable has an in-repo analog; the "new" work is EXTEND/EDIT, not net-new invention)

> **Read this first (planner):** This is a hardware-bench + ledger-update phase. There is essentially
> ONE code task — extending `check_ledger.py` + `test_check_ledger.py` to admit a v1.18-native `0x08`
> graduation (written-image SHA == read-back SHA) without a v1.15 write baseline, keeping the 11
> existing rows green. Everything else is (a) irreducibly-physical operator bench steps with NO code
> analog, or (b) JSON/Markdown data edits whose analog is an existing PASS row / evidence cell. Do NOT
> scaffold new subsystems. Every excerpt below is a pattern to *copy and minimally extend*, not rewrite.

---

## File Classification

| File (create/modify) | Role | Data Flow | Closest Analog | Match Quality |
|----------------------|------|-----------|----------------|---------------|
| `.planning/v1.16/ledger/tools/check_ledger.py` | gate script (validator) | transform / batch-assert | *self* (extend `_assert_ledger02_d09` + `_VALID_STATUSES`) | exact (edit-in-place) |
| `.planning/v1.16/ledger/tools/test_check_ledger.py` | test | request-response (subprocess+exit-code) | *self* (existing 5 tests + fixtures pattern) | exact (extend) |
| `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` | data record (canonical ledger) | CRUD (row + open_defects edit) | `0x05`/`0x07` PASS row (same file) | exact |
| `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` | doc mirror | CRUD (lockstep table + defect block edit) | `0x07` row + FUT-06 block (same file) | exact |
| `.planning/v1.18/bench/EVIDENCE.json` | evidence record | CRUD (append/extend AM27C020 P99 cell) | Phase-97 AM27C020 + W27C512 cells (same file) | exact |
| `.planning/v1.18/bench/EVIDENCE.md` | doc mirror | CRUD | Phase-97 EVIDENCE.md (same file) | exact |
| `.planning/v1.18/bench/AM27C020-graduation/SHA256SUMS.txt` | evidence artifact (NEW dir) | file-I/O | `.planning/v1.16/ledger/bench/W27C512-fix/SHA256SUMS.txt` | exact (mirror convention) |
| `.planning/v1.18/bench/check_graduation.py` (OPTIONAL) | gate script | transform | `check_signature.py` (Phase-97 sibling) | role-match |

### No code analog (hardware / manual — do NOT invent one)

| Step | Why no analog |
|------|---------------|
| Seat AM27C020, set VPP pot to 12.75V±0.25, DMM at socket pin 1, confirm Rev-2.0 silkscreen | Irreducibly physical. Operator owns the pot (state target → operator says "done" → ONE confirmation read). No monitor loops. |
| Authorize each live `write -b` spend | Operator-gated bench action. |
| Reflash Leonardo to Phase-98 fix (`35706c2`) if `firestarter fw` shows an older commit | Physical (Leonardo is chip-out-EXEMPT); scripted invocation exists but the act is bench-side. |

The bench *invocations* (`firestarter write -b`, `verify`, `read`, `dev consistency-check`, `vpp`, `fw`,
`hw`, `config`, `gen_test_image.py`, `sha256sum`) are documented in 99-RESEARCH.md §Code Examples /
§Pattern 1 — the planner should cite those directly rather than duplicate them here; they are host-CLI
usage, not code the executor writes.

---

## Pattern Assignments

### `check_ledger.py` — the D-09 PASS constraint (gate script, transform) — THE central code task

**Analog:** *self* — `_assert_ledger02_d09` at `.planning/v1.16/ledger/tools/check_ledger.py:140-179`.
The current gate structurally CANNOT pass a graduated `0x08` row (Pitfall 2). Extend, don't rewrite.

**Status enum to extend** (lines 56-57):
```python
# Valid verification_status enum values
_VALID_STATUSES = {"PASS", "UNVERIFIED", "FAIL-INVESTIGATE", "open-defect-carried", "bench-pending"}
```
Two documented options (99-RESEARCH.md §Schema Tension / Claude's Discretion): (a) keep `PASS` but
teach `_assert_ledger02_d09` a v1.18-native evidence shape for the `0x08` bucket, or (b) add a distinct
status (e.g. `PASS-v1.18-native`) to this set with its own constraint. Recommend the minimal, tested change.

**The D-09 PASS constraint that must be extended** (lines 140-179 — the blocker):
```python
def _assert_ledger02_d09(ledger, violations):
    """LEDGER-02 / D-09: PASS rows must have oracle + non-empty evidence + both sha-match flags."""
    for row in ledger.get("rows", []):
        bucket = row.get("bucket", "<unknown>")
        status = row.get("verification_status")
        if status != "PASS":
            continue

        oracle = row.get("oracle")
        if oracle != "leonardo+Rev2.0":
            violations.append(...)          # oracle must be leonardo+Rev2.0

        evidence = row.get("evidence")
        if not isinstance(evidence, dict):
            violations.append(...); continue

        artifacts = evidence.get("p90_artifacts")
        if not artifacts:
            violations.append(...)          # non-empty artifacts required

        if evidence.get("p90_read_sha_matches_v115") is not True:
            violations.append(...)          # <-- 0x08 HAS a v1.15 read baseline (OK)
        if evidence.get("p90_writecycle_sha_matches_v115") is not True:
            violations.append(...)          # <-- 0x08 has NO v1.15 write baseline (THE TENSION)
```
**Extension shape (recommended, per §Schema Tension option a):** branch on `bucket == "0x08"` (or on the
presence of a `v1_18_writeverify_sha_selfconsistent` evidence key) so a v1.18-native graduation is
proven by written-image-SHA == read-back-SHA on the fixed firmware, keeping `oracle` + non-empty
`p90_artifacts` required. Do NOT force `p90_writecycle_sha_matches_v115: true` — that would fabricate a
v1.15 write baseline that does not exist (Anti-Pattern in §Common Pitfalls).

**The `status_changed is False` invariant for FUT-06** (lines 207-214 — Pitfall 3):
```python
    # (c) open_defects[].status_changed must be false
    for defect in ledger.get("open_defects", []):
        did = defect.get("id", "<unknown>")
        if defect.get("status_changed") is not False:
            violations.append(
                f"LEDGER-03: open_defect id={did!r} status_changed is not false ..."
            )
```
To *retire* FUT-06 on graduation, **remove** its block from `open_defects[]` (do NOT flip
`status_changed: true`). On deferral, keep the block, re-describe `disposition`, leave
`status_changed: false`.

**The D-04 no-copy SHA guard** (lines 59-60, 129-137 — Pitfall 4): the ledger must NEVER contain a raw
64-hex SHA — those live in EVIDENCE.json / SHA256SUMS.txt. Reference by artifact path + join key only:
```python
_RAW_SHA_RE = re.compile(r"\b[0-9a-f]{64}\b")
# ...
    serialized = json.dumps(ledger)
    sha_matches = _RAW_SHA_RE.findall(serialized)
    if sha_matches:
        violations.append(f"LEDGER-01 (D-04): raw 64-hex SHA string(s) found in ledger ...")
```

**Exit-code contract (unchanged):** 0 = OK / 0 contradictions, 1 = structural BLOCK, 2 = infra error.
Run: `python3 .planning/v1.16/ledger/tools/check_ledger.py ; echo "exit=$?"`.

---

### `test_check_ledger.py` — gate unit tests (test, subprocess+exit-code)

**Analog:** *self* — the existing 5 tests at `.planning/v1.16/ledger/tools/test_check_ledger.py`.
Extend to cover the new `0x08` graduation path; the 5 existing tests MUST stay green (they prove the
11-row status quo).

**Test harness pattern** (lines 39-65 — copy this shape for a new `0x08`-graduation test):
```python
def _run_checker(ledger_path, evidence_path=None, matrix_path=None):
    env = os.environ.copy()
    env["FIRESTARTER_LEDGER_FILE"] = ledger_path
    env["FIRESTARTER_EVIDENCE_FILE"] = evidence_path or _EVIDENCE_MIN
    env["FIRESTARTER_MATRIX_FILE"] = matrix_path or _MATRIX_MIN
    result = subprocess.run([sys.executable, _CHECKER], env=env, capture_output=True, text=True)
    return result

def _write_tmp_ledger(data):
    fd, path = tempfile.mkstemp(suffix=".json", prefix="ledger_test_")
    ...
```

**Mutate-the-valid-fixture pattern** (lines 89-107 — copy for the new positive/negative graduation test):
```python
def test_pass_row_missing_oracle_exits_1():
    ledger = _load_valid_ledger()
    for row in ledger["rows"]:
        if row.get("verification_status") == "PASS":
            row.pop("oracle", None)
            break
    path = _write_tmp_ledger(ledger)
    try:
        result = _run_checker(path)
    finally:
        os.unlink(path)
    assert result.returncode == 1, (...)
```
**New tests to add (§Validation Architecture Wave-0):**
1. A v1.18-native graduated `0x08` row (self-consistent SHA evidence, no v1.15 write baseline) → exit 0.
2. A `0x08` row claiming PASS but WITHOUT the new self-consistency evidence → exit 1 (honesty guard).
3. (If FUT-06 is retired) assert removing it from `open_defects[]` still yields exit 0.

**Fixtures** live at `.planning/v1.16/ledger/tools/fixtures/` — `ledger_valid.json` (12 rows, the `0x08`
row is `open-defect-carried` / `on_hand_chip: "AM27C020"`), `evidence_min.json`, `matrix_min.json`.
Extend the fixture (or mutate in-test) to model the graduated `0x08` row. The valid fixture's `0x05`
PASS row is the shape template for a graduated evidence block.

---

### `PROTOCOL-LEDGER.json` — the `0x08` row + FUT-06 (data record, CRUD)

**Analog:** the `0x05` / `0x07` PASS rows in the SAME file (`check_ledger.py`-green PASS shape) and the
current `0x08` `open-defect-carried` row.

**Current `0x08` row to edit** (`PROTOCOL-LEDGER.json:145-165`):
```json
{
  "bucket": "0x08",
  "proposed_name": "EPROM-QUICK",
  "handler": "configure_eprom()",
  "handler_file": "eprom.cpp",
  "matrix_family": "eprom",
  "matrix_protocols_dec": [8],
  "primitives_used": ["P4", "P3"],
  "verification_status": "open-defect-carried",
  "oracle": null,
  "on_hand_chip": null,
  "defect_ref": "FUT-06",
  "evidence": null
}
```

**Graduated PASS shape to copy from** (`0x07` row, `PROTOCOL-LEDGER.json:106-144`) — note the evidence
sub-object with `v1_15_read_cell`, `p90_artifacts` (path list, NEVER a raw SHA), and the two sha-match
flags. For the `0x08` graduation the evidence block must be the v1.18-native variant the gate extension
recognizes (self-consistency), with `oracle: "leonardo+Rev2.0"`, `on_hand_chip: "AM27C020"`, and
`p90_artifacts: [".planning/v1.18/bench/AM27C020-graduation/"]`.

**FUT-06 block to retire/re-record** (`PROTOCOL-LEDGER.json:351-357`):
```json
{
  "id": "FUT-06",
  "chip": "AM27C020",
  "bucket": "0x08",
  "disposition": "AM27C020 0x08 32-pin write/VPP path — deferred, RCA'd, not trivially fixable. ...",
  "source_link": ".planning/STATE.md#deferred-items / ...",
  "status_changed": false
}
```
On GRADUATE: remove this block (retirement lives in the graduated row's evidence citation). On DEFER:
keep the block, update `disposition`, keep `status_changed: false` (Pitfall 3).

---

### `PROTOCOL-LEDGER.md` — human-readable mirror (doc, CRUD lockstep)

**Analog:** the `0x07` PASS table row + the FUT-06 Open-Defects block in the SAME file. The `.md` and
`.json` carry the SAME rows and MUST be edited in lockstep (Runtime State Inventory).

**Bucket-table `0x08` row to edit** (`PROTOCOL-LEDGER.md:25`):
```
| `0x08` | EPROM-QUICK | `configure_eprom()` (`eprom.cpp`) | `eprom` [proto 8] | P4, P3 | — | **open-defect-carried** (FUT-06) | See Open Defects below |
```
Model the graduated cell on the `0x07` row (`PROTOCOL-LEDGER.md:24`): set On-Hand Chip = `AM27C020`,
Verification Status = `**PASS**` (or the chosen v1.18-native status), Evidence Refs = a prose citation
of `bench/AM27C020-graduation/` + method + firmware commit (NO raw SHA).

**Status legend** (`PROTOCOL-LEDGER.md:35-40`) — if a new status enum value is chosen, add its
one-line definition here to match the `.json` gate `_VALID_STATUSES`.

**FUT-06 Open-Defects block** (`PROTOCOL-LEDGER.md:64-70`): remove on graduate / re-describe on defer,
mirroring the `.json` edit.

---

### `EVIDENCE.json` — Phase-99 AM27C020 graduation cell (evidence record, CRUD)

**Analog:** the Phase-97 AM27C020 cell (pre-fix failure signature) and the W27C512 cell (a PASS
write→verify cell) in the SAME file `.planning/v1.18/bench/EVIDENCE.json`.

**Locked column schema to reuse** (`EVIDENCE.json:9-19`) — do NOT invent new columns:
```json
"locked_columns": ["chip", "family", "board", "shield", "blank_state", "op", "sha256", "verdict", "anomalies"]
```

**Cell shape to copy** — the W27C512 PASS cell (`EVIDENCE.json:51-64`) is the closest analog for a
successful write→verify (it carries `write_image_sha256`, `readback_sha256`, `vpp_adc_mv`, `verdict`):
```json
{
  "chip": "W27C512", "family": "0x07 (EPROM_STD)", "board": "leonardo", "shield": "Rev 2.0",
  "op": "differential_control_write",
  "write_image_sha256": "d9471636...",
  "readback_sha256": "d9471636... (first-4096 region; == image → byte-exact)",
  "vpp_adc_mv": "12000 (12.0–12.1V; W27C512 target 12.0V)",
  "verdict": "PASS — 0x07 write→verify→readback byte-exact ...",
  "sha256": "d9471636...", "anomalies": "..."
}
```
And the Phase-97 AM27C020 cell (`EVIDENCE.json:23-49`) carries the bench-discipline fields to reuse:
`controller`, `port`, `r1_readback` (270000), `r2_readback` (44000), `fw_commit`, `jp4_position`,
`pre_read_sha256`, `post_read_sha256`, plus the honest "not measured" DMM pattern:
```json
"dmm_pin1_v": "not measured — held-rail proxy blocked by DTR-reset-on-close tooling bug (...). VPP→pin-1 routing CONFIRMED by code RCA ...",
"vpp_adc_mv": "13000 (confirmed immediately pre-attempt; regulator stable)",
"bits_flipped": "0", "bad_bytes": "1/1", "retries": "20",
```
**Do NOT overwrite the Phase-97 RCA cell** (`check_signature.py` / `check_pre01.py` still read it).
Add a NEW Phase-99 cell (e.g. `op: "phase99_graduation"`) or a clearly-versioned field. For the
graduation cell, `write_image_sha256 == readback_sha256` is the graduation oracle; for a deferral, record
the failing-vs-fixed differential (0-bits again) — never fabricate (§Anti-Patterns).

---

### `EVIDENCE.md` — human-readable mirror (doc, CRUD)

**Analog:** the existing `.planning/v1.18/bench/EVIDENCE.md` (Phase-97 mirror). Add the Phase-99 cell
in the same section/table style; keep in lockstep with `EVIDENCE.json`.

---

### `AM27C020-graduation/SHA256SUMS.txt` — bench artifact (NEW dir, file-I/O)

**Analog:** `.planning/v1.16/ledger/bench/W27C512-fix/SHA256SUMS.txt` — the established SHA-artifact
convention (annotated comment header + `sha256sum` lines):
```
# W27C512 (0x07) FIX confirmation — Leonardo + RURP Rev 2.0 (operator returned, chip swapped in)
# Firmware: STOCK recompose a296195 (no firmware edit). Chip-ID check PASSED for W27C512 (0xDA08).
# Method: write A -> verify A (erase proof) -> write B -> verify B -> consistency-check N=3.
# v1.15 baseline image-B gate: e16b2a5b...
#
# writeA RC=0 ; verifyA RC=0 ; consistency-check N=3: 1 distinct SHA, PASS
#
e16b2a5b...  cc-w27/run_01.bin
e16b2a5b...  cc-w27/run_02.bin
```
For Phase 99: `mkdir -p .planning/v1.18/bench/AM27C020-graduation`, prepend a header with firmware
commit (`35706c2`), controller, shield (Rev 2.0), method (manual `write -b` → read/verify → SHA), and
verdict; then `sha256sum imgA.bin readback.bin >> SHA256SUMS.txt`. AM27C020 image size = **262144** bytes
via `gen_test_image.py 262144 <seed>`.

---

### `check_graduation.py` (OPTIONAL — recommended) — Phase-99 evidence gate

**Analog:** `.planning/v1.18/bench/check_signature.py` (Phase-97 sibling gate). Same shape: load
`EVIDENCE.json`, filter the AM27C020 P99 cell, assert required fields are filled (no "TBD") and
SHA-self-consistent, exit non-zero on any gap.
```python
EV = ".planning/v1.18/bench/EVIDENCE.json"
REQ = ["bad_bytes", "retries", "bits_flipped", "vpp_adc_mv", "dmm_pin1_v", "dmm_pin31_v", "post_read_sha256"]
def main() -> int:
    d = json.load(open(EV))
    cells = [c for c in d["cells"] if c["chip"] == "AM27C020"]
    ...
    missing = [k for k in REQ if "TBD" in str(a.get(k, "TBD"))]
    if missing: ...; return 1
```
A `check_graduation.py` sibling would assert `write_image_sha256 == readback_sha256` for the graduated
cell (or the failing 0-bits differential for a deferral).

---

## Shared Patterns

### Honest "not measured" discipline (never fabricate)
**Source:** `EVIDENCE.json:35-36` (Phase-97 dmm_pin1_v / dmm_pin31_v).
**Apply to:** any tooling-blocked reading (held-rail DMM at pin 1). Record `"not measured — <reason> ..."`
with the debug-doc reference; lean on the `vpp` ADC monitor + code-decode. Pitfall 5 / Anti-Patterns.

### Bench-discipline row fields
**Source:** `EVIDENCE.json:39-45` (`controller`, `port`, `r1_readback`, `r2_readback`, `fw_commit`,
`jp4_position`).
**Apply to:** every Phase-99 EVIDENCE cell. Verify `controller:` identity per port (ACM numbers shuffle),
live R1/R2 readback, record shield-rev + firmware submodule commit (`35706c2`, NOT the version string).

### D-04 no-copy SHA guard (SHAs live in evidence, not the ledger)
**Source:** `check_ledger.py:59-60, 129-137`.
**Apply to:** all `PROTOCOL-LEDGER.{json,md}` edits — reference artifacts by path + join key; put raw
64-hex SHAs only in `EVIDENCE.json` / `SHA256SUMS.txt`.

### `.json` ↔ `.md` lockstep
**Source:** both PROTOCOL-LEDGER pairs and both EVIDENCE pairs carry the same rows.
**Apply to:** every ledger/evidence edit — update both files together; run `check_ledger.py` after.

### SAFE-01 invariant (never `--force`; `-b` skips only blank-check)
**Source:** `EVIDENCE.json:48` anomalies note (`flags=0x08 SkipBlankCheck only, no FLAG_FORCE — SAFE-01
intact`); 99-RESEARCH.md §Pattern 1 note.
**Apply to:** the bench write invocation — `write -b` (chip is NOT-BLANK), NO `--skip-erase` (no erase
path on a UV EPROM), NO `--force`. The over-voltage guard keys on `FLAG_FORCE`, not
`FLAG_SKIP_BLANK_CHECK`, so SAFE-01 holds.

---

## No Analog Found

None. Every code/data deliverable has an exact in-repo analog (usually in the same file). The only
"no-analog" items are the irreducibly-physical operator bench steps listed under
**File Classification → No code analog**, which are hardware acts, not files.

## Metadata

**Analog search scope:** `.planning/v1.16/ledger/` (tools + fixtures + PROTOCOL-LEDGER pair + bench/
SHA256SUMS convention), `.planning/v1.18/bench/` (Phase-97 gates + EVIDENCE pair).
**Files scanned:** check_ledger.py, test_check_ledger.py, PROTOCOL-LEDGER.{json,md},
fixtures/{ledger_valid,evidence_min,matrix_min}.json, EVIDENCE.json, check_{signature,pre01,diff07,verdict}.py,
W27C512-fix/SHA256SUMS.txt.
**Pattern extraction date:** 2026-07-01
