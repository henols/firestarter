# Phase 82: Electrically-Rewritable Silicon Validation - Pattern Map

**Mapped:** 2026-06-24
**Files analyzed:** 3 (1 new script, 2 artifact extensions)
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_app/tools/gen_test_image.py` (new, D-04) | utility/script | file-I/O + transform | `firestarter_app/write_test.sh` (image generation block) | role-match |
| `.planning/v1.15/bench/EVIDENCE.md` (append rows) | evidence artifact | batch | existing Phase 81 EVIDENCE.md (same file) | exact |
| `.planning/v1.15/bench/EVIDENCE.json` (append cells) | evidence artifact | batch | existing Phase 81 EVIDENCE.json (same file) | exact |

> No new CLI handler or eprom_operations code is written in Phase 82. The plan exclusively INVOKES existing tooling (`dev write-cycle`, `dev consistency-check`) — both already exist in `cli_handlers.py` and `eprom_operations.py`. Pattern excerpts for those call sites are provided below as invocation references, not authoring targets.

---

## Pattern Assignments

### `firestarter_app/tools/gen_test_image.py` (new, utility, file-I/O + transform)

**Analog:** `firestarter_app/write_test.sh` (lines 36–68) for the image-generation pattern; use Python's `random.Random(seed)` for determinism (the shell script uses `/dev/urandom` which is non-deterministic — the new tool must be deterministic per D-03).

**Analog image-generation block** (`write_test.sh` lines 36–68):
```bash
# Query size from chip_database.json via jq
MEMORY_SIZE_HEX=$(jq -e --arg target_name "$EPROM_NAME" -r '
  .[] | .[] |
  select(.part_number == $target_name) |
  .electrical.size_bytes
' "$JSON_FILE")

MEM_SIZE=$((MEMORY_SIZE_HEX))

# Produces /dev/urandom-sourced (non-deterministic) full-chip image
dd if=/dev/urandom of="$TEMP_DIR/low_data.bin" bs=1 count=$HALF_SIZE status=none
dd if=/dev/urandom of="$TEMP_DIR/high_data.bin" bs=1 count=$HALF_SIZE status=none
cat "$TEMP_DIR/low_data.bin" "$TEMP_DIR/high_data.bin" > "$TEMP_DIR/full_data.bin"
```

**Deterministic Python equivalent pattern the planner must use** (D-03 — fixed seed for reproducibility):
```python
import random
import sys
from pathlib import Path

def generate_image(size_bytes: int, seed: int) -> bytes:
    """Full-size deterministic pseudo-random image.  Fixed seed → reproducible SHA."""
    rng = random.Random(seed)
    return bytes(rng.randint(0, 255) for _ in range(size_bytes))

# Invocation pattern:
# python tools/gen_test_image.py <size_bytes> <seed> <output_path>
# e.g. python tools/gen_test_image.py 65536 1 /tmp/W27C512_img_A.bin
#      python tools/gen_test_image.py 65536 2 /tmp/W27C512_img_B.bin
```

**Storage pattern** (D-04, planner's call — suggested):
```
/tmp/firestarter_bench_p82/<chip>_img_A.bin   (seed=1, size=chip.electrical.size_bytes)
/tmp/firestarter_bench_p82/<chip>_img_B.bin   (seed=2, same size)
```
Rationale: temp storage keeps test artifacts out of the repo; seed+chip name in the filename makes each artifact self-describing for EVIDENCE records.

---

### `.planning/v1.15/bench/EVIDENCE.md` — append Phase 82 write rows

**Analog:** existing Phase 81 EVIDENCE.md (at `/workspaces/.planning/v1.15/bench/EVIDENCE.md`)

**Locked column schema** (extract from EVIDENCE.md header row, line 16):
```
| # | Chip | Family / Algorithm | Board+Shield | Op | Blank-state | Read N | SHA-256 | Verdict | Anomalies |
```

**Phase 82 extension columns** (same EVID extension pattern as Phase 81's `read_count`/`blank_check_result`):
```
| write_image_seed_A | sha256_image_A | write_image_seed_B | sha256_image_B | cr01_risk |
```
- `write_image_seed_A` / `write_image_seed_B` — integer seed used with gen_test_image.py (ensures reproducibility)
- `sha256_image_A` / `sha256_image_B` — SHA-256 of the written image (the oracle value `dev write-cycle` asserts against)
- `cr01_risk` — `"yes (W29C020 — page-size under-sized, defer to Phase 84)"` or `"none"`

**Phase 82 op column values** (distinct from Phase 81 `read+blank_check`):
```
op: "write_A+verify_A"   — first pass (image A)
op: "write_B+verify_B"   — second pass (image B, no explicit erase → auto-erase proof D-05)
```

**Verdict wording pattern** (extend Phase 81 FAIL-vs-ANOMALY semantics, D-08/D-09):
- `PASS` — `dev write-cycle` exits 0, B SHA matches B source, no residual A-bits
- `FAIL (CR-01)` — W29C020 mid-page-poll failure, pre-attributed per D-01/D-02
- `FAIL (genuine)` — N=2 reseat+retry exhausted, non-CR-01 root cause
- `ANOMALY` — flaky result (intermittent SHA mismatch), reseat/retry not deterministic

**Existing Phase 81 row pattern to mirror** (EVIDENCE.md lines 18–28):
```markdown
| 1 | W27C512 | 0x07 (EPROM_STD / EEPROM) | leonardo Rev 2.0 | read+blank_check | n/a — not factory-blank, current contents recorded | 3 | `9376dcd81713…97ad23c8` | **PASS** | VPP-high read refusal (~18.8V) cleared by board reset before this read; negative-control verify exited RC=1 |
```

---

### `.planning/v1.15/bench/EVIDENCE.json` — append Phase 82 cells

**Analog:** existing Phase 81 EVIDENCE.json (at `/workspaces/.planning/v1.15/bench/EVIDENCE.json`)

**Existing JSON cell schema** (EVIDENCE.json lines 23–36, `locked_columns` + `evid_extension_columns`):
```json
{
  "locked_columns": [
    "chip", "family", "board", "shield", "blank_state",
    "op", "sha256", "verdict", "anomalies"
  ],
  "evid_extension_columns": [
    "read_count", "blank_check_result"
  ]
}
```

**Phase 82 new extension columns** to declare under `evid_extension_columns`:
```json
"evid_extension_columns": [
  "read_count", "blank_check_result",
  "write_image_seed_A", "sha256_image_A",
  "write_image_seed_B", "sha256_image_B",
  "cr01_risk"
]
```

**Per-cell shape for a PASS write row** (mirroring existing cell at EVIDENCE.json lines 24–36):
```json
{
  "chip": "W27C512",
  "family": "0x07 (EPROM_STD / EEPROM)",
  "board": "leonardo",
  "shield": "Rev 2.0",
  "blank_state": "non-blank (Phase 81 SHA: 9376dcd8…)",
  "op": "write_A+verify_A → write_B+verify_B (A→B auto-erase proof)",
  "sha256": "<SHA of final B read-back>",
  "verdict": "PASS",
  "anomalies": "none",
  "write_image_seed_A": 1,
  "sha256_image_A": "<sha256 of gen_test_image output seed=1 size=65536>",
  "write_image_seed_B": 2,
  "sha256_image_B": "<sha256 of gen_test_image output seed=2 size=65536>",
  "cr01_risk": "none"
}
```

**W29C020 pre-attributed FAIL cell shape** (D-01/D-02):
```json
{
  "chip": "W29C020",
  "family": "0x05 (FLASH_AMD_STD / Flash/EEPROM)",
  "op": "write_A+verify_A",
  "verdict": "FAIL (CR-01)",
  "anomalies": "Mid-page-poll write failure expected: flash4_page_size(262144) → 128B (guessed), real datasheet page = 256B. Pre-attributed per D-01; RCA/fix deferred to Phase 84 FIX-01. See flash4-page-size-datasheet-sourced-cr01.md.",
  "cr01_risk": "yes (W29C020 — flash4_page_size heuristic under-sizes page for 256KB, defer to Phase 84)"
}
```

---

## Shared Patterns (Invocation References)

These are EXISTING commands the planner invokes — not files to author.

### `dev write-cycle` — primary A→B driver

**Source:** `firestarter_app/firestarter/cli_handlers.py` lines 1139–1189, `eprom_operations.py` lines 766–870

**Handler signature** (cli_handlers.py lines 1163–1189):
```python
@dev.command(name="write-cycle")
@click.argument("eprom", shell_complete=_complete_eprom)
@click.argument("source_image", type=click.Path(exists=True))
@click.option("--runs", type=int, default=5)
@click.option("--output-dir", "output_dir", type=str, default=None)
@click.option("-f", "--force", is_flag=True)
@click.pass_obj
@map_typed_errors
def dev_write_cycle(app, eprom, source_image, runs, output_dir, force):
    eprom_data = resolve_chip(eprom, db=app.db)
    verdict_int = app.eprom_operator.write_cycle_eprom(
        eprom, eprom_data,
        source_image_path=source_image,
        runs=runs, output_dir=output_dir,
        operation_flags=_build_op_flags(force=force),
    )
    sys.exit(verdict_int)   # 0=PASS, 1=mismatch, 2=hw-error
```

**A→B two-image invocation pattern** (D-05 — two separate calls, one per image):
```bash
# Image A: write → read-back N (--runs 1 for the phase 82 protocol)
firestarter dev write-cycle W27C512 /tmp/bench_p82/W27C512_img_A.bin --runs 1
# RC=0 → PASS (image A verified); RC=1 → FAIL (mismatch); RC=2 → hw-error

# Image B: write → read-back (no explicit erase — auto-erase proof)
firestarter dev write-cycle W27C512 /tmp/bench_p82/W27C512_img_B.bin --runs 1
# Clean B SHA → auto-erase fired; residual A bits → B SHA mismatch → RC=1
```

**write_cycle_eprom internals** (eprom_operations.py lines 766–810):
```python
def write_cycle_eprom(self, eprom_name, eprom_data_dict, source_image_path,
                      runs=5, output_dir=None, operation_flags=0) -> int:
    source_sha = hashlib.sha256(Path(source_image_path).read_bytes()).hexdigest()
    for i in range(1, runs + 1):
        if not self.erase_eprom(eprom_name, eprom_data_dict, operation_flags):
            return 2   # hw-error
        if not self.write_eprom(eprom_name, eprom_data_dict, source_image_path, operation_flags):
            return 2   # hw-error
        # read-back + SHA compare → 0 (PASS) or 1 (mismatch)
```

### `dev consistency-check` — N≥3 read oracle (EVID-03)

**Source:** `firestarter_app/firestarter/cli_handlers.py` lines 1049–1136

**Invocation pattern** (Phase 81 established):
```bash
firestarter dev consistency-check W27C512 --runs 3
# 0=all 3 reads byte-identical (PASS), 1=divergence, 2=hw-error
```

### `dev validate-family` — alternative matrix driver (EVID-02)

**Source:** `firestarter_app/firestarter/cli_handlers.py` lines 1419–1457

**Invocation pattern**:
```bash
firestarter dev validate-family flash4 --board leonardo --chip W29C040 \
    --source /tmp/bench_p82/W29C040_img_A.bin
```
Note: `validate-family` uses the per-family representative chip, not per-chip iteration. For the A→B per-chip protocol (D-05), `dev write-cycle` (two calls) is the natural fit.

### Negative control (EVID-03 non-vacuous bar)

**Pattern from Phase 81** (EVIDENCE.md line 11, row 1):
```bash
# After write+verify W27C512 image A:
firestarter verify W27C512 /tmp/bench_p82/W27C512_img_B.bin   # must exit RC=1
```
Wrong-file verify must exit non-zero. Phase 81 fired this on W27C512 Task 1. Re-apply per-session or per-first-chip (either satisfies EVID-03 per D-14).

---

## No Analog Found

None. All artifacts either have direct analogs in the existing Phase 81 EVIDENCE scaffold or in the existing CLI/operations layer.

---

## Metadata

**Analog search scope:** `firestarter_app/firestarter/`, `firestarter_app/tools/`, `.planning/v1.15/bench/`
**Files scanned:** 6 (cli_handlers.py, eprom_operations.py, write_test.sh, firestarter_test.sh, EVIDENCE.md, EVIDENCE.json)
**Pattern extraction date:** 2026-06-24
