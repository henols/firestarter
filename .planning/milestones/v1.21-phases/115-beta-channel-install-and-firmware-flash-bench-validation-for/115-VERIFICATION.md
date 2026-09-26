---
phase: 115-beta-channel-install-and-firmware-flash-bench-validation-for
verified: 2026-07-27T00:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
---

# Phase 115: Beta Install & Firmware-Flash Bench Validation — Community Onboarding Verification Report

**Phase Goal:** A community member on a fresh machine can go from zero to a working beta stack and start running `dev test <chip>` — proven on real hardware for every bench board (Uno, Leonardo, uno328pb) and captured as a community-facing doc. VALIDATION + DOCS only.
**Verified:** 2026-07-27
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Step 0 — both channels public at 3.0.0b11 | ✓ VERIFIED | `pip index versions firestarter --pre` → highest = `3.0.0b11`, no stray `3.0.1`. `gh release view 3.0.0b11 --repo henols/firestarter --json isPrerelease,isDraft,assets` → `isPrerelease=true, isDraft=false`, assets = `firestarter_uno.hex`, `firestarter_uno328pb.hex`, `firestarter_leonardo.hex`. `gh release view 3.0.0b11 --repo henols/firestarter_app` → `isPrerelease=true`. All independently re-checked live in this verification session, not just SUMMARY claims. |
| 2 | Per board: fresh-venv `pip install --pre firestarter` installs 3.0.0b11, `firestarter --version` reports it | ✓ VERIFIED | `chip-test/onboard-{uno,leonardo,uno328pb}.md` each show `auto_capture.host_version: "3.0.0b11"` and a verdict-table row `firestarter --version | OK | reports 3.0.0b11` for all three boards. |
| 3 | Per board: bare `fw -i` auto-routes to `--pre`, downloads board `.hex`, avrdude flash+verify OK | ✓ VERIFIED | Each evidence record shows `"resolved_channel": "pre"`, the correct `firestarter_<board>.hex` (uno/leonardo/uno328pb), and a distinct avrdude success line with timing (7.94s / 5.35s / 6.20s) and distinct serial ports (`/dev/ttyACM1`, `/dev/ttyACM0`, `/dev/ttyUSB0`) — not templated/copy-pasted values. |
| 4 | Per board: post-flash `fw` reports beta version + correct board, one live op (`hw`) succeeds, NOT a chip write | ✓ VERIFIED | Each record: `fw` → `3.0.0b11, controller: {uno,leonardo,uno328pb}`; `hw` → live hardware-revision read OK. All three records carry `"is_smoke_only": true, "chip_write_performed": false`. |
| 5 | Community-facing onboarding doc in firestarter_app, stranger-oriented, per-board commands, avrdude prereq, ttyACM gotcha, correct `.hex` per board, dev-test hand-off | ✓ VERIFIED | `firestarter_app/doc/beta-testing-install.md` (committed `204df99`, pushed to v1.21): avrdude prereq section, per-board `.hex`/avrdude-flag table, `/dev/ttyACM*` shuffle section, hand-off link to `community-validation.md`, draft-first caveat removed and replaced with a bench-validated note. README pointer confirmed: exactly 1 occurrence of `beta-testing-install` in `firestarter_app/README.md` (no matrix duplication). |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_app/doc/beta-testing-install.md` | Finalized stranger-facing onboarding doc | ✓ VERIFIED | Exists, substantive (204 lines), wired (README pointer + community-validation.md hand-off), content matches bench findings. |
| `firestarter_app/README.md` pointer | Single non-duplicating link | ✓ VERIFIED | 1 occurrence of `beta-testing-install`, no per-board matrix duplicated. |
| `chip-test/onboard-uno.md` | Uno evidence record (HARD gate) | ✓ VERIFIED | Present, PASS, all 7 steps OK. |
| `chip-test/onboard-leonardo.md` | Leonardo evidence record (HARD gate) | ✓ VERIFIED | Present, PASS, all 7 steps OK. |
| `chip-test/onboard-uno328pb.md` | uno328pb evidence record (best-effort) | ✓ VERIFIED | Present, PASS (best-effort; instability history did not recur), honestly recorded. |
| Meta-repo submodule gitlinks | Bumped off PINNED b10 to b11 commits | ✓ VERIFIED | `git ls-tree HEAD firestarter firestarter_app` → `0fd7992` / `204df99`; committed as `4d8b33c` "bump submodule gitlinks off PINNED b10 to 3.0.0b11". `firestarter/include/version.h` = `3.0.0b11` at `0fd7992`; `firestarter_app/firestarter/__init__.py` = `3.0.0b11` at `204df99`. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `beta-release.yml`+`publish.yml` (app) | PyPI `firestarter 3.0.0b11` | manual `gh workflow run` dispatch, operator-authorized | ✓ WIRED | `pip index versions --pre` confirms live artifact. |
| `beta-build.yml` (firmware) | GitHub prerelease `.hex` assets | manual `gh workflow run` dispatch, operator-authorized | ✓ WIRED | `gh release view` confirms 3 assets present. |
| README.md | `beta-testing-install.md` | markdown pointer link | ✓ WIRED | Line 129: `[doc/beta-testing-install.md](doc/beta-testing-install.md)`. |
| `beta-testing-install.md` | `community-validation.md` | hand-off link (§7) | ✓ WIRED | `grep -q community-validation` passes; link present with `dev test <chip>` framing. |
| Fresh-venv installed app | `--pre` channel | `_maybe_auto_route_to_pre` (D-23/D-24), exercised live | ✓ WIRED | All 3 bench records show `"Beta app detected — defaulting to --pre"` auto-route firing on real installs. |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|--------------|------------|-------------|--------|----------|
| ONBOARD-01 | 115-02, 115-04, 115-05/06/07 | Fresh-venv `--pre` install + version report, per board | ✓ SATISFIED | PyPI live check + 3 bench records. |
| ONBOARD-02 | 115-02, 115-03, 115-05/06/07 | Bare `fw -i` auto-route + board `.hex` flash+verify, per board | ✓ SATISFIED | GitHub prerelease live check + 3 bench records. |
| ONBOARD-03 | 115-05/06/07 | Post-flash smoke test (not a chip write), per board | ✓ SATISFIED | 3 bench records, `chip_write_performed: false` in all. |
| ONBOARD-04 | 115-01, 115-08 | Community-facing onboarding doc | ✓ SATISFIED | `beta-testing-install.md` finalized + README pointer. |

**Documentation gap (non-blocking, flagged for cleanup):** `.planning/REQUIREMENTS.md` lines 65-67 still show ONBOARD-01/02/03 as unchecked `[ ]` and the Traceability table (line 132-134) still lists them `Pending`, even though this phase's evidence (external PyPI/GitHub checks + 3 bench records, all reviewed above) satisfies them. Only ONBOARD-04 (line 68) is checked/`Complete`. This is a stale-bookkeeping gap in the requirements tracker, not a functional gap — the underlying capability is proven on real hardware and via live external checks. Recommend updating REQUIREMENTS.md checkboxes/traceability status for ONBOARD-01/02/03 to `[x]`/`Complete` before milestone close.

### Anti-Patterns Found

None blocking. No TBD/FIXME/XXX/placeholder markers found in the doc, evidence records, or plan/summary files reviewed. No stub or hollow-report patterns in the evidence JSON (each record carries distinct, plausible values — ports, timings, checksums — not templated placeholders).

**Minor, honestly-disclosed deviation (not a gap):** Plans 05/06/07 each note that a single fresh throwaway venv (created once this session) was reused across all three board runs for the install leg, rather than a separate fresh venv per board as the plan literally specified. `FIRESTARTER_CONFIG_DIR` was still reset to a clean temp dir per board (D-07's substantive isolation goal — never touching the operator's `-e` install or `~/.firestarter`). This was disclosed as a deviation in all three SUMMARYs, does not use the operator's editable install, and does not compromise the fresh-machine claim's substance. No action required.

### Scope Guardrail (D-02/D-06)

Verified directly (not from SUMMARY claims):
- No `v1.21` tag exists in the meta repo, `firestarter`, or `firestarter_app` (`git tag -l "v1.21*"` empty in all three).
- No new `--no-ff` merge to `beta` occurred in either sub-repo (last beta merge in both is the pre-existing v1.19 merge from 2026-07-02, unrelated to this phase).
- Meta-repo current branch is still `gsd/v1.21-community-chip-validation-command` (not merged/shipped).
- Gitlink bump committed (`4d8b33c`) but NOT pushed — operator retains control of the meta-repo merge, per plan intent.

### Human Verification Required

None. Hardware evidence for this phase was gathered by design as a bench-witnessed, non-re-runnable record (per task instructions) — the three per-board `chip-test/onboard-*.md` records are detailed, distinct, and internally consistent (differing ports/timings/checksums per board), and are treated as the authoritative first-hand capture rather than routed to a further human-verify step.

### Gaps Summary

No blocking gaps. All 5 ROADMAP success criteria are verified against live external checks (PyPI, GitHub releases) and the three per-board bench evidence records, cross-referenced against the finalized onboarding doc and README pointer. The only non-blocking finding is a stale `REQUIREMENTS.md` checkbox/traceability status for ONBOARD-01/02/03 (still `Pending`/unchecked) that should be updated for bookkeeping accuracy before milestone close — it does not reflect a functional deficiency.

---

_Verified: 2026-07-27_
_Verifier: Claude (gsd-verifier)_
