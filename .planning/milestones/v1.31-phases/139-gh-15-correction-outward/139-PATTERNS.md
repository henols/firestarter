# Phase 139: gh#15 Correction (outward) - Pattern Map

**Mapped:** 2026-08-09
**Files analyzed:** 11 (6 from RESEARCH §"Wave 0 gaps", plus the plan, the summary, an optional paired
test module, and two hold-branch in-place edits)
**Analogs found:** 11 / 11 (7 exact, 3 role-match, 1 mechanics-only-with-named-rejections)

**Scope note.** Phase 139 is **meta-repo-only**. It writes `.planning/` markdown, one small Python
gate script, and makes `gh` calls. It touches no file in `firestarter/` or `firestarter_app/` — those
are read-only citation sources. So the pattern library mapped here is `.planning/` itself. Every
excerpt below was read live this session from the path and line range named; nothing is paraphrased
from `139-RESEARCH.md`.

**What this document does not do.** It does not re-derive RESEARCH's F-01…F-09 findings, does not
re-decide any CONTEXT decision, and does not draft any comment prose. It answers one question per
artifact: *which existing file does the executor copy, and which exact lines?*

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `139-01-PLAN.md` | plan (gated outward act) | request-response (human gate in the middle) | `137-close-honesty-ledger-claim-gate-gh12-followup/137-05-PLAN.md` | **exact** |
| `139-GH15-COMMENT.md` | outward content artifact (THE deliverable) | one-shot publication | `137-.../137-GH12-COMMENT.md` | **exact** |
| `139-GH15-BODY-AMENDMENT.md` | outward content artifact (issue-body replacement) | one-shot publication, default-SKIP | `137-GH12-COMMENT.md` (voice) + gh#15's own live body (structure) | role-match |
| `139-GH15-ORIGINAL-CRITERIA.md` | verbatim-preservation capture | file-I/O capture from a live API read | `138-02-PULSE-DISTRIBUTION.md` §"Run 1" verbatim-input block; `122-DELIVERY.md` §6 "copy-pasted, not paraphrased" | role-match |
| `139-CITATIONS.md` | evidence register + verification transcript | batch verify → record | `138-BRANCH-BASES.md` §1 "Oracles" table; `122-DELIVERY.md` §1/§3 tables | **exact** (two donors) |
| `139-check-claims.py` | gate script (forbidden-claim scan) | transform → exit code | `137-.../check_permitted_claims.py` (**MECHANICS ONLY** — see §4 rejections) + `138-pulse-distribution.py` (non-vacuity + naming) | mechanics-only |
| `test_139_check_claims.py` *(optional)* | test (paired anti-hollow suite) | subprocess assertion | `137-.../test_check_permitted_claims_v130.py` | **exact** |
| `.planning/v1.31-OPERATOR-BATCH.md` | operator hand-off record | parked-command register | `.planning/v1.30-OPERATOR-BATCH.md` §A-1 | **exact** |
| `139-01-SUMMARY.md` | plan summary | record | `137-05-SUMMARY.md` | **exact** |
| `.planning/ROADMAP.md` Phase 140 `Depends on:` *(hold branch only)* | in-place annotation | edit | `137-05-SUMMARY.md` §"Deviations" (REQUIREMENTS.md CLOSE-06 annotated in place, not ticked) | role-match |
| `.planning/REQUIREMENTS.md` ISSUE-03 row *(hold branch only)* | in-place annotation | edit | same as above | **exact** |

---

## Pattern Assignments

### 1. `139-01-PLAN.md` — the three-task gated-outward-act skeleton

**Analog:** `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-05-PLAN.md`
(302 lines — read in full this session)

This is the worked instance of Phase 139's exact gate. CONTEXT D-09 says copy its task shape
**wholesale**. Quoted here so the planner does not have to re-open it.

#### 1a. Frontmatter, verbatim (`137-05-PLAN.md:1-32`)

```yaml
---
phase: 137-close-honesty-ledger-claim-gate-gh12-followup
plan: 05
type: execute
wave: 5
depends_on: ["137-04"]
files_modified:
  - .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md
  - .planning/v1.30-OPERATOR-BATCH.md
autonomous: false
requirements: [CLOSE-06]
user_setup:
  - service: github
    why: "CLOSE-06's blocking operator wording review of the gh#12 follow-up reply, and (conditionally) authorizing/posting it"
    dashboard_config:
      - task: "Read the review packet (Task 1's output) and the current draft, then explicitly approve the wording or name exact corrections, AND state whether the removal has actually shipped and posting should happen now, or should be held"
        location: "This plan's Task 2 checkpoint, presented in the execution transcript"
must_haves:
  truths:
    - "The gh#12 reply is never posted without a genuine, real-time operator wording approval — this task type is checkpoint:human-action specifically because --auto/--chain auto-approve checkpoint:human-verify gates but NEVER checkpoint:human-action gates (per this project's own established practice for outward-facing irreversible acts)"
    - "The draft at .planning/v1.30-GH12-REPLY-DRAFT.md is treated as INPUT, never re-authored from scratch"
    - "write --sdp-relock is never named as available in the frozen reply text"
    - "Actual posting to GitHub requires BOTH a live, mechanical confirmation that the removal has shipped AND the operator's explicit real-time instruction to post now -- absent either signal, the reply is frozen and reviewed, but posting is deferred as a named follow-up, never silently skipped and never silently performed"
  artifacts:
    - path: ".planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md"
      provides: "The operator-approved, frozen gh#12 reply text (byte-identical to what would be/was posted)"
  key_links:
    - from: ".planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md"
      to: ".planning/v1.30-GH12-REPLY-DRAFT.md"
      via: "the frozen file is the draft, unchanged or corrected exactly per the operator's named edits -- never a fresh re-authoring"
      pattern: "sdp-relock"
---
```

**Fields present:** `phase`, `plan`, `type`, `wave`, `depends_on`, `files_modified`, `autonomous`,
`requirements`, `user_setup`, `must_haves{truths,artifacts,key_links}`.
**Fields ABSENT — note for Phase 139:** there is **no `commits_land_in:` key** in this frontmatter.
137-05 was meta-only and did not need one. Phase 139 is also meta-only, but CONTEXT.md §Phase
Boundary states `commits_land_in:` is the meta repo explicitly — and the recorded project finding
(worktrees leave submodules empty; the gate under-detects) prefers `commits_land_in:` over
`files_modified` for repo-ownership. **This is the one frontmatter delta the planner should add
rather than copy.**

**Substitutions for Phase 139:** `requirements: [ISSUE-01, ISSUE-02, ISSUE-03]` — but see §"Shared
Patterns → Requirement ticking" before assigning all three to one plan.

#### 1b. Task XML shape (three tasks, `137-05-PLAN.md:91-249`)

```
<tasks>
  <task type="auto">                                   Task 1  — assemble packet, freeze candidate
    <name> <files> <read_first> <action>
    <acceptance_criteria> <verify><automated> <done>
  </task>
  <task type="checkpoint:human-action" gate="blocking">Task 2 — BLOCKING review + authorization
    <name> <files> <read_first> <what-built> <action>
    <acceptance_criteria> <verify><human-check> <resume-signal> <done>
  </task>
  <task type="auto">                                   Task 3 — apply corrections, freeze, branch
    <name> <files> <read_first> <action>
    <acceptance_criteria> <verify><automated> <done>
  </task>
</tasks>
```

Note the element asymmetry: only the checkpoint task carries `<what-built>` and `<resume-signal>`,
and it uses `<verify><human-check>` where the auto tasks use `<verify><automated>`.
Post-`</tasks>` sections, in order: `<threat_model>`, `<verification>`, `<success_criteria>`,
`<output>`.

#### 1c. The `checkpoint:human-action` task, **in full** (`137-05-PLAN.md:151-197`)

This is the block CONTEXT D-09 says is copied wholesale.

```xml
<task type="checkpoint:human-action" gate="blocking">
  <name>Task 2: BLOCKING operator wording review AND explicit posting authorization</name>
  <files>none (gate only)</files>
  <read_first>
    - The review packet from Task 1.
    - `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md`
    - `.planning/v1.30-GH12-REPLY-DRAFT.md`'s "Notes for the reviewer" section.
  </read_first>
  <what-built>
The gh#12 follow-up reply is drafted (2026-08-05, per `.planning/v1.30-GH12-REPLY-DRAFT.md`), copied
unmodified into this phase's own `137-GH12-COMMENT.md`, and mechanically scanned clean against this
milestone's own claim gate (no forbidden phrase, `write --sdp-relock` not named as available). A live
check of whether the removal has actually shipped has been run and its result is in the packet.
  </what-built>
  <action>
Present the packet and BLOCK until the operator answers BOTH of the following. Do not proceed on
silence, and do not treat `auto_advance`/`--auto`/`--chain` as an answer to either question — this task
type is `checkpoint:human-action` specifically so that no automated mode ever supplies these answers.

1. **Wording.** Read `137-GH12-COMMENT.md`. Approve it as-is, or name the exact sentences that must
   change. Two things must never be true regardless of any correction: (a) it must never claim the
   lock is proven/verified/works on silicon — only "checkable"/"built to surface it"; (b) it must never
   name `write --sdp-relock` as available now.
2. **Posting authorization and timing.** State one of:
   - "Approved, and the removal has already shipped — post it now" (only say this if you have
     independently confirmed a new release is public; Task 1's live check result is in the packet as a
     cross-check, not a substitute for your own knowledge), OR
   - "Approved, but hold — do not post until I say so" (the expected answer today, since the beta push
     has not happened yet), OR
   - name corrections, in which case restate one of the two options above once the corrections are
     described.

Capture the operator's verdict **verbatim** in the plan SUMMARY, including which of the two posting-
timing options they chose. If they name corrections, apply **exactly** those corrections in Task 3 — no
silent auto-approval and no rewording beyond what was asked for.
  </action>
  <acceptance_criteria>
    - The operator's verdict is recorded verbatim in the SUMMARY, including an unambiguous choice between "post now" and "hold".
    - If corrections were named, each is traceable to a line of the verbatim verdict.
    - Nothing was posted before or during this task: `gh issue view 12 --repo henols/firestarter_prom --json comments -q '.comments | length'`'s count is unchanged from before this plan started (record the before-count in the SUMMARY for comparison).
  </acceptance_criteria>
  <verify>
    <human-check>The operator has typed an explicit wording approval (or named corrections) AND an explicit posting-timing choice ("post now" or "hold"), both recorded verbatim in the SUMMARY.</human-check>
  </verify>
  <resume-signal>Type "approved, post now" / "approved, hold" / or name the sentences that must change plus your posting-timing choice.</resume-signal>
  <done>The operator has explicitly answered both questions; the verdict is recorded verbatim; nothing has been posted.</done>
</task>
```

**Phase 139 adaptation (three questions, not two).** CONTEXT D-01 adds a third authorization: the
optional body edit, **default SKIP**. Extend the `<action>` numbered list to 3 items and extend
`<resume-signal>` accordingly; keep every other element structurally identical. RESEARCH §"Anti-patterns"
is explicit that wording ≠ posting ≠ body-edit and they must be three separately-recorded answers.

#### 1d. The objective's `--auto`/`--chain` prohibition, verbatim (`137-05-PLAN.md:63-67`)

```
**This plan, and this phase, must NOT be executed under `--auto`/`--chain`** (ROADMAP's own explicit
instruction for Phase 137). Task 2 below is written so that even if a future execution session runs
under one of those flags anyway, the `checkpoint:human-action` type is never auto-approved by this
project's own execution machinery — but the correct operational answer is: do not pass either flag for
this phase at all.
```

Copy this paragraph into `139-01-PLAN.md`'s `<objective>` with "137" → "139". D-09 requires it.

#### 1e. Threat-model entries T-137-16 and T-137-18, verbatim (`137-05-PLAN.md:265` and `:267`)

Table header (`137-05-PLAN.md:262-263`):

```
| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
```

```
| T-137-16 | Repudiation | `--auto`/`--chain` silently supplying an approval that was never given | critical | mitigate | Task 2 is `checkpoint:human-action`, not `human-verify` — per this project's own established practice, only `human-action` is presented to the operator regardless of auto-mode |
```

```
| T-137-18 | Repudiation | a genuine follow-up silently dropped if posting is deferred | high | mitigate | The operator-batch A-1 row is updated with the exact follow-up command and the frozen file's blob SHA, in the same task that decides not to post |
```

RESEARCH's threat register already maps these forward as T-139-01 (inherits T-137-16) and T-139-07
(inherits T-137-18). Two neighbours are worth carrying too — `T-137-15` (posting before a stated
precondition holds → Phase 139's D-10 `eprom.cpp`-untouched analogue, RESEARCH T-139-03) and
`T-137-SC` (`| T-137-SC | Tampering | npm/pip/cargo installs | high | accept | Zero installs in this
plan's scope |`), which Phase 139 reproduces verbatim as T-139-SC.

#### 1f. Trust-boundary table, verbatim (`137-05-PLAN.md:254-259`)

```
| Boundary | Description |
|----------|-------------|
| operator's real-time wording judgement → permanent public GitHub comment | The exact boundary CLOSE-06 exists to gate |
| an execution session run under `--auto`/`--chain` → this plan's checkpoint | The reference note's documented failure mode; `checkpoint:human-action` typing is the mitigation, not the `autonomous: false` frontmatter flag alone |
| "reviewed" text → "posted" text | The freeze (blob SHA + byte length) plus a live byte-diff after any actual post is what proves the two are identical |
```

All three transfer unchanged (substitute ISSUE-03 for CLOSE-06 in row 1).

---

### 2. The freeze mechanism — **two donors, and they are not interchangeable**

**Bottom line for the planner: copy `137-05-PLAN.md` for the PLAN STRUCTURE; copy
`122-DELIVERY.md` §3 for the EXECUTABLE RECIPE.** 137-05's byte-diff was written but never
executed (the hold branch was taken, per `137-05-SUMMARY.md:133-137`), and its wording —
"must be identical" — would have **failed on a correct post**, because GitHub appends one
trailing newline. 122-12 ran four outward calls and measured that behaviour.

#### 2a. The freeze pair (blob SHA + byte length) — written form, `137-05-PLAN.md:208-210`

```
Re-run the claim gate alone (env seam) — must exit 0. Commit the file, then
record its git blob SHA (`git rev-parse HEAD:<path>`) and byte length (`wc -c`) in the SUMMARY — the
freeze values that would prove posted-text-equals-reviewed-text if and when posting happens.
```

Realized values, `137-05-SUMMARY.md:139-146`:

```
**Freeze values** (the file was already committed under the operator's approval, before this session):
- Blob SHA: `3a628c56de4d45dfe2be0c645fced0e25d5ebceb`
- Byte length: **2646 bytes**
- Committing commit: `3596604d1ec614d2cc1ab96dbb8adab0350f38bd`
```

Three values, not two: **blob SHA, byte length, and the committing commit**. Copy all three.

#### 2b. The post-hoc byte-diff — **137-05's version (WRITTEN, NEVER EXECUTED, and wrong)**

`137-05-PLAN.md:213-221`:

```
- **If the operator's verdict said "post now" AND a FRESH re-run of Task 1's live shipped-check
  (re-run now, not reused from Task 1 — origin/beta and PyPI may have changed between the two tasks)
  confirms SHIPPED:** post via
  `gh issue comment 12 --repo henols/firestarter_prom --body-file 137-GH12-COMMENT.md`. Immediately
  verify: `gh issue comment` output includes a comment URL; fetch the comment back
  (`gh api repos/henols/firestarter_prom/issues/comments/<id> -q .body`) and diff it byte-for-byte
  against the frozen `137-GH12-COMMENT.md` — must be identical. Confirm the issue is still `OPEN` (no
  label flag sent). Record the comment URL and the byte-diff result in the SUMMARY. This branch ticks
  CLOSE-06 as fully discharged, posting included.
```

What to keep from it: the **dual-signal fail-closed structure** ("operator's 'post now'" AND "a FRESH
re-run … not reused"), the "still `OPEN` (no label flag sent)" assertion, and the requirement to record
the URL. What to **reject**: "diff it byte-for-byte … must be identical" — no normalization is named,
and this line never ran.

#### 2c. The post-hoc byte-diff — **122-DELIVERY.md's version (EXECUTED, 4×)**

`122-DELIVERY.md:62-76`:

```
**Normalization applied, stated once for all four rows:** CRLF→LF (no CRLF present in any of the
four retrieved bodies — a no-op in practice) and collapsing to a single trailing newline. In every
one of the four cases the *only* difference between the committed file and the retrieved body was
GitHub appending exactly one trailing newline the committed file did not already end with; the byte
length differs by exactly 1 in all four cases, and the line-level `diff` shows exactly one added
blank line at end-of-file and nothing else. No other divergence occurred on any of the four calls.

**Retrieval commands used for the byte-equality proof:**
- Release bodies: `gh release view <tag> --repo <repo> --json body -q '.body'`, piped through
  `tr -d '\r'`, written to a file in `$(mktemp -d)`.
- Issue comments: `gh issue view <n> --repo henols/firestarter_prom --json comments -q
  '.comments[-1].body'`, piped through `tr -d '\r'`, written to a file in `$(mktemp -d)`.
- Comparison: `diff <(sed -e '$a\' <committed file>) <(sed -e '$a\' <retrieved file>)` — the
  `sed -e '$a\'` idiom ensures both sides end in exactly one newline before comparing, isolating the
  trailing-newline normalization from any real content difference.
```

The `sed -e '$a\'` idiom is the whole trick. The normalization must be **named in the plan text before
posting**, not discovered afterwards.

#### 2d. The pre-flight re-assertion table (`122-DELIVERY.md:20-28`) — copy this shape into `139-CITATIONS.md`

```
| File | Frozen blob SHA (`122-11-SUMMARY.md`) | Re-measured blob SHA (this plan, pre-call) | Match | `git status --porcelain` |
|---|---|---|---|---|
| `122-GH12-COMMENT.md` | `454db0fd48540b3b0e56eaa116340071c02164c6` | `454db0fd48540b3b0e56eaa116340071c02164c6` | ✅ | empty |
```
```
All four SHAs matched exactly. The working tree carried zero uncommitted changes to any of the
four files. Nothing the operator did not review was posted.
```

#### 2e. The exact-increment state assertion (`122-DELIVERY.md:78-103`)

```
$ gh issue view 12 --repo henols/firestarter_prom --json state,comments,labels -q '{state:.state,n:(.comments|length),labels:.labels}'
{"labels":[],"n":8,"state":"OPEN"}
```
```
| Assertion | Issue 11 | Issue 12 | Result |
|---|---|---|---|
| Comment count incremented by exactly 1 | 12 → 13 | 8 → 9 | ✅ both exactly +1 |
| `state` still `OPEN` | `OPEN` | `OPEN` | ✅ neither closed |
| Label list still empty | `[]` | `[]` | ✅ zero labels on either issue |
| New comment author | `henols` (the authenticated `gh` account posting on the operator's behalf) | `henols` | recorded |
```

For gh#15 the increment is `0 → 1`, which makes `.comments[-1]` unambiguously ours.

#### 2f. The negative-flag audit (`122-DELIVERY.md:132-154`) — a table Phase 139 should reproduce

```
| Forbidden flag | Present in any of the 4 calls? |
|---|---|
| `--label` / `--add-label` / `-l` | **No** |
| `--assignee` / `-a` | **No** |
| `--milestone` / `-m` | **No** |
| `--project` / `-p` | **No** |
| `--web` / `-w` | **No** |
| `--editor` / `-e` | **No** |
| `--edit-last` / `--delete-last` | **No** |
| `--body` (inline string form, issue comment) | **No** — `--body-file` used exclusively |
| Heredoc / shell-piped body construction | **No** — every body/notes argument is a literal committed file path |
| `gh issue close` | **No** — never invoked, on either issue |
| `gh auth token` | **No** — never invoked at any point in this plan |
```

Phase 139 adds one row for `gh issue edit`: `--add-label` / `--remove-label` exist on that subcommand
and must not be passed (RESEARCH §Code Examples confirms this against `gh 2.96.0`).

---

### 3. `139-GH15-COMMENT.md` — the prose skeleton

**Analog:** `.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md`
(46 lines — read in full this session)

**File shape.** No YAML frontmatter. No `#` title heading. The file **is** the comment body, byte for
byte — first character of line 1 is the first character the reader sees on GitHub. Headings are
**bold paragraphs** (`**What's changing**`), never `##`. This matters mechanically: the byte-diff in
§2c compares this file directly against the retrieved body, so anything a planning-artifact header
would add is corruption.

**Section order (four movements, `137-GH12-COMMENT.md`):**

| Lines | Section | Register |
|---|---|---|
| 1-2 | *(untitled opening)* — why I am posting, in two sentences | first person, states the trigger |
| 4-18 | `**What's changing**` — what is gone, split into what survives vs what does not | bulleted, each bullet leads with a bolded verdict |
| 20-25 | `**What did get better**` — the genuine improvement, stated without inflation | one paragraph |
| 27-46 | `**This is where I need help, and it's the honest reason `dev test` exists**` — the ask | ends the comment |

#### 3a. The opening, verbatim (`137-GH12-COMMENT.md:1-2`)

```
Following up here, because `firestarter dev sdp` was named in this thread and in the `3.0.0b14`
release notes, and it's being removed.
```

Two lines. States the trigger and the change, nothing else. No greeting, no preamble, no "I wanted to
take a moment". CONTEXT §Specific Ideas ("Lead with the self-correction, not with the evidence") maps
onto exactly this: *I filed this, two numbers are wrong, one premise is inverted, here is what
changes* — one short paragraph, evidence after.

#### 3b. The plain-spoken concession — the sentence that sets the register (`137-GH12-COMMENT.md:16-19`)

```
This isn't the "enable/disable" you asked for. You asked for both, and what you get is one of them
automatically and none of the other. There's a second limitation worth stating: the protection bit on
these parts can't be read back, so even when a part is protected, nothing can show you that it is.
```

This is the register D-02 carries forward: name the shortfall in the reader's own words before they
have to. Phase 139's analogue is the 6.25 V ceiling paragraph (D-05, ISSUE-02) — *its own paragraph,
not a footnote*, and framed as a limit on what **any** implementation of gh#15 on this shield can
claim.

#### 3c. The bulleted kept/withdrawn split (`137-GH12-COMMENT.md:9-14`)

```
- **`disable`'s behaviour survives, and you no longer need a command for it.** Unlocking is already
  what `write` does by default on every protocol-`0x0D` part — it auto-unlocks unless you pass
  `--skip-sdp-unlock`. So `dev sdp disable` was genuinely redundant, not merely dropped.
- **`enable` is withdrawn, with no replacement in this release.** If you want a part deliberately
  left protected, there is currently no supported way to do it. The design for one is settled and the
  work is queued, but it is not in this release and I'm not going to promise a version for it.
```

Note the shape: **bold verdict sentence first**, then the mechanism, then a closing clause that
forecloses the obvious misreading ("genuinely redundant, not merely dropped"). This is the exact
shape D-03's nine-box kept/corrected/replaced dispositions want — RESEARCH §"gh#15 Live State"
already supplies all nine rows with their reasons.

#### 3d. The community ask, verbatim in full (`137-GH12-COMMENT.md:27-46`)

D-11 mirrors this. It is the closing movement, and it is longer than "four lines" in 137 — D-11
constrains Phase 139's to four.

```
**This is where I need help, and it's the honest reason `dev test` exists**

I don't have most of these parts. No AT28C silicon was tested during this milestone — I can't buy
one of everything, and a lot of what the database
claims about a chip has never been checked against the actual silicon — including the AT28C family in
this thread. That's not a gap I can close on my own bench.

`dev test` is built for exactly that. If you have a part — the AT28C from this thread, or anything
else:

```
firestarter dev test <chip>
```

It derives what that chip's protocol supports, runs each operation as an independent step, and writes
a diagnostic report you can file straight back to this repo. Non-destructive by default; add
`--destructive` only on a chip you're willing to risk, and it'll tell you what it skipped without it.

One run from a part in someone's hand tells us more than anything I can derive from the database. If
the SDP lock doesn't actually hold on real AT28C silicon, a report is how we find out.
```

Four transferable moves: (1) name the missing evidence as *mine to lack*, not the reader's to supply;
(2) name the specific parts; (3) give a runnable command; (4) close with one sentence saying what a
single report buys. D-11's parts are `M2716`/`M2732` (for `0x0B`) and `AM27C020` (for `0x08`), and the
unanswerable question is `0x0B` one-shot-vs-looped.

**One structural warning for the planner.** Line 30's caveat sentence exists because 137's claim gate
*required* it (`137-05-SUMMARY.md:79-86`, and `v1.30-OPERATOR-BATCH.md` A-4 records the operator
choosing to weave it into the ask rather than bolt it on as a disclaimer). Phase 139 should reuse that
technique — RESEARCH F-04 recommends making the 6.25 V ceiling sentence the gate's *required* caveat,
which makes the gate and ISSUE-02 the same check — but the ceiling paragraph must read as a
statement of the hardware limit, **not** as a disclaimer appended to satisfy a checker.

---

### 4. `139-check-claims.py` — mechanics donor, with the parts that MUST change marked

**Analog (mechanics only):**
`.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/check_permitted_claims.py`
(360 lines — read in full this session).
**Secondary analog (non-vacuity discipline + phase-prefixed naming):**
`.planning/phases/138-preconditions-baseline/138-pulse-distribution.py`.

RESEARCH F-04 proved by five executed probes that this checker cannot do D-05's job. Below, each
quoted block is labelled **COPY** or **CHANGE**.

#### 4a. **CHANGE** — `_HERE` and `_DEFAULT_TARGETS` (`check_permitted_claims.py:74-91`)

```python
# Module-top path constant (mirrors both donor checkers' shape). This is the
# ONLY directory `_DEFAULT_TARGETS` below is ever built from -- never a
# sibling-directory string constant, unlike the v1.23 copy this module's own
# docstring names as the anti-pattern to not repeat.
_HERE = os.path.dirname(os.path.abspath(__file__))

# Explicit four-element default target list -- the v1.30 closing artifacts.
# Never a wildcard expansion, never a recursive directory walk of any kind.
# The `fixtures/` subdirectory deliberately contains violating text and must
# never be reachable from this list -- if a future edit turns this into a
# wildcard-expanded or recursively-walked set, the fixtures directory would
# poison every default-mode run.
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "137-LEDGER.md"),
    os.path.join(_HERE, "137-DECISION.md"),
    os.path.join(_HERE, "137-RELEASE-NOTES-app.md"),
    os.path.join(_HERE, "137-GH12-COMMENT.md"),
]
```

`_HERE`'s **construction is correct and should be copied verbatim**; the *contents* of
`_DEFAULT_TARGETS` are the trap. A naive copy into `139-*/` leaves four `137-*.md` names that do not
exist there → the arming branch in §4d fires → exit 0 `UNARMED` (RESEARCH probe A).
**Phase 139 replacement:**

```python
_DEFAULT_TARGETS = [
    os.path.join(_HERE, "139-GH15-COMMENT.md"),
    os.path.join(_HERE, "139-GH15-BODY-AMENDMENT.md"),
]
```

Keeping `_HERE`-built defaults (rather than RESEARCH's "argv-only") is what gives the two mandatory
P-11 test legs (§4h, legs 10/11) something to assert. Combine both: argv precedence **and**
own-directory defaults **and** the never-vacuous guard **and** no arming branch. See §4d.

#### 4b. **CHANGE (delete entirely)** — the proximity gate (`check_permitted_claims.py:107-110` and `205-226`)

```python
# D-16-style proximity-window context tokens (v1.23 mechanics, adapted from
# its `py32` token to this milestone's own domain): AT28C part numbers, the
# bare word "SDP", and the protocol id "0x0D".
_SDP_CONTEXT_TOKENS = re.compile(r"at28c\w*|\bsdp\b|0x0d", re.IGNORECASE)
```

```python
    lines = text.splitlines()
    n = len(lines)

    def _window(i):
        return range(max(0, i - 1), min(n, i + 2))

    def _sdp_context_in_window(i):
        return any(_SDP_CONTEXT_TOKENS.search(lines[w]) for w in _window(i))
...
    for label, pattern in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(lines):
            for m in pattern.finditer(line):
                if _sdp_context_in_window(lineno) or _caveat_in_window(lineno):
                    forbidden_hits.append((label, m.group(0), lineno + 1))
```

This is RESEARCH probe E's vacuous green: gh#15's vocabulary is `0x07`/`0x08`/`0x0B` and **none of
`at28c`/`sdp`/`0x0d` ever appears**, so every forbidden hit is filtered out and the scan reports PASS.
Delete the window. RESEARCH's reasoning: *"applies no proximity gate (the whole file is on-topic — a
proximity window has nothing to buy here and everything to lose)."* Also delete the relational
`_SELF_VERIFYING_PATTERN` rule (`:169-172`, `:234-241`) and `_emission_in_window` (`:217-218`) — all
three are v1.30 SDP-domain machinery.

#### 4c. **CHANGE** — the vocabulary and the required caveat (`check_permitted_claims.py:118-181`)

The forbidden list, verbatim (14 entries; the first 8 forked from Phase 122, the last 6 v1.30-specific):

```python
FORBIDDEN_PATTERNS = [
    # -- forked verbatim from Phase 122's check_permitted_claims.py --
    ("verified-fixed", re.compile(r"verified\s+fixed", re.IGNORECASE)),
    ("confirmed-working", re.compile(r"confirmed\s+working", re.IGNORECASE)),
    ("silicon-verified", re.compile(r"silicon[-\s]verified", re.IGNORECASE)),
    (
        "verified-on-silicon",
        re.compile(
            r"verified\s+(?:on|against)\s+(?:real\s+)?(?:at28c\w*|silicon)",
            re.IGNORECASE,
        ),
    ),
    (
        "works-on-silicon",
        re.compile(
            r"works?\s+on\s+(?:\w+\s+){0,2}(?:at28c\w*|silicon)", re.IGNORECASE
        ),
    ),
    ("now-works", re.compile(r"now\s+works?\b", re.IGNORECASE)),
    ("should-now-work", re.compile(r"should\s+now\s+work", re.IGNORECASE)),
    (
        "proven-on-silicon",
        re.compile(
            r"proven\s+on\s+(?:\w+\s+){0,2}(?:at28c\w*|silicon)", re.IGNORECASE
        ),
    ),
    # -- v1.30-specific additions, PITFALLS.md P-11 point 2 --
    (
        "lock-inhibited-the-write",
        re.compile(r"lock\s+inhibited\s+the\s+write", re.IGNORECASE),
    ),
    (
        # Do not confuse with the literal rendered enum values HELD/NOT-HELD
        # from chip_test.sdp_hold_state() -- those are permitted data, not a
        # prose causal claim. This pattern requires the words "the", "lock",
        # "held" in that order.
        "lock-held-unqualified",
        re.compile(r"\bthe\s+lock\s+held\b", re.IGNORECASE),
    ),
    ("proven-behaviour", re.compile(r"proven\s+behaviou?r", re.IGNORECASE)),
    (
        "behaviourally-verified",
        re.compile(r"behaviou?rally\s+verified", re.IGNORECASE),
    ),
    ("now-proven", re.compile(r"now\s+proven\b", re.IGNORECASE)),
    (
        "dev-test-proves-unqualified",
        re.compile(r"dev\s+test\s+proves\b", re.IGNORECASE),
    ),
]
```

```python
REQUIRED_CAVEAT_PROSE = "no AT28C silicon was tested"
REQUIRED_CAVEAT_PATTERN = re.compile(
    r"no\s+AT28C\s+silicon\s+was\s+tested", re.IGNORECASE
)
```

Both blocks are **v1.30 domain vocabulary and do not port**. `grep -c 'datasheet'` over this file
returns 0 — D-05's own three forbidden phrases are absent. Keep the **(label, compiled-regex) tuple
shape** and the `REQUIRED_CAVEAT_PROSE` / `REQUIRED_CAVEAT_PATTERN` pairing (prose for the error
message, regex for the match); replace the contents with v1.31 vocabulary per RESEARCH F-04:
`datasheet[-\s]conformant`, `datasheet[-\s]correct`, `algorithm[-\s]accurate`, plus
`verified on silicon`, `confirmed working`, `proven`, and any unqualified `datasheet-` compound —
and a required-caveat pattern built from the 6.25 V ceiling sentence.

Two carry-forward candidates from the 137 list that *are* still dangerous in a 27C comment:
`now-works` and `should-now-work` (both un-anchored to AT28C). Keep them; they cost nothing and cover
the "this now works" drift class.

#### 4d. **COPY (with one deletion)** — target resolution and the never-vacuous guard

`resolve_targets`, verbatim (`check_permitted_claims.py:247-268`) — precedence is argv → env seam →
defaults, with the `is not None` subtlety that makes an explicitly-empty env value resolve to **zero**
targets rather than silently falling back:

```python
def resolve_targets(argv):
    """Resolve the scan target list.

    Precedence: explicit positional `argv` paths win; else the
    FIRESTARTER_CLAIMSCAN_TARGETS_V130 env seam if the variable is present
    in os.environ (checked via `is not None`, not truthiness -- an
    explicitly empty value must resolve to zero targets, never a silent
    fall-back to defaults); else `_DEFAULT_TARGETS`.
    ...
    """
    if argv:
        return list(argv), False
    if FIRESTARTER_CLAIMSCAN_TARGETS_V130 is not None:
        return [
            p for p in FIRESTARTER_CLAIMSCAN_TARGETS_V130.split(os.pathsep) if p
        ], False
    return list(_DEFAULT_TARGETS), True
```

The hoisted never-vacuous guard, verbatim (`check_permitted_claims.py:288-295`) — RESEARCH names
exactly this block as the one part worth reusing:

```python
    targets, used_defaults = resolve_targets(argv)

    if not targets:
        print(
            "FAIL: no scan targets resolved -- the gate cannot vacuously "
            "pass with nothing scanned"
        )
        return 1
```

**DELETE the arming branch** (`check_permitted_claims.py:304-312`) — this is probe A's false green:

```python
    if used_defaults and len(missing) == len(targets):
        print(
            "UNARMED: none of Phase 137's 4 named closing artifacts exist "
            "yet ("
            + ", ".join(os.path.basename(t) for t in _DEFAULT_TARGETS)
            + ") -- Phase 137's four closing artifacts do not exist yet -- "
            "this is expected before they are authored, not a failure."
        )
        return 0
```

Arming existed because v1.30 authored its gate **before** its artifacts. Phase 139 authors the gate in
the same task as the artifacts, so there is no pre-authored window to protect and no reason to keep an
exit-0-on-nothing-scanned path. **Keep** the fail-closed missing-file branch that follows
(`:314-319`):

```python
    if missing:
        print(
            "FAIL: scan target(s) not found on disk -- the gate cannot "
            f"vacuously pass with a target silently skipped: {missing}"
        )
        return 1
```

#### 4e. **COPY** — the bucketed failure printer and the PASS line (`check_permitted_claims.py:271-276`, `343-356`)

```python
def _print_bucket(label, violations):
    print(f"FAIL: {len(violations)} {label}:")
    for v in violations[:20]:
        print(f"  {v}")
    if len(violations) > 20:
        print(f"  ... and {len(violations) - 20} more")
```

```python
    if forbidden_violations or caveat_violations:
        if forbidden_violations:
            _print_bucket("forbidden phrase match(es)", forbidden_violations)
        if caveat_violations:
            _print_bucket("missing required silicon caveat", caveat_violations)
        return 1

    print(
        f"PASS: scanned {', '.join(os.path.relpath(s, _HERE) for s in scanned)}; "
        f"{caveat_present_count} file(s) carry the required silicon caveat "
        "(this PASS is the mechanizable half of the honesty ledger "
        "discipline only -- see the module docstring's explicit non-claim)"
    )
    return 0
```

The **PASS line naming every scanned file** is load-bearing (it is what test 7 asserts, and what makes
a silent skip visible). Keep it. Keep the parenthetical non-claim too — a green run is the
mechanizable half only, and D-08's operator wording review is the other half.

#### 4f. **COPY (adapt wording)** — the module docstring's explicit non-claim (`check_permitted_claims.py:43-49`)

```
**Explicit non-claim (load-bearing):** a green run of this gate -- at any
point in the phase -- is the mechanizable half of CLOSE-04's honesty ledger
discipline only. It cannot detect an implied overclaim, a misleading
omission, or wrong tone. That is CLOSE-06's blocking operator wording review
(plan 137-05). A green run of this gate must never be reported, in any
SUMMARY, ledger entry, or Phase 137 artifact itself, as by itself satisfying
the honesty ledger discipline.
```

Substitute: CLOSE-04 → D-05/ISSUE-02, CLOSE-06 → ISSUE-03's Task 2 gate. Phase 139's docstring must
also carry a **scope non-claim**: this is *compliance* with CLOSE-01's spirit, not a build of CLOSE-01
(which is Phase 146's, per CONTEXT §Deferred Ideas). RESEARCH states this boundary explicitly.

#### 4g. Naming — and a real trap

Two naming precedents exist in `.planning/`:

| Precedent | File | Importable as a module? |
|---|---|---|
| Phase 137 | `check_permitted_claims.py` (snake_case, no phase prefix) | yes |
| Phase 138 | `138-pulse-distribution.py` (phase-prefixed, hyphenated) | **no** |

RESEARCH prescribes `139-check-claims.py` — the Phase-138 shape, which matches this milestone's own
in-flight convention and makes the file self-identifying. **`import 139_check_claims` is a
SyntaxError and `import 139-check-claims` is not a name** — but this costs nothing, because the paired
test module never imports by name: `subprocess.run([sys.executable, str(_SCANNER), ...])` for legs 1-9
and `importlib.util.spec_from_file_location("<any_name>", str(_SCANNER))` for legs 10-11 both accept an
arbitrary path (§4h). The test module itself must still be a legal module name — `test_139_check_claims.py`
is fine.

Env-seam naming: if a seam is kept at all, PITFALLS P-11 point 5 makes suffixing mandatory —
`FIRESTARTER_CLAIMSCAN_TARGETS_V131`, never the bare name already used by three checkers.

#### 4h. The paired test module — **it exists, and here is its shape**

`.planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/test_check_permitted_claims_v130.py`
(349 lines), with committed fixtures in `137-.../fixtures/`:
`clean_control.md`, `clean_control_second.md`, `planted_forbidden_claim.md`,
`planted_missing_caveat.md`, `planted_self_verifying_unqualified.md`.

Docstring's governing claim (`test_check_permitted_claims_v130.py:1-14`):

```
This is the MANDATORY anti-hollow pairing for the v1.30 claim gate: a
checker with no negative-fixture test is exactly this project's v1.12
hollow-GATE-03 failure mode -- a declared-empty detector that could never
fail because nothing concrete was asserted against it. Every planted-
violation test below invokes the checker as a real subprocess against a
committed fixture file via the FIRESTARTER_CLAIMSCAN_TARGETS_V130 env seam
-- never an in-process import -- so a passing test suite proves the checker
itself (not the test) fails the build on a real violation.
```

The two harness helpers, verbatim (`:68-100`) — copy both:

```python
def _run_scanner(targets=None, argv=None):
    """Invoke the scanner as a real subprocess. ..."""
    env = {**os.environ}
    if targets is not None:
        env["FIRESTARTER_CLAIMSCAN_TARGETS_V130"] = targets
    else:
        env.pop("FIRESTARTER_CLAIMSCAN_TARGETS_V130", None)
    return subprocess.run(
        [sys.executable, str(_SCANNER), *(argv or [])],
        cwd=str(_HERE),
        capture_output=True,
        text=True,
        env=env,
    )


def _import_scanner_module():
    """Import check_permitted_claims.py by file path (never as a package)
    solely to introspect its module-level `_DEFAULT_TARGETS` constant --
    used only by legs 10 and 11 ..."""
    spec = importlib.util.spec_from_file_location(
        "check_permitted_claims_v130_introspect", str(_SCANNER)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

The planted-failure leg (`:126-140`) — the shape Phase 139's non-vacuity obligation copies:

```python
def test_planted_forbidden_phrase_flips_checker_to_failure():
    """The committed planted_forbidden_claim.md fixture MUST fail the gate,
    attributed to the lock-inhibited-the-write label ..."""
    result = _run_scanner(targets="fixtures/planted_forbidden_claim.md")
    assert result.returncode != 0, (
        f"scanner exited 0 on a planted forbidden-phrase violation.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "FAIL:" in result.stdout, (
        f"Expected 'FAIL:' in output but got:\n{result.stdout}"
    )
    assert "lock-inhibited-the-write" in result.stdout, (
        f"Expected the lock-inhibited-the-write label in output but got:\n{result.stdout}"
    )
```

Note the assertion strength: not just non-zero exit — it names **the specific label**, so a checker
that fails for an unrelated reason (RESEARCH probe B's irrelevant caveat failure) still goes red.

The two **mandatory P-11 legs** (`:314-349`), which are precisely what defuses the `_HERE` trap for a
future copy:

```python
def test_default_targets_resolve_inside_this_phase_directory():
    module = _import_scanner_module()
    expected_dir = str(_HERE.resolve())
    for entry in module._DEFAULT_TARGETS:
        assert os.path.dirname(entry) == expected_dir, (
            f"_DEFAULT_TARGETS entry {entry!r} does not resolve inside this "
            f"phase's own directory {expected_dir!r} -- this is the exact "
            "cross-phase-copy defect this test exists to catch"
        )


def test_default_target_basenames_are_this_milestones():
    module = _import_scanner_module()
    for entry in module._DEFAULT_TARGETS:
        basename = os.path.basename(entry)
        assert basename.startswith("137-"), (
            f"_DEFAULT_TARGETS basename {basename!r} does not carry this "
            "milestone's own '137-' prefix -- this is the exact stale-name "
            "defect this test exists to catch"
        )
```

`"137-"` → `"139-"`. These two legs are the mechanical reason to keep `_DEFAULT_TARGETS` rather than
go argv-only.

Also copy legs 5 and 6 (`:188-223`) — fail-closed on a nonexistent target, and never-vacuous on an
explicitly empty target list, which asserts `"PASS:" not in stdout` **and** `"UNARMED:" not in stdout`.
Drop leg 9 (ARMED-and-green against four v1.30 artifacts) and leg 4 (self-verifying) as domain-specific.

**Running it** (`139-VALIDATION.md` and RESEARCH both note this): the meta repo has no pytest workflow
and no config; 137 ran its module directly from the phase dir. Project `addopts` is `-ra -q`, so use
`-o addopts=""` to see the count line.

#### 4i. Fixture strategy — two precedents, planner picks

| Precedent | Where the planted input lives | Recorded how |
|---|---|---|
| Phase 137 | **committed** under `137-.../fixtures/` | referenced by path in the test |
| Phase 138 | scratchpad only, **never committed**, deleted after the run | content reproduced verbatim in `138-02-PULSE-DISTRIBUTION.md` §"Run 1" |

Phase 138's record, verbatim (`138-02-PULSE-DISTRIBUTION.md:22-30`) — this is the in-milestone house
style and matches RESEARCH's `/tmp/planted.md` code example:

```
## Run 1 — the non-vacuity proof (planted failure)

A gate that has only ever passed is untrusted. Before this script's `RESULT: PASS` was relied
on for Runs 2 and 3 below, it was observed to **FAIL**, for an attributable reason, against a
deliberately-broken synthetic database. The input lived only in the session scratchpad
directory — never inside `firestarter`, never inside `firestarter_app`, never inside
`.planning/` — and was deleted immediately after this run; it was **never committed**. Its
exact content (reproduced here so the exercise itself stays re-creatable even though the file
is gone) was ...
```

**Recommendation:** if a paired pytest module is written, fixtures must be committed (Phase 137's
shape) or the suite is not re-runnable. If only an inline planted-failure run is done (RESEARCH says
this suffices), use Phase 138's shape and reproduce the planted text verbatim in `139-CITATIONS.md`
or the SUMMARY. Either way the run must be **recorded**, not merely performed.

---

### 5. `139-CITATIONS.md` — the evidence-register shape

**Analogs:** `138-BRANCH-BASES.md` §1 (the "Oracles" table) for per-anchor verification;
`122-DELIVERY.md` §1/§3 for the freeze/delivery tables (§2d/§2e above).

#### 5a. Header + measurement-discipline preamble (`138-BRANCH-BASES.md:1-9`)

```markdown
# Phase 138 Plan 01: Branch Bases — PREP-01 / PREP-02 Adjudication

**Owner requirement:** PREP-01 (`firestarter_app`'s v1.30 branch merged into `origin/beta`, verified)
and PREP-02 (milestone branches exist in all three repos off their decided bases, each verified by
naming the base commit, not assumed).

**Measured:** 2026-08-08, this session, live and read-only. Per the plan's own instruction, nothing
below is copied from `138-RESEARCH.md` — every command was re-run fresh, and any divergence from
research's recorded figures is stated explicitly rather than reconciled.
```

Copy this preamble shape exactly. For Phase 139 the divergence clause is load-bearing: RESEARCH's
citation register was measured 2026-08-09 and its own §Metadata sets a **7-day validity** and
instructs re-reading gh#15 live before drafting and again before the gate.

#### 5b. The Oracles table — command-as-run beside result (`138-BRANCH-BASES.md:19-23`)

```markdown
| Oracle | Command (as run) | Result |
|--------|-------------------|--------|
| 1. GitHub PR record | `gh pr view 44 --repo henols/firestarter_app --json state,mergedAt,mergeCommit` | `state=MERGED`, `mergedAt=2026-08-05T21:13:01Z`, `mergeCommit.oid=568e58b903338d6e9191b2a165fa0e876c1c84dc` |
| 1b. Merge-commit parent count | `git log -1 --format='%h parents=[%p]' 568e58b` | `568e58b parents=[16a313a]` — **single parent**, confirming a squash (a true merge would show 2 parents) |
| 2. Ancestry | `git merge-base --is-ancestor gsd/v1.30-sdp-surface-retirement origin/beta` | **exit 1** — measured, not assumed. This is the squash-merge false negative (see Section 2 mechanism) |
```

Three columns: **numbered oracle · the literal command · the literal result**. Numbered so later prose
can say "oracle 3 forward is the load-bearing proof". Phase 139's per-anchor rows should carry a
**fourth** column that no `.planning/` precedent has yet, because RESEARCH's Pitfall 2 demands it:
the **sliced line-range text actually returned**, not just a status. RESEARCH's own `verify_anchor`
helper prints `OK   <url>#L<a>-L<b>` — the register should record the matched substring beside it.

For the same reason, record the **enclosing function** for every source anchor (RESEARCH Pitfall 1:
`eprom.cpp:283` resolves, is a real `delayMicroseconds(handle->pulse_delay)`, and is the *erase* pulse).

#### 5c. The outward-act custody record (`138-BASELINE.md:15-25`) — quote this when recording who did what

```
## 1. The runs

Two outward actions occurred, both taken by the **operator**, per Task 1's `checkpoint:human-action`
gate: pushing `gsd/v1.31-27c-programming-algorithm-fidelity` to `origin` in all three repos, and
dispatching `firestarter_app`'s `ci.yml` (`Host CI`) against that branch. The operator's Task 1 reply,
quoted verbatim: *"The operator authorized the orchestrator to perform the pushes and the dispatch on
their behalf. All three branches are pushed and all three CI runs are complete and green. Response:
pushed and dispatched."* No agent ran `git push`, `gh workflow run`, `gh pr create`, `gh pr merge` or
`git merge` at any point in this plan. Every command in this section, in §2, and in §8's re-verification
is a read-only `gh run view`, `gh run list`, or `git ls-remote` call, re-run independently by this plan
rather than accepted from the orchestrator's gate-clearance evidence on trust alone.
```

Two transferable moves: **name who performed each outward act**, and **state explicitly which commands
were read-only and that they were re-run rather than trusted**. This is also the precedent RESEARCH
F-06 cites for "`git push` is an operator-owned act here" — and the reason the operator-authorizes-
agent-performs path is available (it was used in Phase 138, one phase ago).

#### 5d. Correction-by-appending, not by rewriting (`138-BASELINE.md:90-94`)

```
`138-RESEARCH.md`'s trigger table is **incomplete for the one workflow it omits, not
wrong about the one it names** — `build.yml`'s own row is accurate. This document's §1 table above is
the corrected, complete two-workflow record for a firmware push; `138-RESEARCH.md` itself is left
unedited, per this project's standing convention of appending a correction in a later, citing document
rather than rewriting a prior research artifact in place.
```

This is the standing convention. Phase 139 will have corrections to record (RESEARCH's own F-01…F-09
already correct CONTEXT.md in four places, and CONTEXT.md is likewise left unedited). Record any new
divergence in `139-CITATIONS.md` and cite it; do not edit `139-CONTEXT.md` or `139-RESEARCH.md`.

---

### 6. `139-GH15-ORIGINAL-CRITERIA.md` — verbatim preservation

**No exact analog.** Nearest patterns, both quoted above:
`138-02-PULSE-DISTRIBUTION.md` §Run 1's *"exact content (reproduced here so the exercise itself stays
re-creatable even though the file is gone)"* (§4i), and `122-DELIVERY.md:134-135` —

```
The four argv strings recorded in §3's table are the literal, complete commands executed —
copy-pasted, not paraphrased.
```

**Generation is mechanical, not authored** (RESEARCH §Code Examples):

```bash
gh issue view 15 --repo henols/firestarter_prom --json body -q .body \
  | awk '/^## Acceptance criteria/,0' > 139-GH15-ORIGINAL-CRITERIA.md
gh issue view 15 --repo henols/firestarter_prom --json body -q .body | grep -c '^- \[ \]'   # → 9
```

**Two assertions the planner should add**, because this file's whole value is fidelity:
1. `grep -c '^- \[ \]'` on the captured file equals **9** (RESEARCH F-01 — CONTEXT.md and ROADMAP both
   say seven; nine is the measured truth).
2. The captured block matches RESEARCH's own verbatim copy (`139-RESEARCH.md` §"The nine
   acceptance-criteria boxes, verbatim") — a `diff` between the live capture and that fenced block is a
   free, independent corroboration that the body has not changed since research ran. gh#15's
   `updatedAt == createdAt` (never edited) makes this diff meaningful.

This file is also the source for the body amendment's `<details>` block (D-01) and the target of the
post-edit read-back assertion (D-10).

---

### 7. `.planning/v1.31-OPERATOR-BATCH.md` — the parked-command record

**Analog:** `.planning/v1.30-OPERATOR-BATCH.md` (112 lines — read in full this session).
**Do not append a v1.31 row to the v1.30 file** — RESEARCH lists it under "Deprecated / do not reuse"
(closed milestone, A-1 already RESOLVED). Create the v1.31 file on the same shape.

#### 7a. Header, verbatim (`v1.30-OPERATOR-BATCH.md:1-9`)

```markdown
# v1.30 — Operator Batch

Everything that needs the operator, accumulated across phases 136 → 136.1 → 137 and presented
**once**, immediately before `/gsd-complete-milestone`. Per the operator's standing instruction
(2026-08-04, reaffirmed 2026-08-05): **drive all phases in order; do not stop mid-flight to ask.**

Anything Claude could decide, Claude decided and recorded in the owning phase's CONTEXT/RECORD.
This file holds only what genuinely needs a human — plus questions raised and answered along the way,
kept so the close can see what was assumed.
```

Section skeleton: `## A. Blocking` (table) · `## ▶ RUN STATUS` · `## B. Decisions Claude made that the
operator may want to reverse` · `## C. Known-open findings deliberately NOT fixed` · `## D. Questions
raised and answered mid-run` · `## E. Operator decisions deferred`. Phase 139 needs only **A**
(and possibly a stub RUN STATUS); the rest accrue as later v1.31 phases run.

#### 7b. The §A table header and the A-1 row anatomy (`v1.30-OPERATOR-BATCH.md:13-17`)

```markdown
## A. Blocking — must be done by the operator before the milestone closes

| # | Item | Why it cannot be delegated | Raised by |
|---|---|---|---|
```

The A-1 row (line 17) is the shape D-08's hold branch copies. Its eight load-bearing elements, in
order, with the exact phrasing:

1. **Struck-through original + resolution stamp** — `~~Approve the gh#12 follow-up reply wording, then post it~~ — **RESOLVED 2026-08-05.**`
2. **Who approved what, and when** — `Wording **APPROVED** by the operator in real time at 137-05 Task 2, with one named correction made under that approval (already committed `3596604d`)`
3. **The freeze values** — ``Frozen at `137-GH12-COMMENT.md` blob `3a628c56de4d45dfe2be0c645fced0e25d5ebceb` (2646 bytes).``
4. **The unambiguous posting state** — `**Posting is HELD, not authorized** — the operator did not say "post now"`
5. **The independent mechanical evidence** — `137-05 Task 3's fresh, independent shipped-check (re-run 2026-08-05, not reused from Task 1) confirms the removal has **not** shipped`
6. **A named precondition for acting** — `**POST ONLY after the beta push (A-2) confirms the removal is live**`
7. **The exact single command, full path, no ellipsis** — ``run exactly: `gh issue comment 12 --repo henols/firestarter_prom --body-file .planning/phases/137-close-honesty-ledger-claim-gate-gh12-followup/137-GH12-COMMENT.md`.``
8. **Provenance** — `Raised by: Phase 137 / CLOSE-06`

Also note the honest-arithmetic aside embedded in that row (`info.version` returns latest *stable*,
which is a different field from "highest prerelease") — recorded rather than smoothed over. Phase 139
has an analogous trap worth pre-empting in the row: the fetch-back diff **expects** exactly one added
trailing newline (§2c), so a bare "the diff was non-empty" note would misread as a failure.

#### 7c. The RUN STATUS section (`v1.30-OPERATOR-BATCH.md:25-41`) — the hold-branch's second landing site

```markdown
## ▶ RUN STATUS — where the autonomous run stopped
```
```
- **Requirements: 54 ticked / 2 open.** Open: **CLOSE-01** ... and **CLOSE-06** (deliberately held open — see A-1/A-3).
- **Nothing has been posted to GitHub. Nothing has been pushed. No release exists.**
```

The flat, unhedged inventory sentence (*"Nothing has been posted to GitHub"*) is the shape Phase 139's
hold branch wants.

**D-08's other landing site** is `ROADMAP.md` §"Phase 140" line 4, which currently reads exactly:

```
**Depends on**: Phase 139 (the correction is public before this implementation phase lands).
```

(verified live this session at `.planning/ROADMAP.md`). The hold branch amends **this line** with the
named exception. ⚠ Amend it by hand — a recorded project finding is that `phase.complete` clobbers an
unrelated phase's `**Plans:**` line; snapshot and diff ROADMAP if any state tool touches it.

---

### 8. `139-01-SUMMARY.md` — the summary shape

**Analog:** `137-05-SUMMARY.md` (257 lines).

**Frontmatter keys** (`137-05-SUMMARY.md:1-61`): `phase`, `plan`, `subsystem`, `tags`, `requires`,
`provides`, `affects`, `tech-stack{added,patterns}`, `key-files{created,modified}`, `key-decisions`,
`requirements-completed`, `coverage[]{id,description,verification[]{kind,ref,status},human_judgment,
rationale}`, `duration`, `completed`, `status`.

Two entries worth copying exactly:

```yaml
requirements-completed: []
```

— empty, because posting was held. Phase 139's hold branch must do the same for **ISSUE-03**
(RESEARCH Pitfall 7: *"In the hold branch, ISSUE-03 must stay `[ ]`"*; ISSUE-01/ISSUE-02 may tick on
the frozen, approved draft).

```yaml
provides:
  - "137-GH12-COMMENT.md: the operator-approved, frozen gh#12 reply (blob 3a628c56, 2646 bytes)"
  - "an exact, recorded follow-up command for posting after the beta ships"
  - "CLOSE-06 deliberately held open, annotated with cause and the single closing action"
```

— `provides` carries the freeze values inline, so a reader never has to open the artifact to know
what was frozen.

Body sections in order: title + one-sentence bolded verdict · `## Performance` · one `##` per task ·
`## Task Commits` · `## Files Created/Modified` · `## Decisions Made` · `## Deviations from Plan` ·
`## Issues Encountered` · `## User Setup Required` · `## Next Phase Readiness` · footer
(`*Phase: …*` / `*Completed: …*`) · `## Self-Check: PASSED` with `FOUND:` lines naming every artifact
and every commit.

The verbatim-verdict block (`137-05-SUMMARY.md:77-97`) is the model for recording a
`checkpoint:human-action` answer — numbered, one item per question asked, each with the operator's own
words, followed by the mechanical before/after proof that nothing was posted:

```
**Nothing was posted before or during this task.** `gh issue view 12 --repo henols/firestarter_prom
--json comments -q '.comments | length'` returned **9** both before Task 2/3 ran and again after Task 3
completed — confirmed unchanged.
```

---

## Shared Patterns

### S-1. Record-artifact file conventions (applies to every `.md` this phase creates)

**Source:** `138-BASELINE.md`, `138-BRANCH-BASES.md`, `137-LEDGER.md`, `137-RECORD.md`,
`122-DELIVERY.md`, `138-02-PULSE-DISTRIBUTION.md` — all six inspected this session.

| Property | Convention |
|---|---|
| **Naming** | `<padded-phase>-<NAME>.md`, `NAME` in SCREAMING-KEBAB (`138-BASELINE.md`, `137-GH12-COMMENT.md`, `122-DELIVERY.md`). Plan-scoped records may embed the plan number: `138-02-PULSE-DISTRIBUTION.md`, `138-04-HOST-BASELINE.md`. |
| **Frontmatter** | **None.** Record artifacts carry no YAML. Only `*-PLAN.md`, `*-SUMMARY.md` and `*-VALIDATION.md` do. |
| **Header** | `# <Phase/Plan> <n> — <Title>` followed by bolded metadata lines (`**Owner requirement:**`, `**Measured:**`, `**Written:**`, `**Purpose:**`), then `---`. |
| **Footer** | Italic provenance block, e.g. `*Phase: 137-close-…*` / `*Recorded: 2026-08-05, plan 137-06, against `firestarter_app` submodule commit `cc036e8` …*` |
| **Sections** | Numbered `## 1.`, `## 2.` … in evidence records (`122-DELIVERY.md`, `138-BASELINE.md`); named `## Run 1` / `## Reconciliation` in measurement records. |

**The one deliberate exception: `139-GH15-COMMENT.md` and `139-GH15-BODY-AMENDMENT.md`.**
`137-GH12-COMMENT.md` has **no title, no metadata, no footer** — the file is the literal payload. Any
header would be posted to GitHub. Same for `139-GH15-ORIGINAL-CRITERIA.md`, which is a raw capture.

**How SUMMARY files reference record artifacts:** by full repo-relative path under
`## Files Created/Modified` with a one-line purpose (`137-05-SUMMARY.md:176-181`), and by bare filename
in the `provides:` frontmatter with the freeze values inline. `## Self-Check` lists them as `FOUND:`
lines.

### S-2. Freeze → gate → act → prove they matched

**Sources:** `137-05-PLAN.md:208-233` (structure), `122-DELIVERY.md` §1-§4 (executed mechanics).
**Apply to:** `139-GH15-COMMENT.md`, `139-GH15-BODY-AMENDMENT.md`.

Two independent mechanisms, always both: (1) **blob SHA + byte length + committing commit** recorded
before the gate and re-asserted immediately before the call; (2) **fetch-back byte-diff** under the
single named `sed -e '$a\'` trailing-newline normalization. CONTEXT §Claude's Discretion says a third
byte-identity gate is optional precisely because these two already exist.

### S-3. A gate that has only ever passed is untrusted

**Sources:** `138-02-PULSE-DISTRIBUTION.md` §"Run 1" (§4i above); `test_check_permitted_claims_v130.py`
(§4h); PITFALLS P-11 point 4.
**Apply to:** `139-check-claims.py`, and to every `<verify><automated>` block that could pass vacuously.

Binding per ROADMAP's v1.31 must-not-do list. The planted-failure run must precede the clean run **and
be recorded**, with the planted input's exact content reproduced. RESEARCH's ordering is explicit: run
the planted file, assert exit 1, and only then is the clean run meaningful.

### S-4. Cite by commit or `file:line`, never by recollection — and verify by content

**Sources:** `138-BRANCH-BASES.md` §1 (command-as-run beside result); `122-DELIVERY.md` §3
("copy-pasted, not paraphrased"); RESEARCH F-05/Pitfall 2.
**Apply to:** `139-GH15-COMMENT.md`, `139-CITATIONS.md`.

An HTTP 200 proves a file exists at a SHA, never that a line range says what you claim. Every anchor
gets fetched at its pinned SHA, sliced to the pinned range, and grepped for expected content; the
sliced text goes into the register.

### S-5. In-place annotation, never silent ticking or silent rewriting

**Sources:** `137-05-SUMMARY.md:196-209` (REQUIREMENTS.md CLOSE-06 annotated in place, original text
preserved above the annotation, recorded as a Rule-2 auto-fixed deviation because it fell outside
`files_modified`); `v1.30-OPERATOR-BATCH.md` A-1/A-3/A-4 (struck through, not deleted).
**Apply to:** the hold-branch edits to `REQUIREMENTS.md` (ISSUE-03 row) and `ROADMAP.md` (Phase 140
`Depends on:`).

Note the mechanical lesson from 137: those two files were **not** in 137-05's `files_modified` and
editing them had to be recorded as a deviation. Phase 139 knows in advance that the hold branch touches
`REQUIREMENTS.md`, `ROADMAP.md` and `.planning/v1.31-OPERATOR-BATCH.md` — **declare all three in
`files_modified` up front** so the branch is not a deviation.

### S-6. Requirement ticking is named exhaustively per plan

**Source:** `.planning/ROADMAP.md` §Phase 138's plan list preamble, verbatim:

```
Requirement ticking is named exhaustively per plan so no plan ticks a multi-plan requirement early:
`138-01` → PREP-01, PREP-02 · `138-02` → none (PREP-04 delivered) · `138-03`/`138-04`/`138-05`/`138-06`
→ none (PREP-03 delivered across all four) · `138-07` → PREP-03, PREP-04.
```

**Apply to:** the ROADMAP Phase 139 `**Plans:**` line and the dispatch prompt. RESEARCH Pitfall 7
records the failure mode (executors ticked multi-plan requirements early 4× in Phase 116). If Phase 139
is one plan, the branch-dependence still needs stating: ISSUE-01/ISSUE-02 tick on the frozen approved
draft; **ISSUE-03 ticks only on the post branch**.

### S-7. Read-only sub-repo discipline

**Source:** meta `CLAUDE.md` (*"This repo tracks only `.planning/` … Neither sub-repo is committed
here"*); RESEARCH F-09.
**Apply to:** the D-10 precondition in Task 1 and Task 3.

Use the three-ref blob-equality form, not `git status` on the meta repo (which shows ` M firestarter`
for a **stale gitlink pointer**, not an edit) and never `git submodule status` (F-08: fails
unconditionally in this repo on `.planning/v1.7/upstream-rurp`).

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `139-GH15-BODY-AMENDMENT.md` | outward content artifact | one-shot publication | **No issue body has ever been edited by this project.** `gh#15`'s `updatedAt == createdAt` confirms it has never been modified, and no `.planning/` precedent exists for a `gh issue edit --body-file` call — every prior outward act was a *comment* or a *release body*. The voice comes from `137-GH12-COMMENT.md`; the **structure** must come from gh#15's own live body (headings and section order preserved, `⚠ AMENDED` block prepended, criteria list replaced, original list moved verbatim into `<details>`). RESEARCH §"gh#15 Live State" carries the nine boxes and the two prose directives that must also be corrected. The `<details>`-preservation idea has no in-repo precedent either — the nearest is `v1.30-OPERATOR-BATCH.md`'s strike-through-don't-delete convention (S-5). |
| *(none of the others)* | | | Every other artifact has at least a role-match analog above. |

---

## Metadata

**Analog search scope:** `.planning/` only — `phases/122-close-honesty-ledger-community-ask-release-decision/`,
`phases/137-close-honesty-ledger-claim-gate-gh12-followup/` (all 20 entries),
`phases/138-preconditions-baseline/` (all 26 entries), `phases/139-gh-15-correction-outward/`,
`.planning/` root (`ROADMAP.md`, `research/PITFALLS.md`, `v1.30-OPERATOR-BATCH.md`), `.claude/skills/`.

**Files read in full this session:** `139-CONTEXT.md`, `139-RESEARCH.md` (1484 lines, 3 passes),
`137-05-PLAN.md`, `137-05-SUMMARY.md`, `137-GH12-COMMENT.md`, `check_permitted_claims.py`,
`test_check_permitted_claims_v130.py`, `122-DELIVERY.md`, `v1.30-OPERATOR-BATCH.md`.
**Files read in part (targeted, non-overlapping ranges):** `138-BASELINE.md:1-95`,
`138-BRANCH-BASES.md:1-80`, `138-pulse-distribution.py:1-60`,
`138-02-PULSE-DISTRIBUTION.md` (§heading index + §Run 1), `ROADMAP.md:215-265`,
`research/PITFALLS.md:408-470`, `139-VALIDATION.md:1-30`, plus head/tail probes of
`137-LEDGER.md`, `137-RECORD.md`, `138-PATTERNS.md`.

**Project skills checked:** `.claude/skills/` contains `devtest-triage`, `devtest-rootcause`,
`skill-writer`, `find-skills`. None applies to an issue-correction phase (RESEARCH reaches the same
conclusion independently). No `SKILL.md` rules were loaded.

**Read-only compliance:** no source file was modified; no file in `firestarter/` or `firestarter_app/`
was opened for write; no git write command was run in the meta repo or either submodule; no branch was
created, switched, or pushed; no `gh` state-changing call was made. The only file written is this one.

**Pattern extraction date:** 2026-08-09
