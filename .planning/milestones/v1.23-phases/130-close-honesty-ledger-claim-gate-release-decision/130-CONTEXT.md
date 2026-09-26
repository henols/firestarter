# Phase 130: Close — Honesty Ledger, Claim Gate, Release Decision - Context

**Gathered:** 2026-08-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Close v1.23 with an honest, verifiable record of exactly what was and was not proven; carry every
research correction into the planning record; land the ROADMAP slot renumber; and make the
`beta`-push decision deliberately, before the act, rather than as a side effect.

**In scope (CLOSE-01, CLOSE-02, CLOSE-03, CLOSE-04):**
- **CLOSE-01** — R-1…R-18 applied to `PROJECT.md`, `STATE.md`, `ROADMAP.md` and
  `.planning/notes/py32f071-port-branch-state.md`, plus **two deliberate in-scope additions to that
  file list**: `REQUIREMENTS.md`'s PCB-03 and FUT-N04 VTOR clauses (D-06) and the Validation
  Ceiling's toolchain-absent clause (D-07). Proven by a committed, label-aware checker (D-08).
- **CLOSE-02** — a new `130-LEDGER.md`, organised as claim classes **by evidence tier** (D-09),
  carrying the full negative space (D-10) and both the sourcing and claim-status axes (D-12).
- **CLOSE-03** — the ROADMAP slot renumber and the stale v1.28 prior-art correction in one change
  (D-13, D-14, D-15), with a one-shot before/after proof that v1.24–v1.27 are byte-unchanged (D-16).
- **CLOSE-04** — `130-DECISION.md` committed **before any push**; the `beta` merge in both
  sub-repos; the `3.0.0b15` cut; the manual PyPI dispatch; both channels verified directly; the
  observed cut tag read from `gh release list`, never computed (D-01, D-03).
- **Two hand-written release bodies** (`130-RELEASE-NOTES-fw.md`, `130-RELEASE-NOTES-app.md`)
  behind a **blocking operator wording review** (D-02).
- **One firmware source change, chosen deliberately in this discussion:** land the interim
  pid.codes `1209:0001` in `platform/py32f071/src/usb_cdc.c` before the cut, with the source
  warning pid.codes' terms require, plus the lockstep `[SHARED:S4]` body edit in both copies of the
  flash-path record (D-11).

**Explicitly NOT in scope:**
- The `v1.23` annotated tag and any merge toward `main` — both stay with `/gsd-complete-milestone`
  (D-04).
- Any stable release. Stable is operator-gated and nothing here approaches it.
- Deleting the stray `3.0.0b12` prereleases — declined at v1.22 D-05 and not re-opened.
- A bench smoke-test of anything. **No PY32F071 PCB exists.**
- Compacting the `v1.30` SDP slot into the freed `v1.29` — its own entry says to do that at
  activation, not now (D-14).
- Any `support_status`, `chip_database.json` or `PROTOCOL-LEDGER` change.

**Validation ceiling applies and is load-bearing.** `.planning/REQUIREMENTS.md` §"Validation
Ceiling" holds the permitted and forbidden claims. This phase's entire job is to not cross that
line in public — and it is the first phase in the milestone that publishes anything.

**The four closing artifact names are a pre-existing contract, not a choice.**
`.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py`
`_DEFAULT_TARGETS` names `130-LEDGER.md`, `130-DECISION.md`, `130-RELEASE-NOTES-fw.md`,
`130-RELEASE-NOTES-app.md` with **all-or-nothing arming**: producing three of four is a hard
failure by design. Renaming or adding a scanned artifact requires amending that list **in the same
commit**.

</domain>

<decisions>
## Implementation Decisions

### The push, the cut, and the close boundary — CLOSE-04

- **D-01: Accept the auto-fire — the merge IS the `3.0.0b15` cut, in both sub-repos.** Both repos
  carry `on: push: branches: [beta]` with git-tag-scan auto-increment and both sit at a `3.0.0b14`
  tag ceiling, so the outbound `--no-ff` merge push cuts the next beta by itself. Sequence: record
  the decision, merge, push, let CI cut, manually dispatch `publish.yml` for PyPI, verify both
  channels. This is the first publication of `firestarter_py32f071.hex` as a real release asset,
  which is the only thing that makes the 21 already-landed host capabilities reachable; REL-01…04's
  present evidence is a rehearsal draft that has since been deleted. The two halves are lockstep —
  a firmware asset with no published host that can install it is inert, and vice versa. Risk is
  bounded: no PY32F071 board exists anywhere, and the py32 board is beta-only by construction
  (`_BOARD_CHOICES` is computed at import time, so a stable build hides it entirely).
  **Rejected:** avoid — a recorded no-push leaves the milestone's one user-visible deliverable
  permanently unexercised and makes the two required release-notes artifacts notes for nothing.
  **Rejected:** accept gated on a fresh rehearsal dispatch — re-derives evidence that already
  exists from run `30722352902` and costs an operator round-trip plus a draft cleanup.

- **D-02: Both b15 release bodies are hand-written and sit behind a blocking operator wording review.**
  `130-RELEASE-NOTES-fw.md` and `130-RELEASE-NOTES-app.md` are committed drafts carrying
  the ceiling verbatim, PCB-05's socket-empty instruction, the USB identity statement (D-11), and
  an explicit statement that the py32 image has never run on silicon and no PCB exists. The claim
  scanner's own module docstring says a green run is the **mechanizable half only** — it cannot
  detect an implied overclaim, a misleading omission, or wrong tone. Precedent: v1.22 D-08/D-16 and
  Plan 116-07. **Rejected:** posting once the scanner is green, with no human read, on the first
  release ever to carry a py32 asset. **Rejected:** hand-writing the firmware body only — the app
  is the half that gained `fw --board py32f071`, and a PyPI installer never sees the firmware body.

- **D-03: The py32 asset's presence on the real b15 cut is a gate, not a note.** `beta-build.yml`'s
  ARM steps are `continue-on-error: true` by design, so b15 can publish green with no py32 asset at
  all. The phase asserts `firestarter_py32f071.hex` is among b15's published assets, read from
  `gh release view`; absence is a hard failure to be root-caused (`py32f071.yml` is the loud gate
  and says what broke) before close. This does not touch the containment design — containment
  protects the AVR release, this gate protects the honesty claim, and it is the only chance to
  prove REL-02 on a real published release rather than a deleted draft. **Rejected:** record-don't-
  gate, which would leave REL-02's real-cut evidence a rehearsal artifact permanently.
  **Rejected:** gate with one diagnostic re-dispatch — the loud run is already available read-only.

- **D-04: Publish in-phase; the `v1.23` tag and any merge toward `main` stay with `/gsd-complete-milestone`.**
  Mirrors v1.22 D-07 and v1.21 Phase 115: the tag then points at a beta
  already published and channel-verified. This phase **asserts** the meta gitlinks still match the
  milestone-branch tips at phase end, re-bumping only if its own commits move a tip — which honors
  this milestone's own in-phase gitlink practice (Phases 125/128/129) rather than v1.22's pinned
  model. **Rejected:** tagging in-phase — couples this phase's verification scope to the tag, and
  local `beta` lags origin after CI's auto-commit, so a tag cut before a fetch points at the wrong
  commit. **Rejected:** saying nothing about gitlinks — v1.22 learned an unasserted gitlink drifts
  silently and had to be corrected out-of-band.

### Carrying the corrections — CLOSE-01

- **D-05: Corrections land per document kind, not uniformly.** `PROJECT.md` and `ROADMAP.md` get
  labeled `⚠ CORRECTION` blocks — v1.22's eight-block register is the precedent, and
  `/gsd-new-milestone` reads both to seed scope, so a block warns a future reader where an in-place
  edit would not. `STATE.md` is edited in place; it is a working file that already carries a
  partial `⚠ RESEARCH CORRECTIONS` block. `.planning/notes/py32f071-port-branch-state.md` gets an
  **append-only SUPERSEDED section** rather than in-place surgery, because it is a timestamped
  2026-07-28 capture that says so in its own frontmatter. **Rejected:** edit-in-place everywhere —
  destroys the what-did-we-once-believe trail and silently rewrites a dated capture.
  **Rejected:** correction blocks everywhere — STATE.md and the note become block sprawl.

- **D-06: CLOSE-01 amends `REQUIREMENTS.md`'s two VTOR clauses, each with an inline supersession note.**
  PCB-03's *"on a part with no VTOR"* and FUT-N04's *"Cortex-M0+ has no VTOR"* are both
  corrected, citing `129-RESEARCH.md` C-1 and preserving the superseded wording. Justified because
  these are false **facts**, not narrower **mechanisms** — a distinction the standing
  don't-edit-REQUIREMENTS discipline (LOCK-04, LOCK-06, HOST-04, 121 D-06/D-17) does not cover —
  and because PCB-03's own text explicitly assigns the job to CLOSE-01. This widens CLOSE-01's
  stated four-file list by one, recorded as a deliberate in-scope addition. Note the asymmetry that
  makes both worth fixing: PCB-03 already carries its correction inline so no reader is misled,
  while FUT-N04 states the falsehood bare as the first of four deferral reasons on a live
  forward-looking item. **Rejected:** FUT-N04 only. **Rejected:** leaving REQUIREMENTS.md untouched.

- **D-07: The Validation Ceiling's toolchain clause is narrowed in place; the reproduction recipe goes in `130-NONREGRESSION.md`.**
  The false premise (*"arm-none-eabi-gcc, cmake and ninja are
  absent… unmeasurable locally, by anyone"*) is replaced: the toolchain **is** installable here,
  but a local build's **absolute** size may never be compared against a CI figure — measured
  `text=27260` local against `text=27344` CI — so every absolute ARM size claim still cites a run
  URL + SHA. What becomes newly permitted is stated explicitly: local **delta** and byte-identity
  claims only, and byte-identity never implies the image runs. This is consistent, not novel:
  `.planning/v1.23-FLASH-PATH-DECISION.md` §4(b) already independently uses this exact wording.
  **Rejected:** putting the recipe in the ceiling — a claims-policy statement should not become a
  how-to. **Rejected:** ledger-only, leaving the governing document asserting something disproven.

- **D-08: CLOSE-01 is proven by a committed, label-aware checker with a planted-violation fixture.**
  A phrase table of every superseded figure/claim, skipping hits inside labeled
  correction blocks, with a fixture proving it exits non-zero on **both** a planted stale figure and
  a mislabeled block — BASE-08's milestone-wide discipline applies to any checker this milestone
  introduces, and label-awareness is exactly where a fail-open bug would hide. The forward payoff is
  the point: `/gsd-new-milestone` reads `PROJECT.md` and `ROADMAP.md` to seed the next milestone,
  which is precisely how the stale v1.28 prior-art paragraph was going to propagate.
  **Rejected:** a one-off recorded sweep — nothing then prevents reintroduction at seeding time.
  **Rejected:** extending `check_permitted_claims.py` — it conflates outward-facing overclaim
  scanning with planning-doc staleness, and its D-15 all-or-nothing arming is keyed to four
  artifact names.

### The honesty ledger — CLOSE-02

- **D-09: `130-LEDGER.md` is organised as claim classes by evidence tier.** Rows are grouped by
  what **kind** of evidence backs them — CI-compile-only (the ARM target builds), AVR-measured
  (flash/RAM, native case and suite counts, golden traces), native-simulated (CFG-05's dual-slot
  fake backend), mock-only (HOST-03's readback, the DFU sequence against descriptors and mocks),
  real-published-artifact (the b15 py32 asset), and decision-only-unverified (the flash path and
  PCB record). Each row still pairs a permitted wording with its explicit non-claim. This
  milestone's defining fact is that all of it is software-only, so the honest statement is the
  **strength gradient**: a green CMake configure and a published release asset are not comparable
  proof. **Rejected:** one row per requirement category — adjacent rows would read equally strong.
  **Rejected:** honesty surface only — the release bodies would then have no single source for the
  permitted wording they must match.

- **D-10: The negative space covers the deferrals AND every owned residual.** The eight deferrals
  (FUT-N02, FUT-N04, FUT-N05, FUT-N06, FUT-VPP, FUT-CAL, FUT-ORACLE, FUT-ARMSIZE) one line each
  with its reason, **plus** every trade-off and unresolved residual this milestone's phases
  recorded: HOST-01's accepted `flash_method()` deviation, HOST-04's separate mypy-debt CI failure,
  HOST-06's network-unreachable UM1504 residual, REL-03's fails-on-missing-AVR-asset half proven
  locally only, REL-04's F-8 (neither app CI workflow checks out the firmware sibling), Phase 129's
  F-10 (a contiguous PB0–PB7 data bus is **physically impossible on QFN56 and QFN32** — a
  part-selection constraint, unrecoverable after layout), and 129's two open hardware questions
  (`nBOOT1`'s factory default, and whether the USB PHY provides an internal D+ pull-up).
  **Rejected:** deferrals only — F-10 especially deserves top billing. **Rejected:** residuals only,
  pointing at REQUIREMENTS.md §Future Requirements, which v1.22 D-12 considered and rejected.

- **D-11 — The interim pid.codes `1209:0001` lands in `usb_cdc.c` before the cut, and the release body states it.**
  D-01 publishes an image whose USB device descriptor currently presents
  `0x36B7`/`0xFFFF` — **Puya Semiconductor's registered vendor identity**, copied verbatim from the
  pinned SDK's CDC example — against a hard ship gate that reads *"no PY32F071 board ships, and no
  release advertises a USB identity, until a PID allocated under VID 0x1209 exists"*
  (`.planning/v1.23-FLASH-PATH-DECISION.md` §5(c)). The record's own §5(b) calls the interim id
  *"strictly better than the status quo"* and notes it *"does not weaken the ship gate, because the
  test id's own terms forbid shipping"*. Phase 129 D-06 declined the edit only because that phase
  was docs-only and no cut was planned; publishing is a new fact. Scope: two `#define`s plus the
  not-universally-unique source warning pid.codes' terms require. **Two consequences a plan must
  carry:** the change is a real firmware code change and needs an ARM pass before the merge; and
  §5 is `[SHARED:S4]` under the 41-leg body-only sync gate
  (`firestarter/tests/test_flash_path_record_sync.py::test_shared_sections_match`, parametrized
  over all five keys), so §5(a)'s *"what the descriptor currently presents"* must be updated
  **identically in both copies** or the gate goes red. PCB-04's *"`usb_cdc.c` itself stays unedited
  **this phase**"* is Phase-129-scoped and stays true; no amendment needed there.
  **Rejected:** stating it in the body while leaving `usb_cdc.c` alone — the published artifact
  still presents someone else's identity and everyone who flashes it inherits that.
  **Rejected:** blocking the py32 asset from b15 — loses REL-02's real-cut proof again, and §5(e)
  rates confidence LOW that an allocation is even fileable before a schematic exists.
  **Rejected:** ledger-only with a silent body — the one option where an outward-facing artifact
  omits a known problem, which is the exact shape this phase exists to prevent.

- **D-12: The ledger carries both axes explicitly.** The evidence tier (D-09) groups the rows and
  carries Phase 129's sourcing vocabulary — `[VERIFIED]` / `[CITED: …]` / `[ASSUMED — …]` /
  `[UNVERIFIED-UNTIL-SILICON]` — and each row **additionally** carries a v1.22-style claim status
  (`PERMITTED` / `CONTEXT-ONLY` / `FORBIDDEN`-cited-never-asserted). They answer orthogonal
  questions — where the fact came from versus what may be written about it — and a row can
  legitimately be `PERMITTED` and `[ASSUMED]` at once. Composition with
  `.planning/v1.23-FLASH-PATH-DECISION.md` is **cross-reference only, no data copied**, per that
  record's own line 28 (*"Phase 130's CLOSE-02 honesty ledger consumes the per-claim pairs"*).
  **Rejected:** 129's sourcing tags alone — sourcing does not tell a release-notes author which
  wording is safe. **Rejected:** v1.22's status key alone — drops the sourcing distinction just
  when half this milestone's facts are datasheet citations rather than measurements.

### The ROADMAP renumber — CLOSE-03

- **D-13: The two py32 slots collapse into one pointer line, and v1.23 gains its real SHIPPED entry.**
  `ROADMAP.md`'s `## Milestones` list currently has **no `v1.23 PY32F071 Integration`
  entry at all** — it runs `✅ v1.22` (line 27) straight to `⬜ v1.23 Binary Command Protocol`
  (line 28), with the active milestone existing only as a detail section at line 1993. So: lines 33
  (`v1.28 PY32F071 Port`) and 34 (`v1.29 PY32F071 USB Firmware Install`) collapse into a single
  dated retirement line recording that both were absorbed into v1.23 and pointing at the v1.23
  detail section; the full historical text stays in git history. Line 28 becomes
  `✅ v1.23 PY32F071 Integration — Phases 123–130 (SHIPPED …)`, matching every other shipped
  entry's shape. The stale prior-art paragraph disappears with the entry it lives in, which is the
  propagation hazard `todos/pending/correct-v128-py32-roadmap-prior-art.md` was filed about.
  **Rejected:** deleting both outright — leaves the 999.23/999.24 stubs pointing into a void.
  **Rejected:** keeping both marked RETIRED with bodies intact — the option the todo explicitly
  warns against, since a scoping pass reads the body regardless of the marker.

- **D-14: Binary Command Protocol moves into version order; `v1.30` stays `v1.30`; BCP's stale sequence sentence is annotated.**
  BCP is renumbered v1.23 → v1.28 and **moves** to after v1.27,
  preserving the list's strict version ordering (v1.15…v1.30) rather than breaking it for the first
  time. Its *"Sequence ahead of v1.24 (also breaking)"* sentence gets a short note that the number
  is bookkeeping while the sequence claim is the substance — the project's own stated convention,
  quoted verbatim in two other entries. `v1.29` is left **vacant**, explained by the retirement
  line. The `v1.30` SDP entry is untouched: its own text says to compact *"at activation, not
  now"*, and `/gsd-new-milestone` settles its number anyway. **Rejected:** compacting v1.30 → v1.29
  now — contradicts that entry's written instruction and risks two renumbers disagreeing.
  **Rejected:** a pure renumber with no annotation, leaving unexplained residue.

- **D-15: Backlog stubs 999.23 and 999.24 retire as shipped-into-v1.23, and the v1.29 back-references are corrected.**
  Both stubs' work landed in Phases 123–130, so they retire the way
  999.4–999.7 did when promoted — marked with the phases that delivered them. Their
  *"→ v1.28, leads/follows"* pointers are actively wrong once v1.28 is Binary Command Protocol, and
  the renumber is what breaks them, so fixing them is in scope by consequence. The `v1.30` entry's
  and 999.25's *"the v1.29 slot immediately above"* back-references are corrected to name the
  retirement. **999.22 (→ v1.27) and 999.25 (→ v1.30) are untouched.**
  **Rejected:** retargeting the pointer only — leaves two stubs `⏫ QUEUED` for work that is done,
  so the backlog's open-item count keeps overstating. **Rejected:** leaving the backlog untouched.

- **D-16: The v1.24–v1.27 byte-unchanged claim is proven one-shot, not by a checker.** SHA-256 of
  each of the four entry lines captured **before** the edit and re-hashed after, plus the exact
  path-scoped `git diff` invocation and its output showing zero changed lines in those four, all
  recorded in `130-NONREGRESSION.md`. **A committed checker is deliberately not built**, and the
  reason is recorded so a later reader does not read its absence as an oversight: *"these four
  entries never change"* is false as a standing invariant — those entries **should** change when
  v1.24 is scoped — so a permanent gate would either ship pre-obsolete or block a legitimate edit
  forever. This is the one place in the milestone where BASE-08's ships-with-a-fixture discipline
  would misfire. **Rejected:** a committed checker + fixture. **Rejected:** folding the assertion
  into the CLOSE-01 checker, which would give the combined tool the shorter of two lifetimes.

### Hard sequencing constraints these decisions imply

Not preferences. A plan that reorders any of these breaks a requirement or publishes an unproven
artifact.

1. **`130-DECISION.md` is committed before any push to `beta`** — literal CLOSE-04 text; v1.21's
   close skipped it and auto-cut a stray b12.
2. **The `1209:0001` edit, its `[SHARED:S4]` lockstep body update, and an ARM pass all precede the
   outbound merge** (D-11) — the cut must not publish an image whose descriptor and whose record
   disagree.
3. **`130-LEDGER.md` exists before either release-notes draft is written** — the ledger is the
   single source of the permitted wording both bodies must match (D-02, D-09, D-12).
4. **The blocking operator wording review precedes any body reaching a public release** (D-02).
5. **The observed cut tag is read from `gh release list` after the cut, never computed** — no
   `3.0.0b15` literal may appear inside a command intended to be run verbatim (CLOSE-04, D-01).
6. **The PyPI publish is a manual `workflow_dispatch` with a required `tag` input**, not a side
   effect of the merge — 6 of 13 published app betas never reached PyPI.
7. **Both channels are verified public — PyPI resolution checked directly from a clean temp env,
   never inferred from a green CI tick** — before the phase claims the cut complete (D-01).
8. **The py32 asset presence assertion runs against the real b15 release** (D-03).
9. **CLOSE-01's checker runs against the tree that actually gets merged**, so its result is a
   statement about what was published.
10. **Only the closing plan may tick CLOSE-01…CLOSE-04** — the Phase-116 4× premature-tick guard;
    name the allowed ids in every dispatch prompt.

### Claude's Discretion

- **Every word of both release bodies and of `130-LEDGER.md`**, subject to: the permitted and
  forbidden claims come in substance from the Validation Ceiling; the USB identity statement (D-11)
  is present; PCB-05's socket-empty instruction is present; and nothing is phrased as
  *"verified"*, *"validated"* or *"works end to end"*.
- **The ledger's exact row count, column set and section order** — D-09 fixes evidence-tier
  grouping and D-12 fixes the two axes; the layout is open.
- **Whether `130-LEDGER.md` quotes the ceiling verbatim or cites it by location.** Note the
  self-reference trap: the scanner matches phrase **shape** regardless of quotation context, so a
  ledger that quotes a forbidden phrase to say it is not claimed will trip its own gate — this bit
  all six `125-0N-SUMMARY.md` files. v1.22 solved it by citing the forbidden claim by file:line and
  reproducing only the permitted one.
- **Whether the channel verification is a committed transcript, a small script, or named checks in
  a plan's task list** — only the fact that it ran before the phase claims completion is fixed.
- **Whether any artifact beyond the contracted four is added** — if one is, `_DEFAULT_TARGETS` must
  be amended in the same commit (the scanner's own docstring).
- **Plan ordering**, subject to the ten constraints above.
- **Commit granularity for the R-N corrections** (per-file versus per-correction).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The ceiling and the requirements (read first)
- `.planning/REQUIREMENTS.md` — §**"Validation Ceiling"** (`:8-22`) for the exact permitted and
  forbidden claims, the two-claims-never-conflated rule, and the explicit non-claims to carry to
  close; **CLOSE-01…04 verbatim** (`:102-105`); **PCB-03** (`:96`) and **FUT-N04** (`:116`), the two
  clauses D-06 amends; §**"Future Requirements"** (`:108-123`) for the eight deferral reasons D-10
  needs; the REL-01…04 parentheticals (`:86-89`) for what the release-asset evidence actually is.
- `.planning/ROADMAP.md` §"v1.23 — PY32F071 Integration" → **Phase 130** (`:2461+`) — the four
  success criteria this phase is verified against, plus its **"Ordering note — this phase's push is
  its own gate"** paragraph. Also the `## Milestones` list (`:28-35`), which is CLOSE-03's subject.
- `.planning/research/SUMMARY.md` — §**"Corrections to the Planning Record"** (`:179-202`) for
  **R-1…R-18 verbatim**, §**"Adjudicated Conflicts"** (A-1…A-7, including **A-5**'s
  operator-visible flash-constraint decision the research spine assigns to this phase), and
  §**"What Cannot Be Validated — carry this table forward verbatim"** (`:223-245`), which is the
  raw material for D-09's evidence tiers and D-10's negative space.

### CLOSE-01's targets
- `.planning/PROJECT.md` §"Current Milestone: v1.23" — written **before** the four-stream research;
  carries the stale figures. Gets `⚠ CORRECTION` blocks (D-05), in the same register as v1.22's
  eight.
- `.planning/STATE.md` — §"Milestone Context (v1.23)" already carries a partial
  `⚠ RESEARCH CORRECTIONS` block; edited in place (D-05).
- `.planning/notes/py32f071-port-branch-state.md` — a dated 2026-07-28 capture; gets an
  append-only SUPERSEDED section (D-05). Confirmed to still contain `27 commits behind`, `311eacf`,
  `cli_handlers.py:819` and the `PORTING.md` citation R-8 refutes.
- `.planning/todos/pending/correct-v128-py32-roadmap-prior-art.md` — CLOSE-03 owns it; its header
  note records that v1.23 research re-verified all five corrections and found a sixth (A-6/R-8).

### The honesty ledger's subject matter and shape
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-LEDGER.md` — the
  structural precedent: identity header, status key, claim classes with explicit non-claims,
  mechanism corrections, "what this milestone chose not to prove", "what no test can close", and
  the scanner-status paragraph.
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/122-DECISION.md` — the
  precedent for `130-DECISION.md`: live-measured pre-flight evidence with an AGREES/DRIFTED verdict
  per item, the three-option accept/avoid/cleanup table, the accepted sequence naming each step's
  owning plan, and an explicit "no mutation occurred" section.
- `.planning/v1.23-FLASH-PATH-DECISION.md` — §1.6 (VTOR, the C-1 correction), §4 `[SHARED:S3]`
  (flash budget; §4(b) already carries D-07's narrowed local-versus-CI wording), §5 `[SHARED:S4]`
  (USB identity, the ship gate at `:202`, and the pid.codes terms at `:198`), §6 `[SHARED:S5]`
  (socket-empty), §9 (open questions), and `## Claim ceiling`. Line 28 states this record's
  per-claim pairs are what CLOSE-02 consumes.
- `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` — the firmware subset. **Any `[SHARED:S*]`
  body edit must land identically here** (D-11).
- `firestarter/tests/test_flash_path_record_sync.py` — the 41-leg fail-closed sync gate;
  `_SHARED_KEYS = ("S1"…"S5")`, body-only comparison, `test_shared_sections_match` parametrized
  over all five.

### The claim gate
- `.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py` — the
  v1.23 scanner. Read its **module docstring in full**: `_DEFAULT_TARGETS`' four-name contract,
  D-15's all-or-nothing arming, D-16's 3-line proximity window, the `FIRESTARTER_CLAIMSCAN_TARGETS`
  env seam, and the load-bearing non-claim that a green run is the mechanizable half only.
- `.planning/phases/123-non-regression-baselines-gate-hardening/test_check_permitted_claims.py`
  and `fixtures/` — the BASE-08 pattern D-08's new checker must mirror.
- `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/check_permitted_claims.py`
  — v1.22's original, for the self-reference trap's shape.

### Release mechanics — verify live, do not re-derive from these notes
- `firestarter/.github/workflows/beta-build.yml` — `push: branches: [beta]` with `paths-ignore`;
  `workflow_dispatch` with `beta_version` **and** the permanent `rehearsal` boolean; ARM steps
  `continue-on-error: true` after the `update_version.py` auto-commit; two `files:` entries, the
  py32 one a **glob** (`build/py32f071/firestarter_*.hex`).
- `firestarter/.github/workflows/py32f071.yml` — the **loud** ARM gate; `push: branches: [beta]`
  with no paths filter (MERGE-03). Its header comment records why both ARM builds exist.
- `firestarter_app/.github/workflows/beta-release.yml` — same trigger shape and auto-increment.
- `firestarter_app/.github/workflows/publish.yml` — `on: release: published` **plus**
  `workflow_dispatch` with a **required** `tag`. Its in-file comment records why a PAT-created
  release suppresses `release.published` — the b12 failure mode and the reason D-01's PyPI step is
  a manual dispatch.
- `.planning/phases/128-release-asset-fold/128-NONREGRESSION.md` §2.5/§2.6/§3.2/§3.5/§7 — what
  REL-01…04 actually proved, including REL-03's locally-only half and the deleted rehearsal draft.

### Prior-phase decisions that bind this phase
- `.planning/phases/129-flash-path-decision-pcb-requirements-record/129-CONTEXT.md` — **D-06**
  (`usb_cdc.c` not edited, scoped to that phase), D-09 (the superseded VID/PID premise), and the
  record-shape decisions.
- `.planning/phases/129-flash-path-decision-pcb-requirements-record/129-RESEARCH.md`
  §"Corrections to CONTEXT.md" — **C-1…C-4**, the input to CLOSE-01, and **F-10** (QFN56/QFN32
  cannot carry a contiguous PB0–PB7 bus).
- `.planning/phases/127-host-dfu-installer/127-NONREGRESSION.md` §3/§6/§7 — HOST-03's mock-only
  ceiling, HOST-04's separate mypy-debt failure, HOST-06's UM1504 residual. D-10 needs all three.
- `.planning/phases/122-…/122-CONTEXT.md` — the analogous close's decision set, sequencing
  constraints, and the STATE.md-tooling / premature-tick / bold-label-format warnings in its
  `<code_context>`.

### Project conventions
- `CLAUDE.md` (meta) — repo layout; note its *"Neither sub-repo is committed here"* is imprecise,
  `.gitmodules` exists and gitlinks are tracked (D-04's subject).
- `firestarter/CLAUDE.md` — names the five `[SHARED:S*]` keys (the three-places convention).
- `firestarter_app/CLAUDE.md` — the tooling gate, validated against the **py3.9/3.11 CI targets**,
  not the devcontainer's 3.12.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured live during this discussion (2026-08-02) — re-verify at plan time, do NOT inherit
- **Both sub-repos are on `v1.23-py32f071-integration`**: `firestarter` at `5a89ee7`,
  **83 ahead / 0 behind** `origin/beta` (`5c9160a`); `firestarter_app` at `cc9452f`,
  **37 ahead / 0 behind** `origin/beta` (`e7d3ee8`). **Zero behind in both** — unlike v1.22, there
  is **no inbound catch-up merge and no conflict resolution to plan for**. The outbound merge is
  clean in both repos.
- **Tag ceiling is `3.0.0b14` in both repos**, so the auto-increment target is derivable as b15 —
  but it is **read after the cut, never hardcoded** (D-01, constraint 5).
- **b14 is live on all three surfaces**: GitHub prereleases in both repos (2026-07-30), and PyPI
  carries `3.0.0b14`. Latest stable on PyPI is `2.0.7`. So `pip install --pre firestarter` today
  resolves to b14 — which contains **zero** v1.23 work.
- **Meta gitlinks already match the working tips** — `git ls-tree HEAD` gives `5a89ee7` /
  `cc9452f`. This milestone bumps gitlinks in-phase (Phases 125/128/129), the opposite of v1.22's
  pinned D-07 model. D-04 asserts, it does not re-pin.
- **`gh` is authenticated as `henols`** with scopes `gist, read:org, repo, workflow` — enough for
  `gh release view` / `gh release edit` / `gh workflow run`, though **no task may run
  `gh workflow run` or `git push`** (standing structural gate).
- **`ROADMAP.md`'s `## Milestones` list has no v1.23 PY32F071 Integration entry** — confirmed by
  grep; the only `PY32F071 Integration` hits in the list region are inside line 34's supersession
  marker. D-13 fills that gap.
- **The superseded figures are live**: `2992 B` in ROADMAP/PROJECT/STATE, `27 commits behind` in
  the note + ROADMAP, `311eacf` in the note + ROADMAP + PROJECT, `no VTOR` in
  REQUIREMENTS/STATE/PROJECT/ROADMAP. Some hits are **already inside correctly-labeled blocks**
  (STATE.md's `⚠ RESEARCH CORRECTIONS` legitimately quotes `2992 B`), which is exactly the
  distinction D-08's checker must make.
- **Working-tree dirt to expect** (so a cleanliness assertion does not read pre-existing dirt as
  its own damage): `firestarter_app` carries a modified `.gitignore` plus untracked `.coverage`,
  `.planning/config.json`, `SECURITY.md`, `write_test_port.sh`; meta shows `m firestarter_app`.
- **⚠ `.planning/config.json`'s `planning.sub_repos` lists FOUR repos** — `firestarter`,
  `firestarter_app`, `firestarter_app_py32`, `firestarter_py32_ci`. Any close step that iterates it
  reaches into two py32 scratch worktrees that are **not** part of the deliverable. Iterate the two
  named sub-repos explicitly.

### Reusable Assets
- **`122-LEDGER.md` / `122-DECISION.md`** — the two shapes D-09 and CLOSE-04 follow. Do not
  re-derive their structure.
- **`123/check_permitted_claims.py` + `test_check_permitted_claims.py` + `fixtures/`** — already
  written, already armed, already contracts the four artifact names. D-08's new checker copies its
  fixture-and-pytest pattern, not its phrase table.
- **`test_flash_path_record_sync.py`** — the existing 41-leg cross-repo gate. D-11's `[SHARED:S4]`
  edit is proven by re-running it, not by writing a new gate.
- **`beta-build.yml`'s `rehearsal` input** — permanent by design (128-CONTEXT D-03), available if a
  dry run is ever wanted; D-01 declined it as redundant with run `30722352902`.
- **`115-VALIDATION.md` and `122-CHANNELS.md`** — the shape of a committed channel-verification
  artifact.

### Established Patterns
- **Honesty lives in the message text, never in a status code** (117 D-05, 118 D-02, 119 D-12,
  120 D-11).
- **A reversal is recorded *as* a reversal, with its constraints named** (119 D-18, 120 D-20).
  D-11 reverses Phase 129 D-06 and says so.
- **Every claim is judged against the live measured figure, never a predicted one.**
- **Executors prematurely mark multi-plan requirements Complete** — 4× in Phase 116. Name the
  allowed `CLOSE-NN` ids in every dispatch prompt and re-check `REQUIREMENTS.md` after each plan.
- **STATE.md tooling under-writes and re-clobbers fields.** Call `state.record-session` first, then
  the progress/metric calls, then hand-verify `current_phase`, `current_phase_name`, `status`,
  `stopped_at`, `last_activity_desc` and `progress.percent`.
- **`- **D-NN: text**` must close its bold run on ONE line**, carry at most one colon before the
  closing `**`, and never open with a glyph — otherwise plan-phase's §13a decision-coverage gate
  fails closed.
- **`--auto` / `--chain` auto-approve human-verify checkpoints, and `autonomous: false` does not
  protect an outward-facing gate.** D-02's wording review and the push itself must be gated
  **structurally** — by which plan owns which command — not by a checkpoint type or a flag.
- **A pre-authored gate leg can be UNREACHABLE** (Phase 129's linker-comment locator). RED proves
  nothing until it is seen to pass for the right reason; read failure reasons, and fix locators
  only, with a RED-preserving proof.

### Integration Points
- `.planning/phases/130-…/130-LEDGER.md`, `130-DECISION.md`, `130-RELEASE-NOTES-fw.md`,
  `130-RELEASE-NOTES-app.md` (**all four, contractually**) and `130-NONREGRESSION.md`.
- `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`,
  `.planning/notes/py32f071-port-branch-state.md`, `.planning/REQUIREMENTS.md` — CLOSE-01/03.
- `.planning/todos/pending/correct-v128-py32-roadmap-prior-art.md` → `completed/` once CLOSE-03
  lands.
- `firestarter/platform/py32f071/src/usb_cdc.c` — the two `#define`s plus the source warning
  (D-11).
- `.planning/v1.23-FLASH-PATH-DECISION.md` §5 **and**
  `firestarter/platform/py32f071/FLASH-PATH-AND-PCB.md` `[SHARED:S4]` — lockstep body edit (D-11).
- Both sub-repos' `beta` branches — the outbound `--no-ff` merge that cuts b15.
- `firestarter_app`'s `publish.yml` — one manual `workflow_dispatch` with the **observed** tag.
- Both repos' b15 GitHub prerelease bodies — hand-written, posted after the D-02 review.

### Setup precondition — verify at plan time, do not assume
Both sub-repos must be on `v1.23-py32f071-integration` before any write — confirmed at
`5a89ee7` / `cc9452f` at discussion time. The branch-base check has been a real trap twice
(`project_v121_submodule_branch_base.md`), and this phase additionally **moves `beta`**, so
re-confirm both branch positions, the b14 starting point, and `origin/beta`'s tip immediately
before the merge. After CI runs, local `beta` is one commit behind the remote in each repo (the
version-bump auto-commit) — any later local operation touching `beta` must `git fetch` first.

</code_context>

<specifics>
## Specific Ideas

- **The fact that reshaped this phase: b15 will publish an image presenting another company's
  registered USB vendor identity.** `usb_cdc.c` still defines `0x36B7`/`0xFFFF` — Puya
  Semiconductor's VID, copied verbatim from the pinned SDK's CDC example — while
  `v1.23-FLASH-PATH-DECISION.md` §5(c) carries a hard ship gate saying no release advertises a USB
  identity until an allocated `0x1209` PID exists. Phase 129 declined the edit as a docs-only
  phase; D-01's cut changes the facts, and D-11 lands the interim `1209:0001` rather than
  publishing someone else's identity. This is the single largest scope addition of the discussion.

- **`continue-on-error` means a green CI tick is not evidence the asset shipped.** The ARM steps
  are contained by design so a broken ARM build can never block the three AVR images. The
  consequence, which D-03 refuses to let slide, is that b15 can publish perfectly green with no
  py32 asset at all — and REL-02's only current evidence is a rehearsal draft that was deleted
  after the run.

- **The milestone's one user-visible deliverable has never been exercised for real.** PROJECT.md
  measured it plainly: 21 host capabilities already exist and need landing, 8 items remained to
  build, and **only the release-asset publication gates any user-visible value at all.** Everything
  else in v1.23 is integration. That is why D-01 accepts the cut rather than deferring it.

- **A requirement can be wrong about a fact, not just narrow about a mechanism.** The project's
  standing discipline — satisfy the intent, record the correction, leave `REQUIREMENTS.md` alone —
  was built for mechanisms turning out narrower (LOCK-04, LOCK-06, HOST-04). PCB-03 and FUT-N04
  assert the PY32F071 has no VTOR, which is simply false: the pinned SDK declares
  `__VTOR_PRESENT 1` and the firmware already writes `SCB->VTOR` at every boot. D-06 draws that
  line explicitly so the exception does not read as discipline erosion.

- **The ceiling was wrong in its premise and right in its conclusion.** *"`arm-none-eabi-gcc`,
  `cmake` and `ninja` are absent… unmeasurable locally, by anyone"* is false — the toolchain
  installs here and research built 41/41 objects with it. But local `text=27260` against CI's
  `text=27344` means the conclusion survives for a **better** reason than the premise gave: local
  and CI compilers differ, so absolute sizes are not comparable across them. D-07 narrows rather
  than deletes.

- **The renumber exposed a gap nobody had noticed:** the active milestone has no entry in
  `ROADMAP.md`'s own `## Milestones` list. The list runs `✅ v1.22` → `⬜ v1.23 Binary Command
  Protocol`, and v1.23 PY32F071 Integration exists only as a detail section 1,900 lines down. BCP
  vacating the v1.23 number is exactly what makes room to fix it.

- **This is the one place a fixture-shipping discipline would misfire.** BASE-08 requires every
  checker this milestone introduces to ship with a planted-violation fixture. D-08 obeys it.
  D-16 deliberately does **not build a checker at all**, because "v1.24–v1.27 never change" is
  false as a standing invariant — and records why, so the absence is not later read as an
  oversight.

</specifics>

<deferred>
## Deferred Ideas

### Raised during this discussion, declined with a reason
- **Deleting the stray `3.0.0b12` prereleases.** Not re-opened; declined at v1.22 D-05 because b12
  has been public since 2026-07-27 and may already be installed. If it is ever cleaned up it is an
  operator-driven outward-facing act, not close work.
- **A fresh `rehearsal=true` dispatch before the merge.** Declined at D-01 — run `30722352902`
  already proved the asset publishes, and re-deriving it costs an operator round-trip plus a draft
  cleanup.
- **Compacting the `v1.30` SDP slot into the freed `v1.29`.** Declined at D-14 — that entry's own
  text says to compact at activation, not now, and `/gsd-new-milestone` settles the number anyway.
- **A committed checker for the v1.24–v1.27 byte-unchanged claim.** Declined at D-16 with its
  reason recorded: the invariant is one-shot, not standing.
- **Blocking the py32 asset from b15 on the ship gate.** Declined at D-11 — the interim
  `1209:0001` resolves the conflict without losing REL-02's real-cut proof, and §5(e) rates
  confidence LOW that an allocation is even fileable before a schematic exists.

### Carried forward, still not taken
- **Filing the pid.codes PR for a real `1209:<pid>` allocation.** The operator's act, not an
  agent's (Phase 129 D-08). Its prerequisite is a publicly available repo with modifiable **PCB
  design files**, which may not exist until a schematic does — so the allocation sits downstream of
  the very board the ship gate protects. The ship gate stands regardless of D-11.
- **FUT-N02, FUT-N04, FUT-N05, FUT-N06, FUT-VPP, FUT-CAL, FUT-ORACLE, FUT-ARMSIZE.** D-10 records
  their deferral reasons in the ledger; none is acted on. FUT-N05 (the self-flash bootloader) is
  the seed's primary route and its own milestone; landing the DFU path did not retire it.
- **Phase 129's two open hardware questions** — `nBOOT1`'s factory default (a bad option byte can
  strand a board without SWD) and whether the USB PHY provides an internal D+ pull-up. Recorded,
  not guessed; both `[UNVERIFIED-UNTIL-SILICON]`.
- **F-10's part-selection consequence** — a contiguous PB0–PB7 data bus is physically impossible on
  QFN56 and QFN32 (PB2/PB3 not bonded). Viable packages: LQFP64, CSP64, QFN64, LQFP48, QFN48.
  Recorded as PCB checklist row R3; unrecoverable after layout.
- **The v1.30 SDP milestone's outward-facing debt** — `dev sdp` is named in the gh#12 reply and the
  b14 app release notes, both published 2026-07-30. Owned by
  `todos/pending/gh12-followup-after-dev-sdp-retirement.md`, not by this phase. **No community
  thread gets a comment this milestone**: unlike v1.22, v1.23 has no outstanding reporter and no
  requirement depends on a reply.
- **999.22 (→ v1.27) and 999.25 (→ v1.30)** — untouched by D-15; only the two py32 stubs retire.

### Reviewed Todos (not folded)
`todo.match-phase 130` returned 12 matches, all scoring 0.6 or below on generic keyword overlap —
`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads`,
`avrdude-mcu-detection-fallback`, `cobs-decoder-framelevel-deadline-wr01`,
`decode-infoic-flags-bits-14-15-protect-metadata`, `fix-jp4-labels-and-rev2-revision-block`,
`fold-response-code-into-log-macro`, and others. None is close work. `fold-response-code-into-log-
macro` has now been declined at Phases 118, 119, 120, 121, 122 and here, for the same reason — it
conflicts with 117 D-05 / 118 D-02 / 119 D-12.

**`correct-v128-py32-roadmap-prior-art` is the one substantive hit and is NOT folded — it is
already owned by CLOSE-03 by requirement.** D-13 discharges it; move it to
`.planning/todos/completed/` when CLOSE-03 lands.

</deferred>

---

*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Context gathered: 2026-08-02*
