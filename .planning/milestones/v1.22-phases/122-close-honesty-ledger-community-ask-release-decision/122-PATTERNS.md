# Phase 122: CLOSE — honesty ledger, community ask, release decision - Pattern Map

**Mapped:** 2026-07-30
**Files analyzed:** 13 (10 new/modified planning artifacts + 1 new gate script trio + 2 merge-resolved sub-repo files)
**Analogs found:** 11 / 13 (2 have no analog — see §No Analog Found)

> **Shape warning honoured.** This is a CLOSE phase: nine of the thirteen deliverables are prose.
> Their analogs are **prior phase artifacts**, not code. The one genuinely-code deliverable (the
> permitted-claim scanner) has three strong code analogs and a mandatory anti-hollow test pairing.
> **No product source is modified by this phase** — the only sub-repo file changes are a merge
> resolution that must produce a **zero diff** against branch HEAD (RESEARCH C-11/C-12).

---

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|------|-----------|----------------|---------------|
| `.planning/phases/122-…/122-LEDGER.md` (**new**) | meta | evidence-record doc | transform (evidence → claim classes) | `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` (structure only; **verify, never edit**) + `.planning/phases/121-…/121-NONREGRESSION.md` §1 | role-match |
| `.planning/PROJECT.md` (EIGHTH CORRECTION) | meta | project evidence record | append-only doc edit | the **SEVENTH CORRECTION** block, `PROJECT.md:101-111` | exact |
| `.planning/phases/122-…/122-RELEASE-NOTES-fw.md` (**new**) | meta | outward-facing prose | file-I/O → `gh release edit --notes-file` | `.planning/phases/116-…/116-PREMISE.md` §2 (ceiling-compliant claim prose) | partial |
| `.planning/phases/122-…/122-RELEASE-NOTES-app.md` (**new**) | meta | outward-facing prose | file-I/O → `gh release edit --notes-file` | same as above | partial |
| `.planning/phases/122-…/122-GH11-COMMENT.md` (**new**) | meta | outward-facing prose | file-I/O → `gh issue comment --body-file` | **none committed in-tree** — nearest is `116-PREMISE.md` + shipped `dev sdp --help` text | no analog |
| `.planning/phases/122-…/122-GH12-COMMENT.md` (**new**) | meta | outward-facing prose | file-I/O → `gh issue comment --body-file` | same | no analog |
| `.planning/phases/122-…/122-DECISION.md` (**new**, CLOSE-03) | meta | decision record | append-only doc | `116-PREMISE.md` frontmatter + `119-NONREGRESSION.md` §5 statement style | role-match |
| `.planning/phases/122-…/122-CHANNELS.md` (**new**, D-03 evidence) | meta | verification transcript | request-response (PyPI/GH API → transcript) | `.planning/phases/115-…/115-VALIDATION.md` + `115-03/04-SUMMARY.md` channel steps | role-match |
| `.planning/phases/122-…/122-NONREGRESSION.md` (**new**) | meta | gate-result artifact | batch (11 commands → table) | `121-NONREGRESSION.md` (which itself inherits `119-NONREGRESSION.md` §CORRECTION-4) | exact |
| `.planning/phases/122-…/check_permitted_claims.py` (**new**) | meta | gate script | file-I/O + exit-code contract | `firestarter_app/tools/check_no_community_support_status_write.py` | role-match |
| `…/tests/test_check_permitted_claims.py` + planted fixture (**new**) | meta | test + fixture | file-I/O | `firestarter_app/tests/test_check_no_community_support_status_write.py` + `tests/fixtures/planted_log_in_window.cpp` | role-match |
| `firestarter_app/firestarter/submit.py` | **firestarter_app** | (merge resolution only) | — | itself at branch HEAD — resolution must be a **no-op diff** | exact |
| `firestarter_app/tests/test_submit.py` | **firestarter_app** | (merge resolution only) | — | itself at branch HEAD — same | exact |

**Auto-merged, no resolution, no pattern needed:** `firestarter/include/version.h` (b11→b13, firmware
repo, **zero conflicts** per C-1) and `firestarter_app/firestarter/__init__.py` (b11→b13, C-2).
A plan that lists `version.h` as a conflict cannot execute.

**Also touched (routine GSD bookkeeping, no analog needed):** `.planning/REQUIREMENTS.md`
(CLOSE-01/02/03 checkboxes + 3 `Pending` traceability rows), `.planning/STATE.md`,
`122-NN-PLAN.md` / `122-NN-SUMMARY.md`.

---

## Pattern Assignments

### `122-LEDGER.md` (evidence-record doc, transform)

**Primary analog:** `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` — **structure only. D-09 makes this
file read-only for this phase.** Copy its *shape*: a pinned-provenance header block, one wide table,
then a **status key** legend, then an open-defects/negative-space section.

**Header-provenance pattern** (`PROTOCOL-LEDGER.md:1-14`) — note the explicit "caveat" line and the
compose-by-cross-reference clause; both are exactly what D-11/D-12 need:

```markdown
# v1.16 Protocol Ledger — Per-Protocol Bench Validation + Documentation

**Milestone:** v1.16 — Protocol-First Architecture Rebuild
**Firmware under test:** submodule commit `a296195` (Phase 89 HEAD, incl. CR-01 fix)
**Version string caveat:** firmware reports `3.0.0b10`; the actual build is the v1.16 recompose —
  record the submodule commit, not the version string
**Oracle:** leonardo + RURP Rev 2.0
**Generated:** 2026-06-26

**Composes with (cross-reference only — no data copied):**
- `firestarter_app/tools/validation_matrix_spec.json` — join key: `matrix_family`

**D-04 compose-by-cross-reference:** this ledger holds join keys only; SHA-256 digests and verdict
data remain authoritative in the upstream files above.
```

⚠ For 122 the header must pin **two** commits (firmware `48c36e5`+merge, host `c3c9424`+merge) and
the **published tag** — not a version string, per the caveat pattern above. RESEARCH A3: read the
*observed* cut tag, never assume `b14`.

**Row-with-explicit-status pattern** (`PROTOCOL-LEDGER.md:26-27`) — the `0x0D` row is both the model
and the subject of CLOSE-01's verify-don't-edit check:

```markdown
| Bucket | Proposed Name | Handler (File) | Matrix Family | … | Verification Status | Evidence Refs |
| `0x0D` | EEPROM-POLL | `configure_eeprom28c()` (`eeprom_28c.cpp`) | `eeprom28c` [proto 13] | … | **UNVERIFIED** | No on-hand silicon. Rep chip: AT28C256 (`datasheets/0x0D-EEPROM-POLL/AT28C256.pdf`) |
```

**Status-key legend pattern** (`PROTOCOL-LEDGER.md:31-36`) — 122's analogue is a
permitted-vs-non-claim key:

```markdown
**Verification status key:**
- `UNVERIFIED` — no on-hand silicon; full row with datasheet-representative chip; bench-proven when silicon acquired
- `open-defect-carried` — on-hand chip exists but under an open defect; carried verbatim from STATE.md (no status change)
- `PASS` — bench-proven: oracle=leonardo+Rev2.0, SHA regression matches v1.15 baseline
```

**Secondary analog — the "precise statements" section:** `121-NONREGRESSION.md:19-48`. This is the
project's established way of writing a claim so it is *individually checkable*, and it is the closest
thing in-tree to D-11's permitted-wording/non-claim pairing:

```markdown
## 1. The claim, as precise statements

Each statement below is individually checkable against the artifacts named in §2-§4, not merely
asserted:

1. **An unmapped `dev test` op string cannot reach a chip-mutating operator method.** … —
   verified structurally present in `_DESTRUCTIVE_OPS`/dispatch and by the still-green
   `test_chip_test.py` suite (§4, row-adjacent host pytest count).
2. **UV-ness is decided once, from the exact `electrical-type` axis, and only read downstream.**
   `chip_test.is_uv_eprom(full)` measures **301/301** against the live 746-entry DB (re-derived
   live this session, §"Requirement Row Re-Verification")…
```

**Normative claim wording to copy verbatim in substance** — `.planning/REQUIREMENTS.md:148-152`:

```markdown
**Permitted claim at close:** *"The SDP lock and unlock sequences are emitted exactly as specified,
verified byte-exact by golden register trace across all four `0x0D` pinouts, with a documented and
measured host-side timing assumption."*

**Forbidden claim:** *"SDP lock/unlock works on an AT28C256."*
```

⚠ RESEARCH's ALLOW/REFUSE table (43/41; `DIP24_2816` 0/19) is the row that keeps "all four pinouts"
from reading as broader capability than shipped. Emission-traced ≠ operation-permitted.

---

### `.planning/PROJECT.md` — EIGHTH CORRECTION (project evidence record, append-only)

**Analog:** the **SEVENTH CORRECTION**, `PROJECT.md:101-111`. Match this format exactly — bold `⚠`
opener with ordinal + phase + date + a one-sentence thesis, then a numbered item list where each item
opens with a bold claim sentence:

```markdown
**⚠ SEVENTH CORRECTION — Phase 120 close (2026-07-29): the host surface lands, the SDP-capability
partition is re-derived from ground truth, and the operator's `dev test` redesign is folded into
Phase 121 as a recorded reversal.** Phase 120 (host-only, 12 plans) closed HOST-01 through HOST-06
and produced the following corrections and findings:

1. **The `dev test` redesign is folded into Phase 121, and it is a REVERSAL (D-20).** …
2. **"Non-destructive means a partial write" is a contract change, not a flag change.** …
```

Ordinal sequence in the live file: `SECOND REFRAMING` (`:59`), `THIRD` (`:67`), `FOURTH` (`:73`),
`FIFTH` (`:81`), `SIXTH` (`:91`), `SEVENTH` (`:101`) — six ⚠ blocks (C-10), so **EIGHTH is correct**.
Append immediately after `:111`, before the bullet list that follows.

**Precedent for finding-inside-a-correction** (`PROJECT.md:85`, FIFTH item 3) — the shape D-10's
asymmetric silicon datapoint should take, including the "this corrects the decision's premise, not
the code" move:

```markdown
3. **⚠ FINDING F-118-01 — the measured headroom is 4.7 %, not "never".** The Leonardo emits the
   six-write sequence in **572 µs against a 600 µs budget** … CONTEXT.md D-09 framed the runtime
   check as a latent invariant that *"should never fire"*; the measurement says it *barely* does
   not fire. … this corrects the **decision's premise**, not the code.
```

---

### `122-RELEASE-NOTES-fw.md` / `122-RELEASE-NOTES-app.md` (outward-facing prose, file-I/O)

**Analog for ceiling-compliant claim prose:** `116-PREMISE.md:20-36` — a finding stated as
*"Yes/No" + mechanism traced end to end + how to re-run it*, with a frontmatter provenance block:

```markdown
---
title: TRACE-06 premise — does `firestarter write at28c256` abort at INIT on 3.0.0b11?
date: 2026-07-27
context: >
  Written by Phase 116 Plan 07 (D-14) to settle the milestone's highest-value
  PREDICTED claim one phase early, and to correct the "all 84" framing error
  before six downstream researchers (Phases 117-122) inherit it.
---

## 2. The finding, at the software layer

**Yes.** `eeprom28c_write_init` returns `RESPONSE_CODE_ERROR` before any data byte is
transferred, for all four `0x0D` pinouts.
```

**Shipped, reviewed, drift-proof wording to reuse** (`dev sdp --help`, quoted at RESEARCH:704-711):

```
On this chip family the resulting protection state cannot be read back afterward
(Phase 117 D-05, Phase 119 D-12), so neither direction can be confirmed -- a successful run
means only that the command sequence was **emitted**, nothing more.
```

**Delivery pattern** (C-6: CI writes an **empty** body, so this is an *add*, not an overwrite; C-7:
only the **firmware** release carries the three `.hex` assets):

```bash
gh release edit 3.0.0b14 --repo henols/firestarter     --notes-file .planning/phases/122-…/122-RELEASE-NOTES-fw.md
gh release edit 3.0.0b14 --repo henols/firestarter_app --notes-file .planning/phases/122-…/122-RELEASE-NOTES-app.md
```

---

### `122-GH11-COMMENT.md` / `122-GH12-COMMENT.md` (outward-facing prose, file-I/O)

**No committed outward-facing draft exists anywhere in `.planning/`** (searched: no `*DRAFT*`,
`*COMMENT*`, `*REPLY*` artifact). Prose patterns come from `116-PREMISE.md` (above) and the shipped
help text; the **delivery + gating** patterns are concrete and reusable:

**Blocking-operator-wording-review pattern** — copy `116-07-PLAN.md:235-253` verbatim in shape:

```xml
<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 3: BLOCKING operator review of the premise wording (TRACE-06 / D-14, the phase's one manual-only verification)</name>
  <read_first>
    - .planning/phases/116-ground-truth-trace-harness/116-PREMISE.md (written in Task 2)
    - .planning/REQUIREMENTS.md §"Validation Ceiling"
  </read_first>
  <action>
Present both documents to the operator and BLOCK until they explicitly approve the wording or name
the sentences that must change. … Capture the operator's verdict verbatim in the plan summary. If
the operator names corrections, apply exactly those corrections … — no silent auto-approval, and no
rewording beyond what was asked for.
  </action>
  <verify>
    <human-check>Operator has typed "approved", or has named the sentences to change and confirmed the reworded versions.</human-check>
  </verify>
  <done>The operator has explicitly approved the wording …, and the verdict is recorded in the plan summary.</done>
</task>
```

**`gh` argv pattern** — `firestarter_app/firestarter/submit.py:236-278` is the in-tree,
permission-independent idiom (list argv, never a shell string; explicit `--repo`; `--body-file`;
`check=False` with an explicit returncode branch; failure narrated, never silent):

```python
    proc = run_fn(
        ["gh", "issue", "create", "--repo", SUBMIT_REPO, "--title", title, "--body-file", "-"],
        input=body, text=True, capture_output=True, check=False,
    )
    if proc.returncode == 0:
        return proc.stdout.strip()
    err = (getattr(proc, "stderr", "") or "").strip()
    if err:
        _print(f"gh issue create failed: {err}", console=console)
```

Its docstring states the constraint this phase inherits: *"The create argv carries only the repo,
title, and stdin body — nothing that requires triage/write access … permission-independent by
construction."* **Never add `--label` / `--add-label` / `-l`:** both abort on a missing label, and
neither issue carries any label.

For 122 the delivery is `--body-file <committed path>` (not `-`), which is what makes
posted == reviewed:

```bash
gh issue comment 11 --repo henols/firestarter_prom --body-file .planning/phases/122-…/122-GH11-COMMENT.md
gh issue comment 12 --repo henols/firestarter_prom --body-file .planning/phases/122-…/122-GH12-COMMENT.md
# Both issues STAY OPEN (D-13).
```

⚠ **C-5 blocks D-14's `No-Hazmats` sentence as written.** "AT28C parts should now work" is measured
false (19/19 `DIP24_2816` REFUSED). Rewrite before the review gate.

---

### `122-CHANNELS.md` (verification transcript, request-response)

**Analog:** `115-VALIDATION.md` (artifact shape) + `115-04-PLAN.md:12-21` (the acceptance-criteria
phrasing for a channel), which pins the two-step GH-then-PyPI mechanism:

```yaml
    - "PyPI exposes 3.0.0b11 to pip install --pre (pip index versions firestarter --pre shows 3.0.0b11 as the highest prerelease)"
    - "The published PyPI version is a beta (3.0.0b11), not a stable (3.0.1)"
      via: "beta-release.yml bumps + creates the GH release; publish.yml builds + uploads to PyPI (manual dispatch)"
```

`115-03-SUMMARY.md:83` also carries the post-cut divergence warning this phase must repeat: *"the CI
git-auto-commit added a version-bump commit to the remote branch, so local … is now 1 commit behind;
fetch/pull that commit before …"* — Pitfall 3.

Verification commands: RESEARCH §"Channel verification (D-03)". **Never** via the local editable
install.

---

### `122-NONREGRESSION.md` (gate-result artifact, batch)

**Analog:** `121-NONREGRESSION.md` — exact match, same inherited discipline. Copy its header block
(base + HEAD commits for all three repos) and its re-execution pledge, `121-NONREGRESSION.md:3-14`:

```markdown
**Written:** 2026-07-29 (Plan 121-14)
**Firmware phase base:** `0048b3d` … · **Host phase base:** `96e0622` …
**Firmware HEAD at this sweep:** `48c36e5…` · **Host HEAD at this sweep:** `c3c9424…`

… every row below was **re-executed in this session** — nothing here is copied from a prior plan's
SUMMARY. Where a prior plan's SUMMARY made a claim this document re-checks it against the live tree
and says so.
```

Row set = the eleven commands in RESEARCH §"GATE-03's Nine-Row Non-Regression Set". Must be run
**after** the inbound merge (rows 9a/9b scan `submit.py`, one of the two conflicted files).

---

### `check_permitted_claims.py` + paired test + planted fixture (gate script, file-I/O)

**Primary analog:** `firestarter_app/tools/check_no_community_support_status_write.py`. Copy four
things concretely.

**1. Exit-code contract stated in the module docstring** (`:54-59`):

```python
"""
Exit codes:
  0 -- both scan targets exist and contain zero `support_status` writes
       (PASS: line printed, naming both scanned files).
  1 -- a scan target is missing from disk (fail-closed), OR a target
       resolves into the firmware sub-repo (host-only violation), OR at
       least one `support_status` write was found (FAIL: summary printed).
"""
```

`tools/diff_db.py:12-20` shows the three-code variant when an infra error must be distinguishable:

```python
Exit codes:
  0 — all changed chips explained by a cited root-cause rule; …
  1 — at least one chip has an unexplained diff … (D-03 BLOCK)
  2 — infrastructure error: a required input file could not be loaded or parsed …
      Distinct from 1 so a CI consumer does not confuse a missing input with a real diff BLOCK (WR-04).
```

**2. Env-overridable path constants — the injection seam the test needs** (`:66-91`):

```python
_HERE = os.path.dirname(__file__)
_DEFAULT_DISP01_REPORT = os.path.join(_HERE, "..", "firestarter", "diagnostic_report.py")

# Env-override seam (mirrors check_devtest_orchestrator.py's FIRESTARTER_DEVTEST_SRC):
# lets the paired pytest point this checker at a deliberately-violating fixture
# file without editing the real, clean source (D-05).
FIRESTARTER_DISP01_REPORT = os.environ.get("FIRESTARTER_DISP01_REPORT", _DEFAULT_DISP01_REPORT)
```

For 122 the seam is an override of the artifact-path list (e.g. `FIRESTARTER_CLAIMSCAN_TARGETS`).

**3. Fail-closed on a missing target + never-vacuous, and a PASS line that names every scanned
file** (`:210-257`):

```python
    targets = [FIRESTARTER_DISP01_REPORT, FIRESTARTER_DISP01_PARSER]

    missing_targets = [t for t in targets if not os.path.isfile(t)]
    if missing_targets:
        print("FAIL: scan target(s) not found on disk -- the gate cannot "
              f"vacuously pass with a target silently skipped: {missing_targets}")
        sys.exit(1)
    …
    if not scanned:
        # Defense in depth: … a scanned-empty state must never vacuously pass
        # regardless of how it was reached (D-05 anti-hollow contract).
        sys.exit(1)
    …
    print(f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
          "0 support_status writes (sole write locus stays tools/build_db.py)")
```

**4. Bucketed FAIL summary, capped at 20** (`:191-196`):

```python
def _print_bucket(label: str, violations: list[str]) -> None:
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")
```

**Paired-test pattern (GATE-01 anti-hollow — MANDATORY):**
`firestarter_app/tests/test_check_no_community_support_status_write.py`. Its docstring states the
contract, and its runner invokes the checker as a **subprocess** so the exit code is the assertion:

```python
"""
This is the mandatory anti-hollow pairing for the DISP-01 gate (D-05) … a checker tool with no
negative-fixture test is exactly the v1.12 hollow-GATE-03 failure mode … Every planted-violation
test below injects a REAL subprocess-level `support_status` write via the env-overrides -- never an
in-process synthetic -- so a passing test suite proves the checker itself (not the test) fails the
build on a real violation.

Coverage:
  1. Clean-pass baseline …
  2. Planted violation via <ENV> flips the checker to a non-zero exit with a FAIL: summary
  4. Fail-closed on a missing/nonexistent scan target …
  5. Env-override seam sanity: a CLEAN fixture injected via <ENV> still passes -- isolates test 2's
     failure as genuinely caused by the planted violation, not the injection seam.
  7. PASS-line-names-both-scanned-files (anti-skip) …
"""

_FA_DIR = Path(__file__).parent.parent

def _run_checker(env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_overrides or {})}
    return subprocess.run(
        [sys.executable, "tools/check_no_community_support_status_write.py"],
        cwd=str(_FA_DIR), capture_output=True, text=True, env=env,
    )

def test_checker_exits_zero_on_clean_source() -> None:
    result = _run_checker()
    assert result.returncode == 0, (…)
    assert "PASS:" in result.stdout, (…)
```

**Committed-planted-fixture precedent:** `firestarter_app/tests/fixtures/planted_log_in_window.cpp`
(referenced by `tools/check_no_log_in_sdp_window.py`'s docstring) — the violating fixture is a
committed file, not generated at test time.

**Minimal-meta-script precedent (if the scanner stays tiny and phase-local):**
`.planning/phases/120-…/check_note_append_only.py` — a 33-line meta-repo phase-directory script,
module-top path constant, plain asserts, `print("OK: …")` + `sys.exit(0)`:

```python
#!/usr/bin/env python3
"""Assert that the … note was edited append-only … Used by Phase 120 plan 04, Task 3."""
NOTE = ".planning/notes/infoic-xml-protection-flags-research.md"
committed = subprocess.run(["git", "show", f"HEAD:{NOTE}"], capture_output=True, text=True, check=True).stdout
assert working.startswith(committed), (
    "Working-tree file is NOT a prefix of the committed (HEAD) file — … Append-only violation.")
print("OK: append-only edit confirmed")
sys.exit(0)
```

⚠ **That analog has no paired test.** GATE-01 requires one here, so take the *shape* from
`check_note_append_only.py` and the *anti-hollow discipline* from
`check_no_community_support_status_write.py` + its test. A phase-local script with a planted fixture
and one test asserting exit 1 satisfies both.

---

### `firestarter_app/firestarter/submit.py` + `tests/test_submit.py` (merge resolution)

**The "pattern to copy" is literally branch HEAD's own content.** Resolution is whole-file
`--ours`; the proof is an empty diff. No hand-merge, no hunk selection.

```bash
cd /workspaces/firestarter_app
git merge --no-ff origin/beta                                          # conflicts in exactly 2 files
git checkout --ours -- firestarter/submit.py tests/test_submit.py
git add firestarter/submit.py tests/test_submit.py
git diff --cached HEAD -- firestarter/submit.py tests/test_submit.py   # MUST be empty
git commit                                                             # __init__.py auto-merged to 3.0.0b13
```

**Why hunk-level resolution is forbidden (C-12):** hunks 3 (L644-666) and 4 (L676-707) sandwich a
shared region (L667-675, a `submit_via_browser(...)` call) that HEAD needs **twice** — once on the
comment-degrade path, once on the new-issue gh-degrade path. A textual "ours" on both hunks leaves
one call site and a dangling `elif url:` bound to the wrong `if`. **It compiles and the suite may
still pass.**

**Warning signs:** a merged `submit_report` tail containing exactly one `submit_via_browser(` call,
or a resolved `submit.py` shorter than HEAD's 688 lines.

**Superset proof to commit as the justification** (C-11) — `comm -23` empty means all 60 of `beta`'s
test functions exist among HEAD's 77:

```bash
comm -23 <(git show origin/beta:tests/test_submit.py | grep -o '^\s*def test_[a-z0-9_]*' | sed 's/^ *def //' | sort) \
         <(git show HEAD:tests/test_submit.py       | grep -o '^\s*def test_[a-z0-9_]*' | sed 's/^ *def //' | sort)
```

**Negative-argv assertion idiom to preserve** (`tests/test_submit.py:310-325`) — the one honest
assertion a mocked `run_fn` can make, and the pattern any new `gh` call in this phase should follow:

```python
def test_submit_via_gh_argv_carries_nothing_permission_gated():
    # D-1/T-ahy-05: the ONE assertion a mocked run_fn can honestly make about the real-world
    # failure -- no permission-gated argument is ever sent on the create path.
    run_fn = Mock(return_value=Mock(returncode=0, stdout="https://…/issues/1\n"))
    submit.submit_via_gh("My Title", "My Body", run_fn=run_fn)
    argv = run_fn.call_args[0][0]
    assert isinstance(argv, list)
```

---

## Shared Patterns

### Verify-don't-edit a closed milestone's artifact
**Source:** `.planning/v1.16/ledger/PROTOCOL-LEDGER.md:27` (read), D-09.
**Apply to:** every CLOSE-01 task.
```bash
grep -c '^| `0x0D` .*\*\*UNVERIFIED\*\*' /workspaces/.planning/v1.16/ledger/PROTOCOL-LEDGER.md   # → 1
```
Never `check_ledger.py` — pre-existing RED from v1.19's `flash3`/`flash4` rename (C-4).

### Exit-code-contract gate scripts
**Source:** `firestarter_app/tools/check_no_community_support_status_write.py`, `tools/diff_db.py`.
**Apply to:** the new claim scanner and every verification task.
Contract: 0 = PASS with a line naming every scanned file; 1 = violation **or** missing target
(fail-closed); optional 2 = infra error. `diff_db.py` interprets its own result — **use the exit
code**, do not read the "2 changed chips" number as a failure (C-13).

### Anti-hollow gate pairing (GATE-01)
**Source:** `tests/test_check_no_community_support_status_write.py` + committed
`tests/fixtures/planted_log_in_window.cpp`.
**Apply to:** the claim scanner, mandatorily. Subprocess invocation, env-override injection seam,
one clean-fixture control leg proving the seam itself is innocent, one fail-closed leg.

### Blocking operator review before outward-facing text
**Source:** `116-07-PLAN.md:235-253`.
**Apply to:** both comment drafts (D-16) and, by extension, both release bodies.
Delivery re-reads the **committed** file (`--body-file`), which is what proves posted == reviewed.

### `gh` argv discipline
**Source:** `firestarter_app/firestarter/submit.py:236-278`.
**Apply to:** every `gh` call in this phase. List argv, explicit `--repo`, `--body-file`,
`check=False` + explicit branch, narrate failures. **Never** `--label` / `--add-label`.

### Cleanliness proof
**Source:** `PROJECT.md:111` (SEVENTH CORRECTION item 9).
**Apply to:** every "unchanged" assertion.
> *"a path-scoped `git diff` can pass vacuously, so the proof used is
> `git -C /workspaces/firestarter status --porcelain` being empty, which subsumes every path."*

### Measured-not-predicted figures
**Source:** `PROJECT.md:85` (F-118-01), `119-MEASUREMENT.md:33-34,420-453`, `119-09-PLAN.md:161-162`.
**Apply to:** every ledger row and every outward-facing sentence. Cite 572/568 µs (do not average),
84/88 µs page-load, 2600 B free, 66 of 84 (**never "all 84"**), 43 ALLOW / 41 REFUSE, 301/301 UV.
Keep the **flash** budget (LOCK-06) and the **timing** budget (F-118-01) in separate rows.

### `- **D-NN: text**` bullet formatting
Close the bold run on **one** line, at most one colon before the closing `**`, never open with a
glyph — plan-phase's §13a decision-coverage gate fails closed otherwise.

---

## No Analog Found

| File | Repo | Role | Data Flow | Reason |
|------|------|------|-----------|--------|
| `122-GH11-COMMENT.md` | meta | outward-facing prose | file-I/O → `gh issue comment` | **No committed public-communication draft has ever existed in `.planning/`** (searched for `*DRAFT*`/`*COMMENT*`/`*REPLY*`: only `09-03-host-comment-refresh-PLAN.md`, an unrelated code-comment plan). Use `116-PREMISE.md`'s claim prose + the shipped `dev sdp --help` wording (RESEARCH:704-726) as the substance source, and the `--body-file` + blocking-review patterns above as the mechanism. |
| `122-GH12-COMMENT.md` | meta | outward-facing prose | file-I/O → `gh issue comment` | Same. Additionally has **no** analog for its own hardest content: C-5's corrected `No-Hazmats` refusal answer is new prose with no precedent. |

---

## Metadata

**Analog search scope:** `.planning/v1.16/ledger/`, `.planning/phases/{115,116,118,119,120,121}-*/`,
`.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `firestarter_app/tools/`,
`firestarter_app/tests/`, `firestarter_app/firestarter/submit.py`.
**Files scanned:** ~24 (5 read in full or in targeted ranges; the rest listed/grepped).
**Pattern extraction date:** 2026-07-30

**Do-not list honoured:** no edit proposed to `PROTOCOL-LEDGER.{md,json}` (D-09), to
`firestarter/include/messages.h` (codegen-generated, ID-only), or to `check_ledger.py` (C-4).
