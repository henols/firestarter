# Pending todos

These todos came from `agent-os/todos/`. Agent OS was removed from the project on 2026-10-29.
The original files, with their full frontmatter, are at the tag `archive/agent-os-final`:

```bash
git ls-tree -r --name-only archive/agent-os-final agent-os/todos
```

Many entries cite `.planning/` paths. Those files are at the tag `archive/planning-tree-final`.

## Skip VPP error/warning checks when VPP is unused (reads/blank-checks)

*`2026-06-24-skip-vpp-error-and-warning-checks-when-vpp-unused-on-reads.md` · date: 2026-06-24T09:41:26+02:00 · area: firmware*

### Problem

During operations that do NOT apply VPP — `read` and `blank-check` — the firmware still
measures the VPP rail and either **refuses** the operation or emits a **warning**, even
though VPP is irrelevant to a read. This caused real friction in the Phase 81 bench sweep:

- **Chip 1 (W27C512): read-init REFUSED** with `VPP is high: 18.8V > 12.0V` — blocked the
  read entirely until a board reset cleared the rail. A read needs no VPP, so this gate
  should not fire.
- **ST M27C512 / 2516: benign `VPP is low` warnings** on reads (11.9V, 15.3V) — noise,
  since reads don't use VPP.
- **2516 (0x0B Legacy, shared OE/VPP pin): read UNSTABLE** (3 distinct SHAs across 3
  reseat cycles) with VPP pinned at 15.3V on the shared OE/VPP pin — the VPP-rail state
  appears to actively corrupt the read on the shared-pin protocol.

User directive (2026-06-24): "don't check or report errors/warnings when VPP isn't used."

### Solution

TBD — candidate for **Phase 84 FIX-01**. Likely:
1. Gate the VPP voltage check (`VPP is high/low`) on operations that actually drive VPP
   (write/program/erase), not on read/blank-check.
2. For shared-OE/VPP protocols (0x0B Legacy), investigate how the VPP rail is driven
   during a read and ensure the OE/VPP shared pin is held at a clean read level (not a
   floating mid-rail ~15V) so reads are stable — this is the load-bearing fix for the
   2516 read instability that currently GATES Phase 83.
3. Keep parity between host (`eprom_operations.py`) and firmware (`firestarter.cpp`) checks.

Related: the Phase 81 EVIDENCE 2516 ANOMALY + chip-1 refusal; the VPP/VPE rail behavior
documented in v1.14 Phase 79 (rail correction). Does NOT block the Phase 81 read baseline
(recorded as anomalies + Phase 83 gate).

## Drive outputs/pins to a safe state ASAP on power-up and on ANY fault — not only via the 1 s command timeout

*`2026-08-27-safe-state-outputs-on-powerup-and-fault.md` · date: 2026-08-27T18:53:09+02:00 · area: firmware*

### Problem

Operator requirement, captured verbatim in intent: **when power is applied, or when
something goes wrong — connection lost or whatever — the state of the outputs and pins
must be reset ASAP.**

A chip is sitting in a ZIF socket while all of this happens. Anything the shield is
still asserting (VPP/VPE, chip enable, output enable, a latched address, a driven data
bus) is being applied to that part. Today the firmware only guarantees that teardown on
the *clean* path, and the timing on the *dirty* path is neither immediate nor uniform
across boards.

What the code actually does today (verified at fw `5759dc8`):

1. **Clean teardown exists and is correct.** `command_done()`
   ([firestarter.cpp:208-217](firestarter/src/firestarter.cpp#L208-L217)) switches to
   programmer mode, calls `rurp_chip_disable()`, and zeroes `CONTROL_REGISTER`,
   `LEAST_SIGNIFICANT_BYTE`, and `MOST_SIGNIFICANT_BYTE`. That is the safe state.

2. **The only dirty-path trigger is a 1 s poll in `loop()`.**
   [firestarter.cpp:219-221](firestarter/src/firestarter.cpp#L219-L221) reaches
   `command_done()` only when `handle.cmd != CMD_IDLE && timeout < millis()`, with
   `TIMEOUT_MS 1000` ([firestarter.h:47](firestarter/include/firestarter.h#L47)) and
   the deadline pushed forward by `op_reset_timeout()`
   ([firestarter.cpp:349](firestarter/src/firestarter.cpp#L349)) on every accepted
   frame. So a host that disappears mid-command leaves the outputs asserted for up to
   a full second — and only if the main loop is actually reached, which it is not while
   a blocking operation is still running inside the op handler.

3. **`rurp_board_setup()` is NOT board-symmetric at power-up.** The Uno path
   ([uno_rurp_shield.cpp:42-59](firestarter/src/boards/uno_rurp_shield.cpp#L42-L59))
   sets `DDRB`/`PORTB`, then `rurp_chip_disable()`, `rurp_chip_input()`, and zeroes all
   three registers. The Leonardo path
   ([leonardo_rurp_shield.cpp:32-45](firestarter/src/boards/leonardo_rurp_shield.cpp#L32-L45))
   sets the three DDR masks and starts serial — **no `rurp_chip_disable()`, no
   `rurp_chip_input()`, no register zeroing.** On Leonardo the shield's latched outputs
   are whatever they happened to be at power-up until the first command writes them.
   This matters more on Leonardo than Uno because closing the serial port does not
   reset a Leonardo (see `chip-out-before-sideload` — Uno-class only), so there is no
   implicit MCU reset to fall back on.

4. **Power-up ordering puts config work ahead of the safe state.** `setup()`
   ([firestarter.cpp:37-49](firestarter/src/firestarter.cpp#L37-L49)) runs
   `rurp_load_config()` and `rurp_detect_hardware_revision()` *before*
   `rurp_board_setup()`. Whatever those cost in time, the pins are unconstrained for
   that whole window.

Weeks-later context: this was captured during the v1.34 bench campaign, on the back of
repeated cell A2 write failures where a chip stayed in the socket across failed connects
and aborted writes.

### Solution

Not yet designed. Directions worth testing, roughly in order of value:

- **Leonardo parity** — make `rurp_board_setup()` assert the same safe state on both
  boards (`chip_disable` + `chip_input` + zero all three registers). Cheapest and most
  clearly correct item here.
- **Safe state first in `setup()`** — hoist the pin/register safing ahead of
  `rurp_load_config()` / `rurp_detect_hardware_revision()`, so the socket is quiet from
  the earliest instruction that can make it so. Needs a check that safing does not
  depend on loaded config (hardware revision affects some register semantics — confirm
  before moving it).
- **Funnel every fault through the teardown** — audit the error exits (frame decode
  failure, `MSG_ERR_EMPTY_INPUT` at the `n <= 0` branch, unknown command, parse
  failure, per-op error returns) and confirm each one either is already `CMD_IDLE` or
  reaches `command_done()`. Log-and-continue paths that leave a command mid-flight are
  the bug class to hunt.
- **Faster / independent dirty-path trigger** — TBD. Options to evaluate: shorten the
  poll, safe the outputs inside the long-running op handlers on serial silence rather
  than only between commands, or arm the AVR watchdog so a hang resets into `setup()`
  (which then must itself safe the pins first — depends on the item above).
- **Host-disconnect detection** — TBD, and board-dependent. Investigate whether a DTR
  drop is observable on each board and whether it is worth acting on.

Explicitly out of scope of the capture: hardware-side pull-downs / power sequencing on
the shield. That is a board-revision question, not firmware.

## Add a `dev test` flag that files the issue automatically when the run finishes

*`2026-08-30-dev-test-flag-to-auto-file-issue.md` · date: 2026-08-30T22:57:55+02:00 · area: host app*

### Problem

Operator ask (2026-08-30): a flag on `dev test` that auto-creates the GitHub issue when
the run is done, with no prompt.

Today there is no way to get there. `dev test` takes exactly one option, `--fast`
(`cli_handlers.py:2329-2345`); the `--submit` flag it carried through v1.21 was
**removed**, and the comment block at `cli_handlers.py:2292` records it as now erroring
as an unknown option. Every run still ends by handing the report to `submit_report`
(`submit.py:590`), which forks two ways and files on neither automatically:

- **On a TTY** — Step 5 asks `Submit this report to henols/firestarter_prom?` with
  `default=False`. A human has to answer every single run.
- **Off a TTY** — Step 4 prints the prefilled issue URL and returns *without* calling
  `confirm_fn`, `submit_via_gh` or `comment_via_gh_fn`. Filing nothing there is
  deliberate: it is v1.21 SUB-01's ban on silent off-TTY submission, which survived the
  removal of the explicit flag precisely because no flag was left to carry the consent.

So an unattended sweep files nothing at all, and an attended one costs a prompt per chip.
A flag is the missing piece of consent the off-TTY ban was written around — it makes
scripted multi-chip sweeps (e.g. Backlog 999.42, six chips × two shields) able to file
their own reports.

**This is outward-facing:** the flag creates public issues in `henols/firestarter_prom`
(`submit.py:62`) with no human in the loop, so the gate must be provably unable to fire
on a run the operator did not opt into.

### Solution

Add one flag; keep every existing safety property of `submit_report` intact. Points to
settle at discuss-phase:

- **Name.** `--submit` reads naturally and matches the docs/history, but that exact
  spelling was deliberately retired and is currently documented as an unknown option;
  `--auto-submit` or `-y/--yes` avoid re-animating a removed surface. Whichever wins, the
  removal note at `cli_handlers.py:2292` must be corrected in the same change, not left
  contradicting the code.
- **Refuse gate stays.** The flag consents to *filing*; it must never bypass
  `is_submittable` (`diagnostic_report.py:150`) — a report missing
  `chip`/`protocol`/`host_version` still refuses with the named fields.
- **Dedup outcome drives the action.** Step 3 already runs on every path before any ask.
  Under the flag, a found prior issue should comment (the `comment_via_gh_fn` path)
  rather than file a second issue. When the dedup check *could not run* (gh absent,
  unauthenticated, offline), the interactive path asks anyway — unattended, refusing
  loudly is the safer default, because a duplicate public issue is not undoable by the
  tester.
- **Tier.** `gh` only. `submit_via_browser` is meaningless without a human at the tab
  (nothing is filed until someone presses Submit there), so a `gh`-absent run under the
  flag should fail with a stated reason, never open a browser.
- **Interaction with `--fast`.** A fast run's `repeat_policy_tag` already re-keys
  `dedup_fingerprint` so it cannot join an accurate run's N≥2 promotion group. Whether
  auto-filing *weaker* reports at scale is wanted needs an explicit decision — possibly
  refuse the combination.
- **Tests.** Prove the auto-path is unreachable without the flag (TTY and off-TTY), that
  the refuse gate and dedup-comment branch still hold under it, and that no browser tier
  is reachable from it.

## sync_to_subrepos.sh runs `diff -q $X $X` twice — two verifications that assert nothing

*`2026-08-30-sync-to-subrepos-self-diff-asserts-nothing.md` · date: 2026-08-30T13:20:00+02:00 · area: tooling*

### Problem

`tools/catalog/sync_to_subrepos.sh` contains two verification blocks that compare a path to
**itself**:

- line 84: `if diff -q "$FS_ROOT/include/messages.h" "$FS_ROOT/include/messages.h" >/dev/null 2>&1; then`
  followed by `echo "  OK: firestarter/include/messages.h regenerated."`
- line 97: the same shape for `"$FA_ROOT/firestarter/messages.py"`

Both comparisons are tautologically true. Each prints a success line for a property it never
tested, and neither has a reachable failure branch — there is no `else`, so nothing can ever be
observed red. This sits in the repository's only sync tooling, immediately after the `codegen.py`
invocations whose output it purports to verify.

Same defect class as `.github/workflows/catalog-sync-check.yml` (5 runs, 5 failures, never once
asserted the property it existed to assert) and as the ~20 v1.34 rig defects that were all
fixture-selftest-green and all failed on first hardware contact.

Line numbers re-verified 2026-08-30 while planning Phase 167. `167-RESEARCH.md` cites these as
`:88-90` / `:100-102`; `167-PATTERNS.md`'s `:84-86` / `:97-99` are the correct ones.

### Solution

Out of scope for v1.35 — Phase 167 was told to extract the transferable structure from this file
without carrying the defect, not to fix the file. Candidate fix, whenever it is picked up:

1. Regenerate into a temporary path, then `diff` the committed artifact against that temp copy —
   two traceably distinct operands.
2. Add the missing `else` branch: `echo "ERROR: ..." >&2` and a non-zero exit, so the failure
   branch exists and can be observed.
3. Prove it: mutate the committed `messages.h`, run the script, confirm it goes red, restore.
   A verification whose red state has never been seen proves nothing.

The correct pattern already exists in the same file at lines 65-70 (the cross-sub-repo
byte-identity assertion) — copy that shape.

Reference implementation of the discipline: `tools/wiki/selftest.sh` and its evidence table,
authored in Phase 167, where every case asserts a control leg and a mutated leg.

## Record which pin JP4's third position routes VPP to (Rev 2.2 / Rev 2.3)

*`2026-08-31-jp4-third-position-vpp-destination-pin.md` · date: 2026-08-31T02:00:00+02:00 · area: hardware-docs*

The wiki's Shield Revisions page states that JP4's third position reroutes VPP and
that this is what reaches the TI 2516 and 2532, but does not say **which pin** VPP
lands on. Operator will supply the value.

An earlier draft claimed the TI parts take VPP "on a different pin than the JEDEC
parts". That was removed on 2026-08-31 because it is false for the 2516: it uses the
`DIP24_2716` pinout with VPP on pin 21, exactly as the JEDEC 2716 does.

The pinout data does not explain why a reroute is needed, so the answer is in the
schematic or on the board, not in the repository. Unverified inference worth checking
when this is settled: the 2532 is the part that actually needs it — pin 21 is VPP on
`DIP24_2532` but A11 on the JEDEC `DIP24_2732`, and pin 18 flips the other way
(A11 vs /CE). A fixed JEDEC-wired socket would therefore need pin 21 switched from an
address line to VPP for a 2532, with the 2516 following because it shares protocol
`0x0B`.

## dev test m27c512 now passes on a non-blank UV part via FLAG_SKIP_BLANK_CHECK while firestarter write is still refused by the identical firmware, and no exported key discloses the divergence

*`2026-09-08-uv-write-shortcut-disclosure-key.md` · date: 2026-09-08 · priority: low*

### What is true after Phase 179

`firestarter dev test m27c512` now passes (`overall_verdict == "PASS"`, `run_count == 2`) on a
non-blank UV part, by passing `FLAG_SKIP_BLANK_CHECK` on a proven monotonic masked write. On the
IDENTICAL part, `firestarter write -a 0x…` is still refused by the identical firmware write-init
pre-flight — the user-facing write command does not set `FLAG_SKIP_BLANK_CHECK`, and nothing in the
current report discloses that the `dev test` harness took a path the product's own write command
does not take.

`.planning/research/PITFALLS.md:236-247` (Pitfall 7) argued this divergence needs disclosure, and its
own verdict was "Both, or neither" — either export a key naming the divergence AND fix the harness to
mirror the product path, or accept the divergence explicitly and disclose it. Phase 179 took
"neither" as its working answer for THIS phase, for two reasons:

1. `write_current_source` (the per-step field Phase 179 already exports, reading
   `"probe read (tranche N/2)"` on the write step that used the flag) already discloses that the
   write was probe-masked — a triager reading a UV `PASS` report can see the write step's
   `write_current_source` field and infer the shortcut was taken, even without a dedicated key.
2. `RPT-A4` (`plan.is_uv` reaching the report as a top-level boolean, read off the single
   `derive_plan` decision, never re-derived) is EXPLICITLY Phase 181's requirement
   (`.planning/REQUIREMENTS.md`'s Report Fidelity section). A UV-shortcut disclosure key is a natural
   sibling of `plan.is_uv` — it belongs in the same phase that adds the boolean it would key off of,
   not bolted on ahead of it in Phase 179.

An unrequested exported key added in Phase 179 would also grow the frozen-key surface this milestone
is deliberately holding still mid-milestone (the blast-radius invariance harness treats every new
top-level report key as a re-key event across the frozen corpus) — a cost Phase 179's own scope
(UV-01/UV-02/UV-03) does not require paying.

### Disposition

**Deferred to Phase 181**, alongside `RPT-A4`. When Phase 181 lands `plan.is_uv`, revisit whether a
dedicated `write_flags_diverge_from_product` (or similarly-named) key is warranted, or whether
`write_current_source`'s existing probe-masked disclosure plus `plan.is_uv` together already satisfy
Pitfall 7's "Both, or neither" bar without a new key. Not resolved by this todo — filed as the
decision point Phase 181 should reach, not a specific implementation this todo prescribes.

## Close the six stale enforcement claims WR-01..WR-06 left open by Phase 188

*`2026-09-13-close-six-stale-claims-wr01-wr06.md` · date: 2026-09-13T05:10:00+02:00 · area: both*

### What

Phase 188 retired the host `tools/` gate family. Six prose claims elsewhere in the tree still
describe those retired gates as live enforcement. The operator accepted all six as **disclosed
follow-on debt** at the Phase 188 UAT checkpoint on 2026-09-13 — they are recorded here rather
than fixed inside 188, because fixing them expands the phase beyond its nine plans.

**None of these breaks a test or falsifies a roadmap success criterion.** All four suites were
green and all seven Phase 188 criteria verified. These are false *claims about enforcement*, which
matters because the milestone is named "Claim Hygiene".

### The six, each with the claim that is now false

All six were re-measured directly in the tree on 2026-09-13 and confirmed still present.

| ID | Location | The false claim |
|----|----------|-----------------|
| WR-01 | `firestarter_app/tools/parse_devtest_issue.py:215` | "No claim gate scans this file today (P-5); that test is the only enforcement." Both named enforcers are gone: `check_diagnostic_report_claims.py` is deleted (0 tracked files) and the only surviving mention of `test_parser_marker_strings_trip_no_forbidden_claim_pattern` anywhere in the repo is this comment itself. The claim-safety property now has **zero** enforcement, not one test. |
| WR-02 | `firestarter_app/tests/test_sdp_db_invariant.py:165` | Says widening of the SDP allow-set is what "`tools/check_sdp_capability_invariants.py` already gates elsewhere." That checker is deleted (0 tracked files; 0 files match `tools/check_*.py`). The narrowing direction is still gated by this test; the widening direction is not gated at all. |
| WR-03 | ~~`firestarter_app/tests/test_numeric_schema_source_scan.py:215,235`~~ **CLOSED 2026-09-14** — module deleted by the source-introspection sweep (see `.planning/notes/test-suite-source-introspection-removal.md`); the self-contradicting docstring no longer exists. | The non-vacuity test's docstring and its assertion message both still say "tests 1 and 2". The module docstring at line 43 was correctly repaired to "test 1" — these two were missed in the same sweep, so the file now contradicts itself. |
| WR-04 | `firestarter_app/tests/test_build_db_inclusion.py:11` | "the SC#3 dispatch-safety invariant enforced by Plan 04." The enforcing test was deleted with the `check_*` family; the invariant is unenforced. |
| WR-05 | `firestarter/.github/workflows/beta-build.yml:107` | "Same rationale as the vector gates above" — those vector-gate steps were deleted by 188-06, so the comment's antecedent no longer exists in the file. The step it annotates (`native_nodevtools`) is still correct and must stay; only the back-reference is stale. |
| WR-06 | `firestarter_app/CLAUDE.md:127` | The "Tooling gate (v1.8)" line still lists `mypy` among the checks "all enforced by `.github/workflows/ci.yml` on every PR". 188-04 deleted that CI step under D-02. `ruff check`, `ruff format --check` and `pytest --cov-fail-under=70` remain true; only `mypy` is false. |

### WR-06 carries a second, separate obligation

`188-04`'s own SUMMARY promised that the mypy-gate removal would be recorded permanently in
`.planning/notes/host-tools-retirement.md`, and `188-09` did not deliver it in full.

The note **does** record the CI leg's removal ("The mypy CI leg (D-02) — retired, no replacement",
§2). What it does **not** record is that `firestarter_app/CLAUDE.md` still advertises mypy as
CI-enforced — so a later reader who trusts CLAUDE.md is misled with nothing in the retirement note
to correct them. Fixing WR-06 means **both** editing CLAUDE.md line 127 **and** adding that fact to
the retirement note.

### Disposition 2026-09-13

Executed by quick task `260913-e7t`.

- **WR-02, WR-03, WR-04, WR-06a** — corrected in `firestarter_app` commit
  `71cc762bc9c5e95dd3b3e8e303fa10597020dc2a`.
- **WR-05** — corrected in `firestarter` commit `447b73e235f533c3ae1be9e054534b937ca21ca6`.
- **WR-06b** — recorded in `.planning/notes/host-tools-retirement.md` §1, appended to the
  `**The mypy CI leg (D-02) — retired, no replacement:**` paragraph.
- **WR-01 — NOT fixed here, and deliberately so.** WR-01 is a source comment at
  `firestarter_app/tools/parse_devtest_issue.py:215`. The operator's hard rule (see
  `firestarter_app/CLAUDE.md`, "Source code comments — hard rule") forbids any comment in product
  source, including a corrected one — rewording it to name a different enforcer would manufacture
  exactly the kind of provenance-laden prose the rule exists to remove. Its correct disposition is
  **deletion** of the comment block, folded into the existing sweep tracked by
  `.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md`, not a reword in
  this task. A carry-over line was added to that todo's `firestarter_app/tools/` bullet so its
  "DISCHARGED 2026-09-13 (Phase 188)" measurement — which covered only `.planning/` citations — is
  not misread as covering WR-01 too.

**Five of six resolved (WR-02 through WR-06); WR-01 remains open by design.** This file stays under
`pending/`, not `completed/`, because its own "Done when" block requires all six, and filing a
five-of-six todo as `completed/` in a milestone named Claim Hygiene would be the same species of
over-claim this task exists to remove.

### Note on line numbers

`188-REVIEW.md` cites each finding as a **range** covering the whole comment block (212-215,
161-166, 9-11) and those ranges are correct. The `188-UAT.md` table collapsed each range to its
*first* line rather than to the line carrying the false claim. The line numbers in this file are the
measured claim lines — **215, 165 and 11** — and the UAT table has been repaired to match. WR-03,
WR-05 and WR-06 were already exact in both records.

### Done when

- ~~All six claims are corrected in place (WR-05 by rewording the back-reference, not by deleting
  the step it annotates).~~ **WR-02..WR-06 corrected 2026-09-13 — see Disposition above.** WR-01
  remains: the sole open condition is that the comment block at
  `firestarter_app/tools/parse_devtest_issue.py:215` is **deleted** (not reworded) by the
  provenance-strip sweep tracked in
  `.planning/todos/pending/2026-08-27-strip-gsd-provenance-comments-from-source.md`.
- ~~WR-06's CLAUDE.md correction is accompanied by a matching entry in
  `.planning/notes/host-tools-retirement.md`.~~ **Done 2026-09-13 — see Disposition above.**
- The four app suites and the firmware native gate stay green. **Confirmed 2026-09-13: 2129 passed
  (`firestarter_app`), 316 passed (`firestarter`).**

## publish.yml's release published trigger is suppressed for bot-created releases — 2.0.8 was cut and never published

*`2026-09-13-publish-yml-release-published-never-fires.md` · date: 2026-09-13T22:45:00+02:00 · area: tooling*

> **Corrected 2026-09-13, after filing.** The original version of this item asserted the
> `release: published` trigger "has literally never fired in this repository — 8 of 8 runs are
> `workflow_dispatch`." **That measurement was wrong**, and it was wrong because it was taken with
> `gh run list --limit 10`: eleven runs existed, so the listing cut exactly one row — the oldest,
> which was the single `release`-event counterexample. The trigger fires. The **fix** proposed
> below was correct then and is unchanged now; only the diagnosis has been replaced.

### Problem

`publish.yml` declares two triggers: `release: [published]` and a `workflow_dispatch` taking a
required `tag` input. The `release: published` trigger **works** — but it is silently suppressed
for exactly the releases that matter most: the ones `release.yml` creates automatically.

Measured live 2026-09-13 (`gh run list --workflow publish.yml --limit 30`, 13 runs total), the
correlation is perfect:

| tag | release created by | `publish.yml` run | on PyPI? |
|-----|--------------------|-------------------|----------|
| 2.0.7 | `henols` (User) | `20956549620`, `event: release`, **success** | yes |
| 2.0.8 | `github-actions[bot]` (Bot) | **none — never fired** | **no** |
| 2.0.9 | `henols` (User) | `34785081535`, `event: release` (raced, see below) | yes |

Every **human**-created release triggered a publish. The one created by a **workflow** did not.

The mechanism is documented GitHub behavior, and `publish.yml`'s own comment block already names
it (dated from an earlier recovery, Phase 20 E2E-01): a workflow run authenticated with the
default `GITHUB_TOKEN` does not create new workflow runs, so the `release: published` event it
emits is never delivered. `release.yml` creates its release via `softprops/action-gh-release` with
that token — so the event it raises reaches nothing.

**The consequence is on disk, not hypothetical:** GitHub release `2.0.8` exists (cut 2026-08-07 by
`github-actions[bot]`) while PyPI skips straight from `2.0.7` to `2.0.9`. `2.0.8` was cut and
never published, and nothing reported an error.

**Secondary hazard, observed 2026-09-13:** when the operator hand-creates a release *and* also
hand-dispatches `publish.yml`, the two race. Run `34785081535` (auto, `event: release`) and run
`34785081751` (manual, `workflow_dispatch`) started in the same second for `2.0.9`; the manual one
won the upload and the automatic one failed with a PyPI "File already exists" collision on the
sdist. **For a hand-cut release the manual dispatch is redundant** — create the tag and release,
then watch whether the release-event run publishes on its own before reaching for
`gh workflow run`.

### Why it matters

A tag/release existing on GitHub gives no signal about whether the corresponding artefact is
installable from PyPI — and the gap opens precisely on the automated path, which is the one nobody
is watching. Anyone reading GitHub's releases page (the operator, or an automated check keying off
the latest GitHub release) would believe `2.0.8` was the current stable when PyPI never received
it. The silent-failure shape is identical to the one `publish.yml`'s comment block already
describes for the beta channel ("GitHub reached b17 while PyPI stopped at b15").

### Known-good fix

Unchanged from the original filing — and the corrected diagnosis makes it *more* clearly right,
not less. `beta-release.yml` (`origin/beta`) already solved this exact problem for the beta
channel by adding a second job:

```yaml
pypi:
  needs: github
  uses: ./.github/workflows/publish.yml
  with:
    tag: ${{ needs.github.outputs.version }}
  secrets: inherit
```

This calls `publish.yml` **directly as a reusable workflow** rather than relying on an event
cascade — which is exactly the right shape, because the event cascade is what `GITHUB_TOKEN`
suppresses. A reusable-workflow call is not an event and is not subject to the restriction. The
tag comes from the release job's own `outputs.version` rather than being re-derived, so it cannot
drift. It also passes `target_commitish` on the release step so the tag lands on the commit
containing the version bump rather than the pre-bump trigger SHA.

`main`'s `release.yml` has neither piece.

### Relationship to the sibling defect

Both this and `2026-09-13-release-yml-autocommit-vs-ruleset.md` are the **same root cause**: the
default `GITHUB_TOKEN`'s deliberate limitations. There, it cannot bypass the ruleset's
`pull_request` requirement to push a version bump (observed live: `GH013`, run `34784468070`).
Here, it cannot cascade an event to another workflow. `beta-release.yml`'s pattern addresses both,
which is why both items name it.

### Disposition

**Filed, not fixed, in Phase 191.** Porting the `pypi`-job pattern to `main`'s `release.yml` here
would be inert: this phase's D-04 deliberately does not fix the push-blocker defect filed alongside
this one, so the job that would call `publish.yml` still never runs regardless of whether a `pypi`
job exists to call it. A half-fix that cannot execute is worse evidence than a filed defect — the
next stable cut on `main` should reach for `beta-release.yml`'s pattern in full.

## release.yml's git-auto-commit-action push to main is rejected by the Protect main ruleset

*`2026-09-13-release-yml-autocommit-vs-ruleset.md` · date: 2026-09-13T22:45:00+02:00 · area: tooling*

### Problem

`release.yml` runs `on: push: branches: [main]`, with a `paths-ignore` list covering `**.md`,
`**.sh`, `.gitignore`, `docs/**`, `images/**`, `.github/**`, `.vscode/**` and `tools/**` — but
**not** `firestarter/**`. Any merge touching `firestarter/constants.py` (URL-02's own change,
among others) fires it.

Its `update_version.py` step bumps the patch version, and
`stefanzweifel/git-auto-commit-action@v5` then pushes the bump **directly to `main`** using the
default `GITHUB_TOKEN` — the step's `PERSONAL_ACCESS_TOKEN` env line is commented out.

`main`'s branch protection is ruleset **`22046179`** ("Protect main"), `enforcement: active`,
scope `~DEFAULT_BRANCH`, created **2026-09-01**. It enforces `pull_request` (among
`deletion`/`non_fast_forward`), its only bypass actor is `DeployKey`, and
`current_user_can_bypass` is `never` — no person, and no `GITHUB_TOKEN`, can push past a
`pull_request` rule. GitHub's own documentation and community guidance are explicit that the
default `GITHUB_TOKEN` cannot bypass a `pull_request` rule even when actors are listed.

**Consequence:** the auto-commit push is rejected, the step fails, the job aborts, and the
`Release` step never runs — no tag, no GitHub release, nothing reaches PyPI from this workflow.

**This has never been exercised under protection.** `release.yml`'s last recorded run was
`2026-08-07` on `e4112ef` — **25 days before** the ruleset was created on `2026-09-01`. The
collision is real but has not yet been observed failing in CI; Phase 191 predicts it and hands the
operator a manual tag/release/`workflow_dispatch` sequence instead of relying on this workflow.

### Why it matters

`main` is the branch every default `pip install firestarter` resolves against. Its own automatic
release pipeline cannot complete a single cut without manual intervention, and nothing in the
workflow surfaces that failure other than a red run in the Actions tab — the same silent-failure
shape as the `publish.yml` defect filed alongside this one.

### Known-good fix

This repository already solved the equivalent problem on its `beta` channel.
`beta-release.yml` (`origin/beta`) commits its own version bump with
`git-auto-commit-action` and pushes to `beta`, which is **not** under a `pull_request`-enforcing
ruleset — so the direct push succeeds there. Porting that exact shape to `main` is not possible
while `main` requires a pull request for every change; the fix here is either:

1. a credential change — a `PERSONAL_ACCESS_TOKEN` (or a `DeployKey`-based bypass) with the
   authority to push past the ruleset, wired into the commented-out `env:` line, or
2. a redesign that stops `release.yml` pushing to `main` at all — e.g. opening a bot-authored
   pull request for the version bump instead of pushing directly, mirroring how this milestone's
   own `main`-facing changes are prepared and merged.

Either direction changes how `main`'s protection interacts with automation and is out of scope for
a rename milestone.

### Disposition

**Filed, not fixed, in Phase 191.** URL-02 repoints one constant and bumps the version by hand in
the same commit specifically so the stable release does not depend on this workflow completing.
No ruleset change and no redesign of the stable release flow was made as part of this phase.

## Reject a negative write start address instead of silently clamping it to 0

*`2026-09-16-reject-negative-write-start-address.md` · date: 2026-09-16T15:05:00+02:00 · area: both*

### Problem

Filed as accepted debt at the Phase 195 UAT checkpoint (2026-09-16), disposition (a).
Recorded in code review as **WR-01**.

`firestarter write W29C020 <file> -a -256` passes the host page-alignment guard and
exits 0. Two independent behaviours combine:

1. `parse_address` does not reject a negative string — it hands `-256` straight through.
2. Python's `%` returns a non-negative result for a negative dividend, so
   `-256 % 256 == 0` reads as **aligned** in `require_page_alignment`.

The firmware does not catch it either. `simple_strtoul` consumes only `[0-9]`; a leading
`-` is not a digit, so the loop body never runs and the function returns 0. Confirmed by
compiling the function verbatim and running it: `-256` -> 0, `-1` -> 0.

### Why this was not fixed in Phase 195

The consequence is narrower than the review could establish. A write requested at a
negative address silently lands at **address 0**, which is page-aligned, for a length
already proven to be a whole number of pages. It therefore erases nothing outside the
range it writes and violates neither WRITE-01 nor WRITE-02.

It is a **wrong-destination** defect — a silent clamp to 0 where a refusal belongs — not
a partial-page-destruction defect. All four of Phase 195's success criteria concern
alignment and length, not address sign, so it was out of scope.

The user still loses data: the write lands at 0 and overwrites whatever is there, with
no diagnostic and a zero exit code.

### Solution

TBD. Candidate shape:

1. Reject a negative start address in `require_page_alignment` **before** the modulo
   check, with a refusal message naming the address — the modulo check cannot be made to
   catch it, because it reports the sign-folded value as aligned.
2. Decide whether `parse_address` itself should refuse negatives. It is shared with the
   read and blank-check paths, so a change there is wider than the write guard and needs
   its own callers audited first.
3. Consider a firmware-side refusal so the host guard is not the only line of defence —
   `simple_strtoul` currently makes a negative address indistinguishable from `0` on the
   wire, which is what hides the defect today.

Any fix needs a regression test pinning `-256` (and `-1`) as a refusal, not a pass.

## test_flash_path_record_sync.py's _META_DOC_REL points at a path the .planning layout reorganisation moved — 17 local failures, invisible to CI

*`2026-09-19-flash-path-record-sync-meta-doc-rel-stale.md` · date: 2026-09-19T02:00:00+02:00 · area: firmware test suite*

### Problem

`firestarter_fw/tests/test_flash_path_record_sync.py:77` defines

```python
_META_DOC_REL = "v1.23-FLASH-PATH-DECISION.md"
```

resolved under `META_ROOT/.planning/` by the module's own `meta_path()` helper. The file now lives
at `/workspaces/.planning/milestones/v1.23-FLASH-PATH-DECISION.md` — the `.planning` layout
reorganisation moved it into `milestones/` and this scan path was never updated to match. Every leg
that reads the meta copy of the flash-path decision record fails with a `MissingScanTargetError` in
any checkout where the meta repository is present.

### Reproduction

```bash
cd /workspaces/firestarter_fw
python3 -m pytest tests/ -o addopts="" -q
# -> 17 failed, 284 passed (or higher, depending on suite growth since) in this devcontainer
```

### Why CI never sees this

`tests/meta_presence.py:84` computes `META_PRESENT: bool = META_MARKER.exists()`, and every affected
leg in `test_flash_path_record_sync.py` carries the `requires_meta` marker
(`tests/meta_presence.py:95`: `requires_meta = pytest.mark.skipif(not META_PRESENT, reason=...)`).
CI checks out `firestarter_fw` standalone — no parent `.git` — so `META_PRESENT` is `False` and all
17 legs **skip** rather than fail. In `/workspaces`, the meta repository's `.git` is present, so
`META_PRESENT` is `True` and the same legs run for real, hit the stale path, and fail closed by
design (the module's own docstring calls this the "hard-failure half of the split" — a present meta
repo with a broken scan target must FAIL, never silently skip).

### Workaround, confirmed working, used throughout Phase 201's own verify blocks

```bash
cd /workspaces/firestarter_fw
mkdir -p /tmp/no-meta
FIRESTARTER_META_ROOT=/tmp/no-meta python3 -m pytest tests/ -o addopts="" -q
# -> 269 passed, 32 skipped in ~13-15s (pre-Phase-201 baseline; higher after Phase 201's own new legs)
```

`FIRESTARTER_META_ROOT` must be set in the **child process** environment — it binds at import time
(`tests/meta_presence.py:79`), so a post-import monkeypatch does not work. Setting it to a directory
with no `.git` reproduces CI's meta-absent condition exactly, and `META_PRESENT` resolves `False`
identically to a standalone-checkout CI run.

### Disposition

**Not repaired here.** The repair belongs with the `.planning` layout change that moved the file
(a meta-repository change), not with a bench-gated dual-repo lockstep phase whose commit pairing
between `firestarter_fw` and the meta repository is already load-bearing (Phase 201 threat model
T-201-05-03 and sibling plans' verify legs both depend on precise, minimal per-commit diffs). Fixing
`_META_DOC_REL` here would add an unrelated firmware commit into that lockstep.

**Fix, when picked up:** update `_META_DOC_REL` in
`firestarter_fw/tests/test_flash_path_record_sync.py:77` to
`"milestones/v1.23-FLASH-PATH-DECISION.md"` (or wherever the file lives by the time this is picked
up — re-verify the live path first), then confirm
`FIRESTARTER_META_ROOT=/workspaces python3 -m pytest tests/test_flash_path_record_sync.py -o addopts="" -q`
goes from failing to passing with the meta repository genuinely present.

### Two more stale in-repo citations found while checking this (same root cause class: a deleted or
moved target, never updated)

Neither of the following affects test behaviour — both are prose citations in comments, not scan
targets — but both are wrong today and are recorded here so they are fixed in the same pass as the
`_META_DOC_REL` repair rather than rediscovered separately:

1. `firestarter_fw/include/firestarter.h:181-184` cites
   `firestarter_app/tests/test_revision_constants_parity.py` as the gate that bidirectionally pins
   the largest `ctrl_flags` value at `0x100`. That file does not exist —
   `ls firestarter_app/tests/test_revision_constants_parity.py` reports "No such file or directory".
   It was deleted by operator ruling `088d2b7` (the host-side source-scanning gate ban).
2. `firestarter_fw/tests/meta_presence.py:19` and `:70` both cite
   `firestarter_app/tests/fw_presence.py` as the sibling module whose "two parents up" arithmetic
   this module's docstring contrasts itself against. That file also does not exist —
   `ls firestarter_app/tests/fw_presence.py` reports "No such file or directory" — deleted by the
   same operator ruling.

Both citations describe real, still-correct reasoning (the parity invariant firestarter.h's comment
describes, and the parent-vs-sibling arithmetic meta_presence.py's docstring describes); only the
named file each points at is gone. Whoever repairs `_META_DOC_REL` should either point these two
citations at whatever gate now carries the same invariant (if one exists post-088d2b7) or rephrase
them to state the invariant without naming a file that no longer resolves.

## Pre-flash firmware version guard — refuse a firmware whose feature version exceeds the CLI's

*`2026-09-20-preflight-firmware-version-compat-guard.md` · date: 2026-09-20T02:00:00+02:00 · area: host*

### Problem

The published 2.0.9 wheel resolves firmware through a hard-coded endpoint
(`git show 2.0.9:firestarter/constants.py`):

```
"https://api.github.com/repos/henols/firestarter_fw/releases/latest"
```

`/releases/latest` excludes pre-releases. Today it returns a matched pair —
`gh api repos/henols/firestarter_fw/releases/latest` gives `tag_name: 2.0.6`, `prerelease: false`,
with `firestarter_uno.hex` and `firestarter_leonardo.hex`. A 2.0.9 user running `firestarter fw`
gets 2.0.6 firmware and everything works.

**The first stable 3.0.0 firmware release flips that endpoint for every 2.0.9 CLI in the field.**
Per the wiki's Breaking-Changes page, "a new CLI cannot drive old firmware, and old firmware cannot
be driven by a new CLI."

The CLI does not merely permit this — it recommends it. `FirmwareManager._compare_versions` reads:

```python
current = tuple(map(int, current_version_str.split(".")))
latest  = tuple(map(int, latest_version_str.split(".")))
return current >= latest
```

`(2,0,6) >= (3,0,0)` is `False`, which the caller reads as "out of date". The user is prompted to
flash, accepts, and ends up with a programmer their installed CLI cannot talk to, no error that
explains why, and no hint that the fix is `pip install --upgrade firestarter`.

Sequencing the app release before the firmware release does not fix this: a user who never upgrades
the CLI still walks into it. **The guard has to be on the stable channel before any stable firmware
release**, which means a `2.0.10` release cut from `main`.

### The rule

Compare feature versions — `(major, minor)`, patch ignored:

```
refuse when (fw.major, fw.minor) > (cli.major, cli.minor)
```

| CLI | firmware | result | rationale |
|---|---|---|---|
| 2.0.10 | 3.0.0 | refuse | the case at hand |
| 3.0.0 | 3.1.0 | refuse | generic to any future minor bump |
| 3.0.0 | 3.0.5 | allow | patches flow freely |
| 3.0.0b50 | 3.0.0b35 | allow | same wire protocol |
| 3.1.0 | 3.0.0 | allow | reverse mismatch — out of scope, see below |

The guard must work from release metadata alone. The CLI is deciding whether to download a `.hex` it
has not run yet, so no handshake is available and the release tag is the only signal.

### Decisions already made

Taken in the explore session of 2026-09-20; reasons recorded so they are not relitigated.

- **Hand-roll the parser; do not add `packaging`.** 2.0.9 depends on `pyserial`, `requests`, `tqdm`,
  `argcomplete`, `rich` and nothing else (`git show 2.0.9:pyproject.toml`). Adding a dependency to a
  branch 1060 commits stale, whose CI carries its own release-cutting hazards, buys nothing.
  `^v?(\d+)\.(\d+)` suffices and tolerates the `b35` pre-release suffix that the existing `int()`
  parse raises `ValueError` on.
- **Fail closed on an unparseable version, either side.** This project has a documented history of
  gates that fail open. "I could not read the firmware tag" must refuse, not proceed. Give the
  CLI-side parse failure a distinct message — it indicates a packaging fault, not a mismatch.
- **Ship a `--force` escape hatch.** Mismatched pairs are flashed deliberately at the bench; a
  refusal with no override breaks the operator's own workflow.
- **The message is the feature.** The refusal must name `pip install --upgrade firestarter`
  verbatim. This guard converts "CLI first, then firmware" from prose in the wiki into a contract
  enforced in code, permanently — every future minor firmware bump blocks users until they upgrade
  the CLI, so the refusal will be seen often and must be self-explanatory.

### Scope

Lands twice, with the same rule and the same message:

1. **`2.0.10`**, cut from `main`. The guard is the *only* change. This is the release that closes
   the trap, and it must reach PyPI before any stable firmware release.
2. **The 3.0.x line** on `beta`, so the rule is permanent rather than a one-off patch to a dead
   branch.

**Explicitly out of scope, by operator decision on 2026-09-20:** the mirror case — a new CLI driving
old firmware already on a board. It is detectable at runtime, since `check_current_firmware()`
already returns the board's version string, but it is a different mechanism in a different place and
was deferred rather than filed.

### Caution

`main` in `firestarter_app` is 1060 commits stale and cutting `2.0.10` from it means exercising that
branch's release path. Check `release.yml` and `publish.yml` behaviour there first — see
`.planning/todos/pending/2026-09-13-publish-yml-release-published-never-fires.md` and
`.planning/todos/pending/2026-09-13-release-yml-autocommit-vs-ruleset.md`, both of which concern
exactly this branch's publishing machinery.

## `programming_vcc_over_rail_mv` fails closed on a non-dict `electrical`

*`2026-09-20-programming-vcc-predicate-fails-closed-on-non-dict-electrical.md` · date: 2026-09-20 · priority: critical*

`firestarter_app/firestarter/eprom_info.py:63-71` — the function's own docstring states it "must
fail open" and enumerates the malformed shapes it defends against. Its `except` tuple is
`(TypeError, ValueError)`, which does not cover `AttributeError`, so a present-but-non-dict
`electrical` value raises instead of returning `None`:

```python
programming_vcc_over_rail_mv({"electrical": "bogus"})   # AttributeError, not None
programming_vcc_over_rail_mv({"electrical": 123})       # AttributeError, not None
programming_vcc_over_rail_mv({"electrical": [1, 2, 3]}) # AttributeError, not None
```

**Why it was not fixed in Phase 200.** No must-have in any of the three plans enumerates a
present-but-non-dict `electrical` — 200-01's D-06 truth and 200-03's fail-open matrix both list
five malformed `vdd_mv` shapes plus an absent key and a `None` record, and every one of those
returns `None` correctly. `200-VERIFICATION.md` judged it real but not a phase blocker and
explicitly recommended filing it as a follow-up. That filing is this file; it did not happen at the
time.

**Why it is narrow today.** `firestarter/database.py:356` does `electrical = ic.get("electrical",
{})` then unconditionally `electrical.get("pin_count")` one call earlier in the same request, so a
malformed `electrical` already raises `AttributeError` in `_map_data` before this predicate is
reached via `info`. The live 746-row shipped database has zero rows in any fail-open state.

**Why it is still worth fixing.** `programming_vcc_over_rail_mv` is a public, standalone, directly
tested predicate — `test_programming_vcc_census.py` calls it with no `_map_data` in the path — and
the operator-supplied `~/.firestarter/database.json` override that `EpromDatabase` merges over the
packaged database is exactly the source of a malformed shape. A docstring that promises fail-open
without carving out this case is false as written.

Also fix `200-REVIEW.md` WR-01 in the same change: the fail-open test's name overstates its
coverage, since it never exercises a non-dict `electrical`.

Suggested fix: add `AttributeError` to the except tuple, or validate `isinstance(electrical, dict)`
explicitly, and add the three cases above to the fail-open test. Two-line change, obvious test.

## `region-end` has no test coverage through the real `json_parse()` path

*`2026-09-20-region-end-wire-key-has-no-json-parse-coverage.md` · date: 2026-09-20 · priority: warning*

Phase 201 added the `region-end` wire key: a PROGMEM key string plus a `FIELD()` table row in
`firestarter_fw/src/json_parser.c`, and a per-command reset to 0.

Every test that exercises the region behaviour sets `handle->region_end` **directly on the C
struct**, bypassing the PROGMEM-string / offset / width machinery entirely. So a typo in the key
string, a wrong offset or width in the table row, or a broken per-command reset would not redden
any automated test.

The mechanism *was* proven once on real hardware — the bench session's confirming run could only
have produced its observed progress denominator if `json_parse()` wrote `handle->region_end`
correctly. But a bench record is evidence, not a regression test, and it does not re-run.

**Precedent to follow:** `firestarter_fw/test/native/avr/test_read_timing/test_read_timing_params.cpp`
does exactly this for `read-settling-delay` and `read-strobe-us`, in the same pinned native env.
`201-REVIEW.md` carries ready-to-drop-in cases.

Two things to cover: a round-trip through `json_parse()` asserting the parsed value lands in
`handle->region_end`, and the per-command reset to 0.

## `check_eprom_blank`'s SRAM/FRAM short-circuit is inert on the CLI path

*`2026-09-21-blank-check-sram-fram-shortcircuit-is-inert.md` · date: 2026-09-21 · priority: major*

`firestarter_app/firestarter/eprom_operations.py:2639-2648` short-circuits the blank check for
SRAM/FRAM parts by reading `electrical-type` and `protocol-id` from the programmer wire dict.
**The wire dict `resolve_chip` returns carries neither key.** It carries `algorithm`, `flags`,
`memory-size`, `pin-count`, `vpp_mv`, `pulse-delay` and three conditional keys — nothing else.
The short-circuit therefore never fires on the CLI path: both lookups miss, the branch evaluates
falsy, and an SRAM part gets the full blank read it was written to skip.

Probed during Phase 203 research; the probe **refuted** the assumption rather than confirming it.

**The repository already knows this failure class.** `firestarter_app/firestarter/sdp_capability.py:186-195`
hard-fails on a missing wire-dict key with a comment naming this exact bug as its reason. That
module chose `raise KeyError` over `.get(key, default)` precisely so a future key rename could not
silently reintroduce a vacuous predicate. The `check_eprom_blank` short-circuit predates that
lesson and never got it.

**Why it was not folded into Phase 203.** It is a `blank` defect; no WRITE requirement covers it,
and folding it would have widened an already-large phase. 203-RESEARCH.md recommended filing rather
than folding, and the planner agreed. Phase 203's own new predicate is protected against joining
this failure class by an AST test asserting it reads only `algorithm` and `flags` — so the fix here
is isolated, not a prerequisite for anything 203 builds.

**Blast radius.** The observable symptom is a slow `blank` on an SRAM/FRAM part, not a wrong answer:
the read returns whatever the part holds and the comparison is honest about it. The cost is time and
an unnecessary port session, not a false verdict. That is why this is major rather than critical.

Suggested fix: decide what the predicate should key on — `algorithm` against the four SRAM protocol
ids is the shape Phase 203's guard uses and the one the wire dict can actually answer — then make
the missing-key case `raise KeyError` in the `sdp_capability.py` style rather than defaulting. Add a
test that drives the short-circuit through a real `resolve_chip` wire dict, not a hand-built one; a
hand-built dict carrying `electrical-type` is exactly what let this survive.

## platformio.ini Leonardo comment says the host reads DATA_BUFFER_SIZE from the identity string

*`2026-09-24-platformio-leonardo-buffer-comment-is-stale.md` · date: 2026-09-24T02:00:00+02:00 · area: firmware*

### Problem

The `[env:leonardo]` comment in `firestarter_fw/platformio.ini` says: "The host reads
DATA_BUFFER_SIZE from the FW identity string and sizes its chunks to 1022". That mechanism was
removed. `firestarter.h` says the identity string is now `<version>:<board>` only. The buffer size
is sent as a u16 param on every `MSG_OK_READY` ack. The host reads that value
(`firmware_max_chunk`) and falls back to 512 when it is absent.

### Fix

Rewrite the comment to name the `MSG_OK_READY` ack as the transport. Check the "1022" figure against
the value `_calculate_buffer_size` really returns before keeping it.

## `update_version.py --set-version` does not enter beta mode

*`2026-09-24-update-version-set-version-ignores-beta-mode.md` · date: 2026-09-24 · area: release tooling · priority: major*

`firestarter_app/.github/scripts/update_version.py`'s `--set-version` help text calls it an "Alias
for BETA_VERSION env var". The env var turns on beta mode (`is_beta_mode`, `:61`). The alias does
not: `is_beta_mode` never reads `args.set_version`.

Run `update_version.py --set-version 3.0.0b50` on a ref other than `beta`, without `--beta` or
`BETA_VERSION`. It takes the STABLE branch (`:181-199`), discards the requested version, increments
the patch, and writes a stable `X.Y.(Z+1)` into `firestarter/__init__.py` and `$GITHUB_OUTPUT`.

**Why this matters more than its size.** The script is on the publish path. PyPI never accepts
the same version twice, and a stable release is operator-gated (root `CLAUDE.md`). No test covers
the script (`grep -rl update_version tests/` is empty), and it is outside every CI gate. v1.41
Phase 207.1 D-12 touched the file, but only to reformat it.

**Needs an operator decision:** fix it, or move it to the backlog. The v1.41 re-audit recorded it
as open for that reason.

### Fix

Treat an explicit `--set-version` as a beta request, or refuse the combination:

```python
def is_beta_mode(args) -> bool:
    if args.beta or args.set_version:
        return True
    ...
```

Add a test that runs the script with `--set-version` on a non-beta ref and asserts that either a
beta version or a refusal is the result, never a stable patch bump.

### Status (2026-09-24)

The code fix is in `firestarter_app` `11c9a8c`. `is_beta_mode` now returns True for an explicit
`--set-version`. A manual `--dry-run --set-version 3.0.0b99` run on a non-beta ref printed
`3.0.0b99`. The automated test that this todo asks for is not written yet. That test is the only
open item.

## `firestarter_fw` issue template still names the old `firestarter_prom` repo

*`2026-09-27-fw-issue-template-still-names-firestarter-prom.md` · date: 2026-09-27 · area: repo hygiene · priority: minor*

`firestarter_fw/.github/ISSUE_TEMPLATE/config.yml:4` points the "Central Firestarter issue
tracker" contact link at:

```
https://github.com/henols/firestarter_prom/issues/new/choose
```

Stale on **`main`, `beta` and `release/3.1.x`** — all three. `firestarter_app`'s copy of the same
file already names `henols/firestarter`, so the two sub-repos disagree.

### Not urgent, and here is why

The old name still resolves: `henols/firestarter_prom/issues` returns **301** and lands correctly
on `henols/firestarter/issues` (measured 2026-09-27). Nothing is broken for anyone clicking it.

But a GitHub rename redirect is not a guarantee. It stops working permanently the moment anyone
creates a new repository named `firestarter_prom`, and the link sits in the issue-creation UI —
the one place a new contributor meets the project.

### Why it is a todo rather than a PR

Neither route is free for a one-line docs change:

- **Push to `beta`** publishes a firmware pre-release. `beta-build.yml` has no path filter, so a
  documentation-only push still cuts a release and burns a version number.
- **Push to `main`** fires `build.yml`, the stable publisher. `config.yml` is not covered by its
  `**.md` paths-ignore, so it is not skipped. The job currently dies at the version bump (GH013,
  rejected by the `Protect main` ruleset), so it publishes nothing — but it does go red.

### How to apply

Fold the one-line change into the **next `beta` change that is happening anyway** for other
reasons, so it rides along at zero extra cost. Then it flows to `main` and `release/3.1.x` by the
normal promotion path.

Two of PR #67's three hunks — `README.md` and `.github/CONTRIBUTING.md` — already landed via the
sibling branch `fix/point-at-firestarter-beta`. Only `config.yml` remains. Do not resurrect #67
wholesale; it was measured from a 2026-09-15 merge base and its other two hunks are no-ops now.

## AT28C256 write-path failure (gh#20) — blank-check/write/verify all BAD on Rev 2.3

*`at28c256-write-path-failure-gh20.md` · date: 2026-08-04 · priority: medium*

**Owner: henols** (the repo owner/operator). Named explicitly and deliberately, so this does not
become another unowned acknowledgement — the same failure mode this project's own backlog has
flagged before (v1.30's `write-sdp-relock-deferred.md` and the RELOCK pair carry the identical
discipline). May be reassigned to whoever is best positioned to obtain a bench sample or correspond
with the reporter.

### The symptom, as reported

[gh#20](https://github.com/henols/firestarter_prom/issues/20) — OPEN since 2026-07-30, title
`[dev test] at28c256 — FAIL (00e121446ceb)`, 0 comments. Measured facts (re-verified read-only
2026-08-04, unchanged since filing):

- host `3.0.0b14`, `hw_revision Rev 2.3`, chip `at28c256`, protocol `13`
- `blank-check`, `write`, and `verify` steps **all BAD** — the write step's fingerprint is
  `indeterminate`, meaning the read-back neither matched the expected pattern nor classified as a
  recognizable degenerate shape (blank/contact, address-line, transport)
- `id` step is `NA` (no chip-id in this DB entry — expected, `AT28C256` has none), `erase` is `NA`
  (protocol `0x0D` has no erase operation)
- voltage `vpp 11800 mV` / `vpe 13700 mV`, before == after both directions — no droop observed
  across the run
- `dedup_fingerprint 00e121446ceb`; `db_diff`: `current_support_status: supported`,
  `proposed_disposition: suggests community-fail signal`, `ladder_state: community-fail`

### What this phase (v1.30 Phase 134) established, and what it did not

Phase 134's `dev test` SDP leg was **triaged against this bench** (see
[`134-GH20-TRIAGE.md`](../../phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-GH20-TRIAGE.md)):
under the new baseline-transition gate, `write-baseline-b` would itself report BAD on this bench,
the gate would close, and **no SDP lock would ever be emitted** against this part — the mechanism
that prevents "lock a part whose baseline write never worked" is what this milestone shipped.

**This does NOT diagnose the chip.** The Evidence Ceiling (`133-RECORD.md` §6, restated in the
triage artifact) applies here without softening: no fixture in this milestone simulates real SDP
inhibition, and this triage does not establish *why* the write path failed on this specific bench —
only what the tool would now correctly *do* about it (refuse to lock, render the drop visibly).
Candidate causes not distinguished by the report alone: a genuinely SDP-locked die with no
supported unlock path reached, a marginal/failing VPP rail at the measured 11.8 V, a contact fault
not caught by the blank-check's own classification, or a firmware/host protocol mismatch on this
specific board revision (`Rev 2.3`). Diagnosing between these needs either the reporter's continued
engagement (a follow-up `dev test` at a different VPP, or with an oscilloscope on the write strobe)
or a bench sample the maintainer does not currently have.

### What is owed

1. **The public reply to gh#20 is Phase 137's** (CLOSE-06), behind its blocking operator
   wording-review gate, alongside the gh#12 reply. Nothing in this todo, or in `134-GH20-TRIAGE.md`,
   is posted anywhere — this item and its sibling artifact exist so the finding is recorded rather
   than silently dropped, per D-16.
2. **The underlying defect itself** — whether `AT28C256`/Rev 2.3 boards have a real, reproducible
   write-path problem, and if so what causes it — remains open and unowned by any phase in this
   milestone. Named here with an owner so it is tracked rather than lost.
3. **May be reassigned** — `henols` is named as the repo owner/operator, not necessarily as the
   engineer who will investigate; reassignment to whoever picks this up is expected and fine.

### Related

- [`134-GH20-TRIAGE.md`](../../phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-GH20-TRIAGE.md)
  — the full triage finding (LEG-18).
- `134-CONTEXT.md` D-16, D-11 — the decision record for why this is triaged-not-fixed and why the
  `dedup_fingerprint` orphaning is an accepted, recorded cost.
- `.planning/todos/pending/gh12-followup-after-dev-sdp-retirement.md` — the sibling outward-facing
  follow-up this milestone also owes Phase 137, under the same operator wording-review gate.
- ROADMAP `## Backlog` — Backlog **999.29** cross-links this item.

## avrdude MCU-detection fallback for blank-chip / wrong-firmware recovery

*`avrdude-mcu-detection-fallback.md` · date: 2026-05-21 · status: pending · priority: low · type: enhancement*

### The idea

Add an avrdude-based MCU-detection fallback to `firestarter_app/firestarter/firmware.py` so the host CLI can flash the right firmware even when the device's firmware handshake fails (blank chip, pre-1.0 firmware, wrong firmware previously flashed). Today the install flow requires the device to handshake and self-report its `board` string — no handshake means no install.

### Empirical basis (bench-verified 2026-05-21)

`avrdude` requires `-p <partno>` to launch and cannot answer "what's connected?" in isolation, BUT if you pass the **wrong** `-p`, avrdude reads the chip signature from the bootloader on connect and names the actual part in stderr:

```
$ avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328p -n
avrdude error: connected part ATmega328PB differs in signature from -p ATmega328P
                              ^^^^^^^^^^^^^ ← regex anchor
```

Verbose mode also prints `(probably mXXX)`:

```
$ avrdude -c urclock -P /dev/ttyUSB0 -b 115200 -p m328pb -n -v
avrdude: device signature = 0x1e9516 (probably m328pb)
```

Either parse path works. Confirmed live on the operator's 328PB-Uno (`/dev/ttyUSB0`, Urclock bootloader).

### Why deferred (not Phase 23 / not v1.5)

- The happy path — device handshakes, reports `board: uno328pb`, host flashes `firestarter_uno328pb.hex` — already works end-to-end at the firmware layer (Phase 23 D-15 + bench validation 2026-05-21).
- Adding detection now would expand v1.5 scope beyond the milestone's "third board target" framing. CONTEXT D-11 (Phase 23) explicitly bounded the edit surface to one elif branch + argparse widening.
- This is a v1.6+ "recovery / diagnostics" feature, not a "third board" feature.

### Sketch (for whoever picks this up)

```python
def detect_mcu_via_avrdude(port: str, programmer: str = "urclock", baud: int = 115200) -> Optional[str]:
    """Probe the connected MCU via avrdude. Returns lowercase partno (e.g. 'atmega328pb') or None."""
    result = subprocess.run(
        ["avrdude", "-c", programmer, "-P", port, "-b", str(baud), "-p", "m328p", "-n"],
        capture_output=True, timeout=10
    )
    stderr = result.stderr.decode("utf-8", errors="replace")
    # Route 1: "connected part ATmega328PB differs in signature"
    m = re.search(r"connected part (\w+)", stderr)
    if m:
        return m.group(1).lower()
    # Route 2: "device signature = 0xNNNNNN (probably mXXX)"
    m = re.search(r"\(probably (m\w+)\)", stderr)
    if m:
        return m.group(1)
    return None
```

Then a `firestarter fw -i --detect-mcu` flag would call this when the firmware handshake fails, map the partno back to a board name, and proceed with the matching `.hex`.

### Two real scenarios this unlocks

1. **Blank-chip / pre-1.0-firmware recovery** — operator has a virgin 328PB-Uno with only the Urclock bootloader. Today: `firestarter fw -i` bails because handshake fails. With detection: probe → `atmega328pb` → flash `firestarter_uno328pb.hex` → done.
2. **Wrong-firmware diagnostic** — operator accidentally flashed `firestarter_uno.hex` onto a 328PB. Handshake reports `uno` (the firmware's `RURP_BOARD_NAME` literal), but the silicon is 328PB. Today: host obediently re-flashes `firestarter_uno.hex`, leaving the diagnostic gap intact. With detection: compare handshake-board vs probed-MCU, warn on mismatch.

### Open questions for the eventual implementer

- Which programmers besides `urclock` does this work with? `arduino` (stk500v1) probably reports signature too — needs probing per-board.
- Where to put the partno → board-name reverse map? `(atmega328p → uno, atmega32u4 → leonardo, atmega328pb → uno328pb)` — could live in `firmware.py` constants or as a mirror of the existing forward map.
- UX: silent fallback vs explicit `--detect-mcu` flag? Probably explicit — silent fallback could mask real handshake bugs.

### Cross-references

- Phase 23 CONTEXT D-15: defers real-silicon verification to Phase 24 (now bench-validated 2026-05-21)
- Phase 23 D-11: bounds Phase 23 edit surface; this idea is explicitly outside that surface
- Memory `project-bench-findings-v15`: operator's specific bootloader is Urclock @ 115200
- `firestarter_app/firestarter/firmware.py:_install_with_avrdude` — the function this would extend

### 2026-08-27 annotation (v1.34 Phase 160)

Phase 160 (v1.34, RIG — Dual-Arm Build, Flash Provenance & the Shared Cell Procedure) reused
this idea's bench-verified avrdude signature-probe mechanism (the deliberately-wrong-`-p`
route and the verbose `(probably mXXX)` fallback route described above) in a **phase-owned
rig tool**, `.planning/milestones/v1.34-artifacts/tools/probe_board.py` — RIG-02's "board identity by signature,
never by handshake" requirement is built directly on the two parse routes sketched in this
todo. This is mechanism reuse only: the tool lives under the meta-repo's own
`.planning/milestones/v1.34-artifacts/tools/`, is invoked by this milestone's bench procedure, and is never
imported by or copied into `firestarter_app/`.

This phase does **not** build this todo's product deliverable — a `firestarter fw -i
--detect-mcu` flag in `firestarter_app/firestarter/firmware.py` — because that would be a
product-code change untraceable to a v1.33-caused regression, and `REQUIREMENTS.md`'s Out of
Scope table forbids exactly that class of change for this milestone. This todo's `status` and
`resolves_phase` fields are left unchanged by this annotation: the product-side flag remains
unbuilt and unowned by any phase.

## Add a frame-level deadline to the firmware COBS decoder byte-wait (WR-01)

*`cobs-decoder-framelevel-deadline-wr01.md` · date: 2026-06-01 · status: pending · priority: medium · type: enhancement*

### The issue

Phase 50 deliberately removed the per-byte `timeout_ms = 2000` loop from
`firestarter/src/boards/rurp_serial_utils.cpp` (it was the SC1 cascade source — len_u16
corruption → wrong-length read → 2 s timeout per chunk). The replacement decoder waits for
bytes with an **unbounded** spin: `while (rurp_communication_available() <= 0) {}` (decoder
byte-wait ~line 125 and `_drain_to_delimiter` ~lines 92-98).

Consequence: if the host disconnects mid-frame, the firmware spins **forever** instead of the
old 2 s. The Phase 50 plan (D-01/D-03) assumed incomplete frames would be "governed by existing
op-level timeout machinery," but the decoder blocks inside `rurp_communication_read_data` and
never returns `OP_MSG_INCOMPLETE`, so that machinery is never reached.

Verifier classification (50-VERIFICATION.md): real residual risk but **does not defeat any
Phase-50 must_have** — it is a clean hang, not a corrupt transfer, and the 2 s *cascade* source
is gone. Classified advisory/deferred.

### The fix (proposed)

Reintroduce a timeout at the **frame level** (a single `millis()`-based deadline across the whole
frame read + drain), NOT a per-byte 2 s loop — so a stalled/disconnected host returns an error and
lets the op layer recover, without re-creating the per-chunk cascade that Phase 50 eliminated.
Pick a deadline generous enough not to trip on normal inter-byte gaps at 250000 baud.

### Where

- `firestarter/src/boards/rurp_serial_utils.cpp` — decoder byte-wait + `_drain_to_delimiter`.
- Add a firmware Unity case (truncated frame → bounded error return, no hang) under
  `firestarter/test/native/avr/test_cobs_data_frame/`.

Candidate landing: Phase 51 (command-channel framing migration) or a Phase 50 follow-up, operator's call.

## dev test / dev write-cycle verify connects are not port-pinned

*`dev-test-verify-connect-unpinned.md` · date: 2026-09-21 · priority: medium*

Phase 203's CR-01 fix (`0fc6c77`, firestarter_app) pins the guard read, the write, and
`firestarter write --verify`'s read-back to one resolved port for the invocation.

`chip_test.py`'s own `verify_eprom` calls, used by `dev test` and `dev write-cycle`, do NOT pass
`preferred_port`, so they still re-run discovery and can land on a different board than the write
they are verifying. They inherit guard+write pinning for free (that is internal to `write_eprom`),
so the unpinned leg is the verify connect only.

Lower severity than CR-01 because `dev test` is a validation command, not an operator write path,
and a wrong-board verify reports a false mismatch rather than causing an irreversible write.

Fix: thread `preferred_port=<the write's resolved port>` into `chip_test.py`'s `verify_eprom`
calls, the same way `cli_handlers.write` does via `last_write_port`.

Deliberately out of scope for 203 — that phase's authorised fix was CR-01 on the
`firestarter write` path.

## dev test's fixed 256-byte write region refuses on the two protocol 0x05 parts with page size 512

*`dev-test-write-region-rounds-to-page-size.md` · date: 2026-09-16T02:00:00+02:00 · area: host*

### Problem

`dev test`'s chip-test engine writes a fixed 256 bytes at address 0 for every non-UV part
(`_WRITE_REGION_START = 0`, `_WRITE_REGION_LENGTH = 256`). Measured directly against
`chip_database.json`'s 27 protocol-`0x05` rows: this is a whole number of pages -- and therefore
unaffected by Phase 195's alignment refusal -- for **25 of 27 rows** (page size in `{64, 128,
256}`), including all three protocol-`0x05` validated parts (`W29C020`, `W29C040`, `AE29F2008`).
It becomes a **refused partial page** on the remaining **2 of 27 rows**, both recording page size
512: `AT29BV040,AT29LV040` and `AT29C040`. Neither of those two parts has ever been tested on
silicon.

### Why Phase 195 did not fix this

Changing the write region's length changes what every community validation run measures --
`dev test`'s region is what every `dev test` submission against a protocol `0x05` part actually
exercises. That is a ledger-affecting decision with consequences for every future `dev test` run,
not a safety fix, and it must not ride along with the alignment-refusal change that landed in
Phase 195. Folding it in would have made one commit responsible for two different kinds of
correctness: "the write can no longer erase bytes outside its range" and "what `dev test` measures
changed."

### The proposal

Round the write region's length up to the part's recorded page size, where one is recorded, rather
than using a hard-coded 256 for every part. For the 25 rows already at a page size dividing 256
this is a no-op; for the 2 rows at page size 512 it would extend the region to 512 bytes so the
fixed-region write stays aligned under Phase 195's refusal.

### Filed by

Phase 195 (partial writes stop destroying the page), D-12, Plan 04.

### Closed by

## Fix JP4 labels + Rev-2 revision block in info jumper display

*`fix-jp4-labels-and-rev2-revision-block.md` · date: 2026-07-02 · priority: medium*

Safe, self-contained display fix. **No chip-database or firmware change** — does
NOT attempt to add the 3rd-position / 2516 support (that's the seed
`rev22-3pin-header-2516-family-support.md`).

### Split history (recorded 2026-09-10, Phase 182 Plan 07)

This todo carried three items and was **split** during Phase 182 (JP5 Destructive-Operation Gate):

- **Item 3 (delete the dead renderer) landed in Phase 182, 2026-09-10, as SAFE-05.** See
  `.planning/phases/182-jp5-destructive-operation-gate/182-04-SUMMARY.md` — `_get_rev2_2_jumper_settings_data`
  and its commented-out call site are deleted (`firestarter_app@2a9a335`). That work is done; item 3 below
  is retained only as a historical record of what Phase 182 resolved.
- **Items 1 and 2 move to the backlogged D-09 work, filed as `.planning/ROADMAP.md` Phase 999.58** (this
  todo's `resolves_phase` is re-pointed there accordingly). That phase does not exist yet — Phase 187
  (Answered Reports) must stay last in the v1.37 milestone, so a phase carrying this scope slots before it,
  which is an operator scope decision rather than a planner's to make. See Phase 999.58 in `ROADMAP.md` for
  the full backlog stub, including the three enlargements Phase 182 discovered to this job.
- **Both items 1 and 2's premises are corrected below**, dated 2026-09-10, with their evidence — the D-09
  work inherits the corrected premise rather than the one this todo originally carried.

### Scope

In [ic_layout.py:169-183](../../../firestarter_app/firestarter/ic_layout.py#L169-L183)
(`_get_rev2_jumper_settings_data`):

1. **Fix JP4's copy-paste labels.** `config_text` and `pin_text` are currently
   `"28pin"` / `"32pin"` (cloned from JP3) and render as meaningless text. JP4 is
   the VPP bypass jumper — its meaningful values are Open / Closed. Give it
   labels that describe VPP-on-pin-1, not pin count.

   **Corrected 2026-09-10 (Phase 182, D-10):** the standard to write to is still JP4's own
   silkscreen parenthetical — *"Only for ROMs with VPP on P1"* — but the clause beside it on the
   same silkscreen, *"Open for 32 pin ROMs, Closed for 28 pin ROMs"*, is **two-state language on a
   three-pole jumper and must NOT be reproduced** in the rewrite. On Rev 2.2 and later the existing
   `"28pin"`/`"32pin"` labels this item targets for removal are not merely meaningless, as originally
   stated — they are **wrong**: JP4 has a third position (the 24-pin pole, added at Rev 2.2) those two
   labels cannot express at all. Evidence: `.planning/phases/182-jp5-destructive-operation-gate/evidence/shield-rev2.2-jp4-jp5-jp6-jp9.jpg`
   (the silkscreen photograph) and `.planning/notes/jumper-display-ground-truth.md`.

2. **Relabel the Rev-2 block** from `"2.0 & 2.1"` to cover all four revs that
   share this JP4 header: `"2.0, 2.1, 2.2 & 2.3"` (WRONG, corrected 2026-09-10 below — original
   premise was: operator confirmed 2.2/2.3 have the same JP4, plus a 3rd angled pin handled
   separately by the seed).

   **Corrected 2026-09-10 (Phase 182, D-10):** this premise is now known wrong in a way that
   matters. Rev 2.2's JP4 is a **three-pole selector**, not the two-pin header Rev 2.0/2.1 carry, and
   the footprint change is at **Rev 2.1 → Rev 2.2** — not Rev 2.2 → Rev 2.3 as this item originally
   assumed. A single block covering revisions 2.0 through 2.3 therefore cannot describe all of them:
   2.0/2.1 share a 2-pin header state (2 values), 2.2/2.3 share a 3-pole state (3 values). Evidence:
   Rev 2.2's own pick-and-place CSV
   (`.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/Rev2.2/W27C512Programmer-top-pos.csv`:
   `"JP4","P1_VPP_JMP","PinHeader_2x02_P2.54mm_Vertical"`) against Rev 2.1's
   (`.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/Rev2.1/W27C512Programmer-top-pos.csv`:
   `"PinHeader_1x02_P2.54mm_Vertical"`), and the JP4 KiCad symbol
   (`.planning/milestones/v1.7-artifacts/upstream-rurp/hardware/RelativelyUniversalROMProgrammer.kicad_sch:22555-22620`,
   `Description "Jumper, 3-pole, both open"`). **The new block structure (how many blocks, which
   revisions in each) is left for the D-09 work (Phase 999.58) to design** — not decided here.

3. **Delete the dead `_get_rev2_2_jumper_settings_data`** method — **DONE 2026-09-10, Phase 182 SAFE-05**
   (`firestarter_app@2a9a335`, guarded by a `hasattr` deletion test and a positive survivor test for the
   live JP4 sibling — see `182-04-SUMMARY.md`). It invented a phantom "JP5" solder-jumper setting as an
   operator-settable Rev 2.2 config header, which does not exist on the hardware; the method and its
   commented-out call site are gone. *(Original citations, now stale since the deletion removed the
   lines: the method was at `ic_layout.py:186-201`, the commented call site at `ic_layout.py:656`. Both
   are rewritten here as this past-tense reference to the removing commit, per this project's citation
   hygiene rule — a citation to deleted lines is not "repaired" forward, it is replaced with the commit
   that removed them.)*

### Acceptance

Items 1 and 2 (still open, D-09 work):

- `firestarter info <a 28-pin UV-EPROM>` prints a JP4 line with sensible
  Open/Closed labels (no "28pin, 32pin"), checkable against JP4's own
  "Only for ROMs with VPP on P1" standard, and not reproducing the two-state
  "Open for 32 pin ROMs, Closed for 28 pin ROMs" clause.
- The Rev-2 jumper block(s) correctly describe 2.0 through 2.3, with the
  2-pin/3-pole split the corrected premise above requires — exact block
  structure is the D-09 work's to design.

Item 3 (done):

- No `_get_rev2_2` / phantom-JP5 references remain — confirmed 2026-09-10 (`182-04-SUMMARY.md`).

Whole file, at close of the D-09 work:

- Existing tests + ruff/format/mypy gate stay green.

### Context

See `notes/info-jumper-display-design-audit.md` for the full audit, and
`.planning/phases/182-jp5-destructive-operation-gate/182-CONTEXT.md` § "Folded Todos" and § D-10…D-15
for the split and correction history recorded above.

## FM1608 byte 0 write never lands — register cache-skip elides all three shift-register strobes

*`fm1608-byte0-write-never-lands-register-cache-elision.md` · date: 2026-08-09 · status: pending · area: firmware · priority: medium*

Carried out of the `fm1608-fresh-chip-baseline` debug session, parked since 2026-05-18
awaiting hardware. Keeping it as a debug session made it a permanent milestone-close
blocker; it is a tracked defect with a strong hypothesis, so it belongs here.

### Symptom

On FM1608, byte 0 retains its factory `0xFF` across every write attempt while bytes
1..N-1 program correctly.

### Hypothesis H1 (well-supported, not yet confirmed on silicon)

`rurp_write_to_register` in `firestarter/include/rurp_register_utils.h` early-returns when
the cached value equals the value being written. On the **first** `memory_set_data(0, byte0)`
call, all three shift-register writes (LSB, MSB, CONTROL) are cache hits, so **no clock
strobe fires at all**:

- After `command_done`, cache == HW == `LSB=0, MSB=0, CONTROL=0`.
- `configure_memory` calls `mem_util_set_address(handle, 0)` → LSB=0 (skip), MSB=0 (skip),
  CONTROL=`0x10` from `ADDRESS_LINE_17` (cache `0 → 0x10`, strobes).
- First `memory_set_data(0, byte0)` recomputes the same targets — LSB=0, MSB=0,
  CONTROL=`0x10` — **all three skipped, zero strobes**.

On paper the shift register should still be holding `0/0/0x10` from the previous strobes, so
the write ought to land. Empirically it does not, which points at a timing/state dependency
requiring a strobe immediately before the data CE pulse.

**Why bytes 1..N work:** for byte 1 the LSB goes `0 → 1`, so a strobe always fires; every
later address differs in LSB too.

### Already falsified

- Three uniform writes (`0x00`, `0xAA`, `0x5A`) — byte 0 stays `0xFF`, bytes 1..8191 take
  each pattern. Refutes "byte 0 holds a stale value from a prior write".
- Triple-read after a single write — byte-identical across reads, so reads are deterministic
  and not the source of variance.
- Single-byte write with `-a 0` — byte 0 still `0xFF`; the path triggers even for a 1-byte chunk.

### Note on test coverage

This is the same register-write-elision mechanism that the native trace stubs are known to
miss unless `rurp_register_utils.h` is included in the host stubs. A native trace test that
does not model the elision **cannot** reproduce this bug — any test written for it must
assert on strobe counts, not just final register values.

### Next step when a chip is available

Instrument strobe counts around the first `memory_set_data` on a seated FM1608 and confirm
zero strobes fire; then test the candidate fix (force a strobe on the first data write of a
block, or dirty the cache at block start) and confirm byte 0 programs.

## Fold response_code into the handler-layer log macro (derive from ID band)

*`fold-response-code-into-log-macro.md` · date: 2026-07-28 · status: pending · priority: medium · type: refactor*

Every handler in `firestarter/src/proms/` hand-writes the same two-line pair —
29 times:

```c
LOG_ERROR_ID_U32(MSG_ERR_MEM_SIZE_TOO_SMALL, (uint32_t)handle->mem_size);
handle->response_code = RESPONSE_CODE_ERROR;
```

Nothing enforces that the two agree. A site can log ERROR and set WARNING, or
log and forget the store entirely, and it compiles clean. This is the fail-safe
path (VPP checks, chip-ID mismatch, verify, blank-check), so a silent
severity/response divergence is the wrong defect class to leave representable.

### Fix

Add a handler-scoped macro family that takes the handle explicitly and derives
the response code from the message ID's severity band (WARN `0x80-0x9F`,
ERROR `0xA0-0xDF`):

```c
LOG_RESP_ID_U32(handle,
    is_flag_set(FLAG_FORCE) ? MSG_WARN_MEM_SIZE_TOO_SMALL : MSG_ERR_MEM_SIZE_TOO_SMALL,
    (uint32_t)handle->mem_size);
```

Full design, grounding facts, and the four decisions (explicit handle; derive
from ID band not macro name; codegen emits the band constants and asserts
`severity` ↔ band; DATA band must not map) are in
`.planning/seeds/logging-macro-derives-response-code.md`.

### Scope

- 29 call sites, all under `src/proms/` — all mechanical (the nested blocks
  around the log calls are `_b[]` scope, not conditionals).
- Do **not** touch the 16 sites outside `src/proms/`. Those signal failure by
  return value, and `_check_response()` (`src/operation_utils.cpp:330-351`)
  resets `response_code` to OK after every callback, so a store there is dead.
- `messages.h` is codegen-generated — band constants go in
  `tools/catalog/codegen.py` + `messages.toml`, never hand-edited.
- Existing native suites already assert `h.response_code` on locally
  constructed handles; they are the regression net.

### Sequencing

Blocked on Phase 117 (remap-aware 0x0D emitter + honest completion signal),
which is actively rewriting `eeprom_28c.cpp`. Land that first.

## FM28V020 and MB85R256H (FRAM) ride the 0x0D EEPROM handler by pinout promotion -- a classification question

*`fram-parts-ride-the-0x0d-handler-by-pinout-promotion.md` · date: 2026-08-19T02:00:00+02:00 · area: host*

### Problem

Two FRAM parts reach `configure_eeprom28c()` (protocol `0x0D`) purely through `classify()`'s
pinout-promotion arm 2 (`firestarter_app/tools/build_db.py:371-386`), the same mechanism the
`promoted-0x0d-rows-keep-the-64-byte-floor.md` todo covers for page-size purposes. This is filed
as a **separate** todo deliberately: it is a **classification question** (should these parts be
routed to the 28C EEPROM handler at all), not a page-size question.

### The two parts (measured)

- **CYPRESS `FM28V020`** -- upstream `protocol_id 0x07`, upstream `page_size 128`, `vcc_mv 5000`,
  `vpp_mv 12000`.
- **FUJITSU `MB85R256H`** -- upstream `protocol_id 0x07`, upstream `page_size 256`, `vcc_mv
  3300`, `vpp_mv 12000`.

Both are typed `EEPROM` in the database and both reach the `0x0D` handler by the same
`DIP28_28C64`/`DIP28_28C256`-pinout promotion described in the sibling todo above.

### Why this is a genuine question, not a bug

FRAM (ferroelectric RAM) has **no page buffer and no internal write cycle** -- every byte write
completes immediately and independently, unlike true 28C EEPROM's page-write-then-poll model.
A delivered `page_size` would therefore be **meaningless** for these two parts: there is no
buffer boundary for it to describe. D-01's provenance rule (deliver only where the upstream
record's own `protocol_id` is `0x0D`) already **excludes both of these parts by construction** --
neither carries an upstream `0x0D` record, so neither is a D-01 mover -- which is the concrete
harm the provenance rule was built to prevent. What D-01 does *not* answer is the prior
question: should these two parts be dispatched to `configure_eeprom28c()` at all, given they are
electrically FRAM, not EEPROM? `MB85R256H`'s 3.3 V `vcc_mv` also makes it electrically distinct
from the 5 V 28C family the handler was designed around.

### What would close it

An independent classification pass over the database's FRAM-typed parts that reach `0x0D` by
pinout promotion, to decide (a) whether they should be re-typed/re-routed to a dedicated FRAM
path, or (b) whether riding the existing EEPROM handler is electrically harmless for FRAM and can
stay as-is with the classification simply documented. Not attempted in this phase -- no FRAM part
exists in operator inventory (Evidence Ceiling, `PROJECT.md` §Current Milestone: v1.32) and the
question is orthogonal to the page-size seam this phase delivers.

### Filed by

Phase 149 (dual-repo lockstep), D-04 deliverable 2, Plan 07.

## Restore unaligned protocol 0x05 writes by splicing the head and tail page host-side before an aligned write

*`host-side-page-alignment-splicing.md` · date: 2026-09-16T02:00:00+02:00 · area: host*

### Problem

Phase 195 shipped a two-layer refusal (host pre-flight predicate plus firmware per-chunk guard)
for protocol `0x05` writes whose start address or payload length is not a whole multiple of the
part's page size. This is correct and necessary -- the part's own datasheet states the page erase
is implicit, whole-page and unconditional, so any byte not loaded when the page commits is erased.
But it also means patching part of a ROM image with an unaligned start address -- a normal
operation an operator does routinely -- now refuses outright where it previously silently erased
neighbouring bytes. Phase 195 measured and accepted that regression rather than build a fix for it
(`.planning/milestones/v1.39-artifacts/195-partial-write-refusal-record.md` §4); this todo is the deferred strand that
would restore the capability.

### The shape

Read the head page and the tail page of the target range through the existing region-read
primitive, splice the caller's payload over them in memory, and issue a single page-aligned write
covering the full spliced range. The firmware guard from Phase 195 stays in place unconditionally
as the backstop -- this strand only ever produces host-side inputs the guard already accepts.

### The three facts that make it tractable

1. It needs **no firmware RAM** -- the splice buffer lives in Python on the host, not in the
   firmware's constrained AVR memory. Phase 195's own measurement (a 512-byte firmware staging
   buffer leaves 142 bytes of RAM on `uno` and 213 bytes on `leonardo` for the whole call stack)
   is what ruled out doing this in firmware at all.
2. It works at **every page size the database carries, including 512** -- the two parts Phase 195
   found un-bench-tested at that geometry are exactly the case a host-side splice does not need to
   special-case, because the read-splice-write shape does not depend on the page fitting in any
   fixed-size buffer.
3. The region-read primitive this needs already exists and is already used this way by the
   chip-test engine (`chip_test._read_region`), so this strand extends an existing, tested
   capability rather than opening a new one.

### Two honest caveats

- **A read failure must abort rather than proceed.** If the host cannot read back the head or tail
  page before splicing, it must not fall back to writing an incomplete page -- that would silently
  reintroduce the exact defect Phase 195's refusal exists to prevent.
- **The region-read's accuracy should be verified explicitly before anything is built on it.** This
  strand's correctness depends entirely on the read primitive returning the true current contents
  of the page; that assumption should be tested directly, not assumed because the primitive is
  already used elsewhere.

### What would close it

A plan that implements the read-splice-write shape in `eprom_operations.py`, wired behind the same
call sites `require_page_alignment` uses today, with the firmware guard left untouched as the
backstop, and a native/host test matrix proving the splice is byte-correct at every page size the
database carries plus the two honest caveats above.

### Filed by

Phase 195 (partial writes stop destroying the page), D-01/D-03, Plan 04.

### Closed by

## New host / old firmware skew corrupts the 9 previously under-sized 0x05 parts silently

*`new-host-old-firmware-0x05-page-size-skew.md` · date: 2026-09-15T02:00:00+02:00 · area: both*

### Problem

Phase 194 (D-12) delivers a per-chip `page_size` on the wire for every protocol `0x05` part and
makes the firmware refuse a write when it cannot resolve one. The host does **not** gate a
protocol `0x05` write on the connected firmware's version. Deliberately, per D-12: the host
already sends `page-size` on every write today with zero code change (Phase 149's seam), and
adding a version gate for this phase's fix would be a separate, unbounded piece of work.

### The mechanism

A host carrying this phase's database resolves the real page size (e.g. `128` for `AT29C512`, one
of the 9 previously under-sized parts) and sends `page-size: 128` on the wire. Firmware older than
this phase (pre-`194-01`) has no `page_size` consumer on the `0x05` write path: it silently ignores
the field and re-derives the old, wrong capacity-bracket value (`64` for `AT29C512`). The result is
exactly the silent corruption this milestone exists to end (D-1) — a write against one of the 9
still corrupts every other page, the firmware never rejects it (the old code path has no refusal),
and the operator still sees `successful`.

This is a **regression path that only opens once the host is upgraded ahead of the firmware** — a
host at this phase's version, paired with firmware still at `3.0.0b22` or earlier. It does not
affect a host+firmware pair that upgrades together, and it does not affect any of the 18
already-correct parts (their derived and real pages already agreed).

### The caveat for whoever picks this up

**The host's own firmware version probe cannot resolve this precisely.** `_probe_port`'s version
regex (`[\d.x]+`) truncates the prerelease suffix, so the host cannot distinguish firmware `b11`
from `b12` from `b22` from whatever build first ships `194-01`'s consumption fix — only the
numeric `major.minor.patch` triple is visible to the host today. Any version boundary this fix
introduces must therefore be decided on the numeric triple alone, which means either:

- bumping to a new numeric version specifically to mark the boundary (a release-process decision,
  not a code change), or
- widening the probe to preserve the prerelease suffix first, so a boundary can be drawn precisely
  against a `b`-numbered prerelease instead of only a numeric release.

Neither is this phase's decision to make.

### What would close it

A host-side pre-write gate, keyed on the connected firmware's version (once precisely resolvable),
that refuses or warns before a protocol `0x05` write when the connected firmware predates the
`page_size`-consumption fix — mirroring the existing fail-closed pattern in
`firestarter/page_size_gate.py` (194-05) and `firestarter/flash4_erase_gate.py`, but keyed on
firmware version rather than on database content.

### Filed by

Phase 194 (real page size reaches the firmware), D-12, Plan 06.

## Lock pinouts.json against one-rom chip-types.json -- 3 families ARE the May-2026 defect fixes and nothing would notice them regressing

*`onerom-pinout-external-corroboration-gate.md` · date: 2026-08-20T02:00:00+02:00 · area: host*

### Problem

`firestarter/data/pinouts.json` holds all 15 pin-map families that every one of the 746
`chip_database.json` rows routes through. It is **hand-maintained** — `tools/build_db.py:23`
reads it as an *input*, so unlike `chip_database.json` it is not regenerated from
`infoic.xml` and gets no protection from the generator's decode tests. A wrong pin number
in a family silently mis-drives up to 255 chips (`DIP32_SST39SF040`), and the only oracles
we have today are (a) the datasheet, read by hand at authoring time, and (b) bench silicon,
which we have for a small fraction of families.

**This source has already caught two real defects here, and 3 families exist only because of
it.** On 2026-05-13 (meta `fd9efaea`) one-rom was cross-checked against our priority chips;
on 2026-05-20 (`a332464`) the findings were acted on. It found AT28C256 mis-routed to
`DIP28_2764` (needed 15 address lines, A14 at pin 1 not VPP, WE at pin 27 not PGM), and
SST39SF040 mis-routed to `DIP32_STD` with **pins 1 and 31 swapped** — which likely explained
a 2026-05-12 bench failure previously attributed to a dead chip. The fixes authored
`DIP28_28C256`, `DIP32_SST39SF040` and `DIP24_6116`, moving 92 database entries.

Those three families are **the fixes**, and nothing today would notice an edit silently
un-fixing one. A regression in `DIP32_SST39SF040` alone mis-drives 255 chips and reintroduces
a defect that already once looked like dead silicon.

The source itself: [One ROM](https://github.com/piersfinlayson/one-rom)
(RP2350 ROM-replacement, 345 stars, actively maintained) publishes
[`rust/config/json/chip-types.json`](https://github.com/piersfinlayson/one-rom/blob/main/rust/config/json/chip-types.json)
— 34 real chip types with DIP pin numbers per signal, in a schema that is a near-exact
match for ours: `address` ordered A0..An, `data` D0..D7, `control.{ce,oe,write}` with
polarity, `programming.{vpp,pgm}` pin, `power` VCC/GND, plus `size`/`pins`/`aliases`.

Its independence is the point:

- **Different lineage.** No relationship to `infoic.xml`. Authored from datasheets by a
  different maintainer for a different purpose.
- **Different validation oracle.** One ROM never programs a chip — it *emulates* one. Its
  bus maps are validated by the emulator working when plugged into real retro machines.
  That is in-circuit read-path evidence, orthogonal to our write-path bench evidence.
- **Blind spot is disjoint from ours.** It carries no VPP millivolts, no `pulse_duration_us`,
  no algorithm, no chip ID, no page size. It can only speak to the bus map — but the bus map
  is exactly the axis `pinouts.json` owns.

### Evidence already in hand

Full cross-check result, schema correspondence table, reproduction script and the
what-it-cannot-do limits live in
[`notes/onerom-pinout-external-corroboration.md`](../../notes/onerom-pinout-external-corroboration.md).
**Read that first** — it is the authoritative record; this todo carries only the summary the
gate needs, and the note must not be duplicated here.

Snapshot cross-checked: blob `56cb04ca91e66aef0fd15236cc357602367c2b05` (58601 bytes),
`main`, fetched 2026-08-20. Fields compared: `address-bus-pins`, `data-bus-pins`, `ce-pin`,
`oe-pin`, `rw-pin`, `vpp-pin`, `vcc-pin`, `gnd-pin`.

**Provenance matters and the gate must not pretend otherwise.** 12 families are byte-identical,
but only 8 of those agreements are *corroborating* — 3 are circular (pins authored from
one-rom) and 2 are ambiguous (authored the same day as the cross-check, commit message silent).
The circular ones are the most important to lock and the least meaningful to cite as
confirmation. Buckets:

| bucket | families | gate behaviour |
|---|---|---|
| **byte-identical, corroborating (7 + 1 semantic)** | `DIP24_2716`, `DIP24_2732`, `DIP28_27256`, `DIP28_27512`, `DIP32_STD`, `DIP28_JEDEC_SRAM_8K`→`28C64`, `DIP24_2816` — plus `DIP32_27C020` semantically | assert equality; may be cited as independent confirmation |
| **byte-identical, CIRCULAR (3)** | `DIP24_6116`, `DIP28_28C256`, `DIP32_SST39SF040` (292 chips) | assert equality — **this is the regression guard on the May fixes.** Must NOT be cited as independent confirmation |
| **byte-identical, ambiguous (2)** | `DIP28_28C64`, `DIP32_28C512_EEPROM` (`ff70920`, same day) | assert equality; label provenance-unresolved |
| **semantic agreement (1)** | `DIP32_27C020` — our `rw-pin: [31]` vs their `programming.pgm.pin: 31` | expected divergence, reason recorded |
| **non-comparison (1)** | `DIP28_2764` — 2764+27128 superset, pin 26 = A13 | expected divergence, reason recorded |
| **no counterpart (1)** | `DIP24_2532` | out of scope, stays single-sourced |

Pairing note the gate must get right: `DIP28_JEDEC_SRAM_8K` pairs with one-rom **`28C64`**
(8 KB, 13 lines, `nc-pin: [1, 26]`), **not** `62256` (32 KB) — our own `61256,62256` row routes
to `DIP28_28C256`. And their `control.write` is our **`rw-pin`**; we have no `we-pin` key, so a
pass looking for one reports 6 spurious mismatches that are all agreements.

Verified expected output of the reproduction script in the note: **12 AGREE, 2 DIFF**.

### What to build

A host-side corroboration test — no firmware, no hardware, no `chip_database.json` write.

1. **Vendor the snapshot** under `firestarter_app/tests/fixtures/` (or `tests/golden/`, to
   match the existing `chip_database_field_inventory.json` convention) with a provenance
   header recording upstream repo, path, blob SHA, and fetch date. Do **not** fetch at test
   time — the suite must stay offline and deterministic.
2. **Assert the 12 byte-identical families stay byte-identical**, and **carry the provenance
   label per family** so a future reader cannot mistake a circular agreement for independent
   confirmation. The 3 circular families are the highest-value asserts in the set.
3. **Pin the 3 non-agreeing entries as explicitly-expected divergences, each with its
   reason inline** — `DIP32_27C020` (semantic agreement via `programming.pgm`),
   `DIP28_2764` (2764+27128 superset), `DIP24_2532` (no counterpart). Expected-divergence entries must be enumerated, not skipped by a
   catch-all: a *new* family added to `pinouts.json` that has a one-rom counterpart and
   disagrees should fail, not fall through a wildcard.
4. **Do not auto-refresh the snapshot.** A drift-detection leg is fine (compare vendored
   blob SHA to a recorded expectation) but re-pointing at a newer upstream must be a
   deliberate, reviewed act — an upstream edit landing silently would invert the gate from
   "guards us" to "upstream now dictates our pin maps."

### Licensing

Resolved — **MIT**, safe to vendor with attribution (`Copyright (c) 2026 Piers Finlayson`).
Rationale and the two traps that will make a reviewer re-open it (GitHub reports
`NOASSERTION`; there is no root `LICENSE`, only `LICENSE.md`) are recorded in the note's
"three hard limits" section. Do not re-litigate from the API field.

### Why a gate on top of the note

The note records the corroboration; it cannot *enforce* it. "12 families agree" is a fact
that decays the moment someone edits a pin list —
and pin-list edits are exactly what this project does (`3659121`, `38b55d5`, `94ea3b5`,
`fa0c1a4` all touched `pinouts.json`). Related: [[reference_chip_database_schema_algorithm_pulse_duration]]
records that `chip_database.json` is generated and must never be hand-edited; `pinouts.json`
is the hand-maintained input that rule leaves unprotected.

## Phase 44 read-timing knobs (read_settling_us, read_strobe_us) are missing from json_parse's optional-key reset block

*`phase-44-read-timing-knobs-missing-json-parse-reset.md` · date: 2026-08-19T02:00:00+02:00 · area: firmware*

### Problem

Research Open Question 5 (149-RESEARCH.md). `firestarter_handle_t handle` is a single
file-scope global (`firestarter/src/firestarter.cpp:33`) with **no per-command `memset`** --
`json_parse` resets only its *optional* keys at the top of each parse, because the mandatory
keys are always overwritten by the current command. Phase 149 / D-05 added exactly this reset
for the new `page_size` field, on the reasoning that without it, a 128 parsed for one chip would
persist into the next command's chip if that command omitted `page-size` -- turning "absent means
64" false in practice.

**Measured (`firestarter/src/json_parser.c:83-100`):** the two Phase 44 read-timing knobs,
`read_settling_us` and `read_strobe_us`, are **not** in that reset block. This is the exact same
category of latent defect one field over -- it predates Phase 149 and Phase 149 does not
introduce it, but Phase 149's own D-05 fix makes its absence for these two fields conspicuous by
contrast (the reset block's own comment now says so explicitly, filed as this todo).

### Why this is not simply a page overrun

Both knobs treat `0` as "use the firmware default" (`read_settling_us == 0` -> no settling
delay; `read_strobe_us == 0` -> use the default 3µs), per
`firestarter/src/json_parser.c:358-359`. So the symptom of the missing reset is a **stale
non-zero knob value persisting into a later command** that did not specify one -- e.g. a read
issued with `read-settling-delay: 500` followed by a plain read for a different chip would
silently keep applying a 500µs settling delay -- rather than any buffer or address overrun. Lower
severity than the page-size case, but the same shape of bug.

### Deliberately not fixed in this phase

Adding the reset here would perturb
`firestarter/test/native/avr/test_read_timing/test_read_timing_params.cpp`'s
`test_read_timing_fields_default_zero_when_absent` test, which characterizes the current
(pre-fix) behaviour. A defect in this neighbouring field is its own change, with its own test
update, not a page-size phase's business.

### What would close it

Add `handle->read_settling_us = 0;` and `handle->read_strobe_us = 0;` to `json_parse`'s
optional-key reset block (`firestarter/src/json_parser.c:83-100`, immediately alongside the
existing `chip_id`/`page_size` resets), and update
`test_read_timing_fields_default_zero_when_absent` (and any sibling test asserting persistence
across commands) to match the corrected behaviour.

### Filed by

Phase 149 (dual-repo lockstep), research Open Question 5, Plan 07.

## Photograph operator's Modified Rev 0 board (Phase 31 follow-up #3)

*`photograph-modified-rev-0.md` · date: 2026-05-26 · status: deferred · priority: MEDIUM · type: documentation*

### ⏸ DEFERRED 2026-08-29 by operator direction — do not plan this

Operator directed on 2026-08-29 to **skip Rev 0 and defer it**. This todo is parked with **no target
milestone**. It is split out of backlog **999.42**, which now covers only the six unswept chips and the
two unswept shields; it is **not** a blocker on that item and must not be sized into a resumption of it.

Pick this up only if the operator puts the Modified Rev 0 board on the bench for some other reason.
Nothing downstream depends on it: firmware handles the board correctly today via the broad-bucket
`REVISION_2_0` + EEPROM override fall-through, regardless of how the rework landed.


### ⚠ STATUS UPDATE 2026-08-29 — v1.34 Phase 164 closed UNRUN; now carried as backlog 999.42

`resolves_phase: 164` is retained, but **Phase 164 never ran.** v1.34 closed early and scope-reduced
by operator direction on 2026-08-29; Phase 163 (cell B1) never put the board on the bench, so Phase
164 — which was scheduled to photograph it *while it was already out for B1* — never started either.

**Current home: backlog 999.42** ("Finish the v1.34 sweep — six chips, two shields, and the Rev 0
rework trace"). See `.planning/ROADMAP.md` §Phase 999.42 and `.planning/milestones/v1.34-artifacts/CLOSE-RECORD.md` §2.3.

**The third deferral in this todo's life** (Phase 31 → Phase 35 → post-v1.7 → Phase 164 → 999.42),
and the board is **still never physically inspected**. No photographs of it exist anywhere.
**Nothing here is discharged.** REV0-01 is NOT RUN. This todo is unchanged in scope: it still needs
the operator, the board in hand, and a camera. It is the hard blocker on its companion
`write-modifications-md-rework-trace.md`, which cannot proceed without it.

### The deferral

Operator photo session for the third on-hand RURP shield (Modified Rev 0 — hardware-bug-A/B rework with cuts + jumpers) was deferred from Phase 31 to Phase 35, then deferred again from Phase 35 to post-v1.7 per D-07. Rationale: the rework trace is independent of v1.7's detect-fw substrate. The operator's Modified Rev 0 board uses the EEPROM `hw_revision` override path regardless of how the rework cuts/jumpers landed; firmware detect logic does not depend on Modified Rev 0 specifics during v1.7 (broad-bucket `REVISION_2_0` + override fall-through cover all observed cases).

Phase 35 Wave 3 bench session (2026-05-26) discovered that the Modified Rev 0 board, after Plan 01 INPUT high-Z fix, lands in the mid ADC band (220-600) → firmware classifies as `REVISION_2_3`. This is consistent with an external 10k pull-up on A3 added by the rework, but the exact cut/jumper trace is uninventoried.

### What's needed

Photographs to `.planning/milestones/v1.7-artifacts/photos/rev-0-modified/`:
- `top.jpg` — full top view, all components visible, silkscreen-version region readable if present
- `bottom.jpg` — full bottom view
- `silkscreen.jpg` — macro of silkscreen-version region (or "no silkscreen-version printed" if Rev 0 era pre-dates the convention)
- `rework-cuts.jpg` — close-up of each PCB trace cut (with annotations)
- `rework-jumpers.jpg` — close-up of each added jumper / mod wire (with annotations identifying which net it bridges to which)
- (Optional) `r41-area.jpg` — close-up of where R41 would be on a stock Rev 2.0+ board, to document whether the rework added a substitute R41 or wired in a 10k pull-up via a different mechanism

### Sentinel cross-references (preserve verbatim per Phase 35 D-Discretion Pattern E)

The following sentinels in `.planning/milestones/v1.7-SHIELD-REVS.md` carry `as-modified — pending Phase 35` or `pending Phase 35` annotations that will resolve when this todo + its companion (`write-modifications-md-rework-trace.md`) close:

- `.planning/milestones/v1.7-SHIELD-REVS.md` §1 row 4 (Modified Rev 0 row — `state: upstream-only`, `photo_dir: —`)
- `.planning/milestones/v1.7-SHIELD-REVS.md` §4 row 8 (Rev 2.2 → Modified Rev 0 electrical delta — `as-modified — pending Phase 35`)
- `.planning/milestones/v1.7-SHIELD-REVS.md` §5 row 7 (mechanical delta — `as-modified — pending Phase 35`)
- `.planning/milestones/v1.7-SHIELD-REVS.md` §6 row 91 (capability matrix Modified Rev 0 row — `as-modified — pending Phase 35`)
- `.planning/milestones/v1.7-SHIELD-REVS.md` §7 row 16+17 (R41 + JP4 alias rows — `as-modified — pending Phase 35` for mod_rev_0 column)

### When to triage

- At next milestone-start sweep (`/gsd-new-milestone`); operator can opt to bundle this with another bench-touch milestone (e.g., v1.6 Phase 27 RCA re-open if the bench-attached Modified Rev 0 board is being used during the A/B disambiguation)
- Standalone "v1.8: Modified Rev 0 documentation completion" mini-milestone is also viable

### Cross-references

- Memory `[[user_shield_revisions]]` — operator owns Rev 2.2 / Rev 2.0 / Modified Rev 0; EEPROM byte doesn't disambiguate
- Phase 35 CONTEXT D-07 — deferral rationale
- Phase 31 Plan 05 — original photo session that was blocked
- Companion todo: `write-modifications-md-rework-trace.md` (Phase 31 follow-up #4 — depends on photos as evidentiary substrate)
- Phase 35 bench evidence: `.planning/milestones/v1.7-artifacts/bench-evidence-35.md` §"Modified Rev 0 Board" — bench observation that the rework wired a 10k pull-up on A3

## 29 chips ride a pinout too narrow or wrong for them — AM27C080 gets 13V on A19, AT28C040 addresses 64KB of 512KB, and all of them are support_status: supported

*`pinout-address-width-and-we-pin-corrections.md` · date: 2026-08-22T02:00:00+02:00 · area: host*

### Problem

Five groups of chips — **29 rows, every one `support_status: "supported"`** and reachable by
`firestarter <chip> write` today — are routed to a `pinouts.json` family whose address bus is
too narrow for the part, whose write-strobe pin is wrong, or whose VPP pin lands on an
address line.

Found mechanically, not by inspection: infoic.xml's own `<maps>` table (per-chip bonded-pin
connectivity, indexed by the `pin_map` low byte the generator already parses) crossed with
one-rom's `chip-types.json` (per-layout pin function). Method, validation of the oracle, and
reproduction: [`notes/infoic-maps-onerom-three-way-join.md`](../../notes/infoic-maps-onerom-three-way-join.md).
**Read that first** — in particular §4, because a join keyed on the raw `protocol_id` instead
of `flags & 0x10` re-authors the WARNING-5 hazard, and that trap is live for anyone
regenerating pin maps from these sources.

Not previously recorded: `grep -rn "27C080\|SST28SF040\|AT28C040" .planning/` returns nothing
outside these artifacts.

### The five groups

Address-line requirement is `(size - 1).bit_length()`. "Truth" columns are agreed by both
`<maps>` (which pins are bonded) and one-rom (what each does).

| # | Chips | Currently | Truth | Consequence |
|---|---|---|---|---|
| 1 | `AM27C080`, `AT27C080`, `MX27C8000` (1M, algo `0x08`) | `DIP32_STD` — 19 addr lines, **`vpp-pin: [1]`** | 20 lines with **A19 on pin 1**; **VPP on pin 24**, **PGM on pin 22** (one-rom `27C080`: `pgm 22`, `vpp 24`) | `configure_eprom` asserts VPP → **13V onto A19**. Address bus also one line short. |
| 2 | `SST28SF040`, `SST28SF040A`, `SST28LF040(A)`, `SST28VF040` (512K, algo `0x10`) | `DIP32_STD` — **`vpp-pin: [1]`** | A18 on pin 1, WE on pin 31 (one-rom `SST39SF040`) | Same shape as the 2026-05 `SST39SF040` defect that read as dead silicon on the bench (`a332464`). Address bus scrambled regardless of whether the `0x10` handler asserts VPP — **not traced, do not assume it does not**. |
| 3 | `AT28C040`, `AT28MC040`, `CAT28C040`, `WE512K8` (512K, algo `0x0D`) | `DIP32_28C512_EEPROM` — **16 addr lines**, `rw-pin: [30]` | **19 lines** (A18 on 1, A17 on 30), **WE on 31** | Reaches only the low 64KB of a 512KB part, and strobes WE onto A17. No VPP on this family, so no damage path — functionally broken only. |
| 4 | `AT28C010`, `AT28LV010`, `AT28MC010` + 7 more (128K); `AT28MC020`, `CAT28C020`, `WE256K8` (256K) | same family, 16 addr lines, `rw-pin: [30]` | 17 and 18 lines; **WE on 31** | Same class as #3. `<maps>` shows pin 31 bonded and pin 30 NC on every one of them. |
| 5 | `AT27C011`, `D27011`, `D27C011` (128K in **DIP28**) | `DIP28_2764` — 14 addr lines | 17 lines | 1Mbit part on an 8K/16K layout. |

Only `CAT28C512@DIP32` (64K) actually fits `DIP32_28C512_EEPROM` — **17 of its 18 rows are
mis-provisioned.**

#### Why one-rom alone did not catch #3 and #4

[`notes/onerom-pinout-external-corroboration.md`](../../notes/onerom-pinout-external-corroboration.md)
records `DIP32_28C512_EEPROM` as byte-identical to one-rom `28C512`, `rw-pin` included. It
is — but **one-rom is the source that is wrong here.** Its own `SST39SF040`, on the identical
JEDEC 32-pin layout, puts `control.write` at **31**; its `28C512` says **30** and models only
the 64K part, where pin 30 is NC anyway. The agreement was two sources sharing one error, and
that family is one of the two the note already labels **provenance-ambiguous** (`ff70920`,
authored the same day as the cross-check).

`<maps>` breaks the tie because it is per-chip and mechanical rather than per-family and
hand-compared: `maps[9]` for `AT28C010` lists pin 31 bonded and pin 30 not.

### Why no existing gate sees this

- `tools/check_dispatch.py` asserts *no chip routes to `configure_eprom` on a pinout with no
  `vpp-pin`*. Groups 1 and 2 are the **inverse** — a `vpp-pin` that points at an address
  line — which the structural guard cannot express.
- `chip_database.json` is generated, so no reviewer diffs pin assignments per chip.
- `pinouts.json` is a hand-maintained **input** (`tools/build_db.py:204`) and gets no
  protection from the generator's decode tests — the gap
  [`todos/pending/onerom-pinout-external-corroboration-gate.md`](onerom-pinout-external-corroboration-gate.md)
  was filed to close.
- Nothing anywhere compares a row's address-bus width against its `code_memory_size`.

### What to build

Ordered by severity. Group 1 first — it is the only one where a wrong pin carries programming
voltage on an algorithm known to assert it.

1. **Width gate first, as a RED test.** For every row in `chip_database.json`, assert
   `len(address-bus-pins) >= (size_bytes - 1).bit_length()`. This fails today on groups 1, 3,
   4 and 5 — land it red, then fix. Cheap, total, and independent of both external sources.
2. **Connectivity gate.** For every row with `pin_map & 0xFF` resolving to a non-`map[0]`
   entry, assert `{pins assigned by pinouts.json} == {pins bonded per <maps>}`, both
   directions. Over-assignment catches a function on an NC pin; under-assignment is what
   caught groups 3 and 4. Note the family-level limit in the method note §1 — the connected
   set is an upper bound for the smallest member of a map group, so scope the equality to the
   largest member or assert `assigned ⊆ bonded` plus a separate width check.
3. **VPP-sanity gate**, closing the `check_dispatch.py` inverse: a family's `vpp-pin` must
   not appear in any row's sliced `address-bus-pins`. This is the guard that would have
   caught group 1.
4. **Correct `pinouts.json`.** New family for the 27C080 class (A19 on 1, VPP on 24, PGM on
   22 — CE and OE displaced, so it is genuinely a new layout, not a widened `DIP32_STD`).
   Re-route groups 2 and 3 onto the `SST39SF040`-shaped 32-pin layout. Widen or split the
   28C0x0 family and move its `rw-pin` to 31. New family for the DIP28 27C011 class.
5. **Adopt address-bus slicing in the generator** so the width defects cannot recur:
   layouts hold the ordered superset, the generator emits
   `address-bus-pins[:(size-1).bit_length()]`. This is the same change that deletes
   `MAX_27C020_SIZE` — see
   [`todos/pending/derive-away-max-27c020-size-hardcode.md`](derive-away-max-27c020-size-hardcode.md);
   sequence them together, the slice is a prerequisite for both.

### Verification limits — state these, do not paper over them

All five groups are **software-proven and unvalidated on silicon.** None of these parts is
in the bench inventory as far as `.planning/notes/VALIDATED-EPROMS.md` records. The evidence is two
independent documentary sources agreeing, plus datasheet-consistent address arithmetic — the
same evidence class that fixed `SST39SF040` in 2026-05 and was later borne out on the bench.

Group 2's damage question specifically needs the `0x10` / `configure_flash` firmware path
traced for a VPP assert before the hazard is described either way.

## 66 promoted 0x0D rows keep the 64-byte page floor -- floor safety is unproven for 11 of them

*`promoted-0x0d-rows-keep-the-64-byte-floor.md` · date: 2026-08-19T02:00:00+02:00 · area: host*

### Problem

Phase 149 / PGSZ-01 delivers a per-chip `page_size` to firmware only where the upstream `<ic>`
record's own `protocol_id` is `0x0D` (D-01) -- 18 of `chip_database.json`'s 84 `algorithm: 13`
rows qualify. The remaining **66 rows never carried a `0x0D` page value at all**: they arrived
under a different upstream algorithm and were promoted into the `0x0D` handler by
`classify()` **arm 2** (`firestarter_app/tools/build_db.py:371-386`), which routes any
`0x07`/`0x08`/`0x0B` (EPROM-family) part on a `DIP24_2816` / `DIP28_28C64` / `DIP28_28C256`
pinout (or `DIP28_2764` with the CMOS flag set) into the 28C EEPROM handler. Their `page_size`
field is whatever that OTHER algorithm's own record happened to carry -- a reading a
28C-page-write buffer never produced.

### Measured (this phase, D-04)

Full join of all 84 `algorithm: 13` rows against the pinned upstream XML, partitioned by
upstream `protocol_id` and `page_size` value (all 84 matched, zero unmatched):

| upstream `protocol_id` | `page_size` values -> counts | row total |
|---|---|---|
| `0x07` | 1->14 · 16->1 · 32->8 · 64->22 · 128->1 · 256->1 | 47 |
| `0x0B` | 1->17 · 16->2 | 19 |
| `0x0D` | 64->3 · 128->15 | 18 |

Only the 18 `0x0D` rows are upstream-native; their page sizes are exactly the CONFIRMED field
dictionary's documented band ("typically 64 or 128 bytes for 28C-family") and are the ones
PGSZ-01/D-01 delivers.

The remaining **66** rows (47 + 19 = 66, matching `84 - 18`) are promoted, and split by their
raw page value:

- **31** at raw `1` -- 14 from upstream `0x07`, 17 from upstream `0x0B`
- **8** at raw `32` -- all from upstream `0x07`
- **3** at raw `16` -- 1 from upstream `0x07`, 2 from upstream `0x0B`
- **1** at raw `256` -- from upstream `0x07`
- **1** at raw `128` -- from upstream `0x07`
- (the remaining 22 promoted `0x07` rows at raw `64` are numerically indistinguishable from the
  correct 64-byte floor and are not a risk this todo tracks separately)

31 + 8 + 3 + 1 + 1 + 22 = 66.

### Why they keep the 64 floor

A `page_size` value read out of a record filed under another algorithm is not evidence about a
28C page-write buffer -- `0x07`/`0x0B` (UV-EPROM) records have no page-write mechanism at all, so
whatever integer sits in that field describes something else (or nothing) for these parts. D-01
therefore does not deliver any of these 66 values to firmware; all 66 keep the existing
`PAGE_SIZE 64` floor (`firestarter/src/proms/eeprom_28c.cpp:19-33`).

**Precision matters for the safety claim.** For the **31** rows at raw `1` and the **1** at `256`
and the **1** at `128`, the raw value is either obviously not a page size (`1`) or wildly larger
than the shipped 28C family band (`256`), so the 64-byte floor is very likely safe. But for the
**11** rows at 16/32 (3 + 8), the raw value sits inside the plausible 28C page-size range, so it
is **not disproven** that the real chip's page could be smaller than 64 -- the floor's safety for
those 11 rows is **unproven**, not disproven. `eeprom_28c.cpp`'s comment was corrected in this
phase to say exactly that (D-04 deliverable 3).

### What would close it

Any future attempt to deliver a real page size to these 66 rows -- and especially the 11 at
16/32 -- needs either **datasheet curation per family** (looking up each part's actual 28C page
size independently of `infoic.xml`) or a **new corroboration axis**, because `infoic.xml` does
not supply one: `write_buffer_size`, `read_buffer_size` and `pages_per_block` were all measured
during this phase's research and found not to corroborate `page_size` for these rows.

**Explicitly out of scope by `REQUIREMENTS.md` §Out of Scope / DATA-04:** extending
`_PAGE_SIZE_BY_PART` (or any equivalent per-chip guess table) to cover these 66 rows without that
independent corroboration.

### Filed by

Phase 149 (dual-repo lockstep), D-04 deliverable 1, Plan 07.

## Decide the output contract for a protocol 0x05 write override, before any override flag ships

*`protocol-0x05-write-override-flag-output-contract.md` · date: 2026-09-16T02:00:00+02:00 · area: host*

### Problem

The originating issue (gh#68, `henols/firestarter_prom` issue #68) requested the alignment
refusal be offered behind an explicit override flag, so an operator who understands the risk could
proceed anyway. Phase 195 declined to ship one (D-03).

### The trap that made this phase decline it

An override that proceeds past the alignment refusal and then prints the plain success line
(`Write to X successful`) violates WRITE-02 **literally** -- that requirement is unconditional: no
protocol `0x05` write reports `successful` when bytes outside the requested address range were
erased. An override flag alone does not change what actually happened to the chip; it only changes
whether the operator asked for it. Shipping the flag without first deciding what the override path
*reports* would be the single easiest way to fail this phase's own requirement while believing the
requirement had been honoured, because the failure is in the output line, not in the write itself.

### What would close it

Not the flag -- **a decided output contract for the override path**, specifically:

- What the outcome line says (it must not be the plain "successful" line WRITE-02 forbids for this
  case; it needs wording that is honest about partial/unaligned collateral damage having occurred)
- What the exit code is (whether an overridden write that completes its protocol steps should still
  exit 0, given that the operation itself did not fail -- only the safety property did)
- What the operator must acknowledge before the override takes effect (a confirmation prompt, a
  required second flag, or some other friction proportional to the risk)

Once that contract is decided and recorded, the override flag itself is a small, mechanical
addition behind it.

### Filed by

Phase 195 (partial writes stop destroying the page), D-03, Plan 04.

### Closed by

## Prove the PlatformIO dev-tools build flag fails CLOSED (empirical, not assumed)

*`prove-pio-dev-flag-fails-closed.md` · date: 2026-07-28T02:00:00+02:00 · area: firmware*

### Problem

The channel-split gating design (see `notes/dev-tools-gating-channel-split.md`) needs a
PlatformIO mechanism that turns `DEV_TOOLS` **off by default** and **on only in the dev
environment / pre-release build**. The obvious mechanism is fail-**open** and would silently
defeat the entire feature:

```ini
build_flags = -D DEV_TOOLS=${sysenv.FIRESTARTER_DEV_TOOLS}
```

With the variable unset this plausibly expands to `-D DEV_TOOLS=`, which still **defines** the
macro (as empty), so every `#ifdef DEV_TOOLS` guard stays true and the dev commands leak into
every release build. That is the exact bug class being removed — `-D DEV_TOOLS` currently
leaking from the shared `[env]` block into `uno` / `uno328pb` / `leonardo` *and* `native`.

This must be **measured**, not reasoned about. A design that assumes the expansion behaviour
and gets it backwards ships dev tools in the stable release while all its tests pass.

### Task

Run the matrix and record the result:

1. Try the two candidate shapes:
   - `-D DEV_TOOLS=${sysenv.FIRESTARTER_DEV_TOOLS}` (suspected fail-open)
   - `${sysenv.FIRESTARTER_DEV_FLAGS}` carrying the whole flag, i.e. env var value is
     literally `-D DEV_TOOLS` (suspected fail-closed — the safe shape)
2. For each, build with the variable **set** and **unset**: `pio run -e leonardo`.
3. Do **not** trust the build log or the flash-size delta as the oracle. Check the linked
   binary for the symbols:
   ```bash
   avr-nm .pio/build/leonardo/firmware.elf | grep -iE 'dt_set_registers|dt_set_address'
   ```
   Absent in both = gated. Present with the var unset = fail-open, mechanism rejected.
4. Also confirm `pio test -e native` still passes with `DEV_TOOLS` **absent** — grep says
   nothing under `firestarter/test/` references `DEV_TOOLS` or `CMD_DEV_*`, so this should
   hold, but the shared-`[env]` inheritance means it has never actually been exercised without
   the flag.

### Why symbol-checking, not exit codes

A `pio run` that succeeds proves nothing about whether the guards fired — the guarded code
compiles fine either way. And a flash-size comparison is a weak oracle here: v1.22 Phase 117
already produced a +204 B Leonardo delta that contradicted a size-based prediction
(`project_v122_phase117_closed`). The symbol table is the only direct evidence that
`dev_tools.cpp` did not link.

### Acceptance

- A recorded before/after `avr-nm` capture for the chosen mechanism, both var-set and
  var-unset, on at least one AVR target.
- An explicit statement of which mechanism was chosen and which was rejected, with the
  observed expansion behaviour — so the phase does not re-derive it.

### Item 4 — ANSWERED (v1.22 Phase 119 Plan 02, 2026-07-28)

`pio test -e native_nodevtools` (a new env compiling and running the full 16-suite
`test_filter` without `-D DEV_TOOLS`) passes **112/112 across 16/16 suites**, identical to
`[env:native]`'s baseline, with **zero test-code changes**. This confirms the grep-based
prediction empirically: no test file under `firestarter/test/` references `DEV_TOOLS` or
`CMD_DEV_*`, so the suites are DEV_TOOLS-invariant by construction.

This answers item 4 ONLY. Items 1 through 3 (the `sysenv.FIRESTARTER_DEV_TOOLS` fail-open
vs fail-closed matrix and the `avr-nm` symbol capture) are **untouched** — they remain
scoped to 999.15 / gh#8 and were explicitly out of bounds for Plan 119-02 (LOCK-03/LOCK-02
firmware work), not this item's concern.

**Additional evidence folded in (v1.22 Phase 119 Plan 08/09, 2026-07-28):** RESEARCH's
temporary `[env:leonardo_nodevtools]` measurement at the phase base (commit `1880054`,
before any Phase 119 change) recorded **24388/28672** for a release-config (`-D DEV_TOOLS`
absent) Leonardo build, against `25680/28672` with the flag present — i.e. **`-D DEV_TOOLS`
costs 1292 B** (25680 − 24388) rather than saving it. Since it costs flash, the `DEV_TOOLS`
build carries the SMALLER headroom of the two configurations and is therefore the binding
constraint for LOCK-06's judgement (`.planning/PROJECT.md`'s SIXTH CORRECTION item 3).
This remains evidence for item 4 only (the env now compiles and its tests pass with the
flag absent) — it is not new evidence toward items 1 through 3's fail-open/fail-closed
`sysenv.*` matrix question, which stays open under 999.15 / gh#8. The env itself is now
permanent in `platformio.ini` as `[env:native_nodevtools]` with a CI step, per Plan 119-02.
Items 1 through 3 remain OPEN; this todo stays open pending them.

## Phase 130 record gate degrades superlinearly on STATE.md's single-line last_activity_desc

*`record-gate-superlinear-on-state-md-single-line.md` · date: 2026-08-17T23:40:00+02:00 · area: tooling*

### Problem

`check_record_corrections.py` is a required-green gate for every closing phase. Its runtime has
gone from a few seconds to **over two minutes**, and the cause is not the gate — it is the shape of
one of its scan targets.

`.planning/STATE.md` keeps `last_activity_desc` as a **single physical line**. Every plan appends
its record to that one line. Measured across Phase 146's execution:

| commit | plan | line 11 length (chars) |
|---|---|---|
| `d2c212f1` | 146 planning complete | 6,551 |
| `083e4e5f` | 146-03 | 13,619 |
| `0accb44e` | 146-04 | 19,393 |
| `9b93a339` | 146-05 | 26,423 |
| `84c70ec3` | 146-06 | 31,243 |
| `825ead7c` | 146-07 | 35,600 |
| `d7ae43e8` | 146-08 | 42,227 |
| `70671033` | 146-09 | 48,335 |
| `982982dd` | 146-10 | 51,725 |

Growth is roughly linear at **+5,000 chars per plan**. Gate runtime measured at that last value:
**rc=0 in 130 s** (also observed at 114 s and 127 s in plan 146-11's runs), against a few seconds
early in the phase. The tally is unaffected — `{'block': 23, 'line-label': 4, 'inline-history': 6,
'inline-allow': 10, 'superseded': 12}` — so this is cost, not correctness.

### Why it matters more than it looks

**A short `timeout` now produces `rc=124`, which reads exactly like a RED.** This already happened
once during Phase 146 orchestration: a 100 s allowance returned 124 and was briefly misread as a
gate failure. Any plan that wraps this gate in a 60 s or 100 s timeout will report a false RED, and
the natural next move — "investigate why the record gate broke" — burns a whole debugging cycle on
a gate that is passing.

Phase 146's executors were each given the ≥300 s allowance explicitly. That mitigation does not
survive into the next phase unless it is written down somewhere the next planner reads.

### Candidate fixes, in preference order

1. **Stop growing one line.** Give `last_activity_desc` a folded/block scalar, or move the
   per-plan `PRIOR (...)` history out of frontmatter into a body section. The field is already
   append-only history; frontmatter is the wrong home for kilobytes of it. Note that `phase.complete`
   and the `state.*` writers are recorded as destructive against this file, so any restructuring is a
   hand edit with a snapshot-and-diff, not a verb call.
2. **Make the gate's own regexes line-length-insensitive** — profile which pattern dominates before
   touching any of them, since the pattern table is deliberately transcribed-unchanged across
   phases and loosening one silently weakens a real check.
3. **At minimum, document the ≥300 s allowance** in the gate's own module docstring, so the next
   caller sees it without having to rediscover the 124.

### Not resolved by Phase 146

Phase 146 is a documentation-and-closure phase whose D-06 forbids behaviour changes, and the gate
is a live target of its own record checks. Deliberately left as a finding rather than absorbed.

---

### UPDATE 2026-08-18 — largely resolved by Phase 146 plan 146-13

Candidate fix 1 above ("stop growing one line") was effectively applied by `146-13` when it
restructured `last_activity_desc` and moved the per-plan `PRIOR (...)` history into the body.

Measured before and after, same gate, same tally:

| STATE.md line 11 | gate runtime |
|---|---|
| 51,725 chars | **130 s** |
| 2,079 chars | **23 s** |

Tally unchanged at `{'block': 23, 'line-label': 4, 'inline-history': 6, 'inline-allow': 10,
'superseded': 12}` across both, confirming this was always cost and never correctness.

**What remains worth doing**, so this does not simply regrow:

1. The field is still a single line and still append-only, so the same drift will recur over the next
   milestone unless the convention changes. Consider capping it, or making the body section the
   canonical home and the frontmatter field a one-line pointer.
2. Candidate fix 3 is still undone and is cheap: document the allowance in
   `check_record_corrections.py`'s module docstring. At 2,079 chars a 60 s timeout is now ample, which
   is exactly when the next caller will hardcode a short one and get bitten after the field regrows.
3. Candidate fix 2 (profiling the dominating pattern) remains untouched and is now lower priority.

## Spike — measure programming-time delta from a larger DATA_BUFFER_SIZE

*`spike-databuffer-size-speed-delta.md` · date: 2026-07-02 · status: pending · priority: medium · type: spike*

De-risks the *speed* half of the binary-command-protocol seed **before**
committing to a breaking wire change. The whole payoff hinges on: reclaimed RAM →
larger buffer → fewer ack round-trips → faster. That chain's magnitude is
currently unmeasured.

### Experiment

- Bump `DATA_BUFFER_SIZE` within *existing* free RAM (no protocol change needed
  to test the buffer-size effect):
  - Uno: 512 → 1024 (if it fits with token array still present; else free RAM
    first via a temporary token-array shrink)
  - Leonardo: 1024 → 1536
- Time a full write+verify of a representative chip at each buffer size.
- Record: total wall-clock, and if possible per-chunk turnaround vs raw transfer
  time at 250k baud (this ratio is what determines whether more buffer helps).

### Decision it informs

- **Big speedup** → binary-command-protocol seed is worth the breaking change.
- **Marginal** → the RAM reclaim isn't worth a wire break for speed alone;
  reconsider on flash/cruft grounds only.

### Run it

`/gsd-spike` when ready (needs bench hardware — Uno + Leonardo). Operator-gated.

### Related

- Seed: `binary-command-protocol.md`
- Note: `binary-protocol-savings-analysis.md`

## Write full MODIFICATIONS.md rework trace for operator's Modified Rev 0 (Phase 31 follow-up #4)

*`write-modifications-md-rework-trace.md` · date: 2026-05-26 · status: deferred · priority: MEDIUM · type: documentation*

### ⏸ DEFERRED 2026-08-29 by operator direction — do not plan this

Operator directed on 2026-08-29 to **skip Rev 0 and defer it**. This todo is parked with **no target
milestone**. It is split out of backlog **999.42**, which now covers only the six unswept chips and the
two unswept shields; it is **not** a blocker on that item and must not be sized into a resumption of it.

Pick this up only if the operator puts the Modified Rev 0 board on the bench for some other reason.
Nothing downstream depends on it: firmware handles the board correctly today via the broad-bucket
`REVISION_2_0` + EEPROM override fall-through, regardless of how the rework landed.


### ⚠ STATUS UPDATE 2026-08-29 — v1.34 Phase 164 closed UNRUN; now carried as backlog 999.42

`resolves_phase: 164` is retained, but **Phase 164 never ran.** v1.34 closed early and scope-reduced
by operator direction on 2026-08-29; Phase 163 (cell B1) never put the board on the bench, so Phase
164 — which was scheduled to photograph it *while it was already out for B1* — never started either.

**Current home: backlog 999.42** ("Finish the v1.34 sweep — six chips, two shields, and the Rev 0
rework trace"). See `.planning/ROADMAP.md` §Phase 999.42 and `.planning/milestones/v1.34-artifacts/CLOSE-RECORD.md` §2.3.

**The third deferral in this todo's life** (Phase 31 → Phase 35 → post-v1.7 → Phase 164 → 999.42),
and the board is **still never physically inspected**. No photographs of it exist anywhere.
#### PARTIALLY ADVANCED at the desk by `0e114fb7` (2026-08-29) — read before restarting

Desk work done with **no board in hand and no photographs**, so the trace itself is still blocked.
What it settled, and what it did not:

- **The schematic reference this todo would have been traced against was WRONG.** Every prior
  citation named blob `d2a7f691` / `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`.
  Both halves are wrong: `d2a7f691` is `hardware/W27C512Programmer.kicad_sch` on `origin/rev2.0`, and
  it is a bare `.kicad_sch`, not a member of that zip. **The true Rev 0 schematic is blob `cfe6139f`
  at commit `486f3d1`.**
- **This would have wasted the photo session.** The two differ by 23 components, concentrated exactly
  where a rework trace looks. Rev 0 has JP1 (24-pin ROM VCC), JP2 (≥SST39SF020 & 28C512 need A17),
  JP3 (W27C010/AT27C010 needs p1 VPE/VPP) and global label A18. `rev2.0` instead has JP4/JP5, R41=4k7
  at A3, Q9–Q12, RN2-5/7-8 at 10k not 4k7, and drops RN1/RN9. A tracer working from `d2a7f691` would
  hunt the board for JP4/JP5 **that are not on it** and never inspect JP1/JP2/JP3 **that are** — and
  JP2 is the A17 strap, directly relevant to the Bug A upper-address jitter.
- **`.planning/milestones/v1.7-artifacts/MODIFICATIONS.md` is no longer the stub this todo was written against.** It now
  carries the reference correction with the full delta table, a corrected identity table including
  the Rev 2.2 10 kΩ ADC collision, an empty-but-structured rework inventory ready to be filled from
  photographs, and a seven-item inspection priority list derived from the Rev 0 netlist.
- **The ten `TBD pending Phase 35` sentinel cells in `v1.7-SHIELD-REVS.md` §4/§5 are discharged**
  (10 → 0) via REV0-03's *named-reason* branch — each cell now names the specific artefact that is
  missing (a photograph, a continuity probe, a DMM reading) instead of saying "pending". Two resolved
  to real attested values (the 10 kΩ A3 pull-up — an **addition**, since Rev 0 has no A3 divider at
  all), and the §5 "gated" cell resolved to gated on that pull-up's electrical nature.

**What remains for this todo is unchanged and still blocked:** the actual cut-and-jumper trace, which
needs the photographs from `photograph-modified-rev-0.md`. Use `cfe6139f`, **not** `d2a7f691`, and
start from the seven-item inspection priority list rather than from scratch.

### The deferral

Companion to `photograph-modified-rev-0.md` — the rework trace requires the photographs as evidentiary substrate. Both deferred from Phase 31 → Phase 35 → post-v1.7 per Phase 35 D-07. Independence from v1.7 detect-fw substrate confirmed by Phase 35 Wave 3 bench session: firmware correctly handles the Modified Rev 0 board via the broad-bucket `REVISION_2_0` + override fall-through path regardless of rework internals.

Phase 35 bench discovery: the Modified Rev 0 board's A3 net reads in the mid band (220-600) → firmware classifies as `REVISION_2_3`. Implies the rework added an external 10k pull-up on A3. Exact wiring (which trace was cut, which jumper added, what net it connects to) is uninventoried.

### What's needed

Author `.planning/milestones/v1.7-artifacts/MODIFICATIONS.md` (currently a stub created in Phase 31 Plan 05) with:

Per-rework-entry trace against upstream Rev 0 schematic blob `d2a7f691` on `origin/rev2.0`:

For each cut + jumper:
1. **Net affected** (which schematic net was the cut on; which two nets does the jumper bridge)
2. **Schematic-side delta** (compare modified state against the upstream blob — what would have been connected pre-rework vs post-rework)
3. **Capability matrix delta** (does this rework change which chip families / algorithms the board can program? Likely no — the rework is the hardware-bug-A/B fix, not a capability change)
4. **Bench evidence** (the Phase 35 ADC mid-band reading + the `MSG_OK_REV` `Rev 2.0-class, Override HW: Rev 2.3` output is one data point; additional evidence as needed)
5. **Rationale** (what was the original bug being fixed; cite memory `[[user_shield_revisions]]` for "hardware-bug-A/B" context if relevant)

Cross-link from `.planning/milestones/v1.7-SHIELD-REVS.md` Modified Rev 0 rows to the new MODIFICATIONS.md sections.

### Sentinel resolution

Once both todos close, upgrade the following `.planning/milestones/v1.7-SHIELD-REVS.md` rows from `as-modified — pending Phase 35` to bench-verified state:
- §1 row 4 (`state` flips to `operator-photographed`; `photo_dir` to `.planning/milestones/v1.7-artifacts/photos/rev-0-modified/`)
- §4 row 8 (Rev 2.2 → Modified Rev 0 electrical delta — fill with per-cut/per-jumper specifics)
- §5 row 7 (mechanical delta)
- §6 row 91 (capability matrix Modified Rev 0 row — should match parent Rev 0 capability set if rework is the hardware-bug-A/B fix without capability changes)
- §7 row 16+17 (R41 + JP4 alias rows — Modified Rev 0 column)

Bench-evidence-35.md analysis is the seed for the rework-trace narrative.

### When to triage

**AFTER** `photograph-modified-rev-0.md` resolves. Sequence:
1. Schedule operator photo session (or fold into next bench-touch milestone)
2. Operator captures the 5+ photos to `.planning/milestones/v1.7-artifacts/photos/rev-0-modified/`
3. Author working through the photos + upstream schematic blob + Phase 35 bench evidence → write MODIFICATIONS.md
4. Update SHIELD-REVS.md sentinel rows
5. Close both todos atomically

### Cross-references

- Phase 35 CONTEXT D-07 — deferral rationale
- Phase 31 Plan 05 — original MODIFICATIONS.md stub creation
- Phase 35 bench evidence: `.planning/milestones/v1.7-artifacts/bench-evidence-35.md` §"Modified Rev 0 Board" — 10k pull-up inference seed
- Upstream Rev 0 schematic blob `d2a7f691` on `origin/rev2.0` in `firestarter` sub-repo's upstream clone (`.planning/milestones/v1.7-artifacts/upstream-rurp/`)
- Companion (predecessor) todo: `photograph-modified-rev-0.md` (Phase 31 follow-up #3)
- Memory `[[user_shield_revisions]]` — "hardware-bug-A/B" rework context

## Land `write --sdp-relock` — deferred TWICE (v1.30 Phase 135, v1.32 Phase 150), tracked as Backlog 999.28

*`write-sdp-relock-deferred.md` · date: 2026-08-03 · priority: medium*

### ⏸ SECOND DEFERRAL — 2026-08-20 (read this first)

Promoted 2026-08-18 into **v1.32 as Phase 150**, then deferred out again by operator decision on
**2026-08-20** during `/gsd-discuss-phase 150` — before the gray-area selection was answered, and before
any research, plan or CONTEXT.md existed. **Nothing was created**: no `.planning/phases/150-*/`
directory, no CONTEXT.md, no commits in either sub-repo. Operator's words: *"I don't want the relock
implementation right now. I will implement it later if it is requested later."*

**So everything below still applies, once, with three amendments:**

1. **RELOCK-08 came and went with the feature** — v1.32 added it (`write --help` pins updated
   deliberately) and it returns to Backlog 999.28. **DATA-06 did NOT return**: it was retained in v1.32
   and re-homed to **Phase 151**, resolving on its documented-advisory branch, which the deferral makes
   the only reachable one. A future promotion must **not** re-claim DATA-06 or re-open that fork.
2. **The outward-facing obligation below has now fired twice, and the second firing is harder.** v1.32's
   Phase 152 OUT-01/OUT-04 were amended on 2026-08-20 to describe a **second withdrawal** rather than a
   migration, and OUT-05's fail-provable claim gate gained a **fifth claim class** rejecting any outward
   text that names `write --sdp-relock` as shipped or available. **A future promotion must reverse that
   gate class in the same change that lands the feature** — otherwise the gate will reject the very
   release notes announcing it.
3. **Six measurements were taken on 2026-08-20 against app `9cc57c7`** and are recorded in
   ROADMAP §"Phase 150" → *Measured findings*, so a re-promotion needs no fresh archaeology: the
   `protect_on_after` distribution (70/746 true; 43 of 84 `algorithm: 13`; **27 of 27** `algorithm: 5`,
   i.e. a constant there); its `MP_PROTECT_AFTER` = *"can* re-protect after write" capability-not-policy
   semantics; the machine-proven element-wise equality between that field and `sdp_capability`'s
   transcription (`tests/test_sdp_db_invariant.py::test_sdp_partition_matches_infoic_derived_field_element_wise`);
   `tools/check_sdp_capability_invariants.py` Class 2(b) forbidding any binding of `SDP_CAPABLE_TOKENS`
   other than a literal `frozenset` of string literals (so "read the DB field at runtime" trips an
   existing gate); the **true** `write --help` pin locations —
   `tests/test_characterization.py::test_help_write` and `::test_no_blank_check_polarity`, two syrupy
   snapshots each carrying the full help text, **not** Phase 136's channel-gating tests, and `write` is
   not channel-gated at all; and the fact that the non-verbose log formatter is `"%(message)s"`
   (`cli_handlers.py:110`), so `logger.warning` emits **no** level prefix and RELOCK-04's "mandatory
   final `WARNING:` line" needs a **literal** `WARNING:` in the message string
   (`eprom_info.py:269` is the in-tree precedent).

Also still true and worth re-reading before promoting: the deleted `dev sdp` handler, with its four
ordered gates (absent-chip → capability → support-status → consent), is recoverable **verbatim** at
`firestarter_app` commit `259a0f0`, and `firestarter/sdp_honesty.py`'s module docstring still names
`write --sdp-relock` as its intended caller.

---

## `write --sdp-relock` was deferred out of v1.30 — and the deletion shipped without it

**Deferred 2026-08-03** by operator decision, while v1.30 Phase 132 was in flight at plan 08 of 09.
Scoped as **v1.30 Phase 135**, never planned, never executed — no `.planning/phases/135-*/` directory
was ever created. Filed as ROADMAP Backlog **999.28**, which carries the full goal, success criteria,
prerequisites and promotion constraints. **The v1.30 phase number was not reused:** Phases 136 and 137
keep their numbers and the 135 slot stays vacant, same convention as v1.13's Phase 75 → Backlog 999.4.

### Why this is a todo and not just a backlog stub

Because a **paired** change was split, and only one half shipped.

`REQUIREMENTS.md` §`write --sdp-relock` (RELOCK) opens with its own constraint:

> Must ship with the deletion — they are a pair, and deleting the lock before re-homing it strands the
> only legitimate use case the deleted command served.

v1.30 Phase 132 ships the deletion of `firestarter dev sdp <chip> enable|disable`. This half did not
ship with it. So **v1.30 strands exactly the use case that sentence names**, and the window stays open
until 999.28 is promoted:

- `write` auto-unlocks on every protocol-`0x0D` write (v1.22 policy (d), declinable via
  `--skip-sdp-unlock`) and **never re-locks**.
- The `dev sdp enable` surface is **gone**.
- ⇒ There is **no supported way to deliberately protect an SDP part**, and on `0x0D` the protection bit
  cannot be read back, so a user cannot observe the resulting state either.

That is an accepted cost, recorded in `REQUIREMENTS.md` §Out of Scope and ROADMAP §`Phase 135` /
§`Phase 999.28`. It is not a defect to fix — it is a **promise not to overstate**, which is what makes it
a live todo rather than a parked idea.

### The outward-facing obligation this creates for v1.30's own close

v1.30 Phase 137 (CLOSE-05, CLOSE-06) was amended on 2026-08-03 because both criteria previously
described a substitution that will not exist in the shipped release:

- **Release notes** must map `dev sdp disable` → `write` (automatic — real, the firmware auto-unlocks on
  every `0x0D` write), and `dev sdp enable` → **nothing in this release**: withdrawn, tracked as Backlog
  999.28. They must **not** map it to `write --sdp-relock`.
- **The gh#12 reply** must say the same thing. gh#12 asked for enable/disable; after v1.30 it gets
  `disable`-by-default and **no** `enable` at all. See the amended
  [`gh12-followup-after-dev-sdp-retirement.md`](gh12-followup-after-dev-sdp-retirement.md).

Announcing a command that does not exist in the release being announced is the same overclaim class as
v1.22's C-5 correction — the class v1.30's honesty ledger exists to catch. Getting this wrong would be
the milestone failing its own stated purpose in its most public artifact.

### What this todo owes, and when

1. **At v1.30's close (Phase 137)** — verify the release notes and the gh#12 reply describe a
   **withdrawal**, not a migration. This is the urgent half; it expires when v1.30 ships.
2. **Whenever 999.28 is promoted** — land the feature, then correct the record outward: the shipping
   version's release notes announce it, and gh#12 gets the follow-up it was promised. This half has no
   deadline.

### Nothing to redo at promotion time

Every prerequisite is already in the tree:

- Firmware `CMD_SDP_LOCK` / `CMD_SDP_UNLOCK` — v1.22 Phase 119. **Host-only work**: no firmware change,
  no dual-repo lockstep, no `.hex` re-cut.
- The capability gate to reuse — `sdp_capability()`.
- `eprom_operations.py` `sdp_unlock` / `sdp_lock` and their `COMMAND_NAMES` entries — kept deliberately,
  load-bearing for this caller. (Their dereference sites were re-measured by v1.30 plan 132-08 to
  `_setup_operation:329` / `_operation_context:405`; the older `:301`/`:377` citations are stale.)
- The D-10 honesty wording and D-14 unknown-command mapping — Phase 132 authored them into a shared
  production helper as an explicit **forward contract** for this caller (`132-CONTEXT.md` D-01), and
  `tests/test_sdp_honesty.py` is its stable module name (`132-03-SUMMARY.md:153` — no further rename
  owed).
- **Polarity already decided, do not re-litigate:** verify failure ⇒ **skip the relock and report it
  loudly**, leaving the recoverable state. Per v1.22 auto-unlock policy (d), recorded at
  `PROJECT.md:823`. Relocking a part whose write did not verify would protect a bad image behind a lock
  that cannot be read back and can only be cleared by another write.

### Constraints at promotion

- **One-writer-per-file.** This writes `firestarter/cli_handlers.py` in the `write` handler (~:570).
  Worktree isolation is unavailable while the code lives in the `firestarter_app` submodule — the
  executor commit protocol cannot commit into a submodule from an isolated worktree — so it cannot run
  concurrently with another phase writing that file. See ROADMAP §v1.30 "Dependency spine".
- **`write --help` changes.** Any `write`-help output pinned by v1.30 Phase 136's channel-gating tests
  must be updated **deliberately** as part of this work, not silently re-baselined.

### Related

- ROADMAP Backlog **999.28** — the promotable stub (full success criteria).
- ROADMAP §v1.30 `### Phase 135` — the deferral record and renumbering rationale.
- `REQUIREMENTS.md` §RELOCK — RELOCK-01…06 retained verbatim with `⏸` checkboxes; §Out of Scope carries
  the decision row.
- **RELOCK-07 did NOT come here.** The stale-label re-homing stayed in v1.30, re-homed to Phase 137, and
  its targets now name Backlog 999.28. It also carries a warning worth reading: four places in the
  record cite those two labels and no two agree.

---

### ◐ PARTIAL DISCHARGE 2026-08-21 — v1.32 Phase 152, plan 152-14. **THIS TODO STAYS IN PENDING.**

This note records that **one half** of §"What this todo owes, and when" is discharged. The other half is
**not**, and must not be presented as met.

**Discharged — the gh#12 follow-up half.** The reply owed on gh#12 is posted:
[issuecomment-5373440001](https://github.com/henols/firestarter_prom/issues/12#issuecomment-5373440001),
id `IC_kwDOSX4ER88AAAABQEgwAQ`, `2026-08-21T20:00:19+02:00`. It describes a **withdrawal spanning a second
release**, not a migration, and it never names `write --sdp-relock` — satisfying both this todo's
outward-facing obligation and the amended companion todo now at
`.planning/todos/completed/gh12-followup-after-dev-sdp-retirement.md`.

**NOT discharged — "the shipping version's release notes announce it."** That half is *unmeetable* until
the feature exists, and the feature does not exist. v1.32's release notes announce the **withdrawal**
and name Backlog 999.28; they do not announce the feature, because there is nothing to announce. Do not
read this partial discharge as closing that obligation.

**`resolves_phase` stays `none`.** Unchanged and deliberate, for the reason already recorded in the
frontmatter: pointing it at a vacated phase number (v1.30's 135 or v1.32's 150) would make this todo
look resolvable by a phase that never existed. Both slots stay unreused.

**The standing instruction survives, and v1.32 made it sharper.** A future promotion of Backlog 999.28
must **reverse OUT-05's fifth claim-gate class in the same change that lands the feature**, or the gate
will reject the very release notes announcing it. As of this phase that gate is no longer hypothetical:
`152-check-claims.py` is armed at seven real outward artifacts, its `sdp-relock-as-shipped` row is
proven to reject 11/11 planted overclaims while permitting 7/7 withdrawal phrasings, and its 34-leg
paired suite pins both directions. The reversal is therefore a real, testable code change with a named
owner — not a note to remember.

One implementation detail measured during this phase and worth carrying: the negative lookahead requires
the withdrawal word (`withdrawn|deferred|not shipped|not shipping|unavailable|absent`) to follow the
command name almost immediately. An intervening word breaks it — "`write --sdp-relock` **command** is
withdrawn" is rejected as an overclaim. Any reversal must account for that shape.

## Full 64KB streaming reads return 57% scrambled data on uno328pb (small reads stable)

*`v1.8-seed/large-read-data-jitter-uno328pb.md` · date: 2026-05-21 · status: v1.8-deferred · priority: HIGH · type: bug*

v1.6 ships as "diagnostic + revert" per D-17v2: the Phase 28 v1 firmware-induced
regression (commit 437339b6 PORTx-clear) was reverted cleanly via ea25174; the
4f205e58 `_NOP()` settling change preserved (Plan 28-04 parks); Leonardo Modified
Rev 0 returns to the Phase 26 baseline shape (WORST=0.047% zeros vs Phase 28 v1's
83.8% pre-revert). The original read-bug itself is NOT fixed in v1.6 — it predates
v1.6 and remains by design.

Phase 29 v2 (closed 2026-05-26) characterized the bug as two independent failure modes:

### Bug A — Modified Rev 0 upper-address jitter (the original v1.6 read-bug; carries to v1.8)

- 858/65536 (1.31%) of byte positions disagree within N=5 consistency-check.
- Address-bit correlation (smoking gun): A15=1 → 1.70% jitter vs A15=0 → 0.92% (1.86× skew);
  A14=1 → 1.55% vs A14=0 → 1.07% (1.46× skew). Upper 24KB (0xA000-0xFFFF) accounts for
  2/3 of jittery bytes.
- Bit-direction bias: 63% of jitters BIT-RAISE (read more 1s than the mode); mean delta +8.89.
- Hypothesis: address-bus signal-integrity at upper addresses (A14/A15 high → more bits
  toggling → ground bounce / supply sag / capacitive crosstalk) combined with weak data-bus
  pull-down. The `_NOP()` settling at 4f205e58 targeted timing; insufficient on its own.

### Bug B — Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch (independent shield-specific)

- All 5 Rev 2.0 N=5 byte-identical (deterministic; zero within-session jitter).
- 49.06% of read bytes are bus-tristate symptoms: 36.19% `0xff` + 12.87% `0x00`.
- VPP measured 13.1-13.2V > 12.0V expected — voltage divider ratio differs from Modified Rev 0.
- 54473/65536 (83.1%) bytes differ from Modified Rev 0; per-bit XOR distribution uniform across
  D0-D7 (~22-25K flips each) — NOT a single stuck data line.
- Hypothesis: Rev 2.0 has different /CE or /OE timing AND/OR different voltage-divider ratio.
  VPP-too-high warning corroborates voltage-divider mismatch.

### v1.8 RCA substrate (ready to consume)

- 15 N=5 W27C512 binaries (3 sessions × 5 runs × 65536 B):
  - `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-155021-v2/` — Modified Rev 0 canonical
  - `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-155617-v2-rev20/` — Rev 2.0 bonus
  - `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-160035-v2-rep/` — Modified Rev 0 replication
- `.planning/milestones/v1.6-artifacts/bench-logs/W27C512-leonardo-20260526-*.log` — 3 tee'd stdout logs
- `.planning/milestones/v1.6-EVIDENCE.md` §"Phase 29 v2 — Post-Revert Bench Verification (2026-05-26)" (H3 block at lines 394+) — full pattern findings
- `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md` — canonical Phase 29 v2 close narrative
- v1.7 substrate (shipped 2026-05-26): `.planning/milestones/v1.7-SHIELD-REVS.md` per-rev capability table + labeled schematic + shield-version-detect firmware plumbing → enables v1.8 to design A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step.

### Phase references

- Phase 27 RCA (original) — `.planning/phases/27-root-cause-analysis/27-01-SUMMARY.md`
- Phase 27 RCA re-open (2026-05-26) — `.planning/phases/27-root-cause-analysis/27-05-SUMMARY.md` (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing hardware)
- Phase 28 v1 (reverted) — commits 437339b6 (PORTx-clear) + 4f205e58 (`_NOP()`) in `firestarter/`
- Phase 28 re-iteration (2026-05-26) — Plan 28-03 revert ea25174 + Plan 28-04 parked
- Phase 29 v2 close — `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md`

---

*(Original v1.6-era bug report text preserved verbatim below for v1.8 RCA context.)*

## Full 64KB streaming reads are unreliable on uno328pb

### The bug

`firestarter read SST27SF512 file.bin` (the high-level full-chip read) returns substantially different data on consecutive invocations against the same physically-static chip. Empirical jitter rate **57.8% (37,883 / 65,536 bytes)** between two reads taken minutes apart with no chip changes in between.

Concrete evidence (bench 2026-05-21, SST27SF512 in socket on operator's 328PB-Uno via /dev/ttyUSB0):

```
read 1: SHA b126a4df...05c9cf
read 2: SHA f4a06e16...d98e4b  (after a 16-byte write + 256-byte write)
read 3: SHA b6f83c7c...d616   (no further chip changes after read 2)

diff(read2, read3) = 37,883 / 65,536 bytes (57.8%)

Sample at offset 0x009e:
  read1: 0x1d
  read2: 0x80   ← scrambled
  read3: 0x1d   ← matches read1

Sample at offset 0x0053:
  read1: 0x1e
  read2: 0x1e
  read3: 0x81   ← scrambled differently
```

The scrambled bytes are **not single-bit flips** — they're completely different values (e.g., 0x1d → 0x80, 0xde → 0x41), suggesting transport-level corruption rather than chip cell instability.

### What still works (so it's localized)

- `firestarter id SST27SF512` — consistent ✓
- `firestarter dev read SST27SF512 -s 16/256` — small reads return identical bytes across calls ✓
- `firestarter dev read SST27SF512 -s 256` after a 256-byte write — exact `pre AND target` pattern verified byte-by-byte
- `firestarter fw / hw / config` — handshake + EEPROM read stable ✓
- `firestarter vpp / vpe` — 12.4V / 14.4V stable across multiple sample sessions
- `firestarter fw -i --pre --force` (full firmware install via avrdude) — committed 22340 bytes and verified ✓

So the firmware's chip-read path WORKS for small bursts. The bug is somewhere in the **streaming 64KB chunked-read state machine** — either in the firmware's MAIN-state chunking or in the host's `serial_comm.py` per-chunk handshake.

### Hypotheses (for whoever investigates)

1. **Host-side serial buffer overflow.** At 250000 baud, 512 bytes = ~20ms wire time. If the host's pyserial input buffer fills and Python's read loop misses an ACK timing window, the next chunk could be misaligned.
2. **Firmware MAIN-state phase-transition off-by-N.** The protocol's 3-phase state machine (INIT → MAIN → END) chunks data; if a chunk-end marker is missed, subsequent chunks could be byte-shifted.
3. **328PB-specific timing.** The `[env:uno328pb]` mirrors `[env:uno]` settings (16MHz, 250000 baud) but the 328PB has additional peripherals (USART1 — even if unused, its register-set is present). A timing-critical loop that worked on 328P might just barely miss on 328PB due to slightly different instruction-cycle accounting in the inherited HAL.
4. **`[env:uno328pb]` is missing a `-D SERIAL_RX_BUFFER_SIZE=...` or similar.** The Phase 21 `[env:uno328pb]` declaration carries `-D SERIAL_ON_IO` (from CONTEXT D-07) and the inherited build flags from `[env]`, but no buffer-size overrides. The Leonardo gets `DATA_BUFFER_SIZE=1024` (per CLAUDE.md); the 328PB inherits the uno default of 512. Maybe SST27SF512's protocol needs a different timing.

### How to triage

```bash
# Run consecutive full reads against a stable chip
for i in 1 2 3; do
  firestarter -p /dev/ttyUSB0 read <chip> /tmp/read_$i.bin
  sha256sum /tmp/read_$i.bin
done
# Compare hashes — should be identical; aren't.

# Then narrow: do consecutive 1KB chunks via dev-read also jitter?
for offset in 0x0 0x400 0x800 0x1000; do
  firestarter -p /dev/ttyUSB0 dev read <chip> -a $offset -s 1024 > /tmp/devread_${offset}_a.txt
  firestarter -p /dev/ttyUSB0 dev read <chip> -a $offset -s 1024 > /tmp/devread_${offset}_b.txt
  diff /tmp/devread_${offset}_a.txt /tmp/devread_${offset}_b.txt | head -5
done
```

If dev-reads stay stable across all sizes but full reads jitter → the bug is in `firmware.py`'s `read_eprom()` / chunk loop or in `serial_comm.py`'s buffer management.

If dev-reads at 1KB ALSO jitter → the bug is in the firmware's per-chunk send code, not host-side.

**Triage result (bench 2026-05-21):** 1KB `dev read -s 1024` ALSO jitters — observed 1 byte difference at offset 0x5C across two consecutive reads of the same chip. Rate is much lower than full-chip (0.1% vs 57.8%), but still nonzero. This **points the bug at the firmware-side per-chunk send code on the 328PB, not host-side buffer management.** The bug is rate-limited — it manifests as occasional bit/byte corruption per chunk that compounds across many chunks. Small enough reads (16/256 bytes — single buffer fill) escape it; anything that streams multiple chunks accumulates errors.

**3-shield A/B/C triage (bench 2026-05-21, operator-driven):**

The operator rotated through three RURP shields on the same `[env:uno328pb]` board (`/dev/ttyUSB0`, hw_rev byte EEPROM-stored), same firmware (v3.0.0b4 from Phase 23 install), to isolate hardware-vs-firmware origin:

| Shield | Rev | EEPROM hw byte | Chip in socket | 32-byte sample reads as | 1KB jitter (consecutive reads) | 64KB full read completes |
|--------|-----|----------------|----------------|-------------------------|-------------------------------|--------------------------|
| 1 | 2.2 (recent) | Rev2 | SST27SF512 | varied (actual chip data) | 1 byte diff / 1024 | ✓ (with 57.8% inter-read jitter) |
| 2 | 2.0 | Rev2 | SST27SF512 | `77 14 b1 4e ...` (chip data) | 2 bytes diff / 1024 (offsets 0x4F + 0xBB) | ✗ timeout |
| 3 | 0/1.0 + voltage-divider mod | **Rev1** | (chip not transferred) | all `0x00` (bus pull) | **110-124 diff LINES / 3 reads** — multi-way jitter, much worse | ✗ timeout |

**Findings from the 3-shield methodology:**

1. **Jitter is NOT shield-specific.** Every shield shows it at the 1KB level. Differences in magnitude are explained by chip-vs-bus-pull data content and possibly minor electrical variations, but the *presence* of the bug is invariant across shields.

2. **Shield 3 (floating bus, no chip) jitters MORE than shields with real chips.** This is the smoking gun: when the chip is missing and the data bus is just floating/pulled to `0x00`, the host *still* receives different "0x00"-mostly values across consecutive reads. The variation cannot be coming from the chip (there is no chip). The bytes are being **introduced or corrupted somewhere between firmware's bus sample and host's serial receive.**

3. **Shields 2 and 3 fail full 64KB reads entirely** (timeout, zero bytes captured) while Shield 1 completed earlier in the session (with 57.8% inter-read jitter). The most likely explanation is not a shield-specific failure mode but a session-state difference: Shield 1's test ran when the chip socket was driving real data, and Shield 2+3 tests ran with a missing or wrong-orientation chip — the host's READ command may have a different timeout path when the firmware's blank-or-pattern detector trips.

4. **hw_rev EEPROM byte distinguishes Rev1 from Rev2 families** but not 2.0 vs 2.2. Shield 3 (Rev 0/1.0 modified) reports `Rev1`; Shields 1+2 both report `Rev2`. The voltage-divider mod on Shield 3 makes it electrically behave Rev2-alike for VPP/VPE measurement, but does not change the EEPROM-stored revision flag the firmware reads at startup.

**Updated implication:** This is a **pre-Phase-21 bug**, not a regression introduced by the uno328pb build. The Phase 21 work didn't change the read state-machine code — it only widened macro guards for board setup, ADC bandgap, and added the new env. The fact that the same jitter appears on all 3 shields with the same firmware suggests the bug has been latent in the codebase since at least v1.4 (probably earlier — full-chip reads weren't byte-compared in the v1.4 lockstep fixture).

**Re-tag:** demote from "v1.5 hotfix candidate" to "pre-existing latent bug surfaced by Phase 24 verify rigor". Still HIGH priority because it blocks meaningful read-back verification, but doesn't block v1.5 ship — uno + leonardo have the same bug, and they shipped at v1.4 without anyone noticing.

### Cross-checks needed

- **Does this happen on uno?** Re-run the same triage on `/dev/ttyACM0` with a chip in its socket (or test against the existing uno328pb data). If yes — bug is pre-existing, not 328PB-specific.
- **Does this happen on leonardo?** Same test on /dev/ttyACM1 (1024-byte buffer). Leonardo's buffer size means fewer chunks per 64KB read, so even if it jitters, the magnitude could differ.

### Impact on Phase 24 BENCH-02 closure

Phase 24 BENCH-02 acceptance — "run write→read→verify on a representative EPROM" — **CANNOT BE CLOSED** until this bug is fixed, because the verify-step's read-back comparison is meaningless when reads return scrambled data.

What WAS proven during Phase 24 bench validation 2026-05-21:
- Write path commits exactly the right bits (verified via `dev read -s 256` on the explicit-write regions, which IS stable)
- VPP regulator engages at 12V during writes
- Chip programming pulses respect the 1→0-only EPROM constraint
- Address bus + data bus + control bus all functional

What CANNOT be claimed:
- 64KB byte-identical round-trip verification (the read-back returns garbage)
- Any read-based verification of the explicit-write regions IF read via the full-chip `read` command (use `dev read -s N` for stable evidence instead)

### Cross-references

- Phase 24 BENCH-02 — partial closure pending this bug fix
- Memory `project-bench-findings-v15` — 328PB-Uno bench environment
- `firestarter_app/firestarter/firmware.py` — `read_eprom()` (suspect: chunked read loop)
- `firestarter_app/firestarter/serial_comm.py` — INIT/MAIN/END state machine + per-chunk handshake
- `firestarter/src/firestarter.cpp` — firmware-side MAIN-state read implementation
- `firestarter/CLAUDE.md` — Board differences note: Uno 512-byte buffer, Leonardo 1024-byte buffer
