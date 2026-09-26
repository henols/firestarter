# Phase 139: gh#15 Correction (outward) — Research

**Researched:** 2026-08-09
**Domain:** Outward-facing publication — a public GitHub issue correction, drafted → frozen → operator-gated → posted, with every claim citation-resolved
**Confidence:** HIGH (nearly every finding was measured live this session against the live GitHub API, the live repos, and executed probes; only two items are MEDIUM and both are flagged)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

Copied verbatim from `139-CONTEXT.md` §Implementation Decisions. **Discussion mode:** the operator
delegated all four gray areas — *"you decide, do the best decisions to finalize the EPROM protocols."*
Every decision below is Claude's call. They are **decisions, not suggestions** — downstream agents
implement them rather than re-open them.

**Comment shape & mechanism**

- **D-01: One comment is the deliverable; the issue-body edit is a frozen, named, *optional* second
  action offered at the same gate.** ISSUE-01/02/03 speak of "a gh#15 comment", and the comment alone
  discharges all three. But gh#15 was authored by the operator himself (`author: henols`, created
  2026-07-12, **zero comments** — verified live this session), so amending the body is available here
  in a way it never is on a stranger's issue. The plan therefore **drafts and freezes both**:
  (a) the comment, and (b) a ready-to-apply body amendment — a dated `⚠ AMENDED` block at the **top**
  of the body pointing at the comment, plus the acceptance-criteria list replaced by the corrected
  list, with **gh#15's original list preserved verbatim** in a collapsed `<details>` block.
  Both are presented at the single `checkpoint:human-action` gate; **the body edit is skipped by
  default** and applied only on a separate, explicit yes.
  **Rationale:** a stranger — or an agent — who implements gh#15 reads the *body*, not the comments,
  and stopping exactly that is D-03's stated purpose ("Stops anyone implementing `50000 us`"). But
  rewriting a filed spec without the original visible destroys the public record, and an outward
  action beyond what ISSUE-01…03 ask for must never happen by default.
  *Rejected:* comment-only with no body edit even drafted; body edit as a default action.

- **D-02: Voice carries forward from `137-GH12-COMMENT.md`** — first person, plain-spoken maintainer,
  no hedging, no corporate register. Framed explicitly as **self-correction**: *I filed this; two
  numbers in it are wrong and one premise is inverted.* That framing is honest and available here in
  a way it is not when correcting someone else, and it forecloses any reading of the comment as a
  rebuttal of a contributor.

**Amendment scope**

- **D-03: Full amendment — including the architecture criterion, not only the two numbers.** The
  comment proposes a **rewritten acceptance-criteria list mapped item-for-item onto gh#15's original
  seven boxes**, each marked *kept* / *corrected* / *replaced*, with the reason. It states plainly
  that gh#15's *"each protocol must own its programming state machine and timing constants"* is
  **replaced**: protocol owns *shape*, the database owns the *pulse* (milestone D-01) — and gives the
  measured reason, that no protocol has a single pulse width (`0x07` n=170 spans 50–1000 µs;
  `0x08` n=127; `0x0B` n=32).
  **Rationale:** leaving the architecture criterion uncontested would force Phase 146's CLOSE-04 to
  mark three or four acceptance boxes "met-as-corrected" against a public spec that was never
  publicly corrected. Half-correcting a spec is worse than not correcting it, because it looks complete.
  *Rejected:* numbers-only (C1/C2/C3), leaving gh#15's separate-handlers architecture standing.

  > ⚠ **See F-01 below — "seven boxes" is wrong. gh#15 carries NINE. The "four conflict" count is right.**

- **D-04: The comment publishes the corrected design's *shape*, not per-value datasheet
  attributions.** It states the parameter table's columns (`max_pulses`, `overprogram_factor`,
  `overprogram_cap_us`, `verify_mode`, `vpp_path`), the **no-pulse-column** rule,
  `handle->pulse_delay` on every write path with protocol constants surviving only as
  `pulse_delay == 0` fallbacks, the `0x0B` 50 ms accumulated-energy cap with no overpulse, and
  hard-fail-on-max-pulses with address + pulse count reported. **Every numeric row is marked
  proposed** — per-value datasheet citation is TABLE-04's job in Phase 140 and does not exist yet.
  Do not present proposed rows as datasheet-attributed.

- **D-05: The comment already complies with the Phase 146 claim gate, before that gate exists.** No
  unqualified "datasheet-conformant" / "datasheet-correct" / "algorithm-accurate". The ~6.25 V
  program-VCC ceiling gets **its own paragraph, not a footnote**, naming what the milestone buys
  (timing / pulse-count / verify fidelity) and what it explicitly does not (silicon-margin fidelity),
  and naming which of gh#15's implied criteria are **not reachable on this hardware**. Check it
  mechanically with `check_permitted_claims.py` — **but read the landmine in Code Insights first**:
  its `_HERE` resolves to the *checker's own* phase directory, so naive cross-phase reuse scans
  nothing and exits 0, a false green.

  > ⚠ **See F-04 below — the landmine is worse than stated and the v1.30 checker CANNOT do this job.
  > Proven by execution this session.**

**Evidence & citation**

- **D-06: Condensed evidence inline; full evidence one permalinked click away; every claim carrying
  `file:line` or a commit SHA (ISSUE-01's literal requirement).** Inline: the three per-protocol
  histogram lines and each one's disagreement with gh#15's constant — that is the actual payload.
  **Not** inline: the full `138-02-PULSE-DISTRIBUTION.md` dump. Citations, each resolved before posting:
  - **C1** → `firestarter_app/doc/infoic-field-dictionary.md:210-217` (the adjudication) **plus the
    commits**: `8de307f` *"feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts
    (DEC-03)"* and `12286df` *"feat(57-03): regenerate chip_database.json from corrected build_db.py"*.
  - **C2** → `138-02-PULSE-DISTRIBUTION.md` + the **runnable** `138-pulse-distribution.py` +
    `firestarter_app/firestarter/database.py:128` (`_parse_pulse_duration`) + minipro `t48.c:250-267`.
  - **C3** → `firestarter/src/proms/eprom.cpp` anchors (`:20` `NUMBER_OF_RETRIES`, `:69-77` the
    `pulse_delay == 0` fallback, `:177` the adaptive growth formula, `:283` the pulse) and
    `delayMicroseconds()`'s 16383 µs ceiling against the `3 × 25 × 1000 µs = 75 ms` overprogram pulse.

  > ⚠ **See F-02 below — `eprom.cpp:283` is the ERASE pulse. The program pulse is `memory.cpp:329`.**

- **D-07: Citations pin to commit SHAs, never branch names — and permalink reachability is a hard
  posting precondition, measured rather than assumed.** `henols/firestarter_prom` is **PUBLIC** and
  carries `.planning/`. At the currently pushed meta tip **`b6aa1dcb`**, `138-02-PULSE-DISTRIBUTION.md`
  ✓, `138-pulse-distribution.py` ✓ and `PROJECT.md`'s C1/C2/C3 table ✓ all resolve — but
  **`138-BASELINE.md` does not**: it landed in `baa131a3`, and six meta commits are **unpushed**. The
  plan must push the v1.31 meta branch (or pin every link to a newer *pushed* SHA), then **fetch each
  permalink back and confirm it resolves** before posting. A correction whose evidence 404s is worse
  than no correction — it reads as fabricated.

  > ⚠ **See F-05/F-06 — now EIGHT unpushed commits; `PROJECT.md`'s table LINE NUMBERS shift by 10
  > between the pushed tip and HEAD; and the push is itself an operator-owned outward act.**

**Posting gate & what unblocks Phase 140**

- **D-08: The gate is the operator's *wording review*, not the network call.** Phase 140 must never
  start against an **unreviewed** draft. Posting is the default and expected outcome of the same gate.
  If the operator approves the wording but explicitly says *hold the post*, Phase 140 **may proceed
  under a recorded, named exception** written into both the phase record and the ROADMAP entry, so
  Phase 146's CLOSE-04 reconciles against what actually happened. ISSUE-03 stays **open** in that
  branch, with the exact one-command follow-up recorded in the `.planning/v1.30-OPERATOR-BATCH.md`
  A-1 shape. What must never happen: silently posting, silently skipping, or starting implementation
  against a draft nobody read.
  *Rejected:* hard-blocking the whole milestone on a network call the operator may simply be away from.

- **D-09: `checkpoint:human-action`, never `checkpoint:human-verify`.** `--auto`/`--chain`
  auto-approve every `human-verify` gate but never `human-action`; the `autonomous: false` frontmatter
  flag alone is **not** self-protecting. Copy `137-05-PLAN.md`'s task shape wholesale.
  **Phase 139 must not be run under `--auto`/`--chain`.**

- **D-10: Posting re-verifies the "before implementation" claim mechanically.** Confirm
  `firestarter/src/proms/eprom.cpp` is untouched at posting time via `git status --porcelain` on the
  file rather than inferring it from phase order. After any post: fetch the comment back and byte-diff
  it against the frozen file, and confirm gh#15 is still `OPEN`. If the body edit was also authorized,
  read the body back and confirm the original list survives verbatim in its `<details>` block.

**Community ask**

- **D-11: One short, specific ask — and only one.** The `0x0B` one-shot-vs-looped question is **not
  answerable from source**: minipro never runs the algorithm, it packs `pulse_delay` into a
  `BEGIN_TRANS` message and hands it to closed TL866/T48/T56/T76 firmware — so D-02's 50 ms energy cap
  is *reasoned*, not *derived*, and the comment must say so. Invite a datasheet or logic-analyzer
  correction, and name the parts this milestone cannot guarantee bench coverage for (M2716/M2732 for
  `0x0B`, AM27C020 for `0x08` — opportunistic per the operator's inventory, D-08 of the milestone).
  Four lines, at the end, matching 137's close.

### Claude's Discretion

- Exact comment prose, section order, and headings within the decisions above.
- Whether the corrected acceptance-criteria list renders as a markdown checklist or a table.
- Whether the frozen comment gets a byte-identity gate of its own, or relies on the blob-SHA +
  byte-length freeze that `137-05-PLAN.md` used.
- Plan and wave structure. The natural shape is three tasks mapping 1:1 onto `137-05-PLAN.md`:
  draft + freeze + verify every permalink resolves → blocking operator gate → conditional
  post-or-hold, each branch recorded.
- Where the frozen artifacts live, subject to the naming precedent (`139-GH15-COMMENT.md` mirrors
  `137-GH12-COMMENT.md`; the body amendment wants its own file so the freeze covers each separately).

### Deferred Ideas (OUT OF SCOPE)

- **Per-value datasheet attribution for the parameter table** — TABLE-04, Phase 140. Phase 139
  publishes the table's *shape* and marks every numeric row **proposed** (D-04).
- **Item-by-item reconciliation of gh#15's acceptance criteria as met / met-as-corrected /
  not-reachable** — CLOSE-04, Phase 146. Phase 139 *proposes* the amendment; Phase 146 *reports*
  against it.
- **Release notes describing the programming-behavior change** — CLOSE-05, Phase 146.
- **The claim gate itself** (`check_permitted_claims.py`, armed and seen to fail on a planted
  violation) — CLOSE-01, Phase 146. Phase 139 *complies* with its forbidden-claim list (D-05) but does
  not build or arm the gate.
- **Reviewed todos not folded:** gh#12 follow-up (v1.30 CLOSE-06, a different milestone's requirement);
  VPP skip-checks-when-unused (Phase 142); AT28C256 gh#20 (different family); Phase 31 photo/MODIFICATIONS
  follow-ups; v1.30 close (already discharged, PR #44 squashed to `568e58b` — **never re-merge**);
  `dev test` triage skill (unrelated).

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `REQUIREMENTS.md:111-118`) | Research Support |
|----|---------------------------------------------------|------------------|
| **ISSUE-01** | A gh#15 comment states C1 (`0x0B` is 500 µs; `50000 us` is the ×100 BUG-2 fingerprint Phase 57 removed), C2 (pulse width is a database datum, with the PREP-04 distribution) and C3 (the safe delay helper is for the 75 ms overprogram pulse), each citing its evidence by `file:line` or commit. | §"Citation Register" — all 11 citations resolved live at pinned public SHAs, with corrected anchors for C3 (F-02) and a corrected C2 framing (F-03). §"C1/C2/C3 Substance" reproduces the correction table verbatim. |
| **ISSUE-02** | The same comment states the ~6.25 V program-VCC ceiling plainly and proposes the specific amendment to gh#15's acceptance criteria that it requires. | §"gh#15 Live State" carries all **nine** acceptance boxes verbatim with a kept/corrected/replaced disposition and the two extra non-checkbox directives that must also be corrected (F-01). §"The 6.25 V Ceiling" carries the three canonical statements verbatim. |
| **ISSUE-03** | The comment is frozen, operator-approved for wording, and posted **only** on explicit operator authorization — and posted before any implementation phase lands the new loop. | §"Architecture Patterns" gives the 137-05 three-task shape and the 122-12 *actually-executed* posting + byte-diff recipe. §"D-10 Mechanical Precondition" gives a false-green-proof "eprom.cpp untouched" assertion. §"gh CLI Mechanics" gives the exact argv, the correct fetch-back endpoint, and the permission caveat. |
</phase_requirements>

---

## Summary

Phase 139 has no code to design. Its entire difficulty is **making a public correction whose every
factual claim survives a reader checking it** — while gating an irreversible outward act behind a
human. Research therefore concentrated on two things: (1) reading gh#15 live and resolving every
citation the comment will carry, and (2) extracting the two worked precedents this project already
owns for gated outward publication.

Both precedents are real and directly reusable. `137-05-PLAN.md` is the *gate* precedent — a three-task
draft → `checkpoint:human-action` → conditional-post shape, with a fail-closed branch that freezes and
records a follow-up rather than posting. `122-DELIVERY.md` §3 is the *posting* precedent, and it is
strictly better than 137-05's because it **actually executed**: four outward calls, each byte-verified
after the fact, with the exact normalization recorded ("GitHub appended exactly one trailing newline").
137-05's byte-diff recipe was never run. Use 137-05 for structure and 122-DELIVERY for mechanics.

**The research found six defects that would have made the plan wrong**, all measured rather than
inferred. gh#15 has **nine** acceptance-criteria boxes, not the seven CONTEXT.md and ROADMAP both
state — and D-03's whole deliverable is an item-for-item mapping onto them. `eprom.cpp:283`, listed as
C3's "the pulse" anchor, is the **erase** pulse inside `eprom_internal_erase()`; the program pulse is
`memory.cpp:329`, in a different file. PROJECT.md's and STATE.md's summary claim "all three gh#15
constants disagree with the modal value" is **false for `0x08`**, where gh#15's `100 us` *is* the mode
(104 of 127) — copying that sentence into a public comment beside a link to the distribution that
disproves it is precisely the credibility failure the correction exists to prevent. The v1.30
`check_permitted_claims.py` **cannot** perform D-05's check: proven by execution, a naive copy exits 0
`UNARMED`, and an explicitly-targeted run reports PASS on a file containing four forbidden overclaims
because its proximity gate requires an `AT28C`/`SDP`/`0x0D` token that a gh#15 comment never contains.
Eight meta commits are unpushed (not six), and `PROJECT.md`'s C1/C2/C3 table sits at lines **61-63** at
the pushed tip versus **71-73** locally — an HTTP 200 proves a file exists at a SHA, never that the
line range says what you claim. Finally, `git push` is an operator-owned act in this project by its own
Phase 138 precedent, which means D-07's "the plan must push" needs its own gate — or, better, can be
avoided entirely, because `138-BASELINE.md` is the only citation that does not already resolve and it
appears nowhere in D-06's binding citation list.

**Primary recommendation:** Plan three tasks on the `137-05-PLAN.md` skeleton; drop `138-BASELINE.md`
from the citation set so **no push is required and the phase's only outward act is the post itself**;
pin every sub-repo citation to `origin/beta` (all four cited files are blob-identical there and at the
milestone tip) and every meta citation to `b6aa1dcb`, verifying each anchor by fetching raw and
`sed`-slicing the pinned line range rather than trusting a 200; replace the C3 anchor set with the
corrected `memory.cpp:329`; restate C2 with the honest per-protocol *wrong-pulse counts* (203 of 329
chips) instead of the false "all three disagree with the modal value"; and implement D-05 as a small
Phase-139-scoped forbidden-phrase check seen to fail on a planted violation, **not** by reusing the
v1.30 checker.

---

## Architectural Responsibility Map

This phase is a documentation/publication pipeline, not a runtime system. Tiers map to artifact
custody rather than to servers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Comment + body-amendment authoring | Meta repo `.planning/phases/139-*/` | — | `commits_land_in:` is the meta repo; CONTEXT.md §Phase Boundary forbids any sub-repo commit |
| Evidence generation | Phase 138 artifacts (already committed) | — | C2's evidence exists and was pre-formatted for this audience; Phase 139 quotes, never re-measures |
| Citation resolution / permalink verification | Local `git` + `curl` against `raw.githubusercontent.com` | `gh api` for commit objects | Read-only, agent-safe, no permission barrier |
| Forbidden-claim scan (D-05) | Phase-139-local checker script | — | The v1.30 checker is domain-incompatible (F-04); a new narrow one is proportionate and CLOSE-01 owns the real gate |
| Wording approval | **Operator** (`checkpoint:human-action`) | — | Irreversible public act; `--auto` never auto-approves `human-action` (D-09) |
| Posting authorization | **Operator** | — | Distinct authorization from wording approval; gate them together but record two separate answers (137-05 Task 2 shape) |
| The `gh issue comment` network call | Operator, or agent **after** an explicit permission grant | — | Not in the allowlist and state-changing → auto-mode classifier risk (F-07) |
| Post-hoc verification | Agent, read-only `gh api` / `gh issue view` | — | Always permitted; the whole byte-diff proof is automatable |
| Follow-up parking if held | `.planning/v1.30-OPERATOR-BATCH.md` §A-1 shape (or a v1.31 equivalent) | ROADMAP Phase 140 `Depends on:` line | D-08's named-exception branch must land in **both** places |

---

## Project Constraints (from CLAUDE.md)

`/workspaces/CLAUDE.md` is a repository-structure and system-overview document; it contains no
prohibitions that bear on Phase 139. Three of its statements are still load-bearing here:

1. **This repo tracks only `.planning/` and `.claude/`.** Neither sub-repo is committed here — which is
   exactly why CONTEXT.md's "no submodule commit is expected or permitted" is structurally enforceable.
2. **`firestarter/` and `firestarter_app/` are separate repos with their own CLAUDE.md files.** Any
   citation into them must resolve in *their* GitHub repos (`henols/firestarter`,
   `henols/firestarter_app`), not in `henols/firestarter_prom`. Both verified PUBLIC.
3. **Constants and protocol are duplicated across `constants.py` / `firestarter.h` and
   `serial_comm.py` / `firestarter.cpp` and must change together.** Phase 139 changes neither, but the
   comment's D-04 shape description should not imply a host change that Phase 143 has not made.

**Project skills** (`.claude/skills/`): `devtest-triage`, `devtest-rootcause`, `skill-writer`,
`find-skills`. None applies to an issue-correction phase. `devtest-triage`/`devtest-rootcause` are for
`dev test` chip reports (gh issues 23-32), a different issue class from gh#15.

---

## F-nn: Findings That Would Make the Plan Wrong

These are the highest-value output of this research. Each was measured, not inferred.

### F-01 — gh#15 has **NINE** acceptance-criteria boxes, not seven `[VERIFIED: gh issue view 15, live 2026-08-09]`

`139-CONTEXT.md` §canonical_refs and the research brief both say "seven acceptance-criteria boxes".
`grep -c '^- \[ \]'` over the live body returns **9**. D-03's entire deliverable is a list "mapped
item-for-item onto gh#15's original seven boxes" — a nine-box reality means a seven-row mapping is
missing two rows, and Phase 146's CLOSE-04 would then reconcile against an incomplete amendment.

**The "four of them conflict" count in CONTEXT.md is correct** — see the disposition table below.
Only the *total* is wrong.

### F-02 — `eprom.cpp:283` is the **erase** pulse, not the program pulse `[VERIFIED: source read + grep, firestarter @ fb7949c0]`

D-06 lists `firestarter/src/proms/eprom.cpp:283` as C3's anchor for "the pulse". Line 283 is:

```cpp
283:    delayMicroseconds(handle->pulse_delay);
```

…but it sits inside `eprom_internal_erase()` (opens at line 274), two lines above the comment
`// After the erase pulse, we should disable the chip to end the programming cycle.` It is the **only**
`delayMicroseconds()` call in `eprom.cpp`.

The **program** pulse is in a different file:

```cpp
// firestarter/src/proms/memory.cpp — memory_set_data(), opens at 249
256:    rurp_chip_enable();
257:    delayMicroseconds(handle->pulse_delay);
258:    rurp_chip_disable();
```

`grep -rn 'pulse_delay' src/ include/` confirms the complete usage set: `json_parser.c:503` (wire
ingest), `eprom.cpp:69-77` (fallback), `eprom.cpp:161/172/177/178` (adaptive growth), `eprom.cpp:283`
(erase), `memory.cpp:329` (**program**), plus `eeprom_28c.cpp` (a different family).

**Consequence:** `program_mismatched_bytes()` (`eprom.cpp:114-126`) contains **no delay at all** — the
per-byte program pulse is applied inside the `firestarter_set_data` function pointer, which
`memory.cpp:86` binds to `memory_set_data`. A comment citing `eprom.cpp:283` as the program pulse is
checkably wrong, and a reader who follows the link lands in the erase function.

**Corrected C3 anchor set:** `eprom.cpp:20`, `eprom.cpp:69-77`, `eprom.cpp:177`, **`memory.cpp:321-330`**
(and optionally `eprom.cpp:283` explicitly labelled *the erase pulse* — which is itself relevant, since
`handle->pulse_delay` doing double duty as both program and erase pulse is a real design observation).

### F-03 — "All three gh#15 constants disagree with the modal value" is **false for `0x08`** `[VERIFIED: arithmetic over the 138-02 histograms]`

That sentence appears verbatim in `PROJECT.md:72` and in `STATE.md` (C2 bullet). It is not in the seed
(`27c-algorithm-fidelity-param-table-refactor.md`), which correctly presents the distribution and the
gh#15 constant side by side without editorializing. The summary added the error.

| protocol | n | modal width | gh#15 constant | constant == mode? | chips the constant gets **wrong** |
|---|---|---|---|---|---|
| `0x07` | 170 | **100 µs** ×113 (66.5%) | `1000 us` | **no** | 148/170 (87.1%) |
| `0x08` | 127 | **100 µs** ×104 (81.9%) | `100 us` | **YES** | 23/127 (18.1%) |
| `0x0B` | 32 | **500 µs** ×21 (65.6%) | `50000 us` | **no** | 32/32 (100.0%) |
| **total** | **329** | | | | **203/329 (61.7%)** |

Posting "all three disagree with the modal value" next to a permalink to the distribution that shows
`0x08`'s mode *is* 100 µs is a self-inflicted wound: the one claim a skeptical reader can check in ten
seconds would be the one that is wrong.

**The honest framing is stronger anyway**, because it does not depend on the mode at all:

- No protocol has a single pulse width. `0x07` takes 5 distinct values (50, 100, 200, 500, 1000 µs);
  `0x08` takes 6 (10, 20, 50, 100, 200, 1000); `0x0B` takes 3 (200, 500, 1000).
- Under gh#15's three constants, **203 of 329 chips (61.7%) would be programmed at the wrong width.**
- Even choosing the *corrected* modal `0x0B` value of 500 µs as a constant still mis-programs 11 of 32
  (34.4%) — which is the actual argument for the database owning the pulse.

Also worth stating: `0x08`'s constant being right *by coincidence* is the sharpest illustration of the
point. Getting the right answer from the wrong model is not a defense of the model.

### F-04 — The v1.30 `check_permitted_claims.py` **cannot** perform D-05's check `[VERIFIED: executed this session, 5 probes]`

D-05 says "Check it mechanically with `check_permitted_claims.py` — but read the landmine … `_HERE`
resolves to the *checker's own* phase directory". The landmine is real, and there are **two more**.

| Probe | Setup | Result | Verdict |
|---|---|---|---|
| A | Naive copy of the file into a Phase-139-like dir, default targets | `UNARMED: none of Phase 137's 4 named closing artifacts exist yet …` → **exit 0** | **False green**, exactly as D-05 warns |
| B | `python3 check_permitted_claims.py 139-GH15-COMMENT.md` on a draft containing *four* overclaims | `FAIL: 1 missing required silicon caveat … 'no AT28C silicon was tested'` → exit 1, **zero forbidden hits reported** | Fails for an irrelevant v1.30 reason; detection half silent |
| C | Same via `FIRESTARTER_CLAIMSCAN_TARGETS_V130=` env seam | Identical to B | Env seam does not help |
| D | File containing `no AT28C silicon was tested` *adjacent to* the overclaims | `FAIL: 2 forbidden phrase match(es): confirmed-working, verified-on-silicon` → exit 1 | Detection works **only** with an AT28C/SDP token adjacent |
| E | Same two overclaims, with `Protocol 0x07 programs each byte…` as context instead | **`PASS: scanned probe2.md` → exit 0** | **Completely vacuous green** |

Three independent incompatibilities:

1. **`_HERE` trap** (D-05's own warning) — `_DEFAULT_TARGETS` is built from `_HERE`; in a new directory
   all four v1.30 filenames are missing, and the `used_defaults and len(missing) == len(targets)`
   branch at `check_permitted_claims.py:304-312` prints `UNARMED` and returns 0.
2. **Wrong required caveat.** `REQUIRED_CAVEAT_PATTERN = r"no\s+AT28C\s+silicon\s+was\s+tested"`
   (line 179-181). A gh#15 comment about 27C EPROMs has no business asserting that. Any
   explicitly-targeted run therefore **fails on a criterion that does not apply**.
3. **Proximity gate makes detection vacuous.** `_SDP_CONTEXT_TOKENS = r"at28c\w*|\bsdp\b|0x0d"`
   (line 110); a forbidden match is only recorded if that token appears within ±1 line
   (`scan_text`, lines 222-226). gh#15's vocabulary is `0x07`/`0x08`/`0x0B` — **none of the three tokens
   ever appears**. Probe E proves the consequence.
4. *(bonus)* The v1.30 `FORBIDDEN_PATTERNS` list contains **zero** occurrences of the string
   `datasheet` (`grep -c 'datasheet' → 0`). D-05's own three forbidden phrases —
   "datasheet-conformant", "datasheet-correct", "algorithm-accurate" — are simply not in it.

**Recommendation for the planner:** do **not** copy, fork, or env-seam the v1.30 checker. Write a
small Phase-139-scoped script (`139-check-claims.py`, ~40 lines) that:
- takes its target(s) as **explicit argv only**, with a hoisted never-vacuous guard (`if not targets:
  exit 1`) copied from the v1.30 mechanics (lines 288-295) — that part is sound and worth reusing;
- carries the **v1.31** forbidden vocabulary (`datasheet[-\s]conformant`, `datasheet[-\s]correct`,
  `algorithm[-\s]accurate`, plus `verified on silicon`, `confirmed working`, `proven`, and any
  unqualified `datasheet-` compound);
- applies **no** proximity gate (the whole file is on-topic — a proximity window has nothing to buy here
  and everything to lose, per probe E);
- requires a **v1.31** caveat pattern instead of the AT28C one — the natural choice is the 6.25 V
  ceiling sentence, which ISSUE-02 requires anyway, making the gate and the requirement the same check;
- is **seen to fail on a planted violation before its pass is believed** — binding per ROADMAP's v1.31
  must-not-do list *and* Phase 138's Run 1 house style.

This is compliance with CLOSE-01's spirit, not a build of CLOSE-01. It stays inside the deferred-ideas
boundary because it forbids and requires nothing beyond what ISSUE-02 and D-05 already state, and it
scans exactly one or two files.

### F-05 — Eight unpushed meta commits; `PROJECT.md` line anchors shift by 10 `[VERIFIED: git + live raw.githubusercontent fetch]`

```
$ git rev-parse HEAD                                    → cbc66d602dde3f1975e58161c27b0276f4ce0a53
$ git ls-remote --heads origin | grep v1.31              → b6aa1dcb23ef9931105752ed6dd6badccf6719de
$ git log --oneline origin/gsd/v1.31-…..HEAD | wc -l     → 8
```

CONTEXT.md recorded six (`baa131a3` … `78904a0e`); two more have landed since (`d849597d`,
`cbc66d60`). Reachability at the pushed tip `b6aa1dcb`, measured by HTTP:

| path | status @ `b6aa1dcb` |
|---|---|
| `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md` | **200** (and byte-identical to local) |
| `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | **200** |
| `.planning/PROJECT.md` | **200** |
| `.planning/phases/138-preconditions-baseline/138-BASELINE.md` | **404** |

**But an HTTP 200 does not validate a line range.** `PROJECT.md`'s C1/C2/C3 table is at
**lines 61-63** at `b6aa1dcb` and at **lines 71-73** in the working tree. A permalink written from local
line numbers (`…/blob/b6aa1dcb/.planning/PROJECT.md#L71-L73`) resolves with a 200 and points at the
**wrong ten lines**. GitHub's `#Lnn` fragment is client-side; no request ever validates it.

`138-02-PULSE-DISTRIBUTION.md` is byte-identical at tip and local, so its anchors (237 / 243 / 247 for
the three histogram lines) are stable.

**Verification recipe the plan must use — content, not status code:**

```bash
verify_anchor() {  # url  first  last  expected-substring
  curl -sf "$1" | awk -v a="$2" -v b="$3" 'NR>=a && NR<=b' | grep -qF "$4" \
    && echo "OK   $1#L$2-L$3" || { echo "FAIL $1#L$2-L$3"; return 1; }
}
```

### F-06 — `git push` is an operator-owned act here; and it may not be needed at all `[VERIFIED: 138-BASELINE.md §1; v1.30-OPERATOR-BATCH.md A-2]`

`138-BASELINE.md` §1 records, of Phase 138's own pushes: *"Two outward actions occurred, both taken by
the **operator**, per Task 1's `checkpoint:human-action` gate … No agent ran `git push`,
`gh workflow run`, `gh pr create`, `gh pr merge` or `git merge` at any point in this plan."* The v1.30
operator batch classifies the branch push identically ("Outward-facing, so left for the operator").

So D-07's "the plan must push the v1.31 meta branch" is **not** a task an executor can simply run. It
would need its own `checkpoint:human-action` — a second outward gate in a phase designed around one.

**But D-07 offers the alternative — "or pin every link to a newer *pushed* SHA" — and it is free here,
because `138-BASELINE.md` is the only artifact that 404s and it appears nowhere in D-06's binding
citation list.** D-06 enumerates C1's, C2's and C3's citations exhaustively; `138-BASELINE.md` appears
only in CONTEXT.md's looser §canonical_refs "Evidence being cited" list. Drop it and **the phase needs
no push at all** — its single outward act becomes the post itself, which is exactly the shape D-08
describes.

If the planner nonetheless wants `138-BASELINE.md` cited, note two mitigations: the meta-branch push
fires **zero CI** (see below), and everything it would prove is already in
`138-02-PULSE-DISTRIBUTION.md`, which already resolves.

**Meta-repo push is CI-free** `[VERIFIED: .github/workflows/]`. The meta repo has exactly one workflow,
`catalog-sync-check.yml`, triggering on `push`/`pull_request` to **`main` only**, filtered to paths
`tools/catalog/**` and the workflow file itself. Pushing `gsd/v1.31-27c-programming-algorithm-fidelity`
fires nothing. (Contrast `firestarter`, where the Phase 138 push fired two runs.)

### F-07 — `gh issue comment` / `gh issue edit` are not allowlisted and are state-changing `[VERIFIED: settings.local.json; CITED: memory reference note]`

`.claude/settings.local.json`'s allow list contains exactly five `gh` entries:
`gh repo create *`, `gh run:*`, `gh release:*`, `gh workflow:*` (twice). **`gh issue` is absent.**

The recorded project finding
(`reference_gh_workflow_run_blocked_by_automode_classifier`, corrected 2026-08-09 during Phase 138) is
that a *separate* auto-mode classifier layer blocks state-changing `gh` regardless of the allowlist,
while read-only `gh run list` / `gh run view` / `gh auth status` execute fine — and that **the operator
can lift it**, after which the identical command succeeds first try. The agent must not attempt to
self-unblock (no settings edits, no `gh api --method POST` workaround).

**`gh auth status` (live):** logged in as `henols`, token scopes `gist, read:org, repo, workflow`. The
`repo` scope **is** sufficient for commenting on and editing an issue in a public repo owned by that
account. So the *token* is not the constraint; the classifier is.

**Plan implication:** the posting task must offer both paths at the gate — "grant the permission and I
run it", or "here is the exact one-line command, run it yourself" — and the verification half is fully
automatable either way, because every fetch-back call is read-only.

**Not verified (would require posting):** whether the classifier actually blocks `gh issue comment` in
this specific session. Rated MEDIUM by analogy to `gh workflow run`. The plan should assume blocked and
be pleasantly surprised, never the reverse.

### F-08 — `git submodule status` fails unconditionally in this repo `[VERIFIED]`

```
$ git submodule status
fatal: no submodule mapping found in .gitmodules for path '.planning/v1.7/upstream-rurp'
```

Any verification step using it exits non-zero for an unrelated reason. Use `git ls-tree HEAD <path>` or
per-repo `git -C <repo> …` instead.

---

## gh#15 Live State (read 2026-08-09)

```
$ gh issue view 15 --repo henols/firestarter_prom --json title,state,author,createdAt,updatedAt,comments,labels
```

| Field | Value |
|---|---|
| Title | *Implement protocol-specific EPROM programming algorithms in firmware* |
| State | **OPEN** |
| Author | **`henols`** (Henrik Olsson — the operator) |
| Created | **2026-07-12T09:15:27Z** |
| Updated | **2026-07-12T09:15:27Z** — identical to created, so the body has **never been edited** |
| Comments | **0** |
| Labels | none |
| Body size | 5964 bytes |
| URL | https://github.com/henols/firestarter_prom/issues/15 |

Every fact CONTEXT.md asserts about gh#15 is confirmed **except the acceptance-box count**. The
`updatedAt == createdAt` equality is a useful extra: it means a body edit (D-01's optional second
action) would be the first modification ever made, and `updatedAt` becomes a free post-hoc proof that
it happened.

### The nine acceptance-criteria boxes, verbatim

> ```markdown
> ## Acceptance criteria
>
> - [ ] `0x07`, `0x08`, and `0x0B` use separate write handlers.
> - [ ] No new database algorithm flags are introduced.
> - [ ] `EPROM_STD` uses per-byte fixed 1 ms pulse/verify cycles and a final overprogram pulse.
> - [ ] `EPROM_QUICK` uses its own fixed short-pulse handler.
> - [ ] `EPROM_LEGACY` uses a long fixed programming pulse rather than the current adaptive loop.
> - [ ] The current block mismatch/adaptive pulse-growth algorithm is removed from EPROM writing.
> - [ ] VPP routing remains protocol-correct and is disabled on all exits.
> - [ ] Native tests cover dispatch, pulse behavior, verification, failure, and cleanup.
> - [ ] All firmware targets build successfully.
> ```

Copy this block into `139-GH15-BODY-AMENDMENT.md`'s `<details>` verbatim. It is the "original must
survive" artifact of D-01 and §Specific Ideas.

### Proposed disposition — D-03's item-for-item mapping

Four conflict, five are kept. This is the planner's starting table; wording is Claude's discretion.

| # | gh#15 box (abbreviated) | Disposition | Reason to state publicly |
|---|---|---|---|
| 1 | `0x07`/`0x08`/`0x0B` use **separate write handlers** | **REPLACED** | Milestone D-01: protocol owns *shape*, the DB owns the *pulse*. One shared per-byte pulse→verify loop driven by a `const` table keyed by `protocol_id`. Three state machines duplicate ~80-85% of their body (seed §Reuse split) on a device with a hard AVR flash budget. |
| 2 | No new database algorithm flags | **KEPT** | Unchanged; TABLE-05 enforces it with a committed gate. |
| 3 | `EPROM_STD`: per-byte **fixed 1 ms** pulse/verify + final overprogram | **CORRECTED** | The per-byte loop and the overprogram pulse are kept — this is gh#15's central and correct insight. The **`1 ms` is wrong**: `0x07`'s modal DB value is 100 µs (113 of 170) and it spans 50-1000 µs. Pulse comes from `handle->pulse_delay`. |
| 4 | `EPROM_QUICK` uses **its own** fixed short-pulse handler | **CORRECTED** | "Its own handler" falls with box 1. "Fixed" falls with C2 — `0x08` spans 10-1000 µs across 6 distinct values, and 23 of 127 chips are not 100 µs. gh#15's 100 µs happening to equal the mode does not make it a constant. |
| 5 | `EPROM_LEGACY` uses a **long fixed** pulse rather than the adaptive loop | **CORRECTED** | Dropping the adaptive loop is kept. **`long` is wrong**: C1 — the 50 ms figure is the ×100 BUG-2 artifact; true modal value is 500 µs. Also: gh#15's body says *"Do not retain the current generic 500 us legacy default"* — that instruction is exactly backwards and must be named. |
| 6 | Block mismatch/adaptive pulse-growth algorithm removed | **KEPT** | gh#15's core diagnosis, endorsed. Pulse count and overprogram duration belong to the individual byte, which a block mismatch-mask cannot express. |
| 7 | VPP routing protocol-correct and disabled on all exits | **KEPT** | Unchanged (VPP-01…03). |
| 8 | Native tests cover dispatch, pulse behavior, verification, failure, cleanup | **KEPT** (scope adjusted) | Kept; "dispatch" now means table-row selection rather than handler selection. |
| 9 | All firmware targets build successfully | **KEPT** | Unchanged. |

**Two body directives outside the checkbox list that the amendment must also correct** — a reader
implementing gh#15 obeys these as readily as the boxes:

- §*Required design*: *"The handlers may share low-level electrical primitives, but **each protocol
  must own its programming state machine and timing constants**."* — **REPLACED**, and D-03 names this
  one explicitly.
- §`0x0B`: *"**Do not retain the current generic 500 us legacy default.**"* — **REVERSED**. 500 µs is
  correct; `50000 us` is the bug. This sentence is the single most dangerous line in the issue after
  the `pulse: 50000 us` default itself, because it pre-emptively forbids the right answer.

**Two of gh#15's own numbers are load-bearing *in the correction's favour* and should be cited as
such:** its `0x07` defaults `maximum pulses: 25`, `overpulse multiplier: 3`, `maximum overpulse:
75000 us`. C3's arithmetic (`3 × 25 × 1000 µs = 75 ms`) is gh#15's own figure — the comment is not
importing an outside number to make its point.

**ISSUE-02's "amendment that the ceiling requires":** boxes 3, 4 and 5 as written imply datasheet
*algorithm* fidelity. The 6.25 V program-VCC gap means no implementation on this shield can claim
silicon-margin fidelity, so the amended list must carry an explicit not-reachable-on-this-hardware
qualifier attached to those three (and to the implied whole).

---

## C1 / C2 / C3 Substance — reproduced verbatim, do not paraphrase

From `.planning/PROJECT.md` §"Current Milestone: v1.31", **local lines 71-73** (= **lines 61-63** at the
pushed tip `b6aa1dcb` — see F-05):

> | | gh#15 states | Correction (evidence) |
> |---|---|---|
> | **C1** | `0x0B` pulse = `50000 us` | **500 µs.** `50000 = 500 × 100` is the fingerprint of **BUG-2**, a ×100 multiplier `interpret_timing()` applied to `0x07`/`0x0B`, affecting 252 chips, removed in Phase 57. The shipped DB reads `500 us` for AM2716. Adjudicated at `firestarter_app/doc/infoic-field-dictionary.md:210-217`. Cross-checked: `AT28C64B` → 10000 µs = 10 ms (its datasheet byte-write); `DS1225` NVRAM → 1 µs. A ×100 would make the 28C64 1 s/byte. |
> | **C2** | Hardcode `1000 / 100 / 50000 µs` into three handlers | **Pulse width is DATA, not a per-protocol constant.** Measured live against the shipped DB on 2026-08-08: `0x07` n=170 (**100 µs ×113**, 200×27, 1000×22, 500×4, 50×4); `0x08` n=127 (**100 µs ×104**, 50×11, 10×7, 200×2, 1000×2, 20×1); `0x0B` n=32 (**500 µs ×21**, 1000×6, 200×5). All three gh#15 constants disagree with the modal value. minipro ships `protocol_id` and `pulse_delay` as **two orthogonal wire fields** (`t48.c:250-267`, identical in `tl866a.c`, `tl866iiplus.c`, `t56.c`, `t76.c`) and exposes `-o pulse=N` per run — a uint16, so 65535 µs is the hard ceiling. |
> | **C3** | Need a 32-bit-safe delay because of the 50 ms pulse | Helper is still needed, **for the overprogram pulse** — `3 × 25 × 1000 µs = 75 ms` exceeds `delayMicroseconds()`'s 16383 µs ceiling. With C1 applied, no *pulse* comes near it. |

> ⚠ **C2's sentence "All three gh#15 constants disagree with the modal value" must NOT be carried into
> the public comment — see F-03.** Everything else in the table is verified correct. The seed
> (`27c-algorithm-fidelity-param-table-refactor.md` §C2) states the same evidence without that sentence
> and is the safer source to draft from.

**Structural consequence (milestone D-01), verbatim, `PROJECT.md`:**

> **Structural consequence (D-01):** protocol owns *shape*; the database owns the *pulse*. That is a
> parameter table, not three state machines — the opposite of gh#15's "each protocol must own its
> timing constants". `handle->pulse_delay` stays on the write path; protocol constants survive only as
> fallbacks for `pulse_delay == 0` (`eprom.cpp:70-77`).

**`0x0B` energy cap (milestone D-02), verbatim, `PROJECT.md`:**

> **`0x0B` energy-budget cap (D-02)** — the one-shot-vs-looped question is *not answerable from
> source*: minipro never runs the algorithm, it packs `pulse_delay` into a `BEGIN_TRANS` message and
> hands it to closed TL866/T48/T56/T76 firmware. Resolution shipped: loop pulse→verify but **cap
> accumulated program time per byte at 50 ms**, since `100 × 500 µs = 50 ms` is exactly the classic
> 2716 total programming time. Early-verifying bytes exit fast; stubborn bytes still receive the
> datasheet's full energy budget. No overpulse on this row.

### C3, strengthened — the AVR argument is harder than "exceeds 16383" `[VERIFIED]`

`delayMicroseconds()`'s documented accurate ceiling is **16383 µs** (Arduino official reference: *"The
largest value that will produce an accurate delay is 16383"*). But the AVR core signature is:

```c
// framework-arduino-avr/cores/arduino/Arduino.h:144
void delayMicroseconds(unsigned int us);
```

`unsigned int` is **16-bit** on AVR. So `delayMicroseconds(75000)` does not merely lose accuracy — the
argument **cannot represent 75000 at all**: it truncates to `75000 − 65536 = 9464 µs`, a 12.5 % pulse
delivered silently. (The documented 16383 boundary is the `us *= 4` overflow point at 16 MHz:
`16383 × 4 = 65532` fits; `16384 × 4 = 65536` wraps to 0.)

Arithmetic re-verified: `3 × 25 × 1000 µs = 75 000 µs = 75 ms`; `75000 > 16383` ✓; `75000 > 65535` ✓.

### The 6.25 V ceiling — three canonical statements, verbatim

`REQUIREMENTS.md:30-34` (§"Evidence ceiling — fixed before any code moves"):

> The ~**6.25 V program-VCC** all four vendor algorithms assume for threshold margin is **unreachable on
> this shield** — the RURP has no VCC-raise path. This milestone buys *timing / pulse-count / verify*
> fidelity and **not** silicon-margin fidelity. It is hardware-bound, best-effort, the same shape as
> prior hardware-bound graduations. **gh#15 omits this entirely**, so its acceptance criteria imply a
> fidelity unreachable on this hardware and are amended by CLOSE-04.

`REQUIREMENTS.md` §Future, `FUT-VCC`:

> | **FUT-VCC** | 6.25 V program-VCC rail | Hardware, not firmware. No VCC-raise path exists on any shield revision. Accepted debt, recorded not attempted. |

Seed §"Hardware ceiling (state plainly)":

> Firmware fidelity buys *timing / pulse-count / verify* correctness but **not** full silicon-margin
> fidelity, because 6.25V program-VCC is unreachable on the current shield. This is best-effort — the
> same shape as prior D-07 hardware-bound graduations. Don't let the VCC gap block the (real,
> achievable) timing fixes. gh#15's acceptance criteria should be amended to acknowledge it.

Per D-05 this gets **its own paragraph, not a footnote**, and per §Specific Ideas it is framed as a
limit on what *any* implementation of gh#15 on this shield can claim — not as an excuse for this one.

---

## Citation Register — every citation resolved live

**Pinning strategy.** Pin sub-repo citations to **`origin/beta`** — all four cited files are
blob-identical at `beta` and at the milestone branch tip, and `beta` is what a stranger reads. Pin meta
citations to the pushed tip **`b6aa1dcb`**. Never pin to a branch *name*.

| Repo | Pin SHA | Note |
|---|---|---|
| `henols/firestarter_prom` (meta) | `b6aa1dcb23ef9931105752ed6dd6badccf6719de` | pushed tip; PUBLIC; carries `.planning/` |
| `henols/firestarter` (fw) | `6fab4eafdcd0981d24fddc3ff177abc5c74e313c` (`origin/beta`) — or `fb7949c0bdd575177262a76af506cec3b73ea28b` (branch tip) | PUBLIC; `eprom.cpp` + `memory.cpp` blobs identical on both |
| `henols/firestarter_app` (host) | `4d18b645ab18a2d2465f0f623062e9249eb24132` (`origin/beta` **and** branch tip — same commit) | PUBLIC; all cited blobs identical |

### Resolution results

| # | Citation | Resolves? | Verified content at the pinned SHA |
|---|---|---|---|
| 1 | `firestarter_app/doc/infoic-field-dictionary.md:210-217` | ✅ **exact** | L210-215 = the raw-hex→µs table incl. `AM2716 \| 0x0B \| 0x1F4 \| 500 µs \| 50000 µs (×100 wrong)`; L216 blank; L217 = `**BUG-2 (DEC-03):** … interpret_timing() applies val * 100 for protocol_id 0x07 and 0x0B … 252 chips … fix deferred to Phase 57.` A textbook anchor — it lands on exactly the adjudication. |
| 2 | commit `8de307f` (`firestarter_app`) | ✅ | `8de307f278370c07bfd3328aa9020248e66d0649` — *"feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts (DEC-03)"*, 2026-06-08 13:23:24 +0000. Reachable from **`origin/beta`** ✓ |
| 3 | commit `12286df` (`firestarter_app`) | ✅ | `12286df86abaf02be1d8e719818b7ca76a4c00e9` — *"feat(57-03): regenerate chip_database.json from corrected build_db.py"*, 2026-06-08 13:39:48 +0000. Reachable from **`origin/beta`** ✓ |
| 4 | `.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md` | ✅ 200 | Byte-identical to local. Histogram lines at **237 / 243 / 247** — quote-ready (below). |
| 5 | `.planning/phases/138-preconditions-baseline/138-pulse-distribution.py` | ✅ 200 | The runnable script (22 358 bytes). |
| 6 | `.planning/phases/138-preconditions-baseline/138-BASELINE.md` | ❌ **404** | Landed in unpushed `baa131a3`. **Recommendation: drop it** — F-06. |
| 7 | `.planning/PROJECT.md` C1/C2/C3 table | ⚠️ 200, **anchor shifted** | Table at **L61-63** at `b6aa1dcb`, **L71-73** locally — F-05. |
| 8 | `firestarter_app/firestarter/database.py:128` | ✅ **exact** | `128: def _parse_pulse_duration(pulse_str: str) -> int:` — the `"100 us"` string → int-µs layer (body L129-143; returns 0 for `""` / `"Algorithm Controlled"` / unparseable). |
| 9 | `firestarter/src/proms/eprom.cpp:20` | ✅ **exact** | `#define NUMBER_OF_RETRIES 20` |
| 10 | `firestarter/src/proms/eprom.cpp:69-77` | ✅ **exact** | L69 comment + the `if (handle->pulse_delay == 0)` switch: `0x08 → 100`, `0x0B → 500`, `default → 1000`. Note this line range shows **the firmware already defaults `0x0B` to 500 µs**, which is independent corroboration of C1 straight out of the code gh#15 asks to change. |
| 11 | `firestarter/src/proms/eprom.cpp:177` | ✅ **exact** | `handle->pulse_delay = org_delay + (org_delay * retries / NUMBER_OF_RETRIES);` |
| 12 | `firestarter/src/proms/eprom.cpp:283` | ⚠️ resolves, **wrong semantics** | Inside `eprom_internal_erase()` — the **erase** pulse. **F-02.** |
| 13 | **`firestarter/src/proms/memory.cpp:321-330`** ← *corrected C3 anchor* | ✅ **exact** | `memory_set_data()`; L256-258 = `rurp_chip_enable(); delayMicroseconds(handle->pulse_delay); rurp_chip_disable();` — **the program pulse**. |
| 14 | minipro `t48.c:250-267` | ⚠️ **not local** | Present only in *another session's* scratchpad (`/tmp/claude-1000/-workspaces/7668f856-…/minipro`), which is ephemeral and uncitable. Must cite the public **GitLab** URL. |

### minipro — repo, SHA and the load-bearing lines `[VERIFIED: local clone @ cae74c0]`

Upstream is **GitLab**, not GitHub: `https://gitlab.com/DavidGriffith/minipro.git`, clone HEAD
`cae74c0607077d6260b24995f5e4c0d0b66a6a2e` (2026-07-13, *"fix rpm .spec files; correct description in
.rules file"*). Permalink form: `https://gitlab.com/DavidGriffith/minipro/-/blob/<SHA>/src/t48.c#L255`.

`t48_begin_transaction()` opens at **line 246**. Within the cited 250-267 window, the two lines that
carry the whole "two orthogonal wire fields" claim are:

```c
255:		msg[1] = device->protocol_id;
...
266:		format_int(&(msg[12]), device->pulse_delay, 2,
267:			   MP_LITTLE_ENDIAN);
```

The four cross-references in the seed all check out at the stated lines:

| file | line | content |
|---|---|---|
| `tl866a.c` | 257 | `format_int(&(msg[9]), handle->device->pulse_delay, 2,` |
| `tl866iiplus.c` | 238 | `format_int(&(msg[12]), device->pulse_delay, 2,` |
| `t56.c` | 193 | `format_int(&(msg[12]), device->pulse_delay, 2,` |
| `t76.c` | 529 | `format_int(&(msg[12]), device->pulse_delay, 2,` |
| `main.c` | 698 | `"Default write pulse: %u us\nAvailable write pulse[us]: 1-65535\n",` |

The 65535 ceiling claim is supported directly by `main.c:698`'s own help string and by the 2-byte
`format_int` width. **`t48.c:250-267` is a defensible window** (it shows the whole `BEGIN_TRANS`
packing, which is the point — protocol_id and pulse_delay are siblings in one message), but if the
planner wants the tightest possible anchor, `#L255` and `#L266-L267` are the two load-bearing lines.

**Planner action:** since minipro is not in this workspace, the plan must either (a) cite the GitLab
permalink at `cae74c0` without a local re-verification step, marking it `[CITED]` rather than
`[VERIFIED]`, or (b) add a shallow clone step to the drafting task and re-verify the four line
anchors before freeze. (b) is cheap and matches this milestone's house style.

### C2's three histogram lines — quote-ready, verbatim from `138-02-PULSE-DISTRIBUTION.md:237-249`

> - Protocol **0x07**: **n = 170**, histogram `100 us ×113, 200×27, 1000×22, 500×4, 50×4`.
> - Protocol **0x08**: **n = 127**, histogram `100 us ×104, 50×11, 10×7, 200×2, 1000×2, 20×1`.
> - Protocol **0x0B**: **n = 32**, histogram `500 us ×21, 1000×6, 200×5`.

Arithmetic re-verified this session: 113+27+22+4+4 = **170** ✓; 104+11+7+2+2+1 = **127** ✓;
21+6+5 = **32** ✓; 170+127+32 = **329** ✓, matching the document's `329 + 417 = 746` whole-database
partition. Every count is independently checkable by a reader from the quoted line alone — which is
exactly why these three lines are the comment's payload.

The same document (§"Independent confirmation — database blob identity") records that the measured
`chip_database.json` blob is `ebd1eaac01698f64dc0861f8478b8931493d3bab`, identical on the worktree,
`origin/beta` and the v1.30 branch. Worth one clause in the comment: *the distribution was measured
against the blob that ships.*

---

## Architecture Patterns

### System Architecture Diagram

```
                          ┌──────────────────────────────────────────┐
   LOCKED INPUTS          │  PROJECT.md C1/C2/C3 · REQUIREMENTS.md   │
   (read-only)            │  ISSUE-01..03 · 139-CONTEXT.md D-01..11  │
                          └───────────────────┬──────────────────────┘
                                              │
   EVIDENCE (read-only)    ┌──────────────────┼──────────────────┐
   ┌───────────────────┐   │                  ▼                  │
   │ gh#15 live body   │──▶│         ┌────────────────┐          │
   │ (9 boxes, 0 cmts) │   │         │  TASK 1        │          │
   └───────────────────┘   │         │  DRAFT         │          │
   ┌───────────────────┐   │         │  + FREEZE      │          │
   │ 138-02-PULSE-DIST │──▶│         └───┬────────┬───┘          │
   │ infoic-dict:210-17│   │             │        │              │
   │ database.py:128   │   │             ▼        ▼              │
   │ eprom.cpp 20/69/177   │   139-GH15-      139-GH15-BODY-     │
   │ memory.cpp:329    │   │   COMMENT.md     AMENDMENT.md       │
   │ 8de307f / 12286df │   │   (deliverable)  (optional, D-01)   │
   │ minipro t48.c     │   │        │              │             │
   └───────────────────┘   └────────┼──────────────┼─────────────┘
                                    │              │
                     ┌──────────────▼──────────────▼──────────────┐
                     │ PRE-GATE MECHANICAL CHECKS (all agent-run) │
                     │  · every permalink: fetch raw @ pinned SHA │
                     │    + sed line-range + grep expected text   │
                     │  · 139-check-claims.py (planted-fail first)│
                     │  · eprom.cpp blob == baseline (3 refs)     │
                     │  · gh#15 still OPEN, comment count == 0    │
                     │  · blob SHA + byte length recorded         │
                     └──────────────────┬─────────────────────────┘
                                        │  review packet
                     ┌──────────────────▼─────────────────────────┐
                     │  TASK 2 — checkpoint:human-action BLOCKING │
                     │  Q1 wording: approve / name exact edits    │
                     │  Q2 posting: "post now" / "approved, hold" │
                     │  Q3 body edit: yes / SKIP  (default SKIP)  │
                     │  ⛔ never auto-approved by --auto/--chain  │
                     └───────┬──────────────────────────┬─────────┘
                             │ post now                 │ hold
                             ▼                          ▼
        ┌────────────────────────────────┐   ┌──────────────────────────────┐
        │ TASK 3a  gh issue comment 15   │   │ TASK 3b  FREEZE ONLY         │
        │  → comment URL                 │   │  · exact command parked in   │
        │  (optional: gh issue edit 15)  │   │    OPERATOR-BATCH A-1 shape  │
        │            │                   │   │  · ROADMAP P140 Depends-on   │
        │            ▼                   │   │    amended w/ named exception│
        │  fetch back → normalize 1 NL   │   │  · ISSUE-03 stays OPEN       │
        │  → byte-diff vs frozen blob    │   │  · NO gh call is made at all │
        │  → count 0→1, state still OPEN │   └──────────────┬───────────────┘
        └────────────────┬───────────────┘                  │
                         └──────────────┬───────────────────┘
                                        ▼
                             Phase 140 unblocked either way
                             (hold branch = recorded named exception, D-08)
```

### Recommended artifact layout

```
.planning/phases/139-gh-15-correction-outward/
├── 139-CONTEXT.md              # exists
├── 139-DISCUSSION-LOG.md       # exists
├── 139-RESEARCH.md             # this file
├── 139-01-PLAN.md              # draft + freeze + verify
├── 139-GH15-COMMENT.md         # THE deliverable  (mirrors 137-GH12-COMMENT.md)
├── 139-GH15-BODY-AMENDMENT.md  # optional 2nd action (D-01); own file so the freeze covers it separately
├── 139-CITATIONS.md            # permalink register + per-anchor verification transcript
├── 139-check-claims.py         # Phase-139-scoped forbidden-phrase gate (F-04)
└── 139-01-SUMMARY.md
```

### Pattern 1: The three-task gated-outward-act shape (`137-05-PLAN.md`)

**What:** `auto` draft/freeze/assemble-packet → `checkpoint:human-action gate="blocking"` → `auto`
apply-corrections/freeze/conditionally-act.
**When:** any irreversible outward act. This is the project's settled shape; do not re-derive it.

Frontmatter worth copying wholesale:

```yaml
files_modified:
  - .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md
  - .planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md
autonomous: false
requirements: [ISSUE-01, ISSUE-02, ISSUE-03]
user_setup:
  - service: github
    why: "ISSUE-03's blocking operator wording review of the gh#15 correction, and (conditionally) authorizing/posting it"
    dashboard_config:
      - task: "Read the review packet and the frozen draft, then explicitly approve the wording or name exact corrections, AND state whether to post now or hold, AND whether to also apply the issue-body amendment"
        location: "This plan's Task 2 checkpoint, presented in the execution transcript"
```

The checkpoint task's own shape (`137-05-PLAN.md:151-197`), abbreviated:

```xml
<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: BLOCKING operator wording review AND explicit posting authorization</name>
  <files>none (gate only)</files>
  <action>
Present the packet and BLOCK until the operator answers BOTH of the following. Do not proceed on
silence, and do not treat `auto_advance`/`--auto`/`--chain` as an answer to either question — this task
type is `checkpoint:human-action` specifically so that no automated mode ever supplies these answers.
  </action>
  <acceptance_criteria>
    - The operator's verdict is recorded verbatim in the SUMMARY, including an unambiguous choice between "post now" and "hold".
    - Nothing was posted before or during this task: `gh issue view 15 … -q '.comments | length'` is unchanged from the recorded before-count.
  </acceptance_criteria>
  <verify>
    <human-check>The operator has typed an explicit wording approval (or named corrections) AND an explicit posting-timing choice, both recorded verbatim in the SUMMARY.</human-check>
  </verify>
  <resume-signal>Type "approved, post now" / "approved, hold" / or name the sentences that must change plus your posting-timing choice.</resume-signal>
</task>
```

**Adaptation for Phase 139:** 137-05's Task 3 gated on *two* signals (operator "post now" **AND** a
mechanical shipped-check). Phase 139's analogous mechanical signal is **D-10's eprom.cpp-untouched
assertion** — fail-closed the same way, so a "post now" plus a dirty `eprom.cpp` does **not** post.

### Pattern 2: Freeze → post → prove they matched (`122-DELIVERY.md` §3 — the executed one)

**What:** record blob SHA + byte length before the gate; after any post, retrieve and byte-diff under
exactly one named normalization.
**Why this beats 137-05's version:** 137-05's recipe was written but never executed (the hold branch was
taken). 122-12 executed four outward calls and recorded the empirical result.

Verbatim from `122-DELIVERY.md:62-76`:

> **Normalization applied, stated once for all four rows:** CRLF→LF (no CRLF present in any of the
> four retrieved bodies — a no-op in practice) and collapsing to a single trailing newline. In every
> one of the four cases the *only* difference between the committed file and the retrieved body was
> GitHub appending exactly one trailing newline the committed file did not already end with; the byte
> length differs by exactly 1 in all four cases, and the line-level `diff` shows exactly one added
> blank line at end-of-file and nothing else.
>
> **Retrieval commands used for the byte-equality proof:**
> - Issue comments: `gh issue view <n> --repo henols/firestarter_prom --json comments -q '.comments[-1].body'`, piped through `tr -d '\r'`, written to a file in `$(mktemp -d)`.
> - Comparison: `diff <(sed -e '$a\' <committed file>) <(sed -e '$a\' <retrieved file>)` — the `sed -e '$a\'` idiom ensures both sides end in exactly one newline before comparing.

**The `sed -e '$a\'` idiom is the whole trick** and the plan must name the one-trailing-newline
normalization *in advance*, not discover it at posting time.

`.comments[-1]` is safe here in a way it was not for gh#11/#12: **gh#15 has zero comments**, so after
posting, `[-1]` is unambiguously ours and the exact-increment assertion is the strongest form — `0 → 1`.

### Pattern 3: The frozen-but-unposted follow-up record (`v1.30-OPERATOR-BATCH.md` §A-1)

**What:** if the operator says "approved, hold", the deferral is recorded as an *actionable* row —
approval date, blob SHA, byte length, the deciding evidence, and the exact single command — never as a
gap. Verbatim shape (v1.30 A-1): *"Wording **APPROVED** by the operator in real time at 137-05 Task 2 …
Frozen at `137-GH12-COMMENT.md` blob `3a628c56de4d45dfe2be0c645fced0e25d5ebceb` (2646 bytes). **Posting
is HELD, not authorized** … **POST ONLY after …** — run exactly: `gh issue comment 12 --repo
henols/firestarter_prom --body-file .planning/phases/137-…/137-GH12-COMMENT.md`."*

**Phase 139 needs a v1.31 home for this** — `.planning/v1.30-OPERATOR-BATCH.md` belongs to a closed
milestone and its A-1 row is already RESOLVED. Create `.planning/v1.31-OPERATOR-BATCH.md` on the same
shape, or park the row in `139-01-SUMMARY.md` + the ROADMAP Phase 139 entry. **Do not** append a v1.31
row to the v1.30 file.

**D-08's second landing site:** `ROADMAP.md` §"Phase 140" line 4 currently reads
`**Depends on**: Phase 139 (the correction is public before this implementation phase lands).` — the
hold branch must amend exactly this line with the named exception, so CLOSE-04 has something honest to
reconcile against. `.planning/ROADMAP.md:229-241` is the Phase 139 block; Phase 140's block follows.

⚠ Amending ROADMAP by hand is safe; **do not** run `phase.complete` to do it — a recorded project
finding is that it clobbers an unrelated phase's `**Plans:**` line. Snapshot and diff ROADMAP if any
state tool touches it.

### Anti-patterns to avoid

- **`checkpoint:human-verify` for the gate.** `--auto`/`--chain` auto-approve every `human-verify` and
  auto-select the first option of every `decision` checkpoint; only `human-action` is always presented.
  `autonomous: false` alone is **not** self-protecting. (D-09; project memory.)
- **Batching the three authorizations into one approval.** Wording ≠ posting ≠ body-edit. The v1.22
  lesson recorded in project memory is to gate each distinct outward channel separately, so the
  operator can stop halfway.
- **Trusting an HTTP 200 as anchor verification.** F-05: `PROJECT.md#L71-L73` returns 200 and points at
  the wrong lines.
- **Reusing the v1.30 claim gate.** F-04: proven vacuous on this phase's vocabulary.
- **An agent running `git push` or `gh issue comment` unilaterally.** F-06/F-07.
- **Copying `PROJECT.md`'s C2 sentence verbatim.** F-03.
- **Citing `eprom.cpp:283` as the program pulse.** F-02.
- **A claim gate that has only ever passed.** ROADMAP's v1.31 must-not-do list makes planted-failure
  non-vacuity binding on *every* phase in this milestone.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Gated outward publication flow | A new checkpoint/approval design | `137-05-PLAN.md`'s three-task shape verbatim | Worked instance of this exact gate, including the deferred-post branch |
| Post-hoc "posted == reviewed" proof | A hand-rolled diff or a hash comparison | `122-DELIVERY.md` §3's `diff <(sed -e '$a\' A) <(sed -e '$a\' B)` | The only *executed* recipe; the one-trailing-newline behavior is empirically established across 4 calls |
| Retrieving the posted comment | Constructing a comment ID from the post output | `gh issue view 15 --json comments -q '.comments[-1].body'` | No ID parsing; and with 0 pre-existing comments `[-1]` is unambiguous |
| Pulse-width evidence | Re-running any measurement | Quote `138-02-PULSE-DISTRIBUTION.md:237-249` + link `138-pulse-distribution.py` | Already measured, already proved its own capacity to fail (planted-failure Run 1), already formatted for this audience |
| Parsing `pulse_duration` | Any re-implementation | Cite `database.py:128` `_parse_pulse_duration` | Phase 138's D-11 rule: the parser is imported, never reimplemented — the comment must not blur the string→int-µs layer |
| Overclaim scan | Forking `check_permitted_claims.py` | A ~40-line Phase-139-scoped script | F-04. Reuse only its *never-vacuous guard* (lines 288-295) and its argv-only precedence idea |
| Freeze mechanism | A checksum file or a lockfile | `git rev-parse HEAD:<path>` blob SHA + `wc -c` | The project's standing freeze pair, used at 137-05 and 122-12 |
| "Is `eprom.cpp` untouched?" | `git status` on the meta repo | Blob-SHA equality across three refs (below) | The meta repo shows ` M firestarter` for a stale **gitlink pointer**, which is not an edit — F-09 |

**Key insight:** every mechanism this phase needs already exists in this repo, executed at least once.
The failure mode is not missing tooling — it is copying a precedent's *text* without checking whether
that particular line ever ran (137-05's byte-diff never did) or still means what it says (F-02, F-04).

---

## Runtime State Inventory

Not a rename/refactor phase, but it *is* a publication phase whose "runtime state" lives in a third
party's database. Answered explicitly so the planner does not have to guess.

| Category | Items found | Action required |
|---|---|---|
| **Stored data (external service)** | **gh#15 on GitHub**: `state=OPEN`, `comments=0`, `labels=[]`, `updatedAt == createdAt` (never edited), body 5964 bytes. This is the state the phase mutates. | Record all four before/after. Post = `comments 0→1`; body edit = `updatedAt` changes and body bytes change. Assert `state` stays `OPEN` and `labels` stays `[]` — `gh issue comment` sends neither, but assert it anyway (122-12 did). |
| **Live service config not in git** | None. The comment body is a git-committed file; nothing lives only in a GitHub UI. | None. |
| **OS-registered state** | None. | None — verified: no scheduler/daemon/service registration exists for this phase. |
| **Secrets / env vars** | `gh` OAuth token at `/home/vscode/.config/gh/hosts.yml`, scopes `gist, read:org, repo, workflow`, account `henols`. `repo` suffices for issue comment/edit on a public repo. No `.env`, no SOPS key involved. | None — but the plan must **not** print the token, and `gh auth status` masks it (`gho_***`). |
| **Build artifacts / installed packages** | None. Zero installs; no `npm`/`pip`/`cargo` in scope. | None. |
| **Unpushed git state (meta)** | **8** commits ahead of `origin/gsd/v1.31-…` (`baa131a3`, `385bdca7`, `e8a120da`, `57116888`, `7fffc289`, `78904a0e`, `d849597d`, `cbc66d60`); working tree also has ` M .gitignore`, untracked `.claude/`, `.planning/VALIDATED-EPROMS.md`, `package.json`, `package-lock.json`. | A push carries only committed history, so none of the untracked/dirty items would travel. But see F-06 — **no push should be needed**. |
| **Stale submodule gitlinks (meta)** | Meta records `firestarter → 0933bd7d`, `firestarter_app → cc036e8d`; actual checkouts are `fb7949c0` / `4d18b645`. Hence ` M firestarter` / ` M firestarter_app` in `git status`. | **None** — and critically, **do not** treat this as evidence that `eprom.cpp` was touched (F-09). |

### F-09 — D-10's mechanical precondition, made false-green-proof `[VERIFIED]`

The meta repo's `git status --porcelain` shows:

```
 M .gitignore
 M firestarter          ← STALE GITLINK POINTER, not a source edit
 M firestarter_app      ← STALE GITLINK POINTER, not a source edit
?? .claude/
?? .planning/VALIDATED-EPROMS.md
?? package-lock.json
?? package.json
```

A naive "the tree is clean" assertion would fail; a naive "ignore the submodules" assertion could pass
while `eprom.cpp` was genuinely edited-and-committed inside the submodule. Neither is acceptable.

**"Untouched" must mean three things, and all three are checkable today:**

```bash
# 1. No uncommitted edit in the working tree of the firmware repo
test -z "$(git -C /workspaces/firestarter status --porcelain -- src/proms/eprom.cpp)"

# 2. No COMMITTED change since the Phase 138 frozen baseline (3085084, PROJECT.md's named fw base)
test -z "$(git -C /workspaces/firestarter diff --stat 3085084..HEAD -- src/proms/eprom.cpp)"

# 3. Strongest form — the blob is byte-identical at all three refs a reader could look at
for r in HEAD origin/beta 3085084; do git -C /workspaces/firestarter rev-parse $r:src/proms/eprom.cpp; done \
  | sort -u | wc -l    # must print 1
```

Measured live 2026-08-09 — all three pass:

| ref | `src/proms/eprom.cpp` blob |
|---|---|
| `HEAD` (`fb7949c0`) | `8dfa4cced460416fc1b0f73cf3f0e6f77965f962` |
| `origin/beta` (`6fab4eaf`) | `8dfa4cced460416fc1b0f73cf3f0e6f77965f962` |
| `3085084` (Phase 138 base) | `8dfa4cced460416fc1b0f73cf3f0e6f77965f962` |

`3085084` is confirmed an ancestor of `HEAD`; the five commits between them are all Phase 138 trace /
baseline work, none touching `eprom.cpp`. Use check 3 as the primary assertion — it cannot false-green
on a gitlink pointer, on an uncommitted edit, or on a committed one. And **do not** use
`git submodule status` (F-08).

Consider extending the same three-ref blob check to `memory.cpp` — F-02 makes it a cited file, and the
comment's "before implementation" claim reads more honestly if the *program pulse* file is also proven
untouched. Measured: `memory.cpp` blob is `478fa1d35fed2abbefb27d4d2c54dcec02086687` at both `HEAD` and
`origin/beta`.

---

## Common Pitfalls

### Pitfall 1: Citing a line number that resolves but means something else
**What goes wrong:** `eprom.cpp:283` is a real `delayMicroseconds(handle->pulse_delay)` — it just isn't
the program pulse. A reader following the link lands in `eprom_internal_erase()`.
**Why it happens:** the anchor was recorded from a `grep` for `delayMicroseconds` without reading the
enclosing function. `eprom.cpp` has exactly one such call, so the grep looked conclusive.
**How to avoid:** for every `file:line` citation, fetch the pinned raw file, slice the range, and
confirm the **enclosing function** as well as the line. Record the sliced text in `139-CITATIONS.md`.
**Warning signs:** an anchor that is a single line with no function context; a citation whose
surrounding comment mentions a different operation than the one being claimed.

### Pitfall 2: Believing an HTTP 200 verifies a permalink
**What goes wrong:** `#L71-L73` on a file whose table moved to `L61-63` returns 200 and shows the wrong
content. Fragments are client-side; no request validates them.
**Why it happens:** line numbers get read off the working tree, permalinks get pinned to a pushed SHA,
and the two differ by every unpushed commit that touched the file.
**How to avoid:** derive line numbers **from the pinned SHA's content**, never from local. Verify by
content match, not status code (recipe in F-05).
**Warning signs:** any unpushed commit touching a cited file; a citation to `PROJECT.md`, `STATE.md` or
`ROADMAP.md` — all three churn constantly.

### Pitfall 3: A claim gate that scans nothing
**What goes wrong:** exit 0 with `UNARMED`, or exit 0 with `PASS` on a file full of overclaims.
**Why it happens:** `_HERE`-relative defaults resolve to filenames that don't exist in the new
directory; and a proximity window tuned to another milestone's vocabulary filters out every real hit.
**How to avoid:** argv-only targets, a hoisted never-vacuous guard, no proximity window for a
single-topic file, and a **planted violation** run recorded before the clean run is believed.
**Warning signs:** a gate whose only recorded output is a pass; a `PASS:` line that names zero files or
names files you did not expect.

### Pitfall 4: Half-correcting a public spec
**What goes wrong:** the two numbers get corrected, the architecture criterion and the two body
directives (*"each protocol must own its … timing constants"*, *"Do not retain the current generic
500 us legacy default"*) stand. A reader implementing from the body still builds the wrong thing —
and now the issue *looks* corrected.
**Why it happens:** the checkbox list is the visible artifact; prose directives in the body are easy to
miss. And the box count itself was mis-recorded.
**How to avoid:** map all **nine** boxes plus both prose directives; preserve the original verbatim in
a `<details>` block wherever the amendment lands (D-01, §Specific Ideas).

### Pitfall 5: An outward act performed by an agent that the operator owns
**What goes wrong:** an executor runs `git push` or `gh issue comment` because the plan's action text
said to. Under `--auto`/`--chain`, a `human-verify` gate would have been auto-approved on the way there.
**Why it happens:** `137-05-PLAN.md`'s Task 3 *is* an `auto` task that calls `gh issue comment` — but
only under a doubly-gated condition. Copying the shape without the conditions loses the protection.
**How to avoid:** `checkpoint:human-action` for the gate; fail-closed conditions on the acting task;
and prefer eliminating the push entirely (F-06). State plainly in the plan objective that Phase 139
must not run under `--auto`/`--chain`.

### Pitfall 6: A byte-diff that fails for a reason nobody predicted
**What goes wrong:** the fetched body differs from the frozen file by one trailing newline, and the
verification step reports a mismatch on a genuinely-correct post — at the worst possible moment, right
after an irreversible act.
**Why it happens:** GitHub appends exactly one trailing newline (measured across four calls in 122-12).
137-05's recipe says "must be identical" with no normalization and was never exercised.
**How to avoid:** name the normalization in the plan text *before* posting, and use the
`diff <(sed -e '$a\' A) <(sed -e '$a\' B)` idiom.
**Also:** use the correct single-comment endpoint. `gh api repos/OWNER/REPO/issues/comments/<id>` is
right; `…/issues/<n>/comments/<id>` **404s** — and if piped to a file without an exit-code check, the
404 JSON body (which *does* use CRLF) becomes the "retrieved comment" and the diff reports a spurious
content mismatch. Verified this session by making exactly that mistake.

### Pitfall 7: Executors prematurely ticking multi-requirement work
**What goes wrong:** all three of ISSUE-01/02/03 get ticked when only the drafting task ran.
**Why it happens:** a recorded project pattern — executors marked multi-plan requirements Complete 4×
in Phase 116; ROADMAP's own v1.31 notes call it out.
**How to avoid:** name the allowed requirement IDs per task when dispatching. In the hold branch,
**ISSUE-03 must stay `[ ]`** (its text says "posted"), matching v1.30's CLOSE-06 handling; ISSUE-01 and
ISSUE-02 can tick on the frozen, approved draft.

---

## Code Examples

All verified this session against the live repos/API unless marked.

### Read gh#15's current state and freeze the before-counts

```bash
gh issue view 15 --repo henols/firestarter_prom \
  --json state,comments,labels,updatedAt \
  -q '{state:.state, n:(.comments|length), labels:.labels, updated:.updatedAt}'
# → {"labels":[],"n":0,"state":"OPEN","updated":"2026-07-12T09:15:27Z"}
```

### Extract the nine acceptance boxes verbatim (for the `<details>` block)

```bash
gh issue view 15 --repo henols/firestarter_prom --json body -q .body \
  | awk '/^## Acceptance criteria/,0' > 139-GH15-ORIGINAL-CRITERIA.md
gh issue view 15 --repo henols/firestarter_prom --json body -q .body | grep -c '^- \[ \]'   # → 9
```

### Verify a permalink by CONTENT, not status code

```bash
verify_anchor() {  # $1=raw-url  $2=first  $3=last  $4=expected substring
  local out; out=$(curl -sf "$1") || { echo "FAIL(fetch) $1"; return 1; }
  printf '%s\n' "$out" | awk -v a="$2" -v b="$3" 'NR>=a && NR<=b' | grep -qF -- "$4" \
    && echo "OK   $1#L$2-L$3" || { echo "FAIL(anchor) $1#L$2-L$3"; return 1; }
}

APP=https://raw.githubusercontent.com/henols/firestarter_app/4d18b645ab18a2d2465f0f623062e9249eb24132
FW=https://raw.githubusercontent.com/henols/firestarter/6fab4eafdcd0981d24fddc3ff177abc5c74e313c
META=https://raw.githubusercontent.com/henols/firestarter_prom/b6aa1dcb23ef9931105752ed6dd6badccf6719de

verify_anchor "$APP/doc/infoic-field-dictionary.md" 210 217 '50000 µs (×100 wrong)'
verify_anchor "$APP/firestarter/database.py"        128 128 'def _parse_pulse_duration'
verify_anchor "$FW/src/proms/eprom.cpp"              20  20 '#define NUMBER_OF_RETRIES 20'
verify_anchor "$FW/src/proms/eprom.cpp"              69  77 'case 0x0B: handle->pulse_delay = 500;'
verify_anchor "$FW/src/proms/eprom.cpp"             177 177 'org_delay * retries / NUMBER_OF_RETRIES'
verify_anchor "$FW/src/proms/memory.cpp"            249 258 'delayMicroseconds(handle->pulse_delay);'
verify_anchor "$META/.planning/phases/138-preconditions-baseline/138-02-PULSE-DISTRIBUTION.md" \
                                                    237 249 'n = 170'
```

### Verify the two C1 commits resolve publicly

```bash
for c in 8de307f278370c07bfd3328aa9020248e66d0649 12286df86abaf02be1d8e719818b7ca76a4c00e9; do
  gh api repos/henols/firestarter_app/commits/$c \
    --jq '.sha[0:7] + " | " + (.commit.message | split("\n")[0])'
done
# → 8de307f | feat(57-01): remove interpret_timing x100 multiplier and fix bare excepts (DEC-03)
# → 12286df | feat(57-03): regenerate chip_database.json from corrected build_db.py
```

### Freeze (blob SHA + byte length) — the project's standing pair

```bash
F=.planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md
git add "$F" && git commit -m "docs(139): freeze the gh#15 correction comment"
git rev-parse HEAD:"$F"      # blob SHA
wc -c < "$F"                 # byte length
test -z "$(git status --porcelain -- "$F")" && echo FROZEN
```

### Post, then prove posted == reviewed (122-DELIVERY §3, adapted)

```bash
# --- gated: only after explicit operator "post now" AND the eprom.cpp blob check ---
gh issue comment 15 --repo henols/firestarter_prom \
  --body-file .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md
# prints the new comment URL, e.g. https://github.com/.../issues/15#issuecomment-XXXXXXXXXX

T=$(mktemp -d)
gh issue view 15 --repo henols/firestarter_prom --json comments \
  -q '.comments[-1].body' | tr -d '\r' > "$T/posted.md"
diff <(sed -e '$a\' .planning/phases/139-gh-15-correction-outward/139-GH15-COMMENT.md) \
     <(sed -e '$a\' "$T/posted.md") \
  && echo "BYTE-EQUAL under the one-trailing-newline normalization"

gh issue view 15 --repo henols/firestarter_prom \
  --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
# expect {"labels":[],"n":1,"state":"OPEN"}   ← exact 0→1 increment
```

Single-comment endpoint, if an ID is preferred over `[-1]` (**note the path has no issue number**):

```bash
ID=$(gh issue view 15 --repo henols/firestarter_prom --json comments -q '.comments[-1].url' \
     | sed 's/.*issuecomment-//')
gh api repos/henols/firestarter_prom/issues/comments/$ID --jq .body   # ✅
# gh api repos/henols/firestarter_prom/issues/15/comments/$ID         # ❌ 404
```

### Optional body amendment (D-01 — default SKIP, separately authorized)

```bash
gh issue edit 15 --repo henols/firestarter_prom \
  --body-file .planning/phases/139-gh-15-correction-outward/139-GH15-BODY-AMENDMENT.md

gh issue view 15 --repo henols/firestarter_prom --json body,updatedAt -q .body \
  | tr -d '\r' > "$T/body.md"
# assert the ORIGINAL nine boxes survive verbatim inside <details>
grep -c '^- \[ \]' "$T/body.md"     # ≥ 9 (9 original + the corrected list's own boxes)
diff <(sed -e '$a\' 139-GH15-ORIGINAL-CRITERIA.md) \
     <(awk '/<details>/,/<\/details>/' "$T/body.md" | grep '^- \[ \]' | sed 's/^/PLACEHOLDER/')  # shape check
```

`gh issue edit` flags confirmed present in `gh 2.96.0`: `-F, --body-file file`. `--add-label` /
`--remove-label` exist but must not be passed.

### The D-05 gate, with its mandatory planted-failure run

```bash
cd .planning/phases/139-gh-15-correction-outward

# 1. NON-VACUITY FIRST — must FAIL
cp 139-GH15-COMMENT.md /tmp/planted.md
printf '\nThis firmware is datasheet-conformant and algorithm-accurate.\n' >> /tmp/planted.md
python3 139-check-claims.py /tmp/planted.md; test $? -eq 1 || { echo "GATE IS VACUOUS"; exit 1; }

# 2. Only now is a pass meaningful
python3 139-check-claims.py 139-GH15-COMMENT.md 139-GH15-BODY-AMENDMENT.md
```

### Environment probe transcript (measured 2026-08-09)

```
python3 3.12.13 · pytest 9.1.1 · node v22.23.2 · gh 2.96.0 · git 2.55.0 · curl 8.14.1
gh auth: henols, scopes: gist, read:org, repo, workflow
henols/firestarter_prom  PUBLIC  default=main
henols/firestarter       PUBLIC  default=main
henols/firestarter_app   PUBLIC  default=main
```

---

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|---|---|---|---|
| `checkpoint:human-verify` for outward acts (122-11) | `checkpoint:human-action` | Phase 137 (2026-08-05) | Binding — D-09; `137-05-PLAN.md:86-88` explicitly says "do not downgrade it back" |
| "diff must be identical" after posting | diff under one named normalization (`sed -e '$a\'`), one trailing newline expected | Phase 122 delivery (2026-07-30), empirically | 137-05's stricter wording was never executed and would fail |
| `git push` / workflow dispatch as an executor step | Operator-performed, or operator-granted then agent-run | Phase 138 (2026-08-09) + the corrected classifier memory note | F-06/F-07 |
| Claim gates copied between phases | Authored **and hosted** in the phase that uses them, with paired P-11 non-vacuity tests | Phase 137 | F-04 — but the v1.30 *vocabulary* is milestone-specific and does not port |
| Cite by branch name | Cite by commit SHA | D-07, this phase | Branch tips move; SHAs do not |

**Deprecated / do not reuse:**
- `.planning/v1.30-OPERATOR-BATCH.md` as a landing site for new rows — it belongs to a closed milestone
  and its A-1 is RESOLVED.
- `.planning/research/PITFALLS.md` P-11's checker-fork prescription **for this phase specifically** —
  the fork mechanics are sound but the v1.30 vocabulary/caveat/proximity design does not transfer (F-04).
  (P-11 remains binding for Phase 146's CLOSE-01.)
- `git submodule status` anywhere in a verification step (F-08).

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|---|---|---|---|---|
| `gh` CLI | read gh#15, post, fetch back | ✓ | 2.96.0 | none needed |
| `gh` auth w/ `repo` scope | posting / body edit | ✓ | `henols`; `gist, read:org, repo, workflow` | — |
| `gh issue` **permission** | the post itself | ✗ **not allowlisted** | — | Operator grants it, or runs the one-liner (F-07) |
| `git` | freeze, blob-SHA assertions | ✓ | 2.55.0 | — |
| `curl` | permalink content verification | ✓ | 8.14.1 | `gh api` raw fetch |
| `python3` | the D-05 claim gate | ✓ | 3.12.13 | — |
| `pytest` | optional paired test for the gate | ✓ | 9.1.1 | inline planted-failure run suffices |
| `node` + `gsd-tools.cjs` | GSD state/commit ops | ✓ | v22.23.2; `.claude/gsd-core/bin/gsd-tools.cjs` | node is **not** on PATH by default — invoke via the explicit path |
| Public network → github.com / raw.githubusercontent.com | citation resolution | ✓ | 200s confirmed | — |
| Public network → gitlab.com | minipro permalink | **untested** | — | Cite `[CITED]` without local re-verify, or shallow-clone (below) |
| minipro source | verifying `t48.c:250-267` | ✗ locally | — | `git clone --depth 1 https://gitlab.com/DavidGriffith/minipro.git` — or reuse the verified line contents recorded in §"Citation Register" |

**Missing with no fallback:** none.
**Missing with fallback:** `gh issue` permission (operator lifts it, or runs the command); minipro
source (shallow clone, or cite the recorded contents).

---

## Validation Architecture

### Test framework

| Property | Value |
|---|---|
| Framework | `pytest` 9.1.1 (available; **optional** here) + shell assertions in `<verify><automated>` blocks |
| Config file | none for meta-repo phases — 137 ran `test_check_permitted_claims_v130.py` directly from its phase dir |
| Quick run | `cd .planning/phases/139-gh-15-correction-outward && python3 139-check-claims.py <files>` |
| Full suite | the Task-3 verification block: anchors + freeze + blob-equality + gh state |

Note: `pytest` addopts in this project are `-ra -q`; doubling `-q` hides the count line. Use
`-o addopts=""` if a paired test module is added.

### Phase requirements → test map

| Req | Behavior | Type | Automated command | Exists? |
|---|---|---|---|---|
| ISSUE-01 | Comment states C1 and cites `infoic-field-dictionary.md:210-217` + commits `8de307f`/`12286df` | content assertion | `grep -qF '500' 139-GH15-COMMENT.md && grep -qF '8de307f' … && grep -qF '12286df' …` | ❌ Wave 0 (artifact) |
| ISSUE-01 | Every C1/C2/C3 citation **resolves at its pinned SHA with the claimed content** | integration | `verify_anchor` loop (§Code Examples) — 7 anchors + 2 commits, exit 0 | ❌ Wave 0 (script) |
| ISSUE-01 | Comment states C2 with the three histogram lines | content | `for p in 'n = 170' 'n = 127' 'n = 32'; do grep -qF "$p" 139-GH15-COMMENT.md; done` | ❌ Wave 0 |
| ISSUE-01 | Comment states C3 as the **overprogram** pulse, and cites the **program**-pulse line | content | `grep -qF 'memory.cpp' 139-GH15-COMMENT.md && grep -qF '75' … && grep -qF '16383' …` | ❌ Wave 0 |
| ISSUE-01 | C2 does **not** carry the false "all three disagree with the modal value" (F-03) | negative content | `! grep -qiE 'all three.*disagree.*modal' 139-GH15-COMMENT.md` | ❌ Wave 0 |
| ISSUE-02 | 6.25 V ceiling present as its own paragraph | content | `grep -qF '6.25' 139-GH15-COMMENT.md` + manual paragraph check | ❌ Wave 0 |
| ISSUE-02 | Amendment maps **all nine** boxes, each marked kept/corrected/replaced | structural | `test $(grep -cE '\b(kept\|corrected\|replaced)\b' 139-GH15-COMMENT.md) -ge 9`; and the original nine survive verbatim | ❌ Wave 0 |
| ISSUE-02 | No forbidden overclaim | claim gate | `python3 139-check-claims.py …` — **preceded by** the planted-failure run | ❌ Wave 0 (script) |
| ISSUE-03 | Nothing posted before the gate | state | `gh issue view 15 … -q '.comments\|length'` == 0 at Task 1 and Task 2 | ✅ command exists |
| ISSUE-03 | Draft frozen | git | blob SHA + `wc -c` recorded; `git status --porcelain -- <file>` empty | ✅ |
| ISSUE-03 | Operator approved wording | **human** | verbatim verdict in SUMMARY | 🧑 human-only |
| ISSUE-03 | Posting explicitly authorized | **human** | verbatim "post now" / "approved, hold" | 🧑 human-only |
| ISSUE-03 | Posted == reviewed | integration | `diff <(sed -e '$a\' frozen) <(sed -e '$a\' fetched)` → empty | ✅ recipe proven at 122-12 |
| ISSUE-03 | Exactly one comment added, issue still OPEN, no label | state | `{"labels":[],"n":1,"state":"OPEN"}` | ✅ |
| ISSUE-03 | Correction precedes implementation (D-10) | git | 3-ref blob equality on `eprom.cpp` (§F-09) → 1 unique SHA | ✅ passes today |

### ROADMAP success criteria → validation

| # | Criterion | Mechanically checkable? |
|---|---|---|
| 1 | Draft states C1/C2/C3, each cited by `file:line` or commit | **Yes** — content greps + the `verify_anchor` loop. *Judgement remains for whether the prose is accurate; the anchors are mechanical.* |
| 2 | States the 6.25 V ceiling and proposes a specific amendment | **Partly** — presence is greppable; nine-box coverage is structurally checkable; whether the amendment is *right* is the operator's call |
| 3 | Frozen and operator-approved before posting; posted only on explicit authorization | **No — human-only.** Mechanically enforceable only *negatively*: comment-count-unchanged before the gate, and `checkpoint:human-action` typing |
| 4 | Posting precedes any TABLE/LOOP/VPP/HOST work | **Yes** — F-09's 3-ref blob check on `eprom.cpp` (extend to `memory.cpp`), plus ROADMAP Phase 140 still unstarted |

### Sampling rate

- **Per task commit:** `139-check-claims.py` on the changed artifact + `git status --porcelain` empty.
- **Per gate crossing:** full `verify_anchor` loop + the 3-ref `eprom.cpp` blob check + gh#15 state read.
- **Phase gate:** all of the above green, plus the byte-diff (post branch) or the parked-command record
  (hold branch), before `/gsd-verify-work`.

### Wave 0 gaps

- [ ] `139-GH15-COMMENT.md` — the deliverable (ISSUE-01, ISSUE-02)
- [ ] `139-GH15-BODY-AMENDMENT.md` — optional second action (D-01)
- [ ] `139-GH15-ORIGINAL-CRITERIA.md` — the nine boxes captured verbatim, for the `<details>` block
- [ ] `139-CITATIONS.md` — permalink register + per-anchor verification transcript
- [ ] `139-check-claims.py` — Phase-139-scoped forbidden-phrase gate (F-04), with a planted-failure run
- [ ] `.planning/v1.31-OPERATOR-BATCH.md` — **only if** the hold branch is taken

No test-framework install is needed.

---

## Security Domain

`security_enforcement` is not set to `false` in `.planning/config.json`, so this section is included.
This phase writes markdown and makes one authenticated API call; most ASVS categories are inapplicable.

### Applicable ASVS categories

| Category | Applies | Standard control |
|---|---|---|
| V2 Authentication | yes (weakly) | `gh`'s stored OAuth token; never printed, never echoed. `gh auth status` masks it. No credential is authored into any artifact |
| V3 Session Management | no | no sessions |
| V4 Access Control | **yes** | Two independent layers: the token's `repo` scope, and the Claude Code auto-mode classifier gating state-changing `gh` (F-07). The agent must not attempt to weaken either — no settings edits, no `gh api --method POST` workaround |
| V5 Input Validation | yes (weakly) | The only untrusted input is gh#15's body, consumed via `--json … -q` (JSON-decoded, never shell-interpolated). Use `--body-file`, **never** `--body "$(...)"` — STATE.md records this as an existing project rule |
| V6 Cryptography | no | none used; git blob SHAs are integrity checks, not secrets |
| V7 Error Handling | **yes** | Every gate must fail **closed**. A 404, an empty fetch, or a non-zero `gh` exit must abort, never fall through to "assume it matched" (Pitfall 6) |
| V14 Configuration | yes | `.claude/settings.local.json` is read-only to this phase |

### Threat register

| ID | Threat | STRIDE | Mitigation |
|---|---|---|---|
| T-139-01 | `--auto`/`--chain` supplies an approval that was never given | Repudiation | `checkpoint:human-action`, not `human-verify` (D-09); plan objective states the phase must not run under those flags. Inherits T-137-16 |
| T-139-02 | Posted text ≠ reviewed text | Tampering | Blob SHA + byte length before the gate; post-hoc `diff` under the named one-trailing-newline normalization; re-confirm the blob SHA immediately before the call (122-12 did) |
| T-139-03 | Posting before implementation is genuinely untouched, invalidating criterion 4 | Repudiation | F-09's 3-ref blob check as a fail-closed precondition on the acting task, not an inference from phase order |
| T-139-04 | A citation 404s or points at wrong lines → the correction reads as fabricated | Information disclosure / credibility | Content-based `verify_anchor` on every anchor at the pinned SHA (F-05); drop `138-BASELINE.md` (F-06) |
| T-139-05 | A vacuous claim gate green-lights an overclaim | Repudiation | Argv-only targets, never-vacuous guard, no proximity window, **planted-failure run first** (F-04; binding per ROADMAP's v1.31 must-not-do list) |
| T-139-06 | Body edit destroys the public record | Tampering | Original nine boxes preserved verbatim in `<details>`; read-back assertion after any edit; default-SKIP (D-01) |
| T-139-07 | A held follow-up silently evaporates | Repudiation | Exact one-line command parked in a v1.31 operator-batch row **and** the ROADMAP Phase 140 `Depends on:` amendment. Inherits T-137-18 |
| T-139-08 | Requirements ticked prematurely | Repudiation | Name allowed requirement IDs per task at dispatch; ISSUE-03 stays `[ ]` in the hold branch |
| T-139-09 | Token leakage into a committed artifact | Information disclosure | No `gh auth token`, no `--body "$(...)"`; artifacts are hand-authored markdown |
| T-139-SC | Supply chain (npm/pip/cargo) | Tampering | **accept** — zero installs in this phase's scope |

---

## Package Legitimacy Audit

**Not applicable — this phase installs no external packages.** No `npm install`, `pip install`, or
`cargo add` appears anywhere in its scope. `slopcheck` was therefore not run.

The only optional external artifact is a **shallow clone of minipro** for re-verifying `t48.c:250-267`:
`https://gitlab.com/DavidGriffith/minipro.git` — the canonical upstream, GPL, David Griffith's project,
already the established reference throughout this project's planning record (Phases 02, 120, 136.1). It
is cloned and read, never executed or installed.

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|---|---|---|
| A1 | `gh issue comment` / `gh issue edit` are blocked by the auto-mode classifier the same way `gh workflow run` is | F-07 | Low. If they turn out to be permitted, the plan simply proceeds without the operator having to grant anything. Not verified because verifying means posting. |
| A2 | `gh issue comment` prints the created comment's URL on stdout | §gh CLI Mechanics | Low. `137-05-PLAN.md:217` asserts it, and 122-12 recorded four resulting URLs. Even if not, `.comments[-1].url` retrieves it. Not exercised here. |
| A3 | Pinning sub-repo citations to `origin/beta` is preferable to pinning to the milestone branch tip | §Citation Register | None material — all four cited blobs are byte-identical at both, so either pin resolves to identical content. A style call, left to the planner. |
| A4 | `gitlab.com` is reachable from this environment | §Environment Availability | Low. If not, cite `[CITED]` from the line contents recorded in §Citation Register, which were read from a verified clone at `cae74c0`. |
| A5 | The v1.31 operator-batch file should be a new `.planning/v1.31-OPERATOR-BATCH.md` rather than a section in `139-01-SUMMARY.md` | Pattern 3 | Low, cosmetic. Both satisfy D-08's "recorded, actionable, not a gap". |
| A6 | The four-of-nine conflict disposition in §gh#15 Live State is the right split | §gh#15 Live State | Medium. Boxes 1/3/4/5 conflicting is derived from the locked milestone D-01 + C1 + C2 and matches CONTEXT.md's own "four of them conflict". Box 8's scope adjustment is a judgement call the operator's wording review will settle. |

Everything else in this document was measured live and is tagged `[VERIFIED]` at its point of use.

---

## Open Questions (RESOLVED)

All four were answered during phase planning, 2026-08-09. Each resolution below names the plan that
carries it; none required re-opening a locked decision.

1. **Should `138-BASELINE.md` be cited at all — and therefore should the meta branch be pushed?**
   - Known: it 404s at the pushed tip; it is absent from D-06's binding citation list; a meta push
     fires zero CI but is an operator-owned act by this project's Phase 138 precedent.
   - Unclear: whether the operator considers the push trivial enough to fold into the same gate.
   - **Recommendation:** drop the citation; the phase then has exactly one outward act. If the planner
     disagrees, add the push as a *separate* explicit line in the same `checkpoint:human-action`, never
     as an executor step.
   - **RESOLVED — recommendation taken.** `138-BASELINE.md` is dropped from the citation set, and the
     meta branch is **not** pushed. Owned by **139-01 Task 2 §1**, which records the drop with its reason
     in `139-CITATIONS.md` alongside the parallel decision not to cite `PROJECT.md`. All five plans carry
     an explicit `MUST NOT run git push` prohibition, so the phase's only outward act is the post itself.

2. **Does the comment name `write --pulse-us`?**
   - Known: it is milestone locked decision D-04 (ROADMAP §v1.31 line 19) and it is genuinely
     user-facing — it is *the* answer to "what if the database's pulse is wrong for my part". But
     CONTEXT.md's D-04 shape list does not include it, and HOST work is Phase 143.
   - **Recommendation:** one clause, marked **proposed** like every other numeric/shape claim. It
     strengthens D-11's community ask (a reader with a logic analyzer can override the pulse and
     report back). Planner's call; either choice is defensible.
   - **RESOLVED — recommendation taken.** Yes, one clause, marked proposed. Owned by **139-03 Task 1**,
     final paragraph of the action ("One clause may mention that a per-run pulse override (`--pulse-us`)
     is proposed, so a reader with a logic analyzer can override the database value and report back;
     mark it proposed like every other shape claim").

3. **Does the corrected criteria list render as a checklist or a table?** Explicit Claude's Discretion.
   Note one mechanical consideration: `- [ ]` inside the body's `<details>` block plus a new `- [ ]`
   list makes `grep -c '^- \[ \]'` ambiguous as an assertion — a table for the *new* list keeps the
   nine-original-boxes count cleanly assertable.
   - **RESOLVED — table, in both artifacts, for exactly that mechanical reason.** Owned by **139-03
     Task 1** ("Render it as a markdown table with one row per box, so the count of original checkbox
     lines stays cleanly assertable elsewhere") and **139-04 Task 1 step 5** ("A table rather than a
     checklist is deliberate: it keeps the count of `- [ ]` lines in this file equal to the nine
     originals preserved below"). The mandated column order is original box · disposition · reason in
     both files; 139-04 Task 2's box-anchored cross-check reads the second column and depends on it.

4. **Is `handle->pulse_delay` serving as both the program pulse (`memory.cpp:329`) and the erase pulse
   (`eprom.cpp:283`) worth stating publicly?**
   - Known: it is true, it was discovered while correcting F-02, and it is directly relevant to gh#15's
     "shared implementation helpers" section.
   - Unclear: whether it belongs in a correction comment or in Phase 141's work.
   - **Recommendation:** one sentence at most, framed as an observation, not a defect claim — it is
     out of ISSUE-01/02's scope and D-04 confines the comment to the corrected design's shape.
   - **RESOLVED — recommendation taken.** Owned by **139-03 Task 1**, C3 paragraph ("At most one
     sentence, framed as an observation rather than a defect claim, may note that `handle->pulse_delay`
     currently does double duty as both the program pulse and the erase pulse"). The two anchors are
     kept distinct throughout the phase: `memory.cpp:321-330` / `memory_set_data()` is the program
     pulse, `eprom.cpp:274-283` / `eprom_internal_erase()` is the erase pulse.

---

## Sources

### Primary (HIGH confidence — measured live this session)

- **GitHub API via `gh` 2.96.0** — `gh issue view 15 --repo henols/firestarter_prom --json …`
  (title, body, state, author, comments, createdAt, updatedAt, labels); `gh repo view` ×3;
  `gh api repos/henols/firestarter_app/commits/{8de307f,12286df}`;
  `gh api repos/henols/firestarter_prom/issues/{23,24,26,27,28,29,31,32}/comments`;
  `gh api repos/henols/firestarter_prom/issues/comments/{id}` (15 comment bodies surveyed);
  `gh auth status`; `gh issue comment --help`; `gh issue edit --help`
- **`raw.githubusercontent.com`** — HTTP status + content for 8 paths across all three repos at pinned SHAs
- **Local repos** — `git log/rev-parse/ls-remote/diff/status/merge-base/branch -r --contains` across
  `/workspaces`, `/workspaces/firestarter`, `/workspaces/firestarter_app`
- **Source read** — `firestarter/src/proms/eprom.cpp` (332 lines), `.../memory.cpp`,
  `firestarter_app/firestarter/database.py`, `firestarter_app/doc/infoic-field-dictionary.md`
- **minipro @ `cae74c0`** — `src/t48.c`, `tl866a.c`, `tl866iiplus.c`, `t56.c`, `t76.c`, `main.c`
- **Executed probes** — 5 runs of `check_permitted_claims.py` proving the three F-04 failure modes
- **AVR core** — `framework-arduino-avr/cores/arduino/Arduino.h:144`, `wiring.c`
- **Planning record** — `139-CONTEXT.md`, `139-DISCUSSION-LOG.md`, `137-05-PLAN.md`, `137-05-SUMMARY.md`,
  `137-GH12-COMMENT.md`, `137-RECORD.md`, `check_permitted_claims.py`, `122-DELIVERY.md`,
  `122-12-SUMMARY.md`, `v1.30-OPERATOR-BATCH.md`, `138-BASELINE.md`, `138-02-PULSE-DISTRIBUTION.md`,
  `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`,
  `seeds/27c-algorithm-fidelity-param-table-refactor.md`, `.github/workflows/catalog-sync-check.yml`,
  `.claude/settings.local.json`

### Secondary (MEDIUM confidence)

- **Arduino official reference — `delayMicroseconds()`**
  (https://docs.arduino.cc/language-reference/en/functions/time/delayMicroseconds/) — *"The largest
  value that will produce an accurate delay is 16383."* Reached via WebSearch (direct WebFetch returned
  empty) and **independently corroborated** by reading the AVR core's own `unsigned int` signature and
  the `us *= 4` overflow arithmetic, which is the stronger proof.
- **Project memory notes** — `reference_gh_workflow_run_blocked_by_automode_classifier` (corrected
  2026-08-09), `reference_auto_mode_autoapproves_outward_facing_gates`,
  `reference_phase_complete_clobbers_unrelated_phase_plans_line`,
  `reference_executors_prematurely_mark_requirements_complete`,
  `reference_pytest_addopts_q_suppresses_count_line`

### Tertiary (LOW confidence — flagged, not relied on)

- Knowledge graph at `.planning/graphs/graph.json` — **not queried**: `graphify status` reports
  `stale: true`, `age_hours: 930`, `commits_behind: 1052`, built at `f4150b8` vs current `cbc66d6`.
  Direct measurement was used throughout instead.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|---|---|---|
| gh#15 live state (nine boxes, author, zero comments) | **HIGH** | Read directly from the GitHub API this session; box count verified by `grep -c` |
| Citation resolution | **HIGH** | Every anchor fetched at its pinned public SHA and content-checked; two defects found and corrected (F-02, F-05) |
| C1/C2/C3 substance | **HIGH** | Reproduced verbatim from PROJECT.md; the seed cross-checked; the one erroneous sentence identified by arithmetic (F-03) |
| Claim-gate reuse (F-04) | **HIGH** | Proven by five executed probes, not by reading |
| Posting / byte-diff mechanics | **HIGH** | `122-DELIVERY.md` §3 is an executed record; endpoints re-verified live, including the 404 trap |
| D-10 mechanical precondition | **HIGH** | Three-ref blob equality measured; the gitlink false-green characterized |
| `gh issue` permission behavior | **MEDIUM** | Allowlist absence verified; classifier behavior inferred by analogy to a recorded finding — not exercised, because exercising it means posting |
| `delayMicroseconds()` ceiling | **HIGH** | Official docs + independent source-level confirmation of the 16-bit argument |
| minipro anchors | **MEDIUM-HIGH** | Verified against a real clone at `cae74c0`, but that clone is in an ephemeral scratchpad outside this workspace |

**Research date:** 2026-08-09
**Valid until:** **2026-08-16** (7 days) — gh#15 is a live object. Re-run `gh issue view 15 --json
state,comments,updatedAt` immediately before drafting and again immediately before the gate; a new
comment, a body edit, or a state change invalidates the amendment mapping and the before-counts. The
unpushed-commit count (8) also drifts with every meta commit.
</content>
</invoke>
