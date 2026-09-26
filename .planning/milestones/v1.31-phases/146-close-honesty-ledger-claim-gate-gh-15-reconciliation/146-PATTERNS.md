# Phase 146: Close — Honesty Ledger, Claim Gate & gh#15 Reconciliation - Pattern Map

**Mapped:** 2026-08-17
**Files analyzed:** 20 (9 new in the phase dir + 5 fixtures + 3 sub-repo docs + 3 `.planning` records + 1 canonical toml)
**Analogs found:** 20 / 20 (every file has an in-tree donor; nothing is designed from scratch)

RESEARCH.md already did the archaeology. This file is the **excerpt-level analog map**: per new file,
the donor lines to copy, the donor lines that must change, and the donor lines that must NOT be copied.
Nothing here re-litigates a locked decision.

---

## File Classification

| New/Modified file | Role | Data flow | Closest analog | Match |
|---|---|---|---|---|
| `146-check-claims.py` | gate/utility (CLI, exit-code) | file-I/O + transform (read → regex → report) | `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` (331 ln) | **exact** (same milestone vocabulary) |
| `146-check-close03-docs.py` | gate/utility (CLI, exit-code) | file-I/O, cross-repo read-only | `139-check-claims.py` (structure) + `.planning/phases/130-…/check_record_corrections.py:120-172` (out-of-phase-dir target resolution) | role-match, two donors |
| `test_check_claims_v131.py` | test | subprocess-driven, request-response | `.planning/phases/137-…/test_check_permitted_claims_v130.py` (350 ln, 11 legs) | **exact** |
| `fixtures/*.md` (5) | test data | static | `.planning/phases/137-…/fixtures/` (5 files, 8–17 ln each) | exact layout, **content NOT copyable** (see §Fixtures) |
| `146-LEDGER.md` | record/artifact | authored prose + 4-col table | `137-LEDGER.md` (most recent) → `130-LEDGER.md` (evidence tiers) → `122-LEDGER.md` (key wording) | **exact** ×3 instances |
| `146-CORRECTIONS.md` | record/register | table | `139-CITATIONS.md` §-style register + the row shape in `146-RESEARCH.md:2117-2122` | role-match (no prior CORRECTIONS register exists) |
| `146-GH15-RECONCILIATION.md` | outward artifact | authored prose + disposition table | `139-GH15-COMMENT.md:48-58` (disposition table) + `139-GH15-ORIGINAL-CRITERIA.md` (the 9 boxes) | **exact** |
| `146-RELEASE-NOTES-fw.md` | outward artifact | authored prose | `130-RELEASE-NOTES-fw.md` (9 sections) + `122-RELEASE-NOTES-fw.md` (8 sections) | **exact** ×2 |
| `146-RELEASE-NOTES-app.md` | outward artifact | authored prose | `137-RELEASE-NOTES-app.md` (6 sections, leanest) | **exact** |
| `146-CITATIONS.md` | record/register | tables of commands-as-run | `139-CITATIONS.md` (45 KB, §0/§1/§4/§5/§6 skeleton) | **exact** |
| `firestarter/doc/PROTOCOLS.md` | documentation | in-place edit | its own §1.5 (F-140-07 already corrected there) is the in-file style donor | self-analog |
| `firestarter/CLAUDE.md` | documentation | in-place numeral fix + 1 paragraph | its own `0x0B` row `:66` and `:136-137` | self-analog |
| `firestarter_app/README.md` | documentation | in-place option-list edit | its own §Write `:315-318` block | self-analog |
| `tools/catalog/messages.toml` (canonical) | config (codegen source) | batch → generated artifacts | its own `[[debug.messages]]` stanza at `:920-925` | self-analog |
| `.planning/{ROADMAP,PROJECT,STATE}.md` | record | in-place `⚠ CORRECTION` block insert | `.planning/PROJECT.md:470` (live recognized block) | **exact** |

---

## Pattern Assignments

### 1. `146-check-claims.py` (gate, file-I/O + transform)

**Analog:** `.planning/phases/139-gh-15-correction-outward/139-check-claims.py` — read in full; 331 lines,
stdlib-only (`os`, `re`, `sys`).

**Structure map to reproduce 1:1** (donor line → 146 element):

| Donor lines | Element | 146 action |
|---|---|---|
| `:1-62` | module docstring: why-a-replacement, exit-code contract, 2 explicit non-claims | rewrite (names CLOSE-01 + the blocking operator wording review, not ISSUE-02/D-05) |
| `:73` | `_HERE` | copy verbatim |
| `:78-81` | `_DEFAULT_TARGETS` | **replace** with the five 146 basenames |
| `:90-92` | env seam | **rename** (139's `_V131` name is taken) |
| `:98-128` | 12 forbidden patterns | copy **verbatim** — D-14 forbids loosening |
| `:134-145` | 2 required caveats | copy verbatim, but **consume per-file** (new `_CAVEAT_RULES`) |
| `:148-181` | `_assert_default_targets_are_local()` | copy, `"139-"` → `"146-"` in **both** the `startswith` call and the printed string |
| `:184-202` | `resolve_targets` | copy verbatim (argv → env `is not None` → defaults) |
| `:205-238` | `scan_text` | copy verbatim; add a caveat-rule parameter, do not touch the pattern loop |
| `:241-246` | `_print_bucket` (20-cap + "… and N more") | copy verbatim |
| `:249-326` | `main()` order of operations | copy verbatim; **do not add** an UNARMED branch |

**Imports + `_HERE` (donor `:64-73`) — copy verbatim:**
```python
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
```

**`_DEFAULT_TARGETS` — donor `:78-81` shape, 146 content** (never a glob; `146-CONTEXT.md` alone carries
6 `proven-unqualified` hits and would be swept in):
```python
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "146-LEDGER.md"),
    os.path.join(_HERE, "146-CORRECTIONS.md"),
    os.path.join(_HERE, "146-GH15-RECONCILIATION.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-fw.md"),
    os.path.join(_HERE, "146-RELEASE-NOTES-app.md"),
]
```

**Env seam — donor `:83-92` verbatim, name changed:**
```python
# Env-override seam, SUFFIXED `_V131`: three prior checkers in this project
# already use the bare or `_V130`-suffixed name, and a collision would let
# one phase's seam silently retarget another phase's gate.
FIRESTARTER_CLAIMSCAN_TARGETS_V131 = os.environ.get(
    "FIRESTARTER_CLAIMSCAN_TARGETS_V131"
)
```
`FIRESTARTER_CLAIMSCAN_TARGETS_V131` is **already live in 139, this same milestone**. Use a distinct
name (e.g. `FIRESTARTER_CLAIMSCAN_TARGETS_146`) and update the comment's justification sentence.
A bare copy "works", which is why this is the easiest mandatory edit to miss.

**The self-check — donor `:165-181` verbatim; two literals change:**
```python
    all_local = True
    for entry in _DEFAULT_TARGETS:
        if os.path.dirname(entry) != _HERE:
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not resolve "
                "inside this phase's own directory -- this is the exact "
                "cross-phase-copy defect this self-check exists to catch"
            )
            all_local = False
        if not os.path.basename(entry).startswith("139-"):   # <-- "146-"
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                "this phase's own 139- prefix -- this is the exact "        # <-- 146-
                "stale-name defect this self-check exists to catch"
            )
            all_local = False
    return all_local
```
This is the answer to the recorded `_HERE` trap: `check_permitted_claims.py`'s `_HERE`-relative defaults
resolve to the **checker's own** phase dir, so a cross-phase copy scans nothing and exits 0. 139 solves it
with `_HERE` + the prefix assertion; a 146 copy that fixes `_DEFAULT_TARGETS` but leaves `"139-"` in the
`startswith` **fails closed immediately** (safe), whereas one that fixes the call and leaves the message
stale is a silent doc defect the fixture suite cannot see.

**Never-vacuous + fail-closed branches — donor `:266-282`, copy verbatim:**
```python
    targets, _used_defaults = resolve_targets(argv)

    if not targets:
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    missing = [t for t in targets if not os.path.isfile(t)]

    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- the gate cannot "
            f"vacuously pass with a target silently skipped: {missing}"
        )
        return 1
```
A **partial** default set (1–4 of 5 present) therefore lands in the second branch and is a hard failure —
which is exactly D-11's arming contract, achieved with **no** extra code.

**`argv`/env precedence — donor `:196-202`, copy verbatim; the `is not None` is load-bearing:**
```python
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_V131 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_V131.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True
```

**The one genuinely new mechanism (D-11), no donor exists.** Keyed on basenames so it cannot drift from
`_DEFAULT_TARGETS`' directory construction; unknown basename → **full** set (fail closed):
```python
_CAVEAT_RULES = {
    "146-LEDGER.md":              {"ceiling-voltage", "ceiling-narrowing"},
    "146-GH15-RECONCILIATION.md": {"ceiling-voltage", "ceiling-narrowing"},
    "146-RELEASE-NOTES-fw.md":    {"ceiling-voltage", "ceiling-narrowing"},
    "146-RELEASE-NOTES-app.md":   {"ceiling-voltage", "ceiling-narrowing"},
    "146-CORRECTIONS.md":         frozenset(),
}
```
The donor's report site to adapt: `139-check-claims.py:288-308` builds `caveat_prose_by_label` and
increments `caveat_present_count`; the per-file rule replaces the unconditional
`REQUIRED_CAVEAT_PATTERNS` iteration inside `scan_text` (`:232-236`). The `PASS:` line at `:320-325`
counts "file(s) carry both required caveats" — that count text must change, because under D-11 one target
legitimately carries none.

**Lines that must NOT be copied or altered:**
- `139-check-claims.py:57-61` — explicit non-claim #2 (*"is not a build of [CLOSE-01]"*). 146 **is** the
  build; copying that paragraph would assert the opposite of the phase's own deliverable.
- `:49-55` — non-claim #1 names ISSUE-02 / D-05 / plan 139-05. Retarget, don't copy.
- `:14-20` / `:209-212` — the no-proximity-window justification: copy the **design** (no window), keep the
  measurement citation accurate (it is 139's measurement, cite it as such).
- Do **not** import 137's window (`137/check_permitted_claims.py:208-219`) or its relational
  `self-verifying` rule (`:228-241`). 146 inherits 139's design.
- Do **not** port 137's UNARMED branch (`137/check_permitted_claims.py:299-305`) — an exit-0-on-nothing
  path is a green that proves nothing.

---

### 2. `146-check-close03-docs.py` (gate, cross-repo file-I/O)

**Primary analog:** `139-check-claims.py` (whole skeleton: `_HERE`, self-check, `resolve_targets`,
never-vacuous, fail-closed, `_print_bucket`, `PASS:` line).
**Second analog for target resolution only:** `.planning/phases/130-…/check_record_corrections.py:120-172`
— the only in-tree checker whose targets live **outside** its own phase directory.

**Copy this repo-root walk (donor `:120-137`) rather than `_HERE`-relative `../../..` hops:**
```python
def _find_repo_root():
    """Walk upward from `_HERE` and return the first ancestor directory that
    contains a `.planning` subdirectory. Raises `RuntimeError` -- never
    silently falls back to `_HERE` -- if no such ancestor exists, because a
    silent fallback here is exactly the C-2 defect this checker exists to
    avoid."""
```
and the target-list shape (donor `:163-171`), retargeted at the sub-repo docs:
```python
_DEFAULT_TARGETS = [
    os.path.join(_REPO_ROOT, "firestarter", "doc", "PROTOCOLS.md"),
    os.path.join(_REPO_ROOT, "firestarter", "CLAUDE.md"),
    os.path.join(_REPO_ROOT, "firestarter", "README.md"),
    os.path.join(_REPO_ROOT, "firestarter_app", "README.md"),
]
```

**The recorded trap this shape answers.** This script scans **firmware source-tree paths from a
phase-local script**, and the recorded pattern is that host-side gates scanning firmware source break on
renames and **fail OPEN** (4× in Phase 117; `firestarter_app/tests/test_py32_flash_map_host.py`'s
`requires_fw` gate is the live instance, and `PROJECT.md:1181` disclosure 4 states those gates fail open
across the repo boundary by design). Mitigations, all already present in the donors:

1. Host it in `.planning/phases/146-…/`, **not** in either sub-repo — nothing is `requires_fw`-conditional.
2. Reuse the fail-closed missing-target branch verbatim (`139-check-claims.py:275-282`) so a renamed or
   moved doc is exit 1, never a skip.
3. Reuse the never-vacuous guard verbatim (`:268-273`) so an emptied target list is exit 1.
4. Keep its own `_assert_default_targets_are_local()`-analog — but the prefix assertion cannot be
   `startswith("146-")` here (targets are sub-repo docs). Replace that leg with: every entry resolves
   under `_REPO_ROOT`, and every entry is a member of a literal 4-element allowlist — i.e. assert the
   list's *shape*, not its prefix. Do not silently drop the self-check leg; a self-check with one leg
   removed and nothing substituted is the fail-open shape.

**Structural difference from the claim gate (D-13):** **no caveat rule at all**; instead five
required-topic patterns (per-byte algorithm, parameter table, database-supplied pulse, `--pulse-us`,
6.25 V debt) plus the same 12 forbidden patterns. Two of the five topics are measured **absent from all
six candidate docs today** (`grep -c '6\.25'` = 0 everywhere; `--pulse-us` = 0 in every host doc), so this
checker is a true RED before the edits and a GREEN after — the "seen to fail for the right reason"
discipline is satisfied without a plant.

---

### 3. `test_check_claims_v131.py` (test, subprocess-driven)

**Analog:** `.planning/phases/137-…/test_check_permitted_claims_v130.py` — 350 lines, 11 legs.

**Docstring `:1-56`** carries the anti-hollow rationale and the leg-by-leg coverage list — copy the shape,
retarget the numbers. Note `:16-21`, the module-rename rationale:
> *"Renamed … (PITFALLS P-11 point 5) -- a THIRD file literally named `test_check_permitted_claims.py`, alongside the v1.22 and v1.23 copies already on disk in sibling phase directories, would collide under pytest's default `prepend` import mode for anyone running pytest from `/workspaces`."*

**Header + the two invocation idioms — donor `:58-100`, copy with the env name changed:**
```python
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_SCANNER = _HERE / "check_permitted_claims.py"          # -> "146-check-claims.py"


def _run_scanner(targets=None, argv=None):
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_V130"] = targets    # -> the fresh 146 name
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_V130", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


def _import_scanner_module():
    spec = importlib.util.spec_from_file_location(
        "check_permitted_claims_v130_introspect", str(_SCANNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```
Note `_SCANNER` will be `146-check-claims.py` — a filename that is **not a valid Python identifier**.
That is fine for `spec_from_file_location` (the module *name* argument is arbitrary) and for
`subprocess`, and it is another reason legs 1–9 must stay subprocess-driven, never `import`.

**Fixtures are parameterized by path string through the env seam**, one target per leg, `os.pathsep`-joined
for the multi-file leg (donor `:235-239`):
```python
    result = _run_scanner(
        targets=os.pathsep.join(
            ["fixtures/clean_control.md", "fixtures/clean_control_second.md"]
        )
    )
```
Relative paths work because `cwd=str(_HERE)`.

**The two introspection legs — donor `:314-349`, copy verbatim with `"137-"` → `"146-"`:**
```python
def test_default_targets_resolve_inside_this_phase_directory():
    module = _import_scanner_module()
    expected_dir = str(_HERE.resolve())
    for entry in module._DEFAULT_TARGETS:
        assert os.path.dirname(entry) == expected_dir, (
            f"_DEFAULT_TARGETS entry {entry!r} does not resolve inside this "
            f"phase's own directory {expected_dir!r} -- this is the exact "
            "cross-phase-copy defect this test exists to catch"
        )


def test_default_target_basenames_are_this_milestones():
    module = _import_scanner_module()
    for entry in module._DEFAULT_TARGETS:
        basename = os.path.basename(entry)
        assert basename.startswith("137-"), (        # <-- "146-"
            f"_DEFAULT_TARGETS basename {basename!r} does not carry this "
            "milestone's own '137-' prefix -- this is the exact stale-name "
            "defect this test exists to catch"
        )
```
Add two cheap 146-only introspection legs beside them: every `_DEFAULT_TARGETS` basename has a
`_CAVEAT_RULES` entry, and an unknown basename resolves to the **full** caveat set.

**Leg-level adaptations (donor → 146):**
- Leg 2 (`:126-140`) asserts the **specific label** `"lock-inhibited-the-write"`, not just non-zero. 146's
  equivalent label must come from the 12-pattern table (`confirmed-working` is the probed choice).
- Leg 4 (`:167-180`) tests 137's **relational** `self-verifying` rule. 146 has no relational rule —
  replace with a second forbidden-pattern plant on `proven-unqualified`.
- Leg 6 (`:207-223`) is the never-vacuous leg and asserts `"PASS:" not in` **and** `"UNARMED:" not in`.
  Keep both assertions even though 146 has no UNARMED branch — it pins that absence.
- Leg 9 (`:276-305`) is the literal discharge of "armed against the real files": `_run_scanner(targets=None,
  argv=None)` then a loop asserting each real basename appears in stdout. Its donor docstring is the
  recorded warning about pre-authored legs:
  > *"Supersedes the prior UNARMED-expecting leg this test replaces (its own docstring anticipated exactly this edit: 'stays green until 137-06 makes all four exist')."*
  Schedule it so it is observed RED-for-the-right-reason (naming the *missing artifact*), then GREEN.

**Lines that must NOT be copied:** the donor's `"missing required silicon caveat"` bucket string (`:157`)
and `"self-verifying"` label (`:178`) — both are v1.30 vocabulary and would assert against strings 146's
gate never prints.

---

### 4. `fixtures/` (test data)

**Analog layout:** `.planning/phases/137-…/fixtures/` — exactly 5 files, 8–17 lines each,
611–967 bytes. Every file opens with a self-labelling HTML comment; planted files add a second one naming
the violation:
```markdown
<!-- test fixture for check_permitted_claims.py — NOT a closing artifact — never add to _DEFAULT_TARGETS -->
<!-- planted violation: trips the lock-inhibited-the-write forbidden label -->
```
Copy that two-line convention verbatim (retargeting the script name). It is also why no glob may ever
reach `fixtures/`.

**⚠ The donor fixture BODIES are not copyable.** All five 137 fixtures contain the sentence *"…are
**proven** in native test environments"*, which is a direct `proven-unqualified` hit under 146's table —
so 137's `clean_control.md` would fail 146's gate. Measured-safe substitutes for the clean controls:
*validated*, *bench-validated*, *established*, *demonstrated*, *measured*, *shown*. And both clean controls
must **carry** `6.25 V` + a `silicon-margin` phrase or leg 1 fails for the wrong reason.

**Five 146 fixtures** (from RESEARCH's file layout): `clean_control.md`, `clean_control_second.md`,
`planted_forbidden_claim.md`, `planted_proven_unqualified.md`, `planted_missing_caveat.md`.
Probe each plant's label set with `scan_text` **before** writing the assertion — the recorded plant
`confirmed working on silicon` fires `confirmed-working` but **not** `works-on-silicon`.

---

### 5. `146-LEDGER.md` (record)

**Analog:** `137-LEDGER.md` (26.8 KB, most recent); `130-LEDGER.md` for the evidence tiers;
`122-LEDGER.md` for the status-key wording.

**Section skeleton, with donor line numbers:**

| Section | `122` | `130` | `137` |
|---|---|---|---|
| identity header | `:1-21` | `:1-23` | `:1-42` |
| the ceiling, quoted verbatim | `:22` | `:24` | `:44` |
| status / claim key | `:34` | `:36` | `:84` |
| evidence tiers, weakest→strongest | — | `:53-102` | — |
| the claim classes | `:43` | — | `:98` |
| mechanism corrections | `:81` | `:103` | `:120` |
| process failures, not only technical | — | — | `:165` |
| negative space | `:97-122` | `:115-148` | `:195-233` |
| what no test/gate/review can close | `:123` | `:149` | `:234` |
| scanner status | `:133` | `:173` | folded into the header |

**The 4-column claim table header — identical in all three; copy verbatim** (`137-LEDGER.md:104-105`):
```markdown
| Class | Permitted wording | Evidence (measured, source) | Explicitly does NOT prove |
|---|---|---|---|
```
Column 4 **is** CLOSE-02's "explicit non-claim". A status token is bolded into the Class cell —
`137-LEDGER.md:106`: `| **1. Plan derivation, full 84-chip 0x0D population** \`PERMITTED\` | … |`.

**Status key — `137-LEDGER.md:86-94`, reused unchanged from 122; the `FORBIDDEN` entry is the D-14
discipline in the ledger's own voice:**
```markdown
- **`FORBIDDEN`** — the ceiling's forbidden claim shape. Appears in this ledger only as a citation of
  what is *not* claimed, never as prose asserting it.
```

**Identity-header moves worth copying literally** (`137-LEDGER.md:10-22`): submodule HEAD *"captured live
via `git -C … rev-parse HEAD` at this plan's own execution … never reused from a prior document's
citation"*; an **Oracle:** line naming every gate and suite with counts; a **Generated:** line; and a
`**Composes with (cross-reference only — no data copied):**` block (`:24-40`) whose last entry asserts a
referenced-but-unedited file's `git status --porcelain` was confirmed empty — the exact shape 146 needs for
"archived milestone requirements are never edited".

**Two reusable disciplines from `137-LEDGER.md:100-102` and `:71-76`:** every figure *"re-measured live
this plan … not copied from a citation"*, and where two readings of a number exist **both are stated
rather than silently reconciled** (137's four-vs-six step-count note at `:71-76` is the template for
146's three carry-forward counting discrepancies).

**Gate interaction the ledger's author must respect:** `145-BENCH-LOG.md:2709` is *"Nothing here says the
algorithm is datasheet-correct"* — a verbatim quote of it trips this phase's own gate. Cite as
`145-BENCH-LOG.md:2707-2709`, boundary 2, and paraphrase. `145-08-SUMMARY.md`, `139-GH15-COMMENT.md` and
`139-GH15-ORIGINAL-CRITERIA.md` all measure **0 hits** and are safe to quote verbatim.

---

### 6. `146-CORRECTIONS.md` (register)

No prior phase shipped a corrections **register** (v1.23 D-05 used blocks only) — so the analogs are
`139-CITATIONS.md`'s table-per-section register style plus the row shape RESEARCH already drafted
(`146-RESEARCH.md:2117-2122`):
```markdown
| # | Origin finding | Owning file:line | False text (cited, never re-quoted if it carries a forbidden phrase) | Corrected text |
|---|---|---|---|---|
```
Four fields per D-05: origin finding id · false text · corrected text · owning file. The
`file:line`-only citation column is D-14's solution to the self-reference trap (v1.22's original fix;
the 125 incident tripped all six `125-0N-SUMMARY.md` files by quoting the phrases they disclaimed).

**Per-row site inventory is already located** — `146-RESEARCH.md:1295-1306`. Rows 1b (no false site
exists), 5 (**two** rows `PROJECT.md:212` and `:213`, not one) and 6 (`doc/PROTOCOLS.md` §1.5 **already
corrected**) diverge from CONTEXT's statement and must be written as measured, not as inherited.

**This is the one gate target with `frozenset()` caveats (D-11)** — do not paste a 6.25 V paragraph into it
just to satisfy a rule that no longer applies.

---

### 7. `146-GH15-RECONCILIATION.md` (outward artifact)

**Analog for the boxes:** `139-GH15-ORIGINAL-CRITERIA.md` — the nine boxes already extracted, verified
byte-matching the live body's `## Acceptance criteria` tail, and measured **0 forbidden hits**. D-08 grades
exactly this file; no re-scrape.

**Analog for the table:** `139-GH15-COMMENT.md:48-58`:
```markdown
| Original box | Disposition | Why |
| `0x07`, `0x08`, and `0x0B` use separate write handlers. | **Replaced** | Protocol owns *shape*; the database owns the *pulse*. One shared per-byte loop, driven by a `const` table keyed by `protocol_id`, replaces three handlers … |
| No new database algorithm flags are introduced. | **Kept** | Unchanged. |
```
139's disposition vocabulary is `Replaced` / `Corrected` / `Kept`. **146's is CLOSE-04's own three tokens**
— *met* / *met-as-corrected (naming the correction)* / *not-reachable-on-this-hardware (naming the reason)*
— both measured clean under the pattern table, as are `met-as-corrected` and
`not-reachable-on-this-hardware` as literal strings. Box 1 → met-as-corrected quoting 139's *Replaced*
row; boxes 3/4/5 → met-as-corrected quoting 139's *Corrected* rows verbatim (safe, 0 hits).

**Posting mechanics analog:** `139-05-SUMMARY.md` + `139-CITATIONS.md` §6.2–6.7 — sections
`6.2 Fail-closed preconditions, re-measured in this task (not carried forward)`,
`6.3 The outward act — who performed it, and the literal argv`, `6.4 Byte-diff result — the fetch-back
proof`, `6.6 Before/after state assertion` (a `| Field | Before this task | After this task |` table), and
`6.7 Negative-flag audit`. Copy that section set into `146-CITATIONS.md`.

---

### 8–9. `146-RELEASE-NOTES-fw.md` / `146-RELEASE-NOTES-app.md`

**App analog:** `137-RELEASE-NOTES-app.md` (3.3 KB, leanest, read in full). Section skeleton, verbatim
headings:
```
# Host app prerelease — <one-line headline>          (:1)
`pip install --pre --upgrade firestarter`            (:3)  + what the release page does/doesn't carry
## Removed                                           (:10)
## <what changed, in the user's terms>               (:23)
## Also in this release                              (:37)
## What is proven, and what is not                   (:44)
## The ask                                           (:53)
```
⚠ The donor's own §5 heading contains `proven` — a `proven-unqualified` hit. **Rename it** (e.g.
"What is established, and what is not"); do not copy that heading string.

**Firmware analog:** `130-RELEASE-NOTES-fw.md` (9 sections) with `122-RELEASE-NOTES-fw.md` for the
asset-list opener:
```
# Firmware prerelease — <headline>                                  (130:1 / 122:1)
<assets + `firestarter fw --install` sentence>                      (122:3-7)
## The headline: <named section>                                    (130:10 / 122:9)
## New capability: <…>                                              (130:23 / 122:29)
## Before you plug anything in: <safety>                            (130:53)
## What is proven, stated exactly                                   (130:66 / 122:37)
## What is NOT proven                                               (130:91 / 122:48)
## The capability boundary                                          (130:119 / 122:61)
## Feedback wanted                                                  (130:127 / 122:80)
```
Same rename obligation on the two `proven` headings. 130's load-bearing move to copy is stating the
boundary **immediately inside** the headline section (`130-RELEASE-NOTES-fw.md:10-22`), not saving it for
the end — that is the shape v1.31's ARM/py32 and Uno-class boundaries need.

**Version-agnosticism (D-02):** none of the four precedents hardcodes a `3.0.0bNN`; 137 self-identifies as
*"Host app prerelease"* and points at `pip install --pre`. Both bodies need `6.25 V` + a `silicon-margin`
phrase (they are caveat-required targets).

---

### 10. `146-CITATIONS.md`

**Analog:** `139-CITATIONS.md` (45 KB). Copy this section spine and its table headers:
```
# Phase 146 — Citation Register
## 0. <subject> before-state          | Field | Command (as run) | Result |      (:18-20)
## 1. Pinning strategy                 "Citations pin to commit SHAs, never branch names"  (:44)
## 2. Anchor verification table                                                  (:119)
## 4. Claim gate — planted-first, then the real run over both artifacts          (:282)
###   Run 1 — planted-violation re-run, MUST FAIL — observed FAIL                (:294)
###   Run 2 — default-mode run … MUST PASS — observed PASS                       (:324)
###   Mid-task correction, recorded here rather than smoothed over               (:355)
## 5. Freeze — | File | Frozen blob SHA | Byte length | Committing commit | `git status --porcelain` |  (:419-426)
## 6. Delivery  (6.0 operator verdict verbatim … 6.8 requirement discharge pointer)
```
§4's two-run shape **is** the plant-and-revert transcript home (D-12 second half). §0's
`| Field | Command (as run) | Result |` is where the gh#15 read-only measurement block lands.

---

## Modified sub-repo documentation (D-06 — wording only)

### `firestarter/doc/PROTOCOLS.md` — the exact lines to replace

Current text, §1.3, `:150-152` (measured; both halves now false):
```
firmware's present loop (`eprom.cpp:159-179`) is **retry escalation of `pulse_delay`**, not an Intel
3N margin pulse; Phase 141 replaces it. Full per-value attribution:
```
Phase 141 landed at commit `3504e50`; the shipped per-byte inner `for(;;)` is at `eprom.cpp:449-478`.
The **style donor is the same file's §1.5**, which already carries F-140-07's in-place correction — match
its `Citation:`-line convention and its five sub-headings (Write algorithm / Erase model / VPP behavior /
Pin roles). §1.3 `:143-149` already gets `overprogram_factor = 0` and F-140-05's scoped divergence right;
do not re-derive. Missing from §§1.3–1.5 entirely: `--pulse-us`, the 6.25 V ceiling.

### `firestarter/CLAUDE.md` — F-144-01's two stale numerals, `:277-282`

Current text, verbatim:
```
**Phase 142 addition:** `[env:native_loop_v131]` now runs **two** suites -- the pre-existing
`test_loop_eprom_v131` (39 cases) plus the new `test_vpp_eprom_v131` (32 cases), **71 cases
total** (plan 142-05's tip; …)
```
Two numerals wrong (`39` and `71`); measured tip is **47 + 32 = 79**. The `⚠ CORRECTION` block appended
after this paragraph is drafted at `146-RESEARCH.md:2101-2108`. This file's `0x0B` row (`:66`) and its
`--pulse-us` interaction paragraph (`:136-137`) are the in-file style donors for the one new 6.25 V
sentence — it carries 4 of CLOSE-03's 5 topics already.

### `firestarter_app/README.md` — the exact lines `--pulse-us` inserts into

Current §Write options list, verbatim `:316-318`:
```
* `-b, --ignore-blank-check`: Ignore blank check before write (and skip erase).
* `-f, --force`: Force write, even if the VPP or chip ID don't match.
* `-a, --address <address>`: Write start address in decimal or hexadecimal.
```
Two pre-existing defects sit in exactly these lines: `-b`'s long name is shipped as **`--no-blank-check`**,
and it no longer skips erase (that is a separate `--skip-erase` flag). §Description `:322-323` repeats both
errors:
```
1. **Blank Check:** By default, the command checks if the EPROM is blank before writing. This can be skipped using the `--ignore-blank-check` option.
2. **Erase:** If the EPROM is not blank, it may need to be erased before writing. This step is also skipped if `--ignore-blank-check` is used.
```
Shipped surface (`cli_handlers.py:546-610`) is seven options: `-b/--no-blank-check`, `--skip-erase`,
`-f/--force`, `-a/--address`, `--vpe-as-vpp`, `--pulse-us`, `--skip-sdp-unlock`. The `--pulse-us` help
text is quotable verbatim from `cli_handlers.py:590-593` and already states the provenance narrowing:
> *"Override the database program-pulse width for this run (microseconds, 1-65535). This bound is minipro parity (`-o pulse=N` is a uint16), NOT a wire-type or hardware limit -- see `write()`'s docstring."*

§Eprom Configuration (`:530-571`) is the donor style for the database-supplied-pulse topic; its W27C512
example JSON already carries `"pulse-delay": "0x0064"`.

---

## Modified: `tools/catalog/messages.toml` (config, codegen source)

**Edit ONE file** — `./tools/catalog/messages.toml` (meta, canonical). The sync script propagates to the
other two. Current stanza, `:920-925`:
```toml
[[debug.messages]]
id     = 0x15
name   = "DBG_PULSE_DELAY_MISMATCH"
format = "Mismatch, retrying with increased pulse delay from %d to %d"
params = [{ type = "u8" }, { type = "u8" }]
```
`MSG_INFO_RETRIES` (`:161-167`, `id = 0x51`, `format = "Number of retries: %d"`) is **recorded as orphaned,
not removed**.

**Constraint on the replacement text:** keep `params = [{ type = "u8" }, { type = "u8" }]` — two `u8` — or
the change stops being wording-only and becomes a wire-format change.

**Regen command (one command, from `/workspaces`):**
```bash
bash tools/catalog/sync_to_subrepos.sh
```

**Measured diff shape to assert** (proved empirically in RESEARCH against temp copies):
- `firestarter/include/messages.h` — **zero diff** (ID-only, `:137` is `#define DBG_PULSE_DELAY_MISMATCH 0x15`)
- `firestarter_app/firestarter/messages.py` — **exactly one changed line, `:1072`** (the `format=` line;
  `:1070` is the `name=` anchor CONTEXT cites)
- `tools/catalog/messages.toml` ×3 — one changed line each, all three SHA-identical afterwards

**Two traps: do not cite the script's own output as evidence.** `sync_to_subrepos.sh`'s regen
confirmations are gated on a self-comparison (`diff -q X X`), and `codegen.py --check` returns at
`codegen.py:704-713` **before** any target comparison — there is no drift-detection mode. Verify with
`git diff --numstat` per repo. A nonzero `messages.h` diff is stop-and-report (it would mean an id moved).

---

## Modified: `.planning/{ROADMAP,PROJECT,STATE}.md` — the `⚠ CORRECTION` block sites

**⚠ These three files are the live, currently-GREEN target set of
`.planning/phases/130-…/check_record_corrections.py`** (its `_DEFAULT_TARGETS`, `:163-171`, are
`_REPO_ROOT`-absolute). It ran clean this milestone:
```
PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md, … ;
      exempt hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6,
                               'inline-allow': 10, 'superseded': 12}
```

**The recognized block syntax, verbatim from the gate's own source:**
```python
# check_record_corrections.py:284 — opens a multi-line labeled block
_LABEL_OPENER_RE = re.compile(r"^\s*(?:[-*]\s+)?\*\*⚠")

# :289-292 — a label token on the hit line itself
_LINE_LABEL_RE = re.compile(
    r"⚠\s*(?:CORRECTION|RESEARCH CORRECTIONS|SUPERSEDED|DESIGN)\b|^SUPERSEDED\b",
    re.IGNORECASE,
)

# :303 — closes the block at the first heading, rule, non-opener bold line, or top-level bullet
_BLOCK_CLOSER_RE = re.compile(r"^#{1,6}\s|^---\s*$|^\*\*(?!⚠)|^\s*-\s+")
```
So a valid opener is `**⚠ CORRECTION …` at line start (optionally list-marked), and the block **extends
forward** to the next heading / `---` / bold line / top-level bullet. **The block must therefore sit AFTER
the text it corrects, never before it.** Live instance to copy: `.planning/PROJECT.md:470`:
```markdown
**⚠ CORRECTION (2026-08-02) — Phase 130 close: six research corrections carried into this record.** …
```

**The recorded trap, and why appending beats inserting.** Exemption mechanism 3 is
`<!-- recordscan:supersedes needle=<label> lines=<n,n,…> reason: … -->` — an explicit enumerated list of
**1-based line numbers in the same file** — and the live run reports **`'superseded': 12`** active. Any
insertion that shifts line numbers above such a marker silently orphans it: the named lines stop holding
the needle and the real needle line becomes `unlabeled`. Phase 146 inserts prose into **all three** files.
Therefore: **append correction blocks at the end of the relevant section** wherever the choice exists, and
re-run the gate after every insertion, recording the exempt-hit tally before and after.

**Correction sites, current text (measured):**

| Site | Current text (excerpt) |
|---|---|
| `ROADMAP.md:167` (spine) | *"HOST (143) is independent of 140–142 (different repo) and can run in parallel with them"* |
| `ROADMAP.md:380` | *"**Depends on**: Phase 138 …. Independent of Phases 140–142 (different repo); converges with them at Phase 144's cross-repo constants-parity leg."* |
| `PROJECT.md:212` and `:213` (F-140-05, **two** rows) | `` \| `0x07` \| `handle->pulse_delay` \| 25 \| `3 × N × pulse`, cap 75 ms \| … `` and the `0x08` row's `` `3 × N × pulse` `` — shipped `overprogram_factor` is `0` on both |
| `PROJECT.md:216` (candidate 8th, surfaced not decided) | *"**Faster than today in the typical case** — the current code can make 20 full block passes."* — a comparative claim 145 D-08 forbids |
| `PROJECT.md:176-181` (F-140-07) | *"…cap accumulated program time per byte at 50 ms, since `100 × 500 µs = 50 ms` is exactly the classic 2716 total programming time."* — TI TMS 2516 gives total programming time as **100 seconds**; 50 ms is per-location `t_w(PR)` TYP |
| `STATE.md:67`, `REQUIREMENTS.md:20`, gh#15 comment body line 39 | the same F-140-07 justification, including the **public** copy |

Note `ROADMAP.md`, `PROJECT.md` and `STATE.md` carry 50 / 66 / 29 forbidden-phrase hits respectively and
are correctly **not** claim-gate targets — the `⚠ CORRECTION` prose written into them is scanned by the
record gate, not by `146-check-claims.py`.

---

## Shared Patterns

### Fail-closed, never-vacuous exit-code contract
**Source:** `139-check-claims.py:249-282` (order of operations) + `:35-47` (docstring exit-code contract).
**Apply to:** both new scripts. Self-check first → resolve → never-vacuous → fail-closed missing target →
scan → bucketed report. No exit-0-on-nothing-scanned path anywhere.

### Startup self-check as a substitute for a cross-phase-copy test
**Source:** `139-check-claims.py:148-181`.
**Apply to:** both new scripts. It is the run-time equivalent of the mandatory paired-test legs, moved
inside the script so a future copy fails loudly on first run.

### Cite by `file:line` + finding id, never by quotation (D-14)
**Source:** `122-LEDGER.md:39` / `137-LEDGER.md:93-94`'s `FORBIDDEN` key entry.
**Apply to:** all five gate targets and `146-CORRECTIONS.md`. The self-reference trap tripped all six
`125-0N-SUMMARY.md` files; `145-BENCH-LOG.md:2709` is this phase's live instance.

### Subprocess-driven negative fixtures (anti-hollow)
**Source:** `test_check_permitted_claims_v130.py:1-14, 68-87`.
**Apply to:** `test_check_claims_v131.py`. Legs 1–9 subprocess; only introspection legs import by path.

### Both readings stated, never silently reconciled
**Source:** `137-LEDGER.md:71-76` (four-vs-six step count) and `:100-102` (re-measured live, agreement
stated as re-confirmation).
**Apply to:** `146-LEDGER.md`'s three counting discrepancies and the seven corrections' three
does-not-hold-as-stated verdicts.

### `git diff --numstat`, never `git diff | grep -c '^[+-][^+-]'`
**Source:** 145-08 substitution #5 (the `-` marker collides with the markdown list bullet; a genuinely
changed file measured as zero changed lines).
**Apply to:** every doc-edit and record-edit blast-radius assertion in this phase.

### Capture the script's own exit status, not a pipeline's
**Source:** RESEARCH's measured case — `python3 … | tail -6; echo "EXIT=$?"` printed `EXIT=0` for a script
that had just printed `FAIL:`.
**Apply to:** the plant-and-revert transcript and every `<automated>` verify leg.

---

## No Analog Found

| File | Role | Data flow | Reason |
|---|---|---|---|
| `_CAVEAT_RULES` / `_required_caveats_for()` inside `146-check-claims.py` | gate mechanism | transform | D-11's per-file caveat map is the **only** genuinely new mechanism in the phase. 139/137/123/122 all apply caveats uniformly. Draft exists at `146-RESEARCH.md:2079-2093`; needs two new introspection legs (every default basename has a rule entry; unknown basename → full set). |
| `146-CORRECTIONS.md` as a **register** | record | table | v1.23 D-05 shipped blocks only; no prior close produced a consolidated register. Row shape is drafted, section order is Claude's (D-05 fixes four fields, not the table shape). |

---

## Metadata

**Analog search scope:** `.planning/phases/{122,123,130,137,139,145}-*/`, `.planning/{ROADMAP,PROJECT,STATE}.md`,
`firestarter/{CLAUDE.md,doc/PROTOCOLS.md,README.md}`, `firestarter_app/README.md`, `tools/catalog/`.
**Files read this session:** `139-check-claims.py` (full, 331 ln), `137/test_check_permitted_claims_v130.py`
(full, 350 ln), `137/fixtures/` (all 5), `137-LEDGER.md:1-125`, `130-…/check_record_corrections.py`
(targets + all three exemption mechanisms), `139-GH15-COMMENT.md:48-58`, `139-GH15-ORIGINAL-CRITERIA.md`
(full), `139-CITATIONS.md` (heading spine), release-note heading spines ×5, and the exact modification
sites in all four sub-repo/config targets.
**Pattern extraction date:** 2026-08-17
