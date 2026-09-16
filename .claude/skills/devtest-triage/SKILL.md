---
name: devtest-triage
description: Triage community `dev test` chip-validation issues in henols/firestarter against the chip's real datasheet. Close a PASS issue and log the chip. Close a failure when a later PASS supersedes it. Post a datasheet-grounded findings comment on the rest. Labels every issue by cause. Use this skill to triage dev test issues, or go through the chip test reports. Use it also to check an EPROM against its datasheet, or check the pin map or VPP for a chip. Use it to close passing validation issues, defer failures that later passed, or work an issue like "[dev test] at28c256 — FAIL".
---

# Triage `dev test` issues against the datasheet

One community `dev test` issue in → one of three outcomes. The issue is **closed and
the chip logged** (PASS). Or the issue is **closed against a later PASS that supersedes
it** (§3a). Or triage posts a **datasheet-grounded comment** naming every capability that
disagrees with the database (FAIL / marginal). Every outcome carries a label saying
what happened and, where triage got that far, who owns the fix (§3b).

This skill only inspects firestarter code. It sends output only to GitHub, plus one
ledger entry. It never edits the chip database — see `devtest-rootcause` for the fix side.

**Self-contained.** `scripts/devtest_issues.py` is stdlib-only and owns its own issue
parser. It does not import or shell out to anything in `firestarter_app`, so it keeps
working if that repo moves, is renamed, or is not checked out. External tools it does
use: `gh`, `curl`, `pdftotext`. Do not replace it with a call into `firestarter_app/tools/`.

```bash
# ROOT works from anywhere in the checkout, including inside either submodule.
ROOT=$(git rev-parse --show-superproject-working-tree 2>/dev/null)
ROOT=${ROOT:-$(git rev-parse --show-toplevel)}

LEDGER=$ROOT/VALIDATED-EPROMS.md
APP=$ROOT/firestarter_app              # only for `firestarter info` + datasheet cache
S=$ROOT/.claude/skills/devtest-triage/scripts

python3 $S/devtest_issues.py list       # every open [dev test] issue + verdict
python3 $S/devtest_issues.py show 21    # parse one issue and route it
python3 $S/devtest_issues.py fold       # group issues by EPROM (dry run)
python3 $S/devtest_issues.py labels     # create the label taxonomy (idempotent)
python3 $S/eprom_ledger.py check        # the ledger still matches a fresh render
```

## 1. Enumerate and pick the issues

```bash
python3 $S/devtest_issues.py list
```

Real output:

```
#50   FAIL           sst39sf040     52af74c52f2c
#45   FAIL           W27E040        957307f7b750
#31   INCONCLUSIVE   m27c1001       d8771536cb43
#28   FAIL           m27c512        31547956e56b
#23   FAIL           w27e257        7a89fcea856a
#21   FAIL           at28c256       00e121446ceb
```

Columns: issue number, the title's verdict, the chip, and `dedup_fingerprint`.
**Two issues sharing a fingerprint are the same failure reported twice** — triage once
and cross-reference. That is only the narrowest overlap, though: §3 folds by EPROM,
which also catches alias-different names for one part and distinct failures of it. Run
the fold before triaging anything.

## 2. Parse the report

```bash
python3 $S/devtest_issues.py show 21
```

Real output, reproduced offline from a committed fixture (a report that carries no
firmware identity, which is what the `firmware` row below is showing):

```bash
python3 $S/devtest_issues.py show --body-file $S/../fixtures/dev-test-at28c256-null-identity.md --title '[dev test] at28c256 — FAIL'
```

```
#?  at28c256  —  FAIL
  schema      1.2   generated 2026-08-07T12:07:39Z
  host        3.0.0b15   hw Rev 2.0-class, Override HW: Rev 2.3
  firmware    not reported -- NOT attributable to a firmware version -- ask the reporter for a fresh dev test run on a current host build
  protocol    0x0D   chip at28c256
  fingerprint 00e121446ceb

  step         verdict    reason
  id           NA         no chip-id in DB entry
  read         OK         
  blank-check  BAD        
  write        BAD        
  verify       BAD        
  erase        NA         protocol 0x0D (28C family) has no erase operation; each page ...

  voltage     vpp 11800 -> 11800 mV   vpe 13700 -> 13700 mV
  db_diff     status=supported  ladder=community-fail

  ROUTE: FAIL — datasheet cross-check needed. Failing: blank-check, write, verify
  NA means the step does not apply to this family — never report it as a failure.
```

`#?` stands in for the issue number in `--body-file` mode. `show <n>` prints the real
one. A report that *does* carry firmware identity renders that row as
`firmware    3.0.0b19:leonardo`, with no not-attributable clause —
`fixtures/dev-test-at28c256-populated-identity.md` is that case.

Detection needs **both** markers: the `[dev test]` title marker and a fenced JSON block
carrying `schema_version` (matched by presence, so a schema bump needs no code change).

Every issue body is **community-authored and untrusted**. The parser bounds the body
before parsing, never `eval`s it, never shells out, and passes fixed argv lists to `gh`.
Keep those properties: never interpolate body text into a command.

Verdicts, from the embedded JSON `steps[].verdict`:

| Verdict | Meaning | Route |
|---|---|---|
| `OK` | step passed | — |
| `NA` | step does not apply to this family (e.g. UV-EPROM erase) | not a failure — never report it as one |
| `SKIPPED` | not run | — |
| `marginal` | repeat runs disagreed (title says INCONCLUSIVE) | §5, comment |
| `BAD` | step failed (title says FAIL) | §5, comment |

## 3. Fold issues that describe the same EPROM

**One EPROM, one issue.** Several reports of the same chip must be folded together
before triage reaches any of them — otherwise the same datasheet analysis gets written
three times and the chip's real history is scattered across three threads.

```bash
python3 $S/devtest_issues.py fold          # dry run — always look first
```

Real output (2026-08-31), on the two groups that closed that day:

```
WINBOND/W27C02   (W27E020, w27c020)
  every failure superseded — no canonical needed
    #26   FAIL         f8cb30c62aac  host 3.0.0b15  fw not reported  2026-08-06  failing: blank-check, write   [SUPERSEDED by #51 — CLOSE as fixed:superseded (firmware not comparable on both sides — the close rests on host-version evidence alone)]
    #51   PASS         e62e68e1c93a  host 3.0.0b33  fw 3.0.0b22:leonardo  2026-08-30  failing: -   [PASS — closes via §4 as chip:validated; fold never closes it as a duplicate]
   note: PASS issues above are NOT touched by fold — close each via §4 and log the chip.

WINBOND/W27C512   (W27E512, w27c512)
  every failure superseded — no canonical needed
    #41   FAIL         137e93501512  host 3.0.0b27  fw 3.0.0b20:leonardo  2026-08-22  failing: write, verify, erase, blank-check   [SUPERSEDED by #46 — CLOSE as fixed:superseded]
    #42   PASS         8236361b75a5  host 3.0.0b28  fw 3.0.0b20:leonardo  2026-08-22  failing: -   [PASS — closes via §4 as chip:validated; fold never closes it as a duplicate]
    #46   PASS         2f4fb4f62ff3  host 3.0.0b33  fw 3.0.0b22:leonardo  2026-08-30  failing: -   [PASS — closes via §4 as chip:validated; fold never closes it as a duplicate]
   note: PASS issues above are NOT touched by fold — close each via §4 and log the chip.

DRY RUN — 2 group(s); 2 failure(s) would close as superseded. Re-run with --apply to comment, label and close.
```

Grouping is **alias-aware**: `fold` resolves chip names through `chip_database.json`,
parsed only as data, so `w27c020` and `w27e020` land in one group as `WINBOND/W27C02`.
Granularity is the database entry, which means `M27C512` (SGS-Thomson) and `27C512`
(Intel) stay apart — different parts, and the two "512"s in particular are genuinely
different devices. With the database unreadable it falls back to name matching and
says so on stderr.

| Rule | Why |
|---|---|
| A failure a later PASS **supersedes** is CLOSED, referencing that PASS | The defect is gone. Keeping it open buries live work under noise. See §3a for the three tests that must all hold |
| A PASS that does NOT supersede is **evidence only** | The chip working once on the same build does not undo a FAIL — that is intermittency, which is its own finding. Label `intermittent`, leave open |
| `fold` never closes a PASS issue | A PASS closes via §4 as `chip:validated` and gets logged. Folding it in as a duplicate would bury a clean result |
| Canonical `*` = oldest **actionable** issue that is not superseded | The original live report, and never a PASS — the tracking issue should describe a problem that still exists |
| A group that is **all PASS** is not folded at all | Each closes normally via §4 and the chip gets logged |
| Different fingerprints still fold | Two distinct failures of one EPROM belong in one thread. The consolidated table keeps both reports intact |

### 3a. When does a later PASS supersede a failure?

**All three tests must hold.** Any one failing leaves the issue OPEN — a close is
outward-facing and must never rest on a guess. `supersedes()` in
`scripts/devtest_issues.py` implements exactly this and names the leg that blocked.

| # | Test | Why it is not optional |
|---|---|---|
| 1 | The PASS is later **by the report's own `generated` stamp** | Not by issue number or creation date — an old run can be filed late |
| 2 | The software **moved forward**: PASS host ≥ FAIL host, PASS firmware ≥ FAIL firmware, and at least one strictly greater | A later PASS on the **same** build is flaky, not fixed. On an **older** build it is evidence the failure is version-independent. Both are worse findings than a fix, and both must stay open |
| 3 | Every failing step comes back **`OK`** | **`NA` does not count.** `NA` means the step stopped running, not that it started passing — #48 legitimately reports `blank-check NA`. Closing a `blank-check BAD` against a later `blank-check NA` hides a live defect behind a green title |

When firmware identity is absent on either side (an old report, per §2's
not-attributable rule), test 2 falls back to host-version evidence alone and the close
comment says so. That is a caveat, not a silent assumption.

Show the dry run to the operator before applying — closing issues is outward-facing
and not yours to decide unilaterally. Then:

```bash
python3 $S/devtest_issues.py fold --apply
```

That closes each superseded failure with a comment naming the PASS that answered it
and the three tests it met, labels it `fixed:superseded`, then posts a consolidated
table of the remaining live reports onto the canonical and folds the rest in. Nothing
is lost: every fingerprint, host version, firmware, report date and failing-step list
survives in that table.

Use `--canonical <n>` to override the choice when a later issue is plainly the better
tracking thread.

After folding, triage the canonical issue only.

### 3b. Labels

`python3 $S/devtest_issues.py labels` creates the taxonomy idempotently — do this once
per tracker, since a fresh clone has only GitHub's stock labels. `fold --apply` applies
the mechanical ones itself. The taxonomy is shared with `devtest-rootcause`, which owns
the `fix:*` pair.

| Label | Meaning | Applied by |
|---|---|---|
| `dev-test` | A community `dev test` report | `fold --apply`, and by hand on any issue you triage |
| `chip:validated` | Every applicable step passed. Chip is in the ledger | you, at §4 |
| `fixed:superseded` | Closed against a qualifying later PASS | `fold --apply` |
| `intermittent` | A later PASS exists but the software did not move | `fold --apply` |
| `needs:report` | Waiting on a fresh run from the reporter | you |
| `fix:committed` | A fix exists in a branch or PR. No release carries it yet | `devtest-rootcause` |
| `fix:released` | A released version carries the fix. Re-test to close | `devtest-rootcause` |
| `cause:harness` | Defect in the `dev test` harness itself | you, after §5 |
| `cause:firmware` | Defect in the Arduino firmware | you, after §5 |
| `cause:database` | Wrong field in the generated chip database | you, after §5 |
| `cause:rig` | Operator wiring, socket or voltage — not a software defect | you, after §5 |

The `cause:*` label is the single most useful thing triage produces for the backlog: it
says **who owns the fix** before anyone opens the thread. It encodes a judgement no
parser can derive, so it is never applied mechanically — only after §5's datasheet work
or a root-cause. More than one may apply. Apply every one you can defend.

A PASS issue gets `dev-test` + `chip:validated` and nothing more. Do **not** label by
chip name — the database has 746 rows, and the chip is already in the title.

## 4. PASS → close the issue and log the chip

Only when **every** step is `OK`/`NA`/`SKIPPED`.

```bash
cd $APP && firestarter info w27e020 | head -12     # capture protocol + pinout for the row
gh issue close 51 --repo henols/firestarter \
  --comment "Validated: all applicable steps OK/NA on host 3.0.0b33, firmware 3.0.0b22. Thanks for running the sweep."
gh issue edit 51 --repo henols/firestarter --add-label dev-test,chip:validated
```

**Name what passed, not where you logged it.** The close comment names the
chip's host and firmware and stops there. Do not cite `VALIDATED-EPROMS.md` or any
other repo path — the ledger lives in a repo the reporter does not have, so the
reference is noise to the only person who sees the comment. The `chip:validated` label
already shows you logged the chip.

Then record the chip. **The ledger is generated — never edit it by hand.**
`eprom_ledger.py` owns its format, so every write produces the same shape:

```bash
S=$ROOT/.claude/skills/devtest-triage/scripts
python3 $S/eprom_ledger.py add --chip W29C040 --host 3.0.0b33 \
    --firmware 3.0.0b22 --issues '#48' --date 2026-08-31
python3 $S/eprom_ledger.py check     # exit 1 if the file differs from a fresh render
```

Take `--host` from the report's `auto_capture.host_version` and `--firmware` from
`auto_capture.fw_board_identity`, not from the issue text. Omit `--firmware` when the
report carried none — it then records `not reported`, and the host version is never
used to infer it. Pass every closing issue in `--issues` for a chip that passed more
than once. `add` refuses a chip the database does not know, and refuses to overwrite an
existing row without `--force`.

Everything else in the file is derived from that row plus `chip_database.json`: the
vendor, size, VCC and chip ID, the alternative part numbers sharing its database entry,
and the family tables. The script recomputes all of it on every write.

### Reading the ledger

A **family** is every part sharing `programming.algorithm`, `pinout` and
`electrical.vpp_mv` — the three fields that decide the programming path, the socket
wiring and the rail.

A logged member is evidence for its untested siblings, **never proof**. The key fixes
the path, the wiring and the rail. It does not fix size, page size or chip ID, and those
are what a sibling fails on:

| Sibling differs in | Consequence |
|---|---|
| Size | It drives address lines the logged part never drove. On 32-pin parts, suspect the JP4 and JP5 straps before the protocol |
| Page size, on `PROTO_FLASH_5V_PAGE` | That protocol reads the part's real page size when it writes, so the write is one no logged row covers |
| Chip ID | It fails at the `id` step whatever the family says. No family shares identity bytes |

The Family variation table in the ledger records how much each family varies.

Two columns carry a sentinel rather than a value:

| Reads | Means |
|---|---|
| `Chip ID` = `none` | The part reports no identity, so `id` is `NA` — not a failure |
| `Firmware` = `not reported` | The run cannot be attributed to a firmware version. Do not infer one from the host version |

The ledger's `## Notes` section is for facts about specific rows that no column can
carry. General rules for reading it belong here, not there. The script preserves Notes
verbatim across a rewrite.

## 5. FAIL or marginal → datasheet analysis, then comment

### 5a. Get the datasheet

Datasheets are cached, tracked, and flat-named by part number in `$APP/datasheets/`:

```bash
ls $APP/datasheets/
# AT28C256.pdf  M27C1001.pdf  M27C512.pdf  SST39SF0x0A.pdf
# W27C020.pdf   W27C512.pdf   W27E257.pdf
```

Reuse the cached copy when present. Otherwise get it from the **manufacturer** (avoid
aggregator sites — they serve HTML interstitials, not PDFs) and check that it really is a PDF:

```bash
curl -sL -o $APP/datasheets/AT28C256.pdf \
  "https://ww1.microchip.com/downloads/en/devicedoc/doc0006.pdf"
file $APP/datasheets/AT28C256.pdf     # => PDF document, version 1.6, 30 page(s)
```

If `file` does not say `PDF document`, the download failed — discard it and find another URL.
Use WebSearch for `"<part>" datasheet filetype:pdf` when no manufacturer URL is known.

### 5b. Inspect it

Text first, to find the page numbers, then inspect the page as an image — **pin diagrams
are graphics and do not survive text extraction**:

```bash
pdftotext -f 1 -l 6 $APP/datasheets/AT28C256.pdf - | grep -n "Pin Config\|DIP\|Absolute Max"
```

Then use the Read tool on the PDF with `pages: "2"` for the pin-configuration page.
`pdftotext`/`pdftoppm` come from `poppler-utils`. Install with
`sudo apt-get install -y poppler-utils` if missing. Fallback with no poppler:
`python3 -c "from pypdf import PdfReader; print(PdfReader('f.pdf').pages[1].extract_text())"`
(text only — it cannot show you the diagram).

### 5c. Cross-check the datasheet against what firestarter believes

```bash
cd $APP && firestarter info -a at28c256
```

Compare every row. This is the checklist the comment must cover:

| Check | Datasheet source | firestarter source | Failure means |
|---|---|---|---|
| **Pin map** — every DIP pin, both columns | Pin Configurations, the **DIP/PDIP** view (never TSOP/PLCC/SOIC) | the ASCII package diagram in `firestarter info` | wrong `pinout` key → address/data lines crossed |
| **Pin count / size** | ordering info, organisation (e.g. 32,768 × 8) | `Number of pins`, `Memory size` | wrong device family selected |
| **VPP / program voltage** | programming section, absolute-max ratings | `VPP:` | over-voltage risk, or a program that never takes |
| **VCC** | operating range (e.g. 5V ±10%) | `VCC:` | marginal/erratic writes |
| **Erase** | "electrically erasable" vs UV window | `Can be erased:` | `erase` reported NA/BAD wrongly |
| **Chip ID** | device-identification / signature-byte section | `Chip ID:` | `id` step NA or mismatching |
| **Program algorithm** | programming waveform: page-write, DQ7 polling, unlock sequence, single-pulse | `Protocol:` line | the whole write path is wrong for the part |
| **Page size** | page-write buffer size (e.g. 64-byte page) | `infoic_page_size_raw` in the DB entry | partial/corrupt page writes |
| **Write protection** | SDP / hardware data protection section | `Flags:` | a locked chip that silently refuses writes |
| **Pulse timing** | write cycle / program pulse time | `pulse_duration` | under- or over-programming |

State which of these you actually checked. A check you could not perform (datasheet
section absent) is reported as *unchecked*, never as passing.

Voltage sanity from the report itself — `voltage.vpp_before_mv` / `vpp_after_mv` /
`vpe_before_mv` / `vpe_after_mv` against the datasheet rating — is worth one line when it
is out of spec. These four are REGULATOR RAIL readings, never socket readings: a rig
whose EPROM socket is unhooked entirely still measures a healthy rail, and a healthy rail
proves nothing about contact — the report says so itself, in its own
`rail_reading_disclosure` field, which is worth quoting in the comment when you cite a
voltage row. As of schema 2.0 the report no longer carries the two standalone
`voltage.vpp_mv` / `vpe_mv` keys these four before/after fields replaced. A body still
carrying them is a pre-2.0 report. This skill's own two frozen fixtures under
`fixtures/` (`dev-test-at28c256-null-identity.md`, `dev-test-at28c256-populated-identity.md`)
are deliberately such pre-2.0 bodies — their own headers forbid regenerating them from a
live `to_dict()` output, and that stays true here.

### 5d. Post the comment

Save the body to a file and pass `--body-file`. Never interpolate report text into
the command line.

```bash
gh issue comment 21 --repo henols/firestarter --body-file /tmp/comment.md
```

Template:

```markdown
### Datasheet cross-check — AT28C256

Datasheet: Atmel/Microchip AT28C256, doc0006 rev 0006M-12/09 (`datasheets/AT28C256.pdf`)
Failing steps: blank-check BAD, write BAD, verify BAD

| Check | Datasheet | Database | Verdict |
|---|---|---|---|
| Pin map (28-DIP) | §2.4 pins 1–28 | `DIP28_28C256` | MATCH — all 28 pins agree |
| Size | 32,768 × 8 | `0x8000` | MATCH |
| Erase | electrically erasable; page write auto-erases | `yes` | MATCH |
| Algorithm | page write, DQ7 polling, SDP | `0x0D` (5V parallel, SDP + DQ7 poll) | MATCH |
| Page size | 64-byte page (§1) | `infoic_page_size_raw: 64` | MATCH |
| Write protect | software data protection | `protect_off_before`/`protect_on_after: true` | MATCH — represented |
| VCC | 5V ±10% (4.5–5.5V) | `vcc_mv: 5000` | MATCH |
| VPP | none; single 5V supply | `12V` | MATCH in effect — protocol `0x0D` never routes VPP |

**Not a pin-map fault, and not a missing-SDP-config fault.** The wiring is right and
the database already asks for SDP disable-before / enable-after, so the failure is in
how that sequence is *executed*, not in the data describing it.

Most likely cause: <the one you actually believe, and why>.

Unchecked: <anything the datasheet did not let you confirm>.
```

An all-MATCH table like that one is a real result, not a wasted pass: it says the data
describing the part is right and moves the fault into execution. A row that does
*not* match names the field and both values, e.g. from W27E257 (#23):

```markdown
| VPP (program) | 12V program; 14V is the ERASE voltage only | `vpp_mv: 13500` | MISMATCH — neither the program nor the erase voltage |
```

Lead with the checks that **matched** as well as the ones that did not — ruling the
pin map out is the single most useful thing this analysis produces. Then apply the
`cause:*` label your analysis earned (§3b).

**Do not close a FAIL issue on the strength of your own analysis.** Naming the cause is
not fixing it. A failure closes on exactly two grounds: a later PASS that passes all
three tests in §3a, or a fold into another live issue. Everything else stays open —
including a failure you have root-caused completely, which stays open until a build
carrying the fix is re-tested.

## Worked example — issue #21, at28c256

`firestarter info at28c256` prints pin 1 `A14`, 2 `A12`, 3 `A7` … 14 `GND`, 28 `VCC`,
27 `R/W(WE)`, 26 `A13` … 15 `D3`. The datasheet's §2.4 28-lead PDIP view is identical
pin for pin. So the `DIP28_28C256` pinout is right and the FAIL is elsewhere.

Checking the rest of the entry ruled out the next two suspects too: `infoic_page_size_raw`
is `64`, exactly the datasheet's page size, and `protect_off_before`/`protect_on_after`
are both `true`, so SDP handling *is* requested. With the data right, `blank-check BAD`
plus `write BAD` points at the SDP unlock sequence not taking effect on the wire — which
is what open issue #12 ("AT28Cxxx Write Protection Enable/Disable missing") describes.
Cross-link it, and hand it to `devtest-rootcause` as a host/firmware question, not a
database one.

That is the model: compare all pins, then keep going and rule out each remaining field
by its real value. **Inspect the field, do not assume it** — a plausible guess about
`page_size` or whether write protection is represented is wrong often enough to invert
the conclusion.

## Handing off

Comments left here are the input to `devtest-rootcause`, which investigates the code.
Say plainly which issues you commented on,
and which `cause:*` label you put on each — that label is the handoff, because it says
which repo the fix lives in before anyone opens the thread.

Save the cross-check table in the template's exact shape. Whoever picks up the
investigation reads every **MATCH** row as already settled and does not re-check it.
A verdict that is not `MATCH` is left open on purpose. That is the whole payoff of
doing the datasheet work carefully here.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pdftoppm is not installed` from the Read tool | `sudo apt-get install -y poppler-utils` |
| Downloaded "PDF" is 4 KB of HTML | Aggregator interstitial. `file` it, discard, get it from the manufacturer |
| `firestarter: command not found` | `cd $APP && pip install -e .` |
| `firestarter info <chip>` says unknown | Lookup is alias-aware over comma-split `part_number`. Try `firestarter search <partial>` |
| `show` says NOT a parseable dev test issue | Needs **both** the `[dev test]` title marker and a fenced JSON block with `schema_version`. In `--body-file` mode, pass `--title` too |
| `gh: not found` | Install the GitHub CLI. It is the only external binary `list`/`show` need |
| Two issues for one chip, only one triaged | Run `fold` FIRST (§3). Triage per-EPROM, not per-issue |
| `gh: 'label' ... not found` when applying a label | The taxonomy is not created yet — `python3 $S/devtest_issues.py labels` |
| `fold` will not close a failure you think is fixed | Inspect the bracketed reason on its row: one of §3a's three legs blocked. A same-build PASS or an `NA` step is deliberately not grounds to close |
| A closed `fixed:superseded` issue turns out to be live again | Reopen and label `intermittent`. The three legs prove the failure did not reproduce, not that the defect is impossible |
| `fold` says "grouping by chip NAME only" | `chip_database.json` not found — pass `--db` or set `FIRESTARTER_DB`. Alias-different names will not group until then |
| `gh` cannot comment | Token needs `repo` scope. Run `gh auth status` |
| Two issues, same `dedup_fingerprint` | Same failure. Comment once, cross-reference from the other |
