---
phase: 85
slug: datasheet-acquisition
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-25
---

# Phase 85 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Doc/asset-only phase: validation is a single structural shell assertion over the
> produced `datasheets/` tree (no unit-test framework — SAFE-05 forbids new deps and
> the existing native/host harness is not exercised here).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | shell assertion (`bash` + coreutils `find`/`grep`/`head`) — no unit-test framework |
| **Config file** | none |
| **Quick run command** | `bash datasheets/datasheets-check.sh` (run from `firestarter/` repo root) |
| **Full suite command** | `bash datasheets/datasheets-check.sh` (single structural check) |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bash datasheets/datasheets-check.sh` (cheap — re-runnable after each download batch)
- **After every plan wave:** Run the same check
- **Before `/gsd-verify-work`:** `datasheets-check: PASS` must print, exit 0
- **Max feedback latency:** ~2 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 85-01-01 | 01 | 0 | SAFE-05 | T-85-SC1 | downloaded files are real PDFs (`%PDF` magic), not HTML masquerade | structural | `bash datasheets/datasheets-check.sh` | ❌ W0 (author script) | ⬜ pending |
| 85-02-01 | 02 | 1 | DSHEET-01 | — | N/A | structural | `bash datasheets/datasheets-check.sh` | ❌ W0 | ⬜ pending |
| 85-02-02 | 02 | 1 | DSHEET-02 | — | N/A | structural | `bash datasheets/datasheets-check.sh` | ❌ W0 | ⬜ pending |
| 85-03-01 | 03 | 2 | DSHEET-03 | — | N/A | structural | `bash datasheets/datasheets-check.sh` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Wave/Plan IDs above are indicative — the planner sets the authoritative task IDs; the automated command is identical for every task because the single structural check covers all four requirements.*

---

## Wave 0 Requirements

- [ ] `datasheets/datasheets-check.sh` — authored fresh (no existing equivalent). Covers DSHEET-01 (every on-hand chip's expected PDF exists, non-empty, `%PDF` magic), DSHEET-02 (each no-silicon bucket dir has ≥1 non-trivial PDF), DSHEET-03 (README exists; every README-referenced filename maps to a real file; phantom `0x35`/`0x39` and infeasible `0x11`/`0x2A`/`0x2B`/`0x2C` exclusions are named in README and have NO folder), and SAFE-05 (`git diff --name-only` touches only `datasheets/**`). Reference implementation in `85-RESEARCH.md` §"Reference check script".
- [ ] No framework install needed — `bash`, `find`, `grep`, `head` are all present.

*The check script is itself a `datasheets/` artifact, so committing it does not violate SAFE-05.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Each PDF is the *correct* part's datasheet (not just a valid PDF of something else) | DSHEET-01, DSHEET-02 | Content identity (right title-page part number) can't be asserted by magic-byte check alone; operator spot-reviews the README provenance table | Open 2–3 PDFs, confirm the title-page part number matches the README row; confirm substitute/representative flags are honest |
| Representative exemplar picks for the 6 no-silicon buckets are reasonable | DSHEET-02 | Editorial judgement (D-06 "best-documented exemplar") | Operator reviews the no-silicon picks in README against the bucket algorithm |

---

## Validation Sign-Off

- [ ] All tasks have an `<automated>` verify (the structural check) or Wave 0 dependency (the check script itself)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify — satisfied (every task runs the same check)
- [ ] Wave 0 covers all MISSING references (`datasheets-check.sh` is the sole Wave 0 item)
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter (set by planner once the script task is in a plan)

**Approval:** pending
