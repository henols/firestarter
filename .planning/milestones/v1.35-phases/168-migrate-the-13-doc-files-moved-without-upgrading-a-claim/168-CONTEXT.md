# Phase 168: MIGRATE — The 13 `doc/` Files, Moved Without Upgrading a Claim - Context

**Gathered:** 2026-08-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Get the content of **12** `doc/` files onto the live `firestarter_prom` wiki, delete both `doc/`
directories, repair every reference that pointed into them, and prove the move upgraded no claim.
Then absorb the model reversal's leftovers: retire Phase 167's in-repo source tree and publish
path (WIKI-02), and give the now-hand-maintained navigation a check with real work to do (WIKI-05).

**Nine requirements:** MIGRATE-01…04, HONEST-01, HONEST-02, LEGACY-06, WIKI-02, WIKI-05.

**Not in this phase.** The `firestarter_prom` README is Phase 169's. The two sub-repo READMEs are
170's — except that criterion 2 forces their `doc/` links to be repaired here (see D-17). The
tracker and branch rulesets are 172's. No compatibility matrix, family pages, algorithm pages or
tutorials are authored — those stay deferred as FUT-W-01…05 (activation decision 4).
`PY32F071-FIRMWARE-INSTALL.md` is **deferred, not migrated** — the PY32F071 work is planning-stage
with proof-of-concept code, so an install guide would promise a capability the project cannot back.

**This phase runs against a live, public wiki.** `firestarter_prom.wiki.git` exists as of Phase 167
(`refs/heads/master` @ `0155a85`, 5 commits, 3 pages). Two of those pages are **currently public
and currently false** — see D-21 and D-22. That is not cleanup at the end of the phase; it is a
correctness defect sitting on the front-door repository's wiki right now.

</domain>

<decisions>
## Implementation Decisions

### Claim honesty — HONEST-01, criterion 4

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
  **WIKI-02-clean**: a committed 2,425-line snapshot of documents that now live on the wiki *is*
  an in-repo mirror of wiki content, which is the one thing WIKI-02 forbids. It also makes
  `MIGRATION-TABLE.md` load-bearing rather than decorative, which it has to be anyway for criterion
  1 and for the Backlog 999.9 rename sweep.
  **The SHAs must be recorded before the delete commits, or the oracle is gone.**
  Rejected: a committed `tools/wiki/snapshot/` fixture (duplicates content and violates WIKI-02);
  reconstructing from `git log` at check time (guesses which commit was "immediately before").

- **D-03: HONEST-01 is a one-shot in-phase proof, not a standing gate.** *(Operator decision.)* It
  runs during the migration, is demonstrated failing on a deliberately weakened claim before any
  green result is believed, and its output is committed as evidence. Then it retires. HONEST-02 is
  the standing truth gate.
  **Accepted cost, stated rather than elided:** once `doc/` is gone the source side is frozen at
  the recorded SHAs forever, and nothing thereafter stops a later wiki edit from quietly softening
  a claim the 2026-08-30 documents made. The alternative was rejected because a frozen-snapshot
  gate goes red on any legitimate restructure of a page.
  Rejected: durable scheduled gate against the frozen snapshot (red for innocent reasons → ignored).

- **D-04: The vacuous half is reported as vacuous, in the checker's own output.** Measured
  2026-08-30 across the 12 migrating files: `support_status` appears **12×** as a field name but in
  only **3 files** (`community-validation.md` ×10, `PROTOCOLS.md` ×1, `AT28C04-ADAPTER.md` ×1), and
  only **two values** occur — `adapter-required` ×4 and `protocol-not-implemented` ×1.
  **`vpp-exceeds-max` occurs 0 times. `UNVERIFIED` / `PROTOCOL-LEDGER` occurs 0 times.**
  (`PROTOCOL-LEDGER.json` is a v1.16 planning artifact last touched at Phase 99 and is cited by no
  migrating document.) The checker must print the zero counts explicitly — a "0 of 0 checked, PASS"
  reported as a plain PASS is precisely the false-PASS this milestone exists to prevent.

### The two clone-based gates — HONEST-02 criterion 5, WIKI-05 criterion 8

- **D-05: Two checkers, one workflow, one shared clone step.** They share only the clone;
  HONEST-02 asserts truth against the chip database, WIKI-05 asserts graph reachability. Fusing
  them would mean a database failure and a navigation failure arrive as one indistinguishable red.

- **D-06: WIKI-05 is `wiki.py links` repointed at the clone, plus one new leg.** `links` already
  does orphan detection, internal-link-form validation and filename legality, and it is already
  selftested. Repointing is `--source-dir <clone>` — but note `DEFAULT_SOURCE_DIR` is hardcoded to
  `<repo>/wiki` ([`tools/wiki/wiki.py:45`](../../../tools/wiki/wiki.py#L45)), a directory this phase
  deletes, so the default must move or the flag must become required. Its existing semantics are
  **kept unchanged**: only `Home.md` counts as reachability evidence
  ([`wiki.py:210-228`](../../../tools/wiki/wiki.py#L210-L228)), and `_Sidebar.md` is in
  `NAV_EXCLUDED_PAGES`. That is *stricter* than WIKI-05's "Home **or** a sidebar", and stricter is
  correct — a page reachable only from a hand-maintained sidebar is one forgotten edit from being
  lost. **New leg:** the hand-maintained `_Sidebar.md` lists every page. Together the two legs
  catch drift in both directions.

- **D-07: HONEST-02 is a new standalone checker in `tools/wiki/`, same shape as `wiki.py`.** A
  `python3` script with the 0/1/2 exit contract, driven by `selftest.sh`. This follows the decision
  already taken this session that gates take the `tools/wiki/` standalone-checker shape rather than
  a new pytest harness — the meta repo still has no test harness and this keeps it that way.

- **D-08: The stamp cannot say "generated from DB vN" — there is no DB version. It carries a
  content hash and a date.** Measured 2026-08-30: `chip_database.json` is a 59-key vendor-keyed
  object with **no version field anywhere**. HONEST-02's requirement text is therefore
  *unsatisfiable as literally written*, and the planner must not paper over that. The honest
  substitute is a truncated `sha256` of the database file plus the verification date — it changes
  exactly when the database changes, which is what "stale stamp" has to mean. Current value at
  discussion time: `0cfd3a83e881bfcc`.

- **D-09: Stamp-plus-resolve, because 11 of 12 pages carry per-chip or per-protocol claims.**
  Measured distinct part-number tokens / distinct `0xNN` tokens per file: `PROTOCOLS` 28/34,
  `lockable-proms` 35/0, `infoic-field-dictionary` 9/50, `AT28C04-ADAPTER` 6/1,
  `pinout-safety-review` 4/4, `sram-nvram-behavior` 3/6, `SHIELD-REVISIONS` 0/20, `protocol-id`
  0/18, `package-details` 0/9, `protocol-flags` 0/5, `community-validation` 0/5. Only
  `beta-testing-install` is clean. Exhaustively checking every claim on every page is not
  achievable in this phase; the requirement's own stamp escape hatch is the way through, but a
  stamp is only honest if something checks it. The checker asserts three things:
  1. every page matching the claim signature carries a stamp;
  2. the part numbers and algorithm values a stamped page asserts **resolve in the current
     database**;
  3. the stamp's hash matches the current database — a mismatch flags the page **stale**, which is
     a distinct outcome from *wrong*, not a silent pass.

- **D-10: Scheduled weekly plus `workflow_dispatch`, and demonstrated failing twice — fixture and
  live.** Wiki edits produce no pull request, so there is nothing to gate on; a schedule is the
  only trigger available. 167's D-07 rejected cron for the *drift* check because it would sit red
  by construction between wiki creation and first publish; that reasoning does not transfer —
  HONEST-02 can only go red for a real reason. The negative case runs against a **fixture clone**
  (a page claiming a part number absent from the database; an unreferenced page for WIKI-05), and
  then the checker is run once against the **real clone**. Both are required: v1.34's rig phase
  produced ~20 tooling defects that were all fixture-green and all failed on first contact with
  the real thing.

### Legacy framing — LEGACY-06, criterion 6

- **D-11: Every unopenable `.planning/` path goes, in all 12 files; the two named files are fully
  de-framed; "as of Phase NN" prose stays.** *(Operator decision.)* The distinguishing test is
  **can a public reader act on this?** A `.planning/…` path on a public wiki page is a link that
  cannot be opened — repairing it is *correcting*, which activation decision 4 explicitly permits.
  A phase number inside a sentence is provenance flavour, not a defect, and stripping all 41 of
  them would be *rewriting*, which decision 4 forbids.
  Measured spread — **6 files, 15 references**, not the 2 that LEGACY-06 names: `PROTOCOLS.md` ×5,
  `SHIELD-REVISIONS.md` ×4, `sram-nvram-behavior.md` ×4, `AT28C04-ADAPTER.md` ×1,
  `pinout-safety-review.md` ×1. The two named files additionally lose their `— Phase 58` /
  `— Phase 59` titles, their `**Full audit trail:**` pointers, and — in `sram-nvram-behavior.md` —
  the three `[CITED: .planning/research/PITFALLS.md §E-3]` markers at lines 35, 75 and 97, which
  are the same defect in a different syntax and would otherwise survive a search for the phrase
  LEGACY-06 quotes.
  Rejected: strictly the two named files (ships `PROTOCOLS.md`, the largest page at 556 lines,
  publicly with 5 unopenable pointers); full de-GSD-ification of all 41 mentions (crosses
  activation decision 4 and floods the D-01 claim comparison with edit noise).

- **D-12: Both files ship, rewritten — they are not dropped.** Each is short (88 and 114 lines) and
  each carries genuine operator-facing safety content: the `DIP24_2816` 5V-only / no-VPP-path
  guarantee, and the NVRAM blank-check limitation. LEGACY-06 permits either outcome; dropping
  content that tells an operator what not to do to a chip is the worse one.

### Link repair — MIGRATE-04, criterion 2

- **D-13: References are repaired to a page *title*, not a URL — everywhere except the two
  READMEs.** Backlog 999.9 renames all three repositories and will invalidate every URL this
  milestone writes; `MIGRATION-TABLE.md` is what that sweep greps. Every URL written outside the
  files 999.9 will already be re-sweeping is a link that breaks silently later. A title reference
  also satisfies criterion 2 trivially — it is not a link to a path beneath `doc/` because it is
  not a link. Full wiki URLs are written **only** in the READMEs, which Phases 169 and 170 own and
  999.9 re-sweeps.

- **D-14: The 18 database references are fixed in the generator and regenerated — the JSON is never
  hand-edited.** `chip_database.json` carries the string 9× and
  `tools/baseline/chip_database.baseline.json` carries it 9× more; both are **generated**, emitted
  from [`firestarter_app/tools/build_db.py:569`](../../../firestarter_app/tools/build_db.py#L569)
  with a companion comment at `:543`. The fix is: edit the emitter, regenerate, re-baseline. The
  emitted text is operator-visible `support_status` prose, so under D-13 it names the page rather
  than carrying a path — a repository path inside a database row is exactly what 999.9 breaks.

- **D-15: The `proto_constants.h` provenance comment is deleted, not repointed.** *(Operator
  decision.)* [`firestarter/include/proto_constants.h:14`](../../../firestarter/include/proto_constants.h#L14)
  cites `firestarter/doc/PROTOCOLS.md` as truth for an operator-approved constant set. The operator
  rule is no comments in source, and the cited path is about to stop existing. Provenance for those
  constants lives on the wiki page, which is where the truth now is.

- **D-16: `firestarter/CLAUDE.md`'s lockstep-maintenance rule must survive the move.** It carries 5
  `doc/` references, and among them is a rule requiring lockstep maintenance against
  `doc/SHIELD-REVISIONS.md` §4. Repointing it is not link hygiene — dropping it silently retires a
  real maintenance invariant. This is the single easiest thing in the phase to lose in a
  find-and-replace pass.

- **D-17: The READMEs are repaired in 168 even though 169 and 170 rewrite them.** Criterion 2 says
  *no* file in either repository links to a path beneath `doc/`, and 168 is where `doc/` is
  deleted, so the repair cannot wait. Measured: `firestarter_app/README.md` ×2,
  `firestarter/README.md` ×3. The double work is accepted; leaving five dangling links live between
  168 and 170 is not.

- **D-18: Historical and archive records are excluded from repair — explicitly and by name, not
  silently.** `firestarter/test/native/avr/test_eeprom28c_sdp/RED-BASELINE.md`,
  `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md`,
  `firestarter/tests/golden/eprom_params_citations.json` and
  `firestarter_app/.planning/codebase/STRUCTURE.md` record what was true when they were written;
  the golden sidecar in particular contains a sentence *about* `doc/PROTOCOLS.md` citing paths that
  did not resolve. Repairing a historical record destroys the evidence it exists to hold. The
  planner lists these as a stated exclusion with its reason, so a reviewer sees a decision rather
  than an oversight.

### Getting content onto the wiki, and retiring Phase 167's tooling — WIKI-02, criterion 7

- **D-19: Content reaches the wiki by cloning `firestarter_prom.wiki.git`, committing the pages,
  and pushing.** No tooling is built or retained for it — after the reversal there is no in-repo
  source to publish *from*, so a publish command has nothing to be idempotent about. Twelve pages
  through the web UI would be error-prone and would leave no reviewable commit.

- **D-20: Retirement is deletion, not dormancy.** Removed: `wiki/` (all 3 files),
  `.github/workflows/wiki-publish.yml`, and `wiki.py`'s `publish`, `sidebar` and `check`
  subcommands with their argparse entries and selftest legs. A retired-but-present publish path is
  a loaded gun aimed at the live wiki — running it would wipe the wiki worktree and re-lay it from
  a stale source, which is exactly what its own `--push` documentation says it does. Kept:
  `.planning/v1.35/MIGRATION-TABLE.md`, and `wiki.py links` per D-06.
  `.github/workflows/wiki-check.yml` is repointed at the clone rather than deleted.

- **D-21: `How-This-Wiki-Is-Published` is live, public and false — it is rewritten in this phase,
  not deleted.** It currently states the in-repo-is-authoritative rule and warns that wiki edits
  are overwritten on the next publish. Both statements became false at the reversal. It is rewritten
  into a short "how to edit this wiki" page — the wiki *is* the source, edits happen here, the
  `Title-Case-With-Hyphens` naming convention, and the D-09 stamp rule. Deleting it instead would
  leave nothing telling an editor the conventions the two checkers enforce. Same justification
  Phase 167 recorded for authoring it (D-12): pipeline scaffolding, not product documentation.

- **D-22: `Home.md` is live and false in three places — it is rewritten too.** It links to the page
  above for "why you should not edit them here directly" (false); it says the wiki is published from
  `beta` (nothing publishes now); and its "Coming to this wiki" list names the twelve pages by raw
  source filename (`PROTOCOLS`, `beta-testing-install`) rather than by the `Title-Case-With-Hyphens`
  page names they will actually have. That list becomes the real index, and it is what
  `wiki.py links` walks for reachability under D-06 — so it is load-bearing, not decorative.

### Claude's Discretion

The operator answered the three decisions that were his — HONEST-01's lifetime (D-03), the
de-GSD-ification boundary against his own activation decision 4 (D-11), and the source comment
against his no-comments rule (D-15). Everything else above was decided from measured facts and
recorded precedent and is offered to the planner as **locked but revisable on evidence**, not as
operator-locked: D-01/D-02/D-04, D-05…D-10, D-12, D-13/D-14/D-16/D-17/D-18, D-19…D-22.

Two things are deliberately left to research and planning:

- **Wiki push authentication** — whether the default `GITHUB_TOKEN` with `contents: write` can push
  to `.wiki.git`, or a PAT secret is needed. Only the HONEST-02/WIKI-05 workflow needs read (clone)
  access; D-19's push is a local operator-run action. `gh` is authenticated locally as `henols`.
- **Page-name resolution for the two hyphen hazards** — `AT28C04-ADAPTER.md`, whose natural title is
  a part number already containing a hyphen, and `sram-nvram-behavior.md`, which reads naturally
  with a slash. `MIGRATION-TABLE.md` already flags both and forbids the U+2010 look-alike
  workaround.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The reversal — read this first
- `.planning/notes/v135-wiki-only-reversal.md` — the operator's reversal of activation decision 5,
  what it voids, what survives, the four claim-gate decisions taken earlier in the same session
  that survive it, and the measured facts behind them. **This is the document that makes Phase 167's
  CONTEXT.md safe to read.**

### Milestone scope and constraints (authoritative)
- `.planning/ROADMAP.md` §"Phase 168: MIGRATE — The 13 `doc/` Files, Moved Without Upgrading a
  Claim" — the eight success criteria, with the re-scoping banner. Criteria 4, 5 and 8 all demand
  *observed* failure before a green result is believed.
- `.planning/ROADMAP.md` §"v1.35 — Documentation Consolidation & Wiki Migration" — the activation
  decisions with their accepted costs, and the **999.9 sequencing hazard** that drives D-13.
- `.planning/REQUIREMENTS.md` — MIGRATE-01…04, HONEST-01, HONEST-02, LEGACY-06, WIKI-02, WIKI-05.
  WIKI-03 and WIKI-04 are **withdrawn**; their struck-through original text is preserved in place.
- `.planning/REQUIREMENTS.md` §"Constraints and Hazards" — the honesty constraint, the 999.9
  hazard, and why HONEST-02 became load-bearing when WIKI-04 was withdrawn.
- `.planning/phases/167-wiki-bootstrap-in-repo-source-sync-drift-check/167-CONTEXT.md` — **read
  with the reversal note in hand.** D-03 (page naming) and D-11 (link/orphan check semantics)
  carry forward. D-01/D-02/D-04 through D-10 and D-12 describe the retired model.

### The tooling this phase inherits, retires and repoints
- `tools/wiki/wiki.py` — `links` survives (D-06); `publish`, `sidebar` and `check` are retired
  (D-20). Note `DEFAULT_SOURCE_DIR` at `:45`, `HOME_PAGE`/`NAV_EXCLUDED_PAGES` at `:46-48`,
  `check_orphans` at `:210`, and the 0/1/2 exit contract.
- `tools/wiki/selftest.sh` — the driver every gate in this phase hangs off. Its fixture helpers
  (`new_source_dir`, `new_bare_wiki`) are what the D-10 negative cases are built from.
- `.planning/v1.35/MIGRATION-TABLE.md` — 2 filled rows, 12 `TBD` rows to complete, the deferred
  PY32F071 note, and the hyphen-hazard warning. D-02 adds a per-row SHA column.
- `.github/workflows/wiki-check.yml`, `.github/workflows/wiki-publish.yml` — the first is
  repointed, the second deleted.
- `.github/workflows/catalog-sync-check.yml` — read its comment block as a cautionary record: 5
  runs, 5 failures, never once asserted the property it existed to assert.

### The content being moved
- `firestarter/doc/` — `PROTOCOLS.md` (556), `SHIELD-REVISIONS.md` (128), `AT28C04-ADAPTER.md` (160).
- `firestarter_app/doc/` — `beta-testing-install.md` (213), `community-validation.md` (265),
  `infoic-field-dictionary.md` (325), `lockable-proms.md` (399), `package-details.md` (70),
  `pinout-safety-review.md` (88), `protocol-flags.md` (54), `protocol-id.md` (53),
  `sram-nvram-behavior.md` (114).
- `firestarter_app/doc/PY32F071-FIRMWARE-INSTALL.md` (299) — **deferred, do not migrate.**

### Truth sources for HONEST-02
- `firestarter_app/firestarter/data/chip_database.json` — 59 vendors, **no version field** (D-08).
- `.planning/PROTOCOL-LEDGER.json` — a v1.16 planning artifact last touched at Phase 99. Named by
  the requirement, cited by no migrating document (D-04).

### Repair targets
- `firestarter_app/tools/build_db.py:543,569` — the generator emitting the 18 database references (D-14).
- `firestarter/CLAUDE.md` — 5 references, one of them a lockstep-maintenance rule (D-16).
- `firestarter/include/proto_constants.h:14` — deleted (D-15).
- `firestarter_app/README.md`, `firestarter/README.md` — repaired here, rewritten in 169/170 (D-17).
- `firestarter_app/firestarter/` — `protection_readability.py`, `py32_dfu.py`, `firmware.py`,
  `diagnostic_report.py`, `ic_layout.py`.
- `firestarter_app/tools/` — `diff_db.py`, `check_protection_readability_invariants.py`.

### Project conventions
- `CLAUDE.md` (repo root) — the meta repo tracks `.planning/`, `.claude/`, `tools/`, `.github/`,
  and `wiki/`; this phase removes the last of those.
- `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/STRUCTURE.md`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`wiki.py links`** — orphan detection, internal-link-form validation and filename legality,
  already written and already selftested. It is WIKI-05's check with a `--source-dir` change, and
  it is also the ready-made tool for criterion 2's "no file links to a path beneath `doc/`" sweep
  across 12 imported documents whose relative links were written for a different layout. Measured:
  the migrating files contain 20 relative-link targets, of which 2 are cross-file
  (`infoic-field-dictionary.md#…` ×2, `community-validation.md` ×1) and the rest are same-page
  anchors.
- **`selftest.sh`** — an 18KB bash driver with fixture helpers that build a source tree and a bare
  wiki remote. Both D-10 negative cases plug into it directly.
- **`MIGRATION-TABLE.md`** — 12 pre-seeded `TBD` rows with source repo and source path already
  recorded, so the migration is auditable against the table rather than trusted to remember all
  twelve files.
- **A live wiki with history** — 5 commits including a deliberate hand-edit that was overwritten,
  so the destructive-publish behaviour is already on the record.

### Established Patterns

- **Tooling is a standalone `python3` script plus a `bash` driver under `tools/<name>/`.** No
  package, no import path, no test harness. The meta repo still has no `pyproject.toml`, no
  `pytest.ini` and no `tests/`. D-07 keeps it that way.
- **A checker exits 0/1/2** — 2 distinguishes an operator-gated precondition from a real failure.
- **Generated artifacts are committed and regenerated by tooling, never hand-edited.** `messages.h`
  / `messages.py` via `codegen.py`; `chip_database.json` via `build_db.py`. D-14 follows this.
- **A check is not evidence until it has been seen to fail for the right reason.** Stated in the
  ROADMAP's own criteria 4, 5 and 8, and independently by the `catalog-sync-check.yml` record.

### Integration Points

- **Deleted:** `wiki/`, `.github/workflows/wiki-publish.yml`, `wiki.py`'s three retired
  subcommands, `firestarter/doc/`, `firestarter_app/doc/`.
- **New:** the HONEST-02 claim checker under `tools/wiki/`; the HONEST-01 one-shot claim comparison;
  a clone-driven workflow with `schedule` + `workflow_dispatch`.
- **Changed:** `wiki-check.yml` repointed at a clone; meta CI gains `submodules: recursive` for the
  relocated claim gates; `MIGRATION-TABLE.md` gains a SHA column and 12 filled rows.
- **External and live:** `https://github.com/henols/firestarter_prom.wiki.git` — `master` @
  `0155a85`. Pushing to it is publishing to a public page.

### Gaps the planner must price

- **The relocated `test_dispatch_mirror.py` may come back RED on its first real run.** It has never
  executed in app CI — a bare `actions/checkout@v4` has no firmware sibling, so its doc leg has
  always skipped. In the meta repo all three legs exist for the first time. Fixing it is in-phase
  work, and it is not a small unknown: it parses `PROTOCOLS.md` §0's table as its canonical leg, and
  that document is being moved and edited in the same phase.
- **19 doc-reading legs relocate; ~19 code-side legs across the same ~1,962 lines stay behind.**
  The split runs *inside* five test modules (`test_lockable_proms_doc_claims.py` 154 lines,
  `test_protect_flags_doc_measurements.py` 662, `test_protection_table_citations.py` 268,
  `test_lock_status_class_partition.py` 878, `test_dispatch_mirror.py` 366), several of which
  resolve `_FA_DIR / "doc" / …` at module scope — so a partial move breaks import for the legs that
  stay. This is the largest single mechanical risk in the phase.
- **MIGRATE-03 must be observed on the CI Python floor, not the devcontainer's.** The devcontainer
  runs 3.12 and app CI runs 3.11; the devcontainer has been *proven* to mask app CI breakage before.
  Three files leave the sdist (`SOURCES.txt:28-30`), so the packaging change is real.
- **`firestarter_app` tracks its own `.planning/codebase/`** — one of the `doc/` references lives
  there. Never `rm -rf` that directory.

</code_context>

<specifics>
## Specific Ideas

- **"Can a public reader act on this?"** (D-11) This is the test that settles the de-GSD-ification
  boundary, and it should survive into implementation as the stated rule rather than as a file list.
  An unopenable `.planning/` path fails it. A phase number inside a sentence does not.

- **The snapshot is a SHA, not a copy.** (D-02) Pinning the pre-deletion state as a git ref keeps
  HONEST-01's oracle exact while keeping WIKI-02 true — the one design where "prove nothing was
  lost" and "no in-repo mirror exists" do not fight each other.

- **A stamp is only honest if something checks it.** (D-09) The requirement offers the stamp as an
  alternative to a check; taking that at face value would produce twelve pages asserting their own
  correctness. The stamp carries a database hash so that a stale stamp is a distinct, detectable
  outcome from a wrong claim.

- **"Generated from DB vN" cannot be written, because there is no N.** (D-08) Worth stating plainly
  in the phase's output rather than quietly substituting something — the requirement text is
  unsatisfiable as written and the substitution is a decision, not an implementation detail.

- **Two public pages are false right now.** (D-21, D-22) The reversal did not merely retire tooling;
  it left the front-door repository's wiki asserting a publishing model that no longer exists. This
  is the one item in the phase with a reader-visible cost for every day it is not done.

</specifics>

<deferred>
## Deferred Ideas

- **A durable anti-erosion gate for HONEST-01** — rejected as this phase's mechanism (D-03) because
  a frozen-snapshot comparison goes red on legitimate restructuring. If wiki-side claim erosion
  later proves real, the shape to revisit is a claim-token *floor* (the vocabulary must never
  shrink) rather than a full multiset equality, which tolerates restructuring while still catching
  a deleted hedge.

- **Exhaustive per-claim verification of all 11 claim-bearing pages** — out of reach in this phase
  (D-09), which is why the stamp path exists. `PROTOCOLS.md` alone asserts 28 distinct part numbers
  and 34 distinct algorithm values.

- **The compatibility matrix, family pages, algorithm pages and tutorials** — carried into Backlog
  999.12 from the retired 999.14/gh#7 and deferred at activation as FUT-W-01…05. This phase
  relocates and corrects; it authors none of them.

- **Re-sweeping every wiki URL after Backlog 999.9's repository rename** — the accepted sequencing
  hazard. D-13 minimises the blast radius by keeping URLs out of everything except the two READMEs,
  but Phases 169, 170 and 172 still need the sweep.

- **External link liveness checking** — deferred at 167 (D-11) for CI flakiness, and still deferred.
  The 6 dead issue links it would catch are Phase 172's work via a deterministic grep.

### Reviewed Todos (not folded)

`todo.match-phase 168` returned matches, all scoring on generic keyword overlap (`phase`, `check`,
`read`, `source`, `firestarter`) rather than domain relevance — firmware behaviour, chip-database
decoding, protocol command surfaces and GSD tooling. None touch documentation, the wiki or
repository configuration. Reviewed as a set and deferred wholesale.

One is worth naming because it is adjacent without being in scope:
**"`sync_to_subrepos.sh` runs `diff -q $X $X` twice — two verifications that assert nothing"**
(`2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md`). It is the same defect class this
phase's criteria are written against — a check that can only ever be green — but it lives in the
catalog sync tooling, not the wiki tooling, and fixing it here would be scope creep.

</deferred>

---

*Phase: 168-MIGRATE — The 13 `doc/` Files, Moved Without Upgrading a Claim*
*Context gathered: 2026-08-30*
