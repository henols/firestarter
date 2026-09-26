---
phase: 152-outward-facing-close-operator-gated
verified: 2026-08-21T19:15:08Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 152: Outward-Facing Close (Operator-Gated) Verification Report

**Phase Goal:** The public record says what actually shipped and what remains unproven — the owed
gh#12 reply, gh#21/#32 and gh#11 answered, release notes corrected — with every `0x0D` claim paired
with its explicit non-claim.

**Verified:** 2026-08-21T19:15:08Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The owed gh#12 reply is posted, states the ask is half-answered for a second release, does NOT name `write --sdp-relock` as shipped | VERIFIED | `gh issue view 12` live-read: OPEN, 11 comments, last comment id `5373440001` / node `IC_kwDOSX4ER88AAAABQEgwAQ` @ `2026-08-21T18:00:19Z` — matches REQUIREMENTS.md citation exactly. Body text read live: "the ask is half-answered... for a second release", "`enable` returns as nothing in this release... tracked as Backlog 999.28". No "sdp-relock" named as shipped. |
| 2 | gh#21 (#32 folded) receives a comment naming what changed/unproven and a fresh-run request attributable to firmware provenance; gh#21/#11/#12 stay OPEN, gh#32 stays CLOSED | VERIFIED | `gh issue view 21`: OPEN, 3 comments, last id `IC_kwDOSX4ER88AAAABQEyGMg` @ `2026-08-21T18:27:49Z` — matches citation. `gh issue view 32`: CLOSED, `stateReason: COMPLETED`, `closedAt: 2026-08-08T09:31:09Z` (predates milestone, matches D-05's amendment). Comment text requests both `pip install --pre firestarter` and `firestarter fw --install`, and explicitly reasons why (firmware-side fix, host sends no override flag). |
| 3 | gh#11's 2024 report is answered in FIX-06 conflation terms, not left silently superseded | VERIFIED | `gh issue view 11`: OPEN, 19 comments, last id `IC_kwDOSX4ER88AAAABQE07QQ` — matches citation. Comment text explicitly answers the 2026-08-03 `CMD_ERASE` commitment, names the three-way host/wire/firmware conflation, cites datasheet DS20006386B Table 6-1, and credits both `@datapaganism` and `@AndersBNielsen` by name (the escalated attribution decision recorded in 152-LEDGER.md item 4). |
| 4 | Release notes announce `lock-status` as shipped, correct v1.30's forward-looking wording, and state the `write --sdp-relock` withdrawal by name (Backlog 999.28) rather than announcing or omitting it | VERIFIED | `gh release view 3.0.0b23 -R henols/firestarter_app`: prerelease=true, body length 9707B (matches citation exactly). `gh release view 3.0.0b20 -R henols/firestarter`: prerelease=true, body length 9122B, 4 assets (matches citation exactly). Both bodies read live: app body has a `## Removed` section stating "`enable` is withdrawn, with no replacement in this release — for a second release now... `write --sdp-relock` is withdrawn — tracked as Backlog 999.28"; fw body has a `## The withdrawal` section with the identical Backlog 999.28 citation. Neither body claims the command as shipped or available. |
| 5 | A fail-provable claim gate — seen to fail on a planted violation before any pass believed — rejects the 5 forbidden claim classes, and every permitted `0x0D` claim about write-path correctness/validation is paired with its non-claim | VERIFIED | Ran `python3 152-check-claims.py` live: rc=0 over 27 targets. Ran `python3 -m pytest test_check_claims_152.py -q -o addopts=""`: 34 passed (all substantive — collected and inspected test names, none trivial). **Planted a fresh violation myself** (text claiming "proven on AT28C silicon" + "0x0D graduates out of UNVERIFIED") via `FIRESTARTER_CLAIMSCAN_TARGETS_152=<tmp file>`: gate correctly returned rc=1 with itemized forbidden-phrase and missing-caveat failures. Gate is genuinely fail-provable, not merely green. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| gh#12 comment (posted) | Owed CLOSE-06 reply | VERIFIED | Live-read, content matches criterion 1 exactly |
| gh#21 comment (posted) | What-changed/unproven + fresh-run ask | VERIFIED | Live-read, content matches criterion 2 |
| gh#11 comment (posted) | FIX-06 conflation answer | VERIFIED | Live-read, content matches criterion 3 |
| App release body `3.0.0b23` | `lock-status` announced, withdrawal stated | VERIFIED | Live-read, 9707B, includes dated errata correction (see below) |
| Firmware release body `3.0.0b20` | Same, firmware side | VERIFIED | Live-read, 9122B, 4 assets |
| `152-check-claims.py` | Fail-provable claim gate | VERIFIED | rc=0 on real artifacts, rc=1 on self-planted violation |
| `test_check_claims_152.py` | Gate test suite | VERIFIED | 34/34 passed, all substantive (enumerated, not trivial) |
| `152-LEDGER.md` | Honesty ledger, D-03 delegation record | VERIFIED | Explicitly and consistently states operator did not read the 5 bodies (item 6), names the W29C020/W29C040 misattribution (item 5) |
| `152-MERGE-RECORD.md` | Merge record + tail | VERIFIED | Meta PR #38, 2-parent merge `9e154847`, tail section names post-merge commits by path with explicit no-re-merge instruction |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| REQUIREMENTS.md OUT-01..05 | Live GitHub/PyPI artifacts | Evidence citations (comment IDs, node IDs, body byte-lengths) | WIRED | Every citation independently re-measured live via `gh` and matched exactly — no drift between claimed and actual state |
| `152-check-claims.py` `_DEFAULT_TARGETS` | 8 named artifacts + 19 SUMMARYs (152-01..19) | Explicit `os.path.join` list, no glob | WIRED | Confirmed 27-target list; `152-20-SUMMARY.md` deliberately absent and scanned only via positional argv (`python3 152-check-claims.py 152-20-SUMMARY.md` → rc=0), pinned by `test_the... assert "152-20-SUMMARY.md" not in actual_basenames` |
| ROADMAP.md Phase 153 dependency | Phase 152 execution order | `[x] Phase 153` checkbox + phase dir exists | WIRED | Phase 153 marked complete with its own phase directory (`153-write-path-erase-policy/`), satisfying the stated out-of-order dependency (D-08) |
| Meta repo commits | `beta` branch | PR #38 merge + `git cherry` | WIRED | Live `git fetch origin beta && git cherry origin/beta HEAD` on meta repo shows exactly 2 unmerged commits — both are the documented TAIL (`732a2507`, `627aeac8`), matching `152-MERGE-RECORD.md`'s tail list exactly |
| `firestarter` / `firestarter_app` submodule commits | `beta` branch | PR merges | WIRED | Live `git cherry origin/beta HEAD` returns empty in both submodules — fully merged, confirming the "nothing on the milestone branch remains re-mergeable" claim |

### Data-Flow Trace (Level 4)

Not applicable in the conventional sense (no runtime app/DB) — the phase's "data flow" is the
evidence chain from `.planning` claim to live public artifact. This was traced end-to-end and holds:
every requirement's cited comment ID, node ID, timestamp, and byte-length was independently
re-measured against the live GitHub API in this verification and matched exactly.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Claim gate passes on real artifacts | `python3 152-check-claims.py` | rc=0, "PASS: scanned 27 targets" | PASS |
| Claim gate test suite passes | `python3 -m pytest test_check_claims_152.py -q -o addopts=""` | 34 passed | PASS |
| Claim gate is genuinely fail-provable (self-planted violation) | `FIRESTARTER_CLAIMSCAN_TARGETS_152=<tmp> python3 152-check-claims.py` | rc=1, 2 forbidden-phrase matches + 3 missing-caveat failures | PASS |
| `152-20-SUMMARY.md` scans clean via positional argv (deliberately excluded from defaults) | `python3 152-check-claims.py 152-20-SUMMARY.md` | rc=0 | PASS |
| Meta repo tail is exactly the documented commits | `git cherry origin/beta HEAD` (meta repo) | 2 commits: `732a2507`, `627aeac8` | PASS — matches `152-MERGE-RECORD.md` §TAIL |
| Both sub-repos fully merged to beta | `git cherry origin/beta HEAD` (firestarter, firestarter_app) | empty in both | PASS |
| `--auto`/`--chain` guard is armed | `python3 152-check-not-auto.py` | rc=0, config confirms `workflow._auto_chain_active: false` | PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` probes declared or found for this phase (outward-facing/records
phase, not firmware/tooling). Skipped — N/A.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| OUT-01 | 152-05, 152-14 | gh#12 reply posted, honest half-answer framing | SATISFIED | Live gh#12 read matches citation and criterion 1 |
| OUT-02 | 152-06, 152-15 | gh#21 (#32 folded) comment, fresh-run ask | SATISFIED | Live gh#21/#32 read matches citation and criterion 2 |
| OUT-03 | 152-07, 152-16 | gh#11 FIX-06 conflation answer | SATISFIED | Live gh#11 read matches citation and criterion 3 |
| OUT-04 | 152-08, 152-09, 152-10, 152-11, 152-12, 152-17, 152-18 | Release notes corrected, `lock-status` announced, withdrawal stated | SATISFIED | Live release body reads match citation and criterion 4; errata correction present and dated |
| OUT-05 | 152-01, 152-02, 152-13, 152-19, 152-20 | Fail-provable claim gate, 5 forbidden classes, non-claim pairing | SATISFIED | Gate run + self-planted violation confirm fail-provability; pairing confirmed present in published bodies |

No orphaned requirements found — `grep "Phase 152" REQUIREMENTS.md` shows only OUT-01..05 mapped to
this phase, and all five appear in at least one plan's `requirements:` frontmatter.

### Anti-Patterns Found

None that are blockers. Scanned all `*.md`/`*.py` in the phase directory for `TBD`/`FIXME`/`XXX`,
`TODO`/`HACK`/`PLACEHOLDER`, and stub patterns:

- The one `TBD` hit (`152-RESEARCH.md:1293`) references a *pre-existing* ROADMAP defect being fixed,
  not an unresolved marker left by this phase.
- All "placeholder" hits are the documented `APP_TAG_TBD`/`FW_TAG_TBD` version-placeholder mechanism
  (152-08), verified fully substituted in the final files (`grep -c "APP_TAG_TBD\|FW_TAG_TBD"` on both
  release notes files = 0).
- No debt markers, no empty-implementation stubs, no hardcoded-empty data flows found in the
  claim-gate script or test suite.

### Human Verification Required

None. All five must-haves resolved to VERIFIED against live, independently re-measured public
artifacts (GitHub issues/comments, GitHub releases, PyPI registry per `152-LEDGER.md`'s own citation,
and git ancestry via `git cherry`). No visual, UX, or unobservable-behavior items remain.

### Gaps Summary

No gaps. Every one of the "things you must check rather than assume" items in the task brief was
independently verified against live state, not against the SUMMARYs' own narration:

1. **Claim gate fail-provability** — confirmed by planting a fresh violation myself (not reusing the
   phase's own fixtures) and observing rc=1 with itemized failures, plus rc=0/34-passed on the real
   artifacts.
2. **Non-claim pairing in published text** — confirmed by reading the live published app and firmware
   release bodies; both carry the "software-proven and unvalidated on silicon" / "`0x0D` stays
   UNVERIFIED" pairing verbatim.
3. **Requirement traceability** — all five OUT items cross-checked against live `gh`/PyPI reads, not
   plan assertions; every citation matched exactly (comment IDs, node IDs, timestamps, byte-lengths).
4. **D-03 delegation honesty** — `152-LEDGER.md` item 6 and `152-CONTEXT.md` both state plainly that
   the operator read none of the five bodies and performed no wording review; `152-20-SUMMARY.md`
   repeats this without softening. Recorded honestly, not implied as operator-reviewed.
5. **W29C020/W29C040 errata** — the published app body now reads `W29C020` with a dated,
   self-identifying errata paragraph; `152-CONTEXT.md` still cites the wrong `W29C040` name, and this
   is explicitly recorded as an operator decision (errata-only, not also correcting the upstream
   CONTEXT citation) in both `152-LEDGER.md` and `152-20-SUMMARY.md` — not silently left.
6. **`152-20-SUMMARY.md` exclusion** — confirmed absent from `_DEFAULT_TARGETS`, pinned by an explicit
   test assertion, and confirmed to pass (rc=0) when scanned via positional argv.
7. **Tail not on beta** — confirmed live via `git cherry origin/beta HEAD` on the meta repo: exactly
   the 2 commits `152-MERGE-RECORD.md` names as the tail, with the no-re-merge instruction present and
   explicit for both sub-repos.

**Note on the ROADMAP.md phase-level checkbox:** `- [ ] **Phase 152...**` (line 193) is still
unchecked, and `STATE.md` still reads `status: executing`. This is by design, not a gap — plan
152-20's own SUMMARY states explicitly "ROADMAP.md was not touched — no phase checkbox flipped, no
phase-complete state written here... The phase checkbox and phase-complete state are the close's to
write, not this plan's." Flipping that checkbox and STATE.md is downstream of this verification
passing, not a prerequisite for it.

---

_Verified: 2026-08-21T19:15:08Z_
_Verifier: Claude (gsd-verifier)_
