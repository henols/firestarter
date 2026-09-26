# Phase 130: Close — Honesty Ledger, Claim Gate, Release Decision - Pattern Map

**Mapped:** 2026-08-02
**Files analyzed:** 12 (7 new markdown artifacts, 2 new Python files + fixtures, 5 modified records/sources)
**Analogs found:** 11 / 12 (one deliberate no-analog: the D-16 one-shot proof)

This is a **closing/documentation phase**. Almost every "file to create" has a committed analog from
the v1.22 close (Phases 122) or from this milestone's own Phases 123/128/129. Nothing below needs to
be re-derived; every excerpt was read from disk this session.

---

## File Classification

| New/Modified file | Role | Data flow | Closest analog | Match quality |
|---|---|---|---|---|
| `130-LEDGER.md` (new) | record / honesty ledger | transform (requirements + measurements → claim classes) | `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md` | **exact** (same requirement, same close shape) |
| `130-DECISION.md` (new) | record / pre-flight decision | request-response (measure → verdict → accepted sequence) | `122-…/122-DECISION.md` | **exact** |
| `130-RELEASE-NOTES-fw.md` (new) | outward-facing prose | one-way publish | `122-…/122-RELEASE-NOTES-fw.md` (committed draft) + live b14 fw body | **exact** |
| `130-RELEASE-NOTES-app.md` (new) | outward-facing prose | one-way publish | `122-…/122-RELEASE-NOTES-app.md` + live b14 app body | **exact** |
| `130-NONREGRESSION.md` (new) | sweep record | batch (execute → tabulate → discharge criteria) | `128-release-asset-fold/128-NONREGRESSION.md`, `129-…/129-NONREGRESSION.md` | **exact** |
| channel-verification transcript (new, name at discretion) | verification transcript | request-response (query public surface → record) | `122-…/122-CHANNELS.md`; secondary `115-…/115-VALIDATION.md` | **exact** (`122-CHANNELS.md`); `115-VALIDATION.md` is a *validation-strategy* doc, not a transcript — weaker |
| `check_record_corrections.py` (new) | CLI gate / checker | file-I/O scan → exit code | `.planning/phases/123-…/check_permitted_claims.py` | **role-match** (copy CLI/exit-code/arming shape, **not** the phrase table or the caveat logic) |
| `test_check_record_corrections.py` (new) | test | subprocess + fixture | `.planning/phases/123-…/test_check_permitted_claims.py` | **exact** |
| `fixtures/` (new, ≥2 planted + ≥1 clean control) | test data | file-I/O | `.planning/phases/123-…/fixtures/` (5 files) | **exact** |
| `check_permitted_claims.py` (**modify** — C-2 `_DEFAULT_TARGETS` repoint) | config constant in existing gate | — | the file itself (lines 74–91) | self |
| `test_check_permitted_claims.py` (**modify** — C-3 narrow the side-effect glob) | test | — | the file itself (lines 299–304) | self |
| `firestarter/platform/py32f071/src/usb_cdc.c` (**modify** — 2 `#define`s + warning comment) | firmware source / config | — | the file itself (lines 1–45) | self |
| `.planning/v1.23-FLASH-PATH-DECISION.md` §5 + `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` §5 (**modify**, lockstep) | shared record section | exact-string-equality sync | each other | self (byte-identical pair) |
| ROADMAP v1.24–v1.27 byte-unchanged proof (D-16) | one-shot procedure | — | **no analog by design** (D-16 forbids a checker) | none |

---

## Pattern Assignments

### `130-LEDGER.md` (record, transform) — analog `122-LEDGER.md`

`122-LEDGER.md` is 140 lines. **Actual section skeleton, in order:**

1. `# v1.22 Honesty Ledger — <milestone name>` (H1)
2. Identity header block (bold key/value lines, no heading): `**Milestone:**`,
   `**Firmware inbound-merge commit:**`, `**Host inbound-merge commit:**`, `**Published cut tag:**`,
   `**Version-string caveat:**`, `**Oracle:**`, `**Generated:**`
3. `**Composes with (cross-reference only — no data copied):**` + bullet list
4. A one-paragraph "referenced and verified here, never edited" note for the ledger it must NOT touch
5. `## The ceiling, quoted verbatim`
6. `## Status / claim key`
7. `## The nine claim classes` (one table)
8. `## The four 0x0D pinouts — composition, and why "all four pinouts" needs a qualifier`
   (the milestone-specific "qualifier" section)
9. `## Mechanism corrections recorded here, not in REQUIREMENTS.md` (numbered list)
10. `## What this milestone chose not to prove` → `### Deferred by decision or on research grounds`,
    `### Two trade-offs Phase 121 recorded and owned`, `### One trade-off this phase itself owns`
11. `## What no test, gate or review in this phase can close` (the three-way split)
12. `## Scanner status`
13. Footer: `*Phase: …*` / `*Written: … (Plan 122-05)*`

**Status-key block, verbatim (122-LEDGER.md:34-39)** — this is the v1.22 axis D-12 keeps:

```markdown
## Status / claim key

- **`PERMITTED`** — a wording backed by a measured, re-runnable software artifact (a trace, a test, a source scan, a size report).
- **`CONTEXT-ONLY`** — measured, and cited for context, but explicitly not a gate — Phase 119 D-16 declined to make it one.
- **`COMMUNITY-CORROBORATED`** — a real-silicon datapoint supplied by a third party, provenance stated plainly, not independently reproducible on this bench.
- **`FORBIDDEN`** — the ceiling's forbidden claim. It appears in this ledger only as a citation of what is *not* claimed, never as prose asserting it.
```

**Table header + one representative claim row, verbatim (122-LEDGER.md:47-50):**

```markdown
| Class | Permitted wording | Evidence (measured, with source) | Explicitly does NOT prove |
|---|---|---|---|
| **1. Per-pinout emission byte-exactness** `PERMITTED` | The SDP lock and unlock sequences are emitted exactly as specified, verified byte-exact by golden register trace across all four `0x0D` pinouts. | Phase 116 trace harness + Phase 119 golden traces (`test_eeprom28c_sdp.cpp`); re-confirmed green on the merged tree by `122-NONREGRESSION.md` §3 rows 1–4. Coverage figure: **66 of 84** chips individually trace-covered — not the full 84-chip bucket, and never rounded up. | That any silicon accepted the sequence, entered or left the protected state, or that the magic addresses are correct for every family member — **SDP-F7** leaves them `UNVERIFIED` for AT28C040 / AT28C16 / AT28C04. |
```

**D-09's delta against this known shape:** keep columns 1/2/3/4; replace the flat "nine claim
classes" grouping with `###` sub-headings per **evidence tier** (CI-compile-only, AVR-measured,
native-simulated, mock-only, real-published-artifact, decision-only-unverified), each holding its own
table; and extend the `Class` cell to carry **both** axes (D-12): the v1.22 status token
(`PERMITTED` / `CONTEXT-ONLY` / `FORBIDDEN`) **plus** Phase 129's sourcing tag (`[VERIFIED]` /
`[CITED: …]` / `[ASSUMED — …]` / `[UNVERIFIED-UNTIL-SILICON]`).

**Self-reference trap — the exact wording v1.22 used to escape it (122-LEDGER.md:28), copy this
technique:**

```markdown
> **Forbidden claim:** cited by location rather than reproduced — `.planning/REQUIREMENTS.md:152`. This ledger does not repeat that sentence's exact wording: doing so would trip this same document's own claim scanner (`check_permitted_claims.py`), which matches a phrase's shape regardless of quotation context, by design. That is the gate working as intended, not a defect to route around. The permitted claim above is safe to reproduce because it contains no trigger shape.
```

**Scanner-status paragraph, verbatim (122-LEDGER.md:135)** — the "mechanizable half only" sentence
the new ledger must carry in its own voice:

```markdown
This document is one of `check_permitted_claims.py`'s five default outward-facing targets. It is required to exit 0 against this file, carrying the required silicon caveat above and containing zero forbidden-phrase matches, before this file is committed. **A green result from that scanner is the mechanizable half of ROADMAP criterion 4 only** — per the scanner's own module docstring and the split stated in the section immediately above.
```

⚠ Every one of the four contracted artifacts must contain the literal caveat
`no PY32F071 hardware exists` (whitespace-tolerant, document-level, **not** proximity-scoped) —
`check_permitted_claims.py:154-157`.

---

### `130-DECISION.md` (record, request-response) — analog `122-DECISION.md`

**Skeleton, in order (heading list read from disk):**

```
# Phase 122 — CLOSE-03: Recorded `beta`-push Decision + Pre-flight Evidence
**Purpose:** …  (the "this file's own commit timestamp is the evidence" paragraph)
## Pre-flight state (measured <UTC timestamp range>)
   ### 1. Branch tips
   ### 2. `origin/beta` tips (after `git fetch origin` in each repo)
   ### 3. Ahead/behind counts (`git rev-list --left-right --count HEAD...origin/beta`)
   ### 4. Merge-base / fork-point coincidence with `v1.21^{commit}` (C-9)
   ### 5. Version strings on both sides
   ### 6. Highest `3.0.0b*` tag and absence of `3.0.0b14`
   ### 7. Dry-run merge conflict probe (`git merge-tree --write-tree --messages HEAD origin/beta`)
   ### 8. `--ours` superset proof for the app conflict resolution
   ### 9. A5 gitlink baseline (meta repo, must stay unchanged at phase end — D-07)
   ### 10. Working-tree dirt, all three repos (`git status --porcelain`)
   ### No mutation occurred
   ### ⚠ Divergence from 122-RESEARCH.md
## The decision (CLOSE-03, D-05)
   ### The three options, all recorded (CLOSE-03 asks for accept/avoid/cleanup, not merely a plan)
   ### The accepted sequence, each step naming its owning plan and the CONTEXT constraint it satisfies
   ### Four facts the sequence depends on
   ### Out of scope for this phase (D-07)
## Summary of what this artifact proves
```

**Purpose paragraph, verbatim (122-DECISION.md:3-6)** — the load-bearing "decision precedes act"
framing constraint 1 needs:

```markdown
**Purpose:** CLOSE-03's text is literal — the accept/avoid/cleanup decision for the `beta` push
must be made and recorded **before any push**. v1.21's close skipped exactly this step and
auto-cut a stray `3.0.0b12`. This artifact's own commit timestamp is the evidence that the
decision preceded the act — nothing is pushed, merged, or published by this plan or this file.
```

**Pre-flight AGREES/DRIFTED pattern, verbatim (122-DECISION.md:12-19 + the item-1 table):**

```markdown
**`122-RESEARCH.md` is stamped valid only until ~2026-08-02, precisely because `origin/beta` moves
on any push. Every number below was re-measured live in this session, not copied from RESEARCH.**
Verdict per item: **AGREES** or **⚠ DRIFTED** against the recorded value.

Commands run were fetch-only (`git fetch origin`) plus read-only inspection
(`rev-parse`, `rev-list`, `merge-base`, `show`, `tag --list`, `merge-tree --write-tree`, `status
--porcelain`, `ls-tree`). No merge, checkout, commit, or push was executed against either
sub-repo.

### 1. Branch tips

| Repo | Branch | Tip SHA measured | Recorded (RESEARCH) | Verdict |
|------|--------|-------------------|----------------------|---------|
| `firestarter` | `v1.22-…` | `48c36e569c8ddfd3daa8aea7e55c5bbc79b48b08` | `48c36e5` | **AGREES** |
```

**Three-option table shape, verbatim header + the CHOSEN row (122-DECISION.md:238-243):**

```markdown
| Option | Disposition | Why |
|---|---|---|
| **ACCEPT** | **CHOSEN** | Both workflows fire unconditionally on a `beta` push carrying non-ignored paths … This is the *"do the cut FROM beta so the merge IS the cut"* option the v1.21 post-mortem named. |
| **AVOID** | **DECLINED** | … **No workflow trigger is edited by this phase, and `paths-ignore` is not weakened, in either repo.** |
| **CLEANUP** | **DECLINED** | The stray `3.0.0b12` prereleases **stay public** in both repos. … **No `--force` push, no history rewrite, and no deletion of any published artifact occurs in this phase.** |
```

**Accepted-sequence pattern — each step names its owning plan and the constraint (122-DECISION.md:246-268).**
Numbered list; each item is `**<action>** (plan 122-0N) — constraint N`. Two excerpts to copy
verbatim in shape:

```markdown
1. **This decision recorded and committed** (this plan, 122-02) — constraint 1 (CLOSE-03's literal
   text: the decision exists and precedes any push).
5. **A manual `gh workflow run publish.yml --repo henols/firestarter_app -f tag=<observed tag>`**
   for PyPI (plan 122-08) — constraint 7. The tag passed is the tag **observed** after CI cuts it,
   never assumed as `3.0.0b14` in advance.
```

Note for the planner: 130's tag ceiling is b14, so the **placeholder must stay `<observed tag>`** in
every command a task will run verbatim (constraint 5; RESEARCH C-15 / risk 11). Also 130 has
**0 behind in both repos**, so items 7/8 (`merge-tree` conflict probe, `--ours` superset proof) have
no subject and should be recorded as no-ops rather than invented. Item 9's gitlink section changes
meaning: D-04 **asserts** the gitlinks match the tips, it does not pin them unchanged.

---

### `130-RELEASE-NOTES-fw.md` / `130-RELEASE-NOTES-app.md` (outward-facing prose)

**Primary analog: the committed drafts `122-RELEASE-NOTES-fw.md` (83 lines) and
`122-RELEASE-NOTES-app.md` (74 lines).** They are byte-substantially what became the live b14 bodies
(verified this session with `gh release view 3.0.0b14 --repo henols/firestarter` and
`… henols/firestarter_app` — the published bodies open with the same H1 and same paragraphs).

**fw body section skeleton (122-RELEASE-NOTES-fw.md):**

```
# Firmware prerelease — <milestone one-liner>
   (opening paragraph: what assets are attached, how to install, `firestarter fw --install`)
## The headline: <the user-visible fix, in plain language>
## A second, separate defect fixed in the same area
## New capability: …
## What is proven, stated exactly
## What is NOT proven
## The capability boundary
## One honest datapoint from the community
## Feedback wanted
```

**app body skeleton (122-RELEASE-NOTES-app.md), opening verbatim (lines 1-8)** — note it leads with
the install command and states the zero-assets fact:

```markdown
# Host app prerelease — AT28C Software Data Protection lifecycle

`pip install --pre --upgrade firestarter`

This GitHub release carries no attached files — it is a tag-and-marker page only. PyPI is the
distribution channel for the host app; the command above pulls it. The matching firmware for this
release is published separately, and its three `.hex` files are what `firestarter fw --install`
pulls when you update your board.
```

**The two load-bearing sections to copy structurally (122-RELEASE-NOTES-fw.md:37-59):**

```markdown
## What is proven, stated exactly

The SDP lock and unlock command sequences are emitted exactly as specified, and this has been
checked byte-exact by golden register trace across all four `0x0D`-protocol pinouts this family
spans, with a documented and measured host-side timing assumption. …

## What is NOT proven

On this chip family the resulting protection state cannot be read back afterward, so neither
direction — locking or unlocking — can be confirmed once the command sequence has been sent. A
successful run means only that the command sequence was emitted; it does not mean the state
changed on the physical part.

The caveat this whole release turns on: **no AT28C silicon was tested.** Nobody working on this
project currently has an AT28C part on the bench. …
```

The v1.23 analogue of that last paragraph must use the **canonical caveat literal**
`no PY32F071 hardware exists` (see the checker excerpt below) — the phrase `no AT28C silicon was
tested` has no scanner status; `no PY32F071 hardware exists` is required by regex.

Per-body v1.23-specific content the planner must name (CONTEXT `<domain>` + D-11 + PCB-05):
the ceiling in substance, PCB-05's socket-empty instruction, the USB identity statement, and an
explicit "this image has never run on silicon and no PCB exists".

---

### `130-NONREGRESSION.md` (sweep record, batch) — analogs `128-NONREGRESSION.md`, `129-NONREGRESSION.md`

**Section skeleton (both files agree; 128's is the closer fit because it has a CI/operator-dispatch
half, which 130 also has):**

```
# Phase 128 Non-Regression Sweep — closing plan (128-10)
   header block: **Written:** / firmware branch + HEAD SHA / host branch + HEAD SHA / meta branch
   > blockquote ceiling paragraph
   **Re-execution pledge.** …
## 1. The claim, as precise statements
## 2. Locally provable, executed now        (129 splits into ### per-repo sub-sections)
## 3. CI-only, discharged by the operator-authorised rehearsal dispatches
     (129's counterpart: "## 3. Deliberately empty — no CI dispatch, no operator gate")
## 4. The operator dispatch procedure     (+ "### 4a. Procedure defect discovered during dispatch")
     (129: "## 4. Success criteria" with a "### Criterion N" per criterion)
## 5. What this phase does NOT claim       (129: "## 5. Decision coverage — D-01…D-18")
## 6. Precedent and prior art
## 7. Criterion discharge                  (129: "## 7. What this phase does NOT claim")
## 8. Deviations recorded during Task 3
   (129 additionally ends with "## Claim ceiling" and "## Sweep Summary")
```

**Header + ceiling blockquote + re-execution pledge, verbatim (128-NONREGRESSION.md:1-25)** — copy
this exact opening shape, it is what makes the sweep auditable:

```markdown
# Phase 128 Non-Regression Sweep — closing plan (128-10)

**Written:** 2026-08-01
**Firmware branch (`firestarter`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`0de57da3c9edfb40f86eee8b0964e0f1bcdd8559`
**Host branch (`firestarter_app`):** `v1.23-py32f071-integration` · **HEAD at this sweep:**
`cc9452f4db9a814ffb221bab767c24db67288365`
**Meta branch:** `gsd/v1.23-py32f071-integration`

> **No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon,
> and nothing in it can. Everything below is about **publication**: that a file with a
> particular name, carrying a particular version string, becomes a downloadable release
> asset. Nothing here says the published image runs, boots, or installs. The permitted claim
> is exactly one sentence wide.

**Re-execution pledge.** Every row in §2 was executed in **this session** (Plan 128-10's
Task 1), against the trees exactly as they now stand — nothing is copied from any of this
phase's nine prior plans' (128-01 through 128-09) SUMMARY files. Where a prior SUMMARY made a
claim (an exit code, a test count, a parsed literal), this document re-checked it
independently against the live tree and says so below.
```

`130-NONREGRESSION.md` additionally owns three things named only in this phase: D-07's toolchain
reproduction recipe, D-16's one-shot before/after SHA-256 proof for ROADMAP lines 29–32 (plus the
recorded reason no checker exists), and RESEARCH C-17's A-5 discharge-at-Phase-124 record.
For the D-16 proof, `129-NONREGRESSION.md` §"ARM byte-identity row (executed locally in this
session)" (`:101+`) is the shape for a hash-based before/after record.

---

### channel-verification transcript — analog `122-CHANNELS.md`

**Skeleton (verbatim heading list):**

```
# Phase 122 Plan 08 — Both-Channels-Public Verification Transcript
## 1. The PyPI dispatch that made this verification possible
## 2. Channel (a) — PyPI, the host app's sole distribution channel
   ### The eventual-consistency caveat (explicit, not a failure)
## 3. Channel (b) — the firmware GitHub prerelease (carries the actual `.hex` deliverable)
## 4. Presence-only — the app's own GitHub release (not an install path, recorded as expected)
## 5. A green workflow tick was explicitly NOT accepted as evidence for either channel
## 6. No stable release was published
## 7. No community comment has been posted at this point
## 8. Summary verdict
## Self-verifying facts for downstream automation
```

§5 is the section constraint 7 exists for; §3 is where D-03's `firestarter_py32f071.hex`
asset-presence assertion belongs.

`115-VALIDATION.md` is a **weaker** analog — it is a validation *strategy* document
(`## Test Infrastructure`, `## Sampling Rate`, `## Per-Task Verification Map`, `## Wave 0
Requirements`, `## Manual-Only Verifications`, `## Validation Sign-Off`), not a channel transcript.
Use it only if the phase chooses the "named checks in a plan's task list" option from Claude's
Discretion.

⚠ v1.22 shipped `122-CHANNELS.md`, `122-CUT.md` and `122-DELIVERY.md` **outside** the scanned target
set. That precedent covers adding an unscanned fifth artifact without amending `_DEFAULT_TARGETS`
(RESEARCH §"The Four-Artifact Contract").

---

### `check_record_corrections.py` (new checker) — analog `check_permitted_claims.py`

Copy the **CLI / exit-code / arming / seam shape**. Do **not** copy `FORBIDDEN_PATTERNS`,
`REQUIRED_CAVEAT_*`, `PY32_TOKEN_RE` or `PROXIMITY_WINDOW` — those are the outward-facing
overclaim concern, and D-08 explicitly refuses to conflate the two.

**Module docstring shape** — `check_permitted_claims.py:1-66` has, in order: a one-sentence purpose
naming the exact targets; a "Distilled from …" provenance paragraph; an `Exit codes:` block; an
`**Explicit non-claim (load-bearing):**` paragraph; a `**Phase 130 coupling (load-bearing):**`
paragraph; a design-rationale paragraph (`**Why line-scoped proximity …**`); and a RESEARCH-assumption
paragraph. The new checker needs the analogous set, with its own rationale paragraphs for
**label-awareness (correction *and* history blocks)** and the **self-reference exemption** (C-7, C-8).

**Path constant + default-target list, verbatim (lines 68-91)** — including the anti-wildcard warning
comment, which is exactly the guard the new checker needs against its own `fixtures/`:

```python
import os
import re
import sys

# Module-top path constant (mirrors v1.22's `check_permitted_claims.py` and
# `check_note_append_only.py`'s shape).
_HERE = os.path.dirname(os.path.abspath(__file__))

# Explicit four-element default target list -- the v1.23 closing artifacts,
# NAMED NOW per D-15, seven phases before Phase 130 writes them. NEVER
# pattern-based and NEVER discovered by walking a directory tree. The
# `fixtures/` subdirectory deliberately contains violating text
# (planted_py32_overclaim.md, planted_missing_caveat.md) and must never be
# reachable from this default set -- if a future edit turns this into a
# wildcard-expanded or tree-walked set, the fixtures directory would poison
# every default-mode run. See the module docstring's "Phase 130 coupling"
# paragraph: Phase 130 must produce exactly these four names, or amend this
# list in the same commit that renames one.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "130-LEDGER.md"),
    os.path.join(_HERE, "130-DECISION.md"),
    os.path.join(_HERE, "130-RELEASE-NOTES-fw.md"),
    os.path.join(_HERE, "130-RELEASE-NOTES-app.md"),
]
```

⚠ **This is the C-2 bug.** `_HERE` is the *Phase 123* directory, so those four paths resolve to
`.planning/phases/123-non-regression-baselines-gate-hardening/130-LEDGER.md` etc. The new checker's
own default targets are the six planning files (`PROJECT.md`, `STATE.md`, `ROADMAP.md`,
`REQUIREMENTS.md`, `notes/py32f071-port-branch-state.md`) — all **outside** its own directory — so it
must resolve them relative to a repo root, not `_HERE`, or it will inherit the identical defect.

**Env seam, verbatim (lines 93-104)** — note the `.get()`-with-no-default rationale and the
import-time binding:

```python
# Env-override seam … lets the paired pytest point this checker at
# deliberately-violating fixtures under fixtures/ without editing a real
# closing artifact. `os.environ.get(...)` with NO default is deliberate --
# it must return None when FIRESTARTER_CLAIMSCAN_TARGETS is absent from the
# environment, and the (possibly empty) raw string when present, so
# resolve_targets() below can tell "absent -> use defaults" apart from
# "present-but-empty -> zero targets, never a silent fall-back to defaults".
# Values are split on os.pathsep; empty segments are dropped.
FIRESTARTER_CLAIMSCAN_TARGETS = os.environ.get("FIRESTARTER_CLAIMSCAN_TARGETS")
```

Use a **new, distinct env-var name** for the new checker (e.g. `FIRESTARTER_RECORDSCAN_TARGETS`) —
the docstring's own RESEARCH-A3 paragraph (lines 59-65) says reuse is only safe while two checkers
never coexist in one process, and these two will.

**`resolve_targets`, verbatim (lines 202-215)** — the precedence contract test 9 pins:

```python
def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS env seam if the variable is present in
    os.environ (checked via `is not None`, not truthiness -- an explicitly
    empty value must resolve to zero targets, never a silent fall-back to
    defaults); else `_DEFAULT_TARGETS`.
    """
    if argv:
        return list(argv)
    if FIRESTARTER_CLAIMSCAN_TARGETS is not None:
        return [p for p in FIRESTARTER_CLAIMSCAN_TARGETS.split(os.pathsep) if p]
    return list(_DEFAULT_TARGETS)
```

**Bucketed failure printer, verbatim (lines 218-223):**

```python
def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")
```

**`main()` — never-vacuous guard hoisted above missing-target, then the all-or-nothing arming
branch, verbatim (lines 226-291).** This is the exact code CONTEXT's "producing three of four is a
hard failure by design" rests on:

```python
def main(argv):
    """Entry point: resolve targets, scan each, exit non-zero on any
    violation.

    Deliberate hardening over v1.22's ordering: the never-vacuous guard (an
    explicitly empty resolved target list) is checked FIRST, above the
    missing-target guard, rather than after it. …
    """
    targets = resolve_targets(argv)

    if not targets:
        # Universal never-vacuous guard: reached when argv or the env seam
        # explicitly resolves to zero targets. …
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1

    used_defaults = not argv and FIRESTARTER_CLAIMSCAN_TARGETS is None
    if used_defaults:
        # D-15 all-or-nothing arming. Arming applies ONLY to the default
        # target set … This is the difference between "the close has not
        # started" (zero of the four named artifacts exist; UNARMED, exit 0)
        # and "the close is half written" (one or more exist but not all
        # four; hard failure).
        existing_count = sum(1 for t in targets if os.path.isfile(t))
        if existing_count == 0:
            print(
                "UNARMED: none of the 4 named v1.23 closing artifacts for "
                "Phase 130 exist yet (130-LEDGER.md, 130-DECISION.md, "
                "130-RELEASE-NOTES-fw.md, 130-RELEASE-NOTES-app.md) -- the "
                "close has not started, so the claim gate has nothing to "
                "scan yet. This is expected before Phase 130 runs."
            )
            return 0
        missing = [t for t in targets if not os.path.isfile(t)]
        if missing:
            print(
                "FAIL: armed (at least one of the 4 named v1.23 closing "
                "artifacts exists) but not all 4 exist -- a half-written "
                f"close is a hard failure (D-15). Missing: {missing}"
            )
            return 1
    else:
        # Ordinary fail-closed guard for explicitly-named targets (argv or
        # env seam) -- the caller named these paths explicitly, so a
        # missing one is always a hard failure, never a skip.
        missing = [t for t in targets if not os.path.isfile(t)]
        if missing:
            print(
                "FAIL: scan target(s) not found on disk -- the gate cannot "
                f"vacuously pass with a target silently skipped: {missing}"
            )
            return 1
```

The PASS line and entry point, verbatim (lines 322-332):

```python
    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_present_count} file(s) carry the required silicon caveat "
        "(this PASS is the mechanizable half of the honesty criterion only "
        "-- see the module docstring's explicit non-claim)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

**Note on arming for the new checker:** the six planning files always exist, so all-or-nothing arming
has no subject — the new checker takes the ordinary fail-closed path only. Say so in its docstring
rather than copying an inert `UNARMED` branch.

---

### `test_check_record_corrections.py` + `fixtures/` — analog `test_check_permitted_claims.py` + `123-…/fixtures/`

**Module docstring shape (lines 1-38):** an anti-hollow rationale paragraph naming the project's own
v1.12 hollow-GATE-03 failure mode and the "real subprocess, never an in-process import" rule, then a
numbered `Coverage:` list — one entry per test, each stating what direction it proves.

**Subprocess harness, verbatim (lines 40-69)** — reuse this shape exactly:

```python
import os
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_SCANNER = _HERE / "check_permitted_claims.py"


def _run_scanner(targets=None, argv=None):
    """Invoke the scanner as a real subprocess.

    `targets`, when not None, sets FIRESTARTER_CLAIMSCAN_TARGETS to that
    exact string (so the empty string is reachable, per test 6) -- when
    None, the env var is left absent from the child's environment entirely,
    reaching the "variable absent -> use real defaults" path.
    """
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )
```

**Planted-violation fixture test, verbatim (lines 95-109)** — the exact assertion triple
(non-zero exit, `FAIL:` in stdout, the *label* named):

```python
def test_planted_py32_overclaim_flips_checker_to_failure():
    """The committed planted_py32_overclaim.md fixture MUST fail the gate,
    attributed to the bench-validated label -- a py32 token and the
    forbidden phrase co-occur on one line."""
    result = _run_scanner(targets="fixtures/planted_py32_overclaim.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted py32 overclaim.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "bench-validated" in result.stdout, (
        f"Expected the bench-validated label in output but got:\n{result.stdout}"
    )
```

**The "suppression is real, not accidental" pattern (lines 142-168)** is the single most important
one to copy for D-08's label-awareness: a clean control that *contains* the needle but must pass
(because it sits inside a labeled block), plus a tmp_path mutation that **moves the needle out of the
label** and proves the same text then FAILS. Without the second test, label-awareness is
indistinguishable from the needle never matching (Phase 129's unreachable-leg lesson):

```python
def test_d16_proximity_suppression_is_real_not_accidental(tmp_path):
    original = (_HERE / "fixtures" / "clean_avr_bench_control.md").read_text()
    lines = original.splitlines()
    bench_idx = next(i for i, line in enumerate(lines) if "bench-validated" in line)
    lines.insert(bench_idx, "The PY32F071 bring-up notes are inserted right here.")
    mutated = "\n".join(lines) + "\n"
    target = tmp_path / "mutated_avr_bench_control.md"
    target.write_text(mutated)

    result = _run_scanner(targets=str(target))
    assert result.returncode != 0, (
        "expected the mutated fixture … to FAIL -- if it still passes, D-16's "
        "suppression in test 3 cannot be distinguished from the pattern "
        f"simply never matching.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
```

Also copy: `test_never_vacuous_on_explicitly_empty_target_list` (lines 195-210 — asserts the
*specific message*, not just non-zero), `test_fail_closed_on_nonexistent_target` (218-229),
`test_positional_argv_overrides_the_env_seam` (312-325), and
`test_pass_line_names_every_scanned_file` (333-349).

**The side-effect guard that is currently RED (C-3), verbatim (lines 299-304):**

```python
    # This test must never create a real Phase 130 artifact as a side
    # effect -- everything above happened inside tmp_path only.
    real_phase_130_dir = _HERE.parent / "130-close-honesty-ledger-claim-gate-release-decision"
    assert not real_phase_130_dir.exists() or not any(
        real_phase_130_dir.glob("130-*.md")
    ), "test must not create a real 130-*.md artifact as a side effect"
```

Fix is **locator-only** (C-3): narrow `glob("130-*.md")` to the four contracted names. Do not delete
the guard; prove the narrowed guard still fires by planting a `130-LEDGER.md` in the real directory
(RED-preserving proof).

**What lives under `123-…/fixtures/` and what each file plants:**

| Fixture | Lines | Plants |
|---|---|---|
| `clean_control.md` | 12 | clean pass baseline; permitted claims + the caveat literal `no PY32F071 hardware exists` |
| `clean_control_second.md` | 14 | a second, *textually distinct* clean control, solely so the anti-skip test can assert both basenames in one PASS line |
| `clean_avr_bench_control.md` | 22 | contains `bench-validated` **and** `hardware-validated` as true AVR sentences with no py32 token in the 3-line window → must PASS (the negative direction). Carries an in-file `<!-- WARNING: do not reflow this file … -->` comment protecting the blank-line spacing the test depends on |
| `planted_py32_overclaim.md` | 12 | `bench-validated` co-occurring with a `PY32F071` token on one line, caveat present and intact, so the failure is attributable to the forbidden phrase alone |
| `planted_missing_caveat.md` | 11 | zero forbidden phrases, caveat deliberately absent, so the failure is attributable to the missing-caveat bucket alone |

Every fixture opens with the same first line — copy it verbatim:

```markdown
<!-- test fixture for check_permitted_claims.py -- NOT a closing artifact; never add to _DEFAULT_TARGETS -->
```

…followed by an HTML-comment block stating **which single bucket** the fixture is designed to trip
and why the other buckets are held clean. D-08's fixture set needs at minimum: one clean control,
one planted stale figure, one **mislabeled** block, and one correctly-labeled-block control whose
needle must be skipped (plus the mutation test above).

---

### `firestarter/platform/py32f071/src/usb_cdc.c` (2 `#define`s + a source warning)

**Lines 1-27 verbatim** — the planner must specify an edit that keeps the `:20` / `:24` line
citations true, which means the warning comment goes **below line 24**, never above line 19
(RESEARCH C-4 item 3, risk 8):

```c
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "boards/py32f071_rurp_shield.h"
#include "rurp_platform.h"
#include "usbd_cdc.h"
#include "usbd_core.h"

#define FIRESTARTER_CDC_IN_EP 0x81U
#define FIRESTARTER_CDC_OUT_EP 0x02U
#define FIRESTARTER_CDC_INT_EP 0x83U
#define FIRESTARTER_CDC_MAX_PACKET_SIZE 64U
#define FIRESTARTER_USB_RX_CAPACITY 1024U
#define FIRESTARTER_USB_TX_CAPACITY 1024U
#define FIRESTARTER_USB_TIMEOUT_MS 100U

#ifndef FIRESTARTER_USB_VID
#define FIRESTARTER_USB_VID 0x36B7U
#endif

#ifndef FIRESTARTER_USB_PID
#define FIRESTARTER_USB_PID 0xFFFFU
#endif

#define FIRESTARTER_USB_CONFIG_SIZE (9U + CDC_ACM_DESCRIPTOR_LEN)
```

Consumed at lines 35-36 inside `USB_DEVICE_DESCRIPTOR_INIT(...)`. Both `#define`s are `#ifndef`-guarded,
so the edit is a value change only — no structural change, and no other VID/PID site exists in the
py32 tree. The file has **no existing comment style** for provenance notes; the nearest in-tree
convention for a warning-in-source is the block-comment rationale style used throughout
`check_permitted_claims.py` and `beta-build.yml` — a short `/* … */` or `//` block directly under the
`#endif` at line 25. Per C-6, word it as *"pid.codes' terms for `1209:0001` ask that source
referencing it warn the PID is not universally unique; this firmware does"* — never "required".

---

### `[SHARED:S4]` lockstep pair — `.planning/v1.23-FLASH-PATH-DECISION.md` §5 ↔ `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` §5

**Section markers and comparison semantics (from `firestarter/tests/test_flash_path_record_sync.py`,
41 legs, currently green, runs in NO CI leg):**

| Property | Value |
|---|---|
| Meta copy heading | `## 5. USB vendor and product identity [SHARED:S4]` — file line **194** |
| Firmware copy heading | `## USB vendor and product identity [SHARED:S4]` — file line **104** |
| Span | from the `## ` heading carrying the marker to the next `## ` heading (meta: `## 6. Socket empty …` at :216; fw: `## Socket empty …` at :126) |
| Heading itself | **excluded** from the compared body (which is why the differing `5. ` prefix is legal) |
| Normalisation | trailing blank lines stripped; **otherwise exact string equality**, no whitespace normalisation |
| Duplicate marker | `refusing to guess`; missing marker → `None` → non-vacuity `AssertionError` |
| Needles that must stay present in §5 | `0x1209`, `1209:0001`, `pid.codes`, `0x36B7`, `0xFFFF`, `Puya Semiconductor`, `usbd_cdc_if.c`, `pycdc.inf`, `0ed2f4b…`, `0x0448`, `py32_dfu.py`, `0xFE/0x01` |
| Re-run | `cd firestarter && FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` |
| Third copy of the ship-gate sentence | `test_flash_path_record_sync.py:345-348`, byte-exact constant `_L2_SHIP_GATE` — only in play if §5(c) is touched |

The two bodies are **currently byte-identical** (verified by reading both). Below are the two
sub-paragraphs D-11 must edit, quoted verbatim from **both** copies so the planner can specify a
character-identical replacement.

**§5(a) — meta `.planning/v1.23-FLASH-PATH-DECISION.md:196` and firmware
`FLASH-PATH-AND-PCB.md:106`, identical text:**

```markdown
**(a) What the descriptor currently presents, and where it came from.** `platform/py32f071/src/usb_cdc.c` defines `FIRESTARTER_USB_VID 0x36B7U` at line 20 and `FIRESTARTER_USB_PID 0xFFFFU` at line 24, consumed inside the `USB_DEVICE_DESCRIPTOR_INIT` call that builds `firestarter_cdc_descriptor`. The vendor id `0x36B7` is registered to Puya Semiconductor (Shanghai) Co., Ltd. `[CITED: the-sz.com USB ID database, accessed 2026-08-02 — single-source for the allocation holder]`. The exact pair is copied verbatim from the pinned SDK's own USB CDC example, `Projects/PY32F071-STK/Applications/USB_Device/USBD_Virtual_COM_Port/Src/usbd_cdc_if.c` lines 9–10 (`#define USBD_VID 0x36b7` / `#define USBD_PID 0xFFFF`), whose companion Windows driver INF `pycdc.inf` lines 28 and 31 matches it (`USB\VID_36B7&PID_FFFF`), both at `GIT_TAG 0ed2f4b4d3391eccfd4491006a30295fd78e32c2` `[VERIFIED: pinned SDK blobs]`. The consequence in one sentence a reader cannot misread: the board does not squat an empty slot — it presents **another company's registered vendor identity**, specifically the silicon vendor's, on a product they did not make. Every PY32 project that starts from Puya's CDC example without changing the descriptor presents the same pair, so a collision between two such devices on one host is a common failure mode rather than a hypothetical one. The values are undocumented *in this tree* — no comment in `usb_cdc.c` says where they came from — but they are fully traceable upstream, and this record is where that traceability now lives.
```

**§5(d) — meta `:206` and firmware `:116`, identical text.** RESEARCH C-4 item 1: this paragraph
asserts the opposite of what D-11 does and needs substantive rework, not a tweak:

```markdown
**(d) What this phase does and does not change.** `usb_cdc.c` is **not edited** this phase (D-06): PCB-04 is satisfied by a recorded decision plus a tracked obligation, which is what keeps this phase free of an ARM rebuild. Editing the descriptor follows the allocation, which follows an operator-filed public pull request, and it will need an ARM build to stay honest. The host-side fact, stated explicitly so PCB-04 is never read as a host bug: `firestarter_app/firestarter/py32_dfu.py`'s `find_dfu_interfaces` discovers DFU devices by **interface class** `0xFE/0x01`, not by vendor and product id, because the identity the Puya bootloader presents is not confirmed. Also, from the same family of confusions: `0x0448` is a bootloader-parameter table **device** id sitting beside a separate bootloader id column (Puya UM1504 Table 1-1) — it is not a USB product id, and this record confirms `REQUIREMENTS.md` §"Out of Scope"'s note ("Hardcoding `--usb-id 0448` as a default") is correct on that point. One further line: the datasheet §2.3 describes the boot loader as downloading through the USART interface and does not mention USB, while UM1504 documents USB DFU for this part — UM1504 is the authority for the USB DFU capability, and a reader who checks the datasheet first should not conclude the DFU path is imaginary.
```

**§5(c), for reference** — do **not** touch unless C-5 is resolved by amendment, in which case
`_L2_SHIP_GATE` is a third edit site (meta `:200-204`, fw `:110-114`):

```markdown
**(c) The ship gate.**

**Ship gate: no PY32F071 board ships, and no release advertises a USB identity, until a PID allocated under VID 0x1209 exists.**

This is deliberately a condition rather than a warning, so a future reader can fail it.
```

Both copies also close §5 with, identically (meta `:214`, fw `:124`):

```markdown
This section is shared verbatim with `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`; any edit must land in both copies in the same change.
```

---

## Shared Patterns

### The required caveat literal — applies to all four contracted artifacts
**Source:** `.planning/phases/123-…/check_permitted_claims.py:154-157`

```python
REQUIRED_CAVEAT_PROSE = "no PY32F071 hardware exists"
REQUIRED_CAVEAT_PATTERN = re.compile(
    r"no\s+PY32F071\s+hardware\s+exists", re.IGNORECASE
)
```

Document-level, not proximity-scoped. Any of the four artifacts missing it is a hard failure.

### The self-reference / negated-honesty trap — applies to the ledger, both release bodies, and the new CLOSE-01 checker
**Source:** `check_permitted_claims.py:144-153` (verbatim)

```python
# Canonical required-caveat sentence fragment, and its whitespace-tolerant
# regex. Deliberate interaction, recorded here rather than "fixed" by
# weakening the pattern set above …: an honest negated phrasing such as
# "nothing about the PY32F071 is silicon-verified" contains BOTH a py32 token
# and a forbidden phrase in the same proximity window, so it WILL trip the
# `silicon-verified` forbidden pattern. The correct response when that happens
# is to reword the artifact to use the canonical caveat sentence below, not to
# narrow FORBIDDEN_PATTERNS or PY32_TOKEN_RE to dodge the alarm -- the
# canonical caveat exists precisely so authors have an approved way to say this.
```

**Apply to:** every outward-facing artifact (use `122-LEDGER.md:28`'s cite-by-file:line technique),
and to the new checker's design (C-8: `ROADMAP.md:2468` quotes three of the new checker's own
needles, so an explicit success-criteria/self-reference exemption is a first-class requirement with
its own fixture).

### "Mechanizable half only" non-claim — applies to the ledger, `130-NONREGRESSION.md`, and every SUMMARY
**Source:** `check_permitted_claims.py:36-41` (verbatim)

```
**Explicit non-claim (load-bearing):** a green run of this gate is the
mechanizable half of the milestone's honesty criterion ONLY. It cannot
detect an implied overclaim, a misleading omission, or wrong tone. A green
run of this gate must never be reported, in any SUMMARY, ledger entry, or
Phase 130 artifact itself, as by itself satisfying the milestone's honesty
criterion.
```

### Observed-not-computed tag — applies to `130-DECISION.md`, the channel transcript, and every command in a task list
**Source:** `122-LEDGER.md:6` (identity header) and `122-DECISION.md:270-275`

Header field shape: `**Published cut tag:** **`3.0.0b14`** — **observed, not predicted.** Read from
the actual published releases, not from the auto-increment arithmetic that happened to predict the
same value. Evidence: `gh release list --repo …` …`

No literal `3.0.0b15` may appear in any command intended to be run verbatim (constraint 5).

### Section-marker lockstep discipline — applies to any `[SHARED:S*]` edit
**Source:** `firestarter/CLAUDE.md` §"PY32F071 Flash-Path and PCB Documentation"

Five keys named in three places; enforced by `tests/test_flash_path_record_sync.py`, which
**runs in no CI leg** — re-running it locally is a stated obligation, and the record must not imply
CI coverage.

---

## No Analog Found

| File / work item | Role | Data flow | Reason |
|---|---|---|---|
| D-16's v1.24–v1.27 byte-unchanged proof | one-shot procedure inside `130-NONREGRESSION.md` | batch | **Deliberately** has no checker analog — D-16 records that "these four entries never change" is false as a standing invariant, so a permanent gate would ship pre-obsolete. Closest *shape* analog for a hash-based before/after record is `129-NONREGRESSION.md` §"ARM byte-identity row" (`:101+`) |
| The ROADMAP `## Milestones` renumber itself (CLOSE-03) | record edit | transform | No prior phase in this project renumbered a milestone slot; the only precedents are the 999.4–999.7 *promotion* retirements inside `ROADMAP.md`'s backlog section (cited by D-15) and line 34's existing `⚠ SUPERSEDED — this slot is RETIRED into v1.23 … Marker added 2026-07-31` marker, which is the wording model for the new retirement line |

---

## Metadata

**Analog search scope:** `.planning/phases/{115,122,123,128,129}-*/`, `.planning/`,
`firestarter/platform/py32f071/`, `firestarter/tests/`, live `gh release view` on both repos' b14.
**Files read this session:** 122-LEDGER.md (full), 122-DECISION.md (:1-80, :226-275),
122-RELEASE-NOTES-fw.md (:37-66), 122-RELEASE-NOTES-app.md (:1-20), 122-CHANNELS.md (headings),
128-NONREGRESSION.md (:1-40 + headings), 129-NONREGRESSION.md (headings), 115-VALIDATION.md (headings),
123/check_permitted_claims.py (full), 123/test_check_permitted_claims.py (full), all 5 fixtures,
usb_cdc.c (:1-45), FLASH-PATH-DECISION.md §5, FLASH-PATH-AND-PCB.md §5, firestarter/CLAUDE.md.
**Pattern extraction date:** 2026-08-02
