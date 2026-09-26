# Phase 122: CLOSE — honesty ledger, community ask, release decision - Research

**Researched:** 2026-07-30
**Domain:** Milestone close mechanics — dual-repo git merge + GitHub Actions release channels + public issue communication under a validation ceiling
**Confidence:** HIGH (every load-bearing claim below was executed live against the working tree, the GitHub API, and PyPI in this session)

---

## Summary

This phase writes markdown, resolves a two-file merge, pushes two branches, dispatches one workflow,
edits two release bodies, and posts two issue comments. It ships **no product code**. That makes its
risk profile unusual: nothing can break at runtime, but two outward-facing artifacts (a public
prerelease body and two public issue comments) can permanently record an overclaim, and one
irreversible act (a push to `beta` that auto-cuts a release) happens in the middle.

Research found the CONTEXT/ROADMAP framing **substantially correct on intent and materially wrong on
five specific mechanisms**. The two that most change the plan: (1) the merge D-06 treats as a
dangerous three-file conflict is actually a **zero-conflict firmware merge plus a two-file app
conflict whose correct resolution is provably `--ours` wholesale** — the superset proof is mechanical,
not a judgement call; and (2) **D-14's prescribed public answer to `No-Hazmats` is the opposite of
what the shipped code does** — all 19 chips on their pinout are on the REFUSE side of the SDP
allow-set, measured 0/19. Posting D-14 as written would put an overclaim into a public issue in the
one phase whose entire purpose is not overclaiming.

A third finding reframes D-03 from a safety net into the normal path: **6 of the 13 published app
GitHub beta releases never reached PyPI** (b4, b5, b6, b9, b10, b12). The b12 loss is not an
anomaly to guard against; the manual `publish.yml` dispatch is more often required than not.

**Primary recommendation:** Plan the merge as *firmware = fast-forward-equivalent version bump, no
conflict* and *app = `git checkout --ours` on exactly two files, justified by a committed superset
proof*; treat `check_ledger.py` as a known-RED pre-existing condition and never as a CLOSE-01 gate;
and rewrite D-14's `No-Hazmats` answer from "should now work" to the measured refusal before it
reaches the operator wording review.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

*Copied verbatim from `122-CONTEXT.md` §Implementation Decisions. Where research corrected a
decision's stated premise, the correction is cross-referenced in `## Corrections` — the decision
itself stands unless the correction says otherwise.*

**The beta publish and the community ask are coupled — CLOSE-02 / CLOSE-03**

- **D-01: Phase 122 publishes the v1.22 beta itself, then comments.** `origin/beta` is at
  `3.0.0b13` in both sub-repos and b13 predates every line of v1.22 work, so there is nothing
  published for the standing tester to test. Precedent: v1.21's Phase 115 drove the b11 publish
  in-phase while tag and final merge stayed separate. It is also the only way a `dev test` report can
  be trustworthy — b13 lacks Phase 121's phantom-erase fix and would auto-tag `community-fail` on a
  good run, the exact evidence-poisoning the 121-before-122 ordering invariant exists to prevent.
  **Rejected:** publish, bench-smoke-test the install/flash path, *then* comment — the consequence is
  owned, not incidental, and is recorded in `<specifics>`. **Rejected:** comment now and publish
  later — it matches the 2026-07-28 promise but leaves the re-test ask hollow and the follow-up ping
  landing outside the milestone with nobody owning it.

- **D-02: The ask is a plain write plus verify first, with `dev test` offered second and optional.**
  The plain write directly answers *"did your symptom go away"* — the INIT abort at `0x005555` either
  reproduces or it doesn't, and there is no new command to learn. `dev test` offered second yields the
  dedup-fingerprinted structured report. The reporter's chip already holds throwaway random data, so
  the full-device write is safe on it. **Phase 121 D-04's obligation is inherited:** the ask must
  state plainly that `dev test` always writes to the chip and expects a blank or scratch part.
  **Rejected:** plain write only (forgoes the artifact Phase 121 exists to make trustworthy).
  **Rejected:** `dev test` only (buries their specific symptom inside a sweep verdict, and 28C is
  non-UV so Phase 121 D-01 gives it no stop-and-ask).

- **D-03: Both channels must be verified public before any comment goes out.**
  PyPI `--pre` *and* a GitHub prerelease carrying the board `.hex` assets, then an explicit resolution check — Phase 115's
  Step 0 pattern. Without the PyPI half the tester's `pip install --pre firestarter` silently gets
  b13 and *"it still fails"* means nothing. **This is exactly how b12 was lost:** the app GH release
  was created by a PAT, which suppressed `release: published`, so CI looked green while PyPI never
  moved. **Rejected:** commenting as soon as CI reports success. **Rejected:** GitHub-only, pointing
  the tester at a release asset (leaves PyPI `--pre` on b13 for everyone else and asks a volunteer for
  a non-standard install).

- **D-04: The cut is `3.0.0b14` and the beta series simply continues.** What the CI auto-increment
  produces for free, and consistent with b8→b13. The host structurally cannot order pre-release
  suffixes anyway (`_probe_port`'s capture regex truncates them, Phase 120 D-16), so a larger number
  buys no capability detection — HOST-06 already detects via the `0x86` ack. **This closes the
  version-numbering question Phase 120 D-16 explicitly routed to CLOSE-03.** **Rejected:** `3.1.0b1`
  — it breaks the auto-increment path, invites *"when is 3.1.0 stable?"* when stable is
  operator-gated, and re-couples release numbering to HOST-06's correctness, the coupling D-16
  refused. **Rejected:** b14 plus a recorded `3.1.0` stable-candidate marker.

**The push mechanics — CLOSE-03**

- **D-05: Accept the auto-fire — the merge IS the b14 cut.** Both repos carry
  `on: push: branches: [beta]` with auto-increment from a git-tag scan and both sit at b13, so the
  merge push cuts b14 by itself in both. Sequence: record the decision, merge `--no-ff`
  v1.22→`beta` in both repos, push, let CI cut b14 (firmware `.hex` assets, app GH release, and the
  version-bump auto-commit onto `beta`), manually dispatch `publish.yml` for PyPI, verify both
  channels, then comment. No trigger surgery and no spurious extra release — this is the *"do the cut
  FROM beta so the merge IS the cut"* option the v1.21 post-mortem named. **Rejected:** avoid — a
  `workflow_dispatch` cut from the branch with an explicit `-f beta_version=3.0.0b14` plus temporarily
  disabling `push: beta` (two repos of trigger edits, and a forgotten re-enable silently kills every
  future beta). **Rejected:** accept-plus-cleanup of the stray b12 (outward-facing deletion of
  something public for three days that may already be installed).

- **D-06: The merge conflicts are resolved on the v1.22 branch, with the gate proven there first.**
  Merge `beta` **into** the branch, resolve `version.h` and `submit.py`/`test_submit.py`, run
  GATE-03's nine-row non-regression set green on the result, and only then merge out to `beta`. So
  `beta` never sees an unproven intermediate state, and the push that fires CI is a clean merge. The
  conflict is real and specific: `version.h` is b11 on the branch versus b13 on `beta`, and the same
  five `quick-260728-ahy` commits exist on **both** sides with different SHAs, layered on top of
  Phase 121's rewrite of the very same `submit_report` step order. **Rejected:** resolving during the
  outbound merge (the proof then happens after CI has already cut and published b14). **Rejected:**
  additionally asserting each of the five hotfix behaviours survives by name.

- **D-07: The `v1.22` tag and the meta-repo gitlink bump stay with `/gsd-complete-milestone`.**
  Mirrors v1.21 exactly — Phase 115 published in-phase while tag and final merge stayed separate.
  Keeps this phase's verification scope on things it can prove, and the tag then points at a beta
  already published and channel-verified. Note the meta repo's gitlinks are currently stale at
  `0048b3d` / `96e0622`, one phase behind; correcting them is the close ritual's job, not this
  phase's. **Rejected:** doing publish, gitlink bump and tag all in-phase. **Rejected:** publish plus
  gitlink bump in-phase with the tag deferred.

- **D-08: The b14 prerelease body is hand-written and carries the ceiling.**
  Criterion 4 demands every claim in the closing documentation match the validation
  ceiling; an auto-generated commit-list body makes no claim at all, yet a reader will infer *"SDP
  works."* The body says plainly that the lock and unlock sequences are emitted byte-exact across all
  four `0x0D` pinouts and verified in software, and that no AT28C silicon was tested. **Rejected:**
  leaving CI's generated body and keeping the honesty statement in the ledger and issue comments only.
  **Rejected:** hand-writing both repos' bodies with cross-links into the Phase 121 GATE-02 docs.

**The honesty ledger — CLOSE-01**

- **D-09: The honesty ledger is a new `122-LEDGER.md`; `PROTOCOL-LEDGER` is verified, never edited.**
  CLOSE-01 asks that `0x0D` *stays* `UNVERIFIED` there — a check, not a write. The
  `PROTOCOL-LEDGER` pair lives at `.planning/v1.16/ledger/` as a closed-milestone artifact whose
  header pins firmware `a296195`, which is not even an ancestor of the live line; editing it would
  make that stale pin newly load-bearing. This is the same discipline that refuses to edit a closed
  milestone's REQUIREMENTS wording. **Rejected:** `122-LEDGER.md` plus one cross-reference line in the
  `0x0D` row (would also re-run `check_ledger.py` against a v1.16-scoped schema). **Rejected:** a full
  v1.22 addendum section appended to `PROTOCOL-LEDGER.{md,json}`.

- **D-10: The community silicon datapoint gets an EIGHTH CORRECTION and a premise-confirmed row.**
  `datapaganism`'s 2026-07-27 run on b11 reproduced the exact
  inverted-check INIT abort — `ERROR: EEPROM timeout at 0x005555: wrote 0x20 got 0xff` — on a real
  AT28C256. That is a claim class the ceiling called unprovable, and it confirms the **defect**, not
  the **fix**, which is a genuinely new and asymmetric fact worth its own correction block in the same
  register as the seven before it. It raises Phase 116's TRACE-06 from software-predicted to
  community-corroborated **without** touching `support_status` or the `UNVERIFIED` status. State the
  provenance honestly — an issue-comment paste, no captured logs beyond the text, board revision and
  firmware build unconfirmed. **Rejected:** a ledger row with no PROJECT.md correction. **Rejected:**
  keeping it out of the evidence record entirely and citing it only in the reply.

- **D-11: The ledger is organised as claim-class rows carrying explicit non-claims.**
  Each row pairs a permitted wording with what it does NOT prove. Roughly eight classes — per-pinout emission byte-exactness, measured
  host-side timing, `0x0D`-scoped fail-closed refusal, `DEV_TOOLS` invariance, other families
  byte-identical, the host refusing before the wire, the defect silicon-confirmed by community
  report, and the flash deltas. This makes the permitted-versus-forbidden line auditable instead of
  re-deriving `REQUIREMENTS.md`, whose per-requirement parentheticals already carry the evidence.
  **Rejected:** claim classes plus a 41-row requirement-to-class appendix. **Rejected:** one row per
  v1 requirement across all 41.

- **D-12: The ledger carries a short section on what the milestone chose not to prove.** SDP-F1 to
  SDP-F8's deferral reasons in one line each, plus the two trade-offs Phase 121 recorded and owned —
  an off-TTY `dev test` writes silicon with nobody consenting, and `lockable-proms.md` ships roughly
  300 datasheet-compiled rows with no provenance header. A close that lists only wins reads as
  overclaiming even when every individual claim is true. **Rejected:** leaving the negative space to
  REQUIREMENTS.md's Future Requirements and Out of Scope tables. **Rejected:** recording only the two
  owned trade-offs and dropping the SDP-F deferrals.

**The community replies — CLOSE-02**

- **D-13: gh#12 is answered and left open pending a silicon re-test.** The 2024 question was yours —
  *"always unlock, write and lock again? A special command?"* — and the reporter never answered it, so
  the reply answers it for them with the decided policy: auto-unlock stays default-on and **reported**,
  `--skip-sdp-unlock` declines it, `firestarter dev sdp <chip> enable|disable` gives standalone
  control, and `--sdp-relock` is deferred. Closing the issue would read as *"verified fixed"*, which
  CLOSE-02 forbids regardless of the comment text. **Rejected:** answering and closing as implemented
  with the ceiling stated in the closing comment. **Rejected:** adding an
  `awaiting-silicon-verification` label — `gh issue edit --add-label` fails on a missing label exactly
  the way `create` does.

- **D-14: gh#12's drifted asks are addressed inline and nothing is split out.** Two sentences each —
  `pdr0663`'s Windows `ClearCommError` crash was on app 1.3.44 with firmware 1.4.2, a pre-3.0
  transport failure the COBS hardening replaced, worth a fresh report if it reproduces on b14;
  `No-Hazmats`'s AT28C parts should now work; `AndersBNielsen`'s SST39SF SDP request is SDP-F6,
  deferred with its stated reason. Costs nothing and opens no issue nobody will own. **Rejected:**
  splitting `pdr0663`'s crash into its own issue (filing on someone else's behalf from a year-old
  paste with no way to confirm it still reproduces). **Rejected:** answering only the SDP question
  and leaving three participants unanswered after one to two years.

- **D-15: gh#11's reply gives the full account and credits the reporter's b11 reproduction.** It names
  both defects — the `/WE`-inhibited command emitter, and the page-verify **conflation** that let a
  partial write report success, which is the likelier cause of their actual 2024 symptom — explains
  that b11 turned a silent partial write into an honest hard failure at INIT (so their re-test looking
  *worse* than 2024 was the fix landing halfway, not a regression), states plainly that nothing is
  silicon-verified here, and thanks them for the reproduction that raised a software prediction to a
  confirmed defect. **Rejected:** the same content without the credit framing. **Rejected:** the short
  version, which loses the one explanation they are most likely to want.

- **D-16: Both comment drafts sit behind a blocking operator wording review, then post via `gh`.**
  The Phase 116 plan 116-07 precedent — its PROJECT.md correction sat behind
  an explicit blocking operator wording review. The draft lands in the phase record so what was said
  is auditable against the ledger, and the ceiling wording gets a human read before it reaches two
  strangers. **Rejected:** the operator posting both manually (posted text can drift from the
  committed draft and nothing proves what went out). **Rejected:** posting directly in-plan once the
  channels verify — it removes the human read on outward-facing text in the one phase whose entire job
  is not overclaiming.

### Hard sequencing constraints these decisions imply

1. **The accept/avoid/cleanup decision is recorded before any push to `beta`.**
2. **`beta` → branch merge and a green nine-row gate precede the branch → `beta` merge** (D-06).
3. **b14 exists and both channels are verified public before any comment is posted** (D-03).
4. **The blocking operator wording review precedes any comment reaching GitHub** (D-16).
5. **`122-LEDGER.md` and the EIGHTH CORRECTION exist before the prerelease body and the two comment
   drafts are written** (D-08, D-11, D-15).
6. **CLOSE-01's verification runs against the tree that actually gets merged.**
7. **The PyPI publish is a manual `workflow_dispatch`** with a required `tag` input (D-03, D-05).

### Claude's Discretion

- **Every word of the two comment drafts and the prerelease body**, subject to three constraints: the
  permitted claim and forbidden claim come verbatim in substance from the validation ceiling; the
  `dev test` mention carries Phase 121 D-04's always-writes warning; and nothing may be phrased as
  *"verified fixed."*
- **The shape and column set of `122-LEDGER.md`** — D-11 fixes that rows are claim classes each
  carrying a permitted wording and an explicit non-claim; the table layout, row count and section
  order are open.
- **How the b14 channel verification is evidenced** — a committed transcript, a small script, or a
  named check in the plan's task list. Only the fact that it ran before the comments is fixed.
- **Plan ordering**, subject to the seven sequencing constraints above.
- **Whether the two comment drafts live in one artifact or two.**

### Deferred Ideas (OUT OF SCOPE)

Declined with a reason during discussion: deleting the stray b12 prereleases (D-05); a bench
smoke-test of the b14 install/flash path (D-01); `3.1.0b1` and a `3.1.0` stable-candidate marker
(D-04); splitting `pdr0663`'s Windows crash into its own issue (D-14); an
`awaiting-silicon-verification` label on gh#12 (D-13); editing `PROTOCOL-LEDGER` with a v1.22
addendum or cross-reference row (D-09).

Carried forward, still not taken: `dev test`'s release-channel disposition (999.15 / gh#8); a
read-only `dev test` mode; the wider CLI flag re-design; the end-to-end `infoic.xml` `page_size`
decode phase; widening `_probe_port`'s `[\d.x]+` version capture; **SDP-F1 to SDP-F8**; hardening
`derive_plan`'s vestigial `locked_destructive`; Unity-teardown SIGABRT root cause; all-84-chips
table-driven trace coverage.

`todo.match-phase 122` returned 12 matches, all ≤0.6 and all generic keyword overlap. None is close
work. `fold-response-code-into-log-macro` is declined again (conflicts with 117 D-05 / 118 D-02 /
119 D-12).
</user_constraints>

---

<phase_requirements>
## Phase Requirements

Verbatim from `.planning/REQUIREMENTS.md:102-104` — all three currently `[ ]`.

| ID | Description | Research Support |
|----|-------------|------------------|
| **CLOSE-01** | `0x0D` stays `UNVERIFIED` in `PROTOCOL-LEDGER`, **zero** chips change `support_status`, and the 84-chip count is unchanged | All three sub-claims verified live and mechanically re-runnable: `PROTOCOL-LEDGER.md:27` reads `**UNVERIFIED**`; `tests/test_sdp_db_invariant.py` passes 4/4 pinning the 84 count; `tools/diff_db.py` exits 0 with `PASS: all 2 changed chips explained (0 new, 0 removed)`; `tools/check_no_community_support_status_write.py` exits 0. Exact commands in `## Code Examples`. **`check_ledger.py` must NOT be used — it is pre-existing RED (C-4).** |
| **CLOSE-02** | gh#12 answered with the decided auto-unlock policy; gh#11 followed up; both framed as "here is what changed — please re-test", never as a verified fix | Both issues confirmed OPEN and public in `henols/firestarter_prom`; `gh` authenticated as `henols` with ADMIN permission and `workflow` scope. Full thread content read and quoted in `## Community Thread Ground Truth`. The policy D-13 must state is verified against the live `dev sdp --help` text. **D-14's `No-Hazmats` answer is corrected in C-5 — it currently overclaims.** |
| **CLOSE-03** | The accept/avoid/cleanup decision is made and recorded **before** any push | D-05's auto-fire premise verified in both workflow YAMLs; auto-increment provably yields `b14` (highest tag = `3.0.0b13` in both repos, `3.0.0b14` absent from both); the PAT suppression is documented in `publish.yml`'s own comment and confirmed live in `beta-release.yml`'s `GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`. **C-3 reframes the PyPI gap as the norm, not an anomaly.** |
</phase_requirements>

---

## Corrections to CONTEXT.md / ROADMAP Framings

Every row was executed live in this session. **Plan from this table, not from the prose it corrects.**

| # | Stated in CONTEXT/ROADMAP | Live fact | Impact on the plan |
|---|---------------------------|-----------|--------------------|
| **C-1** | D-06: "resolve `version.h` and `submit.py`/`test_submit.py`" — implying a three-file conflict spanning both repos | **The firmware inbound merge has ZERO conflicts.** `git merge-tree --write-tree --messages HEAD origin/beta` in `/workspaces/firestarter` returns a clean tree (`cc86c8b`) with no conflict output. The only difference from branch HEAD is `include/version.h` b11→b13, auto-merged (only `beta` touched it since the fork base). | Delete the firmware conflict-resolution task. The firmware inbound merge is a one-line version bump. Its nine-row/native re-proof is *cheap insurance*, not a resolution proof. |
| **C-2** | D-06: `version.h` is part of the conflict set | **`firestarter/__init__.py` (the app's version file) does NOT conflict either** — it auto-merges b11→b13. The app conflict set is **exactly two files**: `firestarter/submit.py` and `tests/test_submit.py`. `version.h` is a firmware path and has no app analogue. | The plan's conflict list is two paths, both in `firestarter_app`. A plan that names `version.h` as a conflict cannot execute. |
| **C-3** | D-03 / `<specifics>`: "This is exactly how b12 was lost" — framed as a singular incident | **6 of 13 app GH beta releases never reached PyPI**: GH has b1–b13; PyPI has only b1, b2, b3, b7, b8, b11, b13. Missing: **b4, b5, b6, b9, b10, b12**. | The manual `publish.yml` dispatch is the *normal* path (46% historical failure), not a guard against a rare event. Strengthens D-03; the plan should treat the dispatch as a mandatory step with its own verification, never as a contingency. |
| **C-4** | `<canonical_refs>`: `check_ledger.py` is "the machine-checked half. Untouched under D-09." | **`check_ledger.py` exits 1 (BLOCK) today**, with 2 `LEDGER-01` violations: rows `0x05`/`0x06` carry `matrix_family` `flash4`/`flash3`, which **v1.19 Phase 104 renamed** to `5v_page`/`nor_unlock`. `validation_matrix_spec.json` now lists `['5v_page','eeprom28c','eprom','flash_intel','nor_unlock','sram']`. Pre-existing, unrelated to v1.22 (`tools/validation_matrix_spec.json` is not in the `beta...HEAD` diff). | **Never gate CLOSE-01 on `check_ledger.py`.** CLOSE-01's text does not mention it. Record its RED as a known-and-explained condition with the v1.19 cause. The `0x0D` row's own join key (`eeprom28c`, protocols `[13]`) is valid — only `0x05`/`0x06` are stale. |
| **C-5** | D-14: "`No-Hazmats`'s AT28C parts should now work" | **The opposite is true, measured 0/19.** `No-Hazmats` bought "an EPROM of that size — 2K x 8". Every 2K×8 part in the `0x0D` bucket sits on pinout `DIP24_2816`, and the live allow-set refuses **all 19 of 19** `DIP24_2816` chips (`sdp_capability_for_entry`, measured). Seven are refused as `pre-SDP generation`, twelve as `unrecognised`. `dev sdp --help` states this in the shipped text: *"Refused on protocol-0x0D parts with no SDP command decoder at all (the two FRAM parts and the pre-SDP `2804`/`2816`/`2817` generation)"*. Additionally `AT28C16` is `support_status: adapter-required`, and **SDP-F7** (magic addresses unverified for AT28C16/AT28C04) and **SDP-F8** (`DIP24_2816` has no `static-high-pins`, verified below) both name that exact family. | **Rewrite this sentence before the wording review.** The honest answer: their part is on the *refuse* side by design — v1.22 deliberately does not send SDP commands to pre-SDP silicon because the bytes would land as data at truncated magic addresses. Whatever they hit is therefore **not** the gh#12 SDP-lock symptom, and v1.22 does not address it. |
| **C-6** | D-08: "an auto-generated commit-list body makes no claim at all" | **Both b13 release bodies are empty strings**, not generated commit lists. `beta-release.yml`/`beta-build.yml` pass no `body` and no `generate_release_notes` to `softprops/action-gh-release@v2`. | D-08's conclusion stands and is *better* motivated. Mechanically: there is nothing to preserve, so the body is *added* post-cut via `gh release edit <tag> --notes-file <path>`. No careful overwrite needed. |
| **C-7** | D-03: "a GitHub prerelease carrying the board `.hex` assets" (as one of two channels) | **Only the firmware release carries assets** — `firestarter_leonardo.hex`, `firestarter_uno.hex`, `firestarter_uno328pb.hex`. The **app** GH release carries **zero assets**; it is a tag+release marker only, and PyPI is the app's sole distribution channel. | State the two channels precisely: (a) **PyPI** `3.0.0b14` for the host app, (b) the **firmware** GH prerelease for the three `.hex` files. A verification that only checks the app GH release proves nothing a user can install. |
| **C-8** | Implicit in D-05/D-06 ("the gate", "CI") | **`ci.yml` never runs on a `beta` push** — it triggers on `push: branches: [main]` and `pull_request` only. Same for firmware `build.yml` (`main` only). The merge push fires **only** `beta-release.yml` / `beta-build.yml`. Further, `ci.yml`'s ruff gate is scoped `ruff check firestarter/ tests/` — so the 4 pre-existing `ruff check` findings and 4 `ruff format` drift files (all in `tools/` + `.github/scripts/`) are structurally invisible to CI. | The gates the push actually runs are enumerated in `## Release Mechanics` — three per repo. Do not plan for `ci.yml` output on the beta push. Do not "fix" the pre-existing ruff findings; they are out of CI scope and out of phase scope. |
| **C-9** | Task prompt / memory: "milestone branches for v1.22 were forked off the v1.21 tag, NOT `beta`" | **v1.22 forked off `beta`.** Fork base = `git merge-base HEAD origin/beta` = `ecf35ea` (firmware) / `7c5dd13` (app) = *"Merge v1.21-community-chip-validation-command into beta (v1.21 milestone close)"*, which is on `beta`. The annotated tag `v1.21` resolves (`v1.21^{commit}`) to **that same commit**, so both descriptions coincide here. The fork-off-the-previous-version exception applied to v1.15 and v1.21, **not** v1.22. | No archaeology surprise. It is also *why* the merge is small: `beta` is only 2 (firmware) / 7 (app) commits ahead of the fork point. |
| **C-10** | `<canonical_refs>`: "`PROJECT.md` §v1.22 — **all seven** ⚠ correction blocks" | There are **six** ordinal ⚠ blocks: `SECOND REFRAMING`, then `THIRD`–`SEVENTH CORRECTION`. Five carry the literal word CORRECTION. | **D-10's `EIGHTH` ordinal is still correct** — the sequence ends at SEVENTH, so the next ordinal is EIGHTH. Only CONTEXT's count is off by one. |
| **C-11** | `<specifics>`: "the double-applied hotfix… any resolution that compiles and passes will *look* right" | **A mechanical superset proof exists.** All five beta hotfix behaviours are present on branch HEAD, and **all 60** of `beta`'s `test_submit.py` test functions exist among HEAD's **77** (`comm -23 beta head` = empty set), including all ten added by the five hotfix commits. So `--ours` provably loses nothing. **But a hunk-by-hunk hand-merge is actively dangerous** (see C-12). | Resolve by whole-file `git checkout --ours`, and commit the superset proof as the justification. This is *stronger* than D-06's nine-row gate alone, and it retires the "weakest available proof" worry. |
| **C-12** | D-06's implied hand-resolution of `submit.py` | The four `submit.py` conflict hunks are structurally interleaved: hunks 3 (L644–666) and 4 (L676–707) **sandwich a shared region** (L667–675, a `submit_via_browser(...)` call) that HEAD needs **twice** — once on the comment-degrade path, once on the new-issue gh-degrade path. Taking "ours" on hunks 3 and 4 *textually* leaves a dangling `elif url:` that silently rebinds to the wrong `if`. Verified: HEAD's `submit_report` tail contains two distinct `submit_via_browser(` calls; the conflicted tree collapses them into one. | **Forbid hunk-level resolution in the plan.** Mandate `git checkout --ours -- firestarter/submit.py tests/test_submit.py`, then `git diff HEAD -- <those two paths>` must be **empty** as the proof the resolution is exactly branch HEAD. |
| **C-13** | `<code_context>`: "`diff_db.py` … Do not report a two-change result as a failure" | Correct, and lower-risk than implied: **`diff_db.py` performs the interpretation itself** and exits **0** printing `PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)`. | Use the exit code. No human reading of the "2" is required. |

**Confirmed as stated (stop re-deriving these):** `origin/beta` at `3.0.0b13` in both repos ✓;
branch tips `48c36e5` / `c3c9424` ✓; 42/2 and 75/7 ahead/behind ✓; the five `quick-260728-ahy`
commits double-applied with the SHAs listed ✓; `SUBMIT_REPO = "henols/firestarter_prom"` at
`submit.py:73` ✓; meta gitlinks stale at `0048b3d` / `96e0622` ✓; `.planning/config.json` lists four
sub_repos and is uncommitted ✓; working-tree dirt exactly as named ✓; `a296195` is an ancestor of
neither `beta` nor HEAD ✓; `PROTOCOL-LEDGER.md:27` `0x0D` = `**UNVERIFIED**` ✓; 84 chips at
`algorithm == 13`, all `chip_id_check: false` ✓; both issues open and public with the described
comment history ✓; `gh` authenticated as `henols` ✓; the nine-row gate is nine rows and all green ✓.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Honesty ledger (`122-LEDGER.md`) | Meta repo `.planning/` | — | Planning artifact; neither sub-repo ships it |
| EIGHTH CORRECTION | Meta repo `.planning/PROJECT.md` | — | The project-level evidence record |
| CLOSE-01 verification | `firestarter_app` tooling (`tools/`, `tests/`) + meta `.planning/v1.16/ledger/` (read-only) | — | The proofs already live where the data lives; nothing new is built |
| Nine-row non-regression gate | `firestarter_app` (host, scans firmware source cross-repo) | `firestarter` (scanned subject) | Host-side gates that read firmware text — the cross-repo asymmetry that broke 4× in Phase 117 |
| Merge resolution | `firestarter_app` git (2 files) | `firestarter` git (0 files) | C-1/C-2 |
| b14 cut | GitHub Actions on `beta` (both repos) | — | Auto-fire; not driven from the workstation |
| PyPI publish | GitHub Actions `publish.yml` via manual dispatch | — | C-3; never a side effect of the merge |
| Prerelease bodies | GitHub Releases API via `gh release edit` | — | Post-cut edit; CI writes an empty body (C-6) |
| Community replies | GitHub Issues API via `gh issue comment` | Committed drafts in `.planning/` | D-16: the draft is the auditable artifact, the API call is the delivery |
| The `v1.22` tag + gitlink bump | **Out of scope** — `/gsd-complete-milestone` | — | D-07 |

---

## Runtime State Inventory

This phase changes no source and installs nothing, but it **does** mutate remote runtime state.
The canonical question — *after every file is updated, what still has the old value cached, stored,
or registered?* — answered per category:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | **None** — no database, collection, key or user_id is touched. `chip_database.json` is byte-identical between `beta` and the branch (absent from the `beta...HEAD` diff). Verified. | none |
| **Live service config** | **Two GitHub repos' `beta` refs** (moved by the outbound merge, then moved *again* by each workflow's `git-auto-commit-action` version bump — so the local `beta` will be 1 commit behind the remote after CI runs). **Two GitHub Releases** (`3.0.0b14`, created by CI with an empty body, then edited). **One PyPI project** (`firestarter`, new `3.0.0b14` sdist/wheel). **Two GitHub issues** (comments appended). None of this state lives in git. | Re-`git fetch` after CI; `gh release edit` for bodies; `gh workflow run publish.yml`; `gh issue comment` |
| **OS-registered state** | **None** — no Task Scheduler, pm2, launchd or systemd registration references this milestone. | none |
| **Secrets / env vars** | `secrets.PERSONAL_ACCESS_TOKEN` (app `beta-release.yml`), `secrets.GITHUB_TOKEN` (firmware `beta-build.yml`), `secrets.PYPI_API_TOKEN` (`publish.yml`). **All three are consumed, none is created, renamed or rotated by this phase.** No `.env`, no SOPS key involved. | none — but see `## Security Domain` on never echoing them |
| **Build artifacts / installed packages** | The devcontainer has `firestarter` installed editable from the branch (`pip install -e .`), so it will **not** reflect the published b14 — a local `firestarter --version` proves nothing about PyPI. `.pio/build/` is stale local output. `.coverage` is untracked dirt. **Two new tags** `3.0.0b14` are created by CI in both repos (a local `git tag --list` will not show them until fetch). | Verify PyPI via the **PyPI JSON API or a clean-env install**, never via the local editable install |

**Also stale and deliberately left alone (D-07):** the meta repo's committed gitlinks `0048b3d` /
`96e0622` against working tips `48c36e5` / `c3c9424`. Phase 121's own footer records that gitlinks
"stay PINNED (submodule pointer bumps deliberately uncommitted per this project's pattern)."

---

## Merge Ground Truth (D-06)

### Firmware — `/workspaces/firestarter`

```
branch: v1.22-at28c-software-data-protection-lifecycle @ 48c36e5
origin/beta @ 6611fba  (VERSION "3.0.0b13")
branch version.h        VERSION "3.0.0b11"
ahead/behind:           42 / 2   (the 2 are both "Apply automatic changes" version bumps)
fork base:              ecf35ea == v1.21^{commit}  (on beta)
```

`git merge-tree --write-tree --messages HEAD origin/beta` → tree `cc86c8b`, **zero conflicts**.
`git diff --stat HEAD cc86c8b` → `include/version.h | 2 +-`. Merged value: `3.0.0b13`. **[VERIFIED: git]**

### App — `/workspaces/firestarter_app`

```
branch: v1.22-at28c-software-data-protection-lifecycle @ c3c9424
origin/beta @ 1bb5599  (__version__ = "3.0.0b13")
branch __init__.py      __version__ = "3.0.0b11"
ahead/behind:           75 / 7   (5 quick-260728-ahy hotfixes + 2 version bumps)
fork base:              7c5dd13 == v1.21^{commit}  (on beta)
```

`git merge-tree --write-tree --messages HEAD origin/beta` → **2 conflicts**:

```
CONFLICT (content): Merge conflict in firestarter/submit.py     (4 hunks)
CONFLICT (content): Merge conflict in tests/test_submit.py      (5 hunks)
```

`firestarter/__init__.py` **auto-merges** to `3.0.0b13`. **[VERIFIED: git]**

### The superset proof — why `--ours` is correct, not merely convenient

| Beta hotfix behaviour | Present on branch HEAD? | Evidence |
|---|---|---|
| `SUBMIT_REPO` retargeted to the project tracker | ✓ | `submit.py:73` = `"henols/firestarter_prom"` |
| `gh` tier permission-independent + surfaces stderr | ✓ | `submit.py:272`, `:425` (`getattr(proc,"stderr","")`) |
| Browser tier stops claiming success when unreachable | ✓ | `submit.py:472`, `:501` |
| Caller owns the fallback narration | ✓ | `submit.py:640`, `:669` (`"degrading to"`) |
| Created issue URL echoed on success | ✓ | `submit.py:681`, `:683` (`"Report filed"`) |

```bash
# All 60 of beta's test functions exist among HEAD's 77 — empty output = nothing lost.
comm -23 <(git show origin/beta:tests/test_submit.py | grep -o '^\s*def test_[a-z0-9_]*' \
             | sed 's/^ *def //' | sort) \
         <(git show HEAD:tests/test_submit.py | grep -o '^\s*def test_[a-z0-9_]*' \
             | sed 's/^ *def //' | sort)
# → (empty)
```

All ten test functions added by the five hotfix commits (`591c819 379bb30 98c7de6 2b9e8dd 0050277`)
are present on HEAD by name. **[VERIFIED: git]**

### The trap that makes hunk-level resolution wrong (C-12)

HEAD's `submit_report` tail calls `submit_via_browser(` **twice**. The conflicted merge collapses
both into one shared region between hunks 3 and 4:

```
<<<<<<< HEAD        (hunk 3, L644)   if prior_url: … comment_via_gh_fn … "gh comment failed"
=======             (L659)           if gh_available(…): url = submit_via_gh(…) … "gh tier failed"
>>>>>>> origin/beta (L666)
                    (L667-675)       console=console,) ; submit_via_browser(title, body, …)   ← SHARED, needed TWICE
<<<<<<< HEAD        (hunk 4, L676)   else: "Comment added" ; return ; if not dedup_ran: … ; if gh_available(…) …
=======             (L706)           (empty)
>>>>>>> origin/beta (L707)
                    (L708-711)       elif url: "Report filed: {url}" ; else: "Report filed to …"
```

Taking `--ours` on hunks 3 and 4 textually yields **one** `submit_via_browser` call, leaving
`elif url:` (L708) bound to `if url is None:` from the *comment* path rather than the *create* path.
That compiles, and the suite may still pass. **Mandate whole-file `--ours` and assert
`git diff HEAD -- firestarter/submit.py tests/test_submit.py` is empty.** **[VERIFIED: git]**

### Prescribed sequence

```bash
# --- inbound (on the v1.22 branch), APP ---
cd /workspaces/firestarter_app
git fetch origin
git merge --no-ff origin/beta            # conflicts in exactly 2 files
git checkout --ours -- firestarter/submit.py tests/test_submit.py
git add firestarter/submit.py tests/test_submit.py
git diff --cached HEAD -- firestarter/submit.py tests/test_submit.py   # MUST be empty
git commit                                # __init__.py auto-merged to 3.0.0b13

# --- inbound, FIRMWARE (no conflict) ---
cd /workspaces/firestarter
git fetch origin
git merge --no-ff origin/beta            # clean; version.h -> 3.0.0b13
```

Then the nine-row gate + full suites, **then** the outbound `--no-ff` merge to `beta` and the push.

---

## Release Mechanics (verified live — do not re-derive)

### What the merge push actually triggers

| Repo | Workflow | Trigger | Fires on beta push? |
|------|----------|---------|---------------------|
| `firestarter` | `beta-build.yml` | `push: [beta]` (+ `workflow_dispatch`) | **YES** |
| `firestarter` | `build.yml` | `push`/`pull_request`: **`main` only** | no |
| `firestarter_app` | `beta-release.yml` | `push: [beta]` (+ `workflow_dispatch`) | **YES** |
| `firestarter_app` | `ci.yml` | `push`: **`main` only**; `pull_request` | no |
| `firestarter_app` | `publish.yml` | `release: published` **+ `workflow_dispatch` (required `tag`)** | **NO** (suppressed — see below) |

`paths-ignore` cannot suppress either beta workflow: the app merge carries 42 non-ignored paths
(`firestarter/*.py`, `pyproject.toml`, `tests/**`) and the firmware merge carries `src/`, `include/`,
`test/`, `platformio.ini`, `tools/`. **[VERIFIED: workflow YAML + `git diff --name-only`]**

### Gates each beta workflow runs (this is the whole gate set for the cut)

**`firestarter/beta-build.yml`:** catalog validity → codegen drift (`include/messages.h`, `git diff
--exit-code`) → `pio test -e native` → `pytest tests/ -v` → version bump + auto-commit → `pio run`
→ Release with `files: .pio/build/**/firestarter_*.hex`, `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`.

**`firestarter_app/beta-release.yml`:** `pip install -e .[test]` → catalog validity → codegen drift
(`firestarter/messages.py`, ruff-normalized then `git diff --exit-code`) → `pytest tests/ -v` →
version bump + auto-commit → Release with `GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}`.

Note what beta-release.yml does **not** run: ruff, mypy, coverage floor, the vector catalog gate,
the CLI smoke test. Those live only in `ci.yml` (main/PR).

### The PyPI suppression — root cause, in the workflow's own words

`firestarter_app/.github/workflows/publish.yml`:

```yaml
on:
  release:
    types: [published]
  # workflow_dispatch added 2026-05-20 (Phase 20 E2E-01 recovery): when a
  # release is created by another workflow (e.g. beta-release.yml) using a
  # PAT that lacks `workflow` scope, GitHub suppresses the release.published
  # event from triggering downstream workflows. ...
  workflow_dispatch:
    inputs:
      tag:
        description: 'Release tag to publish to PyPI (e.g. 3.0.0b1, 2.0.7).'
        required: true
```

`beta-release.yml` does use that PAT. The firmware workflow deliberately does not, with its own
comment: *"PERSONAL_ACCESS_TOKEN is not configured on the firmware repo… the firmware Release has no
downstream workflow that needs `release.published` to cascade."* **[VERIFIED: workflow YAML]**

### Historical evidence that the dispatch is the norm (C-3)

```
app GH releases : b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13   (13)
PyPI 3.0.0bN    : b1 b2 b3       b7 b8         b11     b13     ( 7)
missing on PyPI :          b4 b5 b6    b9 b10      b12         ( 6 = 46%)
PyPI info.version (latest stable) = 2.0.7
```
**[VERIFIED: `gh release list` + PyPI JSON API]**

### Why the cut is `b14` (D-04)

`.github/scripts/update_version.py` → `compute_beta_version()` → `_git_tag_scan_fallback(base)`
where `base = major.minor.patch` read from the version file. Merged value is `3.0.0b13` → base
`3.0.0` → `git tag --list '3.0.0b*'` → max `13` → **`3.0.0b14`**. Robust either way: if the version
file had stayed `b11`, base is still `3.0.0`. Both repos have tags `3.0.0b1`…`3.0.0b13`;
`3.0.0b14` does not exist in either. **[VERIFIED: script source + `git tag` + `gh release view`]**

### Release bodies (C-6, C-7)

`gh release view 3.0.0b13 --json body` → `""` in **both** repos. Assets: firmware = 3 `.hex`;
app = **none**. Both workflows pass no `body` and no `generate_release_notes`.
Add the body with `gh release edit 3.0.0b14 --repo <r> --notes-file <path>`. **[VERIFIED: gh API]**

### Post-cut local/remote divergence — easy to trip on

Each workflow's `git-auto-commit-action` pushes a version-bump commit **onto `beta`**. After CI,
local `beta` is 1 commit behind the remote in each repo. Any later local operation on `beta` must
`git fetch` first. This is the mechanism that produced `a981642` and `6611fba`.

---

## CLOSE-01's Verification Mechanisms (they exist — do not rebuild)

All four executed live in this session, from the paths shown.

| # | Mechanism | Command | Live result |
|---|-----------|---------|-------------|
| 1 | `0x0D` still `UNVERIFIED` | `grep -n '`0x0D`' .planning/v1.16/ledger/PROTOCOL-LEDGER.md` | line 27, `… \| **UNVERIFIED** \| No on-hand silicon. Rep chip: AT28C256 …` |
| 2 | 84-count + `chip_id_check` invariant | `cd firestarter_app && python3 -m pytest tests/test_sdp_db_invariant.py -q` | `4 passed` |
| 3 | DB identity | `cd firestarter_app && python3 tools/diff_db.py` | exit **0**, `PASS: all 2 changed chips explained (0 new chips confirmed; 0 chips removed from baseline)` |
| 4 | No code path writes `support_status` | `cd firestarter_app && python3 tools/check_no_community_support_status_write.py` | exit **0**, `PASS: scanned ../firestarter/diagnostic_report.py, parse_devtest_issue.py; 0 support_status writes (sole write locus stays tools/build_db.py)` |

**Independent live measurement of the numbers themselves** (a second, non-test path to the same
facts — useful because it does not depend on the test's own assertions):

```
total chips in chip_database.json : 746
algorithm == 13                   :  84
chip_id_check among those 84      : {False}   (all)
support_status among those 84     : supported 75, adapter-required 9
```

### The four `0x0D` pinouts named by the ceiling — with counts

The permitted claim says *"across all four `0x0D` pinouts"*. Measured composition:

| Pinout | Chips | SDP ALLOW | SDP REFUSE |
|--------|------:|----------:|-----------:|
| `DIP28_28C64` | 35 | 15 | 20 |
| `DIP24_2816` | 19 | **0** | **19** |
| `DIP32_28C512_EEPROM` | 18 | 18 | 0 |
| `DIP28_28C256` | 12 | 10 | 2 |
| **Total** | **84** | **43** | **41** |

The 43/41 split reproduces STATE.md's derived partition exactly (`infoic.xml` INFOIC2PLUS `flags`
bit 15). **[VERIFIED: `sdp_capability.sdp_capability_for_entry` executed over all 84 entries]**

> **This table is the ledger's most important row.** *Emission traced byte-exact for a pinout* and
> *the operation permitted on parts with that pinout* are **different claims**. For `DIP24_2816` the
> first is true and the second is false for all 19 chips. A ledger row that says "all four pinouts"
> without this distinction reads as broader capability than shipped.

### `check_ledger.py` — pre-existing RED (C-4)

```bash
cd /workspaces/.planning/v1.16/ledger && python3 tools/check_ledger.py; echo $?
# FAIL: ledger self-consistency check found violations:
#   LEDGER-01: row bucket=0x05 matrix_family='flash4' not in validation_matrix_spec families:
#              ['5v_page','eeprom28c','eprom','flash_intel','nor_unlock','sram']
#   LEDGER-01: row bucket=0x06 matrix_family='flash3' not in … (same list)
# Total: 2 violation(s). Exit 1 (BLOCK).
# 1
```

Cause: v1.19 Phase 104 renamed `flash_type_3`/`flash_type_4` → `flash_nor_unlock`/`flash_5v_page`;
the v1.16 ledger's `matrix_family` join keys never followed. `tools/validation_matrix_spec.json` is
**not** in the `beta...HEAD` diff, so this is not v1.22's damage. The `0x0D` row's own join key
(`eeprom28c`, `protocols: [13]`, `rep_chip: AT28C256`) is present and valid.
**Do not gate CLOSE-01 on this tool.** **[VERIFIED: executed]**

### The ledger header's stale firmware pin (D-09 — premise holds)

`PROTOCOL-LEDGER.md:4` → *"**Firmware under test:** submodule commit `a296195` (Phase 89 HEAD, incl.
CR-01 fix)"*. Ancestry, measured in `/workspaces/firestarter`:

```
a296195 ancestor of origin/beta ? NO
a296195 ancestor of HEAD (v1.22)? NO
a296195 = "fix(89): CR-01 — restore eprom CHECK_CHIP_ID unconditional ERROR …"  (2026-06-26)
```

D-09's reasoning is sound as stated. `119-MEASUREMENT.md:558` independently supports it: *"the
`PROTOCOL-LEDGER` … records bench-verification status against silicon."* **[VERIFIED: git]**

---

## GATE-03's Nine-Row Non-Regression Set (D-06)

Source: `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-NONREGRESSION.md`
§5 (line 275), *"The CORRECTION-4 item-4 gate table — now nine rows"*, explicitly handed to Phases
120, 121 and 122. **All eleven commands re-run in this session at branch HEAD: all PASS.**

Run from `/workspaces/firestarter_app`:

| # | Command | Baseline |
|---|---------|----------|
| 1 | `python3 tools/check_no_log_in_sdp_window.py` | PASS |
| 2 | `python3 -m pytest tests/test_check_no_log_in_sdp_window.py -q` | PASS |
| 3 | `python3 -m pytest tests/test_sdp_table_parity.py -q` | PASS |
| 4a | `python3 tools/check_is_memory_cmd_no_ifdef.py` | PASS |
| 4b | `python3 -m pytest tests/test_check_is_memory_cmd_no_ifdef.py -q` | PASS |
| 5 | `python3 tools/gen_sdp_bus_config.py` (then assert `git -C ../firestarter status --porcelain` clean) | PASS |
| 6 | `python3 -m pytest tests/test_sdp_bus_config_drift.py -q` | PASS |
| 7 | `python3 -m pytest tests/test_revision_constants_parity.py -q` | PASS |
| 8 | `python3 -m pytest tests/test_dispatch_mirror.py -q` | PASS |
| 9a | `python3 tools/check_dispatch.py` | PASS |
| 9b | `python3 tools/check_devtest_orchestrator.py` | PASS |

**Why re-running it after the inbound merge is still correct** even though C-1/C-2 shrink the merge:
rows 9a/9b scan `firestarter/submit.py` and `cli_handlers.py`, and `submit.py` is one of the two
conflicted files. Row 9b's own PASS line names `submit.py` explicitly. So the merge *does* touch a
scanned file, and the `--ours` resolution must be re-proved against the gate.
**[VERIFIED: executed]**

### Full-suite baselines at branch HEAD (pre-merge)

| Suite | Command | Result |
|---|---|---|
| App pytest | `cd firestarter_app && python3 -m pytest -q` | **1150 passed**, 29 snapshots passed |
| Firmware native | `cd firestarter && pio test -e native` | **141/141 succeeded** (17 suites, 46.5 s) |
| Firmware script tests | `cd firestarter && python3 -m pytest tests/ -q` | **8 passed** |
| Catalog validity | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (73 messages, version 1).` |
| Catalog three-way identity | `cmp` meta ↔ fw, meta ↔ app | both exit 0 |
| mypy watermark | `cd firestarter_app && python3 tools/check_mypy_watermark.py` | `1 error (watermark: 35)` — 34 below |
| `default_envs` | `firestarter/platformio.ini:16` | `uno, uno328pb, leonardo` (so `pio run` = 3 envs) |

**Pre-existing, out of CI scope, NOT this phase's work (C-8):** `ruff check .` → 4 findings in
`tools/audit_coverage_matrix.py`, `tools/catalog/codegen.py`, `tools/catalog/codegen_vectors.py`.
`ruff format --check .` → 4 drift files: those latter two plus `tools/check_mypy_watermark.py` and
`.github/scripts/update_version.py`. **Zero findings in `firestarter/` or `tests/`**, which is
exactly what `ci.yml` scopes to. Matches Phase 121's GATE-03 record.

---

## Community Thread Ground Truth

`gh repo view henols/firestarter_prom` → `visibility: PUBLIC`, `hasIssuesEnabled: true`,
`viewerPermission: ADMIN`. `gh auth status` → `henols`, scopes `gist, read:org, repo, workflow`
(so `gh workflow run` is available). **Neither issue carries any label** — consistent with D-13's
decision to skip `--add-label`. **[VERIFIED: gh API]**

### gh#11 — *"Issues with AT28C256 Reading / Writing"* (D-15)

`OPEN`, author `datapaganism` (display name "Alen Karnil"), created 2024-09-26, **12 comments**.

**The 2024 symptom, verbatim from the original body** — note it reported *success*:

```
PS D:\dev\firestarter-1.0.13> firestarter write at28c256 .\1.bin
Sending file .\1.bin in blocks of 512 bytes
100%, address: 0x7E00 - 0x8000
File sent successfully in 339.49 seconds
```
> *"Reading the eeprom after writing to it reveals that only some of it has been properly burned."*

Their input file is *"32Kb of random data"* — **D-02's "throwaway data, safe to write" premise
holds, verified from their own words.** They also state they *"did the rev 2 mod"*, and ran Python
3.8 on Windows.

**This is the conflation bug, exactly as D-15 frames it:** a partial write that reported success.
The FOURTH CORRECTION item 2 is right that it is a conflation, not a sampling-rate, defect.

**The live exchange (comments 10–12):**
- `datapaganism` 2026-07-27: reflashed, read fine, `ERROR: EEPROM timeout at 0x005555: wrote 0x20 got 0xff` on write
- `henols` 2026-07-28: *"Sorry it hasn't been fixed 😔 the issue was moved. But there will be a fix soon and I will let you know."*
- `datapaganism` 2026-07-29: **"That's fine, happy to test for you."**

**Practical note:** their recent comments arrive via **email reply**, so each carries a large quoted
signature and notification block. Post the reply with `gh issue comment` (clean markdown) — do not
mirror that formatting.

### gh#12 — *"AT28Cxxx Write Protection Enable/Disable missing"* (D-13, D-14)

`OPEN`, author `humbertocsjr`, created 2024-09-15, **8 comments**.

**The unanswered question is `henols`' own, comment 1, 2024-09-16:**
> *"What is the behavior you are expecting or how do you want it to work? Always unlock, write and
> lock the chip again? A special command for unlocking and locking? What is the use cases you can
> see? Since it's a rear behavior of a chip I don't want it over shadow more common functionally."*

D-13's framing is exact — the reporter never answered, and the reply answers it for them.

**The three drifted participants, as they actually wrote (D-14):**

| Who | When | What they actually said | Honest disposition |
|---|---|---|---|
| `AndersBNielsen` | 2024-09-16 | Wants the sequences for the **`sst39sf010`** — *"At the very least the 'chip erase' and 'byte program' operations."* Plus: *"The most important part is to make sure firestarter doesn't try to put VPP on any pin."* | **SDP-F6**, deferred (*"multiplies the no-silicon problem across settled bench evidence"*). His VPP concern is already satisfied — `0x0D` is 5V-only and never asserts the VPP regulator. Worth saying. |
| `pdr0663` | 2025-06-21 | AT28C256 write failure. Log header confirms **app `1.3.44`, Python 3.12.3, Windows 11**, and the debug dump shows the **pre-v1.20 `'type': 4` axis**. | D-14's "app 1.3.44" ✓. **The "firmware 1.4.2" detail is NOT visible in the retrievable comment text** — see A1 in the Assumptions Log. The pre-3.0 transport framing is sound; `'type': 4` alone dates it before the v1.20 protocol-only dispatch. |
| `No-Hazmats` | 2026-04-02 | *"I was looking for an EPROM of that size — **2K x 8** … I experienced this issue when I tried to erase and write to them."* Asks for a recommendation. | **C-5: D-14's "should now work" is wrong.** All 19 `DIP24_2816` chips are REFUSED. `AndersBNielsen` already answered them (2026-04-05) recommending `W27C512`. |

### The auto-unlock policy D-13 must state — verified against shipped help text

`python3 -m firestarter.main dev sdp --help` on the branch:

```
Usage: … dev sdp [OPTIONS] EPROM {enable|disable}

  Enable or disable Software Data Protection (SDP) on an AT28C-family EEPROM.
  … On this chip family the resulting protection state cannot be read back
  afterward (Phase 117 D-05, Phase 119 D-12), so neither direction can be
  confirmed -- a successful run means only that the command sequence was
  **emitted**, nothing more.

  Refused on protocol-0x0D parts with no SDP command decoder at all (the two
  FRAM parts and the pre-SDP ``2804``/``2816``/``2817`` generation), and on
  every non-0x0D protocol.

Options:
  -y, --yes  Bypass the confirm prompt on a TTY. … off a TTY this flag is
             REQUIRED -- without it the command refuses rather than proceeding
             unattended.
```

`--skip-sdp-unlock` confirmed at `cli_handlers.py:509-510`, threaded through
`eprom_operations.py:180/208/1612/1657`. `dev test` confirmed to take **zero options**
(`cli_handlers.py:1955-1964`: *"Takes ZERO options -- CHIP is the only argument (D-05, Phase 121)"*).
**[VERIFIED: executed / source]**

> The help text's own *"a successful run means only that the command sequence was **emitted**,
> nothing more"* is already ceiling-compliant. **Reuse this wording** in the comments — it is
> shipped, reviewed, and cannot drift from the product.

---

## Measured Figures the Ledger Must Cite (measured, never predicted)

The established pattern is *"every claim is judged against the live measured figure."* These are the
live figures, with sources.

**Timing — SDP unlock sequence, six writes against a 600 µs budget (`6 × AT28C_TBLC_MAX_US`)**
(`119-MEASUREMENT.md:451-453`):

| Board | Duration | Headroom |
|---|---:|---|
| Leonardo | **568 µs** | 32 µs / 5.3 % |
| Uno | **412 µs** | 188 µs / 31.3 % |
| uno328pb | **424 µs** | 176 µs / 29.3 % |

F-118-01 separately measured **572 µs** on the Leonardo — a 4 µs difference from the 568 µs above,
same emitter and board class. Cite one, note the other; do not average them.

**Timing — page-load per-byte worst interval vs the 100 µs datasheet maximum**
(`AT28C_TBLC_MAX_US`, `eeprom_28c.cpp:54`; `119-MEASUREMENT.md:420-433`): Uno **84 µs** (84 %),
Leonardo **88 µs** (88 %). D-16 explicitly declined a runtime budget check on this path — these are
context, **not a gate**.

**Flash** (`119-09-PLAN.md:161-162,224`): LOCK-06's **3348 B** is a **superseded pre-117 figure**.
Live Leonardo headroom at the Phase 119 base was **2992 B** (`25680/28672`) because **+204 B**
(Phase 117) and **+152 B** (Phase 118) were already spent; Phase 119 lands at **2600 B free**, with
*"no threshold claim beyond 'fits'"*. Phase 121's final builds: Leonardo `26072/28672`, Uno
`23932/32256`, uno328pb `23976/32384` → Leonardo free = **2600 B**, consistent. `-D DEV_TOOLS` costs
**1292 B**.

> **`119-MEASUREMENT.md:33-34` records a correction the ledger must respect:** *"LOCK-06 is a **flash
> budget** (bytes of program memory) and **F-118-01 is a timing budget** (microseconds per byte load)
> — those are different budgets, and PROJECT.md's directive conflates them."* Keep them in separate
> claim-class rows.

**Counts:** 84 `algorithm == 13` chips; **43 ALLOW / 41 REFUSE**; four pinouts 35/19/18/12; UV axis
**301/301** via `electrical-type` (the old `algorithm == 0x0B` proxy measured 32/301); 746 total DB
entries; 736 dispatchable, 10 confirmed non-dispatchable; **66 of 84** — *not* "all 84" — is Phase
116's honest trace-coverage figure (THIRD CORRECTION).

---

## Architecture Patterns

### The close's data flow

```
                    ┌───────────────────────────────────────────────┐
   REQUIREMENTS.md  │  Validation Ceiling: permitted / forbidden     │
   §Validation ─────▶  claim  (the single normative source)          │
   Ceiling          └───────────────────┬───────────────────────────┘
                                        │  (D-11: distilled into claim classes)
                                        ▼
                          ┌─────────────────────────────┐
   119-MEASUREMENT ──────▶│      122-LEDGER.md          │◀────── CLOSE-01 verification
   PROJECT.md corrections │  claim class → permitted     │        results (4 mechanisms,
   Phase SUMMARY files    │  wording + explicit NON-claim│        run on the MERGED tree)
                          └──────┬───────┬───────┬──────┘
                                 │       │       │   (constraint 5: ledger FIRST)
              ┌──────────────────┘       │       └──────────────────┐
              ▼                          ▼                          ▼
   ┌─────────────────────┐   ┌────────────────────┐   ┌────────────────────────┐
   │ PROJECT.md          │   │ b14 prerelease     │   │ gh#11 + gh#12 comment  │
   │ EIGHTH CORRECTION   │   │ bodies (×2 repos)  │   │ drafts (committed)     │
   └─────────────────────┘   └─────────┬──────────┘   └───────────┬────────────┘
                                       │                          │
                        ┌──────────────┘                          │
                        │  requires b14 to EXIST                  │ D-16 BLOCKING
                        │                                         │ operator wording
   ┌────────────────────┴──────────────────────────┐              │ review
   │  CLOSE-03 decision recorded  (constraint 1)   │              │
   │                 │                             │              ▼
   │                 ▼                             │   ┌────────────────────┐
   │  beta → branch merge  (2 files, --ours)       │   │ gh issue comment   │
   │                 │                             │   │  ×2  (issues stay  │
   │                 ▼                             │   │      OPEN)         │
   │  nine-row gate + full suites GREEN            │   └────────────────────┘
   │                 │        (constraint 2)       │              ▲
   │                 ▼                             │              │
   │  branch → beta merge --no-ff  +  PUSH ────────┼──▶ CI: b14 cut          │
   │                                               │    (+version auto-commit)│
   │                 ┌─────────────────────────────┼──▶ gh workflow run       │
   │                 │  (constraint 7, MANUAL)     │    publish.yml -f tag=…  │
   │                 ▼                             │              │           │
   │  CHANNEL VERIFY: PyPI b14 + fw .hex assets ───┼──────────────┘           │
   │                        (constraint 3) ────────┼──────────────────────────┘
   └───────────────────────────────────────────────┘
```

### Pattern 1: Verify-don't-edit a closed milestone's artifact

**What:** When a requirement says a value *stays* X, read and assert it; never write the file.
**When to use:** CLOSE-01 against `PROTOCOL-LEDGER` (D-09).
**Why it is load-bearing here:** editing `PROTOCOL-LEDGER.md` would make its stale `a296195`
firmware pin — an ancestor of neither `beta` nor HEAD — newly load-bearing, and would drag the
v1.19-broken `check_ledger.py` into the phase's gate set.
**Precedent:** the same discipline that leaves a closed milestone's REQUIREMENTS wording unedited
(LOCK-04, LOCK-06, HOST-04, 121 D-06/D-17).

### Pattern 2: Record a mechanism correction in phase artifacts; never edit `REQUIREMENTS.md`

**What:** When a requirement's stated mechanism is narrower or wrong, satisfy the *intent*, record
the correction in the phase record, leave the requirement text alone.
**Applies to:** C-4 (CLOSE-01's implied `check_ledger.py`), C-5 (D-14's wording), C-1/C-2 (D-06's
conflict set). All belong in `122-LEDGER.md` and/or the EIGHTH CORRECTION.

### Pattern 3: Honesty lives in the message text, never in a status code

Established at 117 D-05, 118 D-02, 119 D-12, 120 D-11. Here it generalises: honesty lives in the
**prose**, not in the fact that an issue was left open or a release was marked `prerelease: true`.
`prerelease: true` is not a caveat a reader will decode as "unverified on silicon."

### Pattern 4: A superset proof beats a green suite

C-11's `comm -23` empty set proves `--ours` loses nothing. Prefer a structural proof of *what is
present* over an outcome proof of *what passed*. This is the same instinct as GATE-01's
planted-violation fixtures: prove the gate can fail, not merely that it passed.

### Pattern 5: Blocking operator wording review before outward-facing text

Precedent: plan 116-07. Mechanically: the draft is committed to `.planning/` **first**, the operator
reads it, and the delivery step re-reads the **committed file** (`gh issue comment --body-file
<path>`) so the posted text provably equals the reviewed text. `--body-file`, not `--body "…"`.

### Anti-Patterns to Avoid

- **Hunk-level conflict resolution on `submit.py`** — C-12. Produces compiling, test-passing, wrong code.
- **Gating on `check_ledger.py`** — C-4. Fails on a v1.19 rename this phase did not cause.
- **Treating "CI is green" as channel evidence** — the whole point of D-03; and `ci.yml` does not even run.
- **Verifying PyPI via the local editable install** — `pip install -e .` means `firestarter --version` reports the branch, not PyPI.
- **Writing "all four pinouts" without the ALLOW/REFUSE split** — reads as broader capability than shipped (C-5).
- **Writing "all 84"** — the honest trace figure is 66 of 84 (THIRD CORRECTION).
- **Iterating `planning.sub_repos`** — it lists four repos, two of them v1.29 PY32 scratch. Name `firestarter` and `firestarter_app` explicitly.
- **`gh issue edit --add-label` / `gh issue create --label`** — both abort on a missing label. Neither issue has any label.
- **`--force` push, history rewrite, or deleting a published release** — forbidden; b12 stays (D-05).
- **A path-scoped `git diff` as a cleanliness proof** — can pass vacuously. Use `git status --porcelain` (SEVENTH CORRECTION item 9).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Prove the 84-count and `chip_id_check` invariant | A new assertion script | `pytest tests/test_sdp_db_invariant.py` | TRACE-05's test, no skipif, already pins the count itself |
| Prove the chip DB is untouched | A JSON differ | `python3 tools/diff_db.py` | Interprets its own result and exits 0 on the 2 explained changes (C-13) |
| Prove no code writes `support_status` | A grep | `python3 tools/check_no_community_support_status_write.py` | Exists; names its scanned files in the PASS line |
| Cross-repo non-regression | A new sweep | `119-NONREGRESSION.md` §5's nine rows | Authored and explicitly handed to this phase |
| Channel-verification artifact shape | A new format | `115-VALIDATION.md` | The Step 0 both-channels-public precedent D-03 reuses |
| Decide the next beta number | Manual reasoning | Let `update_version.py`'s tag scan do it | Provably yields b14; a hand-set `beta_version` re-introduces D-05's rejected trigger surgery |
| Compute the SDP allow/refuse split | A hand-curated table | `sdp_capability.sdp_capability_for_entry(entry, name)` | The derived ground truth (43/41); a curated table is exactly what Phase 120 replaced |
| Gate outward-facing wording | Trust review alone | Committed draft + `--body-file` delivery | Proves posted == reviewed (D-16) |

**Key insight:** CLOSE-01 is the rare requirement whose entire verification surface already exists
and is already green. The failure mode is not "the check is missing" — it is "a plan invents a fifth
check, or resurrects a sixth (`check_ledger.py`) that is already RED for unrelated reasons."

---

## Common Pitfalls

### Pitfall 1: The `submit.py` conflict resolves to compiling, passing, wrong code

**What goes wrong:** Hunk-by-hunk `--ours` collapses two `submit_via_browser` call sites into one,
rebinding `elif url:` to the wrong `if`.
**Why:** hunks 3 and 4 sandwich a shared region HEAD needs twice (C-12).
**Avoid:** whole-file `git checkout --ours`; assert `git diff HEAD -- <2 paths>` empty.
**Warning signs:** a merged `submit_report` containing exactly one `submit_via_browser` call in its
tail, or a resolved `submit.py` shorter than HEAD's 688 lines.

### Pitfall 2: Commenting before PyPI actually moved

**What goes wrong:** the tester's `pip install --pre firestarter` silently resolves b13; *"it still
fails"* becomes uninterpretable and the milestone's own evidence is poisoned.
**Why:** the PAT-created release suppresses `release: published` — historically **46 %** of the time
(C-3).
**Avoid:** verify against the PyPI JSON API (or a clean-env `pip download`), not the local editable
install, not the workflow's green tick.
**Warning signs:** a green `beta-release.yml` run with no corresponding `publish.yml` run.

### Pitfall 3: Local `beta` is stale immediately after CI

**What goes wrong:** a follow-up local operation on `beta` rejects, or worse, gets force-reasoned.
**Why:** `git-auto-commit-action` pushes the version bump onto `beta` after your push.
**Avoid:** `git fetch origin` before any post-cut `beta` operation; expect `beta` 1 ahead.
**Warning signs:** `! [rejected] beta -> beta (fetch first)`.

### Pitfall 4: Overclaiming to `No-Hazmats`

**What goes wrong:** D-14's "should now work" is posted; a stranger buys/keeps parts on the belief
v1.22 fixed them; the phase whose job is not overclaiming overclaims publicly and permanently.
**Why:** their part is 2K×8, and 19/19 `DIP24_2816` chips are REFUSED (C-5).
**Avoid:** rewrite before the wording review; state the refusal and *why it is correct*.
**Warning signs:** any sentence pairing "AT28C" with "should now work" without a pinout qualifier.

### Pitfall 5: Firmware renames breaking host source-scanning gates

**What goes wrong:** the host suite stays green while cross-repo gates silently break (4× in Phase
117, 4 of 6 cases in Phase 118).
**Why:** rows 9a/9b scan `firestarter/submit.py` and `cli_handlers.py` — and `submit.py` is one of
the two conflicted files.
**Avoid:** re-run all nine rows **after** the inbound merge, never accept a prior SUMMARY's PASS.
**Warning signs:** `check_devtest_orchestrator.py` PASS line naming a file list that changed.

### Pitfall 6: Executors prematurely ticking requirements

**What goes wrong:** 4× in Phase 116, and 121-08 needed a revert (`2492154`).
**Avoid:** name the exact allowed `CLOSE-NN` id in each dispatch prompt; re-read the requirement
**prose** (not a plan's summary of it) before ticking; re-check `REQUIREMENTS.md` after each plan.
**Note:** CLOSE-02 cannot be ticked until **both** comments are posted; CLOSE-03 not until the
decision is recorded **and** the push happened **and** both channels verified.

### Pitfall 7: `catalog-sync-check.yml` is red-until-`main`-merge by design

`119-NONREGRESSION.md` §6 item 1: the meta workflow checks out both sub-repos at `ref: main`, so it
cannot go green until v1.22 merges to `main` — which is `/gsd-complete-milestone`'s job, not this
phase's. The in-phase proof is the three-way `cmp` + `codegen --check` (all green, re-verified here).
**Do not chase this red.** Related: firmware `build.yml`'s new `pio test -e native_nodevtools` step
(added by Phase 119) also triggers on `main` only, so it first executes for real at that same merge.

### Pitfall 8: `- **D-NN: text**` formatting breaks plan-phase's §13a gate

Close the bold run on **one** line, at most one colon before the closing `**`, never open with a
glyph. Fails closed on wrapped labels and on non-decision bullets whose bold run starts `D-NN`.

### Pitfall 9: STATE.md tooling under-writes and re-clobbers

Call `state.record-session` **first**, then progress/metric/decision calls, then hand-verify
`current_phase_name`, `status`, `stopped_at`, `progress.percent`, `progress.total_plans`.

---

## Code Examples

### CLOSE-01 — the complete verification, runnable as one block

```bash
# Run this AGAINST THE MERGED TREE (sequencing constraint 6), not branch HEAD.
set -e
cd /workspaces/firestarter_app
python3 -m pytest tests/test_sdp_db_invariant.py -q          # 4 passed  (84 count + chip_id_check)
python3 tools/diff_db.py                                     # exit 0: PASS: all 2 changed chips explained
python3 tools/check_no_community_support_status_write.py      # exit 0: 0 support_status writes
grep -c '^| `0x0D` .*\*\*UNVERIFIED\*\*' \
  /workspaces/.planning/v1.16/ledger/PROTOCOL-LEDGER.md       # 1
# Independent second path to the same numbers:
python3 - <<'EOF'
import json, collections
d = json.load(open('firestarter/data/chip_database.json'))
chips = [c for lst in d.values() if isinstance(lst, list) for c in lst]
z = [c for c in chips if c['programming']['algorithm'] == 13]
assert len(chips) == 746 and len(z) == 84, (len(chips), len(z))
assert {c['programming']['chip_id_check'] for c in z} == {False}
print("OK 746 total / 84 at 0x0D / chip_id_check all False")
print("support_status:", dict(collections.Counter(c['support_status'] for c in z)))
print("pinouts:", dict(collections.Counter(c['pinout'] for c in z)))
EOF
# NOTE: do NOT run .planning/v1.16/ledger/tools/check_ledger.py — pre-existing RED (C-4).
```

### The SDP ALLOW/REFUSE split — the ledger's key row

```bash
cd /workspaces/firestarter_app && python3 - <<'EOF'
import json, collections
from firestarter import sdp_capability as sc
d = json.load(open('firestarter/data/chip_database.json'))
z = [c for lst in d.values() if isinstance(lst, list) for c in lst
     if c['programming']['algorithm'] == 13]
by = collections.defaultdict(collections.Counter)
for c in z:
    # sdp_capability_for_entry HARD-FAILS on a programmer dict (Phase 120's
    # anti-vacuity design) -- it needs the db.get_eprom() shape.
    entry = dict(c, **{'protocol-id': 13, 'name': c['part_number']})
    ok, _ = sc.sdp_capability_for_entry(entry, c['part_number'])
    by[c['pinout']][ok] += 1
for p, cc in by.items():
    print(f"{p:24} ALLOW={cc[True]:3} REFUSE={cc[False]:3}")
print("TOTAL ALLOW", sum(cc[True] for cc in by.values()),
      "REFUSE", sum(cc[False] for cc in by.values()))
# DIP28_28C64  ALLOW=15 REFUSE=20 | DIP24_2816 ALLOW=0 REFUSE=19
# DIP32_28C512_EEPROM ALLOW=18 REFUSE=0 | DIP28_28C256 ALLOW=10 REFUSE=2
# TOTAL ALLOW 43 REFUSE 41
EOF
```

### SDP-F8 verified — `DIP24_2816` has no `static-high-pins`

```bash
cd /workspaces/firestarter_app && python3 -c "
import json
p = json.load(open('firestarter/data/pinouts.json'))
for k in ('DIP24_2716','DIP24_2732','DIP24_2816','DIP28_28C64','DIP28_28C256','DIP32_28C512_EEPROM'):
    print(f'{k:22} static-high-pins = {p[k][\"pins\"].get(\"static-high-pins\")}')"
# DIP24_2716  [24]   DIP24_2732  [24]   DIP24_2816  None   (28/32-pin: None)
# NOTE: the key is nested under ["pins"], not at the top level.
```

`SDP-F8` is confirmed exactly as written: the two 24-pin **UV** pinouts force VCC (pin 24) high;
`DIP24_2816` does not. The honest nuance: the 28- and 32-pin `0x0D` pinouts also carry none, so the
asymmetry is specifically among **24-pin** pinouts sharing that socket position — which is precisely
why SDP-F8 says *"Confirm against the shield schematic before acting."*

### The dry-run merge probe (non-mutating — use this before touching either repo)

```bash
for r in firestarter firestarter_app; do
  echo "### $r"; cd "/workspaces/$r"; git fetch origin --quiet
  git merge-tree --write-tree --messages HEAD origin/beta | grep -E '^CONFLICT|^[0-9]{6} ' || echo "  no conflicts"
  cd /workspaces
done
```

### Superset proof for the `--ours` resolution

```bash
cd /workspaces/firestarter_app
comm -23 <(git show origin/beta:tests/test_submit.py | grep -o '^\s*def test_[a-z0-9_]*' \
             | sed 's/^ *def //' | sort) \
         <(git show HEAD:tests/test_submit.py       | grep -o '^\s*def test_[a-z0-9_]*' \
             | sed 's/^ *def //' | sort)
# empty output == every beta test exists on HEAD (60 of HEAD's 77)
```

### Channel verification (D-03) — never via the local editable install

```bash
# PyPI (the host channel)
python3 - <<'EOF'
import json, urllib.request
d = json.load(urllib.request.urlopen('https://pypi.org/pypi/firestarter/json'))
print('3.0.0b14 on PyPI:', '3.0.0b14' in d['releases'])
print('all betas:', sorted((v for v in d['releases'] if '3.0.0b' in v),
                           key=lambda s: int(s.split('b')[1])))
EOF

# Firmware GH prerelease (the .hex channel) — assets are the deliverable
gh release view 3.0.0b14 --repo henols/firestarter \
   --json isPrerelease,assets,body -q '{pre:.isPrerelease, hex:[.assets[].name], body_len:(.body|length)}'
# expect: pre=true, hex=[firestarter_leonardo.hex, firestarter_uno.hex, firestarter_uno328pb.hex]

# App GH release exists but carries ZERO assets (C-7) — presence only, never "installable"
gh release view 3.0.0b14 --repo henols/firestarter_app --json isPrerelease,assets
```

### The PyPI dispatch (constraint 7) and the body edits (C-6)

```bash
gh workflow run publish.yml --repo henols/firestarter_app -f tag=3.0.0b14   # `tag` is REQUIRED
gh run list --repo henols/firestarter_app --workflow publish.yml --limit 1

gh release edit 3.0.0b14 --repo henols/firestarter     --notes-file .planning/phases/122-.../122-RELEASE-NOTES-fw.md
gh release edit 3.0.0b14 --repo henols/firestarter_app --notes-file .planning/phases/122-.../122-RELEASE-NOTES-app.md
```

### Posting the reviewed drafts (D-16) — `--body-file`, never `--body`

```bash
# Proves posted == reviewed: the delivery step re-reads the committed file.
gh issue comment 11 --repo henols/firestarter_prom --body-file <committed-draft-path>
gh issue comment 12 --repo henols/firestarter_prom --body-file <committed-draft-path>
# Both issues STAY OPEN (D-13). Do NOT pass --add-label / -l (aborts; neither issue has labels).
gh issue view 11 --repo henols/firestarter_prom --json state,comments \
  -q '{state:.state, n:(.comments|length), last:.comments[-1].url}'
```

### Proving the CLOSE-03 decision preceded the push

```bash
# The decision artifact's commit must be an ancestor of the merge commit that was pushed to beta.
cd /workspaces && git log -1 --format='%H %ad' -- <decision-artifact-path>
cd /workspaces/firestarter_app && git log origin/beta --oneline -3
# Plus the durable record: the decision artifact is committed in the META repo BEFORE
# either sub-repo push, so `git log --date=iso` timestamps order the two events.
```

---

## State of the Art

| Old approach | Current approach | When changed | Impact here |
|---|---|---|---|
| `matrix_family` = `flash3` / `flash4` | `nor_unlock` / `5v_page` | v1.19 Phase 104 | Breaks `check_ledger.py` against the v1.16 ledger (C-4) |
| Curated SDP-capability list (37/47, then ~74/10) | Derived from `infoic.xml` INFOIC2PLUS `flags` bit 15 → **43/41** | v1.22 Phase 120 | The ledger cites the derived split; `120-SDP-PARTITION.md` supersedes `120-RESEARCH.md` §F-01 |
| `algorithm == 0x0B` UV proxy (32/301) | `electrical-type` structural axis (**301/301**) | v1.22 Phase 121 | Cite 301/301 |
| `mem_type` / `type` dispatch axis | protocol-only dispatch | v1.20 (breaking) | `pdr0663`'s 2025 log shows `'type': 4` — dates it pre-v1.20 |
| v1.21 SUB-01/02: `--submit` explicit + interactive-only | DEVTEST-05: every run asks; dedup first | v1.22 Phase 121 | A recorded **reversal**; `dev test` takes zero options |
| Whole-file blob-SHA identity for `_shared/sdp_expected.h` | Per-array byte-identity | v1.22 Phase 119 | Retired shorthand — do not reach for it |

**Deprecated / stale in this phase's own inputs:** `check_ledger.py` (RED, v1.19 rename);
`PROTOCOL-LEDGER`'s `a296195` pin (ancestor of nothing live); LOCK-06's 3348 B (→ 2992 B → 2600 B);
"all 84" (→ 66 of 84); the memory note recording `beta` at b11/b12 (→ **b13**);
`CLAUDE.md`'s *"Neither sub-repo is committed here"* (imprecise — `.gitmodules` exists and gitlinks
are tracked).

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| `git` | merges, ancestry, `merge-tree` | ✓ | 2.55.0 | — (`--write-tree` needs ≥2.38) |
| `gh` | issue comments, release edits, workflow dispatch | ✓ | auth `henols`, ADMIN on tracker, scopes incl. `workflow` | — |
| `python3` | all host gates | ✓ | 3.12.13 (CI targets 3.9/3.11) | `uv`-provisioned 3.11 venv for CI parity |
| `pytest` | app + firmware script suites | ✓ | 1150 app / 8 fw passing | — |
| `pio` | firmware native suite + `pio run` | ✓ | `/usr/local/bin/pio` | — |
| `ruff` | scoped lint/format | ✓ | 0.16.0 (== CI-resolved) | — |
| PyPI JSON API | channel verification | ✓ | reachable | `pip index versions firestarter --pre` |
| GitHub API | releases, issues, workflows | ✓ | reachable | — |
| AT28C silicon | **the forbidden claim** | **✗** | — | **none — this is the ceiling, not a gap to close** |
| `mcp__context7__*` / web-research MCP | external docs | ✗ | — | not needed: every claim is repo-local or GitHub/PyPI API |

**Missing with no fallback:** AT28C silicon — by design. **Missing with fallback:** nothing blocking.

**Note:** `firestarter` is installed **editable** from the branch in this devcontainer, so
`firestarter --version` reports branch state. It is **not** a valid PyPI channel check (Pitfall 2).

---

## Package Legitimacy Audit

**Not applicable — this phase installs zero external packages.** No `pip install`, `npm install` or
`cargo add` appears anywhere in its scope: the deliverables are markdown artifacts, a two-file git
merge resolution, two `gh release edit` calls, one `gh workflow run`, and two `gh issue comment`
calls. `pyproject.toml`'s dependency set is byte-identical between `beta` and the branch except for
Phase 121's already-merged changes; the `beta...HEAD` diff touches `pyproject.toml` but adds no new
runtime dependency this phase introduces.

`gh`, `git`, `python3`, `pytest`, `pio` and `ruff` are all pre-installed in the devcontainer and
verified above. **Nothing to audit; no `checkpoint:human-verify` install gate required.**

If a plan proposes any install, that is a scope escape — reject it and re-read this section.

---

## Project Constraints (from CLAUDE.md)

From `/workspaces/CLAUDE.md` (meta) and `firestarter_app/CLAUDE.md`:

- **Repo layout:** meta tracks only `.planning/` and `.claude/`. ⚠ *"Neither sub-repo is committed
  here"* is **imprecise** — `.gitmodules` exists and the meta repo tracks sub-repo gitlinks (D-07's
  subject). Verified: gitlinks `0048b3d` / `96e0622`.
- **Protocol changes must stay in sync** between `firestarter_app/firestarter/serial_comm.py` and
  `firestarter/src/firestarter.cpp`. **Not exercised** — this phase changes no protocol code.
- **Constants/flag bits are duplicated** between `constants.py` and `include/firestarter.h`; change
  both together. **Not exercised.** Row 7 of the nine-row gate covers it anyway.
- **`firestarter/include/messages.h` is codegen-generated and ID-only.** The canonical source is the
  meta `tools/catalog/messages.toml`; a wording-only change yields a **zero** header diff. **Do not
  hand-edit `messages.h`.** Three-way `cmp` identity re-verified green here.
- **Tooling gate** (`firestarter_app/CLAUDE.md`): `ruff check`, `ruff format --check`, `mypy`,
  `pytest --cov-fail-under=70` — validate against the **py3.9/3.11 CI targets**, not the
  devcontainer's 3.12. A literal py3.9 pytest run is **structurally impossible** (`syrupy>=5.0`
  requires ≥3.10, reproduced live in Phase 121); py3.9 is satisfied by ruff `target-version = "py39"`
  and mypy `python_version = "3.9"`, both config-pinned.
- **Board buffer sizes** (Uno 512 / Leonardo 1024). **Not exercised.**

**Project skills:** `/workspaces/.claude/skills/` is empty; no `.agents/skills/`. No project-skill
rules to apply.

**Knowledge graph:** `.planning/graphs/graph.json` exists but is **stale** — built 692 h ago at
`f4150b8`, **445 commits behind** `1d2424d`. A discovery query returned zero nodes. Treat any
semantic relationship from it as approximate; **every fact in this document was verified directly
against the live tree instead.**

---

## Validation Architecture

Test framework detection and requirement mapping. Most of this phase's output is prose, so the
central design question is **which claims a machine can sample and which cannot** — stated
explicitly below rather than left implicit.

### Test Framework

| Property | Value |
|---|---|
| Framework (host) | `pytest` 8.x + `syrupy` snapshots, via `pip install -e .[test]` |
| Config file | `/workspaces/firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.ruff]`, `[tool.mypy]`) |
| Framework (firmware) | Unity via PlatformIO (`pio test -e native`), 17 suites |
| Config file | `/workspaces/firestarter/platformio.ini` (`default_envs = uno, uno328pb, leonardo`) |
| Standalone gates | `firestarter_app/tools/*.py` — plain scripts, exit-code contract |
| Quick run command | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_sdp_db_invariant.py -q && python3 tools/diff_db.py && python3 tools/check_no_community_support_status_write.py` (~6 s) |
| Full suite command | `cd /workspaces/firestarter_app && python3 -m pytest -q` (1150 tests, ~90 s) **+** `cd /workspaces/firestarter && pio test -e native` (141 cases, ~47 s) **+** the eleven nine-row commands |

### Phase Requirements → Test Map

| Req | Behaviour | Type | Automated command | Exists? |
|---|---|---|---|---|
| CLOSE-01 | `0x0D` still `UNVERIFIED` | gate | `grep -c '^| \`0x0D\` .*\*\*UNVERIFIED\*\*' .planning/v1.16/ledger/PROTOCOL-LEDGER.md` → `1` | ✅ |
| CLOSE-01 | 84-chip count + `chip_id_check` unchanged | unit | `python3 -m pytest tests/test_sdp_db_invariant.py -q` | ✅ |
| CLOSE-01 | zero `support_status` change / DB identity | gate | `python3 tools/diff_db.py` (exit 0) | ✅ |
| CLOSE-01 | no code path writes `support_status` | gate | `python3 tools/check_no_community_support_status_write.py` | ✅ |
| CLOSE-01 | the above hold **on the merged tree** (constraint 6) | integration | re-run all four after the inbound merge, before the outbound merge | ✅ |
| CLOSE-01 | cross-repo non-regression survives the merge | integration | the eleven nine-row commands | ✅ |
| CLOSE-02 | both comments posted, issues still OPEN | gate | `gh issue view {11,12} --json state,comments -q '{state:.state,n:(.comments\|length)}'` — `state == OPEN`, `n` incremented | ✅ |
| CLOSE-02 | posted text == reviewed draft | gate | deliver with `--body-file <committed path>`; then `gh issue view … -q '.comments[-1].body'` compared to the committed file | ✅ |
| CLOSE-02 | **no forbidden phrasing** in any closing artifact | gate | forbidden-phrase scan over `122-LEDGER.md`, both release-note files, both comment drafts — see Wave 0 | ❌ **Wave 0** |
| CLOSE-02 | the wording is *honest*, not merely non-matching | **manual** | **D-16 blocking operator wording review** | n/a |
| CLOSE-03 | decision recorded before any push | gate | decision-artifact commit is an ancestor of / earlier-dated than the pushed merge commit | ✅ |
| CLOSE-03 | b14 live on PyPI | gate | PyPI JSON API contains `3.0.0b14` | ✅ |
| CLOSE-03 | b14 firmware prerelease carries 3 `.hex` | gate | `gh release view 3.0.0b14 --repo henols/firestarter --json assets` → 3 names | ✅ |
| CLOSE-03 | both bodies carry the permitted claim + silicon caveat | gate | `gh release view … -q '.body'` non-empty **and** passes the same forbidden-phrase scan | ❌ **Wave 0** |
| — | SDP works on real AT28C silicon | **UNVERIFIABLE** | **none — this is the forbidden claim** | n/a |

### What can and cannot be sampled — stated explicitly

**Mechanically checkable (14 of the rows above).** Every CLOSE-01 sub-claim, every CLOSE-03
sub-claim, and CLOSE-02's *delivery* facts (posted, still open, byte-equal to the reviewed draft).
These are cheap, deterministic, and re-runnable; sample them at every commit that could move them.

**Requires the blocking operator review (D-16).** Whether the prose is *honest* — not merely free of
banned strings. A forbidden-phrase scan cannot detect *"we've addressed this"* used to mean *"this is
fixed"*, cannot judge whether omitting the `DIP24_2816` refusal misleads `No-Hazmats`, and cannot
weigh tone. This is why D-16 is a hard gate and not advisory. **A green claim-scan must never be
presented as satisfying criterion 4.**

**Inherently unverifiable in-phase.** That silicon enters or leaves the protected state; that `tBLC`
is met as accepted by the die; that gh#11's symptom is gone; that the capability partition is correct
per family. No test, gate or review can close these. `0x0D` stays `UNVERIFIED` precisely because they
are open, and the only correct response is to say so in every outward-facing artifact. The single
asymmetry (D-10): the **defect** is now community-corroborated on real AT28C256 silicon; the **fix**
is not. Sampling rate for this class is **zero, permanently, by design.**

### Sampling Rate

- **Per task commit:** the quick run command (~6 s), plus — for any commit touching a closing
  artifact — the forbidden-phrase scan.
- **Per wave merge:** the eleven nine-row commands + full app pytest + `pio test -e native`.
- **Immediately after the inbound merge (before the outbound merge):** the full set again. This is
  the load-bearing sample — constraint 2 exists so `beta` never sees an unproven tree, and rows
  9a/9b scan the very file that was conflicted.
- **Before any comment posts:** the channel verification (constraint 3) and the operator review
  (constraint 4). Neither is a test; both are blocking.
- **Phase gate:** full suite green + both channels verified + `/gsd-verify-work`.

### Wave 0 Gaps

- [ ] **A forbidden-phrase / permitted-claim scanner** over the closing artifacts (`122-LEDGER.md`,
      both release-note files, both comment drafts) — the only mechanizable half of criterion 4.
      Suggested contract: exit 1 on any case-insensitive match of a forbidden set (e.g. `verified
      fixed`, `works on`, `confirmed working`, `silicon[- ]verified`, `now works`, `should now work`,
      `proven on`) and exit 1 if the **required** silicon caveat is absent from each artifact.
      **If built, it must follow this project's anti-hollow discipline (GATE-01):** ship a planted
      violating fixture and a test proving the scanner exits 1 on it — a scanner that has never
      failed is the hollow-GATE-03 debt repeating. *(Discretion: D-11 leaves ledger shape open, and
      CONTEXT does not require this tool. It is recommended because criterion 4 is otherwise
      100 % judgement, and because C-5 shows a real overclaim already made it into a locked decision.)*
- [ ] **No other gaps.** All four CLOSE-01 mechanisms, the nine-row gate, both full suites, and
      every `gh`/PyPI verification command exist and were executed green in this session. No test
      framework install, no `conftest.py`, no fixture scaffolding is needed.

---

## Security Domain

`security_enforcement` is absent from `.planning/config.json` → treated as **enabled**. This phase
ships no product code, so most ASVS categories are inapplicable; two are genuinely live because the
phase publishes artifacts and posts public text.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | no | No auth code. `gh`/CI credentials are consumed, never implemented |
| V3 Session Management | no | No sessions |
| V4 Access Control | **partly** | `gh` runs as `henols` with ADMIN on the tracker. `gh issue comment` needs only an authenticated account (`submit.py:252-268`'s permission-independent argv idiom); `--label`/`--add-label` require write access **and** a pre-existing label and **abort** without both — never send them |
| V5 Input Validation | no | No user input is parsed. The comment bodies are authored, not received |
| V6 Cryptography | no | No crypto. Never hand-roll; nothing here needs it |
| V7 Error Handling & Logging | **yes** | Do not paste raw local tracebacks or absolute workstation paths into public comments |
| V8 Data Protection / secrets | **yes** | Three secrets are consumed by CI: `PERSONAL_ACCESS_TOKEN`, `GITHUB_TOKEN`, `PYPI_API_TOKEN`. **Never echo, log, or paste any of them**; never add a step that prints a workflow env dump. `gh auth token` output must never enter an artifact or a comment |
| V14 Configuration | **yes** | Do not edit workflow triggers (D-05 rejected trigger surgery: a forgotten re-enable silently kills every future beta). Do not weaken `paths-ignore` |

### Known Threat Patterns for this phase

| Pattern | STRIDE | Standard mitigation |
|---|---|---|
| Secret leakage into a public issue comment or release body | Information Disclosure | Author bodies from the committed drafts only; deliver via `--body-file`; never interpolate shell output into a body |
| Local-environment disclosure (absolute paths `/workspaces/...`, devcontainer usernames, host serial ports) in public text | Information Disclosure | Reuse `submit.py`'s existing `sanitize_dict` discipline in spirit: quote product output, not workstation output. Scrub `/workspaces/` and `/dev/tty*` from anything outward-facing |
| Publishing an artifact built from an unproven tree | Tampering | Constraint 2 — the nine-row gate + full suites run on the inbound-merge result **before** the push that cuts b14 |
| Irreversible outward action taken without consent | Repudiation | D-16's blocking operator review; CLOSE-03's recorded decision before the push; no `--force`, no history rewrite, no deletion of published artifacts (b12 stays) |
| A wrong `--ours` resolution silently shipping to every `pip install --pre` user | Tampering | The superset proof (C-11) + `git diff HEAD` empty assertion (C-12) + row 9b re-run |
| Misleading a stranger into a hardware purchase or a destructive write | Information Disclosure / integrity of advice | C-5's corrected `No-Hazmats` answer; Phase 121 D-04's always-writes warning carried into the `dev test` offer |

**Note on the one destructive instruction this phase gives a stranger:** the ask invites a full-device
write. That is safe for `datapaganism` specifically — their own 2024 report says the input was *"32Kb
of random data"* — but the `dev test` half must carry Phase 121 D-04's warning verbatim in substance:
`dev test` **always writes** and expects a blank or scratch part.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| **A1** | `pdr0663`'s 2025-06-21 crash ran **firmware 1.4.2** and the failure was a Windows `ClearCommError` | Community Thread Ground Truth / D-14 | The retrievable comment body is truncated by the API at the point where the firmware version and the exception would appear; I confirmed **app 1.3.44 / Python 3.12.3 / Windows 11** and the pre-v1.20 `'type': 4` axis, but **not** the firmware version or the exception name. If the reply names either as fact, it may misattribute. **Mitigation:** the pre-3.0 framing is safe on the app version alone; either drop the firmware version and the exception name, or re-read the full comment in the browser before the wording review. |
| **A2** | The five `quick-260728-ahy` behaviours on branch HEAD are *semantically* identical to `beta`'s, not merely present under the same names | Merge Ground Truth | I verified all five behaviours by locating their implementations on HEAD and all 60 beta test **names** as a subset of HEAD's 77 — I did not diff each same-named test's assertions. A beta test could in principle assert something HEAD's same-named test does not. **Mitigation:** low risk (Phase 121 D-09/D-10/D-11 deliberately restructured these and re-verified), and the nine-row gate row 9b plus the full 1150-test suite re-run on the merged tree covers behaviour. If certainty is wanted, add one task diffing the ten hotfix tests' bodies. |
| **A3** | CI will actually produce `3.0.0b14` when the merge lands | Release Mechanics | Derived from reading `update_version.py` and confirming the tag inputs — not executed. A concurrent push, a failing gate before the version step, or a manual `beta_version` input would change the outcome. **Mitigation:** the plan verifies the *actual* cut tag after CI rather than assuming b14; every downstream step (`publish.yml -f tag=`, both `gh release edit`) must read the observed tag. |
| **A4** | `No-Hazmats`' 2K×8 part is one of the 19 `DIP24_2816` entries | C-5 | They never named a part number, only *"2K x 8"*. Verified: **every** 2048-byte `0x0D` entry is on `DIP24_2816` and all 19 are REFUSED, and no 2K×8 part anywhere in the 746-entry DB is SDP-allowed — so the conclusion holds for any 2K×8 part they own. Residual risk is only that their part is not `0x0D` at all, which would make "should now work" *even less* applicable. **Mitigation:** phrase the answer by size class, not by an assumed part number. |
| **A5** | The gitlinks and the `.planning/config.json` four-`sub_repos` change stay untouched | Runtime State Inventory | Verified as *current state*; whether some other tool bumps them mid-phase is not controlled here. **Mitigation:** D-07 assigns gitlinks to the close ritual; the plan should assert `git ls-tree HEAD firestarter firestarter_app` is unchanged at phase end. |

Everything else in this document is `[VERIFIED: …]` by live execution in this session.

---

## Open Questions

1. **Should the forbidden-phrase scanner be built?**
   - Known: criterion 4 is otherwise 100 % human judgement; C-5 proves an overclaim already reached
     a locked decision; the project has a strong anti-hollow-gate discipline (GATE-01).
   - Unclear: CONTEXT does not ask for it, and D-09's "do not rebuild existing mechanisms" cuts
     against new tooling in a close phase.
   - **Recommendation:** build it, small, in the meta repo (not a sub-repo — it validates
     `.planning/` artifacts), with one planted fixture and one test proving it exits 1. Treat it as
     an aid to the operator review, never a replacement for it.

2. **Where do the release-note files live?**
   - Known: the bodies are added post-cut via `--notes-file`, so they must exist as committed files.
   - Unclear: CONTEXT is silent.
   - **Recommendation:** in the meta phase directory (e.g. `122-RELEASE-NOTES-fw.md`,
     `122-RELEASE-NOTES-app.md`) so they are auditable against `122-LEDGER.md` in one repo, and so
     the sub-repos carry no v1.22-close artifacts that would need merging.

3. **Does `pdr0663`'s truncated comment need a browser read?** See A1. Cheap to resolve and it
   removes the only unverified factual claim heading into a public reply. **Recommendation:** yes,
   fold it into the drafting task.

4. **Is `check_ledger.py`'s RED worth fixing?**
   - Known: it is a two-line `matrix_family` rename in a **closed v1.16 milestone artifact**.
   - **Recommendation:** **no** — fixing it edits a closed milestone's artifact, which is exactly
     what D-09 refuses. Record it as a known-and-explained condition with its v1.19 cause, and
     consider a backlog seed.

---

## Sources

### Primary (HIGH confidence — executed live in this session)

- `git` in `/workspaces`, `/workspaces/firestarter`, `/workspaces/firestarter_app` — branch
  positions, ancestry, `merge-tree` dry-run merges, conflict hunk extraction, tag/blob inspection,
  gitlinks
- `gh` API — `repo view`, `issue view` (full bodies + all comments, #11 and #12), `release list`,
  `release view --json body,assets,isPrerelease`, `auth status`
- PyPI JSON API — `https://pypi.org/pypi/firestarter/json`
- Executed: `pytest` (app 1150, firmware 8, `test_sdp_db_invariant` 4), `pio test -e native`
  (141/141), `tools/diff_db.py`, `tools/check_no_community_support_status_write.py`,
  `tools/check_ledger.py` (RED), all eleven nine-row gate commands, `ruff check` / `ruff format
  --check`, `tools/check_mypy_watermark.py`, `tools/catalog/codegen.py --check`, three-way `cmp`
- Executed Python against live data — 746/84 counts, `support_status` and pinout histograms,
  `sdp_capability_for_entry` over all 84 entries (43/41 and the per-pinout split),
  `pinouts.json` `static-high-pins` comparison, `dev sdp --help`
- Read: both repos' `.github/workflows/*.yml`, `.github/scripts/update_version.py`,
  `firestarter/submit.py`, `platformio.ini`, `pyproject.toml`

### Secondary (HIGH confidence — project documents of record)

- `.planning/REQUIREMENTS.md` — CLOSE-01/02/03 (`:102-104`), §Validation Ceiling, Out of Scope,
  Future Requirements (SDP-F1..F8)
- `.planning/ROADMAP.md` — §v1.22 goal, Ordering invariants, Locked decisions, Phase 122 detail
- `.planning/PROJECT.md` — SECOND REFRAMING + THIRD–SEVENTH CORRECTION; the Phase 121 close footer
- `.planning/STATE.md` — the derived-partition banner (ALLOW 43 / REFUSE 41)
- `.planning/phases/119-…/119-NONREGRESSION.md` §5 (nine-row table), §6 (known-and-explained)
- `.planning/phases/119-…/119-MEASUREMENT.md` — the timing figures and the budget-conflation note
- `.planning/phases/119-…/119-09-PLAN.md` — the 3348 B → 2992 B → 2600 B flash correction
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` — `:4` firmware pin, `:27` the `0x0D` row
- `.planning/phases/122-…/122-CONTEXT.md`, `122-DISCUSSION-LOG.md`
- `/workspaces/CLAUDE.md`, `firestarter_app/CLAUDE.md`

### Tertiary (LOW confidence — flagged, not relied on)

- `.planning/graphs/graph.json` — **stale**: 692 h old, 445 commits behind, zero query results.
  Contributed nothing; every fact was verified directly instead.

**No external web or Context7 lookup was performed or needed** — every claim in this document is
repo-local or verifiable through the GitHub / PyPI APIs. No package recommendations are made, so
no package-legitimacy risk exists.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| Merge conflict set + resolution | **HIGH** | Non-mutating `merge-tree` executed in both repos; conflict hunks read line-by-line; superset proof mechanical (`comm -23` empty) |
| Release mechanics | **HIGH** | Both workflow YAMLs and `update_version.py` read in full; PAT suppression documented in-file; PyPI/GH state read via API; b14 absence confirmed |
| CLOSE-01 mechanisms | **HIGH** | All four executed; a second independent Python path reproduced the same numbers |
| SDP allow/refuse split + the `No-Hazmats` correction | **HIGH** | Computed by the production predicate over all 84 entries; reproduces STATE.md's 43/41 exactly; corroborated by shipped `--help` text and SDP-F7/F8 |
| Community thread content | **HIGH** for #11 and for #12's structure; **MEDIUM** for one `pdr0663` detail | Full bodies and all comments retrieved; one comment body truncated by the API (A1) |
| Measured figures for the ledger | **HIGH** | Quoted from `119-MEASUREMENT.md` / `119-09-PLAN.md` with line references; the flash arithmetic re-derived from Phase 121's recorded build sizes |
| Baseline suite state | **HIGH** | Every suite and gate re-run in this session |
| Wording of the drafts | **n/a** | Claude's discretion under D-16's blocking review |

**Research date:** 2026-07-30
**Valid until:** **~2026-08-02 (3 days).** Unusually short and deliberately so: `origin/beta` moves
the moment anyone pushes, the b13/b14 boundary is the phase's entire premise, and the branch is
7 commits behind. **Re-run the dry-run merge probe and re-read both `beta` version files immediately
before the merge** (CONTEXT's own setup precondition, and a trap that has bitten twice).
