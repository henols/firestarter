# Phase 181: Report Fidelity — Schema 2.0, Canonical Naming & Hygiene Close - Context

**Gathered:** 2026-09-09
**Status:** Ready for planning

<domain>
## Phase Boundary

The last phase of v1.36. Eighteen requirements, **host-only** (`firestarter_app/`) — no firmware
change, so no dual-repo lockstep, no golden register traces, no size baseline. `git -C firestarter
status --porcelain` must stay clean.

**In scope — the five requirement clusters plus four folded residuals:**

1. **RPT-A (5)** — make five report fields describe what the run actually knows: `chip_id_actual` on
   a passing id check, `steps[].fingerprint`'s `total`/`bad`/`bad_pct`/`evidence` siblings,
   `steps[].divergence` exported, `plan.is_uv` as a top-level boolean, and the detected chip ID as a
   structured `StepResult` field instead of prose scraped out of `reason`.
2. **RPT-B (2)** — delete `voltage.vpp_mv`, `voltage.vpe_mv` and `banner.locked_steps`, plus the
   `Plan.locked_destructive` adjudication D-7 deferred here. `.claude/skills/devtest-triage/SKILL.md`
   updated in the **same commit** as the `vpp_mv` deletion (D-5).
3. **RPT-D (2)** — `duration_s` stops summing across cycles; a real wall-clock `elapsed` is added;
   the render-only "steps total" sum-of-sums row is removed.
4. **RPT-E (3)** — `schema_version` → `2.0`; the frozen schema-1.2 fixtures keep parsing; the dedup
   hash is proven unmoved.
5. **RPT-F (2)** — `auto_capture.canonical_part_number` carries the matched database `part_number`
   and drives the issue title and body; `ac.chip` keeps the operator's raw token.
6. **HYG (4)** — `syrupy>=5.0,<7`; no new runtime dependency; the never-hash-`to_dict()` decision
   recorded in `MILESTONES.md`; every new `dev_test` helper registered in
   `tools/check_devtest_orchestrator.py`.
7. **Four folded residuals** — see `### Folded Todos`.

**Explicitly out of scope:**

- **The milestone close itself** (D-22). The beta cut, the `v1.36` tag and the three
  `.github`-only PRs to protected `main` stay with `/gsd-complete-milestone` and `/gsd-ship`.
- **Any firmware edit.** The 999.44 firmware half (region-scoped `mem_util_blank_check`) stays open
  in the backlog; `firestarter write foo.bin -a 0x3FF00` remains refused on a non-blank
  non-erasable part, knowingly.
- **Any re-key of `dedup_fingerprint`.** This phase declares **zero** — see D-16.
- **A canonical-spelling sweep of the app test suite.** Measured actively harmful; see D-04.
- **Replying to or closing gh#21/#23/#28/#31/#45/#50.** This milestone builds the fixes; it does
  not work the tracker.
- **Second-count acceptance criteria.** House rule for this milestone: criteria are stated in
  operation counts, never seconds.

</domain>

<decisions>
## Implementation Decisions

### Canonical naming (RPT-F1)

- **D-01:** **The title shows the alias that case-insensitively equals the operator's raw token;
  when none matches, the first alias.** Measured: 514 of 953 database aliases resolve to a
  comma-joined `part_number`, and "first alias" is actively wrong on some of them — `w27c020`
  resolves to `W27C02,W27C020,W27E02,W27E020,W27L02`, whose first entry is a genuinely different
  part number. The token-match rule names the part that was in the socket for all 26 filed issues.
  — **Reversibility:** costly — the rule is baked into every issue title filed after it lands, and
  `count_agreeing` reads the hash embedded in a filed body; a later rule change renames chips
  across the tracker with no migration path for already-filed issues.

- **D-02:** **The selected alias keeps infoic's parenthetical mode annotation verbatim.**
  `canonical_part_number` reads `DS1245AB(RW)`, never `DS1245AB`. Measured: 43 rows carry parens and
  **24 paren-stripped names appear on more than one row** — every DALLAS NVRAM ships as an `(RW)`
  row *and* a `(TEST)` row. Stripping would file two distinct database rows under one title.
  The selector **mirrors `get_eprom_config`'s own exact-then-paren-stripped ladder**
  (`database.py:466-485`) rather than writing a second normalization, so the alias it picks is by
  construction the one the lookup matched.

- **D-03:** **Four surfaces switch to canonical; artifact filenames do not.** Canonical: the issue
  title, the issue body's new `canonical_part_number` line, the console table title
  (`diagnostic_report.py:826`) and the saved report heading (`cli_handlers.py:2497`). Raw token:
  `dev-test-<chip>.json` / `.md` filenames and `ac.chip`. Rationale: the operator finds the file
  under the name they typed, and `_sanitize_chip_token` would otherwise emit
  `dev-test-DS1245AB_RW_.json`, unpredictable from the command line.

- **D-04:** **No canonical-spelling sweep of the app test suite.** The RPT-F1 todo asks for one; it
  is refused with the measurement. The todo counts "12 occurrences of `at28c256`, 6 of `w27c512`";
  the real count is **103 across 23 test files**, including
  `tests/fixtures/report_shapes.py` and `tests/test_blast_radius_invariance.py`. Under D-2 a test's
  chip token models what an operator **types**, and `dedup_fingerprint` hashes `ac.chip` first —
  rewriting `chip="m27c512"` to `chip="M27C512"` produces `776846bf2dc8`, which is **already frozen
  as the `m27c512-full-canonical-name` shape** Phase 174 registered expressly to redden if someone
  normalizes `parts[0]`. A sweep would collide two frozen shapes and re-key the milestone's own
  oracle. `tests/fixtures/devtest_issue_corpus.json` is historical evidence of what was actually
  filed and must not be rewritten either. **What does change:** assertions on `build_title()` output
  and on the rendered headings.

### Duration semantics (RPT-D1, RPT-D2)

- **D-05:** **`duration_s` becomes the mean over the cycles that ran.** `_aggregate_cycle_results`
  (`chip_test.py:1360`) currently sums; the replacement is `sum / cycles that reached the operator`.
  Identical to the median at the default N=2, and the only candidate under which a `--fast` value
  and a default value measure the same quantity — RPT-D1's stated property. Rejected: last-cycle
  (the sibling-field convention, but a `--fast` run's only cycle is cycle 1, which the engine's own
  `_CYCLE_BLOCK_OPS` note says is not equivalent to cycle 2) and max (at N=2 that is mostly
  "whichever cycle had the unknown start", a property of cycle ordering).
  **Stated caveat, to be carried into the docstring:** cycle 1 and cycle 2 are not the same
  operation, so the mean blends two slightly different things; it uses all the evidence rather than
  discarding half of it. **When no cycle produced a duration, the field stays `None`** — never
  `0.0`, per the existing rule that a `0.0` there reads as "ran, took no time".

- **D-06:** **`elapsed` runs from CLI entry to just before the first serialization.** It captures
  the `EpromDatabase` load, the identity read, plan derivation and every step — everything the
  current "steps total" row admits it excludes. It stops before render, file write and the submit
  prompt, and the field's docstring names those three exclusions plainly.
  **Two mechanical constraints, measured:** `to_dict()` is called **three times** per run (console
  render, the saved `.json`, and `to_json_block()` inside the `.md`), each re-stamping `generated` —
  so `elapsed` **must be a stored field stamped once**, never computed inside `to_dict()`, or the
  console and the saved artifact would disagree. And the submit prompt runs *after* all three
  serializations, so any definition including the operator's think-time would need the artifact
  written twice.

- **D-07:** **An `elapsed` row replaces "steps total" in the console table, and the filed issue body
  carries it too.** The operator who just waited for the run keeps a total in front of them, and it
  is now a number that does not silently under-report by excluding the connects and the database
  load.

### How deep the deletions cut (RPT-B1, RPT-B2, D-7)

- **D-08:** **D-7 is adjudicated at the fullest depth: `banner.locked_steps`,
  `Plan.locked_destructive` and `write_scope="none"` all go.** This is a deliberate operator choice
  **against** the narrow reading D-7's own wording hints at ("the deletion is narrower than 999.36's
  RPT-B2 states") and against Claude's recommendation. The concern was stated at the time: it is the
  largest surface change in the milestone's closing phase, and it touches
  `sdp_oracle_applicable` (`chip_test.py:2013-2031`), which reads `plan.locked_destructive` and
  feeds `_dev_test_exit_code`'s `sdp_oracle_not_run` code-2 candidate — a path Phase 178 just
  changed. The operator reaffirmed the choice. **Two measurements taken afterwards materially
  de-risk it and should be re-verified by the planner:** every frozen shape in `report_shapes.py`
  builds with `write_scope="full"` (none uses `"none"`), and `tests/plan_corpus.py` explicitly
  **excludes** `"none"` from its 1,354-plan sweep — so neither the invariance corpus nor Phase 175's
  PRUNE-06 coverage claim is touched.
  — **Reversibility:** costly — restoring it means re-adding a dataclass field, a parameter, four
  `derive_plan` branches, `count_applicable`'s `+ len(...)` term and
  `sdp_oracle_applicable`'s second arm, plus ~69 `write_scope="none"` test uses across 7 files and
  41 `locked_*` assertions across 7 files.

- **D-09:**

  ## Status: Phase 181 amendment

  **2026-09-09, operator adjudication.** `derive_plan`'s `write_scope` parameter is NARROWED to
  `"full"`/`"partial"` with NO DEFAULT, not dropped entirely. This D-09 decision originally called
  for dropping the parameter; that reading is reversed here, on a measurement, not a preference.
  The equivalence `write_scope == "partial"` **iff** `is_uv` holds on every path `dev test` itself
  can reach, but 7 of the 19 registered shapes in `tests/fixtures/report_shapes.py` build a UV chip
  at `write_scope="full"` — a combination `dev test` never produces. Selecting the write op from
  `is_uv` instead of `write_scope` renames their write op and re-keys all seven filed dedup
  fingerprints, including `m27c512-full-canonical-name` (`776846bf2dc8` → `c4ab2e895c1a`) and
  `m27c512-full-comma-joined-name`, the two shapes Phase 174 froze expressly as D-02's rejected
  alternatives — this phase's own RPT-F1 depends on both as a tripwire. Measured pairs and method:
  `.planning/phases/181-.../evidence/181-04-frozen-hash-reproof.txt`.
  **Therefore:** `write_scope` stays keyword-only with **no default** — a bare two-argument call now
  raises `TypeError` rather than silently selecting the retired `"none"` scope, which is the shape
  that makes the 15 previously-bare call sites (measured in `181-02-derive-plan-equivalence.txt`)
  safe. `_resolve_write_scope` is **still deleted**; its two-line rule is inlined at the single
  production `derive_plan` call site in `cli_handlers.dev_test`. Everything else D-08 names still
  dies. **D-16 stands unamended** — zero re-keys, all 19 frozen hashes byte-identical, precisely
  because `write_op` and `full_device_permitted` are left reading off `write_scope`.
  **Consequences the planner must carry:** `full_device_permitted = write_scope == _WRITE_SCOPE_FULL`
  and `write_op = OP_WRITE_PARTIAL if write_scope == _WRITE_SCOPE_PARTIAL else OP_WRITE` are
  **BYTE-UNCHANGED** — do not re-point either onto `is_uv`; that is now an instruction to cause the
  defect this amendment exists to prevent. `_resolve_write_scope` still dies, so **HYG-04 must
  *remove* it from `_HANDLER_FUNCTION_NAMES`** or
  `test_handler_function_names_all_resolve_to_real_callables` goes RED; and `_WRITE_SCOPE_NONE`, the
  three-member `_WRITE_SCOPES` (now two members) and the `ValueError` ladder's value list narrow with
  it — the ladder itself survives, since two values still need fail-closed validation.
  The gate that would redden if a later change tried the rejected reading anyway:
  `test_the_write_op_selector_reads_write_scope_and_never_is_uv` in
  `firestarter_app/tests/test_derive_plan_structural_sentinel.py`, observed RED against the exact
  planted mutation (`.planning/phases/181-.../evidence/181-04-write-op-pin-red.txt`).
  — **Reversibility:** costly — same surface as D-08, plus the one production call site.

- **D-10:** **The console `chip_id` row stays one-sided on agreement and two-sided only on a
  mismatch.** RPT-A1 is satisfied in the **export**: `chip_id_actual` populates in `to_dict()` and
  the filed body on a passing id check. The render is deliberately left as the 2026-08-21 operator
  decision set it — *"the two-sided row now appears only when there IS a disagreement to show"*.
  A matching `0x1F65 / 0x1F65` pair is not added to the table.

- **D-11:** **An agreeing read records a divergence result with `bad: 0`, mirroring PRUNE-03.**
  Today `_dispatch_read` sets `divergence` only when the two runs disagreed, so `None` conflates
  "compared and matched" with "never compared". After this change `None` means exactly what RPT-A3
  says it means — no comparison was possible (`--fast`, or a failed read). This is the same move
  PRUNE-03 made for the fingerprint: a passing compare reports `bad=0` rather than nothing.
  **Declared cost:** it reddens `test_read_step_agreement_no_divergence_recorded`
  (`tests/test_chip_test.py:2166`), which Phase 180's D-06 cited as covering the agreeing case. That
  test is edited with its reason recorded, not deleted silently. `divergence` is not in the dedup
  hash, so no re-key.

- **D-12:** **RPT-B1's premise is confirmed, and the proving test is a source census.** Verified:
  the only assignments anywhere to `.vpp_mv` / `.vpe_mv` on a report object are
  `tests/test_diagnostic_report.py:982-983`, a test that builds the standalone shape by hand.
  `_make_sampler` (`cli_handlers.py:2230-2255`) assigns **only** the four before/after fields.
  So "no code path assigns them" is provable by an AST/grep census over `firestarter/` returning
  zero, and the one test that assigns them is the test that must be re-pointed or removed.

### Closing scope (RPT-E1, RPT-E2, RPT-E3, HYG-01…04)

- **D-13:** **`schema_version` → `"2.0"`** (D-3, already settled at requirements definition). Two
  literal assertions must move with it: `tests/test_blast_radius_invariance.py:517` and
  `tests/test_diagnostic_report.py:1489`, both of which assert `== "1.8"` today. Both parsers accept
  `schema_version` by presence only and the dedup hash never reads it, so the bump is mechanically
  free.

- **D-14:** **The six Phase 174 key-list pins move in the SAME commit as the key change they
  describe.** `_TO_DICT_KEYS` (+`elapsed`, +`is_uv`), `_VOLTAGE_KEYS` (−2), `_BANNER_KEYS` (−1),
  `_AUTO_CAPTURE_KEYS` (+`canonical_part_number`) and `_STEPS_ELEMENT_0_KEYS` (+ the fingerprint
  siblings, `divergence`, and RPT-A5's field) all move; `_TRANSPORT_HEALTH_KEYS` and `_DB_DIFF_KEYS`
  do not. These are **key-list** pins, not frozen hash literals: a key change with a stale pin is
  simply a broken tree, so splitting them across commits would leave the suite RED at a bisect
  point for no review benefit. The two-commit rule at
  `tests/test_blast_radius_invariance.py:278-280` governs **`FROZEN_HASHES` literals only** — and
  under D-16 no hash literal moves this phase, so that rule never fires here. Phase 174 pinned these
  keys deliberately, stating that *"Phase 181's deletion has to argue with a gate that predates
  it"*; the argument is D-08/D-12/RPT-A2, recorded in the commit message.

- **D-15:** **RPT-E3 re-anchors to the surviving mechanism, and the ledger's retirement is stated.**
  GATE-06's `RK-174-` ledger table, its app-side fixture, its checker and its CI workflow were all
  **retired on 2026-09-08** (`MILESTONES.md` §v1.36, first paragraph). RPT-E3's phrase "the re-keys
  declared under GATE-06" therefore has no table to point at. Its anchor is now the **19 absolute
  `FROZEN_HASHES` literals** in `firestarter_app/tests/fixtures/report_shapes.py` plus the
  two-commit review rule carried in the oracle's own failure message. The planner states this
  substitution explicitly rather than citing a mechanism that no longer exists.

- **D-16:** **Phase 181 declares ZERO re-keys, asserted positively.** Every change in this phase
  falls outside `dedup_fingerprint`'s five-entry allow-list (`chip` | `protocol` |
  `op=verdict:classification` | `repeat_policy_tag` | `coverage_tag`): canonical naming is additive
  and `ac.chip` keeps the raw token (D-2); every RPT-B deletion is unhashed; `duration_s`, `elapsed`,
  `divergence`, `is_uv`, `chip_id_actual` and the fingerprint siblings are all unhashed;
  `schema_version` is never read by the hash; and D-09 leaves the `op=` component unmoved by
  construction. **All 19 frozen hashes must be byte-identical after this phase**, and RPT-E3's
  exception clause discharges as empty. This is the strongest closing claim the milestone can make
  and it is the phase's headline verification leg.

- **D-17:** **HYG-01 bounds `syrupy` to `>=5.0,<7`** in `pyproject.toml`'s `test` extra (line 73,
  currently `syrupy>=5.0` unbounded). HYG-02 is asserted by pinning the runtime `dependencies` list
  (`pyproject.toml:46-53`) to exactly `pyserial, requests, tqdm, click, rich, packaging` — a test,
  not a claim.

- **D-18:** **HYG-03's decision is recorded in `MILESTONES.md`**, in the v1.36 section, in the same
  voice as the existing corrections: `dedup_fingerprint` must **never** be refactored to hash
  `to_dict()`, because every additive field would then re-key every historical report — the precise
  failure this milestone forbids, and the tempting cleanup that D-14's own additive changes would
  otherwise invite.

- **D-19:** **HYG-04 is a two-way edit, not an append.** Any new `dev_test` helper this phase
  introduces (the canonical-name selector is the likely one, if it lands as a handler-side helper)
  is added to `_HANDLER_FUNCTION_NAMES` (`tools/check_devtest_orchestrator.py:152-164`), **and
  `_resolve_write_scope` is removed from it** because D-09 deletes the function. The allow-list is
  not documentation: RESEARCH C-4 proved a violating helper in an unlisted function passes the gate
  with `EXIT=0`.

- **D-20:** **`slots_remaining` means "after this run".** `slots_total - slot_index - 1`, matching
  the wording the operator already reads (*"slots left on this part"*). It must be conditional on
  the write **actually having run** — a SKIPPED / saturated / refused write consumes nothing.

- **D-21:** **That same "did a write actually run" predicate is the fix for the UV ladder
  false-green.** One guard serves both folded defects: it corrects `slots_remaining` and it stops
  `build_db_diff`'s fourth arm (`diagnostic_report.py:403-405`) proposing
  `candidate for community-reported` for a run in which nothing was written. The fix is **not** a UV
  special case — the hole is pre-existing and reachable on any refused write.

- **D-22:** **The phase stops at the record.** Phase 181 delivers its 18 requirements, the four
  folded residuals, HYG-03's `MILESTONES.md` entry, D-16's zero-re-key statement, and the 18
  `REQUIREMENTS.md` checkbox/traceability flips. The beta cut, the `v1.36` tag and the three
  `.github`-only PRs to protected `main` are left to `/gsd-complete-milestone` and `/gsd-ship`,
  matching how v1.35 closed and keeping a verifier pass between the last code change and any
  outward-facing push. **Before `/gsd-ship`, local `beta` must be recreated from `origin/beta`** —
  `ship.md` anchors its audit range on `git merge-base beta HEAD`.

### Claude's Discretion

The operator did not open these; Claude disposed of them and records the disposition so the planner
does not re-derive it:

- **D-23:** **RPT-A5's shape is one additive `StepResult` field, `chip_id_detected: int | None =
  None`.** `_dispatch_id` (`chip_test.py:2744`) **already receives** `detected_id` from
  `operator.check_eprom_id` and throws it away on a pass — the field records the value it already
  has. `_chip_id_fields` (`cli_handlers.py:2189-2217`) then stops scraping
  `r.reason.rsplit("0x", 1)[-1]` and reads the field. The step's `reason` prose on a mismatch is
  **left unchanged** — it is the human sentence, and RPT-A1's own text forbids a companion
  provenance key or qualifier string. The field exports in `steps[]`, so it lands in
  `_STEPS_ELEMENT_0_KEYS` per D-14.

- **D-24:** **`canonical_part_number` is `None`-safe.** It reads `None` when the token resolves to
  no row. `dev test` refuses an unresolvable or non-`supported` chip before a report exists (16
  aliases are `chip_not_implemented`), so this is defensive rather than reachable — but the title
  builder must fall back to the raw token rather than render `None`.

- **D-25:** **No rounding rule is invented for the mean.** `duration_s` keeps its full float and the
  existing `submit._duration_text` formatter continues to own display precision, so the console
  table, the saved markdown and the filed body cannot disagree.

- **D-26:** **No comments.** `/workspaces/CLAUDE.md` §"Source code comments — hard rule" is absolute
  and covers `firestarter_app/tests/` as product source. Every rationale in this phase goes in a
  **docstring** (permitted, and how these modules already carry their reasoning), the plan
  `SUMMARY.md`, or the commit message. A plan may not override this and must not make "a comment
  exists" an acceptance criterion. Click docstrings are user-facing `--help` text and are not a
  home for design history.

### Folded Todos

Four residuals absorbed, all inside "the report describes only what the run knows":

1. **`.planning/todos/pending/2026-09-08-uv-ladder-flip-on-exhausted-slots.md`** (T-179-05) — a UV
   run whose slots are all spent reads `blank-check`/`write`/`verify` = `SKIPPED`, and
   `build_db_diff`'s fourth arm proposes the **same disposition a genuinely-verified PASS
   proposes**. Introduced as a forced consequence of Phase 179's UV-02 adjudication and left open.
   Fixed by D-21's guard. `resolves_phase: none` today — the planner updates it to `181`.
2. **`.planning/todos/pending/2026-09-08-slots-remaining-off-by-one-at-target-resolution.md`**
   (T-179-07) — measured on real hardware: a run that spent a slot printed *"256 of 256 slots left
   on this part"* while its own artifact said *"Slots spent this run: 1"*. Fixed by D-20.
3. **`.planning/todos/pending/2026-09-04-stale-uv-prompt-comment-in-cli-handlers.md`** — the
   `# ALWAYS WRITES` block at `cli_handlers.py:2331-2345` describes the reverted `260821-wna` prompt
   design in the present tense, contradicting `_resolve_write_scope`'s own docstring 40 lines below
   it and a test class (`TestUVWriteHasNoPrompt`) that pins the prompt's absence. Blocked twice
   before on "rewrite two `#` lines vs delete accurate prose"; **the hard no-comments rule settles
   it as delete the whole block.** Anything in it that is still true is either derivable from the
   code or belongs nowhere. Note D-09 deletes `_resolve_write_scope` and its docstring in the same
   phase, so the contradiction's other half goes too.
4. **`.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md`**
   (2026-08-05, owner `henols`) — **already fixed, verified in code.** `FP_MATCH` exists at
   `chip_test.py:143` and `build_db_diff`'s fourth arm reaches `_LADDER_COMMUNITY_REPORTED`; Phase
   177's D-4/D-6 `match` bucket closed it and nobody closed the todo. **Zero implementation** —
   move it to `.planning/todos/completed/` naming Phase 177 as the fixing phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap (read first)
- `.planning/REQUIREMENTS.md` — §"Report Fidelity" carries RPT-A1…A5, RPT-B1/B2, RPT-D1/D2,
  RPT-E1…E3, RPT-F1/F2 verbatim; §"Hygiene" carries HYG-01…04; §"Decisions taken at definition"
  carries **D-3 (schema 2.0), D-5 (same-commit SKILL.md), D-7 (the `locked_destructive`
  adjudication this phase performs)** and D-2 (additive canonical naming). The 18 v1 checkboxes and
  the 18 traceability rows are this phase's only requirement edits — **touch no other row.**
- `.planning/ROADMAP.md` §"Phase 181: Report Fidelity — Schema 2.0, Canonical Naming & Hygiene
  Close" — the five success criteria. Also §"The one hard ordering constraint" and the
  **"operation counts, never seconds"** house rule.

### The record that governs the close — read before writing any verify block
- `.planning/MILESTONES.md` §"v1.36 Frozen-Shape Blast Radius", **first paragraph**. Three
  corrections are aimed by name at *"a phase 180/181 plan"*: the re-key ledger protocol is
  **RETIRED** (no ledger row for this phase, and `tools/rekey/check_rekey_ledger.py` **does not
  exist** — a plan copying the eight-leg ritual invokes a deleted script); the green-tree ritual is
  **seven** legs, not eight; and the app suite floor is **2239**, not the 2242 recorded in Phase
  179's plans. This is also where HYG-03's decision (D-18) and D-16's zero-re-key statement land.
  Line-pinned citations from the 174-179 records no longer land where they did — read them against
  `git show f81b1e8b^:.planning/MILESTONES.md`, not the current numbering.

### The invariance oracle this phase must leave unmoved
- `firestarter_app/tests/fixtures/report_shapes.py` — `SHAPE_IDS` (19) and `FROZEN_HASHES`, the
  absolute-value table D-16 asserts. Note `m27c512-full-canonical-name` (`776846bf2dc8`) and
  `m27c512-full-comma-joined-name` (`37ad34d39a19`): Phase 174 froze **D-2's rejected alternatives**
  precisely so a phase that normalizes `parts[0]` reddens against a row naming the consequence.
  Every builder uses `write_scope="full"`.
- `firestarter_app/tests/test_blast_radius_invariance.py` — the six key-list pins D-14 moves
  (`_TO_DICT_KEYS`, `_VOLTAGE_KEYS`, `_BANNER_KEYS`, `_AUTO_CAPTURE_KEYS`,
  `_STEPS_ELEMENT_0_KEYS`, and the two that do not move), the `SCHEMA_VERSION == "1.8"` assertion at
  `:517`, and the surviving two-commit review rule in the failure message at `:278-280`.
- `firestarter_app/tests/fixtures/part_number_delta.json` — GATE-04's measured artifact.
  `aggregate` carries the numbers D-01/D-02/D-04 rest on: 953 distinct aliases, 942 differing from
  their `part_number`, **514 resolving to a comma-joined value**, 234 rows with a comma, 43 rows
  with parens, 16 `chip_not_implemented`. `filed_issues` carries all 26 raw-token → `part_number`
  pairs.
- `firestarter_app/tests/fixtures/devtest_issue_corpus.json` — the 26 filed issues as historical
  evidence. **Never rewritten** (D-04).

### Prior-phase records that bound this phase
- `.planning/phases/180-read-step-sampling-conditional-on-phase-176/180-CONTEXT.md` — the seven-leg
  green-tree battery, the py3.11 venv rule and the ugrep warning, all still in force.
- `.planning/phases/178-fault-attribution-the-two-axis-vocabulary/178-CONTEXT.md` — D-07 took
  `SCHEMA_VERSION` to `1.8` and explicitly said *"Phase 181 still takes it to `2.0` on its
  deletions"*; D-08 documents that `dedup_fingerprint` builds from an explicit five-entry allow-list
  with **no reflection over dataclass fields**, which is why D-16's additive changes cannot re-key;
  D-11 records that `is_submittable` is byte-unchanged and must stay so.
- `.planning/phases/177-evidence-gated-read-back/177-READBACK-INVENTORY.md` — the
  *measured-empty / named-and-excluded* closing form, and the `read_eprom` census that reddens if a
  third call site appears.
- `.planning/phases/179-uv-slot-writes-flag-skip-blank-check-hardware-gated/179-MEASUREMENT.md` —
  the bench run that produced the `slots_remaining` off-by-one (D-20) and the ladder flip (D-21).

### Product source this phase edits
- `firestarter_app/firestarter/diagnostic_report.py` — `SCHEMA_VERSION` (`:50`),
  `dedup_fingerprint` (`:263`), `build_db_diff`'s four arms (`:375-410`), `AutoCapture` (`:78`),
  `DiagnosticReport` (`:630`), `_voltage_dict` (`:733`), `_step_dict` (`:786-845`), `_banner_dict`
  (`:848-855`), `to_dict` (`:886`), `render`'s `chip_id` row (`:955-968`) and the "steps total" row
  (`:995-1007`).
- `firestarter_app/firestarter/chip_test.py` — `Fingerprint` (`:154`, already carries all four
  siblings), `Plan` / `locked_destructive` (`:498-515`), `derive_plan` (`:540`), `StepResult`
  (`:1096`), `_aggregate_cycle_results` (`:1360`), `sdp_oracle_applicable` (`:2013`),
  `WriteTarget.slots_remaining` (`:2388`), `_dispatch_id` (`:2744`), `_dispatch_read` (`:2767`),
  `slots_remaining=` (`:3014`), `BannerCounts` / `count_applicable` (`:3690-3731`).
- `firestarter_app/firestarter/cli_handlers.py` — `_chip_id_fields` (`:2189`), `_make_sampler`
  (`:2230`), `_is_uv_eprom` (`:2257`), `_resolve_write_scope` (`:2272`, **deleted**), the
  `# ALWAYS WRITES` block (`:2331-2345`, **deleted**), `derive_plan` call site (`:2403`), the
  report heading (`:2497`).
- `firestarter_app/firestarter/submit.py` — `build_title` (`:174`) and its one caller (`:698`);
  `_duration_text` / `_runs_text` / `_reason_text`, imported by `cli_handlers` so the two tables
  cannot disagree.
- `firestarter_app/pyproject.toml` — `dependencies` (`:46-53`, HYG-02), `syrupy>=5.0` (`:73`,
  HYG-01).
- `tools/check_devtest_orchestrator.py` — `_HANDLER_FUNCTION_NAMES` (`:152-164`, HYG-04, D-19).
- `.claude/skills/devtest-triage/SKILL.md`

  ## Status: Phase 181 amendment

  **2026-09-09, measured correction (plan 181-09).** This bullet previously instructed
  the planner to treat the skill's `:375` example row as the report's own field and to
  rewrite it with the deleted key's before/after replacements. That instruction is
  **wrong and is removed outright rather than annotated** — an annotated caveat still
  reads as the original instruction with a footnote, and a future reader could act on
  the footnoted half by mistake. Measured instead: the `:375`
  row sits inside the datasheet-versus-database cross-check table (`### 5c. Cross-check
  the datasheet against what firestarter believes`), whose firestarter-side column reads
  the `VPP:` line from `firestarter info -a <chip>` — so its value is the **DATABASE's**
  programming voltage for the part, a different field that happens to share a name with
  the report's deleted key. Rewriting it as a rail reading would turn a correct row into
  a false one. The report's own rail fields are named separately, in the sentence at
  `:330` (*"Voltage sanity from the report itself..."*), and RPT-F2 is discharged by
  extending THAT sentence — naming all four before/after fields, stating plainly they
  are regulator-rail readings never socket readings, and adding the pre-2.0 note —
  while the `:375` example row stays byte-unchanged. The leg that proves it: Task 1's
  skill-diff verify leg in `181-09-PLAN.md` fails if that row is added to or removed
  from the file. Full measurement and column-structure evidence:
  `evidence/181-09-skill-same-commit.txt`.

  **D-5's two-repo residue, stated once here rather than glossed:** one commit across
  two git repositories is structurally impossible. The criterion is discharged as two
  commits landing inside one task (plan 181-09 Task 1) with cross-referencing commit
  messages, skill first — so this record does not claim a literal same-commit that did
  not happen.

  Its two frozen fixtures under `.claude/skills/devtest-triage/fixtures/` carry
  `"schema_version": "1.2"` / `"1.4"`, `"locked_steps": []`, `"vpp_mv": 11800` and
  `"vpe_mv": 13700` — these are **RPT-E2's forward-only parse targets** and their
  headers forbid regeneration.

### Project rules (non-negotiable)
- `/workspaces/CLAUDE.md` §"Source code comments — hard rule" — D-26.
- `/workspaces/CLAUDE.md` §"Milestone close and branch protection" — `main` protected in all three
  repos, `current_user_can_bypass: never`; this project's base branch is `beta`.
- `.planning/notes/v135-close-procedure-under-protection.md` — the close mechanics D-22 defers to.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets — several requirements are smaller than they read
- **`Fingerprint` (`chip_test.py:154-161`) already carries `total`, `bad`, `bad_pct` and
  `evidence`.** RPT-A2 is a **serialization change only** — `_step_dict` currently emits
  `result.fingerprint.classification` as a bare string (`diagnostic_report.py:832-834`). No new
  computation.
- **`_dispatch_id` already receives `detected_id`** from `operator.check_eprom_id`
  (`chip_test.py:2745`) and discards it on a pass. RPT-A1 and RPT-A5 are one additive field between
  them (D-23), not a new firmware read.
- **`Plan.is_uv` already exists** (`chip_test.py:515`), decided exactly once by `derive_plan`
  (`:591`). RPT-A4 is a carry-through to `to_dict()`; the re-derivation D-09 deletes is the
  duplicate at `cli_handlers.py:2257`.
- **`render()` already dropped the `vpp_mv`/`vpe_mv` rows** — only `to_dict()` still emits them, so
  RPT-B1 is a dataclass + `_voltage_dict` + schema change with no console consequence.
- **`get_eprom_config`'s exact-then-paren-stripped ladder** (`database.py:466-485`) is the
  normalization D-02 mirrors. Do not write a second one.
- **`tests/plan_corpus.py`** builds 1,354 real plans and is the natural home for any whole-database
  sweep this phase needs.

### Established patterns that constrain this phase
- **`dedup_fingerprint` builds from an explicit five-entry allow-list with no reflection over
  dataclass fields.** Exclusion is by construction, not by a filter that could be inverted — this is
  why every additive field in this phase is hash-safe, and it is what HYG-03 protects.
- **`repeat_policy_tag` / `coverage_tag` return `""` for the default case and the append is
  skipped.** The empty-default direction is load-bearing: it is how prior changes stayed
  byte-identical for already-filed reports. Any new discriminator must follow it.
- **Anti-vacuity discipline** — a gate is not trusted until observed RED against a planted
  counter-example, with the transcript recorded in the phase's `evidence/`. See
  `test_readback_inventory.py`'s planted legs and `test_blast_radius_invariance.py`'s recorded RED
  transcripts. Use the **in-memory string mutation** pattern; write no fixture files.
- **Absent data may never fabricate confidence** — `NOT_MEASURED` for an unwired counter,
  `duration_s=None` rather than `0.0` for a step that did not run. D-05 and D-24 both inherit this.
- **`to_dict()` is hand-written, never `dataclasses.asdict()`** (Pitfall 3) and is the one place
  `schema_version` is baked in and `NOT_MEASURED` substituted.

### Integration points
- `tools/check_devtest_orchestrator.py`'s allow-list is a **fail-open** gate: a violating helper in
  an unlisted function passes with `EXIT=0`. D-19 is therefore load-bearing, not bookkeeping.
- `parse_devtest_issue.py` and the `devtest-triage` skill both consume the report body; both accept
  `schema_version` **by presence only** (a live fixture carries `"9.9-future"`).
- `count_agreeing` reads the `dedup_fingerprint` **embedded in a filed issue body** and never
  re-hashes — which is why D-16's zero-re-key claim matters and why a re-key would be permanent.
- No `chip_database.json` change. It is **generated**; never hand-edit it.

### Environment notes for whoever runs the gates
- Use **`firestarter_app/.venv311/bin/python`**. The devcontainer default is 3.12 and app CI runs
  **3.11 only** — a divergence that has already broken beta CI once.
- The green-tree battery is **seven** legs: `ruff check` and `ruff format --check` on
  `firestarter/ tests/`, `tools/check_mypy_watermark.py` (watermark 35),
  `tools/snapshot_report_shapes.py --check`, `tools/check_devtest_orchestrator.py`,
  `tools/check_diagnostic_report_claims.py`, and the full suite (floor **2239**).
- `pytest` addopts are `-ra -q`; a count line needs `-o addopts=""`.
- `grep` in this devcontainer is **ugrep** and honours `.gitignore`, silently under-scanning. Use
  `/usr/bin/grep` for any evidence-grade scan.
- `tests/test_skip_census.py`'s three failures are **pre-existing** (a 180 s child-run timeout cap
  against a ~741 s suite), unrelated to anything this phase touches.

</code_context>

<specifics>
## Specific Ideas

- **The alias rule, stated the way RPT-F1 demands.** *"`canonical_part_number` is the alias within
  the matched row's `part_number` that equals the operator's raw token under the same normalization
  `get_eprom_config` used to match it; when no alias matches, the first alias in the list. The
  alias is carried verbatim, including any parenthetical mode annotation."* That sentence is the
  deliverable — RPT-F1 asks for a **stated** rule, so it belongs in a docstring and in the phase
  `SUMMARY.md`, not only in code.

- **The one comparison that makes the `elapsed` change legible.** On the same run, the old
  "steps total" row and the new `elapsed` differ by the connects, the database load and the identity
  read. Showing both numbers once, in the phase record, is what demonstrates the old row was
  under-reporting rather than merely being replaced. Per the house rule, present it as **what the
  row excluded**, not as a second-count acceptance criterion.

- **Lead the closing document with D-16, not with the field list.** "Eighteen requirements landed and
  all nineteen frozen hashes are byte-identical" is a stronger closing sentence than any enumeration
  of added keys, and it is the claim the whole milestone was scoped around. Mirror
  `177-READBACK-INVENTORY.md`'s "PRUNE-04's closure" form: state the verdict, name what is excluded,
  give the reason, and say which gate would redden if the situation changed.

- **D-08 is the phase's risk concentration; treat it that way in the plan.** It is the only decision
  taken against the recommendation, it touches an exit-code path Phase 178 just changed, and its
  blast radius is ~110 test sites. It deserves its own plan and its own wave, ahead of the
  smaller additive work, so a failure there is isolated rather than entangled with RPT-A.

</specifics>

<deferred>
## Deferred Ideas

- **Exposing the gap between `elapsed` and the sum of step durations** — the connect and
  database-load overhead MEAS-01 measured. Raised at the duration gate and not opened. It would be a
  derived field, and RPT-D2 asks for the sum row's **removal**, not its replacement by a second
  derived number.
- **Size-gated read sampling for parts ≥512 KiB** — carried forward from Phase 180's deferred set.
  The operator declined it as both a ship option and a re-file option (180 D-01/D-05). Deliberately
  **not** a requirement, backlog item or todo. A future attempt starts from
  `180-PRUNE-08-CLOSURE.md` and 180 D-11's `_read_region` note.
- **R4-01 — `EpromOperator` leasing one validated link per plan.** Already filed in
  `.planning/REQUIREMENTS.md` §Future Requirements. Named here only because it is the change that
  would invalidate Phase 180's close; this phase adds nothing to it.
- **The 999.44 firmware half** — region-scoped `mem_util_blank_check`. Out of scope for a host-only
  milestone, and the product-level bug stays open knowingly.

### Reviewed Todos (not folded)
`todo.match-phase 181` returned **41 matches**. Four were folded (see `### Folded Todos`); the rest
are keyword artefacts or belong elsewhere. The highest-scoring, recorded so a future phase knows
they were considered and rejected here:
- *Strip residual GSD provenance comments from product source* (0.6) — a repo-wide sweep, ~463 open
  lines in the app. This phase deletes exactly one such block, the stale `ALWAYS WRITES` comment,
  because it is a **false statement about current behaviour** in a file this phase edits — not as a
  down payment on the sweep. The sweep stays its own task.
- *Report the chip's exact database name in `dev test` issues, artifacts, and tests* (0.6) — this is
  RPT-F1 itself and its `resolves_phase` is already `181`. Its proposed solution (putting the
  canonical name **into** `AutoCapture.chip`) is **superseded by D-2** and must not be followed;
  its two open sub-questions are answered by D-01 and D-02, and its test-sweep ask is refused by
  D-04. The planner marks it resolved by this phase, not implemented as written.
- *Add a `dev test` flag that files the issue automatically* (0.6) — a new CLI capability; its own
  phase.
- *`dev test m27c512` passes on a non-blank UV part while `firestarter write` is still refused*
  (0.6) — the 999.44 product-level inconsistency, firmware half, out of scope above.
- *Write-init blank check scans the whole device* (0.6) — the same 999.44 firmware defect.
- *`MAX_27C020_SIZE` parity test is a tautology* (0.6) — a real finding about a fake firmware-parity
  gate, unrelated to the report.
- *Separate the `.gitignore` classes* (0.6) — meta-repo tooling.

</deferred>

---

*Phase: 181-report-fidelity-schema-2-0-canonical-naming-hygiene-close*
*Context gathered: 2026-09-09*
