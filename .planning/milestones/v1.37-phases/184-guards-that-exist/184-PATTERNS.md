# Phase 184: Guards That Exist - Pattern Map

**Mapped:** 2026-09-11
**Files analyzed:** 10 (1 created, 7 modified, 2 deleted)
**Analogs found:** 10 / 10

All analog paths below were verified git-TRACKED in their own repository
(`git ls-files` non-empty, run inside `/workspaces`, `/workspaces/firestarter_app`,
`/workspaces/firestarter` respectively). No path here is a gitignored mirror.

---

## HARD PROJECT RULE — read before using any excerpt below

`/workspaces/CLAUDE.md` § "Source code comments — hard rule": **no comments may be
written into product source** under `firestarter/` or `firestarter_app/`. Not
overridable by a plan, task, skill, or subagent instruction.

Several analogs in this document are heavily commented and/or docstring-dense
(`scan_paths.py`, `check_no_exists_proxy.py`, the two `planted_dispatch_*.cpp`
fixtures, `test_configure_memory.cpp`). **Their comments are pre-existing. Presenting
them here is NOT licence to author new ones.** Concretely:

- **C++ site (`test_configure_memory.cpp:200-202`)** — the only permitted operation is
  **deleting the false clause**. Authoring replacement prose is unavailable. If the
  clause cannot be removed without writing new prose, leave it and record the deviation
  in the plan's `SUMMARY.md` (D-10).
- **Python sites** — module docstrings and test docstrings are the established carrier
  in this suite; edits to `scan_paths.py` / `test_scan_paths_resolve.py` /
  `check_no_exists_proxy.py` / `planted_no_exists_proxy.py` go in **docstrings**, and
  the new CLAIM-09 test carries its rationale in its own docstring and assertion
  message — not in `#` comments. Note `planted_no_exists_proxy.py:40-42` is a `#`
  comment carrying one of D-02's citations; re-dating existing prose in place is an
  edit to an existing comment, not authoring a new one.
- **Markdown** (`PROTOCOLS.md`, `.planning/notes/*`, meta `CLAUDE.md`) is outside the
  rule entirely (D-09 states this explicitly).

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `firestarter_app/tests/test_scan_paths_resolve.py` — new 5th test (CLAIM-09, D-11/D-12) | test | transform (in-repo data → assertion) | `test_all_eleven_tool_resolvers_exist`, same file :143-159 | **exact** (same file, same population idiom) |
| `firestarter_app/tests/test_scan_paths_resolve.py` — `_FLOOR` re-anchor + docstring (D-15) | test | transform | `_FLOOR` :43-47 + `test_inventory_is_non_vacuous` :94-106 (self) | exact (edit in place) |
| `firestarter_app/tests/scan_paths.py` — remove entry :112-115, fix "8 paths" docstring (D-14/D-15) | config/data module | transform | self; sibling entries :98-131 are the target shape | exact |
| `firestarter_app/tools/check_no_exists_proxy.py:19` — re-date citation (D-02) | utility (lint) | file-I/O (AST scan) | `planted_no_exists_proxy.py:20` (the paired citation) | exact |
| `firestarter_app/tests/fixtures/planted_no_exists_proxy.py:20,41` — re-date citations (D-02) | test fixture | n/a (scan input) | `check_no_exists_proxy.py:19` | exact |
| `firestarter_app/tests/fixtures/planted_dispatch_comment_only_hex.cpp` — **DELETE** (D-07) | test fixture | n/a | no analog needed; knowledge migrates to the verdict note | n/a |
| `firestarter_app/tests/fixtures/planted_dispatch_missing_hex.cpp` — **DELETE** (D-07) | test fixture | n/a | same | n/a |
| `firestarter/PROTOCOLS.md:11-13` — paragraph → one honest line (D-09) | doc (prose) | n/a | meta `CLAUDE.md:12` "**no automated wiki guard exists now**" | exact (D-09 names it as the precedent) |
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:201` — delete false clause (D-10) | test (C++, comment only) | n/a | none — deletion only, no pattern to copy | **deliberately none** |
| `.planning/notes/<verdict>.md` — **NEW** (CLAIM-03, D-08/D-16) | doc (verdict record) | n/a | `ae29f2008-classification-verdict.md` (183) + `jumper-display-ground-truth.md` (182) | exact (both named in D-08) |
| `/workspaces/CLAUDE.md:12` — repair the `tools/wiki/` claim (D-04) | doc (project instructions) | n/a | the same sentence's own second half | exact (one-line repair) |

---

## Pattern Assignments

### `firestarter_app/tests/test_scan_paths_resolve.py` — new CLAIM-09 test (test, transform)

**Analog:** `firestarter_app/tests/test_scan_paths_resolve.py:143-159` —
`test_all_eleven_tool_resolvers_exist`. Same file, same inventory, Population B's
existing precedent for exactly the check Population A lacks.

**Imports pattern** (lines 30-50, already present — the new test adds nothing but
possibly a name to the existing `from tests.scan_paths import (...)` tuple):

```python
from __future__ import annotations

from pathlib import Path

from tests.fw_presence import requires_fw
from tests.scan_paths import (
    ALL_CROSS_REPO_PATHS,
    CROSS_REPO_TEST_PATHS,
    CROSS_REPO_TOOL_RESOLVERS,
    SAME_REPO_LOOKALIKES,
    resolve_scan_path,
)

_FLOOR = 6

_APP_REPO_ROOT = Path(__file__).resolve().parent.parent
_TOOLS_DIR = _APP_REPO_ROOT / "tools"
```

Note: the new test needs a `tests/` directory constant analogous to `_TOOLS_DIR`
(e.g. `_TESTS_DIR = _APP_REPO_ROOT / "tests"`, or simply `Path(__file__).resolve().parent`).
Build it the same way `_TOOLS_DIR` is built — from `_APP_REPO_ROOT`, not from a new
independent derivation.

**Core pattern to copy — collect-then-assert-once** (lines 143-159). Copy the shape of
the `missing_tools` comprehension and the single terminal assertion:

```python
def test_all_eleven_tool_resolvers_exist() -> None:
    """Every tool file named in CROSS_REPO_TOOL_RESOLVERS must exist in
    tools/, so a renamed or deleted tool is caught rather than silently
    dropping its paths from the inventory -- population B coverage."""
    assert len(CROSS_REPO_TOOL_RESOLVERS) == 11, (      # <-- DO NOT COPY (see below)
        f"expected exactly 11 tool-resolver entries, found "
        f"{len(CROSS_REPO_TOOL_RESOLVERS)}"
    )
    missing_tools = [
        tool_entry.tool
        for tool_entry in CROSS_REPO_TOOL_RESOLVERS
        if not (_TOOLS_DIR / tool_entry.tool).is_file()
    ]
    assert not missing_tools, (
        f"the following tools named in CROSS_REPO_TOOL_RESOLVERS no longer "
        f"exist in {_TOOLS_DIR}: {missing_tools}"
    )
```

Elements that transfer:
1. `not (<dir> / <name>).is_file()` as the existence predicate (`is_file`, not `exists`).
2. List-comprehension **collect**, then **one** assertion — never fail-on-first.
3. Failure message names **every** offending item at once, plus the directory it was
   looked for in, so the message states the fix and not just the symptom.
4. Docstring states what defect the test catches and which population it covers.

**ANTI-PATTERN — explicitly NOT copied:** the `assert len(...) == 11` census arm at
line 147-150. CONTEXT.md § Reusable Assets and D-15 both name it: a hardcoded census
goes stale on every legitimate removal. The new test gets **no** count assertion; the
non-vacuity job already belongs to `test_inventory_is_non_vacuous` and its `_FLOOR`.
(The identical anti-pattern also exists at module scope in `scan_paths.py:250-254` —
out of scope for this phase, do not sweep it.)

**Iteration pattern already proven** (lines 53-63) — `_resolvers_for` already walks
`entry.resolved_by`; the new test iterates the same field:

```python
def _resolvers_for(fw_relative_path: str) -> tuple[str, ...]:
    """Every test module and/or tool file that resolves `fw_relative_path`,
    for a failure message that names the fix, not just the symptom."""
    resolvers: list[str] = []
    for entry in CROSS_REPO_TEST_PATHS:
        if entry.fw_relative_path == fw_relative_path:
            resolvers.extend(entry.resolved_by)
```

**Failure-message pattern for a per-entry (not per-path) failure** (lines 76-91) — when
the offending item must be reported *with* the entry it came from, copy this shape,
which pairs each offender with its context and joins on newlines:

```python
    missing: list[str] = []
    for fw_relative_path in ALL_CROSS_REPO_PATHS:
        resolved = resolve_scan_path(fw_relative_path)
        if not resolved.exists():
            resolvers = _resolvers_for(fw_relative_path)
            missing.append(
                f"{fw_relative_path} (resolved: {resolved}) -- resolved by: "
                f"{', '.join(resolvers) or 'unknown'}"
            )

    assert not missing, (
        "The following cross-repo scan path(s) do not resolve -- the "
        "firmware repo IS present, so this is a rename or move, not an "
        "absence. Update the path in tests/scan_paths.py (or the resolving "
        "module/tool) to match:\n" + "\n".join(f"  - {m}" for m in missing)
    )
```

For D-11 the reported item is `(entry.fw_relative_path, resolver_string)` — a
`resolved_by` value that is not a bare filename, or is a bare filename that is not
`is_file()` under `tests/`, is reported with the `fw_relative_path` entry that carries it.

**Marker pattern — and the D-11 reason it must NOT be used here.** Three of the four
existing tests are unmarked; only `test_all_cross_repo_paths_resolve` carries
`@requires_fw` (line 66), because it touches the sibling repo. The new test resolves
only `firestarter_app/tests/`, which is always present, so it is **unmarked** — exactly
D-11's argument: a cross-repo resolver would degrade to a skip in app CI, which is the
fail-open mode CLAIM-09 exists to close. Do not decorate the new test.

---

### `firestarter_app/tests/test_scan_paths_resolve.py` — `_FLOOR` re-anchor (D-15)

**Analog:** the constant and its consumer in the same file.

**Current state** (lines 43-47) — the census justification D-15 replaces:

```python
# Floor equal to what actually ships (measured at plan time): 6 population-A
# test paths, the deduplicated union of population A + the genuinely
# cross-repo subset of population B. An emptied or mis-globbed inventory
# must fail this, not pass silently.
_FLOOR = 6
```

**Both assertions are in scope** (lines 94-106) — `test_inventory_is_non_vacuous`
asserts the floor twice; after D-14 both populations are 6:

```python
    assert len(ALL_CROSS_REPO_PATHS) >= _FLOOR, (...)
    assert len(CROSS_REPO_TEST_PATHS) >= _FLOOR, (...)
```

The value stays **6**; only the justification changes — from "measured at plan time"
to why the inventory cannot be doing its job below that count, plus the note that a
deliberate removal must move the floor deliberately. The module docstring's
"Four tests" (line 10) and its numbered list (lines 13-27) need a fifth entry.

---

### `firestarter_app/tests/scan_paths.py` — entry removal + docstring correction (D-14, D-15)

**Analog:** its own sibling entries. The exact entry D-13/D-14 removes (lines 112-115):

```python
    ScanPathEntry(
        "test/native/avr/test_dispatch/test_configure_memory.cpp",
        ("tools/wiki/dispatch_mirror.py (meta repo; relocated by 168-10)",),
    ),
```

**The `resolved_by` field shape D-11 constrains** (lines 88-94):

```python
@dataclass(frozen=True)
class ScanPathEntry:
    """One cross-repo path, relative to the sibling firmware repo root, and
    the test module(s) that resolve it."""

    fw_relative_path: str
    resolved_by: tuple[str, ...]
```

**The uniform shape every surviving entry already has** (lines 98-131) — bare
`tests/` filenames, one or two per entry:

```python
CROSS_REPO_TEST_PATHS: tuple[ScanPathEntry, ...] = (
    ScanPathEntry(
        "include/firestarter.h",
        (
            "test_revision_constants_parity.py",
            "test_check_is_memory_cmd_no_ifdef.py",
        ),
    ),
    ...
    ScanPathEntry(
        "src/json_parser.c",
        ("test_json_key_parity.py",),
    ),
)
```

The removed entry is the **only** non-conforming one — it is the sole annotated,
cross-repo-pathed string in the tuple. That uniformity is what makes D-11's check
land green on the first run after the removal.

**Stale docstring figure (D-15)** — lines 29-34 claim 8:

```
**Two populations, and they are asymmetric in size.**
  - `CROSS_REPO_TEST_PATHS` -- 8 paths (originally 6, resolved from the 7
    proxy-carrying `tests/` modules rekeyed by this same plan (Task 1/2);
    Phase 147 added `src/firestarter.cpp` making 7, Phase 149 Plan 05 added
    `src/json_parser.c` making 8 -- both additions landed without this prose
    figure being updated in lockstep until now).
```

The tuple holds **7** today and **6** after D-14. Correct it to the real count. There
is a second stale figure downstream at lines 261-265 ("this union is the same 8 paths
as population A") — same defect, same sentence family, fix in the same pass.

**Downstream import sites to check after removal** — `ALL_CROSS_REPO_PATHS` is derived
(lines 268-277), so it follows automatically; no other module needs editing.

---

### `firestarter_app/tools/check_no_exists_proxy.py:19` and `tests/fixtures/planted_no_exists_proxy.py:20,41` — re-dated citations (D-02)

**These two files cite each other and are each other's analog.** Edit both in the same
pass so the wording matches. Three sites total, verified by
`/usr/bin/grep -n 'test_dispatch_mirror'`:

`tools/check_no_exists_proxy.py:16-21` (module docstring):

```python
  - the compound shape: `FW_ABSENT = not (a.exists() and b.exists())` --
    exactly what `tests/test_dispatch_mirror.py` used before its rekey onto
    `tests/fw_presence.py`.
```

`tests/fixtures/planted_no_exists_proxy.py:18-21` (module docstring):

```python
  2. `COMPOUND_ABSENCE_PROXY` -- the compound shape, a `not` over a boolean
     combination of two `.exists()` calls -- the exact shape
     `tests/test_dispatch_mirror.py` used before its own rekey.
```

`tests/fixtures/planted_no_exists_proxy.py:39-42` (a `#` comment — an **existing**
comment being re-dated, not a new one):

```python
# PLANTED VIOLATION (compound shape): a module-level absence proxy over a
# boolean combination of two `.exists()` calls -- mirrors the exact shape
# test_dispatch_mirror.py used before its Phase 123 Plan 08 rekey (it ANDed
# the existence of two firmware-repo paths together before negating).
```

**Pattern to apply:** keep the module name (it is the only record of why the compound
arm exists) and add its disposal, i.e. state the module was **deleted 2026-08-31 in
`39ea3e8`**. The house style for "this thing is gone, here is where it went" is already
in this repo at meta `CLAUDE.md:12` and in D-09's PROTOCOLS.md replacement — state the
absence, do not silently strip the name. All three sites already carry a `Phase 123
Plan 08` provenance token; follow that citation format.

**Do not confuse** this live lint with the deleted `test_dispatch_mirror.py` it cites
(CONTEXT.md canonical refs). `check_no_exists_proxy.py` stays, unmodified except for
its docstring.

---

### The two `planted_dispatch_*.cpp` fixtures — DELETE (D-07)

**No analog, and no successor.** Both are listed here in full-header form because D-08
requires the knowledge to survive their deletion. Read both **before** deleting.

`planted_dispatch_comment_only_hex.cpp:22-32` — **this is the fail-open finding**, the
paragraph D-08 item 3 must carry into the verdict note:

```
 * THIS FIXTURE'S PAIRED TEST LEG asserts GREEN, not RED. Do NOT "fix" this file by
 * removing the comment or by wrapping the paired leg
 * (test_planted_comment_only_hex_is_NOT_detected) in `pytest.raises`. The
 * GREEN result IS the finding: `test_dispatch_mirror_firmware_leg_enumerates_all_protocols`
 * extracts every `0x[0-9A-Fa-f]+` token from the WHOLE file text via a bare
 * regex with no comment-awareness, so a comment-only mention of `0x10`
 * satisfies the gate exactly as well as a real dispatch case would. A
 * reader who "corrects" this fixture or its leg to expect RED destroys the
 * one committed proof that the gate cannot distinguish "a native dispatch
 * test exists for this protocol" from "a comment mentions this protocol".
```

`planted_dispatch_missing_hex.cpp:28-36` — the same regex named from the RED side,
and the reason the fixture's own header never spells the token:

```
 * never spells the real identifier as one contiguous `0x`-prefixed token
 * anywhere in this file (not even here in the header) -- because
 * `test_dispatch_mirror_firmware_leg_enumerates_all_protocols` extracts
 * every `0x[0-9A-Fa-f]+` token from the WHOLE file text via a bare regex
 * with no comment-awareness, and a stray mention in this very docstring
 * would silently satisfy that regex and invalidate this fixture's entire
 * purpose.
```

Both fixtures also carry a byte-faithful copy of `kAllProtocolFamilies` with
flash_intel rewritten `0x10` → `0xFF` — **13 rows**, matching the firmware side of
D-16's drift table. That corroborates the 13 figure independently of
`test_configure_memory.cpp`.

Deleting these also clears two of the five app-repo `dispatch_mirror` grep hits (D-07).
Both files' headers instruct future readers **not** to delete them; that instruction is
superseded by D-05/D-07 (their consumer was deleted 2026-08-31 by `39ea3e8`, and under
D-05 no consumer will ever exist again). Record that supersession in the verdict note,
which is where the knowledge goes.

**D-06 guard:** do not file a successor backlog item for the two-way
`KNOWN_PROTOCOLS` ↔ `kAllProtocolFamilies` guard. Zero backlog items on the CLAIM-03
axis. The 182 (999.55-999.59) / 183 (999.63-999.66) filing pattern does **not** apply.

---

### `firestarter/PROTOCOLS.md:11-13` — paragraph replacement (D-09)

**Analog:** meta `/workspaces/CLAUDE.md:12`, named by D-09 as the precedent.

**The site being replaced** (`PROTOCOLS.md:11-13`, verified verbatim):

```markdown
The claims region below is machine-read by `tools/wiki/dispatch_mirror.py` in
the meta repository, which checks that the dispatch table here, the host tool
and the firmware all agree. Keep its table shape intact when editing.
```

**The precedent's shape** — state the absence in the same sentence that retires the
claim, rather than silently erasing it (meta `CLAUDE.md:12`, second half):

```markdown
The `tools/wiki/` checkers that used to validate a clone of that wiki were retired
on 2026-09-02 (`5426d7ef`); only `MIGRATION-TABLE.md` survives there, as a record of
the completed migration, and **no automated wiki guard exists now**.
```

Elements that transfer: the retirement date, the commit sha in backticks, and a
**bolded** statement of the current absence. D-09's replacement line states that no
tool machine-reads this document and the table is maintained for human readers.
Markdown — the source-comment rule does not apply here.

**Surrounding structure to preserve** (`PROTOCOLS.md:1-9`): title, a 3-line purpose
paragraph, then a wiki cross-reference. The replaced line sits directly after the wiki
link, before the body. Keep the one-blank-line-between-paragraphs rhythm.

---

### `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp:200-202` — delete the false clause (D-10)

**No analog is offered, deliberately.** There is nothing to copy here — the only
permitted operation is a deletion.

**The site** (lines 200-203, verified verbatim):

```cpp
/* Walks configure_memory's protocol chain (memory.cpp:70-113) literally,
 * one row per KNOWN_PROTOCOLS entry -- table-driven so adding a protocol is
 * one row, not one function. */
static const protocol_family_row_t kAllProtocolFamilies[] = {
```

- **False clause (delete):** `one row per KNOWN_PROTOCOLS entry` — false in three
  places per D-15/D-16's drift table (`0x34` host-only; `0x35`, `0x39` firmware-only).
- **True remainder (keep):** that the table is table-driven so adding a protocol is one
  row, not one function; and the `memory.cpp:70-113` chain citation.

**HARD CONSTRAINT restated:** writing a corrected or replacement comment is NOT
available. If the clause cannot be excised without authoring replacement prose, leave
it and record the deviation in the plan's `SUMMARY.md` (D-10).

**The table itself** (lines 203-216, 13 rows) is **not** edited by this phase — no
firmware behaviour change, and D-16 bars adjudicating the drift. It is read only to
count rows for the drift table.

---

### `.planning/notes/<verdict>.md` — NEW verdict document (D-08, D-16)

**Analogs:** both named by D-08.
- `/workspaces/.planning/notes/ae29f2008-classification-verdict.md` (Phase 183, 220 lines) — **the closer template**: a verdict on a question, with an evidence chain and an explicit "what this did not do, and why" section.
- `/workspaces/.planning/notes/jumper-display-ground-truth.md` (Phase 182, 279 lines) — the ground-truth/measurement-table template; source of the evidence-table shape D-16's drift table needs.

**Frontmatter pattern** (identical shape in both; 183's version):

```markdown
---
title: AE29F2008 classification verdict — algorithm 5 is correct, and gh#62 is correct too
date: 2026-09-11
context: v1.37 Phase 183, SAFE-09 — re-verified in this session against 183-RESEARCH.md §B
---
```

`title` states the verdict itself, not the topic. `context` names milestone, phase,
requirement ID, and how the content was obtained.

**Verdict-and-grounds pattern** (183, the `## THE VERDICT` section) — the verdict in
**bold** first, then immediately the epistemic limits of the evidence, before any
detail:

```markdown
# AE29F2008 classification verdict (SAFE-09)

## THE VERDICT

**AE29F2008 is classified `algorithm 5` CORRECTLY. gh#62's reporter is ALSO correct that the chip
can be chip-erased. Both are true at once: ...**

**This verdict is equivalence-based, not a direct datasheet reading.** No primary AE29F2008
datasheet was retrieved or read — none is retrievable; ... If a future reader wants a direct
AE29F2008 vendor-datasheet confirmation, this record is not that — it is the best evidence this
project could obtain, and it says so plainly.
```

This second paragraph is the **direct model for D-16**: state in the note's own words
what was measured versus what was verified, so no reader mistakes the record for a
clean bill of health.

**Evidence-chain pattern** (183, `## THE EVIDENCE CHAIN`) — lettered legs, each a
bolded one-sentence claim followed by a fenced command-and-output block:

```markdown
**Leg (a) — the classification is an upstream transcription, not a generator decision.** ...

```
$ cd /workspaces/firestarter_app && /usr/bin/grep -n '0x05, 0x06, 0x0D, 0x10' tools/build_db.py
356:    if proto_id in {0x05, 0x06, 0x0D, 0x10}:
```
```

For D-08 item 2 (the two-deletion history), each of `39ea3e8` (2026-08-31) and
`5426d7ef` (2026-09-02) is a leg, with a `git show --stat` / `git log -1` block as its
evidence.

**Measurement-table pattern** (182, `## Ground-truth sources` / `## What each jumper
actually routes`) — a source-provenance table then a findings table, each row carrying
the reason its own side holds:

```markdown
| Revision family | Source | Status |
|---|---|---|
| Rev 0 / Rev 1 (identical, per operator) | `firestarter/document/rurp_schematics_rev1.pdf` | Read 2026-07-10 |
```

D-16's drift table is already drafted in CONTEXT.md § Specific Ideas with the same
four-column "each side's stated reason" shape. Carry it verbatim, with an explicit
sentence that this phase did not verify either reason.

**Negative-record pattern** (183, `## WHAT THIS PHASE DID NOT DO, AND WHY (D-21)`) —
directly applicable to **D-06**: the note must state that no successor guard and no
backlog item were filed, and that this is deliberate:

```markdown
A later reader of this record should not mistake the absence of a DB diff for the
question having gone unasked — it was asked, tested against every leg of D-19's
projection, and answered CORRECT.
```

**Do NOT copy** 183's `## Summary of backlog items this verdict generates` section.
Under D-06 this phase files **zero** backlog items on the CLAIM-03 axis. If an
equivalent section is written at all, it states that none were filed and why.

**Naming:** both existing notes are kebab-case, subject-first, ending in the
document's kind (`-ground-truth.md`, `-classification-verdict.md`). Follow that.

---

### `/workspaces/CLAUDE.md:12` — repair the `tools/wiki/` claim (D-04)

**Analog:** the same sentence's own second half (quoted above under PROTOCOLS.md).
The clause "only `MIGRATION-TABLE.md` survives there" is false since 2026-09-08 — the
file moved to `.planning/v1.35/MIGRATION-TABLE.md` and `tools/wiki/` was removed
entirely (`tools/` now holds `catalog/` alone).

**Pattern:** keep the retirement date, the `5426d7ef` sha, and the bolded "**no
automated wiki guard exists now**"; repair only the survives-there clause, stating
where the file actually went.

**Planner must carry this deliberately** (D-04): it names `tools/wiki/`, not
`dispatch_mirror`, so criterion 1's grep does not catch it.

---

## Shared Patterns

### RED-first proof (D-13)
**Source:** Phase 183 Plan 04 precedent; CONTEXT.md § Established Patterns.
**Apply to:** the CLAIM-09 guard, **twice**.
1. Build the check, run it against the **real** rotted entry
   (`scan_paths.py:112-115`), observe RED, remove the entry, observe GREEN.
2. Then plant a synthetic entry, observe RED, remove, observe GREEN — criterion 2's
   literal wording.
Both halves required. No hand-delete of the real entry before the guard exists.

### Fail-closed over fail-open (D-11)
**Source:** the project's repeated fail-open history, and `test_scan_paths_resolve.py`'s
own `@requires_fw` boundary (line 66 — only the one test that genuinely needs the
sibling repo carries it).
**Apply to:** the new CLAIM-09 test.
- The new test must be **unmarked** — it resolves only `firestarter_app/tests/`.
- No sanctioned escape hatch / "no live consumer" marker (D-14 rejected one explicitly:
  it would reintroduce the silent-claim failure mode).
- `is_file()`, not `exists()` — matches the analog at line 154 and rejects a directory.

### Collect-then-assert-once failure messages
**Source:** `test_scan_paths_resolve.py:76-91` and `:151-158`.
**Apply to:** the new CLAIM-09 test.
Every test in this file that can have N failures collects all N and asserts once, with
a message naming each offender **and the fix**. Never fail on the first.

### Census assertions are the anti-pattern (D-15)
**Source (negative):** `test_scan_paths_resolve.py:147` and `scan_paths.py:250`.
**Apply to:** the new test (no count assertion at all) and to `_FLOOR`'s justification
(re-anchor to a reason, not a measurement).

### `planted_*` fixture convention
**Source:** `tests/fixtures/planted_no_exists_proxy.py` (survives, edited by D-02) and
the two `planted_dispatch_*.cpp` (deleted by D-07).
**Apply to:** D-13's second half. The convention: a `tests/fixtures/` file, never
imported/compiled, unreachable from any checker's default target list, with a header
docstring stating which paired test consumes it and what it plants. D-13's planted
`ScanPathEntry` is transient (plant, observe red, remove) — it does **not** become a
committed fixture file.

### Prose citations state the disposal, not just the name
**Source:** meta `CLAUDE.md:12`.
**Apply to:** D-02 (three citation sites), D-09 (`PROTOCOLS.md`), D-04 (`CLAUDE.md`).
Name + retirement date + commit sha + bolded statement of the current absence.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `firestarter/test/native/avr/test_dispatch/test_configure_memory.cpp` | test (C++) | n/a | Deletion-only edit under `CLAUDE.md`'s hard comment rule. There is deliberately no pattern to copy — presenting one would invite authoring replacement prose, which is forbidden. |

Every other file has a tracked in-repo analog above.

---

## Scope Guards (from CONTEXT.md — a planner must not cross these)

- **D-05/D-06:** no replacement dispatch guard, no successor backlog item, no
  "unverified drift" item. Zero backlog filings on the CLAIM-03 axis.
- **D-01:** no broader retired-checker sweep. Only `dispatch_mirror` survives of
  `5426d7ef`'s eight deletions; the other seven are clean.
- **D-16:** the drift is recorded, not adjudicated.
- **D-10:** the C++ `kAllProtocolFamilies` table itself is not edited.
- Files not named in CONTEXT.md are out of scope, including the second census assertion
  at `scan_paths.py:250` and the `test_configure_memory.cpp:9` line-number citation
  (CONTEXT.md § Deferred — flagged, not filed).

---

## Metadata

**Analog search scope:** `/workspaces/.planning/notes/`, `/workspaces/CLAUDE.md`,
`/workspaces/firestarter_app/tests/`, `/workspaces/firestarter_app/tools/`,
`/workspaces/firestarter/PROTOCOLS.md`,
`/workspaces/firestarter/test/native/avr/test_dispatch/`
**Files read in full:** 8 (`test_scan_paths_resolve.py`, `scan_paths.py`, both
`planted_dispatch_*.cpp`, `planted_no_exists_proxy.py`, plus targeted ranges of
`check_no_exists_proxy.py`, `PROTOCOLS.md`, `test_configure_memory.cpp`, and both
`.planning/notes/` verdict templates)
**Tracked-source verification:** `git ls-files` run in all three repositories; all 11
analog paths tracked, zero mirror paths.
**Grep tool note:** `/usr/bin/grep` used throughout — the devcontainer's default `grep`
is ugrep and honors `.gitignore`, which under-scans.
**Pattern extraction date:** 2026-09-11
