# Phase 104: Rename protocol header and .cpp files to descriptive protocol-type names - Research

**Researched:** 2026-07-02
**Domain:** Arduino/PlatformIO C++ firmware refactor (mechanical file + symbol rename, behavior-preserving)
**Confidence:** HIGH

## Summary

Phase 104 is the trailing cleanup of the v1.19 "Protocol Naming Labels" milestone. Phases 100–103
authored the operator-approved `PROTO_<NAME>` name set, relabeled the `memory.cpp` dispatch chain to
named constants, consolidated host display names, and reconciled `PROTOCOLS.md` prose. Two
minipro-heritage handler files were deliberately left with hard-to-read names — `flash_type_3.{cpp,h}`
(`configure_flash3`, dispatched for 0x06 `PROTO_FLASH_NOR_UNLOCK`) and `flash_type_4.{cpp,h}`
(`configure_flash4`, dispatched for 0x05 `PROTO_FLASH_5V_PAGE` + phantoms 0x35/0x39). Phase 104 renames
these files and their symbols to descriptive protocol-type names. `flash_intel.{cpp,h}`,
`eprom.{cpp,h}`, `sram.{cpp,h}`, `eeprom_28c.{cpp,h}`, and `not_implemented.{cpp,h}` are ALREADY
descriptive and are **out of scope** [VERIFIED: `ls firestarter/src/proms/`].

**This is a pure mechanical rename with no runtime behavior change.** Numbers stay the dispatch key
end-to-end (GATE-01); no `chip_database.json`, wire, or lockstep-constant *value* changes (GATE-02); no
CLI grammar change (GATE-03). The rename touches: 2 header files, 2 cpp files, `memory.cpp` includes,
`platformio.ini` (only if the internal function name changes — the `test_val_flash3/4` directory names
are family-ids, not filenames, so they do NOT need renaming), the host-side `test_dispatch_mirror.py`
`DOC_FILE_TO_FUNC` map (if `PROTOCOLS.md` filenames change), and `PROTOCOLS.md` itself. The misspelled
header guards (`__FALSH__TYPE_3_H__` / `__FALSH__TYPE_4_H__`) should be fixed as part of the rename.

**Primary recommendation:** Rename `flash_type_3` → `flash_nor_unlock` and `flash_type_4` →
`flash_5v_page`, aligning file basenames with the 0x06/0x05 `PROTO_` tokens; use `git mv` to preserve
history; fix the misspelled guards; and — CRITICAL — decide up front whether the internal function names
(`configure_flash3`/`configure_flash4`) ALSO rename. If they do, this becomes a **dual-repo lockstep**
change (host `check_dispatch.py`, `validation_matrix_spec.json`, `test_dispatch_mirror.py` all key on
those function-name strings). If only filenames change, only `test_dispatch_mirror.py`'s filename map is
affected. This decision belongs in `/gsd-discuss-phase` (see Open Questions Q1).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Protocol → handler dispatch | Firmware (`memory.cpp`) | — | `configure_memory()` switches on `handle->protocol`; filenames are firmware-internal |
| Handler file/symbol names | Firmware source | — | C++ file + function identifiers; never on the wire |
| Dispatch-mirror invariant | Host tests (`firestarter_app/tests/`) | Firmware doc (`PROTOCOLS.md`) | Host test parses `PROTOCOLS.md` filenames + asserts against `check_dispatch` func names |
| Wire protocol (`algorithm` int) | Firmware ↔ Host | — | Numeric protocol IDs only; UNCHANGED by this phase |

**Why this matters:** File/function names are firmware-internal legibility. The ONLY cross-repo coupling
is that the host regression tests (`test_dispatch_mirror.py`, `check_dispatch.py`,
`validation_matrix_spec.json`) hard-code either the `.cpp` filename strings or the `configure_*`
function-name strings. A rename that changes those strings without updating the host mirror trips
GATE-01. This is the one non-obvious risk of an otherwise trivial rename.

## Standard Stack

No new libraries. This is a rename within the existing PlatformIO/Arduino C++ + Unity native-test stack.

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| PlatformIO Core | 6.1.19 | Build (`pio run -e uno/leonardo`) + native test (`pio test -e native`) | Project's canonical build system [VERIFIED: `pio --version` in devcontainer] |
| Unity | (bundled via PIO) | `pio test -e native` dispatch/validation suites | Existing native test framework [VERIFIED: platformio.ini `test_framework=unity` per firestarter/CLAUDE.md] |
| `git mv` | git 2.x | Rename with history preservation | Preserves blame/log across rename |

**No package installation required** — this phase installs nothing. The Package Legitimacy Audit is
therefore N/A.

## Rename Map (authoritative basis: PROTOCOLS.md §0 + proto_constants.h)

The descriptive names derive from the operator-approved `PROTO_<NAME>` tokens (their numeric value IS
the protocol) and the PROTOCOLS.md handler-family layer.

| Old (file/symbol) | Protocol | PROTO_ token | Proposed new basename | Basis |
|-------------------|----------|--------------|-----------------------|-------|
| `flash_type_3.{cpp,h}` | 0x06 | `PROTO_FLASH_NOR_UNLOCK` | `flash_nor_unlock.{cpp,h}` | PROTOCOLS.md §1.2 "AMD/SST unlock-sequence NOR"; token `PROTO_FLASH_NOR_UNLOCK` (proto_constants.h:19) |
| `configure_flash3()` | 0x06 | — | `configure_flash_nor_unlock()` | matches file basename; see Open Q1 |
| `flash_type_4.{cpp,h}` | 0x05 (+0x35/0x39) | `PROTO_FLASH_5V_PAGE` | `flash_5v_page.{cpp,h}` | PROTOCOLS.md §1.1 "5V page-write (EEPROM-like)"; token `PROTO_FLASH_5V_PAGE` (proto_constants.h:18) |
| `configure_flash4()` | 0x05 | — | `configure_flash_5v_page()` | matches file basename; see Open Q1 |

> **Naming caution (name-vs-number in the header guard):** `proto_constants.h:31-37` explicitly warns
> NOT to "fix" `PROTO_PHANTOM_0x35`/`0x39` — the `0x35`/`0x39` substrings are literal identifier text.
> That caution does NOT apply to the flash3/flash4 file rename (there is no numeric substring in
> `flash_nor_unlock`/`flash_5v_page`), but the planner should mirror that "the label reflects the
> protocol, and the numeric value is unchanged" discipline.

**Out-of-scope files (already descriptive — confirmed):** `flash_intel.{cpp,h}` (0x10),
`eprom.{cpp,h}` (0x07/0x08/0x0B), `sram.{cpp,h}` (0x0E/0x27/0x28/0x29), `eeprom_28c.{cpp,h}` (0x0D),
`not_implemented.{cpp,h}` (0x34 + infeasible), `flash_utils.{cpp,h}` (shared helpers), `memory.{cpp,h}`
[VERIFIED: `ls firestarter/src/proms include/`, all present with descriptive names, none contain the
"type N" pattern].

## Full Reference Inventory

Every place the old names appear (grep-verified 2026-07-02 across `firestarter/`).

### A. `flash_type_3` / `configure_flash3` (0x06)

| File:line | Reference | Rename action |
|-----------|-----------|---------------|
| `include/flash_type_3.h` (file) | header file itself | `git mv` → `flash_nor_unlock.h` |
| `include/flash_type_3.h:8-9,22` | guard `__FALSH__TYPE_3_H__` (MISSPELLED) | rewrite guard → `__FLASH_NOR_UNLOCK_H__` |
| `include/flash_type_3.h:16` | `void configure_flash3(...)` decl | rename if func renamed (Q1) |
| `src/proms/flash_type_3.cpp` (file) | cpp file itself | `git mv` → `flash_nor_unlock.cpp` |
| `src/proms/flash_type_3.cpp:8` | `#include "flash_type_3.h"` | update include path |
| `src/proms/flash_type_3.cpp:17-135` | `flash3_*` internal fns + `configure_flash3` (lines 17,18,19,20,21,23,25,31,33,36,37,40,48,53,55,60,64,71,74,82,96,108,111,118,131,135) | rename `configure_flash3` (Q1); `flash3_*` static helpers = optional cosmetic (Q2) |
| `src/proms/memory.cpp:14` | `#include "flash_type_3.h"` | update include path |
| `src/proms/memory.cpp:86,130` | `configure_flash3(handle);` call | rename if func renamed (Q1) |
| `include/flash_utils.h:65` | comment "Used by flash_type_3 and flash_type_4" | update comment text |
| `src/proms/flash_utils.cpp:80` | comment "Used by flash3 and flash4" | update comment text |
| `test/native/avr/test_val_flash3/test_val_flash3.cpp` | comments + test fn names referencing `configure_flash3`/`flash3` (lines 10,15,19,24,84,90,94,100,104,110,114,120,128-131) | update comments; rename `configure_flash3` refs if func renamed (Q1) |
| `test/native/avr/test_dispatch/test_configure_memory.cpp:71,166,203` | `test_protocol_0x06_dispatches_flash3` + comment | update if func/family renamed |
| `test/native/avr/_shared/validation_matrix.h:21` | `{ 0x06, "flash3", "configure_flash3" }` | **GENERATED FILE — do NOT hand-edit**; regenerate via host `tools/gen_validation_header.py` after editing `tools/validation_matrix_spec.json` (Q1 lockstep) |
| `platformio.ini:91,109` | `native/avr/test_val_flash3` (test_filter + `-I`) | rename ONLY if the test *directory* is renamed (optional — it's a family-id, not a filename) |
| `doc/PROTOCOLS.md:46,66,67,104,113,356,419` | handler-family table + prose + INV-09 | update `flash_type_3.cpp`→new file; `configure_flash3()`→new fn if renamed (Q1) |

### B. `flash_type_4` / `configure_flash4` (0x05 + phantoms)

| File:line | Reference | Rename action |
|-----------|-----------|---------------|
| `include/flash_type_4.h` (file) | header file itself | `git mv` → `flash_5v_page.h` |
| `include/flash_type_4.h:8-9,22` | guard `__FALSH__TYPE_4_H__` (MISSPELLED) | rewrite guard → `__FLASH_5V_PAGE_H__` |
| `include/flash_type_4.h:16` | `void configure_flash4(...)` decl | rename if func renamed (Q1) |
| `src/proms/flash_type_4.cpp` (file) | cpp file itself | `git mv` → `flash_5v_page.cpp` |
| `src/proms/flash_type_4.cpp:8` | `#include "flash_type_4.h"` | update include path |
| `src/proms/flash_type_4.cpp:27-145` | `flash4_*` internal fns + `configure_flash4` | rename `configure_flash4` (Q1); `flash4_*` static helpers = optional cosmetic (Q2) |
| `src/proms/memory.cpp:15` | `#include "flash_type_4.h"` | update include path |
| `src/proms/memory.cpp:91,133` | `configure_flash4(handle);` call | rename if func renamed (Q1) |
| `test/native/avr/test_val_flash4/test_val_flash4.cpp` | ~30 refs to `configure_flash4`/`flash4_*` (see grep in phase notes) | update comments; rename `configure_flash4` refs if func renamed (Q1) |
| `test/native/avr/test_dispatch/test_configure_memory.cpp:77-224` | `test_protocol_0x05/0x35/0x39_dispatches_flash4` + `configure_flash4` comments | update if func/family renamed |
| `test/native/avr/_shared/validation_matrix.h:22` | `{ 0x05, "flash4", "configure_flash4" }` | **GENERATED** — regenerate (see above) |
| `platformio.ini:92,110` | `native/avr/test_val_flash4` | rename ONLY if test dir renamed (optional) |
| `doc/PROTOCOLS.md:45,57,58,66,84,96,356,405,414` | handler-family table + §1.1 prose + INV-04 + phantom §2.1 | update `flash_type_4.cpp`→new file; `configure_flash4()`→new fn if renamed (Q1) |

### C. Host-app cross-repo references (firestarter_app) — LOCKSTEP SURFACE

| File:line | Reference | Kind |
|-----------|-----------|------|
| `firestarter_app/tests/test_dispatch_mirror.py:75-76` | `DOC_FILE_TO_FUNC = {"flash_type_4.cpp": "configure_flash4", "flash_type_3.cpp": "configure_flash3", ...}` | Maps **filename → function**; parses `PROTOCOLS.md` handler-family table (regex `_FAMILY_ROW_RE`). **Breaks if PROTOCOLS.md `.cpp` filename or the func name changes and this dict is not updated in lockstep.** |
| `firestarter_app/tools/check_dispatch.py:81-82,140,142,155-156` | `configure_flash3`/`configure_flash4` returned by `dispatch()` + `_FAMILY_VPP_INVARIANTS` keys | Keys on **function names only** (not filenames). Breaks ONLY if function names change (Q1). |
| `firestarter_app/tools/validation_matrix_spec.json` | `"handler": "configure_flash3/4"` (source for generated `validation_matrix.h`) | Function names; breaks only if func renamed. |
| `firestarter_app/tests/test_check_dispatch_invariants.py:112-113` | expects `configure_flash3`/`configure_flash4` in `_FAMILY_VPP_INVARIANTS` | Function names. |
| `firestarter_app/doc/protocol-id.md:17-18`, `infoic-field-dictionary.md:79-80` | doc tables listing `configure_flash4`/`configure_flash3` | Doc references (function names). |
| `firestarter_app/val-results/flash3/validation-matrix.{md,json}` | historical bench notes ("configure_flash3 erase+write PASS") | **Historical artifacts — do NOT rewrite** (they record what was run at the time). |

**Decision axis:** If Phase 104 renames **filenames only** and keeps `configure_flash3`/`configure_flash4`
function names, the only host file that must change is `test_dispatch_mirror.py` (its `DOC_FILE_TO_FUNC`
keys are `.cpp` filenames). If Phase 104 ALSO renames the **functions**, then `check_dispatch.py`,
`validation_matrix_spec.json`, `test_check_dispatch_invariants.py`, and the two host doc tables must all
change too — and this becomes a full dual-repo lockstep commit-pair.

## Host Lockstep Verdict

**Firmware-primary, with a REQUIRED host-test lockstep leg.** The wire protocol is unaffected — only the
`algorithm` integer flows on the wire, and no numeric value changes (GATE-01/02). BUT the claim "the host
does NOT reference these C++ names" is **FALSE** [VERIFIED: grep of `firestarter_app`]. The host's
dispatch-mirror regression tests and the validation-matrix generator hard-code the `.cpp` filename
strings (`test_dispatch_mirror.py`) and/or the `configure_flash3/4` function-name strings
(`check_dispatch.py`, `validation_matrix_spec.json`). These are **test/tooling references, not wire
references** — but they are exactly the GATE-01 dispatch-mirror guard, so they must move in lockstep or
the guard fails.

**Planner implication:** This phase is dual-repo (firestarter + firestarter_app) at the *test/tooling*
layer, matching the v1.19 lockstep pattern (STATE.md:64). Plan a commit-pair; keep gitlinks PINNED per
milestone convention.

## Common Pitfalls

### Pitfall 1: Dispatch-mirror guard breaks if PROTOCOLS.md filename / host map drift
**What goes wrong:** `test_dispatch_mirror.py` parses `firestarter/doc/PROTOCOLS.md` handler-family table
(`_FAMILY_ROW_RE` matches `` `<file>.cpp` ``) and joins it to `DOC_FILE_TO_FUNC`. If PROTOCOLS.md says
`flash_nor_unlock.cpp` but `DOC_FILE_TO_FUNC` still says `flash_type_3.cpp`, the join yields `None` and
the test fails.
**How to avoid:** Update PROTOCOLS.md (handler-family table lines 66-67 + §1.1/§1.2 handler lines) AND
`DOC_FILE_TO_FUNC` (lines 75-76) in the same change. Run `pytest firestarter_app/tests/test_dispatch_mirror.py`.
**Warning sign:** `parse_protocols_md() returned an empty table` or `doc says X but ... returned Y`.

### Pitfall 2: validation_matrix.h is generated — hand-editing gets clobbered
**What goes wrong:** `test/native/avr/_shared/validation_matrix.h` says `/* DO NOT EDIT -- generated by
tools/gen_validation_header.py */`. Its `handler_name` field ("configure_flash3") comes from the host's
`tools/validation_matrix_spec.json`. Hand-editing the `.h` will be overwritten on next regen; editing
only the `.h` and not the spec leaves them inconsistent.
**How to avoid:** If function names change (Q1), edit `firestarter_app/tools/validation_matrix_spec.json`
then re-run `python tools/gen_validation_header.py` to emit the new `.h`. If only filenames change, this
file needs no edit (it carries family-id + function-name, not filenames).
**Warning sign:** validation_matrix.h and spec disagree; native `test_val_*` build errors.

### Pitfall 3: Stale `.pio` build artifacts after rename
**What goes wrong:** PlatformIO caches object files keyed by source path. After `git mv`, a stale
`flash_type_3.o` may linger or a ghost dependency edge may cause a confusing incremental-build error.
**How to avoid:** Run `pio run -t clean` (or delete `.pio/build`) before the verification build.
**Warning sign:** Linker errors referencing the old object name, or "file not found" for old header.

### Pitfall 4: Header-guard collision / stale guard
**What goes wrong:** The current guards are misspelled `__FALSH__TYPE_3_H__` / `__FALSH__TYPE_4_H__`. If
you rename the file but forget to rewrite the guard, you keep the misspelling; if two renamed files
accidentally share a guard macro, one file's contents get skipped (silent, dangerous).
**How to avoid:** Rewrite each guard to a unique correct token derived from the new basename
(`__FLASH_NOR_UNLOCK_H__`, `__FLASH_5V_PAGE_H__`). Grep post-rename: `grep -rn FALSH firestarter/` must
return nothing.
**Warning sign:** Redefinition or missing-symbol errors; leftover `FALSH` in grep.

### Pitfall 5: `git mv` vs delete+add (history loss)
**What goes wrong:** Recreating the file (Write new + delete old) loses `git log --follow` history and
blame continuity for a file that carries the flash3/flash4 algorithm heritage.
**How to avoid:** Use `git mv old new`, THEN edit contents (include path, guard, symbols). Git detects
the rename when the content overlap is high.
**Warning sign:** `git status` shows separate "deleted" + "new file" instead of "renamed".

### Pitfall 6: MIT license header
**What goes wrong:** Dropping the `/* Project Name: Firestarter ... MIT license */` block (lines 1-6 of
each file) during the rewrite.
**How to avoid:** Preserve the copyright/license header verbatim in both renamed files.

### Pitfall 7: platformio.ini test-dir names are family-ids, not filenames (do NOT over-rename)
**What goes wrong:** Renaming the `test/native/avr/test_val_flash3` directory (and its 6 `platformio.ini`
references at lines 81-112) is NOT required — those are validation-family suite names (matching the
`family_id` "flash3"/"flash4" in validation_matrix.h), not source filenames. Renaming them expands blast
radius and touches the SAFE-02 INV suite-path contract (PROTOCOLS.md §3 maps INV-04 → `test_val_flash4/`,
INV-09 → `test_val_flash3/`).
**How to avoid:** Scope the rename to source files + symbols. Leave `test_val_flash3/4` directory names
alone unless the operator explicitly wants the family-id renamed too (that would be a larger change
touching the INV traceability matrix). Surface as Open Q2.

## Runtime State Inventory

This is a source-rename phase (no stored data, no live services, no OS state). Explicit findings:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no DB keys, collection names, or persisted IDs reference these C++ filenames. `chip_database.json` keys on `algorithm` integers only (GATE-02 identity). | none |
| Live service config | None — no external service references firmware source filenames. | none |
| OS-registered state | None — no task/service names embed `flash_type_3/4`. | none |
| Secrets/env vars | None — no env var or secret name references these files. | none |
| Build artifacts | `.pio/build/*/flash_type_3.o`, `flash_type_4.o` become stale after rename. Also the **generated** `test/native/avr/_shared/validation_matrix.h` (regen via host `gen_validation_header.py` if function names change). | `pio run -t clean`; regen validation_matrix.h if Q1=rename-functions |

**The canonical question — "after every file is updated, what runtime systems still have the old string
cached?"** Answer: only the PlatformIO object cache (`.pio/`) and the generated `validation_matrix.h`.
Both are addressed by a clean build + (conditional) header regen. No wire/DB/service state carries these
names.

## Verification / Gates

The three v1.19 gates apply to this rename. How to run each in THIS devcontainer:

| Gate | What it proves | How to run here | Availability |
|------|----------------|-----------------|--------------|
| **GATE-01** (dispatch-mirror + golden traces) | Numbers stay the dispatch key; dispatch order unchanged; the three-way doc↔tool↔firmware bind holds | `pio test -e native` (all native suites, 82/82 expected); `pytest firestarter_app/tests/test_dispatch_mirror.py` | `pio` PRESENT (6.1.19) → REAL executed PASS possible. `pytest` for host leg: run in firestarter_app venv. |
| **GATE-02** (`diff_db.py` DB identity + constants-parity) | No `chip_database.json` value change; no wire/lockstep-constant value change | `python firestarter_app/tools/diff_db.py` (identity); constants-parity test. NOTE: this rename touches NO DB/constants — GATE-02 is trivially held (no `chip_database.json` or `constants.py`/`firestarter.h` edit). | `diff_db.py` runnable under py3.12; the py3.11-target constants-parity CI leg is CI-PENDING (no python3.11 binary here — Phase 98/103 precedent, STATE.md:39,183). |
| **GATE-03** (no CLI grammar change) | Chip selection stays by part number; no protocol name accepted as CLI input | Confirm no `cli_handlers.py`/argparse/Click grammar edit; this phase touches only firmware source + tests. Trivially held. | Static confirmation; no run needed. |

**Precedent (STATE.md:37,183):** GATE-01 firmware leg (`pio test -e native`) is a REAL PASS this session
because `pio` is present. The GATE-02 constants-parity py3.11-target leg records **CI-PENDING** (never a
fabricated PASS for an absent tool) — but note this rename does not touch constants at all, so the
constants-parity concern is even weaker than in Phase 101/103.

**Behavior-preservation proof for a pure rename:** (1) `pio test -e native` green (dispatch + all
`test_val_*` suites unchanged behavior); (2) `pio run -e uno` and `pio run -e leonardo` both compile
(link resolves renamed symbols); (3) host `test_dispatch_mirror.py` green (doc↔tool↔firmware bind intact);
(4) grep shows zero surviving `flash_type_3`/`flash_type_4`/`FALSH` tokens except intentionally-retained
historical bench artifacts.

## Suggested Requirement IDs

The phase is an appended stub with no formal REQUIREMENTS.md entries. Suggested `RENAME-*` set the
planner can adopt (traceable to the v1.19 GATE non-regression contract):

| ID | Description |
|----|-------------|
| RENAME-01 | `flash_type_3.{cpp,h}` renamed to a descriptive basename derived from `PROTO_FLASH_NOR_UNLOCK` (0x06); include sites + header guard updated; MIT header + history preserved (`git mv`). |
| RENAME-02 | `flash_type_4.{cpp,h}` renamed to a descriptive basename derived from `PROTO_FLASH_5V_PAGE` (0x05); include sites + header guard updated; MIT header + history preserved. |
| RENAME-03 | Misspelled header guards (`__FALSH__TYPE_3/4_H__`) corrected to spelled-correct unique tokens matching the new basenames. |
| RENAME-04 | `configure_flash3`/`configure_flash4` function-name disposition applied consistently (rename or keep — see Open Q1) across firmware + host lockstep surface (`check_dispatch.py`, `validation_matrix_spec.json`, `test_dispatch_mirror.py`, host doc tables) as decided. |
| RENAME-05 | `PROTOCOLS.md` handler-family table + §1.1/§1.2/§2.1/§3(INV-04,INV-09) file/function references updated to new names; DOC-02 slug divergence record unaffected. |
| GATE-01/02/03 | (carried) Non-regression — `pio test -e native` green, host dispatch-mirror green, `diff_db.py` identity, no CLI grammar change. |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| PlatformIO Core | `pio run` / `pio test -e native` (GATE-01 firmware leg) | ✓ | 6.1.19 | — |
| python3 | host tools (`diff_db.py`, `gen_validation_header.py`) + host pytest | ✓ | 3.12.13 | — |
| python3.11 | constants-parity CI-target leg (GATE-02) | ✗ | — | Record CI-PENDING (Phase 98/103 precedent); this phase touches no constants so it is a weak leg |
| git | `git mv` history-preserving rename | ✓ | 2.x | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** python3.11 → GATE-02 constants-parity CI-target leg recorded
CI-PENDING (structurally green under py3.12); acceptable per established precedent and because this phase
makes zero constants edits.

## Validation Architecture

`nyquist_validation` is absent from `.planning/config.json` `workflow` block → treated as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Unity (via PlatformIO `[env:native]`) + pytest (host) |
| Config file | `firestarter/platformio.ini` (`[env:native]`, `test_framework=unity`); `firestarter_app` pytest |
| Quick run command | `pio test -e native -f "*test_dispatch*"` |
| Full suite command | `pio test -e native` (all native suites) + `pytest firestarter_app/tests/test_dispatch_mirror.py firestarter_app/tests/test_check_dispatch_invariants.py` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RENAME-01/02 | renamed files still compile + link, dispatch unchanged | build + native | `pio run -e uno && pio run -e leonardo && pio test -e native` | ✅ (existing dispatch + val suites) |
| RENAME-03 | no surviving misspelled/old guard | grep smoke | `! grep -rn "FALSH\|flash_type_3\|flash_type_4" firestarter/src firestarter/include` | ✅ (grep) |
| RENAME-04 | function-name disposition consistent; dispatch-mirror holds | host pytest | `pytest firestarter_app/tests/test_dispatch_mirror.py firestarter_app/tests/test_check_dispatch_invariants.py` | ✅ |
| RENAME-05 | doc↔tool↔firmware bind intact | host pytest | `pytest firestarter_app/tests/test_dispatch_mirror.py` | ✅ |
| GATE-02 | DB identity | host | `python firestarter_app/tools/diff_db.py` | ✅ |

### Sampling Rate
- **Per task commit:** `pio test -e native -f "*test_dispatch*"` (fast dispatch sanity)
- **Per wave merge:** `pio test -e native` full + host `pytest` dispatch-mirror suites
- **Phase gate:** `pio run -e uno` + `pio run -e leonardo` compile green + full native + host mirror green before `/gsd-verify-work`

### Wave 0 Gaps
None — existing test infrastructure (native dispatch/val suites + host dispatch-mirror + validation
generator) fully covers a behavior-preserving rename. No new test files needed. If the function names are
renamed (Q1), the existing tests are UPDATED (string substitution), not newly authored.

## Security Domain

`security_enforcement` is not disabled in config (absent = enabled), but this phase is a mechanical
source rename with **no security-relevant surface**: no input validation, auth, session, crypto, or
access-control code is added or changed. No `algorithm`/wire/VPP behavior changes (the VPP-hazard
fail-closed invariants in `memory.cpp` steps 6a/6b are untouched). ASVS categories V2–V6 do not apply to
an identifier rename. The one safety-adjacent invariant — that SRAM/flash 5V handlers never assert the
12V VPP regulator — is preserved by construction (no handler *logic* changes) and re-proven by the
unchanged `test_val_flash3`/`test_val_flash4` VPP-safety suites.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Proposed basenames `flash_nor_unlock` / `flash_5v_page` are the right descriptive names | Rename Map | LOW — names derive directly from operator-approved PROTO_ tokens; operator confirms exact spelling in discuss-phase (Q1/Q3) |
| A2 | Function names `configure_flash3/4` MAY stay unchanged (only files rename) | Host Lockstep / Q1 | MEDIUM — determines whether host `check_dispatch.py`/`validation_matrix_spec.json` are in scope; must be an explicit operator decision |
| A3 | `test_val_flash3/4` directory names should NOT be renamed | Pitfall 7 / Q2 | MEDIUM — renaming them touches the SAFE-02 INV suite-path contract (PROTOCOLS.md §3) |

## Open Questions

1. **Do the internal handler FUNCTIONS rename too, or only the files?**
   - What we know: `configure_flash3`/`configure_flash4` are referenced by the host `check_dispatch.py`,
     `validation_matrix_spec.json`, `test_check_dispatch_invariants.py`, host doc tables, AND
     `test_dispatch_mirror.py` (which also keys on the `.cpp` filenames). FW-03 in REQUIREMENTS.md
     (already marked Complete) lists `configure_flash3`/`flash_type_3.cpp` as the *family-layer* names —
     ambiguously implying the current names were the intended target, yet Phase 104 exists precisely to
     replace the "type N" naming.
   - What's unclear: Whether "descriptive protocol-type names" means files-only, or files + functions.
   - Recommendation: **Rename both files AND functions** for full legibility (`configure_flash_nor_unlock`,
     `configure_flash_5v_page`), and treat the host references as a required lockstep leg. Confirm with
     operator in `/gsd-discuss-phase` — this is the single decision that sets the phase's blast radius.

2. **Rename the `test_val_flash3` / `test_val_flash4` suite directories + `family_id` too?**
   - What we know: These are validation-family names (family_id "flash3"/"flash4"), wired in
     `platformio.ini` (6 refs) and the SAFE-02 INV suite-path contract (PROTOCOLS.md §3: INV-04 →
     `test_val_flash4/`, INV-09 → `test_val_flash3/`).
   - What's unclear: Whether operator wants the family-id relabeled or only the source files.
   - Recommendation: **Leave suite dirs + family-ids as-is** (out of scope) to keep the SAFE-02 contract
     stable; a family-id rename is a separately-scoped change. Flag for operator to confirm.

3. **Exact target spelling.** Confirm `flash_nor_unlock` vs `flash_amd_unlock` vs `flash6`-style, and
   `flash_5v_page` vs `flash_page_write`. Recommendation: derive verbatim from the PROTO_ token stem
   (`PROTO_FLASH_NOR_UNLOCK` → `flash_nor_unlock`; `PROTO_FLASH_5V_PAGE` → `flash_5v_page`) for a
   mechanical, defensible mapping.

## Sources

### Primary (HIGH confidence)
- `firestarter/doc/PROTOCOLS.md` (operator-approved name set, §0 handler-family table, §1.1/§1.2, §3 INV matrix) — authoritative naming basis [VERIFIED: Read]
- `firestarter/include/proto_constants.h` (PROTO_ tokens, lines 18-19) [VERIFIED: Read]
- `firestarter/src/proms/memory.cpp` (dispatch chain lines 75-135) [VERIFIED: Read]
- `firestarter/CLAUDE.md` (dispatch-order source-of-truth, handler table, native test layout) [VERIFIED: Read]
- Grep inventory across `firestarter/` and `firestarter_app/` [VERIFIED: 2026-07-02 grep runs]
- `firestarter_app/tests/test_dispatch_mirror.py`, `tools/check_dispatch.py`, `test/native/avr/_shared/validation_matrix.h` [VERIFIED: Read]
- `.planning/REQUIREMENTS.md` (FW-03, GATE-01/02/03), `.planning/STATE.md` (v1.19 close, gate history), `.planning/config.json` (sub_repos, workflow) [VERIFIED: Read]

### Secondary (MEDIUM confidence)
- Environment probes: `pio --version` (6.1.19), `python3 --version` (3.12.13), python3.11 absent [VERIFIED: devcontainer]

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Rename map: HIGH — derived directly from operator-approved PROTO_ tokens + PROTOCOLS.md
- Reference inventory: HIGH — exhaustive grep across both repos, file:line verified
- Host lockstep verdict: HIGH — host references directly read (corrects the "no host refs" assumption)
- Gates/verification: HIGH — `pio` present + gate mechanics confirmed against STATE.md precedent
- Function-rename scope: MEDIUM — requires operator decision (Q1)

**Research date:** 2026-07-02
**Valid until:** 2026-08-01 (stable — mechanical rename in a closed-milestone cleanup; low churn)
