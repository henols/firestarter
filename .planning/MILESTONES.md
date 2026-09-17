# Milestones

## v1.39 Protocol 0x05 Write Correctness (Closed: 2026-09-17)

**3 phases (194-196) · 15 plans · 43 tasks · 7/8 requirements · `override_closeout` · tagged `v1.39` — a bare tag, never a GitHub Release.**

Full close record: [`v1.39-CLOSE-RECORD.md`](milestones/v1.39-CLOSE-RECORD.md).

**This milestone has not shipped, and that is the first thing to know about it.** The fixes are on the milestone branch only — 16 meta commits, 17 firmware commits and 1 host commit ahead of their `beta` branches, measured after a live fetch and by `git cherry` rather than SHA ancestry. `git grep -c flash_5v_page_page_size origin/beta -- src/proms/flash_5v_page.cpp` still returns **2**; the derivation this milestone removed is still there. gh#67 and gh#68 remain live for everyone on the beta channel. Worse, no version string separates the two states: `firestarter_fw` reads `3.0.0b31` and `firestarter_app` reads `3.0.0b46` both on `beta` and at the milestone tip, because the bumps landed before the fixes did. Whoever ships this must bump first, since a `beta` push publishes a firmware pre-release and a PyPI upload with no path filter, and a PyPI version can never be reused.

Two firmware defects on protocol `0x05`, filed by the operator on 2026-09-11 with bench evidence and tracked by no milestone until this one. A partial or unaligned write erased every byte of the touched physical page outside the write, in **both** directions, and printed `successful` — all **27** protocol-`0x05` parts, the four validated ones included (gh#68). And `flash_5v_page_page_size()` derived a page size from total device size rather than reading the part's real page, undersized on **9 of the 27**, so a contiguous write ran two page cycles into one physical page and the second erased the first (gh#67). Phase 194 fixed the second one first, deliberately inverting severity: a read-modify-write built on a derived page size would still have corrupted those 9.

**Both were fixed by refusing, and the deciding measurement is on the record rather than assumed.** D-2 permitted either shape. A firmware page-staging buffer was measured to leave **142 bytes** of RAM on `uno` for the entire call stack, and only a host pre-connect refusal can claim the device is unchanged, because the firmware never learns the total payload length. Both refusals are proved on silicon: a pre-fix build reproduced both loss directions with `sha256` baselines and exact byte ranges and printed the success line over the erased bytes; the post-fix build refused the identical commands with a named error, a non-zero exit, and a read-back hashing identical to the pre-refusal baseline.

**PAGE-03 is open by design, and it is the whole of the override.** Its bench part must be one of the 9 under-sized parts; the ordered `W29C512` has not arrived, and the `W29C020` that was run is one of the **18** already-correct parts — which is precisely what made it the right part for Phase 195 and useless for this. The record reads *0 of 9 on hardware, 9 of 9 on the database comparison* in three separate documents and conflates them in none.

**Three defects surfaced in the plans' own verify legs, none caught by the plan-checker.** A plan required a quote to be verbatim while its own gate forbade a word that quote contains. A gate leg asserted on a file written only by a hook that is inert on a milestone branch, so the executor hand-wrote the file the gate reads — disclosed as self-attested, and corroborated from four independent sources instead. And a leg matched a porcelain status pattern against the whole line including the path, so an uppercase `D` in `SEED-claim-firestarter-slug.md` made it reject every legitimate status for that one file.

**Accepted debt:** a negative write start address passes the host guard (`-256 % 128 == 0`) and the firmware's `simple_strtoul` clamps it to 0, so the write lands at address 0 and reports success. Address 0 is page-aligned and the length was already proven a whole number of pages, so it destroys nothing outside what it writes — a **wrong-destination** defect, not a page-destruction one. Filed, not fixed.

**Not claimed:** no part from the 9 was ever written on hardware; every silicon result is one part, one controller, one shield revision (`W29C020`, Leonardo, Rev 2.0-class); `SST39SF020` is `algorithm: 6` and never traverses this path at all; `AE29F2008` rests on database-proven row identity with `W29C020`, not its own bench run. `milestone.complete` was not run — hand-archived, as v1.35 through v1.38 were. `audit-open acknowledge` was not run either; **86** open artifacts are disclosed in `STATE.md` by hand, with **0** suppressed.

## v1.38 Repository Rename (Shipped: 2026-09-15)

**5 phases (189-193) · 23 plans · 15/15 requirements · app `3.0.0b42`, firmware `3.0.0b29` on `beta` · tagged `v1.38` — a bare tag, never a GitHub Release.**

Full close record: [`v1.38/CLOSE-RECORD.md`](milestones/v1.38-CLOSE-RECORD.md).

The firmware repository was `henols/firestarter` and the meta repository had no name of its own. This milestone gave the meta repository that name and moved the firmware to `henols/firestarter_fw`, on one rule: **nothing may depend on GitHub's redirect**, because a redirect is a courtesy that lasts only until someone claims the freed slug. The three firmware release endpoints address the new slug on both `beta` and `main`, the test fixtures are **derived from** those endpoint constants so a future retarget cannot pass silently, and every live tracked reference across the three repositories is correct.

**The part that cannot be fixed is documented instead.** `.gitmodules` records a submodule URL per commit, so checking out a pre-rename ref — or bisecting firmware history — resurrects the old URL. Fixing the live branches does not fix history. `.planning/notes/gitmodules-archaeology-trap.md` carries both workarounds, their executed transcripts, and the `git submodule sync` hazard that silently undoes one. It does not bite today because the old slug still redirects; it arms the moment that slug is claimed.

**Work that rode along, larger than the requirement count suggests.** An operator ruling retired source-text scanning as a testing technique, `ast`-based introspection included. The removal set was measured rather than guessed: regex classification of the test sources gave answers between 80 and 205 depending on the heuristic, so a pytest plugin recorded the resolved path of every file read per test nodeid across a full run instead — **129 tests read source or docs, 377 read data**. The 129 went, with 24 modules, a fixture repo and 11 `planted_*` fixtures. Host suite 2145 → 1886 with zero skips, coverage 84.91%.

It surfaced *because* of the rename: the sibling checkout moved out from under `fw_presence.py`'s hardcoded `FW_ROOT`, so 71 `@requires_fw` legs began skipping — and no workflow in either repository had ever set `FIRESTARTER_FW_ROOT`, so they had never run in CI at all. Host-side source-scanning gates fail open, and nothing goes red when the coverage stops.

**A planning-citation leak was root-caused after three weeks of false confidence.** 1254 comment lines across both sub-repositories, of which the v1.33 detector could see 141. Its regex bound the token group to the comment marker, so **deleting the marker-adjacent label — the normal repair — pushed the rest of the line out of its own view**. Its visibility fell across its own remediation, 48% → 26%, and it reported 73% removal against an actual 50%. A replacement gate now runs in CI in both sub-repositories and exits 2 on a vacuous scan.

**Four silent build defects, all found by reading `platformio.ini`.** Leonardo built at 86.6% of its real ceiling while the size report said 75.8%, because every AVR env overrides `maximum_size` to 32768 and the linker no longer protects Caterina's 4096 B — a `bootloader_guard.py` post-build hook now refuses an image that would overwrite the bootloader. A suite quarantined four months earlier as "intermittently flaky" was failing **5 runs out of 5** for want of three mock lines. Nine build targets became five, carrying 98 test cases that ran nowhere. And `-D DEV_TOOLS`, compiled into every shipped binary, became a per-channel decision that fails closed to the stable configuration.

**Not claimed:** no hardware was involved. The stable firmware configuration compiles and passes its native suite but has never been flashed to a board, and `PLATFORMIO_BUILD_FLAGS` reaching the compiler on `beta` is first tested by the build this close triggers. `milestone.complete` was not run — hand-archived, as v1.35, v1.36 and v1.37 were.

## v1.37 Operator Safety, Answered Reports & Claim Hygiene (Shipped: 2026-09-13)

**7 phases (182-188) · 49 plans · 35/35 requirements · merged to `beta` in all three repositories. Not tagged — stable release stays operator-gated.**

Full close record: [`v1.37/CLOSE-RECORD.md`](milestones/v1.37-CLOSE-RECORD.md).

The goal was to stop the project withholding what it already knew — from the operator about to destroy a chip, from the reporter who had waited a month, and from the maintainer reading a guard that no longer existed. Three signals arrived inside a week and were the same defect wearing three coats: a user **destroyed chips** (gh#60) for want of a warning the repo could already have given, the hardware fact having sat in-tree since 2026-07-10; a user was **taught to bypass a safety gate** (gh#62) because a correct refusal said only `Not supported`, and re-ran the operation under a different chip's identity with `--force`; and **three reporters were still waiting** on machinery v1.36 had already shipped. All three are closed, and the internal half with them.

**"Retire it" was a valid answer, and is recorded as one.** Six of TOOLS' seven requirements resolve to a decision not to build rather than a build. Phase 188 was a subtraction measured as one: **−21,281 net lines**, ten `check_*.py` gates retired by name, the frame-vector apparatus gone from both repos, and `firestarter_app/tools/` reduced to exactly six declared survivors, all swept citation-free. The suite came down 2373 → 2129 with zero errors at every boundary and coverage held at 84.74% against a 70% floor.

**What the close cost, recorded rather than absorbed.** Six stale enforcement claims that Phase 188's own deletions created (WR-01…WR-06) were **accepted as disclosed follow-on debt**, not fixed — filed by ID with measured locations rather than dropped. TOOLS-05's literal text is broader than what shipped, and the ROADMAP amendment names the narrowing instead of hiding it. `derive_sdp_partition.py` was deleted despite a not-in-scope paragraph protecting it, and the amendment states plainly that it went on the operator's judgment, not on the evidence class that paragraph forbids.

**A verification defect found at close, and a wrong first diagnosis corrected.** `188-VERIFICATION.md`'s `covered_digest` matched its covered files at neither the verification commit nor HEAD, forcing `verification.status` to `stale` permanently. The first conclusion — that it was hand-written and never valid — was **wrong and is retracted**: sweeping historical revisions showed it is the honest digest of those 26 files with `ROADMAP.md` at `cccfb7aa`, taken before the phase's own close amendments landed. It is systemic — the same reconstruction explains 183, 184 and 187, so **five of seven phases committed a digest that could never verify**. Only 188 was re-anchored, because only its content was independently re-verified at UAT; re-anchoring 182–187 would assert a check nobody performed.

**Transition-writer damage, caught by snapshot.** `phase.complete` reported clean while deleting `current_phase_name` and setting `completed_phases` **6 → 1** with `percent` **85 → 14** — on the call completing the last phase of a 7/7 milestone — and overwriting ROADMAP's multi-line `**Plans:**` entry, orphaning its continuation. All repaired against a pre-write snapshot and reconciled with `query progress`, which recomputes from disk.

**Not claimed:** no hardware was involved — this is the first milestone since v1.33 with no bench-gated leg, so nothing here is validated against a board. `milestone.complete` was not run; the close is hand-archived, as v1.35 and v1.36 were.

## v1.36 `dev test` Fidelity (Shipped: 2026-09-09)

**8 phases (174-181) · 42 plans · 46/46 requirements · app `3.0.0b38`, firmware `3.0.0b26` on `beta`. Not tagged, by operator decision.**

Full close record: [`v1.36/CLOSE-RECORD.md`](milestones/v1.36-CLOSE-RECORD.md).

`dev test` files community chip-validation issues. This milestone asked whether those reports tell the truth — whether every field corresponds to something the run actually measured. Seven ways it did not are now closed: fields that populated only on failure, a summed number presented as a per-operation one, fields no code path ever assigned, a chip ID recovered by scraping the report's own prose, an absent value meaning two different things, chips named however the operator typed them, and a `schema_version` that had not moved while the shape underneath it had.

**The governing constraint, and it held.** A filed issue body carries its own `dedup_fingerprint`, and `count_agreeing` reads that embedded hash and never re-hashes — so a re-key is **permanent for the historical corpus**. Phase 174 built the blast-radius harness before any behaviour change landed, precisely so this could be measured. The closing phase then added seven exported keys and moved **none** of the 19 frozen hashes: zero literal lines changed, re-verified at every wave, including across the two shapes that genuinely could have moved them — `duration_s`'s semantic change and a schema *removal*. HYG-03's standing refusal to ever hash `to_dict()` is recorded below and pinned by an AST test with a planted-mutant leg.

One deliberate re-key did happen and is **not** a dedup re-key: five `LADDER_PINS` disposition entries moved CANDIDATE → NO_CHANGE, closing the T-179-05 exhausted-slots ladder-flip bug. The check discriminates — the five shapes that moved carry `write` `status=SKIP`; the controls that actually wrote did not move.

**What the close cost, recorded rather than absorbed.** Nine corrections were applied that the executors' own self-checks reported as clean. Six were GSD-provenance comments in shipped source, five of them the same shape: a deletion falsifies a pre-existing comment and the author *rewords* it, which is still writing comment prose. One was a red Host CI gate waived as "pre-existing" by measuring against the wave-3 tip instead of the phase base. Three were records asserting something untrue — a closure claiming its own suite floor was re-derived when the evidence shows it was not, a summary citing a CLAUDE.md convention that does not exist, and a requirements row still instructing a change that would have turned a correct row false.

**The one verified gap was an orchestrator error.** The verifier returned `gaps_found` 18/19: the meta `firestarter_app` gitlink was never advanced, because all ten executor prompts carried a v1.6–v1.8 convention that phase 180 had already superseded. Every executor complied with a wrong instruction. Closed, independently re-checked, `passed` 19/19 — with the `gaps:` block replaced by a `re_verification:` block rather than deleted, so the record shows a gap found and closed rather than a gap that never was.

**CI caught what local testing could not.** `test_skip_census.py` failed on the PR: a `pytest.skip` guard added by 181-01 had no registered reason. It cannot fire locally, because here the app *is* a submodule and the fixtures resolve; on CI the repo is standalone. Both halves of the mechanism worked as designed.

Security: **36/36 threats closed, `threats_open: 0`** (ASVS L1). App suite **2285 passed / 0 failed**, up from 2247 at milestone start; regression gate 886/886.

**Not claimed:** `chip_id_actual` is an echo, not a read-back — on a pass the firmware echoes the host's own expected id, and the docstring says so rather than hiding it behind a passing equality. The mypy watermark is fail-open in this devcontainer and is not trustworthy local evidence. `WR-01` is open and filed: `_is_interactive` is dead code, and two tests named `..._on_a_tty` pass for the wrong reason.

### v1.36 Frozen-Shape Blast Radius (2026-09-03)

**Measured by Phase 174, the milestone's own blast-radius invariance harness, before any behaviour change lands.**

**The declared-re-key protocol and its ledger table were RETIRED on 2026-09-08.** Phase 174 created a `RK-174-` table here and a machine binding between it and `firestarter_app/tests/fixtures/rekey_ledger.py`, enforced from the meta side by `tools/rekey/check_rekey_ledger.py` plus a registered CI workflow. All of it is gone: the checker, the workflow, the app-side ledger fixture and its tests, the table, and the protocol paragraph. Operator ruling — keeping a `.planning` record accurate is GSD's responsibility, not a CI gate's, and GSD must not depend on such a gate. Two measured defects independently condemned it: the app test suite reached out to the meta tree via `Path(__file__).parent.parent.parent` with no skip guard, so app CI on a bare checkout went `13 failed, 13 passed` where the devcontainer showed `26 passed`; and three of the checker's own fail-closed proofs were tautological, because `python3` on a missing script exits `2` exactly as the checker's fail-closed path did, so they passed with their own subject deleted. The two-commit discipline it encoded — land a behaviour change first, re-key the frozen literal in a separate reviewable commit, never overwrite the original value — survives as a **review** rule, asserted in `tests/test_blast_radius_invariance.py`'s own failure message. The measurements below are kept: they are this milestone's evidence and are independent of the retired mechanism. Phases 174-179's archived records still describe the protocol as live, which is what was true when they were written; they are deliberately left unedited. One of those archived artifacts is load-bearing for FUTURE plans and is called out here because of it: the reusable green-tree ritual recorded at `179-PATTERNS.md:454` and `179-RESEARCH.md:508` lists **eight `rc=0` legs**, one of which is `check_rekey_ledger.py`. That ritual is now **seven** legs — ruff check, ruff format, mypy watermark, `snapshot_report_shapes.py --check`, `check_devtest_orchestrator.py`, `check_diagnostic_report_claims.py`, full suite. A phase 180/181 plan that copies the eight-leg version forward would invoke a script that no longer exists. **Line numbers in this section shifted.** Removing the table and the protocol paragraph took 11 lines out of the range that was lines 34-49, so the roughly three dozen line-pinned citations into `MILESTONES.md` from the 174-179 records — `:14-45`, `:36-53`, `:39`, `:41` among them — no longer land where they did, and the ones that named table rows name nothing. They are left as written: a `.planning`-to-`.planning` citation is historical by intent, and rewriting one destroys the evidence of what the record said at the time. Read them against this section's pre-2026-09-08 revision (`git show f81b1e8b^:.planning/MILESTONES.md`), not against the current line numbering. `174-05-PLAN.md:202` additionally carries an `<automated>` verify block that invokes the deleted checker and parses the deleted workflow; it is archived and will not be re-run. **The full-suite floor moved and the old one is superseded.** Deleting `tests/test_rekey_ledger.py` removed exactly 26 test instances, so the app suite's measured count went from 2265 to **2239 passed, 0 failures, 32 snapshots passed** (84.37% coverage against the `--cov-fail-under=70` gate in `ci.yml:90`, measured 2026-09-08). That is **below** the `>= 2242` floor recorded at `179-02-PLAN.md:39` and `:540` and in `179-02-SUMMARY.md:92`. Those are phase-179 green-tree assertions, not standing CI gates — the only standing count-adjacent gate is the coverage floor, which passes with 14 points of headroom — but a phase 180/181 plan that copies `>= 2242` forward would read RED against a healthy tree. **The current floor is 2239.**

`.planning/phases/174-blast-radius-invariance-harness/174-CONTEXT.md` D-12 inherited four before/after hash pairs from an earlier research session against `firestarter_app @ 0a93999`. Phase 174 re-measured every one of them this session, in the py3.11 CI-replica venv, against the actual branch base `firestarter_app @ 49bac1a` — proven content-identical to `0a93999` (one line differs, in `firestarter/__init__.py`, a field `dedup_fingerprint` deliberately excludes). An exhaustive pre-image sweep over the documented 12-step `m27c512/full` plan shape — every verdict × classification assignment, both step layouts, four protocol spellings, roughly 2.1e8 candidate canonical strings — found **zero** report shape that produces either `a00791f1c2b4`, `7d1cd4157cfa` or `a6f6c6354047`.

| Measurement | Old claim (D-12, unreproduced) | Corrected (measured this session) |
|---|---|---|
| Read-back gating, `sst27sf512-six-step` | `4dc282a5d596` → `60a031573aab` | reproduces byte-exactly; canonical pre-image recovered |
| SDP-step pruning, `m27c512/full` | `a00791f1c2b4` → `7d1cd4157cfa` | not reproducible from any m27c512 report shape |
| Canonical `part_number` naming, `m27c512/full` | `a00791f1c2b4` → `a6f6c6354047` | not reproducible; `6d3afbc52315` → `776846bf2dc8` (`m27c512` → `M27C512`) measured instead |

**Three of the four inherited pairs measured something that cannot be reproduced from any m27c512 report shape expressible in the hash's own input grammar.** The most likely explanation is a transcription or bookkeeping error in the original research session; what matters for this ledger is that no builder committed in this phase can be made to emit the two unreproduced values, so they are recorded here as an unverified prior rather than carried forward as a frozen row. This discrepancy is itself the blast-radius finding this ledger exists to surface, and it belongs in the record on the day the ledger is created.

**Corrections measured by plan 174-03, beyond the three D-12 hash pairs above.** Pre-seeding all six ledger rows surfaced four further corrections to inherited claims, plus one ratified scope widening — recorded here rather than dropped, per this project's standing rule against silently absorbing a measured disagreement. Three further corrections, measured by plans 177-01/177-02 against `177-RESEARCH.md`'s own projections for the read-back-gating change, are appended below the original five in the same table and voice, per the identical standing rule:

| Claim | As inherited | As measured |
|---|---|---|
| Count of filed `[dev test]` issues | 27 | **26** — measured by title (the `[dev test]` prefix); the `dev-test` *label* covers only 15 of 26 and is not a usable enumerator |
| m27c512 canonical-naming pair | `a00791f1c2b4` → `a6f6c6354047` (not reproducible) | `6d3afbc52315` → `776846bf2dc8` (`m27c512` → `M27C512`), both measured this session |
| UV `run_count` collapse mechanism | fires via `repeat_policy_tag` | fires via the `blank-check` verdict triple (OK → BAD); the collapsed `write`/`verify` steps carry `run_count == 0`, not `1`, so `repeat_policy_tag` never fires |
| Every filed issue title is lowercase | true | **falsified** — gh#45's raw token is `W27E040`; five of the 26 filed titles (gh#45, #46, #48, #51, #52) are not lowercase |
| D-06 corpus reproduction boundary (SCOPE correction, not a hash correction — carries no `ledger_id`) | four of the filed hashes reproduce (sst27sf512, m27c512, at28c256, w27e257 named explicitly) | **26 of 26** reproduce — widened by operator ratification (2026-09-03) once the corpus committed each row's step vector as data and a step's `fingerprint` proved to serialise as a bare classification string rather than an object. `SHAPE_IDS` and the four D-06-named builder shapes are unchanged by this widening. |
| `sst27sf512-six-step-readback-gated` inherited R2 projection (measured by plan 177-01, corrected by plan 177-02) | fingerprint dropped entirely on a pass, projected `after_hash` `60a031573aab` | **falsified** — PRUNE-03 forbids a passing step ever reporting an absent fingerprint, and applying its rule to this shape's dropped classification converges on the SAME value as the tracer's own re-pointed `after_hash` (`7fb88e0b07d6`), collapsing it onto the tracer instead of producing a distinct shape. Re-pointed instead (D-177-3 Option A) to the gate's failing branch — a step whose own cycle failed (verdict `marginal`), keeping its real `indeterminate` classification — now `ff974e416dca`. |
| `LADDER_PINS` INCONCLUSIVE arm empties once the match bucket lands (RESEARCH.md projection) | `distinct_arms` drops to 3 | **falsified** — measured `distinct_arms=4` immediately after plan 177-01's behaviour commit alone, before any repair. Two of the three INCONCLUSIVE-arm members (`gh47-sst27sf512-pass`, `sst27sf512-six-step`) are hand-specified fixtures whose literal classification strings `classify_fingerprint` never recomputes, so only `at28c256-full-all-ok-sdp` (the one real-path builder in that arm) moved automatically. Plan 177-02's re-pointed `sst27sf512-six-step-readback-gated` restores the arm to four by design, not by coincidence. |
| `gh47-sst27sf512-pass` projected `after_hash` (RESEARCH.md and this ledger's earlier prose) | `1f812aae49ca` | **falsified as a value to declare** — D-177-6 rules the shape stays inside D-177-3's stated re-pointing scope (the two `sst27sf512-six-step*` builders only); its hand-specified `step_specs` are deliberately not edited, and `FROZEN_HASHES['gh47-sst27sf512-pass']` stays `f9dbc31dcd27`, unmoved. The filed corpus row for issue gh#47 still re-keys under the PRUNE-03 rule applied to its RAW step vector (`f9dbc31dcd27` → `1f812aae49ca`, `177-REKEY-MAPPING.md`) — that is a statement about the historical filed report, independent of whether the registered shape builder moves. |

**What was done about it.** No inherited hash is frozen anywhere in this record or in `firestarter_app/tests/fixtures/report_shapes.py` — every `before_hash` value measured by this phase is produced by a committed builder, and every one was recomputed in the session that seeded it, never transcribed from a prior document. That recompute-never-transcribe rule is what makes RPT-E3's "exactly the change it declared and nothing more" checkable at all, and it is unaffected by the retirement of the ledger table above.

The read-back-gating projection recorded on 2026-09-03 as **`60a031573aab`** (measured by emptying the `write`/`verify` steps' `indeterminate` fingerprint classification on the frozen shape) is **falsified** — see the corrections table above. Plan 177-02 measured that PRUNE-03 forbids a passing step ever reporting an absent fingerprint, and that applying its rule to the dropped-fingerprint projection converges on the SAME value as the measured re-key (`7fb88e0b07d6`) rather than a distinct one. `7fb88e0b07d6` is the measured value; `60a031573aab` was never anything but a projection.

**Filed-corpus re-key (GATE-06), measured by plan 177-01 and declared by plan 177-02.** Applying the PRUNE-01+PRUNE-03 rule (a `write`/`write-partial`/`verify` step with verdict `OK` classifies `match` instead of `indeterminate`) to each of the 26 committed rows in `firestarter_app/tests/fixtures/devtest_issue_corpus.json`'s own recorded step vector re-keys **18 of 26** filed `[dev test]` issues: gh#22, #24, #25, #26, #27, #29, #31, #39, #40, #42, #45, #46, #47, #48, #49, #50, #51, #52. This matches `177-RESEARCH.md`'s projected count and issue list exactly — no correction row is needed for the count itself. `count_agreeing` reads the `dedup_fingerprint` embedded in each filed issue body and never re-hashes, so this re-key is **permanent for the historical corpus**; no migration of an already-filed issue is possible, and `tests/fixtures/devtest_issue_corpus.json` itself is unchanged (it is historical evidence, not a re-hashed derivation). The full old-to-new mapping, one row per re-keyed issue with chip name and both hashes, is published at `.planning/phases/177-evidence-gated-read-back/177-REKEY-MAPPING.md`. gh#39 and gh#40 share a `filed_hash` before this re-key and move TOGETHER after it — the dedup group survives intact, merely re-keyed.

**What this phase measured about itself.** The five new test modules as measured at phase close (dedup_fingerprint/build_db_diff pins, ledger-binding tests, the filed-issue corpus, the part-number delta drift gate — 110 tests; the ledger-binding module was deleted on 2026-09-08, so this count is historical) run together in 7.92 s, against a measured full-suite baseline of **740.92 s**: a 0.58%-of-baseline `derive_plan` sweep and this phase's own new modules both stay far under any threshold that would justify a slow marker. `tests/test_skip_census.py`'s three failures are **pre-existing** — a 180 s child-run timeout cap against the 740.92 s suite, unrelated to anything this phase touched, re-run and re-confirmed unchanged (still exactly three, same cause) at phase close. No file under `firestarter_app/firestarter/` and no file in the `firestarter` firmware submodule was modified by any of this phase's five plans.

**Phase 178 (Fault Attribution) — ATTR-04 measured and held, not merely asserted.** Phase 178 asserted NO re-key from its post-177 anchor (`14d306256076`), and this phase's own frozen corpus is the confirmation: plan 178-03 grew the corpus from 17 to 18 shapes by registering `attr01-status-axis-transport-fault` (hash `93cef8030c40`, a real `derive_plan`/`run_plan` transport fault through the actual re-pointed `(SerialError, HardwareOperationError)` arm), and every one of the 17 inherited `dedup_fingerprint` hashes reproduced byte-unmoved against the 18-shape corpus (`stale_frozen=`, `inherited_drifted=`, `178-03-attr04-seal.txt`). The anchor was left undeclared — recording a non-move as a re-key is a bookkeeping error, not a re-key (D-09) — and the then-current ledger stayed byte-unchanged at 8 rows (`ledger_diff=0`). Three research projections did not survive contact with the codebase and are recorded here rather than silently dropped: **T3** ("an `ERROR`-bearing run is not submittable") is **void** — ATTR-05 forbids suppressing the submit prompt, so `is_submittable` was left byte-unchanged and proven so (`test_is_submittable_is_unchanged_by_the_status_axis`), and the milestone research's run-validity term never lands (D-11). **T4** (a machine-readable non-submittable reason key) is **out of scope** — no ATTR requirement names it, and an unrequested exported field would grow the frozen-key surface this milestone is holding still (D-15). Reviving `classify_fingerprint`'s dead **`FP_TRANSPORT`** bucket is likewise **out of scope** — `_run_cycle_block` hard-codes `runs=1` at `chip_test.py:1622`, every fingerprint-bearing op sits inside the cycle block, and a probe across `sst27sf512`/`at28c256`/`w27e257` confirmed every fingerprint-bearing dispatch receives `runs=1` (D-16); the ROADMAP's dependency on Phase 177's fingerprint gate is real but narrower than it reads — only the reachable `blank/contact` and `match` buckets are consumable, not `transport`.

**HYG-03 (D-18) — `dedup_fingerprint` must NEVER be refactored to hash `to_dict()` or to reflect over dataclass fields.** The function's pre-image is an explicit five-entry allow-list (`chip` | `protocol` | `op=verdict:classification` | `repeat_policy_tag` | `coverage_tag`), built with no reflection over `DiagnosticReport`'s dataclass fields — a field's ABSENCE from that list is the entire exclusion mechanism, not a filter that could later be inverted. `to_dict()` already produces the whole mapping, and a hand-written five-entry list sitting beside it will look like duplication to a future reader tempted to "simplify" it by hashing the serialized mapping directly, or by reflecting over the dataclass's own fields — do not. `count_agreeing` reads the `dedup_fingerprint` embedded in an already-filed issue body and never re-hashes, so a reflective rewrite is **permanent for the historical corpus**: no migration of an already-filed issue is possible. This phase alone is the measurement that makes the temptation concrete rather than hypothetical — Phase 181 added seven exported keys, among them `elapsed`, `is_uv`, `canonical_part_number`, `chip_id_detected`, `divergence` and the four `fingerprint_*` siblings — every one of which would have moved every one of the 19 frozen hashes under a reflective implementation, and instead moved none, because none of them sits inside the five-entry allow-list. The gate that reddens if someone tries the refactor anyway: `test_dedup_fingerprint_hashes_an_explicit_allow_list_and_never_the_serialized_mapping` and its planted-mutant leg `test_a_planted_reflective_body_reddens_the_allow_list_pin` in `tests/test_blast_radius_invariance.py`, plus the pre-existing 19-way `test_dedup_fingerprint_is_frozen` parametrization and the two-commit review rule carried in that oracle's own failure message.

## v1.35 Documentation Consolidation & Wiki Migration (Shipped: 2026-09-02)

**Phases completed:** 7 phases authored (167–173), 7 delivered. **41 plans** across the five that ran the machinery (167: 6 · 168: 13 · 171: 4 · 172: 9 · 173: 9). **Phases 169 and 170 have no plans at all** — they were executed ad hoc; see Known Gaps.
**Timeline:** 2026-08-30 → 2026-09-02 (4 days)
**Requirements:** **29/32 Complete** — 2 WITHDRAWN (WIKI-03, WIKI-04), 1 NOT MET by operator decision (FRONT-02). All 32 mapped to exactly one phase, 0 orphans.
**Closeout type:** `override_closeout` — **not** for any gap in the work's outcome. Three record gaps drive it: phases 169/170 ran outside the machinery, and phase 172 has no `172-VERIFICATION.md`. See Known Gaps.
**Code:** meta 265 commits, 245 files, +43971/−247 (227 of those files, +42822/−42, are `.planning/`) · firmware **6 commits, 9 files, +480/−452** (`a218b4f` → `4f73c80`) · host app **18 commits, 76 files, +858/−4681** (`cb189a9` → `0a93999`) — the app's net −3823 is the documentation coming out.
**Close posture:** **MERGED AND PUSHED.** Meta tagged `v1.35` at `6e84030b`; the `beta` lockstep cut performed and channel-verified under the new rulesets; three `.github`-only pull requests merged through the ordinary route into three protected `main` branches (`firestarter_prom#54`, `firestarter#58`, `firestarter_app#57`) between 08:56:58Z and 08:57:06Z on 2026-09-02. No stable release in any repository.
**Known verification overrides:** **72 newly acknowledged, 0 carried forward from a prior close.** Recorded by disclosure in `STATE.md` §Deferred Items rather than through the `audit-open acknowledge` writer, which was found at this close to destroy the artifacts it annotates — see Backlog **999.49**.

**Delivered:** A single documented front door. `firestarter_prom` had **no README at all**; it now has one,
and its GitHub wiki is the home for project documentation — 11 pages live, indexed from `Home` and a
hand-written `_Sidebar`. All 12 migrating `doc/` files moved and **both sub-repo `doc/` directories are
gone** (fw 3 files, app 10). The two sub-repo READMEs were cut to repo scope, the app's from 779 lines,
its table of contents corrected from advertising three sections that did not exist. Three root-level
strays disposed: `things.md` and `SECURITY.md` deleted, `autocomplete.md` published as `Shell-Completion`.
Policy is now **configured, not merely stated** — one tracker, three issue templates live on the chooser,
`.github/CONTRIBUTING.md` pointers byte-identical by sha256 across all three repos, and `main` behind an
`enforcement: active` ruleset in all three requiring a pull request and forbidding direct push, force-push
and deletion, with `current_user_can_bypass: never`.

**The milestone-level non-claim, stated once here in this milestone's own canonical wording:
relocation is not verification.** HONEST-01 compared a claim-token multiset between each pre-deletion
`doc/` source (read via `git show <sha>:<path>`) and its published wiki page, proving **no claim was
upgraded in the move** — no `support_status` softened, no `PROTOCOL-LEDGER` `UNVERIFIED` bucket quietly
promoted. That is the whole of what was proven. **Nothing on the wiki was confirmed accurate.** A wrong
sentence that moved unchanged is still wrong, and is now wrong somewhere more discoverable.

**Key accomplishments:**

1. **The wiki is real and the `doc/` directories are gone** — 12 files migrated by copy-then-edit with a
   bounded edit set, stamped with provenance footers, re-verified from independent fresh clones rather
   than the working copy that made the edits. `firestarter/doc/` and `firestarter_app/doc/` both deleted.
2. **The move was proven claim-preserving, not assumed to be** — HONEST-01's multiset comparison, plus a
   deliberately weakened-claim RED before the live GREEN, so a passing result meant something.
3. **Protected `main` proven by rejection, not by configuration read-back** — Phase 173 pushed a true
   fast-forward empty commit at `main` in all three repositories and captured GitHub's own GH013
   rule-violation refusal. The pull-request route was then demonstrated four times by actually merging.
4. **The close procedure was fixed by construction before it could break** — POLICY-03 would have broken
   the next `/gsd-complete-milestone`, so `git.base_branch` was repointed to `beta` and verified by a
   *distinguishing* before/after read-back. This incidentally corrected three fork-point consumers that
   had been branching every new phase and quick task off the wrong ref.
5. **The authoring model was reversed mid-milestone, and the record says so** — Phase 167 built and
   shipped in-repo markdown source, one-command publish, and a working drift check; the operator then
   chose wiki-only authoring for simplicity, and Phase 168 deleted the machinery Phase 167 had just
   proven. WIKI-03/04 are withdrawn, not failed.
6. **A test suite that could no longer collect was severed cleanly** — `test_dispatch_mirror.py`'s
   module-scope `fw_path("doc", "PROTOCOLS.md")` would have aborted the entire app suite at collection
   the moment `firestarter/doc/` vanished. Found and severed before the deletion, not after.

### Known Gaps

- **FRONT-02 — NOT MET, declined outright by the operator (2026-08-31).** It cannot hold at the same time
  as FRONT-03; the wiki `Home` page owns the getting-started path instead. Struck through and recorded in
  `REQUIREMENTS.md`, not silently dropped.
- **WIKI-03 and WIKI-04 — WITHDRAWN (2026-08-30).** Retired by the authoring reversal after being built
  and shown working.
- **Phases 169 (FRONT) and 170 (REPO) were executed ad hoc** — direct commits, no plans, no summaries, no
  phase directory, no `gsd-verifier` pass. Their requirement marks rest on an after-the-fact, same-agent
  criterion re-check (`.planning/notes/v135-phases-169-170-executed-ad-hoc.md`), not on the machinery
  every other phase went through.
- **Phase 172 has no `172-VERIFICATION.md`.** It ran 9 plans with summaries and 26 evidence files, and its
  own `evidence/172-09-closing-sweep.txt` was written before any requirement box was flipped — but no
  independent verifier pass exists, so `init.manager` reads it `phase_complete: false`. Its nine ROADMAP
  checkboxes were flipped at this close, the write `CLOSE-RECORD.md` §1 had assigned to the orchestrator
  and never performed.
- **The automated guard this milestone built was retired the day it closed.** `wiki-check.yml` and every
  checker under `tools/wiki/` were deleted on 2026-09-02 (`5426d7ef`); `MIGRATION-TABLE.md` is the only
  survivor. **There is now no automated wiki guard of any kind.** HONEST-02 is a disjunction — a check
  **or** a stamp — and only the stamp half remains, on six pages. See `CLOSE-RECORD.md` §8.
- **Two findings filed at close, not fixed:** **999.49** — `gsd-tools query audit-open acknowledge`
  destroys artifact content it is asked only to annotate (it wiped 100 lines of YAML frontmatter from a
  quick-task summary; the pass was reverted uncommitted). **999.50** — the retirement left two live
  references to the deleted `tools/wiki/dispatch_mirror.py`, one of which leaves a firmware file declared
  guarded in `scan_paths.py` and actually unguarded.
- **Carried from earlier milestones:** 999.46 (the new rulesets block the stable-release version bump in
  both sub-repos), 999.47 (`firestarter_prom`'s `Catalog sync check` was already red on `main` before this
  milestone's merges), 999.9 (the repository rename that will invalidate every link written here —
  phases 169, 170 and 172 are the recorded re-sweep set).

**Archives:** [`milestones/v1.35-ROADMAP.md`](milestones/v1.35-ROADMAP.md) ·
[`milestones/v1.35-REQUIREMENTS.md`](milestones/v1.35-REQUIREMENTS.md) ·
[`v1.35/CLOSE-RECORD.md`](milestones/v1.35-CLOSE-RECORD.md) (21-row honesty ledger)

## v1.34 Pre-Merge Hardware Regression Validation (Closed: 2026-08-29 — EARLY / SCOPE-REDUCED)

**Phases completed:** 7 phases authored (160–166); **4 complete** (160, 161, 165, 166), **1 partial** (162, at 5 of 11 chips), **2 not run** (163 SHIELD, 164 REV0). 28 plans authored, **24 completed** — 160 at 13/13, 161 at 5/5, 162 at 6 summarised of 10 (plan 162-07 executed but never summarised; the sweep stopped mid-plan on operator direction).
**Timeline:** 2026-08-25 → 2026-08-29 (5 days)
**Requirements:** **19/31 Complete** — 5 PARTIAL/MET-in-scope (CHIP-01…05), 6 NOT RUN (SHIELD-01/02/04, REV0-01/02/03), 1 DEVIATED (CLOSE-04). See Known Gaps.
**Closeout type:** `operator_directed_early_close` — **not** a gap in the work that ran. On 2026-08-29 the operator directed "stop testing, close ASAP", and the milestone closed on the evidence already banked rather than on the planned sweep. Every phase that ran, ran clean; more than half the planned evidence base was simply never measured, and this record says so in every place a reader could mistake it for complete.
**Code:** meta 202 commits, 901 files, +80496/−376 (896 of those files, +80492/−258, are `.planning/`) · firmware **2 commits, 2 files, +18/−1** (`5759dc8` → `a218b4f`) — **+16 B flash on all three AVR targets, +0 RAM** · host app **0 commits** (`cb189a9` is v1.33 tail work from 2026-08-25, not v1.34). v1.34 touched no product code except the one pre-existing defect it found.
**Close posture:** **MERGED, BY OPERATOR DIRECTION — a deliberate break with the local-only precedent, recorded as a deviation.** The three v1.33 PRs merged to `beta`: [`firestarter_prom#43`](https://github.com/henols/firestarter_prom/pull/43) (`ee562a03`), [`firestarter#56`](https://github.com/henols/firestarter/pull/56) (`01be7885`), [`firestarter_app#54`](https://github.com/henols/firestarter_app/pull/54) (`db262331`), each firing its own beta pre-release cut; meta followed via PR **#44** (`eb87413e`). Meta's beta gitlinks read fw `a218b4f` / app `cb189a9` — the firmware **with** the blank-check fix this gate found. **No sub-repo tag, no meta `v1.34` tag, and no stable release** — those stay operator-gated and were deliberately untaken. (v1.33 was tagged at its close; v1.34 is not.)

**Delivered:** A hardware gate in front of a merge that had never touched an Arduino. v1.33 shipped −2938 B
flash / −13 B RAM across all three AVR targets on a premise of byte-level equivalence — heap allocator
removed, the 438 B 64-bit runtime dropped, `jsmntok_t` narrowed 8 → 6 B, `key_parsers[]` rewritten, handle
types narrowed — every claim backed by native tests, golden traces and cold builds, **and none by silicon.**
v1.34 bought the A/B comparison v1.31 declined to make: every cell ran a **control arm** (the exact
merge-bases the v1.33 branches forked from, firmware `8695ee5` / host `6bfa645`) before the v1.33 arm, so
"this failed" could be told apart from "this has always failed here."

**The verdict: MERGE WITH CAVEATS.** Not "merge" — six chips and two shields were never measured. Not
"do-not-merge" — every position that *was* measured came back clean of v1.33 attribution, and the one hard
failure was affirmatively shown to predate v1.33 by two independent methods. Withholding a merge on
evidence that never contradicted it would be overcaution; calling it validated would be overclaiming.

**The milestone-level non-claim, stated once here in this milestone's own canonical wording:**
**program-window VPP/VCC under load was never measured**, because the Phase-97 DTR-reset-on-close tooling
gap still stands. Every voltage figure in this milestone is a static or idle reading. **v1.34 therefore
makes no electrical claim whatsoever.** Its results are read-back SHA facts, not rail facts.

**Key accomplishments (curated):**

1. **Zero v1.33-caused regressions in any position actually measured** — 12 board positions (3 boards × 2
   arms × 2 chips, cells A1 Uno / A2 uno328pb / A3-B2 Leonardo, all Rev 2.0) plus 6 chip-sweep rows. **RCA-02
   is therefore satisfied vacuously, and the close record says so rather than dressing it up**: there was no
   v1.33-caused regression to root-cause. A real result about what was measured; not a result about what was not.

2. **The one hard failure was proven pre-existing, then root-caused, then fixed — in that order.** W27E040
   blank-check died at ~98% with `ERROR: Empty input` (`MSG_ERR_EMPTY_INPUT`, 164/0xA4). Classified
   pre-existing on **two independent grounds**: a control-arm re-run reproduced it, and `git show
   8695ee5:src/operation_utils.cpp` shows the control firmware carries the byte-identical
   `LOG_DATA_ID_U32_U32(MSG_DATA_PROGRESS, …)` with no `op_wait_for_ack` after it. **Mechanism:** standalone
   blank-check emitted one progress frame per 2048 B chunk and never consumed the host's per-frame ack, so
   the firmware ran unthrottled without touching the incoming byte stream; past ~4–5 KB of cumulative TX,
   `handle->cmd` reverted to `CMD_IDLE` outside `command_done()` and the unread backlog decoded into the
   overloaded 0xA4. Deterministic at 251/256 chunks on a 512 KB part. **Fixed on the v1.33 PR branch** —
   `1e8bbae` (consume the ack) and `a218b4f` (chunk 2048 → 8192, cutting a 512 KB part from 256 frames and
   256 round-trips to 64 of each at zero added instructions) — and **re-validated in the cell that caught
   it**: 4/4 clean at 59.66–59.68 s, bar landing exactly on `0x80000/0x80000`, `MSG_ERR_NOT_BLANK` still
   correctly reported with its offset+value payload.

3. **A flash was made provable by device read-back, not by an upload exit code.** Phase 160 built both arms ×
   three AVR targets into six committed arm-tagged images with `SHA256SUMS.txt`, added an address-attributable
   image generator, a signature probe that identifies a board without a handshake, an independent avrdude
   read-back judge, and a deliberate **wrong-arm cross-flash on all three targets** with the MISMATCH observed
   and recorded — the negative control that makes every later "the right firmware was running" claim mean
   something.

4. **The A2 program failure was captured on both arms rather than assumed from Backlog 999.2** — which is the
   whole point of BOARD-02, and the discipline that kept a known fault from being adopted as a v1.34 finding.

5. **A finding nobody was looking for: the VPP ADC error is ratiometric, ~+7.5% (range 6.8–8.3%).** Three
   paired firmware-vs-multimeter readings across **two independently calibrated boards** cluster near the same
   ratio, which is *consistent with* — **not proof of** — a shield-wide gain/divider fault rather than
   per-board EEPROM miscalibration. It **materially weakens** the leading low-VPP hypothesis for A2's four
   write failures: if the error is shield-wide, A1's firmware-reported 12.0 V also meant a real rail near
   ~11.0–11.2 V, and A1 **passed** all four positions there. **Standing operational rule while this is open:**
   do **not** correct the pot down toward 12.0 V against the firmware's own reading — that would drive the real
   rail toward ~11.2 V and make the rig worse while looking like a fix. Set it from a multimeter, never from
   the firmware's `vpp` figure.

6. **Findings were filed, not narrated.** Six new backlog items — **999.37** (the unexplained 64 KiB `Empty
   input` occurrences), **999.38** (the ratiometric VPP ADC error), **999.39** (the app writing
   `~/.firestarter/config.json` despite `FIRESTARTER_CONFIG_DIR`, three recurrences), **999.40**
   (`MSG_ERR_EMPTY_INPUT` is overloaded — frame-integrity failures need their own id), **999.41**
   (`size_baseline.json` stale by +16 B on all three targets after the fix), **999.42** (the unfinished sweep
   itself). Pre-existing failures were linked to **999.2** and **CR-01** and explicitly not fixed.

### Known Gaps

**These are carried, not hidden, and the first one is not a gap in execution — it is the shape of the close.**

- **(1) More than half the planned evidence base was never measured.** Six of eleven chips unswept (ST
  M27C512, SST39SF040, W29C040, W29C020, AM27C020, 2516) and two of three shields unswept (Rev 2.2, Modified
  Rev 0). **Every v1.34 result is Rev 2.0 only**, so v1.33 merged with **zero** bench evidence on Rev 2.2 and
  Modified Rev 0. Three of the unswept parts carry known prior trouble — SST39SF040, W29C040 (permanently
  locked §6.6 boot block, CR-01) and AM27C020 (non-deterministic marginality). No claim is made about any of
  them under v1.33. → **999.42**.
- **(2) The 64 KiB `Empty input` occurrences are unexplained and were NOT folded into the 512 KB
  explanation.** The identical text appeared on `w27c512`, `w27e512`, `sst27sf512` and one superseded control
  row, at differing steps, without changing any step verdict. All three parts are 64 KiB = 32 chunks ≈ 544 B
  of cumulative TX — **an order of magnitude below** the ~4–5 KB threshold that triggers the defect in gap
  (3)'s sibling. Recorded **INCONCLUSIVE** and not resolved by assumption in either direction; Phase 162-07's
  earlier "intermittent arm-independent frame corruption" reading is superseded **for the 512 KB case only**.
  Arm-independent, so nothing about it is v1.33-attributable. → **999.37**.
- **(3) The two fix commits were absent from every measurement in this milestone.** Both pinned arm images
  predate them; the bench board was restored to the v133 arm (`5759dc8`) and proven so by independent avrdude
  read-back (`judged_match=True`, 25098 B). The fix is verified on a W27C040/W27E040 and **on no other part** —
  second-chip confirmation needs an operator chip swap. Consequence for anyone resuming **999.42** against the
  same pinned images: expect blank-check to fail at ~98% on the three 512 KiB parts on **both** arms; that is
  the known, explained, pre-existing defect, not a new finding. Re-pinning both arms to carry the fix
  **invalidates every row already recorded**, which is why v1.34 did not do it.
- **(4) The VPP ADC mechanism is undetermined**, and so, consequently, is A2's write-failure cause — the
  leading hypothesis was low VPP and finding (5) above substantially weakens it. → **999.38**.
- **(5) A2's N=3 read instability remains UNDETERMINED.** The same physical W27C512 on the same v133 arm read
  three distinct SHAs on the uno328pb; the same arm/chip pairing read perfectly stable on the Leonardo. That
  points away from the chip and toward the uno328pb or its state — a relevant but **non-resolving** data point.
- **(6) Only the diverging chip got a control re-run**, per CHIP-04 by design. The four PASSes were **not**
  A/B-contrasted, and this record does not imply they were.
- **(7) `hw_revision` still cannot identify a shield.** Board identity was verified per cell by avrdude
  signature; **no firmware-reported field can distinguish the operator's three shields**, and the A3 ADC check
  collides at 10 kΩ between Rev 2.2 and Modified Rev 0.
- **(8) The Modified Rev 0 board has still never been physically inspected.** No photographs of it exist
  anywhere. See the post-close note below for what *was* settled at the desk.

### The CLOSE-04 Deviation, Recorded Rather Than Hidden

CLOSE-04 read: *"v1.34 performs no merge, no push to `beta`, no sub-repo tag, no beta cut and no release —
every outward-facing step is left to the operator."* **v1.34 did not meet it.** Asked directly whether closing
should also merge the three v1.33 PRs, and told in the same exchange that the step is outward-facing and
auto-fires a beta pre-release cut, the operator answered *"Yes — merge as part of the close."*

The requirement's **purpose** — that no outward-facing step happens without the operator's decision — is
satisfied: the operator made the decision. Its **letter** is not. It is recorded as a **deviation** and left
unticked rather than marked complete, so the ledger stays honest. Not performed even so: **no sub-repo tag, no
meta `v1.34` tag, no stable release.**

### Post-Close Desk Work: The Rev 0 Schematic Blob Was Wrong (2026-08-29)

**Found after the close, at the desk, with no board in hand** (`0e114fb7`). Every prior citation of "the
upstream Rev 0 schematic" — in `ROADMAP.md`, `REQUIREMENTS.md`, `v1.7-SHIELD-REVS.md` and elsewhere — named
blob **`d2a7f691`** / `UniversalProgrammerRev0b0.zip::W27C512Programmer.kicad_sch`. **Both halves are wrong.**
`d2a7f691` is `hardware/W27C512Programmer.kicad_sch` on `origin/rev2.0`, and it is a bare `.kicad_sch` rather
than a member of that zip. The true Rev 0 schematic is blob **`cfe6139f`** at commit **`486f3d1`**.

**This is not cosmetic.** The two differ by **23 components, concentrated exactly where a rework trace
looks.** Rev 0 carries JP1 (24-pin ROM VCC), JP2 (≥SST39SF020 & 28C512 need A17), JP3 (W27C010/AT27C010 needs
p1 VPE/VPP) and global label A18. `rev2.0` instead carries JP4/JP5, R41 = 4k7 at A3, Q9–Q12 and RN2-5/7-8 at
10k rather than 4k7, and drops RN1/RN9. **A tracer working from `d2a7f691` would hunt a Rev 0 board for
JP4/JP5 that are not on it and never inspect JP1/JP2/JP3 that are** — and JP2 is the A17 strap, directly
relevant to the Bug A upper-address jitter.

**Ten cells discharged.** The ten `TBD pending Phase 35` sentinel cells in `v1.7-SHIELD-REVS.md` §4/§5 were
re-measured at start rather than assumed — 10 across two rows, confirming the 2026-08-25 "ten cells"
correction and refuting REQUIREMENTS.md's original "six rows" — and taken **10 → 0** via REV0-03's
*named-reason* branch: each cell now states the specific artefact that is missing (a photograph, a continuity
probe, a DMM reading), never the word "pending". Two resolved to real attested values (the 10k A3 pull-up — an
*addition*, since Rev 0 has no A3 divider at all), and the §5 "gated" cell resolved to gated on that pull-up's
electrical nature, with its single-datum basis stated. `.planning/milestones/v1.7-artifacts/MODIFICATIONS.md` was upgraded from the
stub it had been since v1.7 into a reference correction with the full delta table, a corrected identity table
including the Rev 2.2 10 kΩ ADC collision, an empty-but-structured rework inventory, and a seven-item
inspection priority list derived from the Rev 0 netlist.

**REV0-03 is left UNTICKED despite this**, because the work landed *after* the milestone closed, and because
the trace itself is still blocked on operator photographs that do not exist. The 2026-06-01 correction notice
recording that no physical inspection has ever occurred deliberately still stands. Phase 164's criterion 2 in
`ROADMAP.md` still carries the stale `d2a7f691` citation, annotated in place — that phase closed unrun, and
the citation is retained as inert history rather than rewritten.

**Backlog:** files **999.37**, **999.38**, **999.39**, **999.40**, **999.41** and **999.42**. Links
pre-existing failures to **999.2** (uno328pb program-path brownout) and **CR-01** (W29C040 locked boot block)
without fixing them. Retires nothing.

## v1.33 Source Hygiene & Firmware Size Reduction (Shipped: 2026-08-24)

**Phases completed:** 6 phases executed (154–159), 45 plans, ≥66 tasks (66 enumerated across the 30 of 45 plan summaries that carry an explicit task list; the remaining 15 use a different summary shape, so the true total is higher and is not claimed here)
**Timeline:** 2026-08-23 → 2026-08-24 (2 days)
**Requirements:** 42/43 Complete — SWEEP-13 deliberately left open (see Known Gaps)
**Closeout type:** `override_closeout` — **not** for any gap in this milestone's own work, which verified 13/13, 6/6, 4/4, 7/7, 8/8 and 17/17 across its six phases. Ten **inherited** open artifacts were acknowledged and deferred at close: Phase 08/09/84 verification (`human_needed`), Phase 08 UAT (`partial`), the `w27c512-devtest-all-bad` debug session (recorded NOT REPRODUCIBLE), and 28 pending todos. Full list in `.planning/STATE.md` §Deferred Items. No milestone audit was run — matching the v1.30/v1.31/v1.32 precedent.
**Code:** meta 155 commits, 673 files, +100908/−2200 · firmware 22 commits, 120 files, +5309/−1344 (`8695ee5` → `2ccda8d4`) · host app 1 commit, 60 files, +1419/−474 (`6bfa645` → `38f0d83`)
**Close posture:** **LOCAL ONLY.** Meta tagged `v1.33`. **Nothing pushed, no PR, no merge, no beta cut, no release** — every outward-facing step is operator-gated and was deliberately untaken at close. All three repos remain on `gsd/v1.33-source-hygiene-firmware-size-reduction`.

**Delivered:** Make the source shorter without changing what it does — and prove the "without changing
what it does" half rather than assert it. Two halves that shared that one property. First, the promoted
Backlog 999.34 provenance-comment sweep: the GSD `// Phase NNN (REQ-NN):` comments that ~150 phases had
stamped into shipped source across both sub-repos were swept, and the `.planning/` `file:LINE` citations
that shift as a result were repaired by a purpose-built remap tool applied **exactly once**, at the end,
over the composite pre-154 → post-158 diff. Second, four measured firmware size reductions plus a fifth
found during landing. **Zero product-code behaviour changed anywhere in the milestone** — byte-level
equivalence was the entire premise, and the algorithm-first dispatch contract was not touched at all.

**The milestone-level non-claim, stated once here in this milestone's own canonical wording:**
**no bench phase existed and no silicon was tested.** Two changes have runtime consequences a bench
could have measured — the 32-bit voltage reformulation (Phase 155) and the `flash_5v_page` per-byte
model (Phase 157) — and neither was measured on hardware. Every claim in this milestone is a
**build-and-test fact**, not a bench fact.

**Key accomplishments (curated):**

1. **The firmware is now heap-free, and the removal closed a latent unchecked-allocation dereference.**
   `mem_util_blank_check` malloc'd **4 bytes** — and dragged in the whole **586 B** avr-libc allocator
   behind it — while dereferencing the returned pointer **unchecked** on a part with ~470 B of free RAM.
   In the same phase, `rurp_read_voltage_mv` turned out to be the **only** user-code caller of the entire
   **438 B** 64-bit runtime. Both libraries left the image. `realloc` and `calloc` were checked for
   explicitly and confirmed absent from all three linked ELFs, rather than assumed gone by silence.
2. **Two report blocks that were copy-pasted four times each are collapsed** (Phase 156). Between them the
   VPP-report and chip-ID-report blocks held **24 of the image's 30 `__udivmodhi4` call sites** — the
   duplication was paying for the 16-bit division helper over and over. The same phase repaired the
   boolean convention the duplication had been hiding.
3. **`json_parser.c`'s half-done refactor is finished** (Phase 157). The `key_parsers[]` table re-matched
   every wire key a *second* time inside each `get_*` stub, costing **1012 B** across 11 PROGMEM
   function-pointer stubs — while five *identical* directly-called siblings cost zero.
4. **Phase 158 refuted three of the ROADMAP's own predictions with measurement instead of inheriting
   them.** `jsmntok_t` narrowed 8 → 6 B on AVR for a measured **−138/−138/−136 B flash and −128 B RAM**
   cold-to-cold — the ROADMAP had predicted **+30 B flash**, and that prediction is superseded, not
   quietly dropped. LAND-06's mask rewrite was **DECLINED with its measurement** (+22/+24/+22 B flash, no
   linkage saving) rather than skipped, and LAND-07's "57 tokens / 7 headroom" figure was refuted by three
   independently re-derived bounds (50/14, 51/13, 55/9) and closed on the forward-compatibility budget
   rather than on arithmetic. Thirteen corrections C-1..C-13 and ten decisions OD-1..OD-10 are closed out
   in `.planning/milestones/v1.33-artifacts/158-after-figures.md`, each carrying the verbatim command that produced it.
   `size_baseline.json` was re-recorded from **cold** builds with fixtures severed onto a new `*_v158*`
   family, and BASE-01 was fixed on a third native test-inventory axis (141 → 184) with its growth axis
   byte-unchanged.
5. **Leonardo Caterina headroom went 502 B → 3440 B (6.9×)** — which mattered concretely, because v1.32
   Phase 151 left that target at **zero** MERGE-05 headroom. Worth recording alongside it: **MERGE-05 is
   one-sided** (`check_size_baseline.py` gates `flash_delta > allowance`), so a shrink needs no named
   exemption — the first size movement in this project's history that did not.
6. **The citation remap ran exactly once and is provably a fixed point.** 2,706 citations rewritten across
   562 documents, out of 14,391 records and 1,291 documents examined; the corpus was then proven a
   **byte-stable dry-run fixed point**, and the close-blocking marker `.planning/milestones/v1.33-artifacts/CITATIONS-STALE.md`
   was removed as the phase's final mutation. The 515-record exception ledger closed 339 reviewed / 176
   retired across 8 causes with **zero** `needs_review`, settled at the phase's single manual checkpoint
   over four operator rounds. Phase 159's footprint was 585 files, **100% inside `.planning/`** — zero
   product code touched — with the tools suite 133/133 green.

### Known Gaps

**These are carried, not hidden. None of them is a discovery made at close — each was recorded by the
phase that found it.**

- **The remap's honesty caveat — ROADMAP criterion 2 is NOT universally satisfied.** 269 of the 515
  resolved exception records rest on **`diff_provenance_reworded`** — diff provenance, **not** verbatim
  source-text equality — because Phase 154 deliberately *reworded* the comments those citations point at.
  Each of the 269 carries an explicit `verbatim_oracle_applied: false` field. No closure text in this
  milestone claims the verbatim oracle was universally applied, and this entry does not either.
- **SWEEP-13 is deliberately unticked.** One commit per sub-repo (PROVEN, anchored to the plan-01 shas
  rather than to the `HEAD~1` tautology), commit ordering before the host suite (PROVEN, 1976 passed),
  and the archived-`milestones/` question (recorded as a verified absence with cause) all hold. The
  fourth clause — one meta commit — is **measurably not met at 9**, and rewriting meta history to
  manufacture a single commit was dispositioned **accept/declined** (T-154-53) because meta history
  contains GSD's own doc commits. A false tick would be worse than an open box.
- **149 `citation_absent_from_citing_document` retirements** are the ledger's largest retire class:
  citations deleted from their *citing* documents by ordinary hand-editing since the sweep. That is a
  measurement about `.planning/` hygiene, not a remap failure — recorded as such.
- **One permanent residual on a disk-level dry run.** `.planning/STATE.md` was committed as a
  citation-only blob while its disk bytes stayed frozen at the dirty preimage
  (`auth-state-md-dirty` → `preserve_unstaged`), so a disk-level dry run reports exactly one residual
  document, permanently. Expected, not a regression.
- **Two deliberately-stale historical figures were excluded from the remap by design.** The two
  `recordscan:supersedes`-protected lines in `notes/py32f071-port-branch-state.md` (corrections recorded
  in that same file) were excluded by a new general marker-driven engine rule, keeping Phase 130's
  archive gate at PASS/superseded:12. Their literal figures are not restated anywhere in the close text,
  because the Phase-130 needles treat any unexempted occurrence as a FAIL.
- **Ten inherited open artifacts acknowledged and deferred** — Phases 08/09/84 verification, Phase 08
  UAT, one debug session, 28 pending todos. See `.planning/STATE.md` §Deferred Items.

### Corrections Applied At Close (2026-08-24)

- **The `firestarter_app` Phase-154 sha in SWEEP-13 was stale.** SWEEP-13 clause (a) recorded
  `bc9d59293b9a08b16d6d7eb16eaf6c6f53e88e65`; that commit was **amended** on 2026-08-23 at 07:51 UTC to
  `38f0d839a1984fa71cb16ea98afa4d8a4e6bcfe2`, and `bc9d592` is not an ancestor of app HEAD. **The
  clause's substance was re-verified and is unaffected:** the count is still exactly 1, the parent is
  still `6bfa645`, and the amend changed a single line in `tests/test_dispatch_mirror.py` (1 insertion /
  1 deletion, **net zero lines**) a full day before Phase 159's remap ran — so no citation line number
  computed against that tree shifted. The same stale sha appears in the Phase-159 plan text as the
  "post-154 retarget base" and is left as-executed there for historical fidelity, corrected once in
  `REQUIREMENTS.md` §SWEEP-13.
- **Eight Phase-159 artifacts were executing uncommitted and are now committed** (`4f3a4fa2`). A second
  plan-check revision round at 13:32–13:56 on 2026-08-24 — after `c3b0cf0f` (12:32) and before execution
  began (~14:00) — was never committed, so HEAD carried a *different* plan than the one that ran.
  Proven by content: 159-01/02/03-SUMMARY.md cite the measured 110-stable and 881-supplemental figures
  and the `/usr/local/py-utils` interpreter, none of which appear in the committed plans. The plan of
  record is now the plan that executed.
- **The `firestarter` gitlink was stale at `2ad5b322`** — the Phase-154 firmware commit, predating
  Phases 155–158 entirely. Re-pinned to the v1.33 firmware tip `2ccda8d4` in the same commit.
  `firestarter_app` was already correct at `38f0d83`.

### Post-Close Correction: The Sweep's Oracle Was Blind (2026-08-24)

**Found by the operator, after close, by reading the code** — `include/eprom_budget.h` still carried
`Phase 145 may record the real figure`. It was not an isolated survivor.

**The instrument, not the procedure.** `survey_provenance.py` was the SWEEP-03/SWEEP-06 gate, and it
shipped with **no test file at all**. Its detector anchors the provenance token immediately after the
comment opener:

    (//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)

So a token appearing **mid-sentence** was invisible — `# needed (D-02).` never matched — as was every
requirement family outside that fixed 5-name list. The project has **96 families**, derived from its own
`REQUIREMENTS` records. Python **docstrings** were invisible too: `chip_test.py:537` opens a docstring
with `Ordered, derived test plan for a single chip (SWEEP-01).` and carries no `#` anywhere.

| Measurement | Old gate | Corrected |
|---|---|---|
| Hit lines, shipped source (both repos) | **43** | **1,174** |
| Hit lines, whole corpus | 198 | 4,214 |
| `D-#` in `firestarter/{src,include}` | 4 across 1 file | **87 across 21 files** |

**SWEEP-03's headline evidence was an artifact of where the regex anchored.** Its discharge records
`D-#` going "34 across 9 files → 4 across 1 file". That reproduces exactly under the old detector — 4,
re-measured — but the property the requirement *states*, "requirement/decision IDs are stripped from
shipped source", was never what the 4 measured.

**What was done about it.** The detector was corrected to separate two questions the regex conflated —
is this comment-or-docstring context (per language: a C scanner tracking string/char/block state,
`tokenize` for Python), and does that text carry a token anywhere within it. `--legacy-anchored`
reproduces the historical figure **exactly at 198**, so every number already recorded in `.planning/`
stays reproducible. The oracle got its first **21 tests**, proven RED first.

**Sweep outcome:**

- **Firmware: complete.** 27 files; residue **zero** outside two named exemptions — CAP-01/02/03
  (8 lines, live cross-repo wire vocabulary per SWEEP-02) and the blob-SHA-pinned
  `eprom.cpp`/`eprom_params.h` (65 lines, Ruling B, whose `protocol_branch_inventory.json` sidecar
  carries a **line-bearing** `sites` array extracted from `eprom.cpp`). Gates: **byte-identical cold on
  all three AVR targets**, sizes unmoved, 184/184 native, 184/184 native_nodevtools, 360 pytest.
- **App package: partial.** 285 of 787 lines swept, all strictly within-line so **no app line number
  moved**. 1947 passed / 29 pre-existing errors — byte-equal to the pre-sweep baseline.
  **463 lines remain unswept** and are enumerated by `strip_provenance.py --show-residue`.
- **Not in scope:** `tools/` (288) and both test trees (2,977). `packages = ["firestarter"]`, so
  `tools/` does not ship; test-tree IDs are deliberately retained per SWEEP-03/04.

**Three defects were introduced by this correction and caught by gates, not by review** — recorded
because the catch is the point:

1. A hand edit left a dangling `(157-03,` with an unbalanced paren in `firestarter.h`.
2. `rurp_vpp.h` lost an opening paren while its closing partner survived on the next line. Both were
   found by a block-level comment-hygiene check written for this pass.
3. The stripper's `\s*\(` swallowed a **line's leading indentation** when a parenthetical opened the
   line, turning a `serial_comm.py` docstring line into `. 0-byte param region ...` and taking the
   CAP-03 parity gate from 6-of-6 facts to **0**. A second stripper defect edited three lines inside
   `_read_and_parse_lines`, whose body is SHA-pinned by a gate whose failure text says a change must be
   **flagged and deferred, not re-pinned** — so unlike the firmware C-14 census that is a do-not-touch.

Each has a regression test. The stripper is deliberately fail-closed: it rewrites only three provable
shapes and **declines** everything else, which is why 463 lines are a reviewable list rather than
silent damage.

**Honest status of the requirements:** SWEEP-01 is **procedure correct, coverage incomplete**; SWEEP-03
is **discharged for firmware, open for the app package**. Both are annotated in place in
`milestones/v1.33-REQUIREMENTS.md` rather than silently re-ticked.

### Citation-Shift Audit Of This Close (2026-08-24)

**A milestone close necessarily shifts line numbers in the very records it writes,** and in a milestone
whose subject was citation hygiene that deserved measuring rather than assuming. It was measured.

The close edited five records (`PROJECT.md` +7 lines, `STATE.md` +42, `ROADMAP.md` +2, `MILESTONES.md`
+138, `RETROSPECTIVE.md` +110). Every `.planning/` → `.planning/` `file:LINE` citation into those five was
re-resolved against the pre-close blob at `295c5215`; a citation counts as **displaced** when the line at
its cited number now holds different content than it did before the close.

| Result | Count |
|---|---|
| Citations examined (into the five edited records) | 1,035 |
| Unchanged by the close | 472 |
| **Displaced** | **563** |
| — of those, inside **historical** phase/archive artifacts | **546** (90 citing documents) |
| — of those, inside the **live** records themselves | **17** |

**None of the 563 was repaired, and that is a decision with evidence, not an omission.**

- **The 546 are audit trails, and rewriting them would corrupt the record.** The largest single block is
  **176 in `159-03-SUMMARY.md`** — this milestone's own exception ledger, whose entries read *"…
  `.planning/PROJECT.md:1607` no longer contains any citation to `check_size_baseline.py` … chosen
  endpoint: none (retired)"*. Those line numbers are the **evidence for a retirement decision**, quoted as
  of review time. Advancing them would make the ledger assert something it never found. The same holds for
  the 130-\* and 146-\* close-ledger blocks.
- **The 17 in live records are deliberately-historical too — each is labelled stale by its own
  surrounding prose.** `STATE.md:154` / `PROJECT.md:671` are introduced with *"the design note's own …
  line references are themselves stale"*; `STATE.md:532` / `PROJECT.md:705` with *"used to read"*;
  `STATE.md:634` / `PROJECT.md:823` with *"was ITSELF already stale"*; `ROADMAP.md:363` with *"is
  wrong"*; and `STATE.md:11` with *"deliberately left"*. They form a **documented drift chain** this
  project has recorded across four separate corrections — advancing the numbers would delete the drift
  the chain exists to demonstrate. Two further cases are structurally unrepairable and prove the point:
  `STATE.md:972`'s pre-close target is an **empty line matching 309 lines** in the new file, and
  `ROADMAP.md:2414`'s is `**Plans**: 3 plans`, matching six.
- **Scope check:** this class was **never** in the v1.33 remap's scope. The Phase-154 manifest targets
  source files — 5,646 records under `firestarter_app/` and 5,381 under `firestarter/` — not `.planning/`
  documents. So the close did not undo remap work; it moved lines in a class the remap never covered.

**Carried forward as the actionable finding:** `.planning/` → `.planning/` line citations have no
maintaining mechanism, and every close shifts them. The distinction that must survive is
**historical-by-intent vs live-pointer** — a future sweep of this class that cannot tell them apart would
do more damage than the drift. The Phase-130 archive gate was re-run after all close edits and holds at
**PASS, `superseded: 12`**, unchanged.

### Firmware Size — Before and After

**Read the labels before reading the deltas.** The pre-milestone figures are **WARM**; the
post-milestone figures are **COLD**, because Phase 158 deliberately re-recorded the baseline from cold
builds. They are therefore **not a like-for-like pair**, and the delta column below is arithmetic on two
differently-labelled measurements, shown for orientation rather than claimed as a single measurement.

| Target | Flash WARM (pre) | Flash COLD (post) | Δ | RAM WARM (pre) | RAM COLD (post) | Δ |
|---|---|---|---|---|---|---|
| `uno` | 26026 | 22952 | −3074 | 1575 | 1434 | −141 |
| `uno328pb` | 26074 | 23000 | −3074 | 1581 | 1440 | −141 |
| `leonardo` | 28170 | 25098 | −3072 | 2016 | 1875 | −141 |

That reconciles against the two independently-recorded components — the survey's **−2938 B flash /
−13 B RAM** and Phase 158's separately-measured **−138/−138/−136 B flash / −128 B RAM** — to within
**2 B on `leonardo`**, and exactly on the two ATmega328 targets. The residual 2 B is stated rather than
smoothed away.

**Backlog:** retires **999.34** (provenance comment sweep). Files **999.35** (binary command protocol)
rather than carrying it — 999.35 carries this milestone's own measurement, which **corrects v1.28's
flash estimate from ~1–1.5 KB to −3.7 KB** and confirms its ~512 B RAM figure exactly.

---

## v1.32 AT28C Write-Path Root Cause & Report Provenance (Shipped: 2026-08-21)

**Phases completed:** 6 phases executed (147–149, 151–153; **150 deferred**), 72 plans, 183 tasks
**Timeline:** 2026-08-18 → 2026-08-21 (4 days)
**Requirements:** 35/35 in-scope v1 requirements Complete (42 defined — 7 RELOCK deferred to Backlog 999.28)
**Closeout type:** `override_closeout` — two reasons, both recorded before the close, neither a gap in this milestone's own work: **(a)** Phase 150 (`write --sdp-relock`) was deferred by operator decision on 2026-08-20 and reads `phase_complete: false` / `verification_status: not_required`, so `ALL_PHASES_VERIFIED` is structurally false; **(b)** `audit-open` reported the same **9** pre-existing carry-forward items acknowledged at the v1.31 close. **None of the 4 UAT/verification carry-forwards originate in v1.32.** All six executed phases read `phase_complete: true` / `verification_status: passed`. Known verification overrides: 9 (see STATE.md → *Deferred Items — acknowledged at v1.32 milestone close*). This is the **ninth** consecutive acknowledgement of substantially this set.
**Code:** firmware 39 commits, 86 files, +7561/−387 · host app 85 commits, 86 files, +37999/−3813 (the bulk is the regenerated 746-chip `chip_database.json`) · meta 288 commits
**Issues:** [gh#21](https://github.com/henols/firestarter_prom/issues/21) (with [gh#32](https://github.com/henols/firestarter_prom/issues/32) folded in), [gh#11](https://github.com/henols/firestarter_prom/issues/11), [gh#12](https://github.com/henols/firestarter_prom/issues/12) — all three **answered publicly and all three still OPEN**. A code fix is not a validation.

**Delivered:** A `dev test` report now names the firmware it ran against, so a community report can be
attributed to the code that produced it before any protocol-`0x0D` write-path claim is made about it.
On top of that spine: the chip database states voltages and timing as integers in one unit each
(with the AT28C256 VCC margin-rail correction), the firmware receives page size over the wire instead
of a hardcoded constant, `dev lock-status` reports protection state or refuses with a named class
token, and the `0x0D`/`0x05` write path no longer runs a pre-write blank check while `0x0D` gains a
real standalone software chip erase. Every one of those is a software fact. **No AT28C part was on a
bench at any point** — `0x0D` stays `UNVERIFIED` and the underlying failure is still undiagnosed.

**The milestone-level non-claim, stated once here in this milestone's own canonical wording:**
**no AT28C part was tested**, at any point, by any phase — protocol `0x0D` stays UNVERIFIED in
PROTOCOL-LEDGER exactly as it stood at the open, and every write-path change v1.32 shipped is
**software-proven and unvalidated on silicon**.

**Key accomplishments (curated):**

1. **F-01, the spine: every `dev test` report ever filed carried `fw_board_identity: null`, and now
   does not.** `cli_handlers.py` hardcoded `None` because `EpromOperator.comm` is a transient
   per-operation connection torn down after every operator call. `read_hardware_revision_value` was
   renamed to `read_programmer_identity` and widened to a `ProgrammerIdentity` NamedTuple harvesting
   the firmware/board identity off the connection the revision read *already* opens — proved to keep
   PROV-02's one-connection/one-disconnect contract mechanically, with the first-ever unit coverage of
   that function (13 → 22 tests) and the first-ever tests of `render_diff` (0 → 7). An absent identity
   renders an explicit `"not reported"` marker while the fenced report JSON keeps typed `null`.
   **Stated with it, not buried:** every report filed *before* this fix — gh#21's and gh#32's included
   — remains permanently unattributable.
2. **The database states numbers as numbers, and one wrong number was corrected.** `chip_database.json`
   moved to `vcc_mv`/`vdd_mv`/`vpp_mv`/`pulse_duration_us` integers; `database.py`'s string-coercion
   layer was deleted outright and replaced with one shared `format_mv` render helper, and the second
   live string parser (`audit_coverage_matrix.py`'s `parse_pulse_us`) with direct integer indexing.
   `firestarter info AT28C256`'s `VCC:` line went from `4.0v` to `5.0v` via a **value-keyed**
   substitution that never touches the faithfully-decoded `VCC_VOLTAGES` table — blast radius measured
   at exactly **56 chips, zero decreases**, in a dedicated `diff_db.py` bucket. The 746-chip host→wire
   golden was held byte-identical through the whole migration.
3. **The page-size seam ships with its own no-op consequence stated as loudly as the change.** A
   provenance-keyed emit rule delivers `programming.page_size` for exactly the **18** upstream-native
   `0x0D` rows (15 at 128 B, 3 at 64 B) and the firmware consumes it through a validated bitwise page
   mask, with a cross-repo JSON-key parity gate proving the host key is both declared and dispatched in
   `json_parser.c`. **For the AT28C256 named in the community threads this changes nothing observable**
   — its 64-byte page is exactly the pre-existing floor — so the seam is explicitly *not* offered as an
   explanation of gh#20/#21/#32/#11.
4. **`dev lock-status` is refusal-first, and structurally incapable of guessing.**
   `protection_readability.protection_gate_for_entry` is a pure `(entry, display_name) →
   (class_token, reason)` classifier that **cannot return `protected`/`unprotected`** — only the one
   function permitted to read a device response may — frozen by an AST invariant gate with committed
   planted fixtures, and walked over all 746 committed rows by an 18-leg partition invariant. On the
   28C/SDP family the honest answer is usually the refusal: **665 of 746 rows resolve to a refusal
   class, 81 are `read_permitted`**. Firmware gained the two read sequences and command-16 admission in
   dual-repo lockstep.
5. **Write-path erase policy: three deletions, one new operation, and a fourth recorded reversal.** The
   pre-write blank check is gone from both auto-erasing protocols — `0x0D` (`eeprom_28c.cpp:517-519`,
   deleted outright, not re-gated) and `0x05` (`flash_5v_page.cpp:88-90`, **located in code before
   being touched**, not assumed by symmetry) — each proved by a native case observed failing before the
   deletion and passing after. `0x0D` gained `eeprom28c_erase_execute`, the Atmel AN 0544B **software
   six-byte** chip erase (never the datasheet's 12 V-on-OE path), 0 B RAM by construction, its emitted
   stream pinned against in-tree tables at head, tail and an *exact* divergence index of 51 — never a
   bare `!= -1`. `FLAG_CAN_ERASE` was restored on all **84** algorithm-13 rows by a one-character-class
   change, proved exhaustively over all 746 rows twice, and recorded as the **fourth** reversal in the
   Phase 119 → 120 → 121 → 153 chain in the project's established mechanism-corrected voice. The real
   VPP hazard control is a new brace-matched negative source scan, `check_erase_no_vpp.py`, proved both
   reachable *and* discriminating — while `check_dispatch.py` (GATE-03), which an earlier criterion
   named as this control, stays byte-unchanged and is explicitly **not** cited as the proof it
   structurally cannot be. That criterion was **corrected, not satisfied**.
6. **The first milestone in three to actually publish its release notes — behind a gate seen to
   fail.** Phase 137 and Phase 146 each authored release-note sets that were never posted; v1.32 put
   publishing *inside* the phase. Five public artifacts shipped: comments on gh#12 (discharging the
   2026-08-03 commitment 18 days late), gh#21 and gh#11 (answering a 2024 report in FIX-06 conflation
   terms, citing DS20006386B, crediting both reporters by name), plus both release bodies. All of it
   policed by `152-check-claims.py`, a fail-provable gate seen RED on planted violations before any
   GREEN was believed, over 27 targets with a 34-leg paired suite — including the hardest row in it: a
   variable-width **negative lookahead** that makes `write --sdp-relock` *mandatory* as withdrawn and
   *forbidden* as shipped, after a verb allow-list was rejected for failing OPEN and a proximity window
   for this project's own D-14 precedent.

**Known gaps carried, not hidden:**

- **The evidence ceiling, binding and unchanged from open to close: no AT28C part has ever been in
  operator inventory.** `0x0D` stays `UNVERIFIED` in PROTOCOL-LEDGER, no `support_status` field moved
  (machine-checked, `chip_database.json` byte-unchanged), and **no bench phase existed** in this
  milestone by design.
- **Backlog 999.29** (the AT28C256 write-path failure itself) — **open, partially addressed, explicitly
  NOT retired.** v1.32 removed the blocker to diagnosing it and answered it publicly; it did not
  diagnose it. Operator is the named owner.
- **Backlog 999.28** (`write --sdp-relock`) — **deferred a second time** (v1.30 as Phase 135, v1.32 as
  Phase 150). So for a second release running there is **no supported way to deliberately protect an
  SDP part**, and on `0x0D` the protection bit cannot be read back either. Standing instruction: a
  future promotion **must reverse OUT-05's fifth gate class in the same change that lands the feature**,
  or the gate rejects the very release notes announcing it.
- **`leonardo` MERGE-05 flash headroom is 0 B** — `+724 B` measured against BASE-01, exactly equal to
  the four-term allowance (band 0 + defect-fix 96 + page-size seam 210 + lock-status read 288 + erase
  standalone 130). **Separately, the Caterina USB-bootloader cliff at 28672 B is UNGUARDED** with
  1042 B remaining: `board_upload.maximum_size` does not enforce it, so nothing in the build stops a
  future change from silently overwriting the bootloader region. A split-or-trimmed-build phase was
  raised and deliberately deferred.
- **The protection-class count is stated with its own disagreement, not resolved into one number.**
  Method A (a synthetic counterfactual) gives 664/82, Method B (the live production path) 665/81, and
  Phase 151's own published 406/111/39 **reproduces under neither**. Only 665/81 plus the two
  method-invariant counts (`no_mechanism` 405, `not_implemented` 40) are citable.
- **The 20 ms `t_EC` wait is an Atmel-family maximum applied to a multi-vendor 84-row bucket**, and no
  native test can prove the wall-clock wait is honoured — the trace stubs never stub `delay()` and
  record no time, so the proof is structural, never temporal.
- **A part-name misattribution (W29C020 vs W29C040) is already published** and, under this project's own
  discipline, cannot be edited in the body that carries it — only corrected in a future artifact.
- **A green claim-gate run is not a wording review**, and this milestone's own ledger records how far
  short of D-03's per-artifact blocking operator review the posting checkpoints fell.

<details>
<summary><strong>All 72 plan one-liners</strong> (raw, as extracted from each SUMMARY.md — includes a
few deviation-log and status lines that the extractor picked up in place of a one-liner)</summary>

**Key accomplishments:**

- Moved `firestarter_app` onto `gsd/v1.32-…` forked off `origin/beta` (3.0.0b21), recorded a 1590-passed baseline, and tracked the devtest-triage skill files in the meta repo for the first time via a `.gitignore` un-ignore.
- Renamed `HardwareManager.read_hardware_revision_value` to `read_programmer_identity`, widened it to a `ProgrammerIdentity` NamedTuple carrying both the hardware-revision string and the raw firmware/board identity harvested off the connection the revision read already opens, and wired `cli_handlers.py`'s `dev_test` handler to feed real values into `AutoCapture` instead of a hardcoded `fw_board_identity=None`.
- Bumped `SCHEMA_VERSION` to `"1.4"` with a documented value-population rationale, and made an absent `fw_board_identity`/`hw_revision` render as an explicit `"not reported"` marker in the `rich` console table — while the fenced report JSON keeps typed `null` throughout.
- Built the first-ever unit coverage of `read_programmer_identity()` in `tests/test_hardware.py` (13 → 22 tests) proving PROV-02's one-connection/one-disconnect claim mechanically and D-04's two independent failure paths, plus the D-13(b) handler-level leg proving an absent identity renders the explicit marker while the saved JSON stays typed `null`.
- `render_diff` now labels `host_version`/`fw_board_identity` and folds a not-attributable clause into the identity row when absent, tested for the first time ever (0 -> 7 tests), with a second frozen fixture proving PROV-04's null-identity real-world case and a value-parity assert pinning the app-side and parser-side `NOT_REPORTED` literals equal.
- All three tasks complete.
- Committed a 746-chip byte-identical host->wire golden fixture, a 5-test regression gate proving Phase 148 changes nothing on the wire, and the measured pre-change state of all four gates in the D-12 review artifact.
- Made GATE-02 (`diff_db.py`) schema-agnostic ahead of the numeric-database migration by adding a load-time `_canonicalize_db` normalizer, renaming every field-name-keyed classification read to the canonical `vcc_mv`/`vdd_mv`/`pulse_duration_us` names, and migrating the gate's own test fixtures — while the pinned pre-136.1 baseline and GATE-03 stay byte-unchanged.
- Migrated build_db.py's emitter and interpret_timing to the millivolt/microsecond numeric schema, made the pulse_delay decode-fault path fatal (D-08), migrated the authored extra_chips.json supplement, and regenerated a 746-chip chip_database.json with diff_db.py's bucket distribution byte-identical to the pre-migration reading.
- Deleted database.py's string-coercion layer entirely, replaced it with one shared `format_mv` render helper, moved all three display call sites onto it, and proved the 746-chip wire dict and the pinned CLI snapshot both stayed byte-unchanged through the migration.
- Deleted `tools/audit_coverage_matrix.py`'s `parse_pulse_us` — the second live string parser DATA-03 targeted — moved all eight reads to direct integer indexing, regenerated the tool-produced coverage-matrix golden (297 pulse cells become bare integers), and proved by direct ledger-content comparison that the DEFECT-COV-NN defect signatures are completely unaffected by the schema migration.
- Corrected `firestarter info AT28C256`'s `VCC:` line from `4.0v` to `5.0v` via a value-keyed post-construction substitution in `build_db.py` (never touching the faithfully-decoded `VCC_VOLTAGES` table), and proved the exact 56-chip blast radius in `diff_db.py` with a dedicated `RULE_VCC_MARGIN_RAIL` bucket — discovering along the way that the plan's own predicted RED mechanism was wrong, and documenting the corrected, stronger measurement.
- Re-derived `tests/golden/chip_database_field_inventory.json` by independent traversal + AST walk for the numeric mv/us schema (6 electrical keys, `pulse_duration_us`, 25 generator keys), then proved the gate can still fail on six planted legs (five RED, one new to this milestone against `tools/extra_chips.json` itself) before trusting it green — retiring the last transient of Phase 148's schema migration, full suite now 1633 passed / 0 failed.
- Closed DATA-03 and DATA-04 with assertions rather than assurances (a tree.body-scoped AST gate that catches a new part-keyed dict without firing on the pre-existing local `_AT28C_DIP24_NAMES`, plus two proven-capable-of-failing token scans), completed `148-DB-DIFF.md` into a single reviewable document with the corrected 28-chip (not 29) deferred non-claim, and stated the breaking numeric schema and AT28C VCC correction in README's changelog surface — full suite now 1641 passed, 0 failed, all five DATA-01..05 requirements Complete.
- Forked `firestarter` onto the v1.32 milestone branch off `origin/beta` (verified by content, not ancestry), captured a cold pre-edit flash/RAM/warning baseline for all three AVR targets, and created the phase's `149-PAGE-SIZE.md` review-artifact skeleton with the D-01 provenance evidence pre-loaded.
- Authored the D-19 claim gate over `149-PAGE-SIZE.md`, resolved the measured bare-claim-word / PGSZ-05 collision with a negative-lookbehind narrowing shown satisfiable by both a forward fixture and a negative control, and got the operator's explicit sign-off on the narrowing's exact width before the rest of the phase relies on it.
- Added a provenance-keyed emit rule to `build_db.py` that delivers `programming.page_size` for exactly the 18 upstream-native protocol-`0x0D` rows (15 at 128, 3 at 64), proved it exhaustively with an 11-leg host invariant suite, and preserved Phase 148's wire golden with a committed 18-entry delta list instead of a re-baseline.
- 1. [Rule 1 - Bug] Task 1's `firestarter.h` field comment leaked a Task-3 identifier before it existed
- Added a 10-leg pytest module proving `constants.py`'s `JSON_KEY_PAGE_SIZE` is both declared and dispatched in `firestarter/src/json_parser.c`, with all 3 host JSON keys mapping two-way to the firmware's 11 PROGMEM keys via a completeness-checked 8-key exemption tuple, and two planted fixtures observed RED before being committed in their intentionally-violating state.
- Cold-measured the page-size seam's real flash (+210 B) and RAM (+2 B) cost on all three AVR targets, then funded it with two new named, SHA-attributed MERGE-05 exemptions — leaving leonardo's post-exemption headroom at exactly 0 bytes — after seeing the gate genuinely fail, then pass, then still fail one byte past the new floor.
- `size_baseline.json` re-anchored to plan 06's cold post-change figures with the stale Phase-144 tree SHA corrected, both size gates green, and four measured deferred todos filed.
- Completed `149-PAGE-SIZE.md` and its outward-facing README changelog mirror, extended the phase's claim gate from one target to nine (surfacing and fixing four missing caveats and three vocabulary collisions in earlier SUMMARYs along the way), got operator sign-off on the wording, and flipped PGSZ-01 through PGSZ-05 to Complete — the last plan of Phase 149.
- Corrected five stale `firestarter lock-status` references to the beta-only `dev lock-status` surface, fixed two "one firmware workstream" sentences to say two, and landed 151-DESIGN.md as the phase's single source of truth for wire shape, exit codes, the corrected 40-row `not_implemented` class census, and the C-17 documentation tiebreak rule.
- Hand-curated all 273 alias tokens across DB algorithms 0x05/0x06 into a fail-closed three-state frozenset table with per-row `lockable-proms.md` citations, plus a 6-leg test proving every citation resolves.
- Firmware/host command-16 admission: `is_memory_cmd()` grows to nine cases, the parse gate widens to `is_memory_cmd(handle->cmd) || handle->cmd < CMD_READ_VPP`, both native mirror suites and the host constant ladder move in lockstep, leonardo stays 1424 B clear of the unguarded Caterina cliff.
- Presented the operator with the two sourcing-path
- Minted one new DATA-band catalog id (`0xE1`, two `u8` params) and propagated it through the codegen path across all five tracked files in three repositories, each generated output re-verified idempotent before commit, while leaving the ERROR band's last free id `0xBF` unspent behind a durable pytest guard.
- Authored the pure `(entry, display_name) -> (class_token, reason)` classifier in `protection_readability.py`, structurally incapable of returning `protected`/`unprotected`, plus a 23-leg proof suite covering both measured worked examples and all three raise controls.
- Task 1 — the authoritative section (`firestarter_app/doc/infoic-field-dictionary.md`).
- Landed both protection-status read sequences end-to-end — a shared AMD/JEDEC ID-mode single-byte read, two family-specific operations emitting a two-byte raw-byte-plus-decode DATA frame, their dispatch arms, and the `loop()` arm — with five new native legs per family proving dispatch, pinned bytes, 5V-only safety, raw-byte fidelity, and mode bracketing.
- AST invariant gate freezing `protection_readability.py`'s curated table (two parameterised frozensets, a generalised unconditional Class 1(a), and a deliberately-weaker Class 3), paired with a 13-leg subprocess test and two committed planted fixtures.
- Authored the only function in the codebase permitted to turn a device response into `protected`/`unprotected`, its literal four-code exit map, a strictly-additive `sdp_honesty.py` sibling, `EpromOperator.read_protection_status`, and a six-leg frame-level wire test — all on the existing `conftest.py` harness.
- Landed `test_lock_status_class_partition.py` — an 18-leg invariant walking `protection_gate_for_entry` over all 746 committed database rows, pinning the corrected 405/40/84/217 census as literals and proving `protected`/`unprotected` structurally unreachable via a real planted-fixture failure through the subprocess gate seam.
- Registered `dev lock-status <chip> [--force]` as a beta-only Click subcommand wired to the D-09/D-10 classifier and exit map, proved it with an 18-leg class-token x exit-code CLI matrix, extended the channel gate and the `dev --help` snapshot to the seventh gated name, and flipped LOCK-02/03/04 after re-confirming the full host and firmware-native evidence chain.
- Sideloaded the Phase 151 firmware to the operator's Leonardo, confirmed the flash took via a comms-error discriminator (not the truncated version string), ran the one bench leg with an oracle (leg A, `0xDA45`) and the one probe leg with a seated part (leg B, raw byte `0xFE`), and recorded leg C as not-run because no `W29C040` sample exists on the bench — with an explicit non-claims list closing out every claim this session is prohibited from making.
- Built OUT-05's fail-provable claim gate as a sibling of 149-check-claims.py, armed against a new contract document, and proved it rejects the deferred command's shipped-framing planted violation while permitting its mandated withdrawal sentence.
- Completed the fifteen-fixture set, built the thirty-leg paired suite `test_check_claims_152.py`, and committed the plant-and-revert transcript with every RED pasted verbatim -- proving Plan 152-01's gate fails on a planted violation before any pass is believed.
- Hand-edited dated amendments to ROADMAP criteria 2 (D-05, gh#32 closure) and 5 (D-11, pairing-clause narrowing), corrected the three stale record sites RESEARCH found, and added one labelled correction block to PROJECT.md disproving Phase 121 D-12's erase-capability premise — every edit re-confirmed green against the record-corrections gate.
- Hand-edited REQUIREMENTS.md's OUT-01/02/04/05 bullets to the post-deferral, post-153 text with four dated AMENDED markers, reconciled the Coverage block's 25/34-vs-35 off-by-one to DATA-06's re-homing, and corrected the `database.py` citation drift to the live-measured line 638 — no checkbox flipped, no `gsd-tools` normalizer run.
- Adapted the frozen 137 gh#12 donor into a gate-clean second-release withdrawal naming Backlog 999.28, with the D-14 review diff committed alongside it.
- 1. [Rule 1 - Bug] The mandated caveat sentence was split by an 80-column line wrap
- Authored `152-GH11-COMMENT.md`, a frozen gh#11 reply that discharges the 2026-08-03 "I will soon get it pushed and I will keep you posted" commitment 18 days late, answers the 2024 report in FIX-06 conflation terms citing Microchip DS20006386B, and passes `152-check-claims.py` (rc=0).
- `2026-08-21T15:42:06Z`
- Re-measured both sub-repos' merge pictures with `git cherry` as the sole oracle, found all three repos already tracked-clean, and proved the app suite green under both the devcontainer interpreter and a freshly provisioned CI-parity interpreter with the sibling firmware root severed.
- Opened both PRs against `beta`, measured the app PR's mergeability before touching anything and found it textually clean by two independent oracles (GitHub's own computation and a local `git merge-tree` dry run), so no hand conflict-resolution was needed. The blocking operator checkpoint was presented; the operator delegated the merge-method choice ("you decide"), the orchestrator chose merge-commit from measured precedent, and — after a harness permission denial on the first attempt and a subsequent operator grant — the orchestrator executed both `gh pr merge` calls directly rather than the plan executor, because the delegation path was blocked. Both PRs are now `MERGED`. Post-merge `git cherry origin/beta HEAD` is literal empty output in both repos, independently re-measured by this executor twice (immediately after the merge, and again after each repo's pre-release workflow's own version-bump auto-commit moved `origin/beta` a second time). Both pre-release workflows completed with `conclusion: success`. No version number appears anywhere in this document.
- Extended `152-check-claims.py`'s `_DEFAULT_TARGETS` from one entry to seven real outward artifacts, re-proved the gate RED against the specified plant while so armed, closed a live false-positive in an inherited forbidden-pattern row, and shipped `152-check-not-auto.py` as the fail-closed guard the five posting plans run first.
- Status: complete.
- Status: complete.
- Status: complete.
- Status: complete.
- Status: complete.
- Status: complete.
- Status: complete.
- Settled the erase supply form, SDP-disable prefix, and GATE-03 mechanism correction in writing before any code was touched, and reproduced a byte-identical cold pre-change size/test baseline on all three AVR targets plus native and host suites.
- Deleted the three-line `FLAG_SKIP_BLANK_CHECK`-gated `mem_util_blank_check` call from the tail of `eeprom28c_write_init`, proven by a native case that was observed failing before the deletion and passing after.
- `eeprom28c_erase_execute` gives protocol 0x0D a real, RAM-neutral AT28C software six-byte chip erase, dispatched from a new `case CMD_ERASE:` arm, with the datasheet's 12V hardware erase path deliberately absent.
- Split and inverted the two firmware-test assertions that claimed `CMD_ERASE` on `0x0D` is refused, then added three stream-equality cases (head/tail/divergence, all pinned against in-tree tables) plus a configure-phase no-VPP case, bringing both native environments to 169/17, fully green and in agreement.
- `scripts/check_erase_no_vpp.py` -- a brace-matched, comments-included negative source scan of `eeprom28c_erase_execute`'s body, proven both reachable (fails on a committed planted control-register write) and discriminating (flags `eeprom28c_check_chip_id`'s legitimate A9-12V writes) -- while `tools/check_dispatch.py` stays byte-unchanged, invariant-green, and never cited as the VPP proof it structurally cannot be.
- Located the flash4 (0x05) blank-check conditional in code at `flash_5v_page.cpp:88-90` (correcting a stale pattern-map figure of 87-89), then deleted it, proven by a native case observed failing before the deletion and passing after, with the sibling erase-on-write block and four other-protocol blank checks provably untouched.
- One-line, one-character-class change (`algo not in (5, 13)` -> `(5,)`) that flips the wire capability flag on all 84 algorithm-13 rows, plus a full rewrite of the Phase 121 D-12 comment block recording this as the fourth reversal in the 119/120/121/153 chain.
- Committed `wire_dict_expected_deltas_153.json` (84 flags-only, non-vacuous entries generated programmatically) and extended `test_wire_dict_equivalence.py` to compose it with the existing Phase 149 layer over the untouched Phase 148 golden, adding an exhaustive 746-row scope proof and a reachability proof.
- Inverted the two committed host assertions that pinned FLAG_CAN_ERASE clear (conversion layer + SDP wire-shape layer), and added the positive capability-flag proof the eeprom28c tier-2 wire suite was missing — leaving both anti-bleed negative controls provably untouched.
- Corrected the two `chip_test.py` reason texts that falsely claimed the 28C family has no erase operation, kept the now-unreachable `_PROTOCOL_EEPROM_28C` arm as a tested defensive fallthrough, and re-measured all four downstream `dev test` legs (sweep, two count/banner legs, SDP-leg baseline gate, blank-check placement) to the live post-restoration plan shape -- taking the host suite from 5 failing to fully green (1811 passed).
- Corrected the one user-visible string this phase falsifies (`write --skip-erase`'s "no erase operation at all" claim), extended both `write` and `erase` docstrings with the new flag semantics from D-153-04/D-153-05, and added a test that fails loudly if a symmetric-but-rejected blank-check-vacuity warning is ever added.
- Exhaustive 84-of-746 database scope proof, both-directions info/wire agreement for ERASE-06 with zero source edits, and three-layer ERASE-05 non-regression coverage for `blank` — closing the scope gap the inversions in plans 08-11 left open.
- Rewrote `PROTOCOLS.md` §1.6's (0x0D) erase-model paragraph to describe the shipped `CMD_ERASE` standalone software chip erase and remove the "`-b` is required" recommendation, added a parallel sentence to §1.1 (0x05), and corrected `protocol-id.md`'s 0x0D row — the two documents that were the last false claim sites for ERASE-01/02/03.
- Measured this phase's firmware footprint cold on all three AVR targets (+130 B flash, +0 B RAM), funded it with a fourth named, SHA-attributed MERGE-05 exemption (`MERGE05_ERASE_STANDALONE_EXEMPTION_BYTES = 130`), and re-recorded `size_baseline.json` so both gate modes are green.
- 1. [Rule 1 - Bug] Fixed 4 additional red legs not named in plan 14's hand-off
- Corrected the two stale "one/two firmware-touching workstream" claims in PROJECT.md and ROADMAP.md to three (149, 151, 153), wrote `153-RECORD.md` as the phase's own honesty record carrying the verbatim "software-proven and unvalidated on silicon" phrase and an equally-weighted what-was-NOT-proven section, ran the full phase gate from a committed tree across both sub-repositories, and flipped ERASE-09 — closing all nine ERASE requirements.

</details>

---

## v1.31 27C Programming-Algorithm Fidelity (Shipped: 2026-08-18)

**Phases completed:** 9 phases (138–146), 74 plans, 164 tasks
**Timeline:** 2026-08-05 → 2026-08-18 (13 days)
**Requirements:** 45/45 v1 requirements Complete
**Closeout type:** `override_closeout` — 9 acknowledged carry-forward items, **none originating in v1.31** (see STATE.md § Deferred Items). All nine phases verified.
**Code:** firmware 68 commits, 58 files, +15745/−265 · host app 18 commits, 19 files, +4456/−41 · meta 332 commits
**Issue:** [gh#15](https://github.com/henols/firestarter_prom/issues/15) — implemented **as corrected**, not as filed.

**Delivered:** The three 27C EPROM protocols (`0x07`/`0x08`/`0x0B`) now program with one shared
per-byte pulse-to-verify loop driven by a `const` PROGMEM table keyed on `protocol_id`, with the
pulse width read from the chip database per byte rather than baked in as a protocol constant. A byte
that exhausts its per-protocol backstop fails by reporting its own address and pulse count instead of
failing the block opaquely. Bench-proved byte-exact on one part, one controller, one shield revision.

**Key accomplishments (curated):**

1. **gh#15 implemented as corrected, and the corrections published before any code landed.** Three of
   the issue's numbers were wrong and one premise inverted: `0x0B`'s pulse is 500 µs not `50000 us`
   (the ×100 fingerprint Phase 57 already removed); pulse width is a *database datum*, not a
   per-protocol constant (re-derived live from `chip_database.json` — 170/127/32 chips); and the
   safe 32-bit delay helper is needed for the overprogram pulse, not any bare pulse. Posted as
   comment `#5233463320` on operator approval, byte-verified against the reviewed text.
2. **One shared loop plus a parameter table, not gh#15's three state machines** (D-01). Protocol owns
   *shape* (`max_pulses`, `overprogram_factor`, `overprogram_cap_us`, `verify_mode`, `vpp_path`); the
   database owns the *pulse*. No new database field and no second firmware algorithm selector —
   `protocol_id` stays the single dispatch key, enforced by TABLE-05.
3. **Bench-validated on real silicon:** three full 65536-byte write→read→verify cycles on a Winbond
   W27C512 (`0xda08`) on Leonardo / shield Rev 2.0, three *distinct* images, nine clean oracle cells,
   read stability N=3 at one SHA each, write timing consistent to 0.37 s across all three. `0x08` and
   `0x0B` recorded **skipped-with-reason** with the missing parts named — never inferred from `0x07`.
4. **A firmware defect this milestone introduced was found and fixed on the bench, not papered over.**
   Phase 141 had deleted the only `CTRL_VPE_ENABLE` assert; the first bench cycle failed on byte 0
   (`failed to program within 25 pulses`). Root-caused by a debug session, fixed, then 3/3 byte-exact.
   The failure stands in the record with its cause and is *not* one of the three counted cycles.
5. **`write --pulse-us N` ships**, bounded 1..65535 and pre-validated before a serial byte is sent,
   riding the existing wire field with no new protocol surface — plus a host-side long-write timeout
   fix and intra-block write progress, honestly scoped to the `leonardo` class only (on
   `SERIAL_ON_IO` boards the emission is compiled out *structurally*, because a buffered progress
   frame there could displace a later error frame and turn a program failure into a transport timeout).
6. **An honesty ledger led by the evidence ceiling.** The ~6.25 V program-VCC rail is unreachable on
   every shield revision this project owns, so this milestone claims **fidelity, not improvement** and
   makes no datasheet-conformance claim in either direction. A fail-provable claim gate (proven RED on
   planted violations before its GREEN was trusted) polices the closing documents, gh#15's nine
   original acceptance boxes are graded item by item, and all twelve carry-forwards are named with the
   literal phrase `no v1.31 owner` rather than dropped.

**Known gaps carried, not hidden:** the ~6.25 V ceiling (accepted debt); MERGE-05's +96 B leonardo
band breach, open and un-adjudicated, with the operator as its named owner; `0x08` (AM27C020) and
`0x0B` (M2716/M2732) unvalidated on hardware for want of parts; program-window VPP/VCC under load,
blocked by the standing Phase-97 DTR-reset-on-close tooling gap. Backlog **999.30** (progress bar
never reaches 100%, cosmetic) and **999.31** (no firmware `--pulse-us` ceiling for `0x07`/`0x08`)
were filed by this milestone's own bench work.

<details>
<summary><strong>All 74 plan one-liners</strong> (raw, as extracted from each SUMMARY.md — includes a
few deviation-log lines that the extractor picked up in place of a one-liner)</summary>

- Self-checking Python script re-derives the live 0x07/0x08/0x0B pulse-width distribution from chip_database.json via the production parser (170/127/32 chips, matching the seed's C2 table exactly), observed to fail on a planted input before its three verbatim runs were committed as C2's evidence for gh#15.
- firestarter_app switched to the v1.31 base (4d18b64) and measured under py3.11.15 CI parity at 1539 passed / 0 skipped — a genuine, unreconciled divergence from 138-RESEARCH.md's 1493 passed / 46 skipped figure for that identical commit, recorded with both values and a named-but-unconfirmed mechanism.
- Three empirically-captured 27C write-loop traces (198/221/201 merged entries) frozen as literal arrays with provenance banners, pinned by a parallel two-mechanism identity gate that was proven to fail on three independent break classes before being trusted.
- Cold flash/RAM for three AVR targets and case/suite/warning counts for four native envs, frozen into an immutable `size_baseline_v131.json` beside BASE-01 and verified green through the existing `check_size_baseline.py`/`check_build_warnings.py` `--baseline` seam; two D-07-class gate findings (base-dependent verdict, unknown-env KeyError) recorded with owners and left unfixed.
- Ten-section `138-BASELINE.md` narrative assembling the whole v1.31 pre-change baseline (branch bases, frozen golden trace, per-target flash/RAM, four native env counts, host suite count, pulse distribution) with operator-gated CI evidence re-verified read-only across two repos and three runs, an 11-entry findings register, and PREP-03/PREP-04 ticked with citations.
- Captured gh#15's nine acceptance-criteria boxes verbatim and built a 15-row, content-verified citation register at three pinned commit SHAs — correcting a mis-cited erase-pulse anchor and confirming the program-pulse file untouched by three-ref blob equality.
- Authored `139-check-claims.py` -- a Phase-139-scoped forbidden-claim/required-caveat scanner carrying v1.31 vocabulary and the ~6.25 V program-VCC ceiling as its required caveat, with no proximity window and no arming branch -- and proved it can fail (a planted four-label RED) before its first pass was trusted, then proved both of its fail-closed paths RED as well.
- Drafted `139-GH15-COMMENT.md` -- the byte-for-byte gh#15 correction comment carrying C1/C2/C3, the ~6.25V ceiling as its own paragraph, and a nine-row acceptance-criteria amendment quoting every original box verbatim -- and it passed the phase's own claim gate clean on the first attempt.
- Authored `139-GH15-BODY-AMENDMENT.md` -- the frozen, default-skipped, ready-to-apply gh#15 body replacement -- built programmatically from the live-fetched issue body; fixed a table-shape defect the mechanical cross-check surfaced in plan 139-03's comment; then froze both outward artifacts with blob SHA, byte length, and committing commit each.
- Operator approved the frozen gh#15 correction verbatim ("approved, post now") and it is now public: comment #5233463320, byte-verified against the reviewed text, gh#15 still OPEN and unlabelled at exactly one comment; the optional body amendment was declined (default) and the body remains unedited.
- PROGMEM `eprom_params_t` table (0x07/0x08/0x0B, six columns, no pulse-width) with a fail-closed linear-scan accessor, plus pre-measurement predictions committed before any cold flash/warning capture -- both landed with zero AVR flash/RAM delta and zero added native warnings.
- 24-site two-tier branch-predicate inventory pinning `eprom.cpp`'s exactly-3 protocol-keyed algorithm sites, enforced by a 7-test independent bracket-matched re-parser gate, proven RED on 3 planted violations before its GREEN was believed.
- A committed pytest gate in `firestarter_app/tests/` that freezes `chip_database.json`'s field inventory by per-key occurrence count (not names) and scans `tools/build_db.py`'s generator AST unioned with a `tools/extra_chips.json` key scan -- seen RED on four independently planted violations before being believed GREEN.
- Fifth PlatformIO native env (`native_params_v131`) plus a 9-case Unity suite that exercises `configure_eprom`'s `pulse_delay == 0` fallback and `eprom_params_for()`'s row resolution by running code — the only possible oracle for TABLE-03, since 0 of 329 shipped 27C chips ever hit that branch on the bench.
- Machine-readable D-14 citation sidecar for all 18 `eprom_params_t` cells (one datasheet or reasoned-basis attribution each), gate-enforced by a 10-test pytest module that proved itself on five distinct planted violations before its GREEN was trusted.
- Removed the false "1 ms pulse × N + 3× overpulse" / "Same Intelligent Programming algorithm" claims and their nonexistent-section citations from `doc/PROTOCOLS.md` §§1.3/1.4/1.5 and the stale "1ms pulse, DQ7 verify" / "12–18V direct" claims from `CLAUDE.md`'s Algorithm Handlers table, replacing all of it with the datasheet-grounded facts 140-05's citation sidecar already ships, plus the D-11 native-env exception CLAUDE.md's own reuse-pattern section was missing.
- Cold post-prediction measurement of all 3 AVR + 4 native envs plus both repos' full suites reconciled every one of 140-PREDICTIONS.md's testable claims exactly (0-byte AVR flash/RAM delta, 1166 native warnings, 141/17 pinned suites, 5/1 and 9/1 on the two non-CI envs); the Phase 140 close record names both divergences (the 0x07 Intel-family split candidate and the 0x08 PROJECT.md self-contradiction) without smoothing either, and TABLE-01 through TABLE-05 are now marked Complete exactly once.
- Three new ERROR-band message IDs (0xAE/0xBD/0xBE) authored in the canonical meta catalog and regenerated into both sub-repos, plus a falsifiable flash/RAM/D-13-inventory prediction for plan 141-04's loop rewrite -- committed before any `eprom.cpp` byte moves.
- 1. [Rule 3 - Blocking] Task 2's own verify script tripped on its comment's use of the literal function name it slices on
- New `[env:native_loop_v131]` plus `test_loop_eprom_v131/` (host_stubs.cpp + test_loop_eprom_v131.cpp): a 16-bit-latched-address read-back model, a strong logged-id capture, and a fixed drive-helper contract for plans 141-04/141-07/141-08 -- six loop-independent harness cases green, both pinned native envs still exactly 141/17, zero AVR flash delta.
- Replaced `eprom_write_execute`'s block-level mismatch-mask retry loop with a per-byte fixed-width pulse-to-verify loop driven by Phase 140's `eprom_params_for()` table, added D-03's pre-flight refusal to `configure_eprom`, and rerouted the erase pulse through `mem_util_delay_us`.
- Re-derived the protocol-branch-inventory golden from its own scanner (24->27 sites, tier-1 held at exactly 3), re-pinned the test module's hard-coded tier-1 line literal with a two-directional D-15 armed-gate proof, and reconciled CLAUDE.md's Algorithm Handlers rows with the shipped per-byte loop -- including a corrected arithmetic claim.
- New firestarter/tests/test_write_path_source_contract_v131.py: 12 pytest legs mechanically proving LOOP-02's four named constructs removed and LOOP-07's global delayMicroseconds() ceiling claim, with nine planted-RED transcripts confirming each leg fails for its own reason.
- 14 new native Unity cases (20 total in `native_loop_v131`) proving the per-byte loop's fixed-width cadence, its two skip rules, and the 0x0B energy cap at all three shipped widths -- driven against the real `eprom_write_execute`, with a documented finding that register-shift writes share `STROBE_KIND_DATA`'s exact shape with a genuine chip-data pulse and must be filtered by value, not counted raw.
- 19 new native Unity cases (39 total in `native_loop_v131`) completing the phase's behavioural proof: the overprogram arithmetic as a pure function, the hard-fail exit with a non-vacuous, correctly-scoped route disable, the delay ceiling under a real over-ceiling drive plus the pre-flight refusal, and the DIP32 A16-crossing seam -- with both load-bearing safety assertions seen RED on a planted violation before being restored.
- Captured the post-change v131 trace as a committed artifact, measured flash/RAM cold against the pre-committed prediction and recorded MERGE-05's RED verdict verbatim (operator decision: accepted, not remediated), wrote the phase's non-claims and hand-offs into 141-LOOP-RECORD.md, and flipped all eight LOOP-01..08 requirements in one 16-line hand edit.
- `mem_util_calculate_top_address_register` now preserves `CTRL_VPP_VPE_DROP_ENABLE` for 32-pin EPROM parts on Rev 2-class hardware (an explicit four-case switch inside `#ifdef HARDWARE_REVISION`), proven by a RED-before-GREEN nine-row truth table and two planted-violation transcripts, with the `0x08` write path empirically unmoved at this commit.
- Authors the VPP-04 over-voltage refusal gate (by message id, route-clear with paired non-vacuity, FLAG_FORCE downgrade, in-range control) as a regression oracle against the CURRENT, unrewritten `eprom_check_vpp`, and pins the pre-rewrite `CMD_ERASE`/`CMD_CHECK_CHIP_ID` control-value streams as measured literals for VPP-03 -- five named planted violations, each independently seen RED for its own reason and byte-exact restored.
- One exposed resolver (`eprom_hv_route_mask`) now drives EPROM HV route selection from the `eprom_params` table's `vpp_path` column at both call sites, two conditional single-exit wrappers close the write path's pre-existing `MSG_ERR_VERIFY` disable leak, the Rev-2-class drop bit now survives a 32-pin block observably, and the D-18 protocol-branch-inventory golden was re-derived and landed in the same single commit as the source change (26 sites, tier-1 3->1) -- all five files, one commit, verified by direct binary invocation past a known `pio test` CLI wrapper artifact and two child-process planted-violation transcripts.
- 15 new native cases proving what Phase 142 actually changed (the resolver truth table incl. its fail-closed NULL-row arm, three route-strobe proofs incl. the Rev 1 negative, and the eprom_check_vpp/write-path route equality on the 0x08 row) and what it did not (every write-path error exit still disables), with three named planted violations -- one reproducing the exact pre-142-04 measure/apply divergence, two proving the write-path wrapper is both load-bearing and correctly conditional -- all landed in one commit, src/ and include/ byte-identical throughout.
- New firestarter/tests/test_hv_routing_source_contract_v142.py (16 legs, two import-time env seams): D-09's owed command_done() source contract pinning all three zeroing registers and both dispatch call arms individually inside a brace-matched body, plus VPP-03's structural half (one resolver, one definition of each composite across include/, zero surviving hand-rolled equivalents) -- nine planted-RED transcripts, each failing on its own named assertion, all reverted with zero production-file diff.
- Reconciled firestarter/CLAUDE.md's three Algorithm Handlers rows with the shipped route resolution as a docs-only commit, measured cold flash/RAM on all three AVR targets (leonardo at 2130 B headroom), recorded both MERGE-05 baseline-anchor verdicts and native_trace_v131's expected RED verbatim without fixing either, wrote the 521-line 142-VPP-RECORD.md phase-close record, and hand-flipped VPP-01 through VPP-04 to Complete in both coverage tables with a snapshot-verified 8-line/4-line diff.
- New `eprom_budget.h`/`eprom_budget.cpp` implement the corrected per-block worst-case write-time budget (ceil pulse count, UNCAPPED zero-cap guard, overprogram term delegated to the shipped function, divide-before-multiply seconds conversion, x2+2 padding), proven by six native Unity cases each seen RED under a named production-code plant.
- `SerialCommunicator._decode_id_frame` now decodes a third length-discriminated `MSG_OK_READY` field — the firmware's advertised per-block write-time budget in seconds — at the computed `ver_end` offset with a derived `[1, 14400]` plausibility clamp, proven by five byte-layout cases each seen RED under a named production-code plant.
- The operation-setup ack now packs CAP-01, a PORTED CAP-02 identity tail and CAP-03's per-block write-time budget into one `LOG_OK_ID_BYTES(MSG_OK_READY, ...)` emit -- closing BF-1 (a v1.31 firmware build could not previously connect to the v1.31 app at all) -- and the layout is pinned by a new 10-leg, stdlib-only source-contract gate, every leg proven RED on a scratch-file plant and GREEN against the real source.
- `write_eprom`'s MAIN-phase wait now uses the firmware-advertised per-block budget verbatim (falling back to a derived 120 s when absent or implausible), every other operation still waits exactly 10 s, and `write_eprom` accepts a `pulse_us` override that rides the existing `pulse-delay` wire key -- all proven by a call-argument oracle that never waits out a real timeout.
- A time-gated `MSG_DATA_PROGRESS` (0xE0) emission now fires from inside `eprom.cpp`'s per-byte write loop on leonardo and native, compiled out entirely on uno/uno328pb (BF-2's deferred-log-buffer hazard), landed in one commit with a parse-re-derived `protocol_branch_inventory.json` golden, plus two native cases proving the cadence both fires and doesn't vacuously.
- A mid-block `MSG_DATA_PROGRESS` frame on the write path is now rendered instead of raised on, is never acked, positions the bar as `absolute - start_addr` without ever re-entering `set_progress`'s rebuild arm, and a latch stops the chunk-handoff `update()` once the firmware starts driving the bar -- while a board that never delivers a mid-block frame keeps today's handoff-based bar unchanged.
- `firestarter write --pulse-us N` (`click.IntRange(1, 65535)`, `default=None`) overrides the database program pulse through the existing `pulse-delay` wire field, refuses out-of-range/non-integer values at Click parse time with exit 2 and no port ever opened, always prints a default-visible provenance line naming both values, and is exposed on `write` alone -- with a bare `write` (no flag) still working, per the plan's one measured trap.
- A new 10-leg, stdlib-only source-contract gate pins plan 143-05's intra-block `MSG_DATA_PROGRESS` emission (and its `millis()` state variable) as compiled OUT on `uno`/`uno328pb` and compiled in on `leonardo`/native, with every leg proven RED on a planted violation and GREEN against the real source -- no behavioural oracle exists for this `#ifdef`-scoped guard, so this module is explicitly labelled a source contract, never behavioural evidence.
- A 0xBD/0xBE per-byte program-budget failure now raises `EpromOperationError` naming the failing address plus a hint stating the write aborted and the firmware will not accept another block for it (no continuation implied), and a 0xAE pre-flight `--pulse-us` refusal raises with a hint naming the flag and the exact refused width -- both composed on the existing `_boot_block_hint_message` seam, with zero new exception types or message ids.
- `checkpoint:human-verify`, `gate="blocking"`, `autonomous: false`. Presented in full per the plan's `<what-built>` / `<how-to-verify>` blocks, exactly as authored (reproduced below verbatim in substance, per T-143-AUTOAPPROVE's mitigation and this plan's own instruction that the presentation must be written into the SUMMARY in full).
- Machine-checked TEST-01...TEST-05 -> RUN_TEST case map in `firestarter/tests/test_requirement_case_mapping_v131.py`, proven under D-18 with two planted violations (renamed case, emptied scan root), correcting C-04's phantom "two fallback cases" to the real six-case TEST-05 shape.
- Cross-repo pytest gate proving the firmware's MSG_OK_READY pack order against the host's computed-`ver_end` decode, plus two committed planted-violation fixtures proving it fails for the right reasons (BF-1's defect class).
- Froze Phase 138's pre-change golden trace as a byte-identical historical artifact by pure rename, captured a fresh empirical post-v1.31 trace (91/115/59 entries, not 141-NEW-TRACE.md's stale 91/119/59), and re-armed the six-assertion identity gate in ONE commit -- `native_trace_v131` goes from 3-failed/2-succeeded to 5/5.
- A six-segment state machine partitions all 885 v1.31 trace entries (620 pre-change + 265 new) by set equality and disjointness, proving TEST-06's attribution is complete -- not merely counted -- with both D-18 plants seen RED for genuinely distinct reasons.
- One cold consolidated run measured the FINAL v1.31 tree (+870/+870/+890 B flash, RAM unmoved), then re-anchored all three size baselines to that tip and re-derived the seven fixtures the re-anchor moved the ground under — retiring MERGE-05's standing RED as an explicit anchor move, not a band victory.
- Constants parity measured in both directions on the CI-parity interpreter (14 passed present / 6 passed + 8 skipped absent, both verbatim), all four `ci.yml`-scoped commands green, and the host suite holding at 1590 passed / 82.92% coverage -- exactly Phase 143's 1578/82.92% plus 144-02's 12 new tests, coverage unmoved.
- 144-TEST-RECORD.md authored and operator-approved; TEST-01 through TEST-08 flipped to Complete in both REQUIREMENTS.md and ROADMAP.md via hand-edit with a verified snapshot-and-diff.
- Address-attributable write images, a self-proven tqdm frame extractor, and the Phase-99-shaped bench record skeleton — all built and digest-verified before any hardware is touched.
- BENCH-03 re-measured validated on four independent legs at the tip; both BENCH-02 disposition records written citing Phase 99's and Phase 79's exact numbers — Gate 0 closed with zero hardware touched.
- Reflashed the Leonardo from a clean v1.31 tree (commit `a594173d`, 26906/2014 bytes matching baseline exactly) and confirmed the seated Winbond W27C512 by chip-id `0xda08`, clearing Gate 1's identity half while leaving VPP and the D-03 erase pre-flight explicitly outstanding for 145-04.
- Confirmed VPP in band at 12.0 V with no pot adjustment needed, recorded the operator's verbatim "you are authorized" as informed consent for the erase specifically (not an expendability claim), then settled D-03 on silicon — `erase W27C512 -b` and a standalone `blank W27C512` both exited 0 — closing Gate 1 with the part blank and ready for cycle 1.
- No reflash was performed or needed in this plan.
- The required 4688 µs run: AUTHORIZED (2026-08-17), by SELECTION — no verbatim quote exists.
- "It looked ok". **Artifact:** the bar terminated at **99.02 %** on that run and short of 100 % on all five other writes this phase. Neither side is suppressed and they are not massaged into agreement. A bar stopping one frame short is not something a casual observer would flag — which is the argument **for** requiring both halves, not against the operator.
- The flip was authorized by the operator.
- `146-CITATIONS.md` §§0-2
- A phase-local, fail-closed five-topic documentation checker over the four CLOSE-03 doc targets, seen to fail for a named reason before any doc is edited: `program-vcc-ceiling` is absent from all four, 7 topics unsatisfied in total, and four content locators recorded RED with their commands.
- The ARM `py32f071` target compiles against v1.31 code — arm **GREEN**, exactly one
- Full suite
- Landed the five still-owed D-04/D-05 correction blocks (four in PROJECT.md, one in REQUIREMENTS.md) and wrote `146-CORRECTIONS.md`, a ten-row register that also names three places the inherited correction framing itself was wrong.
- Task 1 — `doc/PROTOCOLS.md` §§1.3-1.5.
- Completed CLOSE-03's host half in firestarter_app/README.md (full write-option surface, two adjacency corrections, DB-pulse and 6.25 V ceiling text), corrected DBG_PULSE_DELAY_MISMATCH's stale wording through the catalog with a pre-commit-verified regen shape, and flipped 146-check-close03-docs.py from RED to GREEN across all four sub-repo targets.
- Wrote `146-LEDGER.md`, the milestone's honesty ledger — a nine-row four-column claim table pairing every permitted v1.31 claim with its explicit non-claim, leading with the 6.25 V program-VCC ceiling and the MERGE-05 +96 B adjudication quoted verbatim, and closing with all twelve Phase 145 carry-forwards, a three-way count disagreement stated rather than reconciled, and four first-class process failures.
- Task 1 — firmware body.
- Planted the probed `confirmed-working` label into the real, committed `146-LEDGER.md` through the claim gate's own default target list, observed leg 9 flip RED under that perturbation, reverted to byte-identical content, then brought all five standing gates green in one recorded pass with both sub-repo suites at/above baseline.
- Both blocking operator gates were answered — wording APPROVED (delegated), posting DEFERRED to after the milestone push — and zero comments were posted to gh#15, which is within this plan's own stated "at most one" output range.
- CLOSE-01 through CLOSE-05 ticked Complete in both `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`, behind the operator's scoped "take it through the gate" authorization, against five freshly re-run green gates and an independently re-derived CLOSE-04/CLOSE-05 settlement — nothing pushed, merged, tagged, or posted to gh#15.

</details>
---

## v1.30 SDP Surface Retirement & Behavioral Lock Proof (Shipped: 2026-08-05)

**Phases completed:** 7 phases, 48 plans, 125 tasks

**Key accomplishments:**

- Fail-closed mypy watermark gate (returncode-before-regex, 120-file coverage floor, `sys.executable -m mypy`) plus an honest `python_version = "3.10"` in `firestarter_app` — no watermark set, no mypy errors fixed.
- `tests/test_check_mypy_watermark.py` (8 tests: 6 legs + 2 controls) gives `check_mypy_watermark.py` its first-ever paired pytest, and the D-03 revert-and-reobserve proved the truncated-run leg was genuinely RED (`DID NOT RAISE SystemExit`) before the fix was restored byte-identically — no mypy errors fixed, no watermark set.
- Closed P-10's hole with a committed 43-entry ALLOW snapshot compared element-wise against `sdp_capability_for_entry`, plus a synthetic non-vacuity proof that a moved chip is caught by name.
- A body-only AST derivation proves every module-level helper `dev_test` actually calls is listed in `_HANDLER_FUNCTION_NAMES`, converting the allow-list's additive fail-open into an additive fail-closed, without touching the checker or the handler.
- Operator-dispatched `ci.yml` run on `beta` @ `16a313a` (run `30822281624`) measured 69 mypy errors — exactly matching research — recorded verbatim in `131-CI-BASELINE.md` as an input to Phase 132's watermark, with the plan's unreachable `(checked K source files)` acceptance criterion amended and filed as correction F-07 rather than satisfied by fabrication.
- `firestarter_app/tools/ci_parity.sh` runs four labelled legs (pytest with an empty firmware sibling, pytest with the sibling present, CI-scoped ruff, and the hardened mypy watermark gate), never aborts early, prints per-leg exit codes plus a BOARD-ATTACHED stamp, and one recorded no-board run shows legs 1-3 green and leg 4 exiting 2 -- the Phase 131 hardened gate correctly refusing to trust a numpy-stub-truncated mypy run.
- `131-RECORD.md` carries F-01..F-07, D-04's four-reason canary rejection, D-10/D-17/D-18 as record-only discharges, and a ten-row GATE cross-reference table; GATE-07 is ticked in REQUIREMENTS.md only after independently re-reading its CI-run evidence; no gap found in the other nine ticks; the block-scoped prohibition scan across all seven plans returns empty.
- Built a committed, numpy-free CI-replica venv script and took the pre-change readings: 69 mypy errors (watermark 35, checked 121 source files) and a reproducible four-leg ci_parity.sh baseline, before any `dev sdp` deletion or mypy fix landed.
- Authored `firestarter/sdp_honesty.py` (three functions, no click dependency), rewired the still-live `dev_sdp` subcommand to compose both its summary line and its outdated-firmware error through it, joined the mypy strict island with zero regression (69 errors unchanged), and captured the unmodified 26-test equivalence proof while it was still takeable.
- Same-commit `git mv` + gate target-list edit (proven RED-then-GREEN), the four honesty assertions retargeted onto `firestarter/sdp_honesty.py` with a new AST import-purity test (proven non-vacuous on a planted `click` import), and a five-section, 18-row prune ledger accounting for the 550-line reduction.
- Deleted the ~112-line `dev_sdp` span (registration decorator through EOF) and its four gates from `cli_handlers.py`, removed the one orphaned `sdp_honesty` import, and node-scoped the `test_help_dev` snapshot down by exactly one line -- the `dev` group's roster is now eight commands, proven by positive enumeration, and the retired command fails with Click's no-such-command error.
- One typed, keyword-only, six-parameter `make_app_context` factory (plus a thin `app_context` fixture) landed in `tests/conftest.py`, discharging all 25 of the four surviving `
- Six bare-collection mypy annotations landed across `config.py` and `database.py` (three each, all derived from actual usage rather than mypy's placeholder hint), bringing the measured mypy count from 38 to 32 -- 3 below the existing watermark of 35 -- without touching the watermark or the ring-fenced `eprom_operations.py` module.
- Placed a comment-only tripwire at the host's write auto-unlock DECISION site in `cli_handlers.py` (not the ring-fenced audit site the record's stale coordinate pointed at), a pointer note at the flag's definition in `constants.py`, and one named test in `test_write_skip_sdp_unlock.py` that has been seen to fail on a planted inversion of the condition it pins -- mypy holds at 32, unchanged from plan 132-06.
- Added an unconditional dereference test proving both SDP command-name entries still resolve at operation setup, corrected all five stale `eprom_operations.py:301`/`:377` citations across two files to name the two dereferencing functions with their true line numbers alongside, and corrected RETIRE-08's own requirement text from a wrong count of three to the measured five — honouring D-12's impossible "same commit" binding as adjacent, cross-citing commits between the submodule and the meta-repo instead of silently working around it.
- `firestarter_app`'s primary `ci` job — red for two months, invisible outside PRs and manual dispatch — is certified GREEN: run `30856059940` on `gsd/v1.30-sdp-surface-retirement` @ `42a1971`, conclusion `success`, mypy at 32 against the unratcheted watermark of 35, all eight RETIRE requirements now Complete.
- Post-edit nine-row precedence matrix
- Two new op strings (`sdp-lock`/`sdp-unlock`), the `_SDP_OPS` allow-list, a `_dispatch_sdp` guard/branch/terminal-raise arm cloned structurally from `_dispatch_multi_run`, wired LAST in `_dispatch_step` and mutation-proved (not merely asserted) to add zero branching cost to the seven shipped ops -- plus the `_DESTRUCTIVE_OPS` asymmetry (`OP_SDP_LOCK` in, `OP_SDP_UNLOCK` deliberately out) that is LEG-09 itself.
- A generic cleanup registry drained in a bare `try/finally` around `run_plan`'s step loop -- registering a successful lock's unlock, reaching `KeyboardInterrupt`/`SystemExit` while still letting them propagate by identity, wrapping each cleanup callable in its own narrow except (never masking the in-flight exception), and mechanically proven -- at the AST level, not by comment -- to never touch the `results` list the caller holds.
- Fourth AST deny bucket in `tools/check_devtest_orchestrator.py` catches `except Exception:`/`except BaseException:`/bare `except:`/tuple forms -- gated GREEN on real, clean source via one `(file, function)`-scoped exemption (D-14) with two independently mutation-proven guards (empty-reason, stale-row).
- A fail-closed op-registration parity gate (`tests/test_op_registration_parity.py`, the phase's second and final new source file): 6 measured policed registries checked op-by-op via an argument-taking `_assert_op_parity`, 6 measured declared non-registries whose zero-op-vocabulary claim is re-derived via AST every run (the inversion guard), four D-12 guards, and a non-vacuity leg -- replacing ROADMAP criterion 5's inherited "eight previously fail-open registries" with a measured breakdown.
- 1. [Rule 1 - Bug] Fixed a regression in `test_shipped_ops_never_reach_sdp_arm`
- 1. [Rule 1 - Bug] `_dev_test_exit_code`'s own docstring tripped its own acceptance-criteria grep
- 1. [Rule 1 - Bug] `134-GH20-TRIAGE.md`'s own prose tripped its Task 1 acceptance-criteria grep
- Measured a fresh mypy/test baseline with no number to inherit, empirically pinned `get_command` (not `resolve_command`) as Click's gate hook via a throwaway spike, and added a fail-closed `FIRESTARTER_DEV_TOOLS` bench-override vocabulary to `channel.py` — proven fail-closed by a planted `bool()`-coercion mutation observed RED then restored byte-identically.
- Wired both D-01 mechanisms into `cli_handlers.py` -- a `_DevGroup(click.Group)` subclass supplying an informative refusal, and `if _DEV_TOOLS_ENABLED:` guards genuinely un-registering the six beta-only `dev` subcommands -- then rewrote the `dev` group's own docstring so it stops warning off the two commands (`read`, `test`) being kept in stable specifically for its own audience.
- Proved, from outside the process in real subprocesses, everything plans 136-01/136-02 built: a dual-channel Click harness pinning `dev --help` and `dev.commands` on both simulated channels (CHAN-01/02/03/04/06), a comprehensive no-firmware-read source scan across the gate's five new callables (CHAN-07), and two named source mutations each observed to break a specific assertion before being restored byte-identically.
- Deliberately re-baselined BOTH the `test_help_dev` snapshot the plan named AND the `test_help` snapshot 136-02 separately discovered breaks by the same mechanism, diff-scoped to prove only the CHAN-05 docstring text changed; then measured and recorded the phase's real post-edit CI-parity state -- mypy flat at 33/35 (checked 130), full suite 1494 passed / 0 failed, zero headroom spent across the whole phase.
- 1. [Rule 1 - Bug] GATE-02's `tools/diff_db.py` had no rule for the new fields, went RED
- None in the code sense
- Forked v1.30's own claim gate from Phase 122's vocabulary + Phase 123's mechanics per PITFALLS.md P-11, hosted inside Phase 137's own directory so `_DEFAULT_TARGETS` can never repeat the sibling-dir resolution defect, and proved the two mandatory target-resolution/basename tests non-vacuous via two independent seen-to-fail-then-restore demonstrations.
- AST-derived string-literal scanner over `diagnostic_report.py` -- the one `dev test` report surface no gate scanned before this plan -- sharing the meta-repo gate's 14-label vocabulary verbatim, proven non-hollow by a committed planted-violation fixture, wired into `pytest tests/` where CI already runs it.
- Authored `137-LEDGER.md` — the milestone's central closing artifact — pairing 11 permitted claims with their explicit non-claims, carrying forward all nine of the milestone's own measured-wrong corrections and three process failures into one outward-visible document, every figure re-measured live rather than copied from a citation.
- Fresh-measured RELOCK-07's fifth citation drift (634/823 -> 972/844) and closed it at all four sites; authored the next release's honest "withdrawal, not migration" release notes; dispositioned operator-batch C-1 defer-with-owner with a named-owner backlog todo; corrected CLOSE-05's own stale requirement text in the process.
- Operator approved the gh#12 reply wording (silicon caveat woven into the ask, not a disclaimer); posting is explicitly HELD pending the beta ship, and CLOSE-06 is deliberately left open at 55/56 rather than ticked-on-freeze.
- Armed and greened the v1.30 claim gate against its own four real closing artifacts for the first time this milestone (CLOSE-01), ran the whole-milestone CI-parity recipe a final time with every metric reconciled, and authored Phase 137's own closing record — leaving v1.30 at 55/56 requirements complete, by design, with CLOSE-06 openly outstanding and its single closing action already recorded.

---

## v1.23 PY32F071 Integration (Shipped: 2026-08-03)

**Phases completed:** 8 phases (123–130), 88 plans, 226 tasks

**Delivered:** Landed the in-flight PY32F071 firmware port and the host USB-DFU firmware installer onto `beta` as one lockstep integration — plus the cross-repo release-asset unblock that makes them reachable outside this tree — without touching the three AVR targets and without claiming anything about silicon that does not exist. 47/47 v1 requirements (BASE/MERGE/VPP/CFG/HOST/REL/PCB/CLOSE). A fourth board target now exists *beneath* the algorithm-first dispatch contract without disturbing it.

**The milestone is software-only, by physical necessity, and the record says so everywhere.** **No PY32F071 PCB exists** — nothing in this milestone has ever run on this silicon, and nothing in it could. The permitted claims are: the target builds clean; the native and host suites pass at their recorded case *and* suite counts; the DFU sequence is exercised against device descriptors and mocks; host-side timing and sizes are measured where a tool exists to measure them. `check_permitted_claims.py` — an 8-row forbidden-phrase table gated to a `PY32F071`/`py32` token within a 3-line proximity window, armed all-or-nothing over four named closing artifacts — mechanically forbids the rest, and was written in Phase 123 **before any firmware moved**. PR #48's pin map (PB0–PB7 data, PA0–PA5 control, VPP on PA4/ADC ch4) remains a placeholder describing no existing PCB, chosen only to match the vendor's own ADC example. The two claims never conflated: **a successful firmware install says nothing about the programmer working.**

**Closeout type:** `override_closeout` — 47/47 requirements ticked and every phase `phase_complete` with 7 of 8 `verification_status: passed`, but Phase 126 closed `passed-with-findings` (5/5 success criteria substantively achieved, 7/7 requirements, one *informational* finding: Criterion 3's literal "empty `git diff` on the test file" wording was not met because Plan 126-03's own three-board `#if` guard forced one compiler-argv line into the regression test, no assertion changed, disclosed in `126-NONREGRESSION.md` §Criterion 3 rather than smoothed over) — and `audit-open` reported the same 14 pre-existing cross-milestone open artifact items. Known verification overrides: 15 (see STATE.md → *Deferred Items — acknowledged at v1.23 milestone close*). **None of the 14 originate in v1.23 (Phases 123–130)** — they are the identical carry-forwards re-confirmed at the v1.18/v1.19/v1.20/v1.21/v1.22 closes, now the **sixth** consecutive close to acknowledge them.

**Requirements:** 47/47 v1 complete (BASE 8 · MERGE 8 · VPP 3 · CFG 7 · HOST 8 · REL 4 · PCB 5 · CLOSE 4), 0 unmapped, exact 1:1 category→phase mapping. Several shipped with the mechanism corrected rather than as prescribed, each recorded as a correction: **HOST-01** as an *accepted deviation* — the prescribed flasher-strategy extraction was declined precisely to keep the bench-earned avrdude ladder verbatim, which the branch achieves by not touching that function at all; **PCB-03/PCB-04** amended in `REQUIREMENTS.md` **in place** rather than annotated elsewhere, because those two clauses asserted a *fact* that is false (that the part lacks a vector table offset register) and a false fact does not survive being merely footnoted — the fact/mechanism boundary is now written into `REQUIREMENTS.md` itself, naming LOCK-04/LOCK-06/HOST-04/121 D-06/D-17 as the mechanism-class precedents it does not disturb; **REL-03**'s second half proven *locally only*, stated as such.

**Release state:** dual-repo lockstep merged to `beta` with `--no-ff` and pushed by the operator, after the D-02 blocking wording review. Observed cut tag **`3.0.0b15`** in both repos — *read verbatim from `gh release list`, never predicted or computed*. Both community channels independently re-verified public: the firmware GitHub prerelease carries **four** `.hex` assets including **`firestarter_py32f071.hex` — the first-ever publication of that asset**, which is the single thing that makes the 21 already-landed host DFU-install capabilities reachable outside this tree; and PyPI carries `firestarter==3.0.0b15`, resolved from a clean venv. `publish.yml` was manually dispatched, as at v1.22. **No stable release** — PyPI `info.version` remains `2.0.7`, consistent with every milestone since v1.11; stable stays operator-gated per standing policy.

**Key accomplishments:**

- **Every gate written before the thing it judges (Phase 123).** Six fail-provable checkers and the BASE-01 baseline JSON exist before a single firmware file moved: `check_cmake_manifest.py` (source-list drift with a commented `PY32_EXCLUDED` allow-list so a reader can tell deliberate omission from rename damage), `check_orphan_provisional.py`, `check_build_warnings.py`, `check_landing_range.py`, `check_size_baseline.py --policy merge05`, and `check_permitted_claims.py`. Every one ships with a committed planted-violation fixture and a pytest proving it exits non-zero. The BASE-01 baseline records flash **and RAM** for all three AVR targets plus native case *and* suite counts — RAM because a `PROGMEM`→RAM regression is invisible in a flash number. And **BASE-02/03 closed a gate that failed OPEN**: `_FW_ABSENT` used one *file* as the proxy for repo presence, so renaming that file flipped 5 gate legs PASS→SKIP at exit 0 with the false reason "firmware checkout absent" — now keyed on the un-renameable `../firestarter/.git`, with a present-repo-missing-target raising `MissingScanTargetError` instead of skipping.
- **The atomic landing, and the defect git could not see (Phase 124).** `agent/portability-macros` + `agent/py32f071-toolchain` landed as **one** commit-pair, because research measured that the "HAL prep leads" framing inherited from gh#16 describes a branch that is not self-sufficient: cherry-picked alone onto `beta` it takes `pio test -e native` from 141 cases / 17 suites passing to **0 passing / 17 ERRORED**. Both repos merged with zero textual conflicts and disjoint changed-file sets — and that is exactly why the milestone's highest-confidence finding matters: `platform/py32f071/CMakeLists.txt` still named `flash_type_3.cpp`/`flash_type_4.cpp`, renamed by v1.19 Phase 104, so git produced a *perfect* merge of a tree whose ARM target fails at CMake **configure** time, and `py32f071.yml` had no `push` trigger so nothing on `beta` would have reported it. **"The merge had no conflicts" is not a quality statement.** Fixed, plus `push: branches: [beta]` added; the AVR constraint discharged by measurement — Leonardo **−56 B**, Uno **+22 B**, 328PB **+28 B**, RAM unchanged on all three; and the **hollow guard already inside the branch** repaired: `RURP_PY32F071_PINMAP_CONFIGURED` was `#define`d `1` two lines above its own `#if !… → #error`, so the one mechanical hook for *"this pin map must not be trusted near a PROM"* enforced nothing. It now refuses all eight `is_memory_cmd()` commands, proven RED-before-GREEN in a third native env that compiles the real production path.
- **The VPP seam, with a permanence finding (Phase 125).** `include/rurp_vpp.h` + `src/rurp_vpp.cpp` **hand-authored** — nothing cherry-picked from PR #45, whose commits smuggle a `CONFIG_VERSION` bump and reroute AVR voltage measurement; proven not-ancestor of `HEAD` for all ten of PR #45's commits by a `merge-base --is-ancestor` classification, after the ROADMAP's own prescribed mechanism (`git log --all --grep`) was measured wrong two independent ways. `rurp_set_vpp_target_mv()` returns `MANUAL_ADJUSTMENT_REQUIRED` on every board, at **0 B flash and 0 B RAM** on all three AVR targets, proven non-vacuous in both directions. Two findings carried forward: the `#include "rurp_vpp.h"` line that all of this milestone's own planning documents described as *the phase's header change* collapses `pio test -e native` from 141/141 to 0 — omitted entirely, `rurp_shield.h` untouched; and **AVR-class manual VPP control is permanent, not provisional** — no Arduino-class board will ever carry the DAC.
- **Flash-persistent config on a part with no EEPROM (Phase 126).** A dual-slot CRC32 storage design — vendored `StoredConfiguration`, `CONFIG_MAGIC`, a table-free reflected CRC-32, and a `magic` → bounds-checked `length` → `crc32` validation *ordering* — behind a common/per-platform seam, with the AVR EEPROM backend proven a **pure move**: zero flash and zero RAM delta on all three targets under two named comparators, and the `rurp_configuration_t` schema and its `VER06` literal pinned by a 17-function gate. Sector 15 reserved in the linker script (page 256 B / sector 8192 B, a zero-length bootloader seam with its migration-cost comment), PR #48's non-persisting `config.cpp` **deleted and verified absent by path**, and the ARM manifest closed at 26 enforced sources — all in one commit, so the duplicate-definition link window was never opened. Design work, not integration: the cited `PORTING.md` specification exists only on two closed PRs.
- **The host DFU installer, and a gate that had been lying (Phase 127).** `feature/py32f071-fw-install` landed as a real merge commit; suite **1158 → 1293 passed / 0 failed / 0 skipped** at 81.88% coverage. `_check_envelope` retightened from the 128 KiB part size to the 120 KiB application region Phase 126 reserved; `DFU_UPLOAD` readback added with a `VerifyResult` enum and a "written but NOT verified" completion line — closing the gap where py32 was the project's only install path that wrote without verifying; `--usb-id` now actually *rejected* on a stable channel rather than merely hidden; DFU 1.1 opcodes anchored to literals genuinely fetched from `usb.org`, not imported from the module under test. And **the mypy watermark gate had been fail-open**: it shells to a bare `mypy` from `PATH`, and under Python 3.12 the configured `python_version = "3.9"` is rejected and a stub aborts the run — so it reported green without type-checking anything, hiding **69 inherited errors** against a watermark of 35. Phase 127's own net contribution measured **zero** (69 → 72 → 69). The 69 and the fail-open tool are deliberately left OPEN for a dedicated gate-hardening phase.
- **The release-asset fold, proven on two real CI dispatches rather than by reading YAML (Phase 128).** The ARM build became a composite action called by both `py32f071.yml` (LOUD) and `beta-build.yml` (SOFT, contained at the call site only), placed strictly *after* the version-bump auto-commit. Run A published `firestarter_py32f071.hex` (77284 B) alongside the three AVR hexes and asserted `PASS: image contains version string 3.0.0b99:py32f071`. Run B planted a real ARM compile error: the job still went green and published exactly the three AVR assets and no py32 asset — **and empirically validated the `outcome`-vs-`conclusion` distinction**, since GitHub set the contained step's `conclusion: success` while its `outcome` was `failure`, so a `conclusion`-keyed gate could never have fired. Both were draft rehearsal releases, since deleted; zero tags created. Also: **the phase's own prescribed way to break run B was unusable** — renaming a source path trips Phase 123's manifest-drift gate at a step with no `continue-on-error`, so the job would have failed *before* the ARM build and published nothing, demonstrating the exact opposite of the requirement. A phase's validation procedure can be wrong in a way that would have produced false evidence.
- **PCB decisions recorded while the board is still paper (Phase 129).** Self-flash bootloader over the existing CDC + COBS transport as the intended primary route, factory USB DFU as the maintainer/manufacturing recovery route; BOOT0/nBOOT1 straps, SWD pads, contiguous 8-bit port, VID/PID, and a flash budget citing the addresses Phase 126 **actually reserved** rather than an estimate. Held in two layers — the authoritative meta record and its firmware-repo subset — whose five `[SHARED:Sn]` sections a **41-leg cross-repo gate** compares body-for-body; firmware suite 180 → **221 passed**. Top-billed finding **F-10**: a contiguous 8-bit data bus is *physically impossible* on two of the seven candidate packages, which is a **part-selection** constraint, unrecoverable once layout starts. And the direct answer to the fail-open idiom: this gate was authored **before** the content it judges and went 31 RED → 0 RED entirely through content written afterwards — but one leg was authored **unreachable** (it required `MEMORY` and `{` on one source line; the linker script has them on lines 8 and 9), and nothing caught it until a later plan tried to satisfy it. **A gate that has never been seen to pass is not yet known to be reachable.**
- **An honesty ledger, not a victory lap (Phase 130).** `130-LEDGER.md` organises every claim into **six evidence tiers ordered weakest to strongest** — CI-compile-only, AVR-measured, native-simulated, mock-only, real-published-artifact, decision-only-unverified — so two adjacent rows cannot read as equally strong, and pairs each permitted claim with its explicit non-claim. It names, as things the milestone chose *not* to prove: the provisional pin map; the **absent ARM bus-trace oracle** (`HOST_STUBS_RECORD_BUS` runs on `native`, never on ARM, so the ARM target could diverge from the AVR goldens with nothing able to notice); **unmeasured USB-ISR-versus-PROM-pulse timing**; and HOST-03's mock-only ceiling. All 18 research corrections landed across `PROJECT.md`/`STATE.md`/`ROADMAP.md`/`REQUIREMENTS.md` and the notes file, proven by a committed label-aware checker (`check_record_corrections.py`, **0 unlabeled of 60** exempt hits). The v1.28/v1.29 py32 slots retired into v1.23 with v1.24–v1.27 proven byte-unchanged by a one-shot SHA-256 proof. And the `beta` push was made its **own explicit, operator-gated decision** — recorded in `130-DECISION.md` and committed *before* any push — because pushing `beta` auto-fires CI and cuts a beta, so the cut must never be a side effect.

**Known gaps / carried forward:**

- **Nothing here has run on a PY32F071, and that is the stated ceiling, not an oversight.** Every silicon-behaviour claim carries `[UNVERIFIED-UNTIL-SILICON]`. Two Phase 129 hardware questions stay open and unguessed: the **boot-selection option bit's factory default** (unknown from datasheet or bootloader manual — if it selects the wrong boot area the DFU recovery path is gone) and **whether the USB PHY provides an internal D+ pull-up** or a discrete resistor is required.
- **D-17's USB-identity tension is owned, not resolved.** The interim pid.codes `1209:0001` pair now published in `usb_cdc.c` is the registry's own documented *private-testing* pair, not an allocation, and the flash-path record's ship gate — no board ships and no release advertises a USB identity until a PID allocated under the community vendor id exists — stays byte-unchanged. A future reader may find that condition unmet, which is exactly what a condition's wording permits. Research's own assumption A3 (publishing an image carrying the interim pair does not redistribute a *device*, because there is no board) is named as a judgment call, not a settled reading.
- **The ARM pass is delta-and-byte-identity only.** The ARM toolchain *is* installable in this devcontainer (correcting a false "absent" premise), but a local build's absolute size is never comparable to CI's — measured `text=27260` local against `text=27344` CI. Every absolute ARM size claim cites a CI run URL plus a commit SHA. **Byte-identity never implies the image runs.**
- **Eight deferrals, each with a reason:** FUT-N02 live install progress (avrdude's own progress is swallowed by pipe buffering on all three AVR boards; adding it to the least-proven path alone would be perverse) · FUT-N04 software reboot-into-bootloader (its VTOR-absence reason is corrected false; the deferral stands on its other three) · **FUT-N05 the self-flash bootloader — the seed's own primary route; landing DFU does not retire it** · FUT-N06 raw-binary release asset · FUT-VPP closed-loop DAC control · FUT-CAL the bandgap calibration model (owned by the queued White-Box Voltage-Reading Calibration milestone) · **FUT-ORACLE the ARM bus-trace oracle** · FUT-ARMSIZE ARM flash/RAM as a checked-in baseline with a RAM ceiling (CI reports size only into the job log today — nobody would notice a regression there).
- **REL-04's cross-repo filename binding is held by local runs and developer discipline, not by CI in either repo** — neither app CI workflow checks out the firmware sibling. Say so rather than implying otherwise.
- **⚠ 69 mypy errors and the fail-open `check_mypy_watermark.py` are deliberately OPEN**, and `firestarter_app`'s primary `ci` job is RED until a dedicated gate-hardening phase fixes them. Not v1.23's contribution (measured net zero) and not v1.23's to fix.
- **⚠ Three CI-only sibling-checkout test defects fired on the real b15 push**, invisible in this devcontainer because it *has* the sibling layout standalone CI lacks. Two fixes (`firestarter` `1c511e8`, `firestarter_app` `5934a54`) landed on `beta` directly during the operator's hand-off, **outside any plan** — and one of them **softened a Phase-129-authored hard assert** (`test_present_root_with_missing_target_raises_not_skips`) to a skip, a defect-class change flagged rather than treated as routine. Both are ancestors of `origin/beta` and of neither milestone branch; the divergence is recorded, not silently reconciled.
- **The community inbox is not empty, and this close does not imply otherwise.** gh#20 (an AT28C256 `dev test` FAIL, reported 2026-07-30) and gh#18 (FM1608 `dev test` PASS) both arrived *after* the 2026-07-27 backlog import that stopped at gh#17. Out of scope here; no community thread received a comment this milestone and no CLOSE requirement depended on a reply.
- **Carried from v1.22, still owed:** reintroduce `firestarter_app`'s `81fa53c` whenever a milestone branch next merges toward `main`; `check_ledger.py`'s 2 pre-existing `LEDGER-01` REDs from v1.19 Phase 104's rename remain unfixed (a small self-contained backlog seed).

**Release state (repos):** meta tagged `v1.23` on `gsd/v1.23-py32f071-integration` (pushed); firmware + app tagged `v1.23` on `beta` (pushed); meta gitlinks bumped to the published `3.0.0b15` commits (firmware `0933bd7` / app `16a313a`). Consistent with v1.19–v1.22: **`main` is never merged** in any of the three repos.

**Full detail:** `.planning/milestones/v1.23-ROADMAP.md` · `.planning/milestones/v1.23-REQUIREMENTS.md` · `.planning/milestones/v1.23-FLASH-PATH-DECISION.md` · phase artifacts under `.planning/phases/130-close-honesty-ledger-claim-gate-release-decision/` (`130-LEDGER.md`, `130-DECISION.md`, `130-CHANNELS.md`, `130-NONREGRESSION.md`, `130-RELEASE-NOTES-{fw,app}.md`) and each phase's own `12N-NONREGRESSION.md`.

---

## v1.22 AT28C Software Data Protection Lifecycle (Shipped: 2026-07-30)

**Phases completed:** 7 phases (116–122), 69 plans, 176 tasks

**Delivered:** Made Software Data Protection on protocol `0x0D` (`configure_eeprom28c`) explicit, observable and bidirectional — and, in doing so, fixed the shipped SDP-disable sequence that four independent research streams proved almost certainly never reached silicon. 41/41 v1 requirements (TRACE/FIX/OBS/LOCK/HOST/DEVTEST/GATE/CLOSE).

**The milestone opened with a FIX, not a feature.** Kickoff research falsified the promoting note's own premise twice. `flash_util_byte_flipping` → `fu_flash_fast_address` bypassed `mem_util_remap_address_bus` entirely and hard-coded `/WE` for the single pinout (`DIP32_SST39SF040`) every bench-proven chip uses — so on all four `0x0D` pinouts at least one command write in the shipped sequence was emitted with `/WE` HIGH (a documented Write Inhibit), across all 84 `0x0D` chips. The success check `eeprom28c_wait_for_write(handle, 0x5555, 0x20)` was **inverted**, not merely weak: both datasheets state the command data "is not written to the device," so the check could only pass when the sequence was *not* recognised.

**Closeout type:** `override_closeout` — all 7 phases `phase_complete` + `verification_status: passed` (Phase 122 verified 5/5), but `audit-open` reported 14 pre-existing cross-milestone open artifact items. Known verification overrides: 14 (see STATE.md → *Deferred Items — acknowledged at v1.22 milestone close*). **None originate in v1.22 (Phases 116–122)** — they are the identical carry-forwards re-confirmed at the v1.18/v1.19/v1.20/v1.21 closes.

**Requirements:** 41/41 v1 complete (TRACE 6 · FIX 6 · OBS 5 · LOCK 6 · HOST 6 · DEVTEST 6 · GATE 3 · CLOSE 3), 0 unmapped. Two shipped mechanism-corrected rather than as prescribed: **LOCK-04** as a generic op-layer NULL-`main` refusal in `operation_utils.cpp` rather than the roadmap's `0x0D`-local `default:` arm (which would have refused `read`/`verify` on all 84 `0x0D` chips); **D-01/D-02's** curated SDP allow-set replaced by one **derived** from minipro `infoic.xml` `flags` bit 15 (`MP_PROTECT_AFTER`) at operator directive — ALLOW 43 / REFUSE 41 = 84, all matched, zero MIXED.

**Validation ceiling — honoured, not softened.** No AT28C part on the operator's bench, so validation is software-only throughout: native register-trace goldens, host pytest, source-scan gates, and measured host-side timing. `0x0D` stays **`UNVERIFIED`** in `PROTOCOL-LEDGER` at close, zero chips changed `support_status`, the 84-chip count unchanged (`diff_db.py` identity). The permitted claim is *"the SDP lock and unlock sequences are emitted exactly as specified, verified byte-exact by golden register trace, with a documented and measured host-side timing assumption"*; the forbidden claim is *"SDP lock/unlock works on an AT28C256."* A committed regex gate (`check_permitted_claims.py`, 7 subprocess pytest legs + 2 planted-violation fixtures) mechanically enforces the forbidden half across all five closing artifacts.

**Release state:** dual-repo lockstep merged to `beta` and pushed (firmware `953f748` → CI auto-cut, app `4001396` → CI auto-cut); observed cut tag **`3.0.0b14`** in both repos — *derived from `gh release list`, never hardcoded* — with `publish.yml` manually dispatched (run 30555530238) because 6 of 13 historical app betas never reached PyPI. Both community channels independently verified public: PyPI JSON API + clean-env `pip index`/`pip download` from `$(mktemp -d)`, and the firmware GitHub prerelease's three `.hex` assets via `gh release view`. Never via a green CI tick, never via the editable install. **No stable release** — PyPI `info.version` remains `2.0.7`; stable stays operator-gated per standing policy. The stray `3.0.0b12` prereleases stay public (D-05, CLEANUP declined).

**Community close:** gh#12 answered with the decided auto-unlock policy (its reporter's own 2024 design question) and gh#11 followed up on both defects — each framed as *"here is what changed and why we believe it addresses your report; please re-test,"* never as a verified fix. Both left **OPEN** with zero labels; both comment bodies verified byte-equal to artifacts frozen by committed git blob SHA. gh#11's reporter had **reproduced the exact predicted INIT abort on real AT28C256 silicon** — the defect is community-corroborated even though the fix is not.

**A locked decision was caught overclaiming.** Phase 122's research measured D-14's prescribed public answer to `No-Hazmats` ("your AT28C parts should now work") as **false**: every 2K×8 `0x0D` part sits on pinout `DIP24_2816` and all 19 of 19 are REFUSED by the derived allow-set (7 `pre-SDP generation`, 12 `unrecognised`), with `AT28C16` additionally `adapter-required`. Surfaced as an explicit operator accept-or-overturn at the D-16 wording review rather than silently posted — inside the one phase whose job is not overclaiming.

**Key accomplishments:**

- **The oracle before the fix (Phase 116).** A second opt-in `host_stubs_common.inc` recording layer captures production's real register-cache *elision* as an ordered data+strobe stream — closing the fidelity gap that let abandoned commit `0052c42` swap the SDP tables and still report "22 tests PASS (zero-diff)". `bus_config_t` ground truth for 5 representative AT28C chips was *derived* from the host's own `convert_to_programmer` path (not transcribed) into a generated `DO NOT EDIT` header behind a 4-test drift gate, and the `0x0D` SDP trace suite was proven RED against the shipped tree before a line of production code moved.
- **The remap-aware emitter + honest completion signal (Phase 117).** A `0x0D`-local command emitter built on `handle->firestarter_set_data` puts every command write through the full remap, so `/WE` is asserted on all four pinouts and the A16–A18 staleness gap for the 18 chips ≥64 KB closes as a by-product; the inverted `(0x5555, 0x20)` read-back is gone. `eeprom28c_write_execute`'s per-page polling was corrected from **1 byte in 64** to full coverage — the more likely root cause of gh#11's symptom than SDP, and the finding that reclassified gh#11 as a **conflation** bug rather than a sampling-rate bug. `flash_utils.{h,cpp}`, `flash_5v_page.cpp`, `flash_nor_unlock.cpp` stayed byte-untouched; the `0x05`/`0x06`/`0x07`/`0x10`/SRAM traces stayed byte-identical.
- **Auto-unlock made visible and declinable (Phase 118).** One report line before the sequence and one after, never inside it — proven by a source-scan test with a planted `LOG_` fixture; `FLAG_SKIP_SDP_UNLOCK` (`0x100`) honoured in firmware; `AT28C_TBLC_MAX_US = 100` named and cited at every call site; and the emitted sequence's host-side duration **measured** per board via `micros()`. That measurement is one of the very few v1.22 claims provable without an AT28C — and it undercut D-09's "never fires" framing: 572/600 µs is 4.7 % headroom, not comfortable margin.
- **The lock half, which never existed (Phase 119).** `CMD_SDP_UNLOCK`/`CMD_SDP_LOCK` invocable standalone with no data payload and no host `DONE` round-trip; the lock body emitted as 3 loads + `t_WC` per Atmel doc0270 §19 note 2; the ordinal `cmd < CMD_DEV_ADDRESS` admission guard replaced by an explicit `is_memory_cmd()` predicate proven identical with and without `-D DEV_TOOLS`. Flash delta +392 B against the live 2992 B headroom.
- **The host half, landed second on purpose (Phase 120).** `firestarter dev sdp <chip> enable|disable` behind the v1.21 destructiveness confirm + `-y` + the SAFE-04 absent-chip hard-fail; `write --skip-sdp-unlock` emitting `0x100`; `CMD_*`/`FLAG_*` landing in the same commit pair across `firestarter.h` ↔ `constants.py`. HOST-06 exploits the detectability asymmetry between an unknown *command* (loud error) and an unknown *flag bit* (silence): the host now **requires** firmware's `MSG_WARN_SDP_UNLOCK_SKIPPED` (0x86) ack and fails loudly when it never arrives — so a user asking to skip the unlock against old firmware can no longer have it run anyway in silence. The capability refusal is a fail-closed allow-list with zero DB change.
- **`dev test` made trustworthy before it was used as evidence (Phase 121).** `FLAG_CAN_ERASE` cleared for `0x0D` at `database.py`'s source, so the sweep stops fabricating an erase against the 28C family and stops auto-tagging a *passing* chip `community-fail` — without which every community re-test report would have poisoned this milestone's own evidence. Plus the operator's `dev test` redesign (recorded as a REVERSAL of three locked decisions): zero CLI options, an exact name-keyed `is_uv_eprom` predicate at **301/301** versus the old execution-time proxy's 32/301, a three-valued `write_scope`, and a read-only `gh issue list` dedup query before every ask.
- **Anti-hollow gates throughout.** Every new CI checker ships paired with a pytest that proves it *fails* on committed planted-violation fixtures — `check_sdp_capability_invariants.py` (9 legs, the repo's first `.py` fixtures), `check_permitted_claims.py` (7 legs), and the SAFE-03 orchestrator scan extended to `submit.py`. This is the discipline that closed v1.12's hollow-GATE-03 debt, now applied by default.
- **An honesty ledger instead of a victory lap (Phase 122).** `122-LEDGER.md` pairs each of nine claim classes with an **explicit non-claim**, carries the emission-traced-vs-operation-permitted distinction per pinout, records five mechanism corrections including the flagged D-14 divergence, and documents D-12's negative space (SDP-F1..F8 plus three owned trade-offs). `PROJECT.md`'s **EIGHTH CORRECTION** was proven purely additive by `git diff --numstat`.

**Known gaps / carried forward:**

- **`0x0D` graduation is silicon-blocked, by design.** "SDP works on real AT28C silicon" has a sampling rate of **zero** and stays that way until a community re-tester (gh#11/gh#12) or a future bench session supplies real silicon. This is the milestone's stated ceiling, not an oversight.
- **AT28C 2K×8 class (19 chips on `DIP24_2816`) remains REFUSED** — 7 `pre-SDP generation`, 12 `unrecognised`; SDP-F7/SDP-F8 name that family deferred. `AT28C16` also stays `adapter-required` (FUT-04).
- **`check_ledger.py` is pre-existing RED** — 2 `LEDGER-01` violations from v1.19 Phase 104's `flash_type_3`/`flash_type_4` → `flash_nor_unlock`/`flash_5v_page` rename. Unrelated to v1.22 and deliberately not fixed here (fixing it would edit a closed milestone's artifact). CLOSE-01 never gated on it. Recommended as a backlog seed.
- **⚠ App CI fix `81fa53c` lives on `firestarter_app`'s `beta` only.** It adds a `pytest.mark.skipif` guard to `test_check_is_memory_cmd_no_ifdef.py` and `test_check_no_log_in_sdp_window.py`'s `test_checker_exits_zero_on_clean_source` legs, both of which hard-fail in a standalone checkout with no sibling `firestarter` repo to resolve the real firmware source path against. It was cherry-picked onto the milestone branch and then **reverted** to keep the branch HEAD an exact match for Plan 122-03's recorded merge SHA. **It must be reintroduced whenever the milestone branch next merges toward `main`**, or `ci.yml`'s equivalent standalone-checkout risk resurfaces. Recorded in `122-CUT.md` §8.
- **Meta `catalog-sync-check.yml` and firmware `build.yml`'s `pio test -e native_nodevtools` step are `main`-gated — dormant, never run against v1.22 code.** Corrected against the workflow files at close: the Phase 122 hand-over attributed `ref: main` checkout steps to both, but only one has them. `catalog-sync-check.yml` lives in the **meta** repo (not a sub-repo), triggers on push/PR to `main` scoped to `paths: tools/catalog/**`, and checks out **both sub-repos at `ref: main`**. Firmware `build.yml` carries no `ref:` override — it simply only triggers on `push: branches: [main]`. Under the never-merged-to-`main` branch model both are dormant rather than red. A known property, not a defect to chase.
- `--sdp-relock`, the three-field SDP report shape, and `lock-status` + a hand-curated protection table all stay **deferred/out of scope** (seed planted).

**Release state (repos):** meta tagged `v1.22` on `gsd/v1.22-at28c-software-data-protection-lifecycle` (pushed); firmware + app tagged `v1.22` on `beta` (pushed); meta gitlinks bumped off PINNED-at-b11 to the published `3.0.0b14` commits (firmware `5c9160a` / app `e7d3ee8`). Consistent with v1.19–v1.21: **`main` is never merged** in any of the three repos (firmware `main` lags `beta` by 268 commits, app by 544, meta by 1267).

**Full detail:** `.planning/milestones/v1.22-ROADMAP.md` · `.planning/milestones/v1.22-REQUIREMENTS.md` · phase artifacts under `.planning/phases/122-close-honesty-ledger-community-ask-release-decision/` (`122-LEDGER.md`, `122-DECISION.md`, `122-CUT.md`, `122-CHANNELS.md`, `122-NONREGRESSION.md`, `122-DELIVERY.md`).

---

## v1.21 Community Chip-Validation Command (Shipped: 2026-07-27)

**Phases completed:** 9 phases, 34 plans, 70 tasks

**Key accomplishments:**

- EpromOperationError gains a backward-compatible `error_code` attribute carrying the firmware `response.id` byte, threaded through the single `_raise_for_error_response` chokepoint.
- Greenfield `chip_test.py` module: XOR-fold address-derived pattern generator (region-parameterized) plus a four-bucket byte-mismatch fingerprint classifier that reuses `consistency_check_eprom`'s divergence math and never over-confidently coerces an ambiguous distribution into a false diagnosis.
- Added `derive_plan()` to `chip_test.py` — derives an ordered, per-chip op list (id/read/blank-check/write/verify/erase) strictly from frozen DB fields via `get_eprom`/`convert_to_programmer`, structurally bypassing `resolve_chip`'s support-status guard so coverage-expansion chips (even `adapter-required` ones) still get a plan.
- `run_plan()` composes existing `EpromOperator` methods through the guard-honoring `resolve_chip` path into a non-fatal, id-first, N>=2 sweep executor with an OK/BAD/NA/SKIPPED/marginal verdict vocabulary and firmware `error_code` capture.
- `derive_plan()` now structurally strips write/erase from non-destructive plans into an advisory `locked_destructive` list, and UV-EPROM chips get a 256 B top-anchored high-address write window enforced as an engine constant no DB field can widen
- Applicable-only N-of-M banner count helper (`count_applicable`) reads Phase 109-01's `Plan.locked_destructive` field without a second derivation, and the SAFE-02 orchestrator-only safety property is now asserted by 5 mechanical tests instead of merely documented
- AST-based CI checker (`tools/check_devtest_orchestrator.py`) denies VPP-set / raw-wire-dict / `--force` in `dev test`'s code paths, paired with a mandatory anti-hollow pytest that proves the gate actually fails on 4 planted violation classes -- closing this project's v1.12 hollow-GATE-03 tech debt.
- New `diagnostic_report.py` module: a single-source `DiagnosticReport` dataclass whose `render()` (rich table) and `to_json_block()` (fenced JSON) both read the same `to_dict()` mapping, plus `AutoCapture`/`TransportHealth` sub-objects with an honest `"not measured"` fallback for unreachable transport counters.
- `Provenance` dataclass + `prompt_provenance()` (injectable `rich.prompt` component) + `is_submittable()` predicate added to `diagnostic_report.py`, composed into `DiagnosticReport`'s existing single-source `to_dict()`/`render()` without restructuring plan-01's contract.
- `DbDiff` dataclass + `build_db_diff()` read-only transform added to `diagnostic_report.py`, composed into `DiagnosticReport`'s single-source `to_dict()`/`render()`, proven read-only-by-construction with a write-method-less Mock DB and a structural no-write scan.
- Seven named pytest functions across test_hardware.py and test_diagnostic_report.py pin the VOLT-01 measured-voltage sampler contract (units, median, state routing, honest-fallback, format-drift guard, and report voltage-split) as intentional RED state ahead of Plans 02/03's implementation.
- Value-returning `sample_vpp_mv()`/`sample_vpe_mv()` on `HardwareManager` reconstruct median millivolt readings from 0xE4/0xE5 DATA frames by regexing `Response.message` (Pattern A), turning the print-only VPP/VPE monitor into a report-ready numeric value.
- Split `DiagnosticReport`'s combined `vpp_vpe_mv` slot into six D-01/D-03/D-04 voltage fields (destructive before/after per rail + standalone), surfaced through a new `_voltage_dict()` helper and a single `render()` table row — turning the Plan-01 RED test GREEN.
- Threaded an optional `sampler` callback through `run_plan`'s dispatch chain, bracketing each OP_WRITE's `operator.write_eprom` call with `sampler("before")`/`sampler("after")` while keeping `chip_test.py` fully agnostic of `hardware.py`.
- Built the `firestarter dev test <chip>` end-to-end CLI flow — provenance/destructive-confirm prompts, derive_plan/run_plan/count_applicable composition with a hardware-sampler thunk bracketing the write step, DiagnosticReport assembly, stdout render, optional dual-artifact write, and a 3-way (0/1/2) scriptable exit code.
- Repointed the SAFE-03 AST checker off a nonexistent stub onto the real `cli_handlers.py` handler with a new AST function-name-scoped scan (avoiding 10 pre-existing unrelated `--force` false positives), added its anti-hollow negative-fixture proof, and shipped 16 hardware-free CliRunner tests covering every `dev test` exit-code/prompt/sampler/artifact behavior.
- Deleted `dev test`'s four interactive provenance prompts (the `/`-in-choice-string bug that rejected `new`/`used`/`2.0`), replaced them with firmware-auto-captured `hw_revision`, and redefined `is_submittable` on auto-capture completeness only -- the `--destructive` SAFE-03 safety confirm is untouched.
- Fixed `derive_plan`'s unconditional OP_VERIFY append (chip_test.py:387) so a non-destructive `dev test` run is genuinely 3 steps (id, read, blank-check) instead of 4 — restoring the tool's safest default invocation to a trustworthy `exit 0`, matching every locked success criterion and the shipped `--help` text.
- Deterministic 12-char SHA-256-derived dedup id (chip + protocol + ordered step verdict/fingerprint shape) landed in `diagnostic_report.py`'s single-source `to_dict()`, so both renders and Plan 02's submission flow can read `dedup_fingerprint` for free.
- `submit.py` foundations -- D-01 hardcoded-repo constants, a recursive SUB-02 PII/path sanitizer, title/body/URL builders reading the Plan-01 dedup fingerprint, and a PATH/auth-gated `gh` shell-out tier using list argv + stdin body.
- Browser-tier D-05 byte-cap escalation (drop JSON at 7.5 KB encoded, hard-stop at 8 KB) plus the single `submit_report` orchestration entry implementing the D-03 refuse gate and D-04 TTY/off-TTY dispatch, all seam-injected against `test_submit.py`.
- `--submit` Click flag + lazy `submit_report` call site closes SUB-01/02; SAFE-03 orchestrator gate now scans `submit.py` as a third full-scan leg, proven non-hollow via planted-violation fixtures — this closes Phase 113.
- `DbDiff` gains a report-side `ladder_state` field (community-reported/community-fail/none) derived purely from sweep verdicts, with `community-confirmed` formalized as a documented human-only target that no code path can emit; `doc/community-validation.md` documents the full taxonomy and N>=2 promotion process.
- `tools/parse_devtest_issue.py` — a stdlib-only CLI that detects a community `dev test` GitHub issue via its `[dev test]` title marker plus fenced-JSON `schema_version`, surfaces the current-vs-proposed DB-diff (including Plan 01's `ladder_state`), and counts matching `dedup_fingerprint`s across saved issue bodies to realize GRAD-01's cross-report N>=2 signal.
- AST-based CI gate (`tools/check_no_community_support_status_write.py`) proves no code path in the report/parse path writes a chip's `support_status`, mirroring SAFE-03's anti-hollow checker+pytest pairing with a write-target deny rule instead of a call-site/dict-literal deny rule.
- `dev test <chip>` now hard-fails before energizing hardware when the chip name is absent from the database, via a 2-line `get_eprom`-keyed guard reusing the existing `ChipNotFoundError` path — while a present-but-unsupported chip still runs the full community-validation sweep.
- New stranger-oriented `firestarter_app/doc/beta-testing-install.md` covering the full fresh-machine install → flash → smoke → dev-test hand-off chain, plus a single non-duplicating README pointer link.
- Reproduced the app (`beta-release.yml`) and firmware (`beta-build.yml`) release CI gates locally on the exact v1.21 trees — both green modulo documented pre-existing REDs — and cleared the operator publish-precondition gate. No repo files changed; no publish/push/merge fired.
- Published the `3.0.0b11` GitHub prerelease on `henols/firestarter` carrying all three board `.hex` assets, and positively confirmed it resolves through the app's own `fw -i` code path for every bench board — the ONBOARD-02 firmware half of Step 0 is public.
- Published `firestarter 3.0.0b11` to PyPI (`pip install --pre firestarter`) and the matching app GitHub release — the ONBOARD-01 Python-package half of Step 0. With Plan 03, BOTH community channels are now public; the milestone is community-installable and the PINNED-at-b10 gitlinks can move forward.
- Arduino Uno HARD gate PASSES — a fresh-machine `pip install --pre firestarter` (3.0.0b11) flashed the Uno beta firmware via the bare `fw -i` `--pre` auto-route and the flashed stack is alive (fw + hw).
- Arduino Leonardo HARD gate PASSES — fresh-machine beta install flashed the Leonardo beta firmware via the `fw -i` `--pre` auto-route and the flashed stack is alive (fw + hw).
- uno328pb best-effort gate PASSES — fresh-machine beta install flashed `firestarter_uno328pb.hex` via the `fw -i` `--pre` auto-route and the flashed stack is alive (fw + hw). The historically-unstable third board was stable this smoke-only run.
- Closed the loop: finalized the ONBOARD-04 onboarding doc from the three clean per-board bench runs and bumped the meta-repo submodule gitlinks off the long-standing PINNED-at-b10 hold to the public `3.0.0b11` commits.

## v1.20 Protocol-Only Dispatch (Shipped: 2026-07-02)

**Phases completed:** 3 phases (105–107), 7 plans, 19 tasks

**Delivered:** Removed the vestigial `mem_type`/`type` backward-compat dispatch axis end to end — firmware, wire, and host now trust *only* the real protocol (`algorithm`); 12/12 v1 requirements (FW/WIRE/HOST/DOC/GATE/SAFE).

**Closeout type:** `override_closeout` — all 3 phases verified (`passed`), but `audit-open` reported 14 pre-existing cross-milestone open artifact items. Known verification overrides: 14 (see STATE.md → *Deferred Items — acknowledged at v1.20 milestone close*). None originate in v1.20.

**Requirements:** 12/12 v1 complete. LEGACY-01 (`FLAG_VPE_AS_VPP`) + LEGACY-02 (`EPROM_LEGACY` naming) deferred to v2.

**Release state:** meta tagged `v1.20` + `gsd/v1.20-protocol-only-dispatch-remove-the-legacy-mem-type-axis` merged to `beta`, both pushed to origin at close (operator override). Firmware/host sub-repo work on the v1.20 branch; gitlinks PINNED at b10 (fw `2d93379` / app `e0bdea4`); lockstep beta cut `3.0.0b11` + gitlink bump remain operator-gated per standing v1.11–v1.19 policy.

**Key accomplishments:**

- 1. [Rule 3 - Blocking] Executed the D-01 v1.19→beta merge + v1.20 branch fork (both sub-repos) as a precondition
- Deleted the `_ALGO_MEM_TYPE` fallback dict, `determined_type` derivation, and both `type` dict keys from `database.py`, completing the host emit-side of WIRE-01 — the wire dict now carries `algorithm` as the sole dispatch datum, proven by 8 inverted test functions asserting `type`'s absence.
- Removed the last numeric `mem_type`-keyed display fallback (`type_map`) from `ic_layout.py`'s shared label helper — `info`/`list`/`search` now derive labels solely from `electrical.type` then protocol, landing on bare `"Unknown"` for anything else.
- Added the fail-closed algorithm-presence guard to `chip_resolver.resolve_chip` mirroring firmware `protocol == 0 → 0xBB`, proved by a D-06 regression test, and closed out the wave-close integration gate for Phase 106.
- Rewrote firestarter/CLAUDE.md's dispatch narrative to protocol-only dispatch, scrubbed the stale numeric `type` wire references from both agent-facing CLAUDE.md files, and recorded the v1.20 wire-contract break in both sub-repo READMEs.
- Removed the retired `MSG_ERR_MEM_TYPE_UNSUPPORTED (0xAE)` message from the canonical catalog and regenerated host/firmware artifacts, incidentally catching and fixing an unrelated pre-existing Phase-95 catalog desync (`MSG_WARN`/`MSG_ERR_FL4_BOOT_BLOCK_LOCKED`) that the naive sync would otherwise have silently deleted from the host, breaking a live test.
- Re-ran every GATE-01/GATE-02/SAFE-01 non-regression gate on the fully-applied v1.20 state (post 107-01 doc scrub + 107-02 codegen fix) — all green or exactly matching the documented pre-existing beta baseline, zero new regressions, mem_type-axis removal proven dead code for all 746 chips.

---

## v1.19 Protocol Naming Labels (Shipped: 2026-07-02)

**Phases completed:** 5 phases (100–104), 10 plans

**Delivered:** A single canonical, behavior/datasheet-correct, human-readable name set for
every protocol number (0x05/06/07/08/0B/0D/0E/10/27/28/29/34 + phantom 0x35/0x39), applied as
a legibility layer on top of the unchanged algorithm-first dispatch contract — a `PROTO_<NAME>`
C-token in firmware, a consolidated display name in the host CLI, and reconciled facet prose +
an INV-01..09 traceability matrix + a name↔slug divergence record in `firestarter/doc/PROTOCOLS.md`.
Protocol numbers stayed the dispatch key end to end throughout — no `chip_database.json` / wire
/ lockstep-constant value change; CLI grammar unchanged (GATE-01/02/03 held in every phase that
touched their surface, re-verified at close).

**Audit:** GATE-01/02/03 re-verified at close (Phase 103 Plan 02) — dispatch-mirror guard
green, `check_dispatch.py` green, `pio test -e native` 82/82 green, `diff_db.py` identity vs
the documented Phase-94 baseline, constants-parity 6/6 green under py3.12 (py3.11-target leg
CI-PENDING per the Phase-98 precedent — no python3.11 binary in the devcontainer), no CLI/source
file touched. No `FAIL` verdict recorded for any gate. Report:
`.planning/phases/103-docs-reconcile-prose-divergence-record/103-VERIFICATION.md`.

**Release:** meta tagged `v1.19` + milestone branch `gsd/v1.19-protocol-naming-labels`
`--no-ff` merged into `beta`; both the tag and `beta` **pushed to origin** at this close
(operator-authorized override of the usual keep-local policy, 2026-07-02). Sub-repo lockstep
beta cut `3.0.0b11` + gitlink bump remain operator-gated (standing v1.11–v1.18 policy);
gitlinks stay PINNED at b10 — NOT triggered by this naming/legibility-layer milestone.

**Known deferred items at close:** NAME-F1 (renaming the `datasheets/<hex>-<NAME>/` folder
slugs to match the new vocabulary — avoids provenance churn; the name↔slug divergence is
recorded, not resolved) and NAME-F2 (accepting a protocol name/alias as CLI input — chip
selection stays by part number). Both explicitly out of scope per `.planning/REQUIREMENTS.md`.
Pre-existing cross-milestone carry-forwards (FUT-01/03/04/05/07/08 etc.) are unchanged by this
milestone — see STATE.md → Accumulated Context.

**Key accomplishments:**

- **Phase 100 (NAME):** Authored the single canonical 3-field name set (`PROTO_<NAME>` token +
  short display name + datasheet-cited facet prose) for every protocol number + phantom ID +
  an operator-approved handler-family name layer for the many-to-one handlers; resolved the
  0x0E-vs-0x29 (both 32-pin SRAM) name collision at explicit operator approval — a blocking
  gate that gated all downstream phases. Recorded in `firestarter/doc/PROTOCOLS.md`, revised
  in place. Operator-approved deviations from draft: 0x29=`PROTO_SRAM_32PIN_NVRAM` (0x0E stays
  `PROTO_SRAM_32PIN`), phantoms=`PROTO_PHANTOM_0x35`/`0x39`, 0x34=`PROTO_EEPROM_8051BUS`.

- **Phase 101 (FW):** Defined the `PROTO_<NAME>` constants (numeric values unchanged — the
  label *is* the number), relabeled the raw-hex dispatch chain in `memory.cpp` to named
  constants (including honest phantom tokens for 0x35/0x39), and renamed the many-to-one
  handler files/functions from the approved family-name layer. Dual-repo lockstep
  (`constants.py` ↔ `firestarter.h`); GATE-01/02/03 first/primarily enforced here.

- **Phase 102 (HOST):** Consolidated the two divergent host protocol vocabularies
  (`ic_layout.proto_display` + `protocol_info_data`) onto the canonical display names via a
  single `_PROTOCOL_DISPLAY_NAME` map, so `firestarter info` / `list` / `search` render one
  consistent name per protocol (ASCII-normalized dashes — a documented punctuation deviation
  from the doc's em-dash names).

- **Phase 103 (DOCS, close):** Renamed all 12 §1.x PROTOCOLS.md headings to `PROTO_` token
  form, regenerated the 8 dependent §3 cross-link anchors (grep-verified against actual
  rendered headings, not hand-guessed), augmented all 9 INV-01..09 rows with their tokens
  beside the raw hex (SAFE-02 grep-contract columns kept byte-identical), purged two residual
  bucket-label jargon prose sentences respecting the three D-02 locked retentions (approved
  0x06 name, frozen slug strings + citation paths, §2 minipro-provenance prose), and added a
  "Name ↔ Slug Divergence" callout recording the frozen-slug map / NAME-F1 deferral / host
  ASCII-dash deviation. Re-verified GATE-01/02/03 at close with zero FAIL verdicts.

- **Phase 104 (RENAME, post-close follow-on):** Renamed the two remaining minipro-heritage flash
  handler file-pairs + entry functions in dual-repo lockstep — `flash_type_3.{h,cpp}` →
  `flash_nor_unlock.{h,cpp}` / `configure_flash3` → `configure_flash_nor_unlock` (0x06);
  `flash_type_4.{h,cpp}` → `flash_5v_page.{h,cpp}` / `configure_flash4` →
  `configure_flash_5v_page` (0x05 + phantom); fixed two long-mismatched header guards; updated
  all 4 `memory.cpp` dispatch call sites (Wave 1). Brought host GATE-01 dispatch-mirror tooling
  into lockstep — `check_dispatch.py`, `validation_matrix_spec.json`, regenerated
  `validation_matrix.h`, host doc tables (Wave 2). Renamed native validation suites
  `test_val_flash3/4` → `test_val_nor_unlock`/`test_val_5v_page`, updated `platformio.ini`,
  `PROTOCOLS.md` §0/§1/§3 + SAFE-02 INV suite-path contract, `firestarter/CLAUDE.md`, and closed
  the doc↔tool↔firmware dispatch-mirror bind (Wave 3). `git mv` preserved rename history. Full
  phase gate green: `pio test -e native` 82/82, both boards build byte-identical (25654 B /
  89.5% Leonardo — pure rename, zero flash delta), host `pytest` 14/14, `diff_db.py` GATE-02
  identity, `cli_handlers.py` never touched (GATE-03). Verifier passed 9/9 must-haves. Disclosed
  non-blocking backlog item: `cli_handlers.py`'s `dev validate-family` Click Choice still lists
  retired `flash3`/`flash4` ids (left alone per GATE-03).

---

## v1.18 AM27C020 0x08 Write-Path RCA & Fix (Shipped: 2026-07-01)

**Phases completed:** 3 phases, 12 plans, 26 tasks

**Delivered:** Root-caused the AM27C020 `0x08` 0-bits-programmed fault (RC-1: DIP32 pin 31 modeled as address line A18, not held /PGM), shipped a scoped `DIP32_27C020` + `rw-pin:[31]` → `CTRL_READ_WRITE` (0x40) fix dual-repo lockstep, and bench-proved it **effective** (write#1 60/64 byte-exact, refuting the 0-bits signature) but **marginal/unreliable** (write#2 0/64). No byte-exact graduation → honest **DEFER**; AM27C020 carried forward as **FUT-08** (FUT-06 retired-by-replacement).

**Audit:** `tech_debt` — 11/11 requirements satisfied, 3/3 phases verified passed, cross-phase integration 6/6 WIRED, 0 broken flows. BENCH-01 satisfied via the documented deferral branch. Report: `.planning/milestones/v1.18-MILESTONE-AUDIT.md`.

**Release:** meta tagged `v1.18` + gsd planning merged to `beta`; lockstep beta cut + gitlink bump remain operator-gated (standing v1.11–v1.17 policy; gitlinks PINNED).

**Known deferred items at close:** 14 (all pre-existing cross-milestone carry-forwards, none from v1.18 Phases 97–99; see STATE.md → Accumulated Context → "Deferred Items — acknowledged at v1.18 milestone close").

**Key accomplishments:**

- No-hardware Wave-1 foundation for the AM27C020 `0x08` RCA: SAFE-01 confirmed non-invasively by file:line code-read (over-voltage ERROR path intact, host guard unbypassed), the v1.18 bench EVIDENCE record + 97-RCA-FINDINGS verdict skeleton stood up with never-fabricated TBD cells, held-rail proxy values 0x188/0x180 pinned against the live host `dev reg -f` bit map, and the four committed Wave-0 gate scripts asserted present/tracked/parse-clean.
- Operator-witnessed bench session (Leonardo + RURP Rev 2.0, fw 3.0.0b10 / bccd995) that captured the PRE-01 writability pre-flight and reproduced the RCA-01 0-bits-programmed failure on the seated AM27C020 — at a CORRECTED rig (VPP 13.0V, JP4 closed) so the 0-bits outcome is unambiguous — with exactly ONE irreversible program attempt, the chip left pristine, and SAFE-01 held throughout. A held-rail DMM tooling bug surfaced mid-session was root-caused (debug session), worked around (hold_rail.py), and the routing question it blocked was answered by code instead.
- Closed the RCA: the passing 0x07 Winbond W27C512 control wrote byte-exact in the same session (write 6.52s, verify 0.64s, readback SHA `d9471636…` matched) where the 0x08 AM27C020 programmed 0 bits — exonerating every shared axis. Combined with Plan 02's code-level H2-disproof (VPP IS routed to pin 1), the cause is named RC-1: socket pin 31 is modeled as address line A18 (DIP32_STD) rather than a held program-active PGM pin, so the chip gets VPP but never a program strobe. Classified host-pinout + firmware-algorithm; Phase-98 fix surfaces handed off. RC-1 CONFIRMED + RC-2 EXONERATED (D-03 exit bar met), RC-3/RC-4 not-pursued, RC-5 INDETERMINATE (no deferral).
- DIP32_27C020 scoped pinout (pin 31 off address bus) assigned to 88 ≤256K 0x08/32-pin chips via size-keyed build_db.py arm; diff_db PASS; host CI gate green (ruff+mypy+check_dispatch); upstream bus-config contract for Plan 02 firmware PGM-assert delivered
- Gated deliberate PGM=VIL hold-LOW in memory_set_data for 0x08 32-pin ≤256K (AM27C020), backed by TDD CODE-STRUCTURE tests (RC-98A/B/C); golden traces 0x07/0x0B/chip-id byte-identical; 0x08 trace unchanged (A5); full native suite 117/117 green
- Host half of the corrected CR-01 fix: DIP32_27C020 gains `rw-pin:[31]`, resolving pin 31 to `config.rw_line=22` so the firmware's existing rw_line mechanism drives CTRL_READ_WRITE (0x40) as the AM27C020's /PGM write strobe — plus WR-03/WR-05 hardening and the IN-02 host-side named constant.
- Reverted Plan 02's physically-inert `CTRL_ADDRESS_LINE_18` clear in `memory_set_data` and relies on the existing, revision-agnostic `rw_line` mechanism (fed by 98-03's `rw-pin:[31]` on `DIP32_27C020`) to hold pin 31 (/PGM = RW = `CTRL_READ_WRITE` physical 0x40) program-active LOW across the full write pulse — closing the CR-01 physical-no-op blocker with a native-test-provable, revision-agnostic fix.
- Closed all three INFO findings from 98-REVIEW.md: uint32_to_bytes now writes its four bytes to distinct indices (IN-01), the double-evaluation `min` macro is replaced with a single-evaluation inline function (IN-03), and the 262144-byte AM27C020 size boundary is now a named `MAX_27C020_SIZE` constant on both sides of the wire with a cross-repo pytest parity assertion (IN-02) — closing Phase 98's gap-closure work with the native suite and host CI both green.
- Extended check_ledger.py's D-09 PASS constraint to admit a v1.18-native 0x08 graduation (self-consistent write/read-back SHA) without fabricating a nonexistent v1.15 write baseline, while keeping the honesty guard and all 11 existing ledger rows green.
- Staged the deterministic AM27C020 write image, its annotated SHA256SUMS provenance header, and a Phase-99 anti-fabrication EVIDENCE gate (check_graduation.py) so the operator bench session (99-03) is a pure execute-and-record step.
- BENCH-01, BENCH-02
- Transcribed the 99-03 bench outcome (Phase-98 fix bench-effective-but-unreliable on AM27C020) into a new EVIDENCE.json phase99_deferral cell and a superseding FUT-08 ledger defect, both gates green with zero fabrication.

---

## v1.17 Implement & Test the W29C040 Programming Protocol (Shipped: 2026-06-29)

**Phases completed:** 3 phases, 8 plans, 18 tasks

**Key accomplishments:**

- FLAG_CAN_ERASE (0x02) IS set in W29C040 wire flags (T-93-CANERASE HIGH-severity), flash4_write_execute is VPP-free, Phase-74 traps ruled out by native evidence (11/11 tests PASSED), and the canonical 93-RCA-FINDINGS.md H1–H5 scaffold is ready for bench Plans 02–04
- W29C040 page-0 write fault reproduced N=2 deterministically (0x0000ff stays 0x00 after N=5 settled reads — H4 disconfirmed, page never committed)
- W29C040 §6.6 first-16K boot block programming lockout confirmed as the sole root cause: silicon-level hardware protection on this chip instance, not a firmware timing/addressing/SDP bug.
- W29C040 §6.6 first-16K boot-block programming lockout named as root cause (SILICON/chip-instance-specific state), firmware algorithm proven correct for unlocked pages, Phase-94 hand-off complete with T-93-CANERASE FIX-01 and lock-reversibility fork
- Defense-in-depth removal of the FLAG_CAN_ERASE 12V-on-5V hazard for protocol 0x05 flash4 chips: host flag derivation gated on algorithm!=5, firmware guard keyed on handle->protocol==0x05, dual-repo lockstep.
- Datasheet-sourced per-chip page_size carried over the wire (page-size JSON field) with emit-when-present host emission, json_parser.c struct population, and flash4 safe-fallback consumption — W29C040=256 / W29C020=128 cited only
- W29C040 §6.6 boot-block lockout diagnosed host-side (heuristic hint) and firmware-side (DETECT read); MSG_ERR_FL4_BOOT_BLOCK_LOCKED 0xBC added via codegen; golden write trace confirmed unchanged
- py3.11 CI all-green (703 tests, 78.35% coverage) + 3-run SHA-match bench proof on W29C040 writable region (0x4000+) with no 12V, proving FIX-01a

---

## v1.16 Protocol-First Architecture Rebuild (Shipped: 2026-06-26)

**Phases completed:** 8 phases (85–92; Phase 92 a host-only follow-on with no separate phase dir), 29 plans, 39 tasks

**Key accomplishments:**

- v1.16 branch forked from beta + `datasheets-check.sh` Wave-0 gate authored enforcing 12-bucket %PDF contract (correctly RED until Plans 02/03 populate the tree)
- 17 protocol datasheets committed to firestarter sub-repo: 11 on-hand chip PDFs across 6 buckets (DSHEET-01) + 6 no-silicon representative PDFs (DSHEET-02); 3 exact-leaf fallbacks documented for Plan 03 provenance
- datasheets/README.md authored (DSHEET-03): 12-bucket index with D-08 provenance, 6 exclusions named, D-02/D-03 policy documented; datasheets-check.sh exits 0 (PASS)
- VAR-01 variant-field decode documented in full (low byte = pinout discriminator, high byte = minipro `algo_number` per `database.c#L1918`, NOT a classifier) with pinned SHA `a8efaedc`, plus the refactor-under-test oracle (FM1608 GREEN / X88C64 RED / 10-chip EVIDENCE wire-stability GREEN) that Plan 02's classifier rewrite must satisfy.
- Replaced the build_db.py Rule 1 / Rule 2 (WARNING-5) / Rule 3 override stack and the two-pass `_etype` derivation with one principled `classify(type,proto,pm_idx,flags,pinout,mem_size)` keyed on minipro's own classification fields; regenerated chip_database.json (744 chips) so FM1608 (0x28/FRAM) and X88C64 (EEPROM) fall out of the general decode; extended diff_db.py with a cited VARIANT_DECODE label that fully explains the regen diff vs the OLD baseline; and proved check_dispatch.py 0 violations + EVIDENCE-11 wire-stability (zero chips moved).
- Re-pinned both diff_db baselines (`chip_database.baseline.json` byte-identical + `dispatch_baseline.json` regenerated) to the classify()-corrected 746-chip DB including the 2516/2532 non-upstream supplement — strictly LAST after the Plan-02 + Plan-04 diff was reviewed PASS-all (D-07 / RESEARCH Pitfall 4) — turning diff_db.py into an empty identity diff and proving the full Phase 86 gate green against the CI py3.11 target (686 tests, 77.69% coverage, ruff/format/mypy-watermark all clean, check_dispatch 0 violations).
- Shipped the two upstream-absent 24-pin oddballs (2516, 2532) first-class in `chip_database.json` via a curated, provenance-cited non-upstream supplement (`tools/extra_chips.json`) that `build_db.py` merges AFTER the infoic.xml decode loop (VAR-05 / D-10); proved the supplement rows pass the same gates as decoded chips — `check_dispatch.py` 0 violations and `diff_db.py` explains them as cited non-upstream-supplement rows (exit 0) — and pinned 2516's SAFE-04 UNVERIFIED status with its v1.15 wire values unmoved.
- Protocol vocabulary doc (`firestarter/doc/PROTOCOLS.md`) with 12-bucket NAME-01 facets, datasheet citations, FM1608/X88C64 NAME-04 corrections, Honest non-protocols section, and INV-01..09 traceability matrix with per-INV suite paths — plus pre-phase Leonardo flash baseline capture (25654 bytes).
- Nine live Unity assertions across 4 native test suites complete the SAFE-02 doc+handler+test traceability contract for every firmware behavioral invariant
- All four hard frozen-world gates pass — check_dispatch 0 violations, diff_db empty, flash delta 0 bytes vs 25654 baseline, all 9 INV ids greppable in >=3 files, host repo byte-frozen
- Shared assert_trace_eq() helper + four byte-exact (reg,data) golden fixtures for eprom 0x07/0x08/0x0B write and chip-id (P4) paths, all 16 suite tests green
- Byte-exact golden register traces for eeprom28c 0x0D (SDP unlock P7 + DQ7 poll P5 + A9 chip-id P4) and flash_intel 0x10 (VPP-gate P3 + command-register P4), all 10 suite tests green
- Byte-exact golden register traces pinned for flash3 0x06 write and flash4 0x05 write + chip-id; all suite tests (6 + 11) pass with INV-04 and INV-09 intact
- Host pytest binding PROTOCOLS.md §0 doc-parse ↔ check_dispatch.dispatch() ↔ firmware test_configure_memory.cpp for all 12 dispatch table entries, ruff-clean for CI py3.11
- All frozen-world gates PASS and SC#4 safety posture confirmed present + unmodified after golden-trace (88-01/02/03) and dispatch-mirror (88-04) work landed — 0-byte flash delta, 0 DB changes, over-voltage check intact at known lines, resolve_chip guard intact, 2516 UNVERIFIED
- Stdlib-only ledger gate with pytest-proven 0/1/2 exit-code contract enforcing LEDGER-01 join keys, D-04 no-copy SHA guard, LEDGER-02/D-09 PASS structural constraint, and LEDGER-03 UNVERIFIED/defect-status rules.
- 12-bucket PROTOCOL-LEDGER.{json,md} authored with cross-reference-only composition (D-04), 4 bench-pending rows, 6 UNVERIFIED rows, 3 verbatim open-defect carries — check_ledger.py exits 0
- Verified firmware vpp_check_window +500 mV over-voltage gate (primitives.cpp:106) and host resolve_chip support-status guard (chip_resolver.py:55) present and unmodified on firmware a296195, with 2516 UNVERIFIED and all frozen-world gates green.
- **Phase 90 bench (Leonardo + RURP Rev 2.0):** all 4 on-hand reads byte-identical to v1.15; 0x05 W29C020 + 0x28 FM1608 PASS immediately; 0x06 SST39SF040 + 0x07 W27C512 write-cycles recorded FAIL-INVESTIGATE (not auto-passed, per D-03) and spun out to Phase 91 RCA rather than blocking the close. UAT 5/5; ledger checker + SAFE-04 + frozen-world all green.
- **Phase 91 RCA — verdict: NOT a 12V-VPP nor a code regression, a TEST-METHOD error.** `firestarter write -b` set `FLAG_SKIP_ERASE`; flash3 (SST39SF040, NOR) + EEPROM-class W27C512 require erase-before-write, so `-b` left un-erased bits unprogrammable. Controlled A/B proved b10 (`a1953c2`) fails identically to the recompose (`a296195`) → **recompose innocent** (diff comment-only; DB wire params byte-identical). FIX = plain erase-enabled `firestarter write`: SST39SF040 write+verify == v1.15 `a38b13b4` (N=3, 1 SHA) and W27C512 (operator returned, chip-ID 0xDA08, erase = `e16b2a5b`) both **graduated to PASS** — no firmware/host code edit; SAFE-04 intact. **LEDGER-02 FULLY satisfied — all 4 on-hand protocols PASS (0x05/0x06/0x07/0x28).**
- **Phase 92 (HARD-01) — footgun eliminated at its source:** decoupled `write -b`/`--no-blank-check` from skip-erase in the host (`firestarter_app`) — `-b` now skips ONLY the blank check while the pre-write erase still runs for `FLAG_CAN_ERASE` chips, so `write -b` on a non-blank flash/EEPROM Just Works; new explicit `--skip-erase` opt-in (with hardware-damage warning) preserves the pre-erased/non-erasable case. Host-only; firmware byte-identical. ruff + format + mypy + full pytest (78.19% cov, 29 snapshots) green + new decouple regression test; bench-confirmed on the seated W27C512.

**Git range:** `0c2dc7b` (Phase 85 context) → `a859233` (Phase 92 HARD-01); 88 meta commits on `gsd/v1.16-protocol-first-architecture-rebuild`. Sub-repos on `v1.16-protocol-first-architecture-rebuild`: fw `a296195` (Phase 89 primitive recompose — final 25136 B / 87.7% / −518 B vs the 25654 B baseline) / app `883c78f` (Phase 92 decouple). Gitlinks remain **PINNED at b10** (fw `a1953c2` / app `98b3a92`). Timeline: 2026-06-25 → 2026-06-26 (2 days).

**Outcome:** 28 requirements all Complete (DSHEET ×3, VAR ×5, NAME ×5, PRIM ×6, LEDGER ×3, SAFE ×6, HARD-01). Turned the inherited-from-minipro hex-ID protocol buckets into a named, datasheet-verified, primitive-decomposed architecture: `infoic.xml`'s `variant` field decoded in full and `build_db.py` rewritten to a single principled `classify()` (Rule 1/2/3 override stack deleted; FM1608→SRAM_STD 0x28 + X88C64→EEPROM now fall out structurally; DB 744→746 with the 2516/2532 non-upstream supplement); top-level `datasheets/` + `firestarter/doc/PROTOCOLS.md` 12-bucket vocabulary + INV-01..09 native-test traceability matrix; primitives P7/P4/P3/P5 extracted behind golden traces + dispatch-mirror guard with a net flash **decrease** (−518 B); `PROTOCOL-LEDGER.{md,json}` + self-consistency checker with all 4 on-hand protocols PASS and 6 no-silicon buckets explicit UNVERIFIED. The Phase-90/91 "regression" scare resolved as a test-method error (recompose proven innocent) and the underlying footgun hardened away in Phase 92. Host-first, NO dual-repo lockstep (wire/constant values unchanged).

**Known deferred items at close:** 14 open artifact items acknowledged & deferred (see STATE.md "Deferred Items") — 12 are pre-existing carry-forwards from prior milestones (Phase 08/09/71/84 verifications, `firmware-vpp-misread` + `fm1608-fresh-chip-baseline` debug sessions, 5 hardware/firmware todos incl. flash4 page-size CR-01); the 2 v1.16-born items (Phase 85 HUMAN-UAT 2 pending scenarios + 85-VERIFICATION human_needed) are operator datasheet-confirmation gates on a zero-code-risk acquisition phase. Operator chose Acknowledge & close.

**Release state:** Meta tagged `v1.16`; gsd planning to be merged to meta `beta` per standing policy. Lockstep beta cut (`3.0.0b11`) + submodule gitlink bump remain OPERATOR-GATED (gitlinks PINNED at b10), per standing v1.11–v1.15 policy.

---

## v1.15 Bench Validation of Operator Inventory (Shipped: 2026-06-25)

**Phases completed:** 4 phases, 15 plans, 22 tasks

**Key accomplishments:**

- Fresh adversarial re-audit of the FLAG_CAN_ERASE decode chain for Flash/EEPROM (W29C040 / 0x05) confirmed SOUND; pinned by new test `test_convert_w29c040_flash_eeprom_flag_can_erase`; 651 tests green.
- Hand-authored the irreplaceable Intel 2516 user-override DB entry (absent from minipro), captured a full SR-1 safety review verifying all 6 D-02 values against the TMS2516 datasheet, obtained the operator's blocking-human sign-off, and scaffolded the milestone EVIDENCE record with 11 pending chip rows.
- Read + blank-checked all 11 physical chips on Leonardo + Rev 2.0 with zero chips consumed (reads apply no VPP); 10 PASS with N≥3 byte-identical SHAs, the 3 UV gating blank-states recorded, and the irreplaceable 2516 flagged ANOMALY (0x0B read path unstable) — gating Phase 83.
- Deterministic full-size PRNG image generator (random.Random seed), 12 pinning tests, SAFE-02 green (663 tests + 0xA4 guard), and Phase 82 write-column schema added to EVIDENCE without dropping any Phase 81 row
- Established the SAFE-02 software gate (663-test host suite + 0xA4 `ack_data=False` guard + CI-scoped ruff all green) and generated the two deterministic UV write payloads (ST M27C512 64KB pseudo-random image + AM27C020 256KB all-0x00) with recorded reproducible SHA-256 oracles, then scaffolded the Phase 83 EVIDENCE.md section scoping the work to the 2 read-stable UV chips and recording the 2516→Phase 84 deferral — all with zero source/firmware/dependency changes (EVID-02 reuse-first).
- Bench-proved the WRITE PATH of the read-stable BLANK UV-EPROM ST M27C512 on Leonardo + Rev 2.0. After re-confirming the BLANK state non-destructively (no VPP) and obtaining the operator's irreversible spend authorization, executed an operator-directed **minimal 16-byte partial-spend** (deviation from the plan's D-05 full-image): write 16 B @0x0000 (RC=0), `verify -a` of those bytes (RC=0), full-chip read-back showing first 16 B = payload / rest 0xFF, N=3 byte-identical reads (1 distinct SHA), and a wrong-file negative control (RC=1). Verdict **PASS**; the part remains mostly blank/reusable.
- Bench-tested the AM27C020 (0x08, NOT-BLANK, DIP32) write path on Leonardo + Rev 2.0. After re-confirming NOT-BLANK non-destructively and obtaining operator spend authorization (a minimal 16-byte 0x00 partial-spend, deviation from D-06), the `write` deterministically failed — `bad bytes 15/16`, **zero bits programmed**, chip data intact — across the initial attempt + 2 retries (incl. operator closing JP4), plus a mild intermittent read glitch. Operator classified it **ANOMALY** (0x08 write/VPP path on this bench, not silicon wear), flagged Phase 84 FIX-01, phase not halted (D-14). Then recorded the GRAD-03 / 2516 → Phase 84 handoff across EVIDENCE + REQUIREMENTS + ROADMAP.
- Operation-type-keyed VPP-skip in `eprom_generic_init` — CMD_READ/CMD_BLANK_CHECK skip `eprom_check_vpp` entirely (clears chip-1 18.8V read refusal + benign low warnings); write/erase/chip-id still gate VPP; proven by 5-assertion native dispatch test (2 positive + 3 negative).
- Host SRAM/FRAM blank-check short-circuit in `check_eprom_blank()` via `_SRAM_PROTO_IDS` frozenset, preventing firmware 0xA4 MSG_ERR_EMPTY_INPUT for FM1608 and all SRAM families.
- Consolidated 11-chip decode-correctness audit (SC#1) in `.planning/milestones/v1.15-artifacts/DECODE-AUDIT.md` with per-attribute CONFIRMED/MISMATCH verdicts cross-referencing EVIDENCE; REWR-01/02/04 traceability annotated with silicon FAIL/deferral dispositions; UV-01..04 checkbox drift confirmed already corrected (D-41).
- VPP-skip re-flash proven (89.5% flash, 18.8V boot-refusal cleared); 2516 read still unstable (N=3, 3 distinct SHAs, 1.9% byte jitter) — GRAD-03/FUT-03 DEFERRED; AM27C020 0x08 takes 0 bits (FUT-06); W29C040 flash4 256B-page fault reconfirmed (Phase-74 fix not silicon-effective, reopen CR-01)
- DECODE-AUDIT.md finalized (SC#1 complete); FIX-01 closed per D-43 with in-posture fixes + named deferrals; GRAD-03/FUT-03 explicitly deferred best-effort (D-22); SC#3 full software gate GREEN — milestone ready for `/gsd-verify-work`

**Git range:** `afceb01` (v1.15 start) → `827e87f` (Phase 84 SECURED); 72 meta commits on `gsd/v1.15-bench-validation-of-operator-inventory`. Sub-repos: fw `cb947c7` (VPP-skip) / app `4d5b3de`, both on `v1.15-bench-validation-of-operator-inventory` (gitlinks PINNED). Timeline: 2026-06-23 → 2026-06-25 (3 days).

**Outcome:** 23 reqs — 21 satisfied, GRAD-03 deferred best-effort (D-22; 2516 0x0B read instability → FUT-03), FIX-01 closed-by-disposition (D-43; in-posture fixes shipped + bench-confirmed, deeper write-path defects RCA'd + named-tracked → FUT-06 AM27C020 0x08, CR-01/Phase-74 Wave-2 W29C040 flash4). First Flash/EEPROM auto-erase silicon proof (W29C020). Genuine silicon FAILs (W27E512/W27E040 stuck bits) faithfully recorded — not DB/algo faults. Milestone audit `gaps_found` is stale (predates Phase 84); both gaps closed-by-disposition + operator-accepted. 3/4 phases Nyquist-compliant; Phase 84 SECURED (threats_open:0).

**Known deferred items at close:** 12 open artifact items acknowledged & deferred (see STATE.md "Deferred Items") — all pre-existing carry-forwards or intentional v1.15 deferrals; operator chose Acknowledge & close.

**Release state:** Meta tagged `v1.15`; gsd planning merged to meta `beta`. Lockstep beta cut (`3.0.0b11`) + submodule gitlink bump remain OPERATOR-GATED (gitlinks PINNED), per standing v1.11–v1.14 policy.

---

## v1.14 Feasible-Gap Implementation (Shipped: 2026-06-23)

**Phases completed:** 4 phases (77–80), 9 executed plans of 13 (4 deferred plans are hardware-gated), 14 tasks. Host-only delta (firmware sub-repo untouched, stayed on `beta`). Git range: `d42fed3` (v1.14 start) → `3882377` (rail correction); 55 meta commits + 5 host code commits (Phase 77 ×3, Phase 79 ×2) on `firestarter_app@26cc62d`. Timeline: 2026-06-18 → 2026-06-23 (5 days).

**Delivered:** The first milestone since v1.0 where chips actually **graduate to `supported`**, implementing the four evidence-surfaced, RURP-feasible gaps v1.13 scoped out. Of the four: **1 fully landed + bench-proven** (erase write-path), **1 landed software-side best-effort** (25V NMOS), **2 cleanly deferred on genuine hardware blockers** (X88C64 PCB-block, AT28C04/16 adapter-not-built) — every deferral FUT-tracked. The cross-cutting SAFE-01/02/03 graduation-gate-last discipline (drop the host-guard refusal only after native + wire + bench evidence; `check_dispatch.py` full-DB VPP-safety gate green; lockstep constant parity) was established in Phase 77 and held across the milestone. Audit `gaps_found` but **all gaps are intentional, operator-authorized, hardware-gated deferrals, not execution failures**; integration PASS (744-chip dispatch gate, 0 violations; 650 host tests; constants parity 8/8).

**Key accomplishments:**

- **Phase 77 (Erase write-path) — ERASE-01/02, SAFE-01/02/03, ✅ verified 5/5:** `convert_to_programmer` derives `FLAG_CAN_ERASE` from the canonical `electrical.type == "EEPROM"` (not the always-zero `info-flags & 0x10`), locked by 3 wire-level tests, so the 7–8 0x07 EE-EPROMs (W27C512-class) auto-erase before programming. A host regression test pins the `ack_data=False` invariant (INIT/END DATA frames not acked) so the default write path can't re-trigger the 0xA4 desync. **First hardware graduation:** the full write→auto-erase→program→verify cycle is bench-proven on a real non-blank W27C512 on the Leonardo (clean no-`-b` write, independent read SHA-match, wrong-file verify exits non-zero).
- **Phase 78 (X88C64 0x34) — XIC-01 ✓, ✅ verified 7/7 (clean deferral):** source-traced the RURP control-register allocation + 74HC573 strobe; the A6 ALE-routing verdict is **PCB-BLOCKED (HIGH confidence)** — the control register is fully allocated and no free strobe exists. The contingent handler-write plan correctly took the DEFER branch — **zero firmware code**; X88C64 stays `protocol-not-implemented`/host-refused; graduation deferred to FUT-01. "No blind handler."
- **Phase 79 (25V NMOS ceiling raise) — NMOS-02 ✅ (best-effort, D-07):** under the operator override (no hardware change, ever; the strict ≥25V pre-gate retired), raised the host VPP ceiling 22000→25000 in lockstep (`build_db.py` + `check_dispatch.py`) and regenerated `chip_database.json` so the 4 NMOS UV-EPROMs (INTEL M2716, INTEL 2732/M2732, SGS-THOMSON ETC2716, ST ETC2716) graduate `vpp-exceeds-max` → `supported` (0x0B, vpp_mv=25000); zero `vpp-exceeds-max` chips remain; M2732A (21V) untouched. The chips program on the existing 0x0B direct-VPE rail (22.4V DMM / 23.9V fw, ~90% of 25V) where the firmware warns-and-proceeds on under-voltage (over-voltage stays blocked). Rail correction (operator): the ~15–19V earlier mislogged as VPE was actually VPP.
- **Phase 80 (AT28C04/16 adapter) — ADPT-01 evaluated NOT CLEARED (clean deferral):** the gating DIP24→DIP32 adapter is not built and no AT28C04/AT28C16 chip is on hand. Per the operator decision the phase deferred cleanly — **zero DB/code/constants change**, the 9 AT28C chips stay honestly `adapter-required`, the v1.12 host-guard refusal preserved; Plans 02/03/04 blocked; FUT-04 recorded.

**Hardware-gated deferrals (FUT-tracked, carried forward):**

- **FUT-01** — X88C64 graduation if the ALE PCB-block is later resolved by a shield modification (Phase 78; XIC-02/03/04).
- **FUT-03** — Definitive Leonardo write+verify SHA-match bench proof of the 4 graduated NMOS chips on the ~22.4V VPE rail; demoted to informational best-effort (chips stay `supported` without it); deferred for lack of an NMOS chip on hand (Phase 79; NMOS-03).
- **FUT-04** — AT28C04/16 graduation once the DIP24→DIP32 adapter is built + DMM-verified (/WE pin 21→30) and an AT28C chip is on hand (Phase 80; ADPT-01/02/03).

**Branch/release state:** v1.14 forked off the gsd/v1.13 close tip (`f486ad4`) in the meta repo; sub-repo work on `v1.14-feasible-gap-implementation` (`firestarter_app` only — firmware untouched). Meta tagged `v1.14`; gsd planning merged to meta `beta`. **The lockstep beta cut (`3.0.0b11`) + submodule gitlink bump remain operator-gated** (gitlinks intentionally PINNED) — same standing policy as v1.11/v1.12/v1.13.

See `.planning/milestones/v1.14-ROADMAP.md`, `.planning/milestones/v1.14-REQUIREMENTS.md`, `.planning/milestones/v1.14-MILESTONE-AUDIT.md`.

---

## v1.13 Programming Algorithm Validation + Gap Implementation (Shipped: 2026-06-18)

**Phases completed:** 5 phases, 19 plans, 31 tasks (Phase 75 erase path + Phase 74 Wave-2 HW re-bench deferred to v1.14)

**Delivered:** Three-tier software-first validation harness + per-family matrix proving the 6 write/program/verify families correct (Tier-3 HIL on Leonardo, PARTIAL bench coverage); evidence-driven feasible-gap subset (flash4 `CMD_CHECK_CHIP_ID` + W29C040 SDP/page-write fix; spec-only AT28C04/16 adapter-required arm + DIP24→DIP32 adapter pin-map; X88C64 0x34 MEDIUM feasibility verdict). Dual-repo lockstep merged to `beta` (fw `a33513f` / app `34deccb` @ `3.0.0b9`, no tag — beta cut + stable operator-gated).

**Known deferred items at close:** 9 (see STATE.md Deferred Items) — all pre-existing or accepted tech debt; none v1.13 blockers.

**Key accomplishments:**

- Define-guarded `HOST_STUBS_RECORD_BUS` opt-IN recording buffer in `host_stubs_common.inc`: four extern-C API symbols, 256-entry bound-checked array, byte-identical no-op fallback for all existing native suites.
- Authored JSON matrix spec (D-01) + deterministic codegen script emit
- Per-family VPP range invariants in check_dispatch.py with flash_intel DB enforcement + synthetic-fixture-proven non_supported_dispatchable population, closing v1.12 CR-01 hollow-GATE-03 tech debt.
- test_val_eprom
- Six pytest wire round-trip suites prove each family's rep chip (from the
- `dev validate-family` Tier-3 runner composes cycle methods,
- Replaced the vacuous source==source SHA self-compare in `dev_validate_family` verdict_int==0 branch with a direct board-class verdict mapping (`pass_type` = authoritative/advisory), proven non-vacuous by a distinct-hash mismatch test.
- Trimmed flash4 host matrix to protocols=[5] (CR-02 resolution), regenerated 11-row header byte-identically (drift gate green), documented firmware/native vs host-matrix distinction durably, marked HARN-04 Complete.
- 14-row per-protocol feasibility verdict table committed, with v1.12 overstated-claim review (3 items) and both open questions resolved by code trace to file:line
- v1.13 protocol re-enumeration artifact confirmed complete: 5-item gap index + anti-feature block (0x11/0x2A/0x2B/0x2C + 25V NMOS) + 22V ceiling constraint, all internally consistent and cited — RSCH-01 closed
- Confirmed all six families Tier-1/Tier-2 GREEN (28+26 tests), armed the R1 precondition gate (r1=270000 persisted to local config), and emitted three explicit SKIP-deferred Tier-3 matrix cells for the chipless families (eeprom28c/flash4/flash_intel).
- W27C512 (electrically-erasable EEPROM, 12V VPP, configure_eprom 0x07) achieves authoritative Tier-3 PASS on Leonardo/Rev 2.0 — write_cycle_eprom erase+write+readback SHA match confirmed, negative control oracle proven non-vacuous (wrong-file verify exits 1)
- flash3/VAL-03 recorded as SKIP-deferred (no AM29F040 on hand per operator 2026-06-17); flash4/VAL-04 upgraded from SKIP-deferred to real FAIL verdict on seated W29C040 (Winbond flash4, algorithm 5) with passing negative control and Phase-74 escalation
- FM1608 FRAM two-pattern N=2 bench confirms VAL-06 = table-stakes-PASS: configure_sram writes via generic_memory_write_execute with zero mismatches across 0x5A/0xA5 patterns on both runs — FIX-01 closed not-needed with evidence
- FIX-01 closed not-needed via VAL-06 bench evidence (configure_sram persists data); FIX-03 comment-reconciled across firmware CLAUDE.md and host database.py/ic_layout.py with consistent 0-DB-chip phantom framing for 0x35 and 0x39.
- Flash4 CMD_CHECK_CHIP_ID dispatch mirror + W29C040 SDP/page-write fix, proven VPP-safe by recording-stub tests; flash budget mitigated to 89.5% via shared AMD chip-ID util.
- Named `_AT28C_DIP24_NAMES` rule arm in build_db.py classifies 14 AT28C04/AT28C16 aliases as adapter-required with explicit adapter-spec reference, plus X88C64P reason reworded to datasheet-accurate 8051 multiplexed-bus description.
- DIP24→DIP32 adapter pin-map spec (two-layer, verified against pinouts.json) + X88C64P 8051-multiplexed-bus feasibility verdict (MEDIUM; STORE/RECALL corrected; NO handler committed)

---

## v1.12 Firmware Protocol Dispatch Hardening + Skeletons (Shipped: 2026-06-16)

**Phases:** 8 delivering (62, 63, 64, 65, 66, 67.1, 69, 70) | **Plans:** 22 | **Timeline:** 2026-06-10 → 2026-06-16 (7 days) | **Ship:** Dual-repo lockstep (first firmware-touching milestone since v1.10); both sub-repos merged to `beta` (fw `b71c6fd` / app `6b5480f`), **no tag** — lockstep beta cut + stable promotion operator-gated. | **Audit:** tech_debt — 17/17 requirements satisfied, 8/8 phases passed, 5/5 E2E flows wired, security closed on every secure-gated phase (66/67.1/69/70, threats_open: 0) (`.planning/milestones/v1.12-MILESTONE-AUDIT.md`). | **Known deferred items at close:** 7 (carried from the v1.11 close — pre-existing / out-of-scope / v1.9-gated; none v1.12 work; see STATE.md Deferred Items).

**Delivered (17/17 requirements):** Made the whole stack honest about what it can and cannot program. Firmware now fail-closes: any non-zero unimplemented `protocol` returns an explicit `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED` (0xBB) with zero hardware side effects instead of silently falling through the `mem_type` chain to `configure_eprom` (the 12V-VPP-on-a-5V-part hazard). The host raises a typed `ProtocolNotImplementedError` and prints an actionable message. The database now *lists* (not silently drops) DIP parallel chips RURP can't fully support, tagged with a `support_status` taxonomy (`protocol-not-implemented` / `adapter-required` / `vpp-exceeds-max`); the host reports the status via `info` and refuses `write`/`read`/`verify` in-host before any serial byte. No new chip became programmable — framework + honest reporting only. DB grew 743 → 744 chips. The v1.12 branch (forked off the pre-v1.11 beta) was re-ported onto v1.11's `resolve_pinout_key` architecture and merged to `beta` dual-repo lockstep.

**Key accomplishments:**

1. **Phase 62 — Dispatch baseline + check_dispatch (GATE-01/02).** Pinned the pre-change 743-chip dispatch triples to `dispatch_baseline.json`; reconciled the 0x35/0x39 dispatch-mirror gap and added the `protocol != 0` not_implemented arm + FAIL bucket to `check_dispatch.py` before any firmware touched.
2. **Phase 63 — Catalog lockstep wire change (WIRE-01).** Added `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB` to canonical `messages.toml`, regenerated `messages.h` + `messages.py` under py3.11; drift gates green in both repos; zero call sites (reviewable in isolation).
3. **Phase 64 — Firmware fail-closed dispatch + native tests (DISP-01..04, WIRE-02, TEST-01/02).** `configure_not_implemented()` (NULL op pointers, no VPP enable) + `protocol != 0` guard before the legacy `protocol == 0` fallback + named arms for 0x11/0x2A/0x2B/0x2C; 49/49 native Unity tests; Uno 72.4% flash.
4. **Phase 65 — Host graceful handling (HOST-01/02).** `ProtocolNotImplementedError(EpromOperationError)`; centralized id-0xBB typed-raise in the state-machine ERROR path; subclass-first arm in `map_typed_errors`. Gap-closure 65-02 wired the probe/connect boundary (Option B) so the 0xBB frame reaches the CLI instead of being masked as `ProgrammerNotFoundError`.
5. **Phase 66 — DB inclusion + VPP correction + dispatch gate (DB-01/03/05; SECURED).** `build_db.py` includes unknown-protocol DIP chips as `protocol-not-implemented`; true NMOS VPP (M2716/M2732=25V → vpp-exceeds-max, M2732A=21V → supported); `RURP_VPP_CEILING_MV=22000`; `support_status` on every chip (DB 744). 66-05 pulled the host-refusal guard forward (`ChipNotImplementedError` in `resolve_chip`) — the authoritative 12V-VPP-hazard closure.
6. **Phase 67.1 — DB-02 pinout + DB-04 capability (SECURED).** Closed the first-audit gaps (consolidating the never-run 67 & 68): 14 SRAM chips corrected to RURP pinouts via extended `resolve_pinout_key` rules; `info` shows a status-specific support line; chip-ops refuse with the DB reason string verbatim; per-status CLI matrix. Verified PASSED 9/9.
7. **Phase 69 — CLI command-surface robustness audit (SECURED).** Root-fixed the live `info` `TypeError` (list-valued pin fields vs `<= pin_count` in `ic_layout.py`); smoke-audited every CLI command for crash-free execution; pinned each surface with regression tests including all three non-supported statuses.
8. **Phase 70 — v1.11+v1.12 DB-pipeline integration for beta merge (verified 6/6; SECURED).** Resolved the architecture collision (v1.12 forked off pre-v1.11 beta): re-ported v1.12's `support_status`/VPP-safety features onto v1.11's `resolve_pinout_key`, regenerated the DB, validated via GATE-03 + diff_db; merged both sub-repos to `beta` lockstep (fw fast-forward `b71c6fd`, app `6b5480f`), no tag.

**Technical debt accepted at close (operator 2026-06-16):** GATE-03 `non_supported_dispatchable` detector in `check_dispatch.py` is hollow (declared, asserted empty, never populated) — the host guard (`chip_resolver.resolve_chip`) is the authoritative safety layer, so there is no live hazard. Plus latent WR-01 (Site B 0x00 re-promoted to 0x0D for adapter-required chips; electrically safe) and Nyquist validation gaps on 6/8 phases (behavioral coverage holds via VERIFICATION.md + integration check). See the milestone audit and v1.12-ROADMAP archive.

---

## v1.11 Complete infoic.xml Decode & Database Correctness (Shipped: 2026-06-10)

**Phases:** 6 (56–61) | **Plans:** 14 | **Timeline:** 2026-06-08 → 2026-06-10 (3 days) | **Ship:** HOST-ONLY (`firestarter_app`; firmware untouched like v1.8); beta-only — lockstep `3.0.0b9` cut + stable promotion operator-gated. | **Audit:** PASSED — 15/15 requirements, 5/5 E2E flows, both correctness gates green on 743 chips, 559 tests (`.planning/milestones/v1.11-MILESTONE-AUDIT.md`). | **Known deferred items at close:** 7 (pre-existing / out-of-scope / v1.9-gated; see STATE.md Deferred Items).

**Delivered (15/15 requirements):** Authoritatively decoded every Firestarter-relevant `infoic.xml` field grounded in minipro C source, rebuilt the `build_db.py` decode, unblocked the 9 blocked 24-pin EEPROMs host-only, and extended the corrected decode to the operator-facing display — all behind a full-class VPP-safety gate + per-chip diff gate. DB grew 734 → 743 chips. Research overturned the original "expand types + add firmware handlers" framing: the hardware-feasible memory set was already covered, so this shipped as a host-only decode-correctness + authoritative-docs milestone.

**Key accomplishments:**

1. **Phase 56 — Field dictionary + corrected docs (DEC-01/03/04/05, DOC-01/02/03, GATE-01).** Authoritative 288-line source-cited `infoic-field-dictionary.md` (13 attributes, CONFIRMED/INFERRED/UNKNOWN); rewrote `protocol-id.md`/`protocol-flags.md`/`package-details.md` fresh (canonical `IC2_ALG_*` names, 0x39 phantom fixed, bit-4 = `MP_ERASE_MASK`, bits 3/6/7 UNKNOWN). GATE-01 anchored via committed `chip_database.baseline.json` (operator-authorized D-01/D-02 live-fetch deviation).
2. **Phase 57 — Decode bug fixes + check_dispatch extension (DEC-02..05, GATE-03).** Fixed all 4 confirmed bugs in `build_db.py` (`interpret_timing` ×100 → µs; `VCC_VOLTAGES` 0x02=4V/0x03=4.5V; vcc/vdd label swap; `PROTOCOL_MAP` canonicalized, 0x35/0x39/0x3C removed). Extended `check_dispatch.py` to a full-class VPP-safety guard keyed on `electrical.type` (CR-01 — the algorithm predicate was dead code). `firestarter info W27C512` → 100 µs (not 10000).
3. **Phase 58 — Pinout re-derivation + 24-pin EEPROM unblock (PIN-01/02/03).** Deleted the `PIN_MAP_*`/`DIP28_VARIANT_MAP` guess tables; `resolve_pinout_key` rebuilt as a pure function of `(pin_count, proto_id, mem_size)`; 3 load-bearing safety overrides preserved as explicit rules; 9 × AT28C04/16 EEPROMs exposed via `DIP24_2816` + `0x0D` with a two-layer SR-1 safety review. 30 RED→GREEN Wave-0 tests; GATE-03 0 violations on 743 chips.
4. **Phase 59 — Correctness gate + per-chip diff + SRAM audit (GATE-02, GATE-04).** `diff_db.py` classifies every changed chip by root-cause rule vs the pinned baseline with minipro `a8efaedc` citations (a CR-01 BLOCKER — non-unique `part_number` index silently dropping ~69 records — caught and fixed in `f3b2ed7`); `sort_keys` byte-identity proved; `configure_sram` NVRAM/WP#/RTC behavior documented in two lockstep doc layers, no firmware escalation.
5. **Phase 60 — Display-layer decode correctness (`info`).** `firestarter info` derives Type/erasability/VPP from `electrical.type` ground truth: W27C512/SST27VF512/etc. show EEPROM + electrically erasable + 12V VPP; genuine UV-EPROMs (2764/M27C512/27C256) unchanged. 539 tests green; EEPROM snapshot canary added.
6. **Phase 61 — List/search display correctness + table layout.** Routed `firestarter list`/search Type+VPP through a single shared `resolve_type_label` helper (D-04) sourced from `electrical.type`, resolving the info-vs-list divergence and the spurious SRAM VPP (D-03); Name column clamped to [13,20], VPP fixed at 5; parametrized list-vs-info parity test. Code-review fix cycle landed WR-01 (Type clamp) + WR-02 (vpp_str parity).
7. **Post-close FM1608 follow-up (operator-driven).** SRAM/FRAM `vcc`→`vdd` (5V) normalization in `build_db.py` (24 entries — minipro's lower test-rail misrepresented the supply the RURP shield actually applies); `info` no longer renders a zero pulse-delay row; chip-ID shows `-` for absent/placeholder IDs. 560 tests; GATE green.

ROADMAP archived: `.planning/milestones/v1.11-ROADMAP.md` · Requirements: `.planning/milestones/v1.11-REQUIREMENTS.md` · Audit: `.planning/milestones/v1.11-MILESTONE-AUDIT.md`.

---

## v1.10 Serial Transport Hardening (COBS) (Shipped: 2026-06-07)

**Phases:** 7 (numbered 49–53, plus inserted 54 & 55; 45–48 reserved for the deferred v1.9 RCA) | **Plans:** 27 | **Tasks:** 36 | **Timeline:** 2026-06-01 (Phase 49 context capture) → 2026-06-05 (Phase 53 bench close, operator-witnessed) | **Commits:** ~139 (meta-repo, coordinated dual-repo firmware + host lockstep) | **Branch model:** `v1.10-serial-transport-hardening` stacked off the `v1.9-read-bug-rca` tip in all 3 repos (NOT off main/beta — stale at v1.8 close, missing the COBS ADOPT decision + Phase 44 read-timing knobs). | **Ship:** beta-only — stable `3.0.1` promotion remains operator-gated and deferred to the v1.9 read-bug fix (D-17v2 carry-forward).

**Delivered:** A custom delimiter-based serial framing + automatic-resync layer on the Arduino↔host data path, covering **both** the binary data-block path **and** the host→firmware JSON command channel, making the transport **provably byte-exact** end to end. This rules serial corruption out as a confounding variable before the paused per-shield read-bug RCA resumes (v1.9 Phase 45+). All 14 requirements satisfied (FRAME-01..05, CRC-01, LOCK-01/02, SAFE-01, XACT-01/02/03, EVEN-01, CAP-01); every phase VERIFICATION passed. Per `.planning/v1.9-COBS-DECISION.md` §2: ADOPT a custom framing layer; REJECT all off-the-shelf libraries; KEEP CRC8-CCITT poly 0x07 (D-05); honor the Uno-fit filter (D-04 — streaming encode only, ~545 B free-RAM ceiling).

**Key accomplishments:**

1. **Phase 49 — Framing Mechanism Decision (SAFE-01).** COBS `0x00` selected over SLIP `0xC0` via a conclusive static SAFE-01 proof (host `0x00`-silence during the programmer↔communication mode transition window confirmed) plus a scored 4-criterion evidence matrix (COBS 11/12 vs SLIP 10/12). The `len_u16` length prefix and XOR checksum were dropped from the data-block frame; CRC8-CCITT replaces XOR; the frozen D-06 frame contract + CRC8-before-parse mandate were written to `.planning/milestones/v1.10-FRAMING-DECISION.md`.

2. **Phase 50 — Data-Path Framing + Auto-Resync (FRAME-01..04, CRC-01).** Streaming COBS decode-in-place with 1-byte lookahead + CRC8 verify + drain-to-`0x00` resync. The receiver recovers within a single packet, eliminating the 2-second `len_u16`-corruption timeout cascade. Encoder is streaming (no second ~512 B buffer): Uno held at 545 B free (FRAME-03). Host `frame_parser.py` + `_main_phase_send_data` switched to the atomic `b"#" + COBS(chunk + CRC8) + b"\x00"` send. Both suites green (28/28 native + 408/408 host).

3. **Phase 51 — Command-Channel Framing Migration (FRAME-05).** Breaking wire change: the host→fw JSON command channel migrated into the same COBS+CRC8 framing — the firmware verifies CRC8 before `parse_json()` on every `CMD_IDLE` ingest, replacing the legacy `{`-peek-and-discard loop. CR-01 (decoder cap lowered to `DATA_BUFFER_SIZE-1`, OOB write closed) and CR-02 (both spin sites bounded with a `millis()`-based inter-byte deadline, hang closed) hardened the decoder. Documented as a lockstep upgrade with no mixed-version interop in both sub-repo READMEs. 36/36 native tests green.

4. **Phase 52 — Lockstep Contract + Round-Trip Tests (LOCK-01/02).** Host-encode↔firmware-decode byte-compatibility proven for data blocks **and** command frames, including delimiter-laden and all-delimiter payloads. A separate `codegen_vectors.py` pins golden vectors in the `test_messages` Unity suite + host parser tests; both codegen drift gates clean; D-09 byte-identity proven. Firmware 39/39, host 422/422.

5. **Phases 54 & 55 — Even-Block Transfers (EVEN-01) + Capability Advertisement (CAP-01).** Host→fw write/verify blocks made full even buffer-sized (512/1024) instead of `buffer−2`, so a chip-sized transfer divides into whole blocks with no odd remainder chunk (one fewer write round). Phase 55 then relocated the buffer-size advertisement off the FW version string onto a `u16` param on the per-operation `MSG_OK_READY` ack; the host defaults to a universally-safe 512 when absent (no `FirmwareOutdatedError` — reverses Phase 54 D-05). FW identity returned to pure `<version>:<board>`. Both verified (54: 12/13, 55: 5/5); host 458/458 at 72% coverage.

6. **Phase 53 — Byte-Exact Bench Verification, operator-witnessed (XACT-01/02/03).** N=5 read self-consistency (verdict 0) + N=5 write→read-back==source (verdict 0) on clean Uno (512 B) and Leonardo (1024 B), Rev 2.0, on the shipped post-55 contract (self-consistency form per D-05 — neither chip was the original GATE-1.8d baseline). COBS/CRC8 resync proven on real hardware in both directions and both fault forms with no silent corruption: ~1 ms NAK for complete corrupt frames, a single bounded ~1 s inter-byte deadline for truncated frames — the Phase-50 2 s cascade stays gone. uno328pb re-tested on the hardened transport: the catastrophic v1.6 floating-bus mode (~99.4% 0xff) is resolved, but read instability (intermittent timeouts + run-to-run divergence) **persists** — recorded as a structured transport-**exoneration** verdict, NOT a per-shield hardware fix; the RCA stays deferred to v1.9 Phase 45+. Bench evidence aggregated at `.planning/milestones/v1.10-artifacts/bench-verification/SUMMARY.md` as the direct hand-off to the resumed RCA.

**Known deferred items at close:** 8 (see STATE.md → Deferred Items). None are incomplete v1.10 transport work — they are v1.0-era logging UAT/verification gaps (Phases 08/09), an already-fixed debug session (`firmware-vpp-misread`, fixed in Phase 54 UAT), a pre-v1.10 parked FRAM session, and carry-forward todos (incl. the WR-01 COBS decoder byte-wait deadline, explicitly deferred per REQUIREMENTS.md §Future).

**Carry-forward to v1.9:** The transport is now a settled, byte-exact variable. v1.9 Read-Bug RCA resumes at Phase 45 (`/gsd-plan-phase 45`) once the hardened transport is merged. Bench evidence + the uno328pb exoneration verdict feed directly into Bug A / Bug B per-shield diagnosis.

---

## v1.8 — Host CLI Structural Cleanup (firestarter_app) — Shipped 2026-05-29

**Phases:** 8 (numbered 36-43) | **Plans:** 26 (Phase 36 = 4, Phase 37 = 3, Phase 38 = 5, Phase 39 = 4, Phase 40 = 3, Phase 41 = 4, Phase 42 = 3, Phase 43 = 3) | **Timeline:** 2026-05-27 (planning start; v1.8 branched off `beta@3.0.0b6` in firestarter_app + off `main` in meta-repo) → 2026-05-28 (Phase 36–42 complete; suite green at v1.8-app-cleanup tip `9999bdb`) → 2026-05-29 (Phase 43 close; branch promotion) | **Ship tag:** `3.0.0b7` (beta-only — stable `3.0.1` deferred to v1.9 read-bug fix per D-17v2 carry-forward) | **Commits:** meta-repo 75, firestarter_app sub-repo 66 (notable: `9999bdb` Phase 42 tip carries mypy strict on 8 modules + 70% coverage gate; `04a0c13` Phase 42 BUG-2 except-clause split; `910ed75` Phase 42 `@map_typed_errors` decorator; `3224f7e` Phase 41 entry-point swap; `6241dba` Phase 41 BUG-1 `build_arg_flags` fix), firestarter sub-repo UNCHANGED (`0bbe017` v1.6 close tip; host-only milestone — no v1.8 commits).

**Delivered:** v1.8 is a **pure-software structural cleanup** of the `firestarter_app` Python host CLI. Per the locked scope (PROJECT.md v1.8 Decisions 2026-05-27), GATE-1.8 is a "refactor + fix bugs found" non-regression contract: wire protocol stays byte-identical (a); end-user CLI surface preserved (b); firmware/app constant contract preserved via parity tests (c); host read path ring-fenced for the v1.9 RCA (d); full test suite green + entry point installs (e). All five sub-clauses verified at Phase 43 close. The 21-module flat layout under `firestarter_app/firestarter/` reflects the post-v1.8 shape: `main.py` (35 lines, was 932 lines pre-Phase-41); `cli_handlers.py` (~1022 lines, 14 Click commands + `dev` group); `chip_resolver.py` (replaces 9× chip-lookup copy-paste); `frame_parser.py` + `codec.py` (split from the 1037-line pre-cleanup `serial_comm.py`); `address_parser.py` + `exceptions.py` (consolidated typed hierarchy). 30/30 requirements closed: 27 DELIVERED (TEST-01..05 + TOOL-01..03 + STRUCT-01..05 + DATA-01..04 + SERIAL-01..03 + CLI-01..04 + ERR-01..03) + 3 VERIFIED-at-close (DOC-01 + DOC-02 + MS-01). Two latent bugs fixed as INTENTIONAL BEHAVIOR CHANGEs and documented in commit messages: BUG-1 `build_arg_flags` `if "force" in args` attribute-vs-truthiness check (Phase 41 Plan 41-01 commit `6241dba`); BUG-2 `eprom_operations._run_state_machine` `EpromOperationError`-conflated-as-comm-error except clause (Phase 42 Plan 42-01 commit `04a0c13`). The v1.9 read-bug (Bug A + Bug B) carries forward with GATE-1.8d ring-fence intact; the 15 W27C512 N=5 baseline binaries at `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid because `_read_and_parse_lines` body is byte-identical pre/post v1.8.

### Key Accomplishments

1. **Phase 36 — Characterization Test Baseline (TEST-01..05).** Landed the safety net BEFORE any structural change: 29 syrupy snapshots pin the CLI surface via subprocess goldens (TEST-01; D-01 — subprocess harness since CLI was still argparse at Phase 36, CliRunner adopted in Phase 41); `tests/test_serial_characterization.py` + `tests/test_decoder.py` pin the `_read_and_parse_lines` preamble→body→terminator sequence + sliding-window timeout invariant (TEST-02); `EpromDatabase` de-singletoned via `skip_local_override` constructor seam (TEST-03 / D-06); firmware-contract parity extended from `REVISION_*` only to also cover `COMMAND_*`, `FLAG_*`, `CTRL_*` (TEST-04); BUG-1 `build_arg_flags` + BUG-2 `EpromOperationError`-conflated-as-comm-error pinned `xfail(strict=True)` (TEST-05 / D-08/D-09 — TEST-05 second slot substituted from `COMMAND_FW_VERSION`-may-be-missing since the constant was confirmed PRESENT at 0x0D and folded into TEST-04).

2. **Phase 37 — Tooling Baseline + CI Gate (TOOL-01..03).** `ruff` + `ruff format` configured in `pyproject.toml` (categories E, F, I + UP; no `select = ["ALL"]`); `target-version = py39` + legacy `Optional[X]` / `List[X]` style chosen per D-08. mypy configured gradually with `disallow_untyped_defs = false` globally + watermark gate (`tools/check_mypy_watermark.py`). `.github/workflows/ci.yml` enforces ruff check + ruff format --check + mypy + pytest with `--cov-fail-under=50` floor (raised to 70% by Phase 42 Plan 42-03). `pre-commit` config wires the same hook order (ruff-check → ruff-format → mypy). `.git-blame-ignore-revs` carries the green-baseline transform commit so future blame ignores the format/import-sort sweep.

3. **Phase 38 — Low-Risk Extractions (STRUCT-01..05).** Four new flat modules: `frame_parser.py` (CRC8 + `_decode_param` + structured `Response`/`LogMessage` types; STRUCT-01 — `_decode_id_frame` deliberately STAYS in `serial_comm.py` per D-06, deferred to Phase 40); `codec.py` (`format_message` + revision-silkscreen rendering; STRUCT-02); `address_parser.py` (hex/decimal parsing; STRUCT-03); `exceptions.py` (consolidated hierarchy from `serial_comm` + `eprom_operations` + `hardware`; STRUCT-04). Dead code removed: `read_data_block`, `globals()`-introspection patterns, commented-out blocks (STRUCT-05). Full suite green after each file move.

4. **Phase 39 — Database Cleanup + chip_resolver (DATA-01..04).** New flat `chip_resolver.py` provides `resolve_chip(name, db) -> programmer_config` used by every command — eliminating the chip-lookup boilerplate copy-pasted across 9 handlers (DATA-01). `pin_conversions` dict + `pinouts.json` documented as DISTINCT composing layers (NOT duplicates) per D-05 — documentation-only fix (DATA-02). All `from firestarter.constants import *` star-imports replaced with named imports across all modules for readability + mypy traceability (DATA-03). `COMMAND_FW_VERSION` verified PRESENT at `0x0D` (no missing-constant fix needed; folded into TEST-04 parity per Phase 36 D-08); wire-protocol constants consolidated into one authoritative module with clear firmware-sync markers (DATA-04).

5. **Phase 40 — Serial / Transport Restructure (SERIAL-01..03).** `SerialCommunicator` reduced to transport + command dispatch; firmware-handshake concern lifted out of port discovery (`_probe_port`); type hints added on the public API (SERIAL-01). `_validate_firmware_version` extracted as a testable `@staticmethod` with negative-branch unit tests (SERIAL-02). `_read_and_parse_lines` generator body byte-identical (relocated callees only); `# DO NOT MODIFY — v1.9 RCA territory` marker added per GATE-1.8a + GATE-1.8d; existing + new tests confirm wire byte-identity (SERIAL-03).

6. **Phase 41 — CLI Migration argparse → Click (CLI-01..04).** Migrated the full CLI from argparse to Click as a 4-wave INTENTIONAL BEHAVIOR CHANGE: Wave 1 BUG-1 `build_arg_flags` `getattr`-fix (`6241dba`; CLI-03 + BUG-1 closes); Wave 2 Click skeleton + 3 read-only commands (`631a038`); Wave 3 11 remaining commands + `dev` group + all 5 argparse→Click traps addressed (`73c32fb`; exit codes via `sys.exit(0 if op() else 1)`, no prefix matching, `--no-blank-check` polarity via `is_flag=True flag_value=False`, 3-way mutex via per-option `_check_install_mutex` callback, custom `_FirmwareVersionType(click.ParamType)`); Wave 4 entry-point swap + `argcomplete` removed + `click>=8.1` added + autocomplete.md rewritten for Click's `_FIRESTARTER_COMPLETE=<shell>_source` + CI smoke step `pip install -e . && firestarter --help` (`3224f7e`; CLI-04). `main.py` trimmed 932 → 35 lines; 14-branch argparse dispatcher + 14 `create_*_args` factories + EpromCompleter machinery + argparse-form `_validate_firmware_version` all DELETED. `cli_handlers.py` houses `AppContext` dataclass + 14 `@cli.command()` + `dev` `@cli.group()` with 4 sub-commands. 22 of 29 syrupy snapshots updated to capture Click's `--help/--version/error` format (Phase 36 D-01's "migration-transparent / no snapshot updates" rule was mechanically impossible without a custom Click formatter to mimic argparse byte-for-byte — out-of-scope architectural work). CLI behavioral contract preserved (commands, flags, exit codes, business-logic output); only help/usage/error lexical formatting drifted — a Click formatter implementation detail, not GATE-1.8b's end-user CLI surface.

7. **Phase 42 — Error Handling Normalization + Quality Sweep (ERR-01..03).** ERR-01 closed in two atomic commits: BUG-2 except-clause split in `eprom_operations._run_state_machine` (Plan 42-01 `04a0c13`; INTENTIONAL BEHAVIOR CHANGE — separates `(SerialError, SerialTimeoutError)` from a new dedicated `EpromOperationError` clause with distinct "Programmer error during {op}" log line); `@map_typed_errors` decorator at the Click boundary catches 5 typed-exception clauses and re-raises each as `click.ClickException` → exit 1 (Plan 42-02 `910ed75`); `_resolve_or_exit` shim deleted (9 call sites rewritten to call `resolve_chip(eprom, db=app.db)` directly); applied to all 20 Click callbacks (1× cli group + 14 commands + 1× dev group + 4× dev sub-commands; AST-verified). `firestarter/logging_utils.py:52` `except Exception:` → `except Exception as e: # noqa: F841` so ERR-01 SC#1 grep contract closes end-to-end. ERR-02 + ERR-03 closed by Plan 42-03 (`9999bdb`): mypy strict overrides on 8 modules (D-06 — main, cli_handlers, chip_resolver, frame_parser, codec, address_parser, exceptions, serial_comm; `eprom_operations.py` DELIBERATELY EXCLUDED per D-07 GATE-1.8d read-path ring-fence; deferred to v1.9 post-RCA); 6 missing method docstrings added to `serial_comm.py` (is_connected/send_bytes/send_string/send_json_command/send_ack/send_done/disconnect); 9 new test files (+123 new tests); `pytest --cov-fail-under` raised 50 → 70 in `.github/workflows/ci.yml`; final coverage 70.12%.

8. **Phase 43 — Documentation + Milestone Close (DOC-01, DOC-02, MS-01).** `firestarter_app/README.md` grows a new `## Architecture` section (21-module map + layer-boundary rules + tooling workflow subsection) per D-01 (Plan 43-01); `firestarter_app/CLAUDE.md` receives three targeted edits per D-02 (de-singleton fix + 6 new Key Files lines + tooling-gate one-liner) (Plan 43-01); PROJECT.md ship-state flipped (v1.8 line + Current Milestone → v1.9 PROPOSED + v1.8 Archive section + footer refresh) per D-04 (Plan 43-01); MILESTONES.md grows this entry per D-03 (Plan 43-01); `.planning/milestones/v1.8-archive.sh` mirrors `v1.6-archive.sh` verbatim with phase numbers 36-43, archives `.planning/phases/36-*` through `43-*` into `.planning/milestones/v1.8-phases/` (Plan 43-02 per D-07); ROADMAP.md v1.8 section collapsed to `<details>` block per D-05 (Plan 43-02); new `.planning/milestones/v1.8-REQUIREMENTS.md` extracts the 30-row coverage table from ROADMAP.md with per-requirement disposition column (DELIVERED for 27 of 30 + VERIFIED for DOC-01/DOC-02/MS-01) per D-06 (Plan 43-02); operator-authorized HUMAN-UAT.md drives the 6-step branch-promotion checklist (real-hardware GATE-1.8a witness Step 0 + branch identity Step 1 + firestarter_app `v1.8-app-cleanup` → `beta` merge + `3.0.0b7` beta cut Step 2 + firmware no-op verify Step 3 + meta-repo merge Step 4 + STATE.md flip + token substitution Step 5) per D-08 + D-10 (Plan 43-03).

### Branch Strategy

Per operator standing instruction (memory `feedback_branching`): all v1.8 work landed on `v1.8-app-cleanup` branches. `firestarter_app` sub-repo `v1.8-app-cleanup` off `beta@3.0.0b6` (v1.6 close tip); meta-repo `v1.8-app-cleanup` off `main`; **firmware sub-repo NOT branched** (host-only milestone; firmware stays at `beta@0bbe017` from v1.6 close throughout v1.8). Plan 43-03 (operator-authorized, NOT autonomous) handles the sub-repo `v1.8-app-cleanup` → `beta` merge + ship tag `3.0.0b7` cut + meta-repo `v1.8-app-cleanup` → `main` merge. Ship tag `3.0.0b7` is **LOCKED beta-only** per D-09 — the `3.0.1` stable bump is DEFERRED to v1.9 because v1.8 doesn't fix the read-bug (carried to v1.9 with GATE-1.8d ring-fence intact). The previously-proposed Read-Bug RCA milestone was renumbered v1.8 → **v1.9** on 2026-05-27 when the host-CLI cleanup took the v1.8 slot (cleanup is pure-software / not hardware-gated; cleaner host read path de-risks the RCA work).

### Open backlog carried forward to v1.9

Same three pending todos Phases 37/38/39/40/41/42/43 reviewed — all hardware/protocol/DB-content, out of v1.8's host-CLI-cleanup domain:

- **`large-read-data-jitter-uno328pb.md`** (HIGH, at `.planning/todos/pending/v1.8-seed/`) — the original v1.6 read-bug. Carries to v1.9 with Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) characterized as RCA seed. GATE-1.8d ring-fence preserved the read-path baseline binaries (`.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`) so v1.9 inherits the substrate cleanly.
- **`avrdude-mcu-detection-fallback.md`** (low) — blank-chip / wrong-firmware recovery (hardware; v1.9-or-later).
- **`serial-cobs-resync-data-path.md`** (medium) — COBS framing on the serial data path (protocol; would change wire framing — forbidden by GATE-1.8a; v1.9-or-later if revisited).
- **`w27c512-eeprom-misclassification.md`** (HIGH, operator-tagged) — chip-DB content classification fix (DB data; not docs/close work; v1.9-or-later).

Additionally carried forward to v1.9:

- **`eprom_operations.py` mypy strict overrides** — DEFERRED per Phase 42 D-07 (GATE-1.8d read-path ring-fence prevents touching the read-loop body during v1.8; lifted post-RCA in v1.9).
- **`ProtocolStateMachine` extraction from `serial_comm.py`** (PROTOSM-01) — DEFERRED per v1.8 REQUIREMENTS Future Requirements + Phase 42 deferred list (HIGH complexity; would touch the read path).

### Stats

| Metric | Value |
|--------|-------|
| Phases | 8 (numbered 36-43) |
| Plans | 26 (Phase 36 = 4, Phase 37 = 3, Phase 38 = 5, Phase 39 = 4, Phase 40 = 3, Phase 41 = 4, Phase 42 = 3, Phase 43 = 3) |
| Requirements (v1.8 scope) | 30 total; 27 DELIVERED (TEST-01..05 + TOOL-01..03 + STRUCT-01..05 + DATA-01..04 + SERIAL-01..03 + CLI-01..04 + ERR-01..03) + 3 VERIFIED-at-close (DOC-01 + DOC-02 + MS-01) |
| Meta-repo commits | 75 |
| Firestarter_app sub-repo commits | 66 (notable: `9999bdb` Phase 42 close; `04a0c13` BUG-2 fix; `910ed75` `@map_typed_errors`; `3224f7e` Phase 41 entry-point swap; `6241dba` BUG-1 fix) |
| Post-merge firestarter_app `beta` HEAD | 4f04d98 |
| Post-merge meta-repo `main` HEAD | 305e525 |
| Firmware sub-repo commits | 0 (host-only milestone; firmware stays at `beta@0bbe017` from v1.6 close) |
| main.py line count | 35 (was 932 pre-Phase-41; ROADMAP SC#2 / D-16 enforced ≤ 50) |
| cli_handlers.py line count | ~1022 (14 `@cli.command()` + `dev` group with 4 sub-commands) |
| `@map_typed_errors` callbacks decorated | 20 (1× cli group + 14× @cli.command + 1× dev group + 4× dev sub-commands; AST-verified Phase 42 Plan 42-02) |
| Test count at v1.8 close | 365 (Phase 42 Plan 42-03 raised from 241 baseline via +9 new test files + 123 new tests; 0 xfail; 29 syrupy snapshots green) |
| mypy strict 8-module list | main, cli_handlers, chip_resolver, frame_parser, codec, address_parser, exceptions, serial_comm |
| Coverage at v1.8 close | 70.12% (≥ 70% floor per `.github/workflows/ci.yml` post-Phase-42) |
| INTENTIONAL BEHAVIOR CHANGE commits | 3 (BUG-1 build_arg_flags `6241dba`; BUG-2 except-clause split `04a0c13`; entry-point swap + argcomplete removal `3224f7e`) |
| Hardware impact | NONE (host-only milestone; firmware sub-repo byte-identical to v1.6/v1.7 close state at `0bbe017`) |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **GATE-1.8 (a–e) = "refactor + fix bugs found"** | Locked at milestone start 2026-05-27 (PROJECT.md). Internal structure changes freely; latent bugs and dead code discovered during refactor may be fixed (BUG-1 + BUG-2 closed as INTENTIONAL BEHAVIOR CHANGE per convention); wire protocol stays byte-identical (a); CLI surface preserved (b); constant contract preserved via parity tests (c); host read path ring-fenced for v1.9 RCA (d); suite green (e). | ✓ Good (all five sub-clauses verified at Phase 43 close; software floor passed pre-commit + the BOTH-path real-hardware Step 0 in Plan 43-03 HUMAN-UAT.md) |
| **Phase 36 D-01 — characterization tests run as syrupy subprocess goldens (NOT in-process CliRunner)** | Pinning the argparse-form CLI surface BEFORE the Click migration required subprocess invocation because the in-process import would consume the argparse module's side effects; CliRunner adopted Phase 41 once Click was live. | ✓ Good (29 snapshots pinned in Phase 36; 22 updated in Phase 41 Plan 41-04 to capture Click format swap per documented Rule 4 deviation; CLI behavioral contract preserved through both formats) |
| **Phase 36 D-06 — EpromDatabase `skip_local_override` seam (NOT full DI rewrite)** | Minimal constructor change to make the database injectable for testability without rewriting the singleton consumers; full Click-context DI deferred to Phase 41. The seam is what TEST-03 exercises. | ✓ Good (Phase 36 closes TEST-03 with the seam; Phase 41 Click-context DI replaces singleton call sites cleanly; CLAUDE.md de-singleton edit at Phase 43 reflects the final state per D-02) |
| **Phase 37 D-08 — `target-version = py39` + legacy `Optional[X]` / `List[X]` style** | Codebase still ran on py39 at v1.8 start; `from __future__ import annotations` not adopted milestone-wide; legacy annotation style avoids the bytecode-walking edge cases mypy hits with PEP 604 unions on py39. | ✓ Good (mypy gradient runs clean; baseline transform was format/import-sort sweep + 2× `# noqa` only; no `# type: ignore` blanket additions) |
| **Phase 38 D-01 — `exceptions.py` consolidates the typed hierarchy in one flat module** | Avoids cross-module exception-import cycles; the hierarchy `ChipNotFoundError`/`FirmwareOutdatedError`/(`SerialError`,`SerialTimeoutError`)/`EpromOperationError`/`HardwareOperationError` becomes the single re-raise point for the Click boundary; Phase 42 `@map_typed_errors` decorator depends on this consolidation. | ✓ Good (Phase 42 ERR-01 closed with a 5-clause except chain in `cli_handlers.py:map_typed_errors`; all decorator behavior traced back to the Phase 38 consolidated types) |
| **Phase 39 D-01 — `chip_resolver.resolve_chip(name, db)` is the single call site** | Eliminates the 9× chip-lookup copy-paste across the legacy handlers; makes the call site testable; Phase 41 + Phase 42 `_resolve_or_exit` shim removal depends on this. | ✓ Good (Phase 42 D-05 removed the shim; all 9 chip-op call sites now call `resolve_chip(eprom, db=app.db)` directly + the `@map_typed_errors` decorator catches `ChipNotFoundError` uniformly) |
| **Phase 40 SERIAL-03 — `_read_and_parse_lines` body byte-identical (relocated callees only)** | GATE-1.8a + GATE-1.8d demand the read-path generator body stays bit-stable so v1.9 baseline binaries remain valid. `# DO NOT MODIFY — v1.9 RCA territory` marker added per Plan 40 spec. | ✓ Good (Phase 43 verifies via Plan 43-03 Step 0 real-hardware byte-identity check against `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` — confirms no wire-byte regression slipped through suite-green Phase 36-42) |
| **Phase 41 D-08 — `firestarter.main:main` entry-point ABI preserved via `main = cli` re-export** | The pip entry point in `pyproject.toml` resolves `firestarter:main`; renaming would force every installed user to rebuild. `main.py` stays as a re-export stub. | ✓ Good (entry-point smoke `pip install -e . && firestarter --help` exits 0 across Phase 41 Plan 41-04 + Phase 43 Plan 43-01 pre-flight; ABI preserved) |
| **Phase 41 D-13 — All 5 argparse→Click traps handled explicitly** | Trap #1 exit codes via `sys.exit(0 if op() else 1)`; #2 no prefix matching (Click default); #3 `--no-blank-check` polarity via `is_flag=True flag_value=False default=True`; #4 3-way mutex via per-option `_check_install_mutex` callback; #5 firmware-version validator via custom `_FirmwareVersionType(click.ParamType)`. | ✓ Good (all 5 traps tested in `test_cli_handlers.py` per Phase 41 Plan 41-03 W3 + W4 deviations documented inline; CLI behavioral contract preserved) |
| **Phase 42 D-03 — `@map_typed_errors` decorator at Click boundary; exit codes 0/1/2 preserved** | Service-layer code raises typed exceptions; Click boundary maps them to `click.ClickException` → exit 1; `dev consistency-check` 3-way verdict (0=PASS, 1=FAIL, 2=hardware-error) preserved because `sys.exit(verdict_int)` raises `SystemExit` (outside decorator's except list); GATE-1.8b satisfied. | ✓ Good (Phase 42 Plan 42-02 ERR-01 fully closed; 1 of 29 snapshots updated for the wrapper-frame traceback in `test_info_known_chip_stderr` per Rule 1 deviation documented in SUMMARY) |
| **Phase 42 D-06 — mypy strict on 8 modules (NOT 9)** | The 8th module is `serial_comm.py` (with per-line `# type: ignore[union-attr]` on GATE-1.8d ring-fenced read-loop lines to preserve byte-identical generator body). 9th candidate `eprom_operations.py` DELIBERATELY EXCLUDED per D-07. | ✓ Good (mypy on the 8-module strict list exits 0; preserves the read-path ring-fence; defers full strict to v1.9 post-RCA) |
| **Phase 42 D-07 — `eprom_operations.py` mypy strict DEFERRED to v1.9** | Touching the read-loop body during v1.8 would invalidate the v1.6 baseline binaries (GATE-1.8d violation). Strict mode adoption requires touching the body to fix any `Optional`/`Union` narrowing the type checker surfaces. | ✓ Good (carry-forward recorded in this entry's "Open backlog carried to v1.9"; lifted post-RCA in v1.9) |
| **Phase 42 D-15 — `pytest --cov-fail-under` raised 50 → 70 in CI** | The +9 new test files from Phase 42 Plan 42-03 lifted measured coverage 60.27% → 70.12%; raising the floor matches measured reality and locks the gain. | ✓ Good (CI green at 70.12% post-Plan 42-03; future regression below 70% blocks the build) |
| **Phase 43 D-08 — GATE-1.8 verification via BOTH path (software-floor + real-hardware Step 0)** | Operator-selected at /gsd-discuss-phase. Software floor (Plan 43-01 pre-flight) provides suite-green; real-hardware Step 0 (Plan 43-03 HUMAN-UAT.md) confirms no wire-byte regression slipped past suite-green via byte-identity match against `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/`. | Pending (Plan 43-03 — operator runs `firestarter read -e W27C512` on Modified Rev 0 + Leonardo bench; PASS = byte-identical match; FAIL = re-open Phase 43) |
| **Phase 43 D-09 — Ship tag LOCKED `3.0.0b7` beta-only (NOT `<ship-tag-TBD>` hedged)** | Per v1.6 D-17v2 carry-forward: stable `3.0.1` deferred to "a real read-bug fix in v1.8" — v1.8 doesn't fix the read-bug (carried to v1.9 with GATE-1.8d ring-fence), so the deferral carries forward to v1.9 close. Beta-only `3.0.0b7` (next pre-release from current `3.0.0b6` at v1.6 close) lets `pip install --pre firestarter` users pick up the structural cleanup + bug fixes without misleading the stable channel. | Pending (Plan 43-03 cuts `3.0.0b7` via firestarter_app `beta-release.yml` workflow; operator may overrule to `3.0.1` stable IFF accepting carry of unfixed read-bug, but plan default is `3.0.0b7`) |
| **Phase 43 D-11 — 3-plan strict-sequential decomposition mirrors v1.6 Phase 30** | Plan 43-01 (autonomous docs+state) → Plan 43-02 (autonomous archive+collapse) → Plan 43-03 (operator-authorized HUMAN-UAT branch promotion); worktrees OFF per memory `project_v18_phase_execution_mechanics` (sequential execution; SDK can't parse v1.8 ROADMAP — flip checkboxes/STATE manually). | Pending (Plans 43-01 + 43-02 + 43-03 land in sequence; 43-03 emits the operator checklist) |

### Known Gaps (carried to v1.9)

Per Phase 42 D-07 + the host-only milestone scope, the following carry forward to v1.9:

- **v1.6 read-bug (Bug A + Bug B)** — original 64KB streaming-read byte-jitter, carried forward from v1.6 close (D-17v2 re-scope). GATE-1.8d ring-fence preserved through v1.8; `_read_and_parse_lines` generator body byte-identical pre/post; 15 N=5 W27C512 baseline binaries at `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` remain valid; pattern findings in `.planning/milestones/v1.6-EVIDENCE.md` Phase 29 v2 H3 block; canonical close narrative at `.planning/milestones/v1.6-phases/29-multi-board-bench-verification/29-04-SUMMARY.md`.
- **`eprom_operations.py` mypy strict overrides** — DEFERRED per Phase 42 D-07. Lifted post-RCA in v1.9.
- **`ProtocolStateMachine` extraction from `serial_comm.py`** (PROTOSM-01) — DEFERRED per v1.8 REQUIREMENTS Future Requirements (HIGH complexity; would touch the read path).
- **`avrdude-mcu-detection-fallback.md`** + **`serial-cobs-resync-data-path.md`** + **`w27c512-eeprom-misclassification.md`** — three pending todos reviewed across Phases 37-42-43; all hardware/protocol/DB-content, out of v1.8's domain.

### Hardware impact

NONE. v1.8 is a host-only milestone — the `firestarter` firmware sub-repo is byte-identical to v1.6/v1.7 close state at `beta@0bbe017`. The constant contract between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` + `rurp_shield.h` + `rurp_pinout.h` is preserved verbatim and guarded by extended parity tests covering `COMMAND_*`, `FLAG_*`, `CTRL_*`, and `REVISION_*` (TEST-04 extension). No firmware tag is cut at v1.8 close (Plan 43-03 Step 3 VERIFY NO-OP).

---

## v1.6 — Fix the Read Bug (Shipped: 2026-05-26 — diagnostic + revert)

**Phases:** 5 (numbered 26-30) | **Plans:** 13 (Phase 26 = 2, Phase 27 = 3 including re-open Plan 27-05, Phase 28 = 4 including revert Plan 28-03 + parked Plan 28-04, Phase 29 = 4 including v2 re-iteration Plans 29-03/04, Phase 30 = 3) | **Timeline:** 2026-05-21 (planning start) → 2026-05-22 (Wave B FAIL — D-07 milestone-reopens) → 2026-05-26 (Phase 27 re-open Plan 27-05 closes + Phase 28 re-iterates with revert + Phase 29 v2 PASS_PARKED on bench + v1.7 ships in parallel + Phase 30 close) | **Ship tag:** `3.0.0b6` (beta-only — `3.0.0b5` was v1.7's cut, so v1.6 ships as the next pre-release; `3.0.1` stable deferred to a real read-bug fix in v1.8 per D-17v2; both sub-repos cut `3.0.0b6` in lockstep 2026-05-26) | **Commits:** meta-repo 48, firestarter sub-repo 5 v1.6 commits + beta merge `0bbe017` (notable: `437339b6` reverted via `ea25174`; `4f205e58` `_NOP()` settling preserved), firestarter_app sub-repo 2 v1.6 commits + beta merge `6b2687d` (notable: `999c3cc` host-CLI tip carrying the `dev consistency-check` GREEN implementation).

**Delivered:** v1.6 ships as a **course-correction milestone**. Per D-17v2 (re-scope locked 2026-05-26), the milestone delivers a permanent diagnostic + revert of the Phase 28 v1 firmware-induced regression — NOT a fix for the underlying 64KB streaming-read byte-jitter bug, which is intentionally deferred to v1.8 with characterized pattern findings as the RCA seed. Three artifacts ship to main: (1) `firestarter dev consistency-check <chip> --runs N` host CLI subcommand for N-run SHA-256 byte-identity measurement (REPRO-03, Phase 26), permanent regression check for any future fix candidate; (2) Phase 27 RCA narrative + Phase 27 re-open dual-cause disposition in `.planning/milestones/v1.6-EVIDENCE.md` (RCA-01..03); (3) Phase 28 v1's `437339b6` PORTx-clear cleanly reverted via `ea25174` in `firestarter/`, leaving Leonardo Modified Rev 0 returning to the Phase 26 baseline shape (WORST=0.047% zero-bytes across N=10 vs 83.8% pre-revert). The `4f205e58` `_NOP()` settling change is PRESERVED (Plan 28-04 parks permanently). Cross-board bench evidence and Bug A + Bug B pattern findings ship as the v1.8 RCA substrate. The original read-bug (Bug A = Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew; Bug B = Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch) is documented but not addressed.

### Key Accomplishments

1. **Phase 26 — Cross-board reproduction + diagnostic tooling (REPRO-01/02/03).** Landed `firestarter dev consistency-check <chip> --runs N` in `firestarter_app/firestarter/` — runs N consecutive `read` operations against a static chip, computes per-run SHA-256s, reports pass/fail verdict + first-divergence offset on mismatch + per-run binary capture under `.planning/milestones/v1.6-artifacts/consistency-check-runs/<chip>-<board>-<timestamp>/`. 8-test pytest scaffold landed at `firestarter_app/tests/test_consistency_check.py`. Cross-board pre-fix baseline captured: Plain Uno (`/dev/ttyACM0`, Rev 2.0) = PASS (refuted the pre-existing-bug prediction); Leonardo (`/dev/ttyACM1`, Modified Rev 0) = FAIL (~2.1% jitter at 64KB; 1349/65536 divergent bytes). The diagnostic is the permanent post-fix regression check that v1.8 will invert.

2. **Phase 27 — RCA narrative + introducing-commit triangulation (RCA-01/02/03).** Identified the Leonardo data-bus pinout (PORTD/PORTC/PORTE three-port reassembly in `rurp_read_data_buffer`) + the missing PORTx-clear in `rurp_set_data_input` as the dual-mechanism source: residual pullup bias on partially-erased EPROM cells + multi-instruction PINx read race. 78% single-bit XOR distribution + 63% address-bit-3 correlation + 15% 0xFF partial-erased-chip signature triangulated H2 over H1/H3/H4/H5 with HIGH confidence (no Wave B instrumented bench build needed — Plan 27-02 parked). Introducing-commit bracketed to **pre-v1.0** via tag-walk of `2.0.2..3.0.0b4` (current shape introduced by `5b1f1cd` 2025-02-11). GATE-1.6 three-axis risk assessment GREEN.

3. **Phase 27 re-open (2026-05-26, Plan 27-05) — dual-cause disposition.** After Phase 29 v1 Wave B FAIL, Plan 27-05 confirmed dual-cause disposition: Outcome A (Leonardo firmware-induced via Phase 28 v1 `437339b6` PORTx-clear over-correction) + Outcome B-independent (uno328pb pre-existing hardware regression — independent of v1.6 scope; deferred to v1.8). The re-open closes with split-scope handoff: Leonardo revert via Plan 28-03; uno328pb operator hardware diagnosis deferred.

4. **Phase 28 — Initial fix + unit test (FIX-01/02/03 v1) shipped 2026-05-21 then reverted 2026-05-26.** Plan 28-01 RED Unity scaffold + Plan 28-02 two atomic fix commits (`437339b6` PORTx-clear masked-form mirror of Uno-side `df5fb44`; `4f205e58` `_NOP()` settling) landed clean desk-side with 22/22 Unity test PASS. Phase 29 v1 Wave B FAIL on Leonardo + uno328pb (83.8% zeros + 5 distinct SHAs) triggered D-07 milestone-reopens. **Plan 28-03 (2026-05-26)** atomically reverted `437339b6` alone via `ea25174` on `firestarter/v1.6-read-bug`; pullup-clear Unity test pruned as obsolete; Axis 4 `.hex` SHA identity table preserved (uno + uno328pb Δ=0). **Plan 28-04 (drafted-but-not-executed)** parks permanently — `4f205e58` `_NOP()` settling ships to main as the only behavioral firmware change from v1.6.

5. **Phase 29 v2 — operator-on-bench PASS_PARKED gate emission (2026-05-26).** Plan 29-03 desk-side rebuild from `firestarter/v1.6-read-bug` @ `efd203a` captured Leonardo SHA `734b9a85…` (68884 B) matching Phase 28 re-iteration Axis 4 expected. Plan 29-04 bench gate emission: 3× N=5 `firestarter dev consistency-check W27C512` (Modified Rev 0 canonical + Rev 2.0 bonus diagnostic + Modified Rev 0 replication). Modified Rev 0 WORST zero-byte ratio 0.047% (≤ 1.00% D-21v2 structured_data threshold); 99.50% cross-session-stable-byte agreement; Phase 26 baseline shape match. Emitted `plan_28_04_gate: pass_parked` per D-22v2. VERIFY-02 PASS; VERIFY-01 + VERIFY-04 unconditionally DEFERRED to v1.8 per D-29v2 + D-30v2; VERIFY-03 DEFERRED per D-26v2 operator-optional. Pattern findings (Bug A + Bug B) characterized in `.planning/milestones/v1.6-EVIDENCE.md` H3 block as v1.8 RCA seed.

6. **Phase 30 — Documentation + milestone close (DOC-01/02 + MS-01).** Read-bug todo `large-read-data-jitter-uno328pb.md` moved from `.planning/todos/pending/` to `.planning/todos/pending/v1.8-seed/` with `status: v1.8-deferred` + Bug A + Bug B annotation header + 15 N=5 W27C512 binaries + Phase 29 v2 H3 block + Plan 29-04 SUMMARY cross-references (DOC-01). PROJECT.md flipped to ship-state reflecting the re-scoped "diagnostic + revert" disposition; v1.7 shipped-archive entry written; Current Milestone block flipped per operator discretion (default: v1.8 PROPOSED). v1.5 backlog carry-forward annotated `carried forward to v1.8 with Bug A + Bug B pattern findings` (DOC-02). MILESTONES.md grows this entry (MS-01). Phase artifacts archived via `.planning/milestones/v1.6-archive.sh` in Plan 30-02; sub-repo branch promotion in Plan 30-03 (operator-authorized).

### Branch Strategy

Per operator standing instruction (memory `feedback_branching`): all v1.6 work landed on `v1.6-read-bug` branches in all 3 repos. Sub-repos branched off `beta@3.0.0b4` post-v1.5 ship; meta-repo `v1.6-read-bug` branched off `main`. Plan 30-03 (operator-authorized, NOT autonomous) handles the sub-repo `v1.6-read-bug` → `beta` merge + meta-repo `v1.6-read-bug` → `main` merge. **Per the re-scope (D-17v2): this is likely a BETA-ONLY ship — the read-bug is not fixed, so stable promotion is operator-discretion.** Actual cut (2026-05-26): `3.0.0b6` pre-release from `beta` in both sub-repos (lockstep), carrying the `4f205e58` `_NOP()` settling + `dev consistency-check` CLI. `3.0.0b5` was already taken by v1.7's ship, so v1.6 advanced to the next pre-release. The `3.0.1` stable bump is deferred until v1.8 ships the real read-bug fix.

### Open backlog carried forward to v1.8

The Phase 29 v2 pattern analysis (15 N=5 W27C512 binaries) surfaced two independent failure modes that DO NOT close in v1.6 — they carry to v1.8 as the RCA starting hypothesis substrate:

- **Bug A — Modified Rev 0 upper-address jitter (the original v1.6 read-bug; carries to v1.8).** 858/65536 (1.31%) byte positions disagree within N=5; A15=1 → 1.70% jitter vs A15=0 → 0.92% (1.86× skew); 63% of jitters BIT-RAISE; mean delta +8.89. Hypothesis: upper-address signal-integrity (A14/A15 high → ground bounce / capacitive crosstalk) + weak data-bus pull-down. `_NOP()` settling at `4f205e58` targeted timing but is insufficient on its own.
- **Bug B — Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch (independent shield-specific issue).** All 5 Rev 2.0 N=5 byte-identical (zero within-session jitter); 49.06% of bytes are bus-tristate symptoms (36.19% `0xff` + 12.87% `0x00`); VPP=13.1-13.2V > 12.0V expected; 83.1% bytes differ from Modified Rev 0 with uniform XOR across D0-D7 (NOT a single stuck data line).
- **VERIFY-01 (uno328pb byte-identity)** — DEFERRED to v1.8 per D-29v2 (independent pre-existing hardware regression per memory `project_uno328pb_bench_instability_27_04`).
- **VERIFY-03 (1KB low-rate jitter)** — DEFERRED operator-optional per D-26v2 (over-determined by 64KB structured_data verdict via shared `_run_state_machine` + `_main_phase_read_data` code path).
- **VERIFY-04 (Phase 24 BENCH-02 closure)** — DEFERRED to v1.8 per D-30v2 (BENCH-02 needs working read path which carries to v1.8 alongside Bug A fix).
- **`w27c512-eeprom-misclassification.md`** (HIGH, operator-tagged "asap") — still carried forward; out-of-scope of v1.6 per D-17v2.
- **`avrdude-mcu-detection-fallback.md`** (low) — still carried forward.

v1.8 RCA substrate (ready to consume): `.planning/milestones/v1.6-artifacts/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` (15 N=5 W27C512 binaries — Modified Rev 0 canonical + Rev 2.0 bonus + Modified Rev 0 replication); `.planning/milestones/v1.6-EVIDENCE.md` Phase 29 v2 H3 block; `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md` canonical close narrative; v1.7 substrate (`.planning/milestones/v1.7-SHIELD-REVS.md` per-rev capability table + labeled schematic + shield-version-detect firmware plumbing — enables v1.8 to design A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step).

### Stats

| Metric | Value |
|--------|-------|
| Phases | 5 (numbered 26-30) |
| Plans | 13 (Phase 26 = 2, Phase 27 = 3 incl. re-open 27-05, Phase 28 = 4 incl. revert 28-03 + parked 28-04, Phase 29 = 4 incl. v2 re-iteration 29-03/04, Phase 30 = 3) |
| Requirements (v1.6 scope) | 16 total; closed-as-DELIVERED: REPRO-01/02/03 + RCA-01/02/03 + FIX-01/02/03 + DOC-01/02 + MS-01 (12); closed-as-DEFERRED-to-v1.8: VERIFY-01 + VERIFY-03 + VERIFY-04 (3); closed-as-PASS via structured_data shape: VERIFY-02 (1) |
| Meta-repo commits | 48 (`git log --oneline --since=2026-05-21 -- .planning/ \| wc -l` at Phase 30 Plan 30-01 write time, pre-30-01 commits) |
| Firmware sub-repo commits | 5 v1.6 commits; beta merge `0bbe017`; CI version-bump `8fead2d` (notable: `437339b6` reverted via `ea25174`; `4f205e58` `_NOP()` settling preserved; v1.6-read-bug tip `efd203a` per Phase 29 v2 VERIFICATION) |
| Host sub-repo commits | 2 v1.6 commits; beta merge `6b2687d`; CI version-bump `c24df71` (notable: `999c3cc` carries the `dev consistency-check` GREEN implementation + 8-test pytest scaffold) |
| Bench sessions (operator-on-bench) | 4 (Phase 26 Wave B, Phase 29 v1 Wave B Attempt 1, Phase 29 v1 Wave B Attempt 2 FAIL, Phase 29 v2 Wave B PASS_PARKED) |
| Bench binaries captured | 21 × 65536 B (6 in Phase 26 baseline + 15 in Phase 29 v2 across 3 sessions) + 3 Phase 29 v1 sessions (audit-trail-immutable per D-25v2) |
| New CLI subcommand | 1 (`firestarter dev consistency-check`) |
| New pytest tests | 8 (`firestarter_app/tests/test_consistency_check.py`) |
| New Unity tests (firmware) | 2 (`test_rurp_set_data_input_clears_data_pullups_leonardo` + `test_rurp_read_data_buffer_reassembles_data_bus`; pullup-clear pruned in Plan 28-03) |
| Hardware impact | Leonardo `.hex` size unchanged from `beta@3.0.0b4` (PORTx-clear reverted); `4f205e58` `_NOP()` settling adds ~4 B (well within ±200 B GATE-1.6); Uno + uno328pb Δ=0. The only behavioral firmware ship is the `_NOP()` settling; the read-bug is NOT fixed by design per D-17v2. |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **D-17v2 (re-scope 2026-05-26): v1.6 ships as "diagnostic + revert" NOT as "fix the read-bug"** | Phase 29 v1 Wave B FAIL revealed Phase 28 v1 firmware-induced regression on Leonardo (83.8% zeros). Plan 27-05 re-open confirmed dual-cause disposition (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware). Continuing with a wrong fix would compound technical debt; clean revert + characterized pattern findings as v1.8 RCA seed is the integrity-preserving path. | ✓ Good (Phase 29 v2 PASS_PARKED confirms Leonardo Modified Rev 0 returns to Phase 26 baseline shape; Bug A + Bug B characterized; v1.7 substrate shipped in parallel gives v1.8 known-good schematics) |
| **D-22v2: triple-state Plan 28-04 gate emission (`pass_parked` \| `activate` \| `needs_human`) APPENDED to verdict file** | Preserves the audit trail of the default-before-bench state alongside the live emission; avoids overwriting prior decisions; mirrors v1.4's E2E iterative substrate fix pattern. | ✓ Good (Phase 29 v2 emitted `pass_parked`; verdict file 8-line preamble byte-identical pre/post; D-25v2 immutability satisfied) |
| **D-25v2: Phase 29 v1 audit-trail content byte-identical post-v2** | Re-iteration must not overwrite prior failure evidence — the FAIL outcome is itself load-bearing evidence (it triggered Plan 27-05 + Plan 28-03). Immutability rule with single explicit D-24v2 exception (placeholder cross-link replacement). | ✓ Good (lines 188-376 SHA-256 byte-identical across `f902a63` and `47c364c`; verified in Phase 29 VERIFICATION.md) |
| **D-29v2: VERIFY-01 (uno328pb byte-identity) DEFERRED to v1.8 unconditionally** | uno328pb regression is independent pre-existing hardware issue per memory `project_uno328pb_bench_instability_27_04` + Plan 27-04 falsifier `d9e51b7e…` over-determination; not a v1.6 scope item. v1.7 labeled-schematic + shield-version-detect substrate gives v1.8 the foundation. | ✓ Good (Phase 29 v2 closes VERIFY-01 as DEFERRED; not an artificial failure) |
| **D-30v2: VERIFY-04 (Phase 24 BENCH-02 closure) DEFERRED to v1.8 unconditionally** | BENCH-02 needs working read path — carries to v1.8 alongside Bug A fix. Write-path non-regression already confirmed desk-side via Phase 28 re-iteration Axis 4 `.hex` SHA identity (uno + uno328pb Δ=0). | ✓ Good (BENCH-02 carry is explicit, not silent; v1.8 inherits the substrate cleanly) |
| **D-27v2: Modified Rev 0 + voltage-divider mod is the canonical bench shield for Phase 29 v2** | Anchors against Phase 26 baseline (same shield); Rev 2.0 bonus diagnostic produces additive forward-traceability for v1.8 but does NOT replace the canonical anchor. | ✓ Good (multi-shield bench session within single operator visit per `feedback_chip_out_before_sideload` discipline; produced richer pattern findings without weakening gate verdict) |
| **D-21v2: structured_data shape classification threshold = zero-byte ratio < 1.00% across N=5** | Distinguishes "Leonardo baseline jitter character per Phase 26" from "Phase 28 v1 firmware-induced zeros-dominant regression" empirically. | ✓ Good (Phase 29 v2 WORST 0.047% across N=10; well-clear of threshold; classification is unambiguous) |
| Phase 30 SC#5 sub-repo branch promotion = operator-authorized, NOT autonomous (default beta-only) | Per memory `feedback_branching` + the re-scope (read-bug not fixed, stable bump is premature). Plan 30-03 documents exact `git` commands + branch identity verification but does not pre-decide ship tag. | Pending (Plan 30-03 — operator confirms `3.0.0b5` beta-only vs `3.0.1` stable promotion at execution time) |

### Known Gaps (deferred to v1.8 — pointers to v1.8 RCA seed substrate)

Per D-17v2 re-scope, the following are explicit pointers to v1.8 RCA hand-off material recorded in `.planning/todos/pending/v1.8-seed/large-read-data-jitter-uno328pb.md` + `.planning/milestones/v1.6-EVIDENCE.md` Phase 29 v2 H3 block + `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md`:

- **Bug A (Modified Rev 0 upper-address jitter)** — the original v1.6 read-bug; carries to v1.8 with characterized address-bit correlation (A15=1 → 1.86× skew; A14=1 → 1.46× skew) + bit-direction bias (63% BIT-RAISE) + upper-24KB-dominant footprint. v1.7's per-rev capability matrix anchors which shield is on the bench at each v1.8 fix-candidate A/B step.
- **Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch)** — independent shield-specific issue; carries to v1.8 with VPP=13.1V anomaly + 49.06% bus-tristate-symptom signature + uniform D0-D7 XOR distribution.
- **VERIFY-01 (uno328pb byte-identity)** — DEFERRED to v1.8; independent pre-existing hardware regression.
- **VERIFY-03 (1KB low-rate jitter)** — DEFERRED operator-optional; over-determined by 64KB structured_data verdict.
- **VERIFY-04 (Phase 24 BENCH-02 closure)** — DEFERRED to v1.8; needs working read path.
- **`w27c512-eeprom-misclassification.md`** (HIGH) — still carried forward; v1.6 out-of-scope per D-17v2.
- **`avrdude-mcu-detection-fallback.md`** (low) — still carried forward.

### Hardware impact

The only behavioral firmware change shipping from v1.6 is the `_NOP()` settling at commit `4f205e58` in `firestarter/src/boards/leonardo_rurp_shield.cpp:rurp_read_data_buffer` (adds 2 `_NOP()` calls between PIND/PINC/PINE reads — ~125 ns settling, comfortably > 90 ns W27C512 tACC; ~8 ms total overhead per 64KB read, invisible against ~3 s read time). Phase 28 v1's PORTx-clear at `437339b6` was reverted via `ea25174` and DOES NOT ship. Uno + uno328pb `.hex` artifacts byte-identical to `beta@3.0.0b4` (Δ=0). Leonardo `.hex` carries the `_NOP()` settling only (well within ±200 B GATE-1.6 budget). The 64KB streaming-read byte-jitter bug itself is NOT fixed and remains by design per D-17v2 re-scope — characterized as Bug A + Bug B in the v1.8 RCA seed substrate.

---

## v1.5 — Arduino Uno (ATmega328PB) Board Support (Shipped: 2026-05-21)

**Phases:** 5 (numbered 21-25) | **Plans:** 6 (Phase 21 = 2, Phase 22 = 1, Phase 23 = 2, Phase 24 = bench-only / 0 plans, Phase 25 = 1) | **Timeline:** 2026-05-20 (planning) → 2026-05-21 (execution + bench validation + close — single-day operator-on-bench cut) | **Ship tag:** 3.0.0b4 (auto-incremented from v1.4's 3.0.0b3 via the v1.4 lockstep mechanism on push to `beta`) | **Commits:** meta-repo ~30, firestarter sub-repo 3 (`da607d4` + `ab7c2a9` + merge `62df517`), firestarter_app sub-repo 4 (`67c8357` + `d13d9b1` + `c184910` urclock fix + merge `75db46e`)

**Delivered:** Added `uno328pb` as a third first-class firmware target alongside `uno` and `leonardo`. Three-board release matrix flows end-to-end: `pio run` emits three `.hex` files per cut → CI workflows' existing `files: .pio/build/**/firestarter_*.hex` glob picks up the new artifact with zero workflow YAML changes → `firestarter fw -i --pre` resolves and flashes the matching artifact for `uno328pb`-reporting devices. Bench-validated on operator's 328PB-Uno (/dev/ttyUSB0): full install path proven on real silicon, post-flash handshake reports `v3.0.0b4, controller: uno328pb`. Existing `uno` + `leonardo` artifacts remain byte-identical (GATE-1.5 preserved via `cmp -s` against baselines captured at firestarter/beta @ 5fd751e).

### Key Accomplishments

1. **Firmware build target (Phase 21 — FW-01..FW-04).** New `[env:uno328pb]` in `firestarter/platformio.ini` between `[env:uno]` and `[env:leonardo]` (`platform = atmelavr`, `board = ATmega328PB`, `-D RURP_BOARD_NAME=\"uno328pb\"`). MiniCore-the-core is bundled inside `platformio/atmelavr@5.2.0` via the stock `ATmega328PB` board file's `build.core` field — no custom board JSON needed (CONTEXT D-05 Path B). Atomic 4-site macro-guard widening (`ARDUINO_AVR_UNO` → `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`) in `uno_rurp_shield.cpp`, `rurp_common.cpp` (×2 lines), `rurp_register_utils.h` — no umbrella macro per CONTEXT D-02. `name_firmware.py` reworked to derive PROGNAME from `-D RURP_BOARD_NAME` via `env.ParseFlags()` so the board-id triple (board-id = artifact-name = handshake-string) has a single source of truth.

2. **Release pipeline (Phase 22 — REL-01, REL-02).** `platformio.ini` `default_envs` widened to `uno, uno328pb, leonardo` (Phase 21 D-08 section order); ROADMAP SC#1 literal realigned to match (Phase 21 D-12 hand-off). Zero `.github/workflows/*.yml` edits — both `build.yml:105` and `beta-build.yml:92` already used the `firestarter_*.hex` glob. Verified by `softprops/action-gh-release@v2` attaching the third asset on the first real beta cut.

3. **Host CLI installer (Phase 23 — INST-01, INST-02, INST-03, GATE-01).** Two-file edit in `firestarter_app/`: `firmware.py:_install_with_avrdude` gained `uno328pb` elif branch with `("atmega328pb", "urclock", 115200)` profile (bench-validated; initial guess of `arduino` programmer_id was incorrect — operator's MiniCore-flashed 328PB-Uno ships with Urclock bootloader); `main.py` argparse `-b/--board` `choices=` widened to `["uno", "uno328pb", "leonardo"]`. TDD shape (RED tests landed first; 5 new test methods in `test_firmware_install.py` plus a `_FakeAvrdude` module-local mock helper). Full pytest 82/82 PASS; GATE-01 `pytest -k "not uno328pb"` = 77 PASS byte-identical to pre-Phase-23.

4. **Bench validation (Phase 24 — BENCH-01, BENCH-02).** Merge `v1.5-uno328pb` → `firestarter/beta` triggered CI → GitHub Pre-release `3.0.0b4` with three `.hex` artifacts. `firestarter fw -i --pre --force` on `/dev/ttyUSB0` against the 328PB-Uno + RURP shield: downloaded `firestarter_uno328pb.hex` (22,340 bytes in 0.51s), flashed via avrdude+urclock (5.94s), post-flash handshake reports `version: 3.0.0b4, controller: uno328pb`. VPP 12.4–12.5V stable, VPE 14.4V stable, hardware rev EEPROM-read works. Write path bench-validated for small (16B) and medium (256B) writes via SST27SF512 in socket — every committed bit matches expected `pre AND target` pattern byte-for-byte. Full evidence in `.planning/milestones/v1.5-BENCH-RESULTS.md`.

5. **Documentation + milestone close (Phase 25 — DOC-01, DOC-02, MS-01).** Both READMEs (firmware + host CLI) gained three-board references and a per-board PlatformIO env table; ROADMAP Phase 21–24 closed with shipped dates; REQUIREMENTS FW-01..04 + REL-01..02 + INST-01..03 + GATE-01 + BENCH-01..02 all flipped to `[x]`. PROJECT.md updated to "v1.5 shipped 2026-05-21".

### Branch Strategy

Per operator standing instruction (memory `feedback-branching-firestarter-milestones`): all milestone work landed on `v1.5-uno328pb` branches in all 3 repos (meta + firestarter + firestarter_app). Sub-repos merged `v1.5-uno328pb` → `beta` during Phase 24 to trigger the beta CI cut. Meta-repo `v1.5-uno328pb` retains the full planning trail and gets merged to `main` at milestone-close (this file).

### Open backlog carried v1.5 → v1.6 → v1.8

The Phase 24 bench rigor surfaced three pre-existing bugs that do NOT block v1.5 ship but warrant near-term attention:

- **`large-read-data-jitter-uno328pb.md`** (HIGH, **affects all controllers**) — full 64KB streaming reads return ~57% different bytes across consecutive reads. 3-shield A/B/C triage proves the bug is hardware-independent and existed in v1.4 unnoticed. **Carried forward to v1.8** with characterized Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) pattern findings per Phase 29 v2 close (NOT resolved in v1.6 — see v1.6 entry below for D-17v2 re-scope rationale).
- **`w27c512-eeprom-misclassification.md`** (HIGH, operator-tagged "asap") — chip database routes 8 electrically-erasable EEPROMs (W27C512, W27E512, W27C257, W27E257, SST27SF512, SST27VF512, SST27SF256, SST27VF256) to the UV-only EPROM dispatch path. `firestarter erase <chip>` returns `ERROR: Not supported`. Fix requires new firmware dispatch for "12V VPP write + electrical erase" chips, not a one-line override. **Still carried forward** — not in scope for v1.6 (per D-17v2 re-scope, v1.6 ships as 'diagnostic + revert' only).
- **`avrdude-mcu-detection-fallback.md`** (low) — host CLI enhancement for blank-chip recovery; empirical basis bench-validated (avrdude reveals MCU type via stderr on signature mismatch). **Still carried forward** — not in scope for v1.6 (per D-17v2 re-scope, v1.6 ships as 'diagnostic + revert' only).

### Key Decisions (locked)

- **Path B for FW-02** (CONTEXT D-05): drop `boards/uno328pb.json`; use stock `platform = atmelavr` + `board = ATmega328PB`; rework `name_firmware.py` to derive PROGNAME from `RURP_BOARD_NAME`. Preserves the locked board-id-triple invariant.
- **`platform = atmelavr`** (RESEARCH Open Q1 resolution): `MCUdude/MiniCore` is not a registered PlatformIO platform; the MiniCore core ships bundled inside atmelavr@5.2.0.
- **`programmer_id="urclock"`** for uno328pb (bench-validated): MiniCore's stock bootloader on the operator's 328PB-Uno is Urclock, not optiboot. Phase 23 CONTEXT D-02 documented this as a known contingency; bench confirmed it 2026-05-21.
- **GATE-1.5 byte-identity** (CONTEXT D-04): `firestarter_uno.hex` + `firestarter_leonardo.hex` from v1.5 cuts byte-identical to pre-v1.5 (modulo `update_version.py` drift). Baselines captured at `firestarter/beta` tip `5fd751e` (SHA-256 `0dd5c01a…` uno, `f49e2a57…` leonardo); verified via `cmp -s` during Phase 22.
- **Local milestone branches, beta-cut only on operator authorization** (memory `feedback-branching-firestarter-milestones`): work stays on `v1.5-uno328pb` until the operator explicitly authorizes a merge to `beta`. The "merge in to beta and test that we can install via the app to the pb" instruction on 2026-05-21 was the explicit auth point.

---

## v1.4 — Beta & Pre-release Deployment Pipeline (Shipped: 2026-05-20)

**Phases:** 6 (numbered 15-20) | **Plans:** 10 (Phase 15 = 4, Phase 16 = 1, Phase 17 = 1, Phase 18 = 2, Phase 19 = 1, Phase 20 = 1) | **Timeline:** 2026-05-20 (single-day cut: planning + execution + live verification including real-hardware flash) | **Ship tag:** 3.0.0b3 (auto-incremented from b1/b2 during E2E iteration; .pyc hygiene fix triggered b3) | **Commits:** meta-repo 56, firestarter sub-repo 13, firestarter_app sub-repo 17

**Delivered:** Added a parallel beta / pre-release deployment channel across both Firestarter sub-repos without touching the existing main → stable pipelines. Branch-driven trigger (`beta` branch in each sub-repo) wired to new beta workflows that emit PEP 440 / matching pre-release version strings, publish PyPI pre-release wheels (installable via `pip install --pre`), and create GitHub Pre-releases with `make_latest: false` carrying per-board `firestarter_*.hex` artifacts. App and firmware ship locked-step on a single `BETA_VERSION` operator input. Beta-installed app grows three new CLI flags (`--pre`, `--firmware-version`, `firmware list`) plus a PEP 440-safe version comparator; stable-installed app's `firestarter --install` defaults remain byte-identical to pre-v1.4. Documentation: both READMEs grew a Beta channel section; meta-repo `v1.4-RELEASE-PROCEDURES.md` documents the release-engineer cutting workflow.

### Key Accomplishments

1. **Versioning + lockstep foundation (Phase 15 — VER-01/02/03).** Extended both
   sub-repos' `.github/scripts/update_version.py` to recognize beta-branch context
   and emit PEP 440 pre-release identifiers (`X.Y.ZbN`, `X.Y.ZrcN`) on `BETA_VERSION`
   input, preserving stable-branch patch-bump behavior verbatim. Shared validation
   regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$` between both scripts (string-equality
   lockstep check). Lockstep mechanism finalized as **manually-paired beta-branch
   push with explicit `BETA_VERSION` input** (rejected: shared meta-repo VERSION file,
   cross-repo `repository_dispatch`). Documented in `15-LOCKSTEP-PROCEDURE.md` and
   proven via `lockstep-dryrun-fixture.sh` cross-script byte-identity check.

2. **App beta release pipeline (Phase 16 — REL-01, GATE-01).** New
   `firestarter_app/.github/workflows/beta-release.yml` — single-file deliverable
   covering push:beta + workflow_dispatch triggers, inline CI gates (pytest),
   Phase 15 version-bump call, GitHub Pre-release creation, and PyPI publish via
   the existing `publish.yml`. GATE-01 preserved: stable `main`-push behavior
   byte-identical to pre-v1.4.

3. **Firmware beta release pipeline (Phase 17 — REL-02, GATE-02).** New
   `firestarter/.github/workflows/beta-build.yml` — single-file deliverable
   covering push:beta + workflow_dispatch triggers, inline catalog/codegen/Unity/
   PlatformIO gates, Phase 15 version-bump auto-commit, `pio run` build, and
   GitHub Pre-release with `firestarter_*.hex` artifacts per board (Uno +
   Leonardo). GATE-02 preserved: stable `main`-push behavior + existing
   `build.yml` artifacts byte-identical to pre-v1.4.

4. **Beta-aware firmware downloader (Phase 18 — INST-01/02/03/04).** Scope
   amendment 2026-05-20 added a narrow CLI carve-out to make the published beta
   firmware actually installable. `firestarter --install` (no flags) preserves
   byte-identical stable behavior; `--pre` fetches highest PEP 440 pre-release;
   `--firmware-version X.Y.ZbN` pins exact tag via `/releases/tags/{tag}`;
   `firestarter firmware list [--all|--pre|--stable]` enumerates releases.
   `_compare_versions` refactored to PEP 440-safe via `packaging.version.Version`.

5. **Documentation (Phase 19 — DOC-01/02/03).** App + firmware READMEs grew
   Beta channel sections (install via `pip install --pre` + `firestarter --install
   --pre/--firmware-version`/`firmware list`; stability guarantee; issue-reporting
   guidance). Meta-repo `.planning/milestones/v1.4-RELEASE-PROCEDURES.md` documents the
   release-engineer cutting workflow end-to-end, consuming `15-LOCKSTEP-PROCEDURE.md`
   verbatim with corrected workflow filenames.

6. **End-to-end acceptance gate (Phase 20 — E2E-01, MS-01).** Real beta cut in
   both repos following the documented procedure; PyPI shows `<BETA_VERSION>`,
   `pip install --pre` works cleanly, firmware GitHub Pre-release page carries
   the expected per-board `.hex` artifacts, both repos' tags string-equal per
   VER-03, beta-installed app's `firestarter fw -i --pre` fetches the matching
   firmware, and stable-installed app's `firestarter fw -i` (no flags) still
   pulls stable firmware (INST-01 non-regression). Verified via the automated
   `.planning/milestones/v1.4-e2e-verify.sh` (PyPI + GitHub Releases API checks) and the
   6-test operator checklist `20-HUMAN-UAT.md`.

### Stats

| Metric | Value |
|--------|-------|
| Phases | 6 (numbered 15-20) |
| Plans | 10 (Phase 15 = 4, Phase 16 = 1, Phase 17 = 1, Phase 18 = 2, Phase 19 = 1, Phase 20 = 1) |
| Requirements | 16/16 mapped, 16/16 shipped (E2E-01 + MS-01 close on operator green) |
| Meta-repo commits | 56 (`git log --oneline 261a430^..HEAD | wc -l` — from `docs(15): capture phase context` to ship) |
| Firmware sub-repo commits | 13 (`git log --oneline 6c66b29^..origin/beta | wc -l` — from `test(15-01): wave 0 scaffold` to 3.0.0b3 cut) |
| Host sub-repo commits | 17 (`git log --oneline a7390cc^..origin/beta | wc -l` — from `test(15-01): wave 0 scaffold (app)` to 3.0.0b3 cut) |
| Live cut iterations | 3 (`3.0.0b1` → `3.0.0b2` → `3.0.0b3`; b1 cut surfaced 5 substrate fixes E2E-01..05, b2 added firmware.py parser fix E2E-06, b3 added .pyc hygiene) |
| Hardware flash validated | Uno (`/dev/ttyACM0`) + Leonardo (`/dev/ttyACM1`) at `3.0.0b3` via `firestarter fw -i --pre` end-to-end |
| New workflow files | 2 (`firestarter_app/.github/workflows/beta-release.yml`, `firestarter/.github/workflows/beta-build.yml`) |
| Existing workflow files modified | 0 (additive only — GATE-01/GATE-02 preserve stable verbatim) |
| New CLI flags on `firestarter` | 3 (`--pre`, `--firmware-version`, `firmware list`) |
| New planning docs | `.planning/milestones/v1.4-RELEASE-PROCEDURES.md`, `.planning/milestones/v1.4-e2e-verify.sh`, `.planning/milestones/v1.4-archive.sh`, `15-LOCKSTEP-PROCEDURE.md`, `lockstep-dryrun-fixture.sh` |
| Hardware impact | None (software-only milestone; no firmware behavior change, no chip support change) |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Branch-driven beta (push to `beta` branch) | Mirrors current `main` -> stable trigger shape; one mental model | Good (single trigger pattern across both pipelines; operator picks the branch, not a tag) |
| PEP 440 pre-release identifiers (`X.Y.ZbN`/`X.Y.ZrcN`) on same PyPI index | TestPyPI adds operator friction; `pip install --pre` is the cleaner opt-in | Good (single source of truth; stable users unaffected) |
| Lockstep mechanism = manually-paired beta-branch push with explicit `BETA_VERSION` input | Rejected alternatives: shared meta-repo VERSION file (cross-repo write coupling), cross-repo `repository_dispatch` (requires cross-repo PAT with `repo` scope) | Good (no new cross-repo trust surface; operator-readable; `lockstep-dryrun-fixture.sh` proves byte-identity) |
| Firmware GitHub Pre-release with `make_latest: false` | `/releases/latest` API automatically filters pre-releases out -- protects stable-installed `firestarter --install` without code changes | Good (INST-01 non-regression preserved via API filtering, not via brittle client-side logic) |
| Stable pipeline preservation (GATE-01 + GATE-02) | v1.4 is additive plumbing; main -> stable behavior byte-identical to pre-v1.4 | Good (zero regressions; verified by independent main-push smoke during Phase 16/17 development) |
| Scope amendment 2026-05-20: add Phase 18 Beta-Aware Firmware Downloader | Without `--pre`/`--firmware-version`/`firmware list`, published beta firmware was uninstallable via `firestarter` CLI -- half a feature | Good (full operator round-trip: cut beta -> install beta app -> install beta firmware via app) |
| Auto-promotion beta -> stable workflow DEFERRED to v1.5+ | Manual fast-forward merge `beta` -> `main` is sufficient for the milestone's first beta cuts; auto-promotion needs real-world usage data before designing | Revisit (when beta channel sees real use) |

### Known Gaps (deferred — pointers to REQUIREMENTS.md Future Requirements)

Per D-15, the following are explicit pointers to existing entries in `.planning/REQUIREMENTS.md`
section "Future Requirements (deferred past v1.4)":

- **Auto-promotion beta -> stable workflow** — `promote.yml` (or equivalent) that fast-forwards
  `beta` -> `main` and bumps to stable in one CI run. Deferred until beta channel sees real use
  and the promotion pattern stabilizes. See REQUIREMENTS.md Future Requirements.

- **Branch-protection rules on `beta` branch** — accidental force-pushes possible today. Add
  post-v1.4 if accidental-push problems surface. See REQUIREMENTS.md Future Requirements.

- **Signed release artifacts** (sigstore / GPG) — both stable and beta ship unsigned today;
  signing is a dedicated milestone covering both at once. See REQUIREMENTS.md Future Requirements.

- **TestPyPI publishing channel** — explicitly rejected for v1.4 (operator friction); could
  revisit if beta operators report needing isolated install testing. See REQUIREMENTS.md
  Future Requirements.

- **Beta installation metrics / telemetry** — not in scope; future release-ops milestone.
  See REQUIREMENTS.md Future Requirements.

- **Per-board `--pre` fallback** — if Uno has a beta but Leonardo doesn't, INST-02's fallback
  policy is unspecified. Add explicit policy in a later milestone if it surfaces. See
  REQUIREMENTS.md Future Requirements.

- **Cached firmware download / offline install** — app always hits GitHub today; cache layer
  is a separate feature. See REQUIREMENTS.md Future Requirements.

### Carry-forward technical debt

Items surfaced during v1.4 development but explicitly NOT cleaned up here (preserves
v1.4's "additive plumbing only" discipline). Each is documented at the listed
phase-local artifact and may be addressed in a follow-on milestone:

- **Phase 17 WR-01** — pre-existing `build.yml` technical debt (vestigial `setup-python@v4` step, `.editorconfig/**` glob).
- **Phase 18 CR-01..CR-03** — pre-existing `update_version.py` code-review findings (atomic file write, none-return crash, rc-series tag fallback).
- **Phase 15 D-25** — `_dev` / `-dev` suffix conventions in version files (e.g. `2.0.7_dev`, `3.0.0-dev`); silently truncated by the version-file parse regex today.

### Hardware impact

None — v1.4 is CI/CD plumbing + consumer-side CLI + docs only. Firmware semantics
stay at v1.2's 3.0.0-dev baseline. No new chip support, no flash budget movement,
no bench session required for milestone close.

---

## v1.2 — Message-ID Logging Rework (Shipped: 2026-05-19)

**Phases:** 4 (numbered 6-9; Phase 10 closed by this milestone-close workflow) | **Plans:** 32 | **Timeline:** 2026-05-08 → 2026-05-19 (~11 days, 108 meta-repo commits, 104 firmware + 64 host sub-repo commits)

**Delivered:** Replaced every firmware text-prefix log emit (`OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` / `DEBUG:`) with a 1-byte message-ID + raw-byte-param wire protocol driven by a canonical catalog in the meta-repo. The catalog is the single source of truth; codegen emits a C++ header for firmware and a Python module for the host, both regenerated and byte-identity-checked in CI. Old log helpers (`rurp_log`, `rurp_log_P`, `LOG_*_MSG` PROGMEM strings, `log_info_const` / `log_error_format` / `log_warn`) deleted. Leonardo flash 98.7% → **85.4%** (−13.3 pp / −3,792 B of headroom); firmware major bumps to 3.0.0 to enforce lockstep upgrade.

### Flash-Savings Comparison (LMIG-04 acceptance — DOC-02 anchor)

| Snapshot | Leonardo Flash | Uno Flash | SRAM (Uno) | Notes |
|----------|---------------|-----------|------------|-------|
| v1.1 close (baseline) | 28,292 / 28,672 B = **98.7%** | n/a | n/a | Carried v1.1 risk: < 400 B Leonardo headroom |
| v1.2 Phase 6 close | 28,292 B = 98.7% | 26,178 / 32,256 B = 81.1% | 1,593 B | Catalog + helpers landed; no call-sites converted yet (LMIG-01 coexistence proven) |
| v1.2 Phase 7 close | 27,952 B = 97.5% | 25,818 B = 80.0% | 1,593 B | ERROR + WARN + INFO converted (LMIG-02) |
| v1.2 Phase 8 close | 26,096 B = 91.0% | 23,718 B = 73.5% | 1,497 B | State-machine prefix converted (LMIG-03); MSG_DATA_CHUNK streaming (W-04) |
| v1.2 Phase 9 close | 24,500 B = **85.4%** | 22,282 B = 69.1% | 1,497 B | Legacy infra deleted; 3.0.0-dev bump (LFW-03/04, LMIG-04) |
| v1.2 ship | 24,482 B = **85.4%** | 22,262 B = **69.0%** | 1,497 B | Post-ship polish: drop MSG_OK_FW_HANDSHAKE, INFO echo, helper refactor |

### Key Accomplishments

1. **Canonical message catalog + codegen pipeline** (LCAT-01..05, Phase 6 Plan 01)
   — `tools/catalog/messages.toml` is the single source of truth for every log
   message in the system. `tools/catalog/codegen.py` (stdlib-only, deterministic,
   byte-identical re-runs) emits both `firestarter/include/messages.h` (C++) and
   `firestarter_app/firestarter/messages.py` (Python) from the same TOML.
   `sync_to_subrepos.sh` distributes the canonical copy to both sub-repos with
   `diff -q` byte-identity guarantees. CI workflow (`.github/workflows/catalog-
   sync-check.yml` in meta-repo + matching gates in both sub-repos) fails any
   PR that introduces drift.

2. **ID-encoded wire protocol** (LFW-01/02, LHOST-01/02, Phase 6 Plans 02-03)
   — `rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count)`
   replaces the legacy `rurp_log(LOG_*_MSG, char*)` family. Wire frame is
   `MAGIC_PREAMBLE | len_u16 | id | params | crc8 | 0x0A` (W-04 wide len
   added in Phase 8 for MSG_DATA_CHUNK > 255 B). Host decoder in
   `serial_comm.py::_decode_id_frame` handles the same shape with WR-03
   guard for text-format catalog entries.

3. **All firmware log call-sites migrated** (LMIG-02, LMIG-03, LFW-03, Phases 7-9)
   — Every text-prefix emit converted across 13 sub-systems
   (`eprom_operations`, `eeprom_28c`, `flash_intel`, `flash_type_3/4`,
   `hardware_operations`, `memory`, `firestarter` main loop, `dev_tools`,
   `json_parser`, plus catalog/helpers). Composite shapes added for
   `MSG_OK_REV` (P-02 [u8, u8]), `MSG_OK_CFG` (P-03 [u32, u32, u8]),
   `MSG_DATA_CHUNK` (W-04 wide bytes), and the host's sentinel-aware
   `_format_message` renderer.

4. **Legacy log infrastructure deletion** (LFW-03/04, Phase 9 Plan 02)
   — Atomic deletion across 23 files: `logging.h` + `logging.c` outright;
   `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`,
   `LOG_OK_MSG`, `send_ack`, `send_ack_const`, `debug_setup`, `log_debug`,
   plus all four `#ifdef SERIAL_DEBUG` SoftwareSerial blocks + RX_DEBUG/TX_DEBUG
   defines. `#include "logging.h"` swept from 20 sites. Firmware version
   bumped to `3.0.0-dev` (LFW-05) so the host's `major < 3` guard refuses
   pre-v1.2 firmware cleanly.

5. **Phase 9 flash measurement** (LMIG-04, Phase 9 Plan 05 Task 1)
   — Cold-cache PlatformIO measurement on Leonardo + Uno, two delta tables
   in `09-MEASUREMENT.md`: incremental Phase 8 → Phase 9 attribution and the
   milestone-close v1.1 → v1.2 comparison. SC#1 PROGMEM exemption audit
   landed (12 named-symbol declarations: MAGIC_PREAMBLE + CRC8_TABLE +
   json_parser keys + key_parsers[]; 1 inline `F(...)` literal at LFW-05
   bootstrap; zero uncategorized log-purposed PROGMEM hits).

6. **Post-ship polish: protocol simplification + verbose diagnostics**
   (post-Phase-9 cleanup, ~9 commits) — Dropped per-command `MSG_OK_FW_HANDSHAKE`
   composite (P-04) in favour of a plain `MSG_OK_READY` setup-complete ack;
   added 4 single-purpose INFO emits (`MSG_INFO_FW` / `_HW` / `_PHYSICAL_HW` /
   `_CMD` at 0x5A-0x5D) that mirror the dropped handshake content under the
   `FLAG_VERBOSE` runtime gate. Migrated the EXTRA_INFO_LOGGING build-flag
   block (BUF_VAL, TOKEN_COUNT, FLAG_*, BUFFER_SIZE, MEM_SIZE, ADDR_MASK,
   MATCH_LINES) to SERIAL_DEBUG-gated `DBG_*` sub_ids (0x29-0x35) so the
   diagnostics ride the existing DEBUG channel — zero production wire bytes,
   full breadcrumb chain available in `-D SERIAL_DEBUG` builds.

7. **Host probe path + symbolic command names** — Refactored `_probe_port`
   to send a dedicated `CMD_FW_VERSION` pre-probe with two-ack pattern
   handling (skip setup-complete "Ready", parse "OK: FW: ..." for version
   validation) so the host correctly recognizes 3.0.0-dev firmware without
   the dropped FW_HANDSHAKE in every ack. `COMMAND_NAMES` lookup in
   `constants.py` + a `_format_message` branch renders `MSG_INFO_CMD` as
   "Cmd: 0x0f (HW_VERSION)" and the same annotation applies to `DBG_CMD`
   via the new MSG_DEBUG sub_id decoder path.

8. **Helper-function refactor of macro internals** — Factored
   `LOG_ID_U{8,16,24,32}` byte-pack bodies into `rurp_log_id_u{8,16,24,32}`
   helpers in `rurp_serial_utils.cpp`. The macros collapse to one-liners;
   each call site emits a single CALL instead of inlining the byte-array
   build. Net Flash impact small (−20 B Uno / −18 B Leonardo) since
   AVR-gcc was already inlining well — main value is code cleanliness.

### Stats

| Metric | Value |
|--------|-------|
| Phases | 4 active phases (6-9) + Phase 10 milestone-close (this workflow) |
| Plans | 32 (Phase 6 = 6, Phase 7 = 13, Phase 8 = 8, Phase 9 = 5) |
| Meta-repo commits | 108 |
| Firmware sub-repo commits | 104 |
| Host sub-repo commits | 64 |
| Files changed (meta-repo + planning) | 101 files / +26,173 / −63 |
| Firmware LOC | 4,932 (src + include, C++) |
| Host LOC | 5,200 (firestarter/, Python) |
| Catalog LOC | 1,743 (messages.toml + codegen.py) |
| Native tests | 20/20 PASS (test_dispatch + test_messages) |
| Host pytest | 29/29 PASS (test_decoder + test_fwguard + others) |
| Hardware-bench verified | Uno + Leonardo at 3.0.0-dev, verbose + SERIAL_DEBUG modes |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| ID width = 1 byte | < 100 distinct strings; generous headroom for future growth | ✓ Good (60 catalog entries + 41 DBG sub_ids = 101 total; comfortable) |
| Raw byte params, no type tags on wire | Catalog declares each ID's shape; type tags would waste bytes | ✓ Good (Phase 8 W-04 added `bytes` variable-length shape without protocol break) |
| Codegen output committed to both sub-repos | Operators can build without running codegen first; CI drift gate catches changes | ✓ Good (zero drift incidents; tags ship reproducibly) |
| Phased migration (infra → batched convert → delete last) | Allows both old + new paths to coexist during migration; safer than big-bang | ✓ Good (each phase shipped a working build; LMIG-01 coexistence proven Phase 6) |
| Lockstep upgrade (no backwards compat) | Wire format change too invasive to support both; FW major bump enforces | ✓ Good (3.0.0-dev gate works; host pre-v1.2 refusal clean) |
| MSG_OK_FW_HANDSHAKE → plain MSG_OK_READY (post-ship polish) | Per-command FW echo over-specified; INFO emits handle verbose case better | ✓ Good (saved ~5 wire bytes per command; INFO echo restored visibility) |
| EXTRA_INFO_LOGGING → SERIAL_DEBUG | Build-flag gate is coarser than macro-level; DBG channel already SERIAL_DEBUG-gated | ✓ Good (10 fewer INFO catalog entries; debug breadcrumbs richer) |
| Helper functions for byte-pack | Deduplicate ~10-line macro bodies | ⚠️ Revisit (Flash savings ~20 B — AVR-gcc was already optimizing well; kept for code cleanliness) |

### Known Gaps / Hardware-Pending UAT

Recorded in [STATE.md `## Deferred Items`](.planning/STATE.md). All four items bundle on a single chip-seated W27C512 bench session:

- **Phase 09 Plan 05 Task 3** — chip-seated W27C512 write + readback on both boards (Plan 09-05 hardware UAT)
- **Phase 08 SC#2 / SC#3** — chip-seated UAT carried forward from Phase 8 close (same scope)
- **Phase 08 HUMAN-UAT.md** — 2 pending scenarios (same scope, different artifact)
- **v1.1 debug session `fm1608-fresh-chip-baseline`** — parked since 2026-05-18; unrelated to v1.2 scope (needs different Uno R3 to unblock)

Known deferred items at close: **4** (see STATE.md Deferred Items).

### v1.1 Items Carried Forward (still open after v1.2)

- v1.1 Phase 4 — FM1608 byte-0 read bug (parked, needs different Uno R3)
- WARNING-4 — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json`
- v1.1 DOC-01 — v1.1 milestone close (Phase 5 of v1.1 deferred)

---

## v1.0 — Protocol-Aware Programming Architecture (Shipped: 2026-05-11)

**Phases:** 13 | **Plans:** 22 | **Timeline:** 2026-05-08 → 2026-05-11 (4 days, 66 commits)

**Delivered:** Replaced the guessing-based chip-type pipeline with an explicit
algorithm-first architecture where minipro `protocol_id` flows authoritatively
from upstream XML through the database, wire protocol, and firmware dispatch —
and the firmware executes exactly that algorithm for every chip in the 743-entry
DB. Two safety-critical hazards closed (BLOCKER-1, BLOCKER-2, WARNING-5).

### Key Accomplishments

1. **Algorithm-first wire protocol** (REQ-SER-01, REQ-FW-01) — `firestarter_handle_t`
   carries an explicit `algorithm` integer; `memory.cpp::configure_memory`
   protocol-prefix dispatch covers all 13 KNOWN_PROTOCOLS (0x05/0x06/0x07/0x08/
   0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x35/0x39); legacy `type` enum retained
   as fallback only. Verified by 15/15 Unity dispatch tests on `[env:native]`
   plus `check_dispatch.py` PASS across all 743 chips.

2. **Database pipeline canonicalized** (REQ-DB-01..05, Phases 01 + 11) — Single
   `build_db.py` fetches `infoic.xml` from upstream minipro at runtime,
   parses deterministically to `minipro_complete_db.json` with explicit
   `algorithm` integer, decoded-millivolt `vpp`, correct DIP28 variant splitting
   (`DIP28_27512` / `DIP28_27256` / `DIP28_2764`), unknown-protocol chips
   skipped with WARN. Legacy `parse_db.py`, `infoic.xml`, `verified.txt`,
   `database_generated.json`, `pin-maps.json` all removed.

3. **Five new firmware handlers** — `configure_eprom` (UV-EPROM STD/QUICK/LEGACY,
   Phase 03), `configure_flash3` (AMD-style sector erase, Phase 04),
   `configure_flash_intel` (Intel command-register flash, Phase 05),
   `configure_eeprom28c` (AT28C SDP-disable + DQ7-polling page write, Phase 06),
   `configure_sram` (5V SRAM safe no-op, Phase 12).

4. **Pre-write safety stack** (REQ-SAF-01/02/03, Phases 03 + 07) — VPP ADC
   compare before first write pulse on UV-EPROM and 28C-EEPROM paths;
   chip-ID validation for Intel + AMD + UV-EPROM (`A9_VPP_ENABLE` sequence
   for 27Cxxx); blank check across Flash/EEPROM write inits gated by
   `!FLAG_SKIP_BLANK_CHECK`.

5. **Static-pin and address-bus correctness** (REQ-FW-05/06, Phase 10) —
   `static_high_mask` end-to-end (`pinouts.json` static-high-pins → wire JSON
   static-high → `bus_config_t.static_high_mask` → `mem_util_remap_address_bus`
   unconditional OR); replaces hardcoded `pins == 24` heuristic for tied-high
   CE2/NC pins. Dead `READ_WRITE == WRITE_FLAG` condition replaced with the
   physical-reality `if (handle->pins < 32)` plus VPE_TO_VPP/A16-sharing comment.

6. **CLI hardware-compatibility surface** (REQ-UX-01/02, Phase 09) —
   `firestarter search` flags chips with no valid pinout via `[!]` marker;
   `firestarter info --adapter` prints a DIP-mirrored two-column physical-pin →
   RURP-signal table derived entirely from `pinouts.json`, enabling adapter
   wiring without source-code reference.

7. **Three safety-critical close-out phases** —
   - **Phase 11** consolidated the build pipeline to `build_db.py` and removed
     all legacy artifacts (REQ-DB-05; byte-identical regeneration verified).

   - **Phase 12** closed BLOCKER-1 (277 chips fell through to "Memory type
     0x%02x not supported" before the protocol-prefix dispatch) + BLOCKER-2
     (52 SRAM chips routed to `configure_eprom` with 12V VPP regulator on 5V
     parts). Fixed at three layers: firmware dispatch + Python `_ALGO_MEM_TYPE`
     table + `build_db.py` SRAM tagging.

   - **Phase 13** closed WARNING-5 (23 DIP28_2764 5V EEPROMs mistagged in
     upstream minipro as `algorithm=0x07` would have applied 12V to socket
     pin 1 = A14 address line on write). Data-layer-only fix via inline
     3-predicate override in `build_db.py` flipping these chips to `0x0D`
     (`EEPROM_POLL` → `configure_eeprom28c`, pure 5V path with zero VPP
     regulator engagement). Permanent regression guard `_28C_EEPROM_HAZARD_PINOUT`
     in `check_dispatch.py`.

### Stats

- **Files modified:** firmware (Arduino C++) + Python CLI submodules; meta-repo
  tracks `.planning/` only

- **Verification:** Phase 11 (4/4), Phase 12 (8/8), Phase 13 (8/8) formally
  verified end-to-end. Phases 01-10 verified by independent
  `INTEGRATION-CHECK.md` + Phase 12 `check_dispatch.py` regression on the full
  743-chip DB.

- **E2E flows shipped:** `write -e W27C512`, `write -e AM29F040`,
  `write -e SST39SF040`, `erase -s 0x10000 -e SST39SF040`, `write -e 6116`
  (SRAM safe), `write -e AT28C256` (now safe via Phase 13), `write -e AM28F010`
  (Intel — see Known Gaps), `info <chip> --adapter`, `python tools/build_db.py`.

### Key Decisions

- **Database source:** minipro `infoic.xml` via `build_db.py` (not hand-curated
  JSON). Outcome: ✓ — 743 chips covered without per-chip curation overhead.

- **Wire protocol:** New explicit `algorithm` integer field (minipro
  `protocol_id`); `type` retained as legacy fallback. Outcome: ✓ — all 13
  KNOWN_PROTOCOLS dispatched correctly; no regressions.

- **Firmware dispatch:** Protocol-prefix `if-return` block per KNOWN_PROTOCOLS
  entry in `configure_memory`, mem_type chain retained only for legacy
  user-override DB entries. Outcome: ✓ — verified by Phase 12 `check_dispatch.py`.

- **Packages in scope:** DIP 24, 28, 32 only. Outcome: ✓ — SMD/PLCC/serial
  filtered cleanly by `build_db.py`.

- **WARNING-5 fix:** Data-layer override in `build_db.py` rather than
  per-chip firmware switch. Outcome: ✓ — preserves the "algorithm is
  authoritative" contract while routing around the upstream minipro
  classification error for 23 5V EEPROMs.

### Known Gaps (accepted as tech debt for v1.1)

Captured from `.planning/milestones/v1.0-MILESTONE-AUDIT.md` (status:
`gaps_found`). Audit-time score: 4/18 SATISFIED, 13 PARTIAL (verification-gap
only), 1 UNSATISFIED.

- **REQ-SAF-01 partial — Intel-flash write path** (WARNING-1): `flash_intel_write_init`
  (`firestarter/src/proms/flash_intel.cpp:47-62`) enables `REGULATOR |
  P1_VPP_ENABLE` and delays 500ms before the first write pulse, but never calls
  `rurp_read_voltage_mv()` ADC compare. The UV-EPROM and 28C-EEPROM paths
  satisfy REQ-SAF-01; the Intel-flash family (39 chips, algo=0x10, highest VPP
  in firmware) does not. **Severity: WARNING.** Fix scope: 1-2 lines in
  `flash_intel.cpp`; pattern mirrors `eprom_check_vpp`.

- **Phases 01-10 lack formal VERIFICATION.md files** (verification-gap on 13
  requirements). Wiring is independently verified by `.planning/INTEGRATION-CHECK.md`

  + Phase 12 `check_dispatch.py` (743/743 chips PASS) + Phase 13 hazard guard
  (0 violations) + 15/15 Unity dispatch tests. By the workflow rule "missing
  VERIFICATION.md = unverified phase", 10 of 13 phases remain structurally
  unverified. Optional retroactive `/gsd-validate-phase` runs would close.

- **WARNING-2 — 28C chip-ID forward-compat hazard**:
  `eeprom_28c.cpp::eeprom28c_write_init` ignores `handle->chip_id`. Vacuous
  today (zero 0x0D chips in regenerated DB carry `chip_id_value`) but breaks
  REQ-SAF-02 the moment a user-override or upstream DB change populates
  chip_id for an AT28C-family chip.

- **WARNING-3 — wire-protocol key naming**: JSON `"vpp"` key now carries
  millivolts (was volts) — semantic overload. Recommend renaming wire key to
  `"vpp_mv"`. `firestarter_app/CLAUDE.md` example currently shows a phantom
  `"vpp_mv"` key that is not emitted.

- **WARNING-4 — test-script drift**: `firestarter_test.sh:31` and
  `write_test.sh:17` reference the deleted `database_generated.json`. Breaks
  the documented hardware-integration E2E flow.

- **`build_db.py` robustness**: Bare `except:` at lines ~138-186 (silent chip
  drops + KeyboardInterrupt swallow). `requests.get` lacks `raise_for_status()`
  and `timeout` (non-200 upstream silently overwrites DB). Pre-existing,
  out-of-scope of Phase 11 lock.

- **Lost `verified` field**: `minipro_complete_db.json` no longer carries the
  `verified` field; `database.py::get_eproms(verified=True)` silently returns
  empty. Carried in `11-VERIFICATION.md` follow_ups.

- **DIP24/DIP28/DIP32 `static-high-pins` coverage**: Only DIP24 variants
  populated in `pinouts.json` today. DIP28/DIP32 quirk pins (CE2, JEDEC-tied
  NC) could be added in a future phase (INFO-3).

- **`DIP24_2732` pinout** never appears in regenerated DB (no 24-pin
  variant=0x01 chips survive the DIP/memory-type filter on current
  `infoic.xml`). May be intentional; flag for review.

### Hardware Verification

Not performed in this milestone — no RURP shield available in the dev
environment. All verification was structural (code/DB/dispatch tests). The
documented hardware integration tests (`firestarter_test.sh`, `write_test.sh`)
should be re-run against a physical board before declaring the four
chip-family canon (W27C512, 29F040, SST39SF040, AT28C256) hardware-validated.

---
