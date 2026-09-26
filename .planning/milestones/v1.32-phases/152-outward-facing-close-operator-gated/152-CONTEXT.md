# Phase 152: Outward-Facing Close (operator-gated) - Context

**Gathered:** 2026-08-20
**Status:** Ready for planning — **BLOCKED on a precondition, see §Hard Preconditions**

<domain>
## Phase Boundary

The public record for v1.32, and nothing else. Five outward artifacts plus the machine gate over
them:

1. **The owed gh#12 reply** (v1.30's CLOSE-06, held open by design) — OUT-01.
2. **A gh#21 comment** (with #32 folded) — OUT-02.
3. **A gh#11 answer** in terms of the FIX-06 conflation — OUT-03.
4. **Two release-note bodies** (app + firmware) for the v1.32 cut — OUT-04.
5. **A fail-provable claim gate** over all of the above, plus `152-LEDGER.md` — OUT-05.

Plus the in-repo record corrections these force (D-05, D-11, D-15) and the beta merges that make the
announced version exist (D-04).

**This phase also owns the milestone's beta merges** (D-04) — PRs to `beta` in all three repos, the
two CI cuts they fire, and reading the resulting versions. That is a deliberate scope addition taken
at discuss time; see D-04 for what it absorbs and why.

**Not in scope:** any code change in either sub-repo (D-06 — the record corrections land in
`.planning`; the one code comment that needs fixing is assigned to Phase 153); implementing `0x0D`
erase or the write-path blank-check policy (**Phase 153**, D-07); closing gh#21/#11/#12; any
`support_status` change or `0x0D` graduation; rewriting the published `b14` notes; backfilling
`b16`–`b22` bodies (D-02).

**⚠ This phase must NOT be run under `--auto`/`--chain`.** Every OUT requirement is operator-reviewed
before posting, `--auto`/`--chain` auto-approves human-verify checkpoints, and `autonomous: false`
alone is not self-protecting. D-03's per-artifact gates reduce blast radius but do **not** remove this
dependence — the rule stays load-bearing and must be restated in every posting plan's frontmatter.

## Hard Preconditions

**These are not decisions. They are gates on the phase being runnable at all.**

1. **Phase 153 must exist and be COMPLETE before Phase 152 starts** (D-07, D-08). 153 is a new v1.32
   phase, created at discuss time for this milestone, and 152's `Depends on` gains it as a deliberate
   **out-of-number-order** dependency. Creating it is a `/gsd-phase` operation — ROADMAP.md entry with
   goal / depends-on / requirements / success criteria, a new REQUIREMENTS.md section with new
   requirement IDs, traceability rows, and a PROJECT.md workstream row. **None of that exists yet.**
2. **`/gsd-complete-milestone` must be told the merges are already done.** v1.30's close merged via a
   squashed PR, which made `git merge-base --is-ancestor` a **false negative**; never re-merge on that
   signal. Use `git cherry`.
3. **Point the sibling root at an empty dir before any beta push** — the devcontainer's sibling layout
   masks CI-only test defects.

</domain>

<decisions>
## Implementation Decisions

### Publication boundary

- **D-01: Comments are posted inside this phase; release notes are authored version-agnostic.**
  Criteria 1 and 2 use the verbs *"is posted"* and *"carries a comment"*, which Phase 146's
  draft-only boundary cannot satisfy; criterion 4's verb is *"announce"*, which 146 D-13 already
  established is dischargeable by content. **Superseded in sequencing by D-04** — with 152 owning the
  merges, both the comments and the release bodies go public in-phase. The *version-agnostic authoring*
  half survives: the tag is filled in at cut time, never predicted.

  *Measured, and the reason this was a real question:* Phase 146 authored `146-RELEASE-NOTES-app.md`
  and `-fw.md` for `3.0.0b21` and **they were never posted** — `b21`'s body length is `0`. v1.30's
  correction of the `b14` `dev sdp` announcement therefore never reached the public either.

- **D-02: Only the v1.32 cut gets bodies.** One app body, one firmware body. `b16`–`b22` stay
  bodiless — **an accepted cost, recorded not hidden**. The `b14` notes are historical and published:
  they are **not** rewritten; the correction lands in the new notes, per the standing constraint in
  `.planning/todos/pending/gh12-followup-after-dev-sdp-retirement.md`.

  *Measured:* every app release from `3.0.0b16` (2026-08-05) through `3.0.0b22`, and every firmware
  release from `3.0.0b16` through `3.0.0b19`, has `body` length **exactly 0**. `beta-release.yml`
  uses `softprops/action-gh-release@v2` and passes **no `body:`**, so bodies are only ever added
  manually via `gh release edit --notes-file`. The last live notes are `3.0.0b14` (2026-07-30), which
  still publicly announce `firestarter dev sdp <chip> enable|disable` — deleted 2026-08-05 — and still
  say *"An opt-in re-lock after a write is deliberately not part of this release."* **That sentence is
  the forward-looking wording OUT-04 names.**

- **D-03: Per-artifact blocking operator gate, agents post.** A separate blocking checkpoint
  immediately before each post, so approval for gh#12 cannot carry to gh#11. **Accepted cost, stated:**
  the protection is still the checkpoint mechanism the roadmap warns is not self-protecting. Rejected:
  one blocking review for all artifacts (a single approval covering five public acts); agents-never-post
  with a `152-POST-COMMANDS.md` (structurally safest — the capability would be absent rather than gated
  — but rejected by the operator in favour of fewer manual steps).

- **D-04: Phase 152 owns the beta merges, then posts everything.** Merge both sub-repos (and meta) to
  `beta` via PRs, let CI cut, **read** both versions from `gh release list`, then post three comments
  and both release bodies.

  **Why this was forced, and it is the load-bearing measurement of this whole phase:** `origin/beta` —
  the commit that cut `3.0.0b22`, i.e. what `pip install --pre` gives a reporter **today** — still
  carries `fw_board_identity=None` hardcoded at `cli_handlers.py:2514`. The provenance fix exists only
  on the unmerged milestone branch (**67** app commits ahead of `origin/beta`; `vcc_mv` and
  `lock-status` both absent from beta). So criterion 2's request for a fresh run *"stated as answerable
  because the report now identifies its firmware"* would have been **false in every published version**.
  Posting it before the merge is the exact overclaim class this phase exists to prevent.

  **What the phase now absorbs, and the planner must fund each explicitly:**
  - **PRs to `beta`, never direct merges** — v1.31 used fw #52 / app #51 / meta #35; v1.30 used #44.
    Meta gets a PR too but has no release CI, so it cuts nothing.
  - **Two cuts fire, by design.** Every merge to `beta` triggers `beta-release.yml`. Versions are
    **read after the fact**, never predicted. Re-read `origin/beta`'s version before acting on it —
    local `beta` lags.
  - **`git cherry`, not SHA ancestry**, to establish what beta already has. The fw-targeting patches
    landed via PR #52 under different SHAs, and v1.30's squashed merge already produced one
    `--is-ancestor` false negative.
  - **`gh workflow run` is blocked by the auto-mode classifier** — any manual PyPI dispatch is
    operator-only. Settings edits cannot fix it; read-only `gh run` works.
  - **Known CI gotchas at a milestone cut:** codegen drift vs ruff; `.[dev]` vs `.[test]`; PyPI needs
    manual dispatch. Verify the PyPI artifacts independently of GitHub — this project has had GitHub
    carrying betas past PyPI before.

  **Rejected:** split posting (gh#12/#11 now, gh#21 gated on the cut) — one owed carry-forward, and
  this project's carry-forwards have a measured record of never being discharged; posting gh#21 worded
  as *"landed but not yet published"* — softens criterion 2's *"answerable because"* and asks the
  reporter to come back twice.

### The three issue threads

- **D-05: Criterion 2's OPEN list is amended to gh#21, gh#11, gh#12.** **gh#32 is CLOSED** —
  2026-08-08, `stateReason: COMPLETED`, with the operator's own comment *"Folded into #21 — same EPROM
  (at28c256). This report is preserved in the consolidated table there."* That is **10 days before
  v1.32 opened**, so the criterion was already false when written. `"with #32 folded in"` describes
  exactly that state, so the amendment makes the criterion consistent with itself.

  **Same amendment class, same change: `REQUIREMENTS.md`'s OUT-01 and OUT-04 bullets are stale.** They
  still literally read *"`enable` returns as `write --sdp-relock`"* and *"announce `write --sdp-relock`
  and `lock-status` as shipped"*. ROADMAP.md amended both on 2026-08-20 with the Phase 150 deferral;
  the requirements text never followed. **OUT-04's own bullet is therefore currently a violation of
  OUT-05's fifth claim class.**

  Mechanics: dated amendment note, pre-amendment wording retained, as a labelled correction block plus
  a register entry (146 D-05) so `check_record_corrections.py` still tallies it. **Hand-edit ROADMAP.md
  and REQUIREMENTS.md** — the `gsd-tools` requirements/roadmap verbs run `_normalizeMd` over the whole
  file.

  **Rejected:** reopening #32 (un-does a correct `devtest-triage` fold under the very rule that closed
  it, and re-splits a report the consolidated table already preserves); leaving the text alone and
  reading *"still OPEN"* as *"not closed by this milestone"* (stands a criterion whose plain reading is
  false — the exact class this phase's gate exists to catch).

- **D-06: The AT28C256 erase contradiction is stated outward, backlogged, and its premise corrected in the record. No code change in 152.**

  **Established from primary sources during this discussion. Do not re-derive; do not soften.**

  *Datasheet* — Microchip **DS20006386B**, `firestarter_app/datasheets/AT28C256.pdf`, 32 pages. **Two**
  documented erase mechanisms:
  - **Hardware Chip Erase**, a first-class entry in **Table 6-1 Operating Modes (p11)**:
    `CE = VIL`, **`OE = VH = 12.0 V ± 0.5 V`**, `WE = VIL`, I/O High-Z. Waveforms **§6.10 (p15)**:
    `tS = tH = 5 µs` min, **`tW = 10 ms` min**.
  - **Optional software chip erase (p11)**: *"The entire device can be erased using a 6-byte software
    code. See Software Chip Erase application note for details."* **The 6-byte code is NOT in this
    datasheet** — it is in an app note this project does not have.

  *infoic.xml* — the `AT28C256,…,AT28HC256L` record carries `flags = 0x0000C010`, so bit `0x10`
  (**erasable**) is **SET**. Upstream `protocol_id = 0x07`, promoted to `0x0D`; `page_size = 0x40`.
  **infoic and the datasheet agree: the part is erasable.**

  *firestarter* — three surfaces, mutually inconsistent:

  | surface | says | origin |
  |---|---|---|
  | `firestarter info AT28C256` | "Can be erased: **yes** (electrically erasable)" | `firestarter_app/firestarter/ic_layout.py:579` — keys on `electrical.type` only |
  | wire `flags` | **`0`** — `FLAG_CAN_ERASE` clear | `firestarter_app/firestarter/database.py:621` — excludes `algo ∈ {5, 13}` |
  | `firestarter erase AT28C256` | `MSG_ERR_NOT_SUPPORTED` | firmware `configure_eeprom28c` has no erase op |

  **Phase 121 D-12's stated premise is DISPROVEN.** `database.py:591` records the reason for clearing
  the flag as *"advertising `FLAG_CAN_ERASE` for these 84 chips is a **false capability statement**."*
  The capability is real in the silicon and real in infoic. What is false is only that *firestarter*
  can perform it. D-12 made the host claim less rather than making the firmware do more — and
  datapaganism independently hacked a `CMD_ERASE` into `configure_eeprom28c` on 2026-08-03, reaching
  the same conclusion from the other direction. That question on gh#11 was **never answered**.

  152 states this outward, files the backlog items, and corrects the premise **in `.planning`**.

- **D-07: The operator's write/erase policy becomes a NEW PHASE 153 in v1.32.**

  **Policy, verbatim intent:** on protocols where a blank part is *not* required in order to write —
  `0x0D` (28C family) and `0x05` (flash4), which auto-erase per page during the write — **`write` must
  not perform a blank check at all**. And **`erase` and `blank` must each be available as standalone
  steps.**

  Decomposition measured during this discussion:

  | what | where | state |
  |---|---|---|
  | pre-write blank check on `0x0D` | `firestarter/src/proms/eeprom_28c.cpp:517` — `if (!is_flag_set(FLAG_SKIP_BLANK_CHECK)) { mem_util_blank_check(handle); }` | **one conditional**, in the handler |
  | same, `0x05` | `flash_5v_page.cpp` sibling | to locate |
  | `blank` as its own step | `cli_handlers.py:854` + `eeprom_28c.cpp:218` wires `CMD_BLANK_CHECK` → `mem_util_blank_check` | **ALREADY WORKS — nothing owed** |
  | `erase` as its own step | no `CMD_ERASE` arm in `configure_eeprom28c`; `FLAG_CAN_ERASE` cleared for `algo 13` | **missing** |
  | `info`'s "can be erased" row | `ic_layout.py:579` | contradicts the wire flag |

  **⚠ HAZARD for whoever implements erase:** the datasheet's *hardware* path puts **12 V on OE
  (pin 22)** on `DIP28_28C256`. That is precisely what GATE-03 / `tools/check_dispatch.py` exists to
  prevent on a 5 V part, and `check_dispatch.py` is **not to be weakened**. The *software* 6-byte path
  carries no such hazard but needs the app note. **Phase 153 must decide which path it implements and
  fund the GATE-03 question explicitly.**

  Phase 153 also owns the `database.py:591` **code comment** correction, since it must touch
  `database.py:621` anyway to restore `FLAG_CAN_ERASE` (D-15).

  **Rejected:** a backlog item stated outward as queued; landing the one-conditional blank-check half
  inside 152 (would make the close a dual-repo firmware phase mid-merge, needing native tests and a
  cold triple-target size re-measure against **zero** leonardo MERGE-05 headroom).

- **D-08: Phase 153 runs BEFORE Phase 152.** 152's `Depends on` gains 153 as a deliberate
  out-of-number-order dependency. One merge, one cut, one set of release notes, and every claim is true
  at the moment it becomes public.

  **Rejected — and the reasoning is load-bearing:** *152 first, 153 gets its own cut* would post
  `write -b` as the recommended path into the most public artifact this project has, hours after the
  operator declared that check should not exist. Writing a known-superseded workaround into the record
  is exactly the failure class OUT-05's gate exists to catch. *Folding 153's work into 152's merge*
  would draft the close's artifacts against code landing after them, collide with 153 on
  `cli_handlers.py` under one-writer-per-file, and run the close's gates against a moving target.

  **Consequence the gate must absorb:** by the time 152's notes are written, `0x0D` erase and the
  write-path policy **are shipped**, while `write --sdp-relock` still is not. See D-10/D-11.

  **The ask on gh#21, resolved by this ordering.** Measured before the ordering was chosen:
  `chip_test.py:1893` calls `operator.write_eprom(name, eprom_data, tmp_source_path)` with **no
  flags**, and `write_eprom`'s signature defaults `operation_flags: int = 0`, so
  `FLAG_SKIP_BLANK_CHECK` (`0x08`) is never set and the firmware blank-checks at write INIT —
  **`dev test` fails on any non-blank part**, exactly the `Not blank, at 0x000000, v: 0x40` pasted on
  gh#20 with `b15`. The standalone blank-check *step* was already fixed (`chip_test.py` marks it
  `supported=False` for `0x0D`, reason *"auto-erases per page during write; no step in this plan can
  ever leave the device blank"*, quick task `260807-kaq`) **and that fix IS on `origin/beta`** — but
  the write step's own precondition is separate. With 153 landing first, the ask becomes answerable
  rather than a request for a run we already know fails.

### The claim gate (OUT-05)

- **D-09: Two invocation modes, one pattern table — drafts first, then the posted text.**
  - **File mode** (default): hard-coded `_DEFAULT_TARGETS`, offline, CI-runnable. Must pass **before**
    each artifact's per-artifact operator gate (D-03).
  - **Posted mode** (opt-in, network): re-fetch the live body via `gh issue view --json comments` /
    `gh release view --json body` and run the **same** patterns over what actually landed.

  A blob SHA proves what we *intended* to send, never what GitHub stored; and `updatedAt` bumps on
  creation, so it is **not** a body-edit oracle. Re-reading the text is the only sound post-check.

  **Mechanics inherited from `149-check-claims.py`, including its rename discipline:**
  - `_DEFAULT_TARGETS` **enumerated one by one, never a wildcard**. A `152-`-prefixed glob would sweep
    in `152-CONTEXT.md`, `152-RESEARCH.md`, `152-DISCUSSION-LOG.md` (all carrying forbidden vocabulary
    as discussion prose), the fixtures directory (planted violations by design), and the plant-and-revert
    transcript itself (whose RED blocks necessarily quote forbidden text).
  - **Hard-code the paths.** `check_permitted_claims.py`'s `_HERE` resolves to the *checker's own*
    phase directory, so cross-phase reuse scans nothing and **exits 0** — it has already failed open
    once.
  - Env seam **`FIRESTARTER_CLAIMSCAN_TARGETS_152`** — a bare or milestone-suffixed name lets one
    phase's seam retarget another phase's live gate.
  - The `"152-"` self-check literal in **both** the `startswith` call **and** its failure message.

  **Rejected:** drafts only, verified by blob SHA (146 D-10's mechanics — proves intent, not storage);
  live posted text only (catches violations only after they are public, and makes the gate
  network-dependent and unrunnable in CI).

- **D-10: The Phase 153 capabilities are permitted with NO per-claim caveat requirement.**
  **Operator decision.** The concern was raised twice — that nothing then stops *"erase now works on
  AT28C256"* standing unqualified beside a family this project has never had in hand, the drift from
  *"now provable"* to *"now proven"* that v1.22's C-5 correction exists to prevent — and the operator
  resolved it via D-11's amendment rather than by adding the caveat. Proceeding as chosen.

- **D-11: Criterion 5's pairing clause is narrowed, not deleted.** Scope it to claims about `0x0D`
  **write-path correctness or validation status** — the things silicon would have to confirm — and
  explicitly exempt statements of shipped, user-visible command behaviour (*"erase is now available"*,
  *"write no longer blank-checks"*). Dated amendment, pre-amendment wording retained.

  **The five FORBIDDEN classes are UNTOUCHED and the amendment cannot reach them.** AT28C silicon
  validation, page-size validation on silicon, a `0x0D` graduation, a `support_status` change, and
  `write --sdp-relock`-as-shipped all still get rejected — as do *"proven"*, *"confirmed working"*,
  *"datasheet-conformant"*, *"works on silicon"*.

  **Plus, inherited convention rather than a new rule (operator may veto):** each release-note body
  carries the milestone-level non-claim **once** — no AT28C silicon tested, `0x0D` stays `UNVERIFIED` —
  enforced by the gate's `REQUIRED_CAVEAT_PATTERNS` table, which is 149's PGSZ-05 required-phrase
  mechanism reused. `b14` and `b15` both shipped with a *"What is NOT proven"* section; this is where
  v1.22 / v1.23 / v1.31 actually put the honesty-ledger discipline — at the artifact level, not bolted
  to each sentence.

  **⚠ Watch for the 149 collision:** 149's gate carries
  `("proven-unqualified", re.compile(r"(?<!software-)\bproven\b", re.IGNORECASE))` — a negative
  lookbehind added *only* because PGSZ-05 mandates the literal phrase *"software-proven and unvalidated
  on silicon"*. If 152's required caveat uses a different spelling, **re-derive the lookbehind for
  that exact spelling.** Widening it past one prefix silently permits *"bench-proven"*,
  *"datasheet-proven"* and *"silicon-proven"*.

- **D-12: `152-LEDGER.md` is produced AND is a hard-coded gate target.** Follows `137-LEDGER.md` /
  `146-LEDGER.md`: every v1.32 claim with its oracle and its **explicit non-claim**; live-captured
  sub-repo and meta HEADs (measured in-plan, never reused from a prior document's citation); each
  gate/suite named with its own count. Given D-11's narrowing, **the ledger is where the per-claim
  pairing discipline now lives.** Arming the gate at it means the ledger cannot itself overclaim —
  146's gate included its own ledger for exactly this reason.

  **Rejected:** a ledger that is not a gate target (an unscanned internal document is the one most
  likely to state a claim generously); no ledger at all (breaks a three-milestone convention OUT-05
  cites by name).

- **The planted violation is already specified by criterion 5** and is not a discretion item: *the
  pre-amendment criterion-1 wording this roadmap itself carried until 2026-08-20* — the text naming
  `enable` as returning via `write --sdp-relock`. The gate must be **seen to reject it** before any
  pass is believed.

### What may be claimed

- **D-13: `lock-status` is announced with the refusal as the feature.** Lead with what it actually
  does — either report a real state read from silicon, or refuse with a named, actionable reason —
  because on the 28C/SDP family **the honest answer IS the refusal**. Name it **beta-only** and
  **matched-firmware-required**. State that the W29C040 run was an exploratory **probe**, never
  validation.

  *The measurement that decides this (151 D-06/D-09 class sizes — re-derive, do not trust):* **406 of
  746** DB rows have no protection mechanism at all; **111** are documented-not-readable (`0x0D` 84 +
  `0x05` 27); and **no `0x05` row answers by default** (D-06's unanimity rule plus the uncurated
  `W29C022` alias). A named refusal is therefore the command's dominant designed behaviour, and a
  feature paragraph opening *"reports your chip's protection state"* would be wrong for most chips a
  reader tries — an overclaim, in the release notes, about the one command whose entire premise is not
  guessing.

  Firmware dependency to state: it is a new `CMD_*`, and against older firmware the host maps
  `MSG_ERR_UNKNOWN_CMD` → `FirmwareOutdatedError` (151 D-04). So: beta install **plus**
  `firestarter fw --install`.

  **Rejected:** caveats collected in a "NOT proven" section only (a reader skimming the feature
  paragraph may never reach the part saying it refuses on the family they came for); a two-line
  mention (151 spent 288 B of leonardo's last flash headroom and a bench leg on this).

- **D-14: OUT-01's reply ADAPTS `137-GH12-COMMENT.md`, with the diff committed.** Keep its
  *"the two halves don't survive equally, and I'd rather be plain about that"* framing and its *"This
  isn't the 'enable/disable' you asked for. You asked for both, and what you get is one of them
  automatically and none of the other"* paragraph — the hardest sentences to write, and already
  operator-reviewed once. Add: the **second** withdrawal spanning two releases, Backlog **999.28** by
  name, `lock-status`, and Phase 153. Commit the diff against the 137 original so the review sees
  exactly what changed.

  **Omit** a process-failure narration. Criterion 1 already mandates stating the ask is half-answered
  **for a second release**, which discloses the slip in the terms that affect the reporter — what they
  can and cannot do. Narrating our milestone process serves us, not them.

  **Must NOT say** (criterion 1's own negative case): that `enable` returns as `write --sdp-relock`;
  that the v1.30 gap was satisfied all along.

- **D-15: In-repo record corrections, settled by precedent.**
  - `PROJECT.md`'s *"one firmware-touching workstream"* → **three** (149, 151, 153). The v1.32
    roadmap entry and PROJECT.md both carry the stale claim; 151-CONTEXT.md already flagged it and
    said 152's outward text must not repeat it.
  - `PROJECT.md`'s workstream table gains a row for 153; workstream 4's description updates.
  - Phase 121 D-12's disproven premise is corrected in **`.planning`** by 152. The **code comment** at
    `firestarter_app/firestarter/database.py:591` is left to **Phase 153**, which must touch
    `database.py:621` anyway — so 152 never reaches into a sub-repo for a comment edit.

### Claude's Discretion

The operator said "you decide" on these; they are recorded as decisions above with their reasoning:
**D-01** (publication boundary), **D-05** (the gh#32 amendment), **D-08** (153-before-152), **D-09**
(gate scan surface), **D-11** (criterion 5 narrowing), **D-13** (`lock-status` framing), **D-14**
(adapt vs author fresh). Still open to the planner:

- The exact `_DEFAULT_TARGETS` list. Expected: the three comment drafts, both release-note drafts,
  `152-LEDGER.md`, and every `152-*-SUMMARY.md`. **Note the 149 ordering trap** — a SUMMARY cannot be
  added to the default list before it exists on disk, or the never-vacuous guard returns rc=1; 149
  extended its list in its *last* plan for exactly this reason.
- The fixture-suite shape and the plant-and-revert transcript artifact name (146 D-12 required **both**
  fixtures and a real-file plant-and-revert; 149 followed it). A pre-authored gate leg can be
  **unreachable** — RED proves nothing until it is seen to pass, and the fix must be locator-only.
- Plan/wave shape given the phase owns three repo merges and five gated posts, and the
  one-writer-per-file constraint across `.planning` record files.
- What `/gsd-complete-milestone` is left holding once 152 has merged and cut, and how the handoff is
  recorded so nothing re-merges.
- Whether the firmware release notes say anything about the three `.hex` assets and the leonardo
  ceiling.
- Whether `152-LEDGER.md` or a separate correction register carries the D-05/D-11/D-15 amendments.

### Folded Todos

- **`gh12-followup-after-dev-sdp-retirement.md`** — *"Reply on gh#12 (and correct the b14 app release
  notes) after `dev sdp` is retired"*, `resolves_phase: 152`. **Folded — it IS OUT-01.** Its four
  "What the reply must say" points and its four Constraints are binding input to D-14, in particular:
  *"The b14 release notes are historical and already published — correct the **next** release notes,
  do not rewrite the shipped ones"* (→ D-02), and *"Do not name `write --sdp-relock` as an available
  command"* with the required Removed mapping `dev sdp disable` → `write` (automatic) and
  `dev sdp enable` → *withdrawn, no replacement, Backlog 999.28*. Mark it resolved when OUT-01 posts.

- **`write-sdp-relock-deferred.md`** — folded **only for its second obligation half**: *"the shipping
  version's release notes announce it, and gh#12 gets the follow-up it was promised."* That half stays
  **unmet** and must not be presented as met. Its `resolves_phase` is deliberately `none` and stays
  that way. It carries one instruction that outlives this phase: **a future promotion of 999.28 must
  reverse OUT-05's fifth gate class in the same change that lands the feature**, or the gate will
  reject the very release notes announcing it.

- **`at28c256-write-path-failure-gh20.md`** — Backlog 999.29, still open, operator-owned. **Folded as
  outward-facing subject matter only**, not as work: gh#20's own paste is the primary evidence behind
  D-06 and D-08's blank-check finding. Not retired by this phase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The requirements, the ceiling, and this phase's own criteria — read first
- `.planning/ROADMAP.md` §"Phase 152" — the five success criteria, including the `--auto`/`--chain`
  prohibition. **Criteria 1 and 4 were amended 2026-08-20; do not restore the pre-amendment wording.**
  Criteria 2 and 5 are amended by this phase (D-05, D-11).
- `.planning/ROADMAP.md` §"Phase 150" — the deferral record and its **Measured findings** block, so a
  999.28 re-promotion needs no fresh archaeology.
- `.planning/ROADMAP.md` §"Phase 999.28" and §"Phase 999.29" — the two backlog items this close hands
  to.
- `.planning/REQUIREMENTS.md` §"Outward-Facing Close (OUT)" (OUT-01…05, lines ~262-285) — **OUT-01 and
  OUT-04 carry pre-amendment text that D-05 corrects.** §"Out of Scope" carries the
  `write --sdp-relock` deferral row, the *"Reading protection state on `0x0D`/SDP parts"* row (the gap
  OUT-01 must admit to), and the *"Re-litigating RELOCK's verify-failure polarity"* row (decided, not
  reopened).
- `.planning/PROJECT.md` §"Current Milestone: v1.32" — the **Evidence ceiling** block (binding, not
  decorative), the kickoff decisions D-01…D-04, and the **§"⏸ Phase 150 DEFERRED"** record which
  states the outward-facing obligation this phase discharges. **Its "one firmware-touching workstream"
  claim is stale — D-15 corrects it.**

### The outward artifacts' donors and precedents
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md` — **the
  frozen v1.30 gh#12 reply, never posted.** D-14's base. Read in full before authoring.
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-RELEASE-NOTES-app.md` — v1.30's
  authored notes, also never posted. Its "Removed" section is the correct `dev sdp` mapping.
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-LEDGER.md` — ledger shape.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CONTEXT.md` — the
  closest prior close. **D-01** (draft-only publication boundary — superseded here by D-04, read the
  reasoning), **D-02** (version-agnostic bodies), **D-05** (labelled correction blocks plus a
  register), **D-06** (sub-repo edits wording-only), **D-07/D-10** (comment posted, issue stays OPEN,
  body not edited; freeze the artifact and record its blob SHA), **D-11/D-12** (gate armed
  all-or-nothing with per-file caveat rules; proven by fixtures **and** a real-file plant-and-revert),
  **D-14** (forbidden claims cited by location and finding id, never reproduced).
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-LEDGER.md` — the
  ledger to model `152-LEDGER.md` on, including its live-HEAD-capture discipline.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-RELEASE-NOTES-app.md`
  and `-fw.md` — **authored for `b21` and never posted.** Their opening paragraph is the model for the
  version-read discipline (*"read from `gh release list` … never predicted"*).
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-CLAIM-FACTCHECK.md`,
  `146-CORRECTIONS.md`, `146-DOC-CHECK-RECORD.md` — the correction-register shapes.

### The claim gate's donors
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/149-check-claims.py` — **the direct
  donor** (531 lines). Read its module docstring in full: it records the four mandatory renames a
  sibling gate must make, the wildcard-target trap, and the measured `proven-unqualified` lookbehind
  collision. `FORBIDDEN_PATTERNS` at :179, `REQUIRED_CAVEAT_PATTERNS` at :259.
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/test_check_claims_v132.py` and
  `149-CLAIM-GATE-TRANSCRIPTS.md` — the fixture suite and the plant-and-revert transcript shapes.
- `.planning/phases/149-firmware-page-size-seam-dual-repo-lockstep/fixtures/` — planted-violation
  fixtures, incl. `planted_at28c256_fixed.md`.
- `.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/146-check-claims.py` — the
  ancestral gate, and `146-check-close03-docs.py` — the sub-repo documentation checker.
- `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py` — **the
  gate that failed OPEN.** Its `_HERE` resolves to the checking phase's own directory. Read to know
  what not to do.

### The four issue threads (live state, captured 2026-08-20)
- [gh#12](https://github.com/henols/firestarter_prom/issues/12) — *"AT28Cxxx Write Protection
  Enable/Disable missing"*, opened 2024-09-15, **OPEN**, 10 comments. Its **2026-07-30** comment
  publicly states `firestarter dev sdp <chip> enable|disable` *"gives standalone control in both
  directions"* — the claim v1.30 deleted 2026-08-05 and never retracted.
- [gh#21](https://github.com/henols/firestarter_prom/issues/21) — *"[dev test] at28c256 — FAIL
  (00e121446ceb)"*, **OPEN**, 2 comments: the consolidated-reports table folding #32, and the
  `devtest-triage` datasheet cross-check that cleared the data outright.
- [gh#32](https://github.com/henols/firestarter_prom/issues/32) — **CLOSED 2026-08-08**,
  `stateReason: COMPLETED`, folded into #21. Same fingerprint `00e121446ceb`. **D-05.**
- [gh#11](https://github.com/henols/firestarter_prom/issues/11) — *"Issues with AT28C256 Reading /
  Writing"*, opened 2024-09-26, **OPEN**, 18 comments. Its **2026-07-30** comment already answers
  FIX-06 verbatim (*"That is a conflation, not a sampling-rate shortfall"*). **Unanswered:
  datapaganism's 2026-08-03 question about `erase not supported` and hacking a `CMD_ERASE` into
  `configure_eeprom28c`.** Also carries AndersBNielsen's 2025-09-28 page-write analysis.
- [gh#20](https://github.com/henols/firestarter_prom/issues/20) — CLOSED, but its 2026-08-07 pastes on
  `b15` are the primary evidence for D-06 and D-08: `firestarter erase AT28C256` → `ERROR: Not
  supported`, and `dev test`'s write failing `Not blank, at 0x000000, v: 0x40`.

### The erase finding's primary sources (D-06, D-07)
- `firestarter_app/datasheets/AT28C256.pdf` — Microchip **DS20006386B**, 32 pages. **Table 6-1
  Operating Modes, p11** (the `Chip Erase` row and its `VH = 12.0 V ± 0.5 V` note); the **OPTIONAL
  CHIP ERASE MODE** paragraph, **p11**; **§6.10 Chip Erase Waveforms, p15**. Reading it needs
  `pip install pypdf 'cryptography>=3.1'` — the file is AES-encrypted and `pdftotext` is absent from
  this devcontainer.
- `firestarter_app/firestarter/database.py` :565-625 — `FLAG_CAN_ERASE` derivation, the
  `algo not in (5, 13)` exclusion at :621, and the **Phase 121 D-12 REVERSAL RECORD** at :591 whose
  premise D-06 disproves.
- `firestarter_app/firestarter/ic_layout.py` :578-585 — the `can_erase_str` derivation that keys on
  `electrical.type` only.
- `firestarter/src/proms/eeprom_28c.cpp` — :226 (`CMD_BLANK_CHECK` → `mem_util_blank_check`),
  **:547-548** (the pre-write blank check Phase 153 removes), :104 (a comment already naming gh#11's
  shape).
- `firestarter_app/firestarter/chip_test.py` — :1893 (the flagless `write_eprom` call), :605-670 (the
  blank-check placement logic and `_AUTO_ERASE_ON_WRITE_PROTOCOLS`, quick task `260807-kaq`).
- `firestarter_app/firestarter/eprom_operations.py` :1872-1880 — `write_eprom`'s
  `operation_flags: int = 0` default.
- `firestarter_app/firestarter/constants.py` :122 — `FLAG_SKIP_BLANK_CHECK = 0x08`.
- `firestarter_app/tools/check_dispatch.py` — GATE-03. A hardware-damage guard, **not to be weakened**;
  the 12 V-on-OE erase path must be adjudicated against it in Phase 153.

### The release mechanism (D-02, D-04)
- `firestarter_app/.github/workflows/beta-release.yml` — its header comment records that **every merge
  to `beta` cuts a pre-release, by design**; `softprops/action-gh-release@v2` at :105 with **no
  `body:`**, which is why `b16`–`b22` are bodiless. `target_commitish` resolution at :94-108; the PyPI
  upload job at :114-125.
- `firestarter_app/CLAUDE.md` §"Database Pipeline" — the **WARNING-5 protocol override** that promotes
  AT28C256 from upstream `0x07` to `0x0D`, and why 12 V on that pinout's pin 1 is a damage path.

### What shipped in v1.32, for the notes to describe accurately
- `.planning/phases/147-*/147-VERIFICATION.md` — PROV-01…06.
- `.planning/phases/148-*/148-VERIFICATION.md` and `148-DB-DIFF.md` — the 56-chip 4000→5000 mV
  `RULE_VCC_MARGIN_RAIL` change, `vcc_mv`/`vdd_mv`/`vpp_mv`/`pulse_duration_us`.
- `.planning/phases/149-*/149-PAGE-SIZE.md` — the seam. **Load-bearing non-claim: AT28C256 carries
  `page_size 64`, exactly today's floor, so this phase cannot change its behaviour at all and explains
  nothing about gh#21.**
- `.planning/phases/151-*/151-CONTEXT.md` and `151-VERIFICATION.md` — `lock-status`, its eight class
  tokens, D-03's probe-not-validation cap on the W29C040 leg, and the note that v1.32's
  "one firmware-touching workstream" self-description is out of date.
- `.planning/phases/151-*/151-BENCH.md` — the W29C040 probe result.
- `firestarter_app/doc/lockable-proms.md` — the protection table's source, for anything the notes say
  about readability.

### Todos
- `.planning/todos/pending/gh12-followup-after-dev-sdp-retirement.md` — folded, IS OUT-01.
- `.planning/todos/pending/write-sdp-relock-deferred.md` — second obligation half folded; carries the
  gate-class reversal instruction for a future 999.28 promotion.
- `.planning/todos/pending/at28c256-write-path-failure-gh20.md` — Backlog 999.29, subject matter only.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`149-check-claims.py`** — the gate to sibling. 531 lines, with its rename discipline documented in
  its own docstring. Eleven of its twelve forbidden patterns transcribe unchanged; the twelfth
  (`proven-unqualified`) carries a measured negative lookbehind that must be **re-derived** for 152's
  own required phrase (D-11).
- **`test_check_claims_v132.py` + `149-CLAIM-GATE-TRANSCRIPTS.md`** — the paired fixture-suite and
  plant-and-revert-transcript shapes, already proven in this milestone.
- **`137-GH12-COMMENT.md`** — a complete, once-reviewed gh#12 reply. D-14's base.
- **`146-LEDGER.md` / `137-LEDGER.md`** — the ledger structure, including per-gate counts and
  live-captured HEADs.
- **`146-RELEASE-NOTES-app.md`'s opening paragraph** — the version-read discipline, verbatim reusable.
- **`gh` CLI, read-only** — `gh issue view --json comments`, `gh release view --json body`,
  `gh release list`. All used live during this discussion; all available. `gh workflow run` is **not**
  (auto-mode classifier).

### Established Patterns
- **Versions are read, never predicted.** Every prior release-notes artifact opens by naming where the
  version was read from and when.
- **Corrections land as labelled correction blocks plus a register entry**, never as a silent edit —
  `check_record_corrections.py` tallies `{block, line-label, inline-history, inline-allow, superseded}`.
- **Forbidden claims are cited by location and finding id, never reproduced** (146 D-14) — which is
  also why the transcript artifact must stay out of `_DEFAULT_TARGETS`.
- **A gate is not believed until it is seen to fail on a planted violation**, and a pre-authored gate
  leg can be structurally unreachable — the fix must be locator-only.
- **Outward-facing acts are operator-gated separately**, because `--auto`/`--chain` auto-approves
  human-verify checkpoints and `autonomous: false` is not self-protecting.
- **Hand-edit ROADMAP.md and REQUIREMENTS.md.** The `gsd-tools` requirements/roadmap verbs run
  `_normalizeMd` over the whole file.

### Integration Points
- **Three repos, three PRs to `beta`** — `firestarter` (fw), `firestarter_app` (host), meta. Both
  sub-repos are on `gsd/v1.32-at28c-write-path-root-cause-report-provenance`; the app is **67 commits**
  ahead of `origin/beta`. Executors commit **inside** each submodule; use `commits_land_in:` in plan
  frontmatter — worktrees leave submodules empty and the gate under-detects.
- **Two CI cuts**, one per sub-repo merge. Meta cuts nothing.
- **`.planning` record files** are the phase's main write surface: ROADMAP.md, REQUIREMENTS.md,
  PROJECT.md, plus the new phase-152 artifacts. One-writer-per-file applies across plans.
- **`STATE.md` is a 339 KB file with very long lines** — the record gate needs a **300 s** timeout on
  it; a short timeout returns rc=124 and reads like a RED.

### Measured live during this discussion (2026-08-20) — re-verify at plan time, do NOT inherit
- `origin/beta` app: `fw_board_identity=None` at `cli_handlers.py:2514`; no `vcc_mv`; no `lock-status`.
  **67** commits behind the milestone branch.
- Release body lengths: app `b14` 4490, `b15` 4856, **`b16`–`b22` all 0**; fw `b14` 5257, `b15` 8841,
  **`b16`–`b19` all 0**. App latest pre-release **`3.0.0b22`** (2026-08-19), stable **2.0.8**; fw
  latest pre-release **`3.0.0b19`** (2026-08-18).
- `leonardo`: `flash_used` **27500**, `flash_total` 32768, `flash_free` 5268; MERGE-05 delta vs
  `base01` **+594 ≤ 594** — exactly zero headroom; three stacked exemptions 96 + 210 + **288**;
  **1172 B** below the **unguarded** 28672 B Caterina cliff.
- `AT28C256` DB row: `algorithm: 13`, `infoic_page_size_raw: 64`, `type: EEPROM`, `vcc_mv: 5000`,
  `support_status: "supported"`. **Note:** the chip-level `support_status` is `supported` while the
  *protocol* ledger has `0x0D` as `UNVERIFIED` — two different axes. **No outward artifact may cite
  `support_status: supported` as evidence about the write path.**
- `infoic.xml` `AT28C256` record: `protocol_id 0x07`, `flags 0x0000C010` (bit `0x10` erasable **SET**),
  `page_size 0x40`, `write_buffer_size 0x80`, `chip_id 0x00000000`.

</code_context>

<specifics>
## Specific Ideas

- **The single most important sentence in this phase** is the one that says the ask is half-answered
  *for a second release*. gh#12 was opened 2024-09-15 by someone who had to build a separate Arduino
  to disable SDP before Firestarter could write at all. v1.30 removed the surface; v1.32 was the
  milestone scoped to restore it and did not. Getting this wrong would be the milestone failing its
  own stated purpose in its most public artifact, for the second release running.
- **datapaganism is the only real-silicon evidence this work has ever had**, has said *"happy to test
  for you"*, and asked to be replied to on the issue rather than Discord. Two of their questions have
  gone unanswered: the 2026-08-03 `CMD_ERASE` question, and implicitly the 2026-08-07 `erase → Not
  supported` dead end. Phase 153 answers both by making the thing work; 152's job is to say so
  truthfully.
- **`137-GH12-COMMENT.md`'s "This isn't the 'enable/disable' you asked for"** paragraph is the tonal
  target for all three comments: name the shortfall before naming the gain.
- The `b14` release notes remain live and wrong. They are **not** edited (D-02) — but the next notes'
  "Removed" section is the only place a reader ever learns that, so it must be findable, not buried.

</specifics>

<deferred>
## Deferred Ideas

- **Split or trimmed AVR firmware builds to relieve the leonardo ceiling** — raised by the operator
  during this discussion. Its own phase; **do not fold into 152 or 153.** Measured live at the
  milestone tip so a future phase needs no re-measurement: `leonardo` `flash_used` **27500 B**,
  `flash_total` 32768, `flash_free` 5268; the **Caterina USB-bootloader cliff at 28672 B** leaves only
  **1172 B** usable and is **UNGUARDED** — past it, the USB bootloader bricks; MERGE-05 delta vs
  `base01` is **+594 ≤ 594**, i.e. *exactly* zero headroom, funded by three stacked named exemptions
  (96 defect-fix + 210 page-size-seam + **288** `lock-status`-read).
  Two facts make it more tractable than 151 D-01 implied: `-D DEV_TOOLS` lives in the shared `[env]`
  block at `firestarter/platformio.ini:26` and is inherited by `uno`, `uno328pb` **and** `leonardo`
  (which is why 151 D-01 recorded that no `#ifdef` makes firmware code free) — **and**
  `platformio.ini:194` already carries `[env:native_nodevtools]`, which omits it and is proven
  DEV_TOOLS-invariant semantically. So the build mechanism exists; it has simply never been wired to an
  AVR target or a released `.hex`. A two-`.hex` split, or a `leonardo_nodevtools` target, interacts
  with `fw --install`'s asset naming, `--board` matching, and the channel gate — which is exactly why
  it is its own phase. A related idea was already declined once: a compensating bootloader-safe flash
  guard, raised when quick task `260820-a7w` removed the linker's protection over the bootloader
  region.
- **Backfilling `b16`–`b22` release bodies**, including posting `146-RELEASE-NOTES-app.md`/`-fw.md` to
  `b21` where they were always meant to go. Declined by D-02. v1.31's 27C work is currently announced
  nowhere.
- **A `--json` output mode for `lock-status`, and folding lock state into `dev test` reports** — 151's
  deferred idea, unchanged. D-08's class tokens keep it cheap later.
- **A live protection read for protocol `0x10`** (39 rows, Intel command-register) — ships as
  `not_implemented`.
- **Curating `W29C022`** — would flip the `W29C020,W29C020C,W29C022` entry to answerable with no rule
  change. Needs a datasheet, not an inference.
- **Obtaining the Atmel/Microchip *Software Chip Erase* application note** — it holds the 6-byte
  software erase code, which is the hazard-free path for Phase 153's erase. Not in
  `AT28C256.pdf`.
- **`write --sdp-relock`** — Backlog **999.28**, deferred twice. Not this phase, not Phase 153. A
  future promotion **must reverse OUT-05's fifth gate class in the same change that lands the
  feature.** RELOCK's verify-failure polarity (skip-and-report-loudly) is decided and travels with the
  requirements; a re-promotion does not reopen it.

### Reviewed Todos (not folded)

`todo.match-phase 152` returned **25** matches. The six at 0.9 are all firmware items matched on
generic tokens (`phase`, `read`, `gate`, `version`, `date`) plus an `area: firmware` bonus — score
noise, not signal. Reviewed and **not** folded:

- **`prove-pio-dev-flag-fails-closed.md`** — *adjacent and newly more interesting*: it would prove the
  PlatformIO dev-tools flag fails CLOSED, and the split-firmware deferred idea above depends on exactly
  that property. Still its own task, and not outward-facing.
- **`runtime-info-log-naming-the-effective-page-size.md`**, **`phase-44-read-timing-knobs-missing-json-parse-reset.md`**,
  **`fm1608-byte0-write-never-lands-register-cache-elision.md`**,
  **`config-version-not-bumped-strands-stale-eeprom-calibration.md`**,
  **`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md`** — firmware defects,
  unrelated to the outward record.
- **`fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md`** — a `0x0D` classification question
  (Phase 149 D-04). Worth a look from **Phase 153**, since FRAM parts riding `0x0D` would be affected
  by a blank-check policy change and `sdp_capability.FRAM_TOKENS` already refuses two of them. Not 152.
- **`promoted-0x0d-rows-keep-the-64-byte-floor.md`** — Phase 149's page-size floor; its measured part
  lists are input to what the notes may say, but the todo itself stays open.
- **`vcc-5500-high-margin-verify-rail-group.md`** — Phase 148's deferred 28-chip group, filed with its
  part list. Unchanged.
- **`onerom-pinout-external-corroboration-gate.md`** — an independent pinout oracle; unrelated axis.
- **`record-gate-superlinear-on-state-md-single-line.md`** — **operationally relevant**: it is why the
  record gate needs a 300 s timeout in this phase, but fixing it is not 152's work.
- **`explore-seeds-invisible-to-new-milestone-glob-mismatch.md`** (0.4) — GSD tooling.
- The remainder (`avrdude-mcu-detection-fallback`, `build-db-diff-ladder-state`,
  `cobs-decoder-framelevel-deadline`, `delete-jp5-dead-renderer`, `fix-jp4-labels`,
  `fold-response-code-into-log-macro`, `gsd-plan-scan-loose-plan-regex`, `photograph-modified-rev-0`,
  `spike-databuffer-size-speed-delta`, `write-modifications-md-rework-trace`) matched on generic
  tokens only.

</deferred>

---

*Phase: 152-outward-facing-close-operator-gated*
*Context gathered: 2026-08-20*
