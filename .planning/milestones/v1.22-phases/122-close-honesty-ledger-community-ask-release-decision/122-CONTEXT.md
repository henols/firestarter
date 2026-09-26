# Phase 122: CLOSE — honesty ledger, community ask, release decision - Context

**Gathered:** 2026-07-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Close v1.22 with an honest, verifiable record of exactly what was and wasn't proven, give both
community reporters an accurate (non-overclaiming) update, and make the beta-push decision
deliberately instead of by accident.

**In scope (CLOSE-01, CLOSE-02, CLOSE-03):**
- The honesty ledger — a new `122-LEDGER.md` recording, per claim class, the permitted wording and
  the explicit non-claim (D-09, D-11, D-12).
- Verification (not mutation) that `0x0D` is still `UNVERIFIED` in `PROTOCOL-LEDGER`, that **zero**
  chips changed `support_status`, and that the **84**-chip `algorithm == 13` count is unchanged
  (CLOSE-01).
- **The v1.22 beta cut itself — `3.0.0b14`, published on both channels** (D-01, D-03, D-04, D-05).
  This is the single largest scope fact this discussion settled: the ROADMAP's Phase 122 criteria
  never mention a publish, but CLOSE-02's *"please re-test"* is hollow without one.
- The recorded accept/avoid/cleanup decision, written **before** any push (CLOSE-03, D-05).
- A hand-written b14 prerelease body carrying the permitted claim and the silicon caveat (D-08).
- The gh#12 reply (answering its reporter's own 2024 design question) and the gh#11 follow-up, both
  drafted as committed artifacts behind a **blocking operator wording review**, then posted via `gh`
  (D-13, D-14, D-15, D-16).
- An **EIGHTH CORRECTION** block in `PROJECT.md` recording that the milestone's headline premise is
  now silicon-confirmed by a community report while the fix remains unproven (D-10).

**Explicitly NOT in scope:**
- The `v1.22` tag and the meta-repo gitlink bump — both stay with `/gsd-complete-milestone` (D-07).
- Any `support_status` change, any `chip_database.json` change, any `PROTOCOL-LEDGER` **edit**, any
  ladder-state promotion. CLOSE-01 is a check, not a write.
- Any stable release. Stable is operator-gated and nothing in this phase approaches it.
- Deleting the stray `b12` prereleases (declined at D-05 — they stay public).
- A bench smoke-test of the b14 install/flash path (declined at D-01 — see the owned trade-off in
  `<specifics>`).
- Splitting gh#12's drifted reports into new issues (declined at D-14).

**Validation ceiling applies, unchanged and load-bearing here more than anywhere.** No AT28C part is
on the operator's bench. See `.planning/REQUIREMENTS.md` §"Validation Ceiling" for the exact
permitted claim and the exact forbidden claim. This phase's whole job is to not cross that line in
public.

</domain>

<decisions>
## Implementation Decisions

### The beta publish and the community ask are coupled — CLOSE-02 / CLOSE-03

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

### The push mechanics — CLOSE-03

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

### The honesty ledger — CLOSE-01

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

### The community replies — CLOSE-02

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

Not preferences. A plan that reorders any of these breaks a requirement or publishes an unproven
artifact:

1. **The accept/avoid/cleanup decision is recorded before any push to `beta`.** Literal CLOSE-03
   text; v1.21's close skipped it and auto-cut a stray b12.
2. **`beta` → branch merge and a green nine-row gate precede the branch → `beta` merge** (D-06).
3. **b14 exists and both channels are verified public before any comment is posted** (D-03).
4. **The blocking operator wording review precedes any comment reaching GitHub** (D-16).
5. **`122-LEDGER.md` and the EIGHTH CORRECTION exist before the prerelease body and the two comment
   drafts are written** — the ledger is the single source of the permitted wording those three
   artifacts must all match (D-08, D-11, D-15).
6. **CLOSE-01's verification runs against the tree that actually gets merged**, so its result is a
   statement about what was published, not about an earlier commit.
7. **The PyPI publish is a manual `workflow_dispatch`** with a required `tag` input; it does not
   happen as a side effect of the merge (D-03, D-05).

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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone framing and the ceiling (read first)
- `.planning/REQUIREMENTS.md` — **CLOSE-01/02/03 verbatim** (`:102-104`); §**"Validation Ceiling"**
  (`:144-152`) for the exact permitted and forbidden claims; the **Locked decisions** table
  (`:20-33`); the **Out of Scope** table (`:127-140`); §**"Future Requirements"** (`:108-123`) for
  SDP-F1..F8's deferral reasons, which D-12 needs; and the 41/41 traceability table (`:160-208`).
- `.planning/ROADMAP.md` §v1.22 → "Phase Details" → **Phase 122** (`:481-499`) — the four success
  criteria this phase is verified against. Also the **Ordering invariants** block (`:131-137`) and the
  **Locked decisions** paragraph (`:139`), whose *"no requirement depends on a community reply"* is
  what keeps D-01's publish honest rather than a dependency.
- `.planning/PROJECT.md` §"Current Milestone: v1.22" — **all seven** ⚠ correction blocks; D-10 appends
  the **eighth**. Load-bearing here: the **THIRD**'s 66-of-84 measured figure (do not write "all 84"),
  the **FOURTH** item 2 (gh#11's cause is a **conflation** bug, not a sampling-rate bug — D-15 states
  it that way) and item 4 (every phase from 118 on checks firmware renames against the host
  source-scanning gates), the **FIFTH** item 3 (the 572/600 µs measurement), the **SIXTH** items 1-3
  (mechanism-corrected-not-failed, and LOCK-06's superseded figure), and the **SEVENTH** items 4
  (`--submit`'s wrong-repo defect is a released-artifact fact) and 8 (a two-repo requirement can pass
  its own phase and still be false end to end).
- `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-NONREGRESSION.md`
  §CORRECTION-4 — the **nine-row** cross-repo gate table, explicitly handed to Phases 120-122.
  **Mandatory here**, and it must be re-run *after* D-06's inbound merge, because that merge brings
  `beta`'s `submit.py` history into the tree.

### Prior-phase decisions that bind this phase
- `.planning/phases/121-dev-test-fix-gates-docs-redesign/121-CONTEXT.md` — **D-04** (`dev test`
  always writes; *"Phase 122's community ask must carry the same warning"* — an explicit obligation on
  this phase), **D-08** (a partial run can never cross-agree with a full one toward N≥2, so GRAD-01
  holds **through the fingerprint, not the tag** — Phase 122 should state it that way), **D-03** and
  **D-16** (the two owned trade-offs D-12 records), **D-06** (`OP_WRITE_PARTIAL`, and the correction
  that `parse_devtest_issue.py` has no op vocabulary at all).
- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-CONTEXT.md` — **D-11**
  (honesty lives in the message text, never in a status code) and **D-16** (why no version floor
  exists, and why the numbering decision was routed to CLOSE-03 — D-04 closes it).
- `.planning/phases/116-ground-truth-trace-harness/116-PREMISE.md` — TRACE-06's written premise
  artifact and its ceiling-compliant wording. D-10's correction sits directly on top of this.
- `.planning/phases/115-beta-channel-install-and-firmware-flash-bench-validation-for/115-CONTEXT.md`
  and `115-VALIDATION.md` — the in-phase-publish precedent D-01 follows, and the Step 0
  both-channels-public check D-03 reuses.

### The honesty ledger's subject matter
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` **line 27** — the `0x0D` row, status **UNVERIFIED**,
  *"No on-hand silicon. Rep chip: AT28C256"*. **Verify, never edit** (D-09). Its header pins firmware
  `a296195`, which is an ancestor of neither `beta` nor the live line.
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.json` + `.planning/v1.16/ledger/tools/check_ledger.py` —
  the machine-checked half. Untouched under D-09.

### CLOSE-01's verification mechanisms — they already exist, do not rebuild them
- `firestarter_app/tests/test_sdp_db_invariant.py` — TRACE-05's test, pinning `chip_id_check: false`
  across all **84** `algorithm == 13` entries **and the count itself**, with no skipif. This is the
  84-count proof.
- `firestarter_app/tools/diff_db.py` (+ `firestarter_app/tools/baseline/chip_database.baseline.json`)
  — ⚠ **"identity" here means "still exactly 2 explained `PGSZ_PAGE_SIZE` changes, 0 new, 0 removed",
  not zero diff** (GATE-03, `REQUIREMENTS.md:98`). Do not report a two-change result as a failure.
- `firestarter_app/tools/check_no_community_support_status_write.py` — the no-code-path-writes-
  `support_status` gate.

### Release mechanics — verified live, do not re-derive
- `firestarter/.github/workflows/beta-build.yml` — `on: push: branches: [beta]` with `paths-ignore`,
  plus `workflow_dispatch` with an optional `beta_version`; blank input means auto-increment via
  git-tag scan.
- `firestarter_app/.github/workflows/beta-release.yml` — same trigger shape and same auto-increment.
- `firestarter_app/.github/workflows/publish.yml` — `on: release: published` **plus**
  `workflow_dispatch` with a **required** `tag` input. Its own in-file comment records why: a release
  created by another workflow using a PAT without `workflow` scope suppresses the `release.published`
  event. **This is the b12 failure mode and D-03's reason.**

### Community threads
- `https://github.com/henols/firestarter_prom/issues/11` — open, author `datapaganism`, 12 comments.
  The live exchange is comments 9-12 (2026-07-27 → 2026-07-29): your status update, their b11
  reproduction, your *"there will be a fix soon and I will let you know"*, and their **"That's fine,
  happy to test for you."**
- `https://github.com/henols/firestarter_prom/issues/12` — open, author `humbertocsjr`, 8 comments.
  Your unanswered 2024-09-16 design question is comment 1; the drift D-14 addresses is `pdr0663`
  (2025-06-21), `No-Hazmats` (2026-04-02) and `AndersBNielsen`.

### Project conventions
- `CLAUDE.md` (meta) — repo layout and the constants/flag-bit duplication rule. ⚠ Its *"Neither
  sub-repo is committed here"* is **imprecise**: `.gitmodules` exists and the meta repo **does** track
  sub-repo gitlinks (D-07's subject).
- `firestarter_app/CLAUDE.md` — the tooling gate (`ruff check`, `ruff format --check`, `mypy`,
  `pytest --cov-fail-under=70`), to be validated against the **py3.9/3.11 CI targets**, not the
  devcontainer's 3.12.

</canonical_refs>

<code_context>
## Existing Code Insights

### Verified live during this discussion — do NOT re-derive
- **`origin/beta` is at `3.0.0b13` in BOTH sub-repos**, not b11 and not b12. The spurious auto-cut
  happened **twice**: `a981642` (firmware, 2026-07-27, b12 — the v1.21 close) and `6611fba`
  (firmware, 2026-07-28, b13), both pure `include/version.h` bumps titled *"Apply automatic
  changes"*. The prior memory note recording only b12 is stale.
- **Public release state.** GitHub prereleases exist for b11, b12 and b13 in **both** repos. PyPI
  carries `3.0.0b11` and `3.0.0b13` but **not b12**; latest stable on PyPI is `2.0.7`. So
  `pip install --pre firestarter` today resolves to b13, and `firestarter fw -i` pulls firmware b13 —
  a consistent pair containing **zero** v1.22 work.
- **Branch positions.** `firestarter` is on `v1.22-at28c-software-data-protection-lifecycle` at
  `48c36e5`, **42 ahead / 2 behind** `origin/beta`; the 2 behind are exactly the two version bumps.
  `firestarter_app` is at `c3c9424`, **75 ahead / 7 behind**; the 7 behind are the 5
  `quick-260728-ahy` commits plus 2 version bumps.
- **The five hotfix commits are double-applied with different SHAs.** On the branch:
  `688bf10`, `d4f8130`, `0245828`, `e615b4c`, `36a9bb5`. On `beta`: `591c819`, `379bb30`, `98c7de6`,
  `2b9e8dd`, `0050277`. The `beta`-only diff touches `firestarter/__init__.py`,
  `firestarter/submit.py` (**+97**) and `tests/test_submit.py` (**+244**) — the same functions Phase
  121's D-09/D-10/D-11 restructured. **This is D-06's whole reason.**
- **`SUBMIT_REPO = "henols/firestarter_prom"` is already correct on the branch** (`submit.py:73`),
  and the branch already carries the hotfix behaviours (stderr surfacing at `:272`, created-URL echo
  at `:245`). The wrong-repo defect is a released-artifact fact only — shipped b11 misfiles, and b14
  is what fixes it for users.
- **The meta repo tracks sub-repo gitlinks.** `.gitmodules` exists; committed gitlinks are `0048b3d`
  (firestarter) and `96e0622` (firestarter_app) against working tips `48c36e5` / `c3c9424` — stale by
  one phase. D-07 leaves them to the close ritual.
- **`gh` is authenticated as `henols`** with write access to the tracker, so `gh issue comment` on
  both threads is available in-session.
- **Working-tree dirt to expect.** `firestarter_app` carries a modified `.gitignore` plus untracked
  `.coverage`, `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`; `firestarter` carries an
  untracked nested `firestarter/` directory. Named so a plan's clean-tree assertion does not read
  pre-existing dirt as its own damage.
- **⚠ The meta `.planning/config.json` now lists FOUR sub-repos** — `firestarter`, `firestarter_app`,
  `firestarter_app_py32`, `firestarter_py32_ci` (uncommitted change). Any close step that iterates
  `planning.sub_repos` would reach into two v1.29 PY32 scratch repos that are **not** part of this
  milestone. Iterate the two named sub-repos explicitly.

### Reusable Assets
- **`test_sdp_db_invariant.py`** — the 84-count and `chip_id_check` proof already exists as a test;
  CLOSE-01 runs it, it does not write a new one.
- **`diff_db.py` + its pinned baseline** — the DB-identity proof, with GATE-03's "still exactly 2"
  reading.
- **`119-NONREGRESSION.md` §CORRECTION-4's nine-row table** — the cross-repo gate checklist, already
  authored and already handed to this phase.
- **`115-VALIDATION.md`** — the shape of a committed channel-verification artifact for D-03.
- **Plan 116-07's blocking-operator-wording-review pattern** — D-16's precedent for gating
  outward-facing text.
- **`gh issue comment`'s permission-independent argv** (`submit.py:252-268`'s idiom) — needs only an
  authenticated account, never write access.

### Established Patterns
- **Honesty in the message text, not in a status code** (117 D-05, 118 D-02, 119 D-12, 120 D-11).
- **A requirement whose stated mechanism is narrower than its intent:** satisfy the intent, record the
  correction in phase artifacts, **do not edit `REQUIREMENTS.md`** (LOCK-04, LOCK-06, HOST-04, 121
  D-06/D-17). D-09's verify-don't-edit reading of CLOSE-01 is the same move.
- **A reversal is recorded *as* a reversal, with its constraints named** (119 D-18, 120 D-20).
- **Every claim is judged against the live measured figure, never a predicted one** (LOCK-06's 3348 B
  → 2992 B; the "all 84" → 66 of 84 correction). The ledger must cite measured values only.
- **Firmware renames break host source-scanning gates** — 4× in Phase 117. This phase changes no
  source, but D-06's inbound merge changes the tree, so the gates re-run after it.
- **Executors prematurely mark multi-plan requirements Complete** — 4× in Phase 116. Name the allowed
  `CLOSE-NN` ids in every dispatch prompt and re-check `REQUIREMENTS.md` after each plan.
- **STATE.md tooling under-writes and re-clobbers fields.** Call `state.record-session` first, then the
  progress/metric/decision calls, then hand-verify `current_phase_name`, `status`, `stopped_at` and
  `progress.percent`.
- **`- **D-NN: text**` must close its bold run on ONE line**, carry at most one colon before the
  closing `**`, and never open with a glyph — otherwise plan-phase's §13a decision-coverage gate fails
  closed.

### Integration Points
- `.planning/phases/122-.../122-LEDGER.md` (**new**) — the claim-class honesty ledger.
- `.planning/PROJECT.md` — the EIGHTH CORRECTION block, appended after the SEVENTH.
- `.planning/REQUIREMENTS.md` — CLOSE-01/02/03 checkboxes and the traceability table's three
  `Pending` rows, ticked only when each is genuinely closed.
- Both sub-repos' `beta` branches — the inbound merge, then the outbound merge that cuts b14.
- `firestarter_app`'s `publish.yml` — one manual `workflow_dispatch` with `tag=3.0.0b14`.
- Both repos' b14 GitHub prerelease bodies — hand-written under D-08.
- `henols/firestarter_prom` issues **11** and **12** — one `gh issue comment` each, after the review
  gate.

### Setup precondition — verify at plan time, do not assume
Both sub-repos must be on `v1.22-at28c-software-data-protection-lifecycle` before any write —
**confirmed at `48c36e5` / `c3c9424` at discussion time**. The branch-base check has been a real trap
twice (`.planning` memory `project_v121_submodule_branch_base.md`), and this phase additionally moves
`beta`, so re-confirm both branch positions and the b13 starting point immediately before the merge.

</code_context>

<specifics>
## Specific Ideas

- **The single fact that reshaped this phase: the community ask had no target.** `beta` is at b13 and
  b13 predates the entire milestone, so *"please re-test"* against anything published would have been
  meaningless — and worse, a b13 `dev test at28c256` would have auto-tagged `community-fail` on a
  perfectly good run, because Phase 121's phantom-erase fix is not in b13. The ROADMAP's Phase 122
  never asked for a publish. D-01 pulls it in, which makes this the largest scope addition of the
  discussion and the reason CLOSE-02 and CLOSE-03 are now one interlocked sequence rather than two
  independent criteria.

- **The milestone's headline premise turned out to be silicon-confirmed by a stranger, four days
  ago.** `datapaganism` re-tested on b11 and pasted `ERROR: EEPROM timeout at 0x005555: wrote 0x20 got
  0xff` — the exact inverted-check INIT abort Phase 116 could only predict in software. The ceiling
  called that claim class unprovable, and it is still right about the **fix**; what changed is that the
  **defect** now has silicon evidence. Getting that asymmetry stated precisely is the sharpest honesty
  test in the whole close: premise confirmed, fix unproven, `0x0D` still `UNVERIFIED`, zero
  `support_status` movement.

- **Their re-test looked like a regression and the reply has to explain why it wasn't.** In 2024 the
  write *completed* and silently burned only part of the image in 339 s. On b11 it hard-fails at INIT.
  That is the fix landing halfway — the inverted check turned a silent partial write into an honest
  refusal — and if the comment does not say so, the reporter will reasonably read b11 as worse than
  what they had.

- **The b12 loss is the operational lesson D-03 encodes.** CI reported success, the GitHub release
  existed, and PyPI never moved, because a PAT-created release suppresses `release: published`. The
  workflow file's own comment documents it. *"CI is green"* is not evidence a channel is live, which is
  why the comments are gated on a resolution check rather than on a workflow status.

- **One owned trade-off, chosen with the cost named.** D-01 declined the bench smoke-test of the b14
  install and flash path, so `pip install --pre` → `fw -i` → one live op is **not** re-proven before two
  strangers are pointed at b14. Phase 115 existed to prove exactly that path, and it is being trusted
  rather than re-verified. Recorded here so no downstream agent quietly re-opens it — and so that if a
  b14 install problem surfaces, the record shows it was a known, accepted gap rather than an oversight.

- **The double-applied hotfix is the kind of thing a green test suite hides.** Five commits with the
  same messages and different SHAs sit on both sides of the merge, layered on Phase 121's rewrite of the
  same `submit_report` step order. Git will present that as a conflict, and any resolution that
  compiles and passes will *look* right. D-06 puts the resolution where the nine-row gate actually runs
  precisely because "it merged cleanly and the tests pass" is the weakest available proof here.

</specifics>

<deferred>
## Deferred Ideas

### Raised during this discussion, declined with a reason
- **Deleting the stray b12 prereleases.** Declined at D-05 — b12 has been public for three days and
  may already be installed somewhere; firmware b12 is byte-identical to b11 and app b12 was the v1.21
  close artifact. If it is ever cleaned up it is an operator-driven outward-facing act, not close work.
- **A bench smoke-test of the b14 install and flash path.** Declined at D-01. If wanted it is a
  hardware-gated task in its own right, shaped like Phase 115's ONBOARD criteria.
- **A minor version bump to `3.1.0b1`, and a recorded `3.1.0` stable-candidate marker.** Both declined
  at D-04. Whenever a stable cut is authorised, the accumulated wire commands (`CMD_SDP_UNLOCK`,
  `CMD_SDP_LOCK`) and the `dev test` flag removal are what it would carry.
- **Splitting `pdr0663`'s Windows `ClearCommError` crash into its own issue.** Declined at D-14 —
  addressed inline instead, with an invitation to file fresh if it reproduces on b14.
- **An `awaiting-silicon-verification` label on gh#12.** Declined at D-13 — the label would have to
  pre-exist, and `gh issue edit --add-label` fails the same way `create` does on a missing one.
- **Editing `PROTOCOL-LEDGER` with a v1.22 addendum or cross-reference row.** Declined at D-09; the
  `0x0D` row is verified, not touched.

### Carried forward, still not taken
- **`dev test`'s release-channel disposition** (999.15 / gh#8) — the stable channel is meant to keep
  only `dev read` and `dev test`, and Phase 121 D-04 made `dev test` a command that always writes.
  Whether an always-writing command belongs in stable is still unanswered, and becomes live the moment
  a stable cut is authorised.
- **A read-only `dev test` mode.** Declined at Phase 121 D-04; wants its own phase and its own
  flag-surface decision if community feedback asks for it.
- **The wider CLI flag re-design** — `-f/--force`'s two unrelated meanings, `-b`'s opposite polarity
  between `write` and `erase`, a project-wide `-y` idiom.
- **The end-to-end `infoic.xml` `page_size` decode phase** — still operator-approved, still **not
  inserted into ROADMAP.md**. Insert with `/gsd-phase`; heed `.planning` memory
  `reference_new_milestone_phases_clear_destructive.md`.
- **Widening `_probe_port`'s `[\d.x]+` version capture** so the host can order `b13 < b14`. Declined
  at Phase 120 D-15/D-16 and untouched by D-04.
- **SDP-F1 to SDP-F8** — `--sdp-relock`, the three-field SDP report shape, a `dev test` SDP step,
  write-probe SDP inference, the software chip-erase, the AT29C/SST39SF/W29EE families, datasheet
  verification of the magic addresses, and `DIP24_2816`'s missing `static-high-pins`. D-12 records
  their deferral reasons in the ledger; none is acted on.
- **Hardening `derive_plan`'s now-vestigial `locked_destructive`** — named in Phase 121's specifics.
- **Unity-teardown SIGABRT root cause** (`test_flash_intel_vpp`); recording every side-effecting
  `rurp_*` call; all-84-chips table-driven trace coverage.

### Reviewed Todos (not folded)
`todo.match-phase 122` returned **12** matches, all scoring 0.6 or below and all generic keyword
overlap only — `avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01`,
`delete-jp5-dead-renderer`, `fix-jp4-labels-and-rev2-revision-block`, `photograph-modified-rev-0`,
`prove-pio-dev-flag-fails-closed`, `remove-dead-json-init-sizeof-pointer-bug`,
`write-modifications-md-rework-trace`, `correct-v128-py32-roadmap-prior-art`,
`fold-response-code-into-log-macro`, `spike-databuffer-size-speed-delta`, and the
VPP-on-reads-skip note. Same disposition as Phases 116-121: none is close work, and
`fold-response-code-into-log-macro` in particular has now been declined at 118, 119, 120, 121 and
here, for the same reason — it conflicts with 117 D-05 / 118 D-02 / 119 D-12.

</deferred>

---

*Phase: 122-CLOSE — honesty ledger, community ask, release decision*
*Context gathered: 2026-07-30*
