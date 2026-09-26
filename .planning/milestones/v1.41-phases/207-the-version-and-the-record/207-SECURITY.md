---
phase: "207"
slug: "the-version-and-the-record"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-09-23"
---

# Phase 207 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

Register origin: **authored at plan time**. All three PLAN.md files (`207-01`, `207-02`,
`207-03`) carry a `<threat_model>` block, so this audit verified the mitigations named there
rather than building a register retroactively. No SUMMARY.md raised a `## Threat Flags` entry.

This phase is a release-process phase, not a code phase: its attack surface is outward,
irreversible publication (PyPI, GitHub pre-releases, a meta Release or tag, the public wiki).
Each high-severity leg was checked twice. The first check read the executor's recorded evidence.
The second re-checked the **live remotes** on 2026-09-23, after execution, because a remote can
move after the evidence was written.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| milestone branch → `beta` | A push or merge to `beta` in either sub-repo publishes at once: PyPI for the app, a GitHub pre-release for the firmware. No path filter applies. | version line, release artifacts |
| local git → remote | Any push crosses into public, irreversible published state. | commits, refs, tags |
| meta working tree → meta commit | Unrelated dirty files share the working tree with the two gitlinks committed here. | gitlinks, stray working-tree files |
| package index → `.venv311` | The venv rebuild installs the project's own `[test]` extra from PyPI. | third-party packages |
| wiki clone → live public wiki | A push publishes page text and commit history instantly and permanently. There is no preview and no pull request. | user-facing prose, commit messages |
| code and bench record → wiki prose | The executor turns code and transcripts into public claims. A mis-transcription becomes a false public statement. | compatibility claims, exit codes, flags |
| operator approval → executor action | The executor may act outward only on an explicit operator reply. | approval intent |
| git credential helper | The push authenticates with the operator's GitHub credential. | credential |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-207-01 | Tampering | version line at ship merge | high | mitigate | `evidence/207-01-oracles.txt`: both publishers print `DRY_RUN: 3.1.0b1`. `git merge-tree --write-tree --name-only HEAD origin/beta \| wc -l` returns `1` in both sub-repos, so there is no conflict. `d347dd3f`'s body records that each tip sits on a merge of `origin/beta` made before its bump. | closed |
| T-207-02 | Elevation of privilege | `git push` to `beta` / `main` | high | mitigate | **Live re-check:** after a fresh fetch, `merge-base --is-ancestor` reports fw bump `a55f2d80` and app bump `67f93e2d` absent from both `origin/beta` and `origin/main`. `ls-remote` finds no `v1.41*` branch and no `3.1.0*` tag on either remote. | closed |
| T-207-03 | Spoofing | meta GitHub Release / `v1.41` tag | high | mitigate | **Live re-check:** `gh api repos/henols/firestarter/releases` returns `0`. No `v1.41*` tag exists locally or on `origin`. Meta has no `.github/workflows`. | closed |
| T-207-04 | Tampering | meta gitlink commit | medium | mitigate | `git show --name-only d347dd3f` lists exactly `firestarter_app` and `firestarter_fw`. No other path rode along. | closed |
| T-207-05 | Tampering | `gsd-tools query commit` branch switch | medium | mitigate | **Live re-check:** meta, `firestarter_fw` and `firestarter_app` are all on `v1.41-verification-to-host`. | closed |
| T-207-06 | Repudiation | commit-pair provenance | low | mitigate | `d347dd3f`'s body names all three sub-repo shas: `a55f2d8`, `2a08c7d`, `67f93e2`. `evidence/207-01-oracles.txt` records every oracle output. | closed |
| T-207-07 | Information disclosure | wiki page text and commit messages | medium | mitigate | **Live re-check** on a fresh clone of the published wiki: a sweep of every page for phase numbers, `D-NN`, `.planning/` and `v1.4x` returns CLEAN. The same sweep of every commit message in `81229d8..HEAD` returns CLEAN. | closed |
| T-207-08 | Information disclosure (omission) | Breaking-Changes 3.1.0b1 entry | high | mitigate | **Live:** "An older CLI on 3.1.0b1 firmware" opens with the bold sentence "An older CLI's `write` no longer refuses a non-blank UV EPROM", followed by the partial-programming consequence. Both install one-liners carry `--upgrade`, at `Breaking-Changes.md:13` and `:63`. | closed |
| T-207-09 | Tampering (false claim) | code-derived compatibility rows | medium | mitigate | **Live:** `grep -c 'not yet observed on hardware' Breaking-Changes.md` returns `2`. `207-REVIEW.md` checked every flag, exit code and label against the source and the `--help` snapshots and found no discrepancy. Its one warning, WR-01, concerns `Testing-Chips.md` text written before this phase and is not a security claim. | closed |
| T-207-10 | Repudiation | Breaking-Changes claim stamp | low | mitigate | **Live:** the last line of `Breaking-Changes.md` is byte-identical to the last line at `81229d8`. | closed |
| T-207-11 | Elevation of privilege | accidental push of the wiki (plan 207-02) | high | mitigate | `207-02-SUMMARY.md` records `git ls-remote` showing the live `master` still at `81229d8` when plan 02 ended. The later push was plan 207-03's approved push, confirmed by the fast-forward from `81229d8` in the push output. | closed |
| T-207-12 | Tampering | unreviewed commit riding the push (`f967398`) | high | mitigate | `evidence/207-03-wiki-prepush.txt` §a lists four outgoing commits with `f967398` on its own line and a note about it. §b carries its full diff. `PASS-207-03-EXPORT` is recorded. | closed |
| T-207-13 | Elevation of privilege | push without operator approval | high | mitigate | `207-03-SUMMARY.md` records the operator's verbatim reply `you acn push`, given after the outgoing log, the diffs, the hedged rows and the push target had all been shown. The operator was present, so the approval was not an auto-mode one. | closed |
| T-207-14 | Tampering | force-push rewriting public history | high | mitigate | **Live re-check:** `81229d8` is an ancestor of the published `master` (`merge-base --is-ancestor` → yes). The push output recorded in the summary is `81229d8..880a59b`: a fast-forward with no `+`. | closed |
| T-207-15 | Tampering | bytes changed between approval and push | medium | mitigate | `evidence/207-03-wiki-prepush.txt` records `APPROVAL_SHA: 880a59b1…`. **Live:** `ls-remote origin refs/heads/master` returns `880a59b1588f8a52ebc89caad12d452d86428369`, equal to it. | closed |
| T-207-16 | Information disclosure | credential leak into config | medium | mitigate | **Live:** the wiki clone's `--local` config has no `credential.*` or `url.*` key. `remote.origin.url` is the plain `https://github.com/henols/firestarter.wiki.git`, with no userinfo or token. | closed |
| T-207-17 | Spoofing | meta Release / `v1.41` tag arming stranded CLIs | high | mitigate | Same live checks as T-207-03: 0 Releases and no `v1.41*` tag. `ls-remote --tags` also shows 0 tags on the wiki remote. `PASS-207-PROHIBITION` is recorded in both 207-01 and 207-03 evidence. | closed |
| T-207-18 | Information disclosure | planning identifiers in published text | medium | mitigate | Same live fresh-clone sweep as T-207-07: CLEAN on every published page. | closed |
| T-207-SC | Tampering | `uv pip install -e '.[test]'` | low | accept | Accepted — see Accepted Risks Log R-01. | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| R-01 | T-207-SC | The venv rebuild adds no new package. It reinstalls the project's own pinned `[test]` extra, which CI already installs on every run. The research package-legitimacy audit found nothing to flag. | plan 207-01 threat model (disposition `accept`) | 2026-09-23 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-09-23 | 19 | 19 | 0 | `/gsd-secure-phase` orchestrator (L1, short-circuit: register authored at plan time, 0 open) |

### Security Audit 2026-09-23

| Metric | Count |
|--------|-------|
| Threats found | 19 |
| Closed | 19 |
| Open | 0 |

No auditor subagent was spawned. The workflow skips the auditor when the register was authored
at plan time, `threats_open` is 0 and ASVS is level 1: grep-depth verification is sufficient.
Of the 19 threats, 12 were re-verified against live remote state, not only the recorded evidence.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-09-23
