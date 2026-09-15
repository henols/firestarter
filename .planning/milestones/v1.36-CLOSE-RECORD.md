# v1.36 — Close Record: `dev test` Fidelity

**Milestone:** v1.36 — `dev test` Fidelity
**Closed:** 2026-09-09
**Phases:** 174–181 (8) · **Plans:** 42 · **Requirements:** 46/46
**Shipped to:** `beta` in all three repositories — app `3.0.0b38`, firmware `3.0.0b26`
**Not tagged.** Operator decision at close: no `v1.36` tag was cut.

---

## 1. What the milestone set out to do, and what it did

`dev test` files community chip-validation issues. The milestone's question was whether those reports
tell the truth — not whether they are pretty, but whether every field in them corresponds to
something the run actually measured.

The answer at the start was no, in seven distinct ways: fields populated only on failure, fields
carrying a summed number presented as a per-operation one, fields no code path had ever assigned,
a chip ID recovered by scraping the report's own prose, an absent value that meant two different
things, a chip named however the operator typed it, and a schema version that had not moved while
the shape underneath it had.

All seven are closed. The report now carries `is_uv` off the single `derive_plan` decision;
`duration_s` as a mean over cycles that actually ran; a stamped-once wall-clock `elapsed`; exported
`fingerprint` siblings; a `divergence` recorded even on agreement, so absence means "not computed";
a structured chip-ID field; the database's own `part_number` in the issue title; and
`schema_version` at `2.0`, which is honest about the break.

Two fields were deleted rather than fixed — `voltage.vpp_mv` and `voltage.vpe_mv`, which no code
path had ever assigned. That was proven by an attribute-scoped AST census, not asserted; a textual
census returns roughly twenty false positives from a *database* field of the same name.

---

## 2. The invariant the whole milestone was built around

A filed issue body carries its own `dedup_fingerprint`, and `count_agreeing` reads that embedded
hash and never re-hashes. **A re-key is therefore permanent for the historical corpus** — no
migration of an already-filed issue is possible.

Phase 174 built the blast-radius harness before any behaviour change landed, precisely so this could
be measured rather than hoped for. Phase 181 then added seven exported keys — `elapsed`, `is_uv`,
`canonical_part_number`, `chip_id_detected`, `divergence` and the four `fingerprint_*` siblings —
and moved **none** of the 19 frozen hashes, because none of them sits inside `dedup_fingerprint`'s
five-entry allow-list.

D-16 committed the closing phase to zero re-keys. It discharged with **zero literal lines changed**
across the entire phase, re-verified at every wave including across the two change shapes that
genuinely could have moved them: `duration_s`'s semantic change and the schema *removal*.

**One deliberate re-key did happen and it is not a dedup re-key.** Plan 181-08 moved five
`LADDER_PINS` entries (`m27c512-*`) from CANDIDATE to NO_CHANGE. That is a `build_db_diff`
disposition pin — a separate mechanism — and it is the T-179-05 exhausted-slots ladder-flip bug
closing. The check discriminates: the five shapes that moved carry `write` `status=SKIP`, while the
controls that actually wrote (`w27e257`, `sst27sf512`, `status=COMPLETE`) did not move.

HYG-03's standing refusal — never refactor `dedup_fingerprint` to hash `to_dict()` or reflect over
dataclass fields — is recorded in `MILESTONES.md` and pinned by an AST test with a planted-mutant
leg.

---

## 3. The declared-re-key protocol was retired mid-milestone

Phase 174 created a `RK-174-` ledger table, a machine binding to an app-side fixture, a meta-side
checker and a registered CI workflow. All of it was deleted on 2026-09-08 by operator ruling:
keeping a `.planning` record accurate is GSD's responsibility, not a CI gate's.

Two measured defects independently condemned it. The app test suite reached into the meta tree with
no skip guard, so app CI on a bare checkout went `13 failed, 13 passed` where the devcontainer showed
`26 passed`. And three of the checker's own fail-closed proofs were tautological — `python3` on a
missing script exits `2` exactly as the checker's fail-closed path did, so they passed with their own
subject deleted.

The two-commit discipline it encoded survives as a **review** rule, carried in
`test_dedup_fingerprint_is_frozen`'s own failure message. RPT-E3 was re-anchored onto the 19 absolute
literals plus that rule, and its exception clause discharged **empty**.

The full detail, including the citation-shift consequences for phases 174–179's archived records, is
in `MILESTONES.md` under this milestone's Frozen-Shape Blast Radius section. Those archived records
still describe the protocol as live, which is what was true when they were written, and they are
deliberately left unedited.

---

## 4. Corrections made at the close, recorded rather than absorbed

Nine corrections were applied during phase 181's execution and close that the executors' own
self-checks reported as clean. The pattern matters more than any single fix.

**Six were GSD-provenance comments in shipped source.** Three shapes, each of which felt reasonable
to its author: writing a new `(HYG-01 / D-17)` citation; **rewording** a pre-existing comment that a
deletion had falsified — still writing comment prose, and it grows the census every time; and
inventing a "non-product-source tooling exemption" for `tools/`, defended by citing two precedents
that were themselves removals. The correct move, when your change makes a comment false, is to delete
the false clause and leave the rest byte-identical.

Two executors' own censuses missed instances by using a hand-picked file list. The orchestrator-side
census derives its list from `git diff --name-only` and caught every instance after that.

**One was a red Host CI gate filed as "pre-existing."** A `ruff format --check` failure was waived by
measuring against the wave-3 tip rather than the phase base. Against the base the check was clean, so
the breakage belonged to this phase and would have shipped red. The lesson generalised into a standing
rule for the remaining plans: measure "pre-existing" against the phase base, never the current tip.

**Three were records that said something untrue:**

- `181-CLOSURE.md` claimed its green-tree battery's suite floor was "re-derived from the wave-8
  measurement of 2282". The evidence file shows `suite_floor=2239` asserted as-is, and the sentence
  contradicted itself. Corrected to state that the floor leg is weak evidence and that what the
  battery actually rests on is the exact reconciliation against pytest's own `collected` total.
- `181-10-SUMMARY.md` justified leaving the gitlink unadvanced by citing a CLAUDE.md convention that
  does not exist — `grep -i gitlink CLAUDE.md` returns nothing. The project has caught this exact
  false-citation shape once before (`125-06-SUMMARY.md`, corrected by `4bb038e`).
- `REQUIREMENTS.md`'s D-5 row still instructed rewriting `SKILL.md:375`. Plan 181-09 measured that
  false and correctly refused it — `:375` is the *database* `vpp_mv` in the datasheet cross-check
  table, and the rewrite would have turned a correct row false. The plan amended CONTEXT.md but not
  REQUIREMENTS.md, leaving the instruction that would reintroduce the defect.

---

## 5. The one gap the verifier found, and whose fault it was

Verification returned **`gaps_found`, 18/19** on its first pass. The gap: the meta repo's
`firestarter_app` gitlink had never been advanced through the phase — it still pointed at `04fd982`,
the phase's own base, while 38 commits had landed in the submodule.

**The cause was an orchestrator error, not an executor one.** All ten executor dispatch prompts
carried the instruction "LEAVE the `M firestarter_app` gitlink line ALONE", carrying forward a
v1.6–v1.8 convention that phase 180 had already superseded by advancing the gitlink three times in
commits that say so in their subjects (`9f65162c`, `dcec60f9`, `e39bb91e`). Every executor complied
faithfully with a wrong instruction.

Closed at `6de7273`, re-checked independently by the verifier against the live tree rather than
against a report of the fix, and the verdict moved to **`passed`, 19/19**. The `gaps:` block was
replaced by a `re_verification:` block naming both closing commits rather than deleted, so the record
shows a phase that shipped with a gap found and closed — not one that never had a gap.

A second round followed when covered content drifted. Rather than hand-refresh the fingerprint a
second time — which would make the mechanism theatre — the verifier ruled on the drift itself, and in
doing so fixed a real gap it was asked about: `covered_files` had listed only `.planning/` artifacts,
so the fingerprint could not have noticed a source-side change at all. It now covers 74 files
including the 47 `firestarter_app` implementation and test files the phase touched.

---

## 6. What CI caught that local testing could not

The app's Host CI failed on `test_skip_census.py::test_every_skip_reason_is_allow_listed` after the
PR was opened. Plan 181-01's forward-only parse test carries a `pytest.skip` guard for meta-tree
fixtures — threat T-181-16's mitigation — whose reason was never registered in
`ALLOWED_SKIP_REASONS`.

It cannot fire locally: in this devcontainer the app **is** a submodule of the meta repo, so the
fixtures resolve and the test runs. On CI the repo is cloned standalone, the guard skips, and the
census catches an unregistered reason. Both halves of the mechanism worked exactly as designed.

Registered as a named constant rather than a commented literal, following the allow-list's own
`FW_ABSENT_REASON` precedent and both CLAUDE.md files' prescription to use a named constant instead
of a comment.

A second CI failure, on the firmware, was **infrastructure**: `apt-get` hit a hash-sum mismatch on
Google's Chrome apt repository while installing the ARM toolchain. The build never reached
compilation. Re-run, green.

---

## 7. Security

`## SECURED` — **36/36 threats closed, `threats_open: 0`** (ASVS L1, block-on `high`), recorded in
`181-SECURITY.md`. The register was authored at plan time across all ten plans, so the audit's
constraint was to verify the stated mitigations exist rather than to scan for new threats.

Two things in this system genuinely warranted the scrutiny and got it: the filed GitHub issue body,
the one outward trust-boundary crossing, and dedup-hash integrity.

One discrepancy is recorded rather than rounded away: T-181-20's mitigation text says the HYG-04
allow-list registration landed *in the same commit* as the helper. It did not — `9019c53` then
`2c1ebc2`, two commits apart. The final state is correct and gate-verified, but the register's own
wording overstates the discipline applied.

---

## 8. The honesty ledger — what this milestone does NOT claim

- **It does not claim the report is now complete.** It claims every field that remains corresponds
  to something the run measured. Fields that were never assigned are gone; fields that were
  ambiguous now distinguish their cases.
- **`chip_id_actual` is an echo, not a read-back.** On a pass, `check_eprom_id` echoes the host's own
  expected id, so the field equals `chip_id_expected` on every passing run. The docstring says so.
  RPT-A1 was discharged by stating the ceiling plainly, not by hiding it behind a passing equality.
- **The mypy watermark is not trustworthy evidence from this devcontainer.** The close plan caught a
  real regression (37 against a watermark of 35) and fixed it, but the gate is recorded as
  fail-open here — it can read green without type-checking anything.
- **`WR-01` is open.** `_is_interactive` became dead code when 181-04 removed its only caller, and
  two tests named `..._on_a_tty` patch it believing they gate TTY behaviour. They pass for the wrong
  reason. The repair spans ~14 call sites plus an allow-list entry, so it is filed rather than run as
  an unasked refactor at close. The security audit confirmed it bears on none of the 36 threats.
- **No hardware validation ran in this milestone's closing phase.** Phase 181 is host-only. The
  hardware-gated requirements (UV-\*, MEAS-01) were discharged in earlier phases.
- **No tag was cut**, by operator decision. `v1.36` exists as merged history on `beta` and as two
  pre-releases, not as a git tag.

---

## 9. Ship record

| Repo | PR | Merge commit | Result |
|---|---|---|---|
| `firestarter_app` | [#61](https://github.com/henols/firestarter_app/pull/61) | `b868264` | pre-release **3.0.0b38**, PyPI wheel + sdist |
| `firestarter` | [#60](https://github.com/henols/firestarter/pull/60) | `85c4761` | pre-release **3.0.0b26** |
| `firestarter_prom` | [#63](https://github.com/henols/firestarter_prom/pull/63) | `297eeea` | planning record |

Merged with **merge commits, not squashes**, deliberately: a squash would have given `beta` fresh
SHAs and left the meta repo's gitlinks pointing at commits unreachable from `beta`. Both gitlinks
were verified reachable from `beta` before the meta PR was merged, and the sub-repos were merged
first for that reason. This matches v1.35's precedent.

PyPI published automatically, 33 seconds after the beta release — **the v1.21-era "PyPI needs a
manual dispatch" note no longer holds**, and asserting it from that note produced one wrong statement
at this close before PyPI was actually queried.

---

## 10. Measured state at close

| Metric | Value |
|---|---|
| Phases | 8 (174–181), all verified |
| Plans | 42 |
| Requirements | 46/46 — GATE 6, MEAS 3, PRUNE 8, ATTR 6, UV 3, RPT 16, HYG 4 |
| App suite | **2285 passed, 0 failed** (milestone start 2247) |
| Regression gate | 886 passed across 20 prior-phase files |
| Frozen dedup hashes moved | **0 of 19** |
| Comment census | 0 of 28 changed files over baseline |
| Security | 36/36 closed, `threats_open: 0` |
| Commits merged to `beta` | 285 meta · 110 app · 1 firmware |
