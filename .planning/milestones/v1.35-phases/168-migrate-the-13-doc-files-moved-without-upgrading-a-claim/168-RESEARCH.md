# Phase 168: MIGRATE — The 13 `doc/` Files, Moved Without Upgrading a Claim - Research

**Researched:** 2026-08-31
**Domain:** Documentation migration across three git repositories; git-wiki publishing; Python packaging and test-suite surgery; standalone stdlib checker tooling
**Confidence:** HIGH — every number below comes from a command run in this session against the live tree, the live wiki and the live PyPI registry. Nothing is estimated.

---

## Summary

This phase is **not** a research problem — CONTEXT.md D-01…D-22 already settled the design. It is a
**measurement** problem, and the measurements materially change what the planner must write. Six of
CONTEXT.md's stated facts are wrong or incomplete, and two of them would produce a shipped, green,
lying gate if carried into a plan unchecked.

The three findings that most change the plan:

1. **Deleting `firestarter/doc/PROTOCOLS.md` while the firmware sibling is present aborts the
   *entire* `firestarter_app` test suite at collection — 0 tests run, not 1 module red.**
   `tests/test_dispatch_mirror.py:38` calls `fw_path("doc", "PROTOCOLS.md")` at module scope, and
   `fw_path` *raises* `MissingScanTargetError` when the repo is present but the target is not
   (`tests/fw_presence.py:130-140`). Proven below. This is a hard ordering constraint, not a risk.

2. **MIGRATE-03's stated premise is false.** No `doc/` file is in the current sdist. Built from a
   clean checkout of `HEAD`, the sdist contains **zero** `doc/` entries; the published
   `firestarter-3.0.0b33` and `3.0.0b34` sdists on PyPI contain **zero** `doc/` entries. The
   `SOURCES.txt:28-30` lines everyone has been citing come from a **stale, gitignored egg-info
   artifact** in the working tree. The packaging delta is a genuine no-op and must be *reported as
   a no-op*, exactly as D-04 requires the `vpp-exceeds-max` half to be reported as vacuous.

3. **D-09's "part numbers and algorithm values a stamped page asserts must resolve in the current
   database" is unimplementable as a green gate on this corpus.** Measured: 3% of the part-shaped
   tokens in `lockable-proms.md` resolve; 11 of the 20 `0xNN` tokens in `SHIELD-REVISIONS.md`
   "resolve as algorithms" by pure numeric coincidence (they are ADC-band and control-register
   values). A free-text scrape produces both massive false-RED and silent false-GREEN. The check
   must be scoped to an explicitly delimited claim region or an allowlist.

**Primary recommendation:** Sequence the phase around three irreversible ordering constraints
(§Ordering Hazards), scope both HONEST checkers to **checked-in claim data rather than free-text
scraping**, and treat the currently-live `Home.md` as the phase's ready-made demonstrated-RED for
WIKI-05 — it already fails `wiki.py links` with 12 orphans the moment the pages land.

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `168-CONTEXT.md` `## Implementation Decisions`. **D-03, D-11 and D-15 are
operator decisions and are not revisable.** The remainder are "locked but revisable on evidence" —
this document supplies evidence against parts of D-04, D-09, D-11, D-14 and the `code_context`
section, flagged inline.

**Claim honesty — HONEST-01, criterion 4**

- **D-01: The claim-diff unit is a claim-token multiset, not a text diff.** The checker extracts a
  defined claim vocabulary from the pre-deletion source and from the published wiki, and compares
  the two multisets. A whole-file or line-level diff is unusable here by construction: the
  migration necessarily edits titles, rewrites relative links for a flat page namespace, and strips
  GSD framing (D-11), so a text diff is guaranteed non-empty for innocent reasons — and a check
  that is non-empty for innocent reasons gets ignored (`catalog-sync-check.yml`, 5 runs, 5
  failures, zero assertions).
  The vocabulary is **checked in as data, not embedded in the checker**, and covers two families:
  (a) the literal `support_status` values, and (b) the negative-capability vocabulary that is what
  "upgrading a claim" actually means in prose — *not implemented*, *unsupported*, *requires an
  adapter*, *cannot*, *do not*, *never*, *unverified*, *at your own risk*, and stated voltage
  ceilings. A hedge quietly becoming a promise is the failure mode; a renamed heading is not.
  Rejected: whole-file normalized diff (drowns in intentional edits); claim-*line* diff (still
  sensitive to reflow and to the link rewrites every page gets).

- **D-02: The pre-deletion snapshot is a git SHA per row in `.planning/v1.35/MIGRATION-TABLE.md`, not a
  committed copy of the documents.** Each of the 12 rows records the sub-repo commit immediately
  before its `doc/` file is deleted; the checker reads the source side with
  `git -C <subrepo> show <sha>:doc/<file>`. Zero content duplication, exact, and — decisively —
  **WIKI-02-clean**. **The SHAs must be recorded before the delete commits, or the oracle is gone.**

- **D-03: HONEST-01 is a one-shot in-phase proof, not a standing gate.** *(Operator decision.)* It
  runs during the migration, is demonstrated failing on a deliberately weakened claim before any
  green result is believed, and its output is committed as evidence. Then it retires. HONEST-02 is
  the standing truth gate.

- **D-04: The vacuous half is reported as vacuous, in the checker's own output.** `support_status`
  appears 12× as a field name in only 3 files; only two values occur — `adapter-required` ×4 and
  `protocol-not-implemented` ×1. **`vpp-exceeds-max` occurs 0 times. `UNVERIFIED` /
  `PROTOCOL-LEDGER` occurs 0 times.** The checker must print the zero counts explicitly.

**The two clone-based gates — HONEST-02 criterion 5, WIKI-05 criterion 8**

- **D-05: Two checkers, one workflow, one shared clone step.**
- **D-06: WIKI-05 is `wiki.py links` repointed at the clone, plus one new leg.** `DEFAULT_SOURCE_DIR`
  is hardcoded to `<repo>/wiki` (`tools/wiki/wiki.py:45`), a directory this phase deletes, so the
  default must move or the flag must become required. Existing semantics **kept unchanged**: only
  `Home.md` counts as reachability evidence; `_Sidebar.md` is in `NAV_EXCLUDED_PAGES`. **New leg:**
  the hand-maintained `_Sidebar.md` lists every page.
- **D-07: HONEST-02 is a new standalone checker in `tools/wiki/`, same shape as `wiki.py`** — a
  `python3` script with the 0/1/2 exit contract, driven by `selftest.sh`.
- **D-08: The stamp cannot say "generated from DB vN" — there is no DB version. It carries a
  content hash and a date.** Current value at discussion time: `0cfd3a83e881bfcc`.
- **D-09: Stamp-plus-resolve, because 11 of 12 pages carry per-chip or per-protocol claims.** The
  checker asserts three things: (1) every page matching the claim signature carries a stamp;
  (2) the part numbers and algorithm values a stamped page asserts **resolve in the current
  database**; (3) the stamp's hash matches the current database — a mismatch flags the page
  **stale**, a distinct outcome from *wrong*.
- **D-10: Scheduled weekly plus `workflow_dispatch`, and demonstrated failing twice — fixture and
  live.**

**Legacy framing — LEGACY-06, criterion 6**

- **D-11: Every unopenable `.planning/` path goes, in all 12 files; the two named files are fully
  de-framed; "as of Phase NN" prose stays.** *(Operator decision.)* The distinguishing test is
  **can a public reader act on this?** The two named files additionally lose their `— Phase 58` /
  `— Phase 59` titles, their `**Full audit trail:**` pointers, and the three
  `[CITED: .planning/research/PITFALLS.md §E-3]` markers in `sram-nvram-behavior.md`.
- **D-12: Both files ship, rewritten — they are not dropped.**

**Link repair — MIGRATE-04, criterion 2**

- **D-13: References are repaired to a page *title*, not a URL — everywhere except the two READMEs.**
- **D-14: The 18 database references are fixed in the generator and regenerated — the JSON is never
  hand-edited.** The fix is: edit the emitter, regenerate, re-baseline.
- **D-15: The `proto_constants.h` provenance comment is deleted, not repointed.** *(Operator
  decision.)*
- **D-16: `firestarter/CLAUDE.md`'s lockstep-maintenance rule must survive the move.**
- **D-17: The READMEs are repaired in 168 even though 169 and 170 rewrite them.**
- **D-18: Historical and archive records are excluded from repair — explicitly and by name.**
  Named: `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`,
  `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`,
  `firestarter/tests/golden/eprom_params_citations.json`,
  `firestarter_app/.planning/codebase/STRUCTURE.md`.

**Getting content onto the wiki, and retiring Phase 167's tooling — WIKI-02, criterion 7**

- **D-19: Content reaches the wiki by cloning `firestarter_prom.wiki.git`, committing the pages, and
  pushing.** No tooling is built or retained for it.
- **D-20: Retirement is deletion, not dormancy.** Removed: `wiki/` (all 3 files),
  `.github/workflows/wiki-publish.yml`, and `wiki.py`'s `publish`, `sidebar` and `check`
  subcommands with their argparse entries and selftest legs. Kept: `.planning/v1.35/MIGRATION-TABLE.md`,
  and `wiki.py links` per D-06. `.github/workflows/wiki-check.yml` is repointed at the clone.
- **D-21: `How-This-Wiki-Is-Published` is live, public and false — it is rewritten in this phase,
  not deleted.**
- **D-22: `Home.md` is live and false in three places — it is rewritten too.** Its "Coming to this
  wiki" list becomes the real index, and it is what `wiki.py links` walks for reachability.

### Claude's Discretion

> Verbatim from CONTEXT.md `### Claude's Discretion`.

The operator answered the three decisions that were his — HONEST-01's lifetime (D-03), the
de-GSD-ification boundary against his own activation decision 4 (D-11), and the source comment
against his no-comments rule (D-15). Everything else above was decided from measured facts and
recorded precedent and is offered to the planner as **locked but revisable on evidence**, not as
operator-locked: D-01/D-02/D-04, D-05…D-10, D-12, D-13/D-14/D-16/D-17/D-18, D-19…D-22.

Two things are deliberately left to research and planning:

- **Wiki push authentication** — whether the default `GITHUB_TOKEN` with `contents: write` can push
  to `.wiki.git`, or a PAT secret is needed. Only the HONEST-02/WIKI-05 workflow needs read (clone)
  access; D-19's push is a local operator-run action. `gh` is authenticated locally as `henols`.
  → **Answered in §Wiki Push and Clone Mechanics below.**
- **Page-name resolution for the two hyphen hazards** — `AT28C04-ADAPTER.md` and
  `sram-nvram-behavior.md`. → **Constraints measured in §Page-Name Resolution below.**

### Deferred Ideas (OUT OF SCOPE)

> Verbatim from CONTEXT.md `## Deferred Ideas`.

- **A durable anti-erosion gate for HONEST-01** — rejected as this phase's mechanism (D-03). If wiki-side
  claim erosion later proves real, the shape to revisit is a claim-token *floor*.
- **Exhaustive per-claim verification of all 11 claim-bearing pages** — out of reach in this phase (D-09).
- **The compatibility matrix, family pages, algorithm pages and tutorials** — deferred as FUT-W-01…05.
- **Re-sweeping every wiki URL after Backlog 999.9's repository rename** — accepted sequencing hazard.
- **External link liveness checking** — deferred at 167 (D-11), still deferred.
- **The `todo.match-phase 168` set** — reviewed and deferred wholesale, including
  `sync_to_subrepos.sh`'s self-diff defect (same class, wrong tooling, scope creep).

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MIGRATE-01 | Content of all 12 migrating `doc/` files reachable on the wiki | §The Corpus (line counts, 3 cross-file links, 18 anchors, page-name constraints); `wiki.py links` proven to detect the 12 orphans |
| MIGRATE-02 | `firestarter/doc/` and `firestarter_app/doc/` no longer exist | §Ordering Hazards H-1 — deletion order is load-bearing; §Repair Surface — 30 files / 79 lines measured |
| MIGRATE-03 | App still builds, installs, passes suite after removal | §MIGRATE-03 on the CI Python Floor — 1976-test baseline on 3.11, 17 doc-caused failures measured, **sdist delta proven to be zero** |
| MIGRATE-04 | No file in either sub-repo links to a dead `doc/` path | §Repair Surface — complete measured inventory split (a)/(b)/(c), including 8 sites CONTEXT.md missed |
| HONEST-01 | Every `support_status` value / `PROTOCOL-LEDGER` UNVERIFIED bucket survives the move | §The Claim Vocabulary — 13 occurrences resolved, vacuity confirmed, D-01's stated vocabulary partly vacuous too |
| HONEST-02 | Claim-bearing pages carry a check or a stamp | §HONEST-02 Truth Sources — sha256 confirmed, 746 rows / 12 algorithm values, **resolve-check falsified as a free-text scrape** |
| LEGACY-06 | No page titled/framed as a GSD phase artifact | §GSD Framing Inventory — 16 `.planning/` refs in 5 files (not 15 in 6), 52 `Phase NN` mentions (not 41) |
| WIKI-02 | No in-repo mirror; wiki is the single home | §Retiring `tools/wiki/` — exact line ranges, argparse entries and the 7 selftest cases to delete |
| WIKI-05 | Every page reachable from Home or the sidebar | §The Live Wiki — the current `Home.md` already produces a live 12-orphan RED, no fixture needed |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Publishing the 12 pages | Operator workstation (git push to `firestarter_prom.wiki.git`) | — | D-19: no tooling; a publish path is a loaded gun aimed at a live wiki |
| HONEST-01 claim comparison | Meta repo, one-shot `tools/wiki/` script | Sub-repo git history (via `git show <sha>:doc/…`) | D-02/D-03: source oracle is a git ref, not a file |
| HONEST-02 truth gate | Meta repo CI (`schedule` + `workflow_dispatch`) | `firestarter_app` submodule/checkout for `chip_database.json` | Needs wiki clone AND database together; neither sub-repo has both |
| WIKI-05 reachability | Meta repo CI, `wiki.py links --source-dir <clone>` | — | Already written and selftested; repoint only |
| Database reference repair | `firestarter_app/tools/build_db.py` (generator) | Regenerated `chip_database.json` | Generated artifact — never hand-edited (D-14, project convention, both devtest skills) |
| Test-suite surgery | `firestarter_app/tests/` | Meta repo (relocated doc legs) | Doc legs lose their oracle; code legs must keep running in app CI |
| Firmware `doc/` deletion | `firestarter` repo | `firestarter_app/tests/scan_paths.py` + `test_dispatch_mirror.py` | Cross-repo coupling — see H-1 |

---

## Ordering Hazards — get these wrong and an oracle is destroyed irrecoverably

### H-1 (CRITICAL, newly measured): the whole app suite aborts at collection

`tests/test_dispatch_mirror.py:38`:

```python
_PROTOCOLS_MD = fw_path("doc", "PROTOCOLS.md")
```

`fw_path` (`tests/fw_presence.py:117-140`) **raises** when the firmware repo marker exists but the
target does not:

```python
resolved = FW_ROOT.joinpath(*parts)
if FW_REPO_PRESENT and not resolved.exists():
    raise MissingScanTargetError(...)
```

Proven this session, running the real suite against a firmware root with `doc/` removed:

```
tests/test_dispatch_mirror.py:38: in <module>
E   tests.fw_presence.MissingScanTargetError: .../doc/PROTOCOLS.md does not exist, but the firmware repo IS present
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1972 tests collected, 1 error in 1.35s
```

**Zero tests execute.** In app CI this never fires (bare `actions/checkout@v4`, no firmware sibling,
`FW_REPO_PRESENT` is `False`, `fw_path` returns without raising, `requires_fw` skips). It fires in
**the devcontainer** and in **any meta-CI job that materialises both repositories** — which is
precisely what the relocated claim gates require.

**Constraint:** `test_dispatch_mirror.py:38` and `tests/scan_paths.py:113` must be repaired **in the
same commit as, or before,** the firmware `doc/` deletion. Not after. `[VERIFIED: pytest run, this session]`

### H-2: the HONEST-01 source oracle (D-02)

Record the 12 per-file SHAs into `MIGRATION-TABLE.md` **before** the delete commits. Verified the
read side works today:

```
$ git -C firestarter show HEAD:doc/PROTOCOLS.md | wc -c
49560
```

Once deleted without recorded SHAs the oracle is reconstructible only by guessing which commit was
"immediately before", which D-02 explicitly rejected. `[VERIFIED: git show, this session]`

### H-3: the WIKI-05 demonstrated-RED is free but time-boxed

Criterion 8 requires WIKI-05 be *demonstrated catching an unreferenced page before it is trusted*.
The **live wiki already supplies that RED**, because the current `Home.md` lists the 12 page names
as plain bullets, not links. Proven against the real live `Home.md` plus 12 landed page files:

```
$ python3 tools/wiki/wiki.py links --source-dir <clone+12 pages>
ERROR: orphan page not linked from Home.md: AT28C04-ADAPTER
... (12 lines) ...
RC=1
```

**Run and capture this immediately after pushing the 12 pages and before rewriting `Home.md`.** It
is a real, non-synthetic, first-contact RED — strictly better evidence than a fixture, and it costs
nothing. Rewrite Home first and it is gone. `[VERIFIED: wiki.py links run, this session]`

### H-4: no `gsd/v1.35-*` branch exists in either sub-repo

```
$ git -C firestarter  branch -a --list '*v1.35*'   → (empty)
$ git -C firestarter_app branch -a --list '*v1.35*' → (empty)
$ git -C firestarter      rev-parse --abbrev-ref HEAD  → HEAD   (detached at a218b4f5)
$ git -C firestarter_app  rev-parse --abbrev-ref HEAD  → chore/strip-provenance-comments
```

Phase 167 was meta-only, so 168 is the first v1.35 phase to write into the sub-repos. The task
brief's claim that all three repos are on `gsd/v1.35-documentation-consolidation-wiki-migration` is
**false for both sub-repos right now**. Both branches must be created (project convention: fork off
`beta`) before any sub-repo commit. `[VERIFIED: git branch, this session]`

---

## The Corpus — 12 files, measured

| Repo | File | Lines | `support_status` | `.planning/` refs | `Phase NN` |
|---|---|---:|---:|---:|---:|
| fw | `doc/PROTOCOLS.md` | 556 | 1 | 6 | 23 |
| fw | `doc/SHIELD-REVISIONS.md` | 128 | 0 | 4 | 5 |
| fw | `doc/AT28C04-ADAPTER.md` | 160 | 1 | 1 | 0 |
| app | `doc/beta-testing-install.md` | 213 | 0 | 0 | 0 |
| app | `doc/community-validation.md` | 265 | 11 | 0 | 4 |
| app | `doc/infoic-field-dictionary.md` | 325 | 0 | 0 | 12 |
| app | `doc/lockable-proms.md` | 399 | 0 | 0 | 0 |
| app | `doc/package-details.md` | 70 | 0 | 0 | 0 |
| app | `doc/pinout-safety-review.md` | 88 | 0 | 1 | 5 |
| app | `doc/protocol-flags.md` | 54 | 0 | 0 | 0 |
| app | `doc/protocol-id.md` | 53 | 0 | 0 | 2 |
| app | `doc/sram-nvram-behavior.md` | 114 | 0 | 4 | 1 |
| | **Total migrating** | **2,425** | **13** | **16** | **52** |
| app | `doc/PY32F071-FIRMWARE-INSTALL.md` | 299 | — | — | — | **DEFERRED — not migrated, but still deleted (see below)** |

`[VERIFIED: wc -l / grep -o, this session]`

### Corrections to CONTEXT.md

| CONTEXT.md says | Measured | Command |
|---|---|---|
| `support_status` 12× (D-04) / 13× (ROADMAP crit. 4) | **13 occurrences on 12 lines in 3 files.** `community-validation.md:120` carries two on one line (`support_status = raw_config.get("support_status", "supported")`). Both numbers were right about different units. | `grep -o 'support_status' $MIG \| wc -l` = 13; `grep -h ... \| wc -l` = 12 |
| "6 files, 15 references" of `.planning/` (D-11) | **5 files, 16 references.** `PROTOCOLS.md:20` carries two on one line. | `grep -o '\.planning/' $MIG \| wc -l` |
| "all 41 of them" (`Phase NN`, D-11) | **52** | `grep -oE 'Phase [0-9]+' $MIG \| wc -l` |
| "20 relative-link targets, 2 cross-file" | **3 cross-file `.md` targets, 18 same-page anchors, 37 external** | markdown link regex over the 12 files |
| the 5 test modules total "~1,962 lines" | **2,328** (154+662+268+878+366 — CONTEXT's own listed numbers sum to this) | `wc -l` |
| wiki has "5 commits, 3 pages" | **6 commits**, 3 pages | `git log --oneline` on the clone |

### The three cross-file links to rewrite

```
beta-testing-install.md → community-validation.md
package-details.md      → infoic-field-dictionary.md#protect-flags-bits-14-15
protocol-flags.md       → infoic-field-dictionary.md#protect-flags-bits-14-15
```

`wiki.py`'s `_LEGAL_TARGET_RE` is `[A-Za-z0-9][A-Za-z0-9-]*(?:#[A-Za-z0-9_-]*)?` (`wiki.py:52`) —
a `.md` suffix is rejected. Correct rewrite form: `[Text](Infoic-Field-Dictionary#protect-flags-bits-14-15)`.
The 18 same-page anchors are unaffected. `[VERIFIED: wiki.py source + regex, this session]`

### `PY32F071-FIRMWARE-INSTALL.md` — deferred but still deleted

MIGRATE-02 says `firestarter_app/doc/` must not exist. The deferred file therefore **is deleted
without being migrated**. CONTEXT.md never states this consequence, and it is the reason
`tests/test_py32_packaging.py` loses 5 legs (§MIGRATE-03). The planner must record the deletion as a
deliberate content loss with the D-19/MIGRATION-TABLE deferral note as its justification, and should
record the pre-deletion SHA for it too so the content is recoverable.

---

## Page-Name Resolution — the two hyphen hazards

Hard constraints, read out of the code rather than assumed:

- `render_title(stem) = stem.replace("-", " ")` (`wiki.py:60-61`). There is **no** way to render a
  literal hyphen in a title. `AT28C04-ADAPTER` renders as `AT28C04 ADAPTER`.
- `check_page_names` (`wiki.py:141-166`) rejects `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`, `..`,
  any non-`.md` suffix, and any subdirectory. So `SRAM/NVRAM` cannot be a filename.
- `_LEGAL_TARGET_RE` restricts a linkable stem to `[A-Za-z0-9][A-Za-z0-9-]*` — **no underscores, no
  dots**. Any stem outside that alphabet is unreachable by the only legal internal link form.
- `check_link_forms` (`wiki.py:169-207`) rejects a case-mismatched link with a distinct message,
  noting GitHub resolves case-insensitively and will never report it. So page-name case must be
  chosen once and used exactly.
- `MIGRATION-TABLE.md:41-55` forbids the U+2010 look-alike workaround.

Consequence: both hazards must be resolved by **rewording the title**, and the reworded title must
be spelled with an alphabet of `[A-Za-z0-9-]` only. This is a naming decision for the planner, not a
technical unknown. `[VERIFIED: wiki.py source, this session]`

---

## MIGRATE-03 on the CI Python Floor

### The floor, and how to reach it in this devcontainer

App CI is `actions/checkout@v4` (bare) + `actions/setup-python` **3.11** + `pip install -e .[test]`
+ `ruff check` + `ruff format --check` + `python tools/check_mypy_watermark.py` +
`pytest tests/ --cov=firestarter --cov-report=term-missing --cov-fail-under=70` +
`pip install -e . && firestarter --help` (`.github/workflows/ci.yml:48-96`). The devcontainer's
system Python is **3.12.14**, which has provably masked app CI breakage before.

Known-good route, run and verified this session:

```bash
export UV_CACHE_DIR=<writable-scratch>/uvcache     # ~/.cache/uv is NOT writable here
uv venv --python 3.11 <scratch>/venv311            # resolves CPython 3.11.16
VIRTUAL_ENV=<scratch>/venv311 uv pip install -e '.[test]'
export FIRESTARTER_CONFIG_DIR=<scratch>/fsconfig   # app leaks into ~/.firestarter regardless
<scratch>/venv311/bin/python -m pytest tests/ -o addopts="" -q
```

Two traps confirmed:
- `uv` fails outright without `UV_CACHE_DIR` — `failed to create directory /home/vscode/.cache/uv: Permission denied`.
- `uv venv` creates a venv **without pip**; `python -m pip` fails. Use `uv pip install`.
- `pyproject.toml:100` sets `addopts = "-ra -q"`; doubling `-q` suppresses the count line. Use
  `-o addopts=""`.
`[VERIFIED: commands run, this session]`

### Baseline, measured

| Environment | Result | Time |
|---|---|---|
| py3.11, real tree, firmware sibling **present** | **1976 passed, 0 failed, 0 skipped** | 287.6 s |
| py3.11, tree with `doc/` removed, no firmware sibling (**= app CI shape**) | 1888 passed, **19 failed**, 69 skipped | 307.6 s |

`[VERIFIED: pytest runs, this session]`

Of the 19, **2 are artifacts of the scratch-tree layout** (`test_gen_validation_header::test_validate_spec_called_before_emission`
and `test_sdp_bus_config_drift::test_bad_pinout_fails_closed_and_writes_nothing` resolve a sibling
`../firestarter_app/firestarter/data/pinouts.json`). **17 are genuine doc-caused failures.**

### The exact doc-leg / code-leg split

| Module | Lines | Legs | Doc legs (fail on deletion) | Legs that stay |
|---|---:|---:|---:|---:|
| `test_lockable_proms_doc_claims.py` | 154 | 4 | **3** | 1 (`test_no_wrong_blanket_shorthand_elsewhere_in_tree` — a tree-wide rglob, independent of `doc/`) |
| `test_protect_flags_doc_measurements.py` | 662 | 10 | **6** | 4 |
| `test_protection_table_citations.py` | 268 | 6 | **2** | 4 |
| `test_lock_status_class_partition.py` | 878 | 18 | **1** | 17 |
| `test_dispatch_mirror.py` | 366 | 4 | **4** (all — module-scope raise, H-1) | 0 |
| `test_py32_packaging.py` **← CONTEXT.md missed this module** | 350 | 12 | **5** | 7 |
| **Total** | **2,678** | **54** | **21** | **33** |

Named failing legs (from the real run):

```
test_lock_status_class_partition.py::test_every_readable_token_has_a_citation_that_resolves_in_the_doc
test_lockable_proms_doc_claims.py::test_section_17_states_at28c64b_at28c256_are_sdp_capable
test_lockable_proms_doc_claims.py::test_section_17_states_at28c16_and_plain_at28c64_are_not_sdp_capable
test_lockable_proms_doc_claims.py::test_no_wrong_blanket_shorthand_anywhere_in_doc
test_protect_flags_doc_measurements.py::test_doc_protect_on_after_figures_match_recomputed_db
test_protect_flags_doc_measurements.py::test_doc_protect_off_before_figures_match_recomputed_db
test_protect_flags_doc_measurements.py::test_doc_both_keys_count_matches_recomputed_db
test_protect_flags_doc_measurements.py::test_algorithm_13_promotion_split_matches_doc
test_protect_flags_doc_measurements.py::test_algorithm_6_correlation_is_stated_as_suggestive_not_derivable
test_protect_flags_doc_measurements.py::test_documented_once_one_heading_two_pointers_no_restated_figures
test_protection_table_citations.py::test_every_quoted_citation_fragment_resolves_in_the_doc
test_protection_table_citations.py::test_citation_resolution_non_vacuity_control
test_py32_packaging.py::test_install_doc_is_non_vacuous
test_py32_packaging.py::test_install_doc_app_region_end_matches_host_constant
test_py32_packaging.py::test_install_doc_flash_base_matches_host_constant
test_py32_packaging.py::test_install_doc_documents_all_three_readback_outcomes
test_py32_packaging.py::test_install_doc_pyusb_floor_matches_pyproject
```

Plus, when the firmware repo is present: `test_scan_paths_resolve.py::test_all_cross_repo_paths_resolve`
(assertion failure naming `doc/PROTOCOLS.md`), and `test_dispatch_mirror.py`'s 4 legs via H-1.

### **CONTEXT.md's "module-scope resolution breaks import" claim is wrong for 5 of the 6 modules**

Every `_DOC_FILE = _FA_DIR / "doc" / "…"` (`test_lockable_proms_doc_claims.py:48`,
`test_protection_table_citations.py:33`, `test_lock_status_class_partition.py:81`,
`test_protect_flags_doc_measurements.py:47-49`, `test_py32_packaging.py:55`) is a pure
`pathlib.Path` construction — **no filesystem access**. `read_text()` happens inside test bodies.
Import is unaffected; only the assertions go red. **The one exception is
`test_dispatch_mirror.py:38`**, and it is the exception because of `fw_path`, not because of path
construction. This makes a partial move *much* safer than CONTEXT.md prices — except for that one
module, which is catastrophic (H-1).

### `test_dispatch_mirror.py` is GREEN today

CONTEXT.md prices it as "may come back RED on its first real run". Measured against the current
firmware gitlink (`a218b4f5`):

```
tests/test_dispatch_mirror.py::test_dispatch_mirror_doc_matches_tool PASSED
tests/test_dispatch_mirror.py::test_dispatch_mirror_firmware_leg_enumerates_all_protocols PASSED
tests/test_dispatch_mirror.py::test_planted_missing_hex_is_detected PASSED
tests/test_dispatch_mirror.py::test_planted_comment_only_hex_is_NOT_detected PASSED
4 passed in 0.11s
```

Its `§0` parse yields exactly 12 rows, matching the 12 algorithm values in the database:

```
0x5→flash_5v_page.cpp  0x6→flash_nor_unlock.cpp  0x7→eprom.cpp  0x8→eprom.cpp
0xb→eprom.cpp  0xd→eeprom_28c.cpp  0xe→sram.cpp  0x10→flash_intel.cpp
0x27→sram.cpp  0x28→sram.cpp  0x29→sram.cpp  0x34→not_implemented.cpp
```

**What the parser needs to survive:** `_BUCKET_ROW_RE` (`test_dispatch_mirror.py:72-75`) demands a
**7-column** pipe row starting `| 0xNN |`, reading col 1 (hex), col 6 (handler family, first
whitespace token) and col 7 (`phantom?`). `_FAMILY_ROW_RE` (`:77-80`) demands a **4-column** row
`| <family> | \`configure_*()\` | \`<file>.cpp\` | …`. Any column reorder, reflow, or table
reformat during migration silently changes the parse. This is a *table-shape* dependency, not a
content one — and it is the strongest argument for migrating `PROTOCOLS.md` §0 verbatim, editing
only prose around it. `[VERIFIED: pytest -v + direct parser invocation, this session]`

### Packaging — the premise is false

| Artifact | `doc/` entries | How obtained |
|---|---:|---|
| `firestarter_app/firestarter.egg-info/SOURCES.txt` (working tree) | 3 (`:28-30`) | pre-existing, **gitignored**, dated 2026-08-29 |
| sdist built from a clean `git archive HEAD` tree | **0** | `python -m build --sdist --no-isolation` |
| published `firestarter-3.0.0b34.tar.gz` on PyPI (174 entries) | **0** | downloaded from PyPI |
| published `firestarter-3.0.0b33.tar.gz` on PyPI (174 entries) | **0** | downloaded from PyPI |
| published `firestarter-2.0.7.tar.gz` on PyPI (58 entries) — legacy | 2 | downloaded from PyPI |

The stale working-tree `SOURCES.txt` (205 lines) additionally lists `.gitignore`, `CLAUDE.md`,
`.github/workflows/*`, `.planning/codebase/*.md`, `datasheets/*.pdf`, `tools/*.py`, `tests/*` —
**39 entries a clean build (166 lines) does not produce**. It is an accumulated artifact of a
historic build environment, not a description of what ships.

`MANIFEST.in` does not mention `doc/` at all. `pyproject.toml` declares
`packages = ["firestarter"]` and `package-data` limited to three JSON files under
`firestarter/data/`. Deleting `doc/` changes the sdist by nothing.

**Plan implication:** MIGRATE-03's verification is still required (build + install + full suite on
3.11), but the sdist delta must be **reported as zero, explicitly**, alongside the corrected record
that `SOURCES.txt:28-30` was a stale artifact. Reporting "3 files left the sdist" would be a false
claim in the phase's own honesty milestone. `[VERIFIED: python -m build ×2, PyPI downloads]`

---

## Repair Surface — MIGRATE-04 / criterion 2, complete measured inventory

Sweep commands (record these in the plan so the verification is reproducible):

```bash
git -C firestarter     grep -n -E '\bdoc/[A-Za-z0-9_.-]+\.md|/doc/|"doc"' -- . | grep -v '^doc/'
git -C firestarter_app grep -n -E '\bdoc/[A-Za-z0-9_.-]+\.md|"doc"'        -- . | grep -v '^doc/'
git -C /workspaces     grep -n -E '(firestarter(_app)?/)?doc/[A-Za-z0-9_.-]+\.md' -- . ':!.planning'
```

**Totals: 30 files, 79 reference lines** (app 23 files / 66 lines; fw 7 files / 13 lines), plus
**5 intra-corpus lines inside the migrating documents themselves**, plus meta's
`.planning/v1.35/MIGRATION-TABLE.md` (13 lines, which are *supposed* to be there).
CONTEXT.md's "52 lines across 27 files (app 40 / fw 12)" used a narrower pattern.

### (a) Repair here

**Firmware repo (`firestarter`)**

| File:line | Content | Disposition |
|---|---|---|
| `CLAUDE.md:37` | "Source of truth for the name set: `firestarter/doc/PROTOCOLS.md`" | repoint to page title (D-13) |
| `CLAUDE.md:60` | "source of truth `firestarter/doc/PROTOCOLS.md`" | repoint |
| `CLAUDE.md:114` | "See `doc/PROTOCOLS.md` §1.6" | repoint |
| `CLAUDE.md:204` | **the lockstep rule** vs `firestarter/doc/SHIELD-REVISIONS.md` §§1/6/7/9 | **D-16 — must survive, repointed** |
| `CLAUDE.md:206` | **the §4 ADC-band lockstep rule** vs `doc/SHIELD-REVISIONS.md` | **D-16 — second lockstep rule CONTEXT.md did not name separately** |
| `README.md:127,137,144` | 3 markdown links `[\`doc/…\`](./doc/…)` | full wiki URLs (D-13/D-17) |
| `include/proto_constants.h:14` | `// truth: firestarter/doc/PROTOCOLS.md (operator-approved, commit 6e7bd38).` | **delete the whole comment block :11-16** (D-15 + no-comments rule) |
| `test/native/avr/test_loop_eprom_v131/test_loop_eprom_v131.cpp:1755` | C++ comment citing `doc/SHIELD-REVISIONS.md` | **⚠ NOT in CONTEXT.md's repair list NOR its D-18 exclusion list.** Needs a decision. Recommended: delete under the same reasoning as D-15 (a comment in product source, citing a path that stops existing). |

**Host app repo (`firestarter_app`)**

| File:line | Content | Disposition |
|---|---|---|
| `CLAUDE.md:46` | `doc/PY32F071-FIRMWARE-INSTALL.md` (the **deferred** file) | rewrite — the file is being deleted, not published |
| `CLAUDE.md:112` | `firestarter/doc/SHIELD-REVISIONS.md` lockstep rule (mirror of fw `CLAUDE.md:204`) | **D-16 applies here too — CONTEXT.md only named the firmware side** |
| `README.md:178,755` | 2 links | full wiki URLs (D-17) |
| `firestarter/diagnostic_report.py:256` | comment citing `doc/community-validation.md` | delete (no-comments rule) |
| `firestarter/firmware.py:629` | user-visible message: "see `doc/PY32F071-FIRMWARE-INSTALL.md` for…" | **runtime output** — must not name a deleted file |
| `firestarter/ic_layout.py:461` | comment citing `firestarter/doc/PROTOCOLS.md` | delete |
| `firestarter/protection_readability.py:11` | module docstring: "The source is `doc/lockable-proms.md`" | repoint to page title (docstring, not a comment) |
| `firestarter/py32_dfu.py:27` | module docstring pointer | rewrite |
| `firestarter/py32_dfu.py:605` | **user-visible error string** "(see doc/PY32F071-FIRMWARE-INSTALL.md)" | must not name a deleted file |
| `tools/check_protection_readability_invariants.py:21` | docstring citing `doc/lockable-proms.md` | repoint |
| `tools/diff_db.py:250` | `[CITED: doc/infoic-field-dictionary.md …]` inside an **emitted report string** | operator-visible — repoint to page title |
| `tests/scan_paths.py:113` | `ScanPathEntry("doc/PROTOCOLS.md", ("test_dispatch_mirror.py",))` | **remove entry (H-1).** Floor is `_FLOOR = 6` (`test_scan_paths_resolve.py:47`); 8 → 7 entries stays legal |
| `tests/test_dispatch_mirror.py:5,37,38` | module docstring + module-scope `fw_path("doc",…)` | **H-1 — repair before or with the fw delete** |
| `tests/test_diagnostic_report.py:844` | comment | delete |
| `tests/test_fw_presence.py:219` | asserts `_FIXTURE_DIR/"doc"/"PROTOCOLS.md"` exists | fixture-tree assertion — see below |
| `tests/fixtures/fake_firestarter/README.md:15,75` | fixture description naming `doc/PROTOCOLS.md` | see below |
| `tests/fixtures/fake_firestarter/doc/PROTOCOLS.md:5` | the fixture stub file **itself lives at a `doc/` path** | see below |
| `tests/test_lockable_proms_doc_claims.py` (11 lines), `test_protect_flags_doc_measurements.py` (10), `test_protection_table_citations.py` (3), `test_lock_status_class_partition.py` (2), `test_py32_packaging.py` (1) | doc-leg constants and assertion messages | move with the legs |

> **The `fake_firestarter` fixture (3 files, 4 lines) is a genuine open question CONTEXT.md never
> raised.** It is a stand-in firmware tree *inside the app repo* whose whole purpose is to mirror
> the real firmware layout, including a `doc/PROTOCOLS.md` stub. It is not under
> `firestarter_app/doc/`, so MIGRATE-02 does not force its removal; but criterion 2's "no file in
> either repository links to a path beneath them" arguably reaches it. Recommended: **rekey the
> fixture onto a scan target that survives** (e.g. `include/firestarter.h`, already in the fixture
> per `test_fw_presence.py:218`) and delete the `doc/` stub, since keeping a fixture that models a
> layout the real repo no longer has is itself a drift hazard.

**Intra-corpus (must be rewritten during migration, not after)**

`infoic-field-dictionary.md:146`, `package-details.md:7`, `protocol-flags.md:7`,
`protocol-id.md:7`, `protocol-id.md:22` — these reference sibling `doc/` files from *inside* the
migrating documents. `protocol-id.md:22` cites `firestarter/doc/PROTOCOLS.md` §1.6 across repos.

**Meta repo**

`.planning/v1.35/MIGRATION-TABLE.md:13-24` carries the 12 source paths **by design** (D-02/D-13,
Backlog 999.9 sweep target) — keep. But `MIGRATION-TABLE.md:3-7` states "The publish path derives a
page's name mechanically… `wiki.py publish` does not read this table, and never will" — **false
after D-20 deletes `publish`**. Repair the prose, keep the table.

### (b) Generator-fix-and-regenerate (D-14)

| File | Occurrences | Action |
|---|---:|---|
| `firestarter_app/tools/build_db.py:543` | 1 (a `#` comment: "The DIP24→DIP32 remap lives in firestarter/doc/AT28C04-ADAPTER.md.") | **delete the comment** (no-comments rule) |
| `firestarter_app/tools/build_db.py:569` | 1 (the emitted `unsupported_reason` string) | edit the emitted text to name the wiki page |
| `firestarter_app/firestarter/data/chip_database.json` | **9** rows | regenerate — never hand-edit |
| `firestarter_app/tools/baseline/chip_database.baseline.json` | **9** rows | see the measurement below |

**Regeneration is deterministic and safe — measured.** `build_db.py` takes no CLI arguments, fetches
`infoic.xml` over HTTPS from a **pinned GitLab commit** (`build_db.py:17-20`,
`a8efaedc236c1d9718bd28299dfbb99536b010ff`), needs `requests`, and writes `OUTPUT_FILE`
unconditionally. Run against a clean checkout of `HEAD` this session:

```
Done! 744 upstream chips processed + 2 non-upstream supplement chip(s) = 746 total.
$ cmp <regenerated> <committed>  → IDENTICAL
```

So the regenerate step is a byte-for-byte round trip today. **Requires network access to
gitlab.com.** `[VERIFIED: build_db.py run + cmp, this session]`

**The re-baseline step is probably unnecessary, and doing it is riskier than not.** Measured by
mutating the 9 reason strings in a scratch DB and running the real gate against the real baseline:

```
$ FIRESTARTER_DB_FILE=<mutated> python tools/diff_db.py
PASS: all 744 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)
RC=0
```

`diff_db.py` is indifferent to `unsupported_reason` text. No test asserts the literal path (only the
`"adapter required:"` prefix and non-emptiness — `test_build_db_inclusion.py:539`), and no syrupy
snapshot pins it. The baseline is consumed by six modules (`test_page_size_invariants.py:63`,
`test_diff_db_gate.py`, `test_chip_database_field_inventory.py`,
`test_variant_decode_evidence_stability.py:62`, `test_vcc_margin_rail.py:55`, `tools/diff_db.py:39`)
and was last re-anchored at Phase 98 (`362bfa0`, 2026-06-30). **Recommendation: do not re-baseline.**
The baseline is a pinned historical snapshot; its 9 copies of the path are historical evidence,
which is exactly D-18's own reasoning. Re-anchoring it is the kind of move this project has already
learned reddens unrelated legs. `[VERIFIED: diff_db.py mutation test, this session]`

### (c) Explicitly excluded — historical records (D-18), stated with reason

| File:line | Why excluded |
|---|---|
| `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md:637` | a recorded RED-baseline file listing; records what was true when written |
| `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md:145` | a scope statement about `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` being out of scope for its phase |
| `firestarter/tests/golden/eprom_params_citations.json:22` | contains a sentence *about* `doc/PROTOCOLS.md` citing paths that did not resolve — repairing it destroys the evidence |
| `firestarter_app/.planning/codebase/STRUCTURE.md:40` | a directory-tree diagram. **⚠ Tension worth naming:** `.planning/codebase/` is a *live* codebase map, not an archive, and it will be factually wrong after this phase. Recommend excluding from the *link* repair (it is not a link) but correcting the tree line, or stating explicitly why not. |
| `.planning/` in the meta repo — **415 files** match | historical-by-intent; out of scope by standing project rule |

---

## The Claim Vocabulary — D-01's checker, made concrete

### `support_status` family (family (a))

Complete, exhaustive: **13 occurrences, 12 lines, 3 files.**

| Value | Count | Sites |
|---|---:|---|
| `adapter-required` | 4 | `AT28C04-ADAPTER.md:12,23,52,58` |
| `protocol-not-implemented` | 1 | `PROTOCOLS.md:458` |
| `vpp-exceeds-max` | **0** | — |
| `UNVERIFIED` | **0** | — |
| `PROTOCOL-LEDGER` | **0** | — |

**Path correction:** `PROTOCOL-LEDGER.json` is at **`.planning/v1.16/ledger/PROTOCOL-LEDGER.json`**,
not `.planning/PROTOCOL-LEDGER.json` as CONTEXT.md and REQUIREMENTS.md both state. It exists, it
holds `schema_version: 1`, `milestone: v1.16`, `generated: 2026-06-26`, and **7 `UNVERIFIED`
occurrences**; last touched `7d428944` (2026-07-01, `fix(99-04)`). None of the 12 migrating
documents cites it — so the requirement's ledger half is vacuous **from the corpus side**, which
must be stated that way. `[VERIFIED: find + json load + git log, this session]`

### Negative-capability family (family (b)) — D-01's own list is partly vacuous too

| D-01 token | Occurrences across the 12 files |
|---|---:|
| `cannot` | 12 |
| `do not` | 11 |
| `never` | 31 |
| `unsupported` | 2 |
| `not implemented` | 1 |
| `requires an adapter` | **0** |
| `unverified` | **0** |
| `at your own risk` | **0** |
| stated voltage ceilings (`max/ceiling/exceeds/up to … N V`) | **1** (`SHIELD-REVISIONS.md:103` "up to +5V") |

Adjacent tokens D-01 did not name but which carry real force in this corpus:
`does not` 17, `warning` 14, `no VPP` 7, `must not` 4, `will not` 2.

Per-file totals for the live tokens (this is the multiset the checker compares):

| File | cannot | do not | does not | never | must not | unsupported | not impl |
|---|---:|---:|---:|---:|---:|---:|---:|
| PROTOCOLS.md | 2 | 4 | 4 | 3 | 1 | 0 | 1 |
| SHIELD-REVISIONS.md | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| AT28C04-ADAPTER.md | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| beta-testing-install.md | 0 | 0 | 3 | 2 | 0 | 0 | 0 |
| community-validation.md | 3 | 1 | 3 | 16 | 0 | 2 | 0 |
| infoic-field-dictionary.md | 1 | 2 | 2 | 5 | 0 | 0 | 0 |
| lockable-proms.md | 2 | 4 | 1 | 1 | 0 | 0 | 0 |
| package-details.md | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| pinout-safety-review.md | 0 | 0 | 1 | 1 | 0 | 0 | 0 |
| protocol-flags.md | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| protocol-id.md | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| sram-nvram-behavior.md | 1 | 0 | 1 | 2 | 0 | 0 | 0 |

`[VERIFIED: grep -oi per token per file, this session]`

### Recommended vocabulary data-file shape and algorithm

D-01 requires the vocabulary be **checked in as data**. Concrete shape (JSON, stdlib-parseable, no
dependency):

```json
{
  "schema_version": 1,
  "families": {
    "support_status": {
      "match": "literal",
      "case_sensitive": true,
      "tokens": ["adapter-required", "protocol-not-implemented", "vpp-exceeds-max"]
    },
    "negative_capability": {
      "match": "literal",
      "case_sensitive": false,
      "tokens": ["cannot", "do not", "does not", "never", "must not", "will not",
                 "unsupported", "not implemented", "no VPP", "warning",
                 "requires an adapter", "unverified", "at your own risk"]
    },
    "voltage_ceiling": { "match": "regex", "tokens": ["(?i)(max(imum)?|ceiling|exceeds?|up to|no more than|limited to)[^.]{0,40}[0-9]+(\\.[0-9]+)?\\s?V"] }
  },
  "expected_zero": ["vpp-exceeds-max", "UNVERIFIED", "PROTOCOL-LEDGER",
                    "requires an adapter", "unverified", "at your own risk"]
}
```

**Algorithm (per source file → destination page pair):**

1. Read the source side with `git -C <subrepo> show <sha>:doc/<file>` (D-02 SHA from
   `MIGRATION-TABLE.md`). Read the destination side from the wiki clone at its mapped page name.
2. Normalise both identically before counting: strip fenced code blocks and inline code spans
   (reuse `wiki.py:109-115`'s `strip_code_spans`), collapse whitespace runs to a single space,
   lowercase for case-insensitive families only.
3. Count occurrences per token per family → two `collections.Counter`s.
4. Compare. **Report three buckets separately, never as one verdict:**
   - **DROPPED** — `source[t] > dest[t]`. This is the failure D-03 exists to catch. Exit 1.
   - **ADDED** — `dest[t] > source[t]`. Report, do not fail: adding a hedge is not upgrading a claim.
   - **ZERO/ZERO** — any token in `expected_zero` present 0 times on both sides. **Print explicitly
     as "0 of 0 — VACUOUS, not checked"** (D-04). Never fold into the PASS line.
5. Preserving *force* across the title/link/GSD-framing rewrites: because step 2 strips code spans
   and the token set is prose-level, a heading rename or a link rewrite moves **zero** tokens
   (verified: all three cross-file links and all 16 `.planning/` paths sit inside backticks or link
   syntax, and none contains a family token). The one real interaction is D-11's deletion of the two
   `Full audit trail:` lines and the three `[CITED: …]` markers — none of which carries a family
   token either. So the multiset is genuinely invariant under the intended edits.
6. **The demonstrated-RED (D-03):** re-run step 4 against a deliberately weakened copy of one page —
   e.g. `AT28C04-ADAPTER.md` with one `adapter-required` softened to "may need an adapter" — and
   capture the DROPPED report. Commit that output as evidence before believing any green.

---

## HONEST-02 Truth Sources

### The database, measured

| Property | Value |
|---|---|
| Path | `firestarter_app/firestarter/data/chip_database.json` |
| Size | 431,835 bytes, 16,565 lines |
| sha256 (full) | `0cfd3a83e881bfcc5011832940823ed70bf120e34cc9b9a504f9b77f66d5e9c9` |
| **sha256 truncated-16 (D-08's stamp)** | **`0cfd3a83e881bfcc`** — unchanged since discussion ✓ |
| Shape | vendor-keyed object, 59 vendor keys → list of chip records |
| Rows | 746 |
| Distinct `part_number` | 677 (part numbers repeat across vendors) |
| **Version field** | **none, anywhere** — confirmed. D-08 stands. |
| Every row has | `part_number`, `support_status`, `programming`, `pinout`, `electrical` |
| `unsupported_reason` | 10 rows (9 `adapter-required` carrying the doc path, 1 `protocol-not-implemented` for `X88C64P,X88C64S`) |

Distinct `programming.algorithm` values (the **only** 12 that exist):

```
int : 5, 6, 7, 8, 11, 13, 14, 16, 39, 40, 41, 52
hex : 0x05 0x06 0x07 0x08 0x0B 0x0D 0x0E 0x10 0x27 0x28 0x29 0x34
counts: 27, 190, 170, 127, 32, 84, 20, 39, 2, 34, 20, 1
```

**Known trap (carry forward):** `algorithm: 13` (`0x0D`) rows are *promoted* rows — a promoted row's
`programming.*` sub-fields belong to another algorithm. A checker that reads `programming.*` off an
`0x0D` row and asserts anything about it will be wrong for a reason no test message will explain.
`[VERIFIED: json analysis, this session; corroborated by project memory]`

**"Does not resolve" definitions:**
- part-number token: `token.upper() not in {r["part_number"].upper() for all rows}`
- algorithm token: `int(token, 16) not in {5,6,7,8,11,13,14,16,39,40,41,52}`

### ⚠ D-09 leg 2 is falsified as a free-text scrape

Measured resolve rates over the 12 files (part-number-shaped tokens vs the 677 known part numbers;
`0xNN` tokens vs the 12 known algorithm values):

| File | PN tokens | resolve | `0xNN` tokens | resolve as algorithm |
|---|---:|---:|---:|---:|
| PROTOCOLS.md | 67 | 14 | 32 | 12 |
| SHIELD-REVISIONS.md | 10 | **0** | 20 | 11 |
| AT28C04-ADAPTER.md | 12 | 5 | 1 | 1 |
| beta-testing-install.md | 2 | 0 | 0 | 0 |
| community-validation.md | 2 | 0 | 5 | 5 |
| infoic-field-dictionary.md | 26 | 10 | 46 | 11 |
| lockable-proms.md | 67 | **5** | 0 | 0 |
| package-details.md | 0 | 0 | 7 | **1** |
| pinout-safety-review.md | 8 | 1 | 4 | 4 |
| protocol-flags.md | 0 | 0 | 4 | 3 |
| protocol-id.md | 4 | 2 | 18 | 11 |
| sram-nvram-behavior.md | 7 | 0 | 5 | 4 |

Tightening to bold-cell part tokens on `lockable-proms.md`: **209 candidates, 7 resolve — 3%.**
Sample of the non-resolving 202: `AT49LHxxx`, `28FXXXP30`, `28F008SA`, `28F160B3`, `HC256`,
`28C256`, `010A`, `04X`. These are **family wildcards, elided suffixes and correct vendor-agnostic
family names** — `protection_readability.py:25-28` documents exactly this: *"the document writes
families in elided shorthand (`Am29F010 / F010B`), where a bare suffix continues the row's shared
stem rather than naming an independent part."*

Two independent failure modes, both fatal:

- **False RED at scale.** A "every part number must resolve" gate on `lockable-proms.md` is red on
  ~200 correct statements. A gate that is red for innocent reasons gets ignored — the exact
  `catalog-sync-check.yml` outcome D-01 argues against, reproduced in the sibling checker.
- **False GREEN by coincidence.** `SHIELD-REVISIONS.md` has **0 part numbers in the database** yet
  **11 of its 20 `0xNN` tokens "resolve as algorithms"** — those tokens are ADC-band and
  control-register values that happen to be numerically equal to algorithm ints. A page with no
  chip claims at all would report an 11-of-20 algorithm pass. The `0xNN` notation is polysemous in
  this corpus (algorithm IDs, minipro `IC2_ALG_*` protocol IDs, flag bits, control-register bits,
  ADC bands, addresses) and is not self-identifying.

**Recommended shape for D-09 leg 2 (revising D-09 on evidence, as its own clause permits):** scope
the resolve check to an **explicitly delimited claim region** on the page — e.g. tokens inside a
fenced block or table marked by an HTML comment sentinel the stamp names — or to a **checked-in
allowlist**, the same "vocabulary as data" pattern D-01 already establishes. Every part-shaped token
outside the delimited region is out of scope by construction; every one inside must resolve or
appear in the allowlist with a reason. Legs 1 (stamp present) and 3 (stamp hash matches) are
unaffected and are already implementable exactly as D-09 states them.
`[VERIFIED: token extraction + resolve measurement, this session]`

---

## Wiki Push and Clone Mechanics

### Clone — answered, no token required

```
$ git clone https://github.com/henols/firestarter_prom.wiki.git
$ git log --oneline
0155a85 Publish wiki from in-repo source
060ff3c Publish wiki from in-repo source
0798b51 Manual test edit (167-06 Step G, to be overwritten)
c9bdce5 Publish wiki from in-repo source
09e8bc6 Initial Home page
9a8a4b8 Initial Home page
```

**6 commits** (CONTEXT.md said 5), branch `master`, HEAD `0155a854752fa9088743daaedc2f2472223dd713`
(matches `0155a85`). The clone succeeded **anonymously, over HTTPS, with no credentials at all** —
`henols/firestarter_prom` is `PUBLIC` and `hasWikiEnabled: true`. Therefore:

- The HONEST-02 / WIKI-05 workflow needs **no PAT and no `GITHUB_TOKEN`** for its clone. A plain
  `git clone https://github.com/henols/firestarter_prom.wiki.git wiki-clone` step is sufficient.
- `actions/checkout` is **not** usable for a `.wiki.git` — its `repository:` input takes
  `owner/name` and resolves the code repo, not the wiki. Use a plain `git clone` step.
- `permissions: contents: read` remains correct and sufficient (it is what the code checkout needs).

`[VERIFIED: git clone + gh repo view, this session]`

### Push — contested; but D-19 makes it moot

Sources disagree. GitHub's own docs state `GITHUB_TOKEN`'s permissions are limited to the repository
containing the workflow; community guidance says a workflow in the *owning* repository can push to
`<repo>.wiki` with `contents: write`, while marketplace actions and multiple reports recommend a PAT
because the default token "often results in permission failures". **This is unresolved and must not
be asserted either way.**

It does not block: **D-19 makes the push a local, operator-run action**, and `gh` is authenticated
here as `henols` with `repo` + `workflow` scopes, so the local push works via
`https://x-access-token:$(gh auth token)@github.com/henols/firestarter_prom.wiki.git`.
`.github/workflows/wiki-publish.yml:18` already encodes the hedge
(`secrets.WIKI_PUSH_TOKEN || secrets.GITHUB_TOKEN`) — and that workflow is being deleted anyway
(D-20). `[CITED: docs.github.com/en/actions/concepts/security/github_token; github.com/orgs/community/discussions/56893]`

### The live wiki — the false lines, quoted for the rewrite

The live wiki is **byte-identical** to `/workspaces/wiki/` (`diff -r` → no differences), so the
planner may edit in-repo and push, or edit the clone directly.

**`Home.md` (26 lines) — false in 3 places (D-22 confirmed):**

| Line | Text | Why false |
|---:|---|---|
| 5 | "See [How this wiki is published](How-This-Wiki-Is-Published) for how these pages are kept in sync with the source repository, and why you should not edit them here directly." | Nothing syncs. Editing here is now the *only* way to edit. |
| 11-22 | Twelve plain bullets: `PROTOCOLS`, `SHIELD-REVISIONS`, `AT28C04-ADAPTER`, `beta-testing-install`, `community-validation`, `infoic-field-dictionary`, `lockable-proms`, `package-details`, `pinout-safety-review`, `protocol-flags`, `protocol-id`, `sram-nvram-behavior` | Raw source filenames, not page names — **and not links at all**, which is why `wiki.py links` reports all 12 as orphans (H-3). |
| 26 | "This wiki is published from the project's `beta` integration branch, not from a tagged release." | Nothing publishes it from anywhere. |

**`How-This-Wiki-Is-Published.md` (40 lines) — 5 of its 8 sections false (D-21 confirmed):**

| Lines | Section | Verdict |
|---|---|---|
| 5-7 | "The in-repo copy is authoritative" — "Every page on this wiki is authored as a markdown file inside the `firestarter_prom` repository, under a top-level `wiki` directory. That in-repo copy is the single source of truth…" | **FALSE** — and it is the exact statement WIKI-02 now forbids |
| 9-11 | "Edits made here are overwritten" — "Do not edit pages directly through this web interface. An edit made here is overwritten the next time the wiki is published…" | **FALSE** — actively discourages the only supported workflow |
| 13-18 | "Publishing" — documents `wiki.py publish` and `publish --push` | **FALSE after D-20** deletes both |
| 20-22 | "How page names are derived" — filename → title, hyphen renders as space, "a page title can never contain a literal hyphen" | **TRUE — keep.** It is also the authoritative statement of the hyphen hazard |
| 24-32 | "Linking between pages" — `[Text](Page-Name)`, rejects `.md`, `[[Page]]`, `[text][ref]`, wrong case | **TRUE — keep**, but line 32's "will fail this wiki's *publishing* check" must become "*link* check" |
| 34-36 | "The sidebar is generated, not written by hand" — "generated automatically by `wiki.py sidebar` … Do not hand-edit it" | **FALSE after D-20**, and it is the exact inverse of D-06's new hand-maintained-sidebar leg |
| 38-40 | "Which branch this wiki tracks" | **FALSE** |

**`_Sidebar.md` (2 lines)** — lists only `Home` and `How This Wiki Is Published`. Becomes the
hand-maintained index D-06's new leg checks.

`[VERIFIED: git clone + cat + diff -r, this session]`

---

## Retiring `tools/wiki/` — exact surgery targets (D-20)

`tools/wiki/wiki.py` — 542 lines, stdlib-only, exit contract documented at `:6-10` (0 = property
holds, 1 = property false, 2 = precondition unmet). `main()` returns 2 when `--source-dir` is not a
directory (`:531-537`) — **that is what fires the moment `wiki/` is deleted with the default intact.**

### Delete

| Symbol | Lines | Note |
|---|---|---|
| `generate_sidebar` | 72-82 | |
| `cmd_sidebar` | 84-106 | |
| `cmd_check` | 252-274 | |
| `_git` | 276-282 | publish-only helper |
| `safe_remote` | 284-286 | publish-only helper |
| `cmd_publish` | 288-421 | |
| `COMMANDS` entries `"sidebar"`, `"check"`, `"publish"` | 423-428 | keep `"links"` |
| `sidebar_parser` block | 461-471 | |
| `check` subparser | 486-495 | |
| `publish_parser` block | 497-521 | incl. `--push`, `--require-wiki` |
| `SIDEBAR_PAGE` | 47 | **only if** the new D-06 leg does not reuse it — it should |
| `DEFAULT_WIKI_REMOTE` 43, `WIKI_BRANCH` 44 | | publish-only |
| imports `difflib`, `shutil`, `subprocess`, `tempfile` | 35-40 | become unused; `ruff` is not run on the meta repo, so this is hygiene not a gate |

### Keep and repoint

| Symbol | Lines | Change |
|---|---|---|
| `DEFAULT_SOURCE_DIR` | 45 | points at `<repo>/wiki`, which this phase deletes → **make `--source-dir` required**, or default it to a conventional clone path. Leaving it is a guaranteed exit-2. |
| `HOME_PAGE`, `NAV_EXCLUDED_PAGES` | 46, 48 | unchanged (D-06: semantics kept) |
| `render_title`, `page_files`, `page_stems` | 60-70 | unchanged |
| `strip_code_spans`, `extract_internal_links` | 109-139 | unchanged — **and reusable by the HONEST-01 checker's normalisation step** |
| `check_page_names` | 141-166 | unchanged |
| `check_link_forms` | 169-207 | unchanged |
| `check_orphans` | 210-228 | unchanged — Home-only reachability |
| `cmd_links` | 231-249 | unchanged |
| `--wiki-remote` on the common parser | 431-448 | now unused by any surviving subcommand; delete or repurpose |

### `selftest.sh` — 12 cases today, all PASS (`OK: selftest complete (12 cases)`, verified)

| Case | Fate under D-20 |
|---|---|
| `stale_sidebar_exit_1` | **delete** (sidebar) |
| `sidebar_deterministic` | **delete** (sidebar) |
| `orphan_exit_1` | keep |
| `sidebar_link_is_not_evidence` | keep — this is the leg proving Home-only reachability |
| `broken_link_exit_1` | keep |
| `md_suffix_link_exit_1` | keep |
| `illegal_filename_exit_1` | keep |
| `wiki_absent_exit_2` | **delete** (publish) |
| `drift_detected_exit_1` | **delete** (publish) |
| `hand_edit_overwritten` | **delete** (publish) |
| `idempotent_head_unchanged` | **delete** (publish) |
| `deleted_page_removed` | **delete** (publish) |

**7 deleted, 5 kept.** Fixture helpers:
- `new_source_dir` (`selftest.sh:17-23`) writes `Home.md`, `Page-One.md`, `_Sidebar.md` — survives,
  and is the base for the D-10 WIKI-05 negative case (add an unreferenced page).
- `new_bare_wiki` (`:25-27`) is `git init --bare --initial-branch=master` — used only by the
  publish cases today, but **survives as the D-10 fixture-clone**: the HONEST-02 negative case needs
  a clonable repo carrying a page that claims an absent part number.
- `rc_of` / `record` / `assert_rc` / `print_evidence_table` (`:29-63`) and the `CASES=(…)` array +
  runner at the tail are the driver shape both new checkers plug into.

**One tension to name:** D-06's new leg ("`_Sidebar.md` lists every page") re-implements part of the
`generate_sidebar` D-20 deletes. They are genuinely different — `sidebar --check` asserts byte
equality against generated content (order- and text-exact, wrong for a hand-maintained file); the
new leg needs **set containment** (`{pages} ⊆ {sidebar entries}`), tolerant of ordering and wording.
Write it as containment; do not resurrect `generate_sidebar`.

### Workflows

- **`.github/workflows/wiki-publish.yml`** — delete (34 lines). Its `WIKI_TOKEN` env
  (`secrets.WIKI_PUSH_TOKEN || secrets.GITHUB_TOKEN`) goes with it.
- **`.github/workflows/wiki-check.yml`** — rewrite. Currently: `pull_request` on `beta` filtered to
  `wiki/**` (a path this phase deletes → the trigger becomes dead), running `wiki.py check` and the
  selftest; plus a `wiki-drift-live` job gated on `workflow_dispatch` running
  `wiki.py publish --require-wiki`. Both `check` and `publish` are being deleted. New shape must be
  `schedule` + `workflow_dispatch`, `permissions: contents: read`, one shared `git clone` of the
  wiki, then two independent checker steps (D-05).

---

## GitHub Actions — do NOT use `submodules: recursive`

CONTEXT.md's `integration_points` says "meta CI gains `submodules: recursive` for the relocated
claim gates." **Three measured reasons that is the wrong mechanism:**

1. **The sub-repos ARE submodules** — `.gitmodules` exists and both are real gitlinks:
   ```
   160000 a218b4f5273d14f0abd796b21ac104792de01603 0  firestarter
   160000 cb189a9b001e9e34fb7651535de339761301d061 0  firestarter_app
   ```
   (Repo-root `CLAUDE.md`'s "Neither sub-repo is committed here" is inaccurate — the gitlinks are.)
   **But a gitlink is a pinned SHA, not a branch.** `submodules: recursive` would check out
   `a218b4f5` (a v1.33-era firmware commit) and `cb189a9b` — **not** the v1.35 branch tips this
   phase writes. The relocated claim gates would assert against stale sub-repo state and could pass
   while the real branches are broken. Note the working tree's app HEAD (`d56424e1`) has already
   drifted from its gitlink (` M firestarter_app` in `git status`), so this is not theoretical.

2. **`.gitmodules` uses SSH URLs** (`git@github.com:henols/…`), which `actions/checkout` must rewrite
   via `insteadOf` to authenticate — one more failure surface for zero benefit.

3. **This repository has already been bitten by exactly this and wrote the record.**
   `.github/workflows/catalog-sync-check.yml:22-29`:

   > *"No `submodules: recursive` here: this job reads only `meta/tools/catalog/messages.toml`, and
   > it checks the sub-repos out explicitly below at the ref it actually wants to compare. Fetching
   > them again as submodules was pure duplicate work — and it re-armed a whole failure class,
   > which is exactly what bit this workflow: an accidentally committed gitlink at
   > `.planning/v1.7/upstream-rurp` with no `.gitmodules` entry made the checkout die with
   > `fatal: No url found for submodule path` before any assertion ran."*

   (That stray gitlink is gone today — `git ls-files -s | awk '$1=="160000"'` returns only the two
   legitimate ones — so `submodules: recursive` would no longer die. The reasoning about pinned
   SHAs stands regardless.)

**Use the established pattern instead:** named `actions/checkout@v4` per repository with
`repository:`, `path:` and a resolved `ref:`, exactly as `catalog-sync-check.yml:53-81` does —
including its "same branch name, else `beta`" resolver
(`git ls-remote --exit-code --heads … "$CAND"`), which encodes the project's per-branch lockstep
rule and the `main`-lags-`beta`-by-~224-commits fact. `[VERIFIED: .gitmodules, git ls-files -s, workflow source]`

### The cautionary record itself

`catalog-sync-check.yml` is the phase's stated warning: *5 runs, 5 failures, 2026-07-11 through
2026-08-18, never once asserted the property it exists to assert.* Its own comment block records
why. Note also the adjacent deferred todo — `sync_to_subrepos.sh` runs `diff -q $X $X` twice, two
verifications that assert nothing. Both are the same defect class this phase's criteria 4, 5 and 8
are written against.

### Workflow shape for D-05/D-10

```yaml
on:
  schedule: [{ cron: '<weekly>' }]
  workflow_dispatch:
permissions:
  contents: read
jobs:
  wiki-truth:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4                 # meta repo
        with: { path: meta }
      - name: Resolve sub-repo ref                # same-branch-else-beta, per catalog-sync-check
        ...
      - uses: actions/checkout@v4                 # app repo, for chip_database.json
        with: { repository: henols/firestarter_app, path: firestarter_app, ref: ... }
      - name: Clone the published wiki            # anonymous; no token needed
        run: git clone --depth 1 https://github.com/henols/firestarter_prom.wiki.git wiki-clone
      - name: HONEST-02 truth check
        run: python3 meta/tools/wiki/<checker>.py --wiki-dir wiki-clone --db firestarter_app/firestarter/data/chip_database.json
      - name: WIKI-05 reachability check
        run: python3 meta/tools/wiki/wiki.py links --source-dir wiki-clone
```

Two steps, one clone, two independently-attributable REDs (D-05). Meta repo has **no** `pyproject.toml`,
`pytest.ini` or `tests/` — D-07 keeps it that way; both checkers are `python3` scripts driven by
`selftest.sh`.

---

## Project Constraints (from CLAUDE.md and operator rules)

| Constraint | Source | Effect on this phase |
|---|---|---|
| **NO comments in product source, at all** — not provenance, not explanatory. Not overridable by a plan. | Operator hard rule | Every repair listed under §(a) that lives in a `#` / `//` comment is a **deletion**, not a repoint: `proto_constants.h:11-16`, `build_db.py:543`, `diagnostic_report.py:256`, `ic_layout.py:461`, `test_diagnostic_report.py:844`, `test_loop_eprom_v131.cpp:1755` |
| Click docstrings are user-facing `--help` text, not comments | Operator rule | A comment sweep must not touch them. Also: **module/function docstrings are not comments** — `protection_readability.py:11`, `py32_dfu.py:27`, `check_protection_readability_invariants.py:21`, `diff_db.py` docstrings get *repointed*, not deleted |
| Meta-repo infrastructure YAML/JSON/shell keeps long rationale comments | `.planning/codebase/CONVENTIONS.md:79-85` | The new workflow and checkers **should** carry a rationale comment explaining what failure they prevent. This does not conflict with the no-comments rule, which is about product source in the two sub-repos. |
| `chip_database.json` is GENERATED — never hand-edit; fix the decode fn | root `CLAUDE.md`, both devtest skills, D-14 | The 9 rows change only via `build_db.py` |
| `constants.py` ↔ `firestarter.h` and `SHIELD-REVISIONS.md` §4 ↔ `rurp_pinout.h` lockstep rules | `firestarter/CLAUDE.md:204,206`; `firestarter_app/CLAUDE.md:112` | D-16 — **three** lockstep statements to preserve, not one |
| Meta repo has no lint/format config; Python is Black-formatted by editor convention | `.planning/codebase/CONVENTIONS.md:87-93` | New `tools/wiki/` scripts should be Black-formatted; nothing enforces it |
| Checkers exit 0/1/2 — 2 distinguishes an operator-gated precondition | `wiki.py:6-10`, D-07 | Both new checkers must honour it |
| `firestarter_app` tracks its own `.planning/codebase/` (8 files) | project memory + `git ls-files` | Never `rm -rf` it |
| STATE.md asserts "**v1.35 touches no product code at all**" | `.planning/STATE.md` "Core value" line | **Now false.** D-14 edits `build_db.py` + regenerates shipped `chip_database.json`; D-15 edits `proto_constants.h`. Flag for correction. |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Markdown link extraction, code-span stripping | A fresh regex in each new checker | `wiki.py:109-139` (`strip_code_spans`, `extract_internal_links`) | Already handles fenced blocks, inline code, `[[Page]]`, reference-style and paren links; already selftested |
| Orphan / reachability detection | A new graph walk | `wiki.py links --source-dir <clone>` (D-06) | 5 surviving selftest cases; Home-only semantics is stricter than WIKI-05 requires, which is correct |
| A fixture proving WIKI-05 catches an orphan | A synthetic wiki | The **live** `Home.md` — it already produces a 12-orphan RED (H-3) | v1.34's rig phase produced ~20 tooling defects that were fixture-green and failed on first hardware contact |
| Test-harness scaffolding in the meta repo | pytest, `pyproject.toml`, `tests/` | `tools/wiki/selftest.sh` + a `python3` script with the 0/1/2 contract (D-07) | The meta repo has none of that and D-07 keeps it that way |
| Re-deriving the pre-deletion document text | A committed snapshot fixture | `git -C <subrepo> show <sha>:doc/<file>` (D-02) | Zero duplication, WIKI-02-clean, exact |
| Editing `chip_database.json` | A `sed` over the JSON | `build_db.py` regenerate (byte-identical round trip verified) | Generated artifact; the project has a standing rule |
| A cron/schedule alternative for wiki edits | PR-triggered gate | `schedule` + `workflow_dispatch` (D-10) | Wiki edits produce no pull request; there is nothing to gate on |

**Key insight:** every piece of tooling this phase needs already exists in `tools/wiki/`, is
already selftested, and needs *repointing* rather than rewriting. The genuinely new code is one
checker (HONEST-02) and one one-shot script (HONEST-01) — both small, both stdlib, both hanging off
`selftest.sh`.

---

## Common Pitfalls

### Pitfall 1: Deleting `firestarter/doc/` before repairing `test_dispatch_mirror.py`
**What goes wrong:** the whole app suite aborts at collection; 0 tests run; every downstream gate in
the phase reports nothing rather than reporting failure.
**Why:** `fw_path` raises at module scope when the firmware repo is present but the target is not.
**How to avoid:** repair `test_dispatch_mirror.py:38` and `scan_paths.py:113` in the same commit as
(or before) the firmware delete. **Warning sign:** `Interrupted: N error during collection` with a
non-zero "tests collected" count.

### Pitfall 2: Believing `SOURCES.txt` about what ships
**What goes wrong:** the phase claims a packaging improvement that never happened.
**Why:** `firestarter.egg-info/` is a gitignored accumulated artifact; setuptools does not prune it.
**How to avoid:** measure with `python -m build --sdist` from a `git archive HEAD` tree, or download
the published sdist. **Warning sign:** `SOURCES.txt` listing `.gitignore`, `.planning/`, `datasheets/`.

### Pitfall 3: A `0xNN` resolve check that passes for the wrong reason
**What goes wrong:** `SHIELD-REVISIONS.md` — a page with zero database chips — reports 11 of 20
algorithm tokens resolving, because ADC-band values collide numerically with algorithm ints.
**How to avoid:** never resolve a `0xNN` token that was not syntactically identified as an algorithm.
**Warning sign:** a resolve rate that looks plausible on a page that makes no chip claims.

### Pitfall 4: Regenerating and then re-baselining `chip_database.baseline.json`
**What goes wrong:** re-anchoring the diff-gate baseline can redden legs across six unrelated
modules for a change `diff_db.py` provably does not care about (verified: RC=0 after mutating all 9
strings).
**How to avoid:** regenerate the DB; leave the baseline alone; state the exclusion with its reason.

### Pitfall 5: Rewriting `Home.md` before capturing the orphan RED
**What goes wrong:** the phase's cheapest and strongest demonstrated-failure evidence for
criterion 8 evaporates, and a synthetic fixture has to stand in for it.
**How to avoid:** push the 12 pages → run `wiki.py links` against the clone → capture the 12-orphan
output → *then* rewrite Home.

### Pitfall 6: Reformatting `PROTOCOLS.md` §0's tables during the move
**What goes wrong:** `test_dispatch_mirror.py`'s two regexes silently stop matching; the doc leg
parses to `{}`; the join yields an empty dict and the comparison may pass vacuously.
**How to avoid:** migrate §0's two tables byte-for-byte. **Warning sign:** `parse_protocols_md()`
returning fewer than 12 rows.

### Pitfall 7: Running the suite on the devcontainer's Python 3.12
**What goes wrong:** app CI breakage is masked — this has provably happened before.
**How to avoid:** `uv venv --python 3.11` with `UV_CACHE_DIR` set; `uv pip install` (the venv has no
pip); `-o addopts=""` to see the count line.

### Pitfall 8: Forgetting that the deferred PY32 file is still deleted
**What goes wrong:** 5 legs of `test_py32_packaging.py` go red, and a module CONTEXT.md never named
goes unaccounted for in the plan's task list.

---

## Runtime State Inventory

This is a migration phase, so the standing question applies: *after every file in the repos is
updated, what state still carries the old paths?*

| Category | Items found | Action required |
|---|---|---|
| **Stored data** | `firestarter_app/firestarter/data/chip_database.json` — 9 rows embed `firestarter/doc/AT28C04-ADAPTER.md` inside `unsupported_reason`, an operator-visible string surfaced by `firestarter info`. `tools/baseline/chip_database.baseline.json` — 9 more. | **Generator edit + regenerate** (D-14). This is a *data migration*, not only a code edit: existing rows carry the string. Baseline: exclude (measured non-blocking). |
| **Live service config** | The **GitHub wiki itself** — 3 live pages whose content exists only in `firestarter_prom.wiki.git`, not in any code repo after D-20. Two of them are publicly false today. | Push the rewrites (D-21/D-22). Nothing in the repos will mirror them afterwards, by design (WIKI-02). |
| **OS-registered state** | None — verified: no scheduler task, pm2 process or systemd unit references `doc/`. `find`/`git grep` over all three repos returns nothing outside the files inventoried above. | none |
| **Secrets / env vars** | `secrets.WIKI_PUSH_TOKEN` (referenced only at `wiki-publish.yml:18`, which is deleted). No evidence it was ever created; the `\|\| secrets.GITHUB_TOKEN` fallback suggests not. | Note in the plan that deleting the workflow orphans the secret name; no repo change needed. |
| **Build artifacts** | `firestarter_app/firestarter.egg-info/` (gitignored, stale, dated 2026-08-29) still lists 3 `doc/` files. `tools/wiki/__pycache__/`. | Cosmetic. The stale egg-info is the direct cause of MIGRATE-03's false premise — the plan should record that, and any MIGRATE-03 verification must build from a clean tree. |
| **Cross-repo pinned state** | Meta's two **gitlinks** (`a218b4f5`, `cb189a9b`) pin sub-repo commits that predate this phase. `git status` already shows ` M firestarter_app`. | The gitlinks must be bumped in the meta repo after the sub-repo work lands, or any submodule-based CI asserts against stale trees (see §GitHub Actions). |

---

## Validation Architecture

This phase's gates **are** its product. Three of the eight criteria (4, 5, 8) demand *observed
failure before a green result is believed*.

### Test Framework

| Property | Value |
|---|---|
| Meta repo | **No test harness at all** — no `pyproject.toml`, no `pytest.ini`, no `tests/`. Validation is `bash tools/wiki/selftest.sh` + the checkers' own 0/1/2 exits (D-07). |
| Host app | pytest 9.1.1 + pytest-cov 7.1.0 + syrupy 6.0.0; config in `pyproject.toml:99-101` (`testpaths=["tests"]`, `addopts="-ra -q"`) |
| Firmware | PlatformIO `pio test -e native`; no `doc/` dependency — verified |
| Quick run (meta) | `bash tools/wiki/selftest.sh` — 12 cases today, **all PASS**, ~3 s |
| Quick run (app, doc modules) | `python -m pytest tests/test_lockable_proms_doc_claims.py tests/test_protection_table_citations.py tests/test_protect_flags_doc_measurements.py tests/test_py32_packaging.py tests/test_dispatch_mirror.py tests/test_scan_paths_resolve.py -o addopts="" -q` — < 5 s |
| Full suite (app, on the floor) | `<venv311>/bin/python -m pytest tests/ -o addopts="" -q` — **1976 tests, 287 s** |
| Full build/install (app) | `python -m build --sdist --no-isolation` then `pip install -e . && firestarter --help` |

### Phase Requirements → Test Map

| Req | Behavior | Type | Automated command | Exists? |
|---|---|---|---|---|
| MIGRATE-01 | 12 pages present and reachable on the live wiki | integration | `git clone …wiki.git && python3 tools/wiki/wiki.py links --source-dir wiki-clone` (asserts 14 pages, all reachable) | ✅ `wiki.py links` |
| MIGRATE-01 | Move is auditable per file | data | `MIGRATION-TABLE.md` has 0 `TBD` cells: `! grep -q TBD .planning/v1.35/MIGRATION-TABLE.md` | ❌ Wave 0 (one-line gate) |
| MIGRATE-02 | Both `doc/` dirs gone | smoke | `! test -d firestarter/doc && ! test -d firestarter_app/doc` | ❌ Wave 0 |
| MIGRATE-03 | Suite green on the CI floor | full suite | `<venv311> -m pytest tests/ -o addopts="" -q` → expect **1976 passed** (fw present) | ✅ exists |
| MIGRATE-03 | Build + install + entry point | integration | `python -m build --sdist --no-isolation && pip install -e . && firestarter --help` | ✅ mirrors `ci.yml:96` |
| MIGRATE-03 | sdist doc-delta **reported**, not assumed | evidence | `tar tzf dist/*.tar.gz \| grep -c 'doc/'` before and after → **0 and 0** | ❌ Wave 0 (report-only) |
| MIGRATE-04 | No dead `doc/` link in either sub-repo | source scan | the three `git grep` sweeps in §Repair Surface, minus the D-18 exclusion list, must return only excluded paths | ❌ Wave 0 |
| HONEST-01 | Claim multiset preserved per page | one-shot checker | `python3 tools/wiki/<honest1>.py --table .planning/v1.35/MIGRATION-TABLE.md --wiki-dir wiki-clone --vocab tools/wiki/claim-vocabulary.json` | ❌ Wave 0 |
| HONEST-01 | **Demonstrated RED** on a weakened claim | negative | same checker against a wiki fixture with one `adapter-required` softened → exit 1, DROPPED bucket non-empty | ❌ Wave 0 |
| HONEST-01 | Vacuous half reported as vacuous | output assertion | checker stdout contains the literal zero-counts for `vpp-exceeds-max`, `UNVERIFIED`, `PROTOCOL-LEDGER` | ❌ Wave 0 |
| HONEST-02 | Stamp present on every claim-bearing page | checker leg 1 | `python3 tools/wiki/<honest2>.py --wiki-dir … --db …` | ❌ Wave 0 |
| HONEST-02 | Delimited claims resolve in the DB | checker leg 2 | same | ❌ Wave 0 |
| HONEST-02 | Stamp hash matches DB → distinct `stale` outcome | checker leg 3 | same | ❌ Wave 0 |
| HONEST-02 | **Demonstrated RED — fixture** | negative | fixture clone via `new_bare_wiki` with a page claiming an absent part number → exit 1 | ❌ Wave 0 |
| HONEST-02 | **Demonstrated run — live** | integration | run once against the real clone; record the outcome whatever it is | ❌ Wave 0 |
| LEGACY-06 | No unopenable `.planning/` path on any page | source scan | `! grep -rn '\.planning/' wiki-clone/` | ❌ Wave 0 (one-liner) |
| LEGACY-06 | Two named pages de-framed | assertion | no `Phase 58`/`Phase 59` in title, no `Full audit trail:`, no `[CITED: .planning` | ❌ Wave 0 |
| WIKI-02 | No in-repo mirror anywhere | smoke | `! test -d wiki && ! test -f .github/workflows/wiki-publish.yml && ! grep -qE 'def cmd_(publish\|sidebar\|check)' tools/wiki/wiki.py` | ❌ Wave 0 |
| WIKI-05 | Every page reachable from Home | checker | `python3 tools/wiki/wiki.py links --source-dir wiki-clone` | ✅ exists |
| WIKI-05 | `_Sidebar.md` lists every page | new leg | new containment leg in `wiki.py links` | ❌ Wave 0 |
| WIKI-05 | **Demonstrated RED** | negative | **live**: run `links` against the clone after pushing the 12 pages, before rewriting Home → 12 orphans (H-3). Plus a fixture case in `selftest.sh`. | ✅ live case proven this session |

### Sampling Rate

- **Per task commit (app-touching):** the 6-module doc subset + `test_scan_paths_resolve.py`, < 5 s.
- **Per task commit (meta-touching):** `bash tools/wiki/selftest.sh`, ~3 s.
- **Per wave merge:** full app suite on **py3.11** (`1976 passed`, 287 s) + `pio test -e native` if
  firmware source changed + `selftest.sh`.
- **Phase gate:** full app suite green on 3.11 + `python -m build` + `firestarter --help` +
  `selftest.sh` green + both new checkers demonstrated RED then GREEN, evidence committed.

### Wave 0 Gaps

- [ ] `tools/wiki/claim-vocabulary.json` — the D-01 checked-in vocabulary data
- [ ] `tools/wiki/<honest1-checker>.py` — one-shot HONEST-01 multiset comparison, 0/1/2 contract
- [ ] `tools/wiki/<honest2-checker>.py` — standing HONEST-02 stamp + resolve + hash checker
- [ ] `tools/wiki/selftest.sh` — delete 7 publish/sidebar cases; add ≥3 new cases (HONEST-01 weakened
      claim, HONEST-02 absent part number, WIKI-05 unreferenced page)
- [ ] `wiki.py links` — new `_Sidebar.md` containment leg + `DEFAULT_SOURCE_DIR` decision
- [ ] `.github/workflows/wiki-check.yml` — rewritten as clone-driven `schedule` + `workflow_dispatch`
- [ ] Shell one-liner gates for MIGRATE-02, MIGRATE-04, LEGACY-06, WIKI-02 (no framework needed)
- [ ] **`test_dispatch_mirror.py` relocation target** — where the relocated doc leg lives and what it
      reads (wiki clone? recorded SHA?) is the single largest unresolved design question left

**Non-vacuity discipline (project standard, `test_py32_packaging.py:33-42`):** every new checker
must assert its scan target was *found* before comparing anything, and every negative case must be
seen to fail before its green is believed. A "0 of 0 checked, PASS" is the failure mode this
milestone exists to prevent.

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `python3` (system) | meta tooling, checkers | ✓ | 3.12.14 | — |
| CPython 3.11 | MIGRATE-03 on the CI floor | ✓ via `uv` | 3.11.16 | — |
| `uv` | creating the 3.11 venv | ✓ | 0.12.6 | `UV_CACHE_DIR` **must** be set — `~/.cache/uv` is not writable |
| `git` | everything | ✓ | — | — |
| `gh` | wiki push, repo metadata | ✓ authed as `henols`, scopes `gist, read:org, repo, workflow` | — | — |
| Network → `github.com` | wiki clone/push | ✓ (anonymous clone verified) | — | — |
| Network → `gitlab.com` | `build_db.py` regeneration (D-14) | ✓ (regen verified byte-identical) | — | **none** — the fetch URL is hardcoded, no `--input` seam |
| Network → `pypi.org` | sdist verification | ✓ | — | — |
| `requests` | `build_db.py` | ✓ (in `[test]` env) | 2.34.2 | — |
| `pytest` + `syrupy` + `pytest-cov` | app suite | ✓ | 9.1.1 / 6.0.0 / 7.1.0 | — |
| `ruff` | app lint gates | ✓ | 0.16.5 | — |
| PlatformIO | firmware build | not probed — no firmware source change beyond one comment deletion | — | Firmware CI (`build.yml`) covers it |

**Missing dependencies with no fallback:** none blocking.
**Notable:** `build_db.py` has **no offline path** — regeneration requires gitlab.com. If a plan task
must run offline, it cannot regenerate the database.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `GITHUB_TOKEN` with `contents: write` *may or may not* push to `.wiki.git`; sources conflict | Wiki Push | None for this phase — D-19 makes push local. Would matter only if a future phase automates publishing. |
| A2 | `firestarter/doc/` deletion breaks no firmware build (only a C++ comment references it) | Repair Surface | Low — `pio test -e native` / `pio run` were not executed this session; the reference at `test_loop_eprom_v131.cpp:1755` is inside a `/* */` comment |
| A3 | The `fake_firestarter` fixture should be rekeyed off `doc/PROTOCOLS.md` rather than kept | Repair Surface | Medium — this is a recommendation, not a measured requirement; criterion 2's reach into fixture trees is a judgement call for the planner |
| A4 | Excluding `chip_database.baseline.json` from repair is safe | Repair Surface (b) | Low — `diff_db.py` RC=0 was measured under the exact mutation; but only `diff_db` was exercised, not all six baseline consumers |
| A5 | The two "artifact" failures in the 19-failure run (`test_gen_validation_header`, `test_sdp_bus_config_drift`) are scratch-layout artifacts, not doc-caused | MIGRATE-03 | Low — both name `pinouts.json`, not a doc path, and both pass in the real-tree baseline |
| A6 | The recommended workflow shape (named checkouts + branch resolver) will work | GitHub Actions | Low — it is copied from a workflow that runs today, but the new workflow has not been executed |

---

## Open Questions

1. **Where does the relocated `test_dispatch_mirror.py` doc leg read `PROTOCOLS.md` from?**
   - Known: it must parse §0's two tables in their exact column shape; the firmware file is being
     deleted; the meta repo has no pytest harness (D-07 keeps it that way).
   - Unclear: whether the relocated leg reads the **wiki clone** (live, drift-catching, but couples a
     firmware gate to a public wiki edit) or the **recorded D-02 SHA** (stable, but frozen forever
     the way D-03 accepts for HONEST-01).
   - Recommendation: read the **wiki clone**, because the whole point of moving the gate is that the
     wiki is now where the truth lives — and because a frozen source makes the gate a HONEST-01
     clone rather than a dispatch gate. Price the §0 table-shape fragility (Pitfall 6) as the cost.

2. **What happens to `test_py32_packaging.py`'s 5 install-doc legs?**
   - Known: the file they read is deferred *and* deleted; 5 legs go red; CONTEXT.md never names the
     module.
   - Recommendation: delete the 5 legs with the deletion recorded as a deliberate loss of the
     flash-map/pyusb-floor doc-parity gate, and note the gap for the PY32 phase to restore when the
     install guide is finally published.

3. **Does `.planning/codebase/STRUCTURE.md`'s tree diagram get corrected?**
   - D-18 excludes it as historical, but it is a live codebase map that becomes factually wrong.
   - Recommendation: correct the one tree line; it is not a link, so it does not affect criterion 2
     either way, but leaving a known-wrong map is the kind of quiet staleness this milestone opposes.

4. **What is the phase's page-name mapping?** The two hyphen hazards need reworded titles inside
   `[A-Za-z0-9-]`. Not a technical unknown — a naming decision the planner or operator must make and
   record in `MIGRATION-TABLE.md`'s "Wiki page" / "Rendered title" columns.

5. **Should the D-02 SHA also be recorded for `PY32F071-FIRMWARE-INSTALL.md`?** It is deleted but not
   migrated, so it has no HONEST-01 row — but recording its SHA is the difference between "deferred"
   and "lost". Recommendation: record it, in the "Deferred, not migrating" section of the table.

---

## Sources

### Primary (HIGH confidence) — commands run this session against the live tree
- `git clone https://github.com/henols/firestarter_prom.wiki.git` — 6 commits, `master` @ `0155a85`, 3 pages, anonymous clone succeeds
- `pytest tests/` on CPython 3.11.16 — 1976 passed baseline; 19 failed / 1888 passed / 69 skipped without `doc/`
- `pytest --collect-only` with a doc-less firmware root — `Interrupted: 1 error during collection`
- `python -m build --sdist --no-isolation` ×2 (with and without `doc/`) — zero doc entries either way
- `python tools/build_db.py` + `cmp` — byte-identical regeneration
- `FIRESTARTER_DB_FILE=<mutated> python tools/diff_db.py` — RC=0, indifferent to the reason string
- `bash tools/wiki/selftest.sh` — 12 cases, all PASS
- `python3 tools/wiki/wiki.py links --source-dir <clone+12>` — 12 orphans, RC=1
- `sha256sum firestarter/data/chip_database.json` — `0cfd3a83e881bfcc…`
- `git grep`, `wc -l`, `grep -o` sweeps across all three repositories
- `gh repo view` / `gh auth status`
- PyPI JSON API + sdist downloads for `firestarter` 2.0.7, 3.0.0b33, 3.0.0b34

### Primary — source files read in full or in the cited ranges
- `tools/wiki/wiki.py` (542 lines), `tools/wiki/selftest.sh` (12 cases), `.planning/v1.35/MIGRATION-TABLE.md`
- `.github/workflows/{wiki-check,wiki-publish,catalog-sync-check}.yml`
- `firestarter_app/.github/workflows/{ci,beta-release,publish}.yml`
- `firestarter_app/tests/{fw_presence,scan_paths,test_scan_paths_resolve,test_dispatch_mirror,test_py32_packaging}.py`
- `firestarter_app/{pyproject.toml,MANIFEST.in,tools/build_db.py,tools/diff_db.py}`
- `.planning/{CONTEXT,REQUIREMENTS,STATE}.md`, `.planning/notes/v135-wiki-only-reversal.md`, `.planning/codebase/CONVENTIONS.md`
- `firestarter/include/proto_constants.h`, both `CLAUDE.md` files

### Secondary (MEDIUM confidence)
- [docs.github.com — GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token) — token scope limited to the workflow's own repository
- [github.com/orgs/community/discussions/56893](https://github.com/orgs/community/discussions/56893) — community reports on `.wiki.git` push with the default token; contradicts the marketplace-action guidance

### Tertiary (LOW confidence)
- Marketplace action READMEs recommending a PAT for wiki pushes — recorded as a conflicting signal only

---

## Metadata

**Confidence breakdown:**
- Test-suite split and collection hazard: **HIGH** — reproduced twice, with the exact error text
- Packaging / sdist: **HIGH** — three independent measurements including published artifacts
- Repair surface: **HIGH** — exhaustive `git grep` over all tracked files in all three repos
- Claim vocabulary counts: **HIGH** — exact `grep -o` counts, per file
- HONEST-02 resolve-rate falsification: **HIGH** — measured over all 12 files, corroborated by
  `protection_readability.py`'s own docstring explaining the elided-shorthand convention
- Wiki clone/read mechanics: **HIGH** — cloned it
- Wiki push via `GITHUB_TOKEN`: **LOW** — sources conflict; not exercised; not needed under D-19
- Firmware build impact: **MEDIUM** — reasoned from source, `pio` not run

**Research date:** 2026-08-31
**Valid until:** 2026-09-14 (14 days) — the live wiki, the sub-repo branch state and the gitlink
SHAs are all moving targets; re-verify `git clone …wiki.git`, `git branch -a --list '*v1.35*'` and
`sha256sum chip_database.json` before executing.
