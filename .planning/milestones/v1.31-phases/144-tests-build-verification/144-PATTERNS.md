# Phase 144: Tests & Build Verification - Pattern Map

**Mapped:** 2026-08-13
**Files analyzed:** 15 (4 created, 11 modified — see the collateral block, which RESEARCH.md did not name)
**Analogs found:** 13 / 15 (2 partial — D-07's state machine and D-01's `RUN_TEST` parse have no functional
precedent in either repo; both have full *structural* precedent)

> **Read this first.** This phase writes no product code. Every file it creates is a **gate**, and in this
> repository the expensive part of a gate is never the assertion — it is the self-protection scaffolding
> (env seam, two-half non-vacuity, no-skip self-check, needle hygiene) that stops the gate passing over an
> empty set. Four firmware modules already implement that scaffolding correctly. **Copy their structure
> verbatim and spend the thinking budget on the assertion.**
>
> **Hard invariant, restated (D-04):** no file under `firestarter/src/` may be modified. Two analogs below
> pin `src/` files by blob SHA (`cedc88dc…` / `5dffe841…`, both verified matching `HEAD:` this session). If
> a plan finds itself wanting an `src/` edit, it must **stop and report**, not absorb it. See the Warnings
> section for the two places that temptation arises.

---

## File Classification

### Created (4)

| New file | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter/tests/test_requirement_case_mapping_v131.py` | test (static source-contract gate) | transform (C text → name set → set membership) | `firestarter/tests/test_ack_layout_source_contract_v143.py` | **role-match** (structure exact, extraction target new) |
| `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` | test (static golden-partition gate) | transform + batch (two C headers → 885 tuples → 6 index sets) | `firestarter/tests/test_golden_trace_identity_eprom_v131.py` | **role-match** (parse + message shape exact; the state machine is new) |
| `firestarter_app/tests/test_cap03_ack_layout_parity.py` | test (cross-repo byte-layout parity gate) | transform (firmware C text ↔ host decoder offsets) | `firestarter_app/tests/test_revision_constants_parity.py` | **exact** |
| `firestarter_app/tests/fixtures/planted_cap03_*.cpp` ×2 | fixture (committed planted violation) | file-I/O (read-only input) | `firestarter_app/tests/fixtures/planted_constants_value_drift.h` | **exact** |

### Modified (11)

| Modified file | Role | Data Flow | Closest Analog / precedent | Match Quality |
|---|---|---|---|---|
| `firestarter/test/native/avr/_shared/eprom_v131_expected.h` → `…_prechange.h` | fixture (git plumbing) | file-I/O | none needed — pure `git mv`; the *proof* pattern is `git rev-parse HEAD:<path>` | exact (mechanism) |
| `firestarter/test/native/avr/_shared/eprom_v131_expected.h` (fresh capture) | fixture (empirical golden) | batch capture | `dump_v131_merged_ready_to_paste` @ `test_trace_eprom_v131.cpp:351` | **exact** |
| `firestarter/tests/golden/eprom_v131_trace_inventory.json` | config/golden data | file-I/O | `firestarter/tests/golden/protocol_branch_inventory.json` (`meta.recorded_by`) | **exact** |
| `firestarter/scripts/baseline/size_baseline.json` | config/baseline data | file-I/O | its own `meta.supersedes` chain + Plan 124-10 precedent | **exact** |
| `firestarter/scripts/baseline/size_baseline_base01.json` | config/baseline data | file-I/O | same | **exact** |
| `firestarter/scripts/baseline/size_baseline_v131.json` | config/baseline data | file-I/O | its own `native_trace_v131` record (the shape to replicate ×2) | **exact** |
| **`firestarter/tests/fixtures/captured_build_{uno,uno328pb,leonardo}.log`** | fixture (captured measurement) | file-I/O | **Plan 124-10's own re-capture**, documented at `test_check_size_baseline.py:272-279` | **exact** |
| **`firestarter/tests/fixtures/planted_size_baseline_policy_{uno_over_band,leonardo_growth,ram_moved}.log`** | fixture (planted violation) | file-I/O | same (they are derivatives of the captured logs) | **exact** |
| **`firestarter/tests/fixtures/planted_size_baseline_flash_regression.log`** | fixture (planted violation) | file-I/O | same | **exact** |
| **`firestarter/tests/test_check_size_baseline.py`** | test | request-response (subprocess) | itself — two hardcoded figure literals only | **exact** |
| `.planning/phases/144-.../144-TEST-RECORD.md` | doc (phase record) | — | `143-HOST-RECORD.md` §7 | exact |

**The five bolded rows are a collateral cost of D-10 + D-11 that RESEARCH.md does not name.** They are
not optional and not cosmetic: two of them are **planted-violation legs that become UNREACHABLE**. See
`## Collateral: D-10/D-11 break five legs of test_check_size_baseline.py` below — read it before planning
TEST-08.

---

## Pattern Assignments

### 1. `firestarter/tests/test_requirement_case_mapping_v131.py` (test, transform) — D-01

**Analog (wins): `firestarter/tests/test_ack_layout_source_contract_v143.py`**
**Runner-up: `firestarter/tests/test_hv_routing_source_contract_v142.py`**

Both implement the identical seven-part scaffolding. **v143 wins** because it is the smaller of the two
(568 vs 806 lines), it is the most recently authored (Phase 143, so it reflects the current convention
without drift), and its Coverage 8 is the *tightest* statement of the two-half non-vacuity pattern. Use
v142 only as a cross-check that a convention is real rather than local to one module.

**Structural skeleton to copy verbatim** (`test_ack_layout_source_contract_v143.py:133-146`):

```python
import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_DISPATCH_REL = "src/firestarter.cpp"

# Environment seam -- binds at IMPORT time. See the module docstring's
# "Environment seams" section above.
_SCAN_DISPATCH = Path(
    os.environ.get("FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE", str(_REPO_ROOT / _DISPATCH_REL))
)
```

- **Copy structurally:** `_HERE` / `_REPO_ROOT` at module scope (there is **no `conftest.py` anywhere in
  the firmware repo** — verified this session by `find . -name conftest.py`: zero hits; do not add one);
  the `os.environ.get(...)` single-seam expression; the docstring sentence saying it binds at import.
- **Phase-specific:** the seam name and the relative path. Per RESEARCH F-03 the seam should point at the
  **suite root**, not one file: `FIRESTARTER_CASE_MAP_SCAN_ROOT` → `test/native/avr`. Stdlib-only imports
  (`os`, `re`, `pathlib`) — the analog imports nothing else and neither should this.

**Comment-stripping — copy verbatim, it is load-bearing** (`:148-182`, docstring extract at `:148-159`):

```python
def _strip_comments(text):
    """Strip `//` line comments and `/* ... */` block comments, replacing
    each stripped span with whitespace of the SAME SHAPE (a newline stays a
    newline, everything else becomes a single space) so every line number
    in the result matches the original file exactly -- copied verbatim from
    tests/test_write_path_source_contract_v131.py:203-235 via
    tests/test_hv_routing_source_contract_v142.py's own copy, ..."""
```

- **Copy structurally:** the whole function body, and the same-shape-whitespace property (it is what makes
  `_line_of(text, idx)` at `:185-186` report a real file line number in a failure message).
- **Phase-specific:** nothing. The four `RUN_TEST` suites carry no string literals outside comments
  (verified — all 88 sites match `^\s*RUN_TEST\([A-Za-z0-9_]+\)`), so no literal-stripping pass is needed.
- **Why it matters here specifically:** C-05. `test_trace_eprom_v131.cpp:392` holds a sixth `RUN_TEST`
  inside `#ifdef EPROM_V131_TRACE_DUMP` which no env defines. Comment-stripping does **not** remove it.
  The gate must **scope to the three mapped suites** and say so in its docstring (RESEARCH Open Question 3's
  recommendation), or strip preprocessor-guarded regions. State which; do not silently include the trace suite.

**The extraction target** (`test/native/avr/test_eprom_params_v131/test_eprom_params_v131.cpp:207-217`,
representative of all three suites — verified one-per-line, unguarded, unique):

```c
    RUN_TEST(test_0x07_zero_pulse_delay_takes_the_1000us_fallback);
    RUN_TEST(test_0x08_zero_pulse_delay_takes_the_100us_fallback);
    RUN_TEST(test_0x0B_zero_pulse_delay_takes_the_500us_fallback);

    RUN_TEST(test_0x07_nonzero_pulse_delay_is_left_alone);
    RUN_TEST(test_0x08_nonzero_pulse_delay_is_left_alone);
    RUN_TEST(test_0x0B_nonzero_pulse_delay_is_left_alone);

    RUN_TEST(test_each_protocol_resolves_to_its_own_distinct_row);
    RUN_TEST(test_unknown_protocol_returns_null);
    RUN_TEST(test_row_values_match_the_frozen_table);
```

Measured counts re-confirmed this session: `test_loop_eprom_v131` **47**, `test_vpp_eprom_v131` **32**,
`test_eprom_params_v131` **9** = **88**.

**Non-vacuity — the two-half pattern, copy verbatim** (`:477-525`, this is the single most important
excerpt in this document):

```python
def test_scan_targets_are_non_vacuous():
    """Coverage 8 -- structural self-check, two halves.

    Part (a): the DEFAULT scan target is recomputed fresh from _REPO_ROOT
    WITHOUT reading os.environ (the check_permitted_claims.py
    `_HERE`-resolves-to-the-wrong-directory landmine, closed here by
    construction, ...)
    Part (b): the body-extractor, run against whatever `_SCAN_DISPATCH`
    currently resolves to (the SAME seam-aware target every leg above
    scans), must itself yield a non-empty body. ..."""
    default_dispatch = _REPO_ROOT / _DISPATCH_REL
    assert default_dispatch.is_file(), (...)
    assert default_dispatch.stat().st_size > 0, (...)
    assert default_dispatch.resolve().is_relative_to(_REPO_ROOT), (
        f"default {_DISPATCH_REL} scan target {default_dispatch} resolves "
        f"outside _REPO_ROOT ({_REPO_ROOT}) -- a naive future copy of this "
        "module into another directory must fail loudly here, not scan "
        "nothing and exit 0."
    )
    default_stripped = _strip_comments(default_dispatch.read_text())
    assert default_stripped.strip() != "", (...)

    stripped = _strip_comments(_SCAN_DISPATCH.read_text())
    body, _ = _extract_ack_pack_body(stripped)
    assert body.strip() != "", (
        "the extracted init_programmer_framed body (from the CURRENT scan "
        f"target {_SCAN_DISPATCH}) is empty -- a brace-matcher that "
        "silently returns an empty body would make every negative-"
        "assertion leg in this module ... pass VACUOUSLY."
    )
```

- **Copy structurally:** both halves, in one test, with the `is_relative_to(_REPO_ROOT)` leg. Part (a) must
  **never read `os.environ`** — that is what closes the `check_permitted_claims.py`-`_HERE` landmine.
  Part (b) must use the **seam-aware** target — that is the half D-18's "emptied scratch root" plant turns RED.
- **Phase-specific:** part (b)'s "non-empty" becomes a **hardcoded floor**: `>= 88` extracted names, plus
  per-suite floors 47 / 32 / 9, plus a uniqueness assertion (`len(set(names)) == len(names)`). Precedent for
  hardcoded floors: `test_checker_convention.py:132-133` (quoted in full below) and
  `test_golden_trace_identity_eprom_v131.py:198-209`:

```python
def test_inventory_is_non_vacuous():
    inventory = _load_inventory()
    arrays = inventory["arrays"]
    assert len(arrays) >= 3, (
        f"non-vacuous guard: expected >= 3 recorded arrays, got {len(arrays)} "
        "-- an empty or truncated inventory must FAIL, not silently pass."
    )
```

**No-skip self-check + needle hygiene** (`:528-568`):

```python
_NEEDLE_SKIP_CALL = "pytest" + ".skip"
_NEEDLE_SKIPIF_MARKER = "mark" + ".skipif"
_NEEDLE_DEPENDENCY_SKIP_CALL = "importor" + "skip"
...
def test_this_module_cannot_be_silently_skipped():
    own_text = Path(__file__).read_text()
    assert _NEEDLE_SKIP_CALL not in own_text, (...)

def test_own_needles_do_not_appear_verbatim_in_this_module():
    own_text = Path(__file__).read_text()
    for label, needle in _ALL_SELF_CHECK_NEEDLES:
        assert needle not in own_text, (
            f"the concatenation-built needle for {label} appears verbatim "
            "in this module's own source -- rebuild it from at least two "
            "literal pieces so this gate cannot match itself."
        )
```

- **Copy structurally:** both tests and all three concatenated needles.
- **Competing analog:** `test_golden_trace_identity_eprom_v131.py:222-244` uses the *line-prefix* form
  (`stripped.startswith("pytest.skip")`) instead of concatenated needles. **The v143 concatenation form
  wins** for a new module — it is stronger (catches a mid-line occurrence too) and it is what the two most
  recent gates use. Do not mix the two forms in one module.

**Fail-closed `git` resolution — only if the gate touches git.** D-01's gate does not need `git`; if a plan
adds a blob-pin leg it must use `test_golden_trace_identity_eprom_v131.py:91-128` verbatim (quoted under
Shared Patterns), which is also the repo's reference `subprocess.run` list-form-argv implementation.

**What has NO analog:** parsing `RUN_TEST` names. RESEARCH F-03 confirms zero in-repo precedent. That is
fine — the assertion is one regex; everything expensive around it is copied.

**Requirement→case map: where does it live?** Discretionary per CONTEXT.md. Recommend a module-level dict
literal, with the `_EXEMPT_FW_TO_HOST` comment at
`firestarter_app/tests/test_revision_constants_parity.py:172-175` as the wording precedent for *why a
second hand-maintained site is correct here*:

```python
# Frozen four-entry firmware -> host name-PAIR map (never a skip-set).
# Deliberately NOT auto-derived: the whole point of this gate is to catch an
# unreviewed drift rather than mirror it, so adding a fifth exemption must be
# a deliberate edit to this dict literal.
```

The same argument applies verbatim: the `TEST-0N → case names` map must be a deliberate literal, because a
map derived *from* the suites could never detect a rename. Use C-04's corrected TEST-05 list (all **six**
params cases, not "the two fallback cases" — that phantom pair is itself the defect class D-01 exists to catch).

---

### 2. `firestarter/tests/test_trace_segment_exhaustiveness_v131.py` (test, transform+batch) — D-07

**Analog (wins): `firestarter/tests/test_golden_trace_identity_eprom_v131.py`** — same fixture, same repo
directory, same parse family. Take the scaffolding from analog #1 above (seam, two-half non-vacuity,
no-skip, needles) and the **parse + failure-message shape** from here.

**Array parse — copy the *technique*, never the import** (`:131-144`):

```python
_ARRAY_DECL_RE = re.compile(
    r"static const v131_trace_entry_t\s+(\w+)\[\]\s*=\s*\{(.*?)\};",
    re.DOTALL,
)
_ENTRY_RE = re.compile(r"\{[^{}]*\}")

def _parse_arrays(text):
    """Re-derive the ordered (name, entries) pairs from eprom_v131_expected.h's
    raw text, independently of the committed inventory JSON. Strips C-style
    comments first so a commented-out entry -- or a provenance banner's prose
    -- can never inflate a count."""
    arrays = []
    for m in _ARRAY_DECL_RE.finditer(text):
        name = m.group(1)
        body = m.group(2)
        body_nc = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
        body_nc = re.sub(r"//[^\n]*", "", body_nc)
        entries = _ENTRY_RE.findall(body_nc)
        arrays.append((name, len(entries)))
    return arrays
```

- **Copy structurally:** `_ARRAY_DECL_RE` verbatim (it matches both fixtures); the comment-strip-then-match
  order; the independent-re-derivation posture. The module's own docstring at `:57-62` states the rule:
  *"`_parse_arrays()` deliberately duplicates the derivation used to author the JSON, rather than importing
  a shared helper -- the inventory and the file are meant to be compared by two INDEPENDENT readings."*
  **Do not import from that module.** Re-implement.
- **Phase-specific:** the entry regex must *capture fields*, not just count. RESEARCH verified this one
  against all 620 pre-change entries with zero misses:

```python
_ENTRY_FIELDS_RE = re.compile(
    r"\{\s*(\d+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(\d+)UL\s*\}"
)
```

**Entry semantics** (`test/native/avr/_shared/eprom_v131_expected.h:77-91`, read this session):

```c
typedef struct {
    uint8_t  kind;
    uint8_t  pin;
    uint8_t  value;
    uint32_t us;
} v131_trace_entry_t;

#define STROBE_KIND_DATA     1
#define STROBE_KIND_PIN      2
#define TIMING_KIND_DELAY_US 3
#define TIMING_KIND_DELAY_MS 4
```

Pin constants (`include/rurp_shield.h:53-57`): `0x01` LSB · `0x02` MSB · `0x04` `OUTPUT_ENABLE` (**the
program-vs-verify discriminator**) · `0x08` `CONTROL_REGISTER` · `0x20` `CHIP_ENABLE`.

**⚠️ A trap specific to this gate, found while reading the two sources.** The **pre-change** fixture is
richly annotated — `eprom_v131_expected.h:274-284` reads:

```c
static const v131_trace_entry_t EPROM_V131_TRACE_PROTO_07[] = {
    /* one-time VPP-regulator enable (ctrl -> 0x81) + ms=500 */
    {1, 0x00, 0x81, 0UL}, {2, 0x08, 0x01, 0UL}, {3, 0x00, 0x00, 1UL}, {2, 0x08, 0x00, 0UL}, {4, 0x00, 0x00, 500UL},
    /* pass 1: VPE/route assert (ctrl -> 0x85) + ms=10 */
    ...
    /* pass 1: program byte@lsb=0x00 payload=0x3C pulse=100us */
```

Those comments name the segments almost directly — and a segmentation keyed on them would *appear* to work.
But the **new** fixture will not have them. `dump_v131_merged_ready_to_paste`
(`test_trace_eprom_v131.cpp:351-361`) emits **only a positional index comment**:

```c
    printf("##### %s total=%d strobe_overflow=%d timing_overflow=%d\n",
           tag, n, strobe_overflowed(), timing_overflowed());
    for (int i = 0; i < n; i++) {
        ...
        printf("    {%d, 0x%02X, 0x%02X, %luUL}, /* %d */\n",
               e.kind, e.pin, e.value, (unsigned long)e.us, i);
    }
```

**Therefore the segmentation MUST be structural (the F-07 state machine over `kind`/`pin`/`value`/`us`),
and the gate must comment-strip before parsing.** A comment-keyed classifier would pass on the 620
pre-change entries and be unable to classify a single one of the 265 new entries. State this in the
module docstring so a future reader does not "improve" it back.

**Failure-message shape — copy verbatim** (`:177-195`). This is the "name the first divergence, never a
bare 'lists differ'" pattern D-18 requires of the RED transcript:

```python
def test_array_entry_counts_match_the_recorded_inventory():
    ...
    for i in range(n):
        rec_name, rec_entries = recorded[i]
        live_name, live_entries = live[i]
        if rec_name != live_name or rec_entries != live_entries:
            raise AssertionError(
                f"first divergence at index {i} -- "
                f"recorded={{'name': {rec_name!r}, 'entries': {rec_entries}}}, "
                f"live={{'name': {live_name!r}, 'entries': {live_entries}}}"
            )
```

- **Copy structurally:** positional iteration, `first divergence at index {i}`, both sides named in the message.
- **Phase-specific:** D-18's RED evidence requires the message to name **the array, the positional index,
  and the `(kind,pin,value,us)` tuple** of the unattributed entry. Extend the shape; keep the discipline.
- **Assertion form (binding, from D-07 + RESEARCH F-07):** assert **set equality over index ranges**, not a
  count sum — `union(segment_index_sets) == set(range(len(array)))` **and** pairwise-disjoint. A count match
  hides a double-count paired with a drop, which is exactly the second planted violation D-18 specifies.

**What has NO analog:** the six-segment state machine. RESEARCH A2 is honest that it was validated on the
620 pre-change entries only; the 265-entry stream does not exist yet. Treat a segment the machine cannot
classify as **stop-and-report**, not as a taxonomy to widen silently.

**Optional CLI:** if a plan wants a runnable form, add `if __name__ == "__main__":` to the module under
`tests/`. `CHECKER_GLOB` never reaches `tests/`, so this costs nothing (F-08).

---

### 3. `firestarter_app/tests/test_cap03_ack_layout_parity.py` (test, transform) — D-17

**Analog (wins): `firestarter_app/tests/test_revision_constants_parity.py`.** This is the template — same
repo, same cross-repo probe, same "read firmware source text, compare against host constants, prove it
with committed planted fixtures" shape, and its own docstring at `:93-109` already records the honest
skip-gap that D-16 measures.

**Cross-repo plumbing — copy verbatim** (`:128` and `:130-148`):

```python
from tests.fw_presence import fw_path, requires_fw

# Repo presence is now decided ONCE, in `fw_presence.py`, keyed on
# `../firestarter/.git` -- immune to any in-repo firmware rename. `requires_fw`
# is the ONLY skip marker this module uses. ...
# Phase 120 Plan 07: FIRMWARE_HEADER now doubles as a SECOND seam beyond the
# repo-presence gate above -- it is the fixture-injection point the
# planted-violation legs below `monkeypatch.setattr` to point the rebuilt
# gate at a committed fixture under tests/fixtures/ instead of the real,
# untouched firestarter.h. Resolved via `fw_path` so a present-repo-renamed
# header is a named `MissingScanTargetError`, never a silent skip.
FIRMWARE_HEADER = fw_path("include", "firestarter.h")
```

- **Copy structurally:** the `from tests.fw_presence import fw_path, requires_fw` import; **one** module-level
  path constant resolved via `fw_path(...)`; the comment recording that the constant doubles as the
  fixture-injection seam. `fw_presence.py:117-140` (`fw_path`) raises `MissingScanTargetError` naming the
  resolved path when the repo is present but the target is not — that is why a bespoke
  `not path.exists()` proxy is forbidden here (`tools/check_no_exists_proxy.py` lints for the old shape).
- **Phase-specific:** `FIRMWARE_ACK_SOURCE = fw_path("src", "firestarter.cpp")`.
- **Do NOT invent an env seam for this module.** `fw_presence.py:66-76` states the rule and the reason:

```python
# The one seam: only the ROOT path is overridable, never the marker name.
# ...
# The read below is the ONLY environment lookup in this module -- the marker
# name stays hardcoded as `.git` on purpose. Making the marker name
# overridable too would be one more knob that can be set wrong in a real run
```

  `FIRESTARTER_FW_ROOT` already exists and overrides the **root only**. The planted legs reach their
  fixtures by `monkeypatch.setattr` on this module's own path constant (an in-process attribute, which
  *does* work) — **not** by `monkeypatch.setenv`, which cannot reach anything in `fw_presence.py` because
  those names bind at import and `skipif` binds at collection (`fw_presence.py:36-45`).

**The requires_fw / no-requires_fw split — copy the *reasoning* verbatim** (`:713-725`):

```python
# None of the five legs below carry the `requires_fw` skip on the same basis:
# three of them (value-drift / host-missing / fw-missing) read a fixture
# file under tests/fixtures/, which is always present in the repo regardless
# of whether the firmware sub-repo checkout exists ... This partially
# offsets the residual host-only-CI skip gap: a host-only PR still
# exercises the checker's failure modes even though it cannot exercise them
# against the REAL header.
```

- **Copy structurally:** live legs get `@requires_fw`; **fixture-driven planted legs get NO decorator**.
  That is what keeps 6 of 14 legs alive in D-16's absent-path run (RESEARCH F-11 measured
  `6 passed, 8 skipped`) and is a *property to record*, not an oversight.

**Planted-violation legs — copy verbatim** (`:727-748`):

```python
_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_FIXTURE_VALUE_DRIFT = _FIXTURES_DIR / "planted_constants_value_drift.h"

def test_planted_value_drift_is_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    """planted_constants_value_drift.h (CMD_VERIFY = 106, real value 6) must
    trip the two-way CMD_* leg's underlying check -- and ONLY that check,
    proving leg isolation. Calls the SAME `_check_cmd_two_way` helper the
    real leg calls, not a parallel reimplementation."""
    assert _FIXTURE_VALUE_DRIFT.is_file(), (
        f"committed fixture missing: {_FIXTURE_VALUE_DRIFT}"
    )
    monkeypatch.setattr(sys.modules[__name__], "FIRMWARE_HEADER", _FIXTURE_VALUE_DRIFT)
    with pytest.raises(AssertionError) as excinfo:
        _check_cmd_two_way()
    message = str(excinfo.value)
    assert "CMD_VERIFY = 106" in message
    assert "COMMAND_VERIFY = 6" in message
    assert "has no host constant" not in message
```

- **Copy structurally, all five moves:** (a) assert the fixture `is_file()` first — a deleted fixture must
  FAIL, not vacuously pass; (b) `monkeypatch.setattr(sys.modules[__name__], "<PATH_CONST>", fixture)`;
  (c) call the **same helper the live leg calls**, never a parallel reimplementation; (d) assert on the
  message *content*, naming the specific values; (e) assert the **other** legs' phrases are **absent** —
  leg isolation, which is what makes the RED attributable.
- **Phase-specific:** the two plants D-18 specifies — `_ready[13]` literal index, and
  `(uint8_t)(4 + _vlen)` omitting the budget from the emitted length. Assert the message names the literal
  index *and* the computed offset it should have been.

**Fail-closed leg — copy verbatim** (`:342-353` helper + `:855-866` leg):

```python
def test_gate_fails_closed_on_an_unreadable_header_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unreadable/absent header path must be an ERROR, never a silent
    pass -- an empty define set would make every downstream assertion
    vacuously true. ..."""
    missing = tmp_path / "does_not_exist.h"
    monkeypatch.setattr(sys.modules[__name__], "FIRMWARE_HEADER", missing)
    with pytest.raises(AssertionError, match="firmware header not found"):
        _check_cmd_two_way()
```

This is the app-repo equivalent of the firmware gates' two-half non-vacuity. Include it.

**What the gate must assert — both sides, read line by line this session.**

Firmware side, `firestarter/src/firestarter.cpp:189-203` (via `fw_path`, read-only):

| Byte | Statement |
|---|---|
| decl | `uint8_t _ready[4 + 32 + 2];` |
| 0,1 | `_ready[0] = (DATA_BUFFER_SIZE >> 8) & 0xFF` / `_ready[1] = DATA_BUFFER_SIZE & 0xFF` |
| 2 | `_ready[2] = rurp_get_hardware_revision()` / `= 0xFE` (`#ifdef HARDWARE_REVISION` / `#else`) |
| 3 | `_ready[3] = _vlen;` |
| 4… | `memcpy(_ready + 4, _ver, _vlen);` |
| 4+_vlen | `_ready[4 + _vlen] = (_budget >> 8) & 0xFF` ; `_ready[4 + _vlen + 1] = _budget & 0xFF` |
| emit | `LOG_OK_ID_BYTES(MSG_OK_READY, _ready, (uint8_t)(4 + _vlen + 2));` |

Host side, `firestarter_app/firestarter/serial_comm.py:388-441` — `params_bytes = body[1:-1]` strips the id
byte and the CRC, so **`params_bytes[i]` is 1:1 with firmware `_ready[i]`**. The load-bearing lines:

```python
                params_bytes = body[1:-1]  # strip id byte and trailing CRC
                if len(params_bytes) >= 2:
                    value = struct.unpack(">H", params_bytes[:2])[0]
                    if 1 <= value <= 4096:
                        self.firmware_max_chunk = value
                if len(params_bytes) >= 4:
                    self.hw_revision = params_bytes[2]
                    ver_end = 4 + params_bytes[3]
                    if ver_end <= len(params_bytes):
                        self.firmware_identity = params_bytes[4:ver_end].decode(...)
                        if len(params_bytes) >= ver_end + 2:
                            value = struct.unpack(
                                ">H", params_bytes[ver_end : ver_end + 2]
                            )[0]
                            if 1 <= value <= WRITE_BUDGET_MAX_S:
                                self.write_block_budget_s = value
```

The central assertion is `ver_end = 4 + params_bytes[3]` at `:410` and the read at
`params_bytes[ver_end : ver_end + 2]` at `:432` — **computed, never a literal**.

**Firmware-side pattern to mirror for the index-literal rule** — `test_ack_layout_source_contract_v143.py:372-386`
already implements the "no bare index > 3" assertion against the firmware text. Mirror its *shape* on the
host side (no bare integer index > 3 reaching the budget), and its *reason* text. Do **not** copy its regexes
wholesale: they are firmware-side (`_ready[...]`), and D-17's gate must compare the **two sides**, which
neither existing module does.

**Explicit anti-duplication statement the plan must make** (`test_ack_layout_source_contract_v143.py:28-35`):

> "It does NOT perform a live cross-repo comparison against
> firestarter_app/firestarter/serial_comm.py's decoder -- that standing gate is handed to Phase 144 /
> TEST-07 (143-RESEARCH.md Open Question 4)."

and the host-side behavioural pin that already exists — `firestarter_app/tests/test_hw_revision_gate.py:174-188`:

```python
def _cap03_params(
    buffer_size: int, revision: int, identity: str, budget_s: int
) -> bytes:
    """[buffer_size u16 BE][hw_revision u8][ver_len u8][ver bytes][write_budget_s u16 BE].
    ... the closest thing this repo has to a cross-repo wire-layout parity
    assertion; nothing else in either repo compares the two sides (RESEARCH
    Open Question 4 hands the standing gate to Phase 144 / TEST-07).
    """
```

**D-17's contribution is exactly the comparison neither side performs — not a third copy of either.** Say
that in the plan or a reviewer will read it as duplication. (`test_hw_revision_gate.py` measured **27 passed**
on the 3.11 replica this session.)

**Style constraints for the app repo** (`pyproject.toml:110-111`, verified): `target-version = "py39"`,
`line-length = 88`. A new module must be written to those or `ruff format --check` goes RED on arrival.
Unlike the firmware repo, `firestarter_app/tests/conftest.py` **does** exist (344 lines, no autouse
fixtures) — using it is allowed; it offers `build_frame(msg_id, params)` at `:125` if a plan wants a real
frame, though a source/offset comparison should not need one.

**Optional (RESEARCH Open Question 2, recommend yes):** add `src/firestarter.cpp` to
`firestarter_app/tests/scan_paths.py`'s `CROSS_REPO_TEST_PATHS` (`:94-125`), whose entry shape is:

```python
@dataclass(frozen=True)
class ScanPathEntry:
    fw_relative_path: str
    resolved_by: tuple[str, ...]

CROSS_REPO_TEST_PATHS: tuple[ScanPathEntry, ...] = (
    ScanPathEntry(
        "include/firestarter.h",
        ("test_revision_constants_parity.py", "test_check_is_memory_cmd_no_ifdef.py"),
    ),
    ...
)
```

There is **no completeness gate** forcing this (`test_scan_paths_resolve.py:47` — `_FLOOR = 6`, resolve-only),
so it is house convention, not an obligation. If added, the entry must resolve (it does) and `_FLOOR`
must not be lowered.

---

### 4. `firestarter_app/tests/fixtures/planted_cap03_*.cpp` ×2 (fixture, file-I/O) — D-18

**Analog (wins): `firestarter_app/tests/fixtures/planted_constants_value_drift.h`** — same directory, same
never-compiled-C-fixture role, same one-planted-change-only discipline.

**Header comment to copy structurally** (`planted_constants_value_drift.h:1-40`, abridged):

```c
/*
 * DELIBERATELY-VIOLATING fixture for
 * tests/test_revision_constants_parity.py (Phase 120 Plan 07, HOST-03, ...).
 *
 * This file is a minimal, standalone, never-compiled C header. It is not
 * built by platformio.ini and is not referenced from any firmware target or
 * build_src_filter. It exists ONLY so the paired pytest can point
 * test_revision_constants_parity.py's module-level FIRMWARE_HEADER path
 * constant at it (via `monkeypatch.setattr` on FIRMWARE_HEADER, never an
 * edit to the real firestarter.h) ...
 *
 * It is a faithful copy of firestarter/include/firestarter.h's CMD_* region
 * ... with exactly ONE planted change: CMD_VERIFY's value below is 106, not
 * the real firmware's 6. ...
 *
 * This fixture deliberately does NOT trip:
 *   - the host-missing-define leg ...
 * A fixture that failed for two reasons at once could not prove which
 * check fired -- this isolation is the whole point of using three separate
 * fixtures instead of one three-drift fixture.
 *
 * "Fixing" this file (i.e. changing 106 back to 6) would silently hollow
 * HOST-03's value-drift detection leg ... Do NOT "fix" this file.
 */
```

- **Copy structurally, all six elements:** (1) name the consuming test module and the plan; (2) state it is
  never compiled and not in any build filter; (3) name the path constant it is injected through; (4) name
  **exactly one** planted change and quote both the planted and real values; (5) list what it deliberately
  does **not** trip (leg isolation); (6) the "do NOT fix this file" warning with the hollowing consequence.
- **Phase-specific:** two fixtures, one per plant — `planted_cap03_literal_index.cpp` (`_ready[4 + _vlen]`
  → `_ready[13]`) and `planted_cap03_truncated_length.cpp` (`(uint8_t)(4 + _vlen + 2)` →
  `(uint8_t)(4 + _vlen)`). Two files, **not one two-drift file** — element (5) is the reason.
- **Cost note:** these land in the **app** repo, whose `tests/fixtures/` has no floor gate. They do **not**
  touch `firestarter/tests/fixtures/`, so `test_checker_convention.py`'s `FIXTURE_FLOOR = 15` is unaffected.

---

### 5. `firestarter/test/native/avr/_shared/eprom_v131_expected_prechange.h` (fixture, git plumbing) — D-05

**No code analog needed — this is a `git mv`.** The *proof* pattern is one command,
`test_golden_trace_identity_eprom_v131.py:158`:

```python
    observed_sha = _git("rev-parse", f"HEAD:{_FIXTURE_PATH}")
```

Re-verified on disk this session: `git rev-parse HEAD:test/native/avr/_shared/eprom_v131_expected.h` →
`ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`. A git blob SHA is content-only and path-independent, so the
same command against the **new** path must print the same SHA after the move. That single check is the
whole of D-05's proof.

**Verified prerequisites for "included by nothing":** exactly one `#include` of the fixture exists
repo-wide (`test_trace_eprom_v131.cpp:45`), and it must keep pointing at the **old name**, which D-06's new
capture takes. The two other textual references (`_shared/host_stubs_common.inc:162`,
`test_loop_eprom_v131/test_loop_eprom_v131.cpp:70`) are comments and stay factually correct.
`_shared/` is reached only by relative `../_shared/…` includes, so an unincluded header there compiles in no
TU → cannot contribute a warning → the zero-headroom 1166 watermark (D-23) is safe.

---

### 6. `firestarter/test/native/avr/_shared/eprom_v131_expected.h` (fixture, batch capture) — D-06

**Analog (wins): `dump_v131_merged_ready_to_paste` @ `test/native/avr/test_trace_eprom_v131/test_trace_eprom_v131.cpp:351-361`** — the shipped recorder helper. Its own header comment is the pattern statement:

```c
/* TEMPORARY empirical-dump machinery (sdp_expected.h:312-336's / D-01's
 * workflow, mirrored from test_eeprom28c_sdp.cpp's SDP_TRACE_DUMP
 * precedent): prints each merged entry as a ready-to-paste initialiser.
 * `pio test` swallows printf -- this is run by invoking the BUILT BINARY
 * directly (.pio/build/native_trace_v131/firestarter_native), never via
 * `pio test`. Kept behind this #ifdef permanently ... never compiled by
 * default (no env passes -D EPROM_V131_TRACE_DUMP). */
```

- **Copy structurally:** run the helper, paste its output. **Every array in this repo is empirical** — a
  hand-derived array asserts what you believe, not what the code emits.
- **Phase-specific / stop-and-report:** expected banner totals **91 / 115 / 59**. A `0x08` total of **119**
  is positive proof of a stale paste from `141-NEW-TRACE.md` §5. Also expect the dump build's Unity summary
  to read **6 test cases** (vs 5 without the macro — C-05) and `strobe_overflow=0 timing_overflow=0` on all three.
- **Do not touch `src/`** to make the capture happen. The `#ifdef EPROM_V131_TRACE_DUMP` is already in the
  test TU; the macro comes from `PLATFORMIO_BUILD_FLAGS`, and `rm -rf .pio/build/native_trace_v131` first
  makes the run cold and the rebuild question moot.

---

### 7. `firestarter/tests/golden/eprom_v131_trace_inventory.json` (config/golden) — D-08

**Analog (wins): `firestarter/tests/golden/protocol_branch_inventory.json`** — the same repo directory,
the same two-independent-pins shape, and it is the **only** in-tree artifact that documents the
one-commit `recorded_at_head` offset in prose. That documentation is the pattern to copy.

**The one-commit offset, quoted from `protocol_branch_inventory.json:meta.recorded_by`:**

> "…because L-2 requires this golden and the eprom.cpp source change to land in the SAME commit (the
> one-commit property that keeps the D-18 gate RED once, for one reason), recorded_at_head necessarily names
> this commit's PARENT rather than the commit that actually carries this file. Do not read that as a mistake:
> it is the deliberate one-commit offset this plan's own objective documents. […] this file's
> blob_shas['src/proms/eprom.cpp'] is the SHA of the working-tree file as it will read once committed
> (git hash-object src/proms/eprom.cpp, run before staging), and recorded_at_head is this commit's PARENT…"

- **Copy structurally:** predict the new fixture's SHA with `git hash-object <path>` **before staging**; set
  `meta.recorded_at_head` to the commit's **parent**; and write a `recorded_by` sentence saying so
  explicitly, in the same "do not read that as a mistake" register.
- **Copy structurally:** the six-field `meta` block the file already has —
  `source` / `recorded_by` / `requirement` / `blob_sha` / `recorded_at_head` / `why_two_checks` /
  `how_to_update` / `frozen_for` / `measured_entry_counts` / `overflow_observed`, plus the positional
  `arrays: [{name, entries}]` list. All six identity assertions read these; changing the shape breaks them.
- **Phase-specific:** new counts **91 / 115 / 59** (`arrays[].entries`), new `blob_sha`, a new `frozen_for`
  pointing at v1.32 rather than at Phase 144, and per-array `measured_entry_counts` re-derived from the
  capture's banners (strobes / timings / merged).
- **Binding, verbatim from the file's own `meta.how_to_update`:**

> "If this file legitimately changes, re-derive this inventory from the file with an independent parse
> (never hand-edit the numbers) AND state in the commit message which array changed and why -- never edit
> this JSON merely to make a surprise disappear."

- **Sequencing (RESEARCH F-05, the phase's single highest-risk hazard):** D-05 + D-06 + D-08 land in **ONE
  commit**. `test_blob_sha_matches_the_recorded_inventory` reads `HEAD:`, not the worktree, and after a bare
  `git mv` the path is absent so `_git`'s `assert result.returncode == 0` fires — a failure whose message is
  about git's exit code, not about a SHA.
- **Named non-claim to record (D-08):** nothing gate-asserts `eprom_v131_expected_prechange.h`. Its
  preserved `ca3e09f1…` is hand-verifiable via `git rev-parse HEAD:<path>` and cited in the record, but it
  is **not** machine-checked. Record the gap; do not imply otherwise.

---

### 8-10. `firestarter/scripts/baseline/size_baseline{,_base01,_v131}.json` (config/baseline) — D-10, D-11/D-12, D-13

**Analog (wins): the files themselves — their own `meta` blocks are the schema and the instruction set.**
`check_size_baseline.py` is a **read-only consumer this phase does NOT modify** (D-11 keeps the band
literals). Structure verified this session; all three share it:

```
top keys: meta, avr_targets, native_envs, envs_agree, envs_agree_note, warnings
avr_targets.<env>: flash_used, flash_total, flash_free, ram_used, ram_total, ram_free
native_envs.<env>: cases, succeeded, suites, all_passed
warnings.avr.<env>: macro_redefinition, total
warnings.native.<env>: macro_redefinition, total_watermark
warnings.policy: avr_rule "== 0", native_rule "<= total_watermark"
```

**Consumer contracts to honour** (`scripts/check_size_baseline.py`, read this session):

```python
AVR_ENVS = ("uno", "uno328pb", "leonardo")          # :99
NATIVE_ENVS = ("native", "native_nodevtools")       # :100
MERGE05_UNO_CLASS_FLASH_BAND = 64                   # :107  -- DO NOT WIDEN (D-11, D-22)
```

```python
def compare_native(env, parsed, baseline):
    rec = baseline["native_envs"][env]      # bare subscript -- KeyError, not ParseError
```

```python
def compare_avr_policy_merge05(env, parsed, baseline):
    band = 0 if env == "leonardo" else MERGE05_UNO_CLASS_FLASH_BAND
    flash_delta = flash_used - rec["flash_used"]
    if flash_delta > band: ...
    if ram_used != rec["ram_used"]: ...        # equality on ALL THREE, incl. uno328pb
    if flash_total != rec["flash_total"]: ...  # "board or framework moved"
```

- **D-10 (`size_baseline.json` → tip):** rewrite `avr_targets` to **24824 / 24874 / 26906** with RAM
  unmoved and `flash_free` recomputed; **preserve `native_envs` at 141/17** and **preserve the entire
  `warnings` block verbatim** (watermarks 1166 / 138, AVR `== 0`) — D-23 says they are unchanged, and
  `check_build_warnings.py` plus `tests/test_check_build_warnings.py:134` read that same block.
  Add a `meta` note stating every delta and its attributing phase (D-10 requires the *commit message* to;
  the file's own `meta.supersedes` / `deltas_vs_base01` fields are the established place to mirror it).
- **D-11/D-12 (`size_baseline_base01.json` → re-anchor in place):** overwrite `avr_targets` with the same
  three tip figures. Keep `MERGE05_UNO_CLASS_FLASH_BAND` at 64 and `check_size_baseline.py` untouched. No
  in-tree copy of the v1.24 content (D-12) — but do record in `meta` that the v1.24 semantics are **retired**
  and the forward mechanism kept, or a v1.32 reader will mis-read the file's name.
- **D-13 + C-01 (`size_baseline_v131.json`):** measured this session — `native_envs` and `warnings.native`
  each hold `['native', 'native_nodevtools', 'native_pinmap_provisional', 'native_trace_v131']`.
  `native_loop_v131` and `native_params_v131` are **absent from both blocks**. So D-13's task is
  **add two records + update one**, not update three. The shape to replicate is the existing
  `native_trace_v131` pair: `native_envs.native_trace_v131 = {cases: 5, succeeded: 5, suites: 1,
  all_passed: true}` and `warnings.native.native_trace_v131 = {macro_redefinition: 140,
  total_watermark: 140}`. Per RESEARCH Open Question 1: add `native_envs` for both (free from the D-02 run);
  add `warnings.native` **only if** the run is cold, else record the gap — **never write a warm figure into
  a watermark field** (`meta.warm_vs_cold_correction` is the file's own rule; 998 is the warm native figure
  against a 1166 cold watermark).
- **D-22 / C-03, unconditional:** never feed a `*_v131` env name to either checker under **any**
  `--baseline`. Once D-13 lands, `native_loop_v131`/`native_params_v131` become *feedable* against
  `size_baseline_v131.json` — the rule must be restated in the unconditional form or it reads as permission.
- **Never-vacuous guard (F-14):** with no `--avr-log`, no `--native-log` and no `--rebuild`, `main()` prints
  `FAIL: no envs compared` and returns 1. Every invocation must name its inputs.
- **D-14's constrained sentence, verbatim, in the record:** *"MERGE-05 reads green because its anchor moved
  to v1.31, not because growth stayed inside v1.24's band."*

---

## Collateral: D-10/D-11 break five legs of `test_check_size_baseline.py`

**RESEARCH.md does not name this.** I verified it by reading every assertion and every fixture figure on
disk. `firestarter/tests/test_check_size_baseline.py` feeds **committed captured `.log` fixtures carrying
the OLD figures** to the real checker against the **real** baselines. Rewriting the baselines therefore
moves the ground under five of its legs — and two of them are planted-violation legs that go
**unreachable**, which is precisely the trap D-18 and RESEARCH Pitfall 3 exist to prevent.

Fixture figures measured this session:

| Fixture | RAM | Flash |
|---|---|---|
| `captured_build_uno.log` | 1573 | 23954 |
| `captured_build_uno328pb.log` | 1579 | 24004 |
| `captured_build_leonardo.log` | 2014 | 26016 |
| `planted_size_baseline_policy_uno_over_band.log` | 1573 | 23997 (= base01 23932 **+65**) |
| `planted_size_baseline_policy_leonardo_growth.log` | 2014 | 26073 (= base01 26072 **+1**) |
| `planted_size_baseline_policy_ram_moved.log` | **1574** | 23932 |
| `planted_size_baseline_flash_regression.log` | 2014 | 26528 (= default 26016 **+512**) |

| Leg | Line | Breaks on | Why |
|---|---|---|---|
| `test_clean_avr_all_three_envs_pass` | :138-155 | **D-10** | strict identity; 23954 ≠ 24824 → exit 1, asserts exit 0 → **RED ×3** |
| `test_default_mode_is_unchanged_by_the_new_flag` | :360-377 | **D-10** | same three logs, asserts exit 0 → **RED ×3** |
| `test_planted_flash_regression_flips_checker_to_failure` | :187 | **D-10** | `assert "26016" in result.stdout`; message will name baseline=26906 → **RED** (exit code still non-zero) |
| `test_policy_merge05_fires_on_uno_class_over_band` | :297-316 | **D-11** | 23997 − 24824 = **−827** ≤ 64 → exit 0; asserts non-zero **and** `delta=+65` → **RED, plant UNREACHABLE** |
| `test_policy_merge05_fires_on_leonardo_growth` | :319-337 | **D-11** | 26073 − 26906 = **−833** ≤ 0 → exit 0; asserts `delta=+1` → **RED, plant UNREACHABLE** |

**Survives:** `test_policy_merge05_fires_on_ram_move` (:340-357 — fires on RAM 1574 ≠ 1573, independent of
flash); `test_clean_native_both_envs_pass` (:158-171 — 141/17 unchanged);
`test_planted_unparseable_log_exits_exactly_2`; `test_planted_suites_errored_flips_checker_to_failure`;
the two `FIRESTARTER_SIZE_BASELINE` seam-precedence legs (:246-257 and
`test_check_release_assets.py:261-276` — both *derive* a tampered copy from whatever the real baseline
holds); `test_check_build_warnings.py` (reads the `warnings` block only).
**Silently hollowed, not RED:** `test_policy_merge05_permits_the_measured_landing_deltas` (:267-294) — after
the re-anchor it passes on a **−870 shrink**, not on "growth stayed inside the band".

**The pattern to copy — Plan 124-10 already did exactly this.** The precedent is documented verbatim in the
module's own docstring at `:272-279`:

```python
    """Coverage 8 — --policy merge05 PASSES on the ACTUAL post-landing figures, read
    against the frozen BASE-01 record ...

    Before Phase 124 Plan 10, this test synthesized RESEARCH's *predicted* post-landing
    deltas ... onto tmp_path copies of the then-still-pre-landing captured_build_*.log
    fixtures, because the real landing had not happened yet. Plan 124-10 re-captured
    captured_build_{uno,uno328pb,leonardo}.log directly from the real, now-landed tree
    (uno 23954/1573, uno328pb 24004/1579, leonardo 26016/2014) -- so this test now feeds
    those committed fixtures straight to the checker with no synthesis step, and the
    assertion is no longer a *prediction* but a direct measurement of the real MERGE-05
    outcome."""
```

**Recommended discharge (cheapest correct path — 6 fixture rewrites, 2 literal edits, 0 test restructuring):**

1. **Re-capture** `captured_build_{uno,uno328pb,leonardo}.log` from the same cold `pio run` outputs D-02/TEST-08
   produces (24824 / 24874 / 26906, RAM unmoved). Legs 1, 2 and 8 then pass at exact identity / zero delta.
2. **Re-derive** the three policy plants from the **new** anchor, preserving each one's single cause and
   therefore every literal the tests assert: uno `24824 + 65 = 24889` (keeps `delta=+65` / `band of 64`),
   leonardo `26906 + 1 = 26907` (keeps `delta=+1`), ram_moved `flash 24824, RAM 1574` (keeps `ram_used`).
3. **Re-derive** `planted_size_baseline_flash_regression.log` to `26906 + 512 = 27418` and update the two
   figure literals at `:187-188` (`26016` → `26906`, `26528` → `27418`) plus the `+512 B` docstring at
   `:174-178`. (27418 < the 28672 flash_total, so it stays physically plausible.)
4. These are **modifications, never additions** — `test_checker_convention.py`'s `FIXTURE_FLOOR = 15` stays
   satisfied with zero edits to that module (see the floor quote below).
5. Record the D-18 RED/GREEN pair for **each re-derived plant**: a re-derived plant is a *new* plant, and
   "RED proves nothing until the leg has also been seen to pass for the right reason" applies to it.

**If the operator prefers not to touch the fixtures,** the only alternative that keeps the two planted legs
reachable is an in-tree frozen copy of the pre-change base01 figures for those legs to compare against —
which **contradicts D-12**. Flag it; do not absorb it silently. Leaving the five legs RED contradicts D-04's
"green throughout" and D-10's own stated purpose ("a gate that is RED for a known accepted reason can no
longer report an unknown one").

**Baseline number to preserve:** the firmware pytest suite is **292 passed, 0 failed** at the current tip.
Post-change it must still read 292 — not 287.

---

### 11. `.planning/phases/144-tests-build-verification/144-TEST-RECORD.md` (doc) — CONTEXT.md's discretion

**Analog: `.planning/phases/143-host-timeout-progress-pulse-override/143-HOST-RECORD.md`** — §7.1 the cold
flash/RAM table, §7.3 the zero-added-frames non-claim, §7.4 the verbatim `check_size_baseline.py` output,
§15 the findings register, §12 hand-offs.

- **Copy structurally:** verbatim gate transcripts (never paraphrased verdicts); a numbered non-claims
  section; a numbered findings register (`F-144-NN`); a hand-offs section; the per-env case/suite counts
  each labelled with **which env** produced it.
- **Phase-specific mandatory contents:** D-03's non-claim (arithmetic proven, in-loop wiring not, because
  no shipped row sets the factor); D-08's un-gated-prechange-file gap; D-14's re-anchor sentence verbatim;
  D-15's "no CI leg covers the three `*_v131` envs" restated; C-04's phantom-pair observation (CONTEXT.md's
  own prose exhibiting the defect class D-01's gate catches); C-01's policy change (two env records added to
  a file whose predecessor recorded them "in prose only, never in a baseline JSON").
- **Labelling rule (Pitfall 2):** never a bare "79" or "88". 88 is the three-suite mapping denominator;
  79 is `native_loop_v131`'s per-env figure (47 + 32). Never add them.

---

## Shared Patterns

### S1. Fail-closed `git` resolution + list-form-argv subprocess
**Source:** `firestarter/tests/test_golden_trace_identity_eprom_v131.py:91-128`
**Apply to:** every new gate leg that reads git, and every planted leg that asserts the real file is untouched.
This is also the repo's ASVS-V5 reference implementation (`shell=False`, `shutil.which`, never string interpolation).

```python
def _resolve_git():
    """Resolve the `git` binary, fail-closed. ... If `git` (or $GIT) cannot be
    resolved via shutil.which, this raises via a plain assert, which the test
    runner reports as a FAILURE, never a skipped outcome."""
    git_bin = shutil.which(os.environ.get("GIT", "git"))
    assert git_bin is not None, (
        "git not found on PATH (checked $GIT, falling back to 'git'). This "
        "must FAIL the suite, never be silently skipped ..."
    )
    return git_bin


def _git(*args):
    """Run `git <args>` as a real subprocess (list-form argv, invoked
    directly rather than through a shell) against _REPO_ROOT, and assert a
    clean exit. Returns stdout, stripped."""
    git_bin = _resolve_git()
    result = subprocess.run(
        [git_bin, *args],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"git {' '.join(args)} failed (exit {result.returncode}).\n"
        f"stderr:\n{result.stderr}"
    )
    return result.stdout.strip()
```

Host-repo twin (identical discipline, `-C <path>` form):
`firestarter_app/tests/test_py32_flash_map_host.py:214-249` (`_git_hash_object`, `_git_porcelain`).

### S2. "The plant never touched the source of truth" ceremony
**Source:** `firestarter/tests/test_flash_path_record_sync.py:1202-1250`; host twin at
`firestarter_app/tests/test_py32_flash_map_host.py:351-395`.
**Apply to:** every planted-violation leg in this phase (D-18 ×5 plants, plus the 4 re-derived
size-baseline plants).

```python
        real_path = _FW_DOC  # captured BEFORE any monkeypatch
        before_blob = _git_hash_object(real_path)
        real_text = real_path.read_text()

        replacement_target = "24 KiB"
        mutated_text = real_text.replace(replacement_target, "8 KiB", 1)
        assert mutated_text != real_text, (
            "planted mutation did not actually differ from the real text "
            f"-- the replacement target {replacement_target!r} was not "
            "found (the record's wording may have changed)."
        )
        ...
        planted_path = tmp_path / "planted-FLASH-PATH-AND-PCB.md"
        planted_path.write_text(mutated_text)
        monkeypatch.setattr(sys.modules[__name__], "_FW_DOC", planted_path)
        ...
        after_blob = _git_hash_object(real_path)
        assert after_blob == before_blob, (
            "the planted mutation touched the REAL FLASH-PATH-AND-PCB.md "
            "-- it must only ever be written under tmp_path"
        )
        assert _git_porcelain(_FW_REPO_ROOT) == "", (
            "the firmware repo's working tree is no longer clean after "
            "the planted-copy test"
        )
```

Six moves, all mandatory: capture the real path **before** any monkeypatch → hash it → assert the mutation
actually differs (a silently-unmatched `replace()` is a vacuous plant) → write under `tmp_path` (or use a
committed fixture) → assert the blob unchanged after → assert porcelain clean.

### S3. The whole-repo porcelain coupling and its scheduling consequence
**Sources:** `firestarter/tests/test_flash_path_record_sync.py:1247` (`assert _git_porcelain(_FW_REPO_ROOT) == ""`)
and `firestarter_app/tests/test_py32_flash_map_host.py:391` (`assert _git_porcelain(FW_ROOT) == ""`).
**Apply to:** every plan's task ordering.

Neither assertion is scoped to the file under test. So **any** modified or untracked file anywhere in
`firestarter/` turns **both** suites RED — including the **host** suite. Ordering rule: every firmware file
(both new gates, the renamed fixture, the new fixture, the inventory, three baseline JSONs, seven fixture
`.log`s) must be **committed** — not staged — before either repo's suite runs. The two halves are separable
in *content*, serialised in *scheduling*.

Measured this session: `firestarter` is **clean** at phase start ✅. `firestarter_app` has **8 untracked**
(`.coverage`, `.planning/config.json`, `SECURITY.md`, four `datasheets/*.pdf`, `write_test_port.sh`) — these
trip neither assertion (neither asserts the *host* repo's porcelain) but are noise to commit or ignore
before the D-21 measurement, and `.coverage` is rewritten by that run.

### S4. Do not add a `firestarter/scripts/check_*.py` — both floors are at zero headroom
**Source:** `firestarter/tests/test_checker_convention.py:113-133`. Counts re-measured on disk this session:
`ls scripts/check_*.py` → **6**; `ls -d tests/fixtures/planted_*` → **15**. Zero headroom on both.

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
_TESTS_DIR = _HERE
_FIXTURES_DIR = _HERE / "fixtures"

# Non-recursive glob, scoped to firestarter/scripts/ only -- never a
# recursive descent, never firestarter_app/tools/. See module docstring
# "SCOPE" section.
CHECKER_GLOB = "check_*.py"

# Hardcoded floors -- see module docstring for what each counts and why a
# future checker addition must raise these in the same commit.
FLOOR = 6
FIXTURE_FLOOR = 15
```

A new `scripts/check_<X>.py` obliges five coordinated edits **in the same commit** (paired test module,
paired planted fixture, the checker's exact filename inside the test, a `returncode != 0` assertion, and
raising **both** floors) — in a phase whose premise is that it changes no behavior. `CHECKER_GLOB` never
reaches `tests/`, so a pytest module under `firestarter/tests/` triggers none of it. **Both new firmware
gates live in `tests/`** (F-08). Corollary for the collateral block: modifying existing planted fixtures
keeps the count at 15; **adding** one would raise `FIXTURE_FLOOR`'s effective count and is unnecessary.

### S5. The env seam overrides a **path only**, never a marker or a policy literal
**Source:** `firestarter_app/tests/fw_presence.py:66-80`.

```python
# The one seam: only the ROOT path is overridable, never the marker name.
# ... Making the marker name overridable too would be one more knob that can
# be set wrong in a real run ...
FW_ROOT: Path = Path(os.environ.get("FIRESTARTER_FW_ROOT", str(_DEFAULT_FW_ROOT)))
```

**Apply to:** the new firmware seam (`FIRESTARTER_CASE_MAP_SCAN_ROOT` and the D-07 equivalent). Override the
scan path; never the floor literal, never the 88 count, never a segment name. Five existing seams are read
by this phase's targets and **none changes name**: `FIRESTARTER_SIZE_BASELINE`, `FIRESTARTER_FW_ROOT`,
`FIRESTARTER_META_ROOT`, `FIRESTARTER_ACK_SCAN_DISPATCH_SOURCE`, `PLATFORMIO_BUILD_FLAGS`. Each **new** seam
must be documented in its module's docstring — neither repo has a central env-variable inventory, so the
docstring is the only discoverable site.

### S6. Import-time binding ⇒ the planted run is a CHILD PROCESS
**Sources:** `firestarter_app/tests/fw_presence.py:36-45` (the warning) and
`firestarter/tests/test_flash_path_record_sync.py:269-305` (the mechanism, with a recursion guard):

```python
def _run_gate_in_subprocess(env_overrides, node_id=None):
    """... A subprocess is mandatory here because `meta_presence`'s names bind at
    import and `pytest.mark.skipif` binds at collection, so
    `monkeypatch.setenv` has no effect on either.

    Guards against infinite recursion by refusing to run (raising
    `AssertionError`) when the environment variable
    `FIRESTARTER_129_GATE_CHILD` is already set in the CURRENT process ..."""
    assert os.environ.get("FIRESTARTER_129_GATE_CHILD") is None, (...)
    module_path = str(_HERE / "test_flash_path_record_sync.py")
    target = f"{module_path}::{node_id}" if node_id else module_path
    env = dict(os.environ)
    env.update(env_overrides)
    env["FIRESTARTER_129_GATE_CHILD"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "pytest", target, "-q", "-rs"],
        cwd=str(_FW_REPO_ROOT), env=env, capture_output=True, text=True,
    )
```

- **Copy structurally, including the recursion guard** for the two firmware gates' planted runs (which reach
  a scratch scan root via an env seam) and for D-16's absent-path leg.
- **Distinction that matters:** the **firmware** gates' seams are `os.environ` reads → **child process, always**.
  D-17's host gate injects via `monkeypatch.setattr` on a **module attribute** → in-process is correct there.
  Never `monkeypatch.setenv("FIRESTARTER_FW_ROOT", …)` — it has no effect.
- **D-16's absent-path leg must assert the SKIP COUNT, not just exit 0.** `FW_REPO_PRESENT` probes
  `FW_ROOT / ".git"` with `.exists()` (`fw_presence.py:86-88`), so a stray `.git` in the "empty" dir silently
  tests the *present* path. RESEARCH executed both directions this session: present → `14 passed`;
  absent → `6 passed, 8 skipped`, one canonical reason string naming the probed marker.

### S7. Two independent pins per golden
**Source:** `firestarter/tests/golden/protocol_branch_inventory.json:meta.why_two_checks`, and the same field
in `eprom_v131_trace_inventory.json`:

> "A whole-file blob match alone cannot distinguish 'unchanged' from 'an array deleted together with the
> assertions that consumed it' … so the per-array name+entry-count inventory is what makes a deletion visible."

**Apply to:** D-08's rewrite (preserve all six assertions' inputs) and to any new golden this phase authors.
A bare count is the hollow shape this project has had to rebuild before.

---

## No Analog Found

| File / element | Role | Data Flow | Reason |
|---|---|---|---|
| The `RUN_TEST`-name extractor in `test_requirement_case_mapping_v131.py` | test (parse) | transform | **No in-repo precedent parses `RUN_TEST` names.** The four source-contract modules are the *structural* template (seam, two-half non-vacuity, needles, no-skip), not a functional one. Mitigation: the extraction is one regex — `RUN_TEST\(\s*([A-Za-z0-9_]+)\s*\)` — and everything expensive around it is copied. Use RESEARCH F-03's measured tolerance table (no guarded/commented/wrapped/duplicate sites in the three mapped suites; `#ifdef`-guarded site **does** exist in the unmapped trace suite — C-05). |
| The six-segment state machine in `test_trace_segment_exhaustiveness_v131.py` | test (classify) | transform + state machine | Nothing in either repo walks a trace stream with state. Per-entry classification alone is provably insufficient: `pin_CE` (38 entries on `0x07`) spans **both** the pulse and verify-read segments. The discriminator is `OUTPUT_ENABLE` (`pin=0x04`) value — verified exact on `0x07`: 7 program + 12 verify = 19, matching all 19 `pin_OE` entries. Use RESEARCH F-07's segment table as the specification. Validated on the 620 pre-change entries only (A2) — a segment the machine cannot classify on the new 265 is **stop-and-report**. |
| A cross-repo *byte-layout* comparison | test | transform | Neither `test_ack_layout_source_contract_v143.py` (firmware side) nor `test_hw_revision_gate.py` (host side) compares the two. That absence **is** D-17's contribution, and both modules' docstrings hand it to Phase 144 / TEST-07 by name. The *plumbing* is fully analogous (`test_revision_constants_parity.py`); only the two-sided comparison is new. |
| Segmentation keyed on fixture comments | — | — | Deliberately **not** available: the pre-change fixture's descriptive banners do not exist in the new capture (`dump_v131_merged_ready_to_paste` emits `/* %d */` only). Recorded here so nobody re-discovers it as a "simplification". |

---

## Competing analogs — adjudicated

| Choice | Winner | Why |
|---|---|---|
| `test_ack_layout_source_contract_v143.py` vs `test_hv_routing_source_contract_v142.py` for the two firmware gates | **v143** | Smaller (568 vs 806), most recently authored, tightest two-half non-vacuity (its Coverage 8). Use v142's Coverage 14/15 only to confirm a convention is repo-wide rather than local. |
| No-skip self-check: concatenated needles (v143 `:528-568`) vs line-prefix `startswith` (`test_golden_trace_identity_eprom_v131.py:222-244`) | **concatenated needles** | Stronger (catches mid-line occurrences) and it is what the two most recent gates use. Do not mix both forms in one module. |
| D-07's fixture parse: import `_parse_arrays` vs re-implement | **re-implement** | The analog's own docstring (`:57-62`) forbids the import: "the inventory and the file are meant to be compared by two INDEPENDENT readings, not by one parser trusting its own prior output." |
| D-01/D-07 home: `firestarter/tests/` vs `firestarter/scripts/check_*.py` | **`tests/`** | S4 — five coordinated edits plus two zero-headroom floors, for zero benefit (F-08). CONTEXT.md already places D-01 there; the same reasoning settles D-07's "script". |
| D-17 home: `firestarter_app/tests/` vs `firestarter/tests/` | **app repo** | Every existing parity gate lives there, `fw_presence.py` is the sanctioned cross-repo probe, and the host decoder is only reachable from there. The firmware side is already pinned separately. |
| D-17 planted input: committed fixture vs `tmp_path` copy | **committed fixture** | It is what keeps 6 of 14 legs live with **no firmware checkout** (F-11 measured) — a property worth having for a gate whose real scan target lives in the other repo. |
| Size-baseline collateral: re-capture fixtures vs freeze a v1.24 copy vs leave RED | **re-capture** | Plan 124-10's own documented precedent (`test_check_size_baseline.py:272-279`); freezing a copy contradicts D-12; leaving RED contradicts D-04 and D-10's stated purpose. |

---

## Warnings — where an analog would tempt an `src/` edit or a floor change

1. **`test_protocol_branch_inventory.py:495` (`test_params_table_has_no_second_selector`)** pins
   `src/proms/eprom_params.cpp` structurally *and* by blob SHA (`5dffe841…`, verified matching `HEAD:` this
   session), alongside `src/proms/eprom.cpp` (`cedc88dc…`):

   ```python
       assert live["switch_statements"] == 0 == recorded["switch_statements"], (
           f"{_SCAN_PARAMS} contains {live['switch_statements']} switch "
           "statement(s) after comment-stripping -- a switch in the params "
           "table's own translation unit IS the second dispatch selector "
           "TABLE-05 forbids."
       )
       assert live["keys"] == ["0x07", "0x08", "0x0B"] == recorded["keys"], (...)
   ```

   Any params-table substitution seam for a synthetic-row overprogram oracle breaks this **and** the blob
   pin. D-03 reversed precisely to avoid it; D-04 makes it an invariant. **This is deferred work
   (CONTEXT.md `<deferred>`), not a path forward.** A plan that needs it must stop and report.
2. **Do not widen `MERGE05_UNO_CLASS_FLASH_BAND` (64) or `NATIVE_ENVS`** in `check_size_baseline.py`
   (D-11, D-22). The band literals stay; only the file they measure *from* moves. The checker itself is
   **not modified** this phase.
3. **Do not add a seventh PlatformIO native env** (D-04), and **do not add a `conftest.py` to
   `firestarter/`** — verified zero in the repo; it is a recorded house rule restated in at least three
   modules' docstrings.
4. **Do not lower a floor to fix a red gate.** `test_checker_convention.py`'s docstring: *"lowering a floor
   is never the correct response to a red gate."* Same for `test_scan_paths_resolve.py`'s `_FLOOR = 6` and
   any new `>= 88`.
5. **Do not feed a `*_v131` env to either checker** — uncaught `KeyError` → exit **1**, the *regression*
   code, which reads as real damage rather than tool failure (C-03). A `Traceback` in a gate's output is
   never a working gate.
6. **Do not paste `141-NEW-TRACE.md` §5's arrays** — stale at 91/**119**/59; `0x08` is 115.
7. **Do not run either suite with uncommitted firmware files** (S3) — two unrelated RED tests, both
   mis-diagnosable.
8. **Do not measure warm.** `rm -rf .pio/build/<env>` / `pio run -t clean -e <env>`, one uninterrupted
   invocation per env, with a **long explicit timeout** — a default 2-minute Bash timeout truncates the
   toolchain mid-compile and silently contaminates the figure.

---

## Metadata

**Analog search scope:** `/workspaces/firestarter/tests/` (29 modules, 13 748 lines — full inventory listed
and size-ranked), `/workspaces/firestarter/tests/golden/`, `/workspaces/firestarter/tests/fixtures/`,
`/workspaces/firestarter/scripts/`, `/workspaces/firestarter/scripts/baseline/`,
`/workspaces/firestarter/test/native/avr/{_shared,test_loop_eprom_v131,test_vpp_eprom_v131,test_eprom_params_v131,test_trace_eprom_v131}/`,
`/workspaces/firestarter_app/tests/`, `/workspaces/firestarter_app/firestarter/serial_comm.py`,
`/workspaces/firestarter_app/pyproject.toml`.

**Files read in full:** 4 (`test_golden_trace_identity_eprom_v131.py`, `fw_presence.py`,
`test_ack_layout_source_contract_v143.py`, `eprom_v131_trace_inventory.json`).
**Files read by targeted non-overlapping range:** 11.
**Facts re-verified on disk this session (not taken from RESEARCH.md):** the D-05 blob
`ca3e09f164e6e1c541ecb63d15bbebf5bce41d70`; firmware porcelain **clean**; app porcelain **8 untracked**;
`FLOOR = 6` / `FIXTURE_FLOOR = 15` against **6** checkers / **15** planted fixtures; `RUN_TEST` counts
**47 / 32 / 9**; zero `conftest.py` in the firmware repo; the three baselines' env-key sets (**C-01
confirmed**); the seven size-baseline fixture `.log` figures; ruff `py39` / 88.

**Discovered during pattern mapping, absent from RESEARCH.md:** the five `test_check_size_baseline.py`
legs that D-10/D-11 break, two of which become unreachable planted legs; and the fact that the new trace
capture carries positional-index comments only, which forecloses any comment-keyed segmentation for D-07.

**Pattern extraction date:** 2026-08-13
