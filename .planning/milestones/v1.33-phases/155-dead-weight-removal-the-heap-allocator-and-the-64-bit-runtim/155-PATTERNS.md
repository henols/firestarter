# Phase 155: Dead-Weight Removal — the heap allocator and the 64-bit runtime — Pattern Map

**Mapped:** 2026-08-23
**Files analyzed:** 10 (6 modified, 3 created, plus 2 mandatory convention-forced companions discovered here)
**Analogs found:** 9 / 10 (one file has no analog in either repo — see "No Analog Found")
**Repo scope:** every path below is relative to `/workspaces/firestarter` (firmware sub-repo) unless prefixed `.planning/`. Firmware HEAD verified `2ad5b32`, `git status --porcelain` empty.

---

## ⚠ Three corrections to the incoming brief (verified against the tree)

1. **`include/memory_utils.h` is NOT in Phase 155's scope.** `grep -n progress include/memory_utils.h include/firestarter.h` → the only hit in the whole pair is `include/firestarter.h:231: void* progress_data;`. The reference's `memory_utils.h` hunk declares `mem_util_report_voltage`/`mem_util_report_chip_id`, which RESEARCH.md's scope fence assigns to **Phase 156**. Drop it from the file list.
2. **`platformio.ini`'s `build_src_filter` is at lines 205, 294, 332, 370, 412, 468 — not `:227` / `:307`.** RESEARCH.md's citations are already stale against `2ad5b32` (Phase 154 reflowed the file's comments). Six identical occurrences, one per native env. Verified: `grep -n build_src_filter platformio.ini`. Plans must cite the symbol/env, not these line numbers (Phase 159 owns citation repair, and this file will move again in 156–158).
3. **Adding `scripts/check_no_heap_or_64bit_symbols.py` mechanically forces three more edits** via `tests/test_checker_convention.py` — see "Shared Patterns → The checker convention" below. This is the single highest-value finding for the planner: the new gate is not one file, it is four.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/proms/memory.cpp` (`mem_util_blank_check`) | firmware service | event-driven / multi-call state machine | `src/boards/uno_rurp_shield.cpp:36` (`static uint8_t deferred_count`) | weak — data-flow only; **the only mutable file-scope static in all of `src/`** |
| `include/firestarter.h` (drop `progress_data`) | model / shared struct | n/a (struct field removal) | reference hunk `8695ee5..a6b46f8` | exact (1-line delete at `:226`) |
| `src/boards/rurp_common.cpp` (`rurp_read_voltage_mv`) | firmware board-layer utility | transform (pure integer arithmetic) | reference hunk `8695ee5..a6b46f8` | exact, **with 3 defects to not copy** |
| `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` | native test (Unity) | assertion edit | its own siblings at `:1783-1787`, `:1792` | exact (in-file idiom) |
| `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` | native test (Unity) | assertion + 2 comment edits | its own siblings at `:325-332`, `:343-350` | exact (in-file idiom) |
| **NEW** `scripts/check_no_heap_or_64bit_symbols.py` | standalone gate script | file-I/O + subprocess (`avr-nm`) over 3 ELFs | **`scripts/check_release_assets.py`** (per-env artifact presence, build-root seam) + **`scripts/check_erase_no_vpp.py`** (exit taxonomy, fail-closed) | strong composite |
| **NEW** `tests/test_check_no_heap_or_64bit_symbols.py` | pytest (gate's anti-hollow pairing) | subprocess assertion | **`tests/test_check_release_assets.py`** / `tests/test_check_size_baseline.py` | exact |
| **NEW** `tests/fixtures/planted_no_heap_or_64bit_symbols*/` | committed planted-negative fixture | file tree | `tests/fixtures/planted_release_assets_missing_uno328pb/pio_build/…` | exact shape, **but content has no analog** (see below) |
| **NEW** `tests/test_voltage_reformulation_oracle.py` | pytest (numerical oracle + source contract) | transform + source scan | **`tests/test_write_path_source_contract_v131.py`** (source-contract half); **no analog for the numeric half** | partial |
| **NEW** before-figures record, e.g. `.planning/v1.33/155-before-figures.md` | planning record | document | `.planning/v1.33/baseline-pre-sweep.md` | exact |
| **MODIFIED (forced)** `tests/test_checker_convention.py` (`FLOOR` 6→7, `FIXTURE_FLOOR` 15→16) | pytest (meta-gate) | n/a | its own docstring's stated rule | exact |

---

## Pattern Assignments

### `scripts/check_no_heap_or_64bit_symbols.py` (gate script, file-I/O + subprocess)

**Primary analog:** `scripts/check_release_assets.py` — the only existing gate that iterates the three AVR envs' build artifacts, fail-closed on a missing/zero-byte file, with an env seam so a fixture tree can stand in for `.pio/build`.
**Secondary analog:** `scripts/check_erase_no_vpp.py` — the exit-code taxonomy and the "non-vacuity anchor" discipline.

**House convention: manual argv parser, NOT argparse** (`check_release_assets.py:120-150`). Note `check_erase_no_vpp.py` *does* use `argparse`; `check_release_assets.py` explicitly calls the manual parser "house convention, mirrors `check_size_baseline.py`'s `_parse_argv`". Both precedents exist — pick one and say which; the newer/majority idiom is manual.

**Repo-root + env-seam pattern** (`check_release_assets.py:80-101`):
```python
REPO_ROOT = Path(__file__).resolve().parent.parent

FIRESTARTER_SIZE_BASELINE = os.environ.get(
    "FIRESTARTER_SIZE_BASELINE", str(REPO_ROOT / "scripts" / "baseline" / "size_baseline.json")
)
FIRESTARTER_PIO_BUILD_ROOT = os.environ.get(
    "FIRESTARTER_PIO_BUILD_ROOT", str(REPO_ROOT / ".pio" / "build")
)
```
**Copy `FIRESTARTER_PIO_BUILD_ROOT` verbatim — same name, same default.** Its docstring records exactly why it exists (`check_release_assets.py:36-44`): `.gitignore` line 1 is the bare pattern `.pio`, which matches at any depth, so a committed fixture cannot live under a real `.pio/build/...` path. The new gate has the identical problem for ELFs.

**Derive the env list from the baseline, never hardcode three names** (`check_release_assets.py:16-20` + `:170-186`):
```python
avr_targets = baseline.get("avr_targets")
if "avr_targets" not in baseline or not isinstance(avr_targets, dict):
    print(f"FAIL: baseline {baseline_path} has no object-valued 'avr_targets' key")
    return 2

keys = sorted(avr_targets.keys())
if not keys:
    print(
        "FAIL: baseline 'avr_targets' parsed empty -- never-vacuous guard "
        "(a gate that requires nothing must not report success)"
    )
    return 1

failures = []
compared = []
for key in keys:
    expected = build_root / key / f"firestarter_{key}.hex"
    if not expected.exists():
        failures.append(f"{key}: missing {expected}")
        continue
```
For this phase substitute `firestarter_{key}.elf`. **Note:** `check_release_assets.py` does NOT re-anchor or write the baseline — it only reads `avr_targets` keys. That is compatible with LAND-01's "do not re-anchor" constraint.

**Exit taxonomy — copy this three-way split** (`check_erase_no_vpp.py:102-113`, mirrored in `check_release_assets.py:46-57`):
```
0 -- PASS: ... (names the file, the resolved range, the scanned count)
1 -- FAIL: at least one real violation found
2 -- ERROR: fail-closed (missing/unreadable input, unresolvable target,
     or a malformed CLI invocation) -- categorically distinct from 1
```
Map for this gate: **0** = every ELF present and heap/64-bit counts all zero; **1** = a forbidden symbol is present; **2** = an ELF is missing/unreadable, `avr-nm` is absent or exits non-zero, or the `avr_targets` key set is unusable. The paired pytest asserts the **literal 2**, not merely non-zero (`tests/test_check_size_baseline.py:646-658`), so the split must be real.

**Fail-closed message + PASS shape** (`check_release_assets.py:104-116`):
```python
def _print_pass(build_root, compared):
    parts = ", ".join(compared)
    print(f"PASS: {parts} (build_root={build_root})")

def _print_fail(failures):
    print("FAIL:")
    for line in failures:
        print(f"  {line}")
```
The PASS line **must name every env compared** — `test_check_release_assets.py` and `test_check_size_baseline.py` both assert the env name appears in stdout.

**Non-vacuity anchor (from `check_erase_no_vpp.py:60-71`, adapted):** a zero-symbol result on an ELF that isn't the real firmware proves nothing. Anchor on a symbol that **must** be present — e.g. require `mem_util_blank_check` and `rurp_read_voltage_mv` to appear in the `avr-nm` output before a zero count is reported as PASS, exiting **2** if absent. `check_erase_no_vpp.py` does exactly this and its docstring gives the reasoning verbatim ("A checker that can only ever pass proves nothing (v1.12's hollow GATE-03 class)").

**Subprocess convention** — every script in `scripts/` uses list-form `subprocess.run`, never `shell=True` (`check_build_warnings.py:188-197`, `check_landing_range.py:133-139`). For `avr-nm`: resolve the toolchain path explicitly and exit **2** if it is missing. **No existing script in either repo shells out to `avr-nm`, `avr-objdump` or any toolchain binary** (`grep -rn "avr-nm\|toolchain-atmelavr" scripts/ tests/*.py .github/workflows/*.yml` → zero hits). So the *locating of the toolchain* is new capability with no precedent; everything else above is copied.

**No `grep` at all.** RESEARCH.md's shell sketch is illustrative only. Parsing `avr-nm` output in Python with `re` sidesteps the documented fail-open inversion (`grep -c` exits 1 on zero matches). Say so in the docstring — this repo documents rejected mechanisms inline.

---

### `tests/test_check_no_heap_or_64bit_symbols.py` (pytest, subprocess assertion)

**Analog:** `tests/test_check_release_assets.py` + `tests/test_check_size_baseline.py`.

**Path resolution and runner** (`tests/test_check_size_baseline.py:495-520`):
```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_CHECKER = _REPO_ROOT / "scripts" / "check_size_baseline.py"
_FIXTURES = _HERE / "fixtures"

def _run_checker(argv=None, env_overrides=None):
    """Invoke check_size_baseline.py as a real subprocess (list argv, never shell=True)."""
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, str(_CHECKER), *(argv or [])],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
```
There is **no `conftest.py` anywhere** in `firestarter/tests/` and no `pytest.ini`/`pyproject.toml`/`setup.cfg`/`tox.ini` — self-contained module-level path resolution is a recorded house rule (stated in `test_checker_convention.py`'s and `test_config_storage_dualslot.py`'s docstrings).

**Clean-control + planted-negative pair** (`test_check_release_assets.py:88-135`):
```python
_CLEAN_BUILD_ROOT = _FIXTURES / "clean_release_assets_all_three" / "pio_build"
_MISSING_BUILD_ROOT = _FIXTURES / "planted_release_assets_missing_uno328pb" / "pio_build"
...
result = _run_checker(["--build-root", str(_CLEAN_BUILD_ROOT)])
```
and the assertion shape (`test_check_size_baseline.py:634-644`):
```python
assert result.returncode != 0, (
    f"expected non-zero exit on a planted flash regression.\n"
    f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
)
assert "FAIL:" in result.stdout, f"Expected FAIL: in output. Got:\n{result.stdout}"
assert "27630" in result.stdout, f"Expected baseline figure 27630. Got:\n{result.stdout}"
```
i.e. **the failure message must name the offending symbol**, and the test asserts that string — not just the exit code.

**Fixture-tree shape to copy** (`find tests/fixtures/planted_release_assets_missing_uno328pb`):
```
tests/fixtures/planted_release_assets_missing_uno328pb/README.md
tests/fixtures/planted_release_assets_missing_uno328pb/pio_build/uno/firestarter_uno.hex
tests/fixtures/planted_release_assets_missing_uno328pb/pio_build/leonardo/firestarter_leonardo.hex
```
Every planted fixture directory carries a `README.md`. There are two negatives per checker where the exit codes differ (`planted_release_assets_missing_uno328pb` → 1, `..._zero_byte_leonardo` → 1, malformed baseline → 2 via `tmp_path`).

**⚠ Open design point the planner must decide (mechanical, decide-don't-ask):** the planted negative needs an artefact the gate can read. Two options, both consistent with existing precedent:
- (a) **Fixture ELF tree** under `planted_no_heap_or_64bit_symbols*/pio_build/<env>/firestarter_<env>.elf` — matches `planted_release_assets_*` exactly, but commits a binary and still requires a real `avr-nm`.
- (b) **`--nm-output PATH` seam** letting the gate read a committed *captured `avr-nm` text listing* instead of invoking the tool — matches the dominant fixture family in this repo (`captured_build_*.log` / `planted_size_baseline_*.log` are all committed **text** captures of tool output, and `test_check_size_baseline.py`'s docstring states "No `pio` invocation happens anywhere in this module … Paying a cold-toolchain `pio` cost inside pytest would make this suite non-hermetic and slow"). **(b) is the better fit** and keeps the pytest hermetic in CI leg 3, where no AVR toolchain need exist.
Whichever is chosen, VALIDATION.md's separate "reinstate one `malloc` in a throwaway worktree, confirm RED" step is still the end-to-end negative and is *additional* to the committed fixture.

---

### `tests/test_voltage_reformulation_oracle.py` (pytest, transform + source contract)

**Analog for the source-contract half:** `tests/test_write_path_source_contract_v131.py`.

**Module header, seam, and root resolution** (`:142-158`):
```python
import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_EPROM_REL = "src/proms/eprom.cpp"
_MEMORY_REL = "src/proms/memory.cpp"

_SCAN_EPROM = Path(
    os.environ.get("FIRESTARTER_WRITE_PATH_SCAN_SOURCE", str(_REPO_ROOT / _EPROM_REL))
)
_SCAN_MEMORY = _REPO_ROOT / _MEMORY_REL
```
**This answers "how does a pytest here locate firmware source": a module-level `_REPO_ROOT = Path(__file__).resolve().parent.parent` constant plus a relative-path string, optionally overridable by a named env seam that binds at import.** No fixture, no conftest. Use `_RURP_COMMON_REL = "src/boards/rurp_common.cpp"`.

**`_strip_comments` — copy verbatim** (`tests/test_write_path_source_contract_v131.py:223-256`; this is the canonical version RESEARCH.md cites):
```python
def _strip_comments(text):
    """Strip `//` line comments and `/* ... */` block comments, replacing
    each stripped span with whitespace of the SAME SHAPE (a newline stays a
    newline, everything else becomes a single space) so every line number
    in the result matches the original file exactly ..."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            out.append("  ")
            i += 2
            while i < n and not (text[i] == "*" and i + 1 < n and text[i + 1] == "/"):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            if i < n:
                out.append("  ")
                i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _line_of(text, idx):
    return text.count("\n", 0, idx) + 1
```
A second, functionally equivalent implementation lives at `scripts/check_erase_no_vpp.py:161-197` (docstring: "length- and newline-preserving, so offsets never drift"). Prefer the `tests/` copy for a `tests/` module — the repo already duplicates it rather than sharing a helper, so duplicating again is the established idiom.

**One complete example assertion — the positive/anti-vacuity leg** (`:394-425`), which is the shape DEAD-04's source-contract half should take:
```python
def test_the_per_byte_loop_constructs_are_present():
    """Coverage 5 -- the positive counterpart to Coverage 1-4: an emptied
    or gutted eprom.cpp would satisfy every absence leg above vacuously."""
    stripped = _strip_comments(_SCAN_EPROM.read_text())
    for label, rx in (
        ("firestarter_set_data", _FIRESTARTER_SET_DATA_RE),
        ("MSG_ERR_MAX_PULSES", _MSG_ERR_MAX_PULSES_RE),
    ):
        count = len(rx.findall(stripped))
        assert count > 0, (
            f"expected at least one occurrence of {label} in the "
            f"comment-stripped {_EPROM_REL}, found {count} -- the "
            "rewritten per-byte loop must still use this construct.\n"
            f"Got (comment-stripped {_EPROM_REL}):\n{stripped}"
        )
```
Note the convention: **compiled module-level `re` patterns** (`:180-205`), a `(label, rx)` tuple loop, and a failure message that dumps the whole comment-stripped source.

**Two mandatory structural legs to copy verbatim in spirit** (`:641-699`):
```python
def test_scan_targets_are_non_vacuous():
    default_eprom = _REPO_ROOT / _EPROM_REL
    ...
        assert p.is_file(), (
            f"default {label} scan target {p} does not exist on disk -- a "
            "missing scan target must FAIL, never silently pass."
        )
        assert p.stat().st_size > 0, ...
        assert p.resolve().is_relative_to(_REPO_ROOT), ...
        stripped = _strip_comments(p.read_text())
        assert stripped.strip() != "", ...

def test_this_module_cannot_be_silently_skipped():
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
    dependency_skip_call = "importor" + "skip"
    assert skip_call not in own_text, ...
```
The concatenation-built needle trick (`"pytest" + ".skip"`) exists so the gate's own source cannot match its own check — reuse it if the oracle asserts absence of a token it must also mention.

**Also note the `is_relative_to(_REPO_ROOT)` leg's comment:** it names "the `check_permitted_claims.py` `_HERE`-resolves-to-the-wrong-directory landmine, closed here by construction". That is the same landmine the new oracle would hit.

**The numeric half has no analog — see "No Analog Found".**

---

### `src/boards/rurp_common.cpp` (board-layer utility, transform)

**Analog:** the preserved reference hunk. Current shipped code is at `:52-71` (quoted in RESEARCH.md). The reference's replacement, **verbatim from `git diff 8695ee5 a6b46f8 -- src/boards/rurp_common.cpp`**:

```c
    // Vin_mV = (voltage_adc_reading * 1100 * (R1 + R2)) / (bandgap_adc_reading * R2)
    //
    // Evaluated entirely in 32-bit by folding the resistor divider into a
    // single scale factor FIRST, rather than forming a 64-bit numerator:
    //
    //     k   = 1100 * (R1 + R2) / R2
    //     Vin = (adc * k + bandgap/2) / bandgap
    //
    // At the shipped calibration (VALUE_R1 270000, VALUE_R2 44000) k is 7850
    // exactly and this is BIT-IDENTICAL to the uint64 form it replaces --
    // adc=1023, bandgap=225 gives 35691 mV either way. Across a sweep of
    // off-nominal calibrations (R2 39k-47k, bandgap 200-250, full ADC range)
    // the worst deviation is 5 mV, against the +/-5% VPP validation windows
    // (+/-600 mV at 12 V) that consume this value.
    //
    // WHY: the uint64 form made this function the ONLY user-code caller of the
    // entire 64-bit runtime -- __muldi3 (158 B), __udivmod64 (162 B),
    // __lshrdi3 (54 B), __udivdi3_umoddi3, __adddi3, __muldi3_6, __umoddi3,
    // __udivdi3 = 438 B of linked helpers for one 7-line function.
    //
    // Both products are kept inside uint32 by the guards below: 1100*(R1+R2)
    // needs R1+R2 <= 3904515, and adc*k needs k <= 4194303 given adc <= 1023.
    // An implausible calibration returns 0, exactly as r2 == 0 already does.
    //
    // NOT covered by any native test: this TU is outside [env:native]'s
    // src_filter (+<proms/>), so this arithmetic is bench-verified only.
    uint32_t sum = r1 + r2;
    if (sum > 3900000UL) {
        return 0;
    }
    uint32_t k = (1100UL * sum) / r2;
    if (k > 4000000UL) {
        return 0;
    }
    uint32_t bg = (uint32_t)bandgap_adc_reading;
    return (uint16_t)((voltage_adc_reading * k + bg / 2) / bg);
```

**🚩 FOUR defects in this reference hunk. Copy the code, rewrite the comment.**
1. **`"so this arithmetic is bench-verified only"` — FALSE and a DEAD-05 violation.** There is no bench coverage and none will be created (D-02). VALIDATION.md §"Honest Coverage Ceiling" item 5 lists *"bench-verified"* as a **forbidden phrasing**. Replace with the mandated wording: *"proven by a committed host-side numerical oracle over a stated input grid, bound to the shipped C by a source-contract scan; no native and no bench coverage exists."*
2. **`if (k > 4000000UL)` contradicts the comment two lines above it** (`k <= 4194303`) and contradicts REQUIREMENTS DEAD-04. Per RESEARCH.md C-1, `4194303` = `0x3FFFFF` measures **−1366 B** and is 2 B cheaper than `4000000`'s **−1364 B**. Ship `4194303UL`.
3. **`+/-5% ... (+/-600 mV at 12 V)`** — RESEARCH.md's DEAD-04 correction: the high edge is a fixed **+500 mV absolute**, only the low edge is −5 %. Restate asymmetrically.
4. **The 8-symbol / 438 B list is undercounted by 90 B** (C-4: 11 symbols, 528 B). Either state 11/528 or mark 438 B as the named-subset figure.
5. **Also inherited:** the reference's comment ends the file without a trailing newline (`\ No newline at end of file`). Preserve/fix deliberately.

---

### `src/proms/memory.cpp` (service, event-driven multi-call state)

**In-scope reference hunks only** (the `mem_util_report_voltage` / `mem_util_report_chip_id` +46-line block in the same diff is **Phase 156** — do not import it):

```c
/* Saved across the multi-call blank check.
 *
 * This WAS a 4-byte malloc of a one-uint32_t struct. That single allocation
 * pulled the whole avr-libc allocator into the image -- malloc 312 B + free
 * 274 B = 586 B -- and mem_util_blank_check was its ONLY caller. It also
 * dereferenced the result UNCHECKED (`progress_data->address = ...` straight
 * after the malloc), on a part with roughly 470 B of free RAM once `handle`
 * (1115 B) and the jsmn token array (512 B) are accounted for. A file-scope
 * static has the identical lifetime -- one command runs at a time -- with none
 * of that. handle->progress_data is removed with it; nothing else read it. */
static uint32_t blank_check_saved_address;
```
plus, inside `mem_util_blank_check`: delete the `blank_check_progress_data_t* progress_data;` local, the `malloc`, both casts, the `free`, and the `handle->progress_data = NULL;`, replacing the two uses with `blank_check_saved_address`.

**🚩 Defect in this hunk's comment:** *"roughly 470 B of free RAM once `handle` (1115 B) and the jsmn token array (512 B) are accounted for"* is RESEARCH.md **C-3** — it double-counts the 512 B (on `uno`, `handle` is **603 B**, and `603 + 512 = 1115`). Use C-3's corrected sentence, and RESEARCH.md's stronger framing that the 473 B is *shared heap-and-stack* headroom, so the true margin is **less than 473 B**.

**Placement:** the deleted `typedef` sits at `memory.cpp:489-460`, immediately above `#define BLANK_CHECK_CHUNK_SIZE 2048` (`:397`). Put the static where the typedef was.

**Local-idiom analog (weak, and the planner should know it is weak):** `grep -rnE "^static <type> <name>;" src/` finds **exactly one** mutable file-scope static in the whole firmware — `src/boards/uno_rurp_shield.cpp:36`:
```c
#define DEFERRED_LOG_MAX 4
#define DEFERRED_PARAM_MAX 8  // widest narrow frame (U32_U32 / U16x4 / progress) = 8 bytes
static uint8_t deferred_count = 0;
static struct {
    uint8_t id;
    uint8_t len;
    uint8_t params[DEFERRED_PARAM_MAX];
} deferred_log[DEFERRED_LOG_MAX];
```
Idiom extracted: declared immediately below its sizing `#define`s, immediately above the function that owns it, with a long preceding comment giving the *reason* the state is file-scope rather than passed. **There is no reset-on-init discipline to imitate** — `deferred_count` is reset inside the flush path, not at command start. Every other `static` in `src/proms/` is either a `static const … PROGMEM` table or a `static` function. So `blank_check_saved_address` is effectively a **new idiom in `src/proms/`**; the reference's write-before-read-only-in-the-else-branch discipline is the correctness argument and should be stated in the comment.

---

### `include/firestarter.h` (model)

One-line delete at `:226`, inside `firestarter_handle_t`:
```c
    bus_config_t bus_config;
    void* progress_data;          /* <-- delete this line */

    void (*firestarter_operation_init)(struct firestarter_handle*);
```
**Same-commit constraint (RESEARCH.md, measured):** deleting this line without the two test edits produces two hard `error:` lines and both suites fail to *build* (172 → 127 cases). The header edit and both test edits must land in **one commit**, as one task.

---

### `test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (native test)

Three sites. Current text and in-file idiom:

**Site 1 — `:237-240`** (the "third stale comment"; the block actually spans 230-240, and the `memory.cpp:489` pin is already stale — `BLANK_CHECK_CHUNK_SIZE` is at `:397` today):
```c
 * false so the deleted conditional's guard would have been satisfied. mem_size is a small 2048 --
 * BLANK_CHECK_CHUNK_SIZE (memory.cpp:489) -- because mem_util_blank_check
 * sets is_operation_in_progress and mallocs progress_data on its FIRST call
 * regardless of mem_size, so the oracle below does not depend on how large
 * mem_size is. */
```

**Site 2 — `:317-325`**, with its stale `memory.cpp:494-498` pin.

**Site 3 — the assertion at `:339-342`**, whose surviving Unity siblings define the local idiom exactly:
```c
    TEST_ASSERT_FALSE_MESSAGE(is_operation_in_progress(&h),
        "ERASE-02: is_operation_in_progress must be FALSE after exactly one "
        "flash_5v_page_write_init call with FLAG_SKIP_BLANK_CHECK clear -- "
        "mem_util_blank_check is the only setter of this flag on the write-INIT "
        "path, so TRUE here would mean the pre-write blank check still ran and "
        "left a multi-call INIT loop pending");
    TEST_ASSERT_NULL_MESSAGE(h.progress_data,        /* <-- DELETE this assertion */
        "ERASE-02: h.progress_data must be NULL -- a non-NULL value means "
        "mem_util_blank_check allocated a blank_check_progress_data_t block, "
        "i.e. the pre-write blank check still ran");
    TEST_ASSERT_NOT_EQUAL_MESSAGE(RESPONSE_CODE_ERROR, h.response_code,
        "ERASE-02: the removed blank check can no longer fail a write on a "
        "non-blank part");
```
**Idiom to match:** `TEST_ASSERT_*_MESSAGE`, message prefixed with the requirement ID (`"ERASE-02: "` / `"Case 30 (ERASE-01): "`), ` -- ` as the reason separator, 4-space continuation indent, and comment blocks in `/* … * … */` form with a leading `─── Phase NNN (REQ): … ───` banner.

**Reference's replacement comment (`git diff 8695ee5 a6b46f8`) — copy the shape, fix the claim:**
```c
    /* The companion `h.progress_data must be NULL` assertion is GONE, and so is
     * the field: mem_util_blank_check no longer mallocs a
     * blank_check_progress_data_t (it keeps its saved address in a file-scope
     * static), so there is no allocation left to observe. This is a loss of a
     * redundant PROBE, not of coverage -- is_operation_in_progress above is set
     * by the same statement of the same function that used to do the malloc, so
     * the behaviour under test is still pinned. */
```
**🚩 `"by the same statement"` is RESEARCH.md C-5 and is FALSE** — `set_operation_in_progress(handle);` (`:408`) and the `malloc` (`:409`) are two distinct statements. The correct, *stronger* formulation: *"unconditionally adjacent statements in the same then-branch of the same `if`, with no intervening control flow, early return or condition — so `is_operation_in_progress == false` strictly implies the branch never executed, which strictly implies the malloc never executed."* This phrasing appears **twice** in the reference (both files) and in a third comment block; fix all occurrences.

**Stale-pin decision (mechanical, settled precedent — decide, do not ask):** RESEARCH.md recommends **deleting the `memory.cpp:NNN` line numbers and naming the symbol instead** for all four in-scope sites, consistent with Phase 154's reflow-vs-delete precedent and because 156/157/158 will move `memory.cpp` again. The out-of-scope 5th stale pin at `test_eeprom28c_sdp.cpp:97` (`mem_util_set_address … memory.cpp:68`) does not mention `progress_data` and belongs to **Phase 159** — do not touch it.

---

### `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` (native test)

Two sites, same idiom. Comment block `:1770-1778` (with the stale `memory.cpp:494-512` pin) and the assertion at `:1788-1791`; surviving siblings at `:1783-1787` (`TEST_ASSERT_FALSE_MESSAGE`) and `:1792` (`sdp_assert_stream_equals(SDP_FIXED_DIP28_28C256, …)`) — the stream-identity assertion is untouched and is the case's real oracle.

---

### Before-figures record (planning document)

**Analog:** `.planning/v1.33/baseline-pre-sweep.md`. Directory contents (`ls .planning/v1.33/`): `CITATIONS-STALE.md`, `baseline-pre-sweep.md`, `sweep-citation-manifest.jsonl`, `sweep-citation-manifest-report.md`, `sweep-corpus-baseline.md`, `sweep-gate-dispositions.md`, `sweep-outcome-record.md`, `tools/`. Lowercase-hyphenated names; big records get YAML frontmatter.

**Frontmatter + opening pattern to copy** (`.planning/v1.33/baseline-pre-sweep.md:1-30`):
```markdown
---
title: Pre-sweep baseline — milestone v1.33, Phase 154
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "01"
measured: 2026-08-23
status: AUTHORITATIVE — every "before/after" comparison in Phase 154 is measured against this file
supersedes: >
  All baseline numbers in 154-RESEARCH.md ...
requirements: [SWEEP-05 (before-half), SWEEP-13 (branch anchors)]
---

# Pre-sweep baseline — v1.33 Phase 154

Every number in this file was measured on a **clean** working tree ...
Each number carries the verbatim command that produced it. Nothing here is quoted
from research.

## 1. Git anchors

| Field | Value |
|---|---|
| `PRE_DIRTY_SHA` | `8695ee52c27a4bee4387c5c489afd5f3d7275e8a` |
```
Note the two load-bearing conventions: **"each number carries the verbatim command that produced it"** and **"nothing here is quoted from research"** — the before-figures record must re-measure, not copy RESEARCH.md's tables. Add RESEARCH.md's own extra requirement: **label every figure warm or cold** (Phase 155's are warm; LAND-01/Phase 158 owns the cold re-record).

---

## Shared Patterns

### The checker convention — `tests/test_checker_convention.py` (applies to the new gate script; **HARD, mechanically enforced**)

**Source:** `tests/test_checker_convention.py:149-152` and its seven tests.
```python
CHECKER_GLOB = "check_*.py"

# Hardcoded floors -- see module docstring for what each counts and why a
# future checker addition must raise these in the same commit.
FLOOR = 6
FIXTURE_FLOOR = 15
```
Adding `scripts/check_no_heap_or_64bit_symbols.py` turns this module RED unless, **in the same commit**:
1. `tests/test_check_no_heap_or_64bit_symbols.py` exists (test 2: `check_<X>.py` → `test_check_<X>.py`, exact name).
2. At least one `tests/fixtures/planted_no_heap_or_64bit_symbols*` entry exists — file **or** directory (test 3, glob `planted_<stem>*` where stem is the name after `check_`).
3. The paired test module's **source text contains the checker's exact filename** (test 5) **and** a literal `returncode != 0` assertion (test 6).
4. `FLOOR` → 7 **and** `FIXTURE_FLOOR` → 16 (tests 1 and 4; current actual counts are 6 checkers / 29 `planted_*` entries, so `FIXTURE_FLOOR` has headroom — but the docstring's rule is explicit: *"A later phase that adds a firmware checker under `firestarter/scripts/` raises both floors deliberately in the SAME commit that adds the checker; lowering a floor is never the correct response to a red gate here."*)

The docstring also names the anti-hollow rationale the new gate must satisfy: *"BASE-08 requires that every checker introduced in v1.23 ships with a committed planted-violation fixture and a pytest proving the checker's non-zero exit against it."* This is the repo's own name for the hollow-gate failure mode VALIDATION.md's "planted negative" bullet demands.

### Lint / format / type gates on `scripts/` and `tests/`

**None.** Verified: no `pyproject.toml`, `setup.cfg`, `ruff.toml`, `.ruff.toml`, `mypy.ini`, `pytest.ini` or `tox.ini` anywhere in `firestarter/` (only `platformio.ini`); `grep -rn ruff .github/workflows/*.yml` → zero hits. A stale `.ruff_cache/` directory exists but nothing in the repo or CI invokes ruff. **The only gate a new Python file must pass is `pytest tests/ -v`** (`.github/workflows/build.yml:161`, `beta-build.yml:134`), preceded by `pip install pytest` (`build.yml:157-158`) — pytest is the *only* Python dependency CI installs, so the new files must be **stdlib + pytest only**. (Contrast: the *host* repo `firestarter_app` does have ruff/mypy gates — irrelevant here, and this phase is firmware-only.)

House style observed in `scripts/` and `tests/` regardless: module docstring with `Requirements:` / `Decisions covered:` lines, `Exit codes:` block, `Usage:` block, an explicit **Non-claim** paragraph, and ` -- ` (double hyphen) rather than an em dash inside code comments.

### Fail-closed / never-vacuous discipline (applies to both new gates)

Recurring, named idiom across `check_size_baseline.py`, `check_release_assets.py`, `check_erase_no_vpp.py`, `check_cmake_manifest.py`:
- a **never-vacuous guard run BEFORE the per-item loop** — "a gate that requires nothing must not print `PASS:`";
- **exit 2 for "cannot render a verdict"** vs **exit 1 for "found a real violation"**, so the paired pytest can tell them apart;
- missing input is **never** a silent pass, and in `tests/` it must **FAIL, never SKIP** (`test_write_path_source_contract_v131.py:671-699` enforces that on itself).

### Requirement-ID labelling

Every artefact ties back by ID: Unity messages start `"ERASE-02: "`; pytest and script docstrings carry `Requirements: DEAD-01, DEAD-03` and `Decisions covered: D-01, …`. Carry `DEAD-0N` / `D-0N` labels through all five new/edited files.

---

## No Analog Found

| File / capability | Role | Data Flow | Reason |
|---|---|---|---|
| `tests/test_voltage_reformulation_oracle.py` — **the numerical half** | pytest oracle | transform | **No test in either repo reimplements firmware arithmetic in Python for comparison.** Searched `tests/` for `//`-integer-division formula transcriptions, `* 95`, `// 100`, "reimplement"/"Python model" — zero. The closest thing is `tests/test_config_storage_dualslot.py`, which does the **opposite**: it **host-compiles the shipped C by explicit path** (`_compile()` at `:507-522`, `gcc -std=gnu++17 -Wall -Wextra -I include -I platform/py32f071/src <core.cpp> <fresh_tu.cpp>`, then runs the binary and parses stdout) and its docstring **explicitly rejects** "an independent fake reimplementation of the algorithm living only in this test (it would prove a copy behaves — the exact hollow-gate shape Phases 118 and 124 each had to unwind)". ⚠ **The planner must confront this tension head-on:** DEAD-04's oracle *is* an independent reimplementation, and this repo has a written precedent calling that shape hollow. The mitigation is exactly what RESEARCH.md mandates — the **source-contract scan is not optional**; it is what converts "a copy behaves" into "the shipped text is the modelled formula". The plan should cite `test_config_storage_dualslot.py`'s rejection by name and state why compile-the-real-C (its option) is unavailable here: `src/boards/rurp_common.cpp:12` wraps the whole file in `#if defined(ARDUINO_AVR_UNO) \|\| defined(ARDUINO_AVR_ATmega328PB) \|\| defined(ARDUINO_AVR_LEONARDO)` and the body writes `ADMUX`/`ADCSRA` and calls `analogRead`/`rurp_get_config` — RESEARCH.md's rejected options (b) and (c). |
| Toolchain-binary invocation from a gate script | build tooling | subprocess | Zero precedent: no script or test in either repo invokes `avr-nm`, `avr-objdump` or `avr-size`. `platformio.ini:220-224` even records that "avr-nm symbol capture" was deliberately **not attempted** (backlog 999.15 / gh#8). Locating the toolchain and exiting 2 when absent is genuinely new; everything around it is copied from `check_release_assets.py`. Do **not** present this as discharging that todo. |
| A committed ELF (binary) fixture | fixture | file | Every existing fixture is text (`captured_*.log`, `planted_*.log`, `.cpp`) or a tiny `.hex` tree. No binary-ELF fixture exists — a further reason to prefer the `--nm-output` captured-text seam. |

---

## Metadata

**Analog search scope:** `/workspaces/firestarter/{scripts,tests,src,include,test,platformio.ini,.github/workflows}`, `/workspaces/.planning/v1.33/`, and the preserved reference range `8695ee5..a6b46f8`.
**Firmware HEAD at mapping time:** `2ad5b32`, working tree clean.
**Analogs read in full or by targeted range:** `scripts/check_release_assets.py` (whole), `scripts/check_erase_no_vpp.py` (`:1-200`, `:200-345`), `tests/test_checker_convention.py` (`:1-200`), `tests/test_check_size_baseline.py` (`:1-60`, `:490-668`), `tests/test_write_path_source_contract_v131.py` (`:140-300`, `:394-428`, `:641-700`), `tests/test_config_storage_dualslot.py` (`:1-40`, `:480-560`), `tests/test_check_release_assets.py` (index), `src/boards/uno_rurp_shield.cpp:25-60`, `src/proms/memory.cpp:453-493`, `include/firestarter.h:223-234`, both native suites' cited ranges, `platformio.ini` `build_src_filter` sites.
**Pattern extraction date:** 2026-08-23
