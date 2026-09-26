# Phase 154: Provenance Comment Sweep + Remap Tool (dual-repo lockstep) — Context

**Gathered:** 2026-08-23
**Status:** Ready for planning

> **How this document was produced.** The operator declined the gray-area
> selection with *"if you want to discuss something that you can decide you can
> ask, otherwise I have full confidence that you know the right path forward"* —
> i.e. decide the mechanical gray areas, ask only what is genuinely
> operator-owned. Nothing here needed an operator ruling: every decision below is
> settled by a measurement taken during this session or by an existing project
> precedent, and each one carries that evidence inline. Two findings are new to
> this session and change the phase's shape; both are marked **NEW**.

<domain>
## Phase Boundary

Delete the GSD planning provenance stamped into source across both sub-repos,
condense the minority that carries load-bearing rationale into ordinary comments,
commit a pre-sweep citation manifest, plant a staleness marker, and **build** the
citation-remap tool.

**The remap is NOT applied in this phase.** Phase 159 applies it exactly once,
over the composite pre-154 → post-158 diff (D-01, milestone-level).

**In scope:** comment text in `firestarter/{src,include,test}`,
`firestarter_app/{firestarter,tests,tools}`; the manifest; the tool; the marker.
**Out of scope:** any change to code, any change to generated artifacts' output,
applying the remap, and every Phase 155–158 size reduction.
</domain>

<decisions>
## Implementation Decisions

### Triage policy — the substance of the phase

- **D-01: The triage is ONE mechanical decision procedure, not a three-way judgment call.** The writeup's three classes (bookkeeping / tombstone /
  rationale) are *outcomes*, not a procedure. Reading all 130 shipped-firmware
  hits this session shows the dominant operation is not "delete vs keep" at all —
  it is **strip the label, keep whatever sentence follows**. The procedure, applied
  per hit:

  1. Delete the provenance token(s) and their enclosing punctuation: `Phase N`,
     `Plan N`, `Plan N-NN`, `Task N`, `PNNN`, `<NNN>-CONTEXT.md`, and the
     requirement/decision IDs (`D-NN`, `LOCK-02`, `PGSZ-01`, `ERASE-04`,
     `LOOP-03`, `MERGE-04`, `TABLE-01`, `W-04`, `OD-3`, `BF-3`, `Q4`, `T-44-01`,
     `FIX-05`, `A-7`, `C-8`, `BASE-02`, `HOST-01`, `VPP-01`, `CFG-03`, `RCA-01`).
  2. Judge what remains:
     - **A sentence describing code that exists** → keep it, reflowed as an
       ordinary comment. **This is the majority case.**
     - **Nothing but connective punctuation** → delete the whole comment.
     - **A sentence describing code that is NOT there** (tombstone) → delete the
       whole comment.
  3. **Guard:** step 2 may never delete the only statement of a non-obvious
     invariant, trap, or fail-closed rationale. If stripping leaves it too terse
     to stand alone, reword it to stand alone — do not delete it.

  Worked against all five keep-examples the todo names
  (`eprom_params.cpp:61`, `uno_rurp_shield.cpp:109`, `database.py:580-630`,
  `flash_5v_page.cpp:101`, `json_parser.c:92`): all five land on "keep,
  reflowed". The procedure reproduces the intended answers without needing the
  three-way classification as an input.

  Measured shape of the corpus this rule runs over (shipped firmware
  `src`+`include`, 130 hits): **89** are `Phase`/`Plan`/`Task`-prefixed narrative
  (→ mostly keep-and-reflow), **24** are requirement-ID-prefixed, **15** are
  tombstones across both repos (→ delete outright).

- **D-02 (NEW): `CAP-0N` is EXEMPT — it is live cross-repo wire-protocol vocabulary, not planning provenance.** The survey regex's `CAP-0` alternation
  is a false-positive class. Evidence: `CAP-0N` names a protocol capability
  generation in *shipped host source* —
  `firestarter_app/firestarter/serial_comm.py:67-156`,
  `hardware.py:39,153`, `firmware.py:180` — and is referenced by 13 host test
  modules. Stripping it would destroy vocabulary that both repos and the wire
  protocol share.

  **Generalised as the exemption test:** a token that appears in **both** repos'
  shipped source is vocabulary, not provenance, and is exempt. Apply this test
  before stripping any token not on D-01's list.

  **Consequence — a no-touch region.**
  `firestarter_app/tests/test_cap03_ack_layout_parity.py:100-102` pins
  `_WIRE_LAYOUT_COMMENT = "[buffer_size u16 BE][hw_revision u8][ver_len u8][ver
  bytes][write_budget_s u16 BE]"` and asserts it **verbatim in the raw,
  un-stripped text** of `firestarter/src/firestarter.cpp`
  (`test_firmware_pack_order_comment_matches_the_wire_layout`, line 442). The
  CAP-01/CAP-02/CAP-03 wire-layout comment block at
  `firestarter/src/firestarter.cpp:177-195` is therefore **no-touch**. It is a
  gate fixture that happens to be spelled as a comment.

- **D-03: Requirement/decision IDs ARE provenance in shipped source and are stripped there — but are RETAINED in test files where the ID is the test case's traceability key.** In shipped source an ID resolves only against `.planning/`,
  which is precisely the coupling this phase exists to remove. In a test file the
  ID is the link that REQUIREMENTS.md traceability runs on (`Case 30 / ERASE-01`,
  `D-11 / BASE-02`) and deleting it would silently sever traceability that no
  gate would notice.

- **D-04: Test-file scope is NARROWED, and this is the phase's biggest re-shaping. 331 of 636 hits (52%) are in test files.** Measured this session:
  `firestarter/test/native` **216**, `firestarter_app/tests` **115** — against
  `firestarter/src`+`include` **130**, `firestarter_app/firestarter` **132**,
  `firestarter_app/tools` **43**. The writeup frames the corpus as "provenance
  stamped into shipped source"; just over half of it is not shipped source at
  all, and the byte-identical `uno` oracle covers **none** of the 331 (native
  tests are not in the `uno` build, and the host repo has no size oracle at all).

  So test files get the **narrow** treatment: **tombstone deletion and
  label-only-comment deletion only.** `Phase N` / `Plan N` narrative prefixes are
  stripped where a sentence follows; requirement/decision IDs stay (D-03). No
  reflowing of substantive test commentary — there is no oracle to catch a
  mistake.

  Named keep-in-full case: `firestarter_app/tests/scan_paths.py`'s module
  docstring. It is dense with `D-11`/`A-7`/`C-8`/`BASE-02`/`Phase 123 Plan 08`
  labels *and* it is the only written statement of the `firestarter` name-collision
  trap (one `..` from `tools/` hits the app's own package; two reach the sibling
  repo). Under D-01 step 3 this is keep-and-reword territory, not delete.

### Gate classification (Hazard 1) — resolved to 8 paths, not "~20 files"

- **D-05: the `ALL_CROSS_REPO_PATHS` list in `firestarter_app/tests/scan_paths.py` is the authoritative inventory, and it is exactly 8 paths.** (Referenced elsewhere as `scan_paths.py::ALL_CROSS_REPO_PATHS`; the label avoids the `::` because the decision-coverage gate's bullet parser permits only the one separator colon before the closing `**`.) The writeup's "~20 files
  under `firestarter_app/tests/`" is an over-count: 21 test modules *import*
  `scan_paths`/`fw_presence`, but they resolve those same 8 firmware paths. The
  inventory is committed, explicitly non-derived, and self-asserting
  (`assert len(CROSS_REPO_TOOL_RESOLVERS) == 11`). Use it; do not re-derive it by
  grep — the module's own docstring explains why a mechanical derivation
  re-creates the name-collision trap.

  Disposition of all 8:

  | Path | Hits | Disposition |
  |---|---|---|
  | `test/native/avr/_shared/sdp_bus_config.h` | — | **Generated** (`tools/gen_sdp_bus_config.py`) — generator rule; output untouched |
  | `test/native/avr/_shared/validation_matrix.h` | — | **Generated** (`tools/gen_validation_header.py`) — same |
  | `doc/PROTOCOLS.md` | — | Outside the sweep's file globs |
  | `include/firestarter.h` | yes | In sweep |
  | `src/proms/eeprom_28c.cpp` | **33** | In sweep — densest file in the corpus |
  | `src/firestarter.cpp` | 8 | In sweep, **minus** the D-02 no-touch region |
  | `src/json_parser.c` | 8 | In sweep |
  | `test/native/avr/test_dispatch/test_configure_memory.cpp` | yes | In sweep, narrow treatment (D-04) |

  Comment-sensitivity classification, **measured this session**:

  | Gate | Strips comments? | Negative control? | Verdict |
  |---|---|---|---|
  | `test_cap03_ack_layout_parity.py` | yes (`_strip_comments`, :123) — **but deliberately reads raw text for the pinned comment** | yes | **Comment-SENSITIVE by design** → D-02 no-touch region |
  | `test_json_key_parity.py` | no — but matches `_KEY_STRING_RE` PROGMEM declarations and `key_parsers[] PROGMEM = {…}`, both code constructs | yes — `planted_json_parser_key_string_drift.c`, `planted_json_parser_undispatched_key.c` | **Safe**, and already proven safe |
  | `test_revision_constants_parity.py` | yes | yes (28 fixture refs) | Safe |
  | `test_check_no_log_in_sdp_window.py` | in its `tools/` checker | yes (35 refs, incl. the comment-not-a-call control) | Safe |
  | `test_check_is_memory_cmd_no_ifdef.py` | yes | yes (25 refs) | Safe |
  | `test_sdp_table_parity.py` | **no** | **no** | ⚠ **See D-06** |
  | `test_dispatch_mirror.py` | **no** | **no** | ⚠ C++ leg needs a control; markdown leg is out of globs |

- **D-06 (NEW): `test_sdp_table_parity.py` is the one genuinely dangerous gate, and a LIVE collision already exists.** It does no comment stripping and ships no
  planted-violation fixture, so per
  `reference_firmware_renames_break_host_source_scanning_gates` a green run from
  it is not evidence. Two independent comment-blind mechanisms:

  1. `_PAIR_RE = \{\s*(0x..)\s*,\s*(0x..)\s*\}` (:120) counts `{addr, byte}`
     pairs. **`firestarter/src/proms/eeprom_28c.cpp:199-201` already contains
     three `_PAIR_RE`-shaped pairs inside a comment** — `{0x5555,0xAA},
     {0x2AAA,0x55}, {0x5555,0xA0}` in the `D-10 … this is a SAFETY property`
     block. They are currently *outside* the sliced initializer, so the gate does
     not see them today. Reflowing that block is exactly what could move them in.
  2. The slice itself is comment-blind: `source_text.index("{", match.end())`
     then a raw `{`/`}` depth count (:141-158). **A single `{` or `}` inside a
     comment placed between a table's declaration and its initializer
     mis-anchors the slice**, and the gate would then compare a wrong or phantom
     table — silently.

  **Requirement:** plant a violation against this gate and prove it goes RED
  *before* the sweep touches `eeprom_28c.cpp`, then prove it still goes RED after.
  Same treatment for `test_dispatch_mirror.py`'s `test_configure_memory.cpp` leg.

  This region is also where the comments are *most* valuable — the AT28C
  datasheet citation of record (Atmel doc0270 rev 0270L-PEEPR-2/09 §19 note 2,
  corroborated by Microchip DS20006432B §6.18 note 2), the C++
  internal-vs-external-linkage explanation for why the `extern` is load-bearing,
  and the D-10 safety property that distinguishes "lock the chip" from "prefix a
  byte write". Highest reflow risk and highest comment value coincide. Treat
  `eeprom_28c.cpp` as its own plan, not as one file in a batch.

### Manifest and the remap tool

- **D-07: The manifest records all 10,054 citations that target a swept file, not only the 6,939 predicted to shift.** The 6,939 figure is derived from a
  *pre-sweep prediction* ("at or below the file's first GSD comment"). Recording
  the full 10,054 lets Phase 159's oracle **prove** the other 3,115 did not move
  rather than assume it — for the cost of ~45% more rows in a generated file.
  Format: **JSONL**, one record per citation:
  `{planning_file, planning_line, target_file, target_line, target_line_end,
  source_text, source_text_end, retarget}`.
  Location: `.planning/v1.33/sweep-citation-manifest.jsonl`.
  Range citations record **both** endpoints and both texts (REMAP-03's
  precondition).

- **D-08: A citation pointing AT a comment line the sweep deletes is retargeted in the manifest, never silently dropped.** It becomes a record with
  `retarget: true`, the original cited text preserved, and the new target set to
  the first surviving code line the comment described. Phase 159's round-trip
  oracle then **skips these by name** instead of failing open on them. The size
  of this subset is unknown until the diff exists; **its count is a deliverable
  of this phase**, and it is the only manual work in the repair.

- **D-09: The remap tool lives at `.planning/v1.33/tools/remap_citations.py` with a sibling `.planning/v1.33/tools/test_remap_citations.py`.** Precedent:
  `.planning/v1.16/ledger/tools/check_ledger.py` + `test_check_ledger.py` — a
  milestone-scoped tool directory with its own unit test, one of 36 Python
  scripts already committed under `.planning/`. **Not** `firestarter_app/tools/`:
  that couples a meta-repo tool to the app's ruff/mypy watermark and to
  `test_flash_path_record_sync`'s whole-repo porcelain assertion, for no benefit
  (`pyproject.toml:94` is `packages = ["firestarter"]`, so `tools/` does not ship
  either way — the objection is coupling, not packaging).

  **The tool takes the repo root as an explicit argument and never derives it
  from `_HERE`.** Per
  `reference_check_permitted_claims_here_resolves_wrong_phase_dir`, a
  `_HERE`-derived root in a mis-sited checker scans nothing and exits 0 — the
  citation tool must not fail open the same way. It must exit non-zero on an
  empty input set.

- **D-10: Keep the D-01 split; the roadmap's sweep-last fallback is DECLINED.**
  The roadmap parks the reordering as available "if the split is rejected at
  `/gsd-discuss-phase 154`". Declining it: the measured justification stands (723
  citations would be remapped twice, 41% of that rework caused by four added
  `#include` lines), REMAP-04's close-blocking marker makes the staleness window
  structural rather than a promise, and one composite mapping avoids the
  range-shrinking hazard that composing four successive mappings would create.

### Sequencing and preconditions

- **D-11: Commit granularity — one commit per sub-repo plus one meta commit.**
  Firmware sweep = 1 commit in `firestarter`; host sweep = 1 commit in
  `firestarter_app`; manifest + tool + marker = 1 commit in the meta repo. Both
  sub-repo commits must land **before** the host suite runs —
  `test_flash_path_record_sync` asserts whole-repo porcelain
  (`reference_flash_path_record_sync_asserts_whole_repo_porcelain`).

- **D-12: Two preconditions must be discharged before the sweep's first edit.**
  Neither is a decision; both are blocking facts found this session.
  1. **The `firestarter` working tree is dirty** — 11 modified files on branch
     `size-reduction-survey`, whose diff is byte-for-byte
     `.planning/notes/firmware-size-reduction-measured.patch` (229 insertions /
     231 deletions, verified by `git apply --stat`). Those 11 files are the *same*
     files Phase 154 sweeps (`json_parser.c`, `eprom.cpp`, `flash_intel.cpp`,
     `flash_utils.cpp`, `memory.cpp`, `eeprom_28c.cpp`, `rurp_common.cpp`,
     `firestarter.h`, `memory_utils.h`, + 2 native tests). The byte-identical
     `uno` oracle requires a clean `beta` tree. The patch is the committed
     recovery record, so the working tree is safe to reset — **but that is the
     operator's call to make at execution time, not the planner's to assume.**
  2. **No `gsd/v1.33-*` branch exists in either sub-repo.** `firestarter` is on
     `size-reduction-survey` (0 ahead / 0 behind `beta`); `firestarter_app` is on
     `beta`. Per `feedback_branching`, fork the milestone branch off `beta` in all
     three repos before any edit.

### Claude's Discretion

The operator delegated the whole gray-area set. Everything above was decided
against a measurement or a precedent rather than a preference, so nothing here is
open. The two items that remain genuinely unknown until the diff exists — and are
therefore *deliverables*, not decisions — are D-08's retarget count and the
per-file keep/delete ratio.

### Folded Todos

- **`todos/pending/2026-08-22-sweep-gsd-provenance-comments-from-firmware-and-host-source.md`**
  (`resolves_phase: 154`) — the phase's full writeup, folded in its entirety. Its
  three hazards map to: Hazard 1 → D-05/D-06, Hazard 2 → D-07/D-08/D-09,
  Hazard 3 → SWEEP-05. Three of its stated figures are corrected by this session's
  re-survey: the gate count (~20 → **8** paths), the corpus split (52% is test
  files, not shipped source), and `CAP-0` being a survey false positive.

</decisions>

<requirements>
## SWEEP Requirements (settled here; REQUIREMENTS.md §1 placeholder resolves to these 13)

- **SWEEP-01**: The triage runs as D-01's single mechanical procedure, stated in
  the plan and applied per hit, with its three outcomes and the step-3 invariant
  guard named. All five keep-examples the todo names are shown to land on
  "keep, reflowed".
- **SWEEP-02**: `CAP-0N` is exempt as cross-repo vocabulary, justified by its
  presence in shipped host source, and the both-repos exemption test is applied
  to every token not on D-01's list. `firestarter/src/firestarter.cpp:177-195` is
  untouched, and `test_cap03_ack_layout_parity.py` is green **and** shown still
  able to fail.
- **SWEEP-03**: Requirement/decision IDs are stripped from shipped source and
  retained in test files where the ID is the case's traceability key. The rule is
  stated; the asymmetry is not left to look like an inconsistency.
- **SWEEP-04**: Test files receive the narrow treatment only (tombstone and
  label-only deletion). The 331-of-636 measurement and the fact that **no oracle
  covers any of them** are both recorded.
- **SWEEP-05**: The `uno` build is byte-identical before and after, stated as a
  **measured pair of numbers**, not asserted. Any delta is reverted, not
  explained.
- **SWEEP-06**: All 8 paths in `scan_paths.py::ALL_CROSS_REPO_PATHS` are
  classified and disposed of per D-05's table. The two generated headers are
  fixed at their generators or shown to need no fix; their output is not edited.
- **SWEEP-07**: `test_sdp_table_parity.py` and `test_dispatch_mirror.py`'s C++
  leg each get a planted-violation control proving they go RED, **before** the
  sweep and again after. The live `_PAIR_RE` collision at
  `eeprom_28c.cpp:199-201` and the comment-blind brace slice at
  `test_sdp_table_parity.py:141-158` are both named as the reason.
- **SWEEP-08**: `eeprom_28c.cpp` is swept as its own plan, not batched — 33 hits,
  the two comment-blind gate mechanisms, and the datasheet citation of record all
  land in one file.
- **SWEEP-09**: The pre-sweep citation manifest is committed at
  `.planning/v1.33/sweep-citation-manifest.jsonl`, covering all **10,054**
  citations that target a swept file, with both endpoints and both source texts
  for every range.
- **SWEEP-10**: Citations targeting a deleted comment line are recorded
  `retarget: true` with the original text preserved and a hand-chosen new target.
  None is silently dropped, and the subset's **count is reported**.
- **SWEEP-11**: `remap_citations.py` + `test_remap_citations.py` are committed
  under `.planning/v1.33/tools/`, proven **idempotent** (run twice = no-op) and
  proven to **shrink** a range spanning a deleted block rather than translate it
  by a constant offset, against synthetic diffs. It takes an explicit repo root,
  exits non-zero on an empty input set, and is **not applied**.
- **SWEEP-12**: The staleness marker is planted, naming the swept files, stating
  that `.planning/` citations into them are knowingly stale, and pointing at
  Phase 159 / REMAP-04 as the close-blocking closer.
- **SWEEP-13**: One commit per sub-repo plus one meta commit; both sub-repo
  commits land before the host suite runs. Whether editing archived
  `milestones/` records tripped
  `reference_milestone_close_breaks_record_gates` is recorded either way — the
  collision or its absence, with cause.

</requirements>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The phase's own writeup (read first)
- `.planning/todos/pending/2026-08-22-sweep-gsd-provenance-comments-from-firmware-and-host-source.md`
  — the full writeup; ROADMAP's entry and Backlog 999.34 are handles only. Three
  of its figures are corrected by D-04/D-05/D-02 above.

### Milestone scope and locked decisions
- `.planning/ROADMAP.md` §"v1.33 — Source Hygiene & Firmware Size Reduction"
  (lines 159–334) — D-01…D-05, the sequencing rationale, and the declined
  sweep-last fallback (D-10).
- `.planning/REQUIREMENTS.md` §1 (SWEEP) and §6 (REMAP-01…05) — §1's
  `SWEEP-01…NN` placeholder resolves to the 13 above; §6 is what this phase's
  manifest and tool must feed.

### The gate surface (Hazard 1)
- `firestarter_app/tests/scan_paths.py` — the committed 8-path inventory,
  `ALL_CROSS_REPO_PATHS`; also a named keep-in-full comment case (D-04).
- `firestarter_app/tests/fw_presence.py` — `FW_ROOT` / `fw_path`, how every gate
  resolves into the sibling repo.
- `firestarter_app/tests/test_sdp_table_parity.py` — the one uncontrolled
  comment-blind gate; `_PAIR_RE` :120, brace slice :141-158.
- `firestarter_app/tests/test_cap03_ack_layout_parity.py` — `_WIRE_LAYOUT_COMMENT`
  :100-102, raw-text assertion :254 and :442; defines the no-touch region.
- `firestarter_app/tests/test_json_key_parity.py` — the model for what a
  comment-safe gate with planted fixtures looks like.
- `firestarter_app/tests/test_dispatch_mirror.py` — uncontrolled; C++ leg in
  scope, markdown leg out of globs.

### Tool precedent
- `.planning/v1.16/ledger/tools/check_ledger.py` +
  `.planning/v1.16/ledger/tools/test_check_ledger.py` — the shape D-09 copies.
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py`
  — the `_HERE` fail-open D-09 must not reproduce.

### Do not disturb (Phases 155–158 territory)
- `.planning/notes/firmware-size-reduction-survey.md` and
  `.planning/notes/firmware-size-reduction-measured.patch` — the recovery record
  for D-12's dirty working tree. **This phase reads them; it does not apply
  them.**

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets
- **`scan_paths.py::ALL_CROSS_REPO_PATHS`** — replaces the writeup's "~20 files"
  guess with a committed, self-asserting 8-path list. The single highest-value
  asset for this phase.
- **`test_json_key_parity.py`'s planted fixtures**
  (`tests/fixtures/planted_json_parser_*.c`) — the existing pattern for proving a
  source-scanning gate can still fail. SWEEP-07's controls should copy this shape
  rather than invent one.
- **`.planning/v1.16/ledger/tools/`** — the `tool + sibling unit test under
  .planning/` layout, already committed and precedented.
- **`.planning/notes/firmware-size-reduction-measured.patch`** — verified
  byte-for-byte equal to the current dirty firmware tree, so D-12's precondition
  is recoverable rather than destructive.

### Established patterns that constrain this phase
- **Source-scanning gates fail OPEN.** A green run proves nothing; only a planted
  violation proves a gate still works. This is why SWEEP-07 exists.
- **Generated artifacts are fixed at the generator.** `messages.h`
  (`messages.toml` + codegen), `chip_database.json` (`build_db.py`),
  `sdp_bus_config.h` (`gen_sdp_bus_config.py`), `validation_matrix.h`
  (`gen_validation_header.py`). Never edit the output.
- **The `firestarter` name-collision trap.** `<app>/firestarter/` is the Python
  package; `<app>/../firestarter/` is the firmware repo. Any path the remap tool
  builds must be checked against this — `scan_paths.py` documents two independent
  live occurrences.
- **Whole-repo porcelain.** `test_flash_path_record_sync` fails on a dirty tree,
  which fixes commit ordering (D-11).

### Integration points
- The manifest is the **only** interface between this phase and Phase 159. If its
  schema is wrong, REMAP-02's oracle has no input and cannot be reconstructed.
- The staleness marker is the interface to REMAP-04's close block.

</code_context>

<specifics>
## Specific Ideas

- The condensed form of `firestarter_app/firestarter/database.py:580-630` (the
  Phase 121 D-12 / Phase 153 REVERSAL RECORD, ~50 lines) is called out in the
  writeup as "the single highest-value comment block in the repo". Under D-01 it
  is keep-and-reflow, and under step 3 it must still say that D-12's *policy* was
  right and its *premise* was wrong — otherwise the reversal gets re-reversed.
  Condense; do not compress to a one-liner.
- `eeprom_28c.cpp:176-202`'s datasheet citation of record (Atmel doc0270 rev
  0270L-PEEPR-2/09 §19 note 2 + Microchip DS20006432B §6.18 note 2) survives
  verbatim. A citation is not provenance.

</specifics>

<deferred>
## Deferred Ideas

- **⚠ Cross-phase flag for Phase 157 — found this session, not in scope here.**
  `test_json_key_parity.py:113` is
  `_KEY_PARSERS_TABLE_RE = re.compile(r"key_parsers\s*\[\s*\]\s*PROGMEM\s*=\s*\{(?P<body>.*?)\};")`.
  **DECODE-01 deletes `key_parsers[]`.** Phase 157 has no success criterion
  covering this gate, and the working-tree diff already carries
  `/* Phase-agnostic field table (replaces key_parser_t / key_parsers[]). */` at
  `json_parser.c:76`. Phase 157's discuss step should pick this up; it is a code
  change, not a comment change, so it is out of Phase 154's scope. Worth adding
  as a DECODE-08 at `/gsd-discuss-phase 157`.
- **A global citation gate.** The writeup notes none exists — the `check-claims`
  scripts under phases 130/146/149/152 are phase-scoped. SWEEP-11's tool is close
  to one but is deliberately a *remapper*, not a *checker*. Promoting it to a
  standing repo-wide citation gate is a real idea and its own phase; note it, do
  not build it here.
- **`reference_gsd_provenance_comments` as a lint.** Preventing recurrence — a
  hook or gate that rejects new `Phase N`-stamped comments in shipped source — is
  the obvious follow-on. Out of scope: this phase removes the debt, it does not
  install the brake.

### Reviewed Todos (not folded)

`gsd-tools query todo.match-phase 154` returned 20+ matches at a uniform score of
0.9, all matching on generic keywords (`phase`, `source`, `planning`, `2026`)
rather than on this phase's subject — the matcher has no signal here because
every todo in the repo mentions phases and planning. Reviewed and **not** folded:
`skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`,
`config-version-not-bumped-strands-stale-eeprom-calibration`,
`fm1608-byte0-write-never-lands-register-cache-elision`,
`fram-parts-ride-the-0x0d-handler-by-pinout-promotion`,
`onerom-pinout-external-corroboration-gate`, and
`phase-44-read-timing-knobs-missing-json-parse-reset`. All are behaviour or data
defects; this phase changes no code. The last one is worth naming: the writeup
cites it as the exact bug class that `json_parser.c:338`'s `D-05: page_size
resets to 0 exactly like chip_id` comment prevents — which is *why* that comment
is keep-and-reflow under D-01 step 3, not why the todo belongs here.

</deferred>

---

*Phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep*
*Context gathered: 2026-08-23*
