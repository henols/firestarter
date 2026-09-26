---
phase: 153-write-path-erase-policy
verified: 2026-08-21T12:30:00Z
status: passed
score: 9/9 must-haves verified
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 8/9
  gaps_closed:
    - "No documentation site in either repository still asserts protocol 0x0D (28C/AT28C family) has no erase operation — firestarter/README.md's Protocol Notes section corrected in firestarter@d990a4c, gitlink bumped in meta@2c085a7a."
  gaps_remaining: []
  regressions: []
---

# Phase 153: Write-Path Erase Policy — Verification Report

**Phase Goal:** On protocols where a blank part is not required in order to write — `0x0D` (28C
family) and `0x05` (flash4), both of which auto-erase per page during the write — `write` performs
**no blank check at all**, and `erase` and `blank` are each available as standalone steps. This
makes a non-blank AT28C part writable without `-b`, which is the precondition that makes gh#21's
requested fresh run worth asking for.

**Verified:** 2026-08-21 (re-verification, after gap closure)
**Status:** passed
**Re-verification:** Yes — after gap closure

## Re-verification Summary

The previous pass (`153-VERIFICATION.md`, first run) found 8/9 truths verified and one gap: a live,
unfixed "0x0D has no erase operation" claim in `firestarter/README.md`, and flagged as informational
(not a gap) that `153-RECORD.md`/`REQUIREMENTS.md` incorrectly asserted gh#32 "stays OPEN" when it
was actually closed 2026-08-08 as a duplicate fold into gh#21. Both were reported as fixed by the
coordinator. Neither claim was taken on trust — both were independently re-checked against the
committed tree, plus a fresh independent sweep for any further site.

### Gap 1 — README.md's seventh claim site — CLOSED, verified

`git -C firestarter log --oneline -3` shows `d990a4c docs(153): correct README's 'no erase operation'
claim (7th claim site)` as the tip of the firmware repo's history. Read `firestarter/README.md`'s
"Protocol Notes" section directly (not from the commit message): it now states 0x0D "exposes a
**standalone chip erase** as of Phase 153," names the `CMD_ERASE` dispatch arm and the software
AN-0544B six-byte sequence, states the datasheet's hardware 12V-on-OE mode is "deliberately **not**
implemented" as a hardware-damage hazard, names `scripts/check_erase_no_vpp.py` as the gate, states
`write` performs no blank check so "a non-blank part is therefore writable without `-b`," notes
`blank` remains its own step, notes SDP state is still unreadable, and carries the verbatim phrase
"**This ships software-proven and unvalidated on silicon**." Every element the coordinator's message
claimed is present, is in fact present — confirmed by direct read, not by trusting the commit
message.

Confirmed the gitlink is actually bumped, not just claimed: `git -C /workspaces ls-tree HEAD
firestarter` resolves to `d990a4ce80fcb56c9becf2312d1fe8757e1fc54d`, which matches `git -C firestarter
rev-parse HEAD` exactly — the meta repo's pinned submodule commit is the same commit that carries the
fix, not a stale pointer. `git -C firestarter status --short` and `git -C firestarter_app status
--short` are both clean of tracked changes (firestarter_app's six untracked files predate this phase,
as established in the first verification pass).

**Re-run live:** `python3 scripts/check_erase_no_vpp.py` → exit 0, unchanged PASS. `python3
tools/check_dispatch.py` (from `firestarter_app/`) → exit 0, unchanged PASS,
`check_no_community_support_status_write.py` → exit 0. No regression from the doc-only fix.

### Informational note — gh#32 correction — CLOSED, verified, and correctly upgraded from informational

The first pass flagged (as informational, not a gap) that `153-RECORD.md` and `REQUIREMENTS.md` both
asserted "gh#21, gh#32, gh#11 and gh#12 stay OPEN," when gh#32 was actually closed 2026-08-08 — two
weeks before this phase — as a duplicate fold into gh#21. The coordinator reports this was corrected
in `meta@2c085a7a` and explains why it deserved more than "informational" weight: Phase 152's OUT-02
folds gh#32 into gh#21, and a record asserting gh#32 is still open would invite a reply to a closed
issue. This reasoning is sound and is accepted — it should have been scored as a real (if narrow)
accuracy defect rather than filed purely as an FYI, since it feeds directly into a downstream phase's
action.

Verified directly, not from the commit message:

- `git -C /workspaces log --oneline -2` shows `2c085a7a docs(153): correct the gh#32-stays-OPEN claim;
  bump gitlink for the README fix` as the tip.
- `grep -n "gh#32" .planning/phases/153-write-path-erase-policy/153-RECORD.md
  .planning/REQUIREMENTS.md` shows exactly four corrected sites, matching the coordinator's count
  (two in each file):
  - `153-RECORD.md:135` — the "What was NOT proven" bullet now reads "gh#21, gh#11 and gh#12 stay
    OPEN," with an inline dated correction note: "gh#32 was already CLOSED on 2026-08-08, two weeks
    before this phase, as an unrelated duplicate-fold into gh#21. The no-graduation rule is unchanged
    and still binds gh#21, gh#11 and gh#12... Phase 152 must not 'reply' to a closed issue on the
    strength of this line."
  - `153-RECORD.md:228` — the "What Phase 152 must not repeat" section now reads "gh#21/#11/#12 all
    stay OPEN (gh#32 was already closed 2026-08-08)."
  - `REQUIREMENTS.md:21` — ERASE-09's requirement text corrected identically to `153-RECORD.md:135`'s
    wording, same dated correction note.
  - `REQUIREMENTS.md:360` — the ERASE-09 requirement-flip closing note corrected identically to
    `153-RECORD.md:228`'s wording.
- Live re-check of the actual GitHub issue states (`gh issue view {21,32,11,12} --repo
  henols/firestarter_prom --json state`): gh#21 OPEN, gh#32 CLOSED (`closedAt:
  2026-08-08T09:31:09Z`), gh#11 OPEN, gh#12 OPEN — unchanged from the first pass, and now correctly
  reflected in both corrected documents.
- `REQUIREMENTS.md`'s "Out of Scope" table (line ~372, "Closing gh#21 / #32 / #11 / #12 — A code fix
  is not a validation...") was **not** touched by this correction and does not need to be: that row
  is a scope-boundary statement about what this milestone does not attempt to close via a code
  change, not a claim about gh#32's current open/closed state, so it was correctly left alone.

### Independent sweep for an eighth claim site

Ran a fresh, broader regex sweep across both repositories independently, rather than trusting the
coordinator's reported sweep:

```
grep -rniE "has no erase|no erase operation|cannot be erased|can.?t be erased|erase.{0,10}is not (possible|supported|implemented)|-b (is )?required|requires? .?-b\b|write -b.{0,20}(required|recommended)" \
  --include="*.py" --include="*.cpp" --include="*.h" --include="*.hpp" --include="*.md" --include="*.rst" --include="*.txt" \
  firestarter firestarter_app
```

Two hits, both already known and both re-examined directly against their current source, not assumed
from either party's prior characterization:

1. `firestarter_app/firestarter/cli_handlers.py:800` — reads, in full context: "Phase 153 correction
   (RESEARCH C-8, now inverted): this arm's message used to justify itself by claiming the 28C family
   'has no erase operation at all'. That clause is now **FALSE**..." This is a past-tense correction
   comment explicitly retracting the old claim, not a present-tense assertion of it. **Agreed: not a
   live claim.** Independently confirmed by reading the full paragraph (not just the matched line),
   which continues to explain the corrected, narrower justification that remains true (the *write*
   path specifically performs no erase, which is accurate and unrelated to the retired claim).

2. `firestarter_app/tests/test_sdp_recovery_wording.py:11` — a docstring quoting `chip_test.py:670-673`
   verbatim as an example of legitimate in-report "erase" usage, to justify why this module does a
   scoped constant-level scan rather than a whole-report grep. Independently re-checked against the
   *current* `chip_test.py` (line 678, not 670-673 — the function has grown since this docstring was
   written): the actual NA-reason string today is `f"protocol {family} auto-erases per page during
   write; no step in this plan can ever leave the device blank"`, not the quoted "has no erase
   operation; each page write auto-erases internally." **The docstring's example quote is stale** —
   it no longer matches the source it cites verbatim, though the module's actual executable
   assertions (forbidding the word "erase" as SDP-lock recovery advice, requiring "rewrite" instead)
   do not depend on the quote and remain correct and unaffected. This is not a live false claim about
   product behavior — it is stale internal documentation of *why a test is shaped the way it is*, not
   a claim read by any user or operator. Recorded here for completeness (this was already noted as an
   ℹ️ Info-severity anti-pattern in the first verification pass) but is not scored as a gap: it does
   not misrepresent the shipped erase capability to anyone outside this test file's own maintainers,
   and no plan in this phase claimed ownership of that docstring.

No third-party (previously unknown) claim site was found. The sweep is now clean of any live,
user/operator-facing false claim.

## Goal Achievement (carried forward from the first pass, all previously-verified truths re-confirmed unchanged)

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The pre-write blank check is gone on both `0x0D` and `0x05`, the `0x05` site located (not assumed) | ✓ VERIFIED | Unchanged from first pass — re-confirmed `eeprom_28c.cpp` and `flash_5v_page.cpp` sites, native tests still green. |
| 2 | `erase` is a real standalone step on `0x0D`: `CMD_ERASE` dispatches, `FLAG_CAN_ERASE` restored for algorithm 13 (exclusion tuple `(5,)`) | ✓ VERIFIED | Unchanged — `database.py:629` exclusion tuple re-confirmed, native/host tests unaffected by the doc-only fix. |
| 3 | GATE-03 funded honestly: mechanism correction recorded, `check_dispatch.py` byte-unchanged, real control built/reachable/discriminating | ✓ VERIFIED | Re-ran `check_erase_no_vpp.py` and `check_dispatch.py` live in this pass — both still exit 0, unaffected by the doc fix. |
| 4 | `blank` remains available as its own step (non-regression) | ✓ VERIFIED | Unchanged. |
| 5 | `info`'s "can be erased" row agrees with the wire flag | ✓ VERIFIED | Unchanged — `ic_layout.py` still has zero commits from this phase. |
| 6 | The stale Phase 121 D-12 code comment is corrected | ✓ VERIFIED | Unchanged. |
| 7 | Dual-repo lockstep, flash/RAM measured against a pre-change baseline, leonardo's zero-headroom constraint honored | ✓ VERIFIED | Unchanged — the README/gitlink fix is doc-only, 0 B flash/RAM impact, no re-measurement required or triggered. |
| 8 | No criterion asserts `0x0D` proven, graduates it out of `UNVERIFIED`, changes `support_status`, or requires an AT28C part | ✓ VERIFIED | Unchanged — `chip_database.json` still byte-unchanged; both machine gates still exit 0. |
| 9 | No documentation site in the tree still contradicts the shipped erase capability by claiming "0x0D has no erase operation at all" | ✓ **VERIFIED (was FAILED)** | `firestarter/README.md` corrected in `d990a4c`, gitlink bumped to that commit in `2c085a7a`, both confirmed by direct read and by `rev-parse`/`ls-tree` cross-check, not by commit-message trust. Independent fresh sweep for further sites found none live. |

**Score:** 9/9 truths verified.

### Requirements Coverage

All nine ERASE-01…09 requirements are `[x]` Complete in `.planning/REQUIREMENTS.md`, and every code,
test, and gate claim behind that traceability was independently re-run or re-read in this or the prior
pass — none taken on the record's word alone. ERASE-09's gh-issue sub-claim is now accurate as well as
present.

### Anti-Patterns Found (carried forward, re-triaged)

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `firestarter/README.md` | 111-127 (was 111-116) | ~~Stale/false claim~~ **RESOLVED** | — | Corrected in `d990a4c`; verified by direct read this pass. |
| `firestarter_app/tests/test_sdp_recovery_wording.py` | 9-13 | Docstring quotes a `chip_test.py` NA-reason string that has since changed wording (line moved 670-673 → 678, text changed) | ℹ️ Info | Internal-only stale citation; does not affect test correctness or any user-facing claim; not owned by any plan in this phase; not scored as a gap. |

### Human Verification Required

None.

### Gaps Summary

Both items from the prior pass are closed and independently re-verified against the committed tree:
the seventh claim site (`firestarter/README.md`) is corrected and its gitlink is genuinely bumped to
the fixing commit, and the gh#32 accuracy correction is applied at all four sites the coordinator
named, verified by direct grep and read rather than assumed from the commit message. A fresh,
independently-run sweep for an eighth site found only two hits, both already-known and both
confirmed non-live (one an explicit past-tense retraction, one a stale-but-non-claim internal test
docstring). No functional, wiring, or gate regression was introduced by the fix — both `firestarter`
and `firestarter_app` are clean of tracked changes, and `check_erase_no_vpp.py` / `check_dispatch.py`
/ `check_no_community_support_status_write.py` all still exit 0.

**Phase goal achieved. Ready to proceed.**

---

_Verified: 2026-08-21 (re-verification)_
_Verifier: Claude (gsd-verifier)_
