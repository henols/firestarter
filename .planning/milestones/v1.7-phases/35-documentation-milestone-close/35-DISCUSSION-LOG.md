# Phase 35: Documentation + Milestone Close - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 35-CONTEXT.md — this log preserves how Claude reasoned through gray areas in auto mode.

**Date:** 2026-05-25
**Phase:** 35-Documentation-Milestone-Close
**Mode:** Auto (system reminder declared Auto Mode active; no `AskUserQuestion` invoked)
**Areas considered:** Phase 34 BLOCKER disposition, Bench validation scope, Sub-repo branch promotion + ship tag, Documentation surface, Archive

---

## Phase 34 BLOCKER Disposition (D-01..D-04)

**Triggering evidence:** `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-REVIEW.md` (reviewed 2026-05-25T16:27Z, status `issues_found`):

| Finding | Severity | File | Issue |
|--------|----------|------|-------|
| CR-01 | BLOCKER | `firestarter/include/rurp_hw_rev_utils.h:60-61` | `INPUT_PULLUP` active during `analogRead` on A3 detect divider corrupts band math (15-30% per-rev shift) |
| CR-02 | BLOCKER | `firestarter/include/rurp_pinout.h:58-62` + `rurp_hw_rev_utils.h:68-87` | Guard-gap band `[200, 220)` is 20 counts wide vs 5-10 count noise floor; silent-misclassifies into `ctrl_reg = 0` fail-silent dispatcher arm |
| WR-01 | WARNING | `firestarter_app/firestarter/serial_comm.py:171-179` + `messages.py:145-146` + `firestarter/src/firestarter.cpp:133-134` | `MSG_INFO_HW` + `MSG_INFO_PHYSICAL_HW` bypass `_REVISION_SILKSCREEN` → render `"HW: Rev254"` for REVISION_UNKNOWN |
| WR-02 | WARNING | `firestarter_app/firestarter/serial_comm.py:359-363` | `MSG_OK_CFG` Override clause bypasses `_REVISION_SILKSCREEN` → renders raw byte adjacent to silkscreen MSG_OK_REV |

**Options considered:**

| Option | Description | Selected |
|--------|-------------|----------|
| A: Close v1.7 with known issues — defer fixes to v1.7.1 | Document CR-01/CR-02/WR-01/WR-02 in MILESTONES.md "Known Gaps"; ship `3.0.0b5` with broken detect substrate; bench UAT-3 fails by design; v1.6 resume consumes broken substrate | |
| B: Fix-then-close in Phase 35 (Wave 1) | Apply firmware INPUT-mode fix + widen guard gap + add hard-fail-loud for REVISION_UNKNOWN + extend host silkscreen rendering; re-baseline `.hex`; then bench-validate + close | ✓ |
| C: Reopen Phase 34 | Hand back the bench items to a Phase 34 fix-up wave; delays v1.7 close arbitrarily | |

**Selected: B (D-01..D-04 in CONTEXT.md).** Rationale:
1. Bench UAT-3 explicitly tests for CR-01 misclassification (per `34-HUMAN-UAT.md` test #3) — without the fix, UAT-3 cannot meaningfully PASS.
2. v1.6 Phase 27 RCA re-open consumes the detect-fw substrate; shipping it broken would force v1.6 to also reopen v1.7.
3. The fix is small (1-line firmware delete + 3 threshold constant edits + 2 small Python format extensions + tests) — bundling with the close paperwork is the cheapest path.
4. The `3.0.0b5` ship tag implicitly bundles the fixes with the v1.7 substrate; the v1.4 lockstep mechanism doesn't support patch-of-pre-release semantics, so deferring would mean cutting `3.0.0b6` with only the fixes — extra ceremony for no benefit.

**Not folded into Phase 35:** WR-03 (import-time `_REVISION_SILKSCREEN` validation against catalog/firmware enum) — robustness, not correctness; defer post-v1.7.

---

## Bench Validation Scope (D-05..D-07)

**Triggering evidence:** `34-HUMAN-UAT.md` lists 3 bench items deferred from Phase 34; `v1.7-SHIELD-REVS.md` lists 5 Phase 35 follow-up actions (photos × 3, MODIFICATIONS.md fill, R41 measurement).

**Options considered:**

| Option | Description | Selected |
|--------|-------------|----------|
| Tight scope: just UAT-1/2/3 | Bench validation only; skip photos + MODIFICATIONS.md trace | |
| Medium scope: UAT + Rev 2.0/2.2 photos + R41 measurement | Bench validation + Phase 35 follow-up #1/#2/#5; defer #3/#4 | ✓ |
| Wide scope: All 5 Phase 35 follow-up items | Bench validation + all 5 photo/trace items including Modified Rev 0 + full MODIFICATIONS.md | |

**Selected: Medium (D-05/D-06/D-07).** Rationale:
1. UAT-1/2/3 are bench-gated and the minimum to ship v1.7.
2. Rev 2.0/2.2 photos (follow-up #1/#2) are operator-already-on-bench; no additional setup; small marginal cost.
3. R41 measurement on Rev 2.2 (follow-up #5) is naturally folded into UAT-2 (sideload + observe `MSG_OK_REV` reports the band → directly measures R41).
4. Modified Rev 0 photos (#3) + MODIFICATIONS.md fill (#4) are orthogonal to detect-fw — operator's Modified Rev 0 always uses EEPROM override path regardless of rework; rework trace is independent work that may take significant operator time. Defer cleanly via two new `pending/` todos preserving the §1/§4/§5/§6 "pending Phase 35" sentinels.

---

## Sub-Repo Branch Promotion + Ship Tag (D-08..D-09)

**Triggering evidence:** Phase 34 CONTEXT D-10 said sub-repo `v1.7-shield-investigation` → `beta` happens at Phase 34 close; CR-01/CR-02 findings landed on the same day (2026-05-25) so the promotion was effectively held.

**Options considered:**

| Option | Description | Selected |
|--------|-------------|----------|
| A: Phase 34 promotion already happened — bolt on fixes via b6 | Promote at Phase 34 close; cut b5 with broken substrate; cut b6 with fixes — two pre-release tags for one milestone | |
| B: Hold promotion to Phase 35 Wave 2 — bundle fixes with b5 cut | Defer Phase 34's planned `beta` promotion; Phase 35 Wave 1 lands fixes; Wave 2 cuts b5 with fixes baked in | ✓ |
| C: Cut b5 with broken substrate, accept the bug | (rejected — see D-01..D-04 rationale) | |

**Selected: B (D-08).** Rationale: confirms via `git branch --show-current` that both sub-repos are still on `v1.7-shield-investigation` (NOT yet merged to `beta`); the promotion can be deferred cleanly.

For `beta` → `main` + ship tag timing — selected: gated on UAT-1/2/3 green (D-09). Stable `3.0.1` cut deferred until v1.6 read-bug resolves (matches v1.4 → v1.5 pre-release-channel-only pattern; operator-side choice).

---

## Documentation Surface (D-10..D-13)

**Triggering evidence:** ROADMAP.md Phase 35 SC#1-4 enumerates the documentation surface (canonical reference + README cross-links + PROJECT.md "Validated" + MILESTONES.md entry + STATE.md hand-off). v1.5 / v1.4 milestone close patterns provide template-of-record.

**Decisions:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| D-10 README depth | (SUPERSEDED 2026-05-25 by user input — original "cross-link to meta-repo" plan was wrong; see "D-10 amendment" section below) | Original cross-link plan would 404 for any user browsing the sub-repo on GitHub since the meta-repo's `.planning/` is private to the planner |
| D-11 PROJECT.md surface | Two new "Validated" entries (alias migration + detect-fw plumbing); v1.7 block rewritten as "Shipped" | Each phase delivers an independently-verifiable artifact per ROADMAP §Structural Notes → separate validated entries respect that boundary |
| D-12 MILESTONES.md entry | Full v1.5 template (Phases/Plans/Timeline/Ship tag/Commits header + Delivered + Key Accomplishments per phase + Branch Strategy + Open Backlog + Key Decisions + Known Gaps) | v1.5 entry is the closest template; matches the operator's mental model of "what shipped, what didn't, why" |
| D-13 STATE.md hand-off | Operator Next Steps rewrites to point at `/gsd-plan-phase 27 --gaps`; cites v1.7 substrate artifacts | Per ROADMAP SC#4 explicit phrasing |

---

## Archive (D-14..D-15)

**Triggering evidence:** v1.4-archive.sh exists as the canonical pattern; v1.5 close (MILESTONES.md commit `8eff40e`) established the REQUIREMENTS archive + ROADMAP collapse pattern.

**Decisions:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| D-14 archive script | `.planning/v1.7-archive.sh` mirroring `.planning/v1.4-archive.sh` (explicit per-phase glob enumeration, `--dry-run`, pre-flight) | Pattern reuse; zero new logic needed |
| D-15 REQUIREMENTS + ROADMAP | Archive `.planning/REQUIREMENTS.md` as `.planning/milestones/v1.7-REQUIREMENTS.md`; collapse ROADMAP §v1.7 to `<details>` summary | Mirror of v1.5 close commit `8eff40e` |

---

## D-10 amendment (2026-05-25, user-driven)

**Triggering observation (user):** "There must be a md doc in the firestarter project" — the original D-10 plan (README sections cross-linking into `.planning/v1.7-SHIELD-REVS.md` in the meta-repo) is wrong. The meta-repo's `.planning/` directory is private to the planner; any user browsing `henols/firestarter` or `henols/firestarter_app` on GitHub gets a 404 on those cross-links. Operator-facing shield-rev documentation does not exist anywhere inside the sub-repos.

**Gap analysis confirmed:**

| Where | What | Operator-visible? |
|-------|------|-------------------|
| `.planning/v1.7-SHIELD-REVS.md` (meta) | Full 201-line investigation | ❌ private |
| `firestarter/README.md` | Mentions "RURP shield" once; no rev info | ❌ no rev table |
| `firestarter_app/README.md` line 354 | `-rev <revision>` flag accepts `0-2` with "WARNING ... only use with HW mods" | ❌ no explanation of what 0/1/2 means |

**Options presented + user choices:**

| Question | Option A | Option B | Option C | Selected |
|---------|---------|---------|---------|---------|
| Doc location | `firestarter/doc/SHIELD-REVISIONS.md` only | Both sub-repos (mirror) | `firestarter_app/doc/SHIELD-REVISIONS.md` only | **A — firestarter only** |
| Content depth | Operator summary (~80 lines, table + flag map) | Full §1+§6+§7+§9 (~150 lines) | Verbatim mirror of v1.7-SHIELD-REVS.md (~200 lines) | **B — full operator+dev copy** |
| Timing | Fold into Phase 35 D-10 (Wave 3) | New Phase 36 / fold into v1.6 close | — | **A — Phase 35 Wave 3** |

**Rationale (user choices):**
- **firestarter sub-repo (not host)**: firmware is the side that drives the bus + reports the rev via `MSG_OK_REV` + holds the `REVISION_*` enum source-of-truth at `rurp_shield.h:25-30`; doc lives where the enum lives. Host README cross-links via GitHub URL. Lower duplication risk than mirroring; meaningful for a dev grepping for `PIN_VPP_REGULATOR_ENABLE` who lands in firmware/.
- **Full §1+§6+§7+§9 (no archaeology)**: gives dev-side readers the alias table (§7) for grep-back-from-code lookups; gives operators the capability matrix (§6) for "can my Rev N program this chip family"; excludes meta-repo investigation sections (§2/§3/§4/§5/§8) that are debug-trail not operator-facing.
- **Phase 35 Wave 3 (not Phase 36)**: v1.7's milestone goal explicitly includes "READMEs cross-link to it" (ROADMAP SC#1) and "PROJECT.md Validated section grows entries" (SC#2) — folding the sub-repo doc into the same wave keeps v1.7 self-consistent. Lands post-bench so §9 ADC band values are finalized from Wave 2 evidence before copying.

**CONTEXT.md updates:**
- D-10 rewritten in `<decisions>` to specify `firestarter/doc/SHIELD-REVISIONS.md` location + content scope + drift policy
- `<canonical_refs>` section "Sub-repo READMEs" renamed to "Sub-repo operator-facing docs" with the new file added
- Drift policy: meta-repo doc remains investigation-canonical; sub-repo doc is operator-canonical; `firestarter/CLAUDE.md` grows a new sync rule

**Drift risk + mitigation:** copy-paste of §1+§6+§7+§9 across two locations introduces drift risk. Mitigation: (a) sync rule in `firestarter/CLAUDE.md` (analogous to the constants-sync rule between `constants.py` and `firestarter.h`); (b) future meta-repo edits to those four sections must also touch the sub-repo doc (explicit in commit message); (c) Wave 4 close commits both files in lockstep — single commit boundary.

---

## Claude's Discretion

The following were deliberately left to the planner:

- Wave decomposition: 4 waves outlined in CONTEXT.md `<domain>`; planner finalizes wave boundaries.
- Atomic vs bundled fix-up commits in Wave 1 (one commit per CR/WR finding, or one bundled "Phase 34 BLOCKER fixes" commit).
- Optional `firestarter dev detect-rev` host-side diagnostic in Wave 1.
- Exact mechanism for the CR-02 hard-fail-loud (LOG_ERROR_ID refuse-to-dispatch vs LOG_WARN_ID startup-time emit + EEPROM-override pass-through).
- Whether to extend `firestarter/CLAUDE.md` + `firestarter_app/CLAUDE.md` "What's load-bearing" sections to mention the new detect-fw substrate.
- Whether to capture D-07 deferrals as one combined todo or two separate todos.
- Whether to re-run `lockstep-dryrun-fixture.sh` from Phase 15 before the b5 cut (good hygiene; optional).

## Deferred Ideas

See `35-CONTEXT.md <deferred>` section. Two new `.planning/todos/pending/` entries land in Phase 35 Wave 4 capturing the Modified Rev 0 photo deferral + MODIFICATIONS.md rework trace deferral per D-07.

---

*Auto-mode discussion. No AskUserQuestion calls were made. All decisions are reversible via plan-phase edit before `/gsd-plan-phase 35` execution.*
