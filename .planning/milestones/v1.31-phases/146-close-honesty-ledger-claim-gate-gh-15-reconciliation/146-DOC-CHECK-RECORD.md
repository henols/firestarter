# Phase 146 — CLOSE-03 Documentation Check Record

**Owner requirement:** CLOSE-03. This document is the **RED half** of the D-13 documentation check:
`146-check-close03-docs.py` authored, armed against the four real sub-repo documentation targets, and
seen to fail for reasons stated by name — **before any documentation is edited**.

**Measured:** 2026-08-17, live. Plan `146-02`, immediately after committing the checker at
`57830381`. Every command in this document was executed here; **no figure is copied from
`146-RESEARCH.md`**, and where a measurement diverges from what research or the plan recorded, the
divergence is stated rather than reconciled.

**Exit-status discipline (RESEARCH Pitfall 5).** Every exit status below was captured with `rc=$?`
**immediately after the command that produced it**, never after a pipe. A recorded instance in this
project printed `EXIT=0` for a script that had just printed a `FAIL:` line, because the status came
from `tail`. Where a count is taken through `wc -l`, the producing command and the count are separate
steps so the producer's own status stays observable.

**Nothing in this document claims any topic is present.** Every topic this checker requires is
recorded here as **unsatisfied** or **satisfied-today**, as measured; the edits that turn the
unsatisfied ones green belong to plans `146-06` (firmware docs) and `146-07` (host docs).

**Citation discipline (D-14).** Forbidden-phrase findings are cited by `file:line` plus the
checker's own pattern label. The phrases themselves are **not reproduced** in this document. Where a
measuring command's regex would itself have spelled a forbidden token, the token is written as a
single-character class (`[v]`) — a behaviourally identical ERE, measured identical in §2.3 — so this
record does not plant a copy of the text the checker forbids. This is not fastidiousness: this phase
has already observed the self-reference trap fire live, and six `125-0N-SUMMARY.md` files trip the
sibling claim gate for exactly this reason.

**The self-reference trap fired on this record too, and the residue is measured rather than
claimed away.** The discipline above is about the *phrases*; it cannot extend to the checker's own
**pattern labels**, and pattern 10's label spells the token it forbids as its own first component.
Citing a finding by label — which §1 and §3.3 must do, because the label is half of what a reader
needs — therefore leaves the token present. Measured on this file, after the two prose uses of the
bare word were reworded out of it:

| Scan of this record | Command, as run | Result |
|---|---|---|
| pattern-10 occurrences | `grep -oiE '\bpro[v]en\b' 146-DOC-CHECK-RECORD.md \| wc -l` | **10** |
| of those, the pattern label | `grep -oiE 'pro[v]en-unqualified' 146-DOC-CHECK-RECORD.md \| wc -l` | **10** |
| all twelve patterns, via the checker through its own seam | `FIRESTARTER_DOCSCAN_TARGETS_146="<this file>" python3 146-check-close03-docs.py` | `rc=1`, **10** matches, every one the label |

So **10 of 10 remaining hits are the pattern label**, and zero are a claim about anything. The count
was **12** before this paragraph was written: two were genuine prose uses of the bare word in §§0 and
2.3, found by re-running the scan over this record *after* drafting it rather than assuming a prose
edit was inert, and both were reworded. This record is not a target of any gate (see the paragraph
above), so those 10 label hits turn nothing red today — but the number is recorded here so that a
future reader who adds this file to a target set knows exactly what it will report and why, instead of
rediscovering it as a mystery regression.

**This document is not a claim-gate target.** `146-check-claims.py`'s `_DEFAULT_TARGETS` (`:114-120`)
are the five closing artifacts; this record is none of them, and it is not a target of the Phase 130
record gate either (`check_record_corrections.py:163-171`). The D-14 discipline above is therefore
observed by choice, not compelled by a gate.

---

## 1. RED (pre-edit) — the checker's own failure, per file and per topic

**Command, as run** (from the phase directory, no argv, no environment seam):

```
cd /workspaces/.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation
python3 146-check-close03-docs.py > /tmp/gsd146/doc_pre.txt 2>&1; rc=$?
```

**`rc=1`** — captured immediately after the interpreter exited, with no pipe in the pipeline.

**Full stdout, verbatim:**

```
FAIL: 4 forbidden phrase match(es):
  /workspaces/firestarter/CLAUDE.md:64: forbidden phrase match [proven-unqualified]: <redacted per D-14>
  /workspaces/firestarter/CLAUDE.md:65: forbidden phrase match [proven-unqualified]: <redacted per D-14>
  /workspaces/firestarter/CLAUDE.md:65: forbidden phrase match [proven-unqualified]: <redacted per D-14>
  /workspaces/firestarter/CLAUDE.md:66: forbidden phrase match [proven-unqualified]: <redacted per D-14>
FAIL: 7 unsatisfied required CLOSE-03 topic(s):
  /workspaces/firestarter/doc/PROTOCOLS.md: missing required topic [program-vcc-ceiling]: expected text describing 'the ~6.25 V program-VCC accepted debt'
  /workspaces/firestarter/doc/PROTOCOLS.md: missing required topic [pulse-override-flag]: expected text describing "the host's per-run program-pulse override flag"
  /workspaces/firestarter/CLAUDE.md: missing required topic [program-vcc-ceiling]: expected text describing 'the ~6.25 V program-VCC accepted debt'
  /workspaces/firestarter/README.md: missing required topic [per-byte-algorithm]: expected text describing 'the shipped per-byte pulse-to-verify loop'
  /workspaces/firestarter/README.md: missing required topic [program-vcc-ceiling]: expected text describing 'the ~6.25 V program-VCC accepted debt'
  /workspaces/firestarter_app/README.md: missing required topic [program-vcc-ceiling]: expected text describing 'the ~6.25 V program-VCC accepted debt'
  /workspaces/firestarter_app/README.md: missing required topic [pulse-override-flag]: expected text describing "the host's per-run program-pulse override flag"
FAIL: scanned firestarter/doc/PROTOCOLS.md, firestarter/CLAUDE.md, firestarter/README.md, firestarter_app/README.md (4 file(s)); see the buckets above
```

**The only alteration to that transcript is the four `<redacted per D-14>` substitutions**, each
replacing the matched token the checker echoed back. The `file:line` and the pattern label — the two
things a reader needs to find the site — are untouched, and the sites are independently cross-checked
in §2.3.

### 1.1 The per-file × per-topic matrix, transcribed from the checker's own report

`✗` = **required and unsatisfied** (named in the bucket above). `✓` = required and satisfied
(required by this file's set, and *not* named in the bucket — satisfaction is inferred from the
report's silence on a topic it does require, which is the report's own contract, not a separate
grep). `—` = not in this file's required set at all, per `_REQUIRED_TOPICS_BY_FILE`.

| Target | `per-byte-algorithm` | `parameter-table` | `database-supplied-pulse` | `pulse-override-flag` | `program-vcc-ceiling` | Verdict |
|---|---|---|---|---|---|---|
| `firestarter/doc/PROTOCOLS.md` | ✓ | ✓ | ✓ | **✗** | **✗** | **FAIL** (2 unsatisfied) |
| `firestarter/CLAUDE.md` | ✓ | ✓ | ✓ | ✓ | **✗** | **FAIL** (1 unsatisfied + 4 forbidden hits) |
| `firestarter/README.md` | **✗** | — | — | — | **✗** | **FAIL** (2 unsatisfied) |
| `firestarter_app/README.md` | — | — | ✓ | **✗** | **✗** | **FAIL** (2 unsatisfied) |

**Totals cross-checked against the report's own arithmetic:** 2 + 1 + 2 + 2 = **7** unsatisfied
topics, which is exactly the count the report prints. Four of four targets fail. Four forbidden-phrase
matches, all in one file.

### 1.2 The RED is for a named reason, and the named reason is the one research predicted

**`program-vcc-ceiling` is unsatisfied in all four targets** — the ~6.25 V program-VCC accepted debt
appears in no sub-repo document this checker scans. That is the single largest CLOSE-03 gap, it needed
no plant, and it is the observation that makes this a *true* RED rather than a pre-authored leg that
has never been seen to fail for the right reason (RESEARCH Pitfall 4). The failure is a bucketed
`FAIL:` report naming the topic id per file — **not** a traceback, not an `ImportError`, and not a
missing-file error. Those three would each be a task failure dressed as a RED, and none occurred.

**Divergence check against research's five-topic × six-file matrix — none found.** Research predicted
`--pulse-us` absent from `firestarter/doc/PROTOCOLS.md` and from `firestarter_app/README.md`, present
in `firestarter/CLAUDE.md`; and `6.25` absent everywhere. All four hold exactly, measured by the
checker's own regexes rather than by re-running research's greps. The one thing worth stating rather
than glossing: `firestarter_app/README.md` **satisfies** `database-supplied-pulse` today, because the
`pulse-delay` database field is documented in its §Eprom Configuration. Research graded that cell `~`
("present but incomplete — nothing about the firmware reading it per byte"), and the checker
necessarily grades it `✓`, because a presence regex cannot see incompleteness. **The checker is
weaker than research's reading on that one cell, and this is recorded rather than papered over** —
it is exactly the boundary the module docstring's explicit non-claim draws, and it is why plan
`146-12`'s operator wording review is blocking rather than advisory.

---

## 2. The four runnable-today content locators, recorded RED

**Why record a locator's RED at all.** A locator that has only ever been observed green proves
nothing about the locator: it may be pointed at the wrong file, matching on the wrong line, or
succeeding for a reason unrelated to its subject. Phase 145 found **three** false GREENs in its own
acceptance set, one of which passed against a record with no content in it. These four locators are
the cheapest available proof that each one is wired to the file it names, because each is a **true**
RED today and becomes green only when the specific text changes. This section is the RED half of a
before/after pair; **plan `146-06` owns the GREEN half** and appends it as §5.

All four were run from `/workspaces`. Each exit status was captured immediately after its `grep`.

| # | Command, as run | Output | `rc` | Now | Required after `146-06` |
|---|---|---|---|---|---|
| L1 | `grep -c 'Phase 141 replaces it' firestarter/doc/PROTOCOLS.md` | `1` | `0` | **1** | **0** |
| L2 | `grep -c 'eprom.cpp:159-179' firestarter/doc/PROTOCOLS.md` | `1` | `0` | **1** | **0** |
| L3 | `grep -c '71 cases' firestarter/CLAUDE.md` | `1` | `0` | **1** | **0** |
| L4 | `grep -c '79 cases' firestarter/CLAUDE.md` | `0` | `1` | **0** | **≥ 1** |

All four match the values `146-VALIDATION.md`'s two *runnable today — true RED* rows predict
(`1` and `1`; `1` and `0`).

**An exit-status subtlety worth stating, because it will bite the GREEN half.** L4's `rc=1` is not an
error: `grep -c` exits **1** when the count it prints is `0`. So for L1–L3 the *required* post-edit
state (`0`) will come with `rc=1`, and for L4 the required post-edit state (`≥1`) will come with
`rc=0` — the statuses **invert** across the edit. Any post-edit criterion written as
`grep -c … && …` therefore reads backwards from what it intends. Assert on the printed integer, as
the table above does, not on `grep`'s status.

### 2.1 What L1 and L2 actually point at

`firestarter/doc/PROTOCOLS.md` §1.3 (the `0x07` row), inside lines 129–167, still asserts that the
firmware's present write loop is retry escalation of the database pulse width and that Phase 141
*will* replace it. Both halves are stale, and the surrounding paragraph is otherwise accurate and
must not be re-derived. Phase 141 landed five phases ago; the source line reference L2 matches no
longer points at a write loop at this tip. This is recorded from reading both the document and the
source in this task, not from research's rendering of it.

### 2.2 What L3 and L4 point at

`firestarter/CLAUDE.md` §Native (Host) Test Environment, the Phase 142 addition at the end of the
file, states a native-env total that F-144-01 superseded. L3 matches the stale total; L4 is the
corrected total and matches nothing today. **The two together are a stronger pair than either alone**:
L3 alone could go green by deleting the sentence, and L4 alone could go green by adding the number
anywhere in the file. Requiring L3 `→ 0` *and* L4 `→ ≥1` is what makes the pair a correction rather
than a deletion or an insertion.

### 2.3 The forbidden-claim-word baseline in `firestarter/CLAUDE.md` — 4 occurrences on 3 lines

The checker's pattern **10**, `proven-unqualified`, is a bare-word match with no qualifying context
permitted. Its baseline in `firestarter/CLAUDE.md`, measured as **occurrences** rather than lines:

| Form | Command, as run | Output | `rc` |
|---|---|---|---|
| occurrence count (the one that matters) | `grep -oiE '\bpro[v]en\b' firestarter/CLAUDE.md > /tmp/gsd146/pw.txt` then `wc -l < /tmp/gsd146/pw.txt` | **4** | `0` (producer), then the count |
| line count (the misleading one) | `grep -ciE '\bpro[v]en\b' firestarter/CLAUDE.md` | **3** | `0` |

**`grep -c` reports 3, and 3 is the wrong number for this purpose.** `-c` counts matching *lines*;
one of the three lines carries the token twice. The checker's own behaviour follows the
**occurrence** count — `scan_text` iterates `pattern.finditer(line)` per line, so it records one
violation per match, and its report prints **4** rows. The occurrence form is therefore the form that
agrees with the gate, and the producer's status is captured on the producing `grep`, with `wc -l` run
as a separate command.

**Equivalence of the bracketed form, measured rather than asserted.** The `[v]` single-character class
is only a device to keep this record from planting a literal copy of the token. Measured both ways in
this task: the bracketed ERE through `grep -oiE … | wc -l` gives **4**, and an independent
`re.findall(r'\bproven\b', …, re.I)` in Python over the same file gives **4**. Same count, so the
bracketing changes nothing about what is measured.

**The four sites, cited by location only** — no sentence from any of them is reproduced anywhere in
this record:

| Site | Occurrences on that line | Context (structural only) |
|---|---|---|
| `firestarter/CLAUDE.md:64` | 1 | §Algorithm Handlers, the `0x07` table row |
| `firestarter/CLAUDE.md:65` | 2 | §Algorithm Handlers, the `0x08` table row |
| `firestarter/CLAUDE.md:66` | 1 | §Algorithm Handlers, the `0x0B` table row |

Per-line counts measured individually (`sed -n "${n}p" … | grep -oiE '\bpro[v]en\b' | wc -l` for
`n` in 64, 65, 66) and summing to 4, which agrees with the whole-file occurrence count above and with
the checker's four report rows at those same three line numbers.

**Required after plan `146-06`: 0 occurrences.** Until then the checker is red on
`firestarter/CLAUDE.md` for this reason *in addition to* its unsatisfied `program-vcc-ceiling` topic —
two independent causes in one file, which is worth knowing because fixing only one of them leaves the
file red and could be misread as the fix having failed.

---

## 3. The three non-vacuity legs

Each leg's status was captured immediately after the interpreter exited. Legs 1 and 2 are the two
guards; **leg 3 is the positive control**, and without it the first two failures could equally be
explained by the environment seam simply being unusable.

### 3.1 Leg 1 — emptied seam → non-zero, and no `PASS:` line

```
FIRESTARTER_DOCSCAN_TARGETS_146="" python3 146-check-close03-docs.py > /tmp/gsd146/doc_empty.txt 2>&1; rc=$?
```

**`rc=1`.** Stdout, verbatim and complete (one line):

```
FAIL: no scan targets resolved -- this checker cannot vacuously pass with nothing scanned
```

`grep -q 'PASS:'` over that output finds nothing. The `is not None` test in `resolve_targets`
(`146-check-close03-docs.py`) is what makes this distinguishable from an absent variable: an
explicitly empty seam resolves to **zero** targets rather than silently falling back to the four
defaults.

### 3.2 Leg 2 — seam repointed at a path that does not exist → non-zero, naming the path

```
FIRESTARTER_DOCSCAN_TARGETS_146="/workspaces/firestarter/doc/NO-SUCH-DOC.md" \
  python3 146-check-close03-docs.py > /tmp/gsd146/doc_missing.txt 2>&1; rc=$?
```

**`rc=1`.** Stdout, verbatim and complete (one line):

```
FAIL: scan target(s) not found on disk -- this checker cannot vacuously pass with a target silently skipped (a renamed or moved document is a hard failure, never a skip): ['/workspaces/firestarter/doc/NO-SUCH-DOC.md']
```

The absent path is named in the message. This is the leg that answers the recorded fail-open pattern:
a renamed or moved document is a hard failure here, never a skipped target that lets the run pass.

### 3.3 Leg 3 — seam at one readable target → a report, not either failure message (**positive control**)

```
FIRESTARTER_DOCSCAN_TARGETS_146="/workspaces/firestarter/CLAUDE.md" \
  python3 146-check-close03-docs.py > /tmp/gsd146/doc_one.txt 2>&1; rc=$?
```

**`rc=1`**, and — the point of the leg — the output is a **content report**, carrying neither the
never-vacuous message nor the not-found message:

```
FAIL: 4 forbidden phrase match(es):
  /workspaces/firestarter/CLAUDE.md:64: forbidden phrase match [proven-unqualified]: <redacted per D-14>
  /workspaces/firestarter/CLAUDE.md:65: forbidden phrase match [proven-unqualified]: <redacted per D-14>
  /workspaces/firestarter/CLAUDE.md:65: forbidden phrase match [proven-unqualified]: <redacted per D-14>
  /workspaces/firestarter/CLAUDE.md:66: forbidden phrase match [proven-unqualified]: <redacted per D-14>
FAIL: 1 unsatisfied required CLOSE-03 topic(s):
  /workspaces/firestarter/CLAUDE.md: missing required topic [program-vcc-ceiling]: expected text describing 'the ~6.25 V program-VCC accepted debt'
FAIL: 1 file(s) scanned ... see the buckets above
```

*(The last line is reproduced from `/tmp/gsd146/doc_one.txt` in the report's own wording:
`FAIL: scanned firestarter/CLAUDE.md (1 file(s)); see the buckets above`.)*

**What the control establishes.** The seam is usable, it accepts a single path, and a run through it
reaches the scanning stage and reports on content. So legs 1 and 2 failed **because of vacuity and
absence**, not because setting the variable breaks the script. It also independently reproduces this
file's row of §1.1's matrix from a different invocation path, and — since a single-file run still
resolves that file's required set from `_REQUIRED_TOPICS_BY_FILE` — shows the per-file rule survives
being reached through the seam rather than through the defaults.

### 3.4 A fourth observation, kept because it is the substituted self-check leg working on real files

Running the checker through the seam at three documents that are **not** in
`_DOC_TARGET_ALLOWLIST` (`firestarter_app/CLAUDE.md` and both
`firestarter_app/doc/protocol-*.md`) produced `rc=1` with **14** unsatisfied topics — the full
five-topic set demanded of each of the two files it has never heard of, and four of five for
`firestarter_app/CLAUDE.md` (whose `database-supplied-pulse` mention happens to satisfy that one
topic). This is `_required_topics_for()`'s unknown-path branch failing **closed** against real files
rather than against a synthetic path, which is a stronger observation than the introspection
assertion on `'some/unknown/doc.md'` alone. Those three files are **not** targets — see §4.

---

## 4. Out-of-target-set findings, recorded as decisions rather than omissions

Two candidate documents (three files) were read in this task and are deliberately **not** in
`_DEFAULT_TARGETS`. Stating them is what makes the omission read as a decision. All three are
recorded as **found, out of scope for this phase, unedited** — none of them is recorded as a pass.

| Finding | Location | Checker's label | Disposition |
|---|---|---|---|
| F-146-02-A | `firestarter_app/CLAUDE.md:46` | `verified-on-silicon`, 1 match | **found, out of scope, unedited** |
| F-146-02-B | `firestarter_app/doc/protocol-id.md` | zero forbidden matches | **found, out of scope, unedited** |
| F-146-02-C | `firestarter_app/doc/protocol-flags.md` | zero forbidden matches | **found, out of scope, unedited** |

**F-146-02-A — why it is not a target.** The hit sits on a single long line in the host repository's
key-files inventory, inside a `firestarter/channel.py` description. It is a real match under the
checker's pattern table, and it is cited here by `file:line` and label only, per D-14. It is **not**
a CLOSE-03 target because CLOSE-03 asks about five specific subjects — the per-byte algorithm, the
parameter table, the database-supplied pulse, the override flag and the program-VCC ceiling — and
`firestarter_app/CLAUDE.md` is the home of none of them. Adding it as a fifth target would mean
requiring five topics of a file whose job is describing the host package's module layout, and would
enlarge D-06's wording-only edit surface for a phrase that is not what CLOSE-03 is about. **Not
edited in this phase.** If the operator wants it fixed, it is a one-line wording change and belongs
in a follow-up, recorded rather than silently carried.

**F-146-02-B / F-146-02-C — why they are not targets.** These two are the host-side protocol
reference pair. Both measure **zero** forbidden-phrase matches, so nothing needs removing from
either. They are left out of the target set because the host half of CLOSE-03 lands in
`firestarter_app/README.md` — the document a CLI user actually reads before running `write` — and
because requiring the override flag and the ceiling in three host documents instead of one would
spread the same sentence across files without adding a reader. Their zero-match state is recorded as
a **measurement**, explicitly not as a pass of a gate they are not subject to.

### 4.1 A mechanism finding from this task's own verification, recorded because it is a false-GREEN shape

The plan's sub-repo-cleanliness leg is written `cd /workspaces && test "$(git -C firestarter status
--porcelain | wc -l)" = "0" && echo …`. Run **without** that `cd` — from the phase directory, as
happens when it is appended to a command that already changed directory — `git -C firestarter`
fails with `fatal: cannot change to 'firestarter'`, `wc -l` counts zero lines of output, the `test`
compares `0` to `0` and **passes**, and the reassuring message prints. Observed live in this task.
The assertion is then vacuous: it would print the same thing if the firmware repository were filthy.
The `cd /workspaces` is load-bearing, and the leg was re-run from the repository root to obtain the
real reading (`0` lines, recorded in §5 below). Anchor such a leg to an absolute path
(`git -C /workspaces/firestarter …`) rather than relying on the caller's working directory.

---

## 5. Sub-repo working trees at the close of this plan

Measured from `/workspaces` after this plan's second commit, each status captured immediately:

| Repo | Command, as run | Result | Baseline in `146-CITATIONS.md` §0.3 | Match? |
|---|---|---|---|---|
| `firestarter` | `git -C /workspaces/firestarter status --porcelain \| wc -l` | **0** | **0** | **yes** |
| `firestarter_app` | `git -C /workspaces/firestarter_app status --porcelain \| wc -l` | **7** | **7** | **yes** |

Both sub-repos are at their phase-start baselines. **No documentation file was edited in this plan** —
this plan writes the checker and records its RED; the edits are `146-06` and `146-07`.

---

## 6. What this record does not contain, and who owes it

- **§7 — the firmware-doc GREEN.** Plan **`146-06`** appends it: L1 `→ 0`, L2 `→ 0`, L3 `→ 0`,
  L4 `→ ≥1`, the `proven-unqualified` occurrence count `→ 0`, and the checker green on
  `firestarter/doc/PROTOCOLS.md`, `firestarter/CLAUDE.md` and `firestarter/README.md`.
- **§8 — the host-doc GREEN and the whole-checker GREEN.** Plan **`146-07`** appends it:
  `firestarter_app/README.md`'s three topics satisfied, and `python3 146-check-close03-docs.py` with
  no argv and no seam at **`rc=0`** with a `PASS:` line naming all four files.
- **The judgement this checker cannot make.** A green run means the five topics are **present**, not
  that the prose is correct. That is plan **`146-12`**'s blocking operator wording review, and no
  green run recorded in this file may be reported as having discharged it.
- **CLOSE-03 itself is not ticked by this plan.** Only plan `146-13` may tick `CLOSE-01` through
  `CLOSE-05`.

---

## 7. GREEN (post `146-06`) — the four firmware-doc locator flips and the claim-word clear

**Measured:** 2026-08-17, live, from `/workspaces`, immediately after this plan's sub-repo commit
`f82479b` (previous `firestarter` tip: `fa6c9c7`). Every command below is the identical command
text §2 and §2.3 used for the RED half.

### 7.1 The four locators, before and after

| # | Command, as run | RED (§2) | GREEN (now) | Required | Match? |
|---|---|---|---|---|---|
| L1 | `grep -c 'Phase 141 replaces it' firestarter/doc/PROTOCOLS.md` | `1` | **`0`** | `0` | yes |
| L2 | `grep -c 'eprom.cpp:159-179' firestarter/doc/PROTOCOLS.md` | `1` | **`0`** | `0` | yes |
| L3 | `grep -c '71 cases' firestarter/CLAUDE.md` | `1` | **`0`** | `0` | yes |
| L4 | `grep -c '79 cases' firestarter/CLAUDE.md` | `0` | **`1`** | `≥ 1` | yes |

All four printed integers were captured directly (never through `grep`'s exit status, per §2's own
warning — L1-L3's `rc=1` here is expected, since each now prints `0`).

### 7.2 The claim-word occurrence count, before and after

| Form | Command, as run | RED (§2.3) | GREEN (now) |
|---|---|---|---|
| occurrence count | `grep -oiE '\bpro[v]en\b' firestarter/CLAUDE.md \| wc -l` | **4** | **0** |

All seven cited technical identifiers (`MSG_ERR_MAX_PULSES`, `MSG_ERR_ENERGY_CAP`,
`MSG_ERR_PULSE_TOO_WIDE`, `MSG_DATA_PROGRESS`, `eprom_hv_route_mask`, `command_done`,
`EPROM_PROGRESS_EMIT_INTERVAL_MS`) were checked present after the reword — all seven survive.

### 7.3 The checker, run per-file through the seam (the §3.3-style positive control)

```
FIRESTARTER_DOCSCAN_TARGETS_146="/workspaces/firestarter/doc/PROTOCOLS.md" python3 146-check-close03-docs.py   # rc=0
FIRESTARTER_DOCSCAN_TARGETS_146="/workspaces/firestarter/CLAUDE.md"        python3 146-check-close03-docs.py   # rc=0
FIRESTARTER_DOCSCAN_TARGETS_146="/workspaces/firestarter/README.md"       python3 146-check-close03-docs.py   # rc=0
```

Each of the three prints a `PASS:` line naming that one file, zero forbidden-phrase matches, every
required CLOSE-03 topic for that file present. This is the GREEN §6 promised for these three files.

### 7.4 The whole checker, no argv, no seam — still RED, and RED for exactly the bucket owed elsewhere

```
python3 146-check-close03-docs.py   # rc=1
```

```
FAIL: 2 unsatisfied required CLOSE-03 topic(s):
  /workspaces/firestarter_app/README.md: missing required topic [program-vcc-ceiling]: expected text describing 'the ~6.25 V program-VCC accepted debt'
  /workspaces/firestarter_app/README.md: missing required topic [pulse-override-flag]: expected text describing "the host's per-run program-pulse override flag"
FAIL: scanned firestarter/doc/PROTOCOLS.md, firestarter/CLAUDE.md, firestarter/README.md, firestarter_app/README.md (4 file(s)); see the buckets above
```

Down from **7 unsatisfied topics + 4 forbidden-phrase matches** at RED to exactly **2 unsatisfied
topics, 0 forbidden matches** now — both remaining topics are `firestarter_app/README.md`'s, owed
by plan **`146-07`**, which appends **§8** and is the only plan that may report `rc=0` with a
`PASS:` line naming all four files. **This plan does not chase that green** — reaching it here would
mean editing `firestarter_app/README.md`, which is out of `146-06`'s file set (`146-DOC-CHECK-RECORD.md`
§1.1 already scoped it there) and would take from `146-07` the RED→GREEN flip it is meant to show.

### 7.5 The firmware suite, run once, after the commit

```
cd /workspaces/firestarter && python3 -m pytest tests -o addopts="" -q
```

`314 passed in 15.34s`, exit `0`. No `146-CITATIONS.md` §0 baseline exists for this suite, so this
count is recorded as the phase's firmware-suite baseline for plan `146-07` to compare against,
not compared against a prior figure. `firestarter`'s inner porcelain was `0` before the run and `0`
after (the run created no untracked artifacts).

### 7.6 Sub-repo state at the close of this plan

| Item | Before this plan | After this plan |
|---|---|---|
| `firestarter` submodule tip | `fa6c9c7` | `f82479b` |
| `firestarter` inner porcelain | `0` | `0` |
| `firestarter` upstream-ahead (`git rev-list --count @{u}..HEAD`) | `61` | `62` |
| `firestarter_app` inner porcelain | `7` | `7` (untouched, per prohibition) |

The ahead-count rose by exactly one (this plan's single sub-repo commit) and never fell — no push
occurred (D-01).

---

## 8. GREEN (post `146-07`) — the host-doc flip and the whole-checker GREEN

**Measured:** 2026-08-17, live, from `/workspaces`, after this plan's three commits: `firestarter_app`
`eca71b2` (README), `firestarter` `f8ac643` (catalog only), `firestarter_app` `3cf429f` (catalog +
messages.py), meta `878e60d` (canonical catalog).

### 8.1 The checker, no argv, no seam — GREEN across all four targets

```
cd /workspaces/.planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation
python3 146-check-close03-docs.py
```

**`rc=0`.** Full stdout, verbatim:

```
PASS: scanned firestarter/doc/PROTOCOLS.md, firestarter/CLAUDE.md, firestarter/README.md, firestarter_app/README.md; 4 file(s), zero forbidden-phrase matches, every required CLOSE-03 topic present in the file that owes it (this PASS means the topics are PRESENT, not that the prose is correct -- see the module docstring's explicit non-claim; correctness is the blocking operator wording review in plan 146-12)
```

### 8.2 The per-file × per-topic matrix, fully satisfied — diff this against §1.1

| Target | `per-byte-algorithm` | `parameter-table` | `database-supplied-pulse` | `pulse-override-flag` | `program-vcc-ceiling` | Verdict |
|---|---|---|---|---|---|---|
| `firestarter/doc/PROTOCOLS.md` | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| `firestarter/CLAUDE.md` | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| `firestarter/README.md` | ✓ | — | — | — | ✓ | **PASS** |
| `firestarter_app/README.md` | — | — | ✓ | ✓ | ✓ | **PASS** |

Every cell that was `✗` in §1.1 is now `✓`. `firestarter_app/README.md`'s two owed topics
(`pulse-override-flag`, `program-vcc-ceiling`) are the only cells this plan flipped; the third cell
(`database-supplied-pulse`) was already satisfied at RED (§1.2) and this plan additionally extended
its treatment in the EEPROM-configuration section without changing its satisfied/unsatisfied status.

### 8.3 Both non-vacuity legs, re-shown in this session

**Leg 1 — emptied seam → non-zero, no `PASS:` line:**

```
FIRESTARTER_DOCSCAN_TARGETS_146="" python3 146-check-close03-docs.py
```

`rc=1`. Stdout, verbatim (one line): `FAIL: no scan targets resolved -- this checker cannot vacuously
pass with nothing scanned`. `grep -c 'PASS:'` over that output: **0**.

**Leg 2 — seam naming one real target plus one nonexistent path → non-zero, naming the missing path:**

```
FIRESTARTER_DOCSCAN_TARGETS_146="/workspaces/firestarter_app/README.md:/workspaces/firestarter/doc/NO-SUCH-DOC.md" \
  python3 146-check-close03-docs.py
```

`rc=1`. Stdout, verbatim (one line): `FAIL: scan target(s) not found on disk -- this checker cannot
vacuously pass with a target silently skipped (a renamed or moved document is a hard failure, never a
skip): ['/workspaces/firestarter/doc/NO-SUCH-DOC.md']`. The absent path is named.

`146-check-close03-docs.py` is byte-unchanged by this plan (`git status --porcelain` on it prints no
output) — the GREEN in §8.1 was reached entirely by editing the documents it scans, never the checker.

### 8.4 Task 2's pre-commit regen diff shape — captured before any commit, one row per repository

| Repository | File | Numstat (captured pre-commit) | Reading |
|---|---|---|---|
| meta (`/workspaces`) | `tools/catalog/messages.toml` | `1 1 tools/catalog/messages.toml` | one changed line, the format string only (`git diff -U0`: `-format = "Mismatch, retrying with increased pulse delay from %d to %d"` / `+format = "Pulse delay mismatch: expected %d, got %d"`) |
| `firestarter` | `include/messages.h` | *(empty — zero lines of numstat output)* | zero-line diff; the generated header is identifier-only, so a wording change never touches it |
| `firestarter_app` | `firestarter/messages.py` | `1 1 firestarter/messages.py` | exactly one changed line; hunk read and confirmed as the same message's `format=` line at line 1072 |

All three catalog copies (canonical + both sub-repo vendored copies) measured at one distinct sha256
digest (`cd5a0bb9...5855ffa`) after the sync. The stale format string (`grep -c 'Mismatch, retrying
with increased pulse delay'` against the canonical catalog) measures **0**; the orphaned
`MSG_INFO_RETRIES` (`0x51`) stanza measures **1**, present and unedited.

### 8.5 Both sub-repo suite counts, with comparison basis

| Suite | Command | Result | rc | Comparison basis |
|---|---|---|---|---|
| `firestarter` (native) | `python3 -m pytest tests -o addopts="" -q` | **314 passed in 14.51s** | `0` | Compared against `146-06`'s recorded baseline of 314 passed (§7.5) — unchanged |
| `firestarter_app` (host) | `python3 -m pytest tests -o addopts="" -q` | **1590 passed, 1 warning, 30 snapshots passed, in 232.46s** | `0` | No `146-CITATIONS.md` §0 host-suite figure exists; recorded here as the host-suite baseline for any later plan to compare against |

Both sub-repo porcelains were confirmed at their recorded baselines (`firestarter` **0**,
`firestarter_app` **7**) immediately before either suite ran, and remained at those same counts
immediately after — neither suite created an untracked artifact.

### 8.6 Sub-repo state at the close of this plan

| Item | Before this plan | After this plan |
|---|---|---|
| `firestarter` submodule tip | `f82479b` | `f8ac643` |
| `firestarter` inner porcelain | `0` | `0` |
| `firestarter` upstream-ahead | `62` | `63` |
| `firestarter_app` inner porcelain | `7` | `7` (untouched) |
| `firestarter_app` upstream-ahead | `16` | `18` |
| meta upstream-ahead | `263` | `264` |

Every ahead-count rose (meta by 2, `firestarter` by 1, `firestarter_app` by 2 — matching this plan's
four commits, one landing in two repositories at once is not the case here: each commit is single-repo)
and none fell — no push occurred (D-01).

### 8.7 What this section does not establish

This checker's GREEN means the five CLOSE-03 topics are **present** in the four documents that owe
them. It does not mean the prose describing them is correct, complete, or well-placed — that judgement
is plan `146-12`'s blocking operator wording review, and this GREEN is not reported anywhere in this
plan's SUMMARY as having discharged it. CLOSE-03 itself is not ticked by this plan; only plan `146-13`
may tick any `CLOSE-*` requirement.
