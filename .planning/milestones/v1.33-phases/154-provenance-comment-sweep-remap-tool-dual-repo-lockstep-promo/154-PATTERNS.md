# Phase 154: Provenance Comment Sweep + Remap Tool — Pattern Map

**Mapped:** 2026-08-23
**Files analyzed:** 12 created + 6 sweep-target groups modified
**Analogs found:** 10 / 12 created (2 have **no precedent in the repo** — see §No Analog Found)

> The new-file inventory was settled by CONTEXT.md / RESEARCH.md / VALIDATION.md and is
> **not re-derived here**. This document supplies the *excerpts*: what to copy, from where,
> and — for three analogs — what must **not** be copied.

---

## File Classification

### Created

| New file | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `.planning/v1.33/tools/remap_citations.py` | utility/CLI checker | batch transform (read blobs → line map → rewrite) | `.planning/v1.16/ledger/tools/check_ledger.py` | role-match (see caveats) |
| `.planning/v1.33/tools/test_remap_citations.py` | test | file-I/O + subprocess | `.planning/v1.16/ledger/tools/test_check_ledger.py` | exact |
| `.planning/v1.33/tools/build_citation_manifest.py` | utility/generator | batch scan → JSONL emit | `.planning/v1.16/ledger/tools/check_ledger.py` (shape only) | partial — no generator precedent under `.planning/` |
| `.planning/v1.33/tools/fixtures/` | fixtures dir | file-I/O | `.planning/v1.16/ledger/tools/fixtures/` (`ledger_valid.json`, `evidence_min.json`, `matrix_min.json`) | exact |
| `firestarter_app/tests/fixtures/planted_sdp_comment_misanchor.cpp` | fixture (planted violation) | file-I/O | `firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c` | exact |
| `…/planted_sdp_comment_brace.cpp` | fixture | file-I/O | same | exact |
| `…/planted_dispatch_comment_only_hex.cpp` | fixture (fail-**open** control) | file-I/O | same | exact |
| `…/planted_dispatch_missing_hex.cpp` | fixture (RED control) | file-I/O | same | exact |
| 3 new legs in `tests/test_sdp_table_parity.py` | test | request-response (env-seam) | `test_sdp_table_parity.py::test_altered_temp_copy_fails_parity_non_vacuous` + `test_json_key_parity.py` planted legs | exact |
| 2 new legs in `tests/test_dispatch_mirror.py` | test | file-I/O (monkeypatch seam) | `test_json_key_parity.py::test_planted_*` | exact |
| `.planning/v1.33/sweep-citation-manifest.jsonl` | data artifact | batch | **none** | ❌ |
| staleness marker (SWEEP-12) | doc/marker | — | `.planning/notes/*.md` (e.g. `firmware-size-reduction-survey.md`) | partial |

### Modified (sweep targets)

| File | Role | Hits | Treatment |
|---|---|---|---|
| `firestarter/src/proms/eeprom_28c.cpp` | model/driver | 33 | own plan (SWEEP-08); highest reflow risk |
| `firestarter/src/firestarter.cpp` | controller (dispatch) | 8 | sweep **minus** `:182-200` NO-TOUCH |
| `firestarter/src/json_parser.c` | service (parser) | 8 | sweep; `:151` is a step-3 keep |
| `firestarter/include/firestarter.h` | config/header | ~10 | sweep; `CAP-01` at `:53` is D-02-exempt |
| `firestarter_app/firestarter/database.py:580-630` | model | 1 block (~50 lines) | condense, both halves of the reversal survive |
| `firestarter_app/tests/scan_paths.py` | test utility | dense | **keep in full**, reword |

---

## Pattern Assignments — Created Files

### `.planning/v1.33/tools/remap_citations.py`

**Analog:** `.planning/v1.16/ledger/tools/check_ledger.py` (D-09's stated precedent). What makes it
the analog: it is the only committed *milestone-scoped* `.planning/` tool with a sibling pytest and
a `fixtures/` dir, plain-stdlib, no package manifest, and an explicit documented exit-code contract.

**Copy — the exit-code contract docstring shape** (`check_ledger.py:1-17`):

```python
"""
Ledger self-consistency gate for PROTOCOL-LEDGER.json.
...
Exit codes:
  0 — all assertions pass; the ledger is structurally consistent.
  1 — at least one structural violation ... This is the real BLOCK.
  2 — infrastructure error: a required input JSON ... could not be loaded or
      parsed. Distinct from 1 so a CI consumer does not confuse a missing
      input with a real structural BLOCK (WR-04).
"""
```

The **0 / 1 / 2** split is the house convention and the remapper should adopt it verbatim:
`1` = a real violation (oracle mismatch, missing resolved target), `2` = infra (manifest unloadable,
**manifest parsed to 0 records** — SWEEP-11's non-zero-on-empty-input, which maps naturally to `2`).

**Copy — the fail-closed loader** (`check_ledger.py:66-78`):

```python
def _load_db(path, label):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot load {label} {path}: {e}", file=sys.stderr)
        sys.exit(2)
```

**Copy — violation accumulation, bucketed report, single exit** (`check_ledger.py:245-283`):

```python
    ledger01_violations = []
    ...
    all_violations = ledger01_violations + ledger02_violations + ledger03_violations
    if all_violations:
        print("FAIL: ledger self-consistency check found violations:\n")
        ...
        print(f"Total: {len(all_violations)} violation(s). Exit 1 (BLOCK).")
        sys.exit(1)
    print(f"PASS: ... {row_count} rows, {defect_count} open_defects, ...")
    sys.exit(0)
```

Note the PASS line **reports counts**. That is exactly the shape SWEEP-10's "the retarget subset's
count is reported" needs, and it is also the anti-vacuity habit: a PASS that names zero rows is
visibly wrong.

#### ⚠ Do NOT copy from this analog

1. **`_HERE`-derived roots.** `check_ledger.py:27-29` is precisely the pattern D-09 forbids:

```python
_LEDGER_DIR = os.path.join(os.path.dirname(__file__), "..")
_EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".planning", "v1.15", "bench")
_MATRIX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "firestarter_app", "tools")
```

   Four `..` segments hard-coded against the tool's own location. Move the file and it resolves
   somewhere else silently. This is the same class as
   `.planning/phases/137-…/check_permitted_claims.py`, whose own docstring names the trap:
   *"a naive future copy of that pattern into yet another phase directory silently resolves its
   targets somewhere else entirely — scanning nothing and exiting 0"*
   (`reference_check_permitted_claims_here_resolves_wrong_phase_dir`).
   **`remap_citations.py` takes the repo root as a required positional argument.** Assert `_HERE`
   is absent from the module (VALIDATION.md already lists that leg).

2. **`argparse` does not exist in the analog.** `check_ledger.py` has **no CLI at all** — it is
   configured entirely by three `os.environ.get(...)` path constants. Across all of `.planning/`
   only `phases/138-preconditions-baseline/138-pulse-distribution.py` imports `argparse`. So the
   argument-parsing shape must be **introduced**, not copied. Recommended minimum, satisfying D-09
   without inventing ceremony:

```python
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo_root", help="explicit repo root; NEVER derived from __file__")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--apply", action="store_true", help="default is dry-run")
```

   Keep the env-var seam **as well** (it is what makes `test_check_ledger.py`'s subprocess style
   work), but the root must be argv-only.

3. **Env-overridable *defaults* that fall back to a derived path.** `check_ledger.py:31-42` gives
   every input a `_HERE`-derived default. For the remapper, an absent `--manifest` must be an
   error (exit 2), not a default.

4. **The `firestarter` name-collision trap** — `check_ledger.py:29` builds
   `…/"firestarter_app"/"tools"` from `..`-chains. Any path the remapper builds must be checked
   against `firestarter_app/tests/scan_paths.py`'s docstring: **one `..` from `tools/` lands in the
   app's own Python package; two reach the sibling firmware repo.** RESEARCH F5 shows this trap in
   *citation* form too — 99 citations to `firestarter.h` collide with
   `firestarter_app/tests/fixtures/fake_firestarter/include/firestarter.h`. Hence the resolution
   rule's `**/fixtures/**` exclusion.

---

### `.planning/v1.33/tools/test_remap_citations.py`

**Analog:** `.planning/v1.16/ledger/tools/test_check_ledger.py` (276 lines). Exact match: sibling
pytest next to the tool, subprocess-driven, fixtures in `fixtures/`.

**Copy — the enumerated-tests docstring** (`test_check_ledger.py:1-28`): each test numbered with its
expected exit code and the requirement it discharges. Reuse this so SWEEP-11's four legs are legible.

**Copy — the subprocess runner** (`test_check_ledger.py:47-60`):

```python
def _run_checker(ledger_path, evidence_path=None, matrix_path=None):
    """Invoke check_ledger.py with the given file paths via env vars."""
    env = os.environ.copy()
    env["FIRESTARTER_LEDGER_FILE"] = ledger_path
    ...
    result = subprocess.run(
        [sys.executable, _CHECKER],
        env=env,
        capture_output=True,
        text=True,
    )
    return result
```

For the remapper, pass the repo root as **argv** rather than env:
`subprocess.run([sys.executable, _TOOL, str(repo_root), "--manifest", str(m)], ...)`.

**Copy — `_HERE` *is* correct in the test** (`test_check_ledger.py:38-45`) — the ban is on the tool
deriving its scan root, not on a test locating its own sibling fixtures:

```python
_HERE = os.path.dirname(os.path.abspath(__file__))
_CHECKER = os.path.join(_HERE, "check_ledger.py")
_FIXTURES = os.path.join(_HERE, "fixtures")
```

**Copy — the assertion shape that prints the tool's output on failure** (`test_check_ledger.py:88-95`):

```python
    assert result.returncode == 0, (
        f"Expected exit 0 but got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "PASS" in result.stdout
```

**Copy — mutate-a-valid-fixture instead of one fixture per violation**
(`test_check_ledger.py:9-11` docstring + `_write_tmp_ledger` / `_load_valid_ledger`, :63-84). This is
the right pattern for the *manifest* legs. It is **not** right for the idempotency/shrink legs, which
need committed synthetic old/new blob pairs with **two separated deletion blocks** (a one-block
fixture passes against a blind implementation — VALIDATION.md W0 note).

**⚠ Do not copy:** `tempfile.mkstemp` + manual `os.close`/caller-deletes
(`test_check_ledger.py:63-76`). Use pytest's `tmp_path`, which every app-repo analog uses
(`test_sdp_table_parity.py:301`). The analog's own docstring concedes the caller-cleanup burden.

---

### `.planning/v1.33/tools/build_citation_manifest.py`

**Analog:** the same `.planning/v1.16/ledger/tools/` shape (module docstring + exit-code contract +
`main()` + `sys.exit`). It shares path resolution with the remapper — factor the resolution rule
into one module imported by both, so F5's 665 ambiguous citations cannot resolve two different ways.

**No JSONL-writing precedent exists anywhere in the three repos** (verified: `find . -name '*.jsonl'`
returns nothing; no `.py` under `firestarter_app/tools`, `firestarter_app/firestarter`, or
`firestarter/tools` mentions `jsonl`). Every committed data artifact under `.planning/` is `.json`,
`.md`, or `.csv`. So the writer shape is **new**; state the newline/text convention in a header
comment as RESEARCH §R1 requires, since there is no in-repo convention to inherit.

**Reuse from `check_ledger.py:130-137`** the "serialize-then-scan" self-check idiom for the
generator's own validity assertion (row count, no unhandled variant, every range carries both
endpoints).

---

### `.planning/v1.33/tools/fixtures/`

**Analog:** `.planning/v1.16/ledger/tools/fixtures/` — the only fixtures dir that sits **beside a
tool** rather than inside a phase directory. Contents: `ledger_valid.json`, `evidence_min.json`,
`matrix_min.json`. Pattern to copy: **minimal, hand-authored, one canonical valid input plus the
minimum satellites**, named `<thing>_valid` / `<thing>_min`.

Suggested parallel: `citations_chained_old.txt` / `citations_chained_new.txt` (≥2 separated deletion
blocks), `manifest_min.jsonl`, `manifest_empty.jsonl` (the exit-non-zero leg).

Sibling precedents that are *phase*-scoped, not tool-scoped — do not follow these for a
milestone tool: `.planning/phases/{123,130,137,146,149,152}/fixtures/`.

---

### The four planted `.cpp` fixtures under `firestarter_app/tests/fixtures/`

**Analog:** `firestarter_app/tests/fixtures/planted_json_parser_key_string_drift.c` (and its 15
siblings, incl. `planted_cap03_literal_index.cpp`, `planted_log_in_window.cpp`).

**Copy — the fixture header comment, verbatim in structure** (`planted_json_parser_key_string_drift.c:1-22`):

```c
/*
 * DELIBERATELY-VIOLATING fixture for
 * tests/test_json_key_parity.py (Phase 149 Plan 05, PGSZ-03, D-18's
 * cross-repo JSON-key parity gate).
 *
 * This file is a minimal, standalone, never-compiled C snippet. It is not
 * built by platformio.ini and is not referenced from any firmware target or
 * build_src_filter in either repository. It exists ONLY so the paired
 * pytest can point test_json_key_parity.py's module-level
 * FIRMWARE_PARSER_SOURCE path constant at it (via `monkeypatch.setattr` on
 * FIRMWARE_PARSER_SOURCE, never an edit to the real
 * firestarter/src/json_parser.c) and prove the gate actually fails on a
 * real firmware/host wire-key disagreement.
 *
 * It is a faithful copy of firestarter/src/json_parser.c's PROGMEM
 * key-string block and key_parsers[] dispatch table (json_parser.c:62-164),
 * with exactly ONE planted change: ...
 */
```

Four load-bearing properties to reproduce: (a) names the gate and the seam it is injected through;
(b) states it is never compiled and not in any `build_src_filter`; (c) states it is a **faithful
copy** of a named source range; (d) names **exactly one** planted change.

⚠ **Provenance caveat for this phase specifically:** these headers are dense with `Phase 149 Plan
05, PGSZ-03, D-18`. The new fixtures are *test files* under D-04's narrow treatment, and D-03
retains requirement IDs in test files where the ID is the traceability key — so write the new
headers keyed on **`SWEEP-07`**, not on `Phase 154 Plan NN`.

For `planted_dispatch_comment_only_hex.cpp` the header must additionally say it asserts **GREEN**:
it documents a fail-**open** mechanism, so a reader who "fixes" it to expect RED destroys the point.

---

### 3 new legs in `firestarter_app/tests/test_sdp_table_parity.py`

**Analog A — the seam (already exists; RESEARCH §R3's correction to D-06).**
`_sdp_src_path()` + `_env_override`, `test_sdp_table_parity.py:90-113`:

```python
def _sdp_src_path() -> Path:
    override = os.environ.get("FIRESTARTER_SDP_SRC")
    path = Path(override) if override else _EEPROM_28C_CPP
    if not path.is_file():
        raise FileNotFoundError(
            f"FIRESTARTER_SDP_SRC points at a missing/unreadable file: {path}"
        )
    return path


@contextmanager
def _env_override(name: str, value: str):
    """Temporarily set an environment variable, restoring the prior value
    (or absence) on exit -- used to plant/withdraw FIRESTARTER_SDP_SRC
    without leaking state into other tests."""
    old_value = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if old_value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old_value
```

This is fail-closed by construction (`FileNotFoundError` on a bad path, pinned by
`test_missing_override_path_fails_closed`, :349-354). The new legs **reuse it**; do not add a second
seam.

**Analog B — the existing non-vacuity leg**, `test_altered_temp_copy_fails_parity_non_vacuous`
(:301-341). Copy its expect-failure shape, which calls the **same helper the live leg calls**:

```python
    with _env_override("FIRESTARTER_SDP_SRC", str(fixture_path)):
        sdp_pairs = _extract_byte_flip_pairs(
            _sdp_src_path().read_text(encoding="utf-8"), "EEPROM_SDP_DISABLE"
        )
    ...
    try:
        _assert_pairs_equal(sdp_pairs, flash_pairs, _PARITY_CONTEXT)
    except AssertionError:
        pass
    else:
        raise AssertionError(
            "Non-vacuity failure: altering one byte in the temp fixture did "
            "not make the parity assertion fail -- the parser or the "
            "parity gate is vacuous."
        )
```

Prefer `with pytest.raises(AssertionError) as excinfo:` (the `test_json_key_parity.py` form) over
this `try/except/else` — it gives a message to assert a distinguishing phrase against, which the
`try/except` form throws away.

**⚠ Do not copy `@requires_fw` onto the new legs.** The existing non-vacuity leg carries it
(:300) because it reads the real committed `eeprom_28c.cpp`. The new legs read **committed
fixtures**, so per `test_json_key_parity.py:374-379` they must carry **no** `requires_fw` and stay
live in an absent-firmware run:

```python
# Tests -- D-18 planted violations. NO `requires_fw` on either: both read a
# committed fixture under tests/fixtures/, always present regardless of
# whether the sibling firmware checkout exists, so both stay live in an
# absent-firmware run.
```

**⚠ The thing the analog does NOT protect against, and the third leg exists for it.**
`_extract_byte_flip_pairs` (:123-160) is comment-blind twice over — `decl_pattern.search()` takes the
**first** match in the file, then `source_text.index("{", match.end())` and a raw `{`/`}` depth walk:

```python
    decl_pattern = re.compile(rf"\b{re.escape(decl_name)}\s*\[\s*\d*\s*\]\s*=\s*")
    match = decl_pattern.search(source_text)
    ...
    brace_start = source_text.index("{", match.end())
    depth = 0
    i = brace_start
    while i < len(source_text):
        if source_text[i] == "{":
            depth += 1
        elif source_text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
```

Its own docstring claims it is "never a bare file-wide regex, which would false-positive" — that
claim is **false with respect to comments**, and RESEARCH F2 proved it fail-**open** (5 passed with
`0xA0`→`0x10`, SDP lock → chip erase). The third leg must assert the slice is anchored on the real
declaration (or feed comment-stripped text). The stripper to reuse is
`test_cap03_ack_layout_parity.py::_strip_comments`, which is **offset-preserving** (replaces each
stripped span with whitespace of the same shape) — do not write a new one.

---

### 2 new legs in `firestarter_app/tests/test_dispatch_mirror.py`

**Analog:** `test_json_key_parity.py::test_planted_key_string_drift_is_detected` (:416-457) — the
**V12 ceremony**, the house pattern for a planted leg. Copy all five steps:

```python
def test_planted_key_string_drift_is_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _FIXTURE_KEY_STRING_DRIFT.is_file(), (
        f"committed fixture missing: {_FIXTURE_KEY_STRING_DRIFT}"
    )
    # V12 ceremony: capture the REAL firmware source (never the fixture)
    # BEFORE any monkeypatch, so the "after" comparison below proves this
    # plant never touched it.
    real_source = FIRMWARE_PARSER_SOURCE
    before_sha = _git_hash_object(real_source) if FW_REPO_PRESENT else None

    monkeypatch.setattr(
        sys.modules[__name__], "FIRMWARE_PARSER_SOURCE", _FIXTURE_KEY_STRING_DRIFT
    )
    with pytest.raises(AssertionError) as excinfo:
        _check_page_size_key_present_and_dispatched()
    message = str(excinfo.value)
    assert "page_size" in message
    assert JSON_KEY_PAGE_SIZE in message
    # Leg isolation: the OTHER plant's distinguishing phrase must be absent.
    assert "does not appear inside the key_parsers" not in message

    if FW_REPO_PRESENT:
        after_sha = _git_hash_object(real_source)
        assert before_sha == after_sha, (
            "the real firmware parser source's git blob hash changed during "
            "this planted-violation run -- the plant must never touch the "
            "real file."
        )
        assert _git_porcelain(FW_ROOT) == "", (
            "the sibling firmware repo is not clean after this "
            "planted-violation run -- the plant must never write into the "
            "real firmware checkout."
        )
```

Plus the two fail-closed subprocess helpers (`test_json_key_parity.py:382-412`), themselves marked
*"Copied from `tests/test_cap03_ack_layout_parity.py` (not reinvented)"* — copy them a third time
rather than importing across modules, matching house practice:

```python
def _git_hash_object(path: Path) -> str:
    git_bin = shutil.which("git")
    assert git_bin is not None, (
        "`git` binary not found on PATH. This must FAIL the suite, never "
        "be silently skipped."
    )
    result = subprocess.run(
        [git_bin, "-C", str(FW_ROOT), "hash-object", str(path)],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()
```

**The seam in `test_dispatch_mirror.py`** is the module constant `_FW_DISPATCH_TEST`
(:36, `fw_path(...)`), read *inside* the test body at :201 — so
`monkeypatch.setattr(test_dispatch_mirror, "_FW_DISPATCH_TEST", fixture)` works, identically to the
analog. The gate itself is a **superset** membership test (:201-224):

```python
    fw_text = _FW_DISPATCH_TEST.read_text(encoding="utf-8")
    fw_hex_tokens: set[int] = {
        int(tok, 16) for tok in re.findall(r"0x([0-9A-Fa-f]+)", fw_text)
    }
    ...
    missing = real_handler_protocols - fw_hex_tokens
    assert not missing, (
        f"firmware leg test_configure_memory.cpp does not enumerate §0 protocol(s): "
        f"{missing_str}" ...
    )
```

No comment stripping anywhere — hence the fail-open control.

**⚠ Do not copy for the fail-open leg:** the `pytest.raises(AssertionError)` wrapper. The
`planted_dispatch_comment_only_hex.cpp` leg asserts the gate goes **GREEN**, i.e. it calls the same
helper with **no** `raises` and documents in its docstring that the green *is* the finding. Keep step
5 (real-file sha + `_git_porcelain(FW_ROOT) == ""`) on both legs regardless.

**⚠ Note (F7/F8, inherited from the analog):** step 5 requires the firmware working tree to be
**porcelain-clean**. These legs are RED today for exactly that reason, and 9 modules assert
porcelain, not 1. D-12 precondition 1 gates them.

---

## Pattern Assignments — Sweep Targets (before/after under D-01)

### `firestarter/src/proms/eeprom_28c.cpp` (33 hits — own plan, SWEEP-08)

Representative comment, **before** (`:176-220`, excerpted):

```cpp
// The `extern` declaration immediately below is LOAD-BEARING, not
// decorative: in C++ a namespace-scope `const` array has INTERNAL linkage
// unless a prior declaration with external linkage is visible, and Plan
// 119-06's three-way identity/distinctness cross-guard must be able to pin
// this PRODUCTION array directly rather than a transcribed test-local copy
// (same load-bearing shape as EEPROM_SDP_DISABLE's extern above, FIX-05
// precedent).
```

**After** — strip `Plan 119-06`, `FIX-05`, and the parenthetical that only resolves against
`.planning/`; keep the C++ linkage sentence, which is a non-obvious invariant (D-01 step 3):

```cpp
// The `extern` declaration immediately below is LOAD-BEARING, not
// decorative: in C++ a namespace-scope `const` array has INTERNAL linkage
// unless a prior declaration with external linkage is visible, and the
// identity/distinctness cross-guard must be able to pin this PRODUCTION
// array directly rather than a transcribed test-local copy (same shape as
// EEPROM_SDP_DISABLE's extern above).
```

The datasheet citation (`:176-182`) survives **verbatim** — `[CITED: Atmel doc0270 rev
0270L-PEEPR-2/09 section 19 note 2 … Microchip DS20006432B section 6.18 note 2]`. A citation is not
provenance. Note `D-11` appears inside it (`"D-11's standalone lock op (below)"`) — strip the token,
keep the clause as `the standalone lock op (below) issues no data write and no read after it`.

**The `D-09` block (`:192-198`)** is a tombstone-shaped cross-reference to a frozen header and
another phase's framing; under step 2 most of it deletes, but the operative fact — *this table is
deliberately not deduped against `flash_utils.h`* — is the same fact D-10 states, so it collapses
into the D-10 block rather than vanishing.

**⚠ THE hazard, restated concretely.** The `D-10` block (`:199-212`) literally contains:

```cpp
// D-10, and this is a SAFETY property, not a style point: {0x5555,0xAA},
// {0x2AAA,0x55}, {0x5555,0xA0} is byte-identical to FLASH_ENABLE_WRITE (the
```

Three `_PAIR_RE`-shaped literals **and** the array names, sitting *above* the real
`extern const byte_flip_t EEPROM_SDP_ENABLE[3];` at `:220`. They are outside the slice today only
because the anchor is below them. Reflowing this block is the exact operation that can move them in.
Safest concrete form: keep the safety sentence but **de-shape the literals** —
write `AA / 55 / A0 to 0x5555 / 0x2AAA / 0x5555` instead of `{0x5555,0xAA}, …` — so no
`{0x…, 0x…}` pair form survives anywhere in a comment in this file. That removes the collision
rather than relying on ordering.

### `firestarter/src/firestarter.cpp` (8 hits, minus `:182-200`)

**NO-TOUCH — quoted for identification only, must not be edited** (`:189-192`):

```cpp
    // Wire layout, three length-discriminated extensions of one variable
    // blob:
    //   [buffer_size u16 BE][hw_revision u8][ver_len u8][ver bytes][write_budget_s u16 BE]
    //      CAP-01              CAP-02                                CAP-03
```

`test_cap03_ack_layout_parity.py` pins `_WIRE_LAYOUT_COMMENT` verbatim against the **raw,
un-stripped** text. `CAP-0N` is D-02-exempt vocabulary everywhere, not just here.

A representative in-scope hit, **before** (`:79-81`):

```cpp
        // v1.22 Phase 119 (LOCK-03, D-02): is_memory_cmd() replaces the old
```

**After** — strip `v1.22 Phase 119`, `LOCK-03`, `D-02`; keep the sentence describing what
`is_memory_cmd()` does and replaces. Where a hit is `Phase 9: deleted the SERIAL_DEBUG bootstrap
call…` (`:38-39`), that is a **tombstone** describing code that is not there → delete the whole
comment.

### `firestarter/src/json_parser.c` (8 hits)

C-style `/* … */`, so the reflow must preserve the delimiter form. Before (`:52`, `:151`):

```c
/* Phase 44 — host-tunable read-timing knobs (D-04 sweep params) */
...
    /* D-05: page_size resets to 0 exactly like chip_id above. handle is a
```

**After** — `:52` strips to `/* Host-tunable read-timing knobs. */`; `:151` is an explicit
**step-3 keep** (it is the only statement of the reset invariant that prevents the
`phase-44-read-timing-knobs-missing-json-parse-reset` bug class), reworded to stand alone:
`/* page_size resets to 0 exactly like chip_id above. … */`.

### `firestarter/include/firestarter.h`

Mixed `//` and `/* */`. `:53` — `* (Phase 55 / CAP-01). */` — `CAP-01` is **exempt** (D-02); strip
`Phase 55`, keep `CAP-01`. `:94` — `// Phase 151, LOCK-02 (D-01/D-02): 16 is the next unused
integer` → keep `16 is the next unused integer`, which is a live invariant about slot allocation.

### `firestarter_app/firestarter/database.py:580-630`

The highest-value block in the repo (CONTEXT `<specifics>`). **Condense, do not compress.** Both
halves of the reversal must survive; this sentence in particular is the load-bearing one and its
`D-12` token strips while the sentence stays:

```python
        # D-12's *policy* was correct given its premise; only the premise
        # changed. Record this as mechanism-corrected and intent-satisfied,
        # never as failed: the honest resolution was to make the firmware
        # do more, not to make the host claim less.
```

**After** — `# The earlier policy was correct given its premise; only the premise changed. …`.
Everything in the block that is a *hardware-hazard* argument (the algorithm-5 / flash4 12V-on-a-5V-part
paragraph, `:583-592`) is step-3 protected and keeps its full force; the plan-shape and
blast-radius paragraphs (`:625-635`) are the condensable part.

### `firestarter_app/tests/scan_paths.py`

**Keep in full, reword.** It is the only written statement of the `firestarter` name-collision trap,
and this is the sentence the remap tool's path handling must be checked against
(`scan_paths.py:38-45`):

```python
#    7 of the 11 files construct their default path with a SINGLE ".."
#    from `tools/` (`os.path.join(_HERE, "..", "firestarter", ...)`), which
#    resolves into `firestarter_app/firestarter/` -- this project's OWN
#    Python PACKAGE, not the sibling repo. Only a path built with TWO ".."
#    segments from `tools/` reaches the sibling firmware repo.
```

Also keep, reworded, the **"deliberately explicit, never derived"** paragraph (`:22-29`) — it is the
reason D-05 says "use the inventory, do not re-derive it by grep". `D-11`/`A-7`/`BASE-02` strip;
`Phase 123 Plan 08` strips; the two prose figures (8 paths / 11 resolvers) stay because
`assert len(CROSS_REPO_TOOL_RESOLVERS) == 11` pins them.

---

## Shared Patterns

### Fail-closed subprocess resolution
**Source:** `firestarter_app/tests/test_json_key_parity.py:382-412` (itself copied from
`test_cap03_ack_layout_parity.py`)
**Apply to:** every new planted leg, both modules.
`shutil.which("git")` → `assert git_bin is not None, "… must FAIL the suite, never be silently
skipped."` → `subprocess.run(..., check=True)`.

### The V12 planted-leg ceremony (5 steps)
**Source:** `test_json_key_parity.py:416-457`; `test_cap03_ack_layout_parity.py::test_planted_literal_index_is_detected`
**Apply to:** all 5 new test legs.
1. sha the **real** file before any monkeypatch; 2. `monkeypatch.setattr` the module constant;
3. call the **same helper the live leg calls**, never a reimplementation; 4. assert a distinguishing
phrase present **and** the sibling plant's phrase absent (leg isolation); 5. assert the real file's
sha unchanged and `_git_porcelain(FW_ROOT) == ""`.

### Exit-code contract 0 / 1 / 2, documented in the module docstring
**Source:** `.planning/v1.16/ledger/tools/check_ledger.py:1-17`
**Apply to:** `remap_citations.py`, `build_citation_manifest.py`.
`2` is reserved for infra so CI cannot confuse a missing input with a real violation. Empty input set
→ non-zero (SWEEP-11) and `2` is the honest code for it.

### Never-vacuous / count-reporting PASS line
**Source:** `check_ledger.py:276-283`; `test_json_key_parity.py:231 test_scan_targets_are_non_vacuous`;
`.planning/phases/137-…/check_permitted_claims.py`'s `UNARMED:` vs `PASS:` split
**Apply to:** both new tools. A PASS must name the number of rows it examined.

### Offset-preserving comment stripper — reuse, never rewrite
**Source:** `firestarter_app/tests/test_cap03_ack_layout_parity.py::_strip_comments`
(structurally copied from `firestarter/tests/test_ack_layout_source_contract_v143.py`)
**Apply to:** the SWEEP-07 anchoring leg, if the planner adopts RESEARCH §R3's recommendation to
feed `_extract_byte_flip_pairs` stripped text (note: that is a **gate behaviour change**, F6).

### Fail-**open** patterns present in the analogs — flagged, not to be copied
1. `test_sdp_table_parity.py::_extract_byte_flip_pairs` — comment-blind, **proven** to pass under a
   `0xA0`→`0x10` corruption (F2). Its docstring's "never a bare file-wide regex" claim is false
   w.r.t. comments.
2. `test_dispatch_mirror.py::test_dispatch_mirror_firmware_leg_enumerates_all_protocols` — superset
   membership over raw hex tokens; a comment mention satisfies it.
3. `check_ledger.py`'s `_HERE` + 4×`..` path constants — the D-09-forbidden shape.
4. `.planning/phases/137-…/check_permitted_claims.py` — the canonical write-up of the trap; read its
   docstring for the wording, do not copy its `_DEFAULT_TARGETS` construction.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.planning/v1.33/sweep-citation-manifest.jsonl` | data artifact | batch | **No JSONL exists anywhere in the three repos** (`find . -name '*.jsonl'` → empty; no `.py` in either `tools/` tree mentions `jsonl`). Every committed `.planning/` artifact is `.json`/`.md`/`.csv`. The nearest structural precedent is `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` (one JSON doc with a `rows` array) — borrow its per-row field discipline, not its container. The newline/text convention must be stated in a header record because there is nothing to inherit. |
| staleness marker (SWEEP-12) | doc/marker | — | No *marker* precedent — `.planning/notes/*.md` are design notes, and the phase-scoped `check-claims` scripts under phases 130/146/149/152 are gates, not markers. Closest shape: `.planning/notes/firmware-size-reduction-survey.md` (a committed note that another phase consumes). The close-blocking behaviour has no mechanical precedent at all; only the literal-`REMAP-04`-plus-a-swept-path check VALIDATION.md specifies. |

Also worth recording: the **survey-regex re-runner** (VALIDATION.md W0, for SWEEP-03/SWEEP-06 hit
counts) has no named analog either. Nearest is `check_ledger.py`'s
`_RAW_SHA_RE.findall(json.dumps(ledger))` scan-and-count idiom.

---

## Metadata

**Analog search scope:** `.planning/v1.16/ledger/tools/`, `.planning/phases/*/` (fixtures +
check-claims scripts), `firestarter_app/tests/` (+ `fixtures/`), `firestarter/src/`,
`firestarter/include/`, `firestarter_app/firestarter/`
**Analogs read in full or by targeted range:** 8 (`check_ledger.py`, `test_check_ledger.py`,
`check_permitted_claims.py` docstring, `test_json_key_parity.py`, `test_sdp_table_parity.py`,
`test_dispatch_mirror.py`, `planted_json_parser_key_string_drift.c`, `scan_paths.py`)
**Read-only:** no source file modified; no build run.
**Pattern extraction date:** 2026-08-23
