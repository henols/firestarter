# Phase 185: Records and Checks That Are Current - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-11
**Phase:** 185-records-and-checks-that-are-current
**Areas discussed:** Catalog sync on main, `_is_interactive` blast radius, Fixture severance shape,
Citation form & scope folds (all four selected by the operator)

---

## Area selection

The operator selected all four offered gray areas.

---

## Catalog sync on main (CLAIM-08)

### Q1 — first attempt

| Option | Description | Selected |
|---|---|---|
| Skip-with-reason on main | Resolve all three at one branch name; exit 0 with a printed reason when the catalog is absent at that ref | |
| Move the trigger to beta | Run on `beta` + PRs; asserts a property that passes today | |
| Fallback resolves meta too | Resolve the meta checkout at `beta` as well so all three operands share a branch | |
| Land the catalog on all three mains | The root fix; a stable-release action | |

**User's choice:** none — the operator interrupted to ask *"Before I can answer, what is the purpose
of the catalog and what does it do?"*

**Notes:** The orchestrator answered from source rather than memory: `messages.toml` is the canonical
numbered log/status catalog (131 entries) from which `codegen.py` generates
`firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py`; the firmware puts a
number on the wire and the host decodes it, so divergence means silent misreporting;
`sync_to_subrepos.sh` distributes byte-identical copies into both sub-repos. It was also measured and
reported that both sub-repos' CI already run catalog validity and codegen drift gates on every branch,
so the meta workflow's only unique assertion is the cross-repo vendoring identity.

### Q1 — re-asked after the explanation

**User's choice (free text):** *"The catalog has no value to the main branch and shall not be executed
by the CI, its a tool that is used when a new message is created while developing and must be
generated there and then. If its not executed before fw is commited the fw will not compile."*

**Notes:** This selected none of the four offered options — it rejected the premise that the check
should run on `main` at all. Recorded verbatim in CONTEXT.md D-01.

### Q2 — how far the removal goes

| Option | Description | Selected |
|---|---|---|
| Retire the workflow entirely | Delete `catalog-sync-check.yml`; the compile and per-sub-repo drift gates are the real enforcement | ✓ |
| Keep it, manual dispatch only | Strip `push`/`pull_request`, leave `workflow_dispatch` | |
| Re-point it at beta | Keep the cross-repo assertion where the catalog exists | |

**User's choice:** Retire the workflow entirely.

**Notes:** Taken against the orchestrator's recommendation, which was "Move the trigger to beta" in Q1
and "Re-point it at beta" in Q2. The orchestrator flagged before the choice that CLAIM-08 and ROADMAP
criterion 5 both become unsatisfiable as written, and that both would need amending in this phase —
the operator proceeded. Recorded as D-02.

### Q3 — what the retirement record says

| Option | Description | Selected |
|---|---|---|
| Name it, file nothing | Note states the retirement, the cause, and that cross-repo vendoring identity is now unguarded, with why that is acceptable | ✓ |
| Name it and file a backlog item | Same note plus a 999.x successor item | |
| Just record the cause | Explain the failure and stop there | |

**User's choice:** Name it, file nothing.

**Notes:** The orchestrator raised the residual gap once, unprompted — that after the retirement a
hand-edit of one sub-repo's vendored `messages.toml`, bypassing meta and the sync script, would
regenerate cleanly, compile, and diverge silently. The operator chose to have it named but not
tracked. Recorded as D-03 (contents) and D-04 (file nothing).

**Post-decision correction:** while verifying the record before commit, the orchestrator found its own
earlier claim — "6 runs, 6 failures, never once succeeded" — was wrong. The true history is 8 runs,
6 failures, **2 successes**, both on the `gsd/v1.31-…` PR branch on 2026-08-18 after `57e63429`
landed. Both `main` runs failed. This strengthens rather than weakens the decision: the check works
where the catalog lives and is meaningless on `main`. CONTEXT.md was corrected before commit, and the
now-false comment inside the workflow file was added to D-03's required contents.

---

## `_is_interactive` blast radius (CLAIM-07)

> `AskUserQuestion` failed twice with `AbortError: Stream closed` at this point; the remaining
> questions were presented as plain-text numbered lists and answered together.

### Q1 — `_off_tty()` and its call sites

| Option | Description | Selected |
|---|---|---|
| Delete it, unwrap all 51 | `CliRunner` is non-TTY by construction, so the state needs no forcing; behaviour-neutral | ✓ |
| Re-point at a real seam | Keep all 51 sites but patch `submit.py`'s `isatty_fn` | |
| Keep as a documented no-op shim | Leave the sites, patch nothing, document why | |

**User's choice:** Option 1 (accepted as part of "All sounds good").

**Notes:** Measured during discussion at **51 uses across 50 distinct tests** plus 3 direct patches —
against the source todo's estimate of ~14. The corrected figure was put in front of the operator
before the choice.

### Q2 — what the two `..._on_a_tty` tests become

| Option | Description | Selected |
|---|---|---|
| Rename and merge | Collapse the redundant on/off pair into one test; rename the `hasattr`-only test | ✓ |
| Rename, keep both | Honest names, accept the duplication | |
| Give them real TTY simulation | Inject a true `isatty_fn` through the CLI | |

**User's choice:** Option 1.

**Notes:** The orchestrator surfaced that once the inert patches are removed the on-TTY and off-TTY
tests assert identical things, so one is redundant — and that option 3 would build a seam to test
nothing, since `dev test` has no TTY-dependent behaviour left after quick task 260822-aq6.

---

## Fixture severance shape (CLAIM-04/05)

### Q3 — the six orphaned fixtures

| Option | Description | Selected |
|---|---|---|
| Delete them | Same defect class as CLAIM-02, same disposal 184 used | ✓ |
| Leave them, file a todo | Out of CLAIM-04/05's literal wording | |
| Leave them, file nothing | They stay as sediment | |

**User's choice:** Option 1.

**Notes:** The six were established by a repo-wide search (excluding `.git`, `.pio`, and each file's
own self-match) as referenced **nowhere** — not in code, not in prose. Every other retired-generation
fixture is still named somewhere and was excluded from scope.

Most of this area turned out to be settled by precedent rather than open: the family naming, the
in-place native-summary update, and BASE-01's freeze were all presented as decided-not-asked and drew
no objection.

---

## Citation form & scope folds

### Q4 — folding the `sync_to_subrepos.sh` tautology todo

| Option | Description | Selected |
|---|---|---|
| Fold it in | Repairs the one remaining guard on the property that just lost its CI check | ✓ |
| Leave deferred | Stays a pending todo; the note names it as the unguarded path | |

**User's choice:** Option 1.

**Notes:** The fold became materially more relevant *because* of D-01 — retiring the workflow makes
this script the sole mechanism asserting cross-repo catalog identity, and two of its three
verifications compare a path to itself.

CLAIM-06 itself produced no gray area: the same file already carries the correct symbol-and-scope form
at line 129, so line 40 simply adopts it.

---

## Claude's Discretion

Six calls were taken from precedent, stated to the operator as decided-not-asked, and drew no
objection:

- The new family name `captured_build_v185_*` plus its planted sibling (families are phase-numbered;
  Phase 158 was itself a cold baseline re-record).
- The two native summary fixtures updated in place rather than severed.
- `size_baseline_base01.json` never re-anchored.
- CLAIM-06's replacement citation form, copied from line 129 of the same file.
- CLAIM-08's record living in `.planning/notes/`.
- Amending the requirement and criterion in the same phase as the work.

Four further calls were the orchestrator's recommendations, accepted wholesale by the operator's
"All sounds good": D-05, D-06, D-12 and D-14.

The two decisions the operator made directly, which must not be revisited without asking them:
**D-01** (retire outright, against the recommendation) and **D-04** (name the gap, file nothing).

## Deferred Ideas

- A successor guard for cross-repo vendored-catalog identity — explicitly declined (D-04). Recorded
  as a rejected option, not a backlog candidate. Do not file it.
- `test_configure_memory.cpp:9` cites `build_db.py:89`; `KNOWN_PROTOCOLS` is at 137. Same defect class
  as CLAIM-06, firmware repo, outside this phase. Carried forward unfiled from 184's deferred list.
- A mechanical guard against `\.py:\d+` citations in test docstrings — in the spirit of 184's
  CLAIM-09, but a new capability, so its own phase.
- The retired-generation fixtures that survive D-12; nothing prunes them on a schedule.

## Reviewed Todos (not folded)

`todo.match-phase 185` returned 35 matches. Two were folded
(`2026-09-09-is-interactive-dead-after-181-04.md`, which carries `resolves_phase: 185` in its own
frontmatter, and `2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md`). The two highest-scoring
matches at 0.9 were reviewed and rejected: `2026-08-27-strip-gsd-provenance-comments-from-source.md`
(a standing `CLAUDE.md` rule, not a unit of work) and
`2026-08-30-remove-cmd-verify-from-firmware-compare-in-app.md` (a firmware protocol change, barred by
the milestone's Out of Scope). The remaining 31 scored 0.6 on generic keyword overlap with no semantic
bearing on any CLAIM requirement.
