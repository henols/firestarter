---
phase: 154-provenance-comment-sweep-remap-tool-dual-repo-lockstep-promo
plan: "04"
subsystem: tooling
tags: [citation-manifest, jsonl, path-resolution, fixture-collision, fail-closed, reconciliation, tdd, remap-input]

requires:
  - phase: 154-01
    provides: "FW_PRE_SHA=8695ee5 / APP_PRE_SHA=6bfa645, both sub-repos branched off beta — the pre-sweep identification written into the manifest header"
  - phase: 154-02
    provides: "survey_provenance.py — the corpus authority this plan CALLS for the candidate set and each candidate's first-hit line, never re-implementing its regex; plus sweep-gate-dispositions.md §C's Ruling B follow-on question"
provides:
  - ".planning/v1.33/sweep-citation-manifest.jsonl — 13,692 records / 2,947 planning documents / 171-file candidate set, generated at the pre-sweep shas and NOT reconstructible after the sweep. The only interface between Phase 154 and Phase 159 (REMAP-01..05)"
  - ".planning/v1.33/tools/citation_paths.py — the SINGLE shared five-step resolver, imported by both the generator and plan 05's remap_citations.py so no citation can resolve two different ways"
  - ".planning/v1.33/tools/build_citation_manifest.py — the generator: four live variants, the D-07 schema plus five stated additions, a stated JSONL convention, atomic write, fail-closed on zero records, and a --stats block carrying every figure the reconciliation needs"
  - ".planning/v1.33/tools/test_build_citation_manifest.py — 26 legs covering all six resolution classes, the fixture guard, all four variants, both-endpoint ranges, idempotency and the exit-2 leg"
  - ".planning/v1.33/sweep-citation-manifest-report.md — the Ruling G reconciliation against 10,054 / 9,989 / 6,939 / 6,928 / 627 / 665 / 1,351 / 160 / 401, every delta explained or explicitly marked unexplained"
affects: [154-05, 154-06, 154-07, 154-08, 154-09, 154-10, 154-11, 154-12, 159]

tech-stack:
  added: []
  patterns:
    - "One resolver, two tools: factor the ambiguity-resolution rule into a shared module so a generator and its consumer cannot disagree about the same input"
    - "A rule the real tree cannot exercise is proven against a synthetic index that CAN — the correction for 'a pre-authored gate leg can be unreachable'"
    - "source_text is never null: an unreadable endpoint carries a declared sentinel plus a text_status, so a downstream oracle skips the row BY NAME instead of failing open on a null"
    - "No timestamp anywhere in a generated artifact — that alone is what makes byte-identical regeneration provable"
    - "Records vs occurrences stated explicitly before any count is compared, because a list-expanding extractor is not comparable to an occurrence census"

key-files:
  created:
    - .planning/v1.33/tools/citation_paths.py
    - .planning/v1.33/tools/build_citation_manifest.py
    - .planning/v1.33/tools/test_build_citation_manifest.py
    - .planning/v1.33/sweep-citation-manifest.jsonl
    - .planning/v1.33/sweep-citation-manifest-report.md
  modified:
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md

key-decisions:
  - "The resolution index is the CANDIDATE set (171 files), exactly as the plan specifies — so `unresolved` means 'does not target a candidate swept file', and every citation found is still emitted as a row with its resolution. Research's ambiguity/unresolved figures were measured against a ~401-file whole-tree index and are therefore not directly comparable; the report bridges them with a whole-repo diagnostic index rather than restating either number"
  - "`rejected` added as a distinct SIXTH resolution class, kept apart from `unresolved`, because the plan's own behaviour text calls a root-escaping path 'rejected' and a reader must be able to tell 'escapes the roots' from 'names nothing in the candidate set'"
  - "source_text/source_text_end are NEVER null; an unreadable endpoint carries the declared `<UNREADABLE>` sentinel and text_status/text_status_end say why. Forced by the requirement that EVERY range record carries both texts — a null would fail that assertion for every unresolved or past-EOF range, of which there are 255 + 2,978"
  - "`anchor_L` emitted under two labels (anchor_L point / anchor_L_range) so 'is this a range record?' is answerable from the variant alone; their sum is research's 407 figure"
  - "The fixture-exclusion rule is DEFENCE IN DEPTH on this tree, not the load-bearing disambiguator research predicted — the colliding fixtures live under firestarter/tests/ (plural), outside the sweep globs, so they never enter the candidate set. Recorded as a correction to research's 639-of-665 expectation, and the rule is kept PROVEN by a synthetic fixtures-inclusive index rather than by an unreachable real-tree leg"
  - "The fixture GUARD is scoped to the fixture-excluded basename step only, where an incorrect index is the bug it detects; an exact or suffix citation that legitimately names a fixture file resolves normally, and a basename carried ONLY by a fixture resolves via an explicitly-labelled fallback rather than becoming a false `unresolved` (4 rows took that path)"
  - ".planning/v1.33/tools/ is excluded from the scan by declared prefix: 12 citation-shaped literals live there and all 12 are illustrative or unit-test-fixture strings, so without the exclusion Phase 159 would rewrite the exact fixtures the generator's own tests assert on"
  - "COMMITTED in this plan, departing from the plan text's task-3 'do not commit' line, on the orchestrator's explicit instruction: D-11's one-commit-per-sub-repo rule constrains the SUB-REPOS, and the manifest is a meta-repo artifact. Plan 03's uncommitted firestarter_app changes were left untouched"
  - "ROADMAP.md / REQUIREMENTS.md / STATE.md hand-edited only; roadmap.update-plan-progress and the requirements verbs were NOT run, per this milestone's binding constraint carried from plans 01-03"

patterns-established:
  - "Bridge the units before comparing the numbers: publish both the record count and the occurrence-equivalent count, because a colon_list-expanding extractor reads as +147% against an occurrence census when the real delta is +0.7%"
  - "When a measured result contradicts the research expectation the plan quotes, report the contradiction as the finding — research's 639-of-665 fixture-disambiguation claim did not reproduce because it was measured against a different index"
  - "Verify a generated artifact against its own source of truth, not only against its own schema: all 10,190 readable rows re-checked byte-for-byte against the on-disk source lines"

requirements-completed: [SWEEP-09]

coverage:
  - id: D1
    description: "citation_paths.py: the five-step rule plus a distinct rejected class, explicit roots, no __file__-derived scan root, the declared fixture-exclusion globs, and the T-154-13 guard"
    requirement: "SWEEP-09"
    verification:
      - kind: integration
        ref: "python3 .planning/v1.33/tools/citation_paths.py --fw-root /workspaces/firestarter --app-root /workspaces/firestarter_app --self-check -> exit 0, 8/8 probes in their expected class against an index of 171 candidate swept files, per-resolution breakdown printed"
        status: pass
      - kind: unit
        ref: "grep -c '_HERE' .planning/v1.33/tools/citation_paths.py == 0; the literals '**/fixtures/**' and '**/fixture/**' present"
        status: pass
      - kind: unit
        ref: "test_resolve_bare_basename_skips_planted_fixture / test_resolve_firestarter_h_is_not_the_fake_fixture / test_resolve_suffix_tie_is_broken_by_fixture_exclusion / test_fixture_guard_raises_on_fixtures_inclusive_index — the collision trap in all three forms plus the guard, against a synthetic index that DOES contain the firmware planted fixtures"
        status: pass
      - kind: unit
        ref: "test_resolve_parent_traversal_is_rejected / test_resolve_absolute_path_is_rejected — recorded, not raised, not opened (T-154-12)"
        status: pass
    human_judgment: false
  - id: D2
    description: "build_citation_manifest.py: all four live variants, colon_list as independent points, both endpoints AND both texts on every range, retarget:false, byte-identical regeneration, exit 2 on zero records"
    requirement: "SWEEP-09"
    verification:
      - kind: unit
        ref: "python3 -m pytest .planning/v1.33/tools/test_build_citation_manifest.py -q -> 26 passed (>=8 required); 4 variant-named legs present"
        status: pass
      - kind: unit
        ref: "test_variant_colon_list_yields_two_independent_records (exactly 2 records, both target_line_end None); test_range_record_carries_both_endpoints_and_both_texts; test_backticked_wrapper_is_not_a_fifth_variant"
        status: pass
      - kind: unit
        ref: "test_regeneration_is_byte_identical; test_zero_record_input_exits_two (exit 2); test_header_record_is_first_and_self_describing"
        status: pass
      - kind: unit
        ref: "grep -c '_HERE' build_citation_manifest.py == 0; 'import citation_paths' present; 'fixtures/**' ABSENT (the rule lives in one place only); meta_root is a required positional"
        status: pass
    human_judgment: false
  - id: D3
    description: "The pre-sweep manifest exists, is valid JSONL with a self-describing header, and every row carries the required keys with all ranges double-ended and all rows retarget:false"
    requirement: "SWEEP-09"
    verification:
      - kind: integration
        ref: "the plan's own verify script over the artifact -> 'rows 13692', every required key present, every colon_range/anchor_L_range record non-null on target_line_end AND source_text_end, every record retarget:false, row count > 5000"
        status: pass
      - kind: integration
        ref: "header record carries schema_version, record_keys, source_text_convention, the <UNREADABLE> sentinel, candidate_set, ordering_resolution, resolution_rule, variants, retarget, generating_command, pre_sweep_shas (8695ee52... / 6bfa6453...) and counts"
        status: pass
      - kind: integration
        ref: "independent fidelity oracle: all 10,190 records with text_status 'read' re-checked line-by-line against the on-disk source -> 10,190 match / 0 mismatch"
        status: pass
      - kind: integration
        ref: "byte-identical regeneration on the REAL tree: two identical-argv runs both md5 34abd50c2d2ea3bfe21271b1216276ab, --stats output identical"
        status: pass
    human_judgment: false
  - id: D4
    description: "Ruling G: the produced count reported with its verbatim command and reconciled against every recorded figure, with the ambiguous and unresolved counts reported rather than dropped"
    requirement: "SWEEP-09"
    verification:
      - kind: integration
        ref: "grep for 10,054 / 9,989 / 6,939 / 627 / retarget in sweep-citation-manifest-report.md -> all present, each in a reconciliation row"
        status: pass
      - kind: integration
        ref: "per-resolution counts published: exact 2,094 / suffix 1,218 / basename 7,133 / ambiguous 10 / unresolved 2,978 / rejected 259, with the top-20 unresolved targets sampled and shown legitimate"
        status: pass
    human_judgment: false
  - id: D5
    description: "SWEEP-10's pre-sweep half: no citation silently dropped, every row retarget:false, plan 12 named as where the subset and its count land"
    requirement: "SWEEP-10"
    verification:
      - kind: integration
        ref: "13,692/13,692 rows retarget:false, asserted by the generator self-check and independently over the artifact; report §6 names plan 12 and states this is D-08's only manual work"
        status: pass
      - kind: manual
        ref: "the correctness of each D-08 retarget target is a per-citation judgment and is DEFERRED to plan 12 against the real diff — named here, not laundered into an automated leg"
        status: deferred
    human_judgment: true
---

# Phase 154 Plan 04: Pre-Sweep Citation Manifest + Shared Path Resolver Summary

The phase's one non-reconstructible deliverable now exists: **13,692 citation records** over
2,947 planning documents and a 171-file candidate swept-file set, generated at the pre-sweep
shas `8695ee5` / `6bfa645` and schema-validated, with **one** resolver shared by the generator
and plan 05's remapper so no citation can resolve two ways.

## What Was Built

**`citation_paths.py` — the single shared resolver.** Research F5's five-step rule in order
(`exact` → `suffix` → `basename` → `ambiguous` → `unresolved`) plus a distinct sixth class,
`rejected`, for a path that escapes the explicit roots. Roots are explicit arguments;
`grep -c '_HERE'` is **0**, so the `check_ledger.py` / `check_permitted_claims.py` fail-open
shape is *introduced*, not copied. A `--self-check` entry point resolves an 8-probe set
covering all six classes against the real candidate index and exits on the house 0/1/2
contract.

**`build_citation_manifest.py` — the generator.** All four live syntax variants in one
non-overlapping pass, with `colon_list` expanded to independent **point** records and
`anchor_L` split into point/range labels. Every range record carries `target_line`,
`target_line_end`, `source_text` **and** `source_text_end`. D-07's field list plus five
**stated** additions. Atomic write, and a serialize-then-scan self-check that exits 1 if the
written file violates its own schema and 2 if it produced zero rows.

**The manifest and its reconciliation report.** 7,192,847 bytes (≈444 KB packed), with a
self-describing `_schema` header carrying the schema version, the 14-key fixed order, the
`source_text` newline convention, the `<UNREADABLE>` sentinel and every `text_status`, the
candidate-set definition, the ordering resolution, the five-step rule, the variant table with
the backtick-wrapper note, the declared exclusions with their reason, the generating command,
and both sub-repo pre-sweep shas.

## Key Measurements

| Figure | This run | Recorded | Research | Δ vs recorded |
|---|---|---|---|---|
| Records / occurrences | 13,692 / 13,290 | — | 13,002 | +288 occurrences (+2.2%) |
| Targeting a candidate swept file | 10,445 / **10,169** | **10,054** | 9,989 | **+115 (+1.1%)** |
| Shifting subset | 7,249 / **7,076** | **6,939** | 6,928 | **+137 (+2.0%)** |
| `colon_single` / `colon_range` (occurrences) | 6,469 / 6,137 | — | 6,253 / 6,068 | +3.5% / +1.1% |
| `anchor_L` / `colon_list` (occurrences) | 408 / 276 | — | 407 / 274 | +1 / +2 |
| Resolution: exact / suffix / basename | 2,094 / 1,218 / 7,133 | — | — | — |
| Resolution: ambiguous / unresolved / rejected | 10 / 2,978 / 259 | — | 11 / 1,351 | see report §5 |
| Candidate files | **171** | — | 160 | +11, traced file-by-file |
| `eprom.cpp` rows (Ruling B) | 831 (648 bare basename) | — | **627** | +21 on the comparable form |

Four subtrees reproduce the recorded shifting figure **exactly** (`research/` 180,
`graphs/` 108, `quick/` 55, `PROJECT.md` 42). Every delta is explained by `.planning/` growth
on the meta side — the source trees are at the identical two shas research measured — plus an
11-file wider candidate set, itself traced to the 9 committed fixture files plan 02 already
explained and plan 03's 2 new hit-bearing ones. **One item is explicitly marked partly
unexplained**: the 1,073 / 955 / 1,351 spread on unresolved citations, which is a definitional
spread inside the recorded research rather than a discrepancy this run can close.

**Per Ruling G, no recorded figure was rewritten and no produced figure was quietly asserted
in its place.** Both stand, side by side, with the cause measured.

## Findings That Correct the Plan's Own Expectations

**1. The fixture-exclusion rule is defence in depth here, not the load-bearing
disambiguator.** The plan (via research) expected it to resolve **639 of 665** ambiguous
citations. Measured against the candidate index, `eeprom_28c.cpp`, `firestarter.cpp`,
`firestarter.h` and `uno_rurp_shield.cpp` were **never ambiguous** — their colliding fixture
copies live under `firestarter/tests/` (**plural**), which is outside the sweep globs
(`firestarter/{src,include,test}`, **singular**), so they never enter the candidate set at all.
Research's 665 was measured against a ~401-file whole-tree index, not against the set the rule
is applied to. The rule is kept, and kept *proven*: because the real tree cannot exercise it,
the unit test builds a synthetic index that deliberately **does** contain the planted-fixture
copies and asserts every leg — including that a fixtures-**inclusive** index makes the
T-154-13 guard raise. That is the correction for "a pre-authored gate leg can be unreachable".

**2. The measured ambiguous residue is 10, not 11.** `host_stubs.cpp` (9) and
`serial_read_mock.h` (1) reproduce research's prediction exactly; the predicted single
`__init__.py` does not appear, because no `__init__.py` in this candidate set carries a
provenance hit, so it falls to `unresolved`.

**3. The Ruling B follow-on answer is NO, confirmed by measurement.** Exempting
`src/proms/eprom.cpp` does not change the manifest's shape. Its 831 rows are generated because
it is a *candidate*; if it ends up untouched they become verified fixed points at Phase 159
rather than rewrites. The exemption changes only the **actual swept set** plan 12's staleness
marker names.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The `--stats` full-repo diagnostic index counted vendored build trees**
- **Found during:** Task 3, on first reading the diagnostic output
- **Issue:** `SKIP_DIRS` omitted `.pio`, `.venv` and `build`, so the whole-repo index used to
  classify unresolved citations was **3,420** files, of which **3,001** were vendored
  dependency copies (2,395 `.py` under `firestarter_app/.venv`, 606 `.c`/`.h` under
  `firestarter/.pio`). An unresolved citation matching a vendored copy was being reported as
  naming "a real repo file".
- **Fix:** extended `SKIP_DIRS` with the build/venv/cache set. Corrected index = **405** files
  against research's 401 — and the +4 is exactly plan 03's four new
  `firestarter_app/tests/fixtures/planted_*.cpp`, so the figure now reconciles to the file.
- **Files modified:** `.planning/v1.33/tools/build_citation_manifest.py`
- **Commit:** `9a78bc6d`

**2. [Rule 2 - Missing critical functionality] Per-variant counts were not comparable to the
figures they had to be reconciled against**
- **Found during:** Task 3
- **Issue:** the plan requires per-variant counts checked against research's four figures, but
  research counted *occurrences* while the manifest holds *records*. `colon_list` therefore read
  as **678 vs 274** (+147%) when the real delta is **276 vs 274** (+0.7%). Reporting the record
  count alone would have manufactured a false discrepancy in the phase's own reconciliation.
- **Fix:** `build_records` now also counts citation **occurrences** per variant; the header
  carries `citation_occurrences` and `by_variant_occurrences` beside `by_variant`, `--stats`
  prints both tables, and the report states the distinction before any comparison.
- **Files modified:** `.planning/v1.33/tools/build_citation_manifest.py`
- **Commit:** `9a78bc6d`

**3. [Rule 1 - Bug] A stale "zero cost" claim about the tool-directory scan exclusion**
- **Found during:** Task 3 self-review
- **Issue:** the exclusion's justification was measured **before** this plan's two tool modules
  existed, so the committed claim "zero real citations live under the excluded prefixes" was
  false by the time it was written.
- **Fix:** re-measured (**12** citation-shaped literals, all illustrative or unit-test-fixture
  strings), corrected in both the tool and the report, and the supersession recorded rather
  than quietly restated. It is the *stronger* justification: without the exclusion Phase 159
  would rewrite the exact fixtures the generator's own tests assert on.
- **Files modified:** `.planning/v1.33/tools/build_citation_manifest.py`,
  `.planning/v1.33/sweep-citation-manifest-report.md`
- **Commit:** `9a78bc6d`

### Deliberate Departures from the Plan Text

**1. The artifacts ARE committed in this plan.** Task 3's action says "Do NOT commit these
files to the meta repo in this plan — per D-11 the meta deliverables are committed once, by
plan 12." The orchestrator's execution instruction overrides this explicitly: *"The manifest is
a meta-repo artifact, so it **is** committed by this plan (D-11's one-commit-per-sub-repo rule
constrains the sub-repos, not meta)."* Followed the orchestrator. Reading that supports it:
research's own sequencing step 3 is "**Commit the manifest before the first sweep edit** — this
is what makes it a pre-sweep deliverable", and the sweeps are Wave 3. Leaving a 7 MB
non-reconstructible artifact uncommitted across eight further plans is the larger risk.

**2. Three schema fields beyond the plan's declared 11.** The plan lists 11 record fields;
the manifest carries 14. `resolution_reason` records *how* each ambiguous or basename case
resolved (the plan's own success criterion asks for "its decisions recorded", not only its
counts), and `text_status` / `text_status_end` are **forced**: the plan's verify script asserts
every range record carries a non-null `source_text_end`, which cannot hold for the 2,978
unresolved and 255 past-EOF ranges unless unreadable text carries a sentinel plus an
authoritative status. All three are declared in the header record as additions, not slipped in.

**3. A sixth resolution class.** The plan names five per-resolution counts; `rejected` is
emitted as a distinct sixth, because the plan's own task-1 behaviour text calls a root-escaping
path "rejected" and folding it into `unresolved` would destroy the distinction it asks to have
recorded. All six are counted in the report.

## Known Stubs

None. Every code path in both tools is exercised by a unit leg or by the real-tree run.

## Threat Flags

None. This plan writes no source in either sub-repo and adds no network, auth or schema
surface. The four threat-register mitigations that apply are implemented and tested:
T-154-12 (path traversal — `rejected`, recorded, never opened), T-154-13 (fixture binding —
index exclusion plus a raising guard, proven against a fixtures-inclusive index),
T-154-14 (silent discard — every citation is a row with a `resolution`; exit 2 on zero rows),
T-154-15 (partial write — temp file plus `os.replace`), T-154-16 (silent count adoption —
Ruling G reconciliation).

## What Plan 05 and Plan 12 Inherit

- **Plan 05 must import `citation_paths`, not re-implement resolution.** That is the whole
  reason the module exists; two resolvers would let the same citation bind two ways.
- **Plan 12 flips `retarget`, it does not extend the schema.** The field is present on all
  13,692 rows with the value `false` precisely so the post-sweep update is a value change to a
  committed 7 MB artifact rather than a re-emission.
- **Phase 159's oracle must honour `text_status`.** A row whose status is not `read` (3,247 of
  13,692: 2,978 unresolved, 259 rejected, 10 ambiguous — plus 255 resolved-but-past-EOF) must
  be skipped **by name**, never treated as a match. The sentinel is `<UNREADABLE>` and the text
  convention is "without the line terminator, compare against `splitlines()`".
- **`firestarter_app`'s working tree is untouched.** Plan 03's 4 fixtures + 2 modified test
  modules and the 7 pre-existing untracked files are all still uncommitted and intact, per
  D-11 and the plan's carried-forward note. `.planning/v1.33/baseline-pre-sweep.md` also remains
  deliberately uncommitted.

## Self-Check: PASSED

- `.planning/v1.33/tools/citation_paths.py` — FOUND
- `.planning/v1.33/tools/build_citation_manifest.py` — FOUND
- `.planning/v1.33/tools/test_build_citation_manifest.py` — FOUND
- `.planning/v1.33/sweep-citation-manifest.jsonl` — FOUND (13,693 lines)
- `.planning/v1.33/sweep-citation-manifest-report.md` — FOUND
- Commit `1f48b5d1` (task 1) — FOUND
- Commit `b56b88e6` (task 2) — FOUND
- Commit `9a78bc6d` (task 3) — FOUND
