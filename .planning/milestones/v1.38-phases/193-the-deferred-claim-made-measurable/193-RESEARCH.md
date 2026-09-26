# Phase 193: The Deferred Claim, Made Measurable - Research

**Researched:** 2026-09-14
**Domain:** meta-repo documentation + one `curl`/ClickHouse shell instrument + git submodule archaeology
**Confidence:** HIGH — every load-bearing claim below was executed in this session; commands and raw
output are reproduced inline.

## Summary

CONTEXT.md fixed every design question this phase had. Research therefore did not re-open any of them.
It executed the four things the plan cannot proceed on: the ClickHouse query, the pre-rename ref, both
`.gitmodules` workarounds, and the `CLAUDE.md` insertion points.

**All four came back positive, and three produced findings CONTEXT.md could not have known.** The
ClickHouse query reproduces D-09's baseline *exactly* (17 / 116 / 52 / 12.8%). The pre-rename ref D-16
needs is **not** the obvious one — the Phase 189 parent commit `9ccf0414` is on an unpushed milestone
branch and is unreachable from a fresh clone; the `v1.35` tag is the correct ref and is the very ref
999.9 names. `git submodule sync` **silently destroys** the existing-clone workaround, which the note
does not mention and which the note's own Phase A step 2 instructs operators to run. And a
`trigger_condition:` value that *begins* with a backtick makes GSD's frontmatter parser return `{}`,
silently dropping `status: dormant` and making the seed invisible to the audit scanner — a direct
hazard for D-12's "verbatim" rewrite.

**Primary recommendation:** write the plan against the exact command lines in §Code Examples; use
`v1.35` as the pre-rename ref; add the `submodule sync` hazard to the new GATE-03 note; and keep the
seed's `trigger_condition` scalar from starting with a backtick.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

Copied by reference, not re-litigated. The binding record is
`.planning/phases/193-the-deferred-claim-made-measurable/193-CONTEXT.md`; nothing in this research
overrides it.

### Locked Decisions

**GATE-01 — form:** D-01 (committed runnable **shell** script under `tools/adoption/`; a minimal
"did the query return rows" guard is permitted, a **staleness gate is not**), D-02 (the honesty caveat
prints in the script's own output, every run, in the strong "new acquisition has stopped — necessary,
not sufficient" form), D-03 (one data source; fallbacks recorded, not built).

**GATE-01 — what the number measures:** D-04 (`installer IN ('pip','uv')`, stable channel, numerator
and denominator both), D-05 (prerelease filter is `match(version, '(a|b|rc)[0-9]|dev')`, **not**
`NOT LIKE '%b%'`), D-06 (numerator = any stable `>= 2.0.9`, **computed**, not an allowlist), D-07
(at-risk denominator is `2.0.7` **exactly**; the pre-2.0.7 tail is outside the instrument's reach and
the record must say so).

**GATE-01 — trigger:** D-08 (share AND absolute floor), D-09 (**fixed share `>= 90%` AND 2.0.7
`<= 10` pip+uv downloads, both over a rolling 90-day window, stable channel**; baseline at authoring
time FIXED 17 · 2.0.7 116 · older-stable tail 52 · fixed share 12.8%), D-10 (a single reading, not two
consecutive), D-11 (re-examination date **2027-09-13**, never an auto-fire), D-12 (the seed's
`trigger_condition:` frontmatter carries D-09's numbers verbatim; 2.0.7 → 2.0.9 corrections applied
throughout).

**GATE-02 / GATE-03 — location:** D-13 (`CLAUDE.md` carries both rules, notes carry the mechanisms),
D-14 (GATE-02's mechanism is **cited**, not restated — `.planning/notes/999.9-repo-rename-impact-analysis.md`
§"Standing rule this must produce"), D-15 (GATE-03 gets a `CLAUDE.md` repo-structure pointer plus a
dedicated note).

**Discretion, settled as locked:** D-16 (GATE-03 "demonstrated" = executed, transcripts under
`${phase_dir}/evidence/`, pre-rename ref chosen to actually reproduce the trap, and **no claim of a
breakage that has not happened**), D-17 (meta `tools/` is outside the no-comments hard rule, so the SQL
may be explained; GSD process commentary — `# Phase 193`, `# GATE-01`, plan/milestone citations — is
forbidden everywhere).

### Claude's Discretion

None left open. D-16, D-17 and D-18 were settled during discussion and are recorded as locked.

### Deferred Ideas (OUT OF SCOPE)

- Fixing `new-milestone.md`'s `SEED-*.md` glob (stays a todo).
- Running the instrument on a schedule (needs a `.github/workflows/` the meta repo does not have).
- A second data source for the instrument (D-03 records the fallbacks rather than building them).
- Resolving the PyPI/GitHub `firestarter` name incoherence.
- **Explicitly offered and declined (D-01, `<specifics>`):** an elaborate self-check, a staleness gate,
  a second data path, a scheduled run, CI scaffolding. A plan that reintroduces any of these is working
  against a choice already made.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description (verbatim, `.planning/REQUIREMENTS.md:95-105`) | Research Support |
|----|-------------|------------------|
| GATE-01 | "An adoption instrument reports per-version download share for the `firestarter` PyPI package, so the seed's trigger is a number with a stated threshold rather than a judgement call. It must state plainly what it does **not** measure — installed base is not observable, and users who never upgrade are unreachable by any threshold." | §Code Examples 1–3: the exact working `curl -G`, executed, reproducing D-09's baseline to the digit. §Common Pitfalls 1–4: the version-comparison idiom, the empty-result shape, error handling, the UTC window boundary. |
| GATE-02 | "The standing rule — the meta repository never publishes a GitHub Release — is recorded where a future milestone will encounter it before acting, together with the `_compare_versions` mechanism that makes violating it silent: a `v1.36` tag parses as PEP 440 `1.36`, so `3.0.0b29 >= 1.36` reads true and the firmware is reported current forever." | §Mechanism Verification: the PEP 440 claim executed against `packaging`. §CLAUDE.md Insertion Points: line 72–77 target. §Finding F-6: the cited section's `firmware.py:272-288` line range is stale. |
| GATE-03 | "The `.gitmodules` history trap is documented with a workaround demonstrated for **both** cases: an existing clone (`git config submodule.firestarter.url`) and a fresh clone at a pre-rename ref (`--no-recurse-submodules` plus a manual URL set)." | §Finding F-2 (the correct pre-rename ref), §Code Examples 4–5 (both workarounds, executed end to end), §Finding F-4 (the `submodule sync` hazard), §Finding F-5 (today's benign behaviour, executed — the honest framing D-16 demands). |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

Read in full at `/workspaces/CLAUDE.md` (77 lines).

- **"Source code comments — hard rule" (`CLAUDE.md:50-70`)** is scoped, verbatim, to "everything under
  `firestarter/` and `firestarter_app/`". Meta `tools/` is **not** named. D-17 is consistent with the
  file as written. GSD process commentary remains forbidden everywhere by D-17 itself.
- **`main` is protected in all three repos; this project's close targets `beta`** (`CLAUDE.md:72-77`).
  This phase writes to the meta repo only and pushes nothing.
- **`tools/` now holds `catalog/` alone** (`CLAUDE.md:12`). Adding `tools/adoption/` makes that sentence
  stale. The plan should update it in the same edit that adds D-15's GATE-03 pointer — both land in the
  Repository Structure paragraph.
- **Project skills** (`.claude/skills/`): `devtest-rootcause`, `devtest-triage`, `find-skills`,
  `skill-creator`. None carry rules bearing on this phase (all are chip/skill-authoring domain).
  [VERIFIED: `ls .claude/skills/`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Per-version download measurement | External data service (ClickHouse public playground) | — | Nothing local holds this data; PyPI publishes it only through query endpoints. |
| Query execution + verdict rendering | Meta-repo tooling (`tools/adoption/`, shell + `curl`) | — | D-01. Runnable artefact, no runtime deps beyond `curl`. |
| Honesty caveat | Same script's stdout | The GATE-01 record | D-02 — the caveat must travel with the number. |
| The trigger's numbers | `.planning/seeds/SEED-claim-firestarter-slug.md` frontmatter | — | D-12; the seed is what `new-milestone.md:79` surfaces. |
| The no-Releases rule | `CLAUDE.md` | `.planning/notes/999.9-…` §"Standing rule this must produce" | D-13, D-14 — rule in-line, mechanism cited. |
| The `.gitmodules` trap | `CLAUDE.md` pointer | new `.planning/notes/` note + `${phase_dir}/evidence/` transcripts | D-15, D-16. |

---

## Findings

### F-1 — The ClickHouse query works and reproduces D-09's baseline exactly

[VERIFIED: executed 2026-09-14, output reproduced in §Code Examples 1–2]

Per-version, stable-channel, pip+uv, 90-day window, project `firestarter`:

| Leg | Measured now | CONTEXT.md D-09 baseline | Delta |
|-----|--------------|--------------------------|-------|
| FIXED (`>= 2.0.9`) | **17** | 17 | 0 |
| 2.0.7 | **116** | 116 | 0 |
| older-stable tail | **52** | 52 | 0 |
| fixed share | **12.8%** | 12.8% | 0 |
| `trigger_met` | **0** | "nowhere near firing" | agrees |

No drift. `max(date)` in the table is **2026-09-13**, one day behind `today()` = 2026-09-14, so the
window `date >= today()-90` spans **2026-06-16 .. 2026-09-13** and covers the same data D-09 saw. The
older-stable tail of 52 is the sum of the 31 rows below 2.0.7 in §Code Examples 1 (6 in the `2.0.x`
band + 12 in `1.5.x` + 17 in `1.4.x` + 15 in `1.3.x` + 2 in `1.1.x`), confirming D-07's "1–4 downloads
each across ~30 ancient 1.x versions" characterisation against live data.

**Endpoint mechanics, learned the hard way:** `user=play` **must be a query-string parameter, not a POST
body field**. A `curl -s ... --data-urlencode "user=play"` without `-G` sends it in the body, ClickHouse
falls back to the `default` user, and the call fails with `Code: 194 … Authentication failed`
[VERIFIED: executed, that exact error returned]. `-G` is not cosmetic. CONTEXT.md's `curl -G` is right.

### F-2 — The pre-rename ref must be `v1.35`, not the Phase 189 parent commit

[VERIFIED: `git log`, `git ls-remote`, `git show <ref>:.gitmodules`, executed]

The commit that landed RENAME-02 is **`5aba9dbc8d760e530638931d19ede0a227dd1a60`** —
`feat(189-02): repoint firmware submodule URL to firestarter_fw`, 2026-09-13 14:04:41 +0000. Its parent
is **`9ccf0414d7a2d86e5e97b6cf1db2da01737bfc81`** — `docs(phase-189): update tracking after wave 1`,
2026-09-13 14:03:21 +0000 — and `git show 9ccf0414:.gitmodules` returns, verbatim:

```
[submodule "firestarter"]
	path = firestarter
	url = git@github.com:henols/firestarter.git
[submodule "firestarter_app"]
	path = firestarter_app
	url = git@github.com:henols/firestarter_app.git
```

Section name and path are both `firestarter` at that ref, as expected.

**But `9ccf0414` is unusable for D-16's fresh-clone transcript.** It lives only on the unpushed
milestone branch `gsd/v1.38-repository-rename-activated-2026-09-13` (GSD pushes at ship time). In a
fresh clone of `origin`, `git cat-file -t 9ccf0414` returns `fatal: Not a valid object name`
[VERIFIED: executed in a clean clone].

Published refs whose `.gitmodules` still carries the old URL [VERIFIED: `git show <ref>:.gitmodules` in
a clean clone]:

| Ref | `.gitmodules` firmware URL | Durable? | Verdict |
|-----|---------------------------|----------|---------|
| `v1.35` (tag, `6e84030b…`, 2026-09-02) | `git@github.com:henols/firestarter.git` | **immutable** | **use this** |
| `origin/beta` | `git@github.com:henols/firestarter.git` | no — changes at v1.38 close | unsuitable |
| `origin/main` | `git@github.com:henols/firestarter_fw.git` | — | already fixed (`d1a83997`, Phase 189-04) |

`v1.35` is also the ref 999.9 itself names: *"Checking out `v1.35`, bisecting firmware history, or
reading any pre-rename commit resurrects the old URL"*
(`.planning/notes/999.9-repo-rename-impact-analysis.md`, §"The `.gitmodules` archaeology trap"). Using
it makes the transcript self-citing.

**Side finding for the seed's checklist (D-12):** the seed's third "Do not fire this while any of these
is untrue" leg reads *"`.gitmodules` points at `firestarter_fw` and `git submodule sync --recursive` has
run"*. Today that is true on `origin/main` and on the milestone branch, and **false on `origin/beta`** —
beta's last `.gitmodules` commit is still `6d54d7be chore: add firestarter and firestarter_app as
submodules`. CONTEXT.md D-12 states the checklist "is now satisfied on all three legs". It will be, once
v1.38 merges to beta; it is not yet. The plan should either scope the leg to `main` (which is the branch
that matters for the trap) or note the beta state, rather than asserting a satisfaction that a reader can
falsify with one `git show`.

### F-3 — Both workarounds execute cleanly; `git submodule init` does **not** clobber a pre-set override

[VERIFIED: executed end to end, full transcripts in §Code Examples 4–5]

Current state of this working clone [VERIFIED: `git config --get-regexp '^submodule\.'`]:

```
submodule.firestarter.url        git@github.com:henols/firestarter_fw.git
submodule.firestarter.active     true
submodule.firestarter_app.url    git@github.com:henols/firestarter_app.git
submodule.firestarter_app.active true
```

and `.gitmodules` on the milestone branch declares `url = git@github.com:henols/firestarter_fw.git`. So
the existing-clone override is already in place here and the acceptance criterion can be written against
those literal values.

Two behaviours worth pinning in the plan's criteria:

- `git submodule init` **preserves** an existing `submodule.<name>.url` in `.git/config` rather than
  re-copying it from `.gitmodules` — so setting the override *before* `submodule update --init` works
  [VERIFIED].
- The `.git/config` override **survives a checkout** from a post-rename ref to `v1.35`; `.gitmodules`
  changes under it and the override does not [VERIFIED].

### F-4 — `git submodule sync` silently destroys the workaround (undocumented hazard)

[VERIFIED: executed — transcript in §Code Examples 6]

With HEAD at the pre-rename ref `v1.35` and the override correctly set to `firestarter_fw`:

```
$ git config --get submodule.firestarter.url
git@github.com:henols/firestarter_fw.git
$ git submodule sync firestarter
Synchronizing submodule url for 'firestarter'
$ git config --get submodule.firestarter.url
git@github.com:henols/firestarter.git          <-- clobbered
$ git -C firestarter remote get-url origin
git@github.com:henols/firestarter.git          <-- child remote rewritten too
```

Re-applying the override and running `sync` again immediately re-clobbers it, because `sync` reads
`.gitmodules` **at the current HEAD**. This matters because 999.9's own ordered procedure, Phase A step
2, instructs `git submodule sync --recursive` as routine hygiene — an operator who has internalised that
step will undo the GATE-03 workaround without any warning.

Repair sequence, verified:

```bash
git config submodule.firestarter.url git@github.com:henols/firestarter_fw.git
git -C firestarter remote set-url origin git@github.com:henols/firestarter_fw.git
```

The plan should carry this into the new GATE-03 note. It is not an invented workaround (D-16 forbids
those) — it is a documented failure mode *of* the workaround the note already prescribes.

### F-5 — The trap does **not** bite today; a plain `submodule update` at `v1.35` succeeds

[VERIFIED: executed — transcript in §Code Examples 7]

The old firmware slug still redirects: `gh api repos/henols/firestarter` returns
`{"full_name":"henols/firestarter_fw","id":810276812}`, identical to
`gh api repos/henols/firestarter_fw`, and `git ls-remote git@github.com:henols/firestarter.git HEAD`
resolves [all VERIFIED].

In a fresh clone at `v1.35` with **no** override, `git submodule update --init --depth 1 firestarter`
prints `From github.com:henols/firestarter` and checks out `4f73c80c…` successfully. This is exactly
D-16's framing: the demonstration shows the **mechanism and its fix**, and the transcript must not claim
a breakage that has not happened.

The note's projected post-claim behaviour — *"`git submodule update --init` resolves that URL to the
**meta** repository and clones the parent into its own `firestarter/` child directory"* — is
**unverified and unverifiable today**, because the redirect is live and D-1 forbids firing the claim.
It is a reasoned projection, and the new note should present it as one.

**Transcript-hygiene hazard, learned by hitting it:** a leftover non-empty `firestarter/` directory or a
stale `.git/modules/firestarter` makes `submodule update` abort with
`Failed to clone 'firestarter' a second time, aborting` — a failure that reads exactly like the trap and
is not. Any transcript-producing script must start from a truly clean state
(`rm -rf firestarter .git/modules/firestarter`) or it will record a false positive. A related artifact:
`git -C firestarter <cmd>` on an **empty** `firestarter/` silently walks up to the *parent* repo and
answers for it. Assert on `git -C firestarter remote get-url origin` only after confirming the child
exists.

### F-6 — The GATE-02 mechanism verifies; the cited note's line range does not

[VERIFIED: executed against the installed `packaging`]

```
$ python3 -c "from packaging.version import Version; print(Version('v1.36')); print(Version('3.0.0b29') >= Version('1.36'))"
1.36
True
```

`Version("v1.36")` normalises to `1.36` and `Version("3.0.0b29") >= Version("1.36")` is `True`. The
REQUIREMENTS.md GATE-02 wording and the ROADMAP criterion 3 wording are both accurate.

The cited section, `.planning/notes/999.9-repo-rename-impact-analysis.md` §"Standing rule this must
produce" (file lines 86-92), reads verbatim:

> **Never publish a GitHub Release on the meta repo. Bare milestone tags only.**
>
> Its present zero-Releases state is exactly what makes the post-claim failure a clean 404. Publish even
> one Release there and the failure mode inverts: `_compare_versions` (`firmware.py:272-288`) parses a
> tag like `v1.36` as PEP 440 `1.36`, evaluates `Version("3.0.0b28") >= Version("1.36")` as **true**, and
> reports the firmware as already up to date — for every stranded CLI, silently, forever. Loud-and-obvious
> becomes silent-and-permanent.
>
> This risk is **latent today and armed by a single future action**, which is why it belongs in a durable
> rule rather than in the rename procedure.

**The mechanism is there in full** — D-14's "cite, do not duplicate" is sound. Two accuracy notes:

1. **The `firmware.py:272-288` line range is stale.** `def _compare_versions` is at
   `firestarter_app/firestarter/firmware.py:282` on the milestone branch `v1.38-repository-rename`
   (function body 282-298), at **271** on `origin/beta`, and at **132** on `origin/main`
   [VERIFIED: `git show <ref>:firestarter/firmware.py | /usr/bin/grep -n "def _compare_versions"`].
   This is a `.planning/` → sub-repo citation, which the project's repair rule covers. It is **not** in
   this phase's scope to fix, but `CLAUDE.md` should cite the note **by section heading**, not by line
   number, exactly as `CLAUDE.md:76` already does for `workflows/ship.md` ("Cited by content, not line
   number").
2. The note says `3.0.0b28`; REQUIREMENTS.md and the ROADMAP say `3.0.0b29`. Both evaluate `True`
   [VERIFIED]. `CLAUDE.md` should use the requirement's `3.0.0b29` so criterion 3 matches literally.

### F-7 — The seed's frontmatter: one shape silently destroys it

[VERIFIED: executed against GSD's real parser,
`.claude/gsd-core/bin/lib/frontmatter.cjs:701` `extractFrontmatter`]

Current file, `.planning/seeds/SEED-claim-firestarter-slug.md:1-6`, verbatim:

```yaml
---
title: Claim henols/firestarter for the meta repo (the destructive half of 999.9)
trigger_condition: A stable release of the app carrying the firestarter_fw firmware URLs has shipped AND has displaced 2.0.7 as the dominant PyPI version
planted_date: 2026-09-13
status: dormant
---
```

Four keys, single-line plain scalars — the same shape all 16 seeds use
(`.planning/seeds/phase-gate-expiry-discipline.md` adds `resolved`, `resolved_by`). Body section
headings and their line numbers:

| Line | Heading |
|------|---------|
| 8 | `# Claim `henols/firestarter` for the meta repo` |
| 16 | `## Why it is separable` |
| **23** | **`## Why the trigger is what it is`** (lines 25-30 — D-12's rewrite target) |
| **32** | **`## Do not fire this while any of these is untrue`** (3 bullets, lines 34-38) |
| 40 | `## Carry this rule forward when it fires` |
| 47 | `## Known residual, accepted` |
| 53 | `Full analysis: …` |

Line 30 is the sentence D-11 must not contradict: *"Gate on that stable having shipped and having
displaced 2.0.7 — not on a calendar date."*

**Parser behaviour, tested directly** — `extractFrontmatter` routes through a real guarded YAML parser
with an ambiguous-colon repair, not a line regex:

| `trigger_condition` shape | Result |
|---|---|
| single-line plain scalar with `>=`, `<=`, `%`, parens | parses ✓ |
| folded block scalar `>-` over four indented lines | parses ✓ (newlines folded to spaces) |
| value containing `Threshold: fixed share >= 90%` (embedded `: `) | parses ✓ (colon repair) |
| value containing **mid-string** backticks | parses ✓ |
| value **starting** with a backtick — `` trigger_condition: `2.0.7` draws <= 10 `` | **returns `{}`** ✗ |

The last row is the trap. A leading backtick is a YAML reserved indicator; the whole frontmatter block
becomes unparseable and every key is lost — including `status: dormant`, which
`.claude/gsd-core/bin/lib/audit.cjs:603-644` `scanSeeds` reads to decide whether the seed is open. A
silently-unparseable seed is treated as "not open" (the module's documented fail-open direction), so the
seed vanishes from the audit with no error. D-12 requires D-09's numbers "verbatim", and D-09's text
opens with backticked tokens — **the plan must make the scalar start with a word.**

Recommended shape, verified to parse and to round-trip the value intact:

```yaml
trigger_condition: >-
  Fixed share of `(>= 2.0.9) / ((>= 2.0.9) + 2.0.7)` is >= 90%, AND `2.0.7` draws
  <= 10 `pip`+`uv` downloads, both measured over a rolling 90-day window on the
  stable channel. Re-examine the premise 2027-09-13 if unfired; never auto-fire.
```

A plain single-line scalar starting `Fixed share of …` also parses and matches the 16-seed convention.
Either is fine; a leading backtick is not.

### F-8 — `CLAUDE.md` insertion points

[VERIFIED: `/workspaces/CLAUDE.md`, 77 lines, trailing newline present]

**GATE-03 pointer (D-15) — the Repository Structure area.** `## Repository Structure` is **line 5**.
Line 7 opens the paragraph; **line 12** is the single long paragraph that ends:

> …`tools/` now holds `catalog/` alone — and **no automated wiki guard exists now**.

Line 13 is blank; line 14 is `## System Overview`. The pointer goes as a new paragraph or bullet after
line 12. **Note:** adding `tools/adoption/` falsifies "`tools/` now holds `catalog/` alone" in that same
sentence — fix it in the same edit.

**GATE-02 rule (D-13, D-14) — the close/branch-protection section.**
`## Milestone close and branch protection` is **line 72**. It is the file's last section, four bullets
at lines 74-77:

| Line | Bullet (opening words) |
|------|------------------------|
| 74 | `**main is protected in all three repositories** — pull request required…` |
| 75 | `**This project's close targets beta, not main.**` |
| 76 | `**Before running /gsd-ship, recreate local beta from origin/beta**` — *"Cited by content, not line number"* |
| 77 | `**The mechanics, the blocked stable-release route and the consumer sites are in .planning/notes/v135-close-procedure-under-protection.md.**` |

Line 77 is the last line of the file. The GATE-02 bullet is best inserted **between 76 and 77**, so the
"see the note for mechanics" pointer stays last — that is the section's existing rhythm, and it is the
template D-13 says to follow. Line 76 is also the in-file precedent for citing a note **by content
rather than line number**, which F-6 recommends for the 999.9 citation.

---

## Standard Stack

No packages are installed by this phase. The instrument is `bash` + `curl` only (D-01).

| Tool | Version verified | Purpose |
|------|------------------|---------|
| `bash` | 5.2.37(1) | the instrument's interpreter |
| `curl` | 8.14.1 | the whole instrument (`-G`, `--data-urlencode`, `--fail-with-body`) |
| `git` | 2.55.0 | GATE-03 transcripts |
| `gh` | 2.98.0 | redirect confirmation only |
| `python3` | 3.12.14 | one-off verification of the PEP 440 claim; **not** a runtime dep |

**Package Legitimacy Audit: not applicable.** This phase installs no external packages in any ecosystem.
`curl`, `git` and `bash` are pre-existing system tools; nothing is added to `package.json`,
`pyproject.toml` or `Cargo.toml`.

---

## Code Examples

All executed 2026-09-14 from `/workspaces`. Output is reproduced verbatim.

### 1. Per-version stable-channel listing (the shape of the data)

```bash
curl -s --max-time 90 -G 'https://sql-clickhouse.clickhouse.com/' \
  --data-urlencode "user=play" \
  --data-urlencode "query=
SELECT version, sum(count) AS n
FROM pypi.pypi_downloads_per_day_by_version_by_installer_by_type
WHERE project = 'firestarter'
  AND date >= today() - 90
  AND installer IN ('pip','uv')
  AND NOT match(version, '(a|b|rc)[0-9]|dev')
GROUP BY version
ORDER BY arrayMap(x -> toUInt32OrZero(x), splitByChar('.', version)) DESC
FORMAT TSV"
```

Output (33 rows, head and tail shown; full run is in the session record):

```
2.0.9	17
2.0.7	116
2.0.6	1
2.0.5	1
2.0.4	1
2.0.3	1
2.0.2	1
2.0.1	1
1.5.6	1
...
1.3.4	2
1.1.32	1
1.1.30	1
```

Sum below 2.0.7 = **52**, matching D-09's "older-stable tail 52" exactly.

### 2. The verdict query — both D-09 legs in one call (this is the instrument)

```bash
curl -s --max-time 90 --fail-with-body -G 'https://sql-clickhouse.clickhouse.com/' \
  --data-urlencode "user=play" \
  --data-urlencode "query=
SELECT
  sumIf(count, arrayMap(x -> toUInt32OrZero(x), splitByChar('.', version)) >= [2, 0, 9]) AS fixed,
  sumIf(count, version = '2.0.7')                                                        AS at_risk,
  round(100 * fixed / nullIf(fixed + at_risk, 0), 1)                                     AS fixed_share_pct,
  fixed_share_pct >= 90 AND at_risk <= 10                                                AS trigger_met
FROM pypi.pypi_downloads_per_day_by_version_by_installer_by_type
WHERE project = 'firestarter'
  AND date >= today() - 90
  AND installer IN ('pip', 'uv')
  AND NOT match(version, '(a|b|rc)[0-9]|dev')
FORMAT TSVWithNames"
```

Output:

```
fixed	at_risk	fixed_share_pct	trigger_met
17	116	12.8	0
```

This satisfies D-04 (`installer IN ('pip','uv')`), D-05 (the PEP 440-shaped regex), D-06 (`>= 2.0.9`
computed, not allowlisted), D-07 (`version = '2.0.7'` exactly) and D-09 (`>= 90` AND `<= 10`, 90-day
rolling) in a single round trip.

### 3. Window / freshness probe (diagnostic — **not** a staleness gate; D-01 forbids gating on it)

```bash
curl -s --max-time 60 -G 'https://sql-clickhouse.clickhouse.com/' \
  --data-urlencode "user=play" \
  --data-urlencode "query=
SELECT today() AS ch_today, today()-90 AS window_start, max(date) AS latest_data, count() AS rows
FROM pypi.pypi_downloads_per_day_by_version_by_installer_by_type
WHERE project='firestarter' AND date >= today()-90 AND installer IN ('pip','uv')
FORMAT TSVWithNames"
```

Output:

```
ch_today	window_start	latest_data	rows
2026-09-14	2026-06-16	2026-09-13	141
```

### 4. GATE-03, fresh clone at a pre-rename ref — executed end to end

```bash
git clone --no-recurse-submodules https://github.com/henols/firestarter_prom.git fresh
cd fresh
git checkout v1.35
cat .gitmodules
git config submodule.firestarter.url git@github.com:henols/firestarter_fw.git
git submodule update --init --depth 1 firestarter
git -C firestarter remote -v
```

Session output:

```
### 1. checkout pre-rename ref
HEAD = 6e84030bb526da7bde603b94c4d899c0b80adc30 (2026-09-02)
### 2. .gitmodules at that ref
[submodule "firestarter"]
	path = firestarter
	url = git@github.com:henols/firestarter.git
[submodule "firestarter_app"]
	path = firestarter_app
	url = git@github.com:henols/firestarter_app.git
### 3. config BEFORE override
(unset)
### 4. set the override in .git/config
git@github.com:henols/firestarter_fw.git
### 5. does 'submodule init' clobber the override?
git@github.com:henols/firestarter_fw.git
### 6. update
From github.com:henols/firestarter_fw
 * branch            4f73c80cfa2915fb22812dde55b2923a86120c5f -> FETCH_HEAD
Submodule path 'firestarter': checked out '4f73c80cfa2915fb22812dde55b2923a86120c5f'
### 7. what did it clone?
origin	git@github.com:henols/firestarter_fw.git (fetch)
origin	git@github.com:henols/firestarter_fw.git (push)
4f73c80cfa2915fb22812dde55b2923a86120c5f docs(172-04): add CONTRIBUTING pointer, trim README and move report bullets
```

**Optional third idiom, verified clean, offered as supplementary — not a replacement for the note's
two (D-16).** A non-persisting one-shot, useful for a single archaeology checkout:

```bash
git -c submodule.firestarter.url=git@github.com:henols/firestarter_fw.git \
    submodule update --init --depth 1 firestarter
```

In a clean clone at `v1.35` with no prior override, this checks out `4f73c80c…`, leaves
`git config --get submodule.firestarter.url` **unset**, and gives the child
`origin = git@github.com:henols/firestarter_fw.git` [VERIFIED]. If the plan wants to stay strictly
inside the note's two documented workarounds, drop this.

### 5. GATE-03, existing clone — the override survives a checkout

```
### on post-rename ref (main):
	url = git@github.com:henols/firestarter_fw.git
git@github.com:henols/firestarter_fw.git
### now check out the pre-rename ref v1.35:
	url = git@github.com:henols/firestarter.git
-> .git/config override survives the checkout:
git@github.com:henols/firestarter_fw.git
### and submodule update honours it:
Submodule path 'firestarter': checked out '4f73c80cfa2915fb22812dde55b2923a86120c5f'
git@github.com:henols/firestarter_fw.git
```

### 6. The `submodule sync` hazard (F-4) — reproduce and repair

```
### override currently:
git@github.com:henols/firestarter_fw.git
### run 'git submodule sync' while HEAD is the pre-rename ref v1.35:
Synchronizing submodule url for 'firestarter'
### override after sync:
git@github.com:henols/firestarter.git
### and the submodule's own remote:
git@github.com:henols/firestarter.git
```

### 7. Today's benign behaviour, no override (F-5)

```
### HEAD ref:
v1.35
	url = git@github.com:henols/firestarter.git
### no override, plain submodule update --init TODAY:
Cloning into '.../fresh2/firestarter'...
From github.com:henols/firestarter
 * branch            4f73c80cfa2915fb22812dde55b2923a86120c5f -> FETCH_HEAD
Submodule path 'firestarter': checked out '4f73c80cfa2915fb22812dde55b2923a86120c5f'
```

### 8. The GATE-02 mechanism

```
$ python3 -c "from packaging.version import Version; \
    print('Version(\"v1.36\") ->', Version('v1.36')); \
    print('3.0.0b29 >= 1.36 ->', Version('3.0.0b29') >= Version('1.36'))"
Version("v1.36") -> 1.36
3.0.0b29 >= 1.36 -> True
```

---

## Architecture Patterns

### Recommended shape for `tools/adoption/`

```
tools/
├── catalog/            # existing — codegen.py, sync_to_subrepos.sh, messages.toml
└── adoption/           # new (D-01)
    └── pypi_version_share.sh
```

`tools/catalog/sync_to_subrepos.sh` is the in-repo precedent for a tracked, runnable, CI-less shell
tool. Its conventions, worth mirroring [VERIFIED: `head -25 tools/catalog/sync_to_subrepos.sh`,
`ls -la tools/catalog/`]:

- `#!/usr/bin/env bash`, `set -euo pipefail`
- a leading `#`-comment header naming purpose, authoritative source, and `Requirements:` line
- mode `0755` (both `codegen.py` and `sync_to_subrepos.sh` are `-rwxr-xr-x`)
- `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` for self-location

That header comment style is permitted by D-17 (meta `tools/` is outside the no-comments rule) — with
the D-17 caveat that no `# Phase 193` / `# GATE-01` / plan citation may appear.

### Pattern: the caveat travels with the number (D-02)

Print the verdict, then the caveat block, unconditionally, on every run. The caveat must carry the
**strong** framing `<specifics>` names, not a weaker paraphrase:

- installed base is **not observable**; download share is a **proxy**;
- a download of a stranded version today is a **new acquisition** of an old version (a pin, a cache, a
  stale tutorial) — a user who installed 2.0.7 in March and never reinstalls generates **zero**
  downloads and is invisible to every instrument considered;
- so the threshold certifies *"new acquisition of stranded versions has effectively stopped"* — a
  **necessary condition, never a sufficient one**;
- the **pre-2.0.7 population is outside the instrument's reach entirely** (D-07) — down there the
  instrument cannot separate a stranded human from a scanner;
- the never-upgrade residual survives any threshold.

### Anti-patterns to avoid

- **A staleness gate.** Offered and declined (D-01). The freshness probe in §Code Examples 3 is a
  diagnostic to print, not a condition to refuse on.
- **A version allowlist in the numerator.** Declined by D-06; a forgotten edit makes the gate read
  permanently un-fired.
- **`NOT LIKE '%b%'`.** Declined by D-05; it would silently admit a future `3.0.0rc1` or `2.1.0a1`.
- **Restating the `_compare_versions` walkthrough inside `CLAUDE.md`.** Declined by D-14 — cite the
  section.
- **A line-numbered citation of the 999.9 note in `CLAUDE.md`.** F-6 shows the note's own
  `firmware.py:272-288` is already stale; `CLAUDE.md:76` sets the "cited by content" precedent.

---

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Compare `2.0.9` vs `1.3.45` in SQL | a string `>=` or a `LIKE` ladder | `arrayMap(x -> toUInt32OrZero(x), splitByChar('.', version)) >= [2,0,9]` | Lexicographic string compare puts `'1.3.45' < '1.3.5'` and `'2.0.10' < '2.0.9'`. ClickHouse array compare is element-wise with shorter-is-less, so `[1,0] < [2,0,9]` and `[2,1] > [2,0,9]` both come out right [VERIFIED — the §Code Examples 1 ordering places `1.3.45` above `1.3.4`]. |
| Detect a ClickHouse error | grep the body for `DB::Exception` | `curl --fail-with-body` | Returns `rc=22` **and** prints the server's message. Verified: a bad function returned `Code: 46. DB::Exception: Function with name 'nonsense_fn' does not exist … (UNKNOWN_FUNCTION)` with `curl_rc=22`. |
| PEP 440 comparison | a hand-rolled parser | `packaging.version.Version` | It is what `firmware.py` already uses; that is precisely why the trap exists. Only needed for the one-off verification in §Code Examples 8, not at runtime. |
| Pre-rename ref selection | a hard-coded local sha | the published `v1.35` tag | F-2 — local milestone-branch shas are unreachable from a fresh clone. |

---

## Common Pitfalls

### Pitfall 1: `user=play` sent in the POST body

**What goes wrong:** `Code: 194. DB::Exception: default: Authentication failed`.
**Why:** without `-G`, `--data-urlencode` builds a POST body; ClickHouse reads `user` from the query
string only, so it falls back to the `default` user.
**Avoid:** always `curl -G`. CONTEXT.md specifies it; do not "simplify" it away.
**Warning sign:** the error names `default:`, not `play:`.

### Pitfall 2: an aggregate-only query always returns exactly one row

**What goes wrong:** a "did we get rows?" guard that counts output lines never fires.
**Why:** `SELECT sumIf(...) ... WHERE project='does-not-exist'` returns `0` on one row. Verified against
a deliberately bogus project name: output was `at_risk\trows` / `0\t0`.
**Avoid:** carry a `count() AS rows` column **inside** the query and branch on its value — that is the
minimal correctness guard D-01 permits. Do not escalate it into a staleness gate.

### Pitfall 3: the window is UTC and the data lags one day

**What goes wrong:** a reader expects the window to end today.
**Why:** ClickHouse `today()` is UTC; `max(date)` for this project is 2026-09-13 against `today()` =
2026-09-14. The window is 2026-06-16 .. 2026-09-13 [VERIFIED, §Code Examples 3].
**Avoid:** state the realised window in the script's output rather than claiming "the last 90 days".

### Pitfall 4: `git submodule sync` undoes the GATE-03 workaround

See F-4. It also rewrites the child's own `origin`. Repair needs **both**
`git config submodule.firestarter.url …` **and** `git -C firestarter remote set-url origin …`.

### Pitfall 5: dirty state fakes the trap

See F-5. A leftover `firestarter/` or `.git/modules/firestarter` produces
`Failed to clone 'firestarter' a second time, aborting`, which looks like the trap and is not; and
`git -C firestarter …` on an empty directory answers for the **parent** repo. Both would put a false
claim into a committed transcript, which is exactly what D-16 forbids.

### Pitfall 6: a leading backtick in `trigger_condition`

See F-7. The whole frontmatter block returns `{}`, `status: dormant` is lost, and
`audit.cjs` `scanSeeds` fails open — the seed silently disappears from the audit. Since GATE-01's whole
value depends on the seed surfacing at a future `/gsd-new-milestone`, this would quietly void the phase.
**Verification leg for the plan:** after rewriting the seed, assert
`extractFrontmatter` returns all four keys (a two-line `node -e` against
`.claude/gsd-core/bin/lib/frontmatter.cjs`), or at minimum that `gsd-tools`' seed scan still lists the
seed as open.

---

## Runtime State Inventory

Not a rename/refactor/migration phase in the code sense, but it touches submodule wiring, so the five
categories are answered explicitly.

| Category | Items found | Action required |
|----------|-------------|------------------|
| Stored data | **None** — no database, no datastore touched. Verified: the phase writes only `tools/adoption/`, `CLAUDE.md`, one `.planning/notes/` file, one `.planning/seeds/` file and `${phase_dir}/evidence/`. | none |
| Live service config | **None the phase changes.** It *reads* the ClickHouse public playground and GitHub's rename redirect; it configures neither. | none |
| OS-registered state | **None** — no scheduler, no service, no daemon. The meta repo has no `.github/workflows/` at all [VERIFIED: CONTEXT `<code_context>`; confirmed by `CLAUDE.md:12`'s wiki-guard retirement note]. | none |
| Secrets / env vars | **None** — the ClickHouse `play` user takes no credentials; `gh` auth is used for read-only confirmation only and nothing in the deliverable depends on it. | none |
| Build artifacts / installed packages | **None** — nothing is compiled, packaged or installed. The scratch clones produced during research live under the session scratchpad and are not committed. | none |
| **Submodule wiring (extra category, this phase)** | This clone's `.git/config` carries `submodule.firestarter.url = git@github.com:henols/firestarter_fw.git`; `origin/beta`'s `.gitmodules` still declares the **old** URL (F-2). | Demonstration only — do **not** mutate this working clone's submodule config while producing transcripts; use a disposable clone (§Code Examples 4). |

---

## Environment Availability

| Dependency | Required by | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `bash` | the instrument | ✓ | 5.2.37(1) | — |
| `curl` | the instrument | ✓ | 8.14.1 | — |
| ClickHouse playground (`sql-clickhouse.clickhouse.com`) | GATE-01 | ✓ reachable, no credentials | server 26.9.1.36875 | D-03 records BigQuery / `pypi.pypi_raw`; not built |
| `git` | GATE-03 transcripts | ✓ | 2.55.0 | — |
| GitHub over **HTTPS** | fresh-clone transcript | ✓ | `git ls-remote https://github.com/henols/firestarter_prom.git HEAD` → `6b518c74…` | — |
| GitHub over **SSH** (`git@github.com`) | submodule URLs are SSH-form | ✓ authenticated as `henols` | — | — |
| `gh` | redirect confirmation only | ✓ | 2.98.0 | — |
| `python3` | one-off PEP 440 check | ✓ | 3.12.14 | — |
| `jq` | optional TSV post-processing | ✓ | 1.7 | not needed — `FORMAT TSV` is enough |
| `shellcheck` | linting the new script | **✗ MISSING** | — | No CI lints `tools/`; review by hand. Do **not** add a CI gate — that is deferred scope. |

**Missing dependencies with no fallback:** none.
**Missing with fallback:** `shellcheck` — hand review; the meta repo has no workflows to run it in anyway.

---

## Validation Architecture

**Omitted.** `.planning/config.json` sets `workflow.nyquist_validation` to `false`
[VERIFIED: `python3 -c "import json; json.load(open('.planning/config.json'))['workflow']"`].
Other relevant flags for the planner: `research: true`, `plan_check: true`, `verifier: true`,
`code_review: true`, `use_worktrees: false`, `auto_advance: false`,
`git.base_branch: "beta"`, `git.protected_branches: ["main"]`.

---

## Security Domain

No `security_enforcement: false` is set, so this section is included. The phase's attack surface is
close to nil: it adds no network listener, no auth, no session, no persistence, and processes no user
input.

| ASVS category | Applies | Control |
|---------------|---------|---------|
| V2 Authentication | no | the ClickHouse `play` user takes no credentials by design |
| V3 Session Management | no | stateless single request |
| V4 Access Control | no | read-only public dataset |
| V5 Input Validation | **partly** | the SQL is a fixed literal in the script with no interpolated user input; keep it that way |
| V6 Cryptography | no | TLS is `curl`'s; nothing hand-rolled |

| Threat | STRIDE | Mitigation |
|--------|--------|------------|
| SQL injection via a script parameter | Tampering | Do not accept a package name or version as `$1` and splice it into the query. If the script ever takes an argument, it must be positionally fixed and validated against `^[A-Za-z0-9._-]+$`. The locked design (D-01, one fixed query) sidesteps this entirely — keep it. |
| Silent wrong answer from a failed request | Spoofing / Repudiation | `curl --fail-with-body` (rc=22 on a ClickHouse error) plus the in-query `count() AS rows` guard. |
| Credential leakage | Information disclosure | None exist; the endpoint is credential-free. Do not add a token. |

---

## State of the Art

| Old approach | Current approach | When changed | Impact |
|--------------|------------------|--------------|--------|
| `pypistats.org` API for download stats | ClickHouse public PyPI dataset | — | `pypistats` has no per-version endpoint; ClickHouse does, per-installer, with no credentials. CONTEXT `<domain>` table, Q1. |
| GitHub release-asset download counts as an adoption proxy | rejected | — | Cumulative only, no time series, no client-version dimension. CONTEXT `<canonical_refs>` Q4 answered "no". |

---

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The ClickHouse `play` user remains available, unthrottled and credential-free for the ~handful of times this gate is evaluated over the next year. | F-1 / Environment | The instrument stops working. D-03 already records the fallbacks, so the plan needs nothing further. |
| A2 | `pypi.pypi_downloads_per_day_by_version_by_installer_by_type` keeps its current schema (`project, version, date, installer, type, count`). | F-1 | The query breaks loudly (`UNKNOWN_IDENTIFIER`), caught by `--fail-with-body`. |
| A3 | The 999.9 note's projected post-claim failure (submodule update resolving to the meta repo and cloning the parent into `firestarter/`) is correct. | F-5 | Unverifiable today by construction. The new note must present it as a projection, which D-16 requires anyway. |
| A4 | `v1.35` remains a published tag on `origin`. | F-2 | The transcript's ref would need re-picking. Tags are not deleted in this project. |

---

## Open Questions

1. **Does the plan fix `CLAUDE.md:12`'s "`tools/` now holds `catalog/` alone" in the same edit?**
   - What we know: adding `tools/adoption/` falsifies it, and D-15 puts the GATE-03 pointer in that same
     paragraph.
   - What's unclear: nothing decision-shaped; it is a one-clause correction.
   - Recommendation: fold it into the D-15 edit. Leaving a freshly-false sentence in the file the phase
     is editing would be a self-inflicted stale reference one phase after Phase 192's "live references
     only".

2. **Does the seed's third checklist leg get scoped to `main`, or annotated with the beta state?**
   - What we know: F-2 — `origin/beta`'s `.gitmodules` still carries the old URL; `origin/main`'s does
     not; the milestone branch is unpushed.
   - What's unclear: whether D-12's "satisfied on all three legs" intends `main` only.
   - Recommendation: scope the leg to `main` (the branch that reaches a default install and the branch
     the trap concerns) and say so, rather than asserting a beta state that is currently falsifiable.

3. **Does the supplementary `git -c …` one-shot idiom go in the GATE-03 note?**
   - What we know: it is verified clean and is genuinely more ergonomic for a one-off archaeology
     checkout.
   - What's unclear: D-16 says the two workarounds are "already written there; do not invent new ones."
   - Recommendation: planner's call. If included, present it as a convenience *beside* the note's two,
     not as a replacement for either.

---

## Sources

### Primary (HIGH confidence — executed this session)

- `https://sql-clickhouse.clickhouse.com/` (`user=play`, `FORMAT TSV`/`TSVWithNames`), server
  26.9.1.36875 — the schema, the per-version listing, the verdict query, the window probe, the
  empty-result probe and the error-handling probe.
- `git` 2.55.0 against `/workspaces` and two disposable clones of
  `https://github.com/henols/firestarter_prom.git` — F-2, F-3, F-4, F-5 and §Code Examples 4–7.
- `gh` 2.98.0 — `repos/henols/firestarter` and `repos/henols/firestarter_fw` (both id `810276812`).
- `python3` 3.12.14 + `packaging` — §Code Examples 8.
- `node` against `.claude/gsd-core/bin/lib/frontmatter.cjs` — F-7's five-shape parser table.

### Primary (HIGH confidence — read this session)

- `.planning/phases/193-the-deferred-claim-made-measurable/193-CONTEXT.md` (335 lines, in full).
- `/workspaces/CLAUDE.md` (77 lines, in full).
- `.planning/REQUIREMENTS.md:90-105` — GATE-01/02/03 verbatim; `:142-144` traceability rows.
- `.planning/ROADMAP.md:435-457` — Phase 193 goal and the four criteria.
- `.planning/notes/999.9-repo-rename-impact-analysis.md:86-118` — §"Standing rule this must produce"
  and §"The `.gitmodules` archaeology trap", verbatim.
- `.planning/seeds/SEED-claim-firestarter-slug.md` (53 lines, in full).
- `tools/catalog/sync_to_subrepos.sh:1-25` and `ls -la tools/catalog/` — the shell-tool precedent.
- `.claude/gsd-core/bin/lib/audit.cjs:595-650` — `scanSeeds`' frontmatter consumption.
- `firestarter_app/firestarter/firmware.py:282-298` (branch `v1.38-repository-rename`) —
  `_compare_versions`, and the same symbol on `origin/beta` (:271) and `origin/main` (:132).

### Secondary / tertiary

None. No WebSearch was used and no claim below HIGH confidence is carried.

---

## Metadata

**Confidence breakdown:**

| Area | Level | Reason |
|------|-------|--------|
| The ClickHouse instrument | HIGH | Executed; reproduces D-09's baseline to the digit, including the 52-download tail. |
| The pre-rename ref | HIGH | Reachability of `9ccf0414` disproved in a clean clone; `v1.35` proved by `git show`. |
| Both `.gitmodules` workarounds | HIGH | Executed end to end in disposable clones; transcripts reproduced. |
| The `submodule sync` hazard | HIGH | Reproduced, and the repair sequence re-verified. |
| The frontmatter leading-backtick trap | HIGH | Executed against GSD's own parser, five shapes. |
| `CLAUDE.md` insertion points | HIGH | Line numbers read directly from the 77-line file. |
| The post-claim failure shape (A3) | LOW | Unverifiable by construction — the redirect is live and D-1 forbids firing the claim. Must be presented as a projection. |

**Research date:** 2026-09-14
**Valid until:** the ClickHouse figures move daily — re-run §Code Examples 2 at execution time and record
the reading in `SUMMARY.md`. The git, `CLAUDE.md` and frontmatter findings are stable until `origin/beta`
takes the v1.38 merge (which changes F-2's beta row and satisfies the seed's third checklist leg).
