---
phase: 139
slug: gh-15-correction-outward
status: mapped-to-plans
nyquist_compliant: true
wave_0_complete: false   # artifacts are authored by plans 139-01..139-04; every MISSING reference below is owned by a named plan
created: 2026-08-09
---

# Phase 139 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `139-RESEARCH.md` §"Validation Architecture". This is a meta-repo-only,
> outward-facing publication phase: most verification is **content assertion + citation
> resolution + state read**, not unit tests.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` 9.1.1 available but **optional** here; primary mechanism is shell assertions inside `<verify><automated>` blocks |
| **Config file** | none for meta-repo phases — Phase 137 ran `test_check_permitted_claims_v130.py` directly from its phase dir |
| **Quick run command** | `cd .planning/phases/139-gh-15-correction-outward && python3 139-check-claims.py <files>` |
| **Full suite command** | the Task-3 verification block: anchor loop + freeze check + 3-ref blob equality + gh#15 state read |
| **Estimated runtime** | ~30 seconds (network-bound: 9 anchor fetches + 1–2 `gh` reads) |

> `pytest` addopts in this project are `-ra -q`; doubling `-q` hides the count line. If a paired
> test module is added, run it with `-o addopts=""`.

---

## Sampling Rate

- **After every task commit:** `139-check-claims.py` on the changed artifact + `git status --porcelain` on the frozen files empty
- **After every plan wave:** full `verify_anchor` loop + 3-ref `eprom.cpp`/`memory.cpp` blob check + gh#15 state read
- **Before `/gsd-verify-work`:** all of the above green, plus either the post-hoc byte-diff (post branch) or the parked-command record (hold branch)
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

Task IDs are assigned by the planner; rows below are the **required** verifications, keyed to
requirement rather than task until plans exist. Every row must land in some plan's `<verify>` block.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 139-03 T1 | 139-03 | 2 | ISSUE-01 | — | Comment states C1 and cites `infoic-field-dictionary.md:210-217` + commits `8de307f`/`12286df` | content | `grep -qF '500' 139-GH15-COMMENT.md && grep -qF '8de307f' … && grep -qF '12286df' …` | ❌ W0 | ⬜ pending |
| 139-01 T2 | 139-01 | 1 | ISSUE-01 | T-139-permalink | Every C1/C2/C3 citation resolves at its pinned SHA **with the claimed content** | integration | `verify_anchor` loop — 7 anchors + 2 commits, exit 0 | ❌ W0 (script) | ⬜ pending |
| 139-03 T1 | 139-03 | 2 | ISSUE-01 | — | Comment states C2 with the three histogram lines | content | `for p in 'n = 170' 'n = 127' 'n = 32'; do grep -qF "$p" 139-GH15-COMMENT.md; done` | ❌ W0 | ⬜ pending |
| 139-03 T1 | 139-03 | 2 | ISSUE-01 | — | C3 stated as the **overprogram** pulse; cites the **program**-pulse line (`memory.cpp`), not the erase pulse | content | `grep -qF 'memory.cpp' … && grep -qF '75' … && grep -qF '16383' …` | ❌ W0 | ⬜ pending |
| 139-03 T1 | 139-03 | 2 | ISSUE-01 | T-139-falseclaim | C2 does **not** carry the false "all three disagree with the modal value" (RESEARCH F-03) | negative content | `! grep -qiE 'all three.*disagree.*modal' 139-GH15-COMMENT.md` | ❌ W0 | ⬜ pending |
| 139-03 T1 + 139-05 T1 | 139-03 / 139-05 | 2 / 4 | ISSUE-02 | — | 6.25 V ceiling present as its own paragraph | content + manual | `grep -qF '6.25' 139-GH15-COMMENT.md` + paragraph read | ❌ W0 | ⬜ pending |
| 139-03 T1 | 139-03 | 2 | ISSUE-02 | — | **Comment's** amendment maps all nine boxes, each marked kept/corrected/replaced; every original box quoted verbatim | structural | `test "$(grep -oiE '\b(kept\|corrected\|replaced)\b' 139-GH15-COMMENT.md \| wc -l)" -ge 9` + per-box verbatim loop → `ORIGINAL-BOXES-QUOTED-OK` | ❌ W0 | ⬜ pending |
| 139-04 T1 | 139-04 | 3 | ISSUE-02 | — | **Amendment's** table maps all nine boxes likewise; the original nine survive verbatim inside the `details` block | structural | `… \| wc -l)" -ge 9` **and** an `awk -F'\|'` count of table rows whose 2nd column carries a disposition token `= 9` → `AMENDMENT-DISPOSITIONS-OK`; plus `ORIGINALS-PRESERVED-OK` | ❌ W0 | ⬜ pending |
| 139-04 T2 | 139-04 | 3 | ISSUE-02 | T-139-12 | The two disposition tables agree **row for row** — re-derived, not self-reported | structural | box-anchored loop over the nine originals comparing each file's 2nd-column token → `DISPOSITIONS-AGREE-OK`; fails naming the row, the box and both values | ❌ W0 | ⬜ pending |
| 139-02 T2 + 139-04 T2 | 139-02 / 139-04 | 1 / 3 | ISSUE-02 | T-139-overclaim | No forbidden overclaim | claim gate | `python3 139-check-claims.py …` — **preceded by a planted-failure run** | ❌ W0 (script) | ⬜ pending |
| 139-01 T1 | 139-01 | 1 | ISSUE-01 | — | The captured nine boxes are byte-identical to RESEARCH's independently-read copy — the capture is faithful, not a transcription | structural | `diff <(grep '^- \[ \]' 139-GH15-ORIGINAL-CRITERIA.md) <(sed -n 's/^> \(- \[ \] .*\)$/\1/p' 139-RESEARCH.md)` → empty, `RESEARCH-DIFF-EMPTY-OK` | ❌ W0 | ⬜ pending |
| 139-01 T1 + 139-05 T1 | 139-01 / 139-05 | 1 / 4 | ISSUE-03 | T-137-16 | Nothing posted before the gate | state | `gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments\|length'` == 0 | ✅ | ⬜ pending |
| 139-04 T2 | 139-04 | 3 | ISSUE-03 | — | Draft frozen before the gate | git | blob SHA + `wc -c` recorded; `git status --porcelain -- <file>` empty | ✅ | ⬜ pending |
| 139-05 T1 | 139-05 | 4 | ISSUE-03 | T-137-16 | Operator approved **wording** | **human** | verbatim verdict recorded in SUMMARY | 🧑 human-only | ⬜ pending |
| 139-05 T1 | 139-05 | 4 | ISSUE-03 | T-137-16 | Posting **explicitly authorized** (separate yes) | **human** | verbatim "post now" / "approved, hold" | 🧑 human-only | ⬜ pending |
| 139-05 T2 | 139-05 | 4 | ISSUE-03 | — | Posted == reviewed | integration | `diff <(sed -e '$a\' frozen) <(sed -e '$a\' fetched)` → empty | ✅ recipe proven at 122-12 | ⬜ pending |
| 139-05 T2 | 139-05 | 4 | ISSUE-03 | — | Exactly one comment added, issue still OPEN, no label added | state | `gh issue view 15 --json state,labels,comments` → `{"labels":[],"n":1,"state":"OPEN"}` | ✅ | ⬜ pending |
| 139-05 T2 | 139-05 | 4 | ISSUE-03 | T-137-18 | Hold branch leaves a named, parked one-command follow-up | record | `.planning/v1.31-OPERATOR-BATCH.md` §A-1 exists with the exact command | ❌ W0 (hold branch only) | ⬜ pending |
| 139-01 T2 + 139-05 T2 | 139-01 / 139-05 | 1 / 4 | ISSUE-03 | — | Correction precedes implementation (D-10) | git | 3-ref blob equality on `eprom.cpp` (+ `memory.cpp`) → 1 unique SHA | ✅ passes today | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `139-GH15-COMMENT.md` — the deliverable (ISSUE-01, ISSUE-02)
- [ ] `139-GH15-BODY-AMENDMENT.md` — optional second action (D-01)
- [ ] `139-GH15-ORIGINAL-CRITERIA.md` — the **nine** boxes captured verbatim, for the `<details>` block
- [ ] `139-CITATIONS.md` — permalink register + per-anchor verification transcript
- [ ] `139-check-claims.py` — Phase-139-scoped forbidden-phrase gate (the v1.30 checker cannot do this job — RESEARCH F-04), with a planted-failure non-vacuity run
- [ ] `.planning/v1.31-OPERATOR-BATCH.md` — **only if** the hold branch is taken

No test-framework install is needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Operator approves the comment's **wording** | ISSUE-03 | Editorial judgement on a public, effectively-irreversible statement | Present the frozen draft in full at a `checkpoint:human-action` gate; record the verdict verbatim |
| Operator **authorizes posting** (separate yes) | ISSUE-03 | An outward network act must never be inferred from a wording approval (D-08) | Ask separately; "approved, hold" is a legitimate distinct answer with its own recorded branch |
| Operator authorizes the **body edit** (default-skipped, third yes) | ISSUE-03 / D-01 | Beyond what ISSUE-01…03 ask for; must never happen by default | Ask only after posting is authorized; default answer is no |
| Whether the proposed amendment is *right* | ISSUE-02 | Nine-box coverage is structural; correctness of each kept/corrected/replaced verdict is editorial | Operator reads the mapping table against the original nine |
| The 6.25 V paragraph reads as a limit on *any* implementation, not an excuse for this one | ISSUE-02 | Tone, not presence | Operator reads the paragraph |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or an explicit human-only justification above
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (only 139-05 Task 1 is human-only; it is immediately followed by 139-05 Task 2's eight automated legs)
- [x] Wave 0 covers all MISSING references — each is owned by a named plan: `139-GH15-ORIGINAL-CRITERIA.md` + `139-CITATIONS.md` → 139-01 · `139-check-claims.py` → 139-02 · `139-GH15-COMMENT.md` → 139-03 · `139-GH15-BODY-AMENDMENT.md` → 139-04 · `.planning/v1.31-OPERATOR-BATCH.md` → 139-05 (hold branch only)
- [x] No watch-mode flags
- [x] Claim gate seen to FAIL on a planted violation before its pass is believed — twice: 139-02 Task 2 Run 1 (four labels) and again in 139-04 Task 2 Step 1, immediately before the default-mode green that licenses the freeze
- [x] No verification in the map is discharged by an executor's self-report: the two that previously were — the capture-vs-RESEARCH byte identity (139-01 T1) and the comment-vs-amendment disposition agreement (139-04 T2) — now each carry their own automated leg, and both legs were exercised green **and** red against mock inputs during plan revision before being written in
- [x] Every `<automated>` command in all five plans parses: extracted from the on-disk bytes and passed through `bash -n` — 40/40 clean, zero surviving HTML entities
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** mapped to plans 139-01 through 139-05 by the phase planner, 2026-08-09; revised 2026-08-09 after plan-checker review (entity-decoded `<automated>` blocks; two self-reported verifications promoted to automated legs). Every row above lands in a named plan's `<verify>` block; the two human-only rows are typed `checkpoint:human-action` in 139-05 Task 1.
