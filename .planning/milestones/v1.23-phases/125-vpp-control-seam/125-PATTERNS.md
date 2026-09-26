# Phase 125: VPP Control Seam - Pattern Map

**Mapped:** 2026-07-31
**Files analyzed:** 5 (4 created, 1 modified) + 1 planning artifact
**Analogs found:** 5 / 5 (every file has a real in-tree analog; nothing needs invention)

> **Path convention — read this first.** Every code path in this document is relative to the
> **firmware submodule root `/workspaces/firestarter`** (branch `v1.23-py32f071-integration`),
> *not* to the meta repo `/workspaces`. So `include/rurp_vpp.h` means
> `/workspaces/firestarter/include/rurp_vpp.h`, and `tests/test_pinmap_guard_fires.py` means
> `/workspaces/firestarter/tests/test_pinmap_guard_fires.py`. The only file outside the
> firmware repo is the evidence artifact `125-NONREGRESSION.md`, which lives in the meta repo
> at `.planning/phases/125-vpp-control-seam/`.
>
> **Never write into `firestarter_py32_ci/` or `firestarter_app_py32/`** — gitignored
> worktrees of the same repos, never gitlinked.
>
> **Explicitly not in this file set, per the operator's Option A on RESEARCH C-1:**
> `include/rurp_shield.h`, `platformio.ini`, `src/boards/rurp_common.cpp`,
> `include/rurp_types.h`, `src/rurp_config_utils.cpp`, `include/messages.h`. No analog is
> offered for any of them because no edit is planned. The last three are *pinned
> byte-identical* by VPP-03.

---

## File Classification

| New/Modified File (firmware repo) | Role | Data Flow | Closest Analog | Match Quality |
|-----------------------------------|------|-----------|----------------|---------------|
| `include/rurp_vpp.h` | config / capability header | compile-time (preprocessor) | `include/boards/py32f071_pinmap_guard.h` | exact |
| `src/rurp_vpp.cpp` | service (refusal-shaped impl) | request-response (in-process, stateless) | `src/proms/not_implemented.cpp` | role-match |
| `tests/test_vpp_seam_manual_on_every_board.py` | test (subprocess-driven gate) | file-I/O + process spawn | `tests/test_pinmap_guard_fires.py` | exact (extended: compile-**and-run**) |
| `tests/test_pr45_non_ancestry.py` | test (subprocess-driven gate) | process spawn (`git`) | `tests/test_golden_trace_identity.py` + `tests/test_pinmap_guard_fires.py` | exact |
| `platform/py32f071/CMakeLists.txt` (2 lines) | config / build manifest | build-time declaration | its own existing `FIRESTARTER_COMMON_SOURCES` + `target_compile_definitions` blocks | exact (self-analog) |
| `.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md` (meta repo) | evidence artifact | document | `124-NONREGRESSION.md`, `123-NONREGRESSION.md` | exact |

---

## THE TWO TRAPS — read before assigning any plan

### Trap 1: the two new pytest modules must NOT be `scripts/check_*.py`

RESEARCH C-11 **planted** one and measured the cost. `tests/test_checker_convention.py` is a
filesystem-derived meta-test with hardcoded floors and no allow-list:

```python
# tests/test_checker_convention.py:110-124  (verbatim)
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
FLOOR = 5
FIXTURE_FLOOR = 10
```

Planting `scripts/check_pr45_ancestry.py` produced (C-11, measured):

```
--- WITH planted scripts/check_pr45_ancestry.py ---
FAILED tests/test_checker_convention.py::test_every_checker_has_paired_test_module
FAILED tests/test_checker_convention.py::test_every_checker_has_planted_fixture
2 failed, 5 passed
--- WITHOUT it (control) --- 7 passed
```

**Cost of the `scripts/` shape: four artifacts in the same commit** — the checker,
`tests/test_check_pr45_ancestry.py`, a `tests/fixtures/planted_pr45_ancestry*` entry, **and**
`FLOOR 5→6` + `FIXTURE_FLOOR 10→11`. The `tests/test_*.py` shape costs **zero**: the glob is
non-recursive over `scripts/` only, so a file under `tests/` is invisible to it. Never lower
either floor.

### Trap 2: the return value crosses the process boundary on stdout, never the exit code

`RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED == 1`, which is also the exit code of a compile failure,
a link failure, an uncaught signal wrapper and a crash. `return (int)result;` would make the
**correct** answer indistinguishable from every failure mode.

**The convention `test_pinmap_guard_fires.py` establishes for reading subprocess output**
(`:99-108`, verbatim) — list argv, never a shell, `capture_output=True, text=True`, and the
whole `CompletedProcess` returned so callers assert on `.returncode`, `.stdout` and `.stderr`
separately:

```python
def _preprocess(compiler, tu_path, define=None):
    """Run the resolved compiler in preprocess-only mode (-E) against the
    given translation unit, with the repository's include/boards directory
    on the include path. Output is discarded; stdout, stderr and returncode
    are captured. List argv only -- the shell is never invoked."""
    argv = [compiler, "-E", "-I", str(_INCLUDE_BOARDS)]
    if define is not None:
        argv += [f"-D{_MACRO_NAME}={define}"]
    argv += [str(tu_path), "-o", os.devnull]
    return subprocess.run(argv, capture_output=True, text=True)
```

The analog's assertion style is `returncode != 0` **plus** an expected-substring check on
`.stderr` (`:131-138`) — it never trusts an exit code alone. Phase 125's board legs invert
that: require `compile.returncode == 0`, require `run.returncode == 0`, and **parse the value
out of `run.stdout`** (`'mode=0 result=1'`, the measured prototype output in RESEARCH §Pattern 3).

---

## Pattern Assignments

### `include/rurp_vpp.h` (config / capability header, compile-time)

**Analog:** `include/boards/py32f071_pinmap_guard.h` (43 lines, Phase 124 Plan 09)

This is the *exact* structural analog: a dependency-free header whose only job is to **test a
macro the build supplies**, with the reasoning written beside it and a named fire-proof test
cited in the comment.

**Pattern to copy — the header opens with `#pragma once`, then a long block comment with
ALL-CAPS section labels, then the guard and nothing else** (`:1-43`, abridged; read the file
in full when authoring):

```c
#pragma once

/*
 * Phase 124 Plan 09 (MERGE-04, D-14) -- dependency-free fragment header
 * carrying the PY32F071 pin-map "configured for a real build" guard.
 *
 * WHY THIS IS A SEPARATE, DEPENDENCY-FREE FILE:
 *   ... This file includes NOTHING AT ALL, so a plain host
 *   preprocessor (`g++ -E`) can evaluate it standalone. ...
 *
 * WHAT THIS HEADER TESTS, NOT DEFINES:
 *   RURP_PY32F071_PINMAP_CONFIGURED is supplied ONLY by the ARM build's
 *   compile definitions (platform/py32f071/CMakeLists.txt's
 *   target_compile_definitions). This header never defines it -- it only
 *   TESTS what the build supplies. A build that forgets to supply it now
 *   fails at the preprocessor with a named error instead of silently
 *   compiling an unconfigured, provisional pin map that could energise a
 *   PROM.
 *
 * THE CONDITION BELOW FIRES ON BOTH THE UNSET AND THE EXPLICITLY-ZERO ARM:
 *   `!defined(X) || !X` states the defined()-ness explicitly rather than
 *   relying on an undefined identifier evaluating to 0 in `#if`. ...
 *   also survives a later `-Wundef` build flag ...
 *
 * FIRE-PROOF:
 *   tests/test_pinmap_guard_fires.py preprocesses THIS file standalone with
 *   a host compiler across three arms -- macro unset, =1, =0 -- and asserts
 *   the exact discriminating exit codes and error text recorded below.
 */

#if !defined(RURP_PY32F071_PINMAP_CONFIGURED) || !RURP_PY32F071_PINMAP_CONFIGURED
#error "RURP_PY32F071_PINMAP_CONFIGURED is not set: ... This macro must be supplied by the build system (platform/py32f071/CMakeLists.txt's target_compile_definitions), not by this header."
#endif
```

**Four concrete things to carry across:**

1. **`#pragma once`**, not an include-guard macro — the house idiom for new headers here.
2. **A named phase/decision attribution in the first comment line** (`Phase 125 (VPP-01,
   D-06/D-09/D-10)`), and a **`FIRE-PROOF:` section naming the pytest module** that proves the
   guard fires. The analog's fire-proof pointer is what a reader follows; reproduce it.
3. **The `#error` message must name where the macro is supposed to come from.** The analog's
   does (`"...must be supplied by the build system (platform/py32f071/CMakeLists.txt's
   target_compile_definitions), not by this header."`). D-06's message should read the same way.
4. **A single-quoted `#error` message on one line** — `test_pinmap_guard_fires.py:111-118`
   reads the message back out of the header with `re.search(r'#error\s+"([^"]*)"', text)`
   rather than hardcoding it. If Phase 125's harness reuses that trick (recommended), the
   `#error` text must be a **single double-quoted string on one line**, or the regex misses it.
   Note: `rurp_vpp.h` carries **one** `#error`, and `rurp_vpp.cpp` carries a **second** — a
   naive "expected exactly one `#error`" assert must be scoped per-file.

**Deltas from the analog, all mandated by RESEARCH:**

- The condition is `#if !defined(RURP_HAS_VPP_DAC)` with a nested `#if defined(__AVR__)` →
  `#define RURP_HAS_VPP_DAC 0` arm and an `#else #error` arm (D-06's verbatim block). It is
  **not** the analog's `!defined(X) || !X` shape — `0` is a legitimate value here, unlike the
  pinmap macro where `0` must also fire.
- It includes `<stdint.h>` (the analog includes nothing). That is still dependency-free in the
  sense the analog cares about: host `g++ -E` resolves it standalone.
- It adds two enums and three `extern "C"` declarations after the guard.
- **The `__AVR__` arm's comment must state PERMANENCE, not provisionality** (D-05, and
  RESEARCH Anti-Patterns): *"Permanent, not provisional: no Arduino/AVR-class RURP board
  carries a VPP DAC — the rail is set by the operator's pot. Operator, 2026-07-31."*
- **Record C-13's reasoning in the comment** so a later phase does not "improve" `__AVR__`
  into `RURP_PLATFORM_AVR`: that macro is derived from `__AVR__`, is never defined during an
  AVR build, and its header (`include/rurp_platform.h`) has a terminal `#error` whose
  `RURP_PLATFORM_NATIVE` escape references a macro defined nowhere in either repo.

**Second analog for the "macro made deliberately load-bearing, reasoning beside it" idiom** —
the `RURP_PY32F071_PINMAP_PROVISIONAL` bridge block in
`include/boards/py32f071_rurp_shield.h:37-69`. Copy its *comment discipline*: it enumerates
the two jobs the block does, and closes with an explicit **"REMOVING this block would…"**
paragraph naming both consequences:

```c
#define RURP_PY32F071_PINMAP_PROVISIONAL 1

/*
 * Phase 124 Plan 08 (MERGE-04, D-11/D-12): bridge this board-specific
 * provisional flag to the platform-neutral RURP_PINMAP_PROVISIONAL flag
 * that include/rurp_pinmap_guard.h's shared refusal predicate tests. This
 * single block does two jobs at once:
 *
 *   1. The `#if RURP_PY32F071_PINMAP_PROVISIONAL` test below is itself a
 *      real CONSUMER of RURP_PY32F071_PINMAP_PROVISIONAL, discharging
 *      scripts/check_orphan_provisional.py for THIS macro ...
 *   2. It DEFINES the neutral flag, wrapped in its own inner #ifndef so a
 *      command-line definition of RURP_PINMAP_PROVISIONAL still wins
 *      without triggering a macro-redefinition warning
 *      (check_build_warnings.py counts those).
 * ...
 * REMOVING this block would make RURP_PY32F071_PINMAP_PROVISIONAL orphaned
 * again (zero consumers) AND would silently stop defining
 * RURP_PINMAP_PROVISIONAL, which would make configure_memory()'s refusal
 * compile away on this board -- do not remove without replacing both jobs.
 */
#if RURP_PY32F071_PINMAP_PROVISIONAL
#ifndef RURP_PINMAP_PROVISIONAL
#define RURP_PINMAP_PROVISIONAL 1
#endif
#endif
```

Note the analog's own note that **`firestarter/tests/` is not scanned by
`check_orphan_provisional.py`**, so a pytest can never serve as a macro's consumer. That gate
is not in play for `RURP_HAS_VPP_DAC` (not `*_PROVISIONAL`-named, D-11), but the *reason* the
consumers must live in `include/`/`src/` is the same reason D-11 names them there.

---

### `src/rurp_vpp.cpp` (service, request-response, ~15-18 lines)

**Analog:** `src/proms/not_implemented.cpp` (19 lines, verbatim below)

The in-tree template for a minimal refusal-shaped `.cpp`: MIT banner, a tight include block,
one function that sets nothing up and returns a refusal.

```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */

#include "not_implemented.h"
#include "firestarter.h"
#include "logging_id.h"
#include "messages.h"

void configure_not_implemented(firestarter_handle_t* handle) {
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = NULL;
    handle->firestarter_operation_end = NULL;
    LOG_ERROR_ID_U8(MSG_ERR_PROTOCOL_NOT_IMPLEMENTED, (uint8_t)handle->protocol);
    handle->response_code = RESPONSE_CODE_ERROR;
}
```

**Copy:** the exact five-line MIT banner (byte-for-byte — it is uniform across `src/`), the
own-header-first include ordering, and the "refusal is a return value, not a side effect"
shape.

**Deltas, all mandated:**

- **Include exactly `"rurp_vpp.h"` and nothing else** (D-02). The analog's four includes are
  precisely what this file must not have — no `firestarter.h`, no `messages.h`, no
  `logging_id.h`, no `rurp_shield.h`, no `<Arduino.h>`, no PY32 HAL, no `rurp_get_config()`.
  D-02 is a **standing constraint**, not a local convenience: it is what lets the harness need
  zero stub scaffolding.
- **It carries the SECOND `#error`** — the one C-4 proved is required and that D-06's header
  block does **not** provide. Measured: with only the header guard, `-DRURP_HAS_VPP_DAC=1`
  exits **0**, so D-03's non-vacuity leg would pass vacuously. RESEARCH §Pattern 1 gives the
  block:

  ```c
  /* src/rurp_vpp.cpp — the second guard C-4 shows is required by D-03 */
  #if RURP_HAS_VPP_DAC
  #error "RURP_HAS_VPP_DAC=1 selects a closed-loop VPP DAC implementation that this branch does not provide"
  #endif
  ```

  **Wording is load-bearing (C-17):** scope it to *this branch*. `origin/feature/py32f071-full-support`
  (PR #47, closed) really does set `RURP_HAS_VPP_DAC=1` and implement
  `rurp_vpp_dac_write` / `rurp_vpp_control_enable` with a feedback loop in
  `platform/py32f071/src/analog.c:168-237`. A universal claim ("no board provides") is
  falsifiable with one `git show`.
- The three bodies are trivial: `rurp_vpp_control_mode()` → `RURP_VPP_CONTROL_MANUAL`,
  `rurp_set_vpp_target_mv(...)` → `RURP_VPP_MANUAL_ADJUSTMENT_REQUIRED`,
  `rurp_disable_vpp_control()` → no-op. Zero production callers (D-11).
- Parameters are unused. There is **no `-Werror` anywhere** in the tree (C-14: `grep -rn
  Werror platform/ scripts/ .github/` → zero hits), but the harness compiles with
  `-Wall -Wextra` and the prototype measured **0 bytes of warning output** — so cast-to-void
  or `(void)param;` the unused parameters rather than accepting a new warning.

---

### `tests/test_vpp_seam_manual_on_every_board.py` (test, subprocess-driven)

**Analog:** `tests/test_pinmap_guard_fires.py` — **read all 235 lines before authoring.** This
is the direct precedent D-01 names, and five of its six structural features transfer verbatim.

**1. Module docstring pattern** (`:1-48`): MIT banner → `Phase NNN Plan NN — <what>` →
`Requirements:` / `Decisions covered:` lines → a **defect-class paragraph** explaining why the
module exists → the conftest note → a numbered `Coverage:` list, one entry per test function,
each naming the test and the mechanical outcome it asserts.

```python
"""
Project Name: Firestarter
Copyright (c) 2024 Henrik Olsson

Permission is hereby granted under MIT license.

Phase 124 Plan 09 — MERGE-04's fire-proof for the PY32F071 pin-map guard.

Requirements: MERGE-04
Decisions covered: D-14
...
Self-contained path resolution below -- NOT in conftest.py (firestarter/tests/
has no conftest.py anywhere in the repo; a recorded house-rule pattern
decision per test_update_version.py's own comment, not an omission).
Stdlib and pytest only.

Coverage:
  1. test_guard_fires_when_the_macro_is_unset -- no define -> non-zero exit,
     the fragment's own #error text appears in stderr.
  ...
  6. test_compiler_is_required_not_optional -- this module's own source
     contains no skip decorator and no skip call, so the fail-closed
     contract is self-enforcing.
"""
```

**2. Self-contained path resolution** (`:56-62`) — **there is no `conftest.py` anywhere in the
firmware repo, and none is to be added.** RESEARCH verified: `find . -name conftest.py -not
-path './.pio/*'` returns nothing, and there is no `pytest.ini`, `pyproject.toml`, `setup.cfg`
or `tox.ini` either. Registration is by filename convention alone. Every module resolves its
own paths at module scope:

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_INCLUDE_BOARDS = _REPO_ROOT / "include" / "boards"
_GUARD_HEADER = _INCLUDE_BOARDS / "py32f071_pinmap_guard.h"
_BOARD_HEADER = _INCLUDE_BOARDS / "py32f071_rurp_shield.h"

_MACRO_NAME = "RURP_PY32F071_PINMAP_CONFIGURED"
```

For Phase 125 the equivalents are `_INCLUDE = _REPO_ROOT / "include"`,
`_SEAM_HEADER = _INCLUDE / "rurp_vpp.h"`, `_SEAM_SRC = _REPO_ROOT / "src" / "rurp_vpp.cpp"`,
`_MACRO_NAME = "RURP_HAS_VPP_DAC"`. Note the `-I` is `include/`, not `include/boards/`.

**3. Fail-closed compiler resolution** (`:65-84`, verbatim) — copy this function almost
unchanged; only the docstring's final sentence needs revising per C-7 (see below):

```python
def _resolve_compiler():
    """Resolve the host C++ compiler, fail-closed.

    Deliberately never bypassed via any decorator or runtime call that would
    mark this outcome as skipped, anywhere in this module: doing so would
    recreate the exact BASE-02/BASE-03 absence-proxy failure class this
    milestone's Phase 123 removed. If $CXX (or 'g++') cannot be resolved via
    shutil.which, this raises via a plain assert, which the test runner
    reports as a FAILURE, never a skipped outcome. ...
    """
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    assert compiler is not None, (
        "host C++ compiler not found on PATH (checked $CXX, falling back to "
        "'g++'). This must FAIL the suite, never be silently skipped -- no "
        "embedded toolchain is invoked here."
    )
    return compiler
```

> **Correct one inherited sentence.** The analog's docstring asserts *"both firmware CI
> workflows run `pytest tests/ -v`"*. True of `build.yml` (push/PR to `main`) and
> `beta-build.yml` (push to `beta`) — but **neither fires on `v1.23-py32f071-integration`, and
> `py32f071.yml` has no pytest step at all** (C-7). The new module runs in **zero CI legs on
> this branch**. Do not copy the CI-coverage claim; say plainly that the local run is the
> evidence.

**4. Temp TU built fresh, never committed** (`:87-96`) — no fixture TU under `tests/fixtures/`
(also what D-03 declined):

```python
def _write_tu(tmp_path):
    """Write a minimal translation unit that includes ONLY the fragment
    header, by relative name (resolved via the -I include path passed to
    the compiler in _preprocess), plus an empty body. No fixture
    translation unit is committed to the repo ..."""
    tu_path = tmp_path / "pinmap_guard_tu.cpp"
    tu_path.write_text('#include "py32f071_pinmap_guard.h"\n')
    return tu_path
```

Phase 125's TU is the measured shim from RESEARCH §Pattern 3, written into `tmp_path`:

```cpp
#include "rurp_vpp.h"
#include <cstdio>
int main(void) {
    printf("mode=%d result=%d\n", (int)rurp_vpp_control_mode(),
           (int)rurp_set_vpp_target_mv(12000, 200, 50));
    rurp_disable_vpp_control();
    return 0;
}
```

**5. The subprocess convention** — `_preprocess` at `:99-108`, quoted in full under **Trap 2**
above. Four deltas for compile-and-run, all validated by the RESEARCH prototype:

- Drop `-E`; emit a real binary to `tmp_path / "<leg>"`, and pass **both** the temp `main.cpp`
  and the production `src/rurp_vpp.cpp` in one `g++` invocation.
- Add `-std=gnu++17 -Wall -Wextra` and `-I <repo>/include`.
- Run the binary as a **second** `subprocess.run`, list argv, `capture_output=True`.
- **Parse the value from `run.stdout`; require `run.returncode == 0`.** See Trap 2.

**6. The self-enforcement leg** (`:215-234`, verbatim) — copy this whole test, including the
string-concatenation trick that stops its own source tripping its own scanner:

```python
def test_compiler_is_required_not_optional():
    """Coverage 6 -- this module's own source contains no skip decorator and
    no skip call anywhere, so the fail-closed contract in _resolve_compiler
    is self-enforcing and cannot be silently bypassed by a future edit.

    The two needle strings below are built via concatenation (not written
    verbatim) so this test's own assertion text does not trip its own
    check -- the literal substrings must appear NOWHERE in this file,
    including inside this test's failure messages."""
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
    assert skip_call not in own_text, (
        "expected no " + skip_call + " call anywhere in this module -- the "
        "compiler-absence case must FAIL, never SKIP."
    )
    assert skipif_marker not in own_text, (
        "expected no @pytest." + skipif_marker + " decorator anywhere in "
        "this module -- the compiler-absence case must FAIL, never SKIP."
    )
```

**7. Assertion-message discipline** (`:131-138`) — every failure message states what was
expected **and dumps both streams**. Never a bare `assert result.returncode == 0`:

```python
    assert result.returncode != 0, (
        f"expected a non-zero exit with the macro unset (the guard must "
        f"fire).\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert expected_text in result.stderr, (
        f"expected the fragment's own #error text in stderr.\n"
        f"Expected substring: {expected_text!r}\nGot stderr:\n{result.stderr}"
    )
```

**8. Read the `#error` text out of the header at test time, don't hardcode it** (`:111-118`):

```python
def _expected_error_text():
    """Read the #error message out of the fragment header at test time,
    rather than hardcoding it a second time here -- a literal that could
    silently desync from the real header on a future edit."""
    text = _GUARD_HEADER.read_text()
    m = re.search(r'#error\s+"([^"]*)"', text)
    assert m, f"expected exactly one #error directive with a quoted message in {_GUARD_HEADER}.\nGot:\n{text}"
    return m.group(1)
```

Phase 125 needs **two** of these (header `#error` and `.cpp` `#error`), each scoped to its own
file — do not reuse the "exactly one" assertion across both.

**9. A `test_seam_source_is_dependency_free` leg**, modelled on the analog's coverage-4
(`:184-193`), asserting `src/rurp_vpp.cpp`'s only `#include` is `"rurp_vpp.h"`. This is what
turns D-02's standing constraint into something a future edit cannot quietly break:

```python
def test_fragment_header_is_dependency_free():
    text = _GUARD_HEADER.read_text()
    assert not re.search(r"^\s*#include\b", text, re.MULTILINE), (
        f"expected {_GUARD_HEADER} to be dependency-free (no #include "
        f"directive) -- hoisting only works if a host preprocessor can "
        f"evaluate this file standalone.\nGot:\n{text}"
    )
```

**Leg inventory for this module** (D-01/D-03/D-04/D-08 + the two meta legs):

| leg | mechanism | required outcome |
|---|---|---|
| uno | `-D__AVR__ -DARDUINO_AVR_UNO -DRURP_BOARD_NAME="uno" -DSERIAL_ON_IO` | compile 0, run 0, stdout `mode=0 result=1` |
| leonardo | `-D__AVR__ -DARDUINO_AVR_LEONARDO -DRURP_BOARD_NAME="leonardo" -DDATA_BUFFER_SIZE=1024` | same |
| uno328pb | `-D__AVR__ -DARDUINO_AVR_ATmega328PB -DRURP_BOARD_NAME="uno328pb" -DSERIAL_ON_IO` | same |
| py32f071 | `-DRURP_PLATFORM_PY32F071=1 -DRURP_HAS_VPP_DAC=0 -DRURP_BOARD_NAME="py32f071"` | same |
| forced-DAC (D-03) | `-D__AVR__ -DRURP_HAS_VPP_DAC=1`, **compiling the `.cpp`** | compile non-zero, `.cpp`'s `#error` text in stderr |
| unset-and-non-AVR (D-08) | no defines | compile non-zero, **header's** `#error` text in stderr |
| drift (D-04) | file reads of `platformio.ini` + `platform/py32f071/CMakeLists.txt` | anchors present |
| no-skip meta | self-source scan | analog's coverage-6, verbatim |

**Drift-leg anchors — C-6, this is a fail-on-arrival trap.** `ARDUINO_AVR_UNO` /
`ARDUINO_AVR_LEONARDO` / `ARDUINO_AVR_ATmega328PB` come from the framework and board JSON and
appear **nowhere** in `platformio.ini` (measured). A leg grepping for them fails immediately,
and the tempting "fix" is to weaken it into something vacuous. Honest anchors, all literal and
all present:

| board | anchors to assert in `platformio.ini` |
|---|---|
| uno | `[env:uno]` + `board = uno` |
| uno328pb | `[env:uno328pb]` + `board = ATmega328PB` |
| leonardo | `[env:leonardo]` + `board = leonardo` |
| py32f071 | `RURP_PLATFORM_PY32F071=1` + `RURP_BOARD_NAME="py32f071"` in the CMake `target_compile_definitions` |

Also note `RURP_BOARD_NAME` is a **literal** only for uno328pb; uno and leonardo use
`${this.board}`.

**And bound the claim (C-6, Pitfall 8).** `rurp_vpp.h` consults exactly two macros —
`__AVR__` and `RURP_HAS_VPP_DAC`. Nothing in the seam distinguishes Uno from Leonardo from
uno328pb. The four legs prove **one AVR fact plus one explicit ARM declaration**, not four
independent per-board facts. Say that in the module docstring and in
`125-NONREGRESSION.md`; the *real* AVR-compiler resolution is discharged by the three
`pio run` builds Criterion 4 already requires.

---

### `tests/test_pr45_non_ancestry.py` (test, subprocess-driven `git`)

**Analogs:** `tests/test_golden_trace_identity.py` (the `git`-subprocess house style) +
`tests/test_pinmap_guard_fires.py` (the fail-closed + self-enforcement skeleton).

`test_golden_trace_identity.py:1-80` is the closest analog for a pytest whose subprocess is
`git`, and its docstring states the two conventions to copy:

```
This module never imports check_*.py machinery: it is a standalone pytest
module asserting directly against the committed inventory JSON and the live
firmware tree via `git` subprocess calls (list-form argv, invoked directly
rather than through a shell) and plain file reads. ...

Self-contained path resolution below -- NOT in conftest.py ...
Stdlib and pytest only.
```

```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
```

Note also its **coverage-6**: `test_git_is_required_not_optional` — the same self-enforcement
leg as the compiler analog's, applied to a missing `git` binary. Copy it; and copy its
docstring's own self-avoidance note (*"The exact two patterns this test scans for are named in
its own docstring below, not repeated here"*).

**The subprocess helper and the whole test, from RESEARCH §Code Examples (verified command
shapes, observed against `HEAD = a145081b59d94530583b9ce365db03ff567d0c2c`):**

```python
PR45_SHAS = (
    "04fd9b3", "fc0b2c7", "86f351a", "768580f", "05f4a77",
    "b964ee6", "9134f2a", "d285b83", "71278d0", "a47228d",
)  # exactly the 10 in `git rev-list origin/beta..origin/feature/common-vpp-calibration`

def _git(*args):
    return subprocess.run(["git", "-C", str(_REPO_ROOT), *args],
                          capture_output=True, text=True)

def test_no_pr45_commit_is_an_ancestor_of_head():
    assert len(PR45_SHAS) == 10, "never-vacuous: the SHA list must be the full 10"
    checked, ancestors = 0, []
    for sha in PR45_SHAS:
        exists = _git("cat-file", "-e", f"{sha}^{{commit}}")
        assert exists.returncode == 0, (            # exit-2 class: tool/config error,
            f"{sha} is not a local object -- fetch "  # NEVER a silent clean pass
            f"origin/feature/common-vpp-calibration first; an absent object must "
            f"not read as 'not an ancestor'"
        )
        r = _git("merge-base", "--is-ancestor", sha, "HEAD")
        assert r.returncode in (0, 1), f"git failed unexpectedly for {sha}: {r.stderr}"
        if r.returncode == 0:
            ancestors.append(sha)
        checked += 1
    assert checked == 10
    assert not ancestors, f"PR #45 commits reachable from HEAD: {ancestors}"
```

**Three non-negotiables (C-2, measured):**

- **Never `--all`.** `git rev-list --all | grep -c '^05f4a77…$'` → **1**, because PR #45's ref
  is fetched locally. Scoped to `HEAD` → **0**. Every reachability test must be HEAD-scoped.
- **Never `git log --grep`.** It searches *messages*: `git log --all --grep=05f4a77 --oneline`
  → **zero rows today**, and it would still return zero after a cherry-pick with a rewritten
  message — the exact evasion Criterion 1 exists to catch.
- **Exit 128 is a tool error, not "clean."** Measured: `git merge-base --is-ancestor
  deadbeef…deadbeef HEAD` → `fatal: Not a valid commit name`, **exit 128**. A naive
  `if ! git merge-base --is-ancestor …: pass` therefore treats a typo'd or unfetched SHA as
  clean. The `assert r.returncode in (0, 1)` line above is what closes that.

**Optional second leg — content divergence** (RESEARCH C-3 recorded the blobs; cheap and
non-vacuous, recommended on the same module):

```python
PR45_BLOBS = {
    "include/rurp_vpp.h":  "c982173813b38ec745b59d6e02817f2504d6c6b4",
    "src/rurp_vpp.cpp":    "fcbe009dffcd46139802f8779865a1d7aa331880",
}
# assert git hash-object <path> != PR45_BLOBS[path] for both
```

**Fresh-clone caveat to encode in the assertion message:** `git cat-file -e` succeeds here
only because PR #45's ref is fetched. In a clone without it the objects are absent and the
gate must fail loudly naming `origin/feature/common-vpp-calibration` — which is what the
message above does.

---

### `platform/py32f071/CMakeLists.txt` (config / build manifest, +2 lines)

**Analog: the file's own two existing blocks.** This phase adds lines and invents nothing.

**Line 1 — the source-list entry.** Current state (lines 30-52 of the file; the five
`# PY32_EXCLUDED:` lines sit immediately above `set(FIRESTARTER_COMMON_SOURCES` and are part
of the required idiom):

```cmake
# PY32_EXCLUDED: src/boards/uno_rurp_shield.cpp -- AVR board impl, no ARM analogue
# PY32_EXCLUDED: src/boards/leonardo_rurp_shield.cpp -- AVR board impl, no ARM analogue
# PY32_EXCLUDED: src/boards/rurp_common.cpp -- AVR-specific common
# PY32_EXCLUDED: src/dev_tools.cpp -- no ARM dev-tools TU; DEV_TOOLS resolves to 0 by the shared default (MERGE-08, D-02)
# PY32_EXCLUDED: src/rurp_config_utils.cpp -- Phase 126 per-platform config backend split; THIS EXCLUSION WILL NEED REVISITING in Phase 126, it is not a permanent exclusion.
set(FIRESTARTER_COMMON_SOURCES
    "${REPOSITORY_ROOT}/src/firestarter.cpp"
    ...
    "${REPOSITORY_ROOT}/src/proms/not_implemented.cpp"
    "${REPOSITORY_ROOT}/lib/jsmn/src/jsmn.c"
)
```

The added entry must be **exactly** `"${REPOSITORY_ROOT}/src/rurp_vpp.cpp"`. C-12 read the
implementation: `enforced_common_relpaths` is built via `resolved.relative_to(_ROOT)`
(`check_cmake_manifest.py:293-299`), so the `${REPOSITORY_ROOT}/` idiom is what makes the
string match. **16 entries → 17.** The list is `rglob`-enumerated and sorted on the checker
side, so *ordering is irrelevant* — but place it among the top-level `src/*.cpp` entries
(before the `src/proms/` group) for readability.

D-12 is **non-optional in both directions** and C-12 proved it both ways:

```
# planted src/rurp_vpp.cpp UNNAMED:
FAIL: … src/rurp_vpp.cpp: present in tree, not named in FIRESTARTER_COMMON_SOURCES,
      and not covered by a reasoned PY32_EXCLUDED entry
exit=1
# named:
PASS: …/platform/py32f071/CMakeLists.txt -- 24 enforced source(s) resolved …
exit=0
```

**The `# PY32_EXCLUDED:` idiom is the alternative this phase rejects, but note its format** —
`# PY32_EXCLUDED: <path> -- <reason>`, mandatory per `check_cmake_manifest.py`'s module
docstring (read it in full). Do **not** add one for the seam.

**Line 2 — the compile definition.** Current state (lines 108-127) — note the comment block
above the call, which is the pattern D-07's addition should extend rather than duplicate:

```cmake
#
# The pin-map "configured for a real build" macro (MERGE-04, D-14) is
# supplied HERE, not by the board header:
# include/boards/py32f071_rurp_shield.h now only TESTS it via the
# dependency-free include/boards/py32f071_pinmap_guard.h fragment, so a
# build that forgets to supply it now fails at the preprocessor with a
# named error instead of silently compiling an unconfigured, provisional
# pin map. This target is the only one that compiles the py32 board
# header, so this is the only place it is supplied.
target_compile_definitions(
    ${TARGET_NAME}
    PRIVATE
        USE_HAL_DRIVER
        PY32F071xB
        RURP_PLATFORM_PY32F071=1
        RURP_BOARD_NAME="py32f071"
        MONITOR_SPEED=250000
        DATA_BUFFER_SIZE=512
        RURP_PY32F071_PINMAP_CONFIGURED=1
)
```

`RURP_HAS_VPP_DAC=0` goes as the **eighth entry, directly after
`RURP_PY32F071_PINMAP_CONFIGURED=1`** (C-14's recommendation) — which keeps the two
"the build supplies what the header tests" macros adjacent and lets one extended comment cover
both. **Extend the existing comment block; do not write a second one.** The comment should
carry D-05's permanence statement and C-17's note that PR #47 chose `1` and this branch
deliberately chooses `0` because no hardware exists.

Note `DEV_TOOLS` is **absent** from this block after Phase 124's D-02 conversion — it lives as
a shared header default and is named only in the comment. Do not read its absence as an
omission to fix.

---

### `.planning/phases/125-vpp-control-seam/125-NONREGRESSION.md` (evidence artifact, meta repo)

**Analog:** `.planning/phases/124-firmware-integration-merge/124-NONREGRESSION.md` (and
`123-NONREGRESSION.md`). Reuse the structure verbatim.

**Header block to copy** — named branches with full head SHAs per repo, fork points, and an
explicit **re-execution pledge** stating every row was executed *in this session*, not copied
from any prior plan's SUMMARY:

```markdown
# Phase 124 Non-Regression Sweep — D-16 recorded evidence, closing plan (124-12)

**Written:** 2026-07-31 (Plan 124-12)
**Firmware branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `a145081…`
**Host branch:** `v1.23-py32f071-integration` · **HEAD at this sweep:** `ccbc401…`
...
**Re-execution pledge.** Every row below was executed in **this session** … against
the trees exactly as they now stand — nothing is copied from any of this phase's eleven prior plans'
SUMMARY files. Where a prior SUMMARY made a claim (a gate's exit code, a figure, a PASS line), this
document re-checked it against the live tree independently and says so.
```

**Section skeleton:** §1 "The claim, as precise statements" (numbered claims, each naming its
evidence); §2 "The baseline, as recorded and as re-verified" (the recorded-vs-observed
two-column tables below); then per-criterion sections. Note the analog's honesty pattern: it
names the **one** figure that legitimately changed and explains why the count grows by design.

```markdown
| Env | Flash used (124-10 recorded) | Flash used (observed, this session) | RAM used (recorded) | RAM used (observed) |
|-----|----------:|----------:|---------:|---------:|
| uno | 23954 | **23954** | 1573 | **1573** |
| uno328pb | 24004 | **24004** | 1579 | **1579** |
| leonardo | 26016 | **26016** | 2014 | **2014** |
```

**Phase-125-specific content this artifact must carry:**

- D-15's flash **and RAM** figures for all three AVR targets, **recorded, not gated** — the
  planner must not add a comparator leg of its own. The strict comparator is already armed
  (`check_size_baseline.py`'s `compare_avr()`, exact equality on four fields, proven strict in
  C-8 by a +2 B perturbation → `FAIL … exit=1`, and never-vacuous).
- **The zero-delta non-vacuity pair** (Pitfall 2 — a `build_src_filter` typo produces the same
  0 B): the `.o` exists in each build dir (`.pio/build/{uno,uno328pb,leonardo}/src/rurp_vpp.cpp.o`),
  **and** `avr-nm <elf> | grep -cE 'rurp_vpp_control_mode|rurp_set_vpp_target_mv|rurp_disable_vpp_control'`
  → 0 while five unrelated pre-existing `vpp` symbols remain, proving the grep is not matching
  nothing by accident. Also record that `-flto` (not just `--gc-sections`) contributes: the
  `.o` is an LTO slim object.
- **Measurement hygiene:** `rm -rf .pio/build/<env>` then a **single** `pio run` per env with
  an extended timeout. A default 2-minute Bash timeout truncates the toolchain build
  mid-compile and silently contaminates the figure (`124-04-SUMMARY.md`'s recorded trap).
- Criterion 3's pin: **blob-SHA re-hash is primary**; `git status --porcelain` is
  **post-commit corroboration only** and every porcelain row must **name the firmware repo
  explicitly** — `firestarter_app`'s porcelain is legitimately non-empty right now (C-15).
  Never `git diff --stat <path> | grep -v <file>`: the `N file changed` trailer survives the
  grep, which is `124-VERIFICATION.md`'s live informational finding.
- D-13's ARM CI **run URL + head SHA**, obtained via the operator-gated push + dispatch.
- The verbatim local `pytest` output, and a plain statement that **no CI leg on this branch
  executes the new harness** (C-7).
- **The claim scan must be invoked explicitly** (C-16): `check_permitted_claims.py`'s
  `_DEFAULT_TARGETS` are four **Phase-130** files, so run
  `FIRESTARTER_CLAIMSCAN_TARGETS=<…/125-NONREGRESSION.md> python3 scripts/check_permitted_claims.py`
  as a real row, and include the canonical caveat **"no PY32F071 hardware exists"** verbatim
  in the document.

---

## Shared Patterns

### Pattern: the build system declares; the header only tests

**Source:** `include/boards/py32f071_pinmap_guard.h:41-43` + `platform/py32f071/CMakeLists.txt:108-127`
**Apply to:** `include/rurp_vpp.h`, `platform/py32f071/CMakeLists.txt`

Phase 124 found `#define …CONFIGURED 1` about thirty lines above the `#if !CONFIGURED →
#error` that tested it — a guard that could not fire under any build configuration. The fix
hoisted the test away from the definition and moved the definition into CMake. D-06/D-07 apply
that lesson before the fact. Corollary for Phase 125: `RURP_HAS_VPP_DAC` is **never** defined
in `include/boards/py32f071_rurp_shield.h`; the CMake `target_compile_definitions` is its only
non-AVR source.

### Pattern: self-contained path resolution, stdlib + pytest only, no conftest

**Source:** `tests/test_pinmap_guard_fires.py:26-28, 56-62`; `tests/test_golden_trace_identity.py:64-76`
**Apply to:** both new pytest modules

There is **no `conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg` or `tox.ini` anywhere
in the firmware repo** — a recorded house-rule decision, not an omission. Every module derives
`_HERE = Path(__file__).resolve().parent` / `_REPO_ROOT = _HERE.parent` at module scope, and
imports only stdlib + pytest. **Do not add a `conftest.py`.**

### Pattern: fail-closed on a missing tool, self-enforced

**Source:** `tests/test_pinmap_guard_fires.py:65-84` (compiler) and `:215-234` (self-scan);
`tests/test_golden_trace_identity.py` coverage-6 (`git`)
**Apply to:** both new pytest modules

A missing `g++` or `git` must **FAIL**, never skip — an absence-proxy skip is the exact
BASE-02/BASE-03 failure class Phase 123 removed. The self-scan leg is what keeps the contract
from being edited away, and the string-concatenation trick is what keeps the leg from tripping
on itself.

### Pattern: list-argv subprocess, never a shell; assert on all three fields

**Source:** `tests/test_pinmap_guard_fires.py:99-108`; `tests/test_check_cmake_manifest.py:69-88`
**Apply to:** both new pytest modules

Always `subprocess.run([...], capture_output=True, text=True)`, never `shell=True`, never a
composed string. When an env seam matters, build the **child's** env explicitly — the
`test_check_cmake_manifest.py` idiom, which matters here because
`FIRESTARTER_SIZE_BASELINE` / `FIRESTARTER_MANIFEST_ROOT` / `FIRESTARTER_CLAIMSCAN_TARGETS`
are all read **once at import**, so an in-process `monkeypatch.setenv` is ineffective:

```python
def _run_checker(manifest_root=None):
    """Invoke check_cmake_manifest.py as a real subprocess (list argv, never
    shell=True). `manifest_root`, when not None, sets
    FIRESTARTER_MANIFEST_ROOT in the CHILD's environment to that exact path ..."""
    env = {**os.environ}
    if manifest_root is not None:
        env["FIRESTARTER_MANIFEST_ROOT"] = str(manifest_root)
    else:
        env.pop("FIRESTARTER_MANIFEST_ROOT", None)
    return subprocess.run(
        [sys.executable, str(_CHECKER)],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
```

### Pattern: numbered `Coverage:` docstring, one entry per test

**Source:** `tests/test_pinmap_guard_fires.py:31-47`; `tests/test_golden_trace_identity.py:25-50`
**Apply to:** both new pytest modules

Module docstring: MIT banner → `Phase NNN Plan NN — <what>` → `Requirements:` /
`Decisions covered:` → a defect-class paragraph → the conftest note → a numbered `Coverage:`
list naming each test function and the mechanical outcome it asserts. Each test function then
repeats its coverage number in its own docstring (`"""Coverage 3 -- …"""`).

### Pattern: the MIT banner on every C/C++ source

**Source:** `src/proms/not_implemented.cpp:1-6`
**Apply to:** `src/rurp_vpp.cpp` (and the pytest modules, in docstring form)

```c
/*
 * Project Name: Firestarter
 * Copyright (c) 2024 Henrik Olsson
 *
 * Permission is hereby granted under MIT license.
 */
```

Uniform across `src/`. Copy byte-for-byte. Note `include/boards/py32f071_pinmap_guard.h` opens
with `#pragma once` and no banner — headers in that family skip it; follow the analog you are
copying.

---

## No Analog Found

None. Every file in this phase's set has a real in-tree analog, and RESEARCH's "Don't
Hand-Roll" table confirms **every gate this phase needs already exists and is already armed**.

The residual risk is not in the new files — it is in the **interaction** between a new
preprocessor `#error` and the 46 translation units that include `rurp_shield.h`, 14 of them
native `host_stubs.cpp`. That is what Option A on C-1 avoids by not adding the `#include`, and
what `pio test -e native` catches in 92 seconds if anyone re-adds it.

---

## Metadata

**Analog search scope (firmware repo `/workspaces/firestarter`):** `tests/` (10 modules),
`include/`, `include/boards/`, `src/`, `src/proms/`, `platform/py32f071/`; plus the meta repo's
`.planning/phases/12{3,4}-*/`
**Files read in full:** `tests/test_pinmap_guard_fires.py` (235 lines),
`include/boards/py32f071_pinmap_guard.h` (43), `src/proms/not_implemented.cpp` (19)
**Files read in targeted ranges:** `platform/py32f071/CMakeLists.txt` (30-80, 108-130),
`include/boards/py32f071_rurp_shield.h` (33-81), `tests/test_checker_convention.py` (110-130),
`tests/test_golden_trace_identity.py` (1-80), `tests/test_check_cmake_manifest.py` (69-95),
`124-NONREGRESSION.md` (1-60)
**Pattern extraction date:** 2026-07-31
