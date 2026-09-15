# Phase 192: Live References Only - Pattern Map

**Mapped:** 2026-09-13
**Files analyzed:** 12 artefact groups (4 edited surfaces, 1 requirements amendment, 3 evidence transcripts)
**Analogs found:** 12 / 12 — every artefact this phase produces has a direct precedent in phases 189/190/191

> This is a planning/meta repository sweep phase. "Role" and "data flow" below are read in the GSD
> artefact sense (evidence transcript, disposition record, mechanical string edit, generated document,
> requirements amendment), not in the web-application sense. All analogs are tracked meta-repo files
> (`git ls-files` verified); none is a gitignored mirror.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `README.md` (meta, line 27) | doc / live reference | transform (1 string edit) | `firestarter/README.md:47` edit in `189-03-PLAN.md` Task 1 | exact |
| `.planning/v1.4-e2e-verify.sh` (7 hits) | runnable script | transform (mechanical repoint) | same 189-03 Task 1 pattern (line-addressed `sed -n 'Np'` verification) | role-match |
| `.planning/v1.4-RELEASE-PROCEDURES.md` (6 hits) | runnable procedure doc | transform | same as above | role-match |
| `.planning/codebase/{ARCHITECTURE,CONCERNS,CONVENTIONS,INTEGRATIONS,STACK,STRUCTURE,TESTING}.md` | generated document | batch regeneration + hand re-attach | `.claude/gsd-core/workflows/map-codebase.md` `--paths` contract; current frontmatter of `.planning/codebase/STACK.md` | exact (tool contract) |
| `.planning/REQUIREMENTS.md` §SWEEP-03 | requirements amendment | transform (hand edit, one paragraph) | `.planning/REQUIREMENTS.md:77-87` existing SWEEP block prose shape | exact |
| `evidence/192-slug-sweep.txt` (new) | evidence transcript | read-only measurement | `190-endpoints.../evidence/190-slug-sweep.txt` | exact |
| `evidence/192-*-enumeration.txt` (new, D-01) | evidence transcript | read-only enumeration | `189-free-the-name/evidence/189-firmware-slug-sweep.txt` | exact |
| `evidence/192-disposition.md` or `SUMMARY.md` D-08 section | disposition record | narrative | `191-the-branch.../evidence/191-stable-disposition.md` | exact |

## Pattern Assignments

### `evidence/192-slug-sweep.txt` (evidence transcript, read-only measurement)

**Analog:** `/workspaces/.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/evidence/190-slug-sweep.txt`
(secondary: `/workspaces/.planning/phases/189-free-the-name/evidence/189-firmware-slug-sweep.txt`)

**Transcript header pattern** (190-slug-sweep.txt lines 1-4):

```
BOUNDARY-AWARE BARE-SLUG SWEEP (D-05)
======================================
capture_date: 2026-09-13T18:03:00Z
capture_commit: app=560ec24523eb2f8c643c9db3dd302efecf57e2e1
```

**Pattern-justification paragraph — always present, always explains why the naive grep is vacuous**
(190-slug-sweep.txt lines 6-17, condensed verbatim):

```
Scope: the firestarter_app working tree only (tracked files), from its own
root. The naive sweep `grep -rn "henols/firestarter" | grep -v
"firestarter_fw\|firestarter_app\|firestarter_prom"` under-reports: it
filters whole LINES, not matches ... The pattern below is boundary-aware
instead: it requires the bare slug be followed by a non-identifier character
or the end of the line, so it cannot match `firestarter_fw`,
`firestarter_app` or `firestarter_prom`, all of which extend the slug with `_`.
```

**Paired-reading pattern — a zero is only evidence when a control is non-zero**
(190-slug-sweep.txt lines 19-30):

```
Reading 1: the bare-slug sweep
-------------------------------
command: git grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- .
matching files: (none)
result: 0

Reading 2: the non-vacuity positive control
--------------------------------------------
command: git grep -lE 'henols/firestarter_prom' -- . | wc -l
matching files:
  ...
result: 8
```

followed by the explicit interpretation sentence (190-slug-sweep.txt lines 38-40):

```
A zero bare-slug reading paired with a zero control would be a failed gate,
not a pass -- it would mean the pattern itself matched nothing, which is
indistinguishable from a clean tree without the control.
```

**Closing boundary section — what the sweep deliberately does NOT cover**
(190-slug-sweep.txt lines 48+, header verbatim):

```
What this sweep deliberately does NOT cover
---------------------------------------------
- The meta repository (/workspaces, outside firestarter_app). ...
- Anything under .planning/milestones/ in any repository. ...
```

**For 192 this section inverts:** the meta repository is now in scope, and the "does NOT cover"
list becomes `.planning/milestones/` (D-5), the 63 record files (D-01), and `.planning/PROJECT.md`.

**The sweep command itself — `/usr/bin/grep` is load-bearing.** Two accepted forms exist in the
precedent; 192 uses the meta form because the meta root's PATH `grep` is ugrep and honours
`.gitignore`:

```bash
# meta-repo form (CONTEXT.md <code_context>, used by the 192 discussion measurement)
git ls-files | while read -r f; do
  /usr/bin/grep -nE 'henols/firestarter($|[^_A-Za-z0-9])' "$f"
done

# sub-repo re-verification form (189-03-PLAN.md:230-232) -- run from inside each submodule
git -C /workspaces/firestarter     grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- . | wc -l
git -C /workspaces/firestarter_app grep -lE 'henols/firestarter([^_a-zA-Z0-9]|$)' -- . | wc -l
```

**Sub-repo control readings to pair with those two zeros** (189-03-PLAN.md:232):

```bash
git -C /workspaces/firestarter grep -lE 'henols/firestarter_prom' -- . | wc -l   # expect 4
```

**Evidence file naming:** `{padded_phase}-{slug}.txt` under `${phase_dir}/evidence/` —
`189-firmware-slug-sweep.txt`, `190-slug-sweep.txt`, `191-url-02-merged-main.txt`. Task-scoped
transcripts add the plan/task key: `189-rename-03-fresh-clone.txt`, `191-stable-01-pypi.txt`.
192's files therefore read `192-slug-sweep.txt`, `192-<nn>-<slug>.txt`.

---

### `evidence/192-disposition.md` (disposition record, narrative)

**Analog:** `/workspaces/.planning/phases/191-the-branch-that-reaches-users/evidence/191-stable-disposition.md`

**Opening pattern — one section per ROADMAP success criterion, every claim citing its evidence file**
(191-stable-disposition.md lines 1-6):

```markdown
# Phase 191 disposition record

The version a person gets from `pip install firestarter` addresses `henols/firestarter_fw`, and
that claim is verified below by installing the published artefact rather than by reading the
diff. This record is the phase's answer to the ROADMAP's four success criteria, one section
each, every claim citing the evidence file and reading that supports it.

## Criterion 1 — ...
```

**Claim-with-citation pattern** (191-stable-disposition.md lines 21-26):

```markdown
- **Three `ref=main` contents-API readings**, all taken live after the merge, all recorded in
  evidence/`191-url-02-merged-main.txt`:
  - `firestarter/constants.py@main`: repointed endpoint count 1; boundary-aware bare-slug sweep
    (`henols/firestarter([^_a-zA-Z0-9]|$)`) count 0.
  - `README.md@main`: ... non-vacuity positive control (`henols/firestarter_app`) count 4 —
    proving the zeros above are a real absence, not an empty API response.
```

192 has four ROADMAP criteria; this is the shape for proving them, plus the D-01 enumeration
(full match list with the edited subset marked) and the D-09 merge-base-anchored D-5 proof.

---

### D-08 declared-but-unpaid debt (SUMMARY.md narrative)

**Analog 1 — the must_haves truth form** (`189-03-SUMMARY.md:43`):

```yaml
  - "D-10 honored: no source-scanning guard, workflow, or lint rule was added inside the firmware
     repository. Cleanliness is proved at verification time by evidence/189-firmware-slug-sweep.txt,
     which carries a positive control (henols/firestarter_prom, 4 matches) so its zero cannot be
     attributed to an empty or misdirected scan."
```

**Analog 2 — the in-body declaration form** (`191-02-SUMMARY.md:110`, a real defect recorded as
deliberately unfixed and unfiled, naming file:line, the consequence, and the governing decision):

```markdown
This is a real, previously-measured `main`-branch defect (not reproduced live in this plan, which
touches no hardware) and is left unfixed and unfiled beyond this note, consistent with the
milestone's stated D-02 posture that `main` carries no regression guard and this milestone does
not add one.
```

**Analog 3 — the disposition-record form** (`191-05-SUMMARY.md:54`): "names all three unachieved
items ... the missing origin/main regression guard D-02 ... with both backlog items linked by
filename". 192's D-08 statement must name, plainly: after this phase **nothing watches any of the
three repositories for slug regression**, including `origin/main`, which has no `tests/`, no
`[test]` extra and no `ci.yml`; and that 189 D-10, 190 D-05 and 191 D-02 each deferred here and
this phase closes it **by declaration, not by construction**.

---

### `README.md`, `.planning/v1.4-e2e-verify.sh`, `.planning/v1.4-RELEASE-PROCEDURES.md` (mechanical string edits)

**Analog:** `/workspaces/.planning/phases/189-free-the-name/189-03-PLAN.md` Task 1 — the
line-addressed edit-and-prove pattern.

**Verification pattern — assert the changed line by number, and assert the untouched lines by
number too** (189-03-PLAN.md:166-179, verbatim):

```xml
  <verify>
    <automated>git -C /workspaces/firestarter show --numstat --format= HEAD</automated>
    <automated>sed -n '47p' /workspaces/firestarter/README.md | /usr/bin/grep -c 'henols/firestarter_fw/releases'</automated>
    <automated>sed -n '22p' /workspaces/firestarter/tests/meta_presence.py | /usr/bin/grep -c 'henols/firestarter_fw'</automated>
    <automated>awk 'NR==1||NR==7||NR==75||NR==80||NR==81' /workspaces/firestarter/README.md | /usr/bin/grep -c 'henols/firestarter_prom\|henols/firestarter_app'</automated>
    <automated>git -C /workspaces branch --show-current</automated>
  </verify>
```

The `awk 'NR==a||NR==b...'` leg is the **untouched-neighbours control**: it proves the edit did
not spill onto sibling lines that legitimately name `firestarter_app` / `firestarter_prom`. 192
needs the same control, because every one of the 13 runnable-artefact hits "sits directly beside a
`henols/firestarter_app` twin" (D-02).

**Concrete edit sites already measured — do not re-derive** (boundary-aware `/usr/bin/grep`, today):

```
README.md:27              | [firestarter](https://github.com/henols/firestarter) | The AVR firmware ...
.planning/v1.4-e2e-verify.sh:142,157,184,186,205,207,208
.planning/v1.4-RELEASE-PROCEDURES.md:40,177,192,200,249,325
```

`v1.4-RELEASE-PROCEDURES.md:325` is the stale-and-destructive one named by D-02
(`gh release delete <tag> -R henols/firestarter`).

**Pattern for the `git ls-files` / `/usr/bin/grep` caveat inside the PLAN body** (189-02-PLAN.md:114,
189-03-PLAN.md:115,122) — every 192 plan should carry the same note:

```
... PATH grep in this devcontainer is ugrep and under-scans. Any leg whose evidence depends on
seeing every file uses `/usr/bin/grep` explicitly ... measured with `git -C firestarter ls-files`,
never with a bare `git ls-files` at the meta root.
```

**Hard prohibitions to carry forward** (189-03-PLAN.md `prohibitions`, still binding here):
no comment, annotation, phase reference or requirement citation is added to any edited file; a
"comment exists" criterion must not be written.

---

### `.planning/codebase/*.md` (generated documents, batch regeneration)

**Analog:** `/workspaces/.claude/gsd-core/workflows/map-codebase.md` lines 33-66 (the `--paths`
contract) plus the live frontmatter of `/workspaces/.planning/codebase/STACK.md`.

**Invocation, verbatim per D-04:**

```
/gsd-map-codebase --paths .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
```

**The contract that makes the scope real** (map-codebase.md:38-47):

```
- Pass `--paths <p1>,<p2>,...` through to each spawned `gsd-codebase-mapper`
  agent's prompt. Agents scope their Glob/Grep/Bash exploration to the listed
  repo-relative prefixes only — no whole-repo scan.
- On write, each mapper stamps `last_mapped_commit: <HEAD sha>` into the YAML
  frontmatter of every document it produces (see `bin/lib/drift.cjs:writeMappedCommit`).
```

**The frontmatter shape the remap must leave true** (`.planning/codebase/STACK.md:1-5`, the
current — and per D-03 false — stamp; the post-remap file must show a fresh commit and date and the
same `mapped_paths` string):

```yaml
---
last_mapped_commit: 3e2f7d89
last_mapped_at: 2026-08-26T20:42:40.949Z
mapped_paths: .claude,.devcontainer,.github,.gitignore,.gitmodules,.vscode,CLAUDE.md
---
```

**The preserved-history text D-05 requires be re-attached verbatim** (`.planning/codebase/STACK.md:8-9`):

```markdown
**Analysis Date:** 2026-08-26 (meta-repo / dev-environment layer)
**Prior analysis:** 2026-05-08 (submodule layer — preserved below, not re-verified this run)
```

Capture all seven documents before the remap (e.g. `git show HEAD:.planning/codebase/<doc>.md`
into the scratchpad) so "dropped preserved section" is a diff, not a memory.

**Post-remap gate (D-06)** — the same boundary-aware sweep, scoped to the seven documents:

```bash
/usr/bin/grep -nE 'henols/firestarter($|[^_A-Za-z0-9])' .planning/codebase/*.md
/usr/bin/grep -nE 'catalog-sync-check|wiki-check|wiki-publish|tools/wiki' .planning/codebase/*.md
```

Pre-remap stale-line inventory is already derived in `192-SCOUT.md` §3 — do not re-derive it.

---

### `.planning/REQUIREMENTS.md` §SWEEP-03 (requirements amendment, hand edit)

**Analog:** the surrounding SWEEP block itself, `.planning/REQUIREMENTS.md:77-87`:

```markdown
- [ ] **SWEEP-03**: `.planning/codebase/STACK.md` no longer describes a catalog-sync workflow that checks
      out the sub-repos via `actions/checkout` — that workflow does not exist, and the meta repository has
      no `.github/workflows/` at all. Found while measuring 999.9's "CI/release workflows" clause, which is
      itself a no-op.
```

House style to preserve: `- [ ] **ID**:` opener, six-space continuation indent, bold for the
load-bearing clause, em-dash for the justification, and a closing provenance sentence.

**Hard constraint (D-07):** hand edit only. GSD requirements verbs reformat the whole file and
would bury a one-line scope correction in an unreviewable diff. The `| SWEEP-03 | Phase 192 |
Pending |` traceability row at `.planning/REQUIREMENTS.md:137` flips at phase completion by the
normal executor path, not by a reformat.

## Shared Patterns

### The boundary-aware discriminator
**Source:** `189-03-PLAN.md:230`, `190-slug-sweep.txt:22`, `192-CONTEXT.md` `<code_context>`
**Apply to:** every measurement leg in every 192 plan
```
henols/firestarter($|[^_A-Za-z0-9])      # meta form (192 discussion measurement)
henols/firestarter([^_a-zA-Z0-9]|$)      # sub-repo form (189/190, equivalent)
```
Pick one form per plan and use it verbatim in both the plan and the transcript, so the transcript's
`command:` line is copy-pasteable.

### `/usr/bin/grep`, never PATH `grep`
**Source:** `189-02-PLAN.md:114`, `189-03-PLAN.md:122`
**Apply to:** every `<automated>` leg and every recorded `command:` line.
PATH `grep` here is ugrep and silently honours `.gitignore`. Absolute path is mandatory; any excerpt
lifted from this document keeps it.

### The non-vacuity control
**Source:** `189-firmware-slug-sweep.txt` READING 2, `190-slug-sweep.txt` Reading 2
**Apply to:** every zero this phase reports (seven codebase docs, both sub-repos, the D-5 diff).
A bare zero is not evidence. Pair it with `henols/firestarter_prom` or `henols/firestarter_app`
and record the expected non-zero count beside it.

### Merge-base anchoring, recomputed not hardcoded
**Source:** D-09; project rule that local `beta` goes stale
**Apply to:** the SWEEP-02 / D-5 proof.
```bash
RANGE_BASE="$(git merge-base beta HEAD)"       # measured 2026-09-13 as f0307ac8
git diff --stat "$RANGE_BASE"..HEAD -- .planning/milestones/     # expect empty
git log --oneline "$RANGE_BASE"..HEAD -- .planning/milestones/ | wc -l   # expect 0
```
Re-taken at verification time, because this phase must not itself be what breaks it.

### Branch-identity leg
**Source:** `189-01/02/03-PLAN.md`, closing `<automated>` of nearly every verify block
```xml
<automated>git -C /workspaces branch --show-current</automated>
```
Cheap guard against work landing on `beta`/`main`. Every 192 verify block should end with it.

### Evidence-file naming and location
**Source:** 189/190/191 `evidence/` directories
`${phase_dir}/evidence/{padded_phase}-{slug}.txt` for transcripts; `.md` only for narrative
disposition records (`191-stable-disposition.md`). The directory is created by the first plan that
writes into it and is listed in that plan's `files_modified`.

### No comments in product source — and no plan may ask for one
**Source:** `CLAUDE.md` hard rule; `189-03-PLAN.md` prohibitions
**Apply to:** nothing in 192 touches `firestarter/` or `firestarter_app/` source, so this binds
mainly as a prohibition on the *plans*: do not write "add a comment citing SWEEP-0N" and do not make
a comment an acceptance criterion. Rationale goes to SUMMARY.md or the commit message.

## No Analog Found

None. Every artefact type this phase produces has a direct precedent in phases 189-191.

Two items are precedent-thin and worth flagging to the planner:

| Item | Why thin | Mitigation |
|---|---|---|
| `/gsd-map-codebase` re-run | No prior phase in this milestone ran it; the last run was 2026-08-26 and four commits hand-patched its output since | D-06 already prescribes the mitigation: the mapper's output is gated by a post-remap sweep, never trusted on intent |
| D-05 preserved-history re-attach | No precedent for restoring a section a generator dropped | Treat as a pre/post diff over seven captured files, not as a memory exercise |

## Metadata

**Analog search scope:** `/workspaces/.planning/phases/189-free-the-name/`,
`/workspaces/.planning/phases/190-endpoints-that-do-not-depend-on-a-redirect/`,
`/workspaces/.planning/phases/191-the-branch-that-reaches-users/`,
`/workspaces/.planning/codebase/`, `/workspaces/.planning/REQUIREMENTS.md`,
`/workspaces/.claude/gsd-core/workflows/map-codebase.md`
**Files scanned:** 14 (all git-tracked meta-repo paths; no gitignored mirrors)
**Pattern extraction date:** 2026-09-13
