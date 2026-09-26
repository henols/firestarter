# Phase 158: Residual Optimizations + Cold Baseline Re-Record (firmware-only) — Pattern Map

**Mapped:** 2026-08-24
**Files analyzed:** 12 (2 new test fixtures groups = 4 new files, 1 new test module, 2 new records, 5 updated in place, 2 JSON data files)
**Analogs found:** 12 / 12 (11 exact, 1 role-match)
**Scope fence:** `firestarter/` submodule + meta-repo `.planning/` only. No `firestarter_app/` file is mapped (RESEARCH F-9).

All paths below are relative to `/workspaces/firestarter` unless prefixed `.planning/`
(meta repo, `/workspaces`).

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `lib/jsmn/src/jsmn.h` (mod — LAND-05) | vendored header / type definition | transform (in-RAM token layout) | `include/firestarter.h` narrowing precedent in Phase 157 + `src/json_parser.c:164-275` `field_desc_t` sizeof warning | role-match (no prior edit to this vendored file exists) |
| `lib/jsmn/src/jsmn.c` (**read-only constraint, no edit**) | vendored implementation | transform | — (constraint file: the twelve `-1` sentinel field refs at `:15,222,241,256,290,348`) | n/a |
| `scripts/baseline/size_baseline.json` (mod — LAND-01) | config / recorded measurement | batch (transcribe-from-log) | its own `meta.generated_by` (quick task 260820-a7w generation) — the convention lives inside the file it governs | exact (self-analog) |
| `scripts/baseline/size_baseline_base01.json` (mod — LAND-03, 4 ints) | config / frozen anchor | batch | the 260820-a7w `flash_total` axis move, machine-checked at `tests/test_check_size_baseline.py:1106` | exact |
| `tests/fixtures/captured_build_v158_{uno,uno328pb,leonardo}.log` (**new**) | test fixture (captured tool output) | file-I/O | `tests/fixtures/captured_build_v153_{uno,uno328pb,leonardo}.log` | exact |
| `tests/fixtures/planted_size_baseline_flash_regression_v158.log` (**new**) | test fixture (planted violation) | file-I/O | `tests/fixtures/planted_size_baseline_flash_regression_v153.log` | exact |
| `tests/fixtures/captured_test_native{,_nodevtools}_summary.log` (mod **in place**) | test fixture (captured tool output) | file-I/O | themselves — in-place is the established convention for this pair (`test_check_size_baseline.py:593-586`) | exact (self-analog) |
| `tests/test_check_size_baseline.py` (mod — 4 legs + `:459` docstring) | test (subprocess gate suite) | request-response (subprocess) | its own Plan 153-15 severance edits (`:500-640`, `:1362`) | exact (self-analog) |
| `tests/test_check_build_warnings.py` (verify only — 24-passed leg) | test | request-response | — (asserted green, not edited) | n/a |
| `tests/meta_presence.py` (mod — `:52-56` docstring) | test helper / skip-gate module | config | its own `:40-53` "binds at import time" prose | exact (self-analog) |
| `tests/test_checker_convention.py` (mod — `:145`/`:146` + `:76-78`) | test (meta-convention gate) | batch (glob count) | its own `:70-90` floor-raise instruction, which names Phase 158 | exact (self-analog) |
| `tests/test_jsmn_token_layout_source_contract_v158.py` (**new**, Wave 0 — LAND-05) | test (source-scanning contract gate) | file-I/O (read + regex) | **`tests/test_boolean_convention_source_contract_v133.py`** | exact |
| `.planning/v1.33/158-before-figures.md`, `158-after-figures.md` (**new**) | record | batch | `.planning/v1.33/157-before-figures.md:1-21`, `157-after-figures.md:1-30` | exact |

**Not touched, by decision:** `src/proms/flash_5v_page.cpp` (LAND-06 DECLINED),
`test/native/avr/test_val_5v_page/test_val_5v_page.cpp` (no new cases),
`.planning/v1.33/CITATIONS-STALE.md` (Phase 159 owns it; REMAP-04 close-blocking),
`ROADMAP.md` / `REQUIREMENTS.md` (corrections live in the record — Pattern 4).

---

## Pattern Assignments

### 1. `tests/test_jsmn_token_layout_source_contract_v158.py` (test, source-scan) — **the highest-risk new file**

**Analog:** `tests/test_boolean_convention_source_contract_v133.py` (442 lines — the smallest
of the four in-tree source-contract gates; the siblings are
`test_write_path_source_contract_v131.py` 715, `test_ack_layout_source_contract_v143.py` 568,
`test_hv_routing_source_contract_v142.py` 806, all the *same* shape).

**Why this analog, on failure mode not shape:** memory records that app-side gates scanning
firmware source **fail OPEN** on a rename. This family closes that hole by construction with
three self-protecting legs (`test_scan_targets_are_non_vacuous`,
`test_this_module_cannot_be_silently_skipped`, `test_own_needles_do_not_appear_verbatim_in_this_module`).
A `jsmn.h` grep gate written without them would pass vacuously the moment `lib/jsmn/src/jsmn.h`
moves. **Copy all three.**

**Imports + path resolution** (`test_boolean_convention_source_contract_v133.py:127-145`) —
stdlib only, no `conftest.py` (house rule):
```python
import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_WRAPPERS_REL = "src/eprom_operations.cpp"          # -> "lib/jsmn/src/jsmn.h"

# Environment seam -- binds at IMPORT time. See the module docstring's
# "Environment seams" section above.
_SCAN_WRAPPERS = Path(
    os.environ.get(
        "FIRESTARTER_BOOLEAN_CONVENTION_SCAN_SOURCE", str(_REPO_ROOT / _WRAPPERS_REL)
    )
)
```
Name the new seam `FIRESTARTER_JSMN_TOKEN_LAYOUT_SCAN_SOURCE`. The docstring **must** carry an
`Environment seams:` section — the analog's own words: *"this repository has no central
environment-variable inventory -- this docstring is the only place a reader can discover them"*
(`:90-92`).

**Comment/literal stripper** (`:171-220`) — copy `_strip_comments` verbatim; it replaces
comments *and quoted-literal contents* with same-shape whitespace so line numbers survive.
Load-bearing here: `jsmn.h` carries the **dead duplicate implementation at `:106-475`** whose
eleven `-1` lines are live text to a naive grep. If the leg must scope to the *live* struct
only, slice the region above `#ifndef JSMN_HEADER` (`jsmn.h:117`) rather than trusting a
global count.

**Non-vacuity leg** (`:371-397`) — copy exactly, retargeted:
```python
def test_scan_targets_are_non_vacuous():
    """Coverage 5 -- structural self-check, never reads the environment
    seam: both DEFAULT scan targets (recomputed fresh from _REPO_ROOT --
    the check_permitted_claims.py _HERE-resolves-to-the-wrong-directory
    landmine, closed here by construction) exist, are non-empty, resolve
    inside this repository, and their comment-and-literal-stripped text is
    non-empty. A missing or empty scan target must FAIL, never silently
    pass as if nothing needed checking."""
    ...
        assert p.is_file(), (
            f"default {label} scan target {p} does not exist on disk -- a "
            "missing scan target must FAIL, never silently pass."
        )
        assert p.stat().st_size > 0, f"default {label} scan target {p} is empty"
        assert p.resolve().is_relative_to(_REPO_ROOT), (...)
        stripped = _strip_comments(p.read_text())
        assert stripped.strip() != "", (...)
```

**Never-skip leg** (`:403-429`) — copy exactly; note the concatenation trick so the module's
own source cannot match its own needles:
```python
def test_this_module_cannot_be_silently_skipped():
    own_text = Path(__file__).read_text()
    skip_call = "pytest" + ".skip"
    skipif_marker = "mark" + ".skipif"
    dependency_skip_call = "importor" + "skip"
    assert skip_call not in own_text, (...)
```

**Own-needles leg** (`:431-442`) — copy; pair it with the `_assert_identifier_absent`
word-boundary helper (`:223-236`).

**The actual LAND-05 assertions** — model on `test_engine_retains_exactly_one_negated_call`
(`:290-315`), which asserts an *exact count*, not mere presence:
- exactly one `int start;` and exactly one `int end;` inside the live `jsmntok` struct
- (recommended) `uint8_t type;` / `uint8_t size;` present, so a revert is also loud

**Anti-pattern from RESEARCH:** do **not** assert `sizeof(jsmntok_t)` in a native test —
AVR is 6 B, host is 12 B. `src/json_parser.c:164-275` carries the same prohibition verbatim for
`field_desc_t`. The linker's `RAM: used N` line and `avr-nm` are the witnesses.

**CI framing clause** — the analog's `:112-118` states CI coverage honestly. Its wording is
**stale in the same way `test_check_size_baseline.py:459` and `meta_presence.py:56-58` are**
(`build.yml` is now `push: branches: ['**','!beta']`). The new module must state the *correct*
framing: `pytest tests/ -v` at `build.yml:161` **does** fire on this milestone branch.

---

### 2. `tests/fixtures/captured_build_v158_{uno,uno328pb,leonardo}.log` (fixture, captured) — **the second-highest risk**

**Analog:** `tests/fixtures/captured_build_v153_{uno,uno328pb,leonardo}.log`.
**The analog's format is normative — it is verbatim `pio run` output, 86 lines, committed unedited.**

Exact shape (v153 uno, head):
```
Processing uno (platform: atmelavr; board: uno; framework: arduino)
--------------------------------------------------------------------------------
Verbose mode can be enabled via `-v, --verbose` option
CONFIGURATION: https://docs.platformio.org/page/boards/atmelavr/uno.html
PLATFORM: Atmel AVR (5.2.0) > Arduino Uno
HARDWARE: ATMEGA328P 16MHz, 2KB RAM, 32KB Flash
...
Compiling .pio/build/uno/src/proms/flash_5v_page.cpp.o
...
Linking .pio/build/uno/firestarter_uno.elf
Checking size .pio/build/uno/firestarter_uno.elf
Advanced Memory Usage is available via "PlatformIO Home > Project Inspect"
RAM:   [========  ]  76.9% (used 1575 bytes from 2048 bytes)
Flash: [========= ]  78.0% (used 25548 bytes from 32768 bytes)
Building .pio/build/uno/firestarter_uno.hex
========================= [SUCCESS] Took 2.07 seconds =========================

Environment    Status    Duration
-------------  --------  ------------
uno            SUCCESS   00:00:02.065
========================= 1 succeeded in 00:00:02.065 =========================
```

**Rules the analog encodes (`tests/fixtures/README.md:6-13`):**
- `captured_*` = **verbatim tool output, committed unedited** — no trimming, no reflow, no ANSI
  stripping, **no hand-edited number**.
- One measurement, two consumers (RESEARCH Pattern 3): the *same three logs* LAND-01 transcribes
  become these fixtures. Capture once; `tee` to a path, transcribe the `RAM:`/`Flash:` lines into
  `size_baseline.json`, then copy the file in as the fixture.
- Presence is verified with `git ls-files tests/fixtures/`, **never** `git add`'s exit code
  (README.md:29-36 — git silently stages nothing at exit 0 for some paths).

**Consumers to repoint (both currently name `captured_build_v153_*`):**
- `test_clean_avr_all_three_envs_pass` — `tests/test_check_size_baseline.py:523` (tuple at `:549-553`)
- `test_default_mode_is_unchanged_by_the_new_flag` — `:1362` (tuple at `:1385-1389`)

Both use the identical loop body — copy it, change only the fixture names:
```python
    for env_name, fixture in (
        ("uno", "captured_build_v158_uno.log"),
        ("uno328pb", "captured_build_v158_uno328pb.log"),
        ("leonardo", "captured_build_v158_leonardo.log"),
    ):
        result = _run_checker(["--avr-log", f"{env_name}={_FIXTURES / fixture}"])
        assert result.returncode == 0, (...)
```

---

### 3. `tests/fixtures/planted_size_baseline_flash_regression_v158.log` (fixture, planted)

**Analog:** `tests/fixtures/planted_size_baseline_flash_regression_v153.log` (86 lines).

**Derivation rule, unchanged since Phase 123:** it is a byte-for-byte copy of the **leonardo**
capture of its own generation with the `Flash:` figure alone advanced by **+512 B**; the `RAM:`
line, percentages and everything else are the capture's. v153: `27630 + 512 = 28142`, and its
`RAM:` line still reads `used 2016 bytes`. So for v158: copy `captured_build_v158_leonardo.log`,
edit the single `Flash:` used figure to `<new leonardo flash> + 512`. Leave the percentage bar as
captured — the analog does (`85.9%` is the 28142 figure's, so recompute or leave per the analog's
own precedent; check the v153 byte diff against its capture before deciding).

`README.md:11-13`: a `planted_*` fixture is *"a deliberate violation, each derived from a named
`captured_` file by a single stated edit"* — **state the edit in the plan's SUMMARY.**

**Consumer:** `test_planted_flash_regression_flips_checker_to_failure`,
`tests/test_check_size_baseline.py:610`. Its assertions name **both** figures (baseline and
observed) as literals — both must be updated:
```python
    result = _run_checker(
        ["--avr-log", f"leonardo={_FIXTURES / 'planted_size_baseline_flash_regression_v158.log'}"]
    )
    assert result.returncode != 0, (...)
```
The docstring records *why* severance rather than repoint: *"a leg that fails, but for a reason
different from the one it names, is exactly the false-cause pattern this severance exists to fix"*
(`:600-611`).

---

### 4. `tests/fixtures/captured_test_native{,_nodevtools}_summary.log` (fixture, updated **in place**)

**Analog:** themselves. 21-line `pio test` SUMMARY tails; the last line is the one that moves:
```
================ 172 test cases: 172 succeeded in 00:00:41.122 ================
```
**Never severed** — the in-place convention is recorded at `test_check_size_baseline.py:593-586`
and its docstring explains the licence: *"this is the ONLY leg in this module that consumes
either native summary fixture, so nothing else depends on 172 staying frozen"*. Both must be
**genuine captures of a real run at the final tree position, not hand-edited counts** — the
docstring says so in as many words (*"not hand-edited counts -- the same in-place convention,
sourced the honest way"*).

**Consumer:** `test_clean_native_both_envs_pass` (`:562`), whose two literal asserts move:
```python
        assert "172" in result.stdout, f"Expected '172' in output. Got:\n{result.stdout}"
        assert "17" in result.stdout, f"Expected '17' in output. Got:\n{result.stdout}"
```

---

### 5. `scripts/baseline/size_baseline.json` (config, recorded measurement)

**Analog:** itself — `meta.generated_by`, written by quick task 260820-a7w:
> *"The figures below are TRANSCRIBED, not computed, from the three cold-rebuild logs this quick
> task committed at `.planning/qu…`"*

`meta` key order to preserve (18 keys): `generated`, `phase`, `generated_by`,
`native_case_count_revision_260822`, `firmware_tree_sha`, `host_app_tree_sha`,
`platformio_core`, `platform_atmelavr`, `toolchain_atmelavr`, `avr_gcc`,
`framework_arduino_avr`, `framework_arduino_avr_minicore`, `roadmap_cross_check`,
`supersedes`, `consumed_by`, `note`, `warm_vs_cold_correction`, `deltas_vs_base01`,
`flash_ceiling_move_260820_a7w`. Follow the precedent of adding a *new* dated `meta.*` note key
(as `native_case_count_revision_260822` and `flash_ceiling_move_260820_a7w` did) rather than
rewriting an existing one.

Fields that move: `avr_targets.{uno,uno328pb,leonardo}.{flash_used,flash_free,ram_used,ram_free}`,
`native_envs.{native,native_nodevtools}.{cases,succeeded}` (172 → the **re-measured** final
count — RESEARCH Pitfall 9: re-measure, do not reuse 184 from the research doc).
Untouched: `flash_total`, `ram_total`, `suites`, `native_pinmap_provisional`, the whole
`warnings` block.

Discretionary prose repairs licensed by F-1: `meta.consumed_by` names 2 consumers, there are 3
(`scripts/check_release_assets.py:5,15-17`); `envs_agree_note` quotes a stale `{cases: 151}`.

---

### 6. `scripts/baseline/size_baseline_base01.json` (config, frozen anchor — LAND-03 FIX)

**Analog:** the 260820-a7w `flash_total` move, whose licence is machine-checked at
`tests/test_check_size_baseline.py:1106` (`test_base01_is_not_re_anchored_by_the_new_exemption`).
Its docstring **is** the axis-split doctrine to cite:
> *"the true invariant this leg proves is narrower and still holds: BASE-01's GROWTH axis
> (`flash_used`, `ram_used`) is byte-unchanged, while its board-identity axis (`flash_total`) is
> licensed to move when the silicon ceiling genuinely changes … it is why this leg pins
> flash_used/ram_used, never flash_total, as the thing that must not move without cause."*

The edit is exactly 4 integers (current values confirmed on disk):
```json
"native_envs": {
  "native":            { "cases": 141, "succeeded": 141, "suites": 17, "all_passed": true },
  "native_nodevtools": { "cases": 141, "succeeded": 141, "suites": 17, "all_passed": true }
}
```
`141 → <final count>` in all four positions. `suites` stays 17. The leg at `:1108` never reads
`native_envs`, so zero legs redden (measured, RESEARCH F-3). Add a `meta` note naming the third
axis (*test-inventory floor*, not a growth anchor), following the `meta.*_260822` note precedent.

---

### 7. `lib/jsmn/src/jsmn.h` (vendored header, LAND-05)

**Current live struct** (`jsmn.h:74-92`):
```c
typedef struct jsmntok {
  jsmntype_t type;
  int start;
  int end;
  int size;
#ifdef JSMN_PARENT_LINKS
  int parent;
#endif
} jsmntok_t;
```
**Target** (RESEARCH F-5; add `#include <stdint.h>` beside the existing `#include <stddef.h>` at `:27`):
```c
typedef struct jsmntok {
  uint8_t type;   /* was jsmntype_t (enum -> 16-bit int on AVR); values 0,1,2,4,8 */
  uint8_t size;   /* was int; max is an object's pair count or an array's length */
  int start;      /* UNCHANGED, signed -- carries the -1 sentinel */
  int end;        /* UNCHANGED, signed -- carries the -1 sentinel */
} jsmntok_t;
```
`JSMN_PARENT_LINKS` is defined nowhere in the tree, so `parent` does not exist in the shipped
struct. The **dead duplicate implementation** begins at `jsmn.h:117` under `#ifndef JSMN_HEADER`
while `#define JSMN_HEADER` sits at `:33` — it compiles in no TU (both confirmed on disk).
Editing it for consistency is a judgement call; correctness does not require it. **If left
alone, say so in the record**, because a reader grepping `jsmn.h` for `int size;` will find the
dead copy.

**House idiom for a vendored-file edit** (from `lib/jsmn/`'s existing local modifications:
`JSMN_HEADER`/`JSMN_STRICT` `#define`d inside the header, a hand-added
`/* to quiet a warning from gcc*/` in `jsmn.c`): mark the local delta with an inline comment
naming the reason, exactly as the two surviving local modifications do.

**Cross-architecture consumer:** `platform/py32f071/CMakeLists.txt:70` compiles the same
`jsmn.c`; `py32f071.yml` is the loud gate (`on: push: branches: ['**']`, `pull_request`
path-filtered on `lib/jsmn/**`). Attempt the toolchain install once; on failure record the
ceiling in `158-after-figures.md` (per the analog record's own `status:` block idiom).

---

### 8. `tests/meta_presence.py` (`:52-56` docstring correction)

**Analog:** its own surrounding prose (`:40-53`), which is precise and correct about the import-time
seam. Only the **CI coverage** paragraph is false:
```
**CI coverage, stated honestly.** This module executes in NO CI leg on this branch:
`pytest tests/ -v` runs only in `build.yml` (push/PR to `main`) and
`beta-build.yml` (push to `beta`) -- neither fires on this firmware
milestone branch, and `py32f071.yml` has no pytest step at all.
```
`build.yml:16-34` is now `on: push: branches: ['**', '!beta']`. Comment-only edit; **no
assertion changes.** Keep the `META_ROOT` / `FIRESTARTER_META_ROOT` seam prose (`:60-88`) intact
— it is the mechanism behind the 32-leg worktree skip (F-12) and is the reason `pytest tests/`
must be run from `/workspaces/firestarter`.

Same correction, same shape, at `tests/test_check_size_baseline.py:459`
(*"Neither repository's CI runs this suite"*).

---

### 9. `tests/test_checker_convention.py` (FLOOR carry-forward closure)

**Analog:** its own `:70-90` docstring, which pre-authors the exact edit and names Phase 158:
> *"`FLOOR`'s own 'the number actually shipped' wording is presently false by one, a carry-forward
> candidate for **Phase 158** to close by raising `FLOOR` to 8 and `FIXTURE_FLOOR` to match the
> fixture count actually present at that time, in the same commit that reconciles it …
> Measured actual counts at this commit: **8** `check_*.py` files, **30** `planted_*` entries."*

The literals (`:143-146`):
```python
# Hardcoded floors -- see module docstring for what each counts and why a
# future checker addition must raise these in the same commit.
FLOOR = 7
FIXTURE_FLOOR = 16
```
`FLOOR = 8`; `FIXTURE_FLOOR` = the count **at this phase's own commit** (30 `planted_*` on disk
today, **+1** once `planted_size_baseline_flash_regression_v158.log` lands → re-count, do not
transcribe). Both are `>=`, so this is a tightening, not a fix for a red gate. Repair the
`:76-78` prose in the same commit; the module's own rule is *"lowering a floor is never the
correct response to a red gate here"*.

---

### 10. `.planning/v1.33/158-before-figures.md` + `158-after-figures.md` (records)

**Analog:** `.planning/v1.33/157-before-figures.md:1-21` (frontmatter template) and
`157-after-figures.md:1-30` + its `##` section layout.

**Frontmatter shape** (copy exactly, retargeted):
```yaml
---
title: Before-figures record — milestone v1.33, Phase 158 (…, firmware-only)
phase: 158-residual-optimizations-cold-baseline-re-record-firmware-only
plan: "01"
measured: 2026-08-24
status: AUTHORITATIVE — this file is the ONLY source for Phase 158's before-half figures. …
supersedes: >
  ROADMAP.md §Phase 158 criteria … ; REQUIREMENTS.md LAND-… prose, wherever they state a
  figure this file corrects (C-1 through C-N). Neither document is edited by this plan; the
  correction lives here per the Phase 155/156/157 convention.
requirements: [LAND-01, LAND-02, LAND-03, LAND-04, LAND-05, LAND-06, LAND-07, LAND-08]
---
```
`157-before-figures.md`'s own `status:` already forward-declares this phase — the successor
record should reciprocate (name what Phase 159 invalidates).

**Body shape** — numbered `##` sections, each carrying **the verbatim command that produced
every number**. `157-after-figures.md`'s section list is the model: `## 1. Git anchors`,
`## 2. The phase ledger -- flash and RAM, before vs after, per target, COLD`, … `## 10. The gate
ledger -- all eight legs`, `## 11. The one-sidedness, quoted from source`, `## 12. The coverage
ceilings -- final form`, `## 13. The corrections ledger -- every row closed out`,
`## 16. Handoffs`, `## Self-verification of this record`. Section 2's excerpt shows the house
table idiom (bold figures, an explicit COLD/WARM statement, and a stated worktree disposition).

Phase 158's own required sections, mapped onto that skeleton:
- `## 11`-style **one-sidedness, quoted from source** — `sed -n '697p;709p' scripts/check_size_baseline.py`
  plus the verbatim PASS line with its negative deltas (LAND-02).
- a **severance inventory** section that explicitly says Groups 2 and 3 are *not needed*
  (every prior generation's docstring documents "the same four groups"; a reader will otherwise
  think two were forgotten — RESEARCH F-2).
- **LAND-06's decline**, with the `+22/+24/+22 B` measurement, the two `__udivmodsi4` sites from
  `avr-nm --print-size` + `avr-objdump -d --start-address --stop-address`, the zero-native-coverage
  gap as the stated reason, and the mandatory disconnection sentence (algorithm-5 flash-page path
  only; **not** the w27c512-write-slow-3x work, which is `src/proms/eprom.cpp`).
- **LAND-04's two clauses**: `grep -rn check_size_baseline .github/` → exit 1, **and**
  `grep -n "pytest tests/" .github/workflows/build.yml` → `:161`.
- **LAND-05's ARM ceiling**, stated rather than left implicit.
- **LAND-07's three bounds** (50 / 51 / 55) with derivations and the unaccounted 2-token gap.
- **LAND-08's** data points as (env, result, wall time) rows, with the prohibition on quoting a
  wall time as evidence.

---

## Shared Patterns

### S-1 — Fixture severance, never re-anchoring
**Source:** `tests/test_check_size_baseline.py:370-385` (module docstring, disposition table)
**Apply to:** every fixture file in this phase
> *"the `*_v151*` family … is retired in place and KEPT -- thirteen files, unmodified …
> re-anchoring or repointing an existing family instead of severing onto a new one reddens legs
> that assert at sub-allowance deltas, the standing lesson this module has already paid for once."*

`*_v153*` is retired in place and **KEPT, never deleted** — the standing disposition since the
260820-a7w severance. Only two of the four historical groups are authored this generation.

### S-2 — Transcribe, never compute
**Source:** `scripts/baseline/size_baseline.json` `meta.generated_by`
**Apply to:** `size_baseline.json`, `size_baseline_base01.json`, both `*-figures.md`
A figure typed from a `Flash:` line in a captured log is auditable; one derived by arithmetic on
another record is not. Corollary anti-pattern: **never** transcribe from
`check_size_baseline.py --rebuild`, whose `_rebuild_avr` (`:753`) uses `pio run -t clean`, not
the mandated `rm -rf .pio/build/<env>`.

### S-3 — Correction lives in the record, not in the prose
**Source:** `.planning/v1.33/157-before-figures.md:11-20` (`supersedes:` block)
**Apply to:** all four of this phase's corrections (F-3, F-5, F-6, F-7).
`ROADMAP.md` and `REQUIREMENTS.md` are **not edited**.

### S-4 — The one-commit rule
**Source:** RESEARCH F-4 / Pitfall 1
**Apply to:** the re-record + severance
The re-record, the 3 new captures, the new plant, the 2 in-place native updates and the four
legs' updated assertions must be **one commit** — `build.yml:161` `pytest tests/ -v` fires on
`push: branches: ['**','!beta']`, so any intermediate commit is CI-red.

### S-5 — Commit before running `pytest tests/`
**Source:** RESEARCH Pitfall 4; `tests/test_requirement_case_mapping_v131.py`,
`tests/test_trace_segment_exhaustiveness_v131.py`
Four legs assert `git status --porcelain` is empty after their own planted mutation, so they
redden for **any** dirty file (`assert ' M lib/jsmn/src/jsmn.h\n' == ''`). Do not conflate these
four with the four size-baseline legs.

### S-6 — Run gate-purpose `pytest tests/` from `/workspaces/firestarter`
**Source:** `tests/meta_presence.py:77-97`; RESEARCH F-12
A worktree run silently skips 32 cross-repo legs (355 vs 323+32). `FIRESTARTER_META_ROOT` is read
at **import time** — `monkeypatch.setenv` cannot move it; set it in the child environment.

### S-7 — A source-scan gate must fail closed
**Source:** the four `test_*_source_contract_*.py` modules' shared trio of self-legs
**Apply to:** the new Wave 0 module. `is_file()` + non-empty + `is_relative_to(_REPO_ROOT)` +
non-empty-after-stripping, plus the no-skip and own-needle legs. Also cited there:
`check_permitted_claims.py`'s `_HERE`-resolves-to-the-wrong-directory landmine, *"closed here by
construction"*.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| — | — | — | Every file in this phase has an in-tree analog; several are self-analogs (the file's own prior generation or its own pre-authored instruction). |

Nearest thing to a gap: **`lib/jsmn/src/jsmn.h`** has no prior *edit* precedent in this repo
(one commit, `155b02f`, vendored the whole library). The narrowing idiom is taken from Phase 157's
handle-type narrowing and the `sizeof`-assertion prohibition from `src/json_parser.c:164-275`, not
from a prior `lib/` edit. Planner should treat the vendored-file marking convention (inline
comment naming the local delta) as **derived from two surviving local modifications**, not from a
documented rule.

---

## Metadata

**Analog search scope:** `firestarter/tests/`, `firestarter/tests/fixtures/`,
`firestarter/scripts/baseline/`, `firestarter/lib/jsmn/src/`, `.planning/v1.33/`
**Files scanned:** 37 `tests/*.py` names, 4 source-contract modules (1 read in depth),
6 fixture files read in full, 2 baseline JSONs, `jsmn.h` (2 ranges), 3 `.planning/v1.33/` records
**Pattern extraction date:** 2026-08-24
