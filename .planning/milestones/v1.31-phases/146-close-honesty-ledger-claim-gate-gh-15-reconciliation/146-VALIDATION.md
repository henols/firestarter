---
phase: 146
slug: close-honesty-ledger-claim-gate-gh-15-reconciliation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-17
---

# Phase 146 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `146-RESEARCH.md` § Validation Architecture (measured 2026-08-17). Every command
> below was executed by the researcher; the runtimes are measured, not estimated.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` (present in both sub-repos; the phase's own new suite is plain `pytest`, hosted in the phase directory) |
| **Config file** | firmware: **none** (no `pytest.ini` / `pyproject.toml` / `setup.cfg` / `tox.ini` / `conftest.py` at repo root). host: `pyproject.toml` `[tool.pytest.ini_options]`, `testpaths = ["tests"]`, `addopts = "-ra -q"`. Phase-local suite: none — invoked by path |
| **Quick run command** | `python3 -m pytest .planning/phases/146-close-honesty-ledger-claim-gate-gh-15-reconciliation/test_check_claims_v131.py -o addopts="" -q` |
| **Full suite command** | firmware: `cd /workspaces/firestarter && python3 -m pytest tests -o addopts="" -q` — baseline **314 passed / 19.17 s**<br>host: `cd /workspaces/firestarter_app && python3 -m pytest tests -o addopts="" -q` — baseline **1590 passed / 30 snapshots / 258.92 s** |
| **Estimated runtime** | phase-local suite ~5 s; firmware ~19 s; host ~259 s |

**Hard precondition — commit before running either sub-repo suite.**
`firestarter/tests/test_flash_path_record_sync.py:1247` and
`firestarter_app/tests/test_py32_flash_map_host.py:391` both assert the firmware repo's whole-repo
`git status --porcelain == ""`. A mid-change diff turns both suites RED for a reason that has nothing
to do with the change.

**`-o addopts=""` is mandatory on the host**, whose `addopts` is `-ra -q`; a second `-q` suppresses
the count line, and the count is the evidence.

---

## Sampling Rate

- **After every task commit:** the phase-local suite (~5 s) plus whichever content locators that
  task's artifact affects. The claim gate itself is instant — run it on every artifact edit.
- **After every plan wave:** the claim gate against every artifact that exists so far (the
  all-or-nothing failure is **expected** until the fifth artifact lands — record it as expected, not
  as a red), the D-13 doc checker once the doc edits land, and
  `.planning/phases/130-*/check_record_corrections.py` once the `⚠ CORRECTION` blocks land.
- **Before `/gsd-verify-work`:** commit, then **both** sub-repo suites at their measured baselines
  (314 / 1590), the claim gate green on all five artifacts, the D-13 checker green, the 130 record
  gate green, and the full plant-and-revert transcript recorded.
- **Max feedback latency:** 5 s (phase-local); 259 s at the phase gate.

---

## Per-Task Verification Map

Task IDs are assigned by the planner. The requirement→behavior→command rows below are the contract
each task's `<automated>` verify block must draw from; the planner MUST map every row to at least one
task and carry the command verbatim.

| Req | Behavior | Test Type | Automated Command | File Exists | Status |
|-----|----------|-----------|-------------------|-------------|--------|
| CLOSE-01 | every forbidden pattern fires on a planted fixture | unit (subprocess) | `pytest …/test_check_claims_v131.py -k planted -x` | ❌ W0 | ⬜ pending |
| CLOSE-01 | every per-file caveat rule fires; unknown basename gets the full set | unit | `pytest …/test_check_claims_v131.py -k caveat -x` | ❌ W0 | ⬜ pending |
| CLOSE-01 | fail-closed on a missing target; never-vacuous on an empty seam; argv beats env | unit | `pytest …/test_check_claims_v131.py -k "closed or vacuous or precedence" -x` | ❌ W0 | ⬜ pending |
| CLOSE-01 | `_DEFAULT_TARGETS` resolve inside **this** phase dir and all carry the `146-` prefix | unit (introspection) | `pytest …/test_check_claims_v131.py -k default_targets -x` | ❌ W0 | ⬜ pending |
| CLOSE-01 | armed and green against all five real artifacts | integration | `python3 …/146-check-claims.py` (no argv, no env) → exit 0, `PASS:` naming all five basenames | ❌ W0 | ⬜ pending |
| CLOSE-01 | seen to fail on a planted violation in a **real** artifact, byte-identical after revert | manual-recorded transcript | plant → `rc_planted == 1` naming the file → revert → `rc_after == 0` + blob SHA identity, recorded in `146-CITATIONS.md` | ❌ W0 | ⬜ pending |
| CLOSE-02 | the ledger leads with the 6.25 V ceiling and the asymmetric bench coverage | automated locator | `awk` from first `##` to second `##`, assert `6\.25` and both skipped-protocol names present; negative control = delete the lead section → 0 | ❌ W0 | ⬜ pending |
| CLOSE-02 | every permitted claim has a non-claim (no empty non-claim cell) | automated locator | row-wise check over the claim-class table; non-vacuity leg: emptied table → exit 1 | ❌ W0 | ⬜ pending |
| CLOSE-02 | all twelve carry-forwards appear with Owner text | automated locator | count rows matching the twelve item names → **12**; negative control: delete one → 11 | ❌ W0 | ⬜ pending |
| CLOSE-03 | all five topics present in the changed docs, zero forbidden phrases | unit (D-13 checker) | `python3 …/146-check-close03-docs.py` → exit 0, naming every scanned file | ❌ W0 | ⬜ pending |
| CLOSE-03 | the D-13 checker cannot pass vacuously | unit | empty/repointed target list → exit 1; a missing doc → exit 1 | ❌ W0 | ⬜ pending |
| CLOSE-03 | the `messages.toml` change produced the measured diff shape | integration | zero-line diff in `messages.h`; one-line diff in `messages.py`; three tomls share one SHA | ❌ W0 | ⬜ pending |
| CLOSE-03 | the stale `doc/PROTOCOLS.md` §1.3 sentence is gone | automated locator | `grep -c 'Phase 141 replaces it' firestarter/doc/PROTOCOLS.md` → **0**; `grep -c 'eprom.cpp:159-179'` → **0** | ✅ **runnable today — true RED (1 and 1)** | ❌ red (expected) |
| CLOSE-03 | `firestarter/CLAUDE.md`'s native-env total is corrected | automated locator | `grep -c '71 cases' firestarter/CLAUDE.md` → **0**; `grep -c '79 cases'` → **≥1** | ✅ **runnable today — true RED (1 and 0)** | ❌ red (expected) |
| CLOSE-04 | all nine **original** boxes appear, each with exactly one of the three dispositions | automated locator | per-box count over `146-GH15-RECONCILIATION.md` → 9 rows; disposition vocabulary constrained to the three literals; negative control: a tenth row → fail | ❌ W0 | ⬜ pending |
| CLOSE-04 | F-140-07's correction is present in the posted text | automated locator | assert both `100 seconds` and `t_w(PR)` appear | ❌ W0 | ⬜ pending |
| CLOSE-04 | the posted comment byte-equals the frozen text | integration | fetch-back: `wc -c` delta `== +1`, one added blank line at EOF, zero other diff lines | ❌ W0 | ⬜ pending |
| CLOSE-04 | gh#15 state after the post | integration | `state == OPEN`, comments `1 → 2`, `labels == []`, `lastEditedAt == null` (**GraphQL only** — not exposed by `gh issue view --json`) | ❌ W0 | ⬜ pending |
| CLOSE-04 | the seven corrections landed and the record gate still passes | integration | `146-CORRECTIONS.md` row count; `python3 .planning/phases/130-*/check_record_corrections.py` → exit 0 | ✅ 130 gate exists, passes today (baseline recorded) | ⬜ pending |
| CLOSE-05 | both bodies are version-agnostic | automated locator | `grep -c '3\.0\.0b'` both bodies → **0**; placeholder token appears exactly once per file | ❌ W0 | ⬜ pending |
| CLOSE-05 | both bodies describe the behavior change and `--pulse-us` | automated locator | assert `--pulse-us` and a per-byte-loop phrase in each; negative control on a stripped copy | ❌ W0 | ⬜ pending |
| CLOSE-05 | the wording review actually happened | manual, blocking | operator's typed authorization recorded verbatim; `autonomous: false`; the **resolved** `check auto-mode` value recorded | ❌ W0 — manual by nature | ⬜ pending |
| all | no push / merge / tag / workflow dispatch occurred | integration | `git rev-list --count @{u}..HEAD` unchanged in all three repos across the phase; negative-argv audit table | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `146-check-claims.py` — the D-11 all-or-nothing gate over the five closing artifacts (CLOSE-01)
- [ ] `test_check_claims_v131.py` — the eleven-leg pytest suite (CLOSE-01, D-12 first half)
- [ ] `fixtures/clean_control.md`, `fixtures/clean_control_second.md` — both must carry the caveats the
      rule set demands, or the clean-control leg fails for the wrong reason
- [ ] `fixtures/planted_forbidden_claim.md`, `fixtures/planted_proven_unqualified.md`,
      `fixtures/planted_missing_caveat.md` — label-specific plants, **probed before** the acceptance
      criterion is written
- [ ] `146-check-close03-docs.py` — the D-13 five-topic + forbidden-phrase checker (CLOSE-03)
- [ ] the plant-and-revert transcript in `146-CITATIONS.md` (CLOSE-01, D-12 second half)
- [ ] the ledger / reconciliation / release-body content locators, **each with a negative control** —
      a locator that cannot fail proves nothing
- [ ] Framework install: **none required** — `pytest` is present in both sub-repos and the phase-local
      suite needs no config file

**Two locators are runnable today and are true REDs** (`Phase 141 replaces it` → 1; `71 cases` → 1).
Record them RED *before* the edit and GREEN after: that satisfies "seen to fail for the right reason"
without needing a plant, and it is the cheapest available proof that the locator is wired to the file.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Operator wording review of both release bodies | CLOSE-05 | Judgement of outward-facing prose is not mechanizable; the mechanizable half (version-agnosticism, `--pulse-us` presence, forbidden phrases) is covered by locators above | Present both bodies in full; capture the operator's typed verdict verbatim into the plan record; `autonomous: false`; record the **resolved** `check auto-mode` value, not the intent |
| Authorization to post the gh#15 comment | CLOSE-04 | One outward-facing, non-revertible act to a public repo | Freeze the artifact → record blob SHA + byte count → claim gate green → **blocking** operator authorization → single `gh issue comment` → byte-verify the fetched-back comment. `updatedAt` bumps on comment creation so it is **not** a body-edit oracle; use `lastEditedAt` via GraphQL. `sed -e '$a\'` cannot cancel GitHub's appended trailing newline |
| Plant-and-revert against a real closing artifact | CLOSE-01 | Mutating a tracked, committed artifact and restoring it byte-exactly is a recorded transcript, not a repeatable test | Record `rc_before` / `rc_planted` / `rc_after` plus the pre- and post-revert blob SHAs; assert byte identity |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or a Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references above
- [ ] No watch-mode flags
- [ ] Feedback latency < 5 s for the phase-local suite
- [ ] Every locator has a negative control recorded alongside its GREEN
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
