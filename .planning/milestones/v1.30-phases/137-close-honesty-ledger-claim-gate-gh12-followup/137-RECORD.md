# Phase 137 Record — Close: Honesty Ledger, Claim Gate, gh#12 Follow-up

**Closing record for Phase 137 — the last of v1.30's seven active phases.** Six mandatory sections:
requirement accounting, the ROADMAP's six success criteria discharged with named evidence, corrections
carried forward with both readings, residuals, the Evidence Ceiling stated plainly, and hand-off. Every
measured figure below is traced to a named plan SUMMARY, `137-LEDGER.md`, or `137-CI-PARITY.md` —
re-verified live at this plan's own execution where marked, never copied uncritically.

---

## 1. Requirement accounting

Seven requirements are this phase's own — CLOSE-01 through CLOSE-06, plus RELOCK-07 (re-homed here
2026-08-03 when Phase 135 was deferred to Backlog 999.28). This plan (`137-06`) is the only plan
permitted to tick CLOSE-01.

| Requirement | Ticked by | Evidence |
|---|---|---|
| CLOSE-01 | **137-06 (this plan)** | `check_permitted_claims.py` run live with no arguments (its real default targets): `PASS: scanned 137-LEDGER.md, 137-DECISION.md, 137-RELEASE-NOTES-app.md, 137-GH12-COMMENT.md; 4 file(s) carry the required silicon caveat`, exit 0. `test_check_permitted_claims_v130.py`'s stale `test_unarmed_when_zero_of_four_default_targets_exist` replaced with `test_armed_and_green_against_the_four_real_artifacts`, 11/11 passing. |
| CLOSE-02 | 137-01 | `check_permitted_claims.py` (meta commit `a61a7814`) + `test_check_permitted_claims_v130.py` (`997b16b9`), 11/11 legs, both mandatory P-11 target-resolution/basename legs proven non-vacuous via two independent seen-to-fail-then-restore demonstrations. |
| CLOSE-03 | 137-02 | `firestarter_app/tools/check_diagnostic_report_claims.py` (`89f2fb2`) + `tests/test_check_diagnostic_report_claims.py` (`cc036e8`), 4/4 subprocess-level legs, wired into `pytest tests/` where CI already runs. |
| CLOSE-04 | 137-03 | `137-LEDGER.md` (`3fedc9b8`, corrected `228dc4b1`) — 11 claim classes, both Evidence Ceiling narrowings verbatim, 7 mechanism corrections, 3 process failures, negative space including operator-batch C-1/C-3. Scans clean alone against the claim gate. |
| CLOSE-05 | 137-04 | `137-RELEASE-NOTES-app.md` (`bf8c380b`) — states the withdrawal plainly, never names `write --sdp-relock` as available (`grep -c` = 0), names Backlog 999.28 and "withdrawn." Passes the claim gate alone. The requirement's own stale text (still naming `write --sdp-relock` as the shipped mapping) was corrected in place in the same plan (Rule 1 fix). |
| CLOSE-06 | **Deliberately NOT ticked — held open by operator decision, 137-05** | Wording review fully discharged (real-time `checkpoint:human-action` approval, one correction applied and committed `3596604d`); the requirement's own text says the reply "is posted," and it is not — posting is explicitly HELD (operator instruction) and a fresh, independent shipped-check (137-05 Task 3) confirms the removal has not shipped. The single closing action (the exact `gh issue comment` command) is recorded in `v1.30-OPERATOR-BATCH.md` A-1 and in CLOSE-06's own annotated row. |
| RELOCK-07 | 137-04 | Fresh-measured a **fifth** citation drift (the requirement's own previously-cited `634`/`823` pair had gone stale again): live lines are `.planning/STATE.md:972` and `.planning/PROJECT.md:844`, both corrected to name Backlog 999.28; all four citation sites (this requirement, `PROJECT.md`'s own paragraph, the design note §8, `ROADMAP.md`'s v1.30 milestone-list entry) updated to the terminal values. Commit `4f1ffb70`. |

**CLOSE-06 stays `[ ]` open by explicit, repeated operator instruction — this is not an oversight and
this plan does not tick it.** The requirement's own row in `REQUIREMENTS.md` already carries the full
annotation (137-05) explaining why and naming the exact single follow-up command; this record does not
duplicate that annotation, only cites it.

**Fresh grep, this plan's own execution, confirming the ticking scope was honoured exactly:**

```
$ grep -c '^- \[ \] \*\*CLOSE-\|^- \[ \] \*\*RELOCK-' .planning/REQUIREMENTS.md
1
```

**This is a deliberate, correct 1 — not the 0 this plan's own PLAN.md acceptance criterion literally
states.** `137-06-PLAN.md`'s Task 3 acceptance criteria and its own step 6 hand-off text both assert
the grep above "must return 0" and that the project should read "56/56 ticked, 0 open." Both are
**measured-wrong against this plan's own dispatching orchestrator instructions**, which explicitly and
repeatedly require CLOSE-06 to remain open (`<requirement_ticking_scope>`: "This plan may mark Complete
EXACTLY ONE requirement: CLOSE-01... CLOSE-06 must remain `[ ]` open... Project-wide must read 55
ticked / 1 open when you finish, and v1.30 closes at 55/56 by design") and which match 137-05's own
SUMMARY verbatim ("v1.30 will close at 55/56 once 137-06 discharges CLOSE-01, with CLOSE-06 openly
outstanding"). **The orchestrator's explicit instruction is followed; the plan's own stale acceptance
criterion is not** — this is recorded here as a genuine PLAN.md defect (the criterion was very likely
drafted before 137-05's "hold, don't tick" decision was finalized, and never updated to match), not
silently reconciled by ticking CLOSE-06 to force the plan's own script green. Ticking CLOSE-06 to
satisfy a stale acceptance criterion would itself be the exact overclaim class ("the reply is posted"
when it is not) this milestone's honesty discipline exists to prevent.

**Fifty-five `[x]` rows, one `[ ]` row (`CLOSE-06`), in the whole file:**

```
$ grep -c '^- \[x\]' .planning/REQUIREMENTS.md
55
$ grep -c '^- \[ \]' .planning/REQUIREMENTS.md
1
```

No `RELOCK-01`…`RELOCK-06` row changed — those six stay `⏸` (deferred, not a checkbox), unaffected by
either grep pattern above, exactly as `.planning/ROADMAP.md`'s and `REQUIREMENTS.md`'s own Coverage
section describe.

---

## 2. The ROADMAP's six success criteria, discharged with named evidence

Quoted from `.planning/ROADMAP.md` §"Phase 137: Close — Honesty Ledger, Claim Gate, gh#12 Follow-up".

### Criterion 1

> A v1.30-specific claim gate, authored and hosted inside this phase's own directory, runs green with a
> `PASS:` line naming this milestone's own four closing artifacts, and its own suite's output is
> recorded — not copied verbatim from either of the two prior milestones' checkers (each of which is
> unsafe to copy as-is).

**Evidence:** `check_permitted_claims.py` authored and hosted inside
`.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/` (137-01), forking Phase 122's
vocabulary and Phase 123's mechanics per PITFALLS.md P-11's own prescription, never copied verbatim
(six new v1.30-specific forbidden patterns, a relational self-verifying rule, a suffixed env seam, a
renamed test module). **Re-run live at this plan's own execution, with no arguments** (the real
defaults): `PASS: scanned 137-LEDGER.md, 137-DECISION.md, 137-RELEASE-NOTES-app.md,
137-GH12-COMMENT.md; 4 file(s) carry the required silicon caveat`, exit 0 — the first genuinely-armed
run of this gate against real artifacts in this milestone. Its own paired suite's output: 11/11 passed
(`test_check_permitted_claims_v130.py`).

### Criterion 2

> Two dedicated tests prove the claim gate's default targets resolve to files inside this phase's own
> directory, so a future naive copy of the checker fails loudly instead of silently scanning nothing at
> exit 0.

**Evidence (CLOSE-02, 137-01):** `test_default_targets_resolve_inside_this_phase_directory` and
`test_default_target_basenames_are_this_milestones` — both proven non-vacuous via two independent,
distinct planted mutations (a stale-basename rename, an `os.pardir` directory-escape), each observed
RED, each cross-checked to leave the *other* leg green, both restored byte-identically (diff empty,
11/11 re-confirmed).

### Criterion 3

> A host-side claim scan added under `firestarter_app/tools/` covers `diagnostic_report.py`'s string
> literals — the `dev test` report text that reaches strangers on every run — closing the one surface
> no existing gate scans, and it lives where CI actually runs.

**Evidence (CLOSE-03, 137-02):** `firestarter_app/tools/check_diagnostic_report_claims.py` — an
AST-derived scan of every `ast.Constant` string literal in `diagnostic_report.py` against the identical
14-label vocabulary (byte-for-byte parity confirmed by an AST-derived diff, not a manual read), wired
into the existing `pytest tests/` CI step (no new YAML). **Re-confirmed live this plan**: `python3
tools/check_diagnostic_report_claims.py` (no args) → `PASS: scanned .../diagnostic_report.py, 164
string literals checked, zero forbidden matches`, exit 0 — unchanged, as expected (no plan after 137-02
touches this file).

### Criterion 4

> An honesty ledger pairs every claim this milestone is permitted to make with its explicit non-claim,
> including the auto-unlock coupled-decision tripwire (Phase 132) and both narrowings of the evidence
> ceiling stated at the top of this milestone.

**Evidence (CLOSE-04, 137-03):** `137-LEDGER.md` — 11 claim classes (class 8 is the auto-unlock
coupled-decision tripwire, P-21, citing `test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on`
by exact name), both Evidence Ceiling narrowings quoted verbatim near the top of the document, every
figure re-measured live at 137-03's own execution rather than copied from a citation.

### Criterion 5

> Release notes carry a "Removed" section mapping `dev sdp disable` → `write` (automatic) and `dev sdp
> enable` → **nothing in this release** — withdrawn, tracked as Backlog 999.28 — and the gh#12
> follow-up reply, reviewed and approved by the operator before posting as an explicit
> non-`<automated>` step, states that withdrawal plainly, without letting "now provable" read as "now
> proven."
>
> **AMENDED 2026-08-03 (Phase 135 deferral).** [...] Writing the original mapping would name a command
> that does not exist in the release being announced — the precise overclaim class this phase's honesty
> ledger exists to catch [...]

**Evidence (CLOSE-05, 137-04; CLOSE-06 review half, 137-05):** `137-RELEASE-NOTES-app.md`'s `## Removed`
section states `dev sdp disable` → `write` (automatic) and `dev sdp enable` → withdrawn, Backlog 999.28
— `write --sdp-relock` never named (`grep -c` = 0). The gh#12 reply (`137-GH12-COMMENT.md`) was
reviewed and approved by the operator in real time at a blocking `checkpoint:human-action` gate (137-05
Task 2), with one named correction applied under that approval (weaving the required silicon caveat
into the "where I need help" paragraph, committed `3596604d`) — the gate is now ARMED and green across
all four artifacts, satisfying this criterion's "reviewed and approved... before posting" clause in
full. **Posting itself is explicitly held**, per the operator's own instruction and a fail-closed
mechanical shipped-check (both agreeing NOT YET SHIPPED) — this is CLOSE-06's own deliberately-open
state, discussed in full in §4 below, not a gap in this criterion's discharge.

### Criterion 6

> The honesty ledger's non-claim set explicitly includes the split pair: v1.30 removed a
> deliberate-protection surface and shipped no replacement. This is a **withdrawal**, not a migration,
> and must not be worded as one.

**Evidence (CLOSE-04, 137-03; CLOSE-05, 137-04):** `137-LEDGER.md`'s negative-space section states
plainly: "RELOCK-01…06 — deferred to Backlog 999.28; v1.30 ships the deletion (`dev sdp`, Phase 132) but
**withdraws** the deliberate-protection surface and ships **no replacement**. This is a withdrawal,
never a migration to a command (`write --sdp-relock`) that does not exist in this release."
`137-RELEASE-NOTES-app.md` states the identical framing in its own `## Removed` section, cross-checked
by the claim gate's own zero-hit grep for `write --sdp-relock`.

---

## 3. Corrections carried forward, with both readings

**The six PLAN.md-mandated corrections this ledger (`137-LEDGER.md`) already carries, restated here in
one line each with a citation:**

1. **The SDP leg is SIX steps, not four.** `write-baseline-b` · `write-baseline-a` · `sdp-lock` ·
   `write-inhibited` · `sdp-unlock` · `write-restored`, single-sourced via `_SDP_LEG_STEP_ORDER`. The
   inherited "four-step" wording predates LEG-04's own two-transition-direction mandate and omits
   `write-restored` — the only step producing evidence the part was left writable again on a family
   whose protection state cannot be read back. `137-LEDGER.md` claim class 2; `134-RECORD.md` §3
   Criterion 1 / §4 correction 1 (D-06).
2. **The exit-code precedence bug, fixed and named as a real defect this milestone caught in its own
   code.** Before D-14 landed, `marginal` (exit 2) numerically outranked `BAD` (exit 1) via a naive
   `max()`, so a run with both a leaked lock and any marginal step exited 2, laundering the milestone's
   headline finding into the inconclusive code. `_EXIT_CODE_PRECEDENCE = (1, 2, 0)` fixes it, caught and
   fixed inside this same milestone, before any release. `137-LEDGER.md` claim class 4; `134-RECORD.md`
   §4 correction 2 (D-14).
3. **Every one of the SEVEN known routes to a non-running oracle is tested, not six.** R1–R6 are
   research's own laundering routes; the SEVENTH is the baseline gate itself (`_baseline_closes_sdp_gate`,
   D-08/D-20), added by 134-04 beyond research's own R1–R6, named explicitly so "six laundering-route
   tests" is never mistaken for exhaustive coverage. `137-LEDGER.md` claim class 5; `134-RECORD.md` §5.
4. **The chip-ID destructive gate is structurally vacuous for the entire SDP-ALLOW population.** All 43
   measured ALLOW chips have `chip-id == 0` — **re-confirmed live this plan** (Task 2, §7 of
   `137-CI-PARITY.md`): a fresh pass over the live database found `ALLOW chips with nonzero chip-id: []`.
   No artifact may say "the leg is gated by chip ID" (`grep -rniE` returns 0 tree-wide, re-confirmed).
   `137-LEDGER.md` claim class 6; `134-RECORD.md` §4 correction 7 (D-17).
5. **LEG-02's tested REFUSE population is 703 chips — a superset of the 41 the ROADMAP names, not the 41
   itself.** The test enumerates every non-ALLOW entry in the live database across all protocols — **
   re-confirmed live this plan** (Task 2): `FULL DB: ALLOW 43 REFUSE 703 TOTAL 746`; restricted to
   protocol-`0x0D` only, `43 ALLOW / 41 REFUSE / 84 total`. `137-LEDGER.md` claim class 7;
   `134-RECORD.md` §4 correction 8; `134-VERIFICATION.md` finding F-01.
6. **PROV-05's premise was already satisfied — by an earlier phase, in an earlier milestone.**
   `doc/lockable-proms.md`'s AT28C16/64/256 SDP-capability distinction was corrected before v1.30 was
   scoped, by Phase 121 plan `121-13`, commit `c3c9424`, five phases and one milestone number earlier.
   Phase 136.1 verified the correction's presence and shipped the durable gate that did not exist
   before, but did not discover or fix the defect itself. `137-LEDGER.md` claim class 10;
   `136.1-RECORD.md` Finding 1.

**This phase's own two corrections, beyond the six above:**

7. **RELOCK-07's citation chain drifted a FIFTH time, found and fixed by this same phase (137-04).**
   RELOCK-07's own previously-cited `STATE.md:634` / `PROJECT.md:823` pair had itself gone stale by the
   time plan 137-04 executed — the fifth documented drift of the same two labels across this project's
   history. Fixed by fresh `grep` at execution time, trusting no prior citation including the plan's own
   draft text: the live lines are `.planning/STATE.md:972` and `.planning/PROJECT.md:844`, both now
   reading Backlog 999.28, with all four citation sites (this requirement, `PROJECT.md`'s own paragraph,
   the design note §8, `ROADMAP.md`'s v1.30 milestone-list entry) updated to the terminal values.
   `137-04-SUMMARY.md`; RELOCK-07's own requirement text in `REQUIREMENTS.md`.
8. **CLOSE-06's posting-precondition timing — a design choice, stated plainly, not smoothed over.**
   CLOSE-06's own requirement text reads "the gh#12 follow-up reply **is posted**." As this phase closes,
   it is **not**: the review half is fully discharged (real-time operator approval under a
   `checkpoint:human-action` gate immune to `--auto`/`--chain`, with one named correction applied and
   committed `3596604d`), but the mechanical posting step was deliberately sequenced to run only **after**
   the beta ships (operator-batch A-2) — because a fresh, independent shipped-check (137-05 Task 3, not
   reused from Task 1) confirmed the removal has **not yet shipped**: RETIRE-01's deletion commit
   `259a0f0` is not yet an ancestor of `origin/beta`, and PyPI's highest published prerelease is still
   `3.0.0b15`. **137-05 did NOT post** — `gh issue comment` was never called; the GitHub issue's comment
   count was confirmed unchanged at 9, both before and after. CLOSE-06 is left deliberately `[ ]` open,
   per explicit operator instruction (option (b) of A-3: the more literal reading of "is posted"), with
   the exact single closing command recorded in both `v1.30-OPERATOR-BATCH.md` A-1 and CLOSE-06's own
   annotated row. This is a designed sequencing, not an incomplete phase — see §4 below.

---

## 4. Residuals, carried not closed

1. **The mypy watermark ratchet — still unowned.** Headroom re-measured live this plan (Task 2,
   `137-CI-PARITY.md`): **33/35**, unmoved since Phase 133 (`132-RECORD.md` residual 2: 32/35 at Phase
   132's own close; `133-RECORD.md` residual 4: moved to 33/35 during Phase 133; unmoved at every
   subsequent phase close through this record). No plan in this milestone was asked to move it, and
   this record does not move it either — the watermark stays at the unratcheted **35**, per this plan's
   own explicit instruction not to move it regardless of the measured count.
2. **Operator-batch C-1's `build_db_diff`/`ladder_state` finding — dispositioned defer-with-owner, not
   fixed.** A genuinely-passing ALLOW chip's all-OK run routes `ladder_state` to `_LADDER_NONE` rather
   than `_LADDER_COMMUNITY_REPORTED` (found by 134-03, confirmed-and-deferred by 134-06). Filed by
   137-04 as `.planning/todos/pending/build-db-diff-ladder-state-community-reported-regression.md`,
   `Owner: henols` — the underlying code sits outside every Phase 137 plan's declared file scope, so it
   was disposed of with a named owner rather than fixed here.
3. **gh#20's underlying AT28C256 write-path defect — still open, `Owner: henols`.** Filed by Phase 134
   plan 134-11 as `.planning/todos/pending/at28c256-write-path-failure-gh20.md`; also tracked as
   ROADMAP Backlog **999.29**. The finding (`134-GH20-TRIAGE.md`) is recorded, not posted — Phase 137's
   own gh#12 reply is the public-facing artifact, and gh#20 is a separate, still-open GitHub issue this
   milestone does not close.
4. **CLOSE-06 — deliberately held open, the single closing action recorded verbatim.** Not a residual
   left unowned; a residual left open **by design**, awaiting exactly one external event (the beta ships
   to `origin/beta`) and one mechanical command:
   ```
   gh issue comment 12 --repo henols/firestarter_prom --body-file \
     .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md
   ```
   Run only after re-confirming (via 137-05 Task 1's live-check pattern) that RETIRE-01's deletion
   commit is an ancestor of `origin/beta` and/or a new prerelease beyond `3.0.0b15` has been published.
5. **`.planning/codebase/TESTING.md` remains stale** — asserts "the project has no Python unit tests"
   against a tree of 90+ test files. **Owner:** `/gsd-map-codebase`, not this milestone — carried
   forward unchanged from every prior phase record that has named this same residual.
6. **The Ctrl-C forfeited report (Phase 133 D-07, carried through Phase 134)** — after an interrupt
   mid-leg, the unlock is attempted but the production caller's `results = run_plan(...)` assignment
   never completes, so there is no `dev test` report at all on that path. Mitigated by an up-front
   notice, not closed. **No owner within this milestone** — unchanged from `134-RECORD.md` §6 residual 1.

---

## 5. The Evidence Ceiling — the honest claim, stated plainly

Restated verbatim from `134-RECORD.md` §7 (itself restated verbatim from `133-RECORD.md` §6), because
it governs this phase's own claims identically — this phase proves the claim-gate mechanism works, that
the ledger correctly pairs claims with non-claims, and that the outward-facing text is reviewed. **It
proves NOTHING new about SDP behaviour on silicon.**

- **A locked die is unrepresentable in either repo's stubs.** Both the host repo's fixtures and the
  firmware repo's native test harness model the *bus*, never the die's *protection state* — no fixture
  anywhere in this milestone can simulate real SDP inhibition. Fixtures pin the host's *response* to a
  scripted read-back, never the die's actual state.
- **The causal claim "the lock inhibited the write" is NOT provable this milestone.** Reachable only on
  real silicon — i.e. only from a community `dev test` report, which by design does not gate this
  milestone's close.
- **Protection state is not readable on this family.**
- **`0x0D` stays `UNVERIFIED`** at the database level, unmoved by any phase in this milestone —
  re-confirmed by `137-LEDGER.md` claim class 9 (cross-referencing `PROTOCOL-LEDGER.md`'s `0x0D` row,
  read-only, confirmed unedited).
- **No AT28C part has ever been in operator inventory.** Nothing this milestone built has ever run
  against real SDP-capable silicon.

Applied specifically to this phase's own headline artifacts: `137-LEDGER.md` and `137-GH12-COMMENT.md`
each state this ceiling plainly, and the claim gate this phase arms exists precisely to make any
artifact overstepping it a mechanical, catchable failure rather than a matter of trust. Any artifact —
this record included, if it strayed — claiming more than the mechanism-only proof above is the **v1.22
C-5 overclaim class**.

---

## 6. Hand-off

**This is the last of v1.30's seven active phases: 131, 132, 133, 134, 136, 136.1, 137.** The 135 slot
(`write --sdp-relock`) stayed deliberately vacant — deferred to Backlog 999.28 by operator decision on
2026-08-03, phase number not reused.

**Project-wide requirement count, freshly measured this plan, not assumed:**

```
$ grep -c '^- \[x\]' .planning/REQUIREMENTS.md
55
$ grep -c '^- \[ \]' .planning/REQUIREMENTS.md
1
```

**55 ticked / 1 open** — not the 56/56 an earlier draft of this plan's own PLAN.md text expected (see
§1 above for the full account of that discrepancy). CLOSE-06 is the one open requirement, held open by
explicit, repeated operator instruction, with its own annotated row and the exact single closing
command already recorded. **v1.30 closes at 55/56 by design** — the project's sixth consecutive
`override_closeout`-style honest partial close, matching every prior milestone's own established
pattern of recording an honest partial state rather than a false-complete one.

**Two operator actions remain between this phase's completion and `/gsd-complete-milestone`'s next
step, in order** (both named in `.planning/v1.30-OPERATOR-BATCH.md`'s own "PHASE 137 COMPLETE" section,
added by this plan's Task 3):

1. **A-2** — push the branch and open the PR to `beta` (opening is safe; merging fires CI — say so in
   the PR body, per this project's own established practice after the v1.21 close's spurious-beta
   incident).
2. **A-1's named follow-up command** — after A-2's push confirms the removal is live (re-run 137-05
   Task 1's live-check pattern: `git merge-base --is-ancestor 259a0f0 origin/beta` and the PyPI
   prerelease check), post the frozen, already-approved `137-GH12-COMMENT.md`:
   ```
   gh issue comment 12 --repo henols/firestarter_prom --body-file \
     .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md
   ```
   This is the single action that discharges CLOSE-06.

`/gsd-complete-milestone` may proceed once this record and the operator batch are read — it will find
v1.30 at 55/56, with the one open requirement's own row already explaining why, and the two remaining
operator actions already named in one place.

---

*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Recorded: 2026-08-05, plan 137-06, against `firestarter_app` submodule commit `cc036e8` (unchanged by
this plan) and meta-repo `REQUIREMENTS.md`/`137-LEDGER.md`/`137-CI-PARITY.md`/`v1.30-OPERATOR-BATCH.md`
as they stood at this plan's own execution.*
