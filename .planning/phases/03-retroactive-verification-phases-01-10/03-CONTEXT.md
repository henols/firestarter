# Phase 3: Retroactive Verification (Phases 01-10) - Context

**Gathered:** 2026-05-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Back-fill 10 `NN-VERIFICATION.md` audit artifacts (one per v1.0 phase 01..10)
under `.planning/milestones/v1.0-phases/{NN-slug}/`, closing the 13 PARTIAL
audit findings from `.planning/milestones/v1.0-MILESTONE-AUDIT.md` and
satisfying ROADMAP Phase 3 success criteria SC#1-SC#4.

This is **a documentation pass over already-verified wiring**. The hard work
of "is the wiring correct" was done by `v1.0-INTEGRATION-CHECK.md` (22 WIRED
traces) and `v1.0-MILESTONE-AUDIT.md` (per-REQ partial-status evidence). The
v1.1 closure phases (Phase 1 SAF-04/05/06, Phase 2 WIRE-01/CLEAN-01/02) have
already re-touched the affected files. Phase 3 reads the source tree, the
integration check, and the audit; then writes 10 verification files in the
established format.

**In scope:**

- 10 new files at:
  - `.planning/milestones/v1.0-phases/01-database-pipeline/01-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/02-firmware-json/02-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/03-eprom-algorithms/03-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/04-flash-sector-erase/04-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/05-intel-flash/05-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/06-eeprom-page-write/06-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/07-chip-id-safety/07-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/08-integration/08-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/09-adapter-support/09-VERIFICATION.md`
  - `.planning/milestones/v1.0-phases/10-static-pins/10-VERIFICATION.md`
- File format: YAML frontmatter + 8-section body matching `11/12/13-VERIFICATION.md` and `01-VERIFICATION.md` (v1.1 Phase 1).
- Evidence: re-grep current source tree for each Observable Truth + Required Artifact + Key Link via `grep -n` / `git ls-files`; quote exact `file:line` matches.
- Cross-milestone closure pointers for v1.1 work that satisfied a v1.0 PARTIAL (SAF-04 → 05-VERIFICATION; SAF-05 → 06-VERIFICATION/07-VERIFICATION; WIRE-01 → 01-VERIFICATION REQ-DB-03; CLEAN-01 → 01-VERIFICATION + 02-VERIFICATION + 11-VERIFICATION cross-link).
- ROADMAP SC#3 explicit lock: 05-VERIFICATION.md records SAF-04 closure of REQ-SAF-01.
- ROADMAP SC#4 explicit lock: 10-VERIFICATION.md confirms `static_high_mask` end-to-end + `pins < 32` VPE_TO_VPP guard intact in current `memory.cpp`.

**Out of scope:**

- Re-running the full integration check (`v1.0-INTEGRATION-CHECK.md` is the source of truth — Phase 3 cites it; doesn't rebuild it).
- Re-running `pio test`, `pio run`, or `check_dispatch.py` for each verification file (already exercised by Phase 1 + Phase 2 verification; cited, not re-run, unless a specific Truth demands fresh execution).
- Fixing any defect surfaced by the verification pass — defects out of v1.1 scope go into `follow_ups` frontmatter, not new code. (WARNING-5 AT28C256 hazard stays deferred to v1.2; WARNING-4 test-script drift stays owned by v1.1 Phase 4 / HW-01.)
- Hardware-execution evidence (Phase 4 owns HW-01..HW-05).
- Authoring `MILESTONES.md` v1.1 entry (Phase 5 / DOC-01).
- Touching any source code in `firestarter/` or `firestarter_app/`.
- Updating `v1.0-MILESTONE-AUDIT.md` itself — Phase 3 produces new artifacts the audit's "gaps" block points to; the audit document is historical.

</domain>

<decisions>
## Implementation Decisions

### Scoring policy

- **D-01: Score each REQ against the current source tree, not v1.0-as-shipped.**
  ROADMAP SC#1 wording is "scoring its phase requirements against the current
  source tree". A REQ that was PARTIAL in `v1.0-MILESTONE-AUDIT.md` but has been
  closed by v1.1 work becomes **SATISFIED** in the retroactive VERIFICATION.md.
  The frontmatter `status` is therefore typically `passed`; v1.0 historical
  state is narrated in a "Cross-Milestone Closure" subsection inside the body,
  not in the score.

- **D-02: Cross-Milestone Closure subsection — mandatory when v1.1 closed a
  v1.0 PARTIAL.** Phases affected:
  - **01-VERIFICATION.md** — REQ-DB-03 was PARTIAL (wire-key `"vpp"` overloaded
    with millivolts). Closed by v1.1 Plan 02-01 (atomic flip to `"vpp_mv"`).
    Cite `firestarter_app/firestarter/database.py:518` (current state emits
    only `"vpp_mv"`) and `firestarter/src/json_parser.c:62,:74,:309` (current
    parser reads only `"vpp_mv"`). Forward-link Phase 2 (this milestone).
  - **02-VERIFICATION.md** — REQ-SER-02 (unknown-key skip) was PARTIAL only for
    verification-gap reasons. WIRED unchanged. No content change needed beyond
    citing `json_parser.c:316-318,:251-255`.
  - **05-VERIFICATION.md** — REQ-SAF-01 (Intel-flash VPP ADC compare). Was
    UNSATISFIED in v1.0. Closed by v1.1 Plan 01-01 (SAF-04). **SC#3 locks the
    record:** explicitly cite `flash_intel.cpp:25-50` (`flash_intel_check_vpp`)
    + call-site at `:77` + 6/6 Unity tests + `01-VERIFICATION.md` Truth #1.
  - **06-VERIFICATION.md** — REQ-FW-03 was PARTIAL (28C handler reachable but
    AT28C256 mis-tag = WARNING-5). The 28C *handler logic itself* is correct;
    score the REQ SATISFIED for what Phase 06 promised; carry WARNING-5 as a
    `follow_ups` entry (D-04).
  - **07-VERIFICATION.md** — REQ-SAF-02 was PARTIAL (WARNING-2: 28C ignored
    chip_id). Closed by v1.1 Plan 01-02 (SAF-05). Cite `eeprom_28c.cpp:55-77`
    (`eeprom28c_check_chip_id`) + call-site at `:82-83` + 4/4 Unity tests +
    `01-VERIFICATION.md` Truth #2.
  - **10-VERIFICATION.md** — REQ-FW-05 / REQ-FW-06 were PARTIAL only for
    verification-gap. **SC#4 locks the record:** `static_high_mask` end-to-end
    chain (`pinouts.json:"static-high-pins":[24]` → `database.py:get_bus_config`
    → wire `"static-high":[13]` → `json_parser.c:parse_bus_config` OR →
    `memory.cpp::mem_util_remap_address_bus`) AND `pins < 32` VPE_TO_VPP guard
    in current `memory.cpp::mem_util_calculate_top_address_register`. Both
    verified intact post-Phase-12.

- **D-03: Phase 08 (Integration, Rebuild & Verification) is the trickiest
  retroactive verification.** Phase 08's own scope was integration, rebuild,
  and verification — it didn't introduce REQs of its own; the audit mapped it
  to REQ-SAF-03 (blank-check gating). Score: 08-VERIFICATION.md focuses on
  REQ-SAF-03 (`flash3_write_init`, `flash_intel_write_init`,
  `eeprom28c_write_init` all call `mem_util_blank_check(handle)` under
  `!FLAG_SKIP_BLANK_CHECK`) + the v1.0 INTEGRATION-CHECK's regenerate-DB +
  CLAUDE.md updates evidence. Cross-link `v1.0-INTEGRATION-CHECK.md` and Phase
  12 verification rather than duplicating their content.

### Follow-up handling (open hazards)

- **D-04: WARNING-5 (AT28C256 active hazard) goes into `follow_ups`
  frontmatter on each affected file** (03, 06, 07 — the phases the audit
  cross-referenced) with severity `warning`, `in_scope: false`,
  `note: "Deferred to v1.2 per MILESTONES.md; upstream-DB classification
  issue, not a v1.0 Phase {NN} defect"`. The frontmatter pattern is taken
  verbatim from `11-VERIFICATION.md` (4-entry `follow_ups` block). REQ scoring
  stays SATISFIED — the v1.0 phase delivered what it promised; the hazard is
  an upstream-data + Phase 12 deferral question.

- **D-05: WARNING-4 (`firestarter_test.sh:31` + `write_test.sh:17` reference
  deleted `database_generated.json`) stays cross-referenced from
  08-VERIFICATION.md and 11-VERIFICATION.md.** Phase 4 (HW-01) owns the fix.
  Note in 08-VERIFICATION.md `follow_ups` with `in_scope: false`,
  `note: "Owned by v1.1 Phase 4 / HW-01"`. Don't fix it.

- **D-06: WARNING-1 / WARNING-2 / WARNING-3 are CLOSED in their affected
  VERIFICATION.md files** — they are not follow-ups. Use a "Cross-Milestone
  Closure" subsection that cites the closing v1.1 phase + commit + Unity test.
  Pattern: see `01-VERIFICATION.md` (v1.1 Phase 1) §"Post-Review Fixes".

### Format / depth

- **D-07: Use the established 8-section template** from `11/12/13/01-VERIFICATION.md`
  with YAML frontmatter:

  ```yaml
  ---
  phase: NN-<slug>
  verified: 2026-05-12T<HH:MM:SS>Z
  status: passed
  score: N/N must-haves verified
  overrides_applied: 0
  requirements_verified:
    - REQ-XX-NN
  follow_ups:
    - source: <where it came from>
      item: <one-line>
      severity: <warning|info>
      in_scope: false
      note: <one-line>
  ---
  ```

  Body sections (drop any that yield zero rows):
  1. Phase Goal (verbatim from `v1.0-ROADMAP.md`)
  2. Goal Achievement → Observable Truths (mapped to v1.0 phase ROADMAP success criteria, scored N/N)
  3. Required Artifacts (key files modified by the phase)
  4. Key Link Verification (cross-file wiring)
  5. Data-Flow Trace (Level 4) — only where a real data path exists in this phase
  6. Behavioral Spot-Checks (commands re-run OR cited from existing artifact)
  7. Requirements Coverage (per REQ-ID: status + evidence)
  8. Anti-Patterns Found (cite pre-existing, not phase-introduced)
  9. Cross-Milestone Closure (only when v1.1 closed a v1.0 PARTIAL)
  10. Gaps Summary

- **D-08: Lean target — 100-160 lines per file.** Match the `11/12-VERIFICATION.md`
  scale, not the v1.0-INTEGRATION-CHECK.md scale (450 lines). Don't re-prove
  the wiring map; cite `v1.0-INTEGRATION-CHECK.md` row N and re-spot-check the
  one or two `file:line` hits that pin down the truth.

- **D-09: Evidence sources, in order of preference:**
  1. Direct `grep -n` / `git ls-files` against the current source tree (always).
  2. Quote the current `file:line` (resolved at write time, not from a stale
     CONTEXT.md or audit doc — the v1.1 closure phases shifted line numbers).
  3. Cite `v1.0-INTEGRATION-CHECK.md` row / `v1.0-MILESTONE-AUDIT.md` REQ-block
     for narrative + cross-phase context.
  4. Cite `01-VERIFICATION.md` (v1.1 Phase 1) and Plan 02-01/02/03 SUMMARYs for
     v1.1 closure evidence.
  5. **Don't** re-run `pio test` or `check_dispatch.py` unless a Truth's
     evidence requires a live result not already captured by a prior
     VERIFICATION.md (Phase 1's 25/25 native suite covers the WARNING-1 /
     WARNING-2 closures; Plan 02-03 covers WIRE-02 743/743).

### Plan granularity

- **D-10: Two plans, split by complexity.** Single plan with 10 deliverables
  would be ~1200-1500 lines of doc work; 10 plans is over-fragmentation
  given the template is identical. Natural split:

  - **Plan 03-01 — "Clean batch" (5 files).** Phases where the PARTIAL was
    purely verification-gap (REQ wired, no open hazard, no v1.1 closure to
    cross-reference): **01, 02, 04, 08, 09**.
    - 01: REQ-DB-01..04 (DB-03 has v1.1 WIRE-01 closure cross-ref — minor)
    - 02: REQ-SER-02 (unknown-key skip)
    - 04: REQ-FW-04 + REQ-SAF-03 (already SATISFIED via Phase 12 verification)
    - 08: REQ-SAF-03 (blank-check gating)
    - 09: REQ-UX-01 + REQ-UX-02 (no-pinout marker + adapter table)

  - **Plan 03-02 — "Closure-and-hazard batch" (5 files).** Phases that need a
    Cross-Milestone Closure subsection OR carry a `follow_ups` entry: **03,
    05, 06, 07, 10**.
    - 03: REQ-FW-01 + REQ-SAF-01 (UV-EPROM portion); WARNING-5 follow-up
    - 05: REQ-FW-02; **SC#3 explicit SAF-04 closure record**
    - 06: REQ-FW-03; WARNING-5 follow-up
    - 07: REQ-SAF-02; SAF-05 closure; WARNING-5 follow-up
    - 10: REQ-FW-05 + REQ-FW-06; **SC#4 explicit static_high_mask + pins<32 record**

  Planner may merge or split further if friction arises; the two-plan split
  is a recommendation, not a hard contract.

- **D-11: Plans land in `.planning/phases/03-retroactive-verification-phases-01-10/`.**
  Each plan writes its 5 VERIFICATION.md files under
  `.planning/milestones/v1.0-phases/{NN-slug}/`. Plan SUMMARY.md goes in the
  phase dir per standard GSD pattern.

### Authoring mechanism

- **D-12: Hand-authored by Claude (no agent dispatch).** The `init.phase-op`
  query reports `agents_installed: false, missing_agents: [...all gsd-* agents]`.
  The natural fit (`gsd-verifier`) is not available in this workspace. Each
  VERIFICATION.md is written by the executor agent reading the live source
  tree + cited artifacts and producing the doc directly.

- **D-13: One VERIFICATION.md per task.** Within each plan, 5 file-write
  tasks. Atomic commits per file (one file per commit) following the existing
  GSD atomic-commit pattern. Commit messages match
  `docs(03-NN): retroactive verification — Phase {NN} ({REQ-IDs})`.

### Claude's Discretion

- Exact frontmatter `verified:` timestamp (use ISO8601 at write time).
- Whether to include Section 5 (Data-Flow Trace) per file — include only when
  a real cross-file data path exists for that phase's REQs (e.g., 01 yes; 02
  no, single-file).
- Phrasing of Anti-Patterns section when only pre-existing patterns exist —
  follow `11-VERIFICATION.md` style.
- Whether 03-VERIFICATION.md (UV-EPROM) cites Phase 12's REQ-FW-01 closure
  (algo-first dispatch for 0x07/0x08/0x0B) inline vs. relegating to
  Cross-Milestone Closure subsection — both reasonable.
- Final commit message format (`docs(03-NN): ...` recommended, alternatives
  like `docs(phase-03): retroactive VERIFICATION for v1.0 Phase {NN}` fine).
- Whether to add a top-level Phase 3 SUMMARY at completion summarising the
  10-file batch (Plan 03-02 SUMMARY would naturally cover it; standalone
  SUMMARY optional).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative evidence (cite, don't rebuild)

- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — per-REQ partial-status
  evidence, 13 PARTIAL findings with `evidence:` strings, the `tech_debt`
  block listing pre-existing items per phase. **This is the primary source
  for what each VERIFICATION.md must close.** Frontmatter `gaps.requirements`
  block enumerates exactly the 13 PARTIAL REQs and their owning phases.
- `.planning/milestones/v1.0-INTEGRATION-CHECK.md` — 22 WIRED cross-phase
  traces (table at §"Verified End-to-End Wiring"); 5 WARNING sections; 4 INFO
  sections; the Requirements Integration Map table; E2E Flow Verification
  table. **Cite by row number; don't duplicate.**
- `.planning/REQUIREMENTS.md` §"Retroactive Verification" — VERIF-01..VERIF-10
  spec (one VERIF-NN per phase).
- `.planning/ROADMAP.md` §"Phase 3: Retroactive Verification (Phases 01-10)"
  — 4 success criteria (SC#1: 10 files exist; SC#2: every missing-VERIFICATION
  finding resolved or carried; SC#3: 05-VERIFICATION records SAF-04;
  SC#4: 10-VERIFICATION confirms static_high_mask + pins<32 guard).
- `.planning/MILESTONES.md` §"Known Gaps" — confirms which warnings carry
  forward to v1.2.

### Format exemplars (template source)

- `.planning/milestones/v1.0-phases/11-build-db-cleanup/11-VERIFICATION.md`
  — clean reference passed/4/4; YAML frontmatter pattern with
  `follow_ups` block; "Collateral Drift (advisory)" sub-table; pre-existing
  anti-patterns scored Info.
- `.planning/milestones/v1.0-phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-VERIFICATION.md`
  — denser 8/8 reference; 8-section body fully exercised.
- `.planning/milestones/v1.0-phases/13-close-gap-warning-5-at28c256-64-5v-eeprom-override-12v-on-we/13-VERIFICATION.md`
  — closure-style reference (Phase 13 closed WARNING-5 at the data layer);
  good template for "Cross-Milestone Closure" framing.
- `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md`
  — most-recent template (v1.1 Phase 1); 5/5 truths; includes "Post-Review
  Fixes (Context Signals)" subsection — useful pattern for 05-VERIFICATION's
  SAF-04 closure narrative.

### v1.1 closure evidence (for Cross-Milestone Closure subsections)

- `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-01-PLAN.md` + `01-01-SUMMARY.md` + `01-02-PLAN.md` + `01-02-SUMMARY.md` — SAF-04 + SAF-05 + SAF-06 closure detail (cited by 05/06/07-VERIFICATION).
- `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-01-SUMMARY.md` + `02-02-SUMMARY.md` + `02-03-SUMMARY.md` — WIRE-01 / CLEAN-01 / CLEAN-02 / WIRE-02 closure detail (cited by 01-VERIFICATION REQ-DB-03 + 02-VERIFICATION + 11-VERIFICATION cross-links).
- `.planning/phases/02-naming-cleanup-wire-key-minipro-references/02-VERIFICATION.md` — direct verification of Phase 2 closures, useful as the "Cross-Milestone Closure" cite for 01-VERIFICATION REQ-DB-03.

### v1.0 phase artifacts (primary scope objects)

Each v1.0 phase directory under `.planning/milestones/v1.0-phases/` contains
`NN-NN-PLAN.md` (claims) + `NN-NN-SUMMARY.md` (delivered). Read the SUMMARYs
to know what was claimed; verify against current source.

- `01-database-pipeline/{01,02,03}-{01,02,03}-{PLAN,SUMMARY}.md` (3 plans)
- `02-firmware-json/02-01-{PLAN,SUMMARY}.md` (1 plan)
- `03-eprom-algorithms/03-01-{PLAN,SUMMARY}.md` (1 plan)
- `04-flash-sector-erase/04-{01,02}-{PLAN,SUMMARY}.md` (2 plans)
- `05-intel-flash/05-01-{PLAN,SUMMARY}.md` (1 plan)
- `06-eeprom-page-write/06-01-{PLAN,SUMMARY}.md` (1 plan)
- `07-chip-id-safety/07-01-{PLAN,SUMMARY}.md` (1 plan)
- `08-integration/08-01-{PLAN,SUMMARY}.md` (1 plan)
- `09-adapter-support/09-01-{PLAN,SUMMARY}.md` (1 plan)
- `10-static-pins/{10-01-{PLAN,SUMMARY}.md, 10-CONTEXT.md}` (1 plan + a stray CONTEXT.md)

### Current source-tree files for spot-check (verbatim paths)

For Phase 01 (DB pipeline):
- `firestarter_app/tools/build_db.py` (sole tool; `KNOWN_PROTOCOLS`,
  `DIP28_VARIANT_MAP`, `VPP_MV`)
- `firestarter_app/firestarter/database.py:_map_data` (algorithm + mem_type)
- `firestarter_app/firestarter/data/chip_database.json` (renamed by CLEAN-01)

For Phase 02 (firmware JSON):
- `firestarter/src/json_parser.c:316-318,:251-255` (unknown-key skip in
  both `json_parse` and `parse_bus_config`)

For Phase 03 (UV-EPROM):
- `firestarter/src/proms/eprom.cpp::configure_eprom` (protocol switch +
  pulse_delay defaults + VPE_AS_VPP routing)
- `firestarter/src/proms/eprom.cpp::eprom_generic_init::eprom_check_vpp`
  unconditional call

For Phase 04 (Flash sector erase):
- `firestarter/src/proms/flash_type_3.cpp::flash3_sector_erase`
- `firestarter/src/proms/flash_type_3.cpp::flash3_erase_execute` branch on
  non-zero address

For Phase 05 (Intel flash):
- `firestarter/src/proms/flash_intel.cpp` full handler
- `firestarter/src/proms/flash_intel.cpp:25-50` `flash_intel_check_vpp` (v1.1)
- `firestarter/src/proms/memory.cpp:72-75` Intel dispatch
- `firestarter/test/native/avr/test_flash_intel_vpp/` (v1.1 Unity tests)

For Phase 06 (EEPROM page write):
- `firestarter/src/proms/eeprom_28c.cpp` full handler
- `firestarter/src/proms/memory.cpp:77-80` 0x0D dispatch

For Phase 07 (chip-ID safety):
- `firestarter/src/proms/flash_intel.cpp::flash_intel_check_chip_id`
- `firestarter/src/proms/eprom.cpp::eprom_generic_init` chip_id branch
- `firestarter/src/proms/eeprom_28c.cpp:55-77` `eeprom28c_check_chip_id`
  (v1.1 SAF-05) + `:82-83` call-site
- `firestarter/test/native/avr/test_eeprom28c_chip_id/` (v1.1 Unity tests)

For Phase 08 (integration):
- `firestarter/src/proms/flash_type_3.cpp::flash3_write_init` (blank check)
- `firestarter/src/proms/flash_intel.cpp::flash_intel_write_init` (blank
  check)
- `firestarter/src/proms/eeprom_28c.cpp::eeprom28c_write_init` (blank check)

For Phase 09 (adapter):
- `firestarter_app/firestarter/database.py::get_adapter_table`
- `firestarter_app/firestarter/eprom_info.py::present_eprom_details`
- `firestarter_app/firestarter/main.py:create_info_args` (-a/--adapter)

For Phase 10 (static pins, ROADMAP SC#4):
- `firestarter_app/firestarter/data/pinouts.json` `static-high-pins`
- `firestarter_app/firestarter/database.py::get_bus_config` (`"static-high"`
  list)
- `firestarter/src/json_parser.c::parse_bus_config` (`bus_config.static_high_mask`
  OR)
- `firestarter/src/proms/memory.cpp::mem_util_remap_address_bus` (mask
  application)
- `firestarter/src/proms/memory.cpp::mem_util_calculate_top_address_register`
  (`if (handle->pins < 32)` guard — explicitly required by SC#4)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **VERIFICATION.md YAML frontmatter pattern** (from
  `11/12/13/01-VERIFICATION.md`): `phase / verified / status / score /
  overrides_applied / requirements_verified / follow_ups`. Drop in verbatim;
  per-phase substitute the values.
- **`follow_ups` block schema** (from `11-VERIFICATION.md`): 4-field entries
  with `source / item / severity / in_scope / note`. Used for WARNING-5 +
  WARNING-4 carry-forwards.
- **8-section body skeleton** from `12-VERIFICATION.md`: Goal → Truths →
  Required Artifacts → Key Link Verification → Data-Flow Trace → Behavioral
  Spot-Checks → Requirements Coverage → Anti-Patterns → Gaps Summary. Drop
  any section that has zero rows.
- **"Cross-Milestone Closure" framing** from `01-VERIFICATION.md` (v1.1
  Phase 1) §"Post-Review Fixes (Context Signals)": narrate the closure event,
  cite the v1.1 commit hash, link the Unity tests, point to the closure REQ.
- **v1.0-INTEGRATION-CHECK.md table rows** are pre-mapped to REQ-IDs in its
  "Requirements Integration Map" table. Each VERIFICATION.md's Requirements
  Coverage row can cite by integration-check row number + spot-check current
  `file:line`.

### Established Patterns

- **`grep -n` evidence quoting** — every Truth/Artifact/Link row in v1.0/v1.1
  VERIFICATION.md files cites a specific `file:line` (or line-range). Pattern:
  resolve the line at write time, not from a stale CONTEXT.md value; the v1.1
  closure phases shifted many line numbers (e.g., `flash_intel.cpp` and
  `eeprom_28c.cpp` got new helper functions).
- **REQ-IDs in `requirements_verified` frontmatter must be a subset of the
  REQs the audit attributed to that phase** (per `v1.0-MILESTONE-AUDIT.md`
  `gaps.requirements`). Each phase's REQ list is fixed.
- **`status: passed`** when all Truths verified; **`status: gaps_found`** if
  any Truth fails. For the 10 v1.0 phases under verification today, all REQs
  resolve to SATISFIED against current tree (per audit + v1.1 closures);
  `passed` everywhere is the expected outcome. If a re-grep surprises us
  (drift since the audit), surface it loudly in `gaps.requirements` not
  silently.

### Integration Points

- **No code touch.** Phase 3 writes 10 markdown files under
  `.planning/milestones/v1.0-phases/`. The meta-repo `.planning/` tree is the
  only thing modified.
- **No sub-repo pointer bumps.** Sub-repos (`firestarter/`, `firestarter_app/`)
  are quiet for Phase 3 — verification is read-only on the source tree.
- **STATE.md transition** after Plan 03-01 + 03-02 commit: `status:
  ready_to_plan` → `status: phase_3_complete` after the final verification
  doc lands.

</code_context>

<specifics>
## Specific Ideas

### Verification scope per file (one-liner each)

| File | REQs verified | Cross-Milestone Closure | follow_ups | Plan |
|------|---------------|------------------------|------------|------|
| 01-VERIFICATION.md | DB-01, DB-02, DB-03, DB-04 | DB-03: WIRE-01 (`vpp` → `vpp_mv`) via v1.1 Phase 2 | — | 03-01 |
| 02-VERIFICATION.md | SER-02 | — | — | 03-01 |
| 03-VERIFICATION.md | FW-01, SAF-01 (UV-EPROM portion) | FW-01: Phase 12 algo-first dispatch 0x07/0x08/0x0B | WARNING-5 (AT28C256 mis-tag; deferred v1.2) | 03-02 |
| 04-VERIFICATION.md | FW-04, SAF-03 (flash3 portion) | FW-04: Phase 12 algo-first dispatch 0x06 (190 chips reachable) | — | 03-01 |
| 05-VERIFICATION.md | FW-02, SAF-01 (Intel portion) | **SC#3: SAF-04 closure (v1.1 Plan 01-01)** | — | 03-02 |
| 06-VERIFICATION.md | FW-03 | FW-03: handler logic correct (no v1.1 work touched it) | WARNING-5 (AT28C256 mis-tag; deferred v1.2) | 03-02 |
| 07-VERIFICATION.md | SAF-02 | SAF-02: SAF-05 closure (v1.1 Plan 01-02) on 28C path | WARNING-5 (related: 28C path not reached for AT28C256) | 03-02 |
| 08-VERIFICATION.md | SAF-03 (cross-handler) | — | WARNING-4 (test scripts; owned by Phase 4 / HW-01) | 03-01 |
| 09-VERIFICATION.md | UX-01, UX-02 | — | — | 03-01 |
| 10-VERIFICATION.md | FW-05, FW-06 | — | INFO-3 (static-high-pins only DIP24 populated; v1.2 candidate per FW-07) | 03-02 |

### 05-VERIFICATION.md SAF-04 closure subsection (SC#3 lock — sample text)

```markdown
### Cross-Milestone Closure — REQ-SAF-01 (Intel-flash VPP ADC compare)

The v1.0 `flash_intel_write_init` shipped without a `rurp_read_voltage_mv()`
pre-pulse VPP ADC compare — flagged WARNING-1 in `v1.0-MILESTONE-AUDIT.md`,
escalated to REQ-SAF-01 UNSATISFIED at v1.0 milestone close (39 algo=0x10
Intel-flash chips affected).

**Closed by v1.1 Plan 01-01 (SAF-04):** `flash_intel_check_vpp` static helper
at `firestarter/src/proms/flash_intel.cpp:25-50`, called from
`flash_intel_write_init` at line 77 — before the `chip_id` branch at line 86
and before any write command. Unity coverage: 6/6 PASS in
`test_flash_intel_vpp/test_flash_intel_vpp.cpp`. Post-review CR-01 regression
(VPP error path clears `REGULATOR | P1_VPP_ENABLE` before returning) covered
by `test_flash_intel_high_vpp_error_clears_regulator`.

See `.planning/phases/01-safety-closure-intel-flash-vpp-28c-chip-id/01-VERIFICATION.md`
Truth #1 + #3 for the canonical v1.1 verification record.

**Current source-tree state:** REQ-SAF-01 is SATISFIED for the Intel-flash
family as of 2026-05-12.
```

### 10-VERIFICATION.md SC#4 lock — verbatim verification items

1. `static_high_mask` end-to-end chain — five hops:
   - `firestarter_app/firestarter/data/pinouts.json` `"static-high-pins":[24]` (DIP24 variants)
   - `firestarter_app/firestarter/database.py::get_bus_config` translates pin → bus-line via `pin_conversions`
   - Wire JSON `"static-high":[13]` (post-translation)
   - `firestarter/src/json_parser.c::parse_bus_config` ORs `1UL<<13` into `bus_config.static_high_mask`
   - `firestarter/src/proms/memory.cpp::mem_util_remap_address_bus` applies the mask
2. `pins < 32` VPE_TO_VPP guard — single hop:
   - `firestarter/src/proms/memory.cpp::mem_util_calculate_top_address_register` `if (handle->pins < 32)` plus explanatory comment about VPE_TO_VPP/A16 sharing. Dead `READ_WRITE == WRITE_FLAG` check confirmed absent.

Cite v1.0-INTEGRATION-CHECK.md rows 10 + 11 + the live grep result.

### follow_ups frontmatter entry for WARNING-5 (verbatim shape, 03/06/07-VERIFICATION.md)

```yaml
follow_ups:
  - source: v1.0-MILESTONE-AUDIT.md WARNING-5 (escalated by Phase 12)
    item: "AT28C256/64 family (30 chips, algo=0x07 + electrical.type='Flash/EEPROM') route through configure_eprom and apply 12V P1_VPP to socket pin 1 (= /WE on DIP28_2764) during write. Reads safe."
    severity: warning
    in_scope: false
    note: "Deferred to v1.2 per MILESTONES.md. Upstream-DB classification issue (minipro tags AT28C256 as EPROM_STD); not a v1.0 Phase {NN} defect. Tracked as a per-chip override candidate."
```

### follow_ups frontmatter entry for WARNING-4 (08-VERIFICATION.md)

```yaml
follow_ups:
  - source: v1.0-MILESTONE-AUDIT.md WARNING-4 / 11-VERIFICATION.md follow_ups
    item: "firestarter_test.sh:31 and write_test.sh:17 reference deleted ./firestarter/data/database_generated.json"
    severity: warning
    in_scope: false
    note: "Owned by v1.1 Phase 4 / HW-01 (Hardware Validation). The hardware-validation phase fixes its own scripts."
```

</specifics>

<deferred>
## Deferred Ideas

- **Update `v1.0-MILESTONE-AUDIT.md` to mark the 13 PARTIAL findings closed.**
  The audit is a historical snapshot dated 2026-05-11T11:00. Don't mutate it.
  Phase 5 (Milestone Close / DOC-01) MAY add a v1.1-resolution table to
  `MILESTONES.md` that cross-references the closures, but Phase 3 only
  produces the closure artifacts.

- **Run a fresh integration-check (`/gsd-audit-milestone`) after Phase 3.**
  Reasonable v1.2 entry-point work but out of scope here — the audit doc is
  a milestone-close artifact, not a per-phase one.

- **Re-verify `gsd-validate-phase` Nyquist gaps for v1.0 phases 01-10.**
  ROADMAP wording is "produced by `/gsd-validate-phase` (or equivalent
  retroactive audit)". Phase 3 chooses the "equivalent retroactive audit" path
  (hand-authored verification using existing audit/integration-check evidence)
  rather than running the Nyquist gap-filler test-generation flow.
  `workflow.nyquist_validation` is unconfigured in this workspace per
  `v1.0-MILESTONE-AUDIT.md` Nyquist Coverage section.

- **Add a unified VERIFICATION.md template file to `.planning/templates/`.**
  Nice-to-have for future GSD work; out of v1.1 scope. The four existing
  exemplars (11, 12, 13, 01) are sufficient template sources.

- **Fix `10-CONTEXT.md` stray location.** A `10-CONTEXT.md` lives in
  `.planning/milestones/v1.0-phases/10-static-pins/` (CONTEXT.md files
  normally live in the active phase dir). Audit / cleanup deferred — not a
  Phase 3 deliverable. Phase 3 reads it for evidence; doesn't move it.

- **Resolve the `firestarter_app/.planning/codebase/` stale files.**
  Pre-existing dirt logged from Phase 2; tracked in STATE.md "Operator Next
  Steps" / belongs in its own scoped plan. Not Phase 3.

</deferred>

---

*Phase: 03-retroactive-verification-phases-01-10*
*Context gathered: 2026-05-12*
