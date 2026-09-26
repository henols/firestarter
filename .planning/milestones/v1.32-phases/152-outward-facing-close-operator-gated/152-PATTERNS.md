# Phase 152: Outward-Facing Close (operator-gated) — Pattern Map

**Mapped:** 2026-08-21
**Files analyzed:** 15 (10 new in the phase dir, 3 hand-edited `.planning` record files, 2 sub-repo
merge surfaces that produce no file)
**Analogs found:** 13 / 15 with a named donor; 2 with a nearest-analog only

**Read this section first.** This is a publication/records phase. Nine of the ten new files have an
explicitly named donor, and **three of them are copy-and-rename jobs, not write-from-analog jobs.**
The distinction is load-bearing for plan-task shape and is stated per file in §"Pattern Assignments"
and summarised in §"Copy-and-rename vs write-from-analog".

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog / Donor | Match Quality | Job kind |
|---|---|---|---|---|---|
| `152-check-claims.py` | gate script (CLI, offline) | file-I/O + transform (regex scan → exit code) | `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py` (531 L) | **exact** | **copy + rename** (4 mandatory renames + 3 table edits) |
| `test_check_claims_152.py` | test (pytest, subprocess-driven) | request-response (subprocess in / rc+stdout out) | `.planning/phases/149-*/test_check_claims_v132.py` (721 L, 20 tests) | **exact** | **copy + rename** (basename MUST change) |
| `fixtures/*.md` | test fixture (markdown) | file-I/O | `.planning/phases/149-*/fixtures/` (11 files, 383–708 B) | **exact** | **copy + author 3 new** |
| `152-CLAIM-GATE-TRANSCRIPTS.md` | evidence record | batch (command → literal stdout paste) | `.planning/phases/149-*/149-CLAIM-GATE-TRANSCRIPTS.md` (274 L) | **exact** | write-from-analog (section skeleton copied) |
| `152-LEDGER.md` | record / honesty ledger | batch (live capture → table) | `.planning/phases/146-*/146-LEDGER.md` (452 L) + `137-*/137-LEDGER.md` | **exact** | write-from-analog |
| `152-GH12-COMMENT.md` | outward comment draft | publication (draft → `gh issue comment`) | `.planning/phases/137-*/137-GH12-COMMENT.md` (46 L) | **exact — D-14 says ADAPT** | **copy + adapt, commit the diff** |
| `152-GH21-COMMENT.md` | outward comment draft | publication | no exact donor; **tonal donor** `137-GH12-COMMENT.md:16-18`; **content oracle** RESEARCH §D-3 | role-match | write-from-analog |
| `152-GH11-COMMENT.md` | outward comment draft | publication | same as above; **content oracle** RESEARCH §D-4 | role-match | write-from-analog |
| `152-RELEASE-NOTES-app.md` | outward release body | publication (`gh release edit --notes-file`) | `.planning/phases/146-*/146-RELEASE-NOTES-app.md` (92 L) + `137-*/137-RELEASE-NOTES-app.md` §Removed | **exact** | write-from-analog (opening ¶ verbatim-reusable) |
| `152-RELEASE-NOTES-fw.md` | outward release body | publication | `.planning/phases/146-*/146-RELEASE-NOTES-fw.md` (112 L) | **exact** | write-from-analog |
| `152-MERGE-RECORD.md` | handoff record | batch (git/gh capture → instruction) | **no donor** — nearest is `146-CITATIONS.md`; shape fully specified by RESEARCH §E-5's 6 numbered items | no analog | write from RESEARCH §E-5 |
| `.planning/ROADMAP.md` | record (hand-edit) | transform (labelled correction block) | in-repo: `ROADMAP.md:604`, `:831` (146 CLOSE-04 blocks) | **exact** | hand-edit, one plan |
| `.planning/REQUIREMENTS.md` | record (hand-edit) | transform | in-repo: same block shape; **not** a `check_record_corrections.py` target | **exact** | hand-edit, one plan |
| `.planning/PROJECT.md` | record (hand-edit) | transform | in-repo: `PROJECT.md:358`, `:443`, `:461` (146 CLOSE-04 blocks) | **exact** | hand-edit, one plan — **scope shrank, see below** |
| sub-repo merges (fw, app, meta) | process | — | v1.31 PRs fw #52 / app #51 / meta #35; v1.30 PR #44 | role-match | no file; `commits_land_in:` |

### Two corrections to the assigned scope, measured 2026-08-21

1. **`152-VALIDATION.md` already exists** in the phase dir (alongside CONTEXT / RESEARCH /
   DISCUSSION-LOG). It is **permanently out** of `_DEFAULT_TARGETS`, like the other three.
2. **D-15's PROJECT.md work is almost entirely already done — by Phase 153.** RESEARCH §B-11 said to
   verify. Verified, and it is worse (better) than §B-11 states:
   - `PROJECT.md:45-47` already reads *"**three** firmware-touching workstreams"* with a
     `152-CONTEXT.md D-15` attribution note at `:47`. **Done.**
   - The workstream table **already carries row 7** for Phase 153 (`PROJECT.md:90`) and
     **workstream 4's description is already updated** (`:91` — *"The write-path half of that book is
     now closed by workstream 7 (Phase 153)"*). **Both done.** RESEARCH §B-11 listed these as
     remaining; they are not.
   - `ROADMAP.md:37` already carries the corrected three-workstream count.
   - **What genuinely remains for 152 in PROJECT.md:** only the Phase 121 D-12 premise correction.
     Grepped: `.planning` carries no labelled block correcting *"advertising `FLAG_CAN_ERASE` for
     these 84 chips is a false capability statement"*. Only the **code** comment was fixed (ERASE-07,
     `REQUIREMENTS.md:340` `[x]`). So the PROJECT.md plan is one block, not four.

---

## Pattern Assignments

### 1. `152-check-claims.py` (gate script, file-I/O + transform) — **COPY AND RENAME**

**Donor:** `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py`,
531 lines, measured GREEN today (`rc=0`, 9 targets).

**Enumerate these renames as explicit plan tasks** (the donor's own docstring `:23-54` mandates the
first four; items 5–7 are this phase's table work):

| # | Site | 149 value | 152 value |
|---|---|---|---|
| 1 | `_DEFAULT_TARGETS` (`:146-156`) | 9 enumerated entries | §C-7's list, enumerated, **never a glob** |
| 2 | Self-check prefix literal — in **both** the `startswith` call (`:350`) **and** its failure message (`:353`) | `"149-"` | `"152-"` |
| 3 | Env seam — the constant name (`:168`), the `os.environ.get` key (`:169`), the docstring (`:45`) and `resolve_targets` (`:374`) | `FIRESTARTER_CLAIMSCAN_TARGETS_149` | `FIRESTARTER_CLAIMSCAN_TARGETS_152` |
| 4 | Docstring + explicit non-claim, retargeted at the requirement id and the review that discharges the gap | PGSZ-05, "plan 08's human wording review" | **OUT-05**, and **D-03's per-artifact blocking operator gates** |
| 5 | `FORBIDDEN_PATTERNS` (`:179-253`) | 17 rows | +2 rows (`sdp-relock-as-shipped`, bare-flag companion), 1 row **modified** (`issue-closed`: drop `32`) |
| 6 | `REQUIRED_CAVEAT_PATTERNS` (`:259-268`) | 1 row | 2 rows (RESEARCH §C-6) |
| 7 | `_CAVEAT_RULES` (`:294-305`) | 10 basenames | one entry per `_DEFAULT_TARGETS` basename + the transcript's empty-set exemption |

**Imports + `_HERE` — transcribe verbatim** (`:118-128`):

```python
import os
import re
import sys

# Module-top path constant. This is the ONLY directory `_DEFAULT_TARGETS`
# below is ever built from -- never a sibling-directory string constant.
_HERE = os.path.dirname(os.path.abspath(__file__))
```

**Env seam — the load-bearing no-default `get`** (`:164-170`, transcribe verbatim, renamed):

```python
# `os.environ.get(...)` with NO default is deliberate: it must return None
# when the variable is absent from the environment so resolve_targets() below
# can tell "absent -> use defaults" apart from "present but empty -> zero
# targets, never a silent fall-back to defaults".
FIRESTARTER_CLAIMSCAN_TARGETS_152 = os.environ.get(
    "FIRESTARTER_CLAIMSCAN_TARGETS_152"
)
```

**`resolve_targets` — precedence, verbatim except the seam name** (`:360-378`):

```python
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_152 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_152.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True
```

**The self-check — verbatim, with the prefix literal in BOTH places** (`:341-357`):

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
        if not os.path.basename(entry).startswith("152-"):
            print(
                f"FAIL: _DEFAULT_TARGETS entry {entry!r} does not carry "
                "this phase's own 152- prefix -- this is the exact "
                "stale-name defect this self-check exists to catch"
            )
            all_local = False
    return all_local
```

**The fail-closed / never-vacuous guards in `main()` — verbatim** (`:448-467`). Note the order: the
self-check runs **first**, before target resolution.

```python
    if not _assert_default_targets_are_local():
        return 1

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

**The fail-CLOSED caveat default — verbatim** (`:308-320`). This is what makes an unknown basename get
the FULL caveat set, and it is the mechanism that bites posted mode (RESEARCH §C-9 point 1):

```python
def _required_caveats_for(path):
    """... Fails CLOSED on an unknown basename: a target with no
    `_CAVEAT_RULES` entry gets the FULL caveat set, never the empty set."""
    return _CAVEAT_RULES.get(os.path.basename(path), _ALL_CAVEAT_LABELS)
```

**`scan_text` — no window, no exclusion, no allow-marker** (`:410-423`, verbatim). Every match
anywhere in the text is a violation:

```python
    lines = text.splitlines()
    forbidden_hits = []
    for label, pattern in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(lines, start=1):
            for m in pattern.finditer(line):
                forbidden_hits.append((label, m.group(0), lineno))

    missing_caveat_labels = {
        label
        for label, _prose, pattern in REQUIRED_CAVEAT_PATTERNS
        if label in required_caveats and not pattern.search(text)
    }
```

**`_print_bucket` — 20-entry display cap, verbatim** (`:426-431`).

**The two new / one modified `FORBIDDEN_PATTERNS` rows.** Copy the donor's row shape (a
`(label, re.compile(...))` 2-tuple with a comment above it recording the measurement and the reason)
and use RESEARCH §C-4's derived pattern **exactly as written there** — note in particular that the
optional backtick must live **inside** the lookahead:

```python
    (
        "sdp-relock-as-shipped",
        re.compile(
            r"write\s+--sdp-relock"
            r"(?!`?\s*(?:(?:is|stays|remains|was)\s+)?(?:still\s+)?"
            r"(?:withdrawn|deferred|not\s+shipped|not\s+shipping|unavailable|absent))",
            re.IGNORECASE,
        ),
    ),
```

For `issue-closed`, the modification is **`32` dropped from the alternation** (RESEARCH §C-5), and the
donor's own precedent for how to record a narrowing is `proven-unqualified`'s comment at `:206-215` —
copy that comment *shape*: state what was measured, why the narrowing is a narrowing and not a
loosening, and what must not be widened.

```python
    # 149's row: r"gh#(?:21|32|11|12)\b(?:\s+\w+){0,3}\s+(?:closed|resolved|fixed)"
    # MODIFIED for 152 (152-RESEARCH.md §C-5): `32` dropped. D-05 REQUIRES this
    # phase to state that gh#32 is closed; the inherited row blocks the natural
    # phrasings of that measured 2026-08-08 fact. Narrowing to the true claim
    # class ("claiming an issue this milestone did not close is closed"), not a
    # loosening -- gh#21/#11/#12 all still fire, proven by three fixture legs.
    (
        "issue-closed",
        re.compile(
            r"gh#(?:21|11|12)\b(?:\s+\w+){0,3}\s+(?:closed|resolved|fixed)",
            re.IGNORECASE,
        ),
    ),
```

**Keep `proven-unqualified` VERBATIM** (`:216`) — RESEARCH §C-6 recommends no change, so no new
lookbehind derivation and no new fixture is owed for it (the two narrowing test legs still transcribe):

```python
    ("proven-unqualified", re.compile(r"(?<!software-)\bproven\b", re.IGNORECASE)),
```

#### The ANTI-PATTERN — read, do not copy

**Anti-donor:** `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py`

Two distinct fail-open shapes, both to be avoided:

**(a) The `_HERE`-resolves-to-a-sibling trap**, documented by 137 itself at `:51-67` (137 *avoided*
it; the file it names as the offender is v1.23's copy in Phase 123's dir):

> *"a prior claim-gate checker (v1.23's copy, hosted in Phase 123's own directory) named its four
> target artifacts against a **sibling** phase directory via a hardcoded string constant
> (`_PHASE_130_DIRNAME`). A naive future copy of that pattern into yet another phase directory
> silently resolves its targets somewhere else entirely — scanning nothing and exiting 0, a green that
> proves absolutely nothing."*

**(b) The `UNARMED: … return 0` branch — 137 DOES carry this one, at `:303-312`. DO NOT PORT IT:**

```python
    if used_defaults and len(missing) == len(targets):
        print(
            "UNARMED: none of Phase 137's 4 named closing artifacts exist "
            "yet (" + ", ".join(...) + ") -- ... not a failure."
        )
        return 0                      # ← exit 0 with nothing scanned
```

149's docstring `:103-108` states the rule to follow instead:

> *"There is deliberately **no branch that exits 0 when nothing was scanned.** Phase 137's checker
> carried one … it is not ported here, because an exit-0-on-nothing-scanned path is a green that
> proves nothing."*

---

### 2. `test_check_claims_152.py` (test, subprocess-driven) — **COPY AND RENAME**

**Donor:** `.planning/phases/149-*/test_check_claims_v132.py` — 721 lines, **20 tests, 0.82 s, green
today** (`python3 -m pytest test_check_claims_v132.py -q -o addopts=""`).

**Renames (enumerate as tasks):**

| # | Site | 149 | 152 |
|---|---|---|---|
| 1 | **the file's own basename** | `test_check_claims_v132.py` | **`test_check_claims_152.py`** — pytest's default `prepend` import mode **collides on a repeated basename** run from `/workspaces`. A second `test_check_claims_v132.py` would be an import collision, not a new suite. |
| 2 | `_SCANNER` (`:73`) | `"149-check-claims.py"` | `"152-check-claims.py"` |
| 3 | Env seam in `_run_scanner` (`:97-101`) | `FIRESTARTER_CLAIMSCAN_TARGETS_149` | `..._152` |
| 4 | `_import_scanner_module`'s arbitrary module name (`:114`) | `"check_claims_149_introspect"` | `"check_claims_152_introspect"` |
| 5 | `_CAVEAT_NEEDLE` (`:78`) | one literal | **two** needles (two required-caveat rows) |
| 6 | `test_armed_against_the_real_149_artifacts` | 149 artifacts | 152's artifacts — see the arming note below |
| 7 | `label_to_fixture` map in the meta leg (`:686-693`) | 6 labels | 152's added/modified labels |

**The subprocess runner — transcribe verbatim, renamed** (`:81-105`). This is the mechanism that makes
a green suite prove *the gate*:

```python
def _run_scanner(targets=None, argv=None):
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_152"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_152", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )
```

**The by-path importer — verbatim, renamed** (`:107-120`). Needed only by the introspection legs; the
gate's filename is not a valid Python identifier, which is why the behavioural legs stay subprocess-only:

```python
    spec = importlib.util.spec_from_file_location(
        "check_claims_152_introspect", str(_SCANNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

**The single-reason assertion discipline — copy this pattern into every plant leg** (`:158-184`). Each
plant must fail for **exactly one** reason, and the leg asserts the *absence* of the other bucket:

```python
    result = _run_scanner(targets="fixtures/planted_forbidden_claim.md")
    assert result.returncode != 0, (...)
    assert "FAIL:" in result.stdout
    assert "forbidden phrase match [confirmed-working]" in result.stdout, (...)
    assert "missing required caveat" not in result.stdout, (
        "This plant must fail for exactly ONE reason; a caveat bucket means "
        f"the fixture lost its caveat:\n{result.stdout}"
    )
```

**The fail-closed leg must NAME the absent target** (`:245-260`) — otherwise it cannot tell which
target was skipped:

```python
    assert "not found on disk" in result.stdout
    assert "fixtures/does-not-exist.md" in result.stdout, (
        "The not-found message must NAME the absent target, or this leg "
        f"cannot tell which target was skipped:\n{result.stdout}"
    )
```

**The meta leg — copy in full** (`:674-721`). It is the strongest single leg and it enforces **leg
isolation**, with a non-vacuity guard before any per-label assertion:

```python
    fixture_files = sorted(p.name for p in fixtures_dir.iterdir() if p.is_file())
    assert fixture_files, "fixtures/ must not be empty"
    label_to_fixture = { ... }                     # ← 152's added/modified labels
    all_labels = {label for label, _pattern in module.FORBIDDEN_PATTERNS}
    for label, fixture_name in label_to_fixture.items():
        assert label in all_labels, (f"{label!r} is not in FORBIDDEN_PATTERNS -- "
                                     "this test's own mapping is stale")
        ...
        other_labels = all_labels - {label}
        for other in other_labels:
            assert f"forbidden phrase match [{other}]" not in result.stdout, (
                f"{fixture_name} unexpectedly also tripped [{other}] -- leg "
                f"isolation is broken:\n{result.stdout}")
```

**The 20 legs to transcribe, by name** (all present in the donor; rename `149`→`152` where the name
carries a phase number):

`test_gate_exits_zero_on_the_clean_control` · `test_planted_overclaim_flips_the_gate_to_failure` ·
`test_planted_missing_caveat_flips_the_gate_to_failure` ·
`test_planted_bare_claim_word_flips_the_gate_to_failure` ·
`test_fail_closed_on_a_nonexistent_scan_target` ·
`test_never_vacuous_on_an_explicitly_empty_target_list` · `test_pass_line_names_every_scanned_file` ·
`test_positional_argv_precedence_beats_the_env_seam` · `test_armed_against_the_real_*_artifacts` ·
`test_default_targets_resolve_inside_this_phase_directory` ·
`test_default_targets_basenames_carry_this_phases_prefix` ·
`test_every_default_targets_basename_has_a_caveat_rule_entry` ·
`test_unrecognised_basename_resolves_to_the_full_caveat_set` ·
`test_caveat_exempt_basename_passes_without_either_caveat` ·
`test_caveat_exempt_basename_still_fails_on_a_forbidden_phrase` ·
`test_the_required_phrase_alone_does_not_trip_the_narrowed_proven_pattern` ·
`test_an_unqualified_proven_still_trips_the_narrowed_pattern` ·
`test_the_transcript_file_is_not_a_gate_target` ·
`test_context_research_and_discussion_log_are_not_gate_targets` (⚠ 152 must extend this to
**`152-VALIDATION.md`** too — it exists on disk today) · `test_every_forbidden_pattern_has_a_planted_fixture`

**Plus three new legs** proving the modified `issue-closed` row still fires: `gh#21 … closed`,
`gh#11 … resolved`, `gh#12 … fixed` (RESEARCH §C-5's explicit requirement).

**Arming note (149's own deviation, `:20-25`, applies here too):** the arming leg is only observable
GREEN once its named artifact exists. 149 pointed it at the one artifact plan 01 had already written.
152's gate-building plan should do the same — point it at the minimal existing set, not at a file three
plans away.

---

### 3. `fixtures/` (test fixtures, markdown) — **COPY 2, AUTHOR 3**

**Donor:** `.planning/phases/149-*/fixtures/` — 11 files: 2 clean controls
(`clean_control.md`, `clean_control_second.md`) + 9 planted, one per added/modified label.

**Copy-and-adapt the two controls; author one new plant per 152-added/modified label** —
`planted_sdp_relock_as_shipped.md`, `planted_bare_sdp_relock_flag.md`,
`planted_issue_closed.md` (re-authored for the narrowed row, i.e. keyed on gh#21/#11/#12, not #32).

**The exact fixture shape — a two-line HTML header, then the required caveat, then ONE plant.** Donor
`fixtures/planted_at28c256_fixed.md`, verbatim:

```markdown
<!-- test fixture for 149-check-claims.py -- NOT a phase artifact -- never add to _DEFAULT_TARGETS -->
<!-- planted violation: trips the at28c256-fixed forbidden label; the required caveat IS present, so
     this fixture fails for exactly one reason -->

This change is software-proven and unvalidated on silicon.

The planted sentence: AT28C256 write path is finally fixed by this change.
```

**The missing-caveat plant is the mirror image** — zero forbidden phrases, caveat deliberately absent
(`fixtures/planted_missing_caveat.md`, header verbatim):

```markdown
<!-- planted violation: the required software-proven-unvalidated caveat is ABSENT; zero forbidden
     phrases appear, so this fixture fails for exactly one reason -->
```

**The clean control carries the caveat inline in prose**, because a fixture basename is absent from
`_CAVEAT_RULES` and therefore held to the fail-closed FULL set (`fixtures/clean_control.md`, tail):

> *"… three upstream-native rows stay at 64. This change is software-proven and unvalidated on
> silicon. No physical AT28C part has been exercised on a bench during this phase …"*

⚠ **Fixture-authoring hazard, measured by 149 (`test_check_claims_v132.py:52-58`):** *"several
candidate fixture wordings tripped an UNINTENDED second label (writing out a forbidden label's own
name in a fixture's HTML comment, for instance, can itself contain a forbidden substring) and were
rewritten before being committed."* **Run every candidate fixture through the scanner before
committing it**, and record the probe.

⚠ **The 152 plants are the highest-risk fixtures this project has authored**, because
`sdp-relock-as-shipped`'s plant must contain the literal `write --sdp-relock` in a shipped framing —
which is exactly the string the fixture headers must then *not* accidentally exonerate. Probe first.

---

### 4. `152-CLAIM-GATE-TRANSCRIPTS.md` (evidence record, batch)

**Donor:** `.planning/phases/149-*/149-CLAIM-GATE-TRANSCRIPTS.md`, 274 lines.

**The header disclaimer — adapt, keep every clause** (`:3-15`). It is what stops a future reader
"fixing" the file and destroying the evidence:

> *"**This file deliberately contains forbidden vocabulary, quoted verbatim as evidence of what the
> gate rejected. It is NOT a claim about the page-size change, and it is deliberately NOT a gate
> target — it is absent from `149-check-claims.py`'s `_DEFAULT_TARGETS` by design …** A future reader
> must not "fix" this file by rewording the RED blocks below to remove the forbidden phrases — doing
> so would destroy the evidence the transcript exists to preserve. If this file were ever added to
> `_DEFAULT_TARGETS`, every RED block below would make the gate permanently fail against its own
> proof of itself working."*

**The per-block shape — literal command, literal stdout, literal `EXIT=`, then prose explaining the
hit** (`:27-44`):

````markdown
### 1. `proven-unqualified` — the MODIFIED pattern (…), narrowed to `(?<!software-)\bproven\b`

```
$ FIRESTARTER_CLAIMSCAN_TARGETS_149=fixtures/planted_proven_unqualified.md python3 149-check-claims.py ; echo EXIT=$?
FAIL: 3 forbidden phrase match(es):
  fixtures/planted_proven_unqualified.md:2: forbidden phrase match [proven-unqualified]: 'proven'
  …
EXIT=1
```
````

**The GREEN block pastes the whole `PASS:` line including the non-claim tail** (`:112-119`) — do not
truncate it.

**Copy the two closing subsections verbatim in shape** — `## What this transcript does and does not
prove` (`:141-155`) with its **Does prove** / **Does not prove** pair, and the
`## Final target list (… close-out)` section (`:232-274`) that records the last SUMMARY scanned **via
positional argv** because it could not be a `_DEFAULT_TARGETS` member while the extending plan ran.

**Section skeleton for 152** (RESEARCH §C-8 names it; the donor's headings are the model):

```text
## RED — one block per forbidden-pattern label this phase added or modified
### 1. `sdp-relock-as-shipped` — ADDED  (plant = the roadmap's pre-amendment criterion-1 wording)
### 2. bare `--sdp-relock` companion — ADDED
### 3. `issue-closed` — MODIFIED (32 dropped), with the three still-fires controls
## RED — donor-carried rows, for completeness
## GREEN — the real default targets, no argv, no seam
## Paired suite — python3 -m pytest test_check_claims_152.py -q -o addopts=""
## What this transcript does and does not prove
## Extended target list (plan NN)
## Final target list (close-out — the last SUMMARY added via argv)
```

---

### 5. `152-LEDGER.md` (record / honesty ledger, batch)

**Donors:** `.planning/phases/146-*/146-LEDGER.md` (452 L) — the primary; and
`.planning/phases/137-*/137-LEDGER.md` for the shorter claim-class shape.

**Heading skeleton, from 146-LEDGER.md:**

`# v1.32 Honesty Ledger — <milestone name>` → `## Status / claim key` (`:90`) →
`## The ceiling, then the …` (`:103`) → `## Evidence tiers — weakest to strongest` (`:202`) →
`## The four-column claim table` (`:254`) → `## Mechanism corrections` (`:289`) →
`## Negative space — all N carry-forwards` (`:317`) →
`## Process failures recorded here, not only technical ones` (`:381`) →
`## What no test, gate or review can close` (`:424`).

**The live-HEAD-capture discipline — the pattern to copy exactly** (`146-LEDGER.md:12-19`):

> **Firmware submodule (`firestarter`) HEAD:** `f8ac6439…` (`f8ac643`) — captured live via
> `git -C /workspaces/firestarter rev-parse HEAD` at this plan's own execution (2026-08-17),
> **measured here, never reused from a prior document's citation.**

Note the donor also *states the divergence* when a sibling artifact captured a different SHA
(*"`146-ARM-BUILD-RECORD.md`'s own capture, `fa6c9c7`, is four commits earlier … both readings are
correct for the moment each was taken"*). 152 will need this: RESEARCH §A-3's HEADs (meta `b23e7dd6`,
fw `d990a4ce`, app `a0bfd5e8`) are 2026-08-21 readings and will move once 152 commits.

**The Oracle block — every gate/suite named with its own count** (`146-LEDGER.md:21-42`, five numbered
items). Copy the shape, including how it reports a **RED-by-construction** leg honestly:

> *"**Its fixture suite**, `test_check_claims_v131.py`: **14 passed, 1 failed**, re-run live this
> plan … The one failure is `test_armed_against_the_five_real_closing_artifacts`, RED by construction
> until `146-11` — its own assertion message says so."*

**The four-column claim table — this is where D-12's per-claim pairing discipline lives**
(`146-LEDGER.md:254-262`). Header, verbatim, and the non-empty-fourth-cell rule:

```markdown
| Class | Permitted wording | Evidence (measured, source) | Explicitly does NOT prove |
|---|---|---|---|
```

> *"Every row's fourth cell is **non-empty** — that cell **is** CLOSE-02's explicit non-claim, and a
> row without one would not satisfy the requirement."*

**The claim key — reuse unchanged** (`146-LEDGER.md:90-100`): `PERMITTED` / `CONTEXT-ONLY` /
`FORBIDDEN`, with *"`FORBIDDEN` … appears in this ledger only as a citation of what is not claimed,
never as prose asserting it."*

**The `Composes with (cross-reference only — no data copied)` block** (`:56-88`) and its closing
porcelain check (*"`git status --porcelain` on each of the ten paths above is confirmed **empty**"*)
are the mechanism for citing sibling records without editing them. Copy it.

---

### 6. `152-GH12-COMMENT.md` (outward comment draft) — **COPY AND ADAPT, COMMIT THE DIFF**

**Donor:** `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md`,
**46 lines, read in full.** D-14 says **adapt**, not author fresh, and **commit the diff against the
137 original so the review sees exactly what changed.** That makes this a copy-then-edit plan task
with a `git diff` artifact, not a write-from-analog task.

**KEEP — the two paragraphs D-14 names, quoted here verbatim so the planner can pin them.**

Paragraph A — the *"two halves don't survive equally"* framing (`137-GH12-COMMENT.md:6-14`):

> `dev sdp <chip> enable|disable` is gone. The two halves don't survive equally, and I'd rather be
> plain about that than let the release notes imply otherwise:
>
> - **`disable`'s behaviour survives, and you no longer need a command for it.** Unlocking is already
>   what `write` does by default on every protocol-`0x0D` part — it auto-unlocks unless you pass
>   `--skip-sdp-unlock`. So `dev sdp disable` was genuinely redundant, not merely dropped.
> - **`enable` is withdrawn, with no replacement in this release.** If you want a part deliberately
>   left protected, there is currently no supported way to do it. The design for one is settled and the
>   work is queued, but it is not in this release and I'm not going to promise a version for it.

Paragraph B — the *"This isn't the 'enable/disable' you asked for"* paragraph (`:16-18`). This is also
the **tonal target for all three comments** (CONTEXT §specifics): name the shortfall before naming the
gain.

> This isn't the "enable/disable" you asked for. You asked for both, and what you get is one of them
> automatically and none of the other. There's a second limitation worth stating: the protection bit on
> these parts can't be read back, so even when a part is protected, nothing can show you that it is.

**ADD (D-14):** the **second** withdrawal spanning two releases; Backlog **999.28** by name;
`lock-status`; Phase 153.

**OMIT (D-14):** any process-failure narration.

**MUST NOT SAY** (criterion 1's negative case): that `enable` returns as `write --sdp-relock`; that
the v1.30 gap was satisfied all along.

**Structural note that reduces gate surface (RESEARCH §C-4, measured):** the donor **never names
`write --sdp-relock`** — it says *"The design for one is settled and the work is queued."* Keep it
that way. Only the two release-note bodies should carry the literal command string, so the fifth
forbidden class never fires on any comment draft.

**Also reusable from the donor, and directly relevant:** its `**This is where I need help…**` section
(`:27-46`) — the `firestarter dev test <chip>` ask, in a fenced block, with the non-destructive-by-default
note. 152's version of this must add the **second half of the install** (`firestarter fw --install`),
per RESEARCH §B-8.

---

### 7. `152-GH21-COMMENT.md` and `152-GH11-COMMENT.md` (outward comment drafts)

**No exact donor.** Three analogs together supply the shape:

1. **Tone and structure:** `137-GH12-COMMENT.md`'s bolded-section rhythm — `**What's changing**` /
   `**What did get better**` / `**This is where I need help…**` — and its paragraph-B discipline
   (shortfall first, gain second).
2. **Correction-register shape, for the "the reason string in your report is now false" move:**
   `.planning/phases/146-*/146-CORRECTIONS.md`'s per-row structure —
   `| Row | Origin finding | Owning file:line | False text (cited, not quoted where it would trip
   D-14) | Corrected text | Owning plan |`. **The D-14 citation discipline is the pattern that
   matters here:** *"this register never reproduces a false statement's exact wording where that
   wording itself carries a forbidden phrase; the false-text column cites `file:line` instead."*
   For gh#21, though, the false string is **the reporter's own paste**, which is safe to quote — see
   RESEARCH §D-3's three citable hooks.
3. **Fact-check and doc-check registers:** `146-CLAIM-FACTCHECK.md` (217 L) and
   `146-DOC-CHECK-RECORD.md` (569 L) — the shapes for recording a claim's oracle before the claim goes
   outward. These are the nearest analogs for a per-comment fact-check appendix if a plan wants one.

**Content oracles are in RESEARCH, not in any donor** — §D-3 (gh#21's report body: `"fw_board_identity":
null`, `"host_version": "3.0.0b15"`, the falsified erase-NA reason string) and §D-4 (gh#11's
2026-08-03 *"I will soon get it pushed and I will keep you posted"* — a **kept promise, 18 days late**,
not a broken silence; CONTEXT's "unanswered" framing must not reach the reply text).

---

### 8. `152-RELEASE-NOTES-app.md` and `152-RELEASE-NOTES-fw.md` (outward release bodies)

**Donors:** `.planning/phases/146-*/146-RELEASE-NOTES-app.md` (92 L) and `-fw.md` (112 L) — both
authored for `b21` and **never posted**; plus
`.planning/phases/137-*/137-RELEASE-NOTES-app.md` for the `dev sdp` Removed mapping.

**The opening version-read paragraph — verbatim-reusable structure** (`146-RELEASE-NOTES-app.md:3`).
Every clause is doing work; keep all of them and swap the measured values:

> **Version:** `3.0.0b21` — read from `gh release list --repo henols/firestarter_app` at
> 2026-08-18T09:58:57Z, never predicted. Cut by `beta-release.yml` from merge commit `91c2add0`
> (PR #51). PyPI upload verified **independently of GitHub**, because this project has had GitHub
> carrying betas through `b17` while PyPI stopped at `b15`: `firestarter-3.0.0b21-py3-none-any.whl`
> and `firestarter-3.0.0b21.tar.gz` are both present on PyPI. Stable is **unchanged** — PyPI
> `info.version` is still `2.0.7`. The matching firmware release is **`3.0.0b19`**; the two
> repositories version independently, so the numbers do not agree and are not expected to.

⚠ Two 152-specific adjustments to that paragraph, measured 2026-08-21: the firmware workflow is
**`beta-build.yml`**, not `beta-release.yml` (RESEARCH §E-2), and PyPI's stable `info.version` is
**still `2.0.7` while GitHub carries a `2.0.8` release** (§A-5) — the paragraph's "stable unchanged"
clause happens to remain literally true, but the notes must not assert `2.0.8` is installable.

**The firmware body's asset line** (`146-RELEASE-NOTES-fw.md:3`) is the model, and it already lists
**four** assets with byte sizes — so the donor is right where CONTEXT's discretion item said "three":

> Assets published: `firestarter_leonardo.hex` (75961 B), `firestarter_uno.hex` (70120 B),
> `firestarter_uno328pb.hex` (70246 B), `firestarter_py32f071.hex` (79047 B). The host app's matching
> release is **`3.0.0b21`** …

**The app body's second paragraph — the channel explanation** (`146-RELEASE-NOTES-app.md:7-11`):
GitHub release page carries no files, PyPI is the distribution channel, the firmware is published
separately and its `.hex` files are what `fw --install` pulls, *"a reader upgrading one half without
the other should know which half does what before doing so."* 152 needs exactly this paragraph,
because RESEARCH §B-8 makes matched firmware a hard precondition for the gh#21 ask.

**The `## Removed` section — donor is `137-RELEASE-NOTES-app.md:10-21`, and it is the correct
`dev sdp` mapping. Quote-adapt it:**

> ## Removed
>
> `firestarter dev sdp <chip> enable|disable` is gone.
>
> - **`disable` is gone because it is genuinely redundant.** `write` already auto-unlocks on every
>   protocol-`0x0D` write by default (declinable via `--skip-sdp-unlock`), so `dev sdp disable` was
>   sending a command sequence `write` already sends on its own.
> - **`enable` is withdrawn, with no replacement in this release.** There is currently no supported
>   way to deliberately protect an SDP part. On this chip family the protection bit cannot be read
>   back afterward either, so even if a replacement existed today there would be no way to confirm
>   the result. The design for a replacement is settled and tracked as **Backlog 999.28** — it is
>   queued, not shipped, and no version is promised for it here.

⚠ **This donor section names Backlog 999.28 and deliberately does NOT name the command string.** For
152 the fifth forbidden class requires the command string to appear **in the mandated withdrawal word
order** (name first, withdrawal predicate immediately after — RESEARCH §C-4). So this is the one place
the donor must be *extended*, not merely copied, and the extension is gate-constrained prose.

**The two-section honesty split — copy both headings and both list shapes:**

- App: `## What is established, and what is not` with **Established:** / **Not established:** bullet
  lists (`146-RELEASE-NOTES-app.md:56-86`).
- Firmware: `## What is established` (`:68`) and `## What this release does not establish` (`:85`) as
  two separate sections, plus `## Before you plug anything in` (`:56`) for hazards and
  `## The capability boundary, and what would help` (`:102`) as the closing ask.

The "does not establish" bullets are the model for 152's D-11 non-claim. Note the donor's own
bolded-lead-then-explain rhythm and that it names *why* something is unestablished, e.g.:

> - **No comparative claim.** This release is not faster or more reliable than what preceded it — no
>   control run was made, and a historical pre-milestone write-time figure recorded elsewhere in this
>   project's history is a recorded number, not a control measurement.

**The closing `## The ask` section** (`146-RELEASE-NOTES-app.md:88-92`) is the model for 152's fresh-run
request, and it already carries the *"either outcome"* framing.

---

### 9. `152-MERGE-RECORD.md` (handoff record) — **NO ANALOG**

No prior phase produced one. The nearest in-repo shapes are `146-CITATIONS.md` (a per-oracle citation
register) and Phase 124's firmware-integration-merge directory. **The content is fully specified by
RESEARCH §E-5's six numbered items plus its one-line instruction** — write from that, using
`146-LEDGER.md`'s live-capture attribution style (command + timestamp + *"measured here, never reused
from a prior document's citation"*) for each captured value.

The load-bearing line, from §E-5 item 6, to be reproduced literally:

> **"the beta merges for v1.32 are COMPLETE; do not re-merge; verify with `git cherry`, never
> `--is-ancestor`."**

⚠ RESEARCH §G-1 recommends `152-LEDGER.md` carry the amendment register rather than a separate
correction register, but says nothing against `152-MERGE-RECORD.md` — it is a different document class
(a handoff instruction, not a claim register). If it is written, decide explicitly whether it joins
`_DEFAULT_TARGETS`; §E-5 says "gate-scanned", which means it also needs a `_CAVEAT_RULES` entry.

---

## Shared Patterns

### Pattern A — The labelled correction block + register entry (the amendment shape)

**Applies to:** every edit in `ROADMAP.md`, `REQUIREMENTS.md`, `PROJECT.md`.

**Gate:** `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/check_record_corrections.py`
(517 L). It scans repo-root-relative defaults — `PROJECT.md`, `STATE.md`, `ROADMAP.md`,
`.planning/milestones/v1.23-REQUIREMENTS.md`, `.planning/notes/py32f071-port-branch-state.md`.
**`REQUIREMENTS.md` is NOT a target.** It is GREEN today at
`{block: 23, line-label: 4, inline-history: 6, inline-allow: 10, superseded: 12}`, rc=0, 23.3 s.

**The five exemption verdicts it recognises, each with the recogniser and a real in-repo example:**

| Verdict | Recogniser (source) | Real in-repo example |
|---|---|---|
| **`block`** | `_LABEL_OPENER_RE = re.compile(r"^\s*(?:[-*]\s+)?\*\*⚠")` (`:283`) — a multi-line block, closed by `_BLOCK_CLOSER_RE` (`:303`) at the next heading, `---`, non-opener bold line, or top-level `-` bullet | `.planning/PROJECT.md:358` — `**⚠ CORRECTION (Phase 146 / CLOSE-04, origin C3 / 141 H3) — the C3 row above …` ; also `:443`, `:461` |
| **`line-label`** | `_LINE_LABEL_RE = re.compile(r"⚠\s*(?:CORRECTION\|RESEARCH CORRECTIONS\|SUPERSEDED\|DESIGN)\b\|^SUPERSEDED\b", re.IGNORECASE)` (`:290-293`) — a label anywhere on the hit line, no block | `.planning/ROADMAP.md:34` — `- ⚠ **Retired: the v1.28 PY32F071 Port …` ; `ROADMAP.md:604`, `:831` are the 146 CLOSE-04 blocks |
| **`inline-history`** | `_INLINE_MARKER_RE = re.compile(r"<!--\s*recordscan:(history\|allow)(.*?)-->")` (`:311`), keyword `history`; **a bare marker with no reason does NOT exempt** (`_marker_has_reason`, `:314-320`) | `.planning/PROJECT.md:32` — `<!-- recordscan:history reason: 2992 B was the pre-Phase-119 Leonardo headroom (28672 - 25680), accurate when this v1.22 archive entry was written … Historically correct, preserved as a record, not corrected. -->` ; also `:671`, `:802` |
| **`inline-allow`** | same regex, keyword `allow` — for a coincidental collocation that is not a stale claim at all | `.planning/ROADMAP.md:33` — `<!-- recordscan:allow py32-buffer-1024: coincidental collocation -- DATA_BUFFER_SIZE/1024 here is the Uno buffer-doubling discussion …, unrelated to the py32 port's own DATA_BUFFER_SIZE=512 … -->` ; also `ROADMAP.md:3581`, `PROJECT.md:723` |
| **`superseded`** ⚠ **DO NOT USE** | `_SUPERSEDE_MARKER_RE = re.compile(r"<!--\s*recordscan:supersedes\s+needle=([a-zA-Z0-9-]+)\s+lines=([0-9,\s]+?)\s+(.*?)-->", re.DOTALL)` (`:329-332`) — requires **both** a known needle label **and** an explicit line-number list; **line-keyed, therefore orphanable** | `.planning/notes/py32f071-port-branch-state.md:172` — `<!-- recordscan:supersedes needle=third-stack-2c2ed10 lines=12 reason: opening paragraph line 12 quotes the ROADMAP's own since-corrected 2c2ed10/603-additions citation … -->` (7 markers in that file; **the only file with live `lines=N` markers, and 152 does not touch it**) |

**Rule for 152 (RESEARCH §G-1 + §A-12):** use `block` / `line-label` / `inline-history` /
`inline-allow` — all position-independent. **Never introduce a `superseded` marker**; there is
currently no live `lines=N` marker in any file 152 edits, and 152 must not create the first one.
Re-run `check_record_corrections.py` after every insertion, with a **300 s** timeout ceiling (measured
23 s, but a short timeout returns rc=124 and reads like a RED).

**The register half:** `146-CORRECTIONS.md`'s row shape (§7 above) — but per RESEARCH §G-1, 152 puts
the register **inside `152-LEDGER.md`**, not in a separate file.

### Pattern B — Read the version, never predict it

**Source:** `146-RELEASE-NOTES-app.md:3` / `146-RELEASE-NOTES-fw.md:3` (quoted in §8).
**Apply to:** both release-note bodies, `152-LEDGER.md`, `152-MERGE-RECORD.md`.
Every version, SHA and count carries the command that read it and the timestamp. Verify PyPI
**independently of GitHub** (`curl -s https://pypi.org/pypi/firestarter/json`), never inferred from
`gh release list`.

### Pattern C — Fail closed, at every layer

**Source:** `149-check-claims.py` (`:308-320`, `:448-467`); the anti-source is
`137-*/check_permitted_claims.py:303-312`.
**Apply to:** the gate script and every test leg. Unknown basename → FULL caveat set. Zero targets →
rc=1. Missing target → rc=1. **No exit-0-on-nothing-scanned branch, ever.**

### Pattern D — Cite forbidden claims by location and finding id; never reproduce them

**Source:** `146-CORRECTIONS.md`'s preamble — *"this register never reproduces a false statement's
exact wording where that wording itself carries a forbidden phrase; the false-text column cites
`file:line` instead."*
**Apply to:** all three comment drafts, `152-LEDGER.md`, the correction blocks. This is also *why*
`152-CLAIM-GATE-TRANSCRIPTS.md` and `fixtures/` must stay out of `_DEFAULT_TARGETS`.

### Pattern E — A gate is not believed until it is SEEN to fail

**Source:** `149-CLAIM-GATE-TRANSCRIPTS.md`'s RED-then-GREEN structure + the meta test leg.
**Apply to:** the gate-building plan and the target-extending plan.
⚠ **A pre-authored gate leg can be structurally UNREACHABLE.** In-repo precedent, `PROJECT.md:723`:
*"`test_linker_comment_cross_references_record` located the MEMORY block by requiring `MEMORY` and
`{` on one source line, but `PY32F071xB_FLASH.ld` has them on lines 8 and 9 — the leg could never
pass, whatever the comment said."* The fix must be **locator-only**, never a change to what the
assertion asserts.

### Pattern F — The `_DEFAULT_TARGETS` ordering trap

**Source:** `149-check-claims.py:130-137` (the comment explaining why `149-08-SUMMARY.md` was
deliberately excluded) + `149-CLAIM-GATE-TRANSCRIPTS.md:232-239`.
**Apply to:** whichever plan extends the target list, and the close-out plan.
Any `_DEFAULT_TARGETS` entry absent from disk makes the gate rc=1. Consequence: one plan builds the
gate armed at a minimal existing set; a **later** plan extends it; the **final** SUMMARY is scanned via
positional argv and that argv run is recorded in the transcript. Every basename added to
`_DEFAULT_TARGETS` must simultaneously gain a `_CAVEAT_RULES` entry, enforced by
`test_every_default_targets_basename_has_a_caveat_rule_entry`.

### Pattern G — Hand-edit the record files

**Apply to:** `ROADMAP.md`, `REQUIREMENTS.md`, `PROJECT.md`.
The `gsd-tools` requirements/roadmap verbs run `_normalizeMd` over the whole file. Hand-edit only.
⚠ Executors are measured to skip `update_requirements` when told "no state writes" — the
`REQUIREMENTS.md` plan must say **explicitly** that the OUT-01…05 checkboxes flip.

### Pattern H — Outward-facing acts are gated per artifact

**Apply to:** every posting plan's frontmatter.
Restate: **this phase must NOT be run under `--auto`/`--chain`**, and `autonomous: false` alone is
**not** self-protecting. Sub-repo plans need `commits_land_in:` — worktrees leave submodules empty and
the gate under-detects.

---

## Copy-and-rename vs write-from-analog

Stated separately because the plan tasks differ.

**Copy-and-rename jobs** (task shape: `cp` the donor, apply an enumerated rename list, then a diff
review):

| File | Donor | Renames |
|---|---|---|
| `152-check-claims.py` | `149-check-claims.py` | 7, enumerated in §1 |
| `test_check_claims_152.py` | `test_check_claims_v132.py` | 7, enumerated in §2, **including the file's own basename** |
| `fixtures/clean_control*.md` | 149's two controls | vocabulary swap only |

**Copy-and-adapt with a committed diff** (task shape: `cp`, edit, `git diff` against the original as
a review artifact):

| File | Donor | Mandate |
|---|---|---|
| `152-GH12-COMMENT.md` | `137-GH12-COMMENT.md` | D-14: keep paragraphs A and B verbatim-in-substance; commit the diff |

**Write-from-analog jobs** (task shape: read the donor for structure, author new content):

`152-CLAIM-GATE-TRANSCRIPTS.md` · `152-LEDGER.md` · `152-GH21-COMMENT.md` · `152-GH11-COMMENT.md` ·
`152-RELEASE-NOTES-app.md` · `152-RELEASE-NOTES-fw.md` · the three record-file amendment sets ·
new `fixtures/planted_*.md`

**Write from RESEARCH, no code analog:** `152-MERGE-RECORD.md` (§E-5).

---

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `152-MERGE-RECORD.md` | handoff record | batch | No prior phase produced a merge/no-re-merge handoff record. Nearest shapes: `146-CITATIONS.md` (citation register), Phase 124's `firmware-integration-merge` dir. Content is fully specified by RESEARCH §E-5. |
| `152-GH21-COMMENT.md`, `152-GH11-COMMENT.md` | outward comment drafts | publication | No prior phase drafted a comment for either thread. Tone donor is `137-GH12-COMMENT.md:16-18`; register shapes are `146-CORRECTIONS.md` / `146-CLAIM-FACTCHECK.md`; **content** comes from RESEARCH §D-3 and §D-4, not from any donor. |

---

## Metadata

**Analog search scope:** `.planning/phases/{130,137,146,149,153}-*/`, `.planning/{ROADMAP,REQUIREMENTS,PROJECT}.md`,
`.planning/notes/`, `.planning/phases/152-outward-facing-close-operator-gated/`
**Files read in full:** `149-check-claims.py` (531 L), `137-GH12-COMMENT.md` (46 L), four 149 fixtures
**Files read in targeted, non-overlapping ranges:** `152-CONTEXT.md`, `152-RESEARCH.md`,
`test_check_claims_v132.py`, `149-CLAIM-GATE-TRANSCRIPTS.md`, `146-LEDGER.md`, `146-CORRECTIONS.md`,
`146-RELEASE-NOTES-{app,fw}.md`, `137-RELEASE-NOTES-app.md`, `check_permitted_claims.py`,
`check_record_corrections.py`, `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`
**Pattern extraction date:** 2026-08-21
**Read-only:** no source file was modified; `152-PATTERNS.md` is the only file written.
