# Phase 188: The Tools Directory - Context

**Gathered:** 2026-09-12
**Status:** Ready for planning

<domain>
## Phase Boundary

The phase as roadmapped asked seven questions about `firestarter_app/tools/`: declare every script's
consumer, decide each of ten `check_*.py` gates by name, place six GSD-process tools, strip `.planning/`
citations, fold the frame-vector catalog into the meta sync, and fix two defects in
`audit_coverage_matrix.py`.

**The operator answered all seven with subtraction.** Opening position, in their words: *"I believe that
they aren't bringing any value at all to the projects."* Six of the seven requirements therefore resolve to
**retired, not delivered** — the questions were answered, and the answer was deletion. Only TOOLS-05 (no
process citations under `tools/`) survives as work, and it now applies to six files instead of twenty-four.

**What this phase delivers:** `firestarter_app/tools/` goes from 26 scripts to **6**; the checker apparatus,
the process tooling, both CI mirrors and the frame-vector catalog are deleted; `diff_db.py` relocates into
the skill that is its only real consumer; the survivors stop citing `.planning/`; and the requirement ledger
records each retirement with its cause.

**Scope changed during discussion — this is no longer host-only.** The roadmap scoped Phase 188 to
`firestarter_app/`. Deleting the frame-vector apparatus (D-08) reaches into the firmware repo (a native test
suite registered in both pinned envs, plus a generated header) and therefore into
`firestarter/scripts/baseline/size_baseline.json`. Relocating `diff_db.py` (D-05) reaches into the meta
repo. **All three repositories are in scope.** The planner must not treat this as a one-repo phase.

**Measured scale of the deletion** (line counts taken live, 2026-09-12):

| Population | Lines |
|---|---|
| 10 `check_*.py` gates | 3,985 |
| Their test files | 3,537 |
| 6 GSD-process tools | 4,144 |
| Their test files | 1,625 |
| `ci_parity.sh` + `ci_replica_venv.sh` | 525 |
| `derive_sdp_partition.py` | 263 |
| Frame-vector apparatus (host side, 4 files) | 949 |
| `scan_paths.py` + `test_scan_paths_resolve.py` | 561 |
| **Host repo subtotal** | **~15,589** |
| Frame-vector apparatus (firmware side, 4 paths) | ~1,142 |
| **Total deleted** | **~16,700** |
| Relocated to meta (`diff_db.py`) | 984 |
| **Survivors in `firestarter_app/tools/`** | **2,672** (6 scripts) |

**Still explicitly NOT in scope:**
- The `firestarter_app/tests/` provenance sweep (~1,774 hits). Test files use phase identifiers as gate
  anchors and several *assert* on them, so stripping them changes gate behaviour rather than hygiene. Stays
  a separate decision, per the standing todo.
- Deleting any survivor on reference-count evidence. Every one of the six has a live automated consumer,
  verified by name below.
- Any change to `chip_database.json` content or to the product CLI.

</domain>

<decisions>
## Implementation Decisions

### The checker family — retired whole

- **D-01:** All ten `check_*.py` gates are deleted, **no exceptions**, together with their test files. The
  operator was offered "retire unless load-bearing" and chose "retire the whole family, no exceptions"
  after being shown that `check_mypy_watermark.py` is the CI-named type-error floor and that
  `check_no_exists_proxy.py` was extended eight days ago by quick-260912-mo6. The gates to delete, by name:
  `check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, `check_dispatch.py`,
  `check_is_memory_cmd_no_ifdef.py`, `check_mypy_watermark.py`,
  `check_no_community_support_status_write.py`, `check_no_exists_proxy.py`, `check_no_log_in_sdp_window.py`,
  `check_protection_readability_invariants.py`, `check_sdp_capability_invariants.py`.
  — **Reversibility:** costly — restoring means recovering ten gates plus 3,537 lines of tests from git, and
  any invariant that drifted while they were absent is not retroactively detectable; the gates assert
  present-tense source shape, not history.

- **D-02:** **mypy leaves CI entirely.** `ci.yml`'s `mypy type check (watermark gate)` step
  (`firestarter_app/.github/workflows/ci.yml:86-87`) is deleted with the script it invokes, and nothing
  replaces it — not a plain `mypy` step, not an inline count. The operator was shown that the tree carries
  ~33 mypy errors (so a must-exit-0 step would be red on day one) and that dropping it means the error count
  can drift upward unnoticed, and chose "Nothing — mypy leaves CI".
  — **Reversibility:** costly — re-adding the gate later means first re-establishing a watermark against
  whatever the error count has drifted to, which is the same work the original gate existed to prevent.

- **D-03:** Three test-file naming conventions are in play and the planner must not assume `test_<tool>.py`.
  Measured: seven gates have `tests/test_<gate>.py`; the other three are
  `tests/test_check_dispatch_invariants.py`, `tests/test_check_protection_readability.py`,
  `tests/test_check_sdp_capability.py`.

### The six GSD-process tools — all deleted

- **D-04:** All six go: `audit_coverage_matrix.py` (1,952 lines), `diff_db.py`, `measure_plan_shapes.py`,
  `measure_part_number_delta.py`, `snapshot_report_shapes.py`, `build_devtest_issue_corpus.py`, with their
  tests. The operator was offered "delete five, keep `diff_db.py`" with its product-facing rationale spelled
  out and chose "delete all six".
  — **Reversibility:** costly — `audit_coverage_matrix.py` mints `DEFECT-COV-NN` IDs into a committed
  ledger; the ledger and the generated matrix stay in `.planning/` as frozen artifacts, but no further IDs
  can be minted without restoring the tool.

- **D-05:** **`diff_db.py` is not simply deleted — it relocates.** `.claude/skills/devtest-rootcause/`
  invokes it by name in six places including the command `scripts/seed_debug_session.py` generates. The
  operator chose "skill takes its own copy": `diff_db.py` moves to
  `.claude/skills/devtest-rootcause/scripts/`, and the skill's `check_dispatch.py` references are dropped.
  This follows the standing rule that a skill owns its scripts rather than importing from
  `firestarter_app/tools/`. **The copy must land before the tool is deleted** — see D-21.

- **D-06:** Deleting `audit_coverage_matrix.py` dissolves **TOOLS-01 and TOOLS-07 outright**. The
  repo-escaping default-path defect and the silent `--check` red both cease to exist with the tool. Neither
  needs a fix, a stronger oracle, or a staleness note. Measured for the record before deletion:
  `python tools/audit_coverage_matrix.py --check` exits **1 printing nothing at all** on either fail path
  (`audit_coverage_matrix.py:1499-1509` — neither the new-finding branch nor the missing-`DEFECT-COV-00`
  branch emits a message).

### The two CI mirrors — both deleted

- **D-07:** `ci_parity.sh` (162 lines) and `ci_replica_venv.sh` (363 lines) are both deleted.
  `ci_replica_venv.sh` exists solely to build a numpy-free py3.11 interpreter so the mypy watermark leg is
  trustworthy; D-02 removes its reason to exist. `ci_parity.sh`'s leg 4 is the mypy leg. The operator was
  shown that the two surviving pytest legs guard a real, non-mypy hazard — the devcontainer's sibling
  `firestarter/` checkout masking CI-only test failures — and chose "both go".
  — **Reversibility:** reversible — CI after this phase is ruff plus pytest, which a developer runs
  directly in two commands.

### The frame-vector apparatus — deleted across both sub-repos

- **D-08:** The whole apparatus goes: generator, catalog, both generated artifacts, and **both consuming
  tests**. By path — host: `firestarter_app/tools/catalog/codegen_vectors.py`,
  `firestarter_app/tools/catalog/frame-vectors.toml`, `firestarter_app/firestarter/frame_vectors.py`,
  `firestarter_app/tests/test_frame_vectors.py`; firmware: `firestarter/tools/catalog/codegen_vectors.py`,
  `firestarter/tools/catalog/frame-vectors.toml`, `firestarter/include/frame_vectors.h`,
  `firestarter/test/native/avr/test_frame_vectors/` (3 files).
  — **Reversibility:** one-way in effect — this removes the only mechanism proving host and firmware agree
  on the same wire bytes. Unlike the ten gates it is not a zero-findings AST checker; it is a live
  byte-level cross-repo contract test. **The operator was shown this cost explicitly in the option text and
  chose it anyway.** Recorded as a disclosed, accepted cost, not an oversight — do not re-litigate it, and
  do not quietly preserve a fragment of it.

- **D-09:** Both `codegen_vectors` CI steps are deleted — `Vector catalog validity check`
  (`ci.yml:66-67`) and `Codegen drift gate (frame_vectors.py)` (`ci.yml:69-75`). The operator's instruction
  was that `codegen_vectors.py` *"is not something that shall be used in any ci"*; D-08 makes that moot by
  deleting it, but the two steps must still come out.

- **D-10:** **`catalog/codegen.py` and `build_db.py` stay** — operator's words: *"build_db.py and
  catalog/codegen.py has a really purpose"*. The `Catalog validity check` and `Codegen drift gate
  (messages.py)` CI steps (`ci.yml:55-64`) are untouched.

- **D-11:** **TOOLS-06 dissolves.** Folding `frame-vectors.toml` and `codegen_vectors.py` into
  `tools/catalog/sync_to_subrepos.sh`'s `FILES=(messages.toml codegen.py)` assumed they survive. They do
  not. The measured drift that motivated the requirement (`01fb1a9b` firmware vs `53b4190d` host — three
  provenance-citation lines, output unaffected) is resolved by deletion. **The sync script's `FILES` array
  is not modified by this phase.**

### The declaration requirement — retired outright

- **D-12:** **TOOLS-02 is retired: no consumer declarations, and no check asserting them.** With the
  directory at six scripts each having a named automated consumer, the operator chose to drop both halves.
  The audit's central finding — that a code-level scan cannot distinguish a live operator tool from a dead
  one — is therefore **not addressed by this phase**, and the next cleanup pass inherits that blind spot on
  a smaller directory. Recorded as a disclosed, accepted cost.
  — **Reversibility:** reversible — a declaration convention can be added later to six files cheaply.

- **D-13:** `tests/scan_paths.py` (354 lines) and `tests/test_scan_paths_resolve.py` are **deleted
  entirely**, both populations — the 11 tool resolvers *and* the 6 cross-repo test paths. The operator was
  shown that the cross-repo half guards a measured defect (seven host test modules silently flipping
  PASS→SKIP at exit 0 on a firmware rename) which none of this phase's other deletions address, and that
  Phase 184 repaired it eight days ago. They chose "delete the module entirely".
  — **Reversibility:** costly — restoring means rebuilding the inventory by reading each resolver's source,
  which is what Phase 184's own note says was required the first time ("read out of the actual source…, not
  copied from a plan").
  — **Planning consequence:** `test_scan_paths_resolve.py` fails closed when an entry names a missing file,
  so it will go RED the moment the first tool is deleted. That RED is expected and is not a defect to chase.
  The clean ordering is to delete the pair in the **same commit or wave** as the tools they index, not to
  leave a red suite between waves.

### The survivors

- **D-14:** `firestarter_app/tools/` ends at exactly **six scripts**, each with a live automated consumer
  verified by name during discussion:

  | Survivor | Lines | Consumer |
  |---|---|---|
  | `build_db.py` | 796 | operator-declared purpose; ~10 tests including `test_build_db_interpret_timing.py` |
  | `catalog/codegen.py` | 735 | `ci.yml:55-64`, two steps |
  | `gen_sdp_bus_config.py` | 424 | `tests/test_sdp_bus_config_drift.py` |
  | `gen_validation_header.py` | 190 | `tests/test_gen_validation_header.py`, `tests/test_matrix_schema.py` |
  | `parse_devtest_issue.py` | 448 | 4+ tests incl. `tests/test_chip_test.py` |
  | `gen_test_image.py` | 79 | `tests/test_gen_test_image.py` |

  Non-script files in the directory (`DECODE-NOTES.md`, `extra_chips.json`, `validation_matrix_spec.json`,
  `variant-decode-diff.txt`, `pin-layouts.odt`, `baseline/`) are **out of scope** — this phase decides
  scripts, not data. `__pycache__/` is untracked.

- **D-15:** `derive_sdp_partition.py` (263 lines) is **deleted**. It has no test and no code reference
  anywhere; its only consumer record is `STATE.md` prose. The operator was shown that this is precisely the
  tool the audit misjudged as dead, and that `STATE.md:2482` records a deliberate design decision to keep it
  standalone — and chose to delete it. Disclosed, accepted.

### TOOLS-05 — the only requirement still doing work

- **D-16:** The citation sweep applies to the **six survivors only**. Everything else carrying citations is
  being deleted, which discharges the requirement for those files by removal rather than by editing.
  Measured citation counts on survivors: `catalog/codegen.py` 4, `build_db.py` 4, `gen_test_image.py` 3,
  `parse_devtest_issue.py` 2, `gen_sdp_bus_config.py` 1, `gen_validation_header.py` 0.

- **D-17:** **`catalog/codegen.py` must be stripped at the META canonical copy, not in the sub-repo.** Its
  four hits are `LCAT-03`, `LCAT-05` ×2 and `LCAT-02 + LCI-04` requirement IDs. `/workspaces/tools/catalog/`
  is the authoritative source and `sync_to_subrepos.sh` copies it into both sub-repos, asserting
  byte-identity. Editing `firestarter_app/tools/catalog/codegen.py` alone breaks that assertion and is
  reverted by the next sync. **Strip at `/workspaces/tools/catalog/codegen.py`, then run
  `tools/catalog/sync_to_subrepos.sh`**, which also regenerates `messages.h` and `messages.py` — those two
  generated files must be verified byte-unchanged by the sweep.

- **D-18:** This is an *editing* task, not a regex task. Three automated passes were attempted on the
  earlier package-half sweep and all three were reverted for collateral damage (a line-wise re-wrapper
  corrupted a string literal until the module stopped parsing; a prose-aware scrubber flattened docstring
  indentation package-wide). Do it by hand with `ruff format --check` and the suite after each batch. Keep
  comments that explain the *code* to a reader without planning context; delete only process provenance.

### Proof, ordering and the ledger

- **D-19:** **Acceptance proof is the executable gates only — no ritual.** Operator's instruction: *"Do the
  simplest that aren't have complex things that isn't adding real value of testing the code."* Concretely:
  - App: `ruff check firestarter/ tests/`, `ruff format --check firestarter/ tests/`,
    `pytest tests/ --cov=firestarter --cov-fail-under=70`, and the `firestarter --help` smoke test.
  - Firmware: `pio test -e native` and `pio test -e native_nodevtools` green, and
    `python scripts/check_size_baseline.py` exit 0.
  - A plain grep for dangling references to every deleted path is run **as part of the work**, not staged as
    a committed evidence artifact.
  - **Not** a full cold three-target AVR rebuild with twelve-figure transcription, unless D-20's check says
    the AVR figures actually moved.

- **D-20:** **The size-baseline re-record is native-only, pending one verification.**
  `firestarter/scripts/baseline/size_baseline.json` pins `cases: 185, suites: 17` for both `native` and
  `native_nodevtools`, and `compare_native` asserts `cases` **exactly** — so deleting the
  `test_frame_vectors` suite (registered at `firestarter/platformio.ini:101` and `:160`, both pinned envs)
  reddens `check_size_baseline.py` until the counts move. But `frame_vectors.h` is included only from
  `test/native/avr/`, never from `src/`, so AVR flash and RAM should be byte-unchanged. **Verify that with
  one cold `rm -rf .pio/build/uno && pio run -e uno` before deciding.** If the AVR figures hold, move only
  the native `cases`/`suites` pair and leave the twelve AVR figures untouched. If they moved, fall back to
  Phase 185's full recipe. `size_baseline_base01.json` is **not** re-anchored either way.

- **D-21:** **Ordering — meta first, then host and firmware in parallel.** (Operator said "you decide.")
  - **Wave 1, meta alone:** `diff_db.py` copied into `.claude/skills/devtest-rootcause/scripts/`, the
    skill's `check_dispatch.py` references dropped. Nothing downstream may delete `diff_db.py` before this
    lands, or the documented root-cause procedure is broken in the interim.
  - **Waves 2 and 3, host ∥ firmware:** file-disjoint, no shared path.
  - **Two hard intra-wave constraints:** (a) `ci.yml`'s mypy and vector steps are deleted in the *same
    commit* as the tools they invoke, or CI is red between commits; (b) the firmware suite deletion and the
    baseline re-record are **one cold capture**, not two.
  - `catalog/codegen.py`'s meta-side strip (D-17) plus its sync touches all three repos and is best landed
    as its own commit after waves 2 and 3, so the regenerated `messages.h`/`messages.py` can be proven
    byte-unchanged against a settled tree.

- **D-22:** **The ledger is amended in-phase, and RETIRED is not Complete.** REQUIREMENTS.md and all seven
  ROADMAP success criteria are amended by hand as the work lands — the Phase 185 criterion 5 and Phase 187
  criterion 4 precedent. A retired requirement is marked **RETIRED with its cause**, never checked off as
  Complete, so the distinction between "we built it" and "we decided not to" stays legible at milestone
  audit. Expected end state: TOOLS-01, -02, -04, -06, -07 → RETIRED; TOOLS-03 → satisfied by family
  retirement; TOOLS-05 → Complete.
  **ROADMAP.md edits are hand-authored.** Do not run `roadmap.update-plan-progress` against this phase — it
  overwrites the dependency table positionally.

- **D-23:** One verdict document at `.planning/notes/host-tools-retirement.md`, on the shape of
  `.planning/notes/catalog-sync-check-retirement.md` — one line per retired item naming what it guarded and
  why it went, plus the disclosed costs from D-08, D-12, D-13 and D-15 in one place. **No successor guard is
  authored**, and no new `check_*.py` or CI gate is created by this phase for any reason.

- **D-24:** Branch model per standing policy: a `v1.37`-slug branch forked off `beta` in **all three**
  repositories including meta. Never work directly on `beta` or `main`.

### Claude's Discretion

- Wave-to-plan decomposition and commit boundaries, subject to D-21's three named constraints.
- Whether the ten gate deletions land as one commit or several, and how their tests are batched with them.
- The verdict note's internal structure and prose.
- Which planted-violation fixtures under `tests/fixtures/` go with their gates and which are shared — read
  each before deleting; a fixture with a surviving consumer stays.
- Exact wording of the six survivors' docstrings after the D-16 sweep, subject to D-18.

### Folded Todos

- **`.planning/todos/pending/2026-09-12-retire-two-orphaned-host-tools.md`** — this phase *is* that todo.
  Its recommendation was "declare consumers, then delete safely"; the operator chose to delete without the
  declaration layer (D-12). Note the irony for the record: the todo's two named tools split — the ones it
  wrongly called dead, `ci_replica_venv.sh` and `derive_sdp_partition.py`, are both deleted here, but on
  operator judgment about value rather than on the reference-count evidence the todo retracted. Close the
  todo with that distinction stated.
- **`.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md`** — its `tools/` half
  (~296 hits) is folded via D-16, mostly discharged by deletion. Its `tests/` half (~1,774 hits) stays open
  and out of scope. Do not close the todo; amend it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The audit and research this phase was scoped from
- `.planning/notes/host-tools-checker-apparatus-audit.md` — the measured mass, the per-gate ratios, the
  one-shot-gate diagnosis, and **both** of its own corrections. Read the "CORRECTED — there is no
  'unambiguous dead weight' section" heading in full; it is the reason criterion 2 existed.
- `.planning/research/questions.md` §"Host `tools/` checker apparatus — retire or keep?" (line 258) and
  §"Which host tools are doing GSD's work?" (line 289) — the questions TOOLS-03 and TOOLS-04 are.
- `.planning/seeds/phase-gate-expiry-discipline.md` — **its premise is answered by deletion, not by
  discipline.** Mark it resolved rather than leaving it dormant; there is no gate family left to expire.

### The requirements and criteria being amended
- `.planning/REQUIREMENTS.md` §TOOLS (lines 202-232) — TOOLS-01…07 verbatim; the traceability rows at
  lines 278-284.
- `.planning/ROADMAP.md` §"Phase 188: The Tools Directory" (line 571) — all seven success criteria, the
  "Explicitly NOT in scope" paragraph, and the Key context list. **Every criterion is now stale; D-22
  governs how they are amended.**

### Precedent this phase follows, by name
- `.planning/notes/catalog-sync-check-retirement.md` — the shape D-23's verdict note copies: a retirement
  recorded outside a commit message, with no successor guard. Also the source of criterion 6's "no new CI
  gate" constraint.
- `.planning/notes/dispatch-invariant-retirement-verdict.md` — a second instance of the same pattern.
- `.planning/phases/185-records-and-checks-that-are-current/` — criterion 5's in-phase hand amendment, and
  plan 185-01's cold-capture recipe that D-20 falls back to.
- `.planning/phases/187-answered-reports/187-CONTEXT.md` — criterion 4's amendment shape.

### The starting point that is now moot
- `.planning/quick/260912-mo6-fail-closed-on-repo-escaping-default-out/260912-mo6-SUMMARY.md` — the guard
  TOOLS-01 was to strengthen. Dissolved by D-04; `tests/test_audit_coverage_matrix_default_paths.py` is
  deleted with the tool it tests.

### Code under change — host
- `firestarter_app/tools/` — the whole directory; D-14's table is the survivor set.
- `firestarter_app/.github/workflows/ci.yml` — `:55-64` catalog steps **stay**; `:66-75` vector steps go
  (D-09); `:86-87` mypy step goes (D-02); `:80-84` ruff and `:89-90` pytest stay and are the acceptance
  gates (D-19). Coverage scope is `--cov=firestarter`, so `tools/` tests were never counted.
- `firestarter_app/tests/` — the ten gate test files (three under non-obvious names, D-03), the six process
  tools' test files, `test_frame_vectors.py`, `scan_paths.py`, `test_scan_paths_resolve.py`.
- `firestarter_app/tests/test_cobs.py` (394 lines) — **independently covers the COBS/CRC8 path**, so D-08
  strands no product coverage. Verified during discussion; do not duplicate its cases elsewhere.
- `firestarter_app/pyproject.toml` — `packages = ["firestarter"]` (`:92`) is why `frame_vectors.py` ships in
  the wheel today; D-08 removes it.

### Code under change — firmware
- `firestarter/platformio.ini` — `:101` and `:160` register `native/avr/test_frame_vectors` in both pinned
  envs; `:122` and `:182` add its include path. All four go.
- `firestarter/scripts/baseline/size_baseline.json` — `cases: 185, suites: 17` at `:69` and `:75`;
  `envs_agree_note` at `:88` quotes the same figures in prose and must move with them.
- `firestarter/scripts/check_size_baseline.py` — `compare_native` asserts `cases` exactly.
- `firestarter/.github/workflows/build.yml` — `:142` and `:155` run the two pinned native envs; `:193` runs
  `pio run`. These are D-19's firmware acceptance gates.

### Code under change — meta
- `/workspaces/tools/catalog/codegen.py` — D-17's strip target, the canonical copy.
- `/workspaces/tools/catalog/sync_to_subrepos.sh` — `FILES=(messages.toml codegen.py)`; **not modified by
  this phase** (D-11). Run it after D-17's strip.
- `.claude/skills/devtest-rootcause/SKILL.md` — `:17`, `:272`, `:281`, `:353`, `:420` reference `diff_db.py`
  and/or `check_dispatch.py`.
- `.claude/skills/devtest-rootcause/scripts/seed_debug_session.py` — `:68` emits a command line calling both
  `build_db.py` and `diff_db.py`.

### Standing rules that constrain this phase
- `/workspaces/CLAUDE.md` §"Source code comments — hard rule" — governs D-16/D-18. Not overridable by a
  plan. It forbids *writing* comments, not deleting them. Click docstrings are user-facing `--help` text and
  are not comments.
- `/workspaces/CLAUDE.md` §"Milestone close and branch protection" — `main` protected in all three repos;
  this project's base branch is `beta` (D-24).

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured facts (live, 2026-09-12 — re-verify before relying on the numbers)

- `audit_coverage_matrix.py --check` exits **1 with zero output**, both stdout and stderr empty. Neither
  fail branch prints. Recorded because criterion 7's "still red, unexplained" is the literal current state,
  and because D-04 dissolves it rather than fixing it.
- CI invokes **three** `tools/` entry points, not the one the audit reported: `check_mypy_watermark.py`,
  `catalog/codegen.py --check`, and `catalog/codegen_vectors.py --check` (plus two regen-and-diff steps).
  The audit's "exactly one checker is named in ci.yml" sentence is true only of the `check_*` family.
- `codegen_vectors.py` has drifted between sub-repos (`01fb1a9b` firmware vs `53b4190d` host); the diff is
  **exactly three provenance-citation lines** (`Phase 52`, `D-04/D-09`, `D-05`) — the host copy was swept,
  the firmware copy was not. `frame-vectors.toml` is byte-identical across both. Neither has a meta copy.
- `messages.toml` and `codegen.py` are byte-identical across all three repos, confirming the sync works.
- No product module on either side imports `frame_vectors`; consumers are one test per repo.
- `test_blast_radius_invariance.py` and `test_devtest_issue_corpus.py` read **committed artifacts** and do
  not invoke their generators — they survive D-04 untouched. `test_plan_shapes_drift.py` and
  `test_part_number_delta_drift.py` **do** invoke theirs by subprocess and are deleted with them.

### Established patterns this phase must follow

- **Retirement writes a note, not a successor.** Phase 185 deleted the `Catalog sync check` workflow
  outright and recorded why; `tools/wiki/` was retired wholesale on 2026-09-02 with no replacement guard.
  D-23 is the third instance.
- **In-phase hand amendment of criteria.** Both Phase 185 and Phase 187 amended their own success criteria
  in place when reality diverged, quoting the conflict. D-22 does the same.
- **Cold-capture transcription for baseline figures.** Never `check_size_baseline.py --rebuild`; transcribe
  from committed capture logs; never compute a figure by arithmetic on a prior record.
- **A skill owns its scripts.** Never an import from `firestarter_app/tools/` — a copy, per D-05.

### Integration points

- `tests/scan_paths.py`'s fail-closed resolve test is the natural ordering detector for the whole phase: it
  goes RED the moment an indexed tool disappears. D-13 deletes it, so pair the deletion with the tools it
  indexes rather than leaving a red suite between waves.
- The `sync_to_subrepos.sh` run in D-17 regenerates `firestarter/include/messages.h` and
  `firestarter_app/firestarter/messages.py`. Both are generated product files; prove them byte-unchanged.
- Deleting `firestarter_app/firestarter/frame_vectors.py` removes a module from the shipped package — check
  nothing in `pyproject.toml` or packaging tests names it.

</code_context>

<specifics>
## Specific Ideas

- The operator's framing, verbatim, for anyone reading this later: *"I believe that they aren't bringing any
  value at all to the projects."* This phase is a subtraction, and the burden of proof throughout is on
  **keeping** a file, not on deleting it.
- *"build_db.py and catalog/codegen.py has a really purpose, if catalog/codegen_vectors.py is needed must be
  investigated, but it's not something that shall be used in any ci."* The investigation was run during
  discussion and its finding is recorded at D-08.
- On acceptance evidence: *"Do the simplest that aren't have complex things that isn't adding real value of
  testing the code."* Read as: run the things that execute code; skip transcription ceremony for figures
  that should not move.

</specifics>

<deferred>
## Deferred Ideas

- **A consumer-declaration convention for the six survivors.** Retired by D-12, not refuted. If the
  directory ever grows back, the audit's finding still stands — a scan cannot tell a live operator tool from
  a dead one.
- **Re-guarding the firmware-rename masking defect.** D-13 deletes its only named guard. If the sibling
  layout ever flips host tests to SKIP again, that is the return of a measured defect, not a new one.
- **A replacement for the cross-repo wire-contract proof.** D-08 removes it deliberately. If host and
  firmware framing ever diverge, nothing will catch it.
- **The `firestarter_app/tests/` provenance sweep (~1,774 hits).** Explicitly out of scope; test files
  assert on phase identifiers, so stripping them changes gate behaviour.
- **A mypy floor in any form.** D-02 removes it with no replacement.

### Reviewed Todos (not folded)

`todo.match-phase 188` returned 9 candidates at score 0.9, but the matcher keys on the words "firestarter",
"tools" and "build" and so matches every chip-database todo in the pending set. Reviewed and **not** folded,
all being chip-database decode questions with no relation to tooling hygiene:
`derive-away-max-27c020-size-hardcode.md`, `fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md`,
`onerom-pinout-external-corroboration-gate.md`, `pinout-address-width-and-we-pin-corrections.md`,
`promoted-0x0d-rows-keep-the-64-byte-floor.md`, `vcc-5500-high-margin-verify-rail-group.md`,
`2026-09-08-reclaim-local-scratch-artifacts.md`,
`2026-09-08-separate-gitignore-classes-live-state-vs-build-junk.md`.

Also reviewed and not folded: `2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md` — already
discharged by Phase 185 plan 185-05; verify and close it rather than carrying it into this phase.

</deferred>

---

*Phase: 188-the-tools-directory*
*Context gathered: 2026-09-12*
