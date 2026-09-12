# Phase 188: The Tools Directory - Pattern Map

**Mapped:** 2026-09-12
**Files analyzed:** 7 created/substantively-edited populations (the ~46 deleted paths are deliberately **not** mapped — a deletion needs no analog)
**Analogs found:** 7 / 7

> **Scope note.** This phase removes ~16,500 lines. Deletion needs no pattern. Everything below is for the
> small set of files an executor must **write** or **edit in place**. All analog paths below were confirmed
> git-TRACKED with `git ls-files` in their owning repo (meta, `firestarter_app`, `firestarter`).

## File Classification

| New/Modified File | Repo | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|---|
| `.claude/skills/devtest-rootcause/scripts/diff_db.py` (created — relocated copy) | meta | utility / skill-owned script | file-I/O, batch | `.claude/skills/devtest-rootcause/scripts/infoic_lookup.py` (+ `seed_debug_session.py:86-93`) | exact |
| `firestarter_app/tests/<dispatch model>.py` (created — new test-tier helper) | app | test helper module (library, not a test) | transform / pure function | `firestarter_app/tests/fw_presence.py`, `firestarter_app/tests/plan_corpus.py` | exact |
| `.planning/notes/host-tools-retirement.md` (created) | meta | record / verdict note | document | `.planning/notes/catalog-sync-check-retirement.md`; `.planning/notes/dispatch-invariant-retirement-verdict.md` | exact |
| `firestarter_app/.github/workflows/ci.yml` (edited — 3 step deletions) | app | config / CI | event-driven | its own surviving `Catalog validity check` / `Codegen drift gate (messages.py)` pair | exact (self) |
| `firestarter/.github/workflows/build.yml`, `beta-build.yml` (edited — 4 step deletions) | fw | config / CI | event-driven | same pair in the same files | exact (self) |
| `firestarter/scripts/baseline/size_baseline.json` + 2 `captured_test_native*_summary.log` fixtures (re-record) | fw | config + test fixture | batch capture → transcription | `.planning/phases/185-records-and-checks-that-are-current/185-01-PLAN.md` Task 1 | exact |
| The six `firestarter_app/tools/` survivors (edited — D-16 citation strip) | app | utility | — (source hygiene) | commits `0f53959` (`tools/check_devtest_orchestrator.py`) and `bffbba8` (`tests/test_numeric_schema_source_scan.py`) | exact |
| `.planning/REQUIREMENTS.md` + `.planning/ROADMAP.md` (edited — D-22 ledger amendment) | meta | record | — | `ROADMAP.md:510` (Phase 187 criterion 4), `ROADMAP.md:457` (185-06 line), `REQUIREMENTS.md` FLOOR-01…03 rows | role-match (no RETIRED precedent exists — see below) |

---

## Pattern Assignments

### 1. `.claude/skills/devtest-rootcause/scripts/diff_db.py` (created, meta)

**Analogs:** `.claude/skills/devtest-rootcause/scripts/infoic_lookup.py`,
`.claude/skills/devtest-rootcause/scripts/seed_debug_session.py`

Both existing skill scripts are **stdlib-only, `argparse`-driven, executable (`chmod +x`), zero-import-from-
`firestarter_app`**. They locate data outside their own directory with an *identical, copy-pasted* four-level
walk-up + env override. Copy that shape verbatim into the relocated `diff_db.py`.

**Repo-root resolution + env seam** (`infoic_lookup.py:35-42`, byte-identical to `seed_debug_session.py:86-93`):

```python
def _repo_root() -> str:
    """Locate the checkout from this file: <root>/.claude/skills/<s>/scripts/.

    Falls back to the current directory when the skill is installed outside a
    checkout, where an explicit flag or env override is the only sane source.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, *[os.pardir] * 4))
    return root if os.path.isdir(os.path.join(root, "firestarter_app")) else os.getcwd()


DEFAULT_APP = os.environ.get(
    "FIRESTARTER_APP", os.path.join(_repo_root(), "firestarter_app"))
```

**Why this is the load-bearing pattern here.** `diff_db.py:30-31` today resolves both inputs relative to
`__file__`:

```python
_DATA_DIR     = os.path.join(os.path.dirname(__file__), "..", "firestarter", "data")
_BASELINE_DIR = os.path.join(os.path.dirname(__file__), "baseline")
```

Under `.claude/skills/devtest-rootcause/scripts/` those resolve to two directories that **do not exist**, and
the 476 KB baseline stays at `firestarter_app/tools/baseline/` (D-14 puts it out of scope). The file already
carries the correct seams at `:33-40`:

```python
DB_FILE       = os.environ.get("FIRESTARTER_DB_FILE",       os.path.join(_DATA_DIR, "chip_database.json"))
BASELINE_FILE = os.environ.get("FIRESTARTER_BASELINE_FILE", os.path.join(_BASELINE_DIR, "chip_database.baseline.json"))
```

**The edit to make:** re-point `_DATA_DIR` / `_BASELINE_DIR` at `_repo_root()`-derived paths using the analog's
exact function, so the defaults are correct without env vars, and keep the two `os.environ.get` seams as the
override. Add an `--app` flag only if you follow `infoic_lookup.py:266` (`ap.add_argument("--app", default=DEFAULT_APP, ...)`).

**Argparse/exit shape** (`infoic_lookup.py:261-263, 326`):

```python
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ...
sys.exit(main())
```

**Do NOT sweep citations from this copy.** It lands under `.claude/` in the meta repo — outside
`firestarter_app/tools/` (TOOLS-05's scope) and outside CLAUDE.md's comment rule's scope (`firestarter/` +
`firestarter_app/`). Its 9 `.planning` refs, 19 phase refs, 9 `D-NN` refs and the runtime string at `:911`
stay. (RESEARCH §"TOOLS-05 does not follow the file".)

**Caller update, same wave** — `seed_debug_session.py:68` emits one command line chaining
`build_db.py && diff_db.py && check_dispatch.py && pytest`. Drop the `check_dispatch.py` clause
(`seed_debug_session.py:59, 69`) and re-point the `diff_db.py` clause at the new path with its two env vars:

```bash
FIRESTARTER_DB_FILE=firestarter_app/firestarter/data/chip_database.json \
FIRESTARTER_BASELINE_FILE=firestarter_app/tools/baseline/chip_database.baseline.json \
python3 .claude/skills/devtest-rootcause/scripts/diff_db.py
```

---

### 2. The surviving home for `dispatch()` + `_ALGO_MEM_TYPE` / `_SRAM_PROTOCOLS` / `KNOWN_PROTOCOLS` (created, app test tier)

**This is RESEARCH Q1 — BLOCKING, needs the operator checkpoint before any file is written.** The pattern
below is what option (a) looks like if it is chosen.

**Analogs:** `firestarter_app/tests/fw_presence.py` (the canonical non-test helper under `tests/`),
`firestarter_app/tests/plan_corpus.py` (a shared oracle/corpus module, same tier).

**Import convention — measured, and it contradicts what the six consumers do today.** `tests/__init__.py`
exists and is **empty (0 bytes)**, so `tests/` is a real package and the established import is
`tests.`-qualified at module level:

```python
from tests.fw_presence import fw_path, requires_fw          # tests/test_gen_validation_header.py:18
from tests.plan_corpus import REAL_DB                        # tests/test_canonical_part_number.py:38
from .fake_chip import FakeChip  # noqa: E402                # tests/test_chip_test.py:3297 (relative variant, rarer)
```

Measured spread: 18 `from tests.X import` sites vs 3 relative `from .X import` sites. **Use the
`from tests.<module> import ...` form.**

**What must be replaced.** The six `test_val_wire_*` modules currently do a `sys.path` prepend of `tools/`
(`tests/test_val_wire_sram.py:28-33`):

```python
# Add tools directory so check_dispatch is importable
_TOOLS_DIR = Path(__file__).parent.parent / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from check_dispatch import _SRAM_PROTOCOLS, dispatch  # noqa: E402
```

The repair deletes the three `sys.path` lines **and** the `# noqa: E402` (no longer a late import), leaving a
top-of-file `from tests.dispatch_model import _SRAM_PROTOCOLS, dispatch`. Do the same at the five in-function
sites in `tests/test_decoder.py:703,713,723,733,743` and at `tests/test_build_db_inclusion.py:729`.

**Module-docstring shape for a test-tier helper** — `fw_presence.py:1-12` is the model: license header, one
sentence naming what the module *is*, then the measured defect it exists to fix. Note it carries citations
(`BASE-02, D-09, ...; Phase 123 Plan 07`) — `tests/` is **out of the TOOLS-05 sweep** (deferred idea), so a
new `tests/` helper is not swept. But per `/workspaces/CLAUDE.md` the executor still **may not write a new
GSD-process comment**: describe the model, not the phase.

**Symbols to carry across, with their guarding comments** (`tools/check_dispatch.py`):

```python
# tools/check_dispatch.py:36-38
_ALGO_MEM_TYPE = { 0x05: 5, ... }   # "Must mirror firestarter_app/firestarter/database.py::_ALGO_MEM_TYPE"

# tools/check_dispatch.py:53-55  — keep this comment, it explains the code, not a phase
# (BLOCKER-2 electrical-safety; configure_eprom calls eprom_check_vpp which
# enables the VPP boost regulator on a 5V SRAM part).
_SRAM_PROTOCOLS = {0x0E, 0x27, 0x28, 0x29}

# tools/check_dispatch.py:118-124 — keep; it names a real non-membership invariant
# X88C64P having proto=0x34 NOT in this set — that is what makes the assertion pass for
# that chip. Do NOT add 0x34 here ("keep in sync" means structure, not membership).
KNOWN_PROTOCOLS = { ... }

# tools/check_dispatch.py:136-137
def dispatch(protocol, mem_type):
    """Mirror firmware D2 dispatch order in memory.cpp::configure_memory."""
```

The `main()` gate half (`check_dispatch.py:177+`), its exit-code docstring block and its JSON/DB loading do
**not** come across — that is the half D-01 retires.

**The same shape applies to the other three orphaned symbols** in the same checkpoint:
`snapshot_report_shapes.render_shape` (38 tests, `test_blast_radius_invariance.py:758,820`),
`check_devtest_orchestrator._HANDLER_FUNCTION_NAMES` (7 tests, `test_op_registration_parity.py:113,365`),
`check_diagnostic_report_claims.FORBIDDEN_PATTERNS` (1 test, `test_parse_devtest_issue.py:740`).

---

### 3. `.planning/notes/host-tools-retirement.md` (created, meta)

**Analog:** `.planning/notes/catalog-sync-check-retirement.md` (named by D-23), corroborated by
`.planning/notes/dispatch-invariant-retirement-verdict.md`.

**Copy this exact skeleton.** YAML frontmatter, an H1 repeating the title with its claim ID in parens, a
`## VERDICT` section *first* stating the outcome in bold before any evidence, then numbered `## N. <clause>`
sections — one per thing the note is required to carry — then a closing Q&A section:

```markdown
---
title: Catalog sync check retirement — why it never asserted what it claimed, and what is lost with it
date: 2026-09-11
context: v1.37 Phase 185, CLAIM-08 (D-01, D-02, D-03) — read from the live workflow file before deletion
---

# Catalog sync check retirement (CLAIM-08)

## VERDICT

**`Catalog sync check` is retired outright — the workflow file is deleted, on the operator's own
decision, taken against the orchestrator's recommendation to re-point its trigger at `beta`.** ...
The operator's grounds, in their own words: ... That is recorded here so a later reader does not
read the deletion as an oversight or as evidence the property stopped mattering ...

This note carries all five things CLAIM-08's amendment requires it to carry: <enumerated>.

## 1. The cause
## 2. Why the 2026-08-18 fix did not fix it
## 3. That the workflow's own comment is now false
## 4. That a naive `beta` fallback would not have worked either
## 5. The residual gap, named explicitly
## Two questions a reader will ask next
```

Four features to reproduce, each load-bearing:

1. **Verbatim quotation of the thing before deletion** — the analog quotes the workflow's own comment block
   in a fenced block *because the source file is being deleted and the note is the only place the correction
   can land*. Phase 188 should do the same for anything a deleted survivor's prose asserted (e.g.
   `firestarter_app/CLAUDE.md:122-128`'s "Regression guard: `tools/check_dispatch.py` asserts…").
2. **A measured evidence table** — the analog's 8-run history table. Phase 188's equivalent is one line per
   retired item naming *what it guarded* and *why it went* (D-23), plus the measured line counts.
3. **The residual gap stated, not filed** — the analog's §5 closes with:
   *"**No successor guard and no backlog item are filed for this gap.** This is deliberate, on the operator's
   own decision (D-04) … Naming a gap and filing a gap are different acts; this note performs only the first."*
   Copy that formulation for the four disclosed costs (D-08 wire-contract proof, D-12 declaration blind spot,
   D-13 firmware-rename masking guard, D-15 `derive_sdp_partition.py`).
4. **A sharper restatement of what is lost** — the analog escalates from "nothing checks X" to "the meta
   repository runs no CI at all". Phase 188's equivalent: state plainly that after D-08 nothing proves host
   and firmware agree on the same wire bytes.

The second analog (`dispatch-invariant-retirement-verdict.md`) adds two section headings worth reusing:
`## WHAT THE DELETED FIXTURES PROVED` (`:199`) and `## WHAT THIS PHASE DELIBERATELY DID NOT DO` (`:299`).

---

### 4. CI workflow step deletions (edited — 3 files, 2 repos)

**Analog: the file's own surviving sibling pair.** Every one of the six steps to delete is the second half of
a two-step `<X> validity check` + `Codegen drift gate (<artifact>)` pair whose `messages` twin **stays**
(D-10). Read the surviving twin, delete its vector mirror, change nothing else.

**Host `firestarter_app/.github/workflows/ci.yml:55-75` — the shape, with keep/delete marked:**

```yaml
      - name: Catalog validity check                                    # STAYS (D-10)
        run: python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check

      - name: Codegen drift gate (messages.py)                          # STAYS (D-10)
        run: |
          python3 tools/catalog/codegen.py \
            --catalog tools/catalog/messages.toml \
            --target firestarter/messages.py \
            --language python
          git diff --exit-code firestarter/messages.py

      - name: Vector catalog validity check                             # DELETE :66-67 (D-09)
        run: python3 tools/catalog/codegen_vectors.py --catalog tools/catalog/frame-vectors.toml --check

      - name: Codegen drift gate (frame_vectors.py)                     # DELETE :69-75 (D-09)
        run: |
          python3 tools/catalog/codegen_vectors.py \
            --catalog tools/catalog/frame-vectors.toml \
            --target firestarter/frame_vectors.py \
            --language python-vectors
          git diff --exit-code firestarter/frame_vectors.py
```

Plus `ci.yml:86-87` (D-02):

```yaml
      - name: mypy type check (watermark gate)                          # DELETE (D-02)
        run: python tools/check_mypy_watermark.py
```

**Firmware `firestarter/.github/workflows/build.yml:122-131`** is the identical pair with
`--target include/frame_vectors.h --language cpp-vectors` and `git diff --exit-code include/frame_vectors.h`.
**`beta-build.yml:101-116`** is the same pair preceded by a six-line `#` comment block explaining why the pair
was duplicated there — **delete the comment block with the steps**; it becomes false otherwise.

**Mechanical rules for all six:** each block is `- name:` + its `run:` body and the **single blank separator
line before the next `- name:`** (host: lines 68, 76, 88). Leave no double blank. Also amend `ci.yml:3`, a
header comment reading *"gate steps: ruff check, ruff format --check, mypy watermark, pytest --cov"* — it
becomes false with D-02, in the same commit.

---

### 5. `size_baseline.json` + its two native fixture logs (re-record, firmware)

**Analog:** `.planning/phases/185-records-and-checks-that-are-current/185-01-PLAN.md`, Task 1
(*"TRACER — one cold pass, one commit: capture, transcribe, sever, green"*). It is the only precedent for this
operation and D-20 names it as the fallback.

**The rules it encodes, quoted from its own criteria:**

> `185-01-PLAN.md:27` — "Every AVR figure written into `scripts/baseline/size_baseline.json` was TRANSCRIBED
> from a `Flash:`/`RAM:` report line in a `captured_build_v185_*.log` this task captured, and every native
> figure from an `N test cases: N succeeded` line in a `captured_test_native*_summary.log` this task
> re-captured. **No figure was computed by arithmetic on any prior record.**"

> `185-01-PLAN.md:29` — "`size_baseline.json` moves `avr_targets` AND `native_envs` in the same edit —
> `compare_native` asserts `cases` exactly, so a re-record that picks up only the flash figures leaves the
> gate red."

> `185-01-PLAN.md:40` — "MUST NOT re-anchor `scripts/baseline/size_baseline_base01.json`, and MUST NOT edit
> any `merge05_*` or `planted_size_baseline_policy_*` fixture."

**Phase 188's narrowed version** (D-20 — AVR verified unchanged, `flash_used: 22734` reproduced cold): move
only the native pair. Capture recipe, run from `/workspaces/firestarter` **after** the suite and its four
`platformio.ini` registrations (`:101`, `:122`, `:160`, `:182`) are deleted, in the tree that will be
committed:

```bash
rm -rf .pio/build/native .pio/build/native_nodevtools
pio test -e native              2>&1 | tee tests/fixtures/<capture>native.log
pio test -e native_nodevtools   2>&1 | tee tests/fixtures/<capture>native_nodevtools.log
```

**Fixture-update convention — updated IN PLACE, never severed** (`185-01-PLAN.md:183-184`): the two
`tests/fixtures/captured_test_native{,_nodevtools}_summary.log` files are re-captured over themselves. The
sever-onto-a-new-family convention applies to the AVR `captured_build_*` family only. Both fixtures are
**21 lines** — the `=== SUMMARY ===` block only, not the 6,954-line raw log; truncate to preserve the shape.

**JSON sites to move** (`firestarter/scripts/baseline/size_baseline.json`): `:69`/`:70`/`:71` and
`:75`/`:76`/`:77` (`cases`, `succeeded`, `suites`) plus `:88` `envs_agree_note`, which quotes the same figures
**in prose** and must move with them. `native_pinmap_provisional` (`:80-85`) is untouched.

**Verification leg, copied from `185-01-PLAN.md:273`** (the checker exits 1 with no args by design):

```bash
cd /workspaces/firestarter && python3 scripts/check_size_baseline.py \
  --native-log native=tests/fixtures/captured_test_native_summary.log \
  --native-log native_nodevtools=tests/fixtures/captured_test_native_nodevtools_summary.log
```

`fails_when`: non-zero exit, or a `FAIL:` line instead of a single `PASS:` line.

**Same commit, or firmware CI is red:** `firestarter/tests/test_check_size_baseline.py::test_clean_native_both_envs_pass`
asserts `"185" in result.stdout` and `"17" in result.stdout`, and
`tests/fixtures/planted_size_baseline_suites_errored.log` still names the deleted suite (H3).

---

### 6. The D-16 citation strip on the six survivors (edited, app + meta)

**Analogs — two real, already-landed sweep edits in this repo:**

`0f53959` *style(181-06): drop the GSD-provenance comment from the HYG-04 allow-list*, on
`firestarter_app/tools/check_devtest_orchestrator.py:148-152` — **keep the sentence, delete the provenance
clause**:

```diff
 # added to the `dev test` surface MUST be listed here, or this gate silently
 # under-covers exactly that new code -- `tests/test_check_devtest_orchestrator
 # .py::test_handler_function_names_all_resolve_to_real_callables` makes this
-# a permanently-enforced invariant rather than a one-off fix. `_cli_start_time`
-# (Phase 181 plan 06, RPT-D2) is the newest entry.
+# a permanently-enforced invariant rather than a one-off fix.
 _HANDLER_FUNCTION_NAMES = frozenset(
```

`bffbba8` *docs(185-04): drop the stale `build_db.py:594` line citation* — same move inside a docstring:

```diff
-     on `_AT28C_DIP24_NAMES` (build_db.py:594) -- that set literal (not
+     on `_AT28C_DIP24_NAMES` -- that set literal (not
```

Its commit message states the governing test for "is this edit correct?":
*"Deleted the parenthetical outright rather than correcting the number — the very next clause in the same
sentence already states the symbol's true scope."*

**The rule, applied to the 30 measured survivor hits** (RESEARCH §The Six Survivors' Citations): every hit is
*"keep the comment, drop the identifier"*. Concretely, from the same source:

| File | Before | After |
|---|---|---|
| `build_db.py:457` | `# DB-07: Initialize support classification fields.` | `# Initialize support classification fields.` |
| `build_db.py:150` | `# NOT 0x35 or 0x39 — removed by v1.11 DEC-05` | `# NOT 0x35 or 0x39 — removed` |
| `catalog/codegen.py:21` | `Determinism contract (LCAT-05): two consecutive runs…` | `Determinism contract: two consecutive runs…` |
| `catalog/codegen.py:151` | `# 2. CATALOG VALIDATION (LCAT-02 + LCI-04)` | `# 2. CATALOG VALIDATION` |

**Hard constraints on this edit, all non-overridable:**

- **Never write a new comment.** `/workspaces/CLAUDE.md` §"Source code comments — hard rule" permits deleting;
  it forbids authoring. The commit message is where the rationale goes (see both analog commits — the whole
  explanation lives in the message, none of it in the file).
- **Never touch `firestarter_app/tools/catalog/codegen.py`.** D-17: edit `/workspaces/tools/catalog/codegen.py`
  (the canonical copy, sha256-identical across all three repos), then run `tools/catalog/sync_to_subrepos.sh`.
  Prove the regenerated artifacts unchanged *after* the sync — the script's own `diff -q` is trivially true:
  ```bash
  cd /workspaces/firestarter     && git diff --exit-code include/messages.h
  cd /workspaces/firestarter_app && git diff --exit-code firestarter/messages.py
  ```
- **Never touch datasheet citations.** `build_db.py:116` and siblings carry
  `[CITED: firestarter/datasheets/…/W29C020.pdf §6.2 …]` — the generator-proof rule depends on them.
- **Two of the hits are user-facing strings**, not comments: `parse_devtest_issue.py:390` and
  `gen_sdp_bus_config.py:347` are `argparse` `description=`; `gen_sdp_bus_config.py:280` is a `ValueError`
  message. Standing memory: Click/argparse docstrings are `--help` text, not commentary (RESEARCH Pitfall 2 /
  Open Q2).
- **By hand, never a regex.** D-18: three automated passes were reverted for collateral damage.
  `gen_test_image.py:20-21` encodes a phase number as `p82` inside a `/tmp/` path — no citation regex matches
  it. Run `ruff format --check firestarter/ tests/` and the suite after each batch. `catalog/codegen.py`
  itself is **not** ruff-format clean — do not run `ruff format` on it (RESEARCH Pitfall 3).

---

### 7. `.planning/REQUIREMENTS.md` + `.planning/ROADMAP.md` ledger amendment (D-22)

**Measured gap: there is no `RETIRED` precedent.** `/usr/bin/grep -n "RETIRED" .planning/REQUIREMENTS.md`
returns **zero hits**. Phase 188 mints the disposition. Follow the two shapes that do exist.

**(a) Traceability row shape — the `Complete — <cause>` form is the model** (`REQUIREMENTS.md`, FLOOR block):

```markdown
| FLOOR-01 | Phase 186 | Complete — all four statements raised to 3.11 together (186-01), the sweep absorbed (186-02), and a fail-closed agreement gate now asserts it (186-03) |
```

Current Phase 188 rows all read `| TOOLS-0N | Phase 188 | Pending … |`. Rewrite the disposition cell in the
same `<word> — <cause> (<plan id>)` form, substituting `RETIRED` for `Complete`:

```markdown
| TOOLS-01 | Phase 188 | RETIRED — dissolved by tool deletion; `audit_coverage_matrix.py` no longer exists, so the repo-escaping default path it guarded cannot occur (D-04/D-06) |
| TOOLS-02 | Phase 188 | RETIRED — declaration layer and its check both dropped on operator decision; the audit's blind spot is carried, not closed (D-12) |
| TOOLS-06 | Phase 188 | RETIRED — both files deleted (D-08), so there is nothing left to sync (D-11) |
```

The checkbox in `REQUIREMENTS.md` §TOOLS stays `- [ ]` for a RETIRED requirement — **never flip it to `- [x]`**;
that is the whole point of D-22's "RETIRED is not Complete".

**(b) Success-criterion amendment shape — amend in place, quote the conflict, never delete the original**
(`ROADMAP.md:510`, Phase 187 criterion 4):

```markdown
4. gh#9 carries a closing reply or is closed as done. **AMENDED by Phase 187 (D-07):** this criterion is
   already satisfied by the pre-existing comment [`#issuecomment-5511487546`](…)
   (posted 2026-09-02, Phase 173-07) — gh#9 stays open and pinned, and Phase 187 posts nothing new per D-06.
```

A second, denser instance at `ROADMAP.md:2287` closes with the retained-negative-case formulation worth
copying when a criterion is being *reversed*:
*"(This criterion previously read '…'. That was written when Phase 150 was in scope; it is … retained here
only as the negative case the gate in criterion 5 must catch.)"*

**(c) Plan-line shape in the Wave block** (`ROADMAP.md:457`, 185-06):

```markdown
- [x] 185-06-PLAN.md — CLAIM-08 (D-01, D-02, D-03, D-04): the `.planning/notes/` verdict document with all five required contents quoted from the workflow before it is deleted, the workflow retired outright, and CLAIM-08 plus this criterion 5 amended by hand with the conflict and the precedent on the record — no successor guard filed
```

**Hard constraint:** `roadmap.update-plan-progress` MUST NOT be run against this phase — it overwrites the
dependency table positionally, killing the phase name and requirement IDs (D-22 + standing memory). Hand
edits only.

---

## Shared Patterns

### No comments in product source — the governing rule for every edit in this phase
**Source:** `/workspaces/CLAUDE.md` §"Source code comments — hard rule"
**Apply to:** everything under `firestarter/` and `firestarter_app/` — items 2, 4, 5, 6 above.
The executor may **delete** a comment; it may **never write one**. Rationale goes in the `SUMMARY.md` or the
commit message. `bffbba8` and `0f53959` are the two in-repo demonstrations: the entire explanation lives in
the commit message, and the file gets shorter.

### Deletion-with-repair in one commit
**Source:** D-21(a), D-13, and `185-01-PLAN.md`'s "one cold pass, one commit" framing
**Apply to:** every deletion wave.
Three separate populations go red *between* commits if split: CI steps vs the tools they invoke; the firmware
suite vs the baseline re-record; `tests/scan_paths.py` vs the 8 tools it indexes (it fails closed on a missing
file). Pair each deletion with its repair in the same commit.

### Retirement writes a note, never a successor guard
**Source:** `.planning/notes/catalog-sync-check-retirement.md` §5; `tools/wiki/` retired 2026-09-02 with no
replacement; `.planning/notes/dispatch-invariant-retirement-verdict.md`
**Apply to:** item 3.
*"Naming a gap and filing a gap are different acts; this note performs only the first."* D-23 forbids any new
`check_*.py` or CI gate from this phase for any reason.

### Search with `/usr/bin/grep` or `git grep`, never the bare devcontainer `grep`
**Source:** RESEARCH §Dangling-Reference Sweep; standing memory
**Apply to:** the D-19 dangling-reference sweep and every evidence leg in every plan.
The devcontainer's `grep` is ugrep and honors `.gitignore`, silently under-scanning. A naive
`grep "tools.check_dispatch"` also misses all six `test_val_wire_*` modules, which import bare via a
`sys.path` prepend.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| — | — | — | Every created/edited file in this phase has a tracked in-repo analog. |

The nearest thing to a gap is the **`RETIRED` requirement disposition**, which has no prior instance in
`REQUIREMENTS.md` (measured: zero hits). Item 7(a) above supplies the shape by analogy to the existing
`Complete — <cause>` rows rather than inventing one.

## Metadata

**Analog search scope:** `/workspaces/.claude/skills/devtest-rootcause/scripts/`, `/workspaces/.planning/notes/`,
`/workspaces/.planning/phases/185-*/`, `/workspaces/.planning/ROADMAP.md`, `/workspaces/.planning/REQUIREMENTS.md`,
`firestarter_app/tests/` (non-`test_` modules), `firestarter_app/tools/`, `firestarter_app/.github/workflows/`,
`firestarter/.github/workflows/`, `firestarter/scripts/baseline/`, plus `git log` over the app repo's landed
provenance-sweep commits.
**Files scanned:** ~30 read or excerpted; ~46 deletion targets deliberately not mapped.
**Tracked-source gate:** all analog paths verified with `git ls-files` in their owning repo; no gitignored
mirror paths are cited.
**Pattern extraction date:** 2026-09-12
