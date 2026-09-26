# v1.30 Honesty Ledger — SDP Surface Retirement & Behavioral Lock Proof

**Milestone:** v1.30 — SDP Surface Retirement & Behavioral Lock Proof
**Phases:** 131 (Gate Hardening & CI Parity), 132 (Retire `dev sdp` & Discharge the mypy Debt), 133 (SDP
Leg Mechanism), 134 (The Plan-Derived SDP Oracle in `dev test`), 136 (Dev-Tools Channel Gating), 136.1
(SDP Partition Provenance), 137 (Close — this phase). **The 135 slot is deliberately vacant** —
`write --sdp-relock` (RELOCK-01…06) was deferred out of scope on 2026-08-03 and filed as ROADMAP
Backlog **999.28**; the phase number was not reused.
**Host-only milestone: no firmware change, no dual-repo lockstep, no `.hex` re-cut.**
**Submodule commit:** `firestarter_app` HEAD **`cc036e8dc3cd77bbdfc7ec5190d79cdb172153c7`** — captured
live via `git -C /workspaces/firestarter_app rev-parse HEAD` at this plan's own execution
(2026-08-05), never reused from a prior document's citation. This plan's own task (137-03) touches no
file inside `firestarter_app` — the pointer is unchanged from the value the meta repo's own tracked
gitlink already carries (`git ls-tree HEAD firestarter_app`, confirmed identical at this plan's start).
**Oracle:** software-only — the Phase 116 native register trace harness (`pio test -e native`, the
firmware submodule's own Unity binary) is **unreachable from the host** (Evidence Ceiling narrowing
1, restated below); `firestarter_app`'s host pytest suite (**1508 passed**, re-run live this plan,
2026-08-05, in `tools/ci_replica_venv.sh`'s numpy-free venv, never the devcontainer's ambient
Python 3.12); source-scan gates (`.planning/phases/137-.../check_permitted_claims.py`, plan 137-01,
and `firestarter_app/tools/check_diagnostic_report_claims.py`, plan 137-02). Restated in full below,
verbatim, per this document's own required caveat: no AT28C silicon was tested during this milestone.
**Generated:** 2026-08-05, plan 137-03.

**Composes with (cross-reference only — no data copied):**
- `.planning/REQUIREMENTS.md` §"⚠ Evidence Ceiling" — the permitted/not-provable wording this ledger
  distils into claim classes, reproduced verbatim below
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-RECORD.md` — §1/§3/§4/§5/§6/§7,
  the source for six of this ledger's nine corrections and the seven non-vacuity obligations
- `.planning/phases/133-sdp-leg-mechanism/133-RECORD.md` — §3 Criterion 5, the registry-count
  correction (6 policed + 6 declared non-registries, not "eight")
- `.planning/phases/136.1-sdp-partition-provenance/136.1-RECORD.md` — Finding 1 (PROV-05's already-
  satisfied premise), Finding 5 (the "committed NOTHING" process failure), §5 (the operator's original
  "no ICs refused" request vs. the measured answer)
- `.planning/phases/134-the-plan-derived-sdp-oracle-in-dev-test/134-VERIFICATION.md` — finding F-01,
  the independent verifier's own re-derivation of the LEG-02 population
- `.planning/v1.30-OPERATOR-BATCH.md` §C — items C-1 and C-3, restated here per this plan's own
  must-have, not only in the operator batch file
- `.planning/v1.16/ledger/PROTOCOL-LEDGER.md` — the `0x0D` row's status. **Referenced and verified
  here, never edited** (matching v1.22's D-09 discipline): `git status --porcelain -- .planning/v1.16/ledger/`
  confirmed empty at this plan's execution.

---

## The ceiling, quoted verbatim

Reproduced from `.planning/REQUIREMENTS.md` §"⚠ Evidence Ceiling" so no downstream reader has to
re-derive it:

> No AT28C part has ever been in operator inventory and protocol `0x0D` stays `UNVERIFIED`.
>
> **Provable this milestone:** the *plan derivation* (43 ALLOW chips get four steps, 41 REFUSE get four
> NA steps carrying reasons — measurable today with zero hardware); the *read-back comparison logic*
> and every degenerate-input arm of it, in native envs; the SDP command *emission* only to the extent
> the host can observe it.
>
> **NOT provable this milestone:** the causal claim *"the lock inhibited the write."* That is reachable
> only on real silicon — i.e. only from a community `dev test` report, which **by design does not gate
> this milestone's close.**

**Both named narrowings, verbatim, never smoothed over:**

1. **The Phase 116 ground-truth trace harness is UNREACHABLE from the host.** It is a PlatformIO
   `[env:native]` Unity binary in the *firmware* repo (`test/native/avr/test_sdp_harness/`,
   `test_eeprom28c_sdp/`), and its recorder hooks `rurp_write_data_buffer` / `rurp_set_control_pin`.
   The host repo has no bus stub at all. So "emission proof" here means what `tests/conftest.py`'s
   `build_frame` / `_FakeSerial` / `make_comm` can assert over a scripted wire — **not** a bus trace.
2. **A locked die is unrepresentable in either repo's stubs.** Both model the bus, never the die's
   protection state. No fixture can simulate real inhibition; fixtures can only pin the host's
   *response* to a scripted read-back.

**Note on the ceiling's own inherited "four-step"/"four NA step" wording, quoted faithfully above and
corrected below (claim class 2):** the requirement text this ceiling paragraph quotes predates
LEG-04's two-transition-direction mandate. The leg that actually derives and ships is **six** steps,
not four. The ceiling's *evidentiary* content — what is and is not provable — is unaffected by this;
only the step-count numeral inherited from the pre-LEG-04 design is stale, and this ledger states both
readings rather than silently reconciling them.

**No AT28C silicon was tested during this milestone.** Every figure below has a software artifact as
its subject — a derived plan, a pytest exit code, a source-scan result, a live database re-derivation —
never a silicon observation.

---

## Status / claim key

Reused from v1.22's `122-LEDGER.md`, unchanged:

- **`PERMITTED`** — a wording backed by a measured, re-runnable software artifact (a test, a source
  scan, a live re-derivation).
- **`CONTEXT-ONLY`** — measured and cited for context, but explicitly not a gate.
- **`COMMUNITY-CORROBORATED`** — a real-silicon datapoint supplied by a third party, provenance stated
  plainly, not independently reproducible on this bench.
- **`FORBIDDEN`** — the ceiling's forbidden claim shape. Appears in this ledger only as a citation of
  what is *not* claimed, never as prose asserting it.

---

## The claim classes

Every figure below was **re-measured live this plan** (2026-08-05, from `/workspaces/firestarter_app`,
`tools/ci_replica_venv.sh`'s venv, `-o addopts=""`), not copied from a citation. Where a figure agrees
with a prior document, that agreement is stated as a re-confirmation, not assumed.

| Class | Permitted wording | Evidence (measured, source) | Explicitly does NOT prove |
|---|---|---|---|
| **1. Plan derivation, full 84-chip `0x0D` population** `PERMITTED` | For each of the 43 SDP-capable ALLOW chips, `dev test` derives — with **no new command-line option** — a six-step SDP leg from `sdp_capability()`; for each of the 41 REFUSE chips, it derives six NA/SKIPPED steps carrying the refusal reason. | `134-RECORD.md` §1/§3 Criterion 1. **Re-measured live**: a fresh Python pass over the live `chip_database.json` via the production `sdp_capability_for_entry` predicate gives **ALLOW=43, REFUSE(protocol-0x0D-only)=41, TOTAL(0x0D)=84** — independently recomputed, not copied. `test_derive_plan_allow_population_emits_six_supported_ops` + `test_derive_plan_refuse_population_emits_six_na_steps_with_reason`: 2 passed. | That the leg holds on real silicon (Evidence Ceiling); that any of the 84 `0x0D` chips has ever been bench-tested this milestone. |
| **2. The SDP leg is SIX steps, not four** `PERMITTED` | The derived leg is, in order: `write-baseline-b` · `write-baseline-a` · `sdp-lock` · `write-inhibited` · `sdp-unlock` · `write-restored` — single-sourced via `_SDP_LEG_STEP_ORDER`. | `134-RECORD.md` §3 Criterion 1 / §4 correction 1 (D-06). **Both readings stated, not silently reconciled**: the ROADMAP's own criterion text, and `REQUIREMENTS.md`'s own prior LEG-01/LEG-02 wording, say "four-step"/"four NA steps" — that wording **predates LEG-04's own two-transition-direction mandate** and omits `write-restored`, the *only* step producing evidence the part was left writable again on a family whose protection state cannot be read back. `REQUIREMENTS.md`'s LEG-01 text already carries this correction in-line. | Anything about silicon — this is a mechanism-shape correction only. |
| **3. The oracle is read-back equality, never an exit code** `PERMITTED` | An unexpected write success reports `BAD`, never `SKIPPED`/`NA`/`OK`. | `134-RECORD.md` §3 Criterion 2. **Re-measured live**: `test_leaked_lock_exits_1` + `test_mixed_bad_and_marginal_exits_1_not_2`, both against the real CLI end to end — 2 passed. | Silicon acceptance of the write; only the host-observable dispatch logic. |
| **4. The exit-code precedence bug is fixed, and named as a real defect this milestone caught in its own code** `PERMITTED` | Before D-14 landed, `marginal` (exit 2) numerically outranked `BAD` (exit 1) via a naive `max()`, so a run with both a leaked lock and any marginal step exited 2 — laundering the milestone's headline finding into the inconclusive code. `_EXIT_CODE_PRECEDENCE = (1, 2, 0)` fixes it. | `134-RECORD.md` §4 correction 2 (D-14). **Re-measured live**: `_EXIT_CODE_PRECEDENCE: tuple[int, ...] = (1, 2, 0)` read directly at `cli_handlers.py:2026`; both named tests pass (see class 3). | That this defect was ever shipped to a community reporter — it was caught and fixed inside this same milestone, before any release. |
| **5. Every one of the SEVEN known routes to a non-running oracle is tested, not six** `PERMITTED` | R1–R6 are research's own laundering routes (`TestLaunderingRoutesR1R2SyntheticChipId`, R3/R4, R5/R6, all tested). The **SEVENTH** — named explicitly so a reader does not mistake "six laundering-route tests" for exhaustive coverage — is the baseline gate itself (`_baseline_closes_sdp_gate`, D-08/D-20), added by 134-04 beyond research's own R1–R6. | `134-RECORD.md` §5; `134-04-SUMMARY.md`. Named in a module comment beside the R1–R6 test family (`test_chip_test.py`, confirmed live: "THESE TWO ARE NOT EXHAUSTIVE EITHER: a seventh route..."). | That seven is itself exhaustive — it is the count of routes *known and tested*, not a claim of completeness. |
| **6. The chip-ID destructive gate is structurally vacuous for the entire SDP-ALLOW population** `PERMITTED`, with an explicit non-claim | **All 43 measured ALLOW chips have `chip-id == 0`** (re-measured live this plan: a fresh pass over every ALLOW-classified DB entry found zero with a nonzero `chip-id`). R1/R2 are driven through a synthetic nonzero-`chip-id` fixture *because* the real gate is unreachable in production today. | `134-RECORD.md` §4 correction 7 (D-17). **No artifact may say "the leg is gated by chip ID."** Re-measured live: `grep -rniE "gated by chip[- ]id" firestarter/ tests/` returns **0** hits tree-wide. | That chip ID meaningfully protects any shipped chip today — it protects nothing today; the fixture exists to prove the *mechanism* would work if it ever became reachable. |
| **7. LEG-02's tested REFUSE population is 703 chips — a superset of the 41 the ROADMAP names, not the 41 itself** `PERMITTED`, citation corrected | The test enumerates **every non-ALLOW entry in the live database, across all protocols** — a strict superset of the 41 protocol-`0x0D` REFUSE chips. **Re-measured live this plan** (2026-08-05): a fresh DB pass gives **ALLOW=43, REFUSE(full DB)=703, TOTAL DB=746**; restricting to protocol-`0x0D` only gives **43 ALLOW / 41 REFUSE / 84 total**, confirming the ROADMAP's "41" figure is real, just scoped narrower than the actual tested population. | `134-RECORD.md` §4 correction 8; `134-VERIFICATION.md` finding F-01 (found by an independent verifier who recomputed rather than trusted the citation, 2026-08-04). The behavior is proven **more** broadly than originally claimed, not less — but the earlier "41" numeral describing the test's own population was wrong, corrected in place in both `REQUIREMENTS.md` and `134-RECORD.md`. | That the test is scoped to protocol `0x0D` only — it is not; it is the full non-ALLOW database. |
| **8. The auto-unlock coupled-decision tripwire (P-21)** `PERMITTED`, with a load-bearing non-claim | `dev sdp disable`'s removal (RETIRE-01, Phase 132) is safe **only because** `write`'s auto-unlock stays default-on: `skip_sdp_unlock: bool = False` in `cli_handlers.py`'s `_build_op_flags` (**re-confirmed live this plan** at `cli_handlers.py:319`). Recorded as the named test `test_dev_sdp_removal_is_safe_only_because_auto_unlock_is_default_on` (`tests/test_write_skip_sdp_unlock.py:328-395`, re-read live this plan), not merely a sentence in a note — two legs, both required: a capability-refused part gets the bit auto-set, a capability-ALLOWED part does not (proving the auto-set is conditional, not blanket). | `132-RECORD.md` RETIRE-07/D-14. Companion tripwire comments live at the D-04 auto-set site in `cli_handlers.py`'s `write()` and at `FLAG_SKIP_SDP_UNLOCK`'s definition in `constants.py`. | **Explicit non-claim**: if that default is ever revisited, this decision (RETIRE-01's removal safety) must be revisited alongside it — this test's failure IS the record of that dependency breaking. |
| **9. `0x0D` stays `UNVERIFIED`** `PERMITTED` | Zero chips changed `support_status`; zero AT28C silicon on this milestone's bench. | Cross-reference `.planning/v1.16/ledger/PROTOCOL-LEDGER.md`'s `0x0D` row (line 27: `EEPROM-POLL`, `configure_eeprom28c()`, **UNVERIFIED**, "No on-hand silicon. Rep chip: AT28C256") — referenced only, confirmed unedited by this milestone (see header). | That any `0x0D` chip has been bench-validated — none has. |
| **10. PROV-05's premise was already satisfied — by an earlier phase, in an earlier milestone** `PERMITTED`, stated as a finding not an embarrassment | `doc/lockable-proms.md`'s AT28C16/64/256 SDP-capability distinction was corrected **before v1.30 was scoped** — by **Phase 121 plan `121-13`, commit `c3c9424`**, five phases and one milestone number earlier. Phase 136.1 did not re-author the fix; it verified the correction's presence, confirmed (whole-tree grep) no stale copy exists anywhere else in `firestarter_app`, and shipped the durable automated gate (`tests/test_lockable_proms_doc_claims.py`) that did not exist before. | `136.1-RECORD.md` Finding 1. | That Phase 136.1 discovered or fixed this defect — it did not; the defect was already gone. Phase 136.1's genuine contribution is the *gate*, not the correction. |
| **11. PROV-01…06 changed provenance, never verdicts** `PERMITTED` | The 43 ALLOW / 41 REFUSE / 84 `0x0D` partition is unchanged across all six PROV requirements — re-verified **nine** independent times across Phase 136.1's four plans plus this ledger's own re-measurement (class 1 above). The operator's original request, at Phase 136.1's inception, was **"no ICs refused."** The honest answer this milestone delivers instead: `infoic.xml` says 41 of the 84 protocol-`0x0D` parts have **no SDP command decoder** in minipro's own upstream data — and on those parts the SDP sequence is **not inert**; its bytes land as data at the bus-truncated magic addresses. Forcing them to ALLOW would corrupt parts and report locks that never existed. | `136.1-RECORD.md` §1 ("six separate times... plus three more"), §5 ("Context worth stating"). | That any chip's ALLOW/REFUSE verdict moved — none did, across any PROV plan. What moved is *provenance*: an in-repo, reproducible, gated derivation path from upstream `infoic.xml` data to the committed verdict, replacing a one-time hand transcription. |

---

## Mechanism corrections recorded here, not restated in `REQUIREMENTS.md`

Per the discipline already applied at Phase 122's LOCK-04/LOCK-06/HOST-04 and Phase 121's D-06/D-17:
when a requirement's stated mechanism turns out narrower or different, the intent is satisfied, the
correction is recorded in the phase record (cited below, not re-derived), and the requirement text is
left alone.

1. **`MIN_CHECKED_SOURCE_FILES = 120` is a FLOOR, not a spent budget** — Phase 133's own D-15 reading
   was inverted; Phase 134 was free to add test modules throughout (checked count moved 124→126, both
   above the floor); the real, spendable budget was the mypy headroom (unmoved at 2 for the entire
   phase). `134-RECORD.md` §4 correction 3.
2. **`_DECLARED_REGISTRY_COUNT` never existed as a name** — the real names are
   `_POLICED_REGISTRY_COUNT = 7` / `_DECLARED_NON_REGISTRY_COUNT = 6`; of the seven Phase-133-authored
   SDP-op exemption rows standing at Phase 133's close, only the two `derive_plan` rows were
   dischargeable by Phase 134, not five. `134-RECORD.md` §4 correction 4.
3. **The stale-row guard does not itself catch a redundant-but-still-valid row** — discharging the 8
   TEMPORARY exemption rows was a discipline obligation enforced by a grep-able marker
   (`TEMPORARY — discharged by plan N`), never an automatic gate outcome. `134-RECORD.md` §4
   correction 5.
4. **The two shipped AT28C256 `0x0D` sweep tests were repaired, not weakened** — `derive_plan`'s
   emission change necessarily altered both tests; a new stateful, SDP-lock-aware operator double
   makes a genuinely-all-OK twelve-step sweep genuinely all-OK, no skip, no narrowed assertion.
   `134-RECORD.md` §4 correction 6.
5. **Also from Phase 133** — LEG-15's own inherited "eight previously fail-open registries" is
   measured-wrong; the real breakdown is **6 policed registries + 6 declared non-registries**
   (`_dispatch_multi_run`'s inner branches were a real registry P-23's original ten-row table missed
   entirely; `tools/parse_devtest_issue.py` has zero op-string constants and was never a registry at
   all). `133-RECORD.md` §3 Criterion 5.
6. **`n_ran = 6`, not the design record's stated `5`, for a gated ALLOW chip's banner** —
   `write-baseline-a` is never itself gated and reports OK against a dead-write-path double (its own
   expected read-back is pattern A); this is the true minimum achievable ran-count for this shape, not
   a fixture quirk. Re-measured live this plan: `test_count_applicable_sdp_gated_allow_chip_ratio_drops`
   + 2 companion pins, 3 passed, `m_applicable=10`, `n_ran=6` confirmed unchanged. `134-RECORD.md` §4
   (D-20 discrepancy list).
7. **A coverage reduction shipped in this same phase, and is named plainly here rather than left
   implicit in a plan SUMMARY**: plan 137-02 added `exclude = ["^tests/fixtures/"]` to
   `[tool.mypy]` (Rule 3 fix — the required `planted_unparsable.py` fixture's genuine `SyntaxError`
   otherwise aborted mypy's whole directory walk). Checked source files fell **132 → 129**
   (re-measured live this plan: `Found 33 errors in 13 files (checked 129 source files)`). Still above
   the `MIN_CHECKED_SOURCE_FILES = 120` floor, and justified by the mypy-abort risk it prevents — but
   it is a genuine reduction, and the floor exists to notice exactly this class of change, not to wave
   it through silently. `pyproject.toml:173`; `137-02-SUMMARY.md`.

---

## Process failures recorded here, not only technical ones

A ledger that admits only code defects is not an honesty ledger. Three process failures this
milestone's own record keeps visible, per this plan's own instruction:

1. **"Committed NOTHING," measured from `git status` alone.** Mid-Phase-136.1, an orchestrator
   dispatch note told a plan's executor that a crashed prior attempt "committed NOTHING," having
   checked only `git status` in the meta repo. Two correct, complete submodule commits (`c9f98b8`,
   `31b5d74`) already existed in `firestarter_app`, made by the crashed session before it died — only
   the meta-repo bookkeeping (gitlink bump, requirement ticks, SUMMARY, STATE update) was actually
   missing. **A clean working tree does not mean no commits were made** — the submodule carries its
   own independent commit history that `git status` in the meta repo cannot see. `136.1-RECORD.md`
   Finding 5.
2. **The AT28C64 "curation gap" misreading, reproduced from part-number familiarity.** Early in this
   milestone, Claude's own initial claim that AT28C64's SDP refusal looked like a curation gap was
   **wrong** — it reproduced a documented, previously-carried error rooted in part-number familiarity,
   the same shape of error `doc/lockable-proms.md` §17 once carried before Phase 121 corrected it. The
   REFUSE verdict is `infoic.xml`'s own answer (no SDP command decoder on those parts), not a gap to be
   closed by relaxing the gate — and forcing it to ALLOW would corrupt real hardware.
   `.planning/v1.30-OPERATOR-BATCH.md` §D, item D-1.
3. **A validation approval asserted an artifact did not exist while it did, moments later.**
   `134-VALIDATION.md`'s original approval text stated no `gsd-plan-checker` verdict existed for
   Phase 134. A concurrent `/gsd-plan-phase 134` planning session was still running when that approval
   was written; it committed its own verdict (`## VERIFICATION PASSED`, 11/11 plans, zero blockers,
   zero warnings, commit `b0e489fa`) minutes later. The original, now-false text was **kept visible in
   the file rather than deleted**, with a correction appended above it, specifically so this ledger
   could see what was claimed and when. `134-VALIDATION.md` (lines ~142-163).

---

## Negative space — what this milestone chose not to prove

A close that lists only wins reads as overclaiming even when every individual claim is true.

- **The causal claim "the lock inhibited the write"** — not provable this milestone (the Evidence
  Ceiling, quoted above). No fixture in either repo can simulate real inhibition.
- **`build_db_diff`'s `ladder_state` regression** (operator batch **C-1**) — a real,
  previously-undocumented finding from Phase 134 (once the SDP leg is genuinely reachable end to end,
  a genuinely-passing ALLOW chip's all-OK run routes `ladder_state` to `_LADDER_NONE` rather than
  `_LADDER_COMMUNITY_REPORTED`, because `classify_fingerprint`'s four-bucket design has no dedicated
  "perfect match" bucket). **Disposition recorded in `137-DECISION.md`, authored later in this same
  phase** (this plan is wave 3; the disposition plan is wave 4) — no disposition is invented here.
  `134-RECORD.md` §6 residual 4; `.planning/v1.30-OPERATOR-BATCH.md` §C item C-1.
- **The Evidence Ceiling itself** (operator batch **C-3**) — restated here in full, not softened: "the
  lock inhibited the write" is not provable this milestone; no fixture simulates real inhibition; real
  silicon is missing with no fallback. Permanent residual, not a defect to be scheduled away.
  `.planning/v1.30-OPERATOR-BATCH.md` §C item C-3.
- **gh#20's underlying AT28C256 write-path defect** — filed as backlog `999.29`, `Owner: henols`
  (`134-RECORD.md` §6 residual 6; `.planning/todos/pending/at28c256-write-path-failure-gh20.md`).
- **RELOCK-01…06** — deferred to Backlog **999.28**; v1.30 ships the deletion (`dev sdp`, Phase 132)
  but **withdraws** the deliberate-protection surface and ships **no replacement**. This is a
  withdrawal, never a migration to a command (`write --sdp-relock`) that does not exist in this
  release.
- **The mypy watermark ratchet** — remains unowned. Headroom re-measured live this plan: **33/35**.
  **Corrected here rather than left implicit**: the error count was **32** (3 of headroom) at Phase
  132's own close (`132-RECORD.md` residual 2), then moved to **33** (2 of headroom) during Phase 133
  (`133-RECORD.md` residual 4) and has stayed **33/35** unmoved from Phase 133 through this plan's own
  live re-measurement — not "unmoved since Phase 132" as an earlier draft of this bullet read (checked-
  file count moved 124→126→130→132→129 across the milestone per correction 7 above, but the *error*
  count and the *watermark* have not moved since Phase 133).
- **The Ctrl-C forfeited report** (Phase 133 D-07, carried through Phase 134) — after an interrupt
  mid-leg, the chip's unlock is attempted but the production caller's `results = run_plan(...)`
  assignment never completes, so there is no `dev test` report at all on that path. Mitigated by an
  up-front notice, not closed. No owner within this milestone.
- **`.planning/codebase/TESTING.md`** — remains stale (asserts "no Python unit tests" against a tree of
  90+ test files). Owner: `/gsd-map-codebase`, not this milestone.

---

## What no test, gate, or review in this phase can close

Reproducing `122-VALIDATION.md`'s three-way split in this ledger's own voice for v1.30:

- **Mechanically checkable.** Every claim-gate sub-claim from both `check_permitted_claims.py` (meta,
  plan 137-01) and `firestarter_app/tools/check_diagnostic_report_claims.py` (plan 137-02); the full
  `firestarter_app` pytest suite (**1508 passed**, re-run live this plan); the mypy watermark gate
  (**33/35**, headroom 2, re-run live this plan); the 43/41/84 SDP partition (re-derived live this
  plan, three independent ways: full-DB pass, protocol-0x0D-scoped pass, and the chip-ID-zero sweep).
  Cheap, deterministic, re-runnable.
- **Requires the blocking operator review (CLOSE-06).** Whether the gh#12 follow-up reply's prose is
  *honest*, not merely free of banned strings — a string scan cannot detect an implied overclaim,
  judge whether describing the withdrawal (no `write --sdp-relock` in this release) reads as a
  migration, or weigh tone. **A green claim-scan does NOT by itself satisfy the honesty ledger
  discipline** — this is the claim-gate's own module docstring's explicit non-claim, restated here.
- **Inherently unverifiable in-phase, at a sampling rate of zero, permanently, until real silicon is
  on the bench.** The ceiling's own not-provable causal claim (quoted in full above — not repeated
  here, to avoid this document's own claim scanner mistaking a citation for an assertion, exactly as
  `122-LEDGER.md` records for its own equivalent forbidden-claim citation); `t_BLC` accepted by a real
  die; `0x0D` graduating from `UNVERIFIED`; whether any of the 84 chips' ALLOW/REFUSE placement is
  correct per family (`infoic.xml`'s own answer is reproducible, not bench-verified). No test in this
  milestone changes this, and none was designed to.

---

*Phase: 137-close-honesty-ledger-claim-gate-gh12-followup*
*Written: 2026-08-05, plan 137-03, against `firestarter_app` submodule commit `cc036e8` and meta-repo
`REQUIREMENTS.md`/`134-RECORD.md`/`133-RECORD.md`/`136.1-RECORD.md` as they stood at this plan's own
execution.*
