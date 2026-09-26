# Phase 124: Firmware Integration Merge - Pattern Map

**Mapped:** 2026-07-31
**Files analyzed:** 10 new/modified artifacts
**Analogs found:** 10 / 10 (8 exact, 2 role-match)

All paths below are **absolute-from-sub-repo-root**. `firestarter/` = `/workspaces/firestarter`,
`firestarter_app/` = `/workspaces/firestarter_app`, meta = `/workspaces/.planning/`.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match |
|---|---|---|---|---|
| `firestarter/scripts/check_landing_range.py` *(name at discretion)* — MERGE-01/D-06 | checker script | batch / git-range scan | `firestarter/scripts/check_orphan_provisional.py` | exact |
| `firestarter/tests/test_check_landing_range.py` | test (pytest, subprocess) | request-response | `firestarter/tests/test_check_orphan_provisional.py` | exact |
| `firestarter/test/native/avr/test_pinmap_provisional/*.cpp` — MERGE-04 refusal suite | native Unity suite | request-response (dispatch) | `firestarter/test/native/avr/test_cmd_admission/` (+ `test_dispatch/test_configure_memory.cpp`) | exact |
| `firestarter/test/native/avr/test_pinmap_provisional/host_stubs.cpp` | test stub TU | link-time | `firestarter/test/native/avr/test_cmd_admission/host_stubs.cpp` | exact |
| `firestarter/tests/test_pinmap_error_fires.py` — MERGE-04/D-14 `g++ -E` fire-proof | test (pytest + real compiler) | file-I/O + subprocess | `firestarter/tests/test_check_build_warnings.py` (`_resolve_compiler`/`_compile_fixture`) | exact |
| `firestarter/tests/test_check_cmake_manifest.py` — W-3 rewrite | test (expiring) | request-response | itself + `test_check_orphan_provisional.py` coverage-4 idiom | exact |
| `firestarter/tests/test_check_orphan_provisional.py` — W-3 rewrite | test (expiring) | request-response | same | exact |
| `firestarter/include/firestarter.h`, `include/dev_tools.h`, `src/firestarter.cpp`, `src/dev_tools.cpp` — D-02 | shared header/config | compile-time | `firestarter/include/firestarter.h:16-18` (`DATA_BUFFER_SIZE` default) | exact |
| `firestarter/src/proms/memory.cpp` (`configure_memory`) — MERGE-04 refusal | dispatch/service | request-response | `firestarter/src/proms/not_implemented.cpp` | exact |
| golden-trace per-array identity check — MERGE-06 | test/evidence | transform | `firestarter/test/native/avr/_shared/sdp_expected.h:60-100` + `RED-BASELINE.md` blob loop | role-match |
| `firestarter/platform/py32f071/CMakeLists.txt` edits (lands with merge) | config | compile-time | `firestarter/tests/fixtures/clean_cmake_manifest_excluded/platform/py32f071/CMakeLists.txt` | exact |
| `.planning/phases/124-.../124-NONREGRESSION.md` | evidence doc | batch | `.planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md` | exact |

---

## Pattern Assignments

### 1. `firestarter/scripts/check_<name>.py` — the Criterion-1 range check (MERGE-01 / D-06)

**Analog:** `firestarter/scripts/check_orphan_provisional.py` (385 lines — read it whole once).
Secondary: `firestarter/scripts/check_cmake_manifest.py` (same idiom, different subject).

**Shebang + docstring shape** — the docstring is the *contract*, and it is long by house rule.
Mandatory sections, in this order (`check_orphan_provisional.py:2-154`):
`<path> -- <REQ-ID> <one-line purpose> (Phase N Plan NN, D-xx)` → why the defect class matters →
what is confirmed present/absent today → arming (if any) → **rejected alternative readings, recorded
deliberately** → scan scope → never-vacuous guard → encoding/binary safety → Output → **Non-claim** →
Exit codes → **Anti-hollow contract** naming the paired pytest → Usage.

**Env seam** (`check_orphan_provisional.py:160-183`) — copy verbatim, renaming the var:
```python
REPO_ROOT = Path(__file__).resolve().parent.parent

# Single-target env seam WITH a default: lets the paired pytest point this
# checker at a fixture tree without editing the real repo. Read ONCE at module
# import time -- an in-process monkeypatch.setenv would be silently ineffective
# (123-RESEARCH.md Correction C-15), so the paired pytest invokes this script as
# a real subprocess with the seam set in the CHILD environment.
FIRESTARTER_PROVISIONAL_ROOT = os.environ.get(
    "FIRESTARTER_PROVISIONAL_ROOT", str(REPO_ROOT)
)
_ROOT = Path(FIRESTARTER_PROVISIONAL_ROOT)
```
For the range check the seam should be **the repo path plus the fork point** (e.g.
`FIRESTARTER_RANGE_ROOT` + `FIRESTARTER_RANGE_FORK`), because the fixture must be a *real git repo*,
not a directory tree. Read both at import time.

**Three-way exit taxonomy + `ScanError`** (`check_orphan_provisional.py:215-222, 320-384`):
```python
class ScanError(Exception):
    """...Caught only at the entry point and converted to exit 2 -- never exit 0
    and never exit 1."""

def main():
    try:
        ...
    except ScanError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if violations:
        print(f"FAIL: {len(violations)} violation(s):")
        for v in violations[:20]:
            print(f"  {v}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more")
        return 1
    print(f"PASS: {', '.join(pass_lines)}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except ScanError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
```
0 = pass, 1 = violation, 2 = tool/config error. Never a silent skip.

**Never-vacuous guard** (`check_orphan_provisional.py:335-345`) — the required analog for the range
check: *"scanned 0 commits"* must be **exit 1**, not a pass. Copy the message shape:
```python
if not definitions:
    print("FAIL: armed ... but ZERO ... were found ... -- either the flag was "
          "renamed out of the pattern, or SCAN_DIRS/SCAN_SUFFIXES no longer "
          "cover where it lives. An armed tree with no provisional flag at all "
          "must never look like a clean pass (never-vacuous guard).")
    return 1
```
Also copy the **PASS line names what it found** rule (`:375`) — `PASS: 15 commits scanned, 0 violations`
so a run that scanned nothing cannot visually resemble a clean run.

**The range logic itself** is prototyped in `124-RESEARCH.md` §"D-06's Criterion-1 range check"
(`git rev-list <fork>..HEAD`; per commit, `git cat-file -e "$c:include/rurp_platform_compat.h"` then
`git rev-parse -q --verify "$c:platform/py32f071"`). Use `subprocess.run` **list argv, never
`shell=True`** — the same rule the paired tests enforce.

**Convention gate this new script must satisfy** (`firestarter/tests/test_checker_convention.py:121-122,
161-296`): `FLOOR = 4` and `FIXTURE_FLOOR = 9` are `>=` assertions so **adding** a checker is safe, but
the meta-test then requires, for every `scripts/check_*.py`:
- a paired `tests/test_check_<same_stem>.py` (test 2),
- a `tests/fixtures/planted_*` fixture whose name relates to the checker (test 3),
- the paired module must **name its checker** (test 5) and must contain a literal
  `returncode != 0` assertion (test 6).
Planner: budget a `planted_*` fixture for the new checker or `test_every_checker_has_planted_fixture`
goes red. **Also bump `FLOOR = 4` → 5** if a fifth checker lands (it is a `>=`, so optional, but the
docstring records the shipped count — keep them in sync).

---

### 2. `firestarter/tests/test_check_<name>.py` — the paired pytest

**Analog:** `firestarter/tests/test_check_orphan_provisional.py` (285 lines).

**Module docstring** (lines 1-52) — MIT header, then
`Phase N Plan NN — the BASE-08 anti-hollow pairing for scripts/<checker>.py`,
`Requirements: …`, `Decisions covered: …`, the anti-hollow paragraph, a numbered **Coverage:** list, and
this house-rule note verbatim:
```
Self-contained path resolution below -- NOT in conftest.py (firestarter/
tests/ has no conftest.py anywhere in the repo; a recorded house-rule
pattern decision per test_update_version.py's own comment, not an
omission). Stdlib and pytest only.
```

**Path constants + runner** (`test_check_orphan_provisional.py:61-89`):
```python
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_CHECKER = _REPO_ROOT / "scripts" / "check_orphan_provisional.py"
_FIXTURES = _HERE / "fixtures"

def _run_checker(provisional_root=None):
    env = {**os.environ}
    if provisional_root is not None:
        env["FIRESTARTER_PROVISIONAL_ROOT"] = str(provisional_root)
    else:
        env.pop("FIRESTARTER_PROVISIONAL_ROOT", None)
    return subprocess.run(
        [sys.executable, str(_CHECKER)],
        cwd=str(_REPO_ROOT), capture_output=True, text=True, env=env,
    )
```
Note the **`env.pop` on the None branch** — required so the "seam genuinely absent" path is exercised.

**Mutate-a-clean-fixture-in-tmp_path idiom** (`:169-192`) — the shape for proving the *new* checker
discriminates the squash (0 violations) from a true merge (5):
```python
def test_undef_is_not_a_consumer(tmp_path):
    dest = tmp_path / "tree"
    shutil.copytree(_CLEAN_CONSUMED, dest)
    consumer = dest / "src" / "fixture_consumer.cpp"
    assert consumer.is_file(), "fixture setup: consumer file must exist"
    consumer.write_text(...)
    result = _run_checker(provisional_root=dest)
    assert result.returncode != 0, (...)
```
For a git-range checker the equivalent is: build a throwaway repo in `tmp_path` with `git init` +
two shapes (squashed / replayed) and assert 0 vs N. Keep the "fixture setup:" assert prefix.

**Exactly-N-violations, plus a named negative control** (`:129-150`) — do not merely assert non-zero:
```python
assert "FAIL: 1 " in result.stdout, (...)
assert "RURP_FIXTURE_ORPHAN_PROVISIONAL" in result.stdout, (...)
assert "RURP_FIXTURE_CONSUMED_PROVISIONAL" not in result.stdout, (
    "the consumed control macro must NEVER appear in the violation bucket...")
```
Every assertion carries an f-string message reproducing `stdout` **and** `stderr`.

**Fixture tree layout** (`firestarter/tests/fixtures/clean_orphan_provisional_consumed/`):
```
README.md
include/fixture_provisional.h
src/fixture_consumer.cpp
platform/py32f071/CMakeLists.txt      <- the arming key, present in every ARMED fixture
```
`clean_unarmed_tree/` is `README.md` + `src/placeholder.cpp` and **no `platform/`** — it is shared
across checkers; reuse it, do not clone it.

---

### 3. MERGE-04 native Unity suite (`test/native/avr/test_pinmap_provisional/`)

**Analog for the suite:** `firestarter/test/native/avr/test_cmd_admission/test_cmd_admission.cpp`
(a two-env truth-table suite over `is_memory_cmd` — closest in intent).
**Analog for driving `configure_memory`:** `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp`.

**Handle-builder + assertion idiom** (`test_configure_memory.cpp:53-77`):
```cpp
static firestarter_handle_t make_handle(uint32_t protocol, uint8_t mem_type, uint8_t cmd) {
    (void)mem_type;
    firestarter_handle_t h = {};
    h.protocol = protocol;
    h.cmd = cmd;
    h.response_code = RESPONSE_CODE_OK;
    return h;
}

void test_protocol_0x06_dispatches_nor_unlock(void) {
    firestarter_handle_t h = make_handle(0x06, 0, CMD_READ);
    configure_memory(&h);
    TEST_ASSERT_NOT_EQUAL(RESPONSE_CODE_ERROR, h.response_code);
}
```
The refusal suite inverts this: `TEST_ASSERT_EQUAL(RESPONSE_CODE_ERROR, h.response_code)` **and**
`TEST_ASSERT_NULL(h.firestarter_operation_main)` (plus `_init`/`_end`) for each of D-12's eight commands.

**`setUp` / `tearDown` + ArduinoFake Serial stubs** — copy verbatim from
`test_configure_memory.cpp:37-50`; without them any `LOG_ERROR_ID_*` on the refusal path aborts:
```cpp
void setUp(void) {
    ArduinoFakeReset();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t))).AlwaysReturn(1);
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}
void tearDown(void) {}
```
`test_cmd_admission.cpp:38-45` carries the "**LOAD-BEARING, do not remove as unused**" comment on those
stubs — reproduce that comment.

**Includes** (`test_configure_memory.cpp:25-35`):
```cpp
#include <Arduino.h>
#include <ArduinoFake.h>
#include <unity.h>
#include <stdio.h>
extern "C" {
#include "memory.h"
}
#include "firestarter.h"
using namespace fakeit;
```

**`main`** (`test_configure_memory.cpp:393-427`): `UNITY_BEGIN();` … one `RUN_TEST(...)` per case,
grouped under `/* comment naming the requirement/decision */`, then `return UNITY_END();`.

**`host_stubs.cpp`** — `test_cmd_admission/host_stubs.cpp` is a **pure pass-through**; copy it whole and
change only the docstring's suite name:
```cpp
#include <stdint.h>
#include <stddef.h>
#include <string.h>
extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}
#include "../_shared/host_stubs_common.inc"
```
Also copy the sibling `avr/pgmspace.h` shim directory (every suite dir has one).

**`platformio.ini` enrolment** — **four** lines per suite (both envs), per `firestarter/CLAUDE.md`
§"Reuse pattern for future native tests": a `test_filter` entry `native/avr/<dirname>` and a
`-I test/native/avr/<dirname>` build flag, in `[env:native]` **and** `[env:native_nodevtools]`.
`[env:native]`'s `test_filter` is the positive allowlist at `platformio.ini:102-119` (17 entries today);
`build_flags` `-I` list starts at line 120.

> **Pitfall 5 (RESEARCH):** adding this suite to either pinned env moves 17→18 suites and breaks
> MERGE-06's `141 cases / 17 suites` assertion. Use a **third env** (`[env:native_pinmap_provisional]`,
> `build_flags = ${env:native.build_flags} -D RURP_PINMAP_PROVISIONAL=1`, its own `test_filter` naming
> only the new suite) and do **not** feed that env name to `check_build_warnings.py` (unknown env = exit 2).

---

### 4. The refusal itself, in `src/proms/memory.cpp`

**Analog:** `firestarter/src/proms/not_implemented.cpp` — the whole file is the template:
```cpp
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
**Insertion site** — `firestarter/src/proms/memory.cpp:42-46`, which already NULLs the three pointers
immediately after `LOG_DEBUG_ID_SUB(DBG_CONFIGURING_MEMORY);`:
```cpp
void configure_memory(firestarter_handle_t* handle) {
    LOG_DEBUG_ID_SUB(DBG_CONFIGURING_MEMORY);
    handle->firestarter_operation_init = NULL;
    handle->firestarter_operation_main = NULL;
    handle->firestarter_operation_end = NULL;
    // <-- the refusal guard goes HERE, before the `switch (handle->cmd)` at :47
```
Per D-13 the payload is `LOG_ERROR_ID_U8(MSG_ERR_NOT_SUPPORTED, (uint8_t)handle->cmd)` (0xA5,
`include/messages.h:82`) — **not** the protocol ordinal `not_implemented.cpp` uses.

**The predicate seam** reuses `is_memory_cmd` at `firestarter/include/firestarter.h:110-124`, whose
comment block (`:95-108`) states the two hard constraints the planner must not break:
*no preprocessor conditional of any kind inside the body*, and *`static inline`, in this header* —
because `[env:native]`'s `build_src_filter` excludes `src/firestarter.cpp`. That comment is itself the
precedent for a new `static inline bool rurp_pinmap_refuses(uint8_t cmd)` header predicate.
`firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` enforces the no-conditional half.

**`check_orphan_provisional.py` consumer shape** (C-12): both `RURP_PY32F071_PINMAP_PROVISIONAL` and any
new neutral flag need a consumer inside `include/ src/ platform/ test/` — `tests/` is **not** scanned
(`check_orphan_provisional.py:189`). RESEARCH prescribes the bridging block in the board header:
```c
#if RURP_PY32F071_PINMAP_PROVISIONAL
#define RURP_PINMAP_PROVISIONAL 1
#endif
```

---

### 5. `firestarter/tests/test_<pinmap>_error_fires.py` — the `g++ -E` fire-proof (D-14)

**Analog:** `firestarter/tests/test_check_build_warnings.py:128-167` — the only in-tree pytest that
shells out to a real compiler.

**Fail-closed compiler resolution** (`:128-145`) — copy verbatim, including the reasoning comment;
**never** `pytest.skip`:
```python
def _resolve_compiler():
    """Resolve the host C++ compiler, fail-closed.

    Deliberately never bypassed via any decorator or runtime call that would
    mark this outcome as skipped, anywhere in this module: doing so would
    recreate the exact BASE-02/BASE-03 absence-proxy failure class inside
    the very phase that removes it. ...
    """
    compiler = shutil.which(os.environ.get("CXX", "g++"))
    assert compiler is not None, (
        "host C++ compiler not found on PATH (checked $CXX, falling back to "
        "'g++'). This must FAIL the suite, never be silently skipped -- ...")
    return compiler
```

**Real-compiler invocation** (`:159-167`) — adapt `-fsyntax-only` to `-E … -o /dev/null` and capture
**both** streams plus `returncode` (RESEARCH proved three discriminating arms: unset → exit 1,
`-D…=1` → exit 0, `-D…=0` → exit 1):
```python
def _compile_fixture(compiler, fixture_name):
    result = subprocess.run(
        [compiler, "-fsyntax-only", str(_FIXTURES / fixture_name)],
        capture_output=True, text=True,
    )
    return result.stderr
```

**Derive-the-literal-from-the-fixture rule** (`:148-156`) — do not hardcode the `#error` text twice;
read it out of the fragment header at test time:
```python
def _fixture_macro_name():
    text = (_FIXTURES / "planted_build_warnings_macro_redef.cpp").read_text()
    m = re.search(r"#define\s+(\S+)", text)
    assert m, f"expected at least one #define directive in the fixture.\nGot:\n{text}"
    return m.group(1)
```

**Path constants** (`:114-118`) are the same `_HERE/_REPO_ROOT/_FIXTURES` triple as §2.
This module is the *one* place a `sys.path.insert(...)` import of the checker is sanctioned
(`:120-125`) and only for regex-level assertions — every exit-code test still uses a subprocess.

---

### 6. W-3 — rewriting the two expiring Phase-123 pytests

**Files:** `firestarter/tests/test_check_cmake_manifest.py`,
`firestarter/tests/test_check_orphan_provisional.py`.

**Exactly one test per file changes.** Both are named
`test_unarmed_on_the_real_tree_with_no_seam_override`:

| File | Lines | Assertions that must change |
|---|---|---|
| `test_check_cmake_manifest.py` | **87-103** | `result.stdout.startswith("UNARMED:")` (`:97`); the docstring's *"must stay true until Phase 124 lands the port"* (`:88-91`); `"platform/py32f071" in result.stdout` **survives** (a PASS line still names it — verify) |
| `test_check_orphan_provisional.py` | **92-111** | `result.stdout.startswith("UNARMED:")` (`:102`); `"124" in result.stdout` (`:109`) — the armed PASS line does **not** name Phase 124, so this assertion must go; docstring `:93-96` |

Everything else in both files (the seam-fixture tests, the `tmp_path` mutation tests, the exit-2 test)
stays. `test_unarmed_on_clean_unarmed_tree_fixture` in both files **must not change** — it points the
seam at `clean_unarmed_tree/`, which never arms.

**Armed-state analog to invert toward** — `test_check_orphan_provisional.py:153-166`:
```python
def test_consumed_control_passes():
    result = _run_checker(provisional_root=_CLEAN_CONSUMED)
    assert result.returncode == 0, (...)
    assert "PASS:" in result.stdout, f"expected PASS:. Got:\n{result.stdout}"
    assert "RURP_FIXTURE_CONSUMED_PROVISIONAL" in result.stdout, (...)
```
and `test_check_cmake_manifest.py:179-193` (`test_reasoned_omission_passes_and_is_named`), which asserts
`"PASS:"` plus the allow-listed path is **named on the PASS line**. Rename the rewritten tests to
something like `test_armed_and_passing_on_the_real_tree`, and update each module docstring's numbered
**Coverage:** list item 1 to match.

**Knock-on:** `124-NONREGRESSION.md` row F1's expected count must be re-recorded (123 recorded
**48 passed, 0 skipped**; the new checker + its pairing add cases).

---

### 7. D-02 `#if DEV_TOOLS` conversion

**Analog / required placement B** — `firestarter/include/firestarter.h:16-18`, five lines above the
block being converted:
```c
#ifndef DATA_BUFFER_SIZE
#define DATA_BUFFER_SIZE 512
#endif
```
Put the new block **beside it, inside the `#ifndef __FIRESTARTER_H__` guard** (which opens at `:8`):
```c
#ifndef DEV_TOOLS
#define DEV_TOOLS 0
#endif
```
Placement above the header guard passes the host parity test only by arithmetic cancellation (C-18).

**The six conversion sites** (RESEARCH D-02 table): `include/firestarter.h:42`,
`include/dev_tools.h:11`, `src/dev_tools.cpp:8`, `src/firestarter.cpp:21, 97, 271`.
`firestarter.h:42` reads today:
```c
#ifdef DEV_TOOLS
#define CMD_DEV_ADDRESS 7
#define CMD_DEV_REGISTER 8
#endif
```

**Line-anchored substitution — never a global `sed`** (Pitfall 3; comment prose at
`firestarter.h:51,70,73` and `firestarter.cpp:79` names the old mechanism deliberately):
```python
re.compile(r'^#ifdef DEV_TOOLS$', re.MULTILINE).sub('#if DEV_TOOLS', text)
```
Verify with `grep -c '#ifdef DEV_TOOLS'`: `firestarter.h` 4 → 3, `firestarter.cpp` 4 → 1.
`platformio.ini` needs **no** edit (`:26` `-D DEV_TOOLS` ⇒ `=1`).

---

### 8. Golden-trace per-array byte identity (MERGE-06)

**File:** `firestarter/test/native/avr/_shared/sdp_expected.h` (blob
`dd1ba1cce60d8aa8934e8c067ed82ad85cfd3b83`, unchanged across the merge).
**Nine arrays** at lines 144, 195, 227, 253, 286, 337, 356, 372, 405 — grep handle:
```bash
grep -n "static const sdp_strobe_t" test/native/avr/_shared/sdp_expected.h
```
**Existing consumers:** `test/native/avr/test_sdp_harness/test_sdp_harness.cpp:61` (`#include
"../_shared/sdp_expected.h"`) and `test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`.
No in-tree test compares the *file* against a recorded identity — that half is new.

**Blob-loop analog** — `test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:521` and `:837`:
```bash
for p in test/native/avr/_shared/sdp_expected.h test/native/avr/_shared/host_stubs_common.inc \
         test/native/avr/_shared/sdp_bus_config.h; do
  echo "$p base=$(git rev-parse f8d10a5:$p) head=$(git rev-parse HEAD:$p)"
done
```
That file also records the results as a `| path | base | head | unchanged? |` table — reuse it.

**In-C++ comparator discipline** — `sdp_expected.h:60-100`, if the per-array inventory is asserted
natively rather than by script. `sdp_first_divergence` / `sdp_assert_stream_equals` are positional,
never counting, and name the first diverging index:
```cpp
static void sdp_assert_stream_equals(const sdp_strobe_t* expected, int expected_len, const char* ctx) {
    TEST_ASSERT_EQUAL_MESSAGE(0, strobe_overflowed(), ctx);
    TEST_ASSERT_EQUAL_MESSAGE(expected_len, strobe_count(), ctx);
    int div = sdp_first_divergence(expected, expected_len);
    ...
}
```

---

### 9. `platform/py32f071/CMakeLists.txt` edits

**Analog (a working, gate-passing manifest already in-tree):**
`firestarter/tests/fixtures/clean_cmake_manifest_excluded/platform/py32f071/CMakeLists.txt` — read it
for the exact `set()` block spelling and a correctly-formatted `PY32_EXCLUDED` line that the gate
accepts today. Its sibling fixture
`planted_cmake_manifest_excluded_no_reason/` is the negative control (path, no `-- reason`).

**The exact required comment format, quoted from `firestarter/scripts/check_cmake_manifest.py`'s module
docstring (lines ~47-70):**
```
    # PY32_EXCLUDED: <path> -- <reason>
```
> "The reason segment is MANDATORY -- an entry with a path but no stated reason is itself a
> violation, because an allow-list without required reasons degrades into a silencer."

and the five lines Phase 124 is expected to write **verbatim**:
```
    src/boards/uno_rurp_shield.cpp       -- AVR board impl, no ARM analogue
    src/boards/leonardo_rurp_shield.cpp  -- AVR board impl, no ARM analogue
    src/boards/rurp_common.cpp           -- AVR-specific common
    src/dev_tools.cpp                    -- DEV_TOOLS deliberately off on ARM (MERGE-08)
    src/rurp_config_utils.cpp            -- Phase 126 per-platform config backend
                                            split; THIS EXCLUSION WILL NEED
                                            REVISITING in Phase 126, it is not
                                            a permanent exclusion.
```
D-15 amends only the `src/dev_tools.cpp` reason (→ "no ARM dev-tools TU; `DEV_TOOLS` resolves to 0 by
the shared default"). Also from the same docstring: `ENFORCED_LISTS = {"FIRESTARTER_COMMON_SOURCES",
"PY32_PLATFORM_SOURCES"}`; `PY32_SDK_SOURCES` is **structurally exempt** (FetchContent), and an
unrecognised `set()` list name is **exit 2**.

**The rename edit:** lines **40-41** (`flash_type_3.cpp` → `flash_nor_unlock.cpp`,
`flash_type_4.cpp` → `flash_5v_page.cpp`). `DATA_BUFFER_SIZE=512` is line **107**;
`target_compile_definitions` is lines **99-108** (where D-02's ARM-side `DEV_TOOLS` comment goes).
Expect **9** violations on the first armed run, not 2 (W-4).

---

### 10. `124-NONREGRESSION.md`

**Analog:** `.planning/phases/123-non-regression-baselines-gate-hardening/123-NONREGRESSION.md`
(343 lines). Section structure to reproduce:

| § | Title | Content |
|---|---|---|
| header | — | Written date; **firmware branch + HEAD SHA**; host branch + HEAD SHA; recorded fork points; meta branch + HEAD |
| — | **Re-execution pledge** (`:11`) | *"Every row below was executed in this session, against the trees as they now stand"* — D-16 forbids copying from prior SUMMARY files |
| 1 | The claim, as precise statements | |
| 2 | The baseline, as recorded and as re-verified | + a ROADMAP cross-check result line |
| 3 | **The gate table — command, expected, observed** | `| # | Command | Expected | Observed |`, IDs `F1…F9` (firmware) / `H1…H13` (host) / meta; observed cell **bolds the number** and quotes the tool's own PASS line |
| 4 | What is UNARMED today and what arms it | 124 inverts this to "what armed, and what it fired on" |
| 5 | Known and explained conditions — never silent | |
| 6 | The phase-wide no-code-moves proof | cumulative range diff; never a path-scoped `git diff` |
| 7 | The validation ceiling | forbidden claim **cited by location** (`.planning/REQUIREMENTS.md:14`), never reproduced verbatim |
| 8 | **Deliberately not taken** | see below |
| — | Sweep Summary | `| Gate | Result |` |

**Row shape, verbatim from §3 (`123-NONREGRESSION.md:88-104`):**
```
| F1 | `python3 -m pytest tests/ -q` | 48 passed, 0 skipped | **48 passed**, 0 skipped |
| F2 | `pio test -e native` | 141/141, 17 suites, all PASSED | **141/141 succeeded**, 17 suites, all PASSED |
| F7a | `check_build_warnings.py --log native=...` | exit 0, total==360 | **exit 0** — `PASS: native: total warnings=360 (== watermark 360)` |
| F8 | `check_cmake_manifest.py` | `UNARMED:`, exit 0 | **exit 0** — see §4 for verbatim line |
```

**"Deliberately not taken" bullet shape (`:302-316`)** — the last bullet is the load-bearing one and
must be re-asserted (or honestly negated, given W-1/W-2) in 124:
```
- **No baseline, watermark, floor, or allow-list was adjusted to make a row green.** Every row in §3
  passed as originally specified against the tree as found; no row required lowering a bar.
- **No push, no `gh` invocation, no release, no tag, no gitlink bump.**
```
Phase 124 *does* push and dispatch (D-08/D-09) and *may* re-baseline (W-1) — so these two bullets must
be rewritten as explicit, reasoned exceptions rather than silently dropped.

---

## Shared Patterns

### Env-seam + real-subprocess (applies to every new checker and its pytest)
**Source:** `firestarter/scripts/check_orphan_provisional.py:160-183`; `firestarter/tests/test_check_orphan_provisional.py:71-89`
Seam read **once at module import**; the pytest sets it in the **child** environment via list-argv
`subprocess.run`. An in-process `monkeypatch.setenv` is silently ineffective (123-RESEARCH C-15).

### Three-way exit taxonomy
**Source:** `check_orphan_provisional.py:131-140` (docstring) + `:320-384` (code)
0 pass / 1 violation / 2 tool-or-config error. Never a silent skip; `ERROR:` goes to **stderr**.

### Never-vacuous guard
**Source:** `check_orphan_provisional.py:96-105, 335-345`; `check_cmake_manifest.py` exit-1 clause
"scanned zero" is a **failure**, not a pass. Every PASS line names what it found.

### Explicit non-claim paragraph
**Source:** `check_orphan_provisional.py:124-129`; `check_cmake_manifest.py` "Non-claim:" paragraph
Every checker docstring states what a green run does **not** prove. Mandatory for the new range check
(*it proves history shape, not that the port builds*).

### Fail-closed, never-skipped external dependency
**Source:** `firestarter/tests/test_check_build_warnings.py:128-145`
Missing `g++`/`git` is a **FAILURE**, never `pytest.skip` — skipping recreates the absence-proxy defect
class Phase 123 removed.

### Assert counts, never "tests pass"
**Source:** `123-NONREGRESSION.md` §3 F2/F3/F6; `check_size_baseline.py --native-log`
141 cases / 17 suites, per-array entry counts, "FAIL: 1 " exact-count string matching.

### Literal-directory-name requirement
**Source:** `firestarter/tests/test_checker_convention.py:280-296` (`test_scope_is_firmware_only`
asserts the resolved scripts path ends `("firestarter", "scripts")`)
Firmware pytest must run from `/workspaces/firestarter`; the host sweep from
`/workspaces/firestarter_app` with a `firestarter` sibling. Never a scratch clone with a different name.

### Cross-repo source-text gates
**Source:** `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py`,
`firestarter_app/tests/test_revision_constants_parity.py:242` (`_find_header_guard_line_indices`),
`:288` (`_extract_defines`), `:592` (the exactly-the-DEV_TOOLS-pair test), `firestarter_app/tests/scan_paths.py`
Any firmware rename or preprocessor restructure must be re-run against these. RESEARCH measured them
green through D-02 (predicate body moved 109-123 → 113-127), but the failure mode is live.

---

## No Analog Found

| Artifact | Role | Data Flow | Reason |
|---|---|---|---|
| A pytest fixture that is a **real git repository** (for the MERGE-01 range check) | test fixture | git | Every existing `tests/fixtures/` entry is a plain directory tree; no in-tree fixture is a git repo. Build it in `tmp_path` with `git init` + scripted commits (RESEARCH §"D-06's Criterion-1 range check" is the source of the shapes to plant), and add a `planted_*` **directory** stub so `test_checker_convention.py::test_every_checker_has_planted_fixture` is satisfied. |
| An AVR-size **policy band** comparator (W-1) | checker function | transform | `check_size_baseline.py:148-165` `compare_avr()` is strict equality only; argv accepts `--baseline/--avr-log/--native-log/--rebuild`. Whichever W-1 option is chosen (policy mode vs re-baseline), the band comparator itself has no in-tree analog — but the `FIRESTARTER_SIZE_BASELINE` seam at `:67-68` and the `PASS:`/`FAIL:` line formats at `:160-162` are reusable verbatim. |
| ARM/CMake build evidence | CI | — | No local ARM toolchain; evidence is a `gh run` URL + SHA (`124-RESEARCH.md` §"Exact commands"). Nothing in-tree to copy. |

---

## Metadata

**Analog search scope:** `firestarter/scripts/`, `firestarter/tests/`, `firestarter/tests/fixtures/`,
`firestarter/test/native/avr/**`, `firestarter/src/proms/`, `firestarter/include/`,
`firestarter/platformio.ini`, `.planning/phases/123-non-regression-baselines-gate-hardening/`.
**Files read in full or in targeted ranges:** 14
**Pattern extraction date:** 2026-07-31
