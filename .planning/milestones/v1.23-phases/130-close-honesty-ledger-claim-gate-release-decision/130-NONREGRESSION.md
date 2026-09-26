# Phase 130 Non-Regression Sweep — closing plan (130-16)

**Written:** 2026-08-02
**Firmware branch (`firestarter`):** `beta` (post-merge, post-CI-fix) · **HEAD at this sweep:**
`1c511e824d2d7e6f3db4d569ef4a2a1a505b3f79` · **milestone branch (`v1.23-py32f071-integration`) tip:**
`05c20bf59a4f0f73acf28d48d5dbbedab5724c5f`
**Host branch (`firestarter_app`):** `beta` (post-merge, post-CI-fix) · **HEAD at this sweep:**
`5934a54984cadb66446b96f25ad40f0d8a2f0a19` · **milestone branch (`v1.23-py32f071-integration`) tip:**
`cc9452f4db9a814ffb221bab767c24db67288365`
**Meta branch:** `gsd/v1.23-py32f071-integration` · **HEAD:** `48912762bba0f0d506a89a690a2a0a002d6bb843`

**Why two SHAs per sub-repo, honestly stated:** the operator's hand-off (`130-HANDOFF.md`) merged
each milestone branch into `beta` and pushed; CI then auto-committed a version-bump plus, in this
cut, a same-session fix for three CI-only test defects (`130-CHANNELS.md` §2). The working
directories in this devcontainer are checked out on `beta` at the fix commits above — every gate
below is run against **that** tree, which is the tree that actually shipped. The gitlink assertion
below (§F, D-04) is scoped to the **milestone branch tip**, per this milestone's own in-phase
gitlink practice (Phases 125/128/129) and per `130-DECISION.md` §9 — the two numbers are not the
same thing, and this document does not conflate them.

> **No PY32F071 hardware exists.** Nothing in this milestone has ever run on this silicon, and
> nothing in it can. Everything below is about **publication**: that a file with a particular
> name, carrying a particular version string, became a downloadable release asset. Nothing here
> says the published image runs, boots, or installs. The permitted claim is exactly one sentence
> wide.

**Re-execution pledge.** Every row in §A below was executed in **this session** (plan 130-16's
Task 1), against the trees exactly as they now stand — nothing is copied from any of this phase's
fifteen prior plans' (130-01, 130-02, 130-03, 130-04, 130-05, 130-06, 130-07, 130-08, 130-09,
130-10, 130-11, 130-12, 130-13, 130-14, 130-15) SUMMARY files. Where a prior SUMMARY made a claim
(an exit code, a test count, a parsed literal), this document re-checked it independently against
the live tree and says so below.

---

## The claim, as precise statements

1. Every checker and suite this milestone introduced or depends on was re-run in this session and
   is green, at the counts recorded in §A.
2. CLOSE-01's four target files plus the notes file carry zero unlabeled stale claims — the
   `check_record_corrections.py` default-mode run's own exempt-hit tally accounts for every match.
3. CLOSE-02's honesty ledger (`130-LEDGER.md`) and both release-note drafts pass the claim gate in
   default mode, scanning all four contracted artifacts.
4. CLOSE-03's ROADMAP renumber left the four v1.24–v1.27 entries byte-unchanged, proven by a
   before/after SHA-256 comparison (§C).
5. CLOSE-04's release decision (`130-DECISION.md`) was committed before any push, the observed cut
   tag `3.0.0b15` was read from `gh release list` (never computed), and PyPI resolution was
   verified directly from a clean venv — all per `130-CHANNELS.md`, re-cited here, not re-derived.
6. The meta gitlinks are asserted against the milestone-branch tips; the firmware gitlink is bumped
   because plan 130-03's commits moved that tip, the host gitlink is unchanged because nothing in
   this phase committed inside `firestarter_app` (§F).
7. Nothing below claims the published image runs, boots, or installs, that the §5(c) USB-identity
   condition is satisfied or resolved, or that the pid.codes source-warning obligation is anything
   stronger than an ask.

---

## A. Locally provable, executed now

### A1. Firmware repo (`/workspaces/firestarter`, `beta` @ `1c511e824`)

| Gate | Command | Result |
|---|---|---|
| Full suite | `python3 -m pytest tests/ -q` | **221 passed**, 0 failed, 0 skipped |
| Native (with devtools) | `pio test -e native` | **141 test cases, 17 suites, 141 succeeded** |
| Native (no devtools) | `pio test -e native_nodevtools` | **141 test cases, 17 suites, 141 succeeded** |
| Cross-repo sync gate | `FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -q` | **41 passed** |
| `usb_cdc.c` descriptor | `sed -n '19,25p' platform/py32f071/src/usb_cdc.c` | Lines 19/23 are still `#ifndef FIRESTARTER_USB_VID` / `#ifndef FIRESTARTER_USB_PID` guards; lines 20/24 read `#define FIRESTARTER_USB_VID 0x1209U` and `#define FIRESTARTER_USB_PID 0x0001U` |

**Stated honestly, per the plan's own instruction:** `test_flash_path_record_sync.py` runs in **no
CI leg** on this branch. Its 41/41 green result above is a local-run obligation for anyone editing
either flash-path-record copy — this document does not imply CI coverage of that gate, and the
first-attempt CI failure recorded in `130-CHANNELS.md` §2 (this exact module, softened from a hard
assert to a skip) is the reason that caution is not theoretical.

### A2. Host repo (`/workspaces/firestarter_app`, `beta` @ `5934a54984`)

| Gate | Command | Result |
|---|---|---|
| Full suite | `python3 -m pytest tests/ -v --tb=no` | **1303 passed** in 110.82s |
| Catalog check | `python3 tools/catalog/codegen.py --catalog tools/catalog/messages.toml --check` | `OK: catalog valid (73 messages, version 1).` exit 0 |
| Codegen drift | `git diff --exit-code firestarter/messages.py` | clean, exit 0 (`codegen_clean`) |

**Environment note (RESEARCH assumption A2, carried forward from `130-DECISION.md` §12):** every
run above executed on Python 3.12 in this devcontainer; both CI workflows pin Python 3.11. No
3.11-specific RED was reachable from this session's toolchain; this residual risk is recorded, not
eliminated — the same wording `130-DECISION.md` uses, not a new claim.

### A3. Meta `.planning/` checkers

| Gate | Command | Result |
|---|---|---|
| CLOSE-01 checker, default mode | `python3 check_record_corrections.py` (run from the phase directory) | `PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md; exempt hits by verdict: {'block': 23, 'line-label': 5, 'inline-history': 6, 'inline-allow': 13, 'superseded': 13}` — exit 0 |
| CLOSE-01 checker fixture suite | `python3 -m pytest test_check_record_corrections.py -q` | **20 passed** |
| CLOSE-01 checker, `--explain` | `python3 check_record_corrections.py --explain` | Every exempt hit listed with its file, line and verdict; **tally `{'block': 23, 'line-label': 5, 'inline-history': 6, 'inline-allow': 13, 'superseded': 13}`** — total **60**, `unlabeled` **absent from the tally (0)**. The green is green because every match is accounted for by a verdict, not because the needles stopped matching. |
| Claim gate, default mode | `python3 check_permitted_claims.py` (run from `123-non-regression-baselines-gate-hardening/`) | `PASS: scanned ../130-close-honesty-ledger-claim-gate-release-decision/130-LEDGER.md, ../130-close-honesty-ledger-claim-gate-release-decision/130-DECISION.md, ../130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-fw.md, ../130-close-honesty-ledger-claim-gate-release-decision/130-RELEASE-NOTES-app.md; 4 file(s) carry the required silicon caveat` — exit 0 |
| Claim gate fixture suite | `python3 -m pytest test_check_permitted_claims.py -q` | **11 passed** |
| Decision parser | `parseDecisions()` (`.claude/gsd-core/bin/lib/decisions.cjs`) against `130-CONTEXT.md` | **16 ids** returned (`D-01`…`D-16`), parseable — matches C-1's fix, re-asserted independently in this session |

### A4. D-16's one-shot before/after proof — the v1.24–v1.27 ROADMAP entries

Per-line SHA-256 of the four ROADMAP entries, re-hashed **before** this plan's Task 2 edits the
`## Milestones` `v1.23` entry line and **again after**:

| Entry | Line (before) | Line (after) | SHA-256 | Verdict |
|---|---|---|---|---|
| v1.24 Bus-Config Mask-Model Redesign | 29 | 29 | `4b83c9e1c980355ee5f75985419c9e2f3c99b4f4dc9d69e282bdf61b21b4630b` | **MATCH** |
| v1.25 Jumper-Display Correctness & 2516-Family Support | 30 | 30 | `4bc536d5783de3cf1a21ba7b60260063141fcb3620338b5643b66b1456cfa61f` | **MATCH** |
| v1.26 White-Box Voltage-Reading Calibration | 31 | 31 | `733b81ddcc45308bcc4c20d643e67cc09263315a0585f80cb0058a8c7f9dddf9` | **MATCH** |
| v1.27 Per-Protocol EPROM Programming Algorithms | 32 | 32 | `bb8cc73acdbe977f8d95a3550e17b2f4bd7ea21d91167359c17484bd8d1d3f52` | **MATCH** |

The before hashes were measured before Task 2 touched anything in `.planning/ROADMAP.md`. The
after hashes were re-measured once Task 2's only `ROADMAP.md` edit (the `v1.23` Milestones-entry
line, line 28 — a single-line replacement that adds no lines above line 29, so the four entries'
line numbers are unaffected) had landed. All four verify script's `MATCH` verdicts pass (`exit 0`).

**The path-scoped diff over the phase's full range**, `git diff -U0 532b0c2a -- .planning/ROADMAP.md`
(`532b0c2a` = "docs(phase-130): mark phase execution started", the commit immediately preceding
plan 130-01's first commit) shows 19 `@@` hunks touching lines 28, 33–35, 1723, 1732, 1738, 1749,
1883, 1997, 2414, 2468, 2475, 2477, 2482–2485, 2489–2493, 2497, 2501, 2505, 2509, 2513, 2517 — **no
hunk anywhere in this range touches lines 29, 30, 31 or 32.** The hash equality above is the
evidence; this diff is the independent corroboration.

**The two changes a reader will see that are NOT violations of the byte-unchanged claim,** both
recorded so neither is mistaken for drift: (1) the v1.30 back-reference correction (plan 130-05,
`ROADMAP.md:35`, correcting a now-false "the v1.29 slot immediately above" phrase inside the
**v1.30** entry, not any of v1.24–v1.27); (2) the line-count drop from collapsing the two former
py32 ROADMAP slots (former v1.28/v1.29) into one dated retirement line (plan 130-04, lines 33–34).
Neither touches v1.24, v1.25, v1.26 or v1.27.

**D-16's recorded reason no committed checker exists, in full:** *"these four entries never
change"* is false as a standing invariant — those entries **should** change once v1.24 is scoped —
so a permanent gate would either ship pre-obsolete (asserting an invariant about entries that have
since been edited for a legitimate reason) or block a legitimate future edit forever. This is the
milestone's single deliberate exception to BASE-08's ships-with-a-fixture discipline. A one-shot
before/after hash proof, recorded once in this document, is the correct-strength evidence for a
claim whose truth is scoped to this phase's execution window, not to all future time.

### A5. D-07's toolchain reproduction recipe

The exact commands to reproduce a local ARM build, drawn verbatim from
`firestarter/.github/actions/build-py32f071/action.yml` (the composite action both `py32f071.yml`
and `beta-build.yml` call):

```bash
cmake -S platform/py32f071 -B build/py32f071 -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build/py32f071
```

**Tool versions measured in this session** (re-confirming `REQUIREMENTS.md:18`'s cited figures,
not copied from it):

```
$ arm-none-eabi-gcc --version | head -1
arm-none-eabi-gcc (15:14.2.rel1-1) 14.2.1 20241119
$ cmake --version | head -1
cmake version 4.4.0
$ ninja --version
1.13.0.git.kitware.jobserver-pipe-1
```

**The standing rule this recipe operates under:** a local build supports **delta** and
**byte-identity** claims only, never an absolute size, because the local and CI compilers differ
and produce different absolute sizes for the same source — measured `text=27260` local (this
session's tool versions above, and 130-03's own local pass, both agree) against `text=27344` CI
(`REQUIREMENTS.md:18`, citing a CI run). Neither figure is comparable to the other; each is
internally consistent only against builds made with the same toolchain.

**The D-11-specific note:** byte-identity is the **wrong** criterion for the `usb_cdc.c` descriptor
swap specifically, because the descriptor bytes change **by design** (VID/PID literals). The
permitted claim for that change is a confined **delta**: 130-03's own local pass recompiled
**exactly one** translation unit (`usb_cdc.c.obj`) plus the final link, and the `.text`/`.data`/
`.bss` totals were numerically identical at both the object level (996/16/2258) and the image level
(27260/112/5888) in both the pre-edit and post-edit states, while the two `.hex` SHA-256 digests
differ (`9599a625…` pre-edit vs. `91da9edf…` post-edit) — confirming the descriptor bytes actually
changed. A size-neutral value swap, reported strictly as a delta, never as byte-identity.

**Environment-Availability drift, named explicitly:** `130-RESEARCH.md`'s own Environment-
Availability row listed the ARM toolchain as **absent** from this devcontainer at research time;
it measured **present** at plan time (research itself built and ran the D-13 byte-identity proof,
41/41 objects) and is confirmed **present** again in this closing session, with the three version
strings above. `REQUIREMENTS.md:18` narrows the Validation Ceiling's toolchain clause accordingly
(plan 130-10); this recipe is the how-to that clause deliberately does not carry.

### A6. A-5 — discharged at Phase 124, not fresh work

RESEARCH C-17 assigns the operator-visible AVR flash-constraint decision (A-5) to Phase 130's
research spine. It is already **discharged**: `REQUIREMENTS.md` "Operator Decisions Locked at
Definition," item 4, restates it as *"Leonardo flash must not grow; Uno-class growth ≤ 64 B,
recorded"*; `REQUIREMENTS.md` MERGE-05 encodes it as a requirement; and `124-NONREGRESSION.md` §F4d
records the independent 328PB build (`uno328pb(flash=24004/32384[+28<=64],ram=1579/2048[=])`) that
closed the single-source gap research had flagged for the ATmega328PB figure. Recorded here as
**discharged with a citation**, explicitly not as fresh work performed by this plan.

### A7. Recorded rulings and no-ops

- **RESEARCH Open Question 2 (history-exemption ruling).** Five dated review-pass paragraphs
  (`ROADMAP.md:1747`, `:1877`, `:1879`, `:1883`, `:1887`) were ruled **history-exempt** by plan
  130-05 — a dated, signed record of what was believed and decided on that date is supposed to
  look stale once superseded, and rewriting it would erase the historical fact itself. The single
  exception is `ROADMAP.md:1883`, whose final clause read as a live instruction to a future reader
  ("scope v1.28 from that document"), pointing at a document RESEARCH's A-6/R-8 established does
  not match what actually shipped — plan 130-05 disarmed only that clause with one additive
  `⚠ SUPERSEDED` bracket, leaving the paragraph's dated text otherwise byte-unchanged (confirmed by
  `git diff -U0` showing exactly one hunk at that line).
- **RESEARCH Open Question 3 (999.25 no-op, verified).** D-15's second half asked whether
  999.25's own "the v1.29 slot immediately above" back-reference needed correcting. Measured: the
  phrase occurs exactly once in the whole file, inside the **v1.30** Milestones-list entry, not
  inside the 999.25 stub itself (lines 1755–1786). 999.25 needed no edit; recorded as a verified
  no-op, not assumed.
- **`122-DECISION.md`'s items 7 and 8, recorded as no-ops.** `130-DECISION.md` §7 and §8 name
  `122-DECISION.md`'s own dry-run merge-conflict probe (`git merge-tree --write-tree --messages`)
  and its `--ours` superset proof as having **no subject here**: both `firestarter` and
  `firestarter_app` measured **0 behind** `origin/beta` (item 3 of that same document), so there is
  no inbound content for either branch to conflict against, and no conflict to prove a superset of.
  Recorded as no-ops, not manufactured as artifacts.
- **Six R-Ns with zero live occurrences, discharged with evidence rather than given checker
  legs.** R-4, R-12 (Leonardo RAM never recorded — now recorded, `BASE-01`/`size_baseline_base01.json`),
  R-13 (py32 SRAM assumed 20 K — no such collocation exists in any target file; `PROJECT.md:38`
  states 16 KiB correctly), R-16 (README glob-vs-literal mismatch — a firmware-repo subject, fixed
  by REL-02's two-entry `files:` glob), R-17 (`write_checksums.cmake` orphaned — recorded deleted at
  `REQUIREMENTS.md:50`, `ROADMAP.md:2101`/`:2118`, `STATE.md:794`, discharged by MERGE-08), and
  R-18 (`DEV_TOOLS` absent on ARM reads as a decision — recorded explicit at `REQUIREMENTS.md:50`,
  discharged by MERGE-08).
- **R-10, needing no substantive correction, per C-7.** Every live `2992 B` occurrence in the
  planning record is either a labeled correction or historically-accurate archive text describing
  the pre-Phase-119 Leonardo headroom — not a live, uncorrected claim. C-7 established this; no
  edit was required or made.

### A8. What this document does NOT claim

1. That the published `firestarter_py32f071.hex` image runs, boots, or installs on any board.
2. Any silicon behaviour of the PY32F071 part — no board exists to observe one.
3. That the USB-identity condition recorded at `.planning/v1.23-FLASH-PATH-DECISION.md` §5(c) has
   been met.
   The condition's own wording states it is written so that a future reader **can** find it unmet,
   and this sweep leaves that judgment exactly where `130-DECISION.md`'s own dedicated section
   leaves it — an owned tension, not a verdict this document reaches.
4. That a green claim-gate run, or a green run of any checker named in this document, by itself
   satisfies this milestone's honesty criterion.
   Every green result above is the **mechanizable half only** — D-02's blocking operator wording
   review, performed before either release body posted, is the other half, and it is not a scanner
   result this document can re-run.
5. That the community inbox (`gh#18`, `gh#20`) is clear — it is not, and neither is out of scope
   because it went unmentioned.
6. That pid.codes' own terms make the source warning in `usb_cdc.c` mandatory.
   Those terms **ask**, per RESEARCH C-6 — the warning is worded to match an ask, and this
   document never upgrades that wording to an obligation.
7. Any absolute ARM flash or RAM figure as a milestone-level number — every ARM figure in this
   document is either a delta, a byte-identity comparison, or explicitly cited to a CI run URL plus
   commit SHA (§A5).

---

## B. Success criteria

Quoted verbatim from `.planning/ROADMAP.md` §"Phase 130: Close — Honesty Ledger, Claim Gate,
Release Decision."

### Criterion 1

> *"All of R-1…R-18 are individually corrected in PROJECT.md, STATE.md, ROADMAP.md and
> `.planning/notes/py32f071-port-branch-state.md` — verified by grepping for each specific
> superseded figure/claim … and confirming zero remaining occurrences outside a labeled
> correction/history block."*

Discharged as written. §A3's `check_record_corrections.py` default-mode run scans exactly these
five files (the notes file is the fifth CLOSE-01 target, D-06 widened the file list by one) and
reports **exit 0**, with every match accounted for by a verdict — `{'block': 23, 'line-label': 5,
'inline-history': 6, 'inline-allow': 13, 'superseded': 13}`, total **60**, **zero** `unlabeled`.
The `--explain` run (§A3) lists every individual hit with its file, line and verdict, so the green
is shown to be green for the right reason — the needles still match; every match now carries a
label or sits inside a history block. Per-file attribution (plans 130-06 PROJECT.md/ROADMAP.md,
130-07 PROJECT.md, 130-08 STATE.md, 130-09 the notes file, 130-10 REQUIREMENTS.md prose) is
recorded in each of those plans' own SUMMARYs and is not re-derived here.

### Criterion 2

> *"An honesty ledger (mirroring v1.22's `122-LEDGER.md` shape) pairs each permitted claim with its
> explicit non-claim, covering at minimum: the provisional pin map, the absent ARM bus-trace
> oracle, unmeasured USB-ISR-vs-PROM timing, and the mock-only ceiling on HOST-03's `DFU_UPLOAD`
> readback."*

Discharged as written. `130-LEDGER.md`'s six evidence tiers (CI-compile-only, AVR-measured,
native-simulated, mock-only, real-published-artifact, decision-only-unverified) each pair a
permitted wording with an explicit non-claim column. The four named minimum-coverage items are all
present: the provisional pin map (decision-only-unverified tier), the absent ARM bus-trace oracle
(negative-space section, "What no test, gate or review in this phase can close"), unmeasured
USB-ISR-versus-PROM timing (same section, citing the 572 µs / 600 µs figure as a **different
board's** measurement, cited for context only), and HOST-03's mock-only ceiling (mock-only tier,
citing `127-NONREGRESSION.md` §7). The claim gate's default-mode run (§A3) scans `130-LEDGER.md`
among the four contracted artifacts and exits 0.

### Criterion 3

> *"The ROADMAP slot renumber lands in the same change as the stale v1.28 prior-art correction: the
> v1.28/v1.29 py32 slots are retired into the v1.23 record, `Binary Command Protocol` is renumbered
> v1.23 → v1.28, and v1.24–v1.27 are byte-unchanged (`git diff` shows zero line changes in those
> four entries)."*

Discharged as written. Plan 130-04 landed the `v1.23 PY32F071 Integration` Milestones entry, the
`Binary Command Protocol` renumber (v1.23 → v1.28, moved into version order after v1.27), and the
collapse of the two former py32 slots into one dated retirement line, all in the same change; plan
130-05 retired backlog stubs 999.23/999.24 as delivered and repaired every stale `→ v1.28` pointer
the renumber broke. §A4 above is this document's own independent re-verification of the
byte-unchanged half: all four SHA-256 hashes MATCH before and after this plan's own ROADMAP edit,
and the phase's full-range diff touches 19 hunks, none inside lines 29–32.

### Criterion 4

> *"A `13X-DECISION.md` release-decision artifact is committed **before any push** of `beta` in
> either sub-repo; once pushed, the actually-cut prerelease tag is read from `gh release list`
> (never computed from a version-bump script), and PyPI resolution is verified directly … never
> inferred from a green CI tick."*

**Discharged in substance; the artifact-naming discrepancy is addressed explicitly, not silently.**
This criterion's own text names `13X-DECISION.md` — a template placeholder never substituted with
the real phase number, exactly as plan 130-06's SUMMARY recorded (line 105: *"Phase 130's own
criterion 4 … names the release-decision artifact as `13X-DECISION.md` … The actual artifact is
`130-DECISION.md`, created by plan 130-13."*). No file named `13X-DECISION.md` exists anywhere in
this tree, and none should — this is a resolved naming question, not an open gap: the artifact
this criterion describes **is** `130-DECISION.md`, and every other clause of the criterion is
discharged against that artifact.

The substance: `130-DECISION.md` is committed at a timestamp preceding `origin/beta`'s move in
either sub-repo — `130-DECISION.md` itself records both `origin/beta` tips as unmoved throughout
its own execution (`5c9160a3…` firmware, `e7d3ee8c…` app), and those tips only advanced later, once
the operator executed `130-HANDOFF.md`'s procedure. The observed cut tag `3.0.0b15` is quoted
verbatim from `gh release list` in `130-CHANNELS.md` §1 (*"3.0.0b15 Pre-release 3.0.0b15
2026-08-02T21:22:42Z"*, both repos), never computed from the version-bump arithmetic that happens
to predict the same value. PyPI resolution is verified directly in `130-CHANNELS.md` §5 — a fresh
`python3 -m venv`, never this project's own editable install, resolved `firestarter==3.0.0b15` via
`pip download --no-deps --pre` on the first attempt, and a direct `info.version` read confirmed no
stable regression (`2.0.7`, unchanged) — never inferred from `publish.yml`'s own `success`
conclusion, which `130-CHANNELS.md` §6 explicitly declines to accept as evidence for either
channel.

---

## C. Decision coverage — D-01…D-17

| Decision | One line | Discharged in | Verified by |
|---|---|---|---|
| **D-01** | Accept the auto-fire: the merge IS the `3.0.0b15` cut, in both sub-repos | 130-13 (`130-DECISION.md`), 130-14/130-15 (execution) | `130-CHANNELS.md` §1 observed tag; §A4/§B Criterion 4 above |
| **D-02** | Both b15 release bodies hand-written, behind a blocking operator wording review | 130-12 (drafts), operator (the review itself, per `130-HANDOFF.md` §2) | `130-15-SUMMARY.md` resume-signal record; §A8 item 4 above |
| **D-03** | The py32 asset's presence on the real b15 cut is a gate, not a note | 130-15 | `130-CHANNELS.md` §3 (`firestarter_py32f071.hex` present, all four assets) |
| **D-04** | Publish in-phase; the `v1.23` tag and any merge toward `main` stay with `/gsd-complete-milestone` | 130-16 (this plan, §F below) | §F's gitlink assertion and bump |
| **D-05** | Corrections land per document kind, not uniformly (blocks in PROJECT/ROADMAP, in-place in STATE, append-only in the notes file) | 130-07, 130-08, 130-09 | §A3's per-file `check_record_corrections.py` scan |
| **D-06** | CLOSE-01 amends REQUIREMENTS.md's two VTOR clauses, each with an inline supersession note | 130-10 | `REQUIREMENTS.md:96/:116`, `<!-- recordscan:allow part-with-no-vtor -->` markers |
| **D-07** | The Validation Ceiling's toolchain clause is narrowed in place; the reproduction recipe lives here | 130-10 (ceiling narrowing), 130-16 (this plan, §A5, the recipe) | `REQUIREMENTS.md:18`; §A5 above |
| **D-08** | CLOSE-01 is proven by a committed, label-aware checker with a planted-violation fixture | 130-02 | `check_record_corrections.py` + `test_check_record_corrections.py` (20 passed, §A3) |
| **D-09** | `130-LEDGER.md` is organised as claim classes by evidence tier | 130-11 | `130-LEDGER.md`'s six tier sections |
| **D-10** | The negative space covers the deferrals AND every owned residual | 130-11 | `130-LEDGER.md` "What this milestone chose not to prove" |
| **D-11** | The interim pid.codes `1209:0001` lands in `usb_cdc.c` before the cut, and the release body states it | 130-03 | §A1's `usb_cdc.c` line check; §A5's confined-delta proof |
| **D-12** | The ledger carries both axes explicitly (evidence tier + sourcing tag) | 130-11 | `130-LEDGER.md`'s "Status/claim key" + "Sourcing key" sections |
| **D-13** | The two py32 ROADMAP slots collapse into one pointer line; v1.23 gains its real SHIPPED entry | 130-04 | `ROADMAP.md:28`, `:33-34`; §B Criterion 3 |
| **D-14** | Binary Command Protocol moves into version order; v1.30 stays v1.30; BCP's stale sequence sentence is annotated | 130-04 | `ROADMAP.md:33`'s BCP entry, its bookkeeping-vs-sequence annotation |
| **D-15** | Backlog stubs 999.23/999.24 retire as shipped-into-v1.23; the v1.29 back-references are corrected | 130-05 | §A7's Open Question 2/3 rulings above |
| **D-16** | The v1.24–v1.27 byte-unchanged claim is proven one-shot, not by a checker | 130-04 (before-hash capture), 130-16 (this plan, §A4, the after-hash re-proof) | §A4 above |
| **D-17** | The operator's locked ship-gate decision: §5(c) stays byte-unchanged; the USB-identity tension is carried as an owned residual, never resolved or amended | delivered during planning, not in `130-CONTEXT.md` | `130-DECISION.md`'s dedicated "USB-identity descriptor tension" section; `130-LEDGER.md`'s D-17 negative-space row |

**Accounting for the count: 16, not 17.** `130-CONTEXT.md`'s own `<decisions>` block carries D-01
through D-16 — sixteen decisions — and the decision parser (§A3) correctly reports **16 ids** for
that file. D-17 is **not missing from the parse**; it is the operator's own locked decision,
delivered during this phase's planning conversation rather than written into `130-CONTEXT.md`
itself (`130-DECISION.md`'s dedicated section states this explicitly). A reader who expects 17
ids out of the decision parser and sees 16 should read this paragraph, not treat 16 as a defect.

---

## D. Success criteria discharge

See §B above (Criteria 1–4, quoted verbatim and discharged with named evidence).

---

## E. `13X-DECISION.md` naming discrepancy — addressed

Covered in full at §B Criterion 4 above: the ROADMAP's own criterion 4 text names a
`13X-DECISION.md` template placeholder that was never substituted with the phase number; the real,
committed artifact discharging that criterion is `130-DECISION.md` (plan 130-13). This document
records the discrepancy plainly rather than silently substituting one name for the other or
leaving a reader to wonder whether a differently-named file was expected.

---

## F. Gitlink assertion and bump (D-04)

`git ls-tree HEAD firestarter firestarter_app` in the meta repo, **before** this plan's Task 2:

```
160000 commit 5a89ee76dc4681abe18db259e57bb92f519520f4  firestarter
160000 commit cc9452f4db9a814ffb221bab767c24db67288365  firestarter_app
```

| Repo | Gitlink (meta HEAD, before) | Milestone-branch tip | Match? | Action |
|---|---|---|---|---|
| `firestarter` | `5a89ee7…` | `05c20bf59a4f0f73acf28d48d5dbbedab5724c5f` | **No.** Plan 130-03's two commits (`c96b576` the descriptor swap, `05c20bf` the `[SHARED:S4]` rewrite) moved the tip after the gitlink was last bumped (`129-NONREGRESSION.md`'s own bump, `7a0a375 → 5a89ee7`, predates 130-03). | **Bump** to `05c20bf59a4f0f73acf28d48d5dbbedab5724c5f`. |
| `firestarter_app` | `cc9452f…` | `cc9452f4db9a814ffb221bab767c24db67288365` | **Yes.** No plan in this phase committed inside `firestarter_app`. | **No bump.** |

This matches `130-DECISION.md` §9's own pre-flight measurement exactly (same two SHAs, same
verdict), re-confirmed independently in this session rather than copied.

**D-04 asserts, it does not pin:** the milestone bumps gitlinks in-phase (Phases 125, 128, 129 all
did), the opposite of v1.22's pinned-at-close model. The bump below is staged via
`git update-index --cacheinfo` against the milestone-branch tip specifically — **not** against
whatever commit the submodule working directory happens to be checked out to (currently `beta` at
the post-merge, post-CI-fix commits named in this document's header), because the milestone branch
tip, not the post-publish `beta` state, is what this phase's own commits are answerable for. The
`firestarter_app` submodule directory's own dirt (` M .gitignore`, four untracked files) is
pre-existing per `130-DECISION.md` item 10 and is not touched by this bump.

`git ls-tree HEAD firestarter firestarter_app`, **after** the bump (staged by this plan's Task 2
commit):

```
160000 commit 05c20bf59a4f0f73acf28d48d5dbbedab5724c5f  firestarter
160000 commit cc9452f4db9a814ffb221bab767c24db67288365  firestarter_app
```

Both gitlinks now equal their sub-repo's milestone-branch tip. **Out of scope for this phase, named
so it is not silently re-opened:** the `v1.23` annotated tag and any merge toward `main` both stay
with `/gsd-complete-milestone`, mirroring D-04's own text and v1.21/v1.22 precedent.

---

## G. Tag placeholders filled

`130-CHANNELS.md` §1 quotes `gh release list`'s verbatim output naming `3.0.0b15` as the newest tag
in both repos, `isDraft: false`, `isPrerelease: true`. This is the **observed** tag this document
and this plan's Task 2 use to fill:

- `130-LEDGER.md`'s identity-header "Published cut tag" field — updated from *"not yet observed"*
  to `3.0.0b15`, marked **observed, not predicted**, citing `130-CHANNELS.md` §1's quoted
  `gh release list` line.
- `.planning/ROADMAP.md`'s `## Milestones` `✅ v1.23 PY32F071 Integration` entry — updated from
  *"cut tag recorded once observed at milestone close, never predicted here"* to name the observed
  `3.0.0b15` tag plus the channel facts: the firmware prerelease carries four `.hex` assets
  including `firestarter_py32f071.hex` (first-ever publication of that asset, per
  `130-CHANNELS.md` §3), PyPI carries the host app (`firestarter==3.0.0b15`, resolved from a clean
  venv, `130-CHANNELS.md` §5), and no stable release exists (PyPI `info.version` still `2.0.7`,
  `130-CHANNELS.md` §7).

After `130-LEDGER.md`'s edit, `check_permitted_claims.py` was re-run in default mode: **exit 0**,
still scanning all four contracted artifacts (§A3 shows the post-edit run; it is the same command,
re-executed after the edit landed, not a distinct one).

---

## H. Deferred items log check

No out-of-scope discovery was made during this plan's execution that required logging to
`deferred-items.md`. The pre-existing dirt in `firestarter_app` (` M .gitignore`, `.coverage`,
`.planning/config.json`, `SECURITY.md`, `write_test_port.sh`) predates this phase (`130-DECISION.md`
item 10) and is out of scope per this plan's own prohibitions; it is named here, not fixed, and not
logged separately since prior plans in this phase already recorded it as pre-existing.

---

## Claim ceiling

`no PY32F071 hardware exists` — stated in the exact form the milestone claim gate matches. This
document defers to `.planning/REQUIREMENTS.md` §"Validation Ceiling" for the full, authoritative
list of permitted and forbidden claims **by reference rather than by restating its wording** — the
claim gate's own forbidden-phrase table is named here only by file path
(`.planning/phases/123-non-regression-baselines-gate-hardening/check_permitted_claims.py`), never
quoted, per the self-reference trap this milestone's own `130-PATTERNS.md` and `130-RESEARCH.md`
warn against.

This document is one of the phase's **unscanned** artifacts (`130-NONREGRESSION.md`,
`130-HANDOFF.md`, `130-CHANNELS.md`, per v1.22's own precedent of shipping unscanned closing
records) — it is not among the four contracted targets `check_permitted_claims.py` scans by
default, and no amendment to `_DEFAULT_TARGETS` is owed by its existence.

---

## Sweep Summary

| Gate | Result |
|---|---|
| Firmware `git rev-parse --abbrev-ref HEAD` / `HEAD` | `beta` / `1c511e824d2d7e6f3db4d569ef4a2a1a505b3f79` (milestone-branch tip `05c20bf59a4f0f73acf28d48d5dbbedab5724c5f`) |
| `firestarter` `pytest tests/ -q` | **221 passed**, 0 failed, 0 skipped |
| `firestarter` `pio test -e native` / `-e native_nodevtools` | **141/141** both envs, 17 suites each |
| `firestarter` sync gate (`test_flash_path_record_sync.py`) | **41 passed** — runs in no CI leg, stated explicitly |
| Host `git rev-parse --abbrev-ref HEAD` / `HEAD` | `beta` / `5934a54984cadb66446b96f25ad40f0d8a2f0a19` (milestone-branch tip `cc9452f4db9a814ffb221bab767c24db67288365`) |
| `firestarter_app` `pytest tests/ -v --tb=no` | **1303 passed** in 110.82s |
| `firestarter_app` codegen check + drift | both clean, exit 0 |
| CLOSE-01 checker, default mode + `--explain` | exit 0; 60 exempt hits, **0 unlabeled** |
| CLOSE-01 checker fixture suite | **20 passed** |
| Claim gate, default mode | exit 0, all four contracted artifacts scanned, re-confirmed after the `130-LEDGER.md` tag fill |
| Claim gate fixture suite | **11 passed** |
| Decision parser against `130-CONTEXT.md` | **16 ids**, parseable |
| D-16 four-hash before/after proof | all four **MATCH**; 19-hunk phase-range diff touches none of lines 29–32 |
| `usb_cdc.c` lines 19–25 | guards at 19/23 intact; values at 20/24 as landed by 130-03 |
| Decision coverage | D-01…D-17, all seventeen rows present |
| Success criteria 1–4 | all discharged with named evidence; criterion 4's `13X-DECISION.md` naming addressed |
| Gitlink assertion | `firestarter` bumped `5a89ee7 → 05c20bf`; `firestarter_app` unchanged `cc9452f` |
| Tag placeholders | `130-LEDGER.md` and `ROADMAP.md`'s `v1.23` Milestones entry both filled with the observed `3.0.0b15` tag |
| Mechanical structural-gate scan, all sixteen `130-*-PLAN.md` files | empty violation list for `git push`, `git merge`, `git tag`, `gh workflow run`, `gh release create/edit/delete`, `twine upload` |

**This phase's entire verification surface is green.** Nothing in this document claims the
published image runs, boots, or installs; nothing claims the §5(c) USB-identity condition has been
met; nothing claims pid.codes' own terms make the source warning mandatory. This plan ticks
CLOSE-01, CLOSE-02, CLOSE-03 and CLOSE-04 in `.planning/REQUIREMENTS.md`, each citing the section
above that discharges it.

---

*Phase: 130-close-honesty-ledger-claim-gate-release-decision*
*Written: 2026-08-02 (Plan 130-16)*
