# Phase 121: `dev test` FIX + GATES + DOCS + REDESIGN - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-29
**Phase:** 121-`dev test` FIX + GATES + DOCS + REDESIGN
**Areas discussed:** Who gets asked and who just gets written; How literal is "no flags";
Partial-write representation + evidence weight; Dedup mechanism for always-ask; DEVTEST-01's
mechanism; GATE-01's AST gate scope; GATE-02's edges; GATE-03 vs the pre-existing RED golden
*(all 8 offered areas selected)*

---

## Who gets asked, and who just gets written — DEVTEST-03 / DEVTEST-04

### Q1: What does "destructive is UV-only" actually govern?

| Option | Description | Selected |
|--------|-------------|----------|
| Ask only on UV; non-UV writes fully, unprompted | The gate exists because a UV write is irrecoverable without a lamp; EEPROM/Flash/SRAM writes are recoverable so they run the full round-trip. Matches `dev-test-design-decisions.md`'s family table. | ✓ |
| Ask always; UV-only governs the warning wording | Every writable part stops and asks; UV-only scopes the chip-sacrificing language and window placement. | |
| Non-UV is never written at all | Literal reading of "non-UV parts are never treated as destructive-capable". | |

**User's choice:** Ask only on UV; non-UV writes fully, unprompted.
**Notes:** The rejected literal reading was flagged as self-defeating — it would leave this
milestone's own AT28C family unable to produce any write evidence for Phase 122's community ask.

### Q2: How does the execution layer know a part is UV-erasable?

| Option | Description | Selected |
|--------|-------------|----------|
| Decide once in `derive_plan`, carry it on the `Plan` | `derive_plan` has the `full` DB dict → exact 301/301; execution layer reads, never re-derives. Closes PATT-03's 269-part miss as a side effect. | ✓ |
| Widen the execution-time algorithm set to `{0x07, 0x08, 0x0B}` | Covers 301/301 but over-includes 28 non-UV EEPROMs and forfeits the `0x0B ⟹ UV` exclusivity property. | |
| Thread the raw `electrical-type` string into the execution path | Exact, but a type-string key at the execution layer is what DEVTEST-03 rules out. | |

**Notes:** A fourth option — adding `electrical-type`/`is_uv` to `convert_to_programmer` — was
ruled out mid-discussion on a verified constraint: `_setup_operation` does
`command_dict = eprom_data_dict.copy()` (`eprom_operations.py:333`), so the programmer dict **is**
the wire payload, and that would re-add a type field v1.20 removed as breaking. Also noted: this
choice became safety-critical rather than cosmetic once Q1 was locked.

### Q3: Off-TTY, a UV part — no prompt possible, no consent flag

| Option | Description | Selected |
|--------|-------------|----------|
| Run the sweep, mark write/verify SKIPPED with a named reason | Phase 120 D-06's "nothing could stand in as consent" logic; read-only steps still yield evidence. | |
| Default to "no" — write the 256B window off-TTY | Treats an absent TTY as a declined prompt; still yields write evidence. | ✓ |
| Refuse the whole command off-TTY | Simplest contract; blocks scripted evidence collection entirely. | |

**Notes:** The cost was stated in the option itself — *"wrote to silicon with no consent given"* —
and chosen anyway. Recorded in CONTEXT.md as an owned trade-off, not an oversight.

### Q4: Composed consequence — `dev test` now always writes

| Option | Description | Selected |
|--------|-------------|----------|
| Confirm — always writes; say so loudly | Help text, first output line, `community-validation.md`, both READMEs and Phase 122's ask all state it. No flag added. | ✓ |
| Keep a read-only path — accept one flag for it | Preserves a safe first-contact sweep at the cost of partially walking back DEVTEST-02. | |
| Keep a read-only path with no flag — a three-way ask | Reintroduces the prompt on non-UV parts that Q1 removed. | |

**Notes:** Raised proactively because Q1 + Q3 compose into a contract change (v1.21's
"non-destructive by default" premise is gone) that neither answer states on its own.

---

## How literal is "no flags" — DEVTEST-02

| Option | Description | Selected |
|--------|-------------|----------|
| Zero options — all four go | `--destructive`, `-y/--yes`, `--submit`, `--output-dir` all removed; `FIRESTARTER_CONFIG_DIR` already redirects the report. | ✓ |
| Keep `--output-dir`; drop the other three | Reads criterion 6's em-dash as operative — only the consent surface goes. | |
| Keep `--output-dir` and `--submit` | `--submit` survives as a non-interactive "yes, file it". | |

**User's choice:** Zero options.
**Notes:** Ripple measured after the answer: 82 references across 6 test files, plus
`tools/check_devtest_orchestrator.py`, which pins `dev_test` by name with a helper allow-list and
fails closed on a zero-match scan.

---

## Partial-write representation + evidence weight — DEVTEST-04

### Q1: How is full vs 256B-region represented?

| Option | Description | Selected |
|--------|-------------|----------|
| Six strings stay; scope as a first-class field on Step/StepResult | Closed vocabulary untouched; new field additive. | |
| Add a 7th op string `OP_WRITE_PARTIAL` | Visible in the op name; `dedup_fingerprint` differentiates automatically. Opens the closed vocabulary. | ✓ |
| Six strings stay; scope only in the `reason` text | Cheapest, but `reason` is excluded from `dedup_fingerprint` and unstructured. | |

**Notes:** Two ROADMAP-framing corrections surfaced while checking the ripple — `parse_devtest_issue.py`
has **no** op vocabulary at all (title marker + `schema_version` presence + fingerprint grouping
only), and `build_db_diff`'s ladder logic keys only on verdicts. Both shrink the work materially.

### Q2: Does verify get a partner string?

| Option | Description | Selected |
|--------|-------------|----------|
| No — `verify` stays one string | Its region is definitionally the write's region; a partner encodes zero new information. | ✓ |
| Yes — add `verify-partial` for symmetry | Every row self-describing when read alone. | |

### Q3: Can a partial run reach `ladder_state = community-reported`?

| Option | Description | Selected |
|--------|-------------|----------|
| No — a partial run cannot reach it | Weaker evidence; consistent with Phase 114's GRAD-01 posture. | |
| Yes — all-OK is all-OK regardless of coverage | Ladder logic unchanged; coverage judgement stays with the human maintainer. | ✓ |
| Yes, but as a distinct third tag | Signal preserved and visibly weaker; opens GRAD-01's vocabulary. | |

**Notes:** The honesty concern raised against this option turned out smaller than stated:
`count_agreeing` groups by `dedup_fingerprint` and the new op string changes that hash, so a partial
run can never cross-agree with a full run toward N≥2. GRAD-01's lock holds through the fingerprint
rather than through the tag — recorded in CONTEXT.md as the reason this is safe.

---

## Dedup mechanism for always-ask — DEVTEST-05 / DEVTEST-06

### Q1: How is the user's own prior report discovered?

| Option | Description | Selected |
|--------|-------------|----------|
| `gh` query on the fingerprint, authored by `@me` | Identity = the authenticated gh account; read-only and permission-independent; works across machines. | ✓ |
| Local fingerprint ledger in the config dir | Works offline; "same user" degrades to same machine, and carries a browser-tier false-positive trap. | |
| Both — gh when available, ledger as fallback and receipt | Best coverage; two sources to reconcile. | |

### Q2: When the `gh` dedup query cannot run?

| Option | Description | Selected |
|--------|-------------|----------|
| Ask anyway; state plainly the check could not run | Preserves "every run asks"; fail-open is safe because duplicates group by fingerprint on arrival. | ✓ |
| Ask anyway, but default the prompt to "no" | Biased against filing when duplication is unknown. | |
| Skip the filing ask when gh is unavailable | Contradicts DEVTEST-05 and removes the browser filing route. | |

### Q3: When the query DOES find an identical prior report?

| Option | Description | Selected |
|--------|-------------|----------|
| Name the issue and file nothing | Requirement-literal reading of "only when it differs". | |
| Name it and offer to add a comment with this run's evidence | The fingerprint excludes measured VPP/VPE, error codes and reason, so a second run can carry genuinely new detail. `gh issue comment` needs no write access. | ✓ |
| Name it and still offer to file a new issue anyway | Tester override; contradicts DEVTEST-05. | |

**Notes:** The comment path is a widening of DEVTEST-05's literal text; recorded as
operator-approved and read-at-intent, following Phase 120 D-04's precedent. Negative-argv discipline
extends to `gh issue comment`.

---

## DEVTEST-01: local NA arm vs fixing the FLAG_CAN_ERASE lie

### Q1: How does `OP_ERASE` become `NA` for `0x0D`?

| Option | Description | Selected |
|--------|-------------|----------|
| Scoped NA arm + a separate host-side flag-surface honesty fix | Two changes, no wire byte touched, no pinned test flipped, `database.py` D-03 untouched. | |
| Fix the root cause — clear `FLAG_CAN_ERASE` for `0x0D` | One fix closes everything downstream; reverses `database.py:591`'s "must stay unchanged" and flips two deliberately-pinned tests. | ✓ |
| Scoped NA arm only — leave the flag surface to GATE-02's docs | Smallest diff; leaves Phase 120's deferred item open. | |

**Notes:** Blast radius was verified live *before* the question was asked and again after:
`chip_database.json` has no `flags` key so `diff_db.py` identity is unaffected; no firmware native
test or validation-matrix family pins `eeprom28c` wire flags; `serial_comm.py:549` is DEBUG-only
logging. Exactly two host tests must be inverted.

### Q2: `--skip-erase` / `-b` still accepted-but-inert on `0x0D`?

| Option | Description | Selected |
|--------|-------------|----------|
| Warn host-side: "this family has no erase to skip" | Mirrors HOST-02 D-18 exactly; closes Phase 120's deferred item. | ✓ |
| Refuse the flag on `0x0D` | Fails a write that would have succeeded — the trade HOST-02 D-18 rejected. | |
| Documentation only — GATE-02 records it as a known wart | Smallest diff; leaves the item open. | |

---

## What GATE-01's AST gate actually asserts

| Option | Description | Selected |
|--------|-------------|----------|
| Both classes in one checker, fixture per class | Follows `check_devtest_orchestrator.py`'s three-class shape: deny permit-by-default returns AND a widenable allow-set, plus the fail-closed zero-match guard. | ✓ |
| Fail-closed-by-construction only | Guards silicon; a comprehension-built allow-set would pass. | |
| Immutable-literal allow-set only | Guards the derived 43/41 partition; a new permitting return path would pass. | |

**Notes:** Established during scouting that `tests/test_sdp_capability.py` already ships 12 legs
including an AST import-purity leg — GATE-01 adds to it rather than replacing it, and no
`tools/check_*.py` gate or planted fixture exists yet.

---

## GATE-02's edges: firmware catalog + an untracked doc

### Q1: `doc/lockable-proms.md` is untracked — ship it?

| Option | Description | Selected |
|--------|-------------|----------|
| Don't ship it — relocate to `.planning/notes/` and correct it there | Matches this project's convention for research artifacts; nothing unverified reaches users. | |
| Commit it with an explicit provenance/uncertainty header | Honors GATE-02's text while scoping every claim as datasheet-derived. | |
| Commit it as-is with §17 fixed, no provenance header | Simplest reading of GATE-02. | ✓ |

**Notes:** The concern was stated in the option text — ~300 datasheet-compiled rows shipping as an
authoritative reference with no evidentiary basis, in the milestone whose validation ceiling forbids
claims about SDP behaviour on real silicon — and the choice was made with that cost visible.
Recorded in CONTEXT.md as an owned trade-off so no downstream agent re-opens it.

### Q2: `MSG_INFO_SDP_UNLOCK_DONE_US` (`0x5F`) honesty caveat — here or Phase 122?

| Option | Description | Selected |
|--------|-------------|----------|
| Fix it here — edit `messages.toml`, regenerate both mirrors | Rides the nine-row sweep this phase runs anyway; Phase 122 is the worst phase to land codegen in. | ✓ |
| Leave it to Phase 122's catalog work | Keeps this phase's firmware footprint docs-only. | |
| Don't fix it — Phase 120 D-10's host line already covers the gap | Zero firmware change; raw firmware log stays asymmetric. | |

### Q3: GATE-02's named doc list

Not a separate ask — derived from the Q4 lock in area 1. `doc/community-validation.md` and
`doc/beta-testing-install.md` join the named list (the latter's line 179 currently tells beta testers
to run a now-always-writing command). Recorded as a correction; `REQUIREMENTS.md` not edited.

---

## GATE-03 vs the pre-existing RED golden

### Q1: How does "host pytest green" reconcile with the RED golden?

| Option | Description | Selected |
|--------|-------------|----------|
| Regen the stale golden FIRST, as its own commit | Proves GREEN with zero DEVTEST code in the tree; makes masking structurally impossible. | ✓ |
| Regen once at the end, together with this phase's changes | One commit; pre-existing drift and this phase's delta become indistinguishable. | |
| Don't regen — scope GATE-03 with a named exception | Hides a real expected change, not just stale drift; debt rolls into the close. | |

**Notes:** RED state measured live before asking: 186034 produced vs 184631 golden bytes, first
divergence at index 1178.

### Q2: `test_no_programmer_found_*` go RED with a board attached

| Option | Description | Selected |
|--------|-------------|----------|
| Prove GREEN with no board attached; record the artifact | No test edits; "green" means green. | |
| Fix the tests so they pass with a board attached | Permanent, bench-independent CI. | ✓ |

**Notes:** Flagged in the option text as scope the roadmap did not authorise, and chosen anyway.
Recorded in CONTEXT.md as an operator-authorised scope addition, following Phase 119's precedent for
its cross-family regression sweep.

---

## Claude's Discretion

Confirmed as Claude's call at the closing check, with constraints named in CONTEXT.md:

- Every user-facing string (the UV ask, the inert-flag warning, the always-writes notice, the
  duplicate-found and could-not-check lines) — subject to two constraints: the always-writes notice
  is unconditional and first, and the `NA` erase reason names the family fact, never the flag
  mechanism.
- Bump the report's `schema_version` — safe because `parse_devtest_issue.py` accepts it by presence
  only.
- Keep `dev test`'s `0/1/2` exit-code tri-state unchanged — `write-partial` adds no new verdict.
- How the UV decision is carried (`Plan` field, `Step` field, or both).
- Where the two planted fixtures live and how the checker is pointed at them.
- Whether b11 back-compat is a tolerant parser or an explicit legacy-vocabulary constant.
- Plan ordering, subject to four hard constraints listed in CONTEXT.md.

## Deferred Ideas

- `dev test`'s release-channel disposition (999.15 / gh#8) — stable keeps only `dev read` and
  `dev test`, and this phase makes `dev test` always write. Surfaced here, not answered here.
- A read-only `dev test` mode — declined because it costs a flag DEVTEST-02 removes.
- Hardening or removing `derive_plan`'s now-vestigial `locked_destructive`.
- The wider CLI flag re-design (`-f` splitting, `-b` polarity, a project-wide `-y`).
- The end-to-end `infoic.xml` `page_size` decode phase — still not inserted into ROADMAP.md.
- Widening `_probe_port`'s version capture; the third trace strobe kind; SDP-F7 / SDP-F8;
  the Unity-teardown SIGABRT; `prove-pio-dev-flag-fails-closed` items 1-3.
- Reviewed todos not folded: `decode-infoic-flags-bits-14-15-protect-metadata.md` (needs a DB
  regeneration that GATE-03 and CLOSE-01 forbid this milestone) and
  `fold-response-code-into-log-macro.md` (declined at 118, 119, 120 and again here). Eleven further
  `todo.match-phase` hits were generic keyword overlap only.
