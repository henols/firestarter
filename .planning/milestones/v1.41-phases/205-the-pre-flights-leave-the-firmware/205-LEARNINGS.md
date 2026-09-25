---
phase: 205
phase_name: "the-pre-flights-leave-the-firmware"
project: "Firestarter — Protocol-Aware Programming Architecture"
generated: "2026-09-23"
counts:
  decisions: 14
  lessons: 11
  patterns: 14
  surprises: 11
missing_artifacts:
  - "205-UAT.md"
---

# Phase 205 Learnings: The pre-flights leave the firmware

## Decisions

### D-01 — `erase -b` is re-implemented on the host before the firmware loses it
`erase -b` keeps its meaning and is rebuilt one tier up on Phase 202's `check_eprom_blank`,
whole-device (not region-scoped) and opt-in behind `-b`. Plan 01 landed it as the explicit
precondition for plans 02–07's firmware sweep.

**Rationale:** The roadmap's stated safety property is that the host gains a capability before
the firmware loses it — the same sequencing Phase 203 used for the write guard. Erase on this
family is device-global, so there is no region to scope to.
**Source:** 205-CONTEXT.md § Implementation Decisions (D-01); 205-01-SUMMARY.md

---

### D-02 — `erase -b` adopts the 0/1/2 exit contract with no mapping layer
`0` erased and blank, `1` erased but not blank, `2` transport or hardware failure during the
check. Plain `erase` keeps 0/1. The handler `sys.exit`s directly on the engine's verdict rather
than mapping a bool to an int.

**Rationale:** Follows Phase 203's D-13, and refuses to re-create the filed `dev test` defect
where a transport failure reads as a chip verdict. `erase_eprom` itself stays `bool` (Fork A) —
D-02 widens the *check's* contract, not the erase's.
**Source:** 205-CONTEXT.md (D-02); 205-01-SUMMARY.md

---

### D-03 — One terse line on failure, and `erase` gains no `--full`
A failed post-erase check prints exactly one line. The documented escape hatch for a full
diagnosis is `firestarter blank <chip> --full`, stated in the `erase` docstring.

**Rationale:** Mirrors Phase 203's D-10/D-11 and the standing terse-output preference (v1.40
Phase 200 UAT rejected a multi-line warning for a one-line form, commit `b3a777e`). Recorded
explicitly so the absence of a richer diagnosis is not mistaken for an oversight — a whole-device
post-erase scan *would* have supported one; terseness was chosen deliberately.
**Source:** 205-CONTEXT.md (D-03); 205-01-SUMMARY.md

---

### OQ-1 — `erase -s <addr> -b` is refused before the erase runs, from a sibling helper
Exit 2, one stated line, checked pre-wire. The refusal lives in `cli_handlers.py` next to
`_region_refusal_exit_code` rather than in a new gate module.

**Rationale:** A whole-device check after a sector erase reports the untouched remainder as
non-blank — a reliable false negative on protocol `0x06`. Exit 2 is the same class the existing
sibling helper returns for both of its refusals, so the shape was settled by local precedent
rather than invented.
**Source:** 205-01-SUMMARY.md (Forks B/C/D)

---

### D-04 — Full retirement of `FLAG_SKIP_BLANK_CHECK` (0x08), with the skew accepted knowingly
The bit leaves both ladders; `-b` reaches the Phase 203 guard as an explicit host-side signal
instead of a wire bit.

**Rationale:** Unlike WRITE-02 (203 D-02) and FWCMD-05 (204 D-03), measurement did not contradict
the requirement — it only priced it. The accepted cost: a post-205 host driving pre-205 firmware
no longer suppresses the firmware's surviving pre-flight. A host firmware-version gate was
considered and rejected (out of milestone scope, and the host structurally cannot read a firmware
prerelease suffix).
**Source:** 205-CONTEXT.md (D-04); 205-04-SUMMARY.md

---

### The `-b` re-plumb is a keyword-only parameter, not a positional one
`write_eprom` gained `blank_check_requested: bool = True`, keyword-only, threaded to
`write_blank_guard.requires_blank_check` as its own keyword-only parameter of the same name.

**Rationale:** `build_flags`' own docstring records that both production callers pass its first
four parameters positionally, and `write_eprom`'s signature is read by roughly forty bool-valued
test sites. A keyword-only addition leaves every existing positional caller byte-identical by
construction — the same shape Phase 203's `suppress_verdict_line` established.
**Source:** 205-CONTEXT.md § Claude's Discretion; 205-04-SUMMARY.md

---

### A reserved-gap record names the retired bit's *value*, never its identifier
Both the firmware header's and `constants.py`'s reserved-gap comments describe `0x08` and the
behaviour it used to select, without writing the macro name.

**Rationale:** The record coexists with a repository-wide absence scan for that identifier. Naming
the identifier in the record would make the record itself a hit on the gate guarding its own
retirement.
**Source:** 205-04-SUMMARY.md (tech-stack patterns)

---

### D-09 — Full sweep: everything reachable only from the deleted machinery goes with it
Not a literal five-symbol removal — the orphaned `uint32_to_bytes`, the `RAW_DATA_PROGRESS`
branch, the saved-address cursor and the chunk-size constant all went too.

**Rationale:** Follows 204's D-01 (a bisect should not land on a state that compiles dead
machinery), reinforced by FWBLANK-05 — a literal reading would leave orphaned code and understate
the measured number the requirement asks for.
**Source:** 205-CONTEXT.md (D-09, with its 21-site measured census); 205-03-SUMMARY.md

---

### The golden's `meta.recorded_by` audit log was left intact, excluded by construction
It still quotes the deleted function names verbatim as historical record (Phase 142/143/145/201
entries). Task 2's own `git grep` acceptance criterion excludes it explicitly.

**Rationale:** Scrubbing an append-only audit field to satisfy a later absence check would violate
the golden's own never-hand-edit convention and destroy the history the field exists to preserve.
The right move is to exclude it from the check, not edit it.
**Source:** 205-03-SUMMARY.md

---

### D-08 — `MSG_ERR_NOT_BLANK` (0xB0) is kept and annotated, not retired with its emit site
The firmware stops emitting it, but the host keeps rendering it, and the catalog annotation states
that divergence explicitly rather than following the plain-orphan shape verbatim.

**Rationale:** 0xB0 is not orphaned on the host — a post-3.1.0 host still *receives* it from
pre-3.1.0 firmware, which is exactly the skew plan 07 put on silicon. Retiring it would make that
refusal render as an unknown id.
**Source:** 205-CONTEXT.md (D-08); 205-06-SUMMARY.md

---

### The negative-address refusal is a table-driven row policy, reusing the existing `-1` channel
`FIELD_POLICY_REJECT_NEGATIVE` (0x40) set on the `key_address` row only, via a new
`FIELD_REJECT_NEGATIVE` macro. No new message id was minted.

**Rationale:** Keeps `json_parser.c`'s existing `FIELD`/`FIELD_MASK` idiom and makes the refusal's
scope visible in `key_parsers[]` rather than buried in a `jsoneq(..., "address")` special case.
`FIELD_MASK`'s own comment already records why no id is minted here: message ids are generated from
the meta repository's catalog, never written in the parser.
**Source:** 205-05-SUMMARY.md (Forks A/B)

---

### D-07 — The version-skew regression is observed on silicon, not argued
Post-205 host + pre-205 firmware, `write -b` against the already-non-blank W27C512, captured
verbatim with exit code and duration, before the only reflash of the session.

**Rationale:** 204's D-08/D-09 precedent is explicit that a claim about what a real user sees gets
observed, not argued — and REL-04 will make exactly that claim. The marginal cost was near zero:
the part was already seated and already non-blank, and the Leonardo is exempt from the
chip-out-before-sideload rule.
**Source:** 205-CONTEXT.md (D-07); 205-07-SUMMARY.md (leg B3)

---

### CR-01 is closed inside Phase 205, not deferred behind an accepted-risk window
The alternative — carrying it the way D-04's skew was carried — was explicitly displaced.

**Rationale:** The two regressions are not the same shape. D-04's is a reversible, flag-gated,
safe-failure-mode version skew the operator controls. CR-01's is a silent, irreversible overwrite
of a non-blank flash region with no operator-visible signal, on 190 of 190 shipped protocol-`0x06`
rows, reachable through an ordinary `-a` with no flag required. A risk window is a reasonable
instrument for the first and not the second — and no later phase's scope covered it, so deferring
meant deferring indefinitely.
**Source:** 205-CR-01-DECISION.md §§ 1–2

---

### D-G2/D-G3 — The withdrawn exemption checks, it does not refuse; and no sector-size model was invented
A non-zero-address protocol-`0x06` write falls back to the ordinary region-scoped blank check.
Any non-zero address withdraws the exemption conservatively.

**Rationale:** Refusing outright would have been a `one-way` user-facing contract change on 190
shipped chip models, load-bearing in operator scripts within one release. Narrowing further to
"inside the erased sector" would require a sector-size field the database does not carry — guessing
in the unsafe direction.
**Source:** 205-CR-01-DECISION.md § 5 (D-G2, D-G3); 205-08-SUMMARY.md

---

## Lessons

### A verify script's fixed-size text window over-captures neighbouring code
Plan 01's literal `<verify>` took a fixed 6000-character window from `def erase(` and swept in
`id`, `vpe` and other unrelated commands that legitimately use the identical
`sys.exit(0 if ok else 1)` idiom — a pattern at 14 sites in that file, none of them `erase`. Run
verbatim it failed against a correct implementation.

**Context:** Bound the window to the next `@cli.command` marker instead of a character count. This
was a defect in the plan's script, not the implementation; no code changed in response.
**Source:** 205-01-SUMMARY.md § Issues Encountered

---

### A plan's declared `<files>` list will be incomplete, and a repo-wide criterion finds what it missed
Three separate instances: plan 03 had to repair `test_eeprom28c_sdp.cpp` and `test_val_5v_page.cpp`
(named by RESEARCH but in neither task's file list); plan 04 had to add `cli_handlers.py` and the
base `FakeChip.write_eprom`, neither declared.

**Context:** In every case the task's own repository-wide absence check or the full suite was what
surfaced the omission. A file list scoped narrower than the acceptance criterion is a latent
blocker, not a tighter scope.
**Source:** 205-03-SUMMARY.md and 205-04-SUMMARY.md § Deviations (Rule 3 blocking)

---

### "Four stale citations" was one real break — verify each individually, never batch-substitute
Of the four cited literals in `test_flash_path_record_sync.py`, only `_META_DOC_REL` actually
resolved to a missing path. It alone caused all 17 red legs.

**Context:** The plan's own task text asked for exactly this ("confirm each of the four
individually… If any one of them is not under `.planning/milestones/`, that is a finding"). A
prefix substitution across the file would have "fixed" three things that were not broken.
**Source:** 205-02-SUMMARY.md § Decisions Made

---

### A test can pass for the wrong reason, and look green while doing it
The seed-link assertions matched the seed's stale link *label* (`../v1.23-FLASH-PATH-DECISION.md`)
via a substring check. The seed's actual href target was already correct. The assertion passed
either way.

**Context:** Both substrings are present in the file, so no run would ever have revealed it. Found
only by reading what the assertion checked against what the file means.
**Source:** 205-02-SUMMARY.md

---

### Writing a retired identifier inside its own annotation breaks offset-based verification
Plan 06's `0x2E` annotation initially wrote `LOG_DEBUG_ID_SUB(DBG_FLAG_SKIP_BLANK)` in prose. That
created an earlier `t.index()` match than the actual `name =` line, so the verify's lookback window
scanned the wrong region.

**Context:** Paraphrase self-references in annotation prose ("a `LOG_DEBUG_ID_SUB` call on this
sub-id") instead of naming the identifier literally.
**Source:** 205-06-SUMMARY.md § Decisions Made

---

### A line wrap in a comment defeats a single-line string match
The same verify also missed its "Not free for reuse." sentence because the sentence had wrapped
across two comment lines. Fixed by keeping it unwrapped.

**Context:** Two instances of the same class of bug in one annotation — string-offset verification
is sensitive to formatting the author does not think of as semantic.
**Source:** 205-06-SUMMARY.md

---

### The base test double needed the new keyword, not just the subclass the plan named
Ten tests across `test_chip_test.py` and `test_dev_test_cmd.py` construct a bare `FakeChip`
directly and all failed with `TypeError: got an unexpected keyword argument`.

**Context:** `chip_test.py`'s dispatch passes the new keyword unconditionally to every operator
double reachable through `run_plan`/`_dispatch_multi_run`. The plan named only the
`WriteInitPreflightChip` subclass that acts on the value; the base class that discards it is
equally on the path.
**Source:** 205-04-SUMMARY.md § Deviations

---

### Removing a firmware backstop can silently strand a host-side assumption nobody wrote down
Plan 03's commit `1cf1b22` deleted the unconditional whole-device `mem_util_blank_check(handle)`
from `flash_nor_unlock_write_init`. That call was what made the host's address-blind erase
exemption safe in practice — it scanned the whole device regardless of what the erase actually
touched. Nothing on the host carried the address-scoping knowledge it implicitly provided.

**Context:** The hazard was not in either side's code in isolation; it lived in the interaction,
and only surfaced at verification. CR-01's regression window opened the moment the backstop left.
**Source:** 205-CR-01-DECISION.md § 4; 205-VERIFICATION.md truth 9

---

### A repo-guidance doc can go stale inside the same phase that wrote it
`firestarter_fw/CLAUDE.md`'s "measured at 320 collected tests" was written by plan 02's commit
`a4e002f2` at 15:26Z. Plan 04's commit at 17:00Z the same day reported 315; the live count at
verification was 316.

**Context:** Surfaced as a verification advisory, not a gap — no must-have truth asserts a
collection count. Still open.
**Source:** 205-VERIFICATION.md § Advisory

---

### A porcelain-asserting test reads as a regression when the tree has uncommitted edits
Three `firestarter_fw/tests/` failures appeared transiently during plan 05's work
(`test_flash_path_record_sync.py`, `test_trace_segment_exhaustiveness_v131.py`) and disappeared on
the post-commit re-run.

**Context:** This is the known "asserts whole-repo porcelain — commit before running it" trap,
confirmed again here. Correctly diagnosed rather than investigated as a regression.
**Source:** 205-05-SUMMARY.md § Issues Encountered

---

### A plan's verify command can name tooling that does not exist on the machine
Plan 05's acceptance-criteria command named `/usr/local/py-utils/bin/python`; only `pytest` exists
at that prefix. `python3` was substituted and the identical assertion logic ran unchanged.

**Context:** A tooling-path correction, not a change to what was being verified — but it blocks the
literal criterion until noticed.
**Source:** 205-05-SUMMARY.md § Decisions Made

---

## Patterns

### Host-gains-before-firmware-loses sequencing
Land the host-side capability in its own plan, verified, *before* the plan that deletes the
firmware's version.

**When to use:** Any cross-repo capability migration where the intermediate commit state is
reachable by a user (a bisect, a partial upgrade). Phase 203 established it for the write guard;
Phase 205 plan 01 applied it to the erase-end blank check.
**Source:** 205-01-SUMMARY.md; 205-CONTEXT.md (D-01)

---

### Run the pre-authored absence leg against the pre-sweep tree, and read *why* it failed
Every new absence leg in plans 03 and 04 was run before its target was deleted, and its failure
text inspected to confirm it failed because it *found* the target — not because a path
mis-resolved or an import broke.

**When to use:** Any test whose assertion is "X is not present." A red run proves nothing until you
have seen it red for the intended reason.
**Source:** 205-03-SUMMARY.md, 205-04-SUMMARY.md (tech-stack patterns)

---

### Capture RED without `git stash` — back up, `git checkout --` restore, run, restore from backup
Used in plans 03 and 04 to observe an absence leg red against a pre-edit tree mid-task.

**When to use:** When you need a transient pre-edit tree in a repo whose state you cannot risk, and
a stash would entangle unrelated working-tree content.
**Source:** 205-03-SUMMARY.md, 205-04-SUMMARY.md § RED Transcripts

---

### Re-derive a golden positionally when entries share a signature
Plan 03's two deleted branch-inventory sites shared an identical `(predicate, keyed_on, tier)`
signature. Old sites were matched to live sites by line-number position — drop the known-removed
entries, zip `old[i]` against `live[i]`, verify 0 mismatches across all 20 pairs — before carrying
`class`/`reason` forward.

**When to use:** Any golden re-derive where a dict keyed on the record's own fields could silently
collapse colliding entries. This golden's history had already hit that collision before.
**Source:** 205-03-SUMMARY.md

---

### Additive keyword-only parameter to re-plumb a retired positional signal
Applied twice: `blank_check_requested` on `write_eprom` (plan 04) and `address` on
`is_erase_exempt`/`requires_blank_check` (plan 08), both keyword-only with a behaviour-preserving
default.

**When to use:** Replacing a wire-level or positional signal with an explicit in-process one, in a
function whose positional call sites are numerous or pinned by tests.
**Source:** 205-04-SUMMARY.md; 205-08-SUMMARY.md

---

### Reserved-gap record by value, never by identifier
See the decision above. The record states the value and the behaviour it selected, the release, the
phase, the counterpart ladder, and the never-reuse mechanism.

**When to use:** Retiring any enumerated wire value (flag bit, ordinal, message id) that a
repository-wide absence gate will police.
**Source:** 205-04-SUMMARY.md

---

### Codegen-inertness proof by regenerate-to-temp-and-diff
Run `codegen.py --language {cpp,python} --target /tmp/...` from the amended catalog and `diff -u`
against each sub-repo's checked-in copy. An empty diff is the proof.

**When to use:** Any comment-only edit to `tools/catalog/messages.toml`, to demonstrate it reaches
no generated artifact and needs no sub-repo sync. Follows the shape commit `694acce3` (phase 204)
established.
**Source:** 205-06-SUMMARY.md

---

### Table-driven row policy for field-scoped wire validation
A policy bit in the field-descriptor table, read by the dispatch loop before the conversion call —
rather than a special case keyed on the field's string name.

**When to use:** Adding validation to one field of a table-driven parser, where the scope of the
rule should be auditable from the table rather than from the loop body.
**Source:** 205-05-SUMMARY.md

---

### Build a pre-phase firmware artifact from a detached worktree, never by checking out the live tree
Plan 07 built the pre-205 `.hex` from a detached worktree at the phase-entry sha, confirmed its
digest against the record, flashed it, and removed the worktree before writing the SUMMARY.

**When to use:** Any bench leg needing an older artifact. It keeps every sha and digest recorded by
sibling plans valid throughout, and leaves no commit from the scratch tree.
**Source:** 205-07-SUMMARY.md

---

### One address, one digest chain, four bench legs
A single non-blank target (`0x000000`, 64 bytes) served the non-blank setup, the pre-205 refusal,
the post-205 acceptance and the erasable-path overwrite — one whole-device digest chain covering
all four instead of a matrix per address.

**When to use:** A bench matrix where several criteria are claims about the same region under
different firmware roles or flags.
**Source:** 205-07-SUMMARY.md

---

### Record a measured figure and a labelled derivation side by side, never blended
`erase -b`'s added wall-clock is recorded as both 10.632 s (measured, N=3) and 2.607 s (derived
from Phase 203's connect-term medians), with the reason they differ stated.

**When to use:** Whenever the measured number legitimately includes cost the derivation
deliberately excludes. Reconciling them would destroy the information in each.
**Source:** 205-07-SUMMARY.md; 205-SESSION-COST.md

---

### Exclude an append-only audit field from a gate by construction, do not scrub it
See the `meta.recorded_by` decision above.

**When to use:** Any absence gate that would otherwise hit a historical record. Write the exclusion
into the gate and say why, in the gate.
**Source:** 205-03-SUMMARY.md

---

### Confirm each cited document's live location individually before rewriting a resolver literal
Never batch-substitute a path prefix across a file — not every citation in the file necessarily
moved.

**When to use:** Repairing stale `.planning/` citations after an archive or a layout change.
**Source:** 205-02-SUMMARY.md (tech-stack patterns)

---

### Prove a new test is not a tautology by reverting only the fix branch
Plan 08's review reverted the `address != 0` branch while keeping the constant and the parameter
in place (so the failure could not be an import error), and confirmed exactly the five
CR-01-relevant tests reddened while the rest stayed green.

**When to use:** After adding tests alongside the fix they cover — especially pre-authored ones.
Keeping the surrounding scaffolding in place during the revert is what distinguishes a real
sensitivity check from a collection failure.
**Source:** 205-REVIEW.md; 205-08-SUMMARY.md § RED Observations

---

## Surprises

### The planned fingerprint re-key was a measured no-op — and RESEARCH's simulated value was wrong
Plan 04's task 3 was to re-key the frozen `dedup_fingerprint` for `uv-slot-write-pass`. Re-derived
against the real post-task-2 tree it came out `927571e5110f` — identical to the value already
committed, and *different* from RESEARCH's simulated `eba362ab0a75`.

**Impact:** No third commit exists for that task. The chosen re-plumb preserves the write step's
outcome byte-for-byte, so no `StepResult` moved. Forcing an edit to satisfy the criterion's letter
would have fabricated a re-key that never happened — and copying RESEARCH's number would have
frozen a wrong value.
**Source:** 205-04-SUMMARY.md (D3, Decisions Made)

---

### One path resolution failure accounted for all 17 red legs
`_META_DOC_REL` resolving to a document that had moved under `milestones/` was the direct cause of
every pre-existing failure in `test_flash_path_record_sync.py` — each raised `MissingScanTargetError`
or depended on a fixture that did.

**Impact:** A one-constant fix took the firmware tree from 17 red to 320/320 green.
**Source:** 205-02-SUMMARY.md

---

### The sweep's flash delta matched the simulated prediction exactly
Plan 03's post-sweep Leonardo build measured 23292 B flash / 1835 B RAM — matching
`205-RESEARCH.md`'s predicted −518 B / −4 B delta exactly. Plan 02's independently-taken phase-entry
figures also matched RESEARCH's control build exactly.

**Impact:** Treated as corroborating evidence that both runs measured the same tree correctly — not
as licence to skip the fresh measurement FWBLANK-05 required. Both plans re-measured anyway, with
their own digests.
**Source:** 205-02-SUMMARY.md; 205-03-SUMMARY.md

---

### `erase -b`'s measured cost is roughly four times the connect-term derivation
10.632 s measured (Leonardo-class, N=3) against 2.607 s derived. The gap is the second port open's
own whole-device read traffic — 7.40 s for this 64 KiB part.

**Impact:** Phase 206's SESS-01 inherits both figures and an explicit statement of which to use for
which reasoning. A single blended number would have been wrong for both purposes.
**Source:** 205-07-SUMMARY.md; 205-SESSION-COST.md

---

### Verification found a real, silent data-integrity hazard created by the phase's own removal
CR-01: `is_erase_exempt` was address-blind, so a `write -a <non-zero>` on protocol `0x06` was
exempted from any blank check even though the firmware only erases the whole chip at address 0.
Reachable on 190 of 190 shipped protocol-`0x06` rows with no flag required.

**Impact:** Dropped the first verification to 8/9 and forced an eighth, unplanned plan. The phase's
own removal of the firmware backstop is what opened the window.
**Source:** 205-VERIFICATION.md (`re_verification.gaps_closed`); 205-CR-01-DECISION.md

---

### Ten unrelated tests broke on a class the plan never mentioned
Adding the keyword to `WriteInitPreflightChip` was not enough — `chip_test.py` passes it
unconditionally to every operator double, and ten tests construct the bare `FakeChip`.

**Impact:** Caught by the full-suite run, not by the targeted legs. Base-class signature
compatibility was invisible from the plan's file list.
**Source:** 205-04-SUMMARY.md § Deviations

---

### The negative-address fix cost exactly +22 B flash and +0 B RAM, identical on all three targets
Reproduced three times with byte-identical output across `uno`, `uno328pb` and `leonardo`.

**Impact:** Made the phase's three-way delta table (sweep reclaim −518 B / fix cost +22 B / net
−496 B) clean and per-target uniform, with the arithmetic check holding on every target.
**Source:** 205-05-SUMMARY.md; 205-06-SUMMARY.md

---

### The chip-ID probe still disagrees with the database, and stayed open
The firmware's own probe read `0x1818` against the expected `0xda08` for the seated W27C512 —
the same `WINDOWS.md` entry 3 finding Phase 204 recorded.

**Impact:** The operator's own statement that the part *is* a W27C512 was recorded as independent
evidence about the physical part, deliberately **not** as a resolution of the firmware-side
mismatch. Both statements stand; neither overwrites the other. `-f/--force` was required on every
bench command as a result.
**Source:** 205-07-SUMMARY.md § Issues Encountered

---

### A gap in the bench evidence was stated plainly rather than inferred away
No whole-device read was taken between B3 (the last chip-content-affecting event on pre-205
firmware) and B4 (the reflash). Chip content is not expected to be affected by an AVR program-memory
flash, but the record does not assert survival by inference.

**Impact:** Criterion 3's proof is unweakened — B5's read-back and digest are self-sufficient
regardless. Recorded in the B4 section rather than glossed.
**Source:** 205-07-SUMMARY.md § Issues Encountered

---

### An untracked, unrelated PDF made a literal `git status --porcelain` emptiness check unsatisfiable
`datasheets/LST62832I.pdf`, present in the `firestarter_app` submodule three days before plan 08
began, makes the meta repo report the submodule as modified ("untracked content") even after clean
commits and a correct gitlink advance.

**Impact:** Only the literal emptiness check was affected; every substantive part of task 3's verify
passed. The file was neither committed nor deleted — correctly treated as out of scope.
**Source:** 205-08-SUMMARY.md § Deviations

---

### Plan durations spread over an order of magnitude
~9 min (plan 06) and ~16 min (plan 02) against ~95 min (plan 03) and ~130 min (plan 04). Token
actuals ranged from 4,200 (plan 05) to 62,000 (plan 03).

**Impact:** The cost sat almost entirely in the two sweep plans with cross-repo citation fallout and
golden re-derives, not in the measurement, bench or documentation plans. Worth weighing when
estimating a future removal phase — the deletion is cheap; the citations it strands are not.
**Source:** 205-02 through 205-08 SUMMARY frontmatter (`duration`, `actuals.tokens`)

---

_Extracted: 2026-09-23_
