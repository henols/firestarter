---
phase: 122-close-honesty-ledger-community-ask-release-decision
verified: 2026-07-30T17:00:00Z
status: passed
score: 5/5 must-haves verified (truth 5 closed by remediation 2026-07-30T17:40Z — see gap_resolution below)
behavior_unverified: 0
overrides_applied: 0
gap_resolution:
  - truth: "122-LEDGER.md is fully filled in — no unresolved placeholder fields remain"
    status: resolved
    resolved_at: 2026-07-30T17:40:00Z
    resolved_by: "orchestrator remediation during post-execution verification (not a gap-closure phase — a one-field backfill of an already-verified fact)"
    action: "Replaced the line-6 `**Published cut tag:** _TBD_` placeholder with the OBSERVED tag `3.0.0b14`, sourced from 122-CUT.md, carrying its evidence inline: both prerelease listings (fw run 30551682616 with 3 named .hex assets; app run 30554308461 with zero assets per C-7) and the PyPI JSON API entry (wheel + sdist, uploaded 2026-07-30T15:12:52Z after one explicit manual publish.yml dispatch). The note records WHY the backfill did not happen in Plan 122-08 — that plan never carried 122-LEDGER.md in its files_modified, so the assigned backfill was structurally impossible from it."
    proof:
      - "`grep -n TBD 122-LEDGER.md` → no matches"
      - "`check_permitted_claims.py` (no args, 5 default targets) → exit 0, PASS naming all five"
      - "`pytest test_check_permitted_claims.py -q` → 7 passed (anti-hollow pairing intact)"
      - "`git diff --name-only df9e08c..HEAD -- check_permitted_claims.py` → empty (pattern set never weakened)"
      - "`git status --short` on the phase dir shows ONLY 122-LEDGER.md modified — the four POSTED artifacts (both release bodies, both comment drafts) are byte-untouched, so their operator-approved frozen blobs still match what is live on GitHub"
    no_claim_changed: true
    note: "No claim in the ledger changed. The field records a fact that was already independently correct in every public-facing artifact (122-CUT.md, 122-CHANNELS.md, 122-DELIVERY.md, both release bodies, both gh comments), which is why the gap carried no outward-facing risk. The D-16 operator approval covered the WORDING of the five artifacts; this backfill alters no wording and none of the four posted bodies."
former_gaps:
  - truth: "122-LEDGER.md is fully filled in — no unresolved placeholder fields remain in the single source-of-truth artifact for the release bodies' and comment drafts' wording"
    status: resolved
    reason: "122-LEDGER.md line 6 still reads '**Published cut tag:** _TBD — to be filled by Plan 122-08...' — a debt marker with no formal follow-up reference (no issue/PR/DEF-* number). Git history shows the file has exactly one commit (79be6f0, Plan 122-05) and was never revisited: Plan 122-08's own files_modified list (122-CHANNELS.md only) never included 122-LEDGER.md, so the promised backfill was structurally impossible within the phase's own plan scope. Plan 122-11 (wording review) also lists 122-LEDGER.md in files_modified but its SUMMARY confirms zero content edits were made (operator approved as-written)."
    artifacts:
      - path: ".planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md"
        issue: "Header line 6 'Published cut tag' field left as literal TBD text; the observed tag (3.0.0b14) is correctly recorded everywhere else (122-CUT.md, 122-CHANNELS.md, 122-DELIVERY.md, both release bodies, both gh comments) but never backfilled into this specific artifact"
    missing:
      - "Replace the TBD placeholder in 122-LEDGER.md line 6 with the observed cut tag 3.0.0b14, sourced from 122-CUT.md, or explicitly convert the marker into a recorded, deliberate non-update with a stated reason (mirroring the discipline this phase applies everywhere else to intentional deferrals)"
---

# Phase 122: Close — Honesty Ledger, Community Ask, Release Decision Verification Report

**Phase Goal:** The milestone closes with an honest, verifiable record of exactly what was and wasn't proven, the two community reporters get an accurate (not overclaiming) update, and the beta-push decision is made deliberately instead of by accident.

**Verified:** 2026-07-30T17:00:00Z
**Status:** passed — all four ROADMAP success criteria independently re-verified against live public state; the single completeness sub-check (truth 5, a `TBD` marker in `122-LEDGER.md`) was remediated 2026-07-30T17:40Z, see `gap_resolution` in the frontmatter
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `PROTOCOL-LEDGER` still lists `0x0D` as `UNVERIFIED`, zero chips' `support_status` changed, 84-chip count unchanged, confirmed by `diff_db.py` identity | ✓ VERIFIED | Live re-run: `grep -c '^\| \`0x0D\` .*\*\*UNVERIFIED\*\*' .planning/v1.16/ledger/PROTOCOL-LEDGER.md` → 1; `git status --porcelain -- .planning/v1.16/ledger/` empty; `python3 tools/diff_db.py` exit 0, "2 changed / 0 new / 0 removed" (the 2 explained pre-existing `PGSZ_PAGE_SIZE` entries, not new); `python3 tools/check_no_community_support_status_write.py` exit 0; `pytest tests/test_sdp_db_invariant.py -q` → 4 passed. `check_ledger.py`'s pre-existing RED (v1.19 Phase 104 rename) correctly never used as a gate. |
| 2 | gh#12 receives a reply with the decided auto-unlock policy; gh#11 receives a follow-up; both framed as "here is what changed... please re-test," never "verified fixed" | ✓ VERIFIED | Live `gh api` fetch of both issues' newest comments confirms both posted, both `OPEN`, zero labels, comment counts 13/9 (up from 12/8). Posted bodies are byte-equal to the committed drafts modulo exactly one GitHub-appended trailing newline (diff on both pairs shows only that). Text reads "no AT28C silicon was tested," "clean run only proves the command sequence was emitted, nothing more," never "verified fixed"/"confirmed working." `check_permitted_claims.py` (re-run live) exits 0 against its 5 default targets. |
| 3 | A recorded accept/avoid/cleanup decision for the `beta` push exists and precedes any push | ✓ VERIFIED | `122-DECISION.md` committed at `d5c49d4` / `2026-07-30T13:03:38Z` (`git log`). Firmware outbound merge/push `b9bb6b7` @ `14:24:48Z`; app outbound merge/push `0adfb4f` @ `14:30:00Z` — both over an hour after the decision commit. ACCEPT chosen, AVOID (edit workflow trigger) and CLEANUP (delete stray b12) both explicitly declined with reasons recorded. `3.0.0b12` confirmed still public via `gh release view 3.0.0b12` in both `henols/firestarter` and `henols/firestarter_app`. |
| 4 | Every claim in closing docs matches the permitted claim (byte-exact traces, measured timing); none matches the forbidden claim (SDP works on real AT28C silicon) | ✓ VERIFIED | Live scan (`check_permitted_claims.py`, no args, 5 default targets) exits 0. Manual read of all four live public bodies (2 release notes, 2 gh comments) confirms the "all four ... pinouts" sentence is qualified (`0x0D-protocol`, `AT28C-family`, or `relevant`) each time, and each body separately states the `2804`/`2816`/`2817` size-class refusal (19/19 `DIP24_2816` chips REFUSE) so "all four pinouts" cannot be conflated with operability. Criterion 4's honesty (non-mechanizable) half was closed by the D-16 blocking operator wording review (Plan 122-11), verbatim verdict "Approve — accept the C-5 correction," recorded in `122-11-SUMMARY.md` — not by the scanner alone. The scanner's own docstring and PASS-line caveat state this explicitly, and no plan/summary claims the scan alone satisfies criterion 4. |
| 5 | 122-LEDGER.md is complete — the single source-of-truth artifact carries no unresolved placeholder | ✓ VERIFIED *(was ✗ FAILED at first verification; remediated 2026-07-30T17:40Z)* | **Originally failed:** line 6's `**Published cut tag:** _TBD — to be filled by Plan 122-08_` was never backfilled. `git log` showed exactly one commit ever touched this file (`79be6f0`, Plan 122-05); Plan 122-08's `files_modified` never listed `122-LEDGER.md` (only `122-CHANNELS.md`), so the assigned backfill was **structurally impossible** from that plan. Plan 122-11 lists the file but made zero content edits (operator approved as-written). **Remediated:** the field now records the OBSERVED tag `3.0.0b14` with its evidence inline (fw run `30551682616` / 3 named `.hex`; app run `30554308461` / 0 assets per C-7; PyPI wheel + sdist uploaded `2026-07-30T15:12:52Z` after one explicit manual `publish.yml` dispatch), plus a note on why 122-08 could not do it. Proof: `grep -n TBD 122-LEDGER.md` → no matches; scanner (no args, 5 targets) → exit 0; `pytest test_check_permitted_claims.py -q` → 7 passed; `git diff df9e08c..HEAD -- check_permitted_claims.py` → empty (pattern set never weakened); `git status --short` shows ONLY `122-LEDGER.md` changed, so the four **posted** bodies remain byte-untouched and their operator-approved frozen blobs still match what is live. No claim changed. |

**Score:** **5/5 truths verified** (0 present-but-behavior-unverified) after the truth-5 remediation of 2026-07-30T17:40Z. Truth 5 is not a ROADMAP success criterion by itself — it is a completeness sub-check on ROADMAP criterion 4's "single source of the permitted wording" artifact, added because the debt-marker gate (Step 7) requires every unresolved `TBD`/`FIXME`/`XXX` to be surfaced. At first verification it was the only failure, and it never affected the 4 numbered ROADMAP criteria, all of which were independently VERIFIED against live public state. It carried **no outward-facing risk**: the observed tag was already correct in every public artifact — the placeholder existed only in an internal cross-reference field.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `check_permitted_claims.py` + `test_check_permitted_claims.py` + fixtures | Forbidden-phrase/required-caveat scanner, proven able to fail | ✓ VERIFIED | Live run exits 0 against 5 default targets; fixtures directory (`planted_forbidden_claim.md`, `planted_missing_caveat.md`) present and excluded from default target list per design |
| `122-DECISION.md` | CLOSE-03 decision + pre-flight evidence | ✓ VERIFIED | 326 lines, `ACCEPT` present, all measured values re-confirmed live (branch tips, ahead/behind, merge-tree conflict probe, gitlink baseline) |
| `firestarter_app/firestarter/submit.py`, `tests/test_submit.py`, `firestarter/include/version.h` | Merged clean, `--ours` proven by empty diff, version b11→b13 | ✓ VERIFIED (indirectly, via merge commit history) | `version.h` at merge commit reads `3.0.0b13`; app merge commit `4001396` confirmed in `git log origin/beta` lineage |
| `122-NONREGRESSION.md` | Merged-tree gate results, 11 cross-repo rows | ✓ VERIFIED | Re-ran rows 9a (`check_dispatch.py`) and 9b (`check_devtest_orchestrator.py`) live — both PASS, matching recorded output exactly |
| `122-LEDGER.md` | Honesty ledger, claim classes, negative space | ⚠️ VERIFIED WITH GAP | Content substantively complete (9 claim classes, pinout composition table, mechanism-corrections section, negative-space section) and passes the claim scanner; header metadata field ("Published cut tag") left as unresolved TBD — see gap above |
| `.planning/PROJECT.md` EIGHTH CORRECTION | Silicon-confirmed-defect / fix-unproven correction | ✓ VERIFIED | Block present at line 113, `git diff --numstat` shows 0 deletions for this edit (additive only), correctly cross-references `122-LEDGER.md` rather than restating evidence |
| `122-CUT.md` | Observed cut record | ✓ VERIFIED | Records `81fa53c` beta-only app fix commit in §8/§13 (correctly flagged as a known carry-forward, not silently dropped) |
| `122-CHANNELS.md` | Both-channels-public transcript | ✓ VERIFIED | PyPI JSON API + clean-env `pip index versions --pre` + `pip download` all independently confirm `3.0.0b14`; firmware GitHub prerelease confirmed 3 named `.hex` assets |
| `122-RELEASE-NOTES-fw.md` / `-app.md` | Ceiling-compliant prerelease bodies | ✓ VERIFIED | Posted bodies byte-equal (mod 1 trailing newline) to committed drafts; both carry "no AT28C silicon was tested" and the `DIP24_2816`/2804/2817 refusal qualifier |
| `122-GH11-COMMENT.md` / `122-GH12-COMMENT.md` | Community reply drafts | ✓ VERIFIED | Posted comments byte-equal (mod 1 trailing newline); both issues remain OPEN, zero labels |
| `122-DELIVERY.md` | Delivery record | ✓ VERIFIED | All 4 argv strings, byte-equality proofs, and before/after issue state cross-checked live and match |
| `.planning/REQUIREMENTS.md` | CLOSE-01/02/03 ticked with evidence | ✓ VERIFIED | Diff scoped to exactly 3 checkboxes + 3 traceability rows + footer line; evidence parentheticals independently re-verified true (see truths 1-3 above) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `122-DECISION.md` commit | outbound merge/push commits | timestamp ordering | ✓ WIRED | `d5c49d4` (13:03:38Z) < `b9bb6b7` (14:24:48Z) < `0adfb4f` (14:30:00Z) |
| `122-CUT.md` OBSERVED CUT TAG | `publish.yml` dispatch, `gh release edit`, PyPI check | tag consumption | ✓ WIRED | `3.0.0b14` used consistently in `122-CHANNELS.md`, `122-DELIVERY.md`, both release bodies |
| `122-11-SUMMARY.md` frozen blob SHAs | `122-DELIVERY.md` delivery calls | byte-equality re-check | ✓ WIRED | All 4 SHAs re-matched immediately before posting; posted-vs-committed diff isolated to 1 trailing newline each |
| `122-LEDGER.md` claim classes | release bodies + comment drafts | wording provenance | ✓ WIRED (content); ⚠️ header field not carried through | The claim-class prose is correctly the source for the public docs; the ledger's own "Published cut tag" header metadata was not itself updated (see gap) |
| `122-NONREGRESSION.md` | `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` | read-only grep, never write | ✓ WIRED | `git status --porcelain` on the ledger directory empty before and after, re-confirmed live |

### Behavioral Spot-Checks / Probe Execution

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| App pytest full suite | `python3 -m pytest -q` (firestarter_app, merged tree) | All green, 29 snapshots passed, exit 0 | ✓ PASS |
| Firmware native suite | `pio test -e native` | 141/141 test cases succeeded | ✓ PASS |
| `diff_db.py` identity | `python3 tools/diff_db.py` | exit 0, 2 explained changes, 0 new, 0 removed | ✓ PASS |
| `check_no_community_support_status_write.py` | same | exit 0, 0 write loci | ✓ PASS |
| `test_sdp_db_invariant.py` | `pytest tests/test_sdp_db_invariant.py -q` | 4 passed | ✓ PASS |
| `check_dispatch.py` | `python3 tools/check_dispatch.py` | PASS, 746 chips, 0 regressions | ✓ PASS |
| `check_devtest_orchestrator.py` | same | PASS, 0 VPP-set / raw-wire-dict / --force | ✓ PASS |
| `check_permitted_claims.py` (default 5 targets) | `python3 check_permitted_claims.py` | exit 0, all 5 files named | ✓ PASS |
| gh#11/#12 live state | `gh issue view {11,12} --json state,labels,comments` | OPEN, zero labels, 13/9 comments | ✓ PASS |
| PyPI live state | `pypi.org/pypi/firestarter/json` | `3.0.0b14` present in `releases`, `info.version` still `2.0.7` | ✓ PASS |
| GitHub releases (fw + app) `3.0.0b14` | `gh release view 3.0.0b14 --repo ...` | fw: 3 `.hex` assets; app: 0 assets (expected, PyPI is the channel) | ✓ PASS |
| Posted body/comment byte-equality (4×) | `diff` committed file vs live-fetched body, both normalized to one trailing newline | Zero content diff in all 4 pairs | ✓ PASS |

No probes (in the `scripts/*/tests/probe-*.sh` sense) apply to this phase — it is a close/publication phase, not a migration/tooling phase.

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| CLOSE-01 | 122-04, 122-05, 122-06, 122-13 | `0x0D` stays UNVERIFIED, zero chip status changes, 84-chip count unchanged | ✓ SATISFIED | Live re-run of all 4 mechanisms (see Truth 1) |
| CLOSE-02 | 122-01, 122-05, 122-09, 122-10, 122-11, 122-12, 122-13 | gh#11/#12 answered honestly, never as verified-fixed | ✓ SATISFIED | Live gh state + byte-equality + D-16 review verdict (see Truth 2) |
| CLOSE-03 | 122-02, 122-03, 122-07, 122-08, 122-09, 122-12, 122-13 | Recorded beta-push decision precedes the push | ✓ SATISFIED | Commit-timestamp ordering + both channels verified public (see Truth 3) |

No orphaned requirements — REQUIREMENTS.md's Phase 122 mapping is exactly CLOSE-01/02/03, and all three appear in at least one plan's `requirements:` frontmatter field.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `122-LEDGER.md` | 6 | `TBD` debt marker, no formal follow-up reference | 🛑 Blocker (per debt-marker gate) | Internal-only header field (published cut tag); does not propagate into any public-facing artifact — all downstream consumers (release notes, gh comments, DELIVERY.md, CUT.md, CHANNELS.md) correctly used the observed tag `3.0.0b14` independently. No dishonesty reaches a stranger. |

No other `TBD`/`FIXME`/`XXX`, no `TODO`/`HACK`/`PLACEHOLDER`, no empty stub returns, and no forbidden-phrase matches found across the phase's 13 plans/summaries and 11 closing artifacts.

### Human Verification Required

None. All must-haves were resolvable by direct inspection of live public state (GitHub API, PyPI API) and live command re-execution; no items required subjective human judgment beyond the D-16 operator wording review, which is itself already recorded and closed within the phase (`122-11-SUMMARY.md`).

### Gaps Summary

Phase 122 substantively achieves its goal: all four numbered ROADMAP success criteria are independently re-verified true against live public state, not merely cited from SUMMARY.md claims. The community replies are honest, non-overclaiming, and byte-verified as posted. The beta-push decision demonstrably preceded the push by over an hour, with all three options (accept/avoid/cleanup) recorded. Criterion 4's claim-scanner-plus-operator-review split is real and both halves are evidenced.

The single gap is narrow: `122-LEDGER.md`'s header metadata field "Published cut tag" was left as a literal `TBD` placeholder that a later plan (122-08) was supposed to backfill but structurally never could, because 122-08's own declared `files_modified` scope never included the ledger file. This is a genuine unresolved debt marker per the verification gate's strict rule, but it is isolated to an internal cross-reference field in a non-public artifact — every downstream public artifact (both release notes, both gh comments, the delivery record) correctly and independently carries the real observed tag `3.0.0b14`. It does not constitute an overclaim, does not touch `PROTOCOL-LEDGER`/`support_status`, and does not affect any of the four ROADMAP success criteria.

**Recommendation:** A one-line fix (replace the TBD text in `122-LEDGER.md` line 6 with the observed tag `3.0.0b14`, or record why it is deliberately left unfilled) closes this gap. Given the otherwise-thorough and independently-reproduced evidence throughout the rest of the phase, this looks like an oversight rather than a substantive defect — a human maintainer may reasonably choose to accept it via an override rather than re-opening the phase for a one-line documentation fix.

**This looks intentional-adjacent but not actually accepted anywhere.** To accept this as a deviation, add to this file's frontmatter:

```yaml
overrides:
  - must_have: "122-LEDGER.md is fully filled in — no unresolved placeholder fields remain"
    reason: "TBD is isolated to an internal header field; every public-facing artifact independently and correctly carries the real observed tag 3.0.0b14"
    accepted_by: "<name>"
    accepted_at: "<ISO timestamp>"
```

---

_Verified: 2026-07-30T17:00:00Z_
_Verifier: Claude (gsd-verifier)_
