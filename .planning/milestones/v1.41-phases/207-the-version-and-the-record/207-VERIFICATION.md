---
phase: 207-the-version-and-the-record
verified: 2026-09-23T17:00:00Z
status: passed
score: 4/4 must-haves verified
covered_files:
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
  - ".planning/phases/207-the-version-and-the-record/207-01-PLAN.md"
  - ".planning/phases/207-the-version-and-the-record/207-01-SUMMARY.md"
  - ".planning/phases/207-the-version-and-the-record/207-02-PLAN.md"
  - ".planning/phases/207-the-version-and-the-record/207-02-SUMMARY.md"
  - ".planning/phases/207-the-version-and-the-record/207-03-PLAN.md"
  - ".planning/phases/207-the-version-and-the-record/207-03-SUMMARY.md"
  - ".planning/phases/207-the-version-and-the-record/207-REVIEW.md"
  - ".planning/phases/207-the-version-and-the-record/evidence/207-01-oracles.txt"
  - ".planning/phases/207-the-version-and-the-record/evidence/207-03-wiki-postpush-freshclone.txt"
  - ".planning/phases/207-the-version-and-the-record/evidence/207-03-wiki-prepush.txt"
  - "firestarter_app/README.md"
  - "firestarter_app/firestarter/__init__.py"
  - "firestarter_fw/include/version.h"
covered_digest: "v1:sha256:b9e2414ad11ee950b38d78f12a3c126574f2f78b317f23fd9b8b2c84c9034a4b"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 207: The Version and the Record Verification Report

**Phase Goal:** Both repositories carry `3.1.0b1` in one commit pair, and the wiki documents the
breaking change alongside the two new user-facing surfaces.
**Verified:** 2026-09-23T17:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

All four checks below were run independently by this verifier against live state (a fresh
`gh api` call, fresh `git ls-remote`/`git fetch` against the sub-repo remotes, a fresh
`GITHUB_REF=... update_version.py --dry-run` run in both sub-repos, and a fresh, independent
`git clone --depth 1` of `henols/firestarter.wiki.git` into a scratch directory). None of the
verdicts below rest on SUMMARY.md's own narration.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Both `firestarter_fw/include/version.h` and `firestarter_app/firestarter/__init__.py` read `3.1.0b1`, bumped in one commit pair | ✓ VERIFIED | Directly read both files on `v1.41-verification-to-host`: `#define VERSION "3.1.0b1"` (fw) and `__version__ = "3.1.0b1"` (app). Each bump is a single-file commit (`a55f2d8` touches only `include/version.h`; `67f93e2` touches only `firestarter/__init__.py`) sitting directly on a merge of `origin/beta` (fw merge `00c90fc`: parent 1 = pre-phase tip `6e11d057`, parent 2 = `origin/beta`; app merge `610fb96`: parent 1 = pre-phase tip `d723cf77`, parent 2 = `origin/beta`). The app commit body names the firmware sha (`Pairs with firestarter_fw a55f2d80...`). Both sub-repos' own publisher, re-run live by this verifier after a fresh tag fetch, prints exactly `DRY_RUN: 3.1.0b1`, and `git merge-tree --write-tree --name-only HEAD origin/beta` prints exactly one line in both repos (re-run live, both `1`). |
| 2 | The wiki states ordinals 4 and 6 are retired, what a pre-`3.1.0` host does against `3.1.0b1` firmware, and what a user does about it | ✓ VERIFIED | Fresh, independent `git clone --depth 1 https://github.com/henols/firestarter.wiki.git` (HEAD `880a59b1588f8a52ebc89caad12d452d86428369`, matching the sha the SUMMARY claims was pushed). `Breaking-Changes.md` carries `## 3.1.0b1 — verify and blank check run on the host` as the first entry, quotes `ERROR: Unknown command: 6` and `ERROR: Unknown command: 4` verbatim, states the older-CLI-on-new-firmware hazard (write no longer refused on a non-blank UV EPROM), and a "What to do" section with `pip install --pre --upgrade firestarter`, `firestarter fw -i`, and the pin option `firestarter fw -i --firmware-version 3.0.0b35`. Cross-checked against `firestarter_fw/include/firestarter.h`: the live `CMD_*` table jumps `CMD_ERASE=3` → `CMD_CHECK_CHIP_ID=5` (4 gone) and has no ordinal 6 before `CMD_DEV_ADDRESS=7`, confirming both ordinals are genuinely retired, not just claimed. |
| 3 | `write --verify`, `--full` and the host-side `-b` semantics are documented where a user will find them | ✓ VERIFIED | Same fresh clone. `Writing-and-Verifying.md` exists with 6 `## ` sections, each labelled `(from 3.1.0b1)`, covering `write` blank-check families, `--verify`/`--full` exit codes and all 4 verdict lines, `verify`/`blank`, and `erase -b`. Linked from `Home.md` (`- [Writing-and-Verifying](Writing-and-Verifying) — ...`) and `_Sidebar.md` (`- [Writing and Verifying](Writing-and-Verifying)`), directly readable by a user browsing the wiki. Spot-checked the verdict-line strings against `firestarter_app/firestarter/cli_handlers.py:588-596` — byte-identical. Link-resolution check across all `.md` files in the fresh clone found zero broken relative links. |
| 4 | No GitHub Release is cut from the meta repo, and no `v1.41`/`v1.41*` tag exists | ✓ VERIFIED | Re-run live: `gh api repos/henols/firestarter/releases --jq length` → `0`. `git -C /workspaces tag --list 'v1.41*'` → empty. `git ls-remote origin 'refs/tags/v1.41*'` (meta) → empty. Both sub-repos' `chore(207-01): bump` commits confirmed NOT ancestors of `origin/beta` or `origin/main` after a fresh fetch, in either `firestarter_fw` or `firestarter_app`. |

**Score:** 4/4 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter_fw/include/version.h` | `#define VERSION "3.1.0b1"` | ✓ VERIFIED | Line 11, confirmed by direct read |
| `firestarter_app/firestarter/__init__.py` | `__version__ = "3.1.0b1"` | ✓ VERIFIED | Line 1, confirmed by direct read |
| `firestarter_app/README.md` | Upgrade-order correction | ✓ VERIFIED | Lines 49-52: `**Upgrade the CLI first, then the firmware.**` plus link to wiki Breaking-Changes; no longer claims every mixed pair fails |
| meta gitlinks `firestarter_fw`, `firestarter_app` | Equal to sub-repo HEADs | ✓ VERIFIED | `git ls-tree HEAD` in meta matches `git -C firestarter_fw rev-parse HEAD` and `git -C firestarter_app rev-parse HEAD` exactly |
| `firestarter.wiki/Breaking-Changes.md` (live) | 3.1.0b1 entry | ✓ VERIFIED | Present in fresh clone, first `## ` heading |
| `firestarter.wiki/Writing-and-Verifying.md` (live) | New command-reference page | ✓ VERIFIED | Present in fresh clone, 6 sections, all reachable |
| `firestarter.wiki/Home.md`, `_Sidebar.md` (live) | Navigation to new page | ✓ VERIFIED | Both link `(Writing-and-Verifying)` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| firmware bump commit | merge of `origin/beta` | direct parent | ✓ WIRED | `a55f2d8^1 = 00c90fc`, whose `^1` is pre-phase tip and `^2` is `origin/beta` |
| app bump commit | merge of `origin/beta` | direct parent | ✓ WIRED | `67f93e2^1 = 610fb96`, whose `^1` is pre-phase tip and `^2` is `origin/beta` |
| app bump commit body | firmware bump sha | textual reference | ✓ WIRED | Body reads `Pairs with firestarter_fw a55f2d80...` |
| meta gitlinks | sub-repo HEADs | `git ls-tree` | ✓ WIRED | Both gitlinks equal live sub-repo `rev-parse HEAD` |
| `Breaking-Changes.md` | `Writing-and-Verifying.md` | relative link | ✓ WIRED | Resolves in fresh clone |
| `Home.md`, `_Sidebar.md` | `Writing-and-Verifying.md` | relative link | ✓ WIRED | Both resolve in fresh clone |
| firmware/app publisher script | version file | `update_version.py --dry-run` | ✓ WIRED | Live re-run: `DRY_RUN: 3.1.0b1` in both repos |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Firmware publisher derives 3.1.0b1 | `GITHUB_REF=refs/heads/beta python3 .github/scripts/update_version.py --dry-run` (firestarter_fw) | `DRY_RUN: 3.1.0b1` | ✓ PASS |
| App publisher derives 3.1.0b1 | same, firestarter_app | `DRY_RUN: 3.1.0b1` | ✓ PASS |
| Ship merge stays conflict-free (fw) | `git merge-tree --write-tree --name-only HEAD origin/beta \| wc -l` | `1` | ✓ PASS |
| Ship merge stays conflict-free (app) | same, firestarter_app | `1` | ✓ PASS |
| No GitHub Release exists | `gh api repos/henols/firestarter/releases --jq length` | `0` | ✓ PASS |
| Neither bump reached `beta`/`main` | `git merge-base --is-ancestor <bump-sha> origin/beta\|main` in both sub-repos | not an ancestor (4/4 checks) | ✓ PASS |
| Live wiki carries the published record | fresh `git clone --depth 1 henols/firestarter.wiki.git`; content/link checks | all present, 0 broken links | ✓ PASS |
| Retired ordinals absent from firmware command table | `grep CMD_ include/firestarter.h` | 4 and 6 absent from the sequence | ✓ PASS |

Full app pytest (2363 passed) and firmware `tests/` (316 passed) suite runs were not re-executed by
this verifier (would re-run the whole suite for no new evidence per the no-repeat-full-suite rule);
these numbers are the orchestrator's own post-return checks (stated in the orchestrator notes: "app
2363 passed, 36 snapshots, ruff clean, on .venv311 (Python 3.11.16); firestarter_fw tests/ 316
passed"), not bare SUMMARY.md narration, and are accepted on that basis.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| REL-01 | 207-01 | Both repos carry `3.1.0b1`, bumped in one commit pair | ✓ SATISFIED | Truth 1 above; REQUIREMENTS.md already hand-marked Complete by the orchestrator — confirmed accurate |
| REL-04 | 207-02, 207-03 | Breaking change and `write --verify`/`--full` surfaces documented in the wiki | ✓ SATISFIED | Truths 2 and 3 above, verified against the live, published wiki. **Orchestrator should mark REL-04 Complete.** |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s traceability table maps only REL-01 and
REL-04 to Phase 207, matching both plans' `requirements:` frontmatter exactly.

### Anti-Patterns Found

None blocking. One pre-existing, out-of-phase-scope documentation defect was found by the phase's
own code review (`207-REVIEW.md`, WR-01): `firestarter.wiki/Testing-Chips.md` states `dev test`
runs its write-and-verify block "twice" in five places; the code's actual default
(`_DEFAULT_RUNS = 3` in `cli_handlers.py`, since `b596249` on 2026-09-17) runs it three times. This
verifier confirmed the phase-207 diff to `Testing-Chips.md` (`git diff f967398..880a59b --
Testing-Chips.md`) touches only 5 new lines in the "How to report it" section — the stale "twice"
text at lines 39/48-62 is untouched by this phase and predates it. Per the orchestrator's framing,
this is recorded as an observed pre-existing defect, not a phase-207 gap.

### Requirements/Prohibitions

All `must_haves.prohibitions` across the three plans (nothing pushed from 207-01; no catalog id and
untouched claim-stamp from 207-02; wiki-only push, no tag/Release, no credential write from 207-03)
were independently re-checked live by this verifier via the criterion-4 checks above (0 Releases,
no `v1.41*` tag anywhere, neither bump commit an ancestor of `beta`/`main`) and hold.

### Human Verification Required

None. All four ROADMAP success criteria are directly, mechanically verifiable and were verified
against live state, not narration.

### Gaps Summary

None. All four ROADMAP success criteria hold, cross-checked against live git/GitHub/wiki state
independent of SUMMARY.md claims.

---

_Verified: 2026-09-23T17:00:00Z_
_Verifier: Claude (gsd-verifier)_

---

**Orchestrator note (2026-09-23):** `covered_digest` was recomputed once after `phase.complete 207`. That verb edited two covered files: it flipped REL-04 in `.planning/REQUIREMENTS.md` and wrote the `**Plans:** 3/3 plans complete` line in `.planning/ROADMAP.md`. The orchestrator then appended REL-04's delivery note. No other covered file changed, and the verdict above was not re-derived.
