# SAFE-02: Host CI Gate Sign-Off — Python 3.11

**Date:** 2026-06-27
**Phase:** 94 Plan 04
**Requirement:** SAFE-02 — host CI green on real py3.11 (not devcontainer py3.12); constants parity green

---

## Python 3.11 Interpreter

| Item | Value |
|------|-------|
| **Source** | `uv python install 3.11` → cpython-3.11.15-linux-x86_64-gnu |
| **Binary** | `/home/vscode/.local/share/uv/python/cpython-3.11-linux-x86_64-gnu/bin/python3.11` |
| **venv** | `/tmp/py311-firestarter/` (clean venv, `pip install -e '.[test]'`) |
| **Version string** | `Python 3.11.15` |
| **Devcontainer default** | Python 3.12.13 (NOT used for SAFE-02) |

> The devcontainer default Python 3.12 was intentionally not used for SAFE-02 validation.
> A genuinely separate cpython-3.11.15 interpreter was obtained via `uv python install 3.11`.

---

## Tool Versions (py3.11 venv)

| Tool | Version |
|------|---------|
| ruff | 0.15.20 |
| mypy | 2.1.0 |
| pytest | 9.1.1 |
| pytest-cov | 7.1.0 |

---

## CI Steps (from ci.yml)

### Step 1: Catalog validity check
**Command:** `python3.11 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check`
**Result:** PASS
**Output:** `OK: catalog valid (66 messages, version 1).`

### Step 2: Codegen drift gate (messages.py)
**Command:**
```
python3.11 tools/catalog/codegen.py \
  --catalog tools/catalog/messages.toml \
  --target firestarter/messages.py \
  --language python
git diff --exit-code firestarter/messages.py
```
**Result:** PASS
**Output:** `OK: wrote firestarter/messages.py (python, 66 messages).` — `git diff` exit code 0 (no drift).

### Step 3a: Vector catalog validity check
**Command:** `python3.11 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check`
**Result:** PASS
**Output:** `OK: catalog valid (12 vectors, version 1).`

### Step 3b: Codegen drift gate (frame_vectors.py)
**Command:**
```
python3.11 tools/catalog/codegen_vectors.py \
  --catalog tools/catalog/frame-vectors.toml \
  --target firestarter/frame_vectors.py \
  --language python-vectors
git diff --exit-code firestarter/frame_vectors.py
```
**Result:** PASS
**Output:** `OK: wrote firestarter/frame_vectors.py (python-vectors, 12 vectors).` — `git diff` exit code 0 (no drift).

### Step 4: Install package + test deps
**Command:** `pip install -e .[test]` (in py3.11 venv)
**Result:** PASS
**Output:** All packages installed successfully including firestarter-3.0.0b10.

### Step 5: ruff lint
**Command:** `ruff check firestarter/ tests/`
**Result:** PASS
**Output:** `All checks passed!`

### Step 6: ruff format check
**Command:** `ruff format --check firestarter/ tests/`
**Result:** PASS
**Output:** `77 files already formatted`

### Step 7: mypy type check (watermark gate)
**Command:** `python3.11 tools/check_mypy_watermark.py`
**Result:** PASS
**Output:** `mypy errors: 35 (watermark: 35)` — `OK: error count at watermark.`

### Step 8: pytest with coverage (includes diff_db + check_dispatch gates)
**Command:** `pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70`
**Result:** PASS
**Output:**
```
703 passed in 32.96s
Total coverage: 78.35% (Required: 70%)
```

**Sub-gates within pytest:**
- `test_diff_db_gate.py` — 4 tests PASS (PGSZ-01 intended-additions gate)
- `test_check_dispatch_invariants.py` — 12 tests PASS (dispatch invariants gate)

### Step 9: Smoke test (firestarter --help)
**Command:** `firestarter --help`
**Result:** PASS
**Output:** Click-rendered help text shown; entry point resolves without error.

---

## Summary: All 9 CI Steps

| # | Step | Result |
|---|------|--------|
| 1 | Catalog validity check | PASS |
| 2 | Codegen drift gate (messages.py) | PASS |
| 3a | Vector catalog validity check | PASS |
| 3b | Codegen drift gate (frame_vectors.py) | PASS |
| 4 | Install package + test deps | PASS |
| 5 | ruff lint | PASS |
| 6 | ruff format check | PASS |
| 7 | mypy watermark gate | PASS |
| 8 | pytest + coverage (70% floor) | PASS — 703 tests, 78.35% |
| 9 | Smoke test (firestarter --help) | PASS |

**Verdict: ALL 9 CI STEPS GREEN on Python 3.11.15**

---

## py3.11-Specific Traps — Explicitly Verified

### Trap 1: f-string backslashes inside expression braces
**Risk:** f-string with backslash inside `{}` expression is a `SyntaxError` on py3.11 but allowed on py3.12.
**Check:** `python3.11 -c "import ast, pathlib; [ast.parse(f.read_text()) for f in pathlib.Path('firestarter').rglob('*.py')]"`
**Result:** All files parse OK on Python 3.11.15 — no SyntaxErrors.
**Observed pattern:** backslashes in firestarter source files (`\n`) appear only in f-string string portions *outside* `{}` expression braces — these are valid on py3.11.

### Trap 2: Non-ruff-clean codegen
**Risk:** A `messages.py` generated on py3.12 might not be ruff-format-stable on py3.11.
**Check:** Step 2 ran codegen on py3.11 then `git diff --exit-code`. Exit code 0.
**Result:** PASS — codegen output is ruff-clean and format-stable under py3.11.

---

## Constants Parity: constants.py ↔ firestarter.h

**Claim:** No new flag/constant was introduced across Plans 01–03 that would affect parity.

**Verification:**

| Symbol | constants.py value | firestarter.h value | Match |
|--------|-------------------|---------------------|-------|
| FLAG_FORCE | 0x01 | 0x01 | YES |
| FLAG_CAN_ERASE | 0x02 | 0x02 | YES |
| FLAG_SKIP_ERASE | 0x04 | 0x04 | YES |
| FLAG_SKIP_BLANK_CHECK | 0x08 | 0x08 | YES |
| FLAG_VPE_AS_VPP | 0x10 | 0x10 | YES |
| FLAG_OUTPUT_ENABLE | 0x20 | 0x20 | YES |
| FLAG_CHIP_ENABLE | 0x40 | 0x40 | YES |
| FLAG_VERBOSE | 0x80 | 0x80 | YES |

**New field added (Plans 01–03):** `JSON_KEY_PAGE_SIZE = "page-size"` in `constants.py` — this is a **wire string constant** (a JSON key name), NOT a flag/bitmask. It has no counterpart in `firestarter.h` (the firmware uses the corresponding PROGMEM string `key_page_size` in `json_parser.c`, not a `#define` in `firestarter.h`). The flag/CTRL parity test is **unaffected**.

**FIX-01a impact:** Plan 01 changed the *value* emitted for `flags` (removed FLAG_CAN_ERASE=0x02 for algorithm 5), NOT the flag constants themselves. The parity contract (constant definitions match) remains intact.

**Constants parity verdict:** PASS — all 8 flags match; no new flag/CTRL constant introduced.

---

## SAFE-02 Verdict

**SAFE-02: CLOSED / GREEN**

- Real py3.11.15 interpreter used (not devcontainer py3.12)
- All 9 ci.yml steps pass on py3.11
- py3.11-specific traps (f-string backslashes, non-ruff-clean codegen) explicitly verified clean
- Constants parity (FLAG_* values) confirmed identical; no new flag introduced across Phase 94 Plans 01–03
- Codegen drift gate clean: fresh regeneration on py3.11 produces no diff

*Evidence recorded by: Phase 94 Plan 04 executor, 2026-06-27*
