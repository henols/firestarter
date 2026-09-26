---
phase: 122
slug: close-honesty-ledger-community-ask-release-decision
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-30
settled: 2026-07-30 (Plan 122-13)
---

# Phase 122 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `122-RESEARCH.md` § Validation Architecture (all commands executed live 2026-07-30).

**Phase shape caveat:** most of this phase's output is *prose* (honesty ledger, two public issue
comments, two release bodies). The central design question is therefore **which claims a machine can
sample and which cannot**. That three-way split is stated explicitly below and is load-bearing — a
green scan must never be presented as satisfying success criterion 4.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (host)** | `pytest` 8.x + `syrupy` snapshots, via `pip install -e .[test]` |
| **Config file (host)** | `/workspaces/firestarter_app/pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.ruff]`, `[tool.mypy]`) |
| **Framework (firmware)** | Unity via PlatformIO (`pio test -e native`), 17 suites |
| **Config file (firmware)** | `/workspaces/firestarter/platformio.ini` (`default_envs = uno, uno328pb, leonardo`) |
| **Standalone gates** | `firestarter_app/tools/*.py` — plain scripts, exit-code contract |
| **Quick run command** | `cd /workspaces/firestarter_app && python3 -m pytest tests/test_sdp_db_invariant.py -q && python3 tools/diff_db.py && python3 tools/check_no_community_support_status_write.py` |
| **Full suite command** | `cd /workspaces/firestarter_app && python3 -m pytest -q` (**1134** tests — see the baseline correction below) **+** `cd /workspaces/firestarter && pio test -e native` (141 cases) **+** the eleven nine-row non-regression commands |
| **Estimated runtime** | quick ~6 s · full ~140 s + nine-row gate |

> **⚠ BASELINE CORRECTION (2026-07-30, wave 3).** The app pytest baseline recorded below and in
> `122-RESEARCH.md` § Validation Architecture as **1150 passed** is **wrong**. The true figure at the
> pre-merge branch HEAD (`c3c9424`, Phase 121's own final commit) is **1134**, which is what Phase 121
> independently recorded. Plan 122-04 observed 1134 on the merged tree and flagged the discrepancy.
>
> **This was investigated as a possible merge-induced test loss and cleared.** Independent proof: the
> set of unique `test_*` function names on the merged tree is **identical** to the set at the pre-merge
> branch HEAD (**1033 each**, `diff` empty) — so the wave-2 `--ours` resolution dropped nothing. The 24
> test names present on `origin/beta` but absent from the branch were **already absent before the
> merge**; Phase 121's `dev test` zero-option redesign removed or renamed them by design (e.g.
> `test_clean_destructive_run_exits_0`, `test_on_tty_destructive_confirm_gates`, the `non_destructive_*`
> family — all superseded when `--destructive` was removed and three-valued `write_scope` replaced it).
> `beta` carries 906 unique test names to the branch's 1033, consistent with being 75 commits behind.
>
> **Use 1134 as the baseline.** Do not treat 1134 as a regression against 1150.

**Live baselines established 2026-07-30 (pre-merge):** app pytest **1134 passed** (corrected — see above) · firmware native
**141/141** · firmware script tests **8 passed** · all eleven nine-row commands **PASS** · catalog
three-way identity clean · mypy 1/35 · four `0x0D` pinouts at 35/19/18/12 with a 43/41 ALLOW/REFUSE
split reproducing STATE.md exactly.

---

## Sampling Rate

- **After every task commit:** the quick run command (~6 s). Additionally, for any commit touching a
  closing artifact, the forbidden-phrase scan (Wave 0).
- **After every plan wave:** the eleven nine-row commands + full app pytest + `pio test -e native`.
- **Immediately after the inbound merge, before the outbound merge:** the full set again. **This is
  the load-bearing sample** — CONTEXT constraint 2 exists so `beta` never sees an unproven tree, and
  rows 9a/9b scan the very file (`submit.py`) that was conflicted.
- **Before any comment posts:** channel verification (constraint 3) and the D-16 blocking operator
  wording review (constraint 4). Neither is a test; both are blocking.
- **Before `/gsd-verify-work`:** full suite green + both channels verified.
- **Max feedback latency:** 6 s (quick) / ~140 s (full).

---

## Per-Task Verification Map

> Requirement-level map lifted from `122-RESEARCH.md`. Task IDs are filled by the planner; the
> executor updates Status. `❌ W0` marks the one Wave 0 dependency.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| Task 1 | 122-04 (re-verified 122-13) | 3 | CLOSE-01 | — | `0x0D` stays `UNVERIFIED` — never edited | gate | `grep -c '^\| \`0x0D\` .*\*\*UNVERIFIED\*\*' .planning/v1.16/ledger/PROTOCOL-LEDGER.md` → `1` | ✅ | ✅ green |
| Task 1 | 122-04 (re-verified 122-13) | 3 | CLOSE-01 | — | 84-chip count + `chip_id_check` unchanged | unit | `python3 -m pytest tests/test_sdp_db_invariant.py -q` | ✅ | ✅ green (4 passed) |
| Task 1 | 122-04 (re-verified 122-13) | 3 | CLOSE-01 | — | zero `support_status` change / DB identity | gate | `python3 tools/diff_db.py` (exit 0) | ✅ | ✅ green |
| Task 1 | 122-04 (re-verified 122-13) | 3 | CLOSE-01 | — | no code path writes `support_status` | gate | `python3 tools/check_no_community_support_status_write.py` | ✅ | ✅ green |
| Task 1-2 | 122-04 (re-verified 122-13) | 3 | CLOSE-01 | T-122-03 | the four above hold **on the merged tree** (constraint 6) | integration | re-run all four after the inbound merge, before the outbound merge — 122-13 re-ran again after the outbound push | ✅ | ✅ green |
| Task 2 | 122-04 (re-verified 122-13) | 3 | CLOSE-01 | T-122-03 | cross-repo non-regression survives the merge | integration | the eleven nine-row commands | ✅ | ✅ green (11/11) |
| Task 3 | 122-12 (re-verified 122-13) | 10 | CLOSE-02 | — | both comments posted, issues still OPEN | gate | `gh issue view {11,12} --json state,comments -q '{state:.state,n:(.comments\|length)}'` — `state == OPEN`, `n` incremented | ✅ | ✅ green (13/9, both OPEN) |
| Task 3 | 122-12 (re-verified 122-13) | 10 | CLOSE-02 | T-122-01 | posted text == reviewed draft | gate | deliver with `--body-file <committed path>`, then `gh issue view … -q '.comments[-1].body'` compared to the committed file | ✅ | ✅ green (byte-equal modulo GitHub's one trailing newline, re-diffed in 122-13) |
| Wave 0 (122-01); default-target run 122-11, re-run 122-13 | 122-01 / 122-11 / 122-13 | 0 | CLOSE-02 | T-122-01 | **no forbidden phrasing** in any closing artifact | gate | `check_permitted_claims.py` (no args) over `122-LEDGER.md`, both release-note files, both comment drafts | ✅ (corrected from ❌ W0 — the scanner and its planted-fixture pytest were built in Wave 0 / Plan 122-01, and 122-13 re-ran the default-target invocation: `PASS: scanned 122-LEDGER.md, 122-RELEASE-NOTES-fw.md, 122-RELEASE-NOTES-app.md, 122-GH11-COMMENT.md, 122-GH12-COMMENT.md`, exit 0) | ✅ green |
| Task 2 | 122-11 | 9 | CLOSE-02 | T-122-06 | wording is *honest*, not merely non-matching | **manual** | **D-16 blocking operator wording review** — verdict "Approve — accept the C-5 correction" | n/a | ✅ green (human judgement recorded verbatim) |
| Task 2 | 122-02 (ordering proof completed 122-07 §13, re-verified 122-13) | 1 | CLOSE-03 | T-122-04 | decision recorded before any push | gate | `122-DECISION.md` commit timestamp (`d5c49d4` @ 13:03:38Z) strictly earlier than both outbound merge/push timestamps (14:24:48Z / 14:30:00Z) | ✅ | ✅ green |
| Task 1-2 | 122-08 (re-verified 122-13) | 7 | CLOSE-03 | — | b14 live on PyPI | gate | PyPI JSON API contains `3.0.0b14` (read the **observed** tag — see A3) | ✅ | ✅ green |
| Task 1-2 | 122-08 (re-verified 122-13) | 7 | CLOSE-03 | — | b14 firmware prerelease carries 3 `.hex` | gate | `gh release view <observed-tag> --repo henols/firestarter --json assets` → 3 names | ✅ | ✅ green |
| Wave 0 (122-01); delivered 122-12, re-verified 122-13 | 122-01 / 122-12 / 122-13 | 0 | CLOSE-03 | T-122-01 | both bodies carry the permitted claim + silicon caveat | gate | `gh release view … -q '.body'` non-empty (re-confirmed byte-equal to the frozen draft in 122-13) **and** passes the default-target `check_permitted_claims.py` scan | ✅ (corrected from ❌ W0 — same scanner as CLOSE-02's row, both release-note files are two of its five default targets) | ✅ green |
| — | — | — | — | — | SDP works on real AT28C silicon | **UNVERIFIABLE** | **none — this is the forbidden claim; sampling rate zero, permanently, by design** | n/a | n/a |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## What can and cannot be sampled — stated explicitly

**Mechanically checkable (14 rows above).** Every CLOSE-01 sub-claim, every CLOSE-03 sub-claim, and
CLOSE-02's *delivery* facts (posted, still open, byte-equal to the reviewed draft). Cheap,
deterministic, re-runnable — sample at every commit that could move them.

**Requires the blocking operator review (D-16).** Whether the prose is *honest*, not merely free of
banned strings. A scan cannot detect *"we've addressed this"* used to mean *"this is fixed"*, cannot
judge whether omitting the `DIP24_2816` refusal misleads `No-Hazmats`, and cannot weigh tone. This is
why D-16 is a hard gate, not advisory. **A green claim-scan must never be presented as satisfying
success criterion 4.**

**Inherently unverifiable in-phase.** That silicon enters or leaves the protected state; that `tBLC`
is met as accepted by the die; that gh#11's symptom is gone; that the capability partition is correct
per family. No test, gate or review closes these. `0x0D` stays `UNVERIFIED` precisely because they are
open. The single asymmetry (D-10): the **defect** is now community-corroborated on real AT28C256
silicon; the **fix** is not. **Sampling rate for this class is zero, permanently, by design.**

---

## Wave 0 Requirements

- [ ] **Forbidden-phrase / permitted-claim scanner** over the closing artifacts (`122-LEDGER.md`,
      both release-note files, both comment drafts) — the only mechanizable half of criterion 4.
      Contract: exit 1 on any case-insensitive match of a forbidden set (e.g. `verified fixed`,
      `works on`, `confirmed working`, `silicon[- ]verified`, `now works`, `should now work`,
      `proven on`) **and** exit 1 if the required silicon caveat is absent from each artifact.
- [ ] **Planted violating fixture + a test proving the scanner exits 1 on it** — mandatory. This
      project's anti-hollow discipline (GATE-01): a scanner that has never failed is the hollow
      GATE-03 debt repeating.

*No other gaps.* All four CLOSE-01 mechanisms, the nine-row gate, both full suites, and every
`gh`/PyPI verification command exist and were executed green on 2026-07-30. No framework install, no
`conftest.py`, no fixture scaffolding needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Closing prose is *honest*, not merely non-matching | CLOSE-02, criterion 4 | Judgement — a string scan cannot detect an implied overclaim, a misleading omission, or wrong tone (D-16) | Operator reads both comment drafts + both release bodies + `122-LEDGER.md` and approves wording **before** anything posts. Blocking. |
| `No-Hazmats`' answer is size-class-correct | CLOSE-02 | Research C-5/A4: all 19 `DIP24_2816` (2K×8) chips are **REFUSED** by the SDP allow-set; D-14's "should now work" is an overclaim | Confirm the reply is phrased by size class, not by an assumed part number, and states the refusal |
| `pdr0663` firmware version / exception name (A1) | CLOSE-02 | The GitHub API truncates the comment exactly where both appear | Either drop both from the reply (safe on app 1.3.44 alone) or re-read the full comment in a browser before the wording review |
| Both channels resolve publicly | CLOSE-03 | Third-party propagation delay; PyPI/GitHub eventual consistency | Fresh-environment `pip install --pre firestarter` resolves the observed tag; `gh release view` returns it |
| `beta` push is authorized | CLOSE-03 | Outward-facing and irreversible | Recorded accept/avoid/cleanup decision committed **before** the push; operator confirms |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (the claim scanner **and** its planted fixture) — built in Plan 122-01, its own paired anti-hollow test re-run by Plan 122-13 (`test_check_permitted_claims.py -q` → 7 passed)
- [x] No watch-mode flags
- [x] Feedback latency < 140 s
- [x] The three-way split above is reflected in the plans — no plan claims a scan satisfies criterion 4. Restated once more, plainly, at phase close: the green `check_permitted_claims.py` run is the mechanizable half of ROADMAP criterion 4 only; the D-16 operator wording review (Plan 122-11) is the judgement half; and "SDP works on real AT28C silicon" has a sampling rate of zero, permanently, by design — no AT28C part was on the bench during this milestone.
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** Settled 2026-07-30 by Plan 122-13, after individually re-verifying every row originally marked `❌ W0` against the real landed file (`check_permitted_claims.py`) and command names (both rows corrected in place above — the scanner exists, runs with no arguments, and both affected rows' release-note files are two of its five default targets).
