# Phase 121: `dev test` FIX + GATES + DOCS + REDESIGN - Context

**Gathered:** 2026-07-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Make community-facing evidence about this milestone trustworthy **before** Phase 122 ever asks for
it — and land the operator's `dev test` redesign at the same time.

**In scope (DEVTEST-01..06, GATE-01..03):**
- `OP_ERASE` marked `NA` for protocol `0x0D` with a named reason — DEVTEST-01's **host** half only
  (the firmware half landed early in Phase 119 as a generic op-layer NULL-`main` refusal, D-06/D-07/D-08).
- `dev test` takes **no options at all** (DEVTEST-02).
- Destructiveness scoped to UV-erasable EPROMs on an explicit structural axis (DEVTEST-03).
- A stop-and-ask on UV parts: yes → full device, no → 256 B region — a **third mode needing a new
  representation** (DEVTEST-04).
- **Every** run asks whether to file an issue, dedup-checked against the user's own prior report
  first (DEVTEST-05).
- `gh`-first submission wherever it can replace the browser/URL path, with the **negative** argv
  asserted for `--label` (DEVTEST-06).
- An AST capability gate over `sdp_capability.py` with a planted-violation pytest per violation
  class (GATE-01).
- Docs corrected where they describe behaviour that does not reach silicon (GATE-02).
- The full nine-row non-regression set green (GATE-03).

**Newly pulled in by decisions below (each recorded, none a scope leak):**
- The root-cause `FLAG_CAN_ERASE` fix for `0x0D` in `database.py` (decision 12), which **reverses**
  `database.py:591`'s explicit *"must stay unchanged"* note. Third reversal in this phase.
- The `--skip-erase` / `-b` host-side warn on `0x0D` (decision 13), closing Phase 120's deferred
  flag-surface honesty item so GATE-02 documents a fixed state rather than a wart.
- `tools/catalog/messages.toml`'s `0x5F` honesty caveat plus both regenerated mirrors (decision 15).
  So this phase **does** touch firmware source, not only firmware docs.
- Hardening the no-programmer-found characterization tests so they pass with a board attached
  (decision 19). Flagged as outside the nine requirements and chosen anyway: **operator-authorised
  scope addition**, recorded the way Phase 119 recorded its cross-family sweep, not a leak.
- GATE-02's named doc list widened to `doc/community-validation.md` and
  `doc/beta-testing-install.md` (decision 17). `REQUIREMENTS.md` is **not** edited.

**Explicitly NOT in scope:**
- Any `chip_database.json` change, any `support_status` change, any `PROTOCOL-LEDGER` entry, any
  `build_db.py` change. `diff_db.py` identity must still hold — **verified reachable**: D-11 changes
  a *runtime* transform, and `chip_database.json` carries no `flags` key at all.
- Re-opening the SDP-capability partition itself (43 ALLOW / 41 REFUSE, derived from `infoic.xml`
  `INFOIC2PLUS` `flags` bit 15 at `a8efaedc`). GATE-01 **guards** it; it does not revisit it.
- Phase 122's closeout comments, the honesty ledger, the `beta`-push decision, the version bump.
- The wider CLI flag re-design, `dev test`'s release-channel disposition, and the `page_size`
  decode phase — see `<deferred>`.

**Validation ceiling applies, unchanged.** No AT28C part is on the bench. `0x0D` stays
`UNVERIFIED`, **zero** chips change `support_status`, the **84**-chip count is unchanged. This phase
adds no bench work. See `.planning/REQUIREMENTS.md` §"Validation Ceiling" for the exact permitted
and forbidden claims.

</domain>

<decisions>
## Implementation Decisions

### Who gets asked, and who just gets written — DEVTEST-03 / DEVTEST-04

- **D-01: The stop-and-ask is UV-only; every other family is written in full, unprompted.**
  "Destructive is UV-only" governs **who gets the gate**, not the warning wording and not who may be
  written at all. The gate exists because a UV write is irrecoverable without a lamp; EEPROM/Flash
  writes are recoverable via erase and SRAM/FRAM writes are essentially free, so those run the full
  `write → verify → erase` round-trip with no prompt. This is exactly
  `.planning/notes/dev-test-design-decisions.md`'s own per-family table. Own the consequence:
  `dev test at28c256` — this milestone's own family — writes the whole part with no prompt.
  Rejected: asking on every writable part (turns the UV-only clause into mere wording and costs a
  prompt where the write is free). Rejected: the literal reading in which non-UV parts are never
  written — it would leave the AT28C family unable to produce any write evidence for Phase 122's
  community ask, defeating the phase's own purpose.

- **D-02: UV-ness is decided once in `derive_plan` and carried on the `Plan`/`Step`.**
  `derive_plan` already reads the `full` DB dict, so `electrical-type == "UV-EPROM"` is exact there
  — **301/301**. It records the gate decision and the write scope on the plan; `run_plan` and
  `_write_region_for` **read** that decision and never re-derive UV-ness. This closes the
  pre-existing PATT-03 defect as a side effect (today's execution-time `algorithm == 0x0B` signal
  matches **32 of 301** UV parts, so 269 UV parts silently fall through to the `[0, 256)` window).
  Now safety-critical rather than cosmetic: under D-01 a UV part misread as non-UV receives an
  **unprompted full-device write**. Rejected: widening the execution-time set to
  `{0x07, 0x08, 0x0B}` — it does cover 301/301 and its over-inclusion of 28 non-UV EEPROMs is
  conservative-safe under D-01, but it forfeits the `0x0B ⟹ UV` exclusivity property and costs
  those 28 parts their full round-trip evidence. **Rejected on a hard constraint:** putting
  `electrical-type`/`is_uv` into `convert_to_programmer` — `_setup_operation` does
  `command_dict = eprom_data_dict.copy()` (`eprom_operations.py:333`), so the programmer dict **is**
  the wire payload verbatim, and that would re-add a type field v1.20 removed as a breaking change.
  Rejected: threading the raw `electrical-type` string as a separate argument — a type-string key at
  the execution layer is the thing DEVTEST-03 rules out, and it opens a second dict to keep in sync.

- **D-03: Off-TTY defaults to "no" — the 256 B window is written.**
  An absent TTY is treated as a declined prompt rather than absent consent, so a piped or CI run
  still yields write evidence. Operator decision after the alternative was put explicitly: this
  **writes to silicon in a context where nobody consented**, and today's off-TTY default writes
  nothing. That consequence is owned, not incidental. Rejected: marking write/verify `SKIPPED` with
  a spoken reason (Phase 120 D-06's *"nothing could stand in as consent"* logic). Rejected:
  refusing the whole command off-TTY — it would also block the read-only steps that are safe in any
  context.

- **D-04: `dev test` always writes, and the docs must say so loudly.**
  Composing D-01 and D-03: UV parts always get at least 256 B, non-UV parts always get a full-device
  write. v1.21's *"non-destructive by default"* premise (SAFE-01 / Phase 109 D-01) is **gone
  entirely** and no read-only mode survives. Therefore the command's help text, the **first line of
  its output**, `doc/community-validation.md`, `doc/beta-testing-install.md` and both READMEs must
  state plainly that `dev test` writes to the chip and expects a blank/scratch part — and Phase 122's
  community ask must carry the same warning. Rejected: preserving a read-only path via one
  `--read-only` flag (would partially walk back DEVTEST-02). Rejected: a three-way full/partial/none
  ask (reintroduces the prompt on non-UV parts that D-01 removed).

### The flag surface — DEVTEST-02

- **D-05: All four current options are removed; `dev test <chip>` takes zero options.**
  `--destructive` and `-y/--yes` are dead by construction (the D-01 ask replaced the first, and D-03
  removed anything for the second to bypass); `--submit` is dead because DEVTEST-05 makes asking
  unconditional; `--output-dir` goes too, because the report is **always** written to
  `<config dir>/reports` and `FIRESTARTER_CONFIG_DIR` already redirects it — the flag is redundant,
  not load-bearing. Ripple to own as task work: **82 references across 6 test files**
  (`test_dev_test_cmd.py`, `test_matrix_artifact.py`, `test_validate_family_cmd.py`,
  `test_dev_sdp_cmd.py`, `test_validate_oracle.py`, `test_check_devtest_orchestrator.py`), plus
  `tools/check_devtest_orchestrator.py`, which pins `dev_test` by name with a helper allow-list and
  **fails closed when its scoped scan matches zero functions**. Rejected: keeping `--output-dir` as
  a non-consent path override. Rejected: keeping `--submit` as a non-interactive "yes, file it" — it
  re-creates the off-TTY silent-submission path v1.21 SUB-01 forbade.

### The partial-write representation — DEVTEST-04

- **D-06: A seventh op string `OP_WRITE_PARTIAL` joins the vocabulary.**
  The distinction is visible in the op name itself, so every consumer sees it without learning a new
  field, and `dedup_fingerprint` differentiates a partial run from a full one **automatically**
  (`diagnostic_report.py:174-203` hashes `f"{op}={verdict}:{classification}"`). Owned task work: the
  `chip_test.py` frozensets `_DESTRUCTIVE_OPS` and `_MULTI_RUN_OPS`, `diagnostic_report.py`'s
  renderer and `to_dict`, the `tests/test_audit_coverage_matrix.py` golden, and **back-compat for
  `3.0.0b11` reports already in the wild**, which carry only the old six strings. Rejected: keeping
  six strings and adding a `scope` field. Rejected: encoding scope only in the free-text `reason` —
  `reason` is deliberately excluded from `dedup_fingerprint` and is unstructured, so scope would be
  invisible to every machine consumer.
  **Correction to the ROADMAP's own framing, recorded not acted on:**
  `tools/parse_devtest_issue.py` has **no op vocabulary at all** — it keys on the `[dev test]` title
  marker, `schema_version` by **presence only**, and `dedup_fingerprint` grouping, and never reads
  step ops or verdicts. The ROADMAP's *"closed six-string set consumed by the issue parser"* is
  wrong; the real consumers are the two `chip_test.py` frozensets, the renderer, and the golden.
  This is the same class as HOST-04's narrower-than-intent mechanism and LOCK-06's superseded
  figure. Do **not** edit `REQUIREMENTS.md`.

- **D-07: `verify` stays a single string.**
  A verify's region is definitionally the preceding write's region — it never has independent scope
  — so a `verify-partial` partner would encode zero new information. The vocabulary stops at seven.
  Rejected: adding it for row-level self-description.

- **D-08: A partial run still auto-tags `ladder_state = community-reported`.**
  All-OK is all-OK regardless of coverage; coverage judgement stays with the human maintainer who
  reads the report. **Verified free:** `build_db_diff` keys **only** on the verdict set
  (`diagnostic_report.py:266-278`) and never on op names, so the new string needs no ladder change
  at all. **The mitigation that makes this safe, and it must be stated in the phase artifacts:**
  `count_agreeing` groups saved bodies by `dedup_fingerprint`, and D-06 changes that hash, so a
  partial run can **never** cross-agree with a full run toward the N≥2 promotion rule. Phase 114's
  GRAD-01 no-auto-graduate lock therefore still holds end to end. Rejected: refusing the tag on a
  partial run. Rejected: a distinct `community-reported-partial` tag (opens GRAD-01's ladder
  vocabulary for a distinction the fingerprint already carries).

### Always-ask filing and dedup — DEVTEST-05 / DEVTEST-06

- **D-09: Dedup is a `gh` query on the fingerprint, authored by `@me`.**
  `gh issue list --repo henols/firestarter_prom --author @me --search <shorthash> --state all`.
  "Same user" is exactly the authenticated `gh` account, so the check works across machines and
  survives a reinstall; the query is read-only and permission-independent, consistent with
  DEVTEST-06's negative-argv discipline. **No local ledger.** Rejected: a config-dir fingerprint
  ledger — "same user" degrades to "same machine + config dir", it is blind to reports filed
  elsewhere or since deleted, and it carries a real trap: on the browser tier **nothing is filed
  until the tester presses Submit**, so a ledger entry written at URL-open time would suppress a
  legitimate later filing. Rejected: both sources (two truths to reconcile for no coverage the `gh`
  query lacks).

- **D-10: When the query cannot run, ask anyway and say so plainly.**
  `gh` absent, unauthenticated, offline, or a non-zero exit → the filing ask still happens (DEVTEST-05's
  *"every run asks"* is preserved) with an explicit line stating the duplicate check could not run.
  Fail-open on filing is acceptable **because** `count_agreeing` groups duplicates by fingerprint on
  arrival, so a duplicate lands visibly grouped rather than as noise the maintainer must detect.
  Rejected: defaulting the prompt to "no" (nudges a first-time tester away from the very report the
  milestone is asking for). Rejected: skipping the ask entirely without `gh` — contradicts
  DEVTEST-05 and removes the community's easiest filing route.

- **D-11: On a duplicate, name the issue and offer to comment this run's evidence.**
  `dedup_fingerprint` deliberately excludes measured `vpp_*`/`vpe_*`, `error_code` and `reason`, so a
  second run at an identical fingerprint **can** carry genuinely new diagnostic detail — which is
  exactly the evidence class that cracked this project's past RCAs. `gh issue comment` on a public
  repo needs only an authenticated account, never write access, so the tier stays
  permission-independent. Recorded as an **operator-approved widening** of DEVTEST-05's literal text
  (*"creating a new issue only when it differs"*), following Phase 120 D-04's read-at-intent
  precedent — not a scope leak. The negative-argv discipline extends to `gh issue comment`: assert
  no triage/write-gated argument is ever sent, using `tests/test_submit.py:301-320`'s idiom.
  Rejected: naming the issue and filing nothing. Rejected: offering a new issue anyway — directly
  contradicts DEVTEST-05.

### DEVTEST-01's host half and the erase-capability lie

- **D-12: `FLAG_CAN_ERASE` is cleared for algorithm `0x0D` in `convert_to_programmer`.**
  The root-cause fix, not a `derive_plan`-local arm: with the bit clear, `derive_plan`'s existing
  generic branch produces the `NA` erase step for free and every downstream advertisement corrects
  itself. This **reverses** `database.py:591`'s explicit *"leaving it set on 0x0D is firmware-inert
  and must stay unchanged"* note — the **third** recorded reversal in this phase, and it must be
  written up as one. **Blast radius verified live, all four facts:** `diff_db.py` identity is
  **unaffected** (`chip_database.json` carries no `flags` key; the bit is computed at runtime); **no**
  firmware native test and **no** `tools/validation_matrix_spec.json` family pins the incoming wire
  flags for `eeprom28c`; `serial_comm.py:549`'s read is **DEBUG-only logging**; and exactly two
  deliberately-pinned host tests must be inverted with the reversal recorded in-test —
  `tests/test_database_conversion.py:99-104` (*"AT28C256 … carries FLAG_CAN_ERASE — the flag is
  firmware-inert"*) and `tests/test_eprom_operations.py:1132` (*"input is 2 (FLAG_CAN_ERASE), NOT
  0"*). `tests/test_val_wire_5v_page.py:142`'s `0x07` pin is unaffected. Rejected: a scoped
  `0x0D` arm in `derive_plan` plus a separate flag-surface fix. Rejected: the scoped arm alone.

- **D-13: `--skip-erase` and `-b` on a `0x0D` chip warn and proceed.**
  One line stating this family has no erase to skip, then the write runs normally — the exact shape
  of HOST-02's D-18 (`--skip-sdp-unlock` on a non-`0x0D` chip). Clearing the wire bit under D-12
  does **not** stop `--skip-erase` being accepted and inert, so this is the residual half of Phase
  120's deferred flag-surface honesty item; with it, GATE-02 documents a **fixed** state rather than
  a wart. Rejected: refusing the flag — it fails a write that would have succeeded to prevent a
  no-op with no silicon risk, the trade HOST-02 D-18 already rejected. Rejected: documentation only.

### GATE-01 — the capability gate

- **D-14: One AST checker denies two violation classes, with a planted fixture per class.**
  Follows `tools/check_devtest_orchestrator.py`'s in-tree shape (three classes in one gate, with a
  fail-closed *"scoped scan matched zero symbols"* guard). **Class 1 — permit-by-default:** any
  `return (True, …)` not lexically dominated by a membership test against `SDP_CAPABLE_TOKENS`, plus
  a bare `except:` around the predicate. **Class 2 — a widenable allow-set:** `SDP_CAPABLE_TOKENS`
  assigned other than exactly once from a `frozenset` of string **literals** (no comprehension, no
  call, no name reference), or mutated/rebound via `|=` / `.union` / `.add` anywhere in the
  `firestarter` package. Class 2 is what protects the derived 43/41 partition from drifting back
  into inference; Class 1 is what protects silicon. The existing AST import-purity leg at
  `tests/test_sdp_capability.py:640` stays and is not duplicated. Rejected: either class alone.

### GATE-02 — the docs

- **D-15: `tools/catalog/messages.toml`'s `0x5F` caveat is fixed here, with both mirrors regenerated.**
  `MSG_INFO_SDP_UNLOCK_DONE_US` gains the *"protection state is not readable"* caveat `0x61` already
  carries, making the two directions symmetric. Edit **only** `messages.toml`, then regenerate
  `firestarter/include/messages.h` and `firestarter_app/firestarter/messages.py` — **never**
  hand-normalise the raw codegen output. Cheapest here because this phase already runs the nine-row
  non-regression sweep; catalog-sync CI is red-until-merge by design (the Phase 118 pattern).
  Consequence to own: this phase's firmware footprint is **not** docs-only. Rejected: deferring to
  Phase 122, the honesty-ledger close and the phase least able to absorb a codegen change. Rejected:
  leaving it to Phase 120 D-10's host line alone.

- **D-16: `firestarter_app/doc/lockable-proms.md` is committed as-is with §17 fixed, no provenance header.**
  The file is currently **untracked** — never committed — and §17's `AT28C16` row is known wrong
  (SEVENTH CORRECTION item 6). It becomes a real shipped doc with that row corrected. The concern
  was put explicitly and the operator chose this path: it ships ~300 rows compiled from third-party
  datasheets, reading as an authoritative reference with no statement of its evidentiary basis, in
  the milestone whose validation ceiling forbids claims about SDP behaviour on real silicon. That is
  an **owned trade-off**, recorded here so no downstream agent re-opens it. Rejected: relocating it
  to `.planning/notes/` as a research artifact. Rejected: committing it with a provenance/uncertainty
  header.

- **D-17: GATE-02's named doc list is widened, and `REQUIREMENTS.md` is not edited.**
  GATE-02 names `firestarter/doc/PROTOCOLS.md` §1.6, `firestarter_app/doc/lockable-proms.md`,
  `firestarter_app/doc/protocol-id.md`, `firestarter/CLAUDE.md` and both READMEs — but **not** the
  two docs D-04 most affects. Added: `firestarter_app/doc/community-validation.md` (the ladder
  taxonomy plus its `dev test` description) and `firestarter_app/doc/beta-testing-install.md`, whose
  line 179 currently tells beta testers to run a command that now always writes. Satisfy the intent,
  record the correction in phase artifacts, do not edit `REQUIREMENTS.md` — the established response
  to a requirement whose stated mechanism is narrower than its intent.

### GATE-03 — the non-regression set

- **D-18: The stale audit-matrix golden is regenerated FIRST, as its own commit.**
  Verified RED live: `test_audit_coverage_matrix.py::test_golden_file_matches` produces 186034 bytes
  against a 184631-byte golden, first divergence at index 1178. Commit 1 regenerates that
  pre-existing 1403-byte drift **alone**, with zero DEVTEST code in the tree, and proves host pytest
  GREEN at that commit. Only then does D-06's new op string land, so this phase's matrix delta is
  attributable in isolation. This makes the masking SEVENTH CORRECTION item 2 forbids structurally
  impossible rather than merely discouraged. Rejected: one combined regen at the end. Rejected: a
  named GATE-03 exception — this phase genuinely changes the matrix, so the exception would hide a
  real expected change, and the debt would roll into the close.

- **D-19: The no-programmer-found characterization tests are hardened to pass with a board attached.**
  Patch the real port-enumeration seam rather than only `comports`, so a live `/dev/ttyACM*` cannot
  defeat the monkeypatch. Flagged as outside the phase's nine requirements and chosen anyway:
  **operator-authorised scope addition**, recorded the way Phase 119 recorded its cross-family
  regression sweep — not a scope leak. Consequence: GATE-03's "green" then means green with hardware
  attached, which is a stronger proof than the detach-the-bench procedure. Rejected: proving green
  with no board attached and recording the artifact.

### Claude's Discretion

- **Every user-facing string.** The UV stop-and-ask wording, the `--skip-erase`-is-inert warning, the
  always-writes notice, the duplicate-found message, and the could-not-check-for-duplicates line.
  Two constraints: the always-writes notice must be **unconditional and first**, and D-12's `NA`
  erase reason must name the **family fact** (*"protocol 0x0D — the 28C family has no erase
  operation"*), never the flag mechanism (*"FLAG_CAN_ERASE not set"*), because DEVTEST-01 requires a
  *named reason* a community tester can act on.
- **Bump the report's `schema_version`.** Safe and informative: `parse_devtest_issue.py` accepts it
  by **presence only** (`:99`), so a bump breaks no consumer while marking the new op vocabulary.
- **Keep `dev test`'s `0/1/2` exit-code tri-state unchanged.** `write-partial` introduces no new
  verdict, so `_VERDICT_EXIT_CODES` needs no edit. Phase 120 D-11's plain-`0/1` reasoning is
  specific to `dev sdp` and does not reach here.
- **How D-02's decision is carried** — a field on `Plan`, a field on `Step`, or both. D-02 fixes
  where the decision is *made* and that the execution layer only *reads* it; the container is open.
- **Where the two planted fixtures live and how the checker is pointed at them** —
  `tests/fixtures/planted_constants_*.h` plus `check_is_memory_cmd_no_ifdef.py`'s fail-closed
  `FIRESTARTER_*_SRC` seam is the closest precedent for a path-injected fixture.
- **Whether the b11 back-compat in D-06 is a tolerant parser or an explicit legacy-vocabulary
  constant**, provided old reports keep parsing and the tolerance is tested.
- **Plan ordering**, subject to four hard constraints: D-18's golden regen is the **first** commit;
  D-06's op string must precede the renderer/`to_dict`/golden work that consumes it; D-02's plan-side
  decision must precede the execution-layer read; and D-15's `messages.toml` edit must precede both
  mirror regenerations.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone framing and constraints (read first)
- `.planning/REQUIREMENTS.md` — **DEVTEST-01..06 and GATE-01..03 verbatim** (`:84`, `:88-92`,
  `:96-98`); the **Locked decisions** table; the **Out of Scope** table; §"Validation Ceiling" (the
  exact permitted and forbidden claims); and `:114`'s record that v1.21 SUB-01/SUB-02's *"explicit +
  interactive-only; never on a bare run"* contract is **REVERSED**, not silently dropped.
- `.planning/ROADMAP.md` §v1.22 → "Phase Details" → **Phase 121** (`:412-434`) — the ten success
  criteria this phase is verified against, plus the **Reversal note** at `:430`, whose collisions
  **(b)** (the `derive_plan` / `locked_destructive` contract change) and **(c)** (the UV axis pick,
  32-of-301) are answered by D-06 and D-02 respectively. ⚠ Its claim that the closed op vocabulary
  is *"consumed by the issue parser"* is **wrong** — see D-06's correction. Also read **Phase 122**
  (`:436-449`): D-04 and D-08 both hand it explicit obligations.
- `.planning/PROJECT.md` §"Current Milestone: v1.22" — **all seven** ⚠ correction blocks. Load-bearing
  here: **SEVENTH CORRECTION** items **1** (the redesign as a reversal, with the three locked
  decisions quoted verbatim from the live tree), **2** (the contract-change framing and the
  already-RED golden that *"must not be allowed to mask"* a new failure — D-18's cause), **3** (the
  32-of-301 measurement — D-02's cause), **4** (`gh issue create --label` aborts before creating —
  DEVTEST-06's constraint), **6** (`doc/lockable-proms.md` §17 is wrong about `AT28C16` — D-16), **8**
  (a two-repo requirement can pass its own phase's verification and still be false end to end), and
  **9** (`git -C … status --porcelain` empty, because a path-scoped `git diff` passes vacuously).
  Also **FOURTH CORRECTION item 4** — every phase from 118 on must include an explicit task checking
  firmware renames/deletions against `firestarter_app`'s source-scanning gates.
- `.planning/phases/119-lock-sdp-enable-command-surface-fw-half/119-NONREGRESSION.md` §CORRECTION-4 —
  the **nine-row** cross-repo gate table, explicitly handed to Phases 120-122. **Mandatory here**,
  and this phase touches firmware (D-15), so the rename-risk runs in both directions.

### Prior-phase decisions that bind this phase
- `.planning/phases/120-host-cli-surface-wire-emission-capability-refusal/120-CONTEXT.md` — **D-01/D-02/D-03**
  (`sdp_capability.py`'s fail-closed ALLOW-list, name-keyed, pure — what GATE-01 asserts against and
  the shape D-03 promised Phase 121 a stable symbol in); **D-04** (read-at-intent precedent for
  D-11's widening); **D-11** (honesty in the message, never the exit code); **D-12/D-13** (the
  planted-violation gate discipline); **D-18** (warn-and-proceed on a vacuous flag — D-13's exact
  precedent); **D-20** (this phase's own scope amendment). Its `<deferred>` names the two items
  D-13 and D-15 now close.
- `.planning/phases/119-.../119-CONTEXT.md` — **D-06/D-07** (the generic op-layer NULL-`main` refusal
  → `MSG_ERR_NOT_SUPPORTED`, which is DEVTEST-01's already-landed firmware half), **D-12** (OK means
  *"the sequence was emitted"*, said in words), **D-18** (how to record a reversal as a reversal).
- `.planning/phases/118-.../118-CONTEXT.md` — **D-01** (unconditional `LOG_ID` on INFO-band ids) and
  **D-04** (separate literal ids) — context for D-15's catalog edit.
- `.planning/phases/117-.../117-CONTEXT.md` — **D-05** (the SDP path never writes `response_code`).

### Design notes — the `dev test` redesign's own substrate
- `.planning/notes/dev-test-design-decisions.md` — the **per-family destructiveness table** D-01
  matches, the small-region-write-for-UV rationale, and the two-tier diagnostic contract.
- `.planning/notes/dev-test-destructive-flag-type-scope.md` — the **32-of-301 tally** and the
  `0x0B ⟹ UV` / `UV ⟹ 0x0B` converse argument. ⚠ Its closing recommendation *"prefer plumbing the
  real type through over widening the algorithm set"* is written for **write-region placement**;
  D-02 adopts its conclusion but for the stronger destructiveness reason.
- `.planning/notes/dev-test-unknown-chip-fail-fast.md` — SAFE-04's absent-chip hard-fail rationale.
- `.planning/notes/dev-tools-gating-channel-split.md` — 999.15 / gh#8. Open disposition: stable keeps
  only `dev read` + `dev test`, and D-04 makes `dev test` always-writing. Recorded, **not acted on**.

### Host — the code this phase changes
- `firestarter_app/firestarter/chip_test.py` — **the op vocabulary at `:272-278`** (D-06's target);
  `Step` at `:281-296` and `Plan` at `:298-316` including **`locked_destructive`'s MUST-NOT-iterate
  docstring**; **`derive_plan` at `:318-427`** (D-02's decision point, `can_erase` read at `:343`,
  the erase composition at `:400-423`); `_DESTRUCTIVE_OPS` / `_MULTI_RUN_OPS` at `:453-457`;
  `run_plan` at `:512-597`; **`_write_region_for` at `:640-670`** and the region constants at
  `:614-637`; `count_applicable` at `:984-1008` (the banner that D-04 makes permanently silent,
  since nothing is ever locked).
- `firestarter_app/firestarter/cli_handlers.py` — **`dev_test` at `:1836-2018`**: the four options at
  `:1838-1877` (D-05 removes all of them), the docstring's three reversal-relevant claims at
  `:1888-1910`, the `--destructive` confirm at `:1919-1925`, **SAFE-04's `get_eprom`-emptiness
  hard-fail at `:1932-1933`** (keep it), `_make_sampler` at `:1812-1833`, `_is_interactive` at
  `:1802-1809`, `_verdict_code` / `_VERDICT_EXIT_CODES` at `:1740-1750`, and the `--submit` call at
  `:2010-2013`. Also **`write` at `:530-548`** (D-13's target; note the `-b` polarity rationale lock
  and TRAP #6) and `_build_op_flags` at `:242-280`.
- `firestarter_app/firestarter/database.py` — **`convert_to_programmer` at `:535-598`**, specifically
  the `FLAG_CAN_ERASE` block at `:569-595` whose comment block **must be rewritten as a recorded
  reversal** by D-12. Also `:187-199`, which merges `~/.firestarter/database.json` live and is
  invisible to CI.
- `firestarter_app/firestarter/diagnostic_report.py` — **`dedup_fingerprint` at `:177-206`** (hashes
  op names, so D-06 differentiates for free); **`build_db_diff` at `:255-285`**, whose ladder logic
  keys **only** on verdicts (why D-08 is free); the `_LADDER_*` constants at `:229-233`;
  `is_submittable` at `:157-170`; `DiagnosticReport` and its renderer / `to_dict` / `to_json_block`
  from `:294`.
- `firestarter_app/firestarter/submit.py` — **`SUBMIT_REPO = "henols/firestarter_prom"` at `:73`**
  (already correct on this branch; only the released `v1.21` tag misfiles); `GSD_INBOX_LABEL` at
  `:79` with its **never-on-the-create-argv** contract; `gh_available` at `:219-232`;
  `submit_via_gh` at `:235-277` (the permission-independent argv D-09/D-11 extend);
  `submit_via_browser` at `:292-357`; **`submit_report` at `:365-468`** — D-09/D-10/D-11 restructure
  its step order, and its Step 3 off-TTY branch and Step 4 confirm both change under D-05.
- `firestarter_app/firestarter/eprom_operations.py` — **`_setup_operation` at `:315+`, especially
  `command_dict = eprom_data_dict.copy()` at `:333`** — the fact that rules out D-02's
  `convert_to_programmer` alternative. Also `build_flags` at `:168-197` and `FLAG_SKIP_ERASE` at
  `:193`.
- `firestarter_app/firestarter/sdp_capability.py` — GATE-01's target: `SDP_PROTOCOL_ID` at `:58`,
  **`SDP_CAPABLE_TOKENS` at `:70`** (43 tokens, D-14 Class 2's subject), `FRAM_TOKENS` at `:156`,
  `PRE_SDP_NAMED_TOKENS` at `:161`, the `REASON_*` constants at `:180-184`,
  `split_part_number_tokens` at `:187`, `sdp_capability_for_entry` at `:201`, `sdp_capability` at
  `:266`. **Leave the module's shape intact** — the gate asserts against it.
- `firestarter_app/firestarter/serial_comm.py` — `_log_command_details` at `:540-556`, the only other
  host reader of `FLAG_CAN_ERASE` and **DEBUG-only** (D-12's bounded blast radius).

### Firmware — this phase's only firmware edits are D-15's catalog + GATE-02's docs
- `firestarter/tools/catalog/messages.toml` — **the canonical catalog; edit ONLY this file.**
  `0x5F` `MSG_INFO_SDP_UNLOCK_DONE_US` is D-15's target; `0x61` `MSG_INFO_SDP_LOCK_DONE_US` is the
  wording to mirror.
- `firestarter/doc/PROTOCOLS.md` §1.6 and `firestarter/CLAUDE.md` — GATE-02 targets.
- `firestarter/src/operation_utils.cpp` — `op_execute_stateful_operation`'s NULL-`main` refusal, the
  landed firmware half of DEVTEST-01. Read-only reference; **do not re-implement**.
- `firestarter/src/proms/eeprom_28c.cpp` — confirms `configure_eeprom28c` has **no** erase op at all,
  which is what makes the `FLAG_CAN_ERASE` advertisement a lie.
- `firestarter/include/messages.h` — **codegen-generated**; regenerate, never hand-edit.

### Docs — GATE-02's full target list (D-17-widened)
- `firestarter/doc/PROTOCOLS.md` §1.6 · `firestarter/CLAUDE.md` ·
  `firestarter_app/doc/lockable-proms.md` §17 (**untracked — D-16**) ·
  `firestarter_app/doc/protocol-id.md` · `firestarter/README.md` · `firestarter_app/README.md`
  (`:131` already documents the flag-free form) ·
  **`firestarter_app/doc/community-validation.md`** (`:7`, `:27` the ladder taxonomy, `:80` the N≥2
  rule, `:96`, `:113`) · **`firestarter_app/doc/beta-testing-install.md`** (`:11`, `:24`, `:81`,
  `:179`, `:185`).

### Host test surfaces
- `firestarter_app/tests/test_dev_test_cmd.py`, `tests/test_chip_test.py` (the `derive_plan` /
  `FLAG_CAN_ERASE` / plan-shape suites at `:274-570` and `:1255-1283`),
  `tests/test_diagnostic_report.py`, `tests/test_submit.py` (**`:237` pins the repo target;
  `:301-320` is the negative-argv idiom D-11 extends**), `tests/test_parse_devtest_issue.py`,
  `tests/test_matrix_artifact.py`, `tests/test_validate_family_cmd.py`,
  `tests/test_validate_oracle.py`, `tests/test_check_devtest_orchestrator.py` — the **82** references
  D-05 breaks.
- `firestarter_app/tests/test_database_conversion.py` **`:99-104`** and
  `tests/test_eprom_operations.py` **`:1132`** — the two deliberately-pinned assertions D-12 inverts.
  `tests/test_val_wire_5v_page.py:142`'s `0x07` pin is **unaffected** — confirm, don't assume.
- `firestarter_app/tests/test_sdp_capability.py` — 12 legs including the AST import-purity leg at
  `:640` and the local-override runtime leg at `:670`. GATE-01 **adds to** this; it does not replace it.
- `firestarter_app/tests/test_audit_coverage_matrix.py` — **RED right now**, 186034 vs 184631 bytes,
  first diff at index 1178. D-18's subject.
- `firestarter_app/tests/test_no_programmer_found_read` / `_erase` — D-19's target.
- `firestarter_app/tools/check_devtest_orchestrator.py` + `tests/test_check_devtest_orchestrator.py` —
  the scoped AST gate that pins `dev_test` by name with a helper allow-list and **fails closed on a
  zero-match scan**; D-05 will trip it if the allow-list is not updated. Also the closest shape
  precedent for D-14.
- `firestarter_app/tools/check_is_memory_cmd_no_ifdef.py` — the fail-closed `FIRESTARTER_*_SRC`
  fixture-injection seam D-14's fixtures should follow.
- The rest of the nine-row checklist: `tools/check_no_log_in_sdp_window.py`,
  `tests/test_sdp_table_parity.py`, `tools/gen_sdp_bus_config.py` + `tests/test_sdp_bus_config_drift.py`,
  `tools/check_dispatch.py`, `tools/build_db.py` + `tools/diff_db.py`,
  `tools/check_no_community_support_status_write.py`, `tests/test_revision_constants_parity.py`.

### Project conventions
- `firestarter_app/CLAUDE.md` — the `constants.py` ↔ `firestarter.h` sync rule and the tooling gate:
  `ruff check` + `ruff format --check` + `mypy` (strict on 8 modules, **`cli_handlers.py` among
  them**) + `pytest --cov-fail-under=70`.
- `CLAUDE.md` (meta) — the constants/flag-bit duplication rule.
- Ruff/format must be validated against the **py3.9/3.11 CI targets**, not the devcontainer's 3.12
  (`.planning` memory `reference_devcontainer_py312_masks_ci_py39.md`).

</canonical_refs>

<code_context>
## Existing Code Insights

### Verified live during this discussion — do NOT re-derive
- **The programmer dict IS the wire payload.** `_setup_operation` does
  `command_dict = eprom_data_dict.copy()` (`eprom_operations.py:333`). This is the single fact that
  rules out adding `electrical-type`/`is_uv` to `convert_to_programmer` — it would re-add a type
  field v1.20 removed as a breaking change.
- **`chip_database.json` has no `flags` key.** Confirmed by enumerating entry keys: `datasheet`,
  `electrical`, `part_number`, `pinout`, `programming`, `provenance`, `source`, `support_status`,
  `verification_note`, `verification_status`. `FLAG_CAN_ERASE` is a **runtime** computation, so
  **D-12 cannot break `diff_db.py` identity or CLOSE-01's 84-count.**
- **No firmware native test and no `validation_matrix_spec.json` family pins the incoming wire flags
  for `eeprom28c`.** Grepped `test_val_eeprom28c/`, `_shared/validation_matrix.h`, and every family
  entry in the spec. D-12's firmware-side exposure is nil.
- **`serial_comm.py:549`'s `FLAG_CAN_ERASE` read is inside `_log_command_details`, guarded by
  `logger.isEnabledFor(logging.DEBUG)`.** DEBUG-only; not a behavioural consumer.
- **`build_db_diff`'s ladder logic keys only on the verdict set** (`diagnostic_report.py:266-278`),
  never on op names — so D-06's new string auto-tags `community-reported` with zero code change.
- **`dedup_fingerprint` hashes op names** (`f"{op}={verdict}:{cls}"`, `:198-204`) — so D-06
  differentiates partial from full runs for free, and `count_agreeing`'s fingerprint grouping means
  a partial run can never cross-agree with a full one toward N≥2.
- **`tools/parse_devtest_issue.py` has no op vocabulary at all.** It keys on the `[dev test]` title
  marker (`:59`), `schema_version` by **presence only** (`:99`, `:24`), and `dedup_fingerprint`
  grouping (`:180`). The ROADMAP's claim that the closed op set is consumed there is wrong.
- **`firestarter_app/doc/lockable-proms.md` is untracked** — `git ls-files` returns nothing and
  `git log -- <path>` is empty, so it was never committed and is not `.gitignore`d. `SECURITY.md`
  and `write_test_port.sh` are likewise untracked in the working tree.
- **`test_audit_coverage_matrix.py::test_golden_file_matches` is RED:** produced 186034 bytes vs
  golden 184631, first divergence at index 1178 (`' '` vs `'|'`).
- **The removed-flag ripple is 82 references across 6 test files**, and
  `tools/check_devtest_orchestrator.py` pins `dev_test` by name with a helper allow-list.
- **`firestarter_app` is on `v1.22-at28c-software-data-protection-lifecycle` at `96e0622`.**
  Working tree carries only untracked artifacts plus a one-line `.gitignore` change.

### Reusable Assets
- **`_write_region_for`'s existing 256-byte top-anchored UV window** (`chip_test.py:640-670`) — the
  "small part" DEVTEST-04 asks for **already exists**; D-02 fixes only *which parts reach it*.
- **`tools/check_devtest_orchestrator.py`** — an AST gate denying three violation classes in one
  checker, with a fail-closed zero-match guard. D-14's shape precedent.
- **`tools/check_is_memory_cmd_no_ifdef.py` + `tests/fixtures/planted_constants_*.h`** — the
  fail-closed `FIRESTARTER_*_SRC` fixture-injection seam for a planted violation.
- **`submit_via_gh`'s permission-independent argv** (`submit.py:252-268`) — repo, title, `--body-file -`
  and nothing triage-gated. D-11's `gh issue comment` must match it.
- **`tests/test_submit.py:301-320`** — the negative-argv idiom (assert the flag is *never* sent).
- **HOST-02's D-18 warn-and-proceed pattern** (`cli_handlers.py:547-551`) — D-13's exact template.
- **`_is_interactive()`** (`cli_handlers.py:1799-1806`) — monkeypatchable precisely because
  `CliRunner` replaces `sys.stdin`. D-03's TTY seam.
- **SAFE-04's `get_eprom`-emptiness hard-fail** (`cli_handlers.py:1929-1930`) — keyed off DB
  emptiness, never a `resolve_chip` refusal. Survives D-05 unchanged.

### Established Patterns
- **Every gate ships a planted-violation fixture proving it actually fails**; structural/AST scans
  over substring greps (v1.21 SAFE-03, 118 D-06, 119 D-04, 120 D-12).
- **Refuse or warn before the wire, with a spoken reason** — never a silent no-op, never fabricated
  success.
- **Honesty in the message text, not in a status code** (117 D-05, 118 D-02, 119 D-12, 120 D-11).
- **A reversal is recorded *as* a reversal, with its constraints named** (119 D-18, 120 D-20). This
  phase carries **three**: DEVTEST-02..06 itself, D-12's `database.py` note, and v1.21 SUB-01/02.
- **A requirement whose stated mechanism is narrower than its intent:** satisfy the intent, record
  the correction in phase artifacts, do **not** edit `REQUIREMENTS.md` (LOCK-04, LOCK-06, HOST-04,
  and now D-06 and D-17).
- **Firmware renames/deletions break host source-scanning gates** — 4× in Phase 117, 4 pytest
  repairs in Phase 118. D-15 touches firmware, so this risk is **live** here
  (`.planning` memory `reference_firmware_renames_break_host_source_scanning_gates.md`).
- **Executors prematurely mark multi-plan requirements Complete** — 4× in Phase 116. **Name the
  allowed DEVTEST-NN / GATE-NN ids in every dispatch prompt** and re-check `REQUIREMENTS.md` after
  each plan (`.planning` memory `reference_executors_prematurely_mark_requirements_complete.md`).
- **Exit-code-only tests lie about `dev test`.** The load-bearing assertion in the absent-chip work
  was `read_hardware_revision_value.assert_not_called()`, not the exit code. D-03's off-TTY path and
  D-09's dedup path both need that treatment: assert **what was and was not called**, never merely
  the exit status (`.planning` memory `reference_dev_test_absent_chip_false_green_trap.md`).
- **`messages.h` / `messages.py` are codegen-generated** — edit `messages.toml` and regenerate;
  **never** hand-normalise the raw output (`.planning` memories
  `reference_firmware_messages_h_is_codegen_generated.md`, `reference_codegen_ruff_clean_emitter.md`).
- **STATE.md tooling under-writes and re-clobbers fields.** Call `state.record-session` first, then
  progress/metric/decision calls, then hand-verify `current_phase_name` and `progress.percent`.
- **`- **D-NN: text**` must close its bold run on ONE line**, carry at most one colon before the
  closing `**`, and never open with a glyph — otherwise plan-phase's §13a decision-coverage gate
  fails closed.

### Integration Points
- `firestarter_app/firestarter/chip_test.py` — the 7th op string, `derive_plan`'s UV decision and
  write-scope recording, the two frozensets, `_write_region_for`'s read-not-guess conversion.
- `firestarter_app/firestarter/cli_handlers.py` — `dev_test` loses all four options and gains the
  UV ask, the always-writes notice and the filing ask; `write` gains D-13's warn.
- `firestarter_app/firestarter/database.py` — D-12's `algorithm == 0x0D` exclusion plus its rewritten
  reversal comment.
- `firestarter_app/firestarter/diagnostic_report.py` — renderer / `to_dict` / `schema_version` for
  the new op string.
- `firestarter_app/firestarter/submit.py` — the dedup query, the comment path, and `submit_report`'s
  restructured step order.
- `firestarter_app/tools/check_sdp_capability_*.py` (**new**) + two planted fixtures + its pytest.
- `firestarter_app/tools/check_devtest_orchestrator.py` — allow-list update for D-05.
- `firestarter/tools/catalog/messages.toml` + both regenerated mirrors (D-15).
- 8 docs across both sub-repos (D-16, D-17).

### Setup precondition — verify at plan time, do not assume
`firestarter_app` must be on `v1.22-at28c-software-data-protection-lifecycle` before any sub-repo
write — **confirmed at `96e0622` at discussion time**. The firmware sub-repo must be on the same
branch, and unlike Phase 120 it is **not** byte-untouched here: D-15 edits `messages.toml` and
GATE-02 edits two firmware docs. The milestone-branch check has been a real trap twice
(`.planning` memory `project_v121_submodule_branch_base.md`).

</code_context>

<specifics>
## Specific Ideas

- **The sharpest thing this discussion settled is that `dev test` is no longer a diagnostic
  command — it is a write test.** D-01 plus D-03 compose to "every run writes": UV parts get at
  least 256 bytes, everything else gets the whole device, TTY or not. v1.21 built the command around
  "non-destructive by default" and locked that in SAFE-01 and Phase 109 D-01; that premise is now
  gone with no read-only escape at all. D-04 makes the notice mandatory and first, because the only
  thing standing between a community tester and a wiped chip is the sentence the command prints.

- **Getting the UV axis wrong is now a chip-destroying bug, not a coverage gap.** Before this phase,
  `_write_region_for`'s 32-of-301 miss cost only upper-address-decode coverage — both branches wrote
  the same 256 bytes. Under D-01, a UV part that fails the UV test receives an **unprompted
  full-device write** and is irrecoverable without a lamp. The same line of code changed severity
  class without changing at all. That is why D-02 moves the decision to the one place that has exact
  information and forbids the execution layer from guessing.

- **`derive_plan`'s D-01/SAFE-01 architecture was built to make a destructive op unreachable, and
  this phase deletes the reason it existed.** `locked_destructive` was designed so `run_plan` had
  *no code path* to a destructive op on a non-destructive plan, with a docstring saying `run_plan`
  MUST NOT iterate it. With the write always happening, that list is permanently empty and
  `count_applicable`'s N-of-M banner never fires again. Do not leave it as vestigial scaffolding with
  a docstring describing a contract nothing enforces any more — either repurpose it or state plainly
  in-source that it is dead.

- **Three ROADMAP/REQUIREMENTS framings turned out to be wrong or overstated, and all three shrink
  the work.** The op vocabulary is not consumed by the issue parser (D-06). The ladder taxonomy needs
  no change for a new op string (D-08). And `diff_db.py` identity cannot be broken by D-12 because
  the flag is never in the DB file. This milestone has a consistent pattern of stated mechanisms
  being narrower or wider than reality — LOCK-04's harmful `default:` arm, LOCK-06's superseded
  figure, HOST-04's five-part list — and the established response holds: verify before planning
  around the text.

- **The evidence-weight concern I raised about D-08 is genuinely smaller than it first looked, and
  the reason should be written down.** A 256-byte partial run auto-tagging `community-reported`
  identically to a full round-trip sounds like it poisons Phase 122's ledger. It does not, because
  `count_agreeing` groups by `dedup_fingerprint` and D-06's new op string changes that hash — so a
  partial run can never contribute to a full run's N≥2 promotion. Phase 114's GRAD-01 lock holds
  end to end **through the fingerprint**, not through the tag. Phase 122 should state it that way.

- **Two owned trade-offs, chosen with the cost named, recorded so nobody re-opens them.** D-03 writes
  to silicon off-TTY where nobody consented. D-16 ships ~300 rows of datasheet-compiled protection
  claims as a project doc with no provenance header, in the milestone whose validation ceiling
  forbids claims about SDP behaviour on real silicon. Both were put explicitly and both were the
  operator's call.

</specifics>

<deferred>
## Deferred Ideas

### Raised during this discussion, routed elsewhere
- **`dev test`'s release-channel disposition.** 999.15 / gh#8's channel split keeps only `dev read`
  and `dev test` in the stable channel — and D-04 makes `dev test` a command that always writes to
  the chip. Whether an always-writing command belongs in stable is a real question this phase
  surfaces and does not answer. Recorded, **not acted on**, consistent with Phase 120's handling.
- **A read-only `dev test` mode.** Declined at D-04 because it costs a flag DEVTEST-02 removes. If
  community feedback shows testers want a safe first-contact sweep, it wants its own phase and its
  own flag-surface decision.
- **Hardening `derive_plan`'s vestigial `locked_destructive`.** Named in `<specifics>`; if the phase
  chooses to state it dead in-source rather than repurpose it, an actual removal is a separate
  cleanup.

### Carried forward, still not taken
- **The wider CLI flag re-design** — splitting `-f/--force`'s two unrelated meanings, reconciling
  `-b`'s opposite polarity between `write` and `erase`, and a project-wide `-y` idiom. Each changes
  behaviour on commands this phase does not otherwise touch. Its own phase.
- **The end-to-end `infoic.xml` `page_size` decode phase** — still operator-approved, still **not
  inserted into ROADMAP.md**. Insert with `/gsd-phase`; heed `.planning` memory
  `reference_new_milestone_phases_clear_destructive.md`.
- **Widening `_probe_port`'s `[\d.x]+` version capture** so the host can order `3.0.0b11 < b12`.
  Declined at Phase 120 D-15/D-16 in favour of ack detection; touches the ring-fenced transport
  version-capture path.
- **Widening the trace recorder to a third strobe kind** (data-bus direction) — declined at 118, 119
  and 120.
- **`DIP24_2816`'s missing `static-high-pins` (SDP-F8)** and **datasheet verification of the SDP
  magic addresses (SDP-F7)** — SDP-F7 bears directly on the allow-set's membership and is still
  UNVERIFIED. GATE-01 guards the set's *shape*, never its *correctness*.
- **Unity-teardown SIGABRT root cause** (`test_flash_intel_vpp`); recording every side-effecting
  `rurp_*` call; all-84-chips table-driven trace coverage.
- **`prove-pio-dev-flag-fails-closed.md` items 1-3** — the `${sysenv.*}` fail-open/fail-closed matrix.
  Belongs to 999.15 / gh#8.

### Reviewed Todos (not folded)
`todo.match-phase 121` returned **13** matches. Eleven carry the same disposition as Phases 116-120 —
generic keyword overlap only (VPP-on-reads skip, `prove-pio-dev-flag-fails-closed`, avrdude MCU
fallback, COBS frame deadline, v1.28 PY32 roadmap prior-art, JP5 dead renderer, JP4 labels, Rev-0
photography, the MODIFICATIONS trace, dead `json_init()`, the `DATA_BUFFER_SIZE` spike). Two were
considered on their merits and declined again:

- **`decode-infoic-flags-bits-14-15-protect-metadata.md`** (0.6) — decode `infoic.xml` flags bits
  14/15 in `build_db.py`. It is real SDP-protection metadata and could eventually replace part of the
  curated allow-set with decoded values. **Not folded:** it requires a DB regeneration, which
  `diff_db.py` identity under GATE-03 and CLOSE-01's unchanged-84 count both forbid this milestone.
  Revisit in the `page_size` phase, where a regeneration is already in scope.
- **`fold-response-code-into-log-macro.md`** (0.6) — derive `response_code` from the log id's
  severity band. Declined at 118, 119, 120 and again here: it conflicts with 117 D-05 / 118 D-02 /
  119 D-12, and D-15's catalog edit touches the same id space without needing it. Its own phase.

</deferred>

---

*Phase: 121-`dev test` FIX + GATES + DOCS + REDESIGN*
*Context gathered: 2026-07-29*
