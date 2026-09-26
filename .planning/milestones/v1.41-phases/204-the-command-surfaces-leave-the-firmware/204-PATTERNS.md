# Phase 204: The command surfaces leave the firmware - Pattern Map

**Mapped:** 2026-09-21
**Files analyzed:** 5 new / 24 modified
**Analogs found:** 5 / 5 new files (all exact or role-match)

This phase is **overwhelmingly modification, not creation**. Only two proof instruments are genuinely
new (plus their scaffolding). Everything else edits files that already exist, where the "pattern to
copy" is the file's own surrounding convention. Both are reflected below.

All analog paths below were checked with `git ls-files` inside the relevant submodule and are
git-TRACKED source. No gitignored mirror paths appear in this document.

---

## File Classification

### New files

| New file | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_fw/tests/test_verify_survival_source_contract.py` (name at planner discretion) | test (source-contract gate) | batch / transform (read source → assert) | `firestarter_fw/tests/test_write_path_source_contract_v131.py` | **exact** — same category, same house shape, explicitly nominated by RESEARCH §Don't Hand-Roll |
| `firestarter_fw/test/native/avr/test_verify_error_ids/test_verify_error_ids.cpp` (name at discretion) | test (native Unity behavioural) | event-driven (drive op → capture emitted frames) | `firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp` | **exact** — the only in-tree test that asserts an emitted message **id**, and it already asserts a severity fork |
| `…/test_verify_error_ids/host_stubs.cpp` | test scaffolding | — | `firestarter_fw/test/native/avr/test_eeprom28c_sdp/host_stubs.cpp` (28 lines) | **exact** |
| `platformio.ini` new-suite registration (2 lines, not 4) | config | — | existing `[native_base]` `test_filter` + `shared_build_flags` blocks | **exact** |
| Bench evidence artifacts (`pre.bin` / `mid.bin` / `post.bin` + logs) under the phase dir | evidence | file-I/O | Phase 203's `203-SESSION-COST.md` evidence shape | role-match |

### Modified files (no new pattern needed — edit in place, follow the file's own convention)

| File | Role | Data Flow | Change |
|---|---|---|---|
| `firestarter_fw/include/firestarter.h` | config/header | — | delete 2 `#define`s + 2 `is_memory_cmd` arms; add reserved-gap comment; repair the stale "nine named macros / a source-scan gate checks this" comment (`:105-110`) |
| `firestarter_fw/src/firestarter.cpp` | controller (dispatch) | request-response | delete 2 switch arms (`:270-272`, `:276-278`) |
| `firestarter_fw/src/eprom_operations.cpp` + `include/eprom_operations.h` | controller wrappers | request-response | delete both wrappers + declarations |
| `firestarter_fw/src/proms/{memory,eprom,flash_nor_unlock,flash_intel,flash_5v_page,eeprom_28c}.cpp` | service (protocol configure) | event-driven | delete the six `configure_*` arms |
| `firestarter_fw/src/operation_utils.cpp` | service | event-driven | delete the whole `CMD_BLANK_CHECK` emit-and-ack block (`:231-251`) |
| `firestarter_fw/src/proms/memory.cpp` `:500-508`, `:529-531` | service | streaming | collapse both cmd-keyed branches to their `else` / unconditional arm |
| `firestarter_fw/tests/test_blank_check_region_source_contract.py` | test | batch | **G1** — `== 6` → `== 1`, docstring census |
| `firestarter_fw/tests/test_boolean_convention_source_contract_v133.py` | test | batch | **G2** — 9 → 7, rename fn, docstring prose |
| `firestarter_fw/tests/test_protocol_branch_inventory.py` | test | batch | **G4** — `protocol_lines == [70]` → `[67]` |
| `firestarter_fw/tests/golden/protocol_branch_inventory.json` | golden | — | **G3/G5** — re-derive `sites[].line`, re-record `meta.blob_shas["src/proms/eprom.cpp"]` |
| `firestarter_fw/test/native/avr/{test_dispatch,test_val_eprom,test_val_nor_unlock,test_val_eeprom28c,test_cmd_admission}/*.cpp` | test | event-driven | re-key/delete the retired-ordinal cases; 9 → 7 in the admission truth table |
| `firestarter_app/firestarter/constants.py` | config | — | delete 4 lines; reserved-gap comment; repair the stale `:59-69` citation block |
| `firestarter_app/firestarter/eprom_operations.py` | service | request-response | delete import; change the `:628` live guard; repair 6 stale comments |
| `firestarter_app/tests/test_eprom_operations.py` | test | — | 3 import sites that become ImportError |
| `firestarter_fw/CLAUDE.md`, `firestarter_fw/PROTOCOLS.md` | docs | — | 4 stale citations |
| `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` | planning | — | D-03 amendment, own commit before the first implementation plan |

---

## Pattern Assignments

### `firestarter_fw/tests/test_<name>_source_contract.py` (test, source-contract gate)

**Analog:** `firestarter_fw/tests/test_write_path_source_contract_v131.py` (primary shape)
**Secondary analog:** `firestarter_fw/tests/test_blank_check_region_source_contract.py` (brace-matching helpers)

This is the eighth member of a house family. **Copy the shape element for element.** Seven analogues
exist; inventing a fresh regex scanner is explicitly rejected by RESEARCH.

**Imports + path-resolution pattern** (`test_write_path_source_contract_v131.py:142-159`):

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

Note the deliberate split: one target carries an env seam (for the planted-violation RED run), the
other does not, and the non-vacuity/self-check legs **never** read the seam. Resolution is always
`_REPO_ROOT`-relative, never `os.environ` alone — this closes the recorded
`check_permitted_claims.py` `_HERE`-resolves-wrong landmine by construction.

**Concatenation-built needles** (`:160-175`):

```python
# Concatenation-built needles. Coverage 12 asserts none of these appear
# verbatim anywhere in this module's own source -- a gate that quotes its
# forbidden tokens verbatim matches itself and can never pass.
_NEEDLE_RETRY_MACRO = "NUMBER" + "_OF_RETRIES"
_NEEDLE_PROGRAM_MISMATCHED_BYTES = "program_mismatched" + "_bytes"

_ALL_SELF_CHECK_NEEDLES = (
    ("the retry-count macro", _NEEDLE_RETRY_MACRO),
    ("the removed block-mismatch reporting function", _NEEDLE_PROGRAM_MISMATCHED_BYTES),
)
```

For FWCMD-04 the needles are `"memory_verify_exec" + "ute"` and
`"VERIFY_PER_PULSE_PLUS" + "_FINAL"`.

**Shape-preserving comment stripper** (`:220-252`) — copy verbatim; every analogue shares it.
It replaces each stripped span with whitespace of the *same shape* so line numbers survive:

```python
def _strip_comments(text):
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
```

**Brace-matched containment** — from `test_blank_check_region_source_contract.py:232-263`. Use this,
never line proximity, to prove the `memory_verify_execute(handle);` call is *inside* the
`VERIFY_PER_PULSE_PLUS_FINAL` arm:

```python
def _find_matching_brace(text, open_idx):
    """Brace-matched (not flat-regex) scan for the `}` closing the `{` at
    `open_idx` -- a containment test based on line proximity would be a guess.
    This is not."""
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _function_body_span(stripped, def_re):
    m = def_re.search(stripped)
    if not m:
        return None
    open_idx = m.end() - 1
    return (open_idx, _find_matching_brace(stripped, open_idx))


def _read_stripped(path):
    return _strip_comments(path.read_text())
```

**Core assertion pattern** — equality against a named count with the offending hits echoed, never a
floor and never a bare count (`test_blank_check_region_source_contract.py:373-395`):

```python
    assert len(wrapper_hits) == 6, (
        "expected exactly 6 function-pointer assignments of the "
        "whole-device wrapper to handle->firestarter_operation_main or "
        f"handle->firestarter_operation_end, found {len(wrapper_hits)}.\n"
        "Got:\n" + "\n".join(wrapper_hits)
    )
```

**Three mandatory belt-and-braces legs** — all three exist verbatim in every analogue and must be
carried into the new module (`test_write_path_source_contract_v131.py:637-712`):

```python
def test_scan_targets_are_non_vacuous():
    default_eprom = _REPO_ROOT / _EPROM_REL           # recomputed fresh, never the env seam
    for label, p in (("eprom.cpp", default_eprom),):
        assert p.is_file(), (
            f"default {label} scan target {p} does not exist on disk -- a "
            "missing scan target must FAIL, never silently pass."
        )
        assert p.stat().st_size > 0, f"default {label} scan target {p} is empty"
        assert p.resolve().is_relative_to(_REPO_ROOT), (
            f"default {label} scan target {p} resolves outside _REPO_ROOT"
        )
        assert _strip_comments(p.read_text()).strip() != ""


def test_this_module_cannot_be_silently_skipped():
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
    dependency_skip_call = "importor" + "skip"
    assert skip_call not in own_text
    assert skipif_marker not in own_text
    assert ("pytest." + dependency_skip_call) not in own_text


def test_own_needles_do_not_appear_verbatim_in_this_module():
    own_text = Path(__file__).read_text()
    for label, needle in _ALL_SELF_CHECK_NEEDLES:
        assert needle not in own_text, (
            f"the concatenation-built needle for {label} appears verbatim "
            "in this module's own source -- rebuild it from at least two "
            "literal pieces so this gate cannot match itself."
        )
```

Plus a **positive** leg (the analogue's `test_the_per_byte_loop_constructs_are_present`,
`:390-423`): `eprom_params.cpp` still ships `VERIFY_PER_PULSE_PLUS_FINAL` for `0x07` and `0x08`.

**Docstring pattern:** the analogue's docstring is ~140 lines and carries, in order: phase/plan
provenance, `Requirements:` line, a "Defect class this closes" section reasoning about *why* a
source scan is the right instrument, a numbered `Coverage:` list with one entry per test function,
and an "Environment seams" section. Match that structure — the house convention is a *reasoned
census*, never a bare count.

---

### `firestarter_fw/test/native/avr/test_<name>/test_<name>.cpp` (test, native Unity behavioural)

**Analog:** `firestarter_fw/test/native/avr/test_eeprom28c_sdp/test_eeprom28c_sdp.cpp`

This is the **only** in-tree test that asserts an emitted message id, and the only one that asserts
a severity fork — precisely the recorded trap D-04 names. Existing native tests assert
`h.response_code == RESPONSE_CODE_ERROR` and nothing more.

**Serial capture seam** (`test_eeprom28c_sdp.cpp:156-164`):

```c
static std::vector<uint8_t> captured_frames;

void setUp(void) {
    ArduinoFakeReset();
    captured_frames.clear();
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(uint8_t)))
        .AlwaysDo([](uint8_t b) -> size_t {
            captured_frames.push_back(b);
            return (size_t)1;
        });
    When(OverloadedMethod(ArduinoFake(Serial), write, size_t(const uint8_t*, size_t))).AlwaysReturn(1);
    When(Method(ArduinoFake(Serial), flush)).AlwaysReturn();
}
```

**Frame-id walker** (`:87-107`) — copy verbatim. It walks `rurp_log_id()`'s documented wire layout
(4-byte magic, 2-byte big-endian length, id at `offset+6`, params, crc, anchor) and never consults a
message-id-to-param-count lookup table, so it stays correct for any id:

```c
static void sdp_captured_frame_ids(std::vector<uint8_t>* out_ids) {
    size_t offset = 0;
    while (offset + 7 <= captured_frames.size()) {
        uint16_t len_value = (uint16_t)(((uint16_t)captured_frames[offset + 4] << 8)
                                        | captured_frames[offset + 5]);
        size_t frame_size = 4 + 2 + (size_t)len_value + 1;
        if (offset + frame_size > captured_frames.size()) {
            break; /* incomplete trailing frame -- not expected in these cases */
        }
        out_ids->push_back(captured_frames[offset + 6]);
        offset += frame_size;
    }
}

static bool sdp_ids_contains(const std::vector<uint8_t>& ids, uint8_t id) {
    for (size_t i = 0; i < ids.size(); i++) {
        if (ids[i] == id) return true;
    }
    return false;
}
```

**The severity-fork assertion pattern** (`:550-586`) — **assert both directions**, so a
transposition is caught rather than passing on a superset:

```c
    TEST_ASSERT_TRUE_MESSAGE (sdp_ids_contains(ids,  (uint8_t)MSG_WARN_CHIP_ID_MISMATCH), "...");
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids,  (uint8_t)MSG_ERR_CHIP_ID_MISMATCH),  "...");
    /* second case, opposite configuration: */
    TEST_ASSERT_TRUE_MESSAGE (sdp_ids_contains(ids2, (uint8_t)MSG_ERR_CHIP_ID_MISMATCH),  "...");
    TEST_ASSERT_FALSE_MESSAGE(sdp_ids_contains(ids2, (uint8_t)MSG_WARN_CHIP_ID_MISMATCH), "...");
```

Apply this to each of D-03's three ids: assert `MSG_ERR_VERIFY` (0xAF) present **and**
`MSG_ERR_OP_TIMEOUT` (0xB7) absent for `eeprom28c_verify_page_readback`; the inverse for
`flash_util_verify_operation`; `MSG_ERR_MAX_PULSES` (0xBD) vs `MSG_ERR_ENERGY_CAP` (0xBE) for the
two per-pulse budget exits.

**Design constraint from RESEARCH:** `eeprom28c_verify_page_readback` is `static`, so it can only be
driven through `eeprom28c_write_execute`.

---

### `firestarter_fw/test/native/avr/test_<name>/host_stubs.cpp` (test scaffolding)

**Analog:** `firestarter_fw/test/native/avr/test_eeprom28c_sdp/host_stubs.cpp` (28 lines)

Per-suite stub file that opts into shared behaviour with a `#define` **before** the include:

```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>

extern "C" {
#include "rurp_shield.h"
#include "rurp_types.h"
}

/* Activate the ordered strobe recorder (opt-IN). MUST precede the include. */
#define HOST_STUBS_REAL_REGISTER_UTILS

#include "../_shared/host_stubs_common.inc"

#include "rurp_register_utils.h"
```

`_shared/host_stubs_common.inc` is 302 lines and carries **no** `millis`/`delay` seam — see the
millis pattern below, which comes from a different source.

---

### The advancing `millis()` seam (for `flash_util_verify_operation`'s 150 ms timeout)

**Analog:** `firestarter_fw/test/native/avr/test_cobs_cmd_frame/test_cobs_cmd_frame.cpp:134-159`

CONTEXT's "no millis seam" is true of `_shared/host_stubs_common.inc` but **not** of the native
environment. Two suites already install an advancing counter through ArduinoFake:

```c
static unsigned long millis_counter;

void setUp(void) {
    ArduinoFakeReset();
    millis_counter = 0;
    When(Method(ArduinoFake(Function), millis))
        .AlwaysDo([&]() -> unsigned long {
            millis_counter += 100;
            return millis_counter;
        });
}
```

Two ticks of 100 ms clears a `millis() + 150` deadline. Every other native suite pins `millis()` to
`.AlwaysReturn(0)`, which is why the timeout arm is unreachable there today.

---

### `platformio.ini` (config) — registering the new native suite

**Analog:** the existing `[native_base]` block in `firestarter_fw/platformio.ini`.

`test_filter` and `shared_build_flags` are each defined **once** in `[native_base]`; both
`[env:native]` and `[env:native_nodevtools]` `extends = native_base`. So registration is **two
lines, not four** (`firestarter_fw/CLAUDE.md` is stale on this point):

```ini
[native_base]
test_filter =
	native/avr/test_dispatch
	...
	native/avr/test_hv_route_ceiling
	native/avr/test_<new_suite>          # <- line 1

shared_build_flags =
	-std=gnu++17
	-I include
	-I test/native/avr/test_dispatch
	...
	-I test/native/avr/test_<new_suite>  # <- line 2
```

**Do not** give either env its own filter: `pio test -e native` is pull-requests-only while
`native_nodevtools` always runs, and sharing the filter is what makes the new suite run in both.

---

### `firestarter_app/firestarter/constants.py` (config) — the reserved-ordinal gap

**Analog:** the file's own existing convention. `constants.py:43-48` already carries the lockstep
rule as a comment at the head of the ladder; `:59-69` and `:79-84` are the precedent for a
*reasoned* comment attached to a ladder entry:

```python
# Wire-protocol command codes — Firmware sync: firestarter.h
# cmd field values sent in JSON commands to the Arduino firmware.
# ... this ladder and firmware's CMD_* ladder in firestarter.h move together —
# every addition here must be mirrored there in the same change, and vice versa.
COMMAND_READ = 1
COMMAND_WRITE = 2
COMMAND_ERASE = 3
COMMAND_BLANK_CHECK = 4          # <- deleted; gap comment goes here
COMMAND_CHECK_CHIP_ID = 5
COMMAND_VERIFY = 6               # <- deleted; gap comment goes here
```

Mirror the comment shape (reason first, then the citation, function-name-plus-line never a bare
line number) on the firmware side at `firestarter_fw/include/firestarter.h:48-54`:

```c
#define CMD_IDLE 0
#define CMD_READ 1
#define CMD_WRITE 2
#define CMD_ERASE 3
#define CMD_BLANK_CHECK 4        // <- deleted; gap comment goes here
#define CMD_CHECK_CHIP_ID 5
#define CMD_VERIFY 6             // <- deleted; gap comment goes here
```

**Stale-citation repair is mandatory in the same edit** (`/workspaces/CLAUDE.md`'s never-accept-
staleness rule). `constants.py:59-69` cites `test_command_names_dereferences_both_sdp_commands` in
`tests/test_revision_constants_parity.py` — **that file does not exist** — and cites
`eprom_operations.py:329` / `:405` for the `COMMAND_NAMES[cmd]` dereferences, which are really at
`:584` and `:693`. Likewise `firestarter.h:105` claims "All nine named macros are unconditionally
defined. A source-scan gate checks this." — the count becomes seven and **no such gate exists**
(the only `is_memory_cmd` reference outside the header is `test_cmd_admission.cpp`).

---

### `firestarter_app/firestarter/eprom_operations.py:612-630` (service) — the live `region-end` guard

**Analog:** the site itself. The surrounding comment is a worked example of the house convention —
reasoning at the site, citing the decision id:

```python
        # BLANK-01 / D-05: the write-init blank check on the firmware side must
        # scope to the region this operation actually touches, not the whole
        # device. ... One code path, no branch on address presence: the
        # key is emitted on every write and verify, not only when --address is
        # given. ...
        if (
            region_length is not None
            and region_length > 0
            and cmd in (COMMAND_WRITE, COMMAND_VERIFY)
        ):
            command_dict[JSON_KEY_REGION_END] = addr + region_length
```

Discretion item (tuple-of-one vs `cmd == COMMAND_WRITE`) — whichever is chosen, **re-write the
comment**: it describes a firmware region-scoped blank check that Phase 205 removes, and names a
`verify` composition that no longer exists.

---

## Shared Patterns

### Gate re-anchor pattern (G1, G2, G4)

**Source:** `firestarter_fw/tests/test_blank_check_region_source_contract.py:359-395`
**Apply to:** all three count/line literals being re-anchored.

A re-anchor is **three coordinated edits, never one**: the literal, the *function name* if it
encodes the count (`test_exactly_six_…` → `test_exactly_one_…`,
`test_the_nine_forwarding_calls_are_present` → `…_seven_…`), and the docstring's census prose. The
house asserts equality against a named count with the hits echoed — never a floor.

### Golden re-derive pattern (G3, G5)

**Source:** `firestarter_fw/tests/golden/protocol_branch_inventory.json` `meta.recorded_by`, plus the
recipe in RESEARCH §Code Examples.
**Apply to:** the branch-inventory golden only.

Re-derive with the gate module's **own** extractor, never by hand, and match old sites to live sites
**positionally** — never through a `(predicate, keyed_on, tier)` dict, which collides for at least
two `eprom.cpp` site pairs and silently keeps only the last:

```python
import sys, json; sys.path.insert(0, "tests")
import test_protocol_branch_inventory as m
from pathlib import Path

live = m._extract_predicates(Path("src/proms/eprom.cpp").read_text())
old  = json.load(open("tests/golden/protocol_branch_inventory.json"))

assert len(old["sites"]) == len(live)
for i, (a, b) in enumerate(zip(old["sites"], live)):
    assert (a["predicate"], a["keyed_on"], a["tier"]) == (b["predicate"], b["keyed_on"], b["tier"]), i
```

Then re-record `meta.blob_shas["src/proms/eprom.cpp"]` with `git hash-object src/proms/eprom.cpp`
against the swept working tree **before staging**. `eprom_params.cpp`'s sha is untouched.
**Source and golden must land in ONE commit.**

### Reasoning-at-the-site pattern

**Source:** `firestarter_fw/src/firestarter.cpp:179-183` (the clearest exemplar in the tree):

```c
// Emitting identity HERE is safe: configure_memory has run, but every
// configure_* handler is pure function-pointer assignment and the VPP
// regulator is not engaged until firestarter_operation_init, behind
// op_wait_for_ack(). A host that reads this ack and refuses stops with the rail
// still DOWN -- the compatibility gate cannot energise the part it protects.
```

**Apply to:** the two reserved-ordinal gap comments, the site-18/19 collapses in `memory.cpp`, and
the rewritten `region-end` guard comment. The no-comments-in-source rule was retired 2026-09-19;
reasoning belongs at the site. State *why*, cite by content or function-name-plus-line, never a bare
line number.

### Gate idioms that must NOT be used

**Apply to:** any new gate or bench script in this phase.
BRE `\+\+\+`, `;`-chains, OR-grep, `grep -c`, `--stat`, unset-var `rev-list`, and `grep -qF` with a
dash-leading pattern (exits 2 → fails open). `grep` in this devcontainer is ugrep and honours
`.gitignore`, so a census sweep needs `--no-ignore` — but note RESEARCH Pitfall 1: `--no-ignore` can
silently return zero matches. Every new gate must have its RED **seen**, not pre-authored.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| The bench evidence bundle (checksums of `pre.bin`/`mid.bin`/`post.bin`, the four commit shas per D-07, flash command logs) | evidence | file-I/O | No prior phase produced a *four-role skew matrix* on silicon. Phase 203's `203-SESSION-COST.md` is the closest shape for a measured-bench artifact, but its content is unrelated. The planner should define the artifact's structure in the plan: D-07 requires the substitution to be stated explicitly and each of the four roles named by sha, because `_probe_port` truncates the prerelease suffix and the host **cannot** tell you which firmware is on the board. |
| The D-03 requirement amendment (`.planning/REQUIREMENTS.md` FWCMD-05, `.planning/ROADMAP.md` criterion 3) | planning | — | Not code. **Precedent, not analog:** Phase 203's D-02 amended WRITE-02 the same way. Land it as its own commit before the first implementation plan. |

---

## Metadata

**Analog search scope:** `firestarter_fw/tests/`, `firestarter_fw/test/native/avr/`,
`firestarter_fw/src/`, `firestarter_fw/include/`, `firestarter_fw/platformio.ini`,
`firestarter_app/firestarter/`, `firestarter_app/tests/`
**Files scanned:** ~40 (census already measured in 204-RESEARCH.md; this map adds the analog reads)
**Tracked-source check:** `git ls-files` run inside each submodule for every analog path named above — all tracked, no mirror paths
**Pattern extraction date:** 2026-09-21
