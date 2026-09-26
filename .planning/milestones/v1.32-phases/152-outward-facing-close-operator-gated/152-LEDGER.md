# v1.32 Honesty Ledger — AT28C Write-Path Root Cause & Report Provenance

**Milestone:** v1.32 — AT28C Write-Path Root Cause & Report Provenance. **Phases:** 147 (Report
Provenance), 148 (Numeric DB Values), 149 (Firmware Page-Size Seam), 151 (Protection Readability /
`lock-status`), 153 (Write-Path Erase Policy), 152 (Outward-Facing Close — this phase).
**Repository scope: dual-repo, three firmware-touching workstreams** (149, 151, 153) — `firestarter`
(Arduino/AVR) and `firestarter_app` (Python host CLI) both carry v1.32 code; this phase (`152`) writes
`.planning` record corrections and posts five outward artifacts, and does not modify either sub-repo's
source.

**Every value below was measured live by this plan, `2026-08-21T18:40:57Z` unless a different
timestamp is stated, and never reused from a prior document's citation.** Where a sibling artifact
cited the same fact earlier in this phase, the two readings are compared explicitly below rather than
silently assumed to agree.

**Meta repository (this repo) HEAD, immediately before this plan's own commits:**
`2f194e29d62ebf0ef879e353f78d6afd381a2a9c` — `git -C /workspaces rev-parse HEAD`, measured here.

**Firmware submodule (`firestarter`) HEAD:** `d990a4ce80fcb56c9becf2312d1fe8757e1fc54d` — `git -C
/workspaces/firestarter rev-parse HEAD`, measured here. This is the meta repository's own tracked
gitlink for `firestarter` (`git -C /workspaces ls-tree HEAD firestarter`, checked live) — the two agree
exactly, and both are the merge commit's second parent on `beta`, not `origin/beta` itself (§ "The
gitlink is not re-pinned" below).

**Host submodule (`firestarter_app`) HEAD:** `a0bfd5e8b32989a60fc93b94e7b102506e6cf56f` — `git -C
/workspaces/firestarter_app rev-parse HEAD`, measured here. Also the meta repository's tracked
gitlink for `firestarter_app`, confirmed identical live.

**No divergence found.** Both HEADs above match `152-MERGE-RECORD.md` §5's table exactly, which itself
cites `152-11-SUMMARY.md`'s live measurement. Three independent readings across two plans and this
ledger agree on both SHAs; there is nothing to reconcile.

**Both published-branch SHAs, re-fetched and re-read live here:**

```
$ git -C /workspaces/firestarter fetch origin --quiet && git -C /workspaces/firestarter rev-parse origin/beta
88d204a5a023bcad6f708b33150502ba90fdec2b
$ git -C /workspaces/firestarter_app fetch origin --quiet && git -C /workspaces/firestarter_app rev-parse origin/beta
86f85d77d8102b633da82aef4b5601947f6cc80b
```

Both match `152-MERGE-RECORD.md` §§2-3's own live capture and the two release tags' `targetCommitish`
values below — the same position, read a third time, still the same.

**Both cut tags, re-read live from the release list, never predicted:**

```
$ gh release list --repo henols/firestarter --limit 3
3.0.0b20  Pre-release  3.0.0b20  2026-08-21T17:07:09Z
3.0.0b19  Pre-release  3.0.0b19  2026-08-18T10:00:08Z
3.0.0b18  Pre-release  3.0.0b18  2026-08-07T14:18:19Z

$ gh release list --repo henols/firestarter_app --limit 3
3.0.0b23  Pre-release  3.0.0b23  2026-08-21T17:06:43Z
3.0.0b22  Pre-release  3.0.0b22  2026-08-19T19:40:06Z
3.0.0b21  Pre-release  3.0.0b21  2026-08-18T09:58:57Z
```

Body lengths, re-read live: firmware `3.0.0b20` → **9122** bytes; app `3.0.0b23` → **9261** bytes. Both
non-zero, both agreeing exactly with `152-17-SUMMARY.md` and `152-18-SUMMARY.md`'s own post-publish
reads.

**All three comment ids and URLs, re-read live from the issues themselves, plus each issue's current
state and comment count:**

| Issue | State | Comments | Last comment id | Last comment URL | Last comment timestamp |
|---|---|---|---|---|---|
| gh#12 | OPEN | **11** | `IC_kwDOSX4ER88AAAABQEgwAQ` | https://github.com/henols/firestarter_prom/issues/12#issuecomment-5373440001 | `2026-08-21T18:00:19Z` |
| gh#21 | OPEN | **3** | `IC_kwDOSX4ER88AAAABQEyGMg` | https://github.com/henols/firestarter_prom/issues/21#issuecomment-5373724210 | `2026-08-21T18:27:49Z` |
| gh#11 | OPEN | **19** | `IC_kwDOSX4ER88AAAABQE07QQ` | https://github.com/henols/firestarter_prom/issues/11#issuecomment-5373770561 | `2026-08-21T18:32:30Z` |
| gh#32 | **CLOSED** (`stateReason: COMPLETED`, `closedAt: 2026-08-08T09:31:09Z`) | 1 | — | — | — |

All four rows agree exactly with `152-14-SUMMARY.md`, `152-15-SUMMARY.md` and `152-16-SUMMARY.md`'s own
post-publish reads — no drift since those plans posted. gh#32's closure is measured a second time here,
independently of Task 1 of plan 152-15, and agrees to the second.

**`git status --porcelain`, re-checked live, all three repos:**

```
$ git -C /workspaces/firestarter status --porcelain | grep -v '^??'
(empty)
$ git -C /workspaces/firestarter_app status --porcelain | grep -v '^??'
(empty)
$ git -C /workspaces status --porcelain | grep -v '^??'
 M firestarter_app
```

**The meta repository's line is not the clean result the other two are, and this is reported exactly
as measured rather than forced into "clean".** `git status --porcelain=2 -- firestarter_app` decodes
this as `S..U` — the submodule's tracked SHA is bit-identical to `firestarter_app`'s own HEAD
(`a0bfd5e8b3...` both sides, confirmed above), and the `M` is the parent repository's own convention
for reporting an **untracked-content** submodule, not a moved gitlink. The untracked content itself is
the same pre-existing set `152-11-SUMMARY.md` already recorded and none of this phase's plans has
touched: `.planning/config.json`, `SECURITY.md`, four datasheet PDFs, and `write_test_port.sh`. No
gitlink SHA differs from HEAD in either sub-repo.

---

## Status / claim key

Reused from `122-LEDGER.md` / `137-LEDGER.md` / `146-LEDGER.md`, unchanged:

- **`PERMITTED`** — a wording backed by a measured, re-runnable software artifact (a test, a source
  scan, a size report, a live re-derivation) or a stated, scoped exploratory read.
- **`CONTEXT-ONLY`** — measured and cited for context, but explicitly not a gate.
- **`FORBIDDEN`** — the ceiling's forbidden claim shape. Appears in this ledger only as a citation of
  what is *not* claimed, never as prose asserting it.

---

## Oracle — every gate and suite named with its own count, re-run live this plan

1. **This phase's own claim gate**, `152-check-claims.py`, invoked with no argv and no env seam against
   its (pre-extension) seven-entry `_DEFAULT_TARGETS`:
   ```
   PASS: scanned 152-CLAIM-CLASSES.md, 152-GH12-COMMENT.md, 152-GH21-COMMENT.md, 152-GH11-COMMENT.md,
   152-RELEASE-NOTES-app.md, 152-RELEASE-NOTES-fw.md, 152-MERGE-RECORD.md; 6 of 6 caveat-required
   file(s) carry every caveat their own rule demands; 1 file(s) carry no caveat requirement
   ```
   **rc=0.** This document is not yet in the scanned set at this read — that extension is this plan's
   own Task 3, demonstrated separately below.
2. **Its paired suite**, `test_check_claims_152.py`: **34 passed**, re-run live
   (`python3 -m pytest test_check_claims_152.py -q -o addopts=""`). Zero skipped, zero failed.
3. **The fail-closed configuration guard**, `152-check-not-auto.py`, run against the live repository
   configuration:
   ```
   PASS: 'workflow._auto_chain_active' is explicitly False in '/workspaces/.planning/config.json' --
   no auto/chained run is active according to this read
   ```
   **rc=0.** Live key value: `False`.
4. **The Phase 130 record-corrections gate**, `check_record_corrections.py`, run with a 300-second
   timeout ceiling per this milestone's own standing note about `STATE.md`'s long single line:
   ```
   PASS: scanned .planning/PROJECT.md, .planning/STATE.md, .planning/ROADMAP.md,
   .planning/milestones/v1.23-REQUIREMENTS.md, .planning/notes/py32f071-port-branch-state.md; exempt
   hits by verdict: {'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10,
   'superseded': 12}
   ```
   **rc=0.**
5. **The firmware source-scan gate guarding this milestone's erase work**, `check_erase_no_vpp.py`:
   ```
   PASS: eeprom28c_erase_execute() in /workspaces/firestarter/src/proms/eeprom_28c.cpp (lines 545-560,
   16 lines scanned) contains no VPP/VPE control-register, chip-enable/disable, or
   bus-config-bypassing hazard token
   ```
   **rc=0.** This is the real hazard control for the software six-byte erase path this milestone
   shipped — not `firestarter_app/tools/check_dispatch.py`'s GATE-03, whose stated mechanism was
   corrected rather than satisfied by this milestone's own record (see Negative space, item 5, below).

**Scanner-status summary:** five gates and suites, all re-run live this plan, all green. None of these
runs is a wording review, and none of them is asserted to be one.

---

## The evidence ceiling, restated because it is binding

Quoted verbatim from `.planning/PROJECT.md` §"Current Milestone: v1.32" → "Evidence ceiling — binding,
not decorative" (`:139-150`):

> **There is still no AT28C part in operator inventory** (recorded 2026-08-04, re-confirmed at this
> milestone's kickoff). This caps what v1.32 may claim, in the same shape as v1.22 and v1.30:
>
> - `0x0D` stays **`UNVERIFIED`** in `PROTOCOL-LEDGER`. No phase may graduate it.
> - gh#21, gh#32, gh#11 and gh#12 stay **OPEN**. A code fix is not a validation; only a fresh passing
>   `dev test` on real silicon closes them, and only `devtest-triage` closes them.
> - The honest outward-facing outcome is a corrected code path plus a request to the reporter for a
>   fresh run — now answerable, because workstream 1 makes that run self-identifying.
> - The firmware page-size change (workstream 3) cannot be validated without a part. It ships
>   software-proven and says so.

This ceiling is the frame every row of the claim table below sits inside. It is stated here, once, as
binding — this ledger does not discharge it, and no phase of v1.32 has attempted to.

---

## The four-column claim table

Header reproduced verbatim from `146-LEDGER.md`/`137-LEDGER.md`. **Every row's fourth cell is
non-empty** — that cell is the explicit non-claim, and a row without one would not satisfy the
requirement. **Row count: 7.**

| Class | Permitted wording | Evidence (measured, source) | Explicitly does NOT prove |
|---|---|---|---|
| **1. Write-path blank-check removal** `PERMITTED` | On the two auto-erasing protocols (algorithm 13, the 28C family, and algorithm 5, flash4), `write` performs no pre-write blank check. This is a change to shipped, user-visible command behaviour, exempt from the pairing clause under D-11. | Live read this plan: `eeprom28c_write_init()` in `firestarter/src/proms/eeprom_28c.cpp` carries no `mem_util_blank_check` call and no `FLAG_SKIP_BLANK_CHECK` conditional in the write path (the flag is now UNREAD there, per the source's own D-07/ERASE-01 comment block at line ~648); `blank` remains reachable through the untouched `CMD_BLANK_CHECK` arm. `153-RECORD.md` (cited, not re-derived). | That this was validated on any physical AT28C or flash4 part — nothing in this milestone put one on a bench. That the removal was tested against any real erase-timing edge case; the read-back verify path this change relies on is a separate, previously-shipped mechanism. |
| **2. Standalone erase step, software six-byte path, with its timing constant** `PERMITTED` | `erase` is now a reachable top-level command for the 28C family, implemented as the software six-byte SDP-unlock-then-erase sequence (Atmel AN 0544B), never the datasheet's 12 V-on-OE hardware path. It waits `AT28C_TEC_MAX_MS` (20 ms) after the erase sequence. | Live read this plan: `CMD_ERASE` is armed in `configure_eeprom28c`'s dispatch (`eeprom_28c.cpp:250-251`) to `eeprom28c_erase_execute`, which contains `#define AT28C_TEC_MAX_MS 20` (line 77) and a `delay(AT28C_TEC_MAX_MS)` call (line 559); `check_erase_no_vpp.py` confirms no VPP/VPE hazard token in that function, re-run green above. `cli_handlers.py:905` registers a top-level `erase` command. | That 20 ms is sufficient for every part sharing algorithm 13 — it is an Atmel-family maximum (AN 0544B) applied to a bucket spanning other vendors; a part with a longer real erase cycle would read non-blank after a successful-looking erase and nothing in the native suite would catch it. That the wall-clock wait is honoured under real timing — the native test harness never stubs `delay()` and records no elapsed time, so this is structural, not temporal, proof. |
| **3. Protection-read command (`lock-status`), refusal-first** `PERMITTED` | `firestarter dev lock-status <chip>` either reports a real state read from silicon or refuses with a named, actionable class token — on the 28C/SDP family the honest answer is usually the refusal, not a report. Requires beta plus `firestarter fw --install` against matching firmware. | Live read this plan: `cli_handlers.py:1788` registers `@dev.command(name="lock-status")`; `152-CLASS-SIZES.md`'s live re-derivation through the actual production code path (`firestarter.protection_readability.protection_gate_for_entry`, as `get_eprom()` actually invokes it) measures **665 of 746** database rows resolve to a refusal class and **81** are `read_permitted`, with zero classification errors. One exploratory bench probe was taken this milestone (151-BENCH.md Leg B): the physically-seated part was a **W29C020**, class token `unadjudicated_probe`, `--force`-gated, explicitly not a state claim (D-07). | That this reads any state at all on the AT28C/`0x0D` family — it is documented-not-readable there by design, and the one bench probe taken was against a **different** algorithm-5 part, not AT28C. That the 665/81 split is method-invariant — `152-CLASS-SIZES.md`'s own two-method re-derivation found a ±1 swing (Method A 664/82 vs Method B 665/81); 665/81 is what the shipped classifier, as the CLI actually invokes it, produces today, not a claim that any conceivable counting method agrees. |
| **4. Report-provenance fix** `PERMITTED` | A `dev test` report now names the firmware it ran against, replacing a hardcoded `None`, on the published branch. | Live read this plan: `git -C /workspaces/firestarter_app show origin/beta:firestarter/cli_handlers.py \| grep -n fw_board_identity` → line 2661, `fw_board_identity=identity.fw_board_identity` — a real assignment, not a literal `None`, on `origin/beta` as published. | That any report filed **before** this fix carries firmware attribution — every `dev test` report filed before this milestone, including gh#21's and gh#32's, still carries `fw_board_identity: null` and cannot be retroactively attributed. |
| **5. Numeric database values** `PERMITTED` | `chip_database.json` states voltages and timing as integers in one unit each (`vcc_mv`, `vdd_mv`, `vpp_mv`, `pulse_duration_us`), including the AT28C256 VCC margin-rail correction (4000→5000 mV, 56 chips, zero decreases). | Live read this plan: `git -C /workspaces/firestarter_app show origin/beta:firestarter/database.py \| grep -c vcc_mv` → 2, present on the published branch. Live re-measurement of the shipped database itself this plan: 746 total rows, **84** carry `programming.algorithm == 13`, **27** carry `programming.algorithm == 5`, and every one of those 27 carries `protect_on_after: true` (27-of-27, cross-checked live). | That any of these values were confirmed against a primary datasheet beyond the decode already performed in Phase 148 and cross-checked against `infoic.xml` — this is a representation fix, not a re-derivation of every chip's electrical parameters from an original source. |
| **6. Page-size seam, and its explicit no-behaviour-change consequence for AT28C256** `PERMITTED`, with a load-bearing non-claim | The firmware now receives `infoic_page_size_raw` through the wire rather than a hardcoded constant. For the AT28C256 part named in the community threads specifically, this changes nothing observable: its own page size, 64 bytes, is exactly the pre-existing floor. | `149-PAGE-SIZE.md` (cited, not re-derived — Phase 149 is not this phase's work to re-verify); live re-confirmation this plan of the chip database figure via the same query used for row 5 above (`infoic_page_size_raw` present per the row 5 measurement's own dataset). | That this seam explains, resolves, or is even relevant to any of the failures reported on gh#20, gh#21, gh#32 or gh#11 — the AT28C256 part's own behaviour under this change is, by the seam's own no-op consequence for a 64-byte-floor part, unchanged. |
| **7. The deferred deliberate-protection command's withdrawal** `PERMITTED`, with a load-bearing non-claim | The disable half of the pre-v1.30 deliberate-protection surface survives as `write`'s automatic, default-on auto-unlock, declinable via a skip flag. The enable half returns as nothing in this release — withdrawn since v1.30, still tracked as Backlog **999.28**, with no version promised for its return. | Live read this plan: the command exists in the firmware image (the six-byte sequence used by `erase` is the same primitive an enable-side command would need) but no host CLI surface reaches it as a standalone enable operation in this release — confirmed by the absence of any registered Click command matching that shape in `cli_handlers.py` beyond `erase` and `dev lock-status`. | That there is any supported way, in this release, to deliberately re-protect a part after a write. There is not. The ask on gh#12 is half-answered for a second release running, and this ledger states that plainly rather than as a queued gain. |

---

## The amendment register

One entry per amendment this phase landed, per D-12's decision that this ledger carries the register
half of the correction mechanism (the labelled correction blocks in place, at each cited site, are the
other half). Every pre-amendment phrasing that would itself trip this phase's own claim gate is cited
by file and location, never reproduced.

1. **The criterion-2 amendment (D-05).** `ROADMAP.md` §"Phase 152" criterion 2, dated marker
   `AMENDED 2026-08-21 (152-CONTEXT.md D-05)`. Pre-amendment text: "gh#21, #32, #11 and #12 are all
   still OPEN" — false when written, since gh#32 was CLOSED 2026-08-08, ten days before v1.32 opened.
   Corrected to name gh#32 as folded rather than open. Authorised by: **D-05**. Landed by: plan
   152-03.

2. **The criterion-5 narrowing (D-11).** `ROADMAP.md` §"Phase 152" criterion 5, dated marker
   `AMENDED 2026-08-21 (152-CONTEXT.md D-11)`. Pre-amendment text paired *every* permitted `0x0D` claim
   with an explicit non-claim, with no scope limit. Narrowed to claims about `0x0D` write-path
   correctness or validation status only, with statements of shipped, user-visible command behaviour
   explicitly exempt. The five forbidden claim classes are untouched by this narrowing. Authorised by:
   **D-11**. Landed by: plan 152-03.

3. **The requirements-document amendments.** `REQUIREMENTS.md` §"Outward-Facing Close (OUT)", four
   bullets, each carrying its own dated marker: OUT-01 (`AMENDED 2026-08-21`, D-05; pre-amendment text
   retained in place as the negative case, at the location the file itself names), OUT-02
   (`AMENDED 2026-08-21`, D-05, 152-RESEARCH.md §B-8), OUT-04 (`AMENDED 2026-08-21`, D-05; pre-amendment
   text retained in place as the negative case, at the location the file itself names), OUT-05
   (`AMENDED 2026-08-21`, D-11). Each bullet's own in-place marker states the decision id and, where the
   pre-amendment wording would itself be a forbidden phrasing, retains it only as the labelled negative
   case a gate test must be seen to reject. Authorised by: **D-05, D-11**. Landed by: plan 152-04.

4. **The stale record sites (D-15).** Two distinct sites, both dated `2026-08-21`: `PROJECT.md`
   §"Current Milestone: v1.32" (`:44-50`) — the "one firmware-touching workstream" claim corrected to
   three, with an inline history note naming 152-CONTEXT.md D-15; and `ROADMAP.md` §"Phase 152"'s own
   summary bullet (`:37`) — the same workstream-count claim, corrected the same way, plus a second,
   separate stale-fraction removal (a requirement-count fraction that predated Phase 153, removed so
   `REQUIREMENTS.md`'s Coverage block stays the single copy of that count). Authorised by: **D-15**.
   Landed by: plan 152-03 (this phase's own record-correction wave) and Phase 153 itself (the PROJECT.md
   workstream-table row and workstream-4 description, confirmed already present before this phase wrote
   to the same file — 152-RESEARCH.md §B-11).

5. **The disproven-premise correction (D-06 / D-15).** `PROJECT.md` (`:1360`), a labelled
   `⚠ CORRECTION (Phase 152 / 152-CONTEXT.md D-06 + D-15 — 2026-08-21)` block. States that Phase 121
   D-12's premise — that advertising an erase capability for the algorithm-13 bucket was a false
   capability statement — is disproven: the capability is real in the silicon (Microchip DS20006386B
   Table 6-1, p.11) and real in `infoic.xml` (the erasable flag bit is set); what was false was only
   that firestarter itself could not perform it, not that the part could not be erased. States plainly
   that the code-comment half of this correction was discharged by Phase 153 (ERASE-07), and that this
   block is the `.planning`-side half only. Authorised by: **D-06, D-15**. Landed by: plan 152-03.

---

## Negative space — every carry-forward

1. **Backlog 999.28** (the deferred deliberate-protection command) **stays open, deferred a second
   time.** `ROADMAP.md` §"Phase 150" and §"Phase 999.28" (cited, not re-derived). The standing
   instruction survives unchanged: a future promotion **must reverse OUT-05's fifth gate class in the
   same change that lands the feature**, or the gate rejects the very release notes announcing it.

2. **Backlog 999.29** (the AT28C256 write-path failure itself, gh#20's paste) **stays open, partially
   addressed, not retired.** `ROADMAP.md` §"Phase 999.29" (cited). v1.32 removed the blocker to
   diagnosing it and answered it publicly; under the evidence ceiling above, it did not diagnose it.
   The operator remains its named owner.

3. **The split-firmware constraint is unaddressed and is not on any roadmap.** No shield revision this
   project has built carries a path to relieve the leonardo Caterina-bootloader ceiling. Re-measured
   live this plan against the committed baselines (the same query used for claim-table row 2's
   corroboration): `size_baseline.json` gives leonardo `flash_used` **27630**, `flash_total` **32768**;
   `size_baseline_v131.json` gives `flash_used` **26906**, `flash_total` **28672** (the Caterina
   USB-bootloader boundary). `27630 - 28672 = -1042`, i.e. **1042 B of headroom remains below that
   boundary**, and the boundary itself is **UNGUARDED** — `board_upload.maximum_size` does not enforce
   it, so nothing in the build stops a future change from silently overwriting the USB bootloader
   region. A dedicated split-or-trimmed-build phase was raised and deliberately deferred; it is not
   this milestone's work.

4. **The protection-class counting method's ambiguity, and which figure is publishable.**
   `152-CLASS-SIZES.md` (cited, not re-derived) found the two candidate counting methods do not agree
   exactly — refusal totals 664 (Method A, a synthetic counterfactual no real CLI invocation can reach)
   versus 665 (Method B, the live production code path) — and that Phase 151's own published figures,
   406/111/39, **do not reproduce under either method**. The only figures this ledger, or any outward
   artifact, may cite are **665 of 746 rows resolve to a refusal class; 81 are `read_permitted`**
   (Method B), and the two method-invariant class counts `no_mechanism` = 405 and `not_implemented` =
   40. This item is not fully settled — it is stated, with its own resolution rule, rather than
   resolved into a single number that erases the disagreement.

5. **The requirements-count reconciliation.** `REQUIREMENTS.md`'s own footer (cited): 33 total minus 7
   deferred (the RELOCK family) equals 26, plus the 9 write-path erase requirements Phase 153 added
   mid-milestone equals **35 in scope, 42 defined**. This reconciliation is recorded once, in
   `REQUIREMENTS.md`'s Coverage block, per amendment-register entry 4 above — this ledger cites the
   number rather than restating a second copy of it.

6. **`firestarter_app/tools/check_dispatch.py` (GATE-03) is not this milestone's erase hazard
   control.** An earlier plan's own stated criterion named it as such; that claim was corrected, not
   satisfied, by this milestone's actual work — the real control guarding the software six-byte erase
   path is `firestarter/scripts/check_erase_no_vpp.py`, re-run green in the Oracle section above.
   GATE-03 continues to guard the unrelated 12 V-dispatch hazard it was built for and was not touched by
   this milestone.

---

## Process failures recorded here, not only technical ones

A ledger that admits only code defects is not an honesty ledger. At minimum, five process failures this
milestone's own record — and this phase's own execution — keeps visible:

1. **Two prior release-notes artifact sets were authored and never posted.** Phase 137 authored
   `137-RELEASE-NOTES-app.md` for a v1.30 cut and Phase 146 authored `146-RELEASE-NOTES-app.md` /
   `-fw.md` for a v1.31 cut; neither was ever published (`146-LEDGER.md`, cited). This is exactly why
   this phase's own boundary put publishing inside the phase rather than deferring it to a future one
   (D-01/D-04), and why the two bodies published this phase carry non-zero body length, re-confirmed
   live in the Header section above.

2. **A published release body announced a deleted command for weeks.** The app's `3.0.0b14` notes
   (2026-07-30, body length 4490, re-confirmed unchanged this milestone) publicly state that a
   standalone deliberate-protection command "gives standalone control in both directions" — the command
   was removed 2026-08-05. The correction lands in the newly-published notes (`3.0.0b23`'s "Removed"
   section), per D-02's rule that historical bodies are corrected in the next notes, never rewritten in
   place. `3.0.0b14`'s body length is confirmed unchanged by that correction.

3. **Class-size figures published by a prior phase did not reproduce.** Phase 151's own D-06/D-09
   figures (406/111/39) do not reproduce under either counting method `152-CLASS-SIZES.md` measured
   this phase — see Negative space item 4. This is recorded here as a process failure, not merely a
   number correction, because it was a **published** figure this milestone's own outward text had to
   route around rather than repeat.

4. **An attribution error about named third parties was caught before publication, by a human
   escalation, not by any gate.** `152-GH11-COMMENT.md`'s frozen draft claimed one community reporter
   was the only person who had ever run any part of this milestone's subject matter against real
   silicon; a second reporter, tagged two paragraphs earlier in the same draft, had filed his own report
   under his own account. The claim gate passed the draft cleanly both before and after the fix — it is
   not a forbidden phrase, a missing caveat, or an unqualified claim word. The operator, escalated to
   specifically on this one question, resolved it: credit both reporters by name (`152-16-SUMMARY.md`,
   cited).

5. **A misattribution of a physical part reached a published body, and was corrected there after
   publication.** The app release body (`3.0.0b23`) was published stating that this milestone's one
   exploratory `lock-status` bench probe was run "against a
   W29C040." Re-measured live against the primary bench record, `151-BENCH.md`: the physically-seated
   part for that probe (Leg B) was a **W29C020** — `151-BENCH.md`'s own text records the operator
   stating no W29C040 sample was available, that Leg C (the true W29C040 probe) **did not run**, and
   explicitly warns against reporting a W29C020 reading under the W29C040 name because doing so "would
   have produced a reading from the wrong physical part and misattributed it." That warning was written
   during Phase 151 and was not heeded by the time this phase's own release-note draft, `152-08`, named
   the part — the mislabel traces back through `152-RESEARCH.md` to `152-CONTEXT.md`'s own
   canonical-references section, which cites "the W29C040 probe result" for the same Leg B data. This
   passed the claim gate (a part-number identity error is not a forbidden phrase), passed the D-03
   wording-review delegation (the operator did not read the body — item 6 below), and is now published.
   **This ledger's non-claim that the probe was "not even from the family under discussion" remains
   true regardless of which algorithm-5 part it names** — W29C020 and W29C040 are both outside the
   AT28C / `0x0D` family this milestone is about — so no claim about the write path is affected. The
   **RESOLVED 2026-08-21, after this ledger entry was first written.** The error was escalated to the
   operator, who ruled that it be corrected with a visible errata line rather than silently or not at
   all. `3.0.0b23`'s body now reads `W29C020` and carries a dated errata paragraph stating what it
   originally said, that no `W29C040` was available or ever seated, and that the misattribution came
   from this milestone's planning record rather than the bench log. Verified on the published body:
   the phrase "against a W29C040 on the bench" occurs 0 times, "against a W29C020 on the bench" once,
   and the two surviving `W29C040` mentions are both inside the errata paragraph. Body length 9261 →
   9707; prerelease flag and target commit unchanged.

   Two things this entry deliberately does **not** claim. First, the correction does not undo the
   process failure: a false statement about which physical part was on the bench was published, and
   was caught only during this ledger's own live evidence capture, four artifacts after the draft that
   introduced it. Second, **the upstream source is still wrong** — `152-CONTEXT.md` continues to cite
   "the W29C040 run" and "the W29C040 probe result", and the operator chose the errata-only option over
   also amending it, so any future phase citing that CONTEXT will inherit the same error unless it
   checks `151-BENCH.md` directly. `151-BENCH.md` is the primary record and it was right throughout.

6. **D-03's per-artifact blocking operator wording review was delegated, not performed, across all five
   outward artifacts.** The operator authorised the full posting sequence, granted the necessary `gh`
   permissions, and stated "you can do the work" and "I delegate everything to you." Across all five
   published artifacts, **the operator read none of the five bodies** and answered exactly **one**
   substantive question — the attribution question in process failure 4 above. Every wording review
   this phase performed was agent-performed, not operator-performed, and this ledger states that
   plainly rather than letting a green claim-gate run stand in for it. The gate's own PASS line
   disclaims discharging D-03, and this ledger repeats that disclaimer rather than softening it.

---

## What no test, gate or review can close

At minimum:

- **The evidence ceiling itself.** No AT28C part has ever been in operator inventory this milestone.
  No test in this or any future milestone answers `0x0D`'s validation status without a physical part on
  a bench.
- **The protocol ledger's status.** `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER at this milestone's
  close, exactly as it stood at its open. Nothing in this phase's own work moves it.
- **The `t_EC` wall-clock wait.** No native test can prove the 20 ms erase-completion wait is honoured
  under real timing — the native test harness never stubs `delay()` and records no elapsed time, so the
  proof available is structural (the call is present in the source) and never temporal.
- **The gh#20/gh#21/gh#32 write-path failure's root cause.** This milestone removed the instrumentation
  defect that made attribution impossible and answered the three community threads publicly; it did
  not diagnose the underlying failure on real silicon, and could not, under the evidence ceiling.
- **The already-published part-name misattribution (process failure 5, above).** Once a body is
  published, this project's own discipline forbids editing it; a factual error discovered after
  publication can be corrected only in a future artifact, never in the one that carries it.
- **Whether a green claim-gate run is a wording review.** It is not, and this ledger's own gate runs in
  the Oracle section above do not substitute for one and must never be reported as discharging D-03.
  The blocking operator checkpoints this phase's own posting plans carried were the mechanism intended
  to close that gap, and process failure 6 above states plainly how far short of that they fell.

---

## Composes with (cross-reference only — no data copied)

- `.planning/REQUIREMENTS.md` §"Outward-Facing Close (OUT)" and §"Evidence ceiling" — the requirement
  text and evidence tiers this ledger distils, reproduced by citation not by copy.
- `.planning/ROADMAP.md` §"Phase 152", §"Phase 150", §"Phase 999.28", §"Phase 999.29" — the amended
  criteria, the deferral record and the two backlog items this ledger names rather than re-files.
- `.planning/PROJECT.md` §"Current Milestone: v1.32" — the Evidence ceiling block quoted verbatim
  above, the three workstream-count correction sites, and the Phase 121 D-12 disproven-premise
  correction block at `:1360`.
- `.planning/phases/152-outward-facing-close-operator-gated/152-CLAIM-CLASSES.md` — the forbidden claim
  classes and the mandated word order for the fifth class, by table location per this phase's own
  citation discipline.
- `.planning/phases/152-outward-facing-close-operator-gated/152-CLASS-SIZES.md` — the two-method
  protection-class re-derivation this ledger's claim-table row 3 and negative-space item 4 draw from.
- `.planning/phases/152-outward-facing-close-operator-gated/152-MERGE-RECORD.md` — the beta-merge
  handoff record for `/gsd-complete-milestone`; this ledger's header HEADs and `origin/beta` SHAs
  corroborate its §§2-3 rather than re-deriving them from scratch.
- `.planning/phases/152-outward-facing-close-operator-gated/152-GH12-COMMENT.md`,
  `152-GH21-COMMENT.md`, `152-GH11-COMMENT.md`, `152-RELEASE-NOTES-app.md`, `152-RELEASE-NOTES-fw.md` —
  the five published artifacts this ledger's claim table and process-failures section describe.
- `.planning/phases/152-outward-facing-close-operator-gated/152-11-SUMMARY.md` through
  `152-18-SUMMARY.md` — the per-post measurement records this ledger's header and process-failures
  section cite by plan number.
- `.planning/phases/153-write-path-erase-policy/153-RECORD.md` — the write-path erase policy's own
  "What was NOT established" record, cited for claim-table rows 1 and 2 rather than re-derived.
- `.planning/phases/151-protection-readability-lock-status/151-BENCH.md` — the primary source for
  process failure 5's part-identity correction, and for claim-table row 3's exploratory-probe citation.

**`git status --porcelain` on every path named above** is confirmed empty (ignoring untracked files
outside this plan's own edits) at this ledger's own write time, re-checked immediately before the
Task 3 commit below.

This ships software-proven and unvalidated on silicon.

No AT28C part was tested at any point in v1.32.

Protocol `0x0D` stays UNVERIFIED in PROTOCOL-LEDGER.

---

*Phase: 152-outward-facing-close-operator-gated*
*Written: 2026-08-21*
