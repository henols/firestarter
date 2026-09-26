---
phase: 130-close-honesty-ledger-claim-gate-release-decision
verified: 2026-08-02T22:24:20Z
status: passed
score: 4/4 must-haves verified (CLOSE-01, CLOSE-02, CLOSE-03, CLOSE-04)
behavior_unverified: 0
overrides_applied: 0
---

# Phase 130: Close — Honesty Ledger, Claim Gate, Release Decision — Verification Report

**Phase Goal:** The planning record carries every research correction, an honesty ledger pairs
each permitted claim with its non-claim, the ROADMAP slot renumber lands, and pushing `beta` is a
deliberate, recorded decision rather than a side effect.

**Verified:** 2026-08-02T22:24:20Z
**Status:** passed
**Re-verification:** No — initial verification

This report does not take `130-NONREGRESSION.md`'s own claims at face value. Every gate it cites
was **re-executed independently in this session**, and every specific-scrutiny concern in the
verification brief was checked against git history, live GitHub/PyPI state, and file diffs rather
than against the phase's own narrative.

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria 1–4)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All of R-1…R-18 individually corrected in PROJECT.md, STATE.md, ROADMAP.md, notes/py32f071-port-branch-state.md | ✓ VERIFIED | Independently re-ran `check_record_corrections.py` → `PASS`, exit 0, `{'block': 23, 'line-label': 5, 'inline-history': 6, 'inline-allow': 13, 'superseded': 13}`, 0 unlabeled. Spot-checked STATE.md/PROJECT.md/notes file directly for "2992 B", "27 commits behind", "1024" — every live occurrence carries a correction/history label. Notes file's append-only SUPERSEDED section (lines 136–178) independently read and confirms the original 2026-07-28 body (lines 1–134) is untouched. |
| 2 | Honesty ledger pairs each permitted claim with its explicit non-claim, covering the 4 named minimum items | ✓ VERIFIED | `130-LEDGER.md` read in full: six evidence tiers present; provisional pin map (decision-only-unverified tier), absent ARM bus-trace oracle, unmeasured USB-ISR-vs-PROM timing, and HOST-03 mock-only ceiling all present in the negative-space section. Independently re-ran `check_permitted_claims.py` from the 123 directory → `PASS`, exit 0, scans all 4 contracted artifacts. |
| 3 | ROADMAP slot renumber lands with v1.24–v1.27 byte-unchanged | ✓ VERIFIED | Independently ran `git diff -U0 532b0c2a -- .planning/ROADMAP.md \| grep '^@@'` — confirmed 19 hunks, none touching lines 29–32 (the v1.24–v1.27 entries). v1.28/v1.29 py32 slots collapsed into one retirement line (`ROADMAP.md:33`); Binary Command Protocol renumbered to v1.28 (`ROADMAP.md:34`). |
| 4 | `130-DECISION.md` committed before any push; observed tag read from `gh release list`; PyPI verified directly | ✓ VERIFIED | Independently ran `gh release list` on both repos → newest tag `3.0.0b15` in both, matching `130-CHANNELS.md`'s quoted output exactly. Independently ran `gh release view 3.0.0b15 --repo henols/firestarter --json assets` → confirmed all 4 assets present incl. `firestarter_py32f071.hex` (77284 B, matching digest). Independently queried PyPI JSON API → `info.version` = `2.0.7` (stable untouched) and `firestarter==3.0.0b15` resolves. `13X-DECISION.md` naming discrepancy in the ROADMAP criterion's own text (a template placeholder never substituted) is correctly identified and explained rather than silently patched over — the real artifact is `130-DECISION.md` (130-13). |

**Score:** 4/4 truths verified, 0 present-but-behavior-unverified.

### Adversarial Scrutiny — the six flagged items

**1. CLOSE-01…04 tick isolation and evidence-vs-qualifier honesty.**
Verified via `git log --oneline 532b0c2a..HEAD -- REQUIREMENTS.md`: exactly 3 commits touch this
file in the whole phase — `7c2ad583`/`d320e30d` (130-10, PCB-03/FUT-N04 prose only, checkbox state
unchanged `[x]`→`[x]`, confirmed by diffing both commits) and `f00c7ef2` (130-16, the sole tick
commit, message: *"tick CLOSE-01..CLOSE-04 -- the only requirement change in the phase"*). No other
plan touched a requirement checkbox. The qualifiers on CLOSE-02 (mechanizable-half-only) and
CLOSE-04 (operator acts structurally excluded) match what the evidence actually shows — they narrow
the claim rather than paper over a gap. **Verdict: honest scoping, ticks do not outrun their
evidence.**

**2. The three CI-only test fixes, esp. the softened assertion.**
Confirmed commit `1c511e824d2d7e6f3db4d569ef4a2a1a505b3f79` exists on `firestarter`/`beta` and
changes `tests/test_flash_path_record_sync.py::test_present_root_with_missing_target_raises_not_skips`
from a bare `assert META_PRESENT` to `if not META_PRESENT: pytest.skip(META_ABSENT_REASON)`. This is
recorded explicitly and non-silently in `130-CHANNELS.md` §2 ("**This softened a leg Phase 129
wrote as a bare hard assert — recorded explicitly, not left to be discovered silently**") and in
`130-NONREGRESSION.md` §A1. The reasoning holds up: the assertion tested was the module's own
environment *premise* (a meta root under the checkout), not the leg's *subject* (a missing scan
target raises rather than skips) — that subject-assertion is untouched and still runs wherever the
premise holds; `test_absent_meta_claim_can_never_be_false` (present, unchanged) still makes a false
absence-claim impossible. **Verdict: legitimate scoping fix, not a weakened gate, and adequately
recorded in two places.**

**3. Gitlink vs. actually-shipped-tree divergence.**
Confirmed independently: meta gitlink for `firestarter` = `05c20bf59a4f...` (milestone-branch tip,
predates the CI fix). Live `origin/beta` for `firestarter` is actually at `0933bd7d602e...`
("Apply automatic changes" — CI's own version-string auto-bump, `3.0.0b14`→`3.0.0b15` in
`include/version.h`, no other diff), one commit past `1c511e8` (the commit `130-NONREGRESSION.md`'s
own header names as "the tree that actually shipped"). `130-NONREGRESSION.md` §F is explicit and
correct that the gitlink is scoped to the **milestone-branch tip**, not `beta`'s live tip, and does
not conflate the two — this matches D-04's own stated practice and is the specific concern flagged.
One genuine, minor imprecision found: `130-NONREGRESSION.md`'s "post-merge, post-CI-fix" framing of
its own local checkout (`1c511e8`) as "the tree that actually shipped" undersells that `origin/beta`
had already moved one commit further (the auto version-bump) by the time of that sweep. This gap
does not affect any test result (the delta is a one-line version string only) and is not hidden —
`origin/beta`'s real tip (`0933bd7`) is explicitly named in `130-CHANNELS.md` §"self-check", and in
`130-15-SUMMARY.md`/`130-16-SUMMARY.md`. **Verdict: honestly recorded where it matters (the gitlink
distinction); a cosmetic, non-material imprecision in one document's own header, not a conflation of
substance.**

**4. Claim ceiling / overclaim drift.**
Read both release-note drafts (`130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`) in full, plus
`130-LEDGER.md`, `130-NONREGRESSION.md`, and the ticked REQUIREMENTS.md/ROADMAP.md lines, and
grepped all planning-record files for the eight forbidden phrases — every hit found is either (a)
inside a prohibition/instruction naming the phrase as forbidden (PLAN task text, RESEARCH/PATTERNS
discussing fixture design) or (b) a reference to a **different**, actually-bench-validated milestone
(v1.5, v1.15, v1.21 — real AVR hardware). Zero live PY32F071-hardware overclaims found anywhere.
**Verdict: claim ceiling intact.**

**5. D-17 / §5(c) byte-unchanged.**
Confirmed via `git log --all -p -- v1.23-FLASH-PATH-DECISION.md`: the "(c) The ship gate" heading
and its "Ship gate: no PY32F071 board ships…" text appear **exactly once** in the file's entire
history (the original 129-05 authoring commit) — the only phase-130 commit touching this file
(`8aa25f0e`, plan 130-03) edits only (a) and (d), confirmed by direct diff inspection. **Verdict:
§5(c) is genuinely byte-unchanged; the USB-identity tension is carried as an owned residual exactly
as claimed.**

**6. C-6 pid.codes wording ("ask" not "require").**
Confirmed in the actual firmware source (`platform/py32f071/src/usb_cdc.c` lines 27–32: "pid.codes'
terms **ask** that any source referencing this id carry a warning… **not** as a requirement") and in
`130-LEDGER.md` (line 99, `[RESEARCH C-6: the terms say should, not must]`) and the release note
("worded the way pid.codes' own terms ask (not require)"). **Verdict: no artifact found asserting
"required."**

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `check_permitted_claims.py` (Phase 123 dir) | Repointed to scan Phase 130 dir, exit 0 | ✓ VERIFIED | Independently re-run: `PASS`, exit 0, 4 targets, 11/11 fixture tests pass |
| `check_record_corrections.py` (Phase 130 dir) | New checker, exit 0, 0 unlabeled | ✓ VERIFIED | Independently re-run: `PASS`, exit 0, 60 exempt hits/0 unlabeled, 20/20 fixture tests pass |
| `130-LEDGER.md` | Six evidence tiers + negative space | ✓ VERIFIED | Read in full; matches D-09/D-10/D-12 |
| `130-DECISION.md` | Committed before push, 12 pre-flight sections | ✓ VERIFIED | Read; D-17 section present, timestamps precede push |
| `130-CHANNELS.md` | Observed tag, py32 asset gate, PyPI clean-venv | ✓ VERIFIED | Independently re-ran all three checks against live GitHub/PyPI |
| `130-HANDOFF.md` | Operator procedure, no privileged commands | ✓ VERIFIED | Mechanical scan of `<automated>` blocks across all 16 `130-*-PLAN.md` files for `git push`/`git merge`/`git tag`/`gh workflow run`/`gh release create|edit|delete`/`twine upload` — empty, reproduced independently |
| `130-NONREGRESSION.md` | Closing sweep, re-executed evidence | ✓ VERIFIED | All cited gates independently re-run with matching counts (221/1303/41/60/20/11) |
| `130-RELEASE-NOTES-{fw,app}.md` | Scanner-green, no overclaim | ✓ VERIFIED | Read in full; claim gate re-run green; manual scan for forbidden phrases clean |
| `v1.23-FLASH-PATH-DECISION.md` §5(c) | Byte-unchanged | ✓ VERIFIED | Confirmed via full commit history of the section |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| REQUIREMENTS.md CLOSE-01..04 ticks | 130-NONREGRESSION.md §B | citation | WIRED | Each tick cites the exact section discharging it; re-verified independently |
| 130-LEDGER.md | check_permitted_claims.py | default-mode scan | WIRED | Re-run confirms LEDGER is one of the 4 scanned artifacts |
| notes/py32f071-port-branch-state.md SUPERSEDED section | check_record_corrections.py `recordscan:supersedes` markers | mechanism 3 | WIRED | 7 markers present, each naming a needle label + line numbers; checker's 60-hit tally accounts for them |
| 130-DECISION.md timestamp | origin/beta push events | ordering proof | WIRED | Both repos' `origin/beta` recorded unmoved at 130-DECISION.md's authoring time; observed to move only after 130-HANDOFF.md execution |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Claim gate green | `python3 check_permitted_claims.py` (from 123 dir) | exit 0, 4 files scanned | ✓ PASS |
| Record-corrections gate green | `python3 check_record_corrections.py` (from 130 dir) | exit 0, 60 exempt/0 unlabeled | ✓ PASS |
| Claim gate fixture suite | `pytest test_check_permitted_claims.py -q` | 11 passed | ✓ PASS |
| Record-corrections fixture suite | `pytest test_check_record_corrections.py -q` | 20 passed | ✓ PASS |
| Firmware suite | `pytest tests/ -q` (firestarter) | 221 passed | ✓ PASS |
| Host suite | `pytest tests/ -q` (firestarter_app) | 1303 passed (collect-only sum verified), exit 0 | ✓ PASS |
| Cross-repo sync gate | `pytest tests/test_flash_path_record_sync.py -q` | 41 passed | ✓ PASS |
| ARM toolchain present | `arm-none-eabi-gcc/cmake/ninja --version` | 14.2.1 / 4.4.0 / 1.13.0 | ✓ PASS |
| GitHub release state | `gh release list/view` (both repos) | `3.0.0b15` newest both, 4 fw assets incl. py32 hex | ✓ PASS |
| PyPI state | direct JSON API query | `info.version=2.0.7`; `3.0.0b15` resolves | ✓ PASS |
| §5(c) byte-unchanged | `git log --all -p` on the file | text appears once, only in 129-05's original commit | ✓ PASS |
| No checkbox drift outside 130-16 | `git log -- REQUIREMENTS.md` since phase start | 3 commits total, only 130-16 changes `[ ]`→`[x]` | ✓ PASS |
| No privileged commands in any plan's automated blocks | regex over `<automated>` blocks, all 16 plans | empty | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| CLOSE-01 | 130-02/06/07/08/09/10, ticked by 130-16 | Research corrections applied to 5 planning files | ✓ SATISFIED | `check_record_corrections.py` re-run green; spot-checked files directly |
| CLOSE-02 | 130-01/03/11/12, ticked by 130-16 | Honesty ledger + claim gate | ✓ SATISFIED | `130-LEDGER.md` read in full; `check_permitted_claims.py` re-run green |
| CLOSE-03 | 130-04/05, ticked by 130-16 | ROADMAP slot renumber, byte-unchanged v1.24-27 | ✓ SATISFIED | Hash/diff proof independently reproduced |
| CLOSE-04 | 130-13/14/15, ticked by 130-16 | Release decision before push, tag/PyPI verified | ✓ SATISFIED | `gh release list`/`view` and PyPI JSON API independently re-queried |

No orphaned requirements — REQUIREMENTS.md traceability table maps CLOSE-01…04 to Phase 130 only,
and all four are claimed by plans within this phase.

### Anti-Patterns Found

None. No unreferenced `TBD`/`FIXME`/`XXX` markers in phase-130-modified files (the two `TBD` hits in
`130-RESEARCH.md` are the standard "Phases TBD" convention for unscoped future milestones, not debt
markers). No placeholder/stub implementations — this phase produces planning-record prose and two
Python checker tools, both with substantive, independently-passing fixture suites.

### Human Verification Required

None. Every truth was either mechanically re-verified against live state (GitHub API, PyPI API, git
history) or directly read and adversarially cross-checked against the specific concerns raised. The
one substantive judgment call in this phase (D-02's operator wording review of the release bodies)
already happened, per `130-HANDOFF.md`'s recorded resume signal, before either body reached a public
release — that is not a gap left for this verification to close.

### Gaps Summary

No gaps found. All four ROADMAP success criteria are independently verified against live external
state (not just the phase's own self-report), all six adversarial scrutiny items hold up under
direct re-investigation, and the one minor imprecision found (item 3 above — a document's own header
undersells that `origin/beta` had already advanced one version-bump-only commit past the tree it
swept) is cosmetic, does not affect any test result, and is not itself hidden elsewhere in the same
phase's own record.

---

*Verified: 2026-08-02T22:24:20Z*
*Verifier: Claude (gsd-verifier)*
