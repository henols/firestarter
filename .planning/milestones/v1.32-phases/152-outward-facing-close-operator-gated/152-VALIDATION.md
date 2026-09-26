---
phase: 152
slug: outward-facing-close-operator-gated
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-21
---

# Phase 152 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `152-RESEARCH.md` §"Validation Architecture" (:1948).
> **Publication phase** — the artifacts under test are *outward-facing text* and *three repo merges*,
> not product code. Every requirement below is provable in software; none requires an AT28C part.
> **⚠ This phase must NOT be run under `--auto`/`--chain`** — every OUT requirement is
> operator-reviewed before posting, and `autonomous: false` alone is not self-protecting.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | **pytest** (present in the devcontainer; 149's sibling suite measured **20 passed in 0.82 s** on 2026-08-21) |
| **Config file** | `firestarter_app/pyproject.toml` supplies `addopts = "-ra -q"` for app-scoped runs. The `.planning`-hosted gate suites take **no** project config and run from their own phase directory. |
| **Quick run command** | `cd .planning/phases/152-outward-facing-close-operator-gated && python3 -m pytest test_check_claims_152.py -q -o addopts=""` |
| **Full suite command** | the quick run **plus** `python3 152-check-claims.py` (file mode) **plus** `timeout 300 python3 ../130-*/check_record_corrections.py` |
| **Estimated runtime** | ~1 s pytest · ~1 s gate · **~24 s** record-corrections (measured 23.3 s, 2026-08-21) |

**Outward-facing / network gates** (read-only `gh`; `gh workflow run` is blocked by the auto-mode classifier)

| Gate | Command |
|------|---------|
| Comment landed (identity) | `gh issue view N --json comments --jq '.comments[-1].body' \| diff -u <frozen draft> -` |
| Comment landed (non-vacuity) | `gh issue view N --json comments --jq '.comments \| length'` — captured **before** and **after**, delta exactly 1 |
| Issue still OPEN | `gh issue view N --json state --jq '.state'` → `OPEN` (gh#21, #11, #12) |
| Release body identity | `gh release view "$TAG" --json body --jq '.body' \| diff -u <frozen draft> -` |
| Release body non-vacuity | `gh release view "$TAG" --json body -q '.body \| length'` — 0 → N |
| Cut version, never predicted | `gh release list --repo <r> --limit 5` read **after** the merge |
| PyPI, independent of GitHub | `curl -s https://pypi.org/pypi/firestarter/json` and assert the tag is in `releases` |
| Merge complete, not re-mergeable | `git -C <repo> cherry origin/beta HEAD` → **all `-`** |

**Traps that invalidate a green run:**

- `addopts` already carries `-q` — **doubling it hides the count line.** Use `-o addopts=""` whenever a count matters.
- `test_check_claims_152.py` needs a **distinct basename**; pytest's default `prepend` import mode collides on a repeated basename when run from `/workspaces` (RESEARCH §C-8).
- `check_record_corrections.py` scans `STATE.md` (339 KB, one ~52k-char line) — **a short timeout returns rc=124 and reads like a RED.** Always `timeout 300`.
- `updatedAt` is **not** a body-edit oracle — it bumps on creation, and comment-level `updatedAt` is `null` on all 30 existing comments (RESEARCH §D-5).
- A blob SHA of a draft proves **intent**, never what GitHub stored.
- `gsd-tools query commit` can **switch branches** on a stale milestone regex — check `HEAD` after every commit (RESEARCH §Pitfall 8).
- A pre-authored gate leg can be structurally **unreachable**. RED proves nothing until the leg is *seen to pass*, and the fix must be **locator-only**.
- Devcontainer python is **3.12**; app CI is **3.11 only**. Point the sibling root at an empty dir before any beta push.

---

## Sampling Rate

- **After every task commit:** `python3 -m pytest test_check_claims_152.py -q -o addopts=""` (sub-second), plus `python3 152-check-claims.py` once any target exists.
- **After every wave:** the above **plus** `timeout 300 python3 ../130-*/check_record_corrections.py`, **plus** (wave 3 onward) `git cherry origin/beta HEAD` in both sub-repos.
- **Before every public post:** file-mode gate **GREEN**, then the blocking operator checkpoint, then the post, then posted-mode gate **plus** the body diff.
- **Phase gate:** all of the above green; all six drafts + `152-LEDGER.md` in `_DEFAULT_TARGETS`; all five posts verified by body diff; both PyPI checks done; `152-MERGE-RECORD.md` written.
- **Max feedback latency:** ~25 s (record-corrections dominates).

---

## Per-Requirement Verification Map

Task IDs are assigned at planning time; this map is the requirement-level contract each task must inherit.

| Req | Behavior to prove | Test Type | Automated Command | File Exists | Status |
|-----|-------------------|-----------|-------------------|-------------|--------|
| OUT-05 | The gate rejects the **specified planted violation** (the pre-amendment criterion-1 wording naming `enable` as returning via `write --sdp-relock`) | integration (subprocess) | `pytest test_check_claims_152.py -q -o addopts="" -k planted_sdp_relock` | ❌ W0 | ⬜ pending |
| OUT-05 | The gate rejects the bare-flag form | integration | same, `-k planted_sdp_relock_bare_flag` | ❌ W0 | ⬜ pending |
| OUT-05 | The permitted **withdrawal** sentence — which must name `write --sdp-relock` — does **not** trip the class | integration | same, `-k withdrawal_sentence_is_permitted` | ❌ W0 | ⬜ pending |
| OUT-05 | The modified `issue-closed` row **still fires** on gh#21/#11/#12 while permitting D-05's required "gh#32 is closed" (RESEARCH §C-5 collision) | integration | same, `-k issue_closed_still_fires` | ❌ W0 | ⬜ pending |
| OUT-05 | `proven-unqualified` rejects `bench-proven`, `datasheet-proven`, `silicon-proven` and permits **only** 152's own caveat spelling — lookbehind **re-derived**, not copied | integration | same, `-k proven_lookbehind` | ❌ W0 | ⬜ pending |
| OUT-05 | Never-vacuous: an empty target list exits **non-zero** | unit | same, `-k never_vacuous` | ❌ W0 (donor leg) | ⬜ pending |
| OUT-05 | Fail-closed: a missing target exits **non-zero** | unit | same, `-k nonexistent_scan_target` | ❌ W0 (donor leg) | ⬜ pending |
| OUT-05 | An unknown basename gets the **full** caveat set | unit | same, `-k unrecognised_basename` | ❌ W0 (donor leg) | ⬜ pending |
| OUT-05 | `CONTEXT.md`, `RESEARCH.md`, `DISCUSSION-LOG.md`, `fixtures/` and the transcript are **not** gate targets (they carry forbidden vocabulary by design) | unit | same, `-k are_not_gate_targets` | ❌ W0 (donor leg) | ⬜ pending |
| OUT-05 | Every added/modified label has an **isolated** fixture — a plant trips exactly its own label, and fails for the forbidden phrase rather than a missing caveat | meta | same, `-k every_forbidden_pattern_has_a_planted_fixture` | ❌ W0 (donor leg) | ⬜ pending |
| OUT-05 | Defaults resolve inside **this** phase's dir and carry the `152-` prefix — the `_HERE` fail-open trap (RESEARCH §C-3) cannot recur | unit | same, `-k defaults_resolve_in_this_phase` | ❌ W0 | ⬜ pending |
| OUT-05 | The env seam is `FIRESTARTER_CLAIMSCAN_TARGETS_152`; present-but-empty yields **zero** targets and rc≠0, never a silent fallback to defaults | unit | same, `-k env_seam` | ❌ W0 | ⬜ pending |
| OUT-05 | **Seen to fail before any pass is believed** — a committed plant-and-revert transcript with the RED **pasted, not described**, one entry per added/modified label | artifact + transcript | `152-CLAIM-GATE-TRANSCRIPTS.md` present, each label's RED block quoting real gate output, then GREEN | ❌ W0/W4 | ⬜ pending |
| OUT-05 | Armed against the **real** artifacts: all six drafts + `152-LEDGER.md` in `_DEFAULT_TARGETS`, list non-empty, every basename has a `_CAVEAT_RULES` entry | integration | same, `-k armed_against_the_real`; then `python3 152-check-claims.py` → rc 0 | ❌ W4 (**149 ordering trap** — a `152-*-SUMMARY.md` cannot enter the list before it exists on disk) | ⬜ pending |
| OUT-01 | The gh#12 reply is **posted**, and its stored body equals the frozen draft | integration | `gh issue view 12 --json comments --jq '.comments[-1].body' \| diff -u 152-GH12-COMMENT.md -` → empty | ❌ W4 | ⬜ pending |
| OUT-01 | It states the ask is half-answered **for a second release**, names Backlog **999.28**, and does **NOT** name `write --sdp-relock` as shipped | source-scan on the draft **and** the posted body | file-mode gate rc 0 on the draft **plus** `-k planted_sdp_relock` proving the gate would have caught the negative case | ❌ W2/W4 | ⬜ pending |
| OUT-01 | The adaptation diff against `137-GH12-COMMENT.md` is **committed** (D-14) | source | `git log --oneline -- 152-GH12-COMMENT.md` non-empty **and** a committed `diff -u 137-GH12-COMMENT.md 152-GH12-COMMENT.md` artifact | ❌ W2 | ⬜ pending |
| OUT-02 | gh#21 carries the comment; body identical to the frozen draft; comment count +1 | integration | body diff **plus** count before/after | ❌ W4 | ⬜ pending |
| OUT-02 | The fresh-run request is stated as answerable **because** the report now identifies its firmware — and names **both** install halves (beta install **plus** `firestarter fw --install`), because 153's fix is in the FIRMWARE (RESEARCH §B-8) | source-scan | required-phrase leg in the gate's `_CAVEAT_RULES` for the gh#21 draft basename | ❌ W2 | ⬜ pending |
| OUT-02 | gh#21 is **still OPEN** after commenting | integration | `gh issue view 21 --json state --jq '.state'` → `OPEN` | ❌ W4 | ⬜ pending |
| OUT-03 | gh#11 carries the comment; body identical; count +1; still **OPEN** | integration | body diff + count + state | ❌ W4 | ⬜ pending |
| OUT-03 | It answers the FIX-06 completion-vs-data-landed conflation **and** discharges the 2026-08-03 `CMD_ERASE` commitment as a kept-late promise, not a silence (RESEARCH §D-4) | source-scan | required-phrase leg for the gh#11 draft basename | ❌ W2 | ⬜ pending |
| OUT-04 | Both release bodies are posted and identical to their frozen drafts | integration | `gh release view "$TAG" --json body --jq '.body' \| diff -u <draft> -` per repo | ❌ W4 | ⬜ pending |
| OUT-04 | Body length moved **0 → N** (non-vacuity) | integration | `gh release view "$TAG" --json body -q '.body \| length'` per repo | ❌ W4 | ⬜ pending |
| OUT-04 | The announced version is **read**, never predicted, and actually contains `lock-status` | integration | `gh release list` read post-merge; then `git -C firestarter_app cherry origin/beta HEAD` all `-` **and** `lock-status` present on `origin/beta` | ❌ W3 | ⬜ pending |
| OUT-04 | Each body carries the milestone-level non-claim **exactly once** — no AT28C silicon tested, `0x0D` stays `UNVERIFIED` (D-11) | source-scan | `REQUIRED_CAVEAT_PATTERNS` leg per release-note basename, `-k required_caveat_once` | ❌ W0/W2 | ⬜ pending |
| OUT-04 | The `write --sdp-relock` **withdrawal** is stated explicitly, naming Backlog 999.28 — announced neither as shipped nor left unmentioned | source-scan | required-phrase leg **plus** the fifth-class negative leg on the same file | ❌ W2 | ⬜ pending |
| OUT-04 | PyPI carries the cut tag, verified **independently** of GitHub | integration | `curl -s https://pypi.org/pypi/firestarter/json` → tag in `releases`. ⚠ RESEARCH §A-5: PyPI is **behind** GitHub on the *stable* channel (`2.0.8` absent) — the notes must not claim it installable | ❌ W3 | ⬜ pending |
| D-04 | Both sub-repo merges landed via **PR to `beta`**, and beta is not re-mergeable by mistake | integration | `git -C <repo> cherry origin/beta HEAD` → all `-`; **never** `merge-base --is-ancestor` (v1.30's squash made it a false negative) | ✅ mechanism exists | ⬜ pending |
| D-04 | ⚠ The app merge is **not** a fast-forward — 85 ahead / **7 behind**, with 5 milestone commits already upstream under different SHAs (RESEARCH §A-1). Conflict resolution must be funded, not assumed | integration | `git -C firestarter_app rev-list --left-right --count origin/beta...HEAD` re-measured at merge time; `git cherry` classifying every commit | ✅ commands exist | ⬜ pending |
| D-05/D-11/D-15 | The hand-edited amendments are **present** | unit | `grep -c` on each amendment's own dated marker in ROADMAP.md / REQUIREMENTS.md / PROJECT.md | ❌ W1 | ⬜ pending |
| D-05/D-11/D-15 | …and landed **without** a whole-file `_normalizeMd` blast | unit | `git diff --numstat` per file, changed-line count within the amendment's expected band. **Do NOT use "byte-unchanged except…"** — that criterion class has broken here before | ❌ W1 | ⬜ pending |
| D-05/D-15 | The record-corrections gate still passes after the hand-edits | integration | `timeout 300 python3 ../130-*/check_record_corrections.py` → rc 0 | ✅ green today (23.3 s) | ⬜ pending |
| D-12 | `152-LEDGER.md` exists, is a **hard-coded gate target**, and carries live-captured HEADs measured in-plan | source + integration | `152-LEDGER.md` in `_DEFAULT_TARGETS`; `python3 152-check-claims.py` rc 0; HEAD SHAs match `git -C <repo> rev-parse HEAD` at write time | ❌ W4 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `152-check-claims.py` — sibling of `149-check-claims.py` (531 lines) with the **four mandatory renames** (RESEARCH §C-2), **two new** forbidden rows (the fifth class, negative-lookahead form — *not* a lookbehind, Python needs fixed width; *not* a verb allow-list, that fails **open**), **one modified** row (`issue-closed`, RESEARCH §C-5), and **two** required-caveat rows.
- [ ] `fixtures/planted_sdp_relock_as_shipped.md` — **the specified planted violation**, verbatim: the pre-amendment criterion-1 wording.
- [ ] `fixtures/planted_sdp_relock_bare_flag.md` — the bare-flag form.
- [ ] `fixtures/planted_issue_closed_still_fires.md` ×3 controls (gh#21 / #11 / #12).
- [ ] `fixtures/clean_control.md` + `fixtures/clean_control_second.md` — the permitted withdrawal sentence and both required caveats, proven clean.
- [ ] `test_check_claims_152.py` — ~20 legs, **subprocess-driven**, **distinct basename**.
- [ ] `152-CLAIM-GATE-TRANSCRIPTS.md` — RED per added/modified label with output **pasted**, then GREEN, then the extension and final-target-list sections.
- [ ] **Re-measure** RESEARCH §A-1, §A-2, §A-4 and §D at the start of the merge plan — they are moving targets and this phase's own merges move them again.
- [ ] Settle RESEARCH Open Question 1 (which method produced 151's 406/111/39 class sizes) **before** any outward sentence cites a count; the robust substitute is "665 of 746 rows refuse; 81 are `read_permitted`".

Framework install: **none needed** — pytest is present and 149's sibling suite is green today.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Operator wording approval before each public post | OUT-01…04 | **Deliberately manual and deliberately per-artifact** (D-03). Five irreversible public acts; approval for gh#12 must not carry to gh#11. The checkpoint mechanism is documented as *not self-protecting* under `--auto`/`--chain`. | A separate **blocking** checkpoint immediately before each post, after that artifact's file-mode gate is GREEN. Restate the `--auto`/`--chain` prohibition in every posting plan's frontmatter. |
| Any manual PyPI dispatch, if the automatic upload fails | OUT-04 | `gh workflow run` is blocked by the auto-mode classifier; settings edits cannot fix it. Read-only `gh run` works. | Operator runs the dispatch. ⚠ RESEARCH §E-3: PyPI upload is now **automatic** (`pypi: needs: github` via `workflow_call`), so this is a fallback, not the path. |
| Merge-conflict adjudication on the app PR | D-04 | 7 commits behind with 5 patch-id duplicates — a semantic call, not a mechanical one. | Operator reviews the PR; `git cherry` classifies each commit before any resolution. |
| That no AT28C part was used, or needed, as evidence | OUT-05 | Nothing to run. **No silicon is cited anywhere**, by construction. | Not performed. The milestone ships AT28C write-path behaviour **software-proven and unvalidated on silicon**. |

**Software-only by construction** (no silicon can be cited as evidence for these, and none is needed): OUT-05 in full, and every claim-gate, record-amendment, merge, and body-diff leg above.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all ❌ MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 25 s
- [ ] Every gate leg **seen to pass** after being seen to fail; every RED **pasted**, never described
- [ ] Every fix that turns a RED green is **locator-only** — no assertion weakened
- [ ] Every `grep`-present amendment paired with a **bounded-diff** assertion
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
