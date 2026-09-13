# Phase 187: Answered Reports - Context

**Gathered:** 2026-09-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Every reporter this project owes an answer gets one, describing what actually shipped, and nothing is
closed on our own reading. Six issues in the **public** `henols/firestarter_prom` tracker: gh#23, gh#28,
gh#31 (disputed `dev test` triage), gh#60 (JP5 hazard), gh#62 (AE29F2008 erase), gh#9 (contribution guide).

**This phase writes no product source.** Its deliverables are outward-facing: three PRs to `beta`, two
release cuts, six issue dispositions, a `.planning/notes/` record, and the in-repo record repairs those
findings force.

**Not in scope:** answering any other issue (gh#65, gh#66, gh#21 are deferred, below); fixing any of the
three still-unfixed chip defects the 2026-08-08 triage found; building a `0x05` software chip-erase
(backlog 999.63); closing gh#23/#28/#31 (REQUIREMENTS.md § Out of Scope, REPLY-06).

</domain>

<decisions>
## Implementation Decisions

### The release seam — 187 ships before it speaks

- **D-01:** **Phase 187 owns the merge and the cut, then posts.** Measured at discussion time:
  `git cat-file -e origin/beta:firestarter/jp5_gate.py` → *"exists on disk, but not in `origin/beta`"*;
  the app branch is **33 commits ahead** of `origin/beta`; firmware is **9 ahead**; **no v1.37 PR is open
  in any of the three repos**. REPLY-03 and REPLY-04 therefore describe code nobody can install today.
  This is Phase 152's D-04 situation exactly — which that phase called *"the load-bearing measurement of
  this whole phase"* — and it takes the same route rather than posting a reply that describes an
  intention.
  — **Reversibility:** one-way — a merge to `beta` triggers `beta-release.yml`, which publishes a
  pre-release to PyPI and GitHub Releases. A published version cannot be unpublished.

- **D-02:** **All three repositories merge: app, firmware, meta.** App is what a reporter installs
  (`jp5_gate.py`, `flash4_erase_gate.py`, the 3.11 floor). Firmware is **not** docs-only — measured,
  `src/proms/flash_5v_page.cpp` loses **52 lines** (SAFE-08's unreachable 12 V bulk-erase arm) alongside
  the re-recorded `size_baseline.json`; behaviour-neutral, because the host clears `FLAG_CAN_ERASE` for
  every `0x05` part, but it is a code edit. Meta carries `.planning/`, and D-13 below makes that merge
  load-bearing for the replies.
  — **Reversibility:** one-way — same publication reason as D-01. Two cuts fire (app + fw); meta has no
  release CI and cuts nothing.

- **D-03:** **187 ships; `/gsd-complete-milestone` afterwards is archive-only.** The three PRs and two cuts
  ARE the v1.37 ship. Close is hand-archival of `.planning/` per the standing rule that milestone close is
  never run through `milestone.complete`. **Accepted and stated:** 187's own tail (posting record,
  SUMMARY, verification) and the archive land on the milestone branch, not on `beta` — the same pattern
  v1.35's close produced. Do not "fix" this by scheduling a second meta PR unless the operator asks.

- **D-04:** **No `v1.37` tag in this phase.** Same call as v1.36 (merged to `beta` in all three repos,
  deliberately not tagged). Whether v1.37 is ever tagged stays a separate operator decision.

- **D-05:** **Versions are READ after the cut, never predicted.** Read the resulting app and firmware
  pre-release versions from `gh release list` after `beta-release.yml` has run, and name those in the
  replies. Reporters are told `pip install --pre -U firestarter`. Use `git cherry`, not SHA ancestry, to
  establish what `beta` already carries — v1.30's squashed merge already produced one `--is-ancestor`
  false negative. Re-read `origin/beta` before acting on it; local `beta` goes stale.

### gh#9 — REPLY-07 was already discharged, and the record says otherwise

- **D-06:** **REPLY-07 is discharged by an existing comment; 187 posts nothing new on gh#9.** Measured:
  Phase 173 posted an operator-approved body verbatim as
  [`#issuecomment-5511487546`](https://github.com/henols/firestarter_prom/issues/9#issuecomment-5511487546)
  on **2026-09-02**, byte-identical to
  `.planning/milestones/v1.35-phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/evidence/bodies/173-gh9.md`,
  then deliberately left gh#9 open and **pinned** it via the GraphQL `pinIssue` mutation
  (`173-07-SUMMARY.md:115-118`). The pin is live — `pinnedIssues` on prom returns `#9` today. gh#9 stays
  open and pinned: that is the configured, deliberate end state, not an omission.

- **D-07:** **The repair set is exactly five live sites, and the sweep stops there.** REPLY-07 was filed
  2026-09-10 against `ROADMAP.md:5424`'s *"gh#9 still owes a closing reply"* — false since 14:50 on
  2026-09-02. Repair:
  1. `.planning/ROADMAP.md:5409-5411` — *"what it needs is a closing reply or a close-as-done"*
  2. `.planning/ROADMAP.md:5424` — *"gh#9 still owes a closing reply"*
  3. `.planning/ROADMAP.md:502` — Phase 187 success criterion 4, **amended** with the reason recorded
  4. `.planning/REQUIREMENTS.md:118` — REPLY-07 **amended**, marked Complete with the comment URL
  5. `.planning/REQUIREMENTS.md:217` — the REPLY-07 traceability row, Pending → Complete

  **Explicitly NOT repaired,** and a planner must not widen into them:
  - `ROADMAP.md:967` and `ROADMAP.md:1224` — both say gh#9 *"stays open as the pinned orientation issue"*,
    which is now literally true and configured.
  - Every hit under `.planning/milestones/` (10 files) — historical-by-intent, never repaired.

  This carries Phase 184's D-01 discipline forward by name: **the sweep is complete here.** Do not turn it
  into a general stale-upstream-claim hunt.

- **D-08:** **The finding is recorded; nothing is filed.** A requirement was promoted off a record that had
  been false for eight days and nothing caught it. Same branch the operator took at 184 D-05/D-06 and
  185 D-01/D-04: **name it, file nothing.** A planner or executor must **NOT** helpfully file a
  "verify upstream claims against the live API before promoting a backlog stub" guard item, and must not
  treat CLAIM-09's shape as licensing one. Zero backlog items on this axis.

- **D-09:** **One `.planning/notes/` document carries both the gh#9 finding and the phase's reply ledger.**
  Following 182 (`jumper-display-ground-truth.md`), 183 (`ae29f2008-classification-verdict.md`), 184 and
  185. It must carry: the gh#9 staleness finding with the comment URL and the eight-day window; and, per
  issue, which body was posted, its permalink, the app and firmware versions named, what was relabelled,
  what was closed and what was deliberately left open. The approved bodies themselves live in the phase
  directory (Phase 152's `152-GH{N}-COMMENT.md` / Phase 173's `173-UPSTREAM-REPLIES.md` pattern); the
  `notes/` document is the durable record a future reader checks before claiming a reply is owed — which
  is precisely what failed here.

### What the replies concede, and what they refuse to bury

- **D-10:** **Concede attribution fully; keep the datasheet findings standing.** Measured against the
  shipped `chip_database.json` at discussion time — **v1.36 fixed none of the three technical findings**:

  | Chip | 2026-08-08 claim | Measured today |
  |---|---|---|
  | `WINBOND W27E257` | `vpp` 13.5 V should be 12 V | `vpp_mv=13500` — **unfixed** |
  | `ST M27C512` | `vdd` 6.5 V vs `vcc` 5 V, nothing applies it | `vdd_mv=6500`, `vcc_mv=5000` — **unfixed** |
  | `ST M27C1001` | pin 30 maps A17, datasheet says NC | `DIP32_27C020` — **unfixed** |

  What v1.36 changed is how a failure is **attributed and reported** — which is what all three reporters
  were actually objecting to. So each reply concedes the reporter's point in full and restates the
  datasheet findings as **unfixed, independent, still-open defects with their measured current values**.
  They are not retracted and not quietly dropped; no other record tracks them.

  Also measured, and it splits the three: `W27E257` is `type=EEPROM`, so **Phase 179's UV slot work does
  not apply to gh#23**. `M27C512` and `M27C1001` are both `type=UV-EPROM`, so it does.

- **D-11:** **REPLY-01 is amended in-phase, because its literal wording would be an overclaim.** Measured:
  `chip_test.py:2599` fires the status axis only on `(SerialError, HardwareOperationError)`; gh#23's
  fault — VPP not hooked up — raises neither, it produces BAD data. `diagnostic_report.py:55-68` says so
  in its own words: *"a rig with VPP unhooked still reads a healthy rail."* **A fresh run today would
  still report `write BAD, verify BAD` and still file as `[dev test] w27e257 — FAIL`.**

  gh#23's reply therefore states the limit plainly: v1.36 did **not** make the tool able to see an
  unhooked VPP — it cannot — and names what did change: Phase 181 deleted the misleading
  `voltage.vpp_mv`/`vpe_mv` from the report, and Phase 178 added `rail_reading_disclosure`, a sentence
  naming the exact trap the reporter hit. REPLY-01's wording is amended in `REQUIREMENTS.md` with the
  reason on the record, following 183 D-08 / 184 D-03 / 185 D-02.

  **Care on the concession's scope:** the reporter wrote *"the second one actually passed"*, but no
  `w27e257` PASS issue exists anywhere in the tracker (gh#24, the folded sibling, is a blank-check FAIL).
  Concede the general point — a rig fault was reported as a chip verdict — and do **not** invent or imply
  a PASS run the tracker does not carry.

- **D-12:** **Both known caveats are carried into the re-run asks.**
  - **gh#28 / gh#31:** `dev test` now passes a non-blank UV part via `FLAG_SKIP_BLANK_CHECK`, by a path
    `firestarter write` does not take — the identical firmware still refuses the user-facing write on the
    identical part, and no exported key discloses the divergence. A PASS on a re-run therefore does not
    mean `write` works on their chip, and the reply says so.
  - **gh#62:** cross-link [gh#68](https://github.com/henols/firestarter_prom/issues/68) (open, filed
    2026-09-11) — protocol `0x05` partial/unaligned writes silently erase the rest of the touched page and
    report success. It names AE29F2008 explicitly.

- **D-13:** **Short and plain; evidence linked, not inlined.** The 2026-08-08 comments ran ~60 lines each
  with full datasheet tables, and all three reporters answered in one or two sentences, two of them
  rejecting the analysis outright. Each reply leads with the concession or the answer in its first two
  sentences, states what changed and what to run, and **links** the `.planning/notes/` record for anyone
  who wants firmware line numbers.

  D-09's instruction in `ae29f2008-classification-verdict.md` — *"REPLY-03 should carry this paragraph
  verbatim"* — is honoured **in substance, not in register**: the reply must carry every load-bearing
  claim of that paragraph (the erase was real; it used the documented six-cycle `FLASH_ERASE` sequence;
  it was benign only because that chip pair happens to share `DIP32_SST39SF040` and a voltage class; and
  `--force` identity forgery is **not** a safe workaround in general), rewritten for a user rather than a
  maintainer reading `flash_utils.h` line numbers.

  **Linking mechanics, locked:** `henols/firestarter_prom` is **PUBLIC** and `.planning/notes/` is tracked
  and already present on `beta` (verified: 26 entries). Links must be **commit-SHA permalinks**, never
  `blob/beta/…` branch links (they rot) and never `main` (it lags `beta`). **Sequencing consequence:** the
  meta merge (D-02) must land *before* any reply is posted, or the links 404.

### Dispositions, labels and the gate

- **D-14:** **Labels change deliberately, per issue, and the reply body says which label moved and why** —
  never a silent reclassification. Taxonomy is `.claude/skills/devtest-triage/SKILL.md:211-220`.
  - **gh#23:** add `cause:rig` alongside the standing `cause:database` (the `vpp_mv=13500` defect is real
    and unfixed, so that label was never wrong); add `needs:report`.
  - **gh#28 / gh#31:** add `needs:report`. **Withhold `fix:released`** — only the *harness* fix shipped;
    the chip defects did not — and say so explicitly rather than letting a label imply closure.
  - **gh#60 / gh#62:** labelled to match their disposition under D-15.

- **D-15:** **gh#60 closes; gh#62 stays open.** gh#60 asked for a warning-and-refusal and v1.37 ships
  exactly that in a released version — a delivered feature request closes as done. gh#62's refusal is
  correct, but the capability the reporter actually wants (a `0x05` software chip-erase, documented in the
  W29C020C command table and backlogged as **999.63**) is real work that has not been done; closing it
  would file *"we refuse, correctly"* as the end of the story. **gh#23, gh#28 and gh#31 stay open
  unconditionally** — REPLY-06, and REQUIREMENTS.md § Out of Scope.

- **D-16:** **Per-artifact blocking operator gate; agents post.** Phase 152's D-03, extended to cover the
  merges: a separate blocking checkpoint immediately before **each** public act, so approval for one issue
  cannot carry to another and the merge approval cannot carry to the posting. Each body is approved on
  disk first, posted via `gh issue comment <n> --repo henols/firestarter_prom --body-file <file>`, then
  read back from the API and proven byte-identical — Phase 173's verification discipline
  (`173-07-SUMMARY.md:115`).

  **Hard constraint (D-5, activation):** this phase must **not** run under `--auto` or `--chain`. Those
  modes auto-approve human-verify gates, and `autonomous: false` is **not** self-protecting against them.
  Every plan touching a public act carries `autonomous: false` *and* the phase is never dispatched in
  those modes.

- **D-17:** **REPLY-05's statement appears in every reply that asks for a re-run** — reports are now
  `schema_version` **2.0**, and v1.36 deliberately re-keyed `dedup_fingerprint`, so a fresh run will not
  group with the old one. A reporter must not read an intended re-key as a new defect. This is a
  requirement, not a gray area; it is recorded here so no plan omits it from a reply.

### Claude's Discretion

- Exact prose of each reply body, subject to D-13's register and the operator gate at D-16.
- File naming inside the phase directory (`187-GH{N}-COMMENT.md` per Phase 152 is the obvious precedent).
- Which specific commit SHA each permalink pins, and how the `notes/` document is sectioned.
- Plan/wave decomposition, and where the record repairs (D-07) sit relative to the ship.

### Folded Todos

- **`.planning/todos/pending/2026-09-08-uv-write-shortcut-disclosure-key.md`** — *"dev test m27c512 now
  passes on a non-blank UV part via `FLAG_SKIP_BLANK_CHECK` while `firestarter write` is still refused by
  the identical firmware, and no exported key discloses the divergence."* Folded as **reply material
  only** (D-12): its measurement becomes the caveat carried into gh#28's and gh#31's re-run asks. It does
  **not** resolve the todo — the exported-key question the todo actually poses stays pending, and this
  phase must not add a report key.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The material the replies are built from
- `.planning/notes/ae29f2008-classification-verdict.md` — REPLY-03's substance. § *"WHY THE REPORTER'S
  `--force` ERASE WORKED, AND WHY THAT IS NOT A LICENCE"* is explicitly marked *"Material for Phase 187's
  REPLY-03, per D-09."* § *"Software chip-erase for the `0x05` family"* carries the 999.63 backlog and the
  boot-block caveat.
- `.planning/notes/jumper-display-ground-truth.md` § *"Which operations energize socket pin 1 — the answer
  to gh#60"* — the direct answer to the reporter's own question (*"Just writing, or reading too?"*):
  **writing and erasing; not reading, verifying, blank-checking, or `id`.** Also carries assumption A1's
  measured confirmation.
- `.planning/REQUIREMENTS.md` §§ REPLY-01…07, § Decisions (D-1…D-7), § Out of Scope — the requirement
  text, the activation decisions, and the explicit prohibition on closing gh#23/#28/#31.
- `.planning/ROADMAP.md:488-506` — Phase 187's goal, requirements and five success criteria.
  `:202-203` — the hard ordering constraint. `:5405-5424` — the stale backlog prose D-07 repairs.

### Precedent this phase follows, by name
- `.planning/milestones/v1.32-phases/152-outward-facing-close-operator-gated/152-CONTEXT.md` — D-01…D-04.
  The near-exact analog: an outward-facing, operator-gated phase that absorbed the beta merges because
  posting first would have described unreleased code. **D-04 is the direct precedent for D-01/D-02 here**,
  including its funded costs (PRs not direct merges, two cuts fire, `git cherry` not SHA ancestry,
  `gh workflow run` blocked by the auto-mode classifier, milestone-cut CI gotchas). **D-03 is the direct
  precedent for D-16.**
- `.planning/milestones/v1.35-phases/173-close-beta-cut-under-protection-close-procedure-honesty-ledg/173-07-SUMMARY.md`
  — the posting and verification discipline (approve on disk, post via `--body-file`, read back from the
  API, prove byte-identical) and the gh#9 evidence at `:115-118`.
- `.planning/milestones/v1.35-phases/173-.../173-UPSTREAM-REPLIES.md` and `evidence/bodies/173-gh9.md` —
  the artifact shape, and the exact body already posted to gh#9.
- `.planning/notes/v135-close-procedure-under-protection.md` — the mechanics of closing under branch
  protection; `main` is protected in all three repos and `current_user_can_bypass` is `never`.

### Mechanism
- `.claude/skills/devtest-triage/SKILL.md` — the label taxonomy at `:211-220` (`cause:rig`,
  `needs:report`, `fix:committed`, `fix:released`, `chip:validated`, `fixed:superseded`), the
  `--body-file` posting convention at `:345-349`, and the fold/close rules.
- `.claude/skills/devtest-rootcause/SKILL.md:336` — the same posting convention for fix reports.

### The code the replies make claims about
- `firestarter_app/firestarter/jp5_gate.py` — `hazard_text` at `:68-79`; call sites are **write and erase
  only** (`cli_handlers.py:754`, `:889`; `eprom_operations.py:2003`, `:2147`). Not on `origin/beta`.
- `firestarter_app/firestarter/flash4_erase_gate.py` — `_REFUSAL_FORMAT` at `:43`
  (`"Erase not supported for {chip_name}"`), deliberately carrying no cause and no alternative (SAFE-06 as
  amended by D-07/D-08). Not on `origin/beta`.
- `firestarter_app/firestarter/chip_test.py:2585-2606` — the status-axis trigger; the ordering comment
  explains why the host-setup clause must precede `(SerialError, HardwareOperationError)`.
- `firestarter_app/firestarter/diagnostic_report.py:55-68` — `_RAIL_READING_DISCLOSURE` and the docstring
  that states *"a rig with VPP unhooked still reads a healthy rail."* This is D-11's evidence.
- `firestarter/src/proms/flash_5v_page.cpp` — the 52-line SAFE-08 deletion in the firmware delta.

### Live upstream state (re-verify before posting; it moves)
- gh#23, gh#28, gh#31 — open, last reporter comment 2026-08-09, all three disputing the triage.
- gh#60 — open, `enhancement`, zero comments. gh#62 — open, zero comments.
- gh#9 — open, **pinned**, one comment (`#issuecomment-5511487546`, 2026-09-02).
- gh#61 — closed `chip:validated`, `[dev test] AE29F2008 — PASS`, filed by gh#62's own reporter the same
  day. Relevant context for REPLY-03: read/write/blank all pass on that part; only erase is refused.
- gh#68 — open, names AE29F2008 (D-12).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`gh issue comment <n> --repo henols/firestarter_prom --body-file <file>`** — the established posting
  mechanism, used by both project skills and by Phase 173 for all four v1.35 replies.
- **GraphQL `pinIssue` / `pinnedIssues`** — already exercised by `173-07`; needed here only to *verify*
  gh#9's pin is intact, not to change it.
- **`.planning/notes/` verdict-document pattern** — four consecutive phases (182–185) have used it; D-09
  continues it.
- **`172-01` / `173-04` approval flow** — draft bodies to disk, operator approves on disk, post, read back,
  diff. Nothing here needs inventing.

### Established Patterns
- **Amend a requirement or criterion in the same phase as the work, with the reason on the record** —
  183 D-08, 184 D-03, 185 D-02. D-07 and D-11 both use it.
- **"Name it, file nothing" is a live operator branch, not a default** — 184 D-05/D-06 and 185 D-04 both
  chose it against the orchestrator's recommendation. D-08 chooses it again, and says so explicitly so no
  executor "helpfully" files a successor item.
- **Cuts are read, never predicted** — every prior milestone close reads the version from
  `gh release list` after `beta-release.yml` has run.

### Integration Points
- `beta-release.yml` fires on every merge to `beta` in both sub-repos; meta has no release CI.
- `main` is protected in all three repos (PR required, no force-push, `current_user_can_bypass: never`);
  this phase targets `beta` per `.planning/config.json` `git.base_branch`.
- `.planning/notes/` is tracked in the **public** `firestarter_prom` repo and present on `beta` — which is
  what makes D-13's "link the evidence" viable, and what makes D-02's meta merge a hard prerequisite for
  posting.

</code_context>

<specifics>
## Specific Ideas

- **gh#60's own question gets a direct answer.** The reporter asked *"Just writing, or reading too? Not
  sure when the VPP is on."* The answer is settled and measured: **writing and erasing; not reading, not
  verifying, not blank-checking, not `id`.** Say it in those words.
- **gh#60 also gets the honest limit.** They wrote *"I don't believe you can check if JP5 is cut
  systematically."* They are right, and REPLY-04 must confirm it from the project's own schematic record:
  the gate warns and refuses; it cannot detect the jumper. `jp5_gate.hazard_text` already says so
  (*"this tool cannot read its current state on the attached board"*), and it quotes the silkscreen —
  *"Cut for ROMs with A19 on P1"* — so the operator can check the claim against the board in front of them.
- **gh#62's reporter is told they were right.** The verdict is equivalence-based and says so plainly: the
  classification is correct **and** the reporter is correct that the silicon can be chip-erased. Both, at
  once. The reply should not choose one.
- **dim20 gets one line acknowledging gh#65 and gh#66.** They filed four issues in one day; three are
  still open. One sentence, no timeline promised.

</specifics>

<deferred>
## Deferred Ideas

- **Answer gh#65 (`MX27C4000`) and gh#66 (`MBM27C4001`).** Both filed 2026-09-09 by gh#62's reporter, both
  unanswered, both needing a full datasheet cross-check. Their own phase's work.
- **gh#21 (`at28c256`, `needs:report`)** — still awaiting a fresh run from AndersBNielsen. Not touched here.
- **Detect a mis-wired VPP at the socket** — the capability gh#23 actually needs, and the one thing that
  would change a fresh run's verdict for that failure mode. SAFE-03 already established the rail reading
  cannot prove socket routing, so this is new hardware-side work, not a host fix. **Not filed** as a
  backlog item under D-08's discipline; recorded here only.
- **Fix the three standing datasheet defects** — `W27E257` `vpp_mv` 13500→12000 (in `build_db.py`'s decode,
  never in the generated JSON), the `vdd != vcc` programming-supply gap across 358 rows, and `M27C1001`'s
  pin-30 `DIP32_27C020` mismatch. All three are restated in the replies as open; none is fixed here.
- **The `0x05` software chip-erase** — backlog **999.63**, with the W29C020C boot-block caveat
  (*"Once the boot block programming lockout feature is activated, the chip erase function will be
  disabled"*). Already filed; not this phase.

### Reviewed Todos (not folded)

`todo.match-phase 187` returned 34 candidates. All matched on generic keywords (`gsd`, `phase`, `one`,
`nothing`) rather than on this phase's subject, and none bears on an outward-facing reply. Only the UV
write-shortcut disclosure todo was folded (above). The rest are untouched and stay pending.

</deferred>

---

*Phase: 187-Answered Reports*
*Context gathered: 2026-09-12*
