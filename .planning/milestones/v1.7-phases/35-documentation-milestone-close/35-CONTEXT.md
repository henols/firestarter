# Phase 35: Documentation + Milestone Close - Context

**Gathered:** 2026-05-25
**Status:** Ready for planning
**Mode:** Auto — decisions made from prior-phase substrate (ROADMAP + REQUIREMENTS + 34-CONTEXT + 34-VERIFICATION + 34-HUMAN-UAT + 34-REVIEW + v1.4/v1.5 close patterns) without per-question prompts. Redirect via plan-phase edit if any call lands wrong.

<domain>
## Phase Boundary

Close v1.7 cleanly. Six deliverables:

1. **Fix the Phase 34 BLOCKER findings before bench.** The Phase 34 code review (2026-05-25, `34-REVIEW.md`) surfaced 2 BLOCKER-class defects in the firmware-side ADC detect path (CR-01 `INPUT_PULLUP` corrupts band math; CR-02 narrow guard gap silent-misclassifies into a fail-silent `ctrl_reg = 0` dispatcher arm) plus 2 warnings on the host-side silkscreen-string rendering (WR-01 `MSG_INFO_HW` / `MSG_INFO_PHYSICAL_HW` bypass the silkscreen map; WR-02 `MSG_OK_CFG` Override clause bypasses the silkscreen map). Bench UAT-3 explicitly tests for CR-01 misclassification. v1.6 Phase 27 RCA re-open consumes the detect-fw substrate. Phase 35 cannot ship v1.7 in good faith leaving these in place. Fix on `firestarter` + `firestarter_app` sub-repos' `v1.7-shield-investigation` branches before promoting to `beta`.

2. **Operator-on-bench validation of Phase 34 firmware** — sideload to operator's Rev 2.0 + Rev 2.2 boards (chip OUT per memory [[feedback_chip_out_before_sideload]]; verify `controller:` identity per port per memory [[feedback_verify_port_identity_each_task]]); confirm `MSG_OK_REV` reports `Rev 2.0-class` (if R41 populated) or `rev_unknown` (if pre-detect-resistor) — either is acceptable per the DETECT-FW-02 backward-compat clause; resolve the §8 OPEN R41 = 4k7-vs-10k discrepancy via the Rev 2.2 ADC read (Phase 35 follow-up #5).

3. **Photo backlog** for the two operator boards that were blocked during Phase 31 (Rev 2.0 = follow-up #2, Rev 2.2 = follow-up #1). Modified Rev 0 (follow-up #3) + full `MODIFICATIONS.md` rework trace (follow-up #4) **DEFER post-v1.7** per scope guardrail — rework trace is orthogonal to detect-fw and the operator may not have bench time; capture as `.planning/todos/` for a later milestone.

4. **Finalize `.planning/v1.7-SHIELD-REVS.md`** — update §3 + §9 rows from bench evidence (UAT-2 R41 measurement on Rev 2.2 resolves the OPEN flag); cross-link both sub-repo READMEs to it; PROJECT.md "Validated" section grows two entries (alias migration + detect-fw plumbing); v1.7 milestone block at the top of PROJECT.md rewritten as "Shipped 2026-05-XX"; v1.6 paused-block carries through unchanged.

5. **MILESTONES.md entry** following the v1.5 / v1.4 template (Phases / Plans / Timeline / Ship tag / Commits header line; Delivered narrative; Key Accomplishments per phase; Branch Strategy; Open Backlog carried; Key Decisions locked; Known Gaps including the CR-02-aware design constraints + post-v1.7 photo/MODIFICATIONS deferral); archive `.planning/v1.7-archive.sh` mirroring `.planning/v1.4-archive.sh` pattern; phases 31-35 directories moved under `.planning/milestones/v1.7-phases/`; ROADMAP.md v1.7 section collapsed to a `<details>` summary; `.planning/REQUIREMENTS.md` archived as `.planning/milestones/v1.7-REQUIREMENTS.md` and removed from the live planning surface (mirror of v1.5 close pattern documented in MILESTONES.md commit `8eff40e`).

6. **Sub-repo branch promotion + ship tag** — sub-repos' `v1.7-shield-investigation` → `beta` (Wave 2 boundary; was deferred from Phase 34 per the v1.7 branch model to land the CR-01/CR-02 fixes on the same pre-release cut); cut `3.0.0b5` pre-release on both sub-repos via the v1.4 lockstep mechanism; `beta` → `main` after operator green on bench UAT-1/2/3 (per v1.7 branch model). Stable `3.0.1` promotion DEFER until v1.6 read-bug resolves (operator-side choice; matches v1.4/v1.5 pattern of leaving the pre-release channel intact while a subsequent milestone is mid-iteration).

7. **STATE.md hand-off to v1.6 resume** — `Operator Next Steps` points at `/gsd-plan-phase 27 --gaps`; cite the v1.7 substrate artifacts the Phase 27 RCA re-open will consume (labeled schematic `.planning/v1.7-SHIELD-REVS.md` §1/§3/§4; per-rev capability table §6; detect-fw substrate `REVISION_2_3` / `REVISION_UNKNOWN` enum + ADC band lookup post-CR-01/CR-02 fix; first disambiguation experiment per the Phase 29-02 SUMMARY hand-off — pre-Phase-28-firmware A/B test on `firestarter/v1.6-read-bug~2`).

Phase 35 is a four-wave phase: Wave 1 desk-side (firmware + host fixes, re-baseline, parity tests green); Wave 2 operator-on-bench (sub-repo `beta` promotion + `3.0.0b5` cut + sideload + UAT-1/2/3 + photo + R41 measurement); Wave 3 desk-side post-bench (SHIELD-REVS.md row updates from bench evidence + README cross-links + PROJECT.md "Validated" + STATE.md hand-off + MILESTONES.md entry); Wave 4 desk-side close (sub-repo `beta` → `main` + meta-repo submodule pointer bumps + `.planning/v1.7-archive.sh` + ROADMAP collapse + REQUIREMENTS archive + final close commit).

</domain>

<decisions>
## Implementation Decisions

### Phase 34 BLOCKER Disposition (D-01..D-04)

- **D-01: CR-01 fix lands in Phase 35 Wave 1.** `firestarter/include/rurp_hw_rev_utils.h:60-61` — delete the `pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT_PULLUP);` line and replace with `pinMode(PIN_HW_REVISION_DETECT_ADC, INPUT);` (high-Z; let R41 + R_top divider drive the pin). Symmetric fix for the A2 disambig read at the same site (per review CR-01b — toggle to `INPUT` so both ADC reads see the same input mode). Rationale: bench UAT-3 specifically tests for CR-01 misclassification; without the fix, UAT-3 cannot meaningfully PASS, and any UAT-1/UAT-2 results are confounded by the per-rev band-shift the review documents (15–30% shift depending on R41 value). Re-derived bands from the pure R41/R_top divider math become the new threshold values per D-02.

- **D-02: CR-02 guard-gap widening + hard-fail-loud on REVISION_UNKNOWN lands in Phase 35 Wave 1.** Two parts per review:
  - **Widen the guard gap** — replace `ADC_BAND_R41_4K7_HIGH = 200`, `ADC_BAND_R41_10K_LOW = 220`, `ADC_BAND_R41_10K_HIGH = 600` in `firestarter/include/rurp_pinout.h:58-62` with empirically-characterized values from the bench session (Wave 2 captures `analogRead(A3)` raw values on the Rev 2.0 + Rev 2.2 boards under `INPUT` mode; Wave 3 derives the per-rev band centers + a guard gap of ≥ 50 counts between adjacent buckets, which is 2-3× the 8-sample-averaged AVR ADC noise floor of ~5-10 counts). If the bench data shows the 4k7 and 10k bands cannot be separated by ≥ 50 counts even with high-Z input, the planner has license to (a) collapse Rev 2.0-class and Rev 2.3 into a single detected band and rely on EEPROM `hw_revision` override for the finer distinction, or (b) defer the per-rev separation to a future Rev 2.4 detect substrate. Either outcome closes v1.7 cleanly; the first is preferred since it leaves the substrate in place for v1.6 resume.
  - **Hard-fail loud on REVISION_UNKNOWN in dispatcher** — `firestarter/include/rurp_hw_rev_utils.h:14-36` (`rurp_map_ctrl_reg_for_hardware_revision`): the current `default:` arm returns 0 silently. Add an explicit `case REVISION_UNKNOWN:` arm that either (a) calls `LOG_ERROR_ID(...)` and refuses to dispatch (returns 0 with explicit error flag), or (b) emits a startup-time `LOG_WARN_ID(...)` from `rurp_detect_hardware_revision()` when the result is `REVISION_UNKNOWN` AND no EEPROM override is set. Planner picks the exact mechanism — the constraint is: operator must SEE that detection failed; silent dispatch with `ctrl_reg = 0` is not acceptable. Existing EEPROM-override precedence at `rurp_hw_rev_utils.h:61-67` is preserved (override beats detection unchanged).

- **D-03: WR-01 silkscreen-string mapping for MSG_INFO_HW + MSG_INFO_PHYSICAL_HW lands in Phase 35 Wave 1.** `firestarter_app/firestarter/serial_comm.py:171-179` (`_REVISION_SILKSCREEN`) + `_format_message` at lines 325-340 — extend the format branch so `MSG_INFO_HW` (catalog ID 0x5B) and `MSG_INFO_PHYSICAL_HW` (catalog ID 0x5C) both render their u8 payload through `_REVISION_SILKSCREEN.get(byte, f'Rev{byte}')`. Add corresponding test coverage in `firestarter_app/tests/test_decoder.py` analogous to the existing `test_ok_rev_p02_with_override_decodes` / `test_ok_rev_p02_no_override_decodes` (one test per new MSG_INFO_*). Rationale: review WR-01 shows the boot-time emit sites at `firestarter.cpp:133-134` currently render `"INFO: HW: Rev254"` (raw byte) when `MSG_OK_REV` renders `"OK: rev_unknown"` (silkscreen) — the two surfaces disagree on what the same byte means, and the inconsistency is visible on every Phase 34 firmware boot regardless of detect outcome.

- **D-04: WR-02 silkscreen-string mapping for MSG_OK_CFG Override clause lands in Phase 35 Wave 1.** `firestarter_app/firestarter/serial_comm.py:359-363` — extend the `MSG_OK_CFG` P-03 renderer to use `_REVISION_SILKSCREEN.get(override, f'Rev{override}')` instead of the raw `Rev{override}` literal. Update `test_ok_cfg_p03_with_override_decodes` in `firestarter_app/tests/test_decoder.py:400-412` to assert the new silkscreen-string format. Rationale: review WR-02 — the same revision byte should not have two different display formats on adjacent ack lines.

### Bench Validation Scope (D-05..D-07)

- **D-05: All 3 Phase 34 HUMAN-UAT items run in Phase 35 Wave 2.** UAT-1 (sideload to Rev 2.0 + capture `MSG_OK_REV`), UAT-2 (sideload to Rev 2.2 + capture `MSG_OK_REV` — resolves §8 R41 = 4k7-vs-10k OPEN flag), UAT-3 (CR-01 misclassification cross-check across multiple boots). All three explicitly recorded as PASS/FAIL/SKIP in `35-HUMAN-UAT.md` (single file, three test rows) and folded into `.planning/v1.7-EVIDENCE.md` (if exists) or appended to `.planning/v1.7-SHIELD-REVS.md` §8 / §9 as the canonical record per ROADMAP SC#1 "complete inventory" clause.

- **D-06: Phase 35 follow-up #1 + #2 (photograph Rev 2.0 + Rev 2.2) run during Phase 35 Wave 2 bench session.** Operator captures top.jpg + bottom.jpg + silkscreen.jpg per board (sufficient resolution to read silkscreen) and stores under `.planning/v1.7/photos/rev-2-0/` + `.planning/v1.7/photos/rev-2-2/` (mirrors the Phase 31 photo dir pattern). `.planning/v1.7-SHIELD-REVS.md` §1 "state" column for the two rows updates from `upstream-only` to `operator-photographed`.

- **D-07: Phase 35 follow-up #3 (photograph Modified Rev 0) + #4 (write full MODIFICATIONS.md) DEFER post-v1.7.** Capture both as new entries in `.planning/todos/pending/` (separate files): `pending/photograph-modified-rev-0.md` + `pending/write-modifications-md-rework-trace.md`. Rationale: rework trace against upstream Rev 0 schematic is independent of v1.7 detect-fw substrate; the operator's Modified Rev 0 board uses the EEPROM `hw_revision` override path regardless of how the rework cuts/jumpers landed (per Phase 34 D-04 + Phase 32 §6 row 91 sentinel pattern); v1.7's milestone goal (canonical reference + detect-fw plumbing + alias migration) does not require this trace. Defer is explicit, not silent — both todos cite the v1.7-SHIELD-REVS.md §1 + §4 + §5 + §6 rows that carry the `pending Phase 35` sentinel so a future milestone can pick them up cleanly.

### Sub-Repo Branch Promotion + Ship Tag (D-08..D-09)

- **D-08: Sub-repo `v1.7-shield-investigation` → `beta` happens at Phase 35 Wave 2 boundary (NOT Phase 34 close).** Phase 34's CONTEXT D-10 said the promotion would happen at Phase 34 close, but the BLOCKER findings (CR-01 + CR-02) landing on 2026-05-25 require a fix-up commit before the promotion. Phase 35 Wave 1 lands the fix; Phase 35 Wave 2 then promotes both sub-repos to `beta` and cuts `3.0.0b5` via the v1.4 lockstep mechanism (manually-paired beta-branch push with explicit `BETA_VERSION=3.0.0b5` input — see `.planning/milestones/v1.4-phases/15-versioning-locked-step-coordination-foundation/15-LOCKSTEP-PROCEDURE.md` for the canonical procedure). `firestarter fw -i --pre --force` becomes the install vehicle for the bench sideload.

- **D-09: Sub-repo `beta` → `main` + ship tag happens at Phase 35 Wave 4 close.** Gated on UAT-1/2/3 green. If UAT-3 surfaces a CR-01-shaped misclassification despite the Wave 1 fix (unlikely but possible if the band math math+silicon disagree), Wave 4 holds; planner documents the gap in MILESTONES.md "Known Gaps" and defers `beta` → `main` to a v1.7.1 patch. Stable `3.0.1` cut DEFER explicitly — pre-release channel remains live; stable promotion bundles with v1.6 ship per the v1.4/v1.5 pattern (each milestone's stable cut waits for the next milestone to validate it doesn't regress).

### Documentation Surface (D-10..D-13)

- **D-10: Operator-facing `firestarter/doc/SHIELD-REVISIONS.md` (firmware sub-repo) + README sections in both sub-repos** — operator-visible documentation must live INSIDE the sub-repos (not in the meta-repo's `.planning/`, which is private to the planner). One canonical doc lives at `firestarter/doc/SHIELD-REVISIONS.md` in the firmware sub-repo; the host sub-repo's README cross-links to it via GitHub URL (`https://github.com/henols/firestarter/blob/main/doc/SHIELD-REVISIONS.md`). Content is a **full operator+dev copy of v1.7-SHIELD-REVS.md §1 + §6 + §7 + §9** (inventory, per-rev capability matrix, silkscreen → code alias table, per-rev ADC band table) — excludes the upstream-git-archaeology sections (§2 mentioned-but-not-recovered, §3 detect-HW history, §4 inter-rev electrical deltas, §5 inter-rev mechanical deltas, §8 detect-HW schematic delta narrative) which remain in the meta-repo `.planning/v1.7-SHIELD-REVS.md` for full provenance traceability. The sub-repo doc opens with a brief "what this is + how to use it" preamble (3-5 sentences) and ends with a "Full investigation history" pointer back to the meta-repo URL. Lands in Wave 3 (post-bench) after §9 row values are finalized from Wave 2 bench evidence — copying mid-investigation would mean re-copying after bench data lands. Each sub-repo README grows a `Shield Revision Support` (firmware) / `Shield Revision Detection` (host CLI) section — 3-5 sentences + a one-liner link to the new doc + a sentence on the `firestarter rev <N>` EEPROM-override escape hatch. Drift policy: the sub-repo doc is operator-facing canonical; meta-repo `.planning/v1.7-SHIELD-REVS.md` is investigation-canonical; Wave 4 close commits both versions in lockstep + adds a CLAUDE.md sync rule extension noting "if §1/§6/§7/§9 in `v1.7-SHIELD-REVS.md` changes, also update `firestarter/doc/SHIELD-REVISIONS.md`" (parallel to the existing constants-parity sync rule between `constants.py` and `firestarter.h`).

- **D-11: PROJECT.md "Validated" section grows two new entries** (insert at the top of the existing Validated bullet list, after the existing v1.5 / v1.4 / v1.2 / v1.0 entries):
  - **Silkscreen → code alias migration (v1.7)** — 4-namespace lock (CTRL_ / PIN_ / RES_ / JMP_) applied across firmware (`firestarter/include/rurp_pinout.h`) + host (`firestarter_app/firestarter/constants.py`); 17 rows in §7 canonical alias table; GATE-1.7 Δ = 0 B across all 3 AVR envs.
  - **Shield-version-detect plumbing (v1.7)** — ADC band lookup on A3 (high-Z) + EEPROM override fall-through + handshake report; `REVISION_2_3` / `REVISION_UNKNOWN` enum on firmware + Python parity; pre-detect-resistor boards (Rev 0 / 2.0 / 2.2) handshake byte-identical to v1.6 baseline modulo the additive `MSG_OK_REV` physical-u8 value.
  - **Update the v1.7 milestone block at the top of PROJECT.md** — change `v1.7 status: STARTED 2026-05-22` to `v1.7 shipped: 2026-05-XX (YYYY-MM-DD when Wave 4 lands)`. Update the milestone narrative to past-tense and add a "Shipped" tag. v1.6 paused-block carries through unchanged.

- **D-12: MILESTONES.md entry follows v1.5 template.** Insert at the top of MILESTONES.md (above the v1.5 entry). Sections in order:
  - Header line: `## v1.7 — RURP Shield Hardware Investigation & Version Detection (Shipped: 2026-05-XX)`
  - Metrics line: Phases (5: 31-35) / Plans (TBD count at close — sum across the 5 phases) / Timeline (2026-05-22 planning → 2026-05-25 execution close) / Ship tag (`3.0.0b5` both sub-repos) / Commits (meta-repo ~N, firestarter sub-repo M, firestarter_app sub-repo P — fill at close)
  - Delivered narrative (3-5 sentences summarizing the milestone)
  - `### Key Accomplishments` — one bulleted item per phase (31 archaeology / 32 difference matrix / 33 alias migration / 34 detect plumbing / 35 fix+bench+close), each 2-4 sentences citing specific artifacts (file paths, commit refs)
  - `### Branch Strategy` — `v1.7-shield-investigation` branches in all 3 repos; sub-repos branched off post-v1.5 `beta`; meta off `main`; `beta` → `main` cut at Wave 4 with `3.0.0b5`
  - `### Open Backlog (carried to v1.7.1 or post-v1.7)` — Modified Rev 0 photo + MODIFICATIONS.md rework trace (D-07 deferral); any CR-02 follow-ups if bench data forces collapse of Rev 2.0/2.3 detect bucket
  - `### Key Decisions (locked)` — D-01 (CR-01 fix in Phase 35); D-02 (CR-02 widen guard gap + hard-fail-loud); D-08 (sub-repo `beta` promotion at Phase 35 Wave 2 not Phase 34 close); D-09 (stable `3.0.1` deferred); D-07 (Modified Rev 0 trace post-v1.7)
  - `### Known Gaps` — runtime capability guards (CAPS-02 deferral); `REVISION_UNKNOWN` hard-fail policy mechanism (planner-final); R41 stock part 5% tolerance worst-case characterization

- **D-13: STATE.md hand-off section** — Wave 4 rewrites the `## Operator Next Steps` section to (a) close v1.7 (mark as `Shipped` at the top), (b) point at v1.6 resume with `/gsd-plan-phase 27 --gaps`, (c) cite the v1.7 substrate artifacts that the Phase 27 RCA re-open consumes (labeled schematic + per-rev capability table + detect-fw substrate), (d) cite the first disambiguation experiment per Phase 29-02 SUMMARY (pre-Phase-28-firmware A/B test on `firestarter/v1.6-read-bug~2`, sideload to Leonardo, re-probe). Update STATE.md frontmatter `milestone:` to v1.6 (resuming) and `status:` to `paused_resume_v1.6`.

### Archive (D-14..D-15)

- **D-14: `.planning/v1.7-archive.sh` mirrors `.planning/v1.4-archive.sh` pattern.** Explicit per-phase glob enumeration (31-* through 35-*); pre-flight (destination empty + sources exist); `--dry-run` flag; safety against accidental capture of paused phases. Run at Wave 4 close. Outputs phase directories moved to `.planning/milestones/v1.7-phases/`.

- **D-15: ROADMAP.md v1.7 section collapsed to `<details>` summary; `.planning/REQUIREMENTS.md` archived as `.planning/milestones/v1.7-REQUIREMENTS.md`.** Mirror of v1.5 close pattern documented in MILESTONES.md commit `8eff40e` (preserved on `git log` as the canonical reference; planner can `git show 8eff40e` for the exact diff shape). The active `.planning/REQUIREMENTS.md` file is removed from the live planning surface — v1.6 resume's Phase 27 RCA re-open will read REQUIREMENTS from the v1.6 archive at `.planning/milestones/v1.6-paused/v1.6-REQUIREMENTS.md` (which doesn't exist yet — operator may need to create at v1.6 close or as part of the resume flow).

### Claude's Discretion

- **Plan-wave decomposition**: 4 waves outlined in `<domain>`. Planner picks final wave count. Wave 1 atomic-fix granularity (one commit per CR / WR finding, or one bundled "Phase 34 BLOCKER fixes" commit) is planner's call; v1.5 Phase 23's "fix-up cluster" pattern shows the bundled approach works for tightly-related findings.
- **Whether to add a `firestarter dev detect-rev` host-side diagnostic subcommand** — Phase 34 CONTEXT mentioned this as a possible opportunistic add. Operator may want it for the Phase 35 Wave 2 R41 measurement on Rev 2.2 (prints raw ADC + detected silkscreen string + EEPROM override state in one operator-facing emit). Planner decides; if added, lands in Wave 1 with the host-side fixes.
- **Whether to land the CR-02 hard-fail-loud mechanism as a planner-final choice or carry the prior-art `LOG_ERROR_ID` / `LOG_WARN_ID` pattern from `firestarter/src/proms/*.cpp`** — both are valid; planner picks based on the bench data tolerance.
- **Whether to update §3 / §4 / §6 rows from Wave 2 bench evidence atomically with §8 / §9** — likely all in one Wave 3 commit (the row-set is tightly coupled); planner finalizes commit boundaries.
- **Whether to fold the open Phase 32 §6 row-91 sentinel pattern (Modified Rev 0 = `as-modified — pending Phase 35`) into the post-v1.7 todo verbatim** — recommended; sentinel pattern preservation across milestone boundaries is valuable for future RCA passes.
- **Whether to bump `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` "What's load-bearing" sections to mention the new detect-fw substrate** — likely yes; small DOC-01 footprint addition.
- **Whether to capture the deferral of `MODIFICATIONS.md` rework trace + Modified Rev 0 photos as separate todos vs one combined todo** — planner picks; separate is cleaner for triage but combined is fewer files.

### Folded Todos

None — `todo.match-phase 35` returned zero matches. The open todos in `.planning/todos/pending/` (`large-read-data-jitter-uno328pb.md`, `w27c512-eeprom-misclassification.md`, `avrdude-mcu-detection-fallback.md`) are orthogonal to Phase 35 scope: the first is v1.6 territory and explicitly resumes after v1.7 close; the second is a separate HIGH-priority chip-DB routing bug for a later milestone; the third is a low-priority blank-chip recovery enhancement. Phase 35 creates two NEW todos at D-07 (`pending/photograph-modified-rev-0.md` + `pending/write-modifications-md-rework-trace.md`) but does not fold any existing todos into v1.7 scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project planning
- `.planning/ROADMAP.md` §v1.7 / Phase 35 — milestone goal, Phase 35 success criteria (SC#1-4), v1.7 branch model, GATE-1.7 non-regression
- `.planning/REQUIREMENTS.md` — DOC-01 (canonical reference + sub-repo README cross-links + PROJECT.md "Validated" updates), MS-01 (MILESTONES.md entry + archive). Note: this file will be archived as `.planning/milestones/v1.7-REQUIREMENTS.md` at Wave 4 close (D-15).
- `.planning/STATE.md` — current milestone state (Phase 34 complete; Phase 35 next); v1.6 paused-block; "Operator Next Steps" gets rewritten at D-13
- `.planning/PROJECT.md` — project overview; v1.7 milestone block at top + "Validated" section both update per D-11
- `.planning/MILESTONES.md` — milestone history pattern (v1.0 / v1.2 / v1.4 / v1.5); new v1.7 entry per D-12

### v1.7 canonical document (Phase 35 finalizes + cross-links)
- `.planning/v1.7-SHIELD-REVS.md` — canonical reference; Phase 35 may update §3 + §9 from Wave 2 bench evidence (R41 = 4k7 vs 10k discrepancy resolution); §1 "state" column for Rev 2.0 + Rev 2.2 rows updates from `upstream-only` to `operator-photographed` per D-06

### Prior phase context (load-bearing)
- `.planning/phases/31-upstream-shield-archaeology/31-CONTEXT.md` — photo/silkscreen capture patterns; mine-notes.md grep references
- `.planning/phases/33-silkscreen-label-code-alias-migration/33-CONTEXT.md` — D-06 hard-rename policy; D-07 `#define` byte-identical math; D-08 Python parity pattern; 4-namespace CTRL_/PIN_/RES_/JMP_ lock
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-CONTEXT.md` — D-01..D-11 detect-fw decisions; D-10 sub-repo `beta` promotion deferral pattern (now superseded by Phase 35 D-08)
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-REVIEW.md` — CR-01 (INPUT_PULLUP corrupts band math) + CR-02 (narrow guard gap silent-misclassify) + WR-01 (MSG_INFO_HW silkscreen bypass) + WR-02 (MSG_OK_CFG silkscreen bypass) — Phase 35 Wave 1 closes ALL FOUR
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-VERIFICATION.md` — 4/4 desk-side PASS; 3 bench items deferred to Phase 35 (UAT-1/UAT-2/UAT-3) — Phase 35 Wave 2 closes all three
- `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-HUMAN-UAT.md` — canonical bench UAT specification (3 tests; Phase 35 Wave 2 owns the file as it grows from pending to PASS/FAIL/SKIP)

### Prior milestone close patterns (Phase 35 mirrors)
- `.planning/milestones/v1.5-ROADMAP.md` — full v1.5 archived roadmap (Phase 25 close = the closest template-of-record)
- `.planning/milestones/v1.5-REQUIREMENTS.md` — REQUIREMENTS archive pattern (D-15)
- `.planning/v1.4-archive.sh` — archive script pattern (D-14); explicit per-phase glob enumeration with safety against capture of paused phases
- `.planning/MILESTONES.md` v1.5 + v1.4 entries — Key Accomplishments / Branch Strategy / Open Backlog / Key Decisions / Known Gaps section template (D-12)
- MILESTONES.md commit `8eff40e` (preserved on `git log`) — REQUIREMENTS archive + ROADMAP collapse for v1.5 close; `git show 8eff40e` is the canonical diff shape

### Firmware source-of-truth files (Phase 35 modifies these)
- `firestarter/include/rurp_hw_rev_utils.h:60-61` — `pinMode(INPUT_PULLUP)` lines to fix per D-01 (CR-01)
- `firestarter/include/rurp_hw_rev_utils.h:14-36` — `rurp_map_ctrl_reg_for_hardware_revision()` dispatcher; D-02 adds explicit REVISION_UNKNOWN arm
- `firestarter/include/rurp_pinout.h:58-62` — `ADC_BAND_R41_*` threshold constants; D-02 widens after bench characterization
- `firestarter/include/rurp_hw_rev_utils.h:68-87` — band-lookup body; D-02 threshold-constant references update
- `firestarter/CLAUDE.md` — Claude-guidance file; Discretion item: optional "What's load-bearing" update to mention post-CR-01/CR-02 detect substrate
- `firestarter/.pio/build/<env>/firmware.hex` — re-baseline target; capture `wc -c` after Wave 1 fix lands (vs Phase 34 baseline at `.planning/v1.7/baseline-34/`)

### Host CLI source-of-truth files (Phase 35 modifies these)
- `firestarter_app/firestarter/serial_comm.py:171-179` — `_REVISION_SILKSCREEN` dict; D-03 + D-04 consumers
- `firestarter_app/firestarter/serial_comm.py:325-340` — `_format_message` extension for MSG_INFO_HW + MSG_INFO_PHYSICAL_HW per D-03
- `firestarter_app/firestarter/serial_comm.py:359-363` — MSG_OK_CFG Override clause extension per D-04
- `firestarter_app/tests/test_decoder.py:400-412` — `test_ok_cfg_p03_with_override_decodes` update + new tests for MSG_INFO_HW / MSG_INFO_PHYSICAL_HW silkscreen rendering per D-03 + D-04
- `firestarter_app/firestarter/messages.py` — auto-generated catalog; **unchanged** by Phase 35 (codegen pass not needed; MessageDef format string is the fallback when `_format_message` doesn't override)
- `firestarter_app/CLAUDE.md` — Claude-guidance file; Discretion item: optional sync-rule prose extension to mention the new format-override surface

### Sub-repo operator-facing docs (Phase 35 Wave 3 creates / Wave 4 ships)
- **NEW: `firestarter/doc/SHIELD-REVISIONS.md`** — operator-facing canonical reference INSIDE the firmware sub-repo per D-10. Full §1+§6+§7+§9 copy of `.planning/v1.7-SHIELD-REVS.md` (inventory + capabilities + alias table + ADC band table); excludes git-archaeology + inter-rev-delta + detect-HW-narrative sections (those stay meta-repo-only). Sub-repo docs are operator-visible on GitHub; meta-repo `.planning/` is not.
- `firestarter/README.md` — add `Shield Revision Support` section per D-10 (links to `doc/SHIELD-REVISIONS.md`)
- `firestarter_app/README.md` — add `Shield Revision Detection` section per D-10 (cross-links to `firestarter/doc/SHIELD-REVISIONS.md` via GitHub URL `https://github.com/henols/firestarter/blob/main/doc/SHIELD-REVISIONS.md` + documents `firestarter rev <N>` EEPROM-override escape hatch with the new `0xFE` rev_unknown sentinel)
- `firestarter/CLAUDE.md` — extend the existing constants-sync rule prose (or add a new "Hardware-revision doc sync" rule) per D-10 drift policy: if `v1.7-SHIELD-REVS.md` §1/§6/§7/§9 changes, the sub-repo `doc/SHIELD-REVISIONS.md` mirror must update in lockstep.

### Memory (auto-recalled, persistent)
- `[[user_shield_revisions]]` — operator owns Rev 2.2 / Rev 2.0 / Modified Rev 0; NO Rev 2.3 on hand; ALWAYS ASK which rev when "swap the shield" comes up; Modified Rev 0 has hardware-bug-A/B rework (cuts + jumpers) — Phase 35 photos #1/#2 cover Rev 2.0/2.2; #3/#4 (Modified Rev 0) DEFER post-v1.7 per D-07
- `[[project_v17_shield_investigation]]` — v1.7 milestone state (Phases 31-35); Phase 35 is the close; v1.6 resumes after via `/gsd-plan-phase 27 --gaps`
- `[[feedback_branching]]` — milestone branches in all 3 repos; sub-repo `v1.7-shield-investigation` → `beta` → `main` at Phase 35 (D-08 + D-09)
- `[[user_firestarter_repo_layout]]` — meta + 2 sub-repos; sub-repos branched off `beta`, meta off `main`
- `[[feedback_chip_out_before_sideload]]` — chip OUT of socket before any firmware sideload (applies to Phase 35 Wave 2 bench)
- `[[feedback_verify_port_identity_each_task]]` — `controller:` identity per port at every task start (applies to Phase 35 Wave 2 multi-board UAT)
- `[[v1.5-bench-findings]]` — programmer_id="urclock" not "arduino" on operator's 328PB-Uno; bench protocol established in v1.5 Phase 24 carries forward verbatim

### Sub-repo CLAUDE.md (must respect)
- `firestarter/CLAUDE.md` — protocol dispatch invariants (Phase 35 CR-01/CR-02 fix MUST NOT perturb `configure_memory` dispatch; rurp_hw_rev_utils.h is OUT of the proms/ dispatch chain by `[env:native] src_filter = +<proms/>` exclusion); CONTROL register bit names verbatim
- `firestarter_app/CLAUDE.md` — Python sync-with-firmware rule (Phase 35 may extend prose for the new format-override surface, optional); MSG_OK_REV wire format invariant (D-03/D-04 honor — host-side rendering changes only, wire shape unchanged)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`.planning/v1.4-archive.sh`** — full archive script pattern with `--dry-run`, explicit per-phase glob enumeration, pre-flight checks, destination-non-empty safety. Phase 35 D-14 copies + edits 4 lines (the phase-number array). Zero new logic needed.
- **`firestarter_app/firestarter/serial_comm.py::_format_message`** — already has a per-message-ID branch surface (Phase 34 added the MSG_OK_REV silkscreen path). D-03 + D-04 extend the same surface with two more branches; pattern is established.
- **`_REVISION_SILKSCREEN` dict** at `serial_comm.py:171-179` — already populated with all REVISION_* enum values per Phase 34 D-05. D-03 + D-04 consume; no new dict entries needed.
- **`.planning/v1.7/baseline-34/`** — pre-Phase-34 `.hex` baseline already captured. Wave 1 re-baseline math: `wc -c` post-fix vs Phase 34 post-fix; recorded in MILESTONES.md "Key Accomplishments" line for Phase 35 with Δ B per env.
- **v1.5 Phase 25 close commit** — single-day execution (planning + execution + bench validation + close on 2026-05-21). Phase 35 has the same shape modulo the Wave 1 fix-up: planning today, Wave 1-4 over the next session. The `lockstep-dryrun-fixture.sh` test from Phase 15 can be re-run before the b5 cut to verify byte-identity (good hygiene, optional).
- **v1.5 / v1.4 "Open Backlog from v1.X bench session" template** — MILESTONES.md `### Open backlog from v1.X bench session (carried to v1.Y)` subsection pattern. Phase 35 D-12 uses the same template; carries Modified Rev 0 photo + MODIFICATIONS.md trace + any CR-02 collapse follow-ups + the runtime-guard CAPS-02 deferral.

### Established Patterns

- **`#ifdef HARDWARE_REVISION` compile-flag gating** — all detect-rev code paths sit under this ifdef (`platformio.ini:23` for all 3 AVR envs; native env excludes). Phase 35 CR-01/CR-02 fixes stay inside the ifdef boundary. Native tests continue to bypass detect-rev.
- **`#define` threshold constants (not `constexpr`)** — Phase 33 D-07 established; `.hex` byte-identical math relies on this. Phase 35 D-02 follows the same pattern for the widened band thresholds.
- **EEPROM-override-byte sentinel = `0xFF`** preserved across CR-02 hard-fail-loud — the `rurp_get_hardware_revision()` precedence at `rurp_hw_rev_utils.h:61-67` is unchanged; the dispatcher hard-fail-loud only fires when there's NO EEPROM override AND ADC detect lands in the guard gap (defensive — operator can always escape via EEPROM).
- **MSG_OK_REV / MSG_INFO_HW / MSG_INFO_PHYSICAL_HW wire shape unchanged** — D-03 + D-04 are host-side rendering only; firmware `LOG_INFO_ID_U8(...)` / `LOG_OK_ID_U8_U8(...)` call sites stay byte-identical to Phase 34 baseline.
- **Atomic commit per CR / WR finding (alternative: bundled fix-up commit)** — v1.4 E2E-01..06 substrate-defect-fix cluster used the bundled approach in a single day; Phase 35 D-Discretion leaves planner choice.
- **Phase 31 photo dir pattern** — `.planning/v1.7/photos/<rev>/` with top.jpg + bottom.jpg + silkscreen.jpg + (optional) per-region close-ups. Phase 35 D-06 follows the same layout for Rev 2.0 + Rev 2.2.
- **`.planning/todos/pending/<descriptive-slug>.md`** — open-backlog file format. Phase 35 D-07 creates two new todos in this directory.

### Integration Points

- **Phase 35 Wave 1 → Wave 2**: re-baselined firmware `.hex` + parity pytest + Unity tests green → sub-repo `beta` merge → CI cuts `3.0.0b5` → `firestarter fw -i --pre --force` installs on operator's boards. The v1.4 beta pipeline substrate (b1/b2/b3 in v1.4; b4 in v1.5) is the proven install vehicle.
- **Phase 35 Wave 2 → Wave 3**: bench evidence (raw ADC values from Rev 2.0 + Rev 2.2 + photos + R41 measurement on Rev 2.2) → §3 + §9 row updates + §8 OPEN flag resolution + §1 "state" column flips. Wave 3 is desk-side document fill from Wave 2 raw data.
- **Phase 35 Wave 3 → Wave 4**: documentation surface complete → sub-repo `beta` → `main` → submodule pointer bump in meta-repo → ROADMAP collapse + REQUIREMENTS archive + phase directories moved → final close commit.
- **Phase 35 → v1.6 resume**: STATE.md D-13 hand-off points at `/gsd-plan-phase 27 --gaps`. v1.7-SHIELD-REVS.md becomes the labeled-schematic substrate that Phase 27 RCA re-open consumes. Detect-fw substrate (`REVISION_2_3` / `REVISION_UNKNOWN` + ADC band lookup post-CR-01/CR-02 fix) becomes available for Phase 27's instrumented A/B builds — boards now self-identify on handshake, removing "which rev is on the bench" as a confound in the RCA debugging.
- **Phase 35 → post-v1.7**: two new todos (Modified Rev 0 photo + MODIFICATIONS.md trace) sit in `.planning/todos/pending/` awaiting triage at the next milestone start. Runtime capability guards (CAPS-02 deferral from Phase 32 §6 follow-up #3) carry through unchanged.

</code_context>

<specifics>
## Specific Ideas

- **CR-01 fix is a one-line code change + one-line symmetric fix.** Deleting the `pinMode(..., INPUT_PULLUP)` line (or replacing with `INPUT`) at `rurp_hw_rev_utils.h:60-61`. The cascade — re-derived ADC band values + new threshold constants — is the larger Wave 1 work, but the actual fix is small. Discretion on whether to keep both lines or delete both stays with planner.

- **CR-02 widen-band-after-bench-characterization is the cleanest pattern.** Pure design-time threshold math (per Phase 34 D-03) gave 200/220/600. Phase 35 Wave 2 captures real-silicon raw ADC values from operator's Rev 2.0 (R41 = 4k7) + Rev 2.2 (R41 = ? per UAT-2) under `INPUT` mode. Wave 3 re-derives the threshold constants from real data, lands a Wave 3 commit. This is the empirical pattern Phase 34's `analog_read_avg8` 8-sample averaging was designed to enable.

- **WR-03 (validate `_REVISION_SILKSCREEN` against catalog at import time)** is mentioned in the review but NOT folded into Phase 35 scope — it's a robustness enhancement, not a correctness bug. Planner can defer to post-v1.7 (D-Discretion).

- **The bench session might surface a 4th BLOCKER** — e.g., the post-CR-01/CR-02 firmware still misclassifies due to AVR-specific noise + R41 stock part 5% tolerance. If so, Wave 4 holds; v1.7.1 patch milestone planned; MILESTONES.md "Known Gaps" documents the rev-detect band-collapse fall-back per D-02's "preferred" branch (collapse Rev 2.0-class + Rev 2.3 into a single detected band; defer per-rev separation to a future Rev 2.4 detect substrate). Operator green is final arbiter.

- **The `3.0.0b5` ship tag implicitly bundles the CR-01/CR-02/WR-01/WR-02 fixes with the v1.7 detect substrate** — there is no `3.0.0b4.1` patch tag in the v1.4 lockstep mechanism; pre-release version bumps are linear. This is by design; the lockstep mechanism doesn't support patch-of-pre-release semantics.

- **Modified Rev 0 deferral is explicit, not silent.** D-07 creates two `pending/` todos with cross-references to v1.7-SHIELD-REVS.md §1/§4/§5/§6 rows carrying the `pending Phase 35` sentinel. The sentinel pattern is preserved across milestone boundaries — a future RCA pass or milestone-start sweep can grep for `pending Phase 35` and pick up the work.

- **Stable `3.0.1` cut deferral is explicit** — operator can promote pre-release → stable at any time after v1.6 resumes + closes; the deferral is documentation, not a hard gate. Operator-side concern.

- **The v1.4 lockstep mechanism handles the `BETA_VERSION=3.0.0b5` input cleanly** — `firestarter_app/.github/workflows/beta-release.yml` + `firestarter/.github/workflows/beta-build.yml` both accept the explicit input and emit matching PEP 440 / GitHub Pre-release version strings. No new CI/CD work; existing substrate is sufficient.

- **`.planning/v1.7/photos/rev-0-modified/` is intentionally NOT created in Phase 35.** Photographing Modified Rev 0 belongs to the post-v1.7 todo (D-07); creating the directory now would imply scope-creep. Photo dirs for Rev 2.0 + Rev 2.2 ARE created by Phase 35 Wave 2 (D-06).

</specifics>

<deferred>
## Deferred Ideas

### For post-v1.7 (new `.planning/todos/pending/` entries created at D-07)

- **Modified Rev 0 photo session** (Phase 31 follow-up #3) — operator's third board carries hardware-bug-A/B rework (cuts + jumpers per memory [[user_shield_revisions]]); photographs are needed to populate `.planning/v1.7-SHIELD-REVS.md` §1 row 4 "state" column. New todo file: `.planning/todos/pending/photograph-modified-rev-0.md`.

- **Full MODIFICATIONS.md rework trace** (Phase 31 follow-up #4) — operator's Modified Rev 0 board has cuts + jumpers that must be traced against the upstream Rev 0 schematic (blob d2a7f691 on origin/rev2.0). Currently a stub at `.planning/v1.7/MODIFICATIONS.md`. Resolution updates §1 row 4 + §4 row 8 + §5 row 7 + §6 row 91 "TBD pending Phase 35" sentinels. New todo file: `.planning/todos/pending/write-modifications-md-rework-trace.md`.

### For post-v1.7 (independent / known gaps)

- **Runtime capability guards** (per Phase 32 §6 follow-up todos) — firmware refuses a `protocol_id` if the detected rev's capability matrix forbids it. Phase 34 substrate enables this (`REVISION_2_3` + `REVISION_UNKNOWN` are now first-class detectable values); implementation deferred per CAPS-02 deferral.

- **`firestarter dev detect-rev` host-side diagnostic** (Discretion item — may land in Phase 35 Wave 1 opportunistically if planner chooses; otherwise post-v1.7).

- **Native-test coverage for `rurp_hw_rev_utils.h`** — extend `[env:native] src_filter` to include the new band-lookup logic with ArduinoFake mocks. Carried from Phase 34 deferred.

- **WR-03 import-time `_REVISION_SILKSCREEN` validation against catalog/firmware enum** — Phase 34 review WR-03 (robustness, not correctness). Defer.

- **8-sample analogRead noise robustness re-characterization** — Phase 34 already shipped `analog_read_avg8`; Phase 35 may revisit if Wave 2 bench data shows the 8-sample window is too noisy/quiet for the chosen band tolerance. Carried from Phase 34 deferred.

- **External pull-up resistor on A3** (schematic change requiring new rev) — would let Phase 34 detect circuit be deterministic across MCU pull-up tolerance. Out of v1.7; operator override + EEPROM byte already handles edge cases. Carried from Phase 34 deferred.

### For v1.6 resume (after v1.7 close)

- **Phase 27 RCA re-open** via `/gsd-plan-phase 27 --gaps` — consumes v1.7 substrate (labeled schematic + per-rev capability table + detect-fw firmware). First disambiguation experiment per Phase 29-02 SUMMARY hand-off: pre-Phase-28-firmware A/B test on `firestarter/v1.6-read-bug~2`, sideload to Leonardo, re-probe.

### Out of v1.7 entirely

- **Designing a Rev 2.4 detect divider with finer per-rev bands** — would let firmware distinguish Rev 2.1 from Rev 2.2 from Rev 2.3 by ADC alone. Operator would need to fabricate + bench-validate. Out of v1.7 (no PCB fabrication in scope).

- **Per-board MCU pull-up calibration stored in EEPROM** — would let firmware self-calibrate to its specific ATmega328 / ATmega32U4 pull-up resistance. Complexity-vs-payoff is poor for a 3-band lookup. Out of v1.7.

- **Stable `3.0.1` cut + sub-repo `main` promotion of v1.6 + v1.7 bundled** — operator-side concern; bundles with v1.6 ship per the v1.4/v1.5 pattern. Carried.

### Reviewed Todos (not folded)

- `large-read-data-jitter-uno328pb.md` — v1.6 milestone scope; v1.6 resumes after v1.7 ships per [[project_v17_shield_investigation]].
- `w27c512-eeprom-misclassification.md` — separate HIGH-priority backlog; chip-database routing bug; carry to its own milestone after v1.6 closes.
- `avrdude-mcu-detection-fallback.md` — low priority; blank-chip recovery path; v1.5 carryover.

(None folded — Phase 35's domain is fix-then-close; the open todos are orthogonal concerns owned by future milestones.)

</deferred>

---

*Phase: 35-Documentation-Milestone-Close*
*Context gathered: 2026-05-25 (auto mode — decisions auto-resolved from prior-phase substrate + Phase 34 code review + Phase 34 verification + v1.5 Phase 25 close template; planner may edit before `/gsd-plan-phase 35`)*
